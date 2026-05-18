#!/usr/bin/env python3
"""
build_v13_summary.py — REPORT v13 / narrative v8 작성용 수치 요약 (task I, 5/17 세션)

aggregated_v13_full.parquet + paired_delta_v13.parquet 로부터 REPORT v13·narrative v8
에 들어갈 모든 수치를 계산해 출력한다. 모든 수치는 두 parquet 직접 재계산값이며,
이전 텍스트 수치를 신뢰하지 않는다 (handoff v35 §9 환각 회피 룰).

3-way matched: B1 대조군 / CaseA 실험군(완전 대체) / CaseB 실험군(결합).
비교 3종: CaseA_vs_B1 / CaseB_vs_B1 / CaseA_vs_CaseB.
delta_pct_mean < 0 = exp(앞) mode 가 더 정확.

usage: python3 build_v13_summary.py
출력: stdout + _internal/cache/rq3/v13_summary.md
"""
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
RQ3 = REPO_ROOT / "_internal" / "cache" / "rq3"
AGG = RQ3 / "aggregated_v13_full.parquet"
PAIRED = RQ3 / "paired_delta_v13.parquet"
OUT_MD = RQ3 / "v13_summary.md"

CLIFF_LARGE = 0.474
USE_16 = ["minibatch_partial", "gmm", "faiss_ivf", "hilbert_real", "zorder_morton",
          "skilling_hilbert", "chao_weighted", "sparse_rp", "pca1d", "rsvd",
          "ica_fastica", "cum_sqrtf", "lavallee_hidiroglou", "rabitq_strat",
          "mhist2", "hyperloglog"]
# K granularity sweep cell — 6 cell × sel=0.01 × 16 method × K{10,20,30}
KGRAN_CELLS = ["A5-scale-sf1", "A5-scale-sf10", "A2-Fig7", "A2-Fig9",
               "A1-DEEP", "A5-scale-sf100"]

_LINES = []


def out(s=""):
    print(s)
    _LINES.append(s)


def stats(sub: pd.DataFrame) -> dict:
    """paired 부분집합 → better/sig/effect-size 집계. delta<0 = exp 우위."""
    n = len(sub)
    if n == 0:
        return dict(n=0, better=0, better_pct=0.0, sig=0, sig_pct=0.0,
                    cl=0, cl_pct=0.0, mean=float("nan"), median=float("nan"),
                    mean_noout=float("nan"))
    better = int((sub["delta_pct_mean"] < 0).sum())
    sig = int(((sub["delta_pct_mean"] < 0) & (sub["p_adj_bh_greater"] < 0.05)).sum())
    cl = int((sub["cliffs_delta"] >= CLIFF_LARGE).sum())
    noout = sub[sub["delta_pct_mean"].abs() < 100]
    return dict(n=n, better=better, better_pct=100 * better / n,
                sig=sig, sig_pct=100 * sig / n, cl=cl, cl_pct=100 * cl / n,
                mean=float(sub["delta_pct_mean"].mean()),
                median=float(sub["delta_pct_mean"].median()),
                mean_noout=float(noout["delta_pct_mean"].mean()) if len(noout) else float("nan"))


def row(label, s, extra=""):
    return (f"| {label} | {s['n']} | {s['better']} | {s['better_pct']:.1f}% | "
            f"{s['sig_pct']:.1f}% | {s['cl_pct']:.1f}% | {s['mean']:+.2f}% | "
            f"{s['median']:+.2f}%{extra} |")


