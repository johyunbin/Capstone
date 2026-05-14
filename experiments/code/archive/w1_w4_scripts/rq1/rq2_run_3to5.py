#!/usr/bin/env python3
"""#3~#5 clean run — D_target cached, PG stable"""
import json, re, time, os
import numpy as np, pandas as pd, psycopg, pyarrow.parquet as pq
import scipy.stats as sst
from pathlib import Path
from datetime import datetime, timedelta, timezone

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'
LOG_DIR = '/mnt/hdd0/home/capstone2026/log'
PORT = 55436; DB = 'wns41559'; USER = 'wns41559'
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
N_QUERIES = 100
TABLE_SIFT = 'customer_sift_10_phase7_noidx_subset'
TABLE_1M = 'partsupp_deep_10_subset_1m'
KST = timezone(timedelta(hours=9))
EST_RE = re.compile(r'Estimated cardinality for range query on table (\S+): ([\d.eE+\-]+)')

def kst():
    return datetime.now(KST).strftime('%H:%M:%S')

def emb_to_pgvec(emb):
    return '[' + ','.join('%.7f' % float(x) for x in emb) + ']'

def find_scan_node(plan):
    node = plan
    while True:
        if 'Scan' in node.get('Node Type', ''):
            return node
        children = node.get('Plans', [])
        if not children:
            return node
        node = children[0]

def run_queries(conn, queries, qp, table, method, seed, log_path, emb_col='embedding'):
    cur = conn.cursor()
    cur.execute(f'SELECT setseed({seed})')
    cur.execute('SET vector.sample_size = 385')
    cur.execute('SET vector.update_sample_size = off')
    cur.execute('SET vector.sample_update_cycle = 50')
    cur.execute(f"SET vector.sampling_method = '{method}'")

    log_offset = log_path.stat().st_size if log_path.exists() else 0
    emb_col_db = 'ps_embedding' if 'partsupp' in table else 'c_embedding'
    results = []

    for q in queries:
        qid = q['query_id']
        D = q['D_target']
        true_card = q['true_card']
        emb = np.asarray(qp.iloc[qid][emb_col], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)
        sql = (f"EXPLAIN (ANALYZE, FORMAT JSON) SELECT count(*) FROM {table} "
               f"WHERE ({emb_col_db} <-> '{vec_str}'::vector) < {D}")
        try:
            cur.execute(sql)
            plan = cur.fetchone()[0][0]['Plan']
            scan = find_scan_node(plan)
            pr = scan.get('Plan Rows')
            qe = max(pr / true_card, true_card / pr) if pr and pr > 0 and true_card > 0 else None
            results.append({'query_id': qid, 'true_card': true_card, 'plan_rows': pr, 'q_error': qe})
        except Exception as e:
            results.append({'query_id': qid, 'true_card': true_card, 'plan_rows': None, 'q_error': None})

    hook_ests = []
    time.sleep(0.5)
    if log_path.exists():
        with open(log_path, 'rb') as f:
            f.seek(log_offset)
            content = f.read().decode('utf-8', errors='replace')
            for m in EST_RE.finditer(content):
                if m.group(1) == table:
                    hook_ests.append(float(m.group(2)))

    df = pd.DataFrame(results)
    for i in range(len(df)):
        he = hook_ests[i] if i < len(hook_ests) else None
        df.loc[i, 'hook_est'] = he
        tc = df.loc[i, 'true_card']
        df.loc[i, 'q_error_hook'] = max(he / tc, tc / he) if he and he > 0 and tc > 0 else None
    cur.close()
    return df

def multiseed_paired(conn, queries, qp, table, sels, seeds, log_path, label, emb_col='embedding'):
    all_results = {}
    for sel in sels:
        qs_sel = [q for q in queries if abs(q['selectivity'] - sel) < 0.0001]
        if not qs_sel:
            continue
        print(f'\n[{kst()}] --- {label} s={sel} ({len(qs_sel)} queries) ---')
        seed_data = []
        for seed in seeds:
            ts = time.time()
            bern = run_queries(conn, qs_sel, qp, table, 'bernoulli', seed, log_path, emb_col)
            strat = run_queries(conn, qs_sel, qp, table, 'stratified', seed, log_path, emb_col)
            pair = bern[['query_id', 'q_error_hook']].rename(columns={'q_error_hook': 'qe_b'}).merge(
                strat[['query_id', 'q_error_hook']].rename(columns={'q_error_hook': 'qe_s'}), on='query_id'
            ).dropna()
            if len(pair) > 0:
                try:
                    p = float(sst.wilcoxon(pair['qe_s'].values, pair['qe_b'].values, alternative='less', zero_method='wilcox').pvalue)
                except:
                    p = float('nan')
                mb = float(np.median(pair['qe_b']))
                ms = float(np.median(pair['qe_s']))
                diff = (mb - ms) / mb * 100 if mb > 0 else 0
                nb = int(np.sum(pair['qe_s'] < pair['qe_b']))
                sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
                r = {'seed': seed, 'n': len(pair), 'bern_med': mb, 'strat_med': ms,
                     'diff_pct': diff, 'p': p, 'n_better': nb}
                seed_data.append(r)
                print(f'[{kst()}]   seed={seed}: B={mb:.4f} S={ms:.4f} d={diff:+.2f}% p={p:.2e}{sig} win={nb}/{len(pair)} ({time.time()-ts:.0f}s)')
            else:
                bh = bern['q_error_hook'].notna().sum()
                sh = strat['q_error_hook'].notna().sum()
                print(f'[{kst()}]   seed={seed}: EMPTY (bern_hook={bh}/{len(bern)}, strat_hook={sh}/{len(strat)})')
                seed_data.append({'seed': seed, 'n': 0})
        all_results[f's{sel}'] = seed_data
    return all_results

