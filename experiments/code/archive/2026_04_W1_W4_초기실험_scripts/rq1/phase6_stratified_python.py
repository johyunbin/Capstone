#!/usr/bin/env python3
"""
RQ1 Phase 6 Step 1~3 — Stratified Sampling Python counterfactual

Phase 5 의 8 지표 종합 결론 (query-side feature 로는 q_error 사전 식별 불가능)
이후, Pivot C 의 *data-side global stratification* 1차 시도.

Layer 정의 (data-side):
  - 1M subset 의 1st PCA component 값을 deciles (10 quantile) 로 partition
  - 각 vector 는 정확히 하나의 stratum 에 속함 (stratum_id ∈ [0, 9])
  - query 와 무관하게 사전계산 (Exqutor 의 vector_index_create 패러다임 호환)

Stratified estimator (Horvitz-Thompson):
  est = sum_{i=1}^{K} (n_i / s_i) * cnt_i
  - n_i: stratum i 의 전체 행 수
  - s_i: stratum i 에서 추출한 sample 행 수 (균등 배분: floor(S/K), 잔여는 stratum 0~r-1 에)
  - cnt_i: stratum i 의 sample 안에서 조건 (||v - q|| < D) 만족하는 행 수

Counterfactual 모드 2 종 (동일 환경, 동일 seed):
  - bernoulli: uniform random sample 385 행, est = cnt × N / S  (Exqutor L1232)
  - stratified: 위 Horvitz-Thompson 형태

100 query × 6 selectivity × 5 seed × 2 mode = 6000 측정. seed 평균 후
600 paired 관측으로 paired Wilcoxon (stratified < bernoulli) 검정.

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase6_stratified_python.py
"""

import argparse
import json
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import scipy.stats as sst

SAMPLE_SIZE_DEFAULT = 385  # Exqutor adaptive default
N_STRATA_DEFAULT = 10
N_SEEDS_DEFAULT = 5


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now()}] {msg}", flush=True)


def load_parquet_vectors(path: str) -> tuple[np.ndarray, np.ndarray]:
    table = pq.read_table(path)
    pks = np.asarray(table.column("ps_partkey").to_numpy(), dtype=np.int32)
    emb_col = table.column("embedding").combine_chunks()
    flat = emb_col.flatten().to_numpy(zero_copy_only=False)
    n = len(pks)
    dim = len(flat) // n
    vecs = flat.reshape(n, dim).astype(np.float32, copy=False)
    return pks, vecs


def compute_first_pc(vectors: np.ndarray) -> tuple[np.ndarray, dict]:
    """
    1M × 96 vector 의 첫 PCA component 값.

    full SVD 대신 covariance eigendecomposition (96 × 96) 으로 효율 처리.
    centering → C = X^T X / (N-1) → eigh → 가장 큰 eigenvalue 의 eigenvector → 투영.
    """
    n, dim = vectors.shape
    mean = vectors.mean(axis=0, dtype=np.float64)
    centered = vectors.astype(np.float64) - mean  # (N, dim)
    cov = (centered.T @ centered) / (n - 1)        # (dim, dim)
    eigvals, eigvecs = np.linalg.eigh(cov)         # ascending order
    first_pc = eigvecs[:, -1]                       # largest eigenvalue
    proj = centered @ first_pc                       # (N,)
    info = {
        "eigenvalues_top5": [float(v) for v in eigvals[-5:][::-1]],
        "first_eigval": float(eigvals[-1]),
        "explained_var_ratio_pc1": float(eigvals[-1] / eigvals.sum()),
        "first_pc_norm": float(np.linalg.norm(first_pc)),
    }
    return proj.astype(np.float32), info


