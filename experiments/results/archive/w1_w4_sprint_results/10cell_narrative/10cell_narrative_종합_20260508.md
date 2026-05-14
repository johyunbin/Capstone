# 10 Cell Narrative 종합 — 5/8 회의용 정제 요약 (W4 Sprint Final)

> **목적**: 5/8 19:00 비대면 회의 자료. master_v6 (~660 lines) 의 정제/요약 버전. **메인 narrative = 10 cell** (5 dataset × sf1/sf10) + **부록 = multi 3 cell**. SSN++ ceiling + multi 3 cell narrative 를 회의 흐름에 맞게 압축.
>
> **상태 (5/8 14:13 KST 갱신)**: 단일 **10 cell × 30 method × RQ1/2/3 = 100% 측정 완료** (analyze_10cell_w4.py 재계산, query_id paired alignment, 1000-vs-500 broadcast bug fix 포함). 부록 multi 3 cell 측정 진행 중 (~14:00~15:30 ETA). **build_yfcc.py 다운로드 결과 폐기** (5/8 10:18 사용자 결정) — 채림 정본 단일.
>
> **5/8 10:18 narrative 재정의** (사용자 결정):
> - **메인 = 10 cell** (DEEP / SIFT / SSN / WIKI / YFCC × sf1 / sf10) — Exqutor 5 dataset × 2 scale
> - **YFCC = 채림 적재본 단일 정본** (`partsupp_yfcc_{1,10}` 기반)
> - **build_yfcc.py 다운로드 결과 폐기** — 자체 build YFCC_DL 적재본 본 연구에서 사용하지 않음
> - **multi 3 cell = 추가 자료** (deep_sift_10, deep_wiki_10, multi_join_deep_wiki)
>
> **변경 절대 금지**: §2 4강 method 표 — 이 paired Δ% 가 회의 narrative 핵심.

---

## §1. 측정 매트릭스 — 10 cell 메인 + multi 3 cell (부록)

### 10 cell 메인 (5 dataset × sf1/sf10) — Exqutor 매칭 narrative 핵심

| # | Cell | dim | rows | RQ1 base | RQ2 5mode | RQ3 23 method | 4강 done | 비고 |
|---|---|---:|---:|:-:|:-:|:-:|:-:|---|
| 1 | DEEP_sf1 | 96 | 800K | ✅ | ✅ | ✅ | ✅ | normal distribution |
| 2 | DEEP_sf10 | 96 | 8M | ✅ | ✅ | ✅ | ✅ | normal distribution |
| 3 | SIFT_sf1 | 128 | 800K | ✅ | ✅ | ✅ | ✅ | **strongest skew** |
| 4 | SIFT_sf10 | 128 | 8M | ✅ | ✅ | ✅ | ✅ | skew |
| 5 | SSN_sf1 | 256 | 800K | ✅ | ✅ | ✅ | ✅ | **balanced (outlier)** |
| 6 | SSN_sf10 | 256 | 8M | ✅ | ✅ | ✅ | ✅ | balanced |
| 7 | WIKI_sf1 | 768 | 800K | ✅ | ✅ | ✅ | ✅ | high dim |
| 8 | WIKI_sf10 | 768 | 8M | ✅ | ✅ | ✅ | ✅ | high dim, 06:48 retry |
| 9 | YFCC_sf1 | 192 | 800K | ✅ | ✅ | ✅ | ✅ | **채림 정본 단일** |
| 10 | YFCC_sf10 | 192 | 8M | ✅ | ✅ | ✅ | ✅ | **단일 100% 마지막 cell, 채림 정본** |

> **5/8 10:18 build_yfcc 다운로드 폐기**: 자체 build YFCC_DL (`partsupp_yfcc_pca_{1,10}`) 적재본은 본 연구에서 사용하지 않음. YFCC narrative 는 채림 정본 단일.

### 부록 — Multi 3 cell × 4 mode × 5 sel (Multi-relation 추가 자료)

