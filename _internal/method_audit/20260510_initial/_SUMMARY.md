# 41 method × 6 paradigm × 615 cell 종합 검증 — _SUMMARY.md

작성: 2026-05-10 20:45 KST (mac-mini 검증 세션, 8 agent 병렬)
출처: `_internal/method_verification_20260510/` 8개 보고서 (총 5,777 lines)

---

## 0. TL;DR

**41 method 중 신뢰 가능 6개, naming/algorithm critical defect 30+ 건.**

| 신뢰 method (★ 후보 + 견조) | 충실도 | paradigm |
|---|---|---|
| pca1d | 10/10 | P4 textbook Pearson 1901 |
| **mb_partial ★2 4강** | **8/10** | P3 Sculley 2010 |
| minibatch | 8/10 | P1 Sculley 2010 |
| lp_bound | 8/10 (P5 audit) → ⚠ | **P5 audit ↔ brainstorm 충돌** — naming SIGMOD 2025 Best Paper "LpBound" 와 충돌 (즉시 rename) |
| **hdbscan ★1 4강** | **7/10** | P1 Campello 2013 (minor tuning 필요) |
| **sparse_rp ★4 4강** | **6/10** | P4 — **Achlioptas 2003 ❌ → Li 2006 ⭕ reference 정정 필수** |
| faiss_ivf | 6/10 | P2 (seed 미고정 minor) |

**4강 학술 정합성 직격 — ★3 hilbert critical fraud risk**:
- ★1 hdbscan 7/10 → minor tuning OK
- ★2 mb_partial 8/10 → 신뢰
- **★3 hilbert 2/10 → PCA 2D lex sort, 진짜 Hilbert curve ❌ → 학술 fraud risk** (별도 raw `experiments/code/rq3/hilbert/hilbert_curve.py` 가 진짜 Wikipedia 표준 구현 존재하나 registry 미사용)
- **★4 sparse_rp 6/10 → Li 2006 1/√D variant 확정** (V9 audit 와 독립 검증 일치)

---

## 1. paradigm 별 평균 충실도 (낮은 순)

| paradigm | 평균 | critical | moderate | OK | total |
|---|---|---|---|---|---|
| **P6 Quantization/Other** | **1.6/10** | 4 | 1 | 0 | 5 — paradigm **폐지 권고** |
| P3 Streaming | 3.4/10 | 5 (kde_pilot leak 포함) | 1 | 1 (mb_partial) | 7 |
| P2 Spatial | 3.6/10 | 4 (★3 hilbert + kdpp≡epsilon_net + kdtree + faiss_ivf seed) | 0 | 1 | 5 |
| P5 QMC/Hashing | 4.4/10 | 2 (ams≡lsh, ccsketch) | 5 | 1 (lp_bound, naming 정정 시) | 8 |
| P4 DimReduction | 4.5/10 | 4 (PCA-alias) | 1 | 3 | 8 |
| P1 Cluster | 5.1/10 | 3 | 4 | 1 | 8 |
| **종합** | **3.8/10** | **22** | **12** | **7** | **41** |

---

## 2. CRITICAL 30건 — 즉시 조치 (paper reviewer 100% reject 위험)

### 2.1 학술 reference fraud / misrepresentation (15건)

