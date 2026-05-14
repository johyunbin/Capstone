#!/usr/bin/env python3
"""
RQ3 Per-Query Method Ranking — query 난이도 vs method 적합성 분석.

각 query 마다 method 들을 q_error 로 ranking → 어떤 query 에서 어느 method 가
이기는지 분석. 다음 narrative 답변:

1. **\"Hilbert 가 평균 best 인데, 어떤 query 에서는 약한가?\"** — query 의 BERN
   q_error (난이도) 에 따라 best method 가 달라지는지 (난이도 stratification).
2. **\"method-disagreement queries\"** — best/worst method 의 q_error 차이가 큰
   query 들의 특성.
3. **\"per-query best method 의 분포\"** — 7-way 중 어느 method 가 most often best?

산출:
  - rq3_per_query_ranking.csv  (query × method × q_error + ranking)
  - rq3_query_difficulty_method.csv  (query 난이도 별 best method)
  - rq3_per_query_ranking.md   (narrative)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESULTS = ROOT / "Capstone" / "experiments" / "results" / "rq3_agnostic"
if not RESULTS.exists():
    RESULTS = Path(__file__).resolve().parent.parent.parent / "results" / "rq3_agnostic"

PARQUET_FILES = [
    "rq3_random20.parquet", "rq3_random20_sift.parquet", "rq3_km20.parquet",
    "rq3_minibatch.parquet", "rq3_minibatch_partial.parquet",
    "rq3_random_proj.parquet", "rq3_pca1d.parquet",
    "rq3_hilbert.parquet", "rq3_zorder.parquet", "rq3_hybrid.parquet",
    "rq3_kdtree.parquet", "rq3_pq.parquet",
    "rq3_lsh.parquet", "rq3_kde_pilot.parquet", "rq3_distance_shell.parquet",
    "rq3_importance_sampling.parquet",
    # 5/7 새벽 final_chain + phase2 추가 method
    "rq3_spectral.parquet", "rq3_birch.parquet",
    "rq3_gmm.parquet", "rq3_hdbscan.parquet",
    "rq3_sobol.parquet", "rq3_sparse_rp.parquet",
]


def load_all() -> pd.DataFrame:
    frames = []
    for fname in PARQUET_FILES:
        path = RESULTS / fname
        if path.exists():
            df = pd.read_parquet(path)
            df["source"] = fname.replace(".parquet", "")
            frames.append(df)
    return pd.concat(frames, ignore_index=True)


def main():
    print("=" * 70)
    print("RQ3 Per-Query Method Ranking")
    print("=" * 70)

    df = load_all().dropna(subset=["q_error"])
    print(f"[load] {len(df):,} rows")

    # bernoulli 만 남기고 dedup
    df_bern = df[df["mode"] == "bernoulli"]
    df_methods = df[~df["mode"].isin(["bernoulli"])]

    # 5 seed 평균: query 별 method 의 q_error
    pivot_q = df_methods.groupby(["dataset", "selectivity", "query_id", "mode"])["q_error"].mean().reset_index()
    bern_q = df_bern.groupby(["dataset", "selectivity", "query_id"])["q_error"].mean().reset_index()
    bern_q.rename(columns={"q_error": "bern_q"}, inplace=True)

    # join
    merged = pivot_q.merge(bern_q, on=["dataset", "selectivity", "query_id"], how="left")
    merged["method_minus_bern"] = merged["q_error"] - merged["bern_q"]

    # method 의 query 별 ranking (q_error 작을수록 좋음)
    merged["rank"] = merged.groupby(["dataset", "selectivity", "query_id"])["q_error"].rank(method="min")
    merged.to_csv(RESULTS / "rq3_per_query_ranking.csv", index=False)
    print(f"[saved] {RESULTS / 'rq3_per_query_ranking.csv'}")

    # === 1. method 가 best (rank=1) 빈도 ===
    print("\n=== Method 가 best (rank=1) 빈도 ===")
    best_freq = merged[merged["rank"] == 1].groupby(["dataset", "mode"]).size().unstack(fill_value=0)
    best_total = best_freq.sum(axis=0)
    best_freq.loc["TOTAL"] = best_total
    print(best_freq.to_string())

    # === 2. query 난이도 (BERN q_error) 별 best method ===
    print("\n=== Query 난이도 별 best method 분포 ===")
    # query 별 BERN q_error 4 quantile bin
    merged_bern = merged.dropna(subset=["bern_q"]).copy()
    merged_bern["difficulty_quartile"] = merged_bern.groupby(["dataset", "selectivity"])["bern_q"].transform(
        lambda x: pd.qcut(x, q=4, labels=["Q1_easy", "Q2", "Q3", "Q4_hard"], duplicates="drop")
    )
    diff_best = merged_bern[merged_bern["rank"] == 1].groupby(["dataset", "difficulty_quartile", "mode"]).size().reset_index(name="count")
    diff_pivot = diff_best.pivot_table(
        index=["dataset", "difficulty_quartile"], columns="mode", values="count", fill_value=0,
    )
    print(diff_pivot.head(20).to_string())
    diff_pivot.to_csv(RESULTS / "rq3_query_difficulty_method.csv")
    print(f"\n[saved] {RESULTS / 'rq3_query_difficulty_method.csv'}")

    # === 3. method-disagreement queries (best vs worst 차이 큰 query) ===
    print("\n=== Method disagreement (best vs worst q_error 차이) ===")
    spread = merged.groupby(["dataset", "selectivity", "query_id"])["q_error"].agg(["min", "max", "mean", "std"])
    spread["spread"] = spread["max"] - spread["min"]
    spread["spread_pct"] = spread["spread"] / spread["mean"] * 100
    print(spread.groupby("dataset")["spread_pct"].describe().round(2).to_string())

    # disagreement query 의 BERN q_error 과의 상관
    spread_with_bern = spread.reset_index().merge(bern_q, on=["dataset", "selectivity", "query_id"])
    corr = spread_with_bern.groupby("dataset").apply(
        lambda g: pd.Series({
            "spread_vs_difficulty_corr": g["spread_pct"].corr(g["bern_q"], method="spearman"),
            "n_queries": len(g),
        }), include_groups=False,
    ).round(3)
    print("\n=== spread_pct vs BERN q_error (난이도) correlation ===")
    print(corr.to_string())

    # === 4. method 별 query 평균 rank ===
    print("\n=== Method 별 평균 rank (낮을수록 better) ===")
    avg_rank = merged.groupby(["dataset", "mode"])["rank"].mean().unstack().round(2)
    print(avg_rank.to_string())

    # === narrative ===
    md = [
        "# RQ3 Per-Query Method Ranking",
        "",
        "각 query 마다 method 들을 q_error 로 ranking → 어떤 query 에서 어느 method 가",
        "이기는지 분석. 박세은 5/5 의문 \"DEEP system 절대값 큼\" 에 대한 query-level 답변.",
        "",
        "## 1. Method 가 Best (rank=1) 빈도",
        "",
        "각 (dataset, sel, query) 조합에서 가장 작은 q_error 를 보인 method 의 빈도.",
        "",
        "```",
        best_freq.to_string(),
        "```",
        "",
        "## 2. Method 별 평균 Rank",
        "",
        "1=항상 best, 7+=항상 worst. query × sel 평균.",
        "",
        "```",
        avg_rank.to_string(),
        "```",
        "",
        "## 3. Method Disagreement vs Query 난이도",
        "",
        "query 별 method 간 q_error 분산 (best vs worst 차이) 의 BERN 난이도 (q_error) 와의",
        "상관. 양수 → 어려운 query 에서 method 차이 큼.",
        "",
        "```",
        corr.to_string(),
        "```",
        "",
        "## 4. RQ3 narrative 결론",
        "",
        "- **Best method 가 dataset/sel 별로 다름** → 본 연구의 7-way contribution 정당화.",
        "- **Hilbert 가 best 비율 + Hilbert 의 평균 rank** 조합으로 \"전반적 우위\" 정량.",
        "- **disagreement 가 BERN difficulty 와 양상관** 이면 \"어려운 query 에서 method",
        "  selection 의 가치 큼\" → production 의 method routing 가능성.",
        "",
    ]
    with open(RESULTS / "rq3_per_query_ranking.md", "w") as f:
        f.write("\n".join(md))
    print(f"\n[saved] {RESULTS / 'rq3_per_query_ranking.md'}")


if __name__ == "__main__":
    main()
