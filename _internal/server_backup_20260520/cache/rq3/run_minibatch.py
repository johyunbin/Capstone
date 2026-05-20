#!/usr/bin/env python3
"""
RQ3 #8 — F. MiniBatch K-means 측정.

P2 commit (39cfc3a) 의 offline_simple/minibatch_kmeans.py 에서 학습/부여 로직 import,
_measure_common.py 의 측정 백엔드로 5 sel × 5 seed × 100 query × 2 dataset 산출.

흐름:
1. fetch_all_vectors_safe(ds): 전체 vector 회수 (~1M~1.5M rows)
2. learn_frac (default 1%) 로 학습 sample subset
3. train_minibatch_kmeans(): MiniBatch K-means K=20 학습 (~수초)
4. assign_minibatch(): 전체 row 에 stratum_id 부여
5. run_method_measurement(): equal allocation 측정

가설 H3-F: recovery_rate 75~95% (MiniBatch 가 KM20 oracle 의 75% 이상 회수).

사용:
    python3 experiments/code/rq3/run_minibatch.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_minibatch.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_minibatch.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_minibatch_meta.json

예상 시간: ~1h (DEEP fetch 5m + SIFT fetch 7m + 학습 30s × 2 + 측정 30m)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "offline_simple"))

from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from offline_simple.minibatch_kmeans import (  # noqa: E402
    assign_minibatch, cluster_size_summary, train_minibatch_kmeans,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #8 — F. MiniBatch K-means 측정")
    ap.add_argument("--out-prefix", default="rq3_minibatch")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01,
                    help="학습 sample 비율 (default 1%%, ~10K~15K rows)")
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #8 — F. MiniBatch K-means ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, "
          f"learn_frac={args.learn_frac}, learn_seed={args.learn_seed}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _km20_sids = fetch_all_vectors_safe(ds)
        n = len(all_vecs)

        n_learn = max(int(n * args.learn_frac), N_STRATA * 50)  # 안전 하한
        rng = np.random.default_rng(args.learn_seed)
        learn_idx = rng.choice(n, size=n_learn, replace=False)
        learn_samples = all_vecs[learn_idx]
        print(f"[{kst()}]   training MiniBatch K-means on {n_learn:,} samples (k={N_STRATA})")
        t_learn = time.time()
        model = train_minibatch_kmeans(
            learn_samples, n_clusters=N_STRATA, random_state=args.learn_seed,
        )
        learn_elapsed = time.time() - t_learn
        print(f"[{kst()}]   learn elapsed: {learn_elapsed:.1f}s, inertia={model.inertia_:.2f}")

        stratum_ids = assign_minibatch(model, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   MiniBatch cluster sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="minibatch",
            all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "MiniBatch K-means (F)",
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
