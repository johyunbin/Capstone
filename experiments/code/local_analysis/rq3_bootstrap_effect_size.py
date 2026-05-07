#!/usr/bin/env python3
"""
RQ3 측정 결과의 robust 통계 — Bootstrap 95% CI + Cohen's d effect size.

기존 wilcoxon_vs_*.csv 는 paired Wilcoxon p-value + delta_pct (median) 만 보고.
본 분석은:
  1. **Bootstrap 95% CI** for delta_pct — 평균 차이의 robust uncertainty
  2. **Cohen's d** — practical effect size (paired t-test 의 effect size)
     - 0.2: small / 0.5: medium / 0.8: large

p-value 가 sample size 에 의존 (n=500 paired observations 면 작은 차이도 유의)
하므로 effect size 가 같이 보고되면 학술적 robust.

산출:
  - rq3_bootstrap_effect_size.csv  (method × dataset × sel × stats)
  - rq3_bootstrap_effect_size.md   (narrative)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESULTS = ROOT / "Capstone" / "experiments" / "results" / "rq3_agnostic"
if not RESULTS.exists():
    RESULTS = Path(__file__).resolve().parent.parent.parent / "results" / "rq3_agnostic"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from recovery_rate import paired_wilcoxon_with_bh_fdr  # noqa: E402

# 분석 driver 의 file 목록 동일하게 로딩
PARQUET_FILES = [
    "rq3_random20.parquet", "rq3_random20_sift.parquet", "rq3_km20.parquet",
    "rq3_minibatch.parquet", "rq3_minibatch_partial.parquet",
    "rq3_random_proj.parquet", "rq3_pca1d.parquet",
    "rq3_hilbert.parquet", "rq3_zorder.parquet", "rq3_hybrid.parquet",
    "rq3_kdtree.parquet", "rq3_pq.parquet",
    "rq3_lsh.parquet", "rq3_kde_pilot.parquet", "rq3_distance_shell.parquet",
    "rq3_importance_sampling.parquet",
    # 5/7 새벽 final_chain + phase2 추가 method
    "rq3_spectral.parquet", "rq3_birch.parquet",
    "rq3_gmm.parquet", "rq3_hdbscan.parquet",
    "rq3_sobol.parquet", "rq3_sparse_rp.parquet",
]

METHODS = ["minibatch", "minibatch_partial", "random_proj", "pca1d",
           "hilbert", "zorder", "hybrid", "kdtree", "pq",
           "lsh", "kde_pilot", "distance_shell",
           "is_p50_noclip", "is_p50_clip", "is_p200_noclip", "is_p200_clip",
           # 5/7 새벽 추가
           "spectral", "birch", "gmm", "hdbscan", "sobol", "sparse_rp"]


def load_all() -> pd.DataFrame:
    frames = []
    for fname in PARQUET_FILES:
        path = RESULTS / fname
        if path.exists():
            df = pd.read_parquet(path)
            df["source"] = fname.replace(".parquet", "")
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def deduplicate_bernoulli(df: pd.DataFrame) -> pd.DataFrame:
    bern = df[df["mode"] == "bernoulli"]
    keep_bern = bern[
        ((bern["dataset"] == "DEEP") & (bern["source"] == "rq3_random20"))
        | ((bern["dataset"] == "SIFT") & (bern["source"] == "rq3_random20_sift"))
    ].copy()
    non_bern = df[df["mode"] != "bernoulli"]
    return pd.concat([keep_bern, non_bern], ignore_index=True)


def bootstrap_delta_ci(
    qe_treat: np.ndarray, qe_ctrl: np.ndarray, n_boot: int = 2000,
    seed: int = 42, alpha: float = 0.05,
) -> dict:
    """paired (qe_treat, qe_ctrl) bootstrap → delta_pct CI.

    delta_pct = (median(treat) - median(ctrl)) / median(ctrl) × 100.
    """
    n = len(qe_treat)
    rng = np.random.default_rng(seed)
    deltas = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        t = qe_treat[idx]
        c = qe_ctrl[idx]
        med_t = np.median(t)
        med_c = np.median(c)
        deltas[i] = (med_t - med_c) / max(med_c, 1e-9) * 100.0
    return {
        "delta_mean": float(np.mean(deltas)),
        "delta_ci_low": float(np.percentile(deltas, 100 * alpha / 2)),
        "delta_ci_high": float(np.percentile(deltas, 100 * (1 - alpha / 2))),
        "delta_se": float(np.std(deltas)),
    }


def cohen_d_paired(qe_treat: np.ndarray, qe_ctrl: np.ndarray) -> float:
    """paired Cohen's d = mean(diff) / std(diff)."""
    diff = qe_treat - qe_ctrl
    if np.std(diff, ddof=1) < 1e-9:
        return 0.0
    return float(np.mean(diff) / np.std(diff, ddof=1))


