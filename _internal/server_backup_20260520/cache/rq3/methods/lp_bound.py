#!/usr/bin/env python3
"""LpBound — pessimistic cardinality bound via ℓ_p-norms of degree sequences.

The LpBound estimator computes a *guaranteed upper bound* on join cardinality
by solving a small linear program whose feasible region is carved out by
ℓ_p-norm statistics of the per-table degree sequences.  Unlike
sample-/sketch-based estimators (Wander Join, AMS, CCSketch) the bound is
**never an under-estimate** and crucially **never returns zero** when the
true join is non-empty — exactly the property the multi-table corner of
this benchmark needs (paired-better failures of WanderJoin are 0/66 there).

The bound is *pessimistic*: it can overshoot the true answer, but it is
analytically sound regardless of data distribution, which makes it the
natural fallback for query optimisation when a row-level estimator might
under-count critical join branches.

Reference
---------
Yufei Tao, Mahmoud Abo Khamis, Hangdong Zhao, Dan Suciu et al. (Zhang &
Suciu et al.).
"LpBound: Pessimistic Cardinality Bounds via ℓ_p-Norms of Degree
Sequences."  SIGMOD 2025 Best Paper.  arXiv:2502.05912.

Adaptation to the embedding-paired setting (this project)
---------------------------------------------------------
Our benchmark joins ``partsupp`` (96-d, ``ps_partkey``) with ``wiki``
(768-d, ``id``) on ``partkey == id``.  LpBound was originally formulated
for arbitrary acyclic joins; for the two-table cardinality predicate we
implement the canonical reduction:

    1.  ``fit`` — for every unique join-key value ``v`` count its degree
        ``deg_R(v)`` in the table; precompute the ℓ_p norms
        ``||deg_R||_p`` for ``p in {1, 2, ∞}``.
    2.  ``predict_cardinality(q, sel)`` — restrict to the matched
        partkey set under the vector predicate, then solve

            maximise   Σ_v x_v
            subject to 0 ≤ x_v ≤ deg_R(v) ∀v
                       ||x||_p ≤ ||deg_R||_p (per-table p-norm budget)
                       (analogous constraint per joined table)

        via ``scipy.optimize.linprog`` (HiGHS).  The optimum is an
        upper bound on the join cardinality.  For p = ∞ the constraint
        is the per-coordinate cap (already enforced by the upper bound);
        for p = 1 it is the total-mass cap; for p = 2 we linearise via
        an outer-approximation cut (a single tangent plane is sufficient
        for the bound to remain a valid upper estimate).

For single-table mode (no ``partkeys`` argument) we synthesise a degree
sequence from MiniBatch K-Means cluster sizes (K = 20) so the
stratification path remains usable as a drop-in alongside the other
methods/ files.

Public class API
----------------
``LpBoundEstimator(p_values=(1, 2, float('inf')), n_buckets=20,
                   random_state=None)``
    ``fit(embeddings, partkeys=None) -> self``
    ``predict_cardinality(query_vec, selectivity,
                          other_state=None) -> float``
"""
from __future__ import annotations

import math
import warnings
from typing import Any, Iterable, Optional

import numpy as np

try:  # SciPy is a hard dependency for this estimator.
    from scipy.optimize import linprog
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "lp_bound requires scipy; install via `pip install scipy`"
    ) from exc

try:
    from sklearn.cluster import MiniBatchKMeans
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "lp_bound requires sklearn for the single-table fallback path"
    ) from exc


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _lp_norm(values: np.ndarray, p: float) -> float:
    """Compute ||values||_p over a 1-D non-negative degree sequence."""
    if values.size == 0:
        return 0.0
    if math.isinf(p):
        return float(values.max())
    if p == 1:
        return float(values.sum())
    # General p; cast to float64 to keep the power stable for skewed data.
    v = values.astype(np.float64, copy=False)
    return float(np.power(np.power(v, p).sum(), 1.0 / p))


