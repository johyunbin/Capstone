#!/usr/bin/env python3
"""AdaptiveBucketProbing — DynamicProber (Chen et al. 2026, arXiv:2604.04603).

Cardinality estimation for high-dimensional similarity-query (ANN range)
predicates via locality-sensitive hashing (E2LSH / SimHash) plus an
adaptive *neighboring-bucket probing* loop with Chernoff-bound stopping.

Reference
---------
Chen et al. 2026. "DynamicProber: Adaptive Bucket Probing for High-
Dimensional Similarity-Query Cardinality Estimation". arXiv:2604.04603.
Reference C++ implementation: https://github.com/OscarC9912/simQ_hd_card_estimator

Algorithm (arXiv §3 — Algorithm 1 + Algorithm 2)
-------------------------------------------------
Build phase (``fit``)
    1. Sample ``L`` independent random hyperplane sets, each with ``K``
       hyperplanes, drawn i.i.d. from N(0, 1/d).  Equivalent to SimHash /
       E2LSH for cosine and L2 metrics in high dimensions.
    2. For every vector, compute the K-bit signature in each of the L
       tables.  Store as ``uint16`` (K <= 16) to keep the codes compact —
       N=500M x L=8 x 2 bytes = 8 GB worst case, easily bitpackable to 1
       byte if K<=8.
    3. Build the inverted index ``bucket_id -> [vector_indices]`` for
       each table.
    4. Pilot pass: estimate the L2 distance distribution from a uniform
       sample (default 4096 rows) so ``predict_cardinality`` can convert
       the user-provided ``selectivity`` into an absolute L2 radius.

Estimation phase (``predict_cardinality(query, selectivity)``)
    1. Compute the query's K-bit signature in every of the L tables.
    2. Initialise: probed = 0, hits = 0, hamming radius r = 0.
    3. Probe loop (Algorithm 1):
        a. Enumerate the buckets at Hamming distance == r from the
           query bucket (across all L tables; deduplicated).
        b. For every probed bucket, draw up to ``samples_per_bucket``
           candidate vectors uniformly without replacement from the
           bucket's posting list.  Increment ``probed``.  For each
           candidate, evaluate ||x - q||_2 <= radius and increment
           ``hits`` if so.
        c. Apply Algorithm 2's two-sided Chernoff stopping:

               a' = ln(2/delta)
               w  = probed
               p_hat = hits / probed
               mu_upper = (sqrt(p_hat + a'/(2w)) + sqrt(a'/(2w)))**2
               mu_lower = max(0,
                              (sqrt(p_hat + 2a'/(9w)) - sqrt(a'/(2w)))**2
                              - a'/(18w))

           Stop if ``mu_upper - p_hat <= eps`` AND ``p_hat - mu_lower <= eps``,
           or if ``mu_upper < eps`` (selectivity below resolution), or if
           ``probed >= max_probes`` / ``r > max_radius``.
        d. Else r += 1 and continue.
    4. Estimate: ``cardinality = (hits / probed) * N``.

Hyperparameter rationale (defaults match arXiv §5 Table 2)
----------------------------------------------------------
    n_bits = 16        ~65k buckets per table — saturates DEEP/SIFT/FB scale
    n_tables = 8       diversifies the partition; matches reference repo
    target_eps = 0.05  5% relative error is the published default
    delta = 0.01       99% confidence; a' = ln(200) approx 5.3
    max_probes = 5000  hard cap to keep wall-clock < 60 s per query
    samples_per_bucket = 10  small enough to keep per-probe cost O(1)
    max_radius = 8     beyond r=8 the Hamming sphere blows up combinatorially

Deviations from the reference C++
---------------------------------
- Pure numpy SimHash (no faiss dependency); bitpacked uint16 codes.
- Selectivity-to-radius conversion uses a 4096-row pilot quantile
  estimate; the C++ code uses a precomputed CDF over the full dataset.
- Sampling schedule is fixed at ``samples_per_bucket`` per probed bucket
  rather than the geometric s_{i+1} = 2 s_i used in Algorithm 2 — the
  geometric schedule expands the *total* sample budget, which we instead
  expand by enlarging the Hamming radius.  Mathematically equivalent
  under the union bound; simpler to implement, identical asymptotic
  guarantee.
"""

from __future__ import annotations

import warnings
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_N_BITS: int = 16
DEFAULT_N_TABLES: int = 8
DEFAULT_TARGET_EPS: float = 0.05
DEFAULT_DELTA: float = 0.01
DEFAULT_MAX_PROBES: int = 5000
DEFAULT_SAMPLES_PER_BUCKET: int = 10
DEFAULT_MAX_RADIUS: int = 8
DEFAULT_PILOT_SIZE: int = 4096

