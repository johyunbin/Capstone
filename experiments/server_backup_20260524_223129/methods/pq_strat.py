#!/usr/bin/env python3
"""Tier A — Product Quantization stratification (Jegou-Douze-Schmid PAMI 2011).

Reference
---------
Jegou H., Douze M., Schmid C. ``Product Quantization for Nearest Neighbor
Search''. IEEE Transactions on Pattern Analysis and Machine Intelligence,
33(1):117-128, 2011. DOI: 10.1109/TPAMI.2010.57
URL: https://ieeexplore.ieee.org/document/5432202

Algorithm
---------
The d-dimensional concatenated embedding ``emb_concat`` (d = d1 + d2) is split
into ``M`` disjoint sub-vectors of dimension ``d / M``. A separate K-means
codebook of size ``K_pq`` is fit on each sub-space. Each row therefore
receives an ``M``-dimensional PQ code, an integer per sub-space in
``[0, K_pq)``. The composite code is hashed to a single ``K``-bin
stratum identifier. Two surrogate hashing schemes are supported:

  * ``hash="modulo"`` (default) — fold the base-K_pq composite integer
    ``sum_j code_j * K_pq^j`` modulo ``K``. Deterministic, distribution
    preserving, drop-in stable across runs.
  * ``hash="murmur"`` — feed the M-tuple to a 64-bit FNV-1a then take
    ``mod K``. Less correlated with the natural lexicographic order of PQ
    codes; useful as a robustness check on the modulo scheme.

For the canonical capstone setting (M=4, K_pq=8) the composite space has
``K_pq^M = 4096`` distinct codes, well above ``K=20`` strata, so the
modulo fold yields balanced occupancy without collisions amplifying
imbalance.
"""

from __future__ import annotations

import warnings
from typing import Literal

import numpy as np
from sklearn.cluster import KMeans

DEFAULT_K: int = 20
DEFAULT_M: int = 4
DEFAULT_K_PQ: int = 8


def _fnv1a_64(arr: np.ndarray) -> np.ndarray:
    """64-bit FNV-1a hash applied row-wise on integer codes (N, M).

    Returns an (N,) array of np.uint64.
    """
    FNV_OFFSET = np.uint64(0xCBF29CE484222325)
    FNV_PRIME = np.uint64(0x100000001B3)
    h = np.full(arr.shape[0], FNV_OFFSET, dtype=np.uint64)
    for j in range(arr.shape[1]):
        col = arr[:, j].astype(np.uint64)
        # 8 byte mixing - process per-byte for full avalanche
        for shift in (0, 8, 16, 24, 32, 40, 48, 56):
            byte = (col >> np.uint64(shift)) & np.uint64(0xFF)
            h = (h ^ byte) * FNV_PRIME
    return h


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    M: int = DEFAULT_M,
    K_pq: int = DEFAULT_K_PQ,
    hash: Literal["modulo", "murmur"] = "modulo",
    sample_size: int | None = 100_000,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by Product Quantization code hashing.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column (e.g. DEEP 96d).
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column (e.g. SIFT 128d, Wiki 768d).
    K : int, default 20
        Target number of strata (output IDs ``[0, K)``).
    seed : int, default 0
        Random seed for K-means initialization on each sub-space.
    M : int, default 4
        Number of PQ sub-spaces (``d`` must be divisible by ``M``; if not
        the trailing dim is trimmed).
    K_pq : int, default 8
        Codebook size per sub-space (PAMI 2011 §3.2 typical 256; 8 is
        chosen here for K=20 stratum compatibility — total composite
        space K_pq^M = 4096 >> K=20).
    hash : {"modulo", "murmur"}, default "modulo"
        Composite-code aggregation scheme.
    sample_size : int or None, default 100_000
        Cap on rows used for K-means fitting (None = use all N).

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
    if M < 1:
        raise ValueError(f"M must be >= 1, got {M}")
    if K < 2:
        raise ValueError(f"K must be >= 2, got {K}")
    if K_pq < 2:
        raise ValueError(f"K_pq must be >= 2, got {K_pq}")

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    # Split into M sub-spaces; trim trailing dim if not divisible by M
    sub_dim = d // M
    if sub_dim < 1:
        raise ValueError(f"M={M} too large for d={d} (sub_dim < 1)")
    if d % M != 0:
        emb_concat = emb_concat[:, : sub_dim * M]
        d = sub_dim * M

    # Optional fit subsample (PQ K-means scales O(N * K_pq * d / M * iters))
    rng = np.random.default_rng(seed)
    if sample_size is not None and N > sample_size:
        fit_idx = rng.choice(N, size=sample_size, replace=False)
        fit_data = emb_concat[fit_idx]
    else:
        fit_data = emb_concat

    codes = np.empty((N, M), dtype=np.int32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for j in range(M):
            sub_fit = fit_data[:, j * sub_dim : (j + 1) * sub_dim]
            sub_full = emb_concat[:, j * sub_dim : (j + 1) * sub_dim]
            # K-means per sub-space (Jegou-Douze-Schmid 2011 §3.2)
            km = KMeans(
                n_clusters=K_pq,
                init="k-means++",
                n_init=3,
                max_iter=50,
                random_state=seed + j,
            )
            km.fit(sub_fit)
            codes[:, j] = km.predict(sub_full).astype(np.int32)

    # Hash composite code -> K-bin stratum
    if hash == "modulo":
        composite = np.zeros(N, dtype=np.uint64)
        base = np.uint64(K_pq)
        for j in range(M):
            composite = composite * base + codes[:, j].astype(np.uint64)
        sids = (composite % np.uint64(K)).astype(np.int32)
    elif hash == "murmur":
        h = _fnv1a_64(codes)
        sids = (h % np.uint64(K)).astype(np.int32)
    else:
        raise ValueError(f"unknown hash={hash!r}; expected modulo|murmur")

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
    nz = (counts > 0).sum()
    ratio = float(counts.max() / max(counts.min(), 1))
    print(
        f"[self-test] PQ (M=4 K_pq=8 hash=modulo): N={N} d={d1+d2} "
        f"K_used={nz}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    assert nz >= 18, f"degenerate PQ stratification (K_used={nz})"

    # Determinism check
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "PQ must be deterministic for fixed seed"

    # Murmur hash variant
    sids_m = stratify_method(emb1, emb2, K=20, seed=0, hash="murmur")
    counts_m = np.bincount(sids_m, minlength=20)
    print(
        f"[self-test] PQ (hash=murmur): K_used={(counts_m > 0).sum()}/20 "
        f"max/min={float(counts_m.max() / max(counts_m.min(), 1)):.2f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
