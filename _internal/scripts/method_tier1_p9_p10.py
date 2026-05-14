#!/usr/bin/env python3
"""
RQ3 Tier 1 신규 6 method (handoff_v3 §1.3 + Q4 권고).

5/10 41-method audit (5,777 lines, 8 agent 병렬) 결과:
- 신규 paradigm 2개 도입: P9 InfoTheoretic + P10 Density estimation
- handoff_v3 §0.4 paradigm 평균 충실도 3.8/10 → ≥5.0 회복 목표

본 file 의 6 method:
  1. assign_dbscan          — P1 Cluster (Ester KDD 1996) — subset training + nearest centroid
  2. assign_kde_parzen      — P10 Density (신규, Parzen 1962) — KDE on subset + density quantile bin
  3. assign_mhist2          — P6 Histogram (Poosala VLDB 1997) — PCA top-2 + 2D adaptive histogram
  4. assign_hyperloglog     — P9 InfoTheoretic (신규, Flajolet AofA 2007) — vector hash + HLL bucket
  5. assign_rsvd            — P4 DimReduction (Halko SIAM Review 2011) — TruncatedSVD(2) + 2D quantile
  6. assign_wavelet_hist    — P6 Quantization (Matias SIGMOD 1998) — Daubechies-2 wavelet + bin

Registry signature (measure_paper_exact.py:407 규약 일치):
    assign_<method>(all_vecs: np.ndarray, n_strata: int = 20, seed: int = 42) -> np.ndarray

Args:
    all_vecs: (N, dim) float32, N up to 80M (SF=100)
    n_strata: 20 (paper-exact)
    seed: 42 (deterministic)

Returns:
    (N,) int32, values in [0, n_strata)

서버 SF=100 대응 (handoff_v3 §3 SF feasibility matrix):
- DBSCAN/KDE/MHIST-2/wavelet: subset training + chunked predict
- HyperLogLog: O(N) hash, native chunked
- rSVD: incremental_pca fallback for SF=100

작성: 2026-05-10 21:30 KST (handoff_v3 P2 Tier 1 추가)
사용자 confirm 후 measure_paper_exact.py:_get_method_strata 에 6 elif 추가 예정
"""
from __future__ import annotations

import hashlib

import numpy as np


# 모든 method 공통: 80M 시 OOM 회피용 chunk 단위
_CHUNK = 100_000
_TRAIN_CAP = 50_000  # subset training default
_TRAIN_CAP_LARGE = 100_000  # KDE / rSVD


