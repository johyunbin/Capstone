#!/usr/bin/env python3
"""
모든 RQ3 method 의 self-test 통합 실행 — 측정 직전 sanity check.

12 stratification method (KDE/DistanceShell/IS 는 inline estimator 라 self-test 형식
다름, 별도 처리) 의 fit + assign API 를 같은 synthetic data 에서 실행 후 결과 검증.

산출:
  - stdout: 각 method 의 OK/FAIL + cluster size summary
  - 종료 code 0/1 (CI 용)

서버 에서도 실행 가능 — 모든 method 가 import 되는지 동작 검증.
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# 12 method API 정의 — fit + assign signature
METHODS = [
    ("minibatch", "offline_simple.minibatch_kmeans",
     "train_minibatch_kmeans", "assign_minibatch", "n_clusters"),
    ("minibatch_partial", "offline_simple.minibatch_partial",
     "train_minibatch_partial", "assign_minibatch", "n_clusters"),
    ("random_proj", "offline_simple.random_projection",
     "make_projection", "assign_random_projection", "k"),
    ("pca1d", "pca1d.pca1d_quantile",
     "fit_pca1d_mapper", "assign_pca1d", "n_strata"),
    ("hilbert", "hilbert.hilbert_curve",
     "fit_hilbert_mapper", "assign_hilbert", "n_strata"),
    ("zorder", "zorder.zorder_curve",
     "fit_zorder_mapper", "assign_zorder", "n_strata"),
    ("hybrid", "hybrid.minibatch_hilbert",
     "fit_hybrid_mapper", "assign_hybrid", "n_strata"),
    ("kdtree", "kdtree.kdtree_partition",
     "fit_kdtree_partition", "assign_kdtree", "n_strata"),
    ("pq", "pq.product_quantization",
     "fit_pq_mapper", "assign_pq", "n_strata"),
    ("spectral", "spectral.spectral_clustering",
     "fit_spectral", "assign_spectral", "n_strata"),
    ("birch", "birch.birch_partition",
     "fit_birch", "assign_birch", "n_strata"),
    ("lsh", "lsh.lsh",
     "make_hyperplanes", "assign_lsh", "k"),
]

N_STRATA = 20
N_SAMPLES = 1000
N_ALL = 5000


def test_method(name: str, mod_path: str, fit_fn_name: str,
                assign_fn_name: str, k_kwarg: str) -> dict:
    """method 별 fit + assign + 결과 검증."""
    rng = np.random.default_rng(42)
    samples = rng.standard_normal((N_SAMPLES, 96)).astype(np.float32)
    all_vecs = rng.standard_normal((N_ALL, 96)).astype(np.float32)

    result = {"name": name, "ok": False, "elapsed_s": 0.0,
              "cluster_min": -1, "cluster_max": -1, "max_min_ratio": -1.0,
              "error": None}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t0 = time.time()
            mod = __import__(mod_path, fromlist=[fit_fn_name, assign_fn_name])
            fit_fn = getattr(mod, fit_fn_name)
            assign_fn = getattr(mod, assign_fn_name)

            # method 별 fit 호출 — kwarg 명 다름
            if name == "random_proj":
                # make_projection(dim, k=20, seed=42)
                fitted = fit_fn(samples.shape[1], k=N_STRATA, seed=42)
            elif name == "lsh":
                fitted = fit_fn(samples.shape[1], k=N_STRATA, seed=42)
            elif name == "minibatch":
                fitted = fit_fn(samples, n_clusters=N_STRATA, random_state=42)
            elif name == "minibatch_partial":
                fitted = fit_fn(samples, n_clusters=N_STRATA, chunk_size=500, random_state=42)
            elif name == "hybrid":
                fitted = fit_fn(samples, k_outer=5, k_inner=4, seed=42)
            elif name == "pq":
                fitted = fit_fn(samples, n_strata=N_STRATA, m=2, seed=42)
            else:
                fitted = fit_fn(samples, **{k_kwarg: N_STRATA}, seed=42)

            # assign — random_projection 과 lsh 는 raw matrix 받음
            if name == "random_proj":
                sids = assign_fn(fitted, all_vecs)
            elif name == "lsh":
                sids = assign_fn(fitted, all_vecs, k=N_STRATA)
            else:
                sids = assign_fn(fitted, all_vecs)

            result["elapsed_s"] = round(time.time() - t0, 3)

            # 검증
            assert sids.shape == (N_ALL,), f"sids shape {sids.shape}"
            assert sids.min() >= 0, f"negative sid: {sids.min()}"
            assert sids.max() < N_STRATA, f"sid exceed N_STRATA: {sids.max()}"
            counts = np.bincount(sids, minlength=N_STRATA)
            result["cluster_min"] = int(counts.min())
            result["cluster_max"] = int(counts.max())
            result["max_min_ratio"] = float(counts.max() / max(counts.min(), 1))
            result["ok"] = True
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result


def main():
    print("=" * 75)
    print("RQ3 12-method Self-Test Integration Runner")
    print("=" * 75)
    print(f"  N_STRATA={N_STRATA}, N_SAMPLES={N_SAMPLES}, N_ALL={N_ALL}, dim=96")
    print()

    results = []
    for spec in METHODS:
        r = test_method(*spec)
        results.append(r)
        if r["ok"]:
            print(f"  ✓ {r['name']:18s} elapsed={r['elapsed_s']:6.3f}s "
                  f"sizes [{r['cluster_min']:>4d}, {r['cluster_max']:>4d}], "
                  f"max/min={r['max_min_ratio']:6.2f}")
        else:
            print(f"  ✗ {r['name']:18s} FAILED: {r['error']}")

    print()
    n_ok = sum(1 for r in results if r["ok"])
    n_total = len(results)
    print(f"=== Summary: {n_ok}/{n_total} method pass ===")
    if n_ok == n_total:
        print("✓ All methods importable + functioning. Ready for measurement.")
        return 0
    else:
        failed = [r["name"] for r in results if not r["ok"]]
        print(f"✗ Failed: {failed}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
