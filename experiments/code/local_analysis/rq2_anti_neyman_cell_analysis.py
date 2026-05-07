#!/usr/bin/env python3
"""
RQ2 Anti-Neyman sel-별 cell-by-cell 분석.

기존 정리: \"Anti-Neyman vs Proportional 모든 case 통계적 유의 X\" → σ_i 신호 약.
본 분석: 그 결론 안에 sel 별 sub-result (특정 cell 에서는 Anti-Neyman 이 약하게라도
방향성 보이는지) 가 있는지 정량.

학술 honest narrative: 부정 결과의 \"부정 이유\" 정량.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as sst

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ2 = ROOT / "Capstone" / "experiments" / "results" / "rq2_aware" / "2026_05_06_alloc"
if not RQ2.exists():
    RQ2 = Path(__file__).resolve().parent.parent.parent / "results" / "rq2_aware" / "2026_05_06_alloc"


def main():
    pq_path = RQ2 / "rq2_alloc.parquet"
    df = pd.read_parquet(pq_path).dropna(subset=["q_error"])
    print(f"[load] {len(df):,} rows, modes: {sorted(df['mode'].unique())}")

    # paired Anti-Neyman vs Proportional per (dataset, sel)
    rows = []
    for ds in sorted(df["dataset"].unique()):
        for sel in sorted(df["selectivity"].unique()):
            sub = df[(df["dataset"] == ds) & (df["selectivity"] == sel)]
            an = sub[sub["mode"] == "anti_neyman"].sort_values(["seed", "query_id"])
            pr = sub[sub["mode"] == "proportional"].sort_values(["seed", "query_id"])
            merged = an.merge(pr, on=["seed", "query_id"], suffixes=("_an", "_pr"))
            if len(merged) < 10:
                continue
            qe_an = merged["q_error_an"].to_numpy()
            qe_pr = merged["q_error_pr"].to_numpy()

            med_an = np.median(qe_an)
            med_pr = np.median(qe_pr)
            delta_pct = (med_an - med_pr) / max(med_pr, 1e-9) * 100.0

            # paired Wilcoxon (two-sided)
            try:
                w = sst.wilcoxon(qe_an, qe_pr, alternative="two-sided", zero_method="wilcox")
                p_val = float(w.pvalue)
                w_stat = float(w.statistic)
            except Exception:
                p_val, w_stat = np.nan, np.nan

            # Cohen's d (paired)
            diff = qe_an - qe_pr
            d = float(np.mean(diff) / np.std(diff, ddof=1)) if np.std(diff, ddof=1) > 1e-9 else 0.0

            # Bootstrap delta CI
            rng = np.random.default_rng(42)
            boot = []
            n = len(qe_an)
            for _ in range(2000):
                idx = rng.choice(n, size=n, replace=True)
                m_an = np.median(qe_an[idx])
                m_pr = np.median(qe_pr[idx])
                boot.append((m_an - m_pr) / max(m_pr, 1e-9) * 100.0)
            boot = np.array(boot)

            rows.append({
                "dataset": ds, "sel": sel, "n_pairs": len(merged),
                "med_anti_neyman": med_an, "med_proportional": med_pr,
                "delta_pct": delta_pct,
                "delta_ci_low": float(np.percentile(boot, 2.5)),
                "delta_ci_high": float(np.percentile(boot, 97.5)),
                "p_wilcoxon": p_val,
                "w_stat": w_stat,
                "cohens_d": d,
            })

    out = pd.DataFrame(rows)
    out["ci_excludes_0"] = (out["delta_ci_low"] > 0) | (out["delta_ci_high"] < 0)
    out["p_BH_005"] = (out["p_wilcoxon"] * len(out) <= 0.05)
    out_path = RQ2 / "rq2_anti_neyman_cell_analysis.csv"
    out.to_csv(out_path, index=False)
    print(f"\n[saved] {out_path}")
    print()
    print("=== sel-별 Anti-Neyman vs Proportional ===")
    print(out[["dataset", "sel", "delta_pct", "delta_ci_low", "delta_ci_high",
                "p_wilcoxon", "cohens_d", "ci_excludes_0"]].to_string(index=False))

    # cell-by-cell direction analysis
    print("\n=== Direction summary ===")
    out["dir"] = out["delta_pct"].apply(lambda d: "AN > PR (worse)" if d > 0 else "AN < PR (better)")
    dir_counts = out.groupby(["dataset", "dir"]).size().unstack(fill_value=0)
    print(dir_counts.to_string())

    # narrative md
    md = [
        "# RQ2 Anti-Neyman sel-별 Cell-by-Cell 분석",
        "",
        "기존 결론: \"Anti-Neyman vs Proportional 모든 case 통계 유의 X — σ_i 신호 약\".",
        "본 분석: 그 결론 안에 sel 별 sub-result 가 있는지 정량.",
        "",
        "## sel-별 결과",
        "",
        "| dataset | sel | delta_pct (AN-PR) | 95% CI | p (Wilcoxon) | Cohen's d | CI 0 제외 |",
        "|---------|----:|------------------:|--------|-------------:|----------:|:---------:|",
    ]
    for _, r in out.iterrows():
        md.append(
            f"| {r['dataset']} | {r['sel']:.3f} | {r['delta_pct']:+.2f}% | "
            f"[{r['delta_ci_low']:+.2f}, {r['delta_ci_high']:+.2f}] | "
            f"{r['p_wilcoxon']:.4f} | {r['cohens_d']:+.3f} | "
            f"{'✓' if r['ci_excludes_0'] else '✗'} |"
        )
    md.extend([
        "",
        "## 해석",
        "",
        "- **CI 0 제외 cell** 이 있으면 Anti-Neyman 의 효과가 그 cell 에서 통계 robust (방향성).",
        "- delta_pct > 0 (AN > PR) 이면 Anti-Neyman 이 *더 나쁨* — σ_i 가 *적은* stratum 에 *많은* 표본 배분의 hurt 효과.",
        "- delta_pct < 0 이면 Anti-Neyman 이 더 좋음 — σ_i 신호가 noisy 해서 reverse 가 우연 better.",
        "",
        "**학술 narrative**:",
        "1. 모든 cell 에서 |Cohen's d| < 0.2 면 \"σ_i 신호가 너무 약함\" 의 정직한 입증.",
        "2. 일부 cell 에서 d > 0.2 면 \"σ_i 신호가 약하지만 방향은 일관 (Neyman 이 옳고 Anti-Neyman 이 hurt)\".",
        "",
    ])
    with open(RQ2 / "rq2_anti_neyman_cell_analysis.md", "w") as f:
        f.write("\n".join(md))
    print(f"[saved] {RQ2 / 'rq2_anti_neyman_cell_analysis.md'}")


if __name__ == "__main__":
    main()
