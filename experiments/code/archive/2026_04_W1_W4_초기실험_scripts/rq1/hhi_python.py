#!/usr/bin/env python3
"""
Per-selectivity HHI — Python 직접 계산 (Exqutor hook 우회)

vector.c hook이 GROUP BY 쿼리를 변조하므로, 데이터를 Python으로 가져와서
거리 계산 + HHI를 직접 수행.

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/rq1_hhi_python.py
"""
import json, time, numpy as np, psycopg, pyarrow.parquet as pq
from datetime import datetime, timedelta, timezone

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'
SELS = [0.001, 0.010, 0.050, 0.100, 0.300, 0.500]
N_QUERIES = 100

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

print(f'[{kst()}] Per-selectivity HHI analysis (Python distance computation)')

# Load query data
qp = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()
qs = pq.read_table(f'{CACHE}/query_selectivity.parquet').to_pandas()
print(f'[{kst()}] query_pool: {len(qp)}, query_selectivity: {len(qs)}')

# Load table data: stratum_id + embedding from DB
print(f'[{kst()}] Loading 1M rows (stratum_id + embedding) from DB...')
t0 = time.time()

conn = psycopg.connect(host='/tmp', port=55436, user='wns41559', dbname='wns41559',
                        autocommit=True)
cur = conn.cursor()
cur.execute("SET vector.update_sample_size = off")

# Export stratum_id only (embeddings from parquet if available, else DB)
cur.execute("SELECT ps_partkey, stratum_id FROM partsupp_deep_10_subset_1m ORDER BY ps_partkey")
rows = cur.fetchall()
strat_map = {r[0]: r[1] for r in rows}
n_rows = len(strat_map)
n_clusters = len(set(strat_map.values()))
print(f'[{kst()}] Loaded {n_rows} stratum_ids, {n_clusters} clusters ({time.time()-t0:.0f}s)')

# Check if we have a precomputed embedding export
emb_path = f'{CACHE}/subset_1m_embeddings.npy'
try:
    all_embs = np.load(emb_path)
    all_keys = np.load(f'{CACHE}/subset_1m_keys.npy')
    print(f'[{kst()}] Loaded cached embeddings: {all_embs.shape}')
except FileNotFoundError:
    print(f'[{kst()}] No cached embeddings, exporting from DB...')
    cur.execute("SELECT ps_partkey, ps_embedding FROM partsupp_deep_10_subset_1m ORDER BY ps_partkey")
    db_rows = cur.fetchall()
    all_keys = np.array([r[0] for r in db_rows])
    # Parse vector strings to numpy
    all_embs = np.zeros((len(db_rows), 96), dtype=np.float32)
    for i, r in enumerate(db_rows):
        vec_str = r[1]
        if isinstance(vec_str, str):
            vals = vec_str.strip('[]').split(',')
            all_embs[i] = [float(v) for v in vals]
        else:
            all_embs[i] = np.array(vec_str, dtype=np.float32)
        if (i+1) % 200000 == 0:
            print(f'[{kst()}]   parsed {i+1}/{len(db_rows)}')
    np.save(emb_path, all_embs)
    np.save(f'{CACHE}/subset_1m_keys.npy', all_keys)
    print(f'[{kst()}] Saved embeddings cache: {all_embs.shape} ({time.time()-t0:.0f}s)')

conn.close()

# Build stratum array aligned with embeddings
strat_arr = np.array([strat_map.get(k, -1) for k in all_keys])
print(f'[{kst()}] stratum array built, valid: {np.sum(strat_arr >= 0)}/{len(strat_arr)}')

# Query embeddings
query_embs = np.stack([np.asarray(qp.iloc[i]['embedding'], dtype=np.float32) for i in range(N_QUERIES)])
print(f'[{kst()}] Query embeddings: {query_embs.shape}')

# Per-selectivity HHI computation
all_results = {}
t_total = time.time()