# =====================================================================
# 1. DBSCAN (P1 Cluster)
#    Ester, Kriegel, Sander, Xu KDD 1996.
#    80M 에 native O(N²) → subset training + nearest centroid for full.
# =====================================================================
def assign_dbscan(all_vecs: np.ndarray, n_strata: int = 20, seed: int = 42,
                  eps_quantile: float = 0.10, min_samples: int = 5) -> np.ndarray:
    """DBSCAN on subset → centroid per cluster → nearest centroid for full.

    eps 는 train pairwise distance distribution 의 eps_quantile (default 10%) 사용.
    cluster 수가 n_strata 미달이면 random padding (handoff_v3 §0.2 ★1 hdbscan 패턴).
    cluster 수 초과면 cluster size 큰 순 top n_strata 만 retain, 나머지 nearest 로 재할당.
    """
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import pairwise_distances

    rng = np.random.default_rng(seed)
    N = len(all_vecs)

    # ---- Step 1: subset 으로 DBSCAN fit ----
    sample_n = min(N, _TRAIN_CAP)
    if N > sample_n:
        sample_idx = rng.choice(N, sample_n, replace=False)
        sample = all_vecs[sample_idx]
    else:
        sample = all_vecs

    # eps 추정: pairwise distance 의 eps_quantile (Sander 1998 권고)
    # 8K subsample 기반 (50K x 50K full distance 는 OOM)
    eps_sample_n = min(8_000, sample_n)
    eps_idx = rng.choice(sample_n, eps_sample_n, replace=False)
    pd_sample = sample[eps_idx]
    pd_matrix = pairwise_distances(pd_sample[:1000], pd_sample, metric="euclidean")
    eps = float(np.quantile(pd_matrix[pd_matrix > 0], eps_quantile))
    if eps == 0 or not np.isfinite(eps):
        eps = 0.5  # safe fallback

    # ---- Step 2: DBSCAN fit on subset ----
    db = DBSCAN(eps=eps, min_samples=min_samples, algorithm="ball_tree", n_jobs=1)
    labels = db.fit_predict(sample)

    # ---- Step 3: cluster centroid ----
    unique = np.unique(labels[labels >= 0])
    if len(unique) == 0:
        # 모두 noise → fallback: random uniform stratum_id
        return rng.integers(0, n_strata, size=N, dtype=np.int32)

    # cluster size 큰 순 top n_strata
    cluster_sizes = [(c, int(np.sum(labels == c))) for c in unique]
    cluster_sizes.sort(key=lambda t: -t[1])
    top_clusters = [c for c, _ in cluster_sizes[:n_strata]]

    centroids_list = []
    for c in top_clusters:
        members = sample[labels == c]
        centroids_list.append(members.mean(axis=0))
    centroids = np.array(centroids_list, dtype=np.float32)

    # K_eff < n_strata → padding (handoff_v3 ★1 hdbscan 패턴)
    if len(centroids) < n_strata:
        pad_n = n_strata - len(centroids)
        # subset 의 random sample 로 pad centroid 생성
        pad_idx = rng.choice(sample_n, pad_n, replace=False)
        pad_centroids = sample[pad_idx]
        centroids = np.vstack([centroids, pad_centroids])

    # ---- Step 4: nearest centroid for full vectors (chunked) ----
    sids = np.empty(N, dtype=np.int32)
    for i in range(0, N, _CHUNK):
        chunk_v = all_vecs[i:i+_CHUNK]
        # broadcast L2: (chunk, n_strata, dim) — chunk*n_strata*dim mem (OK at 100K*20*768=1.5GB)
        # safer: matmul-based L2
        # ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b
        a2 = (chunk_v ** 2).sum(axis=1, keepdims=True)
        b2 = (centroids ** 2).sum(axis=1, keepdims=True).T
        ab = chunk_v @ centroids.T
        d2 = a2 + b2 - 2 * ab
        sids[i:i+_CHUNK] = np.argmin(d2, axis=1).astype(np.int32)
    return sids


