#!/usr/bin/env python3
"""Tier A — Dense Gaussian Random Projection stratification (Bingham-Mannila ICDM 2001).

Reference
---------
Bingham E., Mannila H. ``Random Projection in Dimensionality Reduction:
Applications to Image and Text Data''. KDD 2001 / Proc. ICDM 2001.
DOI: 10.1145/502512.502546 (KDD)  https://dl.acm.org/doi/10.1145/502512.502546

Algorithm
---------
A dense projection matrix ``R`` of shape ``(d, k)`` is drawn from
i.i.d. ``N(0, 1/d)`` entries (Bingham-Mannila 2001, §3 ``Gaussian random
matrix''). The full embedding ``X`` of shape ``(N, d)`` is projected as

    Y = X @ R, R_{ij} ~ N(0, 1/d)

For ``k = 1`` the projection collapses to a 1-D coordinate, which is
quantile-binned into ``K`` strata. The Johnson-Lindenstrauss lemma
guarantees pairwise distance preservation for sufficiently large ``k``;
here we use ``k = 1`` for direct stratification — an explicit ablation of
the *sparse* Achlioptas 2003 variant already deployed as ``sparse_rp`` in
``measure_multi_paradigm.py``.

The dense Gaussian variant carries ~3x the memory and ~3x the matmul
FLOPs of the sparse Achlioptas matrix at identical statistical guarantees,
making the two an apples-to-apples ablation for distortion vs. compute.
"""

from __future__ import annotations

import warnings

import numpy as np

DEFAULT_K: int = 20
DEFAULT_K_PROJ: int = 1


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    k_proj: int = DEFAULT_K_PROJ,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by 1-D dense Gaussian random projection then quantile-bin.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of quantile bins for the projected 1-D coordinate.
    seed : int, default 0
        Random seed for the Gaussian projection matrix.
    k_proj : int, default 1
        Output dimension of the projection. Must be 1 for direct
        quantile-bin stratification (k > 1 would require an additional
        aggregator; we keep ``k=1`` as the canonical Tier A choice).

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
    if K < 2:
        raise ValueError(f"K must be >= 2, got {K}")
    if k_proj != 1:
        raise NotImplementedError(
            f"k_proj={k_proj}: only 1-D projection supported for direct quantile binning"
        )

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    # Dense Gaussian projection vector R ~ N(0, 1/d) of shape (d,)
    rng = np.random.default_rng(seed)
    R = rng.standard_normal(d).astype(np.float32) / np.sqrt(d)

    # 1-D projection (chunked to limit memory). Cast to float64 for the
    # matmul to avoid numpy 2.x spurious float32 overflow warnings on large d.
    proj = np.empty(N, dtype=np.float32)
    R64 = R.astype(np.float64)
    chunk = 200_000
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for i in range(0, N, chunk):
            j = min(i + chunk, N)
            proj[i:j] = (emb_concat[i:j].astype(np.float64) @ R64).astype(np.float32)

    # Quantile bins on 1-D projection
    edges = np.quantile(proj, np.linspace(0.0, 1.0, K + 1))[1:-1]
    sids = np.searchsorted(edges, proj, side="right")
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
        f"[self-test] DenseRP (Gaussian k=1 quantile): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    assert ratio < 1.5, f"quantile bins should be ~uniform, got {ratio:.2f}"

    # Determinism check
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "DenseRP must be deterministic"

    # Different seed -> different binning (different projection matrix)
    sids3 = stratify_method(emb1, emb2, K=20, seed=1)
    diff = (sids != sids3).mean()
    print(f"[self-test] seed sensitivity: frac differing = {diff:.3f}")
    assert diff > 0.5, "different seed should produce different projection"

    # Skewed input
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
        f"[self-test] DenseRP skewed: K_used={(counts_skew > 0).sum()}/20 "
        f"max/min={float(counts_skew.max() / max(counts_skew.min(), 1)):.2f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
