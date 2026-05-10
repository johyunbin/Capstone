#!/usr/bin/env python3
"""
Multi-vector paradigm framework wrapper — RQ3 5-paradigm × 11-method 확장.

`measure_multi_4kang.py` (4 method) 의 11-method 확장. 5/8 20:48 paradigm
framework 확정 후, multi-table cell 에 대해 5 paradigm 의 representative
method 11종 측정.

Paradigm framework (5/8 20:43 Deep Review + user confirm 20:48):
  P1 Cluster:     HDBSCAN, MiniBatch, GMM
  P2 Spatial:     Hilbert, faiss_ivf
  P3 Streaming:   MB_partial, Reservoir
  P4 DimReduction: sparse_rp, PCA1D
  P5 Quasi-random: LSH, Sobol

5/9 18:50 — methods/* (Tier S/A/B) 신규 10종 통합 (extension):
  P6_Sketch:        AMSCountSketch (SimHash sign-bit signature)
  P7_Joint:         CCA1D (joint canonical 1D projection)
  P8_DimInvariant:  NeurAM (1D autoencoder bottleneck)
  P10_Theoretical:  DenseRP (Bingham-Mannila Gaussian RP)
  P11_Hierarchical: PQ (product quantization), CoCluster_Nystrom
                    (bipartite spectral co-clustering)
  P12_Adaptive:     BanditUCB1 (KMeans + UCB1 metadata)
  P13_AdaptiveSel:  Coreset (lightweight coreset sensitivity)
  P14_Latent:       NeuroCard (gaussian-head MLP latent log-density bin)
  S_MultiRelation:  WanderJoin (index-aware random walk)

Tier C (ConditionalAdaptive) 는 single-table single-vector 만 다루므로
이 multi-vector pipeline 에서는 무시 — measure_multi_adaptive_sampling /
run_adaptive_sampling 의 변형으로 별도 통합 필요.

Cell list (3 multi cell):
  - partsupp_deep_sift_10:  4-way (emb1=deep 96d, emb2=sift 128d)
  - partsupp_deep_wiki_10:  4-way (emb1=deep 96d, emb2=wiki 768d)
  - multi_join_deep_wiki:   join (partsupp_deep_10 ⨝ part_wiki_10)

전략:
  1. concat([emb1, emb2]) (norm-aware, measure_multi_4kang 와 동일) 단일 vector 화
  2. method 별 fit + assign (4 method 는 4kang 과 동일, 7 method 는 measure_multi_all
     의 stratify_method() 재사용 + Reservoir inline)
  3. measure_strategy / measure_strategy_join 호출 (Bernoulli 비교 X — 이미 4way baseline)
  4. (cell × method × 5 sel × 5 seed × 100 q) → 12500 row / cell / method

규모: 3 cell × 11 method × 5 sel × 5 seed × 100 q = 8250 measurement (~10h, HDD IO 1).
LSH 는 Wave 0 hyperparameter (mod 20, 5 hyperplanes) 그대로 — limitation 명시.

산출:
  _internal/cache/rq3/multi_paradigm/multi_paradigm_<cell>.csv  (cell 별 통합)

CLI:
  python3 _internal/scripts/measure_multi_paradigm.py \\
      --cells partsupp_deep_sift_10 partsupp_deep_wiki_10 multi_join_deep_wiki \\
      --methods HDBSCAN MiniBatch GMM Hilbert faiss_ivf MB_partial \\
                Reservoir sparse_rp PCA1D LSH Sobol
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup — 서버 경로 우선, 로컬 dry-run fallback
# ---------------------------------------------------------------------------

ROOT_SERVER = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
ROOT_LOCAL = Path("/Users/hyunbin/Capstone/experiments/code/rq3")
ROOT = ROOT_SERVER if ROOT_SERVER.exists() else ROOT_LOCAL
sys.path.insert(0, str(ROOT))

# 서버에서는 _internal/scripts 경로도 sys.path 추가 (measure_multi_vector / _join 위치)
SCRIPTS_PATH = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_PATH))


# ---------------------------------------------------------------------------
# 11 method canonical name mapping (user-facing → internal)
# ---------------------------------------------------------------------------
#
# stratify_method() / 4kang assign_method() 는 lowercase canonical name 사용.
# CLI 는 paper 표기 (HDBSCAN, MiniBatch, ...) 라 lower-snake 매핑 필요.
METHOD_MAP = {
    # ---- 기존 11 method (변경 X) -----------------------------------------
    # P1 Cluster
    "HDBSCAN":   "hdbscan",     # 4kang assign_method (hdbscan_partition.py)
    "MiniBatch": "minibatch",   # measure_multi_all stratify_method (offline_simple)
    "GMM":       "gmm",         # measure_multi_all stratify_method (gmm_partition)
    # P2 Spatial
    "Hilbert":   "hilbert",     # 4kang assign_method (hilbert_curve.py)
    "faiss_ivf": "faiss_ivf",   # measure_multi_all in-line _fit_faiss_ivf
    # P3 Streaming
    "MB_partial": "mb_partial",  # 4kang assign_method (minibatch_partial.py)
    "Reservoir":  "reservoir",   # inline _fit_reservoir (this file, 신규)
    # P4 DimReduction
    "sparse_rp": "sparse_rp",   # measure_multi_all stratify_method (sparserp)
    "PCA1D":     "pca1d",       # measure_multi_all stratify_method (pca1d)
    # P5 Quasi-random
    "LSH":       "lsh",         # measure_multi_all stratify_method (lsh.lsh, Wave 0 hyperparams)
    "Sobol":     "sobol",       # measure_multi_all stratify_method (sobol)
    # ---- 5/9 신규 10 method (methods/__init__.py STRATIFY_FUNCTIONS) -----
    # Tier S — multi-relation native sampling
    "WanderJoin":      "wander_join",        # Li SIGMOD 2016 / TODS 2019
    "AMSCountSketch":  "ams_count_sketch",   # Alon PODS 1999 / JCSS 2002
    # Tier A — productionized stratification primitives
    "PQ":          "pq",            # Jegou-Douze-Schmid PAMI 2011
    "Coreset":     "coreset",       # Bachem-Lucic-Krause ICML 2017
    "DenseRP":     "dense_rp",      # Bingham-Mannila ICDM 2001
    "BanditUCB1":  "bandit_ucb1",   # Carpentier-Munos NeurIPS 2011
    "NeurAM":      "neuram",        # Geraci 2026 (arXiv:2506.08921)
    # Tier B — multi-vector aware joint stratification
    "CCA1D":             "cca1d",                 # Hotelling Biometrika 1936
    "CoCluster_Nystrom": "coclustering_nystrom",  # Dhillon KDD 2003 + Nystrom
    # NeuroCard (latent-feature K-bin wrapper, drop-in compatible — option A)
    "NeuroCard":   "neurocard",     # Yang VLDB 2020 (lite reimpl)
    # ---- 5/9 v8 신규 5 method (research agent + brainstorm dispatch) -----
    # Tier S+ — cross-agent 합의, 즉시 구현
    "ThompsonSampling":       "thompson_sampling",       # Russo 2018 / Marcus Bao SIGMOD 2021
    "EpsilonNetBaseline":     "epsilon_net",             # Haussler-Welzl SoCG 1986 (theoretical floor)
    "AdaptiveBucketProbing":  "adaptive_bucket_probing", # Chen arXiv 2604.04603 (vector-native LSH+Chernoff)
    "CCSketch":               "cc_sketch",               # Heddes SIGMOD 2024 (multi-join FFT conv)
    "FactorJoin":             "factor_join",             # Wu SIGMOD 2023 (factor-graph BP)
    # ---- 5/9 v9 (23:30) extreme-mode 9 additional methods ----
    "LpBound":                "lp_bound",                # Zhang/Suciu SIGMOD 2025 Best Paper
    "MFMC":                   "mfmc",                    # Peherstorfer SIAM JSC 2016
    "Tucker":                 "tucker",                  # Tucker 1966 / Mu 2025 CoDe
    "VineCopula":             "vine_copula",             # Bedford-Cooke 2002
    # "HNSW_SS":              "hnsw_ss",                # DROPPED 5/10 00:10 — narrative violation (uses HNSW vector index)
    "HKBU_RepSample":         "hkbu_repsample",          # Wu SIGMOD 2026 (HKBU)
    "LHS":                    "lhs",                     # McKay Technometrics 1979
    "kDPP":                   "kdpp",                    # Kulesza-Taskar ICML 2011
    "OPQ":                    "opq",                     # Ge CVPR 2013 / PAMI 2014
    "LPM2":                   "lpm2",                    # Grafstrom-Lundstrom-Schelin 2012 (well-spread design)
}

# Paradigm 별 method 분류 (출력 / meta 용)
PARADIGM = {
    # 기존 5 paradigm (변경 X)
    "HDBSCAN": "P1_Cluster", "MiniBatch": "P1_Cluster", "GMM": "P1_Cluster",
    "Hilbert": "P2_Spatial", "faiss_ivf": "P2_Spatial",
    "MB_partial": "P3_Streaming", "Reservoir": "P3_Streaming",
    "sparse_rp": "P4_DimReduction", "PCA1D": "P4_DimReduction",
    "LSH": "P5_Quasi-random", "Sobol": "P5_Quasi-random",
    # 5/9 신규 paradigm
    "AMSCountSketch":    "P6_Sketch",
    "CCA1D":             "P7_Joint",
    "NeurAM":            "P8_DimInvariant",
    "DenseRP":           "P10_Theoretical",
    "PQ":                "P11_Hierarchical",
    "CoCluster_Nystrom": "P11_Hierarchical",
    "BanditUCB1":        "P12_Adaptive",
    "Coreset":           "P13_AdaptiveSel",
    "NeuroCard":         "P14_Latent",
    "WanderJoin":        "S_MultiRelation",
    # ---- 5/9 v8 신규 paradigm 라벨 ----
    "ThompsonSampling":      "P15_BayesianBandit",
    "EpsilonNetBaseline":    "P16_VCDimBaseline",
    "AdaptiveBucketProbing": "P17_LSHChernoff",
    "CCSketch":              "P18_SketchConv",
    "FactorJoin":            "P19_FactorGraph",
    # ---- 5/9 v9 paradigm 라벨 ----
    "LpBound":            "P20_PessimisticLP",
    "MFMC":               "P21_MultiFidelity",
    "Tucker":             "P22_TensorDecomp",
    "VineCopula":         "P23_CopulaTree",
    # "HNSW_SS":          "P24_GraphStratify",       # DROPPED 5/10 00:10
    "HKBU_RepSample":     "P25_RepSampling",
    "LHS":                "P26_LatinHypercube",
    "kDPP":               "P27_RepulsiveDiverse",
    "OPQ":                "P28_RotatedQuant",
    "LPM2":               "P29_PivotalDesign",
}

# 신규 10 method 의 stratify_method() 는 (emb1, emb2, K, seed) signature 사용 →
# methods/__init__.py 의 STRATIFY_FUNCTIONS dict 에서 dispatch.
# 기존 11 method 는 concat vectors + measure_multi_all helper 경로 유지.
NEW_METHOD_CANONS: set[str] = {
    "wander_join", "ams_count_sketch",
    "pq", "coreset", "dense_rp", "bandit_ucb1", "neuram",
    "cca1d", "coclustering_nystrom",
    "neurocard",
    # ---- 5/9 v8 신규 5 method ----
    "thompson_sampling", "epsilon_net", "adaptive_bucket_probing",
    "cc_sketch", "factor_join",
    # ---- 5/9 v9 extreme-mode 9 method ----
    "lp_bound", "mfmc", "tucker", "vine_copula",
    # "hnsw_ss" DROPPED 5/10 00:10 — narrative violation
    "hkbu_repsample", "lhs", "kdpp", "opq", "lpm2",
}


# ---------------------------------------------------------------------------
# Cell config (4kang + measure_multi_all 와 동일)
# ---------------------------------------------------------------------------

CELL_4WAY = {
    # DROPPED 5/10 01:18 — partsupp_deep_sift (image+image, Exqutor scope 외)
    # "partsupp_deep_sift_10": {...},
    "partsupp_deep_wiki_10": {
        "table": "partsupp_deep_wiki_10",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_wiki", "emb2_dim": 768,
        "kind": "4way",
    },
    # ---------- 5/9 added: existing sf=1 variants (NPY fast-path in cache/rq3) ----------
    # DROPPED 5/10 01:18 — partsupp_deep_sift (image+image, Exqutor scope 외)
    # "partsupp_deep_sift_1": {...},
    "partsupp_deep_wiki_1": {
        "table": "partsupp_deep_wiki_1",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_wiki", "emb2_dim": 768,
        "kind": "4way",
    },
    # ---------- 5/9 added: new prebuilt sf=1 (build_new_multi_cells.py 산출) ----------
    # cache/rq3/<cell>_emb1.npy / _emb2.npy / _query_pool.parquet /
    # _query_selectivity.parquet — fetch_dual_vectors / build_query_pool 우회.
    "partsupp_sift_wiki_1": {
        "prebuilt": True, "table": "partsupp_sift_wiki_1",
        "emb1_dim": 128, "emb2_dim": 768,
        "kind": "4way",
    },
    "partsupp_fb_wiki_1": {
        "prebuilt": True, "table": "partsupp_fb_wiki_1",
        "emb1_dim": 256, "emb2_dim": 768,
        "kind": "4way",
    },
    "partsupp_yfcc_wiki_1": {
        "prebuilt": True, "table": "partsupp_yfcc_wiki_1",
        "emb1_dim": 192, "emb2_dim": 768,
        "kind": "4way",
    },
    # ---------- 5/9 added: new prebuilt sf=10 (build pending — config preload) ----------
    "partsupp_sift_wiki_10": {
        "prebuilt": True, "table": "partsupp_sift_wiki_10",
        "emb1_dim": 128, "emb2_dim": 768,
        "kind": "4way",
    },
    "partsupp_fb_wiki_10": {
        "prebuilt": True, "table": "partsupp_fb_wiki_10",
        "emb1_dim": 256, "emb2_dim": 768,
        "kind": "4way",
    },
    "partsupp_yfcc_wiki_10": {
        "prebuilt": True, "table": "partsupp_yfcc_wiki_10",
        "emb1_dim": 192, "emb2_dim": 768,
        "kind": "4way",
    },
    # ---------- 5/9 v8 added: 22 NEW 4-way pairs (build pending) ---------
    # All prebuilt — relies on build_new_multi_cells.py producing emb1.npy / emb2.npy
    # / partkeys.npy / strata.npy / query_pool.parquet / query_selectivity.parquet /
    # true_card.parquet under /mnt/hdd0/home/capstone2026/cache/rq3/.
    # Convention: <A>_<B> with dims = (dim_A, dim_B). dim refs:
    #   deep=96, sift=128, fb=256, yfcc=192, yfcc_pca=192, wiki=768
    # DROPPED 5/10 01:18 — image+image partsupp 4-way (Exqutor scope 외)
    # Exqutor Fig 8: partsupp_X_WIKI 만 사용 (image+text). image+image 12 cells 폐기.
    # "partsupp_deep_fb_1": {...},
    # "partsupp_deep_fb_10": {...},
    # "partsupp_deep_yfcc_1": {...},
    # "partsupp_deep_yfcc_10": {...},
    # "partsupp_deep_yfcc_pca_*": (already dropped 5/10 01:14)
    # "partsupp_sift_fb_1": {...},
    # "partsupp_sift_fb_10": {...},
    # "partsupp_sift_yfcc_1": {...},
    # "partsupp_sift_yfcc_10": {...},
    # "partsupp_sift_yfcc_pca_*": (already dropped)
    # "partsupp_fb_yfcc_1": {...},
    # "partsupp_fb_yfcc_10": {...},
    # "partsupp_fb_yfcc_pca_*": (already dropped)
    # DROPPED 5/10 01:14 — fb × YFCC_PCA (Exqutor scope 외)
    # "partsupp_fb_yfcc_pca_1": {...},
    # "partsupp_fb_yfcc_pca_10": {...},
    # DROPPED 5/10 01:14 — yfcc × YFCC_PCA (Exqutor scope 외)
    # "partsupp_yfcc_yfcc_pca_1": {...},
    # "partsupp_yfcc_yfcc_pca_10": {...},
    # DROPPED 5/10 01:14 — YFCC_PCA × WIKI (Exqutor scope 외)
    # "partsupp_yfcc_pca_wiki_1": {...},
    # "partsupp_yfcc_pca_wiki_10": {...},
}

CELL_JOIN = {
    # ---------- Existing sf=10 (PG / cache/rq3 NPY fast-path) ----------
    "multi_join_deep_wiki": {
        "partsupp_table": "partsupp_deep_10",
        "part_table": "part_wiki_10",
        "partsupp_emb_col": "ps_embedding", "partsupp_emb_dim": 96,
        "part_emb_col": "p_embedding", "part_emb_dim": 768,
        "kind": "join",
    },
    # ---------- 5/9 added: existing sf=1 variant (NPY fast-path) ----------
    # cache/rq3/partsupp_deep_1_vectors.npy + part_wiki_1_vectors.npy 이미 존재 →
    # fetch_partsupp / fetch_part 의 NPY 분기로 자동 진입.
    "multi_join_deep_wiki_1": {
        "partsupp_table": "partsupp_deep_1",
        "part_table": "part_wiki_1",
        "partsupp_emb_col": "ps_embedding", "partsupp_emb_dim": 96,
        "part_emb_col": "p_embedding", "part_emb_dim": 768,
        "kind": "join",
    },
    # ---------- 5/9 added: new prebuilt sf=1 (build_new_multi_cells.py 산출) ----------
    # cache/rq3/<cell>_emb1_join.npy / _emb2_join.npy / _query_pool.parquet /
    # _query_selectivity.parquet — fetch_partsupp / fetch_part / build_join 우회.
    "multi_join_sift_wiki_1": {
        "prebuilt": True, "join_pair_name": "partsupp_sift_1_join_part_wiki_1",
        "partsupp_emb_dim": 128, "part_emb_dim": 768,
        "kind": "join",
    },
    "multi_join_fb_wiki_1": {
        "prebuilt": True, "join_pair_name": "partsupp_fb_1_join_part_wiki_1",
        "partsupp_emb_dim": 256, "part_emb_dim": 768,
        "kind": "join",
    },
    "multi_join_yfcc_wiki_1": {
        "prebuilt": True, "join_pair_name": "partsupp_yfcc_1_join_part_wiki_1",
        "partsupp_emb_dim": 192, "part_emb_dim": 768,
        "kind": "join",
    },
    # ---------- 5/9 added: new prebuilt sf=10 (build pending — config preload) ----------
    "multi_join_sift_wiki_10": {
        "prebuilt": True, "join_pair_name": "partsupp_sift_10_join_part_wiki_10",
        "partsupp_emb_dim": 128, "part_emb_dim": 768,
        "kind": "join",
    },
    "multi_join_fb_wiki_10": {
        "prebuilt": True, "join_pair_name": "partsupp_fb_10_join_part_wiki_10",
        "partsupp_emb_dim": 256, "part_emb_dim": 768,
        "kind": "join",
    },
    "multi_join_yfcc_wiki_10": {
        "prebuilt": True, "join_pair_name": "partsupp_yfcc_10_join_part_wiki_10",
        "partsupp_emb_dim": 192, "part_emb_dim": 768,
        "kind": "join",
    },
    # ---------- 5/9 v8 added: 4 NEW multi_join cells (build pending) ----------
    # DROPPED 5/10 01:14 — multi_join YFCC_PCA × WIKI (Exqutor scope 외)
    # "multi_join_yfcc_pca_wiki_1": {...},
    # "multi_join_yfcc_pca_wiki_10": {...},
    # DROPPED 5/10 01:18 — multi_join_wiki (wiki self-join, Exqutor scope 외)
    # Exqutor Fig 9: partsupp(IMAGE) ⋈ part(WIKI) 만 사용. wiki self-join 미수록.
    # "multi_join_wiki_1": {...},
    # "multi_join_wiki_10": {...},
}
ALL_CELLS = list(CELL_4WAY.keys()) + list(CELL_JOIN.keys())


# ---------------------------------------------------------------------------
# Prebuilt loader (5/9 added) — short-circuit fetch_dual_vectors /
# fetch_partsupp+fetch_part+build_join + build_query_pool by reading cached
# NPY + parquet artifacts produced by build_new_multi_cells.py.
# ---------------------------------------------------------------------------

def _load_prebuilt_artifacts(
    cell_name: str, cfg: dict, kind: str, n_queries: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
           dict[float, np.ndarray], dict[float, np.ndarray],
           dict[tuple[int, float], int]]:
    """Load prebuilt (emb1, emb2, qids, q1, q2, D1_by_sel, D2_by_sel, true_card).

    Used by both 4way and join cells when ``cfg["prebuilt"] is True``. Mirrors the
    return shape of ``measure_multi_vector.build_query_pool`` so callers do not
    branch beyond the load step.

    For 4-way:  reads {cell}_emb1.npy, {cell}_emb2.npy
    For join:   reads {cell}_emb1_join.npy, {cell}_emb2_join.npy
    Both load:  {cell}_query_pool.parquet, {cell}_query_selectivity.parquet
    """
    cache = ROOT  # /mnt/hdd0/home/capstone2026/cache/rq3 on server
    if kind == "4way":
        emb1 = np.load(cache / f"{cell_name}_emb1.npy")
        emb2 = np.load(cache / f"{cell_name}_emb2.npy")
    else:
        emb1 = np.load(cache / f"{cell_name}_emb1_join.npy")
        emb2 = np.load(cache / f"{cell_name}_emb2_join.npy")
    N = emb1.shape[0]

    # Replay deterministic qids — build_new_multi_cells.py uses
    # rng = np.random.default_rng(QUERY_SEED=1234); rng.choice(N, n_queries).
    rng = np.random.default_rng(1234)
    qids_full = rng.choice(N, size=100, replace=False)
    if n_queries < 100:
        qids = qids_full[:n_queries].copy()
    else:
        qids = qids_full
    q1 = emb1[qids].copy()
    q2 = emb2[qids].copy()

    # Load query_selectivity parquet — schema:
    #   query_id, ps_partkey, selectivity, D1_target, D2_target,
    #   true_cardinality, true_selectivity
    qs = pd.read_parquet(cache / f"{cell_name}_query_selectivity.parquet")
    sels = sorted(qs["selectivity"].unique().tolist())
    D1_by_sel: dict[float, np.ndarray] = {}
    D2_by_sel: dict[float, np.ndarray] = {}
    for sel in sels:
        sub = qs[qs["selectivity"] == sel].sort_values("query_id")
        d1 = sub["D1_target"].to_numpy(dtype=np.float32)
        d2 = sub["D2_target"].to_numpy(dtype=np.float32)
        D1_by_sel[float(sel)] = d1[:n_queries]
        D2_by_sel[float(sel)] = d2[:n_queries]

    true_card: dict[tuple[int, float], int] = {}
    for _, row in qs.iterrows():
        qid_idx = int(row["query_id"])
        if qid_idx >= n_queries:
            continue
        true_card[(int(qids[qid_idx]), float(row["selectivity"]))] = int(
            row["true_cardinality"],
        )

    return emb1, emb2, qids, q1, q2, D1_by_sel, D2_by_sel, true_card


# ---------------------------------------------------------------------------
# Lazy imports — server 에서만 PG 의존 module load
# ---------------------------------------------------------------------------

def _lazy_imports():
    """서버에서 PG / measure helper / method module load.

    로컬 dry-run (CLI 검증) 에서는 import 하지 않고 stub 반환.
    Returns: tuple (mvv: measure_multi_vector module, mvj: measure_multi_table_join module,
                    constants dict)
    """
    from measure_multi_vector import (  # noqa: E402
        CACHE, N_STRATA, SEEDS, SELECTIVITIES, SAMPLE_SIZE, CACHE_PER_CLUSTER,
        N_QUERIES, fetch_dual_vectors, build_query_pool, measure_strategy, kst,
    )
    from measure_multi_table_join import (  # noqa: E402
        fetch_partsupp, fetch_part, build_join,
        build_query_pool as build_query_pool_join,
        measure_strategy as measure_strategy_join,
    )
    consts = {
        "CACHE": CACHE, "N_STRATA": N_STRATA, "SEEDS": SEEDS,
        "SELECTIVITIES": SELECTIVITIES, "SAMPLE_SIZE": SAMPLE_SIZE,
        "CACHE_PER_CLUSTER": CACHE_PER_CLUSTER, "N_QUERIES": N_QUERIES,
        "kst": kst,
    }
    helpers = {
        "fetch_dual_vectors": fetch_dual_vectors,
        "build_query_pool": build_query_pool,
        "measure_strategy": measure_strategy,
        "fetch_partsupp": fetch_partsupp, "fetch_part": fetch_part,
        "build_join": build_join,
        "build_query_pool_join": build_query_pool_join,
        "measure_strategy_join": measure_strategy_join,
    }
    return consts, helpers


# Local dry-run constant fallback (CLI 검증용 — DB query 실행 X)
_FALLBACK_CONSTS = {
    "N_STRATA": 20, "SEEDS": [0.1, 0.2, 0.3, 0.4, 0.5],
    "SELECTIVITIES": [0.01, 0.05, 0.10, 0.30, 0.50],
    "SAMPLE_SIZE": 385, "CACHE_PER_CLUSTER": 500, "N_QUERIES": 100,
    "kst": lambda: datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S"),
}


# ---------------------------------------------------------------------------
# concat helper (4kang 과 동일 norm-aware)
# ---------------------------------------------------------------------------

def build_concat(emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    return np.concatenate([emb1 / n1, emb2 / n2], axis=1).astype(np.float32)


def _learn_subsample(vectors: np.ndarray, frac: float, seed: int,
                     n_strata: int = 20) -> np.ndarray:
    n = vectors.shape[0]
    n_learn = max(int(n * frac), n_strata * 50)
    n_learn = min(n_learn, n)
    rng = np.random.default_rng(seed)
    if n_learn < n:
        idx = rng.choice(n, size=n_learn, replace=False)
        return vectors[idx]
    return vectors


def _assign_nearest_centroid(
    vectors: np.ndarray, centroids: np.ndarray, chunk: int = 50_000,
) -> np.ndarray:
    """centroid 에 nearest argmin (measure_multi_all 의 helper 동일)."""
    n = len(vectors)
    out = np.empty(n, dtype=np.int32)
    cs = (centroids ** 2).sum(axis=1)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = vectors[i:j]
        ds = (block ** 2).sum(axis=1, keepdims=True) + cs[None, :] - 2.0 * block @ centroids.T
        out[i:j] = np.argmin(ds, axis=1).astype(np.int32)
    return out


# ---------------------------------------------------------------------------
# Reservoir sampling stratification (inline — 신규, measure_multi_all 미포함)
# ---------------------------------------------------------------------------

def _fit_reservoir(learn: np.ndarray, vectors: np.ndarray,
                   n_strata: int, seed: int) -> np.ndarray:
    """Reservoir sampling K=n_strata 개 표본 추출 → nearest-centroid 부여.

    streaming context 에서 reservoir sampling (Vitter 1985, Algorithm R) 으로
    K 개 점을 uniform 추출 → 각 row 를 가장 가까운 reservoir 점에 부여.

    학습 의존도: K 개 random sample 만 사용 (KM 등의 iteration X), 진정한 streaming /
    online (P3) paradigm 에 부합. 1-pass 통과로 K 점 확정 가능.

    rq3_reservoir.parquet (single cell 측정본) 와 동일 메커니즘 — DEEP/SIFT 에서
    sel=0.01 mean q_error ~1.6, sel>=0.10 ~1.1 수준 (kmeans 보다 약, BERN 보다 강).
    """
    rng = np.random.default_rng(seed)
    n = learn.shape[0]
    if n <= n_strata:
        # learn 자체가 K 미만 → 그대로 centroid
        centroids = learn.astype(np.float32)
    else:
        # uniform K-subset (Vitter Algorithm R 와 통계적 동일)
        idx = rng.choice(n, size=n_strata, replace=False)
        centroids = learn[idx].astype(np.float32)
    # 부족한 cluster 가 발생할 수 있지만 estimator 단계에서 weight=N_i/s_i 로 보정
    return _assign_nearest_centroid(vectors, centroids)


# ---------------------------------------------------------------------------
# stratify_method — 11 method dispatch
# ---------------------------------------------------------------------------

def stratify_method(method_canon: str, vectors: np.ndarray, kst,
                     learn_frac: float = 0.01, seed: int = 42,
                     n_strata: int = 20,
                     emb1: np.ndarray | None = None,
                     emb2: np.ndarray | None = None) -> np.ndarray:
    """11 method 중 하나로 stratification (lower-snake canonical name).

    신규 10 method (NEW_METHOD_CANONS) 는 (emb1, emb2) 를 직접 받아
    methods.STRATIFY_FUNCTIONS dispatch — concat vectors 와 별도 경로.
    emb1/emb2 None 이면 vectors 를 emb1 으로, emb2=None 으로 fallback
    (PCA-1D fallback in cca1d / coclustering_nystrom).
    """
    # ============ 신규 10 method (Tier S/A/B + NeuroCard) ============
    if method_canon in NEW_METHOD_CANONS:
        from methods import STRATIFY_FUNCTIONS  # noqa: WPS433 (lazy)
        try:
            from methods.neurocard_lite import (  # noqa: WPS433
                stratify_method as neurocard_strat,
            )
        except Exception:  # pragma: no cover — torch optional
            neurocard_strat = None

        # emb1 fallback: concat vectors 를 emb1 으로 사용 (single-vector mode)
        e1 = emb1 if emb1 is not None else vectors
        e2 = emb2  # may be None — Tier B mappers 자체 fallback

        if method_canon == "neurocard":
            if neurocard_strat is None:
                raise ImportError(
                    "NeuroCard 사용에는 torch 필요 (methods/neurocard_lite.py)."
                )
            stratify_fn = neurocard_strat
        else:
            stratify_fn = STRATIFY_FUNCTIONS[method_canon]

        # neurocard_lite 의 stratify_method 는 emb2 가 None 일 때 동작 X — emb1 으로 채움
        if e2 is None and method_canon == "neurocard":
            e2 = e1
        # WanderJoin / AMS count-sketch / pq / coreset / dense_rp / bandit_ucb1 /
        # neuram 도 emb2 None 시 emb1 자체로 채워서 single-vector path 호환
        if e2 is None and method_canon not in ("cca1d", "coclustering_nystrom"):
            e2 = e1

        print(f"[{kst()}]   strat (new): {method_canon} on "
              f"emb1.shape={e1.shape}"
              f"{', emb2.shape=' + str(e2.shape) if e2 is not None else ''}")
        t0 = time.time()
        sids = stratify_fn(e1, e2, K=n_strata, seed=seed).astype(np.int32)
        elapsed = time.time() - t0
        counts = np.bincount(sids, minlength=n_strata)
        nz = counts[counts > 0]
        print(f"[{kst()}]   strat done {elapsed:.1f}s — sizes "
              f"min={int(nz.min()) if len(nz) else 0} "
              f"max={int(counts.max())} K_used={(counts > 0).sum()}/{n_strata}")
        return sids

    # ============ 기존 11 method (변경 X) ============
    learn = _learn_subsample(vectors, learn_frac, seed, n_strata=n_strata)
    print(f"[{kst()}]   strat: {method_canon} on {learn.shape[0]:,}/{vectors.shape[0]:,} "
          f"learn samples (dim={vectors.shape[1]})")
    t0 = time.time()

    # ============ P1 Cluster ============
    if method_canon == "hdbscan":
        from hdbscan.hdbscan_partition import fit_hdbscan, assign_hdbscan
        mapper = fit_hdbscan(learn, n_strata=n_strata, seed=seed)
        sids = assign_hdbscan(mapper, vectors)

    elif method_canon == "minibatch":
        from offline_simple.minibatch_kmeans import (
            train_minibatch_kmeans, assign_minibatch,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            model = train_minibatch_kmeans(
                learn, n_clusters=n_strata, batch_size=1000, random_state=seed,
            )
        sids = assign_minibatch(model, vectors)

    elif method_canon == "gmm":
        from gmm.gmm_partition import fit_gmm, assign_gmm
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mapper = fit_gmm(learn, n_strata=n_strata, seed=seed)
        sids = assign_gmm(mapper, vectors)

    # ============ P2 Spatial ============
    elif method_canon == "hilbert":
        from hilbert.hilbert_curve import fit_hilbert_mapper, assign_hilbert
        mapper = fit_hilbert_mapper(learn, n_strata=n_strata, p=10, seed=seed)
        sids = assign_hilbert(mapper, vectors)

    elif method_canon == "faiss_ivf":
        # measure_multi_all 의 _fit_faiss_ivf 와 동일 — 단 sklearn fallback 포함
        try:
            import faiss
            d = vectors.shape[1]
            quantizer = faiss.IndexFlatL2(d)
            index = faiss.IndexIVFFlat(quantizer, d, n_strata)
            index.train(np.ascontiguousarray(learn.astype(np.float32)))
            quant_index = index.quantizer
            _, I = quant_index.search(
                np.ascontiguousarray(vectors.astype(np.float32)), 1,
            )
            sids = I[:, 0].astype(np.int32)
        except ImportError:
            from sklearn.cluster import MiniBatchKMeans
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                m = MiniBatchKMeans(
                    n_clusters=n_strata, batch_size=1000, random_state=seed,
                ).fit(learn)
            sids = m.predict(vectors).astype(np.int32)

    # ============ P3 Streaming ============
    elif method_canon == "mb_partial":
        from offline_simple.minibatch_partial import (
            train_minibatch_partial, assign_minibatch,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            result = train_minibatch_partial(
                learn, n_clusters=n_strata, chunk_size=1000, random_state=seed,
            )
        sids = assign_minibatch(result, vectors)

    elif method_canon == "reservoir":
        # inline (rq3 server 의 reservoir 구현이 로컬에 없어 동일 메커니즘 재현)
        sids = _fit_reservoir(learn, vectors, n_strata, seed)

    # ============ P4 DimReduction ============
    elif method_canon == "sparse_rp":
        from sparserp.sparse_random_projection import fit_sparse_rp, assign_sparse_rp
        matrix = fit_sparse_rp(vectors.shape[1], n_strata=n_strata, seed=seed)
        sids = assign_sparse_rp(matrix, vectors, k=n_strata)

    elif method_canon == "pca1d":
        from pca1d.pca1d_quantile import fit_pca1d_mapper, assign_pca1d
        mapper = fit_pca1d_mapper(learn, n_strata=n_strata, seed=seed)
        sids = assign_pca1d(mapper, vectors)

    # ============ P5 Quasi-random ============
    elif method_canon == "lsh":
        # Wave 0 hyperparam: 5 hyperplane (ceil(log2(20))) + mod 20 — 변경 X
        from lsh.lsh import make_hyperplanes, assign_lsh
        W = make_hyperplanes(dim=vectors.shape[1], k=n_strata, seed=seed)
        sids = assign_lsh(W, vectors, k=n_strata)

    elif method_canon == "sobol":
        from sobol.sobol_stratification import fit_sobol, assign_sobol
        mapper = fit_sobol(learn, n_strata=n_strata, seed=seed)
        sids = assign_sobol(mapper, vectors)

    else:
        raise ValueError(f"unsupported method: {method_canon}")

    sids = sids.astype(np.int32)
    elapsed = time.time() - t0
    counts = np.bincount(sids, minlength=n_strata)
    nz = counts[counts > 0]
    print(f"[{kst()}]   strat done {elapsed:.1f}s — sizes "
          f"min={int(nz.min()) if len(nz) else 0} "
          f"max={int(counts.max())} K_used={(counts > 0).sum()}/{n_strata}")
    return sids


# ---------------------------------------------------------------------------
# 4-way cell measurement
# ---------------------------------------------------------------------------

def measure_4way(cell_name: str, methods_user: list[str], consts: dict, helpers: dict,
                 n_queries: int, learn_frac: float, learn_seed: int) -> list[dict]:
    cfg = CELL_4WAY[cell_name]
    table = cfg.get("table", cell_name)
    kst = consts["kst"]
    print(f"[{kst()}] === paradigm 4way: cell={cell_name} "
          f"({'prebuilt' if cfg.get('prebuilt') else 'PG/NPY'}) ===")

    if cfg.get("prebuilt"):
        emb1, emb2, qids, q1, q2, D1_by_sel, D2_by_sel, true_card = (
            _load_prebuilt_artifacts(cell_name, cfg, "4way", n_queries)
        )
        N = emb1.shape[0]
        print(f"[{kst()}] N={N:,} dims=({emb1.shape[1]}, {emb2.shape[1]}) "
              f"[prebuilt artifacts]")
    else:
        emb1, emb2 = helpers["fetch_dual_vectors"](
            table, cfg["emb1_col"], cfg["emb2_col"],
            cfg["emb1_dim"], cfg["emb2_dim"],
        )
        N = emb1.shape[0]
        print(f"[{kst()}] N={N:,} dims=({emb1.shape[1]}, {emb2.shape[1]})")

        qids, q1, q2, D1_by_sel, D2_by_sel, true_card = helpers["build_query_pool"](
            emb1, emb2, n_queries=n_queries,
        )

    concat = build_concat(emb1, emb2)
    print(f"[{kst()}]   concat shape={concat.shape} "
          f"({concat.nbytes / 1e6:.1f} MB)")

    all_rows: list[dict] = []
    for m_user in methods_user:
        m_canon = METHOD_MAP[m_user]
        print(f"\n[{kst()}] === method={m_user} ({m_canon}, {PARADIGM[m_user]}) ===")
        sids = stratify_method(
            m_canon, concat, kst,
            learn_frac=learn_frac, seed=learn_seed,
            n_strata=consts["N_STRATA"],
            emb1=emb1, emb2=emb2,
        )
        rows = helpers["measure_strategy"](
            m_canon, sids, emb1, emb2, qids, q1, q2,
            D1_by_sel, D2_by_sel, true_card, table, also_bernoulli=False,
        )
        # method_user / paradigm 부착 (csv 분석용)
        for r in rows:
            r["method_user"] = m_user
            r["paradigm"] = PARADIGM[m_user]
        all_rows.extend(rows)
    return all_rows


# ---------------------------------------------------------------------------
# join cell measurement (multi_join_deep_wiki)
# ---------------------------------------------------------------------------

def measure_join(cell_name: str, methods_user: list[str], consts: dict, helpers: dict,
                 n_queries: int, learn_frac: float, learn_seed: int) -> list[dict]:
    cfg = CELL_JOIN[cell_name]
    kst = consts["kst"]

    if cfg.get("prebuilt"):
        print(f"[{kst()}] === paradigm join: cell={cell_name} (prebuilt) ===")
        deep_join, wiki_join, qids, q1, q2, D1_by_sel, D2_by_sel, true_card = (
            _load_prebuilt_artifacts(cell_name, cfg, "join", n_queries)
        )
        print(f"[{kst()}] join: emb1 {deep_join.shape}, emb2 {wiki_join.shape} "
              f"[prebuilt artifacts]")
        table_name = cfg.get("join_pair_name", cell_name)
    else:
        print(f"[{kst()}] === paradigm join: cell={cell_name} "
              f"({cfg['partsupp_table']} ⨝ {cfg['part_table']}) ===")
        ps_emb, ps_keys = helpers["fetch_partsupp"](
            cfg["partsupp_table"], cfg["partsupp_emb_col"], cfg["partsupp_emb_dim"],
        )
        p_emb, p_keys = helpers["fetch_part"](
            cfg["part_table"], cfg["part_emb_col"], cfg["part_emb_dim"],
        )
        deep_join, wiki_join = helpers["build_join"](ps_emb, ps_keys, p_emb, p_keys)
        print(f"[{kst()}] join: deep {deep_join.shape}, wiki {wiki_join.shape}")

        qids, q1, q2, D1_by_sel, D2_by_sel, true_card = helpers["build_query_pool_join"](
            deep_join, wiki_join, n_queries=n_queries,
        )
        table_name = f"{cfg['partsupp_table']}_join_{cfg['part_table']}"

    concat = build_concat(deep_join, wiki_join)
    print(f"[{kst()}]   concat shape={concat.shape} "
          f"({concat.nbytes / 1e6:.1f} MB)")
    all_rows: list[dict] = []
    for m_user in methods_user:
        m_canon = METHOD_MAP[m_user]
        print(f"\n[{kst()}] === method={m_user} ({m_canon}, {PARADIGM[m_user]}) ===")
        sids = stratify_method(
            m_canon, concat, kst,
            learn_frac=learn_frac, seed=learn_seed,
            n_strata=consts["N_STRATA"],
            emb1=deep_join, emb2=wiki_join,
        )
        rows = helpers["measure_strategy_join"](
            m_canon, sids, deep_join, wiki_join, qids, q1, q2,
            D1_by_sel, D2_by_sel, true_card, table_name, also_bernoulli=False,
        )
        for r in rows:
            r["method_user"] = m_user
            r["paradigm"] = PARADIGM[m_user]
        all_rows.extend(rows)
    return all_rows


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", nargs="+", required=True, choices=ALL_CELLS,
                    help="측정할 multi cell (3종)")
    ap.add_argument("--methods", nargs="+", required=True,
                    choices=list(METHOD_MAP.keys()),
                    help="11 paradigm method (HDBSCAN MiniBatch ...)")
    ap.add_argument("--out-dir", default=None,
                    help="CSV 출력 dir (default: server CACHE / 로컬 _internal/cache/rq3/multi_paradigm)")
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true",
                    help="DB 접속 / measure 실행 X — CLI / import 검증만")
    args = ap.parse_args()

    if args.dry_run:
        print("=== dry-run: validating arguments + method imports ===")
        print(f"cells:   {args.cells}")
        print(f"methods: {args.methods}")
        print(f"  paradigm map:")
        for m in args.methods:
            print(f"    {m:>12} → {METHOD_MAP[m]:<12} ({PARADIGM[m]})")
        print(f"learn_frac={args.learn_frac}  learn_seed={args.learn_seed}  "
              f"n_queries={args.n_queries}")
        # constant fallback (server import 안 함)
        consts = _FALLBACK_CONSTS
        # estimate
        n_meas_per_cell_method = (
            len(consts["SELECTIVITIES"]) * len(consts["SEEDS"]) * args.n_queries
        )
        total = len(args.cells) * len(args.methods) * n_meas_per_cell_method
        print(f"\n[estimate] {len(args.cells)} cell × {len(args.methods)} method "
              f"× {len(consts['SELECTIVITIES'])} sel × {len(consts['SEEDS'])} seed "
              f"× {args.n_queries} q = {total:,} measurement (~10h estimated)")
        print("\n=== dry-run OK ===")
        return

    # 서버 실행 — PG / measure helper import
    consts, helpers = _lazy_imports()
    kst = consts["kst"]

    # output dir
    if args.out_dir:
        out_dir = Path(args.out_dir)
    else:
        # 서버 CACHE 가 존재하면 거기, 아니면 _internal/cache 로컬 fallback
        if consts.get("CACHE") and Path(consts["CACHE"]).exists():
            out_dir = Path(consts["CACHE"]) / "multi_paradigm"
        else:
            out_dir = SCRIPTS_PATH.parent / "cache" / "rq3" / "multi_paradigm"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{kst()}] out_dir: {out_dir}")

    print(f"[{kst()}] === measure_multi_paradigm ===")
    print(f"[{kst()}] cells:   {args.cells}")
    print(f"[{kst()}] methods: {args.methods}")
    print(f"[{kst()}] learn_frac={args.learn_frac}  seed={args.learn_seed}  "
          f"n_queries={args.n_queries}")

    t_total = time.time()
    for cell in args.cells:
        print(f"\n[{kst()}] ###### CELL {cell} ######")
        out_csv = out_dir / f"multi_paradigm_{cell}.csv"
        out_meta = out_dir / f"multi_paradigm_{cell}_meta.json"
        if out_csv.exists():
            print(f"[{kst()}] SKIP — {out_csv.name} already exists")
            continue

        t_cell = time.time()
        if cell in CELL_4WAY:
            rows = measure_4way(
                cell, args.methods, consts, helpers,
                args.n_queries, args.learn_frac, args.learn_seed,
            )
            kind = "4way"
        else:
            rows = measure_join(
                cell, args.methods, consts, helpers,
                args.n_queries, args.learn_frac, args.learn_seed,
            )
            kind = "join"

        df = pd.DataFrame(rows)
        df.to_csv(out_csv, index=False)
        print(f"[{kst()}] saved {out_csv} ({len(df):,} rows)")

        # 요약 (method × selectivity)
        smry = (df.groupby(["method_user", "selectivity"])["q_error"]
                  .agg(["mean", "std", "median", "count"]).round(4))
        print(f"\n=== q_error summary (method × sel) ===\n{smry}\n")

        meta = {
            "kst": kst(),
            "cell": cell, "kind": kind,
            "methods": args.methods,
            "method_map": {m: METHOD_MAP[m] for m in args.methods},
            "paradigm_map": {m: PARADIGM[m] for m in args.methods},
            "n_rows": len(df),
            "n_queries": args.n_queries,
            "learn_frac": args.learn_frac,
            "learn_seed": args.learn_seed,
            "selectivities": consts["SELECTIVITIES"],
            "seeds": consts["SEEDS"],
            "sample_size": consts["SAMPLE_SIZE"],
            "n_strata": consts["N_STRATA"],
            "cache_per_cluster": consts["CACHE_PER_CLUSTER"],
            "stratify_basis": "concat([emb1, emb2]) norm-aware + method fit/assign",
            "elapsed_s": round(time.time() - t_cell, 1),
        }
        with open(out_meta, "w") as f:
            json.dump(meta, f, indent=2, default=str)
        print(f"[{kst()}] saved {out_meta}")
        print(f"[{kst()}] cell {cell} done in {meta['elapsed_s']}s")

    print(f"\n[{kst()}] === all done in {time.time() - t_total:.1f}s ===")


if __name__ == "__main__":
    main()
