#!/usr/bin/env python3
"""
RQ3 #7 — E. Hilbert Curve 측정.

hilbert/hilbert_curve.py 의 결정론적 PCA(2) + Hilbert curve + quantile 분할로
stratum_id 부여, _measure_common.py 백엔드로 측정.

흐름:
1. fetch_all_vectors_safe(ds): 전체 vector 회수 (~1M~1.5M rows)
2. learn_frac (default 1%) 로 학습 sample subset
3. fit_hilbert_mapper(): PCA basis + 2D 그리드 + quantile boundary 결정 (~수초)
4. assign_hilbert(): 전체 row 에 stratum_id 부여
5. run_method_measurement(): equal allocation 측정

가설 H3-E: recovery_rate 20~60% (PCA 2D 가 cluster 구조 일부 반영, contribution 후보).

사용:
    python3 experiments/code/rq3/run_hilbert.py
    # 서버:
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_hilbert.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_hilbert.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq3_hilbert_meta.json

예상 시간: ~30분 (DEEP fetch 5m + SIFT fetch 7m + 학습 5s × 2 + 측정 25m)
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
sys.path.insert(0, str(ROOT / "hilbert"))

from _measure_common import (  # noqa: E402
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from hilbert.hilbert_curve import (  # noqa: E402
    assign_hilbert, cluster_size_summary, fit_hilbert_mapper,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #7 — E. Hilbert Curve 측정")
    ap.add_argument("--out-prefix", default="rq3_hilbert")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01,
                    help="학습 sample 비율 (default 1%%, ~10K~15K rows for PCA + quantile)")
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--p", type=int, default=10,
                    help="Hilbert order (default 10 → 1024×1024 grid)")
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #7 — E. Hilbert Curve ===")
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
        print(f"[{kst()}]   fitting Hilbert mapper on {n_learn:,} samples (k={N_STRATA}, p={args.p})")
        t_learn = time.time()
        with warnings.catch_warnings():
            # 일부 toy 데이터에서 sklearn PCA 의 RuntimeWarning 발생 가능
            # (실제 DEEP/SIFT 에선 안 발생). 안전하게 suppress.
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mapper = fit_hilbert_mapper(
                learn_samples, n_strata=N_STRATA, p=args.p, seed=args.learn_seed,
            )
        learn_elapsed = time.time() - t_learn
        evr = mapper.pca.explained_variance_ratio_
        print(f"[{kst()}]   learn elapsed: {learn_elapsed:.1f}s, "
              f"PCA explained_variance_ratio={evr.tolist()}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            stratum_ids = assign_hilbert(mapper, all_vecs)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   Hilbert quantile bucket sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f} (quantile → 균등 가까움)"
        )

        rows = run_method_measurement(
            method_name="hilbert",
            all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Hilbert Curve (E)",
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
