# Phase 2-1 — 다단계 필터 카테고리 brainstorming + threshold 정의

> 작성: 2026-05-11 00:55 KST (Phase 4 별도 세션)
> 목적: ~553 candidate (~470 신규) 를 거를 다단계 cascade 필터 설계
> 5/27 최종발표 + 6/11 최종보고서 narrative critical filter 5-7 selection

---

## 0. 필터 brainstorming 원칙

1. 각 필터는 **거를 사유** + **threshold** 명시
2. 사용자 명시 선호: "확실히 outperform 하는 method만, 0건 OK"
3. 메인 chain bvf1k64kw 진행 중 — 측정 launch는 메인 confirm 후 (Phase 3 산출물 준비만)
4. 각 필터의 **fail case 일반화** 명시 (이전 audit 결과를 generalize)

---

## 1. 필터 카테고리 (총 14개, 사용자 명시 10+ 충족)

### 필터 A — 시간 복잡도 (8M / 80M scale)

**거를 사유**: kdtree 22h+ stuck (handoff_main §10.1) / agglomerative full predict 12h / Floyd-Warshall O(N³) (Isomap 8M = 5e20 ops) / KDE full pairwise O(N²·D) = 8M² × 96 = 6e15 ops

**fail case 일반화**:
- O(N²) 이상 8M 에서 borderline ⚠, 80M 에서 ❌
- O(N³) 8M 에서 ❌, 80M ❌
- O(N·iter) iter > 50 borderline (8M × 50 = 4e8 fast OK)
- subset_training (sample 50K-200K → predict full chunk) 우회 가능 시 ⚠ → ✅

**threshold (8M @ ETA < 30 min × 1 cell × 10 trials × 100 queries)**:
- ✅ trivial: O(N·D) ≤ 1 GFLOP/sec → ETA < 1 min
- ⚠️ caution: O(N·D·K) ≤ 100 GFLOP → ETA 5-30 min
- ❌ infeasible: O(N²) 또는 O(N·D²) ≥ 1 TFLOP → ETA > 1h
- exception: subset_training (50K subsample fit + chunked predict) 가능 시 caution → ✅

**일반화 규칙 (모든 필터 cascade 적용)**:
- 8M / 80M 모두 ✅ 통과 시 → through
- 8M ✅ / 80M ⚠️ subset → through (ETA ~ 1.5x)
- 8M ⚠️ / 80M ❌ → drop
- 8M ❌ / 80M ❌ → drop

**예상 drop**: A20 two-phase (sub-step OK), A29 BLB OK (sub-bootstrap), A40 HMC ❌, A41 NUTS ❌, F1 KDE Parzen ⚠️ subset OK, F8 KDE-FFT ✅, G3 HOSVD ❌ (high-D), G14 LLE ❌, G17 Isomap ❌, J7 SBM ❌

### 필터 B — 공간 복잡도 (RAM 200-400 GB working memory)

**거를 사유**: HDBSCAN-old 8M+ OOM (handoff_main §12.1) / GMM full covariance cholesky fail / HDBSCAN connectivity matrix N²·8 bytes = 64M² × 8 = 4 EB / vinecopula rankdata 80M × 768d = 245GB

**fail case 일반화**:
- N×N matrix O(N² bytes) — 8M = 256TB ❌, 80M = 25.6 PB ❌ → 항상 drop unless subset
- N×K matrix O(N·K bytes) — 8M × 20 × 4 byte = 640MB ✅, 80M × 20 × 4 = 6.4GB ✅
- Rankdata on N × D — 80M × 768 × 8 = 491GB ❌, 80M × 96 × 8 = 61GB ⚠️ borderline
- HNSW graph 8M × 16 (M=16) = 128M neighbor records ≈ 4-8 GB ✅
- Sparse N×N (kNN graph k=50) — 8M × 50 = 400M edges × 8 byte = 3.2GB ✅

**threshold**:
- ✅ memory-safe: peak working set < 30 GB (server 20% headroom)
- ⚠️ caution: peak 30-200 GB (subset_training 또는 chunk pattern 검증 필요)
- ❌ OOM risk: peak > 200 GB (server other procs 침범)

