#!/usr/bin/env python3
"""
RQ3 baseline — KM20 oracle: fetch_all_vectors_safe 가 반환하는 사전 학습된 KM20 cluster id.

용도: Recovery Rate 의 분자 상한.

    recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20)

KM20 stratum_id 는 _measure_common.fetch_all_vectors_safe() 가 이미 반환 (cache/rq1/.../strata.csv 사전 학습본).

사용:
    python3 experiments/code/rq3/run_km20.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_km20.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_km20.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_km20_meta.json
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 KM20 oracle baseline 측정")
    ap.add_argument("--out-prefix", default="rq3_km20")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 baseline — KM20 oracle (사전 학습된 K-means K=20) ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, km20_sids = fetch_all_vectors_safe(ds)
        counts = np.bincount(km20_sids, minlength=N_STRATA)
        print(
            f"[{kst()}]   KM20 cluster: min={counts.min()}, max={counts.max()}, "
            f"mean={counts.mean():.0f}, ratio={counts.max() / max(counts.min(), 1):.2f}"
        )

        rows = run_method_measurement(
            method_name="km20",
            all_vecs=all_vecs, stratum_ids=km20_sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "KM20 oracle (pre-trained)",
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
