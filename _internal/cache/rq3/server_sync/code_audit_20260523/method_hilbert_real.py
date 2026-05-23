#!/usr/bin/env python3
"""
RQ3 ★3 — 진짜 Hilbert curve assign (Wikipedia 표준 xy2d) — paper exact 재현용.

배경 (handoff_v3 §0.2 / §1.1 #1):
- 기존 ★3 hilbert 는 measure_paper_exact.py L446-456 에서 PCA 2D + lex sort 였음.
  명칭 "Hilbert" 표명 ↔ 실제 simple proxy → 학술 fraud risk.
- 사용자 결정 (5/10 22:25): (C) 현재 → `pca2d_lex` rename + 진짜 hilbert 별도 추가
  → "Hilbert curve 진짜 locality 효과 vs PCA proxy 효과 분리 검증" finding.

본 모듈:
- assign_hilbert_real(all_vecs, n_strata=20, hilbert_order=10, seed=42)
- (a) PCA → 2D projection (sklearn full SVD, deterministic)
- (b) PCA coord → 2^p × 2^p integer grid normalize
- (c) Wikipedia xy2d Hilbert curve algorithm (vectorized) → 1D distance
- (d) quantile boundary (n_strata 분할) → stratum_id

raw 구현체 (`experiments/code/rq3/hilbert/hilbert_curve.py`) 가 server cache
(`/mnt/hdd0/home/capstone2026/cache/rq3/hilbert/hilbert_curve.py`) 에 이미 배치
되어 있음. 본 모듈은 raw import 우선, 실패 시 self-contained fallback.

Reference:
- https://en.wikipedia.org/wiki/Hilbert_curve#Applications_and_mapping_algorithms
- "Convert from a quadrant index to a binary string" 표준 알고리즘
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# ---- 1. raw hilbert_curve 모듈 import 시도 (server / local 양쪽) ----
_HILBERT_PATHS = [
    "/mnt/hdd0/home/capstone2026/cache/rq3/hilbert",     # server
    str(Path(__file__).resolve().parent.parent.parent /  # local repo path
        "experiments/code/rq3/hilbert"),
]

_RAW_AVAILABLE = False
for _p in _HILBERT_PATHS:
    if Path(_p).is_dir() and (Path(_p) / "hilbert_curve.py").is_file():
        if _p not in sys.path:
            sys.path.insert(0, _p)
        try:
            from hilbert_curve import (  # type: ignore
                fit_hilbert_mapper,
                assign_hilbert as _raw_assign,
            )
            _RAW_AVAILABLE = True
            break
        except Exception:
            pass


# ---- 2. self-contained fallback (Wikipedia xy2d 표준) ----
def _hilbert_xy_to_d_fallback(x: np.ndarray, y: np.ndarray, p: int) -> np.ndarray:
    """Wikipedia 표준 Hilbert curve algorithm (xy → distance), NumPy vectorized.

    n = 2^p, x/y in [0, n).
    https://en.wikipedia.org/wiki/Hilbert_curve#Applications_and_mapping_algorithms
    """
    n = 1 << p
    x = np.asarray(x, dtype=np.int64).copy()
    y = np.asarray(y, dtype=np.int64).copy()
    d = np.zeros_like(x)
    s = n >> 1
    while s > 0:
        rx = ((x & s) > 0).astype(np.int64)
        ry = ((y & s) > 0).astype(np.int64)
        d += s * s * ((3 * rx) ^ ry)
        # rotate/flip when ry == 0
        flip = (ry == 0) & (rx == 1)
        x[flip] = n - 1 - x[flip]
        y[flip] = n - 1 - y[flip]
        mask = (ry == 0)
        x_swap = x[mask].copy()
        x[mask] = y[mask]
        y[mask] = x_swap
        s >>= 1
    return d


def _assign_fallback(all_vecs: np.ndarray, n_strata: int, p: int, seed: int) -> np.ndarray:
    """raw module 없을 때 self-contained 진짜 Hilbert curve assign."""
    from sklearn.decomposition import PCA

    if all_vecs.ndim != 2:
        raise ValueError(f"all_vecs must be 2D, got {all_vecs.shape}")
    if all_vecs.shape[1] < 2:
        raise ValueError(f"need dim >= 2 for PCA(2), got {all_vecs.shape[1]}")

    # PCA 2D (float64 fit, full SVD — deterministic)
    samples64 = all_vecs.astype(np.float64)
    pca = PCA(n_components=2, svd_solver="full", random_state=seed).fit(samples64)
    coords = pca.transform(samples64)

    # grid normalize
    grid_min = coords.min(axis=0)
    grid_max = coords.max(axis=0)
    side = 1 << p
    denom = grid_max - grid_min
    denom = np.where(denom < 1e-12, 1e-12, denom)
    norm = (coords - grid_min) / denom
    grid_xy = np.clip((norm * side).astype(np.int64), 0, side - 1)

    # Hilbert distance (chunked for memory — 8M rows씩)
    chunk = 8_000_000
    d = np.empty(len(coords), dtype=np.int64)
    for i in range(0, len(coords), chunk):
        sl = slice(i, i + chunk)
        d[sl] = _hilbert_xy_to_d_fallback(grid_xy[sl, 0], grid_xy[sl, 1], p)

    # quantile boundary (n_strata 분할)
    quantiles = np.quantile(d, np.linspace(0, 1, n_strata + 1))
    edges = quantiles[1:-1]  # n_strata - 1 boundary
    sids = np.searchsorted(edges, d, side="right")
    return np.clip(sids, 0, n_strata - 1).astype(np.int32)


# ---- 3. 공식 entry: assign_hilbert_real ----
def assign_hilbert_real(
    all_vecs: np.ndarray,
    n_strata: int = 20,
    hilbert_order: int = 10,
    seed: int = 42,
) -> np.ndarray:
    """진짜 Hilbert curve 기반 stratum_id 부여.

    args:
      all_vecs: (N, dim) — DEEP/SIFT/SSN/Wiki vector. dim >= 2.
      n_strata: 출력 stratum 수 (기본 20, KM20 정렬).
      hilbert_order: 2^p × 2^p grid 의 p (기본 10 → 1024×1024 grid; 80M row 충분).
      seed: PCA random_state (full SVD 면 영향 없지만 결정론).

    returns:
      stratum_ids: (N,) int32, 값 [0, n_strata).

    deterministic: 같은 (all_vecs, n_strata, hilbert_order, seed) → 항상 동일.
    """
    if _RAW_AVAILABLE:
        # raw module 의 fit_hilbert_mapper + assign_hilbert 재사용
        # (samples = all_vecs 자기 자신; 80M 도 chunked PCA transform 처리)
        # 단, 80M 한번에 fit 은 메모리 무리 — 100K subsample 로 fit 후 전체 assign
        rng = np.random.default_rng(seed)
        n = len(all_vecs)
        if n > 100_000:
            sample_idx = rng.choice(n, size=100_000, replace=False)
            sample_vecs = all_vecs[sample_idx]
        else:
            sample_vecs = all_vecs
        mapper = fit_hilbert_mapper(  # noqa: F821
            sample_vecs, n_strata=n_strata, p=hilbert_order, seed=seed
        )
        # chunked assign for memory
        chunk = 8_000_000
        sids = np.empty(n, dtype=np.int32)
        for i in range(0, n, chunk):
            sids[i : i + chunk] = _raw_assign(  # noqa: F821
                mapper, all_vecs[i : i + chunk]
            )
        return sids
    else:
        return _assign_fallback(all_vecs, n_strata, hilbert_order, seed)


# ---- 4. smoke test ----
def _smoke_test():
    """100K rows × 96d 합성 → 진짜 hilbert vs PCA 2D lex sort 분리도 비교."""
    import time

    rng = np.random.default_rng(0)

    # synthetic 100K × 96d, 5 cluster (DEEP-like)
    centers = rng.standard_normal((5, 96)).astype(np.float32) * 8
    sizes = [22000, 18000, 25000, 15000, 20000]
    chunks = []
    for c, s in zip(centers, sizes):
        chunks.append(rng.standard_normal((s, 96)).astype(np.float32) * 0.5 + c)
    vecs = np.vstack(chunks)
    rng.shuffle(vecs)
    print(f"[smoke] synthetic data: shape={vecs.shape}, dtype={vecs.dtype}")
    print(f"[smoke] raw_module_available={_RAW_AVAILABLE}")

    # ---- (a) 진짜 hilbert ----
    t0 = time.time()
    sids_h = assign_hilbert_real(vecs, n_strata=20, hilbert_order=10, seed=42)
    t_h = time.time() - t0
    counts_h = np.bincount(sids_h, minlength=20)
    print(f"\n[smoke A] hilbert_real elapsed={t_h:.2f}s")
    print(f"[smoke A] stratum count min={counts_h.min()} max={counts_h.max()} "
          f"mean={counts_h.mean():.0f} std={counts_h.std():.0f}")
    print(f"[smoke A] counts={counts_h.tolist()}")

    # ---- (b) 기존 ★3 hilbert (PCA 2D lex sort) — measure_paper_exact L446-456 inline ----
    from sklearn.decomposition import PCA
    t0 = time.time()
    pca = PCA(n_components=2, random_state=42)
    pca_v = pca.fit_transform(vecs)
    order = np.argsort(pca_v[:, 0] * 1000 + pca_v[:, 1])
    sids_p = np.zeros(len(vecs), dtype=np.int32)
    chunk_size = (len(vecs) + 20 - 1) // 20
    for i, idx in enumerate(order):
        sids_p[idx] = min(i // chunk_size, 20 - 1)
    t_p = time.time() - t0
    counts_p = np.bincount(sids_p, minlength=20)
    print(f"\n[smoke B] pca2d_lex (기존 ★3) elapsed={t_p:.2f}s")
    print(f"[smoke B] counts min={counts_p.min()} max={counts_p.max()} "
          f"mean={counts_p.mean():.0f} std={counts_p.std():.0f}")
    print(f"[smoke B] counts={counts_p.tolist()}")

    # ---- (c) 분리도: 두 method 의 stratum 부여 일치율 ----
    # 같은 stratum_id 부여 비율 (random baseline = 1/20 = 5%)
    same_sid = (sids_h == sids_p).sum() / len(vecs)
    print(f"\n[smoke C] hilbert vs pca2d_lex same stratum_id: {same_sid:.4f} "
          f"(random baseline 0.05; 1.0 = identical)")

    # ---- (d) intra-cluster 거리 (locality 측정) ----
    # 각 method 의 같은 stratum 안 vec 들의 평균 pairwise 거리 ≈ locality 강도
    # (stratum 1개 sample 으로 측정; 같은 cluster idx 라도 두 method 가 다른 vec 묶음)
    from numpy.linalg import norm
    def avg_intra_dist(sids: np.ndarray, vecs: np.ndarray, k_strata: int = 20,
                       sample_per: int = 200) -> float:
        ds = []
        for s in range(k_strata):
            mask = sids == s
            idx = np.where(mask)[0]
            if len(idx) < 2:
                continue
            picks = rng.choice(idx, size=min(sample_per, len(idx)), replace=False)
            sub = vecs[picks]
            # pairwise distance (200 picks → 19,900 pair, 빠름)
            for i in range(len(sub)):
                for j in range(i + 1, len(sub)):
                    ds.append(norm(sub[i] - sub[j]))
        return float(np.mean(ds)) if ds else float("nan")

    d_h = avg_intra_dist(sids_h, vecs)
    d_p = avg_intra_dist(sids_p, vecs)
    print(f"\n[smoke D] avg intra-stratum L2 distance:")
    print(f"           hilbert_real  = {d_h:.4f}  ← lower = better locality")
    print(f"           pca2d_lex     = {d_p:.4f}")
    print(f"           ratio (h/p)   = {d_h/d_p:.4f}  (1.0 = no diff)")

    # ---- (e) 결정론 ----
    sids_h2 = assign_hilbert_real(vecs, n_strata=20, hilbert_order=10, seed=42)
    assert np.array_equal(sids_h, sids_h2), "hilbert_real not deterministic"
    print(f"\n[smoke E] determinism ✓")

    print(f"\n[smoke] OK")


if __name__ == "__main__":
    _smoke_test()
