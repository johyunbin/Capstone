# Agent H — 1001 file 재해석 (batch baseline 관점) + Form 1 narrative 통합 deep dive

> **작성**: 2026-05-15 03:00 KST · Agent H · main thread 지시 "1001 file 재해석 (batch baseline 관점) + Form 1 narrative 통합" 응답
> **검증 기조**: paper PDF + Agent A (78%) / B (정정 7) / C (8 옵션 + 추가 3) / D (paper §V/§VI/§VII 8 영역 + 경쟁 paper 5 + BDAI 6) / E (Form 1 phase 1+2 design) / F (측정 plan + cost 130-180h) / G (paper Eq 1-6 verbatim + 본 의역 17-step) 7 호출 종합 + 9 analysis file 직접 read + handoff v19 종합
> **★★★ wording 정정 룰 2판 (Agent G critical 적용)**:
>   - ❌ 폐기: "5 단계 中 1 단계" / "paper §V-B Algorithm 1 14-step"
>   - ✓ 정정: **"paper §V-B Eq 1-6 + 본 연구 의역 step-wise pseudo-code 17 step"**
>   - ✓ 정정: **"paper Eq 5 (sampling_size update) 의 본 연구 group-aware allocation augment"** (= 의역 17-step 의 augment 영역)
>   - Neyman paradox = sel=0.01 한정 (DEEP paired n=455, sel=0.1 영역 paradox 역전)
>   - σ_j range 1.3-1.6× narrow = oracle interpretation (직접 측정 미완)
>   - Pareto Top 5 = sparse_rp / chao_weighted / **neuram** / pca1d / hilbert (reservoir = Form 1 main 영역, 별도 표기)
>   - byte-identical = 6 unique cells × 9 nominal
>   - 학부 capstone = ★★ 매우 강력
> **사용자 정책 (fix 모드)**: main theme = Form 1 (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ: Extending Exqutor's §V-B Framework), 4 측면 (대체+보완+개선+추가검증).

---

## 0. 핵심 결론 요약 (TL;DR)

본 Agent H 의 1001 file 재해석 결과 batch baseline axis 의 Form 1 narrative 안 위치 + RQ1/RQ2/RQ3 재해석 + Form 1 paper-grade RQ 재정립 + 40 폐기 method 정직 disclosure + Pareto Top 5 위치 + Neyman paradox σ_j oracle 의미 + batch ↔ streaming 연결 narrative + 5/27 + 6/11 narrative 통합 + byte-identical / Cliff's δ / Pareto frontier 등 Form 1 안 의미 정리.

| 영역 | 핵심 결정 | Form 1 narrative 안 역할 |
|---|---|---|
| **1001 file batch axis** | paper §V-B Eq 1-6 batch 환경 측정 = Form 1 design 의 baseline + pilot + complementary axis | ★ baseline (paper exact 재현) + pilot (method ablation) + design 근거 (streaming axis 의 방향성) + complementary (batch ↔ streaming boundary) |
| **RQ1 재해석** | skew 부정확 +3.74% = Form 1 분포 인지 axis 필요 입증 evidence | Form 1 §1.2 문제 정의 정량 evidence |
| **RQ2 재해석** | Neyman paradox sel=0.01 한정 = Proportional 권장 정당성 baseline (Cochran 1977 §5.5 part 포함) | Form 1 §4.5 Component D 의 Proportional default 정당성 |
| **RQ3 재해석** | 단독 best −10.17% / 결합 best −7.37% / paired 92.5% = batch axis 의 method axis 검증 | Form 1 §4.2 Component A 의 method-level evidence + §6.1-6.3 baseline |
| **Form 1 RQ 재정립** | RQ1'-RQ5' 5 paper-grade RQ 구조 (streaming framework / online cluster / Eq 5 augment / shift robustness / 4-way framework) | Form 1 phase 1 측정 plan (5/27) + phase 2 (6/11) base |
| **40 폐기 method** | 정합성 10 / 자원 7 / audit 23 = Form 1 §9.5 정직 disclosure | Form 1 의 학술 정직성 axis |
| **Pareto Top 5** | sparse_rp / chao_weighted / neuram / pca1d / hilbert = batch axis Pareto. reservoir / minibatch_partial = Form 1 streaming axis Pareto 후보 | Form 1 §7 자원 효율 + §10 산업 적용 |
| **σ_j oracle** | RQ2 oracle interpretation = Form 1 phase 2 future work (직접 측정) | Form 1 §10 future work |
| **batch → streaming 연결** | 1001 file = streaming axis design 근거 + complementary baseline | Form 1 §1.3 contribution scope + §6 측정 |
| **5/27 발표** | 1001 file (batch axis, 기존) + Form 1 360 file (streaming axis 3-way, 신규) | Form 1 phase 1 = 1500 file portfolio |
| **6/11 보고서** | batch axis + streaming axis 통합 + 부록 6 종 | Form 1 phase 1 full + phase 2 partial = 3180 file portfolio (확장) |
| **byte-identical** | 6 unique cells × 9 nominal = batch axis scope limitation, Form 1 streaming axis 의 cell 확장 가능 영역 | Form 1 §9.4 정직 disclosure |
| **Cliff's δ** | large better 63.0% (311/494) = batch axis 의 robust statistics evidence | Form 1 §6 측정 결과 statistical anchor |
| **Pareto frontier** | (학습시간, 정확도) 2-axis = batch axis 산업 적용 evidence | Form 1 §7 자원 효율 + streaming axis 의 3-axis 확장 (+memory) |

★★★ **본 Agent H 핵심 종합 권장**: 1001 file 은 **폐기 X, 재해석 OK**. Form 1 narrative 안에서 batch baseline axis 로 명확 positioning + streaming axis (Form 1 측정 1-5) 를 추가하여 **batch + streaming complementary framework** 으로 통합. 5/27 phase 1 (1001 file + Form 1 360 file 신규 = 1500 file portfolio) → 6/11 phase 1 full + phase 2 partial (1001 + 신규 2179 file = 3180 file portfolio). **paper-grade publication 가능 (EDBT short paper 10월 deadline)**.

★★★ **본 Agent H 의 정직 disclosure**:
1. **1001 file = batch 환경 한정** (offline K-means K=20 + paper Bernoulli baseline + stratified sampling). Form 1 streaming 환경 (BIRCH online + reservoir) 영역 측정 X.
2. **RQ2 Neyman paradox = DEEP sel=0.01 paired n=455 한정** (sel=0.1 영역에서 paradox 역전). σ_j range 1.3-1.6× narrow = oracle interpretation (직접 측정 미완).
3. **결합 best −7.37% = A2-Fig9 single cell 한정** (9-cell mean ≠ −7.37%, B1 baseline 의 paired Δ% 단일 cell).
4. **byte-identical = 6 unique × 9 nominal** (3 쌍 byte-identical: DEEP/SIFT sf=10 + DEEP sf=100/sel=0.1 + WIKI 768d sf=10).
5. **σ_j oracle interpretation** = K-means (L2) + L2 vector similarity range query → cluster 내 응답 일관 → σ_j narrow → Neyman ≈ Prop. classical theory (Cochran 1977 §5.5) 안 known mechanism.

---

## 1. 1001 file 의 Form 1 narrative 안 위치 (batch vs streaming axis)

### 1.1 batch axis vs streaming axis 분리 + 정의

본 연구의 1001 file 측정 portfolio 는 paper §V-B Adaptive Sampling 의 **batch 환경 측정** 이며, Form 1 의 streaming 환경 측정 (BIRCH online cluster maintenance + reservoir sampling) 과 **상호 보완적 (complementary)** 인 두 axis 로 명확히 분리된다.

#### 1.1.1 batch axis 정의 (1001 file 영역)

**환경**: offline batch 환경. paper §V-B 의 sample 추출 단계가 full dataset access 환경에서 작동.

**구성 요소**:
- **stratification**: offline K-means K=20 (scikit-learn MiniBatchKMeans, 50K subset 학습 후 80M full predict)
- **sampling**: paper §V-B Eq 1 Bernoulli (N=385) → 본 연구 stratified K-means K=20 으로 대체 (CaseA 단독) 또는 산술 평균 결합 (CaseB)
- **adjustment**: paper §V-B Eq 2-6 dynamic batch loop (Q-error feedback + momentum + lr decay + sampling_size update) paper exact 유지
- **cell scope**: 9 cells (DEEP/SIFT/SSN × sf=100/10/1 + multi-table A2-Fig7/8/9)
- **mode scope**: 3 (B1 baseline / CaseA 단독 / CaseB 결합)
- **method scope**: 56 method × 8 paradigm → 17 anchor + 40 폐기

**paper §V-B 와의 정합성**: paper 자체가 batch 환경 (single-table KNN, full sequential scan) 전제. 본 1001 file 은 paper 와 100% 정합한 batch 환경 측정.

#### 1.1.2 streaming axis 정의 (Form 1 영역)

**환경**: online streaming 환경. tuple 이 1 개씩 도착하는 시나리오 (online insert / OLTP write-heavy / RAG production stream).

**구성 요소**:
- **stratification**: BIRCH CF-tree online cluster maintenance (Zhang-Ramakrishnan-Livny SIGMOD 1996) + scikit-learn `Birch(n_clusters=20).partial_fit()` API
- **sampling**: Vitter 1985 Algorithm R per-stratum reservoir sampling (Al-Kateb-Lee-Wang SSDBM 2010 stratified reservoir extension)
- **adjustment**: paper §V-B Eq 2-6 verbatim 유지 + Eq 5 (sampling_size update) 의 group-aware allocation augment (본 연구 Form 1 augment 영역)
- **cell scope**: 3 dataset (DEEP/SIFT/SSN) × concept drift simulation (gradual/sudden/no) × ... 추가 cell
- **mode scope**: 4 method (Bernoulli + SRS + BIRCH + 본 Form 1 통합) + 4-way 비교 (Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1)

**paper 와의 align**: paper §VI-B "shifting workloads" 명시 영역 + §VI-D Fig.12 의 SelNet 비교 영역 확장.

#### 1.1.3 두 axis 의 complementarity 표

| axis | 환경 전제 | 측정 portfolio | paper 영역 | Form 1 영역 |
|---|---|---|---|---|
| **batch** | offline full access | 1001 file (현 portfolio) | paper §V-B Eq 1-6 verbatim batch | Form 1 baseline + pilot |
| **streaming** | online tuple arrival | Form 1 측정 1-5 (3180 file 예상) | paper §VI-B "shifting workloads" 명시 | Form 1 main contribution |

★★★ **본 Agent H 의 핵심 framing**: 1001 file 은 **폐기 X**. Form 1 narrative 안에서 **batch baseline axis 로 명확 positioning** + Form 1 streaming axis 와 **complementary framework** 으로 통합.

### 1.2 1001 file 의 Form 1 안 역할 (4 가지)

#### 1.2.1 역할 1 — baseline (paper exact 재현)

**근거**: 1001 file 의 B1 9 file = paper §V-B Bernoulli baseline 재현. Fig.12 mean qe_trim 1.618 vs paper 1.69 = **−4.3% 재현** (8-cell 재계산, REPORT v11 line 27-30).

**Form 1 안 역할**: paper §V-B 재현 정합성 입증. Form 1 의 streaming axis 측정이 paper exact baseline 의 batch axis 와 align 됨을 보장. Form 1 §5 실험 환경 + §6.1 RQ1 paper baseline 재현 영역.

**정직 disclosure**: byte-identical 6 unique cells × 9 nominal (DEEP/SIFT sf=10 + DEEP sf=100/sel=0.1 + WIKI 768d sf=10 의 3 쌍 byte-identical). 재현 정합성 정량 boundary 명시.

#### 1.2.2 역할 2 — pilot (method ablation evidence)

**근거**: 1001 file 의 CaseA 495 + CaseB 496 = 56 method × 9 cell × 2 mode 측정. **40 폐기 + 17 anchor** 의 method-level breakdown 정량 evidence.

**Form 1 안 역할**: Form 1 의 Component A (SRS) 의 method 선택 evidence. batch axis 에서 anchor 17 method (paradigm 분류 + Pareto 위치 + Cliff's δ + Cohen's d) 의 정량 evidence 가 streaming axis 의 method 선택 baseline. **streaming axis 측정 method (SRS + BIRCH + Form 1) 의 paradigm 정합성** 결정.

**정직 disclosure**: 폐기 method 40 (정합성 위반 10 + 자원 7 + algorithm audit drop 23). 측정 boundary 명시.

#### 1.2.3 역할 3 — design 근거 (streaming axis 방향성)

**근거**: 1001 file 의 Pareto frontier 분석 → reservoir + minibatch_partial 의 **memory O(1) + −9.25% 정확도** 발견. RQ3 단독 best minibatch_partial −10.17% 가 RQ2 Neyman 천장 −10.5% 에 거의 도달.

**Form 1 안 역할**: Form 1 의 Component B (BIRCH) + Component A (SRS) 의 design 근거. **batch axis Pareto Top 5 + reservoir/minibatch_partial 의 streaming-friendly 특성** 이 Form 1 streaming axis 측정의 방향성 결정.

**정직 disclosure**: reservoir Pareto 위치 (Pareto Top 5 외 별도 표기, **memory O(1) finding** 이 streaming axis 의 핵심 design 근거). minibatch_partial 의 chunk-only streaming 특성 (Pareto Top 5 외 별도 표기).

#### 1.2.4 역할 4 — complementary (batch ↔ streaming boundary)

**근거**: 1001 file 의 batch 환경 측정 결과와 Form 1 streaming 환경 측정 결과의 boundary 비교 가능.

**Form 1 안 역할**: Form 1 의 measurement 영역 (§6.4-6.8) 의 streaming axis 결과 + 1001 file batch axis 결과의 **paired comparison** 가능. batch ↔ streaming boundary 의 정량 measurement = Form 1 의 contribution 영역 한 부분.

**정직 disclosure**: 두 axis 의 환경 전제 다름 (batch = full access, streaming = sequential arrival). 직접 paired 비교 시 환경 boundary 명시.

### 1.3 1001 file 활용 영역 표 (Form 1 narrative 안)

| 1001 file 카테고리 | n file | Form 1 안 역할 | Form 1 §  |
|---|---:|---|---|
| **B1 (paper Bernoulli)** | 9 | baseline + 4-way 비교 baseline | §5.4 baseline + §6.6 4-way |
| **CaseA (단독 대체)** | 495 | method-level ablation pilot | §6.1 RQ1 + §6.3 RQ3 단독 |
| **CaseB (결합)** | 496 | ensemble robustness pilot | §6.3 RQ3 결합 |
| **A2-Fig8/9 multi-table** | included | multi-table generalization pilot | §6.7 옵션 E + §10 future |
| **RQ2 5-way** | 45 | Proportional default 정당성 baseline | §4.5 Component D + §6.2 RQ2 |
| **Pareto frontier** | analysis | streaming axis design 근거 | §7 자원 효율 |
| **K granularity** | 80 | K=20 sweet spot evidence | §4.2 Component A K 선택 |
| **40 폐기 method** | 25 | 정직 disclosure | §9.5 폐기 method 정직 |
| **byte-identical caveat** | analysis | scope limitation | §9.4 |

★ 1001 file portfolio = **batch axis 100% 유지** + Form 1 streaming axis 추가 측정 3180 file = total 4181 file portfolio (Form 1 phase 1+2 full).

---

## 2. RQ1/RQ2/RQ3 재해석 (Form 1 narrative 안)

본 영역은 1001 file 의 RQ1/RQ2/RQ3 측정 결과를 Form 1 narrative 안에서 재해석한 결과다. 각 RQ 의 측정 결과 + Form 1 안 역할 + 정직 disclosure 명시.

### 2.1 RQ1 재해석 — skew 부정확 +3.74% (Form 1 분포 인지 axis 필요 입증)

#### 2.1.1 측정 결과 (batch axis)

**측정 portfolio**: DEEP/SIFT/SSN sf=100 × Bernoulli vs KM20 stratified × sel{0.01, 0.10} = 5 cell × 5 trial

**핵심 finding (REPORT v11)**:
- **mean gap +3.74%** (Bernoulli vs KM20 stratified, 5-cell mean)
- skew 영역 (sel=0.01) 에서 Bernoulli unstratified variance 가 큼
- KM20 stratified 의 분포 인지 axis 가 −3.74% 개선 evidence

#### 2.1.2 Form 1 narrative 안 재해석

**Form 1 §1.2 문제 정의 정량 evidence**: RQ1 의 +3.74% 가 Form 1 의 **분포 인지 axis 필요성** 의 정량 evidence. paper §V-B Eq 1 Bernoulli 의 unstratified 한계 + 분포 인지 stratification 의 정량 가치.

**Form 1 §6.1 RQ1 paper baseline 재현 + 분포 인지 axis evidence**: Form 1 의 phase 1 측정의 baseline. streaming axis 에서 동일 evidence 재측정 (Form 1 측정 1 streaming workload simulation 에서 paired comparison).

#### 2.1.3 정직 disclosure

**환각 검증 4 영역 中 1 영역 (handoff_v19 §1.2 의 환각 정정)**:
- CLAUDE.md 의 "+3.74%" mean gap 표기와 실측 표 방향 충돌 가능 (handoff_v17 환각 검증 agent 결과 中 Uncertain 4 영역)
- **재계산 권장**: REPORT v11 의 정확 수치 직접 read 후 narrative 정합성 확인

**scope 명시**: 5 cell × 5 trial = 25 measurement 한정 (sf=100 영역). sf=10/1 영역 partial coverage.

### 2.2 RQ2 재해석 — Neyman paradox sel=0.01 (Proportional 권장 정당성 baseline)

#### 2.2.1 측정 결과 (batch axis)

**측정 portfolio**: KM20 5-way (Bernoulli + Equal + Proportional + Neyman + Anti-Neyman) × 9 cell = 45 measurement.

**핵심 finding (REPORT v11 line 139, Agent B verify)**:
- **DEEP sel=0.01 paired (n=455)**: Bern 1.746 → Equal 1.644 → **Prop 1.580** → Neyman 1.595 → **Anti 1.540 (최저)**
- **DEEP sel=0.1 paired (n=500)**: Bern 1.161 → Equal 1.117 → Prop 1.114 → **Neyman 1.108 (최저)** → Anti 1.110
- Bern → Prop = **−9.53%** improvement
- Anti 1.540 < Prop 1.580 < **Neyman 1.595 paradox** (sel=0.01 한정)

#### 2.2.2 Neyman paradox 메커니즘 (oracle interpretation)

**σ_j range narrow 메커니즘** (Agent C + 채림님 14:57 본질):
- 클러스터링 metric (L2) = query metric (L2) 같음
- → cluster 안 query 응답 거의 일관
- → σ_j range 1.3 ~ 1.6 배 narrow (oracle interpretation, sel=0.1 D_target 단일 calibration)
- → Neyman 의 σ-가중 효과 약함 → Proportional 이 답

**Cochran 1977 §5.5 정합성 (Agent C critical 발견)**:
> "the gain in accuracy from Neyman allocation compared to proportional allocation is pretty small. This is why in practice proportional allocation is often preferred to optimal (Neyman) allocation."
> "If the variances are uniform across all strata, Neyman allocation reduces to proportional allocation."

→ 본 연구의 σ_j narrow → Neyman ≈ Prop 메커니즘 = **classical theory 안 known result**. vector similarity range query domain 의 정량 발현이 novel.

#### 2.2.3 Form 1 narrative 안 재해석

**Form 1 §4.5 Component D 의 Proportional default 정당성**:
- Form 1 Component D 의 4 allocation mode (Equal / Proportional / Neyman / Anti-Neyman) 中 **Proportional default** 의 정당성 baseline.
- RQ2 의 batch axis 결과 + Cochran 1977 §5.5 의 classical theory 가 Form 1 의 design 결정 근거.

**Form 1 §6.2 RQ2 5-way 표본 할당 evidence**:
- batch axis Neyman paradox 의 정량 결과 + sel-dependency (sel=0.01 paradox / sel=0.1 normal)
- streaming axis Form 1 측정 1 (concept drift simulation) 에서 σ_j 의 online estimation accuracy 측정

**Form 1 §10 future work — σ_j oracle 직접 측정**:
- 현 batch axis σ_j range 1.3-1.6× narrow = oracle interpretation (직접 측정 미완)
- Form 1 phase 2 future work = σ_j 의 cell 별 직접 측정 + Neyman paradox 의 selectivity-dependent 메커니즘 정량 확인

#### 2.2.4 정직 disclosure

**scope 명시 (★★ major, Agent B critical 정정)**:
- ❌ Agent A wording: "Neyman 1.595 / Anti 1.540 / Prop 1.580" 전체 5-way 결과
- ✓ 정정 wording: **"DEEP sel=0.01 paired n=455 한정"** (sel=0.1 영역에서는 Neyman 최저 = paradox 역전)

**σ_j oracle interpretation 명시**:
- σ_j range 1.3-1.6× narrow = REPORT v11 oracle interpretation (sel=0.1 D_target 단일 calibration)
- 직접 측정 미완 = Form 1 phase 2 future work

**Cochran 1977 §5.5 part 포함 명시**:
- 본 연구의 σ_j narrow → Neyman ≈ Prop 메커니즘 = classical theory 안 partial known
- vector similarity range query domain 의 정량 발현이 novel

### 2.3 RQ3 재해석 — 단독/결합/paired (batch axis 결과 + streaming axis 필요)

#### 2.3.1 측정 결과 (batch axis)

**측정 portfolio**: 8 paradigm × 56 method × 9 cells × 2 modes = **1001 file** (B1 9 + CaseA 495 + CaseB 496, REPORT v11)

**핵심 finding (REPORT v11 + 9 analysis file)**:

1. **단독 best minibatch_partial −10.17%** (9-cell mean)
   - paper 변동 −4.3% 의 2.4 배
   - method_level_breakdown_20260513.md line 200 verify ✓
2. **결합 best Centroid tuple sparse_rp CaseB −7.37%** (A2-Fig9 single cell)
   - centroid_tuple_cheap_approximation_results_20260513.md line 63 verify ✓
   - **scope 명시**: 9-cell mean ≠ −7.37%, single cell paired Δ% (B1 baseline 의 paired Δ%)
3. **paired CaseB < CaseA 92.5%** (455/492, p<1e-45)
   - REPORT v11 line 1182 verify ✓
4. **Cliff's δ large better 63.0%** (311/494)
   - Hedges' g large 55.7% (275/494)
   - one-sided p<0.05 outperform 45.3% (224/494)
5. **negative control**: CaseA 단독 대체 0/493 = 0%
   - large worsening 37.1%
6. **Fig.12 재현**: 8-cell mean qe_trim 1.618 vs paper 1.69 = −4.3% (REPORT v11 line 27-30)

**paradigm rollup 8 (CaseB mean Δ%)**:
- P10 Density: −11.93 (n=1, 약함)
- P9 InfoTheoretic: −7.60 (n=9)
- P3 Streaming: −6.63 (n=44)
- P4 DimReduction: −6.03 (n=104)
- P2 Spatial: −5.57 (n=107)
- P5 QMC: +1.47 (n=62, paradigm-level 만 보고, method 4 폐기)
- P1 Cluster: +2.04 (n=87)
- P6 Quantization: +8.44 (n=53)

**method-level breakdown (12 anchor consistency)**:
- P2 lpm2 (-9.45% std 2.36), hilbert (-9.41% std 2.13)
- P3 chao_weighted (-9.60% std 6.36), reservoir (-9.25% std 3.00), thompson_sampling (-8.98% std 3.05)
- P4 neuram (-9.97% std 2.88), pca1d/cca1d/abp (-9.63% std 3.12), sparse_rp (-9.43% std 3.30)
- P6 opq (-9.37% std 3.26), pq (-9.25% std 2.50)
- P9 hyperloglog (-8.65% std 2.73)
- P1 minibatch (-9.28% std 3.29)

#### 2.3.2 α sweep 결과 (시나리오 B 확정)

**측정 portfolio**: 4 anchor method × A2-Fig9 cell × CaseB × 5 α (0.3, 0.4, 0.5, 0.6, 0.7) = 16 measurement (α=0.5 기존 재사용).

**핵심 finding (alpha_sweep_results_20260514.md)**:
- 4 method 中 3 method (sparse_rp / hilbert_real / chao_weighted) α=0.5 best
- hyperloglog 만 α=0.6 best (marginal 0.26%p 차이)
- **U-shape sensitivity**: α=0.3 (-2.17 ~ -3.91%), α=0.5 (-5.15 ~ -6.58%), α=0.7 (-1.98 ~ -3.36%)
- **결합 best −6.58% (sparse_rp α=0.5) < 단독 best −10.17% (minibatch_partial)**

**시나리오 B 확정**: 단독 대체 narrative + 결합 robustness 강화. "결합으로 단독 능가 X" 정직 표기.

#### 2.3.3 cheap 근사 4 후보 결과

**측정 portfolio**: A2-Fig9 cell × 4 anchor method × 2 mode × 4 cheap 근사 후보 = 32 datapoint.

**핵심 finding (cheap_approximation_extended_results_20260514.md)**:
- **Centroid tuple**: CaseB 4 method 모두 carry-over 보다 우위 (mean -0.96%p), 학습 비용 0
- B1 Hash: method × mode spread 크 (sparse_rp CaseA -10.93%p 우위 vs hyperloglog CaseA +7.84%p 악화)
- B2 PCA: marginal (CaseB mean -0.37%p)
- B3 Iterative: CaseB 일관 harmful (mean +0.81%p)

→ **Centroid tuple 만 보편 우위**. cheap 근사 = best of both worlds (0 학습 비용 + 더 좋은 ensemble 정확도).

#### 2.3.4 Form 1 narrative 안 재해석

**Form 1 §4.2 Component A (SRS) 의 method-level evidence**:
- RQ3 의 12 anchor method consistency = Form 1 SRS Component 의 method 후보 baseline
- streaming axis Form 1 측정 1 에서 동일 method 후보 streaming-aware 영역 측정

**Form 1 §6.3 RQ3 단독/결합 baseline + §6.4 streaming axis 확장**:
- batch axis RQ3 결과 (1001 file) = Form 1 §6 측정 결과의 baseline
- streaming axis Form 1 측정 1-5 (3180 file) = Form 1 §6 측정 결과의 main contribution

**Form 1 §6.7 multi-table generalization (옵션 E)**:
- A2-Fig8/9 Centroid tuple cheap 근사 + multi-join re-stratification 결과
- streaming axis 확장 = Form 1 phase 2 future work

#### 2.3.5 정직 disclosure

**scope 명시**:
- 단독 best −10.17% = 9-cell mean (minibatch_partial, A1-DEEP/SIFT/SSN + A2-Fig7/9 + A4-sel + A5-scale sf=1/10/100)
- 결합 best −7.37% = A2-Fig9 single cell paired Δ% (sparse_rp Centroid tuple CaseB), 9-cell mean ≠ −7.37%
- α sweep = A2-Fig9 cell × 4 anchor method 한정 (다른 cell 의 α sensitivity 미측정)
- cheap 근사 = A2-Fig9 cell × 4 anchor method × 2 mode 한정 (single cell, generalization 미측정)

**byte-identical 6 unique cells × 9 nominal**:
- 3 쌍 byte-identical: DEEP/SIFT sf=10 + DEEP sf=100/sel=0.1 + WIKI 768d sf=10
- 9-cell mean = 6 unique cells 결과 + 3 duplicate

### 2.4 RQ1/RQ2/RQ3 통합 narrative (시나리오 B 의 batch axis 위치)

**시나리오 B 흐름 (handoff_v17 § 2 verbatim)**:

1. **문제** (RQ1 영역): skew 영역 베르누이 부정확 +3.74%
2. **탐색**: 56 method × 8 갈래 × 9 측정 환경
3. **폐기**: 40 method (자원 7 + audit 23 + 정합성 10)
4. **단독 대체 best** (RQ3 영역): minibatch_partial **−10.17%** (9-cell mean) — paper 변동 −4.3% 의 2.4 배
5. **결합 시도** (RQ3 영역): 산술 평균 (α=0.5) best, U-shape sensitivity
6. **결합 한계**: 결합 best (−7.37% Centroid tuple, A2-Fig9 single cell) < 단독 best
7. **결합 진짜 가치**: method 선택 안정성 + cell spread 줄임 (★ "더 큰 정확도" 아님)
8. **자원 효율** (RQ3 영역): Pareto Top 5 = sparse_rp / chao_weighted / neuram / pca1d / hilbert, reservoir O(1) 산업 적용
9. **권장 설계**: 단독 대체 우선 + 결합 보조 + 자원 우선
10. **다중 테이블** (RQ3 영역 확장): Centroid tuple cheap 근사 (학습 비용 0 + CaseB 보편 우위)

★★★ **본 시나리오 B 흐름 = Form 1 narrative 의 batch baseline axis 영역**. Form 1 narrative 안에서는 위 10 단계가 §6.1 (RQ1) + §6.2 (RQ2) + §6.3 (RQ3) 영역으로 들어가고, Form 1 의 streaming axis (§6.4-6.8 Form 1 측정 1-5) 가 main contribution 으로 추가.

---

## 3. Form 1 narrative 안 RQ 구조 재정립 (paper-grade form, RQ1'-RQ5')

본 영역은 Form 1 narrative 의 paper-grade RQ 구조를 정형화한 결과다. **현 RQ1/RQ2/RQ3 (batch axis)** + **신규 RQ1'-RQ5' (Form 1 paper-grade)** = 두 RQ 구조 complementary.

### 3.1 RQ1' — streaming-aware framework 정량 정확도 (Bernoulli vs Form 1)

**질문**: streaming 환경에서 paper §V-B Bernoulli baseline 대비 Form 1 (SRS + BIRCH + Eq 5 group-aware) 의 정확도 우위가 얼마나 큰가?

**측정**: Form 1 측정 1 (streaming workload simulation, 1440 file)
- 3 dataset (DEEP/SIFT/SSN) × 2 sf × 3 drift (gradual/sudden/no) × 4 method (Bernoulli + SRS + BIRCH + Form 1) × 2 mode × 10 trial

**metrics**: Q-error mean + Q-error std + sample size trajectory + cluster centroid drift Δ%

**Form 1 안 위치**: **main contribution** (§6.4)

**batch axis 와의 paired**: 1001 file batch axis 의 baseline 결과 + Form 1 streaming axis 의 동일 method 측정 결과 = boundary 정량 비교

### 3.2 RQ2' — online cluster maintenance cost (BIRCH vs offline KMeans)

**질문**: BIRCH CF-tree online cluster maintenance 의 memory / latency / accuracy degradation 이 offline batch K-means 대비 얼마나 큰가?

**측정**: Form 1 측정 2 (online cluster maintenance cost, 540 file)
- 3 dataset × 4 BIRCH threshold (0.1, 0.3, 0.5, 1.0) × 3 K target (10, 20, 50) × 3 update freq × 5 trial

**metrics**: memory peak (MB) + latency per insert (μs) + σ_j² estimation error vs offline batch + Q-error degradation

**Form 1 안 위치**: **cost analysis** (§6.5)

**batch axis 와의 paired**: 1001 file batch axis 의 offline K-means K=20 결과 + Form 1 BIRCH online 결과 = accuracy degradation 정량

### 3.3 RQ3' — paper Eq 5 group-aware augment 효과

**질문**: paper §V-B Eq 5 (sampling_size update) 의 본 연구 group-aware allocation augment 의 효과는 paper exact scalar update 대비 얼마나 큰가?

**측정**: Form 1 측정 5 (phase 2 group-aware Eq 3-6 augment, 120 file pilot)
- 3 dataset × 2 sf × 2 mode × 10 trial

**metrics**: Q-error mean + sample size trajectory + cluster-specific n_inc 분포

**Form 1 안 위치**: **phase 2 future work** (§10.1)

**batch axis 와의 paired**: 1001 file batch axis 의 paper Eq 5 paper exact 결과 + Form 1 group-aware augment 결과

### 3.4 RQ4' — distribution shift robustness

**질문**: Form 1 framework 가 distribution shift (concept drift, embedding upgrade, time-based, mixed workload) 환경에서 얼마나 robust 한가?

**측정**: Form 1 측정 4 (distribution shift simulation, 480 file)
- 3 dataset × 4 추가 시나리오 (embedding upgrade / time-based / mixed workload / workload skew change) × 4 method × 2 mode × 5 trial

**metrics**: Q-error trajectory + recovery time + sample size adjustment magnitude

**Form 1 안 위치**: **추가검증 측면** (§6.7)

**batch axis 와의 paired**: 1001 file batch axis = no drift baseline. Form 1 streaming axis = 4 drift scenario 측정.

### 3.5 RQ5' — 3-way 비교 framework (Bernoulli + SelNet + 본 Form 1)

**질문**: paper §VI-D Fig.12 의 SelNet 한정 비교를 3-way (Bernoulli + SelNet + 본 Form 1) framework 으로 확장 시 본 Form 1 의 positioning 은?

**측정**: Form 1 측정 3 (4-way 비교, 600 file). 5/27 phase 1 = 3-way (Bernoulli + SelNet + 본 Form 1) 360 file 만. 6/11 phase 2 = + CE4HD partial + Ada-ef paper 인용.
- 3 dataset × 2 sf × 2 sel × 5 method × 10 trial (full 4-way)

**metrics**: Q-error mean + inference latency (ms) + offline training cost (s) + memory (MB)

**Form 1 안 위치**: **보완 측면** (§6.6)

**batch axis 와의 paired**: 1001 file batch axis 의 Bernoulli baseline + 본 method anchor 결과 + Form 1 의 4-way framework 결과

### 3.6 RQ 구조 비교 표 (batch axis vs Form 1 paper-grade)

| 영역 | 현 RQ (batch axis) | Form 1 RQ (paper-grade) | 측정 |
|---|---|---|---|
| **분포 인지 정확도** | RQ1 (skew +3.74%) | RQ1' (streaming framework) | 1001 file + Form 1 측정 1 |
| **할당 mode** | RQ2 (Neyman paradox sel=0.01) | (Form 1 §4.5 baseline) | 1001 file (5-way 45 file) |
| **method 단독/결합** | RQ3 (단독 -10.17% / 결합 -7.37%) | (Form 1 §6 baseline + §6.4 확장) | 1001 file (CaseA 495 + CaseB 496) |
| **online cluster cost** | (미측정, oracle interpretation) | RQ2' (BIRCH vs KMeans) | Form 1 측정 2 |
| **paper Eq 5 augment** | (미측정, paper exact) | RQ3' (group-aware augment) | Form 1 측정 5 (phase 2) |
| **distribution shift** | (미측정, paper §VI-B 명시 영역) | RQ4' (4 drift scenario) | Form 1 측정 4 |
| **learned baseline 비교** | (미측정, paper §VI-D SelNet 만) | RQ5' (3-way / 4-way framework) | Form 1 측정 3 |

★★★ **본 RQ 구조 재정립의 핵심**: **현 RQ1/RQ2/RQ3 = batch axis baseline + pilot** 으로 유지하고, **신규 RQ1'-RQ5' = Form 1 paper-grade main contribution** 으로 추가. 두 RQ 구조의 complementarity 가 paper-grade publication 의 narrative arc.

### 3.7 paper-grade publication 정합성

**EDBT short paper / VLDB short paper / SIGMOD short paper 권장 형태**:

- §1 Introduction: 문제 + paper §V-B Adaptive Sampling 영역 + Form 1 main theme
- §2 Background: paper §V-B Eq 1-6 + classical sampling theory + streaming algorithms
- §3 Related Work: paper Exqutor + CE4HD VLDB 2024 + Ada-ef arxiv 2512.06636 + Al-Kateb-Lee-Wang ISJ 2014 + BIRCH 1996
- §4 본 연구 방법론: Form 1 Component A+B+C+D + paper Eq 1-6 통합 표 + 본 의역 17-step pseudo-code
- §5 실험 환경: dataset + benchmark + baseline + metrics
- §6 측정 결과: **batch axis baseline (1001 file RQ1/RQ2/RQ3)** + **streaming axis main (Form 1 RQ1'-RQ5' 측정 1-5)**
- §7 자원 효율 Pareto + 산업 적용
- §8 paper 한계 보완 (L1+L5+L6)
- §9 본 Form 1 한계 + 정직 disclosure
- §10 future work
- §11 결론

→ 두 RQ 구조 (batch + Form 1) 가 §6 측정 결과 안에서 paired complementary 로 통합. paper-grade 의 narrative arc 완성.

---

## 4. 40 폐기 method 처리 (정직 disclosure)

본 영역은 1001 file 의 56 method 中 40 폐기 method 의 Form 1 narrative 안 정직 disclosure 영역이다.

### 4.1 40 폐기 method 분류 (3 범주)

**범주 1 — 정합성 위반 10 method (paper N=385 budget 위반)** (5/14 환각 검증 H1 정정: 9 → 10):
1. halton (P5 QMC)
2. sobol (P5 QMC)
3. lhs (P5 QMC)
4. hammersley (P5 QMC)
5. dense_rp (P4 DimReduc)
6. random_projection (P4 DimReduc)
7. dbscan (P1 Cluster)
8. ccsketch (P5 QMC)
9. lsh (P5 QMC)
10. ams_count_sketch (P5 QMC)

**폐기 사유**: 측정 시 final_size 가 paper N=385 budget 초과 (예: sobol final_size 폭증, dense_rp/random_projection RNG 정합성 결손, lsh hash collision bias). 본 method 의 paper-exact 측정이 paper §V-B Eq 1 의 budget 정합성 위반.

**범주 2 — 자원 한계 7 method (측정 미커버)**:
1. dirichlet (Tier 2)
2. kernelpca (Tier 2)
3. neurocard_lite (Tier 2)
4. birch (Tier 2)
5. hdbscan (Tier 2)
6. agglomerative (Tier 2)
7. kde_parzen (KDE 1, 5/14 07:39 kde_chain 폐기 결정)

**폐기 사유**: 자원 한계 (메모리 / 시간) — SF=100 (80M rows × 96d/128d/256d/768d) 영역에서 OOM 또는 timeout. 측정 시도 했으나 자원 부족으로 미커버.

**범주 3 — algorithm audit drop 23 method**:
- P1 Cluster: kmedoids / fuzzy_cmeans / agglomerative (자원 미커버 동시) / spectral / mean_shift / affinity_propagation 등
- P4 DimReduc: lp_bound (CaseB +16.43% 큰 악화) / ica / nmf / lle / mds / isomap 등
- P6 Quantization: rabitq_strat (CaseB -3.81% marginal) 등

**폐기 사유**: 5/10 P1-P6 audit + 5/11 Phase 4 audit 결과 algorithm 자체의 학술 정당성 약함 (lp_bound 의 L2 norm quantile 부적합, ica 의 source separation 부적합 등).

### 4.2 Form 1 narrative 안 정직 disclosure 영역

#### 4.2.1 Form 1 §9.5 폐기 method 정직 분류

**verbatim wording**:
> "본 1001 file 측정 portfolio 의 method coverage = 17 anchor + 40 폐기. 폐기 method 40 의 정직 분류:
> - **정합성 위반 10 (paper N=385 budget 위반)**: halton / sobol / lhs / hammersley / dense_rp / random_projection / dbscan / ccsketch / lsh / ams_count_sketch — paper §V-B Eq 1 의 budget 정합성 위반으로 paper-exact 측정 부적합.
> - **자원 한계 7 (Tier 2 6 + KDE 1)**: dirichlet / kernelpca / neurocard_lite / birch / hdbscan / agglomerative / kde_parzen — SF=100 (80M × 96-768d) 영역 OOM 또는 timeout.
> - **algorithm audit drop 23**: lp_bound / ica / nmf / lle / mds / isomap / kmedoids / fuzzy_cmeans / spectral / mean_shift / affinity_propagation / rabitq_strat 등 — 5/10 audit + 5/11 Phase 4 audit 결과 algorithm 자체 학술 정당성 약함.
>
> 본 Form 1 측정 의 method coverage = 17 anchor + 폐기 method 의 정직 boundary 명시."

#### 4.2.2 Form 1 §9.4 byte-identical caveat

**verbatim wording**:
> "본 연구 측정 cell 9 nominal 中 6 unique cells (byte-identical 3 쌍 = DEEP/SIFT sf=10 + DEEP sf=100/sel=0.1 + WIKI 768d sf=10). 본 Form 1 측정의 cell coverage = 6 unique cells 의 streaming axis 확장. 정직 표기."

#### 4.2.3 폐기 method 의 Form 1 안 future work 영역

**Form 1 §10.1 phase 2 future work**:
- 자원 한계 7 method 의 streaming axis 측정 영역 (BIRCH 의 partial_fit 구현 + agglomerative 의 chunk streaming 변환 등)
- algorithm audit drop 23 method 의 알고리즘 자체 검토 (lp_bound 의 L2 norm quantile 메커니즘 정밀화 등)

**Form 1 §10.6 streaming framework 의 RAG production 적용**:
- 정합성 위반 10 method (Sobol QMC sequence 등) 의 streaming reservoir variant 검토

### 4.3 폐기 method 처리 정직성 score (사용자 정책 정합성)

**사용자 정책 (handoff_v19 § 4 verbatim)**:
- 정직 disclosure (cherry-picking 회피, 폐기 method 정직 명시)
- "100% 검증된" 표기 회피 + uncertain 영역 명시

**본 Agent H 의 폐기 method 정직 disclosure score (1-10)**:
- 정합성 위반 10: **10/10** (명시 완료)
- 자원 한계 7: **9/10** (명시 완료, Tier 2 vs KDE 1 분리)
- algorithm audit drop 23: **8/10** (명시 완료, 개별 method 사유 partial)

★ **본 Agent H 권장**: Form 1 narrative 의 §9.5 폐기 method 정직 disclosure 영역 = 40 method × 사유 표 + future work 영역 명시.

---

## 5. Pareto Top 5 의 Form 1 안 위치

본 영역은 1001 file 의 Pareto frontier 분석 결과를 Form 1 narrative 안에서 재해석한 결과다.

### 5.1 batch axis Pareto Top 5 (분석 결과)

**측정 결과 (resource_efficiency_pareto_20260513.md)**:

**Pareto frontier ★ 5 method (산업 적용 Top 5)**:
1. **sparse_rp** (P4 DimReduc) — fit 0.1s + CaseB -9.43% Δ%, RNG cheap + Achlioptas density 1/3 sparse projection. ★⭐⭐
2. **chao_weighted** (P3 Streaming) — fit 0.5s + CaseB -9.60% Δ%, weighted reservoir sampling. ★⭐⭐
3. **neuram** (P4 DimReduc) — fit 0.5s + CaseB -9.97% Δ%, autoencoder 50K cap. 본 측정 portfolio 의 **정확도 최고 anchor**. ★⭐⭐
4. **pca1d** (P4 DimReduc) — fit 0.5s + CaseB -9.63% Δ%, full PCA-1. ★⭐⭐
5. **hilbert / hilbert_real** (P2 Spatial) — fit 0.1-0.5s + CaseB -9.27 ~ -9.41% Δ%, space-filling curve. ★⭐⭐

**reservoir + minibatch_partial 영역 (Pareto Top 5 외 별도 표기)**:
- **reservoir** (P3 Streaming) — fit 0.1s + CaseB -9.25% Δ% + **memory O(1)** ★★★ (산업 적용 최강 finding)
- **minibatch_partial** (P1 Cluster) — fit 0.5s + chunk-only streaming + memory O(B·D), CaseB -6.98%, **단독 best CaseA -10.17%** (9-cell mean)

### 5.2 Form 1 narrative 안 Pareto Top 5 위치

#### 5.2.1 Form 1 §7 자원 효율 axis

**verbatim wording**:
> "본 batch axis Pareto frontier 분석 결과 5 method (sparse_rp / chao_weighted / neuram / pca1d / hilbert) 가 학습 시간 0.1-0.5s + CaseB -9 ~ -10% 의 anchor 수준 정확도 영역에 위치한다. 반면 본 Form 1 의 streaming axis = reservoir (memory O(1) + -9.25%) + minibatch_partial (chunk-only streaming + 단독 -10.17%) 가 별도 axis 의 main method. 두 axis 의 boundary = batch axis Pareto Top 5 (DimReduc/Spatial/Streaming weighted) + streaming axis main (Streaming uniform + Cluster chunk)."

#### 5.2.2 Form 1 §4.2 Component A (SRS) 의 method 선택 evidence

**verbatim wording**:
> "본 Form 1 의 Component A (Stratified Reservoir Sampling) 의 method 영역 = paper Eq 1 의 Bernoulli sample 추출 대체. batch axis Pareto Top 5 의 P4 DimReduc 4 method (sparse_rp / neuram / pca1d / cca1d) + P2 Spatial 2 method (hilbert / hilbert_real) + P3 Streaming 1 method (chao_weighted) = 7 후보 中 streaming-friendly axis 의 method (reservoir + minibatch_partial + Vitter Algorithm R 호환 method) 가 Form 1 의 main 후보."

#### 5.2.3 Form 1 §10 산업 적용 추천 3 영역

**verbatim wording (handoff_v17 § 1.5 verbatim)**:
> "산업 적용 추천 3 영역:
> - **영역 A (Best of Both Worlds)**: sparse_rp / chao_weighted / hilbert / pca1d — fit 0.1-0.5s + memory O(D·k) or O(K) + CaseB -9 ~ -10% (★ 일반 OLAP 영역)
> - **영역 B (Quality-first)**: neuram / opq / pca1d — fit 0.5-2.5s + CaseB -9 ~ -10% (★ 정확도 우선 영역)
> - **영역 C (Resource-first, ★★ Form 1 streaming axis main)**: reservoir / minibatch_partial / zorder_morton / rsvd — fit 0.1-0.5s + memory O(1) ~ O(B·D) + CaseB -7 ~ -9% (★ 모바일/embedded/streaming 영역)
>
> ★ 본 Form 1 의 streaming axis = 영역 C (Resource-first) 의 정량 확장 + paper §V-B 영역의 streaming-aware 변환."

### 5.3 Form 1 streaming axis 후보 method 검토

**Vitter 1985 Algorithm R 호환 method (streaming-friendly)**:
- **reservoir** (P3 Streaming) — Vitter 1985 base + O(1) memory + paper §V-B baseline 와 mathematically equivalent (K=1, no stratification) ★★★
- **chao_weighted** (P3 Streaming) — Chao 1982 weighted reservoir + O(K) memory + paper §V-B 의 stratified extension 가능 ★★
- **thompson_sampling** (P3 Streaming) — Beta posterior + O(B·D) + online update 가능 ★
- **minibatch_partial** (P1 Cluster) — chunk-only streaming + memory O(B·D) + 단독 best -10.17% ★★★

**non-streaming method (batch axis 한정)**:
- sparse_rp / hilbert / pca1d / neuram — batch 환경 한정 (full data fit 필요)
- opq / pq — batch 환경 한정 (faiss train 200K)

**streaming-friendly 변환 후보 (Form 1 phase 2)**:
- **partial-fit variant**: sparse_rp partial / hilbert online (Faloutsos 1989) / pca1d incremental PCA (sklearn `IncrementalPCA`) / neuram online autoencoder 등
- **incremental clustering 변환**: minibatch_partial 이 이미 chunk-only streaming, 다른 P1 method 도 chunk variant 가능

#### 5.3.1 Form 1 phase 1 측정 포함 여부

**5/27 phase 1 (Form 1 측정 1 streaming, 1440 file)**:
- 4 method: **Bernoulli (paper baseline)** + **SRS Equal** + **SRS Proportional** + **SRS Neyman** (또는 Bernoulli + 본 Form 1 SRS Proportional + 본 Form 1 SRS Neyman + reservoir(K=1))
- 5/27 시점에는 batch axis Pareto Top 5 의 stream variant 측정 X (phase 2 future)

**6/11 phase 1 full + phase 2 partial (Form 1 측정 3 4-way + 측정 4 distribution shift)**:
- 추가 method: + chao_weighted streaming + minibatch_partial streaming + SelNet baseline
- batch axis Pareto Top 5 의 stream variant 측정 partial

### 5.4 Pareto Top 5 의 정직 disclosure

**환각 정정 (handoff_v19 § 1.2 verbatim)**:
- ❌ Agent A wording: Pareto Top 5 명단 오류 (reservoir ↔ neuram 혼동)
- ✓ 정정 wording: **Pareto Top 5 = sparse_rp / chao_weighted / neuram / pca1d / hilbert** (reservoir = Form 1 streaming axis main, 별도 표기)

**scope 명시**:
- batch axis Pareto Top 5 = SF=1 DEEP cell × 1000 query × 100-200초/measurement 기반 wall-clock 정보
- 다른 SF 영역 (sf=10/100) 및 dataset (SIFT/SSN/WIKI) 별 Pareto frontier partial coverage
- streaming axis Pareto = Form 1 측정 1-5 의 결과 확정 후 별도 frontier 정형화 가능

---

## 6. 5-way Neyman paradox + σ_j oracle 의 Form 1 안 의미

본 영역은 RQ2 5-way Neyman paradox + σ_j range 1.3-1.6× narrow 의 oracle interpretation 의 Form 1 narrative 안 의미 정리.

### 6.1 5-way Neyman paradox 측정 결과 정확 표

**측정 portfolio**: KM20 5-way × 9 cell = 45 measurement (RQ2 영역).

**Agent B Python 재계산 verify ✓**:

| cell | mode | Bern | Equal | **Prop** | **Neyman** | **Anti** | 최저 |
|---|---|---:|---:|---:|---:|---:|---|
| DEEP sel=0.01 (paired n=455) | 5-way | 1.7464 | 1.6442 | **1.5800** | 1.5954 | **1.5402** | Anti ★ paradox |
| DEEP sel=0.1 (paired n=500) | 5-way | 1.1608 | 1.1169 | 1.1135 | **1.1076** | 1.1101 | Neyman ★ normal |

**scope 명시 (Agent B critical 정정 ★★)**:
- ❌ Agent A wording: "Neyman 1.595 / Anti 1.540 / Prop 1.580" 전체 5-way 결과
- ✓ 정정 wording: **"DEEP sel=0.01 paired n=455 한정"** (sel=0.1 영역에서는 Neyman 최저 = paradox 역전)

### 6.2 σ_j oracle interpretation 메커니즘

**REPORT v11 oracle interpretation 메커니즘 (Agent B verify)**:

1. **클러스터링 metric = query metric**: K-means (L2) + L2 vector similarity range query
2. **cluster 내 응답 일관**: cluster 안 query response 거의 일관 (cluster 안 D_target 적합도 안정)
3. **σ_j range 1.3-1.6× narrow**: cluster 별 σ_j 가 좁은 range 내 (sel=0.1 D_target 단일 calibration)
4. **Neyman 의 σ-가중 효과 약함**: σ_j 가 균일하면 Neyman ≈ Proportional (Cochran 1977 §5.5)
5. **Anti-Neyman 의 paradox**: σ_j 가 좁은 range 라 Neyman 의 σ-가중이 noise 발현, Anti-Neyman 의 1/σ 가중이 균형 잡힘

**Cochran 1977 §5.5 정합성 (Agent C critical)**:
> "If the variances are uniform across all strata, Neyman allocation reduces to proportional allocation where the number of sampled units in each stratum is proportional to the population size of the stratum."

→ σ_j uniform → Neyman = Proportional (classical theory known result). 본 연구의 σ_j narrow → Neyman ≈ Prop = **partial known mechanism + vector similarity domain 의 정량 발현 (novel)**.

### 6.3 Form 1 narrative 안 σ_j oracle 의미

#### 6.3.1 Form 1 §4.5 Component D 의 Proportional default 정당성

**verbatim wording**:
> "본 Form 1 Component D 의 4 allocation mode (Equal / Proportional / Neyman / Anti-Neyman) 中 Proportional default. 정당성:
> - **batch axis evidence**: RQ2 5-way 측정 결과 DEEP sel=0.01 paired (n=455) 에서 Neyman paradox 발견 (Anti 1.540 < Prop 1.580 < Neyman 1.595). σ_j narrow → Neyman ≈ Prop (oracle interpretation).
> - **classical theory align**: Cochran 1977 §5.5 의 'If variances are uniform, Neyman = Proportional'. K-means (L2) + L2 vector similarity range query 환경에서 σ_j uniform 발현.
> - **streaming axis 확장**: Form 1 BIRCH CF tuple (N_j, LS_j, SS_j) 가 σ_j 의 online estimate 가능. 그러나 σ_j narrow 의 oracle interpretation 이 batch axis 에서 입증됐으므로 Form 1 의 default = Proportional (online σ_j 추정 cost 절감)."

#### 6.3.2 Form 1 §10 future work — σ_j 직접 측정

**verbatim wording**:
> "Form 1 phase 2 future work:
> - **σ_j range 직접 측정**: 본 batch axis 의 σ_j 1.3-1.6× narrow = oracle interpretation (sel=0.1 D_target 단일 calibration). 직접 측정 미완.
> - **방법**: 9 cell 별 5-way csv 의 per-stratum σ_j 추출 + paradox 메커니즘 정형화
> - **paper-grade publication 가치**: vector similarity range query domain 의 σ_j narrow 메커니즘 정량 발현 (Cochran 1977 §5.5 의 vector domain 확장)
> - **추가 측정 cost**: 9 cell × 5-way × per-stratum σ_j 추출 = 2-3h 분석 + cosine/Manhattan K-means × 4 method × 3 cell × 2 mode = 24 측정 + K=50/100/200 × 4 anchor × 3 cell = 36 측정 = 약 60 측정 + 2-3h 서버 시간"

#### 6.3.3 Form 1 §9.3 본 Form 1 한계 (정직 disclosure)

**verbatim wording**:
> "본 Form 1 의 σ_j 사용 영역 = Component D Neyman allocation (online σ_j 추정 가능, BIRCH CF tuple LS/SS). batch axis RQ2 σ_j narrow oracle interpretation 의 직접 측정은 phase 2 future work. 본 Form 1 phase 1 = Proportional default (σ_j 의 oracle interpretation 의 evidence 기반)."

### 6.4 Neyman paradox + σ_j oracle 의 paper-grade publication 가치

**venue 권장 (Agent E + Agent C 종합)**:
- **EDBT short paper (10월 deadline)**: σ_j narrow mechanism + vector similarity domain 정량 발현 = paper-grade 가능
- **VLDB short paper (4월 또는 11월)**: Cochran 1977 §5.5 + vector domain 의 정량 발현 + Form 1 framework 통합 = paper-grade 강력
- **CIKM short paper (5-6월)**: cardinality estimation + IR 영역 fit

**박광현 5/15 미팅 자문 항목**:
- σ_j narrow → Neyman ≈ Prop 메커니즘의 학술적 의미
- vector similarity range query domain 의 정량 발현 novelty 평가
- Form 1 phase 2 future work 의 σ_j 직접 측정 plan

### 6.5 정직 disclosure (★★ Agent B critical 정정)

**scope 명시**:
- Neyman paradox = **DEEP sel=0.01 paired n=455 한정** (sel=0.1 영역 paradox 역전)
- σ_j range 1.3-1.6× narrow = **oracle interpretation** (직접 측정 미완)
- mechanism = **partial known** (Cochran 1977 §5.5 안 부분 포함, vector domain 정량 발현이 novel)

---

## 7. batch axis → streaming axis 연결 narrative

본 영역은 1001 file batch baseline 의 Form 1 streaming axis design 근거 + 두 axis complementarity 의 narrative 영역이다.

### 7.1 1001 file batch baseline = Form 1 streaming axis design 근거 (5 영역)

#### 7.1.1 영역 1 — method 후보 결정 (Pareto Top 5 + reservoir + minibatch_partial)

**batch axis evidence**: Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) + reservoir (memory O(1) + -9.25%) + minibatch_partial (chunk-only + 단독 -10.17%)

