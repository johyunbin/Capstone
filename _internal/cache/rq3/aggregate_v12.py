#!/usr/bin/env python3
"""
aggregate_v12.py — Phase 1 file aggregation (통합 집계 + 16 method 필터)

목적
----
local repo 의 모든 측정 결과 JSON 을 단일 DataFrame 으로 통합.
B1 = 대조군 (Bernoulli random + Adaptive Eq 1-6),
CaseB = 실험군 (16 method stratification ensemble + Adaptive).
CaseA 는 폐기 — 취급 안 함.

framing (박세은 5/15 20:49): sample selection 영역만 contribution,
paper §V-B Adaptive Eq 1-6 은 그대로.

Schema
------
cell, dataset, sf, dim, type_label, single_multi, mode,
method, sample_selection_method_raw, paradigm,
K, alpha, sel, ensemble_strategy, n_queries, trials,
qe_trim, qe_mean, qe_median,
final_size, size_median, size_min, size_max,
trial_qe_list, trial_size_list, eta_final,
content_hash, stage_source, file_path

Sources
-------
- 기존 (REPORT v11 base 691 file): experiments/results/raw/Type{1,2,3,4a,4b}/
- 신규 chain (server → local rsync): _internal/cache/rq3/server_sync/
  - v9_sel_sweep_0530/ (680) — single sel sweep, sel 0.001/0.10 (+ K10/K30)
  - concat_track_0537/ (357) — multi-vector concat, sel 0.001/0.01/0.10
  - v10_full16/ (129), v6_caseB/ (40), v6v7_fix/ (18), v7_extras/ (12),
    g2_k30_pca1d/ (2) — sel=0.01 신규 single
  - v8_full_3method/ (3) — A5-scale-sf1-SIFT 의 cum_sqrtf/faiss_ivf/gmm

서버 → local rsync 는 본 script 외부 작업.

usage
-----
  python3 aggregate_v12.py --dry-run        # 691 기존 file 만
  python3 aggregate_v12.py                  # 전체 (rsync 완료 후)
  python3 aggregate_v12.py --no-filter      # 16 method 필터 OFF (전체 method)
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

# ============================================================
# 1. 상수
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[3]  # /Users/hyunbin/Capstone

# --- input root ---
LOCAL_RAW_ROOT = REPO_ROOT / "experiments" / "results" / "raw"
SERVER_SYNC_ROOT = REPO_ROOT / "_internal" / "cache" / "rq3" / "server_sync"

# --- output ---
OUT_DIR = REPO_ROOT / "_internal" / "cache" / "rq3"

# --- 사용 16 method (사용자 명시 — framing 5/16) ---
USE_16_METHODS = [
    "minibatch_partial", "gmm", "faiss_ivf", "hilbert_real",
    "zorder_morton", "skilling_hilbert", "chao_weighted", "sparse_rp",
    "pca1d", "rsvd", "ica_fastica", "cum_sqrtf",
    "lavallee_hidiroglou", "rabitq_strat", "mhist2", "hyperloglog",
]
USE_16_SET = set(USE_16_METHODS)

# --- cell metadata (EXPERIMENT_REGISTRY.md §1.1 + 신규 chain cell) ---
# single_multi: "single" / "multi" (cross-table) / "concat" (concatenated multi-vector)
CELL_META = {
    # --- 기존 9 메인 cell (REPORT v11) ---
    "A1-DEEP":         {"dataset": "DEEP",          "dim": 96,   "sf": 100, "type": "Type3",  "single_multi": "single"},
    "A1-SIFT":         {"dataset": "SIFT",          "dim": 128,  "sf": 100, "type": "Type3",  "single_multi": "single"},
    "A1-SSN":          {"dataset": "SimSearchNet++","dim": 256,  "sf": 100, "type": "Type3",  "single_multi": "single"},
    "A2-Fig7":         {"dataset": "YFCC",          "dim": 192,  "sf": 10,  "type": "Type4a", "single_multi": "multi"},
    "A2-Fig9":         {"dataset": "DEEP+WIKI",     "dim": 864,  "sf": 10,  "type": "Type4b", "single_multi": "multi"},
    "A2-Fig8":         {"dataset": "DEEP+CC3M",     "dim": 1024, "sf": 10,  "type": "Type4a", "single_multi": "multi"},
    "A4-sel":          {"dataset": "DEEP",          "dim": 96,   "sf": 100, "type": "Type3",  "single_multi": "single"},
    "A5-scale-sf1":    {"dataset": "DEEP",          "dim": 96,   "sf": 1,   "type": "Type1",  "single_multi": "single"},
    "A5-scale-sf10":   {"dataset": "DEEP",          "dim": 96,   "sf": 10,  "type": "Type2",  "single_multi": "single"},
    "A5-scale-sf100":  {"dataset": "DEEP",          "dim": 96,   "sf": 100, "type": "Type3",  "single_multi": "single"},
    # --- 신규 chain single cell (v6/v7/v8/v9/v10/g2) ---
    "A5-scale-sf1-SIFT":  {"dataset": "SIFT", "dim": 128, "sf": 1,   "type": "Type1", "single_multi": "single"},
    "A5-scale-sf1-SSN":   {"dataset": "SimSearchNet++", "dim": 256, "sf": 1,  "type": "Type1", "single_multi": "single"},
    "A5-scale-sf10-SIFT": {"dataset": "SIFT", "dim": 128, "sf": 10,  "type": "Type2", "single_multi": "single"},
    "A5-scale-sf10-SSN":  {"dataset": "SimSearchNet++", "dim": 256, "sf": 10, "type": "Type2", "single_multi": "single"},
    "A6-WIKI-sf1":        {"dataset": "WIKI", "dim": 768, "sf": 1,   "type": "Type1", "single_multi": "single"},
    "A6-WIKI-sf10":       {"dataset": "WIKI", "dim": 768, "sf": 10,  "type": "Type2", "single_multi": "single"},
    "A7-YFCC-sf1":        {"dataset": "YFCC", "dim": 192, "sf": 1,   "type": "Type1", "single_multi": "single"},
    # --- 신규 chain multi (cross-table, non-concat) ---
    "A8-DEEP+SIFT-sf10":  {"dataset": "DEEP+SIFT", "dim": 224, "sf": 10, "type": "Type4a", "single_multi": "multi"},
    # --- 신규 chain concat (concatenated multi-vector) ---
    "A9-DEEP+SIFT-concat-sf1":   {"dataset": "DEEP+SIFT", "dim": 224, "sf": 1,   "type": "Type4a", "single_multi": "concat"},
    "A9-DEEP+SIFT-concat-sf10":  {"dataset": "DEEP+SIFT", "dim": 224, "sf": 10,  "type": "Type4a", "single_multi": "concat"},
    "A9-DEEP+SIFT-concat-sf100": {"dataset": "DEEP+SIFT", "dim": 224, "sf": 100, "type": "Type4a", "single_multi": "concat"},
    "A10-DEEP+WIKI-concat-sf1":  {"dataset": "DEEP+WIKI", "dim": 864, "sf": 1,   "type": "Type4b", "single_multi": "concat"},
    "A10-DEEP+WIKI-concat-sf10": {"dataset": "DEEP+WIKI", "dim": 864, "sf": 10,  "type": "Type4b", "single_multi": "concat"},
    "A11-DEEP+YFCC-concat-sf1":  {"dataset": "DEEP+YFCC", "dim": 288, "sf": 1,   "type": "Type4a", "single_multi": "concat"},
    "A11-DEEP+YFCC-concat-sf10": {"dataset": "DEEP+YFCC", "dim": 288, "sf": 10,  "type": "Type4a", "single_multi": "concat"},
}

TYPE_LABELS = {
    "Type1_small_single_sf1":  "Type 1",
    "Type2_medium_single_sf10":"Type 2",
    "Type3_large_single_sf100":"Type 3",
    "Type4a_large_multi_288d": "Type 4a",
    "Type4b_large_multi_864d": "Type 4b",
}

# --- PARADIGM_MAP (analyze_paper_exact.py verbatim) ---
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

# ============================================================
# 2. parsing helpers
# ============================================================

# stage 별 selectivity default (JSON 에 selectivity 필드 없는 신규 sel=0.01 run)
STAGE_SEL_DEFAULT = {
    "v10": 0.01, "v6_caseB": 0.01, "v6v7_fix": 0.01,
    "v7_extras": 0.01, "v8_3method": 0.01, "g2_k30": 0.01,
}


def infer_stage_source(path: Path) -> str:
    """파일 경로에서 stage 추론."""
    s = str(path).lower()
    if "server_sync" in s:
        if "v9_sel_sweep" in s:    return "v9_sel"
        if "concat_track" in s:    return "concat"
        if "v10_full16" in s:      return "v10"
        if "v6v7_fix" in s:        return "v6v7_fix"
        if "v7_extras" in s:       return "v7_extras"
        if "v6_caseb" in s:        return "v6_caseB"
        if "v8_full_3method" in s: return "v8_3method"
        if "g2_k30_pca1d" in s:    return "g2_k30"
        return "server_other"
    return "REPORT_v11"


def infer_type_label(path: Path, cell: str) -> str:
    """파일 경로의 Type 폴더 또는 CELL_META 에서 type_label 추출."""
    for part in path.parts:
        if part in TYPE_LABELS:
            return TYPE_LABELS[part]
    cm = CELL_META.get(cell, {})
    t = cm.get("type")
    if t:
        return t.replace("Type", "Type ")
    return "?"


def parse_K(path: Path) -> Optional[int]:
    """K_granularity 추출.

    지원 패턴:
    - 정확 part: K=10/K=20/K=30, K10/K20/K30
    - compound suffix: A1-SIFT_K10, A1-SSN_K30 (server_sync v6/v10 sub-dir)
    - compound infix: A1-SIFT_K10_sel0.001, A1-SSN_K30_sel0.10 (v9_sel_sweep)
    - g2_k30_pca1d 디렉토리 → K=30
    None = paper default K=20.
    """
    for part in path.parts:
        # g2_k30_pca1d 특수 디렉토리
        if part == "g2_k30_pca1d":
            return 30
        # 정확 매치 — K=20 은 paper default 이므로 None 반환 (paper_main 과 동일 bucket)
        for k in (10, 30):
            if part == f"K={k}" or part == f"K{k}":
                return k
        if part == "K=20" or part == "K20":
            return None  # paper default — K_granularity/K=20 ≡ paper_main
        # compound suffix (_K10) 또는 infix (_K10_sel0.001)
        for k in (10, 30):
            if part.endswith(f"_K{k}") or f"_K{k}_" in part:
                return k
        if part.endswith("_K20") or "_K20_" in part:
            return None
    return None  # paper default K=20


def parse_alpha(path: Path) -> Optional[float]:
    """alpha_sweep 폴더명 (alpha_0.3 / alpha_0.5_default 등)에서 alpha 추출."""
    for part in path.parts:
        if part.startswith("alpha_"):
            try:
                tail = part.split("_", 1)[1]
                num_str = tail.split("_")[0]
                return float(num_str)
            except (IndexError, ValueError):
                continue
    return None


def parse_sel(path: Path, cell: str, json_sel, stage: str) -> Optional[float]:
    """selectivity 결정 — 우선순위:
    1. JSON selectivity 필드 (v9_sel_sweep, concat_track 은 JSON 에 존재)
    2. 디렉토리 토큰 sel0.001 / sel_0.01 / sel=0.10
    3. stage 별 default (신규 sel=0.01 run 은 JSON 에 selectivity 없음)
    4. A4-sel default 0.001 (Fig 13 anchor)
    5. paper default 0.01
    """
    # 1. JSON 필드
    if json_sel is not None:
        try:
            return float(json_sel)
        except (TypeError, ValueError):
            pass
    # 2. 디렉토리 토큰
    for part in path.parts:
        # sel0.001 / sel0.10 (concat_track, v9 sub-dir suffix)
        if "sel" in part.lower():
            low = part.lower()
            for tok in ("sel0.001", "sel0.01", "sel0.10", "sel0.1"):
                if tok in low:
                    return float(tok.replace("sel", ""))
            # sel_0.01 / sel=0.01 형태
            if low.startswith("sel_") or low.startswith("sel="):
                try:
                    num = part.split("_")[1] if "_" in part else part.split("=")[1]
                    return float(num)
                except (IndexError, ValueError):
                    pass
    # 3. stage default
    if stage in STAGE_SEL_DEFAULT:
        return STAGE_SEL_DEFAULT[stage]
    # 4. A4-sel
    if cell == "A4-sel":
        return 0.001
    # 5. paper default
    return 0.01


def coerce_method(raw_method: str) -> str:
    if not raw_method:
        return ""
    return raw_method.strip().lower()


def lookup_paradigm(method: str) -> str:
    return PARADIGM_MAP.get(method, "Pother")


# ============================================================
# 3. JSON → row 변환
# ============================================================

def parse_one(path: Path) -> Optional[dict]:
    """단일 JSON file → row dict. 실패 시 None."""
    try:
        raw_bytes = path.read_bytes()
        d = json.loads(raw_bytes)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  skip {path}: {e}", file=sys.stderr)
        return None

    cell = d.get("cell", "")
    mode = d.get("mode", "")
    method = coerce_method(d.get("method", ""))

    # B1 은 method 키 없음
    if mode == "B1" and not method:
        method = "_baseline_b1"

    # cell metadata
    cm = CELL_META.get(cell, {})
    dataset = cm.get("dataset", d.get("dataset", ""))
    dim = cm.get("dim", d.get("dim"))
    single_multi = cm.get("single_multi", "?")

    # sf — JSON 우선, 없으면 cell default
    sf = d.get("sf", cm.get("sf"))

    # type / stage
    stage_source = infer_stage_source(path)
    type_label = infer_type_label(path, cell)

    # axis sweep
    K = parse_K(path)
    alpha = parse_alpha(path)
    sel = parse_sel(path, cell, d.get("selectivity"), stage_source)

    # trial-level qe / size
    trial_results = d.get("trial_results", []) or []
    qe_list, size_list, eta_finals = [], [], []
    for tr in trial_results:
        if isinstance(tr, dict):
            qv = tr.get("avg_q_error_finite")
            sv = tr.get("final_size")
            ev = tr.get("final_eta")
            if qv is not None:
                qe_list.append(qv)
            if sv is not None:
                size_list.append(sv)
            if ev is not None:
                eta_finals.append(ev)

    qe_series = pd.Series(qe_list, dtype="float64") if qe_list else pd.Series(dtype="float64")
    size_series = pd.Series(size_list, dtype="float64") if size_list else pd.Series(dtype="float64")

    qe_trim = d.get("avg_q_error_trimmed")
    qe_mean = float(qe_series.mean()) if len(qe_series) else None
    qe_median = float(qe_series.median()) if len(qe_series) else None

    final_size = d.get("final_size_mean")
    size_median = float(size_series.median()) if len(size_series) else final_size
    size_min = float(size_series.min()) if len(size_series) else None
    size_max = float(size_series.max()) if len(size_series) else None
    if final_size is None and len(size_series):
        final_size = float(size_series.mean())

    eta_final = float(pd.Series(eta_finals).mean()) if eta_finals else d.get("final_eta_mean")

    # content hash — byte-identical dedup 용 (trial qe + size + cell + mode + method)
    hash_payload = json.dumps({
        "cell": cell, "mode": mode, "method": method,
        "qe": qe_list, "size": size_list,
    }, sort_keys=True).encode("utf-8")
    content_hash = hashlib.md5(hash_payload).hexdigest()

    row = {
        "cell": cell,
        "dataset": dataset,
        "sf": sf,
        "dim": dim,
        "type_label": type_label,
        "single_multi": single_multi,
        "mode": mode,
        "method": method,
        "sample_selection_method_raw": method,
        "paradigm": lookup_paradigm(method),
        "K": K,
        "alpha": alpha,
        "sel": sel,
        "ensemble_strategy": d.get("ensemble_strategy", "" if mode == "B1" else "simple_average"),
        "n_queries": d.get("n_queries"),
        "trials": d.get("trials"),
        "qe_trim": qe_trim,
        "qe_mean": qe_mean,
        "qe_median": qe_median,
        "final_size": final_size,
        "size_median": size_median,
        "size_min": size_min,
        "size_max": size_max,
        "trial_qe_list": json.dumps(qe_list),
        "trial_size_list": json.dumps(size_list),
        "eta_final": eta_final,
        "content_hash": content_hash,
        "stage_source": stage_source,
        "file_path": str(path.relative_to(REPO_ROOT)),
    }
    return row


# ============================================================
# 4. walker
# ============================================================

def walk_jsons(root: Path):
    """root 하위 모든 JSON file iterator (archive / underscore prefix 제외)."""
    if not root.exists():
        return
    for p in root.rglob("*.json"):
        skip = any(part.startswith("_archive") or part.startswith("_archived")
                   for part in p.parts)
        if skip:
            continue
        yield p


def aggregate(roots: list, label: str = "all", filter_16: bool = True) -> pd.DataFrame:
    rows = []
    n_total = n_skip = n_filtered = 0
    for root in roots:
        for p in walk_jsons(root):
            n_total += 1
            r = parse_one(p)
            if r is None:
                n_skip += 1
                continue
            # 16 method 필터: B1 은 항상 유지, CaseB 는 16 method 만
            if filter_16 and r["mode"] == "CaseB" and r["method"] not in USE_16_SET:
                n_filtered += 1
                continue
            # CaseA 는 framing 상 폐기 — 제외
            if r["mode"] == "CaseA":
                n_filtered += 1
                continue
            rows.append(r)
    print(f"[{label}] scanned={n_total}, parsed={len(rows)}, "
          f"skip(parse-fail)={n_skip}, filtered(16M/CaseA)={n_filtered}")
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


# ============================================================
# 5. dedup + sanity check
# ============================================================

# stage 별 측정 신뢰 precedence (작을수록 우선 보존)
# - K10/K30 16-method 신규 chain (v10/v6v7_fix/v6_caseB/g2) 가 raw K_granularity 5/12 partial run 보다 우선
# - paper default (K20/Knan) 은 REPORT_v11 paper_main 정본 우선
STAGE_DEDUP_RANK = {
    "REPORT_v11": 0,   # paper_main 정본 (K20 default + sel0.01)
    "v9_sel":     1,   # sel sweep
    "concat":     1,   # concat track
    "v10":        2,   # 16-method full chain
    "v6v7_fix":   2,   # v6/v7 fix re-run
    "v6_caseB":   2,
    "v7_extras":  2,
    "v8_3method": 2,
    "g2_k30":     2,
    "server_other": 5,
}


def _k_norm(k):
    """K normalize — null = paper default 20."""
    return 20 if (k is None or pd.isna(k)) else int(k)


def dedup_byte_identical(df: pd.DataFrame) -> pd.DataFrame:
    """2단계 dedup.

    1) byte-identical content_hash 중복 제거 (예: raw K=20 dir ≡ paper_main/CaseB).
    2) semantic 중복 제거 — 같은 (cell, sel, K_norm, method, mode) 의 서로 다른
       측정 run (예: raw K_granularity 5/12 partial vs v10/v6v7_fix 신규 16-method chain).
       STAGE_DEDUP_RANK 기준 우선 stage 보존.
    """
    if df.empty:
        return df
    df = df.copy()
    n_before = len(df)

    # --- 1) byte-identical (content_hash) ---
    df["_rank"] = df["stage_source"].map(lambda s: STAGE_DEDUP_RANK.get(s, 9))
    df = df.sort_values(["content_hash", "_rank", "file_path"])
    df["is_byte_dup"] = df.duplicated(subset=["content_hash"], keep="first")
    n_byte = int(df["is_byte_dup"].sum())
    df = df[~df["is_byte_dup"]].copy()

    # --- 2) semantic (cell, sel, K_norm, method, mode) ---
    df["_k_norm"] = df["K"].map(_k_norm)
    df = df.sort_values(["cell", "sel", "_k_norm", "method", "mode",
                         "_rank", "file_path"])
    df["is_semantic_dup"] = df.duplicated(
        subset=["cell", "sel", "_k_norm", "method", "mode"], keep="first")
    n_sem = int(df["is_semantic_dup"].sum())
    df_dedup = (df[~df["is_semantic_dup"]]
                .drop(columns=["_rank", "_k_norm", "is_byte_dup", "is_semantic_dup"])
                .reset_index(drop=True))
    print(f"  dedup: {n_before} → {len(df_dedup)} "
          f"(byte-identical {n_byte}건 + semantic-supersede {n_sem}건 제거)")
    return df_dedup


def sanity_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "  empty DataFrame.\n"
    out = []
    out.append(f"  rows: {len(df)}")
    out.append(f"  cells (unique): {df['cell'].nunique()}")
    out.append(f"  modes: {sorted(df['mode'].dropna().unique().tolist())}")
    out.append(f"  mode counts: {df.groupby('mode').size().to_dict()}")
    out.append(f"  single_multi counts: {df.groupby('single_multi').size().to_dict()}")
    out.append(f"  sel values: {sorted(df['sel'].dropna().unique().tolist())}")
    out.append(f"  K values: {sorted(df['K'].dropna().unique().tolist())} (null=K20 default)")

    out.append("\n  cell × mode breakdown:")
    pivot = df.groupby(["cell", "mode"]).size().unstack(fill_value=0)
    out.append(pivot.to_string())

    out.append("\n  stage_source distribution:")
    out.append(df["stage_source"].value_counts().to_string())

    # Fig 12 anchor
    fig12_cells = {"A1-DEEP", "A1-SIFT", "A1-SSN", "A2-Fig7", "A2-Fig9",
                   "A5-scale-sf1", "A5-scale-sf10", "A5-scale-sf100"}
    df_b1 = df[(df["mode"] == "B1") & (df["cell"].isin(fig12_cells))
               & (df["sel"] == 0.01) & (df["K"].isna())]
    if not df_b1.empty:
        mean_qe = df_b1["qe_trim"].mean()
        out.append(f"\n  B1 Fig 12 (sel=0.01, K=default) qe_trim mean = {mean_qe:.4f} "
                   f"(n={len(df_b1)}, paper 1.69 vs Δ={(mean_qe-1.69)/1.69*100:+.1f}%)")
    return "\n".join(out)


# ============================================================
# 6. main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="기존 691 file 만 (server_sync X)")
    ap.add_argument("--no-filter", action="store_true",
                    help="16 method 필터 OFF")
    ap.add_argument("--out-suffix", default="",
                    help="output filename suffix")
    args = ap.parse_args()

    roots = [LOCAL_RAW_ROOT]
    if not args.dry_run:
        if SERVER_SYNC_ROOT.exists():
            roots.append(SERVER_SYNC_ROOT)
        else:
            print(f"  warning: {SERVER_SYNC_ROOT} 부재 — local raw 만 aggregate.")

    label = "dry-run" if args.dry_run else "full"
    filter_16 = not args.no_filter
    df = aggregate(roots, label=label, filter_16=filter_16)
    df = dedup_byte_identical(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.out_suffix:
        suffix = args.out_suffix
    elif args.dry_run:
        suffix = "_dryrun"
    else:
        suffix = "_full"
    out_parquet = OUT_DIR / f"aggregated_v12{suffix}.parquet"
    out_csv = OUT_DIR / f"aggregated_v12{suffix}.csv"

    if not df.empty:
        df.to_parquet(out_parquet, index=False)
        df.to_csv(out_csv, index=False)
        print(f"\n  wrote {out_parquet}")
        print(f"  wrote {out_csv}")
    else:
        print("  empty — no output.")

    print("\n=== sanity summary ===")
    print(sanity_summary(df))


if __name__ == "__main__":
    main()
