#!/usr/bin/env python3
"""
RQ1 Phase 6 Step 4 — Native sampling 측정 (BERNOULLI vs STRATIFIED)

phase4_native.py 의 직접 파생. vector.sampling_method GUC 를 설정해서
같은 vector.so 빌드에서 두 mode 를 각각 측정한다.

각 query 는 EXPLAIN (ANALYZE, FORMAT JSON) 으로 실행, Plan 트리의 첫
Scan 노드 정보 + Exqutor hook 이 set 한 rel->rows 를 추출한다. Stratified
mode 에서는 Scan 노드가 없고 대신 Aggregate 위에서 rel->rows 를 확인.

Q-error = max(plan_rows / true_card, true_card / plan_rows) 동일 공식.
Phase 4 Python counterfactual 의 estimator 와 native 의 일치성을 직접
검증하는 것이 본 스크립트의 핵심.

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase6_strat_native.py
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

DEFAULT_LOG_FILE = "/mnt/hdd0/home/capstone2026/log/exqutor-2026-04-14.log"
EST_LINE_RE = re.compile(
    r"Estimated cardinality for range query on table (\S+): ([\d.eE+\-]+)"
)


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now()}] {msg}", flush=True)


def emb_to_pgvec(emb) -> str:
    return "[" + ",".join(f"{float(x):.7f}" for x in emb) + "]"


def find_scan_node(plan: dict) -> dict:
    """Plan 트리를 따라 내려가서 첫 번째 Scan 또는 SampleScan 노드 반환.
    Stratified mode 는 TABLESAMPLE 이 아니므로 Plan Rows 가 top-level Aggregate
    의 estimate (Exqutor hook 결과) 로 나타난다."""
    node = plan
    while True:
        node_type = node.get("Node Type", "")
        if "Scan" in node_type:
            return node
        children = node.get("Plans", [])
        if not children:
            return node
        node = children[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    ap.add_argument(
        "--out-name",
        required=True,
        help="결과 파일 prefix, 예: phase6_strat_km20_native, phase6_bernoulli_native",
    )
    ap.add_argument(
        "--sampling-method",
        choices=["bernoulli", "stratified"],
        required=True,
        help="vector.sampling_method GUC 설정",
    )
    ap.add_argument(
        "--n-queries",
        type=int,
        default=100,
        help="첫 N개 query 만 실행",
    )
    ap.add_argument("--port", type=int, default=55436)
    ap.add_argument("--db", default="wns41559")
    ap.add_argument("--user", default="wns41559")
    ap.add_argument(
        "--update-sample-size",
        choices=["on", "off"],
        default="off",
        help="vector.update_sample_size GUC (기본 off, segfault 회피)",
    )
    ap.add_argument(
        "--reset-qerror",
        action="store_true",
        help="측정 전 exqutor_qerror TRUNCATE",
    )
    ap.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help="Exqutor PG log file (GUC log_directory + log_filename 으로 확인 가능)",
    )
    args = ap.parse_args()

    log(
        f"Phase 6 Step 4 native measurement — out={args.out_name}, "
        f"method={args.sampling_method}, n_queries={args.n_queries}"
    )

    qp = pq.read_table(f"{args.in_dir}/query_pool.parquet").to_pandas()
    qs = pq.read_table(f"{args.in_dir}/query_selectivity.parquet").to_pandas()
    qs_filtered = qs[qs.query_id < args.n_queries].reset_index(drop=True)
    log(
        f"loaded query_pool={len(qp)} rows, query_selectivity={len(qs)} rows, "
        f"filtered={len(qs_filtered)} rows"
    )

    conn = psycopg.connect(
        host="/tmp",
        port=args.port,
        user=args.user,
        dbname=args.db,
        autocommit=True,
    )

    results = []
    t0 = time.time()
    qerror_state = []

    # Log file snapshot for post-hoc "Estimated cardinality" extraction.
    log_path = Path(args.log_file)
    log_start_offset = log_path.stat().st_size if log_path.exists() else 0
    log(f"log snapshot offset={log_start_offset} path={log_path}")

    with conn.cursor() as cur:
        cur.execute("SET vector.sample_size = 385")
        cur.execute(f"SET vector.update_sample_size = {args.update_sample_size}")
        cur.execute("SET vector.sample_update_cycle = 50")
        cur.execute(f"SET vector.sampling_method = '{args.sampling_method}'")
        log(
            f"GUC set: sample_size=385, "
            f"update_sample_size={args.update_sample_size}, "
            f"sample_update_cycle=50, sampling_method={args.sampling_method}"
        )

        if args.reset_qerror:
            cur.execute("TRUNCATE TABLE exqutor_qerror")
            log("exqutor_qerror TRUNCATEd")

        for i, row in qs_filtered.iterrows():
            qid = int(row["query_id"])
            sel = float(row["selectivity"])
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
                explain_row = cur.fetchone()[0]
                plan_root = explain_row[0]["Plan"]
                scan = find_scan_node(plan_root)

                plan_rows = scan.get("Plan Rows")
                actual_rows = scan.get("Actual Rows")
                node_type = scan.get("Node Type")
                sampling_method_actual = scan.get("Sampling Method")
                sample_params = scan.get("Sampling Parameters")

                if true_card > 0 and plan_rows and plan_rows > 0:
                    qerr = max(plan_rows / true_card, true_card / plan_rows)
                else:
                    qerr = None

                results.append(
                    {
                        "query_id": qid,
                        "selectivity": sel,
                        "D_target": D,
                        "true_card": true_card,
                        "plan_rows": plan_rows,
                        "actual_rows": actual_rows,
                        "node_type": node_type,
                        "sampling_method": sampling_method_actual,
                        "sample_params": json.dumps(sample_params)
                        if sample_params is not None
                        else None,
                        "q_error": qerr,
                        "error": None,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "query_id": qid,
                        "selectivity": sel,
                        "D_target": D,
                        "true_card": true_card,
                        "plan_rows": None,
                        "actual_rows": None,
                        "node_type": None,
                        "sampling_method": None,
                        "sample_params": None,
                        "q_error": None,
                        "error": str(exc)[:300],
                    }
                )

            if (i + 1) % 20 == 0:
                elapsed = time.time() - t0
                log(f"  progress {i + 1}/{len(qs_filtered)} ({elapsed:.1f}s)")

        try:
            cur.execute(
                "SELECT table_name, column_name, sample_size, "
                "qerror_count, learning_rate FROM exqutor_qerror"
            )
            qerror_state = [tuple(r) for r in cur.fetchall()]
        except Exception as exc:
            log(f"warn: exqutor_qerror SELECT failed: {exc}")
            qerror_state = []

    conn.close()

    # Parse log tail to extract hook's "Estimated cardinality" values.
    # These are the authoritative hook-return values regardless of sampling_method.
    hook_ests: list[float] = []
    if log_path.exists():
        with open(log_path, "rb") as f:
            f.seek(log_start_offset)
            tail = f.read().decode("utf-8", errors="replace")
        for m in EST_LINE_RE.finditer(tail):
            hook_ests.append(float(m.group(2)))
        log(
            f"log tail: extracted {len(hook_ests)} hook estimates "
            f"(expected {len(results)})"
        )
    else:
        log(f"warn: log file {log_path} not found, hook_est column will be empty")

    # Align hook_ests with results by order (SPI runs sequentially, 1-to-1).
    for i, r in enumerate(results):
        r["hook_est"] = hook_ests[i] if i < len(hook_ests) else None
        if r["hook_est"] is not None and r["true_card"] > 0:
            he = float(r["hook_est"])
            if he > 0:
                r["q_error_hook"] = max(he / r["true_card"], r["true_card"] / he)
            else:
                r["q_error_hook"] = None
        else:
            r["q_error_hook"] = None

    df = pd.DataFrame(results)
    out_parquet = f"{args.in_dir}/{args.out_name}.parquet"
    df.to_parquet(out_parquet, index=False)
    log(f"saved {out_parquet} ({len(df)} rows)")

    n_valid = int(df["q_error"].notna().sum())
    n_valid_hook = int(df["q_error_hook"].notna().sum())
    summary = {
        "n_total": len(df),
        "n_valid_q_error": n_valid,
        "n_valid_q_error_hook": n_valid_hook,
        "n_errors": int(df["error"].notna().sum()),
    }
    if n_valid > 0:
        valid_df = df[df["q_error"].notna()]
        summary.update(
            {
                "median_q_error": float(valid_df["q_error"].median()),
                "p95_q_error": float(valid_df["q_error"].quantile(0.95)),
                "max_q_error": float(valid_df["q_error"].max()),
                "median_by_selectivity": {
                    f"{k:.3f}": float(v)
                    for k, v in valid_df.groupby("selectivity")["q_error"]
                    .median()
                    .items()
                },
            }
        )
    if n_valid_hook > 0:
        valid_hook = df[df["q_error_hook"].notna()]
        summary["median_q_error_hook"] = float(valid_hook["q_error_hook"].median())
        summary["median_by_selectivity_hook"] = {
            f"{k:.3f}": float(v)
            for k, v in valid_hook.groupby("selectivity")["q_error_hook"]
            .median()
            .items()
        }

    sampling_method_set = sorted(
        s for s in df["sampling_method"].dropna().unique()
    )
    node_type_set = sorted(s for s in df["node_type"].dropna().unique())

    meta = {
        "kst": kst_now(),
        "args": vars(args),
        "elapsed_s": round(time.time() - t0, 2),
        "exqutor_qerror_final": [
            list(map(str, r)) for r in qerror_state
        ],
        "sampling_method_set": sampling_method_set,
        "node_type_set": node_type_set,
        "summary": summary,
    }
    out_meta = f"{args.in_dir}/{args.out_name}_meta.json"
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    log(f"saved {out_meta}")
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
