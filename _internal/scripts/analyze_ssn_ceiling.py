#!/usr/bin/env python3
"""SSN++ ceiling hypothesis — 4 analyses combined.

1. Vector norm distribution (4 datasets compared)
2. PCA energy / cumulative explained variance ratio
3. Parquet column structure validation
4. Cluster size + sigma + BERN qerr comparison

Output: clean text summary for narrative patch.
"""
import sys, os, json, glob
import numpy as np
import pandas as pd
from pathlib import Path

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")

# Datasets to compare
DATASETS = {
    "DEEP_sf1": "partsupp_deep_1_vectors.npy",
    "SIFT_sf1": "partsupp_sift_1_vectors.npy",
    "SSN_sf1": "partsupp_fb_1_vectors.npy",
    "SSN_sf10": "partsupp_fb_10_vectors.npy",
}

# memmap for safety on large files
def load_npy_memmap(path):
    arr = np.load(path, mmap_mode="r")
    return arr

# Sample for analysis (8M × 256d × 4 = 8GB; SSN sf10 too big to fully load)
MAX_SAMPLE = 200_000  # subsample if larger
RNG_SEED = 42


def analysis_1_norm(name, arr):
    """Vector norm (L2) distribution stats."""
    n = len(arr)
    if n > MAX_SAMPLE:
        rng = np.random.default_rng(RNG_SEED)
        idx = rng.choice(n, MAX_SAMPLE, replace=False)
        idx.sort()
        sub = np.array(arr[idx], dtype=np.float32)  # copy, force load
    else:
        sub = np.array(arr, dtype=np.float32)

    norms = np.linalg.norm(sub, axis=1)
    return {
        "name": name,
        "n_total": n,
        "n_sampled": len(sub),
        "dim": sub.shape[1],
        "norm_mean": float(np.mean(norms)),
        "norm_std": float(np.std(norms)),
        "norm_min": float(np.min(norms)),
        "norm_p1": float(np.percentile(norms, 1)),
        "norm_p25": float(np.percentile(norms, 25)),
        "norm_p50": float(np.percentile(norms, 50)),
        "norm_p75": float(np.percentile(norms, 75)),
        "norm_p99": float(np.percentile(norms, 99)),
        "norm_max": float(np.max(norms)),
        "norm_cv": float(np.std(norms) / np.mean(norms)) if np.mean(norms) > 0 else 0.0,
    }


def analysis_2_pca(name, arr):
    """PCA cumulative explained variance ratio."""
    from sklearn.decomposition import PCA

    n = len(arr)
    # PCA on subsample (PCA scales as n*d^2, so 100K rows is enough)
    sub_size = min(100_000, n)
    rng = np.random.default_rng(RNG_SEED)
    idx = rng.choice(n, sub_size, replace=False)
    idx.sort()
    sub = np.array(arr[idx], dtype=np.float32)

    d = sub.shape[1]
    n_components = min(d, sub_size, 256)  # cap for speed
    pca = PCA(n_components=n_components, svd_solver="auto", random_state=RNG_SEED)
    pca.fit(sub)
    cum = np.cumsum(pca.explained_variance_ratio_)

    # Targets: dim ratio (1%, 5%, 10%, 20%, 50%) + thresholds for cum (50%, 80%, 90%, 95%, 99%)
    pct_dims = {
        f"cum_at_dim_{p}pct": float(cum[max(0, int(d * p / 100) - 1)])
        for p in [1, 5, 10, 20, 50]
        if int(d * p / 100) >= 1
    }
    # Find the smallest k where cum[k] >= threshold
    threshold_dims = {}
    for thr in [0.50, 0.80, 0.90, 0.95, 0.99]:
        idx_thr = np.searchsorted(cum, thr) + 1
        if idx_thr > n_components:
            threshold_dims[f"dim_for_{int(thr*100)}pct"] = -1  # not reached
        else:
            threshold_dims[f"dim_for_{int(thr*100)}pct"] = int(idx_thr)
    # Effective intrinsic dim (90% threshold) ratio
    eff_dim_90 = threshold_dims.get("dim_for_90pct", -1)
    return {
        "name": name,
        "dim": d,
        "n_pca_sample": sub_size,
        "n_components_fitted": n_components,
        **pct_dims,
        **threshold_dims,
        "eff_dim_90_ratio": float(eff_dim_90 / d) if eff_dim_90 > 0 else -1.0,
    }


def analysis_3_parquet():
    """Parquet column structure check."""
    out = []
    candidates = [
        ("rq3_SSN_sf1_hilbert.parquet", "rq3_DEEP_sf1_hilbert.parquet", "rq3_SIFT_sf1_hilbert.parquet", "rq3_WIKI_sf1_hilbert.parquet"),
    ]
    for files in candidates:
        for f in files:
            p = CACHE / f
            if not p.exists():
                out.append({"file": f, "exists": False})
                continue
            df = pd.read_parquet(p)
            out.append({
                "file": f,
                "exists": True,
                "shape": list(df.shape),
                "columns": list(df.columns),
                "n_rows": len(df),
                "qerr_method_mean": float(df["qerr_method"].mean()) if "qerr_method" in df.columns else None,
                "qerr_method_std": float(df["qerr_method"].std()) if "qerr_method" in df.columns else None,
                "qerr_bernoulli_mean": float(df["qerr_bernoulli"].mean()) if "qerr_bernoulli" in df.columns else None,
                "qerr_bernoulli_std": float(df["qerr_bernoulli"].std()) if "qerr_bernoulli" in df.columns else None,
            })
    return out


