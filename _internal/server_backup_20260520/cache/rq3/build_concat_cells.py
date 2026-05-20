#!/usr/bin/env python3
"""
multi-vector concat 측정 트랙 — NPY/parquet artifact 빌더.

목적
----
measure_paper_exact.py 는 측정 대상 cell 의 vector 를 PG 에서 가져오지 않고
``cache/rq1/{table}_vectors.npy`` + ``{table}_strata.npy`` 가 둘 다 있으면
NPY fast-path 로 읽는다 (_measure_common.fetch_all_vectors_safe).

그래서 concat 벡터 + KM20 strata + query artifact 를 미리 NPY/parquet 로 만들어
두면 measure_paper_exact.py 코드를 한 줄도 안 고치고 224d/288d/864d concat cell 을
측정할 수 있다. 이 스크립트가 그 artifact 를 만든다 — PG 는 전혀 안 건드린다.

빌드 대상 7 cell
----------------
DEEP+SIFT concat : sf1 / sf10 / sf100  → 224d (DEEP 96 + SIFT 128)
DEEP+WIKI concat : sf1 / sf10          → 864d (DEEP 96 + WIKI 768)
DEEP+YFCC concat : sf1 / sf10          → 288d (DEEP 96 + YFCC 192)

table 이름 (measure_paper_exact.py CellSpec.table 과 1:1):
    partsupp_deep_sift_concat_{sf}
    partsupp_deep_wiki_concat_{sf}
    partsupp_deep_yfcc_concat_{sf}

입력 (cache/rq1/ 에 이미 존재)
-------------------------------
partsupp_deep_{1,10,100}_vectors.npy + _pks.npy
partsupp_sift_{1,10,100}_vectors.npy + _pks.npy
partsupp_wiki_{1,10}_vectors.npy     + _pks.npy
partsupp_yfcc_{1,10}_vectors.npy     + _pks.npy
``_pks.npy`` 는 (N,2) int64 = (ps_partkey, ps_suppkey).

출력 (cell 당, cache/rq1/ 아래 — measure_paper_exact.py 가 보는 위치)
--------------------------------------------------------------------
partsupp_{combo}_concat_{sf}_vectors.npy           (N, dim) float32  concat 벡터
partsupp_{combo}_concat_{sf}_strata.npy            (N,)     int32    KM20 strata (원본 순서)
partsupp_{combo}_concat_{sf}_pks.npy               (N,2)    int64    (partkey, suppkey)
query_pool_{combo.upper()}_CONCAT_sf{sf}.parquet         query_id, embedding, q_pk
query_selectivity_{combo.upper()}_CONCAT_sf{sf}.parquet  query_id, selectivity, D_target,
                                                         true_cardinality, actual_sel
partsupp_{combo}_concat_{sf}_concat_meta.json      build meta (dim, n1/n2, missing 등)

query_pool / query_selectivity 의 컬럼 스키마는 기존
``query_pool_DEEP_sf{N}.parquet`` / ``query_selectivity_DEEP_sf{N}.parquet`` 와
완전히 동일 — measure_paper_exact.py 의 mc._load_query_pool() / qs_full lookup
( ``embedding`` / ``selectivity`` / ``D_target`` / ``true_cardinality`` ) 가 그대로 동작한다.

★ 측정 코드와 cell 을 연결하려면 measure_paper_exact.py 에 CellSpec 을 추가하고
  DATASET_ALIAS 에 매핑을 넣어야 한다 (이 스크립트는 artifact 만 만든다).
  예: dataset="DEEP+SIFT concat", table="partsupp_deep_sift_concat_1" → alias
  "DEEP_SIFT_CONCAT" → query_pool_DEEP_SIFT_CONCAT_sf1.parquet 를 읽도록.

CLI
---
    python3 build_concat_cells.py --cell deep_sift_1     # 1 cell
    python3 build_concat_cells.py --all                  # 7 cell 전부
    python3 build_concat_cells.py --dry-run              # 입력 점검 + 계획만

서버 경로: /mnt/hdd0/home/capstone2026/cache/rq3/build_concat_cells.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - 서버엔 pandas 있음
    raise RuntimeError("pandas 필요") from exc

try:
    from sklearn.cluster import MiniBatchKMeans
except ImportError:  # pragma: no cover
    MiniBatchKMeans = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# 경로
# ---------------------------------------------------------------------------

CACHE_RQ1 = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
CACHE_RQ3 = Path("/mnt/hdd0/home/capstone2026/cache/rq3")


# ---------------------------------------------------------------------------
# 상수 — 기존 query_pool_DEEP_sf{N} 과 lock-step
# ---------------------------------------------------------------------------

# 기존 query_selectivity_DEEP_sf{N}.parquet 의 selectivity 5종 + paper Fig 13 의
# 0.001 을 합쳐서 전부 생성 (measure_paper_exact.py 가 cell 마다 필요한 sel 만
# np.isclose 로 골라 씀 — A8 류 TPC-H cell 은 0.01, A4 류 ablation 은 0.001/0.01/0.10).
SELECTIVITIES: tuple[float, ...] = (0.001, 0.01, 0.05, 0.10, 0.30, 0.50)
N_STRATA: int = 20
N_QUERIES: int = 100               # ★ 기존 cell 의 query_pool 행 수와 동일 — 절대 바꾸지 말 것
SAMPLE_FOR_CALIB: int = 50_000     # D_target 분위수 보정용 sample
QUERY_SEED: int = 1234
KMEANS_FIT_SAMPLE: int = 100_000
KMEANS_SEED: int = 42
TRUE_CARD_CHUNK: int = 200_000     # true_cardinality 스트리밍 청크


def kst() -> str:
    """KST 타임스탬프 HH:MM:SS (프로젝트 규칙)."""
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# cell 레지스트리 — 7 concat cell
# ---------------------------------------------------------------------------
#
#   key       : CLI --cell 값
#   combo     : table 이름 prefix (partsupp_{combo}_concat_{sf})
#   src_a/b   : cache/rq1 NPY family (deep 가 항상 row spine)
#   dim_a/b   : 각 source 차원
#   align     : "direct" (pks 동일) | "broadcast" (partkey first-occurrence)
#   alias     : query_pool 파일명 alias (대문자) — measure_paper_exact.py 가 쓸 이름
#
CELLS: dict[str, dict] = {
    f"deep_sift_{sf}": {
        "combo": "deep_sift", "src_a": f"partsupp_deep_{sf}", "src_b": f"partsupp_sift_{sf}",
        "dim_a": 96, "dim_b": 128, "sf": sf, "align": "direct",
        "alias": "DEEP_SIFT_CONCAT",
    }
    for sf in (1, 10, 100)
} | {
    f"deep_wiki_{sf}": {
        "combo": "deep_wiki", "src_a": f"partsupp_deep_{sf}", "src_b": f"partsupp_wiki_{sf}",
        "dim_a": 96, "dim_b": 768, "sf": sf, "align": "broadcast",
        "alias": "DEEP_WIKI_CONCAT",
    }
    for sf in (1, 10)
} | {
    f"deep_yfcc_{sf}": {
        "combo": "deep_yfcc", "src_a": f"partsupp_deep_{sf}", "src_b": f"partsupp_yfcc_{sf}",
        "dim_a": 96, "dim_b": 192, "sf": sf, "align": "broadcast",
        "alias": "DEEP_YFCC_CONCAT",
    }
    for sf in (1, 10)
}

ALL_CELLS: list[str] = list(CELLS.keys())


# ---------------------------------------------------------------------------
# NPY 로더
# ---------------------------------------------------------------------------

def _load_source(name: str) -> tuple[np.ndarray, np.ndarray]:
    """cache/rq1/{name}_vectors.npy + _pks.npy 로드.

    Returns
    -------
    vec : (N, dim) float32
    pks : (N, 2)   int64    — (ps_partkey, ps_suppkey)
    """
    v_path = CACHE_RQ1 / f"{name}_vectors.npy"
    k_path = CACHE_RQ1 / f"{name}_pks.npy"
    if not v_path.exists() or not k_path.exists():
        raise FileNotFoundError(
            f"{name!r} NPY 소스 없음: {v_path} (exists={v_path.exists()}) / "
            f"{k_path} (exists={k_path.exists()})"
        )
    vec = np.load(v_path)
    pks = np.load(k_path)
    if pks.ndim == 1:
        # legacy 1-col → suppkey 0 으로 padding
        pks = np.stack([pks, np.zeros_like(pks)], axis=1)
    return vec, pks


def _sort_by_pks(vec: np.ndarray, pks: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(partkey, suppkey) lexsort — build_new_multi_cells._sort_by_pks 와 동일."""
    order = np.lexsort((pks[:, 1], pks[:, 0]))
    return vec[order], pks[order]