def analyze(df: pd.DataFrame, datasets: list[str], sels: list[float]) -> pd.DataFrame:
    df = df.dropna(subset=["q_error"]).copy()
    rows = []

    for ds in datasets:
        for sel in sels:
            sub = df[(df["dataset"] == ds) & (df["selectivity"] == sel)]
            bern_sub = sub[sub["mode"] == "bernoulli"]

            for method in METHODS:
                m_sub = sub[sub["mode"] == method]
                if len(m_sub) == 0 or len(bern_sub) == 0:
                    continue
                # paired alignment by (seed, query_id)
                merged = m_sub.merge(
                    bern_sub, on=["seed", "query_id"], suffixes=("_t", "_c"),
                )
                if len(merged) < 10:
                    continue
                qt = merged["q_error_t"].to_numpy()
                qc = merged["q_error_c"].to_numpy()

                boot = bootstrap_delta_ci(qt, qc, n_boot=2000, seed=42)
                d = cohen_d_paired(qt, qc)

                magnitude = (
                    "negligible" if abs(d) < 0.2 else
                    "small" if abs(d) < 0.5 else
                    "medium" if abs(d) < 0.8 else
                    "large"
                )
                direction = "improve" if d < 0 else ("hurt" if d > 0 else "neutral")

                rows.append({
                    "dataset": ds, "sel": sel, "method": method,
                    "n_pairs": len(merged),
                    "delta_pct_mean": boot["delta_mean"],
                    "delta_pct_ci_low": boot["delta_ci_low"],
                    "delta_pct_ci_high": boot["delta_ci_high"],
                    "delta_pct_se": boot["delta_se"],
                    "ci_excludes_zero": (boot["delta_ci_low"] > 0) or (boot["delta_ci_high"] < 0),
                    "cohens_d": d,
                    "d_magnitude": magnitude,
                    "direction": direction,
                })

    return pd.DataFrame(rows)


def main():
    print("=" * 70)
    print("RQ3 Bootstrap CI + Cohen's d 분석")
    print("=" * 70)

    df = deduplicate_bernoulli(load_all())
    if df.empty:
        print("[ERROR] no data — parquet 파일 없음")
        return
    print(f"[load] {len(df):,} rows, methods: {sorted(df['mode'].unique())[:10]}")

    datasets = ["DEEP", "SIFT"]
    sels = sorted(df["selectivity"].unique())

    out_df = analyze(df, datasets, sels)
    out_df.to_csv(RESULTS / "rq3_bootstrap_effect_size.csv", index=False)
    print(f"\n[saved] {RESULTS / 'rq3_bootstrap_effect_size.csv'}")

    # === 요약 ===
    print("\n=== Method 별 평균 effect size (Cohen's d) ===")
    avg_d = out_df.groupby("method")["cohens_d"].agg(["mean", "min", "max"]).round(3)
    avg_d["practical"] = avg_d["mean"].apply(
        lambda d: "improve-large" if d < -0.8 else
                  "improve-medium" if d < -0.5 else
                  "improve-small" if d < -0.2 else
                  "negligible" if abs(d) < 0.2 else
                  "hurt-small" if d < 0.5 else
                  "hurt-medium" if d < 0.8 else "hurt-large"
    )
    print(avg_d.to_string())

    # CI excludes 0 비율
    print("\n=== CI excludes 0 비율 (method 별, 통계적 robust 정량) ===")
    ci_robust = out_df.groupby("method").apply(
        lambda g: pd.Series({
            "n_cells": len(g),
            "n_ci_excludes_0": int(g["ci_excludes_zero"].sum()),
            "fraction_robust": float(g["ci_excludes_zero"].mean()),
        }), include_groups=False,
    ).round(3)
    print(ci_robust.to_string())

    # === narrative md ===
    md = [
        "# RQ3 Bootstrap CI + Cohen's d Effect Size",
        "",
        "기존 wilcoxon_vs_*.csv 는 paired Wilcoxon p-value 기반. n=500 paired observations 에서",
        "는 작은 차이도 유의 (p<0.05) 라 *practical significance* 가 같이 보고되어야 학술적 robust.",
        "",
        "## 1. Method 별 평균 Cohen's d",
        "",
        "Cohen's d 의 표준 해석: |d|<0.2 negligible / 0.5 small / 0.8 medium / >0.8 large.",
        "음수 → method 가 BERN 보다 q_error 작음 (개선).",
        "",
        "| method | mean d | min | max | 실용 의미 |",
        "|--------|-------:|----:|----:|----------|",
    ]
    for method in avg_d.index:
        r = avg_d.loc[method]
        md.append(f"| `{method}` | {r['mean']:+.3f} | {r['min']:+.3f} | {r['max']:+.3f} | {r['practical']} |")

    md.extend([
        "",
        "## 2. Bootstrap CI 의 robust 비율",
        "",
        "각 (method × dataset × sel) cell 의 95% bootstrap CI 가 0 을 제외하는 비율.",
        "1.0 → 모든 cell 에서 통계적으로 robust 한 effect.",
        "",
        "| method | n_cells | CI 0 제외 cells | fraction |",
        "|--------|--------:|----------------:|---------:|",
    ])
    for method in ci_robust.index:
        r = ci_robust.loc[method]
        md.append(f"| `{method}` | {int(r['n_cells'])} | "
                  f"{int(r['n_ci_excludes_0'])} | {r['fraction_robust']:.2f} |")

    md.extend([
        "",
        "## 3. RQ3 narrative 결론",
        "",
        "- **Hilbert + MiniBatch 의 mean d 가 negative + |d|≥0.2** 면 small effect 이상 → ",
        "  practical 개선 확정. p<0.05 만 보면 sample size 효과로 small d 도 유의해 보임.",
        "- **lsh / random_proj / pq 의 d 부호** 가 양수로 나오면 → 1M/SIFT 1.5M 에서 BERN 대비",
        "  개선 X. *negative control* 검증.",
        "- **CI 의 fraction_robust 가 1.0 인 method** 만 \"모든 cell 에서 통계 robust 효과 있음\".",
        "  본 연구의 contribution claim 은 이 method 에 한정됨이 보수적 narrative.",
        "",
    ])

    with open(RESULTS / "rq3_bootstrap_effect_size.md", "w") as f:
        f.write("\n".join(md))
    print(f"[saved] {RESULTS / 'rq3_bootstrap_effect_size.md'}")


if __name__ == "__main__":
    main()
