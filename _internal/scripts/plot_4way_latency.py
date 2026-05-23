#!/usr/bin/env python3
"""4-way latency 측정 결과 figure 생성 — 5/24 Phase 5 시각화.

aggregate_4way_latency.py 산출 cell_summary.parquet 을 input 으로 받아
matplotlib figure 2 종 생성:
  fig1_paired_delta.png — variant 별 cell-level paired Δ% vs B1 (boxplot + scatter)
  fig2_variant_latency.png — variant 별 trim latency 분포 (boxplot)

폰트: Apple SD Gothic Neo / NanumGothic / DejaVu Sans (한글 보호).

사용:
    python3 plot_4way_latency.py \\
        --summary phase2_4way_summary/cell_summary.parquet \\
        --output-dir experiments/figures/4way_latency/
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "NanumGothic",
                                "AppleGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def plot_paired_delta(summary: pd.DataFrame, output_dir: Path) -> None:
    """variant 별 cell-level paired Δ% vs B1 boxplot."""
    ref = summary[summary.variant == "B1/-"].set_index("cell")["exec_ms_trim"]
    rows = []
    for variant, g in summary.groupby("variant"):
        if variant in ("B1/-", "baseline/-"):
            continue  # skip ref + baseline (큰 outlier)
        gi = g.set_index("cell")
        common = ref.index.intersection(gi.index)
        if len(common) < 2:
            continue
        deltas = (gi.loc[common, "exec_ms_trim"] - ref.loc[common]) / ref.loc[common] * 100
        for cell, d in deltas.items():
            rows.append({"variant": variant, "cell": cell, "delta_pct": d})
    df = pd.DataFrame(rows)
    if df.empty:
        print("no data for paired delta plot")
        return

    # group 정렬: CaseC < CaseA < CaseB × 13 < oracle
    variant_order = sorted(df.variant.unique(),
                           key=lambda v: (0 if v.startswith("CaseC") else
                                          1 if v.startswith("CaseA") else
                                          2 if v.startswith("CaseB") else 3,
                                          v))
    fig, ax = plt.subplots(figsize=(11, 6))
    bp_data = [df[df.variant == v].delta_pct.values for v in variant_order]
    bp = ax.boxplot(bp_data, labels=variant_order, vert=True, patch_artist=True,
                    showfliers=False)
    colors = []
    for v in variant_order:
        if v.startswith("CaseC"):
            colors.append("#10B981")     # 통제군 green
        elif v.startswith("CaseA"):
            colors.append("#EF4444")     # 음성 대조 red
        elif v.startswith("CaseB"):
            colors.append("#3B82F6")     # 결합 blue
        else:
            colors.append("#F97316")     # oracle orange
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    # scatter overlay
    for i, v in enumerate(variant_order):
        d = df[df.variant == v].delta_pct.values
        x = np.full(len(d), i + 1) + np.random.uniform(-0.1, 0.1, len(d))
        ax.scatter(x, d, alpha=0.5, s=20, color="black")
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.axhline(-2, color="red", linestyle=":", linewidth=0.5, label="|Δ%| = 2% 동등 한계")
    ax.axhline(2, color="red", linestyle=":", linewidth=0.5)
    ax.set_ylabel("paired Δ% vs B1 (베이스라인)")
    ax.set_title("4-way latency paired Δ% 분포 — 동등 한계 ±2% 안 모든 inject variant")
    plt.xticks(rotation=45, ha="right")
    plt.legend(loc="upper left", fontsize=8)
    plt.tight_layout()
    out_png = output_dir / "fig1_paired_delta.png"
    out_pdf = output_dir / "fig1_paired_delta.pdf"
    plt.savefig(out_png, dpi=150)
    plt.savefig(out_pdf)
    plt.close()
    print(f"saved {out_png} + .pdf")


def plot_variant_latency(summary: pd.DataFrame, output_dir: Path) -> None:
    """variant 별 trim latency boxplot (baseline 제외 — 큰 outlier)."""
    s = summary[summary.variant != "baseline/-"].copy()
    variant_order = sorted(s.variant.unique(),
                           key=lambda v: (0 if v == "B1/-" else
                                          1 if v.startswith("CaseC") else
                                          2 if v.startswith("CaseA") else
                                          3 if v.startswith("CaseB") else 4,
                                          v))
    fig, ax = plt.subplots(figsize=(11, 6))
    bp_data = [s[s.variant == v].exec_ms_trim.dropna().values for v in variant_order]
    ax.boxplot(bp_data, labels=variant_order, vert=True, showfliers=True)
    ax.set_ylabel("trim latency (ms)")
    ax.set_title("4-way variant 별 trim latency 분포 (baseline 제외)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_png = output_dir / "fig2_variant_latency.png"
    out_pdf = output_dir / "fig2_variant_latency.pdf"
    plt.savefig(out_png, dpi=150)
    plt.savefig(out_pdf)
    plt.close()
    print(f"saved {out_png} + .pdf")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, required=True,
                    help="aggregate_4way_latency.py 산출 cell_summary.parquet")
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    summary = pd.read_parquet(args.summary)
    print(f"loaded {len(summary)} variant rows")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_paired_delta(summary, args.output_dir)
    plot_variant_latency(summary, args.output_dir)


if __name__ == "__main__":
    main()
