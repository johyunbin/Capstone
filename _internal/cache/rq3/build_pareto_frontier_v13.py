#!/usr/bin/env python3
"""
build_pareto_frontier_v13.py — F7 자원·정확도 Pareto frontier (v13 3-way 데이터)

목적
----
sample selection 16 method 의 (자원, 정확도) 산점도 + Pareto frontier
(lower-left = better) + frontier 구성 method annotation. build_pareto_frontier_v8.py
(v12 데이터) 의 v13 재생성 버전.

v8(v12) 대비 변경점
-------------------
1. 입력을 v13 3-way matched parquet 로 교체 (aggregated_v13_full / paired_delta_v13).
2. 정확도 축은 paired_delta_v13 의 comparison == "CaseB_vs_B1" 행만 사용
   (v12 의 K_norm·pairing 컬럼은 v13 에 없음 — 3-way 는 measurement 자체가 matched).
   K=10/20/30 전체 포함 — v13 은 K=10 B1 결함이 해소되어(자체 1단계 B1)
   v13_summary §4.4 와 동일하게 전 K 집계한다.
3. 자원 축을 2종으로 생성:
   - finalsize : CaseB 소비 표본 수 final_size (v12 F7 과 동일 proxy)
   - fittime   : 측정별 fit_time_sec — 분포 파악(stratification fit) 실측 소요 시간.
                 v13 aggregated 에 새로 기록된 컬럼. "분포 파악 비용 × 정확도" 의
                 직접 Pareto.
4. frontier annotation 은 hardcode 가 아니라 실제 계산된 frontier 구성 method
   (v12 의 PARETO_TOP5 상수는 v13 데이터에서 stale — 제거).

정확도 축 정의 (실측)
--------------------
Y축 = paired Δ% = (CaseB - B1) / B1 × 100, method 단위 mean across measurement.
음수 = 결합 실험군(CaseB) 이 random Bernoulli(B1) 대비 Q-error 개선.
paired_delta_v13.parquet 의 delta_pct_mean 컬럼 직접 사용.

자원 축 정의 (실측)
------------------
finalsize : aggregated_v13 mode==CaseB 의 final_size 평균. AdaptiveState Eq 1-6
            momentum 수렴이 빠를수록 적은 표본 → 작을수록 효율적.
fittime   : aggregated_v13 의 fit_time_sec 평균 (측정당 1값 — B1/CaseA/CaseB 3 row
            에 동일 기록되므로 json_id dedup 후 집계). 작을수록 효율적.

input
-----
_internal/cache/rq3/aggregated_v13_full.parquet   (자원 축: final_size, fit_time_sec)
_internal/cache/rq3/paired_delta_v13.parquet      (정확도 축: delta_pct_mean)

output
------
experiments/figures/paper_exact_v13/F7_pareto_frontier_finalsize.{png,pdf}
experiments/figures/paper_exact_v13/F7_pareto_frontier_finalsize_data.csv
experiments/figures/paper_exact_v13/F7_pareto_frontier_fittime.{png,pdf}
experiments/figures/paper_exact_v13/F7_pareto_frontier_fittime_data.csv

usage
-----
  python3 build_pareto_frontier_v13.py
"""
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
OUT_DIR = REPO_ROOT / "experiments" / "figures" / "paper_exact_v13"

# Apple SD Gothic Neo — 한국어 axis label
KOREAN_FONT = "Apple SD Gothic Neo"
plt.rcParams["font.family"] = KOREAN_FONT
plt.rcParams["axes.unicode_minus"] = False

# paradigm color (Capstone navy palette + accents) — v13 는 P1-P6, P9
PARADIGM_COLOR = {
    "P1": "#1f77b4",   # Cluster — blue
    "P2": "#2ca02c",   # Spatial — green
    "P3": "#ff7f0e",   # Streaming — orange
    "P4": "#9467bd",   # DimReduction — purple
    "P5": "#8c564b",   # QMC — brown
    "P6": "#e377c2",   # Quantization — pink
    "P9": "#17becf",   # InfoTheoretic — cyan
}
PARADIGM_LABEL = {
    "P1": "P1 Cluster", "P2": "P2 Spatial", "P3": "P3 Streaming",
    "P4": "P4 DimReduc", "P5": "P5 QMC", "P6": "P6 Quant",
    "P9": "P9 Info",
}