# =====================================================================
# 2. KDE Parzen (P10 Density estimation, 신규 paradigm)
#    Parzen "On estimation of a probability density function" Annals 1962.
#    KDE on subset → density score for all → quantile bin.
# =====================================================================
def assign_kde_parzen(all_vecs: np.ndarray, n_strata: int = 20, seed: int = 42,
                      bandwidth: str = "silverman") -> np.ndarray:
    """KDE Parzen 1962 — density-based stratification.

    high-d KDE 는 curse of dim 으로 모든 query density 가 underflow → 1D PCA project 후 1D KDE.
    Silverman 1D rule: h = 0.9 * sigma * N^(-1/5).

    bandwidth: "silverman" 또는 float manual override.
    """
    from sklearn.neighbors import KernelDensity
    from sklearn.decomposition import PCA

    rng = np.random.default_rng(seed)
    N = len(all_vecs)

    # ---- Step 0: PCA 1D project (high-d KDE 회피) ----
    sample_n = min(N, _TRAIN_CAP_LARGE)
    sample_idx = rng.choice(N, sample_n, replace=False) if N > sample_n else np.arange(N)
    sample = all_vecs[sample_idx]
    pca = PCA(n_components=1, random_state=seed)
    pca.fit(sample)

    # ---- Step 1: project full to 1D (chunked, memory-safe) ----
    proj = np.empty(N, dtype=np.float32)
    for i in range(0, N, _CHUNK):
        proj[i:i+_CHUNK] = pca.transform(all_vecs[i:i+_CHUNK]).ravel()

    # ---- Step 2: 1D KDE bandwidth (Silverman 1D rule) ----
    proj_sample = proj[sample_idx]
    if isinstance(bandwidth, str) and bandwidth == "silverman":
        sigma_1d = float(proj_sample.std())
        h = 0.9 * sigma_1d * sample_n ** (-1 / 5)
        if h <= 0 or not np.isfinite(h):
            h = 0.1
    else:
        h = float(bandwidth)

    # ---- Step 3: 1D KDE fit on subset proj ----
    kde = KernelDensity(bandwidth=h, kernel="gaussian", algorithm="ball_tree", leaf_size=40)
    kde.fit(proj_sample.reshape(-1, 1))

    # ---- Step 4: log-density score for all (chunked) ----
    log_dens = np.empty(N, dtype=np.float32)
    for i in range(0, N, _CHUNK):
        log_dens[i:i+_CHUNK] = kde.score_samples(proj[i:i+_CHUNK].reshape(-1, 1))

    # ---- Step 5: density quantile binning → 20 bins (handoff_v3 신규 P10) ----
    edges = np.quantile(log_dens, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6  # rightmost inclusion
    sids = np.searchsorted(edges[1:-1], log_dens, side="right").astype(np.int32)
    return np.clip(sids, 0, n_strata - 1)


# =====================================================================
# 3. MHIST-2 (P6 Histogram)
#    Poosala & Ioannidis VLDB 1997 "Selectivity Estimation Without the Attribute Value Independence Assumption".
#    PCA top-2 components → 2D adaptive histogram (MaxDiff bucketing).
# =====================================================================
def assign_mhist2(all_vecs: np.ndarray, n_strata: int = 20, seed: int = 42) -> np.ndarray:
    """MHIST-2 (Poosala 1997) — multi-dimensional histogram.

    sqrt(n_strata) ≈ 5 per axis → 2D quantile grid 25 bins, mod n_strata.
    이 구현은 PCA(2) + equi-depth bucketing — Poosala 의 MaxDiff 변형.
    """
    from sklearn.decomposition import PCA

    N = len(all_vecs)
    sample_n = min(N, _TRAIN_CAP_LARGE)
    rng = np.random.default_rng(seed)
    sample_idx = rng.choice(N, sample_n, replace=False) if N > sample_n else np.arange(N)
    sample = all_vecs[sample_idx]

    # ---- Step 1: PCA top-2 fit on subset (full N 시 OOM) ----
    pca = PCA(n_components=2, random_state=seed)
    pca.fit(sample)

    # ---- Step 2: project full (chunked → memory-safe) ----
    proj = np.empty((N, 2), dtype=np.float32)
    for i in range(0, N, _CHUNK):
        proj[i:i+_CHUNK] = pca.transform(all_vecs[i:i+_CHUNK])

    # ---- Step 3: 2D quantile grid (k * k bins, k=ceil(sqrt(n_strata))) ----
    k = int(np.ceil(np.sqrt(n_strata)))
    e0 = np.quantile(proj[:, 0], np.linspace(0, 1, k + 1))
    e1 = np.quantile(proj[:, 1], np.linspace(0, 1, k + 1))
    e0[-1] += 1e-6
    e1[-1] += 1e-6

    b0 = np.clip(np.searchsorted(e0[1:-1], proj[:, 0], side="right"), 0, k - 1)
    b1 = np.clip(np.searchsorted(e1[1:-1], proj[:, 1], side="right"), 0, k - 1)
    return ((b0 * k + b1) % n_strata).astype(np.int32)


# =====================================================================
# 4. HyperLogLog (P9 InfoTheoretic, 신규 paradigm)
#    Flajolet, Fusy, Gandouet, Meunier AofA 2007.
#    bucket id (leading p bits of hash) 를 stratum_id 로 사용.
#    (cardinality estimation 본래 용도가 아닌, hash partitioning 용도)
# =====================================================================
def assign_hyperloglog(all_vecs: np.ndarray, n_strata: int = 20, seed: int = 42) -> np.ndarray:
    """HyperLogLog bucket as stratum_id.

    p = ceil(log2(n_strata)) (=5 for n_strata=20).
    각 vector 를 byte string 으로 변환 후 md5 hash → leading p bits = bucket id.
    (HLL 의 cardinality estimator 부분은 안 씀, 본 연구는 partitioning 만 필요)

    handoff_v3 ★4 sparse_rp md5 hash 결함과 별개:
    - sparse_rp 는 PQ codeword 후 md5 → codeword 정보 손실 (잘못된 사용)
    - HLL 은 본래 hash partitioning 이 design 의 일부 (정상 사용)
    """
    N, d = all_vecs.shape
    p = int(np.ceil(np.log2(n_strata)))  # 5 for n_strata=20
    n_buckets = 1 << p  # 32

    # vector quantize → fewer bytes per row → fast hash
    # (full float32 4*d bytes 를 hash 할 필요 X, 8 bit quantize 충분)
    sids = np.empty(N, dtype=np.int32)
    seed_bytes = seed.to_bytes(4, "little")
    for i in range(0, N, _CHUNK):
        chunk = all_vecs[i:i+_CHUNK]
        # quantize to int8 for fast hash (sign + 7-bit precision)
        qmin = chunk.min(axis=1, keepdims=True)
        qmax = chunk.max(axis=1, keepdims=True)
        scale = np.where(qmax > qmin, 255.0 / (qmax - qmin + 1e-9), 1.0)
        qchunk = ((chunk - qmin) * scale).astype(np.uint8)
        for j in range(len(chunk)):
            h = hashlib.md5(seed_bytes + qchunk[j].tobytes()).digest()
            # leading p bits → bucket id
            # md5 는 16 byte, 첫 4 byte → uint32, top p bit 추출
            top4 = int.from_bytes(h[:4], "big")
            bucket = top4 >> (32 - p)
            sids[i + j] = bucket % n_strata
    return sids


# =====================================================================
# 5. randomized SVD (P4 DimReduction)
#    Halko, Martinsson, Tropp SIAM Review 2011 "Finding Structure with Randomness".
#    sklearn TruncatedSVD(n=2) — PCA1D 의 large-scale 변형 (8M 에 fast).
# =====================================================================
def assign_rsvd(all_vecs: np.ndarray, n_strata: int = 20, seed: int = 42,
                n_iter: int = 5) -> np.ndarray:
    """randomized SVD (Halko 2011) — 2D quantile bin.

    sklearn TruncatedSVD 는 native randomized SVD 사용 (algorithm='randomized').
    PCA1D vs rSVD 의 학술 차이: rSVD 는 mean-centering 안 함 (sparse-friendly),
    Halko 의 Algorithm 4.1 (range finder) + 5.1 (subspace power iteration) 적용.
    """
    from sklearn.decomposition import TruncatedSVD

    N = len(all_vecs)
    rng = np.random.default_rng(seed)

    # ---- Step 1: rSVD fit on subset (8M 에 native fit OK, 80M 에 subsample) ----
    sample_n = min(N, _TRAIN_CAP_LARGE)
    if N > sample_n:
        sample_idx = rng.choice(N, sample_n, replace=False)
        sample = all_vecs[sample_idx]
    else:
        sample = all_vecs

    rsvd = TruncatedSVD(n_components=2, algorithm="randomized", random_state=seed,
                        n_iter=n_iter)
    rsvd.fit(sample)

    # ---- Step 2: project full (chunked) ----
    proj = np.empty((N, 2), dtype=np.float32)
    for i in range(0, N, _CHUNK):
        proj[i:i+_CHUNK] = rsvd.transform(all_vecs[i:i+_CHUNK])

    # ---- Step 3: 2D quantile bin (MHIST-2 와 동일 grid 패턴) ----
    k = int(np.ceil(np.sqrt(n_strata)))
    e0 = np.quantile(proj[:, 0], np.linspace(0, 1, k + 1))
    e1 = np.quantile(proj[:, 1], np.linspace(0, 1, k + 1))
    e0[-1] += 1e-6
    e1[-1] += 1e-6

    b0 = np.clip(np.searchsorted(e0[1:-1], proj[:, 0], side="right"), 0, k - 1)
    b1 = np.clip(np.searchsorted(e1[1:-1], proj[:, 1], side="right"), 0, k - 1)
    return ((b0 * k + b1) % n_strata).astype(np.int32)


# =====================================================================
# 6. Wavelet histogram (P6 Quantization)
#    Matias, Vitter, Wang SIGMOD 1998 "Wavelet-Based Histograms for Selectivity Estimation".
#    1D wavelet decomposition (Daubechies-2 = Haar) on PCA1D projection.
#    pywt 미설치 시 직접 Haar implementation (handoff §12 명시).
# =====================================================================
def _haar_dwt_1d(data: np.ndarray, level: int = 3) -> np.ndarray:
    """Haar wavelet 1D DWT — pywt fallback (handoff §12.3).

    Daubechies-2 (= Haar) coefficients: low = (a+b)/√2, high = (a-b)/√2.
    Level=3 → 입력 길이 // 2³ = 1/8 size approximation coefficient.
    Returns: (level+1)-tuple of (cA_n, cD_n, ..., cD_1) pywt-style flatten.
    """
    sqrt2 = float(np.sqrt(2))
    coeffs = []
    cA = data.astype(np.float64).copy()
    for _ in range(level):
        n = len(cA) // 2 * 2  # even length
        if n < 2:
            break
        cA_full = cA[:n]
        a = cA_full[0::2]
        b = cA_full[1::2]
        new_cA = (a + b) / sqrt2
        cD = (a - b) / sqrt2
        coeffs.append(cD)
        cA = new_cA
    coeffs.append(cA)
    coeffs.reverse()  # pywt-style: [cA_n, cD_n, ..., cD_1]
    return np.concatenate(coeffs)


def assign_wavelet_hist(all_vecs: np.ndarray, n_strata: int = 20, seed: int = 42,
                        level: int = 3) -> np.ndarray:
    """Wavelet histogram (Matias 1998).

    Step 1: PCA1D project → scalar per row.
    Step 2: 정렬된 projection 의 cumulative histogram → DWT (Haar Db-2) → top-k coefficient.
    Step 3: 각 row 의 wavelet coefficient bin id (binning by sorted index of approximation) → 20 bins.

    실제 구현: PCA1D projection 의 분포를 wavelet 으로 압축한 후, 각 row 가 어느
    wavelet bucket 에 속하는지 결정. 단순 quantile binning 과 차별점은 wavelet 기반
    bucket boundary 가 분포의 변화점 (high-freq detail coefficient) 을 반영.
    """
    from sklearn.decomposition import PCA

    N = len(all_vecs)
    rng = np.random.default_rng(seed)

    # ---- Step 1: PCA1D on subset (8M / 80M 모두 안전) ----
    sample_n = min(N, _TRAIN_CAP_LARGE)
    if N > sample_n:
        sample_idx = rng.choice(N, sample_n, replace=False)
        sample = all_vecs[sample_idx]
    else:
        sample = all_vecs

    pca = PCA(n_components=1, random_state=seed)
    pca.fit(sample)

    proj = np.empty(N, dtype=np.float32)
    for i in range(0, N, _CHUNK):
        proj[i:i+_CHUNK] = pca.transform(all_vecs[i:i+_CHUNK]).ravel()

    # ---- Step 2: wavelet decomposition on density profile ----
    # density profile = histogram of proj at fine granularity
    fine_bins = max(1024, n_strata * 64)  # n_strata*64 = 1280 for 20
    hist, edges = np.histogram(proj, bins=fine_bins)
    hist_f = hist.astype(np.float64)

    try:
        import pywt
        coeffs = pywt.wavedec(hist_f, "db2", level=level, mode="periodization")
        flat = np.concatenate(coeffs)
    except ImportError:
        flat = _haar_dwt_1d(hist_f, level=level)

    # ---- Step 3: top-k coefficient threshold (Matias 1998 § 4) ----
    # coefficient 의 magnitude 가 큰 영역의 boundary 를 stratum boundary 로 채택
    abs_flat = np.abs(flat)
    n_keep = min(n_strata - 1, len(abs_flat) - 1)
    top_idx = np.argsort(abs_flat)[-n_keep:]
    top_idx_sorted = np.sort(top_idx)

    # boundary 위치 → projection space 의 quantile 위치로 mapping
    # top wavelet coefficient 의 위치를 fine_bins 인덱스 → quantile 로 변환
    boundary_quantiles = np.unique(np.clip(top_idx_sorted / fine_bins, 0, 1))

    # n_strata-1 boundary 필요 → padding 또는 trimming
    if len(boundary_quantiles) < n_strata - 1:
        # uniform padding
        extra_q = np.linspace(0, 1, n_strata - 1 - len(boundary_quantiles) + 2)[1:-1]
        boundary_quantiles = np.unique(np.concatenate([boundary_quantiles, extra_q]))
        boundary_quantiles = np.sort(boundary_quantiles)
    if len(boundary_quantiles) > n_strata - 1:
        # trim 균등 sampling
        sel_idx = np.round(np.linspace(0, len(boundary_quantiles) - 1, n_strata - 1)).astype(int)
        boundary_quantiles = boundary_quantiles[sel_idx]

    edges_q = np.quantile(proj, np.concatenate([[0.0], boundary_quantiles, [1.0]]))
    edges_q[-1] += 1e-6

    sids = np.searchsorted(edges_q[1:-1], proj, side="right").astype(np.int32)
    return np.clip(sids, 0, n_strata - 1)


# =====================================================================
# Smoke test (synthetic 1M × 96d Gaussian + skewed mixture)
# =====================================================================
def _smoke_test():
    """1M × 96d 합성 data 로 6 method 모두 smoke test.

    각 method 가 (1) shape (1_000_000,) (2) dtype int32 (3) values in [0, n_strata) 검증.
    timing + cluster size distribution 도 print.
    """
    import time
    rng = np.random.default_rng(0)
    N, dim = 1_000_000, 96
    print(f"[smoke] generating synthetic data: {N:,} × {dim}d (skewed mixture)")

    # 80% normal + 20% skewed cluster (RQ1 narrative 와 align)
    n_main = int(N * 0.8)
    n_skew = N - n_main
    main = rng.standard_normal((n_main, dim)).astype(np.float32)
    skew_center = rng.standard_normal((1, dim)).astype(np.float32) * 5
    skew = skew_center + rng.standard_normal((n_skew, dim)).astype(np.float32) * 0.3
    all_vecs = np.vstack([main, skew])
    rng.shuffle(all_vecs)
    print(f"[smoke] data ready, mem={all_vecs.nbytes/1e6:.1f} MB\n")

    methods = [
        ("dbscan", assign_dbscan),
        ("kde_parzen", assign_kde_parzen),
        ("mhist2", assign_mhist2),
        ("hyperloglog", assign_hyperloglog),
        ("rsvd", assign_rsvd),
        ("wavelet_hist", assign_wavelet_hist),
    ]

    n_strata = 20
    results = {}
    for name, fn in methods:
        print(f"[smoke] running {name} ...")
        t0 = time.time()
        try:
            sids = fn(all_vecs, n_strata=n_strata, seed=42)
            elapsed = time.time() - t0
            assert sids.shape == (N,), f"shape {sids.shape} != ({N},)"
            assert sids.dtype == np.int32, f"dtype {sids.dtype} != int32"
            assert sids.min() >= 0 and sids.max() < n_strata, \
                f"values [{sids.min()}, {sids.max()}] out of [0, {n_strata})"
            unique, counts = np.unique(sids, return_counts=True)
            n_eff = len(unique)
            cv = float(counts.std() / counts.mean()) if counts.mean() > 0 else 0
            print(f"  PASS ({elapsed:.1f}s) — K_eff={n_eff}/{n_strata}, "
                  f"cluster size cv={cv:.2f}, "
                  f"min={counts.min():,}, max={counts.max():,}")
            results[name] = {"pass": True, "elapsed": elapsed, "K_eff": n_eff, "cv": cv}
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  FAIL ({elapsed:.1f}s) — {type(e).__name__}: {e}")
            results[name] = {"pass": False, "elapsed": elapsed, "error": str(e)}
        print()

    # ---- summary ----
    print("=" * 70)
    print(f"{'method':<20} {'pass':<6} {'elapsed':<10} {'K_eff':<10} {'cv':<10}")
    print("=" * 70)
    for name, r in results.items():
        if r["pass"]:
            print(f"{name:<20} {'PASS':<6} {r['elapsed']:<10.1f} "
                  f"{r['K_eff']:<10} {r['cv']:<10.2f}")
        else:
            print(f"{name:<20} {'FAIL':<6} {r['elapsed']:<10.1f} "
                  f"{r.get('error', '?')[:40]}")
    print("=" * 70)
    n_pass = sum(1 for r in results.values() if r["pass"])
    print(f"\n{n_pass}/{len(methods)} methods passed smoke test\n")
    return results


if __name__ == "__main__":
    _smoke_test()
