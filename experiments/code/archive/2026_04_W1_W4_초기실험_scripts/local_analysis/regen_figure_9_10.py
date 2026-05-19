"""
A 등급 figure 재생성 — figure_9 (Two-Level Decomposition) + figure_10 (Cluster Skew)
설계 원칙: PDF 100% zoom 라벨 가독, 라벨 겹침 0, Apple SD Gothic Neo 폰트.
Raw data: experiments/results/RQ1_RQ2 실험 결과 정리.md (L173-181, L185-191; cluster CV).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import rcParams

rcParams["font.family"] = "Apple SD Gothic Neo"
rcParams["axes.unicode_minus"] = False
rcParams["font.size"] = 10

# Colors — 학술 톤
C_L1 = "#E8A857"   # warm orange (비례 배분)
C_L2 = "#4682B4"   # steel blue (공간 인식)
C_TOTAL = "#2E8B57"  # sea green (Total)
C_DEEP = "#4682B4"
C_SIFT = "#E8A857"
C_UNIFORM = "#999999"

OUT_DIR = "/Users/hyunbin/Capstone/experiments/figures/rq2_aware"


# ─────────────────────────────────────────────────────────────────────
# figure_9 — Two-Level Decomposition (DEEP 1M + SIFT 1.5M)
# ─────────────────────────────────────────────────────────────────────
def fig9_two_level_decomposition():
    # raw — RQ1_RQ2 정리.md L173-181, L185-191
    deep = {
        "sels":  ["0.50", "0.30", "0.10", "0.05", "0.01"],
        "L1":    [+2.20, +0.26, +1.74, +0.79, -10.67],
        "L2":    [-0.56, +2.36, +2.45, +1.06, +19.60],
        "Total": [+1.64, +2.62, +4.19, +1.85, +8.93],
    }
    sift = {
        "sels":  ["0.50", "0.05", "0.01"],
        "L1":    [+1.01, -0.05, -12.11],
        "L2":    [+2.06, +4.44, +11.58],
        "Total": [+3.07, +4.39, -0.53],
    }

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5),
                             gridspec_kw=dict(width_ratios=[5, 3], wspace=0.28))
    # inner suptitle 제거 — 보고서 캡션 "그림 7. Two-Level Decomposition ..." 와 중복 회피

    for ax, ds, title in [(axes[0], deep, "DEEP 1M (96d)"),
                          (axes[1], sift, "SIFT 1.5M (128d)")]:
        n = len(ds["sels"])
        x = np.arange(n)
        bw = 0.36

        # stacked bar — L1 (음/양 모두), L2 (양수만 측정됨)
        L1, L2, T = ds["L1"], ds["L2"], ds["Total"]

        # 막대 위치: 각 selectivity 마다 1 stacked bar (왼쪽) + Total 별도 ◆ 마커 (오른쪽)
        # L2 위에, L1 아래/위 (sign 따라)
        bar_x = x - 0.18
        marker_x = x + 0.22

        bars_l1 = ax.bar(bar_x, L1, bw, color=C_L1, edgecolor="white", linewidth=0.8,
                         label="Level 1 — 비례 배분", zorder=3)
        bars_l2 = ax.bar(bar_x, L2, bw, bottom=[max(0, l) if l > 0 else 0 for l in L1],
                         color=C_L2, edgecolor="white", linewidth=0.8,
                         label="Level 2 — 공간 인식", zorder=3)

        # Total ◆ marker
        ax.scatter(marker_x, T, marker="D", s=85, color=C_TOTAL, zorder=5,
                   edgecolor="white", linewidth=1.2, label="Total (KM20)")

        # Total 라벨 + 분해 정보 통합 (작은 막대는 L1/L2 라벨이 막대 안에서 겹치므로 Total 옆에 표시)
        # 큰 막대 (abs(l1) ≥ 4 또는 abs(l2) ≥ 4) 만 막대 내부 라벨, 그 외는 Total 옆 sub-line
        for xi, t, l1, l2 in zip(marker_x, T, L1, L2):
            sign_t = "+" if t >= 0 else ""
            big_l1 = abs(l1) >= 4.0
            big_l2 = abs(l2) >= 4.0
            if big_l1 or big_l2:
                # 막대가 충분히 큼 → Total 라벨만
                ax.annotate(f"{sign_t}{t:.2f}", (xi, t),
                            xytext=(0, 12 if t >= 0 else -16),
                            textcoords="offset points",
                            ha="center", fontsize=10, fontweight="bold",
                            color=C_TOTAL)
            else:
                # 작은 막대 → Total + (L1, L2) 통합 라벨
                label = f"{sign_t}{t:.2f}\nL1 {l1:+.1f} · L2 {l2:+.1f}"
                ax.annotate(label, (xi, t),
                            xytext=(0, 10 if t >= 0 else -32),
                            textcoords="offset points",
                            ha="center", fontsize=8.5, fontweight="medium",
                            color=C_TOTAL, linespacing=1.3)

        # L1, L2 라벨은 큰 막대에서만 (작은 막대는 위에서 Total 옆 통합 처리)
        for xi, l1, l2 in zip(bar_x, L1, L2):
            big_l1 = abs(l1) >= 4.0
            big_l2 = abs(l2) >= 4.0
            if big_l1:
                # L1 음수 큰 막대 (예: -10.67) — 막대 끝 아래
                if l1 < 0:
                    ax.annotate(f"L1 {l1:+.2f}", (xi, l1),
                                xytext=(0, -6), textcoords="offset points",
                                ha="center", va="top",
                                fontsize=9, color="black", fontweight="medium")
                else:
                    ax.annotate(f"L1 {l1:+.2f}", (xi, l1 / 2),
                                xytext=(0, 0), textcoords="offset points",
                                ha="center", va="center",
                                fontsize=9, color="white", fontweight="medium")
            if big_l2:
                # L2 큰 막대 — 막대 정상 위 또는 막대 안 (white)
                l2_top = max(0, l1) + l2 if l1 > 0 else l2
                if l2 > 0:
                    ax.annotate(f"L2 {l2:+.2f}", (xi, l2_top / 2 if l1 <= 0 else (max(0, l1) + l2_top) / 2),
                                xytext=(0, 0), textcoords="offset points",
                                ha="center", va="center",
                                fontsize=9, color="white", fontweight="medium")
                else:
                    ax.annotate(f"L2 {l2:+.2f}", (xi, l2_top),
                                xytext=(0, -6), textcoords="offset points",
                                ha="center", va="top",
                                fontsize=9, color="black", fontweight="medium")

        ax.axhline(0, color="black", linewidth=0.6, zorder=2)
        ax.set_xticks(x)
        ax.set_xticklabels(ds["sels"])
        ax.set_xlabel("Selectivity", fontsize=10)
        ax.set_ylabel("Q-error 개선폭 (%, BERNOULLI 대비)", fontsize=9.5)
        ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
        ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # y range — 라벨 여유 확보
        ymin = min(min(L1), min(L2), min(T)) - 4
        ymax = max(max(L1), max(L2), max(T), [max(0, l1) + l2 for l1, l2 in zip(L1, L2)][-1] if L2 else 0) + 5
        ax.set_ylim(ymin, ymax)

    # 범례 (좌측 패널 상단 안쪽)
    handles = [
        mpatches.Patch(color=C_TOTAL, label="◆ Total (KM20)"),
        mpatches.Patch(color=C_L2, label="L2 — 공간 인식"),
        mpatches.Patch(color=C_L1, label="L1 — 비례 배분"),
    ]
    axes[0].legend(handles=handles, loc="upper left", fontsize=8.5,
                   frameon=True, fancybox=False, edgecolor="gray", framealpha=0.95)

    fig.text(0.5, 0.04,
             "주: Level 1 은 RANDOM20 의 개선분 (파티션 품질 무관). Level 2 는 KM20 vs RANDOM20 격차 (공간 인식 추가 이득).\n"
             "DEEP 1M s = 0.01 에서 Level 2 = +19.60. SIFT 는 s = 0.50 부터 Level 2 가 +2.06 으로 이미 발현.",
             ha="center", fontsize=11, color="#222", linespacing=1.55)

    plt.subplots_adjust(top=0.95, bottom=0.22, left=0.07, right=0.985)
    out = f"{OUT_DIR}/figure_9_two_level_decomposition.png"
    plt.savefig(out, dpi=170, bbox_inches="tight", pad_inches=0.15)
    plt.close()
    print(f"saved: {out}")


# ─────────────────────────────────────────────────────────────────────
# figure_10 — Cluster Skew (DEEP vs SIFT, K=20)
# ─────────────────────────────────────────────────────────────────────
def fig10_cluster_skew():
    # raw — cluster_distribution.md
    deep_min, deep_exp, deep_max = 26343, 50000, 81233   # n/K = 50,000
    sift_min, sift_exp, sift_max = 33330, 75000, 148202  # n/K = 75,000
    deep_max_min = deep_max / deep_min
    sift_max_min = sift_max / sift_min

    deep_hhi, sift_hhi, uni_hhi = 0.0527, 0.0578, 0.0500
    deep_cv, sift_cv, uni_cv = 0.234, 0.394, 0.000

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5),
                             gridspec_kw=dict(width_ratios=[1.05, 1], wspace=0.26))
    # inner suptitle 제거 — 보고서 캡션 "그림 8. DEEP 1M 과 SIFT 1.5M ..." 와 중복 회피

    # ── (a) 클러스터 크기 범위 — K-means K=20
    ax = axes[0]
    groups = ["DEEP 1M (96d)", "SIFT 1.5M (128d)"]
    x = np.arange(len(groups))
    bw = 0.24

    mins = [deep_min, sift_min]
    exps = [deep_exp, sift_exp]
    maxs = [deep_max, sift_max]

    b1 = ax.bar(x - bw, mins, bw, color="#a0c4e0", label="Min 클러스터",
                edgecolor="white", linewidth=0.7)
    b2 = ax.bar(x,      exps, bw, color=C_DEEP, label="Expected (n/K)",
                edgecolor="white", linewidth=0.7)
    b3 = ax.bar(x + bw, maxs, bw, color=C_SIFT, label="Max 클러스터",
                edgecolor="white", linewidth=0.7)

    for bars, vals in [(b1, mins), (b2, exps), (b3, maxs)]:
        for r, v in zip(bars, vals):
            ax.annotate(f"{v:,}", (r.get_x() + r.get_width() / 2, v),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=8, fontweight="medium")

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{g}\nMax/Min = {r:.2f}×" for g, r in zip(groups, [deep_max_min, sift_max_min])],
        fontsize=9.5,
    )
    ax.set_ylabel("클러스터 크기 (행 수)", fontsize=9.5)
    ax.set_title("(a) 클러스터 크기 범위 — K-means K=20", fontsize=10.5,
                 fontweight="bold", pad=8)
    ax.legend(loc="upper left", fontsize=8.5, frameon=True,
              fancybox=False, edgecolor="gray", framealpha=0.95)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, max(maxs) * 1.18)

    # ── (b) 쏠림 정량 — HHI & CV
    ax = axes[1]
    metrics = ["HHI", "CV"]
    x = np.arange(len(metrics))
    bw = 0.24

    deep_vals = [deep_hhi, deep_cv]
    sift_vals = [sift_hhi, sift_cv]
    uni_vals  = [uni_hhi, uni_cv]

    b1 = ax.bar(x - bw, deep_vals, bw, color=C_DEEP, label="DEEP 1M (96d)",
                edgecolor="white", linewidth=0.7)
    b2 = ax.bar(x,      sift_vals, bw, color=C_SIFT, label="SIFT 1.5M (128d)",
                edgecolor="white", linewidth=0.7)
    b3 = ax.bar(x + bw, uni_vals,  bw, color=C_UNIFORM, label="균일 기준",
                edgecolor="white", linewidth=0.7)

    # 라벨 — 막대 위
    for bars, vals in [(b1, deep_vals), (b2, sift_vals), (b3, uni_vals)]:
        for r, v in zip(bars, vals):
            label = f"{v:.4f}" if v < 0.1 else f"{v:.3f}"
            if v == 0:
                label = "0.0000"
            ax.annotate(label, (r.get_x() + r.get_width() / 2, v),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=8, fontweight="medium")

    # SIFT vs DEEP CV 격차 강조 — brace 박스를 우상단 빈 공간에 배치
    # CV 막대 정상점 (SIFT 0.394) 가 라벨 0.394 와 충돌하지 않도록
    # brace 박스 위치: 우상단 (x=1.4, y=0.46), 화살표 끝 = SIFT CV 막대 정상 (x=1.0, y=0.394) 약간 위
    sift_cv_x = 1.0
    sift_cv_y = sift_cv

    # annotation box
    bbox = dict(boxstyle="round,pad=0.4", fc="white", ec=C_TOTAL, lw=1.3)
    ax.annotate("SIFT가 DEEP 대비\nCV 68% 높음",
                xy=(sift_cv_x, sift_cv_y + 0.02),
                xytext=(1.42, 0.50),
                fontsize=8.5, color=C_TOTAL, fontweight="bold",
                ha="center", va="center", bbox=bbox,
                arrowprops=dict(arrowstyle="->", color=C_TOTAL,
                                lw=1.2, shrinkA=0, shrinkB=4))

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylabel("쏠림 지표 값", fontsize=9.5)
    ax.set_title("(b) 쏠림 정량화 — HHI & CV (균일 기준 비교)", fontsize=10.5,
                 fontweight="bold", pad=8)
    ax.legend(loc="upper left", fontsize=8.5, frameon=True,
              fancybox=False, edgecolor="gray", framealpha=0.95)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, 0.62)

    fig.text(0.5, 0.04,
             "주: HHI 는 각 클러스터 비율의 제곱합 (균일 = 1/K = 0.05). CV 는 표준편차 / 평균 (균일 = 0).\n"
             "SIFT 는 클러스터 14 만행 이상 7 개로 전체의 약 19 % (기대 10 %). 쏠림 정량 격차가 KM20 효과 2 배 격차의 직접 원인.",
             ha="center", fontsize=11, color="#222", linespacing=1.55)

    plt.subplots_adjust(top=0.95, bottom=0.22, left=0.06, right=0.985)
    out = f"{OUT_DIR}/figure_10_cluster_skew.png"
    plt.savefig(out, dpi=170, bbox_inches="tight", pad_inches=0.15)
    plt.close()
    print(f"saved: {out}")


if __name__ == "__main__":
    fig9_two_level_decomposition()
    fig10_cluster_skew()
    print("DONE.")
