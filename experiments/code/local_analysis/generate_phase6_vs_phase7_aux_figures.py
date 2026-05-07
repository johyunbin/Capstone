#!/usr/bin/env python3
"""Phase 6 vs Phase 7 보조 figure 2종 — per-seed ρ scatter + 단조성 trend line.

Worker A 의 Slide 4/6 footnote 보강 + 자문 메일 첨부 PDF 의 보조 시각화.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from _matplotlib_korean import enable_korean


SELS = [0.01, 0.05, 0.10, 0.30, 0.50]
PHASE6_DIFF = [+8.93, +1.85, -2.06, -3.11, -10.67]
PHASE7_DIFF = [+3.33, -2.60, -1.31, -0.99, -1.23]

PHASE6_RHO = -0.680
PHASE6_CI = (-0.800, -0.440)
PHASE7_RHO = +0.240
PHASE7_CI = (-0.061, +0.480)

NAVY = "#1B365D"
GRAY = "#A0A0A0"
RED = "#B22222"


def figure_rho(out_path: Path) -> None:
    """per-seed Spearman ρ — Phase 6 vs Phase 7 errorbar."""
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)

    rhos = [PHASE6_RHO, PHASE7_RHO]
    ci_low = [PHASE6_RHO - PHASE6_CI[0], PHASE7_RHO - PHASE7_CI[0]]
    ci_high = [PHASE6_CI[1] - PHASE6_RHO, PHASE7_CI[1] - PHASE7_RHO]
    yerr = np.array([ci_low, ci_high])
    colors = [NAVY, GRAY]
    labels = [
        "Phase 6\n(SQL D, vector.c hook)",
        "Phase 7\n(numpy D, simulation)",
    ]
    x = np.arange(len(rhos))

    for i, (xi, rho, color) in enumerate(zip(x, rhos, colors)):
        ax.errorbar(
            xi,
            rho,
            yerr=[[yerr[0, i]], [yerr[1, i]]],
            fmt="o",
            color=color,
            ecolor=color,
            elinewidth=2.5,
            capsize=8,
            capthick=2,
            markersize=12,
            zorder=3,
        )
        ax.annotate(
            f"ρ={rho:+.3f}\n[{PHASE6_CI[0] if i == 0 else PHASE7_CI[0]:+.3f}, "
            f"{PHASE6_CI[1] if i == 0 else PHASE7_CI[1]:+.3f}]",
            xy=(xi, rho),
            xytext=(15, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=10,
            color=color,
            fontweight="bold",
        )

    ax.axhline(0, color="black", linewidth=1.0, linestyle="--", alpha=0.6, zorder=1)
    ax.text(
        1.45,
        0.02,
        "ρ=0  (단조성 없음)",
        fontsize=8,
        color="black",
        alpha=0.7,
        ha="right",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("per-seed Spearman ρ (mean ± 95% CI)")
    ax.set_title(
        "RQ1 단조성 검정 — Phase 6 ρ CI 0 제외 (확정) vs Phase 7 ρ CI 0 포함 (약화)",
        fontsize=11,
    )
    ax.set_ylim(-1.0, +0.6)
    ax.set_xlim(-0.5, 1.8)
    ax.grid(axis="y", alpha=0.3)

    fig.text(
        0.5,
        0.02,
        "n_seeds=5 · sels=[0.01, 0.05, 0.10, 0.30, 0.50] · DEEP 1M KM20-BERN",
        ha="center",
        fontsize=9,
        style="italic",
    )

    plt.tight_layout(rect=(0, 0.05, 1, 1))
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"saved: {out_path}")


def figure_trend(out_path: Path) -> None:
    """단조성 trend line plot — log(sel) vs KM20-BERN diff (Phase 6 solid / Phase 7 dashed)."""
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    log_sels = np.log10(SELS)

    ax.plot(
        log_sels,
        PHASE6_DIFF,
        marker="o",
        linewidth=2.5,
        markersize=10,
        color=NAVY,
        linestyle="-",
        label="Phase 6 (SQL D, vector.c hook, production-near)",
        zorder=3,
    )
    ax.plot(
        log_sels,
        PHASE7_DIFF,
        marker="s",
        linewidth=2.5,
        markersize=9,
        color=GRAY,
        linestyle="--",
        label="Phase 7 (numpy D, simulation)",
        zorder=2,
    )

    for x_log, y in zip(log_sels, PHASE6_DIFF):
        ax.annotate(
            f"{y:+.2f}%",
            xy=(x_log, y),
            xytext=(0, 8 if y > 0 else -16),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=NAVY,
            fontweight="bold",
        )
    for x_log, y in zip(log_sels, PHASE7_DIFF):
        ax.annotate(
            f"{y:+.2f}%",
            xy=(x_log, y),
            xytext=(0, -16 if y > 0 else 8),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color="#555555",
        )

    ax.axhline(0, color="black", linewidth=0.7)
    ax.set_xticks(log_sels)
    ax.set_xticklabels([f"s={s:g}" for s in SELS])
    ax.set_xlabel("Selectivity (log scale)")
    ax.set_ylabel("KM20 - BERN diff (%)")
    ax.set_title(
        "RQ1 Selectivity Gradient Trend — Phase 6 단조 감소 vs Phase 7 약한 trend",
        fontsize=11,
    )
    ax.legend(loc="lower left", framealpha=0.95)
    ax.grid(alpha=0.3)
    ax.set_ylim(-13, 12)

    arrow_x_start = log_sels[0] + 0.05
    arrow_x_end = log_sels[-1] - 0.05
    ax.annotate(
        "",
        xy=(arrow_x_end, -11.5),
        xytext=(arrow_x_start, -11.5),
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.5),
    )
    ax.text(
        (arrow_x_start + arrow_x_end) / 2,
        -10.7,
        "Phase 6 단조 감소 (ρ=-0.680, CI 0 제외)",
        ha="center",
        fontsize=9,
        color=RED,
        fontweight="bold",
    )

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"saved: {out_path}")


def main() -> None:
    enable_korean()
    out_dir = Path(__file__).resolve().parents[2] / "figures" / "rq1_motivation"
    out_dir.mkdir(parents=True, exist_ok=True)
    figure_rho(out_dir / "phase6_vs_phase7_rho.png")
    figure_trend(out_dir / "phase6_vs_phase7_trend.png")


if __name__ == "__main__":
    main()
