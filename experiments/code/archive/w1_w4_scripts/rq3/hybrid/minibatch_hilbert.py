#!/usr/bin/env python3
"""
RQ3 #12 — MiniBatch + Hilbert hybrid stratification.

설계 동기:
  - MiniBatch K-means (#8): 자연 cluster 발견 가능, 그러나 cluster size unequal
    (DEEP max/min 2.45×, SIFT max/min 4.77×). Equal allocation 시 큰 cluster 의
    표본률이 작은 cluster 보다 낮아 estimator variance 비대칭.
  - Hilbert curve (#7): PCA 2D 의 quantile 분할로 size 균등 (max/min ≈ 1.16),
    그러나 cluster 구조 무시 (PCA 가 dominant axis 만 살림).
  - Hybrid: 외부 MiniBatch (k_outer) → 각 cluster 내부에서 Hilbert (k_inner) 로
    동일 크기 sub-strata 분할. 결과 k_outer × k_inner = N_STRATA.
    → cluster-aware (외부 KMeans) AND size-balanced (내부 quantile).

가설 H3-FH (hybrid):
  - 만약 MiniBatch (-1.88%, -1.97%) 와 Hilbert (-1.78%, -2.47%) 가 각각 부분 효과
    를 보이고 hybrid 가 이를 합산하면 → recovery method_minus_bern_pct 가 두 단일
    method 의 평균 또는 그 이상 (-2.0%~-3.0%) 기대.
  - 만약 hybrid 가 단일 method 와 비슷 → 두 method 가 동일 정보를 다른 방식으로
    포착하는 것 (정보 redundant). 그래도 sensitivity check.
  - 만약 hybrid 가 더 나쁘면 → cluster size 변동 자체가 estimator 에 도움이 됨
    (Neyman 처럼) — 본 연구의 contribution narrative 보강.

Usage:
    from minibatch_hilbert import fit_hybrid_mapper, assign_hybrid
    mapper = fit_hybrid_mapper(samples, k_outer=5, k_inner=4, seed=42)
    stratum_ids = assign_hybrid(mapper, all_vectors)  # ids ∈ [0, k_outer*k_inner)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.cluster import MiniBatchKMeans

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hilbert.hilbert_curve import HilbertMapper, fit_hilbert_mapper, assign_hilbert  # noqa: E402

DEFAULT_K_OUTER = 5
DEFAULT_K_INNER = 4
DEFAULT_K = DEFAULT_K_OUTER * DEFAULT_K_INNER  # 20 — N_STRATA 와 일치
DEFAULT_SEED = 42
DEFAULT_P = 10


@dataclass
class HybridMapper:
    """outer MiniBatch model + per-cluster inner Hilbert mappers."""
    outer_model: MiniBatchKMeans
    inner_mappers: list[HilbertMapper]   # length = k_outer
    k_outer: int
    k_inner: int

    @property
    def n_strata(self) -> int:
        return self.k_outer * self.k_inner

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        """outer cluster_id × k_inner + inner_hilbert_id → 0..(k_outer*k_inner-1)."""
        outer_ids = self.outer_model.predict(vectors).astype(np.int32)
        sids = np.zeros(len(vectors), dtype=np.int32)
        for o in range(self.k_outer):
            mask = outer_ids == o
            if not mask.any():
                continue
            inner_ids = self.inner_mappers[o].assign(vectors[mask])
            sids[mask] = o * self.k_inner + inner_ids
        return sids


def fit_hybrid_mapper(
    samples: np.ndarray,
    k_outer: int = DEFAULT_K_OUTER,
    k_inner: int = DEFAULT_K_INNER,
    p: int = DEFAULT_P,
    seed: int = DEFAULT_SEED,
    # 호환성: caller 가 n_strata 만 주는 경우 (run_method_measurement 패턴).
    # n_strata = k_outer * k_inner 이라 가정. 5*4=20 default.
    n_strata: int | None = None,
    **_kwargs,  # caller 가 추가 kw 를 pass 할 때 무시
) -> HybridMapper:
    """outer MiniBatch + per-cluster inner Hilbert.

    Args:
        samples: 학습 sample (N, dim).
        k_outer/k_inner: 분할 깊이. 기본 5×4=20 (N_STRATA 와 일치).
        n_strata: 전체 strata 수. 주어지면 k_outer*k_inner 와 일치 검증 (호환).
        p: Hilbert grid order.
        seed: 결정론.

    Returns:
        HybridMapper.
    """
    if n_strata is not None and n_strata != k_outer * k_inner:
        # n_strata 만 주어지면 약수 분해 — 가장 균형잡힌 (k_outer ≤ k_inner) 쌍
        for ko in range(int(np.sqrt(n_strata)), 0, -1):
            if n_strata % ko == 0:
                k_outer = ko
                k_inner = n_strata // ko
                break
    if samples.shape[0] < k_outer * 50:
        raise ValueError(f"need >= {k_outer * 50} samples for outer MiniBatch, got {samples.shape[0]}")

    outer_model = MiniBatchKMeans(
        n_clusters=k_outer, random_state=seed, batch_size=1024, n_init=3, max_iter=100,
    )
    outer_model.fit(samples)
    outer_ids = outer_model.predict(samples)

    inner_mappers: list[HilbertMapper] = []
    for o in range(k_outer):
        mask = outer_ids == o
        cluster_samples = samples[mask]
        if len(cluster_samples) < k_inner:
            # 작은 cluster — 학습 sample 에서 충분한 데이터 확보 못 함.
            # cluster 내 모두 한 stratum 으로 (degenerate) → 첫 inner stratum 만 생성.
            # 실측 시 거의 발생 X (outer 5-cluster 면 각 ~2K rows).
            cluster_samples = samples  # fallback: 전체 sample 로 fit (의미는 약하나 안전)
        inner_mappers.append(fit_hilbert_mapper(
            cluster_samples, n_strata=k_inner, p=p, seed=seed + o,
        ))

    return HybridMapper(
        outer_model=outer_model,
        inner_mappers=inner_mappers,
        k_outer=k_outer,
        k_inner=k_inner,
    )


def assign_hybrid(mapper: HybridMapper, vectors: np.ndarray) -> np.ndarray:
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

    # 1. 기본 결정론
    samples = rng.standard_normal((1000, 96)).astype(np.float32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        m1 = fit_hybrid_mapper(samples, k_outer=5, k_inner=4, seed=42)
        m2 = fit_hybrid_mapper(samples, k_outer=5, k_inner=4, seed=42)
        s1 = assign_hybrid(m1, samples)
        s2 = assign_hybrid(m2, samples)
        assert np.array_equal(s1, s2), "Hybrid mapper must be deterministic"
        print("[self-test] determinism ✓")

        # 2. stratum 범위 [0, 20)
        assert s1.min() >= 0 and s1.max() < 20, f"sids range {s1.min()}-{s1.max()}"
        summary = cluster_size_summary(s1, n_clusters=20)
        print(f"[self-test] gaussian iid: max/min={summary['max_min_ratio']:.2f}, counts={summary['counts']}")

        # 3. cluster 구조 데이터 — outer KMeans 가 자연 cluster 5개 발견하기 기대
        centers = rng.standard_normal((5, 96)).astype(np.float32) * 10
        clustered = np.vstack([
            rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
        ])
        m_cl = fit_hybrid_mapper(clustered, k_outer=5, k_inner=4, seed=42)
        s_cl = assign_hybrid(m_cl, clustered)
        cl_summary = cluster_size_summary(s_cl, n_clusters=20)
        print(f"[self-test] clustered (5 gaussians): max/min={cl_summary['max_min_ratio']:.2f}")
        # 5 outer × 4 inner — 자연 cluster 가 잘 잡혀야 max/min 작음

        # 4. n_strata=20 호환 인터페이스 (caller 가 fit_hybrid_mapper(..., n_strata=20))
        m_compat = fit_hybrid_mapper(clustered, n_strata=20, seed=42)
        assert m_compat.n_strata == 20

        # 5. SIFT 128d 동작
        sift = rng.standard_normal((1500, 128)).astype(np.float32)
        m_sift = fit_hybrid_mapper(sift, k_outer=5, k_inner=4, seed=42)
        s_sift = assign_hybrid(m_sift, sift)
        assert s_sift.min() >= 0 and s_sift.max() < 20
        print(f"[self-test] SIFT 128d: max sid {s_sift.max()} ✓")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
