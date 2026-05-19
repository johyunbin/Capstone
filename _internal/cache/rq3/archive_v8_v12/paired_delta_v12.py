#!/usr/bin/env python3
"""
paired_delta_v12.py — paired Δ% 분석 (B1 대조군 vs CaseB 실험군)

framing (박세은 5/15 20:49 — sample selection 영역만 contribution)
----------------------------------------------------------------
- B1     = 대조군: paper §V-B Bernoulli random + Adaptive Eq 1-6
- CaseB  = 실험군: 16 method stratification ensemble + Adaptive
           est_final = (est_b1 + est_method) / 2.0 (사용자 5/9 simple average)
- CaseA  = 폐기 (취급 안 함)

paired Δ% 정의
--------------
delta_pct = (CaseB_qe − B1_qe) / B1_qe × 100,  같은 cell·sel·K 기준
trial-paired (10 trial). 음수 = 실험군이 더 정확 (Q-error 작음).

pairing 규칙
-----------
CaseB (cell, sel, K) 는 B1 (cell, sel, K) 와 매칭.
같은 K 의 B1 이 없으면 K=default (paper K=20) B1 로 fallback —
paper exact 측정 의도: raw K-sweep CaseB 는 paper-default B1 대비 측정,
v6_caseB K30 B1 은 paper-default B1 byte-identical 재사용 확인 (provenance 분석 완료).

통계
----
- Wilcoxon signed-rank (two-sided + one-sided greater), exact (n≤25)
- BH-FDR (Benjamini-Hochberg) 보정
- Cliff's δ (POSITIVE = CaseB 우위), Hedges' g (NEGATIVE = CaseB 우위)
- analyze_paper_exact.py 의 paired_delta / bh_fdr / compute_* 재사용

usage
-----
  python3 paired_delta_v12.py
입력: _internal/cache/rq3/aggregated_v12_full.parquet
출력: _internal/cache/rq3/paired_delta_v12.parquet
      experiments/results/analysis/paired_delta_v12_요약.md
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "_internal" / "scripts"))

# analyze_paper_exact.py 의 검증된 통계 함수 재사용
from analyze_paper_exact import (  # noqa: E402
    paired_delta, bh_fdr, compute_hedges_g, compute_cliffs_delta,
)

IN_PARQUET = REPO_ROOT / "_internal" / "cache" / "rq3" / "aggregated_v12_full.parquet"
OUT_PARQUET = REPO_ROOT / "_internal" / "cache" / "rq3" / "paired_delta_v12.parquet"
OUT_MD = REPO_ROOT / "experiments" / "results" / "analysis" / "paired_delta_v12_요약.md"

USE_16_METHODS = [
    "minibatch_partial", "gmm", "faiss_ivf", "hilbert_real",
    "zorder_morton", "skilling_hilbert", "chao_weighted", "sparse_rp",
    "pca1d", "rsvd", "ica_fastica", "cum_sqrtf",
    "lavallee_hidiroglou", "rabitq_strat", "mhist2", "hyperloglog",
]

CLIFF_LARGE = 0.474   # large effect threshold
CLIFF_MED = 0.330


def k_norm(k):
    """K null = paper default 20."""
    return 20 if (k is None or pd.isna(k)) else int(k)


def trial_qe(row) -> list:
    return json.loads(row["trial_qe_list"])


def build_b1_lookup(df_b1: pd.DataFrame) -> dict:
    """B1 trial qe lookup. key = (cell, sel, K_norm)."""
    lut = {}
    for _, r in df_b1.iterrows():
        key = (r["cell"], r["sel"], k_norm(r["K"]))
        lut[key] = trial_qe(r)
    return lut


def get_b1_trials(lut: dict, cell, sel, K) -> tuple:
    """CaseB (cell,sel,K) 에 매칭되는 B1 trial qe.
    exact-K 없으면 K=20 (paper default) fallback.
    returns (trials, pairing_mode)."""
    kn = k_norm(K)
    if (cell, sel, kn) in lut:
        return lut[(cell, sel, kn)], "exact"
    if (cell, sel, 20) in lut:
        return lut[(cell, sel, 20)], "fallback_K20"
    return None, "missing"


def main():
    df = pd.read_parquet(IN_PARQUET)
    df_b1 = df[df["mode"] == "B1"].copy()
    df_cb = df[df["mode"] == "CaseB"].copy()

    b1_lut = build_b1_lookup(df_b1)

    rows = []
    n_missing_b1 = 0
    for _, r in df_cb.iterrows():
        cell, sel, K = r["cell"], r["sel"], r["K"]
        method = r["method"]
        b1_trials, pmode = get_b1_trials(b1_lut, cell, sel, K)
        if b1_trials is None:
            n_missing_b1 += 1
            continue
        cb_trials = trial_qe(r)
        d = paired_delta(b1_trials, cb_trials)
        rows.append({
            "cell": cell,
            "dataset": r["dataset"],
            "single_multi": r["single_multi"],
            "sf": r["sf"],
            "dim": r["dim"],
            "sel": sel,
            "K": K,
            "K_norm": k_norm(K),
            "method": method,
            "paradigm": r["paradigm"],
            "pairing": pmode,
            "n_trials": d["n_trials"],
            "b1_qe_mean": d["b1_mean"],
            "caseb_qe_mean": d["casea_mean"],   # paired_delta historical key
            "delta_pct_mean": d["delta_pct_mean"],
            "delta_pct_median": d["delta_pct_median"],
            "wilcoxon_p": d["wilcoxon_p"],
            "wilcoxon_p_greater": d["wilcoxon_p_greater"],
            "hedges_g": d["hedges_g"],
            "cliffs_delta": d["cliffs_delta"],
            "stage_source": r["stage_source"],
            "file_path": r["file_path"],
        })

    dfp = pd.DataFrame(rows)
    # BH-FDR 보정 (전체 비교 pool 기준)
    dfp["p_adj_bh"] = bh_fdr(dfp["wilcoxon_p"].tolist())
    dfp["p_adj_bh_greater"] = bh_fdr(dfp["wilcoxon_p_greater"].tolist())
    dfp = dfp.sort_values(["cell", "sel", "K_norm", "delta_pct_mean"]).reset_index(drop=True)

    dfp.to_parquet(OUT_PARQUET, index=False)
    print(f"wrote {OUT_PARQUET}  ({len(dfp)} paired comparisons)")
    if n_missing_b1:
        print(f"  warning: {n_missing_b1} CaseB rows dropped (no matching B1)")

    write_md(df, dfp)


# ============================================================
# 요약 md
# ============================================================

def _better_stats(sub: pd.DataFrame) -> dict:
    """better 비율 + 유의 outperform 집계."""
    n = len(sub)
    if n == 0:
        return dict(n=0, better=0, better_pct=0.0, sig=0, sig_pct=0.0,
                    mean_d=float("nan"), median_d=float("nan"),
                    cliff_large=0, cliff_large_pct=0.0)
    better = int((sub["delta_pct_mean"] < 0).sum())
    sig = int(((sub["delta_pct_mean"] < 0) & (sub["p_adj_bh_greater"] < 0.05)).sum())
    cliff_large = int((sub["cliffs_delta"] >= CLIFF_LARGE).sum())
    return dict(
        n=n,
        better=better, better_pct=100 * better / n,
        sig=sig, sig_pct=100 * sig / n,
        mean_d=sub["delta_pct_mean"].mean(),
        median_d=sub["delta_pct_mean"].median(),
        cliff_large=cliff_large, cliff_large_pct=100 * cliff_large / n,
    )


def write_md(df: pd.DataFrame, dfp: pd.DataFrame):
    L = []
    L.append("# Paired Δ% 분석 v12 — B1 대조군 vs CaseB 실험군\n")
    L.append(f"_생성_: {pd.Timestamp.now():%Y-%m-%d %H:%M}\n")
    L.append("_framing_: B1 = Bernoulli random + Adaptive Eq 1-6 (대조군), "
             "CaseB = 16 method stratification ensemble + Adaptive (실험군). "
             "CaseA 폐기.\n")
    L.append("paired Δ% = (CaseB_qe − B1_qe) / B1_qe × 100, 같은 cell·sel·K, "
             "trial-paired 10 trial. **음수 = 실험군이 더 정확**.\n")
    L.append("---\n")

    # --- 0. 데이터 규모 ---
    n_cb = len(df[df["mode"] == "CaseB"])
    n_b1 = len(df[df["mode"] == "B1"])
    L.append("## 0. 통합 데이터 규모\n")
    L.append(f"- 통합 측정 file (16 method 필터 + dedup 후): **{len(df)}** "
             f"(B1 {n_b1} + CaseB {n_cb})")
    L.append(f"- paired 비교 (CaseB × B1 매칭): **{len(dfp)}**건")
    L.append(f"- cell {df['cell'].nunique()}개, method 16개, sel 3종 (0.001/0.01/0.10), "
             f"K 3종 (10/20-default/30)")
    pairing_cnt = dfp.groupby("pairing").size().to_dict()
    L.append(f"- B1 pairing: {pairing_cnt} (fallback_K20 = K10/K30 CaseB 가 "
             "paper-default B1 과 매칭된 케이스)\n")

    # --- 1. 전체 paired Δ% ---
    overall = _better_stats(dfp)
    L.append("## 1. 전체 paired Δ% 핵심 수치\n")
    L.append(f"- **전체 {overall['n']}건 中 CaseB better (Δ%<0): "
             f"{overall['better']}건 ({overall['better_pct']:.1f}%)**")
    L.append(f"- one-sided greater p_adj(BH-FDR)<0.05 유의 outperform: "
             f"{overall['sig']}건 ({overall['sig_pct']:.1f}%)")
    L.append(f"- Cliff's δ large (≥{CLIFF_LARGE}) better: "
             f"{overall['cliff_large']}건 ({overall['cliff_large_pct']:.1f}%)")
    L.append(f"- 전체 mean Δ%: **{overall['mean_d']:+.2f}%** / "
             f"median Δ%: **{overall['median_d']:+.2f}%**\n")

    # --- 2. sel 별 ---
    L.append("## 2. selectivity 효과 (sel 0.001 / 0.01 / 0.10)\n")
    L.append("| sel | n | better | better% | 유의 outperform% | mean Δ% | median Δ% | δ large% |")
    L.append("|---|--:|--:|--:|--:|--:|--:|--:|")
    for sel in sorted(dfp["sel"].dropna().unique()):
        s = _better_stats(dfp[dfp["sel"] == sel])
        L.append(f"| {sel} | {s['n']} | {s['better']} | {s['better_pct']:.1f}% | "
                 f"{s['sig_pct']:.1f}% | {s['mean_d']:+.2f}% | {s['median_d']:+.2f}% | "
                 f"{s['cliff_large_pct']:.1f}% |")
    L.append("")

    # --- 3. single vs multi vs concat ---
    L.append("## 3. single vs multi(cross-table) vs concat\n")
    L.append("| 유형 | n | better | better% | 유의 outperform% | mean Δ% | median Δ% |")
    L.append("|---|--:|--:|--:|--:|--:|--:|")
    for sm in ["single", "multi", "concat"]:
        s = _better_stats(dfp[dfp["single_multi"] == sm])
        if s["n"] == 0:
            continue
        L.append(f"| {sm} | {s['n']} | {s['better']} | {s['better_pct']:.1f}% | "
                 f"{s['sig_pct']:.1f}% | {s['mean_d']:+.2f}% | {s['median_d']:+.2f}% |")
    L.append("")
    L.append("### 3.1 single vs concat — sel 별 교차\n")
    L.append("| 유형 | sel | n | better% | mean Δ% | median Δ% |")
    L.append("|---|---|--:|--:|--:|--:|")
    for sm in ["single", "concat"]:
        for sel in sorted(dfp["sel"].dropna().unique()):
            s = _better_stats(dfp[(dfp["single_multi"] == sm) & (dfp["sel"] == sel)])
            if s["n"] == 0:
                continue
            L.append(f"| {sm} | {sel} | {s['n']} | {s['better_pct']:.1f}% | "
                     f"{s['mean_d']:+.2f}% | {s['median_d']:+.2f}% |")
    L.append("")

    # --- 4. cell × method 매트릭스 (mean Δ%) ---
    L.append("## 4. cell × method paired Δ% 매트릭스 (mean Δ%, 전 sel·K aggregate)\n")
    L.append("> 셀 값 = 해당 cell × method 의 모든 (sel,K) 평균 Δ%. 음수 = CaseB 우위.\n")
    piv = dfp.pivot_table(index="cell", columns="method",
                          values="delta_pct_mean", aggfunc="mean")
    piv = piv.reindex(columns=[m for m in USE_16_METHODS if m in piv.columns])
    hdr = "| cell | " + " | ".join(piv.columns) + " | row mean |"
    sep = "|---|" + "|".join(["--:"] * (len(piv.columns) + 1)) + "|"
    L.append(hdr)
    L.append(sep)
    for cell, r in piv.iterrows():
        vals = " | ".join(f"{v:+.1f}" if pd.notna(v) else "·" for v in r)
        L.append(f"| {cell} | {vals} | {r.mean():+.2f} |")
    col_mean = piv.mean(axis=0)
    L.append(f"| **col mean** | " +
             " | ".join(f"**{v:+.1f}**" for v in col_mean) +
             f" | **{piv.values[~np.isnan(piv.values)].mean():+.2f}** |")
    L.append("")

    # --- 4.1 method 별 rollup ---
    L.append("### 4.1 method 별 rollup (전 cell·sel·K)\n")
    L.append("| method | paradigm | n | better% | mean Δ% | median Δ% | δ large% |")
    L.append("|---|---|--:|--:|--:|--:|--:|")
    mg = (dfp.groupby("method")
          .apply(lambda g: pd.Series(_better_stats(g)), include_groups=False)
          .reset_index())
    para = dfp.drop_duplicates("method").set_index("method")["paradigm"].to_dict()
    mg = mg.sort_values("mean_d")
    for _, r in mg.iterrows():
        L.append(f"| {r['method']} | {para.get(r['method'],'?')} | {int(r['n'])} | "
                 f"{r['better_pct']:.1f}% | {r['mean_d']:+.2f}% | "
                 f"{r['median_d']:+.2f}% | {r['cliff_large_pct']:.1f}% |")
    L.append("")

    # --- 4.2 paradigm 별 rollup ---
    L.append("### 4.2 paradigm 별 rollup\n")
    L.append("| paradigm | n_method | n_obs | better% | mean Δ% | median Δ% |")
    L.append("|---|--:|--:|--:|--:|--:|")
    for para_id, g in dfp.groupby("paradigm"):
        s = _better_stats(g)
        L.append(f"| {para_id} | {g['method'].nunique()} | {s['n']} | "
                 f"{s['better_pct']:.1f}% | {s['mean_d']:+.2f}% | {s['median_d']:+.2f}% |")
    L.append("")

    # --- 5. K granularity ---
    L.append("## 5. K granularity 효과 (K=10 / 20-default / 30)\n")
    L.append("| K | n | better% | 유의 outperform% | mean Δ% | median Δ% |")
    L.append("|---|--:|--:|--:|--:|--:|")
    for kn in sorted(dfp["K_norm"].unique()):
        s = _better_stats(dfp[dfp["K_norm"] == kn])
        klabel = f"{kn}" + (" (default)" if kn == 20 else "")
        L.append(f"| {klabel} | {s['n']} | {s['better_pct']:.1f}% | "
                 f"{s['sig_pct']:.1f}% | {s['mean_d']:+.2f}% | {s['median_d']:+.2f}% |")
    L.append("")

    # --- 6. cell 별 요약 ---
    L.append("## 6. cell 별 요약\n")
    L.append("| cell | dataset | 유형 | n | better% | mean Δ% | best method (Δ%) |")
    L.append("|---|---|---|--:|--:|--:|---|")
    for cell, g in dfp.groupby("cell"):
        s = _better_stats(g)
        best = g.nsmallest(1, "delta_pct_mean")
        bm = best.iloc[0]
        ds = g["dataset"].iloc[0]
        sm = g["single_multi"].iloc[0]
        L.append(f"| {cell} | {ds} | {sm} | {s['n']} | {s['better_pct']:.1f}% | "
                 f"{s['mean_d']:+.2f}% | {bm['method']} ({bm['delta_pct_mean']:+.2f}%) |")
    L.append("")

    # --- 7. 빠진 조합 ---
    L.append("## 7. 빠진 조합 리포트\n")
    L.append(report_missing(df))
    L.append("")

    # --- 8. top winners / losers ---
    L.append("## 8. Top winner / loser (개별 cell×method×sel×K)\n")
    L.append("### 8.1 Top 10 CaseB winner (smallest Δ%)\n")
    L.append("| cell | method | sel | K | Δ% | p_adj(BH) | Cliff δ | Hedges g |")
    L.append("|---|---|---|--:|--:|--:|--:|--:|")
    for _, r in dfp.nsmallest(10, "delta_pct_mean").iterrows():
        L.append(f"| {r['cell']} | {r['method']} | {r['sel']} | {r['K_norm']} | "
                 f"{r['delta_pct_mean']:+.2f}% | {r['p_adj_bh_greater']:.4f} | "
                 f"{r['cliffs_delta']:+.3f} | {r['hedges_g']:+.3f} |")
    L.append("\n### 8.2 Top 10 CaseB loser (largest Δ%)\n")
    L.append("| cell | method | sel | K | Δ% | p_adj(BH) | Cliff δ | Hedges g |")
    L.append("|---|---|---|--:|--:|--:|--:|--:|")
    for _, r in dfp.nlargest(10, "delta_pct_mean").iterrows():
        L.append(f"| {r['cell']} | {r['method']} | {r['sel']} | {r['K_norm']} | "
                 f"{r['delta_pct_mean']:+.2f}% | {r['p_adj_bh']:.4f} | "
                 f"{r['cliffs_delta']:+.3f} | {r['hedges_g']:+.3f} |")
    L.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L))
    print(f"wrote {OUT_MD}")


def report_missing(df: pd.DataFrame) -> str:
    """각 (cell, sel, K) 가 B1 1개 + CaseB 16 method 갖췄는지 검증."""
    lines = []
    df = df.copy()
    df["K_norm"] = df["K"].map(k_norm)
    m16 = set(USE_16_METHODS)
    missing = []
    for (cell, sel, kn), g in df.groupby(["cell", "sel", "K_norm"]):
        nb1 = len(g[g["mode"] == "B1"])
        cb = g[g["mode"] == "CaseB"]
        present = set(cb["method"])
        miss_m = sorted(m16 - present) if len(present) else []
        if nb1 != 1 or (len(present) and len(present) != 16):
            missing.append({
                "cell": cell, "sel": sel, "K": kn,
                "b1": nb1, "caseb_n": len(present),
                "miss": miss_m,
            })
    n_combo = df.groupby(["cell", "sel", "K_norm"]).ngroups
    lines.append(f"전체 (cell, sel, K) 조합 {n_combo}개 中 불완전 {len(missing)}개:\n")
    if not missing:
        lines.append("(모든 조합 B1 1개 + CaseB 16 method 완비)")
    else:
        lines.append("| cell | sel | K | B1 | CaseB method수 | 빠진 method |")
        lines.append("|---|---|--:|--:|--:|---|")
        for m in missing:
            miss_s = ", ".join(m["miss"][:6]) + (" …" if len(m["miss"]) > 6 else "")
            if not m["miss"]:
                miss_s = "(B1만 결손)" if m["caseb_n"] == 16 else "-"
            lines.append(f"| {m['cell']} | {m['sel']} | {m['K']} | {m['b1']} | "
                         f"{m['caseb_n']} | {miss_s} |")
        lines.append("")
        lines.append("**해석**:")
        lines.append("- `B1만 결손` (CaseB 16 완비, B1=0): K=10/30 변형 cell — 측정 시 "
                     "paper-default(K=20) B1 대비 paired 측정. 분석에서 K=20 B1 fallback 적용 (정상).")
        lines.append("- `CaseB method수=4` (chao_weighted/hilbert_real/hyperloglog/sparse_rp만): "
                     "raw K-sweep 5/12 partial run — A1-DEEP/A2-Fig7/A2-Fig9/A5-DEEP 계열 "
                     "K10/K30 은 4 method만 측정. A1-SIFT/A1-SSN 만 16 method K-chain 완비.")
        lines.append("- A2-Fig8 (DEEP+CC3M multi-vector): paper §V-A multi-table scope 외 "
                     "(C5 cascade drop) — 4 method만, 분석 참고용.")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
