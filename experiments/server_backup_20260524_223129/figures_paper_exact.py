#!/usr/bin/env python3
"""5/27 발표용 figure 자동 생성 (matplotlib).

5/27 storyline anchor figure 6건:
- F1 paradigm rollup bar (P1-P10 mean Δ%, CaseB 우위 입증)
- F2 Cliff's δ bucket bar (CaseA worsening 36.8% vs CaseB better 63.5%)
- F3 CaseA vs CaseB Δ% violin
- F4 Top winners bar (CaseB Top 5)
- F5 5단계 narrative diagram (B1 → CaseA fail → CaseB climax)
- F6 Effect size scatter (Hedges' g × Cliff's δ)

Usage:
    python3 figures_paper_exact.py --out-dir /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact \
                                   --fig-dir /Users/hyunbin/Capstone/experiments/figures/paper_exact_v7
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 일관 style
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 120, "savefig.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
})

# Color palette (학술 톤, navy/red 분리)
COLOR_BETTER = "#1f4e79"  # navy = CaseB better
COLOR_WORSE = "#a13a3a"   # red = worsening
COLOR_NEUTRAL = "#888888"

# 동일 paradigm map (analyze_paper_exact.py와 일치)
PARADIGM_MAP = {
    "minibatch": "P1", "gmm": "P1", "minibatch_partial": "P1",
    "birch": "P1", "agglomerative": "P1", "coreset": "P1",
    "dbscan": "P1", "kmeans_neyman": "P1",
    "hkbu_repsample": "P1", "banditucb1": "P1", "neurocard_lite": "P1",
    "hilbert": "P2", "hilbert_real": "P2", "skilling_hilbert": "P2",
    "zorder_morton": "P2", "idistance": "P2", "idistance_neyman": "P2",
    "faiss_ivf": "P2", "lpm1_proper": "P2", "epsilon_net": "P2",
    "kdtree": "P2", "kdpp": "P2", "lpm2": "P2",
    "chao_weighted": "P3", "reservoir": "P3",
    "thompson_sampling": "P3", "mfmc": "P3",
    "ams_count_sketch": "P3", "ccsketch": "P3",
    "sparse_rp": "P4", "random_projection": "P4", "pca1d": "P4",
    "rsvd": "P4", "ica_fastica": "P4", "dense_rp": "P4",
    "neuram": "P4", "cca1d": "P4", "tucker": "P4",
    "vinecopula": "P4", "factor_join": "P4", "adaptive_bucket_probing": "P4",
    "lsh": "P5", "sobol": "P5", "halton": "P5", "hammersley": "P5",
    "lhs": "P5", "cum_sqrtf": "P5", "lavallee_hidiroglou": "P5",
    "lp_bound": "P5",
    "rabitq_strat": "P6", "mhist2": "P6", "wavelet_hist": "P6",
    "pq": "P6", "opq": "P6", "cocluster_nystrom": "P6",
    "hyperloglog": "P9", "kde_parzen": "P10",
}

PARADIGM_NAME = {
    "P1": "P1 Cluster", "P2": "P2 Spatial", "P3": "P3 Streaming",
    "P4": "P4 DimReduction", "P5": "P5 QMC/Hashing",
    "P6": "P6 Quantization", "P9": "P9 InfoTheoretic", "P10": "P10 Density",
}


def load_paired_results(out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """B1/CaseA/CaseB JSON load + paired Δ% pre-compute."""
    rows_a, rows_b = [], []
    for b1_path in sorted(out_dir.glob("*_B1.json")):
        cell = b1_path.stem.replace("_B1", "")
        b1_d = json.load(open(b1_path))
        b1_trials = np.array([t["avg_q_error_finite"] for t in b1_d["trial_results"]])
        for ca_path in sorted(out_dir.glob(f"{cell}_CaseA_*.json")):
            ca_d = json.load(open(ca_path))
            ca_trials = np.array([t["avg_q_error_finite"] for t in ca_d["trial_results"]])
            finite = np.isfinite(b1_trials) & np.isfinite(ca_trials)
            if not finite.any():
                continue
            b1f, caf = b1_trials[finite], ca_trials[finite]
            delta = ((caf - b1f) / b1f * 100).mean()
            rows_a.append({"cell": cell, "method": ca_d["method"], "delta_pct_mean": delta})
        for cb_path in sorted(out_dir.glob(f"{cell}_CaseB_*.json")):
            cb_d = json.load(open(cb_path))
            cb_trials = np.array([t["avg_q_error_finite"] for t in cb_d["trial_results"]])
            finite = np.isfinite(b1_trials) & np.isfinite(cb_trials)
            if not finite.any():
                continue
            b1f, cbf = b1_trials[finite], cb_trials[finite]
            delta = ((cbf - b1f) / b1f * 100).mean()
            # Hedges' g + Cliff's δ
            pooled_sd = np.sqrt(((len(b1f)-1)*b1f.var(ddof=1) + (len(cbf)-1)*cbf.var(ddof=1))
                                / (len(b1f)+len(cbf)-2))
            g = ((cbf.mean() - b1f.mean()) / pooled_sd if pooled_sd > 0 else np.nan)
            if not np.isnan(g):
                n = len(b1f) + len(cbf)
                g = g * (1 - 3/(4*n - 9))
            gt = int(np.sum(b1f[:, None] > cbf[None, :]))
            lt = int(np.sum(b1f[:, None] < cbf[None, :]))
            cd = (gt - lt) / (len(b1f) * len(cbf))
            rows_b.append({"cell": cell, "method": cb_d["method"],
                          "delta_pct_mean": delta, "hedges_g": g, "cliffs_delta": cd})
    return pd.DataFrame(rows_a), pd.DataFrame(rows_b)


def fig_paradigm_rollup(df_b, out_path: Path):
    """F1 paradigm rollup bar (CaseB mean Δ% per paradigm)."""
    df = df_b.copy()
    df["paradigm"] = df["method"].map(PARADIGM_MAP).fillna("Pother")
    df = df[df["delta_pct_mean"].abs() < 100]  # outlier filter
    agg = df.groupby("paradigm").agg(mean_d=("delta_pct_mean", "mean"),
                                       n=("method", "nunique")).reset_index()
    agg = agg[agg["paradigm"] != "Pother"].sort_values("mean_d")
    agg["label"] = agg["paradigm"].map(PARADIGM_NAME).fillna(agg["paradigm"])

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [COLOR_BETTER if v < 0 else COLOR_WORSE for v in agg["mean_d"]]
    bars = ax.barh(agg["label"], agg["mean_d"], color=colors, edgecolor="white")
    ax.axvline(0, color="black", linewidth=0.6)
    for bar, v, n in zip(bars, agg["mean_d"], agg["n"]):
        xpos = v + (0.3 if v >= 0 else -0.3)
        ha = "left" if v >= 0 else "right"
        ax.text(xpos, bar.get_y() + bar.get_height()/2, f"{v:+.2f}% (n={n})",
                va="center", ha=ha, fontsize=10)
    ax.set_xlabel("Mean Δ% (CaseB vs B1) — 음수 = CaseB 우위")
    ax.set_title("Fig RQ3.E — Paradigm rollup (CaseB, outlier |Δ%|>100 제외)", pad=10)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  ✓ F1 paradigm rollup → {out_path.name}")


def fig_cliffs_delta_bucket(df_a, df_b, out_path: Path):
    """F2 Cliff's δ bucket bar (CaseA vs CaseB 비교)."""
    # CaseA에는 cliff X. 단순 worsening rate count (delta_pct_mean > 0)
    ca_total = len(df_a)
    ca_worse = int((df_a["delta_pct_mean"] > 5).sum())  # +5% 이상 worsening proxy
    ca_better = int((df_a["delta_pct_mean"] < -5).sum())
    ca_neutral = ca_total - ca_worse - ca_better

    cb = df_b.dropna(subset=["cliffs_delta"])
    cb_total = len(cb)
    cb_large_better = int((cb["cliffs_delta"] >= 0.474).sum())
    cb_med_better = int(((cb["cliffs_delta"] >= 0.33) & (cb["cliffs_delta"] < 0.474)).sum())
    cb_small = int(((cb["cliffs_delta"] > -0.33) & (cb["cliffs_delta"] < 0.33)).sum())
    cb_large_worse = int((cb["cliffs_delta"] <= -0.474).sum())

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # CaseA panel
    cats_a = ["large better\n(Δ% < -5)", "neutral\n(-5≤Δ%≤+5)", "worsening\n(Δ% > +5)"]
    vals_a = [ca_better, ca_neutral, ca_worse]
    colors_a = [COLOR_BETTER, COLOR_NEUTRAL, COLOR_WORSE]
    bars_a = axes[0].bar(cats_a, vals_a, color=colors_a, edgecolor="white")
    for bar, v in zip(bars_a, vals_a):
        axes[0].text(bar.get_x() + bar.get_width()/2, v + 5,
                    f"{v} ({100*v/ca_total:.1f}%)", ha="center", fontsize=10)
    axes[0].set_ylabel("Count")
    axes[0].set_title(f"CaseA (n={ca_total}): 단독 대체 = 무너짐", fontsize=12)
    axes[0].grid(axis="y", alpha=0.3)

    # CaseB panel
    cats_b = ["large better\n(δ ≥ +0.474)", "medium better\n(+0.33 ≤ δ < +0.474)",
              "small / inconclusive", "large worsening\n(δ ≤ -0.474)"]
    vals_b = [cb_large_better, cb_med_better, cb_small, cb_large_worse]
    colors_b = [COLOR_BETTER, "#3a76b0", COLOR_NEUTRAL, COLOR_WORSE]
    bars_b = axes[1].bar(cats_b, vals_b, color=colors_b, edgecolor="white")
    for bar, v in zip(bars_b, vals_b):
        axes[1].text(bar.get_x() + bar.get_width()/2, v + 5,
                    f"{v} ({100*v/cb_total:.1f}%)", ha="center", fontsize=10)
    axes[1].set_title(f"CaseB (n={cb_total}): Cliff's δ — 63.5% large better 🔥", fontsize=12)
    axes[1].grid(axis="y", alpha=0.3)
    fig.suptitle("Fig RQ3.D — Effect size (CaseA vs CaseB, 4.4× anchor)", fontsize=13)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  ✓ F2 Cliff's δ bucket → {out_path.name}")


