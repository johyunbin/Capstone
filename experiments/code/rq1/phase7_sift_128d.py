#!/usr/bin/env python3
"""
RQ1 Phase 7-2 — sift 128d 외적 타당성 확장 (BERNOULLI + STRATIFIED KM20)

Pivot C (KM20 stratified) 의 정량 효과가 96d DEEP 뿐 아니라 128d SIFT 에서도
재현되는지 외적 타당성을 확인한다. 원본 `customer_sift_10` 은 HNSW 인덱스
(`c_sift_hnsw` 등) 를 가지고 있어 sampling 경로가 우회될 수 있으므로,
별도 테이블 `customer_sift_10_phase7_noidx_subset` 을 만들어 HNSW 없이 복사.

옵션 B 안전 경로:
  - 원본 ALTER TABLE 하지 않음
  - CREATE TABLE AS SELECT ... FROM customer_sift_10
  - stratum_id 부여 + 인덱스 (단, HNSW 는 생성하지 않음)

query_pool 도 sift 용으로 새로 생성:
  - customer_sift_10 의 100 query 무작위 추출 (seed=42)
  - 각 query 에 대해 s=0.500 의 D_target 을 quantile 계산으로 결정
  - 본 생성 로직은 Phase 1 의 rq1_stage1_dump / rq1_stage3_selectivity 의 직접 파생

측정 범위:
  - selectivity s=0.500 1 구간
  - 100 query × (BERN + STRAT) × 1 seed = 200 측정

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase7_sift_128d.py
  → 결과는 cache/rq1/phase7_sift_<mode>.parquet + phase7_sift_paired.json
  → query_pool_sift.parquet / query_selectivity_sift.parquet 도 cache/rq1/ 에 저장
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
import pyarrow as pa


DEFAULT_LOG_FILE = "/mnt/hdd0/home/capstone2026/log/exqutor-2026-04-15.log"
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
    node = plan
    while True:
        node_type = node.get("Node Type", "")
        if "Scan" in node_type:
            return node
        children = node.get("Plans", [])
        if not children:
            return node
        node = children[0]


# ---- k-means mini-batch (phase6_export_km20_strata.py 에서 inline copy) ----


def build_layer_kmeans(
    vectors: np.ndarray,
    k: int,
    batch_size: int = 4096,
    n_iter: int = 100,
    seed: int = 42,
) -> tuple[np.ndarray, dict]:
    n, dim = vectors.shape
    rng = np.random.default_rng(seed)
    init_idx = rng.choice(n, size=k, replace=False)
    centroids = vectors[init_idx].astype(np.float64).copy()
    counts = np.zeros(k, dtype=np.int64)

    t0 = time.time()
    for it in range(n_iter):
        batch_idx = rng.choice(n, size=batch_size, replace=False)
        batch = vectors[batch_idx].astype(np.float64)
        b_sq = (batch * batch).sum(axis=1)
        c_sq = (centroids * centroids).sum(axis=1)
        dots = batch @ centroids.T
        d2 = b_sq[:, None] + c_sq[None, :] - 2 * dots
        labels = np.argmin(d2, axis=1)
        for kk in range(k):
            mask = labels == kk
            n_k = int(mask.sum())
            if n_k == 0:
                continue
            counts[kk] += n_k
            eta = n_k / counts[kk]
            centroids[kk] = (1 - eta) * centroids[kk] + eta * batch[mask].mean(axis=0)
    t_train = time.time() - t0

    t1 = time.time()
    x_sq = (vectors.astype(np.float32) * vectors.astype(np.float32)).sum(axis=1)
    c_sq32 = (centroids * centroids).sum(axis=1).astype(np.float32)
    dots = vectors.astype(np.float32) @ centroids.T.astype(np.float32)
    d2_full = x_sq[:, None] + c_sq32[None, :] - 2 * dots
    stratum_id = np.argmin(d2_full, axis=1).astype(np.int16)
    t_assign = time.time() - t1

    sizes = np.bincount(stratum_id, minlength=k)
    inertia = float(np.mean(np.min(d2_full, axis=1)))

    info = {
        "layer": f"kmeans_k{k}",
        "n_strata": int(k),
        "size_min": int(sizes.min()),
        "size_max": int(sizes.max()),
        "size_std": float(sizes.std()),
        "inertia_mean": inertia,
        "t_train_s": round(t_train, 2),
        "t_assign_s": round(t_assign, 2),
    }
    return stratum_id, info


# ---- Setup: copy + stratum_id + query pool 생성 ------------------------


def setup_sift_subset(conn, args) -> dict:
    table_name = args.table
    src_table = args.source_table
    log(f"setup: target table={table_name}, source={src_table}")

    with conn.cursor() as cur:
        # 1. Table 존재 확인
        cur.execute("SELECT to_regclass(%s)", (table_name,))
        exists = cur.fetchone()[0] is not None
        if not exists:
            log(f"  [1/6] CREATE TABLE {table_name} AS SELECT FROM {src_table}")
            t0 = time.time()
            # customer_sift_10 의 primary key 컬럼은 c_custkey
            cur.execute(
                f"CREATE TABLE {table_name} AS "
                f"SELECT c_custkey, c_embedding, 0::smallint AS stratum_id "
                f"FROM {src_table}"
            )
            log(f"    done ({time.time() - t0:.1f}s)")
        else:
            log(f"  [1/6] {table_name} 이미 존재 — 재사용")

        cur.execute(f"SELECT count(*) FROM {table_name}")
        n_rows = cur.fetchone()[0]
        log(f"    n_rows = {n_rows}")

    # 2. 128d 벡터 로드
    log("  [2/6] loading 128d embeddings")
    t0 = time.time()
    vecs = np.empty((n_rows, 128), dtype=np.float32)
    pks = np.empty(n_rows, dtype=np.int64)
    i = 0
    with conn.cursor().copy(
        f"COPY (SELECT c_custkey, c_embedding::text FROM {table_name}) TO STDOUT"
    ) as copy:
        for row_bytes in copy:
            line = row_bytes.decode("utf-8", errors="replace").rstrip("\n")
            pk_s, vec_s = line.split("\t", 1)
            pks[i] = int(pk_s)
            vec_s = vec_s.strip().strip("[]")
            vecs[i] = np.fromstring(vec_s, sep=",", dtype=np.float32)
            i += 1
            if i % 200000 == 0:
                log(f"    loaded {i}/{n_rows} ({time.time() - t0:.0f}s)")
    log(f"    done ({time.time() - t0:.1f}s, shape={vecs.shape})")

    # 3. k-means KM20 학습
    log(f"  [3/6] k-means K={args.k} (seed={args.seed}) on 128d")
    stratum_id, info = build_layer_kmeans(
        vecs,
        k=args.k,
        batch_size=args.kmeans_batch,
        n_iter=args.kmeans_iter,
        seed=args.seed,
    )
    log(
        f"    done (sizes [{info['size_min']},{info['size_max']}], "
        f"inertia={info['inertia_mean']:.4f})"
    )

    # 4. stratum_id CSV export + COPY temp + UPDATE
    csv_path = Path(args.cache_dir) / "phase7_sift_strata.csv"
    log(f"  [4/6] dump stratum CSV → {csv_path}")
    with open(csv_path, "w") as f:
        f.write("c_custkey,stratum_id\n")
        for j in range(n_rows):
            f.write(f"{int(pks[j])},{int(stratum_id[j])}\n")
    log(f"    done ({csv_path.stat().st_size / 1e6:.1f} MB)")

    log(f"  [4/6b] UPDATE {table_name}.stratum_id")
    t0 = time.time()
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS _phase7_sift_strata_tmp")
        cur.execute(
            "CREATE UNLOGGED TABLE _phase7_sift_strata_tmp "
            "(c_custkey bigint, stratum_id smallint)"
        )
        with cur.copy(
            "COPY _phase7_sift_strata_tmp (c_custkey, stratum_id) "
            "FROM STDIN WITH (FORMAT csv, HEADER true)"
        ) as copy:
            with open(csv_path, "rb") as f:
                while True:
                    chunk = f.read(1 << 20)
                    if not chunk:
                        break
                    copy.write(chunk)
        cur.execute(
            "CREATE INDEX IF NOT EXISTS _phase7_sift_strata_tmp_pk "
            "ON _phase7_sift_strata_tmp (c_custkey)"
        )
        cur.execute(
            f"UPDATE {table_name} t SET stratum_id = s.stratum_id "
            f"FROM _phase7_sift_strata_tmp s WHERE t.c_custkey = s.c_custkey"
        )
        updated = cur.rowcount
        log(f"    UPDATE done ({time.time() - t0:.1f}s, {updated} rows)")
        cur.execute("DROP TABLE _phase7_sift_strata_tmp")

    # 5. 인덱스 + VACUUM ANALYZE
    log(f"  [5/6] CREATE INDEX + VACUUM ANALYZE")
    with conn.cursor() as cur:
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS idx_phase7_sift_stratum "
            f"ON {table_name} (stratum_id)"
        )
    old_autocommit = conn.autocommit
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"VACUUM ANALYZE {table_name}")
    conn.autocommit = old_autocommit

    # 6. query_pool + query_selectivity 생성
    log("  [6/6] generate query_pool + query_selectivity for sift")
    rng = np.random.default_rng(args.seed)
    query_ids = rng.choice(n_rows, size=args.n_queries, replace=False)
    query_pks = [int(pks[qi]) for qi in query_ids]
    query_embs = [vecs[qi].tolist() for qi in query_ids]
    query_pool_df = pd.DataFrame(
        {
            "query_id": list(range(args.n_queries)),
            "c_custkey": query_pks,
            "embedding": query_embs,
        }
    )
    query_pool_path = Path(args.cache_dir) / "query_pool_sift.parquet"
    query_pool_df.to_parquet(query_pool_path, index=False)
    log(f"    query_pool → {query_pool_path}")

    # 각 query 에 대해 s=0.500 D_target 계산 — 해당 query 와 전체 벡터의 거리의 median
    log("    computing D_target for s=0.500 (median distance per query)")
    t0 = time.time()
    qs_rows = []
    for qi_idx, qi in enumerate(query_ids):
        q = vecs[qi]
        dists = np.linalg.norm(vecs - q, axis=1)
        # s=0.500 → 거리의 median 이 threshold 이도록 quantile 0.5 계산
        D = float(np.quantile(dists, 0.5))
        # true_cardinality 는 실제 개수 (Python 으로 재확인, SQL COUNT 과 일치해야 함)
        true_card = int((dists < D).sum())
        qs_rows.append(
            {
                "query_id": qi_idx,
                "selectivity": 0.5,
                "D_target": D,
                "true_cardinality": true_card,
            }
        )
    log(f"    done ({time.time() - t0:.1f}s)")
    qs_df = pd.DataFrame(qs_rows)
    qs_path = Path(args.cache_dir) / "query_selectivity_sift.parquet"
    qs_df.to_parquet(qs_path, index=False)
    log(f"    query_selectivity → {qs_path}")

    return {
        "kmeans_info": info,
        "n_rows": int(n_rows),
        "query_pool_path": str(query_pool_path),
        "query_selectivity_path": str(qs_path),
    }


# ---- Measure ------------------------------------------------------------


def measure_mode(conn, args, mode: str) -> tuple[pd.DataFrame, dict]:
    qp = pq.read_table(f"{args.cache_dir}/query_pool_sift.parquet").to_pandas()
    qs = pq.read_table(f"{args.cache_dir}/query_selectivity_sift.parquet").to_pandas()
    qs_500 = qs[qs.query_id < args.n_queries].reset_index(drop=True)
    log(f"  filtered to {len(qs_500)} query")

    # 실측 true_cardinality 를 SQL 로 재계산
    log("  [measure 1/3] re-computing true_cardinality via SQL")
    true_cards = {}
    t0 = time.time()
    with conn.cursor() as cur:
        for i, row in qs_500.iterrows():
            qid = int(row["query_id"])
            D = float(row["D_target"])
            emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
            vec_str = emb_to_pgvec(emb)
            cur.execute(
                f"SELECT count(*) FROM {args.table} "
                f"WHERE (c_embedding <-> '{vec_str}'::vector) < {D}"
            )
            true_cards[qid] = int(cur.fetchone()[0])
            if (i + 1) % 20 == 0:
                log(f"    progress {i + 1}/{len(qs_500)} ({time.time() - t0:.1f}s)")
    log(f"    done ({time.time() - t0:.1f}s)")

    log_path = Path(args.log_file)
    log_start_offset = log_path.stat().st_size if log_path.exists() else 0

    log(f"  [measure 2/3] BERN/STRAT measurement, mode={mode}")
    results = []
    t0 = time.time()
    with conn.cursor() as cur:
        cur.execute("SET vector.sample_size = 385")
        cur.execute("SET vector.update_sample_size = off")
        cur.execute("SET vector.sample_update_cycle = 50")
        cur.execute(f"SET vector.sampling_method = '{mode}'")
        if mode == "stratified":
            cur.execute("SET vector.stratum_column = 'stratum_id'")
            cur.execute(f"SET vector.stratum_n = {args.k}")
        cur.execute("TRUNCATE TABLE exqutor_qerror")

        for i, row in qs_500.iterrows():
            qid = int(row["query_id"])
            D = float(row["D_target"])
            true_card = int(true_cards[qid])

            emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
            vec_str = emb_to_pgvec(emb)

            sql = (
                "EXPLAIN (ANALYZE, FORMAT JSON) "
                f"SELECT count(*) FROM {args.table} "
                f"WHERE (c_embedding <-> '{vec_str}'::vector) < {D}"
            )
            try:
                cur.execute(sql)
                plan_root = cur.fetchone()[0][0]["Plan"]
                scan = find_scan_node(plan_root)
                plan_rows = scan.get("Plan Rows")
                qerr = (
                    max(plan_rows / true_card, true_card / plan_rows)
                    if plan_rows and true_card > 0 and plan_rows > 0
                    else None
                )
                results.append(
                    {
                        "query_id": qid,
                        "selectivity": 0.5,
                        "D_target": D,
                        "true_card": true_card,
                        "plan_rows": plan_rows,
                        "q_error": qerr,
                        "error": None,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "query_id": qid,
                        "selectivity": 0.5,
                        "D_target": D,
                        "true_card": true_card,
                        "plan_rows": None,
                        "q_error": None,
                        "error": str(exc)[:300],
                    }
                )
            if (i + 1) % 20 == 0:
                log(f"    progress {i + 1}/{len(qs_500)} ({time.time() - t0:.1f}s)")
    log(f"    measurement done ({time.time() - t0:.1f}s)")

    log("  [measure 3/3] parse hook estimates from log")
    hook_ests = []
    if log_path.exists():
        with open(log_path, "rb") as f:
            f.seek(log_start_offset)
            tail = f.read().decode("utf-8", errors="replace")
        for m in EST_LINE_RE.finditer(tail):
            hook_ests.append(float(m.group(2)))
    for i, r in enumerate(results):
        r["hook_est"] = hook_ests[i] if i < len(hook_ests) else None
        if r["hook_est"] and r["true_card"] > 0:
            he = float(r["hook_est"])
            if he > 0:
                r["q_error_hook"] = max(he / r["true_card"], r["true_card"] / he)
            else:
                r["q_error_hook"] = None
        else:
            r["q_error_hook"] = None
    log(f"    extracted {len(hook_ests)} hook estimates (expected {len(results)})")

    df = pd.DataFrame(results)
    summary = {
        "n_total": len(df),
        "median_q_error": float(df["q_error"].dropna().median()),
        "median_q_error_hook": float(df["q_error_hook"].dropna().median())
        if df["q_error_hook"].notna().any()
        else None,
    }
    return df, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cache-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1"
    )
    ap.add_argument("--source-table", default="customer_sift_10")
    ap.add_argument(
        "--table", default="customer_sift_10_phase7_noidx_subset"
    )
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--kmeans-iter", type=int, default=100)
    ap.add_argument("--kmeans-batch", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--port", type=int, default=55436)
    ap.add_argument("--db", default="wns41559")
    ap.add_argument("--user", default="wns41559")
    ap.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--measure", choices=["bern", "strat", "both"], default=None)
    args = ap.parse_args()

    log(f"Phase 7-2 sift 128d start (setup={args.setup}, measure={args.measure})")

    conn = psycopg.connect(
        host="/tmp",
        port=args.port,
        user=args.user,
        dbname=args.db,
        autocommit=True,
    )

    setup_info = None
    if args.setup:
        setup_info = setup_sift_subset(conn, args)
        with open(Path(args.cache_dir) / "phase7_sift_setup.meta.json", "w") as f:
            json.dump(
                {"kst": kst_now(), "args": vars(args), "setup_info": setup_info},
                f,
                indent=2,
                default=str,
            )

    if args.measure in ("bern", "both"):
        log("== BERN measurement ==")
        df, summary = measure_mode(conn, args, "bernoulli")
        out = Path(args.cache_dir) / "phase7_sift_bern.parquet"
        df.to_parquet(out, index=False)
        with open(out.with_suffix(".meta.json"), "w") as f:
            json.dump(
                {"kst": kst_now(), "summary": summary, "args": vars(args)},
                f,
                indent=2,
                default=str,
            )
        log(f"  saved {out}")

    if args.measure in ("strat", "both"):
        log("== STRAT measurement ==")
        df, summary = measure_mode(conn, args, "stratified")
        out = Path(args.cache_dir) / "phase7_sift_strat.parquet"
        df.to_parquet(out, index=False)
        with open(out.with_suffix(".meta.json"), "w") as f:
            json.dump(
                {"kst": kst_now(), "summary": summary, "args": vars(args)},
                f,
                indent=2,
                default=str,
            )
        log(f"  saved {out}")

    conn.close()

    # paired 분석
    bern_path = Path(args.cache_dir) / "phase7_sift_bern.parquet"
    strat_path = Path(args.cache_dir) / "phase7_sift_strat.parquet"
    if bern_path.exists() and strat_path.exists():
        log("== paired Wilcoxon analysis ==")
        from scipy import stats

        bern = pd.read_parquet(bern_path)
        strat = pd.read_parquet(strat_path)
        merged = bern.merge(
            strat, on=["query_id", "selectivity"], suffixes=("_bern", "_strat")
        )
        mask = merged["q_error_hook_bern"].notna() & merged["q_error_hook_strat"].notna()
        b = merged.loc[mask, "q_error_hook_bern"].values
        s = merged.loc[mask, "q_error_hook_strat"].values
        if len(b) >= 10:
            median_b = float(np.median(b))
            median_s = float(np.median(s))
            diff_pct = ((median_b - median_s) / median_b * 100) if median_b > 0 else 0
            n_better = int((s < b).sum())
            n_worse = int((s > b).sum())
            n_tie = int((s == b).sum())
            try:
                w_stat, p_less = stats.wilcoxon(s, b, alternative="less")
                w_stat = float(w_stat)
                p_less = float(p_less)
            except Exception as exc:
                w_stat, p_less = None, None
                log(f"  wilcoxon failed: {exc}")

            paired = {
                "n_paired": int(len(b)),
                "bern_median": median_b,
                "strat_median": median_s,
                "diff_pct": diff_pct,
                "w_stat": w_stat,
                "p_less": p_less,
                "n_better": n_better,
                "n_worse": n_worse,
                "n_tie": n_tie,
            }
            out_paired = Path(args.cache_dir) / "phase7_sift_paired.json"
            with open(out_paired, "w") as f:
                json.dump({"kst": kst_now(), "rows": [paired]}, f, indent=2)
            log(f"  paired saved → {out_paired}")
            log(
                f"  s=0.500: BERN median={median_b:.4f} STRAT median={median_s:.4f} "
                f"diff={diff_pct:+.2f}% p={p_less} better={n_better} worse={n_worse}"
            )
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
