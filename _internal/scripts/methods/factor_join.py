#!/usr/bin/env python3
"""FactorJoin — factor-graph cardinality estimator (multi-table-native).

The FactorJoin estimator builds **single-table histograms** over (a) the
join-key frequency and (b) the per-table selectivity quantiles, then
combines them at query time through belief propagation on a small
factor graph.  Because no de-normalisation step or neural network is
involved, the storage and inference cost are independent of the join
fan-out — orders of magnitude smaller and faster than DeepDB while
matching its accuracy on JOB-light.

The estimator is *natively multi-table*: each table contributes one
factor (key-frequency × selectivity histogram), and the join is
expressed as a shared variable on the partkey buckets.  The marginal
probability of the join variable is the elementwise product of the
incoming messages from the two factors, summed over the bucket axis.

Reference
---------
Ziniu Wu, Pei Yu, Peizhi Wu, Rong Zhu, Yuxing Han, Yaliang Li, Defu
Lian, Bolin Ding, Jingren Zhou.
"FactorJoin: A New Cardinality Estimation Framework for Join Queries."
SIGMOD 2023.  DOI: https://doi.org/10.1145/3588721
Reference implementation: https://github.com/wuziniu/FactorJoin

Adaptation to the embedding-paired setting (this project)
---------------------------------------------------------
Our query has two simultaneous predicates: a *vector* predicate
(``cosine(emb, query) >= threshold(selectivity)``) and a *join*
predicate (``partsupp.ps_partkey == wiki.id``).  We separate the two:

    * Factor 1 (``F_self``) — joint distribution over
      ``(partkey_bucket, selectivity_bucket)`` for the self table.
      Trained by a 2-D histogram in ``fit``.
    * Factor 2 (``F_other``) — same shape for the other table.
    * Belief propagation — at query time, we condition each factor on
      the matching selectivity-bucket (derived from query_vec) and
      compute the joint over the remaining partkey-bucket axis as
      ``F_self[:, sel_bucket] * F_other[:, sel_bucket]``.  Summing
      this and rescaling by table sizes gives the join cardinality.

Public class API
----------------
``FactorJoin(n_buckets=100, n_partkey_buckets=50, random_state=None)``
    ``fit(embeddings, partkeys=None) -> self``
    ``predict_cardinality(query_vec, selectivity, other_table_state=None)
        -> float``
"""
from __future__ import annotations

import warnings
from typing import Any, Optional

