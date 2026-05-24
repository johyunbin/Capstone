#!/usr/bin/env python3
"""
RQ3 #7 — E. Hilbert Curve stratification.

96d/128d 고차원 vec → PCA 2D → 2^p × 2^p integer grid → Hilbert distance →
quantile-based N_STRATA 분할.

학습 X (PCA 의 SVD 는 한 번의 결정론적 eigendecomposition, iterative training X).
같은 입력 + seed → 항상 동일 stratum_id.

Hilbert curve 의 동기:
  - 2D 평면 → 1D 매핑 시 인접 영역의 locality 보존 (z-order 보다 우수)
  - quantile 분할 → 각 stratum 의 면적이 거의 동일 (균질 stratum)
  - PCA 가 가장 큰 변동 방향 2개 살리므로 cluster 구조 일부 반영

본 모듈은 stratum_id 부여 알고리즘만 제공. 측정 골격 (cluster sample 캐시 +
HT estimator) 은 rq2_alloc_python.py 그대로 사용.

Usage:
    from hilbert_curve import fit_hilbert_mapper, assign_hilbert
    mapper = fit_hilbert_mapper(sample_array, n_strata=20, p=10, seed=42)
    stratum_ids = assign_hilbert(mapper, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import PCA

DEFAULT_K = 20
DEFAULT_SEED = 42
DEFAULT_P = 10  # 2^10 × 2^10 = 1024×1024 grid (1M cell, 1M+ row 분할에 충분)


def hilbert_xy_to_d(x: np.ndarray, y: np.ndarray, p: int) -> np.ndarray:
    """Wikipedia 표준 Hilbert curve algorithm (xy → distance), NumPy vectorized.

    n = 2^p, x/y in [0, n). 모든 좌표 동시 변환.
    Reference: https://en.wikipedia.org/wiki/Hilbert_curve#Applications_and_mapping_algorithms
    """
    n = 1 << p
    x = np.asarray(x, dtype=np.int64).copy()
    y = np.asarray(y, dtype=np.int64).copy()
    d = np.zeros_like(x)
    s = n >> 1
    while s > 0:
        rx = ((x & s) > 0).astype(np.int64)
        ry = ((y & s) > 0).astype(np.int64)
        d += s * s * ((3 * rx) ^ ry)
        # rotate/flip a quadrant when ry == 0
        flip = (ry == 0) & (rx == 1)
        x[flip] = n - 1 - x[flip]
        y[flip] = n - 1 - y[flip]
        # swap x, y where ry == 0
        mask = (ry == 0)
        x_swap = x[mask].copy()
        x[mask] = y[mask]
        y[mask] = x_swap
        s >>= 1
    return d


@dataclass
class HilbertMapper:
    """PCA basis + grid 범위 + quantile boundary 보유. assign() 으로 신규 vec 변환."""
    pca: PCA
    grid_min: np.ndarray   # (2,) PCA coord 의 최소
    grid_max: np.ndarray   # (2,) PCA coord 의 최대
    p: int                 # Hilbert order
    edges: np.ndarray      # (n_strata-1,) quantile boundaries
    n_strata: int

    @property
    def side(self) -> int:
        return 1 << self.p

    def _to_grid(self, coords: np.ndarray) -> np.ndarray:
        """PCA coord (2D) → integer grid [0, side)."""
        denom = (self.grid_max - self.grid_min).astype(np.float64)
        denom = np.where(denom < 1e-12, 1e-12, denom)
        norm = (coords - self.grid_min) / denom
        grid = np.clip((norm * self.side).astype(np.int64), 0, self.side - 1)
        return grid

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        """vectors (N, dim) → stratum_ids (N,) int32."""
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        # PCA matmul 의 numerical stability 위해 float64 로 변환
        coords = self.pca.transform(vectors.astype(np.float64))
        grid_xy = self._to_grid(coords)
        d = hilbert_xy_to_d(grid_xy[:, 0], grid_xy[:, 1], self.p)
        sids = np.searchsorted(self.edges, d, side='right')
        return np.clip(sids, 0, self.n_strata - 1).astype(np.int32)


def fit_hilbert_mapper(
    samples: np.ndarray,
    n_strata: int = DEFAULT_K,
    p: int = DEFAULT_P,
    seed: int = DEFAULT_SEED,
) -> HilbertMapper:
    """대표 sample 로 PCA basis + Hilbert grid + quantile boundary 결정.

    samples: (N, dim) — DEEP/SIFT 의 representative subsample
        dim ≥ 2 필요 (PCA 2D)
        N ≥ n_strata 필요 (quantile 분할 가능)

    학습 X (deterministic): PCA 는 SVD 의 한 번 eigendecomposition, Hilbert
    는 결정론적 매핑. 같은 (samples, seed, p) → 항상 동일 mapper.
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[1] < 2:
        raise ValueError(f"need dim >= 2 for PCA(n_components=2), got dim={samples.shape[1]}")
    if samples.shape[0] < n_strata:
        raise ValueError(f"need >= {n_strata} samples, got {samples.shape[0]}")

    # float64 로 fit — float32 입력에서 components_ 가 unstable 한 케이스 회피
    samples64 = samples.astype(np.float64)
    pca = PCA(n_components=2, svd_solver='full', random_state=seed).fit(samples64)
    coords = pca.transform(samples64)
    grid_min = coords.min(axis=0)
    grid_max = coords.max(axis=0)

    # 학습 sample 의 Hilbert distance 계산 → quantile boundary 결정
    side = 1 << p
    denom = (grid_max - grid_min)
    denom = np.where(denom < 1e-12, 1e-12, denom)
    norm = (coords - grid_min) / denom
    grid_xy = np.clip((norm * side).astype(np.int64), 0, side - 1)
    d = hilbert_xy_to_d(grid_xy[:, 0], grid_xy[:, 1], p)

    quantiles = np.quantile(d, np.linspace(0, 1, n_strata + 1))
    edges = quantiles[1:-1]  # n_strata - 1 boundaries (양 끝 제외)

    return HilbertMapper(
        pca=pca,
        grid_min=grid_min,
        grid_max=grid_max,
        p=p,
        edges=edges,
        n_strata=n_strata,
    )