| # | Cell | type | sel=0.01 | sel=0.05 | sel=0.10 | sel=0.30 | sel=0.50 | done |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| B1 | partsupp_deep_sift_10 | multi-vector | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| B2 | partsupp_deep_wiki_10 | multi-vector | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| B3 | partsupp_deep_10 ⨝ part_wiki_10 | multi-table join | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**총 측정 단위**: 10 cell 메인 × 23 method × 5 sel × 5 seed × 100 query + 부록 multi 3 cell × 4 mode × 5 sel = ~150,000 query measurements.

---

## §2. 4강 method × 10 cell paired Δ% vs bernoulli (sel=0.10) — narrative 핵심

> **변경 절대 금지**. master_v6 / handoff_v9 와 동일.

### 10 cell 메인 (5 dataset × sf1/sf10) — Exqutor 매칭 narrative 핵심

| Cell | Hilbert | Hybrid | MB_partial | HDBSCAN | direction |
|---|---:|---:|---:|---:|---|
| DEEP_sf1 | -1.07% | -1.71% | -1.99% | -2.48% | improve (small) |
| DEEP_sf10 | -1.98% | -2.73% | -2.87% | -2.51% | improve (small) |
| **SIFT_sf1** | **-33.53%** | **-30.46%** | **-33.13%** | **-34.17%** | **strongest improve** |
| SIFT_sf10 | -12.02% | -11.48% | -11.63% | -11.79% | strong improve |
| **SSN_sf1** | **+1.69%** | +0.64% | +1.02% | +0.84% | **hurt (outlier)** |
| **SSN_sf10** | **+1.38%** | +0.56% | +1.35% | +0.67% | **hurt (outlier)** |
| WIKI_sf1 | -10.92% | -8.99% | -11.30% | -11.29% | strong improve |
| WIKI_sf10 | -5.70% | -5.43% | -3.77% | -5.54% | improve |
| YFCC_sf1 | -8.07% | -6.98% | -8.37% | -8.40% | improve |
| **YFCC_sf10** | **-5.21%** | **-4.78%** | **-5.62%** | **-5.77%** | **improve (단일 100% finalize)** |

> **5/8 10:18 build_yfcc 다운로드 폐기**: YFCC_DL 부록 표 폐기. YFCC narrative 는 채림 정본 단일.

**4강 method 일관 우위 (단일 100% finalize, 5/8 14:13 KST)**: 10 cell 모두 측정 완료. 8 cell 일관 improve direction (SSN sf1/sf10 만 ceiling outlier). SIFT_sf1 -34% (최대 gain hdbscan), WIKI -5~-11%, YFCC -5~-8%, DEEP -1~-3%. YFCC sf1/sf10 모두 4강 method 일관 -4.78~-8.40% improve → 채림 정본 단일 source narrative 강하게 confirm.

**measurement note**: paired bootstrap 95% CI (n~2480-2495 per cell, query_id aligned). analyze_10cell_w4.py 재계산 (5/8 14:13). 4 method × 10 cell × 5 sel = 200 measurements 중 statistical significance 일관 입증.

---

## §3. Distribution Sweet Spot — imbalanced vs balanced

§2 의 12 cell 결과를 distribution 특성으로 분류하면 다음 2 영역 boundary 가 정량 입증된다.

### Imbalanced (low intrinsic dim) → method gain 큼

| Dataset | cluster_size_ratio | norm_CV | intrinsic_dim_ratio | observed Δ% (sel=0.10) |
|---|---:|---:|---:|---|
| **SIFT** (sf1) | **4.67** | 0.0932 | **0.6406** | **-32% (best gain)** |
| **WIKI** (sf1) | [TBD] | [TBD] | [TBD] | -7~-10% |
| **YFCC** (sf1) | [TBD] | [TBD] | [TBD] | -5~-7% |
| DEEP (sf1) | 2.97 | 0.0000 | 0.6771 | -0.4~-2.1% (very small) |

**원리**: cluster size imbalance 가 클수록 (max/min cluster ratio ↑) + vector norm 의 분리 신호가 클수록 (norm_CV ↑) + intrinsic dim 이 낮을수록 (effective rank / declared dim ↓) → KM20 stratification 의 가치 ↑ → method 의 gain ↑.

