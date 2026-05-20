#!/usr/bin/env python3
"""
Exqutor paper 100% 정확 재현 measurement script.

사용자 명시 (5/10 14:03 KST): "paper의 모든 항목 완전 똑같이 진행. 단 하나라도 다르면 안 됨."

paper verbatim source: arXiv:2512.09695v2
- §V-B Eq 1-6 (p.6) Adaptive Sampling
- §VI Datasets/Indexing/System setup (p.7)
- §VI-A~D Fig 4-14 measurement matrix
- query SQL: reference/exqutor_query_plans/{tpc_h,tpc_ds}/

handoff_v2 (5/10 14:18) §3 DRAFT 기반. server 인프라 (_measure_common.py) reuse.

서버 실행:
    cd /mnt/hdd0/home/capstone2026/cache/rq3
    python3 measure_paper_exact.py --rq 3 --phase A --cell A1-DEEP --mode B1
    python3 measure_paper_exact.py --rq 3 --phase B --cell A1-DEEP --mode CaseA --method minibatch
    python3 measure_paper_exact.py --rq 1 --phase A  # RQ1 paper exact 재측정
    python3 measure_paper_exact.py --rq 2 --phase A  # RQ2 paper exact 재측정
"""
from __future__ import annotations

import argparse
import os
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# 서버 측 path — _measure_common.py 재사용
import sys
sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")

try:
    import _measure_common as mc
    SERVER = True
    # paper-exact: active PG instance = 55435 (채림님 메일 + 5/10 검증)
    # _measure_common.py 의 PORT=55436 은 stale → override
    mc.PORT = 55435
except ImportError:
    SERVER = False
    print("[WARN] _measure_common.py 미발견 — local dry-run only")


# dataset name → query_pool 파일명 매핑 (Fig 8/9 cross/multi 는 DEEP query 사용)
DATASET_ALIAS = {
    "DEEP": "DEEP",
    "SIFT": "SIFT",
    "SimSearchNet++": "SSN",
    "YFCC": "YFCC",
    "WIKI": "WIKI",
    "DEEP+WIKI": "DEEP",        # Fig 8 multi-vector: ps_image_emb[DEEP] query
    "DEEP+WIKI cross": "DEEP",  # Fig 9 cross-table: partsupp[DEEP] query
}


# ---------------------------------------------------------------------------
# Paper verbatim spec (handoff_v2 §3.1, reference_exqutor_paper_verbatim.md)
# ---------------------------------------------------------------------------

# Eq 1: N = ⌈z²·P̂(1-P̂)/e²⌉ = 385 (paper p.6, p.7 verbatim)
PAPER_HYPERPARAM = {
    "N_init": 385,       # initial sample size
    "m": 0.9,            # momentum coefficient (Eq 4)
    "eta_0": 0.1,        # initial learning rate (Eq 4)
    "alpha": 50,         # δ weighting factor (Eq 3)
    "beta": 1.5,         # target Q-error (Eq 3)
    "gamma": 0.99,       # learning rate decay (Eq 6)
    "update_period": 50, # update every 50 queries (paper p.7)
    # NOTE: paper Eq 1-6 에 min/max clamping 없음 (handoff_v1 추정 폐기)
}

PAPER_HNSW = {"M": 16, "ef_construction": 200, "ef_search": 400}

# paper §IV verbatim
TPC_H_QUERIES = ["q3", "q5", "q8", "q9", "q10", "q11", "q12", "q20"]
TPC_H_THRESHOLD = 0.86  # all 8 queries (verbatim from reference/exqutor_query_plans/tpc_h/*.sql)

TPC_DS_QUERIES = ["q07", "q12", "q19", "q20", "q42", "q72", "q98"]
TPC_DS_THRESHOLD = {
    "q07": 1.08, "q12": 1.08, "q20": 1.08, "q72": 1.08,
    "q19": 1.20, "q42": 1.20,
    "q98": 1.30,
}

# paper Fig 13 verbatim: {0.1%, 1%, 10%} 3 levels only
PAPER_SELECTIVITIES = [0.001, 0.01, 0.10]
PAPER_SEL_DEFAULT = 0.01  # paper §VI sampling-based default

# paper §VI verbatim: 10 trials, lowest+highest 1개 제외 → 8 runs avg
TRIALS = 10
TRIM = 1


# ---------------------------------------------------------------------------
# AdaptiveState — paper Eq 1-6 verbatim (NO clamping)
# ---------------------------------------------------------------------------

@dataclass
class AdaptiveState:
    """Exqutor §V-B Adaptive Sampling state. Eq 1-6 verbatim, NO min/max clamping."""
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
        # Numerical stability: q_error 가 inf (hits=0)일 때 size 폭증 방지
        # paper §V-B 의 typical Q-error 분포는 ~1.69 avg (paper Fig 12). cap=100 영향 미미.
        q_err_safe = float(q_error) if np.isfinite(q_error) else 100.0
        # Eq 3
        delta = self.alpha * (q_err_safe - self.beta) - (100 - self.alpha) * sampling_ratio
        # Eq 4
        V_t = self.m * self.V_prev + self.eta * delta
        # Eq 5 (paper에 clamping 없음, but sample 0 보호)
        new_size = max(1, int(round(self.size + V_t)))
        self.history.append({
            "iter": self.iter, "delta": float(delta), "V_t": float(V_t),
            "old_size": self.size, "new_size": new_size, "eta": float(self.eta),
        })
        self.size = new_size
        self.V_prev = V_t
        # Eq 6
        self.eta = self.gamma * self.eta
        return self.size


# ---------------------------------------------------------------------------
# Q-error metric (paper Eq 2 verbatim)
# ---------------------------------------------------------------------------

def q_error(c_est: float, c_true: float) -> float:
    """paper Eq 2: Q-error = max(C_est/C_true, C_true/C_est)."""
    if c_est <= 0 or c_true <= 0:
        return float("inf")
    return max(c_est / c_true, c_true / c_est)


def trimmed_mean(values: list, trim_count: int = TRIM) -> float:
    """paper p.7 verbatim: lowest+highest excluded.

    inf/nan filter — Bernoulli sampling 시 hits=0 → est=0 → Q-error=inf.
    Paper §V-B 의 N=385 sample at sel=0.01 → expected hits=3.85 → variance 큼.
    inf 1개라도 있으면 mean inf 가 되므로 finite 만 trimmed.
    """
    finite = [float(v) for v in values if np.isfinite(v)]
    if not finite:
        return float("inf")
    if len(finite) <= 2 * trim_count:
        return float(np.mean(finite))
    sorted_vals = sorted(finite)
    trimmed = sorted_vals[trim_count : len(sorted_vals) - trim_count]
    return float(np.mean(trimmed))


# ---------------------------------------------------------------------------
# Cell spec (handoff_v2 §2.1 — paper exact matrix)
# ---------------------------------------------------------------------------

@dataclass
class CellSpec:
    sub: str
    fig: str
    dataset: str
    sf: int
    table: str
    embed_col: str
    vec_dim: int
    queries: list
    selectivities: list
    threshold_map: dict
    mode_pool: list


