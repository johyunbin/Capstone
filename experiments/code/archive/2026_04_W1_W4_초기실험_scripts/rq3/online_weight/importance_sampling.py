#!/usr/bin/env python3
"""
RQ3 #11 (P6) — H. Importance Sampling 비분할 (2x2 factorial) 측정 (Python 시뮬레이션).

알고리즘 (per query q with target distance D):
  1. Pilot phase: cache 전체에서 pilot_k 개 uniform sample → distance d_j = ||v - q||
  2. Proposal density 구축: pilot 거리 위 Gaussian KDE
       g(d) ∝ (1/k) Σ_j exp(-(d - d_j)^2 / (2 h^2))
       Silverman bandwidth h = std(d_j) × (4 / (3 k))^(1/5)
       cache 의 모든 row v 에 대해 d_v 계산 후 g(d_v) 평가 → q_prob[v] (정규화)
  3. Main IS phase: q_prob 으로 (with replacement) main_n = budget - pilot_k 개 sample
       importance weight w(v) = (1/n_cache) / q_prob[v]   ← uniform target / q proposal
       weight_clip 이면 [percentile 1, 99] 에서 clip (variance 안정화, 약간의 bias 도입)
  4. Estimator (sum): C_full = N_total × (1/main_n) × Σ_i (1{d_i<D} × w_i)
       (uniform expectation 의 unbiased IS 추정 × N_total)

비분할 (no partition): cluster/shell 분할 없이 전체 cache 한 덩어리. weight 만으로 차별화.

2x2 factorial:
  - pilot_size: {50, 200} — KDE 정확도 vs main IS 예산 trade-off
  - weight_clip: {False, True} — extreme weight 가 variance 폭발 일으키는지 확인
  → 4 mode: is_p50_noclip, is_p50_clip, is_p200_noclip, is_p200_clip

vector.c 패치 우회 — cluster cache 를 flatten 해서 단일 numpy array 로 사용.
거리는 query 마다 cache 전체에 대해 계산 (n_cache × dim × 1 query, 빠름).

서버 실행: scp 후 `python3 -u importance_sampling.py`
산출: /mnt/hdd0/home/capstone2026/cache/rq1/rq3_importance_sampling.parquet
"""
import argparse
import itertools
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
N_STRATA = 20            # cache 로딩에만 사용 (IS 자체는 비분할)
CACHE_PER_CLUSTER = 500
PILOT_SIZES = [50, 200]
WEIGHT_CLIPS = [False, True]
CLIP_PCT = (1.0, 99.0)

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


def mode_name(pilot_size, weight_clip):
    return f"is_p{pilot_size}_{'clip' if weight_clip else 'noclip'}"


def cache_cluster_samples(ds):
    """cluster 별 LIMIT CACHE_PER_CLUSTER sample 캐시 (fresh conn per cluster)."""
    print(f"[{kst()}]   caching {ds['name']} cluster samples (LIMIT {CACHE_PER_CLUSTER}/cluster)...")
    samples = {}
    sizes = {}

    with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
        cu = c.cursor()
        cu.execute(
            f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} "
            f"GROUP BY stratum_id ORDER BY stratum_id"
        )
        for sid, n in cu.fetchall():
            sizes[sid] = int(n)

    t0 = time.time()
    for sid in range(N_STRATA):
        with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {ds['embed_col']}::real[] FROM {ds['table']} "
                f"WHERE stratum_id = {sid} LIMIT {CACHE_PER_CLUSTER}"
            )
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        if not rows:
            samples[sid] = np.zeros((0, ds["vec_dim"]), dtype=np.float32)
        else:
            samples[sid] = np.stack(rows)
    elapsed = time.time() - t0
    total_mb = sum(s.nbytes for s in samples.values()) / 1e6
    total_rows = sum(s.shape[0] for s in samples.values())
    print(f"[{kst()}]   cached {total_rows} rows ({total_mb:.1f} MB) in {elapsed:.1f}s")
    return samples, sizes


def importance_sampling_estimate(flat_cache, total_rows, qvec, D, rng,
                                 budget=SAMPLE_SIZE, pilot_k=50, weight_clip=False):
    """
    비분할 importance sampling estimator.

    flat_cache: shape (n_cache, dim) 모든 cluster sample 합본.
    proposal q ∝ pilot 거리 KDE, target uniform → IS 추정 후 N_total 스케일.
    """
    n_cache = flat_cache.shape[0]
    if n_cache == 0:
        return float(total_rows)
    pilot_k = min(int(pilot_k), n_cache)

    # ── Phase 1: pilot uniform ──
    pilot_idxs = rng.choice(n_cache, size=pilot_k, replace=False)
    pilot_dists = np.linalg.norm(flat_cache[pilot_idxs] - qvec, axis=1)

    # ── Phase 2: KDE proposal q over all cache rows ──
    pilot_std = float(pilot_dists.std())
    if pilot_std < 1e-9:
        pilot_std = 1e-3
    bw = pilot_std * (4.0 / (3.0 * pilot_k)) ** 0.2  # Silverman

    all_dists = np.linalg.norm(flat_cache - qvec, axis=1)
    # KDE eval: shape (n_cache, pilot_k) → mean over pilot axis
    diff_sq = (all_dists[:, None] - pilot_dists[None, :]) ** 2
    kde_vals = np.exp(-0.5 * diff_sq / (bw ** 2)).mean(axis=1)
    kde_vals = np.maximum(kde_vals, 1e-12)
    q_prob = kde_vals / kde_vals.sum()

    # ── Phase 3: IS sample from q (with replacement, IS 표준) ──
    main_n = int(budget) - pilot_k
    if main_n <= 0:
        # pilot 만 있으면 단순 uniform 추정
        pilot_hits = int((pilot_dists < D).sum())
        return float(total_rows * (pilot_hits / pilot_k))

    main_idxs = rng.choice(n_cache, size=main_n, replace=True, p=q_prob)
    main_dists = all_dists[main_idxs]
    main_hits = (main_dists < D).astype(np.int64)
    main_q = q_prob[main_idxs]

    # importance weight: target = uniform = 1/n_cache, proposal = q
    # w(x) = uniform/proposal = (1/n_cache) / q
    weights = (1.0 / n_cache) / main_q

    if weight_clip:
        lo, hi = np.percentile(weights, CLIP_PCT)
        weights = np.clip(weights, lo, hi)

    # IS estimator of E_uniform[hit indicator] = C_cache / n_cache
    # mean_hit = (1/main_n) Σ_i hit_i × w_i
    # C_full = N_total × mean_hit  (cache 가 N_total 의 uniform sample)
    mean_hit = float((main_hits * weights).sum() / main_n)
    return float(total_rows * mean_hit)


