# 총 정리 — 5/10 12:15 KST 시점 측정 진행 상태 + Gap 식별

> 사용자 요청 (5/10 12:15): "지금 세션 여러개 겹쳐서 진행하다보니까 작업들이 꼬인 게 되게 많고 ... 한 번 총 정리를 하고 가보자". 본 doc 는 최신 측정 진행도 + 누락 작업 명확화.
>
> **Framing 결정 (5/10 12:04)**: Replacement (Exqutor §V-B 자체를 36 alternative samplings 으로 교체). REPORT.md §1, §2, §5, §6, §7, §8.3 정정 완료.

---

## 1. 용어 정리 (Forever Dictionary)

### 1.1 Method portfolio version 표기 (시간순)
| 표기 | 의미 | 시점 |
|---|---|---|
| **v1** = Legacy | HDBSCAN, MiniBatch, GMM, Hilbert, faiss_ivf, MB_partial, Reservoir, sparse_rp, PCA1D, LSH, Sobol — 11 methods | W1 sprint (4월말) |
| **v7** | Legacy 11 + 11 new (5/9 first wave) — Tier S+ 3 + Tier A 5 + Tier B 2 + Tier C 1 | 5/9 새벽 |
| **v8** | v7 + 5 new (5/9 dispatch wave) — ThompsonSampling, EpsilonNetBaseline, AdaptiveBucketProbing, CCSketch, FactorJoin | 5/9 22:30 |
| **v9** | v8 + 9 new (5/9 23:35 extreme mode) — LpBound, MFMC, Tucker, VineCopula, HNSW_SS, HKBU_RepSample, LHS, kDPP, OPQ | 5/9 23:35 |
| **v0 (current)** | v9 - HNSW_SS (dropped narrative violation) + LPM2 (5/10 v0 added) = **36 methods** | 5/10 01:25 baseline |

### 1.2 Wave / Stage / Phase 표기
| 표기 | 의미 |
|---|---|
| **Wave 0** | Legacy 11 methods 측정 단계 (W1 sprint) |
| **Wave 1** | v7 11 new methods 측정 단계 (5/9 새벽) |
| **Stage A** | sf=1, sf=10 main measurement (Phase G analysis 대상) |
| **Stage B** | SF=100 reproducibility measurement |
| **Phase F** | Adaptive sampling baseline 측정 (B1~B6, 6 baselines) |
| **Phase F v2** | Phase F 재측정 (5/9 18:46 backup pre v2 → 19:46 v2 launch) |
| **Phase G** | Method matrix 분석 (analyze_phase_g.py) |

### 1.3 Cell 종류 표기 (Forever)
| 표기 | 의미 | 개수 |
|---|---|---|
| **Single** | Single-table (DEEP/SIFT/SSN/YFCC/WIKI 단일 vector column) | 10 = 5 datasets × 2 sf |
| **Multi 4-way** | partsupp 4-way table (partsupp_X_wiki_sf) — image emb1 + WIKI text emb2 | 8 = 4 datasets × 2 sf |
| **Multi-join** | multi_join_X_wiki_sf — partsupp[image] ⋈ part[wiki text] | 8 = 4 datasets × 2 sf |
| **SF=100 single** | partsupp_X_100 (partsupp deep/sift/ssn 80M, single-table) | 3 datasets |

### 1.4 Baseline 표기 (Phase F)
| 표기 | 의미 | 비교 의미 |
|---|---|---|
| **B1** | **Adaptive sampling = Exqutor §V-B vanilla** (uniform Bernoulli + momentum size adaptation) | **★ 우리 비교 base — replacement framing 의 reference** |
| B2 | BERN N=385 fixed | secondary baseline |
| B3 | Fixed-K=20 | secondary baseline |
| B4 | Adaptive + ensemble (augment) | augment framing baseline (5/10 강등) |
| B5 | Uniform random matched | secondary baseline |
| B6 | Oracle KM20 | upper bound (production X) |

### 1.5 Replacement framing 표기 (5/10 12:04 결정)
- **B1** = Exqutor §V-B vanilla (replacement target)
- **B_alt** = 36 alternative samplings (each method standalone)
- 비교 = direct paired Δ% (q_error_method vs q_error_B1) on same (cell, sel, seed, query)
- B4 (augment) = §5.4 sanity check 영역으로 강등

---

## 2. Dataset × Size 분류 (29 cells × 36 methods = 1,044 measurements ideal)

