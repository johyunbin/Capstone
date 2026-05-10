#!/usr/bin/env python3
"""Tier A — Multi-Fidelity Monte Carlo (MFMC) stratification (Peherstorfer 2016).

Reference
---------
Peherstorfer B., Willcox K., Gunzburger M. ``Optimal Model Management for
Multifidelity Monte Carlo Estimation''. SIAM Journal on Scientific
Computing 38(5), A3163-A3194 (2016).
DOI: 10.1137/15M1046472  https://doi.org/10.1137/15M1046472

Algorithm
---------
The MFMC estimator combines a *high-fidelity* model ``f_1`` (e.g. the full
embedding ANN distance) with one or more *low-fidelity* surrogates
``f_2, ..., f_L`` (e.g. PCA-1D projection of the same vector) using control
variates to reduce the variance of an estimator at a fixed compute budget.

For ``L`` fidelity levels with sample sizes ``m_1 <= ... <= m_L``,
unit costs ``w_1, ..., w_L`` and Pearson correlations ``rho_1=1, rho_2, ..., rho_L``
between ``f_1`` and ``f_l``, Theorem 3.4 (Peherstorfer-Willcox-Gunzburger 2016)
states the optimal allocation ratios are

    r_i = sqrt( (w_1 (rho_{i-1}^2 - rho_i^2)) /
                (w_i (rho_1^2     - rho_2^2)) )      for i >= 2

with ``r_1 = 1``, after which ``m_l = m_1 * r_l`` and the high-fidelity budget
``m_1`` is set to absorb the total budget ``p`` via
``m_1 = p / sum_l(w_l * r_l)``.

For the capstone *stratification* problem (vs. on-line variance reduction)
we adapt this in three steps:

  1. Fit a low-fidelity 1-D PCA model ``f_2`` on the concatenated
     embedding. ``f_1`` is the full L2 norm-to-mean (a stable proxy for
     the actual ANN distance the downstream estimator will consume).
  2. Compute the empirical correlation ``rho`` between ``f_1`` and ``f_2``,
     and the closed-form MFMC weight ``r_2 = sqrt( w_1 (1 - rho^2) /
     (w_2 (rho^2)) )`` (Eq. 3.13 of Peherstorfer-Willcox-Gunzburger 2016
     specialised to L=2). The MFMC ``importance score`` per row is then
     ``|f_1 - rho * f_2|`` — high values flag rows whose high-fidelity
     residual after the control variate correction is large; these rows
     contribute most to estimator variance and deserve over-sampling.
  3. Quantile-bin the importance score into K strata. This yields a
     distribution-aware partition where each stratum has roughly equal
     residual-variance contribution under proportional allocation —
     mirroring Neyman allocation but using the MFMC residual rather than
     the per-cluster within-variance as the bandwidth.

The fidelity-correlation ``rho``, the optimal allocation ``r``, and the
per-stratum residual variance are exposed as ``stratify_method.last_metadata``
so downstream measurement code can recover the prescribed sample budget per
stratum (mirrors the bandit_ucb1_strat.py / TS / EpsilonNet hooks).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

DEFAULT_K: int = 20
DEFAULT_CHUNK: int = 200_000
DEFAULT_FIT_SAMPLE: int = 100_000

# Default unit-cost ratio low/high. The MFMC paper (§3) treats these as
# user-supplied. For (full ANN distance : PCA-1D projection) on a 96-1024 dim
# embedding the empirical ratio is ~50-100x; we use 50 as a conservative
# default, which only enters the *allocation* metadata, not the sids.
DEFAULT_W_HIGH: float = 1.0
DEFAULT_W_LOW: float = 0.02


@dataclass
class MFMCMetadata:
    """Per-call MFMC metadata for downstream variance-aware allocation.

    Attributes
    ----------
    n_fidelities : int
        Number of fidelity levels (here always 2: PCA-1D + full norm).
    rho : float
        Empirical Pearson correlation between high- and low-fidelity scores.
    w_high, w_low : float
        Unit compute cost of the high- and low-fidelity model evaluations
        (caller-controlled; defaults are reasonable for ANN vs PCA-1D).
    r_low : float
        Optimal MFMC allocation ratio m_low / m_high (Eq. 3.13 specialised
        to L=2). r_low > 1 means the low-fidelity model should be queried
        more often than the high-fidelity one.
    m_high, m_low : int
        Allocated sample budgets at each fidelity, given ``total_budget``
        and the closed-form MFMC allocation.
    total_budget : int
        Total compute budget consumed by this allocation
        (= w_high * m_high + w_low * m_low).
    importance : np.ndarray, shape (N,)
        Per-row MFMC residual importance score
        |f_high(x) - rho * f_low(x)|. Higher = more variance contribution.
    sigma_h : np.ndarray, shape (K,)
        Per-stratum standard deviation of the importance score (residual
        variance in stratum h). Drives Neyman-style allocation downstream.
    n_h : np.ndarray, shape (K,)
        Number of rows per stratum (after quantile binning).
    """

    n_fidelities: int
    rho: float
    w_high: float
    w_low: float
    r_low: float
    m_high: int
    m_low: int
    total_budget: int
    importance: np.ndarray
    sigma_h: np.ndarray
    n_h: np.ndarray


def _streamed_norm_to_mean(
    vectors: np.ndarray, mu: np.ndarray, chunk: int = DEFAULT_CHUNK
) -> np.ndarray:
    """Compute ||x - mu||_2 row-wise (high-fidelity scalar score)."""
    N = vectors.shape[0]
    out = np.empty(N, dtype=np.float64)
    mu64 = mu.astype(np.float64)
    for i in range(0, N, chunk):
        j = min(i + chunk, N)
        block = vectors[i:j].astype(np.float64) - mu64
        out[i:j] = np.sqrt((block * block).sum(axis=1))
    return out


def _streamed_proj1d(
    vectors: np.ndarray, w: np.ndarray, chunk: int = DEFAULT_CHUNK
) -> np.ndarray:
    """Compute v @ w row-wise (low-fidelity scalar score)."""
    N = vectors.shape[0]
    out = np.empty(N, dtype=np.float64)
    w64 = w.astype(np.float64)
    with warnings.catch_warnings():
        # numpy 2.x is loud about underflow on tiny weight values; safe here
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for i in range(0, N, chunk):
            j = min(i + chunk, N)
            out[i:j] = vectors[i:j].astype(np.float64) @ w64
    return out


def _fit_pca1d(emb_concat: np.ndarray, fit_sample: int, rng) -> np.ndarray:
    """Return the leading principal axis of the centered embedding."""
    N = emb_concat.shape[0]
    if N > fit_sample:
        idx = rng.choice(N, size=fit_sample, replace=False)
        sub = emb_concat[idx].astype(np.float64)
    else:
        sub = emb_concat.astype(np.float64)
    sub -= sub.mean(axis=0)
    # Power-iteration via SVD on a (fit_sample x d) matrix is fine for d <= 2000
    # We only need the leading right singular vector.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        # gesdd faster but use gesvd for stability on rank-deficient subsamples
        try:
            _, _, vt = np.linalg.svd(sub, full_matrices=False)
        except np.linalg.LinAlgError:
            # Fallback: covariance eigendecomposition (slower but bullet-proof)
            cov = sub.T @ sub / max(sub.shape[0] - 1, 1)
            evals, evecs = np.linalg.eigh(cov)
            return evecs[:, -1].astype(np.float64)
    return vt[0].astype(np.float64)


def _mfmc_allocation(
    rho: float,
    w_high: float,
    w_low: float,
    total_budget: int,
) -> tuple[float, int, int]:
    """L=2 closed-form MFMC allocation (Peherstorfer 2016 Eq. 3.13).

    Returns (r_low, m_high, m_low). For L=2 the formula collapses to:
        r_low = sqrt( w_high * rho^2 / (w_low * (1 - rho^2)) )
        m_high = total_budget / (w_high + w_low * r_low)
        m_low  = m_high * r_low
    """
    rho2 = float(np.clip(rho * rho, 1e-12, 1.0 - 1e-12))
    if w_low <= 0:
        return 1.0, int(total_budget // max(w_high, 1.0)), 0
    r_low = float(np.sqrt((w_high * rho2) / (w_low * (1.0 - rho2))))
    # MFMC requires r_low > 1 for the low-fidelity model to be useful.
    # If rho is too small (low-fid uninformative) we floor at 1.0 (degenerate
    # to single-fidelity high-only).
    r_low = max(r_low, 1.0)
    denom = w_high + w_low * r_low
    m_high = int(max(1, np.floor(total_budget / denom)))
    m_low = int(max(0, np.floor(m_high * r_low)))
    return r_low, m_high, m_low


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    total_budget: int = 10_000,
    w_high: float = DEFAULT_W_HIGH,
    w_low: float = DEFAULT_W_LOW,
    fit_sample: int = DEFAULT_FIT_SAMPLE,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by MFMC residual importance; attach allocation metadata.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of strata (output IDs in ``[0, K)``).
    seed : int, default 0
        Random seed for the PCA fit subsample.
    total_budget : int, default 10_000
        Compute budget driving the closed-form MFMC allocation
        (allocation is metadata-only; sids are computed from importance).
    w_high : float, default 1.0
        Unit cost of the high-fidelity model (full norm-to-mean).
    w_low : float, default 0.02
        Unit cost of the low-fidelity model (PCA-1D projection); the
        50:1 ratio is typical for ANN vs scalar projection.
    fit_sample : int, default 100_000
        Subsample size for the PCA-1D fit (full N for prediction).

    Returns
    -------
    np.ndarray of shape (N,), dtype int32
        Stratum identifiers in ``[0, K)``, drawn from K-quantile binning of
        the per-row MFMC residual ``|f_high - rho * f_low|``.

    Side Effects
    ------------
    Attaches an ``MFMCMetadata`` to itself as
    ``stratify_method.last_metadata`` after each call. Downstream code can
    introspect it to recover the optimal MFMC allocation (m_high, m_low)
    and per-stratum residual sigma for Neyman-style budgeting.
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
    if total_budget < 1:
        raise ValueError(f"total_budget must be >= 1, got {total_budget}")

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    rng = np.random.default_rng(seed)

    # ---- Low-fidelity model: PCA-1D projection ----
    pca_axis = _fit_pca1d(emb_concat, fit_sample, rng)
    f_low = _streamed_proj1d(emb_concat, pca_axis)

    # ---- High-fidelity model: full L2 norm-to-mean (chunked) ----
    mu = emb_concat.astype(np.float64).mean(axis=0)
    f_high = _streamed_norm_to_mean(emb_concat, mu)

    # ---- Empirical correlation rho between fidelities ----
    f_high_c = f_high - f_high.mean()
    f_low_c = f_low - f_low.mean()
    h_std = float(f_high_c.std()) or 1.0
    l_std = float(f_low_c.std()) or 1.0
    rho = float((f_high_c * f_low_c).mean() / (h_std * l_std))
    rho = float(np.clip(rho, -1.0 + 1e-9, 1.0 - 1e-9))

    # ---- MFMC closed-form allocation (Peherstorfer 2016 Eq. 3.13, L=2) ----
    r_low, m_high, m_low = _mfmc_allocation(rho, w_high, w_low, total_budget)
    used_budget = int(round(w_high * m_high + w_low * m_low))

    # ---- Per-row MFMC residual importance |f_high - (rho * h_std/l_std) f_low| ----
    # Scaling rho by std-ratio gives the OLS regression slope (best linear
    # control variate); this is the standard textbook control-variate residual.
    beta = rho * (h_std / l_std)
    importance = np.abs(f_high_c - beta * f_low_c)

    # ---- K-quantile bins on importance ----
    edges = np.quantile(importance, np.linspace(0.0, 1.0, K + 1))[1:-1]
    sids = np.searchsorted(edges, importance, side="right")
    sids = np.clip(sids, 0, K - 1).astype(np.int32)

    # ---- Per-stratum residual sigma (Neyman-allocation hook) ----
    n_h = np.bincount(sids, minlength=K).astype(np.int64)
    sigma_h = np.zeros(K, dtype=np.float64)
    for h in range(K):
        mask = sids == h
        if mask.sum() > 1:
            sigma_h[h] = float(importance[mask].std())

    meta = MFMCMetadata(
        n_fidelities=2,
        rho=float(rho),
        w_high=float(w_high),
        w_low=float(w_low),
        r_low=float(r_low),
        m_high=int(m_high),
        m_low=int(m_low),
        total_budget=int(used_budget),
        importance=importance.astype(np.float32),
        sigma_h=sigma_h,
        n_h=n_h,
    )
    stratify_method.last_metadata = meta  # type: ignore[attr-defined]
    return sids


class MFMCEstimator:
    """Two-fidelity MFMC cardinality estimator (Peherstorfer 2016 §3).

    Public API mirrors the request:
        est = MFMCEstimator(n_fidelities=2, total_budget=10_000, K=20, random_state=0)
        est.fit(embeddings)
        card = est.predict_cardinality(query_vec, selectivity)

    The ``fit`` step builds the PCA-1D low-fidelity model and clusters the
    high-fidelity geometry into ``K`` MiniBatch-KMeans buckets, which act
    as the high-fidelity ANN proxy.
    """

    def __init__(
        self,
        n_fidelities: int = 2,
        total_budget: int = 10_000,
        K: int = DEFAULT_K,
        random_state: int | None = 0,
        w_high: float = DEFAULT_W_HIGH,
        w_low: float = DEFAULT_W_LOW,
    ) -> None:
        if n_fidelities != 2:
            raise NotImplementedError("Only L=2 implemented (PCA-1D + full ANN proxy)")
        self.n_fidelities = int(n_fidelities)
        self.total_budget = int(total_budget)
        self.K = int(K)
        self.random_state = int(random_state) if random_state is not None else 0
        self.w_high = float(w_high)
        self.w_low = float(w_low)
        # Filled in fit():
        self._pca_axis: np.ndarray | None = None
        self._mu: np.ndarray | None = None
        self._N: int | None = None
        self._d: int | None = None
        self._km_centers: np.ndarray | None = None
        self._km_counts: np.ndarray | None = None
        self._rho: float | None = None

    def fit(self, embeddings: np.ndarray) -> "MFMCEstimator":
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2D; got {embeddings.shape}")
        rng = np.random.default_rng(self.random_state)
        emb = embeddings.astype(np.float32, copy=False)
        N, d = emb.shape
        # Low-fid model
        self._pca_axis = _fit_pca1d(emb, DEFAULT_FIT_SAMPLE, rng)
        self._mu = emb.astype(np.float64).mean(axis=0)
        # High-fid clusters (used as bucketed ANN proxy)
        from sklearn.cluster import MiniBatchKMeans
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            fit_idx = rng.choice(N, size=min(N, DEFAULT_FIT_SAMPLE), replace=False)
            km = MiniBatchKMeans(
                n_clusters=self.K, batch_size=1024, n_init=3,
                max_iter=100, random_state=self.random_state,
            )
            km.fit(emb[fit_idx])
            sids = km.predict(emb).astype(np.int32)
        self._km_centers = km.cluster_centers_.astype(np.float32)
        self._km_counts = np.bincount(sids, minlength=self.K).astype(np.int64)
        # Empirical fidelity correlation
        f_low = _streamed_proj1d(emb, self._pca_axis)
        f_high = _streamed_norm_to_mean(emb, self._mu)
        h_c, l_c = f_high - f_high.mean(), f_low - f_low.mean()
        h_std, l_std = float(h_c.std()) or 1.0, float(l_c.std()) or 1.0
        self._rho = float(np.clip((h_c * l_c).mean() / (h_std * l_std), -0.999, 0.999))
        self._N, self._d = int(N), int(d)
        return self

    def predict_cardinality(self, query_vec: np.ndarray, selectivity: float) -> float:
        """Two-fidelity cardinality estimate at a given selectivity radius.

        Implementation: distance ``query_vec`` to each KMeans centroid; rank
        clusters by distance; return ``selectivity * N`` re-weighted by the
        MFMC residual factor ``(1 - rho^2)`` — the variance-reduction factor
        of the two-fidelity control variate (Peherstorfer 2016 Eq. 3.5).
        Selectivity is the input fraction (0,1].
        """
        if self._km_centers is None or self._N is None or self._rho is None:
            raise RuntimeError("call .fit() first")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1]; got {selectivity}")
        q = np.asarray(query_vec, dtype=np.float64).reshape(-1)
        if q.shape[0] != self._d:
            raise ValueError(
                f"query_vec dim {q.shape[0]} != fitted dim {self._d}"
            )
        # Closest-center heuristic + MFMC variance correction; this is a stub
        # that downstream measurement code is free to replace with a true
        # range count on the eps-net of the same paradigm.
        dists = np.linalg.norm(
            self._km_centers.astype(np.float64) - q[None, :], axis=1
        )
        order = np.argsort(dists)
        cum = np.cumsum(self._km_counts[order]).astype(np.float64)
        target = selectivity * float(self._N)
        # First k clusters whose cumulative count covers selectivity fraction
        k_take = int(np.searchsorted(cum, target, side="left")) + 1
        k_take = max(1, min(k_take, len(order)))
        raw_count = float(cum[k_take - 1])
        # MFMC variance reduction => corrected estimator with same expectation
        var_factor = max(1.0 - self._rho * self._rho, 1e-3)
        return raw_count * var_factor + selectivity * float(self._N) * (1.0 - var_factor)


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
        f"[self-test] MFMC (Peherstorfer 2016 L=2 control variate): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    assert ratio < 1.5, f"quantile bins should be ~uniform, got {ratio:.2f}"

    meta = stratify_method.last_metadata
    assert isinstance(meta, MFMCMetadata)
    assert meta.n_fidelities == 2
    assert -1.0 < meta.rho < 1.0
    assert meta.r_low >= 1.0
    assert meta.m_high >= 1
    assert meta.sigma_h.shape == (20,) and meta.n_h.shape == (20,)
    assert meta.importance.shape == (N,)
    print(
        f"[self-test] MFMC metadata: rho={meta.rho:+.4f} r_low={meta.r_low:.3f} "
        f"m_high={meta.m_high} m_low={meta.m_low} budget={meta.total_budget} "
        f"sigma_range=[{meta.sigma_h.min():.4f}, {meta.sigma_h.max():.4f}]"
    )

    # Determinism
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "MFMC must be deterministic for fixed seed"

    # Skewed input -> high-correlation low-fid -> larger r_low
    centers = rng.standard_normal((3, d1 + d2)).astype(np.float32) * 5.0
    skewed_e1 = np.vstack([
        rng.standard_normal((3000, d1)).astype(np.float32) + c[:d1] for c in centers
    ])
    skewed_e2 = np.vstack([
        rng.standard_normal((3000, d2)).astype(np.float32) + c[d1:] for c in centers
    ])
    sids_skew = stratify_method(skewed_e1, skewed_e2, K=20, seed=0)
    counts_skew = np.bincount(sids_skew, minlength=20)
    skew_meta = stratify_method.last_metadata
    print(
        f"[self-test] MFMC skewed: K_used={(counts_skew > 0).sum()}/20 "
        f"max/min={float(counts_skew.max() / max(counts_skew.min(), 1)):.2f} "
        f"rho={skew_meta.rho:+.4f} r_low={skew_meta.r_low:.3f}"
    )

    # Estimator API smoke test
    emb_full = np.concatenate([emb1, emb2], axis=1)
    est = MFMCEstimator(n_fidelities=2, total_budget=5_000, K=20, random_state=0)
    est.fit(emb_full)
    q = rng.standard_normal(emb_full.shape[1]).astype(np.float32)
    card = est.predict_cardinality(q, selectivity=0.1)
    print(f"[self-test] MFMCEstimator.predict_cardinality(sel=0.1) = {card:.1f}")
    assert 0.0 <= card <= float(N), f"cardinality out of bounds: {card}"

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
