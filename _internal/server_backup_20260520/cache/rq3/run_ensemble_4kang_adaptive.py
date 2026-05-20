#!/usr/bin/env python3
"""
RQ3 ⭐⭐⭐ — Ensemble: 4강 stratification + Exqutor Adaptive Sampling dynamic budget.

5/8 박세은 팀장 결정 + V5 audit 권장 (~5h, 5/27 발표 contribution 추가):
    "4강 stratification + Adaptive dynamic budget" 의 ensemble 가 단순 4강
    (고정 budget=385) 또는 단순 Adaptive (no stratification) 보다 우월할 수 있다.
    sample size 동적 조정 (Exqutor) × 분포 인지 stratification (본 연구) 결합.

구조:
    1. base_method (HDBSCAN / MB_partial / Hilbert / sparse_rp) 의 fit + assign
       으로 stratum_id 부여 (학습 분포 정보).
    2. cluster 별 LIMIT 500 sample 캐시 (cache_cluster_samples_inmem, 4강과 동일).
    3. AdaptiveState (식 1~6) 가 매 50 query 마다 total budget S_t 갱신.
    4. cluster 별 sample size = S_t × proportional weight (cluster N_i / total N).
    5. estimator: stratified HT 외삽 (run_method_measurement 의 stratified_estimate
       와 동일, alloc 만 매 query 동적).

paired alignment:
    동일 (cell × seed × sel × query_id) 격자 → run_adaptive_sampling.py 와
    inner-join Δ% 계산 가능. mode 컬럼: 'ensemble_<base>'.

산출:
    rq3_<DATASET>_sf<N>_ensemble_<base>.parquet (cache/rq1/)
    columns: dataset, mode, base_method, selectivity, seed, query_id, D_target,
             true_card, est, q_error, sample_size_used, total_sample_size

CLI:
    # 단일 cell × base_method
    python3 run_ensemble_4kang_adaptive.py --dataset DEEP --sf 1 --base-method hdbscan
    python3 run_ensemble_4kang_adaptive.py --dataset SIFT --sf 10 --base-method minibatch_partial

    # dry-run
    python3 run_ensemble_4kang_adaptive.py --dataset DEEP --sf 1 --base-method hdbscan \\
        --num-queries 1 --num-seeds 1 --selectivity 0.10

서버 launch (cell × base loop):
    nohup bash launch_ensemble_4kang_adaptive.sh \\
        > /mnt/hdd0/home/capstone2026/logs/ensemble_launcher_20260508.log 2>&1 &
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hilbert"))

import _measure_common as mc  # noqa: E402
from _measure_common import (  # noqa: E402
    CACHE_PER_CLUSTER,
    N_STRATA,
    SAMPLE_SIZE,
    SEEDS as DEFAULT_SEEDS,
    SELECTIVITIES as DEFAULT_SELECTIVITIES,
    cache_cluster_samples_inmem,
    fetch_all_vectors_safe,
    kst,
)
from run_adaptive_sampling import AdaptiveState, CELLS, build_dataset_entry  # noqa: E402

try:
    import pyarrow.parquet as pq
except ImportError:
    pq = None


# ---------------------------------------------------------------------------
# base_method dispatch — 4강의 fit + assign 만 import (학습 분포 정보)
# ---------------------------------------------------------------------------

def fit_assign_base(base_method: str, all_vecs: np.ndarray, *,
                     learn_frac: float, learn_seed: int) -> tuple[np.ndarray, dict]:
    """4강 base_method 로 stratum_id 부여.

    각 method 의 run_*.py 에서 fit + assign 호출 패턴 정확 mirror.

    Returns:
        stratum_ids: (N,) int — cluster 할당
        diag: 학습 진단 정보 (elapsed_s, learn_n, etc.)
    """
    n = all_vecs.shape[0]
    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    rng = np.random.default_rng(learn_seed)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    learn_samples = all_vecs[learn_idx]
    diag = {"learn_n": int(n_learn), "learn_seed": int(learn_seed),
            "learn_frac": float(learn_frac), "n_total": int(n)}

    t0 = time.time()
    if base_method == "hdbscan":
        from hdbscan.hdbscan_partition import (assign_hdbscan, fit_hdbscan)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mapper = fit_hdbscan(learn_samples, n_strata=N_STRATA,
                                  min_cluster_size=50, seed=learn_seed)
        stratum_ids = assign_hdbscan(mapper, all_vecs)

    elif base_method == "minibatch_partial":
        from offline_simple.minibatch_partial import (
            assign_minibatch, train_minibatch_partial,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            result = train_minibatch_partial(
                learn_samples, n_clusters=N_STRATA,
                chunk_size=1000, random_state=learn_seed,
            )
        stratum_ids = assign_minibatch(result, all_vecs)

    elif base_method == "hilbert":
        from hilbert.hilbert_curve import (assign_hilbert, fit_hilbert_mapper)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            mapper = fit_hilbert_mapper(learn_samples, n_strata=N_STRATA,
                                         p=10, seed=learn_seed)
            stratum_ids = assign_hilbert(mapper, all_vecs)

    elif base_method == "sparse_rp":
        from sparserp.sparse_random_projection import (assign_sparse_rp, fit_sparse_rp)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            matrix = fit_sparse_rp(all_vecs.shape[1], n_strata=N_STRATA,
                                    seed=learn_seed)
        stratum_ids = assign_sparse_rp(matrix, all_vecs, k=N_STRATA)

    elif base_method == "minibatch":
        from offline_simple.minibatch_kmeans import (
            assign_minibatch, train_minibatch_kmeans,
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            model = train_minibatch_kmeans(
                learn_samples, n_clusters=N_STRATA, batch_size=1000,
                random_state=learn_seed,
            )
        stratum_ids = assign_minibatch(model, all_vecs)

    elif base_method == "gmm":
        from gmm.gmm_partition import assign_gmm, fit_gmm
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mapper = fit_gmm(learn_samples, n_strata=N_STRATA, seed=learn_seed)
        stratum_ids = assign_gmm(mapper, all_vecs)

    elif base_method == "faiss_ivf":
        try:
            import faiss
            d = all_vecs.shape[1]
            quantizer = faiss.IndexFlatL2(d)
            index = faiss.IndexIVFFlat(quantizer, d, N_STRATA)
            index.train(np.ascontiguousarray(learn_samples.astype(np.float32)))
            quant_index = index.quantizer
            _, I = quant_index.search(
                np.ascontiguousarray(all_vecs.astype(np.float32)), 1,
            )
            stratum_ids = I[:, 0].astype(np.int32)
        except ImportError:
            from sklearn.cluster import MiniBatchKMeans
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                m = MiniBatchKMeans(
                    n_clusters=N_STRATA, batch_size=1000, random_state=learn_seed,
                ).fit(learn_samples)
            stratum_ids = m.predict(all_vecs).astype(np.int32)

    elif base_method == "reservoir":
        # inline reservoir (measure_multi_paradigm._fit_reservoir 와 동일 패턴)
        from sklearn.neighbors import NearestNeighbors
        rng_r = np.random.default_rng(learn_seed)
        idx = rng_r.choice(learn_samples.shape[0], size=N_STRATA, replace=False)
        centroids = learn_samples[idx]
        nn = NearestNeighbors(n_neighbors=1).fit(centroids)
        _, I = nn.kneighbors(all_vecs)
        stratum_ids = I[:, 0].astype(np.int32)

    elif base_method == "pca1d":
        from pca1d.pca1d_quantile import assign_pca1d, fit_pca1d_mapper
        mapper = fit_pca1d_mapper(learn_samples, n_strata=N_STRATA, seed=learn_seed)
        stratum_ids = assign_pca1d(mapper, all_vecs)

    elif base_method == "lsh":
        from lsh.lsh import assign_lsh, make_hyperplanes
        W = make_hyperplanes(dim=all_vecs.shape[1], k=N_STRATA, seed=learn_seed)
        stratum_ids = assign_lsh(W, all_vecs, k=N_STRATA)

    elif base_method == "sobol":
        from sobol.sobol_stratification import assign_sobol, fit_sobol
        mapper = fit_sobol(learn_samples, n_strata=N_STRATA, seed=learn_seed)
        stratum_ids = assign_sobol(mapper, all_vecs)

    else:
        raise SystemExit(f"unsupported --base-method: {base_method!r} "
                         "(choose: hdbscan / minibatch_partial / hilbert / sparse_rp / "
                         "minibatch / gmm / faiss_ivf / reservoir / pca1d / lsh / sobol)")

    diag["fit_assign_elapsed_s"] = round(time.time() - t0, 1)
    return stratum_ids.astype(np.int32), diag


# ---------------------------------------------------------------------------
# Adaptive total budget → cluster proportional 분배
# ---------------------------------------------------------------------------

def proportional_alloc_dynamic(sizes: dict[int, int], total_budget: int,
                                 n_strata: int = N_STRATA) -> np.ndarray:
    """매 query 마다 호출. total_budget (Adaptive S_t) 을 cluster N_i 비례 분배.

    _measure_common.proportional_alloc 와 동일 로직, budget 만 동적.
    cluster 의 cache 보다 큰 alloc 발생 가능 → estimator 에서 clip.
    """
    sz = np.array([sizes.get(j, 0) for j in range(n_strata)], dtype=float)
    if sz.sum() <= 0:
        # fallback: equal
        base = total_budget // n_strata
        extra = total_budget - base * n_strata
        s = np.full(n_strata, base, dtype=int)
        s[:extra] += 1
        return np.maximum(s, 1)
    f = sz / sz.sum() * total_budget
    s = np.maximum(f.astype(int), 1)
    extra = total_budget - int(s.sum())
    if extra > 0:
        frac = f - f.astype(int)
        idx = np.argsort(-frac)[:extra]
        s[idx] += 1
    return s


def stratified_estimate_dynamic(samples, sizes, alloc, qvec, D, rng,
                                  n_strata: int = N_STRATA) -> tuple[float, int]:
    """alloc 분배 (매 query 동적) 로 stratified HT 외삽.

    _measure_common.stratified_estimate 와 동일 로직, 추가로 실제 사용한
    sample size sum 반환 (alloc 의 cluster cache clip 후 합).
    """
    est = 0.0
    used = 0
    for sid in range(n_strata):
        s_i = int(alloc[sid])
        cache = samples[sid]
        n_cache = cache.shape[0]
        s_i = min(s_i, n_cache)
        if s_i < 1:
            s_i = 1
        idxs = rng.choice(n_cache, size=s_i, replace=False)
        sub = cache[idxs]
        d = np.linalg.norm(sub - qvec, axis=1)
        hits = int((d < D).sum())
        weight = sizes.get(sid, 0) / s_i
        est += hits * weight
        used += s_i
    return float(est), used


# ---------------------------------------------------------------------------
# Main 측정 — 단일 cell × 단일 base_method
# ---------------------------------------------------------------------------

def run_ensemble_measurement(
    all_vecs: np.ndarray,
    stratum_ids: np.ndarray,
    ds: dict,
    *,
    base_method: str,
    selectivities: list,
    seeds: list,
    n_queries: int = 100,
    state_kwargs: dict | None = None,
    cache_seed: int = 42,
) -> tuple[list[dict], dict]:
    """단일 cell × base_method ensemble 측정.

    매 query 마다:
      1. AdaptiveState.step(prev_qerror) → 다음 total budget S_t
      2. proportional_alloc_dynamic(sizes, S_t) → cluster 별 sample size
      3. stratified_estimate_dynamic(...) → est + used sample size
      4. Q-error 계산 + state.step 에 feedback
    """
    if pq is None:
        raise RuntimeError("pyarrow not available — cannot read query_pool parquet")

    samples, sizes = cache_cluster_samples_inmem(all_vecs, stratum_ids, seed=cache_seed)
    n_total = sum(sizes.values())
    print(f"[{kst()}]   stratum sizes (min/mean/max): "
          f"{min(sizes.values())} / {n_total // N_STRATA} / {max(sizes.values())}")

    qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
    qs_full = pq.read_table(ds["query_sel"]).to_pandas()
    qvecs = np.stack([
        np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
        for i in range(len(qp))
    ])
    print(f"[{kst()}]   loaded {len(qp)} queries (dim={qvecs.shape[1]})")

    method = f"ensemble_{base_method}"
    rows: list[dict] = []
    final_sizes_per_seed: dict = {}

    base_kwargs = {
        "momentum": 0.9, "learning_rate": 0.1, "alpha": 50.0,
        "beta": 1.5, "gamma": 0.99, "update_period": 50,
        "min_size": 50,
        "max_size": min(5000, n_total),
    }
    if state_kwargs:
        base_kwargs.update(state_kwargs)

    for sel in selectivities:
        qs_sel = qs_full[
            (np.isclose(qs_full["selectivity"], sel)) &
            (qs_full["query_id"] < n_queries)
        ].sort_values("query_id").reset_index(drop=True)
        if len(qs_sel) == 0:
            print(f"[{kst()}]   WARNING: sel={sel} 에 해당 query 없음 (skip)")
            continue

        for seed in seeds:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            state = AdaptiveState(**base_kwargs)
            total_budget = SAMPLE_SIZE  # 첫 query 는 식 1 의 N=385

            t0 = time.time()
            qe_list = []
            size_trace = []

            for _, row in qs_sel.iterrows():
                qid = int(row["query_id"])
                D = float(row["D_target"])
                true_card = int(row["true_cardinality"])
                qvec = qvecs[qid]

                alloc = proportional_alloc_dynamic(sizes, total_budget)
                est, used = stratified_estimate_dynamic(
                    samples, sizes, alloc, qvec, D, rng,
                )
                if est > 0 and true_card > 0:
                    qerr = max(est / true_card, true_card / est)
                else:
                    qerr = None

                rows.append({
                    "dataset": ds["name"],
                    "mode": method,
                    "base_method": base_method,
                    "selectivity": sel,
                    "seed": seed,
                    "query_id": qid,
                    "D_target": D,
                    "true_card": true_card,
                    "est": est,
                    "q_error": qerr,
                    "sample_size_used": used,
                    "total_sample_size": int(total_budget),
                })
                qe_list.append(qerr if qerr is not None else float("nan"))
                size_trace.append(used)

                # Adaptive state 갱신 (50 query 마다 budget 변동)
                total_budget = state.step(qerr)

            elapsed = time.time() - t0
            valid = sum(1 for q in qe_list if q == q)
            med = float(np.nanmedian(qe_list)) if valid else float("nan")
            mean_size = float(np.mean(size_trace)) if size_trace else float("nan")
            final_sizes_per_seed[(sel, seed)] = {
                "final_total_budget": int(round(state.sample_size)),
                "mean_sample_size_used": mean_size,
                "final_velocity": state.velocity,
                "final_learning_rate": state.learning_rate,
            }
            print(
                f"[{kst()}]   {ds['name']} {method:>26} s={sel:.2f} seed={seed} "
                f"({elapsed*1000:.0f}ms) valid={valid}/{len(qs_sel)} "
                f"med_qe={med:.4f} mean_size={mean_size:.1f}"
            )

    summary = {
        "n_rows": len(rows),
        "base_method": base_method,
        "n_total_rows_in_table": n_total,
        "final_sizes_per_seed": {
            f"sel={k[0]}_seed={k[1]}": v for k, v in final_sizes_per_seed.items()
        },
    }
    return rows, summary


# ---------------------------------------------------------------------------
# Output saving
# ---------------------------------------------------------------------------

def _save_outputs(rows: list[dict], *, out_path: Path, meta_path: Path,
                   extra_meta: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_parquet(out_path, index=False)
    print(f"[{kst()}] saved {out_path} ({len(df):,} rows)")

    if not df.empty:
        smry = df.groupby(["dataset", "mode", "selectivity"])["q_error"].agg(
            ["mean", "std", "median", "count"]
        ).round(4)
        print(f"\n=== mean q_error per (dataset × mode × sel) ===\n{smry}")

    meta = {
        "kst": kst(),
        "n_rows": len(df),
        "modes": sorted(df["mode"].unique().tolist()) if not df.empty else [],
        "datasets": sorted(df["dataset"].unique().tolist()) if not df.empty else [],
    }
    meta.update(extra_meta)
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2, default=str)
    print(f"[{kst()}] saved {meta_path}")


# ---------------------------------------------------------------------------
# CLI entrypoint — single (cell × base_method)
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="RQ3 ⭐⭐⭐ Ensemble: 4강 stratification × Adaptive dynamic budget"
    )
    ap.add_argument("--dataset", required=True,
                    choices=['DEEP', 'SIFT', 'SSN', 'YFCC', 'WIKI', 'YFCC_DL'],
                    help="Dataset (single cell).")
    ap.add_argument("--sf", type=int, required=True, choices=[1, 10, 100],
                    help="Scale factor (single cell).")
    ap.add_argument("--base-method", required=True,
                    choices=['hdbscan', 'minibatch_partial', 'hilbert', 'sparse_rp',
                             'minibatch', 'gmm', 'faiss_ivf', 'reservoir',
                             'pca1d', 'lsh', 'sobol'],
                    help="4강 base method (학습 stratification).")
    ap.add_argument("--port", type=int, default=55435,
                    help="PostgreSQL port (default 55435 = vanilla).")
    ap.add_argument("--selectivity", nargs="*", type=float,
                    default=DEFAULT_SELECTIVITIES,
                    help=f"Selectivity grid (default {DEFAULT_SELECTIVITIES}).")
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--num-seeds", type=int, default=len(DEFAULT_SEEDS))
    ap.add_argument("--num-queries", type=int, default=100)

    # 학습 hyperparam (4강 default 와 동일)
    ap.add_argument("--learn-frac", type=float, default=0.01,
                    help="base_method 학습 sample 비율 (default 1%%).")
    ap.add_argument("--learn-seed", type=int, default=42)

    # AdaptiveState hyperparam (run_adaptive_sampling.py 와 동일 default)
    ap.add_argument("--momentum", type=float, default=0.9)
    ap.add_argument("--lr0", type=float, default=0.1)
    ap.add_argument("--alpha", type=float, default=50.0)
    ap.add_argument("--beta", type=float, default=1.5)
    ap.add_argument("--gamma", type=float, default=0.99)
    ap.add_argument("--update-period", type=int, default=50)
    ap.add_argument("--min-size", type=int, default=50)
    ap.add_argument("--max-size", type=int, default=5000)

    ap.add_argument("--out-dir", type=Path,
                    default=Path('/mnt/hdd0/home/capstone2026/cache/rq1'),
                    help="parquet + meta 저장 디렉토리 (4강과 동일 경로).")
    ap.add_argument("--out-prefix", default=None,
                    help="parquet basename. 미지정 시 "
                         "rq3_<DS>_sf<N>_ensemble_<base> 자동 생성.")

    args = ap.parse_args()

    # seed 슬라이싱
    end = args.seed_start + args.num_seeds
    seeds = DEFAULT_SEEDS[args.seed_start:end]
    if not seeds:
        raise SystemExit(f"empty seeds: --seed-start={args.seed_start} "
                         f"--num-seeds={args.num_seeds}")

    # === cell config 조립 (run_adaptive_sampling.py 의 build_dataset_entry mirror)
    DS = build_dataset_entry(args.dataset, args.sf)
    mc.DATASETS = [DS]
    mc.PORT = args.port
    mc.SELECTIVITIES = list(args.selectivity)

    cell_label = f"{args.dataset}-SF{args.sf}"
    print(f"[{kst()}] === Ensemble (4강 × Adaptive) — base={args.base_method} ===")
    print(f"[{kst()}] cell: {cell_label} ({DS['table']}, dim={DS['vec_dim']})")
    print(f"[{kst()}] query_pool: {DS['query_pool']}")
    print(f"[{kst()}] query_sel:  {DS['query_sel']}")
    print(f"[{kst()}] sel={args.selectivity}, seeds={seeds}, "
          f"n_queries={args.num_queries}")
    print(f"[{kst()}] base_method: {args.base_method} "
          f"(learn_frac={args.learn_frac}, learn_seed={args.learn_seed})")
    print(f"[{kst()}] adaptive: m={args.momentum}, η₀={args.lr0}, "
          f"α={args.alpha}, β={args.beta}, γ={args.gamma}, "
          f"period={args.update_period}, init_N={SAMPLE_SIZE}")

    state_kwargs = {
        "momentum": args.momentum, "learning_rate": args.lr0,
        "alpha": args.alpha, "beta": args.beta, "gamma": args.gamma,
        "update_period": args.update_period,
        "min_size": args.min_size, "max_size": args.max_size,
    }

    t_total = time.time()

    # 1. 전체 vector fetch
    print(f"\n[{kst()}] === fetch_all_vectors_safe ===")
    all_vecs, _km20_sids = fetch_all_vectors_safe(DS)

    # 2. base_method 학습 + assign
    print(f"\n[{kst()}] === fit + assign ({args.base_method}) ===")
    stratum_ids, fit_diag = fit_assign_base(
        args.base_method, all_vecs,
        learn_frac=args.learn_frac, learn_seed=args.learn_seed,
    )
    cluster_min = int((np.bincount(stratum_ids, minlength=N_STRATA)).min())
    cluster_max = int((np.bincount(stratum_ids, minlength=N_STRATA)).max())
    print(f"[{kst()}]   {args.base_method} cluster sizes: min={cluster_min}, "
          f"max={cluster_max}, max/min={cluster_max / max(1, cluster_min):.2f}, "
          f"learn elapsed: {fit_diag['fit_assign_elapsed_s']}s")

    # 3. ensemble measurement
    print(f"\n[{kst()}] === ensemble measurement ===")
    rows, summary = run_ensemble_measurement(
        all_vecs, stratum_ids, DS,
        base_method=args.base_method,
        selectivities=args.selectivity,
        seeds=seeds,
        n_queries=args.num_queries,
        state_kwargs=state_kwargs,
    )

    # 4. output
    if args.out_prefix:
        base = args.out_prefix
    else:
        base = f"rq3_{args.dataset}_sf{args.sf}_ensemble_{args.base_method}"
    out_pq = args.out_dir / f"{base}.parquet"
    out_meta = args.out_dir / f"{base}_meta.json"

    cell_meta = {
        "method": (f"Ensemble (4강 × Adaptive) — "
                   f"base={args.base_method}, dynamic budget"),
        "base_method": args.base_method,
        "fit_diag": fit_diag,
        "cluster_min": cluster_min,
        "cluster_max": cluster_max,
        "hyperparameters": {
            "m": args.momentum, "eta0": args.lr0,
            "alpha": args.alpha, "beta": args.beta,
            "gamma": args.gamma, "update_period": args.update_period,
            "init_N": SAMPLE_SIZE,
            "min_size": args.min_size, "max_size": args.max_size,
            "learn_frac": args.learn_frac, "learn_seed": args.learn_seed,
            "cache_per_cluster": CACHE_PER_CLUSTER,
            "n_strata": N_STRATA,
        },
        "n_queries": args.num_queries,
        "selectivities": list(args.selectivity),
        "seeds": list(seeds),
        "cell": cell_label,
        "table": DS["table"],
        "vec_dim": DS["vec_dim"],
        "elapsed_s": round(time.time() - t_total, 1),
        "summary": summary,
    }
    _save_outputs(rows, out_path=out_pq, meta_path=out_meta,
                  extra_meta=cell_meta)

    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