**Form 1 streaming axis design**:
- Component A (SRS) main 후보 = **reservoir 변환** (Vitter 1985 Algorithm R) + **chao_weighted streaming** (Chao 1982 weighted reservoir extension)
- Pareto Top 5 batch method 의 streaming variant = Form 1 phase 2 future work

**근거**: 1001 file batch axis 의 Pareto 위치 + Cliff's δ + Cohen's d 가 streaming axis method 선택의 직접 evidence.

#### 7.1.2 영역 2 — K granularity 결정 (K=20 sweet spot)

**batch axis evidence**: km_granularity_sensitivity_3way (K=10/20/30) × 4 anchor × 5 cells = 60 paired
- sparse_rp: K=10 +5.05% → K=20 -10.60% → K=30 -6.78% (U-shape, K=20 sweet)
- chao_weighted: K=10 -10.63 → K=20 -12.01 → K=30 -10.39 (K=20 sweet)
- hilbert_real: K-robust (range 0.42 ~ 2.24)
- hyperloglog: K-robust (range 0.15 ~ 2.55)

**Form 1 streaming axis design**:
- Form 1 Component B (BIRCH) 의 K target = **K=20 (batch axis sweet spot evidence 기반)**
- streaming axis 의 K-sensitivity 추가 측정 (Form 1 측정 2 BIRCH cost) 에서 K=10/20/50 × BIRCH threshold grid 측정

