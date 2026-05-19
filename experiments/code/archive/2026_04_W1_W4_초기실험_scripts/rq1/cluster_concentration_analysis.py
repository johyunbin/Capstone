#!/usr/bin/env python3
"""
Cluster Concentration vs Q-error 분석

교수님 직관 검증: "데이터가 쏠려있으면 uniform sampling이 더 나빠지는가?"

각 query의 true matches가 KM20 cluster에 얼마나 집중되어 있는지 (Herfindahl index)
측정하고, 집중도와 BERN/STRAT Q-error 차이의 상관을 분석한다.

기존 Phase 6 Step 4 데이터 (1M subset, stratum_id 부여됨) 에서 즉시 계산.
"""
import json, time, numpy as np, psycopg, pyarrow.parquet as pq
import scipy.stats as sst
from datetime import datetime, timedelta, timezone

CACHE = '/mnt/hdd0/home/capstone2026/cache/rq1'

def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime('%H:%M:%S')

def emb_to_pgvec(emb):
    return '[' + ','.join(f'{float(x):.7f}' for x in emb) + ']'

print(f'[{kst()}] Cluster concentration vs Q-error analysis')

# Load existing Phase 6 Step 4 results
bern = pq.read_table(f'{CACHE}/phase6_bern_native_v2.parquet').to_pandas()
strat = pq.read_table(f'{CACHE}/phase6_strat_km20_native.parquet').to_pandas()
qp = pq.read_table(f'{CACHE}/query_pool.parquet').to_pandas()
qs = pq.read_table(f'{CACHE}/query_selectivity.parquet').to_pandas()

print(f'[{kst()}] BERN: {len(bern)} rows, STRAT: {len(strat)} rows')

# Connect to DB to get cluster distribution of true matches
conn = psycopg.connect(
    host='/tmp', port=55436, user='wns41559', dbname='wns41559',
    autocommit=True,
    options='-c vector.update_sample_size=off'
)

# For each query × selectivity, compute Herfindahl index of true matches across clusters
print(f'[{kst()}] Computing cluster concentration for each query...')
t0 = time.time()

