#!/usr/bin/env python3
"""
Multi-table Toy 검증 — Worker H minimal scope (단일 → multi 일반화 정량 입증).

설계:
- toy_multi_join (1M rows, 1:1 join via partkey=custkey)
- 100 query pair (DEEP query[i] + SIFT query[i])
- Joint predicate: (deep_emb <-> q_deep) < d_deep AND (sift_emb <-> q_sift) < d_sift
- Joint target sel = sel_deep × sel_sift (independence approx)
  - 본 toy: sel_deep=0.30, sel_sift=0.30 → joint ~0.09 (실제 측정)
  - 5 sel grid 도 측정 (deep, sift 동일 sel: 0.10, 0.30, 0.50)

측정 방법:
- BERN: random sample N rows from joined
- DEEP_strat: stratify by deep_stratum (20)
- SIFT_strat: stratify by sift_stratum (20)
- JOINT_strat: stratify by (deep_stratum, sift_stratum) (400 cells)

산출:
- /mnt/hdd0/home/capstone2026/cache/rq1/multi_table_toy.parquet
- /mnt/hdd0/home/capstone2026/cache/rq1/multi_table_toy_summary.json
"""
from __future__ import annotations
import json, time, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
PORT = 55436
DB = 'wns41559'
USER = 'wns41559'
TOTAL = 1_000_000  # joined rows
N_QUERIES = 100
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SAMPLE_SIZE = 385
N_STRATA = 20
SEL_GRID = [0.10, 0.30, 0.50]  # 3 sel levels (joint = sel × sel)

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')


def fetch_joined_data():
    print(f'[{kst()}] fetching toy_multi_join (1M rows)...')
    t0 = time.time()
    deep_emb = np.zeros((TOTAL, 96), dtype=np.float32)
    sift_emb = np.zeros((TOTAL, 128), dtype=np.float32)
    deep_strata = np.zeros(TOTAL, dtype=np.int16)
    sift_strata = np.zeros(TOTAL, dtype=np.int16)

    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER) as c:
        with c.cursor(name='fetch_toy') as cu:
            cu.itersize = 50000
            cu.execute('SELECT deep_emb::real[], sift_emb::real[], deep_stratum, sift_stratum FROM toy_multi_join ORDER BY join_key')
            i = 0
            for row in cu:
                deep_emb[i] = np.asarray(row[0], dtype=np.float32)
                sift_emb[i] = np.asarray(row[1], dtype=np.float32)
                deep_strata[i] = row[2]
                sift_strata[i] = row[3]
                i += 1
                if i % 200000 == 0:
                    print(f'[{kst()}]   {i:,} / {TOTAL:,} ({time.time()-t0:.0f}s)', flush=True)
    print(f'[{kst()}] fetched {i} rows in {time.time()-t0:.0f}s')
    return deep_emb, sift_emb, deep_strata, sift_strata


def load_query_data():
    qp_deep = pq.read_table(CACHE / 'query_pool.parquet').to_pandas()
    qp_sift = pq.read_table(CACHE / 'query_pool_sift.parquet').to_pandas()
    qs_deep = pq.read_table(CACHE / 'query_selectivity.parquet').to_pandas()
    qs_sift = pq.read_table(CACHE / 'query_selectivity_sift_v2.parquet').to_pandas()
    qs_deep = qs_deep[qs_deep['query_id'] < N_QUERIES]
    qs_sift = qs_sift[qs_sift['query_id'] < N_QUERIES]
    return qp_deep, qp_sift, qs_deep, qs_sift


def compute_distances(emb_matrix, query_emb):
    """L2 distances vectorized."""
    diff = emb_matrix - query_emb
    return np.sqrt(np.sum(diff ** 2, axis=1))


def estimate_card_bernoulli(sample_idx, mask_full):
    """Estimate cardinality using bernoulli sample."""
    n_total = len(mask_full)
    n_sample = len(sample_idx)
    n_satisfy = int(mask_full[sample_idx].sum())
    return n_satisfy * (n_total / n_sample)


