"""
Head-to-head paired Wilcoxon: 4강 vs Adaptive (NOT vs BERN).
For each (cell, method, sel): compare q_error[method] vs q_error[adaptive] on same paired (sel, seed, query_id) keys.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

CACHE = "/mnt/hdd0/home/capstone2026/cache/rq1"
DATASETS = ["DEEP", "SIFT", "SSN", "WIKI", "YFCC"]
SCALES = ["sf1", "sf10"]
METHODS = ["hdbscan", "minibatch_partial", "hilbert", "sparse_rp"]
METHOD_LABEL = {
    "hdbscan": "HDBSCAN",
    "minibatch_partial": "MB_partial",
    "hilbert": "Hilbert",
    "sparse_rp": "sparse_rp",
}
SEL = [0.01, 0.05, 0.10, 0.30, 0.50]
PAIR_KEY = ["selectivity", "seed", "query_id"]


def load_method(ds, scale, method):
    path = f"{CACHE}/rq3_{ds}_{scale}_{method}.parquet"
    df = pd.read_parquet(path)
    df = df.rename(columns={"q_error": f"qerr_{method}"})
    return df[PAIR_KEY + [f"qerr_{method}"]]


def main():
    rows = []
    cell_rows = []
    for ds in DATASETS:
        for scale in SCALES:
            cell = f"{ds}_{scale}"
            print(f"\n=== {cell} ===")
            try:
                adap = load_method(ds, scale, "adaptive")
            except Exception as e:
                print(f"  [skip] {e}")
                continue
            for method in METHODS:
                md = load_method(ds, scale, method)
                merged = adap.merge(md, on=PAIR_KEY, how="inner")
                col_method = f"qerr_{method}"
                col_adap = "qerr_adaptive"
                # drop NaN/inf paired rows (q_error 계산 실패 케이스)
                merged = merged.dropna(subset=[col_method, col_adap])
                merged = merged[
                    np.isfinite(merged[col_method]) & np.isfinite(merged[col_adap])
                ].copy()
                # Δ% method vs adaptive: (q_error[method] - q_error[adaptive]) / q_error[adaptive] * 100
                merged["delta_pct_h2h"] = (
                    (merged[col_method] - merged[col_adap]) / merged[col_adap] * 100
                )
                method_label = METHOD_LABEL[method]

                # cell-level
                cell_mean = merged["delta_pct_h2h"].mean()
                cell_med = merged["delta_pct_h2h"].median()
                # paired Wilcoxon over all 2500 pairs
                try:
                    w_stat_all, w_p_all = stats.wilcoxon(
                        merged[col_method].values, merged[col_adap].values,
                        zero_method="wilcox", alternative="two-sided"
                    )
                except Exception:
                    w_stat_all, w_p_all = np.nan, np.nan
                # n method better (lower q_error)
                n_better = int((merged[col_method] < merged[col_adap]).sum())
                n_total = len(merged)
                cell_rows.append({
                    "cell": cell,
                    "method": method_label,
                    "n_paired_total": n_total,
                    "mean_delta_pct_h2h": cell_mean,
                    "median_delta_pct_h2h": cell_med,
                    "n_better": n_better,
                    "p_better": n_better / n_total,
                    "wilcoxon_p": w_p_all,
                    "significant_05": (w_p_all < 0.05) if not np.isnan(w_p_all) else False,
                    "method_better": cell_med < 0,
                })
                print(f"  {method_label:12s}: median Δ%h2h={cell_med:+7.2f}  p_better={n_better/n_total:.3f}  Wilcoxon p={w_p_all:.2e}")

                # per-sel
                for sel in SEL:
                    sub = merged[np.isclose(merged["selectivity"], sel)]
                    if len(sub) == 0:
                        continue
                    mean_d = sub["delta_pct_h2h"].mean()
                    med_d = sub["delta_pct_h2h"].median()
                    try:
                        w_stat, w_p = stats.wilcoxon(
                            sub[col_method].values, sub[col_adap].values,
                            zero_method="wilcox", alternative="two-sided"
                        )
                    except Exception:
                        w_stat, w_p = np.nan, np.nan
                    rows.append({
                        "cell": cell,
                        "method": method_label,
                        "selectivity": sel,
                        "n_paired": len(sub),
                        "mean_delta_pct_h2h": mean_d,
                        "median_delta_pct_h2h": med_d,
                        "wilcoxon_p": w_p,
                        "significant_05": (w_p < 0.05) if not np.isnan(w_p) else False,
                    })

    out_dir = "/mnt/hdd0/home/capstone2026/cache/single_adaptive_paired"
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(rows).to_csv(f"{out_dir}/single_adaptive_h2h_per_sel.csv", index=False)
    pd.DataFrame(cell_rows).to_csv(f"{out_dir}/single_adaptive_h2h_per_cell.csv", index=False)
    print(f"\n=== output ===")
    print("  - single_adaptive_h2h_per_sel.csv  (40 rows × 5 sel = 200)")
    print("  - single_adaptive_h2h_per_cell.csv (40 rows)")

    # narrative quick summary
    cdf = pd.DataFrame(cell_rows)
    print("\n=== method 별 win count (cell-level median Δ% < 0 기준) ===")
    print(cdf.groupby("method")[["method_better", "significant_05"]].sum())
    print("\n=== method 별 평균 median Δ% (cell-level mean) ===")
    print(cdf.groupby("method")["median_delta_pct_h2h"].agg(["mean", "median", "min", "max"]).round(2))


if __name__ == "__main__":
    main()