**예상 drop**: G14 LLE ❌, G17 Isomap ❌, F1 KDE Parzen full ⚠️ subset OK, F2-F3 ⚠️ subset, J7 SBM ❌, A45 reversible jump ⚠️, F47 score matching ⚠️

### 필터 C — 차원 의존성 (96 / 128 / 192 / 256 / 768 dim)

**거를 사유**: 
- KDE high-d underflow (96-768d Gaussian kernel = exp(-||x||²/h²) → 0 for h moderate)
- LSH on YFCC 192d cluster imbalance (handoff_main §10.1, lsh/RP/sobol 7/9 worse signif)
- QMC sequence high-D degeneracy (Halton base-prime distribution > 8 dim 분포 깨짐)
- KD-tree dimensionality curse > 20 dim
- Faure sequence > 25 dim 약함
- Bengtsson 2008 high-D curse (WIKI 768d)

**fail case 일반화**:
- intrinsic_dim > 8 → space-filling curve (Hilbert/Z-order/Morton/Peano) 약함
- D > 25 → QMC sequence (Halton/Faure/Niederreiter) 약함
- D > 20 → KD-tree leaf 효과 ≈ random hash (kdtree defect 일반화)
- D > 50 → local neighborhood 기반 (LLE/Isomap/spectral) 약함 (curse of dimensionality)
- D > 100 → kernel methods (KDE/kPCA) bandwidth issue
- D > 500 → autoencoder/representation learning needed

**threshold (정의 = method가 dim ≤ X 에서 fit, X = ?)**:
- ✅ all 5 dataset (96/128/192/256/768): distribution-agnostic methods (RP/sketch family)
- ⚠️ ≥ 192d 약함: LSH/QMC sequence/SFC
- ❌ ≥ 100d 약함: KDE/Isomap/LLE/spectral

**dataset별 분류 (V_S → V_M → V_L)**:
- V_S: 96d (DEEP) — 모든 method OK
- V_M: 128d (SIFT) ~ 192d (YFCC) ~ 256d (SSN) — QMC/SFC 약함 시작
- V_L: 768d (WIKI) — kernel/density 약함 (intrinsic ~ 50-100)

**예상 drop**: K4 Faure (high-D 약), K9 lattice (low-D), K14 OA (low-D), E34 true Hilbert ⚠️ low-D, F1 KDE Parzen ⚠️ 768d underflow, G14 LLE ⚠️ high-D, F47 score matching, G17 Isomap

### 필터 D — Dataset 종류 부적합 (DEEP / SIFT / SSN / YFCC / WIKI)

**거를 사유**: 5 distribution category fit (handoff_v3 §3.3, sf_feasibility §4):
- A PCA-based: skew 강함, SSN uniform 약함
- B density: skew 강함, SSN 약함
- C QMC uniform: SSN 강함, skew 약함
- D agnostic: 모든 dataset baseline
- E VQ/centroid: skew strong, SSN moderate

**fail case 일반화**:
- Category C × {SIFT, YFCC} (skew dataset) → handoff_main §10.1 lsh/RP/sobol/ccsketch 43건 worse signif → narrative caveat 필요 OR drop
- Category A/B × SSN (uniform) → BERN ceiling으로 +0~+3% hurt → narrative caveat
- Category D 어디서나 baseline (negative control)

**threshold (5 dataset × method category → ≥ 3 dataset에서 strong fit 또는 neutral fit)**:
- ✅ pass: ≥ 3 dataset에서 ✓ 또는 ◎
- ⚠️ caveat: 1-2 dataset만 ✓ (narrative limitation 명시)
- ❌ drop: 모든 dataset에서 ✗ (학술 정당성 X)

**예상 drop**: 추가 QMC 변형 (K4 Faure, K9 lattice) — 본 5 dataset 중 SSN 1개만 fit. 추가 KDE 변형 (F1 KDE Parzen on WIKI 768d) ⚠️ caveat.

### 필터 E — 학술 정합 (Exqutor §V-B + 9 paradigm)