def define_strata_pca_decile(
    proj: np.ndarray, n_strata: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    첫 PC 값을 quantile bin 으로 partition → 1M stratum_id.

    np.quantile 로 경계값 산출 후 np.searchsorted. boundary 양 끝은 +/- inf 처리.
    return: (stratum_id, edges, sizes)
    """
    qs = np.linspace(0, 1, n_strata + 1)[1:-1]  # n_strata-1 개 internal 경계
    edges = np.quantile(proj, qs)
    stratum_id = np.searchsorted(edges, proj, side="right").astype(np.int16)
    # 보장: 0 <= stratum_id < n_strata
    stratum_id = np.clip(stratum_id, 0, n_strata - 1)
    sizes = np.bincount(stratum_id, minlength=n_strata)
    return stratum_id, edges, sizes


def build_strata_index(
    vectors: np.ndarray, stratum_id: np.ndarray, n_strata: int
) -> tuple[dict[int, np.ndarray], dict[int, int]]:
    """stratum 별 벡터 행을 contig 로 미리 추출 (per-stratum slicing 가속용)."""
    strat_vecs: dict[int, np.ndarray] = {}
    strat_n: dict[int, int] = {}
    for i in range(n_strata):
        idx = np.where(stratum_id == i)[0]
        strat_vecs[i] = vectors[idx]
        strat_n[i] = int(len(idx))
    return strat_vecs, strat_n


def split_sample_budget(sample_size: int, n_strata: int) -> np.ndarray:
    """
    균등 stratified sample 배분: floor(S/K) 모두에게, 잔여 r = S - K*floor 는 stratum 0~r-1 에.
    """
    base = sample_size // n_strata
    rem = sample_size - base * n_strata
    sizes = np.full(n_strata, base, dtype=np.int32)
    sizes[:rem] += 1
    return sizes


def _q_error(est: float, true_card: int) -> float:
    """Stage 4 패턴: max(est / max(tc,1), max(tc,1) / est). est>0 가정."""
    tc = max(float(true_card), 1.0)
    return float(max(est / tc, tc / est))


def estimate_bernoulli(
    rng: np.random.Generator,
    vectors: np.ndarray,
    query_emb: np.ndarray,
    sel_rows: pd.DataFrame,
    sample_size: int,
) -> list[dict]:
    """uniform random sample 추출 후 6 selectivity 일괄 평가.

    Exqutor L1228 cnt clamp: cnt=0 → cnt=1. 동치 공식 (Stage 4 Python 패턴).
    """
    n = vectors.shape[0]
    s = min(sample_size, n)
    chosen_idx = rng.choice(n, size=s, replace=False)
    chosen_vecs = vectors[chosen_idx]
    d = np.linalg.norm(chosen_vecs - query_emb, axis=1)
    out = []
    for _, row in sel_rows.iterrows():
        D = float(row["D_target"])
        true_card = int(row["true_cardinality"])
        cnt_raw = int((d < D).sum())
        cnt_clamped = cnt_raw if cnt_raw > 0 else 1  # Exqutor L1228
        est = float(cnt_clamped) * n / s              # Exqutor L1232
        qerr = _q_error(est, true_card)
        out.append(
            {
                "selectivity": float(row["selectivity"]),
                "D_target": D,
                "true_card": true_card,
                "plan_rows": int(round(est)),
                "cnt_raw": cnt_raw,
                "cnt_clamped": cnt_clamped,
                "sample_size_total": s,
                "q_error": qerr,
            }
        )
    return out


def estimate_stratified(
    rng: np.random.Generator,
    strat_vecs: dict[int, np.ndarray],
    strat_n: dict[int, int],
    n_strata: int,
    sample_budget: np.ndarray,
    query_emb: np.ndarray,
    sel_rows: pd.DataFrame,
) -> list[dict]:
    """
    stratum 별 균등 sample 추출 후 Horvitz-Thompson estimator.
    같은 stratified sample 을 6 selectivity 모두에 재사용.

    Exqutor L1228 의 cnt clamp 를 stratified 로 일반화: cnt_total = 0 인
    경우, 가상 1 hit 가 어느 stratum 에 있는지 모르므로 *active stratum 의
    weight 평균* 으로 fallback. 균등 stratum 균등 sample 에서는 N/S 와
    동일하므로 bernoulli 의 cnt clamp 결과와 정확히 일치한다.
    """
    chunks = []
    chunk_strat = []
    actual_sizes = np.zeros(n_strata, dtype=np.int32)
    for i in range(n_strata):
        n_i = strat_n[i]
        if n_i == 0:
            continue
        s_i = int(min(sample_budget[i], n_i))
        actual_sizes[i] = s_i
        if s_i == 0:
            continue
        idx = rng.choice(n_i, size=s_i, replace=False)
        chunks.append(strat_vecs[i][idx])
        chunk_strat.append(np.full(s_i, i, dtype=np.int16))
    chosen_vecs = (
        np.concatenate(chunks, axis=0) if chunks else np.empty((0, query_emb.shape[0]))
    )
    chosen_strat = (
        np.concatenate(chunk_strat) if chunk_strat else np.empty(0, dtype=np.int16)
    )
    d = np.linalg.norm(chosen_vecs - query_emb, axis=1)
    s_total = int(actual_sizes.sum())

    # cnt_total=0 fallback weight (active stratum weight 평균)
    active = [i for i in range(n_strata) if actual_sizes[i] > 0]
    if active:
        weight_mean = float(
            np.mean([strat_n[i] / float(actual_sizes[i]) for i in active])
        )
    else:
        weight_mean = 1.0

    out = []
    for _, row in sel_rows.iterrows():
        D = float(row["D_target"])
        true_card = int(row["true_cardinality"])
        below = d < D
        est_raw = 0.0
        cnt_total = 0
        for i in range(n_strata):
            s_i = int(actual_sizes[i])
            if s_i == 0:
                continue
            mask_i = chosen_strat == i
            cnt_i = int(np.sum(below & mask_i))
            cnt_total += cnt_i
            est_raw += (strat_n[i] / s_i) * cnt_i
        # Exqutor L1228 stratified 일반화
        if cnt_total == 0:
            est_raw = weight_mean
            cnt_clamped = 1
        else:
            cnt_clamped = cnt_total
        est = est_raw  # float; q_error 계산에서 직접 사용
        qerr = _q_error(est, true_card)
        out.append(
            {
                "selectivity": float(row["selectivity"]),
                "D_target": D,
                "true_card": true_card,
                "plan_rows": int(round(est)),
                "cnt_raw": cnt_total,
                "cnt_clamped": cnt_clamped,
                "sample_size_total": s_total,
                "q_error": qerr,
            }
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    ap.add_argument("--out-prefix", default="phase6_strat_pca")
    ap.add_argument("--sample-size", type=int, default=SAMPLE_SIZE_DEFAULT)
    ap.add_argument("--n-strata", type=int, default=N_STRATA_DEFAULT)
    ap.add_argument("--n-seeds", type=int, default=N_SEEDS_DEFAULT)
    args = ap.parse_args()

    log(
        f"Phase 6 Python counterfactual start — sample_size={args.sample_size}, "
        f"n_strata={args.n_strata}, n_seeds={args.n_seeds}"
    )

    # --- 데이터 로드 -----------------------------------------------------
    t0 = time.time()
    _, subset = load_parquet_vectors(f"{args.in_dir}/subset_1m.parquet")
    _, queries = load_parquet_vectors(f"{args.in_dir}/query_pool.parquet")
    qs = pq.read_table(f"{args.in_dir}/query_selectivity.parquet").to_pandas()
    log(
        f"loaded subset {subset.shape}, queries {queries.shape}, "
        f"selectivity_table {qs.shape} ({time.time()-t0:.1f}s)"
    )

    # --- Layer 정의 (1회) -----------------------------------------------
    t1 = time.time()
    proj, pca_info = compute_first_pc(subset)
    log(
        f"first PC computed (eigval[-1]={pca_info['first_eigval']:.4f}, "
        f"EVR1={pca_info['explained_var_ratio_pc1']:.4f}) ({time.time()-t1:.1f}s)"
    )

    t2 = time.time()
    stratum_id, edges, sizes = define_strata_pca_decile(proj, args.n_strata)
    strat_vecs, strat_n = build_strata_index(subset, stratum_id, args.n_strata)
    log(
        f"strata defined: K={args.n_strata}, sizes_min={int(sizes.min())}, "
        f"sizes_max={int(sizes.max())}, sizes_std={float(sizes.std()):.1f} "
        f"({time.time()-t2:.1f}s)"
    )

    sample_budget = split_sample_budget(args.sample_size, args.n_strata)
    log(f"sample budget per stratum: {sample_budget.tolist()}")

    # --- counterfactual measurement -----------------------------------
    t3 = time.time()
    n_queries = queries.shape[0]
    rows = []
    for seed in range(args.n_seeds):
        rng_b = np.random.default_rng(1000 + seed)
        rng_s = np.random.default_rng(2000 + seed)
        for q_idx in range(n_queries):
            sel_rows = qs[qs["query_id"] == q_idx].sort_values("selectivity")
            if len(sel_rows) == 0:
                continue
            # bernoulli mode
            for r in estimate_bernoulli(
                rng_b, subset, queries[q_idx], sel_rows, args.sample_size
            ):
                rows.append({"mode": "bernoulli", "seed": seed, "query_id": q_idx, **r})
            # stratified mode
            for r in estimate_stratified(
                rng_s,
                strat_vecs,
                strat_n,
                args.n_strata,
                sample_budget,
                queries[q_idx],
                sel_rows,
            ):
                rows.append({"mode": "stratified", "seed": seed, "query_id": q_idx, **r})
        log(f"  seed {seed+1}/{args.n_seeds} done ({time.time()-t3:.1f}s)")
    log(f"counterfactual measurements done ({time.time()-t3:.1f}s, {len(rows)} rows)")

    # --- 결과 저장 -------------------------------------------------------
    df = pd.DataFrame(rows)
    out_parquet = f"{args.in_dir}/{args.out_prefix}_runs.parquet"
    df.to_parquet(out_parquet, index=False)
    log(f"saved {out_parquet} ({len(df)} rows)")

    # --- seed 평균 + paired Wilcoxon -----------------------------------
    df_mean = (
        df.groupby(["mode", "query_id", "selectivity"], as_index=False)["q_error"]
        .mean()
        .rename(columns={"q_error": "q_error_mean"})
    )
    bern = df_mean[df_mean["mode"] == "bernoulli"][
        ["query_id", "selectivity", "q_error_mean"]
    ].rename(columns={"q_error_mean": "qe_bern"})
    strat = df_mean[df_mean["mode"] == "stratified"][
        ["query_id", "selectivity", "q_error_mean"]
    ].rename(columns={"q_error_mean": "qe_strat"})
    paired = bern.merge(strat, on=["query_id", "selectivity"])
    log(f"paired matrix {paired.shape}")

    selectivities = sorted(paired["selectivity"].unique())
    cmp_rows = []
    for sel in selectivities:
        sub = paired[paired["selectivity"] == sel].dropna(subset=["qe_bern", "qe_strat"])
        if len(sub) < 5:
            continue
        b = sub["qe_bern"].values
        s = sub["qe_strat"].values
        med_b, med_s = float(np.median(b)), float(np.median(s))
        mean_b, mean_s = float(np.mean(b)), float(np.mean(s))
        diff_pct = ((med_b - med_s) / med_b * 100.0) if med_b > 0 else float("nan")
        # 대립가설: stratified < bernoulli (stratified 가 더 정확)
        try:
            res = sst.wilcoxon(s, b, alternative="less", zero_method="wilcox")
            w_stat, p_val = float(res.statistic), float(res.pvalue)
        except (ValueError, TypeError) as e:
            w_stat, p_val = float("nan"), float("nan")
        n_strat_better = int(np.sum(s < b))
        n_bern_better = int(np.sum(s > b))
        n_tie = int(np.sum(s == b))
        cmp_rows.append(
            {
                "selectivity": float(sel),
                "n": int(len(sub)),
                "median_bernoulli": med_b,
                "median_stratified": med_s,
                "diff_pct_med": diff_pct,
                "mean_bernoulli": mean_b,
                "mean_stratified": mean_s,
                "wilcoxon_W": w_stat,
                "p_strat_less_bern": p_val,
                "n_strat_better": n_strat_better,
                "n_bern_better": n_bern_better,
                "n_tie": n_tie,
            }
        )

    out_compare = f"{args.in_dir}/{args.out_prefix}_compare.json"
    with open(out_compare, "w") as f:
        json.dump(
            {
                "kst": kst_now(),
                "args": vars(args),
                "n_paired": int(len(paired)),
                "selectivities": [float(s) for s in selectivities],
                "compare_per_sel": cmp_rows,
            },
            f,
            indent=2,
        )
    log(f"saved {out_compare} ({len(cmp_rows)} sel rows)")

    # --- meta -----------------------------------------------------------
    meta = {
        "kst": kst_now(),
        "args": vars(args),
        "elapsed_s": round(time.time() - t0, 2),
        "subset_shape": list(subset.shape),
        "n_queries": int(n_queries),
        "pca_info": pca_info,
        "strata_sizes": [int(x) for x in sizes],
        "strata_edges": [float(x) for x in edges],
        "sample_budget_per_stratum": [int(x) for x in sample_budget],
        "n_runs": int(len(rows)),
    }
    out_meta = f"{args.in_dir}/{args.out_prefix}_meta.json"
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    log(f"saved {out_meta}")

    # --- data-side strata 캐시 (1차 layer 산출물) ---------------------
    strata_table = pa.table(
        {
            "row_idx": np.arange(stratum_id.shape[0], dtype=np.int32),
            "stratum_id": stratum_id.astype(np.int16),
            "first_pc_proj": proj,
        }
    )
    out_strata = f"{args.in_dir}/data_side_strata_pca.parquet"
    pq.write_table(strata_table, out_strata)
    log(f"saved {out_strata} ({stratum_id.shape[0]} rows)")

    # --- 콘솔 요약 -----------------------------------------------------
    print()
    print("=== Strata size distribution ===")
    for i, s in enumerate(sizes):
        print(f"  stratum {i:2d}: n={int(s):>7d}  budget={int(sample_budget[i])}")
    print()
    print(f"=== paired Wilcoxon (alternative: stratified < bernoulli) ===")
    print(
        f"{'sel':>7s}  {'med_BERN':>9s}  {'med_STRAT':>10s}  {'diff%':>7s}  "
        f"{'p':>10s}  {'S<B':>4s}  {'S>B':>4s}  {'tie':>4s}"
    )
    for r in cmp_rows:
        sig = " *" if r["p_strat_less_bern"] is not None and r["p_strat_less_bern"] < 0.05 else ""
        print(
            f"{r['selectivity']:>7.3f}  {r['median_bernoulli']:>9.4f}  "
            f"{r['median_stratified']:>10.4f}  {r['diff_pct_med']:>+7.2f}  "
            f"{r['p_strat_less_bern']:>10.4g}  {r['n_strat_better']:>4d}  "
            f"{r['n_bern_better']:>4d}  {r['n_tie']:>4d}{sig}"
        )
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
