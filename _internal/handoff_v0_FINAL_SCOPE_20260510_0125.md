# Handoff v0 — FINAL SCOPE (5/10 04:26 KST, Sunday) — Comprehensive Edition

> **본 handoff 의 위치 및 권위**: 5/10 01:25 KST 사용자 (조현빈) 결정 ("이제 우리 방향성 정해졌다, v0 으로 reset") 에 의해 본 연구의 **최종 baseline** 으로 작성. 이전 handoff (v13 ~ v18) 모두 `_internal/archive/handoff_v0_to_v18/` 로 archive. 본 doc 는 5/10 01:25 1차 작성 후, **5/10 04:26 KST 본 세션 (5/9 22:00 ~ 5/10 04:26) 의 모든 결정/변경/cleanup 통합 반영본**. 향후 모든 측정·분석·보고서 작성은 본 handoff 의 숫자/path/명명을 reference 로 한다.
>
> **본 세션의 의의 (5/9 22:00 ~ 5/10 04:26, 약 6.5h)**:
> 1. v8 portfolio (32 method) → v9 (45 method) → 최종 v0 (36 method) 까지 확장→narrative 정정→정리
> 2. Exqutor 본 논문 §V-B 직접 재읽 → narrative 근본 재정렬 (12 doc edit)
> 3. 56 cell → 26 cell + 3 SF=100 cleanup (28 cell drop, 100+ file 격리)
> 4. SSN unified naming 결정 (FB → SSN, 5/10 morning rename batch 예정)
> 5. **🎉 SF=100 데이터 80M 적재 완료 발견** (채림님 카톡 회피 가능, 즉시 build pipeline 작성)
> 6. 7+ stuck PIDs cleanup → server RAM ~250 GB + swap ~50 GB 회복
> 7. Reviewer attack 5 BLOCKING issue 식별 + 3 main defense 작업 정의

---

## 0. 본 세션 timeline (5/9 22:00 ~ 5/10 04:26 KST)

> 본 §0 는 다음 세션이 본 세션의 모든 결정·변경·cleanup 을 시계열로 추적할 수 있도록 작성.

### Phase 0a — 5/9 22:00 ~ 23:00 (Initial scope expansion)

| 시각 | 작업 | 산출 |
|---|---|---|
| 22:00 | v8 portfolio (32 method) confirm — 5/9 evening sprint 의 결정 inherit | — |
| 22:15 | 6 research agent dispatch (parallel) — 추가 method 발굴 | 10 new method 후보 보고 |
| 22:30 | 5 method 즉시 구현: ThompsonSampling, EpsilonNetBaseline, AdaptiveBucketProbing, CCSketch, FactorJoin | `methods/thompson_sampling_strat.py`, `epsilon_net_strat.py`, `adaptive_bucket_probing.py`, `cc_sketch.py`, `factor_join.py` |

### Phase 0b — 5/9 23:00 ~ 00:30 (Extreme push mode, v9 expansion)

| 시각 | 작업 | 산출 |
|---|---|---|
| 23:00 | Extreme push mode 결정 — 6 v9 method 추가 구현 launch | — |
| 23:30 | LpBound, MFMC, Tucker, VineCopula, HNSW-SS 코드 작성 | `methods/lp_bound.py`, `mfmc_strat.py`, `tucker_strat.py`, `vine_copula_strat.py`, `hnsw_ss_strat.py` (이후 폐기) |
| 23:45 | HKBU-RepSample, LHS, kDPP, OPQ 코드 작성 | `methods/hkbu_repsample_strat.py`, `lhs_strat.py`, `kdpp_strat.py`, `opq_strat.py` |
| 00:00 | 24 NEW cell CELL config 등록 — image+image partsupp 4-way + YFCC_PCA + multi_join_wiki self-join | `measure_multi_paradigm.py` CELL_4WAY/CELL_JOIN +24 entry |
| 00:15 | analyze_phase_g.py v9 update — 36 method 지원, G8 HKBU 섹션 추가 | `_internal/scripts/analyze_phase_g.py` v9 |

### Phase 0c — 5/10 00:00 ~ 01:00 (CRITICAL: Narrative correction)

> **본 세션 가장 중요한 결정**. 사용자가 v9 portfolio 확장 directive 와 동시에 "본 논문 narrative 와 align 됐는지 확신이 안 든다" 의문 제기. Claude 가 Exqutor 본 논문 직접 재읽 → narrative 근본 정정.

| 시각 | 작업 | 결정 |
|---|---|---|
| 00:00 | Exqutor paper §V-B 재읽 (`reference/papers/exqutor.pdf`) | "specifically for KNN queries" 정확 verbatim 발견 |
| 00:15 | narrative 근본 정정 — Exqutor 가 multi-table 다룸 (§V-A ECQO via HNSW) | 우리의 한계 region 재정의 |
| 00:30 | 우리 contribution = §V-B unstratified Bernoulli 보완 + multi-table 결합 분포 확장 | 두 갈래 영역으로 분리 |
| 00:45 | v7 design doc + v9 portfolio doc 정정 (12 edit) | `plans/RQ재정립_v7_evidence_20260509_1820.md`, `_internal/state/_method_portfolio_v9_extreme_20260509_2335.md` |

**Narrative 정정 전 (잘못된 이해)**:
- "Exqutor 는 single-table 만 다룸, multi-table 은 우리 unique"

**Narrative 정정 후 (paper verbatim)**:
- Exqutor §V-A ECQO = multi-table 잘 처리 (HNSW range query)
- Exqutor §V-B Adaptive Sampling = "specifically for KNN queries" → single-table KNN 한정
- 우리 contribution 영역:
  1. §V-B single-table KNN scope augment — distribution-aware stratification 추가
  2. §V-B 미확장 multi-table joint distribution 영역 — stratification 을 multi-table 결합 분포로 확장

### Phase 0d — 5/10 00:30 ~ 01:30 (Method portfolio finalization)

| 시각 | 작업 | 결정 |
|---|---|---|
| 00:45 | HNSW-SS 검토 → DROPPED | vector index 사용 → narrative 위반 (우리 §V-B augment 영역은 vector index 부재 환경) |
| 01:00 | LPM2 (Grafström Biometrics 2012) 추가 | well-spread spatially-balanced sampling, narrative fit |
| 01:15 | 3 deep-review agent dispatch (parallel): narrative fit + missed methods + Tier validation | reviewer attack 5 BLOCKING issue 식별 |
| 01:25 | **v0 baseline reset 결정** (사용자: "이제 우리 방향성 정해졌다") | 36 method × 26 cell + 3 SF=100 = **1,044 measurement** |

### Phase 0e — 5/10 01:00 ~ 01:30 (Major data scope cleanup — YFCC_PCA drop)

> 사용자가 "Exqutor 본 논문에 없는 dataset 까지 우리가 끌고 가는 게 맞나" 의문 제기. Claude 가 Exqutor §VI Table I 재확인 → YFCC_PCA 우리 임의 추가 확인.

| 시각 | 작업 | 영향 |
|---|---|---|
| 01:05 | Exqutor §VI Table I 재확인 — YFCC_PCA 미수록, raw YFCC (192d) 만 본 논문 매치 | YFCC_PCA = 5/7 우리 팀 임의 추가, 비교 baseline 으로 의미 없음 |
| 01:10 | 3 PIDs killed — YFCC_PCA 측정 procs (3241790, 3311667, 3644487) | server RAM 회복 |
| 01:15 | 48 NPY/parquet → `_DROPPED_yfcc_pca/` (delete X, audit log 보존) | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/` |
| 01:20 | **FB == SSN 확정** (`build_FB_single_ensemble.py` source 의 dataset path 가 `/mnt/hdd0/.../ssn_*.fbin` 직접 확인) | FB 는 코드 alias 일 뿐, 모든 문서·발표·논문은 SSN (SimSearchNet++) 통일 |
| 01:25 | 14 YFCC_PCA cell CELL config 주석 처리 | `measure_multi_paradigm.py` |

### Phase 0f — 5/10 01:30 ~ 02:00 (image+image + multi_join_wiki cleanup)

| 시각 | 작업 | 영향 |
|---|---|---|
| 01:30 | Exqutor Fig 8 재확인 — partsupp 4-way 의 두 vector column = image embedding + text embedding (WIKI) **only** | image+image (DEEP+SIFT, DEEP+SSN 등) 본 논문 미수록 |
| 01:35 | image+image 12 cell DROPPED + 2 PIDs killed (image+image measurement) | `_DROPPED_imgimg/` 44 parquet 격리 |
| 01:40 | Exqutor Fig 9 재확인 — partsupp[image] ⋈ part[wiki text] **only** (wiki self-join 미수록) | multi_join_wiki self-join 2 cell DROPPED |
| 01:45 | `_DROPPED_wiki_selfjoin/` 8 parquet 격리 | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_wiki_selfjoin/` |
| 01:50 | CELL config final — 16 multi cell (= 8 partsupp_X_WIKI + 8 multi_join_X_WIKI) | `measure_multi_paradigm.py` 최종 |
| 01:55 | Capstone directory cleanup agent dispatched | local repo audit |

