# RQ3 16-Method 종합 (W1 sprint 5/6 23:30 update)

> **5/6 21:45 1차 측정** (10 method) + **5/6 23:00 보강 코드** (6 method) + **8M sensitivity overnight** 자동 chain.
> 본 문서: 16 method 의 paradigm / 학습 비용 / 측정 상태 / 5/8 회의 narrative 위치 종합.

---

## 1. 16 method 개관 (paradigm × 학습 비용 × 결정론)

| # | Method | Paradigm | 학습 비용 | 결정론 | 측정 상태 |
|---|--------|----------|----------|--------|----------|
| Baseline | RANDOM20 | random partition | X | ✓ | ✅ DEEP+SIFT |
| Oracle | KM20 | full K-means | high (~30분) | ✓ | ✅ DEEP+SIFT |
| **Offline** | | | | | |
| 1 | MiniBatch K-means | offline cluster | medium (1% sample, ~수초) | ✓ | ✅ DEEP+SIFT |
| 2 | MiniBatch partial_fit | online cluster (streaming) | medium (incremental) | ✓ | 🔁 1M/1.5M wait |
| 3 | Random Projection | hash (Johnson-Lindenstrauss) | minimal (matrix gen) | ✓ | ✅ DEEP+SIFT |
| 4 | **PCA-1D Quantile** | dimensionality reduction | minimal (PCA) | ✓ | 🔁 1M/1.5M wait |
| 5 | **Hilbert Curve** | space-filling + PCA(2D) | minimal (PCA) | ✓ | ✅ DEEP+SIFT |
| 6 | **Z-order Curve** | space-filling + PCA(2D) | minimal (PCA) | ✓ | 🔁 1M/1.5M wait |
| 7 | **Hybrid (KMeans+Hilbert)** | nested partition | medium | ✓ | 🔁 1M/1.5M wait |
| 8 | **KD-tree Partition** | tree (axis-aligned) | minimal (median split) | ✓ | 🔁 1M/1.5M wait |
| 9 | **Product Quantization** | sub-vector quantize (FAISS) | medium (M sub-KMeans) | ✓ | 🔁 1M/1.5M wait |
| 10 | **Spectral Clustering** | graph Laplacian | high (Nystrom 변형) | △ | 🔁 1M/1.5M wait |
| 11 | **BIRCH** | tree (incremental) | medium | ✓ | 🔁 1M/1.5M wait |
| 12 | LSH | random hyperplane | minimal | ✓ | ✅ DEEP+SIFT |
| **Online** | | | | | |
| 13 | KDE-pilot | query-adaptive σ | per-query pilot | ✓ | ✅ DEEP+SIFT |
| 14 | Distance-Shell | rank-based shell | per-query | ✓ | ✅ DEEP+SIFT |
| **Weight (비분할)** | | | | | |
| 15 | Importance Sampling | weighted sample | minimal | ✓ | ✅ DEEP+SIFT (4 mode) |
| **Phase 2 추가 (5/7 새벽)** | | | | | |
| 16 | **GMM** (soft cluster) | offline soft (full / diag cov) | medium (sklearn) | ✓ | 🔁 phase2 wait |
| 17 | **HDBSCAN** | density hierarchical | medium (centroid+KMeans 보정) | ✓ | 🔁 phase2 wait |
| 18 | **Sobol** quasi-random | low-discrepancy stratification | minimal (PCA+sobol) | ✓ | 🔁 phase2 wait |
| 19 | **Sparse RP** (Achlioptas) | sparse RP variant | minimal (matrix gen) | ✓ | 🔁 phase2 wait |

**8M sensitivity (overnight 자동, 5/7 01:50 갱신)**:
- `run_8m_sensitivity.py` 실측 cover = **5 method** (minibatch / random_proj / hilbert / zorder / lsh, fit+assign 패턴) × DEEP_8M × 2 sel × 5 seed × 100 query
- KDE-pilot / Distance-Shell / IS 는 inline estimator 패턴이라 8M sensitivity 미포함
- final_chain.sh (5/7 추가) — post_8m flag 감지 → 1M extra **8 method** (zorder/hybrid/partial/pca1d/kdtree/pq/spectral/birch) + SIFT mid-sel
- phase2_chain.sh (5/7 추가) — final_chain flag 감지 → **4 missing method** (gmm/hdbscan/sobol/sparse_rp, 5/7 새벽 run_*.py 추가 작성)
- 즉 cross-scale 비교는 **5 method 8M 시점** + **17 method 1M/1.5M 시점** 으로 분리

---

