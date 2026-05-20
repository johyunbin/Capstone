#!/usr/bin/env python3
"""6/11 최종 보고서용 figure 9종 생성 (matplotlib).

속도는벡터 캡스톤 — 벡터 카디널리티 추정에서 표본 선택(sample selection) 방식의
효과 검증. 보고서 본문에 들어갈 그림 9종 (각 PNG dpi 200 + PDF).

다이어그램(1-1·2-1·3-1·3-2·5-1)은 FancyBboxPatch + FancyArrowPatch,
데이터 그림(3-3·4-1·4-3·6-1)은 막대/간트차트.

Usage:
    python3 build_report_figures_20260519.py
"""
from __future__ import annotations

from pathlib import Path
import datetime as dt

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---------------------------------------------------------------------------
# 공통 스타일
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": ["Apple SD Gothic Neo", "AppleGothic", "DejaVu Sans"],
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11,
    "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 10,
    "figure.dpi": 120, "savefig.dpi": 200,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.unicode_minus": False,
})

# 색 팔레트
NAVY = "#1f4e79"   # 강한 / 우위
RED = "#a13a3a"    # 약한 / 악화
BLUE = "#4a7bd8"   # 보조
GRAY = "#888888"
NAVY_SOFT = "#dce7f3"
GRAY_SOFT = "#e8e8e8"
RED_SOFT = "#f3dede"

OUT = Path("/Users/hyunbin/Capstone/experiments/figures/보고서_6_11")
OUT.mkdir(parents=True, exist_ok=True)


def save(fig, name: str):
    """PNG(dpi 200) + PDF 동시 저장."""
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight",
                    dpi=200 if ext == "png" else None)
    plt.close(fig)
    print(f"  ✓ {name}.png / .pdf")


# ---------------------------------------------------------------------------
# 다이어그램 헬퍼
# ---------------------------------------------------------------------------
def box(ax, x, y, w, h, text, *, fc="white", ec=NAVY, tc="#1a1a1a",
        fontsize=10, lw=1.4, fontweight="normal", rounding=0.035, ls="-"):
    """FancyBboxPatch 박스 + 중앙 텍스트. (x,y)=좌하단."""
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={rounding}",
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=3)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            color=tc, fontsize=fontsize, fontweight=fontweight,
            zorder=4, linespacing=1.45)
    return patch


def arrow(ax, x0, y0, x1, y1, *, color="#444444", lw=1.8, scale=14,
          style="-|>"):
    """FancyArrowPatch 화살표."""
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle=style, mutation_scale=scale,
        color=color, linewidth=lw, zorder=2,
        shrinkA=0, shrinkB=0))


