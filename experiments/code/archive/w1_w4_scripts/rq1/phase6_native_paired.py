#!/usr/bin/env python3
"""Phase 6 Step 4 — paired Wilcoxon STRAT vs BERN (native hook_est 기준)."""
import json
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import scipy.stats as sst

BERN = "/mnt/hdd0/home/capstone2026/cache/rq1/phase6_bern_native_v2.parquet"
STRAT = "/mnt/hdd0/home/capstone2026/cache/rq1/phase6_strat_km20_native.parquet"
OUT = "/mnt/hdd0/home/capstone2026/cache/rq1/phase6_native_paired.json"


def main() -> None:
    bern = pq.read_table(BERN).to_pandas()
    strat = pq.read_table(STRAT).to_pandas()
    print(f"BERN: {len(bern)} rows, STRAT: {len(strat)} rows")

    bern2 = bern[["query_id", "selectivity", "q_error_hook"]].rename(
        columns={"q_error_hook": "qe_b"}
    )
    strat2 = strat[["query_id", "selectivity", "q_error_hook"]].rename(
        columns={"q_error_hook": "qe_s"}
    )
    pair = bern2.merge(strat2, on=["query_id", "selectivity"])
    print(f"paired: {len(pair)} rows")

    print()
    print("=== paired Wilcoxon STRAT vs BERN (alt: strat < bern, hook_est) ===")
    header = "{:>7s}  {:>10s}  {:>10s}  {:>7s}  {:>10s}  {:>6s}  {:>5s}  sig".format(
        "sel", "bern_med", "strat_med", "diff%", "p(less)", "better", "worse"
    )
    print(header)
    sels = sorted(pair["selectivity"].unique())
    rows = []
    for sel in sels:
        sub = pair[pair["selectivity"] == sel]
        x = sub["qe_s"].values
        y = sub["qe_b"].values
        try:
            res = sst.wilcoxon(x, y, alternative="less", zero_method="wilcox")
            p = float(res.pvalue)
        except Exception:
            p = float("nan")
        mb = float(np.median(y))
        ms = float(np.median(x))
        diff = (mb - ms) / mb * 100 if mb > 0 else float("nan")
        nb = int(np.sum(x < y))
        nw = int(np.sum(x > y))
        nt = int(np.sum(x == y))
        sig = (
            "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        )
        rows.append(
            {
                "selectivity": sel,
                "bern_median": mb,
                "strat_median": ms,
                "diff_pct": diff,
                "p_less": p,
                "n_better": nb,
                "n_worse": nw,
                "n_tie": nt,
            }
        )
        print(
            "{:>7.3f}  {:>10.4f}  {:>10.4f}  {:>+7.2f}  {:>10.4g}  {:>6d}  {:>5d}  {}".format(
                sel, mb, ms, diff, p, nb, nw, sig
            )
        )

    # Python Step 3' 결과와 비교
    print()
    print("=== 참고: Phase 6 Step 3' Python counterfactual KM20 (5 seed 평균) ===")
    py_km20 = {
        0.001: (2.5974, 2.6070, -0.37, 0.925),
        0.010: (1.5905, 1.6713, -5.08, 0.719),
        0.050: (1.1969, 1.1724, 2.04, 0.121),
        0.100: (1.1357, 1.1102, 2.25, 0.0042),
        0.300: (1.0650, 1.0569, 0.76, 0.0160),
        0.500: (1.0408, 1.0374, 0.33, 0.0157),
    }
    print("{:>7s}  {:>10s}  {:>10s}  {:>8s}  {:>10s}".format(
        "sel", "py_bern", "py_strat", "py_diff%", "py_p"
    ))
    for sel, (pb, ps, pd_, pp) in py_km20.items():
        print("{:>7.3f}  {:>10.4f}  {:>10.4f}  {:>+8.2f}  {:>10.4g}".format(
            sel, pb, ps, pd_, pp
        ))

    with open(OUT, "w") as f:
        json.dump(
            {"rows": rows, "n_paired": len(pair), "python_step3prime": py_km20},
            f,
            indent=2,
            default=str,
        )
    print()
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