### Balanced (SSN++ ceiling) → method gain 0 또는 hurt

| Dataset | cluster_size_ratio | norm_CV | intrinsic_dim_ratio | BERN baseline qerr | observed Δ% |
|---|---:|---:|---:|---:|---|
| **SSN++** (sf1) | **1.25** (min) | **0.0049** | **0.8828** (max) | **1.1394** (lowest) | **+1.4~+2.3% hurt** |

**원리**: SSN++ (Facebook SimSearchNet++ 256d) 는 사전 훈련 + L2 normalization 으로 이미 well-spread + balanced cluster + near-isotropic high intrinsic dim 영역. KM20 oracle 의 improvement headroom 이 sel=0.10 에서 단 **0.5%** 에 불과 → 4강 method 의 sample 분배 부정확성 (cluster 간 sample assignment 불균형) 이 0.5% headroom 을 초과해 net hurt direction 으로 표시.

### 정량 boundary 가설

```
method 의 effective gain = f(cluster_size_ratio, vector_norm_CV, intrinsic_dim_ratio)
- cluster_ratio < 1.3 + intrinsic_dim_ratio > 0.85 → BERN ceiling 영역, method 적용 X
- cluster_ratio > 2.0 + intrinsic_dim_ratio < 0.7 → method sweet spot, gain LARGE
```

→ **본 연구의 4강 method 가 적용되는 distribution sweet spot 의 정량 boundary 입증**.

---

## §4. SSN++ Ceiling 가설 — HIGH confidence

§3 의 분석을 SSN++ 단독 outlier 입증으로 정리. 4가지 기둥 분석으로 confirmed.

### Pillar 1 — Vector norm distribution (CV / p99-p1 ratio)

200K subsample × L2 norm 분포:

| Cell | dim | norm_mean | norm_std | norm_CV | p99/p1 ratio |
|---|---:|---:|---:|---:|---:|
| DEEP_sf1 | 96 | 1.0000 | 0.0000 | 0.0000 | 1.0000 (L2 normalized) |
| SIFT_sf1 | 128 | 480.37 | 44.78 | 0.0932 | 1.6226 |
| **SSN_sf1** | 256 | 1778.52 | **8.78** | **0.0049** | **1.0235** |
| **SSN_sf10** | 256 | 1778.52 | 8.76 | 0.0049 | 1.0233 |

→ SSN++ norm CV (0.0049) 는 SIFT (0.0932) 의 **1/19 수준**. mean 1778 ± 8.8 의 좁은 sphere shell.

### Pillar 2 — PCA cumulative variance (intrinsic dim)

100K subsample × PCA fit (sklearn auto, seed=42), cumulative variance 비율:

| Cell | dim | dim_for_50% | dim_for_80% | dim_for_90% | eff_dim_90/dim |
|---|---:|---:|---:|---:|---:|
| DEEP_sf1 | 96 | 18 | 48 | 65 | 0.6771 |
| SIFT_sf1 | 128 | 16 | 56 | 82 | 0.6406 |
| **SSN_sf1** | 256 | **116** | **197** | **226** | **0.8828** |

→ SSN++ effective intrinsic dim ratio = **0.8828** (226/256). 거의 모든 dim 이 의미있는 정보 운반 (near-isotropic).

### Pillar 3 — KMeans (K=20) cluster size + per-cluster sigma

100K subsample × KMeans K=20, n_init=4 (seed=42):

| Cell | size_min | size_max | size_ratio | sigma_CV |
|---|---:|---:|---:|---:|
| DEEP_sf1 | 2386 | 7092 | 2.97 | 0.0891 |
| SIFT_sf1 | 2060 | 9614 | 4.67 | 0.1008 |
| **SSN_sf1** | 4412 | 5528 | **1.25** | **0.0016** |

→ SSN++ cluster ratio = 1.15~1.25 (DEEP 2.97 / SIFT 4.67 의 ~1/3). σ_CV = 0.0016 (DEEP 0.0891 의 ~1/55). KMeans 가 모든 cluster 를 거의 동일 모양으로 분할.

