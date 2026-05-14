#!/usr/bin/env python3
"""
Exqutor 100% paper 정확 재현 measurement script — DRAFT (사용자 confirm 대기).

사용자 명시 (5/10 14:03): "paper의 모든 항목 완전 똑같이 진행. 단 하나라도 다르면 안 됨."

본 DRAFT 는 handoff_v2 (5/10 14:18) §3 설계안 기반. 사용자 외출 중 작성.
사용자 복귀 시 §1 5 critical decisions confirm 후 실행 가능 finalize.

paper verbatim source:
- arXiv:2512.09695v2, Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries
- §V-B Eq 1-6 (p.6) — Adaptive Sampling
- §VI Datasets/Indexing/System setup (p.7)
- §VI-A~D Fig 4-14 (p.7-11) — measurement matrix
- query SQL: reference/exqutor_query_plans/{tpc_h,tpc_ds}/

DRAFT 미반영 (사용자 confirm 후):
- 34 method registry 실제 connect (Tier 1/S+/A/B/C)
- _measure_common.py 의 fetch_all_vectors_safe / cache_cluster_samples_inmem 재사용
- server side path/credentials 확정
- output schema (parquet meta) 확정

사용처: server `/mnt/hdd0/home/capstone2026/cache/rq3/`
"""
from __future__ import annotations

import json
import time
import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Callable

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paper verbatim spec (handoff_v2 §3.1)
# ---------------------------------------------------------------------------

# Eq 1: N = ⌈z²·P̂(1-P̂)/e²⌉ = 385 (paper p.6, p.7)
PAPER_HYPERPARAM = {
    "z": 1.96,           # 95% confidence (paper p.7)
    "P_hat": 0.5,        # proportion estimate (paper p.7)
    "e": 0.05,           # margin of error (paper p.7)
    "N_init": 385,       # initial sample size (Eq 1 result)
    "m": 0.9,            # momentum coefficient (Eq 4, paper p.7)
    "eta_0": 0.1,        # initial learning rate (Eq 4)
    "alpha": 50,         # δ weighting factor (Eq 3)
    "beta": 1.5,         # target Q-error (Eq 3)
    "gamma": 0.99,       # learning rate decay (Eq 6)
    "update_period": 50, # update every 50 queries (paper p.7)
    # NOTE: paper Eq 1-6 에 min/max clamping 없음. handoff_v1 의 "min=355/max=415" 폐기.
}

# paper p.7 verbatim: HNSW M=16, ef_construction=200, ef_search=400
PAPER_HNSW = {"M": 16, "ef_construction": 200, "ef_search": 400}

# paper p.4 §IV verbatim: TPC-H 8 / TPC-DS 7 specific queries
PAPER_QUERIES = {
    "tpc_h": ["q3", "q5", "q8", "q9", "q10", "q11", "q12", "q20"],
    # paper SQL (reference/exqutor_query_plans/tpc_h/) verbatim:
    # 모든 8 query 통일 threshold = 0.86 (DEEP 96d)
    "tpc_h_threshold_default": 0.86,
    "tpc_ds": ["q07", "q12", "q19", "q20", "q42", "q72", "q98"],
    # paper SQL (reference/exqutor_query_plans/tpc_ds/) verbatim:
    "tpc_ds_threshold": {
        "q07": 1.08, "q12": 1.08, "q20": 1.08, "q72": 1.08,
        "q19": 1.20, "q42": 1.20,
        "q98": 1.30,
    },
}

# paper Fig 13 verbatim: {0.1%, 1%, 10%} 3 levels only.
# handoff_v1 §1.3 의 우리 기존 {0.05, 0.30, 0.50} 폐기.
PAPER_SELECTIVITIES = [0.001, 0.01, 0.10]
PAPER_SELECTIVITY_DEFAULT = 0.01  # paper p.7 sampling-based default

# paper p.7 verbatim
PAPER_MEASUREMENT = {
    "trials": 10,
    "trim": "lowest_highest",  # 8 runs avg
    "warmup": 1,
    "max_worker_processes": 8,  # PostgreSQL paper p.7
    "worker_threads": 128,      # DuckDB paper p.7 (참고용)
}

