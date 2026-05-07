#!/usr/bin/env python3
"""
RQ3 #14 — Product Quantization 측정 (FAISS / 산업 표준).

vector DB 의 표준 indexing 기법. M sub-vector × K_sub centroid → composite code →
N_strata 로 mod truncate.

가설 H3-PQ:
  - PQ < MiniBatch (sub-vector 독립 학습 → cross-axis 정보 손실)
  - PQ > RANDOM20 (sub-vector 별 cluster 구조 보존)
  - 산업 기준 비교 narrative 강화 (5/27 발표 ready)

사용:
    python3 experiments/code/rq3/run_pq.py
    python3 experiments/code/rq3/run_pq.py --m 4   # 4 sub-vector
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
from pq.product_quantization import (  # noqa: E402
    assign_pq, cluster_size_summary, fit_pq_mapper,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #14 — Product Quantization")
    ap.add_argument("--out-prefix", default="rq3_pq")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--m", type=int, default=2,
                    help="sub-vector 수 (default 2 → DEEP 48d, SIFT 64d each)")
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #14 — Product Quantization (m={args.m}) ===")

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
        print(f"[{kst()}]   fitting PQ (m={args.m}) on {n_learn:,} samples")

        t_learn = time.time()
        mapper = fit_pq_mapper(
            learn_samples, n_strata=N_STRATA, m=args.m, seed=args.learn_seed,
        )
        learn_elapsed = time.time() - t_learn
        print(f"[{kst()}]   learn elapsed: {learn_elapsed:.1f}s, "
              f"sub_dim={mapper.sub_dim}, k_sub={mapper.k_sub}")

        stratum_ids = assign_pq(mapper, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   PQ stratum sizes: min={summary['min']}, "
            f"max={summary['max']}, max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="pq", all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Product Quantization (FAISS-style)",
            "m": args.m,
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
