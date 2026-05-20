#!/usr/bin/env python3
"""run_hierarchical_kmeans.py — RQ3 (2-level KMeans hierarchy).

Outer K=4 MiniBatchKMeans over a 1% sample. Within each outer cluster,
inner K=5 MiniBatchKMeans → total 4×5 = 20 leaf strata. Outer model assigns
all points to outer; inner per-bucket model maps to leaf id (outer*5 + inner).
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

OUTER_K = 4
INNER_K = 5  # 4 * 5 == N_STRATA == 20


def fit_predict(all_vecs: np.ndarray, seed: int = 42,
                learn_frac: float = 0.01) -> np.ndarray:
    from sklearn.cluster import MiniBatchKMeans
    n = len(all_vecs)
    n_learn = max(int(n * learn_frac), OUTER_K * INNER_K * 50)
    rng = np.random.default_rng(seed)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    learn = all_vecs[learn_idx]

    # Outer split.
    print(f"[{kst()}]   outer MiniBatchKMeans K={OUTER_K} on {n_learn:,} samples")
    outer = MiniBatchKMeans(n_clusters=OUTER_K, random_state=seed,
                            n_init=10, max_iter=100, batch_size=4096)
    outer.fit(learn)
    learn_outer = outer.predict(learn).astype(np.int32)

    # Inner per-outer-cluster split.
    inner_models = []
    for oi in range(OUTER_K):
        mask = learn_outer == oi
        cnt = int(mask.sum())
        if cnt < INNER_K * 5:
            print(f"[{kst()}]   WARN: outer cluster {oi} has only {cnt} learn points "
                  f"→ inner placeholder (single leaf)")
            inner_models.append(None)
            continue
        sub = learn[mask]
        inner = MiniBatchKMeans(n_clusters=INNER_K, random_state=seed + oi + 1,
                                n_init=5, max_iter=100, batch_size=4096)
        inner.fit(sub)
        inner_models.append(inner)

    # Predict for full N: outer first, then per-bucket inner.
    print(f"[{kst()}]   predicting outer + inner for {n:,} rows")
    chunk = 200_000
    out = np.empty(n, dtype=np.int32)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = all_vecs[i:j]
        outer_b = outer.predict(block).astype(np.int32)
        for oi in range(OUTER_K):
            mask = outer_b == oi
            if not mask.any():
                continue
            if inner_models[oi] is None:
                out[i:j][mask] = oi * INNER_K  # all collapse to first inner slot
            else:
                inner_b = inner_models[oi].predict(block[mask]).astype(np.int32)
                out[i:j][mask] = oi * INNER_K + inner_b
    return out


def main():
    ap = argparse.ArgumentParser(description="RQ3 — Hierarchical KMeans (2-level 4x5)")
    ap.add_argument("--out-prefix", default="rq3_hierarchical_kmeans")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — Hierarchical KMeans ({OUTER_K}x{INNER_K}={N_STRATA}) ===")
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
            method_name="hierarchical_kmeans", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": f"Hierarchical KMeans ({OUTER_K}x{INNER_K})",
            "outer_k": OUTER_K,
            "inner_k": INNER_K,
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