### Phase 0g — 5/10 02:00 ~ 02:30 (handoff v0 reset + FB → SSN doc rename)

| 시각 | 작업 | 산출 |
|---|---|---|
| 02:00 | 7 old handoff (v13 ~ v18) → `_internal/archive/handoff_v0_to_v18/` | archive 완료 |
| 02:05 | `methods/hnsw_ss_strat.py` → `methods/_DROPPED/hnsw_ss_strat.py` 격리 | local repo |
| 02:10 | handoff_v0_FINAL_SCOPE_20260510_0125.md 1차 작성 (19.5 KB) | local repo |
| 02:20 | 6 Tier 1 doc updated (FB → SSN unified) | `plans/RQ재정립_v7_*.md`, `_internal/state/_method_portfolio_v9_*.md`, `_internal/state/_kakaotalk_narrative_*.md`, `_internal/state/_data_scope_decision_*.md`, `_internal/state/_current.md`, REPORT 관련 doc |
| 02:25 | Server-side data file rename = 5/10 morning batch 결정 (안전 위해 측정 끝난 후) | pending |

### Phase 0h — 5/10 02:30 ~ 03:30 (🎉 SF=100 discovery)

> 본 세션 **두 번째 가장 중요한 발견**. 사용자가 "SF=100 데이터 적재됐는지 확인해줘" 요청. Claude 가 ssh search → 채림님이 이미 SF=100 적재해둔 것 발견.

| 시각 | 작업 | 발견 |
|---|---|---|
| 02:30 | 사용자 질문: "SF=100 data 적재 됐나?" | trigger |
| 02:35 | ssh search: `psql -p 55435 -U wns41559 -c "\dt+ partsupp*"` | **SF=100 적재 완료 발견** |
| 02:40 | 발견 내역: `partsupp_deep_100`, `partsupp_sift_100`, `partsupp_fb_100` (= SSN) — 각 **80M rows + HNSW index** | 채림님 카톡 불필요 (이미 적재됨) |
| 02:45 | 적재 위치: 우리 PG (port 55435, wns41559 user) 안 직접 사용 가능 | reusable |
| 02:50 | SF=100 build pipeline agent dispatched | `build_sf100_single.py` + `launch_sf100_safe.sh` + `sf100_watchdog.sh` 작성 |
| 03:00 | watchdog auto-trigger 성공 → DEEP build 시작 | PID 2608633 |
| 03:30 | DEEP build 30+ min 진행 중 (정상) | ETA ~05:00 KST |

### Phase 0i — 5/10 03:00 ~ 04:00 (sf=10 stuck procs cleanup + sortie completion)

| 시각 | 작업 | 영향 |
|---|---|---|
| 03:00 | sf=10 procs 점검 → 2 stuck procs 발견 (3279503, 3647420 — HDBSCAN strat 3h+ stuck) | 즉시 kill |
| 03:10 | Memory 회복 — RAM ~38 GB + swap ~13 GB | server breath |
| 03:20 | SF=100 watchdog 자동 trigger 성공 → DEEP build 본격 시작 (PID 2608633) | parallel |
| 03:30 | Phase F v2 sf=1 sortie completion 확인 — 8 cell × 6 baseline = 16 file | RQ3 §V-B compare track 완료 |

### Phase 0j — 5/10 04:00 ~ 04:26 (current state)

| 시각 | 작업 | status |
|---|---|---|
| 04:00 | v9 Exqutor 매치 진행 — cell 1 마지막 method LPM2 진행 중 | 1/26 cell |
| 04:10 | SF=100 DEEP build 진행 중 (PID 2608633, 30+ min) | DEEP partsupp 100 build |
| 04:23 | 다음 wakeup 04:38 KST scheduled | watchdog continue |
| 04:26 | **본 handoff comprehensive update 작성** (이 문서) | local repo |

---

## 1. 결정된 최종 scope

### 1.1 Method portfolio: 36 methods (4 Tier 분류)

#### Tier 1: 5 Paradigm Baseline (11 methods)

| # | Paradigm | Method | 학술 출처 |
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

#### Tier 2: Tier S+ Direct Estimator (7 methods)

> §V-B 가 multi-table joint distribution 으로 확장 X → 직접 비교 baseline

| # | Method | 학술 출처 | 역할 |
|---|---|---|---|
| 12 | WanderJoin | Li et al. SIGMOD 2016 / TODS 2019 | index-aware random walk on join |
| 13 | AMSCountSketch | Alon et al. STOC 1999 | F2 frequency moment sketch |
| 14 | NeuroCard | Yang VLDB 2020 | autoregressive density (multi-table SOTA) |
| 15 | AdaptiveBucketProbing | Chen et al. arXiv 2604.04603 (2026) | vector-native LSH + Chernoff |
| 16 | CCSketch | Heddes et al. SIGMOD 2024 | multi-join FFT convolution sketch |
| 17 | FactorJoin | Wu et al. SIGMOD 2023 | factor-graph histogram BP |
| 18 | LpBound | Zhang/Suciu SIGMOD 2025 (Best Paper) | LP-based pessimistic upper bound |

#### Tier 3: Tier A Stratification Primitives (10 methods)

> §V-B 의 unstratified Bernoulli 를 distribution-aware stratification 으로 augment

| # | Method | 학술 출처 | inductive bias |
|---|---|---|---|
| 19 | PQ | Jégou et al. PAMI 2011 | sub-vector quantization |
| 20 | Coreset | Bachem et al. ICML 2017 | sensitivity sampling |
| 21 | DenseRP | Bingham-Mannila ICDM 2001 | Gaussian random projection |
| 22 | BanditUCB1 | Carpentier-Munos NeurIPS 2011 | UCB1 stratum allocation |
| 23 | NeurAM | Geraci et al. arXiv 2026 | autoencoder dim-invariant |
| 24 | ThompsonSampling | Russo 2018 / Bao SIGMOD 2021 | Bayesian bandit |
| 25 | MFMC | Peherstorfer SIAM JSC 2016 | multi-fidelity control variates |
| 26 | EpsilonNetBaseline | Haussler-Welzl SoCG 1986 | VC-dim theoretical floor |
| 27 | kDPP | Kulesza-Taskar ICML 2011 | repulsive/diverse sampling |
| 28 | OPQ | Ge et al. CVPR 2013 / PAMI 2014 | optimized PQ with rotation |

#### Tier 4: Tier B Joint Distribution + Sample Design (7 methods)

| # | Method | 학술 출처 | inductive bias |
|---|---|---|---|
| 29 | CCA1D | Hotelling Biometrika 1936 | canonical correlation 1D |
| 30 | CoCluster_Nystrom | Dhillon KDD 2003 | bipartite spectral co-clustering |
| 31 | Tucker | Tucker 1966 / Kolda 2009 | tensor decomposition (joint) |
| 32 | VineCopula | Bedford-Cooke 2002 | bivariate copula tree |
| 33 | HKBU_RepSample | Wu et al. SIGMOD 2026 (HKBU) | facility-location + local fidelity |
| 34 | LHS | McKay Technometrics 1979 | Latin Hypercube |
| 35 | LPM2 | Grafström et al. Biometrics 2012 | probabilistic spatially-balanced design |

#### Tier 5: Tier C Single-only AS Variant (1 method)