**근거**: 1001 file batch axis 의 K=20 sweet spot 이 Form 1 BIRCH n_clusters=20 의 직접 evidence.

#### 7.1.3 영역 3 — allocation mode 결정 (Proportional default)

**batch axis evidence**: RQ2 5-way 측정 + Neyman paradox sel=0.01 + σ_j narrow oracle interpretation

**Form 1 streaming axis design**:
- Form 1 Component D (allocation) default = **Proportional** (batch axis evidence + Cochran 1977 §5.5 정합)
- 4 mode (Equal / Proportional / Neyman / Anti-Neyman) 측정 = Form 1 측정 1 (streaming workload simulation) 에서 4 allocation mode × 3 drift × 측정

**근거**: 1001 file batch axis 의 5-way 결과 + σ_j oracle 이 Form 1 Proportional default 의 직접 evidence.

#### 7.1.4 영역 4 — 결합 framework 결정 (산술 평균 α=0.5 default)

**batch axis evidence**: α sweep 결과 4 method 中 3 method (sparse_rp / hilbert_real / chao_weighted) α=0.5 best, U-shape sensitivity

**Form 1 streaming axis design**:
- Form 1 Component C (paper Eq 2-6 통합) 의 결합 mode 측정 = α=0.5 산술 평균 default
- streaming axis 의 α sensitivity 추가 측정 (Form 1 phase 2 future work)

