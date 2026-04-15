#!/usr/bin/env python3
"""
실험 B — RANDOM20 Control Experiment

"쏠림이 원인임을 증명" 하는 핵심 대조 실험.

논리:
  KM20 stratified vs BERN:    +1.64% (p=4.01e-05) → 개선 있음
  RANDOM20 stratified vs BERN: ≈ 0% (예상)        → 개선 없음
  ────────────────────────────────────────────────────────────
  → 차이의 원인 = KM20이 공간 구조(쏠림)를 반영하기 때문

방법:
  1. stratum_id (KM20) 를 km20_stratum_id 에 백업
  2. stratum_id 를 floor(random() * 20) 으로 교체 (균일 무작위 20-partition)
  3. 동일 100 query × 6 selectivity 측정 (stratified mode)
  4. stratum_id 복원

서버 사용 위치: /mnt/hdd0/home/capstone2026/cache/rq1_random20_control.py
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
PORT = 55436
DB = "wns41559"
USER = "wns41559"
TABLE = "partsupp_deep_10_subset_1m"
N_QUERIES = 100
RANDOM_SEED_SQL = 0.42  # setseed() for reproducible random partition
SEEDS = [0.1, 0.2, 0.3, 0.4, 0.5]  # measurement seeds (same as multi-seed)
TARGET_SEL = 0.500  # primary selectivity for multi-seed analysis

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


def setup_random_partition(conn) -> dict:
    """KM20 → RANDOM20 교체. 백업 + 교체 + 검증."""
    print(f"[{kst()}] === RANDOM20 PARTITION SETUP ===")
    with conn.cursor() as cur:
        # 1. 백업 컬럼 추가
        cur.execute(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = '{TABLE}' AND column_name = 'km20_stratum_id'
            ) THEN
                ALTER TABLE {TABLE} ADD COLUMN km20_stratum_id integer;
            END IF;
        END $$
        """)
        print(f"[{kst()}] km20_stratum_id column ensured")

        # 2. KM20 백업
        cur.execute(f"UPDATE {TABLE} SET km20_stratum_id = stratum_id")
        print(f"[{kst()}] KM20 backed up to km20_stratum_id")

        # 3. KM20 분포 기록 (검증용)
        cur.execute(f"SELECT stratum_id, count(*) FROM {TABLE} GROUP BY stratum_id ORDER BY stratum_id")
        km20_dist = {row[0]: row[1] for row in cur.fetchall()}
        km20_gini = gini_coefficient(list(km20_dist.values()))
        print(f"[{kst()}] KM20 distribution: {len(km20_dist)} strata, "
              f"min={min(km20_dist.values())}, max={max(km20_dist.values())}, "
              f"ratio={max(km20_dist.values())/min(km20_dist.values()):.1f}x, Gini={km20_gini:.4f}")

        # 4. RANDOM20 교체
        cur.execute(f"SELECT setseed({RANDOM_SEED_SQL})")
        cur.execute(f"UPDATE {TABLE} SET stratum_id = floor(random() * 20)::integer")
        print(f"[{kst()}] stratum_id replaced with RANDOM20 (setseed={RANDOM_SEED_SQL})")

        # 5. RANDOM20 분포 검증 — 거의 균일해야 함
        cur.execute(f"SELECT stratum_id, count(*) FROM {TABLE} GROUP BY stratum_id ORDER BY stratum_id")
        rand_dist = {row[0]: row[1] for row in cur.fetchall()}
        rand_gini = gini_coefficient(list(rand_dist.values()))
        print(f"[{kst()}] RANDOM20 distribution: {len(rand_dist)} strata, "
              f"min={min(rand_dist.values())}, max={max(rand_dist.values())}, "
              f"ratio={max(rand_dist.values())/min(rand_dist.values()):.2f}x, Gini={rand_gini:.4f}")

        # 6. ANALYZE for planner stats
        cur.execute(f"ANALYZE {TABLE}")
        print(f"[{kst()}] ANALYZE complete")

    return {"km20_dist": km20_dist, "km20_gini": km20_gini,
            "rand_dist": rand_dist, "rand_gini": rand_gini}


