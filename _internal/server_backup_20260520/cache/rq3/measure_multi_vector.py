#!/usr/bin/env python3
"""
Multi-vector measurement adapter — RQ3 보강.

두 개의 embedding column 을 갖는 테이블 (예: partsupp_deep_sift_10) 에서 단일
column 기반 KM20 vs 두 column 결합 KM20 의 정확도 비교를 위한 측정 백엔드.

기존 RQ3 의 _measure_common 패턴 (KM20 + cluster sample 캐시 + HT estimator)
을 멀티-vector 로 확장:
  - emb1 만 보고 K=20 stratify
  - emb2 만 보고 K=20 stratify
  - concat ([emb1 || emb2]) 한 번에 K=20 stratify
  - product (emb1 의 K=5 × emb2 의 K=4 = 20 cross stratum)

쿼리 카디널리티는 두 거리 조건의 AND. true_card =
  | { i : ||emb1_i - q1||₂ < D1 ∧ ||emb2_i - q2||₂ < D2 } |

각 selectivity 별 D1/D2 는 두 column 의 분포 (rank space) 에서
"emb1 distance percentile × emb2 distance percentile" 곱이 sel 이 되도록 calibrate
한다. 단순화를 위해 두 percentile 을 동일하게 sqrt(sel) 로 잡는다 (대칭 가정).

서버: /mnt/hdd0/home/capstone2026/cache/rq3/measure_multi_vector.py
로컬:  /Users/hyunbin/Capstone/_internal/scripts/measure_multi_vector.py

Usage (서버 측 실행):
    python3 measure_multi_vector.py \
        --table partsupp_deep_sift_10 \
        --emb1-col ps_embedding_deep --emb1-dim 96 \
        --emb2-col ps_embedding_sift --emb2-dim 128 \
        --out-prefix rq2_partsupp_deep_sift_10_4way

산출:
    {CACHE}/rq2_partsupp_deep_sift_10_4way.parquet         (5 modes × 5 sel × 5 seed × 100 q)
    {CACHE}/rq2_partsupp_deep_sift_10_4way_meta.json
    {CACHE}/{table}_emb1.npy / {table}_emb2.npy             (NPY caches, 재사용)
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
    from sklearn.cluster import KMeans
except ImportError as e:
    raise RuntimeError("scikit-learn required (KMeans)") from e


# ---------------------------------------------------------------------------
# 상수 — _measure_common 과 동일한 값 사용
# ---------------------------------------------------------------------------

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
PORT = 55435
DB = "wns41559"
USER = "wns41559"

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20
CACHE_PER_CLUSTER = 500
N_QUERIES = 100

# product stratification 의 K1 × K2 분해
PRODUCT_K1 = 5  # emb1 cluster 수
PRODUCT_K2 = 4  # emb2 cluster 수 — K1*K2 = 20 (= N_STRATA)


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def _connect():
    if psycopg is None:
        raise RuntimeError("psycopg unavailable — measurement requires PG (run on server)")
    return psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True)


# ---------------------------------------------------------------------------
# 1. fetch_dual_vectors — emb1, emb2 둘을 한 row 단위로 fetch
# ---------------------------------------------------------------------------

def fetch_dual_vectors(
    table: str, emb1_col: str, emb2_col: str,
    emb1_dim: int, emb2_dim: int,
    chunk_rows: int = 50_000,
) -> tuple[np.ndarray, np.ndarray]:
    """emb1, emb2 를 동시 fetch — partkey-suppkey order 로 정렬.

    NPY cache fast-path: {table}_emb1.npy, {table}_emb2.npy 가 모두 있으면 PG 우회.

    Returns:
        emb1: (N, emb1_dim) float32
        emb2: (N, emb2_dim) float32
    """
    cache1 = CACHE / f"{table}_emb1.npy"
    cache2 = CACHE / f"{table}_emb2.npy"
    if cache1.exists() and cache2.exists():
        t0 = time.time()
        emb1 = np.load(cache1)
        emb2 = np.load(cache2)
        elapsed = time.time() - t0
        print(f"[{kst()}]   loaded NPY cache: emb1 {emb1.shape}, emb2 {emb2.shape} "
              f"({(emb1.nbytes + emb2.nbytes) / 1e6:.1f} MB) in {elapsed:.1f}s")
        return emb1, emb2

    print(f"[{kst()}]   fetching dual vectors from {table} via PG (chunked)")
    parts1: list[np.ndarray] = []
    parts2: list[np.ndarray] = []
    t0 = time.time()
    offset = 0
    while True:
        with _connect() as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {emb1_col}::real[], {emb2_col}::real[] "
                f"FROM {table} ORDER BY ps_partkey, ps_suppkey "
                f"LIMIT {chunk_rows} OFFSET {offset}"
            )
            rows = cu.fetchall()
        if not rows:
            break
        e1 = np.empty((len(rows), emb1_dim), dtype=np.float32)
        e2 = np.empty((len(rows), emb2_dim), dtype=np.float32)
        for i, (v1, v2) in enumerate(rows):
            e1[i] = np.asarray(v1, dtype=np.float32)
            e2[i] = np.asarray(v2, dtype=np.float32)
        parts1.append(e1)
        parts2.append(e2)
        offset += chunk_rows
        print(f"[{kst()}]     chunk @ offset={offset:>10,} "
              f"(total {sum(p.shape[0] for p in parts1):,} rows so far)")
    emb1 = np.concatenate(parts1, axis=0)
    emb2 = np.concatenate(parts2, axis=0)
    elapsed = time.time() - t0
    print(f"[{kst()}]   fetched emb1 {emb1.shape}, emb2 {emb2.shape} in {elapsed:.1f}s")

    np.save(cache1, emb1)
    np.save(cache2, emb2)
    print(f"[{kst()}]   saved NPY caches: {cache1.name}, {cache2.name}")
    return emb1, emb2


# ---------------------------------------------------------------------------
# 2. stratification strategies — 4-way
# ---------------------------------------------------------------------------

def _km_assign(vectors: np.ndarray, K: int, seed: int = 42, sample_n: int | None = None) -> np.ndarray:
    """KMeans K-cluster fit + predict. Default: full-batch 가 비싸면 sample_n 만큼만 fit."""
    rng = np.random.default_rng(seed)
    if sample_n and sample_n < vectors.shape[0]:
        idx = rng.choice(vectors.shape[0], size=sample_n, replace=False)
        fit_data = vectors[idx]
    else:
        fit_data = vectors
    km = KMeans(n_clusters=K, n_init=10, random_state=seed)
    km.fit(fit_data)
    return km.predict(vectors).astype(np.int32)


def stratify_emb1_only(emb1: np.ndarray) -> np.ndarray:
    """emb1 한 column 만 보고 K=20 stratify."""
    print(f"[{kst()}]   strat: emb1-only K={N_STRATA} fit (sample 100K)")
    return _km_assign(emb1, K=N_STRATA, seed=42, sample_n=100_000)


def stratify_emb2_only(emb2: np.ndarray) -> np.ndarray:
    print(f"[{kst()}]   strat: emb2-only K={N_STRATA} fit (sample 100K)")
    return _km_assign(emb2, K=N_STRATA, seed=42, sample_n=100_000)


def stratify_concat(emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
    """[emb1 || emb2] concat 후 K=20. 단순 결합 — scale mismatch 가능."""
    # 각 emb 의 평균 norm 으로 일단 정규화 (scale 보정).
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    e1 = emb1 / n1
    e2 = emb2 / n2
    concat = np.concatenate([e1, e2], axis=1)
    print(f"[{kst()}]   strat: concat ({concat.shape[1]}d) K={N_STRATA} fit (sample 100K)")
    return _km_assign(concat, K=N_STRATA, seed=42, sample_n=100_000)


def stratify_product(emb1: np.ndarray, emb2: np.ndarray,
                      K1: int = PRODUCT_K1, K2: int = PRODUCT_K2) -> np.ndarray:
    """K1 (emb1) × K2 (emb2) 두 축의 곱 stratum.

    sid_product = sid1 * K2 + sid2 → 0 ~ K1*K2-1.
    """
    print(f"[{kst()}]   strat: product K1={K1} (emb1) × K2={K2} (emb2) = {K1*K2}")
    sid1 = _km_assign(emb1, K=K1, seed=42, sample_n=100_000)
    sid2 = _km_assign(emb2, K=K2, seed=43, sample_n=100_000)
    return (sid1.astype(np.int32) * K2 + sid2.astype(np.int32)).astype(np.int32)


# ---------------------------------------------------------------------------
# 3. cluster sample cache (multi-vector — emb1, emb2 둘 다 캐시)
# ---------------------------------------------------------------------------

def cache_dual_samples(
    emb1: np.ndarray, emb2: np.ndarray, sids: np.ndarray,
    n_strata: int = N_STRATA, cache_per: int = CACHE_PER_CLUSTER, seed: int = 42,
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray], dict[int, int]]:
    """stratum 별 emb1, emb2 sample 동시 캐시 + size 반환."""
    rng = np.random.default_rng(seed)
    s1: dict[int, np.ndarray] = {}
    s2: dict[int, np.ndarray] = {}
    sizes: dict[int, int] = {}
    for sid in range(n_strata):
        mask = sids == sid
        n = int(mask.sum())
        sizes[sid] = n
        if n == 0:
            s1[sid] = np.zeros((1, emb1.shape[1]), dtype=np.float32)
            s2[sid] = np.zeros((1, emb2.shape[1]), dtype=np.float32)
            continue
        idx_in_strat = np.flatnonzero(mask)
        if n > cache_per:
            pick = rng.choice(idx_in_strat, size=cache_per, replace=False)
        else:
            pick = idx_in_strat
        s1[sid] = emb1[pick]
        s2[sid] = emb2[pick]
    return s1, s2, sizes


# ---------------------------------------------------------------------------
# 4. query pool — 100 queries pulled from rows + per-query (D1, D2) per sel
# ---------------------------------------------------------------------------

def build_query_pool(
    emb1: np.ndarray, emb2: np.ndarray,
    n_queries: int = N_QUERIES, sample_for_calib: int = 50_000, seed: int = 1234,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[float, np.ndarray], dict[float, np.ndarray], dict[tuple[int, float], int]]:
    """100 query pull + sel 별 (D1, D2) target + true cardinality 사전 계산.

    각 query 마다, 두 column 의 distance 분포에서 동일 percentile p = sqrt(sel)
    위치를 D1, D2 로 잡는다. 그러면 (대칭 + 두 column 독립 가정 하에)
    P(d1 < D1 ∧ d2 < D2) ≈ p² = sel.

    실제 true_cardinality 는 전체 dataset 에서 정확히 카운트 (calibration 과 ≠).

    Returns:
        qids:      (n_queries,) int — query index in dataset
        q1:        (n_queries, dim1) float32 — emb1 vector
        q2:        (n_queries, dim2) float32 — emb2 vector
        D1_by_sel: {sel: (n_queries,) float32}
        D2_by_sel: {sel: (n_queries,) float32}
        true_card: {(qid, sel): int} — joint AND 카운트
    """
    rng = np.random.default_rng(seed)
    N = emb1.shape[0]
    qids = rng.choice(N, size=n_queries, replace=False)
    q1 = emb1[qids].copy()
    q2 = emb2[qids].copy()

    # D1/D2 calibration: 50K subsample 에서 percentile 잡기
    calib_idx = rng.choice(N, size=min(sample_for_calib, N), replace=False)
    calib1 = emb1[calib_idx]
    calib2 = emb2[calib_idx]

    D1_by_sel: dict[float, np.ndarray] = {}
    D2_by_sel: dict[float, np.ndarray] = {}
    for sel in SELECTIVITIES:
        p = float(np.sqrt(sel))
        d1_vec = np.empty(n_queries, dtype=np.float32)
        d2_vec = np.empty(n_queries, dtype=np.float32)
        for i in range(n_queries):
            d1 = np.linalg.norm(calib1 - q1[i], axis=1)
            d2 = np.linalg.norm(calib2 - q2[i], axis=1)
            d1_vec[i] = float(np.quantile(d1, p))
            d2_vec[i] = float(np.quantile(d2, p))
        D1_by_sel[sel] = d1_vec
        D2_by_sel[sel] = d2_vec
        print(f"[{kst()}]   calib sel={sel:.2f} p={p:.4f} "
              f"D1[mean={d1_vec.mean():.3f}] D2[mean={d2_vec.mean():.3f}]")

    # true cardinality 사전 계산 (전체 dataset 에서 AND)
    print(f"[{kst()}]   computing true cardinalities ({n_queries} q × {len(SELECTIVITIES)} sel) on full N={N:,}")
    true_card: dict[tuple[int, float], int] = {}
    t0 = time.time()
    for i, qid in enumerate(qids):
        # query 한 개에 대해 emb1, emb2 distance 계산 (전체)
        d1_full = np.linalg.norm(emb1 - q1[i], axis=1)
        d2_full = np.linalg.norm(emb2 - q2[i], axis=1)
        for sel in SELECTIVITIES:
            D1 = D1_by_sel[sel][i]
            D2 = D2_by_sel[sel][i]
            tc = int(((d1_full < D1) & (d2_full < D2)).sum())
            true_card[(int(qid), sel)] = tc
        if (i + 1) % 20 == 0:
            print(f"[{kst()}]     true_card progress {i+1}/{n_queries} "
                  f"({(time.time()-t0):.0f}s)")
    print(f"[{kst()}]   true_card done in {time.time()-t0:.1f}s")

    return qids, q1, q2, D1_by_sel, D2_by_sel, true_card


# ---------------------------------------------------------------------------
# 5. estimators (multi-vector)
# ---------------------------------------------------------------------------

def stratified_estimate_dual(
    s1: dict[int, np.ndarray], s2: dict[int, np.ndarray], sizes: dict[int, int],
    alloc: np.ndarray, q1v: np.ndarray, q2v: np.ndarray, D1: float, D2: float,
    rng: np.random.Generator, n_strata: int = N_STRATA,
) -> float:
    est = 0.0
    for sid in range(n_strata):
        cache1 = s1[sid]
        cache2 = s2[sid]
        n_cache = cache1.shape[0]
        s_i = min(int(alloc[sid]), n_cache)
        if s_i < 1:
            s_i = 1
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub1 = cache1[idxs]
        sub2 = cache2[idxs]
        d1 = np.linalg.norm(sub1 - q1v, axis=1)
        d2 = np.linalg.norm(sub2 - q2v, axis=1)
        hits = int(((d1 < D1) & (d2 < D2)).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
    return est


def bernoulli_estimate_dual(
    s1: dict[int, np.ndarray], s2: dict[int, np.ndarray], sizes: dict[int, int],
    q1v: np.ndarray, q2v: np.ndarray, D1: float, D2: float,
    rng: np.random.Generator, budget: int = SAMPLE_SIZE, n_strata: int = N_STRATA,
) -> float:
    total = sum(sizes.values())
    flat1 = np.concatenate([s1[sid] for sid in range(n_strata)], axis=0)
    flat2 = np.concatenate([s2[sid] for sid in range(n_strata)], axis=0)
    n = flat1.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return float(total)
    idxs = rng.choice(n, size=s, replace=False)
    sub1 = flat1[idxs]
    sub2 = flat2[idxs]
    d1 = np.linalg.norm(sub1 - q1v, axis=1)
    d2 = np.linalg.norm(sub2 - q2v, axis=1)
    hits = int(((d1 < D1) & (d2 < D2)).sum())
    return hits * (total / s)


def equal_alloc(n_strata: int = N_STRATA, budget: int = SAMPLE_SIZE) -> np.ndarray:
    base = budget // n_strata
    extra = budget - base * n_strata
    s = np.full(n_strata, base, dtype=int)
    s[:extra] += 1
    return np.maximum(s, 1)


# ---------------------------------------------------------------------------
# 6. measurement loop — BERN baseline + 4 stratification strategies
# ---------------------------------------------------------------------------

def measure_strategy(
    method_name: str, sids: np.ndarray, emb1: np.ndarray, emb2: np.ndarray,
    qids: np.ndarray, q1: np.ndarray, q2: np.ndarray,
    D1_by_sel: dict[float, np.ndarray], D2_by_sel: dict[float, np.ndarray],
    true_card: dict[tuple[int, float], int],
    table_name: str, also_bernoulli: bool = False,
) -> list[dict]:
    """한 stratification 방식 (sids) 으로 5 sel × 5 seed × 100 q 측정."""
    s1, s2, sizes = cache_dual_samples(emb1, emb2, sids)
    print(f"[{kst()}]   {method_name}: stratum sizes "
          f"min={min(sizes.values())} mean={sum(sizes.values())//N_STRATA} "
          f"max={max(sizes.values())}")
    alloc = equal_alloc()

    rows: list[dict] = []
    for sel in SELECTIVITIES:
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in SEEDS:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            t0 = time.time()
            qe_method, qe_bern = [], []
            for i, qid in enumerate(qids):
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = true_card[(int(qid), sel)]
                # method estimate
                est_m = stratified_estimate_dual(s1, s2, sizes, alloc,
                                                  q1[i], q2[i], D1, D2, rng)
                qerr_m = (max(est_m / tc, tc / est_m)
                          if (est_m > 0 and tc > 0) else None)
                rows.append({
                    "table": table_name, "dataset": table_name, "mode": method_name,
                    "selectivity": sel, "seed": seed, "query_id": int(qid),
                    "D1_target": D1, "D2_target": D2, "true_card": tc,
                    "est": est_m, "q_error": qerr_m,
                })
                qe_method.append(qerr_m if qerr_m else float("nan"))

                if also_bernoulli:
                    est_b = bernoulli_estimate_dual(s1, s2, sizes,
                                                     q1[i], q2[i], D1, D2, rng)
                    qerr_b = (max(est_b / tc, tc / est_b)
                              if (est_b > 0 and tc > 0) else None)
                    rows.append({
                        "table": table_name, "dataset": table_name, "mode": "bernoulli",
                        "selectivity": sel, "seed": seed, "query_id": int(qid),
                        "D1_target": D1, "D2_target": D2, "true_card": tc,
                        "est": est_b, "q_error": qerr_b,
                    })
                    qe_bern.append(qerr_b if qerr_b else float("nan"))
            elapsed = time.time() - t0
            med_m = float(np.nanmedian(qe_method))
            extra = (f" bern_med={float(np.nanmedian(qe_bern)):.3f}"
                     if also_bernoulli else "")
            print(f"[{kst()}]     {method_name:>14} sel={sel:.2f} seed={seed} "
                  f"({elapsed*1000:.0f}ms) med_qe={med_m:.4f}{extra}")
    return rows


# ---------------------------------------------------------------------------
# 7. main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True)
    ap.add_argument("--emb1-col", required=True)
    ap.add_argument("--emb2-col", required=True)
    ap.add_argument("--emb1-dim", type=int, required=True)
    ap.add_argument("--emb2-dim", type=int, required=True)
    ap.add_argument("--out-prefix", required=True)
    ap.add_argument("--out-dir", default=str(CACHE))
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{kst()}] === measure_multi_vector ===")
    print(f"[{kst()}] table={args.table} "
          f"emb1={args.emb1_col}({args.emb1_dim}d) emb2={args.emb2_col}({args.emb2_dim}d)")
    print(f"[{kst()}] out: {out_dir}/{args.out_prefix}.parquet")

    # 1) fetch
    emb1, emb2 = fetch_dual_vectors(
        args.table, args.emb1_col, args.emb2_col,
        args.emb1_dim, args.emb2_dim,
    )
    assert emb1.shape[0] == emb2.shape[0], (
        f"row count mismatch: emb1={emb1.shape[0]} vs emb2={emb2.shape[0]}"
    )
    N = emb1.shape[0]
    print(f"[{kst()}] N={N:,} (emb1 dim={emb1.shape[1]}, emb2 dim={emb2.shape[1]})")

    # 2) build query pool + true cardinality
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool(
        emb1, emb2, n_queries=args.n_queries,
    )

    # 3) compute 4 stratification strategies
    print(f"[{kst()}] === stratification ===")
    sids_emb1 = stratify_emb1_only(emb1)
    sids_emb2 = stratify_emb2_only(emb2)
    sids_concat = stratify_concat(emb1, emb2)
    sids_product = stratify_product(emb1, emb2)

    # 4) measure — emb1-only carries BERN baseline
    print(f"[{kst()}] === measurement ===")
    all_rows: list[dict] = []
    all_rows.extend(measure_strategy(
        "km20_emb1", sids_emb1, emb1, emb2, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, args.table, also_bernoulli=True,
    ))
    all_rows.extend(measure_strategy(
        "km20_emb2", sids_emb2, emb1, emb2, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, args.table, also_bernoulli=False,
    ))
    all_rows.extend(measure_strategy(
        "km20_concat", sids_concat, emb1, emb2, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, args.table, also_bernoulli=False,
    ))
    all_rows.extend(measure_strategy(
        "km20_product", sids_product, emb1, emb2, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, args.table, also_bernoulli=False,
    ))

    # 5) save parquet + meta
    df = pd.DataFrame(all_rows)
    out_pq = out_dir / f"{args.out_prefix}.parquet"
    out_meta = out_dir / f"{args.out_prefix}_meta.json"
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = (df.groupby(["dataset", "mode", "selectivity"])["q_error"]
              .agg(["mean", "std", "median", "count"]).round(4))
    print(f"\n=== mean q_error (table × mode × sel) ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "table": args.table,
        "emb1_col": args.emb1_col, "emb1_dim": args.emb1_dim,
        "emb2_col": args.emb2_col, "emb2_dim": args.emb2_dim,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_queries": args.n_queries,
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()),
        "product_decomp": {"K1": PRODUCT_K1, "K2": PRODUCT_K2},
        "calibration": "per-query D1=quantile(d1, sqrt(sel)), D2=quantile(d2, sqrt(sel))",
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] === done ===")


if __name__ == "__main__":
    main()