# ===========================================================================
# fig1_1 — 연구 개요 다이어그램
# ===========================================================================
def fig1_1():
    fig, ax = plt.subplots(figsize=(9, 6.2))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12.4)
    ax.axis("off")

    # 상단 가로 파이프라인 4박스
    pw, ph, py = 3.7, 1.55, 9.7
    gap = (18 - 4 * pw) / 5  # 균등 간격
    xs = [gap + i * (pw + gap) for i in range(4)]
    pipe = [
        ("데이터셋", "white", NAVY, "#1a1a1a", "normal"),
        ("표본 선택", NAVY, NAVY, "white", "bold"),
        ("카디널리티 추정\n(논문 식 1–6, 불변)", GRAY_SOFT, GRAY, "#333333", "normal"),
        ("Q-error 평가", "white", NAVY, "#1a1a1a", "normal"),
    ]
    for x, (txt, fc, ec, tc, fw) in zip(xs, pipe):
        box(ax, x, py, pw, ph, txt, fc=fc, ec=ec, tc=tc, fontweight=fw,
            fontsize=10.5)
    # 파이프라인 화살표
    for i in range(3):
        arrow(ax, xs[i] + pw, py + ph / 2, xs[i + 1], py + ph / 2)

    # 표본 선택 강조 라벨
    ax.text(xs[1] + pw / 2, py + ph + 0.55,
            "★ 본 연구의 단일 개입 지점",
            ha="center", va="bottom", fontsize=10.5, fontweight="bold",
            color=NAVY)
    # 카디널리티 추정 라벨
    ax.text(xs[2] + pw / 2, py - 0.45, "논문 그대로 — 변경 없음",
            ha="center", va="top", fontsize=9, style="italic", color=GRAY)

    # 표본 선택 박스 아래 3갈래 분기
    bw, bh, by = 4.85, 1.95, 5.0
    bgap = (18 - 3 * bw) / 4
    bxs = [bgap + i * (bw + bgap) for i in range(3)]
    branches = [
        ("B1 (대조군)\n무작위 베르누이 표본 추출", GRAY_SOFT, GRAY, "#333333", "-"),
        ("CaseA (음성 대조군)\n분포 인지 층화 — 완전 대체", RED_SOFT, RED, "#333333", "-"),
        ("CaseB (결합 실험군)\n베르누이+층화 산술 평균", NAVY, NAVY, "white", "-"),
    ]
    src_x = xs[1] + pw / 2  # 표본 선택 박스 하단 중심
    for bx, (txt, fc, ec, tc, ls) in zip(bxs, branches):
        box(ax, bx, by, bw, bh, txt, fc=fc, ec=ec, tc=tc, fontsize=10,
            lw=1.8, ls=ls, fontweight="bold" if fc == NAVY else "normal")
        # 분기점(표본 선택 박스 하단)에서 각 박스 상단으로
        arrow(ax, src_x, py - 0.02, bx + bw / 2, by + bh, color=NAVY,
              lw=1.6)

    # 하단 캡션
    ax.text(9, 2.55,
            "한 측정이 B1·CaseA·CaseB 세 방식을 동일 조건에서 동시 산출 (3-way matched)",
            ha="center", va="center", fontsize=10.5, color="#333333",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f5f6f8", ec=GRAY,
                      linewidth=0.8))
    ax.set_title("그림 1-1. 본 연구의 개입 지점과 3-way 측정 구조", pad=14,
                 fontweight="bold")
    save(fig, "fig1_1_research_overview")


