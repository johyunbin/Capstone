#!/usr/bin/env python3
"""Phase 6 §6.4 통계 후속 PoC — plan-level effect size · cluster paired bootstrap · variance decomposition.

§5.4 의 결론 ("anchor=B1 의 86.9% small effect → latency 동등성 / plan 회복은 94.9% 차이 → robustness 분리") 을
세 통계 절차로 다축 보강한다. 모든 산출은 6/11 최종 보고서 본문 §5.4·§5.5·§6.4 갱신과 carry 분석용.

PoC 1 — plan-level effect size 분층
  paired_stats.csv 의 Hedges' g 분포를 plan_recovered ∈ {True, False, N/A} 로 분층 → 그룹별 분포.
  가설: 회복 그룹의 small effect 비율이 비회복 보다 ↑ (plan 회복이 latency 동등성을 매개).

PoC 2 — cluster paired bootstrap
  cell 단위로 resample (B=2,000) → naïve bootstrap (행 단위 resample) 대비 95% CI 비교.
  가설: cluster ratio ≥ 1.0 (within-cell 상관 양수 → cluster CI 가 더 넓음 — 보정 효과).

PoC 3 — variance decomposition
  log(exec_ms) ~ C(cell) + C(condition_4) + C(cell):C(condition_4)  · statsmodels OLS Type-III SS.
  4 조건 = baseline · B1 · CaseB (13 method 통합) · oracle.
  가설: C(condition) 의 % SS < C(cell) — latency 변동의 주 원인은 query/qid/sel 이며 조건 효과는 작음.

실행 (서버 미접속 — 로컬 산출물로 self-contained):
    python3 _internal/scripts/stats_poc_6_4.py

출력:
    _internal/cache/rq3/latency/poc_6_4/{plan_level_effect_size,cluster_bootstrap,variance_decomp}.csv
    _internal/cache/rq3/latency/poc_6_4/summary.md
    experiments/figures/보고서_6_11/poc_6_4/{fig_plan_level_g,fig_variance_decomp}.{png,pdf}
"""
from __future__ import annotations

import sys
import csv
import json
import statistics
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "NanumGothic", "AppleGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from analyze_latency import (  # noqa: E402
    load_results, plan_signature, _plan_changed, cell_label, _variant_label
)

REPO = SCRIPT_DIR.parent.parent
PHASE2_DIR = REPO / "_internal/cache/rq3/latency/phase2"
PHASE3_DIR = REPO / "_internal/cache/rq3/latency/phase3"
PAIRED_P2 = PHASE2_DIR / "figures/paired_stats.csv"
PAIRED_P3 = PHASE3_DIR / "figures/paired_stats.csv"

CSV_DIR = REPO / "_internal/cache/rq3/latency/poc_6_4"
FIG_DIR = REPO / "experiments/figures/보고서_6_11/poc_6_4"

BOOTSTRAP_B = 2000
SEED = 7


# ---------------------------------------------------------------------------
# 데이터 준비 — plan_recovered 라벨 + paired_stats merge
# ---------------------------------------------------------------------------

def compute_plan_status(results: list[dict]) -> pd.DataFrame:
    """cell × variant → plan_recovered ∈ {True, False, None}.

    oracle variant 의 plan_signature 를 기준으로 각 variant 가 동일 plan 인지 판정.
    oracle 이 없거나 variant plan 미캡처면 None (N/A).
    baseline 도 포함 — 단 baseline 은 정의상 변동 plan (vs oracle) 이므로 False 가 자연.
    """
    rows = []
    for r in results:
        cell = cell_label(r)
        by = {_variant_label(v): v for v in r["variants"]}
        oracle = by.get("oracle")
        oracle_sig = plan_signature(oracle["plan_json"]) if oracle else ()
        for lab, v in by.items():
            sig = plan_signature(v["plan_json"])
            if not oracle_sig or not sig:
                recovered: bool | None = None
            else:
                recovered = (sig == oracle_sig)
            rows.append({"cell": cell, "variant": lab, "plan_recovered": recovered})
    return pd.DataFrame(rows)


