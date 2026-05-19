"""
RQ1 Stage 1 — partsupp_deep_10 서브셋 + query pool 덤프

입력: 서버 PG (wns41559 DB, partsupp_deep_10 테이블)
출력:
  - cache/rq1/subset_1m.parquet   (1M rows × 96d)
  - cache/rq1/query_pool.parquet  (100 rows × 96d, seed=42)
  - cache/rq1/stage1_meta.json    (메타데이터: seed, block 통계 등)

파이프라인 문서: experiments/plans/RQ1_motivation_pipeline_20260414_162857.md
의존: numpy, pandas, pyarrow, psycopg[binary], pgvector (user pip install 완료)

실행 예:
  python3 scripts/rq1_stage1_dump.py \\
      --subset-rows 1000000 --n-query 100 --seed 42
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import psycopg
import pyarrow as pa
import pyarrow.parquet as pq
from pgvector.psycopg import register_vector

# ----------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------
DEFAULT_OUT_DIR = "/mnt/hdd0/home/capstone2026/cache/rq1"
DEFAULT_CONN = "host=/tmp port=55435 user=wns41559 dbname=wns41559"
TABLE = "partsupp_deep_10"
VEC_COL = "ps_embedding"
DIM = 96


def kst_now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now_iso()}] {msg}", flush=True)


def measure_block_stats(conn) -> dict:
    """partsupp_deep_10의 평균 블록당 행 수 측정 (TABLESAMPLE SYSTEM 근사용)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              pg_relation_size(%s)                    AS rel_size,
              (SELECT reltuples::bigint FROM pg_class WHERE relname = %s) AS reltuples,
              current_setting('block_size')::int      AS block_size
            """,
            (TABLE, TABLE),
        )
        rel_size, reltuples, block_size = cur.fetchone()
    n_blocks = rel_size // block_size
    rows_per_block = reltuples / n_blocks if n_blocks else 0
    return {
        "rel_size_bytes": int(rel_size),
        "reltuples": int(reltuples),
        "n_blocks": int(n_blocks),
        "block_size_bytes": int(block_size),
        "rows_per_block_mean": float(rows_per_block),
    }


def dump_subset(conn, subset_rows: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    ps_partkey 기준 DISTINCT ON으로 1 partkey당 1 row만 선택하여 subset_rows 확보.
    8M 행 테이블에서 1M distinct partkey → 1M rows 반환.

    전송량: 1M × 96 × 4B ≈ 384 MB
    """
    log(f"Stage 1.1 — subset {subset_rows:,} rows 추출 (DISTINCT ON ps_partkey)")
    t0 = time.time()

    pks = np.empty(subset_rows, dtype=np.int32)
    sks = np.empty(subset_rows, dtype=np.int32)
    vecs = np.empty((subset_rows, DIM), dtype=np.float32)

    # BETWEEN 조건으로 partkey 범위 제한 → 서버 측 스캔 범위 축소
    # ps_partkey 분포: 1 ~ 2_000_000 (distinct)
    # 1M subset을 확보하려면 ps_partkey IN [1, subset_rows] BETWEEN 충분
    sql = f"""
        SELECT ps_partkey, ps_suppkey, {VEC_COL}
        FROM (
            SELECT DISTINCT ON (ps_partkey) ps_partkey, ps_suppkey, {VEC_COL}
            FROM {TABLE}
            WHERE ps_partkey BETWEEN 1 AND {subset_rows}
            ORDER BY ps_partkey, ps_suppkey
        ) s
        ORDER BY ps_partkey
    """

    with conn.cursor(name="subset_cursor") as cur:
        cur.itersize = 50_000
        cur.execute(sql)
        idx = 0
        for pk, sk, emb in cur:
            if idx >= subset_rows:
                break
            pks[idx] = pk
            sks[idx] = sk
            # pgvector binding은 numpy array를 반환 (register_vector 호출 후)
            vecs[idx] = np.asarray(emb, dtype=np.float32)
            idx += 1
            if idx % 200_000 == 0:
                log(f"  ... {idx:,} rows 진행 ({time.time()-t0:.1f}s 경과)")

    if idx < subset_rows:
        log(f"경고: 요청 {subset_rows:,} 대비 실제 {idx:,} rows만 확보. 슬라이싱")
        pks = pks[:idx]
        sks = sks[:idx]
        vecs = vecs[:idx]

    log(f"  완료: {len(pks):,} rows, 소요 {time.time()-t0:.1f}s")
    return pks, sks, vecs


