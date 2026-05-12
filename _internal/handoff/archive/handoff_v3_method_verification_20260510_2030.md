# Handoff v3 — 41 method 알고리즘 검증 결과 + registry 정정 결정 (5/10 20:45 KST)

> **출처**: 검증 세션 (mac-mini 로컬, 8 agent 병렬, 5,777 lines 보고서)
> **선행 handoff**: v2 (5/10 14:18 paper verbatim 5 decisions) — 본 v3 와 직교
> **종합 요약**: `_internal/method_verification_20260510/_SUMMARY.md`
> **server 영향**: server SSH 차단 상태에서 진행한 로컬 audit, 측정 결과 변경 없음. 단 measurement 진입 전 method registry 정정 권고.

---

## 0. TL;DR (메인 세션 즉시 read)

### 0.1 검증 결과 한 줄 요약
**41 method 중 신뢰 가능 6개 (★ + 견조), 30+ 건 critical defect (naming fraud / bug / redundancy / leak)**.

### 0.2 4강 학술 정합성 직격 — 즉시 결정 필요

| 4강 | score | 결과 | 즉시 조치 |
|---|---|---|---|
| ★1 hdbscan | 7/10 | minor tuning OK | K_eff<20 padding 명시, stability vs size pruning disclaimer |
| ★2 mb_partial | 8/10 | 신뢰 | (없음) |
| **★3 hilbert** | **2/10** | **PCA 2D lex sort, 진짜 Hilbert curve ❌** — 학술 fraud risk | raw `experiments/code/rq3/hilbert/hilbert_curve.py` (Wikipedia 표준) 사용 OR `pca2d_lex` rename |
| **★4 sparse_rp** | **6/10** | **Li 2006 1/√D variant 확정** (V9 audit 일치) | reference 정정: Achlioptas 2003 ❌ → Li-Hastie-Church 2006 ⭕ |

### 0.3 paradigm 평균 충실도 (낮은 순)
P6 1.6/10 (폐지 권고) > P3 3.4 > P2 3.6 > P5 4.4 > P4 4.5 > P1 5.1 / 종합 3.8

### 0.4 SF feasibility — handoff_v0 1,044 measurement scope의 97.2% 가능
- vinecopula × SF=100 3 cell만 drop 권고
- subset_training 8 method (hdbscan/birch/agglomerative/cocluster_nystrom/kdpp/epsilon_net/kdtree/hkbu_repsample) × SF=10·100 필수

---

## 1. CRITICAL 30건 — registry 정정 사항

### 1.1 학술 reference fraud / misrepresentation (15건) — paper reviewer reject 위험

| # | method | 표명 | 실제 | 결정 (rename / 폐기) |
|---|---|---|---|---|
| 1 | **★3 hilbert** | Faloutsos 1989 | PCA 2D lex sort | **raw 사용 OR `pca2d_lex` rename** |
| 2 | **★4 sparse_rp** | Achlioptas 2003 | Li 2006 1/√D | **reference 정정만 (코드 변경 X)** |
| 3 | reservoir | Vitter 1985 | RANDOM20 random | **rename `random20`** |
| 4 | thompson_sampling | Thompson 1933 | MiniBatchKMeans | **폐기** (Beta posterior 부재) |
| 5 | mfmc | Peherstorfer 2018 | KMeans+RANDOM20 mask | **폐기** (control variate 부재) |
| 6 | lpm2 | Grafström 2012 | Weiszfeld median + radial | **rename `radial_quantile`** |
| 7 | neuram | autoencoder | PCA1D 100% 동일 | **폐기** |
| 8 | cca1d | Hotelling 1936 CCA | PCA(whiten=True) | **폐기** (PCA1D bit-equal) |
| 9 | tucker | Tucker 1966 tensor | PCA(3) + 3D grid | **rename `pca3d_grid`** |
| 10 | vinecopula | Bedford-Cooke 2002 | rank+PCA1D | **rename `spearman_pca1d`** |
| 11 | ams_count_sketch | Alon-Matias-Szegedy 1996 | lsh 와 line-by-line 동일 | **폐기** |
| 12 | ccsketch | Cormode-Muthukrishnan 2005 | float mod + np.min skewed | **폐기** |
| 13 | **lp_bound** | (textbook) | **SIGMOD 2025 Best Paper LpBound (Zhang/Suciu) 명칭 충돌** | **rename `l2_quantile` (P5 8/10 → 명칭만)** |
| 14 | neurocard_lite | Yang 2020 NeuroCard | PCA(8)+KMeans | **rename `pca8_kmeans` + P6 → P1 이동** |
| 15 | factor_join | Zhao 2023 FactorJoin | PCA(2)+5×5 grid | **rename `pca2d_grid` + P6 → P4 이동** |