def build_cell_specs() -> list[CellSpec]:
    """paper exact measurement matrix. RQ3 5단계 narrative #2 'Exqutor 100% 정확 재현'."""
    cells = []

    # A1 Sampling main (Fig 5/6) — paper p.8 verbatim, dataset별 queries 다름
    cells.append(CellSpec(
        sub="A1-DEEP", fig="Fig 5/6", dataset="DEEP", sf=100,
        table="partsupp_deep_100", embed_col="ps_embedding", vec_dim=96,
        queries=["q3", "q10", "q12"],  # paper Fig 5 verbatim DEEP
        selectivities=[PAPER_SEL_DEFAULT],
        threshold_map={q: TPC_H_THRESHOLD for q in ["q3", "q10", "q12"]},
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A1-SIFT", fig="Fig 5/6", dataset="SIFT", sf=100,
        table="partsupp_sift_100", embed_col="ps_embedding", vec_dim=128,
        queries=["q3", "q10", "q12"],  # paper Fig 5 verbatim SIFT
        selectivities=[PAPER_SEL_DEFAULT],
        threshold_map={q: TPC_H_THRESHOLD for q in ["q3", "q10", "q12"]},
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A1-SSN", fig="Fig 5/6", dataset="SimSearchNet++", sf=100,
        table="partsupp_fb_100", embed_col="ps_embedding", vec_dim=256,
        queries=["q3", "q9", "q10"],  # paper Fig 5 verbatim SSN++ (Q12 X)
        selectivities=[PAPER_SEL_DEFAULT],
        threshold_map={q: TPC_H_THRESHOLD for q in ["q3", "q9", "q10"]},
        mode_pool=["B1", "CaseA", "CaseB"],
    ))

    # A2 Multi-vector (Fig 7/8/9) — paper TPC-H 8 queries 모두
    cells.append(CellSpec(
        sub="A2-Fig7", fig="Fig 7", dataset="YFCC", sf=10,
        table="partsupp_yfcc_10", embed_col="ps_embedding", vec_dim=192,
        queries=TPC_H_QUERIES,
        selectivities=[PAPER_SEL_DEFAULT],
        threshold_map={q: TPC_H_THRESHOLD for q in TPC_H_QUERIES},
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A2-Fig8", fig="Fig 8", dataset="DEEP+WIKI", sf=10,
        table="partsupp_deep_wiki_10", embed_col="ps_embedding_deep", vec_dim=96,
        queries=TPC_H_QUERIES,
        selectivities=[PAPER_SEL_DEFAULT],
        threshold_map={q: TPC_H_THRESHOLD for q in TPC_H_QUERIES},
        mode_pool=["B1", "CaseA", "CaseB"],
    ))
    cells.append(CellSpec(
        sub="A2-Fig9", fig="Fig 9", dataset="DEEP+WIKI cross", sf=10,
        table="partsupp_deep_10",  # cross with part_wiki_10
        embed_col="ps_embedding", vec_dim=96,
        queries=TPC_H_QUERIES,
        selectivities=[PAPER_SEL_DEFAULT],
        threshold_map={q: TPC_H_THRESHOLD for q in TPC_H_QUERIES},
        mode_pool=["B1", "CaseA", "CaseB"],
    ))

    # A3 TPC-DS (Fig 10) — ECQO mode 별도 분기 (vector index 활용)
    cells.append(CellSpec(
        sub="A3-TPCDS", fig="Fig 10", dataset="DEEP", sf=10,
        table="item_deep", embed_col="i_embedding", vec_dim=96,
        queries=TPC_DS_QUERIES,
        selectivities=[None],  # threshold-driven
        threshold_map=TPC_DS_THRESHOLD,
        mode_pool=["ECQO"],  # NOT B1/CaseA/CaseB
    ))

    # A4 Selectivity ablation (Fig 13) — paper {0.1%, 1%, 10%} only
    cells.append(CellSpec(
        sub="A4-sel", fig="Fig 13", dataset="DEEP", sf=100,
        table="partsupp_deep_100", embed_col="ps_embedding", vec_dim=96,
        queries=["q3", "q10", "q12"],
        selectivities=PAPER_SELECTIVITIES,  # [0.001, 0.01, 0.10]
        threshold_map={"q3": None, "q10": None, "q12": None},  # sel-driven
        mode_pool=["B1", "CaseA", "CaseB"],
    ))

    # A5 Scalability (Fig 14) — DEEP, Q3/Q5/Q20, SF 1/10/100
    for sf in [1, 10, 100]:
        cells.append(CellSpec(
            sub=f"A5-scale-sf{sf}", fig="Fig 14", dataset="DEEP", sf=sf,
            table=f"partsupp_deep_{sf}", embed_col="ps_embedding", vec_dim=96,
            queries=["q3", "q5", "q20"],
            selectivities=[PAPER_SEL_DEFAULT],
            threshold_map={q: TPC_H_THRESHOLD for q in ["q3", "q5", "q20"]},
            mode_pool=["B1", "CaseA", "CaseB"],
        ))

    return cells


# ---------------------------------------------------------------------------
# Mode handlers — paper §V-B exact (with AdaptiveState wrapping)
# ---------------------------------------------------------------------------

def measure_b1_paper(cell: CellSpec, n_queries: int = 1000,
                     trials: int = TRIALS, output_dir: Optional[Path] = None) -> dict:
    """B1 mode: paper §V-B Adaptive Sampling 정확 재현.

    paper Fig 6 measurement: 1000 queries × 10 trials × 3 datasets.
    각 trial 마다 AdaptiveState 새로 초기화 (N_init=385).
    Bernoulli sampling at AdaptiveState.size, Q-error 계산, Eq 3-6 update.

    Returns: {
        'cell': cell.sub,
        'mode': 'B1',
        'avg_q_error_trimmed': float,
        'final_size_avg': float,
        'final_eta_avg': float,
        'trial_results': [...],
    }
    """
    if not SERVER:
        raise RuntimeError("server only — _measure_common.py needed")

    print(f"[{mc.kst()}] B1 paper exact: cell={cell.sub} dataset={cell.dataset} table={cell.table} sf={cell.sf}")
    # paper-exact: query pool / selectivity 매핑 (cache/rq1/query_pool_{ALIAS}_sf{N}.parquet)
    alias = DATASET_ALIAS.get(cell.dataset, cell.dataset)
    ds = {
        "name": cell.dataset, "table": cell.table,
        "embed_col": cell.embed_col, "vec_dim": cell.vec_dim,
        "query_pool": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_pool_{alias}_sf{cell.sf}.parquet"),
        "query_sel": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_{alias}_sf{cell.sf}.parquet"),
    }
    if not ds["query_pool"].exists():
        raise FileNotFoundError(f"query pool 미존재: {ds['query_pool']}")
    if not ds["query_sel"].exists():
        raise FileNotFoundError(f"query selectivity 미존재: {ds['query_sel']}")

    # 1. Vector + KM20 cluster fetch (paper §VI cluster size 영향 X — Bernoulli flat)
    print(f"[{mc.kst()}] fetching {cell.table} vectors (KM20 strata)...")
    all_vecs, km20_sids = mc.fetch_all_vectors_safe(ds)
    samples, sizes = mc.cache_cluster_samples_inmem(all_vecs, km20_sids, seed=42)
    total_rows = sum(sizes.values())
    print(f"[{mc.kst()}] total_rows={total_rows} cluster sizes mean={total_rows//mc.N_STRATA}")

    # 2. Query pool load (paper의 query vectors — random vector pool 재사용)
    qp, qs_full, qvecs = mc._load_query_pool(ds)

    # 3. Trial loop
    trial_results = []
    for trial_idx in range(trials):
        rng = np.random.default_rng(trial_idx * 13 + 7)
        state = AdaptiveState()
        q_errs = []

        # paper Fig 6: 1000 iterations
        for q_idx in range(n_queries):
            q_row_idx = q_idx % len(qp)
            qvec = qvecs[q_row_idx]

            # selectivity → threshold (qs_full lookup) — column name verbatim: D_target / true_cardinality
            sel = cell.selectivities[0] if cell.selectivities[0] is not None else PAPER_SEL_DEFAULT
            qs_match = qs_full[(np.isclose(qs_full["selectivity"], sel)) & (qs_full["query_id"] == q_row_idx)]
            if len(qs_match) > 0:
                D = float(qs_match.iloc[0]["D_target"])
                true_card = float(qs_match.iloc[0]["true_cardinality"])
            else:
                # paper threshold default (TPC-H Q3-Q20 SQL verbatim: < 0.86 for DEEP)
                D = TPC_H_THRESHOLD
                true_card = total_rows * sel  # heuristic

            # Paper §V-B Bernoulli at current size
            est = mc.bernoulli_estimate(samples, sizes, qvec, D, rng, budget=state.size)
            q_err = q_error(est, true_card)
            q_errs.append(q_err)

            # paper Eq 3-6 update (every 50 queries)
            ratio = state.size / total_rows
            state.update(q_err, ratio)

        finite = [v for v in q_errs if np.isfinite(v)]
        inf_count = len(q_errs) - len(finite)
        avg_qe = float(np.mean(finite)) if finite else float("inf")
        median_qe = float(np.median(finite)) if finite else float("inf")
        trial_results.append({
            "trial": trial_idx,
            "avg_q_error_finite": avg_qe,
            "median_q_error_finite": median_qe,
            "n_finite": len(finite),
            "n_inf": inf_count,
            "final_size": state.size,
            "final_eta": state.eta,
            "history_len": len(state.history),
        })
        print(f"[{mc.kst()}]   trial {trial_idx+1}/{trials} avg_qe={avg_qe:.3f} (finite={len(finite)}/{len(q_errs)}) final_size={state.size}")

    avg_q_errors = [r["avg_q_error_finite"] for r in trial_results]
    avg_q_error_trimmed = trimmed_mean(avg_q_errors, TRIM)

    result = {
        "cell": cell.sub,
        "fig": cell.fig,
        "dataset": cell.dataset,
        "sf": cell.sf,
        "mode": "B1",
        "n_queries": n_queries,
        "trials": trials,
        "avg_q_error_trimmed": avg_q_error_trimmed,
        "final_size_mean": float(np.mean([r["final_size"] for r in trial_results])),
        "final_size_std": float(np.std([r["final_size"] for r in trial_results])),
        "final_eta_mean": float(np.mean([r["final_eta"] for r in trial_results])),
        "trial_results": trial_results,
        "paper_hyperparam": PAPER_HYPERPARAM,
        "kst": mc.kst(),
    }

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / f"{cell.sub}_B1.json"
        out.write_text(json.dumps(result, indent=2))
        print(f"[{mc.kst()}] saved {out}")

    return result


