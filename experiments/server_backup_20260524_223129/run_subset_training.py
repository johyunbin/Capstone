#!/usr/bin/env python3
"""run_subset_training.py — RQ3 subset-training wrapper for slow density methods.

8M (sf10) 에서 timeout, 80M (sf100) 에서 infeasible 한 method (HDBSCAN / BIRCH /
Spectral / Agglomerative) 를 1M random subset 에 fit → centroid 산출 → full N 을
nearest-centroid 로 chunked predict 하는 공용 wrapper.

Pattern (run_agglomerative.py 의 1M-fit + nearest-centroid 를 일반화):
1. random subset (default 1,000,000, deterministic seed=42) 추출
2. method-specific fit_predict 로 sub_labels 산출
3. sub_labels 의 cluster 별 centroid 계산
4. full N 을 chunked Euclidean nearest-centroid 로 assign (ds = a² + b² - 2ab)
5. run_method_measurement 호출 → save_parquet_meta

methods:
- hdbscan       — density-based hierarchical (noise=-1 제외 후 centroid)
- birch         — incremental tree
- spectral      — affinity O(N²) → subset 자동 cap (default 100K)
- agglomerative — Ward linkage hierarchical

서버 경로: /mnt/hdd0/home/capstone2026/cache/rq3/run_subset_training.py
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

import _measure_common as mc  # noqa: E402
from _measure_common import (  # noqa: E402
    DATASETS, fetch_all_vectors_safe, kst,
    run_method_measurement, save_parquet_meta,
)

DEFAULT_SUBSET_FIT_N = 1_000_000
SPECTRAL_CAP = 100_000  # spectral 은 affinity O(N²) → 100K 가 현실적 상한


def _assign_nearest_centroid(
    all_vecs: np.ndarray, centroids: np.ndarray, chunk: int = 200_000,
) -> np.ndarray:
    """Chunked Euclidean nearest-centroid assignment.

    ||a - b||² = ||a||² + ||b||² - 2 a·b 로 vectorize.
    full broadcast (O(chunk × K × dim)) 회피, BLAS gemm 활용.
    """
    n = len(all_vecs)
    out = np.empty(n, dtype=np.int32)
    cs = (centroids ** 2).sum(axis=1)
    for i in range(0, n, chunk):
        j = min(i + chunk, n)
        block = all_vecs[i:j]
        ds = (block ** 2).sum(axis=1, keepdims=True) + cs[None, :] - 2.0 * block @ centroids.T
        out[i:j] = np.argmin(ds, axis=1).astype(np.int32)
    return out


def _centroids_from_labels(
    fit_data: np.ndarray, labels: np.ndarray, exclude: tuple = (),
) -> np.ndarray:
    """labels 의 unique cluster (exclude 제외) 별 centroid 산출.

    Returns:
        centroids (K_eff, dim) float32 — K_eff 는 unique label 수 (noise 제외).
        empty cluster 는 자동 skip (label 이 없으면 stack 에서 제외).
    """
    uniq = sorted(set(int(l) for l in np.unique(labels)) - set(exclude))
    if not uniq:
        raise SystemExit("[subset-training] no usable clusters (all noise?)")
    centroids = np.zeros((len(uniq), fit_data.shape[1]), dtype=np.float64)
    for new, old in enumerate(uniq):
        mask = labels == old
        if mask.sum() == 0:
            continue
        centroids[new] = fit_data[mask].mean(axis=0)
    return centroids.astype(np.float32)


def fit_subset(
    all_vecs: np.ndarray, method: str, subset_n: int, K: int,
    seed: int = 42,
    hdbscan_min_cluster_size: int | None = None,
    birch_threshold: float = 0.5,
    spectral_n_neighbors: int = 10,
) -> np.ndarray:
    """Subset-training: random subset → method fit → centroid → full N nearest-centroid.

    Returns:
        sids: (N,) int32 — 0..K-1 (또는 K_eff < K 일 경우 0..K_eff-1).
    """
    n = len(all_vecs)
    rng = np.random.default_rng(seed)

    if method == "spectral" and subset_n > SPECTRAL_CAP:
        print(f"[{kst()}]   spectral cap: subset_n {subset_n:,} → {SPECTRAL_CAP:,} "
              f"(affinity O(N²) memory)")
        subset_n = SPECTRAL_CAP

    if n > subset_n:
        idx = rng.choice(n, size=subset_n, replace=False)
        fit_data = all_vecs[idx]
    else:
        fit_data = all_vecs

    print(f"[{kst()}]   subset-training fit on {len(fit_data):,} sample "
          f"(full N={n:,}, K={K}, method={method})")

    t_fit = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if method == "hdbscan":
            try:
                import hdbscan
            except ImportError as e:
                raise SystemExit(f"[subset-training] hdbscan missing: {e}")
            mcs = hdbscan_min_cluster_size or max(50, len(fit_data) // (K * 4))
            print(f"[{kst()}]   HDBSCAN(min_cluster_size={mcs}, min_samples=10)")
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=mcs, min_samples=10, core_dist_n_jobs=4,
            ).fit(fit_data)
            labels = clusterer.labels_
            n_noise = int((labels == -1).sum())
            uniq_clusters = sorted(set(int(l) for l in np.unique(labels)) - {-1})
            print(f"[{kst()}]   HDBSCAN clusters={len(uniq_clusters)} (noise={n_noise:,})")
            # 만약 cluster 가 K 보다 많으면 큰 cluster K 개만, 적으면 그대로
            if len(uniq_clusters) > K:
                sizes = [(c, int((labels == c).sum())) for c in uniq_clusters]
                sizes.sort(key=lambda x: -x[1])
                kept = set(c for c, _ in sizes[:K])
                exclude = (-1,) + tuple(c for c in uniq_clusters if c not in kept)
            else:
                exclude = (-1,)
            centroids = _centroids_from_labels(fit_data, labels, exclude=exclude)

        elif method == "birch":
            from sklearn.cluster import Birch
            print(f"[{kst()}]   BIRCH(n_clusters={K}, threshold={birch_threshold})")
            b = Birch(n_clusters=K, threshold=birch_threshold).fit(fit_data)
            # BIRCH 는 predict 가 있지만 일관성을 위해 centroid 경유
            sub_labels = b.predict(fit_data)
            centroids = _centroids_from_labels(fit_data, sub_labels)

        elif method == "spectral":
            from sklearn.cluster import SpectralClustering
            print(f"[{kst()}]   SpectralClustering(n_clusters={K}, "
                  f"affinity=nearest_neighbors, n_neighbors={spectral_n_neighbors})")
            sc = SpectralClustering(
                n_clusters=K, affinity="nearest_neighbors",
                n_neighbors=spectral_n_neighbors, n_jobs=4, random_state=seed,
                assign_labels="kmeans",
            ).fit(fit_data)
            centroids = _centroids_from_labels(fit_data, sc.labels_)

        elif method == "agglomerative":
            from sklearn.cluster import AgglomerativeClustering
            print(f"[{kst()}]   AgglomerativeClustering(n_clusters={K}, linkage=ward)")
            ag = AgglomerativeClustering(n_clusters=K, linkage="ward").fit(fit_data)
            centroids = _centroids_from_labels(fit_data, ag.labels_)

        else:
            raise SystemExit(f"unsupported method: {method}")

    fit_elapsed = time.time() - t_fit
    print(f"[{kst()}]   fit elapsed: {fit_elapsed:.1f}s, "
          f"centroids={centroids.shape[0]}×{centroids.shape[1]}")

    # full N 을 chunked nearest-centroid 로 assign
    t_assign = time.time()
    sids = _assign_nearest_centroid(all_vecs, centroids)
    assign_elapsed = time.time() - t_assign
    print(f"[{kst()}]   nearest-centroid assign {assign_elapsed:.1f}s "
          f"(unique={len(np.unique(sids))})")
    return sids


def main():
    ap = argparse.ArgumentParser(
        description="RQ3 subset-training wrapper (HDBSCAN/BIRCH/Spectral/Agglomerative)"
    )
    ap.add_argument("--method", required=True,
                    choices=["hdbscan", "birch", "spectral", "agglomerative"])
    ap.add_argument("--out-prefix", default=None,
                    help="default: rq3_subset_{method}")
    ap.add_argument("--datasets", nargs="*", default=None,
                    help="DATASETS 의 name 부분집합 (없으면 전체)")
    ap.add_argument("--subset-n", type=int, default=DEFAULT_SUBSET_FIT_N,
                    help=f"fit subset 크기 (default {DEFAULT_SUBSET_FIT_N:,})")
    ap.add_argument("--K", type=int, default=None,
                    help="override mc.N_STRATA (default 20)")
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--learn-seed", type=int, default=42)
    ap.add_argument("--include-bernoulli", action="store_true")
    # method-specific knobs
    ap.add_argument("--hdbscan-min-cluster-size", type=int, default=None,
                    help="HDBSCAN: default = max(50, subset_n//(K*4))")
    ap.add_argument("--birch-threshold", type=float, default=0.5)
    ap.add_argument("--spectral-n-neighbors", type=int, default=10)
    args = ap.parse_args()

    if args.K is not None:
        mc.N_STRATA = args.K
    K = mc.N_STRATA

    out_prefix = args.out_prefix or f"rq3_subset_{args.method}"
    use_datasets = DATASETS if not args.datasets else [
        d for d in DATASETS if d["name"] in args.datasets
    ]
    if not use_datasets:
        raise SystemExit(f"no matching datasets: {args.datasets}")

    modes = ("equal", "bernoulli") if args.include_bernoulli else ("equal",)

    print(f"[{kst()}] === RQ3 subset-training {args.method} (K={K}, "
          f"subset_n={args.subset_n:,}) ===")

    all_rows = []
    t_total = time.time()

    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ({ds['table']}) ===")
        all_vecs, _ = fetch_all_vectors_safe(ds)

        sids = fit_subset(
            all_vecs, method=args.method, subset_n=args.subset_n, K=K,
            seed=args.learn_seed,
            hdbscan_min_cluster_size=args.hdbscan_min_cluster_size,
            birch_threshold=args.birch_threshold,
            spectral_n_neighbors=args.spectral_n_neighbors,
        )

        method_name = f"{args.method}_subset"
        rows = run_method_measurement(
            method_name=method_name, all_vecs=all_vecs, stratum_ids=sids,
            ds=ds, n_queries=args.n_queries, modes=modes,
        )
        all_rows.extend(rows)

    save_parquet_meta(
        all_rows, prefix=out_prefix,
        extra_meta={
            "method": f"{args.method} subset-training (fit on {args.subset_n})",
            "subset_n": args.subset_n,
            "K": K,
            "learn_seed": args.learn_seed,
            "n_queries": args.n_queries,
            "hdbscan_min_cluster_size": args.hdbscan_min_cluster_size,
            "birch_threshold": args.birch_threshold,
            "spectral_n_neighbors": args.spectral_n_neighbors,
            "elapsed_s": round(time.time() - t_total, 1),
        },
    )
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
