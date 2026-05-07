#!/usr/bin/env python3
"""
RQ1 DEEP s=0.05 의 numpy D_target 통일 재측정 (Phase 6/7 methodology 차이 제거).

배경 (rq1_phase6_vs_phase7_comparison.json):
- Phase 6 (4/15) DEEP s=0.05 KM20: +1.85% (SQL 이진 탐색 D_target)
- Phase 7 (5/06) DEEP s=0.10 KM20: +4.19% (numpy D_target)
- 두 측정의 sel 다름 + methodology 다름 → 비단조 패턴의 origin 분리 X.

본 wrapper: DEEP s=0.05 를 **numpy D_target** 으로 재측정. Phase 7 의 s=0.10 와 직접
비교 가능 → 비단조성이 (a) sel 자연 변동 vs (b) methodology 차이 의 정량 분리.

전제:
- query_selectivity_5sel_numpy.parquet 또는 phase7_dtarget*.json 등에 DEEP 1M 의
  s=0.05 numpy D_target 사전 계산 필요. 만약 sift_1m_mid_summary 의 1m_mid_km20
  계산 시 함께 만들어진 query_selectivity*.parquet 가 있으면 거기서 사용.

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/deep_s005_numpy_remeasure.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/deep_s005_numpy_remeasure_summary.json

분석:
    Phase 6 결과 (random20_low_sel_summary.json: km20 +1.85%) 와 본 측정 비교
    → t-test, methodology 효과 정량
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

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SAMPLE_SIZE = 385
N_STRATA = 20

DEEP_DS = {
    "name": "DEEP",
    "table": "partsupp_deep_10_subset_1m",
    "embed_col": "ps_embedding",
    "vec_dim": 96,
    "query_pool": CACHE / "query_pool.parquet",
    # Phase 7 numpy D_target 사용
    "query_sel": CACHE / "query_selectivity.parquet",  # 본 file 의 D_target 이 numpy 기반인지 검증 필요
}


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def _connect():
    return psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True)


def fetch_all_vectors_safe(ds, n_strata=N_STRATA):
    parts, sids_list = [], []
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
            sids_list.append(np.full(arr.shape[0], sid, dtype=np.int32))
    return np.concatenate(parts, axis=0), np.concatenate(sids_list, axis=0)


def cache_cluster_samples(all_vecs, sids, n_strata=N_STRATA, cache_per_cluster=500, seed=42):
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
        if n_c > cache_per_cluster:
            idx = rng.choice(n_c, size=cache_per_cluster, replace=False)
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


def main():
    ap = argparse.ArgumentParser(description="RQ1 DEEP s=0.05 numpy D_target 재측정")
    ap.add_argument("--target-sel", type=float, default=0.05,
                    help="재측정 대상 sel (default 0.05)")
    ap.add_argument("--n-queries", type=int, default=100)
    args = ap.parse_args()

    print(f"[{kst()}] === DEEP s={args.target_sel} numpy D_target 재측정 ===")
    t_total = time.time()

    qp = pd.read_parquet(DEEP_DS["query_pool"]).reset_index(drop=True)
    qs_full = pd.read_parquet(DEEP_DS["query_sel"])
    qs_sel = qs_full[
        (np.isclose(qs_full["selectivity"], args.target_sel)) &
        (qs_full["query_id"] < args.n_queries)
    ].sort_values("query_id").reset_index(drop=True)
    if len(qs_sel) == 0:
        print(f"⚠️ s={args.target_sel} 의 D_target 데이터 없음 — sift_1m_mid 계산 시 함께 만들어진 file 인지 확인")
        return

    print(f"[{kst()}] {len(qs_sel)} queries with D_target for s={args.target_sel}")
    qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32) for i in range(len(qp))])

    print(f"[{kst()}] fetching DEEP 1M vectors...")
    all_vecs, km_sids = fetch_all_vectors_safe(DEEP_DS)
    print(f"[{kst()}]   {all_vecs.shape[0]:,} × {all_vecs.shape[1]}d")
    samples, sizes = cache_cluster_samples(all_vecs, km_sids, seed=42)

    alloc = equal_alloc()
    rows = []
    for mode in ["bernoulli", "km20"]:
        for seed in SEEDS:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            t0 = time.time()
            for _, q in qs_sel.iterrows():
                qid = int(q["query_id"])
                D = float(q["D_target"])
                true_card = int(q["true_cardinality"])
                qvec = qvecs[qid]
                if mode == "bernoulli":
                    est = bernoulli_estimate(samples, sizes, qvec, D, rng)
                else:
                    est = stratified_estimate(samples, sizes, alloc, qvec, D, rng)
                if est > 0 and true_card > 0:
                    qerr = max(est / true_card, true_card / est)
                else:
                    qerr = None
                rows.append({
                    "dataset": "DEEP", "mode": mode, "selectivity": args.target_sel,
                    "seed": seed, "query_id": qid, "D_target": D,
                    "true_card": true_card, "est": est, "q_error": qerr,
                })
            print(f"[{kst()}]   {mode:>10s} seed={seed} ({(time.time()-t0)*1000:.0f}ms)")

    df = pd.DataFrame(rows)
    out_pq = CACHE / "deep_s005_numpy_remeasure.parquet"
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq}")

    # summary
    df_clean = df.dropna(subset=["q_error"])
    bern_med = df_clean[df_clean["mode"] == "bernoulli"].groupby("seed")["q_error"].median()
    km_med = df_clean[df_clean["mode"] == "km20"].groupby("seed")["q_error"].median()
    diffs = []
    per_seed = []
    for seed in SEEDS:
        bm = float(bern_med.get(seed, np.nan))
        km = float(km_med.get(seed, np.nan))
        d_pct = (km - bm) / max(bm, 1e-9) * 100.0
        diffs.append(d_pct)
        per_seed.append({"seed": seed, "bern_med": bm, "km_med": km, "diff_pct": d_pct})

    summary = {
        "method": "numpy D_target",
        "dataset": "DEEP",
        "selectivity": args.target_sel,
        "mean_diff_pct": float(np.mean(diffs)),
        "std_diff_pct": float(np.std(diffs, ddof=1)),
        "per_seed": per_seed,
        "phase6_reference": {
            "mean_diff_pct": 1.853716991299882,
            "note": "random20_low_sel_summary.json s=0.05 km20 (SQL D_target, 4/15)"
        },
    }
    out_json = CACHE / "deep_s005_numpy_remeasure_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_json}")
    print(f"\n=== Comparison ===")
    print(f"Phase 6 (SQL D, 4/15) s=0.05: +1.85%")
    print(f"Phase 7 (numpy D, now)  s=0.05: {summary['mean_diff_pct']:+.2f}%")
    delta = summary["mean_diff_pct"] - 1.85
    print(f"   Δ = {delta:+.2f}%p")
    if abs(delta) > 1.0:
        print(f"   → methodology 효과 의미 있음 (>1%p)")
    else:
        print(f"   → methodology 효과 작음 — sel 자체 변동이 비단조 origin")
    print(f"\n[{kst()}] total elapsed {time.time()-t_total:.1f}s")


if __name__ == "__main__":
    main()