# paper §VI dataset spec (verbatim)
PAPER_DATASETS = {
    "DEEP": {"dim": 96, "ref": "[59]"},
    "SIFT": {"dim": 128, "ref": "[60]"},
    "SimSearchNet++": {"dim": 256, "ref": "[61]"},
    "YFCC": {"dim": 192, "ref": "[62][63]"},
    "WIKI": {"dim": 768, "ref": "[64]"},
}


# ---------------------------------------------------------------------------
# AdaptiveState — paper Eq 1-6 verbatim (NO clamping)
# ---------------------------------------------------------------------------

@dataclass
class AdaptiveState:
    """Exqutor §V-B Adaptive Sampling state. Eq 1-6 verbatim, NO min/max clamping.

    paper Eq 3-6:
        δ            = α·(Q-error - β) - (100-α)·sampling_ratio        (3)
        V_t          = m·V_{t-1} + η_t·δ                              (4)
        size_{t+1}   = size_t + V_t                                   (5)
        η_{t+1}      = γ·η_t                                          (6)

    handoff_v1 의 "min_size=355, max_size=415" 강제는 paper Eq 1-6 에 없음 → 제거.
    Fig 6 trace 의 stable point (~358 DEEP / ~415 SIFT / ~362 SSN) 는 자연 수렴값.
    """
    size: int = PAPER_HYPERPARAM["N_init"]
    m: float = PAPER_HYPERPARAM["m"]
    eta: float = PAPER_HYPERPARAM["eta_0"]
    alpha: float = PAPER_HYPERPARAM["alpha"]
    beta: float = PAPER_HYPERPARAM["beta"]
    gamma: float = PAPER_HYPERPARAM["gamma"]
    update_period: int = PAPER_HYPERPARAM["update_period"]
    V_prev: float = 0.0
    iter: int = 0
    history: list = field(default_factory=list)

    def update(self, q_error: float, sampling_ratio: float) -> int:
        """Update sample size every `update_period` queries. Returns new size."""
        self.iter += 1
        if self.iter % self.update_period != 0:
            return self.size
        # Eq 3: delta
        delta = self.alpha * (q_error - self.beta) - (100 - self.alpha) * sampling_ratio
        # Eq 4: momentum
        V_t = self.m * self.V_prev + self.eta * delta
        # Eq 5: size update (paper 에 clamping 없음, but >= 1 guard)
        new_size = max(1, int(round(self.size + V_t)))
        self.history.append({
            "iter": self.iter, "delta": delta, "V_t": V_t,
            "old_size": self.size, "new_size": new_size, "eta": self.eta,
        })
        self.size = new_size
        self.V_prev = V_t
        # Eq 6: decay
        self.eta = self.gamma * self.eta
        return self.size


# ---------------------------------------------------------------------------
# Q-error metric (paper Eq 2 verbatim)
# ---------------------------------------------------------------------------

def q_error(c_est: float, c_true: float) -> float:
    """paper Eq 2: Q-error = max(C_est/C_true, C_true/C_est).

    `c_est <= 0` 또는 `c_true <= 0` 시 inf 처리 (paper 명시 없음, 일반 관례).
    """
    if c_est <= 0 or c_true <= 0:
        return float("inf")
    return max(c_est / c_true, c_true / c_est)


def trimmed_mean(values: list, trim_count: int = 1) -> float:
    """paper p.7 verbatim: lowest+highest 1개씩 제외한 8 runs avg (10 runs 기준)."""
    if len(values) <= 2 * trim_count:
        return float(np.mean(values)) if values else float("nan")
    sorted_vals = sorted(values)
    trimmed = sorted_vals[trim_count : len(sorted_vals) - trim_count]
    return float(np.mean(trimmed))


# ---------------------------------------------------------------------------
# Cell spec (5 sub-experiment, handoff_v2 §2.1)
# ---------------------------------------------------------------------------

@dataclass
class CellSpec:
    sub: str                # "A1-DEEP" / "A1-SIFT" / ... / "A5-scale"
    fig: str                # "Fig 5/6" / "Fig 7" / ...
    dataset: str            # "DEEP" / "SIFT" / "SimSearchNet++" / "YFCC" / "WIKI"
    sf: int                 # 1 / 10 / 100
    queries: list           # ["q3", "q10", "q12"] etc.
    selectivities: list     # [0.01] or [0.001, 0.01, 0.10]
    threshold_map: dict     # {q: threshold} (paper SQL verbatim) or single value
    table: str              # "partsupp_deep_100" or "item_deep_10" etc.
    mode_pool: list         # ["B1", "CaseA", "CaseB"] or ["ECQO"]


