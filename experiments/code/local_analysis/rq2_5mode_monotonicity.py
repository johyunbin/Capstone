#!/usr/bin/env python3
"""
RQ2 5-mode × selectivity 단조성 통계 검정 (RQ1 의 단조성과 통일 metric).

각 mode (Equal/Proportional/Neyman/Anti-Neyman) 의 BERN 대비 개선폭이 sel 에 따라
어떻게 변하는지 단조성 정량.

Spearman ρ + Mann-Kendall — RQ1 gradient 와 동일 framework.

핵심 가설:
  - **Equal/Proportional**: KM20 stratification 의 Level 2 효과 → sel↓ → 개선↑ (RQ1 KM20 와 동일).
  - **Neyman**: σ_i adjusted, 좁은 sel 에서 더 강한 단조성?
  - **Anti-Neyman**: Anti-direction 의 hurt 가 sel 에 따라 어떻게 변하는지.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as sst

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ2 = ROOT / "Capstone" / "experiments" / "results" / "rq2_aware" / "2026_05_06_alloc"
if not RQ2.exists():
    RQ2 = Path(__file__).resolve().parent.parent.parent / "results" / "rq2_aware" / "2026_05_06_alloc"


def mann_kendall(x):
    n = len(x)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += np.sign(x[j] - x[i])
    var_s = n * (n - 1) * (2 * n + 5) / 18.0
    if s > 0:
        z = (s - 1) / math.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / math.sqrt(var_s)
    else:
        z = 0.0
    p = 2 * (1 - sst.norm.cdf(abs(z)))
    return {"S": int(s), "z": float(z), "p": float(p)}


def main():
    df = pd.read_parquet(RQ2 / "rq2_alloc.parquet").dropna(subset=["q_error"])
    print(f"[load] {len(df):,} rows")

    # 각 (dataset, mode, sel, seed) median q_error → BERN 과 비교 → diff_pct
    bern_medians = df[df["mode"] == "bernoulli"].groupby(
        ["dataset", "selectivity", "seed"]
    )["q_error"].median().reset_index().rename(columns={"q_error": "bern_med"})

    method_modes = ["equal", "proportional", "neyman", "anti_neyman"]
    rows = []
    for mode in method_modes:
        m_med = df[df["mode"] == mode].groupby(
            ["dataset", "selectivity", "seed"]
        )["q_error"].median().reset_index().rename(columns={"q_error": "method_med"})
        merged = m_med.merge(bern_medians, on=["dataset", "selectivity", "seed"])
        merged["diff_pct"] = (merged["method_med"] - merged["bern_med"]) / merged["bern_med"] * 100.0
        merged["mode"] = mode
        rows.append(merged)
    long_df = pd.concat(rows, ignore_index=True)

    # === per-seed Spearman ρ(sel, diff_pct) per (dataset, mode) ===
    print("\n=== Per-seed Spearman ρ(sel, diff_pct) — bootstrap CI ===")
    test_results = {}
    summary_rows = []
    for ds in sorted(long_df["dataset"].unique()):
        for mode in method_modes:
            sub = long_df[(long_df["dataset"] == ds) & (long_df["mode"] == mode)]
            rhos = []
            for seed, group in sub.groupby("seed"):
                if len(group) < 3:
                    continue
                rho, _ = sst.spearmanr(group["selectivity"], group["diff_pct"])
                if not np.isnan(rho):
                    rhos.append(float(rho))
            if not rhos:
                continue
            rng = np.random.default_rng(42)
            boot = []
            for _ in range(5000):
                idx = rng.choice(len(rhos), size=len(rhos), replace=True)
                boot.append(np.mean([rhos[i] for i in idx]))
            ci_low = float(np.percentile(boot, 2.5))
            ci_high = float(np.percentile(boot, 97.5))
            mean_rho = float(np.mean(rhos))

            # pooled mean per sel + Mann-Kendall
            sel_means = sub.groupby("selectivity")["diff_pct"].mean().sort_index()
            mk = mann_kendall(sel_means.values)
            rho_pool, p_pool = sst.spearmanr(sel_means.index.values, sel_means.values)

            test_results[f"{ds}_{mode}"] = {
                "rhos": rhos, "mean_rho": mean_rho,
                "ci_low": ci_low, "ci_high": ci_high,
                "mk_S": mk["S"], "mk_z": mk["z"], "mk_p": mk["p"],
                "pool_rho": float(rho_pool), "pool_p": float(p_pool),
                "sels": sel_means.index.tolist(), "means": sel_means.values.tolist(),
            }
            summary_rows.append({
                "dataset": ds, "mode": mode, "n_seeds": len(rhos),
                "per_seed_mean_rho": mean_rho,
                "ci_low": ci_low, "ci_high": ci_high,
                "ci_excludes_0": (ci_low > 0) or (ci_high < 0),
                "pooled_rho": float(rho_pool), "pooled_p": float(p_pool),
                "mk_S": mk["S"], "mk_z": mk["z"], "mk_p": mk["p"],
            })
            print(f"  {ds:5s} × {mode:14s}: per-seed ρ = {mean_rho:+.3f} "
                  f"CI [{ci_low:+.3f}, {ci_high:+.3f}] | "
                  f"MK z={mk['z']:+.2f} p={mk['p']:.3f} | "
                  f"sel means = {[f'{m:+.2f}' for m in sel_means.values]}")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(RQ2 / "rq2_5mode_monotonicity_summary.csv", index=False)
    with open(RQ2 / "rq2_5mode_monotonicity_test.json", "w") as f:
        json.dump(test_results, f, indent=2, default=str)
    print(f"\n[saved] {RQ2 / 'rq2_5mode_monotonicity_summary.csv'}")
    print(f"[saved] {RQ2 / 'rq2_5mode_monotonicity_test.json'}")

    # narrative md
    md = [
        "# RQ2 5-mode × Selectivity 단조성 검정",
        "",
        "RQ1 단조성 검정 (DEEP-KM20 ρ=-0.680, CI 0 제외) 과 동일 framework 로 RQ2 의 ",
        "5-mode (Equal/Proportional/Neyman/Anti-Neyman) 단조성 정량.",
        "",
        "## per-seed Spearman ρ + 95% bootstrap CI",
        "",
        "| dataset | mode | per-seed mean ρ | 95% CI | pooled ρ (sel mean) | MK p | 결론 |",
        "|---------|------|---------------:|--------|--------------------:|-----:|------|",
    ]
    for r in summary_rows:
        ci_str = f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}]"
        verdict = "**확정**" if r["ci_excludes_0"] else "약함"
        md.append(
            f"| {r['dataset']} | `{r['mode']}` | {r['per_seed_mean_rho']:+.3f} | {ci_str} | "
            f"{r['pooled_rho']:+.3f} | {r['mk_p']:.3f} | {verdict} |"
        )

    md.extend([
        "",
        "## 해석",
        "",
        "**예상 패턴**:",
        "- Equal/Proportional/Neyman: ρ < 0 (sel↓ → diff%↑, KM20 의 Level 2 효과).",
        "- Anti-Neyman: ρ < 0 도 가능하나 reverse-direction 의 hurt 가 sel 에 따라 어떻게 변하는지.",
        "",
        "**ρ CI 가 0 을 제외하는 mode** 가 \"단조성 통계 확정\" 으로 narrative 강화.",
        "RQ1 의 KM20 single-arm 단조성과 RQ2 의 4-mode 단조성을 합쳐 본 연구의 \"Level 2 효과\"",
        "narrative 가 통일.",
        "",
    ])
    with open(RQ2 / "rq2_5mode_monotonicity.md", "w") as f:
        f.write("\n".join(md))
    print(f"[saved] {RQ2 / 'rq2_5mode_monotonicity.md'}")


if __name__ == "__main__":
    main()
