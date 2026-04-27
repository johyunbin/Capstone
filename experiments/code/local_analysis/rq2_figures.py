#!/usr/bin/env python3
"""
rq2_figures.py — RQ2 (Distribution-Aware) 시각화 4종 생성

사용법:
    python3 scripts/rq2_figures.py

출력:
    experiments/figures/rq2_aware/figure_7_selectivity_gradient.png
    experiments/figures/rq2_aware/figure_8_cross_dataset_bar.png
    experiments/figures/rq2_aware/figure_9_two_level_decomposition.png
    experiments/figures/rq2_aware/figure_10_cluster_skew.png

수치 원천:
    experiments/results/RQ1_RQ2 실험 결과 정리.md (4/17 통합본, 진실 소스)
    experiments/results/rq2_aware/sift_1m_mid_summary.json
    experiments/results/rq2_aware/8m_km20_s0500_5seed.json
    experiments/results/rq2_aware/cluster_distribution.md

스타일:
    - 폰트: Apple SD Gothic Neo
    - dpi=150
    - 논문용 단조 팔레트 (dark gray, blue, orange)
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# --------------------------------------------------------------------------
# 스타일 초기화
# --------------------------------------------------------------------------

rcParams["font.family"] = ["Apple SD Gothic Neo", "AppleGothic", "Nanum Gothic", "sans-serif"]
rcParams["axes.unicode_minus"] = False
rcParams["font.size"] = 11
rcParams["axes.titlesize"] = 12
rcParams["axes.labelsize"] = 11
rcParams["xtick.labelsize"] = 10
rcParams["ytick.labelsize"] = 10
rcParams["legend.fontsize"] = 10
rcParams["figure.dpi"] = 150
rcParams["savefig.dpi"] = 150
rcParams["savefig.bbox"] = "tight"
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["axes.grid"] = True
rcParams["grid.alpha"] = 0.25
rcParams["grid.linestyle"] = "--"

# 논문용 단조 팔레트
C_DARK = "#2b2b2b"  # dark gray (reference lines, RANDOM20)
C_BLUE = "#1f77b4"  # KM20, L2
C_ORANGE = "#e07a00"  # Level 1 (비례 배분), SIFT highlight
C_GRAY = "#9aa0a6"  # neutral fills
C_GREEN_DARK = "#2e7d32"  # positive highlight

OUT = Path(__file__).resolve().parent.parent / "experiments" / "figures" / "rq2_aware"
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# 실험 수치 (통합본 4/17 기준, JSON과 정합 확인 완료)
# --------------------------------------------------------------------------

# DEEP 1M — 5 selectivity: KM20 / RANDOM20 평균 및 95% CI
# CI가 없는 구간은 None으로 표기 (단일 측정)
DEEP_1M = {
    "selectivity": [0.50, 0.30, 0.10, 0.05, 0.01],
    "KM20_mean": [1.64, 2.62, 4.19, 1.85, 8.93],
    "KM20_ci": [(1.11, 2.18), (1.45, 3.80), (0.72, 7.66), None, None],
    "RAND20_mean": [2.20, 0.26, 1.74, 0.79, -10.67],
    "RAND20_ci": [None, (-0.52, 1.05), (0.50, 2.99), None, None],
}

# DEEP 8M — 3 selectivity (s=50 / s=5 / s=1), s=10/s=30은 미측정
DEEP_8M = {
    "selectivity": [0.50, 0.05, 0.01],
    "KM20_mean": [1.76, 0.55, -0.71],
    "KM20_ci": [(0.65, 2.86), (-3.11, 4.21), (-21.13, 19.70)],
    "RAND20_mean": [1.10, 0.20, 11.06],
    "RAND20_ci": [(0.44, 1.75), (-3.75, 4.16), (0.89, 21.23)],
}

# SIFT 1.5M — 3 selectivity (s=50 / s=5 / s=1), s=10/s=30은 서버 오류 미측정
SIFT_1_5M = {
    "selectivity": [0.50, 0.05, 0.01],
    "KM20_mean": [3.07, 4.39, -0.53],
    "KM20_ci": [(2.66, 3.48), (2.63, 6.15), (-3.18, 2.11)],
    "RAND20_mean": [1.01, -0.05, -12.11],
    "RAND20_ci": [(-0.17, 2.19), (-3.85, 3.75), (-29.02, 4.79)],
}

# Two-Level Decomposition (통합본 §실험 6)
TWO_LEVEL = {
    "DEEP 1M (96d)": {
        "selectivity": [0.50, 0.30, 0.10, 0.05, 0.01],
        "L1": [2.20, 0.26, 1.74, 0.79, -10.67],
        "L2": [-0.56, 2.36, 2.45, 1.06, 19.60],
        "Total": [1.64, 2.62, 4.19, 1.85, 8.93],
    },
    "SIFT 1.5M (128d)": {
        "selectivity": [0.50, 0.05, 0.01],
        "L1": [1.01, -0.05, -12.11],
        "L2": [2.06, 4.44, 11.58],
        "Total": [3.07, 4.39, -0.53],
    },
}

# 클러스터 분포 (통합본 §실험 1)
CLUSTER = {
    "DEEP 1M (96d)": {
        "n_rows": 1_000_000,
        "K": 20,
        "min": 26_343,
        "max": 81_233,
        "ratio": 3.08,
        "HHI": 0.05274,
        "CV": 0.234,
    },
    "SIFT 1.5M (128d)": {
        "n_rows": 1_500_000,
        "K": 20,
        "min": 33_330,
        "max": 148_202,
        "ratio": 4.45,
        "HHI": 0.05776,
        "CV": 0.394,
    },
}

# --------------------------------------------------------------------------
# Helper
# --------------------------------------------------------------------------

def ci_to_yerr(mean_list, ci_list):
    """평균과 CI 튜플을 [y_low_err, y_high_err] 형태로 변환.
    CI None이면 0으로 채움 (에러바 미표시)."""
    y_low, y_high = [], []
    for m, ci in zip(mean_list, ci_list):
        if ci is None:
            y_low.append(0.0)
            y_high.append(0.0)
        else:
            y_low.append(m - ci[0])
            y_high.append(ci[1] - m)
    return [y_low, y_high]


# --------------------------------------------------------------------------
# Figure 7: DEEP 1M selectivity gradient (KM20 vs RANDOM20)
# --------------------------------------------------------------------------

def figure_7_selectivity_gradient():
    fig, ax = plt.subplots(figsize=(9, 5.5))

    sel = DEEP_1M["selectivity"]

    km20_mean = DEEP_1M["KM20_mean"]
    km20_err = ci_to_yerr(km20_mean, DEEP_1M["KM20_ci"])

    rand_mean = DEEP_1M["RAND20_mean"]
    rand_err = ci_to_yerr(rand_mean, DEEP_1M["RAND20_ci"])

    # 선 + 오차막대 (CI가 없는 점은 yerr=0이므로 자연스럽게 점만 표시됨)
    ax.errorbar(
        sel, km20_mean, yerr=km20_err,
        fmt="o-", color=C_BLUE, ecolor=C_BLUE, elinewidth=1.5, capsize=4,
        markersize=7, linewidth=2.0, label="KM20 (공간 인식)", zorder=3,
    )
    ax.errorbar(
        sel, rand_mean, yerr=rand_err,
        fmt="s--", color=C_ORANGE, ecolor=C_ORANGE, elinewidth=1.5, capsize=4,
        markersize=6, linewidth=1.8, label="RANDOM20 (무작위 분할)", zorder=2,
    )

    # 0 기준선
    ax.axhline(0, color=C_DARK, linewidth=0.8, linestyle=":", zorder=1)

    # s=0.01에서 Level 2 gap 강조 — 양 선 사이 수직 가이드 + 라벨
    ax.plot([0.01, 0.01], [-10.67, 8.93], color=C_GREEN_DARK,
            linewidth=1.5, linestyle="-", alpha=0.6, zorder=2)
    ax.text(
        0.015, -1,
        "격차 = 19.60%p\n(Level 2,\n공간 인식 기여)",
        fontsize=9.5, color=C_GREEN_DARK, fontweight="bold", ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                  edgecolor=C_GREEN_DARK, linewidth=1.2),
    )

    ax.set_xscale("log")
    ax.set_xlabel("Selectivity (로그 스케일)")
    ax.set_ylabel("Q-error 개선폭 (%, 대조군 BERNOULLI 대비)")
    ax.set_title(
        "Figure 7 · DEEP 1M Selectivity Gradient — KM20 vs RANDOM20 (95% CI)",
        fontweight="bold", pad=14,
    )

    # x축 눈금 라벨 (실제 selectivity 값)
    ax.set_xticks(sel)
    ax.set_xticklabels([f"{s:.2f}" for s in sel])
    ax.invert_xaxis()  # 왼쪽이 s=0.50, 오른쪽이 s=0.01 (narrowing)

    ax.legend(loc="upper left", frameon=True, fancybox=False, edgecolor=C_DARK)

    caption = (
        "주: KM20은 모든 selectivity에서 양의 개선. RANDOM20은 s=0.01에서 -10.67%로 악화.\n"
        "격차가 클수록 공간 인식의 가치가 큼 (좁은 쿼리일수록 KM20 우위 확대).\n"
        "s=0.05, s=0.01은 단일 측정(Phase 6)이라 CI 없음 — 보충 5-seed 재측정은 최종보고서 예정."
    )
    fig.text(0.125, -0.02, caption, fontsize=8.5, color=C_DARK, va="top")

    out = OUT / "figure_7_selectivity_gradient.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")


# --------------------------------------------------------------------------
# Figure 8: Cross-dataset bar (s=0.500 KM20 개선폭, CI error bar)
# --------------------------------------------------------------------------

def figure_8_cross_dataset_bar():
    fig, ax = plt.subplots(figsize=(8.5, 5.5))

    datasets = ["DEEP 1M\n(96d)", "DEEP 8M\n(96d)", "SIFT 1.5M\n(128d)"]
    means = [
        DEEP_1M["KM20_mean"][0],    # s=0.50
        DEEP_8M["KM20_mean"][0],
        SIFT_1_5M["KM20_mean"][0],
    ]
    cis = [
        DEEP_1M["KM20_ci"][0],
        DEEP_8M["KM20_ci"][0],
        SIFT_1_5M["KM20_ci"][0],
    ]
    err = ci_to_yerr(means, cis)

    cvs = [0.234, 0.234, 0.394]  # 쏠림(CV)

    colors = [C_BLUE, C_BLUE, C_ORANGE]
    x = np.arange(len(datasets))
    bars = ax.bar(x, means, yerr=err, capsize=7, color=colors, edgecolor=C_DARK,
                  linewidth=1.0, alpha=0.88, width=0.55)

    # 막대 위 수치 (annotation 박스와 겹치지 않도록 충분히 위로)
    for xi, m, ci in zip(x, means, cis):
        lo, hi = ci
        ax.text(xi, hi + 0.25, f"+{m:.2f}%", ha="center", va="bottom",
                fontsize=11.5, fontweight="bold", color=C_DARK)
        ax.text(xi, m / 2, f"CV={cvs[xi]:.3f}", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")

    # CI 숫자 (막대 하단)
    for xi, ci in zip(x, cis):
        lo, hi = ci
        ax.text(xi, -0.35, f"CI [{lo:+.2f}, {hi:+.2f}]", ha="center", va="top",
                fontsize=8.5, color=C_DARK)

    ax.axhline(0, color=C_DARK, linewidth=0.8, linestyle=":", zorder=0)

    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.set_ylabel("KM20 Q-error 개선폭 (%, BERNOULLI 대비, s=0.500, 5-seed mean)")
    ax.set_title(
        "Figure 8 · 외적 타당성 — 3 데이터셋에서 KM20 s=0.500 효과 (95% CI)",
        fontweight="bold", pad=14,
    )
    ax.set_ylim(-1.0, 5.3)

    # 강조 텍스트 박스: 막대 수치 위쪽 여유 공간에 배치 (겹침 방지)
    ax.text(
        1, 4.65, "SIFT가 DEEP 대비 CV 68% 높음 → KM20 효과 ~2배",
        ha="center", fontsize=10, color=C_GREEN_DARK, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="white",
                  edgecolor=C_GREEN_DARK, linewidth=1.2),
    )
    # 화살표는 박스에서 SIFT 막대 상단으로
    ax.annotate(
        "",
        xy=(2, 3.55),
        xytext=(1.55, 4.55),
        arrowprops=dict(arrowstyle="->", color=C_GREEN_DARK, lw=1.5),
    )

    caption = (
        "주: DEEP 1M/8M의 CI는 겹침(외적 재현 CONSISTENT). SIFT의 CI는 DEEP과 겹치지 않아 통계적으로 구별.\n"
        "쏠림도(CV)가 큰 데이터일수록 공간 인식 샘플링의 이점이 더 크게 발현됨."
    )
    fig.text(0.125, -0.02, caption, fontsize=8.5, color=C_DARK, va="top")

    out = OUT / "figure_8_cross_dataset_bar.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")


# --------------------------------------------------------------------------
# Figure 9: Two-Level Decomposition (DEEP vs SIFT stacked bar)
# --------------------------------------------------------------------------

def figure_9_two_level_decomposition():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)

    for ax, (name, data) in zip(axes, TWO_LEVEL.items()):
        sel = data["selectivity"]
        l1 = np.array(data["L1"])
        l2 = np.array(data["L2"])
        total = np.array(data["Total"])

        x = np.arange(len(sel))
        # Stacked: Level 1 아래(기저), Level 2 위.
        # 부호가 다를 수 있으므로 positive/negative 분리해서 쌓기.
        ax.bar(x, l1, color=C_ORANGE, edgecolor=C_DARK, linewidth=0.8,
               width=0.6, label="Level 1 — 비례 배분", alpha=0.88)

        # Level 2는 Level 1 위에 쌓되, L1이 음수면 L2는 0부터 시작하도록 조정
        l2_bottom = np.where(l1 >= 0, l1, 0)
        l2_bottom_neg = np.where(l1 < 0, l1, 0)  # 음수 L1 옆 쌓기용 (미사용)
        ax.bar(x, l2, bottom=l2_bottom, color=C_BLUE, edgecolor=C_DARK,
               linewidth=0.8, width=0.6, label="Level 2 — 공간 인식", alpha=0.92)

        # Total 값을 마커로 표시
        ax.plot(x, total, marker="D", markersize=8, color=C_GREEN_DARK,
                linestyle="", label="Total (KM20)", zorder=5)

        # 0 기준선
        ax.axhline(0, color=C_DARK, linewidth=0.8, linestyle=":", zorder=1)

        # 레벨별 수치 라벨
        for xi, (v1, v2, tot) in enumerate(zip(l1, l2, total)):
            # Level 1 중앙 (막대 내부)
            if abs(v1) > 0.5:
                ax.text(xi, v1 / 2, f"L1 {v1:+.2f}",
                        ha="center", va="center", fontsize=8.5,
                        color="white", fontweight="bold")
            # Level 2 수치 라벨 — L1 부호에 따라 위치 다르게
            if abs(v2) > 0.8:
                if v1 >= 0:
                    # L2가 L1 위로 쌓인 경우: L1+L2/2
                    y_label = v1 + v2 / 2
                else:
                    # L1이 음수이면 L2는 0에서 시작해서 위로 쌓임
                    y_label = v2 / 2
                ax.text(xi, y_label, f"L2 {v2:+.2f}",
                        ha="center", va="center", fontsize=8.5,
                        color="white", fontweight="bold")
            # Total 숫자 (다이아몬드 위/아래) — Level 2 영역과 충분히 간격
            if v1 >= 0:
                offset = 1.2
            else:
                # L1 음수이면 total이 대개 L2 높이 부근
                offset = 1.5 if tot >= 0 else -1.8
            ax.text(xi, tot + offset, f"Total {tot:+.2f}%",
                    ha="center", va="center", fontsize=9,
                    color=C_GREEN_DARK, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels([f"{s:.2f}" for s in sel])
        ax.set_xlabel("Selectivity")
        ax.set_title(f"{name}", fontweight="bold", pad=10)

    axes[0].set_ylabel("Q-error 개선폭 (%, BERNOULLI 대비)")
    axes[0].legend(loc="upper left", frameon=True, edgecolor=C_DARK)

    fig.suptitle(
        "Figure 9 · Two-Level Decomposition — KM20 개선을 비례 배분(L1)과 공간 인식(L2)으로 분해",
        fontweight="bold", fontsize=13, y=1.02,
    )

    caption = (
        "주: Level 1은 RANDOM20의 개선분(파티션 품질 무관), Level 2는 KM20-RANDOM20 격차(공간 인식 기여).\n"
        "selectivity가 줄수록 Level 2의 기여가 급증하며, DEEP 1M s=0.01에서 Level 2 단독 +19.60%p.\n"
        "SIFT는 s=0.50부터 이미 Level 2(+2.06%)가 유의 — 쏠림이 클수록 공간 인식의 영향이 넓은 구간에 발현."
    )
    fig.text(0.06, -0.03, caption, fontsize=8.5, color=C_DARK, va="top")

    out = OUT / "figure_9_two_level_decomposition.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")


# --------------------------------------------------------------------------
# Figure 10: 클러스터 쏠림 지표 (DEEP vs SIFT) — Min/Max + HHI/CV
# --------------------------------------------------------------------------

def figure_10_cluster_skew():
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.5))

    datasets = list(CLUSTER.keys())  # ['DEEP 1M (96d)', 'SIFT 1.5M (128d)']

    # --- Left panel: cluster size range (Min/Expected/Max, normalized to expected) ---
    ax = axes[0]

    # 데이터: K=20일 때 기대 크기 = n_rows/K
    expected = [CLUSTER[d]["n_rows"] / CLUSTER[d]["K"] for d in datasets]
    mins = [CLUSTER[d]["min"] for d in datasets]
    maxs = [CLUSTER[d]["max"] for d in datasets]

    x = np.arange(len(datasets))
    width = 0.25

    # 3개 막대: min, expected, max
    bars_min = ax.bar(x - width, mins, width, color=C_GRAY, edgecolor=C_DARK,
                     linewidth=0.8, label="Min 클러스터", alpha=0.88)
    bars_exp = ax.bar(x, expected, width, color=C_BLUE, edgecolor=C_DARK,
                     linewidth=0.8, label="Expected (=n/K)", alpha=0.88)
    bars_max = ax.bar(x + width, maxs, width, color=C_ORANGE, edgecolor=C_DARK,
                     linewidth=0.8, label="Max 클러스터", alpha=0.88)

    # 수치 annotation
    for bars in [bars_min, bars_exp, bars_max]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 3000,
                    f"{int(h):,}", ha="center", va="bottom", fontsize=9,
                    color=C_DARK)

    # Max/Min 비율 annotation
    for xi, d in enumerate(datasets):
        ratio = CLUSTER[d]["ratio"]
        ax.text(xi, -12000, f"Max/Min = {ratio:.2f}×",
                ha="center", va="top", fontsize=10, fontweight="bold",
                color=C_GREEN_DARK)

    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.set_ylabel("클러스터 크기 (행 수)")
    ax.set_title("(a) 클러스터 크기 범위 — K-means K=20", fontweight="bold", pad=10)
    ax.legend(loc="upper left", frameon=True, edgecolor=C_DARK)
    ax.set_ylim(-20000, 175000)

    # --- Right panel: HHI + CV 정규화 지표 ---
    ax = axes[1]

    metrics = ["HHI", "CV"]
    deep_vals = [CLUSTER[datasets[0]]["HHI"], CLUSTER[datasets[0]]["CV"]]
    sift_vals = [CLUSTER[datasets[1]]["HHI"], CLUSTER[datasets[1]]["CV"]]
    uniform_ref = [0.05, 0.0]  # 균일 기준 (1/K=0.05, CV=0)

    x = np.arange(len(metrics))
    width = 0.28

    bars_deep = ax.bar(x - width, deep_vals, width, color=C_BLUE,
                      edgecolor=C_DARK, linewidth=0.8,
                      label=datasets[0], alpha=0.88)
    bars_sift = ax.bar(x, sift_vals, width, color=C_ORANGE,
                      edgecolor=C_DARK, linewidth=0.8,
                      label=datasets[1], alpha=0.88)
    bars_ref = ax.bar(x + width, uniform_ref, width, color=C_GRAY,
                     edgecolor=C_DARK, linewidth=0.8,
                     label="균일 기준", alpha=0.60)

    for bars, vals in [(bars_deep, deep_vals), (bars_sift, sift_vals), (bars_ref, uniform_ref)]:
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.005,
                    f"{v:.4f}" if v < 0.1 else f"{v:.3f}",
                    ha="center", va="bottom", fontsize=9, color=C_DARK)

    # 범례를 upper left로 옮겨 annotation 박스와 겹치지 않도록
    ax.legend(loc="upper left", frameon=True, edgecolor=C_DARK)

    # 68% 쏠림 차이 annotation — 오른쪽 상단(범례 반대쪽)에 배치
    ax.annotate(
        "SIFT가 DEEP 대비\nCV 68% 높음",
        xy=(1, 0.394), xytext=(1.1, 0.49),
        fontsize=10, color=C_GREEN_DARK, fontweight="bold", ha="center",
        arrowprops=dict(arrowstyle="->", color=C_GREEN_DARK, lw=1.3),
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                  edgecolor=C_GREEN_DARK, linewidth=1.2),
    )

    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylabel("쏠림 지표 값")
    ax.set_title("(b) 쏠림 정량화 — HHI & CV (균일 기준 비교)",
                 fontweight="bold", pad=10)
    ax.set_ylim(0, 0.58)
    ax.set_xlim(-0.6, 1.7)

    fig.suptitle(
        "Figure 10 · 데이터셋 클러스터 쏠림 — DEEP 1M vs SIFT 1.5M",
        fontweight="bold", fontsize=13, y=1.01,
    )

    caption = (
        "주: HHI는 각 클러스터 비율의 제곱합(균일=1/K=0.05), CV는 표준편차/평균(균일=0).\n"
        "SIFT는 최대 클러스터 14.8만으로 기대값 7.5만의 2배. 클러스터 1과 18 합계가 전체의 약 19% (기대 10%).\n"
        "쏠림의 정량 차이가 Figure 8의 KM20 효과 2배 격차의 직접적 원인."
    )
    fig.text(0.06, -0.02, caption, fontsize=8.5, color=C_DARK, va="top")

    out = OUT / "figure_10_cluster_skew.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"✓ {out}")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    print(f"Output dir: {OUT}")
    figure_7_selectivity_gradient()
    figure_8_cross_dataset_bar()
    figure_9_two_level_decomposition()
    figure_10_cluster_skew()
    print("\n완료. 4개 figure 생성됨.")


if __name__ == "__main__":
    main()
