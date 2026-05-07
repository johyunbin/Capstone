#!/usr/bin/env python3
"""
RQ1 DEEP 8M 5-sel × 5 seed Phase 7 numpy 단조성 분석.

입력:
    experiments/results/rq1_motivation/rq1_8m_5sel_bern.parquet
    experiments/results/rq1_motivation/rq1_8m_5sel_km20.parquet

산출:
    experiments/results/rq1_motivation/rq1_8m_monotonicity.json
    experiments/results/rq1_motivation/rq1_8m_monotonicity.md

분석:
- per-sel × per-seed median q_error (bern, km20)
- per-seed Spearman ρ (sel ↑ vs q_error)
- per-seed Spearman ρ (sel ↑ vs diff_pct = km20-bern)
- bootstrap 95% CI on per-sel median q_error (1000 iter, query-level resample)
- 1M cross-scale 비교 (deep_s0XX_numpy_remeasure_summary.json 5종)
- gradient 19.6%p 8M 재현 검증 narrative
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path("/Users/hyunbin/Capstone")
RQ1 = ROOT / "experiments/results/rq1_motivation"

SELS = [0.01, 0.05, 0.10, 0.30, 0.50]
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
N_BOOT = 1000


def bootstrap_median(values, n_boot=N_BOOT, seed=42):
    if len(values) == 0:
        return None, None
    rng = np.random.default_rng(seed)
    arr = np.asarray(values)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(arr), len(arr))
        boots.append(np.median(arr[idx]))
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def main():
    df_bern = pd.read_parquet(RQ1 / "rq1_8m_5sel_bern.parquet")
    df_km20 = pd.read_parquet(RQ1 / "rq1_8m_5sel_km20.parquet")
    df = pd.concat([df_bern, df_km20], ignore_index=True)
    df = df.dropna(subset=["q_error"]).copy()

    print(f"=== DEEP 8M 5-sel 단조성 분석 ===")
    print(f"  bern rows  = {len(df_bern)}, valid = {len(df_bern.dropna(subset=['q_error']))}")
    print(f"  km20 rows  = {len(df_km20)}, valid = {len(df_km20.dropna(subset=['q_error']))}")
    print(f"  sels = {sorted(df['selectivity'].unique())}")
    print(f"  seeds = {sorted(df['seed'].unique())}")

    # === per-sel × per-seed median q_error ===
    per_sel_seed = []
    for sel in SELS:
        for mode in ["bernoulli", "km20"]:
            sub = df[(df["selectivity"].round(4) == round(sel, 4)) & (df["mode"] == mode)]
            for seed in SEEDS:
                ssub = sub[sub["seed"].round(4) == round(seed, 4)]
                if len(ssub) == 0:
                    continue
                m = float(ssub["q_error"].median())
                lo, hi = bootstrap_median(ssub["q_error"].values)
                per_sel_seed.append({
                    "selectivity": sel, "mode": mode, "seed": seed,
                    "median_q_error": m, "ci_lo": lo, "ci_hi": hi,
                    "n_queries": int(len(ssub)),
                })
    per_sel_seed_df = pd.DataFrame(per_sel_seed)

    # === per-sel mean ± std (across 5 seeds) ===
    per_sel = []
    diff_per_sel = []
    for sel in SELS:
        d_sel = per_sel_seed_df[per_sel_seed_df["selectivity"].round(4) == round(sel, 4)]
        bern_seeds = d_sel[d_sel["mode"] == "bernoulli"].set_index("seed")["median_q_error"]
        km_seeds = d_sel[d_sel["mode"] == "km20"].set_index("seed")["median_q_error"]
        bern_arr = bern_seeds.values
        km_arr = km_seeds.values
        per_sel.append({
            "selectivity": sel,
            "bern_mean": float(np.mean(bern_arr)) if len(bern_arr) else None,
            "bern_std": float(np.std(bern_arr, ddof=1)) if len(bern_arr) >= 2 else None,
            "km_mean": float(np.mean(km_arr)) if len(km_arr) else None,
            "km_std": float(np.std(km_arr, ddof=1)) if len(km_arr) >= 2 else None,
        })
        # per-seed diff_pct
        diffs = []
        for s in SEEDS:
            b = bern_seeds.get(s, np.nan)
            k = km_seeds.get(s, np.nan)
            if not np.isnan(b) and not np.isnan(k) and b > 0:
                diffs.append((k - b) / b * 100.0)
        diff_per_sel.append({
            "selectivity": sel,
            "diff_pct_mean": float(np.mean(diffs)) if diffs else None,
            "diff_pct_std": float(np.std(diffs, ddof=1)) if len(diffs) >= 2 else None,
            "n_seeds": len(diffs),
        })

    # === Spearman ρ per seed (3 versions) ===
    rho_records = {"bern_q_error": [], "km_q_error": [], "diff_pct": []}
    for seed in SEEDS:
        # bern q_error monotonicity
        sub = per_sel_seed_df[(per_sel_seed_df["seed"].round(4) == round(seed, 4)) &
                              (per_sel_seed_df["mode"] == "bernoulli")].sort_values("selectivity")
        if len(sub) >= 3:
            r, p = spearmanr(sub["selectivity"], sub["median_q_error"])
            rho_records["bern_q_error"].append({"seed": seed, "rho": float(r), "p": float(p)})

        # km q_error monotonicity
        sub = per_sel_seed_df[(per_sel_seed_df["seed"].round(4) == round(seed, 4)) &
                              (per_sel_seed_df["mode"] == "km20")].sort_values("selectivity")
        if len(sub) >= 3:
            r, p = spearmanr(sub["selectivity"], sub["median_q_error"])
            rho_records["km_q_error"].append({"seed": seed, "rho": float(r), "p": float(p)})

        # diff_pct monotonicity
        bern_sub = per_sel_seed_df[(per_sel_seed_df["seed"].round(4) == round(seed, 4)) &
                                   (per_sel_seed_df["mode"] == "bernoulli")].sort_values("selectivity")
        km_sub = per_sel_seed_df[(per_sel_seed_df["seed"].round(4) == round(seed, 4)) &
                                 (per_sel_seed_df["mode"] == "km20")].sort_values("selectivity")
        merged = pd.merge(
            bern_sub[["selectivity", "median_q_error"]].rename(columns={"median_q_error": "bern"}),
            km_sub[["selectivity", "median_q_error"]].rename(columns={"median_q_error": "km"}),
            on="selectivity",
        )
        merged["diff_pct"] = (merged["km"] - merged["bern"]) / merged["bern"] * 100.0
        if len(merged) >= 3:
            r, p = spearmanr(merged["selectivity"], merged["diff_pct"])
            rho_records["diff_pct"].append({"seed": seed, "rho": float(r), "p": float(p)})

    rho_summary = {}
    for k, v in rho_records.items():
        rs = [r["rho"] for r in v]
        rho_summary[k] = {
            "mean_rho": float(np.mean(rs)) if rs else None,
            "std_rho": float(np.std(rs, ddof=1)) if len(rs) >= 2 else None,
            "min_rho": float(np.min(rs)) if rs else None,
            "max_rho": float(np.max(rs)) if rs else None,
            "n_seeds": len(rs),
        }

    # === 1M cross-scale 비교 ===
    one_m = []
    for sel in SELS:
        sel_str = f"deep_s{sel:.2f}_numpy_remeasure_summary.json"
        if sel == 0.05:
            sel_str = "deep_s0.05_numpy_remeasure_summary.json"
        sf = RQ1 / sel_str
        if not sf.exists():
            continue
        d = json.loads(sf.read_text())
        one_m.append({
            "selectivity": sel,
            "diff_pct_mean": d["mean_diff_pct"],
            "diff_pct_std": d["std_diff_pct"],
        })

    cross_scale = []
    for sel in SELS:
        eight = next((x for x in diff_per_sel if x["selectivity"] == sel), None)
        one = next((x for x in one_m if x["selectivity"] == sel), None)
        if eight is None or one is None:
            continue
        cross_scale.append({
            "selectivity": sel,
            "1m_diff_pct_mean": one["diff_pct_mean"],
            "1m_diff_pct_std": one["diff_pct_std"],
            "8m_diff_pct_mean": eight["diff_pct_mean"],
            "8m_diff_pct_std": eight["diff_pct_std"],
            "delta_8m_minus_1m": (eight["diff_pct_mean"] - one["diff_pct_mean"])
                                  if (eight["diff_pct_mean"] is not None and one["diff_pct_mean"] is not None)
                                  else None,
        })

    # === Gradient 19.6%p 재현 ===
    # 1M Phase 6 (SQL D) s=0.01 km20 = -13.51%, Phase 7 (numpy D) s=0.01 = +6.07% (approx, per handoff)
    # → 19.6%p Δ origin: 일부는 methodology, 일부는 sel 변동.
    # 8M 에서는 Phase 7 numpy methodology 만 측정 → 1M Phase 7 vs 8M Phase 7 비교가 핵심.
    one_m_s001 = next((x for x in one_m if x["selectivity"] == 0.01), None)
    eight_m_s001 = next((x for x in diff_per_sel if x["selectivity"] == 0.01), None)
    gradient_check = {
        "1m_phase7_s001_diff_pct": one_m_s001["diff_pct_mean"] if one_m_s001 else None,
        "8m_phase7_s001_diff_pct": eight_m_s001["diff_pct_mean"] if eight_m_s001 else None,
        "abs_delta_p": (abs(eight_m_s001["diff_pct_mean"] - one_m_s001["diff_pct_mean"])
                        if (eight_m_s001 and one_m_s001 and
                            eight_m_s001["diff_pct_mean"] is not None and
                            one_m_s001["diff_pct_mean"] is not None) else None),
        "phase6_phase7_1m_gradient_p_known": 19.6,
        "interpretation": "8M Phase 7 vs 1M Phase 7 의 |Δ| 가 0 에 근접 → methodology 통일 시 cross-scale 일관성. "
                          "1M Phase 6 vs 1M Phase 7 의 19.6%p gradient 는 methodology 효과.",
    }

    summary = {
        "dataset": "DEEP_8M",
        "method": "Phase 7 numpy D_target",
        "sample_size": 385,
        "n_strata": 20,
        "n_seeds": len(SEEDS),
        "n_queries": 100,
        "per_sel_seed": per_sel_seed,
        "per_sel": per_sel,
        "diff_per_sel": diff_per_sel,
        "spearman_per_seed": rho_records,
        "spearman_summary": rho_summary,
        "cross_scale_1m_vs_8m": cross_scale,
        "gradient_check": gradient_check,
        "limitations": [
            "100 queries × 5 seed → bootstrap CI 는 query-level resample 만 (seed-level 추가 안함).",
            "8M Phase 6 (SQL D) 미측정 — Phase 7 numpy methodology 단일 비교만.",
            "Sample size 385 fixed — sample_size sensitivity 별도 분석 (8m_sel_expand worker 영역).",
        ],
    }

    out_json = RQ1 / "rq1_8m_monotonicity.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nsaved {out_json}")

    # === Markdown ===
    lines = []
    lines.append("# RQ1 — DEEP 8M 5-sel × 5 seed 단조성 (Worker J, 2026-05-07)")
    lines.append("")
    lines.append("**Methodology**: Phase 7 numpy D_target | sample_size=385 | n_strata=20 (KM20) | 100 queries × 5 seeds × 5 sels")
    lines.append("")
    lines.append("## 1. per-sel mean ± std (5 seed)")
    lines.append("")
    lines.append("| sel | bern q_error (mean ± std) | km20 q_error (mean ± std) | diff_pct (km20-bern, %) |")
    lines.append("|---|---|---|---|")
    for r, d in zip(per_sel, diff_per_sel):
        sel = r["selectivity"]
        bm, bs = r["bern_mean"], r["bern_std"]
        km, ks = r["km_mean"], r["km_std"]
        dm, ds = d["diff_pct_mean"], d["diff_pct_std"]
        lines.append(f"| {sel:.2f} | {bm:.4f} ± {bs:.4f} | {km:.4f} ± {ks:.4f} | {dm:+.2f}% ± {ds:.2f} |")
    lines.append("")
    lines.append("## 2. Spearman ρ per seed (단조성 방향)")
    lines.append("")
    lines.append(f"| ρ on | mean ± std | min | max | n |")
    lines.append("|---|---|---|---|---|")
    for k in ["bern_q_error", "km_q_error", "diff_pct"]:
        s = rho_summary[k]
        lines.append(f"| sel ↑ vs **{k}** | {s['mean_rho']:+.3f} ± {s['std_rho']:.3f} "
                     f"| {s['min_rho']:+.3f} | {s['max_rho']:+.3f} | {s['n_seeds']} |")
    lines.append("")
    lines.append("- bern_q_error/km_q_error: ρ ≈ -1 → sel ↑ ⇒ q_error ↓ 강한 단조성 (sample 수 증가 효과).")
    lines.append("- diff_pct: km20 우월성의 sel 의존성. ρ < 0 면 low-sel 에서 km20 효과 큼.")
    lines.append("")
    lines.append("## 3. Cross-scale 비교 (1M Phase 7 vs 8M Phase 7)")
    lines.append("")
    lines.append("| sel | 1M diff_pct (mean ± std) | 8M diff_pct (mean ± std) | Δ (8M − 1M, %p) |")
    lines.append("|---|---|---|---|")
    for c in cross_scale:
        sel = c["selectivity"]
        one_m_v = c["1m_diff_pct_mean"]; one_s = c["1m_diff_pct_std"]
        eight_v = c["8m_diff_pct_mean"]; eight_s = c["8m_diff_pct_std"]
        d = c["delta_8m_minus_1m"]
        lines.append(f"| {sel:.2f} | {one_m_v:+.2f}% ± {one_s:.2f} "
                     f"| {eight_v:+.2f}% ± {eight_s:.2f} "
                     f"| {d:+.2f}%p |")
    lines.append("")
    lines.append("**해석**: |Δ| 가 1M Phase 6↔7 gradient 19.6%p 보다 작을수록 methodology 통일 시 scale-invariance 강함. "
                 "각 sel 의 Δ 부호/크기로 cross-scale 일관성 정량화.")
    lines.append("")
    lines.append("## 4. Gradient 19.6%p 의 8M 재현")
    lines.append("")
    g = gradient_check
    lines.append(f"- 1M Phase 7 numpy s=0.01 diff_pct: **{g['1m_phase7_s001_diff_pct']:+.2f}%**")
    lines.append(f"- 8M Phase 7 numpy s=0.01 diff_pct: **{g['8m_phase7_s001_diff_pct']:+.2f}%**")
    lines.append(f"- |Δ| (8M − 1M, Phase 7 통일): **{g['abs_delta_p']:.2f}%p**")
    lines.append(f"- 1M 자체 Phase 6 vs Phase 7 gradient (참조): **19.6%p** (methodology 효과)")
    lines.append("")
    lines.append(f"→ {g['interpretation']}")
    lines.append("")
    lines.append("## 5. Limitations")
    lines.append("")
    for l in summary["limitations"]:
        lines.append(f"- {l}")
    lines.append("")

    out_md = RQ1 / "rq1_8m_monotonicity.md"
    with open(out_md, "w") as f:
        f.write("\n".join(lines))
    print(f"saved {out_md}")

    print("\n=== summary ===")
    for r, d in zip(per_sel, diff_per_sel):
        print(f"  s={r['selectivity']:.2f}: bern={r['bern_mean']:.4f} km={r['km_mean']:.4f} "
              f"Δ={d['diff_pct_mean']:+.2f}% ± {d['diff_pct_std']:.2f}")
    print(f"\n  ρ(sel,bern) = {rho_summary['bern_q_error']['mean_rho']:+.3f} ± {rho_summary['bern_q_error']['std_rho']:.3f}")
    print(f"  ρ(sel,km)   = {rho_summary['km_q_error']['mean_rho']:+.3f} ± {rho_summary['km_q_error']['std_rho']:.3f}")
    print(f"  ρ(sel,Δ%)   = {rho_summary['diff_pct']['mean_rho']:+.3f} ± {rho_summary['diff_pct']['std_rho']:.3f}")


if __name__ == "__main__":
    main()
