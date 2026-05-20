#!/usr/bin/env python3
"""
RQ1 SIFT Native sampling 측정 (SYSTEM vs BERNOULLI, multi-seed × multi-sel)

phase4_native.py (DEEP) + phase6_multiseed.py (multi-seed) + phase7_sift_128d.py (SIFT) 합성.

vector.c L940 가 결정하는 sampling clause (SYSTEM or BERNOULLI) 에 따라 출력 파일명만 다름.
GUC vector.sampling_method='bernoulli' 로 native path (line 940) 강제.
multi-seed: PG setseed() 5 회 — phase6 와 동일.

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/sift_rq1_native.py
"""
import argparse
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq
import scipy.stats as sst

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")
LOG_DIR = Path("/mnt/hdd0/home/capstone2026/log")
TABLE = "customer_sift_10_phase7_noidx_subset"
EMBED_COL = "c_embedding"
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]
N_QUERIES = 100
PORT = 55436
DB = "wns41559"
USER = "wns41559"

EST_RE = re.compile(
    r"Estimated cardinality for range query on table (\S+): ([\d.eE+\-]+)"
)


def kst() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def emb_to_pgvec(emb) -> str:
    return "[" + ",".join(f"{float(x):.7f}" for x in emb) + "]"


def find_scan_node(plan: dict) -> dict:
    node = plan
    while True:
        if "Scan" in node.get("Node Type", ""):
            return node
        children = node.get("Plans", [])
        if not children:
            return node
        node = children[0]


def run_one_cell(cur, qs_sel, qp, sel: float, seed: float, log_path: Path) -> pd.DataFrame:
    """one (sel, seed) cell — 100 query 측정."""
    cur.execute(f"SELECT setseed({seed})")
    cur.execute("SET vector.sample_size = 385")
    cur.execute("SET vector.update_sample_size = off")
    cur.execute("SET vector.sample_update_cycle = 50")
    cur.execute("SET vector.sampling_method = 'bernoulli'")  # native path (line 940)

    log_offset = log_path.stat().st_size if log_path.exists() else 0

    results = []
    for _, row in qs_sel.iterrows():
        qid = int(row["query_id"])
        D = float(row["D_target"])
        true_card = int(row["true_cardinality"])
        emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        sql = (
            f"EXPLAIN (ANALYZE, FORMAT JSON) "
            f"SELECT count(*) FROM {TABLE} "
            f"WHERE ({EMBED_COL} <-> '{vec_str}'::vector) < {D}"
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
                "query_id": qid, "selectivity": sel, "seed": seed,
                "D_target": D, "true_card": true_card,
                "plan_rows": plan_rows, "actual_rows": actual_rows,
                "sampling_method": sampling_method,
                "q_error": qerr,
                "error": None,
            })
        except Exception as exc:
            results.append({
                "query_id": qid, "selectivity": sel, "seed": seed,
                "D_target": D, "true_card": true_card,
                "plan_rows": None, "actual_rows": None,
                "sampling_method": None,
                "q_error": None,
                "error": str(exc)[:300],
            })

    # hook_est from log tail
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
    ap.add_argument("--mode", required=True, choices=["system", "bernoulli"],
                    help="output naming only — actual sampling determined by vector.c L940 build")
    ap.add_argument("--out-prefix", default=None,
                    help="default: sift_rq1_{mode}")
    ap.add_argument("--n-queries", type=int, default=N_QUERIES)
    args = ap.parse_args()

    out_prefix = args.out_prefix or f"sift_rq1_{args.mode}"
    print(f"[{kst()}] === SIFT RQ1 native — mode={args.mode}, out={out_prefix} ===")

    qp = pq.read_table(CACHE / "query_pool_sift.parquet").to_pandas()
    qs_full = pq.read_table(CACHE / "query_selectivity_sift_v2.parquet").to_pandas()
    print(f"[{kst()}] loaded: queries={len(qp)}, sel grid={len(qs_full)} rows")

    log_candidates = sorted(LOG_DIR.glob("postgres_exqutor*.log"), reverse=True)
    if not log_candidates:
        log_candidates = sorted(LOG_DIR.glob("exqutor-*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else LOG_DIR / "postgres_exqutor.log"
    print(f"[{kst()}] log file: {log_path}")

    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)

    all_dfs = []
    summary_rows = []
    t_total = time.time()

    for sel in SELECTIVITIES:
        qs_sel = qs_full[(qs_full["selectivity"] == sel) & (qs_full["query_id"] < args.n_queries)].reset_index(drop=True)
        if len(qs_sel) == 0:
            print(f"[{kst()}] skip s={sel}: no queries")
            continue
        for seed in SEEDS:
            t0 = time.time()
            df = run_one_cell(conn.cursor(), qs_sel, qp, sel, seed, log_path)
            all_dfs.append(df)
            n_valid = int(df["q_error"].notna().sum())
            n_valid_hook = int(df["q_error_hook"].notna().sum())
            med_plan = float(df["q_error"].median()) if n_valid else float("nan")
            med_hook = float(df["q_error_hook"].median()) if n_valid_hook else float("nan")
            elapsed = time.time() - t0
            print(
                f"[{kst()}]   s={sel} seed={seed} ({elapsed:.1f}s) "
                f"valid_plan={n_valid}/{len(df)} med_plan_qe={med_plan:.4f} "
                f"valid_hook={n_valid_hook} med_hook_qe={med_hook:.4f}"
            )
            summary_rows.append({
                "selectivity": sel, "seed": seed,
                "n_valid_plan": n_valid, "median_q_error_plan": med_plan,
                "n_valid_hook": n_valid_hook, "median_q_error_hook": med_hook,
                "elapsed_s": round(elapsed, 1),
            })

    conn.close()

    full_df = pd.concat(all_dfs, ignore_index=True)
    out_pq = CACHE / f"{out_prefix}.parquet"
    full_df.to_parquet(out_pq, index=False)
    print(f"\n[{kst()}] saved {out_pq} ({len(full_df)} rows)")

    sm_df = pd.DataFrame(summary_rows)
    print(f"\n--- per-cell summary ---")
    for sel in SELECTIVITIES:
        sub = sm_df[sm_df.selectivity == sel]
        if len(sub):
            print(
                f"  s={sel}: med_plan_qe mean={sub.median_q_error_plan.mean():.4f} "
                f"std={sub.median_q_error_plan.std():.4f} | "
                f"med_hook_qe mean={sub.median_q_error_hook.mean():.4f} "
                f"std={sub.median_q_error_hook.std():.4f}"
            )

    meta = {
        "kst": kst(),
        "args": vars(args),
        "table": TABLE,
        "selectivities": SELECTIVITIES,
        "seeds": SEEDS,
        "n_queries": args.n_queries,
        "elapsed_s": round(time.time() - t_total, 1),
        "per_cell_summary": summary_rows,
    }
    out_meta = CACHE / f"{out_prefix}_meta.json"
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] total elapsed {meta['elapsed_s']}s")


if __name__ == "__main__":
    main()
