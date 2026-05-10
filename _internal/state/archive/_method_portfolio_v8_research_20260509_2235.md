# Method Portfolio v8 — § 0.7 신규 method 발굴 결과

> 5/9 22:35 KST — 6 agent (5 research + 1 brainstorm) 병렬 dispatch 종합 결과.
> 22 method (v7) → **32 method (v8)** 확장 (+10 신규).
> v7 design 인계: `_internal/handoff_v18_session_20260509_2210_MaxPush.md` § 0.7.

---

## 1. v8 추가 10 methods (Tier S+/A)

### Tier S+ (cross-agent 합의 — 즉시 구현, 각 ≤2일)

| # | Method | Year | Venue | First-Author | Mechanism (≤2 sent) | 우리 setup fit (≤1 sent) | Impl 일수 | Multi-table | GPU |
|---|---|---|---|---|---|---|---|---|---|
| 23 | **ThompsonSampling** (Bao-style) | 2018/2021 | FnT-ML / SIGMOD | Russo / Marcus | Beta(α,β) per stratum, sampled posterior 기반 arm 선택. Bao SIGMOD 2021 Best Paper precedent. | BanditUCB1 (Carpentier 2011) 직접 upgrade — non-stationary workload 에 강함, hyperparam 추가 X | 0.5 | partial | No |
| 24 | **CCSketch** (Conv+Cross-Corr Count Sketch) | 2024 | SIGMOD (PACMMOD v2 i3) | Heddes (UCI) | per-tuple insertion 을 single-item count sketch 로, multi-join 추정 = FFT 역변환 inner product. O(rm log m). | AMSCountSketch 의 multi-join 일반화 — 멀티 join 무한 chain composition 가능 | 1 | **Yes (native)** | Optional FFT |
| 25 | **FactorJoin** | 2023 | SIGMOD | Wu | single-table histograms + factor-graph join 추론. de-normalization X, workload X. DeepDB 100× smaller / 40× faster. | partsupp ⋈ wiki two-table 토폴로지 정확히 매치, 50M-1B 행 trivial 학습 | 1 | **Yes** | CPU |
| 26 | **AdaptiveBucketProbing** (DynamicProber) | 2025-2026 | arXiv 2604.04603 | Chen (HKUST) | E2LSH 버킷 분할 + adaptive Hamming-distance 프로빙 + Chernoff bound early stop. unsupervised. | 96-1024d 벡터에서 검증된 유일 방법 — 우리 DEEP/SIFT/FB/YFCC/WIKI dim range 정확히 매치 | 1 | partial (per-table) | No |
| 27 | **LpBound** | 2025 | SIGMOD/PODS Best Paper | Zhang/Suciu (UW) | degree-sequence ℓ_p norms + Shannon inequalities → LP solve → guaranteed upper bound. data sample 무관. | pessimistic-bound paradigm 우리 portfolio 미존재 — query optimizer join 곱셈 폭발 envelope | 2 | **Yes (designed for)** | No |
| 28 | **HNSW-StratifiedSampling** (HNSW-SS) | 2026 (novel composition) | — | (composition) | hnswlib level-0 connected components 또는 entry-point Voronoi cells = strata. 그래프 degree 비례 sampling. | 기존 pgvector HNSW 재활용 — 별도 인덱스 X, ANN 인덱스 자체를 stratifier 로 | 2 | partial | CPU |

### Tier A (보조 — 시간 여유 있을 때, 각 2-3일)

| # | Method | Year | Venue | First-Author | Mechanism | 우리 setup fit | Impl 일수 | Multi-table | GPU |
|---|---|---|---|---|---|---|---|---|---|
| 29 | **MFMC** (Multi-fidelity MC) | 2016 | SIAM JSC | Peherstorfer | row-level 빠른 surrogate + block-level 느린 ground-truth control variates 최적 할당. | Bengtsson 2008 ESS 0.875 → 0.770 직접 회복 — multi-table 변량 감소 | 2-3 | yes | No |
| 30 | **Tucker** (decomposition via tensorly) | 1966/2009 | Psychometrika / SIAM Review | Tucker / Kolda | core G ×₁ U₁ ×₂ U₂ ... — HOSVD init + ALS refine. tensorly.decomposition.tucker. | multi-table joint distribution — PCA1D/CCA1D 가 놓치는 high-order interaction | 2 | yes (joint) | tensorly w/ torch |
| 31 | **VineCopula** (pyvinecopulib) | 2002 | various | Bedford & Cooke | d-dim joint = bivariate copula tree, 고차원 truncation. | Cochran §5.5 stratification efficiency 위배 = within-stratum dependence — vine 이 명시 모델링 | 3 | yes (multi-rel marginal) | No |
| 32 | **EpsilonNetBaseline** (Haussler-Welzl) | 1986 | SoCG | Haussler & Welzl | range query in R^d 에 O(d log d / ε²) uniform sample 이 ε-approximation 보장. | 이론 floor — 22 method 모두가 이 baseline 을 beat 해야 함, 안 beat 면 fundamental 한계 | 0.5 | yes | No |

---

## 2. Cross-agent 합의 highlights

