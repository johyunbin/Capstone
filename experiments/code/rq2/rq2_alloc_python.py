#!/usr/bin/env python3
"""
RQ2 W1 sprint — Allocation method 비교 측정 (Python 시뮬레이션).

vector.c 의 estimate_cardinality_with_stratified_sampling 의 Python 등가 재현.

핵심 흐름:
1. cluster 별 1000 sample 사전 캐시 (PG SAMPLE 한 번, ~1분)
2. 각 query 마다 (sel, seed, mode):
   a. allocation 결정 (n_i for each cluster)
   b. 캐시에서 random.sample(s_i) — seed 적용
   c. Python 거리 계산 + within D filter
   d. HT estimator: est = Σ_i (hits_i × N_i / s_i)
   e. q_error = max(est/true, true/est)

Modes:
  bernoulli   — TABLESAMPLE BERNOULLI baseline (vector.c hook 그대로)
  equal       — n_i = budget / n_strata (기존 KM20)
  proportional — n_i ∝ N_i
  neyman      — n_i ∝ N_i × σ_i  (Neyman 1934, variance-optimal)
  anti_neyman — n_i ∝ N_i / σ_i  (ablation, suboptimal)

서버: /mnt/hdd0/home/capstone2026/cache/rq2_alloc_python.py
"""
import argparse
import json
import random as pyrandom
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
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20
CACHE_PER_CLUSTER = 500   # cluster 당 캐시할 max sample 수 (alloc max 50 정도라 충분)

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

ALLOC_MODES = ["equal", "proportional", "neyman", "anti_neyman"]
ALL_MODES = ["bernoulli"] + ALLOC_MODES


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def parse_pgvec(s):
    """ '[0.1,0.2,...]' → np.array """
    if isinstance(s, list):
        return np.asarray(s, dtype=np.float32)
    return np.fromstring(s.strip("[]"), sep=",", dtype=np.float32)


def cache_cluster_samples(ds):
    """ cluster 별 LIMIT CACHE_PER_CLUSTER sample 을 numpy array 로 캐시.
    PG vector type cast 의 메모리 누수 우회 위해 cluster 마다 fresh connection 사용.
    """
    print(f"[{kst()}]   caching {ds['name']} cluster samples (LIMIT {CACHE_PER_CLUSTER} per cluster, fresh conn)...")
    samples = {}
    sizes = {}
    sigmas = {}

    with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} GROUP BY stratum_id ORDER BY stratum_id")
        for sid, n in cu.fetchall():
            sizes[sid] = int(n)
        cu.execute(
            f"SELECT stratum_id::int, sigma::float8 FROM vector_stratum_sigma "
            f"WHERE table_name = '{ds['table']}' ORDER BY stratum_id"
        )
        for sid, sg in cu.fetchall():
            sigmas[sid] = float(sg)

    t0 = time.time()
    for sid in range(N_STRATA):
        # fresh connection per cluster (PG vector::real[] cast 의 누적 leak 회피)
        with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {ds['embed_col']}::real[] FROM {ds['table']} "
                f"WHERE stratum_id = {sid} LIMIT {CACHE_PER_CLUSTER}"
            )
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        samples[sid] = np.stack(rows)
    elapsed = time.time() - t0
    total_mb = sum(s.nbytes for s in samples.values()) / 1e6
    print(f"[{kst()}]   cached {sum(s.shape[0] for s in samples.values())} rows ({total_mb:.1f} MB) in {elapsed:.1f}s")
    return samples, sizes, sigmas


def allocate_samples(mode, sizes, sigmas, budget, n_strata):
    """ allocation method 에 따른 cluster 별 sample 수 (max budget) — vector.c 와 동일 logic. """
    w = np.zeros(n_strata)
    for j in range(n_strata):
        N_j = sizes.get(j, 0)
        sg = sigmas.get(j, 0.0)
        if mode == "proportional":
            w[j] = N_j
        elif mode == "neyman":
            w[j] = N_j * sg
        elif mode == "anti_neyman":
            w[j] = N_j / sg if sg > 1e-9 else N_j
        else:  # equal
            w[j] = 1.0
    sum_w = w.sum()
    if sum_w <= 0:
        sum_w = n_strata
        w[:] = 1.0
    f = w / sum_w * budget
    s = np.maximum(f.astype(int), 1)  # 최소 1 보장
    frac = f - f.astype(int)
    extra = budget - int(s.sum())
    if extra > 0:
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    # extra < 0 (over-allocation, 최소 1 보장 효과): 무시
    return s


