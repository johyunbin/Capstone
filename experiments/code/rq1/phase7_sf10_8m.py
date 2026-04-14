#!/usr/bin/env python3
"""
RQ1 Phase 7-1 — sf10 8M native 재현 (BERNOULLI + STRATIFIED KM20)

Phase 6 Step 4 의 1M subset 결과가 8M 원본에서 재현되는지 확인하는 내적
타당도 강화 실험. 원본 `partsupp_deep_10` 은 보존하고, 별도 테이블
`partsupp_deep_10_phase7_8m_subset` 을 COPY 후 KM20 stratum_id 부여.

옵션 B 안전 경로:
  - 원본 ALTER TABLE 하지 않음
  - `CREATE TABLE ... AS SELECT ... FROM partsupp_deep_10` 로 복사
  - 복사본에만 stratum_id INT2 컬럼 + 인덱스 추가
  - HNSW 인덱스는 복사본에 생성하지 않음 (sampling 경로 강제)

측정 범위:
  - selectivity s=0.500 1 구간
  - 100 query × 1 seed × (BERN + STRAT) 2 mode = 200 측정

실행 경로:
  1) --setup : 복사 + k-means + UPDATE + index + VACUUM ANALYZE
  2) --measure bern : BERN 측정 (selectivity 0.500 만)
  3) --measure strat : STRAT 측정 (selectivity 0.500 만)

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase7_sf10_8m.py
  → 결과는 cache/rq1/phase7_8m_<mode>.parquet + phase7_8m_<mode>_meta.json
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
        "batch_size": int(batch_size),
        "n_iter": int(n_iter),
        "seed": int(seed),
        "t_train_s": round(t_train, 2),
        "t_assign_s": round(t_assign, 2),
        "size_min": int(sizes.min()),
        "size_max": int(sizes.max()),
        "size_std": float(sizes.std()),
        "inertia_mean": inertia,
    }
    return stratum_id, info


# ---- Setup: copy + k-means + UPDATE + index -----------------------------


def setup_8m_subset(conn, args) -> dict:
    """원본 partsupp_deep_10 → partsupp_deep_10_phase7_8m_subset COPY 후
    KM20 stratum_id UPDATE + 인덱스 + VACUUM ANALYZE.

    이미 존재하면 stratum_id UPDATE 단계부터 재개.
    """
    table_name = args.table
    log(f"setup: target table={table_name}")

    with conn.cursor() as cur:
        # 1. Table 존재 확인
        cur.execute(
            "SELECT to_regclass(%s)",
            (table_name,),
        )
        exists = cur.fetchone()[0] is not None
        if not exists:
            log(f"  [1/5] CREATE TABLE {table_name} AS SELECT FROM partsupp_deep_10")
            t0 = time.time()
            cur.execute(
                f"CREATE TABLE {table_name} AS "
                "SELECT ps_partkey, ps_suppkey, ps_embedding, "
                "0::smallint AS stratum_id "
                "FROM partsupp_deep_10"
            )
            log(f"    done ({time.time() - t0:.1f}s)")
        else:
            log(f"  [1/5] {table_name} 이미 존재 — 재사용")

        cur.execute(f"SELECT count(*) FROM {table_name}")
        n_rows = cur.fetchone()[0]
        log(f"    n_rows = {n_rows}")

    # 2. k-means 학습 (서버에서 8M × 96d float32 로드)
    # NOTE: 8M × 96 × 4 byte = 3.07 GB. 서버 64 GB RAM 충분.
    log("  [2/5] loading 8M embeddings via COPY TO stdout + numpy")
    t0 = time.time()
    vecs = np.empty((n_rows, 96), dtype=np.float32)
    pks = np.empty(n_rows, dtype=np.int64)
    i = 0
    with conn.cursor().copy(
        f"COPY (SELECT ps_partkey, ps_embedding::text FROM {table_name}) TO STDOUT"
    ) as copy:
        for row_bytes in copy:
            # bytes row 는 \t 구분, newline 으로 cut
            line = row_bytes.decode("utf-8", errors="replace").rstrip("\n")
            pk_s, vec_s = line.split("\t", 1)
            pks[i] = int(pk_s)
            # vec_s 는 "[0.1,0.2,...,0.96]" 형태
            vec_s = vec_s.strip().strip("[]")
            vecs[i] = np.fromstring(vec_s, sep=",", dtype=np.float32)
            i += 1
            if i % 500000 == 0:
                log(f"    loaded {i}/{n_rows} ({time.time() - t0:.0f}s)")
    log(f"    done ({time.time() - t0:.1f}s, shape={vecs.shape})")

    log(f"  [3/5] k-means K={args.k} (seed={args.seed}, iter={args.kmeans_iter})")
    t0 = time.time()
    stratum_id, info = build_layer_kmeans(
        vecs,
        k=args.k,
        batch_size=args.kmeans_batch,
        n_iter=args.kmeans_iter,
        seed=args.seed,
    )
    log(
        f"    done ({time.time() - t0:.1f}s, "
        f"sizes [{info['size_min']},{info['size_max']}], inertia={info['inertia_mean']:.4f})"
    )

    # 3. stratum_id 를 CSV 로 export + COPY FROM temp + UPDATE
    csv_path = Path(args.cache_dir) / "phase7_8m_strata.csv"
    log(f"  [4/5] dump stratum CSV → {csv_path}")
    t0 = time.time()
    with open(csv_path, "w") as f:
        f.write("ps_partkey,stratum_id\n")
        for j in range(n_rows):
            f.write(f"{int(pks[j])},{int(stratum_id[j])}\n")
    log(f"    done ({time.time() - t0:.1f}s, {csv_path.stat().st_size / 1e6:.1f} MB)")

    # temp table COPY 후 UPDATE join
    log(f"  [4/5b] UPDATE {table_name}.stratum_id from CSV")
    t0 = time.time()
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS _phase7_strata_tmp")
        cur.execute(
            "CREATE UNLOGGED TABLE _phase7_strata_tmp "
            "(ps_partkey bigint, stratum_id smallint)"
        )
        with cur.copy(
            "COPY _phase7_strata_tmp (ps_partkey, stratum_id) "
            "FROM STDIN WITH (FORMAT csv, HEADER true)"
        ) as copy:
            with open(csv_path, "rb") as f:
                while True:
                    chunk = f.read(1 << 20)
                    if not chunk:
                        break
                    copy.write(chunk)
        log(f"    COPY temp done ({time.time() - t0:.1f}s)")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS _phase7_strata_tmp_pk "
            "ON _phase7_strata_tmp (ps_partkey)"
        )
        t1 = time.time()
        cur.execute(
            f"UPDATE {table_name} t SET stratum_id = s.stratum_id "
            "FROM _phase7_strata_tmp s WHERE t.ps_partkey = s.ps_partkey"
        )
        updated = cur.rowcount
        log(f"    UPDATE done ({time.time() - t1:.1f}s, {updated} rows)")
        cur.execute("DROP TABLE _phase7_strata_tmp")

        # 4. 인덱스 + VACUUM ANALYZE
        log(f"  [5/5] CREATE INDEX + VACUUM ANALYZE {table_name}")
        t1 = time.time()
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS idx_phase7_8m_stratum "
            f"ON {table_name} (stratum_id)"
        )
        # VACUUM ANALYZE 는 autocommit 필요
    conn.commit() if not conn.autocommit else None
    with conn.cursor() as cur:
        old_autocommit = conn.autocommit
        conn.autocommit = True
        cur.execute(f"VACUUM ANALYZE {table_name}")
        conn.autocommit = old_autocommit
    log(f"    done ({time.time() - t1:.1f}s)")

    return {
        "kmeans_info": info,
        "n_rows": int(n_rows),
        "csv_path": str(csv_path),
    }


# ---- Measure: BERN or STRAT × 100 query × s=0.500 -----------------------


def measure_mode(conn, args, mode: str, setup_info: dict) -> tuple[pd.DataFrame, dict]:
    """BERN 또는 STRAT 모드로 100 query × s=0.500 측정.

    기존 Phase 6 의 1M subset 에서 결정된 D_target 을 재사용한다 — 8M 원본에
    대해 distance threshold 가 같은 선택도를 유지하는지 확인 필요. 본 스크립트는
    query_selectivity.parquet 의 s=0.500 D_target 을 그대로 사용 (1M 과 8M 이
    같은 데이터 분포에서 추출되었으므로 분포 차이는 미미할 것으로 예상).

    8M 의 true_cardinality 는 full scan 으로 재계산해야 한다. 이 재계산은
    본 스크립트 내부에서 s=0.500 1 구간 × 100 query 만 수행 (예상 ~5분).
    """
    qp = pq.read_table(f"{args.cache_dir}/query_pool.parquet").to_pandas()
    qs = pq.read_table(f"{args.cache_dir}/query_selectivity.parquet").to_pandas()
    qs_500 = qs[(qs.selectivity == 0.5) & (qs.query_id < args.n_queries)].reset_index(
        drop=True
    )
    log(f"  filtered to s=0.500 × {len(qs_500)} query")

    # 8M true_cardinality 재계산
    log("  [measure 1/3] re-computing true_cardinality for 8M (full scan)")
    true_cards_8m = {}
    t0 = time.time()
    with conn.cursor() as cur:
        for i, row in qs_500.iterrows():
            qid = int(row["query_id"])
            D = float(row["D_target"])
            emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
            vec_str = emb_to_pgvec(emb)
            cur.execute(
                f"SELECT count(*) FROM {args.table} "
                f"WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}"
            )
            true_cards_8m[qid] = int(cur.fetchone()[0])
            if (i + 1) % 20 == 0:
                log(f"    progress {i + 1}/{len(qs_500)} ({time.time() - t0:.1f}s)")
    log(f"    done ({time.time() - t0:.1f}s)")

    # 2. sampling_method 설정 + 측정
    log(f"  [measure 2/3] BERN/STRAT measurement, mode={mode}")
    log_path = Path(args.log_file)
    log_start_offset = log_path.stat().st_size if log_path.exists() else 0

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
            sel = 0.500
            D = float(row["D_target"])
            true_card = int(true_cards_8m[qid])

            emb = np.asarray(qp.iloc[qid]["embedding"], dtype=np.float32)
            vec_str = emb_to_pgvec(emb)

            sql = (
                "EXPLAIN (ANALYZE, FORMAT JSON) "
                f"SELECT count(*) FROM {args.table} "
                f"WHERE (ps_embedding <-> '{vec_str}'::vector) < {D}"
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
                        "selectivity": sel,
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
                        "selectivity": sel,
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

    # 3. log parsing
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
        "true_cards_8m": true_cards_8m,
    }
    return df, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cache-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1"
    )
    ap.add_argument(
        "--table", default="partsupp_deep_10_phase7_8m_subset"
    )
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--kmeans-iter", type=int, default=100)
    ap.add_argument("--kmeans-batch", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--port", type=int, default=55436)
    ap.add_argument("--db", default="wns41559")
    ap.add_argument("--user", default="wns41559")
    ap.add_argument(
        "--log-file", default=DEFAULT_LOG_FILE, help="Exqutor PG log file"
    )
    ap.add_argument(
        "--setup", action="store_true", help="run setup (copy + kmeans + update)"
    )
    ap.add_argument(
        "--measure",
        choices=["bern", "strat", "both"],
        default=None,
        help="run measurement for given mode(s)",
    )
    args = ap.parse_args()

    log(f"Phase 7-1 sf10 8M start (setup={args.setup}, measure={args.measure})")

    conn = psycopg.connect(
        host="/tmp",
        port=args.port,
        user=args.user,
        dbname=args.db,
        autocommit=True,
    )

    setup_info = None
    if args.setup:
        setup_info = setup_8m_subset(conn, args)
        setup_meta_path = Path(args.cache_dir) / "phase7_8m_setup.meta.json"
        with open(setup_meta_path, "w") as f:
            json.dump(
                {
                    "kst": kst_now(),
                    "args": vars(args),
                    "setup_info": setup_info,
                },
                f,
                indent=2,
                default=str,
            )
        log(f"  setup meta → {setup_meta_path}")

    if args.measure in ("bern", "both"):
        log("== BERN measurement ==")
        df, summary = measure_mode(conn, args, "bernoulli", setup_info or {})
        out = Path(args.cache_dir) / "phase7_8m_bern.parquet"
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
        df, summary = measure_mode(conn, args, "stratified", setup_info or {})
        out = Path(args.cache_dir) / "phase7_8m_strat.parquet"
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

    # paired 분석 (둘 다 있으면)
    bern_path = Path(args.cache_dir) / "phase7_8m_bern.parquet"
    strat_path = Path(args.cache_dir) / "phase7_8m_strat.parquet"
    if bern_path.exists() and strat_path.exists():
        log("== paired Wilcoxon analysis ==")
        from scipy import stats  # lazy import

        bern = pd.read_parquet(bern_path)
        strat = pd.read_parquet(strat_path)
        merged = bern.merge(
            strat,
            on=["query_id", "selectivity"],
            suffixes=("_bern", "_strat"),
        )
        # hook_est 기준 비교 (plan_rows 대신)
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
            out_paired = Path(args.cache_dir) / "phase7_8m_paired.json"
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
