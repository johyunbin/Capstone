#!/usr/bin/env python3
"""
RQ3 #7-P — PCA-1D quantile 측정 (Hilbert/Z-order ablation 의 *최상위*).

run_hilbert.py / run_zorder.py 와 동일 골격, fit_pca1d_mapper / assign_pca1d 사용.
가장 단순한 stratification — PCA 1D + quantile (curve X).

Ablation ladder narrative 의 정량 검증:
    BERN < RANDOM20 < PCA-1D < Z-order < Hilbert < MiniBatch < KM20 oracle

만약 PCA-1D ≈ Hilbert → curve 가 가치 적음, PCA 가 dominant.
만약 PCA-1D ≪ Hilbert → curve 의 locality 가 본질.

사용:
    python3 experiments/code/rq3/run_pca1d.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_pca1d.py
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
from pca1d.pca1d_quantile import (  # noqa: E402
    assign_pca1d, cluster_size_summary, fit_pca1d_mapper,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #7-P — PCA-1D quantile 측정")
    ap.add_argument("--out-prefix", default="rq3_pca1d")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #7-P — PCA-1D Quantile (Hilbert ablation 최상위) ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, "
          f"learn_frac={args.learn_frac}")

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
        print(f"[{kst()}]   fitting PCA-1D on {n_learn:,} samples (k={N_STRATA})")

        t_learn = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mapper = fit_pca1d_mapper(learn_samples, n_strata=N_STRATA, seed=args.learn_seed)
        evr1 = float(mapper.pca.explained_variance_ratio_[0])
        learn_elapsed = time.time() - t_learn
        print(f"[{kst()}]   learn elapsed: {learn_elapsed:.1f}s, "
              f"PC1 explained_variance={evr1:.4f}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            stratum_ids = assign_pca1d(mapper, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   PCA-1D quantile bucket sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="pca1d", all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "PCA-1D Quantile (Hilbert ablation 최상위)",
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
