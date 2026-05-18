# 속도는벡터 — 본 연구 narrative v6 draft (Phase A)

> 작성: 2026-05-16 KST · v5 (5/15 21:00) base + handoff v31 박세은 framing 단순화 의도 + prompt v11 (5/16 00:50) 완전 반영
> 핵심 reframing: **"cardinality 추정" 표현 모두 제거 + "Sample Selection" 일관 통일**
> 우리 contribution layer 와 paper 영역 layer 명확 분리
> 본 v6 = Phase A partial draft (즉시 작성 가능 9 § + 부록 §A) · chain 의존 § (§6/§8/§10-§13) 는 placeholder + chain 완료 후 추가 작성

---

## 0. 본 연구 main theme

본 연구의 main theme 은 **"Distribution-aware Sample Selection for VAQ Cardinality Estimation"** 이다. paper Exqutor (arXiv:2512.09695v2) §V-B Adaptive Sampling 의 cardinality 추정 mechanism 은 paper 본인 contribution 영역으로 그대로 유지한다. 본 연구의 영역은 그 estimation 의 **input 인 sample selection 영역만** 이다. 즉 paper 의 Bernoulli random sampling 자리에 분포 인지 sample selection method 를 augment 하여, sample 의 quality 가 estimation accuracy (Q-error) 에 미치는 영향을 정량 검증한다.

---

## 1. ★ framing layer 분리 (NEW v6)

### 1.1 두 layer 의 명확 분리

본 연구의 framing 은 **paper 영역** 과 **우리 영역** 두 layer 로 명확 분리된다. 본 분리는 박세은 5/16 00:18 정리 의도 ("우리는 추가 method 통해서 Q-error 만 보완하면 되는 게 아니냐. 카디널리티 추정은 알아서 할거고") 의 직접 반영이다.

| layer | 영역 | 본 발표 영역 |
|---|---|---|
| **paper 영역 (그대로 유지)** | (a) §V-A ECQO HNSW range query 영역 (b) §V-B Adaptive Sampling Eq 1-6 보정 영역 (c) cardinality 추정 mechanism 자체 | 간단 소개 (paper Exqutor 본인 contribution 인정) |
| **우리 contribution 영역** | (a) Phase 1 = 분포 인지 sample selection (sample 추출 mechanism) (b) Phase 2 = dynamic 할당 mechanism (Type 별 best method 자동 선택) (c) Phase 3 의 결합 영역만 = est_b1 + est_method 산술 평균 (minimal augmentation) | 본 발표 핵심 |

### 1.2 narrative 표현 통일 (★ 본 v6 모든 § 일관)

본 v6 narrative 는 다음 표현 통일 룰을 모든 § 에 일관 적용한다.

- ✗ 사용 금지: "cardinality 추정 우리 영역 contribution" / "estimation algorithm 우리 영역 개선" / "분포 인지 추정"
- ✓ 사용 강조: "sample selection 영역 우리 영역" / "분포 인지 sample 추출" / "Q-error 영역 paired Δ% 개선"
- "augmentation" / "augment" 표현 = paper §V-B base 위 우리 sample selection 추가 (대체 X, 추가)
- "결합 영역" = est_final = (est_b1 + est_method) / 2.0 산술 평균만 (minimal, paper exact 위반 X)

### 1.3 본 framing 의 학술 의의

paper 본인 contribution 영역 (cardinality 추정 mechanism) 을 그대로 인정 + 우리 영역 (sample selection augment) 만 정량 검증 영역. 학부 capstone 이론 검증 자세 일관 + 본 발표 톤 정확. 두 layer 의 명확 분리 가 본 v6 narrative 의 base axis 다.

---

## 2. paper 영역 § 흐름 (간단 소개)

### 2.1 §V-A ECQO HNSW range query

paper §V-A 영역 ECQO (Extended Cardinality Query Optimizer) 는 인덱스 있을 때 HNSW (Hierarchical Navigable Small World) range query 영역 정확 cardinality 1-2ms 수준 영역 정확도 달성 mechanism. 본 영역은 paper 본인 contribution + 본 발표 영역 X (간단 소개만).

### 2.2 §V-B Adaptive Sampling (Eq 1-6 verbatim)

paper §V-B 영역 Adaptive Sampling 은 인덱스 없을 때 Bernoulli random sample N=385 + Eq 1-6 momentum 보정 영역 cardinality 추정 mechanism. paper 의 핵심 6 식은 다음과 같다.

```
Eq 1: N = ⌈z²·P̂(1-P̂)/e²⌉ = 385       (sample budget, z=1.96 / P̂=0.5 / e=0.05)
Eq 2: Ĉ = Σ (matching rows) × (1 - sampling_ratio)   (Bernoulli estimator)
Eq 3: δ = max(true_Q-err, 1/true_Q-err)              (Q-error)
Eq 4: η ← m·η + (1-m)·δ/α                            (momentum update, m=0.9 / α=50)
Eq 5: N_t+1 ← N_t × (1 + η·β·sign(...))              (sample size update, β=1.5)
Eq 6: η ← η · γ                                       (learning rate decay, γ=0.99)
```

period P=50 query 마다 Eq 4-6 update. paper 영역 = 본 6 식 verbatim 100% 정합 유지 + 본 연구 영역 contribution X. **본 발표 영역 = paper 영역 그대로 인정 + 간단 소개만**.

---

## 3. ★ 우리 영역 3 phase 흐름 (NEW v6)

### 3.1 Phase 1: 분포 인지 stratification (★ 우리 영역 sample selection)

데이터셋 load 시 (offline, 1회) sample selection 영역 stratification 단계.

- ① **Type 판별** (row 수 / structure / dim) — Type 1/2/3/4a/4b 분류 (§4)
- ② **Type 별 best sample selection method 자동 선택** (dynamic 할당 mechanism, §7)
- ③ **K=20 stratum 영역 sample selection** (16 method 中 dynamic 선택, §5)
- 결과: row → sid 0..K-1 (stratum_id 매핑)

