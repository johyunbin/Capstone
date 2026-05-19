"""
generate_8m_figures.py — 8M mid-sel 측정 후 figures 자동 생성

산출 figures (저장 위치: experiments/figures/rq1_rq2_w1_sprint/):
  - fig6_8m_midsel_gradient.png — 8M 5sel × KM20 개선 % gradient (1M overlay)
  - fig7_two_level_decomposition_full.png — 1M/SIFT/8M Level 1/2/Total 분해 (8M mid-sel
    은 RAND20 부재로 Level 1/2 hatched 처리)
  - fig8_rq1_cross_dataset_8m_extended.png — 1M/SIFT/8M 의 SYS-BERN Δ% gradient
    (RQ1 의 H1 cross-dataset 패턴, 8M sys20 추가)

Usage:
  python3 experiments/code/local_analysis/generate_8m_figures.py --update
  python3 experiments/code/local_analysis/generate_8m_figures.py --dry-run

본 스크립트는 update_8m_midsel.py 의 데이터 로드 함수를 재사용. 측정 파일 부재 시
graceful skip + 안내 메시지.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
FIGURES_DIR = REPO_ROOT / "experiments" / "figures" / "rq1_rq2_w1_sprint"

sys.path.insert(0, str(Path(__file__).parent))
from update_8m_midsel import (  # noqa: E402
    BASELINE,
    build_gradient_matrix,
    collect_sys20_cells,
    discover_8m_midsel_files,
    load_all_8m_midsel,
)

# RQ1 SYS-BERN 격차 — 정리.md 실험 #1 표에서 (1M/SIFT). Δ% (양수 = BERN 정확).
RQ1_SYS_BERN_BASELINE = {
    "DEEP_1M": {0.50: 12.59, 0.30: 14.05, 0.10: 14.76, 0.05: 12.61, 0.01: 4.66},
    "SIFT_1_5M": {0.50: 14.36, 0.30: 14.85, 0.10: 16.68, 0.05: 17.32, 0.01: 10.27},
}


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def log(msg: str) -> None:
    print(f"[{kst_now()}] {msg}", flush=True)


def setup_matplotlib():
    """matplotlib 한글 폰트 설정."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = "Apple SD Gothic Neo"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["savefig.dpi"] = 150
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3
    return plt


def fig6_8m_midsel_gradient(
    matrix: dict, out_path: Path, plt
) -> bool:
    """8M 의 5 sel KM20 개선 % gradient. 1M 비교 overlay.

    x: selectivity (log scale). y: KM20 mean diff_pct (BERN 대비, 양수 = KM 정확).
    8M (mid-sel 보강 후) + DEEP 1M + SIFT 1.5M 세 라인.
    """
    fig, ax = plt.subplots(figsize=(8, 5.5))
    colors = {"DEEP_1M": "#1f77b4", "SIFT_1_5M": "#d62728", "DEEP_8M": "#2ca02c"}
    labels = {"DEEP_1M": "DEEP 1M", "SIFT_1_5M": "SIFT 1.5M", "DEEP_8M": "DEEP 8M"}

    for ds in ("DEEP_1M", "SIFT_1_5M", "DEEP_8M"):
        cells = matrix.get(ds, {})
        if not cells:
            continue
        sels = sorted(cells.keys())
        kms = [cells[s].km20_diff for s in sels]
        valid = [(s, k) for s, k in zip(sels, kms) if not np.isnan(k)]
        if not valid:
            continue
        vs, vk = zip(*valid)
        ax.plot(
            vs,
            vk,
            marker="o",
            markersize=8,
            linewidth=2,
            color=colors[ds],
            label=labels[ds],
        )
        for s, k in valid:
            ax.annotate(
                f"{k:+.1f}%",
                xy=(s, k),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                color=colors[ds],
            )

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("Selectivity (log scale)")
    ax.set_ylabel("KM20 개선 % (BERN 대비)")
    ax.set_title(
        "Cross-Dataset Selectivity Gradient — KM20 vs BERN\n"
        "(8M mid-sel s=0.10/0.30 보강 후, 5sel × 3 dataset)"
    )
    ax.legend(loc="best", fontsize=10)
    ax.set_xticks([0.01, 0.05, 0.10, 0.30, 0.50])
    ax.set_xticklabels(["1%", "5%", "10%", "30%", "50%"])
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    log(f"  ✓ {out_path.name}")
    return True


