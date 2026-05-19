#!/usr/bin/env python3
"""
RQ2 W1 sprint — Allocation method 비교 측정.

5 mode × 2 dataset × 5 sel × 5 seed × 100 query.

Modes:
  bernoulli   — vector.sampling_method=bernoulli (BERN baseline)
  equal       — stratified, allocation_method=equal (기존 KM20)
  proportional — stratified, allocation_method=proportional (n_i ∝ N_i)
  neyman      — stratified, allocation_method=neyman (n_i ∝ N_i × σ_i)
  anti_neyman — stratified, allocation_method=anti_neyman (n_i ∝ N_i / σ_i, ablation)

서버: /mnt/hdd0/home/capstone2026/cache/rq2_alloc_native.py
"""
import argparse
import json
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
LOG_DIR = Path("/mnt/hdd0/home/capstone2026/log")
PORT = 55436
DB = "wns41559"
USER = "wns41559"
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]

DATASETS = [
    {
        "name": "DEEP",
        "table": "partsupp_deep_10_subset_1m",
        "embed_col": "ps_embedding",
        "query_pool": CACHE / "query_pool.parquet",
        "query_sel": CACHE / "query_selectivity.parquet",
    },
    {
        "name": "SIFT",
        "table": "customer_sift_10_phase7_noidx_subset",
        "embed_col": "c_embedding",
        "query_pool": CACHE / "query_pool_sift.parquet",
        "query_sel": CACHE / "query_selectivity_sift_v2.parquet",
    },
]

MODES = [
    ("bernoulli", {"vector.sampling_method": "bernoulli"}),
    ("equal", {"vector.sampling_method": "stratified", "vector.allocation_method": "equal"}),
    ("proportional", {"vector.sampling_method": "stratified", "vector.allocation_method": "proportional"}),
    ("neyman", {"vector.sampling_method": "stratified", "vector.allocation_method": "neyman"}),
    ("anti_neyman", {"vector.sampling_method": "stratified", "vector.allocation_method": "anti_neyman"}),
]

EST_RE = re.compile(r"Estimated cardinality for range query on table (\S+): ([\d.eE+\-]+)")


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def emb_to_pgvec(emb):
    return "[" + ",".join(f"{float(x):.7f}" for x in emb) + "]"


def find_scan_node(plan):
    n = plan
    while True:
        if "Scan" in n.get("Node Type", ""):
            return n
        children = n.get("Plans", [])
        if not children:
            return n
        n = children[0]


