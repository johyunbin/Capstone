#!/usr/bin/env python3
"""
RQ3 보강 시각화 — ARI heatmap, Cohen's d forest plot, per-query difficulty scatter.

기존 rq3_figures.py 와 별개. 본 세션 (5/6 23:00 이후) 보강 분석 산출의 시각화.

산출 (모두 PNG, 5/8 회의 자료 직접 사용):
  - rq3_method_redundancy_ari_heatmap.png        — 10×10 ARI matrix
  - rq3_cohens_d_forest_plot.png                 — method 별 effect size
  - rq3_per_query_difficulty_scatter.png         — query 난이도 vs method spread
  - rq3_per_query_best_method_distribution.png   — best 빈도 stacked bar

PG 무관, 기존 산출 csv/parquet 만 사용.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _matplotlib_korean import enable_korean  # noqa: E402
_chosen = enable_korean()
if _chosen:
    print(f"[font] applied: {_chosen}")

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESULTS = ROOT / "Capstone" / "experiments" / "results" / "rq3_agnostic"
if not RESULTS.exists():
    RESULTS = Path(__file__).resolve().parent.parent.parent / "results" / "rq3_agnostic"

FIG_DIR = RESULTS.parent.parent / "figures" / "rq3_supplementary"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def fig_ari_heatmap():
    """10×10 ARI matrix heatmap (clustered DEEP-like 데이터)."""
    csv = RESULTS / "rq3_method_redundancy_ari_deep_like_clustered_96d.csv"
    if not csv.exists():
        print(f"[skip] {csv.name} 없음")
        return
    df = pd.read_csv(csv, index_col=0)

    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(df.values, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)
    # Annotate cells
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            val = df.values[i, j]
            color = "white" if val < 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    color=color, fontsize=8)
    ax.set_title("RQ3 Method 간 정보 Redundancy (ARI)\n"
                 "DEEP-like clustered synthetic, 5K samples × 50K all_vecs",
                 fontsize=11)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Adjusted Rand Index")
    plt.tight_layout()
    out = FIG_DIR / "rq3_method_redundancy_ari_heatmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def fig_cohens_d_forest():
    """method 별 Cohen's d × dataset × sel forest plot."""
    csv = RESULTS / "rq3_bootstrap_effect_size.csv"
    if not csv.exists():
        print(f"[skip] {csv.name} 없음")
        return
    df = pd.read_csv(csv)

    # method 별 평균 d 와 (min, max) range
    summary = df.groupby("method")["cohens_d"].agg(["mean", "min", "max"]).reset_index()
    # 평균 d 오름차순 (improve 가 위)
    summary = summary.sort_values("mean")

    fig, ax = plt.subplots(figsize=(9, 6))
    y = np.arange(len(summary))
    ax.errorbar(
        summary["mean"], y,
        xerr=[summary["mean"] - summary["min"], summary["max"] - summary["mean"]],
        fmt="o", color="tab:blue", ecolor="gray", capsize=4, markersize=8,
    )
    ax.axvline(0, color="black", linewidth=0.8)
    # 효과 크기 영역 표시
    for thr, lab, color in [(-0.8, "large improve", "lightgreen"),
                             (-0.5, "medium", "lightblue"),
                             (-0.2, "small", "lightyellow"),
                             (0.2, "negligible", "white"),
                             (0.5, "small hurt", "lightyellow"),
                             (0.8, "medium hurt", "lightpink")]:
        pass
    ax.axvspan(-0.2, 0.2, alpha=0.1, color="gray", label="negligible (|d|<0.2)")
    ax.axvspan(-0.5, -0.2, alpha=0.15, color="green", label="small improve")
    ax.axvspan(-0.8, -0.5, alpha=0.2, color="green")
    ax.axvspan(0.2, 0.5, alpha=0.15, color="red", label="small hurt")
    ax.axvspan(0.5, 0.8, alpha=0.2, color="red")

    ax.set_yticks(y)
    ax.set_yticklabels(summary["method"])
    ax.set_xlabel("Cohen's d (paired vs BERN, 음수 = method 가 BERN 보다 q_error 작음)")
    ax.set_title("RQ3 Method Effect Size — Cohen's d Forest Plot\n"
                 "errorbar = (min, max) over (DEEP/SIFT × 5 sel)", fontsize=11)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    out = FIG_DIR / "rq3_cohens_d_forest_plot.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def fig_per_query_difficulty_scatter():
    """query 의 BERN q_error (난이도) vs method spread (best-worst 차이)."""
    csv = RESULTS / "rq3_per_query_ranking.csv"
    if not csv.exists():
        print(f"[skip] {csv.name} 없음")
        return
    df = pd.read_csv(csv)

    # query 별 spread (best-worst) + bern
    spread = df.groupby(["dataset", "selectivity", "query_id"]).agg(
        q_error_min=("q_error", "min"),
        q_error_max=("q_error", "max"),
        bern=("bern_q", "first"),
    ).reset_index()
    spread["spread"] = spread["q_error_max"] - spread["q_error_min"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, ds in zip(axes, ["DEEP", "SIFT"]):
        sub = spread[spread["dataset"] == ds]
        for sel in sorted(sub["selectivity"].unique()):
            ssub = sub[sub["selectivity"] == sel]
            ax.scatter(ssub["bern"], ssub["spread"], alpha=0.4, s=12, label=f"sel={sel}")
        # 대각선 trend
        ax.set_xlabel("BERN q_error (query 난이도)")
        ax.set_ylabel("method spread (best-worst q_error)")
        ax.set_title(f"{ds} — query 난이도 vs method 분산")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.legend(loc="lower right", fontsize=8)
        ax.grid(True, alpha=0.3)
    fig.suptitle("RQ3: 어려운 query 일수록 method 간 차이가 결정적 (Spearman ρ ≈ 0.78)",
                 fontsize=11)
    plt.tight_layout()
    out = FIG_DIR / "rq3_per_query_difficulty_scatter.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def fig_best_method_distribution():
    """best (rank=1) 인 method 의 빈도 stacked bar (dataset × method)."""
    csv = RESULTS / "rq3_per_query_ranking.csv"
    if not csv.exists():
        print(f"[skip] {csv.name} 없음")
        return
    df = pd.read_csv(csv)

    best = df[df["rank"] == 1].groupby(["dataset", "mode"]).size().unstack(fill_value=0)
    best = best.T  # method × dataset
    best["total"] = best.sum(axis=1)
    best = best.sort_values("total", ascending=True).drop(columns="total")

    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(best))
    width = 0.4
    ax.barh(y - width/2, best["DEEP"], width, label="DEEP 1M", color="tab:blue")
    ax.barh(y + width/2, best.get("SIFT", 0), width, label="SIFT 1.5M", color="tab:orange")
    ax.set_yticks(y)
    ax.set_yticklabels(best.index)
    ax.set_xlabel("query × sel × seed cell 중 'best' (rank=1) 빈도")
    ax.set_title("RQ3 Method Best 빈도 (전체 500 cells × 2 dataset)\n"
                 "Hilbert / MiniBatch 가 KM20 oracle 보다 자주 best",
                 fontsize=11)
    ax.legend()
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    out = FIG_DIR / "rq3_per_query_best_method_distribution.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def fig_method_minus_bern_heatmap():
    """method × dataset × sel 의 method_minus_bern_pct heatmap (recovery_summary 기반)."""
    csv = RESULTS / "recovery_summary.csv"
    if not csv.exists():
        print(f"[skip] {csv.name} 없음")
        return
    df = pd.read_csv(csv)

    # pivot: method × (dataset, sel)
    df["dataset_sel"] = df["dataset"] + "_s" + df["sel"].astype(str)
    pivot = df.pivot_table(
        index="method", columns="dataset_sel", values="method_minus_bern_pct",
    )
    # 행 (method) 평균 절대값으로 정렬 (best 위)
    pivot["abs_mean"] = pivot.abs().mean(axis=1)
    pivot = pivot.sort_values("abs_mean").drop(columns="abs_mean")

    fig, ax = plt.subplots(figsize=(11, 5))
    vmax = max(50, np.nanmax(np.abs(pivot.values)))
    vmin = -vmax
    im = ax.imshow(pivot.values, cmap="RdBu_r", vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)
    # cell value annotate
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if pd.isna(val):
                continue
            color = "white" if abs(val) > vmax * 0.5 else "black"
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", color=color, fontsize=7)
    ax.set_title("RQ3 method_minus_bern_pct (음수 = BERN 보다 q_error 작음)",
                 fontsize=11)
    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04, label="% 차이")
    plt.tight_layout()
    out = FIG_DIR / "rq3_method_minus_bern_heatmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[saved] {out}")
    plt.close()


def main():
    print("=" * 70)
    print(f"RQ3 보강 시각화 → {FIG_DIR}")
    print("=" * 70)
    fig_ari_heatmap()
    fig_cohens_d_forest()
    fig_per_query_difficulty_scatter()
    fig_best_method_distribution()
    fig_method_minus_bern_heatmap()
    print("=" * 70)
    print("완료")


if __name__ == "__main__":
    main()
