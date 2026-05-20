#!/usr/bin/env python3
"""
RQ3 #8 — F. MiniBatch K-means stratification.

기존 KM20 (full batch K-means, 사전 학습 시 ~30분, full pass) 의 distribution-agnostic
대안으로 sklearn MiniBatchKMeans 를 사용. 1% sample 만 보고 20-cluster centroid
근사 → 학습 ~수초. recovery_rate 75~95% 예측 (KM20 oracle 대비).

본 모듈은 stratum_id 부여 알고리즘만 제공. 측정 골격 (cluster sample 캐시 + HT
estimator) 은 rq2_alloc_python.py 그대로 사용.

Usage:
    from minibatch_kmeans import train_minibatch_kmeans, assign_minibatch
    model = train_minibatch_kmeans(sample_array, n_clusters=20, random_state=42)
    stratum_ids = assign_minibatch(model, full_vectors)
"""
from __future__ import annotations

import numpy as np
from sklearn.cluster import MiniBatchKMeans

DEFAULT_K = 20
DEFAULT_BATCH = 1024
DEFAULT_SEED = 42
DEFAULT_N_INIT = 3


def train_minibatch_kmeans(
    samples: np.ndarray,
    n_clusters: int = DEFAULT_K,
    random_state: int = DEFAULT_SEED,
    batch_size: int = DEFAULT_BATCH,
    n_init: int = DEFAULT_N_INIT,
    max_iter: int = 100,
) -> MiniBatchKMeans:
    """1% sample 로 MiniBatchKMeans 학습.

    samples: (N, dim) float array — DEEP/SIFT 의 1% subsample
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[0] < n_clusters:
        raise ValueError(f"need >= {n_clusters} samples, got {samples.shape[0]}")
    model = MiniBatchKMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        batch_size=batch_size,
        n_init=n_init,
        max_iter=max_iter,
    )
    model.fit(samples)
    return model


def assign_minibatch(model: MiniBatchKMeans, vectors: np.ndarray) -> np.ndarray:
    """vectors → stratum_id (0~K-1) 부여. 반환 shape: (N,) int32."""
    if vectors.ndim != 2:
        raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
    return model.predict(vectors).astype(np.int32)


def export_centroids(model: MiniBatchKMeans) -> np.ndarray:
    """학습한 centroid 반환. 측정 외 발표/figure 용도. shape: (K, dim) float32."""
    return model.cluster_centers_.astype(np.float32)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    """stratum 분포 균질성 sanity check. KM20 oracle 과 비교 시 사용."""
    counts = np.bincount(stratum_ids, minlength=n_clusters)
    return {
        "min": int(counts.min()),
        "max": int(counts.max()),
        "mean": float(counts.mean()),
        "std": float(counts.std()),
        "max_min_ratio": float(counts.max() / max(counts.min(), 1)),
        "counts": counts.tolist(),
    }


def _self_test():
    """toy 검증 — 3-cluster Gaussian mixture 에서 cluster 분리 확인."""
    rng = np.random.default_rng(0)
    centers = np.array([[0, 0], [10, 10], [20, 0]], dtype=np.float32)
    samples = np.vstack([
        rng.standard_normal((300, 2)).astype(np.float32) + c for c in centers
    ])
    model = train_minibatch_kmeans(samples, n_clusters=3, random_state=42)
    sids = assign_minibatch(model, samples)
    summary = cluster_size_summary(sids, n_clusters=3)
    print(f"[self-test] cluster sizes: {summary['counts']} (min={summary['min']}, max={summary['max']})")
    print(f"[self-test] centroids:\n{export_centroids(model)}")
    assert summary["min"] >= 200, "MiniBatchKMeans should find 3 well-separated clusters"
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
