#!/usr/bin/env python3
"""
RQ2 잔여 실험 일괄 실행 — 8M redo 완료 후 연쇄 실행

#1 8M RANDOM20 gradient (s=0.010, 0.050, 0.500)
#2 SIFT 128d D_target 재계산
#3 SIFT KM20 vs BERN (5-seed, s=0.500)
#4 SIFT RANDOM20 gradient (s=0.010, 0.050, 0.500)
#5 1M s=0.100, 0.300 KM20 vs RANDOM20 (5-seed)

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/rq1_rq2_remaining_all.py
"""
import json, re, time, os
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
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
N_QUERIES = 100
RANDOM_SEED_SQL = 0.42

EST_RE = re.compile(r"Estimated cardinality for range query on table (\S+): ([\d.eE+\-]+)")


def kst():
    return datetime.now(timezone(timedelta(hours=9))).strftime("%H:%M:%S")


def emb_to_pgvec(emb):
    return "[" + ",".join("%.7f" % float(x) for x in emb) + "]"


def find_scan_node(plan):
    node = plan
    while True:
        if "Scan" in node.get("Node Type", ""):
            return node
        children = node.get("Plans", [])
        if not children:
            return node
        node = children[0]


def run_queries(cur, queries, qp, table, method, seed, log_path, emb_col="embedding"):
    cur.execute(f"SELECT setseed({seed})")
    cur.execute("SET vector.sample_size = 385")
    cur.execute("SET vector.update_sample_size = off")
    cur.execute("SET vector.sample_update_cycle = 50")
    cur.execute(f"SET vector.sampling_method = '{method}'")

    log_offset = log_path.stat().st_size if log_path.exists() else 0
    results = []
    emb_col_db = "ps_embedding" if "partsupp" in table else "c_embedding"

    for q in queries:
        qid = q["query_id"]
        D = q["D_target"]
        true_card = q["true_card"]
        emb = np.asarray(qp.iloc[qid][emb_col], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        sql = (f"EXPLAIN (ANALYZE, FORMAT JSON) "
               f"SELECT count(*) FROM {table} "
               f"WHERE ({emb_col_db} <-> '{vec_str}'::vector) < {D}")
        try:
            cur.execute(sql)
            plan = cur.fetchone()[0][0]["Plan"]
            scan = find_scan_node(plan)
            pr = scan.get("Plan Rows")
            qe = max(pr / true_card, true_card / pr) if pr and pr > 0 and true_card > 0 else None
            results.append({"query_id": qid, "true_card": true_card, "plan_rows": pr, "q_error": qe})
        except Exception as e:
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


def multiseed_paired(conn, queries, qp, table, sels_to_measure, seeds, log_path, label, emb_col="embedding"):
    """Multi-seed BERN vs STRAT measurement for given selectivities."""
    all_results = {}
    for sel in sels_to_measure:
        qs_sel = [q for q in queries if abs(q["selectivity"] - sel) < 0.0001]
        if not qs_sel:
            continue
        print(f"\n[{kst()}] --- {label} s={sel} ({len(qs_sel)} queries) ---")
        seed_data = []
        for seed in seeds:
            ts = time.time()
            bern = run_queries(conn.cursor(), qs_sel, qp, table, "bernoulli", seed, log_path, emb_col)
            strat = run_queries(conn.cursor(), qs_sel, qp, table, "stratified", seed, log_path, emb_col)
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
        all_results[f"s{sel}"] = seed_data
    return all_results


def aggregate_results(results):
    agg = {}
    for key, seeds in results.items():
        valid = [r for r in seeds if r.get("n", 0) > 0]
        if valid:
            diffs = [r["diff_pct"] for r in valid]
            rng = np.random.default_rng(42)
            boot = [np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(10000)]
            ci = np.percentile(boot, [2.5, 97.5])
            agg[key] = {"mean": float(np.mean(diffs)), "ci": [float(ci[0]), float(ci[1])], "per_seed": valid}
    return agg


def swap_to_random(conn, table):
    with conn.cursor() as cur:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS km20_backup integer")
        cur.execute(f"UPDATE {table} SET km20_backup = stratum_id")
        cur.execute(f"SELECT setseed({RANDOM_SEED_SQL})")
        cur.execute(f"UPDATE {table} SET stratum_id = floor(random() * 20)::integer")
        cur.execute(f"ANALYZE {table}")
    print(f"[{kst()}] RANDOM20 partition set on {table}")


def restore_km20(conn, table):
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {table} SET stratum_id = km20_backup")
        cur.execute(f"ALTER TABLE {table} DROP COLUMN km20_backup")
        cur.execute(f"ANALYZE {table}")
    print(f"[{kst()}] KM20 restored on {table}")


def dtarget_binary_search(conn, table, emb_col, qp, n_queries, target_sel, total_rows):
    """Binary search for D_target that gives actual_sel ≈ target_sel."""
    print(f"[{kst()}] D_target binary search: {table}, target_sel={target_sel}, total={total_rows}")
    results = []
    with conn.cursor() as cur:
        cur.execute("SET vector.update_sample_size = off")
        for qid in range(n_queries):
            emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
            vec_str = emb_to_pgvec(emb)
            # Get distance range
            cur.execute(f"SELECT min({emb_col} <-> '{vec_str}'::vector), max({emb_col} <-> '{vec_str}'::vector) FROM {table}")
            d_min, d_max = cur.fetchone()
            lo, hi = float(d_min), float(d_max)
            target_count = int(total_rows * target_sel)
            # Binary search
            for _ in range(30):
                mid = (lo + hi) / 2
                cur.execute(f"SELECT count(*) FROM {table} WHERE ({emb_col} <-> '{vec_str}'::vector) < {mid}")
                cnt = cur.fetchone()[0]
                if cnt < target_count:
                    lo = mid
                else:
                    hi = mid
                if abs(cnt - target_count) / max(target_count, 1) < 0.01:
                    break
            cur.execute(f"SELECT count(*) FROM {table} WHERE ({emb_col} <-> '{vec_str}'::vector) < {hi}")
            final_cnt = cur.fetchone()[0]
            results.append({
                "query_id": qid, "D_target": hi,
                "true_card": final_cnt, "actual_sel": final_cnt / total_rows
            })
            if (qid + 1) % 25 == 0:
                print(f"[{kst()}]   q{qid+1}/{n_queries} D={hi:.4f} cnt={final_cnt} sel={final_cnt/total_rows:.4f}")
    return results


def main():
    print(f"[{kst()}] ========================================")
    print(f"[{kst()}] RQ2 REMAINING EXPERIMENTS — ALL IN ONE")
    print(f"[{kst()}] ========================================")

    qp = pq.read_table(f"{CACHE}/query_pool.parquet").to_pandas()
    qs = pq.read_table(f"{CACHE}/query_selectivity.parquet").to_pandas()

    log_candidates = sorted(Path(LOG_DIR).glob("exqutor-*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else Path(f"{LOG_DIR}/exqutor.log")

    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)
    t_total = time.time()
    all_summaries = {}

    # ================================================================
    # #1: 8M RANDOM20 gradient
    # ================================================================
    print(f"\n[{kst()}] ====== #1: 8M RANDOM20 GRADIENT ======")
    TABLE_8M = "partsupp_deep_10_phase7_8m_subset"

    dtarget_8m = json.load(open(f"{CACHE}/phase7_8m_dtarget_recalc_clean.json"))
    queries_8m = []
    for r in dtarget_8m["results"][:N_QUERIES]:
        queries_8m.append({"query_id": r["query_id"], "D_target": r["D_target_8m"],
                           "true_card": r["true_card_8m"], "selectivity": 0.500})

    # Also need lower selectivities for 8M — use 1M D_target as proxy (smaller D → lower sel on 8M too)
    for sel in [0.010, 0.050]:
        qs_sel = qs[(qs["selectivity"] == sel) & (qs["query_id"] < N_QUERIES)]
        for _, row in qs_sel.iterrows():
            queries_8m.append({"query_id": int(row["query_id"]), "D_target": float(row["D_target"]),
                               "true_card": int(row["true_cardinality"]), "selectivity": sel})

    # KM20 first
    print(f"[{kst()}] 8M KM20 measurement (s=0.010, 0.050)")
    km20_8m = multiseed_paired(conn, queries_8m, qp, TABLE_8M, [0.010, 0.050], SEEDS, log_path, "8M-KM20")

    # RANDOM20
    swap_to_random(conn, TABLE_8M)
    print(f"[{kst()}] 8M RANDOM20 measurement (s=0.010, 0.050, 0.500)")
    rand_8m = multiseed_paired(conn, queries_8m, qp, TABLE_8M, [0.010, 0.050, 0.500], SEEDS, log_path, "8M-RAND")
    restore_km20(conn, TABLE_8M)

    all_summaries["8m_km20"] = aggregate_results(km20_8m)
    all_summaries["8m_rand"] = aggregate_results(rand_8m)

    # ================================================================
    # #2: SIFT D_target recalculation
    # ================================================================
    print(f"\n[{kst()}] ====== #2: SIFT D_target RECALC ======")
    TABLE_SIFT = "customer_sift_10_phase7_noidx_subset"

    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {TABLE_SIFT}")
        sift_total = cur.fetchone()[0]
        cur.execute(f"SELECT count(DISTINCT stratum_id) FROM {TABLE_SIFT} WHERE stratum_id IS NOT NULL")
        sift_strata = cur.fetchone()[0]
    print(f"[{kst()}] SIFT: {sift_total} rows, {sift_strata} strata")

    # Need SIFT query pool
    sift_qp_path = f"{CACHE}/sift_query_pool.parquet"
    if os.path.exists(sift_qp_path):
        sift_qp = pq.read_table(sift_qp_path).to_pandas()
        print(f"[{kst()}] Loaded SIFT query pool: {len(sift_qp)}")
    else:
        print(f"[{kst()}] Creating SIFT query pool from DB...")
        with conn.cursor() as cur:
            cur.execute(f"SELECT c_custkey, c_embedding FROM {TABLE_SIFT} ORDER BY random() LIMIT {N_QUERIES}")
            rows = cur.fetchall()
        sift_qp = pd.DataFrame([{"query_id": i, "embedding": list(map(float, str(r[1]).strip("[]").split(",")))} for i, r in enumerate(rows)])
        sift_qp.to_parquet(sift_qp_path, index=False)
        print(f"[{kst()}] Saved SIFT query pool: {len(sift_qp)}")

    # D_target for multiple selectivities
    sift_queries = {}
    for sel in [0.010, 0.050, 0.500]:
        print(f"[{kst()}] SIFT D_target for s={sel}...")
        dt = dtarget_binary_search(conn, TABLE_SIFT, "c_embedding", sift_qp, N_QUERIES, sel, sift_total)
        sift_queries[sel] = [{"query_id": r["query_id"], "D_target": r["D_target"],
                              "true_card": r["true_card"], "selectivity": sel} for r in dt]

    sift_all_queries = []
    for sel_qs in sift_queries.values():
        sift_all_queries.extend(sel_qs)

    sift_dt_out = f"{CACHE}/sift_dtarget_multsel.json"
    with open(sift_dt_out, "w") as f:
        json.dump({"total": sift_total, "queries": {str(k): v for k, v in sift_queries.items()}}, f, indent=2, default=str)
    print(f"[{kst()}] Saved {sift_dt_out}")

    # ================================================================
    # #3: SIFT KM20 vs BERN (5-seed)
    # ================================================================
    print(f"\n[{kst()}] ====== #3: SIFT KM20 vs BERN ======")
    km20_sift = multiseed_paired(conn, sift_all_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, "SIFT-KM20", "embedding")
    all_summaries["sift_km20"] = aggregate_results(km20_sift)

    # ================================================================
    # #4: SIFT RANDOM20 gradient
    # ================================================================
    print(f"\n[{kst()}] ====== #4: SIFT RANDOM20 GRADIENT ======")
    swap_to_random(conn, TABLE_SIFT)
    rand_sift = multiseed_paired(conn, sift_all_queries, sift_qp, TABLE_SIFT, [0.010, 0.050, 0.500], SEEDS, log_path, "SIFT-RAND", "embedding")
    restore_km20(conn, TABLE_SIFT)
    all_summaries["sift_rand"] = aggregate_results(rand_sift)

    # ================================================================
    # #5: 1M s=0.100, 0.300 KM20 vs RANDOM20 multi-seed
    # ================================================================
    print(f"\n[{kst()}] ====== #5: 1M MID-SELECTIVITY GRADIENT ======")
    TABLE_1M = "partsupp_deep_10_subset_1m"

    qs_mid = qs[(qs["selectivity"].isin([0.100, 0.300])) & (qs["query_id"] < N_QUERIES)]
    mid_queries = [{"query_id": int(r["query_id"]), "D_target": float(r["D_target"]),
                    "true_card": int(r["true_cardinality"]), "selectivity": float(r["selectivity"])}
                   for _, r in qs_mid.iterrows()]

    km20_1m_mid = multiseed_paired(conn, mid_queries, qp, TABLE_1M, [0.100, 0.300], SEEDS, log_path, "1M-KM20")

    swap_to_random(conn, TABLE_1M)
    rand_1m_mid = multiseed_paired(conn, mid_queries, qp, TABLE_1M, [0.100, 0.300], SEEDS, log_path, "1M-RAND")
    restore_km20(conn, TABLE_1M)

    all_summaries["1m_mid_km20"] = aggregate_results(km20_1m_mid)
    all_summaries["1m_mid_rand"] = aggregate_results(rand_1m_mid)

    conn.close()
    elapsed = time.time() - t_total

    # ================================================================
    # Final summary
    # ================================================================
    print(f"\n{'#'*60}")
    print(f"# ALL RQ2 REMAINING EXPERIMENTS COMPLETE")
    print(f"# Total elapsed: {elapsed:.0f}s ({elapsed/60:.0f}min)")
    print(f"{'#'*60}")

    for name, data in all_summaries.items():
        print(f"\n--- {name} ---")
        for sel_key, agg in data.items():
            print(f"  {sel_key}: mean={agg['mean']:+.3f}% CI [{agg['ci'][0]:+.3f}, {agg['ci'][1]:+.3f}]")

    out = f"{CACHE}/rq2_remaining_all_summary.json"
    with open(out, "w") as f:
        json.dump({"elapsed_s": round(elapsed, 1), "results": all_summaries}, f, indent=2, default=str)
    print(f"\n[{kst()}] saved {out}")


if __name__ == "__main__":
    main()
