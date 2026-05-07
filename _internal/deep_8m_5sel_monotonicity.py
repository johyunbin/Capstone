#!/usr/bin/env python3
"""
RQ1 DEEP 8M 5-sel 단조성 측정 — Phase 7 numpy D_target methodology 통일.

배경 (Worker J 핸드오프 2026-05-07):
- DEEP 1M Phase 7 numpy D_target 5-sel 측정 완료 (deep_s0XX_numpy_remeasure.parquet 5종)
- 8M 측정은 phase7_8m_bern.parquet (s=0.5만, 100 row) → 단조성 5-cell 미측정
- 본 wrapper: 8M 5-sel × 5 seed × 100 query × {BERN, KM20} = 5,000 cell 측정
- 목적: 1M gradient 19.6%p (s=0.01) 의 8M cross-scale 재현 + per-seed Spearman ρ

전제:
- /mnt/hdd0/home/capstone2026/cache/rq1/query_pool.parquet (DEEP 100 queries)
- /mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_8m.parquet (5 sel × 100 q D_target)
- PG: partsupp_deep_10_phase7_8m_subset (stratum_id 0-19 사전 부여, 재 fit X)

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/rq1_8m_5sel_bern.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq1_8m_5sel_km20.parquet
    /mnt/hdd0/home/capstone2026/cache/rq1/rq1_8m_5sel_summary.json
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SAMPLE_SIZE = 385
N_STRATA = 20
N_QUERIES = 100
SELS = [0.01, 0.05, 0.10, 0.30, 0.50]

DEEP_8M = {
    "name": "DEEP",
    "table": "partsupp_deep_10_phase7_8m_subset",
    "embed_col": "ps_embedding",
    "vec_dim": 96,
    "query_pool": CACHE / "query_pool.parquet",
    "query_sel": CACHE / "query_selectivity_8m.parquet",
}


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def _connect():
    return psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True)


def fetch_all_vectors_safe(ds, n_strata=N_STRATA):
    """stratum_id 별로 분할 fetch — 8M 한번에 fetch 시 PG psycopg memory 위험."""
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
            print(f"[{kst()}]   stratum {sid:2d}: {arr.shape[0]:,} vectors")
    return np.concatenate(parts, axis=0), np.concatenate(sids_list, axis=0)


def cache_cluster_samples(all_vecs, sids, n_strata=N_STRATA, cache_per_cluster=500, seed=42):
    """per-stratum cache 500 vectors (8M 전체 RAM 보유 부담 회피)."""
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
    ap = argparse.ArgumentParser(description="RQ1 DEEP 8M 5-sel 단조성")
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    args = ap.parse_args()

    print(f"[{kst()}] === DEEP 8M 5-sel × 5 seed × {args.n_queries} q × 2 mode 단조성 측정 ===")
    t_total = time.time()

    qp = pd.read_parquet(DEEP_8M["query_pool"]).reset_index(drop=True)
    qs_full = pd.read_parquet(DEEP_8M["query_sel"])
    print(f"[{kst()}] query pool: {len(qp)} | sel parquet: {qs_full.shape}")

    qvecs = np.stack([
        np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
        for i in range(min(len(qp), args.n_queries))
    ])

    print(f"[{kst()}] fetching DEEP 8M vectors per-stratum (stratum_id 0-{N_STRATA-1})...")
    all_vecs, km_sids = fetch_all_vectors_safe(DEEP_8M)
    total = all_vecs.shape[0]
    print(f"[{kst()}] total {total:,} × {all_vecs.shape[1]}d (~{total*96*4/1e9:.2f} GB)")

    samples, sizes = cache_cluster_samples(all_vecs, km_sids, seed=42)
    # 8M 전체 vectors 는 더 이상 필요 없음 — RAM 회수
    del all_vecs, km_sids

    alloc = equal_alloc()

    rows_bern = []
    rows_km20 = []
    for sel in SELS:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel)) &
            (qs_full["query_id"] < args.n_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if len(qs_sel) == 0:
            print(f"⚠️ s={sel}: D_target 데이터 없음")
            continue
        print(f"\n[{kst()}] === s={sel} ({len(qs_sel)} queries) ===")

        for mode in ["bernoulli", "km20"]:
            for seed in SEEDS:
                seed_int = int(seed * 10**9) % (2**31 - 1)
                rng = np.random.default_rng(seed_int)
                t0 = time.time()
                bucket = rows_bern if mode == "bernoulli" else rows_km20
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
                    bucket.append({
                        "dataset": "DEEP_8M", "mode": mode, "selectivity": sel,
                        "seed": seed, "query_id": qid, "D_target": D,
                        "true_card": true_card, "est": est, "q_error": qerr,
                    })
                print(f"[{kst()}]   {mode:>10s} seed={seed} ({(time.time()-t0)*1000:.0f}ms)")

    df_bern = pd.DataFrame(rows_bern)
    df_km20 = pd.DataFrame(rows_km20)
    out_bern = CACHE / "rq1_8m_5sel_bern.parquet"
    out_km20 = CACHE / "rq1_8m_5sel_km20.parquet"
    df_bern.to_parquet(out_bern, index=False)
    df_km20.to_parquet(out_km20, index=False)
    print(f"\n[{kst()}] saved {out_bern} ({len(df_bern)} rows)")
    print(f"[{kst()}] saved {out_km20} ({len(df_km20)} rows)")

    # === summary: per-sel × per-seed median q_error + diff_pct ===
    df_all = pd.concat([df_bern, df_km20], ignore_index=True)
    df_clean = df_all.dropna(subset=["q_error"])
    summary_rows = []
    for sel in SELS:
        d_sel = df_clean[df_clean["selectivity"] == sel]
        if len(d_sel) == 0:
            continue
        bern_per_seed = d_sel[d_sel["mode"] == "bernoulli"].groupby("seed")["q_error"].median()
        km_per_seed = d_sel[d_sel["mode"] == "km20"].groupby("seed")["q_error"].median()
        per_seed = []
        diffs = []
        for seed in SEEDS:
            bm = float(bern_per_seed.get(seed, np.nan))
            km = float(km_per_seed.get(seed, np.nan))
            d_pct = (km - bm) / max(bm, 1e-9) * 100.0 if not np.isnan(bm) else np.nan
            per_seed.append({"seed": seed, "bern_med": bm, "km_med": km, "diff_pct": d_pct})
            if not np.isnan(d_pct):
                diffs.append(d_pct)
        summary_rows.append({
            "selectivity": sel,
            "n_queries": int(len(d_sel) / 10),  # 5 seed × 2 mode
            "mean_diff_pct": float(np.mean(diffs)) if diffs else None,
            "std_diff_pct": float(np.std(diffs, ddof=1)) if len(diffs) >= 2 else None,
            "per_seed": per_seed,
        })

    summary = {
        "method": "numpy D_target",
        "dataset": "DEEP_8M",
        "n_strata": N_STRATA,
        "sample_size": SAMPLE_SIZE,
        "n_seeds": len(SEEDS),
        "n_queries": args.n_queries,
        "total_rows": total,
        "per_sel": summary_rows,
        "ts_kst": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S"),
    }
    out_json = CACHE / "rq1_8m_5sel_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_json}")

    print(f"\n=== DEEP 8M cross-sel summary (km20 - bernoulli, %) ===")
    for r in summary_rows:
        m = r["mean_diff_pct"]
        s = r["std_diff_pct"]
        print(f"  s={r['selectivity']:.2f}: {m:+.2f}% ± {s:.2f}")

    print(f"\n[{kst()}] total elapsed {time.time()-t_total:.1f}s")


if __name__ == "__main__":
    main()
