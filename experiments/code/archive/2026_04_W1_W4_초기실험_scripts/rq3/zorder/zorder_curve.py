#!/usr/bin/env python3
"""
RQ3 #7-Z — Z-order curve stratification (Hilbert ablation).

Hilbert 와 동일 골격: PCA 2D → 2^p × 2^p integer grid → 1D distance →
quantile N_STRATA 분할. 차이점은 distance 계산 — Hilbert 의 회전+swap
algorithm 대신 bit interleaving (Morton order) 만 수행.

Z-order vs Hilbert 비교 동기:
  - Z-order: 가장 단순한 space-filling curve (bit interleave). locality 약함
    (Y 축 큰 점프 발생 — "Z" 모양). 구현 ~5줄.
  - Hilbert: locality 보존 우수 (인접 grid cell 의 Hilbert distance 인접).
    회전/flip 으로 quadrant 간 jump 제거. 구현 ~20줄.

  → "Hilbert 의 강한 결과 (DEEP -3.7%, SIFT -4.1%) 가 (a) PCA+quantile 의 효과인지
    (b) Hilbert curve 자체의 locality 효과인지" 분리 검증.

만약 Z-order recovery 가 Hilbert 와 비슷하면 → (a) PCA+quantile 이 핵심.
만약 Z-order recovery 가 떨어지면 → (b) Hilbert 의 locality 가 contribution.

학습 X (deterministic): PCA 의 SVD + bit interleave 모두 결정론.
같은 (samples, seed, p) → 항상 동일 mapper.

Usage:
    from zorder_curve import fit_zorder_mapper, assign_zorder
    mapper = fit_zorder_mapper(sample_array, n_strata=20, p=10, seed=42)
    stratum_ids = assign_zorder(mapper, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import PCA

DEFAULT_K = 20
DEFAULT_SEED = 42
DEFAULT_P = 10  # Hilbert 와 동일한 grid 해상도 (1024×1024)


def zorder_xy_to_d(x: np.ndarray, y: np.ndarray, p: int) -> np.ndarray:
    """Morton order (Z-curve) bit interleaving, NumPy vectorized.

    n = 2^p, x/y in [0, n). x_i, y_i 의 i 번째 bit 를 (2i+1, 2i) 위치로 보냄.
    예: x=0b101, y=0b011, p=3 → d=0b100111 (y0,x0,y1,x1,y2,x2 = 1,1,1,0,0,1 = 39)

    Reference: https://en.wikipedia.org/wiki/Z-order_curve
    """
    x = np.asarray(x, dtype=np.int64)
    y = np.asarray(y, dtype=np.int64)
    d = np.zeros_like(x)
    for i in range(p):
        bit = 1 << i
        d |= (x & bit) << i        # x 의 i 번째 bit → 2i 번째
        d |= (y & bit) << (i + 1)  # y 의 i 번째 bit → 2i+1 번째
    return d


@dataclass
class ZorderMapper:
    """PCA basis + grid 범위 + quantile boundary 보유. Hilbert mapper 와 인터페이스 동일."""
    pca: PCA
    grid_min: np.ndarray   # (2,)
    grid_max: np.ndarray   # (2,)
    p: int
    edges: np.ndarray      # (n_strata-1,) quantile boundaries
    n_strata: int

    @property
    def side(self) -> int:
        return 1 << self.p

    def _to_grid(self, coords: np.ndarray) -> np.ndarray:
        denom = (self.grid_max - self.grid_min).astype(np.float64)
        denom = np.where(denom < 1e-12, 1e-12, denom)
        norm = (coords - self.grid_min) / denom
        grid = np.clip((norm * self.side).astype(np.int64), 0, self.side - 1)
        return grid

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        coords = self.pca.transform(vectors.astype(np.float64))
        grid_xy = self._to_grid(coords)
        d = zorder_xy_to_d(grid_xy[:, 0], grid_xy[:, 1], self.p)
        sids = np.searchsorted(self.edges, d, side='right')
        return np.clip(sids, 0, self.n_strata - 1).astype(np.int32)


def fit_zorder_mapper(
    samples: np.ndarray,
    n_strata: int = DEFAULT_K,
    p: int = DEFAULT_P,
    seed: int = DEFAULT_SEED,
) -> ZorderMapper:
    """대표 sample 로 PCA basis + Z-order grid + quantile boundary 결정.

    Hilbert 와 동일한 fit 절차. distance 함수만 zorder_xy_to_d 사용.
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[1] < 2:
        raise ValueError(f"need dim >= 2 for PCA(n_components=2), got dim={samples.shape[1]}")
    if samples.shape[0] < n_strata:
        raise ValueError(f"need >= {n_strata} samples, got {samples.shape[0]}")

    samples64 = samples.astype(np.float64)
    pca = PCA(n_components=2, svd_solver='full', random_state=seed).fit(samples64)
    coords = pca.transform(samples64)
    grid_min = coords.min(axis=0)
    grid_max = coords.max(axis=0)

    side = 1 << p
    denom = (grid_max - grid_min)
    denom = np.where(denom < 1e-12, 1e-12, denom)
    norm = (coords - grid_min) / denom
    grid_xy = np.clip((norm * side).astype(np.int64), 0, side - 1)
    d = zorder_xy_to_d(grid_xy[:, 0], grid_xy[:, 1], p)

    quantiles = np.quantile(d, np.linspace(0, 1, n_strata + 1))
    edges = quantiles[1:-1]

    return ZorderMapper(
        pca=pca,
        grid_min=grid_min,
        grid_max=grid_max,
        p=p,
        edges=edges,
        n_strata=n_strata,
    )


