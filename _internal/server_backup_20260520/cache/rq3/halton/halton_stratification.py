#!/usr/bin/env python3
"""
RQ3 — Halton sequence quasi-random stratification (Wave 1).

Halton sequence (low-discrepancy, deterministic) — Sobol과 같은 QMC family이지만
prime base-{2,3} 라디칼 역수 방식으로 다른 실현. PCA 2D 좌표를 [0,1)^2 로 mapping 후
Halton point 와의 nearest-neighbor 로 stratum 부여.

차이점 (Sobol vs Halton):
- Sobol: digital net (base 2)
- Halton: prime bases (2, 3, 5, ...) — prime radical inverse

가설: Sobol 와 비슷한 성능 — QMC family로 동일 카테고리.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from scipy.stats import qmc
from sklearn.decomposition import PCA

DEFAULT_K = 20
DEFAULT_SEED = 42


@dataclass
class HaltonMapper:
    pca: PCA
    halton_points: np.ndarray   # (n_strata, 2)
    grid_min: np.ndarray
    grid_max: np.ndarray
    n_strata: int

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        coords = self.pca.transform(vectors.astype(np.float64))
        denom = (self.grid_max - self.grid_min)
        denom = np.where(denom < 1e-12, 1e-12, denom)
        norm = np.clip((coords - self.grid_min) / denom, 0, 1)
        n = len(vectors)
        sids = np.zeros(n, dtype=np.int32)
        chunk = 50000
        for start in range(0, n, chunk):
            end = min(start + chunk, n)
            sub = norm[start:end]
            xs = sub @ self.halton_points.T
            xx = (sub * sub).sum(axis=1, keepdims=True)
            ss = (self.halton_points * self.halton_points).sum(axis=1)
            dists = xx - 2 * xs + ss
            sids[start:end] = np.argmin(dists, axis=1).astype(np.int32)
        return sids


def fit_halton(samples: np.ndarray, n_strata: int = DEFAULT_K,
               seed: int = DEFAULT_SEED, **_kwargs) -> HaltonMapper:
    """PCA 2D + Halton point N_STRATA 개 생성."""
    samples64 = samples.astype(np.float64)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pca = PCA(n_components=2, svd_solver='full', random_state=seed).fit(samples64)
        coords = pca.transform(samples64)
    grid_min = coords.min(axis=0)
    grid_max = coords.max(axis=0)

    halton = qmc.Halton(d=2, seed=seed, scramble=True)
    halton_points = halton.random(n=n_strata)

    return HaltonMapper(pca=pca, halton_points=halton_points.astype(np.float64),
                        grid_min=grid_min, grid_max=grid_max, n_strata=n_strata)


def assign_halton(mapper: HaltonMapper, vectors: np.ndarray) -> np.ndarray:
    return mapper.assign(vectors)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    counts = np.bincount(stratum_ids, minlength=n_clusters)
    return {"min": int(counts.min()), "max": int(counts.max()),
            "max_min_ratio": float(counts.max() / max(counts.min(), 1))}


def _self_test():
    rng = np.random.default_rng(0)
    samples = rng.standard_normal((1000, 96)).astype(np.float32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = fit_halton(samples, n_strata=20, seed=42)
    s = assign_halton(m, samples)
    summary = cluster_size_summary(s)
    print(f"[self-test] Halton iid 96d: max/min={summary['max_min_ratio']:.2f}")
    assert s.min() >= 0 and s.max() < 20
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
