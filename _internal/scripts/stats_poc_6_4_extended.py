#!/usr/bin/env python3
"""Phase 6 §6.4 통계 후속 PoC — **평면 확장 본**.

기존 `stats_poc_6_4.py` 는 phase2 (DEEP sf=10 sel=0.001 12 cell core) + phase3 (sel=0.01·0.1 8 cell
carry-over) = 20 cell · 580 paired · 4,800 trial 의 PoC 1·2·3 (plan-level effect size · cluster
paired bootstrap · variance decomposition) 정본.

본 확장 script (`stats_poc_6_4_extended.py`) 는 신규 phase4_extension 평면 측정 raw 가 도착하면
다음 3 평면을 통합 분석한다:

  · **phase2** — DEEP sf=10 sel=0.001 12 cell (carry, §5.4 보고서 base)
  · **phase3** — DEEP sf=10 sel=0.01·0.1 8 cell carry-over
  · **phase4_extension** — DEEP/SIFT/SSN/WIKI/YFCC sf=1·sf=10 + DEEP+SIFT/DEEP+WIKI sf=10
                            + DEEP/SIFT/SSN sf=100 (~160 신규 cell)

세 평면 통합 후 신규 비교 축:
  1. **평면 비교** (phase2 vs phase3 vs phase4_extension) — sf=10 base 대비 평면 확장의 일반화
  2. **dataset 비교** (DEEP/SIFT/SSN/WIKI/YFCC/DEEP+SIFT/DEEP+WIKI) — 단일 → 다중 벡터 일반화
  3. **sf scaling** (sf=1 / sf=10 / sf=100) — 데이터 규모에 따른 condition 효과 변화

신규 모델 (PoC 3 extended): `log(exec_ms) ~ C(cell) + C(condition_4) + C(dataset) + C(sf) + 상호작용`.

honest exception 처리:
  · **DEEP sf=1 plan-invariant** — 5/20 prescan 16 variant 모두 injection_fired=False 확인 (carry)
    → 측정 자체 폐기 또는 분리 보고
  · **WIKI/YFCC sf=100 미적재** — NaN 처리, 평면 비교 표에서 자연 결측
  · **sf=100 censoring** — statement_timeout 180s 도달 cell 의 censored ratio 컬럼
  · **DEEP+CC3M 4건 한계** — A2-Fig8 carry, 현재 PoC 에서 제외

실행:
    python3 _internal/scripts/stats_poc_6_4_extended.py                 # 실제 분석
    python3 _internal/scripts/stats_poc_6_4_extended.py --dry-run       # raw 없어도 import test

constraint:
  · 기존 `stats_poc_6_4.py` 는 carry 정본 — 변경 X
  · 본 script = legacy carry + 확장 함수만 추가
  · font: Apple SD Gothic Neo · NanumGothic · AppleGothic · DejaVu Sans
  · matplotlib backend = "Agg"

출력:
    _internal/cache/rq3/latency/poc_6_4_extended/
      ├─ plan_level_effect_size.csv          (PoC 1)
      ├─ cluster_bootstrap.csv               (PoC 2)
      ├─ variance_decomp.csv                 (PoC 3 model2)
      ├─ variance_decomp_no_baseline.csv     (PoC 3 model3)
      ├─ variance_decomp_model1.csv          (PoC 3 model1)
      ├─ variance_decomp_extended.csv        (★ 신규 — dataset/sf factor 추가 모델)
      ├─ plane_comparison.csv                (★ 신규 — 평면 × condition × 지표)
      ├─ dataset_comparison.csv              (★ 신규 — dataset × sf × condition)
      ├─ sf_scaling.csv                      (★ 신규 — sf=1·10·100 condition 효과 변화)
      └─ summary.md

    experiments/figures/보고서_6_11/poc_6_4_extended/
      ├─ fig_plan_level_g.{png,pdf}
      ├─ fig_variance_decomp.{png,pdf}
      ├─ fig_plane_comparison_g.{png,pdf}    (★ 신규 — 평면 별 |g| 분포 boxplot)
      ├─ fig_dataset_sf_heatmap.{png,pdf}    (★ 신규 — dataset × sf 회복률 heatmap)
      └─ fig_variance_decomp_extended.{png,pdf} (★ 신규 — 모델 4 % SS 비교)
"""
from __future__ import annotations

import sys
import re
import csv
import json
import argparse
import statistics
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["Apple SD Gothic Neo", "NanumGothic", "AppleGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from analyze_latency import (  # noqa: E402
    load_results, plan_signature, _plan_changed, cell_label, _variant_label
)

REPO = SCRIPT_DIR.parent.parent
PHASE2_DIR = REPO / "_internal/cache/rq3/latency/phase2"
PHASE3_DIR = REPO / "_internal/cache/rq3/latency/phase3"
PHASE4_EXT_DIR = REPO / "_internal/cache/rq3/latency/phase4_extension"
PAIRED_P2 = PHASE2_DIR / "figures/paired_stats.csv"
PAIRED_P3 = PHASE3_DIR / "figures/paired_stats.csv"
PAIRED_P4 = PHASE4_EXT_DIR / "figures/paired_stats.csv"

CSV_DIR = REPO / "_internal/cache/rq3/latency/poc_6_4_extended"
FIG_DIR = REPO / "experiments/figures/보고서_6_11/poc_6_4_extended"

BOOTSTRAP_B = 2000
SEED = 7

# honest exception — 측정 평면 정책
PLAN_INVARIANT_KEY = ("DEEP", 1)   # 5/20 prescan 확정 — DEEP sf=1 polluter 자체 폐기 후보
SF100_MISSING_DATASETS = {"WIKI", "YFCC"}  # sf=100 미적재 dataset


# ---------------------------------------------------------------------------
# cell 파싱 — cell_label 역변환 (analyze_latency.cell_label 기준)
# ---------------------------------------------------------------------------
# 예: "tpc-h/q3 DEEP sf10 sel0.001 qid0"
_CELL_RE = re.compile(
    r"^[^/]+/(?P<query>q\d+)\s+(?P<dataset>[\w+]+)\s+sf(?P<sf>\d+)\s+"
    r"sel(?P<sel>[\d.]+)\s+qid(?P<qid>\d+)$"
)


def parse_cell(cell: str) -> dict:
    """cell_label 문자열 → {query, dataset, sf, sel, qid}.

    분석 평면이 늘면 cell 토큰 manual 파싱 필요. cell_label 의 형식이 바뀌면 본 함수도 갱신."""
    m = _CELL_RE.match(cell)
    if not m:
        return {"query": None, "dataset": None, "sf": None, "sel": None, "qid": None}
    g = m.groupdict()
    return {
        "query": g["query"],
        "dataset": g["dataset"],
        "sf": int(g["sf"]),
        "sel": float(g["sel"]),
        "qid": int(g["qid"]),
    }


# ---------------------------------------------------------------------------
# 데이터 준비 — 3 평면 통합 + plan_recovered 라벨 + paired_stats merge
# ---------------------------------------------------------------------------

def compute_plan_status(results: list[dict]) -> pd.DataFrame:
    """cell × variant → plan_recovered ∈ {True, False, None}.

    legacy carry (stats_poc_6_4.compute_plan_status 동일):
    oracle variant 의 plan_signature 를 기준으로 각 variant 가 동일 plan 인지 판정.
    oracle 이 없거나 variant plan 미캡처면 None (N/A).
    """
    rows = []
    for r in results:
        cell = cell_label(r)
        by = {_variant_label(v): v for v in r["variants"]}
        oracle = by.get("oracle")
        oracle_sig = plan_signature(oracle["plan_json"]) if oracle else ()
        for lab, v in by.items():
            sig = plan_signature(v["plan_json"])
            if not oracle_sig or not sig:
                recovered: bool | None = None
            else:
                recovered = (sig == oracle_sig)
            rows.append({"cell": cell, "variant": lab, "plan_recovered": recovered})
    return pd.DataFrame(rows)