### 2.1 Datasets (5 vector + 1 join partner)
| # | Dataset | dim | Exqutor §VI | 코드 alias | NPY 위치 |
|---|---|---|---|---|---|
| 1 | DEEP | 96 | DEEP1B | `deep` | partsupp_deep_*.npy |
| 2 | SIFT | 128 | SIFT1B | `sift` | partsupp_sift_*.npy |
| 3 | **SSN** (SimSearchNet++) | 256 | SimSearchNet++ | `fb` (5/10 dual naming) | partsupp_fb_*.npy |
| 4 | YFCC | 192 | YFCC100M | `yfcc` | partsupp_yfcc_*.npy |
| 5 | WIKI | 768 | Wikipedia | `wiki` | (text emb, join partner) |
| 6 | partsupp | TPC-H | (간접) | `partsupp` | (relational join partner) |

### 2.2 Sizes (sf scale factor)
| sf | rows | NPY size 추정 |
|---|---|---|
| sf=1 | 800K rows | ~3 GB per dim 96 |
| sf=10 | 8M rows | ~30 GB per dim 96 |
| sf=100 | 80M rows | ~80 GB per dim 256 |

### 2.3 Cell scope (29 cells = 26 Exqutor 매치 + 3 SF=100)

**Single (10 cells)**: DEEP/SIFT/SSN/YFCC/WIKI × {sf=1, sf=10} — currently single_ensemble/ **빈 directory** (단일 테이블 측정 진행 X)

**Multi 4-way (8 cells, Exqutor Fig 8 image+text only)**:
| Cell | partsupp[image] | + WIKI[text] | sf | 측정 dir |
|---|---|---|---|---|
| `partsupp_deep_wiki_1` | DEEP 96d | WIKI 768d | 1 | multi_paradigm_*, v9_exqutor_sf1 |
| `partsupp_sift_wiki_1` | SIFT 128d | WIKI 768d | 1 | 같음 |
| `partsupp_fb_wiki_1` | SSN 256d | WIKI 768d | 1 | 같음 |
| `partsupp_yfcc_wiki_1` | YFCC 192d | WIKI 768d | 1 | 같음 |
| `partsupp_deep_wiki_10` | DEEP 96d | WIKI 768d | 10 | multi_paradigm_new_sf10 (**미측정**) |
| `partsupp_sift_wiki_10` | SIFT 128d | WIKI 768d | 10 | (**미측정**) |
| `partsupp_fb_wiki_10` | SSN 256d | WIKI 768d | 10 | new_sf10 (진행 中, PID 1471933) |
| `partsupp_yfcc_wiki_10` | YFCC 192d | WIKI 768d | 10 | (**미측정**) |

**Multi-join (8 cells, Exqutor Fig 9 image⋈text only)**:
| Cell | partsupp[image] | ⋈ part[WIKI] | sf | 측정 dir |
|---|---|---|---|---|
| `multi_join_deep_wiki_1` | DEEP | WIKI | 1 | multi_paradigm_*, v9_exqutor_sf1 |
| `multi_join_sift_wiki_1` | SIFT | WIKI | 1 | 같음 |
| `multi_join_fb_wiki_1` | SSN | WIKI | 1 | 같음 |
| `multi_join_yfcc_wiki_1` | YFCC | WIKI | 1 | 같음 |
| `multi_join_deep_wiki_10` | DEEP | WIKI | 10 | (**미측정**) |
| `multi_join_sift_wiki_10` | SIFT | WIKI | 10 | new_sf10 진행 中 (PID 1471540) |
| `multi_join_fb_wiki_10` | SSN | WIKI | 10 | new_sf10 진행 中 (PID 1471673) |
| `multi_join_yfcc_wiki_10` | YFCC | WIKI | 10 | new_sf10 진행 中 (PID 1471803) |

**SF=100 single (3 cells, Exqutor Fig 4-6 reproducibility)**:
| Cell | dataset | dim | sf | NPY status |
|---|---|---|---|---|
| `partsupp_deep_100` | DEEP | 96 | 100 | NPY 30 GB ✅ |
| `partsupp_sift_100` | SIFT | 128 | 100 | NPY 41 GB ✅ |
| `partsupp_fb_100` (= SSN) | SSN | 256 | 100 | NPY 81 GB ✅ (5/10 03:12 build 완료) |

---

## 3. Methods (36 portfolio, Tier 분류)

### 3.1 Tier 1 Legacy Paradigm Baseline (11)
P1 Cluster: HDBSCAN, MiniBatch, GMM
P2 Spatial: Hilbert, faiss_ivf
P3 Streaming: MB_partial, Reservoir
P4 DimReduction: sparse_rp, PCA1D
P5 QuasiRandom: LSH, Sobol

