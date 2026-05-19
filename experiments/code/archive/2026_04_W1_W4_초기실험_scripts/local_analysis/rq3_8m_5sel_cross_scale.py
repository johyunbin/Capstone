#!/usr/bin/env python3
"""
RQ3 cross-scale 5 selectivity × 19 method 종합 — 1M vs 8M 외적 타당성.

W2 sprint 2026-05-07 — Worker G 측정 산출.

기존 sel 0.10/0.30 (rq3_8m_*.parquet) + 새 sel 0.01/0.05/0.50 (rq3_8m_*_sel_expand.parquet)
를 통합하여 5 selectivity 전 영역에서 19 method 의 1M↔8M 일관성 검증.

산출:
  experiments/results/rq3_agnostic/rq3_8m_5sel_cross_scale.csv  (전체 cell-level)
  experiments/results/rq3_agnostic/rq3_8m_5sel_cross_scale.md   (narrative + 표)
"""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "rq3_agnostic"

METHODS_19 = [
    "birch", "distance_shell", "gmm", "hdbscan", "hilbert", "hybrid",
    "importance_sampling", "kde_pilot", "kdtree", "lsh",
    "minibatch", "minibatch_partial", "pca1d", "pq", "random_proj",
    "sobol", "sparse_rp", "spectral", "zorder",
]
SELS_5 = [0.01, 0.05, 0.10, 0.30, 0.50]


def load_8m_combined(method: str) -> pd.DataFrame:
    """기존 sel 0.10/0.30 + sel_expand 0.01/0.05/0.50 통합."""
    parts = []
    base = RESULTS / f"rq3_8m_{method}.parquet"
    expand = RESULTS / f"rq3_8m_{method}_sel_expand.parquet"
    if base.exists():
        df = pd.read_parquet(base)
        df["source"] = "base"
        parts.append(df)
    if expand.exists():
        df = pd.read_parquet(expand)
        df["source"] = "expand"
        parts.append(df)
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts, ignore_index=True)
    out["scale"] = "8M"
    return out


def load_1m(method: str) -> pd.DataFrame:
    path = RESULTS / f"rq3_{method}.parquet"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    df["scale"] = "1M"
    return df


def _method_mode_filter(method: str, mode_col: pd.Series) -> pd.Series:
    """method 별 표준 mode 매칭 (importance_sampling 은 is_p200_clip 사용)."""
    if method == "importance_sampling":
        return mode_col == "is_p200_clip"
    return mode_col == method


def summarize(df: pd.DataFrame, method: str) -> list[dict]:
    """(scale, sel, method) 별 q_error mean/std/count + bernoulli baseline."""
    rows = []
    for scale in ["1M", "8M"]:
        sub = df[df["scale"] == scale]
        if sub.empty:
            continue
        # DEEP 만 (1M 은 SIFT 도 포함, 8M 은 DEEP 만)
        sub = sub[sub["dataset"].isin(["DEEP", "DEEP_8M"])]
        for sel in SELS_5:
            for mode_kind in ["method", "bernoulli"]:
                if mode_kind == "method":
                    mode_filter = _method_mode_filter(method, sub["mode"])
                else:
                    mode_filter = sub["mode"] == "bernoulli"
                m = sub[(np.isclose(sub["selectivity"], sel)) & mode_filter]
                if m.empty:
                    continue
                rows.append({
                    "method": method,
                    "scale": scale,
                    "sel": sel,
                    "mode_kind": mode_kind,
                    "n_cells": len(m),
                    "mean_q_error": round(m["q_error"].mean(), 4),
                    "std_q_error": round(m["q_error"].std(), 4),
                    "median_q_error": round(m["q_error"].median(), 4),
                })
    return rows