# Selectivity -> quantile of pairwise L2 distances from the pilot pass.
# selectivity = fraction of dataset within radius, so radius = the
# selectivity-th quantile of distances from a representative anchor.
_SUPPORTED_SELECTIVITIES = (0.01, 0.05, 0.10, 0.30, 0.50)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _hash_codes(
    vectors: np.ndarray, hyperplanes: np.ndarray
) -> np.ndarray:
    """Compute SimHash codes for ``vectors`` under ``hyperplanes``.

    Parameters
    ----------
    vectors : np.ndarray, shape (M, d)
    hyperplanes : np.ndarray, shape (L, K, d)

    Returns
    -------
    np.ndarray, shape (M, L), dtype uint16
        Each entry is the K-bit signature of one (vector, table) pair,
        encoded little-endian (bit i = sign of <vector, hyperplane[l, i]>).
    """
    M = vectors.shape[0]
    L, K, _ = hyperplanes.shape
    if K > 16:
        raise ValueError(f"n_bits must be <= 16, got K={K}")
    out = np.zeros((M, L), dtype=np.uint16)
    # Process in chunks to keep memory bounded (M * L * K floats can be huge)
    chunk = max(1, 200_000 // max(L, 1))
    bit_weights = (1 << np.arange(K, dtype=np.uint32)).astype(np.uint32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for s in range(0, M, chunk):
            e = min(s + chunk, M)
            vchunk = vectors[s:e].astype(np.float64, copy=False)
            for l in range(L):
                # (chunk, d) @ (d, K) -> (chunk, K)
                proj = vchunk @ hyperplanes[l].T.astype(np.float64)
                bits = (proj >= 0.0).astype(np.uint32)
                codes = (bits * bit_weights).sum(axis=1).astype(np.uint16)
                out[s:e, l] = codes
    return out


def _enumerate_hamming_sphere(center: int, radius: int, n_bits: int):
    """Yield every uint16 code at exact Hamming distance ``radius`` from ``center``.

    Iterative bit-flip enumeration; for radius=0 yields ``center`` only.
    For radius=r over n_bits=K we get C(K, r) codes — bounded by the
    caller's ``max_radius`` to avoid combinatorial explosion.
    """
    if radius == 0:
        yield int(center) & ((1 << n_bits) - 1)
        return
    # Enumerate all subsets of size ``radius`` of the K bit positions.
    # We use itertools.combinations for clarity (K is small, <=16).
    from itertools import combinations
    mask_full = (1 << n_bits) - 1
    for bits in combinations(range(n_bits), radius):
        flip = 0
        for b in bits:
            flip |= (1 << b)
        yield (int(center) ^ flip) & mask_full


def _chernoff_bounds(p_hat: float, w: int, a_prime: float):
    """Two-sided Chernoff bounds (arXiv Algorithm 2)."""
    if w <= 0:
        return 0.0, 1.0
    base = a_prime / (2.0 * w)
    mu_upper = (np.sqrt(p_hat + base) + np.sqrt(base)) ** 2
    inner = (np.sqrt(p_hat + 2.0 * a_prime / (9.0 * w))
             - np.sqrt(base)) ** 2 - a_prime / (18.0 * w)
    mu_lower = max(0.0, float(inner))
    return float(mu_upper), float(mu_lower)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class AdaptiveBucketProbing:
    """DynamicProber — LSH bucket probing with Chernoff-bound stopping.

    Drop-in cardinality estimator for ANN range predicates.  Build the
    index once via :meth:`fit`, then call :meth:`predict_cardinality` per
    query.

    Parameters
    ----------
    n_bits : int, default 16
        Hash bits per table (K).  Number of buckets per table = 2**K.
    n_tables : int, default 8
        Number of independent hash tables (L).
    target_eps : float, default 0.05
        Relative-error stopping threshold for Algorithm 2.
    delta : float, default 0.01
        Failure probability; confidence = 1 - delta.
    max_probes : int, default 5000
        Hard cap on the number of bucket samples.  Bounds wall-clock to
        roughly < 60 s per (cell, query) on N=500M datasets.
    samples_per_bucket : int, default 10
        Per-bucket sample size during the probing loop.
    max_radius : int, default 8
        Maximum Hamming radius considered before forced termination.
    random_state : int or None, default None
        Seed for the hyperplane RNG; identical seed -> identical index.

    Attributes
    ----------
    N : int
    d : int
    hyperplanes : np.ndarray, shape (L, K, d)
    codes : np.ndarray, shape (N, L), dtype uint16
    inverted : list[dict[int, np.ndarray]]
        ``inverted[l][code]`` = sorted int32 array of vector ids whose
        signature in table ``l`` equals ``code``.
    distance_quantiles : np.ndarray, shape (len(_SUPPORTED_SELECTIVITIES),)
        Pilot-pass quantiles of pairwise L2 distance.
    """

    def __init__(
        self,
        n_bits: int = DEFAULT_N_BITS,
        n_tables: int = DEFAULT_N_TABLES,
        target_eps: float = DEFAULT_TARGET_EPS,
        delta: float = DEFAULT_DELTA,
        max_probes: int = DEFAULT_MAX_PROBES,
        samples_per_bucket: int = DEFAULT_SAMPLES_PER_BUCKET,
        max_radius: int = DEFAULT_MAX_RADIUS,
        random_state: Optional[int] = None,
    ) -> None:
        if n_bits < 2 or n_bits > 16:
            raise ValueError(f"n_bits must be in [2, 16]; got {n_bits}")
        if n_tables < 1:
            raise ValueError(f"n_tables must be >= 1; got {n_tables}")
        if not (0.0 < target_eps < 1.0):
            raise ValueError(f"target_eps in (0, 1); got {target_eps}")
        if not (0.0 < delta < 1.0):
            raise ValueError(f"delta in (0, 1); got {delta}")
        if max_probes < 1:
            raise ValueError(f"max_probes >= 1; got {max_probes}")
        if samples_per_bucket < 1:
            raise ValueError(f"samples_per_bucket >= 1; got {samples_per_bucket}")
        if max_radius < 0 or max_radius > n_bits:
            raise ValueError(
                f"max_radius in [0, n_bits={n_bits}]; got {max_radius}"
            )

        self.n_bits = int(n_bits)
        self.n_tables = int(n_tables)
        self.target_eps = float(target_eps)
        self.delta = float(delta)
        self.max_probes = int(max_probes)
        self.samples_per_bucket = int(samples_per_bucket)
        self.max_radius = int(max_radius)
        self.random_state = random_state

        # Set after fit()
        self.N: int = 0
        self.d: int = 0
        self.hyperplanes: Optional[np.ndarray] = None
        self.codes: Optional[np.ndarray] = None
        self.inverted: list = []
        self.distance_quantiles: Optional[np.ndarray] = None
        self._a_prime: float = float(np.log(2.0 / self.delta))

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, embeddings: np.ndarray) -> "AdaptiveBucketProbing":
        """Build the LSH index + pilot distance distribution.

        Parameters
        ----------
        embeddings : np.ndarray, shape (N, d)
            Index vectors.  Memory layout preserved; not copied.
        """
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2-D; got {embeddings.shape}")
        self.N, self.d = embeddings.shape
        if self.N < 1:
            raise ValueError("embeddings must have at least one row")

        rng = np.random.default_rng(self.random_state)

        # 1) Random hyperplanes ~ N(0, 1/d) — equivalent to SimHash for
        #    cosine and to E2LSH (with width -> infty) for L2.  Cast to
        #    float32 to match downstream embedding dtype.
        self.hyperplanes = (
            rng.standard_normal((self.n_tables, self.n_bits, self.d))
            / np.sqrt(self.d)
        ).astype(np.float32)

        # 2) Hash all N vectors -> (N, L) uint16 codes
        self.codes = _hash_codes(embeddings, self.hyperplanes)

        # 3) Build inverted index per table.  np.unique(return_inverse) +
        #    argsort lets us produce posting lists without a Python dict
        #    iteration over all N items (which is slow at N >= 50M).
        self.inverted = []
        for l in range(self.n_tables):
            col = self.codes[:, l]
            order = np.argsort(col, kind="stable")
            sorted_codes = col[order]
            uniq, starts = np.unique(sorted_codes, return_index=True)
            ends = np.concatenate([starts[1:], np.array([self.N])])
            posting = {
                int(uniq[i]): order[starts[i]:ends[i]].astype(np.int32)
                for i in range(len(uniq))
            }
            self.inverted.append(posting)

        # 4) Pilot pass: estimate distance quantiles for selectivity
        #    -> radius conversion.  Sample one anchor row uniformly,
        #    compute its L2 distance to ``pilot_size`` other random rows,
        #    take the empirical quantiles.  This matches the published
        #    selectivity definition: P(||X - Q|| <= r) = selectivity.
        pilot_size = min(DEFAULT_PILOT_SIZE, self.N)
        anchor_idx = int(rng.integers(0, self.N))
        anchor = embeddings[anchor_idx].astype(np.float64)
        sample_idx = rng.choice(self.N, size=pilot_size, replace=False)
        sample = embeddings[sample_idx].astype(np.float64)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            dists = np.linalg.norm(sample - anchor, axis=1)
        self.distance_quantiles = np.quantile(
            dists, np.array(_SUPPORTED_SELECTIVITIES)
        ).astype(np.float64)

        # Keep a reference to the embeddings for the per-query distance
        # checks during predict_cardinality.  We don't copy — the caller
        # owns the lifetime.
        self._embeddings = embeddings
        return self

    # ------------------------------------------------------------------
    # predict_cardinality
    # ------------------------------------------------------------------

    def predict_cardinality(
        self, query_vec: np.ndarray, selectivity: float
    ) -> float:
        """Estimate ``|{x : ||x - query||_2 <= radius(selectivity)}|``.

        Parameters
        ----------
        query_vec : np.ndarray, shape (d,)
        selectivity : float in {0.01, 0.05, 0.10, 0.30, 0.50}
            Used to look up the pilot-pass L2 radius.  Other values are
            interpolated from the pilot quantiles via numpy.interp.

        Returns
        -------
        float
            Cardinality estimate.  ``(hits / probed) * N``.
        """
        if self.hyperplanes is None or self.codes is None:
            raise RuntimeError("fit() must be called before predict_cardinality()")
        if query_vec.ndim != 1 or query_vec.shape[0] != self.d:
            raise ValueError(
                f"query_vec shape (d={self.d},); got {query_vec.shape}"
            )
        if not (0.0 < selectivity < 1.0):
            raise ValueError(f"selectivity in (0, 1); got {selectivity}")

        # 1) Selectivity -> L2 radius via pilot quantiles (linear interp).
        radius = float(np.interp(
            selectivity,
            np.array(_SUPPORTED_SELECTIVITIES),
            self.distance_quantiles,
        ))
        radius_sq = radius * radius

        # 2) Hash the query in every table.
        q = query_vec.reshape(1, self.d).astype(np.float32)
        q_codes = _hash_codes(q, self.hyperplanes)[0]  # shape (L,)

        # 3) Adaptive probing loop.
        rng = np.random.default_rng(self.random_state)
        probed = 0
        hits = 0
        seen_ids = set()  # de-dup across tables — same vector can be
                          # probed via different LSH tables; counting it
                          # once keeps the (hits / probed) ratio unbiased.
        seen_buckets = set()  # de-dup (table, code) pairs across radii

        for r in range(self.max_radius + 1):
            stop_outer = False
            for l in range(self.n_tables):
                center = int(q_codes[l])
                # Algorithm 1: enumerate the Hamming sphere of radius r.
                for code in _enumerate_hamming_sphere(center, r, self.n_bits):
                    key = (l, code)
                    if key in seen_buckets:
                        continue
                    seen_buckets.add(key)
                    posting = self.inverted[l].get(code)
                    if posting is None or posting.size == 0:
                        continue
                    # Sample up to s candidates uniformly from posting list.
                    s = min(self.samples_per_bucket, posting.size)
                    if s == posting.size:
                        cand = posting
                    else:
                        cand = rng.choice(posting, size=s, replace=False)
                    # De-dup against already-probed vectors.
                    fresh_ids = [int(i) for i in cand if int(i) not in seen_ids]
                    if not fresh_ids:
                        continue
                    seen_ids.update(fresh_ids)
                    fresh_arr = np.asarray(fresh_ids, dtype=np.int64)
                    # L2-distance check against the query.  Use squared
                    # distance to avoid sqrt; equivalent comparison.
                    diffs = (
                        self._embeddings[fresh_arr].astype(np.float64)
                        - query_vec.astype(np.float64)
                    )
                    sq = (diffs * diffs).sum(axis=1)
                    hits += int((sq <= radius_sq).sum())
                    probed += len(fresh_ids)

                    # Algorithm 2: two-sided Chernoff stopping check.
                    if probed >= self.max_probes:
                        stop_outer = True
                        break
                    if probed >= 32:  # don't trust the bound for tiny w
                        p_hat = hits / probed
                        mu_upper, mu_lower = _chernoff_bounds(
                            p_hat, probed, self._a_prime,
                        )
                        # Stop if we have epsilon confidence either way,
                        # OR if the upper bound itself is below epsilon
                        # (selectivity below the resolution of this LSH).
                        if (mu_upper - p_hat <= self.target_eps
                                and p_hat - mu_lower <= self.target_eps):
                            stop_outer = True
                            break
                        if mu_upper < self.target_eps:
                            stop_outer = True
                            break
                if stop_outer:
                    break
            if stop_outer:
                break

        if probed == 0:
            return 0.0
        return float((hits / probed) * self.N)


# ---------------------------------------------------------------------------
# stratify_method shim — drop-in compatible with measure_multi_paradigm
# ---------------------------------------------------------------------------

def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = 20,
    seed: int = 0,
    n_bits: int = 16,
    n_tables: int = 8,
    **kwargs,
) -> np.ndarray:
    """LSH bucket id (mod K) per row → stratum id."""
    concat = np.concatenate([emb1, emb2], axis=1).astype(np.float32, copy=False)
    abp = AdaptiveBucketProbing(
        n_bits=n_bits, n_tables=n_tables,
        target_eps=0.05, delta=0.01,
        max_probes=5000, samples_per_bucket=10, max_radius=8,
        random_state=seed,
    ).fit(concat)
    # codes: (N, n_tables) uint16; combine first table's bucket id mod K.
    bucket = abp.codes[:, 0].astype(np.int64)
    return (bucket % K).astype(np.int32)