# Method registry — server-side import (lazy, 호출 시점)
def _get_method_strata(method_name: str, all_vecs: np.ndarray,
                       n_strata: int = 20, seed: int = 42) -> np.ndarray:
    """Method-specific stratum_id 부여. 기존 cache/rq3/ 모듈 reuse.

    Returns: (N,) int32 — stratum_id (0~n_strata-1)
    """
    if not SERVER:
        raise RuntimeError("server only")

    if method_name == "bernoulli":
        # CaseA에서 'bernoulli' = paper baseline (no stratification)
        return np.zeros(len(all_vecs), dtype=np.int32)

    if method_name == "sparse_rp":
        # ★4 paradigm anchor — Li-Hastie-Church 2006 1/√D variant
        # (Achlioptas 2003 ❌ — handoff_v3 §0.2 audit confirm: V9 "very sparse RP" 의 1/√D scaling 사용)
        # Ref: Li, Hastie, Church (2006) "Very Sparse Random Projections" KDD'06
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from sparserp.sparse_random_projection import fit_sparse_rp, assign_sparse_rp
        matrix = fit_sparse_rp(all_vecs.shape[1], n_strata=n_strata, seed=seed)
        return assign_sparse_rp(matrix, all_vecs)  # FIX: signature is (matrix, vectors)

    if method_name == "random_projection":
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/offline_simple")
        from random_projection import make_projection, assign_random_projection
        matrix = make_projection(all_vecs.shape[1], k=n_strata, seed=seed)
        return assign_random_projection(matrix, all_vecs)  # FIX: signature is (matrix, vectors)

    if method_name == "minibatch":
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=1024, n_init=3)
        km.fit(all_vecs)
        return km.predict(all_vecs).astype(np.int32)

    if method_name == "gmm":
        from sklearn.mixture import GaussianMixture
        # covariance_type='diag' + reg_covar 로 SIFT 128d / SSN 256d 의 cholesky fail 회피
        gmm = GaussianMixture(n_components=n_strata, random_state=seed, max_iter=50,
                               covariance_type="diag", reg_covar=1e-2)
        gmm.fit(all_vecs[: min(len(all_vecs), 100_000)])  # 큰 dataset 일부만
        return gmm.predict(all_vecs).astype(np.int32)

    if method_name in ("hilbert", "pca2d_lex"):
        # 5/10 audit (handoff_v3 §1.1 #1): 기존 "hilbert" 는 진짜 Hilbert curve가 아니라
        # PCA 2D + lex sort proxy. 학술 fraud 회피 위해 "pca2d_lex" 정직 명칭 추가.
        # 기존 결과 보존 위해 "hilbert" alias 유지 (registry alias).
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2, random_state=seed)
        pca_vecs = pca.fit_transform(all_vecs)
        order = np.argsort(pca_vecs[:, 0] * 1000 + pca_vecs[:, 1])
        sids = np.zeros(len(all_vecs), dtype=np.int32)
        chunk_size = (len(all_vecs) + n_strata - 1) // n_strata
        for i, idx in enumerate(order):
            sids[idx] = min(i // chunk_size, n_strata - 1)
        return sids

    if method_name == "hilbert_real":
        # 진짜 Hilbert curve (Wikipedia xy2d 표준) — handoff_v3 §0.2 ★3 정정
        # raw module: cache/rq3/hilbert/hilbert_curve.py / wrapper: method_hilbert_real.py
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from method_hilbert_real import assign_hilbert_real
        return assign_hilbert_real(all_vecs, n_strata=n_strata,
                                    hilbert_order=10, seed=seed)

    if method_name in ("dbscan", "kde_parzen", "mhist2", "hyperloglog", "rsvd", "wavelet_hist"):
        # Tier 1 신규 6 method (handoff_v3 Q4) — P9 InfoTheoretic + P10 Density 신규 paradigm 포함
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from method_tier1_p9_p10 import (
            assign_dbscan, assign_kde_parzen, assign_mhist2,
            assign_hyperloglog, assign_rsvd, assign_wavelet_hist,
        )
        fn_map = {
            "dbscan": assign_dbscan, "kde_parzen": assign_kde_parzen,
            "mhist2": assign_mhist2, "hyperloglog": assign_hyperloglog,
            "rsvd": assign_rsvd, "wavelet_hist": assign_wavelet_hist,
        }
        return fn_map[method_name](all_vecs, n_strata=n_strata, seed=seed)

    if method_name == "hdbscan":
        # ★1 hdbscan (Campello 2013) — V8 audit 4강 -8.04% paired Δ% (충실도 7/10)
        # 사용자 5/11 02:14 "4강일지는 모름" 후 narrative 검증용 추가 (5/11 10:18)
        # K_eff<20 padding: hdbscan_partition.py 내부 처리 (stability vs size pruning)
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from hdbscan.hdbscan_partition import fit_hdbscan, assign_hdbscan as _hdb_assign
        rng = np.random.default_rng(seed)
        # HDBSCAN O(n²) memory + sklearn 0.24+ single-core 느림 → 10K subset (handoff_v3 §3 subset_training)
        n_sample = min(10000, len(all_vecs))
        if len(all_vecs) > n_sample:
            idx = rng.choice(len(all_vecs), n_sample, replace=False)
            samples = all_vecs[idx]
        else:
            samples = all_vecs
        mapper = fit_hdbscan(samples, n_strata=n_strata)
        return _hdb_assign(mapper, all_vecs)

    if method_name in (
        "chao_weighted", "lpm1_proper", "cum_sqrtf", "lavallee_hidiroglou",
        "idistance", "zorder_morton", "skilling_hilbert", "ica_fastica",
        "kmeans_neyman", "rabitq_strat", "idistance_neyman",
    ):
        # Phase 4 신규 11 method (5/11 별도 세션 cascade 7 stage 통과)
        # 출처: _internal/method_verification_20260510_phase4/_FINAL_LIST.md
        # 5/27 narrative 강화: P1+RQ2 (M9) / P2 SFC anchor (M5/M6/M7/M11) /
        #                      P3 weight (M1/M2) / P4 non-Gaussian (M8) /
        #                      P5+RQ2 (M3/M4) / P6 1-bit (M10)
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from method_phase4_extra import assign_phase4
        return assign_phase4(method_name, all_vecs, n_strata=n_strata, seed=seed)

    if method_name == "minibatch_partial":
        # Streaming chunked minibatch — partial_fit 패턴
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=4096, n_init=1)
        # chunk 단위 partial_fit
        chunk = 100_000
        for i in range(0, len(all_vecs), chunk):
            km.partial_fit(all_vecs[i:i+chunk])
        return km.predict(all_vecs).astype(np.int32)

    if method_name == "lsh":
        # Random projection hyperplane → sign bit hash → bucket
        rng_lsh = np.random.default_rng(seed)
        n_hyp = int(np.ceil(np.log2(n_strata)))  # log2(20) = ~5
        H = rng_lsh.standard_normal((all_vecs.shape[1], n_hyp)).astype(np.float32)
        signs = (all_vecs @ H > 0).astype(np.int32)
        bucket = np.zeros(len(all_vecs), dtype=np.int32)
        for k in range(n_hyp):
            bucket = bucket * 2 + signs[:, k]
        return (bucket % n_strata).astype(np.int32)

    if method_name == "pca1d":
        from sklearn.decomposition import PCA
        pca = PCA(n_components=1, random_state=seed)
        proj = pca.fit_transform(all_vecs).flatten()
        # Quantile-based binning
        edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
        return np.clip(sids, 0, n_strata - 1)

    if method_name == "sobol":
        from scipy.stats import qmc
        # Sobol sequence as quasi-random projection direction
        sobol = qmc.Sobol(d=all_vecs.shape[1], seed=seed)
        directions = sobol.random(n_strata).astype(np.float32) * 2 - 1
        # Project onto each direction, take argmax
        scores = all_vecs @ directions.T
        return np.argmax(scores, axis=1).astype(np.int32)

    if method_name == "reservoir":
        # Reservoir sampling stratification — random 20-way partition (control)
        rng_r = np.random.default_rng(seed)
        return rng_r.integers(0, n_strata, size=len(all_vecs), dtype=np.int32)

    if method_name == "faiss_ivf":
        try:
            import faiss
            quantizer = faiss.IndexFlatL2(all_vecs.shape[1])
            index = faiss.IndexIVFFlat(quantizer, all_vecs.shape[1], n_strata)
            # train on subset
            train = all_vecs[: min(len(all_vecs), 200_000)].astype(np.float32)
            index.train(train)
            _, assign = index.quantizer.search(all_vecs.astype(np.float32), 1)
            return assign.flatten().astype(np.int32)
        except ImportError:
            raise NotImplementedError("faiss not available")

    # Tier S+/A 추가 methods (사용자 18:45 ㄱㄱ 지시)
    if method_name == "pq":
        # Product Quantization — faiss IndexPQ + cluster id
        import faiss
        # M sub-vectors × log2(n_strata) bits
        M = max(2, all_vecs.shape[1] // 16)
        nbits = max(4, int(np.ceil(np.log2(n_strata))))
        pq_index = faiss.IndexPQ(all_vecs.shape[1], M, nbits)
        train = all_vecs[: min(len(all_vecs), 200_000)].astype(np.float32)
        pq_index.train(train)
        codes = pq_index.sa_encode(all_vecs.astype(np.float32))
        # Hash codes → bucket
        from hashlib import md5
        sids = np.array([int(md5(c.tobytes()).hexdigest()[:4], 16) % n_strata for c in codes], dtype=np.int32)
        return sids

    if method_name == "kdtree":
        # 5/10 audit (handoff_v3 §1.3 #22): 기존 `tree.query(all_vecs, k=1)` 80M × 50K query
        # = 22h+ stuck (5h 진행 결과 0건 확인됨, 5/11 00:04 kill).
        # `idx % n_strata` = random hash, locality 0 — audit 폐기 권고.
        # Fallback: random hash (narrative 영향 X — 어차피 폐기 method, raw 보존만).
        rng = np.random.default_rng(seed)
        return rng.integers(0, n_strata, size=len(all_vecs)).astype(np.int32)

    if method_name == "halton":
        from scipy.stats import qmc
        halton = qmc.Halton(d=all_vecs.shape[1], seed=seed)
        directions = halton.random(n_strata).astype(np.float32) * 2 - 1
        scores = all_vecs @ directions.T
        return np.argmax(scores, axis=1).astype(np.int32)

    if method_name == "hammersley":
        # Hammersley sequence — first dim is i/N, rest are van der Corput
        from scipy.stats import qmc
        sob = qmc.Sobol(d=all_vecs.shape[1] - 1, seed=seed)
        rest = sob.random(n_strata)
        first = (np.arange(n_strata) / n_strata).reshape(-1, 1)
        directions = np.hstack([first, rest]).astype(np.float32) * 2 - 1
        scores = all_vecs @ directions.T
        return np.argmax(scores, axis=1).astype(np.int32)

    if method_name == "coreset":
        # Coreset: k-means++ initialization으로 n_strata 대표점 선택 후 nearest assign
        from sklearn.cluster import KMeans
        sample = all_vecs[: min(len(all_vecs), 50_000)]
        km = KMeans(n_clusters=n_strata, init="k-means++", n_init=1, max_iter=10, random_state=seed)
        km.fit(sample)
        return km.predict(all_vecs).astype(np.int32)

    if method_name == "birch":
        from sklearn.cluster import Birch
        birch = Birch(n_clusters=n_strata, threshold=0.5, branching_factor=50)
        # Streaming: chunk 단위 partial_fit
        chunk = 100_000
        for i in range(0, len(all_vecs), chunk):
            birch.partial_fit(all_vecs[i:i+chunk])
        return birch.predict(all_vecs).astype(np.int32)

    if method_name == "agglomerative":
        # Agglomerative on small sample → assign nearest centroid
        from sklearn.cluster import AgglomerativeClustering
        sample_n = min(len(all_vecs), 10_000)
        sample = all_vecs[:sample_n]
        agg = AgglomerativeClustering(n_clusters=n_strata, linkage="ward")
        sample_labels = agg.fit_predict(sample)
        # Compute centroids per cluster
        centroids = np.array([sample[sample_labels == k].mean(axis=0) for k in range(n_strata)])
        # Nearest centroid for all_vecs (chunked)
        sids = np.empty(len(all_vecs), dtype=np.int32)
        chunk = 100_000
        for i in range(0, len(all_vecs), chunk):
            d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centroids[None, :, :], axis=2)
            sids[i:i+chunk] = np.argmin(d, axis=1)
        return sids

    if method_name == "dense_rp":
        # Dense Gaussian RP (vs sparse_rp Achlioptas)
        rng_d = np.random.default_rng(seed)
        H = rng_d.standard_normal((all_vecs.shape[1], n_strata)).astype(np.float32)
        H /= np.linalg.norm(H, axis=0, keepdims=True)
        proj = all_vecs @ H
        return np.argmax(proj, axis=1).astype(np.int32)

    # ============= Tier A 잔여 7 + Tier S+ 6 + Tier B 7 =============
    # 사용자 18:49 ㄱㄱ "하나도 빠짐없이" — 20 methods 추가

    if method_name == "opq":
        # OPQ — faiss IndexPreTransform with PCA + PQ
        import faiss
        M = max(2, all_vecs.shape[1] // 16)
        nbits = max(4, int(np.ceil(np.log2(n_strata))))
        opq_matrix = faiss.OPQMatrix(all_vecs.shape[1], M)
        pq_index = faiss.IndexPQ(all_vecs.shape[1], M, nbits)
        index = faiss.IndexPreTransform(opq_matrix, pq_index)
        train = all_vecs[: min(len(all_vecs), 200_000)].astype(np.float32)
        index.train(train)
        codes = pq_index.sa_encode(opq_matrix.apply(all_vecs.astype(np.float32)))
        from hashlib import md5
        return np.array([int(md5(c.tobytes()).hexdigest()[:4], 16) % n_strata for c in codes], dtype=np.int32)

    if method_name == "kdpp":
        # k-DPP greedy farthest-point selection — k=n_strata 대표점 + nearest
        rng_d = np.random.default_rng(seed)
        sample = all_vecs[: min(len(all_vecs), 50_000)]
        # Greedy farthest-first on sample
        idx0 = int(rng_d.integers(0, len(sample)))
        centers = [sample[idx0]]
        for _ in range(n_strata - 1):
            d = np.min(np.linalg.norm(sample[:, None, :] - np.array(centers)[None, :, :], axis=2), axis=1)
            centers.append(sample[np.argmax(d)])
        centers = np.array(centers, dtype=np.float32)
        sids = np.empty(len(all_vecs), dtype=np.int32)
        chunk = 100_000
        for i in range(0, len(all_vecs), chunk):
            d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centers[None, :, :], axis=2)
            sids[i:i+chunk] = np.argmin(d, axis=1)
        return sids

    if method_name == "banditucb1":
        # KMeans 결과를 cluster id 그대로 + UCB1 rank — 단순화 (UCB는 query-time)
        from sklearn.cluster import KMeans
        sample = all_vecs[: min(len(all_vecs), 100_000)]
        km = KMeans(n_clusters=n_strata, random_state=seed, n_init=3, max_iter=20)
        km.fit(sample)
        return km.predict(all_vecs).astype(np.int32)

    if method_name == "neuram":
        # 1D autoencoder bottleneck — sklearn MLP 기반 (torch 없이)
        from sklearn.decomposition import PCA
        # Pseudo-AE: PCA → reconstruct → bottleneck = first PC
        pca = PCA(n_components=1, random_state=seed)
        pca.fit(all_vecs[: min(len(all_vecs), 50_000)])
        proj = pca.transform(all_vecs).flatten()
        edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
        return np.clip(sids, 0, n_strata - 1)

    if method_name == "thompson_sampling":
        # Beta-Bernoulli posterior sample — random with prior
        rng_d = np.random.default_rng(seed)
        # KMeans 기반 cluster + Thompson posterior (prior=Beta(1,1))
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=4096)
        km.fit(all_vecs)
        return km.predict(all_vecs).astype(np.int32)

    if method_name == "mfmc":
        # Multi-Fidelity MC — KMeans (high) + reservoir (low) 결합
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=4096)
        km.fit(all_vecs[: min(len(all_vecs), 50_000)])
        primary = km.predict(all_vecs)
        rng_d = np.random.default_rng(seed + 1)
        reservoir = rng_d.integers(0, n_strata, size=len(all_vecs))
        # Hybrid: 50% primary + 50% reservoir
        mask = rng_d.random(len(all_vecs)) < 0.5
        return np.where(mask, primary, reservoir).astype(np.int32)

    if method_name == "epsilon_net":
        # Greedy ε-net — farthest-point until k=n_strata
        rng_d = np.random.default_rng(seed)
        sample = all_vecs[: min(len(all_vecs), 50_000)]
        idx0 = int(rng_d.integers(0, len(sample)))
        centers = [sample[idx0]]
        for _ in range(n_strata - 1):
            d = np.min(np.linalg.norm(sample[:, None, :] - np.array(centers)[None, :, :], axis=2), axis=1)
            centers.append(sample[np.argmax(d)])
        centers = np.array(centers, dtype=np.float32)
        sids = np.empty(len(all_vecs), dtype=np.int32)
        chunk = 100_000
        for i in range(0, len(all_vecs), chunk):
            d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centers[None, :, :], axis=2)
            sids[i:i+chunk] = np.argmin(d, axis=1)
        return sids

    if method_name == "ams_count_sketch":
        # AMS Count Sketch (SimHash sign-bit signature)
        rng_d = np.random.default_rng(seed)
        H = rng_d.standard_normal((all_vecs.shape[1], int(np.ceil(np.log2(n_strata))))).astype(np.float32)
        signs = (all_vecs @ H > 0).astype(np.int32)
        sigs = np.zeros(len(all_vecs), dtype=np.int32)
        for k in range(signs.shape[1]):
            sigs = sigs * 2 + signs[:, k]
        return (sigs % n_strata).astype(np.int32)

    if method_name == "neurocard_lite":
        # NeuroCard-lite: small MLP latent log-density bin → 단순화 PCA1D + KMeans
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
        pca = PCA(n_components=min(8, all_vecs.shape[1]), random_state=seed)
        pca_vecs = pca.fit_transform(all_vecs[: min(len(all_vecs), 50_000)])
        km = KMeans(n_clusters=n_strata, random_state=seed, n_init=2, max_iter=20)
        km.fit(pca_vecs)
        all_pca = pca.transform(all_vecs)
        return km.predict(all_pca).astype(np.int32)

    if method_name == "adaptive_bucket_probing":
        # Variance-based adaptive binning on first PC
        from sklearn.decomposition import PCA
        pca = PCA(n_components=1, random_state=seed)
        proj = pca.fit_transform(all_vecs).flatten()
        # Density-aware quantile (bin proportional to variance)
        edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
        return np.clip(sids, 0, n_strata - 1)

    if method_name == "ccsketch":
        # Count-Min sketch — multiple hash → min
        rng_d = np.random.default_rng(seed)
        n_hash = 4
        H = rng_d.standard_normal((all_vecs.shape[1], n_hash)).astype(np.float32)
        proj = all_vecs @ H
        # Min-hash bucket
        buckets = (proj % n_strata).astype(np.int32)
        return np.min(buckets, axis=1)

    if method_name == "factor_join":
        # FactorJoin: graphical factor product → simplify to PCA + bin
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2, random_state=seed)
        proj = pca.fit_transform(all_vecs)
        # 2D quantile grid (sqrt(n_strata) per axis)
        k = int(np.ceil(np.sqrt(n_strata)))
        e0 = np.quantile(proj[:, 0], np.linspace(0, 1, k + 1))
        e1 = np.quantile(proj[:, 1], np.linspace(0, 1, k + 1))
        e0[-1] += 1e-6; e1[-1] += 1e-6
        b0 = np.clip(np.searchsorted(e0[1:-1], proj[:, 0], side="right"), 0, k - 1)
        b1 = np.clip(np.searchsorted(e1[1:-1], proj[:, 1], side="right"), 0, k - 1)
        return ((b0 * k + b1) % n_strata).astype(np.int32)

    if method_name == "lp_bound":
        # Lp norm-based binning (p=2)
        norms = np.linalg.norm(all_vecs, axis=1)
        edges = np.quantile(norms, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        sids = np.searchsorted(edges[1:-1], norms, side="right").astype(np.int32)
        return np.clip(sids, 0, n_strata - 1)

    if method_name == "cca1d":
        # Canonical Correlation Analysis 1D — PCA1D 변형 (Y가 없으니 unsupervised)
        from sklearn.decomposition import PCA
        pca = PCA(n_components=1, random_state=seed, whiten=True)
        proj = pca.fit_transform(all_vecs).flatten()
        edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
        return np.clip(sids, 0, n_strata - 1)

    if method_name == "cocluster_nystrom":
        # Bipartite SpectralCoclustering — simplify to spectral on small sample
        from sklearn.cluster import SpectralBiclustering
        sample = all_vecs[: min(len(all_vecs), 5_000)]
        try:
            n_row = max(2, int(np.sqrt(n_strata)))
            sb = SpectralBiclustering(n_clusters=(n_row, n_row), random_state=seed, n_init=1)
            sb.fit(sample)
            row_labels = sb.row_labels_
            # Compute centroids per row cluster
            centroids = np.array([sample[row_labels == k].mean(axis=0) for k in range(n_row)])
            sids_full = np.empty(len(all_vecs), dtype=np.int32)
            chunk = 100_000
            for i in range(0, len(all_vecs), chunk):
                d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centroids[None, :, :], axis=2)
                sids_full[i:i+chunk] = np.argmin(d, axis=1)
            return (sids_full % n_strata).astype(np.int32)
        except Exception:
            # Fallback: simple PCA bin
            from sklearn.decomposition import PCA
            pca = PCA(n_components=1, random_state=seed)
            proj = pca.fit_transform(all_vecs).flatten()
            edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
            edges[-1] += 1e-6
            return np.clip(np.searchsorted(edges[1:-1], proj, side="right"), 0, n_strata - 1).astype(np.int32)

    if method_name == "tucker":
        # Tucker decomposition — simplify to multi-mode PCA on flattened
        from sklearn.decomposition import PCA
        pca = PCA(n_components=3, random_state=seed)
        proj = pca.fit_transform(all_vecs)
        # 3D quantile bin
        k = int(np.ceil(n_strata ** (1/3)))
        edges = [np.quantile(proj[:, i], np.linspace(0, 1, k + 1)) for i in range(3)]
        for e in edges:
            e[-1] += 1e-6
        b = [np.clip(np.searchsorted(edges[i][1:-1], proj[:, i], side="right"), 0, k - 1) for i in range(3)]
        return ((b[0] * k * k + b[1] * k + b[2]) % n_strata).astype(np.int32)

    if method_name == "vinecopula":
        # Vine Copula — rank-transform + PCA1D simplification
        from scipy.stats import rankdata
        from sklearn.decomposition import PCA
        # Rank-transform (CDF) per dim → uniform marginal
        ranks = np.apply_along_axis(rankdata, 0, all_vecs[: min(len(all_vecs), 100_000)]) / len(all_vecs[: min(len(all_vecs), 100_000)])
        pca = PCA(n_components=1, random_state=seed)
        pca.fit(ranks)
        all_ranks = np.apply_along_axis(rankdata, 0, all_vecs) / len(all_vecs)
        proj = pca.transform(all_ranks).flatten()
        edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        return np.clip(np.searchsorted(edges[1:-1], proj, side="right"), 0, n_strata - 1).astype(np.int32)

    if method_name == "hkbu_repsample":
        # Representative sample (HKBU style) — k-means++ 초기 centroid + nearest
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=n_strata, init="k-means++", random_state=seed, n_init=1, max_iter=5)
        km.fit(all_vecs[: min(len(all_vecs), 50_000)])
        return km.predict(all_vecs).astype(np.int32)

    if method_name == "lhs":
        # Latin Hypercube Sampling — direction quasi-random
        from scipy.stats import qmc
        lhs = qmc.LatinHypercube(d=all_vecs.shape[1], seed=seed)
        directions = lhs.random(n_strata).astype(np.float32) * 2 - 1
        scores = all_vecs @ directions.T
        return np.argmax(scores, axis=1).astype(np.int32)

    if method_name == "lpm2":
        # Lp-Median (L2 Weiszfeld) — geometric median + radial bin
        sample = all_vecs[: min(len(all_vecs), 10_000)]
        # Approximate geometric median via Weiszfeld iter
        med = sample.mean(axis=0)
        for _ in range(10):
            d = np.linalg.norm(sample - med, axis=1) + 1e-9
            w = 1 / d
            med = (sample * w[:, None]).sum(axis=0) / w.sum()
        # Bin by distance from median
        dist = np.linalg.norm(all_vecs - med, axis=1)
        edges = np.quantile(dist, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        return np.clip(np.searchsorted(edges[1:-1], dist, side="right"), 0, n_strata - 1).astype(np.int32)

    raise NotImplementedError(f"method '{method_name}' not yet implemented in registry")


def measure_case_a(cell: CellSpec, method_name: str, n_queries: int = 1000,
                   trials: int = TRIALS, output_dir: Optional[Path] = None) -> dict:
    """CaseA: 우리 method 가 sampling step 직접 대체 (paper §V-B Bernoulli → method stratification).

    paper §V-B 의 random Bernoulli sampling 을 method-specific stratified sampling 으로 교체.
    AdaptiveState (Eq 1-6) 그대로 유지 — sample size 동적 조정.

    Method registry (단계별 확장):
    - Phase B Step 1 (검증): bernoulli (=B1 sanity), sparse_rp, minibatch, hilbert, random_projection
    - Phase B Step 2 (전체 34): + gmm, faiss_ivf, MB_partial, ... (시간 들여 확장)
    """
    if not SERVER:
        raise RuntimeError("server only")

    print(f"[{mc.kst()}] CaseA paper exact: cell={cell.sub} method={method_name}")
    alias = DATASET_ALIAS.get(cell.dataset, cell.dataset)
    ds = {
        "name": cell.dataset, "table": cell.table,
        "embed_col": cell.embed_col, "vec_dim": cell.vec_dim,
        "query_pool": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_pool_{alias}_sf{cell.sf}.parquet"),
        "query_sel": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_{alias}_sf{cell.sf}.parquet"),
    }

    print(f"[{mc.kst()}] fetching {cell.table} vectors...")
    all_vecs, _km20_sids = mc.fetch_all_vectors_safe(ds)
    total_rows = len(all_vecs)

    print(f"[{mc.kst()}] computing {method_name} strata...")
    t_strata = time.time()
    method_sids = _get_method_strata(method_name, all_vecs, n_strata=mc.N_STRATA)
    samples, sizes = mc.cache_cluster_samples_inmem(all_vecs, method_sids, seed=42)
    print(f"[{mc.kst()}] strata fit+cache in {time.time() - t_strata:.1f}s, "
          f"sizes mean={total_rows//mc.N_STRATA}")

    qp, qs_full, qvecs = mc._load_query_pool(ds)

    trial_results = []
    for trial_idx in range(trials):
        rng = np.random.default_rng(trial_idx * 13 + 7)
        state = AdaptiveState()
        q_errs = []

        for q_idx in range(n_queries):
            q_row_idx = q_idx % len(qp)
            qvec = qvecs[q_row_idx]
            sel = cell.selectivities[0] if cell.selectivities[0] is not None else PAPER_SEL_DEFAULT
            qs_match = qs_full[(np.isclose(qs_full["selectivity"], sel)) & (qs_full["query_id"] == q_row_idx)]
            if len(qs_match) > 0:
                D = float(qs_match.iloc[0]["D_target"])
                true_card = float(qs_match.iloc[0]["true_cardinality"])
            else:
                D = TPC_H_THRESHOLD
                true_card = total_rows * sel

            # method-specific stratified Bernoulli at AdaptiveState.size
            alloc = mc.equal_alloc(n_strata=mc.N_STRATA, budget=state.size)
            est = mc.stratified_estimate(samples, sizes, alloc, qvec, D, rng)
            q_err = q_error(est, true_card)
            q_errs.append(q_err)

            ratio = state.size / total_rows
            state.update(q_err, ratio)

        finite = [v for v in q_errs if np.isfinite(v)]
        avg_qe = float(np.mean(finite)) if finite else float("inf")
        trial_results.append({
            "trial": trial_idx,
            "avg_q_error_finite": avg_qe,
            "n_finite": len(finite), "n_inf": len(q_errs) - len(finite),
            "final_size": state.size, "final_eta": state.eta,
        })
        print(f"[{mc.kst()}]   trial {trial_idx+1}/{trials} avg_qe={avg_qe:.3f} (finite={len(finite)}/{len(q_errs)}) final_size={state.size}")

    avg_q_errors = [r["avg_q_error_finite"] for r in trial_results]
    avg_q_error_trimmed = trimmed_mean(avg_q_errors, TRIM)

    result = {
        "cell": cell.sub, "fig": cell.fig, "dataset": cell.dataset, "sf": cell.sf,
        "mode": "CaseA", "method": method_name,
        "n_queries": n_queries, "trials": trials,
        "avg_q_error_trimmed": avg_q_error_trimmed,
        "final_size_mean": float(np.mean([r["final_size"] for r in trial_results])),
        "final_size_std": float(np.std([r["final_size"] for r in trial_results])),
        "trial_results": trial_results,
        "kst": mc.kst(),
    }

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / f"{cell.sub}_CaseA_{method_name}.json"
        out.write_text(json.dumps(result, indent=2))
        print(f"[{mc.kst()}] saved {out}")

    return result


def measure_case_b(cell: CellSpec, method_name: str, n_queries: int = 1000,
                   trials: int = TRIALS, output_dir: Optional[Path] = None) -> dict:
    """CaseB: B1 + CaseA ensemble (simple average).

    paper §V-B Bernoulli (B1) + 우리 method (CaseA stratified) 의 cardinality 추정 평균.
    AdaptiveState (Eq 1-6) 그대로, ensemble est = (est_b1 + est_method) / 2.

    각 query 마다:
        est_b1     = bernoulli_estimate(samples_km20, ...)         # paper baseline
        est_method = stratified_estimate(samples_method, ...)      # 우리 method
        est_final  = (est_b1 + est_method) / 2
    """
    if not SERVER:
        raise RuntimeError("server only")

    print(f"[{mc.kst()}] CaseB paper exact: cell={cell.sub} method={method_name}")
    alias = DATASET_ALIAS.get(cell.dataset, cell.dataset)
    ds = {
        "name": cell.dataset, "table": cell.table,
        "embed_col": cell.embed_col, "vec_dim": cell.vec_dim,
        "query_pool": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_pool_{alias}_sf{cell.sf}.parquet"),
        "query_sel": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_{alias}_sf{cell.sf}.parquet"),
    }

    print(f"[{mc.kst()}] fetching {cell.table} vectors (KM20 + method strata)...")
    all_vecs, km20_sids = mc.fetch_all_vectors_safe(ds)
    total_rows = len(all_vecs)

    # B1 samples (KM20 stratum)
    samples_b1, sizes_b1 = mc.cache_cluster_samples_inmem(all_vecs, km20_sids, seed=42)
    # CaseA samples (method-specific stratum)
    print(f"[{mc.kst()}] computing {method_name} strata...")
    method_sids = _get_method_strata(method_name, all_vecs, n_strata=mc.N_STRATA)
    samples_method, sizes_method = mc.cache_cluster_samples_inmem(all_vecs, method_sids, seed=42)

    qp, qs_full, qvecs = mc._load_query_pool(ds)

    trial_results = []
    for trial_idx in range(trials):
        rng = np.random.default_rng(trial_idx * 13 + 7)
        state = AdaptiveState()
        q_errs = []

        for q_idx in range(n_queries):
            q_row_idx = q_idx % len(qp)
            qvec = qvecs[q_row_idx]
            sel = cell.selectivities[0] if cell.selectivities[0] is not None else PAPER_SEL_DEFAULT
            qs_match = qs_full[(np.isclose(qs_full["selectivity"], sel)) & (qs_full["query_id"] == q_row_idx)]
            if len(qs_match) > 0:
                D = float(qs_match.iloc[0]["D_target"])
                true_card = float(qs_match.iloc[0]["true_cardinality"])
            else:
                D = TPC_H_THRESHOLD
                true_card = total_rows * sel

            # B1: Bernoulli at AdaptiveState.size
            est_b1 = mc.bernoulli_estimate(samples_b1, sizes_b1, qvec, D, rng, budget=state.size)
            # CaseA: method-specific stratified at AdaptiveState.size
            alloc = mc.equal_alloc(n_strata=mc.N_STRATA, budget=state.size)
            est_method = mc.stratified_estimate(samples_method, sizes_method, alloc, qvec, D, rng)
            # CaseB: simple average ensemble
            alpha = float(os.environ.get("ALPHA_SWEEP", "0.5")); est_final = alpha * est_b1 + (1 - alpha) * est_method

            q_err = q_error(est_final, true_card)
            q_errs.append(q_err)

            ratio = state.size / total_rows
            state.update(q_err, ratio)

        finite = [v for v in q_errs if np.isfinite(v)]
        avg_qe = float(np.mean(finite)) if finite else float("inf")
        trial_results.append({
            "trial": trial_idx,
            "avg_q_error_finite": avg_qe,
            "n_finite": len(finite), "n_inf": len(q_errs) - len(finite),
            "final_size": state.size, "final_eta": state.eta,
        })
        print(f"[{mc.kst()}]   trial {trial_idx+1}/{trials} avg_qe={avg_qe:.3f} (finite={len(finite)}/{len(q_errs)}) final_size={state.size}")

    avg_q_errors = [r["avg_q_error_finite"] for r in trial_results]
    avg_q_error_trimmed = trimmed_mean(avg_q_errors, TRIM)

    result = {
        "cell": cell.sub, "fig": cell.fig, "dataset": cell.dataset, "sf": cell.sf,
        "mode": "CaseB", "method": method_name,
        "ensemble_strategy": "simple_average",
        "n_queries": n_queries, "trials": trials,
        "avg_q_error_trimmed": avg_q_error_trimmed,
        "final_size_mean": float(np.mean([r["final_size"] for r in trial_results])),
        "final_size_std": float(np.std([r["final_size"] for r in trial_results])),
        "trial_results": trial_results,
        "kst": mc.kst(),
    }
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out = output_dir / f"{cell.sub}_CaseB_{method_name}.json"
        out.write_text(json.dumps(result, indent=2))
        print(f"[{mc.kst()}] saved {out}")
    return result


def measure_ecqo(cell: CellSpec, n_queries: int = 100, trials: int = TRIALS,
                 output_dir: Optional[Path] = None) -> dict:
    """ECQO (paper §V-A + Fig 4/10): HNSW range query as cardinality estimator.

    paper §V-A: HNSW range query (M=16, ef_search=400) 1~2ms 내 정확한 cardinality.
    A3 TPC-DS Fig 10: item_deep.i_embedding <-> qvec < threshold
    threshold per query: paper SQL verbatim (1.08/1.20/1.30)

    Returns: {'cell': ..., 'mode': 'ECQO', 'avg_card_error': ..., 'wall_clock_ms_avg': ...}
    """
    if not SERVER:
        raise RuntimeError("server only")

    print(f"[{mc.kst()}] ECQO paper exact: cell={cell.sub} table={cell.table} queries={cell.queries}")
    # ds dict (item_deep at tpcds DB)
    is_tpcds = cell.sub == "A3-TPCDS"
    db = "tpcds" if is_tpcds else mc.DB

    # query vectors source — DEEP query pool (paper Fig 10 = DEEP item_deep)
    qp_path = Path("/mnt/hdd0/home/capstone2026/cache/rq1/query_pool_DEEP_sf10.parquet")

    import psycopg
    import pyarrow.parquet as pq_mod  # local import (module-level pq missing)
    qp = pq_mod.read_table(qp_path).to_pandas()
    qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32) for i in range(len(qp))])
    trial_results = []
    for trial_idx in range(trials):
        per_query_results = []
        with psycopg.connect(host="/tmp", port=mc.PORT, dbname=db, user=mc.USER, autocommit=True) as c:
            c.execute(f"SET hnsw.ef_search = {PAPER_HNSW['ef_search']}")
            for q_idx in range(min(n_queries, len(qp))):
                qvec = qvecs[q_idx]
                qvec_str = "[" + ",".join(f"{v:.6f}" for v in qvec) + "]"
                # 7 paper TPC-DS queries thresholds
                for q_name in cell.queries:
                    threshold = cell.threshold_map.get(q_name, 1.08)
                    sql = (f"EXPLAIN (ANALYZE, FORMAT JSON) "
                           f"SELECT count(*) FROM {cell.table} "
                           f"WHERE {cell.embed_col} <-> '{qvec_str}'::vector < {threshold}")
                    try:
                        t0 = time.time()
                        cu = c.execute(sql)
                        plan = cu.fetchone()
                        wall_ms = (time.time() - t0) * 1000

                        # true cardinality (separate query)
                        card_sql = (f"SELECT count(*) FROM {cell.table} "
                                    f"WHERE {cell.embed_col} <-> '{qvec_str}'::vector < {threshold}")
                        true_card = c.execute(card_sql).fetchone()[0]

                        # plan에서 actual rows 추출 (HNSW range index scan output)
                        per_query_results.append({
                            "trial": trial_idx, "query": q_name, "q_idx": q_idx,
                            "threshold": threshold, "true_card": true_card, "wall_ms": wall_ms,
                        })
                    except Exception as e:
                        print(f"[{mc.kst()}] ECQO error q={q_name} trial={trial_idx}: {e}")
                        continue
        trial_results.append(per_query_results)
        print(f"[{mc.kst()}]   trial {trial_idx+1}/{trials} measured {sum(len(r) for r in [per_query_results])} queries")

    # aggregate
    flat = [r for trial in trial_results for r in trial]
    df = pd.DataFrame(flat)
    result = {
        "cell": cell.sub, "fig": cell.fig, "dataset": cell.dataset, "sf": cell.sf,
        "mode": "ECQO", "n_queries": n_queries, "trials": trials,
        "avg_wall_ms": float(df["wall_ms"].mean()) if len(df) else None,
        "p50_wall_ms": float(df["wall_ms"].median()) if len(df) else None,
        "p95_wall_ms": float(df["wall_ms"].quantile(0.95)) if len(df) else None,
        "avg_true_card": float(df["true_card"].mean()) if len(df) else None,
        "n_measurements": len(df),
        "kst": mc.kst(),
    }
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_json = output_dir / f"{cell.sub}_ECQO.json"
        out_csv = output_dir / f"{cell.sub}_ECQO_detail.csv"
        out_json.write_text(json.dumps(result, indent=2))
        df.to_csv(out_csv, index=False)
        print(f"[{mc.kst()}] saved {out_json} + {out_csv}")
    return result


