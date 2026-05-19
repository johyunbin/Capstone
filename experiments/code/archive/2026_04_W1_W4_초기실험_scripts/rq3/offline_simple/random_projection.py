#!/usr/bin/env python3
"""
RQ3 #5 — C. Random Projection stratification.

학습 X (결정론, seed 고정). numpy.random.standard_normal((dim, k=20)) 으로 projection
matrix 생성, vec @ matrix → (k=20) projection, argmax bucket 으로 stratum_id 부여.

Johnson-Lindenstrauss lemma: random projection 은 거리 분포를 근사 보존하지만,
cluster 구조는 보장 X → recovery_rate 10~40% 예측 (단순 하한, baseline 역할).

argmax 방식 채택 이유:
  - sign-based (4 bit binary code = 16 bucket) 는 K=20 과 안 맞음
  - 1-d projection + 20-quantile bin 은 정보 손실이 더 큼
  - argmax 는 단순 + 부분 이방성 보존 + K=20 고정 가능

본 모듈은 stratum_id 부여 알고리즘만 제공. 측정 골격은 rq2_alloc_python.py 그대로.

Usage:
    from random_projection import make_projection, assign_random_projection
    matrix = make_projection(dim=96, k=20, seed=42)   # DEEP
    stratum_ids = assign_random_projection(matrix, full_vectors)
"""
from __future__ import annotations

import numpy as np

DEFAULT_K = 20
DEFAULT_SEED = 42


def make_projection(dim: int, k: int = DEFAULT_K, seed: int = DEFAULT_SEED) -> np.ndarray:
    """결정론적 random projection matrix.

    Gaussian iid N(0, 1/k) — JL preserve 거리, scale 1/sqrt(k) 로 norm 안정.
    같은 seed 면 항상 동일 matrix → 측정 reproducibility 보장.

    반환 shape: (dim, k) float32.
    """
    rng = np.random.default_rng(seed)
    matrix = rng.standard_normal((dim, k)).astype(np.float32) / np.sqrt(k)
    return matrix


def assign_random_projection(matrix: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """argmax(vec @ matrix) 로 stratum_id 부여.

    vectors: (N, dim) float
    matrix:  (dim, k) float — make_projection 출력
    반환:    (N,) int32 — 각 row 의 stratum_id (0~k-1)
    """
    if vectors.ndim != 2:
        raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
    if vectors.shape[1] != matrix.shape[0]:
        raise ValueError(
            f"dim mismatch: vectors {vectors.shape}, matrix {matrix.shape}"
        )
    projected = vectors @ matrix              # (N, k)
    return np.argmax(projected, axis=1).astype(np.int32)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    """argmax bucket 분포 균질성 sanity check.

    Random projection argmax 는 unbalanced 가능 (예: 가장 큰 dimension 으로 쏠림).
    KM20 oracle 의 균질 cluster 와 다른 분포가 자연스러움.
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
    """toy 검증 — Gaussian iid 데이터에서 K-bucket 부여 + reproducibility."""
    rng = np.random.default_rng(0)
    vectors = rng.standard_normal((1000, 96)).astype(np.float32)

    # 결정론 확인
    m1 = make_projection(dim=96, k=20, seed=42)
    m2 = make_projection(dim=96, k=20, seed=42)
    assert np.allclose(m1, m2), "make_projection must be deterministic for fixed seed"

    sids = assign_random_projection(m1, vectors)
    summary = cluster_size_summary(sids, n_clusters=20)
    print(f"[self-test] bucket sizes: min={summary['min']} max={summary['max']} "
          f"mean={summary['mean']:.1f} std={summary['std']:.1f} "
          f"max_min_ratio={summary['max_min_ratio']:.2f}")
    print(f"[self-test] counts: {summary['counts']}")
    assert sids.shape == (1000,), f"unexpected shape {sids.shape}"
    assert sids.min() >= 0 and sids.max() < 20, "stratum_id out of range"
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