def run_cell(cur, qs_sel, qp, sel, seed, mode_name, mode_gucs, embed_col, table, log_path):
    cur.execute(f"SELECT setseed({seed})")
    cur.execute("SET vector.sample_size = 385")
    cur.execute("SET vector.update_sample_size = off")
    cur.execute("SET vector.sample_update_cycle = 50")
    for k, v in mode_gucs.items():
        cur.execute(f"SET {k} = '{v}'")

    log_offset = log_path.stat().st_size if log_path.exists() else 0

    results = []
    for _, row in qs_sel.iterrows():
        qid = int(row["query_id"])
        D = float(row["D_target"])
        true_card = int(row["true_cardinality"])
        # query_pool 의 row index = query_id (DEEP/SIFT 둘 다 사전 align 됨)
        emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        sql = (
            f"EXPLAIN (ANALYZE, FORMAT JSON) "
            f"SELECT count(*) FROM {table} "
            f"WHERE ({embed_col} <-> '{vec_str}'::vector) < {D}"
        )
        try:
            cur.execute(sql)
            plan_root = cur.fetchone()[0][0]["Plan"]
            scan = find_scan_node(plan_root)
            plan_rows = scan.get("Plan Rows")
            actual_rows = scan.get("Actual Rows")
            sampling_method = scan.get("Sampling Method")
            qerr = (
                max(plan_rows / true_card, true_card / plan_rows)
                if plan_rows and plan_rows > 0 and true_card > 0
                else None
            )
            results.append({
                "query_id": qid, "selectivity": sel, "seed": seed, "mode": mode_name,
                "D_target": D, "true_card": true_card,
                "plan_rows": plan_rows, "actual_rows": actual_rows,
                "sampling_method": sampling_method,
                "q_error": qerr, "error": None,
            })
        except Exception as exc:
            results.append({
                "query_id": qid, "selectivity": sel, "seed": seed, "mode": mode_name,
                "D_target": D, "true_card": true_card,
                "plan_rows": None, "actual_rows": None, "sampling_method": None,
                "q_error": None, "error": str(exc)[:300],
            })

    hook_ests = []
    if log_path.exists():
        with open(log_path, "rb") as f:
            f.seek(log_offset)
            tail = f.read().decode("utf-8", errors="replace")
        for m in EST_RE.finditer(tail):
            hook_ests.append(float(m.group(2)))

    df = pd.DataFrame(results)
    for i in range(len(df)):
        he = hook_ests[i] if i < len(hook_ests) else None
        df.loc[i, "hook_est"] = he
        if he and he > 0 and df.loc[i, "true_card"] > 0:
            df.loc[i, "q_error_hook"] = max(he / df.loc[i, "true_card"], df.loc[i, "true_card"] / he)
        else:
            df.loc[i, "q_error_hook"] = None
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--out-prefix", default="rq2_alloc")
    ap.add_argument("--datasets", nargs="*", default=None,
                    help="DEEP / SIFT 등 일부만 측정 (기본 둘 다)")
    ap.add_argument("--modes", nargs="*", default=None,
                    help="기본 5 mode 모두; e.g., 'neyman anti_neyman' 만 추가 측정 가능")
    args = ap.parse_args()

    print(f"[{kst()}] === RQ2 W1 — Allocation method 비교 측정 ===")

    log_candidates = sorted(LOG_DIR.glob("postgres_exqutor*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else LOG_DIR / "postgres_exqutor.log"
    print(f"[{kst()}] log: {log_path}")

    use_modes = MODES if not args.modes else [m for m in MODES if m[0] in args.modes]
    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d["name"] in args.datasets]
    print(f"[{kst()}] modes: {[m[0] for m in use_modes]}")
    print(f"[{kst()}] datasets: {[d['name'] for d in use_datasets]}")

    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)

    all_dfs = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === dataset {ds['name']} ({ds['table']}) ===")
        qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
        qs_full = pq.read_table(ds["query_sel"]).to_pandas()
        print(f"[{kst()}] loaded {len(qp)} queries, {len(qs_full)} sel rows")

        for mode_name, mode_gucs in use_modes:
            t_mode = time.time()
            for sel in SELECTIVITIES:
                qs_sel = qs_full[
                    (np.isclose(qs_full["selectivity"], sel)) &
                    (qs_full["query_id"] < args.n_queries)
                ].reset_index(drop=True)
                if len(qs_sel) == 0:
                    print(f"[{kst()}]   skip {mode_name} s={sel}: no rows")
                    continue
                for seed in SEEDS:
                    t0 = time.time()
                    df = run_cell(conn.cursor(), qs_sel, qp, sel, seed, mode_name, mode_gucs,
                                  ds["embed_col"], ds["table"], log_path)
                    df["dataset"] = ds["name"]
                    all_dfs.append(df)
                    n_valid = int(df["q_error"].notna().sum())
                    med = float(df["q_error"].median()) if n_valid else float("nan")
                    elapsed = time.time() - t0
                    print(f"[{kst()}]   {ds['name']} {mode_name} s={sel} seed={seed} "
                          f"({elapsed:.1f}s) valid={n_valid}/{len(df)} med_qe={med:.4f}")
            print(f"[{kst()}] {ds['name']} {mode_name}: total {time.time() - t_mode:.1f}s")

    conn.close()

    full_df = pd.concat(all_dfs, ignore_index=True)
    out_pq = CACHE / f"{args.out_prefix}.parquet"
    full_df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(full_df)} rows)")

    # summary
    print("\n=== mean q_error per (dataset × mode × sel) ===")
    smry = full_df.groupby(["dataset", "mode", "selectivity"])["q_error"].agg(
        ["mean", "std", "median", "count"]
    ).round(4)
    print(smry)

    meta = {
        "kst": kst(),
        "args": vars(args),
        "datasets": [d["name"] for d in use_datasets],
        "modes": [m[0] for m in use_modes],
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "n_queries": args.n_queries,
        "elapsed_s": round(time.time() - t_total, 1),
    }
    with open(CACHE / f"{args.out_prefix}_meta.json", "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