def load_paired(include_phase4: bool = True) -> pd.DataFrame:
    """phase2 + phase3 + (선택) phase4_extension paired_stats.csv 통합.

    paired_stats 컬럼: cell · anchor · variant · n_pairs · pairing_valid ·
                       anchor_n_timeout · variant_n_timeout · median_diff_ms ·
                       anchor_med_ms · variant_med_ms · w_stat · p_value · p_holm ·
                       holm_rank · ci_lo_ms · ci_hi_ms · hedges_g · rank_biserial
    `phase` 컬럼을 append → 평면 비교 표/figure base.
    """
    frames = []
    if PAIRED_P2.exists():
        a = pd.read_csv(PAIRED_P2)
        a["phase"] = "phase2"
        frames.append(a)
    if PAIRED_P3.exists():
        b = pd.read_csv(PAIRED_P3)
        b["phase"] = "phase3"
        frames.append(b)
    if include_phase4 and PAIRED_P4.exists():
        c = pd.read_csv(PAIRED_P4)
        c["phase"] = "phase4_extension"
        frames.append(c)
    if not frames:
        return pd.DataFrame(columns=["cell", "anchor", "variant", "phase"])
    df = pd.concat(frames, ignore_index=True)
    # cell 파싱 → dataset/sf/sel/query/qid 컬럼 추가 (평면·dataset·sf 비교 base)
    parsed = df["cell"].apply(parse_cell).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)
    return df


def load_all_results() -> tuple[list[dict], list[dict], list[dict]]:
    """3 평면의 raw JSON 로드 (디렉토리 존재 시).

    DEEP sf=1 (plan-invariant) 은 PHASE4_EXT_DIR 안에 latency_*_DEEP_sf1_*.json 으로 들어올 수
    있다. compute_plan_status 와 build_long_df 는 raw 를 그대로 사용 — DEEP sf=1 분리 처리는
    각 분석 함수에서 cell 파싱 기준으로 (dataset, sf) 일치 시 폐기/주석 처리.
    """
    r2 = load_results(PHASE2_DIR) if PHASE2_DIR.exists() else []
    r3 = load_results(PHASE3_DIR) if PHASE3_DIR.exists() else []
    r4 = load_results(PHASE4_EXT_DIR) if PHASE4_EXT_DIR.exists() else []
    return r2, r3, r4


# ---------------------------------------------------------------------------
# PoC 1 — plan-level effect size 분층 (legacy carry, anchor=baseline·B1)
# ---------------------------------------------------------------------------

def poc1_plan_level_effect_size(paired: pd.DataFrame) -> pd.DataFrame:
    """legacy carry — anchor × plan_recovered 별 |g| 분포 + 유의 비율 + CI 비제로 비율.

    본 확장에서 변경 X (legacy 정본과 동일 함수). 평면 일반화 분석은 별도
    `plane_comparison_table()` 에서 수행.
    """
    def _label_plan(v):
        try:
            if pd.isna(v):
                return "N/A"
        except (TypeError, ValueError):
            pass
        return "True" if bool(v) else "False"

    paired = paired.copy()
    paired["plan_status"] = paired["plan_recovered"].map(_label_plan)
    paired["abs_g"] = paired["hedges_g"].abs()
    paired["g_band"] = pd.cut(paired["abs_g"],
                              bins=[-0.001, 0.5, 0.8, np.inf],
                              labels=["small", "medium", "large"])
    paired["sig"] = paired["p_holm"] < 0.05
    paired["ci_excl0"] = (paired["ci_lo_ms"] * paired["ci_hi_ms"]) > 0

    out = []
    for anchor in ["baseline", "B1"]:
        for status in ["True", "False", "N/A"]:
            sub = paired[(paired["anchor"] == anchor) &
                         (paired["plan_status"] == status)]
            n = len(sub)
            if n == 0:
                out.append({
                    "anchor": anchor, "plan_recovered": status, "n": 0,
                    "n_small": 0, "n_medium": 0, "n_large": 0,
                    "pct_small": float("nan"), "pct_medium": float("nan"),
                    "pct_large": float("nan"),
                    "mean_abs_g": float("nan"), "median_abs_g": float("nan"),
                    "n_p_holm_sig": 0, "pct_p_holm_sig": float("nan"),
                    "n_ci_excludes_zero": 0, "pct_ci_excludes_zero": float("nan"),
                })
                continue
            n_small = int((sub["g_band"] == "small").sum())
            n_med = int((sub["g_band"] == "medium").sum())
            n_lar = int((sub["g_band"] == "large").sum())
            n_sig = int(sub["sig"].sum())
            n_ci = int(sub["ci_excl0"].sum())
            out.append({
                "anchor": anchor, "plan_recovered": status, "n": n,
                "n_small": n_small, "n_medium": n_med, "n_large": n_lar,
                "pct_small": 100.0 * n_small / n,
                "pct_medium": 100.0 * n_med / n,
                "pct_large": 100.0 * n_lar / n,
                "mean_abs_g": float(sub["abs_g"].mean()),
                "median_abs_g": float(sub["abs_g"].median()),
                "n_p_holm_sig": n_sig, "pct_p_holm_sig": 100.0 * n_sig / n,
                "n_ci_excludes_zero": n_ci,
                "pct_ci_excludes_zero": 100.0 * n_ci / n,
            })
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# PoC 2 — cluster paired bootstrap (legacy carry)
# ---------------------------------------------------------------------------

def poc2_cluster_bootstrap(paired: pd.DataFrame,
                            B: int = BOOTSTRAP_B,
                            seed: int = SEED) -> pd.DataFrame:
    """legacy carry — B1 anchor 의 두 metric naïve vs cluster bootstrap 95% CI."""
    sub = paired[paired["anchor"] == "B1"].reset_index(drop=True).copy()
    cells = list(sub["cell"].unique())
    n_total = len(sub)
    n_cells = len(cells)

    if n_total == 0:
        # 평면 4 한정 dry-run 시 빈 paired 가능
        return pd.DataFrame([
            {"metric": "mean_median_diff_ms_B1", "point_estimate": float("nan"),
             "naive_ci_lo": float("nan"), "naive_ci_hi": float("nan"),
             "naive_width": float("nan"),
             "cluster_ci_lo": float("nan"), "cluster_ci_hi": float("nan"),
             "cluster_width": float("nan"),
             "width_ratio_cluster_over_naive": float("nan"),
             "n_total": 0, "n_clusters": 0, "B": B},
        ])

    md_pos = sub["median_diff_ms"].to_numpy(dtype=float)
    sig_pos = (sub["p_holm"] < 0.05).to_numpy(dtype=bool)
    cell_to_idx = {c: np.where(sub["cell"].to_numpy() == c)[0]
                    for c in cells}

    rng = np.random.default_rng(seed)
    idx_naive = rng.integers(0, n_total, size=(B, n_total))
    md_naive = md_pos[idx_naive].mean(axis=1)
    sig_naive = sig_pos[idx_naive].mean(axis=1) * 100.0

    md_cluster = np.empty(B, dtype=float)
    sig_cluster = np.empty(B, dtype=float)
    cell_idx_arr = np.arange(n_cells)
    for b in range(B):
        chosen = rng.choice(cell_idx_arr, size=n_cells, replace=True)
        rows = np.concatenate([cell_to_idx[cells[i]] for i in chosen])
        md_cluster[b] = md_pos[rows].mean()
        sig_cluster[b] = sig_pos[rows].mean() * 100.0

    def _summarize(arr, point):
        lo, hi = np.percentile(arr, [2.5, 97.5])
        return point, float(lo), float(hi), float(hi - lo)

    p_md = float(md_pos.mean())
    p_sig = float(sig_pos.mean() * 100.0)
    n_pe_md, n_lo_md, n_hi_md, n_w_md = _summarize(md_naive, p_md)
    c_pe_md, c_lo_md, c_hi_md, c_w_md = _summarize(md_cluster, p_md)
    n_pe_si, n_lo_si, n_hi_si, n_w_si = _summarize(sig_naive, p_sig)
    c_pe_si, c_lo_si, c_hi_si, c_w_si = _summarize(sig_cluster, p_sig)

    return pd.DataFrame([
        {"metric": "mean_median_diff_ms_B1",
         "point_estimate": p_md,
         "naive_ci_lo": n_lo_md, "naive_ci_hi": n_hi_md, "naive_width": n_w_md,
         "cluster_ci_lo": c_lo_md, "cluster_ci_hi": c_hi_md, "cluster_width": c_w_md,
         "width_ratio_cluster_over_naive": c_w_md / n_w_md if n_w_md > 0 else float("nan"),
         "n_total": n_total, "n_clusters": n_cells, "B": B},
        {"metric": "pct_p_holm_sig_B1",
         "point_estimate": p_sig,
         "naive_ci_lo": n_lo_si, "naive_ci_hi": n_hi_si, "naive_width": n_w_si,
         "cluster_ci_lo": c_lo_si, "cluster_ci_hi": c_hi_si, "cluster_width": c_w_si,
         "width_ratio_cluster_over_naive": c_w_si / n_w_si if n_w_si > 0 else float("nan"),
         "n_total": n_total, "n_clusters": n_cells, "B": B},
    ])