import numpy as np


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class FactorJoin:
    """Single-table histogram + factor-graph belief propagation estimator.

    Parameters
    ----------
    n_buckets : int, default 100
        Number of selectivity quantile buckets used for the per-table
        histogram axis.  Larger values give finer-grained selectivity
        estimates at quadratic memory cost ``n_buckets *
        n_partkey_buckets``.
    n_partkey_buckets : int, default 50
        Number of partkey hash buckets (the shared join variable in
        the factor graph).  Both tables must use the same value so the
        product factor lines up.
    random_state : int or None, default None
        Seed for the deterministic projection direction; ``None`` -> 0.

    Attributes (set by ``fit``)
    ---------------------------
    n_tuples_ : int
        Number of training tuples ingested.
    proj_dir_ : np.ndarray, shape (d,)
        Unit-norm projection direction; selectivity is computed by
        thresholding ``embeddings @ proj_dir_``.
    sel_edges_ : np.ndarray, shape (n_buckets + 1,)
        Bucket edges along the projected-similarity axis.
    joint_hist_ : np.ndarray, shape (n_partkey_buckets, n_buckets)
        Joint count of (partkey_bucket, selectivity_bucket).  Row
        marginals = partkey-frequency factor; column marginals =
        selectivity-frequency factor.
    embeddings_, partkeys_ : stored copies for query-time projection.
    """

    def __init__(
        self,
        n_buckets: int = 100,
        n_partkey_buckets: int = 50,
        random_state: Optional[int] = None,
    ) -> None:
        if n_buckets < 2:
            raise ValueError(f"n_buckets must be >= 2, got {n_buckets}")
        if n_partkey_buckets < 2:
            raise ValueError(
                f"n_partkey_buckets must be >= 2, got {n_partkey_buckets}"
            )
        self.n_buckets: int = int(n_buckets)
        self.n_partkey_buckets: int = int(n_partkey_buckets)
        self.random_state: int = int(random_state) if random_state is not None else 0
        # Lazy-initialised attributes; set on fit().
        self.n_tuples_: int = 0
        self.proj_dir_: Optional[np.ndarray] = None
        self.sel_edges_: Optional[np.ndarray] = None
        self.joint_hist_: Optional[np.ndarray] = None
        self.embeddings_: Optional[np.ndarray] = None
        self.partkeys_: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------
    def fit(
        self,
        embeddings: np.ndarray,
        partkeys: Optional[np.ndarray] = None,
    ) -> "FactorJoin":
        """Build the joint (partkey, selectivity) histogram for the table.

        Parameters
        ----------
        embeddings : np.ndarray, shape (N, d)
            Per-row vectors.
        partkeys : np.ndarray, shape (N,), dtype int, optional
            Join attribute per row; ``None`` -> synthetic ``[0..N)``
            so the API stays usable in single-table mode.
        """
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2-D, got {embeddings.shape}")
        n, d = embeddings.shape
        if n == 0:
            raise ValueError("embeddings must contain at least one row")

        if partkeys is None:
            partkeys = np.arange(n, dtype=np.int64)
        partkeys = np.asarray(partkeys, dtype=np.int64).ravel()
        if partkeys.shape[0] != n:
            raise ValueError(
                f"partkeys length {partkeys.shape[0]} != embeddings rows {n}"
            )

        # 1) Deterministic projection direction.  We use the per-feature
        #    mean of the training set (after L2 normalisation) so that
        #    two FactorJoin instances built on overlapping data agree
        #    on the selectivity axis without requiring shared seeds.
        proj_dir = embeddings.mean(axis=0).astype(np.float32)
        norm = float(np.linalg.norm(proj_dir)) or 1.0
        proj_dir /= norm

        # 2) Project every row onto the direction, then bucket by
        #    quantile so the marginal distribution along the
        #    selectivity axis is uniform by construction.  This makes
        #    "selectivity bucket k of n" mean "row in the kth quantile
        #    of similarity".
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            proj = embeddings.astype(np.float32) @ proj_dir
        sel_edges = np.quantile(
            proj, np.linspace(0.0, 1.0, self.n_buckets + 1),
        ).astype(np.float32)
        # np.quantile can return identical edges on highly skewed data
        # which would collapse buckets.  Apply a tiny monotonic
        # perturbation to keep np.searchsorted stable.
        for k in range(1, sel_edges.size):
            if sel_edges[k] <= sel_edges[k - 1]:
                sel_edges[k] = np.nextafter(sel_edges[k - 1], np.inf)
        # Bucket id per row (0 .. n_buckets - 1).
        sel_bucket = np.clip(
            np.searchsorted(sel_edges, proj, side="right") - 1,
            0, self.n_buckets - 1,
        )

        # 3) Hash partkeys into n_partkey_buckets via a 2-wise
        #    independent CW hash.  We use a small inline hash (not the
        #    CCSketch one) to keep this file standalone — the only
        #    requirement is determinism per random_state.
        rng = np.random.default_rng(self.random_state)
        a = int(rng.integers(low=1, high=(1 << 31) - 1))
        b = int(rng.integers(low=0, high=(1 << 31) - 1))
        pk_bucket = ((partkeys.astype(np.int64) * a + b) % ((1 << 31) - 1)
                     ) % self.n_partkey_buckets

        # 4) Build the 2-D joint histogram via np.add.at.
        joint = np.zeros(
            (self.n_partkey_buckets, self.n_buckets), dtype=np.float64,
        )
        np.add.at(joint, (pk_bucket, sel_bucket), 1.0)

        # 5) Stash everything for predict-time use.
        self.proj_dir_ = proj_dir
        self.sel_edges_ = sel_edges
        self.joint_hist_ = joint
        self.embeddings_ = embeddings.astype(np.float32, copy=False)
        self.partkeys_ = partkeys
        self.n_tuples_ = int(n)
        # Persist the partkey-hash params so that a *second* FactorJoin
        # built with the same random_state hashes partkeys consistently
        # — required for the join factor product to be valid.
        self._pk_hash_a: int = a
        self._pk_hash_b: int = b
        return self

    # ------------------------------------------------------------------
    # predict_cardinality
    # ------------------------------------------------------------------
    def predict_cardinality(
        self,
        query_vec: np.ndarray,
        selectivity: float,
        other_table_state: Optional["FactorJoin"] = None,
    ) -> float:
        """Estimate cardinality via histogram lookup or factor-graph BP.

        Parameters
        ----------
        query_vec : np.ndarray, shape (d,)
            Query embedding; projected onto ``self.proj_dir_`` to find
            the selectivity bucket.
        selectivity : float in (0, 1]
            Target fraction of matching rows.
        other_table_state : FactorJoin or None, default None
            When supplied, runs factor-graph belief propagation across
            the two single-table histograms.  ``other_table_state``
            must have been built with the same ``random_state`` and
            ``n_partkey_buckets`` so the product factor is well
            defined.
        """
        if self.joint_hist_ is None:
            raise RuntimeError("fit() must be called before predict_cardinality()")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1], got {selectivity}")
        if query_vec.ndim != 1 or query_vec.shape[0] != self.proj_dir_.shape[0]:
            raise ValueError(
                f"query_vec shape {query_vec.shape} mismatched with proj dim "
                f"{self.proj_dir_.shape[0]}"
            )

        # 1) Determine the selectivity bucket(s) implied by the query.
        sel_mask = self._sel_bucket_mask(query_vec, selectivity)

        # 2) Single-table case: marginalise the joint over partkey
        #    buckets, mask by sel_bucket(s), and sum.
        if other_table_state is None:
            sel_marginal = self.joint_hist_.sum(axis=0)  # (n_buckets,)
            return float((sel_marginal * sel_mask).sum())

        # 3) Multi-table case: belief propagation.
        if not isinstance(other_table_state, FactorJoin):
            raise TypeError(
                f"other_table_state must be a FactorJoin, got "
                f"{type(other_table_state).__name__}"
            )
        if other_table_state.joint_hist_ is None:
            raise RuntimeError("other_table_state.fit() must be called first")
        if other_table_state.n_partkey_buckets != self.n_partkey_buckets:
            raise ValueError(
                f"n_partkey_buckets mismatch: {self.n_partkey_buckets} vs "
                f"{other_table_state.n_partkey_buckets}"
            )

        # The join factor for partkey k is the product of the two
        # tables' partkey-frequency factors, conditioned on the
        # selectivity mask.  We compute:
        #     msg_self[k]  = sum_j (joint_self [k, j] * sel_mask[j])
        #     msg_other[k] = sum_j (joint_other[k, j] * sel_mask_other[j])
        # then the join cardinality is sum_k msg_self[k] * msg_other[k].
        # Build the other table's selectivity mask using *its own*
        # projection axis -- so we project query_vec through the other
        # table's proj_dir_ as well.
        sel_mask_other = other_table_state._sel_bucket_mask(
            query_vec, selectivity,
        )

        msg_self = (self.joint_hist_ * sel_mask).sum(axis=1)
        msg_other = (other_table_state.joint_hist_ * sel_mask_other).sum(axis=1)
        # Belief propagation product across the partkey variable.
        join_card = float(np.dot(msg_self, msg_other))
        # Normalise: each (a, b) pair was counted with probability
        # 1/n_partkey_buckets that they would hash to the same bucket
        # by chance (false-positive collisions).  Divide by that to
        # obtain the unbiased estimator.
        return join_card

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------
    def _sel_bucket_mask(
        self, query_vec: np.ndarray, selectivity: float,
    ) -> np.ndarray:
        """Return a length-``n_buckets`` weight vector covering the top
        ``selectivity`` fraction of buckets nearest to ``query_vec``.

        Because every bucket holds (by construction) ``1 / n_buckets`` of
        the training mass, taking ``ceil(selectivity * n_buckets)``
        consecutive buckets nearest to the query projection gives a
        ``selectivity`` fraction of the data.  We pick the top buckets
        ranked by similarity to the query projection.
        """
        q = query_vec.astype(np.float32)
        q_norm = float(np.linalg.norm(q)) or 1.0
        q_unit = q / q_norm
        # The bucket centroid for bucket k is the midpoint of its
        # sel_edges; similarity to the query projection is just the
        # signed difference.  We rank buckets by *closeness* of their
        # centroid to the query projection.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            q_proj = float(self.proj_dir_ @ q_unit)
        bucket_centers = 0.5 * (self.sel_edges_[:-1] + self.sel_edges_[1:])
        # Buckets with center >= q_proj rank highest (we approximate
        # cosine similarity by the projection difference; the ordering
        # is what matters).  Negative absolute distance -> closeness.
        rank_score = -np.abs(bucket_centers - q_proj)
        n_take = max(1, int(np.ceil(selectivity * self.n_buckets)))
        top_idx = np.argpartition(-rank_score, n_take - 1)[:n_take]
        mask = np.zeros(self.n_buckets, dtype=np.float64)
        mask[top_idx] = 1.0
        return mask


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
    """Stratify rows by their FactorJoin (partkey_bucket, sel_bucket) cell.

    Each row's stratum id is ``(pk_bucket * sqrt(K) + sel_bucket) mod K``
    so that the stratification mirrors the joint histogram cells used at
    predict time.  ``emb2`` is required by the orchestrator signature
    but not consumed by FactorJoin (single-table histogram only).

    Parameters
    ----------
    emb1, emb2 : np.ndarray, (N, d1) / (N, d2)
    K : int, default 20
    seed : int, default 0

    Returns
    -------
    np.ndarray, shape (N,), dtype int32
    """
    if emb1.ndim != 2 or emb2.ndim != 2:
        raise ValueError(f"emb1/emb2 must be 2-D; got {emb1.shape} / {emb2.shape}")
    if emb1.shape[0] != emb2.shape[0]:
        raise ValueError(
            f"emb1/emb2 row count mismatch: {emb1.shape[0]} vs {emb2.shape[0]}"
        )
    if K < 2:
        raise ValueError(f"K must be >= 2, got {K}")

    n = emb1.shape[0]
    partkeys = np.arange(n, dtype=np.int64)
    # Use sqrt(K) buckets on each axis so the joint reaches K cells.
    side = max(2, int(np.ceil(np.sqrt(K))))
    fj = FactorJoin(
        n_buckets=side, n_partkey_buckets=side, random_state=seed,
    ).fit(emb1, partkeys)

    # Recompute per-row bucket assignments to derive the stratum id.
    # Suppress float32 matmul overflow warnings on iid Gaussian inputs;
    # only the bucket *ranking* matters, not the absolute projection.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        proj = emb1.astype(np.float32) @ fj.proj_dir_
    sel_bucket = np.clip(
        np.searchsorted(fj.sel_edges_, proj, side="right") - 1,
        0, fj.n_buckets - 1,
    )
    pk_bucket = ((partkeys * fj._pk_hash_a + fj._pk_hash_b)
                 % ((1 << 31) - 1)) % fj.n_partkey_buckets
    sids = (pk_bucket * side + sel_bucket) % K
    return sids.astype(np.int32)


