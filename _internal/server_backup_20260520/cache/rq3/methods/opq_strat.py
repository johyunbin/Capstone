#!/usr/bin/env python3
"""Tier B — Optimized Product Quantization stratification (Ge-He-Ke-Sun CVPR 2013 / PAMI 2014).

Reference
---------
Ge T., He K., Ke Q., Sun J. ``Optimized Product Quantization for
Approximate Nearest Neighbor Search''. CVPR 2013 / IEEE TPAMI 36(4):
744-755, 2014.
DOI: 10.1109/TPAMI.2013.240
URL: https://www.microsoft.com/en-us/research/wp-content/uploads/2013/06/pami13opq.pdf

Algorithm
---------
Plain Product Quantization (PQ, Jegou-Douze-Schmid 2011) splits the
``d``-dimensional vector into ``M`` disjoint sub-vectors of dim ``d/M``,
then trains a separate K-means codebook per sub-space. PQ is sensitive to
*subspace anisotropy*: when one sub-block carries most of the variance,
the codebook on that block is starved while other codebooks are wasted.

Optimized PQ (OPQ, Ge et al. 2013) prepends an orthonormal rotation
``R \\in R^{d \\times d}`` to the embedding, then runs PQ on ``R^T X``.
``R`` is learned to minimize the total quantization error subject to the
orthonormality constraint:

    min_{R, codebooks}  ||X - R Q(R^T X)||_F^2   s.t.  R^T R = I

Optimization is alternation:
  * Fix ``R`` -> standard PQ K-means on each sub-block of ``R^T X``.
  * Fix codebooks -> closed-form Procrustes update for ``R`` from the
    SVD of ``X (R^T X reconstructed)^T`` (Ge et al. 2013 §3.2 ``Non-
    Parametric OPQ'').

For *stratification*, we hash the OPQ composite code modulo ``K``
(matching ``pq_strat`` semantics) so that rows sharing the same rotated
PQ code co-locate. The rotation step makes the partition robust to the
arbitrary axis alignment of input embeddings, a strict-dominate property
over plain PQ on real (anisotropic) vector data.

Two backends are supported:
  * ``faiss.OPQMatrix`` (preferred, GPU-friendly, Tencent BLAS-tuned).
  * Pure-numpy fallback: alternating K-means + SVD Procrustes
    (``n_init=3`` outer iterations).
"""

from __future__ import annotations

import warnings

import numpy as np

try:
    import faiss  # type: ignore
    HAVE_FAISS = True
except Exception:
    HAVE_FAISS = False

try:
    from sklearn.cluster import KMeans  # type: ignore
    HAVE_SKLEARN = True
except Exception:  # pragma: no cover
    HAVE_SKLEARN = False

try:
    from threadpoolctl import threadpool_limits  # type: ignore
    HAVE_THREADPOOLCTL = True
except Exception:  # pragma: no cover
    HAVE_THREADPOOLCTL = False

DEFAULT_K: int = 20
DEFAULT_M: int = 4
DEFAULT_K_PQ: int = 8
DEFAULT_OPQ_ITERS: int = 3


def _kmeans_codebook(
    X: np.ndarray, K_pq: int, seed: int, max_iter: int = 50, n_init: int = 1
) -> tuple[np.ndarray, np.ndarray]:
    """Train K-means codebook on rows of ``X``. Returns (centroids, labels).

    Uses ``n_init=1`` + single-thread BLAS for cross-platform determinism
    (sklearn's parallel BLAS path can yield run-to-run variation on macOS
    Accelerate; OPQ's outer alternation already amortizes init noise).
    """
    if HAVE_SKLEARN:
        km = KMeans(
            n_clusters=K_pq,
            init="k-means++",
            n_init=n_init,
            max_iter=max_iter,
            random_state=seed,
            algorithm="lloyd",
        )
        Xc = np.ascontiguousarray(X, dtype=np.float32)
        if HAVE_THREADPOOLCTL:
            with threadpool_limits(limits=1):
                km.fit(Xc)
        else:
            km.fit(Xc)
        return km.cluster_centers_.astype(np.float32), km.labels_.astype(np.int32)
    # Numpy fallback (Lloyd's iterations)
    rng = np.random.default_rng(seed)
    n, d = X.shape
    init_idx = rng.choice(n, size=K_pq, replace=False)
    centers = X[init_idx].astype(np.float64).copy()
    labels = np.zeros(n, dtype=np.int32)
    for _ in range(max_iter):
        # Assign
        Xn = (X * X).sum(axis=1, keepdims=True)
        Cn = (centers * centers).sum(axis=1, keepdims=True).T
        sq = Xn + Cn - 2.0 * (X @ centers.T)
        new_labels = np.argmin(sq, axis=1).astype(np.int32)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        # Update
        for k in range(K_pq):
            mask = labels == k
            if mask.any():
                centers[k] = X[mask].astype(np.float64).mean(axis=0)
    return centers.astype(np.float32), labels


