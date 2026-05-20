#!/usr/bin/env python3
"""#2~#5 재실행 — postgresql.conf에 update_sample_size=off 반영 후"""
import json, time, os, sys
sys.path.insert(0, '/mnt/hdd0/home/capstone2026/cache')

# 기존 스크립트를 모듈로 임포트
import importlib.util
spec = importlib.util.spec_from_file_location('remaining', '/mnt/hdd0/home/capstone2026/cache/rq1_rq2_remaining_all.py')
mod = importlib.util.module_from_spec(spec)

# 직접 실행하지 않고 필요한 함수만 빌려옴
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

def emb_to_pgvec(emb):
    return '[' + ','.join('%.7f' % float(x) for x in emb) + ']'

# exec the module to get all functions
exec(open('/mnt/hdd0/home/capstone2026/cache/rq1_rq2_remaining_all.py').read(), mod.__dict__)

def main():
    t_total = time.time()
    conn = psycopg.connect(f'host=/tmp port={PORT} dbname={DB} user={USER}')
    conn.autocommit = True
    log_path = Path(f'{LOG_DIR}/exqutor-{datetime.now(KST).strftime("%Y-%m-%d")}.log')
    all_summaries = {}

    # Load existing data
    sift_qp = pq.read_table(f'{CACHE}/sift_query_pool.parquet').to_pandas()
    print(f'[{kst()}] Loaded SIFT query pool: {len(sift_qp)}')

    with conn.cursor() as cur:
        cur.execute(f'SELECT count(*) FROM {TABLE_SIFT}')
        sift_total = cur.fetchone()[0]
        cur.execute(f'SELECT count(DISTINCT stratum_id) FROM {TABLE_SIFT}')
        sift_strata = cur.fetchone()[0]
    print(f'[{kst()}] SIFT: {sift_total} rows, {sift_strata} strata')

    # #2 D_target
    print(f'\n[{kst()}] ====== #2: SIFT D_target RECALC ======')
    sift_queries = {}
    for sel in [0.010, 0.050, 0.500]:
        print(f'[{kst()}] SIFT D_target for s={sel}...')
        dt = mod.dtarget_binary_search(conn, TABLE_SIFT, 'c_embedding', sift_qp, N_QUERIES, sel, sift_total)
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
    km20_sift = mod.multiseed_paired(conn, sift_all_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, 'SIFT-KM20', 'embedding')
    all_summaries['sift_km20'] = mod.aggregate_results(km20_sift)

    # #4 RANDOM20
    print(f'\n[{kst()}] ====== #4: SIFT RANDOM20 GRADIENT ======')
    mod.swap_to_random(conn, TABLE_SIFT)
    rand_sift = mod.multiseed_paired(conn, sift_all_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, 'SIFT-RAND', 'embedding')
    mod.restore_km20(conn, TABLE_SIFT)
    all_summaries['sift_rand'] = mod.aggregate_results(rand_sift)

    # #5 1M mid-sel
    print(f'\n[{kst()}] ====== #5: 1M MID-SELECTIVITY GRADIENT ======')
    qs_path = f'{CACHE}/dtarget_multsel.json'
    with open(qs_path) as f:
        qs_data = json.load(f)
    qp = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()

    mid_queries = []
    for sel_str in ['0.1', '0.3']:
        if sel_str in qs_data.get('queries', {}):
            for q in qs_data['queries'][sel_str][:N_QUERIES]:
                mid_queries.append({'query_id': int(q['query_id']), 'D_target': float(q['D_target']),
                                    'true_card': int(q['true_card']), 'selectivity': float(sel_str)})

    if not mid_queries:
        # Need D_target for s=0.1, 0.3
        print(f'[{kst()}] Computing 1M D_target for s=0.100, 0.300...')
        with conn.cursor() as cur:
            cur.execute(f'SELECT count(*) FROM {TABLE_1M}')
            total_1m = cur.fetchone()[0]
        for sel in [0.100, 0.300]:
            dt = mod.dtarget_binary_search(conn, TABLE_1M, 'ps_embedding', qp, N_QUERIES, sel, total_1m)
            for r in dt:
                mid_queries.append({'query_id': r['query_id'], 'D_target': r['D_target'],
                                    'true_card': r['true_card'], 'selectivity': sel})

    km20_1m = mod.multiseed_paired(conn, mid_queries, qp, TABLE_1M, [0.100, 0.300], SEEDS, log_path, '1M-KM20')
    mod.swap_to_random(conn, TABLE_1M)
    rand_1m = mod.multiseed_paired(conn, mid_queries, qp, TABLE_1M, [0.100, 0.300], SEEDS, log_path, '1M-RAND')
    mod.restore_km20(conn, TABLE_1M)
    all_summaries['1m_mid_km20'] = mod.aggregate_results(km20_1m)
    all_summaries['1m_mid_rand'] = mod.aggregate_results(rand_1m)

    conn.close()
    elapsed = time.time() - t_total
    print(f'\n{"#"*60}')
    print(f'# #2~#5 COMPLETE — {elapsed:.0f}s ({elapsed/60:.0f}min)')
    print(f'{"#"*60}')

    with open(f'{CACHE}/rq2_remaining_2to5_summary.json', 'w') as f:
        json.dump(all_summaries, f, indent=2, default=str)
    print(f'[{kst()}] Summary saved')
    print(f'[{kst()}] ALL DONE')

if __name__ == '__main__':
    main()
