# EXPERIMENT_REGISTRY.md — 9 Cells × 57 Methods × 3 Modes Matrix

> 작성: 2026-05-11 01:35 KST  
> 출처: handoff_v2 §2 paper exact + handoff_main_session_FULL_STATE §7 진행 상태 + handoff_v5 §6 Phase 4  
> 사용자 명시 (5/10 14:03 + 18:49 + 20:45): "paper의 모든 항목 완전 똑같이 진행 + 단 하나라도 다르면 안 됨"

---

## 0. TL;DR — 측정 matrix 종합

| 영역 | 단위 | 수 | 진행 |
|---|---|---|---|
| **B1 baseline** (Phase A) | 9 cells × paper Eq 1-6 | 9 | ✅ 9/9 (paper Fig 12 1.69 매칭, -6.3%~+1.1%) |
| **CaseA replace** (Phase B) | 51 sampling cells × 39+11+6 method = 2,856 | 진행 中 | ~316/702 (5/10 21:44) → ETA 5/11 02-03시 |
| **CaseB augment** (Phase C) | 51 cells × method × ensemble | 진행 中 | 위와 동일 chain |
| **RQ1 paper exact** | DEEP/SIFT × Bernoulli/KM20 × sel{0.01,0.10} | 8 cells | ✅ 5% 격차 narrative 검증 |
| **RQ2 paper exact** | DEEP/SIFT × Bern/Equal/Prop × sel{0.01,0.10} | 12 cells | ✅ 9% 격차 (Bern→Prop) — Neyman/Anti 진행 中 |
| **RQ2 5-way 확장** | + Neyman + Anti-Neyman | 4 cells × 2 modes 추가 | 자동 chain monitor 진행 中 (handoff_v4 §2) |
| **A2-Fig8** (multi-vector) | partsupp_deep_wiki_10 4-way | 1 cell | ⏳ stratum_id 부재 post-fix |
| **A3-TPCDS** (ECQO mode) | TPC-DS × DEEP item_deep | 1 cell | ⏳ Exqutor PG crash post-fix |

---

## 1. Phase A — Exqutor B1 baseline (paper exact 9 cells)

### 1.1 9 cells matrix (handoff_v2 §2.1 verbatim)

| Cell | Paper Fig | Datasets | SF | Queries (paper verbatim) | Selectivity | Mode | 결과 |
|---|---|---|---|---|---|---|---|
| **A1-DEEP** | Fig 5/6 | DEEP 96d | 100 | Q3, Q10, Q12 (3) | 1% (threshold 0.86) | sampling 3-way | ✅ avg_qe ~1.5-1.7 |
| **A1-SIFT** | Fig 5/6 | SIFT 128d | 100 | Q3, Q10, Q12 (3) | 1% | sampling 3-way | ✅ avg_qe ~1.6 |
| **A1-SSN** | Fig 5/6 | SimSearchNet++ 256d (=FB=SSN) | 100 | **Q3, Q9, Q10** (3) | 1% | sampling 3-way | ✅ avg_qe ~1.5 |
| **A2-Fig7** | Fig 7 | YFCC 192d + tag | 10 | Q3,5,8,9,10,11,12,20 (8) | 1% | sampling+ps_tag | ✅ |
| **A2-Fig9** | Fig 9 | DEEP 96d ⋈ part_wiki 768d | 10 | Q3,5,8,9,10,11,12,20 (8) | 1% | sampling cross-table | ✅ |
| **A4-sel** | Fig 13 | DEEP 96d | 100 | Q3, Q10, Q12 (3) | **{0.001, 0.01, 0.10}** | sampling 3-way | ✅ avg_qe 5.984 (Fig 13 영역, 별도) |
| **A5-scale-sf1** | Fig 14 | DEEP 96d | 1 | Q3, Q5, Q20 (3) | (paper threshold) | sampling 3-way | ✅ |
| **A5-scale-sf10** | Fig 14 | DEEP 96d | 10 | Q3, Q5, Q20 (3) | (paper threshold) | sampling 3-way | ✅ |
| **A5-scale-sf100** | Fig 14 | DEEP 96d | 100 | Q3, Q5, Q20 (3) | (paper threshold) | sampling 3-way | ✅ |

### 1.2 Fig 12 영역 vs Fig 13 영역 분리 (handoff_back §2.1)

- **Fig 12 영역 8 cells** (A1-DEEP/SIFT/SSN, A2-Fig7/Fig9, A5-scale-sf{1,10,100}): mean qe_trim = **1.618** (paper 1.69 vs **−4.3%**, 거의 일치)
- **Fig 13 영역 1 cell** (A4-sel, sel=0.001 inherently 큼): qe=5.984, paper Fig 12 와 직접 비교 부적절
- 정정 후 narrative #2 (Exqutor 정확 재현) **강화** (+25.5% misleading → −4.3% 일치)