본 Phase 1 = 본 연구 영역 핵심 contribution 영역 first half. 데이터셋 진입 시 분포를 빠르게 catch + stratification 결정 (§9 fit_time 11.9× evidence).

### 3.2 Phase 2: sample 추출 (★ 우리 영역 sample selection)

쿼리 진입 시 (online, 매 query) sample selection 영역 추출 단계.

- ① **sample budget N=385** (paper Eq 1, verbatim) — paper 영역 그대로 유지
- ② **각 stratum 비례 sample 추출** (proportional allocation, K=20)
- ③ **추출된 sample 영역 → est_method 계산** (matching × weight)

본 Phase 2 = 본 연구 영역 핵심 contribution 영역 second half. paper 의 sample budget 영역 그대로 유지 + 추출 mechanism 영역만 분포 인지 stratification 영역 base 위 변경.

### 3.3 Phase 3: 결합 minimal (minimal augmentation)

쿼리 진입 시 (online, 매 query) 결합 단계. **★ minimal augmentation — paper 영역 위반 X**.

- ① **est_b1** = paper Bernoulli random sample est (paper 영역 그대로)
- ② **est_method** = 우리 sample selection method est (★ 우리 영역)
- ③ **est_final = (est_b1 + est_method) / 2.0** ★ 산술 평균 결합 (minimal)
- ④-⑦ **paper Eq 2-6 verbatim 영역 보정** (그대로 유지, paper 영역)

본 Phase 3 의 결합 영역만 우리 영역 (산술 평균). paper Adaptive Eq 1-6 영역은 그대로 유지 → minimal augmentation. CaseB ensemble = 본 Phase 3 의 직접 instantiation.

### 3.4 3 phase 의 본 연구 axis

Phase 1+2 = 우리 영역 sample selection 핵심 contribution. Phase 3 = paper Adaptive Eq 1-6 영역 그대로 유지 + 결합 영역만 minimal augmentation. **paper 영역 cardinality 추정 mechanism 영역 그대로 유지 + 우리 영역 sample selection 영역 추가** 가 본 v6 narrative 의 핵심 framing 이다.

본 3 phase 흐름은 본 v6 narrative 의 모든 후속 § 의 base axis. §4 (데이터셋 4 type) + §5 (paradigm 별 method) + §7 (dynamic 할당) + §9 (fit_time) 모두 Phase 1+2 영역 구체화.

---

## 4. 데이터셋 4 type 분류 (★ 박세은 정리 #3 + 박광현 input 1)

### 4.1 분류 기준 — scale × structure × dimension

본 §4 는 본 연구의 핵심 contribution axis 다. 1352 file 측정 portfolio 의 9 cell 을 데이터셋 특성 (scale × structure × dimension) 기준으로 **5 type (Type 1/2/3/4a/4b)** 으로 분류한다. 본 axis 가 §7 dynamic 할당 mechanism 의 직접 base.

| Type | 정의 | dim | 본 측정 cell |
|---|---|---:|---|
| **Type 1** | small single sf=1 (0.1M rows) | 96~768 | DEEP/SIFT/SSN/WIKI/YFCC A5-sf1 + v6/v7 |
| **Type 2** | medium single sf=10 (1M rows) | 96~768 | DEEP/SIFT/SSN/WIKI A5-sf10 + v6 |
| **Type 3** | large single sf=100 (10M rows, 저-중차원) | 96~256 | DEEP/SIFT/SSN A1 |
| **Type 4a** | large multi 224-288d (10M rows) | 224~288 | DEEP+SIFT/DEEP+YFCC |
| **Type 4b** | large multi 864d (10M rows) | 864 | DEEP+WIKI |

### 4.2 Type 1 — small single sf=1

데이터 규모 0.1M rows + single-table + 저~고 차원 영역. 본 측정 영역 가장 작은 scale. 분포 인지 sample selection 효과 영역 가장 강력 발현 (chao_weighted K=20 −14.11% best, §7 dynamic 할당). small data 영역 random Bernoulli 의 variance 영역 큰 → 분포 인지 stratification 영역 효과 amplify.

### 4.3 Type 2 — medium single sf=10

데이터 규모 1M rows + single-table + 저~고 차원 영역. 본 측정 영역 sf 중간 영역. 분포 인지 sample selection 효과 영역 sweet spot 약화 (chao_weighted K=20 −6.00%, sf=1 / sf=100 의 절반 수준). paper §VI-B "shifting workloads" 명시 align — sample size trajectory varies depending on the dataset. **데이터 크기 sweet spot 가 sf=1 와 sf=100 양 끝에 있다는 evidence**.

### 4.4 Type 3 — large single sf=100 (저-중차원)

데이터 규모 10M rows + single-table + 96-256d 영역. 본 측정 영역 paper §VI-A 의 default scale 영역. 분포 인지 sample selection 효과 영역 다시 강력 발현 (chao_weighted K=20 −12.20% / sparse_rp K=20 −11.20%). large single 영역 K=20 sweet spot 일관. paper Fig 12 mean Q-error 1.69 영역 baseline → 우리 1.618 (-4.3% 재현) 영역 paper exact 정합 영역.

### 4.5 Type 4a — large multi 224-288d

데이터 규모 10M rows + multi-table + 중차원 224-288d 영역. 본 측정 영역 multi-join cardinality estimation 영역. 분포 인지 sample selection 영역 hilbert_real K=30 영역 slight edge (Pareto Top 5 中 선택 영역). paper §VI-A Fig 7 영역 align — multi-table 환경 영역 sample selection 영역 효과 영역 dim-dependent.

### 4.6 Type 4b — large multi 864d

데이터 규모 10M rows + multi-table + 고차원 864d 영역. 본 측정 영역 가장 challenging scale. 분포 인지 sample selection 영역 Centroid tuple 결합 영역 −7.37% best 발현 (학습 비용 추가 0). 고차원 multi-table 영역 학습 비용 0 의 Centroid tuple 안정 best — 자원 효율 강점. paper §VI-A Fig 9 영역 align — 고차원 multi-table 환경 영역 추가 학습 영역 비효율 + Centroid tuple 영역 강점.

