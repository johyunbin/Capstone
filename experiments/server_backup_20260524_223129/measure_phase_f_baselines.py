#!/usr/bin/env python3
"""
Phase F — Stage VI baseline portfolio measurement (B1 ~ B6 × 28 cell).

Companion to ``measure_multi_paradigm.py`` (Phase E full matrix). Phase F
isolates the 6 reference baselines so the analysis pipeline can compute
``Δ%`` of every Phase E method against each baseline within a paired
(cell × selectivity × seed × query_id) grid.

The 6 baselines (design doc § 6, ``plans/RQ재정립_v7_evidence_20260509_1820.md``):

==  ===========================  =========================================  ================================
#   Baseline                     Estimator                                  Role
==  ===========================  =========================================  ================================
B1  Adaptive Sampling (Exqutor)  Bernoulli HT with momentum-driven N_t      ★ primary head-to-head reference
B2  BERN N=385 fixed             Bernoulli HT with fixed N=385              sanity lower bound
B3  Fixed-K=20 stratified        KM20 oracle stratify + proportional alloc  RQ3 W1 reference (reuse W1 csv)
B4  Adaptive + ensemble (NEW)    KM20 stratify + Adaptive dynamic budget    ★ v7 contribution
B5  Uniform random matched       Bernoulli HT with budget = B1's N_t        budget-controlled lower bound
B6  Oracle KM20 + Neyman         KM20 stratify + Neyman optimal allocation  upper bound (oracle σ_h)
==  ===========================  =========================================  ================================

The output schema is unified across ``cell_kind`` so that downstream analysis
can ``concat`` all baselines:

    columns: cell, cell_kind, baseline, selectivity, seed, query_id,
             true_card, est, q_error,
             sample_size_used, sample_size_total, wall_clock_ms,
             # cell-kind specific D columns are kept in extra dict serialized
             # to JSON or stored as separate D1_target / D2_target

Reuse policy
------------
* B1 — re-implements the *single-cell* AdaptiveState (식 1~6) from
  ``run_adaptive_sampling.py`` and the *multi-cell* per-table state from
  ``measure_multi_adaptive_sampling.py``.  When the W1 sprint produced an
  Adaptive parquet/csv that already covers a (cell, B1) pair we **skip**
  recomputation (``--skip-existing`` is the default).
* B2 — fixed Bernoulli (size=385).  Reuses ``bernoulli_estimate`` from
  ``_measure_common.py`` (single) and ``bernoulli_estimate_dual`` from
  ``measure_multi_vector.py`` (multi).
* B3 — when a W1 5-mode parquet (``rq2_*5mode_*``) or the legacy
  ``rq3_<DS>_sf<sf>_proportional`` parquet already contains the cell, the
  script copies the rows over with ``baseline=B3`` and skips recomputation.
* B4 — wraps ``measure_multi_ensemble.AdaptiveState`` and applies a KM20
  stratification with proportional allocation that is dynamically rescaled
  to the Adaptive S_t every query.  When the matching ensemble csv already
  exists we slice ``mode='ensemble_KM20'`` rows directly.
* B5 — re-uses the per-query ``sample_size_used`` series produced by B1
  (joined on cell × selectivity × seed × query_id) and runs uniform random
  Bernoulli at the same per-query budget.  Requires B1 to be measured
  first; the script enforces this dependency.
* B6 — stratify by KM20 (oracle), allocate by Neyman (σ_h proportional)
  with the σ_h estimated via the cached cluster samples.  This is the
  oracle upper bound used in recovery rate.

Multi-axis contribution metrics (computed at analysis time but the schema
is laid out so each baseline csv carries the raw measurements that the
analysis script needs):

* **accuracy** — ``q_error`` per row → paired Wilcoxon vs B1
* **convergence speed** — ``sample_size_used`` per row → ``t* = first query
  where |S_t - S_∞| < 5%``
* **resource** — ``wall_clock_ms`` aggregated per (cell, baseline, sel,
  seed) → median wall-clock per query
* **rare-query accuracy** — ``selectivity == 0.01`` filter → q_error mean
  on the rare slice

CLI
---

    python3 _internal/scripts/measure_phase_f_baselines.py \
        --cells DEEP_sf1 DEEP_sf10 \
        --baselines B1 B2 B6 \
        --dry-run

    # Mini-run on the server (1 cell, 3 query, B1+B2)
    python3 _internal/scripts/measure_phase_f_baselines.py \
        --cells DEEP_sf1 \
        --baselines B1 B2 \
        --num-queries 3 --num-seeds 1 --selectivity 0.10 \
        --out-dir /tmp/phase_f_mini

    # Full Phase F (server)
    nohup python3 -u /mnt/hdd0/home/capstone2026/cache/rq3/measure_phase_f_baselines.py \
        --cells $(cat 28cell.list) --baselines B1 B2 B3 B4 B5 B6 \
        > /mnt/hdd0/home/capstone2026/logs/phase_f_$(date +%Y%m%d_%H%M).log 2>&1 &
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Logging — production-ready (one logger, KST timestamps)
# ---------------------------------------------------------------------------

KST_TZ = timezone(timedelta(hours=9))


def kst() -> str:
    return datetime.now(KST_TZ).strftime("%H:%M:%S")


class KSTFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.kst = kst()
        return super().format(record)


_handler = logging.StreamHandler()
_handler.setFormatter(KSTFormatter("[%(kst)s] %(levelname)s %(message)s"))
log = logging.getLogger("phase_f")
log.setLevel(logging.INFO)
if not log.handlers:
    log.addHandler(_handler)


# ---------------------------------------------------------------------------
# Path setup — server first, local fallback (for dry-run / unit tests)
# ---------------------------------------------------------------------------

ROOT_SERVER = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
ROOT_LOCAL_RQ3 = Path("/Users/hyunbin/Capstone/experiments/code/rq3")
ROOT_RQ3 = ROOT_SERVER if ROOT_SERVER.exists() else ROOT_LOCAL_RQ3
sys.path.insert(0, str(ROOT_RQ3))

SCRIPTS_PATH = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_PATH))


# ---------------------------------------------------------------------------
# Constants — must match _measure_common / measure_multi_vector exactly
# ---------------------------------------------------------------------------

SEEDS: list[float] = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES: list[float] = [0.01, 0.05, 0.10, 0.30, 0.50]
SAMPLE_SIZE: int = 385
N_STRATA: int = 20
CACHE_PER_CLUSTER: int = 500
N_QUERIES_DEFAULT: int = 100

# Adaptive Sampling hyperparameters (Exqutor §VI exact values)
ADAPTIVE_HP = {
    "momentum": 0.9,
    "learning_rate": 0.1,
    "alpha": 50.0,
    "beta": 1.5,
    "gamma": 0.99,
    "update_period": 50,
    "min_size": 50,
    "max_size": 5000,
}

ALL_BASELINES: tuple[str, ...] = ("B1", "B2", "B3", "B4", "B5", "B6")


# ---------------------------------------------------------------------------
# 28-cell portfolio (design doc § 5) — single 12 + multi-4way 8 + multi-join 8
# ---------------------------------------------------------------------------

# Single-cell config — mirrors run_adaptive_sampling.CELLS but flat name keys.
# pk_col is irrelevant for Phase F (we only need vectors + query pool).
SINGLE_DATASETS = ("DEEP", "SIFT", "FB", "SSN", "WIKI", "YFCC")
SINGLE_SFS = (1, 10)


def _single_table(ds: str, sf: int) -> dict:
    base = {
        "DEEP": ("partsupp_deep_{sf}", "ps_embedding", 96),
        "SIFT": ("partsupp_sift_{sf}", "ps_embedding", 128),
        "FB":   ("partsupp_fb_{sf}",   "ps_embedding", 256),
        "SSN":  ("partsupp_fb_{sf}",   "ps_embedding", 256),  # FB == SSN alias
        "WIKI": ("partsupp_wiki_{sf}", "ps_embedding", 768),
        "YFCC": ("partsupp_yfcc_{sf}", "ps_embedding", 192),
    }[ds]
    table = base[0].format(sf=sf)
    return {
        "kind": "single",
        "name": f"{ds}_sf{sf}",
        "ds": ds,
        "sf": sf,
        "table": table,
        "embed_col": base[1],
        "vec_dim": base[2],
    }


CELLS_SINGLE: dict[str, dict] = {
    f"{ds}_sf{sf}": _single_table(ds, sf)
    for ds in SINGLE_DATASETS for sf in SINGLE_SFS
}

# Multi-4way cells (partsupp_<image>_wiki_<sf>) — 4 image × 2 sf = 8.
# Schema: emb1 = image_dim, emb2 = wiki 768. Cells already documented in
# build_new_multi_cells.py.
_4WAY_IMG = (("deep", 96), ("sift", 128), ("fb", 256), ("yfcc", 192))


def _4way_cell(img: str, dim: int, sf: int) -> dict:
    return {
        "kind": "4way",
        "name": f"partsupp_{img}_wiki_{sf}",
        "table": f"partsupp_{img}_wiki_{sf}",
        "emb1_col": f"ps_embedding_{img}",
        "emb1_dim": dim,
        "emb2_col": "ps_embedding_wiki",
        "emb2_dim": 768,
    }


CELLS_4WAY: dict[str, dict] = {
    f"partsupp_{img}_wiki_{sf}": _4way_cell(img, dim, sf)
    for img, dim in _4WAY_IMG for sf in SINGLE_SFS
}

# Multi-join cells (partsupp_<image>_<sf> ⨝ part_wiki_<sf>) — 4 × 2 = 8.


def _join_cell(img: str, dim: int, sf: int) -> dict:
    return {
        "kind": "join",
        "name": f"multi_join_{img}_wiki_{sf}",
        "partsupp_table": f"partsupp_{img}_{sf}",
        "part_table": f"part_wiki_{sf}",
        "partsupp_emb_col": "ps_embedding",
        "partsupp_emb_dim": dim,
        "part_emb_col": "p_embedding",
        "part_emb_dim": 768,
    }


CELLS_JOIN: dict[str, dict] = {
    f"multi_join_{img}_wiki_{sf}": _join_cell(img, dim, sf)
    for img, dim in _4WAY_IMG for sf in SINGLE_SFS
}

ALL_CELLS: dict[str, dict] = {**CELLS_SINGLE, **CELLS_4WAY, **CELLS_JOIN}
assert len(ALL_CELLS) == 28, (
    f"Phase F expects 28 cells, got {len(ALL_CELLS)} — check portfolio definitions."
)


# ---------------------------------------------------------------------------
# AdaptiveState — exact replica of run_adaptive_sampling.AdaptiveState (식 1~6)
# ---------------------------------------------------------------------------

@dataclass
class AdaptiveState:
    """Exqutor §V-B Adaptive Sampling state — line-by-line same as
    ``run_adaptive_sampling.AdaptiveState``.  Replicated here to avoid a
    hard import dependency on the server-only ``run_adaptive_sampling``
    module so the dry-run / mini-run modes work locally.
    """

    sample_size: float = float(SAMPLE_SIZE)
    velocity: float = 0.0
    learning_rate: float = ADAPTIVE_HP["learning_rate"]
    momentum: float = ADAPTIVE_HP["momentum"]
    alpha: float = ADAPTIVE_HP["alpha"]
    beta: float = ADAPTIVE_HP["beta"]
    gamma: float = ADAPTIVE_HP["gamma"]
    update_period: int = ADAPTIVE_HP["update_period"]
    min_size: int = ADAPTIVE_HP["min_size"]
    max_size: int = ADAPTIVE_HP["max_size"]
    n_total: int = 0
    qerror_window: list = field(default_factory=list)

    def step(self, qerror: Optional[float]) -> int:
        self.n_total += 1
        if qerror is not None and np.isfinite(qerror):
            self.qerror_window.append(float(qerror))
        if self.n_total % self.update_period == 0 and self.qerror_window:
            mean_qe = float(np.mean(self.qerror_window))
            sampling_ratio = self.sample_size / max(self.max_size, 1)
            delta = self.alpha * (mean_qe - self.beta) - (
                100.0 - self.alpha) * sampling_ratio
            self.velocity = self.momentum * self.velocity + self.learning_rate * delta
            self.sample_size = float(np.clip(
                self.sample_size + self.velocity, self.min_size, self.max_size,
            ))
            self.learning_rate = self.gamma * self.learning_rate
            self.qerror_window.clear()
        return int(round(self.sample_size))


# ---------------------------------------------------------------------------
# Estimators — re-implemented locally so dry-run does not require psycopg
# ---------------------------------------------------------------------------

def _bernoulli_single(
    all_vecs: np.ndarray, qvec: np.ndarray, D: float,
    sample_size: int, rng: np.random.Generator,
) -> tuple[float, int, int]:
    """Single-cell Bernoulli HT estimator. Returns (est, hits, s_used)."""
    n = all_vecs.shape[0]
    s = max(1, min(int(sample_size), n))
    idxs = rng.choice(n, size=s, replace=False)
    sub = all_vecs[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return float(hits) * (n / s), hits, s


def _bernoulli_dual(
    vec1: np.ndarray, vec2: np.ndarray,
    q1v: np.ndarray, q2v: np.ndarray, D1: float, D2: float,
    sample_size: int, rng: np.random.Generator,
) -> tuple[float, int, int]:
    """Multi-cell joint Bernoulli HT estimator (paired AND).

    Following Exqutor's per-table separate-state operating mode, each
    multi-cell row is a single sample unit (vec1[i] paired with vec2[i]).
    The estimator counts rows where BOTH conditions hold and applies the
    HT extrapolation factor n / s.
    """
    n = vec1.shape[0]
    s = max(1, min(int(sample_size), n))
    idxs = rng.choice(n, size=s, replace=False)
    sub1 = vec1[idxs]
    sub2 = vec2[idxs]
    d1 = np.linalg.norm(sub1 - q1v, axis=1)
    d2 = np.linalg.norm(sub2 - q2v, axis=1)
    hits = int(((d1 < D1) & (d2 < D2)).sum())
    return float(hits) * (n / s), hits, s


def _stratified_single(
    samples: dict[int, np.ndarray], sizes: dict[int, int],
    alloc: np.ndarray, qvec: np.ndarray, D: float,
    rng: np.random.Generator, n_strata: int = N_STRATA,
) -> tuple[float, int]:
    """Single-cell stratified HT.  Returns (est, total_used)."""
    est = 0.0
    used = 0
    for sid in range(n_strata):
        cache = samples[sid]
        n_cache = cache.shape[0]
        s_i = min(int(alloc[sid]), n_cache)
        if s_i < 1:
            s_i = 1
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub = cache[idxs]
        d = np.linalg.norm(sub - qvec, axis=1)
        hits = int((d < D).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
        used += s_i
    return est, used


def _stratified_dual(
    s1: dict[int, np.ndarray], s2: dict[int, np.ndarray],
    sizes: dict[int, int], alloc: np.ndarray,
    q1v: np.ndarray, q2v: np.ndarray, D1: float, D2: float,
    rng: np.random.Generator, n_strata: int = N_STRATA,
) -> tuple[float, int]:
    """Multi-cell stratified HT (paired AND).  Returns (est, total_used)."""
    est = 0.0
    used = 0
    for sid in range(n_strata):
        cache1 = s1[sid]
        cache2 = s2[sid]
        n_cache = cache1.shape[0]
        s_i = min(int(alloc[sid]), n_cache)
        if s_i < 1:
            s_i = 1
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub1 = cache1[idxs]
        sub2 = cache2[idxs]
        d1 = np.linalg.norm(sub1 - q1v, axis=1)
        d2 = np.linalg.norm(sub2 - q2v, axis=1)
        hits = int(((d1 < D1) & (d2 < D2)).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
        used += s_i
    return est, used


# ---------------------------------------------------------------------------
# Allocation strategies
# ---------------------------------------------------------------------------

def _proportional_alloc(sizes: dict[int, int], budget: int,
                          n_strata: int = N_STRATA) -> np.ndarray:
    sz = np.array([sizes.get(j, 0) for j in range(n_strata)], dtype=float)
    if sz.sum() <= 0:
        base = budget // n_strata
        extra = budget - base * n_strata
        out = np.full(n_strata, base, dtype=int)
        out[:extra] += 1
        return np.maximum(out, 1)
    f = sz / sz.sum() * budget
    s = np.maximum(f.astype(int), 1)
    extra = budget - int(s.sum())
    if extra > 0:
        frac = f - f.astype(int)
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


def _neyman_alloc(
    sizes: dict[int, int], sigmas: dict[int, float],
    budget: int, n_strata: int = N_STRATA,
) -> np.ndarray:
    """Neyman optimal allocation: s_h ∝ N_h × σ_h.

    Falls back to proportional when ``σ_h`` is unknown / zero everywhere.
    """
    weights = np.array([
        sizes.get(j, 0) * sigmas.get(j, 0.0) for j in range(n_strata)
    ], dtype=float)
    if weights.sum() <= 0:
        return _proportional_alloc(sizes, budget, n_strata=n_strata)
    f = weights / weights.sum() * budget
    s = np.maximum(f.astype(int), 1)
    extra = budget - int(s.sum())
    if extra > 0:
        frac = f - f.astype(int)
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


def _estimate_cluster_sigma(
    samples: dict[int, np.ndarray], qvec: np.ndarray, D: float,
    n_strata: int = N_STRATA,
) -> dict[int, float]:
    """Approximate σ_h for Neyman allocation using the cached cluster samples.

    σ_h is the (sample) standard deviation of the indicator ``1[d < D]``
    over the cached subset; this is exactly the σ used in stratified
    Bernoulli (Cochran 1977 §5A.6).
    """
    sigmas: dict[int, float] = {}
    for sid in range(n_strata):
        cache = samples[sid]
        if cache.shape[0] == 0:
            sigmas[sid] = 0.0
            continue
        d = np.linalg.norm(cache - qvec, axis=1)
        ind = (d < D).astype(np.float32)
        sigmas[sid] = float(ind.std(ddof=0))
    return sigmas


def _estimate_cluster_sigma_dual(
    s1: dict[int, np.ndarray], s2: dict[int, np.ndarray],
    q1v: np.ndarray, q2v: np.ndarray, D1: float, D2: float,
    n_strata: int = N_STRATA,
) -> dict[int, float]:
    sigmas: dict[int, float] = {}
    for sid in range(n_strata):
        cache1 = s1[sid]
        cache2 = s2[sid]
        if cache1.shape[0] == 0:
            sigmas[sid] = 0.0
            continue
        d1 = np.linalg.norm(cache1 - q1v, axis=1)
        d2 = np.linalg.norm(cache2 - q2v, axis=1)
        ind = ((d1 < D1) & (d2 < D2)).astype(np.float32)
        sigmas[sid] = float(ind.std(ddof=0))
    return sigmas


# ---------------------------------------------------------------------------
# Lazy server-side imports — keep dry-run independent of psycopg / sklearn
# ---------------------------------------------------------------------------

def _lazy_imports_single():
    """Return helpers for single-cell measurement.

    Imports ``_measure_common`` (psycopg-dependent) and
    ``run_adaptive_sampling`` (single-cell dataset entry).  The function
    is only called from ``measure_cell_single`` which is itself never
    invoked under ``--dry-run``.
    """
    import _measure_common as mc
    from _measure_common import (
        fetch_all_vectors_safe, cache_cluster_samples_inmem,
    )
    from run_adaptive_sampling import build_dataset_entry
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("pyarrow required for query_pool parquet read") from exc
    return {
        "mc": mc,
        "fetch_all_vectors_safe": fetch_all_vectors_safe,
        "cache_cluster_samples_inmem": cache_cluster_samples_inmem,
        "build_dataset_entry": build_dataset_entry,
        "pq": pq,
    }


def _lazy_imports_multi():
    """Return helpers for multi-cell (4way / join) measurement."""
    from measure_multi_vector import (
        fetch_dual_vectors, build_query_pool, cache_dual_samples,
    )
    from measure_multi_table_join import (
        fetch_partsupp, fetch_part, build_join,
        build_query_pool as build_query_pool_join,
        cache_dual_samples as cache_dual_samples_join,
    )
    return {
        "fetch_dual_vectors": fetch_dual_vectors,
        "build_query_pool": build_query_pool,
        "cache_dual_samples": cache_dual_samples,
        "fetch_partsupp": fetch_partsupp,
        "fetch_part": fetch_part,
        "build_join": build_join,
        "build_query_pool_join": build_query_pool_join,
        "cache_dual_samples_join": cache_dual_samples_join,
    }


def _seed_int(seed: float) -> int:
    return int(seed * 10**9) % (2**31 - 1)


# ---------------------------------------------------------------------------
# Reuse — slice existing parquet/csv when available
# ---------------------------------------------------------------------------

def _existing_b1_path_single(cell: dict) -> Optional[Path]:
    """Path to existing single-cell B1 (Adaptive) parquet if present."""
    cache = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
    candidate = cache / f"rq3_{cell['ds']}_sf{cell['sf']}_adaptive.parquet"
    return candidate if candidate.exists() else None


def _existing_b3_path_single(cell: dict) -> Optional[Path]:
    """W1 5-mode parquet that contains the proportional/equal column."""
    cache = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
    candidate = cache / f"rq3_{cell['ds']}_sf{cell['sf']}_proportional.parquet"
    if candidate.exists():
        return candidate
    return None


def _existing_b3_path_multi(cell: dict) -> Optional[Path]:
    """W1 multi 5-mode parquet for 4way / join cells (rq2_multi_5mode_*)."""
    for root in (ROOT_SERVER, Path("/Users/hyunbin/Capstone/_internal/cache/rq3")):
        # Tag changes with cell name conventions used in W1
        legacy_name = cell["name"].replace("partsupp_", "")
        for stem in (cell["name"], legacy_name):
            candidate = root / f"rq2_multi_5mode_{stem}.parquet"
            if candidate.exists():
                return candidate
    return None


def _existing_b4_path_multi(cell: dict) -> Optional[Path]:
    """Existing multi_ensemble csv slice (mode='ensemble_KM20' if present)."""
    for root in (ROOT_SERVER, Path("/Users/hyunbin/Capstone/_internal/cache/rq3")):
        candidate = root / "multi_ensemble" / f"multi_ensemble_{cell['name']}.csv"
        if candidate.exists():
            return candidate
    return None


def _slice_b3_from_w1(parquet_path: Path, cell: dict, *,
                       num_queries: int) -> list[dict]:
    """Slice the W1 ``proportional`` rows (single-cell) into Phase F schema.

    The W1 parquet uses ``mode`` = 'proportional' or 'km20_prop'; both
    are equivalent KM20 + proportional allocation runs for B3.
    """
    df = pd.read_parquet(parquet_path)
    keep_modes = {"proportional", "km20_prop", "km20"}
    df = df[df["mode"].isin(keep_modes)].copy()
    if df.empty:
        return []
    df = df[df["query_id"] < num_queries]
    rows: list[dict] = []
    for r in df.itertuples(index=False):
        rows.append({
            "cell": cell["name"],
            "cell_kind": cell["kind"],
            "baseline": "B3",
            "selectivity": float(r.selectivity),
            "seed": float(r.seed),
            "query_id": int(r.query_id),
            "true_card": int(r.true_card),
            "est": float(r.est),
            "q_error": (float(r.q_error)
                        if (r.q_error is not None
                            and np.isfinite(float(r.q_error))) else None),
            "sample_size_used": int(SAMPLE_SIZE),
            "sample_size_total": int(SAMPLE_SIZE),
            "wall_clock_ms": float("nan"),
            "D1_target": float(getattr(r, "D_target", float("nan"))),
            "D2_target": float("nan"),
            "reused_from": str(parquet_path),
        })
    return rows


# ---------------------------------------------------------------------------
# Single-cell measurement
# ---------------------------------------------------------------------------

def _load_single_cell(cell: dict, helpers: dict, num_queries: int):
    """Fetch all vectors + KM20 sids + query pool + selectivity table."""
    DS = helpers["build_dataset_entry"](cell["ds"], cell["sf"])
    helpers["mc"].DATASETS = [DS]
    log.info("single fetch: cell=%s table=%s dim=%d",
             cell["name"], DS["table"], DS["vec_dim"])
    all_vecs, km20_sids = helpers["fetch_all_vectors_safe"](DS)
    qp = helpers["pq"].read_table(DS["query_pool"]).to_pandas().reset_index(drop=True)
    qs_full = helpers["pq"].read_table(DS["query_sel"]).to_pandas()
    qvecs = np.stack([
        np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
        for i in range(len(qp))
    ])
    log.info("single loaded: N=%d dim=%d, |query|=%d",
             all_vecs.shape[0], all_vecs.shape[1], len(qp))
    return all_vecs, km20_sids, qvecs, qs_full


def _measure_b1_single(
    cell: dict, all_vecs: np.ndarray, qvecs: np.ndarray,
    qs_full: pd.DataFrame, *, selectivities, seeds, num_queries,
) -> list[dict]:
    """B1 — Exqutor Adaptive Sampling on single cell."""
    out: list[dict] = []
    n_total = all_vecs.shape[0]
    state_kwargs = dict(ADAPTIVE_HP)
    state_kwargs["max_size"] = min(state_kwargs["max_size"], n_total)
    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel))
            & (qs_full["query_id"] < num_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if qs_sel.empty:
            continue
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            state = AdaptiveState(**state_kwargs)
            s_next = SAMPLE_SIZE
            for r in qs_sel.itertuples(index=False):
                qid = int(r.query_id)
                D = float(r.D_target)
                tc = int(r.true_cardinality)
                qvec = qvecs[qid]
                t0 = time.perf_counter()
                est, _, used = _bernoulli_single(all_vecs, qvec, D, s_next, rng)
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": "single",
                    "baseline": "B1", "selectivity": sel, "seed": seed,
                    "query_id": qid, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": used,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D, "D2_target": float("nan"),
                    "reused_from": "",
                })
                s_next = state.step(qerr)
    return out


def _measure_b2_single(
    cell: dict, all_vecs: np.ndarray, qvecs: np.ndarray,
    qs_full: pd.DataFrame, *, selectivities, seeds, num_queries,
) -> list[dict]:
    """B2 — fixed BERN N=385 on single cell."""
    out: list[dict] = []
    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel))
            & (qs_full["query_id"] < num_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if qs_sel.empty:
            continue
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            for r in qs_sel.itertuples(index=False):
                qid = int(r.query_id)
                D = float(r.D_target)
                tc = int(r.true_cardinality)
                qvec = qvecs[qid]
                t0 = time.perf_counter()
                est, _, used = _bernoulli_single(
                    all_vecs, qvec, D, SAMPLE_SIZE, rng,
                )
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": "single",
                    "baseline": "B2", "selectivity": sel, "seed": seed,
                    "query_id": qid, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": SAMPLE_SIZE,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D, "D2_target": float("nan"),
                    "reused_from": "",
                })
    return out


def _measure_b3_single(
    cell: dict, samples: dict, sizes: dict,
    qvecs: np.ndarray, qs_full: pd.DataFrame, *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    """B3 — KM20 stratify + proportional allocation."""
    alloc = _proportional_alloc(sizes, SAMPLE_SIZE)
    out: list[dict] = []
    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel))
            & (qs_full["query_id"] < num_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if qs_sel.empty:
            continue
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            for r in qs_sel.itertuples(index=False):
                qid = int(r.query_id)
                D = float(r.D_target)
                tc = int(r.true_cardinality)
                qvec = qvecs[qid]
                t0 = time.perf_counter()
                est, used = _stratified_single(samples, sizes, alloc, qvec, D, rng)
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": "single",
                    "baseline": "B3", "selectivity": sel, "seed": seed,
                    "query_id": qid, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used,
                    "sample_size_total": int(alloc.sum()),
                    "wall_clock_ms": wall_ms,
                    "D1_target": D, "D2_target": float("nan"),
                    "reused_from": "",
                })
    return out


def _measure_b4_single(
    cell: dict, samples: dict, sizes: dict,
    qvecs: np.ndarray, qs_full: pd.DataFrame, *,
    selectivities, seeds, num_queries, n_total: int,
) -> list[dict]:
    """B4 — KM20 stratify + Adaptive dynamic budget (proportional rescaled)."""
    out: list[dict] = []
    state_kwargs = dict(ADAPTIVE_HP)
    state_kwargs["max_size"] = min(state_kwargs["max_size"], n_total)
    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel))
            & (qs_full["query_id"] < num_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if qs_sel.empty:
            continue
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            state = AdaptiveState(**state_kwargs)
            for r in qs_sel.itertuples(index=False):
                qid = int(r.query_id)
                D = float(r.D_target)
                tc = int(r.true_cardinality)
                qvec = qvecs[qid]
                t0 = time.perf_counter()
                budget = int(round(state.sample_size))
                alloc = _proportional_alloc(sizes, budget)
                est, used = _stratified_single(samples, sizes, alloc, qvec, D, rng)
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": "single",
                    "baseline": "B4", "selectivity": sel, "seed": seed,
                    "query_id": qid, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": budget,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D, "D2_target": float("nan"),
                    "reused_from": "",
                })
                state.step(qerr)
    return out


def _measure_b5_single(
    cell: dict, all_vecs: np.ndarray, qvecs: np.ndarray,
    b1_rows: list[dict], qs_full: pd.DataFrame, *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    """B5 — uniform random Bernoulli with B1's per-query budget."""
    if not b1_rows:
        log.warning("B5 single skipped: B1 must be measured first to "
                     "supply per-query budgets.")
        return []
    b1_lookup = {
        (r["selectivity"], r["seed"], r["query_id"]): r["sample_size_used"]
        for r in b1_rows
    }
    out: list[dict] = []
    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel))
            & (qs_full["query_id"] < num_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if qs_sel.empty:
            continue
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed) ^ 0x5B5B5B5B)
            for r in qs_sel.itertuples(index=False):
                qid = int(r.query_id)
                D = float(r.D_target)
                tc = int(r.true_cardinality)
                qvec = qvecs[qid]
                budget = b1_lookup.get((sel, seed, qid), SAMPLE_SIZE)
                t0 = time.perf_counter()
                est, _, used = _bernoulli_single(all_vecs, qvec, D, budget, rng)
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": "single",
                    "baseline": "B5", "selectivity": sel, "seed": seed,
                    "query_id": qid, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": budget,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D, "D2_target": float("nan"),
                    "reused_from": "",
                })
    return out