# ---------------------------------------------------------------------------
# PoC 3 — variance decomposition (legacy 3 model + 신규 extended model)
# ---------------------------------------------------------------------------

def _condition_4(variant: str) -> str:
    if variant.startswith("CaseB:"):
        return "CaseB"
    return variant


def _collapse_caseb(df: pd.DataFrame) -> pd.DataFrame:
    """CaseB 13 method 를 (cell, rep) 별 평균(log_ms)으로 접어 condition 4 levels 를 균형화.

    ★ Codex T4 fix — CaseB 는 method 13종이라 cell 당 baseline/B1/oracle 보다 약 13× 많은
    행을 가져 OLS/ANOVA 가 pseudo-replication 으로 condition 효과를 과가중·분산 과소추정한다.
    method 13종을 cell·rep 별 평균으로 접으면 4 condition 이 행 수 균형 (각 cell·rep 1행).
    ★ Codex 재검증 fix — injection-miss/timeout 으로 일부 method 가 빠진 (cell,rep) 은
    'CaseB=13 평균' 정의가 깨지므로(missingness 편향) method 완전 group 만 collapse 한다.
    """
    if "condition" not in df.columns or int((df["condition"] == "CaseB").sum()) == 0:
        return df
    caseb = df[df["condition"] == "CaseB"]
    other = df[df["condition"] != "CaseB"]
    expected = caseb["variant"].nunique()                  # 완전 method 수 (보통 13)
    counts = caseb.groupby(["cell", "rep"])["variant"].nunique()
    full_keys = counts[counts == expected].index.to_frame(index=False)
    n_partial = int((counts != expected).sum())
    if n_partial:
        print(f"[collapse] CaseB 부분 group {n_partial}개 제외 (method <{expected})")
    caseb = caseb.merge(full_keys, on=["cell", "rep"], how="inner")
    keep_first = ["query", "qid", "sel", "dataset", "sf", "phase", "condition",
                  "injection_fired", "n_timeout"]
    agg = (caseb.groupby(["cell", "rep"], as_index=False)
                 .agg({**{c: "first" for c in keep_first},
                       "exec_ms": "mean", "log_ms": "mean"}))
    agg["variant"] = "CaseB"
    return pd.concat([other, agg], ignore_index=True)


def _tag_phase(cell: str, parsed: dict) -> str:
    """cell parse 결과로 평면 라벨링.

    - phase2: DEEP sf=10 sel=0.001
    - phase3: DEEP sf=10 sel∈{0.01, 0.1}
    - phase4_extension: 그 외 모든 cell (sf=1·sf=100, 비-DEEP, 다중 벡터, 등)
    """
    if parsed.get("dataset") == "DEEP" and parsed.get("sf") == 10:
        if parsed.get("sel") == 0.001:
            return "phase2"
        if parsed.get("sel") in (0.01, 0.1):
            return "phase3"
    return "phase4_extension"


def build_long_df(results: list[dict]) -> pd.DataFrame:
    """raw JSON → tidy DataFrame (cell, query, qid, sel, dataset, sf, phase,
    variant, condition, rep, exec_ms, log_ms).

    legacy build_long_df 와 동일 base + dataset/sf/phase 컬럼 추가 (신규 모델 base).
    plan-invariant 평면 (DEEP sf=1) 도 raw 그대로 포함 — 모델 fit 시 보고 별도 분기.
    """
    rows = []
    for r in results:
        cell = cell_label(r)
        parsed = parse_cell(cell)
        phase_tag = _tag_phase(cell, parsed)
        for v in r["variants"]:
            lab = _variant_label(v)
            cond = _condition_4(lab)
            exec_ms = v.get("exec_ms") or []
            for i, ms in enumerate(exec_ms):
                if ms is None or ms <= 0:
                    continue
                rows.append({
                    "cell": cell,
                    "query": r["query"],
                    "qid": r["query_id"],
                    "sel": r["sel"],
                    "dataset": parsed["dataset"],
                    "sf": parsed["sf"],
                    "phase": phase_tag,
                    "variant": lab,
                    "condition": cond,
                    "rep": i,                       # 성공 run index — n_timeout=0 일 때만 측정 rep 과 일치
                    "exec_ms": float(ms),
                    "log_ms": float(np.log(ms)),
                    "injection_fired": bool(v.get("injection_fired", False)),
                    "n_timeout": int(v.get("n_timeout", 0)),
                })
    return pd.DataFrame(rows)


def _try_fit(formula: str, df: pd.DataFrame) -> tuple[sm.regression.linear_model.RegressionResults | None,
                                                       pd.DataFrame | None]:
    """모델 fit + ANOVA. 평면 1개 또는 dataset 1종이면 fit 불가 → (None, None).

    ★ Codex T4 fix — 분산분해 %는 가산적인 Type-I(순차) SS 로 산출한다. Type-III SS 는
    교호작용·불균형 설계에서 비가산이라 합이 총변동과 달라 100% 정규화가 부정확하다.
    각 factor 의 partial 검정 p 값은 Type-III 로 별도 병기(p_typ3).
    """
    try:
        model = smf.ols(formula, data=df).fit()
        a = anova_lm(model, typ=1)                    # 순차(Type-I) SS — 가산적
        a_clean = a.drop("Intercept", errors="ignore").copy()
        ss_total = a_clean["sum_sq"].sum()            # factor + Residual = 총변동
        a_clean["pct_ss"] = 100.0 * a_clean["sum_sq"] / ss_total
        try:                                          # partial 검정은 Type-III
            a3 = anova_lm(model, typ=3).drop("Intercept", errors="ignore")
            a_clean["p_typ3"] = a3["PR(>F)"]
        except Exception:
            a_clean["p_typ3"] = float("nan")
        return model, a_clean.reset_index().rename(columns={"index": "factor"})
    except Exception as e:
        print(f"[warn] 모델 fit 실패 — {formula}: {e}")
        return None, None


