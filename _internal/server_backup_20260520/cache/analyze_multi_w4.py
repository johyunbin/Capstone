#!/usr/bin/env python3
"""W4 multi-pipeline + fixed-rate analysis (회의 자료용)."""
import json, glob
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
OUT = "/tmp/w4_multi_summary.json"


def paired_ci_pct(method_qe, ref_qe, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    valid = (~np.isnan(method_qe)) & (~np.isnan(ref_qe))
    m, b = method_qe[valid], ref_qe[valid]
    if len(m) < 30: return None
    pct = (m - b) / b * 100
    point = float(pct.mean())
    boot = np.array([rng.choice(pct, len(pct), replace=True).mean() for _ in range(n_boot)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"point_pct": point, "ci_lo": float(lo), "ci_hi": float(hi),
            "ci_excludes_0": (lo > 0) or (hi < 0), "n": int(len(m))}


def analyze_multi_vector(prefix):
    paths = list(CACHE.glob(f"{prefix}*.parquet"))
    if not paths: return None
    out = {}
    for p in paths:
        try:
            df = pq.read_table(str(p)).to_pandas()
            for (mode, sel), g in df.groupby(["mode","selectivity"]):
                key = f"{p.stem}_{mode}_sel{sel}"
                out[key] = {"median_qe": float(np.nanmedian(g["q_error"])), "n": int(len(g))}
            # bernoulli reference for paired CI
            bern = df[df["mode"]=="bernoulli"]
            for mode in df["mode"].unique():
                if mode == "bernoulli": continue
                for sel, gm in df[df["mode"]==mode].groupby("selectivity"):
                    gb = bern[bern["selectivity"]==sel]
                    if len(gb) == len(gm):
                        ci = paired_ci_pct(gm["q_error"].values, gb["q_error"].values)
                        if ci: out[f"{p.stem}_{mode}_sel{sel}_paired"] = ci
        except Exception as e:
            print(f"WARN {p}: {e}")
    return out


def analyze_fixed_rate(prefix="rq3_fixed_rate"):
    paths = list(CACHE.glob(f"{prefix}*.parquet"))
    if not paths: return None
    out = {}
    for p in paths:
        try:
            df = pq.read_table(str(p)).to_pandas()
            for (rate, sel), g in df.groupby(["rate","selectivity"] if "rate" in df.columns else ["mode","selectivity"]):
                out[f"{p.stem}_rate{rate}_sel{sel}"] = {"median_qe": float(np.nanmedian(g["q_error"])), "n": int(len(g))}
        except Exception as e:
            print(f"WARN {p}: {e}")
    return out


def main():
    res = {}
    res["multi_vector_deep_sift"] = analyze_multi_vector("rq2_partsupp_deep_sift_10_4way")
    res["multi_vector_deep_wiki"] = analyze_multi_vector("rq2_partsupp_deep_wiki_10_4way")
    res["multi_join_deep_wiki"] = analyze_multi_vector("rq2_multi_join_deep_wiki")
    res["fixed_rate_baselines"] = analyze_fixed_rate()
    Path(OUT).write_text(json.dumps(res, indent=2, default=str))
    print(f"[done] saved {OUT}")


if __name__ == "__main__":
    main()