def _measure_b6_single(
    cell: dict, samples: dict, sizes: dict,
    qvecs: np.ndarray, qs_full: pd.DataFrame, *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    """B6 — KM20 oracle stratify + Neyman optimal allocation per query."""
    out: list[dict] = []
    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel))
            & (qs_full["query_id"] < num_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if qs_sel.empty:
            continue
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed) ^ 0xDEADBEEF)
            for r in qs_sel.itertuples(index=False):
                qid = int(r.query_id)
                D = float(r.D_target)
                tc = int(r.true_cardinality)
                qvec = qvecs[qid]
                t0 = time.perf_counter()
                sigmas = _estimate_cluster_sigma(samples, qvec, D)
                alloc = _neyman_alloc(sizes, sigmas, SAMPLE_SIZE)
                est, used = _stratified_single(samples, sizes, alloc, qvec, D, rng)
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": "single",
                    "baseline": "B6", "selectivity": sel, "seed": seed,
                    "query_id": qid, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used,
                    "sample_size_total": int(alloc.sum()),
                    "wall_clock_ms": wall_ms,
                    "D1_target": D, "D2_target": float("nan"),
                    "reused_from": "",
                })
    return out


def measure_cell_single(
    cell: dict, baselines: list[str], *,
    selectivities: list[float], seeds: list[float],
    num_queries: int, skip_existing: bool,
) -> list[dict]:
    helpers = _lazy_imports_single()
    all_vecs, km20_sids, qvecs, qs_full = _load_single_cell(
        cell, helpers, num_queries,
    )
    samples, sizes = helpers["mc"].cache_cluster_samples_inmem(
        all_vecs, km20_sids,
    )
    b1_rows: list[dict] = []
    rows: list[dict] = []

    for b in baselines:
        log.info("[%s] cell=%s baseline=%s start", cell["kind"], cell["name"], b)
        t0 = time.time()
        if b == "B1":
            sub = _measure_b1_single(
                cell, all_vecs, qvecs, qs_full,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
            b1_rows = sub
        elif b == "B2":
            sub = _measure_b2_single(
                cell, all_vecs, qvecs, qs_full,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
        elif b == "B3":
            reuse = _existing_b3_path_single(cell)
            if reuse is not None and skip_existing:
                log.info("[B3] reusing %s", reuse)
                sub = _slice_b3_from_w1(reuse, cell, num_queries=num_queries)
            else:
                sub = _measure_b3_single(
                    cell, samples, sizes, qvecs, qs_full,
                    selectivities=selectivities, seeds=seeds,
                    num_queries=num_queries,
                )
        elif b == "B4":
            sub = _measure_b4_single(
                cell, samples, sizes, qvecs, qs_full,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries, n_total=all_vecs.shape[0],
            )
        elif b == "B5":
            sub = _measure_b5_single(
                cell, all_vecs, qvecs, b1_rows, qs_full,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
        elif b == "B6":
            sub = _measure_b6_single(
                cell, samples, sizes, qvecs, qs_full,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
        else:
            raise ValueError(f"unsupported baseline: {b}")
        log.info("[%s] %s done %d rows in %.1fs",
                  cell["name"], b, len(sub), time.time() - t0)
        rows.extend(sub)

    return rows


# ---------------------------------------------------------------------------
# Multi-cell (4way / join) measurement
# ---------------------------------------------------------------------------

def _load_multi_cell(cell: dict, helpers: dict, num_queries: int):
    """Return (vec1, vec2, qids, q1, q2, D1_by_sel, D2_by_sel, true_card)."""
    if cell["kind"] == "4way":
        emb1, emb2 = helpers["fetch_dual_vectors"](
            cell["table"], cell["emb1_col"], cell["emb2_col"],
            cell["emb1_dim"], cell["emb2_dim"],
        )
        qids, q1, q2, D1, D2, tc = helpers["build_query_pool"](
            emb1, emb2, n_queries=num_queries,
        )
        return emb1, emb2, qids, q1, q2, D1, D2, tc
    # join
    ps_emb, ps_keys = helpers["fetch_partsupp"](
        cell["partsupp_table"], cell["partsupp_emb_col"],
        cell["partsupp_emb_dim"],
    )
    p_emb, p_keys = helpers["fetch_part"](
        cell["part_table"], cell["part_emb_col"], cell["part_emb_dim"],
    )
    deep_join, wiki_join = helpers["build_join"](ps_emb, ps_keys, p_emb, p_keys)
    qids, q1, q2, D1, D2, tc = helpers["build_query_pool_join"](
        deep_join, wiki_join, n_queries=num_queries,
    )
    return deep_join, wiki_join, qids, q1, q2, D1, D2, tc


def _km20_assign_multi(vec1: np.ndarray, vec2: np.ndarray,
                        learn_frac: float, learn_seed: int) -> np.ndarray:
    """KM20 oracle stratification on the norm-aware concat of (emb1, emb2).

    Mirrors ``measure_multi_paradigm.build_concat`` and uses
    sklearn.MiniBatchKMeans which is the W1 reference (KM20 oracle).
    """
    from sklearn.cluster import MiniBatchKMeans
    n1 = float(np.linalg.norm(vec1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(vec2, axis=1).mean()) or 1.0
    concat = np.concatenate([vec1 / n1, vec2 / n2], axis=1).astype(np.float32)
    n = concat.shape[0]
    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    rng = np.random.default_rng(learn_seed)
    idx = rng.choice(n, size=min(n_learn, n), replace=False)
    learn = concat[idx]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        km = MiniBatchKMeans(
            n_clusters=N_STRATA, batch_size=1000, random_state=learn_seed,
        ).fit(learn)
    sids = km.predict(concat).astype(np.int32)
    return sids


def _measure_b1_multi(
    cell: dict, vec1: np.ndarray, vec2: np.ndarray,
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card, *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    """B1 — Adaptive Sampling with per-table separate state (Exqutor §V-B)."""
    out: list[dict] = []
    n_total = vec1.shape[0]
    state_kwargs = dict(ADAPTIVE_HP)
    state_kwargs["max_size"] = min(state_kwargs["max_size"], n_total)
    for sel in selectivities:
        if sel not in D1_by_sel or sel not in D2_by_sel:
            continue
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            state1 = AdaptiveState(**state_kwargs)
            state2 = AdaptiveState(**state_kwargs)
            s1_next = SAMPLE_SIZE
            s2_next = SAMPLE_SIZE
            for i, qid in enumerate(qids):
                qid_int = int(qid)
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = int(true_card[(qid_int, sel)])
                t0 = time.perf_counter()
                _, h1, s1u = _bernoulli_single(vec1, q1[i], D1, s1_next, rng)
                _, h2, s2u = _bernoulli_single(vec2, q2[i], D2, s2_next, rng)
                p1 = h1 / max(s1u, 1)
                p2 = h2 / max(s2u, 1)
                est = float(p1 * p2 * n_total)
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                used = s1u + s2u
                out.append({
                    "cell": cell["name"], "cell_kind": cell["kind"],
                    "baseline": "B1", "selectivity": sel, "seed": seed,
                    "query_id": qid_int, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": used,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D1, "D2_target": D2, "reused_from": "",
                })
                s1_next = state1.step(qerr)
                s2_next = state2.step(qerr)
    return out


def _measure_b2_multi(
    cell: dict, vec1: np.ndarray, vec2: np.ndarray,
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card, *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    out: list[dict] = []
    for sel in selectivities:
        if sel not in D1_by_sel or sel not in D2_by_sel:
            continue
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            for i, qid in enumerate(qids):
                qid_int = int(qid)
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = int(true_card[(qid_int, sel)])
                t0 = time.perf_counter()
                est, _, used = _bernoulli_dual(
                    vec1, vec2, q1[i], q2[i], D1, D2, SAMPLE_SIZE, rng,
                )
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": cell["kind"],
                    "baseline": "B2", "selectivity": sel, "seed": seed,
                    "query_id": qid_int, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": SAMPLE_SIZE,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D1, "D2_target": D2, "reused_from": "",
                })
    return out


def _measure_b3_multi(
    cell: dict, samples1: dict, samples2: dict, sizes: dict,
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card, *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    out: list[dict] = []
    alloc = _proportional_alloc(sizes, SAMPLE_SIZE)
    for sel in selectivities:
        if sel not in D1_by_sel or sel not in D2_by_sel:
            continue
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            for i, qid in enumerate(qids):
                qid_int = int(qid)
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = int(true_card[(qid_int, sel)])
                t0 = time.perf_counter()
                est, used = _stratified_dual(
                    samples1, samples2, sizes, alloc,
                    q1[i], q2[i], D1, D2, rng,
                )
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": cell["kind"],
                    "baseline": "B3", "selectivity": sel, "seed": seed,
                    "query_id": qid_int, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used,
                    "sample_size_total": int(alloc.sum()),
                    "wall_clock_ms": wall_ms,
                    "D1_target": D1, "D2_target": D2, "reused_from": "",
                })
    return out


def _measure_b4_multi(
    cell: dict, samples1: dict, samples2: dict, sizes: dict,
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card, *,
    selectivities, seeds, num_queries, n_total: int,
) -> list[dict]:
    out: list[dict] = []
    state_kwargs = dict(ADAPTIVE_HP)
    state_kwargs["max_size"] = min(state_kwargs["max_size"], n_total)
    for sel in selectivities:
        if sel not in D1_by_sel or sel not in D2_by_sel:
            continue
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed))
            state = AdaptiveState(**state_kwargs)
            for i, qid in enumerate(qids):
                qid_int = int(qid)
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = int(true_card[(qid_int, sel)])
                t0 = time.perf_counter()
                budget = int(round(state.sample_size))
                alloc = _proportional_alloc(sizes, budget)
                est, used = _stratified_dual(
                    samples1, samples2, sizes, alloc,
                    q1[i], q2[i], D1, D2, rng,
                )
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": cell["kind"],
                    "baseline": "B4", "selectivity": sel, "seed": seed,
                    "query_id": qid_int, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": budget,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D1, "D2_target": D2, "reused_from": "",
                })
                state.step(qerr)
    return out


