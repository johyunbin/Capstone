#!/usr/bin/env python3
"""
RQ1 Stage 5b — Phase 4 / Phase 5 / Phase 6 / Phase 7 결과 시각화

중간발표 슬라이드 + 자문 이메일 첨부 + 중간보고서 Section 3~5 에 삽입할
figure 6 종을 생성한다. 입력은 전부 `experiments/results/rq1_motivation/`
하의 parquet 및 json, 출력은 `experiments/figures/rq1_motivation/` PNG.

로컬 실행 전용 (서버 rsync 후 로컬에서 실행).

Figure 1: Phase 4 SYSTEM vs BERNOULLI paired scatter (6 selectivity grid)
Figure 2: Phase 6 Step 4 KM20 native s=0.500 box (BERN vs STRAT)
Figure 3: Phase 6 Step 3' 4 mode 비교 (faceted selectivity × mode)
Figure 4: Phase 7 sf10 8M + sift 128d heatmap (dataset × mode)
Figure 5: Python vs Native 일치성 표 형태 figure
Figure 6: Phase 5 local skew 24 조합 Spearman ρ heatmap (negative result)
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Apple SD Gothic Neo 로 한글 렌더 (macOS)
plt.rcParams["font.family"] = [
    "AppleGothic",
    "Apple SD Gothic Neo",
    "Helvetica",
    "Arial",
]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 200
plt.rcParams["savefig.dpi"] = 200
plt.rcParams["savefig.bbox"] = "tight"


def log(msg: str) -> None:
    print(f"[viz] {msg}", flush=True)


def figure_1_phase4_paired(results_dir: Path, out_dir: Path) -> None:
    """Phase 4 SYSTEM vs BERNOULLI paired scatter, 6 selectivity grid."""
    sys_path = results_dir / "phase4_system.parquet"
    bern_path = results_dir / "phase4_bernoulli.parquet"
    if not sys_path.exists() or not bern_path.exists():
        log(f"  SKIP Figure 1 — missing {sys_path} or {bern_path}")
        return

    sys_df = pd.read_parquet(sys_path)
    bern_df = pd.read_parquet(bern_path)
    merged = sys_df.merge(
        bern_df, on=["query_id", "selectivity"], suffixes=("_sys", "_bern")
    )
    sels = sorted(merged["selectivity"].unique())

    fig, axes = plt.subplots(2, 3, figsize=(11, 7.5))
    for idx, sel in enumerate(sels):
        ax = axes[idx // 3, idx % 3]
        sub = merged[merged["selectivity"] == sel]
        sys_q = sub["q_error_sys"].values
        bern_q = sub["q_error_bern"].values
        ax.scatter(bern_q, sys_q, s=14, alpha=0.55, edgecolors="none", color="#1f77b4")
        lo = min(bern_q.min(), sys_q.min(), 1.0)
        hi = max(bern_q.max(), sys_q.max())
        ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, alpha=0.6)
        ax.set_title(f"s = {sel:.3f}", fontsize=10)
        ax.set_xlabel("BERNOULLI q-error", fontsize=9)
        ax.set_ylabel("SYSTEM q-error", fontsize=9)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.tick_params(labelsize=8)
        # 주석
        med_s = float(np.median(sys_q))
        med_b = float(np.median(bern_q))
        diff = ((med_s - med_b) / med_b * 100) if med_b > 0 else 0
        ax.text(
            0.05,
            0.95,
            f"median SYS/BERN\n{med_s:.3f} / {med_b:.3f}\nΔ={diff:+.1f}%",
            transform=ax.transAxes,
            fontsize=8,
            va="top",
            ha="left",
            bbox=dict(
                facecolor="white", edgecolor="#cccccc", alpha=0.85, boxstyle="round"
            ),
        )
    fig.suptitle(
        "Figure 1 — Phase 4 Native SYSTEM vs BERNOULLI (100 query paired, 6 selectivity)",
        fontsize=11,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.965])
    out = out_dir / "figure_1_phase4_scatter.png"
    fig.savefig(out)
    plt.close(fig)
    log(f"  saved {out}")


def figure_2_phase6_strat_box(results_dir: Path, out_dir: Path) -> None:
    """Phase 6 Step 4 s=0.500 BERN vs STRAT native boxplot."""
    bern_path = results_dir / "phase6_bern_native_v2.parquet"
    strat_path = results_dir / "phase6_strat_km20_native.parquet"
    if not bern_path.exists() or not strat_path.exists():
        log(f"  SKIP Figure 2 — missing parquet")
        return

    bern = pd.read_parquet(bern_path)
    strat = pd.read_parquet(strat_path)

    # hook_est 기준 q_error 우선, 없으면 q_error (plan_rows 기준)
    qe_col_b = "q_error_hook" if "q_error_hook" in bern.columns else "q_error"
    qe_col_s = "q_error_hook" if "q_error_hook" in strat.columns else "q_error"

    sels = sorted(set(bern["selectivity"].unique()) & set(strat["selectivity"].unique()))
    if not sels:
        log("  SKIP Figure 2 — no common selectivity")
        return

    fig, ax = plt.subplots(figsize=(9, 5.5))
    positions = np.arange(len(sels))
    width = 0.35

    box_data_b = []
    box_data_s = []
    for sel in sels:
        b = bern[bern["selectivity"] == sel][qe_col_b].dropna().values
        s = strat[strat["selectivity"] == sel][qe_col_s].dropna().values
        box_data_b.append(b)
        box_data_s.append(s)

    bp_b = ax.boxplot(
        box_data_b,
        positions=positions - width / 2,
        widths=width * 0.85,
        patch_artist=True,
        showfliers=False,
    )
    bp_s = ax.boxplot(
        box_data_s,
        positions=positions + width / 2,
        widths=width * 0.85,
        patch_artist=True,
        showfliers=False,
    )
    for box in bp_b["boxes"]:
        box.set(facecolor="#c6dbef", edgecolor="#1f77b4", linewidth=1.2)
    for box in bp_s["boxes"]:
        box.set(facecolor="#fdbb84", edgecolor="#e6550d", linewidth=1.2)
    for key in ("medians",):
        for ln in bp_b[key]:
            ln.set(color="#08306b", linewidth=1.5)
        for ln in bp_s[key]:
            ln.set(color="#7f2704", linewidth=1.5)

    ax.set_xticks(positions)
    ax.set_xticklabels([f"{s:.3f}" for s in sels])
    ax.set_xlabel("Selectivity", fontsize=10)
    ax.set_ylabel("Q-error (hook estimate)", fontsize=10)
    ax.set_title(
        "Figure 2 — Phase 6 Step 4 BERNOULLI vs STRATIFIED (KM20, native, 100 query)",
        fontsize=11,
    )
    ax.set_yscale("log")
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")

    # paired significance 표시 (phase6_native_paired.json)
    paired_path = results_dir / "phase6_native_paired.json"
    if paired_path.exists():
        with open(paired_path) as f:
            paired = json.load(f)
        by_sel = {r["selectivity"]: r for r in paired.get("rows", [])}
        for i, sel in enumerate(sels):
            if sel in by_sel:
                p = by_sel[sel]["p_less"]
                if p is not None and p < 0.001:
                    marker = "★★★"
                elif p is not None and p < 0.01:
                    marker = "★★"
                elif p is not None and p < 0.05:
                    marker = "★"
                else:
                    marker = ""
                if marker:
                    ymax = max(
                        np.percentile(box_data_b[i], 95) if len(box_data_b[i]) else 1,
                        np.percentile(box_data_s[i], 95) if len(box_data_s[i]) else 1,
                    )
                    ax.text(
                        positions[i],
                        ymax * 1.05,
                        marker,
                        ha="center",
                        fontsize=11,
                        color="#d62728",
                    )

    # Legend
    import matplotlib.patches as mpatches

    handles = [
        mpatches.Patch(facecolor="#c6dbef", edgecolor="#1f77b4", label="BERNOULLI"),
        mpatches.Patch(
            facecolor="#fdbb84", edgecolor="#e6550d", label="STRATIFIED (KM20)"
        ),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.85)

    plt.tight_layout()
    out = out_dir / "figure_2_phase6_box.png"
    fig.savefig(out)
    plt.close(fig)
    log(f"  saved {out}")


def figure_3_phase6_step3prime_compare(results_dir: Path, out_dir: Path) -> None:
    """Phase 6 Step 3' 4 mode (bern, pca_decile, km10, km20) paired diff vs BERN."""
    compare_path = results_dir / "phase6_layer_compare_compare.json"
    if not compare_path.exists():
        log(f"  SKIP Figure 3 — missing {compare_path}")
        return
    with open(compare_path) as f:
        data = json.load(f)

    # compare.json 실제 구조: {"pairs_vs_bernoulli": [{"mode": ..., "selectivity": ..., "diff_pct_med": ..., "wilcoxon_p_less": ..., ...}]}
    paired = data.get("pairs_vs_bernoulli") or data.get("paired") or []
    if not paired:
        log(f"  SKIP Figure 3 — no paired data in compare.json")
        return

    df = pd.DataFrame(paired)
    # 컬럼 이름 정규화: diff_pct_med -> diff_pct, wilcoxon_p_less -> p_less
    if "diff_pct_med" in df.columns:
        df["diff_pct"] = df["diff_pct_med"]
    if "wilcoxon_p_less" in df.columns:
        df["p_less"] = df["wilcoxon_p_less"]
    elif "p_less" not in df.columns and "p_value" in df.columns:
        df["p_less"] = df["p_value"]

    modes = [m for m in ["pca_decile", "kmeans_k10", "kmeans_k20"] if m in df["mode"].unique()]
    if not modes:
        log("  SKIP Figure 3 — no mode data")
        return

    sels = sorted(df["selectivity"].unique())

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    width = 0.27
    positions = np.arange(len(sels))
    colors = {
        "pca_decile": "#9467bd",
        "kmeans_k10": "#2ca02c",
        "kmeans_k20": "#e6550d",
    }
    labels = {
        "pca_decile": "PCA decile",
        "kmeans_k10": "k-means K=10",
        "kmeans_k20": "k-means K=20",
    }

    for i, mode in enumerate(modes):
        sub = df[df["mode"] == mode].set_index("selectivity").reindex(sels)
        diffs = sub["diff_pct"].values
        ax.bar(
            positions + (i - (len(modes) - 1) / 2) * width,
            diffs,
            width=width * 0.9,
            label=labels.get(mode, mode),
            color=colors.get(mode, "#888888"),
            edgecolor="black",
            linewidth=0.5,
        )
        # Significance star
        for j, (sel, p) in enumerate(zip(sels, sub["p_less"].values)):
            if p is not None and p < 0.05:
                ax.text(
                    positions[j] + (i - (len(modes) - 1) / 2) * width,
                    diffs[j] + 0.15,
                    "★",
                    ha="center",
                    fontsize=10,
                    color="black",
                )

    ax.axhline(0, color="black", lw=0.7)
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{s:.3f}" for s in sels])
    ax.set_xlabel("Selectivity", fontsize=10)
    ax.set_ylabel("Median q-error 개선률 (%, BERN 대비)", fontsize=10)
    ax.set_title(
        "Figure 3 — Phase 6 Step 3' 4 layer 비교 (paired vs BERNOULLI, Python counterfactual)",
        fontsize=11,
    )
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")
    plt.tight_layout()
    out = out_dir / "figure_3_phase6_layer_compare.png"
    fig.savefig(out)
    plt.close(fig)
    log(f"  saved {out}")