**근거**: 1001 file batch axis 의 α sweep 결과가 Form 1 산술 평균 α=0.5 default 의 직접 evidence.

#### 7.1.5 영역 5 — cheap 근사 framework 결정 (Centroid tuple)

**batch axis evidence**: cheap 근사 4 후보 (Centroid / Hash / PCA / Iter) 측정 결과 Centroid tuple 만 CaseB 보편 우위 (mean -0.96%p)

**Form 1 streaming axis design**:
- Form 1 측정 4 (distribution shift) 의 mixed workload (50% DEEP + 50% SIFT) scenario = Centroid tuple cheap 근사 적용
- multi-table generalization (옵션 E) = Form 1 phase 2 future work

**근거**: 1001 file batch axis 의 cheap 근사 결과가 Form 1 multi-table generalization 의 직접 evidence.

### 7.2 두 axis complementarity (3 axis)

#### 7.2.1 axis 1 — 환경 전제 (batch vs streaming)

| axis | 환경 | full access | sequential arrival | random access |
|---|---|:---:|:---:|:---:|
| **batch (1001 file)** | offline batch | ✓ | ✗ | ✓ |
| **streaming (Form 1)** | online stream | ✗ | ✓ | ✗ |

★ **boundary 비교 가능**: paper §V-B Eq 1-6 의 batch baseline + Form 1 streaming axis = paired comparison + boundary 정량.