# frontier 강조 박스 annotation offset (points). frontier 구성이 자원 축마다
# 다르므로 spec 별 dict (RESOURCE_SPECS 안). 미등록 method 는 DEFAULT_OFFSET.
DEFAULT_OFFSET = (10, 12)

# 정확도 축 컬럼 — 측정별 Δ% 의 method-median. mean 은 minibatch_partial 등의
# 극단 cell(+1043% 등)에 끌려 method 위치를 왜곡하므로(v13_summary §4.4: minibatch
# mean +14.06% vs median -3.58%) robust 한 median 을 산점 위치로 쓴다. CSV 에는
# mean·median 모두 기록한다.
ACC_COL = "median_delta"


# ============================================================
# data loading
# ============================================================
def load_inputs():
    """aggregated_v13 (자원) + paired_delta_v13 (정확도) 로드."""
    agg_path = CACHE_DIR / "aggregated_v13_full.parquet"
    pd_path = CACHE_DIR / "paired_delta_v13.parquet"
    for p in (agg_path, pd_path):
        if not p.exists():
            raise FileNotFoundError(
                f"  {p} 부재. aggregate_v13.py / paired_delta_v13.py 선행 필요.")
    agg = pd.read_parquet(agg_path)
    delta = pd.read_parquet(pd_path)
    print(f"  loaded {agg_path.name}  ({len(agg)} rows)")
    print(f"  loaded {pd_path.name}  ({len(delta)} rows)")
    return agg, delta


# ============================================================
# 정확도 축 — method 단위 mean paired Δ% (CaseB_vs_B1)
# ============================================================
def compute_accuracy(delta: pd.DataFrame) -> pd.DataFrame:
    """paired_delta_v13 에서 method × paradigm 단위 mean Δ% 집계.

    comparison == "CaseB_vs_B1" 한정 — 결합 실험군 vs 대조군. 3-way 측정은
    measurement 자체가 matched 이므로 K=10/20/30 전체 포함 (v13_summary §4.4 동일).
    delta_pct_mean = (CaseB - B1) / B1 × 100, 음수 = 개선.
    """
    d = delta[delta["comparison"] == "CaseB_vs_B1"].copy()
    if d.empty:
        raise RuntimeError("  comparison == 'CaseB_vs_B1' 행 0건 — paired_delta_v13 확인.")
    g = (d.groupby(["method", "paradigm"])
          .agg(mean_delta=("delta_pct_mean", "mean"),
               median_delta=("delta_pct_mean", "median"),
               std_delta=("delta_pct_mean", "std"),
               n_obs=("delta_pct_mean", "size"),
               n_cells=("cell", "nunique"),
               better=("delta_pct_mean", lambda x: int((x < 0).sum())))
          .reset_index())
    g["better_rate"] = g["better"] / g["n_obs"] * 100.0
    return g


# ============================================================
# 자원 축 — method 단위 mean 자원 (2종)
# ============================================================
def resource_finalsize(agg: pd.DataFrame) -> pd.DataFrame:
    """CaseB 모드 final_size 평균 — 소비 표본 수 (작을수록 효율적)."""
    cb = agg[(agg["mode"] == "CaseB") & agg["final_size"].notna()]
    return (cb.groupby("method")["final_size"].mean()
              .reset_index(name="resource"))


def resource_fittime(agg: pd.DataFrame) -> pd.DataFrame:
    """fit_time_sec 평균 — 분포 파악(fit) 소요 시간 (작을수록 효율적).

    fit_time_sec 는 측정당 1값으로 B1/CaseA/CaseB 3 row 에 동일 기록되므로
    json_id 로 dedup 후 집계 (3중 계산 방지 — 평균값 자체는 불변이나 명시적 처리).
    """
    uniq = agg[agg["fit_time_sec"].notna()].drop_duplicates(subset=["json_id"])
    return (uniq.groupby("method")["fit_time_sec"].mean()
              .reset_index(name="resource"))