for sel in SELS:
    qs_sel = qs[(qs['selectivity'] == sel) & (qs['query_id'] < N_QUERIES)].reset_index(drop=True)
    print(f'\n[{kst()}] === s={sel} ({len(qs_sel)} queries) ===')
    ts = time.time()

    hhi_list, entropy_list, top1_list, top3_list, active_list, true_cards = [], [], [], [], [], []

    for _, row in qs_sel.iterrows():
        qid = int(row['query_id'])
        D = float(row['D_target'])

        # Compute L2 distances
        dists = np.sqrt(np.sum((all_embs - query_embs[qid]) ** 2, axis=1))
        mask = dists < D
        matches = strat_arr[mask]
        total = len(matches)

        if total > 0:
            counts = np.bincount(matches[matches >= 0], minlength=n_clusters)
            shares = counts / total
            hhi = float(np.sum(shares ** 2))
            nonzero = shares[shares > 0]
            entropy = -float(np.sum(nonzero * np.log2(nonzero)))
            sorted_s = np.sort(shares)[::-1]
            top1 = float(sorted_s[0])
            top3 = float(np.sum(sorted_s[:3]))
            n_active = int(np.sum(shares > 0))
        else:
            hhi = entropy = top1 = top3 = 0.0
            n_active = 0

        hhi_list.append(hhi)
        entropy_list.append(entropy)
        top1_list.append(top1)
        top3_list.append(top3)
        active_list.append(n_active)
        true_cards.append(total)

        if (qid + 1) % 25 == 0:
            print(f'[{kst()}]   q{qid+1}/100 hhi={hhi:.4f} top1={top1:.3f} active={n_active} matches={total}')

    arr = np.array(hhi_list)
    result = {
        'selectivity': sel,
        'n_queries': len(qs_sel),
        'true_card_median': int(np.median(true_cards)),
        'hhi_mean': float(arr.mean()),
        'hhi_std': float(arr.std()),
        'hhi_min': float(arr.min()),
        'hhi_max': float(arr.max()),
        'hhi_uniform': 1.0 / n_clusters,
        'hhi_ratio': float(arr.mean() / (1.0 / n_clusters)) if arr.mean() > 0 else 0,
        'entropy_mean': float(np.mean(entropy_list)),
        'top1_mean': float(np.mean(top1_list)),
        'top3_mean': float(np.mean(top3_list)),
        'active_clusters_mean': float(np.mean(active_list)),
        'elapsed_s': round(time.time() - ts, 1),
    }
    all_results[f's{sel}'] = result
    print(f'[{kst()}] s={sel}: HHI={arr.mean():.4f} (ratio={result["hhi_ratio"]:.1f}x) '
          f'top1={np.mean(top1_list):.3f} active={np.mean(active_list):.1f} '
          f'true_card_med={int(np.median(true_cards))} ({time.time()-ts:.0f}s)')

# Summary table
print(f'\n{"="*70}')
print(f'SELECTIVITY vs CLUSTER CONCENTRATION (HHI)')
print(f'{"="*70}')
print(f'{"sel":>7s}  {"HHI":>8s}  {"ratio":>6s}  {"top1":>6s}  {"top3":>6s}  {"active":>7s}  {"true_med":>9s}')
for sel in SELS:
    r = all_results[f's{sel}']
    print(f'{sel:>7.3f}  {r["hhi_mean"]:>8.4f}  {r["hhi_ratio"]:>6.1f}x  '
          f'{r["top1_mean"]:>6.3f}  {r["top3_mean"]:>6.3f}  {r["active_clusters_mean"]:>7.1f}  '
          f'{r["true_card_median"]:>9d}')

elapsed = time.time() - t_total
print(f'\n[{kst()}] total: {elapsed:.0f}s')

out = f'{CACHE}/hhi_python_summary.json'
with open(out, 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print(f'[{kst()}] saved {out}')