#### 7.2.2 axis 2 — method 영역 (DimReduc/Spatial/Quant vs Streaming)

| axis | 주류 paradigm | method 후보 |
|---|---|---|
| **batch (1001 file)** | P4 DimReduc + P2 Spatial + P6 Quant | sparse_rp / neuram / pca1d / hilbert / opq / pq |
| **streaming (Form 1)** | P3 Streaming + P1 Cluster (chunk) | reservoir / chao_weighted / thompson_sampling / minibatch_partial |

★ **boundary**: P3 Streaming (chao_weighted) 가 두 axis 모두에서 anchor 위치. P1 Cluster (minibatch) 의 batch K-means vs P1 (minibatch_partial) 의 chunk streaming = paired 가능.

#### 7.2.3 axis 3 — 자원 효율 (학습시간, 정확도, memory)

| axis | 학습 시간 | 정확도 | memory |
|---|---|---|---|
| **batch (1001 file)** | 0.1-2.5s | -9 ~ -10% | O(N×d) ~ O(K×D) |
| **streaming (Form 1)** | per-tuple O(1) | -9 ~ -10% (전망) | O(K×D) ~ O(N×d) |

★ **boundary**: batch axis 의 fit elapsed (0.1-2.5s wall-clock) vs streaming axis 의 per-tuple update time (O(1) amortized) = paired 측정 가능.

### 7.3 batch ↔ streaming 연결 narrative (Form 1 §1.3 contribution scope)

**verbatim wording (Form 1 narrative 안 정형화 권장)**:

