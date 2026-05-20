#!/usr/bin/env python3
"""W4 회의용 master figures.
1. 4강 method × dataset heatmap (sel=0.10, paired Δ%)
2. Per-dataset K_optimal sweep (RQ1 K=10/20/50/100/200)
3. 25 method bar chart (sel=0.10, sorted by Δ%)
4. YFCC chairim vs build_yfcc bar comparison"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path("/tmp/w4_figures")
OUT.mkdir(exist_ok=True)
plt.rcParams["font.family"] = ["DejaVu Sans"]


def load():
    return pd.read_csv("/tmp/w4_15cell_summary.csv")


def fig_4kang_heatmap(df):
    sub = df[(df["selectivity"] == 0.10) & (df["method"].isin(["hilbert","hybrid","minibatch_partial","hdbscan"]))]
    pv = sub.pivot_table(index=["dataset","sf"], columns="method", values="paired_pct_vs_bern")
    pv = pv.reindex(columns=["hilbert","hybrid","minibatch_partial","hdbscan"])
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(pv.values, cmap="RdYlGn_r", vmin=-10, vmax=10)
    ax.set_xticks(range(len(pv.columns)))
    ax.set_xticklabels(pv.columns)
    ax.set_yticks(range(len(pv.index)))
    ax.set_yticklabels([f"{a}_sf{b}" for a, b in pv.index])
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            v = pv.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:+.1f}%", ha="center", va="center", fontsize=9)
    plt.colorbar(im, ax=ax, label="paired Δ% vs bern")
    ax.set_title("4-강 method × cell heatmap (sel=0.10)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_4kang_heatmap.png", dpi=150)
    plt.close(fig)
    print(f"saved fig_4kang_heatmap.png")


def fig_k_sweep(df):
    # use rq1_<DS>_sf<sf>_km_k_*.parquet meta — separate plot per dataset
    pass  # TODO: load km_k parquets, plot K_optimal curve


def fig_25_method_bar(df, ds="DEEP", sf=10):
    sub = df[(df["dataset"] == ds) & (df["sf"] == sf) & (df["selectivity"] == 0.10)].sort_values("paired_pct_vs_bern")
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = ["red" if v > 0 else "green" for v in sub["paired_pct_vs_bern"]]
    ax.barh(sub["method"], sub["paired_pct_vs_bern"], color=colors)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xlabel("paired Δ% vs bern (negative = better)")
    ax.set_title(f"{ds}_sf{sf} — all method ranking (sel=0.10)")
    fig.tight_layout()
    fig.savefig(OUT / f"fig_method_rank_{ds}_sf{sf}.png", dpi=150)
    plt.close(fig)
    print(f"saved fig_method_rank_{ds}_sf{sf}.png")


def fig_yfcc_compare(df):
    sub = df[(df["dataset"].isin(["YFCC","YFCC_DL"])) & (df["selectivity"] == 0.10) & (df["sf"] == 10)]
    if len(sub) == 0:
        return
    pv = sub.pivot_table(index="method", columns="dataset", values="paired_pct_vs_bern")
    fig, ax = plt.subplots(figsize=(10, 7))
    pv.plot.bar(ax=ax)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_ylabel("paired Δ% vs bern")
    ax.set_title("YFCC sf10 — chairim vs build_yfcc (sel=0.10)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_yfcc_compare.png", dpi=150)
    plt.close(fig)
    print(f"saved fig_yfcc_compare.png")


def main():
    df = load()
    fig_4kang_heatmap(df)
    for ds in ["DEEP","SIFT","SSN","WIKI","YFCC","YFCC_DL"]:
        for sf in [1,10]:
            try: fig_25_method_bar(df, ds, sf)
            except Exception as e: print(f"WARN {ds}_sf{sf}: {e}")
    fig_yfcc_compare(df)
    print(f"\n[done] figures → {OUT}")


if __name__ == "__main__":
    main()
