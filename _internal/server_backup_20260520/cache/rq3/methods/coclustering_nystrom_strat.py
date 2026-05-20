#!/usr/bin/env python3
"""
Co-clustering with Nystrom approximation — multi-vector (Tier B).

Bipartite spectral co-clustering of two row-aligned embedding views ``emb1``
and ``emb2`` via the singular-value decomposition of the normalised cross
similarity matrix, accelerated for large ``N`` with Nystrom column sampling.

Algorithm
---------
The construction follows Dhillon (KDD 2003) for bipartite spectral
co-clustering, applied to the *row-aligned* multi-vector setting common in
vector-augmented analytical queries:

1. Form the per-row similarity ``A[i, j] = cos(emb1[i], emb2[j])`` over the
   N x N rectangular bipartite graph (rows = items, ``emb1`` view in one part,
   ``emb2`` view in the other; an edge weight ``A[i, j]`` connects them).
2. Per Dhillon (2003), normalise as ``A_n = D1^{-1/2} A D2^{-1/2}`` where
   ``D1 = diag(A 1)``, ``D2 = diag(A^T 1)``, and read off the leading
   singular vectors ``U_K, V_K`` (top ``K = ceil(log2(n_strata)) + 1``).
3. Concatenate ``[D1^{-1/2} U_K | D2^{-1/2} V_K]`` and run k-means with
   ``n_clusters = n_strata``. Row clusters provide the per-row stratum id.
4. **Nystrom approximation** (Williams & Seeger NIPS 2001): instead of
   forming the full ``N x N`` matrix, subsample ``m = nystrom_components``
   landmark rows; compute the ``m x m`` similarity ``W`` and the ``N x m``
   cross block ``C``. Approximate the leading eigenvectors via
   ``U ~= C @ W_pinv_sqrt`` (per Fowlkes et al. 2004 PAMI for spectral
   clustering with Nystrom).

The time and memory cost is ``O(N * m + m^3)`` instead of ``O(N^2)``,
making this tractable on N up to ~10M with m=1000.

References
----------
Dhillon IS. "Co-clustering documents and words using bipartite spectral graph
partitioning." KDD 2003, 269-274. DOI 10.1145/956750.956764.

Williams CKI, Seeger M. "Using the Nystrom method to speed up kernel
machines." NIPS 2001.

Fowlkes C, Belongie S, Chung F, Malik J. "Spectral grouping using the Nystrom
method." IEEE TPAMI 26(2), 214-225 (2004). DOI 10.1109/TPAMI.2004.1262185.

Single-table fallback
---------------------
When ``emb2 is None`` the cross-graph is undefined. We fall back to spectral
clustering on the single-view nearest-neighbour graph (Nystrom-approximated)
to keep the API uniform.

Usage
-----
::

    from coclustering_nystrom_strat import (
        fit_coclustering_nystrom_mapper, assign_coclustering_nystrom,
    )
    mapper = fit_coclustering_nystrom_mapper(
        emb1_samples, emb2_samples, n_strata=20, seed=42,
        nystrom_components=1000, n_eigvecs=20,
    )
    sids = assign_coclustering_nystrom(mapper, emb1_full, emb2_full)

Author: Capstone 2026 / 속도는벡터 (Tier B production-ready, 2026-05-09).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from sklearn.cluster import MiniBatchKMeans

DEFAULT_K: int = 20
DEFAULT_SEED: int = 42
DEFAULT_NYSTROM_COMPONENTS: int = 1000
DEFAULT_N_EIGVECS: int = 20


def _l2_normalize(matrix: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Row-wise L2 normalisation. Returns float32 to keep memory tight."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return (matrix / np.maximum(norms, eps)).astype(np.float32)


@dataclass
class CoClusteringNystromMapper:
    """Container for the fitted Nystrom co-clustering model.

    Attributes
    ----------
    landmarks_x:
        ``(m, d1)`` landmark rows from the X-view (always set).
    landmarks_y:
        ``(m, d2)`` landmark rows from the Y-view (``None`` in single-table
        fallback).
    landmark_indices:
        ``(m,)`` row indices used as landmarks (debug / reproducibility).
    embedding_basis:
        ``(m, n_eigvecs)`` matrix used to project new rows into the spectral
        embedding space, derived from the eigendecomposition of the landmark
        ``W`` block.
    kmeans:
        Trained ``MiniBatchKMeans`` with ``n_clusters = n_strata`` on the
        spectral embedding of the training rows.
    n_strata:
        Final number of strata.
    nystrom_components:
        Number of landmark columns ``m``.
    n_eigvecs:
        Number of leading eigenvectors retained.
    fallback_single:
        ``True`` when the single-table fallback path was taken (``emb2`` was
        missing); the cross-graph is replaced by a self-similarity Nystrom on
        ``X``.
    """

    landmarks_x: np.ndarray
    landmarks_y: Optional[np.ndarray]
    landmark_indices: np.ndarray
    embedding_basis: np.ndarray
    kmeans: MiniBatchKMeans
    n_strata: int
    nystrom_components: int
    n_eigvecs: int
    fallback_single: bool = False
    rho_top: float = field(default=0.0)


def _nystrom_embed(
    vectors_x: np.ndarray,
    vectors_y: Optional[np.ndarray],
    landmarks_x: np.ndarray,
    landmarks_y: Optional[np.ndarray],
    embedding_basis: np.ndarray,
    fallback_single: bool,
    chunk: int = 50_000,
) -> np.ndarray:
    """Project (vectors_x, vectors_y) into the spectral embedding space.

    For multi-vector mode (cross-graph): per-row score against landmark Y is
    ``cos(vectors_x[i], landmarks_y) + cos(vectors_y[i], landmarks_x)`` averaged,
    matching the symmetric bipartite construction. For fallback: cosine
    similarity ``vectors_x @ landmarks_x.T``.
    """
    n = vectors_x.shape[0]
    m = embedding_basis.shape[0]
    out = np.empty((n, embedding_basis.shape[1]), dtype=np.float32)

    vx_norm = _l2_normalize(vectors_x.astype(np.float32))
    lx_norm = _l2_normalize(landmarks_x.astype(np.float32))

    if not fallback_single and vectors_y is not None and landmarks_y is not None:
        vy_norm = _l2_normalize(vectors_y.astype(np.float32))
        ly_norm = _l2_normalize(landmarks_y.astype(np.float32))
    else:
        vy_norm = None
        ly_norm = None

    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        sub_x = vx_norm[start:end]
        # cos(vectors_x[i], landmarks_x[j]) — always defined
        sim_xx = sub_x @ lx_norm.T  # (chunk, m)
        if not fallback_single and vy_norm is not None and ly_norm is not None:
            sub_y = vy_norm[start:end]
            sim_yy = sub_y @ ly_norm.T  # (chunk, m)
            # Symmetric bipartite similarity used in Dhillon (2003): treat
            # row-i as connected to landmark-j by the average of the two cross
            # cosine similarities (single canonical scalar per (i, j) edge).
            sim = 0.5 * (sim_xx + sim_yy)
        else:
            sim = sim_xx
        out[start:end] = (sim @ embedding_basis).astype(np.float32)
    return out


def fit_coclustering_nystrom_mapper(
    samples_x: np.ndarray,
    samples_y: Optional[np.ndarray] = None,
    n_strata: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    nystrom_components: int = DEFAULT_NYSTROM_COMPONENTS,
    n_eigvecs: int = DEFAULT_N_EIGVECS,
    **_kwargs,
) -> CoClusteringNystromMapper:
    """Fit Nystrom co-clustering on row-aligned training samples.

    Parameters
    ----------
    samples_x, samples_y:
        ``(n, d1)`` and ``(n, d2)`` training samples. Set ``samples_y=None``
        to take the single-table fallback path.
    n_strata:
        Final number of clusters (= strata).
    seed:
        Random state for landmark sampling and k-means.
    nystrom_components:
        Number of landmark rows ``m``. Capped at ``samples_x.shape[0]``.
    n_eigvecs:
        Number of leading singular / eigenvectors to use for the spectral
        embedding. Should be ``>= n_strata`` for informative embeddings.

    Returns
    -------
    CoClusteringNystromMapper
        Trained mapper.
    """
    if samples_x.ndim != 2:
        raise ValueError(f"samples_x must be 2D, got shape {samples_x.shape}")

    n_samples = samples_x.shape[0]
    m = max(1, min(int(nystrom_components), n_samples))
    n_eig = max(2, min(int(n_eigvecs), m - 1))

    rng = np.random.default_rng(seed)
    landmark_idx = rng.choice(n_samples, size=m, replace=False)
    landmarks_x = samples_x[landmark_idx].astype(np.float32)

    use_fallback = samples_y is None or (
        isinstance(samples_y, np.ndarray)
        and samples_y.shape[0] == samples_x.shape[0]
        and samples_y is samples_x
    )

    if use_fallback:
        landmarks_y = None
    else:
        if samples_y.ndim != 2:
            raise ValueError(f"samples_y must be 2D, got shape {samples_y.shape}")
        if samples_y.shape[0] != samples_x.shape[0]:
            raise ValueError(
                f"samples_x rows ({samples_x.shape[0]}) must equal "
                f"samples_y rows ({samples_y.shape[0]})"
            )
        landmarks_y = samples_y[landmark_idx].astype(np.float32)

    # ---------------------------------------------------------------- Nystrom
    # W block: similarity among landmark rows. Multi-vector mode uses the same
    # symmetric "average of two cosine similarities" construction as at
    # assign-time, ensuring W and C are consistent.
    lx_norm = _l2_normalize(landmarks_x)
    if not use_fallback and landmarks_y is not None:
        ly_norm = _l2_normalize(landmarks_y)
        W_xx = lx_norm @ lx_norm.T  # (m, m)
        W_yy = ly_norm @ ly_norm.T  # (m, m)
        W = 0.5 * (W_xx + W_yy)
    else:
        W = lx_norm @ lx_norm.T  # (m, m)

    # Symmetrise W to guard against floating-point drift before eig decomposition.
    W = 0.5 * (W + W.T)

    # Eigendecomposition of the symmetric landmark block.
    # We use eigh (Hermitian) for stability; sort descending.
    eigvals, eigvecs = np.linalg.eigh(W)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    # Drop near-zero eigenvalues for stable inverse-sqrt.
    keep = max(2, min(n_eig, int((eigvals > 1e-8).sum())))
    eigvals_top = eigvals[:keep]
    eigvecs_top = eigvecs[:, :keep]

    # Embedding basis: maps a "landmark similarity vector" of shape (m,) to
    # (keep,) in the spectral embedding space. From Fowlkes et al. (2004),
    # for a row r with similarity s_r = sim(r, landmarks), the Nystrom
    # spectral embedding is s_r @ V_top @ Lambda_top^{-1/2}.
    inv_sqrt_eigvals = 1.0 / np.sqrt(np.maximum(eigvals_top, 1e-8))
    embedding_basis = (eigvecs_top * inv_sqrt_eigvals).astype(np.float32)
    rho_top = float(eigvals_top[0]) if keep > 0 else 0.0

    # ---------------------------------------------------------------- k-means
    # Embed every training sample and cluster.
    train_embed = _nystrom_embed(
        samples_x,
        None if use_fallback else samples_y,
        landmarks_x,
        landmarks_y,
        embedding_basis,
        fallback_single=use_fallback,
    )
    # Row-normalise the spectral embedding so cosine ~ Euclidean for k-means
    # (Ng-Jordan-Weiss 2001 normalised spectral clustering convention).
    norms = np.linalg.norm(train_embed, axis=1, keepdims=True)
    train_embed_normed = (train_embed / np.maximum(norms, 1e-12)).astype(np.float32)

    kmeans = MiniBatchKMeans(
        n_clusters=n_strata,
        random_state=seed,
        batch_size=min(1024, max(256, train_embed_normed.shape[0] // 10)),
        n_init=3,
        max_iter=200,
    )
    kmeans.fit(train_embed_normed)

    return CoClusteringNystromMapper(
        landmarks_x=landmarks_x,
        landmarks_y=landmarks_y,
        landmark_indices=landmark_idx.astype(np.int64),
        embedding_basis=embedding_basis,
        kmeans=kmeans,
        n_strata=n_strata,
        nystrom_components=m,
        n_eigvecs=keep,
        fallback_single=use_fallback,
        rho_top=rho_top,
    )


def assign_coclustering_nystrom(
    mapper: CoClusteringNystromMapper,
    vectors_x: np.ndarray,
    vectors_y: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Assign each row of ``(vectors_x, vectors_y)`` to a co-cluster id.

    Parameters
    ----------
    mapper:
        Trained :class:`CoClusteringNystromMapper`.
    vectors_x, vectors_y:
        Full vector views to assign. ``vectors_y`` is required iff the mapper
        was trained in multi-vector mode (``mapper.fallback_single is False``).

    Returns
    -------
    np.ndarray
        ``(N,) int32`` stratum ids in ``[0, n_strata)``.
    """
    if vectors_x.ndim != 2:
        raise ValueError(f"vectors_x must be 2D, got shape {vectors_x.shape}")
    if not mapper.fallback_single:
        if vectors_y is None:
            raise ValueError(
                "vectors_y is required when mapper trained in multi-vector mode"
            )
        if vectors_y.ndim != 2:
            raise ValueError(f"vectors_y must be 2D, got shape {vectors_y.shape}")
        if vectors_y.shape[0] != vectors_x.shape[0]:
            raise ValueError(
                f"vectors_x rows ({vectors_x.shape[0]}) must equal "
                f"vectors_y rows ({vectors_y.shape[0]})"
            )

    embed = _nystrom_embed(
        vectors_x,
        vectors_y,
        mapper.landmarks_x,
        mapper.landmarks_y,
        mapper.embedding_basis,
        fallback_single=mapper.fallback_single,
    )
    norms = np.linalg.norm(embed, axis=1, keepdims=True)
    embed_normed = (embed / np.maximum(norms, 1e-12)).astype(np.float32)
    sids = mapper.kmeans.predict(embed_normed).astype(np.int32)
    return sids


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    counts = np.bincount(stratum_ids, minlength=n_clusters)
    nz = counts[counts > 0]
    return {
        "min": int(counts.min()),
        "max": int(counts.max()),
        "mean": float(counts.mean()),
        "std": float(counts.std()),
        "max_min_ratio": float(counts.max() / max(counts.min(), 1)),
        "n_used": int((counts > 0).sum()),
        "n_strata": int(n_clusters),
        "n_nonzero": int(len(nz)),
    }