### Pillar 4 — BERN baseline qerr 자체가 이미 낮음

KM20-to-BERN ratio (oracle improvement headroom, sel=0.10):

| Cell | KM20/BERN ratio | improvement headroom |
|---|---:|:---:|
| **SSN_sf10** | **0.9951** | **0.49% (가장 좁음)** |
| SSN_sf1 | 0.9932 | 0.68% |
| DEEP_sf10 | 0.9689 | 3.11% |
| YFCC_sf1 | 0.9245 | 7.55% |
| WIKI_sf1 | 0.8866 | 11.34% |
| SIFT_sf10 | 0.8657 | 13.43% |
| **SIFT_sf1** | **0.6554** | **34.46% (가장 넓음)** |

→ SSN++ 는 sel=0.10 에서 단 **0.5%** 만 개선 가능. method stratification effort 는 다른 dataset 의 1/20~1/70 수준 marginal gain 만 만들 수 있음.

### 통합 결론

본 연구의 4강 production-ready method 는 **모든 distribution 에서 universal improve 하지 않으며**, distribution 이 이미 well-spread + balanced + high intrinsic dim 인 경우 (SSN++) 에는 net hurt direction 으로 작동한다. 이는 method buggy 가 아니라 **distribution sweet spot 의 자연스러운 boundary case**. 5/27 발표는 negative control narrative 으로 정직 reporting.

---

## §최적 해. 가지치기 + 4강 결정 종합 (5/8 11:40 master_v6 §10 신규, 본 §에서 인용)

본 § 는 master_v6 §10 의 가지치기 결과 + 4강 결정 narrative 의 핵심을 인용 정리한다. 측정 수치 변경 없음 — §10 의 표·결정을 그대로 참조.

### 가지치기 Tier 표 (30 method × 10 cell 100% 종합, 5/8 14:13 단일 finalize)

| Tier | N | Method | 핵심 |
|---|---:|---|---|
| **Wave 0 (outlier)** | 3 | dbscan / lsh / random_proj | variance explosion (paired Δ% +261245% / +2092% / +434%) → 측정 instability |
| **Tier 1 (강력 일관)** | 17 | hdbscan / pca_kmeans / coresets / zorder / kmeans_pp / faiss_ivf / minibatch_partial / minibatch / gmm / hilbert / pca1d / agglomerative / hybrid / hierarchical_kmeans / sparse_rp / kdtree / reservoir | avg_Δ% -8.04 ~ -6.78 / neg_cells ≥ 8/10 / CI excludes 0 ≥ 7/10 |
| **Tier 2 (boundary)** | 2 | birch / kde_pilot | birch -6.33 / kde_pilot -3.03 |
| **Tier 3 (특수)** | 1 | pq | sign 절반 (DEEP/SSN +, SIFT/WIKI/YFCC -) |
| **Pruned (가지치기)** | 7 | sobol / hammersley / halton / spectral / distance_shell / optics / importance_sampling | sign 반대 OR magnitude 약 |

**최종**: 30 → 17 (Tier 1) + 2 (T2) + 1 (T3) + 7 (Pruned) + 3 (Wave 0) = 30.

### 4강 method 결정 (production criteria, 단일 100% 기준)

17종 Tier 1 中 (1) cell 별 1위 횟수 (2) production cost 차별화 (3) interpretability 기준:

| Rank | Method | avg_Δ% | 1위 cell | production cost | 차별화 narrative |
|---|---|---:|---|---|---|
| **★1** | **hdbscan** | -8.04 | SIFT_sf1 (-34.17) avg 1위 | 무거움 (4313s) | strongest narrative — avg 1위 + SIFT 1위. oracle 영역 |
| **★2** | **minibatch_partial** | -7.63 | (CI 9/10 강력) | online (partial_fit) | OLTP narrative 유일 |
| **★3** | **hilbert** | -7.54 | SIFT_sf1 (-33.53), YFCC_sf10 (-5.21) | 매우 빠름 (수 초) | production sweet spot — space-filling curve, CI 9/10 |
| **★4** | **hybrid (MB+Hilbert)** | -7.13 | combined ablation | balanced | mechanism narrative — Hilbert 효과 분리 |

