#!/usr/bin/env python3
"""P4 — Reservoir Sampling (Vitter 1985) streaming baseline.

Streaming uniform sampling — random20 의 streaming 변형. 분할 X (단일 stratum=0 모든 row).
HT estimator: weight = N/k (k=sample size).

가설: BERN 와 거의 동일 (둘 다 uniform random). 단, sample size 가 sel 별
exact (정확히 sample_size 만큼) vs BERN (확률 sampling, NaN 발생).
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from _measure_common import (
    DATASETS, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)

def assign_reservoir(n_rows, seed=42, n_strata=N_STRATA):
    """Vitter Algorithm R: streaming reservoir 모방. 모든 row 에 stratum_id 부여.
    실제 streaming reservoir 는 single sample 추출. 측정 비교 위해 random20 동일 변형."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_strata, size=n_rows).astype(np.int32)

def main():
    ap = argparse.ArgumentParser(description='RQ3 P4 — Reservoir streaming baseline')
    ap.add_argument('--out-prefix', default='rq3_reservoir')
    ap.add_argument('--datasets', nargs='*', default=None)
    ap.add_argument('--n-queries', type=int, default=100)
    ap.add_argument('--partition-seed', type=int, default=137)  # different from random20 seed=42
    ap.add_argument('--include-bernoulli', action='store_true')
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d['name'] in args.datasets]
    print(f'[{kst()}] === RQ3 P4 — Reservoir streaming baseline ===')
    modes = ('equal', 'bernoulli') if args.include_bernoulli else ('equal',)

    all_rows = []
    t_total = time.time()
    for ds in use_datasets:
        print(f'\n[{kst()}] === {ds["name"]} ({ds["table"]}) ===')
        all_vecs, _ = fetch_all_vectors_safe(ds)
        sids = assign_reservoir(len(all_vecs), seed=args.partition_seed)
        rows = run_method_measurement('reservoir', all_vecs=all_vecs, stratum_ids=sids,
                                       ds=ds, n_queries=args.n_queries, modes=modes)
        all_rows.extend(rows)

    save_parquet_meta(all_rows, prefix=args.out_prefix,
                      extra_meta={'method': 'Reservoir Sampling (Vitter Algorithm R proxy)',
                                  'partition_seed': args.partition_seed,
                                  'note': 'streaming uniform — random20 와 같은 알고리즘이지만 다른 seed',
                                  'elapsed_s': round(time.time() - t_total, 1)})

if __name__ == '__main__':
    main()
