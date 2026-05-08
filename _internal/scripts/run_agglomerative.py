#!/usr/bin/env python3
"""run_agglomerative.py — RQ3 distribution-agnostic method (Agglomerative Ward).

AgglomerativeClustering(n_clusters=N_STRATA, linkage='ward'). Fits on a 50K
sample (full N intractable for hierarchical), then per-cluster centroid is
computed and the rest of the rows are assigned by nearest centroid.
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


def _assign_nearest_centroid(all_vecs: np.ndarray, centroids: np.ndarray,
                             chunk: int = 50000) -> np.ndarray:
    n = len(all_vecs)
    out = np.empty(n, dtype=np.int32)
    cs = (centroids ** 2).sum(axis=1)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = all_vecs[i:j]
        ds = (block ** 2).sum(axis=1, keepdims=True) + cs[None, :] - 2.0 * block @ centroids.T
        out[i:j] = np.argmin(ds, axis=1).astype(np.int32)
    return out


def fit_predict(all_vecs: np.ndarray, seed: int = 42,
                fit_size: int = 50000) -> np.ndarray:
    from sklearn.cluster import AgglomerativeClustering
    n = len(all_vecs)
    sub_n = min(n, fit_size)
    rng = np.random.default_rng(seed)
    if n > sub_n:
        idx = rng.choice(n, size=sub_n, replace=False)
        sub = all_vecs[idx]
    else:
        sub = all_vecs
    print(f"[{kst()}]   Agglomerative(ward) fit on {len(sub):,} samples (k={N_STRATA})")
    ag = AgglomerativeClustering(n_clusters=N_STRATA, linkage="ward")
    sub_labels = ag.fit_predict(sub).astype(np.int32)

    uniq = np.unique(sub_labels)
    centroids = np.zeros((len(uniq), all_vecs.shape[1]), dtype=np.float64)
    for new, old in enumerate(uniq.tolist()):
        centroids[new] = sub[sub_labels == old].mean(axis=0)

    return _assign_nearest_centroid(all_vecs, centroids.astype(np.float32))


def main():
    ap = argparse.ArgumentParser(description="RQ3 — Agglomerative (Ward)")
    ap.add_argument("--out-prefix", default="rq3_agglomerative")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--fit-size", type=int, default=50000)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — Agglomerative (Ward linkage) ===")
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
                               fit_size=args.fit_size)
        print(f"[{kst()}]   fit_predict {time.time() - t:.1f}s, "
              f"unique={len(np.unique(sids))}")

        rows = run_method_measurement(
            method_name="agglomerative", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Agglomerative (Ward linkage)",
            "fit_size": args.fit_size,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