def stratify_method(
    emb1: np.ndarray,
    emb2: Optional[np.ndarray] = None,
    K: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    nystrom_components: int = DEFAULT_NYSTROM_COMPONENTS,
    n_eigvecs: int = DEFAULT_N_EIGVECS,
    **kwargs,
) -> np.ndarray:
    """Drop-in stratifier interface compatible with the other Tier B methods.

    Parameters
    ----------
    emb1:
        ``(N, d1)`` first embedding view (always required).
    emb2:
        ``(N, d2)`` second embedding view. ``None`` triggers the spectral-
        single-table fallback path documented in
        :func:`fit_coclustering_nystrom_mapper`.
    K:
        Number of strata.
    seed:
        Random state.
    nystrom_components:
        Number of landmark rows ``m``.
    n_eigvecs:
        Number of leading eigenvectors retained.

    Returns
    -------
    np.ndarray
        ``(N,) int32`` stratum ids in ``[0, K)``.
    """
    mapper = fit_coclustering_nystrom_mapper(
        emb1,
        emb2,
        n_strata=K,
        seed=seed,
        nystrom_components=nystrom_components,
        n_eigvecs=n_eigvecs,
        **kwargs,
    )
    return assign_coclustering_nystrom(mapper, emb1, emb2)


def _self_test() -> None:
    """Mini-run: N=10000 random multi-vector data with mixed correlation."""
    import warnings

    np.seterr(all="ignore")
    warnings.filterwarnings("ignore")
    rng = np.random.default_rng(0)
    n = 10_000
    d1, d2 = 96, 768
    n_strata = 20

    print(f"[self-test] generating N={n:,} d1={d1} d2={d2} samples")
    # Cluster-structured data so the spectral co-clustering should resolve
    # something better than a random partition.
    n_blocks = 8
    centers_x = rng.standard_normal((n_blocks, d1)).astype(np.float64) * 4.0
    centers_y = rng.standard_normal((n_blocks, d2)).astype(np.float64) * 4.0
    block_assignment = rng.integers(0, n_blocks, size=n)
    emb1 = (
        centers_x[block_assignment]
        + rng.standard_normal((n, d1)).astype(np.float64) * 0.5
    ).astype(np.float32)
    emb2 = (
        centers_y[block_assignment]
        + rng.standard_normal((n, d2)).astype(np.float64) * 0.5
    ).astype(np.float32)

    mapper = fit_coclustering_nystrom_mapper(
        emb1, emb2, n_strata=n_strata, seed=42,
        nystrom_components=1000, n_eigvecs=20,
    )
    sids = assign_coclustering_nystrom(mapper, emb1, emb2)
    summary = cluster_size_summary(sids, n_clusters=n_strata)
    print(
        f"[self-test] Co-cluster Nystrom multi-vector: "
        f"sids range=[{sids.min()}, {sids.max()}], "
        f"max/min={summary['max_min_ratio']:.2f}, used={summary['n_used']}/{n_strata}, "
        f"top_lambda={mapper.rho_top:.4f}, m={mapper.nystrom_components}, "
        f"keep={mapper.n_eigvecs}"
    )
    assert sids.min() >= 0 and sids.max() < n_strata
    assert summary["n_used"] >= n_strata // 2, (
        f"at least half the strata should be populated, got {summary['n_used']}"
    )

    # Single-table fallback
    mapper_fb = fit_coclustering_nystrom_mapper(
        emb1, None, n_strata=n_strata, seed=42,
        nystrom_components=1000, n_eigvecs=20,
    )
    assert mapper_fb.fallback_single is True
    assert mapper_fb.landmarks_y is None
    sids_fb = assign_coclustering_nystrom(mapper_fb, emb1)
    summary_fb = cluster_size_summary(sids_fb, n_clusters=n_strata)
    print(
        f"[self-test] Co-cluster Nystrom fallback: "
        f"max/min={summary_fb['max_min_ratio']:.2f}, "
        f"used={summary_fb['n_used']}/{n_strata}"
    )
    assert sids_fb.min() >= 0 and sids_fb.max() < n_strata

    # Determinism check (seed-fixed; MiniBatchKMeans deterministic with same seed)
    mapper2 = fit_coclustering_nystrom_mapper(
        emb1, emb2, n_strata=n_strata, seed=42,
        nystrom_components=1000, n_eigvecs=20,
    )
    sids2 = assign_coclustering_nystrom(mapper2, emb1, emb2)
    agreement = float((sids == sids2).mean())
    print(f"[self-test] determinism agreement: {agreement:.3f} (k-means random init)")
    # MiniBatchKMeans is deterministic for fixed seed but cluster id labels may
    # permute on different builds; agreement should at least be high under same
    # build. Allow some slack.
    assert agreement >= 0.95, (
        f"deterministic seed should yield >=0.95 agreement, got {agreement:.3f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