def restore_km20_partition(conn):
    """RANDOM20 → KM20 복원."""
    print(f"\n[{kst()}] === RESTORING KM20 PARTITION ===")
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {TABLE} SET stratum_id = km20_stratum_id")
        print(f"[{kst()}] stratum_id restored from km20_stratum_id")

        # 검증
        cur.execute(f"SELECT stratum_id, count(*) FROM {TABLE} GROUP BY stratum_id ORDER BY stratum_id")
        restored = {row[0]: row[1] for row in cur.fetchall()}
        print(f"[{kst()}] Restored: {len(restored)} strata, "
              f"min={min(restored.values())}, max={max(restored.values())}")

        cur.execute(f"ALTER TABLE {TABLE} DROP COLUMN km20_stratum_id")
        print(f"[{kst()}] km20_stratum_id column dropped")

        cur.execute(f"ANALYZE {TABLE}")
        print(f"[{kst()}] ANALYZE complete")


def gini_coefficient(values: list) -> float:
    arr = np.array(sorted(values), dtype=float)
    n = len(arr)
    if n == 0 or arr.sum() == 0:
        return 0.0
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * arr) - (n + 1) * np.sum(arr)) / (n * np.sum(arr)))


def run_one_mode(cur, qs_sub, qp, method: str, seed: float, log_path: Path) -> pd.DataFrame:
    """한 seed + 한 mode (bern/strat) 로 query 측정."""
    cur.execute(f"SELECT setseed({seed})")
    cur.execute("SET vector.sample_size = 385")
    cur.execute("SET vector.update_sample_size = off")
    cur.execute("SET vector.sample_update_cycle = 50")
    cur.execute(f"SET vector.sampling_method = '{method}'")

    log_offset = log_path.stat().st_size if log_path.exists() else 0

    results = []
    for _, row in qs_sub.iterrows():
        qid = int(row["query_id"])
        sel = float(row["selectivity"])
        D = float(row["D_target"])
        true_card = int(row["true_cardinality"])
        emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
        vec_str = emb_to_pgvec(emb)

        sql = (
            "EXPLAIN (ANALYZE, FORMAT JSON) "
            f"SELECT count(*) FROM {TABLE} "
            f"WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}"
        )
        try:
            cur.execute(sql)
            plan_root = cur.fetchone()[0][0]["Plan"]
            scan = find_scan_node(plan_root)
            plan_rows = scan.get("Plan Rows")
            qerr = max(plan_rows / true_card, true_card / plan_rows) if plan_rows and plan_rows > 0 and true_card > 0 else None
            results.append({
                "query_id": qid, "selectivity": sel,
                "D_target": D, "true_card": true_card,
                "plan_rows": plan_rows, "q_error": qerr,
            })
        except Exception as exc:
            results.append({
                "query_id": qid, "selectivity": sel,
                "D_target": D, "true_card": true_card,
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
        tc = df.loc[i, "true_card"]
        if he and he > 0 and tc > 0:
            df.loc[i, "q_error_hook"] = max(he / tc, tc / he)
        else:
            df.loc[i, "q_error_hook"] = None
    return df


def paired_analysis(bern_df: pd.DataFrame, strat_df: pd.DataFrame, label: str) -> list:
    """BERN vs STRAT paired Wilcoxon, selectivity별."""
    bern2 = bern_df[["query_id", "selectivity", "q_error_hook"]].rename(columns={"q_error_hook": "qe_b"})
    strat2 = strat_df[["query_id", "selectivity", "q_error_hook"]].rename(columns={"q_error_hook": "qe_s"})
    pair = bern2.merge(strat2, on=["query_id", "selectivity"]).dropna()

    print(f"\n{'='*60}")
    print(f"PAIRED ANALYSIS: {label} ({len(pair)} pairs)")
    print(f"{'='*60}")
    header = f"{'sel':>7s}  {'bern_med':>10s}  {'strat_med':>10s}  {'diff%':>7s}  {'p(less)':>10s}  {'better':>6s}  sig"
    print(header)

    rows = []
    for sel in sorted(pair["selectivity"].unique()):
        sub = pair[pair["selectivity"] == sel]
        x = sub["qe_s"].values
        y = sub["qe_b"].values
        try:
            res = sst.wilcoxon(x, y, alternative="less", zero_method="wilcox")
            p = float(res.pvalue)
        except Exception:
            p = float("nan")
        mb = float(np.median(y))
        ms = float(np.median(x))
        diff = (mb - ms) / mb * 100 if mb > 0 else 0
        nb = int(np.sum(x < y))
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        rows.append({
            "selectivity": sel, "bern_median": mb, "strat_median": ms,
            "diff_pct": diff, "p_less": p, "n_better": nb, "n_total": len(sub),
        })
        print(f"{sel:>7.3f}  {mb:>10.4f}  {ms:>10.4f}  {diff:>+7.2f}  {p:>10.4g}  {nb:>6d}  {sig}")

    return rows


def main():
    print(f"[{kst()}] ========================================")
    print(f"[{kst()}] RANDOM20 Control Experiment")
    print(f"[{kst()}] ========================================")

    # Load query data
    qp = pq.read_table(f"{CACHE}/query_pool.parquet").to_pandas()
    qs = pq.read_table(f"{CACHE}/query_selectivity.parquet").to_pandas()
    qs_all = qs[qs.query_id < N_QUERIES].reset_index(drop=True)
    print(f"[{kst()}] query_pool={len(qp)}, filtered={len(qs_all)} (100 queries × {len(qs_all)//N_QUERIES} sel)")

    # Load existing BERN data for paired comparison
    bern_existing = pq.read_table(f"{CACHE}/phase6_bern_native_v2.parquet").to_pandas()
    print(f"[{kst()}] Existing BERN data: {len(bern_existing)} rows")

    # Find log file
    log_candidates = sorted(Path(LOG_DIR).glob("exqutor-*.log"), reverse=True)
    log_path = log_candidates[0] if log_candidates else Path(f"{LOG_DIR}/exqutor.log")
    print(f"[{kst()}] log file: {log_path}")

    conn = psycopg.connect(host="/tmp", port=PORT, user=USER, dbname=DB, autocommit=True)
    t0 = time.time()

    # === PHASE 1: Setup RANDOM20 partition ===
    dist_info = setup_random_partition(conn)

    # === PHASE 2: Measure RANDOM20 stratified (all selectivities, seed 0.1) ===
    print(f"\n[{kst()}] === PHASE 2: RANDOM20 STRAT measurement (all sel, seed=0.1) ===")
    ts = time.time()
    rand_strat_df = run_one_mode(conn.cursor(), qs_all, qp, "stratified", 0.1, log_path)
    rand_strat_df.to_parquet(f"{CACHE}/random20_strat_all_sel.parquet", index=False)
    n_hook = rand_strat_df["q_error_hook"].notna().sum()
    print(f"[{kst()}] RANDOM20 STRAT done ({time.time()-ts:.0f}s), hook_est valid: {n_hook}/{len(rand_strat_df)}")

    # Also measure RANDOM20 BERN for completeness (same random partition)
    print(f"\n[{kst()}] === PHASE 2b: RANDOM20 BERN measurement (all sel, seed=0.1) ===")
    ts = time.time()
    rand_bern_df = run_one_mode(conn.cursor(), qs_all, qp, "bernoulli", 0.1, log_path)
    rand_bern_df.to_parquet(f"{CACHE}/random20_bern_all_sel.parquet", index=False)
    n_hook_b = rand_bern_df["q_error_hook"].notna().sum()
    print(f"[{kst()}] RANDOM20 BERN done ({time.time()-ts:.0f}s), hook_est valid: {n_hook_b}/{len(rand_bern_df)}")

    # === PHASE 3: Multi-seed for s=0.500 (RANDOM20 strat only) ===
    print(f"\n[{kst()}] === PHASE 3: RANDOM20 STRAT multi-seed (s={TARGET_SEL}) ===")
    qs_sel = qs_all[qs_all["selectivity"] == TARGET_SEL].reset_index(drop=True)
    seed_results = []

    for seed in SEEDS:
        ts = time.time()
        strat_s = run_one_mode(conn.cursor(), qs_sel, qp, "stratified", seed, log_path)
        bern_s = run_one_mode(conn.cursor(), qs_sel, qp, "bernoulli", seed, log_path)

        # Paired
        pair = bern_s[["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qe_b"}).merge(
            strat_s[["query_id", "q_error_hook"]].rename(columns={"q_error_hook": "qe_s"}),
            on="query_id"
        ).dropna()

        if len(pair) > 0:
            try:
                res = sst.wilcoxon(pair["qe_s"].values, pair["qe_b"].values, alternative="less", zero_method="wilcox")
                p = float(res.pvalue)
            except Exception:
                p = float("nan")
            mb = float(np.median(pair["qe_b"]))
            ms = float(np.median(pair["qe_s"]))
            diff = (mb - ms) / mb * 100 if mb > 0 else 0
            nb = int(np.sum(pair["qe_s"] < pair["qe_b"]))
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            seed_results.append({
                "seed": seed, "n_paired": len(pair),
                "bern_median": mb, "strat_median": ms,
                "diff_pct": diff, "p_less": p, "n_better": nb,
            })
            print(f"[{kst()}] seed={seed}: BERN {mb:.4f} vs STRAT {ms:.4f}, diff={diff:+.2f}%, p={p:.2e} {sig}, win={nb}/{len(pair)} ({time.time()-ts:.0f}s)")
        else:
            seed_results.append({"seed": seed, "n_paired": 0})
            print(f"[{kst()}] seed={seed}: no valid pairs ({time.time()-ts:.0f}s)")

    # === PHASE 4: Restore KM20 ===
    restore_km20_partition(conn)
    conn.close()
    elapsed = time.time() - t0

    # === PHASE 5: Analysis ===

    # 5a. All-selectivity paired: RANDOM20 strat vs RANDOM20 bern
    print(f"\n{'#'*60}")
    print(f"# ANALYSIS")
    print(f"{'#'*60}")
    rand_paired = paired_analysis(rand_bern_df, rand_strat_df, "RANDOM20: STRAT vs BERN")

    # 5b. Cross-comparison: RANDOM20 strat vs existing KM20 BERN
    # (This answers: does RANDOM20 stratified improve over BERN at all?)
    paired_analysis(bern_existing, rand_strat_df, "RANDOM20 STRAT vs KM20-era BERN")

    # 5c. Multi-seed aggregate
    valid = [r for r in seed_results if r.get("n_paired", 0) > 0]
    if valid:
        diffs = [r["diff_pct"] for r in valid]
        ps = [r["p_less"] for r in valid]
        rng = np.random.default_rng(42)
        boot = [np.mean(rng.choice(diffs, size=len(diffs), replace=True)) for _ in range(10000)]
        ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
        print(f"\n{'='*60}")
        print(f"RANDOM20 MULTI-SEED AGGREGATE (s={TARGET_SEL}, {len(valid)} seeds)")
        print(f"  diff%: mean={np.mean(diffs):+.3f}%, std={np.std(diffs):.3f}%, range=[{min(diffs):+.3f}, {max(diffs):+.3f}]")
        print(f"  bootstrap 95% CI: [{ci_lo:+.3f}%, {ci_hi:+.3f}%]")
        print(f"  p_less: min={min(ps):.2e}, max={max(ps):.2e}")

        # KM20 comparison (from known results)
        print(f"\n--- COMPARISON ---")
        print(f"  KM20 stratified (5-seed):  +1.64% CI [1.25, 2.02]  ← 공간 구조 반영")
        print(f"  RANDOM20 stratified:       {np.mean(diffs):+.2f}% CI [{ci_lo:+.2f}, {ci_hi:+.2f}]  ← 공간 구조 무시")
        if ci_hi < 0.5:
            print(f"  ★ RANDOM20 CI 상한이 0.5% 미만 → KM20 개선은 '쏠림' 때문임을 강력히 지지")
        elif ci_lo > 0:
            print(f"  ⚠ RANDOM20에서도 유의한 개선 → 다른 요인이 존재할 수 있음")
        else:
            print(f"  ○ RANDOM20 CI가 0을 포함 → 개선 없음 (예상대로)")

    # === Save summary ===
    summary = {
        "kst": kst(),
        "elapsed_s": round(elapsed, 1),
        "design": {
            "purpose": "쏠림이 원인임을 증명하는 대조 실험",
            "km20_gini": dist_info["km20_gini"],
            "rand_gini": dist_info["rand_gini"],
            "random_seed_sql": RANDOM_SEED_SQL,
        },
        "all_selectivity_paired": rand_paired,
        "multiseed_s500": {
            "per_seed": seed_results,
            "aggregate": {
                "mean_diff_pct": float(np.mean(diffs)) if valid else None,
                "std_diff_pct": float(np.std(diffs)) if valid else None,
                "bootstrap_95ci": [float(ci_lo), float(ci_hi)] if valid else None,
            } if valid else None,
        },
        "km20_reference": {
            "mean_diff_pct": 1.64,
            "bootstrap_95ci": [1.25, 2.02],
            "source": "phase6_multiseed_summary.json",
        },
    }
    out = f"{CACHE}/random20_control_summary.json"
    with open(out, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[{kst()}] saved {out}")
    print(f"[{kst()}] total elapsed: {elapsed:.0f}s")


if __name__ == "__main__":
    main()