# ===========================================================================
# fig2_1 — Exqutor 카디널리티 추정 파이프라인
# ===========================================================================
def fig2_1():
    fig, ax = plt.subplots(figsize=(9, 6.4))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12.8)
    ax.axis("off")

    # 상단 VAQ 쿼리 박스
    tw, th, tx, ty = 9.0, 1.5, 4.5, 10.6
    box(ax, tx, ty, tw, th,
        "VAQ 쿼리 — 벡터 조건의 카디널리티 추정 필요",
        fc=NAVY_SOFT, ec=NAVY, tc="#1a1a1a", fontsize=10.5, fontweight="bold")

    # 분기 라벨 (박스 바로 아래 중앙, 화살표 시작점보다 위)
    ax.text(9, ty - 0.35, "벡터 인덱스 유무에 따라 분기",
            ha="center", va="top", fontsize=9.5, style="italic",
            color="#555555")

    # 좌(인덱스 있음) / 우(인덱스 없음)
    cw, ch, cy = 7.4, 2.5, 5.4
    lx, rx = 1.0, 18 - 1.0 - cw
    box(ax, lx, cy, cw, ch,
        "§V-A  ECQO\nHNSW range query → 정확값 (1–2ms)",
        fc=GRAY_SOFT, ec=GRAY, tc="#333333", fontsize=10.2)
    box(ax, rx, cy, cw, ch,
        "§V-B  Adaptive Sampling\n무작위 베르누이 표본 N=385\n+ momentum 보정식 1–6",
        fc=NAVY_SOFT, ec=NAVY, tc="#1a1a1a", fontsize=10.2, lw=1.8)

    # 분기 화살표 (분기 라벨 아래 지점에서 시작 → 라벨과 겹침 회피)
    cx_top = tx + tw / 2
    branch_y = ty - 0.95  # 화살표 시작 y (분기 라벨 아래)
    arrow(ax, cx_top, branch_y, lx + cw / 2, cy + ch, color=GRAY, lw=1.6)
    arrow(ax, cx_top, branch_y, rx + cw / 2, cy + ch, color=NAVY, lw=1.8)
    # 화살표 라벨 — 화살표 경로에서 바깥쪽으로 띄움
    ax.text(lx + cw / 2 - 1.3, cy + ch + 0.5,
            "인덱스 있음", ha="center", va="bottom", fontsize=9.5,
            color=GRAY, fontweight="bold")
    ax.text(rx + cw / 2 + 1.3, cy + ch + 0.5,
            "인덱스 없음", ha="center", va="bottom", fontsize=9.5,
            color=NAVY, fontweight="bold")

    # ECQO "본 연구 대상 아님"
    ax.text(lx + cw / 2, cy - 0.4, "본 연구 대상 아님",
            ha="center", va="top", fontsize=9, style="italic", color=GRAY)

    # §V-B 아래 작은 강조 박스
    ew, eh = 4.2, 1.15
    ex = rx + cw / 2 - ew / 2
    ey = cy - eh - 0.7
    box(ax, ex, ey, ew, eh, "표본 선택 단계 ★",
        fc=NAVY, ec=NAVY, tc="white", fontsize=10, fontweight="bold")
    arrow(ax, rx + cw / 2, cy, rx + cw / 2, ey + eh, color=NAVY, lw=1.6)
    ax.text(rx + cw / 2, ey - 0.4, "본 연구의 개입 지점",
            ha="center", va="top", fontsize=9.5, fontweight="bold",
            color=NAVY)

    # 하단 캡션
    ax.text(9, 1.35,
            "본 연구는 §V-B의 표본 선택 단계만 개입, §V-A·식 1–6은 그대로 둔다",
            ha="center", va="center", fontsize=10.5, color="#333333",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f5f6f8", ec=GRAY,
                      linewidth=0.8))
    ax.set_title("그림 2-1. Exqutor 카디널리티 추정 파이프라인", pad=14,
                 fontweight="bold")
    save(fig, "fig2_1_exqutor_pipeline")


# ===========================================================================
# fig3_1 — 표본 선택 3단계 흐름도
# ===========================================================================
def fig3_1():
    fig, ax = plt.subplots(figsize=(8.5, 7.6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 13.4)
    ax.axis("off")

    # 세로 3박스
    bw, bh = 9.6, 2.65
    bx = (14 - bw) / 2 + 0.55  # 색띠 공간 확보 위해 약간 우측
    band_w = 0.55
    stages = [
        ("1단계 — 분포 인지 층화 (stratification)\n"
         "offline · 데이터셋 진입 시 1회\n"
         "Type 판별 → method 선택 → K=20 계층 생성",
         "offline", GRAY),
        ("2단계 — 표본 추출\n"
         "online · 매 쿼리\n"
         "표본 예산 N=385를 K개 계층에 균등 배분 (N/K씩)",
         "online", NAVY),
        ("3단계 — 결합\n"
         "online · 매 쿼리\n"
         "est_final = (est_b1 + est_method) / 2.0",
         "online", NAVY),
    ]
    ys = [9.5, 5.7, 1.9]
    for y, (txt, mode, mc) in zip(ys, stages):
        # 본 박스
        box(ax, bx, y, bw, bh, txt, fc="white", ec=NAVY, tc="#1a1a1a",
            fontsize=10.3, lw=1.6)
        # 왼쪽 색 띠 라벨
        bandp = FancyBboxPatch(
            (bx - band_w - 0.18, y), band_w, bh,
            boxstyle="round,pad=0.0,rounding_size=0.03",
            facecolor=mc, edgecolor=mc, zorder=3)
        ax.add_patch(bandp)
        ax.text(bx - band_w - 0.18 + band_w / 2, y + bh / 2, mode,
                ha="center", va="center", color="white", fontsize=9.5,
                fontweight="bold", rotation=90, zorder=4)
    # 화살표
    for i in range(2):
        arrow(ax, bx + bw / 2, ys[i], bx + bw / 2, ys[i + 1] + bh,
              color=NAVY, lw=1.8)

    # 하단 캡션
    ax.text(7, 0.85,
            "논문 식 1–6을 위반하지 않는 minimal augmentation — 표본 예산은 그대로",
            ha="center", va="center", fontsize=10.3, color="#333333",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f5f6f8", ec=GRAY,
                      linewidth=0.8))
    ax.set_title("그림 3-1. 표본 선택 3단계 흐름도", pad=14, fontweight="bold")
    save(fig, "fig3_1_sample_selection_3stage")