# 자원 축 2종 spec — offsets 는 해당 축의 frontier 구성 method 강조 박스 위치
RESOURCE_SPECS = [
    dict(
        key="finalsize",
        fn=resource_finalsize,
        xlabel="자원 비용  —  CaseB 평균 소비 표본 수 final_size  (작을수록 효율적)",
        title="자원·정확도 Pareto frontier  —  자원 = 소비 표본 수 (final_size)",
        resource_name="소비 표본 수 final_size",
        value_fmt="{:.0f}",
        offsets={
            "cum_sqrtf":     (-54, 2),
            "ica_fastica":   (-32, -26),
            "hilbert_real":  (-6, -34),
            "chao_weighted": (22, -24),
        },
    ),
    dict(
        key="fittime",
        fn=resource_fittime,
        xlabel="자원 비용  —  분포 파악(fit) 평균 소요 시간 (초)  (작을수록 효율적)",
        title="자원·정확도 Pareto frontier  —  자원 = 분포 파악 비용 (fit-time)",
        resource_name="fit-time (초)",
        value_fmt="{:.1f}s",
        offsets={
            "sparse_rp":     (-12, 24),
            "chao_weighted": (10, -30),
        },
    ),
]


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
def make_plot(g: pd.DataFrame, spec: dict, out_png: Path, out_pdf: Path):
    """g: method, paradigm, mean_delta, resource, on_frontier 컬럼 보유."""
    fig, ax = plt.subplots(figsize=(11, 7))

    colors = [PARADIGM_COLOR.get(p, "#7f7f7f") for p in g["paradigm"]]
    ax.scatter(g["resource"], g[ACC_COL],
               s=300, c=colors, alpha=0.78, edgecolors="black",
               linewidths=0.8, zorder=3)

    # Pareto frontier line (lower-left)
    fr = g[g["on_frontier"]].sort_values("resource")
    ax.plot(fr["resource"], fr[ACC_COL],
            color="#d62728", linewidth=1.9, linestyle="--",
            label="Pareto frontier", zorder=2, alpha=0.85, marker="o",
            markersize=6, markerfacecolor="white", markeredgecolor="#d62728")

    # annotation — frontier method 는 강조 박스, 나머지는 작은 라벨
    for _, row in g.iterrows():
        m = str(row["method"])
        x, y = float(row["resource"]), float(row[ACC_COL])
        if bool(row["on_frontier"]):
            dx, dy = spec["offsets"].get(m, DEFAULT_OFFSET)
            ax.annotate(
                m, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                fontsize=10, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="#fffacd",
                          ec="#d62728", lw=1.0, alpha=0.95),
                arrowprops=dict(arrowstyle="-", color="#d62728", lw=0.8),
                zorder=5)
        else:
            ax.annotate(m, xy=(x, y), xytext=(8, -3),
                        textcoords="offset points", fontsize=7.5,
                        color="#444444", zorder=4)

    # axis cosmetics
    ax.set_xlabel(spec["xlabel"], fontsize=12, fontfamily=KOREAN_FONT)
    ax.set_ylabel("정확도 개선  —  paired Δ% 의 method-median   "
                  "[Δ% = (CaseB - B1) / B1 x 100, 음수 = 개선]",
                  fontsize=12, fontfamily=KOREAN_FONT)
    ax.set_title(spec["title"], fontsize=13, fontweight="bold",
                 fontfamily=KOREAN_FONT, pad=14)

    ax.axhline(0, color="gray", linewidth=0.8, linestyle=":", alpha=0.75, zorder=1)
    ax.grid(True, linestyle="-", alpha=0.22, zorder=0)

    # legend (paradigm + frontier) — median 전환 후 upper-left 가 빈 사분면
    paradigms_in = sorted(g["paradigm"].unique())
    handles = [plt.scatter([], [], s=140, c=PARADIGM_COLOR.get(p, "#7f7f7f"),
                           edgecolors="black", linewidths=0.7, alpha=0.78,
                           label=PARADIGM_LABEL.get(p, p))
               for p in paradigms_in]
    handles.append(plt.Line2D([0], [0], color="#d62728", linewidth=1.9,
                              linestyle="--", marker="o", markersize=6,
                              markerfacecolor="white",
                              label="Pareto frontier"))
    ax.legend(handles=handles, loc="upper left", fontsize=9,
              framealpha=0.92, ncol=2)

    fr_methods = " · ".join(fr["method"].tolist())
    fig.text(0.99, 0.01,
             f"data: aggregated_v13 + paired_delta_v13  |  16 method  |  "
             f"정확도 = CaseB_vs_B1 측정별 Δ% 의 method-median (n=1508, K 전체)  |  "
             f"Pareto frontier ({len(fr)}): {fr_methods}",
             ha="right", fontsize=8, color="#555555", fontfamily=KOREAN_FONT)

    plt.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_png}")
    print(f"  wrote {out_pdf}")


