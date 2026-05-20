#!/usr/bin/env python3
"""P1 — KM20 hyperparameter sensitivity (KM10 / KM50).

본 연구의 N_STRATA=20 sweet spot 정당화. K=10 (under-partitioned),
K=20 (current), K=50 (over-partitioned with sample budget=385) 비교.
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
import numpy as np
from sklearn.cluster import MiniBatchKMeans

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import _measure_common as mc
from _measure_common import (
    DATASETS, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)

def main():
    ap = argparse.ArgumentParser(description='RQ3 P1 — KM K hyperparameter sweep')
    ap.add_argument('--out-prefix', default='rq3_km_k')
    ap.add_argument('--datasets', nargs='*', default=None)
    ap.add_argument('--n-queries', type=int, default=100)
    ap.add_argument('--K', type=int, required=True, help='K (10, 50, 100)')
    ap.add_argument('--learn-frac', type=float, default=0.01)
    ap.add_argument('--learn-seed', type=int, default=42)
    args = ap.parse_args()

    # patch N_STRATA = K
    mc.N_STRATA = args.K

    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d['name'] in args.datasets]
    print(f'[{kst()}] === RQ3 P1 — KM K={args.K} ===')

    all_rows = []
    t_total = time.time()
    for ds in use_datasets:
        print(f'\n[{kst()}] === {ds["name"]} ===')
        all_vecs, _ = fetch_all_vectors_safe(ds)
        n = len(all_vecs)
        n_learn = max(int(n * args.learn_frac), args.K * 50)
        rng = np.random.default_rng(args.learn_seed)
        learn_idx = rng.choice(n, size=n_learn, replace=False)
        learn_samples = all_vecs[learn_idx]

        t_fit = time.time()
        mbk = MiniBatchKMeans(n_clusters=args.K, batch_size=4096,
                               max_iter=100, random_state=args.learn_seed,
                               n_init=3, max_no_improvement=20).fit(learn_samples)
        sids = mbk.predict(all_vecs).astype(np.int32)
        print(f'[{kst()}]   K={args.K} fit+assign elapsed: {time.time()-t_fit:.1f}s')

        rows = run_method_measurement(f'km{args.K}', all_vecs=all_vecs, stratum_ids=sids,
                                       ds=ds, n_queries=args.n_queries, modes=('equal',))
        all_rows.extend(rows)

    save_parquet_meta(all_rows, prefix=f'{args.out_prefix}_{args.K}',
                      extra_meta={'method': f'KMeans K={args.K} (hyperparameter sensitivity)',
                                  'K': args.K, 'learn_frac': args.learn_frac,
                                  'learn_seed': args.learn_seed,
                                  'elapsed_s': round(time.time() - t_total, 1)})

if __name__ == '__main__':
    main()
