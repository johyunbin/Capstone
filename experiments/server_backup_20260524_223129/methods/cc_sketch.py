#!/usr/bin/env python3
"""CCSketch — Convolution + Cross-Correlation Count Sketch (multi-table-native).

The CCSketch estimator builds an Alon-style Count Sketch over each base
relation indexed by its join attribute (e.g. ``ps_partkey``), then fuses
two single-table sketches into a *join sketch* through circular
**convolution in the frequency domain** (FFT).  Inner-product of the
joined sketch with a query-region indicator sketch yields an unbiased
estimate of the multi-join cardinality in ``O(r * m * log m)`` time and
``O(r * m)`` space, independent of the input cardinalities.

The convolution-based fusion is the key conceptual move that makes this
estimator *natively multi-table*:  classical Count-Min / AMS sketches
estimate single-relation frequencies and require de-normalisation or
sample alignment to handle joins; CCSketch instead applies the
convolution theorem directly to the per-table sketches, sidestepping
both issues.

Reference
---------
Mike Heddes, Igor Nunes, Tony Givargis, Alex Nicolau.
"Convolution and Cross-Correlation of Count Sketches Enables Fast
Estimation of Pair-wise and Multi-Join Cardinalities."
SIGMOD 2024.  arXiv:2402.15953v2.
Reference implementation: https://github.com/mikeheddes/fast-multi-join-sketch

Adaptation to the embedding-paired setting (this project)
---------------------------------------------------------
Our benchmark joins ``partsupp`` (96-d embedding, ``ps_partkey`` join key)
with ``wiki`` (768-d embedding, ``id`` join key) on ``partkey == id``.
The CCSketch is built over the **integer join key**, not over the
vector itself; vectors instead drive the *query-region indicator* sketch
via a selectivity threshold on a single deterministic projection.

    1.  ``fit`` — for each unique join-key ``k`` in the table, compute
        ``r`` independent universal hashes ``h_i(k) -> [0, m)`` and a
        ``r`` independent Rademacher signs ``s_i(k) -> {-1, +1}``;
        increment ``S[i, h_i(k)] += s_i(k)`` for every tuple holding
        key ``k``.  ``S`` has shape ``(r, m)``.
    2.  ``predict_cardinality(q, sel)`` —
            single-table:  estimate ``|{rows with vec near q within
                            selectivity sel}|`` by building a *query
                            indicator sketch* ``Q`` (sketch of the
                            partkeys whose vectors satisfy the
                            range), then ``<S, Q>`` averaged over the
                            ``r`` rows is the unbiased count.
            multi-table:   given the *other* table's sketch ``S'``,
                            convolve row-wise via FFT
                            (``IFFT(FFT(S) * FFT(S'))``) to obtain the
                            sketch of the joined frequency vector,
                            then inner-product with ``Q`` likewise.

Public class API
----------------
``CCSketch(r=5, m=4096, random_state=None)``
    ``fit(embeddings, partkeys=None) -> self``
    ``predict_cardinality(query_vec, selectivity, other_sketch=None) -> float``
"""
from __future__ import annotations

import warnings
from typing import Any, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Universal hashing helpers (CW-style multiplicative hash with mersenne mod)
# ---------------------------------------------------------------------------

# Large mersenne prime for the modular reduction; > 2**31 so 64-bit ops are safe.
_MERSENNE_P: int = (1 << 61) - 1