### 3.2 Tier S+ Direct Estimator (7)
WanderJoin, AMSCountSketch, NeuroCard-lite, AdaptiveBucketProbing, CCSketch, FactorJoin, **LpBound** (SIGMOD'25 Best Paper)

### 3.3 Tier A Stratification Primitives (10)
PQ, Coreset, DenseRP, BanditUCB1, NeurAM, ThompsonSampling, MFMC, EpsilonNetBaseline, kDPP, OPQ

### 3.4 Tier B Joint Distribution + Sample Design (7)
CCA1D, CoCluster_Nystrom, Tucker, VineCopula, **HKBU_RepSample** (SIGMOD'26), LHS, LPM2

### 3.5 Tier C Single AS variant (1)
ConditionalAdaptive (Exqutor §V-B variant)

### 3.6 Dropped (1)
~~HNSW-SS~~ — narrative violation (vector index 사용)

---

## 4. Coverage matrix — 측정 진행 상태 (5/10 12:15 KST 시점)

### 4.1 Sf=1 multi-table (16 cells × 36 methods = 576 measurements ideal)

| Method 그룹 | 파일 | 진행 상태 |
|---|---|---|
| Legacy 11 × 16 cells | multi_paradigm/, multi_ensemble/, v9_baseline/ | ~~~~ ✅ 거의 완료 |
| Tier S+ 7 × 16 cells | v8_existing/, v9_baseline/ (일부) + v9_exqutor (LpBound 8 cells) | partial |
| Tier A 10 × 16 cells | v8_existing/, torch_existing/ (NeurAM 등 일부) | partial |
| Tier B 7 × 16 cells | v9_exqutor (Tucker/VineCopula/LHS/kDPP/OPQ 8 cells) + v9_exqutor_hkbu (HKBU 진행 中) + LPM2 (?) | 거의 완료 |
| Tier C 1 × 16 cells | v9_baseline (ConditionalAdaptive 부분) | partial |

→ **sf=1 multi-table = 12:30 finalize 가능** (HKBU 8 procs 12:17~20 끝나면).

### 4.2 Sf=10 multi-table (16 cells × 35 methods = 560 measurements ideal)

| Cell | 측정 dir | 진행 상태 |
|---|---|---|
| `multi_join_sift_wiki_10` | new_sf10 PID 1471540 | 🔄 진행 中 (HDBSCAN 1h09m) |
| `multi_join_fb_wiki_10` | new_sf10 PID 1471673 | 🔄 진행 中 |
| `multi_join_yfcc_wiki_10` | new_sf10 PID 1471803 | 🔄 진행 中 |
| `partsupp_fb_wiki_10` | new_sf10 PID 1471933 | 🔄 진행 中 |
| **`multi_join_deep_wiki_10`** | (없음) | ❌ **미측정** |
| **`partsupp_deep_wiki_10`** | (없음) | ❌ **미측정** |
| **`partsupp_sift_wiki_10`** | (없음) | ❌ **미측정** |
| **`partsupp_yfcc_wiki_10`** | (없음) | ❌ **미측정** |

→ **sf=10 큰 gap**: 16 cells 중 4 cells 만 진행 중. **12 cells 미측정** (multi_join_deep_wiki_10 + partsupp_deep/sift/yfcc_wiki_10 = 4 + handoff에 있어야 할 다른 cells 8).

실제로 정리해보면 Multi-join sf=10에서 deep 빠지고, multi 4-way sf=10에서 fb만 진행. 사용자가 "1, 10 빨리 완결" 의도면 **multi-join_deep_wiki_10 + partsupp_{deep,sift,yfcc}_wiki_10 추가 launch 필요**.

### 4.3 SF=100 single (3 cells × 36 methods = 108 measurements ideal — 사용자 5/10 12:15 결정 "전체 비교")

| Dataset | Legacy 11 진행 | Tier S+/A/B/C 25 |
|---|---|---|
| DEEP | 10/11 (hdbscan PID 2437402 진행 中, 다른 method 모두 완료) | ❌ 미측정 (script 확장 필요) |
| SIFT | 10/11 (hdbscan PID 2437519 진행 中) | ❌ 미측정 |
| FB (=SSN) | 0/11 (FB NPY build 끝났으나 measurement auto-launch 실패) | ❌ 미측정 |

→ SF=100 큰 gap: **30 method × 3 datasets = 90 measurements 미측정 + FB Legacy 10 measurements 미측정 = 100 measurements 누락**

### 4.4 Phase F baselines (Phase F + Phase F v2 → 6 baselines × 16+ cells)

| dir | files | 의미 |
|---|---|---|
| phase_f | 40 (= 20 cells × 2) | Phase F v1 (이전 측정, supersedeed) |
| phase_f_backup_pre_v2_1550 | 36 (= 18 cells × 2) | Phase F v2 직전 backup |
| phase_f_v2_full | 16 (= 8 cells × 2) | Phase F v2 (5/9 18:46~19:46 완료) |

→ Phase F v2 = sf=1 8 cells × 6 baselines (B1~B6) ✅ 완료. **sf=10 baseline 측정 미완**.

---

## 5. 진행 중 procs (5/10 12:15 시점, 17 procs total)

| PID | 측정 | dir | 시작 | 진행 |
|---|---|---|---|---|
| 1093694 | SF=100 FB build | logs/build_sf100_FB | 5/9 21:41 | NPY done 03:12, watchdog idle |
| 1471540 | sf=10 multi_join_sift_wiki_10 × 20 methods | new_sf10 | 11:01 | HDBSCAN strat 1h09m |
| 1471673 | sf=10 multi_join_fb_wiki_10 | new_sf10 | 11:01 | HDBSCAN |
| 1471803 | sf=10 multi_join_yfcc_wiki_10 | new_sf10 | 11:01 | HDBSCAN |
| 1471933 | sf=10 partsupp_fb_wiki_10 | new_sf10 | 11:01 | HDBSCAN |
| 1809876 | sf100_watchdog (idle, FB measure auto-launch chain 끊김) | (background) | 5/9 17:04 | idle |
| 2437402 | SF=100 DEEP × hdbscan (재 launch) | rq1/ | ~02:25 | fit+assign |
| 2437519 | SF=100 SIFT × hdbscan (재 launch) | rq1/ | ~02:25 | fit+assign |
| 2449902 ~ 2450820 (8 procs) | HKBU 8 cells parallel sf=1 | v9_exqutor_sf1_hkbu | 12:13 | 4분, fit_cap 30K |

→ **17 procs running**. RAM 598 GB free, swap 95% (위험).

---

## 6. 누락 작업 (Gap List, 5/10 finalize 위한 우선순위)

### 6.1 Critical Gap (sf=1, sf=10 main)

1. **sf=10 multi_join_deep_wiki_10** 미측정 — 즉시 launch 필요 (4 cells 진행 중과 같이)
2. **sf=10 partsupp_{deep,sift,yfcc}_wiki_10** 미측정 — 3 cells 즉시 launch 필요
3. **HKBU 8 procs (sf=1)** 마무리 — ~5분 더, 12:20 finalize
4. **Phase F sf=10 baselines** 미측정? — phase_f_v2_full 가 sf=1 only (8 cells). sf=10 baseline 필요 시 추가 측정

### 6.2 High Priority (SF=100 user 결정 "전체 비교")

5. **SF=100 FB Legacy 11 measurement 수동 launch** — 자동 launch chain 끊김
6. **SF=100 DEEP/SIFT 마지막 hdbscan** — 진행 중 (PIDs 2437402, 2437519, ~2:25h elapsed). 만약 stuck이면 kill (이전 hdbscan 6h+ stuck 사례)
7. **SF=100 Tier S+/A/B/C 25 methods 측정** — `run_ensemble_4kang_adaptive.py` method registry 확장 필요 (1h)

### 6.3 Analysis & Report

8. analyze_phase_g.py v9 실행 (sf=1/10 finalize 후)
9. REPORT.md fill (Stage A + Stage B 통합)
10. B5 ESS instrumentation (post-finalize)
11. WanderJoin FAISS replacement fix (post-finalize)
12. Server-side FB → SSN rename batch (post-finalize)

---

## 7. 5/10 finalize 갱신 timeline

| 시각 | 작업 |
|---|---|
| 12:20 | HKBU 8 procs finalize → **sf=1 완전 finalize** (12 sub-dirs, ~140 measurements) |
| 12:25 | sf=10 추가 4 cells launch (multi_join_deep + partsupp_{deep,sift,yfcc}_wiki_10) — 8 cells parallel |
| 12:30 | SF=100 FB Legacy 11 measurement 수동 launch (10 methods, hdbscan 제외 — 이미 stuck 위험) |
| 13:00 | run_ensemble_4kang_adaptive.py method registry 확장 (Tier S+/A/B/C 25 methods 추가) |
| 14:00 | SF=100 25 methods × 3 datasets parallel launch |
| 16:00 | sf=10 8 cells finalize (예상) |
| 17:00 | SF=100 25 methods 부분 finalize |
| 17:30 | Stage A analysis (sf=1/10 36 methods × 16 cells paired vs B1) |
| 19:00 | SF=100 finalize |
| 19:30 | Stage A+B analysis 통합 |
| 22:00 | REPORT.md fill + 5/10 finalize |

---

## 8. END

작성: 2026-05-10 12:15 KST
다음 단계: 사용자 confirm 후 sf=10 추가 4 cells launch + SF=100 FB measurement launch + run_ensemble_4kang_adaptive.py 확장.