def build_cell_specs() -> list[CellSpec]:
    """handoff_v2 §2.1 measurement matrix verbatim."""
    cells = []

    # A1 Sampling main (Fig 5/6) — dataset별 queries 다름 (paper p.8 verbatim)
    cells.append(CellSpec(
        sub="A1-DEEP", fig="Fig 5/6", dataset="DEEP", sf=100,
        queries=["q3", "q10", "q12"],  # paper Fig 5 verbatim DEEP
        selectivities=[PAPER_SELECTIVITY_DEFAULT],
        threshold_map={q: PAPER_QUERIES["tpc_h_threshold_default"] for q in ["q3", "q10", "q12"]},
        table="partsupp_deep_100",
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A1-SIFT", fig="Fig 5/6", dataset="SIFT", sf=100,
        queries=["q3", "q10", "q12"],  # paper Fig 5 verbatim SIFT
        selectivities=[PAPER_SELECTIVITY_DEFAULT],
        threshold_map={q: PAPER_QUERIES["tpc_h_threshold_default"] for q in ["q3", "q10", "q12"]},
        table="partsupp_sift_100",
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A1-SSN", fig="Fig 5/6", dataset="SimSearchNet++", sf=100,
        queries=["q3", "q9", "q10"],  # paper Fig 5 verbatim SSN++ (Q12 X)
        selectivities=[PAPER_SELECTIVITY_DEFAULT],
        threshold_map={q: PAPER_QUERIES["tpc_h_threshold_default"] for q in ["q3", "q9", "q10"]},
        table="partsupp_fb_100",  # FB = SimSearchNet++ alias on server
        mode_pool=["B1", "CaseA", "CaseB"],
    ))

    # A2 Multi-vector (Fig 7/8/9) — TPC-H 8 queries 모두
    cells.append(CellSpec(
        sub="A2-Fig7", fig="Fig 7", dataset="YFCC", sf=10,
        queries=PAPER_QUERIES["tpc_h"],
        selectivities=[PAPER_SELECTIVITY_DEFAULT],
        threshold_map={q: PAPER_QUERIES["tpc_h_threshold_default"] for q in PAPER_QUERIES["tpc_h"]},
        table="partsupp_yfcc_10",  # ps_tag included
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A2-Fig8", fig="Fig 8", dataset="DEEP+WIKI", sf=10,
        queries=PAPER_QUERIES["tpc_h"],
        selectivities=[PAPER_SELECTIVITY_DEFAULT],
        threshold_map={q: PAPER_QUERIES["tpc_h_threshold_default"] for q in PAPER_QUERIES["tpc_h"]},
        table="partsupp_deep_wiki_10",  # 4-way: ps_image_emb + ps_text_emb same row
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A2-Fig9", fig="Fig 9", dataset="DEEP+WIKI cross", sf=10,
        queries=PAPER_QUERIES["tpc_h"],
        selectivities=[PAPER_SELECTIVITY_DEFAULT],
        threshold_map={q: PAPER_QUERIES["tpc_h_threshold_default"] for q in PAPER_QUERIES["tpc_h"]},
        table="multi_join_deep_wiki_10",  # partsupp[DEEP] × part[WIKI] cross
        mode_pool=["B1", "CaseA", "CaseB"],
    ))

    # A3 TPC-DS (Fig 10) — ECQO mode (with vector index, sampling X)
    cells.append(CellSpec(
        sub="A3-TPCDS", fig="Fig 10", dataset="DEEP", sf=10,
        queries=PAPER_QUERIES["tpc_ds"],
        selectivities=[None],  # threshold-driven, not selectivity
        threshold_map=PAPER_QUERIES["tpc_ds_threshold"],
        table="item_deep_10",  # SF=10 item table (~100K rows) + i_embedding(96)
        mode_pool=["ECQO"],  # NOT B1/CaseA/CaseB — vector index 활용
    ))

    # A4 Selectivity ablation (Fig 13) — DEEP, Q3/Q10/Q12, sel {0.001, 0.01, 0.10}
    cells.append(CellSpec(
        sub="A4-sel", fig="Fig 13", dataset="DEEP", sf=100,
        queries=["q3", "q10", "q12"],
        selectivities=PAPER_SELECTIVITIES,  # [0.001, 0.01, 0.10]
        threshold_map={
            # NOTE: paper Fig 13 의 selectivity 가 threshold 직접 결정 (sel = 회수율)
            # threshold 는 dataset 분포 dependent → measurement 시점에 calibration
            "q3": None, "q10": None, "q12": None,
        },
        table="partsupp_deep_100",
        mode_pool=["B1", "CaseA", "CaseB"],
    ))

    # A5 Scalability (Fig 14) — DEEP, Q3/Q5/Q20, SF 1/10/100
    for sf in [1, 10, 100]:
        cells.append(CellSpec(
            sub=f"A5-scale-sf{sf}", fig="Fig 14", dataset="DEEP", sf=sf,
            queries=["q3", "q5", "q20"],
            selectivities=[PAPER_SELECTIVITY_DEFAULT],
            threshold_map={q: PAPER_QUERIES["tpc_h_threshold_default"] for q in ["q3", "q5", "q20"]},
            table=f"partsupp_deep_{sf}",
            mode_pool=["B1", "CaseA", "CaseB"],
        ))

    return cells