def estimate_card_stratified(sample_idx, mask_full, strata, sample_per_stratum):
    """Estimate via Horvitz-Thompson per stratum."""
    n_total = len(mask_full)
    n_strata = len(np.unique(strata))
    est = 0.0
    for sid in range(N_STRATA):
        stratum_mask = strata == sid
        N_h = int(stratum_mask.sum())
        if N_h == 0:
            continue
        # Find sample indices in this stratum
        sample_in_stratum = sample_idx[stratum_mask[sample_idx]]
        n_h = len(sample_in_stratum)
        if n_h == 0:
            continue
        n_satisfy = int(mask_full[sample_in_stratum].sum())
        est += n_satisfy * (N_h / n_h)
    return est


def estimate_card_joint_strat(sample_idx, mask_full, joint_strata):
    """Joint stratification: deep_stratum * 100 + sift_stratum (max 400)."""
    n_total = len(mask_full)
    est = 0.0
    unique_joint = np.unique(joint_strata)
    for jid in unique_joint:
        mask_j = joint_strata == jid
        N_j = int(mask_j.sum())
        if N_j == 0:
            continue
        sample_in_j = sample_idx[mask_j[sample_idx]]
        n_j = len(sample_in_j)
        if n_j == 0:
            continue
        n_satisfy = int(mask_full[sample_in_j].sum())
        est += n_satisfy * (N_j / n_j)
    return est


def measure_query(qid, q_deep, q_sift, deep_emb, sift_emb, deep_strata, sift_strata,
                  joint_strata, sel_target, qs_deep, qs_sift):
    """Measure single query at given joint sel."""
    # Use d_deep, d_sift at sel = sel_target (each filter ~ sel_target on its own table)
    d_row_deep = qs_deep[(qs_deep.query_id == qid) & (np.isclose(qs_deep.selectivity, sel_target))]
    d_row_sift = qs_sift[(qs_sift.query_id == qid) & (np.isclose(qs_sift.selectivity, sel_target))]
    if len(d_row_deep) == 0 or len(d_row_sift) == 0:
        return None
    d_deep = float(d_row_deep['D_target'].iloc[0])
    d_sift = float(d_row_sift['D_target'].iloc[0])

    # Compute distances
    deep_dist = compute_distances(deep_emb, q_deep)
    sift_dist = compute_distances(sift_emb, q_sift)
    mask = (deep_dist < d_deep) & (sift_dist < d_sift)
    true_card = int(mask.sum())
    actual_joint_sel = true_card / TOTAL

    return {'true_card': true_card, 'actual_joint_sel': actual_joint_sel,
            'mask': mask, 'd_deep': d_deep, 'd_sift': d_sift}