# ===========================================================================
# fig3_2 — 3-way matched 측정 구조
# ===========================================================================
def fig3_2():
    fig, ax = plt.subplots(figsize=(9, 5.7))
    ax.set_xlim(0, 18)
    ax.set_ylim(1.4, 12.6)
    ax.axis("off")

    # 중앙 상단 박스
    cw, ch, cx, cy = 8.6, 2.4, (18 - 8.6) / 2, 9.4
    box(ax, cx, cy, cw, ch,
        "measure_3way — 한 측정\n같은 cell·selectivity·K·method\n10 trial × 1000 query",
        fc=NAVY_SOFT, ec=NAVY, tc="#1a1a1a", fontsize=10.3, fontweight="bold",
        lw=1.8)

    # 3갈래 박스
    bw, bh, by = 4.9, 2.05, 5.0
    bgap = (18 - 3 * bw) / 4
    bxs = [bgap + i * (bw + bgap) for i in range(3)]
    modes = [
        ("B1 (대조군)\nest = est_b1", GRAY_SOFT, GRAY, "#333333"),
        ("CaseA (완전 대체)\nest = est_method", RED_SOFT, RED, "#333333"),
        ("CaseB (결합)\nest = (est_b1 + est_method) / 2", NAVY, NAVY, "white"),
    ]
    src_x = cx + cw / 2
    for bx, (txt, fc, ec, tc) in zip(bxs, modes):
        box(ax, bx, by, bw, bh, txt, fc=fc, ec=ec, tc=tc, fontsize=10,
            lw=1.8, fontweight="bold" if fc == NAVY else "normal")
        arrow(ax, src_x, cy, bx + bw / 2, by + bh, color=NAVY, lw=1.6)

    # 화살표 라벨
    ax.text(9, (cy + by + bh) / 2 + 0.1,
            "동일 조건·동일 trial → 완벽 짝지음 (matched)",
            ha="center", va="center", fontsize=9.7, fontweight="bold",
            color=NAVY,
            bbox=dict(boxstyle="round,pad=0.32", fc="white", ec=NAVY,
                      linewidth=0.9))

    # 하단 캡션
    ax.text(9, 2.5,
            "측정 1,508건 × 3 mode = 통합 4,524행",
            ha="center", va="center", fontsize=10.5, color="#333333",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f5f6f8", ec=GRAY,
                      linewidth=0.8))
    ax.set_title("그림 3-2. 3-way matched 측정 구조", pad=14, fontweight="bold")
    save(fig, "fig3_2_3way_matched")