def load_paired() -> pd.DataFrame:
    a = pd.read_csv(PAIRED_P2)
    b = pd.read_csv(PAIRED_P3)
    a["phase"] = "phase2"
    b["phase"] = "phase3"
    return pd.concat([a, b], ignore_index=True)


# ---------------------------------------------------------------------------
# PoC 1 — plan-level effect size 분층
# ---------------------------------------------------------------------------

def poc1_plan_level_effect_size(paired: pd.DataFrame) -> pd.DataFrame:
    """anchor × plan_recovered 별 |g| 분포 + 유의 비율 + CI 비제로 비율."""
    def _label_plan(v):
        try:
            if pd.isna(v):
                return "N/A"
        except (TypeError, ValueError):
            pass
        return "True" if bool(v) else "False"

    paired = paired.copy()
    paired["plan_status"] = paired["plan_recovered"].map(_label_plan)
    paired["abs_g"] = paired["hedges_g"].abs()
    paired["g_band"] = pd.cut(paired["abs_g"],
                              bins=[-0.001, 0.5, 0.8, np.inf],
                              labels=["small", "medium", "large"])
    paired["sig"] = paired["p_holm"] < 0.05
    paired["ci_excl0"] = (paired["ci_lo_ms"] * paired["ci_hi_ms"]) > 0

    out = []
    for anchor in ["baseline", "B1"]:
        for status in ["True", "False", "N/A"]:
            sub = paired[(paired["anchor"] == anchor) &
                         (paired["plan_status"] == status)]
            n = len(sub)
            if n == 0:
                out.append({
                    "anchor": anchor, "plan_recovered": status, "n": 0,
                    "n_small": 0, "n_medium": 0, "n_large": 0,
                    "pct_small": float("nan"), "pct_medium": float("nan"),
                    "pct_large": float("nan"),
                    "mean_abs_g": float("nan"), "median_abs_g": float("nan"),
                    "n_p_holm_sig": 0, "pct_p_holm_sig": float("nan"),
                    "n_ci_excludes_zero": 0, "pct_ci_excludes_zero": float("nan"),
                })
                continue
            n_small = int((sub["g_band"] == "small").sum())
            n_med = int((sub["g_band"] == "medium").sum())
            n_lar = int((sub["g_band"] == "large").sum())
            n_sig = int(sub["sig"].sum())
            n_ci = int(sub["ci_excl0"].sum())
            out.append({
                "anchor": anchor, "plan_recovered": status, "n": n,
                "n_small": n_small, "n_medium": n_med, "n_large": n_lar,
                "pct_small": 100.0 * n_small / n,
                "pct_medium": 100.0 * n_med / n,
                "pct_large": 100.0 * n_lar / n,
                "mean_abs_g": float(sub["abs_g"].mean()),
                "median_abs_g": float(sub["abs_g"].median()),
                "n_p_holm_sig": n_sig, "pct_p_holm_sig": 100.0 * n_sig / n,
                "n_ci_excludes_zero": n_ci,
                "pct_ci_excludes_zero": 100.0 * n_ci / n,
            })
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# PoC 2 — cluster paired bootstrap
# ---------------------------------------------------------------------------