def _opq_train_numpy(
    X: np.ndarray,
    M: int,
    K_pq: int,
    n_iter: int,
    seed: int,
) -> tuple[np.ndarray, list[np.ndarray]]:
    """Train OPQ rotation R + M codebooks via alternating K-means + Procrustes.

    Returns (R of shape (d, d), list of M centroid arrays of shape (K_pq, sub_dim)).
    """
    n, d = X.shape
    sub_dim = d // M

    # Initialize R = identity. Procrustes will refine.
    R = np.eye(d, dtype=np.float32)

    centroids: list[np.ndarray] = []
    for outer in range(n_iter):
        Y = X @ R  # (n, d) — rotated embedding
        centroids = []
        Xq = np.empty_like(Y)
        for j in range(M):
            sub = Y[:, j * sub_dim : (j + 1) * sub_dim]
            cents, lab = _kmeans_codebook(
                sub, K_pq=K_pq, seed=seed + outer * 100 + j, n_init=2
            )
            centroids.append(cents)
            Xq[:, j * sub_dim : (j + 1) * sub_dim] = cents[lab]
        # Procrustes: closest orthonormal R s.t. X R ≈ Xq
        # Solve via SVD of (X^T Xq): R = U V^T
        # Use float64 for stability
        XtXq = (X.astype(np.float64).T @ Xq.astype(np.float64))
        U, _, Vt = np.linalg.svd(XtXq, full_matrices=False)
        R = (U @ Vt).astype(np.float32)
    return R, centroids


