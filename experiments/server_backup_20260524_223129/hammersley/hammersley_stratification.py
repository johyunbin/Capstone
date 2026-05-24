#!/usr/bin/env python3
"""
RQ3 — Hammersley sequence quasi-random stratification (Wave 1).

Hammersley sequence — Halton 의 단순화. 첫 dimension 은 i/N (uniform), 나머지는
Halton (prime base radical inverse). PCA 2D 좌표 → Hammersley point N_STRATA 와
nearest-neighbor stratum.

특이점 (Sobol/Halton 대비):
- 첫 차원이 i/N 으로 *완벽히 균등* — 2D 평면에서 가장 대칭적
- 단, N 을 미리 알아야 함 (online 환경 X)

가설: Sobol, Halton 와 비슷 — QMC family.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import PCA

DEFAULT_K = 20
DEFAULT_SEED = 42


def _radical_inverse(i: int, base: int) -> float:
    """prime base 의 radical inverse phi_b(i)."""
    f = 1.0
    r = 0.0
    while i > 0:
        f /= base
        r += f * (i % base)
        i //= base
    return r


def hammersley_points(n: int, seed: int = 0) -> np.ndarray:
    """N 개의 Hammersley point in [0,1)^2. 차원 0 = (i+0.5)/N, 차원 1 = phi_2(i+seed_shift)."""
    rng = np.random.default_rng(seed)
    shift = rng.integers(0, 1000)  # scramble base 선택
    pts = np.zeros((n, 2), dtype=np.float64)
    for i in range(n):
        pts[i, 0] = (i + 0.5) / n
        pts[i, 1] = _radical_inverse(i + shift + 1, 2)
    # rotate offset (scramble) — 같은 N 에서 다른 seed 보장
    offset = rng.uniform(0, 1)
    pts[:, 1] = (pts[:, 1] + offset) % 1.0
    return pts


@dataclass
class HammersleyMapper:
    pca: PCA
    hm_points: np.ndarray
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
            xs = sub @ self.hm_points.T
            xx = (sub * sub).sum(axis=1, keepdims=True)
            ss = (self.hm_points * self.hm_points).sum(axis=1)
            dists = xx - 2 * xs + ss
            sids[start:end] = np.argmin(dists, axis=1).astype(np.int32)
        return sids


def fit_hammersley(samples: np.ndarray, n_strata: int = DEFAULT_K,
                   seed: int = DEFAULT_SEED, **_kwargs) -> HammersleyMapper:
    samples64 = samples.astype(np.float64)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pca = PCA(n_components=2, svd_solver='full', random_state=seed).fit(samples64)
        coords = pca.transform(samples64)
    grid_min = coords.min(axis=0)
    grid_max = coords.max(axis=0)

    pts = hammersley_points(n=n_strata, seed=seed)

    return HammersleyMapper(pca=pca, hm_points=pts,
                            grid_min=grid_min, grid_max=grid_max,
                            n_strata=n_strata)


def assign_hammersley(mapper: HammersleyMapper, vectors: np.ndarray) -> np.ndarray:
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
        m = fit_hammersley(samples, n_strata=20, seed=42)
    s = assign_hammersley(m, samples)
    summary = cluster_size_summary(s)
    print(f"[self-test] Hammersley iid 96d: max/min={summary['max_min_ratio']:.2f}")
    assert s.min() >= 0 and s.max() < 20
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