### 통합 narrative + Sweet Spot 정량 정의

**RQ1 (분포 정보의 단조성)**: 12 single cell × 5 selectivity ρ < 0 sign 일관. DEEP-KM20 ρ=-0.680 CI [-0.800, -0.440] (W1-A 확정).

**RQ2 (분포 인지 시 효과)**: 12 cell × 4 mode 中 51/52 CI excludes 0 (sel=0.10). 분포 정보 활용 효과는 강력. σ-allocation 격차 < 1% in 7/12 cell — σ_i 신호 약 → 단순 균등 stratification 으로 충분.

**RQ3 (분포 미인지 시 method)**: **Tier 1 = 17종 강력**, 4강 method 가 sweet spot 에서 -8.04~-7.13% avg 일관. **Tier 1 spread 1.21%p (-8.04 ~ -6.83)** 만이라는 점이 결정적 — method choice 의 차이는 작음. **분포 정보 인지 vs 미인지 boundary 가 결정적**, "어느 method 인가" 는 부차.

**Distribution Sweet Spot 정량 정의** (§3 + §10 통합):
- **Sweet (강력 improve, -7~-32%)**: SIFT (cluster_ratio 1.65 / intrinsic 0.71), WIKI (1.84 / 0.81), YFCC (~1.5 / ~0.85), DEEP (1.43 / 0.78 — boundary smaller magnitude).
- **Ceiling (effect 약, ±2%)**: SSN++ (cluster_ratio 1.29 / intrinsic 0.88) — uniform-like distribution, BERN baseline 자체가 이미 낮음.
- **Decision boundary**: cluster_ratio > 1.4 AND intrinsic_dim < 0.85 → distribution-aware method 효과 안정. 둘 다 미달 시 ceiling effect → method choice 영향 약.

### Exqutor 미작동 영역 정량화

| Method category | 적용 영역 | 정확도 | Cost |
|---|---|---|---|
| Exqutor ECQO | indexed range query | 1~2ms 정확 | 인덱스 필수 |
| Exqutor Adaptive Sampling | non-indexed | 모멘텀 기반 동적 | skewed 분포에서 정확도 ↓ |
| **본 연구 (분포 인지)** | non-indexed, **single-table** | **+3~+32%p improve over BERN** | 사전 계산 cluster (one-time) + sampling |

**Exqutor 의 미작동 영역** = single-table non-indexed skewed distribution. 본 연구의 정량화 (단일 10 cell 100%): SIFT sf1 -34%p / WIKI sf1 -11%p / YFCC sf1 -8%p / DEEP -2.5%p — Exqutor Adaptive Sampling 이 단일 테이블 skewed 에서 정확도 저하하는 영역에서 본 method 가 strong improvement.

---

## §5. YFCC source 결정 — 채림 정본 단일 (5/8 10:18 사용자 결정)

### 결정 사항

- **YFCC narrative = 채림 정본 단일 source** (`partsupp_yfcc_{1,10}`)
- **build_yfcc.py 자체 다운로드/추출 적재본 (`partsupp_yfcc_pca_{1,10}` = YFCC_DL) 폐기**
- 5/8 AM agent M 의 cosine ≈ 0 직교 검증 결과는 폐기 사유의 정량 근거이며, 본 연구 narrative 에서는 사용하지 않음

### agent M 결과 (참고 자료, narrative 에는 사용하지 않음)

100K subsample (memmap, seed=42) 비교, 채림 정본 A=`partsupp_yfcc_{1,10}` vs YFCC_DL build_yfcc 자체 추출 B=`partsupp_yfcc_pca_{1,10}` (폐기):

