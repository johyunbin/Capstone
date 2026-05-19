#!/usr/bin/env python3
"""
RQ1 SIFT 1.5M 5-sel 통합 단조성 narrative.

배경 (Worker J 핸드오프 §5.2):
- SIFT 측정은 3 sel + mid-sel 보강 + RANDOM20 5-sel 분산 형태 → 통합 narrative 부재.
- 본 driver: 재측정 없이 기존 parquet 만 통합 → per-sel × per-seed median q_error
  + Spearman ρ (sel ↑ vs q_error ↑) + diff_pct (km20 - bernoulli, 가능한 sel만).

데이터 source:
1. rq3_random20_sift.parquet      — 5 sel × 5 seed × 100 q × {bernoulli, random20}  (BERN 5-sel canonical)
2. sift_mid_sel.parquet            — 2 sel (0.1 / 0.3) × 5 seed × {bern, km20, random20}  (km20 보강)
3. phase7_sift_bern.parquet        — s=0.5 only, single SQL measurement (driver SQL D, 100 q)
4. phase7_sift_strat.parquet       — s=0.5 only, single SQL km20 measurement

산출:
    experiments/results/rq1_motivation/rq1_sift_5sel_unified.json
    experiments/results/rq1_motivation/rq1_sift_5sel_unified.md
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path("/Users/hyunbin/Capstone")
RQ1 = ROOT / "experiments/results/rq1_motivation"
RQ3 = ROOT / "experiments/results/rq3_agnostic"

SELS = [0.01, 0.05, 0.10, 0.30, 0.50]
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]


def per_seed_median(df, mode_col="mode", target_modes=("bernoulli",)):
    """sel × mode × seed → median(q_error). sel × mode 평균/std 도 함께."""
    out = []
    df_clean = df.dropna(subset=["q_error"]).copy()
    for sel in sorted(df_clean["selectivity"].unique()):
        for mode in target_modes:
            sub = df_clean[(df_clean["selectivity"].round(4) == round(sel, 4)) &
                           (df_clean[mode_col] == mode)]
            if len(sub) == 0:
                continue
            per_s = sub.groupby("seed")["q_error"].median()
            for seed, med in per_s.items():
                out.append({"selectivity": float(sel), "mode": mode,
                            "seed": float(seed), "median_q_error": float(med)})
    return pd.DataFrame(out)


def main():
    rq3 = pd.read_parquet(RQ3 / "rq3_random20_sift.parquet")
    midsel = pd.read_parquet(RQ1 / "sift_mid_sel.parquet")
    bern_sql = pd.read_parquet(RQ1 / "phase7_sift_bern.parquet")
    strat_sql = pd.read_parquet(RQ1 / "phase7_sift_strat.parquet")

    print(f"=== SIFT 5-sel unified 단조성 분석 ===")
    print(f"rq3_random20: shape={rq3.shape}, sels={sorted(rq3['selectivity'].unique())}")
    print(f"sift_mid_sel: shape={midsel.shape}, sels={sorted(midsel['selectivity'].unique())}")
    print(f"phase7_bern : shape={bern_sql.shape}, sels={sorted(bern_sql['selectivity'].unique())}")
    print(f"phase7_strat: shape={strat_sql.shape}, sels={sorted(strat_sql['selectivity'].unique())}")
    print()

    # === BERN 5-sel canonical (rq3_random20 만 사용 — 5 sel × 5 seed 통일) ===
    bern_5sel = per_seed_median(rq3, target_modes=("bernoulli",))
    bern_summary = (bern_5sel.groupby("selectivity")["median_q_error"]
                    .agg(["mean", "std", "count"]).reset_index())
    bern_summary.columns = ["selectivity", "bern_med_mean", "bern_med_std", "n_seeds"]

    # === KM20 partial (sift_mid_sel s=0.1, s=0.3) ===
    km20_2sel = per_seed_median(midsel, target_modes=("km20",))
    km20_summary = (km20_2sel.groupby("selectivity")["median_q_error"]
                    .agg(["mean", "std", "count"]).reset_index())
    km20_summary.columns = ["selectivity", "km_med_mean", "km_med_std", "n_seeds"]

    # === diff_pct (km20 vs bernoulli, mid-sel 만 가능) ===
    bern_mid = per_seed_median(midsel, target_modes=("bernoulli",))
    diffs = []
    for sel in [0.10, 0.30]:
        b_seed = bern_mid[bern_mid["selectivity"].round(4) == round(sel, 4)].set_index("seed")["median_q_error"]
        k_seed = km20_2sel[km20_2sel["selectivity"].round(4) == round(sel, 4)].set_index("seed")["median_q_error"]
        ds = []
        for s in SEEDS:
            b = float(b_seed.get(s, np.nan))
            k = float(k_seed.get(s, np.nan))
            if not np.isnan(b) and not np.isnan(k) and b > 0:
                ds.append((k - b) / b * 100.0)
        if ds:
            diffs.append({
                "selectivity": sel,
                "n_seeds": len(ds),
                "diff_pct_mean": float(np.mean(ds)),
                "diff_pct_std": float(np.std(ds, ddof=1)) if len(ds) >= 2 else None,
            })

    # === Spearman ρ (sel ↑ ⇒ bern q_error ↑ 단조성) per seed ===
    spearman_per_seed = []
    for s in SEEDS:
        sub = bern_5sel[bern_5sel["seed"] == s].sort_values("selectivity")
        if len(sub) < 3:
            continue
        rho, p = spearmanr(sub["selectivity"], sub["median_q_error"])
        spearman_per_seed.append({
            "seed": float(s),
            "rho": float(rho),
            "p_value": float(p),
            "n": int(len(sub)),
        })
    rho_arr = [r["rho"] for r in spearman_per_seed]
    rho_summary = {
        "mean_rho": float(np.mean(rho_arr)) if rho_arr else None,
        "std_rho": float(np.std(rho_arr, ddof=1)) if len(rho_arr) >= 2 else None,
        "min_rho": float(np.min(rho_arr)) if rho_arr else None,
        "max_rho": float(np.max(rho_arr)) if rho_arr else None,
    }

    summary = {
        "dataset": "SIFT_1.5M",
        "method": "numpy/SQL D_target unified (no re-measurement)",
        "data_sources": {
            "bern_5sel_canonical": "rq3_random20_sift.parquet (5 sel × 5 seed × 100 q)",
            "km20_partial": "sift_mid_sel.parquet (s=0.1, s=0.3 only, 5 seed)",
            "phase7_sql_legacy": "phase7_sift_{bern,strat}.parquet (s=0.5 SQL, single)",
        },
        "bern_5sel_per_seed": bern_5sel.to_dict("records"),
        "bern_5sel_summary": bern_summary.to_dict("records"),
        "km20_2sel_per_seed": km20_2sel.to_dict("records"),
        "km20_2sel_summary": km20_summary.to_dict("records"),
        "km20_vs_bern_diff_pct": diffs,
        "spearman_bern_per_seed": spearman_per_seed,
        "spearman_summary": rho_summary,
        "phase7_sql_s050": {
            "bern_median_q_error": float(bern_sql.dropna(subset=["q_error"])["q_error"].median()),
            "km20_median_q_error": float(strat_sql.dropna(subset=["q_error"])["q_error"].median()),
            "diff_pct": float((strat_sql["q_error"].median() - bern_sql["q_error"].median())
                              / bern_sql["q_error"].median() * 100.0),
            "n_queries": int(len(bern_sql)),
            "note": "single SQL measurement, no seed dimension",
        },
        "limitations": [
            "KM20 5-sel canonical 측정 부재 (s=0.01, s=0.05 km20 미측정).",
            "phase7_sift s=0.5 는 SQL D_target single measurement → numpy methodology 와 직접 비교 X.",
            "통합은 driver 단계에서만 정합 (numpy/SQL D 차이 잔존).",
        ],
    }

    out_json = RQ1 / "rq1_sift_5sel_unified.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"saved {out_json}")

    # === Markdown narrative ===
    lines = []
    lines.append("# RQ1 — SIFT 1.5M 5-sel 통합 단조성 (Worker J, 2026-05-07)")
    lines.append("")
    lines.append("## 데이터 source")
    lines.append("")
    for k, v in summary["data_sources"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")
    lines.append("## BERN 5-sel canonical (rq3_random20_sift, 5 seed × 100 q)")
    lines.append("")
    lines.append("| sel | median q_error (mean ± std, 5 seed) |")
    lines.append("|---|---|")
    for r in summary["bern_5sel_summary"]:
        m = r["bern_med_mean"]
        s = r["bern_med_std"]
        lines.append(f"| {r['selectivity']:.2f} | {m:.4f} ± {s:.4f} |")
    lines.append("")
    lines.append(f"**per-seed Spearman ρ (sel ↑ vs bern q_error ↑)**: "
                 f"{rho_summary['mean_rho']:+.3f} ± {rho_summary['std_rho']:.3f} "
                 f"(min {rho_summary['min_rho']:+.3f}, max {rho_summary['max_rho']:+.3f}, n=5 seeds)")
    lines.append("")
    lines.append("→ ρ 부호로 단조성 방향성 판단 (양수: sel ↑ ⇒ q_error ↑, 음수: 반전).")
    lines.append("")
    lines.append("## KM20 partial (sift_mid_sel, 2 sel × 5 seed × 100 q)")
    lines.append("")
    lines.append("| sel | median q_error (km20, mean ± std) | km20 vs bern Δ% |")
    lines.append("|---|---|---|")
    diffs_by_sel = {d["selectivity"]: d for d in diffs}
    for r in summary["km20_2sel_summary"]:
        sel = r["selectivity"]
        m = r["km_med_mean"]
        s = r["km_med_std"]
        d = diffs_by_sel.get(sel, {})
        dm = d.get("diff_pct_mean")
        ds = d.get("diff_pct_std")
        ds_txt = f"±{ds:.2f}" if ds is not None else ""
        lines.append(f"| {sel:.2f} | {m:.4f} ± {s:.4f} | {dm:+.2f}% {ds_txt} |"
                     if dm is not None else f"| {sel:.2f} | {m:.4f} ± {s:.4f} | — |")
    lines.append("")
    lines.append("## Phase 7 SQL legacy (s=0.5, single measurement)")
    lines.append("")
    p7 = summary["phase7_sql_s050"]
    lines.append(f"- bern median q_error: {p7['bern_median_q_error']:.4f}")
    lines.append(f"- km20 median q_error: {p7['km20_median_q_error']:.4f}")
    lines.append(f"- Δ%: {p7['diff_pct']:+.2f}% (n={p7['n_queries']} q, single seed)")
    lines.append("")
    lines.append("## Limitations")
    lines.append("")
    for l in summary["limitations"]:
        lines.append(f"- {l}")
    lines.append("")
    lines.append("## Cross-scale 의의 (DEEP 1M ↔ 8M ↔ SIFT 1.5M)")
    lines.append("")
    lines.append("- DEEP 1M (5 sel canonical): gradient 19.6%p (s=0.01) — Phase 6/7 비교에서 확인.")
    lines.append("- DEEP 8M (별도 산출 `rq1_8m_monotonicity.md` 참조): Phase 7 numpy methodology 통일.")
    lines.append("- SIFT 1.5M: BERN ρ 부호 + km20 mid-sel(0.1/0.3) Δ% 로 단조성 일관성 boundary 평가.")
    lines.append("")

    out_md = RQ1 / "rq1_sift_5sel_unified.md"
    with open(out_md, "w") as f:
        f.write("\n".join(lines))
    print(f"saved {out_md}")

    print()
    print(f"=== SIFT BERN 5-sel ρ summary ===")
    for r in spearman_per_seed:
        print(f"  seed={r['seed']:.1f}: ρ={r['rho']:+.3f} (p={r['p_value']:.3f})")
    print(f"  mean ρ = {rho_summary['mean_rho']:+.3f} ± {rho_summary['std_rho']:.3f}")


if __name__ == "__main__":
    main()
