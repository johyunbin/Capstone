#!/usr/bin/env python3
"""
Multi-vector 4강 method wrapper — RQ3 보강.

기존 measure_multi_vector.py 의 4 KM20 mode (emb1_only / emb2_only / concat / product)
에 추가하여, RQ3 4강 method (Hilbert / Hybrid / MB_partial / HDBSCAN) 를
multi-vector cell 에 적용하기 위한 어댑터.

전략:
  - measure_multi_vector.py 의 measure_strategy / build_query_pool / fetch_dual_vectors
    등을 그대로 import 해서 재사용
  - stratification 단계만 4강 method 의 assign 함수로 대체
  - 기본 입력 vector 는 concat ([emb1 || emb2]) — single-vector 가정으로 동작

Methods:
  1. hilbert      : run_hilbert.py 와 동일 (PCA + Hilbert curve)
  2. hybrid       : run_hybrid.py 와 동일 (MiniBatch outer × Hilbert inner)
  3. mb_partial   : run_minibatch_partial.py 와 동일 (chunk 기반 partial_fit)
  4. hdbscan      : run_hdbscan.py 와 동일 (HDBSCAN partition)

Usage:
    # vector cell (deep_sift, deep_wiki)
    python3 measure_multi_4kang.py vector \
        --table partsupp_deep_sift_10 \
        --emb1-col ps_embedding_deep --emb1-dim 96 \
        --emb2-col ps_embedding_sift --emb2-dim 128 \
        --out-prefix multi_4kang_partsupp_deep_sift_10

    # join cell (multi_join_deep_wiki)
    python3 measure_multi_4kang.py join \
        --partsupp-table partsupp_deep_10 \
        --part-table part_wiki_10 \
        --partsupp-emb-col ps_embedding --partsupp-emb-dim 96 \
        --part-emb-col p_embedding --part-emb-dim 768 \
        --out-prefix multi_4kang_join_deep_wiki

산출:
    {CACHE}/{out_prefix}.parquet  (4 methods × 5 sel × 5 seed × 100 q = 10K rows)
    {CACHE}/{out_prefix}_meta.json
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

# rq3 root path 가 sys.path 에 있어야 method 모듈 import 가능
ROOT = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
sys.path.insert(0, str(ROOT))

# measure_multi_vector / measure_multi_table_join 의 함수 재사용
from measure_multi_vector import (  # noqa: E402
    CACHE, N_STRATA, SEEDS, SELECTIVITIES, SAMPLE_SIZE, CACHE_PER_CLUSTER, N_QUERIES,
    fetch_dual_vectors, build_query_pool, measure_strategy, kst,
)
from measure_multi_table_join import (  # noqa: E402
    fetch_partsupp, fetch_part, build_join,
    build_query_pool as build_query_pool_join,
    measure_strategy as measure_strategy_join,
)

# 4강 method 모듈
from hilbert.hilbert_curve import fit_hilbert_mapper, assign_hilbert  # noqa: E402
from hybrid.minibatch_hilbert import fit_hybrid_mapper, assign_hybrid  # noqa: E402
from offline_simple.minibatch_partial import (  # noqa: E402
    train_minibatch_partial, assign_minibatch,
)
from hdbscan.hdbscan_partition import fit_hdbscan, assign_hdbscan  # noqa: E402


# ---------------------------------------------------------------------------
# concat helper — measure_multi_vector 의 stratify_concat 와 동일 normalization
# ---------------------------------------------------------------------------

def build_concat(emb1: np.ndarray, emb2: np.ndarray) -> np.ndarray:
    """[emb1 || emb2] norm-aware concat (각 column 평균 norm 으로 정규화)."""
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    e1 = emb1 / n1
    e2 = emb2 / n2
    concat = np.concatenate([e1, e2], axis=1).astype(np.float32)
    return concat


# ---------------------------------------------------------------------------
# 4강 method assign — concat 한 vector 에 대해 single-vector 와 동일 동작
# ---------------------------------------------------------------------------

def assign_method(
    method: str, vectors: np.ndarray,
    learn_frac: float = 0.01, learn_seed: int = 42,
) -> np.ndarray:
    """4강 method 중 하나로 stratification.

    Returns: sids (N,) int32 — 0..N_STRATA-1 (HDBSCAN 은 noise 처리됨)
    """
    n = vectors.shape[0]
    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    rng = np.random.default_rng(learn_seed)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    learn_samples = vectors[learn_idx]

    print(f"[{kst()}]   {method}: learn on {n_learn:,} samples (frac={learn_frac})")
    t0 = time.time()

    if method == "hilbert":
        mapper = fit_hilbert_mapper(
            learn_samples, n_strata=N_STRATA, p=10, seed=learn_seed,
        )
        sids = assign_hilbert(mapper, vectors)
    elif method == "hybrid":
        mapper = fit_hybrid_mapper(
            learn_samples, k_outer=5, k_inner=4, p=10, seed=learn_seed,
        )
        sids = assign_hybrid(mapper, vectors)
    elif method == "mb_partial":
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            result = train_minibatch_partial(
                learn_samples, n_clusters=N_STRATA,
                chunk_size=1000, random_state=learn_seed,
            )
        sids = assign_minibatch(result, vectors)
    elif method == "hdbscan":
        mapper = fit_hdbscan(
            learn_samples, n_strata=N_STRATA, seed=learn_seed,
        )
        sids = assign_hdbscan(mapper, vectors)
    else:
        raise ValueError(f"unknown method: {method}")

    sids = sids.astype(np.int32)
    elapsed = time.time() - t0
    # 분포 sanity
    counts = np.bincount(sids, minlength=N_STRATA)
    nz = counts[counts > 0]
    print(f"[{kst()}]   {method}: assign done in {elapsed:.1f}s — "
          f"sizes min={int(nz.min()) if len(nz) else 0} "
          f"max={int(counts.max())} K_used={(counts > 0).sum()}")
    return sids


# ---------------------------------------------------------------------------
# main: vector mode (deep_sift_10 / deep_wiki_10)
# ---------------------------------------------------------------------------

def run_vector(args):
    print(f"[{kst()}] === measure_multi_4kang VECTOR ({args.table}) ===")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) fetch dual vectors (NPY cache fast-path 사용)
    emb1, emb2 = fetch_dual_vectors(
        args.table, args.emb1_col, args.emb2_col,
        args.emb1_dim, args.emb2_dim,
    )
    N = emb1.shape[0]
    print(f"[{kst()}] N={N:,} (emb1 dim={emb1.shape[1]}, emb2 dim={emb2.shape[1]})")

    # 2) query pool + true card
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool(
        emb1, emb2, n_queries=args.n_queries,
    )

    # 3) concat for 4강 method 입력
    print(f"[{kst()}] === build concat input ===")
    concat = build_concat(emb1, emb2)
    print(f"[{kst()}]   concat shape={concat.shape} ({concat.nbytes/1e6:.1f} MB)")

    # 4) measure 4 methods
    all_rows: list[dict] = []
    methods = ["hilbert", "hybrid", "mb_partial", "hdbscan"]
    for method in methods:
        print(f"\n[{kst()}] === method={method} ===")
        sids = assign_method(method, concat, args.learn_frac, args.learn_seed)
        all_rows.extend(measure_strategy(
            method, sids, emb1, emb2, qids, q1, q2,
            D1_by_sel, D2_by_sel, true_card, args.table, also_bernoulli=False,
        ))

    # 5) save
    df = pd.DataFrame(all_rows)
    out_pq = out_dir / f"{args.out_prefix}.parquet"
    out_meta = out_dir / f"{args.out_prefix}_meta.json"
    df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = (df.groupby(["dataset", "mode", "selectivity"])["q_error"]
              .agg(["mean", "std", "median", "count"]).round(4))
    print(f"\n=== mean q_error (table × mode × sel) ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "kind": "vector",
        "table": args.table,
        "emb1_col": args.emb1_col, "emb1_dim": args.emb1_dim,
        "emb2_col": args.emb2_col, "emb2_dim": args.emb2_dim,
        "methods": methods,
        "input_strategy": "concat (norm-aware)",
        "learn_frac": args.learn_frac,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_queries": args.n_queries,
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")


# ---------------------------------------------------------------------------
# main: join mode (multi_join_deep_wiki)
# ---------------------------------------------------------------------------

def run_join(args):
    print(f"[{kst()}] === measure_multi_4kang JOIN "
          f"({args.partsupp_table} ⨝ {args.part_table}) ===")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) fetch partsupp + part, build join (broadcast)
    ps_emb, ps_keys = fetch_partsupp(
        args.partsupp_table, args.partsupp_emb_col, args.partsupp_emb_dim,
    )
    p_emb, p_keys = fetch_part(
        args.part_table, args.part_emb_col, args.part_emb_dim,
    )
    deep_join, wiki_join = build_join(ps_emb, ps_keys, p_emb, p_keys)
    print(f"[{kst()}] join: deep {deep_join.shape}, wiki {wiki_join.shape}")

    # 2) query pool + true card (join script 의 build_query_pool 재사용)
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool_join(
        deep_join, wiki_join, n_queries=args.n_queries,
    )

    # 3) concat
    print(f"[{kst()}] === build concat input ===")
    concat = build_concat(deep_join, wiki_join)
    print(f"[{kst()}]   concat shape={concat.shape} ({concat.nbytes/1e6:.1f} MB)")

    # 4) measure 4 methods
    all_rows: list[dict] = []
    methods = ["hilbert", "hybrid", "mb_partial", "hdbscan"]
    table_name = f"{args.partsupp_table}_join_{args.part_table}"
    for method in methods:
        print(f"\n[{kst()}] === method={method} ===")
        sids = assign_method(method, concat, args.learn_frac, args.learn_seed)
        all_rows.extend(measure_strategy_join(
            method, sids, deep_join, wiki_join, qids, q1, q2,
            D1_by_sel, D2_by_sel, true_card, table_name, also_bernoulli=False,
        ))

    # 5) save
    df = pd.DataFrame(all_rows)
    out_pq = out_dir / f"{args.out_prefix}.parquet"
    out_meta = out_dir / f"{args.out_prefix}_meta.json"
    df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = (df.groupby(["dataset", "mode", "selectivity"])["q_error"]
              .agg(["mean", "std", "median", "count"]).round(4))
    print(f"\n=== mean q_error (table × mode × sel) ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "kind": "join",
        "partsupp_table": args.partsupp_table,
        "part_table": args.part_table,
        "partsupp_emb_col": args.partsupp_emb_col,
        "partsupp_emb_dim": args.partsupp_emb_dim,
        "part_emb_col": args.part_emb_col,
        "part_emb_dim": args.part_emb_dim,
        "methods": methods,
        "input_strategy": "concat (norm-aware) on deep_join + wiki_join",
        "learn_frac": args.learn_frac,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "cache_per_cluster": CACHE_PER_CLUSTER,
        "n_queries": args.n_queries,
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(CACHE))
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    ap.add_argument("--learn-seed", type=int, default=42)
    sub = ap.add_subparsers(dest="kind", required=True)

    sv = sub.add_parser("vector")
    sv.add_argument("--table", required=True)
    sv.add_argument("--emb1-col", required=True)
    sv.add_argument("--emb2-col", required=True)
    sv.add_argument("--emb1-dim", type=int, required=True)
    sv.add_argument("--emb2-dim", type=int, required=True)
    sv.add_argument("--out-prefix", required=True)

    sj = sub.add_parser("join")
    sj.add_argument("--partsupp-table", required=True)
    sj.add_argument("--part-table", required=True)
    sj.add_argument("--partsupp-emb-col", required=True)
    sj.add_argument("--partsupp-emb-dim", type=int, required=True)
    sj.add_argument("--part-emb-col", required=True)
    sj.add_argument("--part-emb-dim", type=int, required=True)
    sj.add_argument("--out-prefix", required=True)

    args = ap.parse_args()
    if args.kind == "vector":
        run_vector(args)
    else:
        run_join(args)


if __name__ == "__main__":
    main()