def figure_4_phase7_heatmap(results_dir: Path, out_dir: Path) -> None:
    """Phase 7 sf10 8M + sift 128d heatmap (placeholder 가능)."""
    bern_8m = results_dir / "phase7_8m_bern.parquet"
    strat_8m = results_dir / "phase7_8m_strat.parquet"
    bern_sift = results_dir / "phase7_sift_bern.parquet"
    strat_sift = results_dir / "phase7_sift_strat.parquet"

    have_8m = bern_8m.exists() and strat_8m.exists()
    have_sift = bern_sift.exists() and strat_sift.exists()
    if not have_8m and not have_sift:
        log(f"  SKIP Figure 4 — Phase 7 results not yet available")
        return

    rows = []
    if have_8m:
        b = pd.read_parquet(bern_8m)
        s = pd.read_parquet(strat_8m)
        qe_b = b["q_error_hook"].dropna() if "q_error_hook" in b.columns else b["q_error"].dropna()
        qe_s = s["q_error_hook"].dropna() if "q_error_hook" in s.columns else s["q_error"].dropna()
        rows.append(
            {
                "dataset": "deep 96d (8M)",
                "bern_median": float(qe_b.median()),
                "strat_median": float(qe_s.median()),
            }
        )
    else:
        rows.append(
            {
                "dataset": "deep 96d (8M)",
                "bern_median": None,
                "strat_median": None,
            }
        )

    if have_sift:
        b = pd.read_parquet(bern_sift)
        s = pd.read_parquet(strat_sift)
        qe_b = b["q_error_hook"].dropna() if "q_error_hook" in b.columns else b["q_error"].dropna()
        qe_s = s["q_error_hook"].dropna() if "q_error_hook" in s.columns else s["q_error"].dropna()
        rows.append(
            {
                "dataset": "sift 128d",
                "bern_median": float(qe_b.median()),
                "strat_median": float(qe_s.median()),
            }
        )
    else:
        rows.append(
            {
                "dataset": "sift 128d",
                "bern_median": None,
                "strat_median": None,
            }
        )

    # 1M subset (Phase 6 Step 4) 기준값 추가
    paired_path = results_dir / "phase6_native_paired.json"
    if paired_path.exists():
        with open(paired_path) as f:
            p = json.load(f)
        row_500 = next((r for r in p.get("rows", []) if abs(r["selectivity"] - 0.5) < 1e-6), None)
        if row_500:
            rows.insert(
                0,
                {
                    "dataset": "deep 96d (1M, Phase 6)",
                    "bern_median": row_500["bern_median"],
                    "strat_median": row_500["strat_median"],
                },
            )

    df = pd.DataFrame(rows)
    datasets = df["dataset"].values
    modes = ["BERNOULLI", "STRATIFIED"]
    mat = np.full((len(datasets), 2), np.nan)
    for i, r in df.iterrows():
        if r["bern_median"] is not None:
            mat[i, 0] = r["bern_median"]
        if r["strat_median"] is not None:
            mat[i, 1] = r["strat_median"]

    fig, ax = plt.subplots(figsize=(7, 0.9 + 0.9 * len(datasets)))
    im = ax.imshow(mat, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(modes)))
    ax.set_xticklabels(modes)
    ax.set_yticks(range(len(datasets)))
    ax.set_yticklabels(datasets)
    for i in range(len(datasets)):
        for j in range(2):
            val = mat[i, j]
            txt = "—" if np.isnan(val) else f"{val:.4f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=10, color="black")
    ax.set_title(
        "Figure 4 — Phase 7 확장: median q-error (s=0.500, hook estimate)",
        fontsize=11,
    )
    fig.colorbar(im, ax=ax, label="median q-error")
    plt.tight_layout()
    out = out_dir / "figure_4_phase7_heatmap.png"
    fig.savefig(out)
    plt.close(fig)
    log(f"  saved {out}")


