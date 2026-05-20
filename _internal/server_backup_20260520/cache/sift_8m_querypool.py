#!/usr/bin/env python3
"""SIFT 8M querypool v3 — long format (query_id × selectivity row, D_target/true_cardinality cols).

_measure_common._load_query_pool 가 expect 하는 format 정확 매칭.
"""
import time
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta

TABLE = 'customer_sift_8m_subset'
N_QUERIES = 100
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_FOR_SEL = 200_000
NPY_DIR = Path('/mnt/hdd0/home/capstone2026/cache/rq1')


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def main():
    print(f'[{kst()}] === SIFT 8M query pool v3 (long format) ===', flush=True)
    all_vecs = np.load(NPY_DIR / f'{TABLE}_vectors.npy')
    custkeys = np.load(NPY_DIR / f'{TABLE}_custkeys.npy')
    print(f'[{kst()}]   loaded {len(all_vecs):,}', flush=True)

    rng = np.random.default_rng(42)
    q_idx = rng.choice(len(all_vecs), size=N_QUERIES, replace=False)
    q_vecs = all_vecs[q_idx]
    q_keys = custkeys[q_idx]
    sample_idx = rng.choice(len(all_vecs), size=SAMPLE_FOR_SEL, replace=False)

    rows = []
    t0 = time.time()
    for qi, qv in enumerate(q_vecs):
        all_d = np.linalg.norm(all_vecs - qv, axis=1)
        sample_d = all_d[sample_idx]
        for sel in SELECTIVITIES:
            d_target = float(np.quantile(sample_d, sel))
            true_card = int(np.sum(all_d <= d_target))
            actual_sel = true_card / len(all_vecs)
            rows.append({
                'query_id': qi,
                'selectivity': sel,
                'D_target': d_target,
                'true_cardinality': true_card,
                'actual_sel': actual_sel,
            })
        if (qi + 1) % 25 == 0:
            print(f'[{kst()}]     {qi+1}/{N_QUERIES} ({time.time()-t0:.1f}s)', flush=True)

    sel_df = pd.DataFrame(rows)
    qp_df = pd.DataFrame([{
        'query_id': qi,
        'embedding': q_vecs[qi].tolist(),
        'q_custkey': int(q_keys[qi]),
    } for qi in range(N_QUERIES)])

    qp_df.to_parquet(NPY_DIR / 'query_pool_sift_8m.parquet')
    sel_df.to_parquet(NPY_DIR / 'query_selectivity_sift_8m.parquet')
    print(f'[{kst()}]   saved query_pool_sift_8m.parquet ({len(qp_df)} rows)', flush=True)
    print(f'[{kst()}]   saved query_selectivity_sift_8m.parquet ({len(sel_df)} rows long format)', flush=True)
    print(f'[{kst()}] === SIFT 8M query pool v3 DONE ===', flush=True)


if __name__ == '__main__':
    main()
