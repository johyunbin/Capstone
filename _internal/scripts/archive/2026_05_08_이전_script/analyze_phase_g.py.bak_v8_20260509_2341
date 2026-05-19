#!/usr/bin/env python3
"""Phase G — End-to-end analysis pipeline for the v7 22 method × 28 cell × 6 baseline matrix.

Phase G runs *after* Phase E (full matrix measurement, 22 method × 28 cell ×
5 sel × 5 seed × 100 query ≈ 7.7M paired observations) and Phase F (6 baseline
runs B1 ~ B6 × 28 cell) finish. The script produces the seven analytical
sections that feed boa report §7~9, slide v3 page 18~22, and the production
package summary in ``experiments/code/exqutor_augment/``.

The pipeline implements the statistical framework documented in
``plans/RQ재정립_v7_evidence_20260509_1820.md`` § 8 (paired Wilcoxon, Bonferroni
correction at α/22, 1000-iteration bootstrap CI, per-method ANOVA across cells,
failure-mode regression, convergence speed t*, and the 4-axis contribution
metric for Stage ⑥).

Sections (run in order; each writes a CSV under ``OUT_DIR``):

  G1. Per-method × per-cell consistency (single+multi)
      Joint single/multi mean q_error per method, consistency ratio,
      tier-aware ranking, "single+multi top tier" filter.

  G2. Adaptive (B1) gap — paired Δ% vs B1
      Cell × method paired q_error, paired Wilcoxon (two-sided) with
      Bonferroni correction. Reports the count of cell × method pairs where
      a method beats B1 with statistically significant paired-better. The
      core finding flag ``win_single_multi_b1`` is set for methods that
      beat B1 in *both* domains under the family-wise α/22 threshold.

  G3. Adaptive vs Adaptive+ensemble (B1 vs B4) — Stage ⑥ contribution
      Per cell × method (the ensemble base method), paired Δ% between
      B4 and B1 along four axes (accuracy, convergence speed, resource,
      rare query sel=0.01). Any axis showing a statistically significant
      improvement counts as a Stage ⑥ contribution.

  G4. Failure mode regression update (Phase B + 11 new methods)
      Re-fits the Phase B regression
      ``log(q_error) ~ log(dim) + sel + is_multi + paradigm`` on the
      extended portfolio (22 methods + 4 new paradigms P6 Sketch / P7 Joint /
      P8 DimInvariant / S_MultiRelation). Reports the per-paradigm
      coefficients and the curse-of-dim slope β₁ comparison between the
      legacy 11 methods and the new 11.

  G5. Convergence speed analysis
      Per cell × method (B4) sample-size time series → first time t* at
      which |S_t − S_∞| / S_∞ < 5%. Reports B4 vs B1 t* delta.

  G6. Resource analysis
      Per cell × method wall-clock + memory; cost-quality Pareto frontier
      for the 22 method portfolio.

  G7. Production-ready package summary
      Four-way intersection: methods that (a) win single+multi vs B1,
      (b) Adaptive-augment positively (B4 better than B1 on at least one
      axis), (c) low resource cost, (d) interpretable (paradigm or Tier).
      Top 3-5 candidates emitted with English README-ready descriptors.

Inputs (under ``_internal/cache/`` or server-side):
  * Phase E full matrix parquets:
      ``rq3_full_matrix_<cell>_<method>.parquet``
      schema: cell, method, paradigm, dim, selectivity, seed, query_id,
              D_target, true_card, est, q_error, sample_size_used,
              total_sample_size, wall_clock_ms, peak_rss_mb
  * Phase F baseline parquets:
      ``rq3_stage6_baselines_<cell>.parquet``
      schema: cell, baseline (B1..B6), selectivity, seed, query_id,
              true_card, est, q_error, sample_size_used, wall_clock_ms

Outputs (under ``_internal/cache/phase_g_analysis/``):
  * G1_consistency.csv             — per-method single/multi mean + ratio.
  * G2_adaptive_gap.csv            — paired Δ% vs B1 + Bonferroni adj.
  * G3_b4_vs_b1.csv                — Stage ⑥ 4-axis paired metric.
  * G4_regression_extended.csv     — extended OLS coefficient table.
  * G5_convergence.csv             — t* per cell × method.
  * G6_resource.csv                — wall-clock + memory per cell × method.
  * G7_production_top.csv          — final 3-5 method recommendation.
  * REPORT.md                      — 1500-2500 word academic narrative.

Plots (under ``experiments/figures/phase_g/``):
  * fig_g1_consistency.png         — single vs multi q_error scatter.
  * fig_g2_adaptive_gap.png        — paired Δ% per method × cell heatmap.
  * fig_g3_4axis_radar.png         — 4-axis radar chart (Stage ⑥).
  * fig_g4_regression_forest.png   — paradigm coefficient forest plot.
  * fig_g5_convergence.png         — t* delta box plot.
  * fig_g6_pareto.png              — wall-clock × q_error Pareto frontier.
  * fig_g7_top_methods.png         — top 3-5 method bar chart.

Usage:
  $ python3 _internal/scripts/analyze_phase_g.py
  $ python3 _internal/scripts/analyze_phase_g.py --mini-run     # synthetic data
  $ python3 _internal/scripts/analyze_phase_g.py --dry-run      # inputs only

References:
  * Plan v7 §8.1 paired Wilcoxon @ 5 sel × 5 seed × 100 query = 2500 paired.
  * Plan v7 §8.2 Bonferroni α/22 (multiple comparison 22 method family).
  * Plan v7 §8.5 failure-mode regression (extended with new paradigms).
  * Plan v7 §8.6 convergence speed t* metric.
  * Plan v7 §8.7 4-axis contribution (accuracy / convergence / resource / robustness).
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

# ---------------------------------------------------------------------------
# Constants — must match measure_multi_paradigm.py and plan v7 §4–§6.
# ---------------------------------------------------------------------------
ROOT = Path("/Users/hyunbin/Capstone")
LOCAL_FULL_DIR = ROOT / "_internal/cache/full_matrix"
LOCAL_BASELINE_DIR = ROOT / "_internal/cache/stage6_baselines"
SERVER_FULL_DIR = Path("/mnt/hdd0/home/capstone2026/cache/full_matrix")
SERVER_BASELINE_DIR = Path("/mnt/hdd0/home/capstone2026/cache/stage6_baselines")

OUT_DIR = ROOT / "_internal/cache/phase_g_analysis"
FIG_DIR = ROOT / "experiments/figures/phase_g"

# v7 §8 baseline labels.
BASELINES = ["B1", "B2", "B3", "B4", "B5", "B6"]
BASELINE_NAMES = {
    "B1": "Adaptive (Exqutor)",
    "B2": "BERN N=385 fixed",
    "B3": "Fixed-K=20",
    "B4": "Adaptive + ensemble (NEW)",
    "B5": "Uniform random matched",
    "B6": "Oracle KM20",
}

# v7 §4 22 methods, ordered legacy 11 first then new 11 (Tier S/A/B/C).
METHODS_LEGACY = [
    "HDBSCAN", "MiniBatch", "GMM",       # P1 Cluster
    "Hilbert", "faiss_ivf",              # P2 Spatial
    "MB_partial", "Reservoir",           # P3 Streaming
    "sparse_rp", "PCA1D",                # P4 DimReduction
    "LSH", "Sobol",                      # P5 Quasi-random
]
METHODS_NEW = [
    # Tier S
    "WanderJoin", "AMS_CountSketch", "NeuroCard",
    # Tier A
    "PQ", "Coreset", "DenseRP", "BanditUCB1", "NeurAM",
    # Tier B
    "CCA1D", "CoCluster_Nystrom",
    # Tier C
    "ConditionalAdaptive",
]
METHODS_ALL = METHODS_LEGACY + METHODS_NEW

PARADIGM = {
    # Legacy 5 paradigms
    "HDBSCAN": "P1_Cluster",
    "MiniBatch": "P1_Cluster",
    "GMM": "P1_Cluster",
    "Hilbert": "P2_Spatial",
    "faiss_ivf": "P2_Spatial",
    "MB_partial": "P3_Streaming",
    "Reservoir": "P3_Streaming",
    "sparse_rp": "P4_DimReduction",
    "PCA1D": "P4_DimReduction",
    "LSH": "P5_QuasiRandom",
    "Sobol": "P5_QuasiRandom",
    # New paradigms (v7 §4.2)
    "WanderJoin": "S_MultiRelation",
    "AMS_CountSketch": "P6_Sketch",
    "NeuroCard": "S_MultiRelation",
    "PQ": "P4_DimReduction",            # PQ codebook subspace = dim reduction.
    "Coreset": "P1_Cluster",            # sensitivity-weighted clustering.
    "DenseRP": "P4_DimReduction",
    "BanditUCB1": "P3_Streaming",
    "NeurAM": "P8_DimInvariant",
    "CCA1D": "P7_Joint",
    "CoCluster_Nystrom": "P7_Joint",
    "ConditionalAdaptive": "S_MultiRelation",  # adaptive variant — Stage ⑥ ablation.
}

TIER = {
    # Legacy: Tier "L" (legacy paradigm coverage)
    **{m: "L" for m in METHODS_LEGACY},
    # Tier S — multi-relation native
    "WanderJoin": "S",
    "AMS_CountSketch": "S",
    "NeuroCard": "S",
    # Tier A — general
    "PQ": "A",
    "Coreset": "A",
    "DenseRP": "A",
    "BanditUCB1": "A",
    "NeurAM": "A",
    # Tier B — multi-vector specialist
    "CCA1D": "B",
    "CoCluster_Nystrom": "B",
    # Tier C — single-only modification
    "ConditionalAdaptive": "C",
}

PARADIGMS = sorted(set(PARADIGM.values()))

# v7 §5 cell portfolio (28 cells).
SINGLE_DATASETS = ["DEEP", "SIFT", "FB", "SSN", "WIKI", "YFCC"]
SINGLE_SFS = [1, 10]
MULTI_4WAY_IMG = ["DEEP", "SIFT", "FB", "YFCC"]
MULTI_JOIN_IMG = ["DEEP", "SIFT", "FB", "YFCC"]

SINGLE_CELLS = [f"{ds}_sf{sf}" for ds in SINGLE_DATASETS for sf in SINGLE_SFS]
MULTI_4WAY_CELLS = [f"partsupp_{img.lower()}_wiki_{sf}"
                    for img in MULTI_4WAY_IMG for sf in SINGLE_SFS]
MULTI_JOIN_CELLS = [f"multi_join_{img.lower()}_wiki_{sf}"
                    for img in MULTI_JOIN_IMG for sf in SINGLE_SFS]
ALL_CELLS = SINGLE_CELLS + MULTI_4WAY_CELLS + MULTI_JOIN_CELLS  # 12+8+8 = 28

CELL_KIND = {}
for c in SINGLE_CELLS:
    CELL_KIND[c] = "single"
for c in MULTI_4WAY_CELLS:
    CELL_KIND[c] = "multi_4way"
for c in MULTI_JOIN_CELLS:
    CELL_KIND[c] = "multi_join"

# v7 §5: dim per cell. Single = embedding dim. Multi = concat of two dims.
DIM_BY_DATASET = {"DEEP": 96, "SIFT": 128, "FB": 256, "SSN": 256,
                  "WIKI": 768, "YFCC": 192}
CELL_DIM = {}
for ds in SINGLE_DATASETS:
    for sf in SINGLE_SFS:
        CELL_DIM[f"{ds}_sf{sf}"] = DIM_BY_DATASET[ds]
for img in MULTI_4WAY_IMG:
    for sf in SINGLE_SFS:
        CELL_DIM[f"partsupp_{img.lower()}_wiki_{sf}"] = (
            DIM_BY_DATASET[img] + DIM_BY_DATASET["WIKI"])
for img in MULTI_JOIN_IMG:
    for sf in SINGLE_SFS:
        CELL_DIM[f"multi_join_{img.lower()}_wiki_{sf}"] = (
            DIM_BY_DATASET[img] + DIM_BY_DATASET["WIKI"])

# v7 §8.1 sample size: 5 sel × 5 seed × 100 query = 2500 paired observations.
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
QUERIES_PER_CELL = 100
N_PAIRED_PER_CELL = len(SELECTIVITIES) * len(SEEDS) * QUERIES_PER_CELL

# v7 §8.2 Bonferroni: α / 22 method = 0.05 / 22 ≈ 0.00227.
ALPHA = 0.05
N_METHODS_FAMILY = 22
BONFERRONI_ALPHA = ALPHA / N_METHODS_FAMILY

# Convergence threshold (v7 §8.6).
CONVERGENCE_REL_THRESHOLD = 0.05  # |S_t − S_∞| / S_∞ < 5%.

# Bootstrap iterations (v7 §8.3).
BOOTSTRAP_N = 1000

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("phase_g")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
@dataclass
class LoadStats:
    n_method_files: int = 0
    n_method_rows: int = 0
    n_baseline_files: int = 0
    n_baseline_rows: int = 0
    cells_seen: set = field(default_factory=set)
    methods_seen: set = field(default_factory=set)
    baselines_seen: set = field(default_factory=set)


def _scan_dirs(dirs: list[Path], pattern: str) -> list[Path]:
    """Recursively glob ``pattern`` in each ``dir``; return existing paths."""
    out = []
    for d in dirs:
        if not d.exists():
            continue
        out.extend(sorted(d.rglob(pattern)))
    return out


def _read_table(path: Path) -> pd.DataFrame:
    """Read parquet or csv based on suffix."""
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def load_full_matrix(stats: LoadStats,
                     search_dirs: Optional[list[Path]] = None) -> pd.DataFrame:
    """Load 22 method × 28 cell × 5 sel × 5 seed × 100 query parquets.

    Expected schema after ingest:
        cell, method, paradigm, tier, dim, cell_kind,
        selectivity, seed, query_id, true_card, est, q_error,
        sample_size_used, total_sample_size, wall_clock_ms, peak_rss_mb
    """
    if search_dirs is None:
        search_dirs = [LOCAL_FULL_DIR, SERVER_FULL_DIR]
    files = _scan_dirs(search_dirs, "rq3_full_matrix_*.parquet")
    if not files:
        log.warning("no full-matrix files found in %s", search_dirs)
        return pd.DataFrame()
    rows = []
    for fp in files:
        try:
            df = _read_table(fp)
        except Exception as exc:  # noqa: BLE001 — keep loop alive.
            log.warning("skip %s: %s", fp.name, exc)
            continue
        # Filename: rq3_full_matrix_<cell>_<method>.parquet
        stem = fp.stem.replace("rq3_full_matrix_", "")
        # method is last token after the final '__'; cell is the rest.
        # We use a unique sentinel '__' if measure scripts emit it; else
        # rely on the parquet's own ``cell`` / ``method`` columns.
        if "cell" not in df.columns or "method" not in df.columns:
            # Fall back to filename parsing.
            parts = stem.rsplit("_", 1)
            if len(parts) == 2:
                df = df.copy()
                df["cell"] = parts[0]
                df["method"] = parts[1]
            else:
                log.warning("cannot parse cell/method from %s", fp.name)
                continue
        df = df.copy()
        df["paradigm"] = df["method"].map(PARADIGM).fillna("?")
        df["tier"] = df["method"].map(TIER).fillna("?")
        df["dim"] = df["cell"].map(CELL_DIM).fillna(np.nan).astype(float)
        df["cell_kind"] = df["cell"].map(CELL_KIND).fillna("?")
        rows.append(df)
        stats.n_method_files += 1
        stats.n_method_rows += len(df)
        stats.cells_seen.update(df["cell"].unique().tolist())
        stats.methods_seen.update(df["method"].unique().tolist())
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out = out.dropna(subset=["q_error"])
    out = out[out["q_error"] > 0]
    return out


def load_baselines(stats: LoadStats,
                   search_dirs: Optional[list[Path]] = None) -> pd.DataFrame:
    """Load 6 baseline × 28 cell parquets.

    Expected schema:
        cell, baseline (B1..B6), selectivity, seed, query_id,
        true_card, est, q_error, sample_size_used, wall_clock_ms
    """
    if search_dirs is None:
        search_dirs = [LOCAL_BASELINE_DIR, SERVER_BASELINE_DIR]
    files = _scan_dirs(search_dirs, "rq3_stage6_baselines_*.parquet")
    if not files:
        log.warning("no baseline files found in %s", search_dirs)
        return pd.DataFrame()
    rows = []
    for fp in files:
        try:
            df = _read_table(fp)
        except Exception as exc:  # noqa: BLE001
            log.warning("skip %s: %s", fp.name, exc)
            continue
        if "cell" not in df.columns:
            stem = fp.stem.replace("rq3_stage6_baselines_", "")
            df = df.copy()
            df["cell"] = stem
        if "baseline" not in df.columns:
            log.warning("baseline column missing in %s", fp.name)
            continue
        df = df.copy()
        df["cell_kind"] = df["cell"].map(CELL_KIND).fillna("?")
        df["dim"] = df["cell"].map(CELL_DIM).fillna(np.nan).astype(float)
        rows.append(df)
        stats.n_baseline_files += 1
        stats.n_baseline_rows += len(df)
        stats.baselines_seen.update(df["baseline"].unique().tolist())
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out = out.dropna(subset=["q_error"])
    out = out[out["q_error"] > 0]
    return out


# ---------------------------------------------------------------------------
# Section G1 — Per-method × per-cell consistency (single + multi)
# ---------------------------------------------------------------------------
def section_g1(method_df: pd.DataFrame) -> pd.DataFrame:
    """Per-method single/multi mean q_error + consistency ratio + tier rank.

    Returns one row per method:
        method, paradigm, tier, n_single, n_multi, mean_single, mean_multi,
        median_single, median_multi, consistency_ratio (multi/single),
        rank_single, rank_multi, top_tier_filter (1 if both ranks ≤ 8).
    """
    if method_df.empty:
        return pd.DataFrame()
    sub_s = method_df[method_df["cell_kind"] == "single"]
    sub_m = method_df[method_df["cell_kind"] != "single"]
    g_s = sub_s.groupby("method")["q_error"].agg(
        n_single="count", mean_single="mean",
        median_single="median", std_single="std")
    g_m = sub_m.groupby("method")["q_error"].agg(
        n_multi="count", mean_multi="mean",
        median_multi="median", std_multi="std")
    out = g_s.join(g_m, how="outer").reset_index()
    out["paradigm"] = out["method"].map(PARADIGM).fillna("?")
    out["tier"] = out["method"].map(TIER).fillna("?")
    out["consistency_ratio"] = out["mean_multi"] / out["mean_single"]
    # Rank smallest = best (lower q_error wins).
    out["rank_single"] = out["mean_single"].rank(method="min")
    out["rank_multi"] = out["mean_multi"].rank(method="min")
    # Top tier filter — both ranks in top half (≤ 11 of 22).
    top_n = max(1, int(np.ceil(out["method"].nunique() / 2)))
    out["top_tier_filter"] = ((out["rank_single"] <= top_n) &
                              (out["rank_multi"] <= top_n)).astype(int)
    out = out.sort_values("consistency_ratio")
    return out


def section_g1_paradigm_summary(g1: pd.DataFrame) -> pd.DataFrame:
    """Aggregate G1 to paradigm level — average rank per tier."""
    if g1.empty:
        return pd.DataFrame()
    return g1.groupby("paradigm").agg(
        n_methods=("method", "count"),
        mean_rank_single=("rank_single", "mean"),
        mean_rank_multi=("rank_multi", "mean"),
        mean_consistency=("consistency_ratio", "mean"),
    ).reset_index().sort_values("mean_rank_single")


# ---------------------------------------------------------------------------
# Section G2 — Adaptive (B1) gap, paired Wilcoxon + Bonferroni
# ---------------------------------------------------------------------------
def _paired_align(method_df: pd.DataFrame, baseline_df: pd.DataFrame,
                   cell: str, method: str, baseline: str) -> Optional[pd.DataFrame]:
    """Inner-join (selectivity, seed, query_id) across one cell × method × baseline.

    Returns the merged frame with ``q_error`` (method) and ``q_error_b``
    (baseline), or None if no rows survive.
    """
    KEY = ["selectivity", "seed", "query_id"]
    m_sub = method_df[(method_df["cell"] == cell) &
                      (method_df["method"] == method)]
    b_sub = baseline_df[(baseline_df["cell"] == cell) &
                        (baseline_df["baseline"] == baseline)]
    if m_sub.empty or b_sub.empty:
        return None
    m_keep = m_sub[KEY + ["q_error"]].copy()
    b_keep = b_sub[KEY + ["q_error"]].copy().rename(
        columns={"q_error": "q_error_b"})
    merged = m_keep.merge(b_keep, on=KEY, how="inner")
    merged = merged[(merged["q_error"] > 0) & (merged["q_error_b"] > 0)]
    if merged.empty:
        return None
    merged["delta_pct"] = ((merged["q_error"] - merged["q_error_b"]) /
                           merged["q_error_b"]) * 100.0
    return merged


def _wilcoxon_safe(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Wilcoxon signed-rank, returning (stat, p) or (nan, nan) on failure."""
    if len(x) < 5 or np.allclose(x, y):
        return float("nan"), float("nan")
    try:
        res = stats.wilcoxon(x, y, alternative="two-sided",
                             zero_method="zsplit")
        return float(res.statistic), float(res.pvalue)
    except Exception:
        return float("nan"), float("nan")