### 4.7 4 type 분류 → dynamic 할당 axis

본 4 type 분류 영역 = §7 dynamic 할당 mechanism 영역 직접 base. 데이터셋 진입 시 Type 판별 (Step 1-2) → Type 별 best sample selection method 자동 선택 (Step 3) → CaseB ensemble (Step 4) 영역 flow. **각 Type 영역 best sample selection method 자동 선택 영역이 본 연구 핵심 contribution**.

---

## 5. ★ paradigm 별 사용 16 sample selection method (NEW v6)

본 §5 는 본 v6 narrative 영역 사용 16 sample selection method 영역 paradigm 별 정리 영역. 7 paradigm 영역 covering — Cluster (3) / Spatial (3) / Streaming (1) / DimReduction (4) / QMC (2) / Quantization (2) / InfoTheoretic (1). 모두 **sample selection 영역 mechanism** — cardinality 추정 algorithm 영역 X. 폐기 40 method 영역 narrative 미언급 (사용자 5/15 결정).

| Paradigm | 사용 method | count |
|---|---|---:|
| **P1 Cluster** | minibatch_partial / gmm / faiss_ivf | 3 |
| **P2 Spatial** | hilbert_real ★ / zorder_morton / skilling_hilbert | 3 |
| **P3 Streaming** | chao_weighted ★ | 1 |
| **P4 DimReduction** | sparse_rp ★ / pca1d ★ / rsvd / ica_fastica | 4 |
| **P5 QMC** | cum_sqrtf / lavallee_hidiroglou | 2 |
| **P6 Quantization** | rabitq_strat / mhist2 | 2 |
| **P9 InfoTheoretic** | hyperloglog ★ | 1 |

★ = Pareto Top 5 (정확도 best = 자원 best, §6).

### 5.1 P1 Cluster (3 method) — sample 영역 cluster center 매핑

- **minibatch_partial** (Sculley 2010 KDD): MiniBatchKMeans + `partial_fit` (sub-batch 단계별 학습). sample → cluster center → stratum_id.
- **gmm** (Dempster-Laird-Rubin 1977 EM, JRSS): Gaussian Mixture Model with EM. 본 측정 영역 `covariance_type='diag'` + `reg_covar=1e-2` (SIFT 128d / SSN 256d cholesky fail 회피).
- **faiss_ivf** (Johnson-Douze-Jégou 2017 FAISS, IEEE): IVF (Inverted File Index) — vector → cluster center 영역 nearest 매핑.

### 5.2 P2 Spatial (3 method) — sample 영역 spatial curve 1D scalar → quantile 분할

- **hilbert_real ★** (Faloutsos 1989 PODS, Pareto Top 5): Hilbert curve indexing — high-D vector → 1D scalar 매핑. ★3 정정 후 raw Wikipedia Hilbert curve 표준 구현 (PCA-2D-lex sort alias 정정 후, 부록 §A-? 참조).
- **zorder_morton** (Morton 1966 IBM): Z-order space-filling curve — bit interleaving.
- **skilling_hilbert** (Skilling 2004 AIP): state-machine algorithm — true high-D Hilbert curve.

### 5.3 P3 Streaming (1 method, ★ Pareto Top 5)

- **chao_weighted ★** (Chao 1982 *Biometrika*): Weighted reservoir sampling (priority queue base). vector → weight 부여 (예: norm or anomaly score) → priority queue (size K=20) → weighted random sample → stratum 부여 → sid. 시간 O(n × log K) + 메모리 O(K) compact. 본 연구 영역 Pareto Top 5 — Type 1 small sf=1 best −14.11%.

### 5.4 P4 DimReduction (4 method) — sample 영역 low-D projection → quantile 분할

- **sparse_rp ★** (Li-Hastie-Church 2006 KDD, Pareto Top 5): Very Sparse Random Projection (Achlioptas 2003 → Li-Hastie-Church 2006 정정). fit_time 3.67s 최단.
- **pca1d ★** (Pearson 1901 Phil. Mag., Pareto Top 5): PCA → 1D 영역 projection. 10/10 textbook audit pass.
- **rsvd** (Halko-Martinsson-Tropp 2011 SIAM Rev.): Randomized SVD — large-scale PCA 영역.
- **ica_fastica** (Hyvärinen 1999 IEEE TNN): FastICA — non-Gaussian independence 영역.

### 5.5 P5 QMC (2 method) — sample 영역 stratification

- **cum_sqrtf** (Dalenius-Hodges 1959 JASA): Minimum Variance Stratification (cum √f).
- **lavallee_hidiroglou** (Lavallée-Hidiroglou 1988 Survey Methodology): take-all stratum + Neyman allocation.

### 5.6 P6 Quantization (2 method) — sample 영역 quantization

- **rabitq_strat** (Gao-Lin 2024 VLDB Best Paper): RaBitQ — sign-based quantization.
- **mhist2** (Poosala 1997 VLDB): MHIST — multi-dimensional histogram.

### 5.7 P9 InfoTheoretic (1 method, ★ Pareto Top 5)

- **hyperloglog ★** (Flajolet-Fusy-Gandouet-Meunier 2007 AofA): HyperLogLog — sketch (★ 영역 활용 = sample selection 영역 stratum 부여). 메모리 O(m × log log n) 매우 compact.

★ **영역 주의**: HyperLogLog 영역 자체 = paper 영역에서 cardinality estimation sketch 영역 알려진 algorithm. **본 연구 영역 = 이 sketch 결과 영역 sample selection stratum 부여 영역에 활용** (cardinality estimation 영역 contribution X). HyperLogLog 결과 = 우리 영역 sample selection mechanism 의 input 영역.

---

## 6. Q-error 영역 정확도 (sample selection vs random Bernoulli) — sample selection 영역 Q-error 개선

