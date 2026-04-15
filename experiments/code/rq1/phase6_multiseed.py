#!/usr/bin/env python3
"""
Phase 6 Step 4 — Multi-seed 재측정 (s=0.500 집중)

목적: 단일 seed 의 +1.81% (p=4.01e-05) 효과가 noise range 안인지 확인.
5 seed 로 effect size 분포 + bootstrap 95% CI 확보.

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/rq1_phase6_multiseed.py
"""

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

CACHE = "/mnt/hdd0/home/capstone2026/cache/rq1"
LOG_DIR = "/mnt/hdd0/home/capstone2026/log"
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]
TARGET_SEL = 0.500
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


def run_one_mode(cur, qs_sel, qp, method: str, seed: float, log_path: Path) -> pd.DataFrame:
    """한 seed + 한 mode (bern/strat) 로 100 query 측정."""
    cur.execute(f"SELECT setseed({seed})")
    cur.execute("SET vector.sample_size = 385")
    cur.execute("SET vector.update_sample_size = off")
    cur.execute("SET vector.sample_update_cycle = 50")
    cur.execute(f"SET vector.sampling_method = '{method}'")

    # log offset snapshot
    log_offset = log_path.stat().st_size if log_path.exists() else 0

    results = []
    for _, row in qs_sel.iterrows():
        qid = int(row["query_id"])
        D = float(row["D_target"])
        true_card = int(row["true_cardinality"])
        emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        sql = (
            "EXPLAIN (ANALYZE, FORMAT JSON) "
            "SELECT count(*) FROM partsupp_deep_10_subset_1m "
            f"WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}"
        )
        try:
            cur.execute(sql)
            plan_root = cur.fetchone()[0][0]["Plan"]
            scan = find_scan_node(plan_root)
            plan_rows = scan.get("Plan Rows")
            qerr = max(plan_rows / true_card, true_card / plan_rows) if plan_rows and plan_rows > 0 and true_card > 0 else None
            results.append({
                "query_id": qid, "true_card": true_card,
                "plan_rows": plan_rows, "q_error": qerr,
            })
        except Exception as exc:
            results.append({
                "query_id": qid, "true_card": true_card,
                "plan_rows": None, "q_error": None,
            })

    # Parse hook_est from log tail
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
    print(f"[{kst()}] Phase 6 Step 4 multi-seed measurement (s={TARGET_SEL}, {len(SEEDS)} seeds)")

    qp = pq.read_table(f"{CACHE}/query_pool.parquet").to_pandas()
    qs = pq.read_table(f"{CACHE}/query_selectivity.parquet").to_pandas()
    qs_sel = qs[(qs["selectivity"] == TARGET_SEL) & (qs["query_id"] < N_QUERIES)].reset_index(drop=True)
    print(f"[{kst()}] query_pool={len(qp)}, filtered to s={TARGET_SEL}: {len(qs_sel)} queries")

    # Find today's log file
    log_candidates = sorted(Path(LOG_DIR).glob("exqutor-*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else Path(f"{LOG_DIR}/exqutor.log")
    print(f"[{kst()}] log file: {log_path}")

    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)

    all_results = []
    t0 = time.time()

    for seed in SEEDS:
        print(f"\n[{kst()}] === seed={seed} ===")
        ts = time.time()

        # BERN
        bern_df = run_one_mode(conn.cursor(), qs_sel, qp, "bernoulli", seed, log_path)
        print(f"[{kst()}]   BERN done ({time.time()-ts:.1f}s), hook_est valid: {bern_df['q_error_hook'].notna().sum()}/{len(bern_df)}")

        # STRAT
        ts2 = time.time()
        strat_df = run_one_mode(conn.cursor(), qs_sel, qp, "stratified", seed, log_path)
        print(f"[{kst()}]   STRAT done ({time.time()-ts2:.1f}s), hook_est valid: {strat_df['q_error_hook'].notna().sum()}/{len(strat_df)}")

        # Paired analysis (hook_est based)
        pair = bern_df[["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qe_b"}).merge(
            strat_df[["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qe_s"}),
            on="query_id"
        )
        pair = pair.dropna()
        n_valid = len(pair)

        if n_valid > 0:
            try:
                res = sst.wilcoxon(pair["qe_s"].values, pair["qe_b"].values, alternative="less", zero_method="wilcox")
                p = float(res.pvalue)
            except Exception:
                p = float("nan")

            mb = float(np.median(pair["qe_b"]))
            ms = float(np.median(pair["qe_s"]))
            diff_pct = (mb - ms) / mb * 100 if mb > 0 else 0
            n_better = int(np.sum(pair["qe_s"] < pair["qe_b"]))

            result = {
                "seed": seed,
                "n_paired": n_valid,
                "bern_median": mb,
                "strat_median": ms,
                "diff_pct": diff_pct,
                "p_less": p,
                "n_better": n_better,
                "n_total": len(pair),
            }
            all_results.append(result)
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"[{kst()}]   RESULT: BERN {mb:.4f} vs STRAT {ms:.4f}, diff={diff_pct:+.2f}%, p={p:.2e} {sig}, win={n_better}/{n_valid}")
        else:
            print(f"[{kst()}]   WARN: no valid paired data")
            all_results.append({"seed": seed, "n_paired": 0})

        # Save per-seed parquets
        bern_df.to_parquet(f"{CACHE}/phase6_multiseed_bern_s{seed}.parquet", index=False)
        strat_df.to_parquet(f"{CACHE}/phase6_multiseed_strat_s{seed}.parquet", index=False)

    conn.close()
    elapsed = time.time() - t0

    # Aggregate summary
    valid = [r for r in all_results if r.get("n_paired", 0) > 0]
    if valid:
        diffs = [r["diff_pct"] for r in valid]
        ps = [r["p_less"] for r in valid]
        wins = [r["n_better"] for r in valid]

        print(f"\n{'='*60}")
        print(f"AGGREGATE ({len(valid)} seeds, s={TARGET_SEL})")
        print(f"  diff%: mean={np.mean(diffs):+.3f}%, std={np.std(diffs):.3f}%, range=[{min(diffs):+.3f}, {max(diffs):+.3f}]")
        print(f"  p_less: min={min(ps):.2e}, max={max(ps):.2e}")
        print(f"  n_better: mean={np.mean(wins):.1f}, range=[{min(wins)}, {max(wins)}]")

        # Bootstrap 95% CI on diff_pct
        rng = np.random.default_rng(42)
        boot_means = [np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(10000)]
        ci_lo, ci_hi = np.percentile(boot_means, [2.5, 97.5])
        print(f"  bootstrap 95% CI on mean diff%: [{ci_lo:+.3f}%, {ci_hi:+.3f}%]")

    summary = {
        "kst": kst(),
        "target_selectivity": TARGET_SEL,
        "seeds": SEEDS,
        "elapsed_s": round(elapsed, 1),
        "per_seed": all_results,
        "aggregate": {
            "mean_diff_pct": float(np.mean(diffs)) if valid else None,
            "std_diff_pct": float(np.std(diffs)) if valid else None,
            "min_p": float(min(ps)) if valid else None,
            "max_p": float(max(ps)) if valid else None,
            "bootstrap_95ci": [float(ci_lo), float(ci_hi)] if valid else None,
        }
    }
    out = f"{CACHE}/phase6_multiseed_summary.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[{kst()}] saved {out}")
    print(f"[{kst()}] total elapsed: {elapsed:.0f}s")


if __name__ == "__main__":
    main()
