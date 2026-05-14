#!/usr/bin/env python3
"""
RQ3 #8b — MiniBatch K-means online (partial_fit) variant.

배치 학습 MiniBatch (#8) 의 online 버전. sklearn 의 MiniBatchKMeans.partial_fit() 으로
chunk 단위 점진 학습 → centroid 가 stream 데이터에 적응. OLTP / streaming 시나리오에서
batch 재학습 없이 운영 가능 한지 측정 (5/5 박세은 의문 직결: "데이터 점진 도착 시").

본 연구의 contribution narrative 와의 관계:
  - 현재 KM20 oracle / MiniBatch (#8): 사전 batch 학습 → production 한계 (OLTP).
  - partial_fit 은 batch 의 production 한계 *어떻게 해소되는지* 정량.
  - 가설 H3-Fp: chunk 별 partial_fit 으로 학습 시 batch-fit MiniBatch (#8) 대비
    recovery 5~15%p loss (chunk noise + non-stationary catch-up). 이 loss 가
    제한적이면 production 의 partial_fit 채택 정당화.

설계:
  - chunk_size 1000 (작은 chunk → 빈번 update, OLTP 와 가까움).
  - n_chunks: learn_samples 를 chunk_size 로 나눈 수.
  - reassignment_ratio=0.01 (sklearn default, 소량 cluster 재할당 활성).

OLTP narrative 답변:
  - 점진 도착 → 매 1K row 마다 partial_fit() 호출 (10ms~). batch 재학습 X.
  - cluster center 변화량 모니터링 (drift_metric) → threshold 초과 시 alert.
  - 본 모듈은 partial_fit + drift_metric 측정만 담당. 측정 / drift trigger 로직은
    wrapper (run_minibatch_partial.py) 에서.

Usage:
    from minibatch_partial import train_minibatch_partial, assign_minibatch
    model = train_minibatch_partial(samples, n_clusters=20, chunk_size=1000)
    sids = assign_minibatch(model, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import MiniBatchKMeans

DEFAULT_K = 20
DEFAULT_CHUNK = 1000
DEFAULT_SEED = 42
DEFAULT_BATCH = 1024


@dataclass
class PartialFitResult:
    """학습 진행 통계 (drift 분석용)."""
    model: MiniBatchKMeans
    n_chunks: int
    chunk_size: int
    inertia_per_chunk: list[float]
    centroid_shift_per_chunk: list[float]   # ‖prev - curr centroid‖ 평균


def train_minibatch_partial(
    samples: np.ndarray,
    n_clusters: int = DEFAULT_K,
    chunk_size: int = DEFAULT_CHUNK,
    random_state: int = DEFAULT_SEED,
    batch_size: int = DEFAULT_BATCH,
    init_warmup: int | None = None,
) -> PartialFitResult:
    """sample 을 chunk 로 나눠 partial_fit 점진 학습.

    Args:
        samples: (N, dim) — full sample 또는 stream simulator. 본 함수 시점에선
            모두 메모리에 있다고 가정 (실 OLTP 는 stream 으로 도착하지만 측정은
            동일 분포의 batch).
        chunk_size: 각 partial_fit 호출당 row 수. 작을수록 OLTP-like.
        init_warmup: 첫 partial_fit 전 fit() 으로 init centroid 고정. None 이면
            chunk_size * 2 만큼 warmup. partial_fit 만으로 시작 시 처음 N_chunks
            동안 centroid 가 매우 unstable.

    Returns:
        PartialFitResult — model + per-chunk inertia + centroid shift 추이.
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[0] < n_clusters * 2:
        raise ValueError(f"need >= {n_clusters * 2} samples, got {samples.shape[0]}")

    n = len(samples)
    rng = np.random.default_rng(random_state)
    perm = rng.permutation(n)  # stream order — 실 환경엔 도착 순서, 여기선 random
    samples = samples[perm]

    model = MiniBatchKMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        batch_size=batch_size,
        n_init=1,
        max_iter=10,
        reassignment_ratio=0.01,
    )

    # init_warmup: 첫 chunk 부분으로 fit 한 번 → centroid 안정화.
    warmup = init_warmup if init_warmup is not None else min(chunk_size * 2, n)
    warmup = max(warmup, n_clusters * 2)
    model.fit(samples[:warmup])

    inertias: list[float] = [float(model.inertia_)]
    shifts: list[float] = [0.0]

    cursor = warmup
    n_chunks = 0
    while cursor < n:
        end = min(cursor + chunk_size, n)
        chunk = samples[cursor:end]
        prev_centers = model.cluster_centers_.copy()
        model.partial_fit(chunk)
        # drift: 평균 centroid shift (각 cluster 의 L2 변위 평균)
        shift = float(np.linalg.norm(model.cluster_centers_ - prev_centers, axis=1).mean())
        inertias.append(float(model.inertia_))
        shifts.append(shift)
        cursor = end
        n_chunks += 1

    return PartialFitResult(
        model=model,
        n_chunks=n_chunks,
        chunk_size=chunk_size,
        inertia_per_chunk=inertias,
        centroid_shift_per_chunk=shifts,
    )