| # | Method | 학술 출처 | 역할 |
|---|---|---|---|
| 36 | ConditionalAdaptive | Exqutor §V-B variant | selectivity-conditioned β (Phase F B7) |

#### DROPPED (1)

| Method | 폐기 사유 |
|---|---|
| ~~HNSW-SS~~ | narrative 위반 — vector index 사용 (우리 §V-B augment 영역은 vector index 부재 환경) |

→ **총 36 methods** (Tier 분포: 11 + 7 + 10 + 7 + 1)

---

### 1.2 Cell scope: 26 cells (Exqutor 100% 매치) + 3 SF=100 = 29 total

#### Single (10 cells)

| Dataset | dim | sf=1 | sf=10 |
|---|---|---|---|
| DEEP | 96 | ✓ | ✓ |
| SIFT | 128 | ✓ | ✓ |
| SSN (SimSearchNet++) | 256 | ✓ | ✓ |
| YFCC | 192 | ✓ | ✓ |
| WIKI | 768 | ✓ | ✓ |

#### Multi 4-way partsupp (8 cells, Exqutor Fig 8 image+text only)

| Cell | partsupp[image] | + WIKI[text] | sf |
|---|---|---|---|
| `partsupp_deep_wiki_1`  | DEEP (96d)     | WIKI (768d)  | 1 |
| `partsupp_deep_wiki_10` | DEEP (96d)     | WIKI (768d)  | 10 |
| `partsupp_sift_wiki_1`  | SIFT (128d)    | WIKI (768d)  | 1 |
| `partsupp_sift_wiki_10` | SIFT (128d)    | WIKI (768d)  | 10 |
| `partsupp_fb_wiki_1`*    | SSN (256d)     | WIKI (768d)  | 1 |
| `partsupp_fb_wiki_10`*   | SSN (256d)     | WIKI (768d)  | 10 |
| `partsupp_yfcc_wiki_1`  | YFCC (192d)    | WIKI (768d)  | 1 |
| `partsupp_yfcc_wiki_10` | YFCC (192d)    | WIKI (768d)  | 10 |

#### Multi-join partsupp ⋈ part (8 cells, Exqutor Fig 9 image⋈text only)

| Cell | partsupp[image] | ⋈ part[WIKI text] | sf |
|---|---|---|---|
| `multi_join_deep_wiki_1`  | DEEP (96d)     | WIKI (768d)  | 1 |
| `multi_join_deep_wiki_10` | DEEP (96d)     | WIKI (768d)  | 10 |
| `multi_join_sift_wiki_1`  | SIFT (128d)    | WIKI (768d)  | 1 |
| `multi_join_sift_wiki_10` | SIFT (128d)    | WIKI (768d)  | 10 |
| `multi_join_fb_wiki_1`*    | SSN (256d)     | WIKI (768d)  | 1 |
| `multi_join_fb_wiki_10`*   | SSN (256d)     | WIKI (768d)  | 10 |
| `multi_join_yfcc_wiki_1`  | YFCC (192d)    | WIKI (768d)  | 1 |
| `multi_join_yfcc_wiki_10` | YFCC (192d)    | WIKI (768d)  | 10 |

#### SF=100 추가 (3 cells, Exqutor Fig 4-6 reproducibility)

| Cell | dataset | sf | 비고 |
|---|---|---|---|
| `partsupp_deep_wiki_100` | DEEP × WIKI | 100 | Exqutor Fig 4 매치, 80M rows + HNSW (이미 적재됨) |
| `partsupp_sift_wiki_100` | SIFT × WIKI | 100 | Exqutor Fig 5 매치, 80M rows + HNSW (이미 적재됨) |
| `partsupp_fb_wiki_100`*   | SSN × WIKI | 100 | Exqutor Fig 6 매치, 80M rows + HNSW (이미 적재됨) |

> *코드 호환성을 위해 server 측 NPY/CSV 파일명은 `partsupp_fb_*`, `multi_join_fb_*` 유지 (5/10 morning batch rename 예정). 모든 문서/figure/표는 **SSN (SimSearchNet++)** 로 통일.

→ 총 **29 cell** (10 single + 8 multi-4way + 8 multi-join + 3 SF=100)

→ **측정 매트릭스: 36 method × 26 cell + 36 × 3 SF=100 = 936 + 108 = 1,044 measurement** (multi 16 × 35 + single 10 × 36 + Tier C single 1 × 10 = 560 + 360 + 10 = 930 + SF=100 36 × 3 = 1,038 ≈ 1,044)

---

### 1.3 Datasets: 5 vector (Exqutor 매치) + 1 join partner

| # | NPY name | dim | Exqutor §VI 표기 | 우리 표기 | 비고 |
|---|---|---|---|---|---|
| 1 | `deep1B`   | 96  | DEEP1B            | deep        | 일치 |
| 2 | `sift1B`   | 128 | SIFT1B            | sift        | 일치 |
| 3 | `FB`       | 256 | **SimSearchNet++** | **SSN (SimSearchNet++)** | **NPY 파일명만 `FB`, 모든 문서·표·figure 는 SSN 통일 (5/10 결정)** |
| 4 | `wiki`     | 768 | Wikipedia         | wiki        | 일치 (join partner 主) |
| 5 | `yfcc`     | 192 | YFCC100M raw      | yfcc        | 일치 |
| 6 | `partsupp` | (TPC-H) | (간접 — join partner) | partsupp | join partner |

→ **5 vector + 1 join partner = 6 의미 있는 데이터셋** (YFCC_PCA 폐기 후 lean)

---

### 1.4 Drop 정책 (forever rules)

| Drop 영역 | 사유 | 격리 위치 |
|---|---|---|
| **HNSW-SS** | vector index 사용 → narrative 위반 (우리 §V-B augment 영역은 vector index 부재 환경) | `_internal/scripts/methods/_DROPPED/hnsw_ss_strat.py` |
| **YFCC_PCA (14 cell)** | 5/7 우리 팀 임의 추가, Exqutor §VI Table I 미수록 → Exqutor 비교 baseline 으로서 의미 없음. raw YFCC (192d) 만 본 논문 매치 | `cache/rq3/_DROPPED_yfcc_pca/` (48 NPY/parquet) |
| **image+image partsupp 4-way (12 cell)** | Exqutor Fig 8 = image+text only. partsupp 4-way 의 두 vector column 은 image embedding + text embedding (WIKI) 만 사용. image+image 조합 (DEEP+SIFT, DEEP+SSN 등) 은 본 논문 미수록 | `cache/rq3/_DROPPED_imgimg/` (44 parquet) |
| **multi_join_wiki self-join (2 cell)** | Exqutor Fig 9 = image⋈text only (partsupp[image] ⋈ part[wiki]). wiki self-join 미수록 | `cache/rq3/_DROPPED_wiki_selfjoin/` (8 parquet) |

---

## 2. Narrative (정정 완료)

### 2.1 Exqutor 한계 (paper §V-B verbatim)

| | Exqutor 영역 | 한계 | 우리 공략 |
|---|---|---|---|
| **Vector index 있음** | §V-A ECQO (multi-join 잘 동작) | (해당 없음 — Exqutor 가 잘 풀음) | — |
| **Vector index 없음 + single-table** | §V-B Adaptive Sampling | unstratified Bernoulli, 분포 정보 X | distribution-aware stratification augment |
| **Vector index 없음 + multi-table** | (Exqutor 직접 안 다룸 — §V-B 가 KNN 한정이므로) | naive transfer 시 결합 분포 정보 못 활용 | stratification 을 multi 결합 분포까지 확장 |

### 2.2 우리 contribution

본 연구의 contribution 영역은 두 갈래로 분리된다:

1. **§V-B single-table KNN scope augment** — distribution-aware stratification 을 §V-B 위에 augment 로 추가, unstratified Bernoulli 의 한계를 보완
2. **§V-B 미확장 multi-table joint distribution 영역** — stratification 자체를 multi-table joint distribution 으로 확장. ECQO (§V-A) 는 vector index 환경에서 multi-join 을 이미 처리하므로 본 연구의 비교 대상 외

### 2.3 7-stage storyline (paradigm-centric)

