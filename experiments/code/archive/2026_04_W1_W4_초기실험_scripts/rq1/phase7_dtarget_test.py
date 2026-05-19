#!/usr/bin/env python3
"""Phase 7 D_target 재계산 — SQL only (TRUNCATE 우회)."""
import json, numpy as np, psycopg, pyarrow.parquet as pq, time
from datetime import datetime, timedelta, timezone

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

def emb_to_pgvec(emb):
    return '[' + ','.join(f'{float(x):.7f}' for x in emb) + ']'

qp = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()
qs = pq.read_table(f'{CACHE}/query_selectivity.parquet').to_pandas()
print(f'[{kst()}] D_target recalc test')

conn = psycopg.connect(host='/tmp', port=55436, user='wns41559', dbname='wns41559', autocommit=True)

with conn.cursor() as cur:
    cur.execute('SET vector.update_sample_size = off')
    cur.execute('TRUNCATE TABLE exqutor_qerror')
    cur.execute('SELECT count(*) FROM partsupp_deep_10_phase7_8m_subset')
    total = cur.fetchone()[0]
    print(f'[{kst()}] 8M rows={total}')

    emb = np.asarray(qp.iloc[0]['embedding'], dtype=np.float32)
    vec_str = emb_to_pgvec(emb)

    # 1M D_target for comparison
    d_1m = float(qs[(qs['query_id']==0) & (qs['selectivity']==0.5)]['D_target'].iloc[0])
    print(f'[{kst()}] 1M D_target(q0,s=0.5) = {d_1m:.4f}')

    # Count at 1M D_target on 8M
    sql = f"SELECT count(*) FROM partsupp_deep_10_phase7_8m_subset WHERE (ps_embedding <-> '{vec_str}'::vector) < {d_1m}"
    cur.execute(sql)
    c1 = cur.fetchone()[0]
    print(f'[{kst()}] 8M count at 1M_D_target = {c1} (sel={c1/total:.6f})')

    # Compute 8M percentile via SQL
    cur.execute('SELECT setseed(0.42)')
    sql2 = (
        "SELECT percentile_cont(0.5) WITHIN GROUP ("
        f"ORDER BY (ps_embedding <-> '{vec_str}'::vector)"
        ") FROM ("
        "SELECT ps_embedding FROM partsupp_deep_10_phase7_8m_subset "
        "ORDER BY random() LIMIT 80000) s"
    )
    cur.execute(sql2)
    d_8m = float(cur.fetchone()[0])
    print(f'[{kst()}] 8M D_target(q0,sampled) = {d_8m:.4f}')

    # Count at 8M D_target
    sql3 = f"SELECT count(*) FROM partsupp_deep_10_phase7_8m_subset WHERE (ps_embedding <-> '{vec_str}'::vector) < {d_8m}"
    cur.execute(sql3)
    c2 = cur.fetchone()[0]
    print(f'[{kst()}] 8M count at 8M_D_target = {c2} (sel={c2/total:.6f})')

conn.close()
print(f'[{kst()}] done')
