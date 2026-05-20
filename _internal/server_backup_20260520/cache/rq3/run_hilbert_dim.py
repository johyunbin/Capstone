#!/usr/bin/env python3
"""P5 — Hilbert curve dimension variation (PCA(d) + Hilbert d-dimensional curve).

기존 hilbert wrapper 는 PCA(2) + 2D Hilbert. 본 wrapper 는 PCA(3) + 3D Hilbert,
PCA(4) + 4D Hilbert 비교. 가설: 고차원 Hilbert 가 cluster locality 더 잘 보존.

학습 비용 trade-off: d↑ → grid 4^d 증가, learning slow but ranking quality 개선 가능.
"""
from __future__ import annotations
import argparse, sys, time, warnings
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'hilbert'))

from _measure_common import (
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)
from sklearn.decomposition import PCA
from hilbertcurve.hilbertcurve import HilbertCurve

def fit_hilbert_dim(samples, n_strata=N_STRATA, dim=3, p=6, seed=42):
    """PCA(dim) + dim-D Hilbert curve quantile partition."""
    pca = PCA(n_components=dim, random_state=seed).fit(samples)
    proj = pca.transform(samples)
    # quantile bin per axis (p bits per axis)
    n_bins = 2**p
    qbins = []
    for d in range(dim):
        edges = np.quantile(proj[:, d], np.linspace(0, 1, n_bins+1))
        edges[0] = -np.inf; edges[-1] = np.inf
        qbins.append(edges)
    hc = HilbertCurve(p=p, n=dim)
    return {'pca': pca, 'qbins': qbins, 'hc': hc, 'p': p, 'dim': dim, 'n_strata': n_strata}

def assign_hilbert_dim(mapper, vecs):
    proj = mapper['pca'].transform(vecs)
    coords = np.zeros(proj.shape, dtype=np.int64)
    for d in range(mapper['dim']):
        coords[:, d] = np.clip(np.searchsorted(mapper['qbins'][d], proj[:, d], side='right') - 1, 0, 2**mapper['p'] - 1)
    # Hilbert distance per row (slow loop — but fits within wrapper time budget)
    distances = np.array([mapper['hc'].distance_from_point(coords[i].tolist()) for i in range(len(coords))])
    # quantile分 to N_STRATA
    boundaries = np.quantile(distances, np.linspace(0, 1, mapper['n_strata']+1))
    boundaries[0] = -np.inf; boundaries[-1] = np.inf
    sids = np.clip(np.searchsorted(boundaries, distances, side='right') - 1, 0, mapper['n_strata'] - 1)
    return sids.astype(np.int32)

def main():
    ap = argparse.ArgumentParser(description='RQ3 P5 — Hilbert dim variation')
    ap.add_argument('--out-prefix', default='rq3_hilbert_dim')
    ap.add_argument('--datasets', nargs='*', default=None)
    ap.add_argument('--n-queries', type=int, default=100)
    ap.add_argument('--learn-frac', type=float, default=0.01)
    ap.add_argument('--learn-seed', type=int, default=42)
    ap.add_argument('--dim', type=int, required=True, help='Hilbert dimension (3 or 4)')
    ap.add_argument('--p', type=int, default=6, help='Hilbert order')
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d['name'] in args.datasets]
    print(f'[{kst()}] === RQ3 P5 — Hilbert {args.dim}D (p={args.p}) ===')

    all_rows = []
    t_total = time.time()
    for ds in use_datasets:
        print(f'\n[{kst()}] === {ds["name"]} ===')
        all_vecs, _ = fetch_all_vectors_safe(ds)
        n = len(all_vecs)
        n_learn = max(int(n * args.learn_frac), N_STRATA * 50)
        rng = np.random.default_rng(args.learn_seed)
        learn_idx = rng.choice(n, size=n_learn, replace=False)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=RuntimeWarning)
            mapper = fit_hilbert_dim(all_vecs[learn_idx], n_strata=N_STRATA, dim=args.dim, p=args.p, seed=args.learn_seed)
            t_assign = time.time()
            sids = assign_hilbert_dim(mapper, all_vecs)
            print(f'[{kst()}]   assign elapsed: {time.time()-t_assign:.1f}s')

        rows = run_method_measurement(f'hilbert_{args.dim}d', all_vecs=all_vecs, stratum_ids=sids,
                                       ds=ds, n_queries=args.n_queries, modes=('equal',))
        all_rows.extend(rows)

    save_parquet_meta(all_rows, prefix=f'{args.out_prefix}_{args.dim}d',
                      extra_meta={'method': f'Hilbert {args.dim}D + PCA({args.dim})',
                                  'dim': args.dim, 'p': args.p,
                                  'learn_frac': args.learn_frac, 'learn_seed': args.learn_seed,
                                  'elapsed_s': round(time.time() - t_total, 1)})

if __name__ == '__main__':
    main()
