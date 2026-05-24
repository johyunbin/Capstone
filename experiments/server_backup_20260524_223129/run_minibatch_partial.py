#!/usr/bin/env python3
"""
RQ3 #8b — MiniBatch K-means online (partial_fit) variant 측정.

run_minibatch.py 와 동일 골격, 학습만 partial_fit 으로 점진. 측정 후 #8 (batch fit)
대비 recovery loss 정량 → "OLTP / streaming 환경에서 batch 재학습 없이 운영 가능한지"
정량 답변.

가설 H3-Fp: chunk-fit 이 batch-fit 대비 recovery 5~15%p loss. loss 가 작으면
production 의 partial_fit 채택 정당화.

사용:
    python3 experiments/code/rq3/run_minibatch_partial.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_minibatch_partial.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_minibatch_partial.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_minibatch_partial_meta.json
        meta 에 drift_summary 포함 → 학습 안정성 sanity check.
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
from offline_simple.minibatch_partial import (  # noqa: E402
    assign_minibatch, cluster_size_summary, drift_summary, train_minibatch_partial,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #8b — MiniBatch K-means online")
    ap.add_argument("--out-prefix", default="rq3_minibatch_partial")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--chunk-size", type=int, default=1000)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #8b — MiniBatch K-means online (partial_fit) ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, "
          f"chunk_size={args.chunk_size}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    drift_per_ds: dict = {}
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _ = fetch_all_vectors_safe(ds)
        n = len(all_vecs)

        n_learn = max(int(n * args.learn_frac), N_STRATA * 50)
        rng = np.random.default_rng(args.learn_seed)
        learn_idx = rng.choice(n, size=n_learn, replace=False)
        learn_samples = all_vecs[learn_idx]
        print(f"[{kst()}]   partial_fit on {n_learn:,} samples "
              f"(chunk_size={args.chunk_size}, ~{n_learn // args.chunk_size} chunks)")

        t_learn = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            result = train_minibatch_partial(
                learn_samples, n_clusters=N_STRATA,
                chunk_size=args.chunk_size, random_state=args.learn_seed,
            )
        learn_elapsed = time.time() - t_learn
        drift = drift_summary(result)
        drift_per_ds[ds["name"]] = drift
        print(f"[{kst()}]   learn elapsed: {learn_elapsed:.1f}s, "
              f"n_chunks={drift['n_chunks']}, shift_decay={drift['shift_decay_ratio']:.3f}, "
              f"inertia: {drift['init_inertia']:.1f} → {drift['final_inertia']:.1f}")

        stratum_ids = assign_minibatch(result, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   partial_fit cluster sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="minibatch_partial",
            all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "MiniBatch K-means online (partial_fit)",
            "chunk_size": args.chunk_size,
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "drift_per_dataset": drift_per_ds,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