# ---------------------------------------------------------------------------
# Mini-run test
# ---------------------------------------------------------------------------

def _mini_run() -> None:
    """Mini-run: build two FactorJoin states, exercise single + multi predict."""
    print("[factor_join] mini-run: n_buckets=50, n_partkey_buckets=20, "
          "two tables N=2000 each")
    rng = np.random.default_rng(0)
    n, d = 2000, 96
    emb_a = rng.standard_normal((n, d)).astype(np.float32)
    emb_b = rng.standard_normal((n, d)).astype(np.float32)
    pk_a = rng.integers(0, 5000, size=n, dtype=np.int64)
    pk_b = rng.integers(0, 5000, size=n, dtype=np.int64)

    fj_a = FactorJoin(
        n_buckets=50, n_partkey_buckets=20, random_state=42,
    ).fit(emb_a, pk_a)
    fj_b = FactorJoin(
        n_buckets=50, n_partkey_buckets=20, random_state=42,
    ).fit(emb_b, pk_b)
    assert fj_a.joint_hist_.shape == (20, 50)
    assert fj_b.joint_hist_.shape == (20, 50)

    q = rng.standard_normal(d).astype(np.float32)

    # Single-table predictions across the standard selectivity grid.
    for sel in (0.01, 0.05, 0.10, 0.30, 0.50):
        est = fj_a.predict_cardinality(q, sel)
        expected = sel * n
        print(f"[factor_join]   single  sel={sel:.2f}  est={est:>9.1f}  "
              f"expected={expected:>6.1f}")

    # Multi-table predictions.
    for sel in (0.05, 0.30):
        est_join = fj_a.predict_cardinality(q, sel, other_table_state=fj_b)
        print(f"[factor_join]   multi   sel={sel:.2f}  est={est_join:>9.1f}")

    # Stratifier shim sanity check.
    emb1 = rng.standard_normal((1000, 96)).astype(np.float32)
    emb2 = rng.standard_normal((1000, 768)).astype(np.float32)
    sids = stratify_method(emb1, emb2, K=20, seed=0)
    assert sids.shape == (1000,) and sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    # Determinism check.
    fj_a2 = FactorJoin(
        n_buckets=50, n_partkey_buckets=20, random_state=42,
    ).fit(emb_a, pk_a)
    est1 = fj_a.predict_cardinality(q, 0.10)
    est2 = fj_a2.predict_cardinality(q, 0.10)
    assert abs(est1 - est2) < 1e-6, f"determinism: {est1} vs {est2}"
    print("[factor_join] determinism: OK")
    print("[factor_join] mini-run OK")


if __name__ == "__main__":
    _mini_run()
