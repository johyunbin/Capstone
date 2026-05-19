#!/usr/bin/env python3
"""
RQ3 #17 — HDBSCAN partition (density-based hierarchical clustering).

HDBSCAN (Hierarchical DBSCAN) — sklearn 0.24+ 의 density-based clustering.
KMeans/MiniBatch 와 직교적: cluster 수 자동 결정 (min_cluster_size 기반), noise 분류 가능.

특이점:
- HDBSCAN 은 cluster 수가 N_STRATA (20) 와 다를 수 있음 → label 재할당 필요.
- Noise (label=-1) 는 별도 처리 (가장 가까운 cluster 또는 별도 stratum).

본 구현은 단순화 — HDBSCAN cluster 수가 N_STRATA 보다 많으면 KMeans on centroid 로 합침,
적으면 추가 random split.

가설 H3-HD: 자연 cluster 수가 K=20 과 다른 데이터에서 HDBSCAN 이 KMeans 와 다른 결과.
SIFT (skewed, cluster 더 명확) 에서 우위 가능성.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from sklearn.cluster import HDBSCAN, KMeans

DEFAULT_K = 20
DEFAULT_MIN_CLUSTER_SIZE = 50
DEFAULT_SEED = 42


@dataclass
class HDBSCANMapper:
    cluster_centroids: np.ndarray   # (n_strata, dim)
    n_strata: int

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        # nearest centroid
        n = len(vectors)
        chunk = 50000
        sids = np.zeros(n, dtype=np.int32)
        for start in range(0, n, chunk):
            end = min(start + chunk, n)
            sub = vectors[start:end]
            xc = sub @ self.cluster_centroids.T
            xx = (sub * sub).sum(axis=1, keepdims=True)
            cc = (self.cluster_centroids * self.cluster_centroids).sum(axis=1)
            dists = xx - 2 * xc + cc
            sids[start:end] = np.argmin(dists, axis=1).astype(np.int32)
        return sids


def fit_hdbscan(samples: np.ndarray, n_strata: int = DEFAULT_K,
                min_cluster_size: int = DEFAULT_MIN_CLUSTER_SIZE,
                seed: int = DEFAULT_SEED, **_kwargs) -> HDBSCANMapper:
    """HDBSCAN 으로 fit, cluster centroid 추출. 부족하면 KMeans 보충."""
    if samples.shape[0] < n_strata * 5:
        raise ValueError(f"need >= {n_strata*5} samples, got {samples.shape[0]}")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hdb = HDBSCAN(min_cluster_size=min_cluster_size)
        labels = hdb.fit_predict(samples.astype(np.float32))

    unique_labels = sorted(set(labels) - {-1})
    if len(unique_labels) >= n_strata:
        # 너무 많음 → centroid 들에 KMeans 로 합침
        centroids_raw = np.array([
            samples[labels == lbl].mean(axis=0) for lbl in unique_labels
        ])
        km = KMeans(n_clusters=n_strata, random_state=seed, n_init=3)
        km.fit(centroids_raw)
        centroids = km.cluster_centers_
    else:
        # 부족 → KMeans 로 보충 (전체 sample 에)
        km = KMeans(n_clusters=n_strata, random_state=seed, n_init=3)
        km.fit(samples)
        centroids = km.cluster_centers_

    return HDBSCANMapper(cluster_centroids=centroids.astype(np.float32),
                         n_strata=n_strata)


def assign_hdbscan(mapper: HDBSCANMapper, vectors: np.ndarray) -> np.ndarray:
    return mapper.assign(vectors)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    counts = np.bincount(stratum_ids, minlength=n_clusters)
    return {"min": int(counts.min()), "max": int(counts.max()),
            "max_min_ratio": float(counts.max() / max(counts.min(), 1))}


def _self_test():
    rng = np.random.default_rng(0)
    centers = rng.standard_normal((5, 96)).astype(np.float32) * 5
    clustered = np.vstack([rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = fit_hdbscan(clustered, n_strata=20, seed=42)
    s = assign_hdbscan(m, clustered)
    summary = cluster_size_summary(s)
    print(f"[self-test] HDBSCAN clustered: max/min={summary['max_min_ratio']:.2f}")
    assert s.min() >= 0 and s.max() < 20
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
