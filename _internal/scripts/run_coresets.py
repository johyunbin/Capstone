#!/usr/bin/env python3
"""run_coresets.py — RQ3 distribution-agnostic method (Coreset KMeans).

Coreset construction: random uniform sample of K*200 weighted points (1%
random core sample, capped to K*200 for tractability). Run weighted KMeans
K=N_STRATA on the coreset, then predict full N by nearest-centroid.
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


def fit_predict(all_vecs: np.ndarray, seed: int = 42,
                core_frac: float = 0.01) -> np.ndarray:
    from sklearn.cluster import KMeans
    n = len(all_vecs)

    target_size = N_STRATA * 200
    n_core = min(max(int(n * core_frac), target_size), n)
    rng = np.random.default_rng(seed)
    core_idx = rng.choice(n, size=n_core, replace=False)
    core = all_vecs[core_idx]
    # Uniform weights for a random uniform coreset (each point covers n/n_core
    # points in expectation under uniform sampling).
    weights = np.full(n_core, n / n_core, dtype=np.float64)

    print(f"[{kst()}]   Coreset KMeans (k={N_STRATA}) on {n_core:,} weighted points "
          f"({core_frac*100:.1f}% random sample, w_mean={weights.mean():.2f})")
    km = KMeans(n_clusters=N_STRATA, init="k-means++", n_init=10,
                max_iter=300, random_state=seed, algorithm="lloyd")
    km.fit(core, sample_weight=weights)
    print(f"[{kst()}]   coreset inertia={km.inertia_:.2f}, n_iter={km.n_iter_}")

    # Assign full N by nearest centroid via km.predict().
    chunk = 200_000
    out = np.empty(n, dtype=np.int32)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        out[i:j] = km.predict(all_vecs[i:j]).astype(np.int32)
    return out


def main():
    ap = argparse.ArgumentParser(description="RQ3 — Coreset KMeans")
    ap.add_argument("--out-prefix", default="rq3_coresets")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--core-frac", type=float, default=0.01)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — Coreset KMeans (k={N_STRATA}) ===")
    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _ = fetch_all_vectors_safe(ds)
        t = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sids = fit_predict(all_vecs, seed=args.learn_seed,
                               core_frac=args.core_frac)
        print(f"[{kst()}]   fit_predict {time.time() - t:.1f}s, "
              f"unique={len(np.unique(sids))}")

        rows = run_method_measurement(
            method_name="coresets", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Coreset KMeans (uniform random core, weighted KMeans)",
            "core_frac": args.core_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
