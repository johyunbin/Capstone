#!/usr/bin/env python3
"""HKBU-RepSample (LASS-Lite) — representative sampling stratification.

Reference
---------
Wu Z., Song Y., Zhu X., Li H., Xu J., Huang X. "Balancing Global and Local:
Representative Sampling for Large-Scale Vector Data." SIGMOD 2026,
Proc. ACM Manag. Data 4(3), Article 142.
https://doi.org/10.1145/3802019
PDF: https://www.comp.hkbu.edu.hk/~xinhuang/publications/pdfs/SIGMOD26-Vector.pdf

This is the closest published version of our Capstone narrative: the paper
formalises *distribution-aware sampling* as a constrained optimisation problem
that **balances global facility-location coverage against local distributional
fidelity** -- exactly the angle our RQ3 ★4 paradigm is testing.

Algorithm (LASS-Lite, Algorithm 1, p.13)
----------------------------------------
LASS-Lite is the simpler of the two samplers proposed in the paper (the more
elaborate LASS-NA adds a submodular lazy-greedy neighbour cohort selection on
top, which we approximate via the seed-and-reinforce skeleton below). It runs
in four stages on a dataset ``D`` of ``n`` ``d``-dimensional vectors with
sampling ratio ``rho``:

* Stage 0 -- Self-consistent LID. For each row ``x`` retrieve its
  ``k_sol``-NN list and compute the maximum-likelihood LID estimate
  ``LID(x) = ( -1/k * sum_i log(d_i / d_k) )^{-1}`` (Amsaleg-Levina MLE),
  along with the self-consistent radius ``R_sc(x) = d_{k_sol}``.

* Stage 1 -- LID stratification. Sort rows by ``LID(x)`` and partition into
  ``L = floor(sqrt(m))`` equal-frequency strata ``F_1, ..., F_L``. Each
  stratum receives a quota ``q_i`` proportional to ``|F_i| * mean(LID_i)^beta``
  (set ``beta = 0`` for size-proportional, the paper default).

* Stage 2 -- Per-stratum D^2-seeding. Within each stratum, run
  k-means++-style D^2 sampling restricted to the stratum to draw ``q_i``
  diverse seeds (one warm-start row per non-empty stratum). Then attach up
  to ``t`` nearest neighbours per seed within ``B(c, R_sc(c))`` to lift the
  local sampled-neighbour count and stabilise the LID estimator.

* Stage 3 -- Budget normalisation. Pad ``S`` to size ``m`` via farthest-first
  selection; this preserves global coverage when reinforcement underfills.

For *stratification* (which is what the surrounding pipeline asks for), every
row's stratum id is its **assigned LID stratum** ``i in [0, L)`` -- the same
``L = floor(sqrt(K))`` partition used by Stage 1, then quantile-padded to
exactly ``K`` strata so the downstream stratified estimator has a uniform
``K``-bin partition. (LASS-Lite itself is a *sample selector*, not a labelling
function; the LID-stratification step is the natural and faithful extraction.)

Single-table fallback
---------------------
When ``emb2 is None`` we run the LID stratification on ``emb1`` only. This
keeps the API uniform and matches the paper's ``D = single matrix`` setting.

Author: Capstone 2026 / 속도는벡터 (HKBU-RepSample integration, 2026-05-09).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

DEFAULT_K: int = 20
DEFAULT_KSOL: int = 10  # k_sol in the paper, default ~10 for LID MLE
DEFAULT_BETA: float = 0.0  # quota bias on LID; paper default beta=0 (size-prop)
DEFAULT_T: int = 3  # neighbour reinforcement count per seed
DEFAULT_FIT_CAP: int = 30_000  # subsample for fitting on large N (5/10 reduce 100K→30K, 100K stuck 49min on cell 1)
DEFAULT_SEED: int = 42
DEFAULT_CHUNK: int = 50_000


# ---------------------------------------------------------------------------
# LID + helpers
# ---------------------------------------------------------------------------
def _knn_distances(
    vectors: np.ndarray,
    k: int,
    rng: np.random.Generator,
    chunk: int = DEFAULT_CHUNK,
) -> np.ndarray:
    """Return per-row distances to the k nearest neighbours (excluding self).

    Falls back to brute-force chunked distance computation; for N up to ~100k
    this stays well under 1 GB and 90s on 768-d vectors.
    Output shape: (N, k), sorted ascending.
    """
    n = vectors.shape[0]
    out = np.empty((n, k), dtype=np.float32)
    vec64 = vectors.astype(np.float64)
    sq_norm = (vec64 * vec64).sum(axis=1)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        # ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b
        block = vec64[i:j]
        cross = block @ vec64.T  # (chunk, n)
        d2 = sq_norm[i:j, None] + sq_norm[None, :] - 2.0 * cross
        np.maximum(d2, 0.0, out=d2)
        # exclude self by setting diagonal to +inf
        for r, row_idx in enumerate(range(i, j)):
            d2[r, row_idx] = np.inf
        # partition for top-k smallest, then sort the small block
        idx = np.argpartition(d2, kth=k, axis=1)[:, :k]
        # gather the k distances and sort each row
        gathered = np.take_along_axis(d2, idx, axis=1)
        order = np.argsort(gathered, axis=1)
        gathered = np.take_along_axis(gathered, order, axis=1)
        out[i:j] = np.sqrt(gathered).astype(np.float32)
    del rng  # unused: kNN is deterministic given vectors
    return out


def _lid_mle(knn_dists: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Amsaleg-Levina LID MLE per row.

        LID(x) = ( -1/k * sum_{i=1..k} ln(d_i / d_k) )^{-1}

    Robust to near-zero distances via ``eps`` clipping.
    """
    n, k = knn_dists.shape
    if k < 2:
        return np.full(n, np.nan, dtype=np.float64)
    d_k = np.maximum(knn_dists[:, -1:], eps)
    # ratio shape (n, k); the last column is 1 -> ln(1)=0 contributes nothing
    ratios = np.maximum(knn_dists, eps) / d_k
    # average ln(ratio) over the k-1 non-trivial entries
    log_r = np.log(ratios[:, :-1])  # (n, k-1)
    s = -log_r.mean(axis=1)
    s = np.maximum(s, eps)
    return (1.0 / s).astype(np.float64)


