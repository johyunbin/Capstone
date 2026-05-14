#!/usr/bin/env python3
"""
RQ3 학술 표준 sampling metric — ESS / DEFF / ICC.

기존 q_error / Cohen's d / paired Wilcoxon 외 **survey sampling 분야 표준 metric** 추가.

1. **DEFF (Design Effect, Kish 1965)**:
   DEFF = Var(estimator under design) / Var(SRS estimator)
   DEFF < 1 → stratification 이 SRS 보다 우수 (variance 감소)
   DEFF > 1 → stratification 이 SRS 보다 나쁨

2. **ESS (Effective Sample Size)**:
   ESS = n / DEFF
   "stratified sample n 이 SRS 의 어느 정도 sample 과 동등한가"

3. **ICC (Intraclass Correlation Coefficient)**:
   cluster homogeneity 정량.
   ICC = (cluster mean variance) / (total variance) = MS_between / (MS_between + MS_within)
   ICC ↑ → cluster 가 매우 다름 (within 동질)
   ICC ↓ → cluster 가 비슷 (within 이질)

기존 측정 데이터 (rq3_*.parquet) 의 q_error 분포 위에서 계산.

산출:
  - rq3_sampling_metrics.csv (method × dataset × sel × {DEFF, ESS, ICC})
  - rq3_sampling_metrics.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESULTS = ROOT / "Capstone" / "experiments" / "results" / "rq3_agnostic"
if not RESULTS.exists():
    RESULTS = Path(__file__).resolve().parent.parent.parent / "results" / "rq3_agnostic"


PARQUET_FILES = [
    "rq3_random20.parquet", "rq3_random20_sift.parquet", "rq3_km20.parquet",
    "rq3_minibatch.parquet", "rq3_random_proj.parquet",
    "rq3_hilbert.parquet", "rq3_lsh.parquet",
    "rq3_kde_pilot.parquet", "rq3_distance_shell.parquet",
    "rq3_importance_sampling.parquet",
]


def compute_deff_ess(qe_method: np.ndarray, qe_bern: np.ndarray, n: int = 385) -> dict:
    """method 의 DEFF + ESS 계산.

    qe_method, qe_bern: 같은 (sel, query, seed) 의 q_error 분포.
    DEFF = Var(qe_method) / Var(qe_bern)
    ESS = n / DEFF (n = 표본 크기, 본 연구 385)
    """
    var_method = np.var(qe_method, ddof=1)
    var_bern = np.var(qe_bern, ddof=1)
    if var_bern < 1e-9:
        return {"deff": float("nan"), "ess": float("nan"),
                "var_method": float(var_method), "var_bern": float(var_bern)}
    deff = var_method / var_bern
    ess = n / deff
    return {"deff": float(deff), "ess": float(ess),
            "var_method": float(var_method), "var_bern": float(var_bern)}


def compute_icc(df_sub: pd.DataFrame) -> dict:
    """ICC — q_error 의 query-level 동질성 정량.

    cluster = query_id (각 query 가 한 cluster, 5 seed 가 그 cluster 내 observation).
    ICC = sigma_between^2 / (sigma_between^2 + sigma_within^2)
    Higher ICC → query 별 q_error 가 query-specific (seed 간 작음).
    Lower ICC → query 별 q_error 가 random (seed dependent).
    """
    if "query_id" not in df_sub.columns or "q_error" not in df_sub.columns:
        return {"icc": float("nan")}

    qe = df_sub["q_error"].dropna()
    if len(qe) < 10:
        return {"icc": float("nan")}

    # one-way random ANOVA: query_id 가 random factor
    grouped = df_sub.dropna(subset=["q_error"]).groupby("query_id")["q_error"]
    if grouped.ngroups < 2:
        return {"icc": float("nan")}

    n_per_group = grouped.size()
    if n_per_group.min() < 2:
        return {"icc": float("nan")}

    grand_mean = qe.mean()
    group_means = grouped.mean()
    n_groups = len(group_means)
    n_avg = n_per_group.mean()

    # SS_between, SS_within
    ss_between = sum(n_per_group[g] * (group_means[g] - grand_mean) ** 2 for g in group_means.index)
    ss_within = sum(((grouped.get_group(g) - group_means[g]) ** 2).sum() for g in group_means.index)

    df_between = n_groups - 1
    df_within = len(qe) - n_groups
    if df_between <= 0 or df_within <= 0:
        return {"icc": float("nan")}

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within

    sigma_within_sq = ms_within
    sigma_between_sq = max((ms_between - ms_within) / n_avg, 0)
    if sigma_between_sq + sigma_within_sq < 1e-9:
        return {"icc": float("nan")}
    icc = sigma_between_sq / (sigma_between_sq + sigma_within_sq)
    return {"icc": float(icc),
            "ms_between": float(ms_between),
            "ms_within": float(ms_within)}


def main():
    print("=" * 70)
    print("RQ3 학술 표준 sampling metric — ESS / DEFF / ICC")
    print("=" * 70)

    frames = []
    for fname in PARQUET_FILES:
        p = RESULTS / fname
        if p.exists():
            df = pd.read_parquet(p)
            df["source"] = fname.replace(".parquet", "")
            frames.append(df)
    df_all = pd.concat(frames, ignore_index=True).dropna(subset=["q_error"])
    print(f"[load] {len(df_all):,} rows")

    bern_df = df_all[df_all["mode"] == "bernoulli"]

    rows = []
    methods = ["minibatch", "random_proj", "hilbert", "lsh", "kde_pilot",
               "distance_shell", "is_p50_clip", "is_p200_clip", "km20", "random20"]

    for method in methods:
        m_df = df_all[df_all["mode"] == method]
        if m_df.empty:
            continue
        for ds in ["DEEP", "SIFT"]:
            for sel in sorted(m_df[m_df["dataset"] == ds]["selectivity"].unique()):
                m_sub = m_df[(m_df["dataset"] == ds) & (m_df["selectivity"] == sel)]
                b_sub = bern_df[(bern_df["dataset"] == ds) & (bern_df["selectivity"] == sel)]
                if len(m_sub) < 10 or len(b_sub) < 10:
                    continue

                # paired alignment
                merged = m_sub.merge(b_sub, on=["seed", "query_id"], suffixes=("_m", "_b"))
                if len(merged) < 10:
                    continue

                deff_ess = compute_deff_ess(merged["q_error_m"].to_numpy(),
                                             merged["q_error_b"].to_numpy(), n=385)
                icc = compute_icc(m_sub.rename(columns={"q_error": "q_error"}))

                rows.append({
                    "method": method, "dataset": ds, "sel": sel,
                    "n_pairs": len(merged),
                    "deff": deff_ess["deff"],
                    "ess": deff_ess["ess"],
                    "var_method": deff_ess["var_method"],
                    "var_bern": deff_ess["var_bern"],
                    "icc": icc.get("icc"),
                })

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "rq3_sampling_metrics.csv", index=False)
    print(f"\n[saved] {RESULTS / 'rq3_sampling_metrics.csv'}")

    # Summary by method
    print("\n=== Method 별 평균 DEFF / ESS / ICC ===")
    summary = out.groupby("method").agg(
        deff_mean=("deff", "mean"),
        ess_mean=("ess", "mean"),
        icc_mean=("icc", "mean"),
        n_cells=("n_pairs", "count"),
    ).round(3)
    summary["deff_class"] = summary["deff_mean"].apply(
        lambda d: ("매우 우수 (DEFF < 0.5)" if d < 0.5 else
                   "우수 (0.5 ~ 0.8)" if d < 0.8 else
                   "약 우수 (0.8 ~ 1.0)" if d < 1.0 else
                   "동등 (~1.0)" if d < 1.1 else
                   "약간 나쁨 (1.0 ~ 1.5)" if d < 1.5 else "나쁨 (>1.5)")
    )
    print(summary.to_string())

    # narrative
    md = [
        "# RQ3 학술 표준 Sampling Metric — ESS / DEFF / ICC",
        "",
        "기존 q_error / Cohen's d / paired Wilcoxon 외 **survey sampling 분야 표준 metric** 추가.",
        "5/27 발표 / 6/11 보고서 의 학술 robust 강화.",
        "",
        "## 정의",
        "",
        "- **DEFF** (Design Effect, Kish 1965): `Var(stratified) / Var(SRS)`. < 1 → 우수.",
        "- **ESS** (Effective Sample Size): `n / DEFF`. 본 연구 budget n=385 기준.",
        "- **ICC** (Intraclass Correlation): query-level 동질성. ↑ → query-specific signal 강.",
        "",
        "## Method 별 평균 DEFF / ESS / ICC (10 dataset × sel cells 평균)",
        "",
        "```",
        summary.to_string(),
        "```",
        "",
        "## 해석",
        "",
        "**DEFF 가 1.0 미만**인 method 만 통계학 표준 의미의 \"우수\":",
        "- KM20 oracle / Hilbert / MiniBatch / KDE-pilot 의 DEFF 가 1.0 미만이면 stratification 효과 정량 입증",
        "- IS / Distance-Shell 의 DEFF > 1.0 은 negative control 의 정량 evidence",
        "",
        "**ESS** = 385 / DEFF — \"stratified 385 표본의 효과 = SRS 의 ESS 표본\":",
        "- DEFF = 0.5 → ESS = 770 (SRS 의 770 표본과 동등)",
        "- DEFF = 1.0 → ESS = 385 (동등)",
        "",
        "**ICC** — query 의 difficulty signal 정량:",
        "- ICC ↑ → query 별 q_error 가 inherent (seed 노이즈와 분리). method routing 의 정당성 ↑.",
        "- 본 연구의 spread vs difficulty ρ=0.78 와 같은 방향의 정량.",
        "",
        "## 5/27 발표용 narrative",
        "",
        "본 metric 은 q_error mean 외 **variance 측면의 정량** 이므로 학술 발표의 robust 강화.",
        "Cohen's d (effect size) + DEFF (variance reduction) + ICC (query signal) 3 metric 의",
        "통합 framework 가 본 연구의 sampling 분야 standard contribution.",
        "",
    ]
    with open(RESULTS / "rq3_sampling_metrics.md", "w") as f:
        f.write("\n".join(md))
    print(f"[saved] {RESULTS / 'rq3_sampling_metrics.md'}")


if __name__ == "__main__":
    main()
