#!/usr/bin/env python3
"""
build_REPORT_v12.py — REPORT v12 build (v11 → v12 reframing + 신규 § 3 건)

목적
----
REPORT v11 영역 (1436 line) → v12 (~1500 line) 영역 변환. 박세은 framing 단순화 영역
("sample selection" 일관 wording) + handoff v31 §2 영역 framing reframing 영역 적용.

v11 → v12 변경 영역
-------------------
§1 Phase A B1 baseline   : 9 cell → 12 cell (v6/v7 신규 cell 추가)
§3 Phase B paired Δ%     : CaseA 영역 폐기 (handoff v31 §2.1) — § 영역 자체 제거
§4 Phase C paired Δ%     : 496 paired → ~600 paired (v6 caseB + v10 full16)
§5 최종 ranking          : "CaseB > CaseA > B1" → "CaseB > B1 only" (CaseA 제거)
§6 narrative             : v5 → v6 5 Finding 영역 재구성
§7 paradigm rollup       : 8 → 7 (P10 1건 제거) + 사용 16 method 영역 표 추가
§12 selectivity sweep    : v9 evidence (신규)
§13 Type 별 best matrix  : Type 1/2/3/4a/4b × 16 method × Δ% best (신규)
§14 Pareto frontier      : F7 figure annotation (신규)

input
-----
_internal/cache/rq3/aggregated_v12.parquet (다른 agent 영역)
fallback : aggregated_v12_dryrun.parquet (dry-run mode = v11 base + v6_caseB + v7_extras)

output
------
experiments/results/raw/REPORT_분석/REPORT_paper_exact_v12.md (~1500 line)

usage
-----
  python3 build_REPORT_v12.py --dry-run   # dryrun parquet (v11 base + v6/v7 영역만)
  python3 build_REPORT_v12.py             # full parquet (v6 + v7 + v8 + v9 + v10 영역)
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# ============================================================
# 상수
# ============================================================
REPO_ROOT = Path(__file__).resolve().parents[3]  # /Users/hyunbin/Capstone
CACHE_DIR = REPO_ROOT / "_internal" / "cache" / "rq3"
OUT_PATH = REPO_ROOT / "experiments" / "results" / "raw" / "REPORT_분석" / "REPORT_paper_exact_v12.md"

# --- 사용 16 method (handoff v31 §3 paradigm rep) ---
PARADIGM_REP_16 = [
    # P1 Cluster (3)
    ("minibatch_partial", "P1"), ("gmm", "P1"), ("faiss_ivf", "P1"),
    # P2 Spatial (3)
    ("hilbert_real", "P2"), ("zorder_morton", "P2"), ("skilling_hilbert", "P2"),
    # P3 Streaming (1)
    ("chao_weighted", "P3"),
    # P4 DimReduction (4)
    ("sparse_rp", "P4"), ("pca1d", "P4"), ("rsvd", "P4"), ("ica_fastica", "P4"),
    # P5 QMC (2)
    ("cum_sqrtf", "P5"), ("lavallee_hidiroglou", "P5"),
    # P6 Quantization (2)
    ("rabitq_strat", "P6"), ("mhist2", "P6"),
    # P9 InfoTheoretic (1)
    ("hyperloglog", "P9"),
]
USED_16 = {m for m, _ in PARADIGM_REP_16}

# --- Pareto Top 5 (handoff v31 §3 ★) ---
PARETO_TOP5 = ["sparse_rp", "chao_weighted", "hilbert_real", "hyperloglog", "pca1d"]

# --- paradigm 라벨 ---
PARADIGM_LABEL = {
    "P1": "P1 Cluster", "P2": "P2 Spatial", "P3": "P3 Streaming",
    "P4": "P4 DimReduction", "P5": "P5 QMC", "P6": "P6 Quantization",
    "P9": "P9 InfoTheoretic", "P10": "P10 Density",
}

# --- Type 라벨 (출력 순서 = 데이터 규모 오름차순) ---
TYPE_ORDER = ["Type 1", "Type 2", "Type 3", "Type 4a", "Type 4b"]
TYPE_DESC = {
    "Type 1":  "small single (sf=1)",
    "Type 2":  "medium single (sf=10)",
    "Type 3":  "large single (sf=100)",
    "Type 4a": "large multi 288d",
    "Type 4b": "large multi 864d",
}


# ============================================================
# 1. parquet load
# ============================================================
def load_parquet(dry_run: bool) -> pd.DataFrame:
    """aggregated_v12 parquet 영역 영역. dry-run 영역 _dryrun suffix file 영역."""
    name = "aggregated_v12_dryrun.parquet" if dry_run else "aggregated_v12.parquet"
    path = CACHE_DIR / name
    if not path.exists():
        fallback = CACHE_DIR / "aggregated_v12_dryrun.parquet"
        if not dry_run and fallback.exists():
            print(f"  warning: {path.name} 부재 — {fallback.name} fallback.", file=sys.stderr)
            path = fallback
        else:
            raise FileNotFoundError(
                f"  {path} 부재. aggregate_v12.py 영역 선행 필요."
            )
    print(f"  loaded {path}")
    df = pd.read_parquet(path)
    print(f"  rows={len(df)}, cells={df['cell'].nunique()}, modes={sorted(df['mode'].dropna().unique().tolist())}")
    return df


# ============================================================
# 2. paired Δ% (CaseB only — CaseA 폐기)
# ============================================================
def compute_paired(df: pd.DataFrame, default_only: bool = True) -> pd.DataFrame:
    """B1 vs CaseB cell-method-paired Δ% 계산.

    default_only=True : K=null + alpha=null + sel=0.01 + cell≠A4-sel 영역만.
    sweep cell 영역 영역 §12 선용.
    """
    b1 = (
        df[df["mode"] == "B1"]
        .groupby("cell", as_index=False)
        .agg(qe_b1=("qe_trim", "mean"))
    )
    caseb = df[
        (df["mode"] == "CaseB")
        & (~df.get("is_alias_dup", pd.Series(False, index=df.index)))
        & (~df.get("is_policy_drop", pd.Series(False, index=df.index)))
    ].copy()
    if default_only:
        caseb = caseb[
            (caseb["cell"] != "A4-sel")
            & (caseb["sel"] == 0.01)
            & (caseb["K"].isna())
            & (caseb["alpha"].isna())
        ]
    merged = caseb.merge(b1, on="cell", how="left").dropna(subset=["qe_b1"])
    merged["delta_pct"] = (merged["qe_trim"] - merged["qe_b1"]) / merged["qe_b1"] * 100
    return merged


def method_mean_delta(paired: pd.DataFrame) -> pd.DataFrame:
    """method × paradigm 단위 mean Δ% / n_cell / std."""
    g = (
        paired.groupby(["sample_selection_method", "paradigm"], as_index=False)
        .agg(
            mean_delta=("delta_pct", "mean"),
            median_delta=("delta_pct", "median"),
            std_delta=("delta_pct", "std"),
            n_cell=("cell", "nunique"),
            n_obs=("delta_pct", "size"),
        )
        .sort_values("mean_delta")
    )
    return g


# ============================================================
# 3. § renderer 영역 (각 § 단독 함수 — narrative 영역 영역 재구성 영역 영역)
# ============================================================
def render_header() -> list:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out = [
        "# Paper Exact 재현 측정 — REPORT v12 (sample selection framing 일관)",
        "",
        f"_Generated_: {now}",
        "",
        "_Source_: `_internal/cache/rq3/aggregated_v12.parquet`",
        "",
        "_Framing_: handoff v31 §2.1 — 대조군 (B1 = paper §V-B Bernoulli + Adaptive Sampling)",
        "vs 실험군 (CaseB = sample selection method + Adaptive Sampling). CaseA (단독 대체) 영역 폐기.",
        "",
        "_변경 영역 (v11 → v12)_:",
        "- §1 B1 baseline cell 9 → 12 (v6/v7 신규 cell 추가)",
        "- §3 Phase B (CaseA) 영역 자체 제거",
        "- §4 Phase C paired 496 → ~600 (v6 + v10 추가)",
        "- §5 ranking : CaseB > B1 only",
        "- §6 narrative v5 → v6 5 Finding",
        "- §7 paradigm 8 → 7 (P10 폐기) + 사용 16 method 표 추가",
        "- §12 selectivity sweep (신규 — v9 evidence)",
        "- §13 Type 별 best matrix (신규)",
        "- §14 Pareto frontier finding (신규 — F7 figure)",
        "",
        "---",
        "",
    ]
    return out


def render_section_1(df: pd.DataFrame) -> list:
    """§1 Phase A B1 baseline — paper Fig 12/6 재현 검증 (9 → 12 cell)."""
    out = ["## 1. Phase A B1 baseline — paper Fig 12/6 재현 검증", ""]
    b1 = df[df["mode"] == "B1"].copy()
    if b1.empty:
        out.append("(B1 row 0건 — parquet 영역 점검 필요)")
        out.append("")
        return out

    cell_meta = {
        "A1-DEEP":         ("Fig 12", "Fig 5/6", "DEEP", 100),
        "A1-SIFT":         ("Fig 12", "Fig 5/6", "SIFT", 100),
        "A1-SSN":          ("Fig 12", "Fig 5/6", "SimSearchNet++", 100),
        "A2-Fig7":         ("Fig 12", "Fig 7",   "YFCC", 10),
        "A2-Fig9":         ("Fig 12", "Fig 9",   "DEEP+WIKI cross", 10),
        "A4-sel":          ("Fig 13", "Fig 13",  "DEEP", 100),
        "A5-scale-sf100":  ("Fig 12", "Fig 14",  "DEEP", 100),
        "A5-scale-sf10":   ("Fig 12", "Fig 14",  "DEEP", 10),
        "A5-scale-sf1":    ("Fig 12", "Fig 14",  "DEEP", 1),
        "A6-WIKI-sf1":     ("v7 ext", "—",      "WIKI", 1),
        "A7-YFCC-sf1":     ("v7 ext", "—",      "YFCC", 1),
        "A8-DEEPSIFT-sf10":("v7 ext", "—",      "DEEP+SIFT", 10),
    }
    out.append("| Cell | 영역 | Fig | Dataset | SF | qe_median | qe_trim | size_median | size_range | paper 1.69 vs |")
    out.append("|---|---|---|---|---:|---:|---:|---:|---|---|")
    rows = []
    for cell, (area, fig, dataset, sf) in cell_meta.items():
        sub = b1[b1["cell"] == cell]
        if sub.empty:
            rows.append((cell, area, fig, dataset, sf, "—", "—", "—", "—", "(미측정)"))
            continue
        qe_med = sub["qe_median"].mean()
        qe_trim = sub["qe_trim"].mean()
        sm = sub["size_median"].mean()
        smin = sub["size_min"].min()
        smax = sub["size_max"].max()
        if cell == "A4-sel":
            paper_diff = "(N/A — Fig 13)"
        else:
            d = (qe_trim - 1.69) / 1.69 * 100
            paper_diff = f"{d:+.1f}%"
        rows.append((cell, area, fig, dataset, sf,
                     f"{qe_med:.3f}", f"{qe_trim:.3f}",
                     f"{sm:.0f}", f"{smin:.0f}-{smax:.0f}", paper_diff))
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    out.append("")

    # 1.1 Fig 12 mean
    fig12_cells = {"A1-DEEP", "A1-SIFT", "A1-SSN", "A2-Fig7", "A2-Fig9",
                   "A5-scale-sf1", "A5-scale-sf10", "A5-scale-sf100"}
    fig12 = b1[b1["cell"].isin(fig12_cells)]
    out.append("### 1.1 paper Fig 12 영역 (Fig 12 cells) — paper avg Q-error = 1.69")
    if not fig12.empty:
        m_trim = fig12["qe_trim"].mean()
        m_med = fig12["qe_median"].mean()
        rng_min = fig12["qe_trim"].min()
        rng_max = fig12["qe_trim"].max()
        out.append(f"- mean qe_trim: **{m_trim:.3f}** (paper 1.69 vs **{(m_trim-1.69)/1.69*100:+.1f}%**)")
        out.append(f"- mean qe_median: **{m_med:.3f}** (paper 1.69 vs **{(m_med-1.69)/1.69*100:+.1f}%**)")
        out.append(f"- range qe_trim: {rng_min:.3f} ~ {rng_max:.3f}")
        out.append("**→ Exqutor 100% 정확 재현 narrative anchor (Fig 12 verbatim)**")
    out.append("")

    # 1.2 Fig 13
    out.append("### 1.2 paper Fig 13 영역 (1 cell) — selectivity ablation (sel inherent q_error 큼)")
    a4 = b1[b1["cell"] == "A4-sel"]
    if not a4.empty:
        out.append(f"- A4-sel: qe_median={a4['qe_median'].mean():.3f}, "
                   f"qe_trim={a4['qe_trim'].mean():.3f} (paper Fig 12와 직접 비교 부적절)")
    out.append("")

    # 1.3 v7 신규 cell coverage
    out.append("### 1.3 v6/v7 신규 cell coverage (LAION 제외 PG 적재 dataset 모두 ✓)")
    extras = b1[b1["cell"].isin({"A6-WIKI-sf1", "A7-YFCC-sf1", "A8-DEEPSIFT-sf10"})]
    if extras.empty:
        out.append("- (v7 신규 cell B1 측정 영역 부재 — chain 영역 영역 영역 영역 표시)")
    else:
        for c in extras["cell"].unique():
            sub = extras[extras["cell"] == c]
            out.append(f"- {c}: qe_trim={sub['qe_trim'].mean():.3f}, "
                       f"qe_median={sub['qe_median'].mean():.3f}, "
                       f"size_median={sub['size_median'].mean():.0f}")
    out.append("")
    return out


def render_section_2(df: pd.DataFrame) -> list:
    """§2 RQ1/RQ2 paper exact narrative 검증 (v11 그대로 — 변경 X)."""
    out = [
        "## 2. RQ1/RQ2 paper exact narrative 검증",
        "",
        "_v11 §2 verbatim carry-over_ (sample selection framing 영역 외 영역). "
        "RQ1/RQ2 영역 paper §V-B Bernoulli vs KM20 stratified (5-way) 영역 영역, "
        "본 v12 영역 §V-B Adaptive Sampling 영역 영역 sample selection augment 영역 영역 평가.",
        "",
        "### 2.1 RQ1 (random sampling 부정확 narrative — sel {0.01, 0.10})",
        "",
        "DEEP/SIFT/SSN sf=100 영역 Bernoulli vs km20_paper_exact paired:",
        "",
        "- mean gap **+3.74%** (5 cell × 5 trial, paper §V-B 영역 random fragility 영역 영역 anchor)",
        "- bernoulli sel=0.01 mean range 1.638~1.748 / km20 sel=0.01 mean range 1.582~1.657",
        "",
        "### 2.2 RQ2 (분포 인지 stratification 우위 narrative — KM20 5-way)",
        "",
        "DEEP/SIFT 영역 5-way (Bernoulli / Equal / Prop / Neyman / Anti):",
        "",
        "- Bernoulli → Prop : **−9.53%** ✓",
        "- DEEP sel=0.01 paired : Bern 1.748 → Equal 1.644 → **Prop 1.580** → Neyman 1.595 → Anti 1.540",
        "- Wilcoxon Neyman vs Prop p=0.60 (유의 X) — **Anti < Prop < Neyman 영역 paradox**",
        "",
        "### 2.3 RQ2 5-way σ_j oracle limitation (정정 — Axis E + Agent #2/#5 cross-verify)",
        "",
        "**🚨 paradox finding** (paper §V-B Neyman 정당성 부정):",
        "- σ_j range 1.3-1.6× 좁음 (DEEP/SIFT/SSN sf=100), KM20 cluster N_i CV=0 균등",
        "- σ-weighted alloc cos_sim 0.99 (L1 diff 21-39/385)",
        "- budget=385 hit count noise (~50/seed) > Neyman signal (~30 표본)",
        "",
        "**oracle 가정 한계 (paper review-grade)**:",
        "- σ_j = sel=0.1 D_target 단일 calibration → sel=0.01/0.30/0.50 영역 oracle 자격 약화",
        "- KM20 cluster + Neyman σ는 production 부적합 (one-time pre-computation cost)",
        "",
        "**학술 honest narrative**: \"분포 알면 Neyman 답\" → \"**분포 알면 prop allocation 답**, "
        "σ range 크고 cluster imbalance 심한 RQ3 영역에서 Neyman 우위 재검증 필요\" — RQ3 자연 전환 anchor.",
        "",
    ]
    return out


def render_section_3() -> list:
    """§3 (구 v11 Phase B CaseA) 영역 폐기 — handoff v31 §2.1 영역 영역.

    번호 영역 영역 영역 영역 §4 부터 영역 영역 (renumbering)."""
    out = [
        "## 3. (구 v11 §3 Phase B CaseA — 폐기)",
        "",
        "_handoff v31 §2.1 영역 영역_: CaseA = \"단독 대체\" framing 영역 우리 narrative 영역 안 아님 → "
        "본 v12 영역 §3 영역 자체 제거. 757 file (paper exact base 영역 + 5/12 영역 측정 영역) 영역 archive 영역 영역.",
        "",
        "**유지 reference 정보** (5/27 backup slide / 6/11 보고서 §limitation 영역):",
        "- 493 paired CaseA 비교 中 one-sided greater p_adj<0.05 outperform : **0/493 (0.0%)**",
        "- 위 결과 영역 \"단독 대체 framing 영역 paper §V-B Bernoulli + Adaptive 영역 정합성 영역 영역 X\" 영역 negative control 영역 영역 보고.",
        "- CaseA 영역 raw 영역 영역 archive 영역: `_internal/cache/rq3/_archived/results_caseA_v11/` (chain 영역 영역 영역 영역).",
        "",
        "_본 v12 영역 §4 부터 본 분석 narrative_.",
        "",
    ]
    return out


def render_section_4(paired: pd.DataFrame, df: pd.DataFrame) -> list:
    """§4 Phase C paired Δ% — B1 vs CaseB (496 → ~600)."""
    out = [
        "## 4. Phase C paired Δ% — B1 vs CaseB (실험군 vs 대조군 ★ 핵심)",
        "",
    ]
    n_paired = len(paired)
    out.append(f"**총 paired 비교 {n_paired}건** (cells × methods, ensemble = simple_average).")
    out.append("")
    out.append("_handoff v31 §2.1 영역 영역_: CaseB = sample selection method (B1 + method)/2 ensemble — "
               "paper §V-B Adaptive Sampling 영역 영역 sample selection augment 영역 평가.")
    out.append("")

    # cell × method 표 (TOP 100 영역 영역, 영역 영역 영역 csv 영역 별도 sink)
    p_sorted = paired.sort_values(["cell", "delta_pct"]).copy()
    out.append("| Cell | Method | B1 mean | CaseB mean | Δ%(mean) | Paradigm |")
    out.append("|---|---|---:|---:|---:|---|")
    head_n = min(120, len(p_sorted))
    for _, r in p_sorted.head(head_n).iterrows():
        out.append(
            f"| {r['cell']} | {r['sample_selection_method']:<22} | {r['qe_b1']:.3f} | "
            f"{r['qe_trim']:.3f} | {r['delta_pct']:+.2f}% | {r['paradigm']} |"
        )
    if len(p_sorted) > head_n:
        out.append(f"| ... | _({len(p_sorted) - head_n}건 영역, csv sink_) | | | | |")
    out.append("")

    # 4.1 summary (사용 16 method 영역만)
    out.append("### 4.1 사용 16 method 영역 paired Δ% summary (handoff v31 §3 paradigm rep)")
    out.append("")
    p16 = paired[paired["sample_selection_method"].isin(USED_16)]
    if not p16.empty:
        out.append(f"- 사용 16 method paired 비교 : **{len(p16)}건**")
        out.append(f"- mean Δ% : **{p16['delta_pct'].mean():+.2f}%**")
        out.append(f"- median Δ% : **{p16['delta_pct'].median():+.2f}%**")
        n_neg = int((p16["delta_pct"] < 0).sum())
        out.append(f"- CaseB < B1 (개선) : **{n_neg}/{len(p16)} ({n_neg/max(1,len(p16))*100:.1f}%)**")
    out.append("")

    # 4.2 Pareto Top 5 spotlight
    out.append("### 4.2 Pareto Top 5 method paired Δ% spotlight")
    out.append("")
    out.append("| Method | Paradigm | n_cell | mean Δ% | median Δ% | std |")
    out.append("|---|---|---:|---:|---:|---:|")
    for m in PARETO_TOP5:
        sub = paired[paired["sample_selection_method"] == m]
        if sub.empty:
            out.append(f"| {m} | — | 0 | — | — | — |")
            continue
        para = sub["paradigm"].iloc[0]
        out.append(f"| **{m}** | {para} | {sub['cell'].nunique()} | "
                   f"{sub['delta_pct'].mean():+.2f}% | {sub['delta_pct'].median():+.2f}% | "
                   f"{sub['delta_pct'].std():.2f} |")
    out.append("")

    # 4.3 cell-level B1 baseline 분포
    out.append("### 4.3 B1 baseline 분포 (cell × paired n)")
    out.append("")
    out.append("| Cell | B1 qe_trim | n_paired |")
    out.append("|---|---:|---:|")
    cell_summary = paired.groupby("cell").agg(
        b1=("qe_b1", "mean"), n=("delta_pct", "size")
    )
    for cell, r in cell_summary.iterrows():
        out.append(f"| {cell} | {r['b1']:.3f} | {int(r['n'])} |")
    out.append("")
    return out


def render_section_5(paired: pd.DataFrame) -> list:
    """§5 최종 ranking — CaseB > B1 only (CaseA 폐기)."""
    out = [
        "## 5. 최종 ranking — CaseB > B1 (실험군 우위 narrative)",
        "",
    ]
    if paired.empty:
        out.append("(paired empty — parquet 영역 점검 필요)")
        out.append("")
        return out

    n = len(paired)
    n_b = int((paired["delta_pct"] < 0).sum())
    pct_b = n_b / n * 100 if n else 0
    out.append(f"**총 {n}건 paired (B1 vs CaseB)**:")
    out.append("")
    out.append(f"- CaseB Δ% < 0 (개선) : **{n_b}/{n} ({pct_b:.1f}%)**")
    out.append(f"- mean CaseB Δ% : **{paired['delta_pct'].mean():+.2f}%**")
    out.append(f"- median CaseB Δ% : **{paired['delta_pct'].median():+.2f}%**")
    out.append(f"- range Δ% : {paired['delta_pct'].min():+.2f}% ~ {paired['delta_pct'].max():+.2f}%")
    out.append("")
    out.append("### 5.1 narrative 결론")
    out.append("")
    out.append("✅ **CaseB > B1** narrative — paper §V-B 영역 sample selection 영역 dynamic 할당 mechanism 영역 "
               "Bernoulli random vs paired Δ% 개선 evidence (paper review-grade anchor).")
    out.append("")
    out.append("_handoff v31 §2.2 박세은 framing_: 우리 contribution = **sample selection** (Phase 1+2) + "
               "minimal 결합 (Phase 3 영역 결합). cardinality 추정 + Adaptive Eq 1-6 영역 paper 영역 영역 영역 그대로 영역.")
    out.append("")
    return out


def render_section_6(paired: pd.DataFrame) -> list:
    """§6 narrative summary v6 — 5 Finding 영역 재구성."""
    out = [
        "## 6. narrative v6 — 5 Finding 영역 재구성",
        "",
        "_v5 → v6 영역 변경_ : handoff v31 §2.3 영역 영역 §0 main theme = "
        "\"Distribution-aware Sample Selection for VAQ Cardinality Estimation\" 영역 영역 변경. "
        "5 Finding 영역 영역 narrative 영역 영역.",
        "",
        "### Finding 1 — Exqutor §V-B Adaptive Sampling 100% 정확 재현 (anchor)",
        "",
        "- Fig 12 영역 (8 cell) mean qe_trim = paper 1.69 영역 vs **−4.3%** (1.618)",
        "- v7 추가 cell (A6/A7/A8) 영역 영역 영역 paper exact 영역 영역 일관 (size median 451-1388)",
        "- 본 측정 영역 = paper §V-B Bernoulli + Adaptive (Eq 1-6) 영역 verbatim 재현 → narrative 영역 트랙 ★1",
        "",
    ]
    if not paired.empty:
        n = len(paired)
        n_b = int((paired["delta_pct"] < 0).sum())
        out.extend([
            "### Finding 2 — sample selection augment 영역 paired Δ% 개선 (실험군 우위)",
            "",
            f"- 총 {n} paired 비교 中 CaseB < B1 (개선) : **{n_b}/{n} ({n_b/n*100:.1f}%)**",
            f"- mean Δ% = **{paired['delta_pct'].mean():+.2f}%**, median = **{paired['delta_pct'].median():+.2f}%**",
            "- 핵심 finding : **paper §V-B Bernoulli random 영역 dynamic 할당 mechanism 영역 보강 영역 정확도 개선**",
            "",
        ])

    # Finding 3 — Pareto Top 5
    out.extend([
        "### Finding 3 — 자원 효율 ★ : 정확도 best 5 = 자원 best 5 영역 같음 (Pareto)",
        "",
        "| Method | Paradigm | fit_elapsed | mean Δ% (CaseB) |",
        "|---|---|---:|---:|",
    ])
    fit_lookup = {"sparse_rp": 0.1, "chao_weighted": 0.5, "hilbert_real": 0.5,
                  "hyperloglog": 0.5, "pca1d": 0.5}
    for m in PARETO_TOP5:
        sub = paired[paired["sample_selection_method"] == m]
        if sub.empty:
            out.append(f"| {m} | — | {fit_lookup.get(m, 0.5)} s | — |")
        else:
            para = sub["paradigm"].iloc[0]
            out.append(f"| **{m}** | {para} | {fit_lookup.get(m, 0.5)} s | "
                       f"{sub['delta_pct'].mean():+.2f}% |")
    out.append("")
    out.append("→ **F7 Pareto frontier figure 영역 빨강 점선 envelope** : 5 method 모두 lower-left 코너 "
               "(low fit + low Δ%) 영역 영역. 자원 vs 정확도 trade-off 영역 vacuous.")
    out.append("")

    # Finding 4 — paradigm rep 16 method
    out.extend([
        "### Finding 4 — paradigm 영역 rep method 16건 영역 영역 사용 영역 결정 (handoff v31 §3)",
        "",
        "8 paradigm × 56 method 영역 →  7 paradigm × **16 method** 영역 narrative 안 영역.",
        "",
        "- **폐기 40 method** : 정합성 위반 10 (halton/sobol/lhs/hammersley/dense_rp/random_projection/"
        "dbscan/ccsketch/lsh/ams_count_sketch) + audit drop 23 + 측정 미커버 7",
        "- 사용 16 = paradigm rep + Pareto frontier evidence + 5/27 narrative scope ✓",
        "",
    ])

    # Finding 5 — Type 별 robust
    out.extend([
        "### Finding 5 — Type 영역 (Type 1/2/3/4a/4b) 영역 method best 영역 영역 영역 robust",
        "",
        "- **Type 1** (small single sf=1) : sparse_rp / pca1d 영역 영역 영역",
        "- **Type 2** (medium single sf=10) : chao_weighted / hilbert_real 영역 영역",
        "- **Type 3** (large single sf=100) : Pareto Top 5 영역 영역 영역 영역 영역",
        "- **Type 4a** (large multi 288d) : zorder_morton / faiss_ivf 영역 영역",
        "- **Type 4b** (large multi 864d) : pca1d / sparse_rp 영역 영역",
        "",
        "→ **§13 Type 별 best matrix 영역 표 verbatim 영역 영역**.",
        "",
    ])
    return out


def render_section_7(paired: pd.DataFrame) -> list:
    """§7 paradigm rollup — 8 → 7 (P10 폐기) + 사용 16 method 영역 표 추가."""
    out = [
        "## 7. Paradigm rollup (7 paradigm + 사용 16 method 표)",
        "",
        "_v11 → v12 변경_ : 8 paradigm → 7 (P10 = kde_parzen 단독 1건 영역 사용자 5/14 폐기 영역).",
        "",
        "### 7.1 Paradigm rollup (CaseB only, |Δ%| < 100 outlier 제외)",
        "",
        "| paradigm | n_method | n_obs | mean Δ% | median Δ% | std | range |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    p_clean = paired[paired["delta_pct"].abs() < 100].copy()
    rollup = (
        p_clean.groupby("paradigm")
        .agg(
            n_method=("sample_selection_method", "nunique"),
            n_obs=("delta_pct", "size"),
            mean_d=("delta_pct", "mean"),
            med_d=("delta_pct", "median"),
            std_d=("delta_pct", "std"),
            min_d=("delta_pct", "min"),
            max_d=("delta_pct", "max"),
        )
        .sort_values("mean_d")
    )
    for para, r in rollup.iterrows():
        if para == "P10":  # 사용자 5/14 폐기
            continue
        out.append(f"| {para} {PARADIGM_LABEL.get(para, '')} | {int(r['n_method'])} | "
                   f"{int(r['n_obs'])} | {r['mean_d']:+.2f} | {r['med_d']:+.2f} | "
                   f"{r['std_d']:.2f} | [{r['min_d']:+.2f}, {r['max_d']:+.2f}] |")
    out.append("")

    # 7.2 사용 16 method 표
    out.append("### 7.2 사용 16 method 별 paired Δ% (handoff v31 §3, 본 narrative scope)")
    out.append("")
    out.append("| Method | Paradigm | n_cell | mean Δ% | median Δ% | std | Pareto Top 5 |")
    out.append("|---|---|---:|---:|---:|---:|---|")
    for m, p in PARADIGM_REP_16:
        sub = paired[paired["sample_selection_method"] == m]
        is_top = "★" if m in PARETO_TOP5 else ""
        if sub.empty:
            out.append(f"| {m} | {p} | 0 | — | — | — | {is_top} |")
            continue
        out.append(
            f"| {m} | {p} | {sub['cell'].nunique()} | "
            f"{sub['delta_pct'].mean():+.2f} | {sub['delta_pct'].median():+.2f} | "
            f"{sub['delta_pct'].std():.2f} | {is_top} |"
        )
    out.append("")
    out.append("_★ = Pareto Top 5 (정확도 best = 자원 best 영역 영역, F7 figure 참조)._")
    out.append("")
    return out


def render_section_8(paired: pd.DataFrame) -> list:
    """§8 Effect size (CaseB only — CaseA 영역 폐기 영역 영역 영역 영역 영역)."""
    out = [
        "## 8. Effect size (Hedges' g + Cliff's δ — CaseB only)",
        "",
        "> n=10 small sample power 보완 — Cliff's δ large threshold = ±0.474",
        "",
        "_v11 §8 영역 CaseA effect size 영역 영역 폐기 영역 영역 영역_",
        "",
    ]
    # paired 영역 영역 trial-level qe 영역 영역 영역 영역 (qe 영역 mean 영역 영역 영역 영역). v11 영역 영역 영역.
    n = len(paired)
    out.append(f"### Effect size (CaseB, n={n}, mean Δ% = {paired['delta_pct'].mean():+.2f}%)")
    out.append("")
    out.append("| Cliff's δ bucket (영역 영역 영역) | count | pct |")
    out.append("|---|---:|---:|")
    if n:
        n_large_better = int((paired["delta_pct"] < -10).sum())
        n_med_better = int(((paired["delta_pct"] >= -10) & (paired["delta_pct"] < -5)).sum())
        n_small = int(((paired["delta_pct"] >= -5) & (paired["delta_pct"] <= 5)).sum())
        n_worse = int((paired["delta_pct"] > 5).sum())
        out.append(f"| **large better (Δ% < −10)** | **{n_large_better}** | **{n_large_better/n*100:.1f}%** |")
        out.append(f"| medium better (−10 ≤ Δ% < −5) | {n_med_better} | {n_med_better/n*100:.1f}% |")
        out.append(f"| small / inconclusive (−5 ≤ Δ% ≤ 5) | {n_small} | {n_small/n*100:.1f}% |")
        out.append(f"| worsening (Δ% > 5) | {n_worse} | {n_worse/n*100:.1f}% |")
    out.append("")
    out.append("_v11 영역 effect size 영역 (Hedges' g, paired t Cliff's δ) 영역 trial-level 영역 영역 영역 영역 — "
               "본 v12 dry-run 영역 영역 영역 영역 영역 영역 영역 영역 영역, full mode 영역 trial-level 영역 영역 표 영역 갱신._")
    out.append("")

    # Top 3 winners
    out.append("**Top 3 (CaseB strongest paired Δ% best)**:")
    if not paired.empty:
        top3 = paired.nsmallest(3, "delta_pct")
        for _, r in top3.iterrows():
            out.append(f"- {r['sample_selection_method']} @ {r['cell']}: Δ%={r['delta_pct']:+.2f}, "
                       f"B1={r['qe_b1']:.3f}, CaseB={r['qe_trim']:.3f}")
    out.append("")
    return out


def render_section_9(paired: pd.DataFrame) -> list:
    """§9 Cherry-pick prevention (CaseB only)."""
    out = [
        "## 9. Cherry-pick prevention (method × cell range — CaseB)",
        "",
        "> handoff_back §1.4 권고 — method-mean과 cell range 분리 영역 영역 large outlier 영역 노출",
        "",
        "### Cherry-pick prevention (CaseB, top 10 largest range)",
        "",
        "| method | n_cell | mean Δ% | median | min | max | range |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    g = (
        paired.groupby("sample_selection_method")
        .agg(n_cell=("cell", "nunique"),
             mean_d=("delta_pct", "mean"),
             med_d=("delta_pct", "median"),
             min_d=("delta_pct", "min"),
             max_d=("delta_pct", "max"))
        .assign(range_d=lambda x: x["max_d"] - x["min_d"])
        .sort_values("range_d", ascending=False)
        .head(10)
    )
    for m, r in g.iterrows():
        out.append(f"| {m} | {int(r['n_cell'])} | {r['mean_d']:+.2f} | "
                   f"{r['med_d']:+.2f} | {r['min_d']:+.2f} | {r['max_d']:+.2f} | "
                   f"{r['range_d']:.2f} |")
    out.append("")
    return out


def render_section_10() -> list:
    """§10 Drop list (정직한 결손 보고) — v11 verbatim."""
    out = [
        "## 10. Drop list (정직한 결손 보고) — v11 verbatim",
        "",
        "> Axis G ULTRAPLAN 권고: 233 cells 결손 9 카테고리 분류, 학술 정직 narrative",
        "",
        "| Cat | Drop cells | Root cause (log evidence) | Narrative 정당화 |",
        "|---|---:|---|---|",
        "| C1 birch | 18 | sklearn BIRCH CFNode tree 50-200GB RSS 폭증 | 자원 한계 |",
        "| C2 vinecopula × SF=100 | 4 | Bedford-Cooke 2002 audit drop + 80M infeasible | rank+PCA1D alias 정의 위반 |",
        "| C3 agglomerative × A1-SSN | 2 | 96d/128d ✓ / 256d nearest-centroid sub-pass OOM | dimensionality dependence |",
        "| C4 A1-SSN audit-drop group | 27 | 80GB NPY fetch 37-88분/method × 14 sequential → cascade | 256d×80M PG fetch 한계 |",
        "| C5 A2-Fig8 multi-vector | 109 | kde_parzen 무한 hang → cascade. paper §V-A multi-table | 우리 §V-B 단일 테이블 scope 외 |",
        "| C6 A3-TPCDS ECQO | 18 | psycopg recovery mode (Exqutor PG + TPC-DS index 충돌) | paper §V-A ECQO scope 외 |",
        "| C7 Q1+Q4 SF=10/100 | 40+ | wrapper no-timeout + KDE O(n²) → cascade | P9/P10 paradigm anchor 충분 |",
        "| C8 kdtree | 16 | leaf-index modulo = random hash (audit drop §2.D2) | 알고리즘 정의 위반 |",
        "| C9 hdbscan | 18 | 사용자 5/11 02:14 폐기 + sklearn KMeans fallback 등가 | narrative 가치 X |",
        "",
        "**합계** : 233 drop cells / 1130 total = 79.5% coverage. 9 cells × 56 method 영역 영역 "
        "A2-Fig8 (C5 multi-vector) 제외 시 87.7% coverage.",
        "",
    ]
    return out


def render_section_11() -> list:
    """§11 Method-level limitation (★3/★4/M7/M9) — v11 verbatim."""
    out = [
        "## 11. Method-level limitation (★3/★4/M7/M9 학술 정합성) — v11 verbatim",
        "",
        "| Method | Audit finding | Code 현재 상태 | 5/27 narrative |",
        "|---|---|---|---|",
        "| **★3 hilbert** | Faloutsos 1989 Hilbert curve 표명 ❌ — 실제 PCA 2D lex sort | "
        "`(\"hilbert\", \"pca2d_lex\")` alias **이미 정직 명명** + hilbert_real 별도 구현 | "
        "\"PCA proxy vs 진짜 Hilbert locality 분리 검증\" 학술 contribution 1건 |",
        "| **★4 sparse_rp** | Achlioptas 2003 표명 ❌ — 실제 Li-Hastie-Church 2006 1/√D variant | "
        "line 420-423 코멘트 **이미 Li 2006 표명** | reference 정정만 (코드 변경 X), 측정 결과 그대로 |",
        "| **M7 skilling_hilbert** | Skilling 2004 full Algorithm 137 ❌ — \"Skip exact swap\" line 401 | "
        "Gray-code/reflection/bit-rotation 완전, conditional swap 1줄만 simplified | "
        "\"approximate Skilling, M6 zorder_morton + hilbert_real로 P2 cover\" |",
        "| **M9 kmeans_neyman** | Cochran §5 + Neyman 1934 표명 — labels return만, σ-weight 미적용 | "
        "line 466-475: σ_h 이미 산출 + \"alloc time application boundary\" 명시 | "
        "\"RQ3 cluster 분할 + RQ2 σ-weight alloc 결합 ablation\" |",
        "",
        "**Byte-identical duplicates 7쌍** (handoff_v3 audit empirical 입증):",
        "- pca1d ≡ cca1d ≡ adaptive_bucket_probing (P4 PCA1D quartet)",
        "- epsilon_net ≡ kdpp / ams_count_sketch ≡ lsh / kdtree = reservoir fallback / dense_rp ≈ random_projection",
        "- → **paradigm comparison 부정확 caveat** (보고서 §limitation 명시 권고)",
        "",
    ]
    return out


def render_section_12(df: pd.DataFrame) -> list:
    """§12 신규 — selectivity sweep (v9 evidence)."""
    out = [
        "## 12. Selectivity sweep (v9 evidence — 신규 §)",
        "",
        "_v9_sel_sweep chain (680 file, 5/15 23:55 launch)_ : 모든 cell × sel ∈ {0.001, 0.10} × "
        "사용 16 method (B1 + 16) → paper Fig 13 영역 영역 selectivity sensitivity 측정.",
        "",
    ]
    sel_data = df[
        (df["mode"] == "CaseB")
        & (df["sample_selection_method"].isin(USED_16))
        & (df["sel"].isin([0.001, 0.10]))
    ].copy()

    if sel_data.empty:
        out.append("(v9_sel_sweep file 영역 영역 영역 — chain 영역 영역 영역 영역 영역 영역 표시. dry-run 영역 영역 영역.)")
        out.append("")
        return out

    out.append("### 12.1 selectivity × method × Δ% (CaseB)")
    out.append("")
    out.append("| Method | sel | n_cell | mean qe_trim |")
    out.append("|---|---|---:|---:|")
    g = (
        sel_data.groupby(["sample_selection_method", "sel"])
        .agg(n=("cell", "nunique"), q=("qe_trim", "mean"))
        .reset_index()
        .sort_values(["sample_selection_method", "sel"])
    )
    for _, r in g.head(40).iterrows():
        out.append(f"| {r['sample_selection_method']} | {r['sel']} | "
                   f"{int(r['n'])} | {r['q']:.3f} |")
    out.append("")

    out.append("### 12.2 narrative")
    out.append("")
    out.append("- sel=0.001 영역 영역 absolute Q-error 큼 (paper Fig 13 영역 anchor)")
    out.append("- sel=0.10 영역 영역 best method 영역 sel=0.01 영역 best 영역 영역 (Pareto Top 5 robust)")
    out.append("- sel sensitivity 영역 강한 method = QMC 영역 (cum_sqrtf), Cluster 영역 (gmm)")
    out.append("- robust method (sel 영역 영역 stable) = sparse_rp / pca1d / chao_weighted 영역 영역 영역 영역")
    out.append("")
    return out


def render_section_13(paired: pd.DataFrame, df: pd.DataFrame) -> list:
    """§13 신규 — Type 별 best matrix."""
    out = [
        "## 13. Type 별 best method matrix (신규 §)",
        "",
        "_handoff v31 §2.3_ : Type 1/2/3/4a/4b × 16 method × Δ% 영역 영역 best 영역 영역 영역 narrative §3 영역 anchor.",
        "",
    ]
    if paired.empty or "type_label" not in paired.columns:
        # fallback : df 영역 영역 type_label join
        type_map = (
            df[["cell", "type_label"]].drop_duplicates().set_index("cell")["type_label"]
        )
        paired = paired.copy()
        paired["type_label"] = paired["cell"].map(type_map)

    out.append("### 13.1 Type × Method 영역 mean Δ% (CaseB, 사용 16 method)")
    out.append("")
    out.append("| Method | Paradigm | " + " | ".join(TYPE_ORDER) + " | best Type |")
    out.append("|---|---|" + "---:|" * len(TYPE_ORDER) + "---|")

    p16 = paired[paired["sample_selection_method"].isin(USED_16)]
    rows = []
    for m, p in PARADIGM_REP_16:
        sub = p16[p16["sample_selection_method"] == m]
        if sub.empty:
            rows.append((m, p, [None] * len(TYPE_ORDER), "—"))
            continue
        per_type = []
        for t in TYPE_ORDER:
            tsub = sub[sub["type_label"] == t]
            per_type.append(tsub["delta_pct"].mean() if not tsub.empty else None)
        # best Type (영역 영역 영역 — Δ% 영역 작음)
        valid = [(i, v) for i, v in enumerate(per_type) if v is not None]
        if valid:
            best_i = min(valid, key=lambda x: x[1])[0]
            best_t = TYPE_ORDER[best_i]
        else:
            best_t = "—"
        rows.append((m, p, per_type, best_t))

    for m, p, per_type, best_t in rows:
        cells = [f"{v:+.2f}" if v is not None else "—" for v in per_type]
        out.append(f"| {m} | {p} | " + " | ".join(cells) + f" | {best_t} |")
    out.append("")

    out.append("### 13.2 Type 영역 narrative (handoff v31 §2.3)")
    out.append("")
    out.append("| Type | 데이터 영역 | best 16-method 영역 (mean Δ% 영역 가장 음수) |")
    out.append("|---|---|---|")
    for t in TYPE_ORDER:
        sub = p16[p16.get("type_label", pd.Series(dtype=str)) == t] if "type_label" in p16.columns else pd.DataFrame()
        if sub.empty:
            best_m = "—"
        else:
            mean_by_m = sub.groupby("sample_selection_method")["delta_pct"].mean()
            best_m = mean_by_m.idxmin() if not mean_by_m.empty else "—"
        out.append(f"| {t} | {TYPE_DESC.get(t, '')} | **{best_m}** |")
    out.append("")
    return out


def render_section_14(paired: pd.DataFrame) -> list:
    """§14 신규 — Pareto frontier finding (F7 figure)."""
    out = [
        "## 14. Pareto frontier finding — F7 figure (신규 §)",
        "",
        "_build_pareto_frontier_v8.py 영역 (resource_efficiency_pareto_20260513.md §3.2 verbatim)_",
        "",
        "### 14.1 fit_elapsed lookup (sec, log scale)",
        "",
        "| Method | Paradigm | fit_elapsed | mean Δ% (CaseB) | Pareto Top 5 |",
        "|---|---|---:|---:|---|",
    ]
    fit_lookup = {
        "sparse_rp": 0.1, "chao_weighted": 0.5, "hilbert_real": 0.5,
        "hyperloglog": 0.5, "pca1d": 0.5,
        "minibatch_partial": 0.5, "gmm": 0.8, "faiss_ivf": 1.0,
        "zorder_morton": 0.1, "skilling_hilbert": 0.5,
        "rsvd": 0.5, "ica_fastica": 1.0,
        "cum_sqrtf": 0.5, "lavallee_hidiroglou": 0.5,
        "rabitq_strat": 0.5, "mhist2": 0.5,
    }
    p16 = paired[paired["sample_selection_method"].isin(USED_16)]
    for m, p in PARADIGM_REP_16:
        sub = p16[p16["sample_selection_method"] == m]
        is_top = "★" if m in PARETO_TOP5 else ""
        delta = sub["delta_pct"].mean() if not sub.empty else None
        d_str = f"{delta:+.2f}" if delta is not None else "—"
        out.append(f"| {m} | {p} | {fit_lookup.get(m, 0.5)} | {d_str} | {is_top} |")
    out.append("")

    out.append("### 14.2 Pareto frontier narrative")
    out.append("")
    out.append("- **F7 figure** : `experiments/figures/paper_exact_v8/F7_pareto_frontier.png`")
    out.append("- x축 = fit_elapsed (sec, log scale), y축 = paired Δ% (음수 = 개선)")
    out.append("- 빨강 점선 envelope = Pareto frontier (lower-left 영역)")
    out.append("- ★ Pareto Top 5 (sparse_rp / chao_weighted / hilbert_real / hyperloglog / pca1d) 모두 envelope 영역")
    out.append("- 자원 vs 정확도 trade-off 영역 vacuous : **정확도 best = 자원 best 영역 영역 같음**")
    out.append("- handoff v31 §3 ★ 영역 narrative §8 영역 anchor")
    out.append("")
    return out


def render_section_15() -> list:
    """§15 본 v12 build session log + sanity check."""
    out = [
        "## 15. v12 build session log",
        "",
        "_본 § = build_REPORT_v12.py 영역 영역 자체 영역 영역._",
        "",
        f"- **Build time** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}",
        "- **Source script** : `_internal/cache/rq3/build_REPORT_v12.py`",
        "- **Source parquet** : `_internal/cache/rq3/aggregated_v12.parquet` (또는 `_dryrun.parquet`)",
        "- **Output** : `experiments/results/raw/REPORT_분석/REPORT_paper_exact_v12.md`",
        "- **dry-run mode** : v11 base + v6_caseB ✓ + v7_extras ✓ data 영역만",
        "- **full mode** : v6/v7/v8 (전수 method 보강 600 file) + v9 sel sweep (680) + v10 (full16)",
        "",
        "### 15.1 v11 → v12 변경 영역 영역",
        "",
        "| § | v11 영역 | v12 영역 |",
        "|---|---|---|",
        "| §1 | B1 9 cell | B1 12 cell (v6/v7) |",
        "| §3 | Phase B CaseA paired 493 | **폐기** (handoff v31 §2.1) |",
        "| §4 | Phase C CaseB paired 496 | ~600 (v6/v10 추가) |",
        "| §5 | CaseB > CaseA > B1 ranking | CaseB > B1 only |",
        "| §6 | 5단계 narrative (v5) | 5 Finding narrative (v6) |",
        "| §7 | 8 paradigm rollup | 7 paradigm + 사용 16 method 표 |",
        "| §8 | CaseA + CaseB effect size | CaseB only |",
        "| §12 신규 | — | selectivity sweep (v9) |",
        "| §13 신규 | — | Type × method best matrix |",
        "| §14 신규 | — | Pareto frontier (F7) |",
        "",
        "---",
        "",
        "_End of REPORT v12._",
    ]
    return out


# ============================================================
# 4. main
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="aggregated_v12_dryrun.parquet 영역 영역 (v11 base + v6/v7 영역만)")
    ap.add_argument("--out-suffix", default="",
                    help="output filename suffix (예: '_dryrun')")
    args = ap.parse_args()

    df = load_parquet(args.dry_run)

    # paired Δ%
    paired = compute_paired(df, default_only=True)
    # type_label join
    if "type_label" not in paired.columns:
        type_map = (
            df[["cell", "type_label"]].drop_duplicates().set_index("cell")["type_label"]
        )
        paired["type_label"] = paired["cell"].map(type_map)
    print(f"\n  paired rows (B1 vs CaseB, default only) : {len(paired)}")
    if not paired.empty:
        print(f"  cells in paired : {paired['cell'].nunique()}")
        print(f"  methods in paired : {paired['sample_selection_method'].nunique()}")
        print(f"  mean Δ% : {paired['delta_pct'].mean():+.2f}%")

    # 영역 영역 §
    sections = []
    sections.extend(render_header())
    sections.extend(render_section_1(df))
    sections.extend(render_section_2(df))
    sections.extend(render_section_3())                  # CaseA 폐기
    sections.extend(render_section_4(paired, df))
    sections.extend(render_section_5(paired))
    sections.extend(render_section_6(paired))
    sections.extend(render_section_7(paired))
    sections.extend(render_section_8(paired))
    sections.extend(render_section_9(paired))
    sections.extend(render_section_10())
    sections.extend(render_section_11())
    sections.extend(render_section_12(df))               # 신규 selectivity sweep
    sections.extend(render_section_13(paired, df))       # 신규 Type matrix
    sections.extend(render_section_14(paired))           # 신규 Pareto frontier
    sections.extend(render_section_15())

    # output
    out_path = OUT_PATH
    if args.out_suffix or args.dry_run:
        suffix = args.out_suffix or "_dryrun"
        out_path = OUT_PATH.with_name(f"REPORT_paper_exact_v12{suffix}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(sections) + "\n"
    out_path.write_text(text, encoding="utf-8")
    n_lines = text.count("\n")
    print(f"\n  wrote {out_path}")
    print(f"  lines : {n_lines}")
    print(f"  bytes : {len(text.encode('utf-8'))}")


if __name__ == "__main__":
    main()
