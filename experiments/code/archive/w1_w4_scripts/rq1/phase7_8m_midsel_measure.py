#!/usr/bin/env python3
"""
8M mid-sel 측정 — DEEP 8M × s∈{0.10, 0.30} × {system, bernoulli, stratified}
5 seed × 100 query × 3 mode × 2 sel = 3,000 rows

W1 sprint 2026-05-06 — RQ1 Cross-Dataset 외적 타당성 매듭.
선행: phase7_8m_midsel_dtarget.sh 실행으로 phase7_8m_dtarget_midsel.json 생성.

서버 사용: /mnt/hdd0/home/capstone2026/cache/rq1_phase7_8m_midsel_measure.py
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
MODES = ["system", "bernoulli", "stratified"]
SEL_TARGETS = [0.10, 0.30]

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

        # 검증 결과: vector hook 의 "Estimated cardinality" log 출력은 ANALYZE 단계에서만 일어남.
        # EXPLAIN-only 로는 hook 안 호출 → q_err_hook 전부 n/a. ANALYZE 유지.
        sql = (f"EXPLAIN (ANALYZE, FORMAT JSON) "
               f"SELECT count(*) FROM {TABLE} "
               f"WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}")
        try:
            cur.execute(sql)
            plan = cur.fetchone()[0][0]["Plan"]
            scan = find_scan_node(plan)
            pr = scan.get("Plan Rows")
            qe = max(pr / true_card, true_card / pr) if pr and pr > 0 and true_card > 0 else None
            results.append({"query_id": qid, "true_card": true_card, "plan_rows": pr, "q_error": qe})
        except Exception as e:
            results.append({"query_id": qid, "true_card": true_card, "plan_rows": None,
                           "q_error": None, "error": str(e)[:200]})

    # Parse hook_est from log
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


def main():
    print(f"[{kst()}] 8M mid-sel measurement (DEEP 8M × s∈{SEL_TARGETS} × {MODES})")

    dtarget = json.load(open(f"{CACHE}/phase7_8m_dtarget_midsel.json"))
    qp = pq.read_table(f"{CACHE}/query_pool.parquet").to_pandas()

    log_candidates = sorted(Path(LOG_DIR).glob("exqutor-*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else Path(f"{LOG_DIR}/exqutor.log")
    print(f"[{kst()}] log: {log_path}")

    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)
    t0 = time.time()

    all_rows = []

    for sel_target in SEL_TARGETS:
        queries = dtarget["results"][str(sel_target)][:N_QUERIES]
        actual_sel_med = float(np.median([q["actual_sel_8m"] for q in queries]))
        print(f"\n[{kst()}] === sel_target={sel_target} (actual_sel_med={actual_sel_med:.4f}) ===")

        for mode in MODES:
            print(f"[{kst()}] --- mode={mode} ---")
            for seed in SEEDS:
                ts0 = time.time()
                df = run_queries(conn.cursor(), queries, qp, mode, seed, log_path)
                df["sel_target"] = sel_target
                df["mode"] = mode
                df["seed"] = seed
                df["actual_sel_med"] = actual_sel_med
                all_rows.append(df)
                med_q = df["q_error_hook"].dropna()
                med_str = f"{float(np.median(med_q)):.4f}" if len(med_q) > 0 else "n/a"
                print(f"[{kst()}] sel={sel_target} mode={mode} seed={seed}: median q_err_hook={med_str} ({time.time()-ts0:.0f}s)")

    conn.close()
    elapsed = time.time() - t0

    full_df = pd.concat(all_rows, ignore_index=True)

    out_dir = f"{CACHE}/2026_05_06_8m_midsel"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_parquet = f"{out_dir}/phase7_8m_midsel.parquet"
    full_df.to_parquet(out_parquet, index=False)
    print(f"\n[{kst()}] saved {out_parquet} ({len(full_df)} rows)")

    summary = {
        "dataset": "DEEP 8M",
        "table": TABLE,
        "n_rows": 8000000,
        "n_queries": N_QUERIES,
        "seeds": SEEDS,
        "modes": MODES,
        "sel_targets": SEL_TARGETS,
        "elapsed_s": round(elapsed, 1),
        "kst": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "per_cell_stats": [],
    }

    # paired Wilcoxon: system vs bernoulli, stratified vs bernoulli per sel
    rng = np.random.default_rng(42)
    for sel_target in SEL_TARGETS:
        sub = full_df[full_df["sel_target"] == sel_target]
        for mode_a, mode_b in [("system", "bernoulli"), ("stratified", "bernoulli")]:
            seed_diffs = []
            for seed in SEEDS:
                a = sub[(sub["mode"] == mode_a) & (sub["seed"] == seed)][["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qa"})
                b = sub[(sub["mode"] == mode_b) & (sub["seed"] == seed)][["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qb"})
                pair = a.merge(b, on="query_id").dropna()
                if len(pair) > 0:
                    ma, mb = float(np.median(pair["qa"])), float(np.median(pair["qb"]))
                    diff = (mb - ma) / mb * 100 if mb > 0 else 0
                    try:
                        # alternative='less': qa < qb (즉 mode_a 가 더 정확)
                        p = float(sst.wilcoxon(pair["qa"].values, pair["qb"].values,
                                               alternative="less", zero_method="wilcox").pvalue)
                    except Exception:
                        p = float("nan")
                    seed_diffs.append({"seed": seed, "n": len(pair), "med_a": ma, "med_b": mb,
                                      "diff_pct": diff, "p": p})

            diffs = [d["diff_pct"] for d in seed_diffs]
            if diffs:
                boot = [np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(10000)]
                ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
                summary["per_cell_stats"].append({
                    "sel_target": sel_target,
                    "comparison": f"{mode_a} vs {mode_b}",
                    "mean_diff_pct": float(np.mean(diffs)),
                    "bootstrap_95ci": [float(ci_lo), float(ci_hi)],
                    "per_seed": seed_diffs,
                })

    out_meta = f"{out_dir}/phase7_8m_midsel_meta.json"
    with open(out_meta, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"[{kst()}] saved {out_meta}")
    print(f"[{kst()}] total elapsed: {elapsed:.0f}s")

    print(f"\n{'='*72}")
    print(f"{'sel':>5}  {'comparison':<28}  {'mean Δ%':>10}  {'CI lo':>10}  {'CI hi':>10}")
    print(f"{'-'*72}")
    for stat in summary["per_cell_stats"]:
        print(f"{stat['sel_target']:>5}  {stat['comparison']:<28}  {stat['mean_diff_pct']:>+9.3f}%  "
              f"{stat['bootstrap_95ci'][0]:>+9.3f}%  {stat['bootstrap_95ci'][1]:>+9.3f}%")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()