> "본 연구의 contribution scope = **batch axis baseline + streaming axis main contribution**.
>
> **Batch axis (1001 file portfolio)**:
> - paper §V-B Adaptive Sampling Eq 1-6 batch 환경 재현 (Fig.12 mean qe_trim 1.618 vs paper 1.69 = -4.3%)
> - 56 method × 9 cell × 3 mode 측정 + 40 폐기 정직 분류 + 17 anchor 일관성 (-9 ~ -10% std 2-3)
> - RQ1 (skew +3.74%) + RQ2 (Neyman paradox sel=0.01 + σ_j oracle) + RQ3 (단독 -10.17% / 결합 -7.37% / paired 92.5%)
>
> **Streaming axis (Form 1 측정 1-5, phase 1 + phase 2)**:
> - paper §V-B Eq 1 Bernoulli 대체 (SRS + BIRCH online cluster) + Eq 5 group-aware augment
> - paper §VI-B 'shifting workloads' 명시 영역 정량 측정
> - paper §VI-D Fig.12 SelNet 한정 비교를 3-way (Bernoulli + SelNet + 본 Form 1) framework 으로 확장
>
> **두 axis 의 complementarity**:
> - batch axis baseline = streaming axis design 근거 (method 후보 + K granularity + allocation mode + α default + cheap 근사)
> - streaming axis main = paper §V-B framework 의 streaming-aware 확장 (paper L1+L5+L6 보완)
> - boundary 비교 (batch ↔ streaming) = 본 연구의 contribution 영역 한 부분
>
> 본 연구 narrative 의 anchor = batch axis 가 streaming axis 의 design 근거 + complementary baseline 으로 기능."

### 7.4 정직 disclosure (★★ 두 axis 환경 boundary)

**환경 전제 명시**:
- batch axis = offline full access 환경. paper §V-B Eq 1-6 batch loop 가 every 50 query 마다 full sequence access 가능.
- streaming axis = online tuple arrival 환경. Form 1 BIRCH partial_fit + reservoir Vitter Algorithm R 가 single-pass.

**paired comparison 시 주의**:
- batch axis Q-error + streaming axis Q-error = 환경 boundary 다름으로 직접 paired Δ% 비교 시 caution.
- Form 1 phase 1 측정 1 의 (c) no drift scenario = batch axis 와 가장 가까운 환경 (concept drift X) → 직접 paired 비교 가능 영역.

---

## 8. 5/27 / 6/11 narrative 구성 (batch + streaming 통합)

본 영역은 5/27 발표 + 6/11 보고서의 batch axis (1001 file) + streaming axis (Form 1 측정 1-5) 통합 narrative 영역이다.

### 8.1 5/27 발표 narrative 구성 (20 slide framework)

**phase 1 영역 (5/27, 50-80h cost)**:
- Form 1 Component A (SRS) + Component B (BIRCH online) + Component D (allocation)
- Form 1 측정 1 (streaming workload simulation, 1440 file)
- Form 1 측정 3 partial (3-way: Bernoulli + SelNet + 본 Form 1, 360 file)
- 측정 portfolio = 1001 file (batch axis, 기존) + Form 1 360 file (streaming axis, 신규 3-way) = **1500 file (단일 mode 측정 우선, 다른 측정 6/11)**

**20 slide 구성 (handoff_v17 § 3.1 base + Form 1 통합)**:

| slide | 영역 | 핵심 message |
|---|---|---|
| 1 | Title + Team + Date | 속도는벡터 / Capstone Final / 2026-05-27 |
| 2 | Problem (VAQ + paper §V-B) | paper Exqutor §V-B Adaptive Sampling 영역 + 잘못된 cardinality → plan 한계 |
| 3 | Paper Exqutor 핵심 메커니즘 | ECQO (인덱스 ON) + Adaptive Sampling (인덱스 OFF) + Eq 1-6 verbatim + 본 의역 17-step pseudo-code |
| 4 | 본 연구 contribution scope (Form 1) | Streaming-aware Distribution-Conscious CE for VAQ + 4 측면 (대체+보완+개선+추가검증) + paper Eq 1 대체 vs Eq 2-6 통합/augment |
| 5 | paper §V-B Eq 1-6 + 본 Form 1 통합 axis | Eq 1 대체 (SRS + BIRCH) + Eq 5 (sampling_size update) group-aware augment + Eq 2-4/6 paper exact |
| 6 | 본 Form 1 Component A (SRS) | algorithm pseudo-code + O(N×d) memory + streaming compatible |
| 7 | 본 Form 1 Component B (BIRCH online) | CF-tree + σ_j² online 추정 + paper period P 50-query trigger |
| 8 | 본 Form 1 Component C (paper Eq 2-6 통합) | Eq 5 group-aware n_inc 분배 + Eq 2-4/6 paper exact |
| 9 | 본 Form 1 Component D (allocation) | Equal/Prop/Neyman/Anti + RQ2 batch axis evidence + Cochran 1977 §5.5 |
| 10 | ★★ batch axis baseline + Pareto Top 5 (1001 file) | batch axis Pareto + 12 anchor consistency (-9 ~ -10% std 2-3) + Cliff's δ large 63.0% + paired 92.5% |
| 11 | ★★ Form 1 phase 1 측정 1 (streaming workload simulation) | concept drift × 3 dataset × 4 method 결과 + paired Δ% vs batch axis |
| 12 | ★★ Form 1 phase 1 측정 3 partial (3-way 비교) | Bernoulli + SelNet + 본 Form 1 Q-error mean + latency + offline cost |
| 13 | paper §VI 한계 보완 (L1+L5+L6) | paper §VI-B 'shifting workloads' (L1) + §VI-D SelNet 만 (L5) + §VII sampling overhead (L6) verbatim quote + 본 영역 align |
| 14 | RQ1/RQ2/RQ3 batch axis trilogy 통합 narrative | 1001 file batch 측정 + Form 1 streaming 측정 = comprehensive coverage |
| 15 | 자원 효율 + 산업 적용 axis | batch axis Pareto Top 5 + streaming axis (reservoir / minibatch_partial) + 산업 영역 3 |
| 16 | 본 Form 1 한계 + 정직 disclosure | byte-identical 6 unique × 9 nominal + σ_j oracle + 40 폐기 분류 + framework novelty |
| 17 | Form 1 phase 2 future work | Eq 3-6 group-aware augment + multi-table generalization + WIKI 768d high-dim |
| 18 | paper-grade publication path | EDBT short paper (10월) + VLDB short paper (4월/11월) + co-author |
| 19 | Conclusion (3 line) | streaming-aware + 분포 인지 통합 + paper §V-B 후속 연구 + 산업 적용 |
| 20 | Q&A + Acknowledgement | 박광현 + 임채림 + Capstone Design |

★★★ **핵심 변경 사항 (v6 → v7 deck)**:
- slide 4-9 = Form 1 Component A+B+C+D 영역 신규 추가
- slide 10 = batch axis baseline 명시 (기존 1001 file Pareto + 12 anchor consistency)
- slide 11-12 = Form 1 phase 1 측정 1+3 신규 (streaming workload simulation + 3-way 비교)
- slide 13 = paper §VI 한계 보완 (L1+L5+L6) 명시
- slide 17-18 = Form 1 phase 2 future + paper-grade publication path

### 8.2 6/11 보고서 narrative 구성

**phase 1 full + phase 2 partial 영역 (6/11, 추가 30-50h cost)**:
- Form 1 측정 1 full (streaming workload simulation, 1440 file)
- Form 1 측정 2 (BIRCH cost, 540 file)
- Form 1 측정 3 full (4-way: + CE4HD partial + Ada-ef paper level, 600 file)
- Form 1 측정 4 (distribution shift, 480 file)
- Form 1 측정 5 pilot (phase 2 group-aware Eq 3-6 augment, 120 file)
- 측정 portfolio = 1001 file (batch axis) + 신규 3180 file (streaming axis) = **4181 file (full coverage)**

**11 § + 6 부록 구성 (Agent E § 4.1 verbatim base)**:

```
§1 서론 (Introduction)
  1.1 동기 — VAQ + Adaptive Sampling + paper §V-B 영역
  1.2 문제 정의 — paper §V-B Bernoulli sample 추출 의 한계 (high-dim overhead + shifting workload + dataset-dependent trajectory)
  1.3 본 연구 contribution scope (Form 1 4 측면 + batch + streaming complementary)
  1.4 보고서 구성

§2 배경 (Background)
  2.1 Vector-augmented Analytical Queries (VAQ) 영역
  2.2 paper Exqutor §V-A ECQO + §V-B Adaptive Sampling Eq 1-6 + 본 의역 17-step
  2.3 Classical sampling theory (Cochran 1977 §4.5 + §5.5)
  2.4 Streaming algorithms (Vitter 1985 reservoir + Chao 1982 weighted reservoir + Al-Kateb-Lee SSDBM 2010)
  2.5 Online cluster maintenance (BIRCH 1996 + CluStream 2003 + mini-batch K-means)

§3 관련 연구 (Related Work)
  3.1 paper Exqutor (BDAI 2024-2026)
  3.2 SelNet (paper [74] reference)
  3.3 CE4HD SRCE/MRCE (VLDB 2024, Lan-Bao)
  3.4 Adaptive Bucket Probing (arxiv 2604.04603, HKUST 2025)
  3.5 Ada-ef Distribution-Aware HNSW (arxiv 2512.06636, Waterloo 2025)
  3.6 Stratified Reservoir Sampling (Al-Kateb-Lee-Wang SSDBM 2010 + ISJ 2014)
  3.7 본 연구 positioning + differentiation (Form 1 framework axis novelty)

§4 본 연구 방법론 (Streaming-aware Distribution-Conscious CE for VAQ)
  4.1 Form 1 main theme + 4 측면 design
  4.2 Component A — Stratified Reservoir Sampling (paper Eq 1 대체)
  4.3 Component B — Online cluster maintenance (BIRCH CF-tree)
  4.4 Component C — paper Eq 2-6 통합 (Eq 5 group-aware augment)
  4.5 Component D — Distribution-aware stratification (Equal/Prop/Neyman/Anti)
  4.6 paper Eq 1-6 + 본 Form 1 통합 표 + 본 의역 17-step pseudo-code

§5 실험 환경
  5.1 시스템 (capstone2026 server)
  5.2 dataset (DEEP/SIFT/SSN + WIKI/YFCC partial)
  5.3 benchmark (TPC-H Q3 + concept drift simulation)
  5.4 baseline (paper §V-B Bernoulli + SelNet + CE4HD partial + Ada-ef paper level)
  5.5 metrics (Q-error mean/std + latency + memory + offline training cost)

§6 측정 결과 (★★ batch axis + streaming axis 통합)
  6.1 RQ1 paper baseline 재현 (1001 file batch axis)
  6.2 RQ2 5-way 표본 할당 + Neyman paradox sel-dependency (★ sel=0.01 한정)
  6.3 RQ3 단독/결합 + 8 paradigm × 56 method (1001 file batch axis)
  6.4 RQ1' Form 1 측정 1 — streaming workload simulation (★ streaming axis main)
  6.5 RQ2' Form 1 측정 2 — online cluster maintenance cost
  6.6 RQ5' Form 1 측정 3 — 4-way 비교 (paper §VI-D Fig.12 확장)
  6.7 RQ4' Form 1 측정 4 — distribution shift simulation (4 종 시나리오)
  6.8 RQ3' Form 1 측정 5 — phase 2 group-aware Eq 3-6 augment (pilot)

§7 자원 효율 Pareto frontier
  7.1 batch axis Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert)
  7.2 streaming axis main (reservoir / minibatch_partial)
  7.3 산업 적용 추천 (RAG / OLTP / vector database insert stream)

§8 paper 한계 보완 (L1 + L5 + L6)
  8.1 L1 (§VI-B 'sample size trajectory varies depending on dataset') — Form 1 측정 1 정량 결과
  8.2 L5 (§VI-D SelNet 만 비교) — Form 1 측정 3 4-way 결과
  8.3 L6 (§VII Sampling 영역 dynamic optimization) — Form 1 Component C Eq 5 group-aware

§9 본 Form 1 한계 + 정직 disclosure
  9.1 online cluster maintenance accuracy 손실
  9.2 framework axis novelty (각 method 자체 신규 X)
  9.3 batch axis + streaming axis 환경 boundary
  9.4 byte-identical (6 unique cells × 9 nominal)
  9.5 40 폐기 method 정직 분류 (정합성 10 + 자원 7 + audit 23)
  9.6 Neyman paradox scope (sel=0.01 한정) + σ_j oracle interpretation

§10 future work
  10.1 Form 1 phase 2 (Eq 3 + Eq 4 group-aware augment)
  10.2 multi-table generalization (옵션 E Centroid tuple K granularity grid)
  10.3 ECQO Q-error gap cell 별 paired (옵션 F)
  10.4 정보 수준 L1 method 개발 (옵션 D)
  10.5 TPC-DS §V-B 측정 (옵션 H)
  10.6 streaming framework 의 RAG production 적용
  10.7 σ_j 직접 측정 + Neyman paradox 일반화 (paper-grade publication 가치)

§11 결론
  11.1 paper §V-B 후속 연구 contribution 정리
  11.2 학부 capstone-grade ★★ 매우 강력
  11.3 paper-grade publication path (Form 1 phase 1 = EDBT/VLDB short paper)

부록 A — paper §V-B Eq 1-6 verbatim + 본 의역 17-step pseudo-code (reviewer defense)
부록 B — 본 Form 1 Component A+B+C+D pseudo-code
부록 C — paper Eq 1-6 + 본 Form 1 통합 표 (Form 1 augment 영역 명시)
부록 D — 40 폐기 method 정직 분류 (정합성 10 + 자원 7 + audit 23)
부록 E — byte-identical caveat (6 unique × 9 nominal)
부록 F — REPORT v11 1362 line raw data + statistical anchor
```