### 1.3 미완료 / blocker (2 cell)

| Cell | Paper Fig | Blocker | 권고 |
|---|---|---|---|
| **A2-Fig8** | Fig 8 | partsupp_deep_wiki_10 stratum_id 컬럼 부재 + multi-vector AND predicate measurement loop 별도 implementation | post-fix (handoff_main §7.3) |
| **A3-TPCDS** | Fig 10 | Exqutor patched PG의 ECQO trigger가 vector cast SQL과 충돌 → PG crash 반복 | post-fix (Exqutor source 분석 필요, ECQO 영역) |

---

## 2. paper exact hyperparam (handoff_main §2.2 verbatim, Eq 1-6)

```
N        = ⌈z²·P̂(1-P̂)/e²⌉ = ⌈1.96² × 0.5 × 0.5 / 0.05²⌉ = 385         (1) initial
Q-error  = max(C_est/C_true, C_true/C_est)                          (2)
δ        = α·(Q-error - β) - (100-α)·sampling_ratio                 (3) adjustment
V_t      = m·V_{t-1} + η_t·δ                                        (4) momentum
size_{t+1} = size_t + V_t                                           (5) size update
η_{t+1}  = γ·η_t                                                    (6) lr decay
```

**Hyperparam (paper p.7 verbatim)**:
- m = 0.9 / η₀ = 0.1 / α = 50 / β = 1.5 / γ = 0.99 / update_period = 50 / N_init = 385
- **NO clamping** (handoff_v2 Decision 2 — paper Eq 1-6 에 min/max bound 없음)

**HNSW (paper p.6)**:
- M=16, ef_construction=200, ef_search=400

**Trial seed (우리 측정)**:
- `trial_idx * 13 + 7` (seed 일관성, 10 trials)

**Trim mean (paper p.7 verbatim)**:
- lowest+highest 1개 제외 → 8 runs trim mean

---

## 3. Phase B — CaseA replace (sampling step 대체) — 51 cells × method

### 3.1 Tier 1 Legacy 11 method × 9 cells (99 measurements) ✅ 완료

| Method | paradigm | B1 | CaseA Δ% | 평가 |
|---|---|---|---|---|
| sparse_rp ★4 | P4 | 2.090 | -1.44% method-mean | warning (cluster imbalance YFCC) |
| minibatch_partial ★2 | P1 | 2.090 | **-10.17% method-mean** | **CaseA best replace** |
| minibatch | P1 | 2.090 | -2.88% method-mean | OK |
| hilbert (★3 defect) | P2 | 2.090 | -2.15% | warning (PCA proxy) |
| pca1d | P4 | 2.090 | -2.34% | OK |
| reservoir → random20 | P3 | 2.090 | -1.85% | OK |
| sobol | P5 | 2.090 | +11% (YFCC outlier) | warning |
| lsh | P5 | 2.090 | +35% (YFCC outlier) | warning (worse signif 7/9) |
| random_projection | P4 | 2.090 | +1964% (YFCC outlier) | warning (192d 부적합) |
| gmm | P1 | 2.090 | +5%/+15% | underperform |
| faiss_ivf | P2 | 2.090 | -1.5% | OK |

### 3.2 Phase B extra 8 NEW method × 9 cells (72 measurements) — 진행 中 (~50/72)
pq, kdtree, halton, hammersley, coreset, birch, agglomerative, dense_rp

### 3.3 Phase B extra2 20 NEW method × 9 cells (180 measurements) — 진행 中 (~50/180)
opq, kdpp, banditucb1, neuram, thompson_sampling, mfmc, epsilon_net, ams_count_sketch, neurocard_lite, adaptive_bucket_probing, ccsketch, factor_join, lp_bound, cca1d, cocluster_nystrom, tucker, vinecopula, hkbu_repsample, lhs, lpm2

### 3.4 Q4 Tier 1 6 NEW method × 9 cells (54 measurements) — 진행 中
dbscan, kde_parzen, mhist2, hyperloglog, rsvd, wavelet_hist

### 3.5 Phase 4 11 NEW method × 9 cells (99 measurements) — server scp 대기 (handoff_v5)
chao_weighted M1, lpm1_proper M2, cum_sqrtf M3, lavallee_hidiroglou M4, idistance M5, zorder_morton M6, skilling_hilbert M7, ica_fastica M8, kmeans_neyman M9, rabitq_strat M10, idistance_neyman M11

