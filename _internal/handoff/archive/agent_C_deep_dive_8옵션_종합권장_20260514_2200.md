# Agent C — 8 옵션 deep dive + 옵션 발산 추가 + 최종 권장 path

> **작성**: 2026-05-14 22:00 KST · Agent C · main thread 지시 "8 옵션 (A-H) deep dive + literature 검증 + 최종 권장 form"
> **검증 기조**: paper PDF 전체 정독 (§V-A + §V-B + §VI-A/B/C/D/E + §VII + §VIII Algorithm 1 14-step) + Agent A (78%) + Agent B (정정 7) + WebSearch 7 건 + measurement 9 analysis file 직접 read
> **★★★ wording 정정 룰 (Agent B critical 반영 — 필수 사용)**:
>   - ❌ 폐기: "5 단계 中 1 단계", "5 단계 알고리즘"
>   - ✓ 정정: "Eq 1 (Bernoulli) 대체 vs Eq 2-6 (dynamic batch loop = paper differentiation) 유지"
>   - Neyman paradox = sel=0.01 한정 명시 (sel=0.1 영역 역전 정량 발견)
>   - σ_j range = oracle interpretation 명시 (직접 측정 미완)
>   - Pareto Top 5 = "sparse_rp / chao_weighted / **neuram** / pca1d / hilbert" (reservoir 별도)
>   - byte-identical = 6 unique cells (9 nominal)
>   - 학부 capstone = **★★ 매우 강력**

---

## 0. 핵심 결론 요약 (TL;DR)

본 Agent C deep dive 결과 8 옵션 (A-H) + 옵션 발산 추가 3 (I/J/K) + hybrid 결합 3 권장 (A+C / A+B+F / A+G) 정형화. 5/15 박광현 미팅 + 5/27 발표 + 6/11 보고서 timeline 종합한 최종 권장 path 는 다음과 같다.

| 우선순위 | 옵션 | 한 줄 요약 | 학술 가치 | 추가 cost (h) | 5/27 timeline |
|---|---|---|---|---:|---|
| **1순위** | **A + G** | 현 narrative 정직 명시 + reservoir streaming 산업 적용 highlight | ★★ 학부 capstone + 산업 contribution | 5h | ★ 안전 |
| **2순위** | **A + B + F partial** | 현 narrative + Eq 2-6 dynamic batch 부분 확장 + ECQO Q-error gap 비교 | ★★★ review-grade 접근 | 25-35h | △ 가능 (가속화 필요) |
| **3순위** | **A + C** | 현 narrative + Neyman paradox sel-dependency 메커니즘 일반화 | ★ vector similarity novelty | 15-20h | ★ 가능 |
| **★ 폐기 권장** | **D / E / H** | L0-L4 framework / multi-table 단독 main / TPC-DS 확장 | timeline 부족 + 분산 위험 | 25-40h | ✗ 무리 |

**5/15 박광현 미팅 1st priority discussion**: 옵션 A 의 학부 capstone 충분성 확인 + 옵션 B (Eq 2-6 확장 가능성, 5/27 timeline 가능?) + 옵션 G (reservoir industry positioning) + 옵션 C (Cochran 1977 §5.5 challenge 대비책).

**★★★ 본 Agent C 의 정직 disclosure**: 옵션 C 의 novelty 가 Cochran 1977 §5.5 ("the gain in accuracy from Neyman allocation compared to proportional allocation is pretty small" + "If the variances are uniform across all strata, Neyman allocation reduces to proportional allocation") 안에 **part 부분 포함** 됨 — vector similarity domain 의 정량 발현은 novel 이나 mechanism 자체는 known. 박광현 자문 시 일정 challenge 가능.

---

## 1. 8 옵션 (A-H) 각 항목별 deep dive

### 1.1 옵션 A — 현 narrative 유지 + 간극 정직 명시

#### A.1 영역 정의 깊이 발산

**paper 어디**: §V-B Eq 1 (N=385 Bernoulli sample budget) 한정.
**우리 어디로**: Eq 1 sampling 추출 방식을 stratified K-Means K=20 으로 대체 (CaseA 단독) 또는 산술 평균 (CaseB 결합). Eq 2-6 (dynamic batch loop = paper differentiation) 유지.
**학술 contribution 영역**: paper §V-B Algorithm 1 의 **sample 추출 방식 augment** 한정. paper main mechanism (Eq 3-6 Q-error feedback 동적 size) 영역 X.

#### A.2 paper 추가 정독 (§VI Discussion / §VIII Conclusion)

paper §VI-B 우단 (Fig.5 다음):
> "Adaptive sampling overcomes this limitation by modifying the sample size based on query feedback. It tracks Q-error over time and adjusts the number of sampled rows accordingly."

→ paper 본 differentiation = **Q-error feedback 의 sample size 동적 조정** (Eq 3-6). 우리가 안 건드림. 옵션 A 정직 wording 의 핵심.

paper §VI-E Limitations 1번:
> "In high-dimensional spaces, the overhead of sampling increases because of the higher cost of distance computations, which may reduce the efficiency of our adaptive sampling strategy."

→ 옵션 A 학술 정당성 = "high-dim 환경 (WIKI 768d) 의 효율 axis 강조" 영역 우리 측정 Pareto frontier 와 직접 align.

#### A.3 literature check (학술 novelty 평가)

- WebSearch 결과: 2024-2025 cardinality estimation literature 다수 (PSDSS 2025 / FLAT / CardBench / ASM / ByteCard) 모두 ML-based 또는 hybrid approach. **distribution-aware stratification + paper exact reproducibility** narrative 는 niche.
- **Novelty: weak** (reproducibility + ablation type). paper level reject 가능성 high. 단 학부 capstone 수준 학술 정직성 axis 는 매우 강력.

#### A.4 우리 1001 file 재해석

- **100% valid** 유지. 현 측정 모두 옵션 A scope.
- 폐기 method 40 (자원 7 + audit 23 + 정합성 10) = 옵션 A 의 **정직 disclosure axis** 의 정량 근거.

#### A.5 추가 측정 / 작업 cost

- 측정: **0**
- 분석: **0** (현 9 analysis file 재사용)
- 문서화: Algorithm 1 box (14-step) 적용 + Eq 2-6 honest limitation 명시 + byte-identical caveat 명시 = **~5-8h**

#### A.6 박광현 review 기대 학술 가치

- **positive 가능**: paper exact 재현 + 1001 file portfolio + 40 폐기 정직 분류 = BDAI 연구실 (DB rigor) 기조 일치
- **challenge 가능**: "Eq 2-6 영역 확장 가능?" → 옵션 B 권유 / "L1 (skew flag only) 산업 가치?" → 옵션 D 권유

#### A.7 timeline 적합성

- ★ **5/15 박광현 미팅 (D-1)**: 옵션 A 의 narrative 로 자문 직접 가능
- ★ **5/27 발표 (D-13)**: 옵션 A 그대로 발표 가능
- ★ **6/11 보고서 (D-28)**: 옵션 A 그대로 작성 가능

#### A.8 hybrid 결합 가능성

★ **모든 hybrid 의 base** — 옵션 A 단독으로 안전 path. 다른 옵션 (B / C / G) 은 옵션 A 위에 layer 로 add. 옵션 A + (다른 옵션 1 개) 가 timeline 균형.

---

### 1.2 옵션 B — Eq 2-6 dynamic batch loop 확장 측정 (★★ Agent B 격상)

#### B.1 영역 정의 깊이 발산

