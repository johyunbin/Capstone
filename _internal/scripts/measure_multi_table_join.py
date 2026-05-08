#!/usr/bin/env python3
"""
Multi-table join measurement adapter — Exqutor 본 논문 직접 매칭 (RQ 보강).

자연 TPC-H 조인 위에서 두 vector 거리 조건의 AND-of-two-ranges 쿼리에 대한
카디널리티 추정 정확도 측정.

조인 의미 (natural foreign key, 4-to-1):
    SELECT count(*)
    FROM partsupp_deep_10 ps
    JOIN part_wiki_10 p ON ps.ps_partkey = p.p_partkey
    WHERE ||ps.ps_embedding - q_deep|| < D_deep
      AND ||p.p_embedding  - q_wiki|| < D_wiki

partsupp 8M × part 2M, FK 구조상 partsupp 의 각 row 는 part 의 정확히 1 row 와 매칭.
따라서 join 결과는 partsupp 사이즈 (~8M) 와 동일하며, 각 partsupp row 에 wiki
embedding 을 broadcast 한 형태가 된다.

본 측정은 single-table 추정 (`_measure_common.run_method_measurement`)이 다루지
못하는 multi-table join 영역의 BERN vs stratified 비교를 제공한다.
4 strata 정의:
  - km20_deep_only:  KMeans K=20 on partsupp.ps_embedding (96d)
  - km20_wiki_only:  KMeans K=20 on part.p_embedding (768d) — partsupp row 별로
                     ps_partkey 로 lookup 해서 매핑
  - km20_product:    K1=5 (deep) × K2=4 (wiki) cross-strata = 20 stratum
  - bernoulli:       BERN baseline (mode 컬럼만 다르게 동시 산출)

Selectivity calibration: 두 column 의 분포 (50K subsample) 에서
sqrt(sel) percentile 위치를 (D_deep, D_wiki) 로 잡는다 — 두 거리가 대략
독립이라는 대칭 가정 하에 P(deep<D ∧ wiki<D) ≈ sqrt(sel)² = sel.
실제 true_card 는 8M 전체에서 정확 카운트 (calibration 과 ≠).

서버: /mnt/hdd0/home/capstone2026/cache/rq3/measure_multi_table_join.py
로컬: /Users/hyunbin/Capstone/_internal/scripts/measure_multi_table_join.py

Usage:
    python3 measure_multi_table_join.py \
      --partsupp-table partsupp_deep_10 \
      --part-table part_wiki_10 \
      --partsupp-emb-col ps_embedding --partsupp-emb-dim 96 \
      --part-emb-col p_embedding --part-emb-dim 768 \
      --out-prefix rq2_multi_join_deep_wiki

산출:
    {CACHE}/rq2_multi_join_deep_wiki.parquet         (4 modes × 5 sel × 5 seed × 100 q)
    {CACHE}/rq2_multi_join_deep_wiki_meta.json
    {CACHE}/{partsupp-table}_vectors.npy              (NPY cache, 재사용)
    {CACHE}/{part-table}_vectors.npy                  (NPY cache, 재사용)
    {CACHE}/{part-table}_partkeys.npy                 (NPY cache, p_partkey 정렬)
    {CACHE}/{partsupp-table}_partkeys.npy             (NPY cache, ps_partkey 정렬)
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
# 상수 — _measure_common 과 동일한 값 사용. PORT=55435 (vanilla, partsupp_deep_10
# + part_wiki_10 가 살아있는 인스턴스)
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

# product stratification 분해: 5 × 4 = 20
PRODUCT_K1 = 5  # deep cluster 수
PRODUCT_K2 = 4  # wiki cluster 수


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def _connect():
    if psycopg is None:
        raise RuntimeError("psycopg unavailable — run on server (165.132.140.240)")
    return psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True)


# ---------------------------------------------------------------------------
# 1. fetch — partsupp (composite PK) + part (single PK)
# ---------------------------------------------------------------------------

def fetch_partsupp(
    table: str, emb_col: str, emb_dim: int, chunk_rows: int = 50_000,
) -> tuple[np.ndarray, np.ndarray]:
    """partsupp_*_10 의 ps_embedding + ps_partkey 동시 fetch.

    ps_partkey, ps_suppkey 복합키 순으로 정렬. NPY cache fast-path:
      - {table}_vectors.npy  : (N, emb_dim) float32
      - {table}_partkeys.npy : (N,) int64

    Returns:
        emb:      (N, emb_dim) float32  — ps_embedding
        partkeys: (N,) int64            — ps_partkey (8M, 같은 partkey 가 4번 반복 가능)
    """
    cache_v = CACHE / f"{table}_vectors.npy"
    cache_k = CACHE / f"{table}_partkeys.npy"
    if cache_v.exists() and cache_k.exists():
        t0 = time.time()
        emb = np.load(cache_v)
        keys = np.load(cache_k)
        elapsed = time.time() - t0
        print(f"[{kst()}]   loaded NPY cache: {table} {emb.shape} + keys {keys.shape} "
              f"({(emb.nbytes + keys.nbytes) / 1e6:.1f} MB) in {elapsed:.1f}s")
        return emb, keys

    print(f"[{kst()}]   fetching {table} via PG (chunked, ORDER BY ps_partkey, ps_suppkey)")
    parts_v: list[np.ndarray] = []
    parts_k: list[np.ndarray] = []
    t0 = time.time()
    offset = 0
    while True:
        with _connect() as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT ps_partkey, {emb_col}::real[] FROM {table} "
                f"ORDER BY ps_partkey, ps_suppkey "
                f"LIMIT {chunk_rows} OFFSET {offset}"
            )
            rows = cu.fetchall()
        if not rows:
            break
        e = np.empty((len(rows), emb_dim), dtype=np.float32)
        k = np.empty(len(rows), dtype=np.int64)
        for i, (pk, v) in enumerate(rows):
            k[i] = pk
            e[i] = np.asarray(v, dtype=np.float32)
        parts_v.append(e)
        parts_k.append(k)
        offset += chunk_rows
        print(f"[{kst()}]     chunk @ offset={offset:>10,} "
              f"(total {sum(p.shape[0] for p in parts_v):,} rows)")
    emb = np.concatenate(parts_v, axis=0)
    keys = np.concatenate(parts_k, axis=0)
    elapsed = time.time() - t0
    print(f"[{kst()}]   fetched {table}: emb {emb.shape}, keys {keys.shape} in {elapsed:.1f}s")

    np.save(cache_v, emb)
    np.save(cache_k, keys)
    print(f"[{kst()}]   saved NPY caches: {cache_v.name}, {cache_k.name}")
    return emb, keys


def fetch_part(
    table: str, emb_col: str, emb_dim: int, chunk_rows: int = 50_000,
) -> tuple[np.ndarray, np.ndarray]:
    """part_*_10 의 p_embedding + p_partkey fetch (single PK, ORDER BY p_partkey).

    Returns:
        emb:     (M, emb_dim) float32  — p_embedding
        partkey: (M,) int64            — p_partkey (M=2M, unique)
    """
    cache_v = CACHE / f"{table}_vectors.npy"
    cache_k = CACHE / f"{table}_partkeys.npy"
    if cache_v.exists() and cache_k.exists():
        t0 = time.time()
        emb = np.load(cache_v)
        keys = np.load(cache_k)
        elapsed = time.time() - t0
        print(f"[{kst()}]   loaded NPY cache: {table} {emb.shape} + keys {keys.shape} "
              f"({(emb.nbytes + keys.nbytes) / 1e6:.1f} MB) in {elapsed:.1f}s")
        return emb, keys

    print(f"[{kst()}]   fetching {table} via PG (chunked, ORDER BY p_partkey)")
    parts_v: list[np.ndarray] = []
    parts_k: list[np.ndarray] = []
    t0 = time.time()
    offset = 0
    while True:
        with _connect() as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT p_partkey, {emb_col}::real[] FROM {table} "
                f"ORDER BY p_partkey "
                f"LIMIT {chunk_rows} OFFSET {offset}"
            )
            rows = cu.fetchall()
        if not rows:
            break
        e = np.empty((len(rows), emb_dim), dtype=np.float32)
        k = np.empty(len(rows), dtype=np.int64)
        for i, (pk, v) in enumerate(rows):
            k[i] = pk
            e[i] = np.asarray(v, dtype=np.float32)
        parts_v.append(e)
        parts_k.append(k)
        offset += chunk_rows
        print(f"[{kst()}]     chunk @ offset={offset:>10,} "
              f"(total {sum(p.shape[0] for p in parts_v):,} rows)")
    emb = np.concatenate(parts_v, axis=0)
    keys = np.concatenate(parts_k, axis=0)
    elapsed = time.time() - t0
    print(f"[{kst()}]   fetched {table}: emb {emb.shape}, keys {keys.shape} in {elapsed:.1f}s")

    np.save(cache_v, emb)
    np.save(cache_k, keys)
    print(f"[{kst()}]   saved NPY caches: {cache_v.name}, {cache_k.name}")
    return emb, keys


# ---------------------------------------------------------------------------
# 2. join broadcast — partsupp row 별로 wiki embedding 매핑
# ---------------------------------------------------------------------------

def build_join(
    ps_emb: np.ndarray, ps_keys: np.ndarray,
    p_emb: np.ndarray, p_keys: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """partsupp 의 각 row 에 part embedding 을 broadcast (FK 매칭).

    각 ps_partkey 는 part_wiki_10 의 정확히 1 row 와 매칭됨 (FK constraint).
    따라서 결과 길이는 partsupp 와 같다 (~8M).

    Returns:
        deep_join: (N_partsupp, deep_dim)  — partsupp 순서 그대로 (변형 X)
        wiki_join: (N_partsupp, wiki_dim)  — partsupp row 별 매칭된 part embedding
    """
    print(f"[{kst()}]   join: building lookup p_partkey → p_embedding row index")
    # part 가 p_partkey 정렬된 상태이고 unique 라고 가정. searchsorted 로 매핑.
    sort_idx = np.argsort(p_keys, kind="stable")
    sorted_p_keys = p_keys[sort_idx]
    pos = np.searchsorted(sorted_p_keys, ps_keys)
    # partsupp 의 모든 ps_partkey 가 part 에 존재해야 함 (FK 보장). 검증.
    if pos.max() >= len(p_keys) or not np.all(sorted_p_keys[pos] == ps_keys):
        # FK 가 끊겨있는 경우 (예: 1M subset 등) 해당 row 만 마스킹
        valid = (pos < len(p_keys)) & (sorted_p_keys[np.clip(pos, 0, len(p_keys) - 1)] == ps_keys)
        n_invalid = int((~valid).sum())
        print(f"[{kst()}]   WARNING: {n_invalid:,} partsupp rows have no matching part (FK gap)")
        # 무효 행은 일단 0번 인덱스로 매핑하지만 이후 측정에서 제외해야 함
        pos = np.where(valid, pos, 0)
    # sort_idx 를 통해 원래 part 의 row index 로 변환
    p_row_idx = sort_idx[pos]
    print(f"[{kst()}]   join: gathering wiki embeddings for {len(ps_keys):,} partsupp rows")
    wiki_join = p_emb[p_row_idx]
    deep_join = ps_emb  # partsupp 그대로 (broadcast 없음)
    print(f"[{kst()}]   join done: deep {deep_join.shape}, wiki {wiki_join.shape} "
          f"({(deep_join.nbytes + wiki_join.nbytes) / 1e9:.2f} GB combined)")
    return deep_join, wiki_join


# ---------------------------------------------------------------------------
# 3. KMeans stratification — 3 strategies (deep / wiki / product)
# ---------------------------------------------------------------------------

def _km_assign(vectors: np.ndarray, K: int, seed: int = 42,
               sample_n: int | None = 100_000) -> np.ndarray:
    """KMeans K-cluster fit (sample) + predict (전체)."""
    rng = np.random.default_rng(seed)
    if sample_n and sample_n < vectors.shape[0]:
        idx = rng.choice(vectors.shape[0], size=sample_n, replace=False)
        fit_data = vectors[idx]
    else:
        fit_data = vectors
    km = KMeans(n_clusters=K, n_init=10, random_state=seed)
    km.fit(fit_data)
    return km.predict(vectors).astype(np.int32)


def stratify_deep_only(deep_join: np.ndarray) -> np.ndarray:
    """partsupp.ps_embedding (96d) 한 column 만으로 K=20."""
    print(f"[{kst()}]   strat: deep-only K={N_STRATA} fit (sample 100K)")
    return _km_assign(deep_join, K=N_STRATA, seed=42)


def stratify_wiki_only(wiki_join: np.ndarray) -> np.ndarray:
    """part.p_embedding (768d) 만으로 K=20. partsupp row 별로 broadcast 된 형태."""
    print(f"[{kst()}]   strat: wiki-only K={N_STRATA} fit (sample 100K)")
    # 768d * 100K * 4byte = ~310 MB fit data — 안전
    return _km_assign(wiki_join, K=N_STRATA, seed=42)


def stratify_product(deep_join: np.ndarray, wiki_join: np.ndarray,
                      K1: int = PRODUCT_K1, K2: int = PRODUCT_K2) -> np.ndarray:
    """K1 (deep) × K2 (wiki) 곱 stratum. sid = sid_deep * K2 + sid_wiki ∈ [0, K1*K2)."""
    print(f"[{kst()}]   strat: product K1={K1} (deep) × K2={K2} (wiki) = {K1*K2}")
    sid1 = _km_assign(deep_join, K=K1, seed=42)
    sid2 = _km_assign(wiki_join, K=K2, seed=43)
    return (sid1.astype(np.int32) * K2 + sid2.astype(np.int32)).astype(np.int32)


# ---------------------------------------------------------------------------
# 4. cluster sample cache — deep + wiki 동시 캐시
# ---------------------------------------------------------------------------

def cache_dual_samples(
    deep: np.ndarray, wiki: np.ndarray, sids: np.ndarray,
    n_strata: int = N_STRATA, cache_per: int = CACHE_PER_CLUSTER, seed: int = 42,
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray], dict[int, int]]:
    """stratum 별 deep, wiki sample 동시 캐시 + 사이즈."""
    rng = np.random.default_rng(seed)
    sd: dict[int, np.ndarray] = {}
    sw: dict[int, np.ndarray] = {}
    sizes: dict[int, int] = {}
    for sid in range(n_strata):
        mask = sids == sid
        n = int(mask.sum())
        sizes[sid] = n
        if n == 0:
            sd[sid] = np.zeros((1, deep.shape[1]), dtype=np.float32)
            sw[sid] = np.zeros((1, wiki.shape[1]), dtype=np.float32)
            continue
        idx_in = np.flatnonzero(mask)
        if n > cache_per:
            pick = rng.choice(idx_in, size=cache_per, replace=False)
        else:
            pick = idx_in
        sd[sid] = deep[pick]
        sw[sid] = wiki[pick]
    return sd, sw, sizes


# ---------------------------------------------------------------------------
# 5. query pool — random row 100개 → (q_deep, q_wiki) + sel 별 (D_deep, D_wiki)
# ---------------------------------------------------------------------------

def build_query_pool(
    deep: np.ndarray, wiki: np.ndarray,
    n_queries: int = N_QUERIES, sample_for_calib: int = 50_000, seed: int = 1234,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[float, np.ndarray], dict[float, np.ndarray], dict[tuple[int, float], int]]:
    """100 query 행 추출 + sel 별 (D_deep, D_wiki) calibration + true cardinality 사전 계산.

    각 query 마다, 두 distance 분포에서 동일 percentile p = sqrt(sel) 위치를
    D_deep, D_wiki 로 잡는다. 두 거리가 대략 독립이라는 대칭 가정 하에
    P(d_deep<D_deep ∧ d_wiki<D_wiki) ≈ p² = sel.

    실제 true_card 는 8M 전체에서 정확 카운트.
    """
    rng = np.random.default_rng(seed)
    N = deep.shape[0]
    qids = rng.choice(N, size=n_queries, replace=False)
    q_deep = deep[qids].copy()
    q_wiki = wiki[qids].copy()

    # 50K subsample 에서 percentile 계산
    calib_idx = rng.choice(N, size=min(sample_for_calib, N), replace=False)
    calib_d = deep[calib_idx]
    calib_w = wiki[calib_idx]

    D_deep_by_sel: dict[float, np.ndarray] = {}
    D_wiki_by_sel: dict[float, np.ndarray] = {}
    for sel in SELECTIVITIES:
        p = float(np.sqrt(sel))
        Dd = np.empty(n_queries, dtype=np.float32)
        Dw = np.empty(n_queries, dtype=np.float32)
        for i in range(n_queries):
            d_d = np.linalg.norm(calib_d - q_deep[i], axis=1)
            d_w = np.linalg.norm(calib_w - q_wiki[i], axis=1)
            Dd[i] = float(np.quantile(d_d, p))
            Dw[i] = float(np.quantile(d_w, p))
        D_deep_by_sel[sel] = Dd
        D_wiki_by_sel[sel] = Dw
        print(f"[{kst()}]   calib sel={sel:.2f} p={p:.4f} "
              f"D_deep[mean={Dd.mean():.3f}] D_wiki[mean={Dw.mean():.3f}]")

    # true cardinality 사전 계산 (8M 전체에서 AND)
    print(f"[{kst()}]   computing true cardinalities ({n_queries} q × {len(SELECTIVITIES)} sel) on N={N:,}")
    true_card: dict[tuple[int, float], int] = {}
    t0 = time.time()
    for i, qid in enumerate(qids):
        d_d_full = np.linalg.norm(deep - q_deep[i], axis=1)
        d_w_full = np.linalg.norm(wiki - q_wiki[i], axis=1)
        for sel in SELECTIVITIES:
            Dd = D_deep_by_sel[sel][i]
            Dw = D_wiki_by_sel[sel][i]
            tc = int(((d_d_full < Dd) & (d_w_full < Dw)).sum())
            true_card[(int(qid), sel)] = tc
        if (i + 1) % 20 == 0:
            print(f"[{kst()}]     true_card progress {i+1}/{n_queries} "
                  f"({(time.time()-t0):.0f}s)")
    print(f"[{kst()}]   true_card done in {time.time()-t0:.1f}s")

    return qids, q_deep, q_wiki, D_deep_by_sel, D_wiki_by_sel, true_card


# ---------------------------------------------------------------------------
# 6. estimators — dual-distance HT + dual-distance bernoulli
# ---------------------------------------------------------------------------

def equal_alloc(n_strata: int = N_STRATA, budget: int = SAMPLE_SIZE) -> np.ndarray:
    base = budget // n_strata
    extra = budget - base * n_strata
    s = np.full(n_strata, base, dtype=int)
    s[:extra] += 1
    return np.maximum(s, 1)


def stratified_estimate_join(
    sd: dict[int, np.ndarray], sw: dict[int, np.ndarray], sizes: dict[int, int],
    alloc: np.ndarray, q_deep: np.ndarray, q_wiki: np.ndarray,
    D_deep: float, D_wiki: float,
    rng: np.random.Generator, n_strata: int = N_STRATA,
) -> float:
    """HT estimator with dual-distance check: hits := |{i: d_deep<D_deep ∧ d_wiki<D_wiki}|."""
    est = 0.0
    for sid in range(n_strata):
        cache_d = sd[sid]
        cache_w = sw[sid]
        n_cache = cache_d.shape[0]
        s_i = min(int(alloc[sid]), n_cache)
        if s_i < 1:
            s_i = 1
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub_d = cache_d[idxs]
        sub_w = cache_w[idxs]
        d_d = np.linalg.norm(sub_d - q_deep, axis=1)
        d_w = np.linalg.norm(sub_w - q_wiki, axis=1)
        hits = int(((d_d < D_deep) & (d_w < D_wiki)).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
    return est


def bernoulli_estimate_join(
    sd: dict[int, np.ndarray], sw: dict[int, np.ndarray], sizes: dict[int, int],
    q_deep: np.ndarray, q_wiki: np.ndarray, D_deep: float, D_wiki: float,
    rng: np.random.Generator, budget: int = SAMPLE_SIZE, n_strata: int = N_STRATA,
) -> float:
    """BERN baseline: 모든 stratum 의 cache 를 합친 후 budget 만큼 random sample."""
    total = sum(sizes.values())
    flat_d = np.concatenate([sd[sid] for sid in range(n_strata)], axis=0)
    flat_w = np.concatenate([sw[sid] for sid in range(n_strata)], axis=0)
    n = flat_d.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return float(total)
    idxs = rng.choice(n, size=s, replace=False)
    sub_d = flat_d[idxs]
    sub_w = flat_w[idxs]
    d_d = np.linalg.norm(sub_d - q_deep, axis=1)
    d_w = np.linalg.norm(sub_w - q_wiki, axis=1)
    hits = int(((d_d < D_deep) & (d_w < D_wiki)).sum())
    return hits * (total / s)


# ---------------------------------------------------------------------------
# 7. measurement loop
# ---------------------------------------------------------------------------

def measure_strategy(
    method_name: str, sids: np.ndarray, deep: np.ndarray, wiki: np.ndarray,
    qids: np.ndarray, q_deep: np.ndarray, q_wiki: np.ndarray,
    D_deep_by_sel: dict[float, np.ndarray], D_wiki_by_sel: dict[float, np.ndarray],
    true_card: dict[tuple[int, float], int],
    table_pair: str, also_bernoulli: bool = False,
) -> list[dict]:
    """한 stratification 으로 5 sel × 5 seed × 100 q 측정."""
    sd, sw, sizes = cache_dual_samples(deep, wiki, sids)
    print(f"[{kst()}]   {method_name}: stratum sizes "
          f"min={min(sizes.values())} mean={sum(sizes.values())//N_STRATA} "
          f"max={max(sizes.values())}")
    alloc = equal_alloc()

    rows: list[dict] = []
    for sel in SELECTIVITIES:
        Dd_vec = D_deep_by_sel[sel]
        Dw_vec = D_wiki_by_sel[sel]
        for seed in SEEDS:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            t0 = time.time()
            qe_method, qe_bern = [], []
            for i, qid in enumerate(qids):
                Dd = float(Dd_vec[i])
                Dw = float(Dw_vec[i])
                tc = true_card[(int(qid), sel)]
                # method estimate
                est_m = stratified_estimate_join(
                    sd, sw, sizes, alloc, q_deep[i], q_wiki[i], Dd, Dw, rng
                )
                qerr_m = (max(est_m / tc, tc / est_m)
                          if (est_m > 0 and tc > 0) else None)
                rows.append({
                    "table_pair": table_pair, "dataset": table_pair, "mode": method_name,
                    "selectivity": sel, "seed": seed, "query_id": int(qid),
                    "D_deep_target": Dd, "D_wiki_target": Dw, "true_card": tc,
                    "est": est_m, "q_error": qerr_m,
                })
                qe_method.append(qerr_m if qerr_m else float("nan"))

                if also_bernoulli:
                    est_b = bernoulli_estimate_join(
                        sd, sw, sizes, q_deep[i], q_wiki[i], Dd, Dw, rng
                    )
                    qerr_b = (max(est_b / tc, tc / est_b)
                              if (est_b > 0 and tc > 0) else None)
                    rows.append({
                        "table_pair": table_pair, "dataset": table_pair, "mode": "bernoulli",
                        "selectivity": sel, "seed": seed, "query_id": int(qid),
                        "D_deep_target": Dd, "D_wiki_target": Dw, "true_card": tc,
                        "est": est_b, "q_error": qerr_b,
                    })
                    qe_bern.append(qerr_b if qerr_b else float("nan"))
            elapsed = time.time() - t0
            med_m = float(np.nanmedian(qe_method)) if qe_method else float("nan")
            extra = (f" bern_med={float(np.nanmedian(qe_bern)):.3f}"
                     if also_bernoulli else "")
            print(f"[{kst()}]     {method_name:>15} sel={sel:.2f} seed={seed} "
                  f"({elapsed*1000:.0f}ms) med_qe={med_m:.4f}{extra}")
    return rows


# ---------------------------------------------------------------------------
# 8. main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partsupp-table", required=True,
                    help="e.g. partsupp_deep_10")
    ap.add_argument("--part-table", required=True,
                    help="e.g. part_wiki_10")
    ap.add_argument("--partsupp-emb-col", required=True, help="e.g. ps_embedding")
    ap.add_argument("--partsupp-emb-dim", type=int, required=True, help="e.g. 96")
    ap.add_argument("--part-emb-col", required=True, help="e.g. p_embedding")
    ap.add_argument("--part-emb-dim", type=int, required=True, help="e.g. 768")
    ap.add_argument("--out-prefix", required=True,
                    help="e.g. rq2_multi_join_deep_wiki")
    ap.add_argument("--out-dir", default=str(CACHE))
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    table_pair = f"{args.partsupp_table}__{args.part_table}"

    print(f"[{kst()}] === measure_multi_table_join ===")
    print(f"[{kst()}] partsupp={args.partsupp_table}.{args.partsupp_emb_col}({args.partsupp_emb_dim}d)")
    print(f"[{kst()}] part    ={args.part_table}.{args.part_emb_col}({args.part_emb_dim}d)")
    print(f"[{kst()}] join: ps_partkey = p_partkey (FK)")
    print(f"[{kst()}] out: {out_dir}/{args.out_prefix}.parquet")

    # 1) fetch — partsupp + part
    ps_emb, ps_keys = fetch_partsupp(
        args.partsupp_table, args.partsupp_emb_col, args.partsupp_emb_dim,
    )
    p_emb, p_keys = fetch_part(
        args.part_table, args.part_emb_col, args.part_emb_dim,
    )
    print(f"[{kst()}] partsupp N={ps_emb.shape[0]:,} part M={p_emb.shape[0]:,} "
          f"(FK ratio = {ps_emb.shape[0] / max(p_emb.shape[0], 1):.2f})")

    # 2) join — partsupp 의 각 row 에 part embedding 매핑
    deep_join, wiki_join = build_join(ps_emb, ps_keys, p_emb, p_keys)
    # 메모리 절약 — ps_emb 는 deep_join 과 동일 (참조) 이므로 p_emb / p_keys 만 free
    del p_emb, p_keys, ps_keys

    N = deep_join.shape[0]
    print(f"[{kst()}] join result N={N:,} "
          f"(deep {deep_join.shape[1]}d + wiki {wiki_join.shape[1]}d, "
          f"{(deep_join.nbytes + wiki_join.nbytes) / 1e9:.2f} GB)")

    # 3) build query pool + true cardinality (8M 전체 dual-distance)
    print(f"[{kst()}] === query pool + true cardinality ===")
    qids, q_deep, q_wiki, Dd_by_sel, Dw_by_sel, true_card = build_query_pool(
        deep_join, wiki_join, n_queries=args.n_queries,
    )

    # 4) stratification — 3 strategies
    print(f"[{kst()}] === stratification ===")
    sids_deep = stratify_deep_only(deep_join)
    sids_wiki = stratify_wiki_only(wiki_join)
    sids_product = stratify_product(deep_join, wiki_join)

    # 5) measure — deep_only 가 BERN baseline 동시 산출
    print(f"[{kst()}] === measurement ===")
    all_rows: list[dict] = []
    all_rows.extend(measure_strategy(
        "km20_deep_only", sids_deep, deep_join, wiki_join, qids, q_deep, q_wiki,
        Dd_by_sel, Dw_by_sel, true_card, table_pair, also_bernoulli=True,
    ))
    all_rows.extend(measure_strategy(
        "km20_wiki_only", sids_wiki, deep_join, wiki_join, qids, q_deep, q_wiki,
        Dd_by_sel, Dw_by_sel, true_card, table_pair, also_bernoulli=False,
    ))
    all_rows.extend(measure_strategy(
        "km20_product", sids_product, deep_join, wiki_join, qids, q_deep, q_wiki,
        Dd_by_sel, Dw_by_sel, true_card, table_pair, also_bernoulli=False,
    ))

    # 6) save parquet + meta
    df = pd.DataFrame(all_rows)
    out_pq = out_dir / f"{args.out_prefix}.parquet"
    out_meta = out_dir / f"{args.out_prefix}_meta.json"
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = (df.groupby(["dataset", "mode", "selectivity"])["q_error"]
              .agg(["mean", "std", "median", "count"]).round(4))
    print(f"\n=== mean q_error (table_pair × mode × sel) ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "partsupp_table": args.partsupp_table,
        "part_table": args.part_table,
        "table_pair": table_pair,
        "partsupp_emb_col": args.partsupp_emb_col,
        "partsupp_emb_dim": args.partsupp_emb_dim,
        "part_emb_col": args.part_emb_col,
        "part_emb_dim": args.part_emb_dim,
        "join": "partsupp.ps_partkey = part.p_partkey (FK, 4-to-1)",
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_queries": args.n_queries,
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()),
        "product_decomp": {"K1_deep": PRODUCT_K1, "K2_wiki": PRODUCT_K2},
        "calibration": "per-query D_deep=quantile(d_deep, sqrt(sel)), D_wiki=quantile(d_wiki, sqrt(sel))",
        "join_n": int(N),
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] === done ===")


if __name__ == "__main__":
    main()