def _measure_b5_multi(
    cell: dict, vec1: np.ndarray, vec2: np.ndarray,
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card,
    b1_rows: list[dict], *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    if not b1_rows:
        log.warning("B5 multi skipped — B1 must run first to supply budgets.")
        return []
    b1_lookup = {
        (r["selectivity"], r["seed"], r["query_id"]): r["sample_size_used"]
        for r in b1_rows
    }
    out: list[dict] = []
    for sel in selectivities:
        if sel not in D1_by_sel or sel not in D2_by_sel:
            continue
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed) ^ 0x5B5B5B5B)
            for i, qid in enumerate(qids):
                qid_int = int(qid)
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = int(true_card[(qid_int, sel)])
                budget = b1_lookup.get(
                    (sel, seed, qid_int), 2 * SAMPLE_SIZE,
                )
                # B1 uses two samples (s1+s2) — keep budget parity by halving.
                per_table = max(1, budget // 2)
                t0 = time.perf_counter()
                est, _, used = _bernoulli_dual(
                    vec1, vec2, q1[i], q2[i], D1, D2, per_table, rng,
                )
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": cell["kind"],
                    "baseline": "B5", "selectivity": sel, "seed": seed,
                    "query_id": qid_int, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used, "sample_size_total": budget,
                    "wall_clock_ms": wall_ms,
                    "D1_target": D1, "D2_target": D2, "reused_from": "",
                })
    return out


