#!/usr/bin/env python3
"""
build_sel_sweep_heatmap.py — Phase 5 selectivity sweep heatmap (F8)

목적
----
selectivity sweep 측정의 paired Δ% = (CaseB - B1) / B1 × 100 을
heatmap 으로 시각화. 박세은 framing "sample selection vs random
Bernoulli paired Q-error Δ%" 그대로.

heatmap 구성
------------
  rows  : 측정 cell (Type 1-4 그룹 정렬)
  cols  : 16 sample selection method (Pareto Top 5 선두 + paradigm 순)
  color : paired Δ% (RdBu_r diverging, midpoint 0)
          음수 = 파랑 = sample selection 우위 / 양수 = 빨강 = 악화
  panel : 3 panel side-by-side — sel = 0.001 / 0.01 / 0.10

입력 데이터 (실측)
-----------------
paired_delta_v12.parquet 의 delta_pct_mean 컬럼 직접 사용.
K_norm=20 (default K) + exact pairing 한정. 3 sel 값 모두 측정 완료
(sel=0.001 24 cell, sel=0.01 23 cell, sel=0.10 23 cell × 16 method,
matrix 100% dense — mock 불필요).

input
-----
_internal/cache/rq3/paired_delta_v12.parquet
fallback: aggregated_v12_dryrun.parquet (--dry-run, paired Δ% 재계산)

output
------
experiments/figures/paper_exact_v8/F8_sel_sweep_heatmap.png  (300 DPI)
experiments/figures/paper_exact_v8/F8_sel_sweep_heatmap.pdf
experiments/figures/paper_exact_v8/F8_sel_sweep_heatmap_data.csv

usage
-----
  python3 build_sel_sweep_heatmap.py             # paired_delta_v12
  python3 build_sel_sweep_heatmap.py --dry-run   # dryrun parquet
"""
import argparse
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
OUT_DIR = REPO_ROOT / "experiments" / "figures" / "paper_exact_v8"

KOREAN_FONT = "Apple SD Gothic Neo"
plt.rcParams["font.family"] = KOREAN_FONT
plt.rcParams["axes.unicode_minus"] = False

SEL_VALUES = [0.001, 0.01, 0.10]   # 측정 완료 3 값

# method column 순서 — Pareto Top 5 선두, 이후 paradigm 묶음
PARETO_TOP5 = ["sparse_rp", "chao_weighted", "hilbert_real",
               "hyperloglog", "pca1d"]
METHOD_ORDER = PARETO_TOP5 + [
    "zorder_morton", "skilling_hilbert", "faiss_ivf",   # P2 잔여
    "ica_fastica", "rsvd",                              # P4 잔여
    "cum_sqrtf", "lavallee_hidiroglou",                 # P5
    "rabitq_strat", "mhist2",                           # P6
    "minibatch_partial", "gmm",                         # P1
]

METHOD_PARADIGM = {
    "sparse_rp": "P4", "chao_weighted": "P3", "hilbert_real": "P2",
    "hyperloglog": "P9", "pca1d": "P4",
    "zorder_morton": "P2", "skilling_hilbert": "P2", "faiss_ivf": "P2",
    "ica_fastica": "P4", "rsvd": "P4",
    "cum_sqrtf": "P5", "lavallee_hidiroglou": "P5",
    "rabitq_strat": "P6", "mhist2": "P6",
    "minibatch_partial": "P1", "gmm": "P1",
}

# cell type 그룹 stripe 색
TYPE_COLORS = {
    "Type 1":  "#e8f1fa",
    "Type 2":  "#cfe2f3",
    "Type 3":  "#9fc5e8",
    "Type 4a": "#f4cccc",
    "Type 4b": "#e06666",
    "기타":     "#eeeeee",
}


# ============================================================
# data loading
# ============================================================
def load_paired_delta(dry_run: bool) -> pd.DataFrame:
    """paired_delta_v12.parquet 로드. --dry-run 시 dryrun aggregated 에서 재계산."""
    if dry_run:
        dry = CACHE_DIR / "aggregated_v12_dryrun.parquet"
        if not dry.exists():
            raise FileNotFoundError(f"  {dry} 부재.")
        print(f"  loaded {dry.name} — paired Δ% 재계산")
        return _recompute_from_aggregated(pd.read_parquet(dry))

    path = CACHE_DIR / "paired_delta_v12.parquet"
    if not path.exists():
        raise FileNotFoundError(f"  {path} 부재. paired_delta_v12.py 선행 필요.")
    print(f"  loaded {path.name}")
    return pd.read_parquet(path)