def poc2_cluster_bootstrap(paired: pd.DataFrame,
                            B: int = BOOTSTRAP_B,
                            seed: int = SEED) -> pd.DataFrame:
    """B1 anchor 의 두 metric 에 대해 naïve vs cluster bootstrap 95% CI 비교.

    metric:
      · mean_median_diff_ms — 168 행의 median_diff_ms 평균 (anchor=B1)
      · pct_p_holm_sig — % p_holm<0.05 (점추정 7.7%)
    cluster = cell. 각 cell 의 B1 anchor 행은 14개 (oracle + 13 CaseB).
    """
    sub = paired[paired["anchor"] == "B1"].reset_index(drop=True).copy()
    cells = list(sub["cell"].unique())
    n_total = len(sub)
    n_cells = len(cells)

    md_pos = sub["median_diff_ms"].to_numpy(dtype=float)
    sig_pos = (sub["p_holm"] < 0.05).to_numpy(dtype=bool)
    cell_to_idx = {c: np.where(sub["cell"].to_numpy() == c)[0]
                    for c in cells}

    rng = np.random.default_rng(seed)

    # --- naïve bootstrap (행 단위) ---
    idx_naive = rng.integers(0, n_total, size=(B, n_total))
    md_naive = md_pos[idx_naive].mean(axis=1)
    sig_naive = sig_pos[idx_naive].mean(axis=1) * 100.0

    # --- cluster bootstrap (cell 단위) ---
    md_cluster = np.empty(B, dtype=float)
    sig_cluster = np.empty(B, dtype=float)
    cell_idx_arr = np.arange(n_cells)
    for b in range(B):
        chosen = rng.choice(cell_idx_arr, size=n_cells, replace=True)
        rows = np.concatenate([cell_to_idx[cells[i]] for i in chosen])
        md_cluster[b] = md_pos[rows].mean()
        sig_cluster[b] = sig_pos[rows].mean() * 100.0

    def _summarize(arr, point):
        lo, hi = np.percentile(arr, [2.5, 97.5])
        return point, float(lo), float(hi), float(hi - lo)

    p_md = float(md_pos.mean())
    p_sig = float(sig_pos.mean() * 100.0)

    n_pe_md, n_lo_md, n_hi_md, n_w_md = _summarize(md_naive, p_md)
    c_pe_md, c_lo_md, c_hi_md, c_w_md = _summarize(md_cluster, p_md)
    n_pe_si, n_lo_si, n_hi_si, n_w_si = _summarize(sig_naive, p_sig)
    c_pe_si, c_lo_si, c_hi_si, c_w_si = _summarize(sig_cluster, p_sig)

    return pd.DataFrame([
        {"metric": "mean_median_diff_ms_B1",
         "point_estimate": p_md,
         "naive_ci_lo": n_lo_md, "naive_ci_hi": n_hi_md, "naive_width": n_w_md,
         "cluster_ci_lo": c_lo_md, "cluster_ci_hi": c_hi_md, "cluster_width": c_w_md,
         "width_ratio_cluster_over_naive": c_w_md / n_w_md if n_w_md > 0 else float("nan"),
         "n_total": n_total, "n_clusters": n_cells, "B": B},
        {"metric": "pct_p_holm_sig_B1",
         "point_estimate": p_sig,
         "naive_ci_lo": n_lo_si, "naive_ci_hi": n_hi_si, "naive_width": n_w_si,
         "cluster_ci_lo": c_lo_si, "cluster_ci_hi": c_hi_si, "cluster_width": c_w_si,
         "width_ratio_cluster_over_naive": c_w_si / n_w_si if n_w_si > 0 else float("nan"),
         "n_total": n_total, "n_clusters": n_cells, "B": B},
    ])


# ---------------------------------------------------------------------------
# PoC 3 — variance decomposition
# ---------------------------------------------------------------------------

def _condition_4(variant: str) -> str:
    """16 variant → 4 condition: baseline · B1 · CaseB · oracle."""
    if variant.startswith("CaseB:"):
        return "CaseB"
    return variant


def build_long_df(results: list[dict]) -> pd.DataFrame:
    """raw JSON → tidy DataFrame (cell, query, qid, sel, variant, condition, rep, log_ms)."""
    rows = []
    for r in results:
        cell = cell_label(r)
        for v in r["variants"]:
            lab = _variant_label(v)
            cond = _condition_4(lab)
            exec_ms = v.get("exec_ms") or []
            for i, ms in enumerate(exec_ms):
                if ms is None or ms <= 0:
                    continue
                rows.append({
                    "cell": cell,
                    "query": r["query"],
                    "qid": r["query_id"],
                    "sel": r["sel"],
                    "variant": lab,
                    "condition": cond,
                    "rep": i,
                    "exec_ms": float(ms),
                    "log_ms": float(np.log(ms)),
                })
    return pd.DataFrame(rows)