results = []
with conn.cursor() as cur:
    cur.execute('SET vector.update_sample_size = off')
    cur.execute('TRUNCATE TABLE exqutor_qerror')

    # Get cluster sizes
    cur.execute('SELECT stratum_id, count(*) FROM partsupp_deep_10_subset_1m GROUP BY stratum_id ORDER BY stratum_id')
    cluster_sizes = {row[0]: row[1] for row in cur.fetchall()}
    total_rows = sum(cluster_sizes.values())
    n_clusters = len(cluster_sizes)
    print(f'[{kst()}] {n_clusters} clusters, total {total_rows} rows')
    print(f'[{kst()}] Cluster sizes: min={min(cluster_sizes.values())}, max={max(cluster_sizes.values())}, '
          f'ratio={max(cluster_sizes.values())/min(cluster_sizes.values()):.1f}x')

    # Focus on s=0.500 (our anchor selectivity)
    qs_sel = qs[(qs['selectivity'] == 0.500) & (qs['query_id'] < 100)].reset_index(drop=True)

    for _, row in qs_sel.iterrows():
        qid = int(row['query_id'])
        D = float(row['D_target'])
        true_card = int(row['true_cardinality'])

        emb = np.asarray(qp.iloc[qid]['embedding'], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        # Get cluster distribution of true matches
        cur.execute(f"""
        SELECT stratum_id, count(*) as cnt
        FROM partsupp_deep_10_subset_1m
        WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}
        GROUP BY stratum_id
        ORDER BY stratum_id
        """)
        cluster_dist = {row[0]: row[1] for row in cur.fetchall()}

        # Herfindahl Index (concentration)
        total_matches = sum(cluster_dist.values())
        if total_matches > 0:
            shares = np.array([cluster_dist.get(i, 0) / total_matches for i in range(n_clusters)])
            hhi = float(np.sum(shares ** 2))  # 1/K for uniform, 1.0 for single cluster
            # Entropy
            nonzero = shares[shares > 0]
            entropy = -float(np.sum(nonzero * np.log2(nonzero)))
            # Top-1 and Top-3 share
            sorted_shares = np.sort(shares)[::-1]
            top1_share = float(sorted_shares[0])
            top3_share = float(np.sum(sorted_shares[:3]))
            n_active_clusters = int(np.sum(shares > 0))
        else:
            hhi = entropy = top1_share = top3_share = 0
            n_active_clusters = 0

        # Get Q-errors from existing data
        bern_row = bern[(bern['query_id'] == qid) & (bern['selectivity'] == 0.500)]
        strat_row = strat[(strat['query_id'] == qid) & (strat['selectivity'] == 0.500)]

        qe_bern = float(bern_row['q_error_hook'].iloc[0]) if len(bern_row) > 0 and bern_row['q_error_hook'].notna().iloc[0] else None
        qe_strat = float(strat_row['q_error_hook'].iloc[0]) if len(strat_row) > 0 and strat_row['q_error_hook'].notna().iloc[0] else None

        results.append({
            'query_id': qid,
            'true_card': total_matches,
            'hhi': hhi,
            'entropy': entropy,
            'top1_share': top1_share,
            'top3_share': top3_share,
            'n_active_clusters': n_active_clusters,
            'qe_bern': qe_bern,
            'qe_strat': qe_strat,
            'qe_diff': (qe_bern - qe_strat) if qe_bern and qe_strat else None,
            'qe_diff_pct': ((qe_bern - qe_strat) / qe_bern * 100) if qe_bern and qe_strat and qe_bern > 0 else None,
        })

        if (qid + 1) % 20 == 0:
            print(f'[{kst()}] q{qid+1}/100 ({time.time()-t0:.0f}s) hhi={hhi:.4f} top1={top1_share:.3f}')

conn.close()

# Analysis
import pandas as pd
df = pd.DataFrame(results)
valid = df.dropna(subset=['qe_bern', 'qe_strat', 'hhi'])

print(f'\n{"="*60}')
print(f'CLUSTER CONCENTRATION ANALYSIS (s=0.500, {len(valid)} queries)')
print(f'{"="*60}')

# Descriptive stats
print(f'\nCluster concentration (Herfindahl Index):')
print(f'  mean={valid["hhi"].mean():.4f}, std={valid["hhi"].std():.4f}')
print(f'  min={valid["hhi"].min():.4f}, max={valid["hhi"].max():.4f}')
print(f'  (1/K={1/n_clusters:.4f} = perfectly uniform, 1.0 = single cluster)')

print(f'\nTop-1 cluster share:')
print(f'  mean={valid["top1_share"].mean():.3f}, max={valid["top1_share"].max():.3f}')

print(f'\nActive clusters (of {n_clusters}):')
print(f'  mean={valid["n_active_clusters"].mean():.1f}, min={valid["n_active_clusters"].min()}')

# Correlation: concentration vs Q-error improvement
rho_hhi, p_hhi = sst.spearmanr(valid['hhi'], valid['qe_diff_pct'])
rho_top1, p_top1 = sst.spearmanr(valid['top1_share'], valid['qe_diff_pct'])
rho_entropy, p_entropy = sst.spearmanr(valid['entropy'], valid['qe_diff_pct'])

print(f'\n--- Correlation: concentration vs STRAT improvement ---')
print(f'Herfindahl vs diff%: rho={rho_hhi:+.3f}, p={p_hhi:.4f}')
print(f'Top-1 share vs diff%: rho={rho_top1:+.3f}, p={p_top1:.4f}')
print(f'Entropy vs diff%: rho={rho_entropy:+.3f}, p={p_entropy:.4f}')

# Group comparison: high vs low concentration
median_hhi = valid['hhi'].median()
high_conc = valid[valid['hhi'] >= median_hhi]
low_conc = valid[valid['hhi'] < median_hhi]

print(f'\n--- Group comparison (median split on HHI={median_hhi:.4f}) ---')
print(f'High concentration ({len(high_conc)} queries, "쏠린" 데이터):')
print(f'  BERN Q-error median: {high_conc["qe_bern"].median():.4f}')
print(f'  STRAT Q-error median: {high_conc["qe_strat"].median():.4f}')
print(f'  Improvement: {high_conc["qe_diff_pct"].median():+.2f}%')

print(f'Low concentration ({len(low_conc)} queries, "일반" 데이터):')
print(f'  BERN Q-error median: {low_conc["qe_bern"].median():.4f}')
print(f'  STRAT Q-error median: {low_conc["qe_strat"].median():.4f}')
print(f'  Improvement: {low_conc["qe_diff_pct"].median():+.2f}%')

# Statistical test: is improvement larger in high-concentration group?
try:
    stat, p_group = sst.mannwhitneyu(
        high_conc['qe_diff_pct'].dropna(),
        low_conc['qe_diff_pct'].dropna(),
        alternative='greater'
    )
    print(f'\nMann-Whitney U (high > low improvement): p={p_group:.4f}')
except Exception as e:
    print(f'\nMann-Whitney failed: {e}')

# Save results
out = f'{CACHE}/cluster_concentration_analysis.json'
summary = {
    'n_queries': len(valid),
    'n_clusters': n_clusters,
    'cluster_sizes': cluster_sizes,
    'hhi_stats': {
        'mean': float(valid['hhi'].mean()),
        'std': float(valid['hhi'].std()),
        'min': float(valid['hhi'].min()),
        'max': float(valid['hhi'].max()),
    },
    'correlations': {
        'hhi_vs_diff': {'rho': rho_hhi, 'p': p_hhi},
        'top1_vs_diff': {'rho': rho_top1, 'p': p_top1},
        'entropy_vs_diff': {'rho': rho_entropy, 'p': p_entropy},
    },
    'group_comparison': {
        'high_conc_improvement_median': float(high_conc['qe_diff_pct'].median()),
        'low_conc_improvement_median': float(low_conc['qe_diff_pct'].median()),
    },
    'per_query': results,
}
with open(out, 'w') as f:
    json.dump(summary, f, indent=2, default=str)
print(f'\n[{kst()}] saved {out}')
print(f'[{kst()}] total: {time.time()-t0:.0f}s')
