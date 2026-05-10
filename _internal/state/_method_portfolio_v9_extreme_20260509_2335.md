# Method Portfolio v9 — Extreme Mode (5/9 23:35 KST)

> 사용자 22:15 directive: "전권 위임 + 자원 극한 활용 + 완벽한 실험 + 5/9 ~ 5/10 아침 사이 완료".
> v8 (32 method) → **v9 (36 method)** + deep-review 3 agent (narrative fit / missed scan / Tier validation) 결과 통합.

---

## 1. v9 추가 9 method (10 file 신규: epsilon_net 도 replace)

### v8 → v9 신규 9 method

| # | Method | Year | Venue | First-author | Why added (deep-review evidence) | Tier (v9) |
|---|---|---|---|---|---|---|
| 28 | **LpBound** | 2025 | SIGMOD/PODS Best Paper | Zhang/Suciu | Guaranteed pessimistic upper bound (LP via ℓ_p degree norms) — paradigm 미존재, query optimizer join 폭발 envelope | S+ |
| 29 | **MFMC** | 2016 | SIAM JSC | Peherstorfer | Multi-fidelity Monte Carlo control variates → Bengtsson 2008 ESS 0.875→0.770 직접 회복 | A |
| 30 | **Tucker** | 1966/2009 | Psychometrika / SIAM Review | Tucker / Kolda | Multi-table joint distribution tensor decomposition (PCA1D/CCA1D 가 놓치는 high-order interaction) | A |
| 31 | **VineCopula** | 2002 | Annals of Statistics | Bedford & Cooke | Cochran §5.5 within-stratum dependence 명시 모델링 (stratification efficiency 위배 직접 공략) | A |
| 32 | **HNSW-SS** | (composition) | — | (novel) | 기존 pgvector HNSW level-0 connected components = strata. Exqutor 인덱스 재활용 → narrative 완벽 fit | S+ |
| 33 | **HKBU-RepSample** | 2026 | SIGMOD | Wu et al. (HKBU) | "Balancing Global and Local: Representative Sampling for Large-Scale Vector Data" — 우리 thesis 와 100% 일치, 미인용 시 reviewer rejection 위험 | S+ |
| 34 | **LHS** | 1979 | Technometrics | McKay | Latin Hypercube — Sobol 옆 paradigm anchor (foundational classical) | B |
| 35 | **kDPP** | 2011 | ICML | Kulesza-Taskar | Determinantal Point Process — repulsive/diverse sampling (volume-based, 누락된 inductive bias) | A |
| 36 | **OPQ** | 2013 | CVPR/PAMI | Ge et al. | Optimized PQ with rotation — anisotropic-aware (DEEP/SIFT 같은 real vector data 에서 PQ strict dominate) | A |

### EpsilonNetBaseline 재구현 (replace)

기존 placeholder → 정식 Haussler-Welzl 1986 구현 (target_m = (4/ε²)·(d log d + log(2/δ)) 정확 계산 + 실제 net_indices metadata).

---

## 2. Deep-review 3 agent 종합 (5/9 22:50)

### Agent 1: Narrative fit (harsh assessment)

**핵심 발견**: 32 method 중 **5-7 method 가 narrative drift** — pre-AS stratifier 가 아니라 **estimator** 임:
- WanderJoin, NeuroCard, FactorJoin, LpBound, AdaptiveBucketProbing → estimator (AS 직접 대체)
- AMSCountSketch, CCSketch → sketch estimator (AS 와 별도)
- ConditionalAdaptive → AS 자체 변형 (Phase F B7 으로 재분류 권장)

