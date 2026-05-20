#!/usr/bin/env python3
"""
RQ3 #13 — KD-tree partition stratification (tree-based paradigm).

Hilbert/MiniBatch/Random Projection 등은 모두 metric 또는 hash. KD-tree 는 다른
paradigm: 재귀적 axis-aligned 분할. 전통 spatial DB / k-NN 의 표준 인덱스.

알고리즘:
1. 학습 sample 의 분산이 큰 axis 선택
2. 해당 axis 의 median 기준 분할 → 2 sub-cluster
3. 각 sub-cluster 에서 재귀 (depth log2(K))
4. 최종 leaf 가 stratum

K=20 ≈ 2^4.32 → ceil(log2(K)) = 5 depth. 16 leaf 까지만 정확히 균등 — 20 으로
맞추려면 마지막 depth 에 일부 leaf 추가 분할.

본 구현은 단순화 — depth 를 ceil(log2(K)) 로 fix, 20 leaf 가 안 나오는 경우 last
level 4 leaf → 뒤 4 leaf 를 다시 분할 (median split 한 번 더).

학습 X 의미: 학습 sample 만 보고 결정. 같은 input → 같은 tree. 결정론.

Usage:
    from kdtree_partition import fit_kdtree_partition, assign_kdtree
    tree = fit_kdtree_partition(samples, n_strata=20, seed=42)
    sids = assign_kdtree(tree, full_vectors)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_K = 20
DEFAULT_SEED = 42


@dataclass
class KDNode:
    """KD-tree internal/leaf node."""
    is_leaf: bool
    leaf_id: int = -1
    axis: int = -1
    threshold: float = 0.0
    left: "KDNode | None" = None
    right: "KDNode | None" = None


@dataclass
class KDTreeMapper:
    root: KDNode
    n_strata: int

    def assign_one(self, vec: np.ndarray) -> int:
        node = self.root
        while not node.is_leaf:
            if vec[node.axis] < node.threshold:
                node = node.left
            else:
                node = node.right
        return node.leaf_id

    def assign(self, vectors: np.ndarray) -> np.ndarray:
        """Vectorized batch assignment."""
        if vectors.ndim != 2:
            raise ValueError(f"vectors must be 2D, got shape {vectors.shape}")
        n = len(vectors)
        sids = np.zeros(n, dtype=np.int32)
        # 단순 loop 구현 — n=1M 에서 ~5s, 충분히 빠름
        for i in range(n):
            sids[i] = self.assign_one(vectors[i])
        return sids


def _build_kdtree(samples: np.ndarray, target_leaves: int, leaf_id_counter: list[int]) -> KDNode:
    """재귀로 KD-tree 생성. 학습 sample 의 분산 큰 axis 의 median 기준 분할.

    target_leaves 가 1 이면 leaf, 아니면 분할.
    """
    if target_leaves <= 1 or len(samples) < 2:
        leaf_id = leaf_id_counter[0]
        leaf_id_counter[0] += 1
        return KDNode(is_leaf=True, leaf_id=leaf_id)

    # 분산 가장 큰 axis 선택
    var = samples.var(axis=0)
    axis = int(np.argmax(var))
    threshold = float(np.median(samples[:, axis]))

    left_mask = samples[:, axis] < threshold
    if left_mask.sum() == 0 or left_mask.sum() == len(samples):
        # degenerate split — 모두 한 쪽. leaf 로 fall-back.
        leaf_id = leaf_id_counter[0]
        leaf_id_counter[0] += 1
        return KDNode(is_leaf=True, leaf_id=leaf_id)

    # 분할 — left = floor(target/2), right = ceil(target/2). 균등하게.
    left_target = target_leaves // 2
    right_target = target_leaves - left_target
    left_node = _build_kdtree(samples[left_mask], left_target, leaf_id_counter)
    right_node = _build_kdtree(samples[~left_mask], right_target, leaf_id_counter)

    return KDNode(
        is_leaf=False, axis=axis, threshold=threshold,
        left=left_node, right=right_node,
    )


def fit_kdtree_partition(
    samples: np.ndarray,
    n_strata: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    **_kwargs,
) -> KDTreeMapper:
    """학습 sample 로 KD-tree 생성.

    seed 는 본질적 random 이 아니나 (median 분할 결정론), API 호환을 위해 받음.
    """
    if samples.ndim != 2:
        raise ValueError(f"samples must be 2D, got shape {samples.shape}")
    if samples.shape[0] < n_strata:
        raise ValueError(f"need >= {n_strata} samples, got {samples.shape[0]}")

    leaf_id_counter = [0]
    root = _build_kdtree(samples.astype(np.float32), n_strata, leaf_id_counter)
    actual_leaves = leaf_id_counter[0]
    if actual_leaves != n_strata:
        # degenerate split 로 인해 leaf 수가 부족할 수 있음 — 학습 sample 작거나 dim 일부 collapsed.
        # 이 경우 leaf id 를 0..(actual_leaves-1) 로 부여, n_strata 에 맞춰 재배정 X.
        # cluster_size_summary 가 일부 빈 stratum 보고함.
        pass

    return KDTreeMapper(root=root, n_strata=n_strata)


def assign_kdtree(mapper: KDTreeMapper, vectors: np.ndarray) -> np.ndarray:
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

    # 결정론
    samples = rng.standard_normal((1000, 96)).astype(np.float32)
    m1 = fit_kdtree_partition(samples, n_strata=20, seed=42)
    m2 = fit_kdtree_partition(samples, n_strata=20, seed=42)
    s1 = assign_kdtree(m1, samples)
    s2 = assign_kdtree(m2, samples)
    assert np.array_equal(s1, s2), "KD-tree must be deterministic"
    print("[self-test] determinism ✓")

    # cluster sizes — median 분할이라 ~균등
    summary = cluster_size_summary(s1, n_clusters=20)
    print(f"[self-test] iid 96d: max/min={summary['max_min_ratio']:.2f}, "
          f"counts (first 5): {summary['counts'][:5]}")
    # median split → 거의 균등

    # cluster 데이터
    centers = rng.standard_normal((5, 96)).astype(np.float32) * 5
    clustered = np.vstack([
        rng.standard_normal((400, 96)).astype(np.float32) + c for c in centers
    ])
    m_cl = fit_kdtree_partition(clustered, n_strata=20, seed=42)
    s_cl = assign_kdtree(m_cl, clustered)
    cl_summary = cluster_size_summary(s_cl, n_clusters=20)
    print(f"[self-test] clustered: max/min={cl_summary['max_min_ratio']:.2f}")

    # SIFT 128d
    sift = rng.standard_normal((500, 128)).astype(np.float32)
    m_sift = fit_kdtree_partition(sift, n_strata=20, seed=42)
    s_sift = assign_kdtree(m_sift, sift)
    assert s_sift.min() >= 0 and s_sift.max() < 20

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