def analysis_4_cluster(name, arr):
    """KMeans cluster size + per-cluster sigma + cluster size CV."""
    from sklearn.cluster import KMeans

    n = len(arr)
    # KMeans on subsample for speed
    sub_size = min(100_000, n)
    rng = np.random.default_rng(RNG_SEED)
    idx = rng.choice(n, sub_size, replace=False)
    idx.sort()
    sub = np.array(arr[idx], dtype=np.float32)

    K = 20
    km = KMeans(n_clusters=K, random_state=RNG_SEED, n_init=4, max_iter=100)
    labels = km.fit_predict(sub)
    sizes = np.bincount(labels, minlength=K)
    size_max = int(sizes.max())
    size_min = int(sizes.min())
    size_mean = float(sizes.mean())
    size_std = float(sizes.std())
    size_cv = float(size_std / size_mean) if size_mean > 0 else 0.0
    size_ratio = float(size_max / size_min) if size_min > 0 else float("inf")

    # Per-cluster sigma (mean of within-cluster L2 std per dim, averaged)
    sigmas = []
    for k in range(K):
        mask = labels == k
        if mask.sum() < 2:
            continue
        member = sub[mask]
        # vector norm of (member - centroid)
        diff = member - km.cluster_centers_[k]
        sigma = np.linalg.norm(diff, axis=1).mean()
        sigmas.append(float(sigma))

    return {
        "name": name,
        "n_sampled": sub_size,
        "K": K,
        "size_min": size_min,
        "size_max": size_max,
        "size_mean": size_mean,
        "size_std": size_std,
        "size_cv": size_cv,
        "size_ratio_max_min": size_ratio,
        "sigma_mean": float(np.mean(sigmas)),
        "sigma_std": float(np.std(sigmas)),
        "sigma_cv": float(np.std(sigmas) / np.mean(sigmas)) if np.mean(sigmas) > 0 else 0.0,
    }


def main():
    results = {"norm": [], "pca": [], "parquet": [], "cluster": []}

    print("=" * 80)
    print("SSN++ ceiling analysis — 4 analyses")
    print("=" * 80)

    for ds_name, fname in DATASETS.items():
        path = CACHE / fname
        if not path.exists():
            print(f"  [WARN] {ds_name}: {path} not found, skip")
            continue
        print(f"\n[{ds_name}] loading {fname}...")
        arr = load_npy_memmap(path)
        print(f"  shape={arr.shape}, dtype={arr.dtype}")

        # Analysis 1
        print(f"  [norm] computing...")
        r1 = analysis_1_norm(ds_name, arr)
        results["norm"].append(r1)

        # Analysis 2
        print(f"  [pca] computing...")
        r2 = analysis_2_pca(ds_name, arr)
        results["pca"].append(r2)

        # Analysis 4 (cluster)
        print(f"  [cluster] computing...")
        r4 = analysis_4_cluster(ds_name, arr)
        results["cluster"].append(r4)

        del arr  # free memmap
        import gc
        gc.collect()

    # Analysis 3 (parquet)
    print(f"\n[parquet] checking schemas...")
    results["parquet"] = analysis_3_parquet()

    out_path = "/tmp/ssn_ceiling_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {out_path}")

    # Pretty summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\n--- Analysis 1: Vector Norm Distribution ---")
    print(f"{'Dataset':<12} {'dim':>5} {'norm_mean':>12} {'norm_std':>12} {'norm_cv':>10} {'p1':>10} {'p99':>10} {'p99/p1':>10}")
    for r in results["norm"]:
        ratio = r["norm_p99"] / r["norm_p1"] if r["norm_p1"] > 0 else float("inf")
        print(f"{r['name']:<12} {r['dim']:>5} {r['norm_mean']:>12.4f} {r['norm_std']:>12.4f} {r['norm_cv']:>10.4f} {r['norm_p1']:>10.4f} {r['norm_p99']:>10.4f} {ratio:>10.4f}")

    print("\n--- Analysis 2: PCA Cumulative Explained Variance ---")
    print(f"{'Dataset':<12} {'dim':>5} {'dim_50pct':>10} {'dim_80pct':>10} {'dim_90pct':>10} {'dim_95pct':>10} {'eff_dim_90_ratio':>18}")
    for r in results["pca"]:
        print(f"{r['name']:<12} {r['dim']:>5} {r.get('dim_for_50pct', -1):>10} {r.get('dim_for_80pct', -1):>10} {r.get('dim_for_90pct', -1):>10} {r.get('dim_for_95pct', -1):>10} {r['eff_dim_90_ratio']:>18.4f}")

    print("\n--- Analysis 4: Cluster Size + Sigma (K=20) ---")
    print(f"{'Dataset':<12} {'size_cv':>10} {'size_ratio':>12} {'size_min':>10} {'size_max':>10} {'sigma_mean':>12} {'sigma_cv':>10}")
    for r in results["cluster"]:
        print(f"{r['name']:<12} {r['size_cv']:>10.4f} {r['size_ratio_max_min']:>12.4f} {r['size_min']:>10} {r['size_max']:>10} {r['sigma_mean']:>12.4f} {r['sigma_cv']:>10.4f}")

    print("\n--- Analysis 3: Parquet Schema ---")
    for r in results["parquet"]:
        if not r["exists"]:
            print(f"  {r['file']}: NOT FOUND")
            continue
        cols_str = ", ".join(r["columns"][:8]) + (" ..." if len(r["columns"]) > 8 else "")
        print(f"  {r['file']}: shape={r['shape']}, cols=[{cols_str}]")
        if r.get("qerr_method_mean") is not None:
            print(f"     qerr_method  mean={r['qerr_method_mean']:.4f} std={r['qerr_method_std']:.4f}")
        if r.get("qerr_bernoulli_mean") is not None:
            print(f"     qerr_bern    mean={r['qerr_bernoulli_mean']:.4f} std={r['qerr_bernoulli_std']:.4f}")

if __name__ == "__main__":
    main()