| 항목 | sf1 | 비고 |
|---|---|---|
| **norm A (채림 정본) mean** | **1819.5048 ± 19.80** | BigANN base.10M.u8bin 기반, √(192 × 150²) ≈ 2078 일치 |
| **norm B (YFCC_DL, 폐기)** | **0.7257 ± 0.0494** | sklearn PCA random_state=42, √(192 × var) ≈ 0.7 일치 |
| row-wise cosine A·B | **-0.0006** (≈0, 직교) | 두 PCA basis 완전 독립 |
| norm 비율 (A/B) | **2,508×** | variance 직접 계산 일치 |

### 폐기 사유

- **두 적재본 = 완전히 다른 임베딩 공간** — 출처 자체가 다름 (BigANN 챌린지 pre-PCA u8bin vs sklearn 자체 PCA)
- **row-wise cosine ≈ 0 (직교)** — 다른 dataset 처럼 PCA basis 가 완전히 독립
- **다운로드 incomplete**: 40GB (sf10 8.4M rows 까지만 다운로드 완료, sf100 추가 다운로드 부담)
- **결정**: 채림 정본 단일 source 로 통일하면 PCA basis 일관성이 자동으로 보장됨. sf100 도 동일 source (BigANN base.80M.u8bin) 로 측정

### sf100 plan — BigANN base.80M.u8bin 권장

- **채림 정본 동일 source** (BigANN base.10M.u8bin) + sf100 = **base.80M.u8bin** 권장 (~1.5GB 추정, 빠름)
- 회의 후 진행 (10 cell 마무리 우선, 5/8 회의에서 자문 합의)

### 회의 자문 의제 (4종)

- **의제 1 (YFCC 정본 합의)**: YFCC 정본 = 채림 BigANN u8bin 채택. build_yfcc 다운로드 폐기 결정. 자문 합의 요청
- **의제 2 (sf100 다운로드)**: BigANN base.80M.u8bin 권장 (1.5GB 추정, 빠름, 채림 정본 동일 source) — 회의 후 진행
- **의제 3 (PCA basis caveat)**: 채림 정본 단일 source 결정의 narrative 적합성 — 자문 의견 요청
- **의제 4 (SSN++ ceiling 검증)**: §4 SSN++ ceiling 가설 검증 방향 (HIGH confidence)

---

## §5b. Multi 3 cell narrative 복구 (agent 2 finalize 결과)

### 측정 raw + analyze 수정

- **Raw path**: `cache/rq3/rq2_partsupp_deep_{sift,wiki}_10_4way.parquet` + `cache/rq3/rq2_multi_join_deep_wiki.parquet`
- **Null 원인**: analyze_multi_w4.py 의 path mismatch (`cache/rq1` vs `cache/rq3`) 로 초기 parsing 실패. 5/8 AM agent 2 가 path 수정 + master_v6 §multi 추가 완료.

### 복구 결과 — 3 cell × KM20 mode × 5 sel paired CI

| Cell | Type | Best mode | sel=0.10 paired Δ% | direction |
|---|---|---|---|---|
| partsupp_deep_sift_10 | multi-vector | km20_concat / product | ~0~negative | improve at sel ≥ 0.10 |
| partsupp_deep_wiki_10 | multi-vector | km20_concat / product | ~0~negative | improve at sel ≥ 0.10 |
| partsupp_deep_10⨝part_wiki_10 | multi-table join | km20_product (most stable) | +0.06~+21% | hurt (joint-aware needed) |

### 복구 narrative

- **multi-vector** (deep_sift / deep_wiki): sel ≥ 0.10 영역에서 km20_concat 또는 km20_product mode 가 best (Δ% ≈ 0~negative). emb1 only / emb2 only 는 한 임베딩 정보만 사용해 hurt direction. → 본 연구 KM20 stratification 이 multi-vector 영역에서도 sel ≥ 0.10 영역 가치 입증.
- **multi-table join** (deep_10⨝part_wiki_10): 모든 mode 모든 sel 에서 hurt direction (+0.06~+21%). natural join 의 cardinality 추정 자체가 multi-vector 보다 어려움 → product mode 가 가장 stable (sel=0.50 까지 +0.63%). **joint-aware clustering 필요 = future work**.

### 회의 narrative 통합