def main():
    print(f'[{kst()}] === Multi-table Toy 검증 시작 ===')
    deep_emb, sift_emb, deep_strata, sift_strata = fetch_joined_data()
    qp_deep, qp_sift, qs_deep, qs_sift = load_query_data()

    # Joint strata: deep * 100 + sift (max 1900+19=1919, but only 400 unique)
    joint_strata = deep_strata.astype(np.int32) * 100 + sift_strata.astype(np.int32)

    rows = []
    n_runs = 0
    for sel_target in SEL_GRID:
        print(f'\n[{kst()}] === sel_target = {sel_target} (joint sel ≈ {sel_target * sel_target:.4f}) ===')
        for qid in range(N_QUERIES):
            q_deep = np.asarray(qp_deep.iloc[qid]['embedding'], dtype=np.float32)
            q_sift = np.asarray(qp_sift.iloc[qid]['embedding'], dtype=np.float32)

            result = measure_query(qid, q_deep, q_sift, deep_emb, sift_emb, deep_strata, sift_strata,
                                   joint_strata, sel_target, qs_deep, qs_sift)
            if result is None:
                continue
            true_card = result['true_card']
            mask = result['mask']

            for seed in SEEDS:
                rng = np.random.default_rng(int(seed * 10**9) % (2**31 - 1))
                # BERN: random N samples
                bern_idx = rng.choice(TOTAL, size=SAMPLE_SIZE, replace=False)
                est_bern = estimate_card_bernoulli(bern_idx, mask)

                # DEEP strat: equal alloc per deep stratum
                deep_strat_idx = []
                per_strat = SAMPLE_SIZE // N_STRATA
                for sid in range(N_STRATA):
                    idx_in_strat = np.where(deep_strata == sid)[0]
                    if len(idx_in_strat) == 0:
                        continue
                    chosen = rng.choice(idx_in_strat, size=min(per_strat, len(idx_in_strat)), replace=False)
                    deep_strat_idx.extend(chosen)
                deep_strat_idx = np.array(deep_strat_idx)
                est_deep = estimate_card_stratified(deep_strat_idx, mask, deep_strata, per_strat)

                # SIFT strat
                sift_strat_idx = []
                for sid in range(N_STRATA):
                    idx_in_strat = np.where(sift_strata == sid)[0]
                    if len(idx_in_strat) == 0:
                        continue
                    chosen = rng.choice(idx_in_strat, size=min(per_strat, len(idx_in_strat)), replace=False)
                    sift_strat_idx.extend(chosen)
                sift_strat_idx = np.array(sift_strat_idx)
                est_sift = estimate_card_stratified(sift_strat_idx, mask, sift_strata, per_strat)

                # JOINT strat: equal per (deep, sift) stratum (400 cells, ~1 sample per cell at SAMPLE_SIZE=385)
                # 실제로는 cells가 적을 수 있어, 실효 sample per cell = max(1, 385/400)
                joint_strat_idx = []
                unique_jstrata = np.unique(joint_strata)
                per_jstrat = max(1, SAMPLE_SIZE // len(unique_jstrata))
                for jid in unique_jstrata:
                    idx_in_strat = np.where(joint_strata == jid)[0]
                    if len(idx_in_strat) == 0:
                        continue
                    chosen = rng.choice(idx_in_strat, size=min(per_jstrat, len(idx_in_strat)), replace=False)
                    joint_strat_idx.extend(chosen)
                joint_strat_idx = np.array(joint_strat_idx)
                est_joint = estimate_card_joint_strat(joint_strat_idx, mask, joint_strata)

                # q_error: max(est, true) / min(est, true)
                def qe(est, true):
                    if est <= 0 or true <= 0:
                        return float('nan')
                    return max(est, true) / min(est, true)

                rows.append({'query_id': qid, 'sel_target': sel_target, 'seed': seed,
                            'true_card': true_card, 'actual_joint_sel': result['actual_joint_sel'],
                            'd_deep': result['d_deep'], 'd_sift': result['d_sift'],
                            'est_bern': est_bern, 'q_error_bern': qe(est_bern, true_card),
                            'est_deep_strat': est_deep, 'q_error_deep_strat': qe(est_deep, true_card),
                            'est_sift_strat': est_sift, 'q_error_sift_strat': qe(est_sift, true_card),
                            'est_joint_strat': est_joint, 'q_error_joint_strat': qe(est_joint, true_card),
                            })
                n_runs += 1
            if (qid + 1) % 25 == 0:
                print(f'[{kst()}]  sel={sel_target} q{qid+1}/{N_QUERIES} done')

    df = pd.DataFrame(rows)
    out = CACHE / 'multi_table_toy.parquet'
    df.to_parquet(out, index=False)
    print(f'\n[{kst()}] saved {out} ({len(df)} rows)')

    print('\n=== mean q_error per sel × method ===')
    for sel in SEL_GRID:
        sub = df[df.sel_target == sel].dropna(subset=['q_error_bern'])
        print(f'sel={sel:.2f}:')
        print(f'  BERN          {sub["q_error_bern"].mean():.4f} (median {sub["q_error_bern"].median():.4f})')
        print(f'  DEEP_strat    {sub["q_error_deep_strat"].mean():.4f} (median {sub["q_error_deep_strat"].median():.4f})')
        print(f'  SIFT_strat    {sub["q_error_sift_strat"].mean():.4f} (median {sub["q_error_sift_strat"].median():.4f})')
        print(f'  JOINT_strat   {sub["q_error_joint_strat"].mean():.4f} (median {sub["q_error_joint_strat"].median():.4f})')

    summary = {
        'sel_grid': SEL_GRID, 'n_queries': N_QUERIES, 'sample_size': SAMPLE_SIZE,
        'methods': ['bern', 'deep_strat', 'sift_strat', 'joint_strat'],
        'total_rows': len(df),
    }
    with open(CACHE / 'multi_table_toy_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'[{kst()}] saved summary')


if __name__ == '__main__':
    main()