def fig7_two_level_decomposition(matrix: dict, out_path: Path, plt) -> bool:
    """1M/SIFT/8M 의 Level 1/Level 2/Total 막대 그림. 8M mid-sel 의 RAND20 부재는
    hatched (사선 패턴) 으로 표시 — 학술적 한계 시각화."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    datasets = [
        ("DEEP_1M", "DEEP 1M"),
        ("SIFT_1_5M", "SIFT 1.5M"),
        ("DEEP_8M", "DEEP 8M (mid-sel 보강)"),
    ]
    for ax, (ds, title) in zip(axes, datasets):
        cells = matrix.get(ds, {})
        sels_sorted = sorted(cells.keys(), reverse=True)
        if not sels_sorted:
            ax.set_title(title + " (데이터 없음)")
            continue
        sel_labels = [f"{s*100:.0f}%" for s in sels_sorted]
        x = np.arange(len(sel_labels))
        width = 0.28

        l1 = [cells[s].rand20_diff for s in sels_sorted]
        kt = [cells[s].km20_diff for s in sels_sorted]
        l2 = [(t - r) if not (np.isnan(t) or np.isnan(r)) else float("nan")
              for t, r in zip(kt, l1)]

        l1_plot = [v if not np.isnan(v) else 0 for v in l1]
        l2_plot = [v if not np.isnan(v) else 0 for v in l2]
        kt_plot = [v if not np.isnan(v) else 0 for v in kt]

        # hatched for missing
        l1_hatch = ["//" if np.isnan(v) else None for v in l1]
        l2_hatch = ["//" if np.isnan(v) else None for v in l2]

        bars1 = ax.bar(x - width, l1_plot, width, label="Level 1 (RAND20)",
                        color="#9ecae1", edgecolor="black", linewidth=0.6)
        bars2 = ax.bar(x, l2_plot, width, label="Level 2 (KM-RAND)",
                        color="#fc9272", edgecolor="black", linewidth=0.6)
        bars3 = ax.bar(x + width, kt_plot, width, label="Total (KM20)",
                        color="#74c476", edgecolor="black", linewidth=0.6)

        # hatched 표시
        for b, h in zip(bars1, l1_hatch):
            if h:
                b.set_hatch(h)
                b.set_color("#dddddd")
        for b, h in zip(bars2, l2_hatch):
            if h:
                b.set_hatch(h)
                b.set_color("#dddddd")

        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(sel_labels)
        ax.set_xlabel("Selectivity")
        ax.set_title(title)
        if ax is axes[0]:
            ax.set_ylabel("개선 % (BERN 대비, 양수 = stratified 정확)")
        if ax is axes[-1]:
            ax.legend(loc="best", fontsize=8)

    fig.suptitle(
        "Two-Level Decomposition — Level 1 (비례 배분) + Level 2 (공간 인식) = Total\n"
        "(8M mid-sel 의 hatched 막대는 RAND20 미측정 영역)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    log(f"  ✓ {out_path.name}")
    return True


def fig8_rq1_cross_dataset_extended(
    sys20_8m: dict, out_path: Path, plt
) -> bool:
    """RQ1 cross-dataset SYS-BERN 격차 gradient. 1M/SIFT 는 baseline, 8M 은 mid-sel
    의 sys20 cell 추가 (hatch 로 부분 측정 표시).

    측정 파일 부재로 sys20_8m 비어있으면 1M/SIFT 만 그림.
    """
    fig, ax = plt.subplots(figsize=(8, 5.5))
    colors = {"DEEP_1M": "#1f77b4", "SIFT_1_5M": "#d62728", "DEEP_8M": "#2ca02c"}
    labels = {"DEEP_1M": "DEEP 1M", "SIFT_1_5M": "SIFT 1.5M", "DEEP_8M": "DEEP 8M (mid-sel)"}

    for ds in ("DEEP_1M", "SIFT_1_5M"):
        baseline = RQ1_SYS_BERN_BASELINE[ds]
        sels = sorted(baseline.keys())
        ys = [baseline[s] for s in sels]
        ax.plot(
            sels,
            ys,
            marker="o",
            markersize=8,
            linewidth=2,
            color=colors[ds],
            label=labels[ds],
        )

    if sys20_8m:
        # sys20 의 diff_pct 부호: (mb-ma)/mb. measure.py 정의에서 ma=system, mb=bern.
        # → mean<0 면 SYS 가 BERN 보다 부정확 (= H1 일관). 절대값 비교 위해 부호 반전.
        sels_8m = sorted(sys20_8m.keys())
        ys_8m = [-sys20_8m[s].mean_diff_pct for s in sels_8m]  # H1 narrative 와 일관
        ax.plot(
            sels_8m,
            ys_8m,
            marker="s",
            markersize=10,
            linewidth=2.5,
            color=colors["DEEP_8M"],
            label=labels["DEEP_8M"],
            linestyle="--",
        )
        for s, y in zip(sels_8m, ys_8m):
            ax.annotate(
                f"{y:+.1f}%",
                xy=(s, y),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color=colors["DEEP_8M"],
                fontweight="bold",
            )

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("Selectivity (log scale)")
    ax.set_ylabel("SYSTEM-BERN Δ% (양수 = BERN 정확)")
    ax.set_title(
        "RQ1 H1 — Cross-Dataset SYSTEM vs BERN Gradient\n"
        "(skew 데이터일수록 block sampling 이 row sampling 대비 부정확)"
    )
    ax.legend(loc="best", fontsize=10)
    ax.set_xticks([0.01, 0.05, 0.10, 0.30, 0.50])
    ax.set_xticklabels(["1%", "5%", "10%", "30%", "50%"])
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    log(f"  ✓ {out_path.name}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="8M mid-sel 측정 후 figures 자동 생성")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--update", action="store_true", help="figures 생성 (기본)")
    g.add_argument("--dry-run", action="store_true", help="데이터 로드만, figures 저장 X")
    parser.add_argument(
        "--out-dir",
        default=str(FIGURES_DIR),
        help="figures 저장 경로",
    )
    args = parser.parse_args(argv)
    if not (args.update or args.dry_run):
        args.update = True

    log("Phase 1 — 8M mid-sel 측정 파일 탐색 + 로드")
    files = discover_8m_midsel_files()
    if not files:
        log("  ! 측정 파일 미발견. 메인 세션 push 후 재실행 필요.")
        log("  ! 예상 파일: experiments/results/.../phase7_8m_midsel.parquet + meta.json")
        return 1
    cells = load_all_8m_midsel(files)
    if not cells:
        log("  ! cell 로드 실패")
        return 1
    log(f"  ✓ {len(cells)} cell 로드")

    log("Phase 2 — Matrix + sys20 분리")
    matrix = build_gradient_matrix(cells)
    sys20_8m = collect_sys20_cells(cells)
    log(f"  matrix: {sum(len(v) for v in matrix.values())} (sel, ds) 점")
    log(f"  sys20 8M: {len(sys20_8m)} sel")

    if args.dry_run:
        log("[dry-run] figures 생성 skip")
        return 0

    log("Phase 3 — figures 저장")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plt = setup_matplotlib()

    fig6_8m_midsel_gradient(matrix, out_dir / "fig6_8m_midsel_gradient.png", plt)
    fig7_two_level_decomposition(matrix, out_dir / "fig7_two_level_decomposition_full.png", plt)
    fig8_rq1_cross_dataset_extended(sys20_8m, out_dir / "fig8_rq1_cross_dataset_8m_extended.png", plt)

    log(f"  → {out_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
