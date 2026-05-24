#!/usr/bin/env python3
"""
RQ3 Multi-cell ALL-method supplement — 잔존 20 method × 3 multi cell 측정.

기존 4kang (Hilbert/Hybrid/MB_partial/HDBSCAN) + Wave1 (Halton/Hammersley/Reservoir) 가
각자 별도 script 로 진행 중. 본 wrapper 는 그 외의 모든 stratification-based method 를
multi-vector 패턴 (concat([emb1, emb2]) 입력) 으로 측정.

대상 cell:
  - deep_sift_10:           partsupp_deep_sift_10 (4way)        → measure_multi_vector pattern
  - deep_wiki_10:           partsupp_deep_wiki_10 (4way)        → measure_multi_vector pattern
  - multi_join_deep_wiki:   partsupp_deep_10 ⨝ part_wiki_10     → measure_multi_table_join pattern

처리 가능 method (20개; mapper.fit + assign 패턴):
  base 10:  minibatch, kdtree, zorder, pca1d, gmm, lsh, pq, sobol, random_proj, sparse_rp
  slow 2:   birch, spectral
  new8 8:   dbscan, optics, agglomerative, hierarchical_kmeans, faiss_ivf,
            pca_kmeans, kmeans_pp, coresets

처리 불가 method (3; query-time online weighting — measure_strategy 와 incompatible):
  distance_shell, importance_sampling, kde_pilot
  → 별도 multi-cell port 가 필요. 본 script 범위 외.

전략:
  1. Stratification 단계: concat([emb1, emb2]) (norm-aware) 로 single-vector 화
  2. method 별 fit_xxx(learn_samples, n_strata=20) + assign_xxx(mapper, full_vectors)
  3. NEW8 method 들은 in-line _fit_NEW8(method, samples) 로 처리 (run_xxx.py 의 fit 로직 정확 재현)
  4. measure_strategy / measure_strategy_join 호출 (Bernoulli 비교 X — already in 4way baseline)

Usage:
    python3 measure_multi_all.py --cell deep_sift_10 --method minibatch
    python3 measure_multi_all.py --cell deep_wiki_10 --method optics
    python3 measure_multi_all.py --cell multi_join_deep_wiki --method dbscan

산출:
    {CACHE}/rq3_multi_all_{cell}_{method}.parquet
    {CACHE}/rq3_multi_all_{cell}_{method}_meta.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
sys.path.insert(0, str(ROOT))

# import existing helpers
from measure_multi_vector import (  # noqa: E402
    CACHE, SEEDS, SELECTIVITIES, SAMPLE_SIZE, N_STRATA, N_QUERIES,
    fetch_dual_vectors, build_query_pool, measure_strategy, kst,
)


# ---------------------------------------------------------------------------
# Cell config (wave1 와 동일)
# ---------------------------------------------------------------------------

CELL_4WAY = {
    "deep_sift_10": {
        "table": "partsupp_deep_sift_10",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_sift", "emb2_dim": 128,
        "kind": "4way",
    },
    "deep_wiki_10": {
        "table": "partsupp_deep_wiki_10",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_wiki", "emb2_dim": 768,
        "kind": "4way",
    },
}

CELL_JOIN = {
    "multi_join_deep_wiki": {
        "partsupp_table": "partsupp_deep_10",
        "part_table": "part_wiki_10",
        "partsupp_emb_col": "ps_embedding", "partsupp_emb_dim": 96,
        "part_emb_col": "p_embedding", "part_emb_dim": 768,
        "kind": "join",
    },
}


# ---------------------------------------------------------------------------
# 처리 가능 method 목록
# ---------------------------------------------------------------------------

BASE_METHODS = [
    "minibatch", "kdtree", "zorder", "pca1d", "gmm", "lsh", "pq",
    "sobol", "random_proj", "sparse_rp",
]
SLOW_METHODS = ["birch", "spectral"]
NEW8_METHODS = [
    "dbscan", "optics", "agglomerative", "hierarchical_kmeans",
    "faiss_ivf", "pca_kmeans", "kmeans_pp", "coresets",
]
ALL_METHODS = BASE_METHODS + SLOW_METHODS + NEW8_METHODS


# ---------------------------------------------------------------------------
# Concat 입력 (4kang/wave1 와 동일 norm-aware)
# ---------------------------------------------------------------------------

def build_concat(emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    e1 = emb1 / n1
    e2 = emb2 / n2
    return np.concatenate([e1, e2], axis=1).astype(np.float32)


# ---------------------------------------------------------------------------
# Stratification per method
# ---------------------------------------------------------------------------

def _learn_subsample(vectors: np.ndarray, frac: float, seed: int,
                      min_samples: int = N_STRATA * 50) -> np.ndarray:
    """학습용 서브샘플 추출. n_strata*50 = 1000 row 미만이면 전체 사용."""
    n = vectors.shape[0]
    n_learn = max(int(n * frac), min_samples)
    n_learn = min(n_learn, n)
    rng = np.random.default_rng(seed)
    if n_learn < n:
        idx = rng.choice(n, size=n_learn, replace=False)
        return vectors[idx]
    return vectors


def stratify_method(method: str, vectors: np.ndarray,
                     learn_frac: float = 0.01, seed: int = 42) -> np.ndarray:
    """concat vector 에 method 별 stratification 적용. sids (N,) int32 반환."""
    n_strata = N_STRATA
    learn = _learn_subsample(vectors, learn_frac, seed)
    print(f"[{kst()}]   strat: {method} on {learn.shape[0]:,}/{vectors.shape[0]:,} "
          f"learn samples (dim={vectors.shape[1]})")
    t0 = time.time()

    # ---- BASE 10 ---------------------------------------------------------
    if method == "minibatch":
        from offline_simple.minibatch_kmeans import (
            train_minibatch_kmeans, assign_minibatch,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            model = train_minibatch_kmeans(
                learn, n_clusters=n_strata, batch_size=1000, random_state=seed,
            )
        sids = assign_minibatch(model, vectors)

    elif method == "kdtree":
        from kdtree.kdtree_partition import (
            fit_kdtree_partition, assign_kdtree,
        )
        mapper = fit_kdtree_partition(learn, n_strata=n_strata, seed=seed)
        sids = assign_kdtree(mapper, vectors)

    elif method == "zorder":
        from zorder.zorder_curve import (
            fit_zorder_mapper, assign_zorder,
        )
        mapper = fit_zorder_mapper(learn, n_strata=n_strata, p=10, seed=seed)
        sids = assign_zorder(mapper, vectors)

    elif method == "pca1d":
        from pca1d.pca1d_quantile import (
            fit_pca1d_mapper, assign_pca1d,
        )
        mapper = fit_pca1d_mapper(learn, n_strata=n_strata, seed=seed)
        sids = assign_pca1d(mapper, vectors)

    elif method == "gmm":
        from gmm.gmm_partition import fit_gmm, assign_gmm
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mapper = fit_gmm(learn, n_strata=n_strata, seed=seed)
        sids = assign_gmm(mapper, vectors)

    elif method == "lsh":
        from lsh.lsh import make_hyperplanes, assign_lsh
        W = make_hyperplanes(dim=vectors.shape[1], k=n_strata, seed=seed)
        sids = assign_lsh(W, vectors, k=n_strata)

    elif method == "pq":
        from pq.product_quantization import (
            fit_pq_mapper, assign_pq,
        )
        mapper = fit_pq_mapper(learn, n_strata=n_strata, seed=seed)
        sids = assign_pq(mapper, vectors)

    elif method == "sobol":
        from sobol.sobol_stratification import fit_sobol, assign_sobol
        mapper = fit_sobol(learn, n_strata=n_strata, seed=seed)
        sids = assign_sobol(mapper, vectors)

    elif method == "random_proj":
        from offline_simple.random_projection import (
            make_projection, assign_random_projection,
        )
        matrix = make_projection(dim=vectors.shape[1], k=n_strata, seed=seed)
        sids = assign_random_projection(matrix, vectors)

    elif method == "sparse_rp":
        from sparserp.sparse_random_projection import (
            fit_sparse_rp, assign_sparse_rp,
        )
        matrix = fit_sparse_rp(vectors.shape[1], n_strata=n_strata, seed=seed)
        sids = assign_sparse_rp(matrix, vectors, k=n_strata)

    # ---- SLOW 2 (subset training default; multi 10M-row 라 충분 빠름) ----
    elif method == "birch":
        from birch.birch_partition import fit_birch, assign_birch
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mapper = fit_birch(learn, n_strata=n_strata, seed=seed)
        sids = assign_birch(mapper, vectors)

    elif method == "spectral":
        from spectral.spectral_clustering import (
            fit_spectral, assign_spectral,
        )
        # spectral 은 fit_spectral 자체가 매우 비쌈 (full O(n^2)). subset 권장.
        sub_n = min(20000, learn.shape[0])
        sub_idx = np.random.default_rng(seed).choice(learn.shape[0], sub_n, replace=False)
        sub = learn[sub_idx] if sub_n < learn.shape[0] else learn
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mapper = fit_spectral(sub, n_strata=n_strata, seed=seed)
        sids = assign_spectral(mapper, vectors)

    # ---- NEW8 (in-line fit; sklearn-based) -------------------------------
    elif method in ("dbscan", "optics", "agglomerative"):
        sids = _fit_density_or_agglom(method, learn, vectors, n_strata, seed)

    elif method == "hierarchical_kmeans":
        sids = _fit_hierarchical_kmeans(learn, vectors, n_strata, seed)

    elif method == "faiss_ivf":
        sids = _fit_faiss_ivf(learn, vectors, n_strata, seed)

    elif method == "pca_kmeans":
        sids = _fit_pca_kmeans(learn, vectors, n_strata, seed)

    elif method == "kmeans_pp":
        sids = _fit_kmeans_pp(learn, vectors, n_strata, seed)

    elif method == "coresets":
        sids = _fit_coresets(learn, vectors, n_strata, seed)

    else:
        raise ValueError(f"unsupported method: {method}")

    sids = sids.astype(np.int32)
    elapsed = time.time() - t0
    counts = np.bincount(sids, minlength=n_strata)
    nz = counts[counts > 0]
    print(f"[{kst()}]   strat done {elapsed:.1f}s — sizes "
          f"min={int(nz.min()) if len(nz) else 0} "
          f"max={int(counts.max())} K_used={(counts > 0).sum()}/{n_strata}")
    return sids


# ---------------------------------------------------------------------------
# NEW8 in-line fit helpers (run_*.py 의 핵심 로직 재현)
# ---------------------------------------------------------------------------

def _assign_nearest_centroid(
    all_vecs: np.ndarray, centroids: np.ndarray, chunk: int = 50000,
) -> np.ndarray:
    """centroid 에 nearest argmin (run_dbscan/optics/agglomerative 와 동일)."""
    n = len(all_vecs)
    out = np.empty(n, dtype=np.int32)
    cs = (centroids ** 2).sum(axis=1)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = all_vecs[i:j]
        ds = (block ** 2).sum(axis=1, keepdims=True) + cs[None, :] - 2.0 * block @ centroids.T
        out[i:j] = np.argmin(ds, axis=1).astype(np.int32)
    return out


def _fit_density_or_agglom(method: str, learn: np.ndarray, vectors: np.ndarray,
                            n_strata: int, seed: int) -> np.ndarray:
    """dbscan / optics / agglomerative — fit on subset, propagate by nearest centroid."""
    sub_n = min(50000, learn.shape[0])
    rng = np.random.default_rng(seed)
    if sub_n < learn.shape[0]:
        sub_idx = rng.choice(learn.shape[0], size=sub_n, replace=False)
        sub = learn[sub_idx]
    else:
        sub = learn

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if method == "dbscan":
            from sklearn.cluster import DBSCAN
            from sklearn.neighbors import NearestNeighbors
            # knee-eps via 5-NN
            k = 5
            nn = NearestNeighbors(n_neighbors=k).fit(sub)
            kth = np.sort(nn.kneighbors(sub)[0][:, -1])
            x = np.arange(len(kth), dtype=np.float64)
            y = kth.astype(np.float64)
            x0, y0, x1, y1 = x[0], y[0], x[-1], y[-1]
            denom = max(np.hypot(x1 - x0, y1 - y0), 1e-12)
            d = np.abs((y1 - y0) * x - (x1 - x0) * y + x1 * y0 - y1 * x0) / denom
            eps = float(kth[int(np.argmax(d))])
            labels = DBSCAN(eps=eps, min_samples=k).fit_predict(sub)

        elif method == "optics":
            from sklearn.cluster import OPTICS
            labels = OPTICS(min_samples=20, n_jobs=-1).fit_predict(sub)

        else:  # agglomerative
            from sklearn.cluster import AgglomerativeClustering
            ac = AgglomerativeClustering(
                n_clusters=n_strata, linkage="ward",
            ).fit(sub)
            labels = ac.labels_

    # 각 cluster 의 평균 → centroid; 너무 많은 노이즈는 -1 → 최근접 cluster 로
    valid = labels >= 0
    if not valid.any():
        # fallback: random partition
        return rng.integers(0, n_strata, size=vectors.shape[0]).astype(np.int32)

    unique, counts = np.unique(labels[valid], return_counts=True)
    # 너무 많거나 너무 적은 cluster 는 top-K 선택
    if len(unique) > n_strata:
        top_idx = np.argsort(-counts)[:n_strata]
        keep = unique[top_idx]
        keep_set = set(keep.tolist())
        # remap labels: keep 만 유효, 나머지는 -1
        labels = np.where(np.isin(labels, list(keep_set)), labels, -1)
        unique = keep
    centroids = np.stack([sub[labels == u].mean(axis=0) for u in unique]).astype(np.float32)
    # remap labels: 0..len(unique)-1
    label_map = {u: i for i, u in enumerate(unique)}
    # vectors -> nearest centroid
    sids = _assign_nearest_centroid(vectors, centroids)
    return sids


def _fit_hierarchical_kmeans(learn, vectors, n_strata, seed):
    """outer 4 × inner 5 = 20 leaf strata."""
    from sklearn.cluster import MiniBatchKMeans
    n_outer = 4
    n_inner = 5
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        outer = MiniBatchKMeans(
            n_clusters=n_outer, batch_size=1000, random_state=seed, n_init=3,
        ).fit(learn)
        outer_labels = outer.predict(vectors)
        inner_labels = np.zeros_like(outer_labels)
        for o in range(n_outer):
            mask_l = outer.labels_ == o
            sub_l = learn[mask_l]
            if len(sub_l) < n_inner * 5:
                # fallback: 0
                inner_labels[outer_labels == o] = 0
                continue
            inner = MiniBatchKMeans(
                n_clusters=n_inner, batch_size=500, random_state=seed + o, n_init=3,
            ).fit(sub_l)
            mask_v = outer_labels == o
            if mask_v.any():
                inner_labels[mask_v] = inner.predict(vectors[mask_v])
        sids = (outer_labels * n_inner + inner_labels).astype(np.int32)
    return sids


def _fit_faiss_ivf(learn, vectors, n_strata, seed):
    """faiss IVF — n_strata 개 centroid, IVF assignment."""
    try:
        import faiss
    except ImportError:
        # fallback: MiniBatchKMeans
        from sklearn.cluster import MiniBatchKMeans
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            m = MiniBatchKMeans(n_clusters=n_strata, batch_size=1000, random_state=seed).fit(learn)
        return m.predict(vectors).astype(np.int32)
    d = vectors.shape[1]
    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFFlat(quantizer, d, n_strata)
    index.train(np.ascontiguousarray(learn.astype(np.float32)))
    # IVF 의 nprobe=1 → top-1 cluster id
    quant_index = index.quantizer
    _, I = quant_index.search(np.ascontiguousarray(vectors.astype(np.float32)), 1)
    return I[:, 0].astype(np.int32)


def _fit_pca_kmeans(learn, vectors, n_strata, seed):
    """PCA reduce to dim/4 (cap 32) → MiniBatchKMeans."""
    from sklearn.decomposition import PCA
    from sklearn.cluster import MiniBatchKMeans
    target_dim = min(32, max(2, vectors.shape[1] // 4))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pca = PCA(n_components=target_dim, random_state=seed).fit(learn)
        learn_p = pca.transform(learn)
        vec_p = pca.transform(vectors).astype(np.float32)
        m = MiniBatchKMeans(
            n_clusters=n_strata, batch_size=1000, random_state=seed,
        ).fit(learn_p)
    return m.predict(vec_p).astype(np.int32)


def _fit_kmeans_pp(learn, vectors, n_strata, seed):
    """Lloyd's KMeans with k-means++ init (sklearn KMeans default)."""
    from sklearn.cluster import KMeans
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = KMeans(
            n_clusters=n_strata, init="k-means++", n_init=3, random_state=seed,
        ).fit(learn)
    return m.predict(vectors).astype(np.int32)


