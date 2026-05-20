#!/usr/bin/env python3
"""Tier B — Latin Hypercube Sampling stratification (McKay-Beckman-Conover 1979).

Reference
---------
McKay M. D., Beckman R. J., Conover W. J. ``A Comparison of Three Methods for
Selecting Values of Input Variables in the Analysis of Output From a
Computer Code''. Technometrics, 21(2):239-245, 1979.
DOI: 10.2307/1268522  URL: https://www.jstor.org/stable/1268522

Algorithm
---------
Latin Hypercube Sampling (LHS) draws ``n`` design points in a ``k``-dimensional
unit hypercube such that each one-dimensional marginal is partitioned into
exactly ``n`` strata, with one and only one sample per stratum per
dimension. The pairing between marginals is a uniformly random
permutation. Compared to plain random sampling LHS reduces the variance
of the mean estimator whenever the response is monotone in any
dimension (McKay et al. 1979 Theorem 1).

For *stratification* of a high-dimensional embedding, we first project the
concatenated embedding to ``k`` PCA components (capturing the dominant
linear structure), then compute the LHS design point closest to each row
in the projected space. Two implementations are supported:

  * Direct quantile bin on the leading PCA component (when ``k_marg=1``).
    Equivalent to the McKay-Beckman-Conover marginal partition for a
    1-D response.
  * Multi-dimensional LHS design via ``scipy.stats.qmc.LatinHypercube``,
    nearest-design-point assignment, then mod-K hashing of the design
    index.

The 1-D variant is the canonical capstone choice — it provides a clean
``paradigm anchor'' next to Sobol low-discrepancy sequences, sharing the
classical statistical sample-design lineage.
"""

from __future__ import annotations

import warnings

import numpy as np

try:
    from scipy.stats.qmc import LatinHypercube  # type: ignore
    HAVE_SCIPY_QMC = True
except Exception:  # pragma: no cover
    HAVE_SCIPY_QMC = False

try:
    from sklearn.decomposition import PCA  # type: ignore
    HAVE_SKLEARN = True
except Exception:  # pragma: no cover
    HAVE_SKLEARN = False

DEFAULT_K: int = 20
DEFAULT_K_MARG: int = 1
DEFAULT_N_COMPONENTS: int = 10


def _pca_project(
    X: np.ndarray, n_components: int, seed: int
) -> np.ndarray:
    """Project ``X`` to ``n_components`` via truncated PCA (centered SVD)."""
    if HAVE_SKLEARN:
        pca = PCA(n_components=n_components, random_state=seed)
        return pca.fit_transform(X.astype(np.float32))
    # Fallback: numpy SVD on centered matrix
    Xc = X.astype(np.float64) - X.astype(np.float64).mean(axis=0, keepdims=True)
    # Take top-k right singular vectors via economy SVD
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return (Xc @ Vt[:n_components].T).astype(np.float32)


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    k_marg: int = DEFAULT_K_MARG,
    n_components: int = DEFAULT_N_COMPONENTS,
    sample_size: int | None = 100_000,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by Latin Hypercube design over PCA-projected embedding.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column (e.g. DEEP 96d).
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of strata (output stratum IDs in ``[0, K)``).
    seed : int, default 0
        Seed for PCA + LHS design generator.
    k_marg : int, default 1
        Number of PCA marginals used in the LHS design.
        ``1`` -> direct quantile bin on PCA1 (canonical, fast, deterministic).
        ``> 1`` -> multi-D LHS via scipy.stats.qmc, mod-K hash of nearest
        design index.
    n_components : int, default 10
        PCA components retained for projection (must be >= ``k_marg``).
    sample_size : int or None, default 100_000
        Cap on rows used for fitting the PCA basis (None = use all N).

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
    if k_marg < 1:
        raise ValueError(f"k_marg must be >= 1, got {k_marg}")
    if n_components < k_marg:
        n_components = k_marg

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    n_components_eff = min(n_components, d)

    # PCA on subsample if too large
    rng = np.random.default_rng(seed)
    if sample_size is not None and N > sample_size:
        fit_idx = rng.choice(N, size=sample_size, replace=False)
        fit_data = emb_concat[fit_idx]
    else:
        fit_data = emb_concat

    if HAVE_SKLEARN:
        pca = PCA(n_components=n_components_eff, random_state=seed)
        pca.fit(fit_data)
        proj = pca.transform(emb_concat).astype(np.float32)
    else:
        # SVD on subsample + apply to full
        mu = fit_data.astype(np.float64).mean(axis=0)
        _, _, Vt = np.linalg.svd(
            fit_data.astype(np.float64) - mu, full_matrices=False
        )
        Vt_k = Vt[:n_components_eff]
        proj = ((emb_concat.astype(np.float64) - mu) @ Vt_k.T).astype(np.float32)

    if k_marg == 1:
        # 1-D LHS = quantile partition of the leading PCA component.
        coord = proj[:, 0]
        edges = np.quantile(coord, np.linspace(0.0, 1.0, K + 1))[1:-1]
        sids = np.searchsorted(edges, coord, side="right")
        return np.clip(sids, 0, K - 1).astype(np.int32)

    # Multi-D LHS design then nearest-design assignment
    if not HAVE_SCIPY_QMC:
        raise RuntimeError(
            "scipy.stats.qmc.LatinHypercube unavailable; install scipy>=1.7 "
            "or use k_marg=1"
        )
    proj_k = proj[:, :k_marg].astype(np.float64)
    # Map each marginal to [0, 1] via empirical CDF (rank / N)
    ranks = np.empty_like(proj_k)
    for j in range(k_marg):
        order = np.argsort(proj_k[:, j])
        rk = np.empty(N, dtype=np.float64)
        rk[order] = (np.arange(N) + 0.5) / N
        ranks[:, j] = rk
    # LHS design over [0, 1)^k_marg
    sampler = LatinHypercube(d=k_marg, seed=seed)
    n_design = max(K, min(K * 50, 2000))  # enough resolution for K bins
    design = sampler.random(n=n_design)
    # Nearest design point per row (Euclidean in unit cube)
    chunk = 10_000
    design_ids = np.empty(N, dtype=np.int64)
    for i in range(0, N, chunk):
        j = min(i + chunk, N)
        diff = ranks[i:j, None, :] - design[None, :, :]
        sq = (diff * diff).sum(axis=2)
        design_ids[i:j] = np.argmin(sq, axis=1)
    sids = (design_ids % np.int64(K)).astype(np.int32)
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
        f"[self-test] LHS (k_marg=1 PCA1 quantile): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    assert ratio < 1.5, f"quantile bin should be uniform, got {ratio:.2f}"

    # Determinism check
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "LHS must be deterministic for fixed seed"

    # Multi-D variant smoke
    if HAVE_SCIPY_QMC:
        sids_md = stratify_method(emb1, emb2, K=20, seed=0, k_marg=3)
        assert sids_md.shape == (N,)
        assert sids_md.min() >= 0 and sids_md.max() < 20
        counts_md = np.bincount(sids_md, minlength=20)
        print(
            f"[self-test] LHS (k_marg=3 multi-D): K_used={(counts_md > 0).sum()}/20 "
            f"max/min={float(counts_md.max() / max(counts_md.min(), 1)):.2f}"
        )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
