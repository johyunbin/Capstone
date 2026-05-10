# 캡스톤 RQ3 narrative + 36 method portfolio (5/10 00:30 KST 기준)

---

## 정정된 narrative

| | Exqutor 영역 | 한계 | 우리 공략 |
|---|---|---|---|
| **Vector index 있음** | §V-A ECQO (multi-join 잘 동작) | (해당 없음 — Exqutor 가 잘 풀음) | — |
| **Vector index 없음 + single-table** | §V-B Adaptive Sampling | unstratified Bernoulli, 분포 정보 X | distribution-aware stratification augment |
| **Vector index 없음 + multi-table** | (Exqutor 직접 안 다룸 — §V-B 가 KNN 한정이므로) | naive transfer 시 결합 분포 정보 못 활용 | stratification 을 multi 결합 분포까지 확장 |

## 우리의 정확한 공략점

**Exqutor 의 §V-B Adaptive Sampling 은**:
1. **specifically for KNN queries** 명시 → single-table 한정 (paper §V-B verbatim)
2. **unstratified Bernoulli random sampling** → 분포 정보 0
3. multi-table 결합 분포 (partsupp ⋈ wiki) 의 stratification 은 본 논문 scope 밖

**우리의 contribution**:
- §V-B 에 distribution-aware stratification 을 augment
- single-table 에서 효과 입증 (RQ1+RQ2: −8% Δ%, HDBSCAN 10/10 sig)
- multi-table 까지 확장 — naive 0/66 발견 후 36 method portfolio 로 정복 시도
- Exqutor 보완 (대체 X) — §V-A ECQO 는 그대로, §V-B 에 layer 추가

## 결론

1. **Exqutor 는 multi-join 풀려고 만든 시스템** (이걸 무시하면 안 됨)
2. **§V-A ECQO (with HNSW)** 는 multi-join 까지 잘 풀음
3. **§V-B Adaptive Sampling** 만이 진짜 weakness 영역:
   - single-table KNN 한정 (paper 에 explicit)
   - unstratified Bernoulli (분포 정보 X)
4. **우리의 contribution**:
   - §V-B 에 distribution-aware stratification augment
   - single 에서 효과 입증 → multi 로 확장 (현재 진행 중인 RQ3)
   - **multi-table 영역은 Exqutor 가 ECQO 로 잘 풀고 있지만, vector index 없는 시나리오의 multi-table 은 §V-B 한계로 인해 아직 미해결 영역 — 우리가 거기 augment**

---

## Method portfolio (36 methods, 4 Tier)

> 모든 method 는 "vector index 없음 + 분포 unknown" 시나리오 100% 부합.
> HNSW-SS 는 narrative 위반 (vector index 사용) 으로 drop. LPM2 (Grafström 2012) 추가.

### 5 Paradigm Baseline (11 methods, 기존)

| # | Paradigm | Method | 학술 출처 (year/venue) |
|---|---|---|---|
| 1 | P1 Cluster | HDBSCAN | Campello et al. PAKDD 2013 |
| 2 | P1 Cluster | MiniBatch K-means | Sculley WWW 2010 |
| 3 | P1 Cluster | GMM | Reynolds 1995 |
| 4 | P2 Spatial | Hilbert curve | Lawder-King SIGMOD 2001 |
| 5 | P2 Spatial | faiss_ivf | Jégou et al. PAMI 2011 |
| 6 | P3 Streaming | MB_partial | Sculley + sklearn API |
| 7 | P3 Streaming | Reservoir | Vitter TOMS 1985 |
| 8 | P4 DimReduction | sparse_rp | Achlioptas JCSS 2003 |
| 9 | P4 DimReduction | PCA1D | Pearson 1901 |
| 10 | P5 Quasi-random | LSH | Indyk-Motwani STOC 1998 |
| 11 | P5 Quasi-random | Sobol | Sobol 1967 |

### Tier S+ — Direct Estimator (7 methods, multi-table cardinality SOTA)

> §V-B 가 multi-table joint distribution 으로 확장 X → 직접 비교 baseline

| # | Method | 학술 출처 | 역할 |
|---|---|---|---|
| 12 | **WanderJoin** | Li et al. SIGMOD 2016 / TODS 2019 | index-aware random walk on join |
| 13 | **AMSCountSketch** | Alon et al. STOC 1999 | F2 frequency moment sketch |
| 14 | **NeuroCard** | Yang VLDB 2020 | autoregressive density (multi-table SOTA) |
| 15 | **AdaptiveBucketProbing** | Chen et al. arXiv 2604.04603 (2026) | vector-native LSH + Chernoff |
| 16 | **CCSketch** | Heddes et al. SIGMOD 2024 | multi-join FFT convolution sketch |
| 17 | **FactorJoin** | Wu et al. SIGMOD 2023 | factor-graph histogram BP |
| 18 | **LpBound** | Zhang/Suciu SIGMOD 2025 (Best Paper) | LP-based pessimistic upper bound |

