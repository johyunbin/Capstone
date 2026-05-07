#!/usr/bin/env python3
"""
RQ3 cross-scale 비교 — 1M vs 8M.

8M sensitivity (5/7 02:30~03:46) 산출 + 1M 1차 측정 산출 결합.

1M / 8M 양쪽에 측정된 5 method (hilbert / lsh / minibatch / random_proj / zorder) 의
q_error mean 을 selectivity (s=0.1, 0.3 — 8M 측정 cell) 별로 비교.

  목적:
   - cross-scale 단조성: 1M 효과가 8M 에서 재현되는가?
   - method ranking 안정성: 1M best method 가 8M 에서도 best 인가?

산출:
   experiments/results/rq3_agnostic/rq3_8m_cross_scale.csv
   experiments/results/rq3_agnostic/rq3_8m_cross_scale.md
"""
from __future__ import annotations

import glob
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "rq3_agnostic"

# 1M / 8M 양쪽에 측정된 method (5)
COMMON_METHODS = ["hilbert", "lsh", "minibatch", "random_proj", "zorder"]
# 8M 측정 selectivity (1M 도 같은 sel 측정)
TARGET_SELS = [0.1, 0.3]


def load_1m(method: str) -> pd.DataFrame:
    path = RESULTS / f"rq3_{method}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    df = df[df["selectivity"].isin(TARGET_SELS)].copy()
    df["scale"] = "1M"
    return df


def load_8m(method: str) -> pd.DataFrame:
    path = RESULTS / f"rq3_8m_{method}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    df["scale"] = "8M"
    return df


def main() -> None:
    rows = []
    for method in COMMON_METHODS:
        df1 = load_1m(method)
        df8 = load_8m(method)
        if df1.empty:
            print(f"[skip] {method}: 1M parquet 없음")
            continue
        if df8.empty:
            print(f"[skip] {method}: 8M parquet 없음")
            continue

        for sel in TARGET_SELS:
            # 1M DEEP only (8M 은 DEEP 만 측정)
            d1 = df1[(df1["dataset"] == "DEEP") & (df1["selectivity"] == sel)]
            d8 = df8[(df8["dataset"] == "DEEP_8M") & (df8["selectivity"] == sel)]
            if d1.empty or d8.empty:
                continue

            mean_1m = d1["q_error"].mean()
            mean_8m = d8["q_error"].mean()
            std_1m = d1["q_error"].std()
            std_8m = d8["q_error"].std()
            rows.append({
                "method": method,
                "sel": sel,
                "mean_q_error_1M": round(mean_1m, 4),
                "mean_q_error_8M": round(mean_8m, 4),
                "std_q_error_1M": round(std_1m, 4),
                "std_q_error_8M": round(std_8m, 4),
                "delta_8M_minus_1M": round(mean_8m - mean_1m, 4),
                "delta_pct": round((mean_8m - mean_1m) / mean_1m * 100, 2),
                "n_1M": len(d1),
                "n_8M": len(d8),
            })

    if not rows:
        print("[error] 1M/8M 공통 데이터 없음")
        return

    df_out = pd.DataFrame(rows)
    csv_path = RESULTS / "rq3_8m_cross_scale.csv"
    df_out.to_csv(csv_path, index=False)
    print(f"[saved] {csv_path}")

    # method ranking by 1M mean and 8M mean (lower q_error = better)
    print("\n=== method ranking (mean q_error, lower = better) ===")
    for sel in TARGET_SELS:
        sub = df_out[df_out["sel"] == sel].sort_values("mean_q_error_1M")
        if sub.empty:
            continue
        print(f"\nsel={sel}:")
        print(sub[["method", "mean_q_error_1M", "mean_q_error_8M",
                   "delta_pct"]].to_string(index=False))

    # markdown 보고서
    md = ["# RQ3 Cross-Scale (1M vs 8M) — 5/7 03:55", ""]
    md.append(f"> 5 common method × 2 sel ({TARGET_SELS}) × 2 scale (1M, 8M) = 측정값 비교")
    md.append("")
    md.append("## 1M vs 8M mean q_error")
    md.append("")
    md.append("| method | sel | 1M mean | 8M mean | Δ (8M-1M) | Δ% |")
    md.append("|--------|-----|--------:|--------:|----------:|---:|")
    for _, r in df_out.sort_values(["sel", "method"]).iterrows():
        md.append(
            f"| {r['method']} | {r['sel']} | {r['mean_q_error_1M']:.4f} | "
            f"{r['mean_q_error_8M']:.4f} | {r['delta_8M_minus_1M']:+.4f} | "
            f"{r['delta_pct']:+.2f}% |"
        )
    md.append("")
    md.append("## 해석")
    md.append("")
    md.append("- 8M q_error 가 1M 보다 일관되게 작으면 → 큰 데이터에서 sampling 정확도 향상 (cardinality estimation 의 자연 안정화).")
    md.append("- method 간 ranking 이 1M / 8M 에서 일치하면 → 본 연구의 method 우수성 결론이 cross-scale robust.")
    md.append("- 차이 큰 method 가 있으면 → scale-dependent 효과, future work 의 명시적 limitation.")

    md_path = RESULTS / "rq3_8m_cross_scale.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"\n[saved] {md_path}")
    print(f"\n총 {len(df_out)} (method × sel) cell 측정")


if __name__ == "__main__":
    main()
