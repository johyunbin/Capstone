#!/usr/bin/env python3
import time, json, numpy as np, psycopg, pyarrow.parquet as pq
from datetime import datetime, timedelta, timezone

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'
N_QUERIES = 100

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

def emb_to_pgvec(emb):
    return '[' + ','.join(f'{float(x):.7f}' for x in emb) + ']'

print(f'[{kst()}] Phase 7 D_target recalc (connection-level GUC)')

qp = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()

# Connection with GUC options to disable hook update
conn = psycopg.connect(
    host='/tmp', port=55435, user='wns41559', dbname='wns41559',
    autocommit=True,
    options='-c vector.update_sample_size=off -c vector.sample_update_cycle=1000'
)

with conn.cursor() as cur:
    cur.execute('SELECT count(*) FROM partsupp_deep_10')
    total_8m = cur.fetchone()[0]
    # Verify GUC
    cur.execute('SHOW vector.update_sample_size')
    guc_val = cur.fetchone()[0]
    print(f'[{kst()}] rows: {total_8m}, update_sample_size={guc_val}')

results = []
t0 = time.time()
with conn.cursor() as cur:
    for qid in range(N_QUERIES):
        emb = np.asarray(qp.iloc[qid]['embedding'], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)
        
        # Use numpy to compute distances in Python instead of SQL <-> operator
        # This avoids the Exqutor hook entirely
        if qid == 0:
            # Load a sample of embeddings for percentile computation
            cur.execute('SELECT ps_embedding::text FROM partsupp_deep_10 TABLESAMPLE BERNOULLI(1)')
            sample_vecs_raw = [row[0] for row in cur.fetchall()]
            sample_vecs = np.array([[float(x) for x in v.strip('[]').split(',')] for v in sample_vecs_raw], dtype=np.float32)
            print(f'[{kst()}] loaded {len(sample_vecs)} sample vectors for percentile')
        
        # Compute distances in Python
        dists = np.sqrt(np.sum((sample_vecs - emb) ** 2, axis=1))
        d_target_8m = float(np.percentile(dists, 50))
        
        # True card via SQL (this will trigger hook but with update disabled)
        cur.execute(f"""
        SELECT count(*) FROM partsupp_deep_10
        WHERE (ps_embedding <-> '{vec_str}'::vector) < {d_target_8m}
        """)
        true_card = int(cur.fetchone()[0])
        actual_sel = true_card / total_8m
        
        results.append({
            'query_id': qid,
            'D_target_8m': d_target_8m,
            'true_card_8m': true_card,
            'actual_sel_8m': actual_sel,
        })
        
        if (qid + 1) % 10 == 0:
            print(f'[{kst()}] q{qid+1}/{N_QUERIES} ({time.time()-t0:.0f}s) sel={actual_sel:.4f}')

conn.close()

sels = [r['actual_sel_8m'] for r in results]
print(f'\nactual_sel: mean={np.mean(sels):.4f} std={np.std(sels):.4f} min={min(sels):.4f} max={max(sels):.4f}')

out = f'{CACHE}/phase7_8m_dtarget_recalc.json'
with open(out, 'w') as f:
    json.dump({'total_8m': total_8m, 'n_queries': N_QUERIES, 'results': results, 'elapsed_s': round(time.time()-t0,1)}, f, indent=2)
print(f'[{kst()}] saved {out}, total: {time.time()-t0:.0f}s')
