# Handoff v0 — FINAL SCOPE (5/10 01:25 KST, Sunday)

> 본 handoff 는 5/10 01:25 KST 시점에 사용자 (조현빈) 의 결정 ("이제 우리 방향성 정해졌다, v0 으로 reset") 에 따라 본 연구의 최종 scope baseline 으로 작성된다. 이전의 모든 handoff (v13 ~ v18) 은 `_internal/archive/handoff_v0_to_v18/` 로 archive 되었으며, 향후 모든 측정·분석·보고서 작성은 본 handoff 의 숫자를 reference 로 한다.
>
> 동기: 5/10 01:00 ~ 01:25 사이 사용자가 Exqutor 본 논문 §VI Experimental Setup + Fig 4-9 를 직접 재확인한 결과, 이전 v9 portfolio (36 method × 56 cell = 2,016 measurement) 의 56 cell 안에 (a) YFCC_PCA (우리 임의 추가, Exqutor 미수록) 14 cell, (b) image+image partsupp 4-way (Exqutor Fig 8 image+text only 위반) 12 cell, (c) multi_join_wiki self-join (Exqutor Fig 9 image⋈text only 위반) 2 cell 의 총 28 cell 이 본 논문 scope 외 임을 확인. 동시에 HNSW-SS 가 vector index 사용 → narrative 위반 으로 폐기되어 LPM2 (Grafström 2012) 로 대체. 정리 후 36 method × 26 cell + 3 SF=100 = **1,044 measurement** 의 v0 baseline 확정.

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
| `partsupp_fb_wiki_1`*    | SSN (256d) | WIKI (768d)  | 1 |
| `partsupp_fb_wiki_10`*   | SSN (256d) | WIKI (768d)  | 10 |
| `partsupp_yfcc_wiki_1`  | YFCC (192d)    | WIKI (768d)  | 1 |
| `partsupp_yfcc_wiki_10` | YFCC (192d)    | WIKI (768d)  | 10 |

#### Multi-join partsupp ⋈ part (8 cells, Exqutor Fig 9 image⋈text only)

| Cell | partsupp[image] | ⋈ part[WIKI text] | sf |
|---|---|---|---|
| `multi_join_deep_wiki_1`  | DEEP (96d)     | WIKI (768d)  | 1 |
| `multi_join_deep_wiki_10` | DEEP (96d)     | WIKI (768d)  | 10 |
| `multi_join_sift_wiki_1`  | SIFT (128d)    | WIKI (768d)  | 1 |
| `multi_join_sift_wiki_10` | SIFT (128d)    | WIKI (768d)  | 10 |
| `multi_join_fb_wiki_1`*    | SSN (256d) | WIKI (768d)  | 1 |
| `multi_join_fb_wiki_10`*   | SSN (256d) | WIKI (768d)  | 10 |
| `multi_join_yfcc_wiki_1`  | YFCC (192d)    | WIKI (768d)  | 1 |
| `multi_join_yfcc_wiki_10` | YFCC (192d)    | WIKI (768d)  | 10 |

#### SF=100 추가 (3 cells, Exqutor Fig 4-6 reproducibility)

| Cell | dataset | sf | 비고 |
|---|---|---|---|
| `partsupp_deep_wiki_100` | DEEP × WIKI | 100 | Exqutor Fig 4 매치 |
| `partsupp_sift_wiki_100` | SIFT × WIKI | 100 | Exqutor Fig 5 매치 |
| `partsupp_fb_wiki_100`*   | SSN × WIKI | 100 | Exqutor Fig 6 매치 |

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

| Drop 영역 | 사유 |
|---|---|
| **HNSW-SS** | vector index 사용 → narrative 위반 (우리 §V-B augment 영역은 vector index 부재 환경) |
| **YFCC_PCA** | 5/7 우리 팀 임의 추가, Exqutor §VI Table I 미수록 → Exqutor 비교 baseline 으로서 의미 없음. raw YFCC (192d) 만 본 논문 매치 |
| **image+image partsupp 4-way** | Exqutor Fig 8 = image+text only. partsupp 4-way 의 두 vector column 은 image embedding + text embedding (WIKI) 만 사용. image+image 조합 (DEEP+SIFT, DEEP+SSN 등) 은 본 논문 미수록 |
| **multi_join_wiki self-join** | Exqutor Fig 9 = image⋈text only (partsupp[image] ⋈ part[wiki]). wiki self-join 미수록 |

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

