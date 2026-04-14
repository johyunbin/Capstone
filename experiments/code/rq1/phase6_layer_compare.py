#!/usr/bin/env python3
"""
RQ1 Phase 6 Step 3' — Layer 비교 (PCA decile vs k-means K=10/20)

Phase 6 Step 1~3 (PCA decile) 의 +0.7~0.8% 효과 위에서, 더 강한 layer
후보를 비교한다. 본 스크립트는 *4 mode 동시 측정* 으로 paired 비교에서
RNG noise 를 제거한다 (같은 query × 같은 selectivity × 같은 5 seed 안에서
4 mode 동시 평가).

4 mode:
  - bernoulli       : layer 없음, uniform random sample 385 행
  - pca_decile      : Phase 6 Step 1~3 의 첫 PC quantile decile, 10 stratum
  - kmeans_k10      : numpy mini-batch k-means K=10, 1M × 96
  - kmeans_k20      : numpy mini-batch k-means K=20, 1M × 96

각 mode 100 query × 6 selectivity × 5 seed = 3 000 측정. 총 12 000 row long-form.
estimator 는 Phase 6 Step 1~3 의 함수와 정확 동일 (Exqutor L1228 cnt clamp +
L1232 공식). bernoulli 는 §VII.2 에서 동치성 검증된 baseline.

서버 사용 위치:
  /mnt/hdd0/home/capstone2026/cache/rq1_phase6_layer_compare.py
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

SAMPLE_SIZE_DEFAULT = 385
N_SEEDS_DEFAULT = 5


def kst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")


def log(msg: str) -> None:
    print(f"[{kst_now()}] {msg}", flush=True)


# ---- 데이터 로드 -----------------------------------------------------------


def load_parquet_vectors(path: str) -> tuple[np.ndarray, np.ndarray]:
    table = pq.read_table(path)
    pks = np.asarray(table.column("ps_partkey").to_numpy(), dtype=np.int32)
    emb_col = table.column("embedding").combine_chunks()
    flat = emb_col.flatten().to_numpy(zero_copy_only=False)
    n = len(pks)
    dim = len(flat) // n
    vecs = flat.reshape(n, dim).astype(np.float32, copy=False)
    return pks, vecs


# ---- Layer 정의 함수 -------------------------------------------------------


def build_layer_pca_decile(
    vectors: np.ndarray, n_strata: int = 10
) -> tuple[np.ndarray, dict]:
    """첫 PCA component decile (Phase 6 Step 1~3 와 동일 함수)."""
    n, dim = vectors.shape
    mean = vectors.mean(axis=0, dtype=np.float64)
    centered = vectors.astype(np.float64) - mean
    cov = (centered.T @ centered) / (n - 1)
    eigvals, eigvecs = np.linalg.eigh(cov)
    first_pc = eigvecs[:, -1]
    proj = (centered @ first_pc).astype(np.float32)
    qs = np.linspace(0, 1, n_strata + 1)[1:-1]
    edges = np.quantile(proj, qs)
    stratum_id = np.searchsorted(edges, proj, side="right").astype(np.int16)
    stratum_id = np.clip(stratum_id, 0, n_strata - 1)
    info = {
        "layer": "pca_decile",
        "n_strata": int(n_strata),
        "first_eigval": float(eigvals[-1]),
        "evr1": float(eigvals[-1] / eigvals.sum()),
        "edges": [float(e) for e in edges],
    }
    return stratum_id, info


def build_layer_kmeans(
    vectors: np.ndarray,
    k: int,
    batch_size: int = 4096,
    n_iter: int = 100,
    seed: int = 42,
) -> tuple[np.ndarray, dict]:
    """
    numpy mini-batch k-means (Sculley 2010). sklearn 의존성 제거.

    1. K random points 로 centroid init
    2. 매 iter: random batch → assign → centroid 의 running average update
    3. 학습 후 전체 N 에 대해 BLAS matmul 한 번으로 전체 assign

    1M × 96 × K=10/20 → 학습 ~수 초 + assign 1~2초.
    """
    n, dim = vectors.shape
    rng = np.random.default_rng(seed)
    init_idx = rng.choice(n, size=k, replace=False)
    centroids = vectors[init_idx].astype(np.float64).copy()
    counts = np.zeros(k, dtype=np.int64)

    t0 = time.time()
    for it in range(n_iter):
        batch_idx = rng.choice(n, size=batch_size, replace=False)
        batch = vectors[batch_idx].astype(np.float64)
        # assign: ||x||^2 + ||c||^2 - 2 x·c
        b_sq = (batch * batch).sum(axis=1)
        c_sq = (centroids * centroids).sum(axis=1)
        dots = batch @ centroids.T
        d2 = b_sq[:, None] + c_sq[None, :] - 2 * dots
        labels = np.argmin(d2, axis=1)
        # running mean update per cluster
        for kk in range(k):
            mask = labels == kk
            n_k = int(mask.sum())
            if n_k == 0:
                continue
            counts[kk] += n_k
            eta = n_k / counts[kk]
            centroids[kk] = (1 - eta) * centroids[kk] + eta * batch[mask].mean(axis=0)
    t_train = time.time() - t0

    # 전체 assign — BLAS matmul 한 번 (1M × 96 × K)
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


# ---- estimator (Phase 6 Step 1~3 의 함수와 정확 동일) ---------------------


def _q_error(est: float, true_card: int) -> float:
    tc = max(float(true_card), 1.0)
    return float(max(est / tc, tc / est))


def estimate_bernoulli(
    rng: np.random.Generator,
    vectors: np.ndarray,
    query_emb: np.ndarray,
    sel_rows: pd.DataFrame,
    sample_size: int,
) -> list[dict]:
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
        cnt_clamped = cnt_raw if cnt_raw > 0 else 1
        est = float(cnt_clamped) * n / s
        out.append(
            {
                "selectivity": float(row["selectivity"]),
                "true_card": true_card,
                "plan_rows": int(round(est)),
                "cnt_raw": cnt_raw,
                "q_error": _q_error(est, true_card),
            }
        )
    return out


def split_sample_budget(sample_size: int, n_strata: int) -> np.ndarray:
    base = sample_size // n_strata
    rem = sample_size - base * n_strata
    sizes = np.full(n_strata, base, dtype=np.int32)
    sizes[:rem] += 1
    return sizes


def build_strata_index(
    vectors: np.ndarray, stratum_id: np.ndarray, n_strata: int
) -> tuple[dict[int, np.ndarray], dict[int, int]]:
    strat_vecs: dict[int, np.ndarray] = {}
    strat_n: dict[int, int] = {}
    for i in range(n_strata):
        idx = np.where(stratum_id == i)[0]
        strat_vecs[i] = vectors[idx]
        strat_n[i] = int(len(idx))
    return strat_vecs, strat_n


def estimate_stratified(
    rng: np.random.Generator,
    strat_vecs: dict[int, np.ndarray],
    strat_n: dict[int, int],
    n_strata: int,
    sample_budget: np.ndarray,
    query_emb: np.ndarray,
    sel_rows: pd.DataFrame,
) -> list[dict]:
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

    active = [i for i in range(n_strata) if actual_sizes[i] > 0]
    weight_mean = (
        float(np.mean([strat_n[i] / float(actual_sizes[i]) for i in active]))
        if active
        else 1.0
    )

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
        if cnt_total == 0:
            est_raw = weight_mean
        out.append(
            {
                "selectivity": float(row["selectivity"]),
                "true_card": true_card,
                "plan_rows": int(round(est_raw)),
                "cnt_raw": cnt_total,
                "q_error": _q_error(est_raw, true_card),
            }
        )
    return out


# ---- 메인 ------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="/mnt/hdd0/home/capstone2026/cache/rq1")
    ap.add_argument("--out-prefix", default="phase6_layer_compare")
    ap.add_argument("--sample-size", type=int, default=SAMPLE_SIZE_DEFAULT)
    ap.add_argument("--n-seeds", type=int, default=N_SEEDS_DEFAULT)
    ap.add_argument("--kmeans-iter", type=int, default=100)
    ap.add_argument("--kmeans-batch", type=int, default=4096)
    args = ap.parse_args()

    log(
        f"Phase 6 Step 3' layer compare start — sample={args.sample_size}, "
        f"seeds={args.n_seeds}, kmeans iter={args.kmeans_iter} batch={args.kmeans_batch}"
    )

    # --- 데이터 로드 -----------------------------------------------------
    t0 = time.time()
    _, subset = load_parquet_vectors(f"{args.in_dir}/subset_1m.parquet")
    _, queries = load_parquet_vectors(f"{args.in_dir}/query_pool.parquet")
    qs = pq.read_table(f"{args.in_dir}/query_selectivity.parquet").to_pandas()
    log(
        f"loaded subset {subset.shape}, queries {queries.shape}, "
        f"selectivity {qs.shape} ({time.time()-t0:.1f}s)"
    )

    # --- Layer 정의 (3 종) ---------------------------------------------
    layer_defs = {}

    log("building layer pca_decile (K=10) ...")
    t1 = time.time()
    pca_id, pca_info = build_layer_pca_decile(subset, n_strata=10)
    layer_defs["pca_decile"] = (pca_id, pca_info)
    log(f"  pca_decile done ({time.time()-t1:.1f}s, EVR1={pca_info['evr1']:.4f})")

    for k in [10, 20]:
        log(f"building layer kmeans_k{k} ...")
        t2 = time.time()
        km_id, km_info = build_layer_kmeans(
            subset,
            k=k,
            batch_size=args.kmeans_batch,
            n_iter=args.kmeans_iter,
            seed=42,
        )
        layer_defs[f"kmeans_k{k}"] = (km_id, km_info)
        log(
            f"  kmeans_k{k} done ({time.time()-t2:.1f}s, train={km_info['t_train_s']}s, "
            f"assign={km_info['t_assign_s']}s, sizes [{km_info['size_min']},{km_info['size_max']}], "
            f"std={km_info['size_std']:.1f})"
        )

    # --- per-layer strata index ------------------------------------------
    strata_caches: dict[str, tuple] = {}
    for name, (sid, info) in layer_defs.items():
        K = info["n_strata"]
        sv, sn = build_strata_index(subset, sid, K)
        budget = split_sample_budget(args.sample_size, K)
        strata_caches[name] = (sv, sn, K, budget)

    # --- counterfactual measurement -----------------------------------
    t3 = time.time()
    n_queries = queries.shape[0]
    rows = []
    for seed in range(args.n_seeds):
        # 각 mode 별 독립 RNG (paired 의 의미는 query/sel 짝, RNG 분리)
        rng_b = np.random.default_rng(1000 + seed)
        rng_pca = np.random.default_rng(2000 + seed)
        rng_k10 = np.random.default_rng(3000 + seed)
        rng_k20 = np.random.default_rng(4000 + seed)

        for q_idx in range(n_queries):
            sel_rows = qs[qs["query_id"] == q_idx].sort_values("selectivity")
            if len(sel_rows) == 0:
                continue

            # bernoulli
            for r in estimate_bernoulli(
                rng_b, subset, queries[q_idx], sel_rows, args.sample_size
            ):
                rows.append({"mode": "bernoulli", "seed": seed, "query_id": q_idx, **r})
            # pca_decile
            sv, sn, K, budget = strata_caches["pca_decile"]
            for r in estimate_stratified(
                rng_pca, sv, sn, K, budget, queries[q_idx], sel_rows
            ):
                rows.append({"mode": "pca_decile", "seed": seed, "query_id": q_idx, **r})
            # kmeans_k10
            sv, sn, K, budget = strata_caches["kmeans_k10"]
            for r in estimate_stratified(
                rng_k10, sv, sn, K, budget, queries[q_idx], sel_rows
            ):
                rows.append({"mode": "kmeans_k10", "seed": seed, "query_id": q_idx, **r})
            # kmeans_k20
            sv, sn, K, budget = strata_caches["kmeans_k20"]
            for r in estimate_stratified(
                rng_k20, sv, sn, K, budget, queries[q_idx], sel_rows
            ):
                rows.append({"mode": "kmeans_k20", "seed": seed, "query_id": q_idx, **r})
        log(f"  seed {seed+1}/{args.n_seeds} done ({time.time()-t3:.1f}s)")
    log(f"all measurements done ({time.time()-t3:.1f}s, {len(rows)} rows)")

    # --- 결과 저장 -------------------------------------------------------
    df = pd.DataFrame(rows)
    out_runs = f"{args.in_dir}/{args.out_prefix}_runs.parquet"
    df.to_parquet(out_runs, index=False)
    log(f"saved {out_runs} ({len(df)} rows)")

    # --- seed 평균 + paired Wilcoxon (모든 mode pair) ------------------
    df_mean = (
        df.groupby(["mode", "query_id", "selectivity"], as_index=False)["q_error"]
        .mean()
        .rename(columns={"q_error": "qe_mean"})
    )

    modes = ["bernoulli", "pca_decile", "kmeans_k10", "kmeans_k20"]
    selectivities = sorted(df["selectivity"].unique())

    # mode × sel 통계
    mode_sel_stats = []
    for mode in modes:
        for sel in selectivities:
            sub = df_mean[(df_mean["mode"] == mode) & (df_mean["selectivity"] == sel)]
            mode_sel_stats.append(
                {
                    "mode": mode,
                    "selectivity": float(sel),
                    "n": int(len(sub)),
                    "median": float(sub["qe_mean"].median()),
                    "mean": float(sub["qe_mean"].mean()),
                    "std": float(sub["qe_mean"].std(ddof=1)),
                }
            )

    # paired Wilcoxon: 모든 stratified mode 를 bernoulli 와 비교
    pair_results = []
    for mode in modes:
        if mode == "bernoulli":
            continue
        for sel in selectivities:
            b = df_mean[(df_mean["mode"] == "bernoulli") & (df_mean["selectivity"] == sel)][
                ["query_id", "qe_mean"]
            ].rename(columns={"qe_mean": "qe_b"})
            m = df_mean[(df_mean["mode"] == mode) & (df_mean["selectivity"] == sel)][
                ["query_id", "qe_mean"]
            ].rename(columns={"qe_mean": "qe_m"})
            paired = b.merge(m, on="query_id")
            if len(paired) < 5:
                continue
            x = paired["qe_m"].values
            y = paired["qe_b"].values
            try:
                res = sst.wilcoxon(x, y, alternative="less", zero_method="wilcox")
                w_stat, p_val = float(res.statistic), float(res.pvalue)
            except (ValueError, TypeError):
                w_stat, p_val = float("nan"), float("nan")
            n_better = int(np.sum(x < y))
            n_worse = int(np.sum(x > y))
            n_tie = int(np.sum(x == y))
            med_b = float(np.median(y))
            med_m = float(np.median(x))
            diff_pct = ((med_b - med_m) / med_b * 100.0) if med_b > 0 else float("nan")
            pair_results.append(
                {
                    "mode": mode,
                    "vs": "bernoulli",
                    "selectivity": float(sel),
                    "n": int(len(paired)),
                    "median_bern": med_b,
                    "median_mode": med_m,
                    "diff_pct_med": diff_pct,
                    "wilcoxon_W": w_stat,
                    "p_less": p_val,
                    "n_better": n_better,
                    "n_worse": n_worse,
                    "n_tie": n_tie,
                }
            )

    # mode 간 비교 (kmeans vs pca_decile, k10 vs k20)
    cross_pair_results = []
    cross_pairs = [
        ("kmeans_k10", "pca_decile"),
        ("kmeans_k20", "pca_decile"),
        ("kmeans_k20", "kmeans_k10"),
    ]
    for left, right in cross_pairs:
        for sel in selectivities:
            l = df_mean[(df_mean["mode"] == left) & (df_mean["selectivity"] == sel)][
                ["query_id", "qe_mean"]
            ].rename(columns={"qe_mean": "qe_l"})
            r = df_mean[(df_mean["mode"] == right) & (df_mean["selectivity"] == sel)][
                ["query_id", "qe_mean"]
            ].rename(columns={"qe_mean": "qe_r"})
            paired = l.merge(r, on="query_id")
            if len(paired) < 5:
                continue
            x = paired["qe_l"].values
            y = paired["qe_r"].values
            try:
                res = sst.wilcoxon(x, y, alternative="less", zero_method="wilcox")
                w_stat, p_val = float(res.statistic), float(res.pvalue)
            except (ValueError, TypeError):
                w_stat, p_val = float("nan"), float("nan")
            n_better = int(np.sum(x < y))
            n_worse = int(np.sum(x > y))
            cross_pair_results.append(
                {
                    "left": left,
                    "right": right,
                    "selectivity": float(sel),
                    "n": int(len(paired)),
                    "median_left": float(np.median(x)),
                    "median_right": float(np.median(y)),
                    "diff_pct_med": (
                        (float(np.median(y)) - float(np.median(x))) / float(np.median(y)) * 100.0
                        if np.median(y) > 0
                        else float("nan")
                    ),
                    "wilcoxon_W": w_stat,
                    "p_left_less": p_val,
                    "n_left_better": n_better,
                    "n_left_worse": n_worse,
                }
            )

    out_compare = f"{args.in_dir}/{args.out_prefix}_compare.json"
    with open(out_compare, "w") as f:
        json.dump(
            {
                "kst": kst_now(),
                "args": vars(args),
                "modes": modes,
                "selectivities": [float(s) for s in selectivities],
                "mode_sel_stats": mode_sel_stats,
                "pairs_vs_bernoulli": pair_results,
                "cross_pairs": cross_pair_results,
                "layer_info": {
                    name: info for name, (_, info) in layer_defs.items()
                },
            },
            f,
            indent=2,
            default=str,
        )
    log(f"saved {out_compare}")

    # --- meta -----------------------------------------------------------
    meta = {
        "kst": kst_now(),
        "args": vars(args),
        "elapsed_s": round(time.time() - t0, 2),
        "n_runs": int(len(rows)),
        "n_modes": len(modes),
        "layers": {name: info for name, (_, info) in layer_defs.items()},
    }
    out_meta = f"{args.in_dir}/{args.out_prefix}_meta.json"
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    log(f"saved {out_meta}")

    # --- 콘솔 요약 -----------------------------------------------------
    print()
    print("=== mode × selectivity median q_error ===")
    print(f"{'sel':>7s}  {'BERN':>9s}  {'PCA10':>9s}  {'KM10':>9s}  {'KM20':>9s}")
    for sel in selectivities:
        vals = {}
        for mode in modes:
            row = next(
                r
                for r in mode_sel_stats
                if r["mode"] == mode and r["selectivity"] == sel
            )
            vals[mode] = row["median"]
        print(
            f"{sel:>7.3f}  {vals['bernoulli']:>9.4f}  {vals['pca_decile']:>9.4f}  "
            f"{vals['kmeans_k10']:>9.4f}  {vals['kmeans_k20']:>9.4f}"
        )

    print()
    print("=== paired Wilcoxon vs BERNOULLI (alt: mode < bernoulli) ===")
    print(
        f"{'mode':>12s}  {'sel':>7s}  {'diff%':>7s}  {'p':>10s}  {'better':>6s}  "
        f"{'worse':>5s}"
    )
    for r in pair_results:
        sig = " *" if r["p_less"] is not None and r["p_less"] < 0.05 else ""
        print(
            f"{r['mode']:>12s}  {r['selectivity']:>7.3f}  {r['diff_pct_med']:>+7.2f}  "
            f"{r['p_less']:>10.4g}  {r['n_better']:>6d}  {r['n_worse']:>5d}{sig}"
        )

    print()
    print("=== cross pair (alt: left < right) ===")
    print(
        f"{'left':>12s} vs {'right':>12s}  {'sel':>7s}  {'diff%':>7s}  {'p':>10s}  "
        f"{'L<R':>4s}  {'L>R':>4s}"
    )
    for r in cross_pair_results:
        sig = " *" if r["p_left_less"] is not None and r["p_left_less"] < 0.05 else ""
        print(
            f"{r['left']:>12s} vs {r['right']:>12s}  {r['selectivity']:>7.3f}  "
            f"{r['diff_pct_med']:>+7.2f}  {r['p_left_less']:>10.4g}  "
            f"{r['n_left_better']:>4d}  {r['n_left_worse']:>4d}{sig}"
        )

    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