| # | method | paradigm | 표명 reference | 실제 알고리즘 | 권고 조치 |
|---|---|---|---|---|---|
| 1 | **★3 hilbert** | P2 | Faloutsos 1989 Hilbert curve | PCA 2D lex sort (`pca[:,0]*1000+pca[:,1]`) | raw `hilbert_curve.py` 사용 OR rename `pca2d_lex` |
| 2 | **★4 sparse_rp** | P4 | Achlioptas 2003 | Li 2006 1/√D variant | reference 정정 (Li-Hastie-Church 2006) |
| 3 | reservoir | P3 | Vitter 1985 | RANDOM20 random partition | rename `random20` |
| 4 | thompson_sampling | P3 | Thompson 1933 | MiniBatchKMeans (Beta posterior 부재) | 폐기 또는 재구현 |
| 5 | mfmc | P3 | Peherstorfer 2018 | KMeans+RANDOM20 50:50 mask (control variate 부재) | 폐기 |
| 6 | lpm2 | P3 | Grafström 2012 LPM | Weiszfeld median + radial bin (pivoting 부재) | rename `radial_quantile` |
| 7 | neuram | P4 | autoencoder | PCA1D 와 100% 동일 | 폐기 |
| 8 | cca1d | P4 | Hotelling 1936 CCA | PCA(whiten=True), Y 부재 → PCA1D bit-equal | 폐기 |
| 9 | tucker | P4 | Tucker 1966 tensor | PCA(3) + 3D grid + modulo | rename `pca3d_grid` |
| 10 | vinecopula | P4 | Bedford-Cooke 2002 | rank+PCA1D (vine graph 부재) | rename `spearman_pca1d` |
| 11 | ams_count_sketch | P5 | Alon-Matias-Szegedy 1996 | line-by-line lsh 와 동일 (rng 변수명만 차이) | 폐기 |
| 12 | ccsketch | P5 | Cormode-Muthukrishnan 2005 | float mod + np.min — 강한 left-skew 분포 | 폐기 |
| 13 | **lp_bound** | P5 | (textbook L2 norm) | naming 충돌 — **SIGMOD 2025 Best Paper "LpBound" (Zhang/Suciu) 와 알고리즘 무관** | rename `l2_quantile` |
| 14 | neurocard_lite | P6 | Yang 2020 NeuroCard | PCA(8)+KMeans (transformer 부재) | rename `pca8_kmeans` (P1 이동) |
| 15 | factor_join | P6 | Zhao 2023 FactorJoin | PCA(2)+5×5 grid (PGM 부재) | rename `pca2d_grid` (P4 이동) |

### 2.2 algorithm bug / leak (5건)

| # | method | paradigm | 결함 |
|---|---|---|---|
| 16 | banditucb1 | P1 | UCB1 algorithm 전혀 미구현 (코드 주석에서 본인 인정 "UCB는 query-time"). 단순 KMeans wrapper |
| 17 | kde_pilot | P3 | **KM20 leak** — `experiments/code/rq3/kde/kde_pilot.py:90-105` 가 PG `stratum_id` column SELECT (KMeans20 결과). 자기 stratification 부재 (V7 audit 일치) |
| 18 | pq | P6 | `IndexPQ.sa_encode → md5 hash → mod 20` — codeword distance preservation 무효, 사실상 reservoir 수학적 등가 |
| 19 | opq | P6 | pq 동일 (md5 destroys OPQ 효과) |
| 20 | cocluster_nystrom | P6 | Williams 2001 Nyström approximation 미구현 (단순 sample-and-extend), n_row=4 → 16 cluster (n_strata=20 미달) |

### 2.3 redundancy / alias (10건)

| # | method | paradigm | 중복 대상 |
|---|---|---|---|
| 21 | kdpp | P2 | kdpp 와 epsilon_net 코드 line-by-line 동일 (주석 1줄 차이) |
| 22 | kdtree | P2 | `idx % n_strata` = spatial locality 0 (random hash 등가) |
| 23 | hkbu_repsample | P1 | coreset 와 본질 중복, max_iter=5 미수렴 |
| 24 | coreset | P1 | max_iter=10 어중간 (true coreset 도, 정상 KMeans 도 아님) |
| 25 | adaptive_bucket_probing | P3 | PCA1D 와 8-line identical (variance 주석만) |
| 26 | dense_rp | P4 | random_projection 와 normalization (column unit norm vs 1/√k) 차이만 |
| 27 | sobol | P5 | argmax 매핑 — QMC 정통 용도 X |
| 28 | halton | P5 | sobol 동일 + high-D Halton degeneracy |
| 29 | hammersley | P5 | first-dim asymmetry + sobol 변형 |
| 30 | lhs | P5 | normalization 부재 + sobol 변형 |

---

## 3. SF feasibility (615 cell = 41 method × 5 dataset × 3 SF)

| 카테고리 | cell 수 | 비율 | 대표 |
|---|---|---|---|
| infeasible | 34 | 5.5% | vinecopula × SF=100 (rank on 80M × 768d) |
| subset_training 필수 | 66 | 10.7% | hdbscan/birch/agglomerative/cocluster_nystrom/kdpp/epsilon_net/kdtree/hkbu_repsample × SF=10·100 |
| 분포 mismatch | 149 | 24.2% | sobol/halton/hammersley/lhs × SIFT/YFCC (skew 무시) |
| strong fit | 218 | 35.4% | PCA-based × skew, density × rich |
| neutral fit | 214 | 34.8% | sparse_rp/lsh × all |

