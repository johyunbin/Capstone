#!/usr/bin/env python3
"""query_selectivity parquet 에 sel=0.001 행 보강 (v9 sel sweep 용).

배경
----
v9 selectivity sweep (sel 0.001/0.01/0.10) 가 measure_paper_exact.py 의

    qs_match = qs_full[(np.isclose(qs_full["selectivity"], sel))
                       & (qs_full["query_id"] == q_row_idx)]
    if len(qs_match) > 0:
        D = float(qs_match.iloc[0]["D_target"])
        true_card = float(qs_match.iloc[0]["true_cardinality"])
    else:
        D = TPC_H_THRESHOLD
        true_card = total_rows * sel   # ← heuristic fallback

로 query_selectivity parquet 에서 (selectivity, query_id) 행을 찾아
D_target / true_cardinality 를 가져온다. 기존 parquet 의 sel 값은
[0.01, 0.05, 0.1, 0.3, 0.5] 뿐 — sel=0.001 행이 없으면 위 else 분기로
떨어져 heuristic 측정이 되어 버린다.

이 스크립트는 sel=0.001 행만 append 한다. 기존 5 sel 행은 절대 안 건드림.

방식 (prepare_cell.py:gen_querypool 와 byte-identical)
------------------------------------------------------
원본 query_selectivity 를 만든 prepare_cell.py 의 gen_querypool() 로직 그대로:

  1. rng = np.random.default_rng(42)                              # QUERY_SEED
  2. q_idx      = rng.choice(n, size=100, replace=False)          # query 인덱스
  3. q_vecs     = all_vecs[q_idx]   /  q_keys = pks[q_idx]         # RNG 미소비
  4. sample_idx = rng.choice(n, size=min(200_000, n), ...)        # calib 샘플
     ※ q_idx → (q_vecs/q_keys 인덱싱) → sample_idx 의 RNG 호출 순서가 핵심 —
       이 순서를 그대로 따라야 기존 sel 행과 동일한 sample_idx 가 나온다.
  5. 각 query qv 에 대해 all_d = L2(all_vecs - qv) 전체 N (chunk 100K)
  6. sample_d = all_d[sample_idx]
  7. for sel: D_target  = quantile(sample_d, sel)        ← sel=0.001
              true_card = (all_d <= D_target).sum()       ← '<=' inclusive, 전체 N
              actual_sel = true_card / n

검증: 위 로직으로 기존 sel=0.01 행을 재계산하면 원본 parquet 와 정확히 일치함을
사전 확인 완료 — DEEP_sf1 q0: sel=0.001 D_target 0.898035 / true_card 784,
sel=0.01 D_target 1.006660 / true_card 7977 모두 stored 값과 일치.

query_pool 의 embedding == all_vecs[q_idx] 임도 확인. 안전을 위해 본 스크립트는
query_pool embedding 과 all_vecs[q_idx] 를 3 지점 대조하고, 불일치 시 abort 한다.

메모리: 큰 NPY (sf100 80M) 는 np.load mmap_mode='r' 로 열고 거리 계산을 chunk
단위로 처리 — 한 번에 전체 array 를 RAM 에 올리지 않는다.

CLI
---
    # 전부 (v9 16 cell 이 읽는 query_selectivity 13 파일, sf1→sf10→sf100 순)
    python3 augment_query_sel_0001.py --all

    # 특정 파일 하나 (파일명으로 지정)
    python3 augment_query_sel_0001.py --file query_selectivity_SIFT_sf100.parquet

    # 계획 + ETA 만 (계산/쓰기 없음)
    python3 augment_query_sel_0001.py --all --dry-run

    # 이미 sel=0.001 있어도 재계산 (기본은 멱등 skip)
    python3 augment_query_sel_0001.py --file query_selectivity_DEEP_sf100.parquet --force

멱등성: 대상 parquet 에 이미 sel=0.001 행이 있으면 skip (--force 로 override).
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 경로 / 상수 — prepare_cell.py 와 lock-step (verbatim)
# ---------------------------------------------------------------------------

CACHE_RQ1 = Path("/mnt/hdd0/home/capstone2026/cache/rq1")

# prepare_cell.py 의 상수 그대로
N_QUERIES = 100              # prepare_cell.N_QUERIES
SAMPLE_FOR_SEL = 200_000     # prepare_cell.SAMPLE_FOR_SEL
QUERY_SEED = 42              # gen_querypool 의 np.random.default_rng(42)
CHUNK = 100_000              # gen_querypool 의 거리 계산 chunk
NEW_SEL = 0.001              # 보강할 selectivity

#: query_selectivity 파일명 → 원본 NPY vectors 파일명 (table).
#: measure_paper_exact.DATASET_ALIAS + prepare_cell.CELLS 의 table 명에서 역산.
#:   query_selectivity_DEEP_sf{N}.parquet           → partsupp_deep_{N}_vectors.npy
#:   query_selectivity_SIFT_sf{N}.parquet           → partsupp_sift_{N}_vectors.npy
#:   query_selectivity_SSN_sf{N}.parquet            → partsupp_fb_{N}_vectors.npy
#:   query_selectivity_WIKI_sf{N}.parquet           → partsupp_wiki_{N}_vectors.npy
#:   query_selectivity_YFCC_sf{N}.parquet           → partsupp_yfcc_{N}_vectors.npy
#:   query_selectivity_DEEP_SIFT_CONCAT_sf{N}.parquet → partsupp_deep_sift_concat_{N}_vectors.npy
#:   query_selectivity_DEEP_WIKI_CONCAT_sf{N}.parquet → partsupp_deep_wiki_concat_{N}_vectors.npy
#: query_pool_{stem}.parquet 도 동일 stem 을 쓴다.
ALIAS_TABLE = {
    "DEEP": "partsupp_deep",
    "SIFT": "partsupp_sift",
    "SSN":  "partsupp_fb",
    "WIKI": "partsupp_wiki",
    "YFCC": "partsupp_yfcc",
    "DEEP_SIFT_CONCAT": "partsupp_deep_sift_concat",
    "DEEP_WIKI_CONCAT": "partsupp_deep_wiki_concat",
    "DEEP_YFCC_CONCAT": "partsupp_deep_yfcc_concat",
}

#: v9 sel sweep CELLS_ALL 16 cell 이 실제로 읽는 query_selectivity 파일 목록.
#: measure_paper_exact CellSpec 의 dataset/sf + DATASET_ALIAS 적용 결과:
#:   A1-DEEP / A5-scale-sf100 / A2-Fig9(DEEP+WIKI cross→DEEP)   → DEEP sf100
#:   A5-scale-sf{1,10}                                          → DEEP sf{1,10}
#:   A8-DEEP+SIFT-sf10 (DEEP+SIFT→DEEP)                         → DEEP sf10
#:   A1-SIFT / A5-scale-sf{1,10}-SIFT                           → SIFT sf{1,10,100}
#:   A1-SSN  / A5-scale-sf{1,10}-SSN                            → SSN  sf{1,10,100}
#:   A6-WIKI-sf{1,10}                                           → WIKI sf{1,10}
#:   A7-YFCC-sf1 / A2-Fig7                                      → YFCC sf{1,10}
#: 중복 제거 → 13 파일. sf1 먼저, sf100 마지막 (거리 계산 비용 순).
DEFAULT_FILES = [
    "query_selectivity_DEEP_sf1.parquet",
    "query_selectivity_SIFT_sf1.parquet",
    "query_selectivity_SSN_sf1.parquet",
    "query_selectivity_WIKI_sf1.parquet",
    "query_selectivity_YFCC_sf1.parquet",
    "query_selectivity_DEEP_sf10.parquet",
    "query_selectivity_SIFT_sf10.parquet",
    "query_selectivity_SSN_sf10.parquet",
    "query_selectivity_WIKI_sf10.parquet",
    "query_selectivity_YFCC_sf10.parquet",
    "query_selectivity_DEEP_sf100.parquet",
    "query_selectivity_SIFT_sf100.parquet",
    "query_selectivity_SSN_sf100.parquet",
]


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def parse_qs_filename(fname: str) -> tuple[str, int, str]:
    """'query_selectivity_DEEP_sf100.parquet' → (alias='DEEP', sf=100, stem='DEEP_sf100').

    stem 은 query_pool / query_selectivity 파일이 공유하는 식별자.
    """
    stem = Path(fname).stem  # query_selectivity_DEEP_sf100
    if not stem.startswith("query_selectivity_"):
        raise ValueError(f"query_selectivity_*.parquet 형식이 아님: {fname}")
    body = stem[len("query_selectivity_"):]  # DEEP_sf100
    alias, sf_part = body.rsplit("_sf", 1)
    return alias, int(sf_part), body


def resolve_paths(fname: str) -> dict[str, Path]:
    """query_selectivity 파일명 → vectors NPY / query_pool / query_sel 경로."""
    alias, sf, stem = parse_qs_filename(fname)
    if alias not in ALIAS_TABLE:
        raise ValueError(
            f"alias '{alias}' 미등록 — ALIAS_TABLE 에 추가 필요 (파일={fname})")
    table = f"{ALIAS_TABLE[alias]}_{sf}"
    return {
        "vectors":    CACHE_RQ1 / f"{table}_vectors.npy",
        "query_pool": CACHE_RQ1 / f"query_pool_{stem}.parquet",
        "query_sel":  CACHE_RQ1 / f"query_selectivity_{stem}.parquet",
    }


def estimate_minutes(n_rows: int, dim: int) -> float:
    """거리 계산 ETA (분). 100 query × N×dim L2.

    경험치 보수 추정: sf1(~0.8M) ~0.3분, sf10(~8M) ~3분, sf100(~80M) ~30-50분.
    100 query × N pairwise L2 ≈ 100·N·dim FLOP 기준.
    """
    flops = 100.0 * n_rows * dim
    sec = flops / 2.5e10  # 보수치
    return max(0.2, sec / 60.0)


# ---------------------------------------------------------------------------
# 핵심 — 한 cell 의 sel=0.001 행 계산 (gen_querypool 와 동일 로직)
# ---------------------------------------------------------------------------

def compute_sel_rows(stem: str, vecs: np.ndarray, qp: pd.DataFrame,
                     sel: float = NEW_SEL) -> pd.DataFrame:
    """prepare_cell.py:gen_querypool 와 동일 로직으로 sel 행 계산.

    vecs 는 mmap array 도 가능 — 거리 계산은 CHUNK 단위라 메모리 안전.

    Returns
    -------
    DataFrame: query_id, selectivity, D_target, true_cardinality, actual_sel
    """
    n = len(vecs)

    # --- prepare_cell.gen_querypool 와 동일한 RNG 순서: q_idx → (인덱싱) → sample_idx ---
    rng = np.random.default_rng(QUERY_SEED)
    q_idx = rng.choice(n, size=N_QUERIES, replace=False)
    # gen_querypool: q_vecs = all_vecs[q_idx]; q_keys = pks[q_idx]  ← RNG 미소비
    sample_n = min(SAMPLE_FOR_SEL, n)
    sample_idx = rng.choice(n, size=sample_n, replace=False)
    # mmap fancy-index 는 새 array 를 만들어 메모리에 올림 — q_vecs 는 100 행이라 무시 가능
    q_vecs = np.asarray(vecs[q_idx], dtype=np.float32)

    # --- 안전장치: query_pool embedding 과 vecs[q_idx] 가 일치하는지 3 지점 대조 ---
    # (gen_querypool 이 q_vecs[qi].tolist() 로 query_pool 을 저장했으므로 일치해야 함)
    if len(qp) != N_QUERIES:
        raise RuntimeError(f"{stem}: query_pool 행 {len(qp)} != {N_QUERIES}")
    for check_i in (0, N_QUERIES // 2, N_QUERIES - 1):
        emb_pool = np.asarray(qp.iloc[check_i]["embedding"], dtype=np.float32)
        if not np.allclose(emb_pool, q_vecs[check_i], atol=1e-5):
            raise RuntimeError(
                f"{stem}: query_pool[{check_i}] embedding 이 vecs[q_idx[{check_i}]] 와 "
                f"불일치 — RNG seed/순서 또는 NPY 가 원본과 다름. abort."
            )

    rows = []
    t0 = time.time()
    for qi in range(N_QUERIES):
        qv = q_vecs[qi]
        all_d = np.empty(n, dtype=np.float32)
        for i in range(0, n, CHUNK):
            blk = np.asarray(vecs[i:i + CHUNK], dtype=np.float32)
            all_d[i:i + CHUNK] = np.linalg.norm(blk - qv, axis=1)
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
            print(f"[{kst()}]     {stem}: {qi + 1}/{N_QUERIES} "
                  f"({time.time() - t0:.0f}s)", flush=True)
    print(f"[{kst()}]     {stem}: sel={sel} 계산 완료 ({time.time() - t0:.1f}s)",
          flush=True)
    return pd.DataFrame(rows)


def augment_one(fname: str, *, force: bool, dry_run: bool) -> dict:
    """한 query_selectivity parquet 에 sel=0.001 행 append (멱등)."""
    try:
        paths = resolve_paths(fname)
        _, _, stem = parse_qs_filename(fname)
    except ValueError as exc:
        print(f"[{kst()}] SKIP {fname}: {exc}")
        return {"file": fname, "status": "bad_name", "error": str(exc)}

    # 입력 존재 확인
    for key in ("vectors", "query_pool", "query_sel"):
        if not paths[key].exists():
            print(f"[{kst()}] SKIP {stem}: {key} 미존재 ({paths[key]})")
            return {"file": fname, "status": "missing_input", "missing": key}

    qs = pd.read_parquet(paths["query_sel"])
    existing_sels = sorted(float(s) for s in qs["selectivity"].unique())

    # 멱등: 이미 sel=0.001 이 있으면 skip (force 시 제거 후 재계산)
    has_new = any(np.isclose(s, NEW_SEL) for s in existing_sels)
    if has_new and not force:
        print(f"[{kst()}] SKIP {stem}: sel={NEW_SEL} 이미 존재 "
              f"(sels={existing_sels}) — --force 로 재계산 가능")
        return {"file": fname, "status": "already_present", "sels": existing_sels}

    # NPY shape 미리 읽기 (mmap — dry-run ETA 용으로도 안전)
    vecs_mmap = np.load(paths["vectors"], mmap_mode="r")
    n_rows, dim = int(vecs_mmap.shape[0]), int(vecs_mmap.shape[1])
    eta_min = estimate_minutes(n_rows, dim)
    gb = n_rows * dim * 4 / 1e9
    print(f"[{kst()}] {stem}: N={n_rows:,} dim={dim} ({gb:.1f}GB) "
          f"기존 sels={existing_sels}  ETA~{eta_min:.1f}분")

    if dry_run:
        del vecs_mmap
        return {"file": fname, "status": "dry", "n_rows": n_rows,
                "dim": dim, "eta_min": round(eta_min, 1), "sels": existing_sels}

    # 거리 계산: mmap array 를 그대로 chunk 처리 (전체 RAM 적재 안 함)
    qp = pd.read_parquet(paths["query_pool"])
    t_compute = time.time()
    new_rows = compute_sel_rows(stem, vecs_mmap, qp, sel=NEW_SEL)
    del vecs_mmap

    # force 재계산이면 기존 sel=0.001 행 제거 후 합침
    if has_new:
        qs = qs[~np.isclose(qs["selectivity"], NEW_SEL)].copy()

    # 컬럼 순서/dtype 을 기존 parquet 과 정확히 맞춤
    new_rows = new_rows[list(qs.columns)]
    for col in qs.columns:
        new_rows[col] = new_rows[col].astype(qs[col].dtype)

    merged = pd.concat([qs, new_rows], ignore_index=True)
    # query_id, selectivity 순 정렬 (가독성 — 측정 코드는 isclose 매칭이라 순서 무관)
    merged = merged.sort_values(["query_id", "selectivity"]).reset_index(drop=True)

    # 백업 후 덮어쓰기 (기존 5 sel 행은 merged 안에 그대로 보존됨)
    backup = paths["query_sel"].with_suffix(
        f".parquet.bak_pre_sel0001_"
        f"{datetime.now(timezone(timedelta(hours=9))).strftime('%Y%m%d_%H%M')}")
    if not backup.exists():
        shutil.copy2(paths["query_sel"], backup)
    merged.to_parquet(paths["query_sel"], index=False)

    d_mean = float(new_rows["D_target"].mean())
    tc_mean = float(new_rows["true_cardinality"].mean())
    print(f"[{kst()}]   {stem}: parquet 갱신 — {len(qs)} → {len(merged)} 행 "
          f"(+{len(new_rows)} sel={NEW_SEL}), backup={backup.name}")
    print(f"[{kst()}]   {stem}: sel={NEW_SEL} D_target mean={d_mean:.4f} "
          f"true_card mean={tc_mean:.1f}  ({time.time() - t_compute:.0f}s)")
    return {
        "file": fname, "status": "augmented",
        "n_rows": n_rows, "rows_before": len(qs), "rows_after": len(merged),
        "d_target_mean": d_mean, "true_card_mean": tc_mean,
        "backup": str(backup),
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description="query_selectivity parquet 에 sel=0.001 행 보강 (v9 sel sweep)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--all", action="store_true",
                    help=f"v9 16 cell 의 query_selectivity 전부 ({len(DEFAULT_FILES)}파일, "
                         f"sf1→sf10→sf100 순)")
    ap.add_argument("--file", nargs="+", default=None,
                    help="대상 query_selectivity 파일명 (예: "
                         "query_selectivity_SIFT_sf100.parquet). 여러 개 가능")
    ap.add_argument("--force", action="store_true",
                    help="이미 sel=0.001 있는 parquet 도 재계산 (기본은 멱등 skip)")
    ap.add_argument("--dry-run", action="store_true",
                    help="계획 + ETA 만 출력, 계산/쓰기 없음")
    args = ap.parse_args()

    if args.all:
        files = DEFAULT_FILES
    elif args.file:
        files = args.file
    else:
        ap.error("--all 또는 --file 중 하나 필요")

    print(f"[{kst()}] === augment_query_sel_0001 (sel={NEW_SEL} 보강) ===")
    print(f"[{kst()}] CACHE_RQ1: {CACHE_RQ1}")
    print(f"[{kst()}] 대상 {len(files)} 파일")
    print(f"[{kst()}] dry_run={args.dry_run} force={args.force}\n")

    t_total = time.time()
    summary: list[dict] = []
    for fname in files:
        try:
            res = augment_one(fname, force=args.force, dry_run=args.dry_run)
        except Exception as exc:  # pragma: no cover - server runtime
            import traceback
            traceback.print_exc()
            res = {"file": fname, "status": "error", "error": str(exc)}
        summary.append(res)

    print(f"\n[{kst()}] === 요약 ===")
    for s in summary:
        extra = ""
        if s["status"] == "augmented":
            extra = (f" {s['rows_before']}→{s['rows_after']}행 "
                     f"D_mean={s['d_target_mean']:.4f} "
                     f"tc_mean={s['true_card_mean']:.0f}")
        elif s["status"] == "dry":
            extra = f" N={s['n_rows']:,} ETA~{s['eta_min']}분"
        print(f"  {s['file']:<42} {s['status']:<16}{extra}")

    n_aug = sum(1 for s in summary if s["status"] == "augmented")
    n_skip = sum(1 for s in summary if s["status"] == "already_present")
    n_err = sum(1 for s in summary
                if s["status"] in ("error", "bad_name", "missing_input"))
    elapsed = time.time() - t_total
    print(f"[{kst()}] augmented={n_aug}  already={n_skip}  problem={n_err}  "
          f"/ {len(files)}  total {elapsed:.0f}s ({elapsed / 60:.1f}분)")
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