def _fit_coresets(learn, vectors, n_strata, seed):
    """Coreset (D2-sampling) + KMeans on coreset."""
    from sklearn.cluster import MiniBatchKMeans
    rng = np.random.default_rng(seed)
    coreset_n = min(2000, learn.shape[0])
    # D2-sampling: sequential weighted by distance to nearest already-picked
    if coreset_n >= learn.shape[0]:
        coreset = learn
    else:
        first = rng.integers(0, learn.shape[0])
        picked = [first]
        d2 = np.linalg.norm(learn - learn[first], axis=1) ** 2
        for _ in range(coreset_n - 1):
            p = d2 / max(d2.sum(), 1e-12)
            idx = rng.choice(learn.shape[0], p=p)
            picked.append(idx)
            new_d = np.linalg.norm(learn - learn[idx], axis=1) ** 2
            d2 = np.minimum(d2, new_d)
        coreset = learn[np.asarray(picked)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        m = MiniBatchKMeans(
            n_clusters=n_strata, batch_size=500, random_state=seed,
        ).fit(coreset)
    return m.predict(vectors).astype(np.int32)


# ---------------------------------------------------------------------------
# 4way cell measurement
# ---------------------------------------------------------------------------

def measure_4way(cell_name: str, method: str, n_queries: int = 100):
    cfg = CELL_4WAY[cell_name]
    table = cfg["table"]
    print(f"[{kst()}] === multi-all 4way: cell={cell_name} method={method} ===")

    emb1, emb2 = fetch_dual_vectors(
        table, cfg["emb1_col"], cfg["emb2_col"],
        cfg["emb1_dim"], cfg["emb2_dim"],
    )
    N = emb1.shape[0]
    print(f"[{kst()}] N={N:,} dims=({emb1.shape[1]}, {emb2.shape[1]})")

    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool(
        emb1, emb2, n_queries=n_queries,
    )

    concat = build_concat(emb1, emb2)
    print(f"[{kst()}]   concat shape={concat.shape}")
    sids = stratify_method(method, concat)

    rows = measure_strategy(
        method, sids, emb1, emb2, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, table, also_bernoulli=False,
    )
    return rows, table


# ---------------------------------------------------------------------------
# multi_join cell measurement
# ---------------------------------------------------------------------------

def measure_join(cell_name: str, method: str, n_queries: int = 100):
    cfg = CELL_JOIN[cell_name]
    print(f"[{kst()}] === multi-all join: cell={cell_name} method={method} ===")

    ps_table = cfg["partsupp_table"]
    cache_v = CACHE / f"{ps_table}_vectors.npy"
    cache_k = CACHE / f"{ps_table}_partkeys.npy"
    if not (cache_v.exists() and cache_k.exists()):
        raise FileNotFoundError(
            f"{ps_table} NPY cache not found — run measure_multi_table_join first"
        )
    t0 = time.time()
    ps_vecs = np.load(cache_v)
    ps_partkeys = np.load(cache_k)
    print(f"[{kst()}]   loaded partsupp NPY: vecs {ps_vecs.shape} "
          f"keys {ps_partkeys.shape} in {time.time()-t0:.1f}s")

    part_table = cfg["part_table"]
    part_v = CACHE / f"{part_table}_vectors.npy"
    part_k = CACHE / f"{part_table}_partkeys.npy"
    if not (part_v.exists() and part_k.exists()):
        raise FileNotFoundError(f"{part_table} NPY cache not found")
    t0 = time.time()
    part_vecs_raw = np.load(part_v)
    part_keys_raw = np.load(part_k)
    print(f"[{kst()}]   loaded part NPY: vecs {part_vecs_raw.shape} "
          f"keys {part_keys_raw.shape} in {time.time()-t0:.1f}s")

    # FK lookup
    t0 = time.time()
    sort_idx = np.argsort(part_keys_raw)
    part_keys_sorted = part_keys_raw[sort_idx]
    part_vecs_sorted = part_vecs_raw[sort_idx]
    pos = np.searchsorted(part_keys_sorted, ps_partkeys)
    bound = np.minimum(pos, len(part_keys_sorted) - 1)
    if (pos >= len(part_keys_sorted)).any() or \
       (part_keys_sorted[bound] != ps_partkeys).any():
        miss = (part_keys_sorted[bound] != ps_partkeys).sum()
        raise RuntimeError(f"FK lookup mismatch: {miss} rows")
    wiki_vecs = part_vecs_sorted[pos]
    print(f"[{kst()}]   FK broadcast: wiki_vecs {wiki_vecs.shape} "
          f"in {time.time()-t0:.1f}s")
    del part_vecs_raw, part_keys_raw, part_vecs_sorted, part_keys_sorted

    table_name = f"{ps_table}__{part_table}"
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool(
        ps_vecs, wiki_vecs, n_queries=n_queries,
    )

    concat = build_concat(ps_vecs, wiki_vecs)
    sids = stratify_method(method, concat)

    rows = measure_strategy(
        method, sids, ps_vecs, wiki_vecs, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, table_name, also_bernoulli=False,
    )
    # rename column for join consistency (wave1 와 동일 패턴)
    for r in rows:
        if "D1_target" in r:
            r["D_deep_target"] = r.pop("D1_target")
        if "D2_target" in r:
            r["D_wiki_target"] = r.pop("D2_target")
        if "table" in r:
            r["table_pair"] = r.pop("table")
    return rows, table_name


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", required=True,
                    choices=list(CELL_4WAY.keys()) + list(CELL_JOIN.keys()))
    ap.add_argument("--method", required=True, choices=ALL_METHODS)
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    ap.add_argument("--out-dir", default=str(CACHE))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_pq = out_dir / f"rq3_multi_all_{args.cell}_{args.method}.parquet"
    out_meta = out_dir / f"rq3_multi_all_{args.cell}_{args.method}_meta.json"

    if out_pq.exists():
        print(f"[{kst()}] SKIP — {out_pq.name} already exists")
        return

    t_start = time.time()
    if args.cell in CELL_4WAY:
        rows, table_name = measure_4way(args.cell, args.method, args.n_queries)
        kind = "4way"
    else:
        rows, table_name = measure_join(args.cell, args.method, args.n_queries)
        kind = "join"

    df = pd.DataFrame(rows)
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = (df.groupby(["dataset", "mode", "selectivity"])["q_error"]
              .agg(["mean", "std", "median", "count"]).round(4))
    print(f"\n=== q_error summary ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "cell": args.cell, "method": args.method, "kind": kind,
        "table_or_pair": table_name,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "n_queries": args.n_queries,
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()) if len(df) else [],
        "stratify_basis": "concat([emb1, emb2]) norm-aware + method fit/assign",
        "elapsed_s": round(time.time() - t_start, 1),
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] === done in {meta['elapsed_s']}s ===")


if __name__ == "__main__":
    main()