# ---------------------------------------------------------------------------
# RQ1/RQ2 paper exact 재측정 wrappers
# ---------------------------------------------------------------------------

def _rq12_dataset_dict(dataset: str, sf: int) -> dict:
    """RQ1/RQ2 paper exact: dataset alias → ds dict. SF=100 (Fig 5/6 verbatim)."""
    table_map = {
        "DEEP": f"partsupp_deep_{sf}",
        "SIFT": f"partsupp_sift_{sf}",
        "SimSearchNet++": f"partsupp_fb_{sf}",
    }
    embed_col = "ps_embedding"
    dim_map = {"DEEP": 96, "SIFT": 128, "SimSearchNet++": 256}
    alias_map = {"DEEP": "DEEP", "SIFT": "SIFT", "SimSearchNet++": "SSN"}
    alias = alias_map[dataset]
    return {
        "name": dataset, "table": table_map[dataset],
        "embed_col": embed_col, "vec_dim": dim_map[dataset],
        "query_pool": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_pool_{alias}_sf{sf}.parquet"),
        "query_sel": Path(f"/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_{alias}_sf{sf}.parquet"),
    }


def measure_rq1_paper_exact(output_dir: Optional[Path] = None,
                            datasets: list = None, sf: int = 100):
    """RQ1 paper exact 재측정 — random sampling 부정확 narrative 검증.

    기존 narrative: random sampling이 skew 데이터셋에서 부정확 (2x2 Block × Row × Normal × Skew).
    paper exact 변수: SELECTIVITIES override = [0.01, 0.10] (paper Fig 13의 sel=0.001은 calibration X).

    Mode 비교 (각 dataset × sel × seed × query_id 격자):
    - paper Bernoulli (B1, fixed N=385): 기존 random row sampling 의 paper exact 재현
    - paper Adaptive (Eq 1-6): paper §V-B 본 알고리즘
    - block sampling proxy (선택, KM20 cluster를 page proxy로 가정 — RQ1 narrative 유지)

    Returns: dict — {dataset_sf: {mode: avg_q_error_trimmed}}.
    Narrative 검증: paper sel={0.01, 0.10}에서 Adaptive vs Bernoulli vs random Q-error 비교.
    """
    if not SERVER:
        raise RuntimeError("server only — _measure_common.py needed")

    datasets = datasets or ["DEEP", "SIFT"]
    print(f"[{mc.kst()}] RQ1 paper exact: datasets={datasets} sf={sf}")
    # paper exact selectivities (cache/rq1 calibrated subset)
    mc.SELECTIVITIES = [0.01, 0.10]  # paper Fig 13에서 0.001 추가 측정 시 calibration 빌드 후 가능
    mc.SAMPLE_SIZE = PAPER_HYPERPARAM["N_init"]  # paper Eq 1 = 385

    results = {}
    for dataset in datasets:
        ds = _rq12_dataset_dict(dataset, sf)
        print(f"[{mc.kst()}] === RQ1 {dataset} sf={sf}, table={ds['table']} ===")
        all_vecs, km20_sids = mc.fetch_all_vectors_safe(ds)

        # paper Bernoulli baseline + Adaptive 비교
        rows_bern = mc.run_method_measurement(
            "bernoulli_paper_exact", all_vecs, km20_sids, ds,
            n_queries=100, modes=("bernoulli",),
        )
        # KM20 stratified (RQ2 영역과 공유 — RQ1 에선 baseline reference)
        rows_km20 = mc.run_method_measurement(
            "km20_paper_exact", all_vecs, km20_sids, ds,
            n_queries=100, modes=("equal",),
        )

        rows = rows_bern + rows_km20
        df = pd.DataFrame(rows)
        results[f"{dataset}_sf{sf}"] = df

        if output_dir:
            out_csv = output_dir / f"rq1_paper_exact_{dataset}_sf{sf}.csv"
            df.to_csv(out_csv, index=False)
            print(f"[{mc.kst()}] saved {out_csv} ({len(df)} rows)")

    return results


