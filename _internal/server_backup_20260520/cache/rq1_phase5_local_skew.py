#!/usr/bin/env python3
"""
RQ1 Phase 5 — Local skew 4지표 + Spearman 재측정

Phase 4 의 글로벌 4 지표 (Fisher γ, log-γ, tail ratio P99/P50, Bowley) 가 모두
q_error 와의 Spearman |ρ| < 0.05 로 무효화된 직후의 후속 단계. 본 스크립트는
*query 주변* 의 local 구조를 포착하는 4 지표를 계산해서 phase4_bernoulli.parquet
의 q_error 와 24 조합 (4 지표 × 6 selectivity) 의 Spearman ρ 를 측정한다.

4 local 지표 (모두 numpy + scipy 만으로 구현, networkx/sklearn 의존성 없음):

  (i)   kNN distance entropy (k=50)
        — 각 query 의 50 nearest neighbor 거리들을 10 bin 히스토그램으로 묶고
          Shannon entropy 를 계산. compact cluster 면 entropy 낮음, isotropic
          spread 면 entropy 높음.

  (ii)  kNN PCA explained variance ratio 1 (k=50)
        — 50 NN 벡터 (50 × 96) 를 centering 후 SVD. 첫 singular value 의
          variance 비율. 한 방향으로 길게 펴진 cluster 면 EVR1 큼, isotropic
          spread 면 EVR1 작음 (1/96 근처).

  (iii) KDE modality count (pilot k=500)
        — 500 nearest distances 의 1D Gaussian KDE 추정 후 grid evaluate +
          scipy.signal.find_peaks 로 mode 개수. multi-modal 이면 query 주변
          이 cluster 가 여러 개 (혼합 분포) 라는 신호.

  (iv)  NN clustering coefficient (k=50, inner_k=10)
        — 50 NN 간의 50×50 거리 행렬에서 각 노드의 inner_k-NN 으로 무방향
          그래프 생성. 각 노드의 local clustering coefficient (이웃들 사이
          의 edge 비율) 평균. cluster 가 강하게 묶이면 높음.

입력:
  - cache/rq1/subset_1m.parquet   (1M × 96d, 374 MB, 서버 only)
  - cache/rq1/query_pool.parquet  (100 × 96d)
  - cache/rq1/phase4_bernoulli.parquet  (600행, q_error 포함, Spearman join 용)

출력:
  - cache/rq1/query_local_skew.parquet     (100행 × 4 + meta)
  - cache/rq1/phase5_local_skew_spearman.json  (24 조합 Spearman ρ + p)
  - cache/rq1/phase5_local_skew_meta.json   (실행 메타 + summary stat)

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase5_local_skew.py
"""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import scipy.signal as ssg
import scipy.stats as sst


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now()}] {msg}", flush=True)


def load_parquet_vectors(path: str) -> tuple[np.ndarray, np.ndarray]:
    """parquet에서 (ps_partkey, embedding matrix) 로드.

    stage2_skew.py 의 load_parquet_vectors 를 단순화 (suppkey 불필요).
    """
    table = pq.read_table(path)
    pks = np.asarray(table.column("ps_partkey").to_numpy(), dtype=np.int32)
    emb_col = table.column("embedding").combine_chunks()
    flat = emb_col.flatten().to_numpy(zero_copy_only=False)
    n = len(pks)
    dim = len(flat) // n
    vecs = flat.reshape(n, dim).astype(np.float32, copy=False)
    return pks, vecs


def compute_distance_matrix(subset: np.ndarray, queries: np.ndarray) -> np.ndarray:
    """
    BLAS matmul 로 (N, Q) Euclidean 거리 행렬.
    stage2_skew.py 의 동명 함수와 동일.
    """
    subset = subset.astype(np.float32, copy=False)
    queries = queries.astype(np.float32, copy=False)
    subset_sq = (subset * subset).sum(axis=1, dtype=np.float32)
    queries_sq = (queries * queries).sum(axis=1, dtype=np.float32)
    dots = subset @ queries.T
    d2 = subset_sq[:, None] + queries_sq[None, :] - 2.0 * dots
    np.maximum(d2, 0, out=d2)
    return np.sqrt(d2, dtype=np.float32)


# ---- 4 local skew 지표 ----------------------------------------------------