**paper 어디**: §V-B Eq 3-6 (δ adjustment + V_t momentum + sampling_size update + γ lr decay). paper §VII 인용:
> "The method in [81] adjusts the sample size dynamically until a desired confidence level is reached, but does not consider sampling overhead or optimize it dynamically based on query characteristics."

→ paper differentiation 영역. Lipton-Naughton 1990 [81] 과 paper 의 differentiation 의 **진짜 contribution**.

**우리 어디로**: Algorithm 1 의사코드 Step 11 ("Sample n_inc more rows via Bernoulli, refresh μ̂_t and σ̂²_t") 의 **n_inc 분배 + Bernoulli 추출 방식** 을 group-aware 로 augment. 구체적:
- Step 10 의 `n_inc = N₀ · max(1, β · σ̂²_t / α)` → group 별 σ̂²_{j,t} 로 분배
- Eq 4 momentum V_t → group-aware V_{j,t} = m · V_{j,t-1} + η_t · δ_j
- Eq 5 sampling_size update → group 별 분배

**학술 contribution 영역**: paper main mechanism (Q-error feedback 동적 batch) 의 distribution-aware augmentation.

#### B.2 paper 추가 정독

paper §VI-B 우단 + Fig.6 (page 8):
> "The sample size trajectory varies depending on the dataset: for DEEP and SimSearchNet++, the sample size decreases over time as Q-error stabilizes... In contrast, for SIFT, the sample size increases to satisfy higher estimation demands due to its more complex distribution."

★ paper 본인 명시: dynamic batch trajectory = **dataset 의 분포 (complexity) 의존**. 옵션 B 의 distribution-aware augment 가 정확히 이 영역.

paper §VI-B 끝 단락 (verbatim):
> "Together, these methods allow Exqutor to apply selectivity-aware optimization even when vector indexes are unavailable, while also ensuring stable performance under shifting workloads."

★ paper 의 "shifting workloads" 영역 contribution 이 Eq 3-6 의 dynamic batch loop. 옵션 B 의 학술 정당성 = 매우 강력.

#### B.3 literature check

- **Sutskever et al. 2013 [22]** (paper reference) = momentum + lr decay 의 deep learning training. paper Eq 4 momentum 의 base.
- **Lipton-Naughton 1990 [81]** = adaptive sampling for join size estimation. paper 가 explicit differentiation 영역.
- WebSearch 결과: "Sampling-Based Cardinality Estimation Algorithms" (cs.wisc.edu lecture, 2024) — adaptive sampling 의 dynamic batch literature 다수 (Lipton-Naughton 1990 / Haas-Stokes 1998 / Hou-Ozsoyoglu 1991) 의 **distribution-aware** augmentation 영역은 sparse.
- "Adaptive Data Optimization: Dynamic Sample Selection with Scaling Laws" (OpenReview 2024-2025) = dynamic sample selection 의 scaling law 영역 — 옵션 B literature base.
- **Novelty: ★★ strong**. paper main contribution 영역 위 distribution-aware augment.

#### B.4 우리 1001 file 재해석

- 옵션 A 의 모든 측정 (1001 file) 이 옵션 B 의 baseline 으로 valid 유지
- 추가 측정 30-60 file 필요 (group-aware dynamic batch loop 의 9 cell × 5 anchor × 2 mode × 5-10 trial)
- 폐기 method 40 분류 그대로 유지

#### B.5 추가 측정 / 작업 cost

- **scheduler 구현**: paper Eq 3-6 verbatim 위 group-aware augment 코드 작성 = **1-2 일 (10-15h)**
- **측정**: 9 cell × 5 anchor method × 2 mode × 10 trial ≈ 90 file × 100-200초/file ≈ **3-5h 서버 시간**
- **검증 + 분석**: paired Δ% + paradigm-level rollup = **1 일 (8h)**
- **문서화**: 5/27 deck + 6/11 보고서 새 section = **0.5-1 일 (4-8h)**
- **총 cost: 약 25-35h** (서버 (capstone2026) + 자원 Max 활용 시 가능)

#### B.6 박광현 review 기대 학술 가치

- **★★ positive 강함**: paper main contribution 영역 (Eq 3-6 dynamic batch) 의 distribution-aware augment 는 BDAI 연구실 (DB rigor) + 박광현 paper 박광현 작성자 한 명 가능성 측면에서 직접 발현
- 옵션 A 의 challenge ("Eq 2-6 영역 확장 가능?") 답이 옵션 B
- **review-grade 가능성**: 학부 capstone 의 ceiling 을 review-grade 까지 끌어올림. 단 paper level (SIGMOD/VLDB) 까지는 generalization 측정 보강 필요.

#### B.7 timeline 적합성

- **5/15 박광현 미팅**: 옵션 B design 합의 + 5/27 timeline 가능성 confirm 권장
- **5/27 발표**: D-13 까지 **측정 + 분석 + 슬라이드 작성 가능** (자원 Max + 가속화 필요)
- **6/11 보고서**: 옵션 B 완전 보고서 작성 가능
- ★★ 가장 큰 risk = **5/27 timeline 압박**. 박광현 미팅 결과에 따라 결정.

#### B.8 hybrid 결합 가능성

- **A + B** (가장 강력): 옵션 A 의 정직 narrative + 옵션 B 의 Eq 3-6 확장 = 학부 capstone + review-grade 접근. 총 cost 25-35h.
- **A + B + F** (★ 본 권장 2순위): A + B + ECQO Q-error gap 비교. 총 cost 35-50h.
- **B + D**: Eq 3-6 확장 + L0-L4 framework. 학술 가치 ★★ but timeline 부담.

---

### 1.3 옵션 C — Neyman paradox σ_j 메커니즘 일반화 (★ Cochran 1977 §5.5 부분 포함)

#### C.1 영역 정의 깊이 발산

**paper 어디**: §V-B Eq 1 (Bernoulli sample) + §VII Related Work (paper 자체가 Lipton-Naughton 1990 [81] differentiation). paper 가 K-means + Neyman allocation 결합 안 검토.

**우리 어디로**: 본 회의 채림님 14:57 본질 발견:
> "K-means (L2) + L2 vector similarity range query → cluster 안 응답 일관 → σ_j range 1.3-1.6× narrow (oracle interpretation, sel=0.1 D_target 단일 calibration) → Neyman 효과 약함, Proportional 이 답"

**학술 contribution 영역**: vector similarity range query 환경 + clustering metric = query metric 의 σ_j narrow 메커니즘 정량 발견 + 일반화 (cosine / Manhattan / K granularity / 다른 datasets).

#### C.2 paper 추가 정독

paper §V-B 본문 Eq 3-6 부분:
> "Adaptive sampling size adjustment. While fixed sample sizes provide statistical guarantees, they may not be equally effective across datasets with varying distributions or dimensionalities."

→ paper 자체가 "varying distributions" 의 영향 영역을 묵시적 인정. 옵션 C 의 σ_j narrow 메커니즘 발견은 정확히 이 영역 한 부분의 정량 발현.

#### C.3 literature check (★★★ critical Cochran 1977 §5.5 발견)

**WebSearch 결과**:
- **Cochran 1977 §5.5** (★★★ critical): "the gain in accuracy from Neyman allocation compared to proportional allocation is pretty small. This is why in practice proportional allocation is often preferred to optimal (Neyman) allocation."
- **Cochran 1977 §5.5 추가**: "If the variances are uniform across all strata, Neyman allocation reduces to proportional allocation where the number of sampled units in each stratum is proportional to the population size of the stratum."

★★★ **결정적 발견**: 본 연구의 Neyman paradox 메커니즘이 **classical theory 안에 이미 명시**됨. σ_j narrow → Neyman ≈ Prop 는 Cochran 1977 §5.5 의 known result.

