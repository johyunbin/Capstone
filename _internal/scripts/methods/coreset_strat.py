#!/usr/bin/env python3
"""Tier A — Lightweight Coresets stratification (Bachem-Lucic-Krause ICML 2017).

Reference
---------
Bachem O., Lucic M., Krause A. ``Practical Coreset Constructions for Machine
Learning''. arXiv preprint, 2017. arXiv:1703.06476 (extends the ICML 2017
``Lightweight Coresets'' paper, arXiv:1702.08249).
URLs: https://arxiv.org/abs/1703.06476  https://arxiv.org/abs/1702.08249

Algorithm
---------
The Lightweight Coreset construction (LWCS, ICML 2017 §3) draws each row's
sensitivity score as

    s(x) = 1/(2 N) + d(x, mu)^2 / (2 * sum_i d(x_i, mu)^2)

where ``mu`` is the global mean and ``d`` is the Euclidean distance. This
yields an importance distribution under which an i.i.d. sample of size
``m = O(d eps^{-2} log K)`` produces an unbiased ``(1 + eps)``-approximation
to the K-means objective (Theorem 1 of LWCS).

For *stratification* (rather than coreset construction itself), we use the
sensitivity score as a 1-D continuous coordinate and quantile-bin it into
``K`` strata. Rows with similar sensitivity (= similar geometric importance
within the dataset) co-locate in the same stratum, producing a
distribution-aware partition without any clustering iteration.
"""

from __future__ import annotations

import numpy as np

DEFAULT_K: int = 20
DEFAULT_CHUNK: int = 200_000


def _streamed_sq_dist_to(
    vectors: np.ndarray, mu: np.ndarray, chunk: int = DEFAULT_CHUNK
) -> np.ndarray:
    """Compute ||x - mu||^2 row-wise, chunked to keep peak RAM bounded."""
    N, d = vectors.shape
    out = np.empty(N, dtype=np.float64)
    mu64 = mu.astype(np.float64)
    for i in range(0, N, chunk):
        j = min(i + chunk, N)
        block = vectors[i:j].astype(np.float64) - mu64
        out[i:j] = (block * block).sum(axis=1)
    return out


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by Lightweight-Coreset sensitivity quantile bins.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of quantile bins (output stratum IDs in ``[0, K)``).
    seed : int, default 0
        Currently unused (kept for signature uniformity); the LWCS sensitivity
        score is fully deterministic given (emb1, emb2).

    Returns
    -------
    np.ndarray of shape (N,), dtype int32
        Stratum identifiers in ``[0, K)``, one per input row.
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
    del seed  # deterministic algorithm

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N = emb_concat.shape[0]

    # Global mean (unweighted, in float64 to avoid drift on large N)
    mu = emb_concat.astype(np.float64).mean(axis=0)

    # Squared distance to mean (chunked)
    sq = _streamed_sq_dist_to(emb_concat, mu)
    sq_total = float(sq.sum())
    if sq_total <= 0.0:
        # All rows equal (degenerate) - assign uniformly hashed by row index
        return (np.arange(N, dtype=np.int64) % K).astype(np.int32)

    # LWCS sensitivity (Bachem-Lucic-Krause 2017 §3, Eq. 1)
    sens = 1.0 / (2.0 * N) + sq / (2.0 * sq_total)

    # Quantile bins on sensitivity (K=20 -> quintile if K=5, vigintile if K=20)
    edges = np.quantile(sens, np.linspace(0.0, 1.0, K + 1))[1:-1]
    sids = np.searchsorted(edges, sens, side="right")
    return np.clip(sids, 0, K - 1).astype(np.int32)


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
        f"[self-test] Coreset (LWCS sens-quintile): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    # Quantile bins on a continuous score should produce near-uniform occupancy
    assert ratio < 1.5, f"quantile bins should be uniform, got {ratio:.2f}"

    # Determinism check
    sids2 = stratify_method(emb1, emb2, K=20, seed=42)
    assert np.array_equal(sids, sids2), "Coreset stratification is deterministic"

    # Skewed input: cluster centers far from mean -> larger sensitivity -> upper bins
    centers = rng.standard_normal((3, d1 + d2)).astype(np.float32) * 5.0
    skewed_e1 = np.vstack([
        rng.standard_normal((3000, d1)).astype(np.float32) + c[:d1]
        for c in centers
    ])
    skewed_e2 = np.vstack([
        rng.standard_normal((3000, d2)).astype(np.float32) + c[d1:]
        for c in centers
    ])
    sids_skew = stratify_method(skewed_e1, skewed_e2, K=20, seed=0)
    counts_skew = np.bincount(sids_skew, minlength=20)
    print(
        f"[self-test] Coreset skewed: K_used={(counts_skew > 0).sum()}/20 "
        f"max/min={float(counts_skew.max() / max(counts_skew.min(), 1)):.2f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