def _measure_b6_multi(
    cell: dict, samples1: dict, samples2: dict, sizes: dict,
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card, *,
    selectivities, seeds, num_queries,
) -> list[dict]:
    out: list[dict] = []
    for sel in selectivities:
        if sel not in D1_by_sel or sel not in D2_by_sel:
            continue
        D1_vec = D1_by_sel[sel]
        D2_vec = D2_by_sel[sel]
        for seed in seeds:
            rng = np.random.default_rng(_seed_int(seed) ^ 0xDEADBEEF)
            for i, qid in enumerate(qids):
                qid_int = int(qid)
                D1 = float(D1_vec[i])
                D2 = float(D2_vec[i])
                tc = int(true_card[(qid_int, sel)])
                t0 = time.perf_counter()
                sigmas = _estimate_cluster_sigma_dual(
                    samples1, samples2, q1[i], q2[i], D1, D2,
                )
                alloc = _neyman_alloc(sizes, sigmas, SAMPLE_SIZE)
                est, used = _stratified_dual(
                    samples1, samples2, sizes, alloc,
                    q1[i], q2[i], D1, D2, rng,
                )
                wall_ms = (time.perf_counter() - t0) * 1000.0
                qerr = (max(est / tc, tc / est)
                        if (est > 0 and tc > 0) else None)
                out.append({
                    "cell": cell["name"], "cell_kind": cell["kind"],
                    "baseline": "B6", "selectivity": sel, "seed": seed,
                    "query_id": qid_int, "true_card": tc, "est": est,
                    "q_error": qerr,
                    "sample_size_used": used,
                    "sample_size_total": int(alloc.sum()),
                    "wall_clock_ms": wall_ms,
                    "D1_target": D1, "D2_target": D2, "reused_from": "",
                })
    return out