def poc3_variance_decomposition(results: list[dict]) -> dict:
    """legacy 3 model (cell×condition · 4 factor · no-baseline) + ★ extended model 4.

    extended 모델 (model4):
      log(exec_ms) ~ C(query) + C(qid) + C(sel) + C(dataset) + C(sf)
                     + C(condition) + C(query):C(condition) + C(sel):C(condition)
                     + C(dataset):C(condition) + C(sf):C(condition)

    dataset/sf factor 가 condition 효과의 modifier 인지 검증.
    """
    df = build_long_df(results)
    if df.empty:
        return {"empty": True}

    # ★ Codex T4 fix — 무효 측정 제외(주입 미발동 treatment·timeout 오염) + CaseB pseudo-replication 보정
    n_raw = len(df)
    df = df[(df["condition"] == "baseline") | df["injection_fired"]].copy()
    df = df[df["n_timeout"] == 0].copy()
    n_filtered = len(df)
    df = _collapse_caseb(df)
    print(f"[poc3] 측정 정합성 필터: {n_raw}행 → {n_filtered}행 "
          f"(주입 미발동·timeout 제거) → CaseB 집계 후 {len(df)}행")
    if df.empty:
        return {"empty": True}

    df["cell_str"] = df["cell"].astype("category")
    df["cond_str"] = df["condition"].astype("category")
    df["query_str"] = df["query"].astype("category")
    df["qid_str"] = df["qid"].astype("category")
    df["sel_str"] = df["sel"].astype("category")
    df["dataset_str"] = df["dataset"].astype("category")
    df["sf_str"] = df["sf"].astype("category")

    # 모델 1 — cell × condition (legacy carry)
    m1, a1 = _try_fit(
        "log_ms ~ C(cell_str, Sum) + C(cond_str, Sum) + "
        "C(cell_str, Sum):C(cond_str, Sum)",
        df,
    )

    # 모델 2 — query+qid+sel + condition 4 levels + 교호작용 (legacy carry)
    m2, a2 = _try_fit(
        "log_ms ~ C(query_str, Sum) + C(qid_str, Sum) + C(sel_str, Sum) + "
        "C(cond_str, Sum) + C(query_str, Sum):C(cond_str, Sum) + "
        "C(sel_str, Sum):C(cond_str, Sum)",
        df,
    )

    # 모델 3 — baseline 제외 (B1·CaseB·oracle 3 levels) (legacy carry)
    df3 = df[df["condition"] != "baseline"].copy()
    df3["cond_str"] = df3["condition"].astype("category")
    df3["query_str"] = df3["query"].astype("category")
    df3["qid_str"] = df3["qid"].astype("category")
    df3["sel_str"] = df3["sel"].astype("category")
    m3, a3 = _try_fit(
        "log_ms ~ C(query_str, Sum) + C(qid_str, Sum) + C(sel_str, Sum) + "
        "C(cond_str, Sum) + C(query_str, Sum):C(cond_str, Sum) + "
        "C(sel_str, Sum):C(cond_str, Sum)",
        df3,
    )

    # ★ 모델 4 — extended: dataset + sf factor 추가 (modifier 검증)
    # dataset 또는 sf 의 unique 가 1 이면 fit 불가 → 단일 평면 dry-run 안전 처리
    if df["dataset_str"].nunique() < 2 or df["sf_str"].nunique() < 2:
        m4, a4 = None, None
        print(f"[warn] 모델 4 (extended) skipped — dataset unique={df['dataset_str'].nunique()}, "
              f"sf unique={df['sf_str'].nunique()}")
    else:
        m4, a4 = _try_fit(
            "log_ms ~ C(query_str, Sum) + C(qid_str, Sum) + C(sel_str, Sum) + "
            "C(dataset_str, Sum) + C(sf_str, Sum) + "
            "C(cond_str, Sum) + C(query_str, Sum):C(cond_str, Sum) + "
            "C(sel_str, Sum):C(cond_str, Sum) + "
            "C(dataset_str, Sum):C(cond_str, Sum) + "
            "C(sf_str, Sum):C(cond_str, Sum)",
            df,
        )

    return {
        "empty": False,
        "model1_cell_condition": a1,
        "model2_factor_decomp": a2,
        "model3_no_baseline": a3,
        "model4_extended": a4,
        "n_obs": len(df),
        "n_obs_no_baseline": len(df3),
        "model1_r2": float(m1.rsquared) if m1 is not None else float("nan"),
        "model2_r2": float(m2.rsquared) if m2 is not None else float("nan"),
        "model3_r2": float(m3.rsquared) if m3 is not None else float("nan"),
        "model4_r2": float(m4.rsquared) if m4 is not None else float("nan"),
    }


# ---------------------------------------------------------------------------
# ★ 신규 — 평면 비교 표
# ---------------------------------------------------------------------------

def _recovery_rate(paired_sub: pd.DataFrame) -> float:
    """paired_stats sub 의 plan_recovered=True 비율 (%)."""
    n = len(paired_sub)
    if n == 0:
        return float("nan")
    n_true = int((paired_sub["plan_recovered"] == True).sum())  # noqa: E712
    return 100.0 * n_true / n


def plane_comparison_table(paired: pd.DataFrame) -> pd.DataFrame:
    """평면 (phase2 / phase3 / phase4_extension) × condition (anchor) × 지표 비교.

    지표 5종:
      · n_pairs — paired 행 수
      · plan_recovery_pct — plan_recovered=True 비율 (B1 anchor 기준 — oracle vs base 의 회복)
      · mean_abs_g — mean(|hedges_g|)
      · pct_large_g — |g|≥0.8 비율 (latency 격차 큰 cell 비율)
      · pct_p_holm_sig — p_holm<0.05 비율
    """
    out = []
    phases = sorted(paired["phase"].dropna().unique().tolist())
    anchors = ["baseline", "B1"]
    for phase in phases:
        for anchor in anchors:
            sub = paired[(paired["phase"] == phase) & (paired["anchor"] == anchor)].copy()
            n = len(sub)
            if n == 0:
                out.append({
                    "phase": phase, "anchor": anchor, "n_pairs": 0,
                    "plan_recovery_pct": float("nan"),
                    "mean_abs_g": float("nan"),
                    "pct_small_g": float("nan"),
                    "pct_medium_g": float("nan"),
                    "pct_large_g": float("nan"),
                    "pct_p_holm_sig": float("nan"),
                })
                continue
            sub["abs_g"] = sub["hedges_g"].abs()
            sub["g_band"] = pd.cut(sub["abs_g"],
                                    bins=[-0.001, 0.5, 0.8, np.inf],
                                    labels=["small", "medium", "large"])
            n_small = int((sub["g_band"] == "small").sum())
            n_med = int((sub["g_band"] == "medium").sum())
            n_lar = int((sub["g_band"] == "large").sum())
            n_sig = int((sub["p_holm"] < 0.05).sum())
            rec = _recovery_rate(sub)
            out.append({
                "phase": phase, "anchor": anchor, "n_pairs": n,
                "plan_recovery_pct": rec,
                "mean_abs_g": float(sub["abs_g"].mean()),
                "pct_small_g": 100.0 * n_small / n,
                "pct_medium_g": 100.0 * n_med / n,
                "pct_large_g": 100.0 * n_lar / n,
                "pct_p_holm_sig": 100.0 * n_sig / n,
            })
    return pd.DataFrame(out)


def dataset_comparison_table(paired: pd.DataFrame) -> pd.DataFrame:
    """dataset × sf × anchor 별 지표 (anchor=B1 기준).

    sf=100 미적재 dataset (WIKI/YFCC) 은 자연 결측 — NaN 으로 출력.
    DEEP sf=1 plan-invariant 도 NaN 처리 가능 (paired_stats 자체가 비어 있을 수 있음).
    """
    out = []
    datasets = sorted(paired["dataset"].dropna().unique().tolist())
    sfs = sorted(paired["sf"].dropna().unique().tolist())
    for ds in datasets:
        for sf in sfs:
            for anchor in ["B1"]:  # 평면 비교에서 B1 만 (baseline 은 정의상 large)
                sub = paired[(paired["dataset"] == ds) &
                              (paired["sf"] == sf) &
                              (paired["anchor"] == anchor)].copy()
                n = len(sub)
                # honest exception 처리
                missing_sf100 = (sf == 100 and ds in SF100_MISSING_DATASETS)
                plan_invariant = (ds == PLAN_INVARIANT_KEY[0] and sf == PLAN_INVARIANT_KEY[1])
                if n == 0:
                    note = ""
                    if missing_sf100:
                        note = "honest_exception_sf100_missing"
                    elif plan_invariant:
                        note = "plan_invariant_injection_miss"
                    out.append({
                        "dataset": ds, "sf": sf, "anchor": anchor,
                        "n_pairs": 0,
                        "plan_recovery_pct": float("nan"),
                        "mean_abs_g": float("nan"),
                        "pct_large_g": float("nan"),
                        "pct_p_holm_sig": float("nan"),
                        "note": note,
                    })
                    continue
                sub["abs_g"] = sub["hedges_g"].abs()
                n_lar = int((sub["abs_g"] >= 0.8).sum())
                n_sig = int((sub["p_holm"] < 0.05).sum())
                rec = _recovery_rate(sub)
                out.append({
                    "dataset": ds, "sf": sf, "anchor": anchor,
                    "n_pairs": n,
                    "plan_recovery_pct": rec,
                    "mean_abs_g": float(sub["abs_g"].mean()),
                    "pct_large_g": 100.0 * n_lar / n,
                    "pct_p_holm_sig": 100.0 * n_sig / n,
                    "note": "",
                })
    return pd.DataFrame(out)


