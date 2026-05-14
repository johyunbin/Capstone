#!/usr/bin/env python3
"""
RQ1 8M selectivity gradient 5-sel 풀 측정 (s=0.01, 0.05, 0.10, 0.30, 0.50).

배경: 현재 8M 측정은 mid-sel (s=0.10, 0.30) 만 진행 중. 1M 의 단조성 (DEEP-KM20
ρ=-0.680, CI 0 제외) 이 8M 에서도 재현되는지 cross-scale 검증하려면 5 sel 모두 필요.

본 스크립트는 8M 의 추가 sel (s=0.01, 0.05, 0.50) 측정 — DEEP 8M × 3 sel × 5 seed
× 100 query × 3 mode (BERN / KM20 / RANDOM20).

전제:
- 현재 8M 측정 (s=0.10, 0.30) 종료 후 (post_8m_pipeline 의 8M sensitivity 도 끝난 후)
  서버 PG 자유 시 실행.
- 8M 의 D_target 이 추가 sel (0.01/0.05/0.50) 에 대해 미리 계산되어야 함 — 본 wrapper
  는 D_target JSON 에서 읽음. 없으면 별도 dtarget 계산 스크립트 (phase7_8m_dtarget*) 활용.

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/phase7_8m_lowsel_highsel.parquet
    → 분석은 RQ1 의 random20_low_sel.py 패턴 + 1M monotonicity 와 합산
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
N_QUERIES = 100
SAMPLE_SIZE = 385
N_STRATA = 20

# 추가 sel — mid-sel (0.10, 0.30) 은 이미 측정됨
TARGET_SELS = [0.01, 0.05, 0.50]

DEEP_8M = {
    "name": "DEEP_8M",
    "table": "partsupp_deep_10_phase7_8m_subset",
    "embed_col": "ps_embedding",
    "vec_dim": 96,
    "query_pool": CACHE / "query_pool.parquet",
}

DTARGET_SOURCES = [
    # Phase 7 mid-sel (이미 측정 — sel 0.1, 0.3)
    CACHE / "phase7_8m_dtarget_midsel.json",
    # Phase 7 추가 sel (만약 이미 사전 계산되어 있으면)
    CACHE / "phase7_8m_dtarget_lowsel.json",
    CACHE / "phase7_8m_dtarget_highsel.json",
    # 모든 sel 통합 (cleanup version)
    CACHE / "phase7_8m_dtarget_recalc_clean.json",
    CACHE / "phase7_8m_dtarget_recalc.json",
]


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def _connect():
    return psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True)


def load_dtarget_8m() -> pd.DataFrame:
    """8M 의 D_target 을 가능한 모든 source 에서 로드, 통합."""
    rows = []
    for src in DTARGET_SOURCES:
        if not src.exists():
            continue
        d = json.load(open(src))
        # 두 형식 모두 처리: results: {sel_str: [...]} 또는 list
        if "results" in d:
            for sel_key, items in d["results"].items():
                sel = float(sel_key)
                for x in items:
                    rows.append({
                        "query_id": int(x["query_id"]),
                        "selectivity": sel,
                        "D_target": float(x.get("D_target_8m", x.get("D_target", 0))),
                        "true_cardinality": int(x.get("true_card_8m", x.get("true_card", 0))),
                        "source": src.name,
                    })
        elif isinstance(d, list):
            for x in d:
                rows.append({
                    "query_id": int(x["query_id"]),
                    "selectivity": float(x.get("selectivity", x.get("sel", 0))),
                    "D_target": float(x["D_target"]),
                    "true_cardinality": int(x.get("true_card", 0)),
                    "source": src.name,
                })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    # 같은 (query_id, sel) 가 여러 source 에 있으면 첫 번째만
    df = df.drop_duplicates(["query_id", "selectivity"]).reset_index(drop=True)
    return df


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
    ap = argparse.ArgumentParser(description="RQ1 8M selectivity gradient 추가 측정 (s=0.01, 0.05, 0.50)")
    ap.add_argument("--out-prefix", default="phase7_8m_lowsel_highsel")
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    args = ap.parse_args()

    print(f"[{kst()}] === 8M selectivity gradient 추가 측정 ===")

    dt_df = load_dtarget_8m()
    if dt_df.empty:
        print(f"⚠️ D_target 데이터 없음 — phase7_8m_dtarget_*.json 사전 계산 필요")
        return
    available_sels = sorted(dt_df["selectivity"].unique())
    print(f"[{kst()}] D_target available sels: {available_sels}")

    target_sels = [s for s in TARGET_SELS if s in available_sels]
    if not target_sels:
        print(f"⚠️ TARGET_SELS {TARGET_SELS} 가 D_target 에 없음. dtarget 사전 계산 필요.")
        return
    print(f"[{kst()}] measuring sels: {target_sels}")

    print(f"[{kst()}] fetching DEEP_8M vectors...")
    all_vecs, km_sids = fetch_all_vectors_safe(DEEP_8M)
    print(f"[{kst()}]   {all_vecs.shape[0]:,} × {all_vecs.shape[1]}d "
          f"({all_vecs.nbytes / 1e6:.1f} MB)")

    samples, sizes = cache_cluster_samples(all_vecs, km_sids, seed=42)

    qp = pd.read_parquet(DEEP_8M["query_pool"]).reset_index(drop=True)
    qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32) for i in range(len(qp))])

    alloc = equal_alloc()
    rows = []
    t_total = time.time()

    for sel in target_sels:
        qs_sel = dt_df[dt_df["selectivity"] == sel].sort_values("query_id").reset_index(drop=True)
        qs_sel = qs_sel[qs_sel["query_id"] < args.n_queries]
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
                        "dataset": "DEEP_8M", "mode": mode, "selectivity": sel,
                        "seed": seed, "query_id": qid, "D_target": D,
                        "true_card": true_card, "est": est, "q_error": qerr,
                    })
                print(f"[{kst()}] {mode:>10s} s={sel:.2f} seed={seed} ({(time.time()-t0)*1000:.0f}ms)")

    out = CACHE / f"{args.out_prefix}.parquet"
    pd.DataFrame(rows).to_parquet(out, index=False)
    print(f"[{kst()}] saved {out}")
    print(f"[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