def metric_knn_distance_entropy(d_top_k: np.ndarray, n_bins: int) -> float:
    """50 NN 거리들의 n_bins 히스토그램 Shannon entropy (nat 단위).

    histogram 이 0 인 bin 은 entropy 합산에서 제외 (0 * log 0 = 0 처리).
    """
    if len(d_top_k) < 2:
        return 0.0
    hist, _ = np.histogram(d_top_k, bins=n_bins)
    total = hist.sum()
    if total <= 0:
        return 0.0
    p = hist[hist > 0].astype(np.float64) / float(total)
    return float(-np.sum(p * np.log(p)))


def metric_knn_pca_evr1(v_top_k: np.ndarray) -> float:
    """50 NN 벡터의 PCA 첫 컴포넌트 explained variance ratio.

    sklearn 미사용. centering 후 SVD 의 singular value 제곱 합 분율.
    edge case (k<2 또는 zero variance) 는 0.0 반환.
    """
    if v_top_k.shape[0] < 2:
        return 0.0
    centered = v_top_k.astype(np.float64) - v_top_k.mean(axis=0, dtype=np.float64)
    try:
        _, s, _ = np.linalg.svd(centered, full_matrices=False)
    except np.linalg.LinAlgError:
        return 0.0
    total_var = float(np.sum(s * s))
    if total_var <= 0:
        return 0.0
    return float((s[0] * s[0]) / total_var)


def metric_kde_modality(
    d_pilot: np.ndarray,
    n_grid: int,
    bandwidth: float | None = None,
) -> tuple[int, float]:
    """500 NN 거리의 1D Gaussian KDE → mode 개수 + 첫 peak prominence.

    bandwidth 는 scipy 기본 (Scott rule) 사용. find_peaks 는 default
    height/distance/prominence 없이 호출 (모든 local maximum 계산), 이후
    prominence > 0.05 * peak max 인 peak 만 유효 mode 로 카운트.
    """
    if len(d_pilot) < 10:
        return 0, 0.0
    try:
        kde = sst.gaussian_kde(d_pilot, bw_method=bandwidth)
    except (np.linalg.LinAlgError, ValueError):
        return 0, 0.0
    d_min = float(d_pilot.min())
    d_max = float(d_pilot.max())
    if d_max <= d_min:
        return 1, 0.0
    span = d_max - d_min
    xs = np.linspace(d_min - 0.05 * span, d_max + 0.05 * span, n_grid)
    density = kde(xs)
    peaks, props = ssg.find_peaks(density, prominence=0.0)
    if len(peaks) == 0:
        return 0, 0.0
    prominences = props["prominences"]
    threshold = 0.05 * float(density.max())
    valid = int(np.sum(prominences >= threshold))
    max_prom = float(prominences.max()) if len(prominences) else 0.0
    return valid, max_prom


def metric_nn_clustering(v_top_k: np.ndarray, inner_k: int) -> float:
    """50 NN 노드 사이의 inner_k-NN 그래프의 평균 local clustering coefficient.

    inner_k 는 자기자신 제외 후의 k. networkx 미사용. numpy 만으로
    bool adjacency + per-node neighbor 사이 edge 카운트 → C_local.
    """
    n = v_top_k.shape[0]
    if n < 3 or inner_k < 2:
        return 0.0
    diff = v_top_k[:, None, :] - v_top_k[None, :, :]
    d2 = np.sum(diff * diff, axis=-1)
    np.fill_diagonal(d2, np.inf)
    k = min(inner_k, n - 1)
    nn_idx = np.argpartition(d2, k - 1, axis=1)[:, :k]
    adj = np.zeros((n, n), dtype=bool)
    rows = np.repeat(np.arange(n), k)
    cols = nn_idx.reshape(-1)
    adj[rows, cols] = True
    adj |= adj.T  # 무방향화
    np.fill_diagonal(adj, False)

    coefs = []
    for i in range(n):
        neighbors = np.where(adj[i])[0]
        deg = len(neighbors)
        if deg < 2:
            continue
        sub_adj = adj[np.ix_(neighbors, neighbors)]
        n_edges = int(np.sum(np.triu(sub_adj, k=1)))
        max_edges = deg * (deg - 1) / 2
        coefs.append(n_edges / max_edges if max_edges > 0 else 0.0)
    if not coefs:
        return 0.0
    return float(np.mean(coefs))