def measure_cell_multi(
    cell: dict, baselines: list[str], *,
    selectivities, seeds, num_queries, skip_existing,
    learn_frac=0.01, learn_seed=42,
) -> list[dict]:
    helpers = _lazy_imports_multi()
    vec1, vec2, qids, q1, q2, D1_by_sel, D2_by_sel, true_card = _load_multi_cell(
        cell, helpers, num_queries,
    )
    log.info("multi loaded: cell=%s N=%d dims=(%d, %d)",
             cell["name"], vec1.shape[0], vec1.shape[1], vec2.shape[1])

    # KM20 stratification (oracle) on norm-aware concat — needed for B3/B4/B6.
    sids = None
    samples1 = samples2 = sizes = None
    needs_strat = any(b in ("B3", "B4", "B6") for b in baselines)
    if needs_strat:
        sids = _km20_assign_multi(vec1, vec2, learn_frac, learn_seed)
        cache_dual = (helpers["cache_dual_samples_join"]
                      if cell["kind"] == "join"
                      else helpers["cache_dual_samples"])
        samples1, samples2, sizes = cache_dual(vec1, vec2, sids)
        log.info("KM20 sizes: min=%d max=%d K_used=%d/%d",
                  min(sizes.values()), max(sizes.values()),
                  sum(1 for v in sizes.values() if v > 0), N_STRATA)

    b1_rows: list[dict] = []
    rows: list[dict] = []
    for b in baselines:
        log.info("[%s] cell=%s baseline=%s start", cell["kind"], cell["name"], b)
        t0 = time.time()
        if b == "B1":
            sub = _measure_b1_multi(
                cell, vec1, vec2, qids, q1, q2,
                D1_by_sel, D2_by_sel, true_card,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
            b1_rows = sub
        elif b == "B2":
            sub = _measure_b2_multi(
                cell, vec1, vec2, qids, q1, q2,
                D1_by_sel, D2_by_sel, true_card,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
        elif b == "B3":
            reuse = _existing_b3_path_multi(cell)
            if reuse is not None and skip_existing:
                log.info("[B3] reusing %s", reuse)
                sub = _slice_b3_from_w1(reuse, cell, num_queries=num_queries)
            else:
                sub = _measure_b3_multi(
                    cell, samples1, samples2, sizes,
                    qids, q1, q2, D1_by_sel, D2_by_sel, true_card,
                    selectivities=selectivities, seeds=seeds,
                    num_queries=num_queries,
                )
        elif b == "B4":
            sub = _measure_b4_multi(
                cell, samples1, samples2, sizes,
                qids, q1, q2, D1_by_sel, D2_by_sel, true_card,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries, n_total=vec1.shape[0],
            )
        elif b == "B5":
            sub = _measure_b5_multi(
                cell, vec1, vec2, qids, q1, q2,
                D1_by_sel, D2_by_sel, true_card, b1_rows,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
        elif b == "B6":
            sub = _measure_b6_multi(
                cell, samples1, samples2, sizes,
                qids, q1, q2, D1_by_sel, D2_by_sel, true_card,
                selectivities=selectivities, seeds=seeds,
                num_queries=num_queries,
            )
        else:
            raise ValueError(f"unsupported baseline: {b}")
        log.info("[%s] %s done %d rows in %.1fs",
                  cell["name"], b, len(sub), time.time() - t0)
        rows.extend(sub)

    return rows


# ---------------------------------------------------------------------------
# Output / IO
# ---------------------------------------------------------------------------

def _save_csv(rows: list[dict], out_csv: Path, meta_path: Path,
                meta_extra: dict) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    log.info("saved %s (%d rows)", out_csv, len(df))
    if not df.empty:
        smry = (df.groupby(["cell", "baseline", "selectivity"])["q_error"]
                  .agg(["mean", "median", "count"]).round(4))
        log.info("\n=== q_error summary (cell × baseline × sel) ===\n%s\n", smry)
    meta = {
        "kst": kst(),
        "n_rows": len(df),
        "baselines": (sorted(df["baseline"].unique().tolist())
                      if not df.empty else []),
        "cells": (sorted(df["cell"].unique().tolist())
                  if not df.empty else []),
    }
    meta.update(meta_extra)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    log.info("saved %s", meta_path)


def _resolve_out_dir(arg_out_dir: Optional[str]) -> Path:
    if arg_out_dir:
        return Path(arg_out_dir)
    if ROOT_SERVER.exists():
        return ROOT_SERVER / "phase_f"
    return SCRIPTS_PATH.parent / "cache" / "rq3" / "phase_f"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--cells", nargs="+", required=True,
                    choices=sorted(ALL_CELLS.keys()),
                    help="One or more of the 28 Phase F cells.")
    ap.add_argument("--baselines", nargs="+", required=True,
                    choices=ALL_BASELINES,
                    help="Subset of {B1..B6}. Order matters: B5 requires B1.")
    ap.add_argument("--out-dir", default=None,
                    help="Output dir (default = server cache/rq3/phase_f).")
    ap.add_argument("--num-queries", type=int, default=N_QUERIES_DEFAULT)
    ap.add_argument("--selectivity", nargs="*", type=float,
                    default=SELECTIVITIES,
                    help=f"Selectivity grid (default {SELECTIVITIES}).")
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--num-seeds", type=int, default=len(SEEDS))
    ap.add_argument("--skip-existing", action="store_true", default=True,
                    help="Skip cells whose output csv already exists, and "
                         "reuse W1 parquets for B3 when available.")
    ap.add_argument("--no-skip-existing", dest="skip_existing",
                    action="store_false")
    ap.add_argument("--learn-frac", type=float, default=0.01,
                    help="KM20 learn fraction for multi-cell stratification.")
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate CLI / cell / baseline config without "
                         "any DB / measurement.  Estimates the run budget.")
    return ap.parse_args(argv)


def _enforce_b1_before_b5(baselines: list[str]) -> list[str]:
    """B5 needs B1 budgets — auto-reorder so B1 runs first."""
    if "B5" in baselines and "B1" not in baselines:
        raise SystemExit("B5 requires B1 budgets. Add B1 to --baselines.")
    if "B5" in baselines:
        ordered = [b for b in baselines if b != "B5"]
        if "B1" in ordered:
            ordered.remove("B1")
            ordered = ["B1"] + ordered
        ordered.append("B5")
        return ordered
    return baselines


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    seeds = SEEDS[args.seed_start:args.seed_start + args.num_seeds]
    if not seeds:
        raise SystemExit(
            f"--seed-start={args.seed_start} --num-seeds={args.num_seeds} → "
            f"empty seed list (SEEDS={SEEDS}).",
        )
    baselines = _enforce_b1_before_b5(list(args.baselines))
    out_dir = _resolve_out_dir(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("=== Phase F — Stage VI baseline portfolio ===")
    log.info("cells:     %s", args.cells)
    log.info("baselines: %s (after B1<B5 reorder: %s)", args.baselines, baselines)
    log.info("seeds:     %s", seeds)
    log.info("sels:      %s", args.selectivity)
    log.info("n_queries: %s", args.num_queries)
    log.info("out_dir:   %s", out_dir)

    if args.dry_run:
        log.info("=== dry-run: validating cell + baseline matrix ===")
        n_meas = (len(args.cells) * len(baselines) *
                  len(args.selectivity) * len(seeds) * args.num_queries)
        log.info("estimate: %d cell × %d baseline × %d sel × %d seed × %d q "
                 "= %d measurement",
                 len(args.cells), len(baselines),
                 len(args.selectivity), len(seeds), args.num_queries, n_meas)
        for c_name in args.cells:
            cell = ALL_CELLS[c_name]
            log.info("  %s  kind=%s", c_name, cell["kind"])
            for b in baselines:
                if b == "B3":
                    reuse = (_existing_b3_path_single(cell)
                             if cell["kind"] == "single"
                             else _existing_b3_path_multi(cell))
                    if reuse is not None:
                        log.info("    %s reuse=%s", b, reuse)
                    else:
                        log.info("    %s (compute)", b)
                else:
                    log.info("    %s (compute)", b)
        log.info("=== dry-run OK ===")
        return 0

    t_total = time.time()
    n_cell_done = 0
    for c_name in args.cells:
        cell = ALL_CELLS[c_name]
        out_csv = out_dir / f"phase_f_{c_name}.csv"
        out_meta = out_dir / f"phase_f_{c_name}_meta.json"

        if out_csv.exists() and args.skip_existing:
            log.info("SKIP %s (csv exists). Use --no-skip-existing to overwrite.",
                      out_csv)
            continue

        log.info("\n###### CELL %s (kind=%s) ######", c_name, cell["kind"])
        t_cell = time.time()
        try:
            if cell["kind"] == "single":
                rows = measure_cell_single(
                    cell, baselines,
                    selectivities=list(args.selectivity), seeds=seeds,
                    num_queries=args.num_queries,
                    skip_existing=args.skip_existing,
                )
            else:
                rows = measure_cell_multi(
                    cell, baselines,
                    selectivities=list(args.selectivity), seeds=seeds,
                    num_queries=args.num_queries,
                    skip_existing=args.skip_existing,
                    learn_frac=args.learn_frac, learn_seed=args.learn_seed,
                )
        except Exception as exc:  # pragma: no cover — runtime safety net
            log.exception("cell %s failed: %s", c_name, exc)
            continue

        meta_extra = {
            "cell": c_name, "cell_kind": cell["kind"],
            "baselines_run": baselines,
            "selectivities": list(args.selectivity),
            "seeds": list(seeds),
            "num_queries": args.num_queries,
            "adaptive_hyperparam": ADAPTIVE_HP,
            "elapsed_s": round(time.time() - t_cell, 1),
            "design_doc": "plans/RQ재정립_v7_evidence_20260509_1820.md §6",
        }
        _save_csv(rows, out_csv, out_meta, meta_extra)
        log.info("cell %s done %.1fs", c_name, time.time() - t_cell)
        n_cell_done += 1

    log.info("\n=== Phase F done: %d/%d cells in %.1fs ===",
              n_cell_done, len(args.cells), time.time() - t_total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
