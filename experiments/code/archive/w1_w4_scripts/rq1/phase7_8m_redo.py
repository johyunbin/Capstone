#!/usr/bin/env python3
"""
Phase 7 Redo — 8M 외적 타당성 (D_target 재계산 완료, actual_sel ≈ 0.5)

이전 Phase 7은 D_target 미재계산으로 actual_sel ≈ 0.0001 → artifact 발생.
본 측정은 8M에서 재계산된 D_target 사용, actual_sel ≈ 0.5001.

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/rq1_phase7_8m_redo.py
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
TABLE = "partsupp_deep_10_phase7_8m_subset"
N_QUERIES = 100
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]

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

def run_queries(cur, queries, qp, method, seed, log_path):
    cur.execute(f"SELECT setseed({seed})")
    cur.execute("SET vector.sample_size = 385")
    cur.execute("SET vector.update_sample_size = off")
    cur.execute("SET vector.sample_update_cycle = 50")
    cur.execute(f"SET vector.sampling_method = '{method}'")

    log_offset = log_path.stat().st_size if log_path.exists() else 0
    results = []

    for q in queries:
        qid = q["query_id"]
        D = q["D_target_8m"]
        true_card = q["true_card_8m"]
        emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        sql = (f"EXPLAIN (ANALYZE, FORMAT JSON) "
               f"SELECT count(*) FROM {TABLE} "
               f"WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}")
        try:
            cur.execute(sql)
            plan = cur.fetchone()[0][0]["Plan"]
            scan = find_scan_node(plan)
            pr = scan.get("Plan Rows")
            qe = max(pr/true_card, true_card/pr) if pr and pr > 0 and true_card > 0 else None
            results.append({"query_id": qid, "true_card": true_card, "plan_rows": pr, "q_error": qe})
        except Exception as e:
            results.append({"query_id": qid, "true_card": true_card, "plan_rows": None, "q_error": None, "error": str(e)[:200]})

    # Parse hook_est
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
        df.loc[i, "q_error_hook"] = max(he/tc, tc/he) if he and he > 0 and tc > 0 else None
    return df

def main():
    print(f"[{kst()}] Phase 7 Redo — 8M external validity (D_target recalculated)")

    # Load recalculated D_target
    dtarget = json.load(open(f"{CACHE}/phase7_8m_dtarget_recalc_clean.json"))
    queries = dtarget["results"][:N_QUERIES]
    print(f"[{kst()}] 8M D_target: {len(queries)} queries, actual_sel median ≈ {np.median([q['actual_sel_8m'] for q in queries]):.4f}")

    qp = pq.read_table(f"{CACHE}/query_pool.parquet").to_pandas()

    log_candidates = sorted(Path(LOG_DIR).glob("exqutor-*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else Path(f"{LOG_DIR}/exqutor.log")
    print(f"[{kst()}] log: {log_path}")

    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)
    t0 = time.time()

    seed_results = []
    for seed in SEEDS:
        ts = time.time()
        bern = run_queries(conn.cursor(), queries, qp, "bernoulli", seed, log_path)
        strat = run_queries(conn.cursor(), queries, qp, "stratified", seed, log_path)

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
            seed_results.append(r)
            print(f"[{kst()}] seed={seed}: B={mb:.4f} S={ms:.4f} d={diff:+.2f}% p={p:.2e}{sig} win={nb}/{len(pair)} ({time.time()-ts:.0f}s)")
        else:
            seed_results.append({"seed": seed, "n": 0})
            print(f"[{kst()}] seed={seed}: no valid pairs ({time.time()-ts:.0f}s)")

    conn.close()
    elapsed = time.time() - t0

    # Aggregate
    valid = [r for r in seed_results if r.get("n", 0) > 0]
    if valid:
        diffs = [r["diff_pct"] for r in valid]
        rng = np.random.default_rng(42)
        boot = [np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(10000)]
        ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
        print(f"\n{'='*60}")
        print(f"8M EXTERNAL VALIDITY (s≈0.500, {len(valid)} seeds)")
        print(f"  diff%: mean={np.mean(diffs):+.3f}%, CI [{ci_lo:+.3f}, {ci_hi:+.3f}]")
        print(f"  1M reference: +1.64% CI [1.25, 2.02]")
        print(f"  {'CONSISTENT' if ci_lo > 0 else 'NOT SIGNIFICANT'}")

    summary = {
        "dataset": "partsupp_deep_10_phase7_8m_subset",
        "n_rows": 8000000,
        "actual_sel_median": float(np.median([q["actual_sel_8m"] for q in queries])),
        "elapsed_s": round(elapsed, 1),
        "per_seed": seed_results,
        "aggregate": {
            "mean_diff_pct": float(np.mean(diffs)),
            "bootstrap_95ci": [float(ci_lo), float(ci_hi)],
        } if valid else None,
        "reference_1m": {"mean_diff_pct": 1.64, "ci": [1.25, 2.02]},
    }
    out = f"{CACHE}/phase7_8m_redo_summary.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[{kst()}] saved {out}")
    print(f"[{kst()}] total: {elapsed:.0f}s")

if __name__ == "__main__":
    main()
