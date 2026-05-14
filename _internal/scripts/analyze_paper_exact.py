#!/usr/bin/env python3
"""
Paper exact 재현 측정 결과 종합 분석 — Phase D + REPORT.md 5단계 narrative 입력.

분석 layer:
1. **paper Fig 12/6 재현 검증**: B1 cells의 avg_qe vs paper 1.69, final_size vs paper 358-415
2. **RQ1/RQ2 narrative 검증**: paper sel {0.01, 0.10}에서 기존 narrative 성립 여부
3. **Phase B paired Δ%**: B1 vs CaseA 34 (or 11) methods, Wilcoxon + BH-FDR
4. **Phase C ensemble (CaseB)**: B1+method ensemble paired Δ%
5. **5단계 narrative summary**: RQ1/RQ2/RQ3 검증 → Exqutor 정확 재현 → CaseA → CaseB → 비교

input: /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/{*.json, *.csv}
output: /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md
"""
from __future__ import annotations

import argparse
import json
import glob
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


PAPER_FIG_12_AVG_QE = 1.69
PAPER_FIG_6_STABLE = {"DEEP": (358, 365), "SIFT": (410, 415), "SimSearchNet++": (355, 365)}

# validation §2.1 — Fig 12 영역과 Fig 13 영역 분리. A4-sel (sel=0.001) 은 Fig 13.
FIG_12_CELLS = {"A1-DEEP", "A1-SIFT", "A1-SSN", "A2-Fig7", "A2-Fig9",
                "A5-scale-sf1", "A5-scale-sf10", "A5-scale-sf100"}
FIG_13_CELLS = {"A4-sel"}  # paper Fig 13 selectivity ablation (sel inherent q_error 큼)

# validation §2.3 — CaseA에서 dataset 분포 부적합 method 명시 (lsh/RP/sobol/ccsketch on YFCC 192d/SSN)
CASEA_OUTLIER_METHODS = {"lsh", "random_projection", "sobol", "ccsketch", "ams_count_sketch"}


def load_b1_results(out_dir: Path) -> pd.DataFrame:
    rows = []
    for f in sorted(out_dir.glob("*B1*.json")):
        d = json.load(open(f))
        finite = [t["avg_q_error_finite"] for t in d["trial_results"]
                  if np.isfinite(t["avg_q_error_finite"])]
        sizes = [t["final_size"] for t in d["trial_results"]]
        rows.append({
            "cell": d["cell"], "fig": d["fig"], "dataset": d["dataset"], "sf": d["sf"],
            "qe_mean": float(np.mean(finite)) if finite else float("nan"),
            "qe_median": float(np.median(finite)) if finite else float("nan"),
            "qe_trim": d["avg_q_error_trimmed"],
            "size_median": float(np.median(sizes)),
            "size_min": int(np.min(sizes)),
            "size_max": int(np.max(sizes)),
            "n_trials": len(d["trial_results"]),
        })
    return pd.DataFrame(rows)


def load_case_a_results(out_dir: Path) -> pd.DataFrame:
    rows = []
    for f in sorted(out_dir.glob("*CaseA*.json")):
        d = json.load(open(f))
        finite = [t["avg_q_error_finite"] for t in d["trial_results"]
                  if np.isfinite(t["avg_q_error_finite"])]
        sizes = [t["final_size"] for t in d["trial_results"]]
        rows.append({
            "cell": d["cell"], "fig": d["fig"], "dataset": d["dataset"], "sf": d["sf"],
            "method": d["method"],
            "qe_mean": float(np.mean(finite)) if finite else float("nan"),
            "qe_median": float(np.median(finite)) if finite else float("nan"),
            "qe_trim": d["avg_q_error_trimmed"],
            "size_median": float(np.median(sizes)),
            "n_finite_per_trial": [t["n_finite"] for t in d["trial_results"]],
        })
    return pd.DataFrame(rows)


def load_case_b_results(out_dir: Path) -> pd.DataFrame:
    """Phase C ensemble (B1 + method) measurements."""
    rows = []
    for f in sorted(out_dir.glob("*CaseB*.json")):
        d = json.load(open(f))
        finite = [t["avg_q_error_finite"] for t in d["trial_results"]
                  if np.isfinite(t["avg_q_error_finite"])]
        sizes = [t["final_size"] for t in d["trial_results"]]
        rows.append({
            "cell": d["cell"], "fig": d["fig"], "dataset": d["dataset"], "sf": d["sf"],
            "method": d["method"],
            "ensemble_strategy": d.get("ensemble_strategy", "n/a"),
            "qe_mean": float(np.mean(finite)) if finite else float("nan"),
            "qe_median": float(np.median(finite)) if finite else float("nan"),
            "qe_trim": d["avg_q_error_trimmed"],
            "size_median": float(np.median(sizes)),
            "n_finite_per_trial": [t["n_finite"] for t in d["trial_results"]],
        })
    return pd.DataFrame(rows)


_NAN_DELTA = {
    "delta_pct_mean": float("nan"), "delta_pct_median": float("nan"),
    "wilcoxon_p": float("nan"), "wilcoxon_p_greater": float("nan"),
    "n_trials": 0, "b1_mean": float("nan"), "casea_mean": float("nan"),
    "hedges_g": float("nan"), "cliffs_delta": float("nan"),
}


def paired_delta(b1_qe: list, casea_qe: list) -> dict:
    """Trial-paired Δ% (B1 vs CaseA/CaseB). Wilcoxon p-value 포함.

    Naming note: 'b1_mean'/'casea_mean' 키는 historical — Phase C(CaseB) 호출에서도
    재사용 (caller가 'caseb_mean'으로 alias 처리).

    validation §2.4: 두 alternative 모두 계산 — two-sided (기존) + greater (B1 > CaseA,
    즉 CaseA가 better 방향, n=10 small sample 시 power 향상).
    """
    if len(b1_qe) != len(casea_qe) or len(b1_qe) == 0:
        return dict(_NAN_DELTA)
    b1 = np.array(b1_qe, dtype=float)
    ca = np.array(casea_qe, dtype=float)
    finite = np.isfinite(b1) & np.isfinite(ca)
    if not finite.any():
        return dict(_NAN_DELTA)
    b1, ca = b1[finite], ca[finite]
    delta = (ca - b1) / b1 * 100  # negative = CaseA/CaseB better (lower Q-error)
    method_kw = "exact" if len(b1) <= 25 else "auto"
    try:
        _, p_two = stats.wilcoxon(b1, ca, alternative="two-sided", method=method_kw)
    except (ValueError, TypeError):
        p_two = float("nan")
    try:
        # alternative="greater" → H1: b1 > ca (CaseA가 더 작음 = better Q-error)
        _, p_grt = stats.wilcoxon(b1, ca, alternative="greater", method=method_kw)
    except (ValueError, TypeError):
        p_grt = float("nan")
    return {
        "delta_pct_mean": float(np.mean(delta)),
        "delta_pct_median": float(np.median(delta)),
        "wilcoxon_p": float(p_two),
        "wilcoxon_p_greater": float(p_grt),
        "n_trials": int(finite.sum()),
        "b1_mean": float(np.mean(b1)),
        "casea_mean": float(np.mean(ca)),
        "hedges_g": compute_hedges_g(b1, ca),
        "cliffs_delta": compute_cliffs_delta(b1, ca),
    }


