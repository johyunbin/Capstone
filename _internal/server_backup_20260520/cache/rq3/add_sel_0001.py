#!/usr/bin/env python3
"""query_selectivity parquet 에 sel=0.001 행 보강.

배경
----
v9 selectivity sweep (sel 0.001/0.01/0.10) 가 measure_paper_exact.py 의
`qs_match = qs_full[(isclose(selectivity, sel)) & (query_id == q_row_idx)]`
로 query_selectivity parquet 에서 (sel, query_id) 행을 찾아 D_target / true_cardinality
를 가져온다. 기존 parquet 에는 sel = [0.01, 0.05, 0.1, 0.3, 0.5] 만 있고 0.001 이
없어서 heuristic fallback (true_card = total_rows * sel) 로 떨어진다.

이 스크립트는 sel=0.001 행만 append 한다. 기존 5 sel 행은 그대로 보존.

방식 (cache/prepare_cell.py:gen_querypool 와 byte-identical)
-----------------------------------------------------------
prepare_cell.py 가 원본 query_selectivity 를 만든 로직 그대로:
  1. rng = np.random.default_rng(42)
  2. q_idx      = rng.choice(n, size=100, replace=False)        ← query 인덱스
  3. sample_idx = rng.choice(n, size=min(200_000, n), ...)      ← calib 샘플
     ※ q_idx 를 먼저 뽑은 다음 sample_idx 를 뽑는 RNG 순서가 중요 —
       이 순서를 그대로 따라야 기존 sel 행과 같은 sample_idx 가 나온다.
  4. 각 query qv 에 대해 all_d = L2(vecs - qv) 전체 N (chunk 100K)
  5. sample_d = all_d[sample_idx]
  6. D_target    = quantile(sample_d, sel)          ← sel=0.001
  7. true_card   = (all_d <= D_target).sum()         ← '<=' inclusive, 전체 N
  8. actual_sel  = true_card / n

검증: 위 로직으로 기존 sel=0.01 행을 재계산하면 원본과 정확히 일치함을
사전 확인 완료 (DEEP_sf1 qid0: D_target 1.006660 / true_card 7977 일치).

query_pool 의 embedding == vecs[q_idx] 임도 확인 완료. 안전을 위해 본 스크립트는
query_pool embedding 과 vecs[q_idx] 를 대조하고, 불일치 시 abort 한다.

CLI
---
    # sf1 cell 만 (가벼움)
    python3 add_sel_0001.py --aliases DEEP_sf1 SIFT_sf1 SSN_sf1 WIKI_sf1 YFCC_sf1

    # 전부 (sf1 → sf10 → sf100 순서로 정렬해서 실행)
    python3 add_sel_0001.py --all

    # 계획만 보기
    python3 add_sel_0001.py --all --dry-run

    # 이미 sel=0.001 있는 parquet 도 재계산 (기본은 skip)
    python3 add_sel_0001.py --aliases DEEP_sf1 --force
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 경로 / 상수 — prepare_cell.py 와 lock-step
# ---------------------------------------------------------------------------

CACHE_RQ1 = Path("/mnt/hdd0/home/capstone2026/cache/rq1")

# prepare_cell.py 의 상수 그대로
N_QUERIES = 100
SAMPLE_FOR_SEL = 200_000
QUERY_SEED = 42
CHUNK = 100_000          # gen_querypool 의 거리 계산 chunk
NEW_SEL = 0.001          # 보강할 selectivity

#: alias → 원본 NPY vectors 파일명 (table). measure_paper_exact.py DATASET_ALIAS +
#: prepare_cell.py CELLS 의 table 명에서 역산. query_selectivity_{alias}_sf{N}.parquet
#: 와 query_pool_{alias}_sf{N}.parquet 도 같은 alias 를 쓴다.
#:   DEEP → partsupp_deep_{sf},  SIFT → partsupp_sift_{sf},
#:   SSN  → partsupp_fb_{sf},    WIKI → partsupp_wiki_{sf},
#:   YFCC → partsupp_yfcc_{sf}
ALIAS_TABLE = {
    "DEEP": "partsupp_deep",
    "SIFT": "partsupp_sift",
    "SSN":  "partsupp_fb",
    "WIKI": "partsupp_wiki",
    "YFCC": "partsupp_yfcc",
}

#: v9 sel sweep 16 cell 이 실제로 읽는 query_selectivity 파일 (DATASET_ALIAS 적용 후).
#:   A5-scale-sf{1,10,100} + A1-DEEP + A8-DEEP+SIFT-sf10 + A2-Fig9   → DEEP sf{1,10,100}
#:   A5-scale-sf{1,10}-SIFT + A1-SIFT                                 → SIFT sf{1,10,100}
#:   A5-scale-sf{1,10}-SSN  + A1-SSN                                  → SSN sf{1,10,100}
#:   A6-WIKI-sf{1,10}                                                 → WIKI sf{1,10}
#:   A7-YFCC-sf1 + A2-Fig7                                            → YFCC sf{1,10}
#: (sf1 먼저, sf100 마지막 — 거리 계산 비용 순)
DEFAULT_ALIASES = [
    "DEEP_sf1", "SIFT_sf1", "SSN_sf1", "WIKI_sf1", "YFCC_sf1",
    "DEEP_sf10", "SIFT_sf10", "SSN_sf10", "WIKI_sf10", "YFCC_sf10",
    "DEEP_sf100", "SIFT_sf100", "SSN_sf100",
]


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def parse_alias(alias: str) -> tuple[str, int]:
    """'DEEP_sf100' → ('DEEP', 100)."""
    ds, sf_part = alias.rsplit("_sf", 1)
    return ds, int(sf_part)


def cell_paths(alias: str) -> dict[str, Path]:
    ds, sf = parse_alias(alias)
    table = f"{ALIAS_TABLE[ds]}_{sf}"
    return {
        "vectors":   CACHE_RQ1 / f"{table}_vectors.npy",
        "query_pool": CACHE_RQ1 / f"query_pool_{alias}.parquet",
        "query_sel": CACHE_RQ1 / f"query_selectivity_{alias}.parquet",
    }


def estimate_minutes(n_rows: int, dim: int) -> float:
    """거리 계산 ETA (분). 100 query × N×dim L2.

    경험치: sf1(~800K) ~0.5분, sf10(~8M) ~5분, sf100(~80M) ~50분 수준.
    100 query × N pairwise L2 ≈ 100·N·dim FLOP. 측정 box 대략 환산.
    """
    # 100 query × N × dim, 대략 2.5e8 (N·dim) 당 1초 수준으로 보수 추정
    flops = 100.0 * n_rows * dim
    sec = flops / 2.5e10  # 보수치
    return max(0.2, sec / 60.0)


# ---------------------------------------------------------------------------
# 핵심 — 한 cell 의 sel=0.001 행 계산
# ---------------------------------------------------------------------------

def compute_sel_rows(alias: str, vecs: np.ndarray, qp: pd.DataFrame,
                     sel: float = NEW_SEL) -> pd.DataFrame:
    """prepare_cell.py:gen_querypool 와 동일 로직으로 sel 행 계산.

    Returns
    -------
    DataFrame: query_id, selectivity, D_target, true_cardinality, actual_sel
    """
    n = len(vecs)

    # --- prepare_cell.py 와 동일한 RNG 순서: q_idx → sample_idx ---
    rng = np.random.default_rng(QUERY_SEED)
    q_idx = rng.choice(n, size=N_QUERIES, replace=False)
    sample_n = min(SAMPLE_FOR_SEL, n)
    sample_idx = rng.choice(n, size=sample_n, replace=False)
    q_vecs = vecs[q_idx]

    # --- 안전장치: query_pool embedding 과 vecs[q_idx] 가 일치하는지 대조 ---
    # (prepare_cell.py 가 q_vecs[qi].tolist() 로 저장했으므로 일치해야 함)
    if len(qp) != N_QUERIES:
        raise RuntimeError(f"{alias}: query_pool 행 {len(qp)} != {N_QUERIES}")
    for check_i in (0, N_QUERIES // 2, N_QUERIES - 1):
        emb_pool = np.asarray(qp.iloc[check_i]["embedding"], dtype=np.float32)
        if not np.allclose(emb_pool, q_vecs[check_i], atol=1e-5):
            raise RuntimeError(
                f"{alias}: query_pool[{check_i}] embedding 이 vecs[q_idx[{check_i}]] 와 "
                f"불일치 — RNG seed/순서 또는 NPY 가 원본과 다름. abort."
            )

    rows = []
    t0 = time.time()
    for qi in range(N_QUERIES):
        qv = q_vecs[qi]
        all_d = np.empty(n, dtype=np.float32)
        for i in range(0, n, CHUNK):
            all_d[i:i + CHUNK] = np.linalg.norm(vecs[i:i + CHUNK] - qv, axis=1)
        sample_d = all_d[sample_idx]
        d_target = float(np.quantile(sample_d, sel))   # gen_querypool 와 동일
        true_card = int((all_d <= d_target).sum())      # '<=' inclusive, 전체 N
        rows.append({
            "query_id": qi,
            "selectivity": sel,
            "D_target": d_target,
            "true_cardinality": true_card,
            "actual_sel": true_card / n,
        })
        if (qi + 1) % 25 == 0:
            print(f"[{kst()}]     {alias}: {qi + 1}/{N_QUERIES} "
                  f"({time.time() - t0:.0f}s)", flush=True)
    print(f"[{kst()}]     {alias}: sel={sel} 계산 완료 ({time.time() - t0:.1f}s)",
          flush=True)
    return pd.DataFrame(rows)


def augment_one(alias: str, *, force: bool, dry_run: bool) -> dict:
    """한 cell 의 query_selectivity parquet 에 sel=0.001 행 append."""
    paths = cell_paths(alias)
    ds, sf = parse_alias(alias)

    # 입력 존재 확인
    for key in ("vectors", "query_pool", "query_sel"):
        if not paths[key].exists():
            print(f"[{kst()}] SKIP {alias}: {key} 미존재 ({paths[key]})")
            return {"alias": alias, "status": "missing_input", "missing": key}

    qs = pd.read_parquet(paths["query_sel"])
    existing_sels = sorted(qs["selectivity"].unique())

    # 이미 sel=0.001 이 있으면 skip (force 시 제거 후 재계산)
    has_new = any(np.isclose(s, NEW_SEL) for s in existing_sels)
    if has_new and not force:
        print(f"[{kst()}] SKIP {alias}: sel={NEW_SEL} 이미 존재 "
              f"(sels={existing_sels}) — --force 로 재계산 가능")
        return {"alias": alias, "status": "already_present",
                "sels": [float(s) for s in existing_sels]}

    # NPY shape 미리 읽기 (mmap — dry-run ETA 용으로도 안전)
    vecs_mmap = np.load(paths["vectors"], mmap_mode="r")
    n_rows, dim = int(vecs_mmap.shape[0]), int(vecs_mmap.shape[1])
    eta_min = estimate_minutes(n_rows, dim)
    print(f"[{kst()}] {alias}: N={n_rows:,} dim={dim} "
          f"기존 sels={[float(s) for s in existing_sels]}  ETA~{eta_min:.1f}분")

    if dry_run:
        return {"alias": alias, "status": "dry", "n_rows": n_rows,
                "dim": dim, "eta_min": round(eta_min, 1),
                "sels": [float(s) for s in existing_sels]}

    # 거리 계산은 실제 array 로 (chunk 단위라 mmap 도 가능하지만 일관성 위해 load)
    del vecs_mmap
    t_load = time.time()
    vecs = np.load(paths["vectors"])
    print(f"[{kst()}]   {alias}: NPY load {time.time() - t_load:.1f}s "
          f"({vecs.nbytes / 1e9:.2f} GB)", flush=True)
    qp = pd.read_parquet(paths["query_pool"])

    new_rows = compute_sel_rows(alias, vecs, qp, sel=NEW_SEL)

    # force 재계산이면 기존 sel=0.001 행 제거 후 합침
    if has_new:
        qs = qs[~np.isclose(qs["selectivity"], NEW_SEL)].copy()

    # 컬럼 순서/dtype 을 기존 parquet 과 맞춤 (query_id/true_cardinality 가 float 로
    # 저장돼 있을 수 있음 — 기존 row 의 dtype 을 그대로 따라간다)
    new_rows = new_rows[list(qs.columns)]
    for col in qs.columns:
        new_rows[col] = new_rows[col].astype(qs[col].dtype)

    merged = pd.concat([qs, new_rows], ignore_index=True)
    # query_id, selectivity 순으로 정렬 (가독성 — 측정 코드는 isclose 매칭이라 무관)
    merged = merged.sort_values(["query_id", "selectivity"]).reset_index(drop=True)

    # 백업 후 덮어쓰기
    backup = paths["query_sel"].with_suffix(
        f".parquet.bak_pre_sel0001_"
        f"{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d_%H%M')}")
    if not backup.exists():
        import shutil
        shutil.copy2(paths["query_sel"], backup)
    merged.to_parquet(paths["query_sel"], index=False)

    d_mean = float(new_rows["D_target"].mean())
    tc_mean = float(new_rows["true_cardinality"].mean())
    print(f"[{kst()}]   {alias}: parquet 갱신 — {len(qs)} → {len(merged)} 행 "
          f"(+{len(new_rows)} sel={NEW_SEL}), backup={backup.name}")
    print(f"[{kst()}]   {alias}: sel={NEW_SEL} D_target mean={d_mean:.4f} "
          f"true_card mean={tc_mean:.1f}")
    return {
        "alias": alias, "status": "augmented",
        "n_rows": n_rows, "rows_before": len(qs), "rows_after": len(merged),
        "d_target_mean": d_mean, "true_card_mean": tc_mean,
        "backup": str(backup),
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="query_selectivity parquet 에 sel=0.001 행 보강",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--aliases", nargs="+", default=None,
                    help="대상 alias (예: DEEP_sf1 SIFT_sf100). 미지정 시 --all 필요")
    ap.add_argument("--all", action="store_true",
                    help=f"v9 16 cell 의 query_selectivity 전부 ({len(DEFAULT_ALIASES)}개)")
    ap.add_argument("--force", action="store_true",
                    help="이미 sel=0.001 있는 parquet 도 재계산")
    ap.add_argument("--dry-run", action="store_true",
                    help="계획 + ETA 만 출력, 계산/쓰기 없음")
    args = ap.parse_args()

    if args.all:
        aliases = DEFAULT_ALIASES
    elif args.aliases:
        aliases = args.aliases
    else:
        ap.error("--aliases 또는 --all 중 하나 필요")

    print(f"[{kst()}] === add_sel_0001 (sel={NEW_SEL} 보강) ===")
    print(f"[{kst()}] CACHE_RQ1: {CACHE_RQ1}")
    print(f"[{kst()}] 대상 {len(aliases)} cell: {aliases}")
    print(f"[{kst()}] dry_run={args.dry_run} force={args.force}\n")

    t_total = time.time()
    summary: list[dict] = []
    for alias in aliases:
        try:
            res = augment_one(alias, force=args.force, dry_run=args.dry_run)
        except Exception as exc:  # pragma: no cover - server runtime
            import traceback
            traceback.print_exc()
            res = {"alias": alias, "status": "error", "error": str(exc)}
        summary.append(res)

    print(f"\n[{kst()}] === 요약 ===")
    for s in summary:
        extra = ""
        if s["status"] == "augmented":
            extra = (f" {s['rows_before']}→{s['rows_after']}행 "
                     f"D_mean={s['d_target_mean']:.4f} tc_mean={s['true_card_mean']:.0f}")
        elif s["status"] == "dry":
            extra = f" N={s['n_rows']:,} ETA~{s['eta_min']}분"
        print(f"  {s['alias']:<16} {s['status']:<16}{extra}")

    n_aug = sum(1 for s in summary if s["status"] == "augmented")
    n_err = sum(1 for s in summary if s["status"] == "error")
    elapsed = time.time() - t_total
    print(f"[{kst()}] augmented={n_aug} / {len(aliases)}  error={n_err}  "
          f"total {elapsed:.0f}s ({elapsed / 60:.1f}분)")
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
