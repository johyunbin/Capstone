#!/usr/bin/env python3
"""W4 15-cell matrix aggregator — 12 single (DEEP/SIFT/SSN/WIKI/YFCC/YFCC_DL × sf1/sf10) + 3 multi.
Produces: per-cell paired CI + Cohen d for each method × selectivity.
Output: /tmp/w4_15cell_summary.csv + .md
"""
import glob
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
DATASETS = ["DEEP", "SIFT", "SSN", "WIKI", "YFCC", "YFCC_DL"]
SCALES = [1, 10]
METHODS = (
    "hilbert hybrid minibatch minibatch_partial kdtree zorder pca1d gmm lsh pq sobol "
    "distance_shell random_proj kde_pilot sparse_rp importance_sampling hdbscan birch "
    "dbscan agglomerative hierarchical_kmeans faiss_ivf pca_kmeans kmeans_pp coresets spectral"
).split()


def paired_ci_pct(method_qe, bern_qe, n_boot=1000, seed=42):
    """paired bootstrap 95% CI of (method - bern) / bern * 100."""
    rng = np.random.default_rng(seed)
    valid = (~np.isnan(method_qe)) & (~np.isnan(bern_qe))
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


def cell_summary(ds, sf):
    cell = load_cell(ds, sf)
    if not cell:
        return None
    # bernoulli baseline parquet (rq2 alloc 5mode 의 bernoulli mode 추출)
    rq2_path = CACHE / f"rq2_alloc_{ds}_sf{sf}_5mode.parquet"
    bern_qe_by_sel = {}
    if rq2_path.exists():
        try:
            bern_df = pq.read_table(str(rq2_path)).to_pandas()
            bern_df = bern_df[bern_df["mode"] == "bernoulli"]
            for sel, g in bern_df.groupby("selectivity"):
                bern_qe_by_sel[float(sel)] = g["q_error"].values
        except Exception as e:
            print(f"WARN rq2 read fail {ds} sf{sf}: {e}")
    rows = []
    for method, df in cell.items():
        if "selectivity" not in df.columns or "q_error" not in df.columns:
            continue
        for sel, g in df.groupby("selectivity"):
            sel_f = float(sel)
            method_qe = g["q_error"].values
            bern_qe = bern_qe_by_sel.get(sel_f)
            ci = paired_ci_pct(method_qe, bern_qe) if bern_qe is not None else None
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
    out_csv = "/tmp/w4_15cell_summary.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n[done] {len(df)} rows → {out_csv}")
    # Per-cell pivot — 4강 method effect at sel=0.10
    pivot = df[(df["selectivity"] == 0.10) & (df["method"].isin(["hilbert","hybrid","minibatch_partial","hdbscan"]))]
    pivot = pivot.pivot_table(index=["dataset","sf"], columns="method", values="paired_pct_vs_bern")
    print("\n=== 4강 method @ sel=0.10 (paired Δ% vs bern) ===")
    print(pivot.to_string())


if __name__ == "__main__":
    main()
