# RQ3 Method 간 정보 Redundancy 분석 (Adjusted Rand Index)

10 RQ3 method 가 같은 row 에 같은 stratum 부여하는 정도를 ARI 로 정량.
ARI = 1.0 → 완전 동의 (정보 redundant). ARI = 0.0 → 완전 독립.

synthetic data 3종 (iid 96d / clustered DEEP-like 96d / skewed SIFT-like 128d)
에서 same fit sample (5K) + same all_vecs 로 fit + assign, pairwise ARI 측정.

## Pairwise ARI (clustered DEEP-like, 5K samples × 50K all_vecs)

| method ↓ \ method → | minibatch | minibatch_partial | random_proj | pca1d | hilbert | zorder | hybrid | kdtree | pq | lsh | spectral | birch | gmm | hdbscan | sobol | sparse_rp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `minibatch` | 1.00 | 1.00 | 0.59 | 0.46 | 0.51 | 0.51 | 0.66 | 0.61 | 0.56 | 0.42 | 1.00 | 1.00 | 0.97 | 1.00 | 0.51 | 0.22 |
| `minibatch_partial` | 1.00 | 1.00 | 0.59 | 0.46 | 0.51 | 0.51 | 0.66 | 0.61 | 0.56 | 0.42 | 1.00 | 1.00 | 0.97 | 1.00 | 0.51 | 0.22 |
| `random_proj` | 0.59 | 0.59 | 1.00 | 0.27 | 0.29 | 0.28 | 0.39 | 0.38 | 0.34 | 0.30 | 0.59 | 0.59 | 0.57 | 0.59 | 0.32 | 0.13 |
| `pca1d` | 0.46 | 0.46 | 0.27 | 1.00 | 0.38 | 0.33 | 0.34 | 0.29 | 0.25 | 0.20 | 0.46 | 0.46 | 0.45 | 0.46 | 0.33 | 0.10 |
| `hilbert` | 0.51 | 0.51 | 0.29 | 0.38 | 1.00 | 0.54 | 0.36 | 0.33 | 0.28 | 0.21 | 0.51 | 0.51 | 0.49 | 0.51 | 0.37 | 0.10 |
| `zorder` | 0.51 | 0.51 | 0.28 | 0.33 | 0.54 | 1.00 | 0.38 | 0.33 | 0.29 | 0.21 | 0.51 | 0.51 | 0.49 | 0.51 | 0.35 | 0.11 |
| `hybrid` | 0.66 | 0.66 | 0.39 | 0.34 | 0.36 | 0.38 | 1.00 | 0.43 | 0.48 | 0.28 | 0.66 | 0.66 | 0.65 | 0.66 | 0.39 | 0.14 |
| `kdtree` | 0.61 | 0.61 | 0.38 | 0.29 | 0.33 | 0.33 | 0.43 | 1.00 | 0.36 | 0.25 | 0.61 | 0.61 | 0.59 | 0.61 | 0.32 | 0.13 |
| `pq` | 0.56 | 0.56 | 0.34 | 0.25 | 0.28 | 0.29 | 0.48 | 0.36 | 1.00 | 0.28 | 0.56 | 0.56 | 0.54 | 0.56 | 0.31 | 0.12 |
| `lsh` | 0.42 | 0.42 | 0.30 | 0.20 | 0.21 | 0.21 | 0.28 | 0.25 | 0.28 | 1.00 | 0.42 | 0.42 | 0.41 | 0.42 | 0.25 | 0.12 |
| `spectral` | 1.00 | 1.00 | 0.59 | 0.46 | 0.51 | 0.51 | 0.66 | 0.61 | 0.56 | 0.42 | 1.00 | 1.00 | 0.97 | 1.00 | 0.51 | 0.22 |
| `birch` | 1.00 | 1.00 | 0.59 | 0.46 | 0.51 | 0.51 | 0.66 | 0.61 | 0.56 | 0.42 | 1.00 | 1.00 | 0.97 | 1.00 | 0.51 | 0.22 |
| `gmm` | 0.97 | 0.97 | 0.57 | 0.45 | 0.49 | 0.49 | 0.65 | 0.59 | 0.54 | 0.41 | 0.97 | 0.97 | 1.00 | 0.97 | 0.51 | 0.21 |
| `hdbscan` | 1.00 | 1.00 | 0.59 | 0.46 | 0.51 | 0.51 | 0.66 | 0.61 | 0.56 | 0.42 | 1.00 | 1.00 | 0.97 | 1.00 | 0.51 | 0.22 |
| `sobol` | 0.51 | 0.51 | 0.32 | 0.33 | 0.37 | 0.35 | 0.39 | 0.32 | 0.31 | 0.25 | 0.51 | 0.51 | 0.51 | 0.51 | 1.00 | 0.12 |
| `sparse_rp` | 0.22 | 0.22 | 0.13 | 0.10 | 0.10 | 0.11 | 0.14 | 0.13 | 0.12 | 0.12 | 0.22 | 0.22 | 0.21 | 0.22 | 0.12 | 1.00 |

