"""
Single 4강 vs Adaptive Sampling paired Δ% 분석.
paired key = (selectivity, seed, query_id)
분모 = bernoulli q_error from rq1_<DS>_sf<N>_km20.parquet

10 cell × 5 method × 5 sel × 5 seed × 100 query → mean Δ%
+ paired Wilcoxon signed-rank test per (cell, method, sel)
"""
import os
import json
import numpy as np
import pandas as pd
from scipy import stats

CACHE = "/mnt/hdd0/home/capstone2026/cache/rq1"

DATASETS = ["DEEP", "SIFT", "SSN", "WIKI", "YFCC"]
SCALES = ["sf1", "sf10"]
METHODS = ["hdbscan", "minibatch_partial", "hilbert", "sparse_rp", "adaptive"]
METHOD_LABEL = {
    "hdbscan": "HDBSCAN",
    "minibatch_partial": "MB_partial",
    "hilbert": "Hilbert",
    "sparse_rp": "sparse_rp",
    "adaptive": "Adaptive",
}
SEL = [0.01, 0.05, 0.10, 0.30, 0.50]
PAIR_KEY = ["selectivity", "seed", "query_id"]


def load_bern(ds, scale):
    path = f"{CACHE}/rq1_{ds}_{scale}_km20.parquet"
    df = pd.read_parquet(path)
    df = df[df["mode"] == "bernoulli"].copy()
    df = df.rename(columns={"q_error": "qerr_bern"})
    return df[PAIR_KEY + ["qerr_bern"]]


def load_method(ds, scale, method):
    path = f"{CACHE}/rq3_{ds}_{scale}_{method}.parquet"
    df = pd.read_parquet(path)
    df = df.rename(columns={"q_error": f"qerr_{method}"})
    return df[PAIR_KEY + [f"qerr_{method}"]]


def main():
    summary_rows = []   # cell × method × sel mean Δ%
    cell_rows = []      # cell × method (mean over 5 sel)
    sign_rows = []      # cell × method × sel — sign consistency over 5 seed
    wilcoxon_rows = []  # cell × method × sel — paired Wilcoxon p

    for ds in DATASETS:
        for scale in SCALES:
            cell = f"{ds}_{scale}"
            print(f"\n=== {cell} ===")
            try:
                bern = load_bern(ds, scale)
            except Exception as e:
                print(f"  [skip] {cell}: {e}")
                continue
            print(f"  bern shape: {bern.shape}")
            for method in METHODS:
                try:
                    md = load_method(ds, scale, method)
                except Exception as e:
                    print(f"  [skip] {cell}/{method}: {e}")
                    continue
                merged = bern.merge(md, on=PAIR_KEY, how="inner")
                col_method = f"qerr_{method}"
                # Δ% = (q_error[method] - q_error[bern]) / q_error[bern] * 100
                merged["delta_pct"] = (
                    (merged[col_method] - merged["qerr_bern"]) / merged["qerr_bern"] * 100
                )
                method_label = METHOD_LABEL[method]
                # per-sel mean Δ% (over 5 seed × 100 query = 500 paired rows)
                for sel in SEL:
                    sub = merged[np.isclose(merged["selectivity"], sel)]
                    if len(sub) == 0:
                        continue
                    mean_d = sub["delta_pct"].mean()
                    median_d = sub["delta_pct"].median()
                    n = len(sub)
                    summary_rows.append({
                        "cell": cell,
                        "method": method_label,
                        "selectivity": sel,
                        "n_paired": n,
                        "mean_delta_pct": mean_d,
                        "median_delta_pct": median_d,
                        "std_delta_pct": sub["delta_pct"].std(),
                    })
                    # paired Wilcoxon signed-rank: H0 method == bern
                    diffs = sub[col_method].values - sub["qerr_bern"].values
                    # filter zero diffs
                    nz = diffs[diffs != 0]
                    if len(nz) >= 10:
                        try:
                            w_stat, w_p = stats.wilcoxon(
                                sub[col_method].values, sub["qerr_bern"].values,
                                zero_method="wilcox", alternative="two-sided"
                            )
                        except Exception:
                            w_stat, w_p = np.nan, np.nan
                    else:
                        w_stat, w_p = np.nan, np.nan
                    wilcoxon_rows.append({
                        "cell": cell,
                        "method": method_label,
                        "selectivity": sel,
                        "n_paired": n,
                        "mean_delta_pct": mean_d,
                        "wilcoxon_stat": w_stat,
                        "wilcoxon_p": w_p,
                        "significant_05": (w_p < 0.05) if not np.isnan(w_p) else False,
                    })
                    # sign consistency: over 5 seeds, count of seeds with mean Δ% < 0
                    seed_means = sub.groupby("seed")["delta_pct"].mean()
                    n_neg = int((seed_means < 0).sum())
                    n_pos = int((seed_means > 0).sum())
                    sign_rows.append({
                        "cell": cell,
                        "method": method_label,
                        "selectivity": sel,
                        "n_seed_negative": n_neg,
                        "n_seed_positive": n_pos,
                        "n_seed_total": len(seed_means),
                        "sign_consistent": max(n_neg, n_pos) == len(seed_means),
                    })
                # cell-level (mean over 5 sel × 5 seed × 100 query)
                cell_mean = merged["delta_pct"].mean()
                cell_med = merged["delta_pct"].median()
                cell_rows.append({
                    "cell": cell,
                    "method": method_label,
                    "n_paired_total": len(merged),
                    "mean_delta_pct": cell_mean,
                    "median_delta_pct": cell_med,
                    "std_delta_pct": merged["delta_pct"].std(),
                })
                print(f"  {method_label:12s}: n={len(merged):5d}  mean Δ%={cell_mean:+7.2f}  median Δ%={cell_med:+7.2f}")

    out_dir = "/mnt/hdd0/home/capstone2026/cache/single_adaptive_paired"
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(summary_rows).to_csv(f"{out_dir}/single_adaptive_paired_summary.csv", index=False)
    pd.DataFrame(cell_rows).to_csv(f"{out_dir}/single_adaptive_paired_cell.csv", index=False)
    pd.DataFrame(sign_rows).to_csv(f"{out_dir}/single_adaptive_paired_sign.csv", index=False)
    pd.DataFrame(wilcoxon_rows).to_csv(f"{out_dir}/single_adaptive_paired_wilcoxon.csv", index=False)
    print(f"\n=== output: {out_dir} ===")
    print("  - single_adaptive_paired_summary.csv")
    print("  - single_adaptive_paired_cell.csv")
    print("  - single_adaptive_paired_sign.csv")
    print("  - single_adaptive_paired_wilcoxon.csv")


if __name__ == "__main__":
    main()