def aggregate_results(results):
    agg = {}
    for key, seeds in results.items():
        valid = [r for r in seeds if r.get('n', 0) > 0]
        if valid:
            diffs = [r['diff_pct'] for r in valid]
            agg[key] = {
                'mean_diff_pct': float(np.mean(diffs)),
                'std_diff_pct': float(np.std(diffs)),
                'n_seeds': len(valid),
                'per_seed': valid
            }
    return agg

def swap_to_random(conn, table):
    cur = conn.cursor()
    cur.execute(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS km20_backup int')
    cur.execute(f'UPDATE {table} SET km20_backup = stratum_id')
    cur.execute(f'UPDATE {table} SET stratum_id = floor(random() * 20)::int')
    cur.execute(f'ANALYZE {table}')
    cur.close()
    print(f'[{kst()}] RANDOM20 set on {table}')

def restore_km20(conn, table):
    cur = conn.cursor()
    cur.execute(f'UPDATE {table} SET stratum_id = km20_backup')
    cur.execute(f'ALTER TABLE {table} DROP COLUMN km20_backup')
    cur.execute(f'ANALYZE {table}')
    cur.close()
    print(f'[{kst()}] KM20 restored on {table}')

def main():
    t0 = time.time()
    conn = psycopg.connect(f'host=/tmp port={PORT} dbname={DB} user={USER}')
    conn.autocommit = True
    log_path = Path(f'{LOG_DIR}/exqutor-{datetime.now(KST).strftime("%Y-%m-%d")}.log')
    all_summaries = {}

    sift_qp = pq.read_table(f'{CACHE}/sift_query_pool.parquet').to_pandas()
    with open(f'{CACHE}/sift_dtarget_multsel.json') as f:
        sift_dt = json.load(f)
    sift_queries = []
    for sel_str, qs in sift_dt['queries'].items():
        sel = float(sel_str)
        for q in qs[:N_QUERIES]:
            sift_queries.append({'query_id': int(q['query_id']), 'D_target': float(q['D_target']),
                                 'true_card': int(q['true_card']), 'selectivity': sel})
    print(f'[{kst()}] SIFT queries: {len(sift_queries)}')

    # #3
    print(f'\n[{kst()}] ====== #3: SIFT KM20 vs BERN ======')
    km20 = multiseed_paired(conn, sift_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, 'SIFT-KM20', 'embedding')
    all_summaries['sift_km20'] = aggregate_results(km20)

    # #4
    print(f'\n[{kst()}] ====== #4: SIFT RANDOM20 GRADIENT ======')
    swap_to_random(conn, TABLE_SIFT)
    rand_sift = multiseed_paired(conn, sift_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, 'SIFT-RAND', 'embedding')
    restore_km20(conn, TABLE_SIFT)
    all_summaries['sift_rand'] = aggregate_results(rand_sift)

    # #5
    print(f'\n[{kst()}] ====== #5: 1M MID-SELECTIVITY ======')
    qp_1m = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()
    with conn.cursor() as cur:
        total_1m = cur.execute(f'SELECT count(*) FROM {TABLE_1M}').fetchone()[0]

    vecs_path = f'{CACHE}/{TABLE_1M}_vectors.npy'
    if os.path.exists(vecs_path):
        all_vecs = np.load(vecs_path)
        print(f'[{kst()}] Loaded 1M vectors: {all_vecs.shape}')
    else:
        print(f'[{kst()}] Loading 1M vectors from DB...')
        with conn.cursor() as cur:
            cur.execute(f'SELECT ps_embedding FROM {TABLE_1M}')
            rows = cur.fetchall()
        all_vecs = np.array([list(map(float, str(r[0]).strip('[]').split(','))) for r in rows], dtype=np.float32)
        np.save(vecs_path, all_vecs)
        print(f'[{kst()}] Cached: {all_vecs.shape}')

    mid_queries = []
    for sel in [0.100, 0.300]:
        target_count = int(total_1m * sel)
        for qid in range(N_QUERIES):
            emb = np.asarray(qp_1m.iloc[qid]['embedding'], dtype=np.float32)
            dists = np.linalg.norm(all_vecs - emb, axis=1)
            sorted_d = np.sort(dists)
            idx = min(target_count, len(sorted_d) - 1)
            D_target = float(sorted_d[idx])
            true_card = int(np.sum(dists < D_target))
            mid_queries.append({'query_id': qid, 'D_target': D_target, 'true_card': true_card, 'selectivity': sel})
        print(f'[{kst()}] 1M D_target s={sel} done')

    km20_1m = multiseed_paired(conn, mid_queries, qp_1m, TABLE_1M, [0.100, 0.300], SEEDS, log_path, '1M-KM20')
    swap_to_random(conn, TABLE_1M)
    rand_1m = multiseed_paired(conn, mid_queries, qp_1m, TABLE_1M, [0.100, 0.300], SEEDS, log_path, '1M-RAND')
    restore_km20(conn, TABLE_1M)
    all_summaries['1m_mid_km20'] = aggregate_results(km20_1m)
    all_summaries['1m_mid_rand'] = aggregate_results(rand_1m)

    conn.close()
    elapsed = time.time() - t0

    with open(f'{CACHE}/rq2_3to5_summary.json', 'w') as f:
        json.dump(all_summaries, f, indent=2, default=str)
    print(f'\n[{kst()}] #3~#5 COMPLETE ({elapsed:.0f}s / {elapsed/3600:.1f}h)')
    print(f'[{kst()}] ALL DONE')

if __name__ == '__main__':
    main()