**handoff_v0 FINAL SCOPE (36 method × 26 cell + 3 SF=100 = 1,044 measurement)**: **97.2% coverage 가능**.
- vinecopula × 3 SF=100 cell만 drop 권고 → 35/36 × 3 = 105 measurement 가능

**5 distribution category fit 매트릭스**:
| Category (method 수) | DEEP (mod skew) | SIFT (high skew) | SSN (balanced) | YFCC (very skew) | WIKI (low intrinsic) |
|---|---|---|---|---|---|
| A: PCA-based (7) | ✓✓ | ✓✓✓ | ✗ | ✓✓✓ | ✓ |
| B: density/cluster (9) | ✓✓ | ✓✓✓ | ✗ | ✓✓✓ | ✓ |
| C: QMC uniform (7) | ✗ | ✗✗ | ✓✓✓ | ✗✗✗ | ✗ |
| D: distribution-agnostic (7) | ◎ | ◎ | ◎ | ◎ | ◎ |
| E: VQ/centroid (11) | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓✓ |

---

## 4. 추가 method 권고 (41 → 47, Tier 1)

| # | method | reference | paradigm | 구현 난이도 | 본 narrative fit |
|---|---|---|---|---|---|
| 1 | DBSCAN | Ester KDD 1996 | P1 강화 (HDBSCAN 비교) | low (sklearn) | ★ |
| 2 | KDE Parzen | Parzen 1962 | **P10 새 paradigm anchor** | low (sklearn KernelDensity) | ★★★ (학술 origin) |
| 3 | MHIST-2 | Poosala VLDB 1997 | P6 진짜 alternative | mid (직접 구현) | ★★ (factor_join 대체) |
| 4 | HyperLogLog | Flajolet 2007 | **P9 새 paradigm** | low (datasketch lib) | ★★ (sketch textbook) |
| 5 | randomized SVD | Halko 2011 | P4 (PCA1D large-scale) | low (sklearn) | ★ |
| 6 | wavelet histogram | Matias 1998 | P6 강화 | mid | ★ |

**새 paradigm 4개 제안 (5 → 9)**:
- **P7 Subspace** (CLIQUE Agrawal 1998)
- **P8 Graph-based** (Leiden Traag 2019, future work)
- **P9 Information-theoretic** (HyperLogLog)
- **P10 Density estimation** (KDE Parzen) — narrative 학술 anchor 강화

