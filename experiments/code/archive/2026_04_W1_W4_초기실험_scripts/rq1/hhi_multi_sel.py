#!/usr/bin/env python3
"""
실험 C — Per-selectivity Cluster Concentration (HHI) 분석

RANDOM20 gradient를 설명하는 정량적 증거:
  s=0.500에서 HHI ≈ 1/K (균일) → 공간 인식 불필요
  s=0.010에서 HHI ↑↑ (집중) → 공간 인식 필수

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/rq1_hhi_multi_sel.py
"""
import json, time, numpy as np, psycopg, pyarrow.parquet as pq
from datetime import datetime, timedelta, timezone

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'
SELS = [0.001, 0.010, 0.050, 0.100, 0.300, 0.500]
N_QUERIES = 100

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

def emb_to_pgvec(emb):
    return '[' + ','.join(f'{float(x):.7f}' for x in emb) + ']'

print(f'[{kst()}] Per-selectivity HHI analysis')
qp = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()
qs = pq.read_table(f'{CACHE}/query_selectivity.parquet').to_pandas()

conn = psycopg.connect(host='/tmp', port=55436, user='wns41559', dbname='wns41559',
                        autocommit=True, options='-c vector.update_sample_size=off')
t0 = time.time()

with conn.cursor() as cur:
    cur.execute('SET vector.update_sample_size = off')
    cur.execute('SELECT stratum_id, count(*) FROM partsupp_deep_10_subset_1m GROUP BY stratum_id ORDER BY stratum_id')
    cluster_sizes = {row[0]: row[1] for row in cur.fetchall()}
    n_clusters = len(cluster_sizes)
    total_rows = sum(cluster_sizes.values())
    print(f'[{kst()}] {n_clusters} clusters, {total_rows} rows')

    all_results = {}

    for sel in SELS:
        qs_sel = qs[(qs['selectivity'] == sel) & (qs['query_id'] < N_QUERIES)].reset_index(drop=True)
        print(f'\n[{kst()}] === s={sel} ({len(qs_sel)} queries) ===')
        ts = time.time()

        hhi_list, entropy_list, top1_list, top3_list, active_list, true_cards = [], [], [], [], [], []

        for _, row in qs_sel.iterrows():
            qid, D, tc = int(row['query_id']), float(row['D_target']), int(row['true_cardinality'])
            emb = np.asarray(qp.iloc[qid]['embedding'], dtype=np.float32)
            vec_str = emb_to_pgvec(emb)

            cur.execute(f"""
            SELECT stratum_id, count(*) as cnt FROM partsupp_deep_10_subset_1m
            WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}
            GROUP BY stratum_id ORDER BY stratum_id
            """)
            rows = cur.fetchall()
            dist = {}
            for r in rows:
                try:
                    dist[int(r[0])] = int(r[1])
                except (IndexError, TypeError):
                    continue
            total = sum(dist.values())

            if total > 0:
                shares = np.array([dist.get(i, 0) / total for i in range(n_clusters)])
                hhi = float(np.sum(shares ** 2))
                nonzero = shares[shares > 0]
                entropy = -float(np.sum(nonzero * np.log2(nonzero)))
                sorted_s = np.sort(shares)[::-1]
                top1 = float(sorted_s[0])
                top3 = float(np.sum(sorted_s[:3]))
                n_active = int(np.sum(shares > 0))
            else:
                hhi = entropy = top1 = top3 = 0
                n_active = 0

            hhi_list.append(hhi)
            entropy_list.append(entropy)
            top1_list.append(top1)
            top3_list.append(top3)
            active_list.append(n_active)
            true_cards.append(total)

            if (qid + 1) % 25 == 0:
                print(f'[{kst()}]   q{qid+1}/100 hhi={hhi:.4f} top1={top1:.3f} active={n_active}')

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
            'hhi_ratio': float(arr.mean() / (1.0 / n_clusters)),
            'entropy_mean': float(np.mean(entropy_list)),
            'top1_mean': float(np.mean(top1_list)),
            'top3_mean': float(np.mean(top3_list)),
            'active_clusters_mean': float(np.mean(active_list)),
            'elapsed_s': round(time.time() - ts, 1),
        }
        all_results[f's{sel}'] = result
        print(f'[{kst()}] s={sel}: HHI={arr.mean():.4f} (ratio={arr.mean()/(1/n_clusters):.1f}x) '
              f'top1={np.mean(top1_list):.3f} active={np.mean(active_list):.1f} '
              f'true_card_med={int(np.median(true_cards))} ({time.time()-ts:.0f}s)')

conn.close()

# Summary table
print(f'\n{"="*70}')
print(f'SELECTIVITY vs CLUSTER CONCENTRATION')
print(f'{"="*70}')
print(f'{"sel":>7s}  {"HHI":>8s}  {"ratio":>6s}  {"top1":>6s}  {"top3":>6s}  {"active":>7s}  {"true_med":>9s}')
for sel in SELS:
    r = all_results[f's{sel}']
    print(f'{sel:>7.3f}  {r["hhi_mean"]:>8.4f}  {r["hhi_ratio"]:>6.1f}x  '
          f'{r["top1_mean"]:>6.3f}  {r["top3_mean"]:>6.3f}  {r["active_clusters_mean"]:>7.1f}  '
          f'{r["true_card_median"]:>9d}')

print(f'\n[{kst()}] total: {time.time()-t0:.0f}s')

out = f'{CACHE}/hhi_multi_sel_summary.json'
with open(out, 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print(f'[{kst()}] saved {out}')
