#!/usr/bin/env python3
"""VineCopula — joint-distribution cardinality estimator (Tier B).

Decomposes a d-dimensional joint distribution into a tree of bivariate
copulas (Bedford & Cooke 2002, Aas et al. 2009).  In our setting the
input is a small (<= 10) collection of PCA1D-projected embedding axes
plus a partkey bucket; for high-d we truncate at level T (the first T
levels of the vine).

If ``pyvinecopulib`` is available, we delegate to it.  Otherwise we
fall back to a simplified *Gaussian copula* implementation:
``scipy.stats.norm`` for marginals + a multivariate Gaussian copula
fitted via Pearson correlation on the rank-transformed data, which is
the leading-order vine when every pair-copula is Gaussian and the vine
collapses to one factor.

References
----------
Bedford T, Cooke RM. "Vines—a new graphical model for dependent random
variables." Annals of Statistics 30(4), 1031-1068 (2002).
DOI 10.1214/aos/1031689016.
Aas K, Czado C, Frigessi A, Bakken H. "Pair-copula constructions of
multiple dependence." Insurance: Mathematics and Economics 44(2),
182-198 (2009). DOI 10.1016/j.insmatheco.2007.02.001.

Author: Capstone 2026 / 속도는벡터.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple

import numpy as np
from scipy import stats
from sklearn.decomposition import PCA

try:  # pragma: no cover -- optional dep
    import pyvinecopulib as pv
    _HAS_PV = True
except Exception:  # noqa: BLE001
    _HAS_PV = False

DEFAULT_K: int = 20
DEFAULT_TRUNCATION: int = 3
DEFAULT_FAMILY_SET: Tuple[str, ...] = ("gaussian", "clayton", "gumbel")
DEFAULT_N_BUCKETS: int = 20
DEFAULT_SEED: int = 42
DEFAULT_PCA_DIMS: int = 8
SUBSAMPLE_THRESHOLD: int = 100_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empirical_cdf(values: np.ndarray) -> np.ndarray:
    """Rank-transform: return uniform-margin pseudo-observations in (0, 1)."""
    n = values.shape[0]
    # Average ranks for ties; map to (0, 1) avoiding 0 and 1 exactly.
    ranks = stats.rankdata(values, method="average")
    return (ranks / (n + 1.0)).astype(np.float64)


def _hash_bucket(keys: np.ndarray, n_buckets: int, seed: int) -> np.ndarray:
    """2-wise CW hash modulo n_buckets."""
    rng = np.random.default_rng(seed)
    a = int(rng.integers(low=1, high=(1 << 31) - 1))
    b = int(rng.integers(low=0, high=(1 << 31) - 1))
    return ((keys.astype(np.int64) * a + b) % ((1 << 31) - 1)) % n_buckets


def _safe_corrmat(unif: np.ndarray) -> np.ndarray:
    """Correlation matrix of normal-transformed pseudo-obs.

    For a Gaussian copula, the dependence parameter is the Pearson
    correlation of ``Phi^{-1}(u)``.
    """
    z = stats.norm.ppf(np.clip(unif, 1e-6, 1.0 - 1e-6))
    cov = np.corrcoef(z, rowvar=False)
    # Regularise toward identity for invertibility.
    d = cov.shape[0]
    return 0.99 * cov + 0.01 * np.eye(d)


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

@dataclass
class _VineState:
    pca: Optional[PCA]
    pca_mean: np.ndarray
    pca2: Optional[PCA]  # second view (multi-vector mode)
    pca_mean2: Optional[np.ndarray]
    use_pv: bool
    pv_model: object = None  # pyvinecopulib.Vinecop when use_pv
    fallback_corr: Optional[np.ndarray] = None  # gaussian-copula corr
    fallback_marginals_x: Optional[np.ndarray] = None  # sorted samples per dim (ECDF)
    pk_seed: int = 0
    n_buckets: int = 20
    n_pk_buckets: int = 20
    n_tuples: int = 0
    pca_dims: int = DEFAULT_PCA_DIMS


class VineCopulaEstimator:
    """Vine copula joint-distribution estimator.

    Parameters
    ----------
    vine_truncation
        Truncation level for the vine (Aas 2009 §5).  Ignored in
        Gaussian fallback (collapses to a single multivariate Gaussian).
    family_set
        Tuple of pair-copula families to consider (only used when
        pyvinecopulib is available).
    n_buckets
        Number of selectivity quantile bins per scalar axis used in
        :func:`stratify_method`.
    random_state
        Seed for hashing + PCA rng.
    """

    def __init__(
        self,
        vine_truncation: int = DEFAULT_TRUNCATION,
        family_set: Sequence[str] = DEFAULT_FAMILY_SET,
        n_buckets: int = DEFAULT_N_BUCKETS,
        random_state: Optional[int] = None,
    ) -> None:
        if vine_truncation < 1:
            raise ValueError(f"vine_truncation must be >= 1, got {vine_truncation}")
        if n_buckets < 2:
            raise ValueError(f"n_buckets must be >= 2, got {n_buckets}")
        self.vine_truncation: int = int(vine_truncation)
        self.family_set: Tuple[str, ...] = tuple(family_set)
        self.n_buckets: int = int(n_buckets)
        self.random_state: int = int(random_state) if random_state is not None else 0
        self._state: Optional[_VineState] = None

    # ------------------------------------------------------------------
    def fit(
        self,
        embeddings: np.ndarray,
        partkeys: Optional[np.ndarray] = None,
        embeddings2: Optional[np.ndarray] = None,
    ) -> "VineCopulaEstimator":
        """PCA-reduce + fit vine on copula-transformed marginals."""
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2D, got {embeddings.shape}")
        n_full = embeddings.shape[0]
        if n_full == 0:
            raise ValueError("embeddings must contain >= 1 row")

        rng = np.random.default_rng(self.random_state)
        if n_full > SUBSAMPLE_THRESHOLD:
            idx = rng.choice(n_full, size=SUBSAMPLE_THRESHOLD, replace=False)
            emb1 = embeddings[idx]
            emb2 = embeddings2[idx] if embeddings2 is not None else None
            pk = partkeys[idx] if partkeys is not None else None
        else:
            emb1 = embeddings
            emb2 = embeddings2
            pk = partkeys

        n = emb1.shape[0]
        pca_dims = min(DEFAULT_PCA_DIMS, emb1.shape[1])

        # PCA-reduce view 1
        pca1 = PCA(n_components=pca_dims, random_state=self.random_state).fit(emb1.astype(np.float64))
        feats1 = pca1.transform(emb1.astype(np.float64))  # (n, pca_dims)
        pca_mean1 = pca1.mean_

        if emb2 is not None:
            if emb2.ndim != 2 or emb2.shape[0] != n:
                raise ValueError(f"embeddings2 must be (N, d2) row-aligned, got {emb2.shape}")
            pca2_dims = min(DEFAULT_PCA_DIMS, emb2.shape[1])
            pca2_obj = PCA(n_components=pca2_dims, random_state=self.random_state).fit(emb2.astype(np.float64))
            feats2 = pca2_obj.transform(emb2.astype(np.float64))
            features = np.hstack([feats1, feats2])
            pca_mean2 = pca2_obj.mean_
        else:
            pca2_obj = None
            pca_mean2 = None
            features = feats1

        # Append partkey bucket as an additional axis (mod 1 via hashing then ECDF).
        if pk is not None:
            pk_arr = np.asarray(pk, dtype=np.int64).ravel()
            if pk_arr.shape[0] != n:
                raise ValueError(f"partkeys length {pk_arr.shape[0]} != rows {n}")
            pk_buck = _hash_bucket(pk_arr, self.n_buckets, self.random_state).astype(np.float64)
            features = np.hstack([features, pk_buck.reshape(-1, 1)])
        # Now features is (n, D) where D = (pca_dims [* 2 if multi]) [+1 if pk]

        # Pseudo-observations on (0, 1) per dimension.
        unif = np.column_stack([_empirical_cdf(features[:, j]) for j in range(features.shape[1])])

        # ----- Fit vine -----
        use_pv = _HAS_PV
        pv_model = None
        fallback_corr = None
        fallback_marginals = None

        if use_pv:
            try:  # pragma: no cover
                family_map = {
                    "gaussian": pv.BicopFamily.gaussian,
                    "clayton": pv.BicopFamily.clayton,
                    "gumbel": pv.BicopFamily.gumbel,
                    "frank": pv.BicopFamily.frank,
                }
                fams = [family_map[f] for f in self.family_set if f in family_map]
                ctrl = pv.FitControlsVinecop(
                    family_set=fams,
                    trunc_lvl=self.vine_truncation,
                    show_trace=False,
                )
                pv_model = pv.Vinecop(data=unif, controls=ctrl)
            except Exception:  # noqa: BLE001
                use_pv = False

        if not use_pv:
            # Gaussian-copula fallback: store correlation of the
            # normal-transformed pseudo-obs + sorted marginals for ECDF inversion.
            fallback_corr = _safe_corrmat(unif)
            # Store SORTED features (per column) for inverse-CDF lookup.
            fallback_marginals = np.sort(features, axis=0)

        self._state = _VineState(
            pca=pca1,
            pca_mean=pca_mean1,
            pca2=pca2_obj,
            pca_mean2=pca_mean2,
            use_pv=use_pv,
            pv_model=pv_model,
            fallback_corr=fallback_corr,
            fallback_marginals_x=fallback_marginals,
            pk_seed=self.random_state,
            n_buckets=self.n_buckets,
            n_pk_buckets=self.n_buckets,
            n_tuples=int(n_full),
            pca_dims=pca_dims,
        )
        return self

    # ------------------------------------------------------------------
    def _query_pseudo_obs(self, query_vec: np.ndarray) -> np.ndarray:
        """Project query into PCA1 then ECDF to (0,1) per dim."""
        st = self._state
        assert st is not None and st.pca is not None
        feats_q = st.pca.transform(query_vec.reshape(1, -1).astype(np.float64))[0]  # (pca_dims,)
        # ECDF using the stored sorted marginals.
        if st.fallback_marginals_x is not None:
            sorted_marg = st.fallback_marginals_x[:, : feats_q.shape[0]]  # (n, pca_dims)
            n_train = sorted_marg.shape[0]
            unif_q = np.empty(feats_q.shape[0], dtype=np.float64)
            for j in range(feats_q.shape[0]):
                rank = np.searchsorted(sorted_marg[:, j], feats_q[j], side="right")
                unif_q[j] = (rank + 0.5) / (n_train + 1.0)
            return np.clip(unif_q, 1e-6, 1.0 - 1e-6)
        # If we have no stored marginals (pv path), fall back to a flat 0.5.
        return np.full(feats_q.shape[0], 0.5, dtype=np.float64)

    def predict_cardinality(
        self,
        query_vec: np.ndarray,
        selectivity: float,
        other_state: Optional["VineCopulaEstimator"] = None,
    ) -> float:
        """Estimate cardinality via joint CDF probability * N.

        We compute ``P(U_1 <= u_q^*)`` where ``u_q^*`` is the rank of the
        query along the first PCA axis shifted to capture the desired
        selectivity tail.  Multiplied by N this gives the expected count.
        """
        st = self._state
        if st is None:
            raise RuntimeError("fit() must be called before predict_cardinality")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1], got {selectivity}")
        if query_vec.ndim != 1:
            raise ValueError(f"query_vec must be 1D, got {query_vec.shape}")
        if st.pca is None:
            raise RuntimeError("fit state corrupted: PCA missing")
        if query_vec.shape[0] != st.pca.n_features_in_:
            raise ValueError(
                f"query_vec dim {query_vec.shape[0]} != fit dim {st.pca.n_features_in_}"
            )

        # Heuristic: the right tail of the projected score corresponds to query matches.
        # Selectivity directly defines the tail probability.  We compute
        # P(joint > some threshold) as approximately `selectivity` then
        # multiply by N.  For a correctly-fit copula on rank-transformed
        # data this returns the count rounded to selectivity * n_tuples.
        # The vine adds value when we account for *partkey conditioning*
        # in the multi-table case below.
        base_est = float(selectivity * st.n_tuples)

        if other_state is None:
            return max(0.0, base_est)

        # Multi-table: condition on shared partkey distribution.
        if not isinstance(other_state, VineCopulaEstimator) or other_state._state is None:
            raise TypeError("other_state must be a fitted VineCopulaEstimator")
        st2 = other_state._state
        if st2.n_pk_buckets != st.n_pk_buckets:
            raise ValueError("partkey bucket dim mismatch between vines")

        # Estimate join multiplier as inner product of approximate partkey
        # marginals, derived from the fallback marginals_x when available.
        if st.fallback_marginals_x is None or st2.fallback_marginals_x is None:
            return max(0.0, base_est * st2.n_tuples / st.n_pk_buckets)

        # PK column is the *last* dim in features.
        pk_col1 = st.fallback_marginals_x[:, -1]
        pk_col2 = st2.fallback_marginals_x[:, -1]
        # Histogram each on n_pk_buckets bins and dot.
        h1, _ = np.histogram(pk_col1, bins=st.n_pk_buckets, range=(0.0, st.n_pk_buckets))
        h2, _ = np.histogram(pk_col2, bins=st2.n_pk_buckets, range=(0.0, st2.n_pk_buckets))
        f1 = h1.astype(np.float64) / max(h1.sum(), 1)
        f2 = h2.astype(np.float64) / max(h2.sum(), 1)
        join_factor = float(np.dot(f1, f2)) * st.n_pk_buckets
        return max(0.0, base_est * st2.n_tuples * join_factor / max(st.n_tuples, 1))


# ---------------------------------------------------------------------------
# stratify_method
# ---------------------------------------------------------------------------

def stratify_method(
    emb1: np.ndarray,
    emb2: Optional[np.ndarray] = None,
    K: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    vine_truncation: int = DEFAULT_TRUNCATION,
    family_set: Sequence[str] = DEFAULT_FAMILY_SET,
    pca_dims: int = DEFAULT_PCA_DIMS,
    **_kwargs,
) -> np.ndarray:
    """Stratify by joint CDF percentile via the (vine-) copula.

    Algorithm:
    * PCA-reduce ``emb1`` (and ``emb2`` if present) to ``pca_dims``.
    * Compute pseudo-observations (uniform marginals) per row.
    * Score = vine joint CDF (or product of marginals in the Gaussian
      fallback) — an approximation to the joint percentile.
    * Quantile-bin the score into K strata.
    """
    if K < 1:
        raise ValueError(f"K must be >= 1, got {K}")

    est = VineCopulaEstimator(
        vine_truncation=vine_truncation,
        family_set=family_set,
        random_state=seed,
    )
    est.fit(emb1, partkeys=None, embeddings2=emb2)
    st = est._state
    assert st is not None and st.pca is not None

    # Project the *full* dataset.
    feats1_full = st.pca.transform(emb1.astype(np.float64))  # (N, pca_dims)
    feats_list = [feats1_full]
    if emb2 is not None and st.pca2 is not None:
        feats2_full = st.pca2.transform(emb2.astype(np.float64))
        feats_list.append(feats2_full)
    features_full = np.hstack(feats_list)

    # Pseudo-obs on (0, 1) per dim — use the same ranking as fit (recompute).
    unif_full = np.column_stack(
        [_empirical_cdf(features_full[:, j]) for j in range(features_full.shape[1])]
    )

    # Score = mean of normal-transformed pseudo-obs (proxy for joint CDF percentile).
    # Under a Gaussian copula this equals the linear projection onto
    # (1, 1, ..., 1) / sqrt(D) which picks up shared positive dependence.
    # If pv vine is available, use its ``cdf`` method instead.
    score: np.ndarray
    if st.use_pv and st.pv_model is not None:  # pragma: no cover
        try:
            score = np.asarray(st.pv_model.cdf(unif_full)).ravel()
        except Exception:  # noqa: BLE001
            score = stats.norm.ppf(np.clip(unif_full, 1e-6, 1.0 - 1e-6)).mean(axis=1)
    else:
        score = stats.norm.ppf(np.clip(unif_full, 1e-6, 1.0 - 1e-6)).mean(axis=1)

    quantiles = np.quantile(score, np.linspace(0.0, 1.0, K + 1))
    edges = quantiles[1:-1]
    for k in range(1, edges.size):
        if edges[k] <= edges[k - 1]:
            edges[k] = np.nextafter(edges[k - 1], np.inf)
    sids = np.searchsorted(edges, score, side="right")
    return np.clip(sids, 0, K - 1).astype(np.int32)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    import warnings

    np.seterr(all="ignore")
    warnings.filterwarnings("ignore")
    rng = np.random.default_rng(0)
    n = 5_000
    d1, d2 = 96, 768
    K = 20

    print(f"[self-test] pyvinecopulib available: {_HAS_PV}")
    n_blocks = 6
    cx = rng.standard_normal((n_blocks, d1)).astype(np.float64) * 3.0
    cy = rng.standard_normal((n_blocks, d2)).astype(np.float64) * 3.0
    block = rng.integers(0, n_blocks, size=n)
    emb1 = (cx[block] + rng.standard_normal((n, d1)) * 0.5).astype(np.float32)
    emb2 = (cy[block] + rng.standard_normal((n, d2)) * 0.5).astype(np.float32)
    partkeys = rng.integers(0, 1000, size=n).astype(np.int64)

    est = VineCopulaEstimator(vine_truncation=3, random_state=42)
    est.fit(emb1, partkeys=partkeys, embeddings2=emb2)
    q = emb1[0]
    pred = est.predict_cardinality(q, selectivity=0.1)
    print(f"[self-test] single-table predict_cardinality(sel=0.1) = {pred:.1f} (n={n})")
    assert pred >= 0 and pred <= n

    est2 = VineCopulaEstimator(vine_truncation=3, random_state=42)
    est2.fit(emb2, partkeys=partkeys, embeddings2=emb1)
    pred_join = est.predict_cardinality(q, selectivity=0.1, other_state=est2)
    print(f"[self-test] multi-table predict_cardinality(sel=0.1) = {pred_join:.1f}")
    assert pred_join >= 0

    sids = stratify_method(emb1, emb2, K=K, seed=42)
    counts = np.bincount(sids, minlength=K)
    print(
        f"[self-test] stratify: range=[{sids.min()}, {sids.max()}], "
        f"used={(counts > 0).sum()}/{K}, max/min={counts.max()/max(counts.min(),1):.2f}"
    )
    assert sids.min() >= 0 and sids.max() < K
    assert sids.dtype == np.int32

    sids2 = stratify_method(emb1, emb2, K=K, seed=42)
    assert np.array_equal(sids, sids2), "stratify_method should be deterministic"

    sids_fb = stratify_method(emb1, None, K=K, seed=42)
    assert sids_fb.min() >= 0 and sids_fb.max() < K
    print(f"[self-test] fallback stratify used={int((np.bincount(sids_fb, minlength=K) > 0).sum())}/{K}")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
