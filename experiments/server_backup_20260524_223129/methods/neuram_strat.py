#!/usr/bin/env python3
"""Tier A — NeurAM autoencoder stratification (Geraci et al. arXiv 2506.08921, 2026).

Reference
---------
Geraci F. et al. ``NeurAM: Neural Auxiliary-variable Multifidelity Monte
Carlo for Variance Reduction''. arXiv preprint 2506.08921, 2026.
URL: https://arxiv.org/abs/2506.08921

Algorithm
---------
NeurAM (Neural Auxiliary-variable Multifidelity) trains a small
auto-encoder

    f_enc : R^d -> R^1   (1-D latent bottleneck)
    f_dec : R^1 -> R^d

with reconstruction loss ``|| f_dec(f_enc(x)) - x ||^2``. Once trained, the
1-D latent ``z = f_enc(x)`` is used as the *auxiliary variable* in
multi-fidelity Monte Carlo. Geraci et al. 2026 §1 prove a
*dimension-invariant* O(S^{-2}) variance reduction guarantee on the
estimator built from this latent — the variance does not blow up with
input dimension ``d``, in contrast to dense RP whose JL bound scales with
``log d``.

For *stratification* (this capstone), we apply the same trained encoder
to all rows and quantile-bin the 1-D latent into ``K`` strata. The
training is short (default 100 epochs over an 80 K-row subsample).
"""

from __future__ import annotations

import os
import warnings

import numpy as np

DEFAULT_K: int = 20
DEFAULT_EPOCHS: int = 100
DEFAULT_SUBSAMPLE: int = 80_000
DEFAULT_BATCH: int = 1024
DEFAULT_HIDDEN: int = 64
DEFAULT_LR: float = 1e-3


def _build_torch_model(d: int, hidden: int, latent: int = 1):
    """Construct symmetric MLP encoder/decoder with a 1-D bottleneck."""
    import torch.nn as nn

    encoder = nn.Sequential(
        nn.Linear(d, hidden),
        nn.ReLU(),
        nn.Linear(hidden, latent),
    )
    decoder = nn.Sequential(
        nn.Linear(latent, hidden),
        nn.ReLU(),
        nn.Linear(hidden, d),
    )

    class AE(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = encoder
            self.decoder = decoder

        def forward(self, x):
            z = self.encoder(x)
            xhat = self.decoder(z)
            return xhat, z

    return AE()


def stratify_method(
    emb1: np.ndarray,
    emb2: np.ndarray,
    K: int = DEFAULT_K,
    seed: int = 0,
    epochs: int = DEFAULT_EPOCHS,
    subsample: int = DEFAULT_SUBSAMPLE,
    batch_size: int = DEFAULT_BATCH,
    hidden: int = DEFAULT_HIDDEN,
    lr: float = DEFAULT_LR,
    device: str | None = None,
    **kwargs,
) -> np.ndarray:
    """Stratify rows by NeurAM 1-D latent quantile bins.

    Parameters
    ----------
    emb1 : np.ndarray, shape (N, d1)
        First embedding column.
    emb2 : np.ndarray, shape (N, d2)
        Second embedding column.
    K : int, default 20
        Number of quantile bins (output stratum IDs in ``[0, K)``).
    seed : int, default 0
        Seed for PyTorch / NumPy.
    epochs : int, default 100
        Autoencoder training epochs over the subsample.
    subsample : int, default 80_000
        Cap on rows used for autoencoder training (full N for inference).
    batch_size : int, default 1024
        Mini-batch size for SGD.
    hidden : int, default 64
        Hidden layer width of encoder/decoder MLP.
    lr : float, default 1e-3
        Adam learning rate.
    device : {"cpu", "cuda", None}, default None
        Torch device. None = auto (cuda if available, else cpu).

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

    import torch
    import torch.nn as nn

    # Norm-aware concat (matches measure_multi_paradigm.build_concat semantics)
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    emb_concat = np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)
    N, d = emb_concat.shape

    # Determine device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    dev = torch.device(device)

    # Reproducibility (subject to torch's caveats on cuDNN nondeterminism)
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Build training subsample
    rng = np.random.default_rng(seed)
    if N > subsample:
        train_idx = rng.choice(N, size=subsample, replace=False)
        train_data = emb_concat[train_idx]
    else:
        train_data = emb_concat

    # Model + optimizer
    model = _build_torch_model(d=d, hidden=hidden, latent=1).to(dev)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    # Train loop
    train_t = torch.from_numpy(train_data).to(dev)
    n_train = train_t.shape[0]
    model.train()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        for ep in range(epochs):
            perm = torch.randperm(n_train, device=dev)
            for start in range(0, n_train, batch_size):
                idx = perm[start : start + batch_size]
                x = train_t[idx]
                xhat, z = model(x)
                loss = loss_fn(xhat, x)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

    # Inference: encode all N rows in chunks
    model.eval()
    proj = np.empty(N, dtype=np.float32)
    chunk = 50_000
    with torch.no_grad():
        for i in range(0, N, chunk):
            j = min(i + chunk, N)
            x = torch.from_numpy(emb_concat[i:j]).to(dev)
            z = model.encoder(x)  # type: ignore[attr-defined]
            proj[i:j] = z.detach().cpu().numpy().reshape(-1)

    # Quantile bins on 1-D latent
    edges = np.quantile(proj, np.linspace(0.0, 1.0, K + 1))[1:-1]
    sids = np.searchsorted(edges, proj, side="right")
    return np.clip(sids, 0, K - 1).astype(np.int32)


def _self_test() -> None:
    rng = np.random.default_rng(0)
    N, d1, d2 = 10_000, 96, 768
    emb1 = rng.standard_normal((N, d1)).astype(np.float32)
    emb2 = rng.standard_normal((N, d2)).astype(np.float32)

    # For the self-test we use a short training schedule to keep runtime bounded
    sids = stratify_method(
        emb1, emb2, K=20, seed=0,
        epochs=20, subsample=8_000, batch_size=512, hidden=32,
    )
    assert sids.shape == (N,)
    assert sids.dtype == np.int32
    assert sids.min() >= 0 and sids.max() < 20

    counts = np.bincount(sids, minlength=20)
    K_used = (counts > 0).sum()
    ratio = float(counts.max() / max(counts.min(), 1))
    print(
        f"[self-test] NeurAM (AE 1-D latent quantile): N={N} d={d1+d2} "
        f"K_used={K_used}/20 max/min={ratio:.2f} counts[:5]={counts[:5].tolist()}"
    )
    assert ratio < 1.5, f"quantile bins should be ~uniform, got {ratio:.2f}"

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
    sids_skew = stratify_method(
        skewed_e1, skewed_e2, K=20, seed=0,
        epochs=20, subsample=5_000, batch_size=512, hidden=32,
    )
    counts_skew = np.bincount(sids_skew, minlength=20)
    print(
        f"[self-test] NeurAM skewed: K_used={(counts_skew > 0).sum()}/20 "
        f"max/min={float(counts_skew.max() / max(counts_skew.min(), 1)):.2f}"
    )

    print("[self-test] OK")


if __name__ == "__main__":
    # Suppress pandas PyArrow / torch warnings under default test runs
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    _self_test()