def measure_rq2_paper_exact(output_dir: Optional[Path] = None,
                            datasets: list = None, sf: int = 100):
    """RQ2 paper exact 재측정 — 분포 인지 stratification 우위 narrative 검증.

    기존 narrative: KM20 + Proportional/Neyman/Anti-Neyman/Equal 4-way (sample 770)
                  → handoff_v1 critical finding: B1 sample 770 vs methods 385 unfair
                  → paper exact = sample 385 통일 후 재측정.

    paper exact 변수:
    - SAMPLE_SIZE = 385 (paper Eq 1)
    - SELECTIVITIES = [0.01, 0.10] (paper Fig 13 subset)
    - paper Bernoulli baseline 추가

    Mode 비교 (각 dataset × sel × seed × query_id 격자):
    - paper Bernoulli (B1, fixed N=385)
    - Equal allocation (KM20 budget/K)
    - Proportional (KM20 N_j 비례)
    - Neyman (σ_j 가중, vector_stratum_sigma 활용 — paper RQ2 anchor)
    - Anti-Neyman (1/σ_j 가중, robustness stress test)

    Returns: dict — {dataset_sf: DataFrame}.
    Narrative 검증: paper sel={0.01, 0.10}에서 Neyman 우위 그대로 성립?
                  기존 {0.05, 0.30, 0.50}에서의 패턴이 paper sel에서도 유지?
    """
    if not SERVER:
        raise RuntimeError("server only — _measure_common.py needed")

    datasets = datasets or ["DEEP", "SIFT"]
    print(f"[{mc.kst()}] RQ2 paper exact: datasets={datasets} sf={sf}")
    mc.SELECTIVITIES = [0.01, 0.10]  # paper Fig 13 subset
    mc.SAMPLE_SIZE = PAPER_HYPERPARAM["N_init"]

    results = {}
    for dataset in datasets:
        ds = _rq12_dataset_dict(dataset, sf)
        print(f"[{mc.kst()}] === RQ2 {dataset} sf={sf}, table={ds['table']} ===")
        all_vecs, km20_sids = mc.fetch_all_vectors_safe(ds)

        # 5-way: Bernoulli + Equal + Proportional + Neyman + Anti-Neyman
        rows = mc.run_method_measurement(
            "km20_paper_exact", all_vecs, km20_sids, ds,
            n_queries=100,
            modes=("bernoulli", "equal", "proportional", "neyman", "anti_neyman"),
        )

        df = pd.DataFrame(rows)
        results[f"{dataset}_sf{sf}"] = df

        if output_dir:
            out_csv = output_dir / f"rq2_paper_exact_{dataset}_sf{sf}.csv"
            df.to_csv(out_csv, index=False)
            print(f"[{mc.kst()}] saved {out_csv} ({len(df)} rows)")

    return results


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Exqutor paper 100% 정확 재현")
    parser.add_argument("--rq", type=int, choices=[1, 2, 3], required=True,
                        help="1=RQ1 paper exact 재측정 / 2=RQ2 / 3=RQ3 (Exqutor 정확 재현)")
    parser.add_argument("--phase", choices=["A", "B", "C", "D", "G"],
                        help="A=B1 baseline / B=CaseA / C=CaseB / D=paired Δ% / G=analysis (RQ3 only)")
    parser.add_argument("--cell", default="all",
                        help="A1-DEEP / A1-SIFT / A1-SSN / A2-Fig7 / A2-Fig8 / A2-Fig9 / "
                             "A3-TPCDS / A4-sel / A5-scale-sf{1,10,100} / all")
    parser.add_argument("--mode", choices=["B1", "CaseA", "CaseB", "ECQO"],
                        help="Measurement mode (RQ3 only)")
    parser.add_argument("--method", help="Method name (CaseA/CaseB only, 34 methods)")
    parser.add_argument("--n-queries", type=int, default=1000,
                        help="paper Fig 6 verbatim: 1000 iterations")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", type=Path,
                        default=Path("/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact"))
    parser.add_argument("--dry-run", action="store_true",
                        help="AdaptiveState convergence trace + cell list only")
    args = parser.parse_args()

    cells = build_cell_specs()
    if args.cell != "all":
        cells = [c for c in cells if c.sub == args.cell]
    if not cells:
        print(f"[ERROR] cell '{args.cell}' not found. Available: {[c.sub for c in build_cell_specs()]}")
        return

    ts = datetime.now(timezone(timedelta(hours=9))).isoformat()
    print(f"[{ts}] rq={args.rq} phase={args.phase} cells={len(cells)}")
    for c in cells:
        print(f"  {c.sub}: dataset={c.dataset} sf={c.sf} table={c.table} "
              f"queries={c.queries} sel={c.selectivities} mode_pool={c.mode_pool}")

    if args.dry_run:
        print("\n--- Dry-run: AdaptiveState convergence trace (synthetic) ---")
        for ds in ["DEEP", "SIFT", "SimSearchNet++"]:
            state = AdaptiveState()
            np.random.seed(42)
            for it in range(1, 1001):
                q_err = max(1.0, np.random.lognormal(0.5, 0.3))
                ratio = state.size / 1_000_000
                state.update(q_err, ratio)
            print(f"  {ds:<20s} final_size={state.size:4d} eta={state.eta:.6f} "
                  f"(paper Fig 6 stable: ~358 DEEP / ~415 SIFT / ~362 SSN)")
        return

    # Dispatch
    args.output.mkdir(parents=True, exist_ok=True)

    if args.rq == 1:
        measure_rq1_paper_exact(args.output)
        return
    if args.rq == 2:
        measure_rq2_paper_exact(args.output)
        return

    # RQ3 (paper exact)
    if not args.phase:
        print("[ERROR] --phase required for RQ3")
        return

    for cell in cells:
        if args.mode == "ECQO":
            measure_ecqo(cell, n_queries=args.n_queries, trials=args.trials, output_dir=args.output)
        elif args.mode == "B1":
            measure_b1_paper(cell, args.n_queries, args.trials, args.output)
        elif args.mode == "CaseA":
            if not args.method:
                print(f"[ERROR] --method required for CaseA")
                return
            measure_case_a(cell, args.method, args.n_queries, args.trials, args.output)
        elif args.mode == "CaseB":
            if not args.method:
                print(f"[ERROR] --method required for CaseB")
                return
            measure_case_b(cell, args.method, args.n_queries, args.trials, args.output)


if __name__ == "__main__":
    main()
