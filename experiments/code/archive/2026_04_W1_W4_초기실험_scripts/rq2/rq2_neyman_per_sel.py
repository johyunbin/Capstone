#!/usr/bin/env python3
"""
RQ2 보강 — selectivity-specific σ_i 로 Neyman Allocation 측정.

기존 rq2_alloc_python.py 의 σ_i 는 sel=0.10 D_target 단일 anchor (limitation).
본 스크립트는 5 sel 각각의 D_target 에서 σ_i 를 사전 계산 → sel-specific Neyman.

가설: 좁은 sel (s=0.01) 에서 σ_i 가 더 다양해져 Neyman 효과 증가할 가능성.
박세은 (5/5 회의) 의 "분포 알 때 더 개선" 의문에 대한 직접 검증.

서버 사용: /mnt/hdd0/home/capstone2026/cache/rq2_neyman_per_sel.py
산출: cache/rq1/rq2_neyman_per_sel.parquet + meta json
"""
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq
import scipy.stats as sst

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20
CACHE_PER_CLUSTER = 500

DATASETS = [
    {"name": "DEEP", "table": "partsupp_deep_10_subset_1m",
     "vec_col": "ps_embedding", "vec_dim": 96,
     "query_pool": CACHE / "query_pool.parquet",
     "query_sel": CACHE / "query_selectivity.parquet",
     "qid_col": None},
    {"name": "SIFT", "table": "customer_sift_10_phase7_noidx_subset",
     "vec_col": "c_embedding", "vec_dim": 128,
     "query_pool": CACHE / "query_pool_sift.parquet",
     "query_sel": CACHE / "query_selectivity_sift_v2.parquet",
     "qid_col": "query_id"},
]


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def emb_to_pgvec(emb):
    return "[" + ",".join(f"{float(x):.6f}" for x in emb) + "]"


def cache_clusters(ds):
    """KM20 cluster 별 vector cache — fresh conn per cluster (메모리 누수 회피)."""
    samples, sizes = {}, {}
    print(f"[{kst()}]   caching clusters ({CACHE_PER_CLUSTER} per cluster)...")
    t0 = time.time()
    for sid in range(N_STRATA):
        with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=True) as c:
            cu = c.cursor()
            cu.execute(f"SELECT count(*) FROM {ds['table']} WHERE stratum_id={sid}")
            sizes[sid] = cu.fetchone()[0]
            cu.execute(
                f"SELECT {ds['vec_col']}::real[] FROM {ds['table']} "
                f"WHERE stratum_id={sid} ORDER BY random() LIMIT {CACHE_PER_CLUSTER}"
            )
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        samples[sid] = np.stack(rows) if rows else np.zeros((1, ds['vec_dim']), dtype=np.float32)
    print(f"[{kst()}]   cached in {time.time()-t0:.1f}s, N_i sum={sum(sizes.values())}")
    return samples, sizes


def compute_sigma_at_sel(ds, sel_target, qp, qs, n_q=100):
    """주어진 sel 의 D_target 에서 cluster 별 σ_i 계산.

    σ_i² = mean_q[ p_{i,q} × (1 - p_{i,q}) ],
    p_{i,q} = cluster i 안에서 query q 결과에 hit 한 row 수 / N_i
    """
    sub = qs[np.isclose(qs['selectivity'], sel_target)]
    if len(sub) == 0:
        return None, None
    sub = sub.set_index('query_id')

    p_iq = np.zeros((n_q, N_STRATA))
    with psycopg.connect(host='/tmp', port=PORT, dbname=DB, user=USER, autocommit=False) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} GROUP BY stratum_id")
        N_dict = dict(cur.fetchall())
        N_arr = np.array([N_dict.get(i, 0) for i in range(N_STRATA)], dtype=float)

        for q_idx in range(n_q):
            qid = q_idx if ds['qid_col'] is None else int(qp.iloc[q_idx][ds['qid_col']])
            if qid not in sub.index:
                continue
            D = float(sub.loc[qid, 'D_target'])
            qvec_str = emb_to_pgvec(qp.iloc[q_idx]['embedding'])
            cur.execute(
                f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} "
                f"WHERE l2_distance({ds['vec_col']}, %s::vector) < %s GROUP BY stratum_id",
                (qvec_str, D)
            )
            hits = dict(cur.fetchall())
            for sid in range(N_STRATA):
                h = hits.get(sid, 0)
                N = N_arr[sid]
                p_iq[q_idx, sid] = (h / N) if N > 0 else 0.0

    sigma = np.sqrt((p_iq * (1 - p_iq)).mean(axis=0))
    return sigma, N_arr