def poc3_variance_decomposition(results: list[dict]) -> dict:
    """log(exec_ms) ~ C(cell) + C(condition) + C(cell):C(condition) Type-III SS.

    부차 모델 — C(query) + C(qid) + C(sel) + C(condition) + 교호작용 — 도 함께 산출."""
    df = build_long_df(results)

    # 모델 1 — cell × condition (most interpretable)
    df["cell_str"] = df["cell"].astype("category")
    df["cond_str"] = df["condition"].astype("category")
    model1 = smf.ols(
        "log_ms ~ C(cell_str, Sum) + C(cond_str, Sum) + "
        "C(cell_str, Sum):C(cond_str, Sum)",
        data=df).fit()
    a1 = anova_lm(model1, typ=3)
    # 부분 SS / 전체 SS (Sum-coded 의 Intercept 행은 제외)
    a1_clean = a1.drop("Intercept", errors="ignore").copy()
    ss_total = a1_clean["sum_sq"].sum()
    a1_clean["pct_ss"] = 100.0 * a1_clean["sum_sq"] / ss_total

    # 모델 2 — query + qid + sel + condition (4 conditions: baseline·B1·CaseB·oracle)
    df["query_str"] = df["query"].astype("category")
    df["qid_str"] = df["qid"].astype("category")
    df["sel_str"] = df["sel"].astype("category")
    model2 = smf.ols(
        "log_ms ~ C(query_str, Sum) + C(qid_str, Sum) + C(sel_str, Sum) + "
        "C(cond_str, Sum) + C(query_str, Sum):C(cond_str, Sum) + "
        "C(sel_str, Sum):C(cond_str, Sum)",
        data=df).fit()
    a2 = anova_lm(model2, typ=3)
    a2_clean = a2.drop("Intercept", errors="ignore").copy()
    ss_total2 = a2_clean["sum_sq"].sum()
    a2_clean["pct_ss"] = 100.0 * a2_clean["sum_sq"] / ss_total2

    # 모델 3 — baseline 제외 (B1·CaseB·oracle 만) — §5.4 의 B1↔CaseB↔oracle 동등성 직접 검증
    df3 = df[df["condition"] != "baseline"].copy()
    df3["cond_str"] = df3["condition"].astype("category")
    df3["query_str"] = df3["query"].astype("category")
    df3["qid_str"] = df3["qid"].astype("category")
    df3["sel_str"] = df3["sel"].astype("category")
    model3 = smf.ols(
        "log_ms ~ C(query_str, Sum) + C(qid_str, Sum) + C(sel_str, Sum) + "
        "C(cond_str, Sum) + C(query_str, Sum):C(cond_str, Sum) + "
        "C(sel_str, Sum):C(cond_str, Sum)",
        data=df3).fit()
    a3 = anova_lm(model3, typ=3)
    a3_clean = a3.drop("Intercept", errors="ignore").copy()
    ss_total3 = a3_clean["sum_sq"].sum()
    a3_clean["pct_ss"] = 100.0 * a3_clean["sum_sq"] / ss_total3

    return {
        "model1_cell_condition": a1_clean.reset_index().rename(columns={"index": "factor"}),
        "model2_factor_decomp": a2_clean.reset_index().rename(columns={"index": "factor"}),
        "model3_no_baseline": a3_clean.reset_index().rename(columns={"index": "factor"}),
        "n_obs": len(df),
        "n_obs_no_baseline": len(df3),
        "model1_r2": float(model1.rsquared),
        "model2_r2": float(model2.rsquared),
        "model3_r2": float(model3.rsquared),
    }


# ---------------------------------------------------------------------------
# 시각화
# ---------------------------------------------------------------------------