## 2. Ablation Ladder — Hilbert contribution origin 분리

본 연구의 narrative 핵심: **\"Hilbert curve = learning-free + 결정론 + competitive recovery\"**.

이 결과의 origin 을 다음 ladder 로 분리:

```
BERN baseline
  ↓ + random partition (information X)
RANDOM20
  ↓ + 1D PCA (variance-aware, curve X)
PCA-1D Quantile
  ↓ + 2D PCA + Z-order curve
Z-order Curve
  ↓ + 2D PCA + Hilbert curve (locality preservation)
Hilbert Curve
  ↓ + Voronoi cluster (96D KMeans)
MiniBatch K-means
  ↓ + outer KMeans + inner Hilbert (cluster + size balanced)
Hybrid
  ↓ + perfect cluster knowledge
KM20 oracle
```

각 단계의 incremental contribution 가 본 연구의 정량 기여.

### 측정 후 narrative 결정 트리

- **PCA-1D ≈ Hilbert** → curve 효과 미미, **PCA 자체가 contribution dominant**.
- **PCA-1D ≪ Z-order ≈ Hilbert** → **2D 가 결정적**.
- **Z-order ≪ Hilbert** → **curve 자체의 locality 가 결정적** (5/6 measurement: ARI 0.479, inverse Manhattan 1.000 vs 1.992).
- **Hilbert ≈ MiniBatch** → cluster 자체보다 \"분할 자체\" 가 핵심.
- **Hybrid > MiniBatch + Hilbert** → 두 method 정보 직교 결합.

---

## 3. ARI Pairwise Redundancy (clustered DEEP-like, 5/6 측정)

| pair | iid 96d | clustered 96d | skewed 128d | 의미 |
|------|---------|---------------|-------------|------|
| Hilbert ↔ Z-order | 0.437 | **0.538** | 0.463 | curve 동의도 50% — PCA+quantile 이 절반 effect |
| Hilbert ↔ PCA-1D | 0.195 | **0.375** | 0.320 | 2D 가 1D 대비 정보 추가 |
| Z-order ↔ PCA-1D | 0.137 | 0.329 | 0.231 | Z-order 의 curve 효과 |
| MiniBatch ↔ partial_fit | 0.009 | **1.000** | 0.566 | clustered 에서 perfect 회복 (OLTP narrative 결정적) |
| Hybrid ↔ MiniBatch | 0.010 | 0.663 | 0.337 | hybrid 가 outer KMeans 정보 dominant |
| Hybrid ↔ Hilbert | 0.007 | 0.365 | 0.197 | hybrid 가 inner Hilbert 부분 유지 |
| KD-tree ↔ MiniBatch | 0.006 | 0.610 | 0.273 | tree paradigm 도 cluster 일부 회복 |
| PQ ↔ MiniBatch | 0.009 | 0.556 | **0.636** | PQ 가 SIFT-like 에서 MiniBatch 와 가장 유사 |
| LSH ↔ Random Projection | 0.004 | 0.295 | 0.415 | hash family 약 동의 |

---

## 4. Effect Size 정량 (Cohen's d, 5/6 측정 결과 기반)

| method | mean d | min d | max d | 실용 의미 |
|--------|-------:|------:|------:|----------|
| **hilbert** | -0.156 | -0.336 | -0.041 | negligible-small **improve** |
| **minibatch** | -0.151 | -0.334 | -0.050 | negligible-small **improve** |
| kde_pilot | -0.049 | -0.205 | +0.033 | negligible |
| lsh | +0.156 | +0.089 | +0.211 | negligible-small hurt |
| random_proj | +0.216 | +0.119 | +0.326 | small **hurt** |
| distance_shell | +0.490 | +0.038 | +0.758 | small-medium **hurt** |
| is_p50_clip | +0.498 | -0.169 | +0.900 | small-medium hurt |
| is_p200_noclip | +0.564 | +0.305 | +0.826 | medium **hurt** |
| is_p50_noclip | +0.642 | +0.412 | +1.127 | medium hurt |
| is_p200_clip | +0.704 | +0.301 | +1.119 | medium hurt |

**honest 한계**: Hilbert / MiniBatch 의 d 평균 -0.156 / -0.151 은 \"negligible to small\" 영역. p<0.05 만 보면 통계 유의해 보이나 practical effect 는 작음. 본 연구의 contribution claim 은 \"meaningful but small improvement\" 가 정직한 narrative.

---

## 5. Per-Query Best Method 분포 (5/6 측정)

전체 500 query × 2 dataset = 1000 cell 의 \"best (rank=1) 빈도\":

