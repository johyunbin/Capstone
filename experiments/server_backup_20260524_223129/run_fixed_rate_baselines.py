#!/usr/bin/env python3
"""
RQ1 fixed-rate baselines — Exqutor 본 논문 직접 비교용 (pgvector / VBASE / DuckDB).

Exqutor (arXiv:2512.09695v2) 가 비교한 시스템들의 cardinality estimation 정책:
- pgvector: ~33.3% fixed sampling rate
- VBASE: ~50% fixed sampling rate
- DuckDB: 100% (full scan, exact)
- Exqutor proposed: ECQO (HNSW range) + Adaptive Sampling (momentum)

본 연구의 BERN(385) baseline 위치를 위 3개 fixed-rate 와 비교하기 위한 측정.
추가로 BERN(3000) 도 측정 — Exqutor adaptive sampling 의 momentum 운영점 (수천 단위)
과 비교 가능한 sample size.

5개 mode × 5 sel × 5 seed × 100 query = 12,500 cells per dataset.

산출:
    {out_prefix}_{dataset}.parquet — dataset, mode, selectivity, seed, query_id,
        D_target, true_card, est, q_error, sample_size_actual

CLI:
    python3 run_fixed_rate_baselines.py
    python3 run_fixed_rate_baselines.py --datasets DEEP --modes bern_385 bern_3000
    python3 run_fixed_rate_baselines.py --out-prefix rq1_fixed_rate_baselines --n-queries 100

서버 경로: /mnt/hdd0/home/capstone2026/cache/rq3/run_fixed_rate_baselines.py
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import _measure_common as mc  # noqa: E402
from _measure_common import (  # noqa: E402
    DATASETS,
    SEEDS,
    SELECTIVITIES,
    fetch_all_vectors_safe,
    kst,
    save_parquet_meta,
)

# ---------------------------------------------------------------------------
# Mode definitions
# ---------------------------------------------------------------------------
# - sample_frac: total_rows * f → sample budget (pgvector / VBASE / duckdb)
# - sample_size: 고정 budget (BERN baseline 385 / 3000)
# - duckdb (sample_frac=1.0) 은 special case — full scan, est = true_card
MODES: dict[str, dict] = {
    "pgvector_33": {"sample_frac": 1.0 / 3.0, "kind": "fraction"},
    "vbase_50":    {"sample_frac": 0.5,        "kind": "fraction"},
    "duckdb_100":  {"sample_frac": 1.0,        "kind": "exact"},
    "bern_385":    {"sample_size": 385,        "kind": "fixed"},
    "bern_3000":   {"sample_size": 3000,       "kind": "fixed"},
}


def _resolve_sample_size(mode_cfg: dict, total_rows: int) -> int:
    """mode 별 실제 sample size 결정. duckdb 는 total_rows 그대로 (보고용)."""
    if mode_cfg["kind"] == "fraction":
        return max(1, int(round(total_rows * mode_cfg["sample_frac"])))
    if mode_cfg["kind"] == "fixed":
        return int(mode_cfg["sample_size"])
    if mode_cfg["kind"] == "exact":
        return int(total_rows)
    raise ValueError(f"unknown mode kind: {mode_cfg['kind']}")


def _bernoulli_from_full(
    all_vecs: np.ndarray,
    total_rows: int,
    sample_size: int,
    qvec: np.ndarray,
    D: float,
    rng: np.random.Generator,
) -> float:
    """전체 all_vecs (N, dim) 에서 sample_size 개 무작위 추출 후 HT 추정.

    bernoulli_estimate (cluster cache 기반) 와 달리 large fraction (33%/50%) 에서
    cache 부족 문제 회피. sample_size <= total_rows 에서 동작. replace=False.
    """
    n = all_vecs.shape[0]
    s = min(int(sample_size), n)
    if s == 0:
        return float(total_rows)
    idxs = rng.choice(n, size=s, replace=False)
    sub = all_vecs[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return float(hits) * (float(total_rows) / float(s))


def measure_one_mode(
    all_vecs: np.ndarray,
    ds: dict,
    mode_name: str,
    mode_cfg: dict,
    n_queries: int = 100,
) -> list[dict]:
    """단일 mode × dataset 측정. 5 sel × 5 seed × n_queries 셀."""
    total_rows = int(all_vecs.shape[0])
    sample_size = _resolve_sample_size(mode_cfg, total_rows)
    kind = mode_cfg["kind"]

    qp, qs_full, qvecs = mc._load_query_pool(ds)
    print(
        f"[{kst()}]   {mode_name:>12} kind={kind} sample_size={sample_size:,} "
        f"({sample_size / total_rows * 100:.2f}% of {total_rows:,})"
    )

    rows: list[dict] = []
    t_mode = time.time()
    for sel in SELECTIVITIES:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel)) &
            (qs_full["query_id"] < n_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if len(qs_sel) == 0:
            continue
        for seed in SEEDS:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            t0 = time.time()
            qe_list = []
            for _, q in qs_sel.iterrows():
                qid = int(q["query_id"])
                D = float(q["D_target"])
                true_card = int(q["true_cardinality"])
                qvec = qvecs[qid]

                if kind == "exact":
                    # DuckDB full scan: est = true_card (analytic), q_error = 1.0
                    est = float(true_card)
                else:
                    est = _bernoulli_from_full(
                        all_vecs, total_rows, sample_size, qvec, D, rng
                    )

                if est > 0 and true_card > 0:
                    qerr = max(est / true_card, true_card / est)
                else:
                    qerr = None

                rows.append({
                    "dataset": ds["name"],
                    "mode": mode_name,
                    "selectivity": sel,
                    "seed": seed,
                    "query_id": qid,
                    "D_target": D,
                    "true_card": true_card,
                    "est": est,
                    "q_error": qerr,
                    "sample_size_actual": sample_size,
                })
                qe_list.append(qerr if qerr is not None else float("nan"))
            elapsed = time.time() - t0
            valid = sum(1 for q in qe_list if q == q)
            med = float(np.nanmedian(qe_list)) if valid else float("nan")
            print(
                f"[{kst()}]   {ds['name']} {mode_name:>12} s={sel:.2f} seed={seed} "
                f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} med_qe={med:.4f}"
            )
    print(
        f"[{kst()}] {ds['name']} {mode_name:>12}: total {time.time() - t_mode:.1f}s"
    )
    return rows


def main():
    ap = argparse.ArgumentParser(
        description="RQ1 fixed-rate baselines (pgvector / VBASE / DuckDB) + BERN comparison"
    )
    ap.add_argument("--out-prefix", default="rq1_fixed_rate_baselines")
    ap.add_argument(
        "--datasets", nargs="*", default=None,
        help="DATASETS subset (default: 전체). 예: --datasets DEEP SIFT",
    )
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument(
        "--modes", nargs="*", default=list(MODES.keys()),
        help=f"측정할 mode subset. 가능: {list(MODES.keys())}",
    )
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    use_modes = [(m, MODES[m]) for m in args.modes if m in MODES]
    if not use_modes:
        raise SystemExit(f"No valid modes selected: {args.modes}")

    print(f"[{kst()}] === RQ1 fixed-rate baselines (Exqutor 본 논문 비교용) ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")
    print(f"[{kst()}] modes:    {[m for m, _ in use_modes]}")
    print(f"[{kst()}] n_queries={args.n_queries}, sels={SELECTIVITIES}, seeds={SEEDS}")

    t_total = time.time()
    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _km20_sids = fetch_all_vectors_safe(ds)
        total_rows = int(all_vecs.shape[0])
        print(f"[{kst()}]   loaded {total_rows:,} × {all_vecs.shape[1]}d")

        ds_rows: list[dict] = []
        for mode_name, mode_cfg in use_modes:
            rows = measure_one_mode(
                all_vecs, ds, mode_name, mode_cfg, n_queries=args.n_queries
            )
            ds_rows.extend(rows)

        save_parquet_meta(
            ds_rows,
            prefix=f"{args.out_prefix}_{ds['name']}",
            extra_meta={
                "method": "RQ1 fixed-rate baselines (pgvector_33 / vbase_50 / duckdb_100 / bern_385 / bern_3000)",
                "n_queries": args.n_queries,
                "modes": [m for m, _ in use_modes],
                "total_rows": total_rows,
                "vec_dim": int(all_vecs.shape[1]),
                "elapsed_s": round(time.time() - t_total, 1),
            },
        )

    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
