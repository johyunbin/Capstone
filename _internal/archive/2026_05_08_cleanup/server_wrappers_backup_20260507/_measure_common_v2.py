#!/usr/bin/env python3
"""
RQ3 측정 공통 백엔드.

rq2_alloc_python.py 의 측정 패턴을 method-agnostic 으로 추출. RQ3 의 7-way 방법은
stratum_id 부여 알고리즘만 다르고 측정 단계 (cluster sample 캐시 + HT estimator + BERN)
는 동일하다.

핵심 흐름 (RQ3 방법별 wrapper 에서 호출):
1. fetch_all_vectors_safe(ds): 전체 row 의 vector 를 KM20 cluster 단위 fresh conn 으로 fetch
   (PG vector::real[] cast 의 메모리 누수 회피, 5/6 발견 사례)
2. method-specific stratum_id 부여 (in-memory, wrapper 에서 호출)
3. cache_cluster_samples_inmem(all_vecs, stratum_ids): cluster 별 LIMIT 500 sample 캐시
4. run_method_measurement(method_name, ...): 5 sel × 5 seed × 100 query × HT estimator

사용 예:
    from _measure_common import (
        DATASETS, fetch_all_vectors_safe, run_method_measurement, save_parquet_meta,
    )
    all_vecs, km20_sids = fetch_all_vectors_safe(ds)
    method_sids = my_method.assign(all_vecs)        # method-specific
    rows = run_method_measurement('minibatch', all_vecs, method_sids, ds)
    save_parquet_meta(rows, prefix='rq3_minibatch', extra_meta={'learn_frac': 0.01})

서버 경로: /mnt/hdd0/home/capstone2026/cache/rq3/_measure_common.py
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import psycopg  # PG 의존 — 서버에서만 import 성공
except ImportError:
    psycopg = None  # 로컬 개발 시 측정 함수 호출 X 라 OK

try:
    import pyarrow.parquet as pq
except ImportError:
    pq = None

# ---------------------------------------------------------------------------
# 측정 상수 (RQ2 와 동일)
# ---------------------------------------------------------------------------

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
PORT = 55436
DB = "wns41559"
USER = "wns41559"

SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE = 385
N_STRATA = 20
CACHE_PER_CLUSTER = 500

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


# 8M sensitivity 분석용 (메인 세션 8M 측정 완료 후 활성). 사용 예:
#     from _measure_common import DATASETS_8M
#     for ds in DATASETS_8M: ...
# query_selectivity_8m.parquet 은 phase7_8m_dtarget_midsel.json 을 변환해 생성
# (scripts/convert_8m_dtarget_to_parquet.py 참조). 현재 sel ∈ {0.1, 0.3} 만 사용 가능.
DATASETS_8M = [
    {
        "name": "DEEP_8M",
        "table": "partsupp_deep_10_phase7_8m_subset",
        "embed_col": "ps_embedding",
        "vec_dim": 96,
        "query_pool": CACHE / "query_pool.parquet",  # 1M 과 같은 query 풀
        "query_sel": CACHE / "query_selectivity_8m.parquet",  # 8M 측정 후 생성 필요
    },
]


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def _connect():
    if psycopg is None:
        raise RuntimeError(
            "psycopg unavailable — measurement requires PG. "
            "Run on server (165.132.140.240, capstone2026)."
        )
    return psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True)


# ---------------------------------------------------------------------------
# 1. fetch_all_vectors_safe — KM20 cluster 단위 fresh conn fetch
# ---------------------------------------------------------------------------

def fetch_all_vectors_safe(ds: dict, n_strata: int = N_STRATA):
    """전체 row 의 vector 를 fetch — cluster (KM20 stratum_id) 별 fresh conn.

    PG `vector::real[]` cast 의 누적 메모리 누수 회피 (5/6 trade-off 검증). 각 cluster
    마다 새 connection 으로 ~50K rows fetch → close → 다음 cluster.

    NPY cache fast-path (5/7 W3 추가): {ds['table']}_vectors.npy 가 존재하면
    PG fetch 우회 — 1순위 cache 로딩 (8M dataset 5분 → 30초 단축).

    Returns:
        all_vecs: (N, dim) float32 — stratum_id 순서로 정렬됨 (cluster 별 grouping)
        km20_sids: (N,) int32
    """
    table = ds["table"]
    embed_col = ds["embed_col"]
    cache_npy = CACHE / f"{table}_vectors.npy"

    if cache_npy.exists():
        t0 = time.time()
        all_vecs_raw = np.load(cache_npy)
        pk_col = "c_custkey" if embed_col == "c_embedding" else "ps_partkey"
        with _connect() as c:
            cu = c.cursor()
            cu.execute(f"SELECT stratum_id::int FROM {table} ORDER BY {pk_col}")
            sid_by_pk = np.asarray([r[0] for r in cu.fetchall()], dtype=np.int32)
        if len(sid_by_pk) != len(all_vecs_raw):
            print(f"[{kst()}]   npy cache size mismatch ({len(all_vecs_raw)} vs PG {len(sid_by_pk)}) — fallback to PG fetch")
        else:
            order = np.argsort(sid_by_pk, kind='stable')
            all_vecs = all_vecs_raw[order]
            km20_sids = sid_by_pk[order]
            elapsed = time.time() - t0
            print(
                f"[{kst()}]   fetched {all_vecs.shape[0]:,} × {all_vecs.shape[1]}d "
                f"({all_vecs.nbytes / 1e6:.1f} MB) in {elapsed:.1f}s [npy cache]"
            )
            return all_vecs, km20_sids

    parts: list[np.ndarray] = []
    km_sids: list[np.ndarray] = []

    t0 = time.time()
    for sid in range(n_strata):
        with _connect() as c:
            cu = c.cursor()
            cu.execute(
                f"SELECT {embed_col}::real[] FROM {table} "
                f"WHERE stratum_id = {sid}"
            )
            rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
        if rows:
            arr = np.stack(rows)
            parts.append(arr)
            km_sids.append(np.full(arr.shape[0], sid, dtype=np.int32))
    elapsed = time.time() - t0
    all_vecs = np.concatenate(parts, axis=0)
    km20_sids = np.concatenate(km_sids, axis=0)
    print(
        f"[{kst()}]   fetched {all_vecs.shape[0]:,} × {all_vecs.shape[1]}d "
        f"({all_vecs.nbytes / 1e6:.1f} MB) in {elapsed:.1f}s"
    )
    return all_vecs, km20_sids


# ---------------------------------------------------------------------------
# 2. cache_cluster_samples_inmem — in-memory stratum_id → cluster 별 sample 캐시
# ---------------------------------------------------------------------------

def cache_cluster_samples_inmem(
    all_vecs: np.ndarray,
    stratum_ids: np.ndarray,
    n_strata: int = N_STRATA,
    cache_per_cluster: int = CACHE_PER_CLUSTER,
    seed: int = 42,
):
    """method-specific stratum_id 로 cluster sample 캐시.

    각 cluster 의 row 가 cache_per_cluster 보다 많으면 무작위 sample. 이 sample 은
    HT estimator 가 매 query 마다 다시 random.choice 하는 모집단 역할. 부족하면 그대로.
    """
    rng = np.random.default_rng(seed)
    samples: dict[int, np.ndarray] = {}
    sizes: dict[int, int] = {}
    for sid in range(n_strata):
        mask = stratum_ids == sid
        n_cluster = int(mask.sum())
        sizes[sid] = n_cluster
        if n_cluster == 0:
            samples[sid] = np.zeros((1, all_vecs.shape[1]), dtype=np.float32)
            continue
        cluster_vecs = all_vecs[mask]
        if n_cluster > cache_per_cluster:
            idx = rng.choice(n_cluster, size=cache_per_cluster, replace=False)
            samples[sid] = cluster_vecs[idx]
        else:
            samples[sid] = cluster_vecs
    return samples, sizes


# ---------------------------------------------------------------------------
# 3. allocation — equal (KM20-compatible) / proportional / neyman
# ---------------------------------------------------------------------------

def equal_alloc(n_strata: int = N_STRATA, budget: int = SAMPLE_SIZE) -> np.ndarray:
    """KM20 등 stratum 균등 배분."""
    base = budget // n_strata
    extra = budget - base * n_strata
    s = np.full(n_strata, base, dtype=int)
    s[:extra] += 1
    return np.maximum(s, 1)


def proportional_alloc(sizes: dict[int, int], budget: int = SAMPLE_SIZE,
                        n_strata: int = N_STRATA) -> np.ndarray:
    """N_i 비례 배분."""
    sz = np.array([sizes.get(j, 0) for j in range(n_strata)], dtype=float)
    if sz.sum() <= 0:
        return equal_alloc(n_strata, budget)
    f = sz / sz.sum() * budget
    s = np.maximum(f.astype(int), 1)
    extra = budget - int(s.sum())
    if extra > 0:
        frac = f - f.astype(int)
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


# ---------------------------------------------------------------------------
# 4. estimators (rq2_alloc_python.py 그대로)
# ---------------------------------------------------------------------------

def stratified_estimate(samples, sizes, alloc, qvec, D, rng):
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
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
    return est


def bernoulli_estimate(samples, sizes, qvec, D, rng, budget=SAMPLE_SIZE,
                        n_strata=N_STRATA):
    total_rows = sum(sizes.values())
    flat = np.concatenate([samples[sid] for sid in range(n_strata)], axis=0)
    n = flat.shape[0]
    s = min(int(budget), n)
    if s == 0:
        return total_rows
    idxs = rng.choice(n, size=s, replace=False)
    sub = flat[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (total_rows / s)


# ---------------------------------------------------------------------------
# 5. run_method_measurement — 측정 골격 (method-agnostic)
# ---------------------------------------------------------------------------

def _load_query_pool(ds: dict):
    qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
    qs_full = pq.read_table(ds["query_sel"]).to_pandas()
    qvecs = np.stack([
        np.asarray(qp.iloc[i]["embedding"], dtype=np.float32) for i in range(len(qp))
    ])
    return qp, qs_full, qvecs


def run_method_measurement(
    method_name: str,
    all_vecs: np.ndarray,
    stratum_ids: np.ndarray,
    ds: dict,
    *,
    n_queries: int = 100,
    modes: tuple[str, ...] = ("equal",),
    cache_seed: int = 42,
) -> list[dict]:
    """주어진 stratum_ids 로 측정 (sel × seed × query). modes 중 'bernoulli' 포함 시 baseline 동시 측정.

    Args:
        method_name: 산출 row 의 'mode' 컬럼 값 (예: 'minibatch', 'random_proj', 'random20').
            'bernoulli' / 'km20' 등 baseline 도 같은 함수로 처리 가능.
        all_vecs: 전체 vectors (N, dim).
        stratum_ids: method-specific stratum_id (N,) int32.
        ds: DATASETS 항목.
        modes: ('equal',) 또는 ('bernoulli',) 또는 ('equal', 'bernoulli').
            method 자체는 보통 'equal' allocation. 'bernoulli' 는 BERN baseline 동시 산출용.

    Returns:
        list[dict] — parquet 행 (dataset/mode/selectivity/seed/query_id/D_target/true_card/est/q_error).
        'mode' 컬럼은 method_name 으로 채움. 단 'bernoulli' 모드는 항상 'bernoulli' 이름.
    """
    samples, sizes = cache_cluster_samples_inmem(all_vecs, stratum_ids, seed=cache_seed)
    print(
        f"[{kst()}]   stratum sizes (min/mean/max): "
        f"{min(sizes.values())} / {sum(sizes.values()) // N_STRATA} / {max(sizes.values())}"
    )
    qp, qs_full, qvecs = _load_query_pool(ds)
    print(f"[{kst()}]   loaded {len(qp)} queries (dim={qvecs.shape[1]})")

    rows: list[dict] = []
    for mode in modes:
        if mode == "bernoulli":
            alloc = None
            row_mode = "bernoulli"
        elif mode == "equal":
            alloc = equal_alloc()
            row_mode = method_name
        elif mode == "proportional":
            alloc = proportional_alloc(sizes)
            row_mode = method_name + "_prop"
        else:
            raise ValueError(f"unsupported mode: {mode}")

        t_mode = time.time()
        for sel in SELECTIVITIES:
            qs_sel = qs_full[
                (np.isclose(qs_full["selectivity"], sel)) &
                (qs_full["query_id"] < n_queries)
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
                        est = bernoulli_estimate(samples, sizes, qvec, D, rng)
                    else:
                        est = stratified_estimate(samples, sizes, alloc, qvec, D, rng)
                    if est > 0 and true_card > 0:
                        qerr = max(est / true_card, true_card / est)
                    else:
                        qerr = None
                    rows.append({
                        "dataset": ds["name"], "mode": row_mode, "selectivity": sel,
                        "seed": seed, "query_id": qid, "D_target": D,
                        "true_card": true_card, "est": est, "q_error": qerr,
                    })
                    qe_list.append(qerr if qerr is not None else float("nan"))
                elapsed = time.time() - t0
                valid = sum(1 for q in qe_list if q == q)
                med = float(np.nanmedian(qe_list)) if valid else float("nan")
                print(
                    f"[{kst()}]   {ds['name']} {row_mode:>15} s={sel:.2f} seed={seed} "
                    f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} med_qe={med:.4f}"
                )
        print(f"[{kst()}] {ds['name']} {row_mode:>15}: total {time.time() - t_mode:.1f}s")

    return rows


# ---------------------------------------------------------------------------
# 6. save_parquet_meta — 표준 산출
# ---------------------------------------------------------------------------

def save_parquet_meta(
    rows: list[dict], *, prefix: str, out_dir: Path = CACHE,
    extra_meta: dict | None = None,
) -> tuple[Path, Path]:
    df = pd.DataFrame(rows)
    out_pq = out_dir / f"{prefix}.parquet"
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = df.groupby(["dataset", "mode", "selectivity"])["q_error"].agg(
        ["mean", "std", "median", "count"]
    ).round(4)
    print(f"\n=== mean q_error per (dataset × mode × sel) ===\n{smry}")

    meta = {
        "kst": kst(),
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()),
        "datasets": sorted(df["dataset"].unique().tolist()),
    }
    if extra_meta:
        meta.update(extra_meta)
    out_meta = out_dir / f"{prefix}_meta.json"
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    return out_pq, out_meta


# ---------------------------------------------------------------------------
# 자체 테스트는 PG 의존 — 서버에서만 실행 가능. 로컬에선 import 만 검증.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[smoke] equal_alloc(20, 385):", equal_alloc())
    sizes = {0: 100000, 1: 50000, 2: 30000, **{i: 20000 for i in range(3, 20)}}
    print("[smoke] proportional_alloc:", proportional_alloc(sizes))
    print("\n✓ _measure_common.py importable + helpers work")
