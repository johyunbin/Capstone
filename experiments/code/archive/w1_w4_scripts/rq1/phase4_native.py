#!/usr/bin/env python3
"""
RQ1 Phase 4 — Native sampling 측정 (SYSTEM vs BERNOULLI)

서버 vector.so의 현재 빌드가 어느 모드인지에 따라 동일 스크립트로 두 번 실행한다.
첫 번째 실행은 SYSTEM 모드 (vector.c L889 원본 그대로), 두 번째 실행은
BERNOULLI 모드 (L889 한 줄 교체 + 재빌드 후). 결과 parquet은 별도 이름으로 저장한다.

각 query 는 EXPLAIN (ANALYZE, FORMAT JSON) 으로 실행하며,
Plan 트리 첫 번째 Scan 노드의 Plan Rows + Actual Rows + Sampling Method 를 추출한다.

Q-error 계산: max(plan_rows / true_card, true_card / plan_rows)
- true_card 는 query_selectivity.parquet 의 ground truth (1M subset 정확 카운트)
- plan_rows 는 Exqutor hook 이 set 한 추정값
- actual_rows 는 sample 안 부분 카운트 (참고용; plan replacement 부작용으로 격하됨)

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase4_native.py
  → 결과는 cache/rq1/phase4_<mode>.parquet + cache/rq1/phase4_<mode>_meta.json
"""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import psycopg
import pyarrow.parquet as pq


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now()}] {msg}", flush=True)


def emb_to_pgvec(emb) -> str:
    return "[" + ",".join(f"{float(x):.7f}" for x in emb) + "]"


def find_scan_node(plan: dict) -> dict:
    """Plan 트리를 따라 내려가서 첫 번째 Scan 노드 (Sample/Seq/Index) 를 반환."""
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
        help="결과 파일 prefix, 예: phase4_system, phase4_bernoulli",
    )
    ap.add_argument(
        "--n-queries",
        type=int,
        default=100,
        help="첫 N개 query 만 실행 (sanity check 용으로 1 가능)",
    )
    ap.add_argument("--port", type=int, default=55436)
    ap.add_argument("--db", default="wns41559")
    ap.add_argument("--user", default="wns41559")
    ap.add_argument(
        "--reset-qerror",
        action="store_true",
        help="측정 전 exqutor_qerror TRUNCATE",
    )
    ap.add_argument(
        "--update-sample-size",
        choices=["on", "off"],
        default="off",
        help=(
            "vector.update_sample_size GUC. 기본값 off는 sample_size=385 고정으로 "
            "Adaptive update path 우회 (segfault 회피, 19:32 KST 발견)"
        ),
    )
    args = ap.parse_args()

    log(
        f"Phase 4 native measurement start — out={args.out_name}, "
        f"n_queries={args.n_queries}, port={args.port}"
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

    with conn.cursor() as cur:
        cur.execute("SET vector.sample_size = 385")
        cur.execute(f"SET vector.update_sample_size = {args.update_sample_size}")
        cur.execute("SET vector.sample_update_cycle = 50")
        log(
            f"GUC set: sample_size=385, "
            f"update_sample_size={args.update_sample_size}, "
            f"sample_update_cycle=50"
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
                sampling_method = scan.get("Sampling Method")
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
                        "sampling_method": sampling_method,
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

    df = pd.DataFrame(results)
    out_parquet = f"{args.in_dir}/{args.out_name}.parquet"
    df.to_parquet(out_parquet, index=False)
    log(f"saved {out_parquet} ({len(df)} rows)")

    n_valid = int(df["q_error"].notna().sum())
    summary = {
        "n_total": len(df),
        "n_valid_q_error": n_valid,
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