def sf_scaling_table(paired: pd.DataFrame) -> pd.DataFrame:
    """sf scaling — sf=1 / 10 / 100 에서 B1 anchor 의 condition 효과 변화.

    가설: sf=1 (작은 테이블) → IndexScan 우회 → plan_recovery_pct 낮음
          sf=10 → 충분히 큰 테이블 → 회복률 ↑
          sf=100 → 더 큰 테이블 → 회복률 ↑↑ (또는 censoring 위험)
    """
    out = []
    sfs = sorted(paired["sf"].dropna().unique().tolist())
    for sf in sfs:
        for anchor in ["B1"]:
            sub = paired[(paired["sf"] == sf) & (paired["anchor"] == anchor)].copy()
            n = len(sub)
            n_datasets = sub["dataset"].nunique() if n > 0 else 0
            if n == 0:
                out.append({
                    "sf": sf, "anchor": anchor, "n_pairs": 0, "n_datasets": 0,
                    "plan_recovery_pct": float("nan"),
                    "mean_abs_g": float("nan"),
                    "pct_large_g": float("nan"),
                    "pct_p_holm_sig": float("nan"),
                })
                continue
            sub["abs_g"] = sub["hedges_g"].abs()
            n_lar = int((sub["abs_g"] >= 0.8).sum())
            n_sig = int((sub["p_holm"] < 0.05).sum())
            rec = _recovery_rate(sub)
            out.append({
                "sf": sf, "anchor": anchor, "n_pairs": n, "n_datasets": n_datasets,
                "plan_recovery_pct": rec,
                "mean_abs_g": float(sub["abs_g"].mean()),
                "pct_large_g": 100.0 * n_lar / n,
                "pct_p_holm_sig": 100.0 * n_sig / n,
            })
    return pd.DataFrame(out)


def censoring_summary(results: list[dict]) -> pd.DataFrame:
    """sf=100 censoring (statement_timeout 도달) — cell × variant 별 timeout 비율.

    raw JSON 의 `n_timeout` 컬럼 base. 보고서 §5.5 paragraph 의 censored ratio 정량.
    """
    rows = []
    for r in results:
        cell = cell_label(r)
        parsed = parse_cell(cell)
        if parsed.get("sf") != 100:
            continue  # sf=100 한정
        for v in r["variants"]:
            lab = _variant_label(v)
            exec_ms = v.get("exec_ms") or []
            n_timeout = int(v.get("n_timeout", 0))
            n_total = len(exec_ms) + n_timeout
            rate = (100.0 * n_timeout / n_total) if n_total > 0 else float("nan")
            rows.append({
                "cell": cell,
                "dataset": parsed["dataset"],
                "sf": parsed["sf"],
                "sel": parsed["sel"],
                "query": parsed["query"],
                "variant": lab,
                "n_timeout": n_timeout,
                "n_total": n_total,
                "timeout_rate_pct": rate,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 시각화 — legacy 2 figure + ★ 신규 3 figure
# ---------------------------------------------------------------------------

def fig_plan_level_g(paired: pd.DataFrame, out_dir: Path) -> None:
    """legacy carry — anchor=B1 의 |g| 분포 by plan_recovered."""
    sub = paired[paired["anchor"] == "B1"].copy()
    if sub.empty:
        print("[skip] fig_plan_level_g — anchor=B1 paired 비어 있음")
        return
    sub["abs_g"] = sub["hedges_g"].abs()
    sub["plan_status"] = sub["plan_recovered"].map(
        lambda v: "True" if v is True else ("False" if v is False else "N/A")
    )
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    groups = ["True", "False", "N/A"]
    data = [sub[sub["plan_status"] == g]["abs_g"].dropna().tolist() for g in groups]
    counts = [len(d) for d in data]
    positions = list(range(1, len(groups) + 1))
    bp = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True,
                    showmeans=True, meanline=False,
                    meanprops=dict(marker="D", markerfacecolor="white",
                                    markeredgecolor="black", markersize=6))
    colors = ["#3a8a4d", "#c54a3f", "#8a8a8a"]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.55)
    ax.axhline(0.5, color="#aaa", linestyle="--", linewidth=0.8)
    ax.axhline(0.8, color="#aaa", linestyle="--", linewidth=0.8)
    ax.text(len(groups) + 0.4, 0.5, "small/medium 경계", fontsize=8,
            color="#666", va="center")
    ax.text(len(groups) + 0.4, 0.8, "medium/large 경계", fontsize=8,
            color="#666", va="center")
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{g}\n(n={c})" for g, c in zip(groups, counts)])
    ax.set_ylabel("|Hedges' g|")
    ax.set_title("plan-level effect size 분층 — anchor=B1 의 |g| 분포 by plan 회복 여부 (3 평면 통합)")
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig_plan_level_g.{ext}", dpi=150)
    plt.close(fig)


def fig_variance_decomp(decomp: dict, out_dir: Path) -> None:
    """legacy carry — model2/model3 % SS bar chart."""
    if decomp.get("empty") or decomp["model2_factor_decomp"] is None or \
            decomp["model3_no_baseline"] is None:
        print("[skip] fig_variance_decomp — model 비어 있음")
        return
    factor_short = {
        "C(query_str, Sum)": "query",
        "C(qid_str, Sum)": "qid",
        "C(sel_str, Sum)": "sel",
        "C(dataset_str, Sum)": "dataset",
        "C(sf_str, Sum)": "sf",
        "C(cond_str, Sum)": "condition",
        "C(query_str, Sum):C(cond_str, Sum)": "query × condition",
        "C(sel_str, Sum):C(cond_str, Sum)": "sel × condition",
        "C(dataset_str, Sum):C(cond_str, Sum)": "dataset × condition",
        "C(sf_str, Sum):C(cond_str, Sum)": "sf × condition",
        "Residual": "Residual (rep 잔차)",
    }
    colors_map = {
        "query": "#1f6d92", "qid": "#2d8eaf", "sel": "#4cb1c4",
        "dataset": "#3a8a4d", "sf": "#7eb53a",
        "condition": "#c54a3f",
        "query × condition": "#e88a3a", "sel × condition": "#e8b13a",
        "dataset × condition": "#d96b87", "sf × condition": "#a874c0",
        "Residual (rep 잔차)": "#888",
    }

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 4.6))
    for ax, key, title in [
        (axes[0], "model2_factor_decomp",
         f"(a) 4 condition (baseline·B1·CaseB·oracle) — n={decomp['n_obs']:,}, "
         f"R²={decomp['model2_r2']:.3f}"),
        (axes[1], "model3_no_baseline",
         f"(b) baseline 제외 — n={decomp['n_obs_no_baseline']:,}, "
         f"R²={decomp['model3_r2']:.3f}"),
    ]:
        df = decomp[key].copy().sort_values("pct_ss", ascending=True)
        factors = df["factor"].tolist()
        pct = df["pct_ss"].tolist()
        labels = [factor_short.get(f, f) for f in factors]
        bar_colors = [colors_map.get(lab, "#555") for lab in labels]
        ypos = np.arange(len(labels))
        ax.barh(ypos, pct, color=bar_colors, alpha=0.85,
                edgecolor="#333", linewidth=0.6)
        max_pct = max(pct) if pct else 1.0
        for i, p in enumerate(pct):
            ax.text(p + max_pct * 0.01, i, f"{p:.1f}%",
                    va="center", fontsize=8.5)
        ax.set_yticks(ypos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("% of total SS (Type-I 순차)")
        ax.set_title(title, fontsize=10)
        ax.grid(True, axis="x", linestyle=":", alpha=0.4)
        ax.set_xlim(0, max_pct * 1.18)
    fig.suptitle("latency 분산 분해 — log(exec_ms) 두 모델 비교 (3 평면 통합)", fontsize=11)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig_variance_decomp.{ext}", dpi=150)
    plt.close(fig)


def fig_plane_comparison_g(paired: pd.DataFrame, out_dir: Path) -> None:
    """★ 신규 — 평면 별 |g| 분포 boxplot (anchor=B1, plane 라벨에 n 표시)."""
    sub = paired[paired["anchor"] == "B1"].copy()
    if sub.empty:
        print("[skip] fig_plane_comparison_g — anchor=B1 비어 있음")
        return
    sub["abs_g"] = sub["hedges_g"].abs()
    phases = ["phase2", "phase3", "phase4_extension"]
    data = []
    counts = []
    for p in phases:
        vals = sub[sub["phase"] == p]["abs_g"].dropna().tolist()
        data.append(vals)
        counts.append(len(vals))
    if all(c == 0 for c in counts):
        print("[skip] fig_plane_comparison_g — 모든 평면 비어 있음")
        return
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    positions = list(range(1, len(phases) + 1))
    bp = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True,
                    showmeans=True, meanline=False,
                    meanprops=dict(marker="D", markerfacecolor="white",
                                    markeredgecolor="black", markersize=6))
    colors = ["#2d8eaf", "#e88a3a", "#3a8a4d"]
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    ax.axhline(0.5, color="#aaa", linestyle="--", linewidth=0.8)
    ax.axhline(0.8, color="#aaa", linestyle="--", linewidth=0.8)
    ax.text(len(phases) + 0.4, 0.5, "small/medium", fontsize=8, color="#666", va="center")
    ax.text(len(phases) + 0.4, 0.8, "medium/large", fontsize=8, color="#666", va="center")
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{p}\n(n={c})" for p, c in zip(phases, counts)])
    ax.set_ylabel("|Hedges' g|")
    ax.set_title("평면 별 effect size 분포 — anchor=B1 의 |g| (phase2 carry · phase4_ext 일반화)")
    ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig_plane_comparison_g.{ext}", dpi=150)
    plt.close(fig)