def _recompute_from_aggregated(agg: pd.DataFrame) -> pd.DataFrame:
    """dry-run fallback — aggregated 에서 (CaseB - B1)/B1 paired Δ% 재계산."""
    b1 = (agg[agg["mode"] == "B1"][["cell", "sel", "qe_trim"]]
          .rename(columns={"qe_trim": "b1_qe_mean"}))
    cb = agg[(agg["mode"] == "CaseB") & agg["K"].isna() & agg["alpha"].isna()]
    merged = cb.merge(b1, on=["cell", "sel"], how="left").dropna(subset=["b1_qe_mean"])
    merged["delta_pct_mean"] = ((merged["qe_trim"] - merged["b1_qe_mean"])
                                / merged["b1_qe_mean"] * 100.0)
    merged["K_norm"] = 20
    merged["pairing"] = "exact"
    return merged


# ============================================================
# cell type 그룹 추론 (cell 이름 패턴)
# ============================================================
def infer_type(cell: str) -> str:
    """cell 이름에서 Type 1-4 그룹 추론.

    sf=1 → Type 1, sf=10 → Type 2, sf=100 / A1 → Type 3,
    concat/multi → Type 4a (단일 차원) / 4b (864d). 추론 불가 → 기타.
    """
    c = cell.lower()
    if "concat" in c:
        return "Type 4b" if ("sf100" in c) else "Type 4a"
    if c.startswith("a2-fig") or "multi" in c or "+" in c:
        return "Type 4a"
    if "sf100" in c or c.startswith("a1-"):
        return "Type 3"
    if "sf10" in c:
        return "Type 2"
    if "sf1" in c:
        return "Type 1"
    return "기타"


TYPE_RANK = {"Type 1": 0, "Type 2": 1, "Type 3": 2,
             "Type 4a": 3, "Type 4b": 4, "기타": 5}


# ============================================================
# heatmap matrix — cell × method (sel 별)
# ============================================================
def build_matrices(delta: pd.DataFrame):
    """sel 별 cell × method paired Δ% matrix. cell 순서 = Type 그룹 정렬.

    K_norm=20 + exact pairing 한정. 16 method 만 사용.
    """
    d = delta[(delta.get("K_norm", 20) == 20)
              & (delta.get("pairing", "exact") == "exact")].copy()
    d = d[d["method"].isin(METHOD_ORDER)]

    # cell 정렬: Type 그룹 → cell 이름
    d["type_group"] = d["cell"].map(infer_type)
    cell_order = (d[["cell", "type_group"]].drop_duplicates()
                  .assign(rank=lambda x: x["type_group"].map(TYPE_RANK))
                  .sort_values(["rank", "cell"])["cell"].tolist())

    matrices = {}
    for sel in SEL_VALUES:
        sub = d[np.isclose(d["sel"], sel)]
        M = sub.pivot_table(index="cell", columns="method",
                            values="delta_pct_mean", aggfunc="mean")
        present_cells = [c for c in cell_order if c in M.index]
        present_methods = [m for m in METHOD_ORDER if m in M.columns]
        M = M.reindex(index=present_cells, columns=present_methods)
        matrices[sel] = M
    return matrices, cell_order


