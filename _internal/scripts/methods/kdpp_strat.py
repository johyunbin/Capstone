#!/usr/bin/env python3
"""Tier B — k-DPP (k-Determinantal Point Process) stratification (Kulesza-Taskar ICML 2011).

Reference
---------
Kulesza A., Taskar B. ``k-DPPs: Fixed-Size Determinantal Point Processes''.
ICML 2011.  URL: https://icml.cc/2011/papers/611_icmlpaper.pdf

Algorithm
---------
A determinantal point process (DPP) on a ground set ``Y`` is parameterized
by a positive semidefinite kernel ``L``. The probability of sampling a
subset ``S`` is proportional to ``det(L_S)`` -- the volume of the
parallelepiped spanned by the rows of ``L`` indexed by ``S``. A k-DPP
restricts the cardinality to ``|S| = k``; samples favor diverse,
near-orthogonal points (Kulesza-Taskar 2011 §3).

For *stratification*, we use the k-DPP to elect ``K`` representatives
that span the embedding manifold under a Gaussian RBF kernel
``L[i, j] = exp(-||x_i - x_j||^2 / (2 sigma^2))``, where ``sigma`` is the
median pairwise distance heuristic (Garreau-Jitkrittum-Kanagawa 2017).
Each remaining row is then assigned to the nearest representative,
yielding a Voronoi-style partition with deliberately diverse seeds.

Two backends are available:
  * ``dppy.finite_dpps.FiniteDPP`` (preferred, exact MCMC sampler)
  * Greedy approximation (fallback, log-det greedy a.k.a. ``maxvol''):
    iteratively add the row maximizing the marginal volume increase.
    This corresponds to Chen-Zhang-Zhou NeurIPS 2018 ``Fast Greedy MAP
    Inference for Determinantal Point Process'' (arXiv:1709.05135).

For ``N > 5000`` we operate on a uniform random subsample of 5000 rows
(empirical rule from Kulesza-Taskar 2012 monograph §6.1) and assign the
full ``N`` to those medoids by Euclidean nearest neighbor.
"""

from __future__ import annotations

import warnings

import numpy as np

try:
    from dppy.finite_dpps import FiniteDPP  # type: ignore
    HAVE_DPPY = True
except Exception:
    HAVE_DPPY = False

DEFAULT_K: int = 20
DEFAULT_SUBSAMPLE: int = 5_000


