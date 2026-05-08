#!/usr/bin/env python3
"""
Multi-vector / multi-table-join paradigm 11-method paired Δ% 분석.

5/8 21:34 launch (PID 4100548 / 4100549) 결과 도착 후 즉시 실행되는 분석 layer.
단일 측정 분석 (`single_adaptive_paired/`) 과 동일한 framework 를 multi 환경으로
확장한다.

입력 (3 cell × multi-relation 측정 산출):
  1. Multi paradigm 11-method (PID 4100549)
       multi_paradigm_<cell>.csv  (3 cell)
       schema: table, dataset, mode, selectivity, seed, query_id,
               D1_target, D2_target, true_card, est, q_error,
               method_user, paradigm
       (mode 컬럼이 method 식별 — measure_multi_paradigm 출력 그대로)

  2. Multi Adaptive Sampling baseline (PID 4100548)
       multi_adaptive_<cell>.csv 또는 .parquet (3 cell)
       schema: table[_pair], dataset, mode='adaptive', selectivity, seed, query_id,
               D1_target/D_deep_target, D2_target/D_wiki_target, true_card, est, q_error,
               sample_size_used_t1, sample_size_used_t2

  3. Multi 5-mode BERN baseline (기존)
       rq2_multi_5mode_<cell>.parquet  (mode == 'bernoulli')

분석 단계:
  1. paired Δ% (각 method vs BERN baseline) — query_id × selectivity × seed 정확 alignment
  2. cell × method × sel mean / median Δ% 표 (3 × 11 × 5 = 165 cell)
  3. method × cell paired Wilcoxon two-sided p-value + Multiple comparison (BH FDR + Bonferroni)
  4. 4강 (HDBSCAN, MB_partial, Hilbert, sparse_rp) vs 11-method full ranking
  5. Multi 4강 vs Multi Adaptive paired Δ% (5 method paired comparison, 3 cell × 5 sel)
  6. 단일 → multi shrinkage chain 재계산 (단일 17.13% → multi-vector / multi-join, sparse_rp 추가)

산출:
  _internal/cache/multi_paradigm_paired/multi_paradigm_paired_summary.csv
  _internal/cache/multi_paradigm_paired/multi_paradigm_paired_wilcoxon.csv
  _internal/cache/multi_paradigm_paired/multi_4kang_vs_adaptive_h2h.csv
  _internal/cache/multi_paradigm_paired/multi_shrinkage_table.csv

CLI:
  python3 _internal/scripts/analyze_multi_paradigm.py            # 자동 input scan
  python3 _internal/scripts/analyze_multi_paradigm.py --input-dir <dir>
  python3 _internal/scripts/analyze_multi_paradigm.py --dry-run  # 입력 스캔만
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# 상수 — measure_multi_* 와 동일
# ---------------------------------------------------------------------------

CELLS = [
    "partsupp_deep_sift_10",  # multi-vector (deep 96d + sift 128d)
    "partsupp_deep_wiki_10",  # multi-vector (deep 96d + wiki 768d)
    "multi_join_deep_wiki",   # multi-table join (partsupp_deep_10 ⨝ part_wiki_10)
]

# paradigm framework — measure_multi_paradigm.py 와 동일 11종
PARADIGM_METHODS = [
    "HDBSCAN", "MiniBatch", "GMM",
    "Hilbert", "faiss_ivf",
    "MB_partial", "Reservoir",
    "sparse_rp", "PCA1D",
    "LSH", "Sobol",
]

# 4강 method (production-friendly criteria, 5/8 14:13 finalize)
FOUR_KANG = ["HDBSCAN", "MB_partial", "Hilbert", "sparse_rp"]

SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]

# 단일 sweet spot baseline (master_v6 §10.6 narrative)
SINGLE_SWEET_MEAN_PCT = 17.13  # 단일 |Δ%| 평균 (4강 method × sweet cell × sel=0.10)


# ---------------------------------------------------------------------------
# Input scan
# ---------------------------------------------------------------------------

def scan_inputs(input_dirs: list[Path]) -> dict[str, dict]:
    """3 cell 별 paradigm / adaptive / bern_baseline 입력 위치 자동 검출.

    Returns:
        {cell: {"paradigm": Path, "adaptive": Path, "bern_baseline": Path}}
        파일 없으면 None.
    """
    found: dict[str, dict] = {}
    for cell in CELLS:
        slot = {"paradigm": None, "adaptive": None, "bern_baseline": None}
        for d in input_dirs:
            for pattern, key in [
                (f"multi_paradigm_{cell}.*",      "paradigm"),
                (f"multi_adaptive_{cell}.*",      "adaptive"),
                (f"rq2_multi_5mode_{cell}*.*",    "bern_baseline"),
            ]:
                if slot[key] is None:
                    for p in d.rglob(pattern):
                        if p.suffix in {".csv", ".parquet"}:
                            slot[key] = p
                            break
        found[cell] = slot
    return found


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# 분석 1 — paired Δ% (vs BERN baseline) per (cell × method × sel)
# ---------------------------------------------------------------------------

def compute_paired_summary(paradigm: pd.DataFrame, bern: pd.DataFrame,
                            cell: str) -> pd.DataFrame:
    """method 별로 query_id × seed × selectivity paired alignment → Δ% 계산.

    Δ% = (q_error[method] − q_error[bern]) / q_error[bern] × 100
    (음수 = method 가 더 정확)
    """
    KEY = ["selectivity", "seed", "query_id"]
    bern_aligned = bern[bern["mode"] == "bernoulli"][KEY + ["q_error"]].copy()
    bern_aligned = bern_aligned.rename(columns={"q_error": "q_error_bern"})

    out_rows = []
    methods = sorted(paradigm["method_user"].dropna().unique().tolist()) \
        if "method_user" in paradigm.columns else \
        sorted(paradigm["mode"].dropna().unique().tolist())

    for method in methods:
        if "method_user" in paradigm.columns:
            sub = paradigm[paradigm["method_user"] == method]
        else:
            sub = paradigm[paradigm["mode"] == method]

        merged = sub.merge(bern_aligned, on=KEY, how="inner",
                            suffixes=("", "_bern"))
        merged = merged.dropna(subset=["q_error", "q_error_bern"])
        merged = merged[(merged["q_error_bern"] > 0)]
        if merged.empty:
            continue

        merged["delta_pct"] = (
            (merged["q_error"] - merged["q_error_bern"]) /
            merged["q_error_bern"] * 100.0
        )

        for sel, grp in merged.groupby("selectivity"):
            d = grp["delta_pct"].values
            out_rows.append({
                "cell": cell, "method": method, "selectivity": sel,
                "n_paired": len(d),
                "mean_delta_pct": float(np.nanmean(d)),
                "median_delta_pct": float(np.nanmedian(d)),
                "std_delta_pct": float(np.nanstd(d)),
            })
    return pd.DataFrame(out_rows)


def compute_paired_wilcoxon(paradigm: pd.DataFrame, bern: pd.DataFrame,
                             cell: str) -> pd.DataFrame:
    """method × selectivity 별 paired Wilcoxon (q_error[method] vs q_error[bern])."""
    KEY = ["selectivity", "seed", "query_id"]
    bern_aligned = bern[bern["mode"] == "bernoulli"][KEY + ["q_error"]].copy()
    bern_aligned = bern_aligned.rename(columns={"q_error": "q_error_bern"})

    methods = sorted(paradigm["method_user"].dropna().unique().tolist()) \
        if "method_user" in paradigm.columns else \
        sorted(paradigm["mode"].dropna().unique().tolist())

    out_rows = []
    for method in methods:
        if "method_user" in paradigm.columns:
            sub = paradigm[paradigm["method_user"] == method]
        else:
            sub = paradigm[paradigm["mode"] == method]

        merged = sub.merge(bern_aligned, on=KEY, how="inner",
                            suffixes=("", "_bern"))
        merged = merged.dropna(subset=["q_error", "q_error_bern"])
        merged = merged[merged["q_error_bern"] > 0]

        for sel, grp in merged.groupby("selectivity"):
            x = grp["q_error"].values
            y = grp["q_error_bern"].values
            stat, p = (np.nan, np.nan)
            try:
                if len(x) > 0 and not np.allclose(x, y):
                    res = stats.wilcoxon(x, y, alternative="two-sided",
                                          zero_method="zsplit")
                    stat, p = float(res.statistic), float(res.pvalue)
            except Exception:
                pass

            mean_delta = float(np.nanmean(
                (x - y) / np.where(y > 0, y, np.nan) * 100.0
            )) if len(x) else float("nan")

            out_rows.append({
                "cell": cell, "method": method, "selectivity": sel,
                "n_paired": len(x),
                "mean_delta_pct": mean_delta,
                "wilcoxon_stat": stat, "wilcoxon_p": p,
                "significant_05": bool(np.isfinite(p) and p < 0.05),
            })
    return pd.DataFrame(out_rows)


# ---------------------------------------------------------------------------
# 분석 2 — Multiple Comparison correction (BH FDR + Bonferroni)
# ---------------------------------------------------------------------------

def add_mc_correction(wilcoxon: pd.DataFrame) -> pd.DataFrame:
    """BH FDR (q=0.05) + Bonferroni (α=0.05/N) 추가 컬럼.

    Test 묶음 = 한 cell × 한 method 의 5 sel (or 전체 cell-method-sel 통합).
    여기서는 전체 (cell × method × sel) 묶음 N 으로 보정 — narrative 단순화.
    """
    out = wilcoxon.copy()
    p = out["wilcoxon_p"].values
    finite_mask = np.isfinite(p)
    finite_idx = np.where(finite_mask)[0]
    p_fin = p[finite_idx]
    n = len(p_fin)

    bonf = np.full(len(p), np.nan)
    bh = np.full(len(p), np.nan)

    if n > 0:
        # Bonferroni
        bonf_fin = np.minimum(p_fin * n, 1.0)
        bonf[finite_idx] = bonf_fin

        # Benjamini-Hochberg
        order = np.argsort(p_fin)
        ranked = p_fin[order]
        bh_ranked = ranked * n / (np.arange(n) + 1)
        # monotone enforce (BH adjustment 표준)
        bh_ranked = np.minimum.accumulate(bh_ranked[::-1])[::-1]
        bh_ranked = np.minimum(bh_ranked, 1.0)
        bh_fin = np.empty_like(bh_ranked)
        bh_fin[order] = bh_ranked
        bh[finite_idx] = bh_fin

    out["bonferroni_p"] = bonf
    out["bh_fdr_q"] = bh
    out["sig_bonf_05"] = (bonf < 0.05) & np.isfinite(bonf)
    out["sig_bh_05"] = (bh < 0.05) & np.isfinite(bh)
    return out


# ---------------------------------------------------------------------------
# 분석 3 — Multi 4강 vs Multi Adaptive paired (head-to-head)
# ---------------------------------------------------------------------------

def compute_h2h_vs_adaptive(paradigm: pd.DataFrame, adaptive: pd.DataFrame,
                              cell: str) -> pd.DataFrame:
    """4강 method 4종 + Adaptive 1종 = 5 method 의 head-to-head paired Δ%.

    Δ%_h2h = (q_error[method] − q_error[adaptive]) / q_error[adaptive] × 100
    """
    KEY = ["selectivity", "seed", "query_id"]
    ada = adaptive[KEY + ["q_error"]].copy()
    ada = ada.rename(columns={"q_error": "q_error_ada"})

    method_col = "method_user" if "method_user" in paradigm.columns else "mode"
    out_rows = []
    for method in FOUR_KANG:
        sub = paradigm[paradigm[method_col] == method]
        if sub.empty:
            continue
        merged = sub.merge(ada, on=KEY, how="inner")
        merged = merged.dropna(subset=["q_error", "q_error_ada"])
        merged = merged[merged["q_error_ada"] > 0]
        if merged.empty:
            continue
        merged["delta_pct_h2h"] = (
            (merged["q_error"] - merged["q_error_ada"]) /
            merged["q_error_ada"] * 100.0
        )

        # cell × method (전 sel pool)
        d_all = merged["delta_pct_h2h"].values
        x_all = merged["q_error"].values
        y_all = merged["q_error_ada"].values
        try:
            stat_all, p_all = stats.wilcoxon(
                x_all, y_all, alternative="two-sided", zero_method="zsplit"
            )
            stat_all, p_all = float(stat_all), float(p_all)
        except Exception:
            stat_all, p_all = float("nan"), float("nan")
        n_better = int((d_all < 0).sum())
        out_rows.append({
            "cell": cell, "method": method, "selectivity": "all",
            "n_paired": len(d_all),
            "mean_delta_pct_h2h": float(np.nanmean(d_all)),
            "median_delta_pct_h2h": float(np.nanmedian(d_all)),
            "n_better": n_better,
            "p_better": n_better / len(d_all) if len(d_all) else float("nan"),
            "wilcoxon_p": p_all,
            "significant_05": bool(np.isfinite(p_all) and p_all < 0.05),
            "method_better": bool(np.nanmedian(d_all) < 0),
        })

        # cell × method × sel (per-sel breakdown)
        for sel, grp in merged.groupby("selectivity"):
            d = grp["delta_pct_h2h"].values
            x = grp["q_error"].values
            y = grp["q_error_ada"].values
            try:
                stat_s, p_s = stats.wilcoxon(
                    x, y, alternative="two-sided", zero_method="zsplit"
                )
                stat_s, p_s = float(stat_s), float(p_s)
            except Exception:
                stat_s, p_s = float("nan"), float("nan")
            out_rows.append({
                "cell": cell, "method": method, "selectivity": sel,
                "n_paired": len(d),
                "mean_delta_pct_h2h": float(np.nanmean(d)),
                "median_delta_pct_h2h": float(np.nanmedian(d)),
                "n_better": int((d < 0).sum()),
                "p_better": float((d < 0).mean()) if len(d) else float("nan"),
                "wilcoxon_p": p_s,
                "significant_05": bool(np.isfinite(p_s) and p_s < 0.05),
                "method_better": bool(np.nanmedian(d) < 0),
            })
    return pd.DataFrame(out_rows)


# ---------------------------------------------------------------------------
# 분석 4 — 단일 → multi shrinkage chain
# ---------------------------------------------------------------------------

def compute_shrinkage_table(summary: pd.DataFrame,
                              single_pct: float = SINGLE_SWEET_MEAN_PCT) -> pd.DataFrame:
    """4강 method × multi cell 의 평균 |Δ%| 추출 → 단일 sweet spot 대비 shrinkage 비.

    sel=0.10 reference (master_v6 §10.6 narrative 와 동일 기준).
    """
    out_rows = []
    sub = summary[(summary["selectivity"] == 0.10) &
                   (summary["method"].isin(FOUR_KANG))].copy()

    # 4강 method × multi cell 평균 |Δ%|
    sub["abs_delta"] = sub["mean_delta_pct"].abs()
    cell_kind = {
        "partsupp_deep_sift_10": "multi_vector_deep_sift",
        "partsupp_deep_wiki_10": "multi_vector_deep_wiki",
        "multi_join_deep_wiki":  "multi_table_join",
    }
    for cell, grp in sub.groupby("cell"):
        mean_abs = float(grp["abs_delta"].mean())
        out_rows.append({
            "cell": cell,
            "kind": cell_kind.get(cell, "multi"),
            "method_set": "4kang (HDBSCAN/MB_partial/Hilbert/sparse_rp)",
            "n_method": int(grp["method"].nunique()),
            "mean_abs_delta_pct": mean_abs,
            "single_sweet_mean_pct": single_pct,
            "shrinkage_x": single_pct / mean_abs if mean_abs > 0 else float("nan"),
        })

    # multi-vector 2 cell 통합 평균 (sparse_rp 포함 4강 vs 단일 비교용)
    mv_cells = ["partsupp_deep_sift_10", "partsupp_deep_wiki_10"]
    mv = sub[sub["cell"].isin(mv_cells)]
    if not mv.empty:
        mean_mv = float(mv["abs_delta"].mean())
        out_rows.append({
            "cell": "multi_vector (avg of 2)",
            "kind": "multi_vector_avg",
            "method_set": "4kang",
            "n_method": int(mv["method"].nunique()),
            "mean_abs_delta_pct": mean_mv,
            "single_sweet_mean_pct": single_pct,
            "shrinkage_x": single_pct / mean_mv if mean_mv > 0 else float("nan"),
        })

    return pd.DataFrame(out_rows)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Multi paradigm 11-method paired Δ% 분석 — 5/9 morning 결과 도착 후 즉시 실행.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--input-dir", type=str, action="append", default=None,
                    help="입력 csv/parquet 검색 dir (반복). default: server CACHE + 로컬 _internal/cache/rq3")
    ap.add_argument("--out-dir", type=str,
                    default="/Users/hyunbin/Capstone/_internal/cache/multi_paradigm_paired",
                    help="출력 dir")
    ap.add_argument("--single-pct", type=float, default=SINGLE_SWEET_MEAN_PCT,
                    help=("단일 sweet spot 평균 |Delta percent| "
                          f"(default: {SINGLE_SWEET_MEAN_PCT})"))
    ap.add_argument("--dry-run", action="store_true",
                    help="입력 파일 detection 만 — 실제 분석 X")
    args = ap.parse_args()

    # input dir 자동 expand
    if args.input_dir is None:
        candidates = [
            Path("/mnt/hdd0/home/capstone2026/cache/rq3"),
            Path("/Users/hyunbin/Capstone/_internal/cache"),
            Path("/Users/hyunbin/Capstone/experiments/code/rq3"),
        ]
    else:
        candidates = [Path(d) for d in args.input_dir]
    input_dirs = [d for d in candidates if d.exists()]
    print(f"[scan] input_dirs: {input_dirs}", file=sys.stderr)

    found = scan_inputs(input_dirs)
    print(f"\n=== input scan ({len(CELLS)} cell) ===", file=sys.stderr)
    missing = []
    for cell, slot in found.items():
        print(f"  {cell}:", file=sys.stderr)
        for k, p in slot.items():
            tag = "OK" if p else "MISSING"
            print(f"    {k:<14} {tag:<8} {p if p else ''}", file=sys.stderr)
            if not p:
                missing.append((cell, k))

    if args.dry_run:
        print(f"\n[dry-run] missing = {len(missing)}, OK = {3*3 - len(missing)}/9",
              file=sys.stderr)
        return 0 if not missing else 1

    if missing:
        print(f"\n[ABORT] {len(missing)} input(s) missing — 5/9 morning 결과 도착 후 재실행", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_dfs: list[pd.DataFrame] = []
    wilcoxon_dfs: list[pd.DataFrame] = []
    h2h_dfs: list[pd.DataFrame] = []

    for cell in CELLS:
        slot = found[cell]
        print(f"\n=== analyze cell={cell} ===", file=sys.stderr)
        paradigm = load_table(slot["paradigm"])
        adaptive = load_table(slot["adaptive"])
        bern = load_table(slot["bern_baseline"])

        s = compute_paired_summary(paradigm, bern, cell)
        w = compute_paired_wilcoxon(paradigm, bern, cell)
        h = compute_h2h_vs_adaptive(paradigm, adaptive, cell)
        summary_dfs.append(s)
        wilcoxon_dfs.append(w)
        h2h_dfs.append(h)

        print(f"  paradigm rows={len(paradigm):,} adaptive rows={len(adaptive):,} "
              f"bern rows={len(bern):,}", file=sys.stderr)
        print(f"  summary rows={len(s)}, wilcoxon rows={len(w)}, h2h rows={len(h)}",
              file=sys.stderr)

    summary = pd.concat(summary_dfs, ignore_index=True) if summary_dfs else pd.DataFrame()
    wilcoxon = pd.concat(wilcoxon_dfs, ignore_index=True) if wilcoxon_dfs else pd.DataFrame()
    h2h = pd.concat(h2h_dfs, ignore_index=True) if h2h_dfs else pd.DataFrame()

    if not wilcoxon.empty:
        wilcoxon = add_mc_correction(wilcoxon)
    shrinkage = compute_shrinkage_table(summary, single_pct=args.single_pct) \
        if not summary.empty else pd.DataFrame()

    out_summary = out_dir / "multi_paradigm_paired_summary.csv"
    out_wilcox = out_dir / "multi_paradigm_paired_wilcoxon.csv"
    out_h2h = out_dir / "multi_4kang_vs_adaptive_h2h.csv"
    out_shrink = out_dir / "multi_shrinkage_table.csv"

    summary.to_csv(out_summary, index=False)
    wilcoxon.to_csv(out_wilcox, index=False)
    h2h.to_csv(out_h2h, index=False)
    shrinkage.to_csv(out_shrink, index=False)

    print(f"\n=== output ===", file=sys.stderr)
    print(f"  {out_summary}  ({len(summary)} rows)", file=sys.stderr)
    print(f"  {out_wilcox}   ({len(wilcoxon)} rows)", file=sys.stderr)
    print(f"  {out_h2h}      ({len(h2h)} rows)", file=sys.stderr)
    print(f"  {out_shrink}   ({len(shrinkage)} rows)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
