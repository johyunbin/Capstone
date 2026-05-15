#!/usr/bin/env python3
"""
aggregate_v12.py — Phase 1 file aggregation (4-stage chain 분석)

목적
----
local repo 의 모든 측정 결과 JSON file 영역을 단일 DataFrame 영역으로 통합.
박세은 framing 단순화 영역: "sample_selection_method" wording 영역 일관 적용.

Schema (~25 column)
-------------------
cell, dataset, sf, dim, type_label, mode, sample_selection_method, paradigm,
K, alpha, sel, ensemble_strategy, n_queries, trials,
qe_trim, qe_mean, qe_median,
size_median, size_min, size_max,
trial_qe_list, trial_size_list, eta_final,
stage_source, file_path

Sources
-------
- 기존 (691 file dry-run anchor): experiments/results/raw/Type{1,2,3,4a,4b}/
- 신규 chain (rsync 후 입수 영역): _internal/cache/rq3/server_sync/
  - results_v6_caseB_*, results_v7_extras_*, results_v6v7_fix_*,
    results_v10_full16_*, results_v9_sel_sweep_*

서버 → local rsync 영역은 본 script 외부 작업.

usage
-----
  python3 aggregate_v12.py --dry-run        # 691 기존 file 만
  python3 aggregate_v12.py                  # 전체 (rsync 완료 후)
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

# ============================================================
# 1. 상수 (analyze_paper_exact.py + EXPERIMENT_REGISTRY.md carry-over)
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[3]  # /Users/hyunbin/Capstone

# --- input root ---
LOCAL_RAW_ROOT = REPO_ROOT / "experiments" / "results" / "raw"
SERVER_SYNC_ROOT = REPO_ROOT / "_internal" / "cache" / "rq3" / "server_sync"

# --- output ---
OUT_DIR = REPO_ROOT / "_internal" / "cache" / "rq3"
OUT_PARQUET = OUT_DIR / "aggregated_v12.parquet"
OUT_CSV = OUT_DIR / "aggregated_v12.csv"

# --- cell metadata (EXPERIMENT_REGISTRY.md §1.1) ---
CELL_META = {
    "A1-DEEP":         {"dataset_canonical": "DEEP",         "dim": 96,  "sf_default": 100, "type": "Type3"},
    "A1-SIFT":         {"dataset_canonical": "SIFT",         "dim": 128, "sf_default": 100, "type": "Type3"},
    "A1-SSN":          {"dataset_canonical": "SimSearchNet++","dim": 256,"sf_default": 100, "type": "Type3"},
    "A2-Fig7":         {"dataset_canonical": "YFCC",         "dim": 192, "sf_default": 10,  "type": "Type4a"},
    "A2-Fig9":         {"dataset_canonical": "DEEP+WIKI",    "dim": 864, "sf_default": 10,  "type": "Type4b"},
    "A4-sel":          {"dataset_canonical": "DEEP",         "dim": 96,  "sf_default": 100, "type": "Type3"},
    "A5-scale-sf1":    {"dataset_canonical": "DEEP",         "dim": 96,  "sf_default": 1,   "type": "Type1"},
    "A5-scale-sf10":   {"dataset_canonical": "DEEP",         "dim": 96,  "sf_default": 10,  "type": "Type2"},
    "A5-scale-sf100":  {"dataset_canonical": "DEEP",         "dim": 96,  "sf_default": 100, "type": "Type3"},
    "A2-Fig8":         {"dataset_canonical": "DEEP+CC3M",    "dim": 1024,"sf_default": 10,  "type": "Type4a"},
}

TYPE_LABELS = {
    "Type1_small_single_sf1":  "Type 1",
    "Type2_medium_single_sf10":"Type 2",
    "Type3_large_single_sf100":"Type 3",
    "Type4a_large_multi_288d": "Type 4a",
    "Type4b_large_multi_864d": "Type 4b",
}

# --- PARADIGM_MAP (analyze_paper_exact.py:435-466 verbatim) ---
PARADIGM_MAP = {
    # P1 Cluster
    "minibatch": "P1", "gmm": "P1", "minibatch_partial": "P1",
    "birch": "P1", "agglomerative": "P1", "coreset": "P1",
    "dbscan": "P1", "kmeans_neyman": "P1",
    "hkbu_repsample": "P1", "banditucb1": "P1", "neurocard_lite": "P1",
    # P2 Spatial
    "hilbert": "P2", "hilbert_real": "P2", "skilling_hilbert": "P2",
    "zorder_morton": "P2", "idistance": "P2", "idistance_neyman": "P2",
    "faiss_ivf": "P2", "lpm1_proper": "P2", "epsilon_net": "P2",
    "kdtree": "P2", "kdpp": "P2", "lpm2": "P2",
    # P3 Streaming
    "chao_weighted": "P3", "reservoir": "P3",
    "thompson_sampling": "P3", "mfmc": "P3",
    "ams_count_sketch": "P3", "ccsketch": "P3",
    # P4 DimReduction
    "sparse_rp": "P4", "random_projection": "P4", "pca1d": "P4",
    "rsvd": "P4", "ica_fastica": "P4", "dense_rp": "P4",
    "neuram": "P4", "cca1d": "P4", "tucker": "P4",
    "vinecopula": "P4", "factor_join": "P4", "adaptive_bucket_probing": "P4",
    # P5 QMC/Hashing
    "lsh": "P5", "sobol": "P5", "halton": "P5", "hammersley": "P5",
    "lhs": "P5", "cum_sqrtf": "P5", "lavallee_hidiroglou": "P5",
    "lp_bound": "P5",
    # P6 Quantization
    "rabitq_strat": "P6", "mhist2": "P6", "wavelet_hist": "P6",
    "pq": "P6", "opq": "P6", "cocluster_nystrom": "P6",
    # P9 InfoTheoretic
    "hyperloglog": "P9",
    # P10 Density
    "kde_parzen": "P10",
}

# --- byte-identical duplicates (analyze_paper_exact.py §11) ---
ALIAS_GROUPS = {
    # P4 PCA1D quartet
    "pca1d_quartet":  {"primary": "pca1d",
                       "aliases": ["cca1d", "adaptive_bucket_probing"]},
    # 단일 쌍
    "epsilon_kdpp":   {"primary": "epsilon_net",
                       "aliases": ["kdpp"]},
    "ams_lsh":        {"primary": "ams_count_sketch",
                       "aliases": ["lsh"]},
    "kdtree_reservoir":{"primary":"kdtree",
                       "aliases": ["reservoir"]},  # kdtree = reservoir fallback
    "dense_random_rp":{"primary": "dense_rp",
                       "aliases": ["random_projection"]},
}
ALIAS_TO_PRIMARY = {
    alias: g["primary"]
    for g in ALIAS_GROUPS.values()
    for alias in g["aliases"]
}

# --- 폐기 method (CLAUDE.md 사용자 정책) ---
POLICY_DROP_METHODS = {
    # 정합성 위반 10
    "halton", "sobol", "lhs", "hammersley",
    "dense_rp", "random_projection",
    "dbscan", "ccsketch", "lsh", "ams_count_sketch",
    # Tier 2 미커버 6
    "dirichlet", "kernelpca", "neurocard_lite",
    "birch", "hdbscan", "agglomerative",
    # KDE 1
    "kde_parzen",
}

# ============================================================
# 2. parsing helpers
# ============================================================

def infer_stage_source(path: Path) -> str:
    """파일 경로에서 stage 영역 추론."""
    s = str(path).lower()
    if "server_sync" in s:
        if "results_v9_sel_sweep" in s:    return "v9_sel"
        if "results_v10_full16" in s:      return "v10"
        if "results_v6v7_fix" in s:        return "v6v7_fix"
        if "results_v7_extras" in s:       return "v7_extras"
        if "results_v6_caseb" in s:        return "v6_caseB"
        return "server_other"
    return "REPORT_v11"


def infer_type_label(path: Path) -> str:
    """파일 경로의 Type 폴더에서 type_label 추출."""
    for part in path.parts:
        if part in TYPE_LABELS:
            return TYPE_LABELS[part]
    return "?"


def parse_K(path: Path) -> Optional[int]:
    """K_granularity 폴더명 (K=10/K=20/K=30 또는 K10/K20/K30)에서 K 추출."""
    for part in path.parts:
        for tok in (f"K={k}" for k in (10, 20, 30)):
            if part == tok:
                return int(tok.split("=")[1])
        for tok in (f"K{k}" for k in (10, 20, 30)):
            if part == tok:
                return int(tok[1:])
    return None  # default K=20 (paper) — null = paper default


def parse_alpha(path: Path) -> Optional[float]:
    """alpha_sweep 폴더명 (alpha_0.3 / alpha_0.4 / alpha_0.5_default / alpha_0.6) 에서 alpha 추출."""
    for part in path.parts:
        if part.startswith("alpha_"):
            try:
                # alpha_0.5_default → 0.5
                tail = part.split("_", 1)[1]
                num_str = tail.split("_")[0]
                return float(num_str)
            except (IndexError, ValueError):
                continue
    return None


def parse_sel(path: Path, cell: str) -> Optional[float]:
    """selectivity 영역. 디렉토리 토큰 영역에서 sel_0.001 / sel_0.01 / sel_0.10 추출.
    A4-sel 영역 default 영역은 0.001 (Fig 13 anchor)."""
    for part in path.parts:
        if part.startswith("sel_") or part.startswith("sel="):
            try:
                num = part.split("_")[1] if part.startswith("sel_") else part.split("=")[1]
                return float(num)
            except (IndexError, ValueError):
                continue
    # default
    if cell == "A4-sel":
        return 0.001
    return 0.01  # paper default


def coerce_method(raw_method: str) -> str:
    """method 문자열 영역 정규화."""
    if not raw_method:
        return ""
    m = raw_method.strip().lower()
    return m


def lookup_paradigm(method: str) -> str:
    return PARADIGM_MAP.get(method, "Pother")


def alias_primary(method: str) -> str:
    """byte-identical 영역 alias 영역 → primary method."""
    return ALIAS_TO_PRIMARY.get(method, method)


# ============================================================
# 3. JSON → row 변환
# ============================================================

def parse_one(path: Path) -> Optional[dict]:
    """단일 JSON file 영역 → row dict. 실패 시 None."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  skip {path}: {e}", file=sys.stderr)
        return None

    # 기본 column
    cell = d.get("cell", "")
    mode = d.get("mode", "")
    method_raw = d.get("method", "")  # B1 영역 영역 method 영역 키 영역 X
    method = coerce_method(method_raw)

    # B1 영역 영역 method 영역 빈 영역 처리
    if mode == "B1" and not method:
        method = "_baseline_b1"

    # cell metadata (CELL_META)
    cm = CELL_META.get(cell, {})
    dataset_canonical = cm.get("dataset_canonical", d.get("dataset", ""))
    dim = cm.get("dim")

    # sf — JSON 영역 영역 우선, 없으면 cell default
    sf = d.get("sf", cm.get("sf_default"))

    # type / stage
    type_label = infer_type_label(path)
    stage_source = infer_stage_source(path)

    # axis sweep parsing
    K = parse_K(path)
    alpha = parse_alpha(path)
    sel = parse_sel(path, cell)

    # trial-level qe / size 분포
    trial_results = d.get("trial_results", []) or []
    qe_list = []
    size_list = []
    eta_finals = []
    for tr in trial_results:
        if isinstance(tr, dict):
            qv = tr.get("avg_q_error_finite")
            sv = tr.get("final_size")
            ev = tr.get("final_eta")
            if qv is not None: qe_list.append(qv)
            if sv is not None: size_list.append(sv)
            if ev is not None: eta_finals.append(ev)

    qe_series = pd.Series(qe_list, dtype="float64") if qe_list else pd.Series(dtype="float64")
    size_series = pd.Series(size_list, dtype="float64") if size_list else pd.Series(dtype="float64")

    qe_trim = d.get("avg_q_error_trimmed")
    qe_mean = float(qe_series.mean()) if len(qe_series) else None
    qe_median = float(qe_series.median()) if len(qe_series) else None

    size_median = float(size_series.median()) if len(size_series) else d.get("final_size_mean")
    size_min = float(size_series.min()) if len(size_series) else None
    size_max = float(size_series.max()) if len(size_series) else None

    eta_final = float(pd.Series(eta_finals).mean()) if eta_finals else d.get("final_eta_mean")

    row = {
        "cell": cell,
        "dataset": dataset_canonical,
        "sf": sf,
        "dim": dim,
        "type_label": type_label,
        "mode": mode,
        "sample_selection_method": alias_primary(method),
        "sample_selection_method_raw": method,
        "paradigm": lookup_paradigm(alias_primary(method)),
        "K": K,
        "alpha": alpha,
        "sel": sel,
        "ensemble_strategy": d.get("ensemble_strategy", "" if mode == "B1" else "simple_average"),
        "n_queries": d.get("n_queries"),
        "trials": d.get("trials"),
        "qe_trim": qe_trim,
        "qe_mean": qe_mean,
        "qe_median": qe_median,
        "size_median": size_median,
        "size_min": size_min,
        "size_max": size_max,
        "trial_qe_list": json.dumps(qe_list),
        "trial_size_list": json.dumps(size_list),
        "eta_final": eta_final,
        "stage_source": stage_source,
        "file_path": str(path.relative_to(REPO_ROOT)),
    }
    return row


