#!/usr/bin/env python3
"""
RQ1 SIFT mid-sel (s=0.10, 0.30) 보강 측정.

배경 (RQ1_RQ2 정리.md line 287-291): SIFT 의 selectivity gradient 가 현재 3 cell
(s=0.01, 0.05, 0.50) 만 측정 → 단조성 검정 power 부족 (n=3). mid-sel 2 cell 추가
시 5 cell → 단조성 통계 power 복구.

측정:
- DEEP 의 random20_low_sel.py 와 동일 패턴 — 같은 query pool, 같은 stratum.
- SIFT 1.5M × s=0.10/0.30 × 5 seed × 100 query × 3 mode (BERN / KM20-stratified / RANDOM20-stratified).
- 추정 시간: 약 30분 (server side, 8M 측정 끝난 후 실행).

서버 실행:
    python3 /mnt/hdd0/home/capstone2026/cache/sift_mid_sel_measurement.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/sift_mid_sel_summary.json
    /mnt/hdd0/home/capstone2026/cache/rq1/sift_mid_sel.parquet (raw measurements)

분석 합산:
    python3 experiments/code/local_analysis/rq1_gradient_monotonicity.py
    (sift_1m_mid_summary.json 의 sift_km20 항목과 합쳐 단조성 재검정)
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import psycopg
except ImportError:
    psycopg = None

try:
    import pyarrow.parquet as pq
except ImportError:
    pq = None

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SAMPLE_SIZE = 385
N_STRATA = 20
CACHE_PER_CLUSTER = 500

# 본 측정 대상 sel 만
TARGET_SELS = [0.10, 0.30]

# SIFT 만
SIFT_DS = {
    "name": "SIFT",
    "table": "customer_sift_10_phase7_noidx_subset",
    "embed_col": "c_embedding",
    "vec_dim": 128,
    "query_pool": CACHE / "query_pool_sift.parquet",
    "query_sel": CACHE / "query_selectivity_sift_v2.parquet",
}


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def _connect():
    return psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True)


def fetch_all_vectors_safe(ds: dict, n_strata: int = N_STRATA):
    parts = []
    km_sids = []
    for sid in range(n_strata):
        with _connect() as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {ds['embed_col']}::real[] FROM {ds['table']} WHERE stratum_id = {sid}"
            )
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        if rows:
            arr = np.stack(rows)
            parts.append(arr)
            km_sids.append(np.full(arr.shape[0], sid, dtype=np.int32))
    return np.concatenate(parts, axis=0), np.concatenate(km_sids, axis=0)


def cache_cluster_samples_inmem(all_vecs, sids, n_strata=N_STRATA, seed=42):
    rng = np.random.default_rng(seed)
    samples, sizes = {}, {}
    for s in range(n_strata):
        mask = sids == s
        n_c = int(mask.sum())
        sizes[s] = n_c
        if n_c == 0:
            samples[s] = np.zeros((1, all_vecs.shape[1]), dtype=np.float32)
            continue
        cv = all_vecs[mask]
        if n_c > CACHE_PER_CLUSTER:
            idx = rng.choice(n_c, size=CACHE_PER_CLUSTER, replace=False)
            samples[s] = cv[idx]
        else:
            samples[s] = cv
    return samples, sizes


def equal_alloc(n_strata=N_STRATA, budget=SAMPLE_SIZE):
    base = budget // n_strata
    extra = budget - base * n_strata
    s = np.full(n_strata, base, dtype=int)
    s[:extra] += 1
    return np.maximum(s, 1)


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


def bernoulli_estimate(samples, sizes, qvec, D, rng, budget=SAMPLE_SIZE):
    total_rows = sum(sizes.values())
    flat = np.concatenate([samples[sid] for sid in range(N_STRATA)], axis=0)
    n = flat.shape[0]
    s = min(int(budget), n)
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (total_rows / s)


def measure_one(samples, sizes, qp, qs_full, qvecs, mode_name, alloc, sels, n_queries=100):
    rows = []
    for sel in sels:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel)) &
            (qs_full["query_id"] < n_queries)
        ].sort_values("query_id").reset_index(drop=True)
        for seed in SEEDS:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            t0 = time.time()
            for _, row in qs_sel.iterrows():
                qid = int(row["query_id"])
                D = float(row["D_target"])
                true_card = int(row["true_cardinality"])
                qvec = qvecs[qid]
                if mode_name == "bernoulli":
                    est = bernoulli_estimate(samples, sizes, qvec, D, rng)
                else:
                    est = stratified_estimate(samples, sizes, alloc, qvec, D, rng)
                if est > 0 and true_card > 0:
                    qerr = max(est / true_card, true_card / est)
                else:
                    qerr = None
                rows.append({
                    "dataset": "SIFT", "mode": mode_name, "selectivity": sel, "seed": seed,
                    "query_id": qid, "D_target": D, "true_card": true_card,
                    "est": est, "q_error": qerr,
                })
            print(f"[{kst()}]   {mode_name:>10s} s={sel:.2f} seed={seed} "
                  f"({(time.time()-t0)*1000:.0f}ms)")
    return rows


def main():
    ap = argparse.ArgumentParser(description="RQ1 SIFT mid-sel 보강 측정")
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--include-random20", action="store_true",
                    help="RANDOM20 (control) 도 측정. SIFT 의 RANDOM20 stratum_id 가 있어야 함.")
    args = ap.parse_args()

    print(f"[{kst()}] === SIFT mid-sel 보강 (s=0.10, 0.30) ===")
    t_total = time.time()

    print(f"[{kst()}] fetching SIFT 1.5M vectors...")
    all_vecs, km20_sids = fetch_all_vectors_safe(SIFT_DS)
    print(f"[{kst()}]   {all_vecs.shape[0]:,} × {all_vecs.shape[1]}d ({all_vecs.nbytes/1e6:.1f} MB)")

    samples, sizes = cache_cluster_samples_inmem(all_vecs, km20_sids, seed=42)

    qp = pq.read_table(SIFT_DS["query_pool"]).to_pandas().reset_index(drop=True)
    qs_full = pq.read_table(SIFT_DS["query_sel"]).to_pandas()
    qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32) for i in range(len(qp))])
    print(f"[{kst()}] loaded {len(qp)} queries")

    alloc = equal_alloc()
    all_rows = []
    all_rows.extend(measure_one(samples, sizes, qp, qs_full, qvecs,
                                  "bernoulli", None, TARGET_SELS, args.n_queries))
    all_rows.extend(measure_one(samples, sizes, qp, qs_full, qvecs,
                                  "km20", alloc, TARGET_SELS, args.n_queries))

    if args.include_random20:
        print(f"[{kst()}] === RANDOM20 (control) 측정 시작 ===")
        # RANDOM20: km20_sids 무관하게 random reassign — 5/7 W2 RQ1 보강
        rng_rand = np.random.default_rng(42)
        rand_sids = rng_rand.integers(0, N_STRATA, size=len(all_vecs)).astype(np.int32)
        samples_rand, sizes_rand = cache_cluster_samples_inmem(all_vecs, rand_sids, seed=42)
        all_rows.extend(measure_one(samples_rand, sizes_rand, qp, qs_full, qvecs,
                                      "random20", alloc, TARGET_SELS, args.n_queries))

    out_pq = CACHE / "sift_mid_sel.parquet"
    pd.DataFrame(all_rows).to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq}")

    # summary JSON (RQ1 monotonicity 분석에 합산 가능 형식)
    df = pd.DataFrame(all_rows).dropna(subset=["q_error"])
    summary = {"sift_km20_mid": {}, "sift_bern_mid": {}, "sift_rand_mid": {}}
    for sel in TARGET_SELS:
        sub = df[df["selectivity"] == sel]
        bern_med_per_seed = sub[sub["mode"] == "bernoulli"].groupby("seed")["q_error"].median()
        km_med_per_seed = sub[sub["mode"] == "km20"].groupby("seed")["q_error"].median()
        rand_med_per_seed = sub[sub["mode"] == "random20"].groupby("seed")["q_error"].median()
        # KM20 vs BERN
        per_seed = []
        for seed in SEEDS:
            bm = float(bern_med_per_seed.get(seed, np.nan))
            km = float(km_med_per_seed.get(seed, np.nan))
            diff_pct = (km - bm) / max(bm, 1e-9) * 100.0 if not np.isnan(bm) else None
            per_seed.append({"seed": seed, "bern_med": bm, "strat_med": km, "diff_pct": diff_pct})
        diffs = [p["diff_pct"] for p in per_seed if p["diff_pct"] is not None]
        summary["sift_km20_mid"][f"s{sel}"] = {
            "mean_diff_pct": float(np.mean(diffs)),
            "std_diff_pct": float(np.std(diffs, ddof=1)),
            "n_seeds": len(diffs),
            "per_seed": per_seed,
        }
        # RANDOM20 vs BERN (RQ1 reverse-monotonic 검정용)
        if not rand_med_per_seed.empty:
            per_seed_rand = []
            for seed in SEEDS:
                bm = float(bern_med_per_seed.get(seed, np.nan))
                rd = float(rand_med_per_seed.get(seed, np.nan))
                diff_pct = (rd - bm) / max(bm, 1e-9) * 100.0 if not np.isnan(bm) and not np.isnan(rd) else None
                per_seed_rand.append({"seed": seed, "bern_med": bm, "strat_med": rd, "diff_pct": diff_pct})
            diffs_rand = [p["diff_pct"] for p in per_seed_rand if p["diff_pct"] is not None]
            if diffs_rand:
                summary["sift_rand_mid"][f"s{sel}"] = {
                    "mean_diff_pct": float(np.mean(diffs_rand)),
                    "std_diff_pct": float(np.std(diffs_rand, ddof=1)) if len(diffs_rand) > 1 else 0.0,
                    "n_seeds": len(diffs_rand),
                    "per_seed": per_seed_rand,
                }
    out_json = CACHE / "sift_mid_sel_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_json}")
    print(f"[{kst()}] total elapsed {time.time() - t_total:.1f}s")
    print(f"\n=== Summary ===")
    for sel in TARGET_SELS:
        s = summary["sift_km20_mid"][f"s{sel}"]
        print(f"  SIFT × KM20 s={sel:.2f}: mean diff = {s['mean_diff_pct']:+.2f}% "
              f"(n_seeds={s['n_seeds']}, std={s['std_diff_pct']:.2f})")
        if f"s{sel}" in summary["sift_rand_mid"]:
            r = summary["sift_rand_mid"][f"s{sel}"]
            print(f"  SIFT × RAND s={sel:.2f}: mean diff = {r['mean_diff_pct']:+.2f}% "
                  f"(n_seeds={r['n_seeds']}, std={r['std_diff_pct']:.2f})")


if __name__ == "__main__":
    main()