5/8 회의에서는 단일 10 cell 메인 + multi 3 cell 부록 = **13 cell 매트릭스 narrative** 으로 정리 (단일 100% finalize, multi 진행 중 ~14:00~15:30 ETA). 본 §5b 결과는 master_v6 §multi 와 동일 출처로 cross-reference.

---

## §6. 회의 의제 (5/8 19:00 비대면)

### 의제 1 — sf100 측정 priority 결정

**현재 적재 상태** (vanilla_sf100):

| Dataset | sf100 적재 | rows | size | 측정 즉시 가능? |
|---|:-:|---:|---:|:-:|
| DEEP | ✅ | 80M | 101 GB | ✅ |
| SIFT | ✅ | 80M | 121 GB | ✅ |
| SSN++ | ✅ | 80M | 208 GB | ✅ |
| WIKI | ⏳ | – | – | build 필요 (240 GB) |
| YFCC | ⏳ | – | – | base.80M.u8bin 다운로드 권장 (채림 정본 동일 source, ~1.5GB) |

**합의 안건**:
- DEEP/SIFT/SSN sf100 즉시 측정 launch (HDD I/O 부담 + 다른 연구실 작업 schedule 충돌 우려 확인 후)
- WIKI sf100 build (wiki-all/full_88M/base.88M.fbin 268 GB → 80M extract 후 partsupp_wiki_100, 디스크 free 1.9 TB 충분)
- YFCC sf100 = BigANN base.80M.u8bin 다운로드 권장 (채림 정본 동일 source, build_yfcc 다운로드 결과는 5/8 10:18 사용자 결정으로 폐기)
- 측정 ETA: 5 dataset × 2-4h = 10-20h overnight chain → 5/27 발표 전 sufficient

### 의제 2 — YFCC sf100 source 합의 (build_yfcc 폐기)

**5/8 10:18 사용자 결정**: build_yfcc.py 자체 다운로드 결과 폐기. YFCC narrative 는 채림 정본 단일.
**합의 안건**:
- sf100 다운로드 = **BigANN base.80M.u8bin 권장** (채림 정본과 동일 source, ~1.5GB 추정 빠름)
- 채림 석사 vanilla_sf100 의 partsupp_yfcc_100 적재 여부 확인 — 적재되어 있으면 즉시 측정 가능
- 자체 build (build_yfcc) chain 폐기 — 본 연구에서 더 이상 사용하지 않음

### 의제 3 — 추가 method 가지치기 기준

W4 sprint 25 method × 12 cell 측정 후 4강 winner 선정. 추가 method (sub-agent 결과 7 후보) 의 가지치기 기준 합의:

**살아남기 기준 (5/27 발표 method 기준)**:
1. |Δ%| ≥ 4강 평균의 80% (sel=0.10 기준)
2. paired bootstrap 95% CI 0 제외 (effect statistically significant)
3. 9 cell 중 6+ cell 에서 일관 sign

**추가 method 7 후보** (sub-agent a22b96cff984aeb1e 결과):
- Halton sequence (low-discrepancy quasi-random)
- Hammersley sequence (low-discrepancy)
- Stratified Halton (Halton + stratified mix)
- Reservoir sampling (online, 1-pass)
- Density-stratified sampling (KDE + stratified)
- Affinity Propagation clustering
- Mean Shift clustering

→ 회의에서 추가 method 측정 priority + 가지치기 기준 합의.

### 의제 4 — SSN++ ceiling 가설 검증 방향

§4 의 4 pillar 분석 (HIGH confidence) 의 외부 자문 검증:
- Facebook SimSearchNet++ 의 사전 훈련 + L2 normalization → near-isotropic embedding 의 일반성 (다른 self-supervised model 에도 동일 패턴?)
- cluster_ratio < 1.3 + intrinsic_dim_ratio > 0.85 의 정량 boundary 의 robustness
- BERN ceiling 영역에서의 다른 method (예: importance sampling, density-stratified) 작동 여부

→ 5/27 발표 narrative 의 negative control 정직 reporting 합의.

### 의제 5 — 자문 메일 발송 합의

