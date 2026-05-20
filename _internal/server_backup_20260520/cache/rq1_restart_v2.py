#!/usr/bin/env python3
"""#2~#5 v2 — D_target을 Python numpy로 계산 (Exqutor hook 회피)"""
import json, time, os, sys, importlib.util
import numpy as np, pandas as pd, psycopg, pyarrow.parquet as pq, scipy.stats as sst
from pathlib import Path
from datetime import datetime, timezone, timedelta

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'
LOG_DIR = '/mnt/hdd0/home/capstone2026/log'
PORT = 55436
DB = 'wns41559'
USER = 'wns41559'
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
N_QUERIES = 100
TABLE_SIFT = 'customer_sift_10_phase7_noidx_subset'
TABLE_1M = 'partsupp_deep_10_subset_1m'

KST = timezone(timedelta(hours=9))
def kst():
    return datetime.now(KST).strftime('%H:%M:%S')

# Load original module for run_queries etc.
ns = {'__name__': 'imported'}; exec(open('/mnt/hdd0/home/capstone2026/cache/rq1_rq2_remaining_all.py').read(), ns)

def dtarget_numpy(conn, table, emb_col, qp, n_queries, target_sel, total_rows):
    """D_target via numpy — load all vectors, compute distances in Python."""
    print(f'[{kst()}] numpy D_target: {table}, sel={target_sel}, n={total_rows}')

    # Load all vectors from DB once
    cache_npy = f'{CACHE}/{table}_vectors.npy'
    if os.path.exists(cache_npy):
        all_vecs = np.load(cache_npy)
        print(f'[{kst()}] Loaded cached vectors: {all_vecs.shape}')
    else:
        print(f'[{kst()}] Loading vectors from DB...')
        with conn.cursor() as cur:
            cur.execute(f'SELECT {emb_col} FROM {table}')
            rows = cur.fetchall()
        all_vecs = np.array([list(map(float, str(r[0]).strip('[]').split(','))) for r in rows], dtype=np.float32)
        np.save(cache_npy, all_vecs)
        print(f'[{kst()}] Cached vectors: {all_vecs.shape}')

    target_count = int(total_rows * target_sel)
    results = []
    for qid in range(n_queries):
        emb = np.asarray(qp.iloc[qid]['embedding'], dtype=np.float32)
        dists = np.linalg.norm(all_vecs - emb, axis=1)  # L2 distance
        sorted_dists = np.sort(dists)
        D_target = float(sorted_dists[min(target_count, len(sorted_dists)-1)])
        true_card = int(np.sum(dists < D_target))
        # Adjust to get closer to target
        if true_card < target_count and target_count < len(sorted_dists):
            D_target = float(sorted_dists[target_count])
            true_card = target_count
        results.append({'query_id': qid, 'D_target': D_target, 'true_card': true_card})
        if (qid+1) % 25 == 0:
            print(f'[{kst()}]   D_target progress: {qid+1}/{n_queries}')
    print(f'[{kst()}] D_target done: median D={np.median([r["D_target"] for r in results]):.4f}')
    return results

def main():
    t_total = time.time()
    conn = psycopg.connect(f'host=/tmp port={PORT} dbname={DB} user={USER}')
    conn.autocommit = True
    log_path = Path(f'{LOG_DIR}/exqutor-{datetime.now(KST).strftime("%Y-%m-%d")}.log')
    all_summaries = {}

    sift_qp = pq.read_table(f'{CACHE}/sift_query_pool.parquet').to_pandas()
    print(f'[{kst()}] Loaded SIFT query pool: {len(sift_qp)}')

    with conn.cursor() as cur:
        cur.execute(f'SELECT count(*) FROM {TABLE_SIFT}')
        sift_total = cur.fetchone()[0]
    print(f'[{kst()}] SIFT: {sift_total} rows')

    # #2 D_target (numpy)
    print(f'\n[{kst()}] ====== #2: SIFT D_target RECALC (numpy) ======')
    sift_queries = {}
    for sel in [0.010, 0.050, 0.500]:
        dt = dtarget_numpy(conn, TABLE_SIFT, 'c_embedding', sift_qp, N_QUERIES, sel, sift_total)
        sift_queries[sel] = [{'query_id': r['query_id'], 'D_target': r['D_target'],
                              'true_card': r['true_card'], 'selectivity': sel} for r in dt]
    sift_all_queries = []
    for sel_qs in sift_queries.values():
        sift_all_queries.extend(sel_qs)
    with open(f'{CACHE}/sift_dtarget_multsel.json', 'w') as f:
        json.dump({'total': sift_total, 'queries': {str(k): v for k, v in sift_queries.items()}}, f, indent=2, default=str)
    print(f'[{kst()}] D_target saved')

    # #3 KM20
    print(f'\n[{kst()}] ====== #3: SIFT KM20 vs BERN ======')
    km20_sift = multiseed_paired(conn, sift_all_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, 'SIFT-KM20', 'embedding')
    all_summaries['sift_km20'] = aggregate_results(km20_sift)

    # #4 RANDOM20
    print(f'\n[{kst()}] ====== #4: SIFT RANDOM20 GRADIENT ======')
    swap_to_random(conn, TABLE_SIFT)
    rand_sift = multiseed_paired(conn, sift_all_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, 'SIFT-RAND', 'embedding')
    restore_km20(conn, TABLE_SIFT)
    all_summaries['sift_rand'] = aggregate_results(rand_sift)

    # #5 1M mid-sel
    print(f'\n[{kst()}] ====== #5: 1M MID-SELECTIVITY GRADIENT ======')
    qp_1m = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()
    with conn.cursor() as cur:
        cur.execute(f'SELECT count(*) FROM {TABLE_1M}')
        total_1m = cur.fetchone()[0]

    mid_queries = []
    for sel in [0.100, 0.300]:
        dt = dtarget_numpy(conn, TABLE_1M, 'ps_embedding', qp_1m, N_QUERIES, sel, total_1m)
        for r in dt:
            mid_queries.append({'query_id': r['query_id'], 'D_target': r['D_target'],
                                'true_card': r['true_card'], 'selectivity': sel})

    km20_1m = multiseed_paired(conn, mid_queries, qp_1m, TABLE_1M, [0.100, 0.300], SEEDS, log_path, '1M-KM20')
    swap_to_random(conn, TABLE_1M)
    rand_1m = multiseed_paired(conn, mid_queries, qp_1m, TABLE_1M, [0.100, 0.300], SEEDS, log_path, '1M-RAND')
    restore_km20(conn, TABLE_1M)
    all_summaries['1m_mid_km20'] = aggregate_results(km20_1m)
    all_summaries['1m_mid_rand'] = aggregate_results(rand_1m)

    conn.close()
    elapsed = time.time() - t_total
    print(f'\n{"#"*60}')
    print(f'# #2~#5 COMPLETE — {elapsed:.0f}s ({elapsed/60:.0f}min)')
    print(f'{"#"*60}')

    with open(f'{CACHE}/rq2_remaining_2to5_summary.json', 'w') as f:
        json.dump(all_summaries, f, indent=2, default=str)
    print(f'[{kst()}] ALL DONE')

if __name__ == '__main__':
    main()