def select_query_pool(
    pks: np.ndarray,
    sks: np.ndarray,
    vecs: np.ndarray,
    n_query: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Python RNG 기반 결정론적 query pool 선택.
    서브셋 내부에서 n_query개 index를 무작위로 뽑는다.
    """
    log(f"Stage 1.2 — query pool {n_query}개 선택 (seed={seed})")
    rng = np.random.default_rng(seed)
    total = len(pks)
    q_idx = rng.choice(total, size=n_query, replace=False)
    q_idx.sort()
    return q_idx, pks[q_idx], sks[q_idx], vecs[q_idx]


def save_parquet(path: str, pks: np.ndarray, sks: np.ndarray, vecs: np.ndarray) -> None:
    """(ps_partkey, ps_suppkey, embedding) FixedSizeList parquet 저장."""
    # vecs를 FixedSizeList<float32>[DIM]로 압축
    flat = pa.array(vecs.ravel(), type=pa.float32())
    vec_arr = pa.FixedSizeListArray.from_arrays(flat, DIM)
    table = pa.table(
        {
            "ps_partkey": pa.array(pks, type=pa.int32()),
            "ps_suppkey": pa.array(sks, type=pa.int32()),
            "embedding": vec_arr,
        }
    )
    pq.write_table(table, path, compression="snappy")
    sz_mb = os.path.getsize(path) / (1024 * 1024)
    log(f"  저장: {path} ({sz_mb:.1f} MB, {len(pks):,} rows)")


def main() -> int:
    parser = argparse.ArgumentParser(description="RQ1 Stage 1 — subset + query pool 덤프")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--conn", default=DEFAULT_CONN)
    parser.add_argument("--subset-rows", type=int, default=1_000_000)
    parser.add_argument("--n-query", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    subset_path = os.path.join(args.out_dir, "subset_1m.parquet")
    query_path = os.path.join(args.out_dir, "query_pool.parquet")
    meta_path = os.path.join(args.out_dir, "stage1_meta.json")

    log(f"시작 — out={args.out_dir}, subset={args.subset_rows:,}, n_query={args.n_query}, seed={args.seed}")

    with psycopg.connect(args.conn) as conn:
        register_vector(conn)

        # 1. 블록 통계 측정
        block_stats = measure_block_stats(conn)
        log(
            f"블록 통계: {block_stats['reltuples']:,} rows / "
            f"{block_stats['n_blocks']:,} blocks = "
            f"{block_stats['rows_per_block_mean']:.1f} rows/block"
        )

        # 2. Subset 덤프
        pks, sks, vecs = dump_subset(conn, args.subset_rows)

        # 3. Query pool 선택
        q_idx, q_pks, q_sks, q_vecs = select_query_pool(pks, sks, vecs, args.n_query, args.seed)

    # 4. Parquet 저장
    log("Stage 1.3 — parquet 저장")
    save_parquet(subset_path, pks, sks, vecs)
    save_parquet(query_path, q_pks, q_sks, q_vecs)

    # 5. 메타데이터 저장
    meta = {
        "timestamp_kst": kst_now_iso(),
        "script": "scripts/rq1_stage1_dump.py",
        "subset_rows": int(len(pks)),
        "subset_rows_requested": int(args.subset_rows),
        "n_query": int(len(q_pks)),
        "seed": int(args.seed),
        "dim": int(DIM),
        "table": TABLE,
        "vec_column": VEC_COL,
        "query_index_in_subset": q_idx.tolist(),
        "block_stats": block_stats,
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    log(f"  메타: {meta_path}")

    # 6. 요약
    log("===== Stage 1 완료 =====")
    log(f"subset       : {subset_path}")
    log(f"query_pool   : {query_path}")
    log(f"meta         : {meta_path}")
    log(f"rows_per_block: {block_stats['rows_per_block_mean']:.1f} (block_system ablation용)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