def _pairwise_sq_dist(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Compute squared Euclidean distances between rows of X (m, d) and Y (n, d)."""
    Xn = (X * X).sum(axis=1, keepdims=True)
    Yn = (Y * Y).sum(axis=1, keepdims=True).T
    sq = Xn + Yn - 2.0 * (X @ Y.T)
    np.maximum(sq, 0.0, out=sq)
    return sq


def _median_pairwise_dist(X: np.ndarray, sample: int = 1000, seed: int = 0) -> float:
    """Median Euclidean distance over a uniform random subsample (heuristic for sigma)."""
    rng = np.random.default_rng(seed)
    n = X.shape[0]
    m = min(sample, n)
    idx = rng.choice(n, size=m, replace=False)
    sub = X[idx].astype(np.float32)
    sq = _pairwise_sq_dist(sub, sub)
    iu = np.triu_indices_from(sq, k=1)
    dists = np.sqrt(sq[iu])
    med = float(np.median(dists))
    return med if med > 0 else 1.0


def _rbf_kernel(X: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian RBF kernel matrix L[i, j] = exp(-||x_i - x_j||^2 / (2 sigma^2))."""
    sq = _pairwise_sq_dist(X, X)
    inv = 1.0 / (2.0 * sigma * sigma)
    return np.exp(-sq * inv).astype(np.float64)


def _greedy_log_det(L: np.ndarray, K: int, seed: int = 0) -> np.ndarray:
    """Greedy log-det (maxvol) selection of K rows from kernel matrix L.

    Implementation follows Chen-Zhang-Zhou NeurIPS 2018 (arXiv:1709.05135 §3):
    incremental Cholesky updates, O(K^2 N) total.
    """
    n = L.shape[0]
    if K > n:
        raise ValueError(f"K={K} > N={n}; cannot select K distinct items")
    rng = np.random.default_rng(seed)

    # diag = squared marginal-gain vector (init)
    di = np.diag(L).astype(np.float64).copy()
    selected = np.zeros(K, dtype=np.int64)
    # Cholesky-style auxiliary matrix c[j, i] (each step appends a column)
    c = np.zeros((K, n), dtype=np.float64)

    # Pick first index: largest diagonal (or tie-break randomly)
    first_max = float(di.max())
    cands = np.flatnonzero(di >= first_max - 1e-12)
    j = int(rng.choice(cands))
    selected[0] = j

    eps = 1e-10
    for i in range(1, K):
        prev = selected[i - 1]
        # Numerical fix: di may go slightly negative
        denom = float(np.sqrt(max(di[prev], eps)))
        # row of L between prev and all -- minus contribution from previously
        # selected items is captured in c[:i-1, prev] (already filled).
        if i == 1:
            ei = (L[prev] - 0.0) / denom
        else:
            # subtract dot of previous c-rows at prev with all c-rows
            cor = c[:i - 1, :] * c[:i - 1, prev:prev + 1]
            ei = (L[prev] - cor.sum(axis=0)) / denom
        c[i - 1] = ei
        di = di - ei * ei
        di[selected[:i]] = -np.inf

        next_max = float(di.max())
        cands = np.flatnonzero(di >= next_max - 1e-12)
        nxt = int(rng.choice(cands))
        selected[i] = nxt

    return selected


def _kdpp_sample(L: np.ndarray, K: int, seed: int = 0) -> np.ndarray:
    """Draw K-set from k-DPP. Use dppy if available, else greedy fallback."""
    if HAVE_DPPY:
        try:
            dpp = FiniteDPP("likelihood", **{"L": L})
            dpp.flush_samples()
            # dppy's RNG is numpy legacy; seed via numpy global state for determinism
            np.random.seed(seed)
            dpp.sample_exact_k_dpp(size=K)
            sample = np.asarray(dpp.list_of_samples[0], dtype=np.int64)
            if sample.size == K:
                return sample
            # Some dppy versions return non-K size; fall through to greedy
            warnings.warn(
                f"dppy returned size {sample.size} != K={K}; using greedy fallback",
                RuntimeWarning,
            )
        except Exception as exc:
            warnings.warn(
                f"dppy.sample_exact_k_dpp failed ({exc}); using greedy fallback",
                RuntimeWarning,
            )
    return _greedy_log_det(L, K, seed=seed)


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    subsample: int = DEFAULT_SUBSAMPLE,
    kernel_sigma: float | None = None,
    **kwargs,
) -> np.ndarray:
    """Stratify rows via k-DPP medoids + Voronoi assignment.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of medoids / strata.
    seed : int, default 0
        Seed for subsampling, kernel sigma sample, and DPP sampler.
    subsample : int, default 5000
        Rows used for kernel construction. For ``N > subsample`` we run
        the k-DPP on the random subsample; the full ``N`` rows are
        assigned by Euclidean nearest-medoid in the original embedding.
    kernel_sigma : float or None, default None
        Bandwidth of the Gaussian RBF kernel. ``None`` -> median pairwise
        distance heuristic (Garreau-Jitkrittum-Kanagawa 2017).

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
    if K < 2:
        raise ValueError(f"K must be >= 2, got {K}")

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    if K > N:
        raise ValueError(f"K={K} > N={N}; cannot select K medoids")

    rng = np.random.default_rng(seed)
    sub_n = min(subsample, N)
    if sub_n < N:
        sub_idx = rng.choice(N, size=sub_n, replace=False)
        sub = emb_concat[sub_idx]
    else:
        sub_idx = np.arange(N, dtype=np.int64)
        sub = emb_concat

    # Bandwidth (median pairwise distance heuristic)
    sigma = (
        float(kernel_sigma)
        if kernel_sigma is not None
        else _median_pairwise_dist(sub, sample=min(1000, sub_n), seed=seed)
    )

    # RBF kernel on the subsample
    L = _rbf_kernel(sub, sigma=sigma)
    # Add tiny ridge for numerical PSD-ness
    L = L + 1e-9 * np.eye(L.shape[0], dtype=np.float64)

    # k-DPP sample of K medoids (in subsample-index space)
    medoid_sub_ids = _kdpp_sample(L, K=K, seed=seed)
    medoid_global_ids = sub_idx[medoid_sub_ids]
    medoids = emb_concat[medoid_global_ids]

    # Assign every row to nearest medoid (Euclidean in original concat space)
    chunk = 50_000
    sids = np.empty(N, dtype=np.int32)
    for i in range(0, N, chunk):
        j = min(i + chunk, N)
        sq = _pairwise_sq_dist(emb_concat[i:j], medoids)
        sids[i:j] = np.argmin(sq, axis=1).astype(np.int32)
    return sids


def _self_test() -> None:
    rng = np.random.default_rng(0)
    N, d1, d2 = 5_000, 96, 768
    emb1 = rng.standard_normal((N, d1)).astype(np.float32)
    emb2 = rng.standard_normal((N, d2)).astype(np.float32)

    sids = stratify_method(emb1, emb2, K=20, seed=0, subsample=1000)
    assert sids.shape == (N,)
    assert sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    counts = np.bincount(sids, minlength=20)
    K_used = (counts > 0).sum()
    ratio = float(counts.max() / max(counts.min(), 1))
    print(
        f"[self-test] k-DPP (RBF + greedy maxvol, dppy={HAVE_DPPY}): "
        f"N={N} d={d1+d2} K_used={K_used}/20 max/min={ratio:.2f} "
        f"counts[:5]={counts[:5].tolist()}"
    )
    # Voronoi partition on isotropic data should not be wildly imbalanced
    assert K_used >= 15, f"degenerate k-DPP stratification (K_used={K_used})"

    # Determinism check
    sids2 = stratify_method(emb1, emb2, K=20, seed=0, subsample=1000)
    assert np.array_equal(sids, sids2), "k-DPP must be deterministic for fixed seed"

    # Skewed input check
    centers = rng.standard_normal((4, d1 + d2)).astype(np.float32) * 4.0
    skewed_e1 = np.vstack([
        rng.standard_normal((1250, d1)).astype(np.float32) + c[:d1]
        for c in centers
    ])
    skewed_e2 = np.vstack([
        rng.standard_normal((1250, d2)).astype(np.float32) + c[d1:]
        for c in centers
    ])
    sids_skew = stratify_method(skewed_e1, skewed_e2, K=20, seed=0, subsample=1000)
    counts_skew = np.bincount(sids_skew, minlength=20)
    print(
        f"[self-test] k-DPP skewed: K_used={(counts_skew > 0).sum()}/20 "
        f"max/min={float(counts_skew.max() / max(counts_skew.min(), 1)):.2f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