def fig_plan_level_g(paired: pd.DataFrame, out_dir: Path) -> None:
    sub = paired[paired["anchor"] == "B1"].copy()
    sub["abs_g"] = sub["hedges_g"].abs()
    sub["plan_status"] = sub["plan_recovered"].map(
        lambda v: "True" if v is True else ("False" if v is False else "N/A")
    )
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    groups = ["True", "False", "N/A"]
    data = [sub[sub["plan_status"] == g]["abs_g"].dropna().tolist() for g in groups]
    counts = [len(d) for d in data]
    positions = list(range(1, len(groups) + 1))
    bp = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True,
                    showmeans=True, meanline=False,
                    meanprops=dict(marker="D", markerfacecolor="white",
                                    markeredgecolor="black", markersize=6))
    colors = ["#3a8a4d", "#c54a3f", "#8a8a8a"]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.55)
    ax.axhline(0.5, color="#aaa", linestyle="--", linewidth=0.8)
    ax.axhline(0.8, color="#aaa", linestyle="--", linewidth=0.8)
    ax.text(len(groups) + 0.4, 0.5, "small/medium 경계", fontsize=8,
            color="#666", va="center")
    ax.text(len(groups) + 0.4, 0.8, "medium/large 경계", fontsize=8,
            color="#666", va="center")
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{g}\n(n={c})" for g, c in zip(groups, counts)])
    ax.set_ylabel("|Hedges' g|")
    ax.set_title("plan-level effect size 분층 — anchor=B1 의 |g| 분포 by plan 회복 여부")
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig_plan_level_g.{ext}", dpi=150)
    plt.close(fig)