### Tier A — Stratification Primitives (10 methods, distribution-aware)

> §V-B 의 unstratified Bernoulli 를 distribution-aware 로 augment

| # | Method | 학술 출처 | inductive bias |
|---|---|---|---|
| 19 | **PQ** | Jégou et al. PAMI 2011 | sub-vector quantization |
| 20 | **Coreset** | Bachem et al. ICML 2017 | sensitivity sampling |
| 21 | **DenseRP** | Bingham-Mannila ICDM 2001 | Gaussian RP |
| 22 | **BanditUCB1** | Carpentier-Munos NeurIPS 2011 | UCB1 stratum allocation |
| 23 | **NeurAM** | Geraci et al. arXiv 2026 | autoencoder dim-invariant |
| 24 | **ThompsonSampling** | Russo 2018 / Bao SIGMOD 2021 | Bayesian bandit |
| 25 | **MFMC** | Peherstorfer SIAM JSC 2016 | multi-fidelity control variates |
| 26 | **EpsilonNetBaseline** | Haussler-Welzl SoCG 1986 | VC-dim theoretical floor |
| 27 | **kDPP** | Kulesza-Taskar ICML 2011 | repulsive/diverse sampling |
| 28 | **OPQ** | Ge et al. CVPR 2013 / PAMI 2014 | optimized PQ with rotation |

### Tier B — Joint Distribution + Sample Design (7 methods)

| # | Method | 학술 출처 | inductive bias |
|---|---|---|---|
| 29 | **CCA1D** | Hotelling Biometrika 1936 | canonical correlation 1D |
| 30 | **CoCluster_Nystrom** | Dhillon KDD 2003 | bipartite spectral co-clustering |
| 31 | **Tucker** | Tucker 1966 / Kolda 2009 | tensor decomposition (joint) |
| 32 | **VineCopula** | Bedford-Cooke 2002 | bivariate copula tree (PCA reduce → vine) |
| 33 | **HKBU_RepSample** | Wu et al. SIGMOD 2026 (HKBU) | facility-location + local fidelity |
| 34 | **LHS** | McKay Technometrics 1979 | Latin Hypercube |
| 35 | **LPM2** | Grafström et al. Biometrics 2012 | probabilistic spatially-balanced design |

### Tier C — Single-only AS Variant (1 method)

| # | Method | 학술 출처 | 역할 |
|---|---|---|---|
| 36 | **ConditionalAdaptive** | Exqutor §V-B variant | selectivity-conditioned β (Phase F B7) |

---

## 측정 매트릭스 (5/10 01:14 update — YFCC_PCA drop 후)

| | sf=1 | sf=10 | total |
|---|---|---|---|
| **Single cells** (5 dataset × 2 sf) | 5 | 5 | 10 |
| **Partsupp 4-way** | 4 | 4 | 8 |
| **Multi-join (`*_wiki_1`)** | 5 | 5 | 10 |
| **Partsupp + wiki_1** | 5 | 5 | 10 |
| **Total cells** | **19** | **19** | **38** |

**측정 조합**: 36 methods × 38 cells = **1,368 measurements** (sf=1 + sf=10)
- Multi cells (28): 35 methods (skip ConditionalAdaptive single-only)
- Single cells (10): 36 methods

**+ SF=100 추가 3 cells × 36 methods = 108 measurements** (Exqutor 100% 매치):
- `partsupp_deep_wiki_100`, `partsupp_sift_wiki_100`, `partsupp_fb_wiki_100`* (* = SSN, 코드 alias)
- raw YFCC 192d × partsupp SF=100 은 메모리 폭발 위험 + 본 논문 미수록 → 제외

→ **grand total: 41 cells × 36 methods = 1,476 measurements** (이전 56 cells / 2,016 → ~27% slim)

---

---

## 데이터셋 정리 (5/10 01:14)

사용자 (조현빈) 의 의문 제기 ("Exqutor paper 가 진짜로 YFCC 를 PCA 처리해서 썼는가?") → Exqutor §VI 직접 재확인 → **YFCC_PCA 본 논문 미사용 데이터셋** 확인. 동시에 build_FB_single_ensemble.py source 에서 **"FB" = SimSearchNet++ (SSN) 의 단순 rename** 확인 → 5/10 결정으로 모든 문서·발표·논문 표기는 **SSN (SimSearchNet++)** 단일화 (코드 path 의 `fb_*` alias 는 5/10 morning batch rename 예정).

### 정리된 7 데이터셋 (Exqutor 매치 5 + 2 join partner)

