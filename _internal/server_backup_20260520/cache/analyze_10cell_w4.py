#!/usr/bin/env python3
"""W4 10-cell matrix aggregator — DEEP/SIFT/SSN/WIKI/YFCC × sf1/sf10 = 10 single cells.
Produces: per-cell paired CI + Cohen d for each method × selectivity.
Patched (2026-05-08):
  - shape mismatch fix (some methods have 5-seeds × 200q = 1000 per sel, bern is 500)
    → average q_error per query_id across seeds, then paired vs bern
  - DATASETS reduced to 5 (drop YFCC_DL → 10-cell focus)
  - METHODS expanded to all 30 (add halton/hammersley/reservoir/distance_shell/kde_pilot/
    importance_sampling/faiss_ivf)
Output: /tmp/w4_10cell_summary.csv
"""
import glob
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
DATASETS = ["DEEP", "SIFT", "SSN", "WIKI", "YFCC"]
SCALES = [1, 10]
METHODS = (
    "hilbert hybrid minibatch minibatch_partial kdtree zorder pca1d gmm lsh pq sobol "
    "distance_shell random_proj kde_pilot sparse_rp importance_sampling hdbscan birch "
    "dbscan agglomerative hierarchical_kmeans faiss_ivf pca_kmeans kmeans_pp coresets spectral "
    "halton hammersley reservoir optics"
).split()


def paired_ci_pct(method_qe, bern_qe, n_boot=1000, seed=42):
    """paired bootstrap 95% CI of (method - bern) / bern * 100.
    Both arrays must be same length & aligned by query_id (handled in cell_summary)."""
    rng = np.random.default_rng(seed)
    if len(method_qe) != len(bern_qe):
        # safety net — should not happen after cell_summary alignment
        n = min(len(method_qe), len(bern_qe))
        method_qe = method_qe[:n]
        bern_qe = bern_qe[:n]
    valid = (~np.isnan(method_qe)) & (~np.isnan(bern_qe)) & (bern_qe > 1e-9)
    m, b = method_qe[valid], bern_qe[valid]
    if len(m) < 30:
        return None
    pct = (m - b) / b * 100
    point = float(pct.mean())
    boot = np.array([rng.choice(pct, len(pct), replace=True).mean() for _ in range(n_boot)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    cd = float(point / pct.std()) if pct.std() > 1e-9 else 0.0
    return {"point_pct": point, "ci_lo": float(lo), "ci_hi": float(hi),
            "ci_excludes_0": (lo > 0) or (hi < 0), "cohens_d": cd, "n": int(len(m))}


def load_cell(ds, sf):
    """Load all rq3_<ds>_sf{sf}_<method>.parquet for one cell. Returns dict[method]=df."""
    pattern = str(CACHE / f"rq3_{ds}_sf{sf}_*.parquet")
    out = {}
    for f in glob.glob(pattern):
        method = Path(f).stem.replace(f"rq3_{ds}_sf{sf}_", "")
        if method == "random20":
            continue
        try:
            df = pq.read_table(f).to_pandas()
            out[method] = df
        except Exception as e:
            print(f"WARN read fail {f}: {e}")
    return out


def aligned_qe_by_query(df, sel):
    """Average q_error per query_id at given selectivity (across seeds if any)."""
    g = df[df["selectivity"] == sel]
    if "query_id" in g.columns:
        agg = g.groupby("query_id")["q_error"].mean()
        # sort by query_id for stable order
        return agg.sort_index().values, agg.index.values
    return g["q_error"].values, np.arange(len(g))


def cell_summary(ds, sf):
    cell = load_cell(ds, sf)
    if not cell:
        return None
    rq2_path = CACHE / f"rq2_alloc_{ds}_sf{sf}_5mode.parquet"
    bern_qe_by_sel = {}  # sel -> dict[query_id]=qe
    if rq2_path.exists():
        try:
            bern_df = pq.read_table(str(rq2_path)).to_pandas()
            bern_df = bern_df[bern_df["mode"] == "bernoulli"]
            for sel in sorted(bern_df["selectivity"].unique()):
                g = bern_df[bern_df["selectivity"] == sel]
                if "query_id" in g.columns:
                    agg = g.groupby("query_id")["q_error"].mean().sort_index()
                    bern_qe_by_sel[float(sel)] = agg
                else:
                    bern_qe_by_sel[float(sel)] = pd.Series(g["q_error"].values)
        except Exception as e:
            print(f"WARN rq2 read fail {ds} sf{sf}: {e}")
    rows = []
    for method, df in cell.items():
        if "selectivity" not in df.columns or "q_error" not in df.columns:
            continue
        for sel in sorted(df["selectivity"].unique()):
            sel_f = float(sel)
            method_agg = df[df["selectivity"] == sel].groupby("query_id")["q_error"].mean().sort_index() if "query_id" in df.columns else pd.Series(df[df["selectivity"] == sel]["q_error"].values)
            bern_agg = bern_qe_by_sel.get(sel_f)
            ci = None
            if bern_agg is not None:
                # align on common query_id index
                common = method_agg.index.intersection(bern_agg.index) if hasattr(method_agg, 'index') else None
                if common is not None and len(common) >= 30:
                    m_aligned = method_agg.loc[common].values
                    b_aligned = bern_agg.loc[common].values
                    ci = paired_ci_pct(m_aligned, b_aligned)
            method_qe = method_agg.values if hasattr(method_agg, 'values') else method_agg
            rows.append({
                "dataset": ds, "sf": sf, "method": method, "selectivity": sel_f,
                "median_qe": float(np.nanmedian(method_qe)),
                "mean_qe": float(np.nanmean(method_qe)),
                "n_valid": int((~np.isnan(method_qe)).sum()),
                "paired_pct_vs_bern": ci.get("point_pct") if ci else None,
                "ci_lo": ci.get("ci_lo") if ci else None,
                "ci_hi": ci.get("ci_hi") if ci else None,
                "ci_excludes_0": ci.get("ci_excludes_0") if ci else None,
                "cohens_d": ci.get("cohens_d") if ci else None,
            })
    return rows


def main():
    all_rows = []
    for ds in DATASETS:
        for sf in SCALES:
            print(f"\n=== {ds} sf{sf} ===")
            rows = cell_summary(ds, sf) or []
            print(f"   {len(rows)} method×sel rows")
            all_rows.extend(rows)
    df = pd.DataFrame(all_rows)
    out_csv = "/tmp/w4_10cell_summary.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n[done] {len(df)} rows → {out_csv}")
    pivot = df[(df["selectivity"] == 0.10) & (df["method"].isin(["hilbert","hybrid","minibatch_partial","hdbscan"]))]
    pivot = pivot.pivot_table(index=["dataset","sf"], columns="method", values="paired_pct_vs_bern")
    print("\n=== 4강 method @ sel=0.10 (paired Δ% vs bern) ===")
    print(pivot.to_string())


if __name__ == "__main__":
    main()