**2024-2025 SIGMOD/VLDB literature 13편 발굴** — 핵심:
- **PDX SIGMOD 2025** (intrinsic_dim + skewness driven algorithm selection) — 본 RQ1 narrative 와 직접 align (memory 에 confirmation 명시)
- **LpBound SIGMOD 2025 Best Paper** — 본 연구 `lp_bound` 명칭 충돌 (#13 critical)
- **CCSketch SIGMOD 2024** (Heddes 2024)
- **PRICE VLDB 2024** (Zeng 2024)
- **Bao et al. VLDB 2025 vol 18 p.544** (Cardinality Estimation for Similarity Search)
- **GaussDB-Vector VLDB 2025**
- **Adaptive Bucket Probing arXiv 2604.04603** (Chen 2026 — 본 연구 method 명칭 일치하나 LSH multi-probe + Chernoff 누락)

---

## 5. 메인 세션 작업 영향

### 5.1 measure_paper_exact.py registry 영향
- 현재 41 method 중 **22 method critical defect** → measurement 진입 전 정정 권고:
  - rename: hilbert / sparse_rp reference / reservoir / lpm2 / tucker / vinecopula / lp_bound / neurocard_lite / factor_join / cca1d (10건)
  - 폐기: thompson_sampling / mfmc / neuram / ams_count_sketch / ccsketch / kdpp / cocluster_nystrom / banditucb1 (8건)
  - bug fix: kde_pilot KM20 leak / pq+opq md5 제거 / kdtree raw 사용 / hilbert raw 사용 (4건)

### 5.2 handoff_v2 §2 measurement matrix 영향
- 51 sampling cell × 34 method = 1,734 measurement 중 P4 redundancy 408×0.61 = ~250 redundant
- 정정 후: 51 cell × 26 method = 1,326 measurement (~24% 감소, 학술 정확성 향상)

### 5.3 5 critical decisions (handoff_v2 §1) 와의 정합성
- 5 decision 모두 paper exact 측정 setup 영역 (Fig 5 queries / clamping / selectivity / ECQO mode / metric) — 본 audit 와 직교
- 본 audit 는 **method 자체** 결함이라 5 decision confirm 받기 전이라도 method registry 정정 진행 가능

### 5.4 narrative 신뢰도 영향
- "5 paradigm × 11 method framework" → P3 7→2 / P5 8→6 / P6 5→0 (paradigm 자체 폐지) 후 재정렬 필요
- **★3 hilbert PCA proxy 발견 = 본 연구 핵심 contribution 의 학술 정합성 직격** — Option C (현재 hilbert를 `pca2d_lex` rename + 진짜 hilbert 별도 추가 → "Hilbert curve 의 진짜 locality 효과 vs PCA proxy 의 효과 분리 검증" 자체가 흥미로운 finding) 권고

### 5.5 reviewer attack 5 BLOCKING 방어
SF feasibility report (paragraph 11) 에 정리:
1. "왜 36 method?" → paradigm × distribution 격자 coverage
2. "왜 SF=100 일부 dataset?" → paper §VI Table I + memory pressure
3. "method 비교 fair?" → sample-cap 일관 검증
4. "분포 mismatch narrative 약화?" → framework falsifiability test 로 격상
5. "subset_training fair degradation?" → Bachem coreset 2017 학술 정당성

---

## 6. 우선 조치 list (메인 세션 진입 시)

### P0 (즉시, 30분-1시간)
1. ★3 hilbert: registry line 446-458 raw `hilbert_curve.py` 사용으로 교체 OR `pca2d_lex` rename
2. ★4 sparse_rp: 보고서 / paper / PPT 의 "Achlioptas 2003" → "Li-Hastie-Church 2006" reference 정정
3. lp_bound: SIGMOD 2025 Best Paper LpBound 와 명칭 충돌 → `l2_quantile` rename
4. neurocard_lite + factor_join: paper 이름 보고 100% reviewer 오해 → 명칭 변경 + paradigm 이동

### P1 (이번 주, 2-3시간)
5. P3 reservoir/thompson/mfmc/lpm2: rename 또는 폐기 결정
6. P4 neuram/cca1d/tucker/vinecopula: 4건 폐기 (PCA1D alias)
7. P5 ams_count_sketch/ccsketch: 폐기 결정
8. P6 paradigm 자체 폐지 → 4 paradigm 으로 축소 OR P9/P10 신규 paradigm 도입
9. kde_pilot: V7 audit 결정 유지 (RQ3 paradigm 비교에서 제외)
10. pq/opq: md5 hash 제거 (codeword id 직접 사용)

### P2 (이번 주말, 4-5시간)
11. Tier 1 6 method 추가 launch (DBSCAN, KDE, MHIST-2, HyperLogLog, randomized SVD, wavelet histogram)
12. kdpp ≡ epsilon_net 차별화 또는 폐기
13. kdtree raw `kdtree_partition.py` 사용 교체

### P3 (5/27 발표 전)
14. PDX SIGMOD 2025 인용 추가 (RQ1 narrative align)
15. 5 → 9 paradigm 체계 narrative 정정
16. handoff_v0 FINAL SCOPE 36 method → 26 method × cleaned naming 으로 재정렬

---

## 7. 산출 파일 위치

```
_internal/method_verification_20260510/
├── _SUMMARY.md                          (이 파일, 종합 요약)
├── paradigm_P1_cluster.md               (719 line, 8 method)
├── paradigm_P2_spatial.md               (692 line, 5 method)
├── paradigm_P3_streaming.md             (660 line, 7 method)
├── paradigm_P4_dimreduction.md          (902 line, 8 method)
├── paradigm_P5_qmc_hashing.md           (815 line, 8 method)
├── paradigm_P6_quantization_other.md    (820 line, 5 method)
├── sf_feasibility_matrix.md             (501 line, 615 cell)
└── additional_methods_brainstorm.md     (668 line, Tier 1 6 + 새 paradigm 4)
                                         5,777 lines / 354 KB
```

---

## END

작성: 2026-05-10 20:45 KST
검증 세션 (mac-mini 로컬, server 측정 영향 X)
다음 단계: handoff_v3_method_verification_20260510_2030.md 작성 (메인 세션 전달)