def assign_minibatch(model_or_result, vectors: np.ndarray) -> np.ndarray:
    """PartialFitResult 또는 MiniBatchKMeans 모두 수용 (caller 단순화).

    run_8m_sensitivity 의 dispatch 에서는 fit_fn 이 mapper 객체를 반환하므로
    PartialFitResult 받도록 통일.
    """
    if isinstance(model_or_result, PartialFitResult):
        model = model_or_result.model
    else:
        model = model_or_result
    if vectors.ndim != 2:
        raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
    return model.predict(vectors).astype(np.int32)


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


def drift_summary(result: PartialFitResult) -> dict:
    """centroid drift 요약 — partial_fit 후반 안정화 검증."""
    shifts = np.array(result.centroid_shift_per_chunk[1:])  # 0번 0 제외
    if len(shifts) == 0:
        return {"n_chunks": 0}
    # 전반 (첫 절반) vs 후반 (마지막 절반) 비교 — 후반 shift 작아야 안정화.
    half = len(shifts) // 2
    early = shifts[:half] if half > 0 else shifts[:1]
    late = shifts[half:] if half > 0 else shifts
    return {
        "n_chunks": result.n_chunks,
        "shift_early_mean": float(early.mean()),
        "shift_late_mean": float(late.mean()),
        "shift_decay_ratio": float(late.mean() / max(early.mean(), 1e-9)),
        # < 1.0 → 안정화 (후반 shift 가 전반보다 작음).
        "final_inertia": result.inertia_per_chunk[-1],
        "init_inertia": result.inertia_per_chunk[0],
    }


def _self_test():
    rng = np.random.default_rng(0)

    # 1. 결정론 확인 (같은 seed → 같은 model)
    samples = rng.standard_normal((5000, 96)).astype(np.float32)
    r1 = train_minibatch_partial(samples, n_clusters=20, chunk_size=500, random_state=42)
    r2 = train_minibatch_partial(samples, n_clusters=20, chunk_size=500, random_state=42)
    s1 = assign_minibatch(r1, samples)
    s2 = assign_minibatch(r2, samples)
    assert np.array_equal(s1, s2), "partial_fit must be deterministic for fixed seed"
    print(f"[self-test] determinism ✓ — n_chunks={r1.n_chunks}, chunk_size={r1.chunk_size}")

    # 2. drift 분석
    drift = drift_summary(r1)
    print(f"[self-test] drift summary:")
    print(f"  n_chunks={drift['n_chunks']}")
    print(f"  shift_early_mean={drift['shift_early_mean']:.4f}, "
          f"shift_late_mean={drift['shift_late_mean']:.4f}")
    print(f"  shift_decay_ratio={drift['shift_decay_ratio']:.3f} (< 1.0 → 안정화)")
    print(f"  inertia: init={drift['init_inertia']:.1f} → "
          f"final={drift['final_inertia']:.1f}")
    # iid 데이터 → centroid drift 가 후반에 약화되어야 (decay < 1)
    # 단 shift_late_mean 자체는 0 이 아닐 수 있음 (continuous update).

    # 3. cluster size 분포
    summary = cluster_size_summary(s1, n_clusters=20)
    print(f"[self-test] cluster sizes: min={summary['min']}, max={summary['max']}, "
          f"max/min={summary['max_min_ratio']:.2f}")
    assert summary["min"] > 0, "all 20 clusters should have at least 1 sample"

    # 4. clustered 데이터에서 partial_fit 가 batch fit 과 비슷한 결과 내는지
    centers = rng.standard_normal((10, 96)).astype(np.float32) * 5
    clustered = np.vstack([
        rng.standard_normal((500, 96)).astype(np.float32) + c for c in centers
    ])
    rng.shuffle(clustered)
    r_cl = train_minibatch_partial(clustered, n_clusters=20, chunk_size=500, random_state=42)
    s_cl = assign_minibatch(r_cl, clustered)
    cl_summary = cluster_size_summary(s_cl, n_clusters=20)
    cl_drift = drift_summary(r_cl)
    print(f"[self-test] clustered: max/min={cl_summary['max_min_ratio']:.2f}, "
          f"shift_decay={cl_drift['shift_decay_ratio']:.3f}")

    # 5. predict 가 (3000,) shape 으로 나오는지
    new_vecs = rng.standard_normal((3000, 96)).astype(np.float32)
    new_sids = assign_minibatch(r1, new_vecs)
    assert new_sids.shape == (3000,)
    assert new_sids.min() >= 0 and new_sids.max() < 20
    print(f"[self-test] new vec assignment: 3000 vecs, sid range "
          f"[{new_sids.min()}, {new_sids.max()}] ✓")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
