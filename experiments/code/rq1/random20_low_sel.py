#!/usr/bin/env python3
"""
실험 B 확장 — 낮은 selectivity에서 KM20 vs RANDOM20 multi-seed 비교

가설: cluster 집중도(HHI)가 높은 저selectivity 영역에서는
      KM20이 RANDOM20보다 나을 수 있다.

방법:
  s=0.010, 0.050 각각에서:
  1. KM20 partition으로 STRAT 5-seed 측정
  2. RANDOM20 partition으로 STRAT 5-seed 측정
  3. paired 비교

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/rq1_random20_low_sel.py
"""

import json, re, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq
import scipy.stats as sst

CACHE = "/mnt/hdd0/home/capstone2026/cache/rq1"
LOG_DIR = "/mnt/hdd0/home/capstone2026/log"
PORT = 55436
DB = "wns41559"
USER = "wns41559"
TABLE = "partsupp_deep_10_subset_1m"
N_QUERIES = 100
RANDOM_SEED_SQL = 0.42
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
TARGET_SELS = [0.010, 0.050]

EST_RE = re.compile(r"Estimated cardinality for range query on table (\S+): ([\d.eE+\-]+)")


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def emb_to_pgvec(emb):
    return "[" + ",".join(f"{float(x):.7f}" for x in emb) + "]"


def find_scan_node(plan):
    node = plan
    while True:
        if "Scan" in node.get("Node Type", ""):
            return node
        children = node.get("Plans", [])
        if not children:
            return node
        node = children[0]


def run_queries(cur, qs_sub, qp, method, seed, log_path):
    cur.execute(f"SELECT setseed({seed})")
    cur.execute("SET vector.sample_size = 385")
    cur.execute("SET vector.update_sample_size = off")
    cur.execute("SET vector.sample_update_cycle = 50")
    cur.execute(f"SET vector.sampling_method = '{method}'")

    log_offset = log_path.stat().st_size if log_path.exists() else 0
    results = []

    for _, row in qs_sub.iterrows():
        qid, D, true_card = int(row["query_id"]), float(row["D_target"]), int(row["true_cardinality"])
        emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)
        sql = f"EXPLAIN (ANALYZE, FORMAT JSON) SELECT count(*) FROM {TABLE} WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}"
        try:
            cur.execute(sql)
            plan = cur.fetchone()[0][0]["Plan"]
            scan = find_scan_node(plan)
            pr = scan.get("Plan Rows")
            qe = max(pr / true_card, true_card / pr) if pr and pr > 0 and true_card > 0 else None
            results.append({"query_id": qid, "true_card": true_card, "plan_rows": pr, "q_error": qe})
        except:
            results.append({"query_id": qid, "true_card": true_card, "plan_rows": None, "q_error": None})

    hook_ests = []
    if log_path.exists():
        with open(log_path, "rb") as f:
            f.seek(log_offset)
            for m in EST_RE.finditer(f.read().decode("utf-8", errors="replace")):
                hook_ests.append(float(m.group(2)))

    df = pd.DataFrame(results)
    for i in range(len(df)):
        he = hook_ests[i] if i < len(hook_ests) else None
        df.loc[i, "hook_est"] = he
        tc = df.loc[i, "true_card"]
        df.loc[i, "q_error_hook"] = max(he / tc, tc / he) if he and he > 0 and tc > 0 else None
    return df


def measure_partition(conn, qp, qs, partition_name, log_path):
    """한 partition (KM20 or RANDOM20) 상태에서 multi-seed STRAT + BERN 측정."""
    all_results = {}

    for sel in TARGET_SELS:
        qs_sel = qs[(qs["selectivity"] == sel) & (qs["query_id"] < N_QUERIES)].reset_index(drop=True)
        print(f"\n[{kst()}] --- {partition_name} s={sel} ({len(qs_sel)} queries) ---")
        seed_data = []

        for seed in SEEDS:
            ts = time.time()
            bern = run_queries(conn.cursor(), qs_sel, qp, "bernoulli", seed, log_path)
            strat = run_queries(conn.cursor(), qs_sel, qp, "stratified", seed, log_path)

            pair = bern[["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qe_b"}).merge(
                strat[["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qe_s"}), on="query_id"
            ).dropna()

            if len(pair) > 0:
                try:
                    p = float(sst.wilcoxon(pair["qe_s"].values, pair["qe_b"].values, alternative="less", zero_method="wilcox").pvalue)
                except:
                    p = float("nan")
                mb, ms = float(np.median(pair["qe_b"])), float(np.median(pair["qe_s"]))
                diff = (mb - ms) / mb * 100 if mb > 0 else 0
                nb = int(np.sum(pair["qe_s"] < pair["qe_b"]))
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                r = {"seed": seed, "n": len(pair), "bern_med": mb, "strat_med": ms,
                     "diff_pct": diff, "p": p, "n_better": nb}
                seed_data.append(r)
                print(f"[{kst()}]   seed={seed}: B={mb:.4f} S={ms:.4f} d={diff:+.2f}% p={p:.2e}{sig} win={nb}/{len(pair)} ({time.time()-ts:.0f}s)")
            else:
                seed_data.append({"seed": seed, "n": 0})
                print(f"[{kst()}]   seed={seed}: no valid pairs")

        all_results[f"s{sel}"] = seed_data
    return all_results


