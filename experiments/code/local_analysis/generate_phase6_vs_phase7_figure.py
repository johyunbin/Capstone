#!/usr/bin/env python3
"""Phase 6 vs Phase 7 5-cell DEEP 1M KM20-BERN selectivity gradient figure.

5/27 발표 Slide 4/6 footnote 보강용. master.md line 86-91 의 5-cell 수치를 직접 시각화.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from _matplotlib_korean import enable_korean


def main() -> None:
    enable_korean()

    sels = [0.01, 0.05, 0.10, 0.30, 0.50]
    phase6 = [+8.93, +1.85, -2.06, -3.11, -10.67]
    phase7 = [+3.33, -2.60, -1.31, -0.99, -1.23]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    x = np.arange(len(sels))
    width = 0.35

    bars1 = ax.bar(
        x - width / 2,
        phase6,
        width,
        label="Phase 6 (SQL D, vector.c hook, production-near)",
        color="#1B365D",
        edgecolor="white",
    )
    bars2 = ax.bar(
        x + width / 2,
        phase7,
        width,
        label="Phase 7 (numpy D, simulation)",
        color="#A0A0A0",
        edgecolor="white",
    )

    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        ax.annotate(
            f"{h:+.2f}%",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3 if h > 0 else -12),
            textcoords="offset points",
            ha="center",
            va="bottom" if h > 0 else "top",
            fontsize=9,
        )

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"s={s:g}" for s in sels])
    ax.set_xlabel("Selectivity")
    ax.set_ylabel("KM20 - BERN diff (%)")
    ax.set_title(
        "RQ1 Phase 6 vs Phase 7 — DEEP 1M KM20-BERN Selectivity Gradient (5/7 W2)"
    )
    ax.legend(loc="lower left", framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(-13.5, 13)

    for i, (p6, p7) in enumerate(zip(phase6, phase7)):
        delta = p6 - p7
        ax.annotate(
            f"Δ={delta:+.2f}%p",
            xy=(i, max(p6, p7) + 2.2),
            ha="center",
            fontsize=8,
            color="#B22222",
            fontweight="bold",
        )

    fig.text(
        0.5,
        0.02,
        "per-seed Spearman ρ — Phase 6: -0.680 [-0.800, -0.440] CI 0 제외 (단조 감소 확정) · "
        "Phase 7: +0.240 [-0.061, +0.480] CI 0 포함 (검정력 약화)",
        ha="center",
        fontsize=9,
        style="italic",
    )

    plt.tight_layout(rect=(0, 0.05, 1, 1))

    out_dir = Path(__file__).resolve().parents[2] / "figures" / "rq1_motivation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "phase6_vs_phase7_5sel.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