def fig_variance_decomp(decomp: dict, out_dir: Path) -> None:
    factor_short = {
        "C(query_str, Sum)": "query",
        "C(qid_str, Sum)": "qid",
        "C(sel_str, Sum)": "sel",
        "C(cond_str, Sum)": "condition",
        "C(query_str, Sum):C(cond_str, Sum)": "query × condition",
        "C(sel_str, Sum):C(cond_str, Sum)": "sel × condition",
        "Residual": "Residual (rep 잔차)",
    }
    colors_map = {
        "query": "#1f6d92", "qid": "#2d8eaf", "sel": "#4cb1c4",
        "condition": "#c54a3f",
        "query × condition": "#e88a3a", "sel × condition": "#e8b13a",
        "Residual (rep 잔차)": "#888",
    }

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6))
    for ax, key, title in [
        (axes[0], "model2_factor_decomp",
         f"(a) 4 condition (baseline·B1·CaseB·oracle) — n={decomp['n_obs']:,}, "
         f"R²={decomp['model2_r2']:.3f}"),
        (axes[1], "model3_no_baseline",
         f"(b) baseline 제외 — n={decomp['n_obs_no_baseline']:,}, "
         f"R²={decomp['model3_r2']:.3f}"),
    ]:
        df = decomp[key].copy().sort_values("pct_ss", ascending=True)
        factors = df["factor"].tolist()
        pct = df["pct_ss"].tolist()
        labels = [factor_short.get(f, f) for f in factors]
        bar_colors = [colors_map.get(lab, "#555") for lab in labels]
        ypos = np.arange(len(labels))
        ax.barh(ypos, pct, color=bar_colors, alpha=0.85,
                edgecolor="#333", linewidth=0.6)
        max_pct = max(pct) if pct else 1.0
        for i, p in enumerate(pct):
            ax.text(p + max_pct * 0.01, i, f"{p:.1f}%",
                    va="center", fontsize=8.5)
        ax.set_yticks(ypos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("% of total SS (Type-III)")
        ax.set_title(title, fontsize=10)
        ax.grid(True, axis="x", linestyle=":", alpha=0.4)
        ax.set_xlim(0, max_pct * 1.18)
    fig.suptitle("latency 분산 분해 — log(exec_ms) 두 모델 비교", fontsize=11)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig_variance_decomp.{ext}", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 환각 회피 sanity check + summary.md
# ---------------------------------------------------------------------------

def sanity_check(poc1: pd.DataFrame, poc2: pd.DataFrame,
                  poc3: dict, paired: pd.DataFrame) -> list[str]:
    """sanity 기준:
       PoC 평면 = phase2 (sel=0.001) + phase3 (sel=0.01·0.1) carry-over = 580 rows.
       §5.4 보고서 본문 수치 = phase2 만 (168 anchor=B1·180 anchor=baseline·146 small).
       두 평면 모두 검증."""
    msgs = []
    # 확장 평면 (PoC 평면) 합
    n_b1_all = int(poc1[poc1["anchor"] == "B1"]["n"].sum())
    n_base_all = int(poc1[poc1["anchor"] == "baseline"]["n"].sum())
    msgs.append(f"PoC plane (phase2+phase3) — anchor=B1 합 = {n_b1_all} (기대 280) · "
                 f"anchor=baseline 합 = {n_base_all} (기대 300)")
    if n_b1_all != 280:
        msgs.append(f"  ⚠️  B1 합 안 맞음! ({n_b1_all} ≠ 280)")
    if n_base_all != 300:
        msgs.append(f"  ⚠️  baseline 합 안 맞음! ({n_base_all} ≠ 300)")
    # §5.4 합치 검증 — phase=phase2 만 추출
    p2 = paired[paired["phase"] == "phase2"]
    n_b1_p2 = int((p2["anchor"] == "B1").sum())
    n_base_p2 = int((p2["anchor"] == "baseline").sum())
    n_small_b1_p2 = int((p2[p2["anchor"] == "B1"]["hedges_g"].abs() < 0.5).sum())
    n_large_base_p2 = int((p2[p2["anchor"] == "baseline"]["hedges_g"].abs() >= 0.8).sum())
    msgs.append(f"§5.4 합치 (phase2 only) — anchor=B1 = {n_b1_p2} (기대 168) · "
                 f"baseline = {n_base_p2} (기대 180)")
    msgs.append(f"§5.4 합치 (phase2 only) — anchor=B1 small (|g|<0.5) = {n_small_b1_p2} "
                 f"(기대 146 = 86.9%) · baseline large (|g|≥0.8) = {n_large_base_p2} "
                 f"(기대 180 = 100%)")
    if n_b1_p2 != 168 or n_small_b1_p2 != 146:
        msgs.append(f"  ⚠️  §5.4 phase2 B1 합치 안 맞음!")
    if n_base_p2 != 180 or n_large_base_p2 != 180:
        msgs.append(f"  ⚠️  §5.4 phase2 baseline 합치 안 맞음!")
    # 4) PoC 3 % SS 합 ≈ 100 (each model)
    s1 = float(poc3["model1_cell_condition"]["pct_ss"].sum())
    s2 = float(poc3["model2_factor_decomp"]["pct_ss"].sum())
    s3 = float(poc3["model3_no_baseline"]["pct_ss"].sum())
    msgs.append(f"sanity: PoC 3 model1 % SS 합 = {s1:.2f}% (기대 100.0%)")
    msgs.append(f"sanity: PoC 3 model2 % SS 합 = {s2:.2f}% (기대 100.0%)")
    msgs.append(f"sanity: PoC 3 model3 % SS 합 = {s3:.2f}% (기대 100.0%)")
    # 5) model3 (no baseline) 의 condition % SS — §5.4 의 latency 동등성 직접 비교
    m3 = poc3["model3_no_baseline"]
    cond_row = m3[m3["factor"] == "C(cond_str, Sum)"]
    cond_pct_m3 = float(cond_row["pct_ss"].iloc[0]) if len(cond_row) else float("nan")
    msgs.append(f"key finding: model3 (no baseline) condition % SS = "
                 f"{cond_pct_m3:.2f}% — §5.4 latency 동등성 정량")
    # 5) cluster ratio
    md_ratio = float(poc2[poc2["metric"] == "mean_median_diff_ms_B1"]
                      ["width_ratio_cluster_over_naive"].iloc[0])
    sig_ratio = float(poc2[poc2["metric"] == "pct_p_holm_sig_B1"]
                       ["width_ratio_cluster_over_naive"].iloc[0])
    msgs.append(f"sanity: PoC 2 cluster/naïve width ratio — "
                 f"mean_diff={md_ratio:.3f}, %sig={sig_ratio:.3f}")
    return msgs


def write_summary_md(poc1: pd.DataFrame, poc2: pd.DataFrame, poc3: dict,
                      sanity: list[str], out_path: Path) -> None:
    lines = []
    lines.append("# Phase 6 §6.4 통계 후속 PoC — 실측 결과 요약")
    lines.append("")
    lines.append("작성: 2026-05-20 KST · 스크립트 `_internal/scripts/stats_poc_6_4.py`")
    lines.append("")
    lines.append("**PoC 평면**: phase2 (sel=0.001, 12 cell × qid 3) + phase3 (sel=0.01·0.1 carry-over, 4 query × qid=0 × 2 sel = 8 cell) = **20 cell**.")
    lines.append("§5.4 보고서 본문의 168/180/146 수치는 phase2 만의 부분 평면이며, PoC 는 phase3 확장까지 포함한 280/300 평면에서 수행한다.")
    lines.append("")
    lines.append("## PoC 1 — plan-level effect size 분층")
    lines.append("")
    lines.append("anchor=B1 280 비교의 Hedges' g 분포를 plan 회복 여부로 분층 (anchor=baseline 300 비교 동시 보고):")
    lines.append("")
    lines.append("| anchor | plan_recovered | n | small (|g|<0.5) | medium | large (|g|≥0.8) | mean |g| | p_holm<0.05 |")
    lines.append("|---|---|--:|--:|--:|--:|--:|--:|")
    for _, row in poc1.iterrows():
        if row["n"] == 0:
            continue
        lines.append(
            f"| {row['anchor']} | {row['plan_recovered']} | {row['n']} | "
            f"{row['n_small']} ({row['pct_small']:.1f}%) | "
            f"{row['n_medium']} ({row['pct_medium']:.1f}%) | "
            f"{row['n_large']} ({row['pct_large']:.1f}%) | "
            f"{row['mean_abs_g']:.3f} | "
            f"{row['n_p_holm_sig']} ({row['pct_p_holm_sig']:.1f}%) |"
        )
    lines.append("")
    lines.append("## PoC 2 — cluster paired bootstrap (B=2,000, cell 단위 resample)")
    lines.append("")
    lines.append("| metric | point | naïve 95% CI | cluster 95% CI | width ratio (cluster/naïve) |")
    lines.append("|---|--:|--:|--:|--:|")
    for _, row in poc2.iterrows():
        lines.append(
            f"| {row['metric']} | {row['point_estimate']:.3f} | "
            f"[{row['naive_ci_lo']:.3f}, {row['naive_ci_hi']:.3f}] | "
            f"[{row['cluster_ci_lo']:.3f}, {row['cluster_ci_hi']:.3f}] | "
            f"{row['width_ratio_cluster_over_naive']:.3f}× |"
        )
    lines.append("")
    lines.append("## PoC 3 — variance decomposition (Type-III SS, sum-coded contrasts)")
    lines.append("")
    lines.append(f"n_obs (4 condition) = {poc3['n_obs']:,} · n_obs (no baseline) = "
                  f"{poc3['n_obs_no_baseline']:,}")
    lines.append(f"R² — 모델 1 (cell × condition) = {poc3['model1_r2']:.3f} · "
                  f"모델 2 (factor·4 cond) = {poc3['model2_r2']:.3f} · "
                  f"모델 3 (no baseline·B1·CaseB·oracle) = {poc3['model3_r2']:.3f}")
    lines.append("")
    lines.append("**모델 2 — query·qid·sel·condition (4 levels) + 교호작용**")
    lines.append("")
    lines.append("| factor | df | SS | F | p | % SS |")
    lines.append("|---|--:|--:|--:|--:|--:|")
    for _, row in poc3["model2_factor_decomp"].iterrows():
        lines.append(
            f"| {row['factor']} | {row['df']:.0f} | {row['sum_sq']:.3f} | "
            f"{row.get('F', float('nan')):.3f} | "
            f"{row.get('PR(>F)', float('nan')):.3e} | "
            f"{row['pct_ss']:.2f}% |"
        )
    lines.append("")
    lines.append("**모델 3 — baseline 제외 (B1·CaseB·oracle 3 levels) — §5.4 의 B1↔CaseB↔oracle 동등성 직접 검증**")
    lines.append("")
    lines.append("| factor | df | SS | F | p | % SS |")
    lines.append("|---|--:|--:|--:|--:|--:|")
    for _, row in poc3["model3_no_baseline"].iterrows():
        lines.append(
            f"| {row['factor']} | {row['df']:.0f} | {row['sum_sq']:.3f} | "
            f"{row.get('F', float('nan')):.3f} | "
            f"{row.get('PR(>F)', float('nan')):.3e} | "
            f"{row['pct_ss']:.2f}% |"
        )
    lines.append("")
    lines.append("**모델 1 — cell × condition (between-cell vs between-condition 단순 분해)**")
    lines.append("")
    lines.append("| factor | df | SS | F | p | % SS |")
    lines.append("|---|--:|--:|--:|--:|--:|")
    for _, row in poc3["model1_cell_condition"].iterrows():
        lines.append(
            f"| {row['factor']} | {row['df']:.0f} | {row['sum_sq']:.3f} | "
            f"{row.get('F', float('nan')):.3f} | "
            f"{row.get('PR(>F)', float('nan')):.3e} | "
            f"{row['pct_ss']:.2f}% |"
        )
    lines.append("")
    lines.append("## 환각 회피 sanity")
    lines.append("")
    for m in sanity:
        lines.append(f"- {m}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[1/5] raw JSON 로드 — phase2 + phase3")
    r2 = load_results(PHASE2_DIR)
    r3 = load_results(PHASE3_DIR)
    results = r2 + r3
    print(f"  cells: phase2={len(r2)}, phase3={len(r3)}, total={len(results)}")

    print(f"[2/5] paired_stats 로드 + plan_status merge")
    paired = load_paired()
    plan_status = compute_plan_status(results)
    paired = paired.merge(plan_status, on=["cell", "variant"], how="left")
    print(f"  paired_stats rows: {len(paired)}")
    print(f"  plan_recovered 라벨 분포: "
           f"{paired['plan_recovered'].value_counts(dropna=False).to_dict()}")

    print(f"[3/5] PoC 1 — plan-level effect size 분층")
    poc1 = poc1_plan_level_effect_size(paired)
    poc1.to_csv(CSV_DIR / "plan_level_effect_size.csv", index=False)
    print(poc1.to_string(index=False))

    print(f"\n[4/5] PoC 2 — cluster paired bootstrap (B={BOOTSTRAP_B})")
    poc2 = poc2_cluster_bootstrap(paired, B=BOOTSTRAP_B, seed=SEED)
    poc2.to_csv(CSV_DIR / "cluster_bootstrap.csv", index=False)
    print(poc2.to_string(index=False))

    print(f"\n[5/5] PoC 3 — variance decomposition (statsmodels OLS Type-III)")
    poc3 = poc3_variance_decomposition(results)
    poc3["model2_factor_decomp"].to_csv(CSV_DIR / "variance_decomp.csv", index=False)
    poc3["model3_no_baseline"].to_csv(CSV_DIR / "variance_decomp_no_baseline.csv",
                                       index=False)
    poc3["model1_cell_condition"].to_csv(CSV_DIR / "variance_decomp_model1.csv",
                                          index=False)
    print(f"  n_obs={poc3['n_obs']:,} (no baseline {poc3['n_obs_no_baseline']:,}) · "
           f"model1 R²={poc3['model1_r2']:.3f} · model2 R²={poc3['model2_r2']:.3f} · "
           f"model3 R²={poc3['model3_r2']:.3f}")
    print("  [model2] 4 condition factor decomp:")
    print(poc3["model2_factor_decomp"].to_string(index=False))
    print("  [model3] no-baseline (B1·CaseB·oracle) factor decomp:")
    print(poc3["model3_no_baseline"].to_string(index=False))

    print(f"\nfigure 생성")
    fig_plan_level_g(paired, FIG_DIR)
    fig_variance_decomp(poc3, FIG_DIR)
    print(f"  saved → {FIG_DIR}")

    print(f"\nsanity check")
    sanity = sanity_check(poc1, poc2, poc3, paired)
    for m in sanity:
        print(f"  {m}")

    write_summary_md(poc1, poc2, poc3, sanity, CSV_DIR / "summary.md")
    print(f"\nsummary.md → {CSV_DIR / 'summary.md'}")
    print(f"\n완료 — 산출 디렉토리:")
    print(f"  · {CSV_DIR}/")
    print(f"  · {FIG_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
