#!/usr/bin/env python3
"""offline CaseC v15 portfolio aggregate — 5/24 Phase 4 분석.

paper_exact_v15_new9_*/A*_CaseC.json (신규 9 cell) + paper_exact_v14_20260523/A*_CaseC.json
(carry 9 cell, optional) 을 합쳐 v15 portfolio summary 생성.

핵심 지표:
  · cell 별 mean qe_trim
  · v14 carry 9 cell vs v15 신규 9 cell mean qe_trim 비교 (1.3729 vs new)
  · 신규 9 cell 의 cell 별 size_a·size_b 독립성 검증

사용:
    python3 aggregate_offline_casec_v15.py \\
        --v15-dir /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v15_new9_<TS> \\
        --v14-dir /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v14_20260523 \\
        --output-dir /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v15_summary
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import numpy as np
import pandas as pd


def load_casec(jp: Path) -> dict:
    d = json.loads(jp.read_text())
    trials = d["trial_results"]
    sizes_a = [t["final_size_a"] for t in trials]
    sizes_b = [t["final_size_b"] for t in trials]
    avg_qes = [t["avg_q_error_finite"] for t in trials]
    return {
        "cell": d["cell"],
        "dataset": d["dataset"],
        "sf": d["sf"],
        "qe_trim": d["avg_q_error_trimmed"],
        "qe_mean": float(np.mean(avg_qes)),
        "qe_median": float(np.median(avg_qes)),
        "qe_std": float(np.std(avg_qes)),
        "size_a_mean": float(np.mean(sizes_a)),
        "size_a_std": float(np.std(sizes_a)),
        "size_b_mean": float(np.mean(sizes_b)),
        "size_b_std": float(np.std(sizes_b)),
        "n_trial": len(trials),
        "source": jp.parent.name,
    }


def collect(v15_dir: Path, v14_dir: Path | None) -> pd.DataFrame:
    rows = []
    for jp in sorted(v15_dir.glob("*_CaseC.json")):
        r = load_casec(jp)
        r["batch"] = "v15"
        rows.append(r)
    if v14_dir and v14_dir.exists():
        for jp in sorted(v14_dir.glob("*_CaseC.json")):
            r = load_casec(jp)
            r["batch"] = "v14"
            rows.append(r)
    return pd.DataFrame(rows)


def write_md(df: pd.DataFrame, out: Path) -> None:
    from datetime import datetime, timezone, timedelta
    kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")
    lines = []
    lines.append(f"# offline CaseC v15 portfolio — aggregate summary ({kst})\n")
    lines.append(f"- total cells: **{len(df)}** (v15 신규 + v14 carry)\n")
    lines.append(f"- batches: {dict(df.batch.value_counts())}\n")

    lines.append("\n## 1. cell 별 mean qe_trim\n")
    cols = ["batch", "cell", "dataset", "sf", "qe_trim", "qe_mean", "qe_std",
            "size_a_mean", "size_b_mean", "n_trial"]
    lines.append(df[cols].round(4).to_markdown(index=False))

    lines.append("\n## 2. batch 별 mean qe_trim (집계)\n")
    by_batch = df.groupby("batch").agg(
        n=("cell", "size"),
        qe_trim_mean=("qe_trim", "mean"),
        qe_trim_median=("qe_trim", "median"),
        qe_trim_std=("qe_trim", "std"),
        qe_trim_min=("qe_trim", "min"),
        qe_trim_max=("qe_trim", "max"),
    ).round(4)
    lines.append(by_batch.to_markdown())

    lines.append("\n## 3. ★ v15 신규 portfolio mean qe_trim — v14 carry 1.3729 와 비교\n")
    v15 = df[df.batch == "v15"]
    if len(v15):
        v15_mean = v15.qe_trim.mean()
        lines.append(f"- v15 신규 {len(v15)} cell mean qe_trim = **{v15_mean:.4f}**\n")
        lines.append(f"- v14 carry 9 cell mean qe_trim = 1.3729 (carry)\n")
        if df.batch.eq("v14").any():
            v14_mean = df[df.batch == "v14"].qe_trim.mean()
            lines.append(f"- v14 재집계 {df.batch.eq('v14').sum()} cell mean qe_trim = {v14_mean:.4f} (정합 확인)\n")
        lines.append(f"- 종합 {len(df)} cell mean qe_trim = {df.qe_trim.mean():.4f}\n")
        diff = v15_mean - 1.3729
        lines.append(f"\n- Δ vs v14 = {diff:+.4f} "
                     f"({'≈ 동등' if abs(diff) < 0.05 else '주목 차이'})\n")

    lines.append("\n## 4. dual-Bernoulli 독립성 (size_a vs size_b)\n")
    lines.append(df[["cell", "size_a_mean", "size_a_std", "size_b_mean", "size_b_std"]]
                 .round(1).to_markdown(index=False))
    out.write_text("\n".join(lines))
    print(f"saved {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v15-dir", type=Path, required=True)
    ap.add_argument("--v14-dir", type=Path, default=None)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    df = collect(args.v15_dir, args.v14_dir)
    if df.empty:
        raise SystemExit("no CaseC JSON found")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.output_dir / "v15_portfolio.parquet", index=False)
    print(f"saved v15_portfolio.parquet ({len(df)} rows)")
    write_md(df, args.output_dir / "v15_portfolio_summary.md")


if __name__ == "__main__":
    main()
