#!/usr/bin/env python3
"""
NeuroCard-lite — learned density estimator for vector-augmented analytical queries.

본 모듈은 Yang et al. NeuroCard (VLDB 2020, arXiv:2006.08109) 의 lightweight variant
로, 단일 테이블 (emb1, emb2) 두 임베딩 컬럼의 결합 분포를 작은 autoregressive
MLP 로 모델링한다. 학습된 모델은 query embedding pair 에 대해 P(emb1) ×
P(emb2|emb1) 로 cardinality 를 직접 추정하므로, RQ3 의 stratification baseline 과
달리 *direct cardinality estimator* 경로 (B7 / alternative) 로 통합된다.

Algorithm (autoregressive factorization on 2 columns):
    P(emb1, emb2) ≈ P_θ1(emb1) × P_θ2(emb2 | emb1)

    - P_θ1: 3-layer MLP, input=emb1 (d1) → output=μ, log σ (Gaussian density head)
    - P_θ2: 3-layer MLP, input=concat(emb1, emb2) (d1+d2) → output=μ, log σ
    - Loss: NLL on full data (또는 1% subsample, 본 lite variant 기본)
    - Inference: query (emb1_q, emb2_q) → density × n_total → cardinality

원 논문 (Yang VLDB 2020) 은 Wide-Deep (Made-style) 의 deep autoregressive 모델이며
schema-level join cardinality SOTA (IMDB median q-error 1.5). 본 lite variant 는
3-layer × hidden 128 + Gaussian head 로 축소하여 CPU 에서 100 epoch 학습 가능하도록
경량화한다.

Reference:
    Yang, Z., Kamsetty, A., Luan, S., Liang, E., Duan, Y., Chen, X., & Stoica, I.
    (2020). NeuroCard: One Cardinality Estimator for All Tables. Proceedings of
    the VLDB Endowment, 14(1). https://arxiv.org/abs/2006.08109

Usage:
    from neurocard_lite import train_neurocard, estimate_card
    model = train_neurocard(emb1, emb2, hidden_dim=128, n_epochs=100, seed=0)
    card = estimate_card(model, query_emb1, query_emb2, D_target=0.5, n_total=1_000_000)
"""
from __future__ import annotations

import time
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

DEFAULT_HIDDEN = 128
DEFAULT_EPOCHS = 100
DEFAULT_SEED = 0
DEFAULT_K = 20
DEFAULT_LR = 1e-3
DEFAULT_BATCH = 256
DEFAULT_LEARN_FRAC = 0.01
MIN_LOG_SIGMA = -6.0  # numeric guard
MAX_LOG_SIGMA = 4.0


# ---------------------------------------------------------------------------
# Gaussian-head MLP (one factor of autoregressive density)
# ---------------------------------------------------------------------------


