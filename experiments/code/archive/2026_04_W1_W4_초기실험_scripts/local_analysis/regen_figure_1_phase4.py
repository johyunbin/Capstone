#!/usr/bin/env python3
"""
Regenerate Figure 1 (Phase 4 SYSTEM vs BERNOULLI scatter) with fixed tick labels.

수정사항:
  * 6-panel → 1x4 layout (s=0.05 / 0.10 / 0.30 / 0.50 만 표시, s=0.001/0.010 제외)
  * LogLocator(numticks=3) 로 x/y 틱 레이블 겹침 제거
  * Colorblind-safe palette (BERNOULLI #2E86AB, SYSTEM #E63946)
  * Panel title 에 p-value 주석 포함
  * 폰트 크기: 14pt title, 12pt axis label, 10pt tick
  * DPI 150, bbox_inches='tight'

또한 slide6_vector_c_snippet.png 도 함께 생성 (vector.c 3줄 수정 요약).

입력: experiments/results/rq1_motivation/{phase4_system,phase4_bernoulli}.parquet
       experiments/results/rq1_motivation/phase4_compare.json (p-value)
출력: experiments/figures/rq1_motivation/figure_1_phase4_scatter.png
       experiments/figures/rq1_motivation/slide6_vector_c_snippet.png
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import LogLocator, NullFormatter, ScalarFormatter


RESULTS_DIR = Path("/Users/hyunbin/Capstone/experiments/results/rq1_motivation")
FIG_DIR = Path("/Users/hyunbin/Capstone/experiments/figures/rq1_motivation")

# 표시할 selectivity (s=0.001 tie, s=0.010 non-significant 제외) — 유의성 별표
KEEP_SELECTIVITIES = [(0.05, "★★"), (0.10, "★★★"), (0.30, "★★★"), (0.50, "★★★")]

# Colorblind-safe palette
COLOR_BERN = "#2E86AB"   # blue
COLOR_SYS = "#E63946"    # red

# Apple SD Gothic Neo 로 한글 렌더 (macOS)
plt.rcParams["font.family"] = [
    "AppleGothic",
    "Apple SD Gothic Neo",
    "Helvetica",
    "Arial",
]
plt.rcParams["axes.unicode_minus"] = False


def format_p_value(p: float) -> str:
    """p-value 를 slide 친화적으로 포맷 (p<0.001, p<0.01, p=0.042, n.s. 등)."""
    if p is None or np.isnan(p):
        return "n.s."
    if p < 1e-6:
        return "p<1e-6"
    if p < 0.001:
        return "p<0.001"
    if p < 0.01:
        return "p<0.01"
    if p < 0.05:
        return f"p={p:.3f}"
    return f"p={p:.2f} (n.s.)"


def generate_figure_1() -> Path:
    sys_df = pd.read_parquet(RESULTS_DIR / "phase4_system.parquet")
    bern_df = pd.read_parquet(RESULTS_DIR / "phase4_bernoulli.parquet")
    merged = sys_df.merge(
        bern_df, on=["query_id", "selectivity"], suffixes=("_sys", "_bern")
    )

    with open(RESULTS_DIR / "phase4_compare.json") as f:
        compare = json.load(f)
    # Phase 4 JSON 의 p_greater 는 'SYSTEM > BERNOULLI' 대립가설 p-value
    p_by_sel = {round(r["selectivity"], 3): r["p_greater"] for r in compare}

    # 2×2 layout — 캡션 일치 + x/y 라벨 겹침 회피
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 8.6))
    axes = axes.flatten()

    for idx, (sel, sig) in enumerate(KEEP_SELECTIVITIES):
        ax = axes[idx]
        sub = merged[merged["selectivity"] == sel]
        sys_q = sub["q_error_sys"].to_numpy()
        bern_q = sub["q_error_bern"].to_numpy()

        ax.scatter(
            bern_q, sys_q, s=42, alpha=0.55,
            edgecolors=COLOR_SYS, facecolors="none", linewidths=1.1, zorder=3,
        )

        lo = min(bern_q.min(), sys_q.min()) * 0.95
        hi = max(bern_q.max(), sys_q.max()) * 1.05
        ax.plot([lo, hi], [lo, hi], "--", color="#475569", lw=0.9, zorder=1)

        ax.set_xscale("log")
        ax.set_yscale("log")
        # 핵심 수정: subs=[1, 2, 5] 로 major tick 명시 + minor formatter NullFormatter
        # → "1.25 × 10⁰" 같은 sub-decade 라벨 완전 차단, 1/2/5/10/20/50 만 표시
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_locator(LogLocator(base=10.0, subs=(1.0, 2.0, 5.0)))
            axis.set_minor_locator(LogLocator(base=10.0, subs=tuple(np.arange(2, 10) * 0.1)))
            axis.set_major_formatter(ScalarFormatter())
            axis.set_minor_formatter(NullFormatter())
        ax.tick_params(axis="both", which="major", labelsize=10)
        ax.tick_params(axis="both", which="minor", length=2)

        med_s = float(np.median(sys_q))
        med_b = float(np.median(bern_q))
        diff = ((med_s - med_b) / med_b * 100) if med_b > 0 else 0.0
        n_winning = int(np.sum(sys_q > bern_q))
        n_total = len(sub)
        p = p_by_sel.get(round(sel, 3))

        text = (f"median Δ = {diff:+.1f} %\n"
                f"SYSTEM: {med_s:.3f}  ·  BERNOULLI: {med_b:.3f}\n"
                f"{format_p_value(p)}  ·  SYS 불리 {n_winning}/{n_total}")
        ax.text(
            0.04, 0.96, text, transform=ax.transAxes,
            fontsize=10, va="top", ha="left", linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                      edgecolor="#13289F", linewidth=1.0, alpha=0.96),
        )

        ax.set_xlabel("BERNOULLI Q-error  (log)", fontsize=11, color=COLOR_BERN, fontweight="bold")
        ax.set_ylabel("SYSTEM Q-error  (log)", fontsize=11, color=COLOR_SYS, fontweight="bold")
        ax.set_title(f"selectivity = {sel:.2f}    {sig}",
                     fontsize=12, fontweight="bold", pad=6, color="#13289F")
        ax.grid(True, which="major", alpha=0.30, linewidth=0.5)
        ax.grid(True, which="minor", alpha=0.10, linewidth=0.3)

    plt.tight_layout(pad=1.4)
    out = FIG_DIR / "figure_1_phase4_scatter.png"
    fig.savefig(out, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def generate_vector_c_snippet() -> Path:
    """vector.c 3줄 수정 요약 이미지 (slide 6 용).

    코드 부분(ASCII)은 monospace, 한국어 설명은 Apple SD Gothic Neo 로 렌더.
    """
    fig, ax = plt.subplots(figsize=(12, 7.0))
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 색상 팔레트 (GitHub Dark 유사)
    C_TYPE = "#79c0ff"        # 파일명
    C_COMMENT = "#8b949e"     # 주석
    C_DEFAULT = "#c9d1d9"     # 일반 텍스트
    C_HIGHLIGHT = "#3fb950"   # + / 강조
    C_REMOVE = "#f85149"      # -

    # 코드용(ASCII 전용)
    code_font = {"family": "monospace"}
    # 한국어 혼합용
    kor_font = {"family": ["AppleGothic", "Apple SD Gothic Neo", "Helvetica"]}

    # 각 블록: title_y / before_y / after_y / note_y — line spacing 0.06 (figsize 7.0 기준 line height ≈ 0.42 inch)
    blocks = [
        {
            "title_y": 0.87,  "title": "Pivot A — Hook trigger (line 243)",
            "before_y": 0.80, "before": "if (table_count > 2)",
            "after_y": 0.73,  "after":  "if (table_count >= 1)",
            "note_y": 0.66,   "note":   "2-way join 부터 hook 활성화 → 단일 테이블 query 에도 주입",
        },
        {
            "title_y": 0.57,  "title": "Pivot B — Sampling method (line 889)",
            "before_y": 0.50, "before": "TABLESAMPLE SYSTEM(%f)",
            "after_y": 0.43,  "after":  "TABLESAMPLE BERNOULLI(%f)",
            "note_y": 0.36,   "note":   "블록 단위 SYSTEM → 행 단위 BERNOULLI 로 교체 (skew 내성 +)",
        },
        {
            "title_y": 0.27,  "title": "Pivot C — Stratified sampling branch",
            "before_y": 0.20, "before": "(no stratification logic)",
            "after_y": 0.13,  "after":  "+228 lines: KM20 strata read -> per-stratum BERNOULLI -> HT aggregate",
            "note_y": 0.06,   "note":   "skew 을 명시적으로 활용하는 층화 추정 경로 추가 (합산/분산 추정 포함)",
        },
    ]

    for blk in blocks:
        ax.text(0.015, blk["title_y"], blk["title"],
                fontsize=13, color=C_HIGHLIGHT, fontweight="bold",
                transform=ax.transAxes, **kor_font)
        ax.text(0.03, blk["before_y"], f"-   {blk['before']}",
                fontsize=12, color=C_REMOVE,
                transform=ax.transAxes, **code_font)
        ax.text(0.03, blk["after_y"], f"+   {blk['after']}",
                fontsize=12, color=C_HIGHLIGHT,
                transform=ax.transAxes, **code_font)
        ax.text(0.03, blk["note_y"], f"    # {blk['note']}",
                fontsize=11, color=C_COMMENT, style="italic",
                transform=ax.transAxes, **kor_font)

    # 상단 파일명 배지 (block 1 title 위로 충분한 간격)
    ax.text(
        0.015, 0.95,
        "vector.c  (Exqutor adaptive sampling hook)",
        fontsize=14, color=C_TYPE, fontweight="bold",
        transform=ax.transAxes, **code_font,
    )

    # 하단 footer 제거 — 캡션이 이미 보고서/발표 측에 표시되므로 중복

    out = FIG_DIR / "slide6_vector_c_snippet.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0d1117", pad_inches=0.20)
    plt.close(fig)
    return out


def main() -> int:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig1 = generate_figure_1()
    snip = generate_vector_c_snippet()

    print("DONE")
    print(f"  {fig1}  ({fig1.stat().st_size:,} bytes)")
    print(f"  {snip}  ({snip.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
