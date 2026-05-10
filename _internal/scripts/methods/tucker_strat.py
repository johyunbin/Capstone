#!/usr/bin/env python3
"""Tucker decomposition — joint-distribution cardinality estimator (Tier B).

Models the joint distribution over ``(selectivity_bin_emb1,
selectivity_bin_emb2, partkey_bucket)`` as a 3-way tensor
``X[i, j, k]`` and Tucker-decomposes it into a small core tensor with
factor matrices.  At query time we recover an estimate of cardinality
from the reconstructed tensor.  Stratification uses each row's
*max-projection* bin in the Tucker subspace.

References
----------
Tucker LR. "Some mathematical notes on three-mode factor analysis."
Psychometrika 31(3), 279-311 (1966).
Kolda TG, Bader BW. "Tensor Decompositions and Applications."
SIAM Review 51(3), 455-500 (2009). DOI 10.1137/07070111X.
Mu et al. "CoDe: Cardinality estimation via tensor decomposition."
arXiv:2508.09602 (2025).

Implementation notes
--------------------
The optional ``tensorly`` library is preferred when available
(``tensorly.decomposition.tucker`` performs HOSVD + ALS refinement
under the hood).  Without it we fall back to pure-numpy HOSVD: stack
unfoldings, compute leading-rank truncated SVD per mode, then form the
core via ``G = X x_1 U1.T x_2 U2.T x_3 U3.T``.  No ALS refinement in
the fallback path -- HOSVD alone is the optimal *Tucker1* truncation
on each mode and is competitive when ranks are small.

Author: Capstone 2026 / 속도는벡터.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple

import numpy as np

try:  # pragma: no cover -- optional dep
    import tensorly as tl
    from tensorly.decomposition import tucker as _tucker
    _HAS_TENSORLY = True
except Exception:  # noqa: BLE001
    _HAS_TENSORLY = False

DEFAULT_K: int = 20
DEFAULT_RANKS: Tuple[int, int, int] = (5, 5, 5)
DEFAULT_N_BUCKETS: int = 20
DEFAULT_SEED: int = 42
SUBSAMPLE_THRESHOLD: int = 100_000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _quantile_bins(values: np.ndarray, n_bins: int) -> Tuple[np.ndarray, np.ndarray]:
    """Quantile-bin a 1-D array. Returns (bin_ids in [0, n_bins), edges)."""
    quantiles = np.quantile(values, np.linspace(0.0, 1.0, n_bins + 1))
    edges = quantiles[1:-1].astype(np.float64)
    # Stabilise against duplicate edges (heavy-tailed data).
    for k in range(1, edges.size):
        if edges[k] <= edges[k - 1]:
            edges[k] = np.nextafter(edges[k - 1], np.inf)
    bin_ids = np.searchsorted(edges, values, side="right")
    return np.clip(bin_ids, 0, n_bins - 1).astype(np.int32), edges


def _project_proj_dir(matrix: np.ndarray) -> np.ndarray:
    """Mean-projection direction (consistent with FactorJoin)."""
    proj = matrix.mean(axis=0).astype(np.float64)
    norm = float(np.linalg.norm(proj)) or 1.0
    return proj / norm


def _hash_bucket(keys: np.ndarray, n_buckets: int, seed: int) -> np.ndarray:
    """2-wise independent CW hash modulo n_buckets."""
    rng = np.random.default_rng(seed)
    a = int(rng.integers(low=1, high=(1 << 31) - 1))
    b = int(rng.integers(low=0, high=(1 << 31) - 1))
    return ((keys.astype(np.int64) * a + b) % ((1 << 31) - 1)) % n_buckets


def _mode_n_unfold(tensor: np.ndarray, mode: int) -> np.ndarray:
    """Mode-n unfolding (fortran-order along the 'mode' axis)."""
    return np.moveaxis(tensor, mode, 0).reshape(tensor.shape[mode], -1)


def _mode_n_product(tensor: np.ndarray, matrix: np.ndarray, mode: int) -> np.ndarray:
    """Mode-n tensor product: tensor x_mode matrix.

    Result shape: same as tensor with dim[mode] replaced by matrix.shape[0].
    """
    new_shape = list(tensor.shape)
    new_shape[mode] = matrix.shape[0]
    unfolded = _mode_n_unfold(tensor, mode)
    out_unfolded = matrix @ unfolded
    return np.moveaxis(
        out_unfolded.reshape([matrix.shape[0]] + [tensor.shape[d] for d in range(tensor.ndim) if d != mode]),
        0,
        mode,
    )


def _hosvd_tucker(
    tensor: np.ndarray, ranks: Sequence[int]
) -> Tuple[np.ndarray, list]:
    """Pure-numpy HOSVD Tucker decomposition (Tucker1 truncation per mode).

    Returns (core G, factors [U1, U2, U3]) such that
    X ~= G x_1 U1 x_2 U2 x_3 U3.
    """
    factors: list = []
    for mode in range(tensor.ndim):
        unf = _mode_n_unfold(tensor, mode).astype(np.float64)
        rank = max(1, min(int(ranks[mode]), unf.shape[0]))
        # Truncated SVD: U = leading 'rank' left singular vectors.
        # For small dims we just call full svd; mode dims here are <= ~50.
        u_full, _s, _vt = np.linalg.svd(unf, full_matrices=False)
        factors.append(u_full[:, :rank].astype(np.float64))
    core = tensor.astype(np.float64)
    for mode, factor in enumerate(factors):
        core = _mode_n_product(core, factor.T, mode)
    return core, factors


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

@dataclass
class _TuckerState:
    proj_dir1: np.ndarray
    proj_dir2: Optional[np.ndarray]
    edges1: np.ndarray
    edges2: Optional[np.ndarray]
    pk_hash_seed: int
    core: np.ndarray
    factors: list
    n_buckets: int
    n_partkey_buckets: int
    n_tuples: int
    ranks: Tuple[int, int, int]


class TuckerEstimator:
    """Joint-distribution cardinality estimator via Tucker decomposition.

    Parameters
    ----------
    ranks
        Tuple of three ints — the Tucker ranks for
        (selectivity_bin_emb1, selectivity_bin_emb2, partkey_bucket).
    n_buckets
        Number of selectivity quantile bins per embedding view.
    random_state
        Seed for hash + (when tensorly used) ALS init.
    """

    def __init__(
        self,
        ranks: Sequence[int] = DEFAULT_RANKS,
        n_buckets: int = DEFAULT_N_BUCKETS,
        random_state: Optional[int] = None,
    ) -> None:
        ranks_tup = tuple(int(r) for r in ranks)
        if len(ranks_tup) != 3 or any(r < 1 for r in ranks_tup):
            raise ValueError(f"ranks must be a length-3 tuple of positive ints, got {ranks_tup}")
        if n_buckets < 2:
            raise ValueError(f"n_buckets must be >= 2, got {n_buckets}")
        self.ranks: Tuple[int, int, int] = ranks_tup
        self.n_buckets: int = int(n_buckets)
        self.random_state: int = int(random_state) if random_state is not None else 0
        self._state: Optional[_TuckerState] = None

    # ------------------------------------------------------------------
    def fit(
        self,
        embeddings: np.ndarray,
        partkeys: Optional[np.ndarray] = None,
        embeddings2: Optional[np.ndarray] = None,
    ) -> "TuckerEstimator":
        """Build the (sel_bin_emb1, sel_bin_emb2, partkey_bucket) tensor and decompose.

        ``embeddings2`` is optional.  When omitted we project ``embeddings``
        onto two orthogonal directions (mean + first PC residual) so the
        3-way tensor is still defined in single-table mode.
        """
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2D, got {embeddings.shape}")
        n_full = embeddings.shape[0]
        if n_full == 0:
            raise ValueError("embeddings must contain >= 1 row")

        # -------- subsample if huge --------
        rng = np.random.default_rng(self.random_state)
        if n_full > SUBSAMPLE_THRESHOLD:
            idx = rng.choice(n_full, size=SUBSAMPLE_THRESHOLD, replace=False)
            emb1 = embeddings[idx]
            emb2 = embeddings2[idx] if embeddings2 is not None else None
            pk = partkeys[idx] if partkeys is not None else None
        else:
            emb1 = embeddings
            emb2 = embeddings2
            pk = partkeys

        n = emb1.shape[0]
        if pk is None:
            pk = np.arange(n, dtype=np.int64)
        pk = np.asarray(pk, dtype=np.int64).ravel()
        if pk.shape[0] != n:
            raise ValueError(f"partkeys length {pk.shape[0]} != embeddings rows {n}")

        # -------- selectivity bins per view --------
        proj_dir1 = _project_proj_dir(emb1)
        proj1 = emb1.astype(np.float64) @ proj_dir1
        bin1, edges1 = _quantile_bins(proj1, self.n_buckets)

        if emb2 is not None:
            if emb2.ndim != 2 or emb2.shape[0] != n:
                raise ValueError(
                    f"embeddings2 must be (N, d2) row-aligned, got {emb2.shape}"
                )
            proj_dir2 = _project_proj_dir(emb2)
            proj2 = emb2.astype(np.float64) @ proj_dir2
        else:
            # Single-table mode: use a residual direction orthogonalised against proj_dir1
            # (PC1 of mean-centred data, projected onto null(proj_dir1)).
            centred = emb1.astype(np.float64) - emb1.mean(axis=0, keepdims=True)
            try:
                # Power-iteration top eigvec on the covariance is overkill — use SVD on a
                # small random subsample to stay cheap.
                sub_n = min(n, 2000)
                sub_idx = rng.choice(n, size=sub_n, replace=False)
                _, _, vt = np.linalg.svd(centred[sub_idx], full_matrices=False)
                pc1 = vt[0]
            except np.linalg.LinAlgError:
                pc1 = rng.standard_normal(emb1.shape[1])
            # Orthogonalise vs proj_dir1
            pc1 = pc1 - (pc1 @ proj_dir1) * proj_dir1
            norm = float(np.linalg.norm(pc1)) or 1.0
            proj_dir2 = pc1 / norm
            proj2 = emb1.astype(np.float64) @ proj_dir2

        bin2, edges2 = _quantile_bins(proj2, self.n_buckets)

        # -------- partkey bucket --------
        n_pk = self.n_buckets  # use same dim for symmetry of the 3-way tensor
        pk_bucket = _hash_bucket(pk, n_pk, self.random_state)

        # -------- 3-way joint count tensor --------
        tensor = np.zeros((self.n_buckets, self.n_buckets, n_pk), dtype=np.float64)
        np.add.at(tensor, (bin1, bin2, pk_bucket), 1.0)

        # Convert to probability tensor for stable decomposition.
        total = float(tensor.sum())
        if total > 0:
            tensor /= total

        # -------- Tucker decomposition --------
        ranks = tuple(min(self.ranks[i], tensor.shape[i]) for i in range(3))
        if _HAS_TENSORLY:
            try:
                tl.set_backend("numpy")
                core, factors = _tucker(
                    tl.tensor(tensor),
                    rank=list(ranks),
                    init="svd",
                    random_state=self.random_state,
                )
                core = np.asarray(core)
                factors = [np.asarray(f) for f in factors]
            except Exception:  # noqa: BLE001
                core, factors = _hosvd_tucker(tensor, ranks)
        else:
            core, factors = _hosvd_tucker(tensor, ranks)

        # Keep counts (un-normalised reconstruction will need scaling by total).
        # Store core in count units.
        core_counts = core * total

        self._state = _TuckerState(
            proj_dir1=proj_dir1,
            proj_dir2=proj_dir2,
            edges1=edges1,
            edges2=edges2,
            pk_hash_seed=self.random_state,
            core=core_counts,
            factors=factors,
            n_buckets=self.n_buckets,
            n_partkey_buckets=n_pk,
            n_tuples=int(n_full),
            ranks=ranks,
        )
        return self

    # ------------------------------------------------------------------
    def _reconstruct(self) -> np.ndarray:
        st = self._state
        assert st is not None
        out = st.core
        for mode, factor in enumerate(st.factors):
            out = _mode_n_product(out, factor, mode)
        return out

    def predict_cardinality(
        self,
        query_vec: np.ndarray,
        selectivity: float,
        other_state: Optional["TuckerEstimator"] = None,
    ) -> float:
        """Estimate cardinality from the Tucker-reconstructed tensor.

        Strategy:
        * Project ``query_vec`` onto ``proj_dir1`` to find the sel-bin on
          axis 1; assume axis-2 marginalises out (we don't have a second
          query vector at predict-time).
        * Sum reconstructed tensor over (bin2, pk_bucket) for the top
          (selectivity * n_buckets) bins on axis 1.
        """
        st = self._state
        if st is None:
            raise RuntimeError("fit() must be called before predict_cardinality")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1], got {selectivity}")
        if query_vec.ndim != 1 or query_vec.shape[0] != st.proj_dir1.shape[0]:
            raise ValueError(
                f"query_vec shape {query_vec.shape} mismatched with proj dim "
                f"{st.proj_dir1.shape[0]}"
            )

        recon = self._reconstruct()  # (n_buckets, n_buckets, n_pk)
        # Marginal on axis 0 (sel_bin_emb1)
        marg1 = recon.sum(axis=(1, 2))  # (n_buckets,)
        # Selectivity mask: top-k buckets along the projected direction.
        # Higher projection score => higher similarity to query => the
        # right tail is "matching".  Number of buckets to keep:
        proj_score = float(query_vec.astype(np.float64) @ st.proj_dir1)
        # Find the bucket the query lands in.
        q_bin = int(np.searchsorted(st.edges1, proj_score, side="right"))
        q_bin = max(0, min(q_bin, self.n_buckets - 1))
        # Selectivity window centred on q_bin.
        n_keep = max(1, int(round(selectivity * self.n_buckets)))
        # Take the n_keep buckets with the largest projection score that are >= q_bin
        # (right tail when query is in the bulk).
        candidates = list(range(q_bin, self.n_buckets)) + list(range(q_bin - 1, -1, -1))
        keep_bins = candidates[:n_keep]
        est = float(marg1[keep_bins].sum())

        if other_state is None:
            return max(0.0, est)

        # Multi-table: marginalise both tensors over selectivity and join on partkey
        if not isinstance(other_state, TuckerEstimator) or other_state._state is None:
            raise TypeError("other_state must be a fitted TuckerEstimator")
        st2 = other_state._state
        if st2.n_partkey_buckets != st.n_partkey_buckets:
            raise ValueError("partkey bucket dim mismatch between tensors")

        recon2 = other_state._reconstruct()
        # Conditional partkey marginal for both tables: sum over sel bins kept by mask.
        cond1 = recon[keep_bins].sum(axis=(0, 1))  # (n_pk,)
        # For other_state we don't have its own query vector — use uniform mask.
        cond2 = recon2.sum(axis=(0, 1))  # (n_pk,)
        join_marg = cond1 * cond2
        # Scale: cond is *probabilities x n* (counts), so join_marg / n_pk approximates
        # the expected number of joined rows under the bucket-uniform assumption.
        return float(max(0.0, join_marg.sum() / max(st.n_partkey_buckets, 1)))


# ---------------------------------------------------------------------------
# stratify_method (drop-in stratifier)
# ---------------------------------------------------------------------------

def stratify_method(
    emb1: np.ndarray,
    emb2: Optional[np.ndarray] = None,
    K: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    ranks: Sequence[int] = DEFAULT_RANKS,
    n_buckets: int = DEFAULT_N_BUCKETS,
    **_kwargs,
) -> np.ndarray:
    """Stratify by Tucker core tensor max-projection bin.

    Algorithm: each row is bucketed into (bin1, bin2) selectivity bins,
    then mapped through the Tucker factor matrices into a 2-D (or 3-D
    if partkey provided) latent coordinate.  The K strata are formed
    by combining the two leading-rank factor coordinates and quantile-
    binning the resulting 1-D scalar score.
    """
    if K < 1:
        raise ValueError(f"K must be >= 1, got {K}")

    est = TuckerEstimator(ranks=ranks, n_buckets=n_buckets, random_state=seed)
    est.fit(emb1, partkeys=None, embeddings2=emb2)
    st = est._state
    assert st is not None

    # Re-bin the *full* dataset (not just the subsample used for fit).
    proj1_full = emb1.astype(np.float64) @ st.proj_dir1
    bin1_full = np.searchsorted(st.edges1, proj1_full, side="right")
    bin1_full = np.clip(bin1_full, 0, st.n_buckets - 1).astype(np.int32)

    if emb2 is not None:
        proj2_full = emb2.astype(np.float64) @ st.proj_dir2
    else:
        proj2_full = emb1.astype(np.float64) @ st.proj_dir2
    bin2_full = np.searchsorted(st.edges2, proj2_full, side="right")
    bin2_full = np.clip(bin2_full, 0, st.n_buckets - 1).astype(np.int32)

    # Project (bin1, bin2) pair onto the leading factor directions.
    # U1 has shape (n_buckets, rank1); take the leading column.
    u1 = st.factors[0][:, 0] if st.factors[0].shape[1] > 0 else np.zeros(st.n_buckets)
    u2 = st.factors[1][:, 0] if st.factors[1].shape[1] > 0 else np.zeros(st.n_buckets)
    score = u1[bin1_full] + u2[bin2_full]

    # Quantile-bin the score into K strata for balanced size.
    quantiles = np.quantile(score, np.linspace(0.0, 1.0, K + 1))
    edges = quantiles[1:-1]
    for k in range(1, edges.size):
        if edges[k] <= edges[k - 1]:
            edges[k] = np.nextafter(edges[k - 1], np.inf)
    sids = np.searchsorted(edges, score, side="right")
    return np.clip(sids, 0, K - 1).astype(np.int32)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    import warnings

    np.seterr(all="ignore")
    warnings.filterwarnings("ignore")
    rng = np.random.default_rng(0)
    n = 5_000
    d1, d2 = 96, 768
    K = 20

    # Block-structured (5 blocks) so Tucker rank-5 should recover signal.
    n_blocks = 5
    cx = rng.standard_normal((n_blocks, d1)).astype(np.float64) * 3.0
    cy = rng.standard_normal((n_blocks, d2)).astype(np.float64) * 3.0
    block = rng.integers(0, n_blocks, size=n)
    emb1 = (cx[block] + rng.standard_normal((n, d1)) * 0.5).astype(np.float32)
    emb2 = (cy[block] + rng.standard_normal((n, d2)) * 0.5).astype(np.float32)
    partkeys = rng.integers(0, 1000, size=n).astype(np.int64)

    print(f"[self-test] tensorly available: {_HAS_TENSORLY}")
    print(f"[self-test] N={n} d1={d1} d2={d2} K={K}")

    est = TuckerEstimator(ranks=(5, 5, 5), n_buckets=20, random_state=42)
    est.fit(emb1, partkeys=partkeys, embeddings2=emb2)
    q = emb1[0]
    pred = est.predict_cardinality(q, selectivity=0.1)
    print(f"[self-test] single-table predict_cardinality(sel=0.1) = {pred:.1f} (n={n})")
    assert pred >= 0

    # Multi-table
    est2 = TuckerEstimator(ranks=(5, 5, 5), n_buckets=20, random_state=42)
    est2.fit(emb2, partkeys=partkeys, embeddings2=emb1)
    pred_join = est.predict_cardinality(q, selectivity=0.1, other_state=est2)
    print(f"[self-test] multi-table predict_cardinality(sel=0.1) = {pred_join:.1f}")
    assert pred_join >= 0

    sids = stratify_method(emb1, emb2, K=K, seed=42)
    counts = np.bincount(sids, minlength=K)
    print(
        f"[self-test] stratify: range=[{sids.min()}, {sids.max()}], "
        f"used={(counts > 0).sum()}/{K}, max/min={counts.max()/max(counts.min(),1):.2f}"
    )
    assert sids.min() >= 0 and sids.max() < K
    assert sids.dtype == np.int32

    # Determinism
    sids2 = stratify_method(emb1, emb2, K=K, seed=42)
    assert np.array_equal(sids, sids2), "stratify_method should be deterministic"

    # Single-table fallback (emb2=None)
    sids_fb = stratify_method(emb1, None, K=K, seed=42)
    assert sids_fb.min() >= 0 and sids_fb.max() < K
    print(f"[self-test] fallback stratify used={int((np.bincount(sids_fb, minlength=K) > 0).sum())}/{K}")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