> ★ **본 § = chain 의존 영역 (v8/v9 chain 완료 후 추가 작성)**. 본 v6 draft 영역 v5 carry-over base + chain 완료 후 update 명시.

본 §6 은 1001 file paper exact base 측정 portfolio 의 sample selection 영역 Q-error 영역 정확도 (sample selection vs random Bernoulli) paired Δ% 직접 evidence. 본 영역은 우리 영역 sample selection 영역 augment 영역 정량 가치 영역 검증 — paper 영역 cardinality 추정 mechanism 영역 그대로 유지 + sample 영역 quality 영역 estimation accuracy (Q-error) 에 미치는 영향 영역만.

### 6.1 negative control — CaseA 단독 대체 (대체 가설 폐기)

paper §V-B 의 Bernoulli random sampling 을 우리 영역 sample selection method 영역 단순 대체 (K=20 cluster stratified reservoir). 9 측정 환경 전반 안정 우위 영역 평균 개선폭 −5 ~ −12% range 발현. 단독 best = **minibatch_partial −10.17%** (A2-Fig8).

negative control: CaseA 단독 대체 모드 영역 large worsening = **37.1%** 발현 + 일부 단독 대체 효과 영역 **0/493 = 0%** (단독 대체 가설 폐기). 단독 대체 효과 영역 method 선택에 따라 양 방향 큰 변동 영역. 본 negative control 영역 = **단독 대체 가설 폐기** + 결합 minimal augmentation 영역 evidence base.

### 6.2 sample selection vs random Bernoulli paired Q-error Δ% (CaseB ensemble)

paper §V-B Bernoulli 추정값과 우리 sample selection method 추정값 영역 산술 평균 (est_final = (est_b1 + est_method) / 2.0) 영역 결합. 492 paired 비교 中 **92.5% (455/492, p<1e-45)** 가 random Bernoulli single 보다 정확 (sample selection 결합 minimal 우위).

paired effect size 통계:
- Cliff's δ large better = **63.0%** (311/494)
- Hedges' g large = **55.7%** (275/494)
- one-sided p<0.05 outperform = **45.3%** (224/494)

결합 best = **Centroid tuple −7.37%** (A2-Fig9, Type 4b). α sweep evidence: 4 method 中 3 (sparse_rp / chao_weighted / hilbert_real) 이 α=0.5 (산술 평균) 에서 best — minimal augmentation 영역 ensemble weight 영역 산술 평균 영역 정합.

### 6.3 method base — 4 component framework (sample selection 영역)

본 sample selection 영역 framework 영역 4 component 통합 (모두 sample selection 영역, cardinality 추정 algorithm X):

- **Component A** (Stratified Reservoir Sampling) = Vitter 1985 + Al-Kateb 2014 — sample selection 영역 reservoir mechanism. paper §V-B Eq 1 Bernoulli 자리 영역 augment.
- **Component B** (BIRCH CF-tree) = Zhang SIGMOD 1996 — CF tuple 의 σ_j² 영역 sample selection 영역 stratification 입력. batch axis 자원 한계 영역 폐기, CF tuple 형식만 Component C 입력.
- **Component C** (paper Eq 2-6 통합) = paper §V-B Eq 1-6 verbatim 100% 정합 — paper 영역 mechanism 영역 그대로 유지.
- **Component D** (Distribution-aware stratification) = Cochran 1977 §5.5 — sample selection 영역 4 mode (Equal / Proportional / Neyman / Anti-Neyman).

> **TBD (chain 완료 후 update)**: v8 (12 cell × 16 method × CaseB = 192 file) + v9 (20 cell × 2 sel × 17 = 680 file) chain 완료 후 sample selection vs random Bernoulli paired Q-error Δ% 통계 영역 update + cell × method 안정성 매트릭스 추가 + selectivity-dependent paradox 영역 update.

---

## 7. ★ dynamic 할당 mechanism flow (sample selection 영역만 dynamic)

### 7.1 본 §7 의 base axis

본 §7 은 §4 의 4 type 분류 + §5 의 paradigm 별 method 매핑 base 위에서 **dynamic method selection flow** 를 제안한다. 본 §7 = 본 연구 핵심 contribution 영역 directly. **★ dynamic 영역 = sample selection 영역만**. paper Adaptive Eq 1-6 영역 = 그대로 유지 (dynamic X).

### 7.2 4-step flow

```
[데이터셋 진입]
        ↓
[Step 1] dataset profile 파악
  - row 수 (sf=1 / sf=10 / sf=100)
  - table 구조 (single / multi)
  - dimension (저 96d / 중 256d / 고 864d)
        ↓
[Step 2] Type 판별
  - Type 1/2/3/4a/4b 中 1
        ↓
[Step 3] Type 별 권장 sample selection method 자동 선택
  - Type 1 (small single sf=1) → chao_weighted K=20 (-14.11%)
  - Type 2 (medium single sf=10) → chao_weighted K=20 (sweet spot 약함)
  - Type 3 (large single sf=100) → chao_weighted / sparse_rp K=20 (-11~-12%)
  - Type 4a (large multi 224-288d) → hilbert_real K=30
  - Type 4b (large multi 864d) → Centroid tuple (-7.37%)
        ↓
[Step 4] CaseB ensemble (★ 우리 영역 결합 minimal)
  - est_final = (est_b1 + est_method) / 2.0
  - 실험군 = paper Bernoulli + dynamic 선택 sample selection method
        ↓
[paper §V-B Adaptive Eq 1-6 보정 (그대로 유지, paper 영역)]
```

### 7.3 dynamic 할당 mechanism 의 본 연구 axis

본 4-step flow 영역 핵심 axis = **Type 별 best sample selection method 자동 선택**. 데이터셋 진입 시 Type 판별 (Step 1-2) 영역 fit_time cost = sparse_rp 3.67s 영역 fast profiling (§9). Step 3 영역 Type 별 권장 method 영역 fit_time = 3.67s ~ 43.50s range (Pareto Top 5).