# ===========================================================================
# fig3_3 — 데이터셋 Type 분류
# ===========================================================================
def fig3_3():
    types = ["Type 1", "Type 2", "Type 3", "Type 4a", "Type 4b"]
    counts = [272, 224, 464, 368, 180]
    dims = ["96~768d", "96~768d", "96~256d", "192~288d", "864~1024d"]
    descs = [
        "소규모 단일 sf=1 (DEEP/SIFT/SSN/WIKI/YFCC)",
        "중규모 단일 sf=10 (DEEP/SIFT/SSN/WIKI)",
        "대규모 단일 sf=100 (DEEP/SIFT/SSN)",
        "다중 벡터 (YFCC·DEEP+SIFT·DEEP+YFCC)",
        "다중 벡터 고차원 (DEEP+WIKI·DEEP+CC3M)",
    ]
    # Type 1~3 BLUE 계열, 4a·4b NAVY
    colors = [BLUE, BLUE, BLUE, NAVY, NAVY]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    y = np.arange(len(types))[::-1]
    bars = ax.barh(y, counts, color=colors, edgecolor="white", height=0.58,
                   zorder=3)
    for bar, c, d, ds in zip(bars, counts, dims, descs):
        yc = bar.get_y() + bar.get_height() / 2
        # 막대 안 측정 수 (흰 글씨, 막대 끝에서 안쪽)
        ax.text(c - 9, yc, f"{c}건", va="center", ha="right",
                fontsize=10, fontweight="bold", color="white", zorder=4)
        # 막대 위쪽에 차원·설명 주석 (막대 길이 무관, 겹침 없음)
        ax.text(8, yc + 0.42, f"{d}  ·  {ds}", va="bottom", ha="left",
                fontsize=8.6, color="#333333", zorder=4)

    ax.set_yticks(y)
    ax.set_yticklabels(types, fontsize=10.5, fontweight="bold")
    ax.set_xlabel("측정 수 (건)")
    ax.set_xlim(0, 510)
    ax.set_ylim(-0.6, len(types) - 0.25)
    ax.grid(axis="x", alpha=0.3, zorder=0)

    # 범례
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=BLUE, label="단일 벡터 (Type 1~3)"),
                        Patch(facecolor=NAVY, label="다중 벡터 (Type 4a·4b)")],
              loc="lower right", frameon=True, framealpha=0.95)
    # 합계 표기
    ax.text(0.99, 1.02, "합계 1,508건", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=10, fontweight="bold",
            color=NAVY)
    ax.set_title("그림 3-3. 데이터셋 Type 분류와 Type별 측정 수 (총 1,508건)",
                 pad=10, fontweight="bold")
    plt.tight_layout()
    save(fig, "fig3_3_dataset_type")