# ---------------------------------------------------------------------------
# Mode handlers (B1 / CaseA / CaseB / ECQO) — SKELETON
# ---------------------------------------------------------------------------

def measure_b1(cell: CellSpec, query_id: str, query_vec: np.ndarray,
               threshold: float, conn) -> dict:
    """B1: paper §V-B Bernoulli Adaptive Sampling (verbatim Eq 1-6).

    각 query 마다:
    1. AdaptiveState.size 만큼 Bernoulli sampling (sample_ratio = size/total_rows)
    2. sample 에서 vector predicate `<-> query_vec < threshold` count_est * (1/sample_ratio)
       = HT estimator
    3. true cardinality = full table count (사전 측정)
    4. Q-error 계산 → AdaptiveState.update() (Eq 3-6)
    5. wall-clock timer (선택)

    Returns: {q_error, wall_clock_ms, sample_size, mode='B1'}
    """
    # TODO (사용자 confirm 후): _measure_common.py 의 HT estimator + Bernoulli sample 재사용
    raise NotImplementedError("DRAFT — 사용자 5 decisions confirm 후 finalize")


def measure_case_a(cell: CellSpec, query_id: str, query_vec: np.ndarray,
                   threshold: float, conn, method_name: str) -> dict:
    """CaseA: 우리 method 가 sampling step 직접 대체.

    paper §V-B 의 Bernoulli step 을 우리 34 methods 중 1개 (method_name) 로 교체.
    AdaptiveState.size 와 update logic 은 paper 그대로.
    sampling 만 method-specific (cluster sample / projection / sketch / ...).

    Returns: {q_error, wall_clock_ms, sample_size, mode='CaseA', method=method_name}
    """
    # TODO: method registry connect (Tier 1/S+/A/B/C 34 methods)
    raise NotImplementedError("DRAFT — 사용자 confirm 후")


def measure_case_b(cell: CellSpec, query_id: str, query_vec: np.ndarray,
                   threshold: float, conn, method_name: str,
                   ensemble_weight: float = 0.5) -> dict:
    """CaseB: B1 + CaseA ensemble (가중 평균).

    c_est_b1 = measure_b1 결과
    c_est_case_a = measure_case_a 결과
    c_est_final = (1 - w) * c_est_b1 + w * c_est_case_a
    또는 fallback: B1 unreliable 시 (Q-error > β) CaseA 사용.

    Returns: {q_error, wall_clock_ms, sample_size, mode='CaseB', method=method_name, weight=w}
    """
    # TODO: ensemble strategy 사용자 결정 필요 (가중 평균 vs fallback)
    raise NotImplementedError("DRAFT — 사용자 confirm 후")


def measure_ecqo(cell: CellSpec, query_id: str, query_vec: np.ndarray,
                 threshold: float, conn) -> dict:
    """ECQO: HNSW range query (vector index 활용, paper §V-A + §VI-A Fig 4).

    paper §V-A: HNSW range query (M=16, ef_search=400) 를 cardinality estimator 로 사용.
    1~2ms 내 정확한 cardinality 반환.
    A3 TPC-DS Fig 10 만 적용 (sampling 영역 외).

    Returns: {q_error, wall_clock_ms, sample_size=None, mode='ECQO'}
    """
    # TODO: pgvector HNSW range query SQL 작성 + EXPLAIN ANALYZE
    raise NotImplementedError("DRAFT — 사용자 confirm 후")