**영역 주의**: Step 4 영역 CaseB ensemble = est_b1 + est_method 산술 평균 (Phase 3 minimal augmentation, §3.3). paper Adaptive Eq 1-6 영역 = Step 4 다음 영역 그대로 유지. dynamic 영역 = Step 1-3 영역 sample selection method 선택 영역만 + Step 4 ensemble 결합 영역만. paper 영역 mechanism 영역 dynamic X.

### 7.4 4-stage chain (1280 file) 영역 evidence base

본 dynamic 할당 mechanism 영역 evidence base = 4-stage chain 측정 portfolio:
- v6_caseB (Pareto Top 5 + B1 × 9 cell, 50 file) — 5/16 00:17 COMPLETE
- v7_extras (3 cell × Pareto Top 5 + B1, 18 file) — 5/16 ~02:00 진행 중
- v8_full (12 cell × 16 method × CaseB, 192 file) — 5/17 새벽 chain
- v9_sel_sweep (20 cell × 2 sel × 17 method, 680 file) — 5/18 새벽 chain

본 chain 완료 후 §7.5 (Type × method best 매트릭스 update) + §6 (paired Δ% 통계 update) + §10-§13 chain 의존 § 추가 작성 영역.

---

## 8. plan robustness across environment variability (★ 박광현 input 6)

> ★ **본 § = chain 의존 영역 (v9 chain 완료 후 추가 작성)**. 본 v6 draft 영역 v5 carry-over base + chain 완료 후 update 명시.

박광현 5/15 미팅 input 6 ("순서 바뀌지 않을 정도 정의 어려움 — 테이블 사이즈, 숫자 등 변수가 너무 많음") 영역 본 연구 측정 evidence 영역.

### 8.1 plan robustness 정의

본 §8 의 plan robustness 정의: **9 측정 환경 (dataset / sf / sel / dimension / multi-table) × 16 사용 sample selection method 영역 sample selection vs random Bernoulli paired Q-error Δ% 안정성**. 본 정의 영역 base = §6 결합 minimal augmentation 영역 92.5% paired 우위 영역.

sample selection vs random Bernoulli paired Q-error Δ% 우위 = **92.5%** (455/492) — 환경 / method 가 어떻게 변하든 약 92.5% 영역 확률로 sample selection 결합 minimal 영역 random Bernoulli single 영역 우위. negative control (CaseA 단독 대체) 영역 large worsening = 37.1% 대비 sample selection 결합 minimal 모드 영역 변동성 감소 영역 plan robustness 영역 직접 evidence.

### 8.2 Neyman selectivity-dependent paradox (sub-evidence)

| selectivity | Neyman | Anti-Neyman | Proportional | best |
|---|---:|---:|---:|---|
| sel=0.01 | 1.595 | 1.540 | 1.580 | **Anti < Prop < Neyman** (paradox) |
| sel=0.10 | 1.1076 | 1.1101 | 1.1135 | **Neyman < Anti < Prop** (classical 정합) |

sel=0.01 paradox 해석: 본 dataset 영역 cluster 간 σ_j range 1.3-1.6× narrow (Cochran 1977 §5.5 Neyman 가정 不만족) + N_i CV=0 (cluster size 균등) 영역 두 가정 不만족. selectivity 환경 variability 영역 plan 결정을 변동시키는 직접 evidence.

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify (부록 §A-7 carry-over).

> **TBD (chain 완료 후 update)**: v9 sel sweep (20 cell × 2 sel × 17 method = 680 file) chain 완료 후 plan robustness 영역 update — sel=0.001 / sel=0.01 / sel=0.10 영역 cell × method sample selection vs random Bernoulli paired Δ% heatmap + 안정성 매트릭스 + selectivity-dependent paradox 영역 update.

---

## 9. 분포 catch speed — fit_time 11.9× range

### 9.1 본 §9 의 base evidence

박세은 정리 #2 ("데이터셋 진입 시 빠르게 분포 catch") + 박광현 input 3 ("분포를 빠른 시간 안에 catch") 의 직접 evidence. 5/15 fit_time 직접 측정 (Pareto Top 5 sample selection method × 9 cell × 2 mode = 90 file 모두 fit_time_sec 정상 회수).

### 9.2 Pareto Top 5 sample selection method × fit_time

| Method | n | fit_time mean | range | cache_time mean |
|---|---:|---:|---|---:|
| **sparse_rp ★** | 18 | **3.67s** | 0.35 ~ 8.64s | 10.64s |
| chao_weighted ★ | 18 | 8.42s (5/15 update 9.40s) | 0.12 ~ 28.34s | 10.11s |
| hyperloglog ★ | 18 | 12.31s | (TBD) | (TBD) |
| pca1d ★ | 18 | 19.97s (slide 23.50s) | 0.81 ~ 68.18s | 10.77s |
| **hilbert_real ★** | 18 | **43.50s** | 1.40 ~ 100.04s | 10.04s |

### 9.3 fit_time 11.9× range 의 해석

fit_time range = sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× 차이**. cache_time mean 약 10s (method 무관, vector dimension 의존). 9 cell × 2 mode 직접 측정으로 SF=1 / SF=10 / SF=100 axis 모두 cover.

★ 영역 주의: **"분포 catch" = sample selection 영역 stratification 시간** (cardinality estimation 영역 X). sparse_rp 영역 fit_time 3.67s 영역 sample selection 영역 stratification 영역 최단 시간 영역 강점.

### 9.4 산업 환경 분포 catch 속도 axis

산업 환경 분포 catch 속도 제약 시 sparse_rp (3.67s) 가 hilbert_real (43.50s) 대비 12× 빠르면서도 정확도는 동일 Pareto frontier (§6) 에서 동시 best 발현. 메모리는 모두 O(K × d) 이하, reservoir 영역 (chao_weighted) 데이터 크기와 무관한 상수 O(K). 모바일 / 임베디드 / 스트리밍 환경 직접 적용 가능 finding.

