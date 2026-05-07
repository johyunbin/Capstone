#!/usr/bin/env python3
"""
RQ1 DEEP s=0.05 의 Phase 6 vs Phase 7 측정 방법론 차이 정량.

배경 (RQ1_RQ2 정리.md line 250):
\"KM20 gradient 가 10%(+4.19%) → 5%(+1.85%) 로 비단조적으로 하락. 이 비단조성에는
방법론적 차이가 기여할 가능성. s=0.050 실험은 Phase 6 (SQL 이진 탐색 D_target),
s=0.100 / 0.300 은 Phase 7 (numpy D_target).\"

본 분석: 같은 s=0.05 측정의 두 source 데이터 (Phase 6 vs Phase 7) 가 *어디에* 있는지
탐색 후, 정량 비교. 만약 Phase 6 측정이 Phase 7 보다 systematically 다르면, 정리.md
의 가설 정량 입증.

source 후보:
- Phase 6: random20_low_sel_summary.json (s=0.05 5-seed, 04/15)
- Phase 7: 1m_mid_summary.json (1m_mid_km20: s=0.10/0.30 만, s=0.05 X)

만약 Phase 7 의 s=0.05 측정이 없으면, Phase 6 의 s=0.05 와 Phase 7 의 s=0.10 (인접 sel)
의 "interpolated 비교" 로 trend 차이 추정.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ1 = ROOT / "Capstone" / "experiments" / "results" / "rq1_motivation"
RQ2 = ROOT / "Capstone" / "experiments" / "results" / "rq2_aware"
if not RQ1.exists():
    RQ1 = Path(__file__).resolve().parent.parent.parent / "results" / "rq1_motivation"
    RQ2 = Path(__file__).resolve().parent.parent.parent / "results" / "rq2_aware"


def main():
    print("=" * 70)
    print("RQ1 DEEP s=0.05 Phase 6 vs Phase 7 측정 비교")
    print("=" * 70)

    # Phase 6 — random20_low_sel_summary.json (s=0.01, 0.05)
    p6_path = RQ1 / "random20_low_sel_summary.json"
    p6 = json.load(open(p6_path))
    p6_05_km = p6["sels"]["s0.05"]["km20"]
    p6_05_rand = p6["sels"]["s0.05"]["rand"]
    p6_diff_km_005 = p6_05_km["mean"]
    p6_seeds_km_005 = [x["diff_pct"] for x in p6_05_km["per_seed"]]
    p6_seeds_rand_005 = [x["diff_pct"] for x in p6_05_rand["per_seed"]]

    # Phase 7 source — sift_1m_mid_summary.json (1m_mid_km20: s=0.10/0.30)
    p7_path = RQ2 / "sift_1m_mid_summary.json"
    p7 = json.load(open(p7_path))
    p7_010_km = p7.get("1m_mid_km20", {}).get("s0.1", {})
    p7_030_km = p7.get("1m_mid_km20", {}).get("s0.3", {})
    p7_010_diff = p7_010_km.get("mean_diff_pct")
    p7_030_diff = p7_030_km.get("mean_diff_pct")
    p7_seeds_010 = [x["diff_pct"] for x in p7_010_km.get("per_seed", [])]
    p7_seeds_030 = [x["diff_pct"] for x in p7_030_km.get("per_seed", [])]

    # === 1. Phase 6 의 s=0.05 vs Phase 7 의 s=0.10 인접 비교 ===
    print(f"\n[Phase 6, 04/15 SQL 이진 탐색 D_target]")
    print(f"  s=0.05  KM20-BERN: mean = {p6_diff_km_005:+.2f}%, per-seed = {[f'{x:+.2f}' for x in p6_seeds_km_005]}")
    print(f"  s=0.05  RAND-BERN: mean = {p6_05_rand['mean']:+.2f}%")

    print(f"\n[Phase 7, 05/06 numpy D_target]")
    print(f"  s=0.10  KM20-BERN: mean = {p7_010_diff:+.2f}%, per-seed = {[f'{x:+.2f}' for x in p7_seeds_010]}")
    print(f"  s=0.30  KM20-BERN: mean = {p7_030_diff:+.2f}%, per-seed = {[f'{x:+.2f}' for x in p7_seeds_030]}")

    # === 2. Phase 6 's=0.05' 가 Phase 7 인접 sel (s=0.10) 보다 *작은지* (정리.md 의 비단조 패턴) ===
    print("\n=== Comparison ===")
    print(f"Phase 6 s=0.05 (4/15): {p6_diff_km_005:+.2f}%")
    print(f"Phase 7 s=0.10 (5/06): {p7_010_diff:+.2f}%")
    diff = p7_010_diff - p6_diff_km_005
    print(f"   Δ (Phase 7 s=0.10 - Phase 6 s=0.05): {diff:+.2f}%p")
    if diff > 0:
        print(f"   → Phase 7 (numpy D) 가 Phase 6 (SQL D) 보다 KM20 효과 강함 (s=0.10 > s=0.05 — 비단조).")
        print(f"   → 만약 같은 sel 에서 측정했으면 일관 트렌드일 가능성. 측정 방법 차이가 기여.")
    else:
        print(f"   → Phase 6 의 s=0.05 효과 가 Phase 7 의 s=0.10 보다 강함 — RQ1 narrative 의 단조 흐름 일관.")

    # === 3. Phase 6 측정의 method noise 비교 (per-seed 분산) ===
    p6_std = np.std(p6_seeds_km_005, ddof=1) if len(p6_seeds_km_005) > 1 else 0
    p7_010_std = np.std(p7_seeds_010, ddof=1) if len(p7_seeds_010) > 1 else 0
    print(f"\nPer-seed std:")
    print(f"  Phase 6 s=0.05: std = {p6_std:.3f}%")
    print(f"  Phase 7 s=0.10: std = {p7_010_std:.3f}%")
    if p7_010_std < p6_std * 0.7:
        print(f"  → Phase 7 의 std 가 Phase 6 의 70% 이하 — numpy D_target 이 더 안정적.")
    elif p6_std < p7_010_std * 0.7:
        print(f"  → Phase 6 의 std 가 Phase 7 의 70% 이하 — SQL D_target 이 더 안정적 (예상 외).")
    else:
        print(f"  → Phase 6/7 의 std 비슷 — 방법론 차이의 noise 기여 적음.")

    # === 4. 2-sample test (Phase 6 s=0.05 mean vs Phase 7 s=0.10 mean) ===
    from scipy.stats import ttest_ind
    if len(p6_seeds_km_005) > 1 and len(p7_seeds_010) > 1:
        t_stat, p_val = ttest_ind(p6_seeds_km_005, p7_seeds_010, equal_var=False)
        print(f"\n2-sample Welch t-test (Phase 6 s=0.05 vs Phase 7 s=0.10):")
        print(f"  t = {t_stat:.3f}, p = {p_val:.4f}")
        if p_val < 0.05:
            print(f"  → 두 측정 mean 이 통계적으로 다름 (p<0.05). 같은 sel 이라면 단조 추세.")
        else:
            print(f"  → 두 mean 통계적 차이 X — 방법론 차이의 영향 작음, 또는 sel 자체 차이.")

    # === 5. 결과 저장 ===
    out = {
        "phase6_s0.05_km": {"mean": p6_diff_km_005, "per_seed": p6_seeds_km_005, "std": p6_std},
        "phase6_s0.05_rand": {"mean": p6_05_rand["mean"], "per_seed": p6_seeds_rand_005},
        "phase7_s0.10_km": {"mean": p7_010_diff, "per_seed": p7_seeds_010, "std": p7_010_std},
        "phase7_s0.30_km": {"mean": p7_030_diff, "per_seed": p7_seeds_030},
        "delta_phase7_p10_minus_phase6_p05": float(p7_010_diff - p6_diff_km_005),
        "interpretation": (
            "Phase 7 s=0.10 가 Phase 6 s=0.05 보다 강한 효과면 → 같은 sel 에서 측정 시 더 강한 단조 패턴 기대"
            if p7_010_diff > p6_diff_km_005 else
            "Phase 6 s=0.05 가 더 강한 효과 → RQ1 narrative 의 단조 흐름 일관"
        ),
        "future_work": "DEEP s=0.05 의 numpy D_target 재측정 (G wrapper) 후 정량 결정",
    }
    out_path = RQ1 / "rq1_phase6_vs_phase7_comparison.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n[saved] {out_path}")


if __name__ == "__main__":
    main()