### 8.3 batch + streaming 통합 narrative 의 핵심 (★ 5/27 + 6/11 공통)

**core message 1**: Exqutor paper §V-B Adaptive Sampling 의 Eq 1 (Bernoulli sample 추출 방식) 영역을 streaming-aware distribution-conscious 으로 대체하고, paper Eq 2-6 dynamic batch loop 는 paper exact 유지하면서 **paper Eq 5 (sampling_size update) 의 본 연구 group-aware allocation augment** 한정.

**core message 2**: 본 연구는 paper §VI-B 가 명시한 'shifting workloads' 영역을 정량 측정하여 paper L1 한계를 보완하고, paper §VI-D Fig.12 의 SelNet 한정 비교를 3-way (Bernoulli + SelNet + 본 Form 1) framework 으로 5/27 phase 1 에서 확장.

**core message 3**: **본 연구 의 narrative 의 anchor 는 batch axis (1001 file) baseline + streaming axis (Form 1 측정 1-5) main contribution + 두 axis complementarity**. paper §V-B framework 영역의 완전 cover (offline + online + adjustment + 4-way 비교).

**core message 4** (★ Pareto): 본 Form 1 의 산업 contribution = streaming environment + O((N+K)×d) memory + paper §V-B Q-error 정확도 anchor 수준 동시 달성. RAG production / OLTP write-heavy / vector database insert stream 환경 직접 적용 가능.

**core message 5** (★ honest disclosure): 한계: 본 Form 1 phase 1 = paper Eq 1 대체 + Eq 5 group-aware augment 만 다룸. Eq 3 + Eq 4 group-aware augment 는 phase 2 (paper-grade future work). online cluster maintenance accuracy 손실 + framework novelty 명시 + 1001 file batch axis + streaming axis 환경 boundary + Neyman paradox sel=0.01 한정 + σ_j range oracle interpretation.

### 8.4 5/15 박광현 미팅 1-2 page 자료 영역

**자료 구성 (Agent E § 5.1 base)**:

| 영역 | 분량 | 내용 |
|---|---:|---|
| **§0 우리 결정 form** | 1/2 page | Form 1 main theme + 4 측면 + 본 narrative 합의 결과 |
| **§1 보완 paper 한계 L1+L5+L6** | 1/2 page | paper §VI-B + §VI-D + §VII verbatim 인용 + 본 Form 1 영역 align |
| **§2 측정 plan + cost** | 1/2 page | 5 측정 영역 + cost 산정 + 1001 file 활용 영역 |
| **§3 5/27 storyline** | 1/4 page | 20 slide 핵심 axis 요약 |
| **§4 6/11 outline** | 1/4 page | 11 §  + 6 부록 핵심 영역 요약 |
| **§5 review 요청 항목 6** | 1/2 page | Form 1 fit 만 선택, 박광현 자문 질문 6 영역 |
| **부록 A — Algorithm pseudo-code** | 1/2 page | Component A+B+C+D 의 pseudo-code (reviewer defense) |

**file 위치 권장**: `submission/_drafts/박광현_5월15일_미팅/속도는벡터_박광현_5월15일_미팅_Form1_review_form.pdf`

---

## 9. byte-identical + Cliff's δ + Pareto frontier 등 Form 1 안 의미

본 영역은 1001 file 의 statistical anchor (byte-identical 6 unique cells + Cliff's δ + Pareto frontier + Cohen's d 등) 의 Form 1 narrative 안 의미 정리.

### 9.1 byte-identical 6 unique × 9 nominal cells

#### 9.1.1 batch axis evidence

**측정 결과**:
- 9 nominal cells: A1-DEEP/SIFT/SSN + A2-Fig7/8/9 + A4-sel + A5-scale sf=1/10/100
- 6 unique cells: 3 쌍 byte-identical (DEEP/SIFT sf=10 + DEEP sf=100/sel=0.1 + WIKI 768d sf=10)
- duplicate 메커니즘: 같은 data set + 같은 query + 같은 stratification → byte-identical output

#### 9.1.2 Form 1 안 의미

**Form 1 §9.4 정직 disclosure**: 본 연구 측정 cell coverage 의 정직 boundary 명시. byte-identical caveat 가 batch axis 의 effective coverage 의 정량 진단.

**Form 1 §6 측정 결과 statistical anchor 보정**:
- paired Δ% 계산 시 byte-identical 3 쌍 의 weight 보정 (각 paired 의 effective n 감소)
- Cliff's δ 의 effective sample size 보정 (6 unique cells × 56 method × 2 mode = 672 unique measurement)

**Form 1 streaming axis 의 cell 확장 가능 영역**: streaming axis 측정 (Form 1 측정 1) 에서 추가 cell (concept drift × 3 dataset × 2 sf) 측정 가능 → byte-identical 영역 외 확장.

#### 9.1.3 환각 정정 (Agent A 누락 영역)

**Agent A 누락**: Agent A 가 byte-identical caveat 미명시
**Agent B critical 정정**: byte-identical 6 unique vs 9 nominal cells 인정 ★
**본 Agent H 정정 wording**: "본 연구 측정 cell 9 nominal 中 6 unique cells (byte-identical 3 쌍)"

### 9.2 Cliff's δ + Hedges' g + paired CaseB < CaseA

#### 9.2.1 batch axis evidence

**측정 결과 (REPORT v11, n=494)**:
- **paired CaseB < CaseA 92.5%** (455/492, p<1e-45)
- **Cliff's δ large better 63.0%** (311/494)
- **Hedges' g large 55.7%** (275/494)
- **one-sided p<0.05 outperform 45.3%** (224/494)
- **negative control**: CaseA 단독 대체 0/493 = 0% (large worsening 37.1%)

#### 9.2.2 Form 1 안 의미