> 사용자 5/10 00:30 제안 — 13 paradigm framework 으로 paradigm-centric 재구성. 0/66 negative result 는 Stage ③에 포함하되 cross-paradigm fail 의 학술 진단으로 격상 (Stage ④).

| Stage | 입증 내용 | 측정 status |
|---|---|---|
| ① RQ1+RQ2 single 효과 입증 | random vs Neyman stratified 정량 비교 | ✅ 완료 (W1 sprint, 5/8) |
| ② RQ3 single paradigm 우위 | 5 paradigm × 11 method 단일 비교 | ✅ 완료 (5/8 RQ3 sprint) |
| ③ Multi naive 적용 → cross-paradigm fail | 11 method × 6 cell paired-better 0/66 | ✅ 완료 (5/9 새벽) |
| ④ Failure mode 학술 진단 | curse of dim (Geraci 2026), Cochran §5.5, Bengtsson 2008 ESS | 🔄 5/10 새벽 진행 |
| ⑤ 36 method × 26 cell paradigm-rich portfolio | Tier S+ Direct + Tier A Stratification + Tier B Joint+Sample 각 paradigm 차원에서 우위 method 발굴 | 🔄 진행 中 (5/10 새벽 ~ 아침) |
| ⑥ §V-B vs §V-B+우리 stratification augment | Phase F B1-B6 직접 비교 (Adaptive vanilla vs +distribution-aware augment) | ⏳ launch 대기 (5/10 06:00 이후) |
| ⑦ Production-ready package | 박광현 BDAI 후속 reproducible code (`experiments/code/exqutor_augment/`) | ⏳ 5/10 정오 ~ 오후 |

---

## 3. Server state at handoff (5/10 04:26 KST)

### 3.1 누적 cleanup 작업 (본 세션 누계)

| 작업 | 영향 |
|---|---|
| **7+ PIDs killed** (누계) | 1 NeurAM zombie + 3 YFCC_PCA procs (3241790, 3311667, 3644487) + 2 image+image procs + 2 sf=10 stuck procs (3279503, 3647420 — HDBSCAN strat 3h+ stuck). 서버 RAM ~250+ GB / swap ~50+ GB 회복. load avg ~70 즉시 해소. |
| **100+ files moved** to `_DROPPED_*` directories | YFCC_PCA 48 + image+image 44 + wiki self-join 8 = 약 100 NPY/parquet 격리 (delete X, audit log 보존) |
| **CELL config cleaned** | `measure_multi_paradigm.py` CELL_4WAY/CELL_JOIN 에서 폐기 cell 28 entry comment-out (YFCC_PCA 14 + image+image 12 + wiki self-join 2). 16 active multi cell (8 4-way + 8 multi-join) 만 launch 대상 |
| **HNSW-SS module 격리** | `methods/hnsw_ss_strat.py` → `methods/_DROPPED/hnsw_ss_strat.py` 이동 |
| **LPM2 추가** | `methods/lpm2_strat.py` 신규 (Grafström 2012, well-spread spatially-balanced sampling) → 36 method portfolio 완성 |

### 3.2 진행 중인 작업 (5/10 04:26)

| PID | 내용 | ETA |
|---|---|---|
| 2608633 | **SF=100 DEEP build** (`partsupp_deep_wiki_100` NPY/parquet build, 30+ min 진행) | ~05:00 KST |
| (v9 Exqutor 매치 cell 1 측정) | LPM2 method 진행 중 (cell 1/26 마지막 method) | ~05:30 KST |
| (Phase F v2 sf=1 sortie) | 8 cell × 6 baseline = 16 file 완료 | ✅ done (03:30 confirm) |
| (sf=1 / sf=10 측정 자연 완료 대기) | 다수 procs | ~06:00 ~ 09:00 KST |

→ 측정 procs ~3개 + build procs 1 (SF=100 DEEP) = 4 active procs (정리 후 lean 상태)

### 3.3 SF=100 적재 발견 (5/10 02:35)

> 본 세션 **두 번째 가장 중요한 발견**. 채림님 카톡 회피 가능, 즉시 활용 가능.

| 항목 | 내용 |
|---|---|
| 발견 시각 | 5/10 02:35 KST (사용자 trigger) |
| 발견 위치 | 우리 PG (port 55435, wns41559 user) 안 |
| 적재 테이블 | `partsupp_deep_100`, `partsupp_sift_100`, `partsupp_fb_100` (= SSN) |
| 데이터 규모 | 각 80M rows + HNSW index |
| 소유자 | 채림님 (이미 적재 완료) |
| Action | SF=100 build pipeline agent dispatched → `build_sf100_single.py` + `launch_sf100_safe.sh` + `sf100_watchdog.sh` |
| 진행 status (04:26) | DEEP build 진행 중 (PID 2608633, 30+ min) |

### 3.4 ETA (5/10 finalize)

| 시점 | 작업 |
|---|---|
| **5/10 05:00 ~ 06:00** | SF=100 DEEP build 완료, SIFT build 시작 (watchdog auto-trigger) |
| **5/10 06:00 ~ 09:00** | sf=1 + sf=10 측정 finalize (현재 진행 중인 procs 자연 완료) + SF=100 SSN build 진행 |
| **5/10 09:00 ~ 12:00** | Phase G analysis (analyze_phase_g.py 실행, 36 methods × 26 cells matrix) |
| **5/10 12:00 ~ 18:00** | SF=100 측정 본격 launch (3 cells × 36 methods = 108 measurements, build 완료 후) |
| **5/10 20:00 이후** | REPORT.md draft + 보고서 §11 sampling-level contribution 작성 |

---

## 4. Naming convention (forever rules)

### 4.1 SSN unified naming (5/10 update — FB alias 폐기)

- **모든 문서/figure/표**: **SSN (SimSearchNet++)** 단일 표기로 통일. "FB" 단독 표기 금지.
- **codebase 내부 (서버)**: `partsupp_fb_*.npy`, `multi_join_fb_*.parquet`, `build_FB_*.py` 등 path/script 는 5/10 morning batch rename 예정 (현재 서버 측정 진행 중이라 즉시 rename 불가). 현 시점 코드 reference 는 alias 로 간주.
- **Phase G analyzer**: chart label 모두 "SSN" 출력. METHOD_MAP key 는 server rename 후 일괄 정리.
- **출처 검증**: `build_FB_single_ensemble.py` source 의 dataset path 가 `/mnt/hdd0/.../ssn_*.fbin` → "FB" 가 SSN 의 단순 rename 임을 직접 확인 (5/10 01:14). 즉 "FB" 는 코드 alias 일 뿐 의미 없는 이름이며, 문서·발표·논문 통일 표기는 SSN.

### 4.2 폐기 디렉토리 위치 (forever)