def bernoulli_estimate(flat_cache, total_rows, qvec, D, rng, budget=SAMPLE_SIZE):
    """TABLESAMPLE BERNOULLI baseline."""
    n = flat_cache.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return float(total_rows)
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat_cache[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (total_rows / s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-prefix", default="rq3_importance_sampling")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--include-bernoulli", action="store_true",
                    help="bernoulli baseline 도 같이 측정 (default off — 다른 RQ3 파일에 이미 있음)")
    args = ap.parse_args()

    print(f"[{kst()}] === RQ3 #11 (P6) — H. Importance Sampling 비분할 (2x2 factorial) ===")
    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d["name"] in args.datasets]
    factorial = list(itertools.product(PILOT_SIZES, WEIGHT_CLIPS))
    print(f"[{kst()}] factorial: {[mode_name(p, c) for p, c in factorial]} ({len(factorial)} cells), "
          f"budget={SAMPLE_SIZE}")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        samples, sizes = cache_cluster_samples(ds)
        total_rows = sum(sizes.values())
        flat_cache = np.concatenate([samples[sid] for sid in range(N_STRATA)
                                     if samples[sid].shape[0] > 0], axis=0)
        print(f"[{kst()}]   N_total={total_rows}, flat_cache shape={flat_cache.shape}")

        qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
        qs_full = pq.read_table(ds["query_sel"]).to_pandas()
        qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
                          for i in range(len(qp))])
        print(f"[{kst()}]   loaded {len(qp)} queries (dim={qvecs.shape[1]}), "
              f"{len(qs_full)} sel rows")

        # bernoulli baseline (optional)
        modes_to_run = []
        if args.include_bernoulli:
            modes_to_run.append(("bernoulli", None, None))
        for pilot_size, weight_clip in factorial:
            modes_to_run.append((mode_name(pilot_size, weight_clip), pilot_size, weight_clip))

        for mode, pilot_size, weight_clip in modes_to_run:
            t_mode = time.time()
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
                            est = bernoulli_estimate(flat_cache, total_rows, qvec, D, rng,
                                                     SAMPLE_SIZE)
                        else:
                            est = importance_sampling_estimate(
                                flat_cache, total_rows, qvec, D, rng,
                                SAMPLE_SIZE, pilot_size, weight_clip,
                            )
                        if est > 0 and true_card > 0:
                            qerr = max(est / true_card, true_card / est)
                        else:
                            qerr = None
                        all_rows.append({
                            "dataset": ds["name"], "mode": mode, "selectivity": sel,
                            "seed": seed, "query_id": qid, "D_target": D,
                            "true_card": true_card, "est": est, "q_error": qerr,
                            "pilot_size": pilot_size if pilot_size is not None else 0,
                            "weight_clip": bool(weight_clip) if weight_clip is not None else False,
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

    # 2x2 factorial main effects (dataset × pilot_size, dataset × weight_clip)
    print("\n=== factorial main effects (mean q_error, IS cells only) ===")
    is_only = full_df[full_df["mode"].str.startswith("is_p")].copy()
    if len(is_only) > 0:
        print("\n— pilot_size effect (avg over weight_clip × sel × seed × query) —")
        print(is_only.groupby(["dataset", "pilot_size"])["q_error"].mean().round(4).unstack())
        print("\n— weight_clip effect (avg over pilot_size × sel × seed × query) —")
        print(is_only.groupby(["dataset", "weight_clip"])["q_error"].mean().round(4).unstack())

    meta = {
        "kst": kst(),
        "args": vars(args),
        "datasets": [d["name"] for d in use_datasets],
        "factorial": [mode_name(p, c) for p, c in factorial],
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "n_queries": args.n_queries,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "pilot_sizes": PILOT_SIZES,
        "weight_clips": WEIGHT_CLIPS,
        "clip_pct": list(CLIP_PCT),
        "elapsed_s": round(time.time() - t_total, 1),
    }
    with open(CACHE / f"{args.out_prefix}_meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
