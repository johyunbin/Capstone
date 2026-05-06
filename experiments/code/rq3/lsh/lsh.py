#!/usr/bin/env python3
"""
RQ3 W1 sprint — LSH (Locality-Sensitive Hashing) Random Hyperplane stratification.

P4 = experiment #6 (A. LSH).

Random Hyperplane LSH (Charikar 2002, cosine LSH):
- 5 hyperplanes → 2^5 = 32 raw buckets → mod 20 → 20 strata (k=20 일치)
- HYPERPLANES_SEED=0 결정론적
- 학습 X (random projection 1회), pure numpy

측정 흐름 (rq2_alloc_python.py 패턴):
1. Precompute LSH bucket — 전체 테이블 chunk-scan (OFFSET + fresh conn 으로 PG vector cast leak 회피)
   각 row 의 LSH bucket 계산 + bucket 별 reservoir sampling (uniform random, CACHE_PER_CLUSTER 개)
   결과: samples[bucket_id] = (s, dim) array, sizes[bucket_id] = exact N_i
2. HT estimator: rq2 와 완전 동일. cluster sample → distance filter → weighted sum.
3. Bernoulli baseline: concat all-bucket cache → uniform random budget pick.

Modes:
  bernoulli           — TABLESAMPLE BERNOULLI 등가 (no stratification)
  lsh_proportional    — LSH 20 buckets + proportional allocation

서버 실행: scp 후
    python3 lsh.py --datasets DEEP SIFT --modes bernoulli lsh_proportional

산출: rq3_lsh.parquet + rq3_lsh_meta.json
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
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20
N_HYPERPLANES = 5  # ceil(log2(20)) = 5 → 32 raw buckets, mod 20 → 20 final
HYPERPLANES_SEED = 0
RESERVOIR_SEED = 0
CACHE_PER_CLUSTER = 500
SCAN_CHUNK = 50000  # rows per fresh PG conn (vector::real[] cast leak 회피)

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

ALL_MODES = ["bernoulli", "lsh_proportional"]


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def make_hyperplanes(dim, n_hp=N_HYPERPLANES, seed=HYPERPLANES_SEED):
    """Random Gaussian hyperplanes for cosine LSH (Charikar 2002)."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_hp, dim)).astype(np.float32)


def lsh_bucket(vecs, hyperplanes, n_strata=N_STRATA):
    """LSH bucket id per row.
    vecs: (N, dim) float32 — input vectors
    hyperplanes: (n_hp, dim) — random hyperplanes (W)
    Returns: (N,) int in [0, n_strata)

    raw_id = sum_j (sign(W_j · v) > 0) << j   ∈ [0, 2^n_hp)
    final  = raw_id mod n_strata               ∈ [0, n_strata)
    """
    n_hp = hyperplanes.shape[0]
    proj = vecs @ hyperplanes.T  # (N, n_hp)
    bits = (proj > 0).astype(np.int32)  # (N, n_hp)
    weights = (1 << np.arange(n_hp)).astype(np.int32)  # [1, 2, 4, 8, 16]
    raw_ids = (bits * weights).sum(axis=1)  # 0 ~ 2^n_hp - 1
    return raw_ids % n_strata


def precompute_lsh_cache(ds, hyperplanes, n_strata=N_STRATA, cache_per=CACHE_PER_CLUSTER, chunk=SCAN_CHUNK):
    """전체 테이블 scan + LSH bucketing + bucket 별 reservoir sampling.

    PG vector::real[] cast 의 누적 leak 회피를 위해 chunk 마다 fresh connection.
    OFFSET 기반 pagination — sequential scan 의 한 번 cost.
    Reservoir sampling 으로 bucket 안에서 uniform random `cache_per` 개 추출.

    Returns:
        samples: dict {bucket_id: np.ndarray(s, dim)}  s ≤ cache_per, uniform random
        sizes:   dict {bucket_id: N_i}                exact count per bucket
    """
    print(f"[{kst()}]   precomputing LSH ({n_strata} buckets via {hyperplanes.shape[0]} hyperplanes, mod {n_strata})...")
    rng = np.random.default_rng(RESERVOIR_SEED)
    sizes = {b: 0 for b in range(n_strata)}
    samples_buckets = {b: [] for b in range(n_strata)}  # reservoir cache (list → stack 후)

    offset = 0
    total_seen = 0
    t0 = time.time()
    while True:
        with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {ds['embed_col']}::real[] FROM {ds['table']} OFFSET {offset} LIMIT {chunk}"
            )
            rows = cu.fetchall()
        if not rows:
            break
        embs = np.stack([np.asarray(r[0], dtype=np.float32) for r in rows])
        bucket_ids = lsh_bucket(embs, hyperplanes, n_strata)
        for i in range(len(rows)):
            b = int(bucket_ids[i])
            sizes[b] += 1
            cache = samples_buckets[b]
            if len(cache) < cache_per:
                cache.append(embs[i])
            else:
                # Algorithm R reservoir sampling — replace with prob cache_per / sizes[b]
                j = int(rng.integers(0, sizes[b]))
                if j < cache_per:
                    cache[j] = embs[i]
        total_seen += len(rows)
        offset += chunk
        if total_seen % (chunk * 4) == 0:
            print(f"[{kst()}]     scanned {total_seen} rows ({time.time() - t0:.1f}s)...")
        if len(rows) < chunk:
            break

    samples = {}
    for b in range(n_strata):
        if samples_buckets[b]:
            samples[b] = np.stack(samples_buckets[b])
        else:
            samples[b] = np.zeros((0, ds["vec_dim"]), dtype=np.float32)

    elapsed = time.time() - t0
    sz_arr = np.array([sizes[b] for b in range(n_strata)])
    cz_arr = np.array([samples[b].shape[0] for b in range(n_strata)])
    print(f"[{kst()}]   scanned {total_seen} rows in {elapsed:.1f}s")
    print(f"[{kst()}]   bucket N_i: min={sz_arr.min()} max={sz_arr.max()} "
          f"mean={sz_arr.mean():.0f} std={sz_arr.std():.0f}")
    print(f"[{kst()}]   cache size: min={cz_arr.min()} max={cz_arr.max()} "
          f"(target {cache_per} per bucket)")
    if sz_arr.min() == 0:
        print(f"[{kst()}]   ⚠️  empty buckets: {[b for b in range(n_strata) if sizes[b] == 0]}")
    return samples, sizes