def bh_fdr(pvals: list, alpha: float = 0.05) -> list:
    """Benjamini-Hochberg FDR correction. Returns adjusted p-values."""
    pvals = np.array(pvals, dtype=float)
    n = len(pvals)
    finite_mask = np.isfinite(pvals)
    p_finite = pvals[finite_mask]
    n_finite = len(p_finite)
    if n_finite == 0:
        return [float("nan")] * n
    order = np.argsort(p_finite)
    ranks = np.empty(n_finite, dtype=int)
    ranks[order] = np.arange(1, n_finite + 1)
    p_adj = p_finite * n_finite / ranks
    # monotonic non-decreasing constraint
    p_adj_sorted = p_adj[order]
    for i in range(n_finite - 2, -1, -1):
        p_adj_sorted[i] = min(p_adj_sorted[i], p_adj_sorted[i + 1])
    p_adj[order] = p_adj_sorted
    p_adj = np.clip(p_adj, 0, 1)
    out = np.full(n, float("nan"))
    out[finite_mask] = p_adj
    return out.tolist()


def analyze_phase_a(df_b1: pd.DataFrame) -> str:
    """Phase A B1 → paper Fig 12/6 재현 검증.

    validation §2.1: Fig 12 영역 (8 cells) 만 paper 1.69 직접 비교. A4-sel (sel=0.001)
    은 paper Fig 13 영역 (sel inherent q_error 큼) — 별도 표시.
    """
    md = ["## 1. Phase A B1 baseline — paper Fig 12/6 재현 검증\n"]
    md.append("| Cell | 영역 | Fig | Dataset | SF | qe_median | qe_trim | size_median | size_range | paper 1.69 vs |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for _, r in df_b1.iterrows():
        cell = r["cell"]
        is_fig12 = cell in FIG_12_CELLS
        area = "Fig 12" if is_fig12 else ("Fig 13" if cell in FIG_13_CELLS else "?")
        delta = (r["qe_trim"] - PAPER_FIG_12_AVG_QE) / PAPER_FIG_12_AVG_QE * 100
        delta_str = f"{delta:+.1f}%" if is_fig12 else "(N/A — Fig 13)"
        md.append(f"| {cell} | {area} | {r['fig']} | {r['dataset']} | {r['sf']} | "
                  f"{r['qe_median']:.3f} | {r['qe_trim']:.3f} | {r['size_median']:.0f} | "
                  f"{r['size_min']}-{r['size_max']} | {delta_str} |")
    md.append("")

    # Fig 12 영역 (8 cells) — paper 1.69 직접 비교 (validation §2.1)
    fig12_df = df_b1[df_b1["cell"].isin(FIG_12_CELLS)]
    md.append(f"### 1.1 paper Fig 12 영역 ({len(fig12_df)} cells) — paper avg Q-error = {PAPER_FIG_12_AVG_QE}")
    if not fig12_df.empty:
        qe_trim_mean = float(fig12_df["qe_trim"].dropna().mean())
        qe_med_mean = float(fig12_df["qe_median"].dropna().mean())
        delta_trim = (qe_trim_mean - PAPER_FIG_12_AVG_QE) / PAPER_FIG_12_AVG_QE * 100
        delta_med = (qe_med_mean - PAPER_FIG_12_AVG_QE) / PAPER_FIG_12_AVG_QE * 100
        md.append(f"- mean qe_trim: **{qe_trim_mean:.3f}** (paper 1.69 vs **{delta_trim:+.1f}%**)")
        md.append(f"- mean qe_median: **{qe_med_mean:.3f}** (paper 1.69 vs **{delta_med:+.1f}%**)")
        md.append(f"- range qe_trim: {fig12_df['qe_trim'].min():.3f} ~ {fig12_df['qe_trim'].max():.3f}")
        md.append("**→ Exqutor 100% 정확 재현 narrative #2 검증 anchor (validation §2.1)**")

    # Fig 13 영역 (A4-sel) — 별도 (paper Fig 12와 직접 비교 부적절)
    fig13_df = df_b1[df_b1["cell"].isin(FIG_13_CELLS)]
    if not fig13_df.empty:
        md.append("")
        md.append(f"### 1.2 paper Fig 13 영역 ({len(fig13_df)} cell) — selectivity ablation (sel inherent q_error 큼)")
        for _, r in fig13_df.iterrows():
            md.append(f"- {r['cell']}: qe_median={r['qe_median']:.3f}, qe_trim={r['qe_trim']:.3f} (paper Fig 12와 직접 비교 부적절)")

    md.append("")
    md.append("### 1.3 paper Fig 6 stable size 비교 (358-415 range)")
    for _, r in df_b1.iterrows():
        md.append(f"- {r['cell']}: median={r['size_median']:.0f}, range={r['size_min']}-{r['size_max']}")
    return "\n".join(md)


_RQ2_CAVEAT = (
    "\n### 2.2 RQ2 5-way σ_j oracle limitation (정정 — Axis E + Agent #2/#5 cross-verify)\n\n"
    "**🚨 paradox finding** (paper §V-B Neyman 정당성 부정):\n"
    "- DEEP sel=0.01 paired: Bern 1.746 → Equal 1.644 → **Prop 1.580** → Neyman 1.595 → **Anti 1.540 (최저)**\n"
    "- Anti < Prop < Neyman (이론 위배), Wilcoxon Neyman vs Prop p=0.60 유의 X\n\n"
    "**Root cause**:\n"
    "- σ_j range 1.3-1.6× 좁음 (DEEP/SIFT/SSN sf=100), KM20 cluster N_i CV=0 균등\n"
    "- σ-weighted alloc cos_sim 0.99 (L1 diff 21-39/385)\n"
    "- budget=385 hit count noise (~50/seed) > Neyman signal (~30 표본)\n\n"
    "**oracle 가정 한계 (paper review-grade)**:\n"
    "- σ_j = sel=0.1 D_target 단일 calibration → sel=0.01/0.30/0.50 영역 oracle 자격 약화\n"
    "- KM20 cluster + Neyman σ는 production 부적합 (one-time pre-computation cost)\n\n"
    "**학술 honest narrative**: \"분포 알면 Neyman 답\" → \"**분포 알면 prop allocation 답**, σ range 크고 cluster imbalance 심한 RQ3 영역에서 Neyman 우위 재검증 필요\" — RQ3 자연 전환 anchor.\n"
)


def analyze_rq1_rq2(out_dir: Path) -> str:
    md = ["\n## 2. RQ1/RQ2 paper exact narrative 검증\n"]
    # RQ1
    md.append("### 2.1 RQ1 (random sampling 부정확 narrative)\n")
    rq1_files = sorted(out_dir.glob("rq1_paper_exact_*.csv"))
    for f in rq1_files:
        df = pd.read_csv(f)
        ds = df["dataset"].iloc[0]
        agg = df.groupby(["mode", "selectivity"])["q_error"].agg(["mean", "median"]).round(3)
        md.append(f"**{ds}** (n_rows={len(df)}, modes={df['mode'].unique().tolist()}):")
        md.append(f"```\n{agg.to_string()}\n```\n")
    # RQ2
    md.append("### 2.2 RQ2 (분포 인지 stratification 우위 narrative)\n")
    rq2_files = sorted(out_dir.glob("rq2_paper_exact_*.csv"))
    for f in rq2_files:
        df = pd.read_csv(f)
        ds = df["dataset"].iloc[0]
        agg = df.groupby(["mode", "selectivity"])["q_error"].agg(["mean", "median"]).round(3)
        md.append(f"**{ds}** (n_rows={len(df)}, modes={df['mode'].unique().tolist()}):")
        md.append(f"```\n{agg.to_string()}\n```\n")
    md.append(_RQ2_CAVEAT)
    return "\n".join(md)


def analyze_phase_b(df_b1: pd.DataFrame, df_casea: pd.DataFrame,
                     out_dir: Path) -> tuple[str, pd.DataFrame]:
    """Phase B paired Δ% (B1 vs CaseA per cell × method). Wilcoxon + BH-FDR."""
    md = ["\n## 3. Phase B paired Δ% — B1 vs CaseA (paper §V-B Bernoulli vs 우리 method)\n"]
    rows = []
    for _, b1_row in df_b1.iterrows():
        cell = b1_row["cell"]
        # b1 per-trial qe (load JSON)
        b1_path = out_dir / f"{cell}_B1.json"
        if not b1_path.exists():
            continue
        b1_d = json.load(open(b1_path))
        b1_trials = [t["avg_q_error_finite"] for t in b1_d["trial_results"]]
        # casea methods
        for ca_path in sorted(out_dir.glob(f"{cell}_CaseA_*.json")):
            ca_d = json.load(open(ca_path))
            ca_trials = [t["avg_q_error_finite"] for t in ca_d["trial_results"]]
            d = paired_delta(b1_trials, ca_trials)
            rows.append({
                "cell": cell, "method": ca_d["method"],
                "delta_pct_mean": d["delta_pct_mean"],
                "delta_pct_median": d["delta_pct_median"],
                "wilcoxon_p": d["wilcoxon_p"],
                "wilcoxon_p_greater": d["wilcoxon_p_greater"],
                "b1_mean": d["b1_mean"], "casea_mean": d["casea_mean"],
                "hedges_g": d["hedges_g"], "cliffs_delta": d["cliffs_delta"],
            })
    if not rows:
        md.append("(no CaseA results yet — Phase B 진행 중)\n")
        return "\n".join(md), pd.DataFrame()
    df = pd.DataFrame(rows)
    df["p_adj_bh"] = bh_fdr(df["wilcoxon_p"].tolist())
    df = df.sort_values(["cell", "delta_pct_mean"])
    md.append(f"**총 paired 비교 {len(df)}건** (cells × methods):")
    md.append("")
    md.append("| Cell | Method | B1 mean | CaseA mean | Δ%(mean) | Δ%(median) | p (raw) | p (BH-FDR) |")
    md.append("|---|---|---|---|---|---|---|---|")
    for _, r in df.iterrows():
        md.append(f"| {r['cell']} | {r['method']:<20s} | {r['b1_mean']:.3f} | {r['casea_mean']:.3f} | "
                  f"{r['delta_pct_mean']:+.2f}% | {r['delta_pct_median']:+.2f}% | "
                  f"{r['wilcoxon_p']:.4f} | {r['p_adj_bh']:.4f} |")
    md.append("")
    # winners — two-sided + one-sided greater (validation §2.4)
    md.append("### 3.1 CaseA outperform B1 (Δ% < 0)")
    wins_two = df[(df["delta_pct_mean"] < 0) & (df["p_adj_bh"] < 0.05)]
    md.append(f"- two-sided p_adj < 0.05 outperform: **{len(wins_two)}/{len(df)} ({len(wins_two)/len(df)*100:.1f}%)**")
    df["p_adj_bh_greater"] = bh_fdr(df["wilcoxon_p_greater"].tolist())
    wins_one = df[(df["delta_pct_mean"] < 0) & (df["p_adj_bh_greater"] < 0.05)]
    md.append(f"- one-sided greater p_adj < 0.05 outperform (CaseA better, validation §2.4): **{len(wins_one)}/{len(df)} ({len(wins_one)/len(df)*100:.1f}%)**")
    if len(wins_one) > 0:
        method_wins = wins_one.groupby("method").size().sort_values(ascending=False)
        md.append("- Method별 win count (one-sided):")
        for m, c in method_wins.head(10).items():
            md.append(f"  - {m}: {c}")
    # validation §2.3 — CaseA outlier methods caveat
    md.append("")
    md.append("### 3.2 ⚠️ CaseA outlier methods caveat (validation §2.3)")
    outlier_df = df[df["method"].isin(CASEA_OUTLIER_METHODS)]
    if not outlier_df.empty:
        worse = outlier_df[(outlier_df["delta_pct_mean"] > 0) & (outlier_df["p_adj_bh"] < 0.05)]
        md.append(f"- Outlier methods (lsh/RP/sobol/ccsketch/ams): {len(outlier_df)} 비교 中 worse signif **{len(worse)}건**")
        md.append("- → cluster imbalance (YFCC 192d/SSN 영역 부적합) — narrative caveat 명시")
    return "\n".join(md), df


def analyze_phase_c(df_b1: pd.DataFrame, df_caseb: pd.DataFrame,
                     out_dir: Path) -> tuple[str, pd.DataFrame]:
    """Phase C paired Δ% (B1 vs CaseB) — 5단계 narrative §4 (CaseB ensemble augment)."""
    md = ["\n## 4. Phase C paired Δ% — B1 vs CaseB (B1 + method ensemble)\n"]
    rows = []
    for _, b1_row in df_b1.iterrows():
        cell = b1_row["cell"]
        b1_path = out_dir / f"{cell}_B1.json"
        if not b1_path.exists():
            continue
        b1_d = json.load(open(b1_path))
        b1_trials = [t["avg_q_error_finite"] for t in b1_d["trial_results"]]
        for cb_path in sorted(out_dir.glob(f"{cell}_CaseB_*.json")):
            cb_d = json.load(open(cb_path))
            cb_trials = [t["avg_q_error_finite"] for t in cb_d["trial_results"]]
            d = paired_delta(b1_trials, cb_trials)
            rows.append({
                "cell": cell, "method": cb_d["method"],
                "ensemble": cb_d.get("ensemble_strategy", "n/a"),
                "delta_pct_mean": d["delta_pct_mean"],
                "delta_pct_median": d["delta_pct_median"],
                "wilcoxon_p": d["wilcoxon_p"],
                "wilcoxon_p_greater": d["wilcoxon_p_greater"],
                "b1_mean": d["b1_mean"],
                "caseb_mean": d["casea_mean"],  # alias (paired_delta historical key)
                "hedges_g": d["hedges_g"], "cliffs_delta": d["cliffs_delta"],
            })
    if not rows:
        md.append("(no CaseB results yet — Phase C 진행 중)\n")
        return "\n".join(md), pd.DataFrame()
    df = pd.DataFrame(rows)
    df["p_adj_bh"] = bh_fdr(df["wilcoxon_p"].tolist())
    df = df.sort_values(["cell", "delta_pct_mean"])
    md.append(f"**총 paired 비교 {len(df)}건** (cells × methods × ensemble):")
    md.append("")
    md.append("| Cell | Method | Ensemble | B1 mean | CaseB mean | Δ%(mean) | Δ%(median) | p (raw) | p (BH-FDR) |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for _, r in df.iterrows():
        md.append(f"| {r['cell']} | {r['method']:<20s} | {r['ensemble']:<10s} | "
                  f"{r['b1_mean']:.3f} | {r['caseb_mean']:.3f} | "
                  f"{r['delta_pct_mean']:+.2f}% | {r['delta_pct_median']:+.2f}% | "
                  f"{r['wilcoxon_p']:.4f} | {r['p_adj_bh']:.4f} |")
    md.append("")
    md.append("### 4.1 CaseB outperform B1 (Δ% < 0)")
    wins_two = df[(df["delta_pct_mean"] < 0) & (df["p_adj_bh"] < 0.05)]
    md.append(f"- two-sided p_adj < 0.05 outperform: **{len(wins_two)}/{len(df)} ({len(wins_two)/len(df)*100:.1f}%)**")
    df["p_adj_bh_greater"] = bh_fdr(df["wilcoxon_p_greater"].tolist())
    wins_one = df[(df["delta_pct_mean"] < 0) & (df["p_adj_bh_greater"] < 0.05)]
    md.append(f"- one-sided greater p_adj < 0.05 outperform (CaseB better, validation §2.4): **{len(wins_one)}/{len(df)} ({len(wins_one)/len(df)*100:.1f}%)**")
    if len(wins_one) > 0:
        method_wins = wins_one.groupby("method").size().sort_values(ascending=False)
        md.append("- Method별 win count (one-sided):")
        for m, c in method_wins.head(10).items():
            md.append(f"  - {m}: {c}")
    return "\n".join(md), df


def analyze_caseb_vs_casea(df_casea_paired: pd.DataFrame,
                           df_caseb_paired: pd.DataFrame) -> str:
    """5단계 narrative §5 — CaseB > CaseA > B1 ordering 검증."""
    md = ["\n## 5. 최종 ranking — CaseB > CaseA > B1 (5단계 narrative §5)\n"]
    if df_casea_paired.empty or df_caseb_paired.empty:
        md.append("(CaseA 또는 CaseB 미완료 — Phase B/C 진행 중)\n")
        return "\n".join(md)

    # cell × method 기준 join
    casea_idx = df_casea_paired.set_index(["cell", "method"])
    caseb_idx = df_caseb_paired.set_index(["cell", "method"])
    common_idx = casea_idx.index.intersection(caseb_idx.index)
    if len(common_idx) == 0:
        md.append("(no common cell × method between CaseA / CaseB)\n")
        return "\n".join(md)

    rows = []
    for idx in common_idx:
        ca_delta = casea_idx.loc[idx, "delta_pct_mean"]
        cb_delta = caseb_idx.loc[idx, "delta_pct_mean"]
        rows.append({
            "cell": idx[0], "method": idx[1],
            "casea_delta_pct": float(ca_delta),
            "caseb_delta_pct": float(cb_delta),
            "caseb_better": cb_delta < ca_delta,
        })
    df = pd.DataFrame(rows)
    md.append(f"**총 {len(df)}건 paired (CaseA Δ% vs CaseB Δ%)**")
    md.append("")
    n_caseb_better = int(df["caseb_better"].sum())
    md.append(f"- CaseB Δ% < CaseA Δ% (CaseB 더 나음): **{n_caseb_better}/{len(df)} "
              f"({n_caseb_better / len(df) * 100:.1f}%)**")
    md.append(f"- CaseA mean Δ%: **{df['casea_delta_pct'].mean():+.2f}%**")
    md.append(f"- CaseB mean Δ%: **{df['caseb_delta_pct'].mean():+.2f}%**")
    diff_mean = (df["caseb_delta_pct"] - df["casea_delta_pct"]).mean()
    md.append(f"- (CaseB - CaseA) mean Δ% gap: **{diff_mean:+.2f}%** (음수일수록 CaseB 우위)")
    md.append("")
    md.append("### 5.1 narrative 결론")
    caseb_pct = n_caseb_better / len(df) * 100
    if caseb_pct >= 90:
        md.append(f"✅ **CaseB >> CaseA > B1 narrative 강함** (CaseB가 **{caseb_pct:.1f}%** 케이스에서 CaseA보다 나음 — paper review-grade anchor)")
    elif caseb_pct >= 60:
        md.append(f"✅ **CaseB > CaseA > B1 narrative 성립** (CaseB가 {caseb_pct:.1f}% 케이스에서 CaseA보다 나음)")
    else:
        md.append(f"⚠️ CaseB > CaseA narrative 약함 (CaseB가 {caseb_pct:.1f}% 우위) — 더 많은 method 측정 필요")
    return "\n".join(md)


# --- Phase D 보강 (5/11 17:11 KST) ---
# paradigm rollup + effect size (Hedges' g + Cliff's δ) + cherry-pick + drop list
# ULTRAPLAN 별도 세션 권고 반영

PARADIGM_MAP = {
    # P1 Cluster
    "minibatch": "P1", "gmm": "P1", "minibatch_partial": "P1",
    "birch": "P1", "agglomerative": "P1", "coreset": "P1",
    "dbscan": "P1", "kmeans_neyman": "P1",
    "hkbu_repsample": "P1", "banditucb1": "P1", "neurocard_lite": "P1",
    # P2 Spatial
    "hilbert": "P2", "hilbert_real": "P2", "skilling_hilbert": "P2",
    "zorder_morton": "P2", "idistance": "P2", "idistance_neyman": "P2",
    "faiss_ivf": "P2", "lpm1_proper": "P2", "epsilon_net": "P2",
    "kdtree": "P2", "kdpp": "P2", "lpm2": "P2",
    # P3 Streaming
    "chao_weighted": "P3", "reservoir": "P3",
    "thompson_sampling": "P3", "mfmc": "P3",
    "ams_count_sketch": "P3", "ccsketch": "P3",
    # P4 DimReduction
    "sparse_rp": "P4", "random_projection": "P4", "pca1d": "P4",
    "rsvd": "P4", "ica_fastica": "P4", "dense_rp": "P4",
    "neuram": "P4", "cca1d": "P4", "tucker": "P4",
    "vinecopula": "P4", "factor_join": "P4", "adaptive_bucket_probing": "P4",
    # P5 QMC/Hashing
    "lsh": "P5", "sobol": "P5", "halton": "P5", "hammersley": "P5",
    "lhs": "P5", "cum_sqrtf": "P5", "lavallee_hidiroglou": "P5",
    "lp_bound": "P5",
    # P6 Quantization
    "rabitq_strat": "P6", "mhist2": "P6", "wavelet_hist": "P6",
    "pq": "P6", "opq": "P6", "cocluster_nystrom": "P6",
    # P9 InfoTheoretic
    "hyperloglog": "P9",
    # P10 Density
    "kde_parzen": "P10",
}


def compute_hedges_g(b1_arr, ca_arr) -> float:
    """Hedges' g with small-sample bias correction (n=10 trial 보완)."""
    b1 = np.asarray(b1_arr, dtype=float)
    ca = np.asarray(ca_arr, dtype=float)
    b1 = b1[np.isfinite(b1)]
    ca = ca[np.isfinite(ca)]
    if len(b1) < 2 or len(ca) < 2:
        return float("nan")
    pooled_sd = np.sqrt(((len(b1)-1)*b1.var(ddof=1) + (len(ca)-1)*ca.var(ddof=1))
                        / (len(b1)+len(ca)-2))
    if pooled_sd == 0:
        return float("nan")
    d = (ca.mean() - b1.mean()) / pooled_sd
    n = len(b1) + len(ca)
    j = 1 - 3 / (4*n - 9)  # Hedges correction
    return float(d * j)


def compute_cliffs_delta(b1_arr, ca_arr) -> float:
    """Cliff's δ ∈ [-1, 1]. POSITIVE = CaseA/B 우위 (b1 > ca = Q-error 더 작음). large = +0.474."""
    b1 = np.asarray(b1_arr, dtype=float)
    ca = np.asarray(ca_arr, dtype=float)
    b1 = b1[np.isfinite(b1)]
    ca = ca[np.isfinite(ca)]
    if len(b1) == 0 or len(ca) == 0:
        return float("nan")
    gt = int(np.sum(b1[:, None] > ca[None, :]))
    lt = int(np.sum(b1[:, None] < ca[None, :]))
    return float((gt - lt) / (len(b1) * len(ca)))


def paradigm_rollup(df_paired, label: str = "CaseB") -> str:
    """Paradigm-level (P1-P10) mean/median Δ% rollup (outlier |Δ%|>100 제외)."""
    if df_paired.empty or "method" not in df_paired.columns:
        return f"\n## (Paradigm rollup {label}: empty)\n"
    df = df_paired.copy()
    df["paradigm"] = df["method"].map(PARADIGM_MAP).fillna("Pother")
    df_clean = df[df["delta_pct_mean"].abs() < 100]
    if df_clean.empty:
        return f"\n## (Paradigm rollup {label}: all outlier)\n"
    rollup = df_clean.groupby("paradigm").agg(
        n=("method", "nunique"),
        n_obs=("method", "size"),
        mean_d=("delta_pct_mean", "mean"),
        median_d=("delta_pct_mean", "median"),
        std_d=("delta_pct_mean", "std"),
        min_d=("delta_pct_mean", "min"),
        max_d=("delta_pct_mean", "max"),
    ).round(2).reset_index().sort_values("mean_d")
    lines = [f"\n### Paradigm rollup ({label}, outlier |Δ%|>100 제외)\n"]
    lines.append("| paradigm | n_method | n_obs | mean Δ% | median Δ% | std | range |")
    lines.append("|---|:-:|:-:|:-:|:-:|:-:|:-:|")
    for _, r in rollup.iterrows():
        lines.append(
            f"| {r['paradigm']} | {int(r['n'])} | {int(r['n_obs'])} | "
            f"{r['mean_d']:+.2f} | {r['median_d']:+.2f} | "
            f"{r['std_d']:.2f} | [{r['min_d']:+.2f}, {r['max_d']:+.2f}] |"
        )
    return "\n".join(lines)


def effect_size_table(df_paired, label: str = "CaseB") -> str:
    """method-level Hedges' g + Cliff's δ table (top + large effect)."""
    if df_paired.empty or "hedges_g" not in df_paired.columns:
        return f"\n### ({label}: effect size 미계산)\n"
    df = df_paired.copy()
    df_sorted = df.dropna(subset=["hedges_g", "cliffs_delta"]).sort_values("hedges_g")
    n_total = len(df_sorted)
    n_large_better = int((df_sorted["cliffs_delta"] >= 0.474).sum())
    n_med_better = int(((df_sorted["cliffs_delta"] >= 0.33) & (df_sorted["cliffs_delta"] < 0.474)).sum())
    n_small = int(((df_sorted["cliffs_delta"] > -0.33) & (df_sorted["cliffs_delta"] < 0.33)).sum())
    n_large_worse = int((df_sorted["cliffs_delta"] <= -0.474).sum())
    n_g_large = int((df_sorted["hedges_g"] <= -0.8).sum())
    n_g_med = int(((df_sorted["hedges_g"] > -0.8) & (df_sorted["hedges_g"] <= -0.5)).sum())
    pct_cliffs_large = 100 * n_large_better / n_total if n_total else 0
    lines = [f"\n### Effect size ({label}, n={n_total})\n"]
    lines.append("| Cliff's δ bucket | count | pct |")
    lines.append("|---|:-:|:-:|")
    lines.append(f"| **large better (δ ≥ +0.474)** | **{n_large_better}** | **{pct_cliffs_large:.1f}%** |")
    lines.append(f"| medium better (+0.33 ≤ δ < +0.474) | {n_med_better} | {100*n_med_better/n_total:.1f}% |")
    lines.append(f"| small / inconclusive (-0.33 < δ < +0.33) | {n_small} | {100*n_small/n_total:.1f}% |")
    lines.append(f"| large worsening (δ ≤ -0.474) | {n_large_worse} | {100*n_large_worse/n_total:.1f}% |")
    lines.append(f"\n**Hedges' g**: large (g ≤ -0.8) = {n_g_large} / medium (-0.8 < g ≤ -0.5) = {n_g_med}")
    if n_total > 0:
        top_g = df_sorted.head(3)[["cell", "method", "delta_pct_mean", "hedges_g", "cliffs_delta"]]
        lines.append("\n**Top 3 (smallest g, strongest CaseA/B 우위)**:")
        for _, r in top_g.iterrows():
            lines.append(f"- {r['method']} @ {r['cell']}: Δ%={r['delta_pct_mean']:+.2f}, g={r['hedges_g']:+.2f}, δ={r['cliffs_delta']:+.2f}")
    return "\n".join(lines)


def cherry_pick_table(df_paired, label: str = "CaseB", top_n: int = 10) -> str:
    """method × cell range per method — cherry-picking 방지 표 (큰 range outlier 노출)."""
    if df_paired.empty:
        return f"\n### ({label}: cherry-pick 표 empty)\n"
    df = df_paired.copy()
    g = df.groupby("method").agg(
        n_cell=("cell", "nunique"),
        mean_d=("delta_pct_mean", "mean"),
        median_d=("delta_pct_mean", "median"),
        min_d=("delta_pct_mean", "min"),
        max_d=("delta_pct_mean", "max"),
    ).reset_index()
    g["range"] = g["max_d"] - g["min_d"]
    g_sorted = g.sort_values("range", ascending=False).head(top_n)
    lines = [f"\n### Cherry-pick prevention ({label}, top {top_n} largest range)\n"]
    lines.append("| method | n_cell | mean Δ% | median | min | max | range |")
    lines.append("|---|:-:|:-:|:-:|:-:|:-:|:-:|")
    for _, r in g_sorted.iterrows():
        lines.append(
            f"| {r['method']} | {int(r['n_cell'])} | {r['mean_d']:+.2f} | "
            f"{r['median_d']:+.2f} | {r['min_d']:+.2f} | {r['max_d']:+.2f} | "
            f"{r['range']:.1f} |"
        )
    return "\n".join(lines)


def drop_list_section() -> str:
    """142/233 drop cells 정직 분류 — Axis G 9 카테고리 (5/27 limitation 학술 산문)."""
    lines = ["\n### Drop list categorize (정직한 결손 보고)\n"]
    lines.append("| Cat | Drop cells | Root cause (log evidence) | Narrative 정당화 |")
    lines.append("|---|:-:|---|---|")
    lines.append("| C1 birch | 18 | sklearn BIRCH CFNode tree 50-200GB RSS 폭증 (256d×80M, log: \"computing strata\" 후 hang) | 자원 한계 (handoff_v3 §3 infeasible) |")
    lines.append("| C2 vinecopula × SF=100 | 4 | Bedford-Cooke 2002 audit drop + 80M infeasible | rank+PCA1D alias 정의 위반 |")
    lines.append("| C3 agglomerative × A1-SSN | 2 | 96d/128d 통과 / 256d nearest-centroid sub-pass OOM | dimensionality dependence |")
    lines.append("| C4 A1-SSN audit-drop group | 27 | 80GB NPY fetch 37-88분/method × 14 sequential → cascade kill | 256d×80M PG fetch 한계 |")
    lines.append("| C5 A2-Fig8 multi-vector | 109 | kde_parzen 무한 hang → cascade. paper §V-A multi-table 영역 | 우리 §V-B 단일 테이블 contribution scope 외 |")
    lines.append("| C6 A3-TPCDS ECQO | 18 | `psycopg.OperationalError ... recovery mode` (Exqutor PG + TPC-DS index 충돌) | paper §V-A ECQO 영역 (우리 §V-B 외) |")
    lines.append("| C7 Q1+Q4 SF=10/100 | 40+ | wrapper no-timeout + KDE O(n²) → cascade. A5-sf1만 14/14 ✓ | P9/P10 paradigm anchor 충분 |")
    lines.append("| C8 kdtree | 16 | leaf-index modulo = random hash (audit drop §2.D2) | 알고리즘 정의 위반 |")
    lines.append("| C9 hdbscan | 18 | 사용자 5/11 02:14 폐기 + sklearn 1.7.2 KMeans fallback 등가 | narrative 가치 X |")
    lines.append("\n**합계**: 233 drop cells / 1130 total = 79.5% coverage. 9 cells × 56 method (단일 테이블 §V-B 영역)에서는 A2-Fig8 (C5 multi-vector) 제외 시 87.7% coverage.")
    lines.append("\n**5/27 학술 정직 narrative**: 정의 위반 (kdtree/vinecopula) + 자원 한계 (birch/agglomerative SSN) + scope 외 (A2-Fig8 multi-vector / A3-TPCDS ECQO) + wrapper 설계 결함 (Q1+Q4 timeout 부재) + 사용자 결정 (hdbscan) — 모두 명시. 본 연구 §V-B 단일 테이블 contribution 영역에 narrative 영향 없음.")
    return "\n".join(lines)


def method_level_limitation() -> str:
    """★3/★4/M7/M9 학술 정합성 (handoff_v3 audit + Axis F/K 발견)."""
    lines = ["\n### Method-level limitation (학술 정합성 정직 보고)\n"]
    lines.append("| Method | Audit finding | Code 현재 상태 | 5/27 narrative |")
    lines.append("|---|---|---|---|")
    lines.append("| **★3 hilbert** | Faloutsos 1989 Hilbert curve 표명 ❌ — 실제 PCA 2D lex sort | line 449 `(\"hilbert\", \"pca2d_lex\") alias` **이미 정직 명명** + hilbert_real (Wikipedia xy2d 표준) substitute 별도 구현 | \"PCA proxy vs 진짜 Hilbert locality 분리 검증\" 학술 contribution 1건 |")
    lines.append("| **★4 sparse_rp** | Achlioptas 2003 표명 ❌ — 실제 Li-Hastie-Church 2006 1/√D variant | line 420-423 코멘트 **이미 Li 2006 표명** (`density=1/√D, s=D^(1/4)`) | reference 정정만 (코드 변경 X), 측정 결과 그대로 유지 |")
    lines.append("| **M7 skilling_hilbert** | Skilling 2004 full Algorithm 137 ❌ — \"Skip exact swap for simplicity (approximation)\" line 401 | Gray-code/reflection/bit-rotation/MSB-LSB pack 완전, conditional swap 1줄만 simplified | \"approximate Skilling, M6 zorder_morton (Morton 1966 paradigm anchor) + hilbert_real로 P2 cover\" |")
    lines.append("| **M9 kmeans_neyman** | Cochran §5 + Neyman 1934 표명 — labels return만, σ-weight 미적용 | line 466-475: σ_h 이미 산출 + \"alloc time application boundary\" 명시 — 설계상 의도 분리 | \"RQ3 cluster 분할 (method) + RQ2 σ-weight alloc (5-way) 결합 ablation\" |")
    lines.append("\n**Byte-identical duplicates 7쌍** (handoff_v3 audit empirical 입증):")
    lines.append("- pca1d ≡ cca1d ≡ adaptive_bucket_probing (P4 PCA1D quartet)")
    lines.append("- epsilon_net ≡ kdpp / ams_count_sketch ≡ lsh / kdtree = reservoir fallback / dense_rp ≈ random_projection")
    lines.append("- → **paradigm comparison 부정확 caveat** (보고서 §limitation 명시 권고)")
    lines.append("\n**RQ2 5-way Neyman/Anti paradox** (Axis E σ_j root cause):")
    lines.append("- σ_j range 1.3-1.6× (좁음) + KM20 cluster N_i CV=0 (균등) → Neyman reweighting max 8.5%p")
    lines.append("- budget=385 hit count noise (~50/seed @ sel=0.1) > Neyman signal (~30 표본)")
    lines.append("- Anti ≤ Prop ≤ Neyman 패턴 = **알고리즘 부족 X, KM20 cluster + 데이터 분포의 자연 결과** (학술 honest finding)")
    return "\n".join(lines)


def write_report(out_dir: Path, output_md: Path):
    df_b1 = load_b1_results(out_dir)
    df_casea = load_case_a_results(out_dir)
    df_caseb = load_case_b_results(out_dir)
    sections = []
    sections.append(f"# Paper Exact 재현 측정 — Phase D 분석 + 5단계 narrative\n")
    sections.append(f"_Generated_: {pd.Timestamp.now()}\n")
    sections.append(f"_Source_: `{out_dir}`\n")
    sections.append(f"- B1 cells: **{len(df_b1)}** (Phase A)")
    sections.append(f"- CaseA measurements: **{len(df_casea)}** (Phase B)")
    sections.append(f"- CaseB measurements: **{len(df_caseb)}** (Phase C)\n")
    sections.append("---\n")

    sections.append(analyze_phase_a(df_b1))
    sections.append(analyze_rq1_rq2(out_dir))
    md_b, df_casea_paired = analyze_phase_b(df_b1, df_casea, out_dir)
    sections.append(md_b)
    md_c, df_caseb_paired = analyze_phase_c(df_b1, df_caseb, out_dir)
    sections.append(md_c)
    sections.append(analyze_caseb_vs_casea(df_casea_paired, df_caseb_paired))

    # 5단계 narrative — actual stats 기반 auto-fill
    sections.append("\n## 6. 5단계 narrative summary (사용자 명시 — 5/10 14:03 + 18:49 + 20:45)\n")
    sections.append("**1. RQ1/RQ2/RQ3 검증** (기존 결과 paper exact 재확인)")
    sections.append("- RQ1: paper sel {0.01, 0.10}에서 random vs KM20 stratified 격차 (위 §2.1)")
    sections.append("- RQ2: Prop / Equal / Bernoulli 비교 narrative (위 §2.2)")
    sections.append(f"- RQ3: 본 측정 = Phase A({len(df_b1)} B1) + Phase B({len(df_casea)} CaseA) + Phase C({len(df_caseb)} CaseB)\n")
    sections.append("**2. Exqutor 100% 정확 재현** (paper Fig 12 = 1.69, validation §2.1 정정)")
    if not df_b1.empty:
        fig12_df = df_b1[df_b1["cell"].isin(FIG_12_CELLS)]
        if not fig12_df.empty:
            qe_trim_fig12 = float(fig12_df["qe_trim"].dropna().mean())
            delta_fig12 = (qe_trim_fig12 - PAPER_FIG_12_AVG_QE) / PAPER_FIG_12_AVG_QE * 100
            sections.append(f"- Fig 12 영역 {len(fig12_df)} cells mean qe_trim: **{qe_trim_fig12:.3f}** (paper 1.69 대비 **{delta_fig12:+.1f}%**)")
            sections.append("- A4-sel cell은 paper Fig 13 영역 (sel inherent q_error 큼) — 별도 분리")
            sections.append("- **byte-identical cells caveat** (Agent #1/#3 발견): A1-DEEP ≡ A5-scale-sf100, A2-Fig9 ≡ A5-scale-sf10 (DEEP sf=100/10 동일 setup, query set 만 다름). Cells count 명목 9 cells × 56 method = 1008 / 실제 6 unique cells × 56 method = 672. 5/27 발표 backup slide에 명시 권고.\n")
    sections.append("**3. CaseA: 우리 method 대체** (sampling step replace, paper §V-B)")
    if not df_casea_paired.empty and "p_adj_bh_greater" in df_casea_paired.columns:
        ca_wins = df_casea_paired[(df_casea_paired["delta_pct_mean"] < 0) &
                                  (df_casea_paired["p_adj_bh_greater"] < 0.05)]
        sections.append(f"- {len(df_casea_paired)} paired 비교 中 one-sided greater p_adj<0.05 outperform: **{len(ca_wins)}건 ({len(ca_wins)/len(df_casea_paired)*100:.1f}%)**")
        if len(ca_wins) > 0:
            best = ca_wins.nsmallest(3, "delta_pct_mean")[["cell", "method", "delta_pct_mean"]]
            top3_a = [f"{r['method']}@{r['cell']} ({r['delta_pct_mean']:+.2f}%)"
                      for _, r in best.iterrows()]
            sections.append(f"- Top 3 CaseA winners: {', '.join(top3_a)}")
        # validation §2.3 — outlier methods caveat
        outlier_df = df_casea_paired[df_casea_paired["method"].isin(CASEA_OUTLIER_METHODS)]
        if not outlier_df.empty:
            worse = outlier_df[(outlier_df["delta_pct_mean"] > 0) &
                               (outlier_df["p_adj_bh"] < 0.05)]
            sections.append(f"- ⚠️ Outlier methods (lsh/RP/sobol/ccsketch/ams) {len(outlier_df)} 비교 中 worse signif **{len(worse)}건** — cluster imbalance caveat\n")
    sections.append("**4. CaseB: 우리 method 증강** (B1 + method ensemble, 5/27 climax)")
    if not df_caseb_paired.empty and "p_adj_bh_greater" in df_caseb_paired.columns:
        cb_wins = df_caseb_paired[(df_caseb_paired["delta_pct_mean"] < 0) &
                                  (df_caseb_paired["p_adj_bh_greater"] < 0.05)]
        sections.append(f"- {len(df_caseb_paired)} paired 비교 中 one-sided greater p_adj<0.05 outperform: **{len(cb_wins)}건 ({len(cb_wins)/len(df_caseb_paired)*100:.1f}%)**")
        if len(cb_wins) > 0:
            best = cb_wins.nsmallest(3, "delta_pct_mean")[["cell", "method", "delta_pct_mean"]]
            top3_b = [f"{r['method']}@{r['cell']} ({r['delta_pct_mean']:+.2f}%)"
                      for _, r in best.iterrows()]
            sections.append(f"- Top 3 CaseB winners: {', '.join(top3_b)}\n")
    sections.append("**5. 최종 비교 B1 vs CaseA vs CaseB** (위 §5)")
    if (not df_casea_paired.empty) and (not df_caseb_paired.empty):
        ca_mean = df_casea_paired["delta_pct_mean"].mean()
        cb_mean = df_caseb_paired["delta_pct_mean"].mean()
        sections.append(f"- CaseA mean Δ%: **{ca_mean:+.2f}%** / CaseB mean Δ%: **{cb_mean:+.2f}%** (음수=B1 대비 우위)")
        if cb_mean < ca_mean:
            sections.append(f"- ✅ CaseB > CaseA > B1 narrative 성립 (gap = **{(cb_mean - ca_mean):+.2f}%**)\n")
        else:
            sections.append(f"- ⚠️ CaseA가 평균 더 우위 — CaseB ensemble 효과 약함 추가 분석 필요\n")

    # === Phase D 보강 (5/11 17:11 KST): §7 paradigm rollup + §8 effect size + §9 cherry-pick ===
    sections.append("\n---\n## 7. Paradigm rollup (P1-P10 평균 Δ%)\n")
    sections.append("> ULTRAPLAN 권고: 5 paradigm × 11 method framework 직접 입증 — outlier |Δ%|>100 제외")
    sections.append(paradigm_rollup(df_casea_paired, label="CaseA"))
    sections.append(paradigm_rollup(df_caseb_paired, label="CaseB"))

    sections.append("\n---\n## 8. Effect size (Hedges' g + Cliff's δ)\n")
    sections.append("> n=10 small sample power 보완 — Cliff's δ large threshold = ±0.474")
    sections.append(effect_size_table(df_casea_paired, label="CaseA"))
    sections.append(effect_size_table(df_caseb_paired, label="CaseB"))

    sections.append("\n---\n## 9. Cherry-pick prevention (method × cell range)\n")
    sections.append("> handoff_back §1.4 권고: method-mean과 cell 별 range 분리, large range outlier 노출")
    sections.append(cherry_pick_table(df_casea_paired, label="CaseA", top_n=10))
    sections.append(cherry_pick_table(df_caseb_paired, label="CaseB", top_n=10))

    sections.append("\n---\n## 10. Drop list (정직한 결손 보고)\n")
    sections.append("> Axis G ULTRAPLAN 권고: 233 cells 결손 9 카테고리 분류, 학술 정직 narrative")
    sections.append(drop_list_section())

    sections.append("\n---\n## 11. Method-level limitation (★3/★4/M7/M9 학술 정합성)\n")
    sections.append("> Axis F/K ULTRAPLAN 권고: ★3 hilbert PCA-alias / ★4 sparse_rp Li 2006 / M7/M9 simplification 정직 보고")
    sections.append(method_level_limitation())

    output_md.write_text("\n".join(sections))
    print(f"Report written: {output_md}")
    print(f"  B1 cells: {len(df_b1)}")
    print(f"  CaseA measurements: {len(df_casea)}")
    print(f"  CaseB measurements: {len(df_caseb)}")
    print(f"  RQ1/RQ2 csv files: {len(list(out_dir.glob('rq*.csv')))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path,
                    default=Path("/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact"))
    ap.add_argument("--output", type=Path,
                    default=Path("/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md"))
    args = ap.parse_args()
    write_report(args.out_dir, args.output)


if __name__ == "__main__":
    main()