### 1.2 algorithm bug / leak (5건)

| # | method | 결함 | 결정 |
|---|---|---|---|
| 16 | banditucb1 | UCB1 미구현 (KMeans wrapper) | **폐기** OR rename `kmeans_subset_100k` |
| 17 | kde_pilot | KM20 leak (`stratum_id` column SELECT) | **RQ3 paradigm 비교에서 제외 유지** (V7 audit 결정) |
| 18 | pq | md5 hash → reservoir 등가 (PQ codeword 효과 0%) | **md5 제거 → codeword id 직접 사용** |
| 19 | opq | md5 hash 동일 결함 | **md5 제거 + niter 명시** |
| 20 | cocluster_nystrom | Nyström 미구현, n_row=4 → 16 cluster (n_strata=20 미달) | **rename `biclustering_5k_centroid`** |

### 1.3 redundancy / alias (10건)

| # | method | 결함 | 결정 |
|---|---|---|---|
| 21 | kdpp | epsilon_net 와 line-by-line 동일 | **폐기 OR 진짜 DPP 재구현** |
| 22 | kdtree | `idx % n_strata` = random hash (locality 0) | **raw `kdtree_partition.py` 사용** |
| 23 | hkbu_repsample | coreset 와 본질 중복 + max_iter=5 | **폐기 OR max_iter ↑** |
| 24 | coreset | max_iter=10 어중간 | **결정 (max_iter=0 또는 100+)** |
| 25 | adaptive_bucket_probing | PCA1D 와 8-line identical | **폐기 OR 진짜 variance-aware bin 재구현** |
| 26 | dense_rp | random_projection normalization 차이만 | **폐기 OR ablation narrative 명시** |
| 27 | sobol | argmax 매핑 — QMC 정통 X | **disclaimer 추가** |
| 28 | halton | sobol 동일 + Halton degeneracy | **disclaimer 추가** |
| 29 | hammersley | first-dim asymmetry | **disclaimer 추가** |
| 30 | lhs | normalization 부재 | **disclaimer 추가** |

---

## 2. measurement matrix 영향

### 2.1 method count 변화

| 단계 | method 수 | 변화 |
|---|---|---|
| 현재 (handoff_v0) | 36 (+ kde_pilot/lp_bound/banditucb1 합 41) | — |
| critical 정정 후 폐기 | -10 (thompson/mfmc/neuram/cca1d/ams/ccsketch/kdpp/cocluster_nystrom/banditucb1/(coreset OR hkbu)) | 31 |
| critical 정정 후 rename only | (-6) hilbert+reservoir+lpm2+tucker+vinecopula+lp_bound+neurocard+factor_join | 23 distinct |
| Tier 1 추가 후 | +6 (DBSCAN/KDE/MHIST-2/HyperLogLog/randomized SVD/wavelet histogram) | 29 |
| **최종 권고** | **29 method × 9 paradigm** | (5→9 paradigm 확장: P7 Subspace, P8 Graph, P9 InfoTheoretic, P10 Density) |

### 2.2 handoff_v2 §2 matrix 영향
- 현재 51 sampling cell × 34 method = 1,734 measurement
- 정정 후 51 cell × 29 method = 1,479 measurement (~15% 감소)
- P4 redundancy 408 → ~250 redundant 제거 후 quality 향상

### 2.3 paradigm framework 정정 (5 → 9)