**옵션 C novelty 평가 (정정)**:
- 메커니즘 자체 (σ_j narrow → Neyman ineffective): **known** in classical theory (Cochran 1977)
- vector similarity range query domain 의 정량 발현: **novel** (vector similarity 영역 + K-means 결합)
- **Novelty: ★ partial** (full novelty 아님, vector domain 의 정량 발현 한정)
- **Agent A 의 "★★ 매우 강함" → Agent C 정정: "★ 강함 (단 Cochran 1977 §5.5 part 포함 명시)"**

#### C.4 우리 1001 file 재해석

- RQ2 5-way (Bern / Equal / Prop / Neyman / Anti) 9 cells × 5 way 측정 = 옵션 C 의 정량 base
- ★★ scope 정정 필수: **Neyman paradox = DEEP sf=100 sel=0.01 paired (n=455) 한정**. sel=0.1 영역 paradox 역전 (Neyman 1.1076 lowest, Anti 1.1101). 즉 paradox 가 selectivity-dependent.
- 추가 측정 필요: cosine / Manhattan K-means × 4 method × 3 cell × 2 mode = 24 측정 + K=50/100/200 × 4 anchor × 3 cell = 36 측정 = 약 60 측정 ≈ **2-3h 서버 시간**

#### C.5 추가 측정 / 작업 cost

- 측정: 60 file ≈ **2-3h 서버 시간**
- 분석: σ_j range 직접 측정 (각 cell 별 5-way csv 의 per-stratum σ_j 추출) + paradox 메커니즘 정형화 = **1-2 일 (10-15h)**
- 문서화: paper level 메커니즘 section + 5/27 deck + 6/11 보고서 = **0.5 일 (4h)**
- **총 cost: 약 15-20h**

#### C.6 박광현 review 기대 학술 가치

- **★ positive**: vector similarity domain 의 정량 발현은 novel 으로 인정 가능
- ★★ **challenge 가능 (Cochran 1977 §5.5 정확히 challenge)**: "σ_j narrow → Neyman ≈ Prop 는 classical theory 안에 있는데, 본 연구 contribution 은?"
- **대응책**: vector similarity range query domain 한정 + K-means metric = query metric alignment 의 자연 발현 메커니즘 명시 + generalization 측정 보강 (cosine / Manhattan)

#### C.7 timeline 적합성

- **5/15 박광현 미팅**: 옵션 C 의 Cochran 1977 §5.5 challenge 대비 자문 권장
- **5/27 발표**: D-13 까지 측정 + 분석 + 슬라이드 가능 (cost 15-20h)
- **6/11 보고서**: 옵션 C main narrative 가능

#### C.8 hybrid 결합 가능성

- **A + C** (Agent A 1순위 추천, Agent B 정정): A 의 정량 결과 + C 의 메커니즘 발견. 단 Cochran 1977 §5.5 challenge 대비 필요.
- **C 단독**: 옵션 A 의 정량 결과를 supporting evidence 로 강등, C 가 main. risk = Cochran 1977 § 5.5 challenge 시 narrative 약화.

---

### 1.4 옵션 D — L0~L4 정보 수준 axis 정형화

#### D.1 영역 정의 깊이 발산

**paper 어디**: paper §V-B 는 단일 정보 수준 ("데이터 모름" 환경) 만 다룸. 본 회의 합의 (§5.3 정보 수준 axis):

| 수준 | 정보 | 현 적용 method |
|---|---|---|
| L0 | raw data only | Bernoulli (paper §V-B baseline) |
| L1 | + skew flag | **본 연구 영역 밖** (Q8 회의 의문) |
| L2 | + cluster boundary (sz_j 모름) | Equal allocation (RQ2 partial) |
| L3 | + cluster + sz_j | Proportional (RQ2/RQ3 main) |
| L4 | + cluster + sz_j + σ_j | Neyman / Anti (RQ2 only, 이상적 천장) |

**우리 어디로**:
1. L1 method 새로 개발 (HHI / CV 기반 skew flag → adaptive Bernoulli sample size + adaptive method selection)
2. L1 영역 측정 (9 cell × 2-3 method × 2 mode = 60 측정)
3. L0~L4 spectrum 학술 정형화

**학술 contribution 영역**: framework contribution + L1 영역 의 산업 환경 (데이터 카탈로그 메타데이터만 있는 경우) 적합성.

#### D.2 paper 추가 정독

paper §V-B + §VI-B + §VI-C 영역 모두 단일 정보 수준 (paper "데이터 모름") 만 다룸. paper §VI-E Limitations 도 정보 수준 axis 미언급.

→ 옵션 D 학술 정당성 = **paper 가 다루지 않은 영역의 framework contribution**.

#### D.3 literature check

- **WebSearch 결과**: "information levels metadata cardinality estimation" 영역 literature sparse.
- **SQL Server cardinality estimation** = histogram base (paper Bernoulli 와 유사 level)
- **Hybrid cardinality estimation** (2025 paper 다수) = query-driven + data-driven hybrid 의 정보 수준 axis 일부 다룸
- **Novelty: △ moderate** (framework contribution + L1 영역 산업 적합성). 단 학술 paper level 측면 framework contribution 만으로는 약함 (학회 reviewer 가 "framework 자체로 novelty?" challenge 가능).

#### D.4 우리 1001 file 재해석

- L2-L4 영역 (Bernoulli / Equal / Prop / Neyman / Anti) 측정 = 옵션 D 의 정량 base
- L0 영역 = paper baseline B1 (9 cells)
- L1 영역 = **측정 0 (옵션 D 의 추가 측정 영역)**

#### D.5 추가 측정 / 작업 cost

- **L1 method 개발**: HHI/CV 기반 skew flag → adaptive Bernoulli sample size + adaptive method selection (high skew = stratified, low skew = Bernoulli) = **2-3 일 (16-24h)**
- **L1 측정**: 2-3 method × 9 cell × 2 mode × 10 trial = 60-90 file ≈ **3-5h 서버 시간**
- **L0~L4 spectrum 분석 + 정형화**: 각 정보 수준 best method 의 Q-error mean 비교 + framework 정형화 = **1-2 일 (10-15h)**
- **문서화**: 5/27 deck + 6/11 보고서 framework section = **0.5 일 (4h)**
- **총 cost: 약 25-35h** (옵션 B 와 동등)

#### D.6 박광현 review 기대 학술 가치

- **positive**: framework contribution = BDAI 연구실 측면 인정 가능
- ★★ **challenge 가능**: "L1 영역의 산업 가치 정량 입증?" (Q8 회의 의문 동일). 답변 = 데이터 카탈로그 메타데이터 환경 + 클라우드 데이터 lake 환경 + sensitive data 환경 (raw access 없이 skew flag 만)
- **review-grade 가능성**: framework + L1 측정 = 학술 paper level **가능 but 약함**

#### D.7 timeline 적합성

- 5/15 박광현 미팅: 옵션 D 의 framework + L1 산업 가치 자문 권장
- 5/27 발표: cost 25-35h → D-13 까지 timeline 빡빡함
- 6/11 보고서: 가능 (D-28)
- ★★ **risk = scope creep**. L1 method 개발 + 측정 + framework 정형화 = scope 분산. timeline 압박 시 risk 높음.

#### D.8 hybrid 결합 가능성

- A + D: 옵션 A + framework. 가능하나 옵션 D 단독으로 cost 부담 → timeline 빡빡함
- B + D: review-grade 강력 but cost 50-70h → timeline 무리
- **★ Agent C 권장: 옵션 D 는 5/27 까지 timeline 측면 무리. 6/11 보고서의 future work 영역 권장.**

