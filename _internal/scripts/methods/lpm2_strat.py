#!/usr/bin/env python3
"""Tier B — Local Pivotal Method 2 stratification (Grafstrom-Lundstrom-Schelin 2012).

Reference
---------
Grafstrom A., Lundstrom N. L. P., Schelin L. ``Spatially Balanced Sampling
through the Pivotal Method''. Biometrics 68(2):514-520, 2012.
DOI: 10.1111/j.1541-0420.2011.01699.x

Variance-reduction extension and well-spread duality:
Grafstrom-Saarela 2023, ``Improved Local Pivotal Methods'', arXiv:2305.02446.

Algorithm (LPM2)
----------------
A probabilistic, spatially balanced design with prescribed inclusion
probabilities pi_i = n/N (uniform). Each iteration picks a still-
undecided unit i, finds its nearest neighbor j in the auxiliary space via
kd-tree, and runs a pivotal duel:

    if pi_i + pi_j < 1:
        with prob pi_j / (pi_i + pi_j):  pi_i <- pi_i + pi_j;  pi_j <- 0
        else:                            pi_j <- pi_i + pi_j;  pi_i <- 0
    else:  # pi_i + pi_j >= 1
        with prob (1 - pi_j) / (2 - pi_i - pi_j):  pi_i <- 1;  pi_j <- pi_i + pi_j - 1
        else:                                       pi_j <- 1;  pi_i <- pi_i + pi_j - 1

(Grafstrom et al. 2012, equations (3)-(4))

The duel preserves marginal inclusion probabilities (martingale property)
while geographically separating selected units: two near neighbors cannot
both ``win'' the pivotal step. After all units are decided (pi in {0, 1}),
the n units with pi_i = 1 form a well-spread sample.

For *stratification*, we run LPM2 once on a uniform fit-subsample to elect
``K`` medoids, then assign every row to its nearest medoid (1-NN) for the
final stratum id. This Voronoi assignment matches the kdpp_strat / opq
convention and yields a probabilistic spatially-balanced anchor.
"""

from __future__ import annotations

import warnings

import numpy as np

try:
    from scipy.spatial import cKDTree  # type: ignore
    HAVE_SCIPY = True
except Exception:  # pragma: no cover
    HAVE_SCIPY = False

DEFAULT_K: int = 20
DEFAULT_FIT_SUBSAMPLE: int = 100_000


