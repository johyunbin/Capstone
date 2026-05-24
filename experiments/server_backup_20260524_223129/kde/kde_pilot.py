#!/usr/bin/env python3
"""
RQ3 #10 (P5) — B. KDE-pilot Online Allocation 측정 (Python 시뮬레이션).

알고리즘 (per query q with target distance D):
  1. Pilot phase: cluster i 마다 n_pilot 개 sample 추출, distance d_ij = ||v - q||
  2. Silverman bandwidth: h_i = 1.06 × std(d_ij) × n_pilot^(-1/5)
  3. KDE-based hit probability:
       p_i_hat = (1/n_pilot) Σ_j Φ((D - d_ij) / h_i)
       (Gaussian kernel CDF integration — empirical 보다 smooth)
  4. Bernoulli σ 추정: σ_i_hat = sqrt(p_i_hat × (1 - p_i_hat))
  5. Neyman main allocation: n_main_i ∝ N_i × σ_i_hat,
       sum to (budget − pilot_used)
  6. Main phase: cluster i 마다 n_main_i 개 추가 sample (pilot 와 disjoint)
  7. HT estimator (pilot + main 결합):
       est = Σ_i (pilot_hits_i + main_hits_i) × N_i / (n_pilot_used_i + n_main_i)

핵심 차이 (vs RQ2 alloc): 쿼리마다 pilot 을 새로 뽑아 σ_i 를 query-adaptive 로 추정.
RQ2 σ_i 는 sel=0.1 한 점에서 사전 계산된 상수였으나, 여기서는 매 query 의 D 에 대해 동적.

vector.c 패치 우회 — 이미 rq2 에서 검증된 Python 시뮬레이션 패턴 그대로 (cluster 별
LIMIT 500 캐시, fresh conn per cluster, HT 거리 numpy 계산).

서버 실행: scp 후 `python3 -u kde_pilot.py` (default n_pilot=5, 모든 dataset/sel/seed)
산출: /mnt/hdd0/home/capstone2026/cache/rq1/rq3_kde_pilot.parquet
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
from scipy.special import erf

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20
CACHE_PER_CLUSTER = 500
N_PILOT = 5  # cluster 당 pilot 개수 → 총 100, main 예산 285 (≈14/cluster avg)

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

ALL_MODES = ["bernoulli", "kde_pilot"]   # bernoulli baseline + kde_pilot online


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def normal_cdf(x):
    """Standard normal CDF — vectorized via scipy.special.erf."""
    return 0.5 * (1.0 + erf(x / np.sqrt(2.0)))


def cache_cluster_samples(ds):
    """NPY cache fast-path (5/8 fix): {table}_vectors.npy + {table}_strata.npy → no PG roundtrip.

    Falls back to PG-based (LIMIT/cluster) loading when NPY caches are missing.
    """
    from pathlib import Path as _P
    import numpy as _np

    _CACHE = _P("/mnt/hdd0/home/capstone2026/cache/rq1")
    table = ds["table"]
    vec_npy = _CACHE / f"{table}_vectors.npy"
    strata_npy = _CACHE / f"{table}_strata.npy"

    if vec_npy.exists() and strata_npy.exists():
        print(f"[{kst()}]   caching {ds['name']} cluster samples (NPY fast-path)...")
        t0 = time.time()
        all_vecs = _np.load(vec_npy)
        all_sids = _np.load(strata_npy).astype(int)
        rng = _np.random.default_rng(42)
        samples = {}
        sizes = {}
        for sid in range(N_STRATA):
            mask = all_sids == sid
            n_cluster = int(mask.sum())
            sizes[sid] = n_cluster
            if n_cluster == 0:
                samples[sid] = _np.zeros((0, all_vecs.shape[1]), dtype=_np.float32)
                continue
            cluster_vecs = all_vecs[mask].astype(_np.float32)
            if n_cluster > CACHE_PER_CLUSTER:
                idx = rng.choice(n_cluster, size=CACHE_PER_CLUSTER, replace=False)
                samples[sid] = cluster_vecs[idx]
            else:
                samples[sid] = cluster_vecs
        elapsed = time.time() - t0
        total_mb = sum(s.nbytes for s in samples.values()) / 1e6
        total_rows = sum(s.shape[0] for s in samples.values())
        print(f"[{kst()}]   cached {total_rows} rows ({total_mb:.1f} MB) in {elapsed:.1f}s [npy]")
        return samples, sizes

    # Fallback: PG-based loading (original logic)
    print(f"[{kst()}]   caching {ds['name']} cluster samples (LIMIT {CACHE_PER_CLUSTER}/cluster, PG)...")
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


def kde_pilot_estimate(samples, sizes, qvec, D, rng,
                       budget=SAMPLE_SIZE, n_pilot=N_PILOT):
    """
    Online KDE-pilot 추정 — query 의 D 에 적응한 Neyman allocation.

    반환: HT estimate (cluster i 마다 (pilot_hits + main_hits) × N_i / (m_i + n_main_i))
    """
    n_strata = N_STRATA
    pilot_hits = np.zeros(n_strata, dtype=np.int64)
    sigma_hat = np.zeros(n_strata, dtype=np.float64)
    pilot_size = np.zeros(n_strata, dtype=np.int64)
    used_masks = [None] * n_strata

    # ── Pilot phase ──
    for sid in range(n_strata):
        cache = samples[sid]
        n_cache = cache.shape[0]
        if n_cache == 0:
            used_masks[sid] = np.zeros(0, dtype=bool)
            continue
        m = min(n_pilot, n_cache)
        pilot_size[sid] = m
        pilot_idxs = rng.choice(n_cache, size=m, replace=False)
        mask = np.zeros(n_cache, dtype=bool)
        mask[pilot_idxs] = True
        used_masks[sid] = mask

        sub = cache[pilot_idxs]
        d = np.linalg.norm(sub - qvec, axis=1)
        pilot_hits[sid] = int((d < D).sum())

        # KDE-based hit probability — Silverman bandwidth + Gaussian kernel CDF
        sd = float(np.std(d))
        if m < 2 or sd < 1e-9:
            # degenerate (pilot 1개거나 모든 거리 동일) → empirical hit rate fallback
            p = float((d < D).mean()) if m > 0 else 0.0
        else:
            h = 1.06 * sd * (m ** (-0.2))
            # p = mean_j P(N(d_j, h^2) < D) = mean_j Φ((D - d_j) / h)
            p = float(normal_cdf((D - d) / h).mean())
        p = min(max(p, 0.0), 1.0)
        sigma_hat[sid] = float(np.sqrt(p * (1.0 - p)))

    # ── Main allocation (Neyman with σ_hat) ──
    pilot_used_total = int(pilot_size.sum())
    main_budget = max(int(budget) - pilot_used_total, 0)
    weights = np.array(
        [sizes.get(sid, 0) * sigma_hat[sid] for sid in range(n_strata)],
        dtype=np.float64,
    )
    sum_w = weights.sum()
    if main_budget <= 0:
        n_main = np.zeros(n_strata, dtype=np.int64)
    elif sum_w <= 1e-12:
        # σ_hat 모두 0 (모든 cluster 가 pilot 에서 명확한 답) → equal fallback
        base = main_budget // n_strata
        n_main = np.full(n_strata, base, dtype=np.int64)
        extra = main_budget - int(n_main.sum())
        if extra > 0:
            n_main[:extra] += 1
    else:
        f = weights / sum_w * main_budget
        n_main = f.astype(np.int64)
        frac = f - n_main
        extra = main_budget - int(n_main.sum())
        if extra > 0:
            top = np.argsort(-frac)[:extra]
            n_main[top] += 1

    # ── Main phase (pilot 와 disjoint indices) ──
    main_hits = np.zeros(n_strata, dtype=np.int64)
    for sid in range(n_strata):
        if n_main[sid] <= 0:
            continue
        cache = samples[sid]
        if cache.shape[0] == 0:
            n_main[sid] = 0
            continue
        avail = np.where(~used_masks[sid])[0]
        n_take = min(int(n_main[sid]), int(avail.size))
        if n_take <= 0:
            n_main[sid] = 0
            continue
        sel = rng.choice(avail, size=n_take, replace=False)
        sub = cache[sel]
        d = np.linalg.norm(sub - qvec, axis=1)
        main_hits[sid] = int((d < D).sum())
        n_main[sid] = n_take

    # ── HT estimator (pilot + main 결합) ──
    est = 0.0
    for sid in range(n_strata):
        n_total = int(pilot_size[sid]) + int(n_main[sid])
        if n_total <= 0:
            continue
        hits_total = int(pilot_hits[sid] + main_hits[sid])
        N_i = sizes.get(sid, 0)
        est += hits_total * (N_i / n_total)
    return est


def bernoulli_estimate(samples, sizes, qvec, D, rng, budget=SAMPLE_SIZE):
    """TABLESAMPLE BERNOULLI baseline — RANDOM20 와 동일 (rq2_alloc 동등 로직)."""
    total_rows = sum(sizes.values())
    flat = np.concatenate([samples[sid] for sid in range(N_STRATA)], axis=0)
    n = flat.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return float(total_rows)
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (total_rows / s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-prefix", default="rq3_kde_pilot")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--modes", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--n-pilot", type=int, default=N_PILOT,
                    help="cluster 당 pilot sample 수 (default 5)")
    args = ap.parse_args()

    print(f"[{kst()}] === RQ3 #10 (P5) — KDE-pilot Online (Python 시뮬레이션) ===")
    use_modes = ALL_MODES if not args.modes else [m for m in ALL_MODES if m in args.modes]
    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d["name"] in args.datasets]
    print(f"[{kst()}] modes: {use_modes}, n_pilot={args.n_pilot}, total budget={SAMPLE_SIZE}")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        samples, sizes = cache_cluster_samples(ds)
        print(f"[{kst()}]   N_i sum={sum(sizes.values())}")

        qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
        qs_full = pq.read_table(ds["query_sel"]).to_pandas()
        qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
                          for i in range(len(qp))])
        print(f"[{kst()}]   loaded {len(qp)} queries (dim={qvecs.shape[1]}), "
              f"{len(qs_full)} sel rows")

        for mode in use_modes:
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
                            est = bernoulli_estimate(samples, sizes, qvec, D, rng, SAMPLE_SIZE)
                        else:  # kde_pilot
                            est = kde_pilot_estimate(samples, sizes, qvec, D, rng,
                                                     SAMPLE_SIZE, args.n_pilot)
                        if est > 0 and true_card > 0:
                            qerr = max(est / true_card, true_card / est)
                        else:
                            qerr = None
                        all_rows.append({
                            "dataset": ds["name"], "mode": mode, "selectivity": sel,
                            "seed": seed, "query_id": qid, "D_target": D,
                            "true_card": true_card, "est": est, "q_error": qerr,
                            "n_pilot": args.n_pilot,
                        })
                        qe_list.append(qerr if qerr else float("nan"))
                    elapsed = time.time() - t0
                    valid = sum(1 for q in qe_list if q == q)
                    med = float(np.nanmedian(qe_list)) if valid else float("nan")
                    print(f"[{kst()}]   {ds['name']} {mode:>10} s={sel:.2f} seed={seed} "
                          f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} med_qe={med:.4f}")
            print(f"[{kst()}] {ds['name']} {mode:>10}: total {time.time() - t_mode:.1f}s")

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
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_pilot": args.n_pilot,
        "elapsed_s": round(time.time() - t_total, 1),
    }
    with open(CACHE / f"{args.out_prefix}_meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