---

### 1.5 옵션 E — Multi-table + Centroid tuple cheap 근사 main 화

#### E.1 영역 정의 깊이 발산

**paper 어디**: §V-B 가 명시한 "specifically for KNN queries" (single-table) 제약 (page 5 우단 verbatim). multi-table joint distribution 영역은 paper §V-A ECQO 만 다룸 (인덱스 있을 때 한정).

**우리 어디로**: A2-Fig7/8/9 multi-table 측정 + Centroid tuple cheap 근사 framework (5/13 16:50 발견) 의 main 화.
- 현 측정: A2-Fig9 single cell + 4 anchor × 2 mode = 8 measurement, Centroid tuple −7.37% (sparse_rp CaseB) + CaseB 4 method 모두 평균 −0.84p 추가 우위
- 확장: Centroid tuple K_A=10/20/30 × K_B=10/20/30 = 9 K-pair × 4 method × 2 cells × 2 mode = 144 측정

**학술 contribution 영역**: paper §V-B "single-table KNN only" 제약 깨기 + cheap approximation (학습 비용 0) + multi-table joint 의 정량 우위.

#### E.2 paper 추가 정독

paper §VI-C (Fig.8/9 multi-vector VAQs, page 10):
> "We further evaluate Exqutor on multi-vector query workloads, where embeddings from multiple sources are integrated into queries. As shown in Figure 8, when both DEEP and WIKI datasets are stored in the partsupp table, we observe substantial performance improvements... Figure 9 illustrates the scenario where DEEP embeddings are stored in partsupp while WIKI embeddings are stored in the part table."

★ paper 본 measurement = multi-vector 영역 다룸 but **ECQO context** (인덱스 있을 때). adaptive sampling context (인덱스 없을 때 multi-table) 는 paper 측정 미실시.

→ 옵션 E 학술 정당성 = paper §V-B + §VI-C 의 boundary 영역 contribution.

#### E.3 literature check

- WebSearch "multi-table join cardinality estimation": **FactorJoin** (2022, arxiv), **Scardina** (2023), **TKHist** (2025, arxiv), **OmniSketches** (2025) — multi-table joint cardinality estimation literature 활발. cross-table joint distribution 영역의 active research.
- **CUBE: Cardinality Estimator Based on Neural CDF** (2512.09622, 2025) — neural CDF base. vector similarity 영역 X.
- **Cardinality Estimation Done Right: Index-Based Join Sampling** (CIDR 2017) — Leis et al. index-based join sampling. paper §V-A ECQO 와 유사.
- **Novelty: △ moderate** (multi-table cheap approximation + 학습 비용 0 axis). 단 FactorJoin / Scardina / TKHist 와의 differentiation 명시 필요.

#### E.4 우리 1001 file 재해석

- A2-Fig7/8/9 측정 (3 cells × 17 method × 2 mode = 약 102 file) = 옵션 E 의 main result base
- Centroid tuple 8 measurement = 옵션 E 의 main contribution 정량 근거
- 추가 측정 = K granularity 9 pair × 4 method × 2 cells × 2 mode = 144 file

#### E.5 추가 측정 / 작업 cost

- 측정: 144 file ≈ **4-6h 서버 시간**
- 분석: K_A × K_B grid 분석 + cheap approximation framework 정형화 = **1-2 일 (10-15h)**
- 문서화: 5/27 deck + 6/11 보고서 multi-table section = **0.5-1 일 (4-8h)**
- **총 cost: 약 15-25h**

#### E.6 박광현 review 기대 학술 가치

- **★ positive 강함**: paper §V-B "single-table KNN only" 제약 깨기 + cheap approximation axis (학습 비용 0 + 정확도 우위) 는 BDAI 연구실 측면 흥미
- ★ **challenge 가능**: "FactorJoin / Scardina / TKHist 와의 차별성?" → 답변 = vector similarity domain 한정 + Centroid tuple folding 의 학습 비용 0 + paper §V-B 와 직접 결합

#### E.7 timeline 적합성

- 5/15 박광현 미팅: 옵션 E 의 multi-table 영역 자문 권장
- 5/27 발표: cost 15-25h → D-13 까지 가능
- 6/11 보고서: 가능
- ★ risk = main narrative 분산. 옵션 E 가 main 되면 RQ1/RQ2/RQ3 trilogy + Pareto frontier 등 다른 axis 무게 분산.

#### E.8 hybrid 결합 가능성

- A + E: 옵션 A 의 정량 결과 + multi-table 확장. 가능 but **★ Agent C 권장 X** (옵션 E 가 main narrative 부상 시 RQ1/RQ2/RQ3 trilogy 무게 약화)
- ★ **Agent C 권장: 옵션 E 는 5/27 발표 + 6/11 보고서의 영역 별 axis 의 하나로 유지** (옵션 A 의 보조 finding 으로 Centroid tuple −0.84p 추가 우위 명시). main 화 X.

---

### 1.6 옵션 F — paper §V-A ECQO 영역과 비교 (Agent B 추가)

#### F.1 영역 정의 깊이 발산

**paper 어디**: §V-A ECQO 영역 (HNSW range query 1-2ms 정확 카디널리티). paper §VI-A 측정 결과 (Fig.4 page 8): pgvector ECQO 3 orders of magnitude speedup, VBASE 4 orders of magnitude.

**우리 어디로**: ECQO 측정 vs Adaptive Sampling 측정의 직접 paired Δ% 비교.
- 현 측정: §V-B (adaptive sampling) 한정 = 1001 file
- 추가 측정: ECQO 영역 9 cells × 17 method (인덱스 ON, range query) = 약 150 file

**학술 contribution 영역**: paper §V-A + §V-B 영역 종합 비교. paper main result 의 정량 grounding + Q-error 1.0 (ECQO) vs 1.05-1.7 (Adaptive Sampling) 의 gap 메커니즘 분석.

#### F.2 paper 추가 정독

paper §VI-A (Fig.4, page 8) verbatim:
> "ECQO performs a lightweight vector index probe during planning using the HNSW structure, which returns the exact number of qualifying tuples."

paper §VI-A 비교 baseline 부재: paper 가 ECQO vs Adaptive Sampling 의 cell 별 paired Δ% 비교 안 수행. paper 가 ECQO Q-error = 1.0 (deterministic) 으로 인정.

→ 옵션 F 학술 정당성 = **paper 가 안 수행한 cell 별 paired 비교 + Q-error gap 분석**.

#### F.3 literature check

- WebSearch "ECQO HNSW range query": Exqutor paper 본인. **Quantization-Enhanced HNSW** (OpenReview) + **Distribution-Aware Exploration for Adaptive HNSW Search** (2512.06636, 2025) — HNSW + cardinality estimation 영역 active.
- **Exact Cardinality Query Optimization with Bounded Execution Cost** (SIGMOD 2019) — ECQO 의 base paper. paper [73] reference.
- **Novelty: ★ weak-moderate** (paper main result 의 grounding axis). 단 paper 의 §V-A vs §V-B 영역 boundary 의 정량 비교는 paper 가 안 수행. 본 연구의 cell 별 paired 비교는 **valid contribution**.

#### F.4 우리 1001 file 재해석

- 옵션 A 의 모든 측정 (1001 file) = 옵션 F 의 §V-B side
- 추가 측정 = §V-A ECQO side (9 cells × 17 method = 150 file)

#### F.5 추가 측정 / 작업 cost