# ===========================================================================
# fig4_1 — method·paradigm별 Δ%
# ===========================================================================
def fig4_1():
    # 16 method
    methods = [
        ("chao_weighted", -6.22), ("hilbert_real", -5.91),
        ("skilling_hilbert", -5.75), ("ica_fastica", -5.69),
        ("pca1d", -5.55), ("zorder_morton", -4.89),
        ("hyperloglog", -4.58), ("cum_sqrtf", -4.53),
        ("lavallee_hidiroglou", -4.40), ("sparse_rp", -4.37),
        ("rsvd", -4.10), ("minibatch_partial", -3.58),
        ("rabitq_strat", -3.56), ("mhist2", -3.41),
        ("faiss_ivf", -2.70), ("gmm", 2.68),
    ]
    weak = {"gmm", "minibatch_partial", "faiss_ivf"}
    # 오름차순 정렬(가장 우월 = 가장 음수 = 맨 위)
    methods = sorted(methods, key=lambda t: t[1])
    m_names = [m for m, _ in methods]
    m_vals = [v for _, v in methods]
    m_colors = [RED if m in weak else NAVY for m in m_names]

    # 7 paradigm
    paradigms = [
        ("P3 Streaming", -6.22), ("P4 DimReduction", -4.72),
        ("P2 Spatial", -4.66), ("P9 InfoTheoretic", -4.58),
        ("P5 QMC", -4.43), ("P6 Quantization", -3.52),
        ("P1 Cluster", -1.40),
    ]
    paradigms = sorted(paradigms, key=lambda t: t[1])
    p_names = [p for p, _ in paradigms]
    p_vals = [v for _, v in paradigms]
    p_colors = [RED if p.startswith("P1 ") else NAVY for p in p_names]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9, 5.6),
                                   gridspec_kw={"width_ratios": [1.35, 1]})

    # ---- 왼쪽: 16 method ----
    yL = np.arange(len(m_names))[::-1]
    barsL = axL.barh(yL, m_vals, color=m_colors, edgecolor="white",
                     height=0.66, zorder=3)
    axL.axvline(0, color="black", linewidth=0.7, zorder=2)
    for bar, v in zip(barsL, m_vals):
        yc = bar.get_y() + bar.get_height() / 2
        if v < 0:
            axL.text(v - 0.2, yc, f"{v:+.2f}", va="center", ha="right",
                     fontsize=8.3, color="#333333")
        else:
            axL.text(v + 0.2, yc, f"{v:+.2f}", va="center", ha="left",
                     fontsize=8.3, color="#333333")
    axL.set_yticks(yL)
    axL.set_yticklabels(m_names, fontsize=8.8)
    axL.set_xlabel("중앙값 Δ% (CaseB vs B1) — 음수 = 우위")
    axL.set_xlim(-7.7, 4.0)
    axL.grid(axis="x", alpha=0.3, zorder=0)
    axL.set_title("16 method", fontsize=11.5, pad=6)
    from matplotlib.patches import Patch
    axL.legend(handles=[Patch(facecolor=NAVY, label="강한 method 13"),
                         Patch(facecolor=RED, label="클러스터링 계열 3")],
               loc="lower left", fontsize=8.6, frameon=True,
               framealpha=0.95)

    # ---- 오른쪽: 7 paradigm ----
    yR = np.arange(len(p_names))[::-1]
    barsR = axR.barh(yR, p_vals, color=p_colors, edgecolor="white",
                     height=0.62, zorder=3)
    axR.axvline(0, color="black", linewidth=0.7, zorder=2)
    for bar, v in zip(barsR, p_vals):
        yc = bar.get_y() + bar.get_height() / 2
        axR.text(v - 0.15, yc, f"{v:+.2f}", va="center", ha="right",
                 fontsize=9, color="#333333")
    axR.set_yticks(yR)
    axR.set_yticklabels(p_names, fontsize=9.3)
    axR.set_xlabel("중앙값 Δ%")
    axR.set_xlim(-7.4, 0.6)
    axR.grid(axis="x", alpha=0.3, zorder=0)
    axR.set_title("7 paradigm", fontsize=11.5, pad=6)

    fig.suptitle("그림 4-1. method·paradigm별 CaseB vs B1 중앙값 Δ%",
                 fontsize=13, fontweight="bold", y=1.005)
    plt.tight_layout()
    save(fig, "fig4_1_method_paradigm_delta")


# ===========================================================================
# fig4_3 — K granularity
# ===========================================================================
def fig4_3():
    ks = ["K=10", "K=20", "K=30"]
    better = [83.6, 89.8, 85.9]
    deltas = [-6.47, -7.12, -6.02]
    colors = [BLUE, NAVY, BLUE]

    fig, ax = plt.subplots(figsize=(7.2, 5.3))
    x = np.arange(len(ks))
    bars = ax.bar(x, better, color=colors, edgecolor="white", width=0.56,
                  zorder=3)
    for bar, b, d in zip(bars, better, deltas):
        xc = bar.get_x() + bar.get_width() / 2
        # 막대 위 better% + 중앙값 Δ% 주석
        ax.text(xc, b + 1.4, f"better {b:.1f}%", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#1a1a1a")
        ax.text(xc, b + 5.0, f"중앙값 Δ% {d:.2f}%", ha="center", va="bottom",
                fontsize=9, color="#555555")

    # K=20 강조 라벨
    ax.annotate("논문 default — 최강", xy=(1, 89.8), xytext=(1, 70),
                ha="center", fontsize=9.5, fontweight="bold", color=NAVY,
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.3))

    ax.set_xticks(x)
    ax.set_xticklabels(ks, fontsize=11, fontweight="bold")
    ax.set_ylabel("better% (CaseB가 B1보다 우수한 비율, %)")
    ax.set_ylim(0, 100)
    ax.set_xlabel("계층 수 K  (각 n=128)")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.set_title("그림 4-3. 계층 수 K별 CaseB vs B1 (8-cell × sel=0.01, K별 128건)",
                 pad=10, fontweight="bold")
    plt.tight_layout()
    save(fig, "fig4_3_k_granularity")


