#!/usr/bin/env python3
"""offline CaseC v16 95 tuple — qe_trim figure (cell × sel × K heatmap + Δ% bar).

input: paper_exact_v16_summary_<TS>/v16_full95_paired.parquet (aggregate_offline_casec_v16 산출)

산출 figure:
  · fig1_qe_heatmap_{sel}.{png,pdf} — 3 figure (sel 별), 25 cell × 3 K grid
  · fig2_delta_vs_B1.{png,pdf} — CaseC v16 vs B1 paired Δ% distribution (95 tuple histogram)
  · fig3_qe_by_sf.{png,pdf} — qe_trim by sf (violin/box, 95 tuple)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Apple SD Gothic Neo 우선 — 한글 깨짐 방지 (보고서·발표 공통)
plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "NanumGothic", "AppleGothic",
                                "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def plot_heatmap_per_sel(df: pd.DataFrame, out_dir: Path) -> None:
    """sel 별 heatmap: rows=cell · cols=K · values=qe_trim_CaseC_v16."""
    for sel in sorted(df["sel"].unique()):
        sub = df[df["sel"] == sel]
        pivot = sub.pivot_table(index="cell", columns="K", values="qe_trim_CaseC_v16",
                                aggfunc="mean").sort_index()
        if pivot.empty:
            continue
        fig, ax = plt.subplots(figsize=(5, max(4, 0.32 * len(pivot))))
        im = ax.imshow(pivot.values, aspect="auto", cmap="viridis")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f"K={k}" for k in pivot.columns])
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=8)
        # value 셀 위에 표시
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                v = pivot.values[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                            color="white" if v > pivot.values.mean() else "black",
                            fontsize=7)
        ax.set_title(f"CaseC v16 qe_trim (sel={sel:g}, {len(sub)} tuples)")
        fig.colorbar(im, ax=ax, label="qe_trim")
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(out_dir / f"fig1_qe_heatmap_sel{sel:g}.{ext}", dpi=180,
                        bbox_inches="tight")
        plt.close(fig)
        print(f"  saved fig1_qe_heatmap_sel{sel:g}.{{png,pdf}}")


def plot_delta_vs_b1(df: pd.DataFrame, out_dir: Path) -> None:
    """CaseC v16 vs B1 paired Δ% histogram + summary."""
    if "caseC_vs_B1_pct" not in df.columns:
        print("  [SKIP] caseC_vs_B1_pct missing")
        return
    valid = df["caseC_vs_B1_pct"].dropna()
    if valid.empty:
        print("  [SKIP] no paired Δ%")
        return
    fig, ax = plt.subplots(figsize=(7, 4.5))
    n_better = int((valid < 0).sum())
    n_total = int(len(valid))
    ax.hist(valid, bins=30, color="steelblue", edgecolor="white")
    ax.axvline(0, color="red", lw=1.4, ls="--", label="0% (B1 equal)")
    ax.axvline(valid.median(), color="orange", lw=1.4, ls=":",
                label=f"median {valid.median():+.2f}%")
    ax.set_xlabel("CaseC v16 vs B1 paired Δ% (negative=CaseC better)")
    ax.set_ylabel("paired tuple 수")
    ax.set_title(f"CaseC v16 vs B1 paired Δ% — better {n_better}/{n_total} = "
                 f"{n_better/n_total*100:.1f}%")
    ax.legend()
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig2_delta_vs_B1.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved fig2_delta_vs_B1.{{png,pdf}}")


def plot_qe_by_sf(df: pd.DataFrame, out_dir: Path) -> None:
    """qe_trim by sf — boxplot."""
    fig, ax = plt.subplots(figsize=(6, 4.5))
    sfs = sorted(df["sf"].unique())
    data = [df[df["sf"] == sf]["qe_trim_CaseC_v16"].dropna().values for sf in sfs]
    ax.boxplot(data, labels=[f"sf={s}" for s in sfs], showmeans=True,
                meanprops=dict(marker="D", markerfacecolor="orange",
                               markeredgecolor="orange", markersize=6))
    ax.set_xlabel("scale factor")
    ax.set_ylabel("CaseC v16 qe_trim")
    ax.set_title(f"CaseC v16 qe_trim — sf 별 분포 ({len(df)} tuples)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig3_qe_by_sf.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved fig3_qe_by_sf.{{png,pdf}}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paired-parquet", type=Path, required=True,
                    help="v16_full95_paired.parquet")
    ap.add_argument("--output-dir", type=Path, required=True,
                    help="figure 저장 디렉토리")
    args = ap.parse_args()

    df = pd.read_parquet(args.paired_parquet)
    print(f"loaded {len(df)} v16 CaseC tuples from {args.paired_parquet}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"writing figures to {args.output_dir}")
    plot_heatmap_per_sel(df, args.output_dir)
    plot_delta_vs_b1(df, args.output_dir)
    plot_qe_by_sf(df, args.output_dir)
    print("done.")


if __name__ == "__main__":
    main()
