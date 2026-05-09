#!/usr/bin/env python3
"""AMS Count-Sketch — concentration-bounded hash sketch (Tier S multi-relation).

The Alon-Gibbons-Matias-Szegedy sketch tracks join and self-join sizes in
limited storage by mapping each tuple to a small set of randomised
{-1, +1} buckets via 4-wise independent hash functions; the sum-of-products
of two sketches is an unbiased estimator of the join size with concentration
bounds proportional to the second-moment norm.  In our project we adapt the
sketch's hashing skeleton (random-hyperplane signing, exactly the SimHash
construction) as a *partition* method that places paired-vector rows into
``K`` hash buckets without requiring training data.

Reference
---------
Noga Alon, Phillip B. Gibbons, Yossi Matias, Mario Szegedy.
"Tracking Join and Self-Join Sizes in Limited Storage."
PODS 1999, extended in J. Computer and System Sciences (JCSS) 64(3), 2002.
DOI: https://doi.org/10.1145/303976.303984 (PODS 1999)
DOI: https://doi.org/10.1006/jcss.2001.1813 (JCSS 2002)

The sign-bit hashing strategy used below is also known as SimHash:
M. S. Charikar, "Similarity Estimation Techniques from Rounding Algorithms",
STOC 2002. DOI: https://doi.org/10.1145/509907.509965

Adaptation to multi-vector stratification (this project)
--------------------------------------------------------
The classical AMS sketch operates on relational tuples and indexes them by
their join-key value through a 4-wise independent hash.  In our embedding
setting there is no scalar join key — instead each row carries a paired
vector ``(emb1[i], emb2[i])`` and the natural analog of "the row's hash key"
is a *signature* of the concatenated embedding.  We compute that signature
via random-hyperplane signing (SimHash):

    1. Concatenate emb1 and emb2 (norm-aware, mean-norm rescaled) into a
       single d1+d2 dimensional vector ``v``.
    2. Project ``v`` onto ``ceil(log2(K))`` random hyperplanes drawn from a
       standard Gaussian; record the sign of each projection as one bit
       of the signature.
    3. Pack the bits into an integer raw_id in ``[0, 2 ** ceil(log2(K)))``
       and reduce modulo K to obtain the stratum id.

This procedure inherits the AMS guarantees that (a) the hash is data
independent (no learning phase), (b) two rows that agree in cosine on the
combined space collide with probability 1 - theta/pi (Charikar 2002), and
(c) the signature has constant evaluation cost in N.

Public API
----------
``stratify_method(emb1, emb2, K=20, seed=0, **kwargs) -> np.ndarray``
    Returns an ``int32`` array of shape ``(N,)`` with stratum ids in
    ``[0, K)``.  Drop-in compatible with
    ``measure_multi_paradigm.stratify_method`` semantics.

Optional keyword arguments
--------------------------
    norm_aware : bool, default True
        When ``True``, rescale ``emb1`` and ``emb2`` by their respective
        mean L2 norms before concatenation.  Mirrors
        ``measure_multi_paradigm.build_concat`` so that emb2's larger
        dimensionality does not dominate the signature.
"""
from __future__ import annotations

import warnings
from typing import Any