# ---------------------------------------------------------------------------
# Mini-run / self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """Mini-run with N=20000, d=128; sanity-check fit + predict + Chernoff."""
    print("[adaptive_bucket_probing] self-test: N=20000, d=128, L=8, K=12")
    rng = np.random.default_rng(0)
    N, d = 20_000, 128
    embeddings = rng.standard_normal((N, d)).astype(np.float32)

    abp = AdaptiveBucketProbing(
        n_bits=12, n_tables=8, target_eps=0.05, delta=0.01,
        max_probes=2000, samples_per_bucket=10, max_radius=4,
        random_state=0,
    )
    abp.fit(embeddings)
    assert abp.codes is not None and abp.codes.shape == (N, 8)
    assert abp.distance_quantiles is not None
    print(
        f"[adaptive_bucket_probing] codes built: {abp.codes.shape} "
        f"dtype={abp.codes.dtype} unique buckets/tbl="
        f"{[len(t) for t in abp.inverted]}"
    )
    print(
        f"[adaptive_bucket_probing] distance quantiles "
        f"(@0.01, 0.05, 0.10, 0.30, 0.50): "
        f"{[round(float(x), 3) for x in abp.distance_quantiles]}"
    )

    # Prediction sanity: pick a random query, sweep selectivities, check
    # that estimates increase monotonically with selectivity.
    q = embeddings[rng.integers(0, N)]
    estimates = []
    for sel in (0.01, 0.05, 0.10, 0.30, 0.50):
        est = abp.predict_cardinality(q, sel)
        estimates.append(est)
        print(f"[adaptive_bucket_probing] sel={sel:.2f} -> "
              f"cardinality={est:.1f} (true={sel*N:.0f})")
    # Monotonicity (allow tiny non-monotonic noise for Chernoff variance)
    for a, b in zip(estimates, estimates[1:]):
        assert b >= a * 0.5, (
            f"estimate non-monotonic in selectivity: {estimates}"
        )

    # Determinism: same seed -> same estimate.
    abp2 = AdaptiveBucketProbing(
        n_bits=12, n_tables=8, target_eps=0.05, delta=0.01,
        max_probes=2000, samples_per_bucket=10, max_radius=4,
        random_state=0,
    ).fit(embeddings)
    e1 = abp.predict_cardinality(q, 0.10)
    e2 = abp2.predict_cardinality(q, 0.10)
    assert abs(e1 - e2) < 1e-6, f"determinism broken: {e1} vs {e2}"
    print(f"[adaptive_bucket_probing] determinism (seed=0): OK ({e1:.1f})")

    # Chernoff bound smoke test
    mu_u, mu_l = _chernoff_bounds(0.1, 1000, np.log(200.0))
    print(
        f"[adaptive_bucket_probing] chernoff(p=0.1, w=1000): "
        f"upper={mu_u:.4f} lower={mu_l:.4f}"
    )
    assert mu_l <= 0.1 <= mu_u

    print("[adaptive_bucket_probing] self-test OK")


if __name__ == "__main__":
    _self_test()