def fig_dataset_sf_heatmap(comp: pd.DataFrame, out_dir: Path) -> None:
    """★ 신규 — dataset × sf 의 plan_recovery_pct heatmap.

    NaN (sf=100 미적재 또는 DEEP sf=1 plan-invariant) 은 회색 표기.
    """
    if comp.empty:
        print("[skip] fig_dataset_sf_heatmap — comp 비어 있음")
        return
    pivot = comp[comp["anchor"] == "B1"].pivot_table(
        index="dataset", columns="sf", values="plan_recovery_pct", aggfunc="first"
    )
    if pivot.empty:
        print("[skip] fig_dataset_sf_heatmap — pivot 비어 있음")
        return
    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    masked = np.ma.masked_invalid(pivot.values)
    cmap = plt.get_cmap("YlGn").copy()
    cmap.set_bad(color="#cccccc")
    im = ax.imshow(masked, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"sf={c}" for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            if np.isnan(val):
                ax.text(j, i, "—", ha="center", va="center", color="#666", fontsize=9)
            else:
                ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                        color="black" if val < 50 else "white", fontsize=9)
    ax.set_title("plan 회복률 (%) — dataset × sf (anchor=B1)")
    fig.colorbar(im, ax=ax, label="plan_recovery_pct")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig_dataset_sf_heatmap.{ext}", dpi=150)
    plt.close(fig)


def fig_variance_decomp_extended(decomp: dict, out_dir: Path) -> None:
    """★ 신규 — model4 (dataset/sf factor 포함) % SS bar chart."""
    if decomp.get("empty") or decomp.get("model4_extended") is None:
        print("[skip] fig_variance_decomp_extended — model4 비어 있음")
        return
    factor_short = {
        "C(query_str, Sum)": "query",
        "C(qid_str, Sum)": "qid",
        "C(sel_str, Sum)": "sel",
        "C(dataset_str, Sum)": "dataset",
        "C(sf_str, Sum)": "sf",
        "C(cond_str, Sum)": "condition",
        "C(query_str, Sum):C(cond_str, Sum)": "query × condition",
        "C(sel_str, Sum):C(cond_str, Sum)": "sel × condition",
        "C(dataset_str, Sum):C(cond_str, Sum)": "dataset × condition",
        "C(sf_str, Sum):C(cond_str, Sum)": "sf × condition",
        "Residual": "Residual (rep 잔차)",
    }
    colors_map = {
        "query": "#1f6d92", "qid": "#2d8eaf", "sel": "#4cb1c4",
        "dataset": "#3a8a4d", "sf": "#7eb53a",
        "condition": "#c54a3f",
        "query × condition": "#e88a3a", "sel × condition": "#e8b13a",
        "dataset × condition": "#d96b87", "sf × condition": "#a874c0",
        "Residual (rep 잔차)": "#888",
    }

    df = decomp["model4_extended"].copy().sort_values("pct_ss", ascending=True)
    factors = df["factor"].tolist()
    pct = df["pct_ss"].tolist()
    labels = [factor_short.get(f, f) for f in factors]
    bar_colors = [colors_map.get(lab, "#555") for lab in labels]
    ypos = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.barh(ypos, pct, color=bar_colors, alpha=0.85,
            edgecolor="#333", linewidth=0.6)
    max_pct = max(pct) if pct else 1.0
    for i, p in enumerate(pct):
        ax.text(p + max_pct * 0.01, i, f"{p:.1f}%", va="center", fontsize=8.5)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("% of total SS (Type-I 순차)")
    ax.set_title(f"latency 분산 분해 (확장) — log(exec_ms) ~ query + qid + sel + "
                  f"dataset + sf + condition + 교호작용\n"
                  f"n={decomp['n_obs']:,}, R²={decomp['model4_r2']:.3f}",
                  fontsize=10)
    ax.grid(True, axis="x", linestyle=":", alpha=0.4)
    ax.set_xlim(0, max_pct * 1.18)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig_variance_decomp_extended.{ext}", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 환각 회피 sanity check + summary.md
# ---------------------------------------------------------------------------

def sanity_check(poc1: pd.DataFrame, poc2: pd.DataFrame, poc3: dict,
                  paired: pd.DataFrame, plane: pd.DataFrame,
                  dscmp: pd.DataFrame) -> list[str]:
    msgs = []
    # 평면 별 행 수
    phases = paired["phase"].value_counts(dropna=False).to_dict()
    msgs.append(f"paired 평면 분포: {phases}")
    # legacy phase2/phase3 anchor 합
    p23 = paired[paired["phase"].isin(["phase2", "phase3"])]
    n_b1_23 = int((p23["anchor"] == "B1").sum())
    n_base_23 = int((p23["anchor"] == "baseline").sum())
    msgs.append(f"legacy carry (phase2+phase3) — anchor=B1 합 = {n_b1_23} (기대 280) · "
                 f"baseline 합 = {n_base_23} (기대 300)")
    # §5.4 phase2 only
    p2 = paired[paired["phase"] == "phase2"]
    n_b1_p2 = int((p2["anchor"] == "B1").sum())
    n_small_b1_p2 = int((p2[p2["anchor"] == "B1"]["hedges_g"].abs() < 0.5).sum())
    msgs.append(f"§5.4 carry (phase2 only) — anchor=B1 = {n_b1_p2} (기대 168) · "
                 f"|g|<0.5 = {n_small_b1_p2} (기대 146 = 86.9%)")
    # phase4_extension 행 수
    p4 = paired[paired["phase"] == "phase4_extension"]
    msgs.append(f"phase4_extension — paired 행 수 = {len(p4)} "
                 f"(0 = 측정 raw 미도착 또는 미적재)")
    # PoC 3 % SS 합
    for key, expected in [("model1_cell_condition", 100.0),
                          ("model2_factor_decomp", 100.0),
                          ("model3_no_baseline", 100.0),
                          ("model4_extended", 100.0)]:
        a = poc3.get(key)
        if a is None:
            msgs.append(f"sanity: PoC 3 {key} — fit 안 됨 (skip)")
            continue
        s = float(a["pct_ss"].sum())
        msgs.append(f"sanity: PoC 3 {key} % SS 합 = {s:.2f}% (기대 {expected}%)")
    # 평면 비교 표 — n_pairs 합 검증
    n_total_plane = int(plane["n_pairs"].sum())
    msgs.append(f"plane_comparison: n_pairs 총합 = {n_total_plane} = anchor 2 (baseline + B1) × "
                 f"평면 별 paired")
    # honest exception 검증
    deep_sf1 = dscmp[(dscmp["dataset"] == "DEEP") & (dscmp["sf"] == 1)]
    if not deep_sf1.empty:
        note = deep_sf1["note"].iloc[0]
        n = int(deep_sf1["n_pairs"].iloc[0])
        msgs.append(f"honest exception: DEEP sf=1 — n_pairs={n}, note={note} "
                     f"(prescan carry: plan-invariant 16 variant injection_fired=False)")
    for ds in SF100_MISSING_DATASETS:
        sub = dscmp[(dscmp["dataset"] == ds) & (dscmp["sf"] == 100)]
        if not sub.empty:
            note = sub["note"].iloc[0]
            n = int(sub["n_pairs"].iloc[0])
            msgs.append(f"honest exception: {ds} sf=100 — n_pairs={n}, note={note}")
    return msgs