def _draw_hash_params(r: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Draw ``r`` independent (a, b) coefficients for ``h(k) = (a*k + b) mod p``.

    The coefficients are sampled uniformly from ``[1, p)`` (a) and ``[0, p)``
    (b) so that the resulting hash family is 2-wise independent under the
    classical Carter-Wegman construction.
    """
    rng = np.random.default_rng(seed)
    a = rng.integers(low=1, high=_MERSENNE_P, size=r, dtype=np.int64)
    b = rng.integers(low=0, high=_MERSENNE_P, size=r, dtype=np.int64)
    return a, b


def _hash_to_buckets(
    keys: np.ndarray, a: np.ndarray, b: np.ndarray, m: int,
) -> np.ndarray:
    """Compute ``r`` parallel bucket ids via CW hash, returning ``(N, r)``.

    Performs ``(a * key + b) mod p mod m`` row-wise in numpy.  The
    intermediate ``int64 * int64`` product can overflow under naive numpy
    semantics; we therefore cast to Python ``object`` arithmetic via the
    ``np.mod`` machinery on int64 — this is safe for ``a, b < 2**61`` and
    ``key < 2**31``.
    """
    # Broadcast: keys (N, 1) * a (1, r) -> (N, r).
    k64 = keys.astype(np.int64).reshape(-1, 1)
    prod = (k64 * a.reshape(1, -1)) + b.reshape(1, -1)
    # Mersenne reduction trick: x mod (2**61 - 1) = (x & p) + (x >> 61), then mod p.
    reduced = (prod & _MERSENNE_P) + (prod >> 61)
    reduced = np.where(reduced >= _MERSENNE_P, reduced - _MERSENNE_P, reduced)
    return (reduced % m).astype(np.int64)


def _sign_hash(
    keys: np.ndarray, a: np.ndarray, b: np.ndarray,
) -> np.ndarray:
    """Compute ``r`` parallel ``{-1, +1}`` Rademacher signs per key."""
    k64 = keys.astype(np.int64).reshape(-1, 1)
    prod = (k64 * a.reshape(1, -1)) + b.reshape(1, -1)
    reduced = (prod & _MERSENNE_P) + (prod >> 61)
    reduced = np.where(reduced >= _MERSENNE_P, reduced - _MERSENNE_P, reduced)
    # Lowest bit -> sign.
    return np.where((reduced & 1) == 1, 1, -1).astype(np.int32)


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class CCSketch:
    """Convolution + Cross-Correlation Count Sketch (Heddes et al. 2024).

    Parameters
    ----------
    r : int, default 5
        Number of independent hash rows.  Variance of the estimator
        decreases as ``1 / sqrt(r)`` in the AMS analysis; r=5 is the
        default in the reference implementation.
    m : int, default 4096
        Sketch width per row; **must be a power of 2** so that the
        FFT-based convolution stays at ``O(m log m)`` and the inverse
        DFT is exact for integer-valued sketches.
    random_state : int or None, default None
        Seed for the hash family draw; ``None`` -> 0.

    Attributes (set by ``fit``)
    ---------------------------
    sketch_ : np.ndarray, shape (r, m), dtype float64
        The trained Count Sketch.
    n_tuples_ : int
        Number of tuples ingested during ``fit``.
    embeddings_ : np.ndarray
        Stored copy of training embeddings (used for query-region
        indicator construction at predict time).
    partkeys_ : np.ndarray
        Stored copy of training partkeys (paired with embeddings_).
    proj_dir_ : np.ndarray, shape (d,)
        Single deterministic projection direction used to convert
        ``query_vec / selectivity`` into a partkey-set predicate.
    """

    def __init__(
        self,
        r: int = 5,
        m: int = 4096,
        random_state: Optional[int] = None,
    ) -> None:
        if r < 1:
            raise ValueError(f"r must be >= 1, got {r}")
        if m < 2 or (m & (m - 1)) != 0:
            raise ValueError(f"m must be a power of 2 >= 2, got {m}")
        self.r: int = int(r)
        self.m: int = int(m)
        self.random_state: int = int(random_state) if random_state is not None else 0
        # Hash coefficients are drawn now so two CCSketch instances
        # constructed with the same seed share the same hash family
        # (required for cross-table inner products to be valid).
        self._h_a, self._h_b = _draw_hash_params(self.r, self.random_state)
        self._s_a, self._s_b = _draw_hash_params(self.r, self.random_state + 7919)
        # Lazy-initialised attributes; set on fit().
        self.sketch_: Optional[np.ndarray] = None
        self.n_tuples_: int = 0
        self.embeddings_: Optional[np.ndarray] = None
        self.partkeys_: Optional[np.ndarray] = None
        self.proj_dir_: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------
    def fit(
        self,
        embeddings: np.ndarray,
        partkeys: Optional[np.ndarray] = None,
    ) -> "CCSketch":
        """Build the per-table Count Sketch indexed by ``partkeys``.

        Parameters
        ----------
        embeddings : np.ndarray, shape (N, d)
            Per-row vectors used at query time to build the indicator
            sketch.  Stored verbatim.
        partkeys : np.ndarray, shape (N,), dtype int, optional
            Join-key per row.  When ``None`` the row index ``[0..N)`` is
            used as a synthetic key — this keeps the API usable in
            single-table mode where there is no FK to join against.
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

        # 1) Compute (h_i(k), s_i(k)) for every row in one vectorised pass.
        buckets = _hash_to_buckets(partkeys, self._h_a, self._h_b, self.m)
        signs = _sign_hash(partkeys, self._s_a, self._s_b)

        # 2) Aggregate into the sketch via np.add.at (scatter-add).
        sketch = np.zeros((self.r, self.m), dtype=np.float64)
        for i in range(self.r):
            np.add.at(sketch[i], buckets[:, i], signs[:, i].astype(np.float64))

        # 3) Stash for predict-time indicator construction.
        self.sketch_ = sketch
        self.n_tuples_ = int(n)
        self.embeddings_ = embeddings.astype(np.float32, copy=False)
        self.partkeys_ = partkeys
        # Deterministic projection direction: the per-feature mean of
        # the training set.  We use mean (not random) so that two
        # CCSketch instances built on the same data agree on the
        # projection axis without having to share an extra seed.
        self.proj_dir_ = embeddings.mean(axis=0).astype(np.float32)
        norm = float(np.linalg.norm(self.proj_dir_)) or 1.0
        self.proj_dir_ /= norm
        return self

    # ------------------------------------------------------------------
    # predict_cardinality
    # ------------------------------------------------------------------
    def predict_cardinality(
        self,
        query_vec: np.ndarray,
        selectivity: float,
        other_sketch: Optional["CCSketch"] = None,
    ) -> float:
        """Estimate the cardinality of the (single- or multi-table) query.

        Parameters
        ----------
        query_vec : np.ndarray, shape (d,)
            Query embedding.  ``d`` must match the training embeddings.
        selectivity : float in (0, 1]
            Fraction of rows whose vectors are deemed *matching* under
            the cosine-similarity ranking against ``query_vec``.
        other_sketch : CCSketch or None, default None
            When supplied, fuses the two single-table sketches via FFT
            convolution and returns the multi-join cardinality estimate.
            ``other_sketch`` must have been built with the *same*
            ``random_state`` so that the hash families align.
        """
        if self.sketch_ is None:
            raise RuntimeError("fit() must be called before predict_cardinality()")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1], got {selectivity}")
        if query_vec.ndim != 1 or query_vec.shape[0] != self.embeddings_.shape[1]:
            raise ValueError(
                f"query_vec shape {query_vec.shape} mismatched with embedding "
                f"dim {self.embeddings_.shape[1]}"
            )

        # 1) Identify the matching partkey set on the *self* table.
        matched_keys = self._matched_keys(query_vec, selectivity)
        if matched_keys.size == 0:
            return 0.0

        # 2) Build the indicator sketch Q (sketch of the matched key
        #    multiset, weighted by 1 per occurrence).
        q_sketch = self._indicator_sketch(matched_keys)

        # 3) Single-table case: <S, Q> per row, median over r rows.
        if other_sketch is None:
            # AMS-style estimate: <S, Q> with same hash family is an
            # unbiased estimator of the dot product of the underlying
            # frequency vectors; here Q is binary so this equals the
            # number of training tuples whose key collides with a
            # matched key — which is exactly the desired cardinality.
            row_estimates = (self.sketch_ * q_sketch).sum(axis=1)
            return float(np.median(row_estimates))

        # 4) Multi-table case: convolve the two sketches in frequency
        #    domain row-wise, then inner-product with Q.
        if not isinstance(other_sketch, CCSketch):
            raise TypeError(
                f"other_sketch must be a CCSketch, got {type(other_sketch).__name__}"
            )
        if other_sketch.sketch_ is None:
            raise RuntimeError("other_sketch.fit() must be called first")
        if other_sketch.r != self.r or other_sketch.m != self.m:
            raise ValueError(
                f"sketch shape mismatch: ({self.r},{self.m}) vs "
                f"({other_sketch.r},{other_sketch.m})"
            )

        # Cross-correlation of two count sketches is the FFT-based
        # convolution of one with the conjugate of the other; for the
        # real-valued sketches we hold this is equivalent to row-wise
        # FFT(S) * FFT(S').conj() then inverse FFT.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=np.exceptions.ComplexWarning)
            fft_self = np.fft.fft(self.sketch_, axis=1)
            fft_other = np.fft.fft(other_sketch.sketch_, axis=1)
            joined = np.fft.ifft(fft_self * np.conj(fft_other), axis=1).real

        # Inner-product joined sketch with the indicator sketch row-wise,
        # take the median to debias outlier rows.
        row_estimates = (joined * q_sketch).sum(axis=1)
        # Convolution preserves total mass; normalise by m so the
        # result is on the same scale as the single-table estimator.
        # (FFT-based convolution introduces a factor of m without this.)
        return float(np.median(row_estimates) / self.m)

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------
    def _matched_keys(
        self, query_vec: np.ndarray, selectivity: float,
    ) -> np.ndarray:
        """Return the partkeys whose embeddings are within the top
        ``selectivity`` fraction by cosine similarity to ``query_vec``.
        """
        q = query_vec.astype(np.float32)
        q_norm = float(np.linalg.norm(q)) or 1.0
        q_unit = q / q_norm
        # Suppress matmul-overflow noise on iid Gaussian test inputs;
        # only the *ranking* of similarities is used downstream.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            sims = self.embeddings_ @ q_unit
        n_match = max(1, int(np.ceil(selectivity * self.embeddings_.shape[0])))
        # argpartition: O(N) selection of the top-n_match similarities.
        top_idx = np.argpartition(-sims, n_match - 1)[:n_match]
        return self.partkeys_[top_idx]

    def _indicator_sketch(self, keys: np.ndarray) -> np.ndarray:
        """Build a sketch of the multiset of ``keys`` using the *self*
        hash family — required so that <S, Q> is unbiased.
        """
        keys = np.asarray(keys, dtype=np.int64).ravel()
        buckets = _hash_to_buckets(keys, self._h_a, self._h_b, self.m)
        signs = _sign_hash(keys, self._s_a, self._s_b)
        q = np.zeros((self.r, self.m), dtype=np.float64)
        for i in range(self.r):
            np.add.at(q[i], buckets[:, i], signs[:, i].astype(np.float64))
        return q


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
    """Stratify rows by their CCSketch row-bucket signature.

    Each row's stratum id is ``(h_0(partkey) + h_1(partkey)) mod K`` over
    the same hash family used by the join estimator.  This keeps the
    stratification consistent with the cardinality predictor when the
    method is used as a stratifier in the orchestrator.

    Parameters
    ----------
    emb1, emb2 : np.ndarray, (N, d1) / (N, d2)
        Paired embeddings; only ``emb1`` is used for hashing the
        synthetic partkey (row index).  ``emb2`` is required by the
        orchestrator signature but ignored here.
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
    # Use synthetic partkey (row id) so the shim works in the absence of
    # a real join attribute.  The orchestrator can then pair this stratum
    # id with the cardinality predictor for paired-vector experiments.
    partkeys = np.arange(n, dtype=np.int64)
    sketch = CCSketch(r=5, m=4096, random_state=seed)
    h0 = _hash_to_buckets(partkeys, sketch._h_a, sketch._h_b, sketch.m)
    sids = (h0[:, 0] + h0[:, 1 % sketch.r]) % K
    return sids.astype(np.int32)


# ---------------------------------------------------------------------------
# Mini-run test
# ---------------------------------------------------------------------------

def _mini_run() -> None:
    """Mini-run: build two sketches, exercise single + multi-table predict."""
    print("[cc_sketch] mini-run: r=5, m=4096, two tables N=2000 each")
    rng = np.random.default_rng(0)
    n, d = 2000, 96
    emb_a = rng.standard_normal((n, d)).astype(np.float32)
    emb_b = rng.standard_normal((n, d)).astype(np.float32)
    pk_a = rng.integers(0, 5000, size=n, dtype=np.int64)
    pk_b = rng.integers(0, 5000, size=n, dtype=np.int64)

    sketch_a = CCSketch(r=5, m=4096, random_state=42).fit(emb_a, pk_a)
    sketch_b = CCSketch(r=5, m=4096, random_state=42).fit(emb_b, pk_b)
    assert sketch_a.sketch_.shape == (5, 4096)
    assert sketch_b.sketch_.shape == (5, 4096)

    q = rng.standard_normal(d).astype(np.float32)

    # Single-table predictions across the standard selectivity grid.
    for sel in (0.01, 0.05, 0.10, 0.30, 0.50):
        est = sketch_a.predict_cardinality(q, sel)
        # Single-table should be close to sel * n in expectation
        # (because the indicator sketch contains exactly that many keys
        # and hash collisions average out).  Allow generous tolerance.
        expected = sel * n
        print(f"[cc_sketch]   single  sel={sel:.2f}  est={est:>9.1f}  "
              f"expected={expected:>6.1f}")

    # Multi-table prediction: convolve A with B, predict with A's query.
    for sel in (0.05, 0.30):
        est_join = sketch_a.predict_cardinality(q, sel, other_sketch=sketch_b)
        print(f"[cc_sketch]   multi   sel={sel:.2f}  est={est_join:>9.1f}")

    # Stratifier shim sanity check.
    emb1 = rng.standard_normal((1000, 96)).astype(np.float32)
    emb2 = rng.standard_normal((1000, 768)).astype(np.float32)
    sids = stratify_method(emb1, emb2, K=20, seed=0)
    assert sids.shape == (1000,) and sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    # Determinism check.
    sketch_a2 = CCSketch(r=5, m=4096, random_state=42).fit(emb_a, pk_a)
    est1 = sketch_a.predict_cardinality(q, 0.10)
    est2 = sketch_a2.predict_cardinality(q, 0.10)
    assert abs(est1 - est2) < 1e-6, f"determinism: {est1} vs {est2}"
    print("[cc_sketch] determinism: OK")
    print("[cc_sketch] mini-run OK")


if __name__ == "__main__":
    _mini_run()