| paradigm | 현재 method | 정정 후 method | 비고 |
|---|---|---|---|
| P1 Cluster | 8 | 7 + DBSCAN | banditucb1 폐기 |
| P2 Spatial | 5 | 3-4 | kdpp/kdtree 정정 후 |
| P3 Streaming | 7 | 1 (mb_partial) + RANDOM20 control | 4건 폐기 + kde_pilot 제외 |
| P4 DimReduction | 8 | 3 + randomized SVD | 4 PCA-alias 폐기 + neuram/cca1d/tucker/vinecopula |
| P5 QMC/Hashing | 8 | 5 (lsh, sobol, halton, hammersley, lhs, lp_bound→l2_quantile) | ams/ccsketch 폐기 |
| **P6 Quantization** | 5 | 2-3 (pq, opq, MHIST-2, wavelet histogram) | 3건 다른 paradigm 이동 |
| **P7 Subspace** (신규) | — | CLIQUE | future work 또는 5/27 추가 |
| **P8 Graph-based** (신규) | — | Leiden | future work |
| **P9 Information-theoretic** (신규) | — | HyperLogLog | Tier 1 추가 |
| **P10 Density estimation** (신규) | — | KDE Parzen | Tier 1 추가, narrative anchor |

---

## 3. SF feasibility 적용

### 3.1 615 cell 분류

| 카테고리 | cell | 비율 | 처리 |
|---|---|---|---|
| infeasible | 34 | 5.5% | **drop** (vinecopula × SF=100 등) |
| subset_training | 66 | 10.7% | `run_subset_training.py` 8 method × SF=10·100 |
| 분포 mismatch | 149 | 24.2% | **negative control 1 cell만 보존, 나머지 narrative 약화 명시** |
| strong fit | 218 | 35.4% | full 측정 |
| neutral fit | 214 | 34.8% | full 측정 |

### 3.2 handoff_v0 FINAL SCOPE 와의 align
- **97.2% coverage 가능** (1,044 measurement 중 vinecopula × 3 SF=100 cell만 drop)
- 35/36 method × 3 SF=100 = 105 measurement 진행 가능

### 3.3 5 distribution category fit (re-tabulated)

| Category | DEEP (mod-skew) | SIFT (high-skew) | SSN (balanced) | YFCC (very-skew) | WIKI (low-intrinsic) |
|---|---|---|---|---|---|
| A: PCA-based | ✓✓ | ✓✓✓ | ✗ | ✓✓✓ | ✓ |
| B: density | ✓✓ | ✓✓✓ | ✗ | ✓✓✓ | ✓ |
| C: QMC uniform | ✗ | ✗✗ | ✓✓✓ | ✗✗✗ | ✗ |
| D: agnostic | ◎ | ◎ | ◎ | ◎ | ◎ |
| E: VQ/centroid | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓✓ |

---

## 4. handoff_v2 5 critical decisions 와의 정합성

본 v3 (method audit) 와 v2 (paper exact setup) 는 **직교**.

| handoff_v2 decision | 본 v3 영향 |
|---|---|
| 1 Fig 5 queries (DEEP/SIFT/SSN 별) | 영향 X (method 자체 audit) |
| 2 min/max bound 제거 | 영향 X |
| 3 Selectivity {0.1%, 1%, 10%} | 영향 X |
| 4 A3 ECQO mode 분리 | 영향 X |
| 5 Q-error + wall-clock | 영향 X |

**결론**: handoff_v2 5 decisions confirm 받기 전이라도 method registry 정정 (1.1~1.3) 진행 가능.

---

## 5. 우선 조치 sequence

### P0 — 즉시 (사용자 확인 후 30분-1시간)
1. **★3 hilbert**: registry line 446-458 raw `hilbert_curve.py` 사용 OR `pca2d_lex` rename
2. **★4 sparse_rp**: 보고서/paper/PPT 의 "Achlioptas 2003" → "Li-Hastie-Church 2006" reference 정정
3. **lp_bound**: SIGMOD 2025 LpBound 명칭 충돌 → `l2_quantile` rename
4. **neurocard_lite + factor_join**: rename + paradigm 이동

### P1 — 이번 주 (2-3시간)
5. P3 reservoir/thompson/mfmc/lpm2: rename 또는 폐기
6. P4 neuram/cca1d/tucker/vinecopula: 4건 폐기 (PCA1D alias)
7. P5 ams_count_sketch/ccsketch: 폐기
8. P6 paradigm 폐지 또는 P9/P10 신규 도입
9. pq/opq: md5 hash 제거

### P2 — 이번 주말 (4-5시간)
10. Tier 1 6 method 추가 launch (DBSCAN, KDE, MHIST-2, HyperLogLog, randomized SVD, wavelet histogram)
11. kdpp ≡ epsilon_net 차별화 또는 폐기
12. kdtree raw 사용