**거를 사유**: 본 연구 narrative anchor:
- Exqutor §V-B Eq 1-6 = unstratified Bernoulli sampling
- 우리 contribution = augment within §V-B (대체 X)
- 5 → 9 paradigm coverage (P1-P10, P11 future)
- ★ 4강 (HDBSCAN P1, MB_partial P3, Hilbert P2, sparse_rp P4) baseline

**fail case 일반화**:
- 본 연구 paradigm 9개 외 영역 → narrative 약함 (drop 또는 future work)
- ★ 4강과 직접 비교 불가 → drop
- Exqutor §V-B 와 plug-in 호환성 X (e.g. multi-table 만 가능) → drop

**threshold**:
- ✅ paradigm fit: 9 paradigm 중 1개 이상 매핑 가능 + ★ 4강과 비교 가능 + plug-in 가능
- ⚠️ paradigm anchor 역할: 신규 paradigm 의 representative (narrative 강화)
- ❌ scope outside: distributed only / multi-table only / RL-based optimizer

**예상 drop**: B12 Lero, B13 E2E learned, B27 RTOS, B29 Bao, B30 Balsa, B46 GaussDB-Vector (distributed), B16 DREAM (join only)

### 필터 F — Outperform 보장 (★ 4강 + B1 baseline 차별화)

**거를 사유**: 사용자 명시 "확실히 outperform 하는 method만". 이미 측정된 41 method 의 결과를 dist 분포로 사용:

```
CaseA Δ% 분포 (handoff_back §4.1):
- ≤ -20%: 7건 (3.6%) — extreme outperform
- -20~-10%: 17건 (8.6%)
- -10~-5%: 17건 (8.6%)
- -5~-1%: 25건 (12.7%)
- ≤ 0%: 79/197 (40.1%)

CaseB Δ% 분포:
- ≤ 0%: 82/103 (79.6%)
- one-sided signif outperform: 46/103 (44.7%)

★ 4강 cell-mean (handoff_back §4.2):
- minibatch_partial CaseA: -10.17%
- sparse_rp CaseB: -8.13%
- pca1d CaseB: -8.50%
- minibatch CaseB: -8.14%
- hilbert CaseB: -8.30%
- reservoir CaseB: -8.05%
```

**fail case 일반화**:
- random에 동등 효과 (예: random_projection ≡ dense_rp normalize 차이) → drop
- KM20 (RQ2 baseline) 보다 약함 (P1 cluster 영역) → narrative 약함
- B1 ensemble (CaseB) 보다 약함 (즉 method 자체 가치 없음) → drop
- 같은 paradigm 내 ★ 4강 보다 약함 → drop unless paradigm anchor

**threshold (preliminary mathematical reasoning, 측정 전 inductive bias 추정)**:
- ✅ ★ candidate: 추정 Δ% ≤ -5% (★ 4강 평균) 가능성 ≥ 50%
- ⚠️ moderate: -2% ≤ Δ% ≤ -5%
- ❌ weak: Δ% > -2% 추정 또는 ★ 4강 alias

**예상 통과**: paradigm anchor (P9 sketch baseline 강화 — HLL++/t-digest), P10 density (KDE+FFT/Sheather-Jones), 또는 신규 paradigm anchor (P7 PROCLUS)
**예상 drop**: PCA1D variants (cca1d/whiten 등 alias 류), QMC 변형 (overlap halton/sobol), LSH 변형 (overlap lsh)

### 필터 G — 알고리즘 정직성 (paper verbatim, 10 audit 폐기 패턴 일반화)

**거를 사유**: 5/10 audit 결과 30+ critical defect (handoff_v3 §1.1):
- 학술 reference fraud 15건 (hilbert/reservoir/lpm2/tucker/vinecopula/cca1d/neuram/lp_bound/neurocard_lite/factor_join)
- algorithm bug/leak 5건 (banditucb1/kde_pilot/pq/opq/cocluster_nystrom)
- redundancy/alias 10건 (kdpp≡epsilon_net/kdtree=random hash/hkbu≡coreset)