def main() -> None:
    print("[load] 19 method × {1M, 8M} parquets")
    all_rows = []
    for method in METHODS_19:
        df1 = load_1m(method)
        df8 = load_8m_combined(method)
        if df1.empty:
            print(f"  [warn] {method}: 1M parquet 없음 — skip")
            continue
        if df8.empty:
            print(f"  [warn] {method}: 8M parquet 없음 — skip")
            continue
        combined = pd.concat([df1, df8], ignore_index=True)
        rows = summarize(combined, method)
        all_rows.extend(rows)
        sels_8m = sorted(df8["selectivity"].unique())
        print(f"  [ok] {method:20s} 1M: sel {sorted(df1['selectivity'].unique())} | "
              f"8M: sel {sels_8m} ({len(df8)} rows)")

    df = pd.DataFrame(all_rows)
    out_csv = RESULTS / "rq3_8m_5sel_cross_scale.csv"
    df.to_csv(out_csv, index=False)
    print(f"\n[saved] {out_csv} ({len(df)} rows)")

    # === ranking stability + Spearman ===
    method_means = df[df["mode_kind"] == "method"].pivot_table(
        index="method", columns=["scale", "sel"], values="mean_q_error",
    )
    print("\n=== 19 method × 5 sel mean q_error ===")
    print(method_means.round(4).to_string())

    # Per-sel Spearman 1M ↔ 8M
    print("\n=== Spearman ranking 1M ↔ 8M (per sel, 19 method ranking) ===")
    spearman_rows = []
    for sel in SELS_5:
        try:
            col_1m = method_means[("1M", sel)].dropna()
            col_8m = method_means[("8M", sel)].dropna()
            common = col_1m.index.intersection(col_8m.index)
            if len(common) >= 4:
                rho, p = spearmanr(col_1m.loc[common], col_8m.loc[common])
                spearman_rows.append({
                    "sel": sel, "n_methods": len(common),
                    "spearman_rho": round(rho, 4), "p_value": round(p, 4),
                })
                print(f"  sel={sel:.2f}: ρ={rho:+.4f} (p={p:.4f}, n={len(common)})")
        except KeyError:
            print(f"  sel={sel:.2f}: 데이터 부족")

    sp_df = pd.DataFrame(spearman_rows)

    # === narrative md ===
    md = []
    md.append("# RQ3 Cross-Scale 5 Selectivity 종합 — DEEP 1M ↔ 8M\n")
    md.append("> **W2 sprint 2026-05-07 산출** — 19 method × 5 selectivity × DEEP 1M↔8M 외적 타당성 매듭\n")
    md.append("## 1. 측정 커버리지\n")
    md.append("| Scale | Methods | Selectivities | Source |\n|---|---|---|---|\n")
    md.append(f"| 1M | 19 | {SELS_5} | 기존 측정 (rq3_*.parquet) |\n")
    md.append(f"| 8M | 19 | {SELS_5} | base ({{0.10, 0.30}}) + sel_expand ({{0.01, 0.05, 0.50}}) |\n\n")

    md.append("## 2. 19 method × 5 sel × 2 scale mean q_error\n\n")
    md.append("```\n")
    md.append(method_means.round(4).to_string())
    md.append("\n```\n\n")

    md.append("## 3. Spearman ranking 일관성 (1M vs 8M, sel 별)\n\n")
    md.append("| Selectivity | n_methods | Spearman ρ | p-value | 해석 |\n|---|---|---|---|---|\n")
    for _, r in sp_df.iterrows():
        if r["spearman_rho"] >= 0.7:
            interp = "**강함** — 1M ranking이 8M에서 잘 보존됨"
        elif r["spearman_rho"] >= 0.4:
            interp = "중간 — 부분 보존"
        else:
            interp = "약함 — scale-dependent ranking 변동"
        md.append(f"| {r['sel']:.2f} | {int(r['n_methods'])} | {r['spearman_rho']:+.4f} | {r['p_value']:.4f} | {interp} |\n")

    # Per-sel top-5 method
    md.append("\n## 4. Selectivity 별 1M vs 8M Top-5 method\n\n")
    for sel in SELS_5:
        try:
            col_1m = method_means[("1M", sel)].dropna().sort_values()
            col_8m = method_means[("8M", sel)].dropna().sort_values()
            md.append(f"### sel = {sel:.2f}\n\n")
            md.append("| Rank | 1M method | 1M q_error | 8M method | 8M q_error |\n|---|---|---|---|---|\n")
            for i in range(min(5, len(col_1m), len(col_8m))):
                m1, q1 = col_1m.index[i], col_1m.iloc[i]
                m8, q8 = col_8m.index[i], col_8m.iloc[i]
                md.append(f"| {i+1} | {m1} | {q1:.4f} | {m8} | {q8:.4f} |\n")
            md.append("\n")
        except KeyError:
            continue

    out_md = RESULTS / "rq3_8m_5sel_cross_scale.md"
    out_md.write_text("".join(md))
    print(f"[saved] {out_md}")


if __name__ == "__main__":
    main()
