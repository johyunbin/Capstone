#!/usr/bin/env python3
"""
RQ3 #18 — Gaussian Mixture Model (GMM) soft clustering.

KMeans (hard) 와 달리 GMM 은 각 point 의 cluster posterior 확률 보고 soft assignment.
Hard assignment (argmax) 으로 stratum_id 부여.

KMeans 의 spherical cluster 가정 vs GMM 의 임의 covariance — non-spherical cluster
(SIFT 의 skewed distribution) 에서 GMM 우위 가능.

가설 H3-GM: GMM 이 SIFT (non-spherical) 에서 MiniBatch 보다 약간 우수.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from sklearn.mixture import GaussianMixture

DEFAULT_K = 20
DEFAULT_SEED = 42


@dataclass
class GMMMapper:
    model: GaussianMixture
    n_strata: int

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        return self.model.predict(vectors).astype(np.int32)


def fit_gmm(samples: np.ndarray, n_strata: int = DEFAULT_K,
            covariance_type: str = "diag", seed: int = DEFAULT_SEED,
            **_kwargs) -> GMMMapper:
    """GMM 학습 — covariance_type='diag' 이 high-D 에서 안정적."""
    if samples.shape[0] < n_strata * 2:
        raise ValueError(f"need >= {n_strata*2} samples, got {samples.shape[0]}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gmm = GaussianMixture(n_components=n_strata, covariance_type=covariance_type,
                              random_state=seed, max_iter=100, n_init=1)
        gmm.fit(samples.astype(np.float32))
    return GMMMapper(model=gmm, n_strata=n_strata)


def assign_gmm(mapper: GMMMapper, vectors: np.ndarray) -> np.ndarray:
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
        m = fit_gmm(clustered, n_strata=20, seed=42)
    s = assign_gmm(m, clustered)
    summary = cluster_size_summary(s)
    print(f"[self-test] GMM clustered: max/min={summary['max_min_ratio']:.2f}")
    assert s.min() >= 0 and s.max() < 20
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
