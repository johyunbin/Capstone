#!/usr/bin/env python3
"""run_kmeans_pp.py — RQ3 distribution-agnostic method (full KMeans++).

sklearn.cluster.KMeans (n_init=10, init='k-means++', max_iter=300) on a 5%
sample (KMeans++ does not scale to full N like MiniBatch). Comparison
baseline against MiniBatchKMeans to quantify the cost of cheaper updates.
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
                learn_frac: float = 0.05) -> np.ndarray:
    from sklearn.cluster import KMeans
    n = len(all_vecs)

    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    rng = np.random.default_rng(seed)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    learn = all_vecs[learn_idx]

    print(f"[{kst()}]   KMeans++ (n_init=10, max_iter=300) on {n_learn:,} samples "
          f"(k={N_STRATA})")
    km = KMeans(n_clusters=N_STRATA, init="k-means++", n_init=10,
                max_iter=300, random_state=seed, algorithm="lloyd")
    km.fit(learn)
    print(f"[{kst()}]   KMeans++ inertia={km.inertia_:.2f}, n_iter_={km.n_iter_}")

    chunk = 200_000
    out = np.empty(n, dtype=np.int32)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        out[i:j] = km.predict(all_vecs[i:j]).astype(np.int32)
    return out


def main():
    ap = argparse.ArgumentParser(description="RQ3 — Full KMeans++")
    ap.add_argument("--out-prefix", default="rq3_kmeans_pp")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--learn-frac", type=float, default=0.05)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — Full KMeans++ (k={N_STRATA}) ===")
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
                               learn_frac=args.learn_frac)
        print(f"[{kst()}]   fit_predict {time.time() - t:.1f}s, "
              f"unique={len(np.unique(sids))}")

        rows = run_method_measurement(
            method_name="kmeans_pp", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Full KMeans++ (sklearn.cluster.KMeans n_init=10)",
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
