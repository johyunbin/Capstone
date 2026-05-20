#!/usr/bin/env python3
"""fig5_5_effect_size_distribution.py — Hedges' g 분포 histogram

phase2 (sel=0.001 핵심) + phase3 (sel=0.01·0.1 carry-over) 의 baseline / B1 anchor 별
|Hedges' g| 분포를 한 figure 에 4 panel 로 시각화.

Cohen's threshold:
- small: |g| < 0.2
- medium: 0.2 ≤ |g| < 0.5
- large: 0.5 ≤ |g| < 0.8
- very large: |g| ≥ 0.8

출력: experiments/figures/보고서_6_11/fig5_5_effect_size_distribution.{png,pdf}
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PHASE2 = ROOT / "_internal/cache/rq3/latency/phase2/figures/paired_stats.csv"
PHASE3 = ROOT / "_internal/cache/rq3/latency/phase3/figures/paired_stats.csv"
OUT_DIR = ROOT / "experiments/figures/보고서_6_11"
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": ["Apple SD Gothic Neo", "Pretendard", "sans-serif"],
    "axes.unicode_minus": False,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
})

NAVY = "#1a2c4e"
ORANGE = "#b85c00"
GREEN = "#10B981"
GRAY = "#94A3B8"

df2 = pd.read_csv(PHASE2)
df3 = pd.read_csv(PHASE3)
df2["abs_g"] = df2["hedges_g"].abs()
df3["abs_g"] = df3["hedges_g"].abs()
df3["sel"] = df3["cell"].str.extract(r"(sel0\.\d+)")[0]

fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), constrained_layout=True)

THRESH = [(0.2, "small"), (0.5, "medium"), (0.8, "large")]


def draw_panel(ax, data, color, label, n, x_max, sub_data=None, sub_colors=None, sub_labels=None):
    n_bins = 30
    bins = np.linspace(0, x_max, n_bins + 1)
    if sub_data is None:
        ax.hist(data.clip(upper=x_max - 1e-6), bins=bins, color=color, alpha=0.82,
                edgecolor="white", linewidth=0.6, label=f"{label} (n={n})")
    else:
        clipped = [s.clip(upper=x_max - 1e-6) for s in sub_data]
        ax.hist(clipped, bins=bins, color=sub_colors, alpha=0.85,
                edgecolor="white", linewidth=0.6,
                label=[f"{lbl} (n={len(s)})" for lbl, s in zip(sub_labels, sub_data)], stacked=True)
    for t, name in THRESH:
        if t <= x_max:
            ax.axvline(t, ls="--", color="#666", lw=0.6, alpha=0.5)
            ax.text(t, ax.get_ylim()[1] * 0.96, name, fontsize=7.5, ha="left", va="top", color="#666")
    ax.set_xlim(0, x_max)
    ax.set_xlabel("|Hedges' g|")
    ax.set_ylabel("count")
    ax.legend(loc="upper right")


# panel 1: phase2 baseline anchor — 극단적 large effect (max 86.5, median 7.6)
ax = axes[0, 0]
g = df2[df2["anchor"] == "baseline"]["abs_g"]
draw_panel(ax, g, NAVY, "baseline anchor", len(g), x_max=25.0)
large_pct = (g >= 0.8).mean() * 100
ax.set_title(f"Phase 2 · 기본 엔진 대비 — large 100% (180/180) · 중앙값 |g|={g.median():.1f}")

# panel 2: phase2 B1 anchor — small effect 다수
ax = axes[0, 1]
g = df2[df2["anchor"] == "B1"]["abs_g"]
draw_panel(ax, g, ORANGE, "B1 anchor", len(g), x_max=2.0)
small_pct = (g < 0.5).mean() * 100
ax.set_title(f"Phase 2 · 베이스라인 대비 — small (|g| < 0.5) {small_pct:.0f}% ({(g < 0.5).sum()}/{len(g)})")

# panel 3: phase3 baseline anchor — sel별 stacked, 양극화 (sel=0.01 large vs sel=0.1 small)
ax = axes[1, 0]
sel001 = df3[(df3["anchor"] == "baseline") & (df3["sel"] == "sel0.01")]["abs_g"]
sel010 = df3[(df3["anchor"] == "baseline") & (df3["sel"] == "sel0.1")]["abs_g"]
draw_panel(ax, None, None, None, None, x_max=6.5,
           sub_data=[sel001, sel010], sub_colors=[NAVY, GRAY],
           sub_labels=["sel=0.01", "sel=0.1"])
g_all = df3[df3["anchor"] == "baseline"]["abs_g"]
ax.set_title(f"Phase 3 · 기본 엔진 대비 (carry-over) — sel=0.01 다수 large, sel=0.1 small")

# panel 4: phase3 B1 anchor — sel별 stacked
ax = axes[1, 1]
sel001 = df3[(df3["anchor"] == "B1") & (df3["sel"] == "sel0.01")]["abs_g"]
sel010 = df3[(df3["anchor"] == "B1") & (df3["sel"] == "sel0.1")]["abs_g"]
draw_panel(ax, None, None, None, None, x_max=4.0,
           sub_data=[sel001, sel010], sub_colors=[ORANGE, "#f0c090"],
           sub_labels=["sel=0.01", "sel=0.1"])
g_all = df3[df3["anchor"] == "B1"]["abs_g"]
small_pct = (g_all < 0.5).mean() * 100
ax.set_title(f"Phase 3 · 베이스라인 대비 (carry-over) — small {small_pct:.0f}% ({(g_all < 0.5).sum()}/{len(g_all)})")

fig.suptitle("그림 5-5. 효과 크기 (|Hedges' g|) 분포 — 기본 엔진 anchor vs 베이스라인 anchor",
             fontsize=12.5, fontweight="bold", y=1.02)

for ext in ["png", "pdf"]:
    out = OUT_DIR / f"fig5_5_effect_size_distribution.{ext}"
    fig.savefig(out, dpi=160, bbox_inches="tight")
    print(f"✓ {out.relative_to(ROOT)}")
