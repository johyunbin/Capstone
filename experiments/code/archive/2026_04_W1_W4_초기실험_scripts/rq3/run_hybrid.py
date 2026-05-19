#!/usr/bin/env python3
"""
RQ3 #12 — MiniBatch + Hilbert hybrid 측정.

run_hilbert.py / run_minibatch.py 와 동일 골격, hybrid stratification 사용.

가설 H3-FH:
  - hybrid 가 단일 method (MiniBatch -1.88%, Hilbert -1.78%) 보다 strict 우수면
    → 두 method 가 직교적 정보 (cluster + size) 를 결합 가능.
  - 비슷하면 → 정보 redundancy.
  - 더 나쁘면 → cluster 크기 변동 자체가 estimator 도움 (Neyman 처럼). RQ2 의
    Anti-Neyman 부정 결과와 대조.

사용:
    python3 experiments/code/rq3/run_hybrid.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_hybrid.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_hybrid.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_hybrid_meta.json
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
from hybrid.minibatch_hilbert import (  # noqa: E402
    assign_hybrid, cluster_size_summary, fit_hybrid_mapper,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #12 — MiniBatch + Hilbert hybrid")
    ap.add_argument("--out-prefix", default="rq3_hybrid")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--k-outer", type=int, default=5)
    ap.add_argument("--k-inner", type=int, default=4)
    ap.add_argument("--p", type=int, default=10)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #12 — MiniBatch + Hilbert hybrid ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, "
          f"k_outer={args.k_outer}, k_inner={args.k_inner}, p={args.p}")
    if args.k_outer * args.k_inner != N_STRATA:
        print(f"⚠️ k_outer*k_inner ({args.k_outer*args.k_inner}) ≠ N_STRATA ({N_STRATA}) — "
              "측정 지장은 없으나 baseline 비교 정합성 X")

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
        print(f"[{kst()}]   fitting hybrid ({args.k_outer}×{args.k_inner}) on "
              f"{n_learn:,} samples")

        t_learn = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mapper = fit_hybrid_mapper(
                learn_samples, k_outer=args.k_outer, k_inner=args.k_inner,
                p=args.p, seed=args.learn_seed,
            )
        learn_elapsed = time.time() - t_learn
        print(f"[{kst()}]   learn elapsed: {learn_elapsed:.1f}s, "
              f"outer inertia={mapper.outer_model.inertia_:.2f}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            stratum_ids = assign_hybrid(mapper, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   hybrid bucket sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="hybrid",
            all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "MiniBatch + Hilbert hybrid",
            "k_outer": args.k_outer,
            "k_inner": args.k_inner,
            "p": args.p,
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
