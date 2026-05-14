#!/usr/bin/env python3
"""
RQ3 #20 — Sparse Random Projection (Achlioptas 2003) 측정.

Random Projection (#5) 의 sparse variant — entry 가 {-√3, 0, +√3} 의 sparse matrix.
Dense Gaussian RP 대비 ~3× faster, 메모리 1/3.

가설 H3-SR: Dense RP 와 비슷한 recovery, 하지만 학습/assignment 시간 단축.
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
from sparserp.sparse_random_projection import (  # noqa: E402
    assign_sparse_rp, cluster_size_summary, fit_sparse_rp,
)


def main():
    ap = argparse.ArgumentParser(description="RQ3 #20 — Sparse Random Projection")
    ap.add_argument("--out-prefix", default="rq3_sparse_rp")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--proj-seed", type=int, default=42,
                    help="sparse RP matrix seed")
    ap.add_argument("--include-bernoulli", action="store_true")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    print(f"[{kst()}] === RQ3 #20 — Sparse Random Projection ===")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}, proj_seed={args.proj_seed}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _km20_sids = fetch_all_vectors_safe(ds)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            matrix = fit_sparse_rp(ds["vec_dim"], n_strata=N_STRATA, seed=args.proj_seed)

        stratum_ids = assign_sparse_rp(matrix, all_vecs, k=N_STRATA)
        summary = cluster_size_summary(stratum_ids, n_clusters=N_STRATA)
        print(
            f"[{kst()}]   SparseRP bin sizes: "
            f"min={summary['min']}, max={summary['max']}, "
            f"max/min={summary['max_min_ratio']:.2f}"
        )

        rows = run_method_measurement(
            method_name="sparse_rp", all_vecs=all_vecs, stratum_ids=stratum_ids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=args.out_prefix,
        extra_meta={
            "method": "Sparse Random Projection (Achlioptas)",
            "proj_seed": args.proj_seed,
            "n_queries": args.n_queries,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