박세은 5/14 9:27 자문 답변: 본 fit_time 영역 sample selection method 학습 시간 영역 + 매 query 마다 fit X 영역 (paper period P=50 가정에서 P 회 query 마다 1 회 또는 데이터 변경 시 incremental fit). 본 fit_time 영역 = Phase 1 (offline, 1 회) 영역 비용.

---

## 10. 결합 한계 — negative control (대체 가설 폐기)

> ★ **본 § = chain 의존 영역 (v8/v9 chain 완료 후 추가 작성)**. 본 v6 draft 영역 v5 carry-over base + chain 완료 후 update 명시.

본 §10 의 핵심 finding: **negative control (대체 가설 폐기)** — paper §V-B 의 random Bernoulli sampling 영역 우리 영역 sample selection method 영역 단순 대체 (CaseA) 영역 결과 영역 한계 영역 직접 evidence.

### 10.1 negative control 결과

CaseA 단독 대체 모드 영역 9 측정 환경 × 16 사용 sample selection method 영역 large worsening 발현 = **37.1%**. 일부 측정 영역 단독 대체 효과 영역 **0/493 = 0%** (대체 가설 폐기). paper §V-B 의 paper 영역 mechanism 영역 그대로 유지 + 우리 영역 sample selection 영역 단순 대체 영역 안정 X.

### 10.2 결합 한계 의 framing 영역 의의

본 negative control 영역 본 v6 narrative 의 framing layer 분리 (§1) 영역 직접 정합. **paper 영역 mechanism 영역 단순 대체 X + 결합 minimal augmentation 영역 valid** — paper §V-B 의 cardinality 추정 mechanism 영역 본 paper 영역 그대로 유지 + 우리 영역 sample selection 영역 augment (산술 평균 결합) 영역만 의의 있는 영역 확정.

> **TBD (chain 완료 후 update)**: 5/15 chain CaseA 폐기 (757 file rm) 영역 narrative 영역 update — chain v8/v9 완료 후 CaseB only 영역 paired uplift 직접 evidence 영역 추가.

---

## 11. 결합 진짜 가치 — 안정성 + 변동성 감소

> ★ **본 § = chain 의존 영역 (v9 chain 완료 후 추가 작성)**. 본 v6 draft 영역 v5 carry-over base + chain 완료 후 update 명시.

본 §11 의 핵심 finding: 결합 minimal augmentation (CaseB ensemble) 영역 진짜 가치 = **안정성 + 변동성 감소**. §6 의 sample selection vs random Bernoulli paired Q-error Δ% 우위 92.5% 영역 base 위에서 결합 영역 본 가치 영역 직접 evidence.

### 11.1 안정성 evidence

sample selection vs random Bernoulli paired Q-error Δ% 우위 = 92.5% (455/492, p<1e-45) — 9 측정 환경 × 16 사용 sample selection method 영역 약 92.5% 환경 영역 결합 minimal augmentation 영역 random Bernoulli single 영역 안정 우위. 본 안정성 영역 §8 plan robustness 영역 직접 base.

### 11.2 변동성 감소 evidence

negative control (CaseA 단독 대체) 영역 large worsening = 37.1% 대비 결합 minimal augmentation (CaseB) 영역 변동성 감소. 산술 평균 결합 (est_final = (est_b1 + est_method) / 2.0) 영역 paper random Bernoulli + 우리 sample selection 영역 양쪽 영역 estimation 영역 평균 영역 → method 선택 영역 실패 영역 risk 영역 hedge.

### 11.3 결합 진짜 가치 의 의의

본 §11 의 결합 진짜 가치 = **단독 best 정확도 (-10.17%) X 결합 best 정확도 (-7.37%) X**. 결합 영역 진짜 가치 = 9 측정 환경 × 16 사용 sample selection method 영역 paired uplift 안정성 92.5% + 변동성 감소. paper §V-B 의 cardinality 추정 mechanism 영역 그대로 유지 + sample selection augment 영역 minimal 영역 안정 우위 영역 정량 evidence.

> **TBD (chain 완료 후 update)**: v9 sel sweep 영역 evidence 영역 update — sel=0.001 / sel=0.01 / sel=0.10 영역 결합 안정성 영역 평가.

---

## 12. 자원 효율 — Pareto frontier (정확도 best = 자원 best)

> ★ **본 § = chain 의존 영역 (v8/v9 chain 완료 후 추가 작성)**. 본 v6 draft 영역 v5 carry-over base + chain 완료 후 update 명시.

본 §12 은 §9 (fit_time 11.9× range) + §6 (sample selection vs random Bernoulli paired Q-error Δ%) evidence 영역 통합한 Pareto frontier 정리.

### 12.1 Pareto Top 5 sample selection method

**Pareto Top 5 sample selection method** = sparse_rp / chao_weighted / hyperloglog / pca1d / hilbert_real (★ hilbert 영역 PCA 2 차원 정렬 별칭 정정 후, 진짜 Hilbert curve 구현인 hilbert_real 영역 별도 측정).

### 12.2 정확도 best = 자원 best 의 핵심 finding

Q-error 영역 정확도 (sample selection vs random Bernoulli) 측면 안정 우위 5 sample selection method 와 자원 효율 측면 파레토 우위 5 sample selection method 영역 동일 영역 finding. **Q-error 영역 정확도 best 와 학습 자원 (시간 + 메모리) 효율 best 영역 동일 sample selection method 군 영역 발현**.

reservoir 표집 (chao_weighted base) 영역 메모리 사용 영역 데이터 크기와 무관한 상수 O(K) 영역 anchor 수준 정확도. sparse_rp (3.67s) 영역 hilbert_real (43.50s) 대비 12× 빠르면서도 Q-error 영역 정확도 동일 Pareto frontier 영역 동시 best 발현. 모바일 / 임베디드 / 스트리밍 환경 직접 적용 가능 finding.