- **ECQO 측정 환경 setup**: HNSW 인덱스 ON 측정 환경 + range query 모드 = **0.5-1 일 (4-8h)**
- **측정**: 150 file ≈ **4-6h 서버 시간**
- **분석**: Q-error gap 의 paired Δ% + 메커니즘 분석 = **1 일 (8h)**
- **문서화**: 5/27 deck + 6/11 보고서 ECQO 비교 section = **0.5 일 (4h)**
- **총 cost: 약 20-30h**

#### F.6 박광현 review 기대 학술 가치

- **★ positive**: paper §V-A + §V-B 영역 종합 비교 framework
- ★ **challenge 가능**: "ECQO 가 인덱스 있을 때 deterministic Q-error 1.0 인데, 비교 의미?" → 답변 = paper 자체가 §V-A + §V-B 영역 boundary 의 cell 별 paired 비교 안 수행. Q-error gap 의 cell 별 메커니즘 (high-dim / skew) 분석 가치

#### F.7 timeline 적합성

- 5/15 박광현 미팅: 옵션 F 자문 권장 (paper §V-A + §V-B 영역 종합 비교 가치)
- 5/27 발표: cost 20-30h → D-13 까지 가능 (옵션 A 와 결합 시)
- 6/11 보고서: 가능

#### F.8 hybrid 결합 가능성

- **A + F**: 옵션 A 의 §V-B 정량 결과 + §V-A ECQO 비교 framework. **★ Agent C 권장 2순위 hybrid 의 한 component**.
- **A + B + F** (★ 2순위 권장): §V-A + §V-B 종합 + Eq 3-6 distribution-aware augment.

---

### 1.7 옵션 G — Streaming reservoir 산업 적용 main (Agent B 추가, ★★ 본 Agent C 격상)

#### G.1 영역 정의 깊이 발산

**paper 어디**: §V-B Algorithm 1 의사코드 Step 11 ("Sample n_inc more rows via Bernoulli"). paper streaming compatibility 영역 명시 X.

**우리 어디로**: reservoir method (P3 Streaming) 의 O(1) memory + <0.1s fit + −9.25% Δ% (CaseB) 의 산업 적용 main 화.
- 현 측정: reservoir 9 cells × 2 mode = 18 file (Pareto frontier 영역 C resource-first Top 1)
- 확장: streaming workload (OLTP TPC-H Q3/Q5 + insert stream) 직접 측정 + reservoir 의 memory footprint + insert latency overhead 측정

**학술 contribution 영역**: paper §V-B 의 streaming compatibility 영역 (paper main result 외) + 산업 적용 axis (O(1) memory + −9.25% 정확도 anchor 수준 동시).

#### G.2 paper 추가 정독

paper §VII Related Work (page 12):
> "One technique in query optimization for efficiently estimating selectivity and cost is sampling. Early works introduced random sampling for join size estimation [79], [80], while later approaches refined these ideas with adaptive sampling strategies [81]."

★ paper streaming reservoir 영역 명시 X. paper 측정 모두 batch 영역 (TPC-H/TPC-DS).

→ 옵션 G 학술 정당성 = paper 측정 boundary 외 영역의 산업 적용 contribution + paper §V-B framework 의 streaming compatibility 입증.

#### G.3 literature check

- **WebSearch "streaming reservoir sampling cardinality"**: "Cardinality Estimation in Streaming Graph Data Management Systems" (UW) + **GraphSketch** (streaming GDBMS) — streaming 영역 active.
- **Vitter 1985 reservoir sampling** (classical) — algorithm base
- **Chao 1982 weighted reservoir** = chao_weighted method (본 연구 Pareto frontier Top 5)
- **Random Sample Database (Olken-Rotem 1990)** = original reservoir in database. Lipton-Naughton 1990 [81] (paper reference) 의 base.
- **OLTP vs OLAP**: WebSearch 결과 "OLTP methods should have fast inference speed, while OLAP-targeting methods can tolerate higher inference latency" — 옵션 G 의 산업 positioning 강력.
- **Novelty: ★ moderate** (streaming compatibility + 산업 적용 axis + paper boundary 외 영역). 단 paper level review-grade 까지는 streaming 측정 framework 자체 contribution 보강 필요.

#### G.4 우리 1001 file 재해석

- reservoir 측정 18 file + chao_weighted 측정 18 file + thompson_sampling 18 file = **streaming method 측정 base 54 file** valid
- Pareto frontier 영역 C (resource-first) reservoir Top 1 + zorder_morton Top 2 + minibatch_partial Top 3 = 옵션 G 의 main result base
- 추가 측정 (streaming workload) = 약 30-50 file

#### G.5 추가 측정 / 작업 cost

**Option G1 — narrative only (저비용)**:
- 측정 추가: **0** (현 Pareto frontier 결과 그대로)
- 분석: 산업 적용 narrative 정리 + 영역 A/B/C 영역별 추천 = **0.5 일 (4h)**
- 문서화: 5/27 deck industry highlight slide + 6/11 보고서 industry section = **0.5 일 (4h)**
- **총 cost: 약 5-8h** ★ 가장 cheap option

**Option G2 — streaming workload 직접 측정**:
- streaming framework 구축: insert stream + TPC-H Q3/Q5 + reservoir = **2-3 일 (16-24h)**
- 측정: 30-50 file ≈ **2-3h 서버 시간**
- 분석 + 문서화: **1-2 일 (8-16h)**
- **총 cost: 약 25-40h**

#### G.6 박광현 review 기대 학술 가치

- **★ positive 매우 강함**: 산업 적용 axis + reservoir O(1) memory + anchor 수준 정확도 = 매우 강력한 narrative
- BDAI 연구실 측면 = DB rigor + 산업 적용 가능성 양쪽 모두 발현
- **paper-grade 가능성**: 옵션 G2 의 streaming framework 측정 시 paper level contribution 가능

#### G.7 timeline 적합성

- **G1 (narrative only)**: 5/27 + 6/11 timeline ★ 안전 (5-8h)
- **G2 (streaming 측정)**: 5/27 까지 가능하나 cost 25-40h
- 박광현 미팅 시 G1 vs G2 선택

#### G.8 hybrid 결합 가능성

- **A + G1** (★ 본 Agent C 권장 1순위): 옵션 A 정직 narrative + reservoir industry highlight. 총 cost 10-15h, timeline 안전.
- **A + G2 + B partial**: review-grade 접근. cost 35-50h.

---

### 1.8 옵션 H — TPC-DS 확장 (Agent B 추가, 본 Agent C 폐기 권장)

#### H.1 영역 정의 깊이 발산

**paper 어디**: §VI-C Fig.10 (page 10) — paper 가 TPC-DS 7 query (Q7, Q12, Q19, Q42, Q72, Q98) 측정 완료. ECQO context (인덱스 ON, SF=10) 한정.

**우리 어디로**: TPC-DS 영역의 §V-B (adaptive sampling, 인덱스 없을 때) 측정. paper 가 안 수행한 영역.

**학술 contribution 영역**: paper benchmark coverage 완전성 (TPC-H + TPC-DS).

#### H.2 paper 추가 정독

paper §VI-C (Fig.10, page 10) verbatim:
> "Evaluation on TPC-DS. To further validate the effectiveness of Exqutor on diverse workloads, we conducted experiments on the TPC-DS based Vector-augmented SQL analytics... As shown in Figure 10, the results demonstrate consistent performance improvements, with query execution times achieving speedups of up to 109.6×."

★ paper TPC-DS 측정 = ECQO context (Fig.10 = "pgvector vs pgvector+Exqutor with vector indexes"). adaptive sampling context (§V-B) TPC-DS 측정 X.

→ 옵션 H 학술 정당성 = paper §V-B benchmark coverage 완전성.