def assign_hilbert(mapper: HilbertMapper, vectors: np.ndarray) -> np.ndarray:
    """vectors → stratum_id 부여. 반환 shape: (N,) int32."""
    return mapper.assign(vectors)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    """quantile 분할이 균질하게 되었는지 sanity check.

    fit_hilbert_mapper 의 quantile 기반 boundary → 학습 sample 위에서는 균등.
    새 vec 도 분포가 비슷하면 균등 가까움 (max/min ratio ~1).
    """
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
    """toy 검증 — Hilbert algorithm + 결정론 + quantile 균등성 + 다중 dim.

    toy 데이터 (1000×96 Gaussian iid) 의 PCA 는 의미있는 변동 축이 없어
    sklearn 이 RuntimeWarning 발생 가능 — 실제 DEEP/SIFT 의 cluster 구조
    데이터에선 발생 X. self-test 만 suppress.
    """
    import warnings

    # 1. Hilbert algorithm 검증 (wiki 표준 예제, sklearn 무관)
    # p=1 (n=2): (0,0)=0, (0,1)=1, (1,1)=2, (1,0)=3
    pts = np.array([[0, 0], [0, 1], [1, 1], [1, 0]], dtype=np.int64)
    ds = hilbert_xy_to_d(pts[:, 0], pts[:, 1], p=1)
    expected = np.array([0, 1, 2, 3])
    assert np.array_equal(ds, expected), f"Hilbert n=2 mismatch: got {ds}, expected {expected}"
    print(f"[self-test] Hilbert p=1: corners → {ds.tolist()} (expected {expected.tolist()}) ✓")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)

        # 2. 결정론 확인
        rng = np.random.default_rng(0)
        vectors = rng.standard_normal((1000, 96)).astype(np.float32)
        m1 = fit_hilbert_mapper(vectors, n_strata=20, p=8, seed=42)
        m2 = fit_hilbert_mapper(vectors, n_strata=20, p=8, seed=42)
        s1 = assign_hilbert(m1, vectors)
        s2 = assign_hilbert(m2, vectors)
        assert np.array_equal(s1, s2), "Hilbert mapper must be deterministic for fixed seed"
        print("[self-test] determinism ✓")

        # 3. quantile 분할 → 학습 sample 에선 거의 균등 (max/min ratio < 3)
        summary = cluster_size_summary(s1, n_clusters=20)
        print(f"[self-test] bucket sizes: min={summary['min']} max={summary['max']} "
              f"mean={summary['mean']:.1f} std={summary['std']:.1f} "
              f"max_min_ratio={summary['max_min_ratio']:.2f}")
        print(f"[self-test] counts: {summary['counts']}")
        assert summary["max_min_ratio"] < 3.0, \
            f"quantile split should yield ~equal buckets on fit sample, got {summary['max_min_ratio']:.2f}"
        assert s1.shape == (1000,), f"unexpected shape {s1.shape}"
        assert s1.min() >= 0 and s1.max() < 20, "stratum_id out of range"

        # 4. unseen vec 도 정상 부여 (fit 안 한 새 vec)
        new_vecs = rng.standard_normal((200, 96)).astype(np.float32)
        new_sids = assign_hilbert(m1, new_vecs)
        assert new_sids.shape == (200,)
        assert new_sids.min() >= 0 and new_sids.max() < 20
        print(f"[self-test] new vec assignment: 200 vecs, sid range [{new_sids.min()}, {new_sids.max()}] ✓")

        # 5. 128d (SIFT) 도 동작 확인
        sift_vecs = rng.standard_normal((500, 128)).astype(np.float32)
        sift_mapper = fit_hilbert_mapper(sift_vecs, n_strata=20, p=8, seed=42)
        sift_sids = assign_hilbert(sift_mapper, sift_vecs)
        sift_summary = cluster_size_summary(sift_sids, n_clusters=20)
        print(f"[self-test] SIFT 128d: max_min_ratio={sift_summary['max_min_ratio']:.2f} ✓")

        # 6. cluster 구조 있는 데이터 (PCA 가 정상 작동) — 5 Gaussian center
        centers = rng.standard_normal((5, 96)).astype(np.float32) * 10
        clustered = np.vstack([
            rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
        ])
        cl_mapper = fit_hilbert_mapper(clustered, n_strata=20, p=8, seed=42)
        cl_sids = assign_hilbert(cl_mapper, clustered)
        cl_summary = cluster_size_summary(cl_sids, n_clusters=20)
        print(f"[self-test] clustered data: max_min_ratio={cl_summary['max_min_ratio']:.2f} ✓")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
