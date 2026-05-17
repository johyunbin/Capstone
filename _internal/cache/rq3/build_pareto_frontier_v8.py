#!/usr/bin/env python3
"""
build_pareto_frontier_v8.py — Phase 4 Pareto frontier figure (자원 × 정확도)

목적
----
sample selection 16 method 의 (자원, 정확도) 산점도 + Pareto frontier
(lower-left = better) + Pareto Top 5 annotation. 박세은 framing 적용:
"sample selection" 일관 표기.

자원 축 정의 (실측)
------------------
X축 = final_size (CaseB 모드에서 실제 소비한 sample budget 평균).
AdaptiveState Eq 1-6 momentum 수렴이 빠른 method 일수록 적은 표본으로
종료 → final_size 작음 = 자원 효율 높음. raw JSON 의 size_median /
final_size 컬럼에서 직접 집계 (hardcode 아님).

  주: 초기 설계의 fit_elapsed (wall-clock) 컬럼은 측정 portfolio 에 없음.
  대신 측정된 final_size 를 자원 proxy 로 사용 — 적은 표본 = 적은 거리
  계산 = 적은 비용. 두 지표 모두 "budget" 성격이라 해석 일관.

정확도 축 정의 (실측)
--------------------
Y축 = paired Δ% = (CaseB - B1) / B1 × 100, method 단위 mean across cells.
음수 = sample selection 이 random Bernoulli 대비 Q-error 개선.
paired_delta_v12.parquet 의 delta_pct_mean 컬럼 직접 사용.

Pareto Top 5 anchor (resource_efficiency_pareto §3.2)
-----------------------------------------------------
sparse_rp / chao_weighted / hilbert_real / hyperloglog / pca1d

input
-----
_internal/cache/rq3/aggregated_v12_full.parquet   (final_size 자원 축)
_internal/cache/rq3/paired_delta_v12.parquet      (delta_pct_mean 정확도 축)
fallback: aggregated_v12_dryrun.parquet (--dry-run)

output
------
experiments/figures/paper_exact_v8/F7_pareto_frontier.png   (300 DPI)
experiments/figures/paper_exact_v8/F7_pareto_frontier.pdf
experiments/figures/paper_exact_v8/F7_pareto_frontier_data.csv

usage
-----
  python3 build_pareto_frontier_v8.py             # full parquet
  python3 build_pareto_frontier_v8.py --dry-run   # dryrun parquet
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ============================================================
# 경로 + 상수
# ============================================================
REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO_ROOT / "_internal" / "cache" / "rq3"
OUT_DIR = REPO_ROOT / "experiments" / "figures" / "paper_exact_v8"

# Apple SD Gothic Neo — 한국어 axis label
KOREAN_FONT = "Apple SD Gothic Neo"
plt.rcParams["font.family"] = KOREAN_FONT
plt.rcParams["axes.unicode_minus"] = False

# Pareto Top 5 anchor (resource_efficiency_pareto §3.2)
PARETO_TOP5 = ["sparse_rp", "chao_weighted", "hilbert_real", "hyperloglog", "pca1d"]

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
}
PARADIGM_LABEL = {
    "P1": "P1 Cluster", "P2": "P2 Spatial", "P3": "P3 Streaming",
    "P4": "P4 DimReduc", "P5": "P5 QMC", "P6": "P6 Quant",
    "P9": "P9 Info", "P10": "P10 Density",
}


# ============================================================
# data loading
# ============================================================
def _resolve(primary: str, dry_run: bool) -> Path:
    """primary parquet 우선, --dry-run 또는 부재 시 dryrun fallback."""
    dry = CACHE_DIR / "aggregated_v12_dryrun.parquet"
    if dry_run:
        if not dry.exists():
            raise FileNotFoundError(f"  {dry} 부재.")
        return dry
    path = CACHE_DIR / primary
    if not path.exists():
        if dry.exists():
            print(f"  warning: {path.name} 부재 — {dry.name} fallback.", file=sys.stderr)
            return dry
        raise FileNotFoundError(f"  {path} 부재. aggregate_v12.py 선행 필요.")
    return path


def load_inputs(dry_run: bool):
    """aggregated (final_size) + paired_delta (delta_pct_mean) 로드."""
    agg_path = _resolve("aggregated_v12_full.parquet", dry_run)
    agg = pd.read_parquet(agg_path)
    print(f"  loaded {agg_path.name}  ({len(agg)} rows)")

    pd_path = CACHE_DIR / "paired_delta_v12.parquet"
    if not pd_path.exists():
        raise FileNotFoundError(f"  {pd_path} 부재. paired_delta_v12.py 선행 필요.")
    delta = pd.read_parquet(pd_path)
    print(f"  loaded {pd_path.name}  ({len(delta)} rows)")
    return agg, delta


# ============================================================
# 정확도 축 — method 단위 mean paired Δ%
# ============================================================
def compute_accuracy(delta: pd.DataFrame) -> pd.DataFrame:
    """paired_delta 에서 method × paradigm 단위 mean Δ% 집계.

    K_norm=20 (default K) + exact pairing 한정 — sel sweep 3 값 모두 포함.
    delta_pct_mean = (CaseB - B1) / B1 × 100, 음수 = 개선.
    """
    d = delta[(delta["K_norm"] == 20) & (delta["pairing"] == "exact")].copy()
    g = (d.groupby(["method", "paradigm"])
          .agg(mean_delta=("delta_pct_mean", "mean"),
               std_delta=("delta_pct_mean", "std"),
               n_obs=("delta_pct_mean", "size"),
               n_cells=("cell", "nunique"),
               better=("delta_pct_mean", lambda x: int((x < 0).sum())))
          .reset_index())
    g["better_rate"] = g["better"] / g["n_obs"] * 100.0
    return g


# ============================================================
# 자원 축 — method 단위 mean final_size
# ============================================================
def compute_resource(agg: pd.DataFrame) -> pd.DataFrame:
    """aggregated 에서 method 단위 mean final_size 집계.

    CaseB 모드 한정 (실험군 = sample selection + ensemble). final_size 는
    AdaptiveState 종료 시점 실제 소비 표본 수 — 작을수록 자원 효율 높음.
    """
    cb = agg[(agg["mode"] == "CaseB") & agg["final_size"].notna()]
    r = (cb.groupby("method")
          .agg(mean_size=("final_size", "mean"),
               size_n=("final_size", "size"))
          .reset_index())
    return r


# ============================================================
# Pareto frontier — lower-left (low resource + low Δ%) = better
# ============================================================
def pareto_frontier(points: np.ndarray) -> np.ndarray:
    """points (n, 2) of (x, y). lower-left Pareto frontier indices.

    x 오름차순 정렬 후 y 가 갱신될 때만 frontier. monotone — 작은 n robust.
    """
    if len(points) < 2:
        return np.arange(len(points))
    order = np.argsort(points[:, 0])
    sorted_pts = points[order]
    mask = np.ones(len(sorted_pts), dtype=bool)
    best_y = np.inf
    for i, (_, y) in enumerate(sorted_pts):
        if y < best_y - 1e-9:
            best_y = y
        else:
            mask[i] = False
    return order[mask]


# ============================================================
# plotting
# ============================================================
def make_plot(g: pd.DataFrame, out_png: Path, out_pdf: Path):
    fig, ax = plt.subplots(figsize=(11, 7))

    # marker size: n_cells 비례 (4-25 cells)
    sizes = 70 + g["n_cells"].clip(lower=1).to_numpy() * 18
    colors = [PARADIGM_COLOR.get(p, "#7f7f7f") for p in g["paradigm"]]

    ax.scatter(g["mean_size"], g["mean_delta"],
               s=sizes, c=colors, alpha=0.70, edgecolors="black",
               linewidths=0.7, zorder=3)

    # Pareto frontier (lower-left)
    pts = g[["mean_size", "mean_delta"]].to_numpy()
    pareto_idx = pareto_frontier(pts)
    pareto_sorted = sorted(pareto_idx, key=lambda i: pts[i, 0])
    pareto_pts = pts[pareto_sorted]
    ax.plot(pareto_pts[:, 0], pareto_pts[:, 1],
            color="#d62728", linewidth=1.9, linestyle="--",
            label="Pareto frontier", zorder=2, alpha=0.85, marker="o",
            markersize=5, markerfacecolor="white", markeredgecolor="#d62728")

    # 모든 method 라벨 (작게) — Top 5 는 강조 박스
    offsets = {
        "sparse_rp":     (-14, -16),
        "chao_weighted": (12, 9),
        "hilbert_real":  (10, -16),
        "hyperloglog":   (12, 10),
        "pca1d":         (-16, 12),
    }
    for _, row in g.iterrows():
        m = row["method"]
        x, y = float(row["mean_size"]), float(row["mean_delta"])
        if m in PARETO_TOP5:
            dx, dy = offsets.get(m, (10, 10))
            ax.annotate(
                m, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="#fffacd",
                          ec="#d62728", lw=1.0, alpha=0.95),
                arrowprops=dict(arrowstyle="-", color="#d62728", lw=0.7),
                zorder=5)
        else:
            ax.annotate(m, xy=(x, y), xytext=(7, -3),
                        textcoords="offset points", fontsize=7.5,
                        color="#444444", zorder=4)

    # axis cosmetics
    ax.set_xlabel("자원 비용  —  소비 표본 수 final_size (CaseB 평균, 작을수록 효율적)",
                  fontsize=12, fontfamily=KOREAN_FONT)
    ax.set_ylabel("정확도 개선  —  paired Δ% = (CaseB - B1) / B1 × 100  (음수 = 개선)",
                  fontsize=12, fontfamily=KOREAN_FONT)
    ax.set_title("Pareto frontier — sample selection 의 자원 대비 정확도",
                 fontsize=13, fontweight="bold", fontfamily=KOREAN_FONT, pad=14)

    ax.axhline(0, color="gray", linewidth=0.7, linestyle=":", alpha=0.7, zorder=1)
    ax.grid(True, linestyle="-", alpha=0.22, zorder=0)

    # legend (paradigm + frontier)
    paradigms_in = sorted(g["paradigm"].unique())
    handles = [plt.scatter([], [], s=120, c=PARADIGM_COLOR.get(p, "#7f7f7f"),
                           edgecolors="black", linewidths=0.7, alpha=0.75,
                           label=PARADIGM_LABEL.get(p, p))
               for p in paradigms_in]
    handles.append(plt.Line2D([0], [0], color="#d62728", linewidth=1.9,
                              linestyle="--", marker="o", markersize=5,
                              markerfacecolor="white",
                              label="Pareto frontier"))
    ax.legend(handles=handles, loc="upper right", fontsize=9,
              framealpha=0.92, ncol=2)

    fig.text(0.99, 0.01,
             f"data: {len(g)} method × (final_size 자원, paired CaseB Δ% 정확도)  |  "
             f"marker 크기 = 측정 cell 수  |  "
             f"Pareto Top 5 = sparse_rp · chao_weighted · hilbert_real · "
             f"hyperloglog · pca1d",
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
                    help="aggregated_v12_dryrun.parquet 사용")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    agg, delta = load_inputs(args.dry_run)
    acc = compute_accuracy(delta)
    res = compute_resource(agg)

    g = acc.merge(res, on="method", how="inner")
    if g.empty:
        raise RuntimeError("  accuracy × resource 병합 결과 0 행 — method 키 불일치 확인.")
    g = g.sort_values("mean_delta")

    # sanity
    print(f"\n  scatter point count: {len(g)} method")
    print(f"  final_size range: {g['mean_size'].min():.1f} – "
          f"{g['mean_size'].max():.1f} (표본 수)")
    print(f"  mean_delta range: {g['mean_delta'].min():.2f}% – "
          f"{g['mean_delta'].max():.2f}%")
    missing = [m for m in PARETO_TOP5 if m not in set(g["method"])]
    if missing:
        print(f"  warning: Pareto Top 5 누락 method: {missing}", file=sys.stderr)
    else:
        print(f"  Pareto Top 5 전원 포함 ✓")

    suffix = "_dryrun" if args.dry_run else ""
    out_png = OUT_DIR / f"F7_pareto_frontier{suffix}.png"
    out_pdf = OUT_DIR / f"F7_pareto_frontier{suffix}.pdf"
    out_csv = OUT_DIR / f"F7_pareto_frontier{suffix}_data.csv"

    g.to_csv(out_csv, index=False)
    print(f"  wrote {out_csv}")

    make_plot(g, out_png, out_pdf)


if __name__ == "__main__":
    main()