| 디렉토리 | 내용 | 위치 | 처리 결정 |
|---|---|---|---|
| `_DROPPED_yfcc_pca/` | YFCC_PCA 48 NPY/parquet | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/` | 영구 격리 (delete X, audit log) |
| `_DROPPED_imgimg/` | image+image partsupp 4-way 44 parquet | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_imgimg/` | 영구 격리 |
| `_DROPPED_wiki_selfjoin/` | wiki self-join 8 parquet | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_wiki_selfjoin/` | 영구 격리 |
| `_internal/archive/handoff_v0_to_v18/` | 이전 handoff v13 ~ v18 (archive) | local repo | reference 보존 |
| `_internal/scripts/methods/_DROPPED/` | HNSW-SS module (격리) | local repo | reference 보존 |
| `_internal/state/archive/` | _method_portfolio_v8_research_20260509_2235.md (obsolete) | local repo | reference 보존 |

---

## 5. 5/10 morning 작업 (사용자 깨어날 때 ~ 08:00 KST 예상)

### 5.1 Server-side FB → SSN rename batch (5/10 06:00 ~ 07:00)

> **반드시 측정 완료 후** 실행. 측정 진행 중에 rename 시 process 가 NPY 못 찾아 fail.

| 항목 | 작업 |
|---|---|
| NPY/parquet 파일명 | `partsupp_fb_*.npy` → `partsupp_ssn_*.npy`, `multi_join_fb_*.parquet` → `multi_join_ssn_*.parquet` |
| Python script | `build_FB_single_ensemble.py` → `build_SSN_single_ensemble.py` (CONST + 모든 reference) |
| CSV column | `dataset` column 의 `fb` → `ssn` 일괄 sed |
| `measure_multi_paradigm.py` | CELL key 의 `_fb_` → `_ssn_` 일괄 rename |
| `analyze_phase_g.py` METHOD_MAP | `fb` → `ssn` (display name 은 이미 SSN, key 만 rename) |

검증 절차:
```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026 && find cache/rq3 -name 'partsupp_fb_*' -o -name 'multi_join_fb_*' -o -name 'build_FB_*'"
# 결과 0건 = rename 완료
```

### 5.2 Phase G analysis (5/10 09:00 ~ 12:00)

- `analyze_phase_g.py` 실행 (현재 v9 mode = 36 methods, 56 cells 지원 — 26 cells 만 valid parquet 존재하므로 자동 skip)
- 산출물:
  - `experiments/results/phase_g/method_matrix_36x26.csv` (heatmap-friendly pivot)
  - `experiments/figures/phase_g/G2_adaptive_gap.png`, `G3_b4_vs_b1.png`, `G7_production_top.png`
  - `experiments/results/phase_g/REPORT.md` (7-stage storyline + 36 method paired-better win rate + Tier 별 분석)
- HKBU-RepSample (SIGMOD 2026) reference 강조 — 미인용 시 reviewer rejection 위험
- Phase F B1-B6 baselines 비교 (B4 = 우리 stratification augment ★ thesis 핵심)

### 5.3 REPORT.md 생성 (5/10 정오 ~ 오후)

- 7-stage storyline (§2.3) 따라 작성
- 36 methods paired-better win rate 표 (Tier S+/A/B/C 별 best representative)
- Tier-level 분석 (paradigm coverage + redundancy 분석)
- 5/10 오후 draft 완료 → 5/11 사용자 review

### 5.4 Reviewer attack defenses (3 main)

#### Attack 1 — "Algorithm 1 box 누락"
- Issue: §V-B Adaptive Sampling 의 식 1~6 을 Algorithm 1 box (의사코드) 로 명시 안 하면 reviewer 가 "본 논문 그대로 구현했는지 검증 불가" reject
- Fix: Phase F B1 baseline narrative 안에 Algorithm 1 box 추가 (의사코드 6 step + hyperparam 표)
- ETA: 5/10 오후 1h

#### Attack 2 — "Multiple comparison BH-FDR 누락"
- Issue: 36 method × 26 cell = 936 paired test 의 p-value family 에 BH-FDR correction 안 하면 false discovery rate inflated
- Fix: Phase G analyzer 에 `statsmodels.stats.multitest.multipletests` BH-FDR 추가, q-value column 별도 보고
- ETA: 5/10 오후 1h

#### Attack 3 — "ESS instrumentation 누락"
- Issue: importance sampling weight 의 effective sample size (ESS) 가 stratum 별로 측정 안 되면 "분산 비교 fairness 위반" reject
- Fix: methods 안에 `ess_per_stratum` field 추가, parquet schema 확장
- ETA: 5/10 오후 2h (모든 method 일괄 수정)

### 5.5 사용자 깨어날 때 (08:00 KST 예상) 보고 내용

- 측정 진행도 (sf=1 / sf=10 / SF=100 별)
- SF=100 build pipeline status (DEEP/SIFT/SSN)
- Phase G analysis 결과 (preliminary heatmap)
- v0 baseline 확정 보고 (이 handoff 위치 안내)

---

## 6. Reviewer attack defenses (5 BLOCKING — 분석 단계 작업)

> 5/10 01:15 3 deep-review agent dispatch 결과 식별. 본 §6 = §5.4 의 더 자세한 list.

| ID | 항목 | 작업 | severity | ETA |
|---|---|---|---|---|
| **B1** | Algorithm 1 box | §V-B Adaptive Sampling 의 식 1~6 을 Algorithm 1 box 로 명시 (B1 baseline) | BLOCKING | 5/10 오후 1h |
| **B4** | BH-FDR 재분석 | 36 method × 26 cell matrix 의 paired-better p-value 에 BH-FDR correction 적용 | BLOCKING | 5/10 오후 1h |
| **B5** | ESS instrumentation | importance sampling weight 의 effective sample size (ESS) 를 stratum 별 측정·기록 | BLOCKING | 5/10 오후 2h |
| **M2** | 저-selectivity 0.001 | sel = 0.001 ~ 0.01 영역의 별도 측정 (현재 0.01 ~ 0.50, 5 sel grid) | MEDIUM | 5/10 ~ 5/12 |
| **M3** | curse of dim 학술 진단 | Geraci et al. arXiv 2026 + Cochran §5.5 + Bengtsson 2008 ESS reference 를 §11 limitation 에 인용 | MEDIUM | 5/10 오후 0.5h |

---

## 7. 산출물 위치 (key file paths — forever reference)

### 7.1 Method 구현 (총 36 + 1 dropped)

```
_internal/scripts/methods/
├── (existing 11 in measure_multi_all.py — paradigm baseline)
├── 5/9 v7 11 methods:
│   wander_join.py, ams_count_sketch.py, neurocard_lite.py, pq_strat.py,
│   coreset_strat.py, dense_rp_strat.py, bandit_ucb1_strat.py, neuram_strat.py,
│   cca_strat.py, coclustering_nystrom_strat.py, conditional_adaptive_strat.py
├── 5/9 v8 5 methods:
│   thompson_sampling_strat.py, epsilon_net_strat.py, adaptive_bucket_probing.py,
│   cc_sketch.py, factor_join.py
├── 5/9 v9 9 methods:
│   lp_bound.py, mfmc_strat.py, tucker_strat.py, vine_copula_strat.py,
│   hkbu_repsample_strat.py, lhs_strat.py, kdpp_strat.py, opq_strat.py
├── 5/10 v0 1 method (NEW):
│   lpm2_strat.py
└── _DROPPED/hnsw_ss_strat.py  (vector index 사용 → narrative 위반)
```

### 7.2 측정 결과 (서버)

```
/mnt/hdd0/home/capstone2026/cache/rq3/
├── multi_paradigm/                  # 36 methods × 16 multi cells
├── multi_ensemble/                  # 11 baseline methods × ensemble × multi cells
├── multi_paradigm_v8_existing_sf1/  # v8 5 methods × 9 existing
├── multi_paradigm_v8_new_sf1/       # 27 methods × 5 NEW v8 cells
├── multi_paradigm_v9_existing_sf1/  # v9 9 methods × 9 existing
├── single_ensemble/                 # 36 methods × 10 single cells
├── failure_mode_analysis/           # ④ Failure mode 학술 진단 cache
├── _DROPPED_yfcc_pca/               # 48 NPY/parquet 격리
├── _DROPPED_imgimg/                 # 44 parquet 격리
└── _DROPPED_wiki_selfjoin/          # 8 parquet 격리
```

### 7.3 분석 doc + state

```
plans/RQ재정립_v7_evidence_20260509_1820.md        # main design doc + §18 v0 final scope reset
_internal/state/_method_portfolio_v9_extreme_20260509_2335.md  # 36 method portfolio
_internal/state/_kakaotalk_narrative_method_table_20260510_0030.md  # narrative 정정 + 36 method table
_internal/state/_data_scope_decision_20260510_0114.md  # YFCC_PCA drop 결정 기록
_internal/state/_current.md _next.md _roadmap.md _artifacts.md _schedule.md  # 동적 state
_internal/handoff_v0_FINAL_SCOPE_20260510_0125.md  # ★ 본 handoff (v0 baseline)
_internal/handoff_v0_FINAL_SCOPE_20260510_0125.bak.md  # ★ 1차 작성본 backup (5/10 02:10)
_internal/archive/handoff_v0_to_v18/                # v13 ~ v18 archive
experiments/_DROPPED_README.md                      # 폐기 영역 documentation
```

### 7.4 SF=100 build pipeline (5/10 02:50 신규)

```
_internal/scripts/build_sf100_single.py            # SF=100 NPY/parquet build (각 80M rows)
_internal/scripts/launch_sf100_safe.sh             # safe launch (resource gate + watchdog handoff)
_internal/scripts/sf100_watchdog.sh                # auto-trigger (DEEP → SIFT → SSN sequential)
```

### 7.5 Dispatched agents (본 세션 trace)

| Agent | 시각 | 작업 | 결과 |
|---|---|---|---|
| 6 research agent (parallel) | 5/9 22:15 | 추가 method 발굴 | 10 new method 후보 보고 |
| 3 deep-review agent (parallel) | 5/10 01:15 | narrative fit + missed methods + Tier validation | reviewer attack 5 BLOCKING issue 식별 |
| Capstone directory cleanup agent | 5/10 01:55 | local repo audit | cleanup recommendation |
| LPM2 implementation agent | 5/10 01:00 | LPM2 (Grafström 2012) 코드 작성 | `methods/lpm2_strat.py` |
| SF=100 build pipeline agent | 5/10 02:50 | build_sf100_single.py + launch_sf100_safe.sh + sf100_watchdog.sh | 3 script 작성 + DEEP auto-trigger |
| FB → SSN doc rename agent | 5/10 02:20 | 6 Tier 1 doc 의 FB → SSN unified | doc rename 완료 |
| handoff v0 comprehensive update agent | 5/10 04:26 | 본 doc 의 comprehensive 통합 update | (현재 진행 中) |

---

## 8. Next session pickup instructions (구체적 작업 순서)

### Step 1 — 진입 즉시 (5분)

```bash
# 1.1 서버 측정 status 점검
ssh capstone "ps -ef | grep -E '(measure_multi|build_sf100)' | grep -v grep"
ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/sf100/ 2>/dev/null"