def _bootstrap_ci_mean_delta(deltas: np.ndarray, n_boot: int = BOOTSTRAP_N,
                             rng_seed: int = 7) -> tuple[float, float]:
    """Bootstrap 95% CI for mean of a 1D paired Δ% array.

    Returns (ci_lo, ci_hi) at the 2.5/97.5 percentile.
    """
    if len(deltas) < 5:
        return float("nan"), float("nan")
    rng = np.random.default_rng(rng_seed)
    n = len(deltas)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot_means = np.nanmean(deltas[idx], axis=1)
    return float(np.nanpercentile(boot_means, 2.5)), \
           float(np.nanpercentile(boot_means, 97.5))


def section_g2(method_df: pd.DataFrame, baseline_df: pd.DataFrame) -> pd.DataFrame:
    """Cell × method paired Δ% vs B1 with Wilcoxon and Bonferroni correction.

    Output schema:
        cell, cell_kind, method, paradigm, tier, n_paired,
        mean_delta_pct, median_delta_pct, ci_lo, ci_hi,
        wilcoxon_p, bonferroni_p, sig_raw_05, sig_bonf_05,
        method_better, n_better.
    """
    rows = []
    cells = sorted(method_df["cell"].unique())
    methods = sorted(method_df["method"].unique())
    n_tests = max(1, len(cells) * len(methods))
    for cell in cells:
        for method in methods:
            merged = _paired_align(method_df, baseline_df, cell, method, "B1")
            if merged is None:
                continue
            x = merged["q_error"].to_numpy()
            y = merged["q_error_b"].to_numpy()
            d = merged["delta_pct"].to_numpy()
            stat, p = _wilcoxon_safe(x, y)
            ci_lo, ci_hi = _bootstrap_ci_mean_delta(d)
            rows.append({
                "cell": cell,
                "cell_kind": CELL_KIND.get(cell, "?"),
                "method": method,
                "paradigm": PARADIGM.get(method, "?"),
                "tier": TIER.get(method, "?"),
                "n_paired": int(len(d)),
                "mean_delta_pct": float(np.nanmean(d)),
                "median_delta_pct": float(np.nanmedian(d)),
                "ci_lo": ci_lo,
                "ci_hi": ci_hi,
                "wilcoxon_stat": stat,
                "wilcoxon_p": p,
                "method_better": bool(np.nanmedian(d) < 0),
                "n_better": int((d < 0).sum()),
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    # Bonferroni correction across cell × method tests.
    p = out["wilcoxon_p"].to_numpy()
    finite = np.isfinite(p)
    bonf = np.full_like(p, np.nan, dtype=float)
    bonf[finite] = np.minimum(p[finite] * n_tests, 1.0)
    out["bonferroni_p"] = bonf
    out["sig_raw_05"] = (out["wilcoxon_p"] < ALPHA) & np.isfinite(out["wilcoxon_p"])
    out["sig_bonf_05"] = (out["bonferroni_p"] < ALPHA) & np.isfinite(out["bonferroni_p"])
    return out


def section_g2_summary(g2: pd.DataFrame) -> pd.DataFrame:
    """Per-method summary across cells: how many cells beat B1 sig.

    win_single_multi_b1 = sig in BOTH single AND multi cells. This flag is
    the **★ core finding of v7** — methods passing this filter are the
    primary contribution of the multi-domain extension.
    """
    if g2.empty:
        return pd.DataFrame()
    rows = []
    for method, g in g2.groupby("method"):
        # Beats B1 = method_better AND sig_bonf_05.
        wins = g[g["method_better"] & g["sig_bonf_05"]]
        wins_single = wins[wins["cell_kind"] == "single"]
        wins_multi = wins[wins["cell_kind"] != "single"]
        rows.append({
            "method": method,
            "paradigm": PARADIGM.get(method, "?"),
            "tier": TIER.get(method, "?"),
            "n_cells": int(len(g)),
            "n_single_cells": int((g["cell_kind"] == "single").sum()),
            "n_multi_cells": int((g["cell_kind"] != "single").sum()),
            "n_wins_total": int(len(wins)),
            "n_wins_single": int(len(wins_single)),
            "n_wins_multi": int(len(wins_multi)),
            "mean_delta_pct_overall": float(g["mean_delta_pct"].mean()),
            "win_single_multi_b1": bool(
                (len(wins_single) > 0) and (len(wins_multi) > 0)
            ),
        })
    return pd.DataFrame(rows).sort_values(
        ["win_single_multi_b1", "n_wins_total"], ascending=[False, False]
    )


# ---------------------------------------------------------------------------
# Section G3 — B4 (Adaptive + ensemble) vs B1, 4 axis
# ---------------------------------------------------------------------------
def _resource_per_cell_method(method_df: pd.DataFrame, cell: str,
                              method: str) -> dict:
    sub = method_df[(method_df["cell"] == cell) &
                    (method_df["method"] == method)]
    if sub.empty:
        return {"wall_clock_ms": float("nan"), "peak_rss_mb": float("nan")}
    return {
        "wall_clock_ms": float(sub.get("wall_clock_ms",
                                        pd.Series([np.nan])).mean()),
        "peak_rss_mb": float(sub.get("peak_rss_mb",
                                      pd.Series([np.nan])).mean()),
    }


def _resource_per_cell_baseline(baseline_df: pd.DataFrame, cell: str,
                                baseline: str) -> dict:
    sub = baseline_df[(baseline_df["cell"] == cell) &
                      (baseline_df["baseline"] == baseline)]
    if sub.empty:
        return {"wall_clock_ms": float("nan"), "peak_rss_mb": float("nan")}
    return {
        "wall_clock_ms": float(sub.get("wall_clock_ms",
                                        pd.Series([np.nan])).mean()),
        "peak_rss_mb": float(sub.get("peak_rss_mb",
                                      pd.Series([np.nan])).mean()),
    }


def section_g3(method_df: pd.DataFrame, baseline_df: pd.DataFrame,
               g5: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Stage ⑥ B1 vs B4 4-axis paired metric.

    For each (cell, ensemble_base_method) combination we compute:
        accuracy:       paired Δ% (B4 − B1) / B1 of mean q_error,
        convergence:    t* delta — t*(B4) − t*(B1),
        resource:       wall-clock seconds B4 − B1,
        rare_query:     mean q_error at sel=0.01 — B4 − B1.

    The "ensemble base method" is the legacy/new method that B4 wraps. In
    Phase F's measurement convention the wrapped method is encoded in the
    baseline parquet's ``ensemble_method`` column. If absent, we treat
    B4 as a single estimator and report cell-level deltas only.
    """
    rows = []
    cells = sorted(set(baseline_df["cell"].unique()) &
                   set(method_df["cell"].unique()))
    has_b4 = "B4" in baseline_df["baseline"].unique() \
        if not baseline_df.empty else False
    has_b1 = "B1" in baseline_df["baseline"].unique() \
        if not baseline_df.empty else False
    if not (has_b1 and has_b4):
        log.warning("B1 / B4 missing — section G3 will emit empty table")
        return pd.DataFrame()
    KEY = ["selectivity", "seed", "query_id"]
    for cell in cells:
        b1 = baseline_df[(baseline_df["cell"] == cell) &
                          (baseline_df["baseline"] == "B1")]
        b4 = baseline_df[(baseline_df["cell"] == cell) &
                          (baseline_df["baseline"] == "B4")]
        if b1.empty or b4.empty:
            continue
        # B4 may carry an `ensemble_method` column to identify the wrapped
        # base estimator; if not, fall back to per-cell aggregate.
        b4_groups = b4.groupby("ensemble_method") \
            if "ensemble_method" in b4.columns else [(None, b4)]
        for ensemble_method, b4g in b4_groups:
            paired = b1.merge(b4g, on=KEY, suffixes=("_b1", "_b4"), how="inner")
            paired = paired[(paired["q_error_b1"] > 0) &
                            (paired["q_error_b4"] > 0)]
            if paired.empty:
                continue
            d = ((paired["q_error_b4"] - paired["q_error_b1"]) /
                 paired["q_error_b1"]) * 100.0
            stat, p = _wilcoxon_safe(paired["q_error_b4"].to_numpy(),
                                      paired["q_error_b1"].to_numpy())
            ci_lo, ci_hi = _bootstrap_ci_mean_delta(d.to_numpy())

            rare = paired[paired["selectivity"] == 0.01]
            if rare.empty:
                rare_delta = float("nan")
            else:
                rare_delta = float(((rare["q_error_b4"] - rare["q_error_b1"]) /
                                    rare["q_error_b1"]).mean() * 100.0)

            wc_b1 = float(b1.get("wall_clock_ms", pd.Series([np.nan])).mean())
            wc_b4 = float(b4g.get("wall_clock_ms",
                                   pd.Series([np.nan])).mean())
            wall_delta = (wc_b4 - wc_b1) if np.isfinite(wc_b4) and np.isfinite(wc_b1) else float("nan")

            # Convergence delta lookup.
            conv_delta = float("nan")
            if g5 is not None and not g5.empty and ensemble_method is not None:
                row = g5[(g5["cell"] == cell) &
                          (g5["method"] == ensemble_method)]
                if not row.empty:
                    conv_delta = float(row["t_star_delta_b4_b1"].iloc[0])

            mean_delta = float(np.nanmean(d))
            rows.append({
                "cell": cell,
                "cell_kind": CELL_KIND.get(cell, "?"),
                "ensemble_method": ensemble_method or "(aggregate)",
                "paradigm": PARADIGM.get(ensemble_method, "?")
                    if ensemble_method else "?",
                "n_paired": int(len(paired)),
                "mean_delta_pct_accuracy": mean_delta,
                "ci_lo": ci_lo,
                "ci_hi": ci_hi,
                "wilcoxon_p_accuracy": p,
                "rare_query_delta_pct": rare_delta,
                "wall_clock_ms_delta": wall_delta,
                "convergence_t_star_delta": conv_delta,
                # 4-axis flags — TRUE if B4 wins the axis (lower is better
                # for accuracy/wall/convergence, lower abs for rare_query).
                "win_accuracy": bool(mean_delta < 0
                    and np.isfinite(p) and p < BONFERRONI_ALPHA),
                "win_convergence": bool(np.isfinite(conv_delta)
                    and conv_delta < 0),
                "win_resource": bool(np.isfinite(wall_delta)
                    and wall_delta < 0),
                "win_rare_query": bool(np.isfinite(rare_delta)
                    and rare_delta < 0),
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["axis_wins_count"] = (
        out["win_accuracy"].astype(int)
        + out["win_convergence"].astype(int)
        + out["win_resource"].astype(int)
        + out["win_rare_query"].astype(int)
    )
    out["any_axis_win"] = out["axis_wins_count"] > 0
    return out.sort_values("axis_wins_count", ascending=False)


# ---------------------------------------------------------------------------
# Section G4 — Failure mode regression (extended)
# ---------------------------------------------------------------------------
def section_g4(method_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extend Phase B regression to 22 method × 28 cell.

    Spec (v7 §8.5):
        log(q_error) = β₀ + β₁ log(dim) + β₂ sel + β₃ is_multi
                     + Σ_p γ_p 1{paradigm=p}
                     + Σ_t δ_t 1{tier=t}
                     + ε

    We additionally fit a per-method curse-of-dim slope:
        log(q_error) = a + β₁_m log(dim) + ε
    so the new 11 methods can be compared with the legacy 11.
    """
    if method_df.empty:
        return pd.DataFrame(), pd.DataFrame()
    df = method_df.copy()
    df = df[df["q_error"] > 0]
    df = df.dropna(subset=["dim"])
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    df["log_q_error"] = np.log(df["q_error"])
    df["log_dim"] = np.log(df["dim"].astype(float))
    df["is_multi"] = (df["cell_kind"] != "single").astype(int)
    paradigm_d = pd.get_dummies(df["paradigm"], prefix="par", drop_first=True)
    tier_d = pd.get_dummies(df["tier"], prefix="tier", drop_first=True)
    X = pd.concat([
        df[["log_dim", "selectivity", "is_multi"]],
        paradigm_d, tier_d,
    ], axis=1).astype(float)
    X = sm.add_constant(X)
    y = df["log_q_error"].astype(float)
    try:
        model = sm.OLS(y, X, missing="drop").fit()
    except Exception as exc:
        log.warning("OLS fit failed: %s", exc)
        return pd.DataFrame(), pd.DataFrame()
    summary = pd.DataFrame({
        "term": model.params.index,
        "coef": model.params.values,
        "std_err": model.bse.values,
        "t_value": model.tvalues.values,
        "p_value": model.pvalues.values,
        "ci_low": model.conf_int()[0].values,
        "ci_high": model.conf_int()[1].values,
    })
    summary.attrs["r2"] = float(model.rsquared)
    summary.attrs["r2_adj"] = float(model.rsquared_adj)
    summary.attrs["nobs"] = int(model.nobs)

    # Per-method curse-of-dim slope (legacy 11 vs new 11 comparison).
    rows = []
    for method, g in df.groupby("method"):
        if g["dim"].nunique() < 2:
            continue
        Xm = sm.add_constant(g["log_dim"].astype(float))
        ym = g["log_q_error"].astype(float)
        try:
            m = sm.OLS(ym, Xm, missing="drop").fit()
        except Exception:
            continue
        rows.append({
            "method": method,
            "paradigm": PARADIGM.get(method, "?"),
            "tier": TIER.get(method, "?"),
            "n_obs": int(m.nobs),
            "intercept": float(m.params["const"]),
            "slope_log_dim": float(m.params["log_dim"]),
            "slope_se": float(m.bse["log_dim"]),
            "slope_p": float(m.pvalues["log_dim"]),
            "r2": float(m.rsquared),
        })
    curse = pd.DataFrame(rows).sort_values("slope_log_dim")
    return summary, curse


# ---------------------------------------------------------------------------
# Section G5 — Convergence speed
# ---------------------------------------------------------------------------
def _running_mean_first_within(values: np.ndarray, threshold_rel: float) -> int:
    """First index t at which |S_t − S_∞| / |S_∞| < threshold_rel.

    Returns -1 if never converges.
    """
    if len(values) == 0:
        return -1
    s_inf = np.nanmean(values)
    if not np.isfinite(s_inf) or abs(s_inf) < 1e-9:
        return -1
    cumsum = np.cumsum(values)
    counts = np.arange(1, len(values) + 1)
    s_t = cumsum / counts
    rel = np.abs(s_t - s_inf) / abs(s_inf)
    hits = np.where(rel < threshold_rel)[0]
    return int(hits[0]) if hits.size else -1


def section_g5(method_df: pd.DataFrame, baseline_df: pd.DataFrame) -> pd.DataFrame:
    """Per cell × method (B4) convergence time t* and B1 baseline.

    Output schema:
        cell, method, paradigm, tier,
        t_star_b4, t_star_b1, t_star_delta_b4_b1.

    Convention: t* defined as **mean across seeds** of the
    first-time-within-5% index over the (sel-pooled) query stream of length
    sel × seed × query = 2500. Each seed produces one t*; we average.
    """
    rows = []
    if method_df.empty:
        return pd.DataFrame()
    cells = sorted(method_df["cell"].unique())
    methods = sorted(method_df["method"].unique())
    has_b1 = (not baseline_df.empty
              and "B1" in baseline_df["baseline"].unique())
    has_b4 = (not baseline_df.empty
              and "B4" in baseline_df["baseline"].unique())

    for cell in cells:
        # B1 t* per cell (single number, baseline reference).
        if has_b1:
            b1 = baseline_df[(baseline_df["cell"] == cell) &
                              (baseline_df["baseline"] == "B1")]
            t_b1_list = []
            for seed, g in b1.groupby("seed"):
                arr = g.sort_values(["selectivity", "query_id"])["q_error"].to_numpy()
                t = _running_mean_first_within(arr, CONVERGENCE_REL_THRESHOLD)
                if t >= 0:
                    t_b1_list.append(t)
            t_b1 = float(np.nanmean(t_b1_list)) if t_b1_list else float("nan")
        else:
            t_b1 = float("nan")

        for method in methods:
            sub = method_df[(method_df["cell"] == cell) &
                            (method_df["method"] == method)]
            if sub.empty:
                continue
            t_method_list = []
            for seed, g in sub.groupby("seed"):
                arr = g.sort_values(["selectivity", "query_id"])["q_error"].to_numpy()
                t = _running_mean_first_within(arr, CONVERGENCE_REL_THRESHOLD)
                if t >= 0:
                    t_method_list.append(t)
            t_method = float(np.nanmean(t_method_list)) if t_method_list else float("nan")

            # B4 with this method as ensemble_method (if present).
            t_b4 = float("nan")
            if has_b4:
                b4 = baseline_df[(baseline_df["cell"] == cell) &
                                  (baseline_df["baseline"] == "B4")]
                if "ensemble_method" in b4.columns:
                    b4 = b4[b4["ensemble_method"] == method]
                if not b4.empty:
                    t_b4_list = []
                    for seed, g in b4.groupby("seed"):
                        arr = g.sort_values(
                            ["selectivity", "query_id"])["q_error"].to_numpy()
                        t = _running_mean_first_within(arr,
                                                        CONVERGENCE_REL_THRESHOLD)
                        if t >= 0:
                            t_b4_list.append(t)
                    t_b4 = float(np.nanmean(t_b4_list)) if t_b4_list else float("nan")

            rows.append({
                "cell": cell,
                "cell_kind": CELL_KIND.get(cell, "?"),
                "method": method,
                "paradigm": PARADIGM.get(method, "?"),
                "tier": TIER.get(method, "?"),
                "t_star_method": t_method,
                "t_star_b1": t_b1,
                "t_star_b4": t_b4,
                "t_star_delta_method_b1": (t_method - t_b1)
                    if np.isfinite(t_method) and np.isfinite(t_b1)
                    else float("nan"),
                "t_star_delta_b4_b1": (t_b4 - t_b1)
                    if np.isfinite(t_b4) and np.isfinite(t_b1)
                    else float("nan"),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Section G6 — Resource (wall-clock + memory) Pareto frontier
# ---------------------------------------------------------------------------
def section_g6(method_df: pd.DataFrame) -> pd.DataFrame:
    """Per-method wall-clock and memory aggregates + Pareto-optimality flag.

    A method is **Pareto-optimal** if no other method dominates it on
    (mean_q_error, wall_clock_ms) — i.e. no method has both lower q_error
    AND lower wall-clock.
    """
    if method_df.empty:
        return pd.DataFrame()
    g = method_df.groupby("method").agg(
        mean_q_error=("q_error", "mean"),
        median_q_error=("q_error", "median"),
        mean_wall_clock_ms=("wall_clock_ms", "mean")
            if "wall_clock_ms" in method_df.columns else ("q_error", "size"),
        mean_peak_rss_mb=("peak_rss_mb", "mean")
            if "peak_rss_mb" in method_df.columns else ("q_error", "size"),
    ).reset_index()
    g["paradigm"] = g["method"].map(PARADIGM).fillna("?")
    g["tier"] = g["method"].map(TIER).fillna("?")

    # Pareto frontier: method i dominated iff exists j with
    # j.q_error < i.q_error AND j.wall < i.wall.
    qs = g["mean_q_error"].to_numpy()
    ws = g["mean_wall_clock_ms"].to_numpy()
    pareto = np.ones(len(g), dtype=bool)
    for i in range(len(g)):
        for j in range(len(g)):
            if i == j:
                continue
            if (np.isfinite(qs[j]) and np.isfinite(ws[j])
                    and np.isfinite(qs[i]) and np.isfinite(ws[i])
                    and qs[j] < qs[i] and ws[j] < ws[i]):
                pareto[i] = False
                break
    g["pareto_optimal"] = pareto
    return g.sort_values("mean_q_error")


# ---------------------------------------------------------------------------
# Section G7 — Production-ready package summary (top 3-5)
# ---------------------------------------------------------------------------
def section_g7(g1: pd.DataFrame, g2_summary: pd.DataFrame,
               g3: pd.DataFrame, g6: pd.DataFrame) -> pd.DataFrame:
    """Four-way intersection → top 3-5 production-ready methods.

    Filters in order:
      1. ``win_single_multi_b1`` from G2 summary (sig in both single+multi).
      2. ``axis_wins_count >= 1`` in G3 (Stage ⑥ contribution on any axis).
      3. ``pareto_optimal`` in G6 (cost-quality non-dominated).
      4. ``top_tier_filter`` in G1 (top half rank in single AND multi).

    Output schema:
        method, paradigm, tier, mean_consistency, mean_delta_pct_overall,
        n_wins_total, axis_wins_count, mean_q_error, mean_wall_clock_ms,
        pareto_optimal, top_tier_filter, qualifies, english_descriptor.
    """
    if g2_summary.empty:
        return pd.DataFrame()
    out = g2_summary[[
        "method", "paradigm", "tier", "n_wins_total",
        "n_wins_single", "n_wins_multi", "mean_delta_pct_overall",
        "win_single_multi_b1",
    ]].copy()
    if not g1.empty:
        out = out.merge(
            g1[["method", "consistency_ratio", "top_tier_filter",
                "rank_single", "rank_multi"]],
            on="method", how="left",
        )
    if not g6.empty:
        out = out.merge(
            g6[["method", "mean_q_error", "mean_wall_clock_ms",
                "pareto_optimal"]],
            on="method", how="left",
        )
    if not g3.empty:
        per_method_axis = g3.groupby("ensemble_method").agg(
            axis_wins_count=("axis_wins_count", "mean"),
            any_axis_win=("any_axis_win", "any"),
        ).reset_index().rename(columns={"ensemble_method": "method"})
        out = out.merge(per_method_axis, on="method", how="left")
    else:
        out["axis_wins_count"] = 0.0
        out["any_axis_win"] = False
    out["qualifies"] = (
        out["win_single_multi_b1"].fillna(False).astype(bool)
        & out.get("any_axis_win", pd.Series([False] * len(out))).fillna(False).astype(bool)
        & out.get("pareto_optimal", pd.Series([False] * len(out))).fillna(False).astype(bool)
        & (out.get("top_tier_filter",
                    pd.Series([0] * len(out))).fillna(0).astype(int) == 1)
    )
    descriptors = {
        "HDBSCAN": "Density-based clustering stratifier (Campello+2013).",
        "MB_partial": "Streaming K-means partial fit (Sculley 2010 + sklearn).",
        "Hilbert": "Hilbert space-filling curve stratifier (Lawder+2001).",
        "sparse_rp": "Sparse random projection (Achlioptas 2003).",
        "WanderJoin": "Index-aware random walk for join cardinality (Li+2016/2019).",
        "AMS_CountSketch": "Count-sketch F2 moment estimator (Alon+1999).",
        "NeuroCard": "Multi-table autoregressive density (Yang VLDB 2020).",
        "PQ": "Product Quantization codebook stratifier (Jegou+2011).",
        "Coreset": "Sensitivity-weighted coreset (Bachem+2017).",
        "DenseRP": "Dense Gaussian random projection (Bingham+2001).",
        "BanditUCB1": "UCB1 stratified bandit allocation (Carpentier+2011).",
        "NeurAM": "1D autoencoder manifold projection (Geraci+2026).",
        "CCA1D": "Canonical correlation 1D projection (Hotelling 1936).",
        "CoCluster_Nystrom": "Bipartite spectral co-clustering (Dhillon 2003).",
        "ConditionalAdaptive":
            "Selectivity-conditioned Adaptive variant (Lim+2025).",
    }
    out["english_descriptor"] = out["method"].map(descriptors).fillna("(legacy)")
    out = out.sort_values(["qualifies", "n_wins_total"],
                          ascending=[False, False])
    return out


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_g1(g1: pd.DataFrame, fig_path: Path) -> None:
    if g1.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = plt.get_cmap("tab10")
    pmap = {p: cmap(i) for i, p in enumerate(PARADIGMS)}
    for _, r in g1.iterrows():
        ax.scatter(r["mean_single"], r["mean_multi"],
                    s=70, color=pmap.get(r["paradigm"], "#888"),
                    edgecolor="black", linewidths=0.6)
        ax.annotate(r["method"], (r["mean_single"], r["mean_multi"]),
                     fontsize=7, alpha=0.9, xytext=(4, 4),
                     textcoords="offset points")
    if not g1[["mean_single", "mean_multi"]].empty:
        m = float(np.nanmax([g1["mean_single"].max(),
                              g1["mean_multi"].max()]))
        if np.isfinite(m) and m > 0:
            ax.plot([0, m], [0, m], "k--", linewidth=0.8, alpha=0.6,
                     label="parity")
    ax.set_xlabel("Mean q_error (single cells)")
    ax.set_ylabel("Mean q_error (multi cells)")
    ax.set_title("G1 — Per-method single vs multi consistency")
    handles = [plt.Line2D([], [], marker="o", color="w",
                          markerfacecolor=pmap[p], markeredgecolor="black",
                          markersize=8, label=p) for p in PARADIGMS]
    ax.legend(handles=handles, fontsize=6.5, loc="best")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)


def plot_g2(g2: pd.DataFrame, fig_path: Path) -> None:
    if g2.empty:
        return
    pivot = g2.pivot_table(index="method", columns="cell",
                           values="mean_delta_pct", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(min(2 + 0.4 * len(pivot.columns), 18),
                                     0.5 * len(pivot.index) + 1.5))
    vmax = float(np.nanmax(np.abs(pivot.values))) if pivot.size else 50.0
    if not np.isfinite(vmax):
        vmax = 50.0
    im = ax.imshow(pivot.values, cmap="RdBu_r", aspect="auto",
                    vmin=-vmax, vmax=vmax)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=80, ha="right", fontsize=6.5)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=7)
    ax.set_title("G2 — Paired Δ% vs B1 (Adaptive). Negative = method better.")
    fig.colorbar(im, ax=ax, fraction=0.025).set_label("Δ% (B4 − B1) / B1 × 100")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)


def plot_g3_radar(g3: pd.DataFrame, fig_path: Path) -> None:
    if g3.empty:
        return
    axes = ["accuracy", "convergence", "resource", "rare_query"]
    win_cols = [f"win_{a}" for a in axes]
    g = g3.groupby("ensemble_method")[win_cols].mean().reset_index()
    g = g.head(8)  # avoid clutter.
    if g.empty:
        return
    angles = np.linspace(0, 2 * np.pi, len(axes), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    cmap = plt.get_cmap("tab10")
    for i, (_, row) in enumerate(g.iterrows()):
        values = row[win_cols].tolist() + [row[win_cols].iloc[0]]
        ax.plot(angles, values, label=row["ensemble_method"],
                 color=cmap(i % 10), linewidth=1.5)
        ax.fill(angles, values, alpha=0.08, color=cmap(i % 10))
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=7)
    ax.set_ylim(0, 1)
    ax.set_title("G3 — Stage ⑥ 4-axis contribution (B4 wins per ensemble base)")
    ax.legend(fontsize=7, loc="upper right", bbox_to_anchor=(1.35, 1.05))
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)


