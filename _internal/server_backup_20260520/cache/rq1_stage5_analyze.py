"""
RQ1 Stage 5 — 분석: Skew 그룹 × Q-error 연관 + RQ1 판단 기준 검증

입력:
  - cache/rq1/adaptive_runs.parquet   (60 run × 100 q_errors)
  - cache/rq1/query_skew.parquet      (100 query × 4 skew 지표)

출력:
  - cache/rq1/stage5_analysis.parquet — query_id × skew × selectivity × mode × seed → q_error
  - cache/rq1/stage5_summary.json     — 그룹별 집계 + 통계 검정
  - stdout: 인간 가독형 요약 테이블

핵심 검증:
  1. v3 절대 기준 Fisher γ 그룹별 median Q-error 비교
  2. "|γ|>1 그룹의 med_qe ≥ 2x |γ|<0.5 그룹" 판정
  3. 4개 skew 지표 × Q-error Spearman 상관
  4. Mann-Whitney U test (양측, α=0.05)
  5. Block vs Bernoulli paired 비교

파이프라인 문서: experiments/plans/RQ1_motivation_pipeline_20260414_162857.md §V
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import scipy.stats as st


def kst_now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now_iso()}] {msg}", flush=True)


def fmt(x: float, d: int = 3) -> str:
    if x is None or np.isnan(x):
        return "    -"
    return f"{x:>{d+5}.{d}f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    args = parser.parse_args()

    runs_path = os.path.join(args.in_dir, "adaptive_runs.parquet")
    skew_path = os.path.join(args.in_dir, "query_skew.parquet")
    out_path = os.path.join(args.in_dir, "stage5_analysis.parquet")
    summary_path = os.path.join(args.in_dir, "stage5_summary.json")

    log(f"시작 — in={args.in_dir}")
    log("Stage 5.1 — parquet 로드")
    runs = pq.read_table(runs_path).to_pandas()
    skew = pq.read_table(skew_path).to_pandas()
    log(f"  runs: {len(runs)}, skew: {len(skew)}")

    # Explode run's q_errors[100] → query_id axis
    log("Stage 5.2 — q_errors 언롤 (run × query_id)")
    rows = []
    for _, r in runs.iterrows():
        qe = np.asarray(r["q_errors"])
        ss = np.asarray(r["sample_size_trajectory"])
        for q in range(len(qe)):
            rows.append(
                {
                    "query_id": int(q),
                    "selectivity": float(r["selectivity"]),
                    "mode": r["mode"],
                    "seed": int(r["seed"]),
                    "q_error": float(qe[q]),
                    "sample_size_at": float(ss[q]),
                }
            )
    import pandas as pd

    long = pd.DataFrame(rows)
    log(f"  long: {len(long)} rows")

    # Join with skew
    long = long.merge(skew, on="query_id", how="left")
    log(f"  joined: {len(long)} rows, cols: {list(long.columns)[:10]} ...")

    # ------- 분석 A: v3 절대 기준 Fisher γ 그룹 -------
    log("===== 분석 A: v3 절대 기준 Fisher γ 그룹 =====")
    log("Fisher γ 기준 — Stage 2 결과가 100 query 전부 음수 (left-skewed)")
    log("절대값 |γ| 기준 그룹 분류 사용")

    abs_fg = long["fisher_gamma"].abs()
    bins = [0, 0.5, 1.0, 2.0, np.inf]
    labels = ["symmetric", "moderate", "skewed", "extreme"]
    long["skew_group"] = pd.cut(abs_fg, bins=bins, labels=labels, right=False)
    # group size check
    query_groups = long.groupby("query_id")["skew_group"].first()
    log(f"  그룹 사이즈 (query 단위): {query_groups.value_counts().to_dict()}")

    # 그룹별 med Q-error (selectivity × mode 축)
    log("Stage 5.3 — 그룹 × selectivity × mode → median Q-error")
    grouped = (
        long.groupby(["skew_group", "selectivity", "mode"], observed=True)["q_error"]
        .agg(["median", "mean", "count"])
        .reset_index()
    )

    # 요약 테이블
    log("===== Skew 그룹 × selectivity × mode → median Q-error =====")
    log(f"{'selectivity':>12} | {'mode':>13} | {'symmetric':>10} {'moderate':>10} {'skewed':>10} {'extreme':>10}")
    for s in sorted(long["selectivity"].unique()):
        for mode in sorted(long["mode"].unique()):
            row = [f"{s:>12.3f}", f"{mode:>13}"]
            for g in labels:
                sub = grouped[
                    (grouped["skew_group"] == g)
                    & (grouped["selectivity"] == s)
                    & (grouped["mode"] == mode)
                ]
                if len(sub) > 0:
                    row.append(fmt(sub["median"].iloc[0], 2))
                else:
                    row.append("    -")
            log(" | ".join(row))

    # ------- 분석 B: RQ1 판단 기준 -------
    log("===== 분석 B: RQ1 판단 기준 ( |γ|>1 median Q-error >= 2x |γ|<0.5 ) =====")
    rq1_results = {}
    for mode in sorted(long["mode"].unique()):
        for s in sorted(long["selectivity"].unique()):
            sub = long[(long["mode"] == mode) & (long["selectivity"] == s)]
            low_grp = sub[sub["fisher_gamma"].abs() < 0.5]["q_error"]
            high_grp = sub[sub["fisher_gamma"].abs() >= 1.0]["q_error"]
            if len(low_grp) < 5 or len(high_grp) < 5:
                continue
            med_low = float(np.median(low_grp))
            med_high = float(np.median(high_grp))
            ratio = med_high / med_low if med_low > 0 else float("inf")
            # Mann-Whitney U
            u, p = st.mannwhitneyu(low_grp, high_grp, alternative="two-sided")
            rq1_results[(mode, s)] = {
                "med_low": med_low,
                "med_high": med_high,
                "ratio": ratio,
                "u": float(u),
                "p": float(p),
                "n_low": int(len(low_grp)),
                "n_high": int(len(high_grp)),
                "pass_2x": bool(ratio >= 2.0),
                "pass_p05": bool(p < 0.05),
            }

    log(f"{'mode':>13} | {'s':>6} | {'med(|γ|<.5)':>13} {'med(|γ|≥1)':>13} {'ratio':>8} {'p':>10} | {'pass':>8}")
    for (mode, s), v in sorted(rq1_results.items()):
        passed = "✓" if (v["pass_2x"] and v["pass_p05"]) else ("~" if v["pass_p05"] else "✗")
        log(
            f"{mode:>13} | {s:>6.3f} | "
            f"{fmt(v['med_low'], 3)} {fmt(v['med_high'], 3)} "
            f"{fmt(v['ratio'], 2)} {fmt(v['p'], 4)} | {passed:>8}"
        )

    # ------- 분석 C: 4 skew 지표 × Q-error Spearman -------
    log("===== 분석 C: Spearman 상관 (skew 지표 × q_error, selectivity별) =====")
    corr_results = {}
    for s in sorted(long["selectivity"].unique()):
        sub = long[(long["selectivity"] == s) & (long["mode"] == "bernoulli")]
        # 각 query의 평균 q_error (seed 평균)
        agg = (
            sub.groupby("query_id")
            .agg(
                q_error_med=("q_error", "median"),
                fisher_gamma=("fisher_gamma", "first"),
                log_gamma=("log_gamma", "first"),
                tail_ratio=("tail_ratio_p99_p50", "first"),
                bowley=("bowley", "first"),
            )
            .reset_index()
        )
        for metric in ["fisher_gamma", "log_gamma", "tail_ratio", "bowley"]:
            rho, p = st.spearmanr(agg[metric], agg["q_error_med"])
            # 절대값 기준도 함께
            rho_abs, p_abs = st.spearmanr(agg[metric].abs(), agg["q_error_med"])
            corr_results[(s, metric)] = {
                "rho": float(rho),
                "p": float(p),
                "rho_abs": float(rho_abs),
                "p_abs": float(p_abs),
            }

    log(
        f"{'s':>7} | {'fisher':>15} {'log':>15} {'tail_ratio':>15} {'bowley':>15}"
    )
    for s in sorted(long["selectivity"].unique()):
        row = [f"{s:>7.3f}"]
        for metric in ["fisher_gamma", "log_gamma", "tail_ratio", "bowley"]:
            c = corr_results[(s, metric)]
            row.append(f"{c['rho']:+.3f}(p={c['p']:.3f})")
        log("  " + " | ".join(row))

    log("  (|.| 절대값 기준 Spearman:)")
    for s in sorted(long["selectivity"].unique()):
        row = [f"{s:>7.3f}"]
        for metric in ["fisher_gamma", "log_gamma", "tail_ratio", "bowley"]:
            c = corr_results[(s, metric)]
            row.append(f"{c['rho_abs']:+.3f}(p={c['p_abs']:.3f})")
        log("  " + " | ".join(row))

    # ------- 분석 D: Block vs Bernoulli paired 비교 -------
    log("===== 분석 D: Block vs Bernoulli paired 비교 =====")
    paired_results = {}
    for s in sorted(long["selectivity"].unique()):
        # per-query median Q-error, seed 평균
        piv = (
            long[long["selectivity"] == s]
            .groupby(["query_id", "mode"])["q_error"]
            .median()
            .reset_index()
            .pivot(index="query_id", columns="mode", values="q_error")
        )
        if "bernoulli" in piv.columns and "block_system" in piv.columns:
            diff = piv["block_system"] - piv["bernoulli"]
            # Wilcoxon signed-rank
            try:
                w, p = st.wilcoxon(
                    piv["block_system"], piv["bernoulli"], alternative="greater"
                )
                paired_results[s] = {
                    "median_diff": float(diff.median()),
                    "mean_diff": float(diff.mean()),
                    "wilcoxon_W": float(w),
                    "wilcoxon_p": float(p),
                    "n_block_higher": int((diff > 0).sum()),
                    "n_bernoulli_higher": int((diff < 0).sum()),
                    "n_tie": int((diff == 0).sum()),
                }
            except Exception as e:
                log(f"  wilcoxon error at s={s}: {e}")

    log(f"{'s':>7} | {'med_diff':>10} {'mean_diff':>10} {'W':>10} {'p':>10} | {'block>ber':>10} {'ber>block':>10}")
    for s, v in sorted(paired_results.items()):
        log(
            f"{s:>7.3f} | "
            f"{fmt(v['median_diff'], 4)} {fmt(v['mean_diff'], 4)} "
            f"{fmt(v['wilcoxon_W'], 1)} {fmt(v['wilcoxon_p'], 5)} | "
            f"{v['n_block_higher']:>10d} {v['n_bernoulli_higher']:>10d}"
        )

    # 저장
    log("Stage 5.4 — 저장")
    long.to_parquet(out_path, compression="snappy", index=False)
    log(f"  long-form: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB, {len(long)} rows)")

    summary = {
        "timestamp_kst": kst_now_iso(),
        "script": "scripts/rq1_stage5_analyze.py",
        "query_group_sizes": query_groups.value_counts().to_dict(),
        "rq1_judgement_v3": {
            f"{mode}__s={s}": v for (mode, s), v in rq1_results.items()
        },
        "spearman_correlations": {
            f"s={s}__{metric}": v for (s, metric), v in corr_results.items()
        },
        "block_vs_bernoulli_paired": {
            f"s={s}": v for s, v in paired_results.items()
        },
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    log(f"  summary: {summary_path}")
    log("===== Stage 5 완료 =====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