# ============================================================
# 4. walker
# ============================================================

def walk_jsons(root: Path):
    """root 영역 하위 영역 모든 JSON file iterator."""
    if not root.exists():
        return
    for p in root.rglob("*.json"):
        # archive / underscore prefix 영역 제외
        skip = any(part.startswith("_archive") or part.startswith("_archived")
                   for part in p.parts)
        if skip:
            continue
        yield p


def aggregate(roots: list, label: str = "all") -> pd.DataFrame:
    rows = []
    n_total = 0
    n_skip = 0
    for root in roots:
        for p in walk_jsons(root):
            n_total += 1
            r = parse_one(p)
            if r is None:
                n_skip += 1
                continue
            rows.append(r)
    print(f"[{label}] scanned={n_total}, parsed={len(rows)}, skip={n_skip}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df


# ============================================================
# 5. dedup + sanity check
# ============================================================

def dedup_alias_rows(df: pd.DataFrame) -> pd.DataFrame:
    """byte-identical alias 영역 영역 raw method 영역 별도 영역 보존하되,
    paradigm rollup 시 primary method 만 카운트되도록 alias_flag 컬럼 추가."""
    if df.empty:
        return df
    df = df.copy()
    df["is_alias_dup"] = (
        df["sample_selection_method_raw"]
        .map(lambda m: m in ALIAS_TO_PRIMARY)
    )
    df["is_policy_drop"] = (
        df["sample_selection_method_raw"]
        .map(lambda m: m in POLICY_DROP_METHODS)
    )
    return df


def sanity_summary(df: pd.DataFrame) -> str:
    """parquet 영역 출력 후 1-page 영역 sanity check."""
    if df.empty:
        return "  empty DataFrame.\n"

    out = []
    out.append(f"  rows: {len(df)}")
    out.append(f"  cells (unique): {df['cell'].nunique()}")
    out.append(f"  modes: {sorted(df['mode'].dropna().unique().tolist())}")

    # mode별 row 수
    mode_cnt = df.groupby("mode").size().to_dict()
    out.append(f"  mode counts: {mode_cnt}")

    # cell별 row 수
    out.append("\n  cell × mode breakdown:")
    pivot = df.groupby(["cell", "mode"]).size().unstack(fill_value=0)
    out.append(pivot.to_string())

    # paradigm rollup
    out.append("\n  paradigm × mode breakdown:")
    p_pivot = df.groupby(["paradigm", "mode"]).size().unstack(fill_value=0)
    out.append(p_pivot.to_string())

    # qe_trim sanity (Fig 12 영역 anchor)
    fig12_cells = {"A1-DEEP","A1-SIFT","A1-SSN","A2-Fig7","A2-Fig9",
                   "A5-scale-sf1","A5-scale-sf10","A5-scale-sf100"}
    df_b1_fig12 = df[(df["mode"] == "B1") & (df["cell"].isin(fig12_cells))]
    if not df_b1_fig12.empty:
        mean_qe = df_b1_fig12["qe_trim"].mean()
        out.append(f"\n  B1 Fig 12 영역 qe_trim mean = {mean_qe:.4f} (paper 1.69 vs Δ={(mean_qe-1.69)/1.69*100:+.1f}%)")

    # alias / drop counts
    n_alias = int(df.get("is_alias_dup", pd.Series(dtype=bool)).sum())
    n_drop = int(df.get("is_policy_drop", pd.Series(dtype=bool)).sum())
    out.append(f"\n  alias rows: {n_alias} / policy_drop rows: {n_drop}")

    # stage distribution
    out.append("\n  stage_source distribution:")
    out.append(df["stage_source"].value_counts().to_string())

    return "\n".join(out)


# ============================================================
# 6. main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="기존 691 file 영역만 (server_sync X)")
    ap.add_argument("--out-suffix", default="",
                    help="output filename suffix (예: '_dryrun')")
    args = ap.parse_args()

    # input root
    roots = [LOCAL_RAW_ROOT]
    if not args.dry_run:
        if SERVER_SYNC_ROOT.exists():
            roots.append(SERVER_SYNC_ROOT)
        else:
            print(f"  warning: {SERVER_SYNC_ROOT} 영역 부재 — local raw 만 aggregate.")

    label = "dry-run" if args.dry_run else "full"
    df = aggregate(roots, label=label)
    df = dedup_alias_rows(df)

    # output
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = args.out_suffix or ("_dryrun" if args.dry_run else "")
    out_parquet = OUT_DIR / f"aggregated_v12{suffix}.parquet"
    out_csv = OUT_DIR / f"aggregated_v12{suffix}.csv"

    if not df.empty:
        df.to_parquet(out_parquet, index=False)
        df.to_csv(out_csv, index=False)
        print(f"\n  wrote {out_parquet}")
        print(f"  wrote {out_csv}")
    else:
        print("  empty — no output.")

    # sanity
    print("\n=== sanity summary ===")
    print(sanity_summary(df))


if __name__ == "__main__":
    main()
