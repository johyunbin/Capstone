"""
RQ1 Stage 2 — Skewness 프로파일링 (4개 지표 병기)

입력:
  - cache/rq1/subset_1m.parquet  (1M × 96d)
  - cache/rq1/query_pool.parquet (100 × 96d)

출력:
  - cache/rq1/query_skew.parquet — query당 4개 skew 지표 + 분포 통계 + 50-bin 히스토그램
  - cache/rq1/stage2_meta.json   — 실행 메타데이터

의존: numpy, scipy, pyarrow (Stage 1에서 설치 완료)

실행 예:
  python3 scripts/rq1_stage2_skew.py --in-dir cache/rq1

파이프라인 문서: experiments/plans/RQ1_motivation_pipeline_20260414_162857.md §III.3
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
import scipy.stats as st

HIST_BINS = 50


def kst_now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now_iso()}] {msg}", flush=True)


def load_parquet_vectors(path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """parquet에서 (ps_partkey, ps_suppkey, embedding matrix) 로드."""
    table = pq.read_table(path)
    pks = np.asarray(table.column("ps_partkey").to_numpy(), dtype=np.int32)
    sks = np.asarray(table.column("ps_suppkey").to_numpy(), dtype=np.int32)
    # ChunkedArray of FixedSizeList<float32> → combine + flatten → flat numpy
    emb_col = table.column("embedding").combine_chunks()
    flat = emb_col.flatten().to_numpy(zero_copy_only=False)
    n = len(pks)
    dim = len(flat) // n
    vecs = flat.reshape(n, dim).astype(np.float32, copy=False)
    return pks, sks, vecs


def compute_distance_matrix(subset: np.ndarray, queries: np.ndarray) -> np.ndarray:
    """
    ||a - b||_2 = sqrt(||a||^2 + ||b||^2 - 2 a·b)
    BLAS matmul 활용 — 단일 matmul로 (N, Q) 거리 행렬 생성.

    subset:  (N, dim)
    queries: (Q, dim)
    returns: (N, Q) float32
    """
    subset = subset.astype(np.float32, copy=False)
    queries = queries.astype(np.float32, copy=False)
    subset_sq = (subset * subset).sum(axis=1, dtype=np.float32)   # (N,)
    queries_sq = (queries * queries).sum(axis=1, dtype=np.float32)  # (Q,)
    # matmul: (N, dim) @ (dim, Q) → (N, Q)
    dots = subset @ queries.T
    d2 = subset_sq[:, None] + queries_sq[None, :] - 2.0 * dots
    np.maximum(d2, 0, out=d2)
    return np.sqrt(d2, dtype=np.float32)


def compute_skew_metrics(d: np.ndarray) -> dict:
    """
    단일 query의 거리 벡터 d (N,)에서 4개 skew 지표 + 분포 통계 계산.
    """
    # 극소값 제거 (query 자신과의 거리 0 포함 가능성)
    d_pos = d[d > 1e-6]
    if len(d_pos) < 100:
        d_pos = d  # fallback

    # Fisher skewness (Pearson 3rd moment)
    fisher = float(st.skew(d_pos, bias=False))

    # Log-Fisher: 고차원 거리 집중 대응 (로그 변환 후 Fisher)
    log_fisher = float(st.skew(np.log(d_pos + 1e-10), bias=False))

    # Tail ratio P99/P50 — heavy-tail 검출, robust
    p50 = float(np.quantile(d_pos, 0.50))
    p99 = float(np.quantile(d_pos, 0.99))
    tail_ratio = p99 / p50 if p50 > 0 else float("nan")

    # Bowley skewness — quartile 기반 robust
    q25, q50, q75 = np.quantile(d_pos, [0.25, 0.50, 0.75])
    iqr = q75 - q25
    bowley = float((q75 + q25 - 2 * q50) / iqr) if iqr > 0 else 0.0

    # 분포 통계
    p5 = float(np.quantile(d_pos, 0.05))
    p95 = float(np.quantile(d_pos, 0.95))

    return {
        "fisher_gamma": fisher,
        "log_gamma": log_fisher,
        "tail_ratio_p99_p50": tail_ratio,
        "bowley": bowley,
        "mean": float(d_pos.mean()),
        "std": float(d_pos.std(ddof=1)),
        "min": float(d_pos.min()),
        "max": float(d_pos.max()),
        "p5": p5,
        "p25": float(q25),
        "p50": p50,
        "p75": float(q75),
        "p95": p95,
        "p99": p99,
    }


def compute_histogram(d: np.ndarray, n_bins: int = HIST_BINS) -> tuple[np.ndarray, np.ndarray]:
    """50-bin 히스토그램. bins는 edges (n_bins+1), counts는 (n_bins,)"""
    counts, edges = np.histogram(d, bins=n_bins)
    return edges.astype(np.float32), counts.astype(np.int64)


def main() -> int:
    parser = argparse.ArgumentParser(description="RQ1 Stage 2 — skewness 4지표 프로파일링")
    parser.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    parser.add_argument("--subset-name", default="subset_1m.parquet")
    parser.add_argument("--query-name", default="query_pool.parquet")
    parser.add_argument("--out-name", default="query_skew.parquet")
    parser.add_argument("--meta-name", default="stage2_meta.json")
    args = parser.parse_args()

    subset_path = os.path.join(args.in_dir, args.subset_name)
    query_path = os.path.join(args.in_dir, args.query_name)
    out_path = os.path.join(args.in_dir, args.out_name)
    meta_path = os.path.join(args.in_dir, args.meta_name)

    t0 = time.time()
    log(f"시작 — in={args.in_dir}")
    log(f"  subset:   {subset_path}")
    log(f"  queries:  {query_path}")

    # 1. 로드
    log("Stage 2.1 — parquet 로드")
    subset_pks, subset_sks, subset_vecs = load_parquet_vectors(subset_path)
    query_pks, query_sks, query_vecs = load_parquet_vectors(query_path)
    log(
        f"  subset: {subset_vecs.shape}, queries: {query_vecs.shape}, "
        f"로드 소요 {time.time()-t0:.1f}s"
    )

    # 2. 거리 행렬 계산
    log("Stage 2.2 — 거리 행렬 (N × Q) 계산 — BLAS matmul")
    t1 = time.time()
    dists = compute_distance_matrix(subset_vecs, query_vecs)
    log(f"  shape: {dists.shape}, dtype: {dists.dtype}, 소요 {time.time()-t1:.1f}s")
    log(f"  메모리: {dists.nbytes / (1024*1024):.1f} MB")

    # 3. 각 query별 skew + histogram
    log("Stage 2.3 — 100 query skew 지표 + 히스토그램")
    t2 = time.time()
    n_query = query_vecs.shape[0]
    all_metrics = []
    all_bins = np.zeros((n_query, HIST_BINS + 1), dtype=np.float32)
    all_counts = np.zeros((n_query, HIST_BINS), dtype=np.int64)

    for q in range(n_query):
        d = dists[:, q]
        m = compute_skew_metrics(d)
        m["query_id"] = int(q)
        m["ps_partkey"] = int(query_pks[q])
        m["ps_suppkey"] = int(query_sks[q])
        all_metrics.append(m)

        bins, counts = compute_histogram(d)
        all_bins[q] = bins
        all_counts[q] = counts

    log(f"  {n_query} queries 처리, 소요 {time.time()-t2:.1f}s")

    # 4. parquet 저장 (FixedSizeList 히스토그램)
    log("Stage 2.4 — parquet 저장")
    arr_cols = {
        "query_id": pa.array([m["query_id"] for m in all_metrics], type=pa.int32()),
        "ps_partkey": pa.array([m["ps_partkey"] for m in all_metrics], type=pa.int32()),
        "ps_suppkey": pa.array([m["ps_suppkey"] for m in all_metrics], type=pa.int32()),
        "fisher_gamma": pa.array([m["fisher_gamma"] for m in all_metrics], type=pa.float64()),
        "log_gamma": pa.array([m["log_gamma"] for m in all_metrics], type=pa.float64()),
        "tail_ratio_p99_p50": pa.array(
            [m["tail_ratio_p99_p50"] for m in all_metrics], type=pa.float64()
        ),
        "bowley": pa.array([m["bowley"] for m in all_metrics], type=pa.float64()),
        "mean": pa.array([m["mean"] for m in all_metrics], type=pa.float64()),
        "std": pa.array([m["std"] for m in all_metrics], type=pa.float64()),
        "min": pa.array([m["min"] for m in all_metrics], type=pa.float64()),
        "max": pa.array([m["max"] for m in all_metrics], type=pa.float64()),
        "p5": pa.array([m["p5"] for m in all_metrics], type=pa.float64()),
        "p25": pa.array([m["p25"] for m in all_metrics], type=pa.float64()),
        "p50": pa.array([m["p50"] for m in all_metrics], type=pa.float64()),
        "p75": pa.array([m["p75"] for m in all_metrics], type=pa.float64()),
        "p95": pa.array([m["p95"] for m in all_metrics], type=pa.float64()),
        "p99": pa.array([m["p99"] for m in all_metrics], type=pa.float64()),
        "hist_bins": pa.FixedSizeListArray.from_arrays(
            pa.array(all_bins.ravel(), type=pa.float32()), HIST_BINS + 1
        ),
        "hist_counts": pa.FixedSizeListArray.from_arrays(
            pa.array(all_counts.ravel(), type=pa.int64()), HIST_BINS
        ),
    }
    table = pa.table(arr_cols)
    pq.write_table(table, out_path, compression="snappy")
    sz_kb = os.path.getsize(out_path) / 1024
    log(f"  저장: {out_path} ({sz_kb:.1f} KB, {n_query} rows)")

    # 5. 요약 통계 출력 (육안 확인용)
    log("===== 4 skew 지표 요약 =====")
    for key in ["fisher_gamma", "log_gamma", "tail_ratio_p99_p50", "bowley"]:
        vals = np.array([m[key] for m in all_metrics])
        log(
            f"  {key:>22s}: "
            f"min={vals.min():+.3f} p25={np.quantile(vals, 0.25):+.3f} "
            f"p50={np.quantile(vals, 0.5):+.3f} p75={np.quantile(vals, 0.75):+.3f} "
            f"max={vals.max():+.3f}"
        )

    # v3 절대 기준 그룹 분포 (Fisher γ)
    fg = np.array([m["fisher_gamma"] for m in all_metrics])
    abs_fg = np.abs(fg)
    groups = {
        "symmetric (|γ|<0.5)": int((abs_fg < 0.5).sum()),
        "moderate  (0.5~1.0)": int(((abs_fg >= 0.5) & (abs_fg < 1.0)).sum()),
        "skewed    (1.0~2.0)": int(((abs_fg >= 1.0) & (abs_fg < 2.0)).sum()),
        "extreme   (>=2.0)  ": int((abs_fg >= 2.0).sum()),
    }
    log("v3 절대 기준 그룹 분포 (Fisher γ):")
    for name, cnt in groups.items():
        log(f"  {name}: {cnt:3d}")

    # 6. 메타 저장
    meta = {
        "timestamp_kst": kst_now_iso(),
        "script": "scripts/rq1_stage2_skew.py",
        "subset_path": subset_path,
        "query_path": query_path,
        "n_query": int(n_query),
        "n_subset": int(subset_vecs.shape[0]),
        "dim": int(subset_vecs.shape[1]),
        "total_time_s": round(time.time() - t0, 2),
        "v3_absolute_groups": groups,
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    log(f"메타: {meta_path}")
    log(f"===== Stage 2 완료 (총 {time.time()-t0:.1f}s) =====")

    return 0


if __name__ == "__main__":
    sys.exit(main())