# ============================================================
# plotting
# ============================================================
def make_heatmap(matrices: dict, out_png: Path, out_pdf: Path):
    n_panel = len(SEL_VALUES)
    fig, axes = plt.subplots(1, n_panel, figsize=(7.0 * n_panel, 11),
                             gridspec_kw={"wspace": 0.30})
    if n_panel == 1:
        axes = [axes]

    # color scale 공통 — 95p of |Δ%|
    all_vals = pd.concat([m.stack() for m in matrices.values()])
    vabs = float(np.nanpercentile(np.abs(all_vals), 95))
    vabs = max(vabs, 5.0)
    vmin, vmax = -vabs, vabs

    for ax_i, sel in enumerate(SEL_VALUES):
        ax = axes[ax_i]
        M = matrices[sel]
        method_labels = [f"{m}\n({METHOD_PARADIGM.get(m, '?')})"
                         for m in M.columns]

        sns.heatmap(
            M, ax=ax, cmap="RdBu_r", center=0, vmin=vmin, vmax=vmax,
            annot=True, fmt=".1f",
            annot_kws={"fontsize": 6.5, "color": "black"},
            cbar=(ax_i == n_panel - 1),
            cbar_kws=dict(
                label=("paired Δ% = (CaseB - B1) / B1 × 100\n"
                       "(음수 = sample selection 정확도 개선)"),
                shrink=0.80, pad=0.02),
            linewidths=0.4, linecolor="#dddddd",
            xticklabels=method_labels, yticklabels=list(M.index),
            square=False)

        # cell 단위 better-rate (panel 소제목 보강)
        flat = M.values.flatten()
        flat = flat[~np.isnan(flat)]
        better = int((flat < 0).sum())
        rate = better / len(flat) * 100 if len(flat) else 0.0
        ax.set_title(f"selectivity = {sel}\n실험군 우위 {better}/{len(flat)} "
                     f"= {rate:.1f}%",
                     fontsize=12, fontweight="bold",
                     fontfamily=KOREAN_FONT, pad=10)
        ax.set_xlabel("sample selection method (paradigm)",
                      fontsize=11, fontfamily=KOREAN_FONT)
        ax.set_ylabel("측정 cell  (Type 1 → 4)" if ax_i == 0 else "",
                      fontsize=11, fontfamily=KOREAN_FONT)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right",
                           fontsize=8.5)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8.5)

        # row Type 그룹 stripe
        cells = list(M.index)
        for r_i, cell in enumerate(cells):
            tg = infer_type(cell)
            ax.add_patch(plt.Rectangle((-0.85, r_i), 0.78, 1,
                                       facecolor=TYPE_COLORS.get(tg, "#eeeeee"),
                                       edgecolor="black", linewidth=0.3,
                                       clip_on=False, zorder=2))
            prev = infer_type(cells[r_i - 1]) if r_i > 0 else None
            if tg != prev:
                ax.text(-0.46, r_i + 0.5, tg, ha="center", va="center",
                        fontsize=6.5, fontfamily=KOREAN_FONT,
                        fontweight="bold", rotation=90, clip_on=False)

        # Pareto Top 5 column frame
        for c_i, m in enumerate(M.columns):
            if m in PARETO_TOP5:
                ax.add_patch(plt.Rectangle(
                    (c_i + 0.02, 0.02), 0.96, len(cells) - 0.04,
                    fill=False, edgecolor="#d62728", linewidth=2.5,
                    clip_on=False, zorder=10))

    fig.suptitle("F8 — selectivity sweep paired Δ%  "
                 "(rows = 측정 cell, cols = 16 method × 3 sel panel)",
                 fontsize=14, fontweight="bold",
                 fontfamily=KOREAN_FONT, y=0.995)

    fig.text(0.5, 0.005,
             "data: paired_delta_v12 실측 (K_norm=20, exact pairing)  |  "
             "붉은 frame = Pareto Top 5  |  "
             "파랑 = sample selection 개선, 빨강 = 악화",
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="aggregated_v12_dryrun.parquet 에서 재계산")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    delta = load_paired_delta(args.dry_run)
    matrices, cell_order = build_matrices(delta)

    # sanity
    for sel in SEL_VALUES:
        M = matrices[sel]
        filled = int(M.notna().values.sum())
        print(f"  sel={sel}: matrix {M.shape[0]} cell × {M.shape[1]} method, "
              f"{filled}/{M.size} filled ({filled / max(M.size,1) * 100:.0f}%)")

    # CSV (long format)
    rows = []
    for sel, M in matrices.items():
        for cell in M.index:
            for method in M.columns:
                rows.append({"sel": sel, "cell": cell,
                             "type_group": infer_type(cell), "method": method,
                             "paradigm": METHOD_PARADIGM.get(method, "?"),
                             "delta_pct": M.at[cell, method]})
    csv_df = pd.DataFrame(rows)

    suffix = "_dryrun" if args.dry_run else ""
    out_png = OUT_DIR / f"F8_sel_sweep_heatmap{suffix}.png"
    out_pdf = OUT_DIR / f"F8_sel_sweep_heatmap{suffix}.pdf"
    out_csv = OUT_DIR / f"F8_sel_sweep_heatmap{suffix}_data.csv"
    csv_df.to_csv(out_csv, index=False)
    print(f"  wrote {out_csv}")

    make_heatmap(matrices, out_png, out_pdf)


if __name__ == "__main__":
    main()