def neyman_alloc(N_arr, sigma, budget=SAMPLE_SIZE):
    """Neyman: n_i ∝ N_i × σ_i."""
    w = N_arr * sigma
    if w.sum() <= 0:
        n_each = max(budget // len(N_arr), 1)
        return np.full(len(N_arr), n_each, dtype=int)
    f = w / w.sum() * budget
    s = np.maximum(f.astype(int), 1)
    extra = budget - int(s.sum())
    if extra > 0:
        frac = f - f.astype(int)
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


def stratified_estimate(samples, sizes, alloc, qvec, D, rng):
    est = 0.0
    for sid, s_i in enumerate(alloc):
        cache = samples[sid]
        n_cache = cache.shape[0]
        s_i = max(min(int(s_i), n_cache), 1)
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub = cache[idxs]
        d = np.linalg.norm(sub - qvec, axis=1)
        hits = int((d < D).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
    return est


def bernoulli_estimate(samples, sizes, qvec, D, rng):
    flat = np.concatenate([samples[sid] for sid in range(N_STRATA)], axis=0)
    n = flat.shape[0]
    s = min(SAMPLE_SIZE, n)
    if s == 0:
        return sum(sizes.values())
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (sum(sizes.values()) / s)


def main():
    print(f"[{kst()}] === RQ2 sel-specific Neyman 측정 시작 ===")
    t_total = time.time()

    all_rows = []
    sigmas_per_sel = {}

    for ds in DATASETS:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        qp = pq.read_table(ds['query_pool']).to_pandas().reset_index(drop=True)
        qs = pq.read_table(ds['query_sel']).to_pandas()

        samples, sizes = cache_clusters(ds)
        N_arr = np.array([sizes[i] for i in range(N_STRATA)], dtype=float)

        ds_sigmas = {}
        for sel in SELECTIVITIES:
            sigma_sel, _ = compute_sigma_at_sel(ds, sel, qp, qs)
            if sigma_sel is None:
                print(f"[{kst()}]   sel={sel}: no D_target rows, skip")
                continue
            ds_sigmas[str(sel)] = sigma_sel.tolist()
            print(f"[{kst()}]   sel={sel}: σ_i range=[{sigma_sel.min():.4f}, {sigma_sel.max():.4f}], "
                  f"avg={sigma_sel.mean():.4f}, ratio={sigma_sel.max()/max(sigma_sel.min(),1e-9):.2f}x")

            alloc_neyman = neyman_alloc(N_arr, sigma_sel)

            qs_sel = qs[np.isclose(qs['selectivity'], sel)].sort_values('query_id').reset_index(drop=True)
            for seed in SEEDS:
                seed_int = int(seed * 1e9) % (2**31 - 1)
                rng = np.random.default_rng(seed_int)
                t0 = time.time()
                for _, row in qs_sel.iterrows():
                    qid = int(row['query_id'])
                    D = float(row['D_target'])
                    true_card = int(row['true_cardinality'])
                    if ds['qid_col'] is None:
                        qvec = np.asarray(qp.iloc[qid]['embedding'], dtype=np.float32)
                    else:
                        match = qp[qp[ds['qid_col']] == qid]
                        if len(match) == 0:
                            continue
                        qvec = np.asarray(match.iloc[0]['embedding'], dtype=np.float32)

                    est_n = stratified_estimate(samples, sizes, alloc_neyman, qvec, D, rng)
                    est_b = bernoulli_estimate(samples, sizes, qvec, D, rng)

                    qe_n = max(est_n / true_card, true_card / est_n) if est_n > 0 and true_card > 0 else None
                    qe_b = max(est_b / true_card, true_card / est_b) if est_b > 0 and true_card > 0 else None

                    all_rows.append({
                        "dataset": ds['name'], "mode": "neyman_sel_specific",
                        "selectivity": sel, "seed": seed, "query_id": qid,
                        "true_card": true_card, "est": est_n, "q_error": qe_n,
                        "sigma_used_min": float(sigma_sel.min()),
                        "sigma_used_max": float(sigma_sel.max()),
                    })
                    all_rows.append({
                        "dataset": ds['name'], "mode": "bernoulli",
                        "selectivity": sel, "seed": seed, "query_id": qid,
                        "true_card": true_card, "est": est_b, "q_error": qe_b,
                        "sigma_used_min": None, "sigma_used_max": None,
                    })
                print(f"[{kst()}]     sel={sel} seed={seed}: {time.time()-t0:.1f}s")

        sigmas_per_sel[ds['name']] = ds_sigmas

    df = pd.DataFrame(all_rows)
    out_pq = CACHE / "rq2_neyman_per_sel.parquet"
    df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(df)} rows)")

    smry = df.groupby(['dataset', 'mode', 'selectivity'])['q_error'].agg(['mean', 'median', 'count']).round(4)
    print(f"\n=== mean/median q_error per cell ===\n{smry}\n")

    # paired Wilcoxon: neyman_sel_specific vs bernoulli
    print("=== paired Wilcoxon: neyman_sel_specific vs bernoulli ===")
    print(f"{'dataset':>6} {'sel':>6} {'n':>4} {'med_n':>8} {'med_b':>8} {'Δ%':>8} {'p':>10}")
    rows_summary = []
    for ds_name in df['dataset'].unique():
        for sel in SELECTIVITIES:
            n = df[(df['dataset'] == ds_name) & (df['mode'] == 'neyman_sel_specific')
                   & (df['selectivity'] == sel)][['query_id', 'seed', 'q_error']]
            b = df[(df['dataset'] == ds_name) & (df['mode'] == 'bernoulli')
                   & (df['selectivity'] == sel)][['query_id', 'seed', 'q_error']]
            pair = n.merge(b, on=['query_id', 'seed'], suffixes=('_n', '_b')).dropna()
            if len(pair) == 0:
                continue
            try:
                p = float(sst.wilcoxon(pair['q_error_n'], pair['q_error_b'],
                                       alternative='less', zero_method='wilcox').pvalue)
            except Exception:
                p = float('nan')
            mn, mb = float(np.median(pair['q_error_n'])), float(np.median(pair['q_error_b']))
            d_pct = (mb - mn) / mb * 100 if mb > 0 else 0
            print(f"{ds_name:>6} {sel:>6.2f} {len(pair):>4d} {mn:>8.4f} {mb:>8.4f} {d_pct:>+7.2f}% {p:>10.2e}")
            rows_summary.append({
                "dataset": ds_name, "sel": sel, "n_pairs": len(pair),
                "med_neyman": mn, "med_bern": mb,
                "delta_pct": d_pct, "p_value": p,
            })

    out_meta = CACHE / "rq2_neyman_per_sel_meta.json"
    with open(out_meta, 'w') as f:
        json.dump({
            "sel_targets": SELECTIVITIES,
            "sigmas_per_sel": sigmas_per_sel,
            "summary": rows_summary,
            "n_rows": len(df),
            "elapsed_s": round(time.time() - t_total, 1),
            "kst": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        }, f, indent=2)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] === total elapsed {time.time()-t_total:.1f}s ===")


if __name__ == "__main__":
    main()
