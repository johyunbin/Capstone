#!/usr/bin/env python3
"""
RQ3 #16 — BIRCH (tree-based incremental clustering) stratification.

BIRCH (Balanced Iterative Reducing and Clustering using Hierarchies, Zhang 1996):
- Clustering Feature (CF) tree 구성 — incremental, single-pass.
- partial_fit 지원 (sklearn) → MiniBatch partial_fit 의 streaming alternative.
- 트리 기반이라 KD-tree 와 paradigm 비슷하나, leaf 가 cluster centroid 임 (spatial
  partition X, density-based).

가설 H3-Bi:
  - BIRCH 가 KMeans 와 다른 cluster discovery (incremental tree).
  - partial_fit 알고리즘이라 OLTP 적합. MiniBatch-partial 과 비교 → 두 streaming
    method 의 trade-off 정량.

학습: sklearn Birch(n_clusters=20). 1% sample 에 fit() — partial_fit 도 가능.

Usage:
    from birch_partition import fit_birch, assign_birch
    mapper = fit_birch(samples, n_strata=20, seed=42)
    sids = assign_birch(mapper, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import Birch

DEFAULT_K = 20
DEFAULT_THRESHOLD = 0.5
DEFAULT_BRANCH = 50


@dataclass
class BirchMapper:
    model: Birch
    n_strata: int

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        return self.model.predict(vectors).astype(np.int32)


def fit_birch(
    samples: np.ndarray,
    n_strata: int = DEFAULT_K,
    threshold: float = DEFAULT_THRESHOLD,
    branching_factor: int = DEFAULT_BRANCH,
    seed: int = 42,   # API 호환 (Birch 자체는 결정론)
    **_kwargs,
) -> BirchMapper:
    """학습 sample 에 BIRCH 적용.

    threshold: leaf 의 sub-cluster radius 한계. 작을수록 leaf 많음.
    branching_factor: 각 internal node 의 max child. 50 (sklearn default).

    Birch 는 본질적 결정론 — 같은 input → 같은 tree.
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[0] < n_strata:
        raise ValueError(f"need >= {n_strata} samples, got {samples.shape[0]}")

    model = Birch(
        n_clusters=n_strata, threshold=threshold,
        branching_factor=branching_factor,
    )
    model.fit(samples)
    return BirchMapper(model=model, n_strata=n_strata)


def assign_birch(mapper: BirchMapper, vectors: np.ndarray) -> np.ndarray:
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

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # iid 96d
        samples = rng.standard_normal((2000, 96)).astype(np.float32)
        m1 = fit_birch(samples, n_strata=20, seed=42)
        m2 = fit_birch(samples, n_strata=20, seed=42)
        s1 = assign_birch(m1, samples)
        s2 = assign_birch(m2, samples)
        assert np.array_equal(s1, s2), "BIRCH must be deterministic"
        print("[self-test] determinism ✓")

        summary = cluster_size_summary(s1, n_clusters=20)
        print(f"[self-test] iid 96d: max/min={summary['max_min_ratio']:.2f}")

        # clustered
        centers = rng.standard_normal((5, 96)).astype(np.float32) * 5
        clustered = np.vstack([
            rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
        ])
        m_cl = fit_birch(clustered, n_strata=20, seed=42)
        s_cl = assign_birch(m_cl, clustered)
        cl_summary = cluster_size_summary(s_cl, n_clusters=20)
        print(f"[self-test] clustered: max/min={cl_summary['max_min_ratio']:.2f}")

        # SIFT 128d
        sift = rng.standard_normal((1000, 128)).astype(np.float32)
        m_sift = fit_birch(sift, n_strata=20, seed=42)
        s_sift = assign_birch(m_sift, sift)
        assert s_sift.min() >= 0 and s_sift.max() < 20
        print("[self-test] SIFT 128d ✓")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
