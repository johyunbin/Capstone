#!/usr/bin/env python3
"""
RQ3 #15 — Spectral Clustering stratification.

KMeans / MiniBatch 와 직교적인 cluster discovery: graph Laplacian eigenvector
기반. Nystrom approximation 으로 large-N 적용 가능.

가설 H3-Sp:
  - Spectral 가 KMeans 와 다른 cluster 발견 → ARI(spectral, minibatch) 작음 정량.
  - non-convex cluster 가 있는 데이터 (SIFT 의 skewed) 에서 KMeans 보다 우수 가능.
  - 그러나 Nystrom 의 sample noise 와 sklearn n_init 한계로 KMeans 보다 약할 수도.

학습: 1% sample 에 sklearn SpectralClustering 적용. 학습 sample 의 cluster id
   를 centroid 로 매핑한 뒤, all_vecs 에 nearest centroid 부여 (Nystrom 변형).

Usage:
    from spectral_clustering import fit_spectral, assign_spectral
    mapper = fit_spectral(samples, n_strata=20, seed=42)
    sids = assign_spectral(mapper, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import SpectralClustering, KMeans

DEFAULT_K = 20
DEFAULT_SEED = 42


@dataclass
class SpectralMapper:
    """학습 sample 의 cluster centroid + 학습 결과의 in-sample sids."""
    centroids: np.ndarray   # (K, dim)
    n_strata: int

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        """nearest centroid 로 stratum 부여 (Nystrom 변형)."""
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        # batched distance — 100K rows × 20 centroids 면 메모리 OK
        # 큰 N 의 경우 chunk 처리.
        n = len(vectors)
        chunk = 50000
        sids = np.zeros(n, dtype=np.int32)
        for start in range(0, n, chunk):
            end = min(start + chunk, n)
            sub = vectors[start:end]
            # ‖x - c‖² = ‖x‖² - 2 x·c + ‖c‖²
            xc = sub @ self.centroids.T   # (chunk, K)
            xx = (sub * sub).sum(axis=1, keepdims=True)
            cc = (self.centroids * self.centroids).sum(axis=1)
            dists = xx - 2 * xc + cc
            sids[start:end] = np.argmin(dists, axis=1).astype(np.int32)
        return sids


def fit_spectral(
    samples: np.ndarray,
    n_strata: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    affinity: str = "nearest_neighbors",
    n_neighbors: int = 10,
    **_kwargs,
) -> SpectralMapper:
    """학습 sample 에 spectral clustering 적용 후 cluster centroid 추출.

    sklearn SpectralClustering 은 transductive (학습 sample 만 cluster id 부여).
    new vec 에 적용하려면 centroid (cluster mean) 추출 후 nearest 부여.

    affinity='nearest_neighbors' 가 'rbf' 보다 large-N (10K+) 에서 안정적.
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[0] < n_strata * 2:
        raise ValueError(f"need >= {n_strata*2} samples, got {samples.shape[0]}")

    samples64 = samples.astype(np.float64)
    sc = SpectralClustering(
        n_clusters=n_strata, affinity=affinity, n_neighbors=n_neighbors,
        random_state=seed, assign_labels="kmeans", n_init=3,
    )
    learn_sids = sc.fit_predict(samples64)
    # cluster mean 으로 centroid 부여
    centroids = np.zeros((n_strata, samples.shape[1]), dtype=np.float32)
    for c in range(n_strata):
        mask = learn_sids == c
        if mask.sum() > 0:
            centroids[c] = samples[mask].mean(axis=0)
        else:
            # empty cluster — 임의 sample 한 개 대표
            centroids[c] = samples[c % len(samples)]
    return SpectralMapper(centroids=centroids, n_strata=n_strata)


def assign_spectral(mapper: SpectralMapper, vectors: np.ndarray) -> np.ndarray:
    return mapper.assign(vectors)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
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
    import warnings
    rng = np.random.default_rng(0)

    # cluster 데이터 — Spectral 의 강점 (non-convex cluster) 시뮬은 toy 어려워서
    # 단순 Gaussian 5 cluster 로 동작 검증만.
    centers = rng.standard_normal((5, 96)).astype(np.float32) * 5
    clustered = np.vstack([
        rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
    ])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m1 = fit_spectral(clustered, n_strata=20, seed=42, n_neighbors=10)
        m2 = fit_spectral(clustered, n_strata=20, seed=42, n_neighbors=10)
        s1 = assign_spectral(m1, clustered)
        s2 = assign_spectral(m2, clustered)
        # sklearn SpectralClustering 은 결정론적 X (k-means assign 단계에 random)
        # 같은 seed 에서 *대부분* 같은 결과 — strict equality 는 X.
        agreement = (s1 == s2).mean()
        print(f"[self-test] determinism: {agreement:.3f} agreement (sklearn 부분 random)")

        # cluster size 분포
        summary = cluster_size_summary(s1, n_clusters=20)
        print(f"[self-test] clustered: max/min={summary['max_min_ratio']:.2f}, "
              f"counts (first 5)={summary['counts'][:5]}")
        assert s1.min() >= 0 and s1.max() < 20

        # 96d iid (non-clustered) 도 동작
        iid = rng.standard_normal((1000, 96)).astype(np.float32)
        m_iid = fit_spectral(iid, n_strata=20, seed=42)
        s_iid = assign_spectral(m_iid, iid)
        iid_summary = cluster_size_summary(s_iid, n_clusters=20)
        print(f"[self-test] iid 96d: max/min={iid_summary['max_min_ratio']:.2f}")

        # 128d (SIFT)
        sift = rng.standard_normal((1000, 128)).astype(np.float32)
        m_sift = fit_spectral(sift, n_strata=20, seed=42)
        s_sift = assign_spectral(m_sift, sift)
        assert s_sift.min() >= 0 and s_sift.max() < 20
        print(f"[self-test] SIFT 128d: range [{s_sift.min()}, {s_sift.max()}] ✓")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
