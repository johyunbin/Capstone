#!/usr/bin/env python3
"""
stats_supplement_v12_compute.py — REPORT v12 §9 item (7) 통계 보완 4건

(a) BH-FDR 다중검정 보정: cell별·method별로 family 분할 재집계
(b) 효과크기 paired 버전: Cliff's δ paired, Hedges' g paired (correlated-design)
(c) Wilcoxon p값 해상도: n=10 → 최소 p ≈ 1/1024 정량화
(d) cell-weighted 재집계: file-weighted headline 대비 검증

★ 모든 수치 parquet 직접 재계산. headline = K=10 paired 120건 제외 1240건.
입력: paired_delta_v12.parquet (1360), aggregated_v12_full.parquet (1444)
출력: stdout (stats_supplement_v12_5_17.md 작성용 raw)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[3]
PAIRED = REPO / "_internal" / "cache" / "rq3" / "paired_delta_v12.parquet"
AGG = REPO / "_internal" / "cache" / "rq3" / "aggregated_v12_full.parquet"

CLIFF_LARGE = 0.474
CLIFF_MED = 0.330
CLIFF_SMALL = 0.147


# ============================================================
# 공통 — BH-FDR
# ============================================================
def bh_fdr(pvals):
    """Benjamini-Hochberg FDR. analyze_paper_exact.py 와 동일 구현."""
    pvals = np.array(pvals, dtype=float)
    n = len(pvals)
    finite_mask = np.isfinite(pvals)
    p_finite = pvals[finite_mask]
    n_finite = len(p_finite)
    if n_finite == 0:
        return np.full(n, np.nan)
    order = np.argsort(p_finite)
    ranks = np.empty(n_finite, dtype=int)
    ranks[order] = np.arange(1, n_finite + 1)
    p_adj = p_finite * n_finite / ranks
    p_adj_sorted = p_adj[order]
    for i in range(n_finite - 2, -1, -1):
        p_adj_sorted[i] = min(p_adj_sorted[i], p_adj_sorted[i + 1])
    p_adj[order] = p_adj_sorted
    p_adj = np.clip(p_adj, 0, 1)
    out = np.full(n, np.nan)
    out[finite_mask] = p_adj
    return out


# ============================================================
# 데이터 로드 + B1/CaseB trial 재페어
# ============================================================
def k_norm(k):
    return 20 if (k is None or pd.isna(k)) else int(k)


def load():
    dfp = pd.read_parquet(PAIRED)
    agg = pd.read_parquet(AGG)
    return dfp, agg


def build_paired_trials(agg):
    """각 paired 비교의 (b1_trials, cb_trials) 재구성.
    paired_delta_v12.py 의 pairing 규칙과 동일하게 재현."""
    b1 = agg[agg["mode"] == "B1"].copy()
    cb = agg[agg["mode"] == "CaseB"].copy()
    b1_lut = {}
    for _, r in b1.iterrows():
        key = (r["cell"], r["sel"], k_norm(r["K"]))
        b1_lut[key] = json.loads(r["trial_qe_list"])
    recs = []
    for _, r in cb.iterrows():
        kn = k_norm(r["K"])
        if (r["cell"], r["sel"], kn) in b1_lut:
            b1t = b1_lut[(r["cell"], r["sel"], kn)]
            pmode = "exact"
        elif (r["cell"], r["sel"], 20) in b1_lut:
            b1t = b1_lut[(r["cell"], r["sel"], 20)]
            pmode = "fallback_K20"
        else:
            continue
        recs.append({
            "cell": r["cell"], "method": r["method"], "paradigm": r["paradigm"],
            "sel": r["sel"], "K_norm": kn, "single_multi": r["single_multi"],
            "pairing": pmode,
            "b1_trials": np.array(b1t, dtype=float),
            "cb_trials": np.array(json.loads(r["trial_qe_list"]), dtype=float),
        })
    return pd.DataFrame(recs)


# ============================================================
# (b) paired 효과크기
# ============================================================
def cliffs_delta_independent(b1, ca):
    """기존 (REPORT v12 보고치) — 독립표본 all-pairs."""
    b1 = b1[np.isfinite(b1)]
    ca = ca[np.isfinite(ca)]
    if len(b1) == 0 or len(ca) == 0:
        return np.nan
    gt = int(np.sum(b1[:, None] > ca[None, :]))
    lt = int(np.sum(b1[:, None] < ca[None, :]))
    return (gt - lt) / (len(b1) * len(ca))


def cliffs_delta_paired(b1, ca):
    """paired Cliff's δ — 같은 trial index 끼리만 비교 (n쌍).
    δ_paired = (#{b1_i > ca_i} − #{b1_i < ca_i}) / n.
    POSITIVE = CaseB 우위 (b1 > ca = Q-error 더 작음)."""
    finite = np.isfinite(b1) & np.isfinite(ca)
    b1, ca = b1[finite], ca[finite]
    n = len(b1)
    if n == 0:
        return np.nan
    gt = int(np.sum(b1 > ca))
    lt = int(np.sum(b1 < ca))
    return (gt - lt) / n


def hedges_g_independent(b1, ca):
    """기존 (REPORT v12 보고치) — pooled-SD 독립표본."""
    b1 = b1[np.isfinite(b1)]
    ca = ca[np.isfinite(ca)]
    if len(b1) < 2 or len(ca) < 2:
        return np.nan
    pooled_sd = np.sqrt(((len(b1) - 1) * b1.var(ddof=1)
                         + (len(ca) - 1) * ca.var(ddof=1))
                        / (len(b1) + len(ca) - 2))
    if pooled_sd == 0:
        return np.nan
    d = (ca.mean() - b1.mean()) / pooled_sd
    n = len(b1) + len(ca)
    j = 1 - 3 / (4 * n - 9)
    return d * j


def hedges_g_paired(b1, ca):
    """paired Hedges' g_av — Cohen's d_av (Lakens 2013) + Hedges 소표본 보정.
    d_av = mean(diff) / pooled_sd, pooled_sd = sqrt((sd_b1^2 + sd_ca^2)/2).
    correlated design 이지만 effect-size unit 은 raw SD 로 유지하여
    독립표본 g 와 직접 비교 가능 (Lakens 2013 권장 d_av).
    NEGATIVE = CaseB 우위 (ca < b1).
    소표본 보정 J 는 paired df = n-1 기준."""
    finite = np.isfinite(b1) & np.isfinite(ca)
    b1, ca = b1[finite], ca[finite]
    n = len(b1)
    if n < 2:
        return np.nan
    sd1 = b1.var(ddof=1)
    sd2 = ca.var(ddof=1)
    pooled_sd = np.sqrt((sd1 + sd2) / 2.0)
    if pooled_sd == 0:
        return np.nan
    d_av = (ca.mean() - b1.mean()) / pooled_sd
    df = n - 1
    j = 1 - 3 / (4 * df - 1)  # Hedges 보정, paired df 기준
    return d_av * j


def hedges_g_paired_drm(b1, ca):
    """참고 — d_rm (repeated measures, correlation 보정).
    d_rm = d_av * sqrt(2(1-r)). r = trial 간 Pearson 상관.
    correlation 이 높으면 d_rm < d_av. 보고용 참고치."""
    finite = np.isfinite(b1) & np.isfinite(ca)
    b1, ca = b1[finite], ca[finite]
    n = len(b1)
    if n < 3:
        return np.nan, np.nan
    sd1 = b1.var(ddof=1)
    sd2 = ca.var(ddof=1)
    pooled_sd = np.sqrt((sd1 + sd2) / 2.0)
    if pooled_sd == 0:
        return np.nan, np.nan
    if b1.std() == 0 or ca.std() == 0:
        r = np.nan
    else:
        r = np.corrcoef(b1, ca)[0, 1]
    d_av = (ca.mean() - b1.mean()) / pooled_sd
    if not np.isfinite(r):
        return np.nan, r
    d_rm = d_av * np.sqrt(2 * (1 - r))
    df = n - 1
    j = 1 - 3 / (4 * df - 1)
    return d_rm * j, r


# ============================================================
def pct(x, n):
    return f"{100*x/n:.1f}%" if n else "—"


def main():
    dfp, agg = load()
    pt = build_paired_trials(agg)
    # paired_delta_v12.parquet 와 정렬 (같은 1360건)
    assert len(pt) == len(dfp), f"row mismatch {len(pt)} vs {len(dfp)}"

    # paired effect size 재계산
    pt["cliff_indep"] = pt.apply(
        lambda r: cliffs_delta_independent(r["b1_trials"], r["cb_trials"]), axis=1)
    pt["cliff_paired"] = pt.apply(
        lambda r: cliffs_delta_paired(r["b1_trials"], r["cb_trials"]), axis=1)
    pt["g_indep"] = pt.apply(
        lambda r: hedges_g_independent(r["b1_trials"], r["cb_trials"]), axis=1)
    pt["g_paired_av"] = pt.apply(
        lambda r: hedges_g_paired(r["b1_trials"], r["cb_trials"]), axis=1)
    drm = pt.apply(lambda r: hedges_g_paired_drm(r["b1_trials"], r["cb_trials"]),
                   axis=1)
    pt["g_paired_rm"] = [x[0] for x in drm]
    pt["trial_corr"] = [x[1] for x in drm]

    # delta + wilcoxon 은 paired_delta_v12.parquet 에서 직접 가져옴 (정렬 일치 확인)
    # merge key 로 정합
    keycols = ["cell", "method", "sel", "K_norm"]
    m = dfp[keycols + ["delta_pct_mean", "delta_pct_median",
                       "wilcoxon_p", "wilcoxon_p_greater", "pairing"]].copy()
    pt2 = pt.merge(m, on=keycols + ["pairing"], how="left",
                   suffixes=("", "_dfp"))
    assert pt2["delta_pct_mean"].notna().all(), "merge failed"
    assert len(pt2) == len(dfp)

    # K=10 제외 마스크 (headline)
    pt2["k10"] = pt2["K_norm"] == 10
    H = pt2[~pt2["k10"]].copy()   # 1240 headline
    F = pt2.copy()                 # 1360 full

    print("=" * 70)
    print("DATA CHECK")
    print("=" * 70)
    print(f"full paired: {len(F)}  headline (K10 excl): {len(H)}  K10: {pt2['k10'].sum()}")
    print(f"headline better: {(H['delta_pct_mean']<0).sum()}/{len(H)} = "
          f"{100*(H['delta_pct_mean']<0).mean():.4f}%")
    print(f"headline mean delta: {H['delta_pct_mean'].mean():.4f}  "
          f"median: {H['delta_pct_mean'].median():.4f}")
    print()

    # ========================================================
    # (a) BH-FDR family 분할
    # ========================================================
    print("=" * 70)
    print("(a) BH-FDR family 분할 재집계")
    print("=" * 70)
    # one-sided greater p values
    for scope_name, scope in [("HEADLINE (K10 excl, n=1240)", H),
                              ("FULL (K10 incl, n=1360)", F)]:
        s = scope.copy()
        # 1) 단일 family (현행)
        s["padj_single"] = bh_fdr(s["wilcoxon_p_greater"].values)
        # 2) cell 별 family
        s["padj_bycell"] = np.nan
        for cell, idx in s.groupby("cell").groups.items():
            s.loc[idx, "padj_bycell"] = bh_fdr(
                s.loc[idx, "wilcoxon_p_greater"].values)
        # 3) method 별 family
        s["padj_bymethod"] = np.nan
        for mth, idx in s.groupby("method").groups.items():
            s.loc[idx, "padj_bymethod"] = bh_fdr(
                s.loc[idx, "wilcoxon_p_greater"].values)
        # 4) (cell, method) 별 family — 가장 fine (각 family = sel×K 조합)
        s["padj_bycellmethod"] = np.nan
        for (cl, mth), idx in s.groupby(["cell", "method"]).groups.items():
            s.loc[idx, "padj_bycellmethod"] = bh_fdr(
                s.loc[idx, "wilcoxon_p_greater"].values)
        # raw uncorrected
        n = len(s)
        better = s["delta_pct_mean"] < 0
        raw_sig = ((better) & (s["wilcoxon_p_greater"] < 0.05)).sum()
        single_sig = ((better) & (s["padj_single"] < 0.05)).sum()
        cell_sig = ((better) & (s["padj_bycell"] < 0.05)).sum()
        meth_sig = ((better) & (s["padj_bymethod"] < 0.05)).sum()
        cm_sig = ((better) & (s["padj_bycellmethod"] < 0.05)).sum()
        print(f"\n  [{scope_name}]")
        print(f"   family 분할         | 유의 우월(better & p_adj<0.05) | 비율")
        print(f"   raw (보정 없음)      | {raw_sig:5d} / {n} | {pct(raw_sig,n)}")
        print(f"   단일 family (현행)   | {single_sig:5d} / {n} | {pct(single_sig,n)}")
        n_cell = s['cell'].nunique()
        n_meth = s['method'].nunique()
        n_cm = s.groupby(['cell','method']).ngroups
        print(f"   cell별 ({n_cell} family)  | {cell_sig:5d} / {n} | {pct(cell_sig,n)}")
        print(f"   method별 ({n_meth} family)| {meth_sig:5d} / {n} | {pct(meth_sig,n)}")
        print(f"   (cell,method)별 ({n_cm} family) | {cm_sig:5d} / {n} | {pct(cm_sig,n)}")
        if scope is H:
            globals()["_A_H"] = dict(n=n, raw=raw_sig, single=single_sig,
                                     cell=cell_sig, method=meth_sig, cm=cm_sig,
                                     n_cell=n_cell, n_meth=n_meth, n_cm=n_cm)
        else:
            globals()["_A_F"] = dict(n=n, raw=raw_sig, single=single_sig,
                                     cell=cell_sig, method=meth_sig, cm=cm_sig,
                                     n_cell=n_cell, n_meth=n_meth, n_cm=n_cm)

    # ========================================================
    # (b) paired 효과크기
    # ========================================================
    print()
    print("=" * 70)
    print("(b) 효과크기 — paired 설계용 재계산")
    print("=" * 70)
    for scope_name, scope in [("HEADLINE (K10 excl, n=1240)", H),
                              ("FULL (K10 incl, n=1360)", F)]:
        n = len(scope)
        # Cliff's delta
        ci_large = (scope["cliff_indep"] >= CLIFF_LARGE).sum()
        cp_large = (scope["cliff_paired"] >= CLIFF_LARGE).sum()
        cp_med = ((scope["cliff_paired"] >= CLIFF_MED)
                  & (scope["cliff_paired"] < CLIFF_LARGE)).sum()
        cp_small = ((scope["cliff_paired"] >= CLIFF_SMALL)
                    & (scope["cliff_paired"] < CLIFF_MED)).sum()
        cp_negl = ((scope["cliff_paired"].abs() < CLIFF_SMALL)).sum()
        cp_neg = (scope["cliff_paired"] < 0).sum()
        cp_plus1 = (scope["cliff_paired"] >= 0.9999).sum()
        # Hedges g
        gi_large = (scope["g_indep"].abs() >= 0.8).sum()
        gp_large = (scope["g_paired_av"].abs() >= 0.8).sum()
        grm_large = (scope["g_paired_rm"].abs() >= 0.8).sum()
        print(f"\n  [{scope_name}]")
        print(f"   Cliff's δ:")
        print(f"     독립표본 공식 (현행 REPORT)  large≥0.474: {ci_large}/{n} = {pct(ci_large,n)}"
              f"  mean δ={scope['cliff_indep'].mean():+.4f}")
        print(f"     paired 공식 (재계산)         large≥0.474: {cp_large}/{n} = {pct(cp_large,n)}"
              f"  mean δ={scope['cliff_paired'].mean():+.4f}")
        print(f"       paired δ 분포: large {cp_large} / medium {cp_med} / small {cp_small}"
              f" / negligible {cp_negl} / (음수 {cp_neg})  δ=+1.0: {cp_plus1}")
        print(f"   Hedges' g:")
        print(f"     독립표본 공식 (현행 REPORT)  |g|≥0.8: {gi_large}/{n} = {pct(gi_large,n)}"
              f"  mean g={scope['g_indep'].mean():+.4f}")
        print(f"     paired g_av (재계산)         |g|≥0.8: {gp_large}/{n} = {pct(gp_large,n)}"
              f"  mean g={scope['g_paired_av'].mean():+.4f}")
        gr = scope["g_paired_rm"].dropna()
        print(f"     paired g_rm (corr 보정,참고) |g|≥0.8: {grm_large}/{n} = "
              f"{pct(grm_large,n)}  mean g={gr.mean():+.4f}  (계산가능 {len(gr)})")
        tc = scope["trial_corr"].dropna()
        print(f"     trial 간 Pearson r: mean={tc.mean():+.4f} median={tc.median():+.4f}"
              f"  [{tc.min():+.3f}, {tc.max():+.3f}]  (계산가능 {len(tc)})")
        if scope is H:
            globals()["_B_H"] = dict(
                n=n, ci_large=ci_large, cp_large=cp_large,
                ci_mean=scope['cliff_indep'].mean(),
                cp_mean=scope['cliff_paired'].mean(),
                cp_med=cp_med, cp_small=cp_small, cp_negl=cp_negl,
                cp_neg=cp_neg, cp_plus1=cp_plus1,
                gi_large=gi_large, gp_large=gp_large, grm_large=grm_large,
                gi_mean=scope['g_indep'].mean(),
                gp_mean=scope['g_paired_av'].mean(),
                grm_mean=gr.mean(), grm_n=len(gr),
                r_mean=tc.mean(), r_median=tc.median(),
                r_min=tc.min(), r_max=tc.max())
        else:
            globals()["_B_F"] = dict(
                n=n, ci_large=ci_large, cp_large=cp_large,
                gi_large=gi_large, gp_large=gp_large)

    # ========================================================
    # (c) Wilcoxon p값 해상도
    # ========================================================
    print()
    print("=" * 70)
    print("(c) Wilcoxon p값 해상도 — n=10 floor 정량화")
    print("=" * 70)
    # n=10 exact one-sided Wilcoxon: 최소 p = 1/2^10 = 1/1024
    floor = 1.0 / 1024
    print(f"  n=10 exact one-sided Wilcoxon 최소 p값 = 1/1024 = {floor:.6f}")
    # two-sided 최소 = 2/1024
    floor2 = 2.0 / 1024
    print(f"  n=10 exact two-sided Wilcoxon 최소 p값 = 2/1024 = {floor2:.6f}")
    print()
    for scope_name, scope in [("HEADLINE (K10 excl, n=1240)", H),
                              ("FULL (K10 incl, n=1360)", F)]:
        n = len(scope)
        pg = scope["wilcoxon_p_greater"]
        pt_ = scope["wilcoxon_p"]
        # one-sided greater floor 도달
        at_floor_g = (pg <= floor * 1.0001).sum()
        # two-sided floor 도달
        at_floor_t = (pt_ <= floor2 * 1.0001).sum()
        # one-sided 가 floor 인데 better 인 비교
        better = scope["delta_pct_mean"] < 0
        floor_and_better = ((pg <= floor * 1.0001) & better).sum()
        # unique p값 개수
        nuniq_g = pg.round(7).nunique()
        nuniq_t = pt_.round(7).nunique()
        print(f"  [{scope_name}]")
        print(f"   one-sided greater p값이 floor(1/1024)에 도달: {at_floor_g}/{n} = {pct(at_floor_g,n)}")
        print(f"     그 중 better(δ<0): {floor_and_better}/{n} = {pct(floor_and_better,n)}")
        print(f"   two-sided p값이 floor(2/1024)에 도달: {at_floor_t}/{n} = {pct(at_floor_t,n)}")
        print(f"   one-sided greater 고유 p값 개수: {nuniq_g}  (이론상 가능 값 ~{55+1})")
        print(f"   two-sided 고유 p값 개수: {nuniq_t}")
        # p값 분포 histogram (one-sided greater)
        bins = [0, floor*1.5, 0.01, 0.05, 0.1, 0.5, 1.01]
        labels = ["floor(≈.001)", "(.001,.01]", "(.01,.05]", "(.05,.1]",
                  "(.1,.5]", "(.5,1]"]
        hist = pd.cut(pg, bins=bins, labels=labels,
                      include_lowest=True).value_counts().reindex(labels)
        print(f"   one-sided greater p값 분포:")
        for lab, cnt in hist.items():
            print(f"     {lab:15s}: {int(cnt):5d} ({100*cnt/n:.1f}%)")
        if scope is H:
            globals()["_C_H"] = dict(
                n=n, at_floor_g=at_floor_g, floor_and_better=floor_and_better,
                at_floor_t=at_floor_t, nuniq_g=nuniq_g, nuniq_t=nuniq_t,
                hist={lab: int(hist[lab]) for lab in labels})
        else:
            globals()["_C_F"] = dict(
                n=n, at_floor_g=at_floor_g, floor_and_better=floor_and_better,
                at_floor_t=at_floor_t, nuniq_g=nuniq_g, nuniq_t=nuniq_t)

    # ========================================================
    # (d) cell-weighted 재집계
    # ========================================================
    print()
    print("=" * 70)
    print("(d) cell-weighted 재집계")
    print("=" * 70)
    for scope_name, scope in [("HEADLINE (K10 excl, n=1240)", H),
                              ("FULL (K10 incl, n=1360)", F)]:
        n = len(scope)
        # file-weighted (현행 headline)
        fw_better = 100 * (scope["delta_pct_mean"] < 0).mean()
        fw_mean = scope["delta_pct_mean"].mean()
        fw_median = scope["delta_pct_mean"].median()
        # cell-weighted: cell별 평균 → cell 동일가중 평균
        cell_grp = scope.groupby("cell")
        per_cell_better = cell_grp.apply(
            lambda g: 100 * (g["delta_pct_mean"] < 0).mean(), include_groups=False)
        per_cell_mean = cell_grp["delta_pct_mean"].mean()
        per_cell_median = cell_grp["delta_pct_mean"].median()
        cw_better = per_cell_better.mean()
        cw_mean = per_cell_mean.mean()
        cw_median = per_cell_median.mean()
        n_cells = scope["cell"].nunique()
        print(f"\n  [{scope_name}]  cell 수 = {n_cells}")
        print(f"   file-weighted (현행): better {fw_better:.4f}%  "
              f"mean {fw_mean:+.4f}  median {fw_median:+.4f}")
        print(f"   cell-weighted        : better {cw_better:.4f}%  "
              f"mean {cw_mean:+.4f}  median {cw_median:+.4f}")
        print(f"   차이 (cell − file)   : better {cw_better-fw_better:+.4f}%p  "
              f"mean {cw_mean-fw_mean:+.4f}%p")
        # cell당 측정 file 수 분포
        cell_n = cell_grp.size()
        print(f"   cell당 paired 비교 수: min {cell_n.min()} max {cell_n.max()} "
              f"median {cell_n.median():.0f} mean {cell_n.mean():.1f}")
        if scope is H:
            globals()["_D_H"] = dict(
                n=n, n_cells=n_cells,
                fw_better=fw_better, fw_mean=fw_mean, fw_median=fw_median,
                cw_better=cw_better, cw_mean=cw_mean, cw_median=cw_median,
                cell_n_min=int(cell_n.min()), cell_n_max=int(cell_n.max()),
                cell_n_median=cell_n.median(), cell_n_mean=cell_n.mean())
            # per-cell table 저장
            globals()["_D_H_table"] = pd.DataFrame({
                "n": cell_n, "better%": per_cell_better,
                "mean": per_cell_mean, "median": per_cell_median,
            }).sort_values("mean")
        else:
            globals()["_D_F"] = dict(
                n=n, n_cells=n_cells,
                fw_better=fw_better, fw_mean=fw_mean, fw_median=fw_median,
                cw_better=cw_better, cw_mean=cw_mean, cw_median=cw_median)

    # per-cell breakdown for (d)
    print()
    print("  per-cell breakdown (HEADLINE, K10 excl) — mean Δ% 오름차순:")
    t = globals()["_D_H_table"]
    print(f"  {'cell':28s} {'n':>5s} {'better%':>9s} {'mean':>9s} {'median':>9s}")
    for cell, r in t.iterrows():
        print(f"  {cell:28s} {int(r['n']):5d} {r['better%']:8.1f}% "
              f"{r['mean']:+8.2f} {r['median']:+8.2f}")

    # save processed parquet for md writer
    out = pt2.copy()
    keep = ["cell", "method", "paradigm", "sel", "K_norm", "single_multi",
            "pairing", "k10", "delta_pct_mean", "delta_pct_median",
            "wilcoxon_p", "wilcoxon_p_greater",
            "cliff_indep", "cliff_paired", "g_indep", "g_paired_av",
            "g_paired_rm", "trial_corr"]
    out[keep].to_parquet(
        REPO / "_internal" / "cache" / "rq3" / "stats_supplement_v12_detail.parquet",
        index=False)
    print()
    print("wrote stats_supplement_v12_detail.parquet")

    # dump summary dict as JSON for md writer
    summary = {k: globals()[k] for k in
               ["_A_H", "_A_F", "_B_H", "_B_F", "_C_H", "_C_F", "_D_H", "_D_F"]}
    # convert numpy types
    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        return o
    summary = conv(summary)
    (REPO / "_internal" / "cache" / "rq3" / "stats_supplement_v12_summary.json"
     ).write_text(json.dumps(summary, indent=2))
    print("wrote stats_supplement_v12_summary.json")
    t.reset_index().to_csv(
        REPO / "_internal" / "cache" / "rq3" / "stats_supplement_v12_percell.csv",
        index=False)
    print("wrote stats_supplement_v12_percell.csv")


if __name__ == "__main__":
    main()
