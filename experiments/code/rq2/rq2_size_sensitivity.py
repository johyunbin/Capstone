#!/usr/bin/env python3
"""
RQ2 W1 sprint #4 — Sample size sensitivity 측정.

가설 H2-S: sample_size 작을수록 KM20-Proportional 의 BERN 대비 개선이 크다.

측정:
- DEEP 1M + SIFT 1.5M
- sample_size: 100, 385, 1000, 3000 (4점)
- selectivity: 0.01, 0.05, 0.50 (3점, 시간 절약)
- seed: 5 / query: 100
- mode: bernoulli vs proportional (KM20-Proportional)

서버: /mnt/hdd0/home/capstone2026/cache/rq2_size_sensitivity.py
"""
import argparse
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.50]
SAMPLE_SIZES = [100, 385, 1000, 3000]
N_STRATA = 20
CACHE_PER_CLUSTER = 500  # 충분 (max alloc ~150 at sample_size=3000)

DATASETS = [
    {
        "name": "DEEP",
        "table": "partsupp_deep_10_subset_1m",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity.parquet",
    },
    {
        "name": "SIFT",
        "table": "customer_sift_10_phase7_noidx_subset",
        "embed_col": "c_embedding",
        "vec_dim": 128,
        "query_pool": CACHE / "query_pool_sift.parquet",
        "query_sel": CACHE / "query_selectivity_sift_v2.parquet",
    },
]


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def cache_cluster_samples(ds):
    """ cluster 별 LIMIT 500 sample, fresh conn per cluster (PG memory leak 우회). """
    print(f"[{kst()}]   caching {ds['name']} ({ds['vec_dim']}d, max sample 3000 → cache 500/cluster 충분)...")
    samples = {}
    sizes = {}

    with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} GROUP BY stratum_id ORDER BY stratum_id")
        for sid, n in cu.fetchall():
            sizes[sid] = int(n)

    # cache_per_cluster 를 sample_size 3000 까지 충분하게 — proportional 의 max 분배 시
    # cluster 가장 큰 N=148K (SIFT) 가 budget 3000 의 비율 148/1500 ≈ 10% → 300 sample 필요
    cache_n = max(CACHE_PER_CLUSTER, 400)
    t0 = time.time()
    for sid in range(N_STRATA):
        with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {ds['embed_col']}::real[] FROM {ds['table']} "
                f"WHERE stratum_id = {sid} LIMIT {cache_n}"
            )
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        samples[sid] = np.stack(rows)
    elapsed = time.time() - t0
    total_mb = sum(s.nbytes for s in samples.values()) / 1e6
    print(f"[{kst()}]   cached {sum(s.shape[0] for s in samples.values())} rows ({total_mb:.1f} MB) in {elapsed:.1f}s")
    return samples, sizes


def allocate_proportional(sizes, budget, n_strata):
    """ n_i ∝ N_i, 최소 1 보장, largest-remainder 분배. """
    w = np.array([sizes.get(j, 0) for j in range(n_strata)], dtype=float)
    sum_w = w.sum() if w.sum() > 0 else n_strata
    f = w / sum_w * budget
    s = np.maximum(f.astype(int), 1)
    frac = f - f.astype(int)
    extra = budget - int(s.sum())
    if extra > 0:
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