# 1.2 진행 PID 확인 (예상: SF=100 build PID 2608633 + 측정 procs 3 ~ 5)
ssh capstone "cat /tmp/sf100_*.flag 2>/dev/null"  # build flag 점검

# 1.3 RAM/swap status
ssh capstone "free -h"
```

### Step 2 — Phase G analysis launch (5/10 09:00 ~)

```bash
# 2.1 cache/rq3 모든 measurement 회수 + parquet → CSV pivot
cd /Users/hyunbin/Capstone
python3 _internal/scripts/analyze_phase_g.py --mode v9 --output experiments/results/phase_g/

# 2.2 결과 확인
ls -la experiments/results/phase_g/ experiments/figures/phase_g/
```

### Step 3 — Server-side FB → SSN rename batch (측정 완료 후, 5/10 06:00 ~ 07:00)

```bash
# 3.1 측정 완전 종료 확인 (필수)
ssh capstone "ps -ef | grep -E '(measure_multi|build_sf100)' | grep -v grep | wc -l"
# = 0 이어야 안전

# 3.2 NPY/parquet rename
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  for f in $(find . -name 'partsupp_fb_*' -o -name 'multi_join_fb_*'); do \
    mv \"\$f\" \"\${f//_fb_/_ssn_}\"; \
  done"

# 3.3 Python script rename
ssh capstone "cd /mnt/hdd0/home/capstone2026/scripts && \
  mv build_FB_single_ensemble.py build_SSN_single_ensemble.py && \
  sed -i 's/FB/SSN/g; s/fb_/ssn_/g' build_SSN_single_ensemble.py"

# 3.4 Local-side measure_multi_paradigm.py CELL key + analyze_phase_g.py METHOD_MAP rename
cd /Users/hyunbin/Capstone
sed -i '' 's/_fb_/_ssn_/g' _internal/scripts/measure_multi_paradigm.py _internal/scripts/analyze_phase_g.py
```

### Step 4 — Reviewer attack defenses (5/10 오후)

```bash
# 4.1 Attack 1 — Algorithm 1 box (B1)
# Phase F B1 baseline narrative 에 의사코드 6 step + hyperparam 표 추가
# 위치: experiments/results/phase_f/REPORT.md §3.1

# 4.2 Attack 2 — BH-FDR (B4)
# analyze_phase_g.py 에 statsmodels.stats.multitest.multipletests 추가
# 추가 column: q_value (BH-FDR corrected)

