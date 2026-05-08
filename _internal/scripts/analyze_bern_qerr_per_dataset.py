#!/usr/bin/env python3
"""Compare BERN qerr across datasets to confirm SSN++ ceiling.

Reads rq1_<DS>_sf{1,10}_km20.parquet which includes mode='bernoulli'.
Computes mean q_error per (dataset, sel) for BERN.
"""
import pandas as pd
import os, glob

CACHE = "/mnt/hdd0/home/capstone2026/cache/rq1"

candidates = [
    "DEEP_sf1", "DEEP_sf10",
    "SIFT_sf1", "SIFT_sf10",
    "SSN_sf1", "SSN_sf10",
    "WIKI_sf1",
    "YFCC_sf1",
]

rows = []
for c in candidates:
    p = f"{CACHE}/rq1_{c}_km20.parquet"
    if not os.path.exists(p):
        # try alternate
        alt = f"{CACHE}/rq1_{c}_km_k.parquet"
        if not os.path.exists(alt):
            print(f"  [WARN] {c}: not found")
            continue
        p = alt
    df = pd.read_parquet(p)
    if "mode" not in df.columns:
        print(f"  [WARN] {c}: no mode col, cols={list(df.columns)}")
        continue
    bern = df[df["mode"] == "bernoulli"]
    km20 = df[df["mode"] == "km20"]
    if len(bern) == 0:
        print(f"  [WARN] {c}: no bernoulli mode (modes={df['mode'].unique()})")
        continue
    for sel, g in bern.groupby("selectivity"):
        g_km = km20[km20["selectivity"] == sel]
        rows.append({
            "dataset": c,
            "selectivity": float(sel),
            "n_bern": len(g),
            "qerr_bernoulli_mean": float(g["q_error"].mean()),
            "qerr_bernoulli_p50": float(g["q_error"].median()),
            "qerr_bernoulli_p90": float(g["q_error"].quantile(0.90)),
            "qerr_km20_mean": float(g_km["q_error"].mean()) if len(g_km) > 0 else None,
            "qerr_km20_p50": float(g_km["q_error"].median()) if len(g_km) > 0 else None,
        })

df_out = pd.DataFrame(rows).sort_values(["dataset", "selectivity"])

# Pivot for narrative — focus on sel=0.10 main + sel=0.01 ceiling
piv_bern = df_out.pivot_table(index="dataset", columns="selectivity", values="qerr_bernoulli_mean")
print("BERN q_error mean by (dataset, sel):")
print(piv_bern.to_string(float_format=lambda x: f"{x:.4f}"))

print("\n[KM20-BERN ratio (lower→ KM20 oracle improves) by (dataset, sel)]:")
df_out["km20_to_bern_ratio"] = df_out["qerr_km20_mean"] / df_out["qerr_bernoulli_mean"]
piv_ratio = df_out.pivot_table(index="dataset", columns="selectivity", values="km20_to_bern_ratio")
print(piv_ratio.to_string(float_format=lambda x: f"{x:.4f}"))

print("\n[BERN qerr at sel=0.10 (W4 main reference)]:")
ref = df_out[df_out["selectivity"] == 0.10][["dataset", "qerr_bernoulli_mean", "qerr_km20_mean"]].sort_values("qerr_bernoulli_mean")
print(ref.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

df_out.to_csv("/tmp/bern_qerr_per_dataset.csv", index=False)
print("\nWrote /tmp/bern_qerr_per_dataset.csv")