def stratified_estimate(samples, sizes, alloc, qvec, D, rng):
    """ HT estimator — cluster 별 random sample (numpy), distance filter, weighted sum.
    samples[sid] 는 cluster i 의 모든 row (N_i, dim) 라 N_i 안에서 sample.
    """
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
        # HT weight: N_i / s_i — cluster 안에서 hits/s_i 비율 × N_i 로 cluster 의 hits 추정
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
    return est


def bernoulli_estimate(samples, sizes, qvec, D, rng, budget=SAMPLE_SIZE):
    """ TABLESAMPLE BERNOULLI 의 Python 등가:
        모든 cluster 통합 sample 에서 budget 개 random pick, vec range 안 hits 비율 × total_rows.
    """
    total_rows = sum(sizes.values())
    # cluster 별 사이즈 비율로 budget 분배 → uniform total sampling
    flat = np.concatenate([samples[sid] for sid in range(N_STRATA)], axis=0)
    n = flat.shape[0]
    s = min(int(budget), n)
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    if s == 0:
        return total_rows
    return hits * (total_rows / s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-prefix", default="rq2_alloc")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--modes", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    args = ap.parse_args()

    print(f"[{kst()}] === RQ2 W1 — Allocation method (Python 시뮬레이션) ===")
    use_modes = ALL_MODES if not args.modes else [m for m in ALL_MODES if m in args.modes]
    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d["name"] in args.datasets]
    print(f"[{kst()}] modes: {use_modes}")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")

    # 측정은 numpy 만 사용 (PG 는 cluster sample 캐시 단계에서만 필요)

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        samples, sizes, sigmas = cache_cluster_samples(ds)
        print(f"[{kst()}]   N_i sum={sum(sizes.values())}, σ_i avg={np.mean(list(sigmas.values())):.4f}")

        qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
        qs_full = pq.read_table(ds["query_sel"]).to_pandas()
        qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32) for i in range(len(qp))])
        print(f"[{kst()}]   loaded {len(qp)} queries (dim={qvecs.shape[1]}), {len(qs_full)} sel rows")

        for mode in use_modes:
            t_mode = time.time()
            for sel in SELECTIVITIES:
                qs_sel = qs_full[
                    (np.isclose(qs_full["selectivity"], sel)) &
                    (qs_full["query_id"] < args.n_queries)
                ].sort_values("query_id").reset_index(drop=True)
                if len(qs_sel) == 0:
                    continue
                # allocation 은 mode + sel 에 대해 한 번만 (sel 무관, σ_i 가 sel 0.1 기준)
                if mode != "bernoulli":
                    alloc = allocate_samples(mode, sizes, sigmas, SAMPLE_SIZE, N_STRATA)
                else:
                    alloc = None
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
                            est = bernoulli_estimate(samples, sizes, qvec, D, rng, SAMPLE_SIZE)
                        else:
                            est = stratified_estimate(samples, sizes, alloc, qvec, D, rng)
                        if est > 0 and true_card > 0:
                            qerr = max(est / true_card, true_card / est)
                        else:
                            qerr = None
                        all_rows.append({
                            "dataset": ds["name"], "mode": mode, "selectivity": sel,
                            "seed": seed, "query_id": qid, "D_target": D,
                            "true_card": true_card, "est": est, "q_error": qerr,
                        })
                        qe_list.append(qerr if qerr else float("nan"))
                    elapsed = time.time() - t0
                    valid = sum(1 for q in qe_list if q == q)
                    med = float(np.nanmedian(qe_list)) if valid else float("nan")
                    print(f"[{kst()}]   {ds['name']} {mode:>13} s={sel:.2f} seed={seed} "
                          f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} med_qe={med:.4f}")
            print(f"[{kst()}] {ds['name']} {mode:>13}: total {time.time() - t_mode:.1f}s")

    full_df = pd.DataFrame(all_rows)
    out_pq = CACHE / f"{args.out_prefix}.parquet"
    full_df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(full_df)} rows)")

    print("\n=== mean q_error per (dataset × mode × sel) ===")
    smry = full_df.groupby(["dataset", "mode", "selectivity"])["q_error"].agg(["mean", "std", "median", "count"]).round(4)
    print(smry)

    meta = {
        "kst": kst(),
        "args": vars(args),
        "datasets": [d["name"] for d in use_datasets],
        "modes": use_modes,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "n_queries": args.n_queries,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "elapsed_s": round(time.time() - t_total, 1),
    }
    with open(CACHE / f"{args.out_prefix}_meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
