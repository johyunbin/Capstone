#!/usr/bin/env python3
"""
RQ3 #7-Z — Z-order curve 측정 (Hilbert ablation).

run_hilbert.py 와 동일 골격, fit_zorder_mapper / assign_zorder 사용.

가설 H3-Z (vs Hilbert):
  - 만약 Z-order recovery ≈ Hilbert → PCA+quantile 효과가 dominant.
    Hilbert 의 locality 보존이 큰 차이 안 만듦. → 본 연구의 contribution
    narrative 가 "결정론 quantile 분할" 로 단순화될 수 있음.
  - 만약 Z-order recovery 낮음 → Hilbert 의 locality 가 핵심. → 본 연구의
    "Hilbert curve 가 contribution 1순위" 격상 narrative 강화.

사용:
    python3 experiments/code/rq3/run_zorder.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_zorder.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_zorder.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_zorder_meta.json
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
sys.path.insert(0, str(ROOT / "zorder"))

from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from zorder.zorder_curve import (  # noqa: E402
    assign_zorder, cluster_size_summary, fit_zorder_mapper,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #7-Z — Z-order curve 측정 (Hilbert ablation)")
    ap.add_argument("--out-prefix", default="rq3_zorder")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01,
                    help="학습 sample 비율 (default 1%%)")
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--p", type=int, default=10,
                    help="grid order (default 10 → 1024×1024 grid, Hilbert 와 동일)")
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #7-Z — Z-order Curve (Hilbert ablation) ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, "
          f"learn_frac={args.learn_frac}, learn_seed={args.learn_seed}, p={args.p}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _km20_sids = fetch_all_vectors_safe(ds)
        n = len(all_vecs)

        n_learn = max(int(n * args.learn_frac), N_STRATA * 50)
        rng = np.random.default_rng(args.learn_seed)
        learn_idx = rng.choice(n, size=n_learn, replace=False)
        learn_samples = all_vecs[learn_idx]
        print(f"[{kst()}]   fitting Z-order mapper on {n_learn:,} samples (k={N_STRATA}, p={args.p})")
        t_learn = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mapper = fit_zorder_mapper(
                learn_samples, n_strata=N_STRATA, p=args.p, seed=args.learn_seed,
            )
        learn_elapsed = time.time() - t_learn
        evr = mapper.pca.explained_variance_ratio_
        print(f"[{kst()}]   learn elapsed: {learn_elapsed:.1f}s, "
              f"PCA explained_variance_ratio={evr.tolist()}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            stratum_ids = assign_zorder(mapper, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   Z-order quantile bucket sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="zorder",
            all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Z-order Curve (Hilbert ablation)",
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "p": args.p,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
