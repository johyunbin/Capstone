#!/usr/bin/env python3
"""run_optics.py — RQ3 distribution-agnostic method (OPTICS density-based).

OPTICS with min_samples=10, xi=0.05. Fits on min(N, 50000) sample (full N
infeasible). Noise points map to nearest cluster centroid; full N then
assigned by nearest centroid as well.
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
                min_samples: int = 10, xi: float = 0.05) -> np.ndarray:
    from sklearn.cluster import OPTICS
    n = len(all_vecs)
    sub_n = min(n, 50000)
    rng = np.random.default_rng(seed)
    if n > sub_n:
        idx = rng.choice(n, size=sub_n, replace=False)
        sub = all_vecs[idx]
    else:
        sub = all_vecs
    print(f"[{kst()}]   OPTICS fit on {len(sub):,} samples "
          f"(min_samples={min_samples}, xi={xi})")
    op = OPTICS(min_samples=min_samples, xi=xi, n_jobs=-1, cluster_method="xi")
    labels = op.fit_predict(sub).astype(np.int32)
    uniq = np.unique(labels[labels >= 0])
    n_found = len(uniq)
    print(f"[{kst()}]   OPTICS found {n_found} clusters "
          f"(noise={int((labels == -1).sum())}/{len(sub)})")

    if n_found == 0:
        print(f"[{kst()}]   WARN: OPTICS produced no cluster → fallback single stratum")
        return np.zeros(n, dtype=np.int32)

    # Cap to top-N_STRATA clusters by size.
    if n_found > N_STRATA:
        sizes = np.array([(labels == old).sum() for old in uniq])
        keep = np.argsort(-sizes)[:N_STRATA]
        uniq = np.sort(uniq[keep])
        n_found = len(uniq)

    centroids = np.zeros((n_found, all_vecs.shape[1]), dtype=np.float64)
    for new, old in enumerate(uniq.tolist()):
        centroids[new] = sub[labels == old].mean(axis=0)

    return _assign_nearest_centroid(all_vecs, centroids.astype(np.float32))


def main():
    ap = argparse.ArgumentParser(description="RQ3 — OPTICS density-based")
    ap.add_argument("--out-prefix", default="rq3_optics")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--min-samples", type=int, default=10)
    ap.add_argument("--xi", type=float, default=0.05)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — OPTICS ===")
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
                               min_samples=args.min_samples, xi=args.xi)
        print(f"[{kst()}]   fit_predict {time.time() - t:.1f}s, "
              f"unique={len(np.unique(sids))}")

        rows = run_method_measurement(
            method_name="optics", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "OPTICS density-based clustering",
            "min_samples": args.min_samples,
            "xi": args.xi,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