class _GaussianHeadMLP(nn.Module):
    """3-layer MLP outputting per-dim Gaussian (μ, log σ).

    Models a conditional density p(target | context) where target dim = `out_dim`
    and context dim = `in_dim`. The likelihood factorizes per-dimension as an
    independent Gaussian — a standard simplifying assumption for the lite
    variant; the full NeuroCard paper uses MADE/MAF-style mixture heads.
    """

    def __init__(self, in_dim: int, out_dim: int, hidden_dim: int = DEFAULT_HIDDEN) -> None:
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.net = nn.Sequential(
            nn.Linear(max(in_dim, 1), hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2 * out_dim),
        )

    def forward(self, context: Optional[torch.Tensor], n_rows: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Return (μ, log σ) tensors of shape (B, out_dim)."""
        if context is None or self.in_dim == 0:
            # unconditional: feed a zero pseudo-context
            x = torch.zeros((n_rows, 1), device=next(self.parameters()).device)
        else:
            x = context
        out = self.net(x)
        mu, log_sigma = out.chunk(2, dim=-1)
        log_sigma = torch.clamp(log_sigma, MIN_LOG_SIGMA, MAX_LOG_SIGMA)
        return mu, log_sigma


def _gaussian_logp(target: torch.Tensor, mu: torch.Tensor, log_sigma: torch.Tensor) -> torch.Tensor:
    """Sum of per-dim Gaussian log-likelihood. Returns (B,)."""
    var = torch.exp(2 * log_sigma)
    sq = (target - mu) ** 2
    # log N(x; μ, σ²) per dim = -0.5 log(2π) - log σ - sq / (2 σ²)
    logp_per_dim = -0.5 * np.log(2 * np.pi) - log_sigma - sq / (2 * var + 1e-12)
    return logp_per_dim.sum(dim=-1)


# ---------------------------------------------------------------------------
# NeuroCard-lite model wrapper (two factors)
# ---------------------------------------------------------------------------


class NeuroCardLite(nn.Module):
    """Two-factor autoregressive density: P(emb1) × P(emb2 | emb1).

    Stores (d1, d2, n_total, n_train) so estimate_card() can multiply density
    by row count without external bookkeeping.
    """

    def __init__(self, d1: int, d2: int, hidden_dim: int = DEFAULT_HIDDEN) -> None:
        super().__init__()
        self.d1 = d1
        self.d2 = d2
        self.head1 = _GaussianHeadMLP(in_dim=0, out_dim=d1, hidden_dim=hidden_dim)
        self.head2 = _GaussianHeadMLP(in_dim=d1, out_dim=d2, hidden_dim=hidden_dim)
        self.register_buffer("n_total", torch.tensor(0, dtype=torch.long))

    def log_prob(self, emb1: torch.Tensor, emb2: torch.Tensor) -> torch.Tensor:
        """log P(emb1, emb2) of each row. Returns (B,)."""
        mu1, ls1 = self.head1(None, n_rows=emb1.shape[0])
        lp1 = _gaussian_logp(emb1, mu1, ls1)
        mu2, ls2 = self.head2(emb1, n_rows=emb1.shape[0])
        lp2 = _gaussian_logp(emb2, mu2, ls2)
        return lp1 + lp2


# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------


def train_neurocard(
    emb1: np.ndarray,
    emb2: np.ndarray,
    hidden_dim: int = DEFAULT_HIDDEN,
    n_epochs: int = DEFAULT_EPOCHS,
    seed: int = DEFAULT_SEED,
    device: str | None = None,
    learn_frac: float = DEFAULT_LEARN_FRAC,
    lr: float = DEFAULT_LR,
    batch_size: int = DEFAULT_BATCH,
    verbose: bool = False,
) -> NeuroCardLite:
    """Train the NeuroCard-lite autoregressive density on (emb1, emb2).

    Following the lite variant convention, learn on a 1% random subsample by
    default (~80K rows for 8M-row tables) to keep CPU training time bounded.

    Args:
        emb1: (N, d1) float embedding of column 1.
        emb2: (N, d2) float embedding of column 2.
        hidden_dim: MLP hidden width.
        n_epochs: Optimization epochs over the subsample.
        seed: RNG seed for subsampling and torch init.
        device: "cpu" or "cuda".
        learn_frac: Fraction of rows used for training (lite default 0.01).
        lr: Adam learning rate.
        batch_size: Mini-batch size.
        verbose: If True, print epoch-level NLL.

    Returns:
        Trained NeuroCardLite model with `n_total` buffer set to len(emb1).
    """
    if emb1.ndim != 2 or emb2.ndim != 2:
        raise ValueError(
            f"emb1/emb2 must be 2D, got {emb1.shape} / {emb2.shape}"
        )
    if emb1.shape[0] != emb2.shape[0]:
        raise ValueError(
            f"emb1/emb2 row count mismatch: {emb1.shape[0]} vs {emb2.shape[0]}"
        )

    n_total = emb1.shape[0]
    d1, d2 = emb1.shape[1], emb2.shape[1]

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)

    # 1% subsample (lite variant) — fall back to all rows if data smaller
    n_train = max(int(round(n_total * learn_frac)), min(n_total, 1024))
    n_train = min(n_train, n_total)
    if n_train < n_total:
        idx = rng.choice(n_total, size=n_train, replace=False)
    else:
        idx = np.arange(n_total)

    e1 = torch.from_numpy(emb1[idx].astype(np.float32)).to(device)
    e2 = torch.from_numpy(emb2[idx].astype(np.float32)).to(device)

    model = NeuroCardLite(d1=d1, d2=d2, hidden_dim=hidden_dim).to(device)
    model.n_total.fill_(n_total)

    optim = torch.optim.Adam(model.parameters(), lr=lr)
    perm_rng = np.random.default_rng(seed + 1)

    model.train()
    for epoch in range(n_epochs):
        perm = perm_rng.permutation(n_train)
        total_nll = 0.0
        n_batches = 0
        for start in range(0, n_train, batch_size):
            batch_idx = perm[start:start + batch_size]
            batch_idx_t = torch.as_tensor(batch_idx, dtype=torch.long, device=device)
            b1 = e1.index_select(0, batch_idx_t)
            b2 = e2.index_select(0, batch_idx_t)
            logp = model.log_prob(b1, b2)
            loss = -logp.mean()
            optim.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optim.step()
            total_nll += float(loss.detach().cpu())
            n_batches += 1
        if verbose and (epoch % max(1, n_epochs // 10) == 0 or epoch == n_epochs - 1):
            print(f"  [neurocard-lite] epoch {epoch:>3d}/{n_epochs} "
                  f"nll={total_nll / max(n_batches, 1):.4f}")

    model.eval()
    return model


# ---------------------------------------------------------------------------
# Cardinality estimation
# ---------------------------------------------------------------------------


def _query_log_density(
    model: NeuroCardLite,
    query_emb1: np.ndarray,
    query_emb2: np.ndarray,
    device: Optional[str] = None,
) -> np.ndarray:
    """Return per-query log P(emb1_q, emb2_q) as float64 array."""
    if device is None:
        device = str(next(model.parameters()).device)
    if query_emb1.ndim == 1:
        query_emb1 = query_emb1[None, :]
    if query_emb2.ndim == 1:
        query_emb2 = query_emb2[None, :]
    e1 = torch.from_numpy(query_emb1.astype(np.float32)).to(device)
    e2 = torch.from_numpy(query_emb2.astype(np.float32)).to(device)
    with torch.no_grad():
        logp = model.log_prob(e1, e2)
    return logp.detach().cpu().numpy().astype(np.float64)


def _query_density(
    model: NeuroCardLite,
    query_emb1: np.ndarray,
    query_emb2: np.ndarray,
    device: Optional[str] = None,
) -> np.ndarray:
    """Return per-query density P(emb1_q, emb2_q) ∈ ℝ⁺ as float64 array.

    NOTE: in high-dim spaces this often underflows to 0; prefer
    `_query_log_density` for downstream math. Kept for API parity.
    """
    log_p = _query_log_density(model, query_emb1, query_emb2, device=device)
    return np.exp(log_p)


def estimate_card(
    model: NeuroCardLite,
    query_emb1: np.ndarray,
    query_emb2: np.ndarray,
    D_target: float,
    n_total: Optional[int] = None,
) -> int:
    """Estimate range-query cardinality |{r : dist(r, q) < D_target}|.

    Approach (lite, two-column): treat the trained density as the joint
    P(emb1, emb2) and approximate the selectivity of a radius-D query as the
    density at the query point times the volume of a d-ball of radius
    D_target / √(d1+d2) per dimension. This is intentionally a coarse first
    approximation — the original NeuroCard uses progressive sampling /
    importance sampling against the autoregressive model, which is heavier.
    Per the lite contract, this gives a numerically stable monotonic
    estimator suitable for B7 baseline comparison.

    Args:
        model: Trained NeuroCardLite.
        query_emb1: Query column-1 embedding, (d1,) or (Q, d1).
        query_emb2: Query column-2 embedding, (d2,) or (Q, d2).
        D_target: Distance threshold of the range query.
        n_total: Total row count to scale density into cardinality. If None,
            use the model's stored buffer.

    Returns:
        Integer cardinality estimate (rounded, ≥ 0). For batch queries the
        first cardinality is returned (callers needing per-query batches can
        loop or call _query_density directly).
    """
    if n_total is None:
        n_total = int(model.n_total.item())
    if n_total <= 0:
        raise ValueError("n_total must be > 0 (call train_neurocard first or pass explicitly)")
    # Work fully in log-space to avoid high-dim underflow.
    log_density = _query_log_density(model, query_emb1, query_emb2)
    # Volume term (per-dim Gaussian, isotropic radius approximation):
    # selectivity ≈ density × (2 D / √d_total)^d_total with d_total = d1 + d2
    d_total = model.d1 + model.d2
    radius_per_dim = max(D_target / np.sqrt(d_total), 1e-8)
    log_vol = d_total * np.log(2.0 * radius_per_dim)
    log_selectivity = np.minimum(log_density + log_vol, 0.0)  # cap at log(1)=0
    selectivity = np.exp(log_selectivity)
    card = int(round(float(selectivity[0]) * n_total))
    return max(card, 0)


# ---------------------------------------------------------------------------
# stratify-compatible wrapper (latent-space K-means assignment)
# ---------------------------------------------------------------------------


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = DEFAULT_SEED,
    hidden_dim: int = DEFAULT_HIDDEN,
    n_epochs: int = 20,
    device: str = "cpu",
    **_kwargs,
) -> np.ndarray:
    """Optional stratify wrapper — bin rows by NeuroCard-lite log-density.

    Usage parity with the 11 RQ3 stratify methods (e.g. sparse_rp.assign_*).
    Maps each row to one of K strata via quantile-bin of model log P(emb1, emb2)
    so that high-density and low-density regions are separated; this is *not*
    the canonical NeuroCard use, but provides a fair latent-feature stratifier
    for ablation against P1/P4 paradigms.

    Args:
        emb1, emb2: Full data, (N, d1) / (N, d2).
        K: Number of strata.
        seed: RNG seed.
        hidden_dim: MLP width.
        n_epochs: Training epochs (kept small here — stratify path is a
            secondary use case).
        device: torch device string.

    Returns:
        Stratum ids of shape (N,) int32, values in [0, K).
    """
    if emb1.shape[0] != emb2.shape[0]:
        raise ValueError("emb1/emb2 row count mismatch")
    if emb1.shape[0] < K:
        raise ValueError(f"need >= {K} rows for {K} strata, got {emb1.shape[0]}")
    model = train_neurocard(
        emb1, emb2,
        hidden_dim=hidden_dim, n_epochs=n_epochs,
        seed=seed, device=device,
    )
    device_t = str(next(model.parameters()).device)
    e1 = torch.from_numpy(emb1.astype(np.float32)).to(device_t)
    e2 = torch.from_numpy(emb2.astype(np.float32)).to(device_t)
    chunk = 4096
    log_densities = np.empty(emb1.shape[0], dtype=np.float64)
    with torch.no_grad():
        for start in range(0, emb1.shape[0], chunk):
            stop = min(start + chunk, emb1.shape[0])
            log_densities[start:stop] = (
                model.log_prob(e1[start:stop], e2[start:stop])
                .detach().cpu().numpy().astype(np.float64)
            )
    quantiles = np.quantile(log_densities, np.linspace(0.0, 1.0, K + 1))
    edges = quantiles[1:-1]
    sids = np.searchsorted(edges, log_densities, side="right")
    return np.clip(sids, 0, K - 1).astype(np.int32)


# ---------------------------------------------------------------------------
# Mini-run self test
# ---------------------------------------------------------------------------


def _self_test() -> None:
    """Mini-run: N=5000, d1=96 (DEEP-style), d2=768 (Wiki-style), 10 epoch."""
    rng = np.random.default_rng(0)
    n, d1, d2 = 5000, 96, 768
    emb1 = rng.standard_normal((n, d1)).astype(np.float32)
    emb2 = rng.standard_normal((n, d2)).astype(np.float32)
    print(f"[self-test] data: emb1={emb1.shape}, emb2={emb2.shape}")

    t0 = time.time()
    model = train_neurocard(
        emb1, emb2,
        hidden_dim=128, n_epochs=10, seed=0, device="cpu", verbose=True,
    )
    t_train = time.time() - t0
    print(f"[self-test] training done in {t_train:.2f}s")

    # 1-query estimate (out-of-distribution random query)
    q_emb1 = rng.standard_normal(d1).astype(np.float32)
    q_emb2 = rng.standard_normal(d2).astype(np.float32)
    card_ood = estimate_card(model, q_emb1, q_emb2, D_target=10.0, n_total=n)
    print(f"[self-test] estimate_card OOD → {card_ood} (n_total={n}, D=10.0)")
    assert card_ood >= 0, "card must be non-negative"

    # In-distribution query (use a training row) — log-space density should be
    # higher than for an OOD point.
    log_dens_id = _query_log_density(model, emb1[0], emb2[0])
    log_dens_ood = _query_log_density(model, q_emb1, q_emb2)
    print(f"[self-test] log P (in-dist row 0) = {float(log_dens_id[0]):.2f}")
    print(f"[self-test] log P (OOD random)   = {float(log_dens_ood[0]):.2f}")
    assert log_dens_id[0] >= log_dens_ood[0] - 50.0, \
        "in-distribution log-density should not be drastically lower than OOD"

    # batched log density
    qbatch1 = rng.standard_normal((4, d1)).astype(np.float32)
    qbatch2 = rng.standard_normal((4, d2)).astype(np.float32)
    log_dens = _query_log_density(model, qbatch1, qbatch2)
    print(f"[self-test] batched log P: {log_dens}")
    assert log_dens.shape == (4,)

    # stratify wrapper sanity
    sids = stratify_method(emb1[:1024], emb2[:1024], K=20, seed=0, n_epochs=2)
    counts = np.bincount(sids, minlength=20)
    print(f"[self-test] stratify K=20: min={int(counts.min())}, max={int(counts.max())}")
    assert sids.min() >= 0 and sids.max() < 20
    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