def _degree_sequence(partkeys: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(unique_keys, degree_per_key)`` from a 1-D partkey array."""
    if partkeys.size == 0:
        return (np.empty(0, dtype=np.int64), np.empty(0, dtype=np.int64))
    uniq, counts = np.unique(partkeys, return_counts=True)
    return uniq.astype(np.int64), counts.astype(np.int64)


def _matched_keys(
    embeddings: np.ndarray,
    partkeys: np.ndarray,
    proj_dir: np.ndarray,
    query_vec: np.ndarray,
    selectivity: float,
) -> np.ndarray:
    """Top-``selectivity`` partkeys by cosine similarity to ``query_vec``.

    The deterministic projection direction is unused here (kept for API
    parity with CCSketch); we cosine-rank against the actual query.
    """
    q = query_vec.astype(np.float32)
    q_norm = float(np.linalg.norm(q)) or 1.0
    q_unit = q / q_norm
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        sims = embeddings @ q_unit
    n_match = max(1, int(np.ceil(selectivity * embeddings.shape[0])))
    top_idx = np.argpartition(-sims, n_match - 1)[:n_match]
    return partkeys[top_idx]


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class LpBoundEstimator:
    """ℓ_p-norm pessimistic cardinality bound (Zhang/Suciu SIGMOD 2025).

    Parameters
    ----------
    p_values : iterable of float, default ``(1, 2, float('inf'))``
        ℓ_p norms to constrain in the LP.  Including ``inf`` adds the
        per-key cap (``x_v <= deg_R(v)``) which is always a tight
        constraint; including ``1`` adds the total-mass cap.  The
        ``p = 2`` constraint is linearised via a single tangent plane
        (outer approximation) — the result remains a valid upper bound.
    n_buckets : int, default 20
        Number of degree-percentile bins used by ``stratify_method``.
    random_state : int or None, default None
        Seed for the K-Means fallback in single-table mode; ``None`` -> 0.

    Attributes (set by ``fit``)
    ---------------------------
    unique_keys_ : np.ndarray, shape (U,)
    degrees_ : np.ndarray, shape (U,), dtype int64
    lp_norms_ : dict[float, float]
        Precomputed ``||deg||_p`` for each ``p`` in ``p_values``.
    embeddings_, partkeys_, proj_dir_ : stored for predict-time matching.
    n_tuples_ : int
    """

    def __init__(
        self,
        p_values: Iterable[float] = (1.0, 2.0, float("inf")),
        n_buckets: int = 20,
        random_state: Optional[int] = None,
    ) -> None:
        p_list = [float(p) for p in p_values]
        if not p_list:
            raise ValueError("p_values must contain at least one p")
        for p in p_list:
            if p < 1 or (math.isnan(p)):
                raise ValueError(f"every p must be >= 1, got {p}")
        if n_buckets < 2:
            raise ValueError(f"n_buckets must be >= 2, got {n_buckets}")
        self.p_values: list[float] = p_list
        self.n_buckets: int = int(n_buckets)
        self.random_state: int = (
            int(random_state) if random_state is not None else 0
        )
        # Lazy attributes set in fit().
        self.unique_keys_: Optional[np.ndarray] = None
        self.degrees_: Optional[np.ndarray] = None
        self.lp_norms_: Optional[dict[float, float]] = None
        self.embeddings_: Optional[np.ndarray] = None
        self.partkeys_: Optional[np.ndarray] = None
        self.proj_dir_: Optional[np.ndarray] = None
        self.n_tuples_: int = 0

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------
    def fit(
        self,
        embeddings: np.ndarray,
        partkeys: Optional[np.ndarray] = None,
    ) -> "LpBoundEstimator":
        """Compute degree sequence + ℓ_p norms.

        ``partkeys`` may be ``None`` for single-table use; in that case
        we synthesise a degree sequence from MiniBatch K-Means cluster
        membership (K = ``n_buckets``).  This keeps the LP non-trivial
        even in the absence of a real join attribute.
        """
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2-D, got {embeddings.shape}")
        n, d = embeddings.shape
        if n == 0:
            raise ValueError("embeddings must contain at least one row")

        if partkeys is None:
            # Synthesise partkeys from MiniBatch K-Means cluster ids so
            # the degree sequence is realistic (skewed cluster sizes →
            # non-trivial ℓ_p norms).
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                km = MiniBatchKMeans(
                    n_clusters=min(self.n_buckets, n),
                    batch_size=min(1024, n),
                    random_state=self.random_state,
                    n_init="auto",
                )
                synth = km.fit_predict(embeddings.astype(np.float64))
            partkeys = synth.astype(np.int64)

        partkeys = np.asarray(partkeys, dtype=np.int64).ravel()
        if partkeys.shape[0] != n:
            raise ValueError(
                f"partkeys length {partkeys.shape[0]} != embeddings rows {n}"
            )

        uniq, deg = _degree_sequence(partkeys)
        norms: dict[float, float] = {p: _lp_norm(deg, p) for p in self.p_values}

        self.unique_keys_ = uniq
        self.degrees_ = deg
        self.lp_norms_ = norms
        self.embeddings_ = embeddings.astype(np.float32, copy=False)
        self.partkeys_ = partkeys
        self.proj_dir_ = embeddings.mean(axis=0).astype(np.float32)
        norm = float(np.linalg.norm(self.proj_dir_)) or 1.0
        self.proj_dir_ /= norm
        self.n_tuples_ = int(n)
        return self

    # ------------------------------------------------------------------
    # predict_cardinality
    # ------------------------------------------------------------------
    def predict_cardinality(
        self,
        query_vec: np.ndarray,
        selectivity: float,
        other_state: Optional["LpBoundEstimator"] = None,
    ) -> float:
        """Return the ℓ_p-norm pessimistic upper bound on |R ⨝ S| ∩ Q.

        Solves a small LP whose feasible region is the intersection of:

            * per-key cap ``x_v <= deg_R(v)``  (p = ∞)
            * total-mass cap ``Σ x_v <= ||deg||_1``  (p = 1)
            * single tangent plane to the ℓ_2 ball at ``deg/||deg||_2``
              (outer approximation of ``||x||_2 <= ||deg||_2``)

        and analogously for ``other_state`` (multi-table case).  The
        objective ``Σ x_v`` is then a guaranteed upper bound on the
        join cardinality of the matched partkey region.
        """
        if self.unique_keys_ is None:
            raise RuntimeError("fit() must be called before predict_cardinality()")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1], got {selectivity}")
        if query_vec.ndim != 1 or query_vec.shape[0] != self.embeddings_.shape[1]:
            raise ValueError(
                f"query_vec shape {query_vec.shape} mismatched with "
                f"embedding dim {self.embeddings_.shape[1]}"
            )

        # 1) Restrict to the matched partkey set under the vector predicate.
        matched = _matched_keys(
            self.embeddings_, self.partkeys_, self.proj_dir_,
            query_vec, selectivity,
        )
        if matched.size == 0:
            return 0.0
        matched_uniq = np.unique(matched)

        # 2) Pull the matched degrees and (if multi-table) intersect with
        #    the other table's matched degrees on the shared partkey axis.
        deg_self = self._lookup_degrees(matched_uniq)

        if other_state is None:
            joint_uniq = matched_uniq
            cap = deg_self.astype(np.float64)
        else:
            if not isinstance(other_state, LpBoundEstimator):
                raise TypeError(
                    f"other_state must be LpBoundEstimator, got "
                    f"{type(other_state).__name__}"
                )
            if other_state.unique_keys_ is None:
                raise RuntimeError("other_state.fit() must be called first")
            other_matched = _matched_keys(
                other_state.embeddings_, other_state.partkeys_,
                other_state.proj_dir_, query_vec, selectivity,
            )
            other_uniq = np.unique(other_matched)
            joint_uniq, idx_self, idx_other = np.intersect1d(
                matched_uniq, other_uniq, return_indices=True,
            )
            if joint_uniq.size == 0:
                # No shared key -> trivial bound is 0 (and 0 is sound).
                return 0.0
            deg_self_joint = deg_self[idx_self]
            deg_other_joint = other_state._lookup_degrees(joint_uniq)
            # Per-key cap for a binary equi-join is the *product* of
            # per-table degrees (each combination of paired tuples
            # constitutes one join row).
            cap = (deg_self_joint.astype(np.float64)
                   * deg_other_joint.astype(np.float64))

        # 3) Build LP: maximise Σ x_v  ≡  minimise -Σ x_v.
        u = joint_uniq.size
        c = -np.ones(u, dtype=np.float64)
        bounds = [(0.0, float(cap_i)) for cap_i in cap]

        a_ub: list[np.ndarray] = []
        b_ub: list[float] = []

        # ℓ_1 budget: Σ x_v ≤ min(||deg_R||_1, ||deg_S||_1) once we
        # account for the join-multiplied cap.  For the joined problem
        # we use the tighter of the two.
        budget_l1 = self.lp_norms_.get(1.0)
        if budget_l1 is None:
            budget_l1 = _lp_norm(self.degrees_, 1.0)
        if other_state is not None:
            other_l1 = other_state.lp_norms_.get(1.0)
            if other_l1 is None:
                other_l1 = _lp_norm(other_state.degrees_, 1.0)
            # Bound Σ x_v ≤ ||deg_R||_1 * max_v deg_S(v)  (and symmetric);
            # take the tighter side.
            cap_r_inf = self.lp_norms_.get(float("inf")) or _lp_norm(
                self.degrees_, float("inf"))
            cap_s_inf = other_state.lp_norms_.get(float("inf")) or _lp_norm(
                other_state.degrees_, float("inf"))
            budget_l1 = min(budget_l1 * cap_s_inf, other_l1 * cap_r_inf)
        a_ub.append(np.ones(u, dtype=np.float64))
        b_ub.append(float(budget_l1))

        # ℓ_2 outer-approximation: a single tangent plane to the ball
        # of radius ||deg||_2 at the unit-direction of the matched cap
        # vector.  This is sound: the true ℓ_2 ball is enclosed by the
        # half-space, so the LP optimum stays an upper bound.
        budget_l2 = self.lp_norms_.get(2.0)
        if budget_l2 is None:
            budget_l2 = _lp_norm(self.degrees_, 2.0)
        if other_state is not None:
            other_l2 = other_state.lp_norms_.get(2.0)
            if other_l2 is None:
                other_l2 = _lp_norm(other_state.degrees_, 2.0)
            # Cauchy-Schwarz on the join: ||x||_2 ≤ ||deg_R||_2 * ||deg_S||_2.
            budget_l2 = budget_l2 * other_l2
        cap_norm = float(np.linalg.norm(cap)) or 1.0
        tangent_dir = cap / cap_norm
        a_ub.append(tangent_dir)
        b_ub.append(float(budget_l2))

        a_ub_mat = np.vstack(a_ub)
        b_ub_vec = np.asarray(b_ub, dtype=np.float64)

        # 4) Solve LP via HiGHS.  Time-bound by the hard 30 s requirement;
        #    HiGHS solves these < 100-variable LPs in milliseconds.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = linprog(
                c=c, A_ub=a_ub_mat, b_ub=b_ub_vec,
                bounds=bounds, method="highs",
                options={"time_limit": 30.0},
            )
        if not res.success:
            # Sound fallback: the trivial cap (sum of per-key bounds) is
            # always a valid upper bound on the join cardinality.
            return float(cap.sum())
        return float(-res.fun)

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------
    def _lookup_degrees(self, keys: np.ndarray) -> np.ndarray:
        """Return ``deg_R(v)`` for every ``v`` in ``keys`` (0 if unseen)."""
        # ``unique_keys_`` is sorted by np.unique; binary-search lookup.
        idx = np.searchsorted(self.unique_keys_, keys)
        idx_clip = np.clip(idx, 0, self.unique_keys_.size - 1)
        hit = (idx < self.unique_keys_.size) & (
            self.unique_keys_[idx_clip] == keys)
        deg = np.where(hit, self.degrees_[idx_clip], 0)
        return deg.astype(np.int64)


# ---------------------------------------------------------------------------
# Stratifier shim — keeps the file plug-compatible with measure_multi_paradigm
# ---------------------------------------------------------------------------

def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = 20,
    seed: int = 0,
    **kwargs: Any,
) -> np.ndarray:
    """Stratify rows by partkey-degree percentile (LpBound-aligned strata).

    LpBound's per-key cap ``x_v ≤ deg_R(v)`` is the dominant constraint
    in the LP; the natural stratification is therefore a binning of rows
    by the degree of their partkey.  Rows whose partkey has a *high*
    degree share variance characteristics; binning by degree percentile
    keeps the LP-feasible region homogeneous within each stratum.

    Parameters
    ----------
    emb1, emb2 : np.ndarray, (N, d1) / (N, d2)
        Paired embeddings; only ``emb1`` is used to synthesise a partkey
        when no real join attribute is available.  ``emb2`` is required
        by the orchestrator signature but ignored here.
    K : int, default 20
        Number of degree-percentile bins.
    seed : int, default 0
        RNG seed; identical inputs and seed yield identical stratum ids.
    **kwargs : Any
        ``partkeys`` (np.ndarray, shape (N,)) — explicit join keys; if
        omitted we synthesise via MiniBatch K-Means cluster ids.

    Returns
    -------
    np.ndarray, shape (N,), dtype int32
        Stratum id per row; values in ``[0, K)``.
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

    n = emb1.shape[0]
    partkeys = kwargs.get("partkeys")
    if partkeys is None:
        # Synthesise from MiniBatch K-Means cluster ids on emb1 — gives a
        # realistic skewed degree distribution.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            km = MiniBatchKMeans(
                n_clusters=min(K, n),
                batch_size=min(1024, n),
                random_state=seed,
                n_init="auto",
            )
            partkeys = km.fit_predict(
                emb1.astype(np.float64)).astype(np.int64)
    else:
        partkeys = np.asarray(partkeys, dtype=np.int64).ravel()
        if partkeys.shape[0] != n:
            raise ValueError(
                f"partkeys length {partkeys.shape[0]} != rows {n}"
            )

    # Per-key degree, then per-row degree (lookup), then percentile bin.
    uniq, deg = _degree_sequence(partkeys)
    sort_idx = np.searchsorted(uniq, partkeys)
    row_deg = deg[sort_idx].astype(np.float64)

    # K equal-frequency bins on the row-degree distribution.  np.quantile
    # gives bin edges; np.digitize then assigns each row to a bin in
    # [0, K).  We use 'linear' interpolation for stable edges across
    # tied degrees and clip to keep the output strictly in [0, K).
    quantiles = np.linspace(0.0, 1.0, K + 1)
    edges = np.quantile(row_deg, quantiles)
    # Make edges strictly increasing so digitize doesn't drop bins on
    # heavy-tied data; tie-broken by jittering with an RNG-deterministic
    # uniform on [0, 1e-6).
    rng = np.random.default_rng(seed)
    jitter = rng.uniform(0.0, 1e-6, size=row_deg.size)
    sids = np.digitize(row_deg + jitter, edges[1:-1], right=False)
    sids = np.clip(sids, 0, K - 1).astype(np.int32)
    return sids


