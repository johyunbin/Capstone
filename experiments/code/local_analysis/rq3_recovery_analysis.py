#!/usr/bin/env python3
"""
RQ3 1차 (offline 4종 + RANDOM20/KM20 baseline) 종합 recovery rate 분석.

입력: experiments/results/rq3_agnostic/rq3_*.parquet
산출: experiments/results/rq3_agnostic/recovery_summary.csv
       + 콘솔에 7-way 표 출력

사용:
    python3 experiments/code/local_analysis/rq3_recovery_analysis.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recovery_rate import (  # noqa: E402
    paired_wilcoxon_with_bh_fdr, summarize_method,
)

RESULTS = Path("/Users/hyunbin/Capstone/experiments/results/rq3_agnostic")
METHODS = ["minibatch", "random_proj", "hilbert", "lsh"]


def load_all() -> pd.DataFrame:
    """모든 측정 parquet 을 long-form 으로 합침. BERN baseline 은 평균 대신 random20 측정의 값 사용."""
    frames = []
    files = {
        "rq3_random20.parquet": None,         # DEEP only
        "rq3_random20_sift.parquet": None,    # SIFT only
        "rq3_km20.parquet": None,
        "rq3_minibatch.parquet": None,
        "rq3_random_proj.parquet": None,
        "rq3_hilbert.parquet": None,
        "rq3_lsh.parquet": None,
    }
    for fname in files:
        path = RESULTS / fname
        if path.exists():
            df = pd.read_parquet(path)
            df["source"] = fname.replace(".parquet", "")
            frames.append(df)
        else:
            print(f"⚠️ missing: {fname}")
    return pd.concat(frames, ignore_index=True)


def deduplicate_bernoulli(df: pd.DataFrame) -> pd.DataFrame:
    """여러 측정에서 BERN baseline 이 중복 측정됨 — 한 source 만 보존 (random20 wrapper).

    이렇게 하면 paired Wilcoxon 시 같은 query × seed 에서 BERN 측정값이 1개 row 로 align.
    """
    bern = df[df["mode"] == "bernoulli"]
    # DEEP: rq3_random20 의 BERN, SIFT: rq3_random20_sift 의 BERN
    keep_bern = bern[
        ((bern["dataset"] == "DEEP") & (bern["source"] == "rq3_random20"))
        | ((bern["dataset"] == "SIFT") & (bern["source"] == "rq3_random20_sift"))
    ].copy()
    non_bern = df[df["mode"] != "bernoulli"]
    return pd.concat([keep_bern, non_bern], ignore_index=True)


def main():
    print("=" * 70)
    print("RQ3 종합 recovery rate 분석 — 1차 4종 + RANDOM20/KM20 baseline")
    print("=" * 70)

    df_all = load_all()
    df = deduplicate_bernoulli(df_all)
    print(f"\n[load] {len(df_all):,} → {len(df):,} rows (BERN dedup)")
    print(df.groupby(["dataset", "mode"]).size().unstack(fill_value=0))

    # ===== 1. 각 method 의 recovery rate =====
    print("\n" + "=" * 70)
    print("[1] Recovery Rate per (dataset × selectivity)")
    print("    rr = (method_q − random20_q) / (km20_q − random20_q)")
    print("=" * 70)

    all_summaries = []
    for method in METHODS:
        s = summarize_method(df, method=method)
        s["method"] = method
        all_summaries.append(s)
        print(f"\n--- {method} ---")
        # 핵심 컬럼만
        print(s[["dataset", "sel", "method_q", "random20_q", "km20_q",
                 "recovery", "metric", "method_minus_random_pct"]].to_string(index=False))

    summary_df = pd.concat(all_summaries, ignore_index=True)
    summary_df.to_csv(RESULTS / "recovery_summary.csv", index=False)
    print(f"\n[saved] {RESULTS / 'recovery_summary.csv'}")

    # ===== 2. 7-way 표 — recovery rate × dataset × selectivity =====
    print("\n" + "=" * 70)
    print("[2] 7-way 표 — Recovery Rate by (method × dataset × sel)")
    print("=" * 70)
    pivot = summary_df.pivot_table(
        index=["dataset", "sel"], columns="method", values="recovery",
    ).round(3)
    print(pivot)

    # ===== 3. paired Wilcoxon vs RANDOM20 (분모) + vs BERN (RQ1/RQ2 metric) =====
    print("\n" + "=" * 70)
    print("[3] paired Wilcoxon + BH-FDR vs RANDOM20 (분모)")
    print("=" * 70)
    pairs_vs_rand = [(m, "random20") for m in METHODS]
    out_rand = paired_wilcoxon_with_bh_fdr(
        df, compare_pairs=pairs_vs_rand, alternative="less",
    )
    print(out_rand.to_string(index=False))

    print("\n" + "=" * 70)
    print("[4] paired Wilcoxon + BH-FDR vs BERN (RQ1/RQ2 비교)")
    print("=" * 70)
    pairs_vs_bern = [(m, "bernoulli") for m in METHODS] + [("km20", "bernoulli"), ("random20", "bernoulli")]
    out_bern = paired_wilcoxon_with_bh_fdr(
        df, compare_pairs=pairs_vs_bern, alternative="less",
    )
    print(out_bern.to_string(index=False))

    # save
    out_rand.to_csv(RESULTS / "wilcoxon_vs_random20.csv", index=False)
    out_bern.to_csv(RESULTS / "wilcoxon_vs_bern.csv", index=False)
    print(f"\n[saved] {RESULTS / 'wilcoxon_vs_random20.csv'}")
    print(f"[saved] {RESULTS / 'wilcoxon_vs_bern.csv'}")

    # ===== 5. dataset 합산 (sel 별 평균 recovery) =====
    print("\n" + "=" * 70)
    print("[5] Recovery Rate dataset 평균 (selectivity 별)")
    print("=" * 70)
    avg = summary_df.groupby(["method", "sel"])["recovery"].mean().unstack().round(3)
    print(avg.T)

    print("\n✓ 분석 완료")


if __name__ == "__main__":
    main()