# ---- 메인 -----------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    ap.add_argument("--out-prefix", default="phase5")
    ap.add_argument(
        "--k-nn",
        type=int,
        default=50,
        help="kNN distance entropy + kNN PCA EVR + clustering 의 k",
    )
    ap.add_argument(
        "--k-pilot",
        type=int,
        default=500,
        help="KDE modality 의 pilot sample 크기",
    )
    ap.add_argument(
        "--n-bins",
        type=int,
        default=10,
        help="kNN distance entropy 의 히스토그램 bin 개수",
    )
    ap.add_argument(
        "--n-grid",
        type=int,
        default=512,
        help="KDE evaluate grid 크기",
    )
    ap.add_argument(
        "--inner-k",
        type=int,
        default=10,
        help="NN clustering 의 inner k (50 NN 안에서의 k)",
    )
    args = ap.parse_args()

    log(
        f"Phase 5 start — k_nn={args.k_nn}, k_pilot={args.k_pilot}, "
        f"n_bins={args.n_bins}, inner_k={args.inner_k}"
    )

    # --- 데이터 로드 -----------------------------------------------------
    t_load0 = time.time()
    _, subset = load_parquet_vectors(f"{args.in_dir}/subset_1m.parquet")
    _, queries = load_parquet_vectors(f"{args.in_dir}/query_pool.parquet")
    log(f"loaded subset {subset.shape}, queries {queries.shape} ({time.time()-t_load0:.1f}s)")

    n_queries = queries.shape[0]
    if args.k_pilot > subset.shape[0]:
        raise ValueError("k_pilot must be <= subset size")
    if args.k_nn > args.k_pilot:
        raise ValueError("k_nn must be <= k_pilot (NN ⊂ pilot 가정)")

    # --- 거리 행렬 계산 (1M × 100, 약 400 MB float32) ----------------------
    t_dm0 = time.time()
    dist = compute_distance_matrix(subset, queries)  # (N, Q)
    log(f"distance matrix {dist.shape} done ({time.time()-t_dm0:.1f}s)")

    # --- query 별 4 지표 -------------------------------------------------
    rows = []
    t_metric0 = time.time()
    for q_idx in range(n_queries):
        d = dist[:, q_idx]
        # top k_pilot indices (sorted)
        pilot_part_idx = np.argpartition(d, args.k_pilot - 1)[: args.k_pilot]
        pilot_d_unsorted = d[pilot_part_idx]
        pilot_sort = np.argsort(pilot_d_unsorted)
        pilot_idx = pilot_part_idx[pilot_sort]
        pilot_d = pilot_d_unsorted[pilot_sort]

        knn_idx = pilot_idx[: args.k_nn]
        knn_d = pilot_d[: args.k_nn]
        knn_v = subset[knn_idx]

        m_entropy = metric_knn_distance_entropy(knn_d, n_bins=args.n_bins)
        m_evr1 = metric_knn_pca_evr1(knn_v)
        m_modes, m_prom = metric_kde_modality(pilot_d, n_grid=args.n_grid)
        m_cluster = metric_nn_clustering(knn_v, inner_k=args.inner_k)

        rows.append(
            {
                "query_id": q_idx,
                "knn_distance_entropy": m_entropy,
                "knn_pca_evr1": m_evr1,
                "kde_modality_count": m_modes,
                "kde_max_prominence": m_prom,
                "nn_clustering_coef": m_cluster,
                "knn_d_min": float(knn_d.min()),
                "knn_d_max": float(knn_d.max()),
                "knn_d_mean": float(knn_d.mean()),
            }
        )
    log(f"4 local metrics computed for {n_queries} queries ({time.time()-t_metric0:.1f}s)")

    # 메모리 절약: dist 해제
    del dist

    # --- parquet 저장 ----------------------------------------------------
    table = pa.Table.from_pylist(rows)
    out_parquet = f"{args.in_dir}/query_local_skew.parquet"
    pq.write_table(table, out_parquet)
    log(f"saved {out_parquet} ({len(rows)} rows)")

    # --- Spearman 분석 — phase4_bernoulli.parquet 와 join --------------
    p4_path = f"{args.in_dir}/phase4_bernoulli.parquet"
    p4 = pq.read_table(p4_path).to_pandas()
    log(f"loaded {p4_path} ({len(p4)} rows)")

    # local skew → DataFrame
    import pandas as pd  # 지연 import (parquet 의존성과 분리)

    local_df = pd.DataFrame(rows)
    merged = p4.merge(local_df, on="query_id", how="inner")
    log(f"merged → {len(merged)} rows (4 metrics × {len(merged) // n_queries} sels)")

    metric_cols = [
        "knn_distance_entropy",
        "knn_pca_evr1",
        "kde_modality_count",
        "nn_clustering_coef",
    ]
    selectivities = sorted(merged["selectivity"].unique())

    spearman_results = []
    for metric in metric_cols:
        for sel in selectivities:
            sub = merged[merged["selectivity"] == sel]
            sub_valid = sub.dropna(subset=["q_error"])
            if len(sub_valid) < 5:
                continue
            x = sub_valid[metric].values
            y = sub_valid["q_error"].values
            try:
                rho, p = sst.spearmanr(x, y)
            except (ValueError, TypeError):
                rho, p = float("nan"), float("nan")
            spearman_results.append(
                {
                    "metric": metric,
                    "selectivity": float(sel),
                    "n": int(len(sub_valid)),
                    "spearman_rho": (
                        float(rho) if rho is not None and not np.isnan(rho) else None
                    ),
                    "p_value": (
                        float(p) if p is not None and not np.isnan(p) else None
                    ),
                    "abs_rho": (
                        float(abs(rho))
                        if rho is not None and not np.isnan(rho)
                        else None
                    ),
                }
            )

    # |ρ| > 0.2 후보 식별
    strong = [
        r
        for r in spearman_results
        if r["abs_rho"] is not None and r["abs_rho"] > 0.2
    ]
    strong_sorted = sorted(
        strong, key=lambda r: r["abs_rho"] or 0.0, reverse=True
    )

    spearman_payload = {
        "kst": kst_now(),
        "n_queries": n_queries,
        "n_metrics": len(metric_cols),
        "n_selectivities": len(selectivities),
        "n_combos": len(spearman_results),
        "strong_threshold": 0.2,
        "n_strong": len(strong),
        "all_combos": spearman_results,
        "strong_combos_sorted": strong_sorted,
    }

    out_spearman = f"{args.in_dir}/{args.out_prefix}_local_skew_spearman.json"
    with open(out_spearman, "w") as f:
        json.dump(spearman_payload, f, indent=2)
    log(f"saved {out_spearman} ({len(spearman_results)} combos, {len(strong)} strong)")

    # --- 메타 -----------------------------------------------------------
    local_summary = {
        col: {
            "min": float(local_df[col].min()),
            "max": float(local_df[col].max()),
            "mean": float(local_df[col].mean()),
            "median": float(local_df[col].median()),
            "std": float(local_df[col].std(ddof=1)),
        }
        for col in metric_cols
    }
    meta = {
        "kst": kst_now(),
        "args": vars(args),
        "n_queries": n_queries,
        "subset_shape": list(subset.shape),
        "elapsed_s": round(time.time() - t_load0, 2),
        "local_metric_summary": local_summary,
        "n_strong_combos": len(strong),
        "strong_combos_top3": strong_sorted[:3],
    }
    out_meta = f"{args.in_dir}/{args.out_prefix}_local_skew_meta.json"
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    log(f"saved {out_meta}")

    # 간단 콘솔 요약
    print()
    print("=== local metric summary ===")
    for col, s in local_summary.items():
        print(
            f"  {col:24s}: med={s['median']:.4f}  "
            f"[min {s['min']:.4f}, max {s['max']:.4f}]  std={s['std']:.4f}"
        )
    print()
    print("=== Spearman ρ (q_error 와의 상관, |ρ|>0.2 후보) ===")
    if not strong_sorted:
        print("  (없음 — 모든 24 조합 |ρ| ≤ 0.2)")
    else:
        for r in strong_sorted:
            tag = " *" if r["p_value"] is not None and r["p_value"] < 0.05 else ""
            print(
                f"  {r['metric']:24s}  s={r['selectivity']:.3f}  "
                f"ρ={r['spearman_rho']:+.3f}  p={r['p_value']:.4g}  n={r['n']}{tag}"
            )
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