def main():
    print(f"[{kst()}] RANDOM20 low-selectivity multi-seed comparison")

    qp = pq.read_table(f"{CACHE}/query_pool.parquet").to_pandas()
    qs = pq.read_table(f"{CACHE}/query_selectivity.parquet").to_pandas()

    log_candidates = sorted(Path(LOG_DIR).glob("exqutor-*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else Path(f"{LOG_DIR}/exqutor.log")
    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)
    t0 = time.time()

    # === Phase 1: KM20 partition (현재 상태) ===
    print(f"\n[{kst()}] ====== PHASE 1: KM20 PARTITION ======")
    km20_results = measure_partition(conn, qp, qs, "KM20", log_path)

    # === Phase 2: RANDOM20 partition ===
    print(f"\n[{kst()}] ====== PHASE 2: RANDOM20 PARTITION ======")
    with conn.cursor() as cur:
        cur.execute(f"ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS km20_backup integer")
        cur.execute(f"UPDATE {TABLE} SET km20_backup = stratum_id")
        cur.execute(f"SELECT setseed({RANDOM_SEED_SQL})")
        cur.execute(f"UPDATE {TABLE} SET stratum_id = floor(random() * 20)::integer")
        cur.execute(f"ANALYZE {TABLE}")
    print(f"[{kst()}] RANDOM20 partition set (setseed={RANDOM_SEED_SQL})")

    rand_results = measure_partition(conn, qp, qs, "RANDOM20", log_path)

    # === Restore ===
    print(f"\n[{kst()}] Restoring KM20...")
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {TABLE} SET stratum_id = km20_backup")
        cur.execute(f"ALTER TABLE {TABLE} DROP COLUMN km20_backup")
        cur.execute(f"ANALYZE {TABLE}")
    print(f"[{kst()}] KM20 restored")
    conn.close()

    elapsed = time.time() - t0

    # === Analysis ===
    print(f"\n{'#'*60}")
    print(f"# COMPARISON: KM20 vs RANDOM20 (multi-seed)")
    print(f"{'#'*60}")

    summary = {"elapsed_s": round(elapsed, 1), "sels": {}}

    for sel in TARGET_SELS:
        key = f"s{sel}"
        km = [r for r in km20_results[key] if r.get("n", 0) > 0]
        rd = [r for r in rand_results[key] if r.get("n", 0) > 0]

        print(f"\n=== s={sel} ===")
        if km:
            km_diffs = [r["diff_pct"] for r in km]
            rng = np.random.default_rng(42)
            km_boot = [np.mean(rng.choice(km_diffs, size=len(km_diffs), replace=True)) for _ in range(10000)]
            km_ci = np.percentile(km_boot, [2.5, 97.5])
            print(f"  KM20:     mean={np.mean(km_diffs):+.3f}%  CI [{km_ci[0]:+.3f}, {km_ci[1]:+.3f}]  seeds={len(km)}")
        if rd:
            rd_diffs = [r["diff_pct"] for r in rd]
            rng = np.random.default_rng(42)
            rd_boot = [np.mean(rng.choice(rd_diffs, size=len(rd_diffs), replace=True)) for _ in range(10000)]
            rd_ci = np.percentile(rd_boot, [2.5, 97.5])
            print(f"  RANDOM20: mean={np.mean(rd_diffs):+.3f}%  CI [{rd_ci[0]:+.3f}, {rd_ci[1]:+.3f}]  seeds={len(rd)}")

        if km and rd:
            diff_of_diff = np.mean(km_diffs) - np.mean(rd_diffs)
            try:
                stat, p = sst.mannwhitneyu(km_diffs, rd_diffs, alternative='greater')
                print(f"  KM20 - RANDOM20 = {diff_of_diff:+.3f}%p  (MWU p={p:.4f})")
            except:
                print(f"  KM20 - RANDOM20 = {diff_of_diff:+.3f}%p")

            summary["sels"][key] = {
                "km20": {"mean": float(np.mean(km_diffs)), "ci": [float(km_ci[0]), float(km_ci[1])], "per_seed": km},
                "rand": {"mean": float(np.mean(rd_diffs)), "ci": [float(rd_ci[0]), float(rd_ci[1])], "per_seed": rd},
            }

    out = f"{CACHE}/random20_low_sel_summary.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[{kst()}] saved {out}")
    print(f"[{kst()}] total: {elapsed:.0f}s")


if __name__ == "__main__":
    main()