**fail case 일반화**:
- 학술 명칭 vs 실제 구현 mismatch → 즉시 drop or rename
- algorithm core 누락 (UCB1 미구현, Nyström 미구현, control variate 부재, codeword distance preserve X) → drop
- 직전 method와 line-by-line 동일 (kdpp ≡ epsilon_net) → drop
- alias / cosmetic difference only → drop

**threshold**:
- ✅ paper verbatim 구현 가능 (sklearn/scipy/library 사용 또는 직접 구현 < 200 line)
- ⚠️ paper 핵심 누락 risk → 폐기 OR 진짜 재구현 (5/10 audit Q2 예시: thompson/mfmc 폐기)
- ❌ paper와 무관 / line-by-line 중복

**예상 drop**: 추가 PCA-alias (CCA1D variants, whitened PCA), 추가 LSH-alias (SimHash), random_projection variants

### 필터 H — 구현 복잡도 (5/27 D-15 시간 budget)

**거를 사유**: 5/27 발표 D-day 까지 implementation + smoke + measurement 가능 시간:
- 1 method = ~200-500 line (registry 추가 + chunked predict 패턴)
- 5/12 ~ 5/14 launch (handoff_v3 §5 P2)
- ~30분 / cell smoke + 10-30분 / cell measurement
- 5/27 발표 D-15

**fail case 일반화**:
- training 필요 (deep learning method) → 5/27 까지 어려움 (PRICE는 pretrained 사용 가능)
- proprietary library 의존 → 사용 불가
- multi-component 시스템 (CluStream 의 micro+macro cluster, SBM) → 1주+ 구현
- GPU 필수 (autoencoder/diffusion) → 단계적 검증 필요

**threshold**:
- ✅ trivial: ~30-100 line (sklearn/scipy/datasketch direct call)
- ⚠️ medium: 100-300 line (custom chunked predict 또는 multi-step)
- ❌ heavy: > 500 line / 외부 library 의존 / training pipeline 필요

**예상 drop**: B1 NeuroCard (training pipeline), B5 FLAT (SPN training), B11 AutoCE (AutoML), B23 Diffusion CardEst, F43-F50 normalizing flows, J17-J19 graph NN, I17 DSC

### 필터 I — Redundancy (현재 46 method × 30+ defect 와 alias)

**거를 사유**: 현재 portfolio 와 본질 동일한 method (paper 다른 명칭이지만 알고리즘 동일):
- random_projection variants (dense_rp / random_projection / sparse_rp 이미 3개)
- LSH variants (lsh / SimHash / Hyperplane LSH 이미 본질 동일)
- KMeans variants (minibatch / minibatch_partial / coreset / hkbu_repsample 이미 4개)
- PCA variants (pca1d / cca1d / neuram / tucker / vinecopula 이미 5개 alias)
- QMC sequences (sobol / halton / hammersley / lhs 이미 4개)

**fail case 일반화**:
- 본질 동일 algorithm 의 cosmetic variant → drop
- normalization 차이만 (column unit norm vs 1/√k) → drop
- 같은 base + reg term 만 차이 → drop unless ablation narrative
- subset selection rule 차이 → drop

**threshold**:
- ✅ distinct: 현재 portfolio 46 method와 paradigm + algorithm core 모두 다름
- ⚠️ ablation: 같은 base + 1 axis 차이 (e.g. fast variant) → 명시적 ablation narrative만 있을 시
- ❌ alias: 본질 동일

**예상 drop**: L3 SimHash (== lsh), L13-L20 LSH variants 대부분 (overlap), C16-C32 IVF/PQ variants 대부분 (overlap pq/opq/faiss_ivf), G33 sparse_rp variants

### 필터 J — Vector DB 컨텍스트 (vector specific vs generic)

**거를 사유**: 본 연구 = vector-augmented analytical query (Exqutor). 단일 vector embedding column에 대한 cardinality estimation. ANN search 자체 (HNSW retrieval) 와 구별:
- vector-specific = embedding 분포에 직접 작용
- generic tabular = scalar value statistics (PG analyze 류)

