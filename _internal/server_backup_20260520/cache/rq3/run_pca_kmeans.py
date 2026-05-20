#!/usr/bin/env python3
"""run_pca_kmeans.py — RQ3 (PCA dim-reduce + MiniBatchKMeans).

Reduce to dim/4 (capped at 32) via PCA fit on 1% sample, then
MiniBatchKMeans K=N_STRATA on the reduced space. Tests whether dim-reduction
preserves enough structure for the clusterer.
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
                learn_frac: float = 0.01) -> np.ndarray:
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.decomposition import PCA

    n, d = all_vecs.shape
    pca_dim = max(min(d // 4, 32), 4)

    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    rng = np.random.default_rng(seed)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    learn = all_vecs[learn_idx]

    print(f"[{kst()}]   PCA fit (dim {d} → {pca_dim}) on {n_learn:,} samples")
    pca = PCA(n_components=pca_dim, random_state=seed)
    learn_proj = pca.fit_transform(learn)
    evr = pca.explained_variance_ratio_.sum()
    print(f"[{kst()}]   PCA explained_variance_total={evr:.4f}")

    print(f"[{kst()}]   MiniBatchKMeans K={N_STRATA} on PCA-{pca_dim} space")
    km = MiniBatchKMeans(n_clusters=N_STRATA, random_state=seed,
                         n_init=10, max_iter=200, batch_size=4096)
    km.fit(learn_proj)

    # Predict in chunks to avoid materialising the full reduced matrix.
    chunk = 200_000
    out = np.empty(n, dtype=np.int32)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = all_vecs[i:j]
        proj = pca.transform(block)
        out[i:j] = km.predict(proj).astype(np.int32)
    return out


def main():
    ap = argparse.ArgumentParser(description="RQ3 — PCA + MiniBatchKMeans")
    ap.add_argument("--out-prefix", default="rq3_pca_kmeans")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — PCA + MiniBatchKMeans (k={N_STRATA}) ===")
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
            method_name="pca_kmeans", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "PCA dim/4 + MiniBatchKMeans",
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