## 핵심 pair 정보 redundancy

| pair | iid 96d | clustered 96d | skewed 128d | 해석 |
|------|--------:|--------------:|------------:|------|
| `hilbert` ↔ `zorder` | +0.437 | +0.538 | +0.463 | PCA+quantile 동일, curve 만 다름 → ARI 가 PCA 효과 dominance 정량 |
| `hilbert` ↔ `pca1d` | +0.195 | +0.375 | +0.320 | 1D vs 2D curve — PCA 차원 효과 |
| `zorder` ↔ `pca1d` | +0.137 | +0.329 | +0.231 | 1D vs 2D curve (curve X) — Z-order 의 curve 효과 |
| `minibatch` ↔ `minibatch_partial` | +0.009 | +1.000 | +0.566 | batch vs streaming — partial_fit production cost |
| `hybrid` ↔ `minibatch` | +0.010 | +0.663 | +0.337 | hybrid 가 outer KMeans 정보 보존? |
| `hybrid` ↔ `hilbert` | +0.007 | +0.365 | +0.197 | hybrid 가 inner Hilbert 정보 보존? |
| `kdtree` ↔ `minibatch` | +0.006 | +0.610 | +0.273 | tree paradigm vs cluster paradigm |
| `pq` ↔ `minibatch` | +0.009 | +0.556 | +0.636 | PQ 가 sub-vector 독립 학습 → MiniBatch 와 차이 |
| `lsh` ↔ `random_proj` | +0.004 | +0.295 | +0.415 | 둘 다 hyperplane 기반 |
| `hilbert` ↔ `minibatch` | +0.009 | +0.510 | +0.245 | PCA(2D) curve vs full-D KMeans |

## 정보 grouping (ARI > 0.2 on clustered dataset)

- **group 0**: `minibatch`, `minibatch_partial`, `random_proj`, `pca1d`, `hilbert`, `zorder`, `hybrid`, `kdtree`, `pq`, `lsh`, `spectral`, `birch`, `gmm`, `hdbscan`, `sobol`, `sparse_rp`

## RQ3 narrative 결론

1. **Hilbert vs Z-order ARI** 가 클수록 → curve 자체보다 PCA+quantile 가 핵심.
   작을수록 → curve 의 locality 가 결정적 (W1-C 의 mechanism 분석과 cross-check).
2. **Hilbert vs PCA-1D ARI** 가 클수록 → 2D curve 가 1D quantile 대비 추가 정보 X.
   작을수록 → 2D 가 정보 추가.
3. **MiniBatch vs MiniBatch-partial ARI** 가 클수록 → streaming 으로 batch 와
   동일 cluster 회복 가능 (partial_fit production 채택 정당화).
4. **Hybrid vs MiniBatch / Hilbert ARI** — hybrid 가 어느 쪽 information 더 가짐?
   양쪽 모두 우수면 정보 직교 결합 성공. 한쪽 dominant 면 information loss.
5. **method group**: 비슷한 method 들이 같은 group 에 모이면 본 연구의 N-way
   measurement 가 정보적으로 N 개 method 인지 평가.

**측정 결과 비교**: 본 분석의 ARI 패턴이 실측 recovery_rate 패턴과 일치하면
narrative 강화. 다르면 — ARI 가 stratum 동의 정도만 측정, q_error 효과는 추가
factor (stratum 내 variance 등) 라는 별도 분석 필요.
