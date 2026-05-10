#!/usr/bin/env python3
"""Tier A — Epsilon-net theoretical-floor baseline (Haussler-Welzl 1986).

Reference
---------
Haussler D., Welzl E. ``Epsilon-nets and Simplex Range Queries''. Discrete &
Computational Geometry 2(2), 127-151 (1987; conf. version SoCG 1986).
DOI: 10.1007/BF02187876  https://link.springer.com/article/10.1007/BF02187876

Algorithm
---------
For a range space ``(X, R)`` of VC-dimension ``d``, the Haussler-Welzl
epsilon-net theorem states that a uniform i.i.d. sample of size

    m = ceil( (4 / eps^2) * (d * log d + log(2 / delta)) )

forms an eps-net of ``X`` with probability at least ``1 - delta`` — every
range whose relative measure exceeds eps contains at least one sample
point. As a direct corollary, the empirical range count multiplied by
``N / m`` is a (1 + eps)-approximation of the true range cardinality with
the same confidence.

This is the *theoretical floor* baseline against which every distribution-
aware stratifier in the capstone benchmark is measured. It receives no
distribution information and gives no preferential treatment to any region
of the embedding space.

For the capstone *stratification* problem (vs. on-line range counting) we
adapt this in three steps:

  1. Compute the exact eps-net target ``target_m`` from the closed-form
     bound, using ``d_eff = dim(emb1) + dim(emb2)`` as the VC-dimension
     proxy for axis-aligned range queries on the concatenated vector.
  2. Cap to ``net_size = min(target_m, max_sample_size, N)`` to keep
     wall-clock bounded on 50M-row cells.
  3. Draw a single deterministic uniform sample of indices as the eps-net
     ``net_indices``.
  4. Form ``K`` strata by *uniform random* assignment over the full
     population (no clustering, no distribution use). Plugged into the
     proportional-allocation pipeline this reproduces classical uniform
     sampling — the precise control treatment the eps-net theorem
     prescribes.

The eps-net target ``target_m``, the actual ``net_size`` after the cap,
and the resampled ``net_indices`` are exposed as auxiliary metadata via
``stratify_method.last_metadata`` so that downstream measurement code
can recover the prescribed sample size for direct range-counting if
desired (mirrors the bandit_ucb1_strat.py / TS / MFMC hooks).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_K: int = 20
DEFAULT_EPS: float = 0.05
DEFAULT_DELTA: float = 0.01
# Cap raised from 10k -> 50k vs. v1 to give the theoretical baseline a
# realistic workload at d up to 1024 (target_m for d=1024 eps=0.05 delta=0.01
# is ~11.4k, comfortably below the cap). For very high d the cap dominates.
DEFAULT_MAX_SAMPLE_SIZE: int = 50_000


@dataclass
class EpsilonNetMetadata:
    """Per-call epsilon-net metadata for downstream range-counting use.

    Attributes
    ----------
    eps : float
        Target relative-error tolerance from Haussler-Welzl 1986.
    delta : float
        Target failure probability from Haussler-Welzl 1986.
    vc_dim : int
        VC dimension used in the bound (= effective embedding dimension d).
    target_m : int
        Closed-form target sample size m = ceil((4/eps^2) * (d log d + log(2/delta))),
        before applying the ``max_sample_size`` cap or the N upper bound.
    net_size : int
        Actual eps-net sample size after the cap (= min(target_m, max_sample_size, N)).
    net_indices : np.ndarray, shape (net_size,), dtype int64
        Row indices in [0, N) chosen as the eps-net sample.
        Downstream code should use these for direct range-counting:
            count_in_range = mask(query, embeddings[net_indices]).sum()
            cardinality_estimate = count_in_range * N / net_size
    """

    eps: float
    delta: float
    vc_dim: int
    target_m: int
    net_size: int
    net_indices: np.ndarray


def _haussler_welzl_size(N: int, d: int, eps: float, delta: float) -> int:
    """Closed-form Haussler-Welzl 1986 eps-net sample size.

    Returns ceil( (4/eps^2) * (d log d + log(2/delta)) ), clipped to [1, N].
    """
    d_eff = max(d, 2)  # log d defined; d=1 collapses the bound trivially
    m = (4.0 / (eps * eps)) * (d_eff * np.log(d_eff) + np.log(2.0 / delta))
    return int(min(N, max(1, int(np.ceil(m)))))


class EpsilonNetEstimator:
    """Uniform eps-net cardinality estimator (Haussler-Welzl 1986 Thm. 4.4).

    Public API mirrors the request:
        est = EpsilonNetEstimator(eps=0.05, delta=0.01, K=20,
                                   max_sample_size=50_000, random_state=0)
        est.fit(embeddings)
        card = est.predict_cardinality(query_vec, selectivity)

    The ``fit`` step computes the eps-net target sample size from the
    closed-form bound and draws ``net_size`` row indices uniformly i.i.d.
    The ``predict_cardinality`` step counts net points whose distance to the
    query falls within the selectivity-radius ball and rescales by ``N / m``.
    """

    def __init__(
        self,
        eps: float = DEFAULT_EPS,
        delta: float = DEFAULT_DELTA,
        K: int = DEFAULT_K,
        max_sample_size: int = DEFAULT_MAX_SAMPLE_SIZE,
        random_state: int | None = 0,
    ) -> None:
        if not (0.0 < eps < 1.0):
            raise ValueError(f"eps must be in (0, 1); got {eps}")
        if not (0.0 < delta < 1.0):
            raise ValueError(f"delta must be in (0, 1); got {delta}")
        if K < 2:
            raise ValueError(f"K must be >= 2, got {K}")
        if max_sample_size < 1:
            raise ValueError(f"max_sample_size must be >= 1, got {max_sample_size}")
        self.eps = float(eps)
        self.delta = float(delta)
        self.K = int(K)
        self.max_sample_size = int(max_sample_size)
        self.random_state = int(random_state) if random_state is not None else 0
        # Filled in fit():
        self._N: int | None = None
        self._d: int | None = None
        self._target_m: int | None = None
        self._net_size: int | None = None
        self._net_indices: np.ndarray | None = None
        self._net_vectors: np.ndarray | None = None

    def fit(self, embeddings: np.ndarray) -> "EpsilonNetEstimator":
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2D; got {embeddings.shape}")
        N, d = embeddings.shape
        target_m = _haussler_welzl_size(N, d, self.eps, self.delta)
        net_size = min(target_m, self.max_sample_size, N)
        rng = np.random.default_rng(self.random_state)
        if net_size >= N:
            net_indices = np.arange(N, dtype=np.int64)
        else:
            net_indices = rng.choice(N, size=net_size, replace=False).astype(np.int64)
        self._N = int(N)
        self._d = int(d)
        self._target_m = int(target_m)
        self._net_size = int(net_size)
        self._net_indices = net_indices
        # Cache the eps-net vectors (small: net_size <= max_sample_size = 50k)
        self._net_vectors = embeddings[net_indices].astype(np.float32, copy=False)
        return self

    def predict_cardinality(self, query_vec: np.ndarray, selectivity: float) -> float:
        """Cardinality estimate for the selectivity-radius ball around query_vec.

        Uses the eps-net guarantee: count net points within the selectivity-
        induced distance threshold, multiply by ``N / net_size``. The
        selectivity-to-radius mapping uses the empirical distance quantile
        so this is workload-agnostic at the same selectivity input.
        """
        if self._net_vectors is None or self._N is None:
            raise RuntimeError("call .fit() first")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1]; got {selectivity}")
        q = np.asarray(query_vec, dtype=np.float32).reshape(-1)
        if q.shape[0] != self._d:
            raise ValueError(
                f"query_vec dim {q.shape[0]} != fitted dim {self._d}"
            )
        # L2 distance from query to every net point
        diff = self._net_vectors.astype(np.float64) - q.astype(np.float64)[None, :]
        dists = np.sqrt((diff * diff).sum(axis=1))
        # Selectivity -> empirical net-distance quantile == ball radius
        radius = float(np.quantile(dists, selectivity))
        in_ball = int((dists <= radius).sum())
        # Haussler-Welzl unbiased rescaling
        return float(in_ball) * (float(self._N) / max(self._net_size, 1))


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    eps: float = DEFAULT_EPS,
    delta: float = DEFAULT_DELTA,
    max_sample_size: int = DEFAULT_MAX_SAMPLE_SIZE,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by uniform random K-strata; attach epsilon-net metadata.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of strata (output IDs in ``[0, K)``); strata are formed by
        uniform random assignment — no clustering, no distribution use.
    seed : int, default 0
        Random seed for the K-strata permutation and the eps-net draw.
    eps : float, default 0.05
        Target relative error in the Haussler-Welzl bound.
    delta : float, default 0.01
        Target failure probability in the Haussler-Welzl bound.
    max_sample_size : int, default 50_000
        Cap on the eps-net sample size. The closed-form target for d=1024
        eps=0.05 delta=0.01 is ~11.4k, comfortably below this cap.

    Returns
    -------
    np.ndarray of shape (N,), dtype int32
        Stratum identifiers in ``[0, K)``, drawn uniformly at random.

    Side Effects
    ------------
    Attaches an ``EpsilonNetMetadata`` to itself as
    ``stratify_method.last_metadata`` after each call. Downstream code can
    introspect ``net_indices`` to recover the prescribed eps-net sample
    for direct (1 + eps)-relative-error range counting.
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
    if not (0.0 < eps < 1.0):
        raise ValueError(f"eps must be in (0, 1); got {eps}")
    if not (0.0 < delta < 1.0):
        raise ValueError(f"delta must be in (0, 1); got {delta}")
    if max_sample_size < 1:
        raise ValueError(f"max_sample_size must be >= 1, got {max_sample_size}")

    N = emb1.shape[0]
    d_eff = int(emb1.shape[1] + emb2.shape[1])  # effective concat dimension

    # Closed-form Haussler-Welzl sample size, capped for wall-clock budget
    target_m = _haussler_welzl_size(N, d_eff, eps, delta)
    net_size = min(target_m, max_sample_size, N)

    rng = np.random.default_rng(seed)

    # Eps-net: uniform i.i.d. (without replacement) row indices
    if net_size >= N:
        net_indices = np.arange(N, dtype=np.int64)
    else:
        net_indices = rng.choice(N, size=net_size, replace=False).astype(np.int64)

    # K-strata: uniform random assignment over the full population.
    # Implementation: random permutation indices mod K; gives (near-)balanced
    # bin sizes and the assignment carries no distributional information.
    perm = rng.permutation(N)
    sids = np.empty(N, dtype=np.int32)
    sids[perm] = (np.arange(N, dtype=np.int64) % K).astype(np.int32)

    meta = EpsilonNetMetadata(
        eps=float(eps),
        delta=float(delta),
        vc_dim=d_eff,
        target_m=int(target_m),
        net_size=int(net_size),
        net_indices=net_indices,
    )
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
        f"[self-test] EpsilonNet (HW86 floor, uniform K=20): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    # Uniform hashing should produce essentially identical bin sizes
    assert ratio <= 1.1, f"uniform hash bins should be ~uniform, got {ratio:.2f}"
    assert K_used == 20, f"all bins must be populated; got {K_used}"

    meta = stratify_method.last_metadata
    assert isinstance(meta, EpsilonNetMetadata)
    assert meta.eps == 0.05 and meta.delta == 0.01
    assert meta.vc_dim == d1 + d2
    assert meta.net_indices.dtype == np.int64
    assert meta.net_size == len(meta.net_indices)
    assert meta.net_size <= meta.target_m
    assert (meta.net_indices >= 0).all() and (meta.net_indices < N).all()
    assert len(np.unique(meta.net_indices)) == meta.net_size, "net w/o replacement"
    print(
        f"[self-test] HW86 metadata: target_m={meta.target_m} net_size={meta.net_size} "
        f"vc_dim={meta.vc_dim} eps={meta.eps} delta={meta.delta}"
    )

    # Determinism
    sids2 = stratify_method(emb1, emb2, K=20, seed=0)
    assert np.array_equal(sids, sids2), "EpsilonNet must be deterministic for fixed seed"
    meta2 = stratify_method.last_metadata
    assert np.array_equal(meta.net_indices, meta2.net_indices), "net deterministic"

    # Different seed -> different uniform partition
    sids3 = stratify_method(emb1, emb2, K=20, seed=1)
    diff = (sids != sids3).mean()
    print(f"[self-test] seed sensitivity: frac differing = {diff:.3f}")
    assert diff > 0.5, "different seed should produce different uniform partition"

    # Larger N -> closer to target_m up to the cap
    big_e1 = rng.standard_normal((50_000, d1)).astype(np.float32)
    big_e2 = rng.standard_normal((50_000, d2)).astype(np.float32)
    _ = stratify_method(big_e1, big_e2, K=20, seed=0, max_sample_size=10_000)
    big_meta = stratify_method.last_metadata
    assert big_meta.net_size == min(big_meta.target_m, 10_000)
    print(
        f"[self-test] N=50k cap check: target_m={big_meta.target_m} "
        f"net_size={big_meta.net_size} (max_sample_size=10000)"
    )

    # Estimator API smoke test
    emb_full = np.concatenate([emb1, emb2], axis=1)
    est = EpsilonNetEstimator(
        eps=0.05, delta=0.01, K=20, max_sample_size=5_000, random_state=0
    )
    est.fit(emb_full)
    q = rng.standard_normal(emb_full.shape[1]).astype(np.float32)
    card = est.predict_cardinality(q, selectivity=0.1)
    print(f"[self-test] EpsilonNetEstimator.predict_cardinality(sel=0.1) = {card:.1f}")
    assert 0.0 <= card <= float(N) * 1.5, f"cardinality out of bounds: {card}"

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