# ---------------------------------------------------------------------------
# row alignment — DEEP 를 spine 으로, B 를 정렬/broadcast
# ---------------------------------------------------------------------------

def align_sources(cell_cfg: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """source A(deep) / B 를 row 정렬해서 (vec_a, vec_b, pks_a, missing) 반환.

    - align="direct"   : pks 가 sort 후 동일 → 1:1 정렬 (DEEP+SIFT)
    - align="broadcast": pks 불일치 → DEEP 를 spine 으로, B 를 partkey
      first-occurrence 로 broadcast (build_new_multi_cells.build_4way_arrays 로직)

    vec_a / vec_b 는 row-for-row 정렬됨. pks_a 는 (N,2) — concat cell 의 pks.
    missing = B 쪽에 매칭 안 된 DEEP row 수 (broadcast 일 때만, direct 는 0).
    """
    src_a, src_b = cell_cfg["src_a"], cell_cfg["src_b"]
    vec_a, pks_a = _load_source(src_a)
    vec_b, pks_b = _load_source(src_b)
    vec_a, pks_a = _sort_by_pks(vec_a, pks_a)
    vec_b, pks_b = _sort_by_pks(vec_b, pks_b)
    print(f"[{kst()}]   src_a={src_a} {vec_a.shape}  src_b={src_b} {vec_b.shape}")

    if cell_cfg["align"] == "direct":
        # pks 가 완전히 동일해야 1:1 concat 가능 — 아니면 오류
        if pks_a.shape != pks_b.shape or not np.array_equal(pks_a, pks_b):
            raise RuntimeError(
                f"{src_a}/{src_b}: align=direct 인데 sort 후 pks 불일치 — "
                f"shape {pks_a.shape} vs {pks_b.shape}"
            )
        print(f"[{kst()}]   pks sort 후 동일 — direct 1:1 정렬")
        return (
            vec_a.astype(np.float32, copy=False),
            vec_b.astype(np.float32, copy=False),
            pks_a.astype(np.int64, copy=False),
            0,
        )

    # broadcast: B 를 partkey first-occurrence 로 펼침
    print(f"[{kst()}]   pks 불일치 — B 를 partkey first-occurrence broadcast")
    b_pk = pks_b[:, 0]
    uniq_pk, first_idx = np.unique(b_pk, return_index=True)
    # uniq_pk 는 정렬되어 있음 → searchsorted 로 O(N log U) broadcast
    a_pk = pks_a[:, 0]
    pos = np.searchsorted(uniq_pk, a_pk)
    pos_clip = np.clip(pos, 0, len(uniq_pk) - 1)
    matched = uniq_pk[pos_clip] == a_pk
    missing = int((~matched).sum())
    src_row = first_idx[np.where(matched, pos_clip, 0)]
    vec_b_bc = vec_b[src_row].astype(np.float32, copy=True)
    if missing:
        # 매칭 실패 row 는 0 벡터 (정상이면 발생 X)
        vec_b_bc[~matched] = 0.0
        print(f"[{kst()}]   WARNING: DEEP row {missing:,}개가 B 매칭 실패 — 0 벡터")
    else:
        print(f"[{kst()}]   broadcast missing=0 ✓ (전 DEEP row B 매칭)")
    return (
        vec_a.astype(np.float32, copy=False),
        vec_b_bc,
        pks_a.astype(np.int64, copy=False),
        missing,
    )


# ---------------------------------------------------------------------------
# concat — 각 emb 를 평균 norm 으로 정규화 후 이어붙임
# ---------------------------------------------------------------------------

def build_concat(emb_a: np.ndarray, emb_b: np.ndarray) -> tuple[np.ndarray, float, float]:
    """concat 벡터 + 정규화 상수 (n1, n2) 반환.

    build_new_multi_cells.build_concat 와 동일 — 각 emb 를 자기 평균 L2 norm 으로
    나눈 뒤 concatenate. n1/n2 를 meta 에 기록해서 재현 가능하게 한다.
    """
    n1 = float(np.linalg.norm(emb_a, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb_b, axis=1).mean()) or 1.0
    concat = np.concatenate([emb_a / n1, emb_b / n2], axis=1).astype(np.float32)
    return concat, n1, n2


# ---------------------------------------------------------------------------
# KM20 strata — concat 벡터에 MiniBatchKMeans
# ---------------------------------------------------------------------------

def km20_strata(concat: np.ndarray) -> np.ndarray:
    """concat 벡터에 KMeans K=20 (100K subsample fit) → 전체 predict.

    ★ 반환값은 원본(partkey) 순서 — fetch_all_vectors_safe 의 NPY fast-path 가
      strata 로 argsort 해서 cluster grouping 을 만들기 때문. 여기서 미리
      정렬하면 안 됨.
    """
    if MiniBatchKMeans is None:
        raise RuntimeError("scikit-learn (MiniBatchKMeans) 필요 — 서버에서 실행")
    rng = np.random.default_rng(KMEANS_SEED)
    n = concat.shape[0]
    if KMEANS_FIT_SAMPLE < n:
        idx = rng.choice(n, size=KMEANS_FIT_SAMPLE, replace=False)
        fit_data = concat[idx]
    else:
        fit_data = concat
    km = MiniBatchKMeans(
        n_clusters=N_STRATA, batch_size=1000, random_state=KMEANS_SEED, n_init=10,
    )
    km.fit(fit_data)
    return km.predict(concat).astype(np.int32)


# ---------------------------------------------------------------------------
# query artifact — concat 공간에서 단일-D query pool
# ---------------------------------------------------------------------------

def build_query_artifacts(
    concat: np.ndarray, pks: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """concat 공간에서 query pool + per-(query, sel) D_target/true_cardinality.

    스키마 (기존 query_pool_DEEP_sf{N} / query_selectivity_DEEP_sf{N} 와 동일)
    -----------------------------------------------------------------------
    query_pool        : query_id, embedding (concat 벡터 list), q_pk
    query_selectivity : query_id, selectivity, D_target, true_cardinality, actual_sel

    query_id 는 query_pool 의 행 index (0..N_QUERIES-1) 와 1:1 — measure_paper_exact.py
    가 ``q_row_idx = q_idx % len(qp)`` 후 ``query_id == q_row_idx`` 로 lookup 하므로
    query_pool 행 순서와 query_selectivity.query_id 가 반드시 일치해야 한다.

    D_target  = concat L2 거리의 sel 분위수 (50K calib sample 기준)
    true_card = 전체 N 중 (concat 거리 < D_target) 행 수 — 청크 스트리밍으로 계산
    """
    rng = np.random.default_rng(QUERY_SEED)
    n = concat.shape[0]

    qids = rng.choice(n, size=N_QUERIES, replace=False)
    q_vecs = concat[qids].copy()
    q_pks = pks[qids].copy()

    # 보정 subset — 거리 분포를 50K sample 에서 미리 계산
    calib_idx = rng.choice(n, size=min(SAMPLE_FOR_CALIB, n), replace=False)
    calib = concat[calib_idx]

    # per-(query, sel) D_target
    D_by_sel: dict[float, np.ndarray] = {}
    for sel in SELECTIVITIES:
        Dd = np.empty(N_QUERIES, dtype=np.float64)
        for i in range(N_QUERIES):
            d = np.linalg.norm(calib - q_vecs[i], axis=1)
            Dd[i] = float(np.quantile(d, sel))
        D_by_sel[sel] = Dd
        print(f"[{kst()}]     calib sel={sel:<5} D_target[mean={Dd.mean():.4f} "
              f"min={Dd.min():.4f} max={Dd.max():.4f}]")

    # true cardinality — 전체 N, 청크 스트리밍 (peak memory 제한)
    print(f"[{kst()}]     true_cardinality 계산 ({N_QUERIES}q × {len(SELECTIVITIES)}sel) on N={n:,}")
    true_card = np.zeros((N_QUERIES, len(SELECTIVITIES)), dtype=np.int64)
    t0 = time.time()
    for i in range(N_QUERIES):
        thr = np.array([D_by_sel[sel][i] for sel in SELECTIVITIES], dtype=np.float64)
        counts = np.zeros(len(SELECTIVITIES), dtype=np.int64)
        for j0 in range(0, n, TRUE_CARD_CHUNK):
            j1 = min(j0 + TRUE_CARD_CHUNK, n)
            d_block = np.linalg.norm(concat[j0:j1] - q_vecs[i], axis=1)
            for k in range(len(SELECTIVITIES)):
                counts[k] += int((d_block < thr[k]).sum())
        true_card[i] = counts
        if (i + 1) % 20 == 0:
            print(f"[{kst()}]       progress {i + 1}/{N_QUERIES} ({time.time() - t0:.0f}s)")
    print(f"[{kst()}]     true_cardinality 완료 {time.time() - t0:.1f}s")

    # ---- query_pool dataframe ----
    pool_rows = []
    for i in range(N_QUERIES):
        pool_rows.append({
            "query_id": int(i),
            "embedding": q_vecs[i].astype(np.float32).tolist(),
            "q_pk": [int(q_pks[i, 0]), int(q_pks[i, 1])],
        })
    qp = pd.DataFrame(pool_rows)

    # ---- query_selectivity dataframe ----
    sel_rows = []
    for i in range(N_QUERIES):
        for k, sel in enumerate(SELECTIVITIES):
            tc = int(true_card[i, k])
            sel_rows.append({
                "query_id": int(i),
                "selectivity": float(sel),
                "D_target": float(D_by_sel[sel][i]),
                "true_cardinality": tc,
                "actual_sel": float(tc) / float(n),
            })
    qs = pd.DataFrame(sel_rows)

    meta = {
        "n_queries": N_QUERIES,
        "n_rows": int(n),
        "selectivities": list(SELECTIVITIES),
        "calibration": "per-query D_target = quantile(concat L2 거리, sel)",
        "calib_sample_n": int(min(SAMPLE_FOR_CALIB, n)),
        "query_seed": QUERY_SEED,
        "true_card_chunk": TRUE_CARD_CHUNK,
    }
    return qp, qs, meta


# ---------------------------------------------------------------------------
# cell 당 출력 경로
# ---------------------------------------------------------------------------

def cell_output_paths(cell_cfg: dict) -> dict[str, Path]:
    combo, sf, alias = cell_cfg["combo"], cell_cfg["sf"], cell_cfg["alias"]
    base = f"partsupp_{combo}_concat_{sf}"
    return {
        # ★ vectors / strata / pks 는 cache/rq1 — measure_paper_exact.py fast-path 위치
        "vectors":   CACHE_RQ1 / f"{base}_vectors.npy",
        "strata":    CACHE_RQ1 / f"{base}_strata.npy",
        "pks":       CACHE_RQ1 / f"{base}_pks.npy",
        # query artifact 도 cache/rq1 — query_pool_{ALIAS}_sf{N} 규칙
        "query_pool": CACHE_RQ1 / f"query_pool_{alias}_sf{sf}.parquet",
        "query_sel":  CACHE_RQ1 / f"query_selectivity_{alias}_sf{sf}.parquet",
        # meta 는 cache/rq3 (artifact 빌드 로그 성격)
        "meta":       CACHE_RQ3 / f"{base}_concat_meta.json",
    }


def all_outputs_present(paths: dict[str, Path]) -> bool:
    return all(p.exists() for p in paths.values())


# ---------------------------------------------------------------------------
# cell 1개 빌드
# ---------------------------------------------------------------------------

def build_one_cell(cell_key: str, *, force: bool) -> dict:
    cfg = CELLS[cell_key]
    paths = cell_output_paths(cfg)
    if (not force) and all_outputs_present(paths):
        print(f"[{kst()}] SKIP {cell_key} — 모든 출력 이미 존재")
        return {"cell": cell_key, "status": "skipped"}

    print(f"[{kst()}] >>> concat 빌드: {cell_key} "
          f"(combo={cfg['combo']} sf={cfg['sf']} align={cfg['align']})")
    t_cell = time.time()

    # 1. source 로드 + row alignment
    vec_a, vec_b, pks, missing = align_sources(cfg)
    n = vec_a.shape[0]
    assert vec_a.shape[1] == cfg["dim_a"], f"dim_a {vec_a.shape[1]} != {cfg['dim_a']}"
    assert vec_b.shape[1] == cfg["dim_b"], f"dim_b {vec_b.shape[1]} != {cfg['dim_b']}"

    # 2. concat (정규화 후 이어붙임)
    concat, n1, n2 = build_concat(vec_a, vec_b)
    dim = concat.shape[1]
    expect_dim = cfg["dim_a"] + cfg["dim_b"]
    assert dim == expect_dim, f"concat dim {dim} != {expect_dim}"
    print(f"[{kst()}]   concat: N={n:,} dim={dim} (n1={n1:.4f} n2={n2:.4f}) "
          f"missing={missing} ({concat.nbytes / 1e9:.2f} GB)")
    del vec_a, vec_b

    # 3. 저장 — vectors / pks
    np.save(paths["vectors"], concat)
    np.save(paths["pks"], pks)
    print(f"[{kst()}]   saved {paths['vectors'].name}, {paths['pks'].name}")

    # 4. KM20 strata (concat 공간, 원본 순서로 저장)
    print(f"[{kst()}]   KM20 stratification (concat)")
    sids = km20_strata(concat)
    np.save(paths["strata"], sids)
    counts = np.bincount(sids, minlength=N_STRATA)
    print(f"[{kst()}]   strata: K_used={int((counts > 0).sum())}/{N_STRATA} "
          f"min={int(counts.min())} max={int(counts.max())} "
          f"mean={int(counts.mean())}")

    # 5. query artifact (concat 공간 단일-D)
    print(f"[{kst()}]   query pool + true_cardinality ({N_QUERIES} queries)")
    qp, qs, q_meta = build_query_artifacts(concat, pks)
    qp.to_parquet(paths["query_pool"], index=False)
    qs.to_parquet(paths["query_sel"], index=False)
    print(f"[{kst()}]   saved {paths['query_pool'].name} ({len(qp)} rows), "
          f"{paths['query_sel'].name} ({len(qs)} rows)")

    # 6. meta json
    elapsed = round(time.time() - t_cell, 1)
    meta = {
        "kst": kst(),
        "cell": cell_key,
        "combo": cfg["combo"],
        "sf": cfg["sf"],
        "table": f"partsupp_{cfg['combo']}_concat_{cfg['sf']}",
        "alias": cfg["alias"],
        "align": cfg["align"],
        "dim": dim,
        "dim_a": cfg["dim_a"],
        "dim_b": cfg["dim_b"],
        "src_a": cfg["src_a"],
        "src_b": cfg["src_b"],
        "n_rows": int(n),
        "norm_const_n1": n1,
        "norm_const_n2": n2,
        "missing_count": missing,
        "strata_K_used": int((counts > 0).sum()),
        "strata_min": int(counts.min()),
        "strata_max": int(counts.max()),
        "outputs": {k: str(v) for k, v in paths.items()},
        "elapsed_s": elapsed,
        "build_kst": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S"),
        **q_meta,
    }
    paths["meta"].parent.mkdir(parents=True, exist_ok=True)
    with open(paths["meta"], "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}]   saved {paths['meta'].name} (elapsed {elapsed}s)")
    return {"cell": cell_key, "status": "built", **meta}


# ---------------------------------------------------------------------------
# 자원 추정 (dry-run + 최종 보고)
# ---------------------------------------------------------------------------

def print_plan(cells: list[str]) -> None:
    print(f"\n[{kst()}] === 빌드 계획 ===")
    print(f"  {'cell':<16} {'table':<32} {'dim':>4} {'sf':>3} {'align':<10} {'~GB':>7}")
    for ck in cells:
        cfg = CELLS[ck]
        n = 800_000 if cfg["sf"] == 1 else (8_000_000 if cfg["sf"] == 10 else 80_000_000)
        dim = cfg["dim_a"] + cfg["dim_b"]
        gb = 4.0 * n * dim / 1024.0 ** 3
        tbl = f"partsupp_{cfg['combo']}_concat_{cfg['sf']}"
        print(f"  {ck:<16} {tbl:<32} {dim:>4} {cfg['sf']:>3} {cfg['align']:<10} {gb:>7.2f}")


def dry_run(cells: list[str]) -> None:
    print(f"\n[{kst()}] === dry-run: 입력 NPY 점검 ===")
    needed: set[str] = set()
    for ck in cells:
        cfg = CELLS[ck]
        needed.update({cfg["src_a"], cfg["src_b"]})
    ok = True
    for src in sorted(needed):
        v = CACHE_RQ1 / f"{src}_vectors.npy"
        k = CACHE_RQ1 / f"{src}_pks.npy"
        tv = "OK  " if v.exists() else "MISS"
        tk = "OK  " if k.exists() else "MISS"
        if not (v.exists() and k.exists()):
            ok = False
        print(f"  [{tv}] {v.name:<36}  [{tk}] {k.name}")

    print(f"\n[{kst()}] === 출력 파일 계획 ===")
    for ck in cells:
        cfg = CELLS[ck]
        paths = cell_output_paths(cfg)
        present = all_outputs_present(paths)
        print(f"  {ck} ({cfg['align']}, sf={cfg['sf']}): "
              f"{'OK (skip)' if present else 'NEEDS BUILD'}")
        for k, v in paths.items():
            tag = "exists" if v.exists() else "MISSING"
            print(f"      [{tag:>7}] {k:<11} -> {v}")
    print(f"\n[{kst()}] dry-run {'OK' if ok else 'FAIL — 입력 NPY 누락'}")
    if not ok:
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="multi-vector concat 측정 트랙 — NPY/parquet artifact 빌더.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cell", choices=ALL_CELLS, help="cell 1개 빌드 (예: deep_sift_1)")
    g.add_argument("--all", action="store_true", help="7 cell 전부 빌드")
    g.add_argument("--dry-run", action="store_true", help="입력 점검 + 계획만 (compute X)")
    ap.add_argument("--force", action="store_true", help="출력 존재해도 재빌드")
    args = ap.parse_args()

    cells = ALL_CELLS if (args.all or args.dry_run) else [args.cell]

    print(f"[{kst()}] === build_concat_cells ===")
    print(f"[{kst()}] CACHE_RQ1: {CACHE_RQ1}")
    print(f"[{kst()}] CACHE_RQ3: {CACHE_RQ3}")
    print(f"[{kst()}] cells ({len(cells)}): {cells}")
    print_plan(cells)

    if args.dry_run:
        dry_run(cells)
        return

    if MiniBatchKMeans is None:
        raise SystemExit("scikit-learn (MiniBatchKMeans) 필요 — 서버에서 실행")

    t_total = time.time()
    summary: list[dict] = []
    for ck in cells:
        try:
            res = build_one_cell(ck, force=args.force)
        except Exception as exc:  # pragma: no cover - 서버 런타임
            import traceback
            traceback.print_exc()
            summary.append({"cell": ck, "status": "error", "error": str(exc)})
            continue
        summary.append(res)

    print(f"\n[{kst()}] === 빌드 요약 ===")
    for s in summary:
        extra = ""
        if s.get("status") == "built":
            extra = (f"  dim={s['dim']} N={s['n_rows']:,} missing={s['missing_count']} "
                     f"K_used={s['strata_K_used']} ({s['elapsed_s']}s)")
        print(f"  {s['cell']:<16} {s.get('status'):<8}{extra}")
    n_built = sum(1 for s in summary if s.get("status") == "built")
    n_skip = sum(1 for s in summary if s.get("status") == "skipped")
    n_err = sum(1 for s in summary if s.get("status") == "error")
    print(f"[{kst()}] built={n_built} skipped={n_skip} error={n_err} "
          f"total {time.time() - t_total:.1f}s")
    if n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