#### H.3 literature check

- TPC-DS benchmark 자체는 widely studied (Poess-Floyd 2000 / Nambiar-Poess 2006, paper references [23] [24])
- vector-augmented TPC-DS 영역 = Exqutor paper 가 처음 도입
- **Novelty: weak** (paper boundary 확장 axis 만). paper level review-grade 측면 약함.

#### H.4 우리 1001 file 재해석

- 현 측정 = TPC-H Q3 중심 (Fig.4 + Fig.5/6 + Fig.7/8/9 영역)
- TPC-DS 측정 = 0

#### H.5 추가 측정 / 작업 cost

- **TPC-DS 환경 setup**: TPC-DS database + 7 query (paper 측정 영역) + vector embedding column 추가 = **3-5 일 (24-40h)**
- 측정: 7 query × 17 method × 2 mode × 10 trial ≈ 240 file ≈ **8-12h 서버 시간**
- 분석 + 문서화: **2 일 (16h)**
- **총 cost: 약 50-70h**

#### H.6 박광현 review 기대 학술 가치

- **moderate**: paper benchmark coverage 완전성 인정 가능
- ★★ **challenge 가능**: "TPC-H Q3 측정 portfolio 1001 file 만으로 충분한 보편성 입증인데, TPC-DS 측정 의의는?"
- 박광현 답변 가능성 = "novelty 측면 약함, future work 영역"

#### H.7 timeline 적합성

- **5/27 발표**: cost 50-70h → ★ 무리 (D-13 timeline 압박 + 환경 setup 부담)
- **6/11 보고서**: 가능하나 cost 부담 + 다른 옵션 우선
- ★★ **Agent C 권장: 옵션 H 폐기. 6/11 보고서 future work 영역 명시.**

#### H.8 hybrid 결합 가능성

- A + H: cost 50-70h → ★ 폐기 권장
- ★ Agent C 권장: 옵션 H 는 **future work 영역 명시** 만.

---

## 2. 옵션 발산 추가 (8 외 새 방향)

### 2.1 옵션 I — 다중축 통합 분석 (paradigm × method × cell × axis 종합 visualization)

**영역 정의**: 본 연구 1001 file 의 raw 데이터를 method × paradigm (8) × cell (9) × axis (정확도/안정성/메모리/fit time) 의 4D heatmap visualization 으로 학술 contribution.

**학술 가치**: ★ moderate (visualization + analysis axis novelty). paper level 까지는 약함, but 5/27 발표 + 6/11 보고서 visual contribution 강력.

**cost**: ~10-15h (visualization 코드 + 분석).

**timeline 적합성**: 5/27 + 6/11 모두 가능.

**Agent C 권장**: ★ 옵션 A + I 결합 권장 (visualization 강화).

### 2.2 옵션 J — 학습 비용 0 + multi-method ensemble framework

**영역 정의**: 본 연구 12 anchor method 의 산술 평균 ensemble (단일 method 만 사용 vs 2-3 method 결합) 영역. CaseB ensemble 의 확장.
- 현 측정: B1 + anchor method (2-way ensemble)
- 확장: anchor method 2 개 + anchor method 3 개 의 ensemble Δ%

**학술 가치**: ★ moderate (ensemble axis + 학습 비용 0). 단 ensemble literature (Bagging / Boosting) 활발해서 novelty 부분 포함.

**cost**: 측정 ~100 file (3-4h 서버) + 분석 ~10h = **15-20h**

**timeline 적합성**: 5/27 가능. 단 main narrative 분산 위험.

**Agent C 권장**: 6/11 보고서 부록 영역.

### 2.3 옵션 K — 박광현 BDAI 연구실 다른 paper 영역 살피기

**영역 정의**: 박광현 교수 다른 publications (BDAI Research group GitHub) 와의 align 영역 확장.
- ECQO base paper (SIGMOD 2019) 또는 BDAI 다른 paper 의 영역 살피기

**학술 가치**: ★ moderate (박광현 교수 자문 alignment).

**cost**: literature review ~5h.

**timeline 적합성**: 5/15 박광현 미팅 자문 항목으로 권장.

**Agent C 권장**: 박광현 미팅 시 자문.

---

## 3. Hybrid 결합 가능성 (1-3 추천 hybrid)

### 3.1 ★ 1순위 — A + G1 (현 narrative + reservoir streaming industry highlight)

**구성**:
- 옵션 A 전체 (현 narrative + Eq 1 한정 disclosure + Algorithm 1 14-step box)
- 옵션 G1 narrative only (reservoir O(1) memory + −9.25% 정확도 anchor 수준 industry highlight)

**총 cost: ~10-15h** (옵션 A 5-8h + 옵션 G1 5-8h)

**timeline**: ★ 안전 (5/27 + 6/11 모두 여유)

**학술 가치**: ★★ 학부 capstone 매우 강력 + 산업 contribution

**박광현 review 기대**:
- positive: paper exact 재현 + 1001 file portfolio + 정직 disclosure + 산업 적용 axis
- challenge 가능: review-grade 측면 약함 → 옵션 B 권유 가능

**5/27 발표 storyline**: §1 problem → §2 paper §V-B 재현 (Algorithm 1 14-step) → §3 단독/결합 정량 결과 (RQ1/RQ2/RQ3) → §4 자원 효율 Pareto + reservoir industry highlight → §5 honest limitation (Eq 2-6 영역 future work)

### 3.2 ★ 2순위 — A + B + F partial (현 narrative + Eq 2-6 확장 + ECQO 비교)

**구성**:
- 옵션 A 전체
- 옵션 B (Eq 2-6 dynamic batch loop 의 distribution-aware augment)
- 옵션 F partial (ECQO Q-error gap 비교 framework, 측정은 paper 결과 인용 또는 1-2 cell 만 직접 측정)

**총 cost: ~35-50h** (A 5-8h + B 25-35h + F partial 8-15h)

**timeline**: △ 가능 (자원 Max + 5/15 박광현 합의 + 5/27 까지 가속화 필요)

**학술 가치**: ★★★ review-grade 접근 (paper main contribution 영역 확장 + paper boundary 영역 비교)

**박광현 review 기대**:
- ★ positive 매우 강함: paper Eq 2-6 영역 확장 + paper §V-A + §V-B 종합 비교
- review-grade publication 가능성

**5/27 발표 storyline**: §1 problem → §2 paper Eq 1-6 + Algorithm 1 → §3 §V-A vs §V-B 영역 paired 비교 (F) → §4 §V-B Eq 1 한정 contribution (A 의 RQ1/RQ2/RQ3) → §5 §V-B Eq 2-6 확장 contribution (B 의 dynamic batch augment) → §6 Pareto frontier + industry → §7 limitations

### 3.3 3순위 — A + C (현 narrative + Neyman paradox sel-dependency)

**구성**:
- 옵션 A 전체
- 옵션 C (Neyman paradox sel-dependency 메커니즘 일반화)

**총 cost: ~20-25h** (A 5-8h + C 15-20h)

**timeline**: ★ 가능

**학술 가치**: ★ vector similarity novelty (단 Cochran 1977 §5.5 challenge 대비)

**박광현 review 기대**:
- positive: vector similarity domain 의 정량 발현
- ★ challenge 가능: Cochran 1977 §5.5 ("σ_j uniform → Neyman ≈ Prop" known result) — 대응책 필수 (vector domain 한정 + K-means metric = query metric alignment 의 자연 발현 메커니즘 강조)

