#!/usr/bin/env python3
"""
RQ3 Wave1 supplement — Halton/Hammersley/Reservoir 를 Multi cell 에 적용.

대상 cell:
  - deep_sift_10:           partsupp_deep_sift_10 (4way)        → measure_multi_vector pattern
  - deep_wiki_10:           partsupp_deep_wiki_10 (4way)        → measure_multi_vector pattern
  - multi_join_deep_wiki:   partsupp_deep_10 ⨝ part_wiki_10     → measure_multi_table_join pattern

기존 km20_emb1/emb2/concat/product 는 KMeans 기반이지만, Wave 1 method 는
PCA-2D 기반 stratification (halton/hammersley) 또는 random partition (reservoir).
Multi cell 에서는 concat([emb1, emb2]) 를 단일 vector 로 취급해 Wave 1 stratify.

Usage:
    python3 measure_multi_wave1.py --cell deep_sift_10 --method halton
    python3 measure_multi_wave1.py --cell deep_wiki_10 --method hammersley
    python3 measure_multi_wave1.py --cell multi_join_deep_wiki --method reservoir

산출:
    {CACHE}/rq3_multi_wave1_{cell}_{method}.parquet
    {CACHE}/rq3_multi_wave1_{cell}_{method}_meta.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/mnt/hdd0/home/capstone2026/cache/rq3")
sys.path.insert(0, str(ROOT))

# import existing helpers from sister scripts
from measure_multi_vector import (  # noqa: E402
    CACHE, SEEDS, SELECTIVITIES, SAMPLE_SIZE, N_STRATA,
    fetch_dual_vectors, build_query_pool,
    measure_strategy, kst,
)
from halton.halton_stratification import fit_halton, assign_halton  # noqa: E402
from hammersley.hammersley_stratification import (  # noqa: E402
    fit_hammersley, assign_hammersley,
)


# ---------------------------------------------------------------------------
# Cell config
# ---------------------------------------------------------------------------

CELL_4WAY = {
    "deep_sift_10": {
        "table": "partsupp_deep_sift_10",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_sift", "emb2_dim": 128,
        "kind": "4way",
    },
    "deep_wiki_10": {
        "table": "partsupp_deep_wiki_10",
        "emb1_col": "ps_embedding_deep", "emb1_dim": 96,
        "emb2_col": "ps_embedding_wiki", "emb2_dim": 768,
        "kind": "4way",
    },
}

CELL_JOIN = {
    "multi_join_deep_wiki": {
        "partsupp_table": "partsupp_deep_10",
        "part_table": "part_wiki_10",
        "partsupp_emb_col": "ps_embedding", "partsupp_emb_dim": 96,
        "part_emb_col": "p_embedding", "part_emb_dim": 768,
        "kind": "join",
    },
}


# ---------------------------------------------------------------------------
# Wave 1 stratification on concat([emb1, emb2])
# ---------------------------------------------------------------------------

def stratify_wave1_concat(
    emb1: np.ndarray, emb2: np.ndarray, method: str,
    n_strata: int = N_STRATA, seed: int = 42, sample_n: int = 100_000,
) -> np.ndarray:
    """concat([emb1, emb2]) 정규화 후 Wave 1 method 로 stratify.

    method: 'halton' | 'hammersley' | 'reservoir'
    """
    if method == "reservoir":
        # streaming uniform — 분포 무시, random partition (random20 와 다른 seed)
        rng = np.random.default_rng(137)
        return rng.integers(0, n_strata, size=emb1.shape[0]).astype(np.int32)

    # halton/hammersley: PCA-2D 기반 → concat 정규화 후 적용
    n1 = float(np.linalg.norm(emb1, axis=1).mean()) or 1.0
    n2 = float(np.linalg.norm(emb2, axis=1).mean()) or 1.0
    e1 = emb1 / n1
    e2 = emb2 / n2
    concat = np.concatenate([e1, e2], axis=1)

    print(f"[{kst()}]   strat: {method} on concat ({concat.shape[1]}d), "
          f"PCA-2D + sample_n={sample_n}")
    rng = np.random.default_rng(seed)
    if sample_n < concat.shape[0]:
        idx = rng.choice(concat.shape[0], size=sample_n, replace=False)
        learn = concat[idx]
    else:
        learn = concat

    if method == "halton":
        mapper = fit_halton(learn, n_strata=n_strata, seed=seed)
        return assign_halton(mapper, concat)
    elif method == "hammersley":
        mapper = fit_hammersley(learn, n_strata=n_strata, seed=seed)
        return assign_hammersley(mapper, concat)
    else:
        raise ValueError(f"unknown method: {method}")


# ---------------------------------------------------------------------------
# 4way cell measurement
# ---------------------------------------------------------------------------

def measure_4way(cell_name: str, method: str, n_queries: int = 100):
    cfg = CELL_4WAY[cell_name]
    table = cfg["table"]

    print(f"[{kst()}] === Wave1 multi 4way: cell={cell_name} method={method} ===")
    emb1, emb2 = fetch_dual_vectors(
        table, cfg["emb1_col"], cfg["emb2_col"],
        cfg["emb1_dim"], cfg["emb2_dim"],
    )
    N = emb1.shape[0]
    print(f"[{kst()}] N={N:,} dims=({emb1.shape[1]}, {emb2.shape[1]})")

    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool(
        emb1, emb2, n_queries=n_queries,
    )

    sids = stratify_wave1_concat(emb1, emb2, method)
    rows = measure_strategy(
        method, sids, emb1, emb2, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, table, also_bernoulli=False,
    )
    return rows, table


# ---------------------------------------------------------------------------
# multi_join cell measurement — partsupp_deep_10 ⨝ part_wiki_10
# ---------------------------------------------------------------------------

def measure_join(cell_name: str, method: str, n_queries: int = 100):
    """join cell 은 measure_multi_table_join 의 NPY cache 를 직접 활용.

    partsupp 8M row × ps_embedding (96d, deep)
    part 2M row × p_embedding (768d, wiki)
    조인 결과: partsupp 의 각 row 에 part_wiki broadcast (FK 4-to-1)
    → row count 는 partsupp 와 동일, emb1=ps_embedding, emb2=p_embedding (broadcast)

    측정 패턴은 4way 와 동일. true_card 도 partsupp full 8M 에서 AND 카운트.
    """
    cfg = CELL_JOIN[cell_name]
    print(f"[{kst()}] === Wave1 multi join: cell={cell_name} method={method} ===")

    # 1) partsupp emb1 load (NPY cache)
    ps_table = cfg["partsupp_table"]
    cache_v = CACHE / f"{ps_table}_vectors.npy"
    cache_k = CACHE / f"{ps_table}_partkeys.npy"
    if not (cache_v.exists() and cache_k.exists()):
        raise FileNotFoundError(
            f"{ps_table} NPY cache not found — run measure_multi_table_join first"
        )
    t0 = time.time()
    ps_vecs = np.load(cache_v)
    ps_partkeys = np.load(cache_k)
    print(f"[{kst()}]   loaded partsupp NPY: vecs {ps_vecs.shape} "
          f"keys {ps_partkeys.shape} ({(ps_vecs.nbytes + ps_partkeys.nbytes)/1e6:.0f} MB) "
          f"in {time.time()-t0:.1f}s")

    # 2) part_wiki load
    part_table = cfg["part_table"]
    part_v = CACHE / f"{part_table}_vectors.npy"
    part_k = CACHE / f"{part_table}_partkeys.npy"
    if not (part_v.exists() and part_k.exists()):
        # try alternate name format
        raise FileNotFoundError(
            f"{part_table} NPY cache not found at {part_v} — "
            "run measure_multi_table_join first"
        )
    t0 = time.time()
    part_vecs_raw = np.load(part_v)
    part_keys_raw = np.load(part_k)
    print(f"[{kst()}]   loaded part NPY: vecs {part_vecs_raw.shape} "
          f"keys {part_keys_raw.shape} ({(part_vecs_raw.nbytes + part_keys_raw.nbytes)/1e6:.0f} MB) "
          f"in {time.time()-t0:.1f}s")

    # 3) FK lookup: partsupp 각 row → part 의 해당 partkey 의 wiki vec
    t0 = time.time()
    sort_idx = np.argsort(part_keys_raw)
    part_keys_sorted = part_keys_raw[sort_idx]
    part_vecs_sorted = part_vecs_raw[sort_idx]
    pos = np.searchsorted(part_keys_sorted, ps_partkeys)
    if (pos >= len(part_keys_sorted)).any() or \
       (part_keys_sorted[np.minimum(pos, len(part_keys_sorted)-1)] != ps_partkeys).any():
        # FK mismatch — fail fast
        miss = (part_keys_sorted[np.minimum(pos, len(part_keys_sorted)-1)] != ps_partkeys).sum()
        raise RuntimeError(f"FK lookup mismatch: {miss} rows")
    wiki_vecs = part_vecs_sorted[pos]
    print(f"[{kst()}]   FK broadcast: wiki_vecs {wiki_vecs.shape} "
          f"in {time.time()-t0:.1f}s")
    del part_vecs_raw, part_keys_raw, part_vecs_sorted, part_keys_sorted

    # 4) 4way pattern: emb1=ps_vecs (96d), emb2=wiki_vecs (768d)
    table_name = f"{ps_table}__{part_table}"
    qids, q1, q2, D1_by_sel, D2_by_sel, true_card = build_query_pool(
        ps_vecs, wiki_vecs, n_queries=n_queries,
    )
    sids = stratify_wave1_concat(ps_vecs, wiki_vecs, method)

    # measure_strategy 가 D1, D2 컬럼명을 D1_target/D2_target 으로 출력 →
    # join 의 D_deep_target/D_wiki_target naming 으로 후처리 rename
    rows = measure_strategy(
        method, sids, ps_vecs, wiki_vecs, qids, q1, q2,
        D1_by_sel, D2_by_sel, true_card, table_name, also_bernoulli=False,
    )
    # rename columns for join consistency
    for r in rows:
        if "D1_target" in r:
            r["D_deep_target"] = r.pop("D1_target")
        if "D2_target" in r:
            r["D_wiki_target"] = r.pop("D2_target")
        if "table" in r:
            r["table_pair"] = r.pop("table")
    return rows, table_name


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", required=True,
                    choices=list(CELL_4WAY.keys()) + list(CELL_JOIN.keys()))
    ap.add_argument("--method", required=True,
                    choices=["halton", "hammersley", "reservoir"])
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--out-dir", default=str(CACHE))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_pq = out_dir / f"rq3_multi_wave1_{args.cell}_{args.method}.parquet"
    out_meta = out_dir / f"rq3_multi_wave1_{args.cell}_{args.method}_meta.json"

    if out_pq.exists():
        print(f"[{kst()}] SKIP — {out_pq.name} already exists")
        return

    t_start = time.time()
    if args.cell in CELL_4WAY:
        rows, table_name = measure_4way(args.cell, args.method, args.n_queries)
        kind = "4way"
    else:
        rows, table_name = measure_join(args.cell, args.method, args.n_queries)
        kind = "join"

    df = pd.DataFrame(rows)
    df.to_parquet(out_pq, index=False)
    print(f"[{kst()}] saved {out_pq} ({len(df):,} rows)")

    smry = (df.groupby(["dataset", "mode", "selectivity"])["q_error"]
              .agg(["mean", "std", "median", "count"]).round(4))
    print(f"\n=== q_error summary ===\n{smry}\n")

    meta = {
        "kst": kst(),
        "cell": args.cell, "method": args.method, "kind": kind,
        "table_or_pair": table_name,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "sample_size": SAMPLE_SIZE,
        "n_strata": N_STRATA,
        "n_queries": args.n_queries,
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()),
        "stratify_basis": ("concat([emb1, emb2]) normalized + PCA-2D"
                            if args.method != "reservoir"
                            else "uniform random partition (seed=137)"),
        "elapsed_s": round(time.time() - t_start, 1),
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] === done in {meta['elapsed_s']}s ===")


if __name__ == "__main__":
    main()
