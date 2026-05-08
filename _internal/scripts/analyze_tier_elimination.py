#!/usr/bin/env python3
"""
RQ3 30-method tier elimination analyzer (5/27 발표 narrative 용).

30 RQ3 distribution-agnostic method × 5 dataset (DEEP/SIFT/SSN/WIKI/YFCC) × 3 scale (sf1/sf10/sf100)
= 30 × 15 cell. 측정 완료 후 4-tier 순차 제거로 4~6개 winner 추출.

Tier 1 — 통계 robustness (paired bootstrap CI 0 제외)
    각 cell (dataset × sf × sel=0.10) 에서 BERN(385) baseline 대비 paired Δ% 계산.
    CI 가 0 을 *improve 방향* (Δ% < 0; method_median < bern_median) 으로 제외하면 cell pass.
    Method pass: 15 cell 중 ≥5 cell pass.

Tier 2 — Production cost (deterministic OR cheap learn)
    method 의 meta JSON 에서 learn_frac 또는 deterministic 여부 확인.
    Pass: learn_frac ≤ 0.01  OR  is_deterministic = True.
    (annotated: hilbert/zorder/distance_shell = deterministic;
     minibatch_partial = OLTP-friendly partial_fit;
     km_k_optimal/hdbscan/spectral = high learn cost.)

Tier 3 — Scale-invariance (sign agreement 80%+)
    같은 method 의 (sf1, sf10) 와 (sf10, sf100) Δ% 부호가 일치하는 비율.
    각 (dataset × sel) 에 대해 인접 sf 쌍의 sign 비교 → 평균 ≥ 0.8.

Tier 4 — Distribution-robustness
    Tier 1 cell pass 를 dataset 별로 집계, 적어도 1 cell 이 CI 0 제외 improve 인 dataset 수 ≥ 3.

산출:
    experiments/results/rq3_agnostic/tier_elimination_table.csv
        — method, tier1_pass / tier1_pct / tier2_production_friendly /
          tier3_scale_invariance_pct / tier4_dataset_pass / final_winner / best_cell
    experiments/results/rq3_agnostic/tier_elimination_summary.md
        — 단계별 elimination narrative + winners + per-dataset 추천
    experiments/figures/rq3_tier_elimination.png  (--plot 시)
        — method 별 tier1~4 pass 비율 bar chart

CLI:
    python3 analyze_tier_elimination.py --rsync-first \
        --datasets DEEP SIFT SSN WIKI YFCC \
        --sf 1 10 100 \
        --output-dir experiments/results/rq3_agnostic/

함정:
    - 측정이 부분적으로만 완료된 method 도 grace 처리 (cell 수 적으면 N/A 표기)
    - BERN baseline parquet 은 method-자체 parquet 안의 mode='bernoulli' 행으로 함께 측정됨.
      별도 parquet 이 없을 경우 fallback: rq3_*_meta.json 에 modes=['bernoulli', method] 패턴.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 경로
# ---------------------------------------------------------------------------

LOCAL_CACHE = Path("/Users/hyunbin/Capstone/_internal/cache/rq1")
SERVER_CACHE = "capstone:/mnt/hdd0/home/capstone2026/cache/rq1/"
DEFAULT_OUT_DIR = Path("/Users/hyunbin/Capstone/experiments/results/rq3_agnostic")
DEFAULT_FIG_DIR = Path("/Users/hyunbin/Capstone/experiments/figures")

DEFAULT_DATASETS = ("DEEP", "SIFT", "SSN", "WIKI", "YFCC")
DEFAULT_SFS = (1, 10, 100)

# 30-method roster — 새로 만든 8개 포함 (32개로 보이지만 km_k_50 하나로 묶음)
ALL_METHODS = (
    "hilbert", "hybrid", "minibatch", "minibatch_partial", "kdtree", "zorder",
    "pca1d", "gmm", "lsh", "pq", "sobol", "distance_shell", "random_proj",
    "kde_pilot", "sparse_rp", "importance_sampling", "hdbscan", "birch",
    "spectral", "opq", "km_k_50", "reservoir",
    # new 8
    "dbscan", "optics", "agglomerative", "hierarchical_kmeans", "faiss_ivf",
    "pca_kmeans", "kmeans_pp", "coresets",
)

# Production cost annotation
DETERMINISTIC_METHODS = {"hilbert", "zorder", "distance_shell", "sobol", "reservoir"}
HIGH_LEARN_METHODS = {"hdbscan", "spectral", "optics", "agglomerative", "dbscan",
                      "hierarchical_kmeans", "km_k_50"}
OLTP_FRIENDLY = {"minibatch_partial"}

# Tier 1 기준
TIER1_TARGET_SEL = 0.10
TIER1_MIN_PASS_CELLS = 5
TIER1_TOTAL_CELLS = 15  # 5 dataset × 3 sf
TIER1_BOOTSTRAP_N = 1000
TIER1_RNG_SEED = 42

# Tier 2 기준
TIER2_LEARN_FRAC_THRESH = 0.01

# Tier 3 기준
TIER3_SIGN_AGREEMENT_THRESH = 0.80

# Tier 4 기준
TIER4_MIN_DATASETS = 3

# parquet filename 패턴: rq3_{1m|8m|sf{X}}_{dataset_lc?}_{method}.parquet 또는
# rq3_{dataset_lc}_sf{X}_{method}.parquet
PAT_RQ3 = re.compile(
    r"rq3_(?:(?P<scale_legacy>1m|8m)_)?"
    r"(?P<dataset>[A-Za-z]+(?:\+\+)?)?_?"
    r"(?:sf(?P<sf>\d+)_)?"
    r"(?P<method>[a-z][a-z0-9_]*?)"
    r"(?:_sel_expand|_meta)?\.parquet$"
)


# ---------------------------------------------------------------------------
# rsync
# ---------------------------------------------------------------------------

def rsync_from_server(local: Path) -> None:
    local.mkdir(parents=True, exist_ok=True)
    cmd = [
        "rsync", "-avz",
        "--include=rq3_*.parquet", "--include=rq3_*_meta.json",
        "--include=*/", "--exclude=*",
        SERVER_CACHE, str(local) + "/",
    ]
    print(f"[rsync] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# parquet 디스커버리
# ---------------------------------------------------------------------------

@dataclass
class ParquetEntry:
    path: Path
    dataset: str
    sf: int
    method: str
    meta: dict


def _parse_filename(path: Path) -> dict | None:
    """파일명에서 dataset / sf / method 추출.

    지원 패턴:
      - rq3_1m_sift_hilbert.parquet            → ds=SIFT, sf=1, method=hilbert
      - rq3_8m_birch.parquet                   → ds=SIFT(default at 8m), sf=8 (legacy)
      - rq3_DEEP_sf10_minibatch.parquet        → ds=DEEP, sf=10, method=minibatch
      - rq3_DEEP_sf1_pca1d.parquet             → ds=DEEP, sf=1, method=pca1d
    """
    name = path.name

    # 1) New canonical pattern: rq3_{DS}_sf{X}_{method}.parquet
    m = re.match(r"rq3_(?P<ds>[A-Za-z\+]+)_sf(?P<sf>\d+)_(?P<method>[a-z0-9_]+)\.parquet$", name)
    if m and not name.endswith("_meta.json"):
        method = m.group("method")
        # sel_expand suffix 제거
        if method.endswith("_sel_expand"):
            method = method[: -len("_sel_expand")]
        return {
            "dataset": m.group("ds").upper(),
            "sf": int(m.group("sf")),
            "method": method,
        }

    # 2) Legacy 1m: rq3_1m_{ds_lc}_{method}.parquet  (1m = sf1)
    m = re.match(r"rq3_1m_(?P<ds>[a-z]+)_(?P<method>[a-z0-9_]+)\.parquet$", name)
    if m:
        method = m.group("method")
        return {
            "dataset": m.group("ds").upper(),
            "sf": 1,
            "method": method,
        }

    # 3) Legacy 8m: rq3_8m_{method}.parquet (default SIFT, sf=8)
    m = re.match(r"rq3_8m_(?P<method>[a-z0-9_]+?)(?P<expand>_sel_expand)?\.parquet$", name)
    if m:
        method = m.group("method")
        return {
            "dataset": "SIFT",
            "sf": 8,
            "method": method,
        }

    return None


def discover_parquets(cache_dirs: Iterable[Path]) -> list[ParquetEntry]:
    out: list[ParquetEntry] = []
    seen: set[tuple[str, int, str]] = set()
    for cache_dir in cache_dirs:
        if not cache_dir.exists():
            continue
        for p in sorted(cache_dir.glob("rq3_*.parquet")):
            parsed = _parse_filename(p)
            if not parsed:
                continue
            key = (parsed["dataset"], parsed["sf"], parsed["method"])
            if key in seen:
                continue  # prefer first cache_dir (results dir > local cache)
            seen.add(key)
            meta_path = p.with_name(p.stem + "_meta.json")
            meta = {}
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text())
                except Exception as exc:
                    print(f"[warn] meta parse fail: {meta_path.name}: {exc}")
            out.append(ParquetEntry(
                path=p, dataset=parsed["dataset"], sf=parsed["sf"],
                method=parsed["method"], meta=meta,
            ))
    return out


# ---------------------------------------------------------------------------
# Tier 1 — paired bootstrap CI
# ---------------------------------------------------------------------------

def _paired_bootstrap_delta_pct(
    method_qe: np.ndarray,
    bern_qe: np.ndarray,
    n_iter: int = TIER1_BOOTSTRAP_N,
    rng_seed: int = TIER1_RNG_SEED,
) -> tuple[float, float, float, bool]:
    """
    Δ% = 100 * (method_median - bern_median) / bern_median.
    음수 = method 가 더 좋음 (improve).

    Paired bootstrap: 동일 인덱스 (query_id × seed) 쌍을 함께 resample 해
    median 차이의 percentile 95% CI 도출. CI 가 0 을 improve 방향 (상한 < 0) 으로 제외하면 pass.

    Returns (delta_pct, ci_lo, ci_hi, ci_excludes_zero_improve)
    """
    if len(method_qe) == 0 or len(bern_qe) == 0:
        return (np.nan, np.nan, np.nan, False)
    n = min(len(method_qe), len(bern_qe))
    a = method_qe[:n]
    b = bern_qe[:n]
    rng = np.random.default_rng(rng_seed)

    deltas = np.empty(n_iter, dtype=np.float64)
    for i in range(n_iter):
        idx = rng.integers(0, n, size=n)
        ma = np.median(a[idx])
        mb = np.median(b[idx])
        if mb == 0:
            deltas[i] = np.nan
        else:
            deltas[i] = 100.0 * (ma - mb) / mb

    deltas = deltas[~np.isnan(deltas)]
    if deltas.size == 0:
        return (np.nan, np.nan, np.nan, False)

    point = float(100.0 * (np.median(a) - np.median(b)) / np.median(b)) if np.median(b) != 0 else np.nan
    ci_lo, ci_hi = np.percentile(deltas, [2.5, 97.5])
    # improve 방향 (Δ% < 0) 으로 0 제외
    ci_excl_improve = bool(ci_hi < 0)
    return (point, float(ci_lo), float(ci_hi), ci_excl_improve)


def _extract_method_bern_pairs(
    df: pd.DataFrame, method: str, sel: float,
) -> tuple[np.ndarray, np.ndarray] | None:
    """
    parquet 안에서 mode==method 와 mode in {'bernoulli','bern_385'} 를 추출,
    같은 (query_id, seed) 키로 paired q_error 두 배열 반환.
    """
    if "mode" not in df.columns or "q_error" not in df.columns:
        return None

    method_mask = df["mode"].astype(str) == method
    bern_mask = df["mode"].astype(str).isin(["bernoulli", "bern_385", "bern385"])

    sel_mask = np.isclose(df["selectivity"].astype(float), sel, atol=1e-6)
    method_df = df[method_mask & sel_mask]
    bern_df = df[bern_mask & sel_mask]

    if method_df.empty or bern_df.empty:
        return None

    key_cols = [c for c in ["query_id", "seed"] if c in df.columns]
    if not key_cols:
        return None

    merged = pd.merge(
        method_df[key_cols + ["q_error"]],
        bern_df[key_cols + ["q_error"]],
        on=key_cols, suffixes=("_method", "_bern"),
    )
    if merged.empty:
        return None
    return merged["q_error_method"].to_numpy(), merged["q_error_bern"].to_numpy()


def tier1_for_method(
    entries: list[ParquetEntry], method: str,
    datasets: tuple[str, ...], sfs: tuple[int, ...],
) -> dict:
    """method × (dataset × sf) cell 별 paired bootstrap → cell pass count.

    Returns:
        {
            'cells': [{dataset, sf, delta_pct, ci_lo, ci_hi, ci_excl_improve}, ...],
            'n_pass': int, 'n_total': int, 'pct_pass': float,
            'best_cell': {dataset, sf, delta_pct},  # most negative Δ%
            'per_dataset_pass': {ds: cells_pass},
        }
    """
    method_entries = [e for e in entries if e.method == method]
    cells: list[dict] = []
    per_dataset_pass: dict[str, int] = {ds: 0 for ds in datasets}

    for ds in datasets:
        for sf in sfs:
            match = [e for e in method_entries if e.dataset == ds and e.sf == sf]
            if not match:
                cells.append({
                    "dataset": ds, "sf": sf, "delta_pct": np.nan,
                    "ci_lo": np.nan, "ci_hi": np.nan, "ci_excl_improve": False,
                    "n_pairs": 0, "missing": True,
                })
                continue
            entry = match[0]
            try:
                df = pd.read_parquet(entry.path)
            except Exception as exc:
                print(f"[warn] read fail: {entry.path.name}: {exc}")
                cells.append({
                    "dataset": ds, "sf": sf, "delta_pct": np.nan,
                    "ci_lo": np.nan, "ci_hi": np.nan, "ci_excl_improve": False,
                    "n_pairs": 0, "missing": True,
                })
                continue

            pair = _extract_method_bern_pairs(df, method, TIER1_TARGET_SEL)
            if pair is None:
                cells.append({
                    "dataset": ds, "sf": sf, "delta_pct": np.nan,
                    "ci_lo": np.nan, "ci_hi": np.nan, "ci_excl_improve": False,
                    "n_pairs": 0, "missing": True,
                })
                continue

            method_qe, bern_qe = pair
            dp, lo, hi, excl = _paired_bootstrap_delta_pct(method_qe, bern_qe)
            cells.append({
                "dataset": ds, "sf": sf, "delta_pct": dp,
                "ci_lo": lo, "ci_hi": hi, "ci_excl_improve": excl,
                "n_pairs": len(method_qe), "missing": False,
            })
            if excl:
                per_dataset_pass[ds] = per_dataset_pass.get(ds, 0) + 1

    n_pass = sum(1 for c in cells if c["ci_excl_improve"])
    valid = [c for c in cells if not c["missing"] and not np.isnan(c.get("delta_pct", np.nan))]
    best_cell = min(valid, key=lambda c: c["delta_pct"]) if valid else None
    return {
        "cells": cells,
        "n_pass": n_pass,
        "n_total": TIER1_TOTAL_CELLS,
        "pct_pass": n_pass / TIER1_TOTAL_CELLS,
        "best_cell": best_cell,
        "per_dataset_pass": per_dataset_pass,
    }


# ---------------------------------------------------------------------------
# Tier 2 — Production cost
# ---------------------------------------------------------------------------

def tier2_for_method(entries: list[ParquetEntry], method: str) -> dict:
    """meta JSON 에서 learn_frac 추출, deterministic annotation 적용.

    Returns {'pass': bool, 'reason': str, 'learn_frac': float|None, 'fit_time_s': float|None}
    """
    method_entries = [e for e in entries if e.method == method and e.meta]
    learn_fracs: list[float] = []
    fit_times: list[float] = []
    for e in method_entries:
        m = e.meta
        if "learn_frac" in m:
            try:
                learn_fracs.append(float(m["learn_frac"]))
            except Exception:
                pass
        # fit_time 은 다양한 키로 저장됨
        for key in ("fit_time", "fit_time_s", "elapsed_s", "learn_time_s"):
            if key in m:
                try:
                    fit_times.append(float(m[key]))
                    break
                except Exception:
                    pass

    learn_frac = float(np.mean(learn_fracs)) if learn_fracs else None
    fit_time = float(np.mean(fit_times)) if fit_times else None

    is_det = method in DETERMINISTIC_METHODS
    is_oltp = method in OLTP_FRIENDLY
    is_high = method in HIGH_LEARN_METHODS

    if is_det:
        return {"pass": True, "reason": "deterministic (no learn)",
                "learn_frac": learn_frac, "fit_time_s": fit_time}
    if is_oltp:
        return {"pass": True, "reason": "OLTP partial_fit",
                "learn_frac": learn_frac, "fit_time_s": fit_time}
    if is_high:
        return {"pass": False, "reason": "high learn cost (annotated)",
                "learn_frac": learn_frac, "fit_time_s": fit_time}
    if learn_frac is not None and learn_frac <= TIER2_LEARN_FRAC_THRESH:
        return {"pass": True, "reason": f"learn_frac={learn_frac:.3f} ≤ {TIER2_LEARN_FRAC_THRESH}",
                "learn_frac": learn_frac, "fit_time_s": fit_time}
    if learn_frac is not None:
        return {"pass": False, "reason": f"learn_frac={learn_frac:.3f} > {TIER2_LEARN_FRAC_THRESH}",
                "learn_frac": learn_frac, "fit_time_s": fit_time}
    # learn_frac 정보 없음 — conservative pass=False 단, deterministic 도 아님
    return {"pass": False, "reason": "learn_frac not in meta",
            "learn_frac": None, "fit_time_s": fit_time}


# ---------------------------------------------------------------------------
# Tier 3 — Scale-invariance
# ---------------------------------------------------------------------------

def _delta_pct_per_cell(
    df_method: pd.DataFrame, df_bern: pd.DataFrame,
    sel: float,
) -> float:
    sel_mask_m = np.isclose(df_method["selectivity"].astype(float), sel, atol=1e-6)
    sel_mask_b = np.isclose(df_bern["selectivity"].astype(float), sel, atol=1e-6)
    a = df_method.loc[sel_mask_m, "q_error"].to_numpy()
    b = df_bern.loc[sel_mask_b, "q_error"].to_numpy()
    if len(a) == 0 or len(b) == 0:
        return np.nan
    ma = float(np.median(a))
    mb = float(np.median(b))
    if mb == 0:
        return np.nan
    return 100.0 * (ma - mb) / mb


def tier3_for_method(
    entries: list[ParquetEntry], method: str,
    datasets: tuple[str, ...], sfs: tuple[int, ...],
    sels: tuple[float, ...] = (0.01, 0.05, 0.10, 0.30, 0.50),
) -> dict:
    """인접 sf 쌍 (sf1↔sf10, sf10↔sf100) 의 Δ% sign 일치율.

    각 (dataset × sel) 에 대해 인접 sf 쌍의 sign 비교. 둘 다 negative or 둘 다 positive = agree.
    전체 비교 횟수 대비 agree 비율 ≥ 0.8 면 pass.
    """
    if len(sfs) < 2:
        return {"pass": False, "agreement_pct": np.nan, "n_compared": 0,
                "reason": "need ≥2 sf values"}

    sf_pairs = [(sfs[i], sfs[i + 1]) for i in range(len(sfs) - 1)]
    method_entries = [e for e in entries if e.method == method]

    # 미리 sf×dataset → df 캐시
    df_cache: dict[tuple[str, int], tuple[pd.DataFrame, pd.DataFrame]] = {}
    for e in method_entries:
        try:
            df = pd.read_parquet(e.path)
        except Exception:
            continue
        if "mode" not in df.columns:
            continue
        df_method = df[df["mode"].astype(str) == method]
        df_bern = df[df["mode"].astype(str).isin(["bernoulli", "bern_385", "bern385"])]
        if df_method.empty or df_bern.empty:
            continue
        df_cache[(e.dataset, e.sf)] = (df_method, df_bern)

    agree = 0
    total = 0
    per_dataset_agree: dict[str, dict] = {ds: {"agree": 0, "total": 0} for ds in datasets}
    for ds in datasets:
        for sel in sels:
            for sf_a, sf_b in sf_pairs:
                if (ds, sf_a) not in df_cache or (ds, sf_b) not in df_cache:
                    continue
                m_a, b_a = df_cache[(ds, sf_a)]
                m_b, b_b = df_cache[(ds, sf_b)]
                d_a = _delta_pct_per_cell(m_a, b_a, sel)
                d_b = _delta_pct_per_cell(m_b, b_b, sel)
                if np.isnan(d_a) or np.isnan(d_b):
                    continue
                total += 1
                per_dataset_agree[ds]["total"] += 1
                if (d_a < 0 and d_b < 0) or (d_a >= 0 and d_b >= 0):
                    agree += 1
                    per_dataset_agree[ds]["agree"] += 1

    if total == 0:
        return {"pass": False, "agreement_pct": np.nan, "n_compared": 0,
                "reason": "no comparable sf pairs"}
    pct = agree / total
    return {
        "pass": bool(pct >= TIER3_SIGN_AGREEMENT_THRESH),
        "agreement_pct": pct, "n_compared": total,
        "reason": f"{agree}/{total} sign agreements",
        "per_dataset": per_dataset_agree,
    }


# ---------------------------------------------------------------------------
# Tier 4 — Distribution-robustness
# ---------------------------------------------------------------------------

def tier4_for_method(tier1_result: dict, datasets: tuple[str, ...]) -> dict:
    per_ds = tier1_result.get("per_dataset_pass", {})
    pass_dataset_count = sum(1 for ds in datasets if per_ds.get(ds, 0) >= 1)
    return {
        "pass": pass_dataset_count >= TIER4_MIN_DATASETS,
        "dataset_pass_count": pass_dataset_count,
        "min_required": TIER4_MIN_DATASETS,
        "per_dataset_pass": per_ds,
    }


# ---------------------------------------------------------------------------
# 종합 분석 + 출력
# ---------------------------------------------------------------------------

def analyze_all(
    entries: list[ParquetEntry],
    methods: tuple[str, ...],
    datasets: tuple[str, ...],
    sfs: tuple[int, ...],
) -> pd.DataFrame:
    rows: list[dict] = []
    for method in methods:
        print(f"[tier-analyze] method={method}")
        t1 = tier1_for_method(entries, method, datasets, sfs)
        t2 = tier2_for_method(entries, method)
        t3 = tier3_for_method(entries, method, datasets, sfs)
        t4 = tier4_for_method(t1, datasets)
        final_winner = bool(t1["n_pass"] >= TIER1_MIN_PASS_CELLS and t2["pass"]
                            and t3["pass"] and t4["pass"])
        best = t1["best_cell"]
        best_str = (f"{best['dataset']}-sf{best['sf']} ({best['delta_pct']:+.2f}%)"
                    if best else "N/A")
        rows.append({
            "method": method,
            "tier1_pass": t1["n_pass"],
            "tier1_total": t1["n_total"],
            "tier1_pct": round(t1["pct_pass"], 4),
            "tier2_production_friendly": t2["pass"],
            "tier2_reason": t2["reason"],
            "tier2_learn_frac": t2["learn_frac"],
            "tier3_scale_invariance_pct": (
                round(t3["agreement_pct"], 4)
                if not np.isnan(t3.get("agreement_pct", np.nan))
                else np.nan
            ),
            "tier3_pass": t3["pass"],
            "tier3_n_compared": t3["n_compared"],
            "tier4_dataset_pass": t4["dataset_pass_count"],
            "tier4_pass": t4["pass"],
            "final_winner": final_winner,
            "best_cell": best_str,
            "_tier1": t1,
            "_tier2": t2,
            "_tier3": t3,
            "_tier4": t4,
        })
    return pd.DataFrame(rows)


def write_csv(df: pd.DataFrame, out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "method", "tier1_pass", "tier1_total", "tier1_pct",
        "tier2_production_friendly", "tier2_reason", "tier2_learn_frac",
        "tier3_scale_invariance_pct", "tier3_pass", "tier3_n_compared",
        "tier4_dataset_pass", "tier4_pass",
        "final_winner", "best_cell",
    ]
    df[cols].to_csv(out_csv, index=False)
    print(f"[csv] wrote {out_csv}  ({len(df)} methods)")


def write_summary_md(df: pd.DataFrame, out_md: Path,
                     datasets: tuple[str, ...], sfs: tuple[int, ...]) -> None:
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# RQ3 30-Method Tier Elimination Summary")
    lines.append("")
    lines.append(f"- Datasets: {', '.join(datasets)}")
    lines.append(f"- Scales: sf{', sf'.join(str(s) for s in sfs)}")
    lines.append(f"- Tier 1: paired bootstrap CI 0 제외 (improve 방향), ≥{TIER1_MIN_PASS_CELLS}/{TIER1_TOTAL_CELLS} cell")
    lines.append(f"- Tier 2: deterministic OR learn_frac ≤ {TIER2_LEARN_FRAC_THRESH}")
    lines.append(f"- Tier 3: 인접 sf 쌍 sign 일치 ≥ {int(TIER3_SIGN_AGREEMENT_THRESH * 100)}%")
    lines.append(f"- Tier 4: 5 dataset 중 ≥{TIER4_MIN_DATASETS} 개에서 ≥1 cell improve")
    lines.append("")

    # 단계별 elimination
    lines.append("## Elimination Funnel")
    lines.append("")
    eliminated_t1 = df[df["tier1_pass"] < TIER1_MIN_PASS_CELLS]
    lines.append(f"### Tier 1 탈락 ({len(eliminated_t1)} method)")
    for _, r in eliminated_t1.iterrows():
        lines.append(f"- **{r['method']}** — {r['tier1_pass']}/{r['tier1_total']} cell pass "
                     f"({r['tier1_pct']:.1%})")
    lines.append("")

    survived_t1 = df[df["tier1_pass"] >= TIER1_MIN_PASS_CELLS]
    eliminated_t2 = survived_t1[~survived_t1["tier2_production_friendly"]]
    lines.append(f"### Tier 2 탈락 ({len(eliminated_t2)} method)")
    for _, r in eliminated_t2.iterrows():
        lines.append(f"- **{r['method']}** — {r['tier2_reason']}")
    lines.append("")

    survived_t2 = survived_t1[survived_t1["tier2_production_friendly"]]
    eliminated_t3 = survived_t2[~survived_t2["tier3_pass"]]
    lines.append(f"### Tier 3 탈락 ({len(eliminated_t3)} method)")
    for _, r in eliminated_t3.iterrows():
        pct = r["tier3_scale_invariance_pct"]
        pct_str = f"{pct:.1%}" if not pd.isna(pct) else "N/A"
        lines.append(f"- **{r['method']}** — scale-invariance {pct_str} "
                     f"(n={int(r['tier3_n_compared'])})")
    lines.append("")

    survived_t3 = survived_t2[survived_t2["tier3_pass"]]
    eliminated_t4 = survived_t3[~survived_t3["tier4_pass"]]
    lines.append(f"### Tier 4 탈락 ({len(eliminated_t4)} method)")
    for _, r in eliminated_t4.iterrows():
        lines.append(f"- **{r['method']}** — {r['tier4_dataset_pass']}/{len(datasets)} dataset improve")
    lines.append("")

    # Winners
    winners = df[df["final_winner"]].sort_values("tier1_pass", ascending=False)
    lines.append(f"## Winners ({len(winners)} method)")
    lines.append("")
    if winners.empty:
        lines.append("> 4-tier 전부 통과한 method 없음. 기준 완화 또는 측정 보완 필요.")
    else:
        lines.append("| Method | T1 pass | T2 reason | T3 % | T4 ds | Best cell |")
        lines.append("|---|---|---|---|---|---|")
        for _, r in winners.iterrows():
            t3_pct = (f"{r['tier3_scale_invariance_pct']:.1%}"
                      if not pd.isna(r["tier3_scale_invariance_pct"]) else "N/A")
            lines.append(f"| {r['method']} | {r['tier1_pass']}/{r['tier1_total']} "
                         f"| {r['tier2_reason']} | {t3_pct} "
                         f"| {r['tier4_dataset_pass']}/{len(datasets)} "
                         f"| {r['best_cell']} |")
    lines.append("")

    # Per-dataset 추천
    lines.append("## Per-Dataset Best Method")
    lines.append("")
    lines.append("| Dataset | Best method (most negative Δ% at sel=0.10, any sf) |")
    lines.append("|---|---|")
    for ds in datasets:
        best_method = None
        best_dp = np.inf
        for _, r in df.iterrows():
            t1 = r["_tier1"]
            for cell in t1["cells"]:
                if cell["dataset"] != ds or cell["missing"]:
                    continue
                dp = cell.get("delta_pct", np.nan)
                if np.isnan(dp):
                    continue
                if dp < best_dp and cell["ci_excl_improve"]:
                    best_dp = dp
                    best_method = (r["method"], cell["sf"], dp)
        if best_method:
            m, sf, dp = best_method
            lines.append(f"| {ds} | **{m}** (sf{sf}, {dp:+.2f}%) |")
        else:
            lines.append(f"| {ds} | (no method passes CI) |")
    lines.append("")
    lines.append(f"_Generated by analyze_tier_elimination.py  ({TIER1_BOOTSTRAP_N} bootstrap iter)_")

    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[md] wrote {out_md}")


def write_plot(df: pd.DataFrame, out_png: Path) -> None:
    try:
        import matplotlib.pyplot as plt  # noqa: WPS433
    except ImportError:
        print("[plot] matplotlib 없음 — skip")
        return
    out_png.parent.mkdir(parents=True, exist_ok=True)

    df_plot = df.copy().sort_values("tier1_pct", ascending=True)
    methods = df_plot["method"].tolist()
    t1 = df_plot["tier1_pct"].fillna(0).to_numpy()
    t2 = df_plot["tier2_production_friendly"].astype(int).to_numpy()
    t3 = df_plot["tier3_scale_invariance_pct"].fillna(0).to_numpy()
    t4 = (df_plot["tier4_dataset_pass"] / max(1, len(DEFAULT_DATASETS))).to_numpy()

    fig, ax = plt.subplots(figsize=(12, max(6, len(methods) * 0.3)))
    y = np.arange(len(methods))
    width = 0.2
    ax.barh(y - 1.5 * width, t1, width, label="Tier 1 (CI pass %)")
    ax.barh(y - 0.5 * width, t2, width, label="Tier 2 (production-friendly)")
    ax.barh(y + 0.5 * width, t3, width, label="Tier 3 (scale-invariance)")
    ax.barh(y + 1.5 * width, t4, width, label="Tier 4 (dataset coverage)")
    ax.set_yticks(y)
    ax.set_yticklabels(methods)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Pass rate")
    ax.set_title("RQ3 30-Method Tier Elimination")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="x", alpha=0.3)

    # winner highlight
    for i, (_, r) in enumerate(df_plot.iterrows()):
        if r["final_winner"]:
            ax.text(1.02, i, "WINNER", color="#0a7d2c", fontsize=9, va="center")

    fig.tight_layout()
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[plot] wrote {out_png}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rsync-first", action="store_true",
                    help="server → local cache 동기화 (기본 capstone:/mnt/hdd0/...)")
    ap.add_argument("--datasets", nargs="+", default=list(DEFAULT_DATASETS))
    ap.add_argument("--sf", nargs="+", type=int, default=list(DEFAULT_SFS))
    ap.add_argument("--methods", nargs="+", default=list(ALL_METHODS),
                    help=f"기본 {len(ALL_METHODS)}개 method (전체)")
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--cache-dir", type=Path, default=LOCAL_CACHE,
                    help="parquet local cache. 기본 _internal/cache/rq1/")
    ap.add_argument("--also-results-dir", action="store_true", default=True,
                    help="experiments/results/rq3_agnostic/ 도 함께 검색")
    ap.add_argument("--plot", action="store_true",
                    help="experiments/figures/rq3_tier_elimination.png 생성")
    args = ap.parse_args()

    if args.rsync_first:
        rsync_from_server(args.cache_dir)

    cache_dirs: list[Path] = []
    if args.also_results_dir:
        cache_dirs.append(DEFAULT_OUT_DIR)
    cache_dirs.append(args.cache_dir)
    print(f"[discover] cache_dirs={[str(c) for c in cache_dirs]}")
    entries = discover_parquets(cache_dirs)
    print(f"[discover] {len(entries)} parquet entries")

    if not entries:
        print("[error] no parquet entries discovered. Either:")
        print("  - run with --rsync-first to fetch from server")
        print("  - or check that cache dirs exist and contain rq3_*.parquet")
        return 1

    # 어떤 (method, dataset, sf) 가 측정 가용한지 빠른 진단
    counts: dict[str, set] = {}
    for e in entries:
        counts.setdefault(e.method, set()).add((e.dataset, e.sf))
    print(f"[discover] methods present: {len(counts)}")
    for m in sorted(counts):
        print(f"  {m}: {len(counts[m])} cells")

    df = analyze_all(entries, tuple(args.methods), tuple(args.datasets), tuple(args.sf))

    out_csv = args.output_dir / "tier_elimination_table.csv"
    out_md = args.output_dir / "tier_elimination_summary.md"
    write_csv(df, out_csv)
    write_summary_md(df, out_md, tuple(args.datasets), tuple(args.sf))

    if args.plot:
        out_png = DEFAULT_FIG_DIR / "rq3_tier_elimination.png"
        write_plot(df, out_png)

    n_winners = int(df["final_winner"].sum())
    print(f"[done] winners={n_winners} / {len(df)} methods")
    return 0


if __name__ == "__main__":
    sys.exit(main())