**5/27 발표 storyline**: §1 problem → §2 paper §V-B + Eq 1-6 → §3 §V-B Eq 1 한정 contribution (A 의 RQ1/RQ2/RQ3) → §4 RQ2 Neyman paradox 메커니즘 일반화 (C 의 sel-dependency + classical theory positioning) → §5 Pareto frontier + industry → §6 limitations

---

## 4. 최종 권장 path

### 4.1 5/15 박광현 미팅 strategic discussion 항목 (paper-grade 형태)

★ 박광현 교수 (BDAI 연구실 DB 전공) 5/15 14:00 미팅 (D-1) 자문 항목 6:

#### 자문 1 — 옵션 A 의 학부 capstone 충분성 (★★★ critical)

**질문**: "본 연구의 contribution scope = paper §V-B Eq 1 한정 (Bernoulli sample 추출 방식 의 distribution-aware augment). paper Eq 2-6 (dynamic batch loop, paper differentiation 영역) 안 건드림. 학부 캡스톤 측면 + 5/27 발표 + 6/11 보고서 narrative 측면 옵션 A 단독으로 충분한가?"

**예상 답변**:
- 학부 capstone-grade: 충분 (paper exact 재현 + 1001 file portfolio + 정직 분류)
- review-grade: 약함 (paper main contribution 영역 안 건드림)

#### 자문 2 — 옵션 B (Eq 2-6 확장) 의 5/27 timeline 가능성 (★★ major)

**질문**: "옵션 B = group-aware dynamic batch loop (paper Eq 3-6 의 distribution-aware augment). cost 25-35h. 5/27 까지 측정 + 분석 + 슬라이드 작성 가능한가? 자원 + 서버 (capstone2026) 활용 시 가속 가능?"

**예상 답변**:
- 자원 Max + 가속화 가능 → 5/27 까지 가능
- 단 risk = timeline 압박 (다른 작업 dependence)

#### 자문 3 — 옵션 C 의 Cochran 1977 §5.5 challenge 대응 (★★ major)

**질문**: "본 연구 Neyman paradox 발견 (σ_j narrow → Neyman ≈ Prop) 은 Cochran 1977 §5.5 ('the gain in accuracy from Neyman allocation compared to proportional allocation is pretty small') 안에 부분 포함. vector similarity domain 의 정량 발현 + K-means metric = query metric alignment 의 자연 발현 메커니즘으로 novelty 확보 가능?"

**예상 답변**:
- vector domain 의 정량 발현 = novel
- 단 paper level publication 까지는 generalization 보강 필요 (cosine / Manhattan / 다른 datasets)

#### 자문 4 — 옵션 G (reservoir industry positioning) 의 학술 가치 (★ minor)

**질문**: "본 연구 Pareto frontier 영역 C (resource-first) 의 reservoir O(1) memory + −9.25% 정확도 anchor 수준 결과는 산업 적용 측면 매우 강력. 학술 paper 측면 contribution 으로 평가 가능?"

**예상 답변**:
- 산업 contribution + paper boundary 외 영역
- paper level 까지는 streaming workload 측정 framework 보강 필요 (옵션 G2)

#### 자문 5 — 옵션 F (ECQO 비교) 의 학술 가치 (★ minor)

**질문**: "paper §V-A ECQO 영역 (Q-error 1.0 deterministic) vs §V-B Adaptive Sampling 영역 (Q-error 1.05-1.7) 의 cell 별 paired Δ% 비교 framework. paper 가 안 수행한 영역. 학술 가치 + 5/27 timeline 가능?"

**예상 답변**:
- paper 영역 boundary 의 정량 비교는 valid contribution
- 측정 cost 20-30h → 5/27 timeline 가능

#### 자문 6 — 옵션 조합 추천 (★ summary)

**질문**: "본 연구 추천 hybrid 3 (A+G1 / A+B+F / A+C) 중 박광현 교수 추천 + BDAI 연구실 기조 + 5/27 + 6/11 timeline 적합성 추천?"

**예상 답변**:
- 안전 path: A + G1
- review-grade 접근: A + B + F partial
- vector similarity novelty: A + C (단 Cochran 1977 challenge 대비)

### 4.2 5/27 발표 storyline 추천 (D-13)

★ Agent C 추천 = **hybrid 1순위 (A + G1) 또는 hybrid 2순위 (A + B + F partial)** 박광현 미팅 결과에 따라.

**hybrid 1순위 (A + G1) storyline (15-20 slide)**:
1. **Title + Team** (1 slide)
2. **Problem motivation** (1 slide) — VAQ + paper §V-B 영역 + 우리 contribution scope
3. **Paper §V-B Algorithm 1 14-step + 우리 contribution scope** (2 slide) — Eq 1 한정 + Eq 2-6 paper exact 유지 명시
4. **RQ1 paper exact 재현** (2 slide) — Fig.12 mean qe_trim 1.618 vs paper 1.69 = -4.3% 재현
5. **RQ2 5-way + Neyman paradox sel-dependency** (2 slide) — DEEP sel=0.01 paired 한정 명시 + sel=0.1 영역 역전
6. **RQ3 정량 결과** (3 slide) — 단독 best −10.17% / 결합 best −7.37% / 92.5% paired
7. **Pareto frontier + reservoir industry highlight (G)** (2 slide) — Pareto Top 5 (sparse_rp / chao_weighted / **neuram** / pca1d / hilbert) + 영역 C reservoir O(1) memory + -9.25% 정확도
8. **40 폐기 method 정직 분류** (1 slide) — 자원 7 + audit 23 + 정합성 10
9. **byte-identical caveat** (1 slide backup) — 9 nominal cells / 6 unique cells
10. **Limitations + Future work (옵션 B / C / D / E / H 영역)** (1 slide) — Eq 2-6 영역 + 정보 수준 L0-L4 + multi-table + TPC-DS
11. **Conclusion + Q&A** (1 slide)

### 4.3 6/11 보고서 outline 추천 (D-28)

**hybrid 1순위 (A + G1) outline**:

**§1 서론** — VAQ + paper §V-B 영역 + 본 연구 contribution scope (Eq 1 한정 + Eq 2-6 honest limitation)

**§2 관련 연구** — paper §VII Related Work + classical sampling theory (Cochran 1977 §4.5 + Lipton-Naughton 1990) + 본 연구 positioning

**§3 paper §V-B 재현** — Algorithm 1 14-step + hyperparam paper exact + Fig.12 mean qe_trim 1.618 재현

**§4 RQ1 paper baseline 재현** — Bernoulli 9 cells × 5 trial = 45 file 측정

**§5 RQ2 5-way 표본 할당** — DEEP/SIFT/SSN sf=100 × sel{0.01, 0.10} × 5 way × 5 trial = 약 250 file 측정 + Neyman paradox sel-dependency 메커니즘 (★ sel=0.01 한정 명시)

**§6 RQ3 단독/결합 + 8 paradigm × 56 method** — 9 cells × 56 method × 3 modes = 1001 file 측정

**§7 자원 효율 Pareto frontier** — Pareto Top 5 + 영역 A/B/C 산업 적용 추천

**§8 reservoir industry highlight** — O(1) memory + −9.25% 정확도 anchor 수준 동시 + paper boundary 외 영역의 산업 contribution

**§9 honest limitation** — Eq 2-6 영역 + 정보 수준 L0-L4 + multi-table + TPC-DS 영역 future work

**§10 결론** — paper exact 재현 + 1001 file portfolio + 정직 disclosure + 산업 적용 + paper main contribution 영역의 future work

**부록 A** — Algorithm 1 14-step 의사코드 (reviewer defense)
**부록 B** — 40 폐기 method 정직 분류 (자원 7 + audit 23 + 정합성 10)
**부록 C** — byte-identical caveat (9 nominal / 6 unique cells)
**부록 D** — REPORT v11 1362 line raw data