def stratified_proportional_estimate(samples, sizes, alloc, qvec, D, rng):
    """ HT estimator. """
    est = 0.0
    for sid, s_i in enumerate(alloc):
        cache = samples[sid]
        n_cache = cache.shape[0]
        s_i = min(int(s_i), n_cache)
        if s_i < 1:
            s_i = 1
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub = cache[idxs]
        d = np.linalg.norm(sub - qvec, axis=1)
        hits = int((d < D).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
    return est


def bernoulli_estimate(samples, sizes, qvec, D, rng, budget):
    """ all clusters 통합 sample 에서 budget 개 random pick. """
    total_rows = sum(sizes.values())
    flat = np.concatenate([samples[sid] for sid in range(N_STRATA)], axis=0)
    n = flat.shape[0]
    s = min(int(budget), n)
    if s < 1:
        return total_rows
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (total_rows / s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-prefix", default="rq2_size_sensitivity")
    ap.add_argument("--n-queries", type=int, default=100)
    args = ap.parse_args()

    print(f"[{kst()}] === RQ2 W1 — Sample size sensitivity ===")
    print(f"[{kst()}] sample_sizes={SAMPLE_SIZES}, sel={SELECTIVITIES}, seeds={SEEDS}")

    all_rows = []
    t_total = time.time()

    for ds in DATASETS:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        samples, sizes = cache_cluster_samples(ds)
        qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
        qs_full = pq.read_table(ds["query_sel"]).to_pandas()
        qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32) for i in range(len(qp))])

        for ssize in SAMPLE_SIZES:
            t_size = time.time()
            alloc = allocate_proportional(sizes, ssize, N_STRATA)
            for mode in ["bernoulli", "proportional"]:
                for sel in SELECTIVITIES:
                    qs_sel = qs_full[
                        (np.isclose(qs_full["selectivity"], sel)) &
                        (qs_full["query_id"] < args.n_queries)
                    ].sort_values("query_id").reset_index(drop=True)
                    if len(qs_sel) == 0:
                        continue
                    for seed in SEEDS:
                        seed_int = int(seed * 10**9) % (2**31 - 1)
                        rng = np.random.default_rng(seed_int)
                        t0 = time.time()
                        qe_list = []
                        for _, row in qs_sel.iterrows():
                            qid = int(row["query_id"])
                            D = float(row["D_target"])
                            true_card = int(row["true_cardinality"])
                            qvec = qvecs[qid]
                            if mode == "bernoulli":
                                est = bernoulli_estimate(samples, sizes, qvec, D, rng, ssize)
                            else:
                                est = stratified_proportional_estimate(samples, sizes, alloc, qvec, D, rng)
                            if est > 0 and true_card > 0:
                                qerr = max(est / true_card, true_card / est)
                            else:
                                qerr = None
                            all_rows.append({
                                "dataset": ds["name"], "sample_size": ssize, "mode": mode,
                                "selectivity": sel, "seed": seed, "query_id": qid,
                                "true_card": true_card, "est": est, "q_error": qerr,
                            })
                            qe_list.append(qerr if qerr else float("nan"))
                        elapsed = time.time() - t0
                        valid = sum(1 for q in qe_list if q == q)
                        med = float(np.nanmedian(qe_list)) if valid else float("nan")
                        print(f"[{kst()}]   {ds['name']} ssize={ssize:>4} {mode:>13} s={sel:.2f} seed={seed} "
                              f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} med_qe={med:.4f}")
            print(f"[{kst()}] {ds['name']} ssize={ssize}: total {time.time() - t_size:.1f}s")

    full_df = pd.DataFrame(all_rows)
    out_pq = CACHE / f"{args.out_prefix}.parquet"
    full_df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(full_df)} rows)")

    # summary: mean q_error per (dataset × ssize × mode × sel) → KM20 vs BERN delta
    print("\n=== KM20-Proportional vs BERN (BERN = baseline) — Δ% ===")
    print(f"{'dataset':>7} | {'sel':>5} | {'ssize':>5} | {'BERN':>8} | {'Prop':>8} | {'Δ%':>8}")
    for ds_name in ["DEEP", "SIFT"]:
        for sel in SELECTIVITIES:
            for ssize in SAMPLE_SIZES:
                b = full_df[
                    (full_df.dataset == ds_name) & (full_df.sample_size == ssize) &
                    (full_df["mode"] == "bernoulli") & (np.isclose(full_df.selectivity, sel))
                ]["q_error"].dropna().mean()
                p = full_df[
                    (full_df.dataset == ds_name) & (full_df.sample_size == ssize) &
                    (full_df["mode"] == "proportional") & (np.isclose(full_df.selectivity, sel))
                ]["q_error"].dropna().mean()
                delta = (p - b) / b * 100 if b > 0 else float("nan")
                print(f"{ds_name:>7} | {sel:>5.2f} | {ssize:>5} | {b:>8.4f} | {p:>8.4f} | {delta:>+7.2f}%")

    meta = {
        "kst": kst(),
        "args": vars(args),
        "datasets": [d["name"] for d in DATASETS],
        "sample_sizes": SAMPLE_SIZES,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "n_queries": args.n_queries,
        "elapsed_s": round(time.time() - t_total, 1),
    }
    with open(CACHE / f"{args.out_prefix}_meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