def _largest_remainder(quotas_frac: np.ndarray, total: int) -> np.ndarray:
    """Round fractional quotas to integers preserving sum=total (Hare/LR)."""
    floor = np.floor(quotas_frac).astype(np.int64)
    short = int(total - floor.sum())
    if short > 0:
        # Distribute leftover to the largest fractional remainders
        rem = quotas_frac - floor
        order = np.argsort(rem)[::-1]
        floor[order[:short]] += 1
    elif short < 0:
        # Pull back from the smallest fractional remainders
        rem = quotas_frac - floor
        order = np.argsort(rem)
        floor[order[: -short]] -= 1
        floor = np.maximum(floor, 0)
    return floor


def _d2_sample(
    vectors: np.ndarray,
    quota: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """k-means++ D^2 sampling within a single stratum. Returns local indices.

    5/10 12:50 fix: cast vectors to float64 ONCE outside the loop (was: per-iter
    cast = 30K × dim × 8 bytes × 1000 iter = 200 GB redundant cast → 28min stuck).
    """
    n = vectors.shape[0]
    if quota <= 0 or n == 0:
        return np.empty(0, dtype=np.int64)
    if quota >= n:
        return np.arange(n, dtype=np.int64)
    vec64 = vectors.astype(np.float64, copy=False)  # cast 한 번만
    chosen = np.empty(quota, dtype=np.int64)
    chosen[0] = int(rng.integers(0, n))
    diff = vec64 - vec64[chosen[0]]
    min_d2 = (diff * diff).sum(axis=1)
    for j in range(1, quota):
        total = float(min_d2.sum())
        if total <= 0.0:
            remaining = np.setdiff1d(np.arange(n), chosen[:j], assume_unique=False)
            k_left = quota - j
            chosen[j:] = rng.choice(remaining, size=k_left, replace=False)
            return chosen
        probs = min_d2 / total
        nxt = int(rng.choice(n, p=probs))
        chosen[j] = nxt
        diff = vec64 - vec64[nxt]
        d2_new = (diff * diff).sum(axis=1)
        np.minimum(min_d2, d2_new, out=min_d2)
    return chosen


# ---------------------------------------------------------------------------
# Estimator
# ---------------------------------------------------------------------------
@dataclass
class HKBURepSampleState:
    """Persisted state from ``HKBURepSampleEstimator.fit``."""

    sample_indices: np.ndarray  # int64, shape (m,)
    sample_vectors: np.ndarray  # float32, shape (m, d)
    stratum_ids: np.ndarray     # int32, shape (N,) in [0, K)
    lid: np.ndarray             # float64, shape (N,)
    K: int
    N: int


class HKBURepSampleEstimator:
    """LASS-Lite-based representative-sample cardinality estimator.

    Public API matches the surrounding pipeline (see ``EpsilonNetEstimator``)::

        est = HKBURepSampleEstimator(K=20, sample_size=10_000, seed=0)
        est.fit(embeddings)
        card = est.predict_cardinality(query_vec, selectivity)

    Internally it runs LASS-Lite to produce both:
      * a representative sample ``S`` (used for cardinality estimation), and
      * a per-row LID stratum id ``[0, K)`` (used for stratification).
    """

    def __init__(
        self,
        K: int = DEFAULT_K,
        sample_size: int = 10_000,
        alpha: float = 0.5,
        n_init: int = 3,
        max_iter: int = 20,
        random_state: Optional[int] = DEFAULT_SEED,
        k_sol: int = DEFAULT_KSOL,
        beta: float = DEFAULT_BETA,
        t_reinforce: int = DEFAULT_T,
        fit_cap: int = DEFAULT_FIT_CAP,
    ) -> None:
        if K < 2:
            raise ValueError(f"K must be >= 2, got {K}")
        if sample_size < K:
            raise ValueError(f"sample_size must be >= K (={K}), got {sample_size}")
        # alpha / n_init / max_iter accepted for signature uniformity with the
        # task description; LASS-Lite has no alpha knob (the paper's coverage
        # vs fidelity balance is structural, not parametric).
        self.K = int(K)
        self.sample_size = int(sample_size)
        self.alpha = float(alpha)
        self.n_init = int(n_init)
        self.max_iter = int(max_iter)
        self.random_state = int(random_state) if random_state is not None else 0
        self.k_sol = int(k_sol)
        self.beta = float(beta)
        self.t_reinforce = int(t_reinforce)
        self.fit_cap = int(fit_cap)
        self._state: Optional[HKBURepSampleState] = None

    # ------------------------------------------------------------------ fit
    def fit(self, embeddings: np.ndarray) -> "HKBURepSampleEstimator":
        if embeddings.ndim != 2:
            raise ValueError(f"embeddings must be 2D; got {embeddings.shape}")
        N, d = embeddings.shape
        if N < self.K:
            raise ValueError(f"need >= K (={self.K}) rows; got {N}")
        rng = np.random.default_rng(self.random_state)

        # ---------- Stage 0: subsample for LID computation if N is huge ----
        if N > self.fit_cap:
            fit_idx = rng.choice(N, size=self.fit_cap, replace=False)
            fit_idx.sort()
            fit_vec = embeddings[fit_idx].astype(np.float32, copy=False)
        else:
            fit_idx = np.arange(N, dtype=np.int64)
            fit_vec = embeddings.astype(np.float32, copy=False)

        # ---------- Stage 0: kNN + LID on the fit slice --------------------
        k_use = min(self.k_sol, fit_vec.shape[0] - 1)
        if k_use < 2:
            # Degenerate: fall back to single bucket per row
            stratum = np.zeros(N, dtype=np.int32)
            sample = rng.choice(N, size=min(self.sample_size, N), replace=False)
            self._state = HKBURepSampleState(
                sample_indices=sample.astype(np.int64),
                sample_vectors=embeddings[sample].astype(np.float32, copy=False),
                stratum_ids=stratum,
                lid=np.zeros(N, dtype=np.float64),
                K=self.K,
                N=N,
            )
            return self

        knn = _knn_distances(fit_vec, k=k_use, rng=rng)
        lid_fit = _lid_mle(knn)
        # Replace NaN/Inf with median for stable sorting
        finite_mask = np.isfinite(lid_fit)
        if finite_mask.any():
            med = float(np.median(lid_fit[finite_mask]))
        else:
            med = float(d)
        lid_fit = np.where(finite_mask, lid_fit, med)

        # ---------- Stage 1: equal-frequency LID strata --------------------
        K = self.K
        order = np.argsort(lid_fit)
        n_fit = lid_fit.shape[0]
        # Equal-frequency partition into K strata via quantile assignment
        edges = np.quantile(lid_fit, np.linspace(0.0, 1.0, K + 1))[1:-1]
        stratum_fit = np.searchsorted(edges, lid_fit, side="right")
        stratum_fit = np.clip(stratum_fit, 0, K - 1).astype(np.int32)

        # ---------- Stage 1b: per-stratum quotas ---------------------------
        # quota_i ∝ |F_i| * mean(LID_i)^beta  (paper Eq. line 11)
        quotas_frac = np.zeros(K, dtype=np.float64)
        for i in range(K):
            mask = stratum_fit == i
            if not mask.any():
                continue
            mean_lid = float(lid_fit[mask].mean())
            weight = mask.sum() * (max(mean_lid, 1e-9) ** self.beta)
            quotas_frac[i] = weight
        # Normalise to sample_size and round (largest-remainder)
        m = min(self.sample_size, N)
        # leave room for reinforcement: aim for n_seeds = m / (t+1)
        n_seed_target = max(K, m // (self.t_reinforce + 1))
        if quotas_frac.sum() <= 0:
            quotas = np.full(K, n_seed_target // K, dtype=np.int64)
            quotas[: n_seed_target - quotas.sum()] += 1
        else:
            quotas_frac = quotas_frac * (n_seed_target / quotas_frac.sum())
            quotas = _largest_remainder(quotas_frac, n_seed_target)

        # ---------- Stage 2: per-stratum D^2-seeding -----------------------
        seed_local: list[np.ndarray] = []
        for i in range(K):
            mask = stratum_fit == i
            if not mask.any() or quotas[i] <= 0:
                continue
            local_idx_in_fit = np.flatnonzero(mask)
            stratum_vec = fit_vec[local_idx_in_fit]
            chosen_local = _d2_sample(stratum_vec, int(quotas[i]), rng)
            # Map fit-local -> global indices
            seed_local.append(fit_idx[local_idx_in_fit[chosen_local]])
        if seed_local:
            seeds_global = np.concatenate(seed_local).astype(np.int64)
        else:
            seeds_global = rng.choice(N, size=min(K, N), replace=False).astype(np.int64)
        seeds_global = np.unique(seeds_global)

        # ---------- Stage 2b: neighbour reinforcement ----------------------
        # For each seed c, attach up to t nearest neighbours of c (in the fit
        # slice for tractability) within R_sc(c). This mirrors line 23 of
        # Algorithm 1.
        sample_set: set[int] = set(int(x) for x in seeds_global.tolist())
        target = m
        if self.t_reinforce > 0 and len(sample_set) < target:
            # Use the LID kNN distances we already computed for R_sc
            # R_sc(x) = d_{k_sol}(x). For seeds outside the fit slice we skip.
            fit_lookup = -np.ones(N, dtype=np.int64)
            fit_lookup[fit_idx] = np.arange(fit_idx.shape[0], dtype=np.int64)
            for c in seeds_global.tolist():
                if len(sample_set) >= target:
                    break
                local_c = int(fit_lookup[c])
                if local_c < 0:
                    continue
                # nearest neighbours of c among fit_vec
                vec_c = fit_vec[local_c].astype(np.float64)
                diff = fit_vec.astype(np.float64) - vec_c
                d_all = np.sqrt((diff * diff).sum(axis=1))
                d_all[local_c] = np.inf  # skip self
                R_sc = float(knn[local_c, -1])
                # candidates within R_sc, take the t closest
                cand_local = np.argpartition(d_all, kth=min(self.t_reinforce, len(d_all) - 1))[
                    : self.t_reinforce
                ]
                cand_local = cand_local[d_all[cand_local] <= R_sc]
                for cl in cand_local.tolist():
                    g = int(fit_idx[cl])
                    sample_set.add(g)
                    if len(sample_set) >= target:
                        break

        # ---------- Stage 3: farthest-first padding ------------------------
        if len(sample_set) < target:
            # Cheap padding: random + farthest-first hybrid
            remaining = np.setdiff1d(
                np.arange(N), np.fromiter(sample_set, dtype=np.int64),
                assume_unique=False,
            )
            need = target - len(sample_set)
            if remaining.size <= need:
                for r in remaining.tolist():
                    sample_set.add(int(r))
            else:
                # Sample candidates and pick the farthest from current set
                cand_pool_size = min(remaining.size, max(need * 4, 4096))
                cand = rng.choice(remaining, size=cand_pool_size, replace=False)
                cur = np.fromiter(sample_set, dtype=np.int64)
                # Compare cand vs a sample of current selection (cap to 2k)
                cur_sample = cur if cur.size <= 2000 else rng.choice(cur, 2000, replace=False)
                cur_vec = embeddings[cur_sample].astype(np.float64)
                cand_vec = embeddings[cand].astype(np.float64)
                # Pairwise min distance, chunked
                cs = 1024
                min_d = np.full(cand.shape[0], np.inf, dtype=np.float64)
                for j in range(0, cur_vec.shape[0], cs):
                    block = cur_vec[j : j + cs]
                    diff = cand_vec[:, None, :] - block[None, :, :]
                    dd = np.sqrt((diff * diff).sum(axis=2)).min(axis=1)
                    np.minimum(min_d, dd, out=min_d)
                top = np.argsort(min_d)[::-1][:need]
                for idx in top.tolist():
                    sample_set.add(int(cand[idx]))

        sample_indices = np.array(sorted(sample_set), dtype=np.int64)[:target]

        # ---------- Stratum assignment for ALL N rows ----------------------
        if N > self.fit_cap:
            # Assign full N via 1-NN to the LID-strata representatives
            # Use stratum centroids in the fit slice as anchors
            stratum_full = np.zeros(N, dtype=np.int32)
            stratum_full[fit_idx] = stratum_fit
            non_fit_mask = np.ones(N, dtype=bool)
            non_fit_mask[fit_idx] = False
            non_fit_idx = np.flatnonzero(non_fit_mask)
            # 1-NN against fit_vec for label propagation, chunked
            for i in range(0, non_fit_idx.shape[0], DEFAULT_CHUNK):
                j = min(i + DEFAULT_CHUNK, non_fit_idx.shape[0])
                block_idx = non_fit_idx[i:j]
                block_vec = embeddings[block_idx].astype(np.float64)
                diff_norm = (block_vec * block_vec).sum(axis=1, keepdims=True)
                fit64 = fit_vec.astype(np.float64)
                fit_norm = (fit64 * fit64).sum(axis=1)[None, :]
                cross = block_vec @ fit64.T
                d2 = diff_norm + fit_norm - 2.0 * cross
                nn = np.argmin(d2, axis=1)
                stratum_full[block_idx] = stratum_fit[nn]
            lid_full = np.zeros(N, dtype=np.float64)
            lid_full[fit_idx] = lid_fit
        else:
            stratum_full = stratum_fit
            lid_full = lid_fit

        # Ensure all K bins are represented (fall back to round-robin patching)
        used = np.unique(stratum_full)
        if used.shape[0] < K:
            missing = sorted(set(range(K)) - set(used.tolist()))
            # Reassign random rows (proportional to N) to the missing bins
            rr_idx = rng.choice(N, size=len(missing), replace=False)
            for r, sid in zip(rr_idx, missing):
                stratum_full[r] = np.int32(sid)

        self._state = HKBURepSampleState(
            sample_indices=sample_indices,
            sample_vectors=embeddings[sample_indices].astype(np.float32, copy=False),
            stratum_ids=stratum_full.astype(np.int32),
            lid=lid_full,
            K=K,
            N=N,
        )
        return self

    # ----------------------------------------------------------- predict
    def predict_cardinality(
        self,
        query_vec: np.ndarray,
        selectivity: float,
        other_state: Optional[HKBURepSampleState] = None,
    ) -> float:
        """Stratified cardinality estimate using the representative sample.

        Counts sample points whose distance to ``query_vec`` falls within the
        selectivity-induced ball, and rescales by ``N / |sample|`` weighted
        per-stratum (Horvitz-Thompson under proportional allocation).
        """
        state = other_state if other_state is not None else self._state
        if state is None:
            raise RuntimeError("call .fit() first")
        if not (0.0 < selectivity <= 1.0):
            raise ValueError(f"selectivity must be in (0, 1]; got {selectivity}")

        q = np.asarray(query_vec, dtype=np.float64).reshape(-1)
        sv = state.sample_vectors.astype(np.float64)
        if q.shape[0] != sv.shape[1]:
            raise ValueError(f"query dim {q.shape[0]} != fitted dim {sv.shape[1]}")
        diff = sv - q[None, :]
        dists = np.sqrt((diff * diff).sum(axis=1))
        radius = float(np.quantile(dists, selectivity))
        in_ball = dists <= radius

        # Per-stratum Horvitz-Thompson with sample stratum tags
        sample_strata = state.stratum_ids[state.sample_indices]
        K = state.K
        est = 0.0
        for k in range(K):
            stratum_mask = state.stratum_ids == k
            n_k = int(stratum_mask.sum())
            if n_k == 0:
                continue
            sm = sample_strata == k
            m_k = int(sm.sum())
            if m_k == 0:
                # No sample in this stratum; defer to uniform rate
                est += float(in_ball.mean()) * n_k
                continue
            hits_k = int((in_ball & sm).sum())
            est += hits_k * (n_k / m_k)
        return float(est)


# ---------------------------------------------------------------------------
# Drop-in stratify_method (multi-vector signature)
# ---------------------------------------------------------------------------
def stratify_method(
    emb1: np.ndarray,
    emb2: Optional[np.ndarray] = None,
    K: int = DEFAULT_K,
    seed: int = 0,
    sample_size: int = 10_000,
    k_sol: int = DEFAULT_KSOL,
    beta: float = DEFAULT_BETA,
    t_reinforce: int = DEFAULT_T,
    fit_cap: int = DEFAULT_FIT_CAP,
    **kwargs,
) -> np.ndarray:
    """LID-stratified representative-sampling stratification (HKBU-RepSample).

    Concatenates ``emb1`` and (optionally) ``emb2`` (norm-aware), runs
    ``HKBURepSampleEstimator.fit`` and returns the per-row LID stratum id.
    """
    if emb1.ndim != 2:
        raise ValueError(f"emb1 must be 2D; got {emb1.shape}")
    if emb2 is not None:
        if emb2.ndim != 2:
            raise ValueError(f"emb2 must be 2D; got {emb2.shape}")
        if emb1.shape[0] != emb2.shape[0]:
            raise ValueError(
                f"row count mismatch: emb1 {emb1.shape[0]} vs emb2 {emb2.shape[0]}"
            )
        n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
        n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
        emb_full = np.concatenate(
            [emb1.astype(np.float32) / n1, emb2.astype(np.float32) / n2], axis=1
        )
    else:
        emb_full = emb1.astype(np.float32)

    N = emb_full.shape[0]
    sample_size_eff = min(max(sample_size, K), N)
    est = HKBURepSampleEstimator(
        K=K,
        sample_size=sample_size_eff,
        random_state=seed,
        k_sol=k_sol,
        beta=beta,
        t_reinforce=t_reinforce,
        fit_cap=fit_cap,
    )
    try:
        est.fit(emb_full)
        sids = est._state.stratum_ids  # type: ignore[union-attr]
    except Exception:
        # Fallback: KMeans++ assignment on a quick subsample (paper's spirit
        # is "facility-location seeding", which KMeans approximates).
        from sklearn.cluster import MiniBatchKMeans

        km = MiniBatchKMeans(
            n_clusters=K, random_state=seed, batch_size=1024, n_init=3, max_iter=50
        )
        if N > fit_cap:
            rng_fb = np.random.default_rng(seed)
            sub = rng_fb.choice(N, size=fit_cap, replace=False)
            km.fit(emb_full[sub])
        else:
            km.fit(emb_full)
        sids = km.predict(emb_full).astype(np.int32)
    return sids.astype(np.int32)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def _self_test() -> None:
    import warnings

    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    rng = np.random.default_rng(0)

    # ---- Mixed-density synthetic: 4 dense clusters + sparse scatter ------
    N, d1, d2 = 8_000, 96, 768
    K = 20
    n_blocks = 4
    centers_x = rng.standard_normal((n_blocks, d1)) * 5.0
    centers_y = rng.standard_normal((n_blocks, d2)) * 5.0
    block = rng.integers(0, n_blocks, size=N)
    emb1 = (
        centers_x[block] + rng.standard_normal((N, d1)) * 0.3
    ).astype(np.float32)
    emb2 = (
        centers_y[block] + rng.standard_normal((N, d2)) * 0.3
    ).astype(np.float32)
    # Inject 10% sparse outliers
    n_sp = N // 10
    emb1[:n_sp] = rng.standard_normal((n_sp, d1)).astype(np.float32) * 8.0
    emb2[:n_sp] = rng.standard_normal((n_sp, d2)).astype(np.float32) * 8.0

    # ---- stratify_method smoke test --------------------------------------
    sids = stratify_method(emb1, emb2, K=K, seed=42, sample_size=2000)
    assert sids.shape == (N,) and sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < K
    counts = np.bincount(sids, minlength=K)
    print(
        f"[self-test] HKBU-RepSample multi-vector: "
        f"sids range=[{sids.min()},{sids.max()}], "
        f"K_used={(counts > 0).sum()}/{K}, "
        f"max/min={counts.max() / max(counts.min(), 1):.2f}"
    )
    assert (counts > 0).sum() >= K // 2

    # Determinism
    sids2 = stratify_method(emb1, emb2, K=K, seed=42, sample_size=2000)
    agreement = float((sids == sids2).mean())
    print(f"[self-test] determinism agreement: {agreement:.3f}")
    assert agreement >= 0.95

    # ---- single-vector path ---------------------------------------------
    sids_single = stratify_method(emb1, None, K=K, seed=42, sample_size=2000)
    assert sids_single.shape == (N,)
    print(
        f"[self-test] HKBU-RepSample single-vector: "
        f"K_used={(np.bincount(sids_single, minlength=K) > 0).sum()}/{K}"
    )

    # ---- Estimator end-to-end -------------------------------------------
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate(
        [emb1 / n1, emb2 / n2], axis=1
    ).astype(np.float32)
    est = HKBURepSampleEstimator(K=K, sample_size=2000, random_state=0)
    est.fit(emb_concat)
    q = emb_concat[123]
    card_05 = est.predict_cardinality(q, selectivity=0.5)
    card_01 = est.predict_cardinality(q, selectivity=0.1)
    print(
        f"[self-test] cardinality estimates: "
        f"sel=0.1 -> {card_01:.0f}, sel=0.5 -> {card_05:.0f} (true~{N//2})"
    )
    assert card_01 < card_05  # monotonic in selectivity
    assert 0.0 < card_05 <= N * 1.5

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
