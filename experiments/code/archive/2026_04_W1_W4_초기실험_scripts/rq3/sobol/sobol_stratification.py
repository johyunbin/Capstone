#!/usr/bin/env python3
"""
RQ3 #19 — Sobol sequence quasi-random stratification.

Sobol sequence (low-discrepancy sequence) — Monte Carlo / quasi-Monte Carlo 분야 표준.
PCA 2D coordinates 의 [0,1)^2 unit square 에 mapping 후 Sobol point 와의 nearest-neighbor
로 stratum 부여.

특이점:
- random projection / hash 와 달리 *결정론적* + low-discrepancy (uniform 보장)
- 각 stratum 의 \"중심\" 이 sobol point — uniform spread

가설 H3-Sb: Sobol 가 RANDOM20 (random partition) 보다 우수, Hilbert (PCA + curve) 와
비교 시 trade-off 발생.
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
class SobolMapper:
    pca: PCA
    sobol_points: np.ndarray   # (n_strata, 2)
    grid_min: np.ndarray
    grid_max: np.ndarray
    n_strata: int

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        coords = self.pca.transform(vectors.astype(np.float64))
        denom = (self.grid_max - self.grid_min)
        denom = np.where(denom < 1e-12, 1e-12, denom)
        norm = np.clip((coords - self.grid_min) / denom, 0, 1)
        # nearest sobol point
        n = len(vectors)
        sids = np.zeros(n, dtype=np.int32)
        chunk = 50000
        for start in range(0, n, chunk):
            end = min(start + chunk, n)
            sub = norm[start:end]
            # ‖x - s‖²
            xs = sub @ self.sobol_points.T
            xx = (sub * sub).sum(axis=1, keepdims=True)
            ss = (self.sobol_points * self.sobol_points).sum(axis=1)
            dists = xx - 2 * xs + ss
            sids[start:end] = np.argmin(dists, axis=1).astype(np.int32)
        return sids


def fit_sobol(samples: np.ndarray, n_strata: int = DEFAULT_K,
              seed: int = DEFAULT_SEED, **_kwargs) -> SobolMapper:
    """PCA 2D + Sobol point N_STRATA 개 생성."""
    samples64 = samples.astype(np.float64)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pca = PCA(n_components=2, svd_solver='full', random_state=seed).fit(samples64)
        coords = pca.transform(samples64)
    grid_min = coords.min(axis=0)
    grid_max = coords.max(axis=0)

    # Sobol n_strata point
    sobol = qmc.Sobol(d=2, seed=seed, scramble=True)
    sobol_points = sobol.random(n=n_strata)

    return SobolMapper(pca=pca, sobol_points=sobol_points.astype(np.float64),
                       grid_min=grid_min, grid_max=grid_max, n_strata=n_strata)


def assign_sobol(mapper: SobolMapper, vectors: np.ndarray) -> np.ndarray:
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
        m = fit_sobol(samples, n_strata=20, seed=42)
    s = assign_sobol(m, samples)
    summary = cluster_size_summary(s)
    print(f"[self-test] Sobol iid 96d: max/min={summary['max_min_ratio']:.2f}")
    assert s.min() >= 0 and s.max() < 20
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