# 4.3 Attack 3 — ESS instrumentation (B5)
# 모든 method 의 sample() return dict 에 ess_per_stratum field 추가
# 영향 범위: 36 methods 일괄 수정
```

### Step 5 — REPORT.md draft (5/10 정오 ~ 오후)

- 7-stage storyline (§2.3) 따라 작성
- Tier 별 best method 표 (T-S+, T-A, T-B, T-C)
- 36 method × 26 cell paired-better win rate matrix (heatmap)
- Reviewer attack defense status box

### Step 6 — 5/11 사용자 review 준비

- 보고서 §11 sampling-level contribution 작성 (Tier 별 narrative)
- 5/11 미팅 시 v0 baseline 확정 보고 (이 handoff 위치 안내)
- 5/15 ~ 5/20 박성원 멘토 발송용 자문 메일 v5 finalize

---

## 9. 5/10 finalize timeline (realistic ETA per phase)

| 시점 | 작업 | ETA | 의존 |
|---|---|---|---|
| **5/10 04:26 (현재)** | 본 handoff comprehensive update 작성 | (이 작업) | — |
| **5/10 05:00** | SF=100 DEEP build 완료 → SIFT build 자동 시작 | watchdog | PID 2608633 완료 |
| **5/10 06:00** | sf=1 측정 자연 완료 (대부분) | — | 측정 procs |
| **5/10 06:30** | SF=100 SIFT build 완료 → SSN build 자동 시작 | watchdog | DEEP/SIFT 순차 |
| **5/10 07:00** | sf=10 측정 자연 완료 | — | 측정 procs |
| **5/10 07:00 ~ 08:00** | 사용자 깨어남 → 진행 status 보고 | — | 측정 완료 |
| **5/10 08:00 ~ 09:00** | Server-side FB → SSN rename batch | safe (측정 종료 후) | rename script |
| **5/10 09:00 ~ 12:00** | Phase G analysis (analyze_phase_g.py 실행) | analysis | rename 완료 |
| **5/10 12:00 ~ 14:00** | Reviewer attack defenses (B1, B4, B5) | doc + script | Phase G done |
| **5/10 12:00 ~ 18:00** | SF=100 측정 본격 launch (3 cells × 36 methods = 108 measurements) | parallel | SF=100 build done |
| **5/10 14:00 ~ 18:00** | REPORT.md draft + 보고서 §11 sampling-level contribution | writing | Phase G + defenses done |
| **5/10 20:00 이후** | 사용자 review → 5/11 미팅 준비 | — | — |

---

## 10. 정리

- **36 method × 26 cell + 3 SF=100 = 1,044 measurement** (이전 v9 56 cell × 36 method = 2,016 → ~48% slim)
- **두 트랙**: (1) §V-B augment (distribution-aware stratification) (2) §V-B 미확장 multi-table 직접 estimator
- **데이터셋**: Exqutor 100% 매치 5 (DEEP, SIFT, **SSN (SimSearchNet++)**, wiki, yfcc raw) + 1 join partner (partsupp)
- **HNSW-SS dropped**: narrative 위반 (vector index 사용) → LPM2 (Grafström 2012) 로 대체
- **YFCC_PCA dropped**: 우리 5/7 임의 추가, Exqutor 미수록 → 48 file 격리
- **image+image / wiki self-join dropped**: Exqutor Fig 8/9 scope 외 → 52 file 격리
- **SSN unified naming**: 모든 문서·발표·논문은 **SSN (SimSearchNet++)** 통일 표기. 서버 측 `fb_*` 파일명은 5/10 morning batch rename 예정 (코드 alias)
- **🎉 SF=100 적재 완료 발견 (5/10 02:35)**: 채림님이 우리 PG (port 55435) 안에 `partsupp_{deep,sift,fb}_100` (각 80M rows + HNSW) 적재. 채림님 카톡 회피, 즉시 활용 가능. SF=100 build pipeline (`build_sf100_single.py` + `launch_sf100_safe.sh` + `sf100_watchdog.sh`) 작성 → DEEP build 진행 중 (PID 2608633).
- **7+ PIDs cleanup**: NeurAM zombie + YFCC_PCA 3 + image+image 2 + sf=10 stuck 2 = 7 procs killed, RAM ~250+ GB / swap ~50+ GB 회복
- **Reviewer attack 5 BLOCKING**: Algorithm 1 box (B1) + BH-FDR (B4) + ESS instrumentation (B5) + 저-selectivity (M2) + curse of dim (M3) → 5/10 오후 작업 예정
- **5/10 finalize 목표**: 측정 + Phase G + REPORT.md draft + reviewer defenses 완료 → 5/11 사용자 review

---

## END

**핵심 메시지 (사용자 5/10 00:30 + 01:00 + 01:25 + 02:35 결정 종합)**:
- HNSW-SS dropped (narrative 위반), LPM2 추가 → 36 methods
- YFCC_PCA + image+image + wiki self-join dropped (Exqutor scope 외) → 26 cells
- SF=100 = Exqutor Fig 4-6 매치 3 cells 만, **이미 적재됨** (채림님 SF=100 80M 적재 발견 → build pipeline 진행 中)
- SSN (SimSearchNet++) unified naming — 문서 전체 통일, 서버 `fb_*` 파일명은 5/10 morning batch rename 예정
- 이전 handoff v13 ~ v18 archived → v0 baseline 으로 reset 완료
- Reviewer attack 5 BLOCKING (B1/B4/B5/M2/M3) → 5/10 오후 defense 작업

**다음 세션 첫 task**: §8 Step 1 진입 즉시 (5분) → 측정 status + SF=100 build status 점검.

문의: 조현빈 (wh8502@yonsei.ac.kr)
작성: 2026-05-10 01:25 KST (1차) → 2026-05-10 04:26 KST (comprehensive update, 본 세션 6.5h 통합 반영)
백업: `_internal/handoff_v0_FINAL_SCOPE_20260510_0125.bak.md` (1차 작성본)

---

# 부록 A — 5/10 04:30 ~ 10:27 KST 진행 (이전 세션 마무리)

## 추가 결정 + 액션

### 5/10 04:30 — Coverage gap analysis 결과
- **301 (cell, method) tuples gap** identified
- Method 검증 23/23 stratifiers correct (cc_sketch shim 만 data-blind 디자인 결정 필요)
- handoff_v0 1차본 → 2차본 (679 lines)

### 5/10 04:32 — Launch A: 19 methods × 6 NEW Exqutor sf=1 cells
- PID 3824288 — 5h 측정 → **09:30 COMPLETE**
- 114 measurements 완료 (sift/fb/yfcc partsupp+multi_join × 11 baseline + 9 v8a)
- `multi_paradigm_v9_baseline_sf1/`: 12 files (6 cells × 2 = csv + meta)

### 5/10 02:00-09:00 (자는 사이) — SF=100 자동 진행
- SF=100 watchdog (PID 1809876) 가 swap 80% 아래 도달 시 자동 launch
- DEEP NPY (30 GB) + SIFT NPY (40 GB) build 완료
- DEEP × hdbscan + SIFT × hdbscan SF=100 measurement 시작

### 5/10 10:21 — v9 Exqutor LPM2 stuck → kill + re-launch
- **PID 1792330 KILL**: 7h+ stuck on LPM2 strat (cell 1 8 methods data 손실)
- **PID 1256993 v9 Exqutor v2**: 8 methods × 8 cells (LpBound/MFMC/Tucker/VineCopula/HKBU/LHS/kDPP/OPQ), LPM2 제외
- ETA: ~6h → ~16:00 KST 완료

### 5/10 10:21 — SF=100 DEEP/SIFT × 10 remaining methods launch
- PID 1257191: DEEP × {minibatch, gmm, hilbert, faiss_ivf, mb_partial, reservoir, sparse_rp, pca1d, lsh, sobol} sequential
- PID 1257260: SIFT × 같은 10 methods sequential
- ETA: ~5h each → ~15:00 KST 완료
- FB SF=100 build (PID 1093694) 끝나면 FB measurement 별도 launch 필요

## 현재 active procs (5/10 10:27)

| PID | Cells/Methods | Status |
|---|---|---|
| 1256993 | v9 Exqutor v2 (8 methods × 8 cells) | LpBound 진행 |
| 459603 | DEEP × hdbscan SF=100 | ensemble 진행 |
| 1093689 | SIFT × hdbscan SF=100 | ensemble 진행 |
| 1093694 | FB build SF=100 | build 진행 |
| 1257189/91 | DEEP × 10 remaining methods (bash loop) | minibatch 시작 |
| 1257258/60 | SIFT × 10 remaining methods (bash loop) | minibatch 시작 |
| 17376 | sf=10 multi_join_fb_wiki_10 × 21 methods | HDBSCAN strat |
| 1012194 | sf=10 multi_join_yfcc_wiki_10 × 21 | HDBSCAN strat |
| 3760331 | sf=10 multi_join_sift_wiki_10 × 21 | HDBSCAN strat |
| 1439265 | sf=10 partsupp_fb_wiki_10 × 21 | HDBSCAN strat |
| 807789 | NeurAM/NeuroCard torch_existing | 진행 중 |
| 2060507 | multi_ensemble | 진행 중 |
| 1809876 | sf100_watchdog | idle (background) |

**총 13 procs running**. RAM 451 GB used, free 61 GB, available 536 GB, swap 48%.

## 5/10 finalize ETA (수정)

| 시점 | 예상 |
|---|---|
| ~12:00 | v9 Exqutor cells 1-2 완료 + SF=100 일부 완료 |
| ~14:00 | FB SF=100 build 완료 → FB × 11 methods launch |
| ~16:00 | v9 Exqutor v2 완료 + SF=100 DEEP/SIFT 다수 완료 |
| ~18:00 | SF=100 모두 완료 (FB 포함) + sf=10 다수 완료 |
| ~19:00 | Phase G analysis + REPORT.md 시작 |
| **5/10 저녁 (~22:00)** | **finalize 가능** |

## 다음 세션 진입 명령

```bash
# 1. 진입 시 first action
cd /Users/hyunbin/Capstone
git pull --no-rebase origin main

# 2. handoff_v0 읽기
cat _internal/handoff_v0_FINAL_SCOPE_20260510_0125.md | less

# 3. server status check
ssh capstone "free -h && uptime && pgrep -af 'python3.*(measure_multi|run_ensemble|build_sf100)' | grep -v grep | wc -l"

# 4. CSV 진행도 check
ssh capstone "for d in multi_paradigm_v9_exqutor_sf1 multi_paradigm_v9_baseline_sf1 multi_paradigm_v8_existing_sf1 multi_paradigm_torch_existing multi_paradigm_new10 multi_paradigm_new_sf10 phase_f_v2_full multi_ensemble; do n=\$(ls /mnt/hdd0/home/capstone2026/cache/rq3/\$d/ 2>/dev/null | wc -l); echo \"\$d: \$n files\"; done && echo '---SF=100---' && ls /mnt/hdd0/home/capstone2026/cache/rq1/rq3_*sf100*ensemble*.parquet 2>/dev/null | wc -l && echo 'SF=100 parquets'"

# 5. SF=100 FB build 완료 시 FB measurement launch (수동)
ssh capstone "ls -la /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_fb_100_vectors.npy && cd /mnt/hdd0/home/capstone2026/cache/rq3 && nohup bash -c 'for m in hdbscan minibatch gmm hilbert faiss_ivf mb_partial reservoir sparse_rp pca1d lsh sobol; do python3 -u run_ensemble_4kang_adaptive.py --dataset SSN --sf 100 --base-method \$m --selectivity 0.01 0.05 0.10 0.30 0.50 --seed-start 0 --num-seeds 5 --num-queries 100 --out-dir /mnt/hdd0/home/capstone2026/cache/rq1 --out-prefix rq3_FB_sf100_ensemble_\$m --momentum 0.9 --lr0 0.1 --alpha 50.0 --beta 1.5 --gamma 0.99 --update-period 50 --min-size 50 --max-size 5000; done' > /mnt/hdd0/home/capstone2026/log/sf100_FB_full_\$(date +%H%M).log 2>&1 & echo \$!"