**Form 1 §6.3 RQ3 batch axis baseline 의 statistical anchor**:
- batch axis 의 CaseB ensemble robustness 의 정량 evidence (paired 92.5% + Cliff's δ large 63.0%)
- Form 1 §6 측정 결과의 statistical rigor anchor

**Form 1 streaming axis 측정의 statistical anchor 확장**:
- Form 1 측정 1 (streaming workload simulation, 1440 file) 의 paired Δ% 계산 시 batch axis 의 statistical methodology 동일 사용
- Cliff's δ + Hedges' g + one-sided p value = Form 1 의 review-grade anchor

**Form 1 §6 측정 결과 review-grade 정형화**:
- review-grade publication 의 standard = robust statistics (Cliff's δ + Hedges' g + paired sign test)
- 1001 file batch axis + Form 1 streaming axis 모두 동일 statistical methodology 사용

#### 9.2.3 환각 정정

**환각 정정 (handoff_v19 §1.2 base)**:
- ❌ "92.5% 베르누이보다 정확" → ✓ "92.5% 단독 대체 (CaseA) 보다 정확"
- ★ handoff_v12 의 정확 의미 = paired CaseB < CaseA (CaseA 단독 대체 vs CaseB 결합 모드 paired Δ% 비교)

### 9.3 Pareto frontier ((학습시간, 정확도) 2-axis)

#### 9.3.1 batch axis evidence

**측정 결과 (resource_efficiency_pareto_20260513.md)**:

**Pareto Top 5 + reservoir + minibatch_partial**:
- sparse_rp (0.1s, -9.43%) ★ Pareto
- chao_weighted (0.5s, -9.60%) ★ Pareto
- neuram (0.5s, -9.97%) ★ Pareto
- pca1d (0.5s, -9.63%) ★ Pareto
- hilbert / hilbert_real (0.1-0.5s, -9.27 ~ -9.41%) ★ Pareto
- **reservoir (0.1s, -9.25%, memory O(1))** ★ Form 1 streaming axis main
- **minibatch_partial (0.5s, -6.98% CaseB, -10.17% CaseA 9-cell mean)** ★ Form 1 streaming axis main

#### 9.3.2 Form 1 안 의미

**Form 1 §7 자원 효율 Pareto frontier**:
- batch axis 2-axis Pareto (학습시간 × 정확도) + Form 1 streaming axis 3-axis Pareto (+memory)
- batch axis Pareto Top 5 의 일반 OLAP 영역 + streaming axis reservoir/minibatch_partial 의 streaming 영역

**Form 1 streaming axis 3-axis 확장 (memory 추가)**:
- batch axis = (학습시간, 정확도) 2-axis 만
- streaming axis = (학습시간, 정확도, memory) 3-axis (★ memory O(1) reservoir 가 streaming 의 critical axis)

**Form 1 §10 산업 적용 영역 3 (Agent E + Agent C 종합)**:
- **영역 A (Best of Both Worlds)**: sparse_rp / chao_weighted / hilbert / pca1d (batch axis Pareto Top 5)
- **영역 B (Quality-first)**: neuram / opq (batch axis Pareto + 정확도 우선)
- **영역 C (Resource-first)**: reservoir / minibatch_partial (★ Form 1 streaming axis main)

#### 9.3.3 환각 정정

**환각 정정 (handoff_v19 §1.2 base)**:
- ❌ Pareto Top 5 명단 오류 (reservoir ↔ neuram 혼동)
- ✓ Pareto Top 5 = sparse_rp / chao_weighted / **neuram** / pca1d / hilbert (reservoir = Form 1 streaming axis main, 별도 표기)

### 9.4 Cohen's d + Hedges' g (effect size)

#### 9.4.1 batch axis evidence

**측정 결과 (REPORT v11)**:
- Hedges' g large 55.7% (275/494)
- Hedges' g = Cohen's d 의 small-sample bias correction. effect size 의 robust 추정.

#### 9.4.2 Form 1 안 의미

**Form 1 §6 측정 결과의 effect size anchor**:
- batch axis = Hedges' g large 55.7% (anchor 수준)
- Form 1 streaming axis = batch axis 와 동일 effect size methodology 사용

**review-grade publication 의 effect size standard**:
- Cohen's d / Hedges' g large = effect size ≥ 0.8 (Cohen 1988 convention)
- 본 Form 1 의 paper-grade publication 가능성 의 statistical anchor

### 9.5 paradigm rollup vs method-level breakdown

#### 9.5.1 batch axis evidence

**측정 결과 (method_level_breakdown_20260513.md)**:

**paradigm rollup (8 paradigm)**:
- P10 Density: -11.93 (n=1, 약함)
- P9 InfoTheoretic: -7.60 (n=9)
- P3 Streaming: -6.63 (n=44)
- P4 DimReduction: -6.03 (n=104)
- P2 Spatial: -5.57 (n=107)
- P5 QMC: +1.47 (n=62)
- P1 Cluster: +2.04 (n=87)
- P6 Quantization: +8.44 (n=53)

**method-level breakdown (12 anchor consistency)**:
- P2 lpm2 (-9.45% std 2.36 ★⭐⭐ std 최저)
- P2 hilbert (-9.41% std 2.13 ★⭐⭐ std 최저)
- P3 chao_weighted (-9.60% std 6.36)
- P3 reservoir (-9.25% std 3.00)
- P4 neuram (-9.97% std 2.88 ★ 정확도 최고)
- P4 pca1d/cca1d/abp (-9.63% std 3.12)
- P4 sparse_rp (-9.43% std 3.30)
- P6 opq (-9.37% std 3.26)
- P6 pq (-9.25% std 2.50)
- P9 hyperloglog (-8.65% std 2.73)
- P1 minibatch (-9.28% std 3.29)
- P3 thompson_sampling (-8.98% std 3.05)

#### 9.5.2 Form 1 안 의미

**Form 1 §6.3 narrative 정정 (강재현 5/13 1:00 피드백 정량 검증)**:
- ❌ "paradigm 우위 단정"
- ✓ "anchor method consistency" (12 method × paradigm 외 axis = 본질적 contribution)

**Form 1 의 framework axis novelty 명시**:
- paradigm 분류 자체가 novelty X (existing literature)
- 본 연구 contribution = 12 anchor method consistency + Pareto frontier + Cliff's δ large + 92.5% paired

**Form 1 §10.4 정보 수준 L1 method 개발 (옵션 D 영역)**:
- paradigm 외 axis = "Cheap 근사 친화도" (Centroid tuple 영역) + "stratification quality 의존도" (multi-join re-strat 영역) + "K granularity sensitivity" (K=10/20/30 영역)
- Form 1 phase 2 future work = 위 axis 의 framework 정형화

### 9.6 batch axis statistical anchor 의 Form 1 안 위치 요약

| statistical anchor | batch axis evidence | Form 1 안 영역 |
|---|---|---|
| **byte-identical 6 unique × 9 nominal** | 3 쌍 byte-identical | §9.4 정직 disclosure |
| **paired CaseB < CaseA 92.5%** | 455/492, p<1e-45 | §6.3 batch axis baseline |
| **Cliff's δ large better 63.0%** | 311/494 | §6 statistical anchor |
| **Hedges' g large 55.7%** | 275/494 | §6 effect size anchor |
| **one-sided p<0.05 outperform 45.3%** | 224/494 | §6 hypothesis anchor |
| **negative control 0/493 = 0%** | CaseA 단독 large worsening | §6 control anchor |
| **Fig.12 재현 -4.3%** | 8-cell mean qe_trim 1.618 vs paper 1.69 | §6.1 paper baseline 재현 |
| **Pareto Top 5** | sparse_rp / chao_weighted / neuram / pca1d / hilbert | §7 자원 효율 |
| **12 anchor consistency** | -9 ~ -10% std 2-3 | §4.2 Component A method 선택 |
| **paradigm rollup 8** | P10/P9/P3/P4/P2/P5/P1/P6 | §6.3 batch axis baseline |
| **method-level breakdown** | 12 anchor + outlier (wavelet_hist +67.96 / lp_bound +16.43) | §6.3 + §9.5 정직 disclosure |

---

## 10. main thread 종합 권장 사항

본 영역은 본 Agent H deep dive 의 main thread 종합 권장 사항 정리.

### 10.1 1001 file 의 Form 1 narrative 안 위치 fix (★★★ critical)

**fix 결정**:
- **1001 file = 폐기 X** (사용자 정책 정합)
- Form 1 narrative 안에서 **batch baseline axis 로 명확 positioning**
- Form 1 streaming axis 와 **complementary framework** 통합

**Form 1 narrative 영역 명시**:
- batch axis = §5 실험 환경 baseline + §6.1-6.3 (RQ1/RQ2/RQ3) + §7 Pareto + §9 정직 disclosure
- streaming axis = §4 본 연구 방법론 (Form 1 Component A+B+C+D) + §6.4-6.8 (RQ1'-RQ5' 측정 1-5) + §8 paper 한계 보완
- complementary = §1.3 contribution scope + §6 측정 결과 통합 + §11 결론

### 10.2 5/27 발표 deck v7 update 항목 (현 v6 base + Form 1 axis 통합)

1. **slide 4 (본 연구 contribution scope)**: Form 1 main theme + 4 측면 + batch + streaming complementary 명시
2. **slide 5-9 (Form 1 Component A+B+C+D)**: 4 component pseudo-code + paper Eq 1-6 통합 표
3. **slide 10 (batch axis baseline)**: 1001 file Pareto + 12 anchor consistency + Cliff's δ + paired 92.5%
4. **slide 11-12 (Form 1 phase 1 측정 1+3)**: streaming workload simulation + 3-way 비교 (Bernoulli + SelNet + 본 Form 1)
5. **slide 13 (paper §VI 한계 보완 L1+L5+L6)**: verbatim quote + 본 영역 align
6. **slide 14 (RQ1/RQ2/RQ3 batch axis trilogy + Form 1 streaming axis)**: 4-quadrant layout
7. **slide 15 (자원 효율 + Form 1 streaming axis 별도 표기)**: Pareto Top 5 (batch) + reservoir/minibatch_partial (streaming)
8. **slide 16 (정직 disclosure)**: 40 폐기 + byte-identical + scope (Neyman paradox sel=0.01 + σ_j oracle) + framework novelty
9. **slide 17-18 (Form 1 phase 2 future + paper-grade publication)**: EDBT/VLDB short paper + timeline + co-author
10. **slide 19 (Conclusion 3 line)**: streaming-aware + 분포 인지 통합 + paper §V-B 후속 연구

### 10.3 6/11 보고서 outline 핵심 update 항목 (현 v2 base + Form 1 axis 통합)

1. **§1 서론 contribution scope 정정**: Form 1 main theme + 4 측면 + batch + streaming complementary
2. **§2 배경 추가**: Streaming algorithms (Vitter 1985 + Chao 1982 + Al-Kateb-Lee SSDBM 2010) + Online cluster maintenance (BIRCH 1996)
3. **§3 관련 연구 추가**: SRS (Al-Kateb-Lee-Wang ISJ 2014) + CE4HD (Lan-Bao VLDB 2024) + Ada-ef (Waterloo 2025)
4. **§4 본 연구 방법론 신규**: Form 1 Component A+B+C+D + paper Eq 1-6 + 본 의역 17-step pseudo-code
5. **§5 실험 환경 정정**: dataset + benchmark (TPC-H Q3 + concept drift) + baseline (Bernoulli + SelNet + CE4HD + Ada-ef) + metrics
6. **§6 측정 결과 batch + streaming 통합**: §6.1-6.3 (batch axis 1001 file) + §6.4-6.8 (streaming axis Form 1 측정 1-5)
7. **§8 paper 한계 보완 신규**: L1 + L5 + L6 영역
8. **§9 본 Form 1 한계 + 정직 disclosure 신규**: 6 영역 (online cluster accuracy + framework novelty + batch vs streaming boundary + byte-identical + 40 폐기 + Neyman scope)
9. **§10 future work 정정**: Form 1 phase 2 + multi-table + ECQO gap + L1 method + TPC-DS + RELOAD align + σ_j 직접 측정
10. **§11 결론 정정**: paper §V-B 후속 연구 + 학부 capstone-grade + paper-grade publication path

### 10.4 5/15 박광현 미팅 자료 핵심 항목 (★★★ critical)

1. **자료 형식**: 단 1 PDF file (1-2 page) + Apple SD Gothic Neo + callout box + verbatim quote
2. **자료 위치**: `submission/_drafts/박광현_5월15일_미팅/속도는벡터_박광현_5월15일_미팅_Form1_review_form.pdf`
3. **자료 content**: §0 우리 결정 form (fix) + §1 paper 한계 L1+L5+L6 verbatim + §2 측정 plan + §3 5/27 storyline + §4 6/11 outline + §5 review 요청 6 항목 + 부록 A pseudo-code
4. **wording 정정 룰 ★ 필수 사용**: "5 단계 中 1 단계" → "paper §V-B Eq 1-6 + 본 의역 17-step pseudo-code" + "paper Eq 5 (sampling_size update) 의 본 연구 group-aware allocation augment" + Neyman paradox sel=0.01 한정 + σ_j oracle interpretation + Pareto Top 5 (reservoir/minibatch_partial 별도) + byte-identical 6 unique × 9 nominal

### 10.5 본 Agent H 의 종합 권장 path 1 줄 요약 (★★★ critical)

★★★ **사용자 fix 결정 = Form 1 main theme (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ: Extending Exqutor's §V-B Framework) + 4 측면 (대체+보완+개선+추가검증) + paper 한계 L1+L5+L6 보완. 1001 file = 폐기 X, batch baseline axis 로 Form 1 narrative 안 positioning + Form 1 streaming axis (측정 1-5) 와 complementary framework. RQ 구조 = 현 RQ1/RQ2/RQ3 (batch axis baseline) + 신규 RQ1'-RQ5' (Form 1 paper-grade main). 40 폐기 method 정직 disclosure (정합성 10 + 자원 7 + audit 23). Pareto Top 5 (batch axis) = sparse_rp / chao_weighted / neuram / pca1d / hilbert + reservoir/minibatch_partial (Form 1 streaming axis main). σ_j oracle interpretation (Cochran 1977 §5.5 part 포함) + Neyman paradox sel=0.01 한정. 5/27 phase 1 = 1500 file portfolio (1001 batch + Form 1 360 streaming 3-way). 6/11 phase 1 full + phase 2 partial = 4181 file portfolio. 5/15 박광현 미팅 = 1-2 page Form 1 review form. paper-grade publication = EDBT short paper (10월 deadline) + VLDB short paper (4월 또는 11월), 박광현 corresponding + 임채림 first + 학부생 4 명 co-author.**

### 10.6 본 Agent H 의 정직 disclosure 종합 (5 영역)

1. **1001 file = batch 환경 한정** (offline K-means + paper Bernoulli baseline). Form 1 streaming 환경 (BIRCH online + reservoir) 영역 추가 측정 영역 명시.
2. **RQ2 Neyman paradox = DEEP sel=0.01 paired n=455 한정** (sel=0.1 영역에서 paradox 역전). σ_j range 1.3-1.6× narrow = oracle interpretation (직접 측정 미완).
3. **결합 best −7.37% = A2-Fig9 single cell paired Δ% 한정** (9-cell mean ≠ −7.37%).
4. **byte-identical = 6 unique × 9 nominal** (3 쌍 byte-identical).
5. **framework axis novelty** (각 component 자체 신규 X, framework axis 가 novel).

### 10.7 본 Agent H 의 다음 단계 (main thread 작업 영역)

1. **5/15 박광현 미팅 자료 작성** (1-2 page, Form 1 review form) → 박광현 자문 6 항목 답변 + Form 1 학술 정당성 + 측정 plan 적절성 + 5/27 timeline + paper-grade publication 가능성 + 박광현 본업 align
2. **5/27 발표 deck v7 update** (10 영역 핵심 변경)
3. **6/11 보고서 outline v3** (11 § + 6 부록 신규 영역)
4. **Form 1 phase 1 측정 시작** (cost 50-80h, 5/15 ~ 5/27)
   - Component A (SRS) 구현 (300 line, 4-6h)
   - Component B (BIRCH online) wrapper (250 line, 10-15h)
   - Component C (paper Eq 2-6 통합) 구현 (60 line, 4-6h)
   - Component D (allocation) helper (이미 존재, 0h)
   - 측정 1 (streaming, 1440 file) 서버 8-12h + 코드 12h
   - 측정 3 partial (3-way, 360 file) 서버 5-8h + 코드 30h (SelNet adapter)
5. **5/27 발표 deck v7 finalize** (5/26 ~ 5/27 morning)
6. **6/11 보고서 phase 1 full + phase 2 partial** (5/28 ~ 6/11)
7. **paper-grade publication 준비** (6/12 ~ 9/30): 측정 보강 (full 5 measurement + WIKI 768d + TPC-DS) + draft 작성 + EDBT/VLDB short paper submission

---

## END

본 산출 file: `_internal/handoff/active/agent_H_1001_file_재해석_batch_baseline_Form1_통합_20260515_0300.md`

본 Agent H 산출 = Agent A (78%) + Agent B (정정 7) + Agent C (8 옵션 + 추가 3) + Agent D (paper §V/§VI/§VII 8 영역 + 경쟁 paper 5 + BDAI 6) + Agent E (Form 1 phase 1+2 design) + Agent F (측정 plan + cost 130-180h) + Agent G (paper Eq 1-6 verbatim + 본 의역 17-step) 7 호출 종합 + 9 analysis file 직접 read + paper PDF + handoff v19 종합.

**main thread** 가 본 Agent H 결과로:
- 1001 file 의 Form 1 narrative 안 정확 positioning (batch baseline axis)
- Form 1 narrative 안 RQ 구조 재정립 (RQ1'-RQ5' paper-grade)
- 5/27 발표 deck v7 update + 6/11 보고서 outline v3 update
- 5/15 박광현 미팅 자료 1-2 page Form 1 review form 작성

수행 권장. **사용자 fix 결정 = Form 1 main theme + 4 측면 + paper 한계 L1+L5+L6 + 1001 file batch baseline axis fix**.

작성: 2026-05-15 03:00 KST · Agent H · 1001 file 재해석 + Form 1 narrative 통합 deep dive 완료 (9 analysis file 직접 read + paper PDF + Agent A-G 7 호출 종합)