def fig_violin(df_a, df_b, out_path: Path):
    """F3 CaseA vs CaseB Δ% violin."""
    a_clean = df_a[df_a["delta_pct_mean"].abs() < 50]["delta_pct_mean"]
    b_clean = df_b[df_b["delta_pct_mean"].abs() < 50]["delta_pct_mean"]
    fig, ax = plt.subplots(figsize=(8, 6))
    parts = ax.violinplot([a_clean, b_clean], showmeans=True, showmedians=True)
    for pc, c in zip(parts["bodies"], [COLOR_WORSE, COLOR_BETTER]):
        pc.set_facecolor(c)
        pc.set_alpha(0.6)
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_xticks([1, 2])
    ax.set_xticklabels([f"CaseA (n={len(a_clean)})\n단독 대체",
                         f"CaseB (n={len(b_clean)})\nensemble augment"])
    ax.set_ylabel("Paired Δ% (vs B1) — 음수 = 우위")
    ax.set_title("Fig RQ3.B — CaseA vs CaseB Δ% distribution (outlier |Δ%|>50 제외)")
    ax.text(1, -45, f"mean: {a_clean.mean():+.2f}%", ha="center", fontsize=10)
    ax.text(2, -45, f"mean: {b_clean.mean():+.2f}%", ha="center", fontsize=10,
            fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  ✓ F3 violin → {out_path.name}")


def fig_top_winners(df_b, out_path: Path):
    """F4 Top 5 CaseB winners bar."""
    df = df_b.copy().dropna(subset=["hedges_g"])
    df = df.sort_values("hedges_g").head(10)
    labels = [f"{r['method']}\n@ {r['cell']}" for _, r in df.iterrows()]
    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.barh(range(len(df)), df["delta_pct_mean"], color=COLOR_BETTER, edgecolor="white")
    for i, (bar, g, cd) in enumerate(zip(bars, df["hedges_g"], df["cliffs_delta"])):
        v = bar.get_width()
        ax.text(v - 0.3, bar.get_y() + bar.get_height()/2,
                f"Δ%={v:+.2f} | g={g:+.2f} | δ={cd:+.2f}",
                va="center", ha="right", color="white", fontsize=9, fontweight="bold")
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_xlabel("Paired Δ% (CaseB vs B1) — 음수 = CaseB 우위")
    ax.set_title("Fig RQ3.C — Top 10 CaseB winners (smallest Hedges' g)")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  ✓ F4 top winners → {out_path.name}")


def fig_effect_size_scatter(df_b, out_path: Path):
    """F5 Hedges' g × Cliff's δ scatter (effect size 일관성)."""
    df = df_b.dropna(subset=["hedges_g", "cliffs_delta"])
    fig, ax = plt.subplots(figsize=(8, 7))
    sc = ax.scatter(df["hedges_g"], df["cliffs_delta"],
                     c=df["delta_pct_mean"], cmap="RdBu_r", vmin=-15, vmax=15,
                     s=30, alpha=0.7, edgecolors="white", linewidths=0.5)
    ax.axhline(0.474, color="green", linestyle="--", alpha=0.5, label="δ=+0.474 (large better)")
    ax.axhline(-0.474, color="red", linestyle="--", alpha=0.5, label="δ=-0.474 (large worsening)")
    ax.axvline(-0.8, color="green", linestyle=":", alpha=0.5, label="g=-0.8 (large better)")
    ax.axvline(0.8, color="red", linestyle=":", alpha=0.5)
    ax.set_xlabel("Hedges' g (음수=CaseB 우위)")
    ax.set_ylabel("Cliff's δ (양수=CaseB 우위)")
    ax.set_title("Fig RQ3.F — Effect size 일관성 (CaseB, n={})".format(len(df)))
    ax.legend(loc="upper right", fontsize=9)
    cbar = plt.colorbar(sc, ax=ax, label="Δ% (mean)")
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  ✓ F5 effect size scatter → {out_path.name}")


def fig_narrative_diagram(out_path: Path):
    """F6 5단계 narrative diagram (B1 → CaseA fail → CaseB climax)."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (1, 3, 1.8, 1.5, "B1 baseline\n(paper §V-B Bernoulli)\n1.6180\n-4.26% paper 일치", "#4a7ab8"),
        (4, 3, 1.8, 1.5, "CaseA (단독 대체)\n0/437 통계 무효\nCliff's δ worsening 36.8%", COLOR_WORSE),
        (7, 3, 1.8, 1.5, "CaseB (ensemble augment)\n201/447 (45.0%)\n**Cliff's δ better 63.5%**", COLOR_BETTER),
    ]
    for (x, y, w, h, txt, c) in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=c, alpha=0.85,
                                     edgecolor="black", linewidth=1.5))
        ax.text(x + w/2, y + h/2, txt, ha="center", va="center",
                color="white", fontsize=10, fontweight="bold")
    # arrows
    ax.annotate("", xy=(4, 3.75), xytext=(2.8, 3.75),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
    ax.text(3.4, 4.0, "단독 대체\n(실패)", ha="center", fontsize=9, color=COLOR_WORSE, fontweight="bold")
    ax.annotate("", xy=(7, 3.75), xytext=(5.8, 3.75),
                arrowprops=dict(arrowstyle="->", color="black", lw=2.5))
    ax.text(6.4, 4.0, "ensemble\n(climax 4.4×)", ha="center", fontsize=9,
            color=COLOR_BETTER, fontweight="bold")
    ax.text(5, 5.5, "본 연구 5단계 narrative — CaseB ensemble augment가 main contribution",
            ha="center", fontsize=12, fontweight="bold")
    ax.text(5, 1.5, "paper §V-B Bernoulli sample budget 공유 + 우리 method estimate 산술 평균 = bias-variance trade-off",
            ha="center", fontsize=10, style="italic", color="#444")
    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"  ✓ F6 narrative diagram → {out_path.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path,
                    default=Path("/tmp/paper_exact_v7"))  # default: REPORT v7 base
    ap.add_argument("--fig-dir", type=Path,
                    default=Path("/Users/hyunbin/Capstone/experiments/figures/paper_exact_v7"))
    args = ap.parse_args()

    args.fig_dir.mkdir(parents=True, exist_ok=True)

    print(f"[figures_paper_exact] loading {args.out_dir}...")
    df_a, df_b = load_paired_results(args.out_dir)
    print(f"  CaseA paired: {len(df_a)} / CaseB paired: {len(df_b)}")

    print(f"\n[figures_paper_exact] generating figures → {args.fig_dir}/")
    fig_paradigm_rollup(df_b, args.fig_dir / "F1_paradigm_rollup_caseB.png")
    fig_cliffs_delta_bucket(df_a, df_b, args.fig_dir / "F2_cliffs_delta_bucket.png")
    fig_violin(df_a, df_b, args.fig_dir / "F3_caseA_vs_caseB_violin.png")
    fig_top_winners(df_b, args.fig_dir / "F4_top_winners_caseB.png")
    fig_effect_size_scatter(df_b, args.fig_dir / "F5_effect_size_scatter.png")
    fig_narrative_diagram(args.fig_dir / "F6_narrative_diagram.png")
    print(f"\n✓ All 6 figures saved → {args.fig_dir}/")


if __name__ == "__main__":
    main()