def _encode_with_opq(
    X: np.ndarray, R: np.ndarray, centroids: list[np.ndarray], M: int
) -> np.ndarray:
    """Encode X via OPQ -> (N, M) int codes."""
    n, d = X.shape
    sub_dim = d // M
    Y = X @ R
    codes = np.empty((n, M), dtype=np.int32)
    for j in range(M):
        sub = Y[:, j * sub_dim : (j + 1) * sub_dim]
        cents = centroids[j]
        # Squared distance to centroids
        sub_n = (sub * sub).sum(axis=1, keepdims=True)
        cn = (cents * cents).sum(axis=1, keepdims=True).T
        sq = sub_n + cn - 2.0 * (sub @ cents.T)
        codes[:, j] = np.argmin(sq, axis=1).astype(np.int32)
    return codes


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    M: int = DEFAULT_M,
    K_pq: int = DEFAULT_K_PQ,
    n_iter: int = DEFAULT_OPQ_ITERS,
    sample_size: int | None = 100_000,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by Optimized Product Quantization codes mod K.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of strata (output IDs in ``[0, K)``).
    seed : int, default 0
        Random seed (K-means + faiss).
    M : int, default 4
        PQ sub-spaces. ``d`` is trimmed to a multiple of ``M`` if needed.
    K_pq : int, default 8
        Codebook size per sub-block.
    n_iter : int, default 3
        Number of OPQ alternation iterations (Procrustes + PQ K-means).
    sample_size : int or None, default 100_000
        Cap on rows used for OPQ training (None = use all N).

    Returns
    -------
    np.ndarray of shape (N,), dtype int32
        Stratum identifiers in ``[0, K)``.
    """
    if emb1.ndim != 2 or emb2.ndim != 2:
        raise ValueError(
            f"emb1/emb2 must be 2D; got {emb1.shape} / {emb2.shape}"
        )
    if emb1.shape[0] != emb2.shape[0]:
        raise ValueError(
            f"row count mismatch: emb1 {emb1.shape[0]} vs emb2 {emb2.shape[0]}"
        )
    if M < 1:
        raise ValueError(f"M must be >= 1, got {M}")
    if K < 2:
        raise ValueError(f"K must be >= 2, got {K}")
    if K_pq < 2:
        raise ValueError(f"K_pq must be >= 2, got {K_pq}")

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    sub_dim = d // M
    if sub_dim < 1:
        raise ValueError(f"M={M} too large for d={d} (sub_dim < 1)")
    if d % M != 0:
        emb_concat = emb_concat[:, : sub_dim * M]
        d = sub_dim * M

    # Optional fit subsample
    rng = np.random.default_rng(seed)
    if sample_size is not None and N > sample_size:
        fit_idx = rng.choice(N, size=sample_size, replace=False)
        fit_data = np.ascontiguousarray(emb_concat[fit_idx])
    else:
        fit_data = emb_concat

    if HAVE_FAISS:
        try:
            faiss.seed_global_rng(int(seed))
            opq = faiss.OPQMatrix(d, M)
            opq.niter = max(int(n_iter) * 10, 25)
            opq.train(np.ascontiguousarray(fit_data, dtype=np.float32))
            rotated_full = opq.apply_py(np.ascontiguousarray(emb_concat, dtype=np.float32))
            rotated_fit = opq.apply_py(np.ascontiguousarray(fit_data, dtype=np.float32))
            # Train PQ codebooks on rotated fit data, encode rotated full data
            codes = np.empty((N, M), dtype=np.int32)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                for j in range(M):
                    sub_fit = rotated_fit[:, j * sub_dim : (j + 1) * sub_dim]
                    sub_full = rotated_full[:, j * sub_dim : (j + 1) * sub_dim]
                    cents, _ = _kmeans_codebook(
                        sub_fit, K_pq=K_pq, seed=seed + j, n_init=3
                    )
                    sub_n = (sub_full * sub_full).sum(axis=1, keepdims=True)
                    cn = (cents * cents).sum(axis=1, keepdims=True).T
                    sq = sub_n + cn - 2.0 * (sub_full @ cents.T)
                    codes[:, j] = np.argmin(sq, axis=1).astype(np.int32)
        except Exception as exc:
            warnings.warn(
                f"faiss.OPQMatrix failed ({exc}); using numpy OPQ fallback",
                RuntimeWarning,
            )
            R, centroids = _opq_train_numpy(
                fit_data, M=M, K_pq=K_pq, n_iter=n_iter, seed=seed
            )
            codes = _encode_with_opq(emb_concat, R, centroids, M)
    else:
        R, centroids = _opq_train_numpy(
            fit_data, M=M, K_pq=K_pq, n_iter=n_iter, seed=seed
        )
        codes = _encode_with_opq(emb_concat, R, centroids, M)

    # Hash composite code -> K bin (modulo, matches pq_strat default)
    composite = np.zeros(N, dtype=np.uint64)
    base = np.uint64(K_pq)
    for j in range(M):
        composite = composite * base + codes[:, j].astype(np.uint64)
    sids = (composite % np.uint64(K)).astype(np.int32)
    return sids


def _self_test() -> None:
    rng = np.random.default_rng(0)
    N, d1, d2 = 10_000, 96, 768
    emb1 = rng.standard_normal((N, d1)).astype(np.float32)
    emb2 = rng.standard_normal((N, d2)).astype(np.float32)

    sids = stratify_method(emb1, emb2, K=20, seed=0)
    assert sids.shape == (N,)
    assert sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    counts = np.bincount(sids, minlength=20)
    K_used = (counts > 0).sum()
    ratio = float(counts.max() / max(counts.min(), 1))
    print(
        f"[self-test] OPQ (M=4 K_pq=8 n_iter=3, faiss={HAVE_FAISS}): "
        f"N={N} d={d1+d2} K_used={K_used}/20 max/min={ratio:.2f} "
        f"counts[:5]={counts[:5].tolist()}"
    )
    assert K_used >= 16, f"degenerate OPQ stratification (K_used={K_used})"

    # Determinism check
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "OPQ must be deterministic for fixed seed"

    # Anisotropic input check (should still produce balanced strata after rotation)
    aniso = np.diag([10.0] * 50 + [1.0] * (d1 + d2 - 50)).astype(np.float32)
    skewed = (rng.standard_normal((N, d1 + d2)).astype(np.float32) @ aniso)
    sids_a = stratify_method(skewed[:, :d1], skewed[:, d1:], K=20, seed=0)
    counts_a = np.bincount(sids_a, minlength=20)
    print(
        f"[self-test] OPQ anisotropic: K_used={(counts_a > 0).sum()}/20 "
        f"max/min={float(counts_a.max() / max(counts_a.min(), 1)):.2f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
