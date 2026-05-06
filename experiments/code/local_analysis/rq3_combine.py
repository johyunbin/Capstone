#!/usr/bin/env python3
"""
rq3_combine.py — RQ3 7-way 결과 통합 분석 (post-measurement orchestrator).

각 method 의 측정 parquet 을 자동 탐색·로드해 mode 이름을 canonical 로 정규화하고,
recovery_rate 라이브러리 (P1) 를 호출해 method × dataset × selectivity 단위 요약 표,
paired Wilcoxon BH-FDR 표, recovery 평균 ranking 표를 한 번에 생성.

자동 탐색 위치 (--results 경로 아래 재귀):
  rq2_aware/.../rq2_alloc.parquet     → mode='bernoulli' → 'random20', 'equal' → 'km20'
  rq3_agnostic/.../rq3_random20.parquet → mode='random20' (혹은 같은 의미 'bernoulli')
  rq3_agnostic/.../rq3_<method>.parquet → method 모드 그대로 (bernoulli row 는 drop)

Outputs (--out-dir 디렉토리 아래):
  rq3_combined.parquet    long-form 통합 (dataset/mode/selectivity/seed/query_id/q_error)
  rq3_summary.csv         method × dataset × sel 요약 (mean q_error, recovery, metric)
  rq3_pairwise.csv        method vs RANDOM20 paired Wilcoxon BH-FDR
  rq3_ranking.csv         method 평균 recovery_rate 내림차순 ranking
  rq3_combine_meta.json   사용한 입력 경로 + 행 수 + KST 시각

사용법:
  python3 experiments/code/local_analysis/rq3_combine.py
  python3 experiments/code/local_analysis/rq3_combine.py \
      --results experiments/results --out-dir experiments/results/rq3_agnostic/2026_05_08

★ Figures 생성은 본 스크립트가 산출한 rq3_combined.parquet 를 rq3_figures.py 에 전달:
  python3 rq3_figures.py --rq3 experiments/results/rq3_agnostic/2026_05_08/rq3_combined.parquet
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent))
from recovery_rate import (
    paired_wilcoxon_with_bh_fdr,
    summarize_method,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS = REPO_ROOT / "experiments" / "results"
DEFAULT_OUT = REPO_ROOT / "experiments" / "results" / "rq3_agnostic"

# rq2_alloc 의 mode 컬럼 → canonical mode 이름
# 주의: RQ2 의 'bernoulli' 는 TABLESAMPLE BERNOULLI baseline, RANDOM20 (랜덤 K=20 분할 +
# equal allocation) 과는 다른 method. RANDOM20 은 measure_offline.py 가 별도 측정.
# RQ2 의 'equal' 은 KM20 oracle (DB stratum_id + equal allocation) 와 동일 → km20 alias.
RQ2_MODE_MAP = {
    "equal": "km20",
}
# RQ2 alloc 에서 canonical 분석에 가져올 mode
RQ2_MODE_KEEP = {"bernoulli", "equal"}  # bernoulli (sanity), equal→km20

# rq3_*.parquet 의 mode 가 method 별 alias 일 때 canonical 이름으로
RQ3_MODE_ALIAS = {
    "lsh_proportional": "lsh",
    "random_projection": "random_proj",
    "minibatch_kmeans": "minibatch",
    # standalone 측정에서 이미 canonical: kde_pilot, distance_shell, hilbert, importance ...
}

# rq3 parquet 의 모든 mode 유지 (random20/km20/methods + bernoulli sanity)
# dedup 으로 중복 (dataset, mode, sel, seed, qid) 제거.
DROP_FROM_RQ3: set[str] = set()


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")


def discover_parquets(results_root: Path) -> dict[str, list[Path]]:
    """results_root 아래에서 RQ2 alloc + RQ3 method parquet 을 카테고리별로 수집."""
    found: dict[str, list[Path]] = {"rq2_alloc": [], "rq3_method": []}
    for p in sorted(results_root.rglob("*.parquet")):
        name = p.name.lower()
        if name == "rq2_alloc.parquet":
            found["rq2_alloc"].append(p)
        elif name.startswith("rq3_") and "size_sensitivity" not in name:
            found["rq3_method"].append(p)
    return found


def load_rq2_alloc(path: Path) -> pd.DataFrame:
    """rq2_alloc.parquet 에서 bernoulli (sanity) + equal→km20 추출 + rename."""
    df = pd.read_parquet(path)
    keep = df[df["mode"].isin(RQ2_MODE_KEEP)].copy()
    keep["mode"] = keep["mode"].replace(RQ2_MODE_MAP)
    return keep


def load_rq3_method(path: Path) -> pd.DataFrame:
    """rq3 method parquet 에서 baseline (bernoulli) drop, alias 정규화."""
    df = pd.read_parquet(path)
    df = df[~df["mode"].isin(DROP_FROM_RQ3)].copy()
    df["mode"] = df["mode"].replace(RQ3_MODE_ALIAS)
    return df


def required_cols() -> set[str]:
    return {"dataset", "mode", "selectivity", "seed", "query_id", "q_error"}


def coerce_long_form(df: pd.DataFrame, source_label: str) -> pd.DataFrame:
    """long-form 스키마 검증 + 누락 컬럼 NaN 보충."""
    missing = required_cols() - set(df.columns)
    if missing:
        raise ValueError(
            f"[{source_label}] 누락 컬럼 {missing}. 측정 parquet 스키마 점검 필요."
        )
    return df[list(required_cols())].copy()


def build_combined(
    rq2_paths: list[Path],
    rq3_paths: list[Path],
) -> tuple[pd.DataFrame, list[dict]]:
    """RQ2 alloc + RQ3 method parquet 을 하나의 long-form 으로 결합."""
    parts: list[pd.DataFrame] = []
    sources: list[dict] = []

    for p in rq2_paths:
        sub = load_rq2_alloc(p)
        sub = coerce_long_form(sub, p.name)
        parts.append(sub)
        sources.append({"path": str(p), "kind": "rq2_alloc", "rows": len(sub),
                        "modes": sorted(sub["mode"].unique().tolist())})

    for p in rq3_paths:
        sub = load_rq3_method(p)
        sub = coerce_long_form(sub, p.name)
        parts.append(sub)
        sources.append({"path": str(p), "kind": "rq3_method", "rows": len(sub),
                        "modes": sorted(sub["mode"].unique().tolist())})

    if not parts:
        raise SystemExit(
            "no parquet found. --results 경로 확인. RQ2 alloc 1개 + RQ3 method 1+ 필요."
        )

    combined = pd.concat(parts, ignore_index=True)
    # random20 가 RQ2 + RQ3-random20.parquet 양쪽에서 들어오면 dedupe (rq2 우선)
    combined = combined.drop_duplicates(
        subset=["dataset", "mode", "selectivity", "seed", "query_id"], keep="first"
    )
    return combined, sources


def make_summary(combined: pd.DataFrame, methods: list[str]) -> pd.DataFrame:
    """각 method 의 (dataset × sel) recovery_rate 표 통합."""
    parts = []
    for m in methods:
        if m not in combined["mode"].unique():
            continue
        sm = summarize_method(combined, method=m)
        sm["method"] = m
        parts.append(sm)
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts, ignore_index=True)
    cols = ["method"] + [c for c in out.columns if c != "method"]
    return out[cols]


def make_pairwise(combined: pd.DataFrame, methods: list[str]) -> pd.DataFrame:
    """method 마다 RANDOM20 baseline 대비 paired Wilcoxon BH-FDR (less = method 가 더 작은 q_error)."""
    pairs = [(m, "random20") for m in methods if m in combined["mode"].unique()]
    if not pairs:
        return pd.DataFrame()
    return paired_wilcoxon_with_bh_fdr(
        combined, compare_pairs=pairs, alternative="less", drop_nan=True,
    )


def make_ranking(summary: pd.DataFrame) -> pd.DataFrame:
    """method 평균 recovery_rate 내림차순 ranking (NaN/fallback 셀 제외)."""
    if summary.empty:
        return pd.DataFrame()
    valid = summary[summary["metric"] == "recovery"].dropna(subset=["recovery"])
    if valid.empty:
        return pd.DataFrame()
    g = valid.groupby("method").agg(
        recovery_mean=("recovery", "mean"),
        recovery_std=("recovery", "std"),
        n_cells=("recovery", "size"),
    ).reset_index()
    g = g.sort_values("recovery_mean", ascending=False).reset_index(drop=True)
    g["rank"] = g.index + 1
    return g[["rank", "method", "recovery_mean", "recovery_std", "n_cells"]]


# 7-way method canonical 이름 (rq3_figures.py METHOD_ORDER 와 동일 순서·동일 이름)
METHODS_7WAY = [
    "random_proj", "lsh", "hilbert", "minibatch",
    "distance_shell", "kde_pilot", "importance",
]


def main():
    ap = argparse.ArgumentParser(description="RQ3 7-way 통합 분석 combiner")
    ap.add_argument("--results", type=Path, default=DEFAULT_RESULTS,
                    help=f"results root (default: {DEFAULT_RESULTS})")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="output dir (default: <results>/rq3_agnostic/<YYYY_MM_DD>)")
    ap.add_argument("--methods", nargs="*", default=METHODS_7WAY,
                    help="대상 method canonical 이름 (default: 7-way 전체)")
    args = ap.parse_args()

    out_dir = args.out_dir or (
        DEFAULT_OUT / datetime.now(timezone(timedelta(hours=9))).strftime("%Y_%m_%d")
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{kst()}] === RQ3 combine — results={args.results} ===")
    found = discover_parquets(args.results)
    print(f"  rq2_alloc paths: {[str(p) for p in found['rq2_alloc']]}")
    print(f"  rq3_method paths: {[str(p) for p in found['rq3_method']]}")

    combined, sources = build_combined(found["rq2_alloc"], found["rq3_method"])
    print(f"\n[{kst()}] combined long-form rows: {len(combined):,}")
    print(f"  modes present: {sorted(combined['mode'].unique().tolist())}")
    print(f"  datasets: {sorted(combined['dataset'].unique().tolist())}")
    print(f"  selectivities: {sorted(combined['selectivity'].unique().tolist())}")

    # 1) combined parquet
    combined_path = out_dir / "rq3_combined.parquet"
    combined.to_parquet(combined_path, index=False)
    print(f"  → {combined_path}")

    # 2) summary
    summary = make_summary(combined, args.methods)
    summary_path = out_dir / "rq3_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"  → {summary_path}  ({len(summary)} rows)")

    # 3) pairwise (method vs RANDOM20)
    pairwise = make_pairwise(combined, args.methods)
    pairwise_path = out_dir / "rq3_pairwise.csv"
    pairwise.to_csv(pairwise_path, index=False)
    n_sig = int(pairwise["reject_005"].sum()) if not pairwise.empty else 0
    print(f"  → {pairwise_path}  ({len(pairwise)} 비교, BH-FDR p ≤ 0.05 유의: {n_sig})")

    # 4) ranking
    ranking = make_ranking(summary)
    ranking_path = out_dir / "rq3_ranking.csv"
    ranking.to_csv(ranking_path, index=False)
    print(f"  → {ranking_path}")
    if not ranking.empty:
        print("\n=== Recovery Rate Ranking (DEEP+SIFT × 5sel 평균) ===")
        print(ranking.to_string(index=False, float_format=lambda x: f"{x:+.3f}"))

    # 5) meta
    meta = {
        "kst": kst(),
        "results_root": str(args.results),
        "out_dir": str(out_dir),
        "sources": sources,
        "n_rows_combined": int(len(combined)),
        "modes": sorted(combined["mode"].unique().tolist()),
        "methods_evaluated": args.methods,
        "n_pairwise_significant_BH": n_sig,
    }
    meta_path = out_dir / "rq3_combine_meta.json"
    with meta_path.open("w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False, default=str)
    print(f"  → {meta_path}")

    print(f"\n[{kst()}] 완료. 다음:")
    print(f"  python3 experiments/code/local_analysis/rq3_figures.py --rq3 {combined_path}")


if __name__ == "__main__":
    main()
