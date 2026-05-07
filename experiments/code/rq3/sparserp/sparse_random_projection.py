#!/usr/bin/env python3
"""
RQ3 #20 — Sparse Random Projection (Achlioptas 2003) stratification.

Random Projection 의 sparse variant — entry 가 {-√3, 0, +√3} 의 sparse matrix.
Dense Gaussian RP 대비 ~3× faster, 메모리 1/3.

본 연구의 RQ3 Random Projection (#5) 은 dense gaussian. 본 method 는 sparse 변형 ablation.
"""
from __future__ import annotations

import numpy as np
from sklearn.random_projection import SparseRandomProjection

DEFAULT_K = 20
DEFAULT_SEED = 42


def fit_sparse_rp(samples_or_dim, n_strata: int = DEFAULT_K, seed: int = DEFAULT_SEED,
                   **_kwargs):
    """Sparse RP matrix 생성. fit 자체는 학습 X (matrix random gen)."""
    if isinstance(samples_or_dim, np.ndarray):
        dim = samples_or_dim.shape[1]
    else:
        dim = int(samples_or_dim)
    rng = np.random.default_rng(seed)
    # sklearn SparseRandomProjection 의 n_components 가 ceil(log(K)) 정도가 적절하나,
    # 본 연구는 K=20 stratum 에 맞게 1D projection + N_STRATA bin 사용
    # sparse random projection matrix (dim → 1)
    density = 1.0 / np.sqrt(dim)  # Achlioptas density
    p_nz = density
    s = 1.0 / np.sqrt(p_nz)
    # entries: ±s with prob p_nz/2 each, 0 otherwise
    matrix = rng.choice([-s, 0, s], size=dim,
                         p=[p_nz / 2, 1 - p_nz, p_nz / 2]).astype(np.float32)
    return matrix


def assign_sparse_rp(matrix: np.ndarray, vectors: np.ndarray, k: int = DEFAULT_K) -> np.ndarray:
    if vectors.ndim != 2:
        raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
    proj = vectors @ matrix
    # quantile bin
    quantiles = np.quantile(proj, np.linspace(0, 1, k + 1))
    edges = quantiles[1:-1]
    sids = np.searchsorted(edges, proj, side='right')
    return np.clip(sids, 0, k - 1).astype(np.int32)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    counts = np.bincount(stratum_ids, minlength=n_clusters)
    return {"min": int(counts.min()), "max": int(counts.max()),
            "max_min_ratio": float(counts.max() / max(counts.min(), 1))}


def _self_test():
    rng = np.random.default_rng(0)
    samples = rng.standard_normal((1000, 96)).astype(np.float32)
    matrix = fit_sparse_rp(samples, n_strata=20, seed=42)
    sids = assign_sparse_rp(matrix, samples, k=20)
    summary = cluster_size_summary(sids)
    print(f"[self-test] Sparse RP iid 96d: max/min={summary['max_min_ratio']:.2f}")
    assert sids.min() >= 0 and sids.max() < 20
    # SIFT 128d
    sift = rng.standard_normal((500, 128)).astype(np.float32)
    matrix_s = fit_sparse_rp(sift, n_strata=20, seed=42)
    sids_s = assign_sparse_rp(matrix_s, sift, k=20)
    print(f"[self-test] Sparse RP SIFT 128d: max/min={cluster_size_summary(sids_s)['max_min_ratio']:.2f}")
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
