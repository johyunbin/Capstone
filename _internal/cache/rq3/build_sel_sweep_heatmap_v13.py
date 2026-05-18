#!/usr/bin/env python3
"""
build_sel_sweep_heatmap_v13.py — F8 selectivity sweep heatmap (v13 3-way 데이터)

목적
----
selectivity sweep 측정의 paired Δ% = (CaseB - B1) / B1 × 100 을 heatmap 으로
시각화. build_sel_sweep_heatmap.py (v12 데이터) 의 v13 재생성 버전.

v12 대비 변경점
---------------
1. 입력을 v13 3-way matched parquet (paired_delta_v13) 로 교체.
2. comparison == "CaseB_vs_B1" 행만 사용 (결합 실험군 vs 대조군).
   v13 paired_delta 는 CaseA_vs_B1 / CaseB_vs_B1 / CaseA_vs_CaseB 3 comparison 포함.
3. K=20 default 한정 — (cell, method, sel) 당 단일 값으로 K-평균 artifact 제거.
   v13 의 K=10/30 은 6 K-granularity cell × sel=0.01 에만 존재 (별도 분석).
4. cell 유형은 v13 parquet 의 type_label 컬럼 직접 사용 (v12 의 cell 이름 regex
   추론 infer_type 폐기).
5. method 열 순서·강조는 hardcode 가 아니라 v13 CaseB_vs_B1 정확도(mean Δ%)
   ranking 으로 계산 (v12 의 METHOD_ORDER / PARETO_TOP5 상수는 v13 에서 stale).

heatmap 구성
------------
  rows  : 측정 cell (Type 1 → 4b 그룹 정렬)
  cols  : 16 sample selection method (v13 정확도 상위 → 하위)
  color : paired Δ% (RdBu_r diverging, midpoint 0)
          음수 = 파랑 = 결합 실험군 우위 / 양수 = 빨강 = 악화
  panel : 3 panel side-by-side — sel = 0.001 / 0.01 / 0.10

input
-----
_internal/cache/rq3/paired_delta_v13.parquet

output
------
experiments/figures/paper_exact_v13/F8_sel_sweep_heatmap.{png,pdf}
experiments/figures/paper_exact_v13/F8_sel_sweep_heatmap_data.csv

usage
-----
  python3 build_sel_sweep_heatmap_v13.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ============================================================
# 경로 + 상수
# ============================================================
REPO_ROOT = Path(__file__).resolve().parents[3]
CACHE_DIR = REPO_ROOT / "_internal" / "cache" / "rq3"
OUT_DIR = REPO_ROOT / "experiments" / "figures" / "paper_exact_v13"

KOREAN_FONT = "Apple SD Gothic Neo"
plt.rcParams["font.family"] = KOREAN_FONT
plt.rcParams["axes.unicode_minus"] = False

SEL_VALUES = [0.001, 0.01, 0.10]   # 측정 완료 3 값
K_DEFAULT = 20                     # paper default — heatmap 단일 K slice
N_HIGHLIGHT = 5                    # 정확도 상위 N method 열 강조

# cell type 그룹 stripe 색 (v13 type_label 기준)
TYPE_COLORS = {
    "Type 1":  "#e8f1fa",
    "Type 2":  "#cfe2f3",
    "Type 3":  "#9fc5e8",
    "Type 4a": "#f4cccc",
    "Type 4b": "#e06666",
}
TYPE_RANK = {"Type 1": 0, "Type 2": 1, "Type 3": 2, "Type 4a": 3, "Type 4b": 4}


# ============================================================
# data loading
# ============================================================
def load_paired_delta() -> pd.DataFrame:
    """paired_delta_v13.parquet 로드 후 comparison == CaseB_vs_B1 한정."""
    path = CACHE_DIR / "paired_delta_v13.parquet"
    if not path.exists():
        raise FileNotFoundError(f"  {path} 부재. paired_delta_v13.py 선행 필요.")
    df = pd.read_parquet(path)
    print(f"  loaded {path.name}  ({len(df)} rows)")
    d = df[df["comparison"] == "CaseB_vs_B1"].copy()
    if d.empty:
        raise RuntimeError("  comparison == 'CaseB_vs_B1' 행 0건.")
    print(f"  CaseB_vs_B1 한정: {len(d)} rows  ({d['cell'].nunique()} cell · "
          f"{d['method'].nunique()} method)")
    return d


# ============================================================
# method 열 순서 — v13 CaseB_vs_B1 정확도(mean Δ%) ranking
# ============================================================
def compute_method_order(d: pd.DataFrame):
    """K 전체 CaseB_vs_B1 median Δ% 오름차순 — 정확도 상위 method 가 좌측.

    method ranking 은 안정적 method 속성이므로 K 전체(v13_summary §4.4 기준)로
    계산한다. 측정별 Δ% 의 mean 은 극단 cell(minibatch_partial +1043% 등)에
    끌리므로 robust 한 median 을 ranking 기준으로 쓴다 — heatmap 셀 값(아래)이
    대부분 음수인 method 가 mean 으로는 최하위에 밀리는 시각 모순을 피한다.
    heatmap 셀 값 자체는 별도로 K=20 만 표시한다.
    """
    rank = (d.groupby("method")["delta_pct_mean"].median()
             .sort_values())
    order = rank.index.tolist()
    paradigm = (d[["method", "paradigm"]].drop_duplicates()
                 .set_index("method")["paradigm"].to_dict())
    return order, paradigm, rank


# ============================================================
# heatmap matrix — cell × method (sel 별, K=20 default)
# ============================================================
def build_matrices(d: pd.DataFrame, method_order, cell_type):
    """sel 별 cell × method paired Δ% matrix. K=20 한정.

    cell 순서 = Type 그룹(1→4b) → cell 이름.
    """
    k20 = d[d["K"] == K_DEFAULT].copy()
    print(f"  K={K_DEFAULT} 한정: {len(k20)} rows")

    # cell 정렬: Type rank → cell 이름
    cells = sorted(k20["cell"].unique(),
                   key=lambda c: (TYPE_RANK.get(cell_type.get(c, ""), 9), c))

    matrices = {}
    for sel in SEL_VALUES:
        sub = k20[np.isclose(k20["sel"], sel)]
        M = sub.pivot_table(index="cell", columns="method",
                            values="delta_pct_mean", aggfunc="mean")
        present_cells = [c for c in cells if c in M.index]
        present_methods = [m for m in method_order if m in M.columns]
        M = M.reindex(index=present_cells, columns=present_methods)
        matrices[sel] = M
    return matrices, cells


# ============================================================
# 셀 annotation 포맷 — 극단 outlier 는 정수, 그 외 소수 1
# ============================================================
def fmt_cell(v) -> str:
    if pd.isna(v):
        return ""
    if abs(v) >= 100:
        return f"{v:.0f}"
    return f"{v:.1f}"


def annot_frame(M: pd.DataFrame) -> pd.DataFrame:
    out = M.copy().astype(object)
    for c in out.columns:
        out[c] = out[c].map(fmt_cell)
    return out


# ============================================================
# plotting
# ============================================================
def make_heatmap(matrices: dict, cell_type: dict, method_paradigm: dict,
                 highlight: list, out_png: Path, out_pdf: Path):
    n_panel = len(SEL_VALUES)
    fig, axes = plt.subplots(1, n_panel, figsize=(7.0 * n_panel, 11),
                             gridspec_kw={"wspace": 0.30})
    if n_panel == 1:
        axes = [axes]

    # color scale 공통 — 95p of |Δ%|, 최소 5
    all_vals = pd.concat([m.stack() for m in matrices.values()])
    vabs = float(np.nanpercentile(np.abs(all_vals), 95))
    vabs = max(vabs, 5.0)
    vmin, vmax = -vabs, vabs

    for ax_i, sel in enumerate(SEL_VALUES):
        ax = axes[ax_i]
        M = matrices[sel]
        method_labels = [f"{m}\n({method_paradigm.get(m, '?')})"
                         for m in M.columns]

        sns.heatmap(
            M, ax=ax, cmap="RdBu_r", center=0, vmin=vmin, vmax=vmax,
            annot=annot_frame(M), fmt="",
            annot_kws={"fontsize": 6.5, "color": "black"},
            cbar=(ax_i == n_panel - 1),
            cbar_kws=dict(
                label=("paired Δ% = (CaseB - B1) / B1 × 100\n"
                       "(음수 = 결합 실험군 정확도 개선)"),
                shrink=0.80, pad=0.02),
            linewidths=0.4, linecolor="#dddddd",
            xticklabels=method_labels, yticklabels=list(M.index),
            square=False)

        # cell 단위 better-rate (panel 소제목 보강)
        flat = M.values.flatten()
        flat = flat[~np.isnan(flat)]
        better = int((flat < 0).sum())
        rate = better / len(flat) * 100 if len(flat) else 0.0
        ax.set_title(f"selectivity = {sel}\nCaseB 우위 {better}/{len(flat)} "
                     f"= {rate:.1f}%",
                     fontsize=12, fontweight="bold",
                     fontfamily=KOREAN_FONT, pad=10)
        ax.set_xlabel("sample selection method (paradigm)",
                      fontsize=11, fontfamily=KOREAN_FONT)
        ax.set_ylabel("측정 cell  (Type 1 → 4b)" if ax_i == 0 else "",
                      fontsize=11, fontfamily=KOREAN_FONT)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right",
                           fontsize=8.5)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8.5)

        # row Type 그룹 stripe
        cells = list(M.index)
        for r_i, cell in enumerate(cells):
            tg = cell_type.get(cell, "")
            ax.add_patch(plt.Rectangle((-0.85, r_i), 0.78, 1,
                                       facecolor=TYPE_COLORS.get(tg, "#eeeeee"),
                                       edgecolor="black", linewidth=0.3,
                                       clip_on=False, zorder=2))
            prev = cell_type.get(cells[r_i - 1], "") if r_i > 0 else None
            if tg != prev:
                ax.text(-0.46, r_i + 0.5, tg, ha="center", va="center",
                        fontsize=6.5, fontfamily=KOREAN_FONT,
                        fontweight="bold", rotation=90, clip_on=False)

        # 정확도 상위 N method column frame
        for c_i, m in enumerate(M.columns):
            if m in highlight:
                ax.add_patch(plt.Rectangle(
                    (c_i + 0.02, 0.02), 0.96, len(cells) - 0.04,
                    fill=False, edgecolor="#d62728", linewidth=2.5,
                    clip_on=False, zorder=10))

    fig.suptitle("F8 (v13) — selectivity sweep paired Δ%, 결합 실험군(CaseB) "
                 "vs 대조군(B1)  ·  K=20 default  "
                 "(rows = 측정 cell, cols = 16 method × 3 sel panel)",
                 fontsize=14, fontweight="bold",
                 fontfamily=KOREAN_FONT, y=0.995)

    hl = " · ".join(highlight)
    fig.text(0.5, 0.005,
             f"data: paired_delta_v13 — CaseB_vs_B1 · K=20 · 측정당 10-trial "
             f"paired  |  붉은 frame = v13 정확도 상위 {len(highlight)} method "
             f"({hl})  |  파랑 = 결합 개선, 빨강 = 악화",
             ha="center", fontsize=8.5, color="#444444",
             fontfamily=KOREAN_FONT)

    plt.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_png}")
    print(f"  wrote {out_pdf}")


# ============================================================
# main
# ============================================================
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    d = load_paired_delta()
    cell_type = (d[["cell", "type_label"]].drop_duplicates()
                  .set_index("cell")["type_label"].to_dict())
    method_order, method_paradigm, rank = compute_method_order(d)
    highlight = method_order[:N_HIGHLIGHT]

    print("\n  method 정확도 ranking (CaseB_vs_B1 median Δ%, K 전체):")
    for i, m in enumerate(method_order, 1):
        mark = " ★강조" if m in highlight else ""
        print(f"    {i:2d}. {m:22s} {method_paradigm.get(m,'?')}  "
              f"{rank[m]:+.2f}%{mark}")

    matrices, cell_order = build_matrices(d, method_order, cell_type)

    # sanity
    print()
    for sel in SEL_VALUES:
        M = matrices[sel]
        filled = int(M.notna().values.sum())
        print(f"  sel={sel}: matrix {M.shape[0]} cell × {M.shape[1]} method, "
              f"{filled}/{M.size} filled ({filled / max(M.size, 1) * 100:.0f}%)")

    # CSV (long format)
    rows = []
    for sel, M in matrices.items():
        for cell in M.index:
            for method in M.columns:
                rows.append({"sel": sel, "cell": cell,
                             "type_label": cell_type.get(cell, ""),
                             "method": method,
                             "paradigm": method_paradigm.get(method, "?"),
                             "delta_pct": M.at[cell, method]})
    csv_df = pd.DataFrame(rows)

    out_png = OUT_DIR / "F8_sel_sweep_heatmap.png"
    out_pdf = OUT_DIR / "F8_sel_sweep_heatmap.pdf"
    out_csv = OUT_DIR / "F8_sel_sweep_heatmap_data.csv"
    csv_df.to_csv(out_csv, index=False)
    print(f"  wrote {out_csv}")

    make_heatmap(matrices, cell_type, method_paradigm, highlight,
                 out_png, out_pdf)


if __name__ == "__main__":
    main()
