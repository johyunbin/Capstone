#!/usr/bin/env python3
"""W4 partial figures — 4강 heatmap + per-cell method ranking + dataset distribution effect."""
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

CSV = Path("/Users/hyunbin/Capstone/_internal/_w4_partial_summary.csv")
OUT = Path("/Users/hyunbin/Capstone/experiments/figures/w4_partial")
OUT.mkdir(parents=True, exist_ok=True)
WINNERS = ["hilbert", "hybrid", "minibatch_partial", "hdbscan"]

for f in fm.findSystemFonts():
    if "AppleSDGothicNeo" in f:
        plt.rcParams["font.family"] = fm.FontProperties(fname=f).get_name()
        break

df = pd.read_csv(CSV)
print(f"loaded {len(df)} rows")


def fig_heatmap_4kang(df: pd.DataFrame) -> None:
    sub = df[
        (df["selectivity"] == 0.10)
        & df["method"].isin(WINNERS)
        & df["paired_pct_vs_bern"].notna()
    ]
    pv = (
        sub.pivot_table(
            index=["dataset", "sf"], columns="method", values="paired_pct_vs_bern"
        ).reindex(columns=WINNERS)
    )
    if pv.empty:
        print("no 4강 paired data")
        return
    fig, ax = plt.subplots(figsize=(8, max(4, len(pv) * 0.6)))
    vmin = max(-12, pv.values.min() - 1)
    vmax = min(12, max(pv.values.max() + 1, 5))
    im = ax.imshow(pv.values, cmap="RdYlGn_r", vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(pv.columns)))
    ax.set_xticklabels(pv.columns)
    ax.set_yticks(range(len(pv.index)))
    ax.set_yticklabels([f"{a}_sf{b}" for a, b in pv.index])
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            v = pv.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:+.2f}%", ha="center", va="center", fontsize=10)
    plt.colorbar(im, ax=ax, label="paired Δ% vs bern (lower = better)")
    ax.set_title("4-강 method × cell heatmap (sel=0.10) — W4 partial")
    fig.tight_layout()
    fig.savefig(OUT / "fig_4kang_heatmap_partial.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved fig_4kang_heatmap_partial.png")


def fig_method_rank_per_cell(df: pd.DataFrame) -> None:
    cells = df[df["paired_pct_vs_bern"].notna()][["dataset", "sf"]].drop_duplicates()
    for _, r in cells.iterrows():
        ds, sf = r["dataset"], r["sf"]
        sub = df[
            (df["dataset"] == ds)
            & (df["sf"] == sf)
            & (df["selectivity"] == 0.10)
            & df["paired_pct_vs_bern"].notna()
        ].sort_values("paired_pct_vs_bern")
        if sub.empty:
            continue
        fig, ax = plt.subplots(figsize=(10, max(6, len(sub) * 0.3)))
        colors = ["red" if v > 0 else "green" for v in sub["paired_pct_vs_bern"]]
        ax.barh(sub["method"], sub["paired_pct_vs_bern"], color=colors)
        ax.axvline(0, color="black", linewidth=0.5)
        ax.set_xlabel("paired Δ% vs bern")
        ax.set_title(f"{ds}_sf{sf} — method ranking (sel=0.10)")
        fig.tight_layout()
        fig.savefig(OUT / f"fig_rank_{ds}_sf{sf}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"saved fig_rank_{ds}_sf{sf}.png")


def fig_distribution_effect(df: pd.DataFrame) -> None:
    sub = df[
        df["method"].isin(WINNERS)
        & df["paired_pct_vs_bern"].notna()
        & (df["selectivity"] == 0.10)
    ]
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    pv = sub.pivot_table(
        index=["dataset", "sf"], columns="method", values="paired_pct_vs_bern"
    ).reindex(columns=WINNERS)
    pv.plot.bar(ax=ax, width=0.8)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_ylabel("paired Δ% vs bern (sel=0.10)")
    ax.set_title("Distribution effect — 4-강 method × cell (W4 partial)")
    ax.legend(loc="best", fontsize=9)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(OUT / "fig_distribution_effect.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved fig_distribution_effect.png")


fig_heatmap_4kang(df)
fig_method_rank_per_cell(df)
fig_distribution_effect(df)
print(f"\n[done] figures → {OUT}")
