#!/usr/bin/env python3
"""
CCA-1D projection stratification — multi-vector (Tier B).

Implements canonical correlation analysis (Hotelling 1936) between two row-aligned
embedding views ``emb1`` and ``emb2`` and uses the joint canonical 1D projection
to assign per-row stratum identifiers via quantile binning.

Algorithm
---------
For mean-centered data matrices ``X`` (N x d1) and ``Y`` (N x d2)::

    Sigma_xx = X.T @ X / (N - 1)
    Sigma_yy = Y.T @ Y / (N - 1)
    Sigma_xy = X.T @ Y / (N - 1)

CCA solves the generalized eigenvalue problem::

    Sigma_xx^-1 @ Sigma_xy @ Sigma_yy^-1 @ Sigma_yx @ a = rho^2 * a

where the leading eigenvector ``a`` (in X-space) and the corresponding ``b`` (in
Y-space) define the canonical correlation directions ``u = X @ a`` and
``v = Y @ b``. The mean canonical projection ``(u + v) / 2`` is then quantile
binned into ``n_strata`` strata. We delegate the eigen-solve to
``sklearn.cross_decomposition.CCA`` (which uses NIPALS — equivalent to the
closed-form for the top component) for numerical stability with ill-conditioned
covariance matrices typical of high-dimensional embeddings.

References
----------
Hotelling H. "Relations between two sets of variates." Biometrika 28(3-4),
321-377 (1936). DOI 10.1093/biomet/28.3-4.321.

Hardoon DR, Szedmak S, Shawe-Taylor J. "Canonical correlation analysis: an
overview with application to learning methods." Neural Computation 16(12),
2639-2664 (2004). DOI 10.1162/0899766042321814.

scikit-learn ``sklearn.cross_decomposition.CCA``.

Single-table fallback
---------------------
When ``emb2 is None`` (or ``emb2 is emb1``) CCA is undefined. The mapper falls
back to standard PCA-1D (top principal direction of ``X``) and bins by quantile
of ``X @ a_pca``, recovering the existing ``pca1d_quantile`` behaviour as a
graceful degrade path.

Usage
-----
::

    from cca_strat import fit_cca1d_mapper, assign_cca1d
    mapper = fit_cca1d_mapper(emb1_samples, emb2_samples, n_strata=20, seed=42)
    sids = assign_cca1d(mapper, emb1_full, emb2_full)   # multi-vector
    sids_pca = assign_cca1d(mapper, emb1_full)          # single-table fallback

Author: Capstone 2026 / 속도는벡터 (Tier B production-ready, 2026-05-09).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import PCA

DEFAULT_K: int = 20
DEFAULT_SEED: int = 42


@dataclass
class CCA1DMapper:
    """Container for the fitted CCA-1D (or PCA-1D fallback) projection.

    Attributes
    ----------
    a_x:
        Canonical direction in X-space, shape ``(d1,)``. ``X @ a_x`` recovers
        the top canonical variate ``u``.
    b_y:
        Canonical direction in Y-space, shape ``(d2,)``. ``Y @ b_y`` recovers
        the top canonical variate ``v``. ``None`` when in single-table fallback.
    mean_x:
        Per-feature mean of the training X used for centering at assign time.
    mean_y:
        Per-feature mean of the training Y. ``None`` in fallback mode.
    edges:
        Inner quantile boundaries of ``(u + v) / 2`` (or ``u`` only in fallback)
        on the training set, shape ``(n_strata - 1,)``.
    n_strata:
        Number of strata.
    canonical_correlation:
        First canonical correlation ``rho_1`` on the training samples. ``None``
        in fallback mode.
    fallback_pca:
        ``True`` when ``emb2`` was missing and PCA-1D was used instead.
    """

    a_x: np.ndarray
    b_y: Optional[np.ndarray]
    mean_x: np.ndarray
    mean_y: Optional[np.ndarray]
    edges: np.ndarray
    n_strata: int
    canonical_correlation: Optional[float]
    fallback_pca: bool

    def assign(
        self,
        vectors_x: np.ndarray,
        vectors_y: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Project full-table vectors and bin into strata.

        Parameters
        ----------
        vectors_x:
            Full ``X`` view, shape ``(N, d1)``. Required.
        vectors_y:
            Full ``Y`` view, shape ``(N, d2)``. Required when ``self.b_y`` is
            set (multi-vector mode); ignored in fallback mode.

        Returns
        -------
        np.ndarray
            ``(N,) int32`` stratum ids in ``[0, n_strata)``.
        """
        if vectors_x.ndim != 2:
            raise ValueError(f"vectors_x must be 2D, got shape {vectors_x.shape}")

        x_centered = vectors_x.astype(np.float64) - self.mean_x
        u = x_centered @ self.a_x

        if self.fallback_pca or self.b_y is None:
            scores = u
        else:
            if vectors_y is None:
                raise ValueError(
                    "vectors_y is required for multi-vector CCA assign "
                    "(mapper has b_y set)"
                )
            if vectors_y.ndim != 2:
                raise ValueError(f"vectors_y must be 2D, got shape {vectors_y.shape}")
            if vectors_y.shape[0] != vectors_x.shape[0]:
                raise ValueError(
                    f"vectors_x rows ({vectors_x.shape[0]}) must equal "
                    f"vectors_y rows ({vectors_y.shape[0]})"
                )
            assert self.mean_y is not None  # narrow type
            y_centered = vectors_y.astype(np.float64) - self.mean_y
            v = y_centered @ self.b_y
            scores = (u + v) / 2.0

        sids = np.searchsorted(self.edges, scores, side="right")
        return np.clip(sids, 0, self.n_strata - 1).astype(np.int32)


