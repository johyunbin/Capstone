#!/usr/bin/env python3
"""
RQ3 #6 — A. LSH (Locality-Sensitive Hashing) Random Hyperplane stratification.

학습 X (결정론, seed 고정). 5 random hyperplanes 로 cosine LSH (Charikar 2002):
  vec → 5 sign bits → raw_id ∈ [0, 32) → mod k=20 → stratum_id ∈ [0, 20).

ceil(log2(20)) = 5 hyperplanes. raw 32 bucket 을 mod 20 으로 매핑하므로 buckets
0~11 은 2 raw bucket 의 합집합 (≈2x density), 12~19 는 1 raw bucket. 자연스러운
LSH 의 imbalance + mod collision → max_min_ratio 2~5 예상 (HT estimator 의 N_i
weighting 으로 보정).

LSH 의 동기:
  - cosine similarity preservation: P(같은 bucket) ≈ 1 - θ/π (Charikar)
  - random projection (#5 C) 와 차이: argmax 1개 vs sign 다수 → 더 fine-grained
  - 학습 데이터 의존성 X — 모든 dim 에서 동일하게 작동, distribution-agnostic

본 모듈은 stratum_id 부여 알고리즘만 제공. 측정 골격은 rq2_alloc_python.py 그대로.

Usage:
    from lsh import make_hyperplanes, assign_lsh
    W = make_hyperplanes(dim=96, k=20, seed=42)        # DEEP
    stratum_ids = assign_lsh(W, full_vectors, k=20)    # (N,) int32 in [0, 20)
"""
from __future__ import annotations

import numpy as np

DEFAULT_K = 20
DEFAULT_SEED = 42


def make_hyperplanes(dim: int, k: int = DEFAULT_K, seed: int = DEFAULT_SEED) -> np.ndarray:
    """결정론적 Random Gaussian hyperplanes (cosine LSH, Charikar 2002).

    n_hp = ceil(log2(k)) — k=20 → 5 hyperplanes (2^5 = 32 raw buckets, mod k 로 축소).
    같은 seed 면 항상 동일 matrix → 측정 reproducibility 보장.

    반환 shape: (n_hp, dim) float32.
    """
    if k < 2:
        raise ValueError(f"k must be >= 2, got {k}")
    n_hp = int(np.ceil(np.log2(k)))
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_hp, dim)).astype(np.float32)


def assign_lsh(hyperplanes: np.ndarray, vectors: np.ndarray, k: int = DEFAULT_K) -> np.ndarray:
    """sign(W·v) bits → raw_id → mod k 로 stratum_id 부여.

    vectors: (N, dim) float
    hyperplanes: (n_hp, dim) float — make_hyperplanes 출력
    반환: (N,) int32 — 각 row 의 stratum_id (0 ~ k-1)
    """
    if vectors.ndim != 2:
        raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
    if vectors.shape[1] != hyperplanes.shape[1]:
        raise ValueError(
            f"dim mismatch: vectors {vectors.shape}, hyperplanes {hyperplanes.shape}"
        )
    n_hp = hyperplanes.shape[0]
    proj = vectors @ hyperplanes.T                      # (N, n_hp)
    bits = (proj > 0).astype(np.int32)                  # (N, n_hp)
    weights = (1 << np.arange(n_hp)).astype(np.int32)   # [1, 2, 4, 8, 16]
    raw_ids = (bits * weights).sum(axis=1)              # 0 ~ 2^n_hp - 1
    return (raw_ids % k).astype(np.int32)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    """LSH bucket 분포 sanity check.

    mod 20 collision 으로 buckets 0~11 이 12~19 의 ≈2x density (uniform 입력 기준).
    실제 embedding 은 isotropy 가 깨져 있어 추가 imbalance 발생 가능.
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
    """toy 검증 — 결정론 + bucket 범위 + mod 20 collision 패턴 + 다중 dim."""
    import warnings

    # 1. 결정론
    W1 = make_hyperplanes(dim=96, k=20, seed=42)
    W2 = make_hyperplanes(dim=96, k=20, seed=42)
    assert np.allclose(W1, W2), "make_hyperplanes must be deterministic for fixed seed"
    assert W1.shape == (5, 96), f"expect (5,96), got {W1.shape}"
    assert W1.dtype == np.float32
    print(f"[self-test] determinism (seed=42, dim=96) ✓ shape={W1.shape}")

    # 2. ceil(log2) 다양한 k
    for k_test, expect_hp in [(20, 5), (16, 4), (32, 5), (33, 6)]:
        W_k = make_hyperplanes(dim=96, k=k_test, seed=42)
        assert W_k.shape[0] == expect_hp, f"k={k_test} should give {expect_hp} hp, got {W_k.shape[0]}"
    print("[self-test] n_hp = ceil(log2(k)) for k ∈ {20,16,32,33} ✓")

    with warnings.catch_warnings():
        # standard_normal 큰 dim 에서 matmul intermediate overflow warning 무해 (sign 만 사용)
        warnings.simplefilter("ignore", category=RuntimeWarning)

        # 3. bucket id range + 분포
        rng = np.random.default_rng(0)
        vectors = rng.standard_normal((10000, 96)).astype(np.float32)
        sids = assign_lsh(W1, vectors, k=20)
        assert sids.shape == (10000,)
        assert sids.dtype == np.int32
        assert sids.min() >= 0 and sids.max() < 20, f"out of range: [{sids.min()}, {sids.max()}]"
        summary = cluster_size_summary(sids, n_clusters=20)
        print(f"[self-test] 96d 10k vecs: min={summary['min']} max={summary['max']} "
              f"mean={summary['mean']:.1f} std={summary['std']:.1f} "
              f"max_min_ratio={summary['max_min_ratio']:.2f}")

        # 4. mod 20 collision check — bucket 0~11 이 12~19 보다 평균 ~2x 높아야 함
        counts = np.array(summary["counts"])
        ratio_low_high = counts[:12].mean() / counts[12:].mean()
        print(f"[self-test] avg(buckets 0-11) / avg(buckets 12-19) = {ratio_low_high:.2f} "
              f"(expect ~2 from mod 20 collision)")
        assert 1.5 < ratio_low_high < 3.0, f"mod collision ratio off: {ratio_low_high:.2f}"

        # 5. SIFT 128d 도 동작
        W_sift = make_hyperplanes(dim=128, k=20, seed=42)
        sift_vecs = rng.standard_normal((5000, 128)).astype(np.float32)
        sift_sids = assign_lsh(W_sift, sift_vecs, k=20)
        sift_sum = cluster_size_summary(sift_sids, n_clusters=20)
        print(f"[self-test] SIFT 128d: max_min_ratio={sift_sum['max_min_ratio']:.2f} ✓")

        # 6. unseen vec 도 정상 부여
        new_vecs = rng.standard_normal((300, 96)).astype(np.float32)
        new_sids = assign_lsh(W1, new_vecs, k=20)
        assert new_sids.shape == (300,)
        assert new_sids.min() >= 0 and new_sids.max() < 20
        print(f"[self-test] new vec assignment: 300 vecs, sid range "
              f"[{new_sids.min()}, {new_sids.max()}] ✓")

        # 7. dim mismatch 에러
        try:
            assign_lsh(W1, rng.standard_normal((10, 64)).astype(np.float32))
            assert False, "should have raised dim mismatch"
        except ValueError as e:
            assert "dim mismatch" in str(e)
        print("[self-test] dim mismatch → ValueError ✓")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