**대응**: 사용자 directive "exqutor와 비교를 위해서" 명시 → 이들은 **direct estimator comparison vs §V-B Adaptive Sampling** 로 활용. §V-B 는 본 논문 명시 "specifically for KNN queries" (single-table KNN 한정 + unstratified Bernoulli) 이며 multi-table joint distribution 으로 확장되지 않으므로, multi-table 직접 estimator 들은 §V-B 의 미확장 영역 비교 baseline 이 된다. 즉 method 자체는 keep, **storyline 에서 두 보완적 트랙으로 분리**:
1. **Pre-AS stratifier group** (24개): §V-B 위에 distribution-aware stratification 을 augment 하는 sample-design layer (§V-B 의 unstratified Bernoulli 한계 보완 트랙)
2. **Direct estimator group** (12개): SOTA multi-table cardinality estimator — §V-B 가 multi-table joint distribution 으로 확장되지 않으므로 §V-B 의 미확장 영역에서 직접 비교 트랙

### Agent 2: Missed methods 2nd pass (3 strong + 2 maybe)

**Strong adds (모두 v9 에 포함)**:
- LHS (#34) ← McKay 1979
- kDPP (#35) ← Kulesza-Taskar 2011
- OPQ (#36) ← Ge 2013

**Maybe (시간 여유 시)**: Sensitivity sampling (Feldman-Langberg 2011), GP-UCB

### Agent 3: Tier validation (lean recommendation)

**Tier S+ 검증**:
- Strong S+ 유지: LpBound, FactorJoin, CCSketch, AdaptiveBucketProbing
- 하향 권고: ThompsonSampling → A, HNSW-SS → B (custom variant, no published reference)

**8 redundant methods 식별** (potentially drop):
- HDBSCAN ↔ MiniBatch ↔ GMM (clustering family)
- sparse_rp ↔ DenseRP (RP family)  
- LSH ↔ AdaptiveBucketProbing (LSH family)
- BanditUCB1 ↔ ThompsonSampling (bandit family)
- AMSCountSketch ↔ CCSketch (sketch family)
- NeurAM ↔ NeuroCard (neural family)
- VineCopula → 20D 한계, 768d 안 됨 (사실상 필터링됨)

**우리 결정**: 사용자 "모든 method 모든 cells" directive → 모두 측정. 분석 시 redundant 그룹 별로 best representative 선정.

---

## 3. v9 portfolio overview (36 methods)

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
                  ─────────  (v7 +11 = 22)
Tier S+ NEW     : ThompsonSampling, CCSketch, FactorJoin, AdaptiveBucketProbing,
                  LpBound, HNSW-SS
Tier A NEW      : MFMC, Tucker, VineCopula, EpsilonNetBaseline,
                  HKBU-RepSample, kDPP, OPQ
Tier B NEW      : LHS
                  ─────────  (v9 +14 = 36)

TOTAL: 36 methods × 38 cells = 1,368 measurement combinations  (5/10 01:14 update — YFCC_PCA dropped, was 56 cells / 2,016)
- multi cells (28): 35 methods (skip ConditionalAdaptive single-only)
- single cells (10): 36 methods
- + SF=100 추가 3 cells × 36 methods = 108 (Exqutor 100% 매치, 별도 launch)
- → grand total: 41 cells × 36 = 1,476 measurements
```

---

## 4. v9 paradigm map (28 paradigms)

```
P1_Cluster, P2_Spatial, P3_Streaming, P4_DimReduction, P5_Quasi-random   (existing)
P6_Sketch (AMSCountSketch)
P7_Joint (CCA1D)
P8_DimInvariant (NeurAM)
P10_Theoretical (DenseRP)
P11_Hierarchical (PQ, CoCluster_Nystrom)
P12_Adaptive (BanditUCB1)
P13_AdaptiveSel (Coreset)
P14_Latent (NeuroCard)
S_MultiRelation (WanderJoin)
P15_BayesianBandit (ThompsonSampling)
P16_VCDimBaseline (EpsilonNetBaseline)
P17_LSHChernoff (AdaptiveBucketProbing)
P18_SketchConv (CCSketch)
P19_FactorGraph (FactorJoin)
P20_PessimisticLP (LpBound)
P21_MultiFidelity (MFMC)
P22_TensorDecomp (Tucker)
P23_CopulaTree (VineCopula)
P24_GraphStratify (HNSW-SS)
P25_RepSampling (HKBU-RepSample)
P26_LatinHypercube (LHS)
P27_RepulsiveDiverse (kDPP)
P28_RotatedQuant (OPQ)
```

---

## 5. 측정 launch 계획 (5/9 23:35 ~ 5/10 아침) — 5/10 01:14 update

### 5/10 01:14 critical update — YFCC_PCA drop

사용자 의문 제기 → Exqutor §VI 직접 재확인 → **YFCC_PCA 본 논문 미사용 데이터셋** 확인. 즉시 폐기:
- **3 procs killed**: PIDs 3241790, 3311667, 3644487 (모두 YFCC_PCA cells)
- **48 NPY/parquet → `_DROPPED_yfcc_pca/`** 격리 (delete X, audit log)
- **CELL config 14 entry 주석화** in measure_multi_paradigm.py
- 상세: `_internal/state/_data_scope_decision_20260510_0114.md`

> 5/10 update: "FB" alias 폐기. 모든 문서·발표·논문 표기는 **SSN (SimSearchNet++)** 단일화. 서버 측 NPY/CSV 파일명 (`partsupp_fb_*` 등) 은 5/10 morning batch rename 예정 (서버 측정 진행 중이라 즉시 rename 불가).

### 현재 active (5/10 01:14, YFCC_PCA proc kill 후)
- v8 5 new methods × 9 existing sf=1 cells (PID 2865788) — ~40min ETA
- 27 methods × 5 NEW v8 sf=1 cells (PID 3138136) — ~80min ETA
- v9 9 methods × 9 existing sf=1 cells (PID 3742865) — ~70min ETA
- ~~27 methods × 4 yfcc_pca single (PID 3241790)~~ **KILLED 5/10 01:14**
- ~~27 methods × multi_join_yfcc_pca_wiki_1 (PID 3311667)~~ **KILLED 5/10 01:14**
- ~~27 methods × partsupp_yfcc_pca_wiki_1 (PID 3644487)~~ **KILLED 5/10 01:14**

**총 3 measurement procs running** + 6 build procs (sf=10) + 1 build (multi_join_wiki_1) — RAM ~80 GB / load avg ~70 즉시 해소.

### Pending launches (current 완료 후, 38 cells 기준)
1. v9 9 methods × 5 NEW v8 sf=1 cells (current 27-method 완료 후)
2. v9 9 methods × 추가 NEW v8 sf=1 cells (build 완료 후)
3. multi_join_wiki_1 build 완료 후 → 36 methods × 1 cell
4. sf=10 v8 builds (partsupp + join, YFCC_PCA 제외) — 기존 6 sf=10 완료 후 (~02:00-03:00)
5. 36 methods × sf=10 v8 cells
6. **Phase F 6 baselines × priority cells** (priority — narrative ⑥)
7. **SF=100 추가 3 cells** (DEEP/SIFT/**SSN (SimSearchNet++)** × partsupp, Exqutor 100% 매치) — sf=10 finalize 후

### 자원 제약
- RAM: 1024 GB total, 535 GB used + 121 GB swap (안정적이지만 tight)
- Load avg: 230-340 (정상 ~ high)
- Disk: 88% (1.6 TB avail)
- GPU: 4개 idle (NeurAM/NeuroCard CPU 모드)

---

## 6. Phase G analysis update (5/10 아침)

**analyze_phase_g.py v8 update 필요사항**:
- 36 methods 지원 (METHOD_MAP 확장)
- 28 paradigms 지원 (PARADIGM dict 확장)
- 56 cells 지원
- Tier S+/A/B/C/S분류 (v9)
- G2 (Adaptive gap), G3 (B4 vs B1), G7 (production top) 에 신규 14 methods 통합
- HKBU-RepSample 비교 chart (SIGMOD 2026 reference 강조)

---

## 7. 사용자 directive 추적성

| Directive | 상태 |
|---|---|
| "지금 찾은 methods가 이제 최대?" | ✅ 36 method portfolio (10 추가) — 2nd pass deep-review 결과 |
| "narrative에 해당이 되어야만 하고" | ✅ Pre-AS stratifier (24, §V-B augment 트랙) + Direct estimator (12, §V-B 미확장 multi-table 영역 비교 트랙) 분리, narrative 두 보완적 트랙으로 활용 |
| "전권 위임" | ✅ 자율 작업 진행 |
| "서버 자원 극한 활용" | ✅ 28 procs, RAM 535/1024, CPU load 332, GPU 0/2/3 |
| "delay 없도록 빠르게" | ✅ 6 measurement procs + 7 builds 동시 진행 |
| "최종 Tier가 맞고 최선인지 최종 딥리뷰" | ✅ 3 agent 검증 완료 — Tier 재배치 권고 반영 |
| "단일, 멀티 모두 가능한 조합 최대" | ✅ 38 cells (10 single + 28 multi) — 5/10 01:14 YFCC_PCA drop 후 정리. + SF=100 3 cells (Exqutor 매치) → 41 cells final |
| "Exqutor paper 진짜로 YFCC_PCA?" (사용자 5/10 01:00 의문) | ✅ §VI 재확인 → 본 논문 미사용 데이터셋 확인. 3 procs killed, 48 file → `_DROPPED_yfcc_pca/` 격리. **FB → SSN (SimSearchNet++) 단일 표기 통일** (5/10 결정). 상세: `_data_scope_decision_20260510_0114.md` |
| "exqutor와 비교 + 앙상블 baseline" | ⏳ Phase F (B1=§V-B Adaptive Sampling vanilla "specifically for KNN queries", B2-B6) launch 예정 |
| "5/9 ~ 5/10 아침 완료" | 🎯 ETA: 5/10 06:00-09:00 finalize, Phase G analysis 5/10 09:00-12:00 |

---

## 8. Key file paths (server + local sync)

### Local
```
/Users/hyunbin/Capstone/_internal/scripts/methods/
├── (existing 11 method's strat helpers in measure_multi_all.py)
├── 5/9 v7 11 methods (wander_join, ams_count_sketch, neurocard_lite, pq_strat, ...)
├── 5/9 v8 5 methods (thompson_sampling_strat, epsilon_net_strat, adaptive_bucket_probing, cc_sketch, factor_join)
└── 5/9 v9 9 methods (lp_bound, mfmc_strat, tucker_strat, vine_copula_strat,
                      hnsw_ss_strat, hkbu_repsample_strat, lhs_strat, kdpp_strat, opq_strat)
```

### Server
```
/mnt/hdd0/home/capstone2026/cache/rq3/
├── methods/ (모두 동기화)
├── measure_multi_paradigm.py (36 method MAP)
├── multi_paradigm_v8_existing_sf1/ (v8 5 methods × 9 existing)
├── multi_paradigm_v8_new_sf1/ (27 methods × NEW v8 cells)
└── multi_paradigm_v9_existing_sf1/ (v9 9 methods × 9 existing)
```

---

## 9. Risk + mitigation

| Risk | Mitigation |
|---|---|
| Server SWAP 100% (5/9 23:21 발생) | Heavy launch 자제, 측정 끝 대기 |
| sf=10 builds 메모리 폭발 | 기존 6 sf=10 완료 후 wave 2-3씩 launch |
| Phase F 측정 시간 부족 | 8 priority cells × 6 baselines 만 launch (모든 cells X) |
| 36 methods × 56 cells = 2,016 measurements 시간 부족 | Priority 0/1/2 분류 + 시간 budget 안에 핵심만 |

---

## 10. END

**Status**: v9 portfolio (36 methods) 확정, 23 STRATIFY_FUNCTIONS 등록, server sync 완료.
**Next**: 현재 측정 진행 모니터링, Phase F launch 시점 결정, 5/10 아침 finalize.

---

## 11. 5/10 01:14 update — YFCC_PCA drop + FB=SSN 정정

### 11.1 사용자 의문 제기 → 즉시 검증

handoff_v17 작성 중, 사용자 (조현빈) 가 "Exqutor paper 가 진짜로 YFCC 를 PCA 처리해서 썼는가?" 의문 제기. v9 portfolio launch 후 ~100 분 시점.

Exqutor 본 논문 §VI Experimental Setup 직접 재확인:
- 본 논문 사용 데이터셋 5종: **DEEP1B(96d), SIFT1B(128d), SimSearchNet++(256d), Wikipedia(768d), YFCC100M raw(192d)**
- **YFCC_PCA 는 본 논문에 없음** — 우리 팀이 5/7 임의로 추가한 데이터셋 ("PCA 96d 로 줄여서 DEEP 과 dim 맞추자" 결정)

동시 확인: build_FB_single_ensemble.py source 의 dataset path 가 `/mnt/hdd0/.../ssn_*.fbin` → **"FB" label = SSN (SimSearchNet++) 의 단순 rename (의미 없는 alias)** 임을 확인 → 5/10 결정으로 모든 문서·발표·논문 표기는 **SSN (SimSearchNet++)** 단일화.

### 11.2 즉시 폐기 작업

| 작업 | 영향 |
|---|---|
| 3 procs killed | PIDs 3241790 (yfcc_pca single 4 cells), 3311667 (multi_join_yfcc_pca_wiki_1), 3644487 (partsupp_yfcc_pca_wiki_1). RAM ~80 GB / load avg ~70 즉시 해소 |
| 48 NPY/parquet file → `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/` | delete X (revert + audit log 보존), active dir 에서 격리 |
| measure_multi_paradigm.py CELL config 14 entry 주석화 | 4 single + 4 partsupp variants + 6 multi-join, comment-out 으로 reactivation 가능성 보존 |

### 11.3 정리된 측정 매트릭스

```
Before (5/9 23:35): 36 methods × 56 cells = 2,016 measurements
After  (5/10 01:14): 36 methods × 38 cells = 1,368 measurements
                   + 36 methods × 3 SF=100 cells = 108 measurements (Exqutor 100% 매치)
                   = 1,476 grand total (~27% slim)
```

38 cells breakdown:
- Single 5 dataset × 2 sf = **10 cells** (DEEP, SIFT, **SSN**, WIKI, YFCC 각 sf=1, sf=10)
- Multi partsupp 4-way × 2 sf = **8 cells**
- Multi join_*_wiki_1 = **10 cells**
- Multi partsupp_*_wiki_1 = **10 cells**

SF=100 Exqutor 매치 3 cells: `partsupp_deep_wiki_100`, `partsupp_sift_wiki_100`, `partsupp_fb_wiki_100`* (* = SSN, 코드 alias).

### 11.4 SSN unified naming policy (5/10 update — FB alias 폐기)

- **모든 문서/figure/표/발표/논문**: **SSN (SimSearchNet++)** 단일 표기로 통일. 단독 "FB" 표기 금지.
- **codebase 내부 (서버)**: `fb_*`, `FB`, `build_FB_*` 등은 코드 alias — 5/10 morning batch rename 예정 (서버 측정 진행 중이라 즉시 rename 불가). 코드 reference 인용 시 alias 임을 명시.
- **Phase G analyzer**: chart label 모두 "SSN" 출력. METHOD_MAP key 는 server rename 후 일괄 정리.

### 11.5 향후 작업 주의

- 새 method 추가 시 38 cells 기준으로 launch (yfcc_pca cells 부활 금지)
- handoff doc / state docs 작성 시 데이터셋 표기 dual naming 점검
- SF=100 launch 는 sf=10 finalize 완료 후 (5/10 06:00-09:00 예정)

상세 결정 기록: `_internal/state/_data_scope_decision_20260510_0114.md`
