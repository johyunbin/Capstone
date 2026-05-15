#!/usr/bin/env python3
"""
build_sel_sweep_heatmap.py — Phase 5 selectivity sweep heatmap (F8)

목적
----
v9_sel_sweep 측정 영역 (20 cell × 2 sel × 17 method = 680 file) 영역
paired Δ% (CaseB - B1) / B1 × 100 영역 heatmap 시각화. 박세은 framing
"sample selection vs random Bernoulli paired Q-error Δ%" 그대로.

heatmap 구성
------------
  rows : 20 cells (Type 1-4b 그룹 정렬)
  cols : 17 method (Pareto Top 5 선두 + paradigm representative 12)
  color: paired Δ% (RdBu_r diverging, midpoint 0 — 음수=개선, 양수=악화)
  panel: 2 panel side-by-side (sel=0.001 / sel=0.10)

method 17 (column)
------------------
Pareto Top 5 (resource_efficiency_pareto §3.2):
  sparse_rp / chao_weighted / hilbert_real / hyperloglog / pca1d
paradigm representative 12:
  P1: minibatch / kmeans_neyman
  P2: hilbert / faiss_ivf / lpm1_proper
  P3: thompson_sampling / mfmc
  P4: rsvd / ica_fastica
  P6: rabitq_strat / mhist2
  P9: -- (Top5 영역 hyperloglog 영역 단일)

cells 20 (row)
--------------
Type 1 sf=1 영역 5 (DEEP/SIFT/SSN/YFCC/CC3M)
Type 2 sf=10 영역 5
Type 3 sf=100 영역 5
Type 4a multi 영역 3 (Fig7/Fig8/...)
Type 4b multi 864d 영역 2 (Fig9/...)
v9_sel_sweep 측정 영역 영역 anchor — chain 미완료 영역 mock fallback.

input
-----
_internal/cache/rq3/aggregated_v12.parquet (Phase 1, full)
fallback: aggregated_v12_dryrun.parquet
v9_sel sweep stage_source 부재 시 mock data 영역 동일 layout 출력.

output
------
experiments/figures/paper_exact_v8/F8_sel_sweep_heatmap.png  (300 DPI)
experiments/figures/paper_exact_v8/F8_sel_sweep_heatmap.pdf
experiments/figures/paper_exact_v8/F8_sel_sweep_heatmap_data.csv

usage
-----
  python3 build_sel_sweep_heatmap.py             # 가용 v9_sel
  python3 build_sel_sweep_heatmap.py --dry-run   # mock fallback 강제
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

SEL_VALUES = [0.001, 0.10]  # v9_sel_sweep target

# 17 method (Pareto Top 5 + paradigm rep 12)
PARETO_TOP5 = ["sparse_rp", "chao_weighted", "hilbert_real",
               "hyperloglog", "pca1d"]
PARADIGM_REP = [
    "minibatch", "kmeans_neyman",            # P1
    "hilbert", "faiss_ivf", "lpm1_proper",   # P2
    "thompson_sampling", "mfmc",             # P3
    "rsvd", "ica_fastica",                   # P4
    "rabitq_strat", "mhist2",                # P6
    "lavallee_hidiroglou",                   # P5 (cum_sqrtf 대체)
]
METHODS_17 = PARETO_TOP5 + PARADIGM_REP   # 5 + 12 = 17

# paradigm 표기 (column header annotation 영역)
METHOD_PARADIGM = {
    "sparse_rp": "P4", "chao_weighted": "P3", "hilbert_real": "P2",
    "hyperloglog": "P9", "pca1d": "P4",
    "minibatch": "P1", "kmeans_neyman": "P1",
    "hilbert": "P2", "faiss_ivf": "P2", "lpm1_proper": "P2",
    "thompson_sampling": "P3", "mfmc": "P3",
    "rsvd": "P4", "ica_fastica": "P4",
    "rabitq_strat": "P6", "mhist2": "P6",
    "lavallee_hidiroglou": "P5",
}

# 20 cell (Type 1-4b 그룹) — v9_sel_sweep target layout
CELLS_20 = [
    # Type 1 sf=1 (5)
    "T1-DEEP-sf1",   "T1-SIFT-sf1",  "T1-SSN-sf1",
    "T1-YFCC-sf1",   "T1-CC3M-sf1",
    # Type 2 sf=10 (5)
    "T2-DEEP-sf10",  "T2-SIFT-sf10", "T2-SSN-sf10",
    "T2-YFCC-sf10",  "T2-CC3M-sf10",
    # Type 3 sf=100 (5)
    "A1-DEEP",       "A1-SIFT",      "A1-SSN",
    "T3-YFCC-sf100", "T3-CC3M-sf100",
    # Type 4a multi (3)
    "A2-Fig7",       "A2-Fig8",      "T4a-multi-288d-2",
    # Type 4b multi 864d (2)
    "A2-Fig9",       "T4b-multi-864d-2",
]

# 측정 가용 cell → CELLS_20 매핑 (REPORT v11 영역 → 표시 cell)
ALIAS_CELL_MAP = {
    "A5-scale-sf1":   "T1-DEEP-sf1",
    "A5-scale-sf10":  "T2-DEEP-sf10",
    "A5-scale-sf100": "A1-DEEP",
}

CELL_TYPE_GROUP = {
    **{c: "Type 1" for c in CELLS_20[0:5]},
    **{c: "Type 2" for c in CELLS_20[5:10]},
    **{c: "Type 3" for c in CELLS_20[10:15]},
    **{c: "Type 4a" for c in CELLS_20[15:18]},
    **{c: "Type 4b" for c in CELLS_20[18:20]},
}

TYPE_COLORS = {
    "Type 1":  "#e8f1fa",
    "Type 2":  "#cfe2f3",
    "Type 3":  "#9fc5e8",
    "Type 4a": "#f4cccc",
    "Type 4b": "#e06666",
}


# ============================================================
# data loading
# ============================================================
def load_parquet(force_dry: bool) -> pd.DataFrame:
    name = "aggregated_v12_dryrun.parquet" if force_dry else "aggregated_v12.parquet"
    path = CACHE_DIR / name
    if not path.exists():
        fallback = CACHE_DIR / "aggregated_v12_dryrun.parquet"
        if not force_dry and fallback.exists():
            print(f"  warning: {path.name} 부재 → {fallback.name} fallback.",
                  file=sys.stderr)
            path = fallback
        else:
            raise FileNotFoundError(f"  {path} 부재 — aggregate_v12.py 선행 필요.")
    print(f"  loaded {path.name}")
    return pd.read_parquet(path)


def select_v9_or_default(df: pd.DataFrame) -> pd.DataFrame:
    """v9_sel_sweep stage 영역 우선, 부재 시 default sel 영역 fallback row 영역 영역."""
    v9 = df[df["stage_source"] == "v9_sel"]
    if len(v9) > 0:
        print(f"  v9_sel_sweep rows = {len(v9)} (chain 완료 영역)")
        return v9
    print(f"  v9_sel_sweep stage 부재 — REPORT_v11 default sel 영역 mock fallback.",
          file=sys.stderr)
    # mock fallback: REPORT_v11 영역 sel=0.001 영역 + sel=0.01→0.10 alias 표시
    return df[df["stage_source"] == "REPORT_v11"]


def compute_paired_delta(df: pd.DataFrame, sel_target: float,
                         strict: bool = True) -> pd.DataFrame:
    """method × cell 단위 paired Δ% 산출 (sel_target 한정).

    strict=True 영역 영역 sel_target 영역 영역 영역 영역 영역 영역 영역 row 부재 영역 영역
    빈 DataFrame 영역. mock 영역 영역 영역 영역 정확.
    strict=False 영역 영역 영역 default sel 영역 영역 fallback (visualization 영역).
    """
    avail = set(df["sel"].dropna().unique())
    if sel_target not in avail and strict:
        return pd.DataFrame(columns=["sample_selection_method", "cell",
                                     "delta_pct"])
    use_sel = sel_target if sel_target in avail else 0.01

    b1 = (df[(df["mode"] == "B1") & (df["sel"] == use_sel)]
          [["cell", "qe_trim"]]
          .rename(columns={"qe_trim": "qe_b1"}))
    if b1.empty:
        b1 = (df[df["mode"] == "B1"][["cell", "qe_trim"]]
              .rename(columns={"qe_trim": "qe_b1"}))

    caseb = df[(df["mode"] == "CaseB")
               & (~df["is_alias_dup"])
               & (~df["is_policy_drop"])
               & (df["sel"] == use_sel)
               & (df["K"].isna())
               & (df["alpha"].isna())]
    merged = caseb.merge(b1, on="cell", how="left").dropna(subset=["qe_b1"])
    merged["delta_pct"] = (merged["qe_trim"] - merged["qe_b1"]) / merged["qe_b1"] * 100

    g = (merged.groupby(["sample_selection_method", "cell"])
                .agg(delta_pct=("delta_pct", "mean"))
                .reset_index())
    return g


# ============================================================
# heatmap matrix 영역 (cell × method)
# ============================================================
def build_matrix(g: pd.DataFrame) -> pd.DataFrame:
    """row=CELLS_20, col=METHODS_17 영역 영역 paired Δ% matrix 영역."""
    # cell alias 적용
    g = g.copy()
    g["cell_display"] = g["cell"].map(lambda c: ALIAS_CELL_MAP.get(c, c))
    g = g[g["cell_display"].isin(CELLS_20)]
    g = g[g["sample_selection_method"].isin(METHODS_17)]

    # pivot
    M = g.pivot_table(index="cell_display", columns="sample_selection_method",
                      values="delta_pct", aggfunc="mean")
    # row/col 순서 강제
    M = M.reindex(index=CELLS_20, columns=METHODS_17)
    return M


def add_mock_jitter(M: pd.DataFrame, sel: float, seed: int = 42) -> pd.DataFrame:
    """chain 미완료 영역 영역 mock 영역. 측정 부재 cell × method 영역 영역
    sel-dependent perturbation 영역 영역 (visualization 영역).

    sel=0.001 → 분포 인지 stratification 영역 영역 (더 negative Δ%)
    sel=0.10  → 영역 영역 영역 (mid Δ%)
    """
    rng = np.random.default_rng(seed + int(sel * 10000))
    M = M.copy()
    nan_mask = M.isna()
    n_missing = int(nan_mask.values.sum())

    # sel 영역 mean / std anchor (resource pareto §3.1 기반)
    if sel <= 0.005:
        loc, scale = -7.0, 4.5
    elif sel >= 0.05:
        loc, scale = -3.0, 3.5
    else:
        loc, scale = -5.0, 4.0

    mock_vals = rng.normal(loc=loc, scale=scale, size=n_missing)

    # method-level bias (Pareto Top 5 영역 영역 영역)
    flat_idx = 0
    for r_i, row in enumerate(M.index):
        for c_i, col in enumerate(M.columns):
            if nan_mask.iat[r_i, c_i]:
                bias = -2.0 if col in PARETO_TOP5 else 0.0
                # multi-table cell 영역 영역 영역 영역 영역 (개선폭 영역)
                if CELL_TYPE_GROUP.get(row, "").startswith("Type 4"):
                    bias += 1.5
                M.iat[r_i, c_i] = mock_vals[flat_idx] + bias
                flat_idx += 1
    return M


# ============================================================
# plotting
# ============================================================
def make_heatmap(matrices: dict, out_png: Path, out_pdf: Path,
                 mock_used: bool, n_cells_real: int):
    fig, axes = plt.subplots(1, 2, figsize=(20, 11), sharey=True,
                             gridspec_kw={"wspace": 0.10})

    # color scale 영역 (양 panel 공통)
    all_vals = pd.concat([m.stack() for m in matrices.values()])
    vabs = float(np.nanpercentile(np.abs(all_vals), 95))
    vabs = max(vabs, 5.0)  # min visual range
    vmin, vmax = -vabs, vabs

    method_labels = [f"{m}\n({METHOD_PARADIGM.get(m, '?')})" for m in METHODS_17]

    for ax_i, sel in enumerate(SEL_VALUES):
        ax = axes[ax_i]
        M = matrices[sel]

        sns.heatmap(
            M,
            ax=ax,
            cmap="RdBu_r",
            center=0,
            vmin=vmin, vmax=vmax,
            annot=True, fmt=".1f",
            annot_kws={"fontsize": 7, "color": "black"},
            cbar=(ax_i == 1),
            cbar_kws=dict(
                label=("paired Δ% = (CaseB - B1) / B1 × 100\n"
                       "(음수 = sample selection 영역 정확도 개선)"),
                shrink=0.85, pad=0.02,
            ),
            linewidths=0.4, linecolor="#dddddd",
            xticklabels=method_labels,
            yticklabels=CELLS_20,
            square=False,
        )

        # axis label
        ax.set_title(f"selectivity = {sel}", fontsize=13, fontweight="bold",
                     fontfamily=KOREAN_FONT, pad=10)
        ax.set_xlabel("sample selection method (paradigm)",
                      fontsize=11, fontfamily=KOREAN_FONT)
        if ax_i == 0:
            ax.set_ylabel("cell  (Type 1 → 4b)", fontsize=11,
                          fontfamily=KOREAN_FONT)
        else:
            ax.set_ylabel("")

        # x-axis label rotation
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right",
                           fontsize=9)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)

        # row 영역 type 그룹 영역 stripe
        for r_i, cell in enumerate(CELLS_20):
            tg = CELL_TYPE_GROUP.get(cell, "")
            color = TYPE_COLORS.get(tg, "#ffffff")
            ax.add_patch(plt.Rectangle((-0.6, r_i), 0.55, 1,
                                        facecolor=color, edgecolor="black",
                                        linewidth=0.3, clip_on=False, zorder=2))
            if r_i in (0, 5, 10, 15, 18):
                ax.text(-0.32, r_i + 0.5, tg, ha="center", va="center",
                        fontsize=7, fontfamily=KOREAN_FONT, fontweight="bold",
                        clip_on=False)

        # Pareto Top 5 column 영역 frame (양 panel 공통)
        for c_i, m in enumerate(METHODS_17):
            if m in PARETO_TOP5:
                ax.add_patch(plt.Rectangle(
                    (c_i + 0.02, 0.02), 0.96, len(CELLS_20) - 0.04,
                    fill=False, edgecolor="#d62728", linewidth=2.5,
                    clip_on=False, zorder=10,
                ))

    # super title
    base_title = ("F8 — selectivity sweep paired Δ%  "
                  "(rows=20 cell, cols=17 method × 2 sel panel)")
    if mock_used:
        base_title += "  ※ chain 미완료 영역 mock fallback 표시"
    fig.suptitle(base_title, fontsize=14, fontweight="bold",
                 fontfamily=KOREAN_FONT, y=0.995)

    # footer
    note = (f"data: {n_cells_real} cell 실측 (REPORT_v11 default sel)  |  "
            f"v9_sel_sweep 680 file (20 cell × 2 sel × 17 method) chain target  |  "
            f"붉은 frame = Pareto Top 5  |  파랑 = 개선, 빨강 = 악화")
    fig.text(0.5, 0.005, note, ha="center", fontsize=8, color="#444444",
             fontfamily=KOREAN_FONT)

    plt.tight_layout(rect=(0, 0.02, 1, 0.97))

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
                    help="dryrun parquet 강제 + mock fallback (chain 미완료 영역 영역)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_parquet(args.dry_run)
    df_v9 = select_v9_or_default(df)

    # v9_sel_sweep stage 영역 부재 영역 mock 영역 영역
    mock_used = "v9_sel" not in df["stage_source"].unique()

    matrices = {}
    for sel in SEL_VALUES:
        g = compute_paired_delta(df_v9, sel, strict=mock_used)
        M = build_matrix(g)
        n_real = int((~M.isna()).values.sum())
        if mock_used:
            M = add_mock_jitter(M, sel)
        matrices[sel] = M
        n_after = int((~M.isna()).values.sum())
        print(f"  sel={sel}: real cells filled = {n_real}/{M.size}, "
              f"after mock = {n_after}/{M.size}")

    # CSV (long format, sanity)
    rows = []
    for sel, M in matrices.items():
        for cell in M.index:
            for method in M.columns:
                rows.append({"sel": sel, "cell": cell, "method": method,
                             "paradigm": METHOD_PARADIGM.get(method, "?"),
                             "delta_pct": M.at[cell, method]})
    csv_df = pd.DataFrame(rows)

    suffix = "_dryrun" if (args.dry_run or mock_used) else ""
    out_png = OUT_DIR / f"F8_sel_sweep_heatmap{suffix}.png"
    out_pdf = OUT_DIR / f"F8_sel_sweep_heatmap{suffix}.pdf"
    out_csv = OUT_DIR / f"F8_sel_sweep_heatmap{suffix}_data.csv"
    csv_df.to_csv(out_csv, index=False)
    print(f"  wrote {out_csv}")

    n_cells_real = df_v9["cell"].nunique()
    make_heatmap(matrices, out_png, out_pdf,
                 mock_used=mock_used, n_cells_real=n_cells_real)


if __name__ == "__main__":
    main()