> **TBD (chain 완료 후 update)**: fit_time × sample selection vs random Bernoulli paired Δ% scatter 영역 update — chain v8/v9 완료 후 16 사용 sample selection method 영역 9 cell × 2 mode 영역 fit_time × paired Δ% 직접 evidence 영역 추가.

---

## 13. 권장 — Dynamic method selection by dataset Type

> ★ **본 § = chain 의존 영역 (v8/v9 chain 완료 후 추가 작성)**. 본 v6 draft 영역 v5 carry-over base + chain 완료 후 update 명시.

본 §13 은 §4 영역 4 type 분류 + Type 별 적합 sample selection method 매핑 + §7 영역 dynamic 할당 mechanism flow 영역 base 위에서 **권장 영역 정리**. 본 v6 narrative 영역 framing layer 분리 (§1) 영역 정합 — paper 영역 cardinality 추정 mechanism 영역 그대로 유지 + 우리 영역 sample selection 영역 augment 영역만.

### 13.1 권장 1 — Type 별 best sample selection method 자동 선택

| Type | 적합 sample selection method | sample selection vs random Bernoulli paired Δ% | fit_time |
|---|---|---:|---:|
| **Type 1** (small single sf=1) | **chao_weighted K=20 ★ 최강** / sparse_rp K=20 | −14.11% / −11.70% | 3.67 ~ 9.40s |
| **Type 2** (medium single sf=10) | chao_weighted K=20 (sweet spot 약함) / sparse_rp K=20 | −6.00% / −6.58% | 3.67 ~ 9.40s |
| **Type 3** (large single sf=100 저-중차원) | chao_weighted / sparse_rp K=20 | −12.20% / −11.20% | 3.67 ~ 19.97s |
| **Type 4a** (large multi 224-288d) | hilbert_real K=30 slight edge | (chain 완료 후 update) | 43.50s |
| **Type 4b** (large multi 864d) | **Centroid tuple ★** (학습 비용 추가 0) | −7.37% | (Centroid 영역) |

### 13.2 권장 2 — 결합 minimal 영역 안정 우위

**결합 minimal augmentation (CaseB ensemble) 영역 권장 default**. paper §V-B 의 random Bernoulli single 대비 sample selection vs random Bernoulli paired Q-error Δ% 안정 우위 92.5% (§11). 환경 variability 큰 산업 환경 영역 결합 minimal 영역 안정성 + 변동성 감소 영역 직접 가치.

negative control (CaseA 단독 대체) 영역 large worsening 37.1% (§10) 영역 단독 대체 가설 폐기 영역. 결합 minimal augmentation 영역 default 권장 + 단독 대체 영역 권장 X.

### 13.3 권장 3 — fit_time × 정확도 동시 best 의 sample selection method

§12 Pareto frontier 영역 = **정확도 best = 자원 best** 영역 직접 권장 evidence. Pareto Top 5 sample selection method (sparse_rp / chao_weighted / hyperloglog / pca1d / hilbert_real) 영역 모두 fit_time 3.67s ~ 43.50s range + Q-error 영역 정확도 동시 best.

산업 환경 영역 분포 catch 속도 제약 시 sparse_rp (3.67s) — fit_time 최단 영역 + Q-error 영역 정확도 동일 Pareto frontier 영역 동시 best.

> **TBD (chain 완료 후 update)**: chain 완료 후 권장 영역 재정리 — v8/v9 영역 cell × method 영역 update + Type 별 best sample selection method 영역 chain 영역 evidence 영역 추가.

---

## 14. post-narrative

본 v6 narrative 영역 base 위에서 5/27 발표 + 6/11 보고서 영역 두 영역 deliverable 영역. 5/27 발표 = deck v11 (25 slide × 60s = 25m + Q&A 5m = 30m, prompt v11 Part 1-3 base). 6/11 보고서 = outline v3 update + 20 page 본문 + 5 finding 자세히 + appendix.

5/27 발표 후 영역 두 영역 향후 작업:
- **박광현 input 4 엔진 통합 POC** (5/27 발표 후 시작): PostgreSQL pgvector + DuckDB + vector.c PG 영역 + 추가 엔진 영역 4 엔진 통합. **sample selection 영역 cross-engine 일반화 검증 영역**. 본 v6 narrative 영역 base 위 cross-engine 적용 evidence 영역 추가.
- **open question**: Type 5 (영역 더 정의) 영역 확장 가능성 + 다중 modal multi-vector 영역 확장 + real workload 영역 production deploy.

본 post-narrative 영역 = 5/27 발표 X (보고서 영역만 + 향후 작업 영역 outline). 본 v6 narrative 영역 closure 영역.

---

# 부록 §A — 정정 룰 7 (carry-over from v5)

## A-1. paper §V-B 자체 algorithm pseudo-code 없음

paper §V-B 영역 Eq 1-6 + 자연 산문 + hyperparam 7 종 만으로 구성. "Algorithm 1" / "Procedure" 등 algorithmic block 형식이 paper 에 없다. 본 연구의 "17-step" 표현은 본 연구 자체의 의역. 본 v6 narrative 영역 = pseudo-code 형식 영역 사용 X (Phase 1+2+3 영역 자연 산문 영역).

## A-2. framework axis novelty 한정

본 연구의 4 component 자체는 각각 신규 X.
- **Component A** (Stratified Reservoir Sampling) = Vitter 1985 + Al-Kateb 2014
- **Component B** (BIRCH CF-tree) = Zhang SIGMOD 1996 (batch axis 자원 한계 폐기, CF tuple 형식만 Component C 입력)
- **Component C** (paper Eq 2-6 통합) = paper §V-B verbatim
- **Component D** (Distribution-aware stratification) = Cochran 1977 §5.5 (4 mode: Equal / Proportional / Neyman / Anti-Neyman)

본 연구의 contribution = framework axis (4 component 통합 + paper §V-B 위에서의 발현 + 4 type 분류 + dynamic method selection + paired uplift 정량 evidence). 본 v6 narrative 영역 framing layer 분리 (§1) 영역 = 본 contribution axis 영역 명확 통일.