### 4.4 미정 영역 / future work / paper-grade publication 가능성

**5/27 + 6/11 까지 미해결 영역**:
1. paper §V-B Eq 2-6 dynamic batch loop 의 distribution-aware augment (옵션 B)
2. Neyman paradox 의 일반화 measurement (cosine / Manhattan / 다른 datasets, 옵션 C)
3. L1 (skew flag only) 영역 method 개발 + 측정 (옵션 D)
4. multi-table joint distribution generalization (옵션 E, Centroid tuple K granularity grid)
5. ECQO Q-error gap cell 별 paired 분석 (옵션 F)
6. streaming workload 직접 측정 framework (옵션 G2)
7. TPC-DS 영역 §V-B 측정 (옵션 H)

**paper-grade publication 가능성 평가**:
- **현 상태 (옵션 A 단독)**: 학부 capstone-grade ★★ 매우 강력, paper level ★ 약함 (paper main contribution 영역 안 건드림 + novelty weak)
- **A + B + F (★ Agent C 2순위 추천)**: paper review-grade 접근 가능, SIGMOD/VLDB workshop / EDBT short paper level
- **A + B + C + F (장기, 5/27 후)**: SIGMOD/VLDB main paper 까지 generalization 측정 보강 필요 (cosine / Manhattan / 다른 datasets / TPC-DS / streaming framework)
- **장기 paper publication 시 timeline**: 5/27 capstone 발표 후 + 6/11 보고서 완료 + 7-8월 generalization 측정 + 9월 SIGMOD/VLDB submission

---

## 5. 미정 영역 / future work / paper-grade publication 가능성

### 5.1 미정 영역

**5/15 박광현 미팅 결과에 따라 결정**:
- hybrid 1순위 (A + G1) vs 2순위 (A + B + F) vs 3순위 (A + C) 선택
- 옵션 B 의 5/27 timeline 가능성 confirm
- 옵션 C 의 Cochran 1977 §5.5 challenge 대응책 confirm

### 5.2 future work 영역 (6/11 보고서 명시)

- 옵션 B (Eq 2-6 distribution-aware augment) — paper main contribution 영역 확장
- 옵션 C (Neyman paradox 일반화) — vector similarity domain 의 정량 발현 + classical theory positioning
- 옵션 D (L0-L4 framework + L1 method) — framework contribution
- 옵션 E (multi-table generalization + Centroid tuple grid) — paper §V-B "single-table KNN only" 제약 깨기
- 옵션 F (ECQO Q-error gap cell 별 분석) — paper §V-A + §V-B 영역 boundary 비교
- 옵션 G2 (streaming workload framework) — paper boundary 외 영역의 산업 contribution
- 옵션 H (TPC-DS §V-B 측정) — benchmark coverage 완전성

### 5.3 paper-grade publication 가능성 (장기)

- **단기 (5/27 + 6/11)**: 학부 capstone-grade ★★ 매우 강력
- **중기 (7-9월 SIGMOD/VLDB workshop / EDBT short paper)**: 옵션 A + B + F 또는 A + B + C 결합
- **장기 (1-2년, SIGMOD/VLDB main paper)**: generalization 측정 보강 + 정보 수준 framework + multi-table + streaming + TPC-DS 종합

---

## 6. main thread 종합 권장 사항

### 6.1 박광현 5/15 미팅 자료 핵심 추가 / 정정 항목 (★★★ critical)

1. **wording 정정 룰 (Agent B critical)**: "5 단계 中 1 단계" → "Eq 1 (Bernoulli) 대체 vs Eq 2-6 (dynamic batch loop = paper differentiation) 유지"
2. **Neyman paradox scope 명시**: "DEEP sf=100 sel=0.01 paired (n=455) 한정, sel=0.1 영역 역전"
3. **σ_j range oracle interpretation 명시**: "REPORT v11 oracle interpretation, 직접 측정 미완"
4. **Pareto Top 5 명단 정정**: "sparse_rp / chao_weighted / **neuram** / pca1d / hilbert" (reservoir 영역 C 별도)
5. **Cochran 1977 §5.5 challenge 대비**: 옵션 C 선택 시 mechanism 자체 known 인정 + vector domain 정량 발현 axis 강조
6. **byte-identical caveat**: 9 nominal cells / 6 unique cells × 56 method

### 6.2 5/27 발표 deck v6 핵심 update 항목

1. ★ hybrid 1순위 (A + G1) 또는 2순위 (A + B + F partial) 박광현 미팅 결과 반영
2. Algorithm 1 14-step box (Agent B critical)
3. Eq 2-6 영역 honest limitation 또는 옵션 B 확장 결과
4. Pareto frontier + reservoir industry highlight (옵션 G1)
5. 40 폐기 method 정직 분류 (자원 7 + audit 23 + 정합성 10)
6. byte-identical caveat backup slide

### 6.3 6/11 보고서 outline 핵심 update 항목

1. §1 서론 의 contribution scope 정정 (Eq 1 한정 명시)
2. §2 관련 연구 의 Cochran 1977 §5.5 + Lipton-Naughton 1990 [81] positioning
3. §3 paper §V-B 재현 의 Algorithm 1 14-step + paper exact 입증
4. §4-§6 RQ1/RQ2/RQ3 (현 narrative 유지 + scope 정정)
5. §7 자원 효율 Pareto frontier + 산업 적용 axis
6. §8 reservoir industry highlight (옵션 G1)
7. §9 honest limitation + future work 영역 명시
8. 부록 A-D (Algorithm 1 + 폐기 method + byte-identical + raw data)

### 6.4 본 Agent C 의 종합 권장 path 1줄 요약

★★★ **5/15 박광현 미팅 자문 후 hybrid 1순위 (A + G1, 안전) 또는 2순위 (A + B + F partial, review-grade) 결정. 옵션 C 의 Cochran 1977 §5.5 challenge 대비 권장. 옵션 D / E 단독 main / H 폐기.**

---

## 7. 사용자 의사결정 위임

★ 본 Agent C 의 deep dive 결과 = brainstorming 발산 + literature 검증 + 정직 disclosure 권장 + 추천 hybrid 3. 실제 옵션 선택은:
1. 사용자 (조현빈) 선호
2. 5/15 박광현 미팅 자문 결과
3. 5/27 timeline 가능성 (자원 Max + 가속화 여부)
의 종합으로 결정.

★ Agent C 의 자체 추천 (사용자 결정 위임): **hybrid 1순위 (A + G1)** 안전 path + 박광현 자문 결과 옵션 B 가능 시 **hybrid 2순위 (A + B + F partial)** 로 확장.

---

## END

본 산출 file: `_internal/handoff/active/agent_C_deep_dive_8옵션_종합권장_20260514_2200.md`

main thread 가 본 Agent C 결과 + Agent A (78%) + Agent B (정정 7) 의 종합으로:
- 박광현 5/15 미팅 자료 정정 (★★★ critical 6 영역)
- 5/27 발표 deck v6 핵심 update (6 영역)
- 6/11 보고서 outline 핵심 update (8 영역)

수행 권장. 사용자 + 박광현 미팅 합의로 hybrid 1순위 (안전) 또는 2순위 (review-grade) 결정.

작성: 2026-05-14 22:00 KST · Agent C · paper PDF 전체 정독 (§V-A + §V-B + §VI + §VII + §VIII + Algorithm 1 14-step) + Agent A (78%) + Agent B (정정 7) + WebSearch 7 건 (Cochran 1977 §5.5 critical 발견) + measurement 9 analysis file 직접 read 완료
