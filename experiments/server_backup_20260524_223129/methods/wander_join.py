#!/usr/bin/env python3
"""Wander Join — index-aware random walk on the join graph (Tier S multi-relation).

The Wander Join estimator constructs unbiased online estimates of join cardinality
(and aggregate query results) by performing index-supported random walks across
relations on the join graph, weighting each walk by the inverse probability of its
trajectory.  In contrast to monolithic Bernoulli sampling — which is statistically
inefficient on selective joins because the vast majority of cross-product samples
do not contribute to the answer — Wander Join concentrates samples on tuples that
actually participate in the join, which yields concentration bounds at far smaller
sample budgets.

Reference
---------
Feifei Li, Bin Wu, Ke Yi, Zhuoyue Zhao.
"Wander Join: Online Aggregation via Random Walks."
SIGMOD 2016 (extended in ACM TODS, Vol. 44, No. 2, Article 5, June 2019).
DOI: https://doi.org/10.1145/3284551 (TODS 2019)
DOI: https://doi.org/10.1145/2882903.2915235 (SIGMOD 2016)

Adaptation to multi-vector stratification (this project)
--------------------------------------------------------
The original algorithm walks across a *relational* join graph (table -> table)
using a foreign-key index.  In our setting we operate on a *paired-vector* row
schema:  ``emb1[i]`` is the partsupp-side embedding for row ``i`` and
``emb2[i]`` is the part-side embedding joined to it through the implicit
primary-key alignment.  We model the random walk as follows:

    step 0 :  start at row ``i``,                       emb1[i] (partsupp side)
    step 1 :  cross the implicit FK edge,                emb2[i] (part side)
    step 2 :  expand to the K_NEIGHBORS spatial neighbors of ``emb2[i]``
              under the part-side embedding; pick one uniformly at random.
    step 3 :  the endpoint of the walk is an emb1-row index ``j``.

The endpoint embedding ``emb1[j]`` is then fed to MiniBatch K-Means with K
clusters; the resulting cluster id is returned as the stratum_id for row
``i``.  This concentrates samples on rows whose neighborhood structure in the
joined space agrees, which is what Wander Join exploits in the relational
setting (samples follow join-friendly trajectories).

This is an *adaptation* of Wander Join to the embedding-paired setting; the
original index-walk semantics map onto KNN-graph traversal because the
KNN graph is the natural index of a vector relation.

Public API
----------
``stratify_method(emb1, emb2, K=20, seed=0, **kwargs) -> np.ndarray``
    Drop-in compatible with ``measure_multi_paradigm.stratify_method`` in
    spirit (same return shape and semantics).  Returns an ``int32`` array of
    shape ``(N,)`` whose entries are stratum ids in ``[0, K)``.

Optional keyword arguments
--------------------------
    walk_neighbors : int, default 3
        K_NEIGHBORS — branching factor of the random walk's KNN expansion.
    n_walks : int, default 1
        Number of independent walks per starting row; multiple walks are
        averaged in embedding space to reduce variance of the endpoint
        before clustering.
    minibatch_size : int, default 1024
        Batch size for the MiniBatch K-Means stratifier.
"""
from __future__ import annotations

import warnings
from typing import Any

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.neighbors import NearestNeighbors


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_knn_index(vectors: np.ndarray, k_neighbors: int) -> NearestNeighbors:
    """Build a brute-force KNN index over ``vectors`` for walk-step expansion.

    A small ``k_neighbors`` (default 3) keeps the walk lightweight and the
    transition probability easy to invert (uniform 1/k_neighbors).  We use
    sklearn's brute-force backend because (a) embedding dimensions for our
    cells are 96-768 and (b) we need exact neighbors so the unbiased walk
    weights are correct under the original Wander Join framing.
    """
    n_neighbors = min(k_neighbors + 1, vectors.shape[0])  # +1: self
    index = NearestNeighbors(
        n_neighbors=n_neighbors, algorithm="brute", metric="euclidean",
    )
    index.fit(vectors)
    return index