# ===========================================================================
# fig5_1 — 동적 method 선택 4단계 흐름도
# ===========================================================================
def fig5_1():
    fig, ax = plt.subplots(figsize=(8.5, 9.4))
    ax.set_xlim(0, 14)
    ax.axis("off")

    bw = 9.4
    bx = (14 - bw) / 2
    steps = [
        ("데이터셋 진입", 1.15, NAVY_SOFT, NAVY, "#1a1a1a"),
        ("Step 1 — 데이터셋 프로파일 파악\n행 수 · 단일/다중 구조 · 차원",
         1.85, NAVY_SOFT, NAVY, "#1a1a1a"),
        ("Step 2 — Type 판별\n(Type 1/2/3/4a/4b)",
         1.85, NAVY_SOFT, NAVY, "#1a1a1a"),
        ("Step 3 — Type별 권장 method 자동 선택",
         1.45, NAVY_SOFT, NAVY, "#1a1a1a"),
        ("Step 4 — CaseB 결합\nest_final = (est_b1 + est_method) / 2.0",
         1.85, NAVY, NAVY, "white"),
        ("논문 §V-B AdaptiveState 식 1–6 보정\n— 어떤 경우에도 불변",
         1.85, GRAY_SOFT, GRAY, "#333333"),
    ]
    # 위에서 아래로 y 좌표 계산 (박스 사이 간격 = GAP 일정)
    GAP = 1.0
    top = 14.6
    coords = []
    y_top = top
    for txt, h, fc, ec, tc in steps:
        y_bottom = y_top - h
        coords.append((y_bottom, h, txt, fc, ec, tc))
        y_top = y_bottom - GAP  # 다음 박스 상단
    for (yy, h, txt, fc, ec, tc) in coords:
        box(ax, bx, yy, bw, h, txt, fc=fc, ec=ec, tc=tc, fontsize=10.2,
            lw=1.8 if fc in (NAVY, GRAY_SOFT) else 1.5,
            fontweight="bold" if fc == NAVY else "normal")
    # 화살표 — 각 박스 하단에서 다음 박스 상단으로
    for i in range(len(coords) - 1):
        y0 = coords[i][0]                       # 현재 박스 하단
        y1 = coords[i + 1][0] + coords[i + 1][1]  # 다음 박스 상단
        col = GRAY if i == len(coords) - 2 else NAVY
        arrow(ax, bx + bw / 2, y0, bx + bw / 2, y1, color=col, lw=1.8)
    last_bottom = coords[-1][0]
    ax.set_ylim(last_bottom - 0.5, top + 0.5)

    # 옆 주석 (마지막 두 박스 옆)
    note_y = (coords[4][0] + coords[5][0] + coords[5][1]) / 2
    ax.annotate(
        "동적으로 바뀌는 것\n= method 선택 + 결합뿐.\n논문 식 1–6은 불변.",
        xy=(bx, note_y), xytext=(0.35, note_y),
        ha="left", va="center", fontsize=9.3, color="#444444",
        fontweight="bold", linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.4", fc="#f5f6f8", ec=GRAY,
                  linewidth=0.8))

    ax.set_title("그림 6-1. 동적 method 선택 4단계 흐름도", pad=12,
                 fontweight="bold")
    save(fig, "fig6_1_dynamic_method_selection")


