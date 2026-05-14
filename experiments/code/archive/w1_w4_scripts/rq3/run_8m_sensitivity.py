#!/usr/bin/env python3
"""
RQ3 8M sensitivity — 5-way 일괄 측정 driver (fit + assign 패턴 method 만).

1M (DEEP/SIFT) 에서 측정한 7개 method 중 stratification 후 run_method_measurement
호출 패턴인 5개 (MiniBatch / Random Projection / Hilbert / Z-order / LSH) 를 8M
데이터에서 재현. KDE-pilot / Distance-Shell / IS 는 inline estimator 패턴이라
본 driver 에서 제외 — 필요시 별도 wrapper 작성.

목적:
  - sample_size=385 가 8M 의 더 큰 cluster 에서 효과 보존하는지 검증.
  - 분모 붕괴 (KM20-RANDOM20 격차 1%p 이하) 가 8M 에서 회복되는지 확인.
  - cross-scale (1M → 8M) 단조성 검정.

사전 조건:
1. 메인 세션 8M 측정 완료 (phase7_8m_dtarget_midsel.json + 추가 sel 측정).
2. convert_8m_dtarget_to_parquet.py 실행 → query_selectivity_8m.parquet 생성.
3. 8M 의 stratum_id 컬럼 존재 (KM20 baseline 비교용 — phase7_8m_strat 에서 부여됨).

사용 (서버):
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_8m_sensitivity.py
    # 일부만:
    python3 .../run_8m_sensitivity.py --methods minibatch hilbert zorder

산출 (서버 cache/rq1/, local 회수):
    rq3_8m_minibatch.parquet, rq3_8m_random_proj.parquet, rq3_8m_hilbert.parquet,
    rq3_8m_zorder.parquet, rq3_8m_lsh.parquet
"""
from __future__ import annotations

import argparse
import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
# NOTE: subdir 추가 시 'lsh.py' 와 'lsh/' namespace package path resolution 충돌.
# ROOT 만 두면 sub-namespace package 로 정상 resolve (run_lsh.py 의 패턴).

from _measure_common import (  # noqa: E402
    DATASETS_8M, N_STRATA, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)


def _fit_assign_minibatch(samples, all_vecs, seed):
    from offline_simple.minibatch_kmeans import (
        train_minibatch_kmeans, assign_minibatch,
    )
    model = train_minibatch_kmeans(samples, n_clusters=N_STRATA, random_state=seed)
    return assign_minibatch(model, all_vecs)


def _fit_assign_random_proj(samples, all_vecs, seed):
    from offline_simple.random_projection import (
        make_projection, assign_random_projection,
    )
    matrix = make_projection(samples.shape[1], k=N_STRATA, seed=seed)
    return assign_random_projection(matrix, all_vecs)


def _fit_assign_hilbert(samples, all_vecs, seed):
    from hilbert.hilbert_curve import fit_hilbert_mapper, assign_hilbert
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mapper = fit_hilbert_mapper(samples, n_strata=N_STRATA, seed=seed)
        return assign_hilbert(mapper, all_vecs)


def _fit_assign_zorder(samples, all_vecs, seed):
    from zorder.zorder_curve import fit_zorder_mapper, assign_zorder
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mapper = fit_zorder_mapper(samples, n_strata=N_STRATA, seed=seed)
        return assign_zorder(mapper, all_vecs)


def _fit_assign_lsh(samples, all_vecs, seed):
    from lsh.lsh import make_hyperplanes, assign_lsh
    hyper = make_hyperplanes(samples.shape[1], k=N_STRATA, seed=seed)
    return assign_lsh(hyper, all_vecs, k=N_STRATA)


def _fit_assign_hybrid(samples, all_vecs, seed):
    from hybrid.minibatch_hilbert import fit_hybrid_mapper, assign_hybrid
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        # 5×4=20 (N_STRATA 와 일치)
        mapper = fit_hybrid_mapper(samples, k_outer=5, k_inner=4, seed=seed)
        return assign_hybrid(mapper, all_vecs)


