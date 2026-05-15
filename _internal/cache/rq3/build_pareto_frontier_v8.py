#!/usr/bin/env python3
"""
build_pareto_frontier_v8.py — Phase 4 Pareto frontier figure (자원 × 정확도)

목적
----
sample selection 영역 56 method 의 (자원 fit_elapsed, paired Δ% 정확도) 산점도 + Pareto
frontier (Convex Hull lower-left) + Top 5 method annotation. 박세은 framing 적용:
"sample selection" 일관 표기.

Pareto Top 5 anchor (resource_efficiency_pareto_20260513.md §3.2 verbatim)
------------------------------------------------------------------------
1. sparse_rp        (P4 DimReduc)  fit 0.1 s + CaseB ~ -9.43%
2. chao_weighted    (P3 Streaming) fit 0.5 s + CaseB ~ -9.60%
3. hilbert_real     (P2 Spatial)   fit 0.5 s + CaseB ~ -9.27%
4. hyperloglog      (P9 Info)      fit 0.5 s + CaseB ~ -8.65%
5. pca1d            (P4 DimReduc)  fit 0.5 s + CaseB ~ -9.63%

input
-----
_internal/cache/rq3/aggregated_v12.parquet (Phase 1, 다른 agent 영역)
fallback: aggregated_v12_dryrun.parquet (691 file 영역)

fit_elapsed source
------------------
raw JSON 영역 fit_elapsed 컬럼 부재. analysis/resource_efficiency_pareto_20260513.md
§2.1 표 영역 verbatim hardcode lookup. 향후 wall-clock 측정 추가 시 parquet
컬럼 promote.

output
------
experiments/figures/paper_exact_v8/F7_pareto_frontier.png   (300 DPI)
experiments/figures/paper_exact_v8/F7_pareto_frontier.pdf
experiments/figures/paper_exact_v8/F7_pareto_frontier_data.csv  (sanity)

usage
-----
  python3 build_pareto_frontier_v8.py             # full parquet
  python3 build_pareto_frontier_v8.py --dry-run   # dryrun parquet (691 file)
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ============================================================
# 경로 + 상수
# ============================================================
REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO_ROOT / "_internal" / "cache" / "rq3"
OUT_DIR = REPO_ROOT / "experiments" / "figures" / "paper_exact_v8"

# Apple SD Gothic Neo 영역 한국어 axis label 영역
KOREAN_FONT = "Apple SD Gothic Neo"
plt.rcParams["font.family"] = KOREAN_FONT
plt.rcParams["axes.unicode_minus"] = False

# Pareto Top 5 anchor (resource_efficiency_pareto_20260513.md §3.2)
PARETO_TOP5 = ["sparse_rp", "chao_weighted", "hilbert_real", "hyperloglog", "pca1d"]

# fit_elapsed lookup (resource_efficiency_pareto_20260513.md §2.1, 단위 sec)
# floor 0.1 s 영역 영역 sub-second 영역 영역 (log scale 영역 0 회피).
FIT_ELAPSED = {
    # P1 Cluster
    "minibatch": 0.5, "minibatch_partial": 0.5, "gmm": 0.8, "coreset": 0.5,
    "kmeans_neyman": 0.5, "hkbu_repsample": 0.5, "banditucb1": 0.5,
    # P2 Spatial
    "hilbert": 0.1, "hilbert_real": 0.5, "skilling_hilbert": 0.5,
    "zorder_morton": 0.1, "idistance": 0.5, "idistance_neyman": 1.0,
    "faiss_ivf": 1.0, "lpm1_proper": 0.5, "epsilon_net": 1.0,
    "lpm2": 0.5,
    # P3 Streaming
    "chao_weighted": 0.5, "thompson_sampling": 0.5, "mfmc": 0.5,
    "cum_sqrtf": 0.5,
    # P4 DimReduction
    "sparse_rp": 0.1, "pca1d": 0.5, "rsvd": 0.5,
    "ica_fastica": 1.0, "neuram": 0.5, "tucker": 1.0,
    "vinecopula": 1.5, "factor_join": 0.5, "lp_bound": 0.5,
    # P5 QMC (대부분 정합성 위반 영역 폐기, 유효 cum_sqrtf/lavallee 만 영역)
    "lavallee_hidiroglou": 0.5, "lp_bound": 0.5,
    # P6 Quantization
    "rabitq_strat": 0.5, "mhist2": 0.5, "wavelet_hist": 0.5,
    "pq": 1.5, "opq": 2.5, "cocluster_nystrom": 1.5,
    # P9 Info
    "hyperloglog": 0.5,
}

# paradigm color (Capstone navy palette + accents)
PARADIGM_COLOR = {
    "P1": "#1f77b4",   # Cluster — blue
    "P2": "#2ca02c",   # Spatial — green
    "P3": "#ff7f0e",   # Streaming — orange
    "P4": "#9467bd",   # DimReduc — purple
    "P5": "#8c564b",   # QMC — brown
    "P6": "#e377c2",   # Quant — pink
    "P9": "#17becf",   # Info — cyan
    "P10": "#bcbd22",  # Density — olive
    "Pother": "#7f7f7f",
}
PARADIGM_LABEL = {
    "P1": "P1 Cluster", "P2": "P2 Spatial", "P3": "P3 Streaming",
    "P4": "P4 DimReduc", "P5": "P5 QMC", "P6": "P6 Quant",
    "P9": "P9 Info", "P10": "P10 Density", "Pother": "Other",
}


# ============================================================
# data loading + paired Δ%
# ============================================================
def load_parquet(dry_run: bool) -> pd.DataFrame:
    name = "aggregated_v12_dryrun.parquet" if dry_run else "aggregated_v12.parquet"
    path = CACHE_DIR / name
    if not path.exists():
        # full 부재 시 dryrun fallback
        fallback = CACHE_DIR / "aggregated_v12_dryrun.parquet"
        if not dry_run and fallback.exists():
            print(f"  warning: {path} 부재 — {fallback.name} fallback.", file=sys.stderr)
            path = fallback
        else:
            raise FileNotFoundError(f"  {path} 부재. aggregate_v12.py 영역 선행 필요.")
    print(f"  loaded {path.name}")
    return pd.read_parquet(path)


def compute_paired_delta(df: pd.DataFrame) -> pd.DataFrame:
    """method × paradigm 단위 mean paired Δ% 산출.

    paired Δ% = (qe_caseB - qe_b1) / qe_b1 * 100  per cell.
    그 후 method 단위 mean across cells.
    """
    # B1 cell-level qe
    b1 = (df[df["mode"] == "B1"][["cell", "qe_trim"]]
          .rename(columns={"qe_trim": "qe_b1"}))
    # CaseB filter: 정책 폐기 영역 + alias 영역 + A4-sel sweep 영역 + non-default sel 영역 제외
    caseb = df[(df["mode"] == "CaseB")
               & (~df["is_alias_dup"])
               & (~df["is_policy_drop"])
               & (df["cell"] != "A4-sel")
               & (df["sel"] == 0.01)
               & (df["K"].isna())
               & (df["alpha"].isna())]
    merged = caseb.merge(b1, on="cell", how="left").dropna(subset=["qe_b1"])
    merged["delta_pct"] = (merged["qe_trim"] - merged["qe_b1"]) / merged["qe_b1"] * 100

    g = (merged.groupby(["sample_selection_method", "paradigm"])
                .agg(mean_delta=("delta_pct", "mean"),
                     n_cells=("cell", "nunique"),
                     std_delta=("delta_pct", "std"))
                .reset_index())
    return g


def attach_fit_elapsed(g: pd.DataFrame) -> pd.DataFrame:
    g = g.copy()
    g["fit_elapsed"] = g["sample_selection_method"].map(FIT_ELAPSED)
    g = g.dropna(subset=["fit_elapsed"])  # FIT_ELAPSED lookup 부재 method 제외
    return g


# ============================================================
# Pareto frontier (lower-left = better: low fit + low Δ%)
# ============================================================
def pareto_frontier(points: np.ndarray) -> np.ndarray:
    """points: (n, 2) of (x, y). lower-left 영역 Pareto frontier indices.

    monotone sort 영역. Convex hull 영역 noise 영역 영역 영역 (n<5).
    """
    if len(points) < 2:
        return np.arange(len(points))
    order = np.argsort(points[:, 0])
    sorted_pts = points[order]
    pareto_mask = np.ones(len(sorted_pts), dtype=bool)
    best_y = np.inf
    for i, (_, y) in enumerate(sorted_pts):
        if y < best_y:
            best_y = y
        else:
            pareto_mask[i] = False
    return order[pareto_mask]


# ============================================================
# plotting
# ============================================================
def make_plot(g: pd.DataFrame, out_png: Path, out_pdf: Path):
    fig, ax = plt.subplots(figsize=(11, 7))

    # marker size: n_cells 영역 영역 (4-9 range). area = 60 + n_cells*30
    sizes = 60 + g["n_cells"].clip(lower=1).to_numpy() * 30

    # color per paradigm
    colors = [PARADIGM_COLOR.get(p, "#7f7f7f") for p in g["paradigm"]]

    # scatter
    ax.scatter(g["fit_elapsed"], g["mean_delta"],
               s=sizes, c=colors, alpha=0.65, edgecolors="black", linewidths=0.6,
               zorder=3)

    # Pareto frontier (lower-left)
    pts = g[["fit_elapsed", "mean_delta"]].to_numpy()
    pareto_idx = pareto_frontier(pts)
    pareto_sorted = sorted(pareto_idx, key=lambda i: pts[i, 0])
    pareto_pts = pts[pareto_sorted]
    ax.plot(pareto_pts[:, 0], pareto_pts[:, 1],
            color="#d62728", linewidth=1.8, linestyle="--",
            label="Pareto frontier", zorder=2, alpha=0.8)

    # Top 5 annotation
    for method in PARETO_TOP5:
        sub = g[g["sample_selection_method"] == method]
        if sub.empty:
            print(f"  warning: Top5 영역 {method} 영역 영역 영역 — annotation skip.", file=sys.stderr)
            continue
        x = float(sub["fit_elapsed"].iloc[0])
        y = float(sub["mean_delta"].iloc[0])
        # 라벨 offset 영역 영역 영역 영역 충돌 방지
        offsets = {
            "sparse_rp":     (12, -8),
            "chao_weighted": (12, 8),
            "hilbert_real":  (-12, -16),
            "hyperloglog":   (12, 16),
            "pca1d":         (-12, 12),
        }
        dx, dy = offsets.get(method, (10, 10))
        ax.annotate(
            method,
            xy=(x, y),
            xytext=(dx, dy), textcoords="offset points",
            fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc="#fffacd", ec="black", lw=0.5, alpha=0.9),
            arrowprops=dict(arrowstyle="-", color="black", lw=0.5),
            zorder=4,
        )

    # axis cosmetics
    ax.set_xscale("log")
    ax.set_xlabel("자원 비용  fit_elapsed (sec, log scale)", fontsize=12, fontfamily=KOREAN_FONT)
    ax.set_ylabel("정확도 개선  paired Δ% = (CaseB - B1) / B1 × 100  (음수 = 개선)",
                  fontsize=12, fontfamily=KOREAN_FONT)
    ax.set_title("Pareto frontier — sample selection 영역 정확도 best = 자원 best",
                 fontsize=13, fontweight="bold", fontfamily=KOREAN_FONT, pad=14)

    # 0% baseline + grid
    ax.axhline(0, color="gray", linewidth=0.6, linestyle=":", alpha=0.7, zorder=1)
    ax.grid(True, which="both", linestyle="-", alpha=0.2, zorder=0)

    # legend (paradigm)
    paradigms_in = sorted(g["paradigm"].unique())
    handles = [plt.scatter([], [], s=120, c=PARADIGM_COLOR.get(p, "#7f7f7f"),
                           edgecolors="black", linewidths=0.6, alpha=0.7,
                           label=PARADIGM_LABEL.get(p, p))
               for p in paradigms_in]
    handles.append(plt.Line2D([0], [0], color="#d62728", linewidth=1.8,
                              linestyle="--", label="Pareto frontier"))
    ax.legend(handles=handles, loc="upper left", fontsize=9, framealpha=0.9, ncol=2)

    # footer note
    fig.text(0.99, 0.01,
             f"data: {len(g)} method x paired CaseB delta% (n_cells=marker size)  |  "
             f"Pareto Top 5 = sparse_rp / chao_weighted / hilbert_real / hyperloglog / pca1d",
             ha="right", fontsize=8, color="#555555", fontfamily=KOREAN_FONT)

    plt.tight_layout(rect=(0, 0.02, 1, 1))

    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_png}")
    print(f"  wrote {out_pdf}")


# ============================================================
# main
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="aggregated_v12_dryrun.parquet (691 file 영역) 영역 영역")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_parquet(args.dry_run)
    g = compute_paired_delta(df)
    g = attach_fit_elapsed(g)

    # sanity
    print(f"\n  scatter point count: {len(g)}")
    print(f"  fit_elapsed range: {g['fit_elapsed'].min():.2f} – {g['fit_elapsed'].max():.2f} s")
    print(f"  mean_delta range: {g['mean_delta'].min():.2f}% – {g['mean_delta'].max():.2f}%")
    missing = [m for m in PARETO_TOP5 if m not in set(g["sample_selection_method"])]
    if missing:
        print(f"  warning: Top 5 영역 영역 영역 method: {missing}", file=sys.stderr)

    suffix = "_dryrun" if args.dry_run else ""
    out_png = OUT_DIR / f"F7_pareto_frontier{suffix}.png"
    out_pdf = OUT_DIR / f"F7_pareto_frontier{suffix}.pdf"
    out_csv = OUT_DIR / f"F7_pareto_frontier{suffix}_data.csv"

    g.sort_values("mean_delta").to_csv(out_csv, index=False)
    print(f"  wrote {out_csv}")

    make_plot(g, out_png, out_pdf)


if __name__ == "__main__":
    main()