def figure_5_python_native_consistency(results_dir: Path, out_dir: Path) -> None:
    """Python vs Native 일치성을 테이블 형태의 figure 로."""
    paired_path = results_dir / "phase6_native_paired.json"
    if not paired_path.exists():
        log(f"  SKIP Figure 5 — missing {paired_path}")
        return
    with open(paired_path) as f:
        data = json.load(f)

    rows = data.get("rows", [])
    py_step3p = data.get("python_step3prime", {})

    # 테이블 구성
    header = ["s", "Python diff%", "Python p", "Native diff%", "Native p", "qualitative 일치"]
    table = []
    for r in rows:
        sel_key = f"{r['selectivity']:.3f}".rstrip("0").rstrip(".")
        py = py_step3p.get(str(r["selectivity"])) or py_step3p.get(sel_key) or None
        py_diff = f"{py[2]:+.2f}%" if py else "—"
        py_p = f"{py[3]:.4g}" if py else "—"
        nat_diff = f"{r['diff_pct']:+.2f}%" if r["diff_pct"] is not None else "—"
        nat_p = f"{r['p_less']:.4g}" if r["p_less"] is not None else "—"
        # qualitative 일치 판단
        if py and py[2] is not None and r["diff_pct"] is not None:
            same_sign = (py[2] > 0) == (r["diff_pct"] > 0) or abs(py[2]) < 0.5 and abs(r["diff_pct"]) < 0.5
            agree = "○" if same_sign else "△"
        else:
            agree = "—"
        table.append([f"{r['selectivity']:.3f}", py_diff, py_p, nat_diff, nat_p, agree])

    fig, ax = plt.subplots(figsize=(9, 0.5 + 0.4 * (len(table) + 1)))
    ax.axis("off")
    tab = ax.table(
        cellText=table,
        colLabels=header,
        cellLoc="center",
        loc="center",
    )
    tab.auto_set_font_size(False)
    tab.set_fontsize(10)
    tab.scale(1.0, 1.5)
    for col_idx in range(len(header)):
        tab[(0, col_idx)].set_facecolor("#deebf7")
        tab[(0, col_idx)].set_text_props(weight="bold")
    ax.set_title(
        "Figure 5 — Python counterfactual vs Native 일치성 (Phase 6 Step 4, KM20)",
        fontsize=11,
    )
    plt.tight_layout()
    out = out_dir / "figure_5_python_native_table.png"
    fig.savefig(out)
    plt.close(fig)
    log(f"  saved {out}")