## A-3. paper §V-B single-table = 구현 코드 한계

paper §V-B 자체는 single-table KNN query 에 대한 sampling-based cardinality estimation 명시 (paper p.5 우단 verbatim). paper 공개 코드 (BDAI-Research/Exqutor github) 의 single-table 영역이 동작하지 않아 본 연구의 측정이 multi-join 으로 자연 이동. 임채림 연구원 자문 base.

## A-4. paper §V-B sampling = block + row hybrid

paper §V-B sampling 영역 초기 N=385 budget = block 추출 + Eq 5 sampling_size update 시 n_inc 행 추가 = row 추출 의 block + row hybrid. 이전 narrative "block only" 표현은 부정확. 임채림 자문 base. 본 v6 narrative 영역 Phase 1 (offline) + Phase 2 (online) 영역 분리 영역 = 본 hybrid 영역 명확 반영.

## A-5. "분포 안다 / 모른다" binary 폐기 (★ 박세은 5/15 20:49 정리 #1)

이전 narrative 의 "분포 안다 (L1/L2/L3 multi-layer) / 모른다" 영역 binary 구분은 부정확. 우리 method (클러스터링 / 차원 축소 / quantization 등) 자체가 분포를 파악하는 도구이며, 데이터셋 진입 시 method 가 빠르게 분포를 catch 한다 (§9 fit_time 11.9× evidence).

본 binary 구분 자체가 paper §V-B 의 "without index" 가정을 잘못 해석한 것. **본 v6 narrative 영역 = "Sample Selection" 영역 일관 통일** + binary 영역 폐기 영역 명확 반영.

## A-6. paper §V-B = "without index" 가정

paper §V-B 자체는 "without vector index" 가정 안에서의 sampling-based cardinality estimation (paper p.5 좌단 + p.5 우단 + p.6 우단 + §VI-A + §VI-B verbatim). ECQO 의 vector index = HNSW (data itself) 구축과 §V-B sampling 은 paper 자체 안에서 상호 배타.

단 "without index" 는 인덱스 없음을 의미하며, **분포 정보 자체의 부재를 의미하지는 않는다** (정정 #5 와 align). 우리 영역 sample selection 영역 = "without index" 가정 영역 안 영역 분포 인지 sample selection augment 영역 valid.

## A-7. "Anti-Neyman > Neyman" wording 정정 → selectivity-dependent

이전 narrative "Anti-Neyman > Neyman = Neyman 가설 무효" 는 부정확. 정확 의미:

- Neyman 가설 자체는 유효 (Cochran 1977 §5.5 classical theory 정합)
- 본 데이터셋이 Neyman 가정 조건 (cluster 간 σ_j heterogeneity) 不만족 (σ_j range 1.3-1.6× narrow + N_i CV=0)
- selectivity-dependent (sel=0.01 paradox / sel=0.10 정합)

| selectivity | Neyman | Anti-Neyman | Proportional | best |
|---|---:|---:|---:|---|
| sel=0.01 | 1.595 | 1.540 | 1.580 | **Anti < Prop < Neyman** (paradox) |
| sel=0.10 | 1.1076 | 1.1101 | 1.1135 | **Neyman < Anti < Prop** (classical 정합) |

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify. 본 v6 narrative 영역 §8 (chain TBD) 영역 selectivity-dependent paradox 영역 update 시 본 룰 영역 carry-over.

---

# 본 v6 draft 영역 작성 룰 (final check)

본 v6 draft 영역 generate 시 영역 final check 영역 verify:

| 항목 | 검증 영역 | 본 v6 |
|---|---|---|
| 1 | 모든 § 영역 "Sample Selection" 일관 사용 (cardinality 추정 표현 모두 제거) | ✓ |
| 2 | §1 framing layer 분리 영역 명확 (paper 영역 vs 우리 영역) | ✓ |
| 3 | §2 paper 영역 § 흐름 영역 = 간단 소개만 (cardinality 추정 mechanism 영역 paper 영역 강조) | ✓ |
| 4 | §3 우리 영역 3 phase 영역 = Phase 1+2 우리 영역 + Phase 3 minimal | ✓ |
| 5 | §4 데이터셋 4 type 분류 영역 = Type 1/2/3/4a/4b | ✓ |
| 6 | §5 paradigm 별 method 영역 = sample selection 영역 mechanism 영역 일관 | ✓ |
| 7 | §7 dynamic 영역 = sample selection 영역만 dynamic (paper Adaptive 영역 그대로) | ✓ |
| 8 | §9 fit_time 영역 = "분포 catch = sample selection 영역 stratification 시간" 일관 | ✓ |
| 9 | §6/§8/§10-§13 chain 의존 영역 v5 carry-over fill in + chain 완료 후 update 표기 | ✓ |
| 10 | 부록 §A 정정 룰 7 carry-over (v5 → v6) | ✓ |
| 11 | wording 정정 일관 적용 ("sample selection 결합 minimal" / "negative control" / "sample selection vs random Bernoulli paired Q-error Δ%" / "Q-error 영역 정확도") + "cardinality 추정 우리 영역 contribution" 표현 모두 제거 | ✓ |

---

작성: 2026-05-16 KST · v5 (5/15 21:00) base + handoff v31 박세은 framing 단순화 의도 + prompt v11 Part 1-3 (5/16 00:50) 완전 반영 · Phase A partial draft (즉시 작성 가능 9 § + 부록 §A) + chain 의존 § (§6/§8/§10-§13) v5 carry-over fill in (실측 수치 + chain 완료 후 update 명시) · wording 정정 일관 적용 ("sample selection 결합 minimal" / "negative control" / "sample selection vs random Bernoulli paired Q-error Δ%" / "Q-error 영역 정확도" / "cardinality 추정 우리 영역 contribution" 표현 모두 제거) · v8/v9 chain (5/17-5/18 새벽) 완료 후 추가 작성 + Phase B 영역 정합 evidence 영역 update