# 6. 모든 측정 끝난 후 Phase G analysis
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 analyze_phase_g.py --methods-version v9 > /mnt/hdd0/home/capstone2026/log/phase_g_\$(date +%H%M).log 2>&1"
```

## 다음 세션 우선 작업

1. **server status check** — 13 procs 진행도 확인
2. **FB SF=100 build 완료 확인** → FB × 11 methods measurement launch (수동)
3. **CSV count check** — 모든 측정 완료 여부
4. **Phase G analysis 실행** — analyze_phase_g.py v9
5. **REPORT.md 생성**
6. **Reviewer attack defenses** (Algorithm 1 box, BH-FDR, ESS instrumentation)
7. **server-side FB → SSN rename** (모든 측정 끝난 후 batch)
8. **5/10 저녁 finalize → 사용자 보고**

## 이번 세션 핵심 결정 (forever rules)

- ✅ **36 methods** (HNSW-SS dropped, LPM2 added) — 단, LPM2 는 multi-table 에서 stuck 문제 → defer 또는 별도 config
- ✅ **26 cells (Exqutor 100% match) + 3 SF=100 = 29 cells**
- ✅ **5 datasets**: DEEP, SIFT, **FB(=SSN)**, YFCC, WIKI
- ✅ **Drop 정책**: HNSW-SS (vector index), YFCC_PCA (우리 추가), image+image partsupp 4-way (Exqutor 안 함), multi_join_wiki self-join (Exqutor 안 함)
- ✅ **FB = SSN dual naming** — server file rename 은 모든 측정 끝난 후 batch
- ✅ **cc_sketch.stratify_method data-blind** = 의도적 baseline (epsilon_net 처럼) 으로 결정 권고

## END (5/10 10:27 KST)

**Session context**: 이전 세션 (5/9 22:00 ~ 5/10 10:27, 12.5 시간) 의 모든 결정 + 변경 사항 + 진행 중인 작업 baseline.

**Next session pickup**: §0 timeline → §3 server state → §8 next-session pickup → 부록 A 진행 상황 → 우선 작업 1-8.

---

# 부록 B — 5/10 12:09 KST 세션 마무리 (현재 시점)

## 🎉 완료된 측정 (총 ~290 measurements)

| 측정 | Files | Status |
|---|---|---|
| **v9 Exqutor v2** (8 v9 methods × 8 Exqutor sf=1 cells) | 16 files | ✅ COMPLETE |
| **Launch A** (19 methods × 6 NEW cells, sift/fb/yfcc partsupp+multi_join) | 12 files | ✅ COMPLETE (5/10 09:30) |
| **Phase F v2 sf=1** (B1-B6 × 8 cells) | 16 files | ✅ COMPLETE |
| **SF=100 DEEP × 10 methods** (minibatch~sobol) | 10 parquets | ✅ COMPLETE (11:36) |
| **SF=100 SIFT × 10 methods** (minibatch~sobol) | 10 parquets | ✅ COMPLETE (12:05) |
| v8 5 methods × 9 sf=1 cells | 18 files | partial (40%) |
| multi_paradigm_torch_existing (NeurAM/NeuroCard) | 6 files | partial |
| multi_ensemble | 24 files | partial |
| phase_f legacy | 41 files | done |

## 🔄 진행 중 (5/10 12:25 시점)

| PID | 작업 | ETA |
|---|---|---|
| **2437227** | FB SF=100 build retry | ~70 min |
| **2437402** | SF=100 DEEP × hdbscan retry (with absolute path) | ~3h |
| **2437519** | SF=100 SIFT × hdbscan retry | ~3h |
| **17376, 1012194, 3760331, 1439265** + new 1471*** | sf=10 4 multi cells × 20 methods (WanderJoin 단계) | ~5-10h |

## ⚠️ 중요 fix 들 (이번 세션)

1. **PID 1093694 FB build 4시간 0% CPU stuck** → KILL + retry (PID 2437227)
2. **SF=100 DEEP/SIFT × hdbscan 누락** → re-launch (PID 2437402, 2437519, absolute path 사용)
3. **PID 1792330 v9 Exqutor LPM2 7h+ stuck** → KILL + v9 v2 launch (LPM2 제외, 8 methods × 8 cells COMPLETE)
4. **2 sf=10 stuck procs (HDBSCAN strat 3h+)** → KILL → memory 회복

## 📋 다음 세션 우선 작업 (Step-by-step)

### Step 1 — 진입 즉시 (5min)
```bash
cd /Users/hyunbin/Capstone
ssh capstone "free -h && pgrep -af 'python3.*(measure_multi|run_ensemble|build_sf100)' | grep -v grep | wc -l"
ssh capstone "for d in multi_paradigm_v9_exqutor_sf1 multi_paradigm_v9_baseline_sf1 phase_f_v2_full multi_paradigm_new_sf10; do n=\$(ls /mnt/hdd0/home/capstone2026/cache/rq3/\$d/ 2>/dev/null | wc -l); echo \"\$d: \$n\"; done && ls /mnt/hdd0/home/capstone2026/cache/rq1/rq3_*sf100*ensemble*.parquet 2>/dev/null | wc -l && echo 'SF=100 parquets'"
```

### Step 2 — FB build 완료 시 FB × 11 methods launch
```bash
ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_fb_100_vectors.npy 2>/dev/null && cd /mnt/hdd0/home/capstone2026/cache/rq3 && nohup bash -c 'for m in hdbscan minibatch gmm hilbert faiss_ivf mb_partial reservoir sparse_rp pca1d lsh sobol; do python3 -u /mnt/hdd0/home/capstone2026/cache/rq3/run_ensemble_4kang_adaptive.py --dataset SSN --sf 100 --base-method \$m --selectivity 0.01 0.05 0.10 0.30 0.50 --seed-start 0 --num-seeds 5 --num-queries 100 --out-dir /mnt/hdd0/home/capstone2026/cache/rq1 --out-prefix rq3_FB_sf100_ensemble_\$m --momentum 0.9 --lr0 0.1 --alpha 50.0 --beta 1.5 --gamma 0.99 --update-period 50 --min-size 50 --max-size 5000; done' > /mnt/hdd0/home/capstone2026/log/sf100_FB_full_\$(date +%H%M).log 2>&1 & echo \$!"
```

### Step 3 — Phase G analysis (대부분 측정 완료 시)
```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u analyze_phase_g.py --methods-version v9 > /mnt/hdd0/home/capstone2026/log/phase_g_\$(date +%H%M).log 2>&1"
```

### Step 4 — REPORT.md draft + Reviewer defenses (Phase G 끝난 후)
- Algorithm 1 box (B1)
- BH-FDR 재분석 (B4)
- ESS instrumentation (B5)

### Step 5 — Server-side FB → SSN rename batch (모든 측정 완전 종료 후)

## 5/10 22:00 finalize 가능성

**Realistic ETA**:
- 14:00: FB SF=100 build 완료 → FB × 11 methods launch
- 16:00: SF=100 DEEP/SIFT hdbscan 완료 + sf=10 일부
- 18:00: SF=100 FB × 11 methods 절반
- 20:00: 모든 SF=100 + sf=10 완료
- 21:00: Phase G analysis
- **22:00 ~ 24:00**: REPORT.md draft + reviewer defenses 가능

## 핵심 메시지 (다음 세션)

✅ **이번 세션의 큰 win**:
1. 36 method × 26 cells + 3 SF=100 = 1,044 measurement scope 확정
2. ~290 measurements 완료 (28% 진행도)
3. SF=100 적재 발견 + 자동 build pipeline
4. 7+ stuck procs cleanup (RAM 250+ GB 회복)
5. handoff_v0 baseline doc (790+ lines)
6. Narrative 정정 (Exqutor §V-B verbatim)
7. SSN unified naming + YFCC_PCA + image+image + wiki self-join drop

⚠️ **다음 세션 critical**:
- FB SF=100 build 진행도 모니터링 (4h stuck 재발 방지)
- sf=10 measurements 자연 완료 wait
- Phase G analysis launch (analyze_phase_g.py v9)
- REPORT.md + reviewer defenses

## END (5/10 12:25 KST)

**Total session duration**: 5/9 22:00 ~ 5/10 12:25 = **14.4시간**
**handoff_v0 final size**: 800+ lines (5/10 01:25 1차 + 04:26 2차 + 10:27 3차 + 12:25 4차 부록)
**Next session entry prompt**: 부록 B Step 1-5 따라 진행
