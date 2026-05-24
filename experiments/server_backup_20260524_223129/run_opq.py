#!/usr/bin/env python3
"""P2 — OPQ (Optimized Product Quantization) — PCA rotation + PQ.

기존 PQ 는 vector 를 axis-aligned sub-vector 로 분할 → PCA rotation 후 PQ 가 더 정확.
sklearn PCA rotation + 기존 product_quantization 모듈 활용.

가설: OPQ < PQ in q_error (PCA rotation 으로 sub-vector 간 분산 균등화 → cluster quality ↑).
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
import numpy as np
from sklearn.decomposition import PCA

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'pq'))

from _measure_common import (
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from pq.product_quantization import (
    assign_pq, cluster_size_summary, fit_pq_mapper,
)

def main():
    ap = argparse.ArgumentParser(description='RQ3 P2 — OPQ (PCA rotation + PQ)')
    ap.add_argument('--out-prefix', default='rq3_opq')
    ap.add_argument('--datasets', nargs='*', default=None)
    ap.add_argument('--n-queries', type=int, default=100)
    ap.add_argument('--learn-frac', type=float, default=0.01)
    ap.add_argument('--learn-seed', type=int, default=42)
    ap.add_argument('--m', type=int, default=2)
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d['name'] in args.datasets]
    print(f'[{kst()}] === RQ3 P2 — OPQ (PCA rotation + PQ m={args.m}) ===')

    all_rows = []
    t_total = time.time()
    for ds in use_datasets:
        print(f'\n[{kst()}] === {ds["name"]} ===')
        all_vecs, _ = fetch_all_vectors_safe(ds)
        n = len(all_vecs)
        n_learn = max(int(n * args.learn_frac), N_STRATA * 50)
        rng = np.random.default_rng(args.learn_seed)
        learn_idx = rng.choice(n, size=n_learn, replace=False)
        learn_samples = all_vecs[learn_idx]

        # PCA rotation (full dim, just rotate)
        t_rot = time.time()
        pca = PCA(n_components=ds['vec_dim'], random_state=args.learn_seed).fit(learn_samples)
        rotated_learn = pca.transform(learn_samples).astype(np.float32)
        rotated_all = pca.transform(all_vecs).astype(np.float32)
        print(f'[{kst()}]   PCA rotation elapsed: {time.time()-t_rot:.1f}s, evr_sum={pca.explained_variance_ratio_.sum():.4f}')

        mapper = fit_pq_mapper(rotated_learn, n_strata=N_STRATA, m=args.m, seed=args.learn_seed)
        sids = assign_pq(mapper, rotated_all)
        summary = cluster_size_summary(sids, n_clusters=N_STRATA)
        print(f'[{kst()}]   OPQ stratum sizes: min={summary["min"]}, max={summary["max"]}, max/min={summary["max_min_ratio"]:.2f}')

        rows = run_method_measurement('opq', all_vecs=all_vecs, stratum_ids=sids,
                                       ds=ds, n_queries=args.n_queries, modes=('equal',))
        all_rows.extend(rows)

    save_parquet_meta(all_rows, prefix=args.out_prefix,
                      extra_meta={'method': f'OPQ (PCA rotation + PQ m={args.m})',
                                  'm': args.m, 'learn_frac': args.learn_frac,
                                  'learn_seed': args.learn_seed,
                                  'elapsed_s': round(time.time() - t_total, 1)})

if __name__ == '__main__':
    main()