def allocate_proportional(sizes, budget, n_strata=N_STRATA):
    """Proportional allocation: n_i ∝ N_i. rq2 와 동일 logic."""
    w = np.array([sizes.get(j, 0) for j in range(n_strata)], dtype=np.float64)
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
    return s


def stratified_estimate(samples, sizes, alloc, qvec, D, rng):
    """HT estimator — cluster 별 random sample, distance filter, weighted sum.
    rq2_alloc_python.py 와 완전 동일. bucket 정의(KM20 vs LSH)만 외부에서 다름.
    """
    est = 0.0
    for sid, s_i in enumerate(alloc):
        cache = samples[sid]
        n_cache = cache.shape[0]
        if n_cache == 0:
            continue  # empty bucket — skip
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


def bernoulli_estimate(samples, sizes, qvec, D, rng, budget=SAMPLE_SIZE):
    """Bernoulli (= RANDOM20 baseline w/o spatial info) — concat all bucket cache, uniform pick."""
    total_rows = sum(sizes.values())
    flat_list = [samples[sid] for sid in range(N_STRATA) if samples[sid].shape[0] > 0]
    if not flat_list:
        return total_rows
    flat = np.concatenate(flat_list, axis=0)
    n = flat.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return total_rows
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (total_rows / s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-prefix", default="rq3_lsh")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--modes", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    args = ap.parse_args()

    print(f"[{kst()}] === RQ3 #6 — LSH (Random Hyperplane, k={N_STRATA}, "
          f"{N_HYPERPLANES} hyperplanes, mod {N_STRATA}) ===")
    use_modes = ALL_MODES if not args.modes else [m for m in ALL_MODES if m in args.modes]
    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d["name"] in args.datasets]
    print(f"[{kst()}] modes: {use_modes}")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        hyperplanes = make_hyperplanes(ds["vec_dim"])
        samples, sizes = precompute_lsh_cache(ds, hyperplanes)
        total_n = sum(sizes.values())
        print(f"[{kst()}]   total N = {total_n}")

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
                if mode == "lsh_proportional":
                    alloc = allocate_proportional(sizes, SAMPLE_SIZE, N_STRATA)
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
                    print(f"[{kst()}]   {ds['name']} {mode:>16} s={sel:.2f} seed={seed} "
                          f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} med_qe={med:.4f}")
            print(f"[{kst()}] {ds['name']} {mode:>16}: total {time.time() - t_mode:.1f}s")

    full_df = pd.DataFrame(all_rows)
    out_pq = CACHE / f"{args.out_prefix}.parquet"
    full_df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(full_df)} rows)")

    print("\n=== mean q_error per (dataset × mode × sel) ===")
    smry = full_df.groupby(["dataset", "mode", "selectivity"])["q_error"].agg(
        ["mean", "std", "median", "count"]
    ).round(4)
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
        "n_hyperplanes": N_HYPERPLANES,
        "hyperplanes_seed": HYPERPLANES_SEED,
        "reservoir_seed": RESERVOIR_SEED,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "scan_chunk": SCAN_CHUNK,
        "elapsed_s": round(time.time() - t_total, 1),
    }
    with open(CACHE / f"{args.out_prefix}_meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