# ---------------------------------------------------------------------------
# Main measurement loop (10 trimmed mean per cell × query × selectivity × mode)
# ---------------------------------------------------------------------------

def run_cell(cell: CellSpec, mode: str, method_name: Optional[str] = None,
             trials: int = 10, output_dir: Optional[Path] = None) -> pd.DataFrame:
    """Run measurement for single cell × mode.

    paper p.7 verbatim: 10 trials, lowest+highest excluded → 8 runs avg.
    각 trial 마다 `update_period=50` 단위로 AdaptiveState 진행.

    NOTE: paper §VI-B Fig 5/6 setup 은 "1000 iterations" trace 로 sample size convergence
    측정. 우리 measurement 도 1000 query × 10 trials = 10000 query/cell 권장.
    """
    # TODO (사용자 confirm 후):
    # 1. fetch query pool (cell.queries 의 SQL 적용한 cardinality 측정 query vectors)
    # 2. for trial in 1..10:
    #    - state = AdaptiveState()
    #    - for query in 1..1000:
    #         vec = query_pool[trial][query]
    #         result = measure_{mode}(cell, query_id, vec, threshold, conn, method_name)
    #         state.update(result['q_error'], sampling_ratio)
    #    - record: avg_q_error, final_size, final_eta, history
    # 3. trimmed_mean(trial_q_errors)
    # 4. save parquet (cache/rq3/exqutor_replication_phase_<X>/cell_<sub>_<mode>_<method>.parquet)
    raise NotImplementedError("DRAFT — 사용자 confirm 후 finalize")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Exqutor paper 100% 정확 재현")
    parser.add_argument("--phase", required=True, choices=["A", "B", "C", "D"],
                        help="A=B1 baseline / B=CaseA replace / C=CaseB augment / D=analysis")
    parser.add_argument("--cell", default="all", help="A1-DEEP / A2-Fig7 / ... or 'all'")
    parser.add_argument("--mode", choices=["B1", "CaseA", "CaseB", "ECQO"], help="Measurement mode")
    parser.add_argument("--method", help="Method name (CaseA/CaseB only, 34 methods)")
    parser.add_argument("--trials", type=int, default=PAPER_MEASUREMENT["trials"])
    parser.add_argument("--output", type=Path, default=Path("/mnt/hdd0/home/capstone2026/cache/rq3/exqutor_replication"))
    parser.add_argument("--dry-run", action="store_true", help="Validation only (Fig 6 convergence trace 비교)")
    args = parser.parse_args()

    cells = build_cell_specs()
    if args.cell != "all":
        cells = [c for c in cells if c.sub == args.cell]

    print(f"[{datetime.now(timezone(timedelta(hours=9))).isoformat()}] phase={args.phase} cells={len(cells)}")
    for c in cells:
        print(f"  {c.sub}: dataset={c.dataset} sf={c.sf} queries={c.queries} sel={c.selectivities} mode_pool={c.mode_pool}")

    if args.dry_run:
        # paper Fig 6 trace 비교 (DEEP ~358 / SIFT ~415 / SSN ~362 stable point)
        print("\n--- Dry-run: AdaptiveState convergence trace ---")
        for ds in ["DEEP", "SIFT", "SimSearchNet++"]:
            state = AdaptiveState()
            # synthetic Q-error trace (paper Fig 6 mock)
            trace = []
            np.random.seed(42)
            for it in range(1, 1001):
                q_err = max(1.0, np.random.lognormal(0.5, 0.3))
                ratio = state.size / 1_000_000  # synthetic
                state.update(q_err, ratio)
                if it % 50 == 0:
                    trace.append((it, state.size, state.eta))
            print(f"  {ds:<20s} final_size={state.size:4d} eta={state.eta:.6f} (paper stable: ~358 DEEP / ~415 SIFT / ~362 SSN)")
        return

    # TODO: phase A/B/C/D dispatch
    raise NotImplementedError("Phase 실행 — 사용자 5 decisions confirm 후 finalize")


if __name__ == "__main__":
    main()