**fail case 일반화**:
- scalar/tabular only (e.g. PG analyze MCV) → vector embedding 적용 위해 변환 필요 (PCA1D 후 scalar → 이미 portfolio)
- ANN search algorithm only (HNSW build) → cardinality estimator 가 아님
- Multi-table only (FactorJoin proper) → 본 연구 single-table scope 외
- RL-based optimizer / plan tree → 본 연구 sampling stage 외

**threshold**:
- ✅ vector-native: high-D vector embedding 직접 처리
- ⚠️ adaptable: scalar method지만 PCA1D 등으로 변환 가능
- ❌ scope outside: tabular only / RL-based / multi-table only

**예상 drop**: B12 Lero, B13 E2E, B16 DREAM (join only), B20 BoundSketch (join only), B21 SafeBound (join), B27-B30 RL optimizers, B46 GaussDB-Vector (distributed)

### 필터 K — Reproducibility / Library availability (5/27 D-15)

**거를 사유**: 시간 budget 안에 method 검증 및 재현:
- sklearn/scipy/numpy/datasketch/faiss-cpu = 즉시 사용 가능
- pywavelets/umap-learn/scann = pip 설치 가능
- 직접 구현 200-500 line = 1-2일
- 외부 paper code clone = 의존성 검증 필요
- proprietary algorithm = 사용 불가 (GaussDB-Vector / Pinecone / Snowflake)

**threshold**:
- ✅ pip-installable: standard library
- ⚠️ direct implementation: 200-500 line 직접 구현 가능
- ❌ proprietary / GitHub clone but not maintained

**예상 drop**: 산업 proprietary (Pinecone / Snowflake / BigQuery 내부), B23 Diffusion (training pipeline)

### 필터 L — Selectivity gradient applicability (RQ4)

**거를 사유**: 본 연구 sel = {0.001, 0.01, 0.10} 3 levels:
- 0.001 = rare event (extreme tail)
- 0.01 = paper Fig 5 default
- 0.10 = relaxed selectivity

**fail case 일반화**:
- rare event sampling 약함 (uniform sample 시 0.001 sel = 80M × 0.001 = 80K hits, but 385 sample × 0.001 = 0.4 hits ≈ 0) → method가 rare event 적응 가능 여부

**threshold**:
- ✅ all 3 levels: density-aware / stratified / proportional 가능
- ⚠️ relaxed only: rare event 약함 (uniform sample-based)
- ❌ never adapts: deterministic uniform without weight

**예상 drop**: 추가 QMC variants (rare event 약함), 추가 reservoir variants (without weight)

### 필터 M — Narrative cohesion (5/27 + 6/11 storyline 7단계)

**거를 사유**: handoff_main §11.6 storyline:
1. Single random sampling skew 무너짐
2. 분포 알면 Neyman 답
3. 분포 모르니까 추정 활용
4. 단일 -8% 격차 입증
5. multi-table 0/66
6. 신규 method 발굴 → multi 강한 방식
7. Adaptive vs Adaptive+ensemble

**fail case 일반화**:
- 7단계 어디에도 fit 안 함 → drop
- 단일 stage 강화 (e.g. RQ1 추가 evidence) 만 → mid-priority

**threshold**:
- ✅ storyline fit: 단계 6 (신규 method 발굴) 또는 단계 7 (climax) 직접 기여
- ⚠️ supporting: 단계 1-5 강화
- ❌ outside: future work 영역

**예상 drop**: future work 영역 (Tier 3) — 모든 normalizing flow / SBM / persistent homology

### 필터 N — Sample-size compatibility (paper N=385 + AdaptiveState)

**거를 사유**: paper Eq 1-6 (N_init=385, period=50 update, decay 0.99). method가 sample size 동적 변화에 호환:
- O(N_sample) 방식: ✅ (sample 추가 시 incremental update 가능)
- O(N_sample²) 방식: ⚠️ (sample size 변경 시 재계산)
- pre-trained model: ⚠️ (sample 무관, 별도 inference)

**threshold**:
- ✅ incremental compatible: O(N_sample) per-update
- ⚠️ batch 재계산: O(N_sample²) — paper 50 query period에 fit
- ❌ batch only: O(N_sample³) 이상