| Method | Cited by | 합의 reasoning |
|---|---|---|
| CCSketch | Agent 1 #4 + Agent 3 #1 | SIGMOD 2024 multi-join native, GitHub code 즉시 사용 |
| AdaptiveBucketProbing | Agent 1 #1 + Agent 2 #7 | 96-1024d 벡터 검증된 유일 SOTA, 우리 emb dim 매치 |
| Tucker / TT / CoDe | Agent 4 + Agent 6 | tensor decomposition multi-relation joint distribution |
| Thompson Sampling | Agent 4 | Bao SIGMOD 2021 precedent, BanditUCB1 직접 upgrade |
| LpBound | Agent 1 #2 | SIGMOD 2025 Best Paper, guaranteed upper bound |
| MFMC | Agent 6 #2 | Bengtsson ESS 회복 직접 매치 |

---

## 3. Skip / not-fit (agent 합의)

| Method | Reason for skip |
|---|---|
| ADC / Diffusion-Cardest (Mu 2025) | GPU 학습 1주+, latency 문제 |
| DiskANN / Vamana | C++ binding, Python harness 부적합 |
| DP-FC (Xie SIGMOD 2025) | 프라이버시 우리 연구 X — DP noise 우리 정확도 story 약화 |
| MSCN (Kipf 2019) | workload-shift brittle, 일반화 약 (Wang VLDB 2021 검증) |
| ALECE (Li VLDB 2024) | 동적 workload 강점이지만 우리 static benchmark 에서는 미활용 |
| PRICE (Zeng VLDB 2024) | 30 dataset pretrained 에 vector emb 없음 — zero-shot transfer 미검증 |
| Naru (Yang VLDB 2019) | NeuroCard 가 explicit superset |
| FACE (Li VLDB 2022) | DeepDB+RSPN 의 tree factorization 과 redundant |
| GNCE (knowledge-graph) | 우리 도메인 X |
| CoLSE (single-table copula) | vine copula 가 superset |

---

## 4. v8 portfolio overview (32 methods)

```
P1 Cluster      : HDBSCAN, MiniBatch, GMM
P2 Spatial      : Hilbert, faiss_ivf
P3 Streaming    : MB_partial, Reservoir
P4 DimReduction : sparse_rp, PCA1D
P5 QuasiRandom  : LSH, Sobol
                  ─────────  (existing 11)
Tier S          : WanderJoin, AMSCountSketch, NeuroCard
Tier A          : PQ, Coreset, DenseRP, BanditUCB1, NeurAM
Tier B          : CCA1D, CoCluster_Nystrom
Tier C          : ConditionalAdaptive
                  ─────────  (v7 +11)
Tier S+ NEW     : ThompsonSampling, CCSketch, FactorJoin, 
                  AdaptiveBucketProbing, LpBound, HNSW-SS
Tier A NEW      : MFMC, Tucker, VineCopula, EpsilonNetBaseline
                  ─────────  (v8 +10)

TOTAL: 32 methods × 56 cells = 1,792 measurement combinations
```

---

## 5. 구현 priority order (5/10 새벽-오전 trigger)

### Wave 1 (5/9 23:00 ~ 5/10 03:00) — 가장 trivial
- ThompsonSampling (0.5 day) — sklearn-style upgrade
- EpsilonNetBaseline (0.5 day) — uniform sample with theoretical n
- AdaptiveBucketProbing (1 day) — github.com/OscarC9912/simQ_hd_card_estimator port

### Wave 2 (5/10 03:00 ~ 5/10 12:00) — moderate
- CCSketch (1 day) — github.com/mikeheddes/fast-multi-join-sketch port
- FactorJoin (1 day) — github.com/wuziniu/FactorJoin direct use
- HNSW-SS (2 days) — composition, hnswlib + stratified

### Wave 3 (5/10 오후 ~ 5/11 새벽) — heavy
- LpBound (2 days) — scipy.optimize.linprog
- Tucker (2 days) — tensorly
- MFMC (2-3 days) — control variates
- VineCopula (3 days) — pyvinecopulib

---

## 6. Server measurement plan v8

### 5/10 정오 시점 (예상)
- 28 cells covered × 32 methods = 896 measurements 진행 中

### 5/11 새벽-오전 시점 (target)
- 56 cells covered × 32 methods = 1,792 measurements 완료

### 5/11 오전 분석
- analyze_phase_g.py v8 (32 methods 통합)
- REPORT.md generate

### 5/11 오후 trigger
- SF=100 결정 사용자에게 보고

---

## 7. 사용자 directive 추적성 (handoff § 0.7)

| Step | 상태 |
|---|---|
| Step 1 — 5-6 agent 병렬 dispatch | ✅ 완료 (5/9 22:35) |
| Step 2 — brainstorming agent dispatch | ✅ 완료 (Agent 6) |
| Step 3 — 신규 candidates 5-10개 추가 | ✅ 10개 확정 (Tier S+ 6 + Tier A 4) |
| Step 4 — 측정 매트릭스 ~1,700 combinations | 🔄 56 cells × 32 methods = 1,792 (5/11 morning target) |
| Step 5 — Phase G analysis 신규 method 통합 | ⏳ 5/11 오전 |

---

## END

**Status**: agent 종합 완료. 10 new methods 확정. v7 → v8 portfolio expansion 직진 가능.
**Next**: Wave 1 implementation dispatch + 26 cells build 병렬 진행.