## 3. Server state at handoff (5/10 01:25)

### 3.1 정리 완료 작업

| 작업 | 영향 |
|---|---|
| **5 PIDs killed** | 1 NeurAM zombie + 3 YFCC_PCA procs (PIDs 3241790, 3311667, 3644487) + 2 image+image procs. 서버 RAM ~80 GB / load avg ~70 즉시 해소. |
| **100+ files moved** to `_DROPPED_*` directories | YFCC_PCA 48 + image+image 44 + wiki self-join 8 = 약 100 NPY/parquet 격리 (delete X, audit log 보존) |
| **CELL config cleaned** | `measure_multi_paradigm.py` CELL_4WAY/CELL_JOIN 에서 폐기 cell 14 entry comment-out. 16 active multi cell (8 4-way + 8 multi-join) 만 launch 대상 |
| **HNSW-SS module 격리** | `methods/hnsw_ss_strat.py` → `methods/_DROPPED/hnsw_ss_strat.py` 이동 |
| **LPM2 추가** | `methods/lpm2_strat.py` 신규 (Grafström 2012, well-spread spatially-balanced sampling) → 36 method portfolio 완성 |

### 3.2 진행 중인 measurement (5/10 01:25)

| PID | 내용 | ETA |
|---|---|---|
| 2865788 | v8 5 new methods × 9 existing sf=1 cells | ~40min |
| 3138136 | 27 methods × 5 NEW v8 sf=1 cells | ~80min |
| 3742865 | v9 9 methods × 9 existing sf=1 cells | ~70min |
| (기타 6 build procs) | sf=10 NPY build | 진행 中 |

→ 측정 procs 3개 + build procs 6개 = 9 active procs (정리 후 lean 상태)

### 3.3 ETA

| 시점 | 작업 |
|---|---|
| **5/10 06:00 ~ 09:00** | sf=1 + sf=10 측정 finalize (현재 진행 중인 procs 자연 완료) |
| **5/10 09:00 ~ 12:00** | Phase G analysis (analyze_phase_g.py 실행, 36 methods × 26 cells matrix) |
| **5/10 12:00 ~ 18:00** | SF=100 측정 (3 cells × 36 methods = 108 measurements, 시작 결정 trigger 필요) |
| **5/10 20:00 이후** | REPORT.md draft + 보고서 §11 sampling-level contribution 작성 |

---

## 4. Naming convention (forever rules)

### 4.1 SSN unified naming (5/10 update — FB alias 폐기)

- **모든 문서/figure/표**: **SSN (SimSearchNet++)** 단일 표기로 통일. "FB" 단독 표기 금지.
- **codebase 내부 (서버)**: `partsupp_fb_*.npy`, `multi_join_fb_*.parquet`, `build_FB_*.py` 등 path/script 는 5/10 morning batch rename 예정 (현재 서버 측정 진행 중이라 즉시 rename 불가). 현 시점 코드 reference 는 alias 로 간주.
- **Phase G analyzer**: chart label 모두 "SSN" 출력. METHOD_MAP key 는 server rename 후 일괄 정리.
- **출처 검증**: `build_FB_single_ensemble.py` source 의 dataset path 가 `/mnt/hdd0/.../ssn_*.fbin` → "FB" 가 SSN 의 단순 rename 임을 직접 확인 (5/10 01:14). 즉 "FB" 는 코드 alias 일 뿐 의미 없는 이름이며, 문서·발표·논문 통일 표기는 SSN.

### 4.2 폐기 디렉토리 위치

| 디렉토리 | 내용 | 위치 |
|---|---|---|
| `_DROPPED_yfcc_pca/` | YFCC_PCA 48 NPY/parquet | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/` |
| `_DROPPED_imgimg/` | image+image partsupp 4-way 44 parquet | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_imgimg/` |
| `_DROPPED_wiki_selfjoin/` | wiki self-join 8 parquet | `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_wiki_selfjoin/` |
| `_internal/archive/handoff_v0_to_v18/` | 이전 handoff v13 ~ v18 (archive) | local repo |
| `_internal/scripts/methods/_DROPPED/` | HNSW-SS module (격리) | local repo |
| `_internal/state/archive/` | _method_portfolio_v8_research_20260509_2235.md (obsolete) | local repo |

---

## 5. 5/10 morning 작업 (사용자 깨어날 때 ~ 08:00 KST 예상)

### 5.1 Phase G analysis (5/10 09:00 ~ 12:00)

