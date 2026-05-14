#!/usr/bin/env python3
"""
RQ2 8M 5 sel × 5 mode × cross-scale 종합 — DEEP 1M ↔ DEEP 8M.

5 mode = bernoulli / equal / proportional / neyman / anti_neyman (KM20-aware allocation)
5 sel = 0.01 / 0.05 / 0.10 / 0.30 / 0.50

산출:
   experiments/results/rq2_aware/2026_05_07_8m_alloc/rq2_8m_5sel_5mode_cross_scale.csv
   experiments/results/rq2_aware/2026_05_07_8m_alloc/rq2_8m_5sel_5mode_cross_scale.md
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results" / "rq2_aware"
OUT = RES / "2026_05_07_8m_alloc"

MODES = ["bernoulli", "equal", "proportional", "neyman", "anti_neyman"]
SELS = [0.01, 0.05, 0.10, 0.30, 0.50]


def load(path: Path, ds_filter: str = None) -> pd.DataFrame:
    df = pd.read_parquet(path)
    if ds_filter and "dataset" in df:
        df = df[df["dataset"] == ds_filter]
    return df


def main():
    df1m = load(RES / "2026_05_06_alloc/rq2_alloc.parquet", ds_filter="DEEP")
    df1m["scale"] = "1M"
    df8m = load(OUT / "rq2_alloc_DEEP_8M_5mode.parquet", ds_filter="DEEP_8M")
    df8m["scale"] = "8M"

    rows = []
    for scale, df in [("1M", df1m), ("8M", df8m)]:
        for sel in SELS:
            for mode in MODES:
                m = df[(np.isclose(df.selectivity, sel)) & (df["mode"] == mode)]
                if m.empty:
                    continue
                rows.append({
                    "scale": scale, "sel": sel, "mode": mode,
                    "n_cells": len(m),
                    "mean_q_error": round(m["q_error"].mean(), 4),
                    "median_q_error": round(m["q_error"].median(), 4),
                    "std_q_error": round(m["q_error"].std(), 4),
                })
    summary = pd.DataFrame(rows)
    out_csv = OUT / "rq2_8m_5sel_5mode_cross_scale.csv"
    summary.to_csv(out_csv, index=False)
    print(f"[saved] {out_csv}")

    # === Δ% vs Bernoulli baseline (KM20 effect) ===
    delta_rows = []
    for scale in ["1M", "8M"]:
        for sel in SELS:
            base = summary[(summary.scale == scale) & (summary.sel == sel) & (summary["mode"] == "bernoulli")]
            if base.empty:
                continue
            b_mean = base["mean_q_error"].iloc[0]
            for mode in MODES:
                if mode == "bernoulli":
                    continue
                m = summary[(summary.scale == scale) & (summary.sel == sel) & (summary["mode"] == mode)]
                if m.empty:
                    continue
                delta_pct = (m["mean_q_error"].iloc[0] - b_mean) / b_mean * 100
                delta_rows.append({
                    "scale": scale, "sel": sel, "mode": mode,
                    "bern_mean": round(b_mean, 4),
                    "mode_mean": round(m["mean_q_error"].iloc[0], 4),
                    "delta_pct_vs_bern": round(delta_pct, 2),
                })
    delta = pd.DataFrame(delta_rows)
    print("\n=== Δ% vs Bernoulli (음수 = 개선) ===")
    pivot = delta.pivot_table(index=["sel", "mode"], columns="scale", values="delta_pct_vs_bern")
    print(pivot.round(2).to_string())

    # === narrative ===
    md = []
    md.append("# RQ2 5 mode × 5 sel × Cross-Scale 종합 — DEEP 1M ↔ 8M\n")
    md.append("> **W2 sprint 2026-05-07 산출** — 5 sel × 5 mode allocation × cross-scale\n\n")
    md.append("## 1. 5 mode × 5 sel mean q_error (DEEP)\n\n")
    md.append("```\n")
    md.append(summary.pivot_table(index=["mode", "sel"], columns="scale", values="mean_q_error").round(4).to_string())
    md.append("\n```\n\n")
    md.append("## 2. Δ% vs Bernoulli (BERN baseline, 음수 = 개선)\n\n")
    md.append("| sel | mode | 1M Δ% | 8M Δ% | cross-scale 보존 |\n|---|---|---|---|---|\n")
    for sel in SELS:
        for mode in ["equal", "proportional", "neyman", "anti_neyman"]:
            r1 = delta[(delta.scale == "1M") & (delta.sel == sel) & (delta["mode"] == mode)]
            r8 = delta[(delta.scale == "8M") & (delta.sel == sel) & (delta["mode"] == mode)]
            if r1.empty or r8.empty:
                continue
            d1 = r1["delta_pct_vs_bern"].iloc[0]
            d8 = r8["delta_pct_vs_bern"].iloc[0]
            same_sign = "✓" if (d1 < 0 and d8 < 0) or (d1 > 0 and d8 > 0) else "✗"
            md.append(f"| {sel:.2f} | {mode} | {d1:+.2f}% | {d8:+.2f}% | {same_sign} |\n")

    md.append("\n## 3. 핵심 발견\n\n")
    md.append("- **KM20-Proportional / KM20-Neyman**: 1M에서 BERN 대비 음수 Δ% (개선) → 8M에서도 동일 방향 보존 시 cross-scale 외적 타당성 입증\n")
    md.append("- **Anti-Neyman**: 1M에서 양수 Δ% (악화) → ablation으로 Neyman의 유의미성 확인. 8M에서도 같은 패턴이면 robustness\n\n")
    out_md = OUT / "rq2_8m_5sel_5mode_cross_scale.md"
    out_md.write_text("".join(md))
    print(f"[saved] {out_md}")


if __name__ == "__main__":
    main()
