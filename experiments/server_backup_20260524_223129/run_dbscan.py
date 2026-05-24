#!/usr/bin/env python3
"""run_dbscan.py — RQ3 distribution-agnostic method (DBSCAN density-based).

DBSCAN with eps auto-tuned via knee detection on k=5 NN distance,
min_samples=5. Noise points (-1) are mapped to the nearest cluster centroid.
For large N, fits on a min(N, 50000) sample, then assigns the rest by
nearest centroid (centroids = per-cluster mean of fitted sample points).
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


def _knee_eps(samples: np.ndarray, k: int = 5, seed: int = 42) -> float:
    """Estimate eps from the knee of sorted k-NN distances (k=5 default)."""
    from sklearn.neighbors import NearestNeighbors
    n = len(samples)
    sub_n = min(n, 20000)
    rng = np.random.default_rng(seed)
    if n > sub_n:
        idx = rng.choice(n, size=sub_n, replace=False)
        sub = samples[idx]
    else:
        sub = samples
    nn = NearestNeighbors(n_neighbors=k + 1, n_jobs=-1)
    nn.fit(sub)
    dists, _ = nn.kneighbors(sub)
    kth = np.sort(dists[:, -1])
    # knee = max distance from chord between first/last point
    x = np.arange(len(kth), dtype=np.float64)
    y = kth.astype(np.float64)
    x0, y0 = x[0], y[0]
    x1, y1 = x[-1], y[-1]
    denom = max(np.hypot(x1 - x0, y1 - y0), 1e-12)
    d = np.abs((y1 - y0) * x - (x1 - x0) * y + x1 * y0 - y1 * x0) / denom
    knee_idx = int(np.argmax(d))
    return float(kth[knee_idx])


def _assign_nearest_centroid(all_vecs: np.ndarray, centroids: np.ndarray,
                             chunk: int = 50000) -> np.ndarray:
    """Vectorised batched argmin distance to centroids."""
    n = len(all_vecs)
    out = np.empty(n, dtype=np.int32)
    cn = centroids.shape[0]
    cs = (centroids ** 2).sum(axis=1)  # (cn,)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = all_vecs[i:j]
        # ||a||^2 + ||c||^2 - 2 a·c
        ds = (block ** 2).sum(axis=1, keepdims=True) + cs[None, :] - 2.0 * block @ centroids.T
        out[i:j] = np.argmin(ds, axis=1).astype(np.int32)
    return out


def fit_predict(all_vecs: np.ndarray, seed: int = 42) -> np.ndarray:
    """DBSCAN stratum assignment. Returns int32 array of length N."""
    from sklearn.cluster import DBSCAN
    n = len(all_vecs)
    sub_n = min(n, 50000)
    rng = np.random.default_rng(seed)
    if n > sub_n:
        sub_idx = rng.choice(n, size=sub_n, replace=False)
        sub = all_vecs[sub_idx]
    else:
        sub = all_vecs

    eps = _knee_eps(sub, k=5, seed=seed)
    print(f"[{kst()}]   DBSCAN auto-tuned eps={eps:.4f} on {len(sub):,} samples")
    db = DBSCAN(eps=eps, min_samples=5, n_jobs=-1)
    labels = db.fit_predict(sub).astype(np.int32)
    uniq = np.unique(labels[labels >= 0])
    n_found = len(uniq)
    print(f"[{kst()}]   DBSCAN found {n_found} dense clusters "
          f"(noise={int((labels == -1).sum())}/{len(sub)})")

    # Build centroids: per-cluster mean of non-noise sample points.
    # If DBSCAN finds fewer or more than N_STRATA clusters, retain all clusters
    # and remap to dense ids 0..K-1; downstream estimators don't require K=N_STRATA.
    if n_found == 0:
        # Degenerate: everything noise → fall back to a single stratum.
        print(f"[{kst()}]   WARN: DBSCAN produced no dense cluster → fallback single stratum")
        return np.zeros(n, dtype=np.int32)

    label_remap = {old: new for new, old in enumerate(uniq.tolist())}
    centroids = np.zeros((n_found, all_vecs.shape[1]), dtype=np.float64)
    for old, new in label_remap.items():
        centroids[new] = sub[labels == old].mean(axis=0)

    # Cap centroids to top-N_STRATA largest clusters if too many.
    if n_found > N_STRATA:
        sizes = np.array([(labels == old).sum() for old in uniq])
        keep = np.argsort(-sizes)[:N_STRATA]
        keep_set = set(int(uniq[i]) for i in keep)
        new_uniq = np.array(sorted(keep_set), dtype=np.int64)
        label_remap = {int(old): new for new, old in enumerate(new_uniq.tolist())}
        centroids = np.zeros((len(new_uniq), all_vecs.shape[1]), dtype=np.float64)
        for old, new in label_remap.items():
            centroids[new] = sub[labels == old].mean(axis=0)
        print(f"[{kst()}]   DBSCAN capped to top-{N_STRATA} clusters by size")

    # Assign EVERY row in all_vecs to nearest centroid (handles noise + scaling).
    return _assign_nearest_centroid(all_vecs, centroids.astype(np.float32))


def main():
    ap = argparse.ArgumentParser(description="RQ3 — DBSCAN density-based")
    ap.add_argument("--out-prefix", default="rq3_dbscan")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — DBSCAN ===")
    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _ = fetch_all_vectors_safe(ds)
        t = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sids = fit_predict(all_vecs, seed=args.learn_seed)
        print(f"[{kst()}]   fit_predict {time.time() - t:.1f}s, "
              f"unique={len(np.unique(sids))}")

        rows = run_method_measurement(
            method_name="dbscan", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "DBSCAN density-based clustering",
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
