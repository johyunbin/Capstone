#!/usr/bin/env python3
"""
Layer 4 audit — cherry-picking 검증 (handoff §2.4).

검증 항목:
1. handoff §1.4 표 ("Top 15 wins" / "Bottom 5 outliers") 의 selection bias
2. 모든 (cell × method × mode) Δ% 분포 (histogram)
3. 메인 REPORT.md 핵심 claim의 cell-level vs method-mean variance
4. minibatch_partial -7.41% / sparse_rp -7.11% 같은 specific number 의 출처 검증
5. paper Fig 12 1.69 비교 시 A4-sel 포함의 inflate 효과
6. method/paradigm별 win rate를 산포 (per-cell variance) 함께 표기
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "cherrypicking_audit.md"

# Paradigm mapping (RQ3 framework — 5 paradigm × 11+ method)
PARADIGM = {
    # P1 Cluster
    "minibatch": "P1-Cluster", "minibatch_partial": "P1-Cluster",
    "gmm": "P1-Cluster", "kdpp": "P1-Cluster", "coreset": "P1-Cluster",
    "birch": "P1-Cluster", "agglomerative": "P1-Cluster",
    "kdtree": "P1-Cluster", "cocluster_nystrom": "P1-Cluster",
    # P2 Spatial / Index
    "faiss_ivf": "P2-Spatial", "lsh": "P2-Spatial", "hilbert": "P2-Spatial",
    "epsilon_net": "P2-Spatial", "hkbu_repsample": "P2-Spatial",
    "opq": "P2-Spatial", "pq": "P2-Spatial",
    # P3 Streaming / Sketch
    "reservoir": "P3-Streaming", "thompson_sampling": "P3-Streaming",
    "banditucb1": "P3-Streaming", "ams_count_sketch": "P3-Streaming",
    "ccsketch": "P3-Streaming", "mfmc": "P3-Streaming",
    "adaptive_bucket_probing": "P3-Streaming",
    # P4 DimReduction
    "pca1d": "P4-DimReduction", "random_projection": "P4-DimReduction",
    "sparse_rp": "P4-DimReduction", "dense_rp": "P4-DimReduction",
    "tucker": "P4-DimReduction", "cca1d": "P4-DimReduction",
    # P5 Low-discrepancy / Quasi-random
    "sobol": "P5-LowDiscrepancy", "halton": "P5-LowDiscrepancy",
    "hammersley": "P5-LowDiscrepancy", "lhs": "P5-LowDiscrepancy",
    # 기타 (P? Other)
    "neuram": "P?-Other", "neurocard_lite": "P?-Other",
    "factor_join": "P?-Other", "lp_bound": "P?-Other",
    "lpm2": "P?-Other", "vinecopula": "P?-Other",
}


def audit():
    md = ["# Layer 4 — Cherry-picking 검증\n",
          "_생성_: 2026-05-10 검증 세션 (read-only)\n",
          "_목적_: REPORT.md / handoff narrative selection bias 점검\n",
          "---\n"]

    df_paired = pd.read_csv(Path(__file__).parent / "audit_data_paired.csv")
    df_wilc = pd.read_csv(Path(__file__).parent / "audit_data_wilcoxon.csv")
    df = df_paired.merge(df_wilc[["cell", "method", "mode", "p_two_sided",
                                    "p_one_sided_better", "p_adj_main",
                                    "p_adj_one_sided"]],
                          on=["cell", "method", "mode"])
    df["paradigm"] = df["method"].map(lambda m: PARADIGM.get(m, "P?-Unknown"))

    # === 1. Δ% 전체 분포 ===
    md.append("## 1. Δ% 전체 분포 (cell × method × mode)\n")
    df_finite = df[np.isfinite(df["delta_A"])].copy()
    md.append(f"- Total finite measurements: {len(df_finite)}")
    md.append(f"  - CaseA: {(df_finite['mode']=='CaseA').sum()}")
    md.append(f"  - CaseB: {(df_finite['mode']=='CaseB').sum()}")
    md.append("")

    # histogram bins
    bins = [-100, -20, -10, -5, -1, 1, 5, 10, 20, 100, 1e6]
    bin_labels = ["≤-20%", "-20~-10%", "-10~-5%", "-5~-1%", "-1~+1%",
                  "+1~+5%", "+5~+10%", "+10~+20%", "+20~+100%", ">+100%"]
    md.append("**Δ% histogram (bins)**:")
    md.append("| Bin | CaseA | CaseB |")
    md.append("|---|---|---|")
    for b_lo, b_hi, lbl in zip(bins[:-1], bins[1:], bin_labels):
        n_a = ((df_finite["mode"] == "CaseA") &
               (df_finite["delta_A"] >= b_lo) &
               (df_finite["delta_A"] < b_hi)).sum()
        n_b = ((df_finite["mode"] == "CaseB") &
               (df_finite["delta_A"] >= b_lo) &
               (df_finite["delta_A"] < b_hi)).sum()
        md.append(f"| {lbl} | {n_a} | {n_b} |")
    md.append("")
    md.append("**핵심 발견**:")
    n_a_neg = ((df_finite["mode"] == "CaseA") & (df_finite["delta_A"] < 0)).sum()
    n_b_neg = ((df_finite["mode"] == "CaseB") & (df_finite["delta_A"] < 0)).sum()
    n_a = (df_finite["mode"] == "CaseA").sum()
    n_b = (df_finite["mode"] == "CaseB").sum()
    md.append(f"- CaseA Δ% < 0 (B1 대비 좋음): **{n_a_neg}/{n_a}** ({n_a_neg/n_a*100:.1f}%)")
    md.append(f"- CaseB Δ% < 0: **{n_b_neg}/{n_b}** ({n_b_neg/n_b*100:.1f}%)")
    md.append("")

    # === 2. handoff §1.4 표 cell-level vs method-mean ===
    md.append("## 2. handoff §1.4 핵심 결과 표 검증\n")
    md.append("**handoff §1.4의 표가 method-mean인지 cell cherry-pick인지 검증**.\n")
    handoff_claims = [
        ("minibatch_partial", "CaseA", -7.41),
        ("sparse_rp", "CaseB", -7.11),
        ("minibatch", "CaseB", -7.17),
        ("hilbert", "CaseB", -5.21),
        ("pca1d", "CaseB", -4.75),
        ("reservoir", "CaseB", -4.68),
        ("minibatch_partial", "CaseB", -2.11),
        ("sparse_rp", "CaseA", -0.98),
        ("minibatch", "CaseA", -2.40),
    ]
    md.append("| Method | Mode | handoff claim | mean across cells | min cell | max cell | best-cell | "
              "is method-mean? | is cherry-pick? |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for method, mode, claim in handoff_claims:
        sub = df_finite[(df_finite["method"] == method) & (df_finite["mode"] == mode)]
        if len(sub) == 0:
            md.append(f"| {method} | {mode} | {claim:+.2f}% | (no data) | - | - | - | - | - |")
            continue
        m_mean = sub["delta_A"].mean()
        m_min = sub["delta_A"].min()
        m_max = sub["delta_A"].max()
        # find cell with closest match to claim
        sub_sorted = sub.assign(diff=lambda d: np.abs(d["delta_A"] - claim))
        best_match = sub_sorted.loc[sub_sorted["diff"].idxmin()]
        is_mean = abs(claim - m_mean) < 1.0
        is_cherry = abs(claim - m_min) < 1.0  # claim == best (minimum) cell
        md.append(f"| {method} | {mode} | {claim:+.2f}% | {m_mean:+.2f}% | "
                  f"{m_min:+.2f}% | {m_max:+.2f}% | "
                  f"{best_match['cell']} ({best_match['delta_A']:+.2f}%) | "
                  f"{'**YES**' if is_mean else 'NO'} | "
                  f"{'**YES**' if is_cherry else 'NO'} |")
    md.append("")
    md.append("**판정**:")
    md.append("- handoff §1.4 표가 method-mean 아닐 경우 → narrative 정정 필요 (best-cell cherry-pick).")
    md.append("- 정확한 cell 평균을 표기해야 'method outperform' claim 정당화 가능.")
    md.append("")

    # === 3. paper 1.69 비교 시 A4-sel 포함 효과 ===
    md.append("## 3. paper Fig 12 1.69 비교 — A4-sel inflate 효과\n")
    b1_files = sorted(DATA.glob("*_B1.json"))
    fig12_qe = []
    fig13_qe = []
    md.append("| Cell | qe_trim | 영역 |")
    md.append("|---|---|---|")
    for f in b1_files:
        d = json.load(open(f))
        cell = d["cell"]
        qe = d["avg_q_error_trimmed"]
        if cell == "A4-sel":
            region = "Fig 13 (sel=0.001, q_error inherently 큼)"
            fig13_qe.append(qe)
        else:
            region = "Fig 12 (정상 비교)"
            fig12_qe.append(qe)
        md.append(f"| {cell} | {qe:.4f} | {region} |")
    md.append("")
    avg_all = np.mean(fig12_qe + fig13_qe)
    avg_f12_only = np.mean(fig12_qe) if fig12_qe else 0
    paper_diff_all = (avg_all - 1.69) / 1.69 * 100
    paper_diff_f12 = (avg_f12_only - 1.69) / 1.69 * 100
    md.append(f"- 9 cells 모두 평균: {avg_all:.4f} (paper 1.69 vs **{paper_diff_all:+.1f}%**) — 메인 REPORT.md 표기")
    md.append(f"- Fig 12 영역 8 cells만 평균: {avg_f12_only:.4f} (paper 1.69 vs **{paper_diff_f12:+.1f}%**)")
    md.append(f"- A4-sel 1 cell 평균: {fig13_qe[0]:.4f} (Fig 13 영역, paper 비교 부적절)\n")
    md.append("**판정**:")
    md.append(f"- 메인 REPORT.md '+25.5%' 격차는 A4-sel inflate 효과로 부풀려짐.")
    md.append(f"- 정확한 paper Fig 12 비교: **Fig 12 영역만 = {paper_diff_f12:+.1f}%** ({len(fig12_qe)} cells).")
    md.append(f"- A4-sel은 별도로 paper Fig 13 (sel=0.001) 영역 분리 표기.")
    md.append("")

    # === 4. method별 outperform consistency (variance vs mean 함께) ===
    md.append("## 4. Method별 outperform consistency (mean Δ% + per-cell variance)\n")
    md.append("**우려**: handoff/REPORT가 'method X -7%'로 쓰면 cell variance 가려짐.\n")
    md.append("### 4.1 CaseA per-method\n")
    df_a = df_finite[df_finite["mode"] == "CaseA"]
    summary_a = df_a.groupby("method")["delta_A"].agg(["count", "mean", "std", "min", "max", "median"]).round(2)
    summary_a = summary_a.sort_values("mean")
    md.append("| Method | n cells | mean Δ% | std | min | max | median | spread (max-min) |")
    md.append("|---|---|---|---|---|---|---|---|")
    for m, r in summary_a.iterrows():
        spread = r["max"] - r["min"]
        md.append(f"| {m} | {int(r['count'])} | {r['mean']:+.2f}% | {r['std']:.2f} | "
                  f"{r['min']:+.2f}% | {r['max']:+.2f}% | {r['median']:+.2f}% | {spread:.1f} |")
    md.append("")

    md.append("### 4.2 CaseB per-method\n")
    df_b = df_finite[df_finite["mode"] == "CaseB"]
    summary_b = df_b.groupby("method")["delta_A"].agg(["count", "mean", "std", "min", "max", "median"]).round(2)
    summary_b = summary_b.sort_values("mean")
    md.append("| Method | n cells | mean Δ% | std | min | max | median | spread |")
    md.append("|---|---|---|---|---|---|---|---|")
    for m, r in summary_b.iterrows():
        spread = r["max"] - r["min"]
        md.append(f"| {m} | {int(r['count'])} | {r['mean']:+.2f}% | {r['std']:.2f} | "
                  f"{r['min']:+.2f}% | {r['max']:+.2f}% | {r['median']:+.2f}% | {spread:.1f} |")
    md.append("")

    # === 5. paradigm rollup ===
    md.append("## 5. Paradigm-level outperform aggregation\n")
    md.append("**RQ3 framework**: 5 paradigm × 11+ method.\n")
    for mode in ["CaseA", "CaseB"]:
        df_m = df_finite[df_finite["mode"] == mode]
        if len(df_m) == 0:
            continue
        md.append(f"### 5.{1 if mode=='CaseA' else 2} {mode}\n")
        rollup = df_m.groupby("paradigm")["delta_A"].agg(["count", "mean", "std", "min", "max"]).round(2)
        rollup = rollup.sort_values("mean")
        md.append("| Paradigm | n | mean Δ% | std | min | max |")
        md.append("|---|---|---|---|---|---|")
        for p, r in rollup.iterrows():
            md.append(f"| {p} | {int(r['count'])} | {r['mean']:+.2f}% | {r['std']:.2f} | "
                      f"{r['min']:+.2f}% | {r['max']:+.2f}% |")
        md.append("")

    # === 6. cell-level outlier impact ===
    md.append("## 6. Cell-level outlier impact (cell 별 method 평균)\n")
    md.append("**우려**: 특정 cell이 method 평균을 dominate.\n")
    for mode in ["CaseA", "CaseB"]:
        df_m = df_finite[df_finite["mode"] == mode]
        if len(df_m) == 0:
            continue
        md.append(f"### 6.{1 if mode=='CaseA' else 2} {mode}\n")
        cell_summary = df_m.groupby("cell")["delta_A"].agg(["count", "mean", "std", "min", "max"]).round(2)
        md.append("| Cell | n methods | mean Δ% | std | min | max |")
        md.append("|---|---|---|---|---|---|")
        for c, r in cell_summary.iterrows():
            md.append(f"| {c} | {int(r['count'])} | {r['mean']:+.2f}% | {r['std']:.2f} | "
                      f"{r['min']:+.2f}% | {r['max']:+.2f}% |")
        md.append("")

    # === 7. inf/nan 비율 cherry-pick ===
    md.append("## 7. inf/nan handling — cell × method 별\n")
    md.append("**우려**: inf 결과가 많은 cell을 narrative에서 silently 제외하면 selection bias.\n")
    inf_rows = []
    for f in DATA.glob("*.json"):
        d = json.load(open(f))
        if "trial_results" not in d:
            continue  # A3-TPCDS_ECQO.json 등 다른 schema
        n_inf = sum(1 for t in d["trial_results"]
                    if not np.isfinite(t["avg_q_error_finite"]))
        if n_inf > 0:
            inf_rows.append({"file": f.stem, "cell": d.get("cell"),
                             "mode": d.get("mode"), "method": d.get("method"),
                             "n_inf": n_inf, "n_total": len(d["trial_results"])})
    df_inf = pd.DataFrame(inf_rows)
    if len(df_inf) > 0:
        md.append(f"- inf 발생 measurements: **{len(df_inf)}** files (총 {df_inf['n_inf'].sum()} trials)")
        md.append("| File | Cell | Mode | Method | n_inf / n_total |")
        md.append("|---|---|---|---|---|")
        for _, r in df_inf.sort_values("n_inf", ascending=False).head(20).iterrows():
            md.append(f"| {r['file']} | {r['cell']} | {r['mode']} | {r['method']} | "
                      f"{r['n_inf']}/{r['n_total']} |")
    else:
        md.append("- **inf 발생 0건** — pairing 완전.")
    md.append("")

    # === 종합 ===
    md.append("## 종합 판정\n")

    # Compute key metrics
    handoff_mean_match = sum(
        1 for method, mode, claim in handoff_claims
        if (sub := df_finite[(df_finite["method"] == method) & (df_finite["mode"] == mode)]).shape[0] > 0
        and abs(claim - sub["delta_A"].mean()) < 1.0
    )
    n_handoff_total = sum(
        1 for method, mode, _ in handoff_claims
        if df_finite[(df_finite["method"] == method) & (df_finite["mode"] == mode)].shape[0] > 0
    )
    md.append(f"- **handoff §1.4 표 정합성**: {handoff_mean_match}/{n_handoff_total} method-mean 일치")
    if handoff_mean_match >= n_handoff_total - 2:
        md.append(f"  → **PASS** (대부분 method-mean으로 표기됨)")
    else:
        md.append(f"  → **WARN** (best-cell cherry-pick 가능성, 정확한 mean 표기 필요)")

    md.append(f"- **paper 1.69 비교**: A4-sel 포함 = {paper_diff_all:+.1f}%, "
              f"Fig 12 영역만 = {paper_diff_f12:+.1f}%")
    md.append(f"  → 메인 REPORT.md '+25.5%' 표현 정정 권장: **'Fig 12 영역만 {paper_diff_f12:+.1f}%, "
              f"A4-sel은 Fig 13 영역 (sel=0.001 inherently 큼)' 분리 표기**.")

    md.append(f"- **method별 spread**: 일부 method spread 넓음 → cell variance narrative에 같이 표기 권장")
    top_spread_method = summary_a["max"].idxmax()
    md.append(f"  - CaseA max spread method: **{top_spread_method}** "
              f"(max={summary_a.loc[top_spread_method, 'max']:+.1f}%, "
              f"min={summary_a.loc[top_spread_method, 'min']:+.1f}%)")

    md.append(f"- **paradigm-level**: P3-Streaming / P4-DimReduction 우세 영역 명시 권장")

    OUT.write_text("\n".join(md))
    print(f"Layer 4 audit → {OUT}")
    print(f"  handoff claim mean-match: {handoff_mean_match}/{n_handoff_total}")
    print(f"  paper 1.69 diff: all={paper_diff_all:+.1f}%, fig12-only={paper_diff_f12:+.1f}%")


if __name__ == "__main__":
    audit()