# ===========================================================================
# fig6_1 — 진행 간트차트
# ===========================================================================
def fig6_1():
    def d(s):
        return dt.datetime.strptime(s, "%Y-%m-%d")

    tasks = [
        ("주제 선정·Exqutor 논문 분석", "2026-03-02", "2026-03-22"),
        ("RQ 설계·연구 방향 확정", "2026-03-23", "2026-04-13"),
        ("RQ1·RQ2 측정·분석", "2026-04-07", "2026-04-27"),
        ("paper exact 재현 측정 (§V-B)", "2026-05-01", "2026-05-15"),
        ("3-way matched 측정 캠페인 (1,508건)", "2026-05-12", "2026-05-20"),
        ("측정 분석·narrative 작성", "2026-05-15", "2026-05-26"),
        ("최종 보고서 작성", "2026-05-29", "2026-06-11"),
    ]
    milestones = [
        ("중간보고서·중간발표", "2026-04-28"),
        ("최종 발표", "2026-05-27"),
        ("전시회 포스터", "2026-05-28"),
        ("최종 보고서 제출", "2026-06-11"),
    ]

    fig, ax = plt.subplots(figsize=(9, 5.6))
    y = np.arange(len(tasks))[::-1]
    for yi, (name, s, e) in zip(y, tasks):
        s0, e0 = d(s), d(e)
        ax.barh(yi, (e0 - s0).days, left=s0, height=0.55, color=NAVY,
                edgecolor="white", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels([t[0] for t in tasks], fontsize=9.5)

    # 마일스톤 ◆ — 마커는 한 줄에, 라벨은 가까우면 좌우 분산 + 리더선
    marker_y = -0.95
    ms_dates = [d(dt_) for _, dt_ in milestones]
    # 라벨 x 위치를 잡되, 가까운 마일스톤은 최소 간격 확보
    label_x = list(ms_dates)
    min_gap = (d("2026-06-18") - d("2026-02-28")).days * 0.135
    for i in range(1, len(label_x)):
        if (label_x[i] - label_x[i - 1]).days < min_gap:
            label_x[i] = label_x[i - 1] + dt.timedelta(days=min_gap)
    # 전체를 약간 왼쪽으로 시프트(오른쪽 끝 넘침 방지)
    overflow = (label_x[-1] - d("2026-06-10")).days
    if overflow > 0:
        label_x = [lx - dt.timedelta(days=overflow) for lx in label_x]
    label_y = -2.0
    for (name, date), mx, lx in zip(milestones, ms_dates, label_x):
        ax.scatter(mx, marker_y, marker="D", s=85, color=RED, zorder=5,
                   edgecolor="white", linewidth=0.8, clip_on=False)
        # 리더선 (마커 → 라벨)
        ax.plot([mx, lx], [marker_y - 0.18, label_y + 0.35],
                color=RED, linewidth=0.7, alpha=0.6, zorder=4,
                clip_on=False)
        ax.annotate(f"◆ {name}\n{date[5:]}", xy=(lx, label_y),
                    ha="center", va="top", fontsize=7.8,
                    color=RED, fontweight="bold", linespacing=1.3,
                    annotation_clip=False)

    # x축 = 날짜 (월 단위)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.set_xlim(d("2026-02-28"), d("2026-06-18"))
    ax.set_ylim(-3.6, len(tasks) - 0.3)
    ax.grid(axis="x", alpha=0.3, zorder=0)
    ax.tick_params(axis="x", labelsize=9)

    # 범례
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=NAVY, label="작업 기간"),
                        Line2D([0], [0], marker="D", color="white",
                               markerfacecolor=RED, markersize=9,
                               label="마일스톤")],
              loc="upper left", fontsize=9, frameon=True, framealpha=0.95)
    ax.set_title("그림 7-1. 캡스톤 연구 진행 일정", pad=10, fontweight="bold")
    plt.tight_layout()
    save(fig, "fig7_1_gantt")


# ---------------------------------------------------------------------------
def main():
    print(f"[build_report_figures] 출력 → {OUT}/")
    fig1_1()
    fig2_1()
    fig3_1()
    fig3_2()
    fig3_3()
    fig4_1()
    fig4_3()
    fig5_1()
    fig6_1()
    print(f"\n✓ 신규 figure 9종 완료 → {OUT}/")


if __name__ == "__main__":
    main()
