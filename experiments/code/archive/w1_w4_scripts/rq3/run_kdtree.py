#!/usr/bin/env python3
"""
RQ3 #13 — KD-tree partition 측정 (tree paradigm).

다른 paradigm (tree-based) 의 비교 baseline. 재귀 axis-aligned median split 으로
20 leaf 생성, 각 leaf 가 stratum.

사용:
    python3 experiments/code/rq3/run_kdtree.py
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from kdtree.kdtree_partition import (  # noqa: E402
    assign_kdtree, cluster_size_summary, fit_kdtree_partition,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #13 — KD-tree partition")
    ap.add_argument("--out-prefix", default="rq3_kdtree")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #13 — KD-tree Partition ===")

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
        print(f"[{kst()}]   building KD-tree on {n_learn:,} samples (k={N_STRATA})")

        t_learn = time.time()
        mapper = fit_kdtree_partition(learn_samples, n_strata=N_STRATA, seed=args.learn_seed)
        learn_elapsed = time.time() - t_learn
        print(f"[{kst()}]   build elapsed: {learn_elapsed:.1f}s")

        t_assign = time.time()
        stratum_ids = assign_kdtree(mapper, all_vecs)
        assign_elapsed = time.time() - t_assign
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(f"[{kst()}]   assign elapsed: {assign_elapsed:.1f}s")
        print(
            f"[{kst()}]   KD-tree leaf sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="kdtree", all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "KD-tree Partition (tree paradigm)",
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