| method | DEEP | SIFT | TOTAL |
|--------|-----:|-----:|------:|
| **hilbert** | 94 | 106 | **200** |
| **minibatch** | 91 | 99 | **190** |
| kde_pilot | 82 | 92 | 174 |
| km20 (oracle) | 84 | 88 | 172 |
| random20 | 59 | 41 | 100 |
| lsh | 32 | 21 | 53 |

- **Hilbert + MiniBatch 가 KM20 oracle 보다 자주 best** — sample noise + per-query 적합성.
- **best 가 method 별로 dispersed** → 본 연구의 multi-way contribution 정당화.
- **Spread vs difficulty 상관 ρ = 0.78 (DEEP/SIFT 모두)** → 어려운 query 에서 method routing 결정적.

---

## 6. 5/8 회의 (D-2) 발표 narrative

### Slide 1 — RQ3 motivation
\"분포 모를 때 어떤 stratification 이 최적?\" — 16-method 비교.

### Slide 2 — Ablation ladder
BERN → RANDOM → PCA-1D → Z-order → Hilbert → MiniBatch → KM20.
각 단계 incremental contribution 정량.

### Slide 3 — 핵심 contribution 4종 (5/7 갱신: hdbscan 추가)
1. **Hilbert Curve = learning-free + 결정론 + competitive recovery**
   (mechanism: inverse Manhattan 1.000 vs Z-order 1.992)
2. **MiniBatch K-means = production-ready solution**
   (partial_fit 으로 OLTP 적용 가능, **paired CI 0 제외 4 cell**, ARI clustered=1.000)
3. **HDBSCAN = SIFT mid-sel best** (5/7 새벽 추가)
   (SIFT s=0.10 **-3.99%** [-5.34, -2.12] paired CI, 모든 method 중 mid-sel 가장 강. SIFT 의 더 큰 skew 가 density-based clustering 의 가치 강화)
4. **Distance-Shell + IS + PQ + Sobol = cluster 분할의 결정적 가치 정량 증명** (negative control 강화)
   (paired CI 0 제외 hurt direction. PQ DEEP s=0.01 +23.64% [+15.91, +31.80])

### Slide 3-bonus — narrative 정정 (5/7 검증 결과)
- **spectral**: recovery_summary 의 -5.39% 는 mean-of-ratios 왜곡, paired CI 검증 시 +16.71% **hurt** (CI [-0.50, +20.87]) → contribution 후보 **제외**.
- **sobol**: SIFT 모든 cell CI 0 제외 hurt direction (s=0.01 +33.62% 가장 큰 hurt) → 사용 불가.
- 따라서 5/7 새벽 추가 4 method (gmm/hdbscan/sobol/sparse_rp) 중 **유일한 contribution 후보 = HDBSCAN**.

### Slide 4 — Practical effect size 한계
\"meaningful but small\" — Cohen's d -0.156 (negligible-small). p<0.05 의 sample-size 효과 별도 보고. RAW 통계의 honest narrative.

### Slide 5 — Per-query 적합성
spread vs difficulty 0.78 — \"method routing\" 의 production 가치.

### Slide 6 — 8M sensitivity (overnight 진행)
1M/1.5M 결과의 8M 재현 검증.

---

## 7. 산출 위치 매핑

| 산출 | 경로 |
|------|------|
| 1차 측정 parquet (10 method) | `experiments/results/rq3_agnostic/rq3_*.parquet` |
| 분석 driver | `experiments/code/local_analysis/rq3_recovery_analysis.py` |
| Recovery summary CSV | `experiments/results/rq3_agnostic/recovery_summary.csv` |
| ARI matrix | `experiments/results/rq3_agnostic/rq3_method_redundancy_ari.{md,csv}` |
| Effect size + Bootstrap CI | `experiments/results/rq3_agnostic/rq3_bootstrap_effect_size.{md,csv}` |
| Per-query ranking | `experiments/results/rq3_agnostic/rq3_per_query_ranking.{md,csv}` |
| Locality mechanism | `experiments/results/rq3_agnostic/locality_curve_comparison.{md,csv}` |
| 시각화 figures | `experiments/figures/rq3_supplementary/*.png` |
| 6 추가 method 코드 | `experiments/code/rq3/{pca1d,kdtree,pq,spectral,birch,zorder,hybrid}/` |
| 8M overnight watchdog | `experiments/code/rq3/post_8m_pipeline.sh` (서버 tmux post_8m 가동 중) |

---

**작성**: 조현빈 · 2026-05-06 23:30 KST · W1 sprint 5/8 회의 D-2 (이번 세션 final)