def main():
    agg = pd.read_parquet(AGG)
    dfp = pd.read_parquet(PAIRED)

    out("# REPORT v13 / narrative v8 수치 요약 — 3-way matched 캠페인")
    out(f"\n_생성_: {pd.Timestamp.now():%Y-%m-%d %H:%M} · "
        f"출처 aggregated_v13_full.parquet ({len(agg)} row) + "
        f"paired_delta_v13.parquet ({len(dfp)} row)\n")

    # ============ 1. portfolio ============
    out("## 1. 측정 portfolio")
    n_meas = agg["json_id"].nunique()
    out(f"- 3-way 측정: **{n_meas}건** (각 측정 = B1·CaseA·CaseB matched). row {len(agg)} = {n_meas}×3")
    out(f"- cell {agg['cell'].nunique()} · method {agg['method'].nunique()} · "
        f"sf {sorted(agg['sf'].dropna().unique().tolist())} · "
        f"K {sorted(agg['K'].dropna().unique().tolist())} · "
        f"sel {sorted(agg['sel'].dropna().unique().tolist())}")
    for ax in ["sf", "K", "sel", "single_multi"]:
        cnt = agg[agg["mode"] == "B1"].groupby(ax).size().to_dict()
        out(f"- by {ax}: {cnt}")
    out("\n### 1.1 mode 별 qe_trim·final_size (descriptive)")
    out("| mode | n | qe_trim mean | qe_trim median | final_size mean |")
    out("|---|--:|--:|--:|--:|")
    for m in ["B1", "CaseA", "CaseB"]:
        g = agg[agg["mode"] == m]
        out(f"| {m} | {len(g)} | {g['qe_trim'].mean():.4f} | "
            f"{g['qe_trim'].median():.4f} | {g['final_size'].mean():.0f} |")

    # ============ 2. B1 K=10 결함 검증 ============
    out("\n## 2. B1 qe_trim by K — v12 K=10 결함 해소 검증")
    out("> v12: K=10 B1 qe_trim 2.2~3.3 손상 (2단계 STRATA_K 캐시 inf 폭증). "
        "v13 B1 = 1단계 → 검증.")
    out("| K | n | B1 qe_trim mean | min | max | n_inf_total mean (10 trial 합) |")
    out("|---|--:|--:|--:|--:|--:|")
    for K in sorted(agg["K"].dropna().unique()):
        b = agg[(agg["mode"] == "B1") & (agg["K"] == K)]
        out(f"| {int(K)} | {len(b)} | {b['qe_trim'].mean():.4f} | "
            f"{b['qe_trim'].min():.4f} | {b['qe_trim'].max():.4f} | "
            f"{b['n_inf_total'].mean():.1f} |")

    # ============ 3. 3-way headline ============
    out("\n## 3. 3-way paired Δ% headline")
    out("> delta = (exp_qe − base_qe)/base_qe × 100, trial-paired 10 trial. 음수 = exp 우위.")
    out("| 비교 | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |")
    out("|---|--:|--:|--:|--:|--:|--:|--:|")
    for comp in ["CaseA_vs_B1", "CaseB_vs_B1", "CaseA_vs_CaseB"]:
        s = stats(dfp[dfp["comparison"] == comp])
        out(row(comp, s))
    for comp in ["CaseA_vs_B1", "CaseB_vs_B1", "CaseA_vs_CaseB"]:
        sub = dfp[dfp["comparison"] == comp]
        out(f"- {comp}: Δ% 범위 [{sub['delta_pct_mean'].min():+.2f}%, "
            f"{sub['delta_pct_mean'].max():+.2f}%], outlier 제외 mean "
            f"{stats(sub)['mean_noout']:+.2f}%")

    # ============ 4. CaseB_vs_B1 상세 ============
    cbb = dfp[dfp["comparison"] == "CaseB_vs_B1"]
    out("\n## 4. CaseB_vs_B1 상세 (결합 실험군 vs 대조군 — REPORT 핵심)")
    out("\n### 4.1 selectivity 별")
    out("| sel | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |")
    out("|---|--:|--:|--:|--:|--:|--:|--:|")
    for sel in sorted(cbb["sel"].dropna().unique()):
        out(row(f"sel={sel:g}", stats(cbb[cbb["sel"] == sel])))
    out("\n### 4.2 single / multi / concat 별")
    out("| 유형 | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |")
    out("|---|--:|--:|--:|--:|--:|--:|--:|")
    for sm in ["single", "multi", "concat"]:
        s = stats(cbb[cbb["single_multi"] == sm])
        if s["n"]:
            out(row(sm, s))
    out("\n### 4.3 single × sel 교차")
    out("| 유형 | sel | n | better% | mean Δ% | median Δ% |")
    out("|---|---|--:|--:|--:|--:|")
    for sm in ["single", "concat"]:
        for sel in sorted(cbb["sel"].dropna().unique()):
            s = stats(cbb[(cbb["single_multi"] == sm) & (cbb["sel"] == sel)])
            if s["n"]:
                out(f"| {sm} | {sel:g} | {s['n']} | {s['better_pct']:.1f}% | "
                    f"{s['mean']:+.2f}% | {s['median']:+.2f}% |")
    out("\n### 4.4 method 별 (mean Δ% 오름차순)")
    out("| method | paradigm | n | better% | 유의% | δlarge% | mean Δ% | mean(outlier제외) | median Δ% |")
    out("|---|---|--:|--:|--:|--:|--:|--:|--:|")
    mrows = []
    for m in cbb["method"].unique():
        s = stats(cbb[cbb["method"] == m])
        para = cbb[cbb["method"] == m]["paradigm"].iloc[0]
        mrows.append((s["mean"], m, para, s))
    for mean, m, para, s in sorted(mrows):
        out(f"| {m} | {para} | {s['n']} | {s['better_pct']:.1f}% | {s['sig_pct']:.1f}% | "
            f"{s['cl_pct']:.1f}% | {s['mean']:+.2f}% | {s['mean_noout']:+.2f}% | {s['median']:+.2f}% |")
    out("\n### 4.5 paradigm 별")
    out("| paradigm | n_method | n | better% | mean Δ% | median Δ% |")
    out("|---|--:|--:|--:|--:|--:|")
    prows = []
    for para in cbb["paradigm"].unique():
        g = cbb[cbb["paradigm"] == para]
        s = stats(g)
        prows.append((s["mean"], para, g["method"].nunique(), s))
    for mean, para, nm, s in sorted(prows):
        out(f"| {para} | {nm} | {s['n']} | {s['better_pct']:.1f}% | "
            f"{s['mean']:+.2f}% | {s['median']:+.2f}% |")
    out("\n### 4.6 cell 별 (mean Δ% 오름차순)")
    out("| cell | dataset | 유형 | n | better% | mean Δ% | median Δ% |")
    out("|---|---|---|--:|--:|--:|--:|")
    crows = []
    for cell in cbb["cell"].unique():
        g = cbb[cbb["cell"] == cell]
        s = stats(g)
        crows.append((s["mean"], cell, g["dataset"].iloc[0], g["single_multi"].iloc[0], s))
    for mean, cell, ds, sm, s in sorted(crows):
        out(f"| {cell} | {ds} | {sm} | {s['n']} | {s['better_pct']:.1f}% | "
            f"{s['mean']:+.2f}% | {s['median']:+.2f}% |")

    # ============ 5. K granularity (clean — 6 cell × sel0.01) ============
    out("\n## 5. K granularity — CaseB_vs_B1 (6 K-gran cell × sel=0.01, matched 3-way)")
    out("> v12 와 달리 v13 은 각 측정이 자체 B1(1단계) 보유 → K=10 도 깨끗한 비교.")
    kg = cbb[(cbb["cell"].isin(KGRAN_CELLS)) & (cbb["sel"] == 0.01)]
    out("| K | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |")
    out("|---|--:|--:|--:|--:|--:|--:|--:|")
    for K in sorted(kg["K"].dropna().unique()):
        out(row(f"K={int(K)}", stats(kg[kg["K"] == K])))
    out(f"- (K-gran subset cells: {', '.join(sorted(kg['cell'].unique()))})")

    # ============ 6. CaseA_vs_B1 (negative control) ============
    cab = dfp[dfp["comparison"] == "CaseA_vs_B1"]
    out("\n## 6. CaseA_vs_B1 — 완전 대체 실험군 (negative control)")
    out("\n### 6.1 selectivity 별")
    out("| sel | n | better% | 유의% | mean Δ% | median Δ% |")
    out("|---|--:|--:|--:|--:|--:|")
    for sel in sorted(cab["sel"].dropna().unique()):
        s = stats(cab[cab["sel"] == sel])
        out(f"| {sel:g} | {s['n']} | {s['better_pct']:.1f}% | {s['sig_pct']:.1f}% | "
            f"{s['mean']:+.2f}% | {s['median']:+.2f}% |")
    out("\n### 6.2 method 별 (mean Δ% 오름차순) — 완전 대체의 불안정성")
    out("| method | paradigm | n | better% | mean Δ% | mean(outlier제외) | median Δ% |")
    out("|---|---|--:|--:|--:|--:|--:|")
    marows = []
    for m in cab["method"].unique():
        s = stats(cab[cab["method"] == m])
        para = cab[cab["method"] == m]["paradigm"].iloc[0]
        marows.append((s["mean"], m, para, s))
    for mean, m, para, s in sorted(marows):
        out(f"| {m} | {para} | {s['n']} | {s['better_pct']:.1f}% | {s['mean']:+.2f}% | "
            f"{s['mean_noout']:+.2f}% | {s['median']:+.2f}% |")

    # ============ 7. CaseA_vs_CaseB ============
    cac = dfp[dfp["comparison"] == "CaseA_vs_CaseB"]
    out("\n## 7. CaseA_vs_CaseB — 완전 대체 vs 결합")
    s = stats(cac)
    out(f"- n={s['n']}, CaseA better(Δ%<0)={s['better']} ({s['better_pct']:.1f}%), "
        f"mean Δ%={s['mean']:+.2f}%, median={s['median']:+.2f}% "
        f"→ {'CaseB' if s['better_pct'] < 50 else 'CaseA'} 우위")

    # ============ 8. top winner/loser ============
    out("\n## 8. CaseB_vs_B1 Top winner / loser (개별 cell×method×sel×K)")
    out("\n### 8.1 Top 8 winner (smallest Δ%)")
    out("| cell | method | sel | K | Δ% | p_adj(BH,greater) | Cliff δ |")
    out("|---|---|--:|--:|--:|--:|--:|")
    for _, r in cbb.nsmallest(8, "delta_pct_mean").iterrows():
        out(f"| {r['cell']} | {r['method']} | {r['sel']:g} | {int(r['K'])} | "
            f"{r['delta_pct_mean']:+.2f}% | {r['p_adj_bh_greater']:.4f} | {r['cliffs_delta']:+.3f} |")
    out("\n### 8.2 Top 8 loser (largest Δ%)")
    out("| cell | method | sel | K | Δ% | p_adj(BH) | Cliff δ |")
    out("|---|---|--:|--:|--:|--:|--:|")
    for _, r in cbb.nlargest(8, "delta_pct_mean").iterrows():
        out(f"| {r['cell']} | {r['method']} | {r['sel']:g} | {int(r['K'])} | "
            f"{r['delta_pct_mean']:+.2f}% | {r['p_adj_bh']:.4f} | {r['cliffs_delta']:+.3f} |")

    OUT_MD.write_text("\n".join(_LINES) + "\n")
    print(f"\nwrote {OUT_MD}")


if __name__ == "__main__":
    main()