def fit_cca1d_mapper(
    samples_x: np.ndarray,
    samples_y: Optional[np.ndarray] = None,
    n_strata: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    **_kwargs,
) -> CCA1DMapper:
    """Fit CCA-1D (or PCA-1D fallback) on row-aligned training samples.

    Parameters
    ----------
    samples_x:
        ``(n, d1)`` mean-centered or raw embedding samples (X view).
    samples_y:
        ``(n, d2)`` mean-centered or raw embedding samples (Y view). When
        ``None`` or ``samples_y is samples_x`` we fall back to PCA-1D.
    n_strata:
        Number of strata to discretise the canonical projection into.
    seed:
        Random state forwarded to PCA fallback (CCA NIPALS is deterministic
        once the data are fixed; seed only matters in the fallback path).

    Returns
    -------
    CCA1DMapper
        Fitted mapper. Stores canonical directions, training-set means, and the
        quantile edges of the joint canonical 1D projection.
    """
    if samples_x.ndim != 2:
        raise ValueError(f"samples_x must be 2D, got shape {samples_x.shape}")
    if samples_x.shape[0] < n_strata:
        raise ValueError(
            f"need >= {n_strata} samples, got {samples_x.shape[0]}"
        )

    use_fallback = (
        samples_y is None
        or samples_y is samples_x
        or (
            isinstance(samples_y, np.ndarray)
            and samples_y.shape == samples_x.shape
            and np.shares_memory(samples_y, samples_x)
        )
    )

    samples_x64 = samples_x.astype(np.float64)
    mean_x = samples_x64.mean(axis=0)
    x_centered = samples_x64 - mean_x

    if use_fallback:
        # Single-table fallback: top PCA component on X
        pca = PCA(n_components=1, svd_solver="full", random_state=seed).fit(samples_x64)
        a_x = pca.components_[0].astype(np.float64)  # (d1,)
        scores = x_centered @ a_x
        quantiles = np.quantile(scores, np.linspace(0.0, 1.0, n_strata + 1))
        edges = quantiles[1:-1]
        return CCA1DMapper(
            a_x=a_x,
            b_y=None,
            mean_x=mean_x,
            mean_y=None,
            edges=edges,
            n_strata=n_strata,
            canonical_correlation=None,
            fallback_pca=True,
        )

    # Multi-vector path
    if samples_y.ndim != 2:
        raise ValueError(f"samples_y must be 2D, got shape {samples_y.shape}")
    if samples_y.shape[0] != samples_x.shape[0]:
        raise ValueError(
            f"samples_x rows ({samples_x.shape[0]}) must equal "
            f"samples_y rows ({samples_y.shape[0]})"
        )

    samples_y64 = samples_y.astype(np.float64)
    mean_y = samples_y64.mean(axis=0)

    cca = CCA(n_components=1, max_iter=1000, tol=1e-6)
    # NIPALS handles centering internally but we keep explicit mean tracking for
    # consistent assignment-time behaviour.
    cca.fit(samples_x64, samples_y64)

    # Canonical loadings: cca.x_weights_ (d1, 1), cca.y_weights_ (d2, 1).
    a_x = cca.x_weights_[:, 0].astype(np.float64)
    b_y = cca.y_weights_[:, 0].astype(np.float64)

    u = x_centered @ a_x
    v = (samples_y64 - mean_y) @ b_y

    # Empirical first canonical correlation (training-set diagnostic).
    u_std = float(np.std(u))
    v_std = float(np.std(v))
    if u_std > 0.0 and v_std > 0.0:
        rho = float(np.corrcoef(u, v)[0, 1])
    else:
        rho = 0.0

    joint = (u + v) / 2.0
    quantiles = np.quantile(joint, np.linspace(0.0, 1.0, n_strata + 1))
    edges = quantiles[1:-1]

    return CCA1DMapper(
        a_x=a_x,
        b_y=b_y,
        mean_x=mean_x,
        mean_y=mean_y,
        edges=edges,
        n_strata=n_strata,
        canonical_correlation=rho,
        fallback_pca=False,
    )