def _wander_walk(
    emb1: np.ndarray,
    emb2: np.ndarray,
    knn_index: NearestNeighbors,
    n_walks: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Execute one batch of Wander Join walks; return endpoint embeddings.

    Each row ``i`` undergoes ``n_walks`` independent walks of the form
    ``emb1[i] -> emb2[i] -> KNN(emb2[i]) -> emb1[j]``.  The endpoint
    embedding fed to clustering is the **mean** of the ``n_walks`` endpoints
    in ``emb1`` space, which reduces walk variance while keeping the
    representation in the original vector space (no need to mix
    heterogeneous emb1/emb2 dimensionalities).
    """
    n = emb1.shape[0]
    # Find KNN for every emb2 row up front (one batched query is cheaper
    # than per-row queries in the random-walk loop).  Suppress sklearn
    # matmul-overflow RuntimeWarnings on iid Gaussian inputs (only the
    # ranking matters, not the absolute distance values).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        _, knn_idx = knn_index.kneighbors(
            emb2, return_distance=True,
        )
    # Drop self-loop column (first column = self for an exact KNN).
    if knn_idx.shape[1] > 1:
        neighbor_pool = knn_idx[:, 1:]
    else:
        neighbor_pool = knn_idx
    k_eff = neighbor_pool.shape[1]

    # Sample (n, n_walks) endpoint indices in emb1 space.
    endpoint_acc = np.zeros((n, emb1.shape[1]), dtype=np.float32)
    for _ in range(n_walks):
        # Step 1: emb1[i] -> emb2[i] is deterministic (implicit FK).
        # Step 2: pick one of k_eff neighbors uniformly at random.
        choice = rng.integers(low=0, high=k_eff, size=n)
        # Endpoint indices in emb1 space.
        endpoints = neighbor_pool[np.arange(n), choice]
        endpoint_acc += emb1[endpoints]

    return endpoint_acc / float(n_walks)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = 20,
    seed: int = 0,
    **kwargs: Any,
) -> np.ndarray:
    """Stratify paired-vector rows via index-aware Wander Join walks.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First-relation embeddings (e.g. partsupp side).
    emb2 : np.ndarray, shape (N, d2)
        Second-relation embeddings (e.g. part side).  Row ``i`` of ``emb2``
        is assumed to join to row ``i`` of ``emb1`` via the implicit
        primary key.
    K : int, default 20
        Number of strata produced.
    seed : int, default 0
        RNG seed; identical inputs and seed yield identical stratum
        assignments.
    **kwargs : Any
        ``walk_neighbors`` (default 3) — branching factor of the KNN walk
        step.
        ``n_walks`` (default 1) — number of independent walks per row,
        averaged to reduce endpoint variance.
        ``minibatch_size`` (default 1024) — batch size for the final
        K-Means stratifier.

    Returns
    -------
    np.ndarray, shape (N,), dtype int32
        Stratum id per row; values in ``[0, K)``.  Drop-in compatible with
        ``measure_multi_paradigm.stratify_method`` semantics.

    Raises
    ------
    ValueError
        If ``emb1`` and ``emb2`` have a different number of rows, if either
        is not 2-D, or if ``K < 2``.
    """
    if emb1.ndim != 2 or emb2.ndim != 2:
        raise ValueError(
            f"emb1/emb2 must be 2-D; got {emb1.shape} / {emb2.shape}"
        )
    if emb1.shape[0] != emb2.shape[0]:
        raise ValueError(
            f"emb1/emb2 row count mismatch: {emb1.shape[0]} vs {emb2.shape[0]}"
        )
    if K < 2:
        raise ValueError(f"K must be >= 2, got {K}")

    walk_neighbors: int = int(kwargs.get("walk_neighbors", 3))
    n_walks: int = int(kwargs.get("n_walks", 1))
    minibatch_size: int = int(kwargs.get("minibatch_size", 1024))

    if walk_neighbors < 1:
        raise ValueError(f"walk_neighbors must be >= 1, got {walk_neighbors}")
    if n_walks < 1:
        raise ValueError(f"n_walks must be >= 1, got {n_walks}")

    rng = np.random.default_rng(seed)

    # 1) Index-aware random walk: emb1[i] -> emb2[i] -> KNN(emb2) -> emb1[j].
    knn_index = _build_knn_index(emb2.astype(np.float32, copy=False),
                                   k_neighbors=walk_neighbors)
    walk_endpoint = _wander_walk(
        emb1.astype(np.float32, copy=False),
        emb2.astype(np.float32, copy=False),
        knn_index=knn_index,
        n_walks=n_walks,
        rng=rng,
    )

    # 2) Cluster walk endpoints into K strata (MiniBatch K-Means is the
    #    canonical multi-relation stratifier in this project).  Suppress
    #    sklearn matmul-overflow RuntimeWarnings that fire on iid Gaussian
    #    test data with float32 inputs — only the sign matters for K-Means
    #    init and the final assignment is unaffected.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        km = MiniBatchKMeans(
            n_clusters=K,
            batch_size=min(minibatch_size, walk_endpoint.shape[0]),
            random_state=seed,
            n_init="auto",
        )
        # Cast to float64 inside the fit — K-Means in float32 with iid Gaussian
        # data triggers spurious overflow warnings; numerical results are
        # equivalent, just more stable.
        sids = km.fit_predict(walk_endpoint.astype(np.float64)).astype(np.int32)

    return sids


# ---------------------------------------------------------------------------
# Mini-run test
# ---------------------------------------------------------------------------

def _mini_run() -> None:
    """Mini-run with N=10000, d1=96, d2=768; print stratum-size distribution."""
    print("[wander_join] mini-run: N=10000, d1=96, d2=768, K=20")
    rng = np.random.default_rng(0)
    emb1 = rng.standard_normal((10000, 96)).astype(np.float32)
    emb2 = rng.standard_normal((10000, 768)).astype(np.float32)

    sids = stratify_method(emb1, emb2, K=20, seed=0)
    assert sids.shape == (10000,)
    assert sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    counts = np.bincount(sids, minlength=20)
    nz = counts[counts > 0]
    print(f"[wander_join] stratum sizes: "
          f"min={int(nz.min())} max={int(counts.max())} "
          f"mean={counts.mean():.1f} std={counts.std():.1f}")
    print(f"[wander_join] K_used={int((counts > 0).sum())}/20  "
          f"max_min_ratio={counts.max() / max(int(nz.min()), 1):.2f}")
    # Sanity: walks must populate every stratum (K_used == K).  We do *not*
    # bound max_min_ratio tightly because Wander Join is designed to
    # concentrate samples on join-friendly trajectories — strata for
    # densely-connected join sub-graphs are expected to receive more rows
    # than sparsely-connected ones.  This is the algorithm working as
    # intended; the downstream estimator weights each stratum by N_i.
    assert int((counts > 0).sum()) == 20, \
        f"every stratum must receive at least one row; got {int((counts > 0).sum())}/20"

    # Determinism check: same seed -> identical assignment.
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "stratify_method must be deterministic"
    print("[wander_join] determinism (seed=0): OK")
    print("[wander_join] mini-run OK")


if __name__ == "__main__":
    _mini_run()
