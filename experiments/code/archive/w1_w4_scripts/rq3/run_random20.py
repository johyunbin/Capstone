#!/usr/bin/env python3
"""
RQ3 baseline — RANDOM20: 무작위 K=20 분할.

용도: Recovery Rate 의 분모 (KM20 oracle ↔ RANDOM20 의 격차) 계산용.

    recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20)

stratum_id 부여 알고리즘:
- 전체 row 에 np.random.default_rng(seed).integers(0, 20, size=N) 로 무작위 부여
- KM20 oracle 의 cluster 를 무시하고 진정 random partition (공간 인식 X)
- 측정 seed 와 분리된 별도 seed 로 1회 부여 (reproducible)

사용:
    python3 experiments/code/rq3/run_random20.py
    # 또는 서버에서:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_random20.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_random20.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_random20_meta.json

예상 시간: ~10분 (DEEP+SIFT, 5 sel × 5 seed × 100 query, BERN+equal 2 mode)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

# 같은 디렉토리의 _measure_common 에 의존
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)


def assign_random20(n_rows: int, seed: int = 42, n_strata: int = N_STRATA) -> np.ndarray:
    """전체 row 에 무작위 stratum_id (0~K-1) 부여. seed 고정 → reproducible."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_strata, size=n_rows).astype(np.int32)


def main():
    ap = argparse.ArgumentParser(description="RQ3 RANDOM20 baseline 측정")
    ap.add_argument("--out-prefix", default="rq3_random20")
    ap.add_argument("--datasets", nargs="*", default=None,
                    help="DEEP / SIFT — None 이면 둘 다")
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--partition-seed", type=int, default=42,
                    help="RANDOM20 partition 부여 seed (측정 seed 와 별개)")
    ap.add_argument("--include-bernoulli", action="store_true",
                    help="BERN baseline 도 동시 측정 (이미 RQ2 에서 측정됐으면 X)")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 baseline — RANDOM20 (무작위 K=20 분할) ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, "
          f"partition_seed={args.partition_seed}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _km20_sids = fetch_all_vectors_safe(ds)

        random20_sids = assign_random20(
            n_rows=len(all_vecs), seed=args.partition_seed,
        )
        counts = np.bincount(random20_sids, minlength=N_STRATA)
        print(
            f"[{kst()}]   RANDOM20 partition: min={counts.min()}, max={counts.max()}, "
            f"mean={counts.mean():.0f}, ratio={counts.max() / max(counts.min(), 1):.2f}"
        )

        rows = run_method_measurement(
            method_name="random20",
            all_vecs=all_vecs, stratum_ids=random20_sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "RANDOM20",
            "partition_seed": args.partition_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