def _pairwise_sq_dist(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Squared Euclidean distances between rows of X (m, d) and Y (n, d)."""
    Xn = (X * X).sum(axis=1, keepdims=True)
    Yn = (Y * Y).sum(axis=1, keepdims=True).T
    sq = Xn + Yn - 2.0 * (X @ Y.T)
    np.maximum(sq, 0.0, out=sq)
    return sq


def _lpm2_sample(
    X: np.ndarray, n_target: int, seed: int = 0
) -> np.ndarray:
    """Local Pivotal Method 2 — return indices of ``n_target`` selected rows.

    Parameters
    ----------
    X : np.ndarray, shape (M, d)
        Auxiliary embedding (rows are units, columns the spread space).
    n_target : int
        Desired sample size (must satisfy 1 <= n_target <= M).
    seed : int
        Seed for the random generator (unit pick + duel coin).

    Returns
    -------
    np.ndarray of shape (n_target,), dtype int64
        Indices into ``X`` of the n_target selected rows.
    """
    M = X.shape[0]
    if n_target < 1 or n_target > M:
        raise ValueError(f"n_target={n_target} not in [1, M={M}]")

    rng = np.random.default_rng(seed)
    # Initial inclusion probabilities (uniform)
    pi = np.full(M, n_target / M, dtype=np.float64)
    # Decided mask: 0 = pending, 1 = included, -1 = excluded
    state = np.zeros(M, dtype=np.int8)
    pending = list(range(M))  # row ids still undecided
    pending_set = set(pending)

    # Build kd-tree on auxiliary space (Euclidean)
    if HAVE_SCIPY:
        tree = cKDTree(X.astype(np.float64))
    else:  # pragma: no cover — scipy is a dependency in this project
        tree = None

    eps = 1e-12
    max_iter = 4 * M  # safety bound; each iteration decides >= 1 unit

    for _ in range(max_iter):
        n_pending = len(pending)
        if n_pending == 0:
            break
        # Pick random pending unit i
        i_idx = int(rng.integers(0, n_pending))
        i = pending[i_idx]

        # Find nearest pending neighbor j != i via kd-tree
        # Query several neighbors then filter to pending; fall back to brute
        # force if all top-k are decided (rare for the early iterations).
        if tree is not None:
            k_query = min(8, M)
            j = -1
            while k_query <= M:
                _, idxs = tree.query(X[i], k=k_query)
                idxs_arr = np.atleast_1d(idxs)
                for cand in idxs_arr:
                    cand_int = int(cand)
                    if cand_int != i and state[cand_int] == 0:
                        j = cand_int
                        break
                if j >= 0:
                    break
                k_query = min(k_query * 2, M)
            if j < 0:
                # Brute-force scan over pending list (very rare)
                if n_pending == 1:
                    # single unit left: deterministic decide
                    if rng.random() < pi[i]:
                        state[i] = 1
                    else:
                        state[i] = -1
                    pending.pop(i_idx)
                    pending_set.discard(i)
                    continue
                # nearest pending != i
                pend_arr = np.fromiter(
                    (p for p in pending if p != i), dtype=np.int64
                )
                sq = ((X[pend_arr] - X[i]) ** 2).sum(axis=1)
                j = int(pend_arr[int(np.argmin(sq))])
        else:
            # Brute-force fallback (no scipy)
            if n_pending == 1:
                if rng.random() < pi[i]:
                    state[i] = 1
                else:
                    state[i] = -1
                pending.pop(i_idx)
                pending_set.discard(i)
                continue
            pend_arr = np.fromiter(
                (p for p in pending if p != i), dtype=np.int64
            )
            sq = ((X[pend_arr] - X[i]) ** 2).sum(axis=1)
            j = int(pend_arr[int(np.argmin(sq))])

        # Pivotal duel (Grafstrom et al. 2012 eq. 3-4)
        pi_i = pi[i]
        pi_j = pi[j]
        s = pi_i + pi_j
        u = float(rng.random())
        if s < 1.0 - eps:
            # Case A: combined mass < 1, one drops to 0
            if u < pi_j / s:
                pi[i] = s
                pi[j] = 0.0
            else:
                pi[j] = s
                pi[i] = 0.0
        else:
            # Case B: combined mass >= 1, one rises to 1
            denom = 2.0 - s
            if denom < eps:
                # both already ~1
                pi[i] = 1.0
                pi[j] = 1.0
            elif u < (1.0 - pi_j) / denom:
                pi[i] = 1.0
                pi[j] = s - 1.0
            else:
                pi[j] = 1.0
                pi[i] = s - 1.0

        # Update state for any newly-decided unit (and remove from pending)
        for k in (i, j):
            pk = pi[k]
            if pk <= eps:
                state[k] = -1
                pi[k] = 0.0
                if k in pending_set:
                    pending.remove(k)
                    pending_set.discard(k)
            elif pk >= 1.0 - eps:
                state[k] = 1
                pi[k] = 1.0
                if k in pending_set:
                    pending.remove(k)
                    pending_set.discard(k)
        # else: still pending (intermediate probability, common)

    selected = np.flatnonzero(state == 1).astype(np.int64)
    # Edge case: if rounding left the selection short, fill from highest pi
    if selected.size < n_target:
        remaining = np.flatnonzero(state == 0)
        if remaining.size > 0:
            # Add any still-pending with highest pi (deterministic top-up)
            order = np.argsort(-pi[remaining])
            need = n_target - selected.size
            top_up = remaining[order[:need]]
            selected = np.concatenate([selected, top_up])
    elif selected.size > n_target:
        # Trim deterministically (lowest indices first) — should not happen
        selected = selected[:n_target]
    return selected


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    fit_subsample: int = DEFAULT_FIT_SUBSAMPLE,
    **kwargs,
) -> np.ndarray:
    """Stratify rows via LPM2 spatially-balanced K medoids + 1-NN assignment.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of medoids / strata (output stratum ids in ``[0, K)``).
    seed : int, default 0
        Seed for fit-subsample, LPM2 unit pick, and duel coin.
    fit_subsample : int, default 100000
        Cap on rows used for the LPM2 election; for ``N > fit_subsample`` we
        run LPM2 on a uniform random subsample and assign the full ``N``
        rows to those medoids by Euclidean nearest neighbor.

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

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    if K > N:
        raise ValueError(f"K={K} > N={N}; cannot select K medoids")

    rng = np.random.default_rng(seed)
    sub_n = min(fit_subsample, N)
    if sub_n < N:
        sub_idx = rng.choice(N, size=sub_n, replace=False)
        sub = emb_concat[sub_idx]
    else:
        sub_idx = np.arange(N, dtype=np.int64)
        sub = emb_concat

    # LPM2 election of K medoids in subsample-index space
    medoid_sub_ids = _lpm2_sample(sub, n_target=K, seed=seed)
    medoid_global_ids = sub_idx[medoid_sub_ids]
    medoids = emb_concat[medoid_global_ids]

    # Assign every row to nearest medoid (Euclidean in concat space)
    chunk = 50_000
    sids = np.empty(N, dtype=np.int32)
    for i in range(0, N, chunk):
        j = min(i + chunk, N)
        sq = _pairwise_sq_dist(emb_concat[i:j], medoids)
        sids[i:j] = np.argmin(sq, axis=1).astype(np.int32)
    return sids


def _self_test() -> None:
    rng = np.random.default_rng(0)
    N, d1, d2 = 5_000, 96, 768
    emb1 = rng.standard_normal((N, d1)).astype(np.float32)
    emb2 = rng.standard_normal((N, d2)).astype(np.float32)

    sids = stratify_method(emb1, emb2, K=20, seed=0, fit_subsample=1000)
    assert sids.shape == (N,)
    assert sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    counts = np.bincount(sids, minlength=20)
    K_used = (counts > 0).sum()
    ratio = float(counts.max() / max(counts.min(), 1))
    print(
        f"[self-test] LPM2 (Grafstrom 2012, scipy={HAVE_SCIPY}): "
        f"N={N} d={d1+d2} K_used={K_used}/20 max/min={ratio:.2f} "
        f"counts[:5]={counts[:5].tolist()}"
    )
    assert K_used >= 15, f"degenerate LPM2 stratification (K_used={K_used})"

    # Determinism check
    sids2 = stratify_method(emb1, emb2, K=20, seed=0, fit_subsample=1000)
    assert np.array_equal(sids, sids2), "LPM2 must be deterministic for fixed seed"

    # Skewed input check
    centers = rng.standard_normal((4, d1 + d2)).astype(np.float32) * 4.0
    skewed_e1 = np.vstack([
        rng.standard_normal((1250, d1)).astype(np.float32) + c[:d1]
        for c in centers
    ])
    skewed_e2 = np.vstack([
        rng.standard_normal((1250, d2)).astype(np.float32) + c[d1:]
        for c in centers
    ])
    sids_skew = stratify_method(
        skewed_e1, skewed_e2, K=20, seed=0, fit_subsample=1000
    )
    counts_skew = np.bincount(sids_skew, minlength=20)
    print(
        f"[self-test] LPM2 skewed: K_used={(counts_skew > 0).sum()}/20 "
        f"max/min={float(counts_skew.max() / max(counts_skew.min(), 1)):.2f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
