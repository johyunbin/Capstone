#!/usr/bin/env python3
"""
RQ3 #7-P — PCA-1D quantile stratification (Hilbert/Z-order ablation 의 *최상위*).

Hilbert curve = PCA(2D) + grid + Hilbert distance + quantile.
Z-order curve = PCA(2D) + grid + Z bit-interleave + quantile.
**PCA-1D = PCA(1D) + quantile** — curve 자체 X. 가장 단순.

Ablation ladder (5/8 회의 narrative 핵심):
    BERN → RANDOM20 → **PCA-1D** → Z-order → Hilbert → MiniBatch → KM20 oracle

이로써 Hilbert 의 contribution origin 이 (a) PCA 효과 (b) curve 효과 두 layer 로
분리. PCA-1D 가 RANDOM20 ≪ PCA-1D 면 PCA 자체가 핵심, PCA-1D ≪ Hilbert 면 curve
효과가 핵심. 보통 둘 다 부분 효과.

학습 X (deterministic): PCA SVD 한 번. quantile 분할.

Usage:
    from pca1d_quantile import fit_pca1d_mapper, assign_pca1d
    mapper = fit_pca1d_mapper(samples, n_strata=20, seed=42)
    sids = assign_pca1d(mapper, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import PCA

DEFAULT_K = 20
DEFAULT_SEED = 42


@dataclass
class PCA1DMapper:
    """PCA basis (1D) + quantile boundary 만 보유."""
    pca: PCA
    edges: np.ndarray   # (n_strata-1,) quantile boundary
    n_strata: int

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        coords = self.pca.transform(vectors.astype(np.float64))[:, 0]
        sids = np.searchsorted(self.edges, coords, side='right')
        return np.clip(sids, 0, self.n_strata - 1).astype(np.int32)


def fit_pca1d_mapper(
    samples: np.ndarray,
    n_strata: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    **_kwargs,
) -> PCA1DMapper:
    """대표 sample 로 PCA basis (1D) + quantile boundary 결정.

    완전 결정론. 같은 input → 같은 mapper.
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[0] < n_strata:
        raise ValueError(f"need >= {n_strata} samples, got {samples.shape[0]}")

    samples64 = samples.astype(np.float64)
    pca = PCA(n_components=1, svd_solver='full', random_state=seed).fit(samples64)
    coords = pca.transform(samples64)[:, 0]
    quantiles = np.quantile(coords, np.linspace(0, 1, n_strata + 1))
    edges = quantiles[1:-1]

    return PCA1DMapper(pca=pca, edges=edges, n_strata=n_strata)


def assign_pca1d(mapper: PCA1DMapper, vectors: np.ndarray) -> np.ndarray:
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
        warnings.simplefilter("ignore", category=RuntimeWarning)
        # 결정론
        samples = rng.standard_normal((1000, 96)).astype(np.float32)
        m1 = fit_pca1d_mapper(samples, n_strata=20, seed=42)
        m2 = fit_pca1d_mapper(samples, n_strata=20, seed=42)
        s1 = assign_pca1d(m1, samples)
        s2 = assign_pca1d(m2, samples)
        assert np.array_equal(s1, s2), "PCA-1D must be deterministic"
        print("[self-test] determinism ✓")

        # quantile 분할 → fit sample 위에서 거의 균등
        summary = cluster_size_summary(s1, n_clusters=20)
        print(f"[self-test] iid 96d: max/min={summary['max_min_ratio']:.2f}, "
              f"explained_var={float(m1.pca.explained_variance_ratio_[0]):.4f}")
        assert summary["max_min_ratio"] < 1.5, f"quantile should be ~equal, got {summary['max_min_ratio']:.2f}"

        # cluster 데이터 → 1D 만으론 cluster 정보 일부만 살림
        centers = rng.standard_normal((5, 96)).astype(np.float32) * 10
        clustered = np.vstack([
            rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
        ])
        m_cl = fit_pca1d_mapper(clustered, n_strata=20, seed=42)
        s_cl = assign_pca1d(m_cl, clustered)
        cl_summary = cluster_size_summary(s_cl, n_clusters=20)
        print(f"[self-test] clustered: max/min={cl_summary['max_min_ratio']:.2f}, "
              f"explained_var={float(m_cl.pca.explained_variance_ratio_[0]):.4f}")

        # SIFT 128d 동작
        sift = rng.standard_normal((500, 128)).astype(np.float32)
        m_sift = fit_pca1d_mapper(sift, n_strata=20, seed=42)
        s_sift = assign_pca1d(m_sift, sift)
        assert s_sift.min() >= 0 and s_sift.max() < 20

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