def assign_cca1d(
    mapper: CCA1DMapper,
    vectors_x: np.ndarray,
    vectors_y: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Convenience wrapper around :meth:`CCA1DMapper.assign`."""
    return mapper.assign(vectors_x, vectors_y)


def cluster_size_summary(stratum_ids: np.ndarray, n_clusters: int = DEFAULT_K) -> dict:
    """Diagnostic summary of stratum size distribution."""
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
    **kwargs,
) -> np.ndarray:
    """Drop-in stratifier interface compatible with the other Tier B methods.

    Parameters
    ----------
    emb1:
        ``(N, d1)`` first embedding view (always required).
    emb2:
        ``(N, d2)`` second embedding view. ``None`` triggers the PCA-1D
        fallback path documented in :func:`fit_cca1d_mapper`.
    K:
        Number of strata.
    seed:
        Random state.

    Returns
    -------
    np.ndarray
        ``(N,) int32`` stratum ids in ``[0, K)``.
    """
    mapper = fit_cca1d_mapper(emb1, emb2, n_strata=K, seed=seed, **kwargs)
    return assign_cca1d(mapper, emb1, emb2)


def _self_test() -> None:
    """Mini-run: N=10000, d1=96, d2=768 with correlated noise."""
    import warnings

    # macOS Apple Silicon BLAS occasionally emits spurious matmul warnings on
    # numpy >= 2.0; they do not affect numerical correctness.
    np.seterr(all="ignore")
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    rng = np.random.default_rng(0)
    n = 10_000
    d1, d2 = 96, 768
    n_strata = 20

    print(f"[self-test] generating N={n:,} d1={d1} d2={d2} correlated samples")
    # Latent shared signal of rank 4 → induces non-trivial canonical correlation.
    latent_dim = 4
    Z = rng.standard_normal((n, latent_dim)).astype(np.float64)
    W1 = rng.standard_normal((latent_dim, d1)).astype(np.float64) * 0.5
    W2 = rng.standard_normal((latent_dim, d2)).astype(np.float64) * 0.5
    noise1 = rng.standard_normal((n, d1)).astype(np.float64) * 0.3
    noise2 = rng.standard_normal((n, d2)).astype(np.float64) * 0.3
    emb1_64 = Z @ W1 + noise1
    emb2_64 = Z @ W2 + noise2
    emb1 = emb1_64.astype(np.float32)
    emb2 = emb2_64.astype(np.float32)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        np.seterr(all="ignore")

        # Multi-vector path
        mapper = fit_cca1d_mapper(emb1, emb2, n_strata=n_strata, seed=42)
        sids = assign_cca1d(mapper, emb1, emb2)
        summary = cluster_size_summary(sids, n_clusters=n_strata)
        print(
            f"[self-test] CCA multi-vector: rho_1={mapper.canonical_correlation:.4f}, "
            f"sids range=[{sids.min()}, {sids.max()}], "
            f"max/min={summary['max_min_ratio']:.2f}, used={summary['n_used']}/{n_strata}"
        )
        assert sids.min() >= 0 and sids.max() < n_strata
        assert summary["n_used"] == n_strata, (
            f"all {n_strata} strata should be populated, got {summary['n_used']}"
        )
        assert mapper.canonical_correlation is not None
        assert mapper.canonical_correlation > 0.3, (
            f"correlated synthetic data should yield rho_1 > 0.3, "
            f"got {mapper.canonical_correlation:.4f}"
        )

        # Determinism — same input should produce the same mapper
        mapper2 = fit_cca1d_mapper(emb1, emb2, n_strata=n_strata, seed=42)
        sids2 = assign_cca1d(mapper2, emb1, emb2)
        assert np.array_equal(sids, sids2), "CCA-1D should be deterministic"
        print("[self-test] CCA determinism OK")

        # Stratum size distribution should be approximately uniform on training data.
        assert summary["max_min_ratio"] < 1.5, (
            f"quantile binning should produce ~equal sizes, "
            f"got max/min={summary['max_min_ratio']:.2f}"
        )

        # Single-table fallback path (emb2 = None) → PCA-1D
        mapper_fb = fit_cca1d_mapper(emb1, None, n_strata=n_strata, seed=42)
        assert mapper_fb.fallback_pca is True
        assert mapper_fb.b_y is None
        sids_fb = assign_cca1d(mapper_fb, emb1)
        summary_fb = cluster_size_summary(sids_fb, n_clusters=n_strata)
        print(
            f"[self-test] CCA fallback PCA-1D: "
            f"max/min={summary_fb['max_min_ratio']:.2f}, "
            f"used={summary_fb['n_used']}/{n_strata}"
        )
        assert summary_fb["n_used"] == n_strata

        # emb2 = emb1 (same array) should also trigger fallback
        mapper_fb2 = fit_cca1d_mapper(emb1, emb1, n_strata=n_strata, seed=42)
        assert mapper_fb2.fallback_pca is True

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