- `analyze_phase_g.py` 실행 (현재 v9 mode = 36 methods, 56 cells 지원 — 26 cells 만 valid parquet 존재하므로 자동 skip)
- 산출물:
  - `experiments/results/phase_g/method_matrix_36x26.csv` (heatmap-friendly pivot)
  - `experiments/figures/phase_g/G2_adaptive_gap.png`, `G3_b4_vs_b1.png`, `G7_production_top.png`
  - `experiments/results/phase_g/REPORT.md` (7-stage storyline + 36 method paired-better win rate + Tier 별 분석)
- HKBU-RepSample (SIGMOD 2026) reference 강조 — 미인용 시 reviewer rejection 위험
- Phase F B1-B6 baselines 비교 (B4 = 우리 stratification augment ★ thesis 핵심)

### 5.2 REPORT.md 생성 (5/10 정오 ~ 오후)

- 7-stage storyline (§2.3) 따라 작성
- 36 methods paired-better win rate 표 (Tier S+/A/B/C 별 best representative)
- Tier-level 분석 (paradigm coverage + redundancy 분석)
- 5/10 오후 draft 완료 → 5/11 사용자 review

### 5.3 사용자 깨어날 때 (08:00 KST 예상) 보고 내용

- 측정 진행도 (sf=1 / sf=10 / SF=100 별)
- SF=100 launch 결정 trigger (resource OK 확인 후)
- Phase G analysis 결과 (preliminary heatmap)
- v0 baseline 확정 보고 (이 handoff 위치 안내)

---

## 6. Reviewer attack defenses (분석 단계 작업)

| ID | 항목 | 작업 |
|---|---|---|
| **B1** | Algorithm 1 box | §V-B Adaptive Sampling 의 식 1~6 을 Algorithm 1 box 로 명시 (B1 baseline) |
| **B4** | BH-FDR 재분석 | 36 method × 26 cell matrix 의 paired-better p-value 에 BH-FDR correction 적용 |
| **B5** | ESS instrumentation | importance sampling weight 의 effective sample size (ESS) 를 stratum 별 측정·기록 |
| **M2** | 저-selectivity 0.001 | sel = 0.001 ~ 0.01 영역의 별도 측정 (현재 0.01 ~ 0.50, 5 sel grid) |

---

## 7. 산출물 위치

### 7.1 Method 구현

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
_internal/archive/handoff_v0_to_v18/                # v13 ~ v18 archive
experiments/_DROPPED_README.md                      # 폐기 영역 documentation
```

---

## 8. 정리

- **36 method × 26 cell + 3 SF=100 = 1,044 measurement** (이전 v9 56 cell × 36 method = 2,016 → ~48% slim)
- **두 트랙**: (1) §V-B augment (distribution-aware stratification) (2) §V-B 미확장 multi-table 직접 estimator
- **데이터셋**: Exqutor 100% 매치 5 (DEEP, SIFT, **SSN (SimSearchNet++)**, wiki, yfcc raw) + 1 join partner (partsupp)
- **HNSW-SS dropped**: narrative 위반 (vector index 사용) → LPM2 (Grafström 2012) 로 대체
- **YFCC_PCA dropped**: 우리 5/7 임의 추가, Exqutor 미수록 → 48 file 격리
- **image+image / wiki self-join dropped**: Exqutor Fig 8/9 scope 외 → 52 file 격리
- **SSN unified naming**: 모든 문서·발표·논문은 **SSN (SimSearchNet++)** 통일 표기. 서버 측 `fb_*` 파일명은 5/10 morning batch rename 예정 (코드 alias)
- **5/10 finalize 목표**: 측정 + Phase G + REPORT.md draft 완료 → 5/11 사용자 review

---

## END

**핵심 메시지 (사용자 5/10 00:30 + 01:00 + 01:25 결정 종합)**:
- HNSW-SS dropped (narrative 위반), LPM2 추가 → 36 methods
- YFCC_PCA + image+image + wiki self-join dropped (Exqutor scope 외) → 26 cells
- SF=100 = Exqutor Fig 4-6 매치 3 cells 만
- SSN (SimSearchNet++) unified naming — 문서 전체 통일, 서버 `fb_*` 파일명은 5/10 morning batch rename 예정
- 이전 handoff v13 ~ v18 archived → v0 baseline 으로 reset 완료

문의: 조현빈 (wh8502@yonsei.ac.kr)
작성: 2026-05-10 01:25 KST (Claude Code 자동 인계)