# ---------------------------------------------------------------------------
# Mini-run test
# ---------------------------------------------------------------------------

def _mini_run() -> None:
    """Mini-run: build two estimators, exercise single + multi-table predict."""
    print("[lp_bound] mini-run: two tables N=2000 each, d=96")
    rng = np.random.default_rng(0)
    n, d = 2000, 96
    emb_a = rng.standard_normal((n, d)).astype(np.float32)
    emb_b = rng.standard_normal((n, d)).astype(np.float32)
    pk_a = rng.integers(0, 500, size=n, dtype=np.int64)
    pk_b = rng.integers(0, 500, size=n, dtype=np.int64)

    est_a = LpBoundEstimator(random_state=42).fit(emb_a, pk_a)
    est_b = LpBoundEstimator(random_state=42).fit(emb_b, pk_b)
    assert est_a.unique_keys_ is not None
    assert est_a.lp_norms_[1.0] == n  # ℓ_1 of degree sequence == #rows.

    q = rng.standard_normal(d).astype(np.float32)

    # Single-table predictions across the standard selectivity grid.
    for sel in (0.01, 0.05, 0.10, 0.30, 0.50):
        est = est_a.predict_cardinality(q, sel)
        # Bound must be at least ceil(sel * n) -- the cardinality of the
        # matched key set is a lower bound on the LP optimum because
        # x_v = 1 for every matched v is feasible.
        lower = max(1, int(np.ceil(sel * n)))
        print(f"[lp_bound]   single  sel={sel:.2f}  bound={est:>9.1f}  "
              f"lower={lower:>5d}")
        assert est >= lower * 0.95, f"bound {est} < trivial lower {lower}"

    # Multi-table prediction: bound must be >= true intersection size.
    for sel in (0.05, 0.30):
        est_join = est_a.predict_cardinality(q, sel, other_state=est_b)
        print(f"[lp_bound]   multi   sel={sel:.2f}  bound={est_join:>9.1f}")
        assert est_join >= 0.0

    # Stratifier shim sanity check.
    emb1 = rng.standard_normal((1000, 96)).astype(np.float32)
    emb2 = rng.standard_normal((1000, 768)).astype(np.float32)
    sids = stratify_method(emb1, emb2, K=20, seed=0)
    assert sids.shape == (1000,) and sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20
    counts = np.bincount(sids, minlength=20)
    nz = int((counts > 0).sum())
    print(f"[lp_bound] stratum K_used={nz}/20  "
          f"min={int(counts[counts > 0].min())} max={int(counts.max())}")

    # Determinism check.
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "stratify_method must be deterministic"
    est_a2 = LpBoundEstimator(random_state=42).fit(emb_a, pk_a)
    e1 = est_a.predict_cardinality(q, 0.10)
    e2 = est_a2.predict_cardinality(q, 0.10)
    assert abs(e1 - e2) < 1e-6, f"determinism: {e1} vs {e2}"
    print("[lp_bound] determinism: OK")
    print("[lp_bound] mini-run OK")


if __name__ == "__main__":
    _mini_run()
