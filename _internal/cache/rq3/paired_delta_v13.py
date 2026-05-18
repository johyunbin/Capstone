#!/usr/bin/env python3
"""
paired_delta_v13.py — 3-way matched paired Δ% 분석 (task I, 5/17 세션)

3-way matched
-------------
각 (cell,sel,K,method) 측정이 measure_3way 로 B1·CaseA·CaseB 를 같은 trial·query
조건에서 산출 → 셋이 완벽히 matched. v12 의 B1 lookup·fallback_K20 가 불필요하며,
K=10 도 자체 B1 (1단계, STRATA_K 캐시 우회 → 결함 없음) 으로 깨끗하게 비교한다.

비교 3종 (delta = (exp_qe − base_qe) / base_qe × 100, 음수 = exp 쪽이 더 정확)
----------------------------------------------------------------------
- CaseA_vs_B1    : exp=CaseA  base=B1     완전 대체 vs 대조군
- CaseB_vs_B1    : exp=CaseB  base=B1     결합 vs 대조군 (REPORT v12 headline 대응)
- CaseA_vs_CaseB : exp=CaseA  base=CaseB  완전 대체 vs 결합

통계
----
trial-paired (10 trial) Wilcoxon signed-rank (two-sided + greater) — exact (n≤25).
BH-FDR 는 comparison family 별 적용 (3 family). Cliff's δ (POSITIVE = exp 우위),
Hedges' g (NEGATIVE = exp 우위). analyze_paper_exact.py 의 검증된 함수 재사용.

usage
-----
  python3 paired_delta_v13.py
입력: _internal/cache/rq3/aggregated_v13_full.parquet
출력: _internal/cache/rq3/paired_delta_v13.parquet  (long, 1 row per (json_id,comparison))
"""
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "_internal" / "scripts"))
from analyze_paper_exact import paired_delta, bh_fdr  # noqa: E402

IN_PARQUET = REPO_ROOT / "_internal" / "cache" / "rq3" / "aggregated_v13_full.parquet"
OUT_PARQUET = REPO_ROOT / "_internal" / "cache" / "rq3" / "paired_delta_v13.parquet"

# (comparison, base mode, exp mode) — paired_delta(base, exp) → delta=(exp−base)/base
COMPARISONS = [
    ("CaseA_vs_B1", "B1", "CaseA"),
    ("CaseB_vs_B1", "B1", "CaseB"),
    ("CaseA_vs_CaseB", "CaseB", "CaseA"),
]


def main():
    df = pd.read_parquet(IN_PARQUET)
    rows = []
    n_skip = 0
    for json_id, g in df.groupby("json_id"):
        modes = {r["mode"]: r for _, r in g.iterrows()}
        if set(modes) != {"B1", "CaseA", "CaseB"}:
            print(f"  skip {json_id}: mode 불완전 {sorted(modes)}", file=sys.stderr)
            n_skip += 1
            continue
        meta = modes["B1"]
        trial_qe = {m: json.loads(modes[m]["trial_qe_list"]) for m in modes}
        for comp, base_m, exp_m in COMPARISONS:
            d = paired_delta(trial_qe[base_m], trial_qe[exp_m])
            rows.append({
                "json_id": json_id,
                "cell": meta["cell"],
                "dataset": meta["dataset"],
                "single_multi": meta["single_multi"],
                "sf": meta["sf"],
                "dim": meta["dim"],
                "type_label": meta["type_label"],
                "sel": meta["sel"],
                "K": meta["K"],
                "method": meta["method"],
                "paradigm": meta["paradigm"],
                "comparison": comp,
                "base_mode": base_m,
                "exp_mode": exp_m,
                "n_trials": d["n_trials"],
                "base_qe_mean": d["b1_mean"],      # paired_delta 의 historical 키
                "exp_qe_mean": d["casea_mean"],
                "delta_pct_mean": d["delta_pct_mean"],
                "delta_pct_median": d["delta_pct_median"],
                "wilcoxon_p": d["wilcoxon_p"],
                "wilcoxon_p_greater": d["wilcoxon_p_greater"],
                "hedges_g": d["hedges_g"],
                "cliffs_delta": d["cliffs_delta"],
            })

    dfp = pd.DataFrame(rows)
    # BH-FDR — comparison family 별 (3 family 독립 보정)
    dfp["p_adj_bh"] = float("nan")
    dfp["p_adj_bh_greater"] = float("nan")
    for comp in dfp["comparison"].unique():
        mask = dfp["comparison"] == comp
        dfp.loc[mask, "p_adj_bh"] = bh_fdr(dfp.loc[mask, "wilcoxon_p"].tolist())
        dfp.loc[mask, "p_adj_bh_greater"] = bh_fdr(dfp.loc[mask, "wilcoxon_p_greater"].tolist())
    dfp = dfp.sort_values(["comparison", "cell", "sel", "K", "method"]).reset_index(drop=True)

    dfp.to_parquet(OUT_PARQUET, index=False)
    print(f"wrote {OUT_PARQUET}  ({len(dfp)} rows = {len(dfp) // 3} 측정 × 3 comparison)")
    if n_skip:
        print(f"  skip(mode 불완전): {n_skip} measurement")

    # --- 요약 ---
    print("\n=== comparison 별 요약 ===")
    for comp, _, _ in COMPARISONS:
        sub = dfp[dfp["comparison"] == comp]
        n = len(sub)
        if n == 0:
            continue
        better = int((sub["delta_pct_mean"] < 0).sum())
        sig = int(((sub["delta_pct_mean"] < 0) & (sub["p_adj_bh_greater"] < 0.05)).sum())
        cliff_l = int((sub["cliffs_delta"] >= 0.474).sum())
        print(f"  {comp:16s}: n={n}  better={better} ({100 * better / n:.1f}%)  "
              f"유의={sig} ({100 * sig / n:.1f}%)  δlarge={cliff_l} ({100 * cliff_l / n:.1f}%)  "
              f"mean Δ%={sub['delta_pct_mean'].mean():+.2f}  median={sub['delta_pct_mean'].median():+.2f}")
    # K 별 (CaseB_vs_B1) — v12 K=10 결함 후 깨끗한 K granularity 검증
    print("\n=== CaseB_vs_B1 — K 별 (v12 K=10 결함 대비 검증) ===")
    cbb = dfp[dfp["comparison"] == "CaseB_vs_B1"]
    for K in sorted(cbb["K"].dropna().unique()):
        s = cbb[cbb["K"] == K]
        better = int((s["delta_pct_mean"] < 0).sum())
        print(f"  K={int(K)}: n={len(s)}  better={better} ({100 * better / len(s):.1f}%)  "
              f"mean Δ%={s['delta_pct_mean'].mean():+.2f}  median={s['delta_pct_mean'].median():+.2f}")


if __name__ == "__main__":
    main()
