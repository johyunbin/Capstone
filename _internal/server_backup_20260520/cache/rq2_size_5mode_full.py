#!/usr/bin/env python3
"""P3 새 wrapper — RQ2 size sensitivity 5-mode 완전 측정.

기존 rq2_size_sensitivity.py 는 BERN+Prop hardcoded → 본 wrapper 는 5 mode 모두.
rq2_alloc_python.py 의 allocate_samples + measurement loop 활용.

DEEP_8M only × 4 ssize × 5 mode × 5 sel × 5 seed × 100 q = 50,000 cells.
"""
from __future__ import annotations
import sys, time, json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import psycopg

sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')
import rq2_alloc_python as rq2

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')
PORT = 55436; DB = 'wns41559'; USER = 'wns41559'

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

DATASETS = [{'name': 'DEEP_8M', 'table': 'partsupp_deep_10_phase7_8m_subset',
             'embed_col': 'ps_embedding', 'vec_dim': 96,
             'query_pool': CACHE / 'query_pool.parquet',
             'query_sel': CACHE / 'query_selectivity_8m.parquet'}]

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZES = [100, 385, 1000, 3000]
N_STRATA = 20
ALL_MODES = ['bernoulli', 'equal', 'proportional', 'neyman', 'anti_neyman']

def cache_cluster_samples(ds):
    """cluster 별 LIMIT 4000 sample (max ssize=3000 충분 + buffer)."""
    table = ds["table"]; embed_col = ds["embed_col"]
    samples = {}; sizes = {}
    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f'SELECT stratum_id::int, count(*)::bigint FROM {table} GROUP BY stratum_id ORDER BY stratum_id')
        for sid, n in cu.fetchall():
            sizes[sid] = int(n)
    cache_n = 4000
    for sid in range(N_STRATA):
        with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=True) as c:
            cu = c.cursor()
            cu.execute(f'SELECT {embed_col}::real[] FROM {table} WHERE stratum_id = {sid} LIMIT {cache_n}')
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        samples[sid] = np.stack(rows) if rows else np.zeros((0, ds['vec_dim']), dtype=np.float32)
    return samples, sizes

def load_sigmas(ds):
    """vector_stratum_sigma 에서 σ 가져오기 — dict 반환 (rq2_alloc_python.allocate_samples 호환)."""
    table = ds["table"]
    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f"SELECT stratum_id, sigma FROM vector_stratum_sigma WHERE table_name='{table}' ORDER BY stratum_id")
        s = {int(sid): float(sig) for sid, sig in cu.fetchall()}
    return s

def measure_one(ds, samples, sizes, sigmas, query_pool, query_sel, mode, sel, seed, ssize, n_queries):
    """본 측정 1 cell — query 수 n_queries.

    query_pool: ['ps_partkey', 'ps_suppkey', 'embedding'] (RangeIndex = query_id)
    query_sel: long format ['query_id', 'selectivity', 'D_target', 'true_cardinality', 'actual_sel']
    """
    rng = np.random.default_rng(int(seed * 100))
    if mode != 'bernoulli':
        alloc = rq2.allocate_samples(mode, sizes, sigmas, ssize, N_STRATA)
    # Pre-filter sel rows
    sel_rows = query_sel[query_sel['selectivity'].round(2) == round(sel, 2)].set_index('query_id')
    rows = []
    n_total_pop = sum(sizes.values())
    for qi in range(min(n_queries, len(query_pool))):
        q = query_pool.iloc[qi]
        if qi not in sel_rows.index:
            continue
        d_target = float(sel_rows.loc[qi, 'D_target'])
        true_card = int(sel_rows.loc[qi, 'true_cardinality'])
        qv = np.asarray(q['embedding'], dtype=np.float32)
        if mode == 'bernoulli':
            sample_p = ssize / n_total_pop
            est = 0.0
            for sid in range(N_STRATA):
                cluster_samples = samples[sid]
                if len(cluster_samples) == 0:
                    continue
                n_take = max(int(sample_p * sizes[sid]), 1)
                idx = rng.choice(len(cluster_samples), size=min(n_take, len(cluster_samples)), replace=False)
                d = np.linalg.norm(cluster_samples[idx] - qv, axis=1)
                est += np.sum(d <= d_target) * sizes[sid] / len(idx)
        else:
            est = 0.0
            for sid in range(N_STRATA):
                cluster_samples = samples[sid]
                n_take = int(alloc[sid])
                if n_take == 0 or len(cluster_samples) == 0:
                    continue
                idx = rng.choice(len(cluster_samples), size=min(n_take, len(cluster_samples)), replace=False)
                d = np.linalg.norm(cluster_samples[idx] - qv, axis=1)
                est += np.sum(d <= d_target) * sizes[sid] / len(idx)
        if true_card == 0:
            qe = float('nan')
        else:
            qe = max(est / true_card, true_card / max(est, 1.0))
        rows.append({'dataset': ds['name'], 'sample_size': ssize, 'mode': mode,
                     'selectivity': sel, 'seed': seed, 'query_id': qi,
                     'true_card': true_card, 'est': float(est),
                     'q_error': float(qe) if not np.isnan(qe) else None})
    return rows

def main():
    print(f'[{kst()}] === RQ2 size sensitivity 5-mode 8M ===')
    all_rows = []
    t_total = time.time()
    for ds in DATASETS:
        print(f'[{kst()}] {ds["name"]} ({ds["table"]})')
        samples, sizes = cache_cluster_samples(ds)
        sigmas = load_sigmas(ds)
        print(f'[{kst()}]   cached sample / sizes / sigmas')
        query_pool = pd.read_parquet(ds['query_pool'])
        query_sel = pd.read_parquet(ds['query_sel'])
        print(f'[{kst()}]   queries={len(query_pool)}, sel={list(query_sel.columns)[:5]}')

        for ssize in SAMPLE_SIZES:
            for mode in ALL_MODES:
                for sel in SELECTIVITIES:
                    for seed in SEEDS:
                        rows = measure_one(ds, samples, sizes, sigmas, query_pool, query_sel,
                                          mode, sel, seed, ssize, n_queries=100)
                        all_rows.extend(rows)
                print(f'[{kst()}]   ssize={ssize} mode={mode} done')

    df = pd.DataFrame(all_rows)
    out = CACHE / 'rq2_size_sensitivity_8m_5mode.parquet'
    df.to_parquet(out)
    print(f'[{kst()}] saved {out} ({len(df)} rows, NaN {df["q_error"].isna().mean()*100:.1f}%)')
    meta = {'measure_total_s': round(time.time() - t_total, 1),
            'n_rows': len(df), 'modes': ALL_MODES, 'sample_sizes': SAMPLE_SIZES}
    with open(str(out).replace('.parquet', '_meta.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))

if __name__ == '__main__':
    main()
