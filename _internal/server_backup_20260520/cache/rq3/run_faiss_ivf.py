#!/usr/bin/env python3
"""run_faiss_ivf.py — RQ3 distribution-agnostic method (FAISS IVF coarse quantizer).

faiss.IndexIVFFlat with N_STRATA centroids (quantizer = IndexFlatL2). Train on
a 1% sample; for each row, the nearest coarse centroid id (via the quantizer)
becomes the stratum id.
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
    import faiss
    n, d = all_vecs.shape
    arr = np.ascontiguousarray(all_vecs, dtype=np.float32)

    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    rng = np.random.default_rng(seed)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    train = np.ascontiguousarray(arr[learn_idx], dtype=np.float32)

    print(f"[{kst()}]   FAISS IVF train (k={N_STRATA}) on {n_learn:,} samples, dim={d}")
    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFFlat(quantizer, d, N_STRATA, faiss.METRIC_L2)
    # IVF needs training to learn coarse centroids.
    try:
        # newer faiss
        faiss.ParameterSpace().set_index_parameter(index, "verbose", 0)
    except Exception:
        pass
    index.train(train)
    print(f"[{kst()}]   FAISS IVF trained, ntotal_centroids={index.nlist}")

    # Use the inner quantizer's nearest-neighbour search to assign each row.
    chunk = 200_000
    out = np.empty(n, dtype=np.int32)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = np.ascontiguousarray(arr[i:j], dtype=np.float32)
        _, I = quantizer.search(block, 1)  # (block, 1)
        out[i:j] = I[:, 0].astype(np.int32)
    return out


def main():
    ap = argparse.ArgumentParser(description="RQ3 — FAISS IVF coarse quantizer")
    ap.add_argument("--out-prefix", default="rq3_faiss_ivf")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 — FAISS IVF (k={N_STRATA}) ===")
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
            method_name="faiss_ivf", all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "FAISS IVF coarse quantizer (IndexIVFFlat)",
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
