#!/usr/bin/env python3
"""
multi-vector concat 측정 트랙 — 빌드 산출물 sanity 검증 게이트.

목적
----
build_concat_cells.py 가 만든 7 concat cell 의 NPY/parquet artifact 가
measure_paper_exact.py 측정에 그대로 투입 가능한 상태인지 검증한다.
launch_concat_track.sh 를 돌리기 전에 반드시 PASS 여야 한다 — 깨진 artifact 로
측정하면 119+ file 을 통째로 버리게 되므로 launch 전 필수 게이트.

검증 항목 (cell 당)
-------------------
1. {table}_vectors.npy   — 존재 + shape (N, 기대차원 224/864/288) + 전부 finite
2. {table}_strata.npy    — 존재 + 길이가 vectors N 과 일치 + KM20 cluster 20개 전부
                           존재 (빈 stratum 없음) + 값 범위 [0, 19]
3. query_pool_{ALIAS}_sf{sf}.parquet
                         — 존재 + 컬럼 {query_id, embedding, q_pk}
                         + embedding 차원 = vectors 차원 + query_id 0..N_QUERIES-1
4. query_selectivity_{ALIAS}_sf{sf}.parquet
                         — 존재 + 컬럼 {query_id, selectivity, D_target,
                           true_cardinality, actual_sel}
                         + query_id 가 query_pool 과 1:1 + paper sel {0.001,0.01,0.10}
                           포함 + true_cardinality 전부 > 0 (sel 0 = 측정 불능)
5. {table}_concat_meta.json
                         — 존재 + missing_count == 0 (broadcast 매칭 실패 0)
                         + dim/n_rows 가 실제 NPY 와 일치

★ measure_paper_exact._measure_common.fetch_all_vectors_safe 의 NPY fast-path 는
  vectors+strata NPY 길이가 어긋나면 PG fallback 으로 빠진다. concat cell 은 PG
  테이블이 없으므로 길이 불일치 = 측정 실패. 그래서 길이 일치를 hard check 한다.
  _load_query_pool 이 기대하는 컬럼명도 그대로 검증한다.

CLI
---
    python3 verify_concat_npy.py                 # 7 cell 전부
    python3 verify_concat_npy.py --cell deep_sift_1   # 1 cell

exit code: 0 = 전체 PASS / 1 = 1개라도 FAIL

서버 경로: /mnt/hdd0/home/capstone2026/cache/rq3/verify_concat_npy.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

try:
    import pyarrow.parquet as pq
except ImportError as exc:  # pragma: no cover - 서버엔 pyarrow 있음
    raise RuntimeError("pyarrow 필요 — 서버에서 실행") from exc


# ---------------------------------------------------------------------------
# 경로 + 상수 — build_concat_cells.py 와 lock-step
# ---------------------------------------------------------------------------

CACHE_RQ1 = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
CACHE_RQ3 = Path("/mnt/hdd0/home/capstone2026/cache/rq3")

N_STRATA = 20          # KM20 — build_concat_cells.N_STRATA
N_QUERIES = 100        # query_pool 행 수 — build_concat_cells.N_QUERIES
# paper Fig 13 verbatim sel — measure_paper_exact.PAPER_SELECTIVITIES.
# query_selectivity 에 이 3종이 반드시 들어 있어야 측정 코드가 sel 을 골라낼 수 있다.
PAPER_SELECTIVITIES = (0.001, 0.01, 0.10)

# query pool / selectivity 가 가져야 할 컬럼 — _measure_common._load_query_pool
# 및 qs_full lookup 이 기대하는 것 (measure_paper_exact 와 동일)
QP_COLS = {"query_id", "embedding", "q_pk"}
QS_COLS = {"query_id", "selectivity", "D_target", "true_cardinality", "actual_sel"}


def kst() -> str:
    """KST 타임스탬프 (프로젝트 규칙)."""
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# cell 레지스트리 — build_concat_cells.CELLS 와 동일한 7 cell
# ---------------------------------------------------------------------------
#   key      : CLI --cell 값
#   combo    : table prefix (partsupp_{combo}_concat_{sf})
#   dim      : concat 기대 차원 (dim_a + dim_b)
#   sf       : scale factor
#   alias    : query_pool 파일명 alias (대문자)
#
CELLS: dict[str, dict] = {
    f"deep_sift_{sf}": {
        "combo": "deep_sift", "dim": 96 + 128, "sf": sf, "alias": "DEEP_SIFT_CONCAT",
    }
    for sf in (1, 10, 100)
} | {
    f"deep_wiki_{sf}": {
        "combo": "deep_wiki", "dim": 96 + 768, "sf": sf, "alias": "DEEP_WIKI_CONCAT",
    }
    for sf in (1, 10)
} | {
    f"deep_yfcc_{sf}": {
        "combo": "deep_yfcc", "dim": 96 + 192, "sf": sf, "alias": "DEEP_YFCC_CONCAT",
    }
    for sf in (1, 10)
}

ALL_CELLS: list[str] = list(CELLS.keys())


# ---------------------------------------------------------------------------
# cell 당 산출물 경로 — build_concat_cells.cell_output_paths 와 동일
# ---------------------------------------------------------------------------

def cell_output_paths(cfg: dict) -> dict[str, Path]:
    combo, sf, alias = cfg["combo"], cfg["sf"], cfg["alias"]
    base = f"partsupp_{combo}_concat_{sf}"
    return {
        "vectors":    CACHE_RQ1 / f"{base}_vectors.npy",
        "strata":     CACHE_RQ1 / f"{base}_strata.npy",
        "pks":        CACHE_RQ1 / f"{base}_pks.npy",
        "query_pool": CACHE_RQ1 / f"query_pool_{alias}_sf{sf}.parquet",
        "query_sel":  CACHE_RQ1 / f"query_selectivity_{alias}_sf{sf}.parquet",
        "meta":       CACHE_RQ3 / f"{base}_concat_meta.json",
    }


# ---------------------------------------------------------------------------
# 단일 cell 검증 — (ok, [체크 결과 줄...]) 반환
# ---------------------------------------------------------------------------

def verify_cell(cell_key: str) -> tuple[bool, list[str]]:
    """cell 1개 검증. Returns (전체 PASS 여부, 사람이 읽는 진단 줄 리스트)."""
    cfg = CELLS[cell_key]
    paths = cell_output_paths(cfg)
    expect_dim = cfg["dim"]
    lines: list[str] = []
    ok = True

    def check(label: str, passed: bool, detail: str = "") -> None:
        nonlocal ok
        tag = "PASS" if passed else "FAIL"
        if not passed:
            ok = False
        lines.append(f"    [{tag}] {label}" + (f" — {detail}" if detail else ""))

    # ---- 1. vectors.npy ----
    n_rows = -1
    vp = paths["vectors"]
    if not vp.exists():
        check("vectors.npy 존재", False, str(vp))
    else:
        try:
            # mmap 으로 shape/dtype 먼저 확인 (대용량 — 224d × 80M = 7GB 류)
            vec_mm = np.load(vp, mmap_mode="r")
            n_rows = int(vec_mm.shape[0])
            dim_ok = vec_mm.ndim == 2 and vec_mm.shape[1] == expect_dim
            check("vectors.npy shape", dim_ok,
                  f"shape={tuple(vec_mm.shape)} (기대 (N, {expect_dim}))")
            # finite 검증은 전체 로드 — sf100 은 7GB, 서버 메모리 충분
            vec = np.load(vp)
            finite = bool(np.isfinite(vec).all())
            check("vectors.npy 전부 finite", finite,
                  "" if finite else f"non-finite {int((~np.isfinite(vec)).sum()):,}개")
            del vec
        except Exception as exc:  # pragma: no cover - 서버 런타임
            check("vectors.npy 로드", False, repr(exc))

    # ---- 2. strata.npy ----
    sp = paths["strata"]
    if not sp.exists():
        check("strata.npy 존재", False, str(sp))
    else:
        try:
            sids = np.load(sp)
            len_ok = (n_rows < 0) or (len(sids) == n_rows)
            check("strata.npy 길이 = vectors N", len_ok,
                  f"len(strata)={len(sids):,} vs N={n_rows:,}")
            counts = np.bincount(sids.astype(np.int64), minlength=N_STRATA)
            k_used = int((counts > 0).sum())
            check(f"strata 클러스터 {N_STRATA}개 전부 존재", k_used == N_STRATA,
                  f"K_used={k_used}/{N_STRATA}")
            empty = [i for i in range(N_STRATA) if counts[i] == 0]
            check("빈 stratum 없음", len(empty) == 0,
                  "" if not empty else f"빈 cluster id={empty}")
            range_ok = int(sids.min()) >= 0 and int(sids.max()) < N_STRATA
            check(f"strata 값 범위 [0, {N_STRATA - 1}]", range_ok,
                  f"min={int(sids.min())} max={int(sids.max())}")
            if k_used == N_STRATA:
                lines.append(f"      strata 분포: min={int(counts.min()):,} "
                              f"max={int(counts.max()):,} mean={int(counts.mean()):,}")
        except Exception as exc:  # pragma: no cover
            check("strata.npy 로드", False, repr(exc))

    # ---- 3. query_pool parquet ----
    qpp = paths["query_pool"]
    qp_n = -1
    if not qpp.exists():
        check("query_pool parquet 존재", False, str(qpp))
    else:
        try:
            qp = pq.read_table(qpp).to_pandas()
            qp_n = len(qp)
            cols = set(qp.columns)
            check("query_pool 컬럼 스키마", QP_COLS.issubset(cols),
                  f"cols={sorted(cols)} (필요 {sorted(QP_COLS)})")
            if "embedding" in cols and qp_n > 0:
                emb_dim = len(qp.iloc[0]["embedding"])
                check("query_pool embedding 차원 = vectors 차원",
                      emb_dim == expect_dim,
                      f"emb_dim={emb_dim} (기대 {expect_dim})")
            if "query_id" in cols and qp_n > 0:
                qid_ok = (int(qp["query_id"].min()) == 0
                          and int(qp["query_id"].max()) == qp_n - 1
                          and qp["query_id"].is_unique)
                check(f"query_pool query_id 0..{qp_n - 1} 연속·유일", qid_ok,
                      f"min={int(qp['query_id'].min())} max={int(qp['query_id'].max())} "
                      f"n={qp_n} unique={bool(qp['query_id'].is_unique)}")
            check(f"query_pool 행 수 = {N_QUERIES}", qp_n == N_QUERIES,
                  f"rows={qp_n}")
        except Exception as exc:  # pragma: no cover
            check("query_pool parquet 로드", False, repr(exc))

    # ---- 4. query_selectivity parquet ----
    qsp = paths["query_sel"]
    if not qsp.exists():
        check("query_selectivity parquet 존재", False, str(qsp))
    else:
        try:
            qs = pq.read_table(qsp).to_pandas()
            cols = set(qs.columns)
            check("query_selectivity 컬럼 스키마", QS_COLS.issubset(cols),
                  f"cols={sorted(cols)} (필요 {sorted(QS_COLS)})")
            if "query_id" in cols and qp_n > 0:
                qs_ids = set(int(x) for x in qs["query_id"].unique())
                pool_ids = set(range(qp_n))
                check("query_selectivity query_id 가 query_pool 과 1:1",
                      qs_ids == pool_ids,
                      f"qs distinct={len(qs_ids)} vs pool={qp_n}")
            if "selectivity" in cols:
                have = sorted(float(x) for x in qs["selectivity"].unique())
                missing_sel = [s for s in PAPER_SELECTIVITIES
                               if not any(np.isclose(s, h) for h in have)]
                check(f"paper sel {PAPER_SELECTIVITIES} 포함",
                      len(missing_sel) == 0,
                      f"보유 sel={have}" + (f" / 누락={missing_sel}" if missing_sel else ""))
            if "true_cardinality" in cols:
                tc = qs["true_cardinality"].to_numpy()
                n_zero = int((tc <= 0).sum())
                check("true_cardinality 전부 > 0", n_zero == 0,
                      "" if n_zero == 0 else f"true_card<=0 인 (query,sel) {n_zero}개")
        except Exception as exc:  # pragma: no cover
            check("query_selectivity parquet 로드", False, repr(exc))

    # ---- 5. meta json ----
    mp = paths["meta"]
    if not mp.exists():
        check("concat_meta.json 존재", False, str(mp))
    else:
        try:
            meta = json.loads(mp.read_text())
            missing = int(meta.get("missing_count", -1))
            check("meta missing_count == 0", missing == 0,
                  f"missing_count={missing}")
            meta_dim = int(meta.get("dim", -1))
            check("meta dim = 기대 차원", meta_dim == expect_dim,
                  f"meta dim={meta_dim} (기대 {expect_dim})")
            if n_rows >= 0:
                meta_n = int(meta.get("n_rows", -1))
                check("meta n_rows = 실제 vectors N", meta_n == n_rows,
                      f"meta n_rows={meta_n:,} vs NPY N={n_rows:,}")
        except Exception as exc:  # pragma: no cover
            check("concat_meta.json 로드", False, repr(exc))

    return ok, lines


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="multi-vector concat 측정 트랙 — 빌드 산출물 sanity 검증 게이트.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--cell", choices=ALL_CELLS,
                    help="cell 1개만 검증 (예: deep_sift_1). 생략 시 7 cell 전부.")
    args = ap.parse_args()

    cells = [args.cell] if args.cell else ALL_CELLS

    print(f"[{kst()}] === verify_concat_npy ===")
    print(f"[{kst()}] CACHE_RQ1: {CACHE_RQ1}")
    print(f"[{kst()}] CACHE_RQ3: {CACHE_RQ3}")
    print(f"[{kst()}] 검증 cell ({len(cells)}): {cells}\n")

    results: list[tuple[str, bool]] = []
    for ck in cells:
        cfg = CELLS[ck]
        tbl = f"partsupp_{cfg['combo']}_concat_{cfg['sf']}"
        print(f"[{kst()}] >>> {ck}  (table={tbl}, dim={cfg['dim']}, sf={cfg['sf']})")
        ok, lines = verify_cell(ck)
        for ln in lines:
            print(ln)
        print(f"    => {ck}: {'PASS' if ok else 'FAIL'}\n")
        results.append((ck, ok))

    # ---- 요약 표 ----
    print(f"[{kst()}] === 검증 요약 ===")
    print(f"  {'cell':<16} {'table':<34} {'결과':<6}")
    print(f"  {'-' * 16} {'-' * 34} {'-' * 6}")
    for ck, ok in results:
        cfg = CELLS[ck]
        tbl = f"partsupp_{cfg['combo']}_concat_{cfg['sf']}"
        print(f"  {ck:<16} {tbl:<34} {'PASS' if ok else 'FAIL':<6}")

    n_pass = sum(1 for _, ok in results if ok)
    n_fail = len(results) - n_pass
    print(f"\n[{kst()}] 전체: {n_pass}/{len(results)} PASS, {n_fail} FAIL")
    if n_fail:
        print(f"[{kst()}] FAIL — launch_concat_track.sh 실행 금지. 위 FAIL 항목 먼저 해결.")
        sys.exit(1)
    print(f"[{kst()}] ALL PASS — launch_concat_track.sh 게이트 통과 ✓")
    sys.exit(0)


if __name__ == "__main__":
    main()