def write_summary_md(poc1: pd.DataFrame, poc2: pd.DataFrame, poc3: dict,
                      plane: pd.DataFrame, dscmp: pd.DataFrame,
                      sfscale: pd.DataFrame, censor: pd.DataFrame,
                      sanity: list[str], out_path: Path) -> None:
    lines = []
    lines.append("# Phase 6 §6.4 통계 후속 PoC — **평면 확장 본** 실측 결과 요약")
    lines.append("")
    lines.append("작성: 2026-05-21 KST · 스크립트 `_internal/scripts/stats_poc_6_4_extended.py`")
    lines.append("")
    lines.append("**PoC 평면**: phase2 (DEEP sf=10 sel=0.001 12 cell) + phase3 "
                  "(DEEP sf=10 sel=0.01·0.1 carry-over 8 cell) + "
                  "**phase4_extension (단일 5 × sf=1/10 + 다중 2 sf=10 + sf=100 단일 3 부분)**.")
    lines.append("§5.4 보고서 본문의 168/180/146 수치는 phase2 만의 부분 평면이며, 본 확장 PoC 는 "
                  "3 평면 통합에서 평면·dataset·sf 일반화를 검증한다.")
    lines.append("")
    lines.append("## 0. 환각 회피 sanity")
    lines.append("")
    for m in sanity:
        lines.append(f"- {m}")
    lines.append("")
    lines.append("## 1. PoC 1 — plan-level effect size 분층 (legacy carry, 3 평면 통합)")
    lines.append("")
    lines.append("| anchor | plan_recovered | n | small (|g|<0.5) | medium | large (|g|≥0.8) | mean |g| | p_holm<0.05 |")
    lines.append("|---|---|--:|--:|--:|--:|--:|--:|")
    for _, row in poc1.iterrows():
        if row["n"] == 0:
            continue
        lines.append(
            f"| {row['anchor']} | {row['plan_recovered']} | {row['n']} | "
            f"{row['n_small']} ({row['pct_small']:.1f}%) | "
            f"{row['n_medium']} ({row['pct_medium']:.1f}%) | "
            f"{row['n_large']} ({row['pct_large']:.1f}%) | "
            f"{row['mean_abs_g']:.3f} | "
            f"{row['n_p_holm_sig']} ({row['pct_p_holm_sig']:.1f}%) |"
        )
    lines.append("")
    lines.append("## 2. PoC 2 — cluster paired bootstrap (B=2,000, cell 단위 resample)")
    lines.append("")
    lines.append("| metric | point | naïve 95% CI | cluster 95% CI | width ratio (cluster/naïve) |")
    lines.append("|---|--:|--:|--:|--:|")
    for _, row in poc2.iterrows():
        lines.append(
            f"| {row['metric']} | {row['point_estimate']:.3f} | "
            f"[{row['naive_ci_lo']:.3f}, {row['naive_ci_hi']:.3f}] | "
            f"[{row['cluster_ci_lo']:.3f}, {row['cluster_ci_hi']:.3f}] | "
            f"{row['width_ratio_cluster_over_naive']:.3f}× |"
        )
    lines.append("")
    lines.append("## 3. PoC 3 — variance decomposition "
                 "(% SS = Type-I 순차 SS · p = Type-III partial, sum-coded contrasts)")
    lines.append("")
    r2s = (f"R² — 모델 1 (cell × condition) = {poc3.get('model1_r2', float('nan')):.3f} · "
           f"모델 2 (factor·4 cond) = {poc3.get('model2_r2', float('nan')):.3f} · "
           f"모델 3 (no baseline) = {poc3.get('model3_r2', float('nan')):.3f} · "
           f"모델 4 (extended, dataset+sf 추가) = {poc3.get('model4_r2', float('nan')):.3f}")
    lines.append(f"n_obs (4 condition) = {poc3.get('n_obs', 0):,} · "
                  f"n_obs (no baseline) = {poc3.get('n_obs_no_baseline', 0):,}")
    lines.append(r2s)
    lines.append("")
    for tag, key, header in [
        ("모델 2 — query·qid·sel + 4 condition + 교호작용", "model2_factor_decomp", "legacy"),
        ("모델 3 — baseline 제외 (B1·CaseB·oracle)", "model3_no_baseline", "legacy"),
        ("★ 모델 4 (extended) — dataset/sf factor 추가", "model4_extended", "extended"),
        ("모델 1 — cell × condition (단순 분해)", "model1_cell_condition", "legacy"),
    ]:
        a = poc3.get(key)
        lines.append(f"**{tag}** ({header})")
        lines.append("")
        if a is None:
            lines.append("_(fit 실패 또는 dataset/sf unique <2 — skip)_")
            lines.append("")
            continue
        lines.append("| factor | df | SS(Type-I) | F | p(Type-III) | % SS |")
        lines.append("|---|--:|--:|--:|--:|--:|")
        for _, row in a.iterrows():
            lines.append(
                f"| {row['factor']} | {row['df']:.0f} | {row['sum_sq']:.3f} | "
                f"{row.get('F', float('nan')):.3f} | "
                f"{row.get('p_typ3', float('nan')):.3e} | "
                f"{row['pct_ss']:.2f}% |"
            )
        lines.append("")
    lines.append("## 4. ★ 신규 — 평면 비교 표 (phase2 vs phase3 vs phase4_extension)")
    lines.append("")
    lines.append("| phase | anchor | n_pairs | plan_recovery_pct | mean |g| | small% | medium% | large% | p_holm<0.05% |")
    lines.append("|---|---|--:|--:|--:|--:|--:|--:|--:|")
    for _, row in plane.iterrows():
        lines.append(
            f"| {row['phase']} | {row['anchor']} | {row['n_pairs']} | "
            f"{row['plan_recovery_pct']:.1f}% | {row['mean_abs_g']:.3f} | "
            f"{row['pct_small_g']:.1f}% | {row['pct_medium_g']:.1f}% | "
            f"{row['pct_large_g']:.1f}% | {row['pct_p_holm_sig']:.1f}% |"
        )
    lines.append("")
    lines.append("## 5. ★ 신규 — dataset × sf 비교 표 (anchor=B1)")
    lines.append("")
    lines.append("| dataset | sf | n_pairs | plan_recovery_pct | mean |g| | large% | p_holm<0.05% | note |")
    lines.append("|---|---|--:|--:|--:|--:|--:|---|")
    for _, row in dscmp.iterrows():
        if row["n_pairs"] == 0:
            lines.append(
                f"| {row['dataset']} | {row['sf']} | 0 | — | — | — | — | "
                f"{row['note']} |"
            )
        else:
            lines.append(
                f"| {row['dataset']} | {row['sf']} | {row['n_pairs']} | "
                f"{row['plan_recovery_pct']:.1f}% | {row['mean_abs_g']:.3f} | "
                f"{row['pct_large_g']:.1f}% | {row['pct_p_holm_sig']:.1f}% | "
                f"{row['note']} |"
            )
    lines.append("")
    lines.append("## 6. ★ 신규 — sf scaling 표 (sf=1·10·100 condition 효과 변화, anchor=B1)")
    lines.append("")
    lines.append("| sf | n_datasets | n_pairs | plan_recovery_pct | mean |g| | large% | p_holm<0.05% |")
    lines.append("|---|--:|--:|--:|--:|--:|--:|")
    for _, row in sfscale.iterrows():
        if row["n_pairs"] == 0:
            lines.append(f"| {row['sf']} | 0 | 0 | — | — | — | — |")
        else:
            lines.append(
                f"| {row['sf']} | {row['n_datasets']} | {row['n_pairs']} | "
                f"{row['plan_recovery_pct']:.1f}% | {row['mean_abs_g']:.3f} | "
                f"{row['pct_large_g']:.1f}% | {row['pct_p_holm_sig']:.1f}% |"
            )
    lines.append("")
    lines.append("## 7. ★ 신규 — sf=100 censoring (statement_timeout 180s 도달 비율)")
    lines.append("")
    if censor.empty:
        lines.append("_(sf=100 raw 미도착 또는 censored=0 — 측정 후 갱신)_")
    else:
        agg = censor.groupby(["dataset", "sf", "sel"]).agg(
            n_cells=("cell", "nunique"),
            n_variants=("variant", "count"),
            mean_timeout_rate=("timeout_rate_pct", "mean"),
            max_timeout_rate=("timeout_rate_pct", "max"),
        ).reset_index()
        lines.append("| dataset | sf | sel | n_cells | n_variants | mean_timeout_rate | max_timeout_rate |")
        lines.append("|---|---|---|--:|--:|--:|--:|")
        for _, row in agg.iterrows():
            lines.append(
                f"| {row['dataset']} | {row['sf']} | {row['sel']} | "
                f"{row['n_cells']} | {row['n_variants']} | "
                f"{row['mean_timeout_rate']:.1f}% | {row['max_timeout_rate']:.1f}% |"
            )
    lines.append("")
    lines.append("## 8. 평면 일반화 결론 (template — 측정 결과 도착 후 갱신)")
    lines.append("")
    lines.append("- **DEEP sf=10 단일 평면 결론 (carry)**: 94.9% plan 회복 · 86.9% small effect · "
                  "model3 condition % SS = 0.00% (p=0.866) → latency 동등성 입증.")
    lines.append("- **평면 확장 (phase4_extension) 일반화**: (측정 도착 후) "
                  "단일 5 dataset · sf=1·10 + 다중 2 + sf=100 부분에서 동일 효과 입증 또는 "
                  "조건부 효과 (sf×condition 또는 dataset×condition 교호작용 검증).")
    lines.append("- **honest exception**: DEEP sf=1 plan-invariant · WIKI/YFCC sf=100 미적재 · "
                  "DEEP+CC3M 4건 한계 · sf=100 censoring 비율 — 각각 별도 paragraph.")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="raw JSON 없어도 import/함수 정의만 검증 (실제 실행 X)")
    parser.add_argument("--no-phase4", action="store_true",
                        help="phase4_extension 평면 제외 (legacy 평면만 분석)")
    args = parser.parse_args(argv)

    if args.dry_run:
        print("[dry-run] script import + 함수 정의 OK. raw 분석 skip.")
        print(f"  PHASE2_DIR exists: {PHASE2_DIR.exists()}")
        print(f"  PHASE3_DIR exists: {PHASE3_DIR.exists()}")
        print(f"  PHASE4_EXT_DIR exists: {PHASE4_EXT_DIR.exists()}")
        print(f"  PAIRED_P2 exists: {PAIRED_P2.exists()}")
        print(f"  PAIRED_P3 exists: {PAIRED_P3.exists()}")
        print(f"  PAIRED_P4 exists: {PAIRED_P4.exists()}")
        print(f"  function registry:")
        for name in ["parse_cell", "load_paired", "load_all_results",
                     "compute_plan_status", "build_long_df",
                     "poc1_plan_level_effect_size", "poc2_cluster_bootstrap",
                     "poc3_variance_decomposition", "plane_comparison_table",
                     "dataset_comparison_table", "sf_scaling_table",
                     "censoring_summary", "fig_plan_level_g",
                     "fig_variance_decomp", "fig_plane_comparison_g",
                     "fig_dataset_sf_heatmap", "fig_variance_decomp_extended",
                     "sanity_check", "write_summary_md"]:
            f = globals().get(name)
            print(f"    · {name}: {'OK' if callable(f) else 'MISSING'}")
        return 0

    CSV_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[1/7] raw JSON 로드 — phase2 + phase3 + phase4_extension")
    r2, r3, r4 = load_all_results()
    if args.no_phase4:
        r4 = []
    results = r2 + r3 + r4
    print(f"  cells: phase2={len(r2)}, phase3={len(r3)}, "
           f"phase4_extension={len(r4)}, total={len(results)}")

    print(f"[2/7] paired_stats 로드 + plan_status merge (3 평면)")
    paired = load_paired(include_phase4=not args.no_phase4)
    plan_status = compute_plan_status(results)
    paired = paired.merge(plan_status, on=["cell", "variant"], how="left")
    # ★ Codex 재검증 fix — pairing-invalid(timeout 으로 rep 어긋남) 행 제외.
    # paired 통계가 NaN 인 행을 poc1/poc2/평면표가 분모에 넣어 무효과·비유의로 오집계하던 문제.
    if "pairing_valid" in paired.columns:
        n_before = len(paired)
        paired = paired[paired["pairing_valid"].ne(False)].copy()
        if n_before - len(paired):
            print(f"  pairing-invalid(timeout) 제외: {n_before - len(paired)}행")
    print(f"  paired_stats rows: {len(paired)}")
    if not paired.empty:
        print(f"  plan_recovered 라벨 분포: "
               f"{paired['plan_recovered'].value_counts(dropna=False).to_dict()}")
        print(f"  phase 분포: {paired['phase'].value_counts(dropna=False).to_dict()}")

    print(f"[3/7] PoC 1 — plan-level effect size 분층 (legacy)")
    poc1 = poc1_plan_level_effect_size(paired)
    poc1.to_csv(CSV_DIR / "plan_level_effect_size.csv", index=False)
    print(poc1.to_string(index=False))

    print(f"\n[4/7] PoC 2 — cluster paired bootstrap (B={BOOTSTRAP_B})")
    poc2 = poc2_cluster_bootstrap(paired, B=BOOTSTRAP_B, seed=SEED)
    poc2.to_csv(CSV_DIR / "cluster_bootstrap.csv", index=False)
    print(poc2.to_string(index=False))

    print(f"\n[5/7] PoC 3 — variance decomposition (legacy 3 model + ★ extended model 4)")
    poc3 = poc3_variance_decomposition(results)
    if not poc3.get("empty"):
        for key, fname in [("model1_cell_condition", "variance_decomp_model1.csv"),
                            ("model2_factor_decomp", "variance_decomp.csv"),
                            ("model3_no_baseline", "variance_decomp_no_baseline.csv"),
                            ("model4_extended", "variance_decomp_extended.csv")]:
            a = poc3.get(key)
            if a is not None:
                a.to_csv(CSV_DIR / fname, index=False)
        print(f"  n_obs={poc3['n_obs']:,} · n_obs_no_baseline={poc3['n_obs_no_baseline']:,}")
        print(f"  R²: m1={poc3['model1_r2']:.3f} · m2={poc3['model2_r2']:.3f} · "
               f"m3={poc3['model3_r2']:.3f} · m4={poc3['model4_r2']:.3f}")
        if poc3.get("model4_extended") is not None:
            print(f"  [model4 extended] dataset/sf factor 추가:")
            print(poc3["model4_extended"].to_string(index=False))

    print(f"\n[6/7] ★ 신규 — 평면 비교 + dataset 비교 + sf scaling + censoring 표")
    plane = plane_comparison_table(paired)
    dscmp = dataset_comparison_table(paired)
    sfscale = sf_scaling_table(paired)
    censor = censoring_summary(results)
    plane.to_csv(CSV_DIR / "plane_comparison.csv", index=False)
    dscmp.to_csv(CSV_DIR / "dataset_comparison.csv", index=False)
    sfscale.to_csv(CSV_DIR / "sf_scaling.csv", index=False)
    censor.to_csv(CSV_DIR / "censoring_summary.csv", index=False)
    print(f"  plane_comparison rows: {len(plane)}")
    print(f"  dataset_comparison rows: {len(dscmp)}")
    print(f"  sf_scaling rows: {len(sfscale)}")
    print(f"  censoring rows (sf=100 only): {len(censor)}")

    print(f"\n[7/7] figure 생성 (legacy 2 + ★ 신규 3)")
    fig_plan_level_g(paired, FIG_DIR)
    fig_variance_decomp(poc3, FIG_DIR)
    fig_plane_comparison_g(paired, FIG_DIR)
    fig_dataset_sf_heatmap(dscmp, FIG_DIR)
    fig_variance_decomp_extended(poc3, FIG_DIR)
    print(f"  saved → {FIG_DIR}")

    print(f"\nsanity check")
    sanity = sanity_check(poc1, poc2, poc3, paired, plane, dscmp)
    for m in sanity:
        print(f"  {m}")

    write_summary_md(poc1, poc2, poc3, plane, dscmp, sfscale, censor, sanity,
                     CSV_DIR / "summary.md")
    print(f"\nsummary.md → {CSV_DIR / 'summary.md'}")
    print(f"\n완료 — 산출 디렉토리:")
    print(f"  · {CSV_DIR}/")
    print(f"  · {FIG_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