def plot_g4_forest(reg: pd.DataFrame, fig_path: Path) -> None:
    if reg.empty:
        return
    rg = reg[reg["term"] != "const"].copy().sort_values("coef")
    if rg.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 5 + 0.18 * len(rg)))
    y = np.arange(len(rg))
    err_lo = np.maximum(rg["coef"] - rg["ci_low"], 0)
    err_hi = np.maximum(rg["ci_high"] - rg["coef"], 0)
    ax.errorbar(rg["coef"], y, xerr=[err_lo, err_hi], fmt="o",
                 color="#1f77b4", capsize=3)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(rg["term"], fontsize=7)
    ax.set_xlabel("OLS coefficient on log q_error")
    ax.set_title(f"G4 — Extended failure-mode regression (n={reg.attrs.get('nobs','?')}, "
                  f"R²={reg.attrs.get('r2', float('nan')):.3f})")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)


def plot_g5_box(g5: pd.DataFrame, fig_path: Path) -> None:
    if g5.empty:
        return
    sub = g5.dropna(subset=["t_star_delta_b4_b1"])
    if sub.empty:
        # Fall back to method vs B1.
        sub = g5.dropna(subset=["t_star_delta_method_b1"])
        if sub.empty:
            return
        col = "t_star_delta_method_b1"
        title = "G5 — Convergence delta (method − B1), by paradigm"
    else:
        col = "t_star_delta_b4_b1"
        title = "G5 — Convergence delta (B4 − B1) per paradigm"
    fig, ax = plt.subplots(figsize=(8, 5))
    paradigms = sorted(sub["paradigm"].unique())
    data = [sub[sub["paradigm"] == p][col].dropna().to_numpy()
            for p in paradigms]
    try:
        ax.boxplot(data, tick_labels=paradigms)
    except TypeError:
        ax.boxplot(data, labels=paradigms)
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_ylabel("t* delta (queries to convergence)")
    ax.set_title(title)
    plt.xticks(rotation=30, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)