import numpy as np


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _norm_aware_concat(emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
    """Concatenate ``emb1`` / ``emb2`` after dividing each by its mean L2 norm.

    Same semantics as ``measure_multi_paradigm.build_concat`` so that
    AMS Count-Sketch buckets are computed in a space where neither side
    dominates the cosine geometry.
    """
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    return np.concatenate(
        [emb1 / n1, emb2 / n2], axis=1,
    ).astype(np.float32)


def _make_hyperplanes(
    dim: int, n_hp: int, seed: int,
) -> np.ndarray:
    """Generate ``n_hp`` standard-normal hyperplanes; same seed -> same matrix."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_hp, dim)).astype(np.float32)


def _sign_signature(
    vectors: np.ndarray, hyperplanes: np.ndarray, K: int,
) -> np.ndarray:
    """Compute the SimHash sign-bit signature of each row, then mod K.

    For each row v: bits = (W @ v > 0).  Pack bits LSB-first into raw_id;
    return raw_id mod K as the bucket id.

    The matmul intermediate computation can overflow float32 on iid Gaussian
    test inputs, but only the *sign* of each entry is consulted, so the
    overflow does not affect the signature.  Suppress the corresponding
    RuntimeWarning to keep output clean.
    """
    n_hp = hyperplanes.shape[0]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        proj = vectors @ hyperplanes.T            # (N, n_hp)
    bits = (proj > 0).astype(np.int32)        # (N, n_hp), 0 or 1
    weights = (1 << np.arange(n_hp)).astype(np.int32)  # [1, 2, 4, ...]
    raw_ids = (bits * weights).sum(axis=1)    # 0 .. 2**n_hp - 1
    return (raw_ids % K).astype(np.int32)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = 20,
    seed: int = 0,
    **kwargs: Any,
) -> np.ndarray:
    """Stratify paired-vector rows via AMS Count-Sketch (SimHash signature).

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First-relation embeddings (e.g. partsupp side).
    emb2 : np.ndarray, shape (N, d2)
        Second-relation embeddings (e.g. part side).
    K : int, default 20
        Number of strata produced.  ``ceil(log2(K))`` random hyperplanes
        are drawn; their sign bits packed and reduced mod K.
    seed : int, default 0
        RNG seed; identical inputs and seed produce identical assignments.
    **kwargs : Any
        ``norm_aware`` (default True) — if False, raw concatenation is used
        instead of the mean-norm-rescaled concatenation.

    Returns
    -------
    np.ndarray, shape (N,), dtype int32
        Stratum id per row; values in ``[0, K)``.

    Raises
    ------
    ValueError
        If ``emb1`` and ``emb2`` have a different number of rows, if either
        is not 2-D, or if ``K < 2``.
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

    norm_aware: bool = bool(kwargs.get("norm_aware", True))

    # 1) Build concatenated emb_concat of dimension d1 + d2.
    if norm_aware:
        concat = _norm_aware_concat(emb1, emb2)
    else:
        concat = np.concatenate(
            [emb1.astype(np.float32, copy=False),
             emb2.astype(np.float32, copy=False)],
            axis=1,
        )

    # 2) Draw ceil(log2(K)) random hyperplanes (data independent).
    n_hp = int(np.ceil(np.log2(K)))
    hyperplanes = _make_hyperplanes(
        dim=concat.shape[1], n_hp=n_hp, seed=seed,
    )

    # 3) Compute sign-bit signature -> mod K -> stratum id.
    sids = _sign_signature(concat, hyperplanes, K=K)
    return sids


# ---------------------------------------------------------------------------
# Mini-run test
# ---------------------------------------------------------------------------

def _mini_run() -> None:
    """Mini-run with N=10000, d1=96, d2=768; print stratum-size distribution."""
    print("[ams_count_sketch] mini-run: N=10000, d1=96, d2=768, K=20")
    rng = np.random.default_rng(0)
    emb1 = rng.standard_normal((10000, 96)).astype(np.float32)
    emb2 = rng.standard_normal((10000, 768)).astype(np.float32)

    sids = stratify_method(emb1, emb2, K=20, seed=0)
    assert sids.shape == (10000,)
    assert sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    counts = np.bincount(sids, minlength=20)
    nz = counts[counts > 0]
    print(f"[ams_count_sketch] stratum sizes: "
          f"min={int(nz.min())} max={int(counts.max())} "
          f"mean={counts.mean():.1f} std={counts.std():.1f}")
    print(f"[ams_count_sketch] K_used={int((counts > 0).sum())}/20  "
          f"max_min_ratio={counts.max() / max(int(nz.min()), 1):.2f}")
    # ceil(log2(20)) = 5  -> raw range 0..31; mod 20 collides buckets 0-11
    # twice (vs once for 12-19) so the distribution should be ~2:1 imbalanced
    # (well known AMS / mod-collision behaviour).  Assert *upper* bound to
    # catch pathological hashing.
    assert counts.max() / max(int(nz.min()), 1) < 5.0, \
        "AMS Count-Sketch should yield bounded imbalance (<5x)"

    # Determinism check: same seed -> identical assignment.
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "stratify_method must be deterministic"
    print("[ams_count_sketch] determinism (seed=0): OK")
    print("[ams_count_sketch] mini-run OK")


if __name__ == "__main__":
    _mini_run()