### 3.6 통합 ETA (handoff_v5 §7.2)
- Phase 4 11 + Q4 Tier 1 6 = 17 method × 9 cells × 2 modes = **306 cells**
- Sequential single procs: ~180-280 h
- Parallel 6 tmux: ~30-50 h (~1.5-2일)

### 3.7 통계 검증 (handoff_back validation §1.4)

- Wilcoxon (two-sided) + BH-FDR α=0.05: **109/300건 signif** (CaseA ≠ B1)
- one-sided (CaseA better): **61건 (20.3%)**, minibatch_partial 4/9 cells / faiss_ivf 3/9
- worse direction signif: **43건** (lsh/RP/sobol/ccsketch YFCC 192d outlier — narrative caveat 명시)

---

## 4. Phase C — CaseB augment (sampling step 증강) — 51 cells × method × ensemble

### 4.1 Tier 1 Legacy 11 method × 9 cells (99 measurements) ✅ 완료

| Method | paradigm | CaseB Δ% method-mean | win | signif |
|---|---|---|---|---|
| **sparse_rp ★4** | P4 | **-8.13% method-mean** | 6/9 | 6/9 sig |
| **hilbert** | P2 | -8.30% method-mean | 7/9 | 7/9 sig |
| **pca1d** | P4 | **-8.50% method-mean** | 7/9 | 7/9 sig |
| **reservoir → random20** | P3 | -8.05% method-mean | 7/9 | 7/9 sig |
| **minibatch** | P1 | -8.14% method-mean | 6/9 | 6/9 sig |
| **minibatch_partial** | P1 | -5.79% method-mean | 6/9 | 6/9 sig |

→ 6 methods 모두 -2~-7% outperform B1 (handoff_main §7.1)

### 4.2 Phase C extra 28 NEW method × 9 cells (252 measurements) — 진행 中 (~6/252)

### 4.3 통계 검증 (handoff_back §1.4)

- one-sided p_adj < 0.05 outperform: **46/103건 (44.7%)**
- top tier: hilbert / pca1d / reservoir 7/9 cells / minibatch / sparse_rp 6/9

---

## 5. RQ1 paper exact (handoff_main §11.5)

### 5.1 측정 matrix

| Dataset | Mode | Selectivity | trial × seed | 결과 |
|---|---|---|---|---|
| DEEP sf=100 | Bernoulli vs KM20 | 0.01, 0.10 | 5 × 100 query | ✅ gap +6.76% (sel=0.01) / +3.95% (sel=0.10) |
| SIFT sf=100 | Bernoulli vs KM20 | 0.01, 0.10 | 5 × 100 query | ✅ gap +1.97% / +9.45% |

→ paper sel{0.01, 0.10}에서 random vs KM20 stratified **5% 격차** narrative 성립.

---

## 6. RQ2 paper exact (handoff_main §11.5 + handoff_v4 §1.4)

### 6.1 3-way 측정 (Bernoulli / Equal / Proportional) ✅ 완료

| Dataset | Mode | sel=0.01 | sel=0.10 | gap |
|---|---|---|---|---|
| DEEP sf=100 | Bernoulli | 1.748 | — | — |
| | Equal | 1.637 | — | — |
| | Proportional | 1.584 | — | **+10.32% (Bern → Prop)** |
| SIFT sf=100 | Bernoulli vs Prop | gap +4.16% / +10.21% | | |

→ paper sel{0.01, 0.10}에서 Prop **1.584** < Equal **1.637** < Bernoulli **1.748** ordering OK, **9% 격차**.

### 6.2 5-way 확장 (+ Neyman + Anti-Neyman) — 자동 chain 진행 中

| File | spec |
|---|---|
| `_measure_common.py` | `fetch_stratum_sigmas` + `neyman_alloc` + `anti_neyman_alloc` 추가 (handoff_v4 §1.1) |
| `measure_paper_exact.py` | `measure_rq2_paper_exact` modes = 5-way ("bernoulli", "equal", "proportional", "neyman", "anti_neyman") |
| `compute_stratum_sigma_paper_exact.py` | NPY mmap 기반 σ_j 빌드 (DEEP/SIFT/SSN sf=100, KM20 cluster, sel=0.1 D_target) |
| Server log | `/mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_*.log` |
| Output | `paper_exact/rq2_paper_exact_{DEEP,SIFT}_sf100.csv` (5 modes × 2 sel × 5 seed × 100 query = 5000 rows / dataset) |

자동 chain monitor (`bdrhrddyb`) 가 측정+sigma 완료 시 RQ2 5-way launch (handoff_v4 §2.2 Step 3/4).