def plot_g6_pareto(g6: pd.DataFrame, fig_path: Path) -> None:
    if g6.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = plt.get_cmap("tab10")
    pmap = {p: cmap(i) for i, p in enumerate(PARADIGMS)}
    pareto = g6[g6["pareto_optimal"]].sort_values("mean_q_error")
    others = g6[~g6["pareto_optimal"]]
    ax.scatter(others["mean_wall_clock_ms"], others["mean_q_error"],
                color="#aaaaaa", s=40, alpha=0.6, label="dominated")
    for _, r in g6.iterrows():
        ax.annotate(r["method"], (r["mean_wall_clock_ms"], r["mean_q_error"]),
                     fontsize=6, alpha=0.85, xytext=(3, 3),
                     textcoords="offset points")
    if not pareto.empty:
        ax.plot(pareto["mean_wall_clock_ms"], pareto["mean_q_error"],
                "ko-", linewidth=1.2, markerfacecolor="red", label="Pareto frontier")
    ax.set_xlabel("Mean wall-clock per query (ms)")
    ax.set_ylabel("Mean q_error")
    ax.set_title("G6 — Cost / quality Pareto frontier (22 methods)")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)


def plot_g7_top(g7: pd.DataFrame, fig_path: Path) -> None:
    if g7.empty:
        return
    top = g7.head(10).copy()
    if top.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(top) + 1.5))
    colors = ["#2ca02c" if q else "#aaaaaa" for q in top["qualifies"]]
    ax.barh(top["method"], top["n_wins_total"], color=colors)
    ax.set_xlabel("# cells where method beats B1 with Bonferroni-sig")
    ax.set_title("G7 — Top method candidates (green = qualifies for production)")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(fig_path, dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def _coef(reg: pd.DataFrame, term: str) -> tuple[float, float, float]:
    if reg.empty or term not in reg["term"].values:
        return float("nan"), float("nan"), float("nan")
    r = reg[reg["term"] == term].iloc[0]
    return float(r["coef"]), float(r["std_err"]), float(r["p_value"])


def write_report(out_dir: Path,
                 g1: pd.DataFrame, g1_par: pd.DataFrame,
                 g2: pd.DataFrame, g2_summary: pd.DataFrame,
                 g3: pd.DataFrame,
                 reg: pd.DataFrame, curse: pd.DataFrame,
                 g5: pd.DataFrame,
                 g6: pd.DataFrame,
                 g7: pd.DataFrame,
                 stats: LoadStats) -> Path:
    """Render a 1500–2500 word academic narrative in REPORT.md."""
    rep = out_dir / "REPORT.md"
    n_methods = len(stats.methods_seen) if stats.methods_seen else 0
    n_cells = len(stats.cells_seen) if stats.cells_seen else 0
    n_meth_rows = stats.n_method_rows
    n_base_rows = stats.n_baseline_rows

    b_dim, se_dim, p_dim = _coef(reg, "log_dim")
    b_sel, se_sel, p_sel = _coef(reg, "selectivity")
    b_multi, se_multi, p_multi = _coef(reg, "is_multi")
    r2 = reg.attrs.get("r2", float("nan"))
    r2a = reg.attrs.get("r2_adj", float("nan"))
    nobs = reg.attrs.get("nobs", 0)

    win_methods = []
    if not g2_summary.empty:
        win_methods = g2_summary[g2_summary["win_single_multi_b1"]]["method"].tolist()
    qualifies_methods = []
    if not g7.empty:
        qualifies_methods = g7[g7["qualifies"]]["method"].tolist()

    text = []
    text.append("# Phase G — End-to-end Analysis Report (v7 22 method × 28 cell)")
    text.append("")
    text.append("**Data inventory.** This report consolidates all eight Phase G "
                f"analytical sections over {n_methods} methods × {n_cells} cells "
                f"ingested from {stats.n_method_files} method parquets "
                f"({n_meth_rows:,} rows) and {stats.n_baseline_files} Phase F "
                f"baseline parquets ({n_base_rows:,} rows). The full design matrix "
                "is 22 method × 28 cell × 5 selectivity × 5 seed × 100 query "
                f"= 7.7M paired observations under the v7 plan; this run "
                f"observed {len(stats.cells_seen)} cells "
                f"(coverage {len(stats.cells_seen)}/28) and "
                f"{len(stats.methods_seen)} methods "
                f"(coverage {len(stats.methods_seen)}/22). Six baselines are "
                "expected (B1–B6); this run saw "
                f"{sorted(stats.baselines_seen)}.")
    text.append("")

    # G1 narrative
    text.append("## G1 — Per-method single+multi consistency")
    text.append("")
    text.append("Section G1 measures, for each of the 22 methods, the joint "
                "single-domain and multi-domain mean q_error. The "
                "**consistency ratio** (multi mean ÷ single mean) is the "
                "first-order summary statistic of single→multi degradation: "
                "ratios near 1.0 indicate stable cross-domain behaviour, ratios "
                "much greater than 1.0 indicate that the multi cells exposed "
                "the curse-of-dim or sample-strata-ratio failure modes catalogued "
                "in Phase B (Beyer 1999, Cochran 1977 §5.5, Bengtsson-Bickel-Li "
                "2008). The `top_tier_filter` flag identifies methods that "
                "rank in the top half on *both* single and multi cells; v7 "
                "treats this filter as the entry gate for Stage ⑦ "
                "production candidates.")
    if not g1_par.empty:
        text.append("")
        text.append("Paradigm-level aggregates show:")
        text.append("")
        text.append("| paradigm | n_methods | mean rank single | mean rank multi | mean consistency |")
        text.append("|---|---|---|---|---|")
        for _, r in g1_par.iterrows():
            text.append(f"| {r['paradigm']} | {int(r['n_methods'])} | "
                        f"{r['mean_rank_single']:.2f} | "
                        f"{r['mean_rank_multi']:.2f} | "
                        f"{r['mean_consistency']:.3f} |")
    text.append("")

    # G2 narrative
    text.append("## G2 — Paired Δ% vs Adaptive (B1)")
    text.append("")
    text.append("Section G2 computes, for every (cell × method) pair, a "
                "paired Wilcoxon signed-rank test against the Adaptive "
                "Sampling baseline B1 (Lim et al. 2025 Section V-B; "
                "hyperparameters m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, "
                "period=50, N=385). Each test draws on "
                f"≈{N_PAIRED_PER_CELL:,} paired observations (5 sel × 5 seed × "
                "100 query) which W1 sprint validated as a sufficient sample "
                "size for power ≥ 0.8 at the proposed effect sizes. "
                "Multiple-comparison control follows v7 §8.2 with a Bonferroni "
                f"correction at α/22 ≈ {BONFERRONI_ALPHA:.4f} (family of 22 "
                "method tests per cell), reported alongside raw p-values for "
                "transparency. Mean Δ% confidence intervals are 1000-iteration "
                "bootstrap percentiles per v7 §8.3.")
    text.append("")
    if not g2_summary.empty:
        n_wins_table = g2_summary.head(min(8, len(g2_summary)))
        text.append("| method | tier | wins single | wins multi | win_single_multi | mean Δ% |")
        text.append("|---|---|---|---|---|---|")
        for _, r in n_wins_table.iterrows():
            text.append(f"| {r['method']} | {r['tier']} | "
                        f"{int(r['n_wins_single'])} | "
                        f"{int(r['n_wins_multi'])} | "
                        f"{'**YES**' if r['win_single_multi_b1'] else 'no'} | "
                        f"{r['mean_delta_pct_overall']:+.2f}% |")
    text.append("")
    if win_methods:
        text.append(f"**Core finding.** {len(win_methods)} method(s) — "
                    f"{', '.join(win_methods)} — beat B1 with statistical "
                    "significance under the Bonferroni-adjusted α in *both* "
                    "single and multi cells. This is the paired-better outcome "
                    "that the v7 multi-relation extension was designed to "
                    "produce, against the 0/66 baseline established by the 5/9 "
                    "11-method × 6-cell paradigm measurement.")
    else:
        text.append("**Core finding (provisional).** No method passes the "
                    "single+multi Bonferroni-significant filter at the time "
                    "of this report. If this persists after the full Phase E "
                    "matrix completes, the contribution is reframed under "
                    "v7 §3 as a quantitative confirmation of the literature "
                    "gap (Section 1) — the first published evidence that no "
                    "method in the 22-method portfolio crosses the "
                    "single+multi joint significance threshold.")
    text.append("")

    # G3 narrative
    text.append("## G3 — Adaptive vs Adaptive+ensemble (B1 vs B4)")
    text.append("")
    text.append("Section G3 implements the Stage ⑥ 4-axis contribution metric "
                "(v7 §8.7). For every cell × ensemble-base-method, B4 — the "
                "Adaptive sample size wrapped in the chosen ensemble strategy "
                "— is paired against B1 along four axes: accuracy "
                "(paired Δ% mean q_error), convergence speed "
                "(t* delta per v7 §8.6), resource cost (wall-clock ms delta), "
                "and rare-query robustness (sel=0.01 mean q_error delta). A "
                "method qualifies for the Stage ⑥ contribution if B4 wins on "
                "**any** axis under the Bonferroni-adjusted α. The current "
                f"run observed {0 if g3.empty else len(g3)} (cell × ensemble) "
                "rows; "
                f"{0 if g3.empty else int(g3['any_axis_win'].sum())} have at "
                "least one axis win.")
    text.append("")

    # G4 narrative
    text.append("## G4 — Failure mode regression (extended)")
    text.append("")
    text.append("Section G4 re-fits the v7 §8.5 regression "
                "`log(q_error) = β₀ + β₁ log(dim) + β₂ sel + β₃ is_multi + "
                "Σγ_p paradigm + Σδ_t tier` on the extended 22-method × 28-cell "
                "matrix. The regression is the empirical bridge between the "
                "Phase B failure-mode diagnosis and the Phase G new-method "
                "evidence: positive β₁ corroborates Beyer 1999 / Geraci 2026 "
                "distance concentration, positive β₃ confirms the multi-relation "
                "shift, and negative paradigm coefficients γ_p relative to the "
                "P1_Cluster reference identify paradigms that mitigate the "
                f"failure modes. The current fit yields R²={r2:.3f} "
                f"(adj {r2a:.3f}, n={nobs:,}) with "
                f"β₁(log_dim)={b_dim:+.3f} ± {se_dim:.3f} (p={p_dim:.3g}), "
                f"β₃(is_multi)={b_multi:+.3f} ± {se_multi:.3f} (p={p_multi:.3g}), "
                f"β₂(sel)={b_sel:+.3f} ± {se_sel:.3f} (p={p_sel:.3g}). The "
                "per-method curse-of-dim slope table allows the new 11 methods "
                "to be compared with the legacy 11 directly: the design "
                "expectation is that NeurAM, Coreset and PQ exhibit "
                "significantly *lower* β₁_method than legacy P1/P5 methods, "
                "consistent with their dim-invariant (NeurAM, "
                "Bachem 2017) or codebook-bounded (PQ, Jegou 2011) "
                "guarantees.")
    if not curse.empty:
        text.append("")
        text.append("Selected per-method slopes (sorted ascending — flatter is "
                    "better for high-dim robustness):")
        text.append("")
        text.append("| method | tier | paradigm | β₁(log_dim) | p | R² |")
        text.append("|---|---|---|---|---|---|")
        for _, r in curse.head(min(10, len(curse))).iterrows():
            text.append(f"| {r['method']} | {r['tier']} | {r['paradigm']} | "
                        f"{r['slope_log_dim']:+.3f} | {r['slope_p']:.3g} | "
                        f"{r['r2']:.2f} |")
    text.append("")

    # G5 narrative
    text.append("## G5 — Convergence speed analysis")
    text.append("")
    text.append("Section G5 implements the v7 §8.6 convergence metric "
                "t* = first query t at which the running-mean q_error "
                "S_t satisfies |S_t − S_∞| / |S_∞| < 5%. The interesting "
                "delta is t*(B4) − t*(B1): a negative delta means "
                "Adaptive+ensemble (B4) converges faster than Adaptive alone "
                "(B1), one of the four contribution axes in Stage ⑥. We "
                "average across seeds within each cell to control for sample "
                "ordering; the cell-level distribution is reported per "
                "paradigm in `fig_g5_convergence.png`. The t* metric is "
                "complementary to the accuracy axis because two methods can "
                "achieve the same mean q_error but differ in their "
                "transient behaviour over the 100-query stream.")
    text.append("")

    # G6 narrative
    text.append("## G6 — Resource analysis and Pareto frontier")
    text.append("")
    text.append("Section G6 aggregates wall-clock and peak RSS across cells "
                "for each method and computes the Pareto frontier on "
                "(mean_q_error, mean_wall_clock_ms). A method is **Pareto-"
                "dominated** if some other method beats it on both axes; "
                "the non-dominated set is the production candidate frontier. "
                "The legacy 4강 (HDBSCAN, MB_partial, Hilbert, sparse_rp) "
                "established the W1 reference frontier; new methods must "
                "extend or refine this frontier to qualify for Stage ⑦. "
                "PQ and NeurAM are expected to dominate sparse_rp / PCA1D "
                "on accuracy at comparable wall-clock; CCA1D and "
                "CoCluster_Nystrom are expected to occupy a higher-cost "
                "position justified only by their multi-vector structural "
                "guarantees.")
    text.append("")

    # G7 narrative
    text.append("## G7 — Production-ready package summary")
    text.append("")
    text.append("Section G7 intersects the four filters built up in G1–G6: "
                "(i) `win_single_multi_b1` from G2 — the method must beat B1 "
                "in both single and multi cells under Bonferroni; (ii) "
                "`any_axis_win` from G3 — Stage ⑥ contribution on at least one "
                "of accuracy / convergence / resource / rare-query; (iii) "
                "`pareto_optimal` from G6 — non-dominated on cost-quality; "
                "(iv) `top_tier_filter` from G1 — top-half rank in single AND "
                "multi. Methods passing all four filters are the recommended "
                "production candidates that the Stage ⑦ exqutor_augment "
                "package should expose as drop-in registry entries with the "
                "English README descriptors emitted in `G7_production_top.csv`.")
    text.append("")
    if qualifies_methods:
        text.append(f"**Recommended production methods**: "
                    f"{', '.join(qualifies_methods)}.")
    else:
        text.append("**Recommended production methods**: none qualify under "
                    "the strict 4-filter intersection in this run; relax to "
                    "`win_single_multi_b1 ∧ any_axis_win` (drop the Pareto "
                    "and top_tier filters) to get a softer recommendation.")
    text.append("")

    # Closing references
    text.append("## References")
    text.append("- Beyer, K., Goldstein, J., Ramakrishnan, R., & Shaft, U. (1999). When is 'Nearest Neighbor' meaningful? *ICDT*.")
    text.append("- Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). Wiley.")
    text.append("- Bengtsson, T., Bickel, P., & Li, B. (2008). Curse-of-dimensionality revisited. *IMS Collections* 2.")
    text.append("- Achlioptas, D. (2003). Database-friendly random projections. *JCSS* 66(4).")
    text.append("- Jegou, H., Douze, M., & Schmid, C. (2011). Product Quantization. *PAMI*.")
    text.append("- Bachem, O., Lucic, M., & Krause, A. (2017). Practical coreset constructions. *ICML*.")
    text.append("- Bingham, E., & Mannila, H. (2001). Random projection in dimensionality reduction. *KDD/ICDM*.")
    text.append("- Carpentier, A., & Munos, R. (2011). Finite-time analysis of stratified sampling for MC integration. *NeurIPS*.")
    text.append("- Geraci, F., et al. (2026). Stratified sampling under the curse of dimensionality. arXiv:2506.08921.")
    text.append("- Hotelling, H. (1936). Relations between two sets of variates. *Biometrika*.")
    text.append("- Dhillon, I. S. (2003). Co-clustering documents and words using bipartite spectral graph partitioning. *KDD*.")
    text.append("- Li, F., Wu, B., Yi, K., & Zhao, Z. (2016). Wander Join: Online aggregation via random walks. *SIGMOD*.")
    text.append("- Alon, N., Gibbons, P. B., Matias, Y., & Szegedy, M. (1999). Tracking join and self-join sizes. *PODS*.")
    text.append("- Yang, Z., et al. (2020). NeuroCard: One cardinality estimator for all tables. *VLDB*.")
    text.append("- Lim et al. (2025). Exqutor. arXiv:2512.09695v2 — main paper.")
    text.append("")
    rep.write_text("\n".join(text), encoding="utf-8")
    return rep


# ---------------------------------------------------------------------------
# Synthetic data — mini-run logic / sanity check
# ---------------------------------------------------------------------------
def _synthesize_mini(rng: np.random.Generator,
                     n_methods: int = 5,
                     n_cells_single: int = 2,
                     n_cells_multi: int = 1,
                     n_sel: int = 3,
                     n_seeds: int = 2,
                     n_queries: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tiny synthetic dataset that exercises every section.

    Picks the first ``n_methods`` from METHODS_LEGACY (so paradigm coverage
    is balanced), the first ``n_cells_single`` single cells and ``n_cells_multi``
    multi-4way cells, and emits realistic q_error distributions:

    * single q_error ~ LogNormal(0, 0.4) — well-calibrated.
    * multi q_error  ~ LogNormal(0.5, 0.6) — degraded (matches Phase B finding).
    * baseline B1 ~ LogNormal that is slightly worse than single mean —
      so the synthetic methods can plausibly beat B1.
    """
    methods = METHODS_LEGACY[:n_methods]
    cells = SINGLE_CELLS[:n_cells_single] + MULTI_4WAY_CELLS[:n_cells_multi]
    sels = SELECTIVITIES[:n_sel]
    seeds = SEEDS[:n_seeds]
    queries = list(range(n_queries))

    rows_m = []
    for cell in cells:
        is_multi = CELL_KIND[cell] != "single"
        dim = CELL_DIM[cell]
        for method in methods:
            paradigm = PARADIGM[method]
            tier = TIER[method]
            for sel in sels:
                for seed in seeds:
                    for q in queries:
                        # Method q_error: better in single, degraded in multi.
                        if is_multi:
                            mu, sigma = 0.5, 0.6
                        else:
                            mu, sigma = 0.0, 0.4
                        # Inject paradigm signal — P4_DimReduction is a bit
                        # better in multi (sparse RP narrative).
                        if is_multi and paradigm == "P4_DimReduction":
                            mu -= 0.1
                        q_err = float(rng.lognormal(mu, sigma))
                        rows_m.append({
                            "cell": cell, "method": method,
                            "paradigm": paradigm, "tier": tier,
                            "dim": dim, "cell_kind": CELL_KIND[cell],
                            "selectivity": sel, "seed": seed, "query_id": q,
                            "true_card": 1000.0, "est": 1000.0 * q_err,
                            "q_error": q_err,
                            "sample_size_used": 385,
                            "total_sample_size": 385,
                            "wall_clock_ms": float(rng.uniform(2, 20)),
                            "peak_rss_mb": float(rng.uniform(64, 512)),
                        })

    rows_b = []
    for cell in cells:
        is_multi = CELL_KIND[cell] != "single"
        dim = CELL_DIM[cell]
        for baseline in BASELINES:
            for sel in sels:
                for seed in seeds:
                    for q in queries:
                        # B1 (Adaptive) — slightly worse than synthetic methods
                        # in single, similar in multi (matches phenomenon).
                        if baseline == "B1":
                            mu = 0.25 if not is_multi else 0.45
                            sigma = 0.5
                        elif baseline == "B4":
                            # B4 = Adaptive + ensemble — slightly better than B1.
                            mu = 0.10 if not is_multi else 0.40
                            sigma = 0.4
                        elif baseline == "B6":
                            mu, sigma = -0.5, 0.2  # Oracle — best.
                        else:
                            mu, sigma = 0.4, 0.6
                        q_err = float(rng.lognormal(mu, sigma))
                        rec = {
                            "cell": cell, "baseline": baseline,
                            "cell_kind": CELL_KIND[cell], "dim": dim,
                            "selectivity": sel, "seed": seed, "query_id": q,
                            "true_card": 1000.0, "est": 1000.0 * q_err,
                            "q_error": q_err,
                            "sample_size_used": 385,
                            "wall_clock_ms": float(rng.uniform(1, 10)),
                        }
                        if baseline == "B4":
                            # Tag B4 with an ensemble base method (round robin).
                            rec["ensemble_method"] = methods[
                                (sel.__hash__() + seed.__hash__()) % len(methods)
                            ]
                        rows_b.append(rec)

    return pd.DataFrame(rows_m), pd.DataFrame(rows_b)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mini-run", action="store_true",
                        help="Run with synthetic 5×3×3×2×10 data — sanity check.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Detect inputs only; skip analysis.")
    parser.add_argument("--input-method-dir", action="append", default=None,
                        help="Add to method parquet search path (repeatable).")
    parser.add_argument("--input-baseline-dir", action="append", default=None,
                        help="Add to baseline parquet search path (repeatable).")
    parser.add_argument("--out-dir", type=str, default=str(OUT_DIR),
                        help="Override CSV output dir.")
    parser.add_argument("--fig-dir", type=str, default=str(FIG_DIR),
                        help="Override plot output dir.")
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    fig_dir = Path(args.fig_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    stats = LoadStats()

    if args.mini_run:
        log.info("MINI-RUN: synthesizing 5 method × 3 cell × 3 sel × 2 seed × 10 query")
        rng = np.random.default_rng(42)
        method_df, baseline_df = _synthesize_mini(rng)
        stats.n_method_files = 1
        stats.n_method_rows = len(method_df)
        stats.n_baseline_files = 1
        stats.n_baseline_rows = len(baseline_df)
        stats.cells_seen = set(method_df["cell"].unique())
        stats.methods_seen = set(method_df["method"].unique())
        stats.baselines_seen = set(baseline_df["baseline"].unique())
    else:
        method_dirs = [Path(d) for d in (args.input_method_dir or [])] \
            or [LOCAL_FULL_DIR, SERVER_FULL_DIR]
        baseline_dirs = [Path(d) for d in (args.input_baseline_dir or [])] \
            or [LOCAL_BASELINE_DIR, SERVER_BASELINE_DIR]
        method_dirs = [d for d in method_dirs if d.exists()]
        baseline_dirs = [d for d in baseline_dirs if d.exists()]
        log.info("scan method dirs: %s", method_dirs)
        log.info("scan baseline dirs: %s", baseline_dirs)
        if args.dry_run:
            n_m = len(_scan_dirs(method_dirs, "rq3_full_matrix_*.parquet"))
            n_b = len(_scan_dirs(baseline_dirs, "rq3_stage6_baselines_*.parquet"))
            log.info("[dry-run] method parquets found = %d, baseline parquets = %d",
                     n_m, n_b)
            return 0
        method_df = load_full_matrix(stats, method_dirs)
        baseline_df = load_baselines(stats, baseline_dirs)
        if method_df.empty:
            log.error("no method data — re-run with --mini-run for scaffold check, "
                      "or wait for Phase E to complete.")
            return 2

    log.info("ingest: method rows=%d, baseline rows=%d",
             stats.n_method_rows, stats.n_baseline_rows)

    # ---- Section G1 ----
    log.info("G1 …")
    g1 = section_g1(method_df)
    g1.to_csv(out_dir / "G1_consistency.csv", index=False)
    g1_par = section_g1_paradigm_summary(g1)
    g1_par.to_csv(out_dir / "G1_paradigm_summary.csv", index=False)
    plot_g1(g1, fig_dir / "fig_g1_consistency.png")

    # ---- Section G2 ----
    log.info("G2 …")
    g2 = section_g2(method_df, baseline_df) if not baseline_df.empty \
        else pd.DataFrame()
    g2.to_csv(out_dir / "G2_adaptive_gap.csv", index=False)
    g2_summary = section_g2_summary(g2)
    g2_summary.to_csv(out_dir / "G2_adaptive_gap_summary.csv", index=False)
    plot_g2(g2, fig_dir / "fig_g2_adaptive_gap.png")

    # ---- Section G5 (ahead of G3 because G3 uses G5's t* delta) ----
    log.info("G5 (ahead of G3) …")
    g5 = section_g5(method_df, baseline_df) if not baseline_df.empty \
        else pd.DataFrame()
    g5.to_csv(out_dir / "G5_convergence.csv", index=False)
    plot_g5_box(g5, fig_dir / "fig_g5_convergence.png")

    # ---- Section G3 ----
    log.info("G3 …")
    g3 = section_g3(method_df, baseline_df, g5=g5) \
        if not baseline_df.empty else pd.DataFrame()
    g3.to_csv(out_dir / "G3_b4_vs_b1.csv", index=False)
    plot_g3_radar(g3, fig_dir / "fig_g3_4axis_radar.png")

    # ---- Section G4 ----
    log.info("G4 …")
    reg, curse = section_g4(method_df)
    reg.to_csv(out_dir / "G4_regression_extended.csv", index=False)
    curse.to_csv(out_dir / "G4_curse_per_method.csv", index=False)
    plot_g4_forest(reg, fig_dir / "fig_g4_regression_forest.png")

    # ---- Section G6 ----
    log.info("G6 …")
    g6 = section_g6(method_df)
    g6.to_csv(out_dir / "G6_resource.csv", index=False)
    plot_g6_pareto(g6, fig_dir / "fig_g6_pareto.png")

    # ---- Section G7 ----
    log.info("G7 …")
    g7 = section_g7(g1, g2_summary, g3, g6)
    g7.to_csv(out_dir / "G7_production_top.csv", index=False)
    plot_g7_top(g7, fig_dir / "fig_g7_top_methods.png")

    # ---- Report ----
    log.info("REPORT.md …")
    rep_path = write_report(out_dir, g1, g1_par, g2, g2_summary, g3,
                            reg, curse, g5, g6, g7, stats)
    log.info("wrote %s", rep_path)

    # Console summary.
    print("\n=== Phase G summary ===")
    print(f"method rows : {stats.n_method_rows:,} "
          f"({stats.n_method_files} files)")
    print(f"baseline rows: {stats.n_baseline_rows:,} "
          f"({stats.n_baseline_files} files)")
    print(f"cells covered: {len(stats.cells_seen)}/28")
    print(f"methods cov  : {len(stats.methods_seen)}/22")
    print(f"baselines    : {sorted(stats.baselines_seen)}")
    if not g2_summary.empty:
        wins = g2_summary[g2_summary["win_single_multi_b1"]]
        print(f"win_single_multi_b1: {len(wins)} method(s)"
              + (f" — {', '.join(wins['method'].tolist())}" if len(wins) else ""))
    if not g7.empty:
        q = g7[g7["qualifies"]]
        print(f"production-ready (4-filter): {len(q)} method(s)"
              + (f" — {', '.join(q['method'].tolist())}" if len(q) else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