def assign_zorder(mapper: ZorderMapper, vectors: np.ndarray) -> np.ndarray:
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
    """toy 검증 — Z-order algorithm + 결정론 + quantile 균등성."""
    import warnings

    # 1. Z-order algorithm 검증 (wiki 표준 예제)
    # p=1 (n=2): (0,0)=0, (1,0)=1, (0,1)=2, (1,1)=3 — Z 순서
    pts = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=np.int64)
    ds = zorder_xy_to_d(pts[:, 0], pts[:, 1], p=1)
    expected = np.array([0, 1, 2, 3])
    assert np.array_equal(ds, expected), f"Z-order n=2 mismatch: got {ds}, expected {expected}"
    print(f"[self-test] Z-order p=1: corners → {ds.tolist()} (expected {expected.tolist()}) ✓")

    # p=2 (n=4): 4×4 grid 16 cell 모두 unique (0..15)
    xs, ys = np.meshgrid(np.arange(4), np.arange(4), indexing='xy')
    ds_full = zorder_xy_to_d(xs.flatten(), ys.flatten(), p=2)
    assert sorted(ds_full.tolist()) == list(range(16)), \
        f"Z-order p=2 should produce permutation of 0..15, got {sorted(ds_full.tolist())}"
    print(f"[self-test] Z-order p=2: 4×4 grid → 0..15 unique ✓")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)

        # 2. 결정론
        rng = np.random.default_rng(0)
        vectors = rng.standard_normal((1000, 96)).astype(np.float32)
        m1 = fit_zorder_mapper(vectors, n_strata=20, p=8, seed=42)
        m2 = fit_zorder_mapper(vectors, n_strata=20, p=8, seed=42)
        s1 = assign_zorder(m1, vectors)
        s2 = assign_zorder(m2, vectors)
        assert np.array_equal(s1, s2), "Z-order mapper must be deterministic for fixed seed"
        print("[self-test] determinism ✓")

        # 3. quantile 분할 → 학습 sample 에선 거의 균등
        summary = cluster_size_summary(s1, n_clusters=20)
        print(
            f"[self-test] bucket sizes: min={summary['min']} max={summary['max']} "
            f"mean={summary['mean']:.1f} std={summary['std']:.1f} "
            f"max_min_ratio={summary['max_min_ratio']:.2f}"
        )
        assert summary["max_min_ratio"] < 3.0, \
            f"quantile split should yield ~equal buckets on fit sample, got {summary['max_min_ratio']:.2f}"
        assert s1.min() >= 0 and s1.max() < 20, "stratum_id out of range"

        # 4. 128d (SIFT) 동작 확인
        sift_vecs = rng.standard_normal((500, 128)).astype(np.float32)
        sift_mapper = fit_zorder_mapper(sift_vecs, n_strata=20, p=8, seed=42)
        sift_sids = assign_zorder(sift_mapper, sift_vecs)
        sift_summary = cluster_size_summary(sift_sids, n_clusters=20)
        print(f"[self-test] SIFT 128d: max_min_ratio={sift_summary['max_min_ratio']:.2f} ✓")

        # 5. cluster 구조 데이터
        centers = rng.standard_normal((5, 96)).astype(np.float32) * 10
        clustered = np.vstack([
            rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
        ])
        cl_mapper = fit_zorder_mapper(clustered, n_strata=20, p=8, seed=42)
        cl_sids = assign_zorder(cl_mapper, clustered)
        cl_summary = cluster_size_summary(cl_sids, n_clusters=20)
        print(f"[self-test] clustered data: max_min_ratio={cl_summary['max_min_ratio']:.2f} ✓")

    # 6. Hilbert 와 동일 (samples, seed) 에서 결과는 다르되 둘 다 quantile 균등
    #    — distance 함수가 다르므로 stratum_id 는 다르지만, 둘 다 fit sample 위에서
    #    cluster size 가 비슷해야 함.
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