**예상 drop**: spectral methods (eig decomposition), kernel methods (Gram matrix)

---

## 2. 필터 selection — 5/27 + 6/11 narrative critical 7개

### 2.1 사용자 명시 critical 영역 align

| 필터 | reason | priority |
|---|---|---|
| **A 시간 복잡도** | kdtree 22h+ stuck, agglomerative 12h | CRITICAL — 측정 불가 시 가치 0 |
| **B 공간 복잡도** | HDBSCAN OOM, vinecopula 245GB | CRITICAL — server 충돌 위험 |
| **F Outperform 보장** | 사용자 명시 "확실 outperform" | CRITICAL — 본 작업 핵심 목표 |
| **G 알고리즘 정직성** | 5/10 audit 30+ defect, paper reviewer reject | CRITICAL — 학술 신뢰성 |
| **I Redundancy** | 46 method 와 alias = 측정 가치 0 | CRITICAL — 시간 낭비 회피 |
| **E 학술 정합** | 9 paradigm + ★ 4강 비교 가능성 | HIGH — narrative anchor |
| **J Vector DB 컨텍스트** | 본 연구 single-vector single-table | HIGH — scope 정합 |

### 2.2 보조 필터 (cascade 후반부)

| 필터 | priority |
|---|---|
| C 차원 의존성 | MEDIUM — narrative caveat 으로 보완 가능 |
| D Dataset 부적합 | MEDIUM — 5 distribution category fit |
| H 구현 복잡도 | MEDIUM — 5/27 시간 budget |
| K Library availability | LOW — direct impl 가능하면 통과 |
| L Selectivity gradient | LOW — narrative 보조 |
| M Narrative cohesion | LOW — 7단계 storyline (대부분 통과) |
| N Sample-size compat | LOW — paper Eq 1-6 plug-in (대부분 통과) |

### 2.3 cascade 순서 (drop count maximize)

1. **G 알고리즘 정직성** (학술 fraud / alias / cosmetic diff → 즉시 drop)
2. **I Redundancy** (현재 46 method 와 본질 동일 → 즉시 drop)
3. **J Vector DB 컨텍스트** (multi-table only / RL only → drop)
4. **B 공간 복잡도** (OOM risk → drop)
5. **A 시간 복잡도** (1h+ → drop)
6. **F Outperform 보장** (★ 4강 alias 또는 약함 → drop)
7. **E 학술 정합** (9 paradigm 외 / ★ 4강 비교 불가 → drop)

→ 7 필터 cascade 후 잔존 method 가 ★ candidate.

---

## 3. cascade 적용 시 예상 drop count

총 candidate = ~553 method (Phase 1)
신규 = ~470 (현재 portfolio 외)
preliminary ★ = ~52

cascade 단계별 drop 추정:
| 단계 | 잔존 | drop |
|---|---|---|
| Start | 470 (신규 only) | 0 |
| **Filter G 정직성** | ~280 | -190 (alias / 명백한 fraud / cosmetic) |
| **Filter I Redundancy** | ~150 | -130 (현재 46 method 와 본질 동일) |
| **Filter J Vector DB** | ~100 | -50 (multi-table only / RL only / proprietary) |
| **Filter B 공간** | ~75 | -25 (OOM risk) |
| **Filter A 시간** | ~50 | -25 (8M ❌ / 80M ❌) |
| **Filter F Outperform** | ~15 | -35 (★ 4강 alias / 약함) |
| **Filter E 정합** | ~5-10 | -5-10 (paradigm scope outside) |

**예상 최종 jugement: 0~15 method 통과** (사용자 명시 "0건 OK")

---

## 4. END

작성: 2026-05-11 01:05 KST
다음 단계: `_FILTER_ANALYSIS.md` (cascade 적용, drop count + 사유 verbatim)

**핵심**: 14 필터 brainstorming 완료, 7 critical filter selection (G/I/J/B/A/F/E). Cascade 순서 = drop maximize 후 fine filter. 예상 통과 0~15 method.
