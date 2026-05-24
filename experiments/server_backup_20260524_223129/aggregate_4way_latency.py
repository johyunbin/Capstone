#!/usr/bin/env python3
"""phase2 4-way latency 측정 결과 aggregate — 5/24 Phase 4 분석.

phase2_4way_*/*.json (12 cell × 18 variant) 을 long-form parquet 으로 합치고,
요약 md 를 생성한다.

핵심 지표:
  · variant 별 trimmed/median latency (cell-level)
  · variant pair paired Δ% (baseline 제외, B1 기준)
  · CaseC 결과: B1↔CaseC paired Δ% — 가설 ≈ 0 (engine 무개선) vs 의미 있게 ≠ 0 (개선·악화)

산출:
  · long.parquet — 1 row = (cell, variant, exec_ms_sample_idx, exec_ms)
  · cell_summary.parquet — 1 row = (cell, variant, trim, median, IQR, n_to)
  · paired_summary.md — variant pair Δ% (paired matched cell)

사용:
    python3 aggregate_4way_latency.py \\
        --input-dir /mnt/hdd0/home/capstone2026/cache/rq3/latency/phase2_4way_<TS> \\
        --output-dir /mnt/hdd0/home/capstone2026/cache/rq3/latency/phase2_4way_summary
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import numpy as np
import pandas as pd


def load_cell(jp: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """1 cell json → (long_df, summary_df)."""
    d = json.loads(jp.read_text())
    cell_key = f"{d['query']}_{d['dataset']}_sf{d['sf']}_sel{d['sel']}_qid{d['query_id']}"
    long_rows, summary_rows = [], []
    for v in d["variants"]:
        c, m = v["condition"], v["method"]
        label = f"{c}/{m or '-'}"
        for idx, ms in enumerate(v["exec_ms"]):
            long_rows.append({
                "cell": cell_key, "query": d["query"], "dataset": d["dataset"],
                "sf": d["sf"], "sel": d["sel"], "qid": d["query_id"],
                "condition": c, "method": m, "variant": label,
                "rep_idx": idx, "exec_ms": ms,
                "injected_card": v["injected_card"], "true_card": d["true_card"],
            })
        summary_rows.append({
            "cell": cell_key, "query": d["query"], "dataset": d["dataset"],
            "sf": d["sf"], "sel": d["sel"], "qid": d["query_id"],
            "condition": c, "method": m, "variant": label,
            "exec_ms_trim": v["exec_ms_trimmed"],
            "exec_ms_median": v["exec_ms_median"],
            "exec_ms_iqr_lo": v["exec_ms_iqr"][0] if v["exec_ms_iqr"] else None,
            "exec_ms_iqr_hi": v["exec_ms_iqr"][1] if v["exec_ms_iqr"] else None,
            "n_timeout": v["n_timeout"],
            "n_samples": len(v["exec_ms"]),
            "injected_card": v["injected_card"], "true_card": d["true_card"],
            "q_error": v["q_error"],
            "injection_fired": v["injection_fired"],
            "injected_card_seen": v["injected_card_seen"],
        })
    return pd.DataFrame(long_rows), pd.DataFrame(summary_rows)


def paired_delta(summary: pd.DataFrame, ref_variant: str = "B1/-") -> pd.DataFrame:
    """variant 별 cell-level paired Δ% vs ref_variant.

    같은 cell 에서 (variant_exec - ref_exec) / ref_exec × 100.
    cell-level matched — variant 종류만큼 row.
    """
    ref = summary[summary.variant == ref_variant].set_index("cell")["exec_ms_trim"]
    rows = []
    for variant, g in summary.groupby("variant"):
        if variant == ref_variant:
            continue
        gi = g.set_index("cell")
        common = ref.index.intersection(gi.index)
        if len(common) == 0:
            continue
        deltas = (gi.loc[common, "exec_ms_trim"] - ref.loc[common]) / ref.loc[common] * 100
        deltas = deltas.dropna()
        if len(deltas) == 0:
            continue
        rows.append({
            "variant": variant,
            "n_cells": len(deltas),
            "delta_pct_mean": float(deltas.mean()),
            "delta_pct_median": float(deltas.median()),
            "delta_pct_std": float(deltas.std()),
            "delta_pct_min": float(deltas.min()),
            "delta_pct_max": float(deltas.max()),
            "n_faster": int((deltas < 0).sum()),
            "n_slower": int((deltas > 0).sum()),
        })
    return pd.DataFrame(rows).sort_values("delta_pct_mean")


def write_summary_md(summary: pd.DataFrame, paired: pd.DataFrame,
                     n_cells: int, out: Path) -> None:
    from datetime import datetime, timezone, timedelta
    kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")
    lines = []
    lines.append(f"# phase2 4-way latency 측정 — aggregate summary ({kst})\n")
    lines.append(f"- cells: **{n_cells}** (paired matched)\n")
    lines.append(f"- variants: {sorted(summary.variant.unique().tolist())}\n")
    lines.append(f"- 출처: phase2 4-way launch 5/24\n")

    # variant 별 cell-level trim mean
    lines.append("\n## 1. variant 별 cell-level trim latency 평균\n")
    by_var = (summary.groupby("variant")["exec_ms_trim"]
              .agg(["mean", "median", "std", "min", "max", "count"])
              .round(2))
    by_var = by_var.sort_values("mean")
    lines.append(by_var.to_markdown())

    lines.append("\n## 2. paired Δ% vs B1 (대조군)\n")
    lines.append("> Δ% = (variant_exec − B1_exec) / B1_exec × 100. 음수 = variant 더 빠름.\n")
    lines.append("> cell-level matched (같은 cell 안 paired).\n\n")
    if len(paired):
        lines.append(paired.round(3).to_markdown(index=False))
    else:
        lines.append("(paired 비교 데이터 없음)\n")

    # CaseC 가설 검증 — paired Δ% 가 0 인지
    lines.append("\n## 3. ★ CaseC 가설 검증\n")
    casec = paired[paired.variant == "CaseC/-"]
    if len(casec):
        r = casec.iloc[0]
        lines.append(f"- CaseC vs B1 paired Δ% mean = {r['delta_pct_mean']:.2f}% "
                     f"(median {r['delta_pct_median']:.2f}%, std {r['delta_pct_std']:.2f})\n")
        lines.append(f"- 빠른 cells: {r['n_faster']}/{r['n_cells']}, "
                     f"느린 cells: {r['n_slower']}/{r['n_cells']}\n")
        if abs(r['delta_pct_mean']) < 2.0:
            lines.append("- 해석: |Δ%| < 2% → ★ CaseC 도 engine 에서 동등 (B1·CaseB·CaseC 모두 ≈ 평균 효과 가설 지지)\n")
        elif r['delta_pct_mean'] < -2.0:
            lines.append("- 해석: Δ% < -2% → ★ CaseC engine 우위 (engine 영향 새 발견)\n")
        else:
            lines.append("- 해석: Δ% > 2% → CaseC engine 악화 (이상)\n")

    # injection sanity
    lines.append("\n## 4. injection sanity\n")
    inj = (summary[summary.condition.isin(["B1", "CaseA", "CaseB", "CaseC", "oracle"])]
           .groupby("variant")["injection_fired"].agg(["sum", "count"]))
    inj["fired_rate"] = inj["sum"] / inj["count"]
    lines.append(inj.round(3).to_markdown())

    out.write_text("\n".join(lines))
    print(f"saved {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", type=Path, required=True,
                    help="phase2_4way_<TS>/ 디렉토리 (*.json)")
    ap.add_argument("--output-dir", type=Path, required=True,
                    help="aggregate 결과 디렉토리")
    args = ap.parse_args()

    jsons = sorted(args.input_dir.glob("latency_*.json"))
    if not jsons:
        raise SystemExit(f"no JSON in {args.input_dir}")
    print(f"loading {len(jsons)} cells…")

    longs, summs = [], []
    for jp in jsons:
        l, s = load_cell(jp)
        longs.append(l)
        summs.append(s)
    long_df = pd.concat(longs, ignore_index=True)
    summary_df = pd.concat(summs, ignore_index=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    long_df.to_parquet(args.output_dir / "long.parquet", index=False)
    summary_df.to_parquet(args.output_dir / "cell_summary.parquet", index=False)
    print(f"saved long.parquet ({len(long_df)} rows) + cell_summary.parquet "
          f"({len(summary_df)} rows)")

    paired = paired_delta(summary_df, ref_variant="B1/-")
    paired.to_parquet(args.output_dir / "paired_summary.parquet", index=False)
    print(f"saved paired_summary.parquet ({len(paired)} rows)")

    write_summary_md(summary_df, paired, n_cells=len(jsons),
                     out=args.output_dir / "phase2_4way_summary.md")


if __name__ == "__main__":
    main()