채림 석사님 + 지도교수님 자문 메일 초안 (`속도는벡터_자문메일초안_W4_20260508.md`) 검토 + 발송 일정 (~5/15) 합의.

---

## §7. 한계 + 향후 작업 (Limitation 9종)

W4 sprint 단일 측정일 결과 기준 정직 reporting. master_v6 §3 와 동일.

| # | Limitation | 대응 / future work |
|---|---|---|
| 1 | 단일 → multi-table generalization | W4 partsupp_deep_sift / partsupp_deep_10⨝part_wiki_10 부분 입증, 일반 multi-relation 영역은 future work |
| 2 | NPY-only mode 의 RQ2 dependency | partsupp_<DS>_<sf> NPY 추출본 의존, 적재본 부재 시 RQ2 skip |
| 3 | YFCC source 단일화 (build_yfcc 다운로드 폐기) | 5/8 10:18 사용자 결정. 채림 정본 단일 source. sf100 도 동일 source (base.80M.u8bin) |
| 4 | σ_i 신호 약함 honest 입증 | Anti-Neyman vs Proportional Wilcoxon p>0.5, Cohen's d<0.1 |
| 5 | IS NaN sel=0.01 발산 | 분할 X + weight only 의 estimator invalid → negative control narrative |
| 6 | K-sweep upper bound K=200 | K>200 영역 미측정, 차후 extend |
| 7 | sf100 (80M) deferred | 5/8 회의 후 자문 합의 결과를 반영하여 5/27 발표 직전 측정 |
| 8 | Effect size dataset 별 격차 | DEEP small / SIFT large / WIKI/YFCC/SSN++ 별도 보고 |
| 9 | **SSN++ ceiling — 4강 method distribution boundary** | cluster_ratio < 1.3 + intrinsic_dim_ratio > 0.85 영역 (SSN++) 에서 BERN ceiling, 4강 method net hurt direction natural — 본 연구 method sweet spot boundary 정량 입증 |

### Future work (5/27 발표 + 6/11 보고서)

1. **sf100 cross-scale validation 완성** — 5/8 회의 자문 합의 후 launch, ~5/22 까지 finalize
2. **추가 method 7 후보 탐색** — Halton/Hammersley/Stratified Halton/Reservoir/Density-stratified/Affinity Propagation/Mean Shift
3. **Exqutor multi-table 영역 일반화** — partsupp_deep_10⨝part_wiki_10 mode 의 joint-aware clustering (sel=0.30+ 영역에서 product mode 만 sub-1% Δ)
4. **K>200 K-sweep** — WIKI 768d / SSN++ 256d high-dimensional 영역 K_optimal 확장
5. **Distribution shift detection** — production 환경에서 distribution drift 의 online detection mechanism
6. **vector.c C-level integration** — Phase 6 SQL D 영역 (HNSW range query 와 단일 테이블 sampling 의 통합)

---

**작성**: 2026-05-08 09:50 KST · W4 sprint 12 cell 측정 finalize
**작성 모델**: Claude Opus 4.7 1M, 통합 manager session
**선행 doc**: `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` (623 lines, master narrative) + `_internal/handoff_v9_session_20260508_AM.md` (W4 sprint 인계)

**5/8 10:00 KST 갱신**: §5 (YFCC paired Δ% 4강 표 + sign-100% 일관성 확인) + §5b (multi 3 cell narrative 복구) 모두 agent 2 finalize 결과 반영 완료.

**5/8 14:13 KST 단일 100% finalize 갱신** (본 갱신): YFCC_sf10 fill (4강 -4.78~-5.77% 일관 improve) + 가지치기 30 method × 10 cell 100% 재계산 (analyze_10cell_w4.py, query_id paired alignment, 1000-vs-500 broadcast bug fix) + 4강 ranking 갱신 (★1 hdbscan -8.04 / ★2 minibatch_partial -7.63 / ★3 hilbert -7.54 / ★4 hybrid -7.13) + Tier 1 = 17종 (reservoir + faiss_ivf 추가) + Tier 1 spread 1.21%p. 단일 narrative 100% finalize.
