"""
RQ1 Stage 3 — Selectivity 타겟별 range distance D 역산

입력:
  - cache/rq1/subset_1m.parquet
  - cache/rq1/query_pool.parquet

출력:
  - cache/rq1/query_selectivity.parquet  (query × selectivity 조합, 600행)
      columns: query_id, selectivity, D_target, true_cardinality
  - cache/rq1/stage3_meta.json

로직:
  각 query q에 대해, 선택도 s 타겟 달성을 위한
    D_target = q-quantile(distances) 인덱스 계산
  → 이후 Stage 4에서 이 D를 Adaptive Sampling의 range 임계값으로 사용
  true_cardinality = (dist < D_target).sum() 로 엄밀히 측정
  (quantile 동치값 이슈로 s * N 과 정확히 같지 않을 수 있음 — 실제값 사용)

파이프라인 문서: experiments/plans/RQ1_motivation_pipeline_20260414_162857.md §III.4
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

# Stage 2와 동일한 함수 재사용 — 간소화 위해 인라인
def kst_now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now_iso()}] {msg}", flush=True)


def load_parquet_vectors(path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    table = pq.read_table(path)
    pks = np.asarray(table.column("ps_partkey").to_numpy(), dtype=np.int32)
    sks = np.asarray(table.column("ps_suppkey").to_numpy(), dtype=np.int32)
    emb_col = table.column("embedding").combine_chunks()
    flat = emb_col.flatten().to_numpy(zero_copy_only=False)
    n = len(pks)
    dim = len(flat) // n
    vecs = flat.reshape(n, dim).astype(np.float32, copy=False)
    return pks, sks, vecs


def compute_distance_matrix(subset: np.ndarray, queries: np.ndarray) -> np.ndarray:
    subset = subset.astype(np.float32, copy=False)
    queries = queries.astype(np.float32, copy=False)
    subset_sq = (subset * subset).sum(axis=1, dtype=np.float32)
    queries_sq = (queries * queries).sum(axis=1, dtype=np.float32)
    dots = subset @ queries.T
    d2 = subset_sq[:, None] + queries_sq[None, :] - 2.0 * dots
    np.maximum(d2, 0, out=d2)
    return np.sqrt(d2, dtype=np.float32)


DEFAULT_SELECTIVITIES = [0.001, 0.01, 0.05, 0.10, 0.30, 0.50]


def main() -> int:
    parser = argparse.ArgumentParser(description="RQ1 Stage 3 — selectivity → D 역산")
    parser.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    parser.add_argument(
        "--selectivities",
        default=",".join(map(str, DEFAULT_SELECTIVITIES)),
        help="쉼표 구분 선택도 리스트",
    )
    args = parser.parse_args()

    selectivities = [float(x) for x in args.selectivities.split(",")]

    subset_path = os.path.join(args.in_dir, "subset_1m.parquet")
    query_path = os.path.join(args.in_dir, "query_pool.parquet")
    out_path = os.path.join(args.in_dir, "query_selectivity.parquet")
    meta_path = os.path.join(args.in_dir, "stage3_meta.json")

    t0 = time.time()
    log(f"시작 — in={args.in_dir}")
    log(f"  selectivities: {selectivities}")

    log("Stage 3.1 — parquet 로드")
    _, _, subset_vecs = load_parquet_vectors(subset_path)
    q_pks, q_sks, query_vecs = load_parquet_vectors(query_path)
    log(f"  subset: {subset_vecs.shape}, queries: {query_vecs.shape}")

    log("Stage 3.2 — 거리 행렬 계산")
    t1 = time.time()
    dists = compute_distance_matrix(subset_vecs, query_vecs)
    log(f"  shape: {dists.shape}, 소요 {time.time()-t1:.1f}s")

    log("Stage 3.3 — selectivity → D 역산 + true cardinality 계산")
    t2 = time.time()
    n_query = query_vecs.shape[0]
    n_total = subset_vecs.shape[0]

    rows = []
    for q in range(n_query):
        d = dists[:, q]
        d_sorted = np.sort(d)  # O(N log N) 한 번만
        for s in selectivities:
            # D_target: s-quantile 직전 경계
            # idx: 선택도 s에 해당하는 위치 (0-based)
            idx = int(s * n_total)
            if idx == 0:
                idx = 1  # 최소 1개는 매칭되도록
            # D_target을 d_sorted[idx] 보다 아주 조금 위로 설정 → 정확히 idx개 매칭
            if idx < n_total:
                D_target = float((d_sorted[idx - 1] + d_sorted[idx]) / 2.0)
            else:
                D_target = float(d_sorted[-1] + 1e-6)
            true_card = int((d < D_target).sum())
            rows.append(
                {
                    "query_id": int(q),
                    "ps_partkey": int(q_pks[q]),
                    "selectivity": float(s),
                    "D_target": D_target,
                    "true_cardinality": int(true_card),
                    "true_selectivity": float(true_card / n_total),
                }
            )

    log(f"  {len(rows)} rows (query × selectivity), 소요 {time.time()-t2:.1f}s")

    log("Stage 3.4 — parquet 저장")
    table = pa.table(
        {
            "query_id": pa.array([r["query_id"] for r in rows], type=pa.int32()),
            "ps_partkey": pa.array([r["ps_partkey"] for r in rows], type=pa.int32()),
            "selectivity": pa.array([r["selectivity"] for r in rows], type=pa.float64()),
            "D_target": pa.array([r["D_target"] for r in rows], type=pa.float64()),
            "true_cardinality": pa.array([r["true_cardinality"] for r in rows], type=pa.int64()),
            "true_selectivity": pa.array(
                [r["true_selectivity"] for r in rows], type=pa.float64()
            ),
        }
    )
    pq.write_table(table, out_path, compression="snappy")
    log(f"  저장: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB, {len(rows)} rows)")

    # 요약 (선택도별 D_target 분포)
    log("===== 선택도별 D_target 요약 =====")
    for s in selectivities:
        Ds = np.array([r["D_target"] for r in rows if r["selectivity"] == s])
        Tc = np.array([r["true_cardinality"] for r in rows if r["selectivity"] == s])
        log(
            f"  s={s:.3f}  →  D_target: "
            f"min={Ds.min():.3f} p50={np.quantile(Ds, 0.5):.3f} max={Ds.max():.3f}  |  "
            f"true_card p50={int(np.quantile(Tc, 0.5))} (target={int(s*n_total)})"
        )

    meta = {
        "timestamp_kst": kst_now_iso(),
        "script": "scripts/rq1_stage3_selectivity.py",
        "selectivities": selectivities,
        "n_query": int(n_query),
        "n_subset": int(n_total),
        "n_rows_out": int(len(rows)),
        "total_time_s": round(time.time() - t0, 2),
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    log(f"메타: {meta_path}")
    log(f"===== Stage 3 완료 (총 {time.time()-t0:.1f}s) =====")

    return 0


if __name__ == "__main__":
    sys.exit(main())
