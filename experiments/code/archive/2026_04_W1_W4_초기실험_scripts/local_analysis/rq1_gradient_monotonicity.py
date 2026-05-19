#!/usr/bin/env python3
"""
RQ1 Cross-Dataset gradient monotonicity 통계 검정.

가설:
  - selectivity 가 낮을수록 KM20 - BERN 개선 폭이 커진다 (Two-Level decomposition
    에서 Level 2 가 selectivity-dependent).
  - 단조 감소: sel ↓ → diff% ↑.

검정:
  - Spearman rank correlation: sel ranks vs diff% ranks per seed → r_s < 0 검증.
  - Mann-Kendall trend test: seed-mean 의 단조 추세 (S statistic + p-value).
  - per-seed 결과를 합쳐서 winsorized 평균 r_s 도 보고.

데이터 출처:
  - DEEP 1M:
    s=0.010, 0.050 → random20_low_sel_summary.json (5-seed)
    s=0.100, 0.300 → sift_1m_mid_summary.json:1m_mid_km20 (5-seed)
    s=0.500       → random20_control_summary.json:all_selectivity_paired (1-seed)
                    또는 sift_1m_mid 가 없음 — 정리.md 의 +1.64% 는 pre-W1 측정.
  - SIFT 1.5M:
    s=0.010, 0.050, 0.500 → sift_1m_mid_summary.json:sift_km20 (5-seed)
    s=0.100, 0.300 → 미측정 (정리.md 287 line 의 future work).

산출:
  - rq1_gradient_monotonicity_summary.csv — long-form (dataset/sel/mean/std/n)
  - rq1_gradient_monotonicity_test.json — 검정 통계
  - rq1_gradient_monotonicity.md — narrative
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RQ1 = ROOT / "experiments" / "results" / "rq1_motivation"
RQ2 = ROOT / "experiments" / "results" / "rq2_aware"
OUT = RQ1


def _load_low_sel():
    """DEEP s=0.010, 0.050 (5-seed)."""
    p = RQ1 / "random20_low_sel_summary.json"
    d = json.load(open(p))
    rows = []
    for sel_key, body in d["sels"].items():
        sel = float(sel_key.replace("s", ""))
        for arm in ("km20", "rand"):
            for x in body[arm]["per_seed"]:
                rows.append({
                    "dataset": "DEEP",
                    "arm": arm.upper(),
                    "sel": sel,
                    "seed": x["seed"],
                    "diff_pct": x["diff_pct"],
                })
    return pd.DataFrame(rows)


def _load_mid_sel():
    """DEEP s=0.100, 0.300 (5-seed) + SIFT s=0.010, 0.050, 0.500 (5-seed)
    + SIFT s=0.100, 0.300 (5/7 새벽 final_chain 측정 — sift_mid_sel_summary.json)."""
    p = RQ2 / "sift_1m_mid_summary.json"
    d = json.load(open(p))
    rows = []
    mapping = {
        "1m_mid_km20": ("DEEP", "KM20"),
        "1m_mid_rand": ("DEEP", "RAND"),
        "sift_km20": ("SIFT", "KM20"),
        "sift_rand": ("SIFT", "RAND"),
    }
    for top, (dataset, arm) in mapping.items():
        if top not in d:
            continue
        for sel_key, body in d[top].items():
            sel = float(sel_key.replace("s", ""))
            for x in body["per_seed"]:
                rows.append({
                    "dataset": dataset,
                    "arm": arm,
                    "sel": sel,
                    "seed": x["seed"],
                    "diff_pct": x["diff_pct"],
                })

    # 5/7 final_chain 신규 SIFT mid-sel (s=0.10, 0.30)
    p2 = RQ1 / "sift_mid_sel_summary.json"
    if p2.exists():
        d2 = json.load(open(p2))
        new_mapping = {
            "sift_km20_mid": ("SIFT", "KM20"),
            "sift_rand_mid": ("SIFT", "RAND"),
        }
        for top, (dataset, arm) in new_mapping.items():
            if top not in d2 or not d2[top]:
                continue
            for sel_key, body in d2[top].items():
                if not body or "per_seed" not in body:
                    continue
                sel = float(sel_key.replace("s", ""))
                for x in body["per_seed"]:
                    rows.append({
                        "dataset": dataset,
                        "arm": arm,
                        "sel": sel,
                        "seed": x["seed"],
                        "diff_pct": x["diff_pct"],
                    })

    return pd.DataFrame(rows)


def _load_deep_500():
    """DEEP s=0.500 (1-seed pre-W1 측정 — random20_control_summary.json).

    Spearman 의 nested 5-seed 와는 다른 source 라 별도 1-seed 점만 사용.
    """
    p = RQ1 / "random20_control_summary.json"
    d = json.load(open(p))
    rows = []
    for x in d.get("all_selectivity_paired", []):
        if x["selectivity"] not in (0.500,):
            continue
        rows.append({
            "dataset": "DEEP",
            "arm": "KM20",
            "sel": x["selectivity"],
            "seed": 0.42,
            "diff_pct": x["diff_pct"],
        })
    # RANDOM20 1-seed 도 포함되어 있지만 5-seed 와 섞으면 noise 균형 깨지므로 제외
    return pd.DataFrame(rows)


def mann_kendall(x: np.ndarray) -> dict:
    """Mann-Kendall trend test (one-sided, 'decreasing as index 증가').

    Args:
        x: 시계열 배열 (여기선 sel 오름차순 → diff% sequence). 단조 *감소* 가
        normalized null 'no trend' 가설. 대립가설: 단조 감소 (S<0).

    Returns:
        S, var_S, z, p_two_sided.
    """
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
    p_two_sided = 2 * (1 - stats.norm.cdf(abs(z)))
    return {"S": int(s), "var_S": var_s, "z": z, "p_two_sided": p_two_sided}


def per_seed_spearman(df: pd.DataFrame, dataset: str, arm: str) -> dict:
    """seed 마다 Spearman ρ(sel, diff%) 계산 → mean ρ + 95% bootstrap CI.

    선언적 가설: ρ < 0 (sel 작을수록 diff% 큼).
    """
    sub = df[(df["dataset"] == dataset) & (df["arm"] == arm)]
    if sub.empty:
        return {"n_seeds": 0}
    rhos = []
    for seed, group in sub.groupby("seed"):
        if len(group) < 3:
            continue
        rho, _p = stats.spearmanr(group["sel"], group["diff_pct"])
        if not np.isnan(rho):
            rhos.append(float(rho))
    if not rhos:
        return {"n_seeds": 0}
    rng = np.random.default_rng(42)
    n_boot = 5000
    boot = []
    for _ in range(n_boot):
        idx = rng.choice(len(rhos), size=len(rhos), replace=True)
        boot.append(np.mean([rhos[i] for i in idx]))
    boot = np.array(boot)
    return {
        "n_seeds": len(rhos),
        "rhos": rhos,
        "mean_rho": float(np.mean(rhos)),
        "ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
    }


def cell_summary(df: pd.DataFrame) -> pd.DataFrame:
    """(dataset, arm, sel) 별 mean ± std + 5-seed n."""
    g = df.groupby(["dataset", "arm", "sel"])["diff_pct"].agg(
        ["mean", "std", "count"]
    ).reset_index()
    g["std"] = g["std"].fillna(0.0)
    return g


def trend_test_pooled(summary: pd.DataFrame, dataset: str, arm: str) -> dict:
    """seed-mean sequence 에 Mann-Kendall + Spearman.

    sel 오름차순으로 sequence 정렬. 단조 감소 (Level 2 가설) 기대.
    """
    sub = summary[(summary["dataset"] == dataset) & (summary["arm"] == arm)].sort_values("sel")
    if len(sub) < 3:
        return {"n_cells": len(sub), "note": "n<3 — trend test impossible"}
    means = sub["mean"].values
    sels = sub["sel"].values
    mk = mann_kendall(means)
    rho_pooled, p_pooled = stats.spearmanr(sels, means)
    return {
        "n_cells": int(len(sub)),
        "sels": sels.tolist(),
        "means": means.tolist(),
        "mann_kendall_S": mk["S"],
        "mann_kendall_z": mk["z"],
        "mann_kendall_p_two_sided": mk["p_two_sided"],
        "spearman_rho": float(rho_pooled) if not np.isnan(rho_pooled) else None,
        "spearman_p_two_sided": float(p_pooled) if not np.isnan(p_pooled) else None,
    }


def main():
    df = pd.concat([_load_low_sel(), _load_mid_sel(), _load_deep_500()], ignore_index=True)
    print(f"[load] {len(df):,} rows")
    print(df.groupby(["dataset", "arm", "sel"]).size().unstack(fill_value=0))

    summary = cell_summary(df)
    print("\n=== cell summary (mean diff% ± std, n_seeds) ===")
    print(summary.to_string(index=False))
    summary.to_csv(OUT / "rq1_gradient_monotonicity_summary.csv", index=False)
    print(f"[saved] {OUT / 'rq1_gradient_monotonicity_summary.csv'}")

    results = {}
    for dataset in ["DEEP", "SIFT"]:
        for arm in ["KM20", "RAND"]:
            key = f"{dataset}_{arm}"
            ps = per_seed_spearman(df, dataset, arm)
            tp = trend_test_pooled(summary, dataset, arm)
            results[key] = {"per_seed": ps, "pooled": tp}
            print(f"\n--- {key} ---")
            if ps.get("n_seeds", 0):
                print(f"  per-seed Spearman: mean ρ = {ps['mean_rho']:+.3f}, "
                      f"95% CI [{ps['ci95'][0]:+.3f}, {ps['ci95'][1]:+.3f}], n_seeds={ps['n_seeds']}")
            else:
                print(f"  per-seed Spearman: n/a (data insufficient)")
            if tp.get("n_cells", 0) >= 3:
                print(f"  pooled Mann-Kendall: S={tp['mann_kendall_S']:+d}, "
                      f"z={tp['mann_kendall_z']:+.3f}, p={tp['mann_kendall_p_two_sided']:.4f}")
                print(f"  pooled Spearman: ρ={tp['spearman_rho']:+.3f}, "
                      f"p={tp['spearman_p_two_sided']:.4f}")
                print(f"  sels={tp['sels']}, means={[f'{m:+.2f}' for m in tp['means']]}")
            else:
                print(f"  pooled trend: skip ({tp.get('note', tp)})")

    with open(OUT / "rq1_gradient_monotonicity_test.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[saved] {OUT / 'rq1_gradient_monotonicity_test.json'}")

    # narrative md 작성
    md = ["# RQ1 Cross-Dataset Gradient 단조성 통계 검정",
          "",
          "5/6 W1 sprint 추가 분석. RQ1 의 핵심 narrative \"selectivity 가 낮을수록 KM20 의",
          "공간 인식 sampling 가치가 커진다 (Level 2 효과)\" 를 정량 검정.",
          "",
          "## 가설",
          "",
          "**H1-G** (Gradient): sel 이 낮을수록 KM20 - BERN 개선 폭이 단조 증가한다.",
          "  - 통계적 표현: ρ(sel, diff_pct) < 0 (Spearman)",
          "  - 또는 Mann-Kendall S < 0 (sel 오름차순 → diff% 단조 감소)",
          "",
          "**H1-G\\***: 같은 단조성이 RANDOM20 의 악화 패턴 (sel 작을수록 diff% 음수 커짐) 으로도",
          "재현된다. 즉 KM20 은 양의 단조 감소 (sel↓ → diff%↑), RANDOM20 은 음의 단조 감소",
          "(sel↓ → diff%↓) 패턴.",
          "",
          "## 데이터",
          "",
          "| dataset | arm | sel | mean diff% | std | n_seeds |",
          "|---------|-----|-----|-----------:|----:|--------:|",
          ]
    for _, r in summary.iterrows():
        md.append(f"| {r['dataset']} | {r['arm']} | {r['sel']:.3f} | "
                  f"{r['mean']:+.2f} | {r['std']:.2f} | {int(r['count'])} |")
    md.extend([
        "",
        "## 검정 결과",
        "",
    ])
    for key, r in results.items():
        md.append(f"### {key.replace('_', ' × ')}")
        md.append("")
        ps = r["per_seed"]
        if ps.get("n_seeds", 0):
            md.append(f"- **per-seed Spearman ρ**: mean = `{ps['mean_rho']:+.3f}`, "
                      f"95% CI `[{ps['ci95'][0]:+.3f}, {ps['ci95'][1]:+.3f}]` (n_seeds={ps['n_seeds']})")
        tp = r["pooled"]
        if tp.get("n_cells", 0) >= 3:
            md.append(f"- **pooled (seed-mean) Mann-Kendall**: S=`{tp['mann_kendall_S']:+d}`, "
                      f"z=`{tp['mann_kendall_z']:+.3f}`, p=`{tp['mann_kendall_p_two_sided']:.4f}`")
            md.append(f"- **pooled Spearman**: ρ=`{tp['spearman_rho']:+.3f}`, "
                      f"p=`{tp['spearman_p_two_sided']:.4f}`")
            md.append(f"- sels: `{tp['sels']}`, means: `{[round(m,2) for m in tp['means']]}`")
        md.append("")

    md.extend([
        "## 해석",
        "",
        "### DEEP 1M",
        "",
        "- **KM20 arm**: sel 5점 (0.01, 0.05, 0.10, 0.30, 0.50) 모두 양의 효과지만, s=0.05 가",
        "  s=0.10 보다 작은 비단조 패턴. RQ1_RQ2 정리.md (line 250) 에 기록된 Phase 6/Phase 7 측정",
        "  방법론 차이 (SQL 이진 탐색 vs numpy D_target) 가 원인 후보. 그럼에도 sel 양 끝 (0.01 vs",
        "  0.50) 에서 +8.93% > +1.64% 의 차이는 강한 Level 2 효과를 시사.",
        "- **RAND arm**: s=0.01 에서 -10.67% (Level 2 의 reverse 효과 — 무작위 partition 이",
        "  집중 영역을 왜곡), s=0.50 에서 +2.20% (Level 1 만 작동). 단조 *증가* (sel 작을수록",
        "  음수 커짐).",
        "",
        "### SIFT 1.5M",
        "",
        "- **KM20 arm**: s=0.01 에서 -0.53% anomaly (sample_size=385 가 1.5만 true_card 추정에",
        "  부족 — RQ1_RQ2 정리.md line 278 의 Anomaly 3 참조). 이 점을 제외하면 s=0.05 (+4.39%) >",
        "  s=0.50 (+3.07%) 의 단조 감소 (Level 2). s=0.10/0.30 미측정 (future work).",
        "- **RAND arm**: s=0.01 에서 -12.11% (DEEP -10.67% 보다 더 심함, skew 더 강한 데이터에서",
        "  무작위 partition 의 손실 배가). s=0.50 에서 +1.01%. 단조 증가 패턴.",
        "",
        "### 검정 결론",
        "",
        "1. **DEEP-KM20 의 단조성**: per-seed Spearman 평균 ρ 가 음수면서 95% CI 가 0 을 포함",
        "   하지 않으면 H1-G confirmed. CI 가 0 을 포함하면 s=0.05/0.10 anomaly 로 단조성 약화로",
        "   해석.",
        "2. **DEEP-RAND 의 단조 감소** 는 KM20 보다 stronger signal 이어야 함 (Level 2 reverse",
        "   가 더 큰 dynamic range 를 가짐: +2.2% ~ -10.7% range 19%p). 만약 |ρ_RAND| > |ρ_KM20|",
        "   이면 본 narrative 가 강화됨.",
        "3. **SIFT 의 단조성**: 3 점만 있으므로 단조성 검정의 power 가 낮음. mid-sel 보충 측정",
        "   (정리.md line 288) 후 재검정 권장.",
        "",
        "### Future Work — 단조성 재검정",
        "",
        "- SIFT s=0.10, s=0.30 측정 (정리.md line 287-291) — 5 점 완성 시 Mann-Kendall power 회복.",
        "- DEEP s=0.05 의 Phase 6/7 방법론 차이 재측정 — numpy D_target 으로 통일 후 단조성 개선",
        "  여부 확인.",
        "- 8M 측정 완료 후 동일 검정 8M 데이터에서 재현 (cross-scale 검증).",
        "",
        ])
    with open(OUT / "rq1_gradient_monotonicity.md", "w") as f:
        f.write("\n".join(md))
    print(f"[saved] {OUT / 'rq1_gradient_monotonicity.md'}")


if __name__ == "__main__":
    main()
