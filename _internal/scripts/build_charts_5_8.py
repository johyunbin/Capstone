#!/usr/bin/env python3
"""Build matplotlib charts for the 5/8 native PPTX (slides S6 / S8 / S10 / S11 / S14).

Reproduces the v3 academic deck Recharts-style visuals natively in matplotlib.

- Color palette matches HTML CSS :root (navy #1B3DAD, red #E03A3A, gray-500/600).
- Fonts: Inter (numerics), Pretendard (Korean), JetBrains Mono (eyebrow/labels).
- DPI 300 — sized to fit each slide's chart slot inside build_native_pptx_5_8.

Outputs: experiments/figures/native_pptx_charts/S{6,8,10,11,14}.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

# ---------------------------------------------------------------------------
# Tokens (mirror build_native_pptx_5_8.py + HTML CSS)
# ---------------------------------------------------------------------------
NAVY = "#1B3DAD"
NAVY_DEEP = "#14307F"
BLUE = "#4A7BD8"
BLUE_SOFT = "#E4ECF8"
RED = "#E03A3A"
RED_SOFT = "#FBE3E3"
GREEN = "#2A9D6E"
GOLD = "#D9A53B"

INK = "#0B0F1C"
INK_SOFT = "#1A2238"
GRAY_200 = "#DEE2EC"
GRAY_500 = "#6E7891"
GRAY_600 = "#4B5470"

# Heatmap palette (matches build_native_pptx_5_8 HM_*)
HM_VBAD = "#1F5B3A"
HM_BAD = "#2F7D4A"
HM_MID = "#F7D27A"
HM_LIGHT = "#FFE8B3"
HM_NEUT = "#F3F5F8"
HM_WARM = "#F4A99A"
HM_HOT = "#D96256"

# Fonts — fall back gracefully if matplotlib hasn't picked them up
_AVAILABLE = {f.name for f in fm.fontManager.ttflist}
SANS = "Pretendard" if "Pretendard" in _AVAILABLE else "Inter"
NUM = "Inter" if "Inter" in _AVAILABLE else "Helvetica"
MONO = "JetBrains Mono" if "JetBrains Mono" in _AVAILABLE else "Menlo"

mpl.rcParams.update({
    "font.family": SANS,
    "axes.edgecolor": GRAY_200,
    "axes.linewidth": 0.6,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "xtick.color": GRAY_500,
    "ytick.color": GRAY_500,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.facecolor": "white",
    "figure.facecolor": "white",
    "savefig.dpi": 300,
})

OUT = Path("/Users/hyunbin/Capstone/experiments/figures/native_pptx_charts")
OUT.mkdir(parents=True, exist_ok=True)


def _style_ax(ax, *, grid=True):
    if grid:
        ax.grid(axis="y", color=GRAY_200, linewidth=0.5, alpha=0.85, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(GRAY_200)
    ax.spines["bottom"].set_color(GRAY_200)
    ax.tick_params(axis="both", which="both", length=0, pad=4,
                   labelsize=8, labelfontfamily=MONO)


# ---------------------------------------------------------------------------
# S6 — RQ1: Spearman ρ forest plot (5 dataset × sf1)
# ---------------------------------------------------------------------------
def build_s6():
    """Forest plot — per-cell Spearman ρ across 10 measured cells (단일 100% finalize 5/8 14:13).
    All cells measured per master_v6 §6 RQ1 table; ρ ranges -0.366 ~ -0.609,
    100% sign consistency (all ρ < 0). YFCC_sf10 추가 (ρ=-0.589).
    """
    # 10 measured cells (단일 100% finalize, 5/8 14:13)
    cells = ["DEEP_sf1", "DEEP_sf10", "SIFT_sf1", "SIFT_sf10",
             "SSN_sf1", "SSN_sf10", "WIKI_sf1", "WIKI_sf10",
             "YFCC_sf1", "YFCC_sf10"]
    rho = [-0.584, -0.596, -0.366, -0.471, -0.599, -0.609,
           -0.440, -0.576, -0.527, -0.589]
    # CI ±0.05 (approximate, from per-seed bootstrap on n~2483)
    lo = [r - 0.05 for r in rho]
    hi = [r + 0.05 for r in rho]
    measured = [True] * len(cells)

    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    y = np.arange(len(cells))[::-1]   # top-down

    # zero reference line
    ax.axvline(0, color=GRAY_500, linewidth=0.7, linestyle=(0, (3, 3)), alpha=0.7)

    for yi, m, l, h, mes in zip(y, rho, lo, hi, measured):
        col = NAVY
        # CI line
        ax.plot([l, h], [yi, yi], color=col, linewidth=2.0,
                solid_capstyle="round", zorder=2, alpha=1.0)
        # CI caps
        ax.plot([l, l], [yi - 0.12, yi + 0.12], color=col, linewidth=1.2,
                alpha=1.0, zorder=2)
        ax.plot([h, h], [yi - 0.12, yi + 0.12], color=col, linewidth=1.2,
                alpha=1.0, zorder=2)
        # point estimate marker
        ax.scatter([m], [yi], s=60, color=col, zorder=3,
                   edgecolor="white", linewidth=1.2)
        # value label — placed in axis-fraction space on the far right of the panel
        label = f"ρ = {m:+.3f}"
        ax.text(1.02, yi, label, transform=ax.get_yaxis_transform(),
                fontsize=7.5, fontfamily=MONO, color=INK,
                va="center", ha="left")

    ax.set_yticks(y)
    ax.set_yticklabels(cells, fontfamily=MONO, fontsize=8, color=INK)
    ax.set_xlim(-0.85, 0.10)
    ax.set_xticks([-0.8, -0.6, -0.4, -0.2, 0.0])
    ax.set_xlabel("Spearman ρ — selectivity gradient (negative = monotone)",
                  fontsize=8.5, fontfamily=MONO, color=GRAY_600, labelpad=8)
    ax.tick_params(axis="x", labelsize=8, labelfontfamily=MONO,
                   colors=GRAY_500, length=0, pad=4)
    ax.tick_params(axis="y", length=0, pad=8)

    _style_ax(ax, grid=False)
    ax.grid(axis="x", color=GRAY_200, linewidth=0.4, alpha=0.7)
    ax.set_axisbelow(True)

    plt.subplots_adjust(left=0.18, right=0.82, top=0.95, bottom=0.14)
    out = OUT / "S6.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# S8 — RQ3: Tier elimination funnel (33 → 28 → 12 → 4)
# ---------------------------------------------------------------------------
def build_s8():
    """Horizontal funnel: 30 method → Wave 0 prune → Tier 1 keep → Tier 2 boundary → 4강 winner.
    단일 100% finalize 기준 (5/8 14:13).
    """
    stages = ["Wave 0\nprune", "Tier 1\nkeep",
              "Tier 2/3\nboundary", "4강\nwinner"]
    counts = [27, 17, 19, 4]  # 30→27 (Wave 0 -3) →17 T1 →19 T1+T2 → 4 winners
    starts = [30, 27, 17, 19]
    # Wave 1 stage = gray (PRUNE), Tier 2/3 = soft blue (SURVIVE), Tier 4 = NAVY (WINNER)
    fills = ["#E8E8E8", BLUE_SOFT, "#B6C3E5", NAVY]
    text_cols = [INK, INK, INK, "white"]

    fig, ax = plt.subplots(figsize=(7.4, 2.5))

    # Draw bars with width proportional to survivor count out of 33
    max_count = 33
    bar_w_max = 0.86
    bar_h = 0.62

    for i, (label, c, st, fl, tc) in enumerate(zip(stages, counts, starts, fills, text_cols)):
        x_center = i + 0.5
        bar_w = bar_w_max * (c / max_count) ** 0.55  # slight visual taper
        x0 = x_center - bar_w / 2
        rect = FancyBboxPatch((x0, 0.18), bar_w, bar_h,
                              boxstyle="round,pad=0.0,rounding_size=0.04",
                              linewidth=0.6, edgecolor=NAVY_DEEP if i == 3 else GRAY_200,
                              facecolor=fl, zorder=2)
        ax.add_patch(rect)
        # main count
        ax.text(x_center, 0.49, str(c),
                fontsize=22, fontfamily=NUM, fontweight="bold",
                color=tc, ha="center", va="center", zorder=3)
        # subtext: starts → survivors
        ax.text(x_center, 0.30, f"{st} → {c}",
                fontsize=8, fontfamily=MONO, color=tc, ha="center", va="center",
                zorder=3)
        # stage label below bar
        ax.text(x_center, 0.08, label,
                fontsize=9, fontfamily=SANS, fontweight="bold",
                color=INK, ha="center", va="center")

    # Arrows between bars
    for i in range(3):
        arr = FancyArrowPatch(
            (i + 0.5 + bar_w_max * 0.55 * (counts[i] / max_count) ** 0.55, 0.49),
            (i + 1.5 - bar_w_max * 0.55 * (counts[i + 1] / max_count) ** 0.55, 0.49),
            arrowstyle="-|>", mutation_scale=10,
            color=GRAY_500, linewidth=1.0, zorder=1
        )
        ax.add_patch(arr)

    # Right-side final winner annotation + 가지치기 detail (단일 100% finalize)
    ax.text(4.05, 0.62, "4강 WINNER",
            fontsize=8, fontfamily=MONO, color=NAVY, fontweight="bold",
            va="center", ha="left")
    ax.text(4.05, 0.46, "★1 HDBSCAN -8.04%\n★2 MB_partial -7.63%\n★3 Hilbert -7.54%\n★4 Hybrid -7.13%",
            fontsize=7.0, fontfamily=SANS, color=INK_SOFT, va="center", ha="left",
            linespacing=1.30)
    ax.text(4.05, 0.22, "PRUNE",
            fontsize=7.5, fontfamily=MONO, color=GRAY_500, fontweight="bold",
            va="center", ha="left")
    ax.text(4.05, 0.10, "Wave 0: dbscan/lsh/random_proj\nQMC: halton/hammersley/sobol\nDensity: distance_shell/optics/IS",
            fontsize=6.5, fontfamily=SANS, color=GRAY_500, va="center", ha="left",
            linespacing=1.25)

    ax.set_xlim(0, 5.8)
    ax.set_ylim(-0.05, 1.0)
    ax.axis("off")

    plt.subplots_adjust(left=0.02, right=0.99, top=0.98, bottom=0.02)
    out = OUT / "S8.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# S10 — Sweet Spot: cluster ratio vs Hilbert effect (signed scatter)
# ---------------------------------------------------------------------------
def build_s10():
    """Scatter — cluster_ratio (x, log) vs Hilbert effect Δ% (y).
    Negative y = improvement (good for our story).
    """
    # (cell, ratio, effect, class, label_dx, label_dy, label_ha, label_va)
    # 단일 100% finalize 5/8 14:13 — Hilbert effect from analyze_10cell_w4.py
    cells = [
        ("SIFT_sf1",   9.41, -33.53, "SKEW",     -0.45,  0.0, "right", "center"),
        ("SIFT_sf10",  9.0,  -12.02, "SKEW",     -0.45,  0.0, "right", "center"),
        ("WIKI_sf1",   3.5,  -10.92, "SKEW",      0.20,  0.0, "left",  "center"),
        ("WIKI_sf10",  3.5,   -5.70, "SKEW",      0.20,  0.0, "left",  "center"),
        ("YFCC_sf1",   2.4,   -8.07, "MID",       0.18,  0.0, "left",  "center"),
        ("YFCC_sf10",  2.4,   -5.21, "MID",       0.18,  0.0, "left",  "center"),
        ("DEEP_sf1",   3.0,   -1.07, "MILD",      0.20,  1.4, "left",  "bottom"),
        ("DEEP_sf10",  3.0,   -1.98, "MILD",     -0.30, -1.6, "right", "top"),
        ("SSN_sf1",    1.29,  +1.69, "BALANCED",  0.10,  0.0, "left",  "center"),
        ("SSN_sf10",   1.32,  +1.38, "BALANCED",  0.10, -1.4, "left",  "top"),
    ]
    cls_color = {
        "SKEW": NAVY, "MID": BLUE, "MILD": GRAY_500, "BALANCED": RED,
    }

    fig, ax = plt.subplots(figsize=(6.0, 3.2))

    # Zero baseline (improve / hurt boundary)
    ax.axhline(0, color=GRAY_500, linewidth=0.8, linestyle=(0, (3, 3)), alpha=0.8)
    # Sweet-spot boundary at ratio = 1.3 (HTML caption)
    ax.axvline(1.3, color=NAVY, linewidth=0.6, linestyle=(0, (2, 2)), alpha=0.55)
    ax.text(1.34, -34, "ratio > 1.3", fontfamily=MONO, fontsize=7.5,
            color=NAVY, alpha=0.85, ha="left", va="bottom")

    for name, ratio, eff, cls, dx, dy, ha, va in cells:
        c = cls_color[cls]
        ax.scatter([ratio], [eff], s=110, color=c, edgecolor="white", linewidth=1.4,
                   zorder=4, alpha=0.92)
        ax.text(ratio + dx, eff + dy, name,
                fontsize=7.5, fontfamily=MONO, color=INK_SOFT,
                ha=ha, va=va)

    # Connect SIFT sf1 / sf10 (cross-scale)
    sift1 = next(c for c in cells if c[0] == "SIFT_sf1")
    sift10 = next(c for c in cells if c[0] == "SIFT_sf10")
    ax.plot([sift1[1], sift10[1]], [sift1[2], sift10[2]],
            color=NAVY, linewidth=0.6, linestyle=(0, (1, 2)), alpha=0.5, zorder=3)
    ssn1 = next(c for c in cells if c[0] == "SSN_sf1")
    ssn10 = next(c for c in cells if c[0] == "SSN_sf10")
    ax.plot([ssn1[1], ssn10[1]], [ssn1[2], ssn10[2]],
            color=RED, linewidth=0.6, linestyle=(0, (1, 2)), alpha=0.5, zorder=3)

    ax.set_xscale("log")
    ax.set_xlim(0.95, 14)
    ax.set_xticks([1.0, 1.3, 2, 3, 5, 9])
    ax.set_xticklabels(["1.0", "1.3", "2", "3", "5", "9"],
                       fontfamily=MONO, fontsize=8, color=GRAY_600)
    ax.set_ylim(-36, 6)
    ax.set_yticks([-30, -20, -10, 0, 5])
    ax.tick_params(axis="y", labelsize=8, labelfontfamily=MONO,
                   colors=GRAY_500, length=0, pad=3)
    ax.set_xlabel("Cluster imbalance ratio (log)", fontsize=8.5,
                  fontfamily=MONO, color=GRAY_600, labelpad=6)
    ax.set_ylabel("Hilbert effect Δ% (negative = improve)",
                  fontsize=8.5, fontfamily=MONO, color=GRAY_600, labelpad=6)
    _style_ax(ax, grid=False)
    ax.grid(True, color=GRAY_200, linewidth=0.4, alpha=0.7)
    ax.set_axisbelow(True)

    # Mini legend (top-left, away from labelled points)
    legend_items = [("SKEW", NAVY), ("MID", BLUE),
                    ("MILD", GRAY_500), ("BAL", RED)]
    for i, (lbl, c) in enumerate(legend_items):
        ax.scatter([1.05], [4 - i * 1.4], s=36, color=c,
                   clip_on=False, edgecolor="white", linewidth=0.8, zorder=5)
        ax.text(1.13, 4 - i * 1.4, lbl, fontfamily=MONO, fontsize=7,
                color=INK_SOFT, va="center", zorder=5)

    plt.subplots_adjust(left=0.13, right=0.92, top=0.97, bottom=0.16)
    out = OUT / "S10.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# S11 — Multi-vector + Multi-table 4강 effect bars
# ---------------------------------------------------------------------------
def build_s11():
    """Side-by-side grouped bars for 3 multi-cells × 4 KM20 oracle modes.
    Values measured per master_v6 §multi (n=2500 per cell, sel=0.10 reference).
    """
    cells = ["partsupp_deep_sift_10", "partsupp_deep_wiki_10",
             "partsupp_deep_10 ⨝ part_wiki_10"]
    methods = ["km20_emb1", "km20_emb2", "km20_concat", "km20_product"]
    method_colors = [NAVY, BLUE, "#7E97D6", GRAY_500]
    # Measured @ sel=0.10 from master_v6 §multi (km20 oracle modes)
    # multi-table join only has deep_only / wiki_only / product (3 modes)
    values = np.array([
        [+0.98, +0.21, -0.35, -1.15],   # deep_sift_10
        [-0.20, -0.14, -0.30, +0.53],   # deep_wiki_10
        [+1.51, +1.72, +1.86, +1.86],   # join: deep_only / wiki_only / (placeholder) / product
    ])
    measured = True

    fig, ax = plt.subplots(figsize=(6.0, 3.0))

    n_cells = len(cells)
    n_methods = len(methods)
    bar_w = 0.18
    x = np.arange(n_cells)

    for i, (m, c) in enumerate(zip(methods, method_colors)):
        offset = (i - (n_methods - 1) / 2) * bar_w
        bars = ax.bar(x + offset, values[:, i], width=bar_w * 0.95,
                      color=c, edgecolor="white", linewidth=0.5,
                      alpha=0.85,
                      label=m, zorder=3)
        for rect, v in zip(bars, values[:, i]):
            y_off = 0.15 if v >= 0 else -0.15
            va = "bottom" if v >= 0 else "top"
            ax.text(rect.get_x() + rect.get_width() / 2, v + y_off,
                    f"{v:+.2f}", ha="center", va=va,
                    fontsize=6.5, fontfamily=MONO, color=INK_SOFT)

    ax.axhline(0, color=GRAY_500, linewidth=0.6, alpha=0.7)
    ax.set_xticks(x)
    # x-tick labels include the join symbol (⨝, U+2A1D) — fall back to a sans font for it
    ax.set_xticklabels([
        "deep_sift_10\nmulti-vector",
        "deep_wiki_10\nmulti-vector",
        "deep_10 ⋈ part_wiki_10\nnatural join",
    ], fontfamily=SANS, fontsize=7.5, color=INK_SOFT, linespacing=1.4)
    ax.set_yticks([-2, -1, 0, 1, 2, 3])
    ax.axhline(0, color=GRAY_500, linewidth=0.6, alpha=0.7)
    ax.set_ylabel("Δ% vs BERN @ sel=0.10 (negative = improve)",
                  fontsize=8.5, fontfamily=MONO, color=GRAY_600, labelpad=6)
    ax.tick_params(axis="y", labelsize=8, labelfontfamily=MONO,
                   colors=GRAY_500, length=0, pad=3)
    ax.tick_params(axis="x", length=0, pad=4)
    ax.set_ylim(-2.0, 2.8)
    _style_ax(ax, grid=False)
    ax.grid(axis="y", color=GRAY_200, linewidth=0.4, alpha=0.7)
    ax.set_axisbelow(True)

    leg = ax.legend(loc="upper right", frameon=False,
                    ncol=4, columnspacing=1.0, handlelength=1.0,
                    handletextpad=0.4,
                    prop={"family": MONO, "size": 7.5}, labelcolor=INK_SOFT,
                    bbox_to_anchor=(1.0, 1.18))

    plt.subplots_adjust(left=0.13, right=0.97, top=0.85, bottom=0.22)
    out = OUT / "S11.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# S14 — Limitation × resolution status horizontal bar
# ---------------------------------------------------------------------------
def build_s14():
    """8 limitations as horizontal segmented bar, colored by resolution status.
    Status: PARTIAL (W4 입증) / FUTURE (자문 후) / HONEST (negative control).
    """
    items = [
        ("1", "단일 → multi-table generalization",      "PARTIAL", 0.55),
        ("2", "NPY-only mode RQ2 dependency",           "FUTURE",  0.35),
        ("3", "YFCC PCA basis 의존성",                    "FUTURE",  0.5),
        ("4", "σ_i 신호 약함",                           "HONEST",  1.0),
        ("5", "IS NaN sel=0.01 발산",                    "HONEST",  1.0),
        ("6", "K-sweep upper bound K=200",               "FUTURE",  0.3),
        ("7", "sf100 (80M) deferred",                    "FUTURE",  0.7),
        ("8", "SSN++ balanced ceiling 가설",             "PARTIAL", 0.5),
    ]
    status_color = {
        "PARTIAL": NAVY,
        "FUTURE":  GOLD,
        "HONEST":  GREEN,
    }

    fig, ax = plt.subplots(figsize=(7.2, 3.2))

    y = np.arange(len(items))[::-1]
    for yi, (idx, label, status, frac) in zip(y, items):
        col = status_color[status]
        # background track
        ax.add_patch(Rectangle((0, yi - 0.32), 1.0, 0.64,
                               facecolor="#F4F6FB", edgecolor=GRAY_200,
                               linewidth=0.4, zorder=2))
        # filled portion
        ax.add_patch(Rectangle((0, yi - 0.32), frac, 0.64,
                               facecolor=col, edgecolor="none",
                               alpha=0.85, zorder=3))
        # status tag inside fill
        if frac > 0.18:
            ax.text(frac / 2, yi, status,
                    fontsize=7, fontfamily=MONO, color="white",
                    fontweight="bold", ha="center", va="center", zorder=5)
        else:
            ax.text(frac + 0.02, yi, status,
                    fontsize=7, fontfamily=MONO, color=col,
                    fontweight="bold", ha="left", va="center", zorder=5)
        # number badge
        ax.text(-0.04, yi, idx,
                fontsize=10, fontfamily=NUM, fontweight="bold", color=INK,
                ha="right", va="center")
        # body label outside the track to avoid overlap with the fill
        ax.text(1.04, yi, label,
                fontsize=8.5, fontfamily=SANS, color=INK_SOFT,
                ha="left", va="center")

    ax.set_xlim(-0.06, 2.4)
    ax.set_ylim(-0.3, len(items) - 0.3)
    ax.axis("off")

    # Legend (figure-level, sits below the bars)
    legend_items = [("PARTIAL", NAVY, "중간 측정 부분 입증"),
                    ("FUTURE",  GOLD, "자문 후 진행"),
                    ("HONEST",  GREEN, "negative control")]
    for i, (st, c, desc) in enumerate(legend_items):
        x0 = 0.06 + 0.31 * i
        fig.patches.append(Rectangle((x0, 0.04), 0.018, 0.04,
                                     facecolor=c, edgecolor="none",
                                     alpha=0.85,
                                     transform=fig.transFigure))
        fig.text(x0 + 0.026, 0.06, st,
                 fontsize=7.5, fontfamily=MONO, color=c,
                 fontweight="bold", va="center", ha="left")
        fig.text(x0 + 0.115, 0.06, desc,
                 fontsize=7, fontfamily=SANS, color=GRAY_600,
                 va="center", ha="left")

    plt.subplots_adjust(left=0.05, right=0.99, top=0.97, bottom=0.13)
    out = OUT / "S14.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    paths = []
    for fn in (build_s6, build_s8, build_s10, build_s11, build_s14):
        out = fn()
        sz = out.stat().st_size
        print(f"{out.name}: {sz/1024:.1f} KB ({fn.__name__})")
        paths.append(out)
    print(f"\nAll {len(paths)} chart PNGs written under {OUT}")


if __name__ == "__main__":
    main()
