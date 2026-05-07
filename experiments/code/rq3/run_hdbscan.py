#!/usr/bin/env python3
"""
RQ3 #17 — HDBSCAN partition 측정 (density-based hierarchical clustering).

HDBSCAN cluster 수 ≠ N_STRATA 가능 → centroid+KMeans 로 N_STRATA 보정.

가설 H3-HD: SIFT (cluster 더 명확한 skewed 분포) 에서 KMeans 와 다른 결과 → 비교 ablation.
"""
from __future__ import annotations

import argparse
import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from hdbscan.hdbscan_partition import (  # noqa: E402
    assign_hdbscan, cluster_size_summary, fit_hdbscan,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #17 — HDBSCAN")
    ap.add_argument("--out-prefix", default="rq3_hdbscan")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--min-cluster-size", type=int, default=50)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #17 — HDBSCAN ===")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _ = fetch_all_vectors_safe(ds)
        n = len(all_vecs)

        n_learn = max(int(n * args.learn_frac), N_STRATA * 50)
        rng = np.random.default_rng(args.learn_seed)
        learn_idx = rng.choice(n, size=n_learn, replace=False)
        learn_samples = all_vecs[learn_idx]
        print(f"[{kst()}]   HDBSCAN fit on {n_learn:,} samples (k={N_STRATA}, min_cluster={args.min_cluster_size})")

        t_learn = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mapper = fit_hdbscan(
                learn_samples, n_strata=N_STRATA,
                min_cluster_size=args.min_cluster_size,
                seed=args.learn_seed,
            )
        learn_elapsed = time.time() - t_learn
        print(f"[{kst()}]   HDBSCAN fit elapsed: {learn_elapsed:.1f}s")

        stratum_ids = assign_hdbscan(mapper, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   HDBSCAN cluster sizes: min={summary['min']}, "
            f"max={summary['max']}, max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="hdbscan", all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "HDBSCAN (density hierarchical)",
            "min_cluster_size": args.min_cluster_size,
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
