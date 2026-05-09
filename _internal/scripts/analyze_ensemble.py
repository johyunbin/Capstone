#!/usr/bin/env python3
"""
Adaptive × base method ensemble paired Δ% 분석 — X6 / X7 결합.

5/8 22:00 launch (X6 Adaptive×4kang ensemble + X7 Adaptive×11-method ensemble) 의
결과 도착 (5/9 morning) 후 즉시 실행되는 분석 layer. analyze_multi_paradigm.py 와
동일 framework + scipy paired Wilcoxon 으로 ensemble 효과를 정량화한다.

입력 (단일 10 cell × 11 base method × 5 sel × 5 seed × 100 query = 110 parquet):
  1. Ensemble 결과 (X6 + X7 통합)
       cache/rq1/rq3_<DS>_sf<N>_ensemble_<base>.parquet  (10 cell × 11 base = 110)
       schema: dataset, sf, mode='ensemble', selectivity, seed, query_id,
               D_target, true_card, est, q_error,
               method_user (= base method), sample_size_used,
               adaptive_n_final, adaptive_n_init=385

  2. Single base method baseline (paired source for "vs base method" comparison)
       cache/rq1/rq3_<DS>_sf<N>_<method>.parquet  (10 cell × 11 method = 110)
       schema: dataset, sf, mode=<method>, selectivity, seed, query_id,
               q_error, sample_size_used (K=20 fixed N=385)

  3. Adaptive Sampling baseline (paired source for "vs Adaptive" comparison)
       cache/rq1/rq3_<DS>_sf<N>_adaptive.parquet  (10 cell)
       schema: dataset, sf, mode='adaptive', selectivity, seed, query_id,
               q_error, sample_size_used (dynamic N)

분석 단계:
  1. paired Δ% (각 ensemble vs single base method) — query_id × selectivity × seed alignment
       → "K=20 fixed N=385 stratification" → "K=20 stratification + Adaptive dynamic N"
         의 dynamic budget uplift 정량
  2. paired Δ% (각 ensemble vs Adaptive baseline)
       → "Adaptive 단독 (unstratified Bernoulli + dynamic N)" → "K=20 stratified + dynamic N"
         의 stratification uplift 정량
  3. cell × base × sel mean Δ% 표 (10 × 11 × 5 = 550 cell)
  4. ensemble winner ranking — 가장 강한 (cell, base) ensemble 조합 (median Δ% < 0 의 cell 비율 + magnitude)
  5. paired Wilcoxon two-sided + Multiple comparison (BH FDR + Bonferroni)

산출:
  _internal/cache/ensemble_paired/ensemble_vs_base_summary.csv
       — (cell, base, sel) × paired Δ% mean/median, n_paired, wilcoxon_p
  _internal/cache/ensemble_paired/ensemble_vs_adaptive_summary.csv
       — (cell, base, sel) × paired Δ% mean/median, n_paired, wilcoxon_p
  _internal/cache/ensemble_paired/ensemble_winner_ranking.csv
       — 11 base 별 cell-pool aggregate (n_better/n_total + median Δ% + significant cell count)

CLI:
  python3 _internal/scripts/analyze_ensemble.py            # 자동 input scan
  python3 _internal/scripts/analyze_ensemble.py --input-dir <dir>
  python3 _internal/scripts/analyze_ensemble.py --dry-run  # 입력 스캔만
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
# 상수
# ---------------------------------------------------------------------------

CELLS = [
    ("DEEP", 1), ("DEEP", 10),
    ("SIFT", 1), ("SIFT", 10),
    ("SSN", 1),  ("SSN", 10),
    ("WIKI", 1), ("WIKI", 10),
    ("YFCC", 1), ("YFCC", 10),
]

# X7 launch 의 11 base method (5 paradigm representative full set, lowercase 매칭)
BASE_METHODS = [
    "hdbscan", "minibatch", "gmm",        # P1 Density Clustering
    "hilbert", "faiss_ivf",               # P2 Spatial Indexing
    "minibatch_partial", "reservoir",     # P3 Online Streaming
    "sparse_rp", "pca1d",                 # P4 Linear Projection
    "lsh", "sobol",                       # P5 Quasi-random
]

# 4강 (X6 launch) — production-friendly criteria
FOUR_KANG = ["hdbscan", "minibatch_partial", "hilbert", "sparse_rp"]

SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]


# ---------------------------------------------------------------------------
# Input scan
# ---------------------------------------------------------------------------

def _cell_tag(ds: str, sf: int) -> str:
    return f"{ds}_sf{sf}"


def scan_inputs(input_dirs: list[Path]) -> dict[str, dict]:
    """10 cell 별 ensemble (11 base) / single base (11) / adaptive 입력 위치 자동 검출.

    Returns:
        {cell_tag: {"ensemble": {base: Path}, "base": {base: Path}, "adaptive": Path}}
        파일 없으면 None.
    """
    found: dict[str, dict] = {}
    for ds, sf in CELLS:
        tag = _cell_tag(ds, sf)
        slot = {
            "ensemble": {b: None for b in BASE_METHODS},
            "base":     {b: None for b in BASE_METHODS},
            "adaptive": None,
        }
        for d in input_dirs:
            for base in BASE_METHODS:
                # ensemble: rq3_DEEP_sf1_ensemble_HDBSCAN.parquet
                if slot["ensemble"][base] is None:
                    pat = f"rq3_{ds}_sf{sf}_ensemble_{base}.*"
                    for p in d.rglob(pat):
                        if p.suffix in {".parquet", ".csv"}:
                            slot["ensemble"][base] = p
                            break
                # single base: rq3_DEEP_sf1_HDBSCAN.parquet
                if slot["base"][base] is None:
                    pat = f"rq3_{ds}_sf{sf}_{base}.*"
                    for p in d.rglob(pat):
                        if p.suffix in {".parquet", ".csv"}:
                            slot["base"][base] = p
                            break
            if slot["adaptive"] is None:
                pat = f"rq3_{ds}_sf{sf}_adaptive.*"
                for p in d.rglob(pat):
                    if p.suffix in {".parquet", ".csv"}:
                        slot["adaptive"] = p
                        break
        found[tag] = slot
    return found


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


# ---------------------------------------------------------------------------
# 분석 1 — ensemble vs single base method paired Δ%
# ---------------------------------------------------------------------------

def compute_paired_vs_base(ensemble: pd.DataFrame, base: pd.DataFrame,
                            cell: str, base_name: str) -> pd.DataFrame:
    """query_id × seed × selectivity paired alignment → Δ% (ensemble − base) / base × 100.

    음수 = ensemble (K=20 strat + Adaptive dynamic) 가 base (K=20 strat + fixed N=385) 보다 정확.
    """
    KEY = ["selectivity", "seed", "query_id"]
    base_aligned = base[KEY + ["q_error"]].copy()
    base_aligned = base_aligned.rename(columns={"q_error": "q_error_base"})

    merged = ensemble.merge(base_aligned, on=KEY, how="inner")
    merged = merged.dropna(subset=["q_error", "q_error_base"])
    merged = merged[merged["q_error_base"] > 0]
    if merged.empty:
        return pd.DataFrame()

    merged["delta_pct"] = (
        (merged["q_error"] - merged["q_error_base"]) /
        merged["q_error_base"] * 100.0
    )

    out_rows = []
    for sel, grp in merged.groupby("selectivity"):
        d = grp["delta_pct"].values
        x = grp["q_error"].values
        y = grp["q_error_base"].values
        try:
            res = stats.wilcoxon(x, y, alternative="two-sided", zero_method="zsplit")
            stat, p = float(res.statistic), float(res.pvalue)
        except Exception:
            stat, p = float("nan"), float("nan")
        out_rows.append({
            "cell": cell, "base": base_name, "selectivity": sel,
            "n_paired": len(d),
            "mean_delta_pct": float(np.nanmean(d)),
            "median_delta_pct": float(np.nanmedian(d)),
            "std_delta_pct": float(np.nanstd(d)),
            "n_better": int((d < 0).sum()),
            "p_better": float((d < 0).mean()) if len(d) else float("nan"),
            "wilcoxon_stat": stat, "wilcoxon_p": p,
            "significant_05": bool(np.isfinite(p) and p < 0.05),
            "ensemble_better": bool(np.nanmedian(d) < 0),
        })

    # cell × base 전 sel pool 통합 row
    d_all = merged["delta_pct"].values
    x_all = merged["q_error"].values
    y_all = merged["q_error_base"].values
    try:
        res = stats.wilcoxon(x_all, y_all, alternative="two-sided",
                              zero_method="zsplit")
        stat, p = float(res.statistic), float(res.pvalue)
    except Exception:
        stat, p = float("nan"), float("nan")
    out_rows.append({
        "cell": cell, "base": base_name, "selectivity": "all",
        "n_paired": len(d_all),
        "mean_delta_pct": float(np.nanmean(d_all)),
        "median_delta_pct": float(np.nanmedian(d_all)),
        "std_delta_pct": float(np.nanstd(d_all)),
        "n_better": int((d_all < 0).sum()),
        "p_better": float((d_all < 0).mean()) if len(d_all) else float("nan"),
        "wilcoxon_stat": stat, "wilcoxon_p": p,
        "significant_05": bool(np.isfinite(p) and p < 0.05),
        "ensemble_better": bool(np.nanmedian(d_all) < 0),
    })
    return pd.DataFrame(out_rows)


# ---------------------------------------------------------------------------
# 분석 2 — ensemble vs Adaptive baseline paired Δ%
# ---------------------------------------------------------------------------

def compute_paired_vs_adaptive(ensemble: pd.DataFrame, adaptive: pd.DataFrame,
                                cell: str, base_name: str) -> pd.DataFrame:
    KEY = ["selectivity", "seed", "query_id"]
    ada = adaptive[KEY + ["q_error"]].copy()
    ada = ada.rename(columns={"q_error": "q_error_ada"})

    merged = ensemble.merge(ada, on=KEY, how="inner")
    merged = merged.dropna(subset=["q_error", "q_error_ada"])
    merged = merged[merged["q_error_ada"] > 0]
    if merged.empty:
        return pd.DataFrame()

    merged["delta_pct"] = (
        (merged["q_error"] - merged["q_error_ada"]) /
        merged["q_error_ada"] * 100.0
    )

    out_rows = []
    for sel, grp in merged.groupby("selectivity"):
        d = grp["delta_pct"].values
        x = grp["q_error"].values
        y = grp["q_error_ada"].values
        try:
            res = stats.wilcoxon(x, y, alternative="two-sided", zero_method="zsplit")
            stat, p = float(res.statistic), float(res.pvalue)
        except Exception:
            stat, p = float("nan"), float("nan")
        out_rows.append({
            "cell": cell, "base": base_name, "selectivity": sel,
            "n_paired": len(d),
            "mean_delta_pct": float(np.nanmean(d)),
            "median_delta_pct": float(np.nanmedian(d)),
            "std_delta_pct": float(np.nanstd(d)),
            "n_better": int((d < 0).sum()),
            "p_better": float((d < 0).mean()) if len(d) else float("nan"),
            "wilcoxon_stat": stat, "wilcoxon_p": p,
            "significant_05": bool(np.isfinite(p) and p < 0.05),
            "ensemble_better": bool(np.nanmedian(d) < 0),
        })

    d_all = merged["delta_pct"].values
    x_all = merged["q_error"].values
    y_all = merged["q_error_ada"].values
    try:
        res = stats.wilcoxon(x_all, y_all, alternative="two-sided", zero_method="zsplit")
        stat, p = float(res.statistic), float(res.pvalue)
    except Exception:
        stat, p = float("nan"), float("nan")
    out_rows.append({
        "cell": cell, "base": base_name, "selectivity": "all",
        "n_paired": len(d_all),
        "mean_delta_pct": float(np.nanmean(d_all)),
        "median_delta_pct": float(np.nanmedian(d_all)),
        "std_delta_pct": float(np.nanstd(d_all)),
        "n_better": int((d_all < 0).sum()),
        "p_better": float((d_all < 0).mean()) if len(d_all) else float("nan"),
        "wilcoxon_stat": stat, "wilcoxon_p": p,
        "significant_05": bool(np.isfinite(p) and p < 0.05),
        "ensemble_better": bool(np.nanmedian(d_all) < 0),
    })
    return pd.DataFrame(out_rows)


# ---------------------------------------------------------------------------
# 분석 3 — Multiple comparison correction (BH FDR + Bonferroni)
# ---------------------------------------------------------------------------

def add_mc_correction(df: pd.DataFrame, p_col: str = "wilcoxon_p") -> pd.DataFrame:
    out = df.copy()
    p = out[p_col].values
    finite_mask = np.isfinite(p)
    finite_idx = np.where(finite_mask)[0]
    p_fin = p[finite_idx]
    n = len(p_fin)

    bonf = np.full(len(p), np.nan)
    bh = np.full(len(p), np.nan)

    if n > 0:
        bonf_fin = np.minimum(p_fin * n, 1.0)
        bonf[finite_idx] = bonf_fin

        order = np.argsort(p_fin)
        ranked = p_fin[order]
        bh_ranked = ranked * n / (np.arange(n) + 1)
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
# 분석 4 — Ensemble winner ranking (11 base × 10 cell aggregate)
# ---------------------------------------------------------------------------

def compute_winner_ranking(vs_base: pd.DataFrame,
                             vs_adaptive: pd.DataFrame) -> pd.DataFrame:
    """11 base 별로 10 cell pool 의 win/sig 비율 + median Δ% 평균.

    "winner" 정의: vs_base 와 vs_adaptive 양쪽에서 ensemble_better == True 그리고
    vs_adaptive paired Wilcoxon p < 0.05 의 cell 수를 강세 지표로 사용.
    """
    out_rows = []
    for base in BASE_METHODS:
        sub_b = vs_base[(vs_base["base"] == base) &
                          (vs_base["selectivity"] == "all")]
        sub_a = vs_adaptive[(vs_adaptive["base"] == base) &
                              (vs_adaptive["selectivity"] == "all")]

        n_cell_b = len(sub_b)
        n_cell_a = len(sub_a)
        if n_cell_b == 0 and n_cell_a == 0:
            continue

        win_vs_base = int((sub_b["ensemble_better"]).sum())
        sig_vs_base = int((sub_b["significant_05"] & sub_b["ensemble_better"]).sum())
        med_delta_base = float(sub_b["median_delta_pct"].mean()) if n_cell_b else float("nan")

        win_vs_ada = int((sub_a["ensemble_better"]).sum())
        sig_vs_ada = int((sub_a["significant_05"] & sub_a["ensemble_better"]).sum())
        med_delta_ada = float(sub_a["median_delta_pct"].mean()) if n_cell_a else float("nan")

        out_rows.append({
            "base": base,
            "n_cell": max(n_cell_b, n_cell_a),
            "win_vs_base": f"{win_vs_base}/{n_cell_b}",
            "sig_vs_base": f"{sig_vs_base}/{n_cell_b}",
            "median_delta_pct_vs_base": med_delta_base,
            "win_vs_adaptive": f"{win_vs_ada}/{n_cell_a}",
            "sig_vs_adaptive": f"{sig_vs_ada}/{n_cell_a}",
            "median_delta_pct_vs_adaptive": med_delta_ada,
            "in_4kang": base in FOUR_KANG,
        })

    df = pd.DataFrame(out_rows)
    if not df.empty:
        # 순위: vs_adaptive sig 강세 + median Δ% (음수일수록 강) 우선
        df["rank_score"] = df.apply(
            lambda r: (-int(r["sig_vs_adaptive"].split("/")[0])
                       if isinstance(r["sig_vs_adaptive"], str) else 0)
                       + (r["median_delta_pct_vs_adaptive"]
                          if pd.notna(r["median_delta_pct_vs_adaptive"]) else 0.0),
            axis=1,
        )
        df = df.sort_values("rank_score").reset_index(drop=True)
        df["rank"] = df.index + 1
        df = df.drop(columns=["rank_score"])
    return df


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Adaptive × base method ensemble paired Δ% 분석 — 5/9 morning 결과 도착 후 즉시 실행.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--input-dir", type=str, action="append", default=None,
                    help="입력 parquet/csv 검색 dir (반복). default: server CACHE + 로컬 cache.")
    ap.add_argument("--out-dir", type=str,
                    default="/Users/hyunbin/Capstone/_internal/cache/ensemble_paired",
                    help="출력 dir")
    ap.add_argument("--dry-run", action="store_true",
                    help="입력 파일 detection 만 — 실제 분석 X")
    args = ap.parse_args()

    if args.input_dir is None:
        candidates = [
            Path("/mnt/hdd0/home/capstone2026/cache/rq1"),
            Path("/Users/hyunbin/Capstone/experiments/results/cache/rq1"),
            Path("/Users/hyunbin/Capstone/_internal/cache"),
        ]
    else:
        candidates = [Path(d) for d in args.input_dir]
    input_dirs = [d for d in candidates if d.exists()]
    print(f"[scan] input_dirs: {input_dirs}", file=sys.stderr)

    found = scan_inputs(input_dirs)

    print(f"\n=== input scan ({len(CELLS)} cell × {len(BASE_METHODS)} base) ===",
          file=sys.stderr)
    n_ens_ok = 0
    n_base_ok = 0
    n_ada_ok = 0
    missing_ens: list[tuple[str, str]] = []
    missing_base: list[tuple[str, str]] = []
    missing_ada: list[str] = []
    for tag, slot in found.items():
        ens_ok = sum(1 for v in slot["ensemble"].values() if v is not None)
        base_ok = sum(1 for v in slot["base"].values() if v is not None)
        ada_ok = 1 if slot["adaptive"] else 0
        n_ens_ok += ens_ok
        n_base_ok += base_ok
        n_ada_ok += ada_ok
        if ens_ok < len(BASE_METHODS) or base_ok < len(BASE_METHODS) or not slot["adaptive"]:
            print(f"  {tag}: ens={ens_ok}/{len(BASE_METHODS)} base={base_ok}/{len(BASE_METHODS)} ada={ada_ok}",
                  file=sys.stderr)
        for b, p in slot["ensemble"].items():
            if p is None:
                missing_ens.append((tag, b))
        for b, p in slot["base"].items():
            if p is None:
                missing_base.append((tag, b))
        if not slot["adaptive"]:
            missing_ada.append(tag)

    n_ens_total = len(CELLS) * len(BASE_METHODS)
    n_base_total = len(CELLS) * len(BASE_METHODS)
    n_ada_total = len(CELLS)
    print(f"\n[summary] ensemble {n_ens_ok}/{n_ens_total}, "
          f"base {n_base_ok}/{n_base_total}, adaptive {n_ada_ok}/{n_ada_total}",
          file=sys.stderr)

    if args.dry_run:
        print(f"\n[dry-run] missing ensemble = {len(missing_ens)}, "
              f"missing base = {len(missing_base)}, missing adaptive = {len(missing_ada)}",
              file=sys.stderr)
        return 0 if (n_ens_ok > 0 and n_ada_ok > 0) else 1

    if n_ens_ok == 0 or n_ada_ok == 0:
        print(f"\n[ABORT] no ensemble or adaptive input found — 5/9 morning 결과 도착 후 재실행",
              file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    vs_base_dfs: list[pd.DataFrame] = []
    vs_ada_dfs: list[pd.DataFrame] = []

    for tag, slot in found.items():
        adaptive_p = slot["adaptive"]
        if adaptive_p is None:
            continue
        adaptive = load_table(adaptive_p)

        for base in BASE_METHODS:
            ens_p = slot["ensemble"][base]
            base_p = slot["base"][base]
            if ens_p is None:
                continue
            ensemble = load_table(ens_p)

            # vs single base (paired)
            if base_p is not None:
                base_df = load_table(base_p)
                d_b = compute_paired_vs_base(ensemble, base_df, tag, base)
                if not d_b.empty:
                    vs_base_dfs.append(d_b)

            # vs Adaptive (paired)
            d_a = compute_paired_vs_adaptive(ensemble, adaptive, tag, base)
            if not d_a.empty:
                vs_ada_dfs.append(d_a)

        print(f"  {tag}: processed {sum(1 for v in slot['ensemble'].values() if v)} ensemble base",
              file=sys.stderr)

    vs_base = pd.concat(vs_base_dfs, ignore_index=True) if vs_base_dfs else pd.DataFrame()
    vs_ada = pd.concat(vs_ada_dfs, ignore_index=True) if vs_ada_dfs else pd.DataFrame()

    if not vs_base.empty:
        vs_base = add_mc_correction(vs_base)
    if not vs_ada.empty:
        vs_ada = add_mc_correction(vs_ada)

    ranking = compute_winner_ranking(vs_base, vs_ada) \
        if (not vs_base.empty or not vs_ada.empty) else pd.DataFrame()

    out_vs_base = out_dir / "ensemble_vs_base_summary.csv"
    out_vs_ada = out_dir / "ensemble_vs_adaptive_summary.csv"
    out_rank = out_dir / "ensemble_winner_ranking.csv"

    vs_base.to_csv(out_vs_base, index=False)
    vs_ada.to_csv(out_vs_ada, index=False)
    ranking.to_csv(out_rank, index=False)

    print(f"\n=== output ===", file=sys.stderr)
    print(f"  {out_vs_base}  ({len(vs_base)} rows)", file=sys.stderr)
    print(f"  {out_vs_ada}   ({len(vs_ada)} rows)", file=sys.stderr)
    print(f"  {out_rank}     ({len(ranking)} rows)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
