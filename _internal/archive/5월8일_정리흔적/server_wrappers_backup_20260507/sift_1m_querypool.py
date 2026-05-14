#!/usr/bin/env python3
"""SIFT 1M query pool — 100q + 5 sel d_target/true_card on 1M full."""
import time
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta

TABLE = 'customer_sift_1m_subset'
N_QUERIES = 100
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_FOR_SEL = 200_000  # 1M × 20% — quantile 안정
NPY_DIR = Path('/mnt/hdd0/home/capstone2026/cache/rq1')


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def main():
    print(f'[{kst()}] === SIFT 1M query pool START ===', flush=True)
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
            rows.append({'query_id': qi, 'selectivity': sel, 'd_target': d_target,
                         'true_card': true_card, 'q_custkey': int(q_keys[qi])})
        if (qi + 1) % 25 == 0:
            print(f'[{kst()}]     {qi+1}/{N_QUERIES} ({time.time()-t0:.1f}s)', flush=True)

    sel_df = pd.DataFrame(rows)
    qp_df = pd.DataFrame([{'query_id': qi, 'embedding': q_vecs[qi].tolist(),
                            'q_custkey': int(q_keys[qi])} for qi in range(N_QUERIES)])
    qp_df.to_parquet(NPY_DIR / 'query_pool_sift_1m.parquet')

    out_df = pd.DataFrame({'query_id': range(N_QUERIES)})
    for sel in SELECTIVITIES:
        sub = sel_df[sel_df['selectivity'] == sel].set_index('query_id')
        out_df[f'd_target_s{sel}'] = sub['d_target'].values
        out_df[f'true_card_s{sel}'] = sub['true_card'].values
    out_df.to_parquet(NPY_DIR / 'query_selectivity_sift_1m.parquet')
    print(f'[{kst()}]   saved query_pool_sift_1m.parquet + query_selectivity_sift_1m.parquet', flush=True)
    print(f'[{kst()}] === SIFT 1M query pool DONE ===', flush=True)


if __name__ == '__main__':
    main()