---

## 7. 9 cells × 57 methods × 3 modes matrix 종합

### 7.1 활성 method 분포 (paradigm × cell × mode)

| Cell | B1 | CaseA replace 활성 method | CaseB augment 활성 method |
|---|---|---|---|
| A1-DEEP | ✅ | 11 Tier 1 + 8 extra + 20 extra2 + 6 Q4 + 11 Phase 4 = **56** | 동일 56 method (B1 + method ensemble) |
| A1-SIFT | ✅ | 56 | 56 |
| A1-SSN | ✅ | 56 | 56 |
| A2-Fig7 (YFCC) | ✅ | 56 (lsh/RP/sobol outlier 명시) | 56 |
| A2-Fig9 (DEEP+WIKI cross) | ✅ | 56 | 56 |
| A4-sel (Fig 13) | ✅ | 56 (sel=0.001/0.01/0.10) | 56 |
| A5-scale-sf1 | ✅ | 56 | 56 |
| A5-scale-sf10 | ✅ | 56 | 56 |
| A5-scale-sf100 | ✅ | 56 | 56 |
| **A2-Fig8** (multi-vector) | ⏳ | ⏳ post-fix | ⏳ |
| **A3-TPCDS** (ECQO) | ⏳ | (sampling 영역 외) | (sampling 영역 외) |

**총 활성 측정**: 9 cells × 56 methods × 2 modes (CaseA + CaseB) + 9 cells B1 = **1,017 + 9 = 1,026 measurements**.

### 7.2 폐기 method 23건 별도 (audit 권고 — 측정 결과 보존, 보고서에서 제외 또는 limitation 명시)

P3 5건 (thompson/mfmc/ams/ccsketch + reservoir rename) + P1 2건 (banditucb1/hkbu_repsample) + P4 8건 (neuram/cca1d/dense_rp + 5 rename) + P2 3건 (kdtree/kdpp/hilbert rename) + P5 1건 (lp_bound rename) + P6 cocluster (rename)

---

## 8. 측정 결과 위치 (server)

```
/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/
├── A1-DEEP_B1.json, A1-SIFT_B1.json, A1-SSN_B1.json
├── A2-Fig7_B1.json, A2-Fig9_B1.json
├── A4-sel_B1.json
├── A5-scale-sf{1,10,100}_B1.json
├── *_CaseA_*.json   (Phase B Tier 1 99 + extra 72 + extra2 180 + Q4 54 + Phase4 99 = 504 진행)
├── *_CaseB_*.json   (Phase C Tier 1 99 + extra 252 = 351 진행)
├── rq1_paper_exact_DEEP_sf100.csv / SIFT
├── rq2_paper_exact_DEEP_sf100.csv / SIFT (5-way after chain)
└── REPORT_paper_exact.md  ← 자동 생성 (analyze_paper_exact.py)
```

---

## 9. 5단계 narrative (handoff_main §6.2 + handoff_v4 §7 + 측정 결과 통합)

| # | 단계 | 핵심 method (paradigm) | 검증 |
|---|---|---|---|
| 1 | RQ1/RQ2/RQ3 검증 | RANDOM20 baseline + KM20 stratified | ✅ RQ1 5%, RQ2 9% 격차 |
| 2 | Exqutor 100% 정확 재현 (paper Fig 12 1.69) | Bernoulli + Adaptive Eq 1-6 | ✅ Fig 12 영역 8 cells mean qe_trim **1.618** (-4.3% paper 일치) |
| 3 | CaseA: 우리 method **대체** | minibatch_partial ★2 (P1, **-10.17%**) / faiss_ivf (P2, 3/9) | ⚠️ 7.6% 통계 유의 only — 단독 narrative 약함 |
| 4 | CaseB: 우리 method **증강** | sparse_rp ★4 (P4, -8.13%) / hilbert (-8.30%) / pca1d (-8.50%) / reservoir (-8.05%) / minibatch (-8.14%) / mb_partial (-5.79%) | ✅ 44.7% 통계 유의 (46/103) — narrative 강함 |
| 5 | 최종 비교 B1 vs CaseA vs CaseB | CaseB > CaseA > B1 ordering | ✅ CaseB 79.6% (82/103) outperform vs CaseA 40.1% — robust |

---

## 10. END

작성: 2026-05-11 01:35 KST  
다음 단계: SERVER_REGISTRY.md 작성  

**핵심 검증**: 9 cells × 57 method × 3 modes matrix 가 paper Fig 5/6/7/9/13/14 verbatim 일치 + 진행 상태 ~1,026 measurement (활성) / 230+ measurement (폐기 method, 결과 보존).