def _fit_assign_minibatch_partial(samples, all_vecs, seed):
    from offline_simple.minibatch_partial import (
        train_minibatch_partial, assign_minibatch,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        result = train_minibatch_partial(
            samples, n_clusters=N_STRATA, chunk_size=1000, random_state=seed,
        )
        return assign_minibatch(result, all_vecs)


def _fit_assign_pca1d(samples, all_vecs, seed):
    from pca1d.pca1d_quantile import fit_pca1d_mapper, assign_pca1d
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return assign_pca1d(fit_pca1d_mapper(samples, n_strata=N_STRATA, seed=seed), all_vecs)


def _fit_assign_kdtree(samples, all_vecs, seed):
    from kdtree.kdtree_partition import fit_kdtree_partition, assign_kdtree
    return assign_kdtree(fit_kdtree_partition(samples, n_strata=N_STRATA, seed=seed), all_vecs)


def _fit_assign_pq(samples, all_vecs, seed):
    from pq.product_quantization import fit_pq_mapper, assign_pq
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return assign_pq(fit_pq_mapper(samples, n_strata=N_STRATA, m=2, seed=seed), all_vecs)


def _fit_assign_spectral(samples, all_vecs, seed):
    from spectral.spectral_clustering import fit_spectral, assign_spectral
    # Spectral O(N²) — 8M sensitivity 에서는 sample size 더 작게
    n_sub = min(len(samples), 5000)
    if len(samples) > n_sub:
        rng = np.random.default_rng(seed)
        sub_idx = rng.choice(len(samples), size=n_sub, replace=False)
        samples = samples[sub_idx]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return assign_spectral(
            fit_spectral(samples, n_strata=N_STRATA, seed=seed), all_vecs,
        )


def _fit_assign_birch(samples, all_vecs, seed):
    from birch.birch_partition import fit_birch, assign_birch
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return assign_birch(
            fit_birch(samples, n_strata=N_STRATA, seed=seed), all_vecs,
        )


def _fit_assign_hdbscan(samples, all_vecs, seed):
    from hdbscan.hdbscan_partition import fit_hdbscan, assign_hdbscan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return assign_hdbscan(fit_hdbscan(samples, n_strata=N_STRATA, seed=seed), all_vecs)


def _fit_assign_gmm(samples, all_vecs, seed):
    from gmm.gmm_partition import fit_gmm, assign_gmm
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return assign_gmm(fit_gmm(samples, n_strata=N_STRATA, seed=seed), all_vecs)


def _fit_assign_sobol(samples, all_vecs, seed):
    from sobol.sobol_stratification import fit_sobol, assign_sobol
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return assign_sobol(fit_sobol(samples, n_strata=N_STRATA, seed=seed), all_vecs)


def _fit_assign_sparse_rp(samples, all_vecs, seed):
    from sparserp.sparse_random_projection import fit_sparse_rp, assign_sparse_rp
    matrix = fit_sparse_rp(samples, n_strata=N_STRATA, seed=seed)
    return assign_sparse_rp(matrix, all_vecs, k=N_STRATA)


METHOD_DISPATCH = {
    "minibatch": _fit_assign_minibatch,
    "random_proj": _fit_assign_random_proj,
    "hilbert": _fit_assign_hilbert,
    "zorder": _fit_assign_zorder,
    "lsh": _fit_assign_lsh,
    "hybrid": _fit_assign_hybrid,
    "minibatch_partial": _fit_assign_minibatch_partial,
    "pca1d": _fit_assign_pca1d,
    "kdtree": _fit_assign_kdtree,
    "pq": _fit_assign_pq,
    "spectral": _fit_assign_spectral,
    "birch": _fit_assign_birch,
    "hdbscan": _fit_assign_hdbscan,
    "gmm": _fit_assign_gmm,
    "sobol": _fit_assign_sobol,
    "sparse_rp": _fit_assign_sparse_rp,
}


def measure_one_method(method: str, ds: dict, all_vecs, n_queries: int,
                       learn_seed: int, learn_frac: float):
    """method 별 fit + assign 후 run_method_measurement 호출."""
    print(f"\n[{kst()}] === {ds['name']} × {method} ===")
    n = len(all_vecs)
    n_learn = max(int(n * learn_frac), N_STRATA * 50)
    rng = np.random.default_rng(learn_seed)
    learn_idx = rng.choice(n, size=n_learn, replace=False)
    learn_samples = all_vecs[learn_idx]

    t_learn = time.time()
    stratum_ids = METHOD_DISPATCH[method](learn_samples, all_vecs, learn_seed)
    learn_elapsed = time.time() - t_learn
    print(f"[{kst()}]   {method} fit+assign elapsed: {learn_elapsed:.1f}s "
          f"on {n_learn:,} learn samples → {len(all_vecs):,} all rows")

    rows = run_method_measurement(
        method_name=method, all_vecs=all_vecs, stratum_ids=stratum_ids,
        ds=ds, n_queries=n_queries, modes=("equal",),
    )
    return rows


def main():
    ap = argparse.ArgumentParser(description="RQ3 8M sensitivity — 5-way driver")
    ap.add_argument("--methods", nargs="*",
                    default=list(METHOD_DISPATCH.keys()),
                    help="측정할 method 목록 (default: 모두)")
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--learn-frac", type=float, default=0.01)
    args = ap.parse_args()

    print(f"[{kst()}] === RQ3 8M sensitivity ===")
    print(f"[{kst()}] methods: {args.methods}")

    for ds in DATASETS_8M:
        # 사전 조건 체크
        if not ds["query_sel"].exists():
            print(f"⚠️ {ds['query_sel']} 없음 — convert_8m_dtarget_to_parquet.py 먼저 실행")
            continue
        print(f"\n[{kst()}] === fetching 8M vectors ({ds['table']}) ===")
        all_vecs, _ = fetch_all_vectors_safe(ds)

        for method in args.methods:
            if method not in METHOD_DISPATCH:
                print(f"⚠️ unknown method '{method}' — skip")
                continue
            t_method = time.time()
            try:
                rows = measure_one_method(
                    method, ds, all_vecs, args.n_queries,
                    args.learn_seed, args.learn_frac,
                )
                save_parquet_meta(
                    rows, prefix=f"rq3_8m_{method}",
                    extra_meta={
                        "method": method,
                        "dataset": ds["name"],
                        "learn_seed": args.learn_seed,
                        "learn_frac": args.learn_frac,
                        "n_queries": args.n_queries,
                        "elapsed_s": round(time.time() - t_method, 1),
                    },
                )
            except Exception as e:
                print(f"⚠️ {method} failed: {type(e).__name__}: {e}")
                # 다음 method 로 계속

    print(f"\n[{kst()}] === 8M sensitivity 측정 완료 ===")


if __name__ == "__main__":
    main()
