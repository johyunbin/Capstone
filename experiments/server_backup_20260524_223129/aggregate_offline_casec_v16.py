#!/usr/bin/env python3
"""offline CaseC v16 전수 95 tuple aggregate — 5/24 Phase 6 분석.

paper_exact_v16_full95_<TS>/A*_CaseC_sel*_K*.json (~95 file) 을 모두 scan,
v13 정본 (aggregated_v13_full.parquet, 4,524 row × 25 cell × 3 mode × 3 sel × 3 K
× 16 method) 와 (cell, sel, K) paired matched 분석.

핵심 결과:
  · cell × sel × K 평면 CaseC mean qe_trim 분포 (95 cell)
  · CaseC vs B1 (mode 평균): cell-level better% + median Δ%
  · CaseC vs CaseB (mode 평균): cell-level better% + median Δ%
  · scale·structure dependent 패턴 (sf=1 vs 10 vs 100, sel=0.001 vs 0.01 vs 0.1)

사용:
    python3 aggregate_offline_casec_v16.py \\
        --v16-dir /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v16_full95_<TS> \\
        --v13-parquet /mnt/hdd0/home/capstone2026/cache/rq3/aggregated_v13_full.parquet \\
        --output-dir /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v16_summary_<TS>
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


# v16 file 명: {cell}_CaseC_sel{sel:g}_K{K}.json
V16_PATTERN = re.compile(r"^(?P<cell>.+)_CaseC_sel(?P<sel>[\d.]+)_K(?P<K>\d+)\.json$")


def load_v16_casec(jp: Path) -> dict | None:
    """v16 CaseC JSON 1건 → 집계용 dict. file 명에서 sel·K 추출, dict 의 sel·K 와 일관 검증."""
    m = V16_PATTERN.match(jp.name)
    if not m:
        return None
    file_sel = float(m.group("sel"))
    file_K = int(m.group("K"))
    d = json.loads(jp.read_text())
    # Phase 1 fix 후 dict 에 sel·K 필드. 일관성 검증.
    json_sel = float(d.get("sel", file_sel))
    json_K = int(d.get("K", file_K))
    if abs(json_sel - file_sel) > 1e-9 or json_K != file_K:
        print(f"[WARN] sel/K mismatch in {jp.name}: file=({file_sel}, {file_K}) "
              f"json=({json_sel}, {json_K}) — file 우선")
    trials = d["trial_results"]
    sizes_a = [t["final_size_a"] for t in trials]
    sizes_b = [t["final_size_b"] for t in trials]
    avg_qes = [t["avg_q_error_finite"] for t in trials]
    finite_qes = [v for v in avg_qes if np.isfinite(v)]
    return {
        "cell": d["cell"],
        "dataset": d["dataset"],
        "sf": d["sf"],
        "sel": json_sel,
        "K": json_K,
        "mode": "CaseC_v16",
        "qe_trim": d["avg_q_error_trimmed"],
        "qe_mean": float(np.mean(finite_qes)) if finite_qes else float("nan"),
        "qe_median": float(np.median(finite_qes)) if finite_qes else float("nan"),
        "qe_std": float(np.std(finite_qes)) if finite_qes else float("nan"),
        "size_a_mean": float(np.mean(sizes_a)),
        "size_b_mean": float(np.mean(sizes_b)),
        "n_trial": len(trials),
        "source_file": jp.name,
    }


def collect_v16(v16_dir: Path) -> pd.DataFrame:
    rows = []
    skipped = []
    for jp in sorted(v16_dir.glob("*_CaseC_sel*_K*.json")):
        r = load_v16_casec(jp)
        if r is None:
            skipped.append(jp.name)
        else:
            rows.append(r)
    if skipped:
        print(f"[INFO] skipped {len(skipped)} non-v16 files (e.g. {skipped[:3]})")
    return pd.DataFrame(rows)


def paired_v13(df_v16: pd.DataFrame, v13_parquet: Path) -> pd.DataFrame:
    """v13 정본 (cell, sel, K) 의 B1·CaseA·CaseB 16-method 평균 → CaseC v16 와 paired join.

    v13 row = (cell, sel, K, method, mode={B1,CaseA,CaseB}, qe_trim, ...). mode 별로 method
    평균 → CaseC v16 와 (cell, sel, K) join.
    """
    df_v13 = pd.read_parquet(v13_parquet)
    needed = {"cell", "sel", "K", "mode", "qe_trim"}
    if not needed.issubset(df_v13.columns):
        raise ValueError(f"v13 parquet missing cols: {needed - set(df_v13.columns)}")
    # mode 별로 method 평균 (B1/CaseA/CaseB) — (cell, sel, K) grain
    v13_grain = df_v13.groupby(["cell", "sel", "K", "mode"], as_index=False)["qe_trim"].mean()
    # pivot mode → 컬럼 (qe_trim_B1, qe_trim_CaseA, qe_trim_CaseB)
    v13_wide = v13_grain.pivot_table(index=["cell", "sel", "K"], columns="mode",
                                      values="qe_trim").reset_index()
    v13_wide.columns.name = None
    rename_cols = {m: f"qe_trim_{m}" for m in ("B1", "CaseA", "CaseB")
                   if m in v13_wide.columns}
    v13_wide = v13_wide.rename(columns=rename_cols)

    # v16 CaseC 와 join (cell, sel, K)
    paired = df_v16.merge(v13_wide, on=["cell", "sel", "K"], how="left",
                          suffixes=("_caseC", ""))
    paired = paired.rename(columns={"qe_trim": "qe_trim_CaseC_v16"})

    # paired Δ% (CaseC v16 vs B1/CaseB)
    if "qe_trim_B1" in paired.columns:
        paired["caseC_vs_B1_pct"] = (
            (paired["qe_trim_CaseC_v16"] - paired["qe_trim_B1"]) / paired["qe_trim_B1"] * 100
        )
    if "qe_trim_CaseB" in paired.columns:
        paired["caseC_vs_CaseB_pct"] = (
            (paired["qe_trim_CaseC_v16"] - paired["qe_trim_CaseB"]) /
            paired["qe_trim_CaseB"] * 100
        )
    return paired


def write_summary(paired: pd.DataFrame, out: Path) -> None:
    from datetime import datetime, timezone, timedelta
    kst = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M KST")
    lines = []
    lines.append(f"# offline CaseC v16 전수 95 tuple — aggregate summary ({kst})\n")
    lines.append(f"- total v16 tuples: **{len(paired)}**\n")
    lines.append(f"- unique cells: {paired['cell'].nunique()} · "
                 f"unique sels: {sorted(paired['sel'].unique())} · "
                 f"unique K: {sorted(paired['K'].unique())}\n")

    matched_b1 = paired["qe_trim_B1"].notna().sum() if "qe_trim_B1" in paired else 0
    matched_caseB = paired["qe_trim_CaseB"].notna().sum() if "qe_trim_CaseB" in paired else 0
    lines.append(f"- v13 paired matched: B1={matched_b1} · CaseB={matched_caseB} "
                 f"(missing → v13 정본에 없는 tuple)\n")

    lines.append("\n## 1. ★ CaseC v16 vs B1 (cell-level paired, mode 평균)\n")
    if "caseC_vs_B1_pct" in paired.columns:
        valid = paired["caseC_vs_B1_pct"].dropna()
        if len(valid):
            better = (valid < 0).sum()
            lines.append(f"- paired tuples: {len(valid)}\n")
            lines.append(f"- CaseC better (qe_trim < B1): **{better}/{len(valid)} = "
                         f"{better/len(valid)*100:.1f}%**\n")
            lines.append(f"- median Δ% (CaseC vs B1): **{valid.median():+.2f}%**\n")
            lines.append(f"- mean Δ% (trimmed 5%): "
                         f"{np.percentile(valid, [5, 95]).mean():+.2f}%\n")
            lines.append(f"- distribution Δ%: min {valid.min():+.2f} / q25 "
                         f"{valid.quantile(.25):+.2f} / q75 {valid.quantile(.75):+.2f} / "
                         f"max {valid.max():+.2f}\n")

    lines.append("\n## 2. CaseC v16 vs CaseB (cell-level paired, mode 평균)\n")
    if "caseC_vs_CaseB_pct" in paired.columns:
        valid = paired["caseC_vs_CaseB_pct"].dropna()
        if len(valid):
            better = (valid < 0).sum()
            lines.append(f"- paired tuples: {len(valid)}\n")
            lines.append(f"- CaseC better (qe_trim < CaseB): **{better}/{len(valid)} = "
                         f"{better/len(valid)*100:.1f}%**\n")
            lines.append(f"- median Δ% (CaseC vs CaseB): **{valid.median():+.2f}%**\n")

    lines.append("\n## 3. mean qe_trim 분포 (sf · sel · K 별)\n")
    pivot_sf = paired.groupby("sf")["qe_trim_CaseC_v16"].agg(["count", "mean", "median",
                                                                "std", "min", "max"]).round(4)
    lines.append("### by sf\n")
    lines.append(pivot_sf.to_markdown())
    pivot_sel = paired.groupby("sel")["qe_trim_CaseC_v16"].agg(["count", "mean", "median",
                                                                  "std"]).round(4)
    lines.append("\n### by sel\n")
    lines.append(pivot_sel.to_markdown())
    pivot_K = paired.groupby("K")["qe_trim_CaseC_v16"].agg(["count", "mean", "median",
                                                              "std"]).round(4)
    lines.append("\n### by K\n")
    lines.append(pivot_K.to_markdown())

    lines.append("\n## 4. 95 tuple 전수 표 (cell · sel · K · qe_trim_CaseC · vs B1 · vs CaseB)\n")
    cols = ["cell", "sf", "sel", "K", "qe_trim_CaseC_v16"]
    if "qe_trim_B1" in paired.columns:
        cols += ["qe_trim_B1", "caseC_vs_B1_pct"]
    if "qe_trim_CaseB" in paired.columns:
        cols += ["qe_trim_CaseB", "caseC_vs_CaseB_pct"]
    cols += ["size_a_mean", "size_b_mean"]
    available = [c for c in cols if c in paired.columns]
    table = paired[available].sort_values(["cell", "sel", "K"]).round(4)
    lines.append(table.to_markdown(index=False))

    out.write_text("\n".join(lines))
    print(f"saved {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v16-dir", type=Path, required=True)
    ap.add_argument("--v13-parquet", type=Path,
                    default=Path("/mnt/hdd0/home/capstone2026/cache/rq3/"
                                  "aggregated_v13_full.parquet"))
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    df_v16 = collect_v16(args.v16_dir)
    if df_v16.empty:
        raise SystemExit(f"no v16 CaseC JSON found in {args.v16_dir}")
    print(f"loaded {len(df_v16)} v16 CaseC tuples from {args.v16_dir}")

    paired = paired_v13(df_v16, args.v13_parquet)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    paired.to_parquet(args.output_dir / "v16_full95_paired.parquet", index=False)
    print(f"saved v16_full95_paired.parquet ({len(paired)} rows)")

    write_summary(paired, args.output_dir / "v16_full95_summary.md")


if __name__ == "__main__":
    main()