### P3 — 5/27 발표 전
13. **PDX SIGMOD 2025 인용 추가** (RQ1 narrative align: intrinsic_dim + skewness 본 thesis 일치)
14. 5 → 9 paradigm 체계 narrative 정정
15. handoff_v0 36 method → 23 method × cleaned naming 으로 재정렬 + 보고서 v8 limitation table

---

## 6. 사용자 결정 필요 (메인 세션 진입 전 confirm)

### Q1: ★3 hilbert 정정 방향
- (A) raw `hilbert_curve.py` 사용 → ★3 결과 재측정 필요 (서버 시간 ~3-5h)
- (B) `pca2d_lex` rename + 결과 그대로 → 학술 정확성 회복 (재측정 X)
- (C) **현재 hilbert를 `pca2d_lex` rename + 진짜 hilbert 별도 추가** → "Hilbert curve 의 진짜 locality 효과 vs PCA proxy 효과 분리 검증" 자체가 흥미로운 finding (재측정 ~3-5h)

권고: **(C) — 학술 contribution 향상 + reviewer attack 방어**.

### Q2: 폐기 method 수 확정 (10건 OR 줄여서?)
권고 폐기 list (10건):
- thompson_sampling, mfmc, neuram, cca1d, ams_count_sketch, ccsketch, kdpp, cocluster_nystrom, banditucb1, hkbu_repsample (또는 coreset)

권고: **10건 모두 폐기** (PCA1D alias / 코드 중복 / 미구현 명백한 케이스).

### Q3: P6 paradigm 폐지 vs P9/P10 신규?
- (A) P6 폐지 → 5 paradigm × method 재정렬
- (B) P9 InfoTheoretic + P10 Density 신규 → **9 paradigm 확장** (PDX 2025 narrative align)

권고: **(B) — 학술 narrative 강화**. P10 (KDE Parzen) 가 본 연구 "분포 인지 stratification" 의 textbook anchor.

### Q4: Tier 1 6 method 5/27 발표 전 추가?
- 구현 시간: ~5-8h (서버 측정 포함)
- 학술 contribution: 매우 높음 (PDX SIGMOD 2025 align + 9 paradigm coverage)

권고: **Tier 1 추가 진행** (DBSCAN/KDE/MHIST-2/HyperLogLog/randomized SVD/wavelet histogram).

### Q5: handoff_v2 5 critical decisions confirm
별도 사항 (paper exact setup). v3 정정과 무관하게 별도 confirm 필요.

---

## 7. 산출물 위치

```
_internal/
├── handoff_v3_method_verification_20260510_2030.md   ← 이 파일
├── handoff_v2_paper_verbatim_decisions_20260510_1418.md (선행, paper exact setup 5 decisions)
├── handoff_v0_FINAL_SCOPE_20260510_0125.md (선행, 36 method × 26 cell scope)
└── method_verification_20260510/                      ← 본 audit 보고서들
    ├── _SUMMARY.md (종합 요약)
    ├── paradigm_P1_cluster.md ~ P6_quantization_other.md (6 paradigm 보고서)
    ├── sf_feasibility_matrix.md
    └── additional_methods_brainstorm.md
                                                       (총 5,777 lines / 354 KB)
```

---

## 8. 메인 세션 진입 시 권장 명령어

```bash
# 1. 본 handoff_v3 + _SUMMARY 함께 read
@_internal/handoff_v3_method_verification_20260510_2030.md
@_internal/method_verification_20260510/_SUMMARY.md

# 2. 핵심 paradigm audit 1-2건 spot-check (★3 hilbert / ★4 sparse_rp 위주)
@_internal/method_verification_20260510/paradigm_P2_spatial.md   (★3 hilbert critical)
@_internal/method_verification_20260510/paradigm_P4_dimreduction.md (★4 sparse_rp Li 2006)

# 3. 사용자 Q1~Q5 confirm 받기
# 4. registry 정정 (measure_paper_exact.py:407-852) 진행
# 5. SSH 복구 후 측정 진입
```

---

## END

작성: 2026-05-10 20:48 KST (mac-mini 검증 세션)
8 agent 병렬 발사 → 5,777 lines audit 보고서 → 이 handoff 압축
**비가역 0** (코드 변경 X, 보고서 작성만)
**다음 step**: 사용자 Q1~Q5 confirm + 메인 세션 진입 + registry 정정 + SSH 복구 후 측정
