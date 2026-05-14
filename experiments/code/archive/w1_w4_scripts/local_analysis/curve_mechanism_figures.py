#!/usr/bin/env python3
"""
Curve mechanism 시각화 — Hilbert vs Z-order 의 1D path 직접 그려서 locality 차이 직관.

5/8 회의에서 \"왜 Hilbert 가 contribution 1순위인가\" 의 시각적 답변.
synthetic 32×32 grid (p=5) 의 Hilbert / Z-order curve path 를 plot.

산출:
  - curve_path_comparison.png       — 두 curve path 나란히
  - curve_neighbor_jump_histogram.png — neighbor jump 분포
  - curve_stratum_partition.png     — 20 stratum 분할 결과 (PCA 2D 좌표)
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _matplotlib_korean import enable_korean  # noqa: E402
_chosen = enable_korean()
if _chosen:
    print(f"[font] applied: {_chosen}")

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ3 = ROOT / "Capstone" / "experiments" / "code" / "rq3"
if not RQ3.exists():
    RQ3 = Path(__file__).resolve().parent.parent / "rq3"
sys.path.insert(0, str(RQ3))

from hilbert.hilbert_curve import hilbert_xy_to_d, fit_hilbert_mapper, assign_hilbert  # noqa: E402
from zorder.zorder_curve import zorder_xy_to_d, fit_zorder_mapper, assign_zorder  # noqa: E402

FIG_DIR = ROOT / "Capstone" / "experiments" / "figures" / "rq3_supplementary"
if not FIG_DIR.parent.exists():
    FIG_DIR = Path(__file__).resolve().parent.parent.parent / "figures" / "rq3_supplementary"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def plot_curve_paths(p: int = 5):
    """32×32 grid 위에 Hilbert vs Z-order path 그리기."""
    n = 1 << p
    xs, ys = np.meshgrid(np.arange(n), np.arange(n), indexing='xy')
    xs, ys = xs.flatten(), ys.flatten()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    for ax, name, fn in [(axes[0], "Hilbert", hilbert_xy_to_d),
                          (axes[1], "Z-order", zorder_xy_to_d)]:
        d = fn(xs, ys, p)
        order = np.argsort(d)
        path_x = xs[order]
        path_y = ys[order]

        # path 그리기 (segment 색을 d 값으로)
        ax.plot(path_x, path_y, '-', color='lightgray', linewidth=0.5, alpha=0.5)
        # consecutive Manhattan distance 계산
        manhattan = np.abs(np.diff(path_x)) + np.abs(np.diff(path_y))
        # large jump 만 빨간색으로 강조
        for i in range(len(path_x) - 1):
            if manhattan[i] > 1:
                ax.plot([path_x[i], path_x[i+1]], [path_y[i], path_y[i+1]],
                        'r-', linewidth=1.5, alpha=0.8)
            else:
                ax.plot([path_x[i], path_x[i+1]], [path_y[i], path_y[i+1]],
                        'b-', linewidth=0.6, alpha=0.5)

        ax.scatter(path_x, path_y, c=d, cmap='viridis', s=8, zorder=3)
        ax.set_title(f"{name} curve (p={p}, {n}×{n} grid)\n"
                     f"red = Manhattan jump > 1 (locality break)")
        ax.set_aspect('equal')
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(-0.5, n - 0.5)
        ax.invert_yaxis()
        # frac > 1 표시
        frac = (manhattan > 1).mean()
        ax.text(0.02, 0.98, f"jump > 1 ratio: {frac:.3f}",
                transform=ax.transAxes, va='top', fontsize=10,
                bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))

    fig.suptitle("Space-Filling Curve Locality Comparison\n"
                 "Hilbert: 1D 인접 → 2D 항상 Manhattan=1 (perfect). "
                 "Z-order: 50% pairs 가 Manhattan>1 ('Z' jump)",
                 fontsize=11)
    plt.tight_layout()
    out = FIG_DIR / "curve_path_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def plot_neighbor_jump_histogram(p: int = 8):
    """4-neighbor jump 분포 + 1D 인접 Manhattan 분포 비교."""
    n = 1 << p
    xs, ys = np.meshgrid(np.arange(n), np.arange(n), indexing='xy')
    xs, ys = xs.flatten(), ys.flatten()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # forward: 4-neighbor 1D distance jump
    for name, fn, color in [("Hilbert", hilbert_xy_to_d, "tab:blue"),
                              ("Z-order", zorder_xy_to_d, "tab:orange")]:
        d = fn(xs, ys, p).reshape(n, n)
        diffs_r = np.abs(d[:, 1:] - d[:, :-1]).flatten()
        diffs_b = np.abs(d[1:, :] - d[:-1, :]).flatten()
        diffs = np.concatenate([diffs_r, diffs_b])
        # log scale histogram
        axes[0].hist(diffs, bins=80, alpha=0.5, label=f"{name} (mean={diffs.mean():.0f})",
                     color=color, log=True)
    axes[0].set_xlabel("|d_a - d_b| (4-neighbor 1D distance jump)")
    axes[0].set_ylabel("count (log)")
    axes[0].set_title(f"Forward locality (2D 인접 → 1D 거리), p={p}")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # inverse: 1D 인접 Manhattan
    for name, fn, color in [("Hilbert", hilbert_xy_to_d, "tab:blue"),
                              ("Z-order", zorder_xy_to_d, "tab:orange")]:
        d = fn(xs, ys, p)
        order = np.argsort(d)
        manhattan = np.abs(np.diff(xs[order])) + np.abs(np.diff(ys[order]))
        # bar plot — Hilbert 는 모두 1, Z-order 는 다양
        unique, counts = np.unique(manhattan, return_counts=True)
        offset = -0.2 if name == "Hilbert" else 0.2
        axes[1].bar(unique + offset, counts, width=0.4, label=f"{name}",
                    color=color, alpha=0.7, log=True)
    axes[1].set_xlabel("Manhattan distance (1D 인접 → 2D)")
    axes[1].set_ylabel("count (log)")
    axes[1].set_title(f"Inverse locality — Hilbert 의 본질 정의")
    axes[1].set_xlim(0.5, 50)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    fig.suptitle("Hilbert vs Z-order Locality 정량 비교 (p=8, 256×256 grid)",
                 fontsize=11)
    plt.tight_layout()
    out = FIG_DIR / "curve_neighbor_jump_histogram.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def plot_stratum_partition():
    """동일 PCA 2D 데이터 위에 Hilbert / Z-order 의 20 stratum 영역 시각화."""
    rng = np.random.default_rng(42)
    # clustered 5-Gaussian (학습 sample 5K)
    centers = rng.standard_normal((5, 2)).astype(np.float32) * 5
    samples = np.vstack([
        rng.standard_normal((1000, 2)).astype(np.float32) + c for c in centers
    ])
    rng.shuffle(samples)

    # all_vecs: 동일 분포 50K
    all_vecs = np.vstack([
        rng.standard_normal((10000, 2)).astype(np.float32) + c for c in centers
    ])
    rng.shuffle(all_vecs)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        h_mapper = fit_hilbert_mapper(samples, n_strata=20, p=10, seed=42)
        z_mapper = fit_zorder_mapper(samples, n_strata=20, p=10, seed=42)
        h_sids = assign_hilbert(h_mapper, all_vecs)
        z_sids = assign_zorder(z_mapper, all_vecs)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, sids, name in [(axes[0], h_sids, "Hilbert"), (axes[1], z_sids, "Z-order")]:
        # 20 색
        scatter = ax.scatter(all_vecs[:, 0], all_vecs[:, 1], c=sids, cmap="tab20",
                              s=2, alpha=0.5)
        ax.set_title(f"{name} — 20 stratum 영역 (clustered 5-Gaussian)")
        ax.set_xlabel("PC 1")
        ax.set_ylabel("PC 2")
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

    fig.suptitle("동일 데이터 + 동일 PCA / quantile 골격, distance function 만 다름",
                 fontsize=11)
    plt.tight_layout()
    out = FIG_DIR / "curve_stratum_partition.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def main():
    print("=" * 70)
    print(f"Curve mechanism 시각화 → {FIG_DIR}")
    print("=" * 70)
    plot_curve_paths(p=5)
    plot_neighbor_jump_histogram(p=8)
    plot_stratum_partition()
    print("완료")


if __name__ == "__main__":
    main()
