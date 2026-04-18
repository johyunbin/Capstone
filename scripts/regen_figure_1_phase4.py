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
from matplotlib.ticker import LogLocator


REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "experiments" / "results" / "rq1_motivation"
FIG_DIR = REPO_ROOT / "experiments" / "figures" / "rq1_motivation"

# 표시할 selectivity (s=0.001 tie, s=0.010 non-significant 제외)
KEEP_SELECTIVITIES = [0.05, 0.10, 0.30, 0.50]

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
    # (paired Wilcoxon, alternative="greater" — SYSTEM 쪽 q-error 가 더 크다는 가설)
    p_by_sel = {round(r["selectivity"], 3): r["p_greater"] for r in compare}

    # 표시할 selectivity 만 필터
    sels_present = sorted(merged["selectivity"].unique())
    sels = [s for s in sels_present if round(s, 3) in [round(x, 3) for x in KEEP_SELECTIVITIES]]
    if not sels:
        raise RuntimeError("No matching selectivities in parquet data")

    n_panels = len(sels)
    fig, axes = plt.subplots(1, n_panels, figsize=(4.2 * n_panels, 4.4))
    if n_panels == 1:
        axes = [axes]

    for idx, sel in enumerate(sels):
        ax = axes[idx]
        sub = merged[merged["selectivity"] == sel]
        sys_q = sub["q_error_sys"].values
        bern_q = sub["q_error_bern"].values

        # Scatter: x=BERNOULLI, y=SYSTEM.  Points above diag → SYSTEM worse.
        ax.scatter(
            bern_q,
            sys_q,
            s=28,
            alpha=0.6,
            edgecolors=COLOR_SYS,
            facecolors="none",
            linewidths=1.1,
            label=None,
        )

        # y=x 대각선
        lo = min(bern_q.min(), sys_q.min(), 1.0)
        hi = max(bern_q.max(), sys_q.max())
        ax.plot([lo, hi], [lo, hi], "k--", lw=0.9, alpha=0.55, zorder=0)

        ax.set_xscale("log")
        ax.set_yscale("log")
        # LogLocator numticks=3 으로 틱 개수 제한 → 겹침 방지
        ax.xaxis.set_major_locator(LogLocator(numticks=3))
        ax.yaxis.set_major_locator(LogLocator(numticks=3))
        ax.tick_params(labelsize=10)

        ax.set_xlabel("BERNOULLI Q-error", fontsize=12, color=COLOR_BERN, fontweight="bold")
        if idx == 0:
            ax.set_ylabel("SYSTEM Q-error", fontsize=12, color=COLOR_SYS, fontweight="bold")
        else:
            ax.set_ylabel("")

        p = p_by_sel.get(round(sel, 3))
        ax.set_title(f"s = {sel:.2f} ({format_p_value(p)})", fontsize=14, pad=10)

        # Median 주석 (작게)
        med_s = float(np.median(sys_q))
        med_b = float(np.median(bern_q))
        diff = ((med_s - med_b) / med_b * 100) if med_b > 0 else 0
        ax.text(
            0.04,
            0.96,
            f"median Δ = {diff:+.1f}%\n(SYS {med_s:.2f} / BERN {med_b:.2f})",
            transform=ax.transAxes,
            fontsize=9,
            va="top",
            ha="left",
            bbox=dict(
                facecolor="white",
                edgecolor="#bbbbbb",
                alpha=0.88,
                boxstyle="round,pad=0.3",
            ),
        )

        ax.grid(True, which="major", alpha=0.25, linestyle=":", linewidth=0.7)

    fig.suptitle(
        "SYSTEM vs BERNOULLI paired Q-error — 유의 구간 4 panel (s=0.001 tie, s=0.010 n.s. 제외)",
        fontsize=13,
        y=1.02,
    )
    plt.tight_layout()
    out = FIG_DIR / "figure_1_phase4_scatter.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def generate_vector_c_snippet() -> Path:
    """vector.c 3줄 수정 요약 이미지 (slide 6 용).

    코드 부분(ASCII)은 monospace, 한국어 설명은 Apple SD Gothic Neo 로 렌더.
    """
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")
    ax.axis("off")

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

    # 각 블록: (y, title_kor, before, after, note_kor)
    blocks = [
        (
            0.88,
            "Pivot A — Hook trigger (line 243)",
            "if (table_count > 2)",
            "if (table_count >= 1)",
            "2-way join 부터 hook 활성화 → 단일 테이블 query 에도 주입",
        ),
        (
            0.58,
            "Pivot B — Sampling method (line 889)",
            "TABLESAMPLE SYSTEM(%f)",
            "TABLESAMPLE BERNOULLI(%f)",
            "블록 단위 SYSTEM → 행 단위 BERNOULLI 로 교체 (skew 내성 +)",
        ),
        (
            0.28,
            "Pivot C — Stratified sampling branch",
            "(no stratification logic)",
            "+228 lines: KM20 strata read -> per-stratum BERNOULLI -> HT aggregate",
            "skew 을 명시적으로 활용하는 층화 추정 경로 추가 (합산/분산 추정 포함)",
        ),
    ]

    for y, title, before, after, note in blocks:
        # 제목 (한글 포함 → kor_font)
        ax.text(
            0.015, y + 0.06,
            title,
            fontsize=12,
            color=C_HIGHLIGHT,
            fontweight="bold",
            transform=ax.transAxes,
            **kor_font,
        )
        # Before 라인 (ASCII → monospace)
        ax.text(
            0.03, y + 0.01,
            f"-   {before}",
            fontsize=11,
            color=C_REMOVE,
            transform=ax.transAxes,
            **code_font,
        )
        # After 라인 (ASCII → monospace)
        ax.text(
            0.03, y - 0.04,
            f"+   {after}",
            fontsize=11,
            color=C_HIGHLIGHT,
            transform=ax.transAxes,
            **code_font,
        )
        # 주석 (한글 포함 → kor_font)
        ax.text(
            0.03, y - 0.09,
            f"    # {note}",
            fontsize=10,
            color=C_COMMENT,
            style="italic",
            transform=ax.transAxes,
            **kor_font,
        )

    # 상단 파일명 배지
    ax.text(
        0.015, 0.98,
        "vector.c  (Exqutor adaptive sampling hook)",
        fontsize=13,
        color=C_TYPE,
        fontweight="bold",
        transform=ax.transAxes,
        **code_font,
    )
    # 하단 캡션 (한글 → kor_font)
    ax.text(
        0.015, 0.02,
        "3 surgical edits — SYSTEM 의 block skew bias 제거 + 층화 경로 활성화",
        fontsize=10,
        color=C_DEFAULT,
        transform=ax.transAxes,
        **kor_font,
    )

    out = FIG_DIR / "slide6_vector_c_snippet.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#0d1117")
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