def figure_6_phase5_local_skew_heatmap(results_dir: Path, out_dir: Path) -> None:
    """Phase 5 local skew 24 조합 (4 metric × 6 selectivity) Spearman ρ heatmap."""
    p5_path = results_dir / "phase5_local_skew_spearman.json"
    if not p5_path.exists():
        log(f"  SKIP Figure 6 — missing {p5_path}")
        return
    with open(p5_path) as f:
        data = json.load(f)

    # 실제 구조: {"all_combos": [{"metric": ..., "selectivity": ..., "spearman_rho": ..., "p_value": ...}, ...]}
    all_combos = data.get("all_combos") or []
    if not all_combos:
        log(f"  SKIP Figure 6 — no all_combos in JSON")
        return
    df_all = pd.DataFrame(all_combos)
    metric_names = sorted(df_all["metric"].unique())
    sels_list = sorted(df_all["selectivity"].unique())
    sels = [str(s) for s in sels_list]

    mat = np.full((len(metric_names), len(sels)), np.nan)
    p_mat = np.full((len(metric_names), len(sels)), np.nan)
    for i, m in enumerate(metric_names):
        for j, s in enumerate(sels_list):
            row = df_all[(df_all["metric"] == m) & (df_all["selectivity"] == s)]
            if len(row) > 0:
                mat[i, j] = float(row.iloc[0]["spearman_rho"])
                p_mat[i, j] = float(row.iloc[0].get("p_value", 1.0))

    fig, ax = plt.subplots(figsize=(8, 0.8 + 0.6 * len(metric_names)))
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-0.3, vmax=0.3, aspect="auto")
    ax.set_xticks(range(len(sels)))
    ax.set_xticklabels([f"{float(s):.3f}" for s in sels])
    ax.set_yticks(range(len(metric_names)))
    # 짧은 label
    label_map = {
        "knn_distance_entropy": "k-NN 거리 entropy",
        "knn_pca_evr1": "k-NN PCA EVR1",
        "kde_modality_count": "KDE modality",
        "nn_clustering_coef": "NN clustering coef",
    }
    ax.set_yticklabels([label_map.get(m, m) for m in metric_names])
    for i in range(len(metric_names)):
        for j in range(len(sels)):
            val = mat[i, j]
            if not np.isnan(val):
                ax.text(
                    j,
                    i,
                    f"{val:+.2f}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="black" if abs(val) < 0.2 else "white",
                )
    ax.set_xlabel("Selectivity", fontsize=10)
    ax.set_title(
        "Figure 6 — Phase 5 Local skew 24 조합 Spearman ρ (negative result: 모두 |ρ| < 0.2)",
        fontsize=10.5,
    )
    fig.colorbar(im, ax=ax, label="Spearman ρ")
    plt.tight_layout()
    out = out_dir / "figure_6_phase5_heatmap.png"
    fig.savefig(out)
    plt.close(fig)
    log(f"  saved {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--results-dir",
        default="experiments/results/rq1_motivation",
        help="parquet / json 위치 (로컬)",
    )
    ap.add_argument(
        "--out-dir",
        default="experiments/figures/rq1_motivation",
        help="PNG 저장 위치",
    )
    args = ap.parse_args()

    results_dir = Path(args.results_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    log(f"results_dir={results_dir}")
    log(f"out_dir={out_dir}")

    figure_1_phase4_paired(results_dir, out_dir)
    figure_2_phase6_strat_box(results_dir, out_dir)
    figure_3_phase6_step3prime_compare(results_dir, out_dir)
    figure_4_phase7_heatmap(results_dir, out_dir)
    figure_5_python_native_consistency(results_dir, out_dir)
    figure_6_phase5_local_skew_heatmap(results_dir, out_dir)

    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
