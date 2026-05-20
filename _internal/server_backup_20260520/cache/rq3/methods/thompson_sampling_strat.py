#!/usr/bin/env python3
"""Tier A — Thompson Sampling stratified allocation (Russo et al. 2018 / Bao SIGMOD 2021).

Reference
---------
Russo D., Van Roy B., Kazerouni A., Osband I., Wen Z. ``A Tutorial on
Thompson Sampling''. Foundations and Trends in Machine Learning, Vol. 11,
No. 1, 2018. DOI: 10.1561/2200000070  https://arxiv.org/abs/1707.02038

Marcus R., Negi P., Mao H., Tatbul N., Alizadeh M., Kraska T. ``Bao: Making
Learned Query Optimization Practical''. SIGMOD 2021.
DOI: 10.1145/3448016.3452838  https://dl.acm.org/doi/10.1145/3448016.3452838

Algorithm
---------
For each of the K strata we maintain a Beta(alpha_h, beta_h) posterior over a
proxy reward signal in [0, 1]. The Bao-style use of Thompson Sampling treats
each stratum as an arm whose reward is the in-sample agreement of a 1-D
projection: a row close to the per-stratum projected mean contributes a
high reward (1 - normalized residual), so high-variance strata gradually
dominate the posterior draws and attract more sampling budget.

For the capstone *stratification* problem (vs. on-line allocation), we use
TS in two ways through the same single-call API:

  1. Initial K-means clustering on the concatenated embedding space gives
     each row a ``stratum_id`` in ``[0, K)``. This part is identical to
     classical KM20 stratification and is the value returned by
     ``stratify_method``.
  2. *Auxiliary metadata* — ``compute_ts_scores`` runs a deterministic
     fixed-budget pseudo-bandit loop (``n_rounds`` iterations) on the 1-D
     projection of each stratum's rows, with reward = 1 - |x_i - mu_h| /
     max(|x - mu_h|). After the loop, ``alpha_h`` / ``beta_h`` summarize
     each arm's posterior; ``post_mean = alpha / (alpha + beta)`` and a
     single deterministic posterior-mean draw per stratum become the
     downstream allocation hint.

The drop-in capstone use only requires (1); (2) is a forward-looking hook
attached as ``stratify_method.last_metadata`` after each call, mirroring
the bandit_ucb1_strat.py convention.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from sklearn.cluster import MiniBatchKMeans

DEFAULT_K: int = 20
DEFAULT_N_ROUNDS: int = 50
DEFAULT_PRIOR_ALPHA: float = 1.0
DEFAULT_PRIOR_BETA: float = 1.0


@dataclass
class TSStrataMetadata:
    """Per-stratum Thompson Sampling Beta posterior metadata.

    Attributes
    ----------
    n_h : np.ndarray, shape (K,)
        Number of rows assigned to each stratum.
    alpha_h : np.ndarray, shape (K,)
        Beta posterior alpha (success accumulator) per stratum.
    beta_h : np.ndarray, shape (K,)
        Beta posterior beta (failure accumulator) per stratum.
    post_mean : np.ndarray, shape (K,)
        Posterior mean reward alpha / (alpha + beta) per stratum.
    ts_score : np.ndarray, shape (K,)
        Posterior-mean draw used as the allocation hint
        (deterministic given seed).
    """

    n_h: np.ndarray
    alpha_h: np.ndarray
    beta_h: np.ndarray
    post_mean: np.ndarray
    ts_score: np.ndarray


def _compute_ts_metadata(
    sids: np.ndarray,
    proj_1d: np.ndarray,
    K: int,
    n_rounds: int,
    prior_alpha: float,
    prior_beta: float,
    seed: int,
) -> TSStrataMetadata:
    """Bao-style TS posterior per stratum (auxiliary, not used in stratum ID)."""
    n_h = np.bincount(sids, minlength=K).astype(np.float64)
    alpha = np.full(K, prior_alpha, dtype=np.float64)
    beta = np.full(K, prior_beta, dtype=np.float64)

    # Per-stratum mean and dispersion of the 1-D projection (reward proxy)
    mean_h = np.zeros(K, dtype=np.float64)
    span_h = np.ones(K, dtype=np.float64)
    for h in range(K):
        mask = sids == h
        if mask.sum() > 0:
            x = proj_1d[mask].astype(np.float64)
            mean_h[h] = float(x.mean())
            span_h[h] = max(float(np.abs(x - mean_h[h]).max()), 1e-12)

    rng = np.random.default_rng(seed)
    for _ in range(n_rounds):
        # Draw theta_tilde ~ Beta(alpha_h, beta_h) for each arm; pick max
        theta = rng.beta(alpha, beta)
        h_star = int(np.argmax(theta))
        if n_h[h_star] <= 0.0:
            beta[h_star] += 1.0  # empty arm -> recorded as a failure
            continue
        # Deterministic mini-batch reward for the chosen arm
        idx = np.where(sids == h_star)[0]
        pick = rng.choice(idx, size=min(len(idx), 16), replace=False)
        x = proj_1d[pick].astype(np.float64)
        reward = float(np.clip(
            1.0 - np.mean(np.abs(x - mean_h[h_star])) / span_h[h_star], 0.0, 1.0
        ))
        alpha[h_star] += reward
        beta[h_star] += 1.0 - reward

    post_mean = alpha / (alpha + beta)
    # One deterministic posterior draw as the allocation hint
    ts_score = rng.beta(alpha, beta)
    return TSStrataMetadata(
        n_h=n_h, alpha_h=alpha, beta_h=beta,
        post_mean=post_mean, ts_score=ts_score,
    )


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    sample_size: int | None = 100_000,
    n_rounds: int = DEFAULT_N_ROUNDS,
    prior_alpha: float = DEFAULT_PRIOR_ALPHA,
    prior_beta: float = DEFAULT_PRIOR_BETA,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by initial K-means clustering; attach Thompson Sampling metadata.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of strata (output IDs in ``[0, K)``).
    seed : int, default 0
        Random seed for K-means initialization and TS draws.
    sample_size : int or None, default 100_000
        Subsample size for K-means fitting (full N for prediction).
    n_rounds : int, default 50
        Number of Thompson Sampling rounds for the auxiliary metadata loop.
    prior_alpha : float, default 1.0
        Beta prior alpha (uniform Beta(1,1) by default).
    prior_beta : float, default 1.0
        Beta prior beta (uniform Beta(1,1) by default).

    Returns
    -------
    np.ndarray of shape (N,), dtype int32
        Stratum identifiers in ``[0, K)``.

    Side Effects
    ------------
    Attaches a ``TSStrataMetadata`` to itself as
    ``stratify_method.last_metadata`` after each call. Downstream code can
    introspect it for variance-aware allocation:

        sids = stratify_method(e1, e2, K=20)
        meta = stratify_method.last_metadata    # TSStrataMetadata
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
    if n_rounds < 1:
        raise ValueError(f"n_rounds must be >= 1, got {n_rounds}")
    if prior_alpha <= 0.0 or prior_beta <= 0.0:
        raise ValueError(
            f"Beta prior must be positive; got alpha={prior_alpha}, beta={prior_beta}"
        )

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

    # Auxiliary TS metadata: project on a random direction to get a 1-D
    # proxy reward signal, then run n_rounds of Bao-style Beta-Bernoulli TS.
    R64 = (rng.standard_normal(d) / np.sqrt(d)).astype(np.float64)
    proj_1d = np.empty(N, dtype=np.float32)
    chunk = 200_000
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for i in range(0, N, chunk):
            j = min(i + chunk, N)
            proj_1d[i:j] = (emb_concat[i:j].astype(np.float64) @ R64).astype(np.float32)
    meta = _compute_ts_metadata(
        sids, proj_1d, K, n_rounds, prior_alpha, prior_beta, seed,
    )

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
        f"[self-test] ThompsonSampling (KMeans K=20 + TS meta): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    assert K_used >= 18, f"degenerate clustering (K_used={K_used})"

    # TS metadata
    meta = stratify_method.last_metadata
    assert isinstance(meta, TSStrataMetadata)
    assert meta.alpha_h.shape == (20,) and meta.beta_h.shape == (20,)
    assert (meta.alpha_h > 0).all() and (meta.beta_h > 0).all()
    print(
        f"[self-test] TS metadata: "
        f"mean(n_h)={float(meta.n_h.mean()):.0f} "
        f"mean(post_mean)={float(meta.post_mean.mean()):.4f} "
        f"ts_range=[{float(meta.ts_score.min()):.4f}, {float(meta.ts_score.max()):.4f}]"
    )
    assert (meta.n_h.sum() == N), f"n_h sum {meta.n_h.sum()} != N {N}"

    # Determinism
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "ThompsonSampling must be deterministic for fixed seed"
    meta2 = stratify_method.last_metadata
    assert np.allclose(meta.alpha_h, meta2.alpha_h), "TS metadata must be deterministic"

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
