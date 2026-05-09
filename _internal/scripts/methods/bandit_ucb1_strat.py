#!/usr/bin/env python3
"""Tier A — Bandit UCB1 stratified sampling (Carpentier-Munos NeurIPS 2011).

Reference
---------
Carpentier A., Munos R. ``Finite Time Analysis of Stratified Sampling for
Monte Carlo''. Advances in Neural Information Processing Systems (NeurIPS)
24, 2011.  arXiv:1106.5853  https://arxiv.org/abs/1106.5853

Algorithm
---------
The Carpentier-Munos *MC-UCB* allocation rule treats each stratum as a
bandit arm and allocates the next sample to the stratum maximizing

    UCB_h(t) = sigma_hat_h + sqrt(2 ln(t) / n_h)

where ``sigma_hat_h`` is the running standard-deviation estimate within
stratum ``h``, ``n_h`` is the cumulative number of samples drawn from
``h``, and ``t`` is the global step counter. The asymptotic regret of
this scheme matches the optimal Neyman allocation up to a logarithmic
factor (Carpentier-Munos 2011 §4 Theorem 2).

For the capstone *stratification* problem (vs. on-line allocation), we
use UCB1 in two ways, exposed through the same single-call API:

  1. Initial K-means clustering on the concatenated embedding space gives
     each row a ``stratum_id`` in ``[0, K)``. This part is identical to
     classical KM20 stratification and is the value returned by
     ``stratify_method``.
  2. *Auxiliary metadata* — ``compute_ucb_scores`` (optional) computes
     per-stratum UCB1 scores using the within-stratum variance of the
     1-D mean coordinate as the proxy reward. Downstream measurement
     code can read these scores to adapt the per-stratum sample budget
     in subsequent passes (Carpentier-Munos 2011 §3 Eq. 5).

The drop-in capstone use only requires (1); (2) is a forward-looking hook
attached as ``stratify_method.last_metadata`` after each call.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from sklearn.cluster import MiniBatchKMeans

DEFAULT_K: int = 20


@dataclass
class UCBStrataMetadata:
    """Per-stratum UCB1 metadata computed alongside the stratum IDs.

    Attributes
    ----------
    n_h : np.ndarray, shape (K,)
        Number of rows assigned to each stratum.
    mean_h : np.ndarray, shape (K,)
        Per-stratum mean of the 1-D projection (proxy reward signal).
    sigma_h : np.ndarray, shape (K,)
        Per-stratum standard deviation of the 1-D projection.
    ucb_score : np.ndarray, shape (K,)
        UCB1 score sigma_h + sqrt(2 ln(t) / n_h) at t = sum(n_h).
        Higher score => stratum should receive more samples next round.
    """

    n_h: np.ndarray
    mean_h: np.ndarray
    sigma_h: np.ndarray
    ucb_score: np.ndarray


def _compute_ucb_metadata(
    sids: np.ndarray, proj_1d: np.ndarray, K: int
) -> UCBStrataMetadata:
    """Carpentier-Munos UCB1 score per stratum (auxiliary, not used in stratum ID)."""
    n_h = np.bincount(sids, minlength=K).astype(np.float64)
    mean_h = np.zeros(K, dtype=np.float64)
    sigma_h = np.zeros(K, dtype=np.float64)
    for h in range(K):
        mask = sids == h
        if mask.sum() > 0:
            mean_h[h] = float(proj_1d[mask].mean())
            sigma_h[h] = float(proj_1d[mask].std())
    t = float(n_h.sum())
    # UCB1: avoid div-by-zero on empty strata by setting score to +inf there
    safe_n = np.where(n_h > 0, n_h, 1.0)
    bonus = np.sqrt(2.0 * np.log(max(t, 2.0)) / safe_n)
    ucb_score = sigma_h + bonus
    ucb_score = np.where(n_h == 0, np.inf, ucb_score)
    return UCBStrataMetadata(
        n_h=n_h, mean_h=mean_h, sigma_h=sigma_h, ucb_score=ucb_score,
    )


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    sample_size: int | None = 100_000,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by initial K-means clustering; attach UCB1 metadata.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of strata (output IDs in ``[0, K)``).
    seed : int, default 0
        Random seed for K-means initialization.
    sample_size : int or None, default 100_000
        Subsample size for K-means fitting (full N for prediction).

    Returns
    -------
    np.ndarray of shape (N,), dtype int32
        Stratum identifiers in ``[0, K)``.

    Side Effects
    ------------
    The function attaches a ``UCBStrataMetadata`` to itself as
    ``stratify_method.last_metadata`` after each call. Downstream code
    can introspect it for variance-aware allocation:

        sids = stratify_method(e1, e2, K=20)
        meta = stratify_method.last_metadata    # UCBStrataMetadata
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

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    # Subsample for K-means fitting
    rng = np.random.default_rng(seed)
    if sample_size is not None and N > sample_size:
        fit_idx = rng.choice(N, size=sample_size, replace=False)
        fit_data = emb_concat[fit_idx]
    else:
        fit_data = emb_concat

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        km = MiniBatchKMeans(
            n_clusters=K,
            batch_size=1024,
            n_init=3,
            max_iter=100,
            random_state=seed,
        )
        km.fit(fit_data)

        # Predict on full N (chunked to keep peak memory bounded)
        sids = np.empty(N, dtype=np.int32)
        chunk = 200_000
        for i in range(0, N, chunk):
            j = min(i + chunk, N)
            sids[i:j] = km.predict(emb_concat[i:j]).astype(np.int32)

    # Auxiliary UCB1 metadata: project on a random direction to get a
    # 1-D proxy reward signal (the within-stratum variance of which is the
    # bandit reward standard deviation in Carpentier-Munos 2011 §3).
    # Chunked float64 matmul to avoid spurious numpy 2.x overflow warnings.
    R64 = (rng.standard_normal(d) / np.sqrt(d)).astype(np.float64)
    proj_1d = np.empty(N, dtype=np.float32)
    chunk = 200_000
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for i in range(0, N, chunk):
            j = min(i + chunk, N)
            proj_1d[i:j] = (emb_concat[i:j].astype(np.float64) @ R64).astype(np.float32)
    meta = _compute_ucb_metadata(sids, proj_1d, K)

    # Attach as a function attribute (read-after-call hook, no global state)
    stratify_method.last_metadata = meta  # type: ignore[attr-defined]
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
    K_used = (counts > 0).sum()
    ratio = float(counts.max() / max(counts.min(), 1))
    print(
        f"[self-test] BanditUCB1 (KMeans K=20 + UCB1 meta): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    assert K_used >= 18, f"degenerate clustering (K_used={K_used})"

    # UCB1 metadata
    meta = stratify_method.last_metadata
    assert isinstance(meta, UCBStrataMetadata)
    assert meta.n_h.shape == (20,) and meta.ucb_score.shape == (20,)
    finite_ucb = meta.ucb_score[np.isfinite(meta.ucb_score)]
    print(
        f"[self-test] UCB metadata: "
        f"mean(n_h)={float(meta.n_h.mean()):.0f} "
        f"mean(sigma)={float(meta.sigma_h.mean()):.4f} "
        f"ucb_range=[{float(finite_ucb.min()):.4f}, {float(finite_ucb.max()):.4f}]"
    )
    assert (meta.n_h.sum() == N), f"n_h sum {meta.n_h.sum()} != N {N}"

    # Determinism
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "BanditUCB1 must be deterministic for fixed seed"

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