| # | NPY name (코드 alias) | dim | Exqutor 본 논문 표기 | 우리 표기 (문서) | 비고 |
|---|---|---|---|---|---|
| 1 | `deep1B` | 96 | DEEP1B | DEEP | 일치 |
| 2 | `sift1B` | 128 | SIFT1B | SIFT | 일치 |
| 3 | `FB` (server alias) | 256 | **SimSearchNet++** | **SSN (SimSearchNet++)** | **NPY 파일명만 alias — 모든 문서·발표·논문은 SSN 통일 표기 (5/10 결정)** |
| 4 | `wiki` | 768 | Wikipedia | WIKI | 일치 (join partner 主) |
| 5 | `yfcc` | 192 | YFCC100M raw | YFCC | 일치 |
| 6 | `partsupp` | (TPC-H) | (간접) | partsupp | join partner |
| 7 | `wiki_1` | 768 | (5번 재사용) | (간접) | join partner |

### 폐기 작업

- **3 procs killed** (PIDs 3241790, 3311667, 3644487 — 모두 YFCC_PCA cells)
- **48 NPY/parquet → `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/`** 격리 (delete X)
- **CELL config 14 entry 주석화** in `_internal/scripts/measure_multi_paradigm.py`
- 상세: `_internal/state/_data_scope_decision_20260510_0114.md`

### Naming convention (5/10 update — SSN 단일화)

- **모든 문서/figure/표**: **SSN (SimSearchNet++)** 단일 표기로 통일. 단독 "FB" 표기 금지.
- **codebase 내부 (서버)**: `fb_*`, `FB`, `build_FB_*` 등은 코드 alias — 5/10 morning batch rename 예정 (서버 측정 진행 중이라 즉시 rename 불가). 코드 reference 인용 시 alias 임을 명시.

> 코드 호환성을 위해 server 측 NPY/CSV 파일명은 `partsupp_fb_*` 유지 (5/10 morning batch rename 예정). 모든 문서/figure/표는 **SSN (SimSearchNet++)** 로 통일.

---

## Phase F — Direct §V-B 비교 (B1-B6, narrative ⑥)

| Code | Name | Description |
|---|---|---|
| **B1** | vanilla §V-B | Exqutor 본 논문 그대로 (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, N=385) |
| **B2** | B1 + stratify | §V-B + 분포 인지 stratified |
| **B3** | B1 + ensemble | §V-B + (1) ensemble |
| **B4** | B2 + ensemble | §V-B + stratified + (1) ensemble (★ thesis 핵심) |
| **B5** | B1 + stratify + importance | §V-B + stratified + importance sampling |
| **B6** | B5 + ensemble | §V-B + stratified + importance + (1) ensemble |

→ 각 baseline 별 q_error / sample size / dropped fraction / time 4축 비교

---

## 7-stage storyline

| Stage | 입증 내용 | 측정 status |
|---|---|---|
| ① RQ1+RQ2 single 효과 입증 | random vs Neyman stratified 정량 비교 | ✅ 완료 (W1 sprint) |
| ② RQ3 single paradigm 우위 | 5 paradigm × 11 method 단일 비교 | ✅ 완료 |
| ③ Multi naive 적용 | 11 method × 6 cell paired-better 0/66 | ✅ 완료 |
| ④ Failure mode 학술 진단 | curse of dim (Geraci 2026), Cochran §5.5, Bengtsson 2008 ESS | 🔄 진행 中 |
| ⑤ 신규 25 method 발굴 (S+/A/B/C) | 36 method portfolio 측정 | 🔄 진행 中 |
| ⑥ §V-B vs §V-B+stratification augment | Phase F B1-B6 직접 비교 | ⏳ launch 대기 |
| ⑦ Production-ready package | 박광현 BDAI 후속 reproducible code | ⏳ 5/10 아침 |

---

## 정리

- **36 methods × 38 cells = 1,368 measurements** (sf=1 + sf=10), + SF=100 3 cells × 36 = 108 → **grand 1,476** (5/10 01:14 update — YFCC_PCA drop 후, 이전 56 cells / 2,016 → ~27% slim)
- **두 트랙**: Pre-AS stratifier (28) vs Direct estimator (8), 둘 다 §V-B 와 비교
- **데이터셋**: Exqutor 본 논문 매치 5 (DEEP, SIFT, **SSN (SimSearchNet++)**, wiki, yfcc raw) + 2 join partner (partsupp, wiki_1)
- **YFCC_PCA drop**: 우리 팀 5/7 임의 추가, Exqutor 미사용 → 5/10 01:14 폐기 (3 procs kill, 48 file 격리, CELL config 14 entry comment-out)
- **SSN unified naming**: 모든 문서·발표·논문은 **SSN (SimSearchNet++)** 단일 표기 (5/10 결정). 서버 `fb_*` 파일명은 코드 alias, 5/10 morning batch rename 예정.
- **5/10 아침 finalize 목표**: 모든 측정 + Phase F + Phase G analysis 완료
- 사용자 monitoring 진행 中 (서버 자원 극한 활용)

상세 결정 기록: `_internal/state/_data_scope_decision_20260510_0114.md`

문의: 조현빈 (wh8502@yonsei.ac.kr)