# ============================================================
# 자원 축 1종 처리
# ============================================================
def build_one(acc: pd.DataFrame, agg: pd.DataFrame, spec: dict):
    res = spec["fn"](agg)
    g = acc.merge(res, on="method", how="inner")
    if g.empty:
        raise RuntimeError(
            f"  [{spec['key']}] accuracy × resource 병합 0행 — method 키 불일치.")
    g = g.sort_values(ACC_COL).reset_index(drop=True)

    # frontier 계산 — (resource, median Δ%) lower-left
    pts = g[["resource", ACC_COL]].to_numpy()
    fr_idx = set(pareto_frontier(pts).tolist())
    g["on_frontier"] = [i in fr_idx for i in range(len(g))]

    # sanity
    fr = g[g["on_frontier"]].sort_values("resource")
    print(f"\n  [{spec['key']}]  scatter point: {len(g)} method")
    print(f"  resource range  : {g['resource'].min():.2f} – {g['resource'].max():.2f}")
    print(f"  median Δ% range : {g[ACC_COL].min():+.2f}% – {g[ACC_COL].max():+.2f}%")
    print(f"  Pareto frontier ({len(fr)}): "
          + ", ".join(f"{r['method']}({spec['value_fmt'].format(r['resource'])}, "
                      f"{r[ACC_COL]:+.2f}%)" for _, r in fr.iterrows()))

    out_png = OUT_DIR / f"F7_pareto_frontier_{spec['key']}.png"
    out_pdf = OUT_DIR / f"F7_pareto_frontier_{spec['key']}.pdf"
    out_csv = OUT_DIR / f"F7_pareto_frontier_{spec['key']}_data.csv"

    csv = g[["method", "paradigm", "resource", "mean_delta", "median_delta",
             "std_delta", "n_obs", "n_cells", "better", "better_rate",
             "on_frontier"]].copy()
    csv = csv.rename(columns={"resource": f"resource_{spec['key']}"})
    csv.to_csv(out_csv, index=False)
    print(f"  wrote {out_csv}")

    make_plot(g, spec, out_png, out_pdf)


# ============================================================
# main
# ============================================================
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    agg, delta = load_inputs()
    acc = compute_accuracy(delta)

    # headline sanity — v13_summary §3 CaseB_vs_B1 대조
    cbb = delta[delta["comparison"] == "CaseB_vs_B1"]
    print(f"\n  CaseB_vs_B1 headline: n={len(cbb)}  "
          f"better={int((cbb['delta_pct_mean'] < 0).sum())} "
          f"({(cbb['delta_pct_mean'] < 0).mean() * 100:.1f}%)  "
          f"mean Δ%={cbb['delta_pct_mean'].mean():+.2f}  "
          f"median Δ%={cbb['delta_pct_mean'].median():+.2f}")

    for spec in RESOURCE_SPECS:
        build_one(acc, agg, spec)


if __name__ == "__main__":
    main()
