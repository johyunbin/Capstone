#!/usr/bin/env python3
"""
RQ3 #14 — Product Quantization (PQ) stratification.

FAISS / 벡터 DB 산업의 표준 indexing 기법. 96d/128d vector 를 M 개 sub-vector 로
분할 (예: 4×24d for DEEP, 4×32d for SIFT) → 각 sub-vector 를 K_sub centroid 로
quantize → composite code.

본 연구의 stratification 적용:
  - sub-vector 4 개 × K_sub=2 (4×2=8 codes 만으로 too few)
  - 또는 sub-vector 2 개 × K_sub=√K = sqrt(20) ≈ 5 (5*5=25, K=20 으로 truncate)
  - 또는 단일 PQ 로 K=20 centroid (= MiniBatch K=20 과 비슷, 의미 약)
  - 본 구현: M=2 sub-vector × K_sub=N_sub centroid → cluster id = pq[0]*N_sub + pq[1]
    N_sub=5 면 25, N_sub=4 면 16 (K=16 으로 truncate or pad). N_strata=20 으로
    맞추기 위해 N_sub=5 + 일부 truncate.

가설 H3-PQ:
  - PQ 가 MiniBatch (#8) 보다 약 — sub-vector 마다 독립 KMeans 라 cross-axis 정보 손실.
  - 그러나 RANDOM20 보다 우수 — sub-vector 별 cluster 구조 보존.
  - 산업 기준 미비교 약점 보강 (FAISS narrative).

학습: M 번의 KMeans (M=2) — 빠름 (~수초).

Usage:
    from product_quantization import fit_pq_mapper, assign_pq
    mapper = fit_pq_mapper(samples, n_strata=20, m=2, seed=42)
    sids = assign_pq(mapper, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import MiniBatchKMeans

DEFAULT_K = 20
DEFAULT_M = 2  # sub-vector 수
DEFAULT_SEED = 42


@dataclass
class PQMapper:
    """M 개의 sub-PQ centroid (각 K_sub centroid)."""
    sub_models: list[MiniBatchKMeans]
    sub_dim: int
    m: int
    k_sub: int
    n_strata: int   # 실제 부여 stratum 수 (K_sub^M 또는 truncated)

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        n = len(vectors)
        # 각 sub-vector 의 cluster id 측정
        composite = np.zeros(n, dtype=np.int64)
        for j in range(self.m):
            sub_vec = vectors[:, j * self.sub_dim:(j + 1) * self.sub_dim]
            sub_id = self.sub_models[j].predict(sub_vec)
            composite = composite * self.k_sub + sub_id
        # composite ∈ [0, k_sub^m). n_strata 로 truncate (mod).
        return (composite % self.n_strata).astype(np.int32)


def fit_pq_mapper(
    samples: np.ndarray,
    n_strata: int = DEFAULT_K,
    m: int = DEFAULT_M,
    seed: int = DEFAULT_SEED,
    **_kwargs,
) -> PQMapper:
    """M sub-vector 분할 + 각 sub-vector 에 KMeans 학습.

    K_sub = ceil(n_strata^(1/M)). M=2, K=20 → K_sub=5 (5^2=25, 20 으로 mod truncate).

    sub-vector 간 동일 K_sub 가정 (대부분 PQ 구현 표준).
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[1] % m != 0:
        # 마지막 sub-vector 가 짧아지는 경우 — 단순화 위해 trim.
        # DEEP 96d (m=2) → 48 each, SIFT 128d (m=2) → 64 each. 모두 짝수.
        raise ValueError(f"dim {samples.shape[1]} not divisible by m={m}. "
                          "현재 구현은 균등 sub-vector 만 지원.")

    sub_dim = samples.shape[1] // m
    k_sub = int(np.ceil(n_strata ** (1.0 / m)))

    sub_models = []
    for j in range(m):
        sub_vec = samples[:, j * sub_dim:(j + 1) * sub_dim]
        if sub_vec.shape[0] < k_sub:
            raise ValueError(f"sub-vector {j} samples {sub_vec.shape[0]} < k_sub {k_sub}")
        model = MiniBatchKMeans(
            n_clusters=k_sub, random_state=seed + j,
            batch_size=1024, n_init=3, max_iter=100,
        )
        model.fit(sub_vec)
        sub_models.append(model)

    return PQMapper(
        sub_models=sub_models, sub_dim=sub_dim, m=m, k_sub=k_sub, n_strata=n_strata,
    )


def assign_pq(mapper: PQMapper, vectors: np.ndarray) -> np.ndarray:
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
    rng = np.random.default_rng(0)

    # 96d 동작 (DEEP) — m=2, sub_dim=48
    samples = rng.standard_normal((1000, 96)).astype(np.float32)
    m1 = fit_pq_mapper(samples, n_strata=20, m=2, seed=42)
    m2 = fit_pq_mapper(samples, n_strata=20, m=2, seed=42)
    s1 = assign_pq(m1, samples)
    s2 = assign_pq(m2, samples)
    assert np.array_equal(s1, s2), "PQ must be deterministic"
    print(f"[self-test] determinism ✓ — m={m1.m}, k_sub={m1.k_sub}, n_strata={m1.n_strata}")

    summary = cluster_size_summary(s1, n_clusters=20)
    print(f"[self-test] iid 96d: max/min={summary['max_min_ratio']:.2f}, counts={summary['counts'][:5]}")
    assert s1.min() >= 0 and s1.max() < 20

    # 128d (SIFT) — m=2, sub_dim=64
    sift = rng.standard_normal((1000, 128)).astype(np.float32)
    m_sift = fit_pq_mapper(sift, n_strata=20, m=2, seed=42)
    s_sift = assign_pq(m_sift, sift)
    sift_summary = cluster_size_summary(s_sift, n_clusters=20)
    print(f"[self-test] SIFT 128d: max/min={sift_summary['max_min_ratio']:.2f}")
    assert s_sift.min() >= 0 and s_sift.max() < 20

    # cluster 데이터
    centers = rng.standard_normal((5, 96)).astype(np.float32) * 5
    clustered = np.vstack([
        rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
    ])
    m_cl = fit_pq_mapper(clustered, n_strata=20, m=2, seed=42)
    s_cl = assign_pq(m_cl, clustered)
    cl_summary = cluster_size_summary(s_cl, n_clusters=20)
    print(f"[self-test] clustered: max/min={cl_summary['max_min_ratio']:.2f}")

    # m=4 (4 sub-vector × k_sub=3, 81 → mod 20)
    m4 = fit_pq_mapper(samples, n_strata=20, m=4, seed=42)
    s4 = assign_pq(m4, samples)
    print(f"[self-test] m=4: k_sub={m4.k_sub}, sids range [{s4.min()}, {s4.max()}]")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
