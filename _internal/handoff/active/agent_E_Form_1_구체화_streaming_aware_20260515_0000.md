# Agent E — Form 1 (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ) 구체화 deep dive

> **작성**: 2026-05-15 00:00 KST · Agent E · main thread 지시 "Form 1 main theme fix 후 구체화 deep dive (Technical / 측정 / 5/27 / 6/11 / 5/15 박광현 review form / publication / 한계 / 종합)"
> **검증 기조**: paper PDF + Agent A/B/C/D 4 호출 결과 종합 + WebSearch 4 건 (Al-Kateb-Lee-Wang ISJ 2014 SRS / SSDBM 2010 SRS / CE4HD VLDB 2024 / Ada-ef arxiv 2512.06636) + 본 연구 1001 file 재해석
> **★★★ wording 정정 룰 (Agent B critical, Agent E 필수 사용)**:
>   - ❌ 폐기: "5 단계 中 1 단계"
>   - ✓ 정정: "Eq 1 (Bernoulli) 대체 vs Eq 2-6 (dynamic batch loop = paper differentiation) 유지/통합"
>   - Algorithm 1 14-step 中 Step 11 ("Sample n_inc more rows via Bernoulli") 의 sample 추출 방식 augment
>   - Neyman paradox = sel=0.01 한정 명시 (selectivity-dependent)
>   - σ_j range = oracle interpretation 명시 (직접 측정 미완)
>   - Pareto Top 5 = "sparse_rp / chao_weighted / neuram / pca1d / hilbert" (reservoir 영역 = 본 Form 1 main, 별도)
>   - byte-identical = 6 unique cells (9 nominal)
>   - 학부 capstone = ★★ 매우 강력
> **사용자 정책 (fix 모드, 공유 완성까지 변경 X)**: main theme = Form 1, 보완 paper 한계 L1+L5+L6, 측면 = 대체+보완+개선+추가검증

---

## 0. 핵심 결론 요약 (TL;DR)

본 Agent E 의 Form 1 (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ) 구체화 결과 다음과 같다.

| 영역 | 핵심 결정 | cost (h) | 학술 가치 | timeline 적합성 |
|---|---|---:|---|---|
| **Technical** | reservoir sampling O(1) memory + BIRCH/CluStream-style online cluster maintenance + paper Eq 2-6 dynamic batch loop 통합 + 분포 인지 stratification axis 추가 | 0 (설계) | ★★★ paper main 영역 확장 | ★ 안전 (설계 단계) |
| **측정** | 4 측면 (대체+보완+개선+추가검증) × 3 dataset × 2 sel × shifting workload simulation + 4-way 비교 (Bernoulli + SelNet + CE4HD + Ada-ef + 본) | 100-150h | ★★★ paper-grade | △ 가능 (자원 Max + 5/27 가속) |
| **5/27 발표** | 20 slide framework (problem / paper §V-B 영역 / Form 1 contribution / shifting workload simulation / 4-way 비교 / paper 한계 L1+L5+L6 보완 / limitation / future work) | 10-15h | ★★ review-grade | ★ 안전 |
| **6/11 보고서** | 학부 capstone + paper-grade 접근 (Introduction / Background / Related Work / 본 연구 방법론 / 측정 결과 / 한계 / future work / 결론) + 부록 5 종 | 20-30h | ★★★ paper-grade 가능 | ★ 안전 |
| **5/15 박광현 review form** | 1-2 page 자료 + Form 1 학술 정당성 + streaming-aware novelty + 측정 plan 적절성 + 5/27 timeline + paper-grade venue + 박광현 본업 align 자문 6 항목 | 1-2h (정리) | ★★★ critical | ★ 안전 |
| **paper-grade publication** | SIGMOD short paper / VLDB / ICDE position paper / CIKM / SoCC / DASFAA / EDBT 中 SIGMOD/VLDB workshop 또는 EDBT short paper 추천 (timeline 7-9월 submission) | -- | ★★ review-grade | 9-12월 submission |
| **본 Form 1 한계** | 우리 KM20 = batch 전제 / online cluster maintenance accuracy 손실 / 1001 file streaming axis 측정 X / framework novelty (각 method 자체 신규 X) | -- | -- | -- |

★★★ **5/15 박광현 미팅 1st priority discussion**: Form 1 학술 정당성 (paper §V-B 후속 연구 form 적절성) + streaming-aware + 분포 인지 통합 framework novelty + 4-way 비교 framework + paper-grade publication 가능성 + 박광현 본업 (RELOAD / CANNON / DFLOP) align.

★★★ **본 Agent E 의 정직 disclosure**:
1. **streaming-aware stratified reservoir sampling** 은 Al-Kateb-Lee-Wang 등 2010-2014 literature 에 이미 존재 (SSDBM 2010 + ISJ 2014). vector similarity range query + cardinality estimation domain 의 정량 발현이 novel.
2. **online cluster maintenance** 은 BIRCH 1996 + CluStream 2003 + mini-batch K-means 등 classical literature 존재. 본 연구 contribution = paper §V-B Adaptive Sampling framework 에 통합 axis.
3. **4-way 비교 framework** (Bernoulli + SelNet + CE4HD + Ada-ef + 본) 의 framework axis 자체가 paper §VI-D Fig.12 영역 확장.

---

## 1. Technical design 구체 (streaming-aware stratified sampling 알고리즘 + pseudo-code + paper Eq 1-6 통합)

### 1.1 알고리즘 design 영역 정의

**main theme**: Streaming-aware Distribution-Conscious Cardinality Estimation for Vector-augmented Analytical Queries: Extending Exqutor's §V-B Framework.

**핵심 design 4 영역 (사용자 명시 4 측면)**:

| 측면 | 영역 | paper 영역 | 본 연구 영역 |
|---|---|---|---|
| **대체** | Bernoulli random → distribution-aware reservoir + online cluster | Eq 1 (Bernoulli sample 추출) | stratified reservoir sampling (각 cluster 별 O(1) memory) |
| **보완** | paper §VI-D limitation framework (SelNet 만 비교) | §VI-D Fig.12 SelNet | 4-way 비교 framework (Bernoulli + SelNet + CE4HD + Ada-ef + 본) |
| **개선** | paper §V-B Eq 2-6 distribution shift augment | Eq 3-6 dynamic batch loop | group-aware momentum V_{j,t} + group-aware n_inc 분배 |
| **추가검증** | paper §VI-B "shifting workloads" 정량 측정 | §VI-B + Fig.6 paper 명시 영역 | concept drift simulation + 정량 measurement |

### 1.2 알고리즘 4 component (Form 1 핵심)

#### 1.2.1 Component A — Stratified Reservoir Sampling (paper Eq 1 대체)

**input**: data stream D = {x_1, x_2, ...} (streaming axis), query Q, sample budget N=385 (paper exact 유지), cluster count K=20 (RQ2/RQ3 정합)

**algorithm**:
```
Initialize:
  reservoir R_j = [] for j = 1, ..., K     # K=20 cluster 별 reservoir
  cluster centroids C_j initialized via online init (first 5K samples)
  reservoir budget n_j = N / K = 385/20 ≈ 20 per cluster (Equal allocation default)

For each new tuple x_t in D (streaming):
  j* = argmin_j ||x_t - C_j||₂          # 가장 가까운 cluster
  if |R_{j*}| < n_{j*}:                  # reservoir 빈 자리 있음
    R_{j*}.append(x_t)
  else:                                  # Vitter 1985 reservoir sampling rule
    r = random_int(0, t-1)
    if r < n_{j*}:
      R_{j*}[r] = x_t                    # replace with prob n_{j*}/t

  Update C_j incrementally (BIRCH CF-tree style):
    LS_{j*} += x_t                       # linear sum
    SS_{j*} += x_t ⊙ x_t                 # squared sum
    n_{j*} += 1
    C_{j*} = LS_{j*} / n_{j*}            # mean

Return: R = ⋃_j R_j (stratified sample)
```

**memory cost**: O(N × d) for reservoir + O(K × d) for cluster centroids (linear sum + squared sum) = **O((N + K) × d)** ≈ O(N × d) since K=20 << N=385.

**comparison**:
- paper Eq 1 Bernoulli: O(N × d) memory + random 추출, batch 환경 한정 (전체 데이터 access 필요)
- 본 Form 1 SRS: O(N × d) memory + streaming compatible + 분포 인지

#### 1.2.2 Component B — Online Cluster Maintenance (BIRCH/CluStream + Mini-batch K-means hybrid)

**선택 reasoning (3 option 中 선택)**:

| Option | 장점 | 단점 | 본 연구 적합성 |
|---|---|---|---|
| **incremental K-means** (Sculley 2010 mini-batch) | 간단 + scikit-learn 구현 가능 + memory O(K × d) | concept drift 적응 약함 | ✓ baseline |
| **BIRCH (Zhang 1996)** | CF-tree O(K × d) memory + 단일 pass + concept drift 적응 | implementation complex | ★ **본 Form 1 채택** |
| **CluStream (Aggarwal 2003)** | micro-cluster + pyramidal time frame | overhead higher | △ future work |

★★★ **본 Form 1 채택 = BIRCH CF-tree** (Zhang-Ramakrishnan-Livny 1996 SIGMOD). 이유:
1. **단일 pass streaming** = paper §V-B 의 sequential scan 환경 (인덱스 없을 때) 와 직접 align
2. **CF (Cluster Feature) tuple = (N_j, LS_j, SS_j)** O(d) per cluster, K cluster total O(K × d) memory
3. **σ_j² 추정 가능**: σ_j² = SS_j / N_j − (LS_j / N_j)² (online 계산 가능) → distribution-aware stratification 의 axis 직접 지원
4. **scikit-learn `Birch` 구현** 활용 가능 (cost 약화) — `sklearn.cluster.Birch(n_clusters=20)` + `partial_fit(X)` API

**algorithm (BIRCH-style online cluster)**:
```
Initialize:
  CF-tree T = empty
  Birch threshold T_b = 0.5 × min_distance_between_initial_centroids
  K target = 20

For each new tuple x_t in D:
  Insert x_t into T:
    Find closest leaf cluster CF_j = (N_j, LS_j, SS_j)
    if dist(x_t, C_j) ≤ T_b:
      CF_j ← (N_j + 1, LS_j + x_t, SS_j + x_t ⊙ x_t)   # absorb
    else:
      create new CF leaf for x_t

  if T 가 너무 큼 (M_T > M_target):
    Rebuild T with larger T_b                  # CF-tree threshold 증가
    (BIRCH 의 standard procedure)

Periodically (e.g., every 50 queries = paper §V-B period P):
  K-means on leaf CFs → K=20 final clusters
  Update centroids C_j and σ_j²_j for stratification
```

**reasoning 보강**:
- paper §V-B Algorithm 1 의 "every 50 queries" period P 와 직접 align (paper Eq 6 lr decay 의 매 iteration trigger 와 결합 가능)
- BIRCH 의 K-means refinement 단계 = paper 의 "period P 마다 sample size update" trigger 와 align

#### 1.2.3 Component C — Adaptive Batch (paper Eq 2-6 통합)

**input**: paper §V-B Algorithm 1 14-step + 본 Form 1 의 group-aware augment

**algorithm (Step 1-14 paper exact 유지 + Step 11 augment)**:
```
# Paper §V-B Algorithm 1 (14-step)
Step 1: N = ⌈z² · P̂ · (1 − P̂) / e²⌉ = 385                    # paper Eq 1 유지
Step 2: V_0 = 0, η_0 = 0.1, t = 0                              # paper init
Step 3: For each query q in workload:
Step 4:   sample S = StratifiedReservoirSample(D, n_j, C_j, σ_j²_j)   # 본 Form 1 Component A 대체
Step 5:   evaluate similarity over S → estimate Card_esti(q)
Step 6:   observe Card_true(q)                                  # from query execution
Step 7:   Q-error_t = max(Card_esti/Card_true, Card_true/Card_esti)   # paper Eq 2 유지
Step 8:   if (t mod 50) == 0:                                   # paper period P 유지
Step 9:     δ_t = α · (Q-error_t − β) − (100 − α) · sampling_ratio   # paper Eq 3 유지
Step 10:    V_t = m · V_{t-1} + η_t · δ_t                       # paper Eq 4 유지
Step 11:    n_inc = N₀ · max(1, β · σ̂²_t / α)                   # paper sampling_size update Eq 5

         ★ 본 Form 1 augment (Step 11 augment):
         group-aware n_inc 분배:
           n_inc_j = n_inc · (N_j · σ_j) / Σ_k (N_k · σ_k)      # Neyman allocation (paper 미사용)
           or
           n_inc_j = n_inc · N_j / Σ_k N_k                       # Proportional (paper 미사용, 본 연구 권장)
         각 cluster j 별로 reservoir n_inc_j tuple 추가
         (StratifiedReservoirSample with augmented budget)

Step 12:    sampling_size_{t+1} = sampling_size_t + V_t          # paper Eq 5 유지
Step 13:    η_{t+1} = γ · η_t                                    # paper Eq 6 유지 (lr decay)
Step 14:  t = t + 1
```

**핵심 design 결정**:
- paper Eq 1-6 verbatim 유지 (paper exact 정합)
- Step 4 sample 추출 방식만 stratified reservoir 로 대체 (현 1001 file 의 Eq 1 대체와 동일)
- Step 11 n_inc 분배만 group-aware augment (옵션 B Agent C/D 의 영역)

#### 1.2.4 Component D — Distribution-Aware Stratification (분포 인지 axis)

**stratification mode**:

| Mode | allocation rule | 정보 수준 | 본 연구 측정 영역 |
|---|---|---|---|
| **Equal** | n_j = N/K | L2 (cluster boundary only) | RQ2 measured ✓ |
| **Proportional** | n_j ∝ N_j | L3 (+ N_j) | RQ2/RQ3 measured ✓ (★ 본 연구 main) |
| **Neyman** | n_j ∝ N_j · σ_j | L4 (+ σ_j) | RQ2 measured ✓ (paradox sel=0.01) |
| **Anti-Neyman** | n_j ∝ N_j / σ_j | L4 (negative control) | RQ2 measured ✓ |

★ **본 Form 1 의 streaming compatibility**:
- Equal/Proportional: streaming 환경에서 online 계산 가능 (n_j 만 알면 됨 = BIRCH CF-tree 의 N_j)
- Neyman: σ_j 도 online 계산 가능 (BIRCH CF-tree 의 SS_j 로부터)
- **본 Form 1 권장 = Proportional** (RQ2 의 Neyman paradox 결과 의 자연 결론, sel=0.01 한정 Neyman ≈ Prop)

### 1.3 paper §V-B Eq 1-6 와 통합 방식 (★★★ critical)

#### 1.3.1 통합 axis 표

| paper Eq | paper 영역 | 본 Form 1 영역 | 통합 방식 |
|---|---|---|---|
| **Eq 1** N=385 | sample budget | **대체 (Bernoulli → SRS Equal/Prop/Neyman)** | 본 Form 1 Component A 대체 |
| **Eq 2** Q-error | accuracy metric | 본 Form 1 동일 사용 | paper exact 유지 |
| **Eq 3** δ adjustment | sampling overhead 의 dynamic tuning | **개선 (group-aware δ_j 가능)** | future work (Form 1 phase 2) |
| **Eq 4** V_t momentum | smoothing | **개선 (group-aware V_{j,t} 가능)** | future work (Form 1 phase 2) |
| **Eq 5** sampling_size update | n_inc dynamic | **augment (n_inc 의 group-aware 분배)** | 본 Form 1 Component C Step 11 augment |
| **Eq 6** lr decay | convergence | 본 Form 1 동일 사용 | paper exact 유지 |

★ **Form 1 phase 1 (5/27 + 6/11 submit)** = Eq 1 대체 + Eq 5 group-aware augment 만 다룸 (cost 25-50h)
★ **Form 1 phase 2 (paper-grade future)** = Eq 3 + Eq 4 의 group-aware augment 까지 (cost 추가 30-50h)

#### 1.3.2 paper hyperparameter 7 종 유지

paper §VI 도입부 verbatim 7 hyperparameter:
- m = 0.9 (momentum coefficient)
- η₀ = 0.1 (initial learning rate)
- α = 50 (weighting factor)
- β = 1.5 (target Q-error)
- γ = 0.99 (lr decay factor)
- period P = 50 queries (sample size update trigger)
- N = 385 (initial sample budget, Eq 1)

★ **본 Form 1 phase 1 = 위 7 hyperparameter 그대로 유지** + K=20 (cluster count) 추가만 도입. paper exact 정합.

---

## 2. 측정 plan + cost (추가 측정 / 1001 file 활용)

### 2.1 추가 측정 필요 영역 (5 영역)

#### 2.1.1 측정 1 — Streaming workload simulation (★★★ 본 Form 1 핵심)

**objective**: paper §VI-B "shifting workloads" 영역 정량 측정 (paper 미수행).

**setup**:
- dataset: DEEP (96d) + SIFT (128d) + SSN (256d) × sf=10/100
- query: paper TPC-H Q3 vector 영역 + concept drift simulation
- **concept drift scenarios (3 종)**:
  - (a) **Gradual drift**: cluster centroid 가 매 1000 query 마다 ε 거리 만큼 shift (Gaussian random walk)
  - (b) **Sudden drift**: 매 5000 query 마다 distribution swap (cluster 재할당)
  - (c) **No drift (baseline)**: paper §V-B 와 동일 정적 환경

**measurement**:
- 본 Form 1 SRS (Equal/Prop/Neyman) vs paper §V-B Bernoulli vs CaseB ensemble
- metrics: Q-error mean + Q-error std + sample size trajectory + cluster centroid drift Δ%
- trial = 10 per scenario

**file count**: 3 dataset × 2 sf × 3 drift × 4 method × 2 mode × 10 trial = **1440 file** (cost ≈ 8-12h 서버 시간)

#### 2.1.2 측정 2 — Online cluster maintenance cost

**objective**: BIRCH CF-tree maintenance 의 memory / latency / accuracy degradation 정량 측정.

**setup**:
- BIRCH threshold T_b 변화: 0.1, 0.3, 0.5, 1.0
- K target = 10, 20, 50
- update frequency = every 50 query (paper period P) vs every 100 vs every 200

**measurement**:
- memory peak (MB) / latency per insert (μs) / σ_j² estimation error vs offline batch K-means
- Q-error degradation vs offline batch K-means baseline

**file count**: 3 dataset × 4 T_b × 3 K × 3 update freq × 5 trial = **540 file** (cost ≈ 3-5h 서버 시간)

#### 2.1.3 측정 3 — 4-way 비교 (Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1)

**objective**: paper §VI-D Fig.12 영역 확장 (paper 미수행).

**setup**:
- **Bernoulli (paper baseline)**: 본 연구 측정 1001 file 中 B1 9 file 재사용
- **SelNet (paper [74] reference)**: scikit-learn neural network MLPRegressor 또는 reference implementation
- **CE4HD SRCE/MRCE (VLDB 2024)**: GitHub 또는 reproduce (reference object 기반 learned model)
- **Ada-ef (arxiv 2512.06636)**: cosine/IP/L2 distribution 추정 (L2 영역 paper 미해결, 본 연구 fallback Gaussian approximation)
- **본 Form 1 SRS + BIRCH**: Component A + B + C + D 결합

**measurement**:
- Q-error mean / Q-error std / inference latency (ms) / offline training cost (s) / memory (MB)
- DEEP / SIFT / SSN × sf=10/100 × sel=0.01/0.1 × 5 method × 10 trial

**file count**: 3 dataset × 2 sf × 2 sel × 5 method × 10 trial = **600 file** (cost ≈ 5-8h 서버 시간)

★★★ **본 측정의 학술 가치**:
- paper §VI-D 가 SelNet 만 비교 (paper L5 explicit limitation)
- CE4HD VLDB 2024 vs paper Exqutor 직접 비교 안 됨 (CE4HD 의 baseline = SimCard + SelNet, Exqutor 의 baseline = SelNet)
- 본 Form 1 의 4-way 비교 framework = paper-grade contribution 가능

#### 2.1.4 측정 4 — Distribution shift simulation (concept drift)

**objective**: paper §VI-E Limitation 1 ("high-dim sampling overhead" + 본 연구 추가 axis "shifting workloads") 영역 정량 측정.

**setup**:
- baseline: 본 측정 1 (streaming workload simulation) 의 (c) no drift
- variant: 본 측정 1 의 (a) gradual + (b) sudden
- **추가 시나리오 (4 종)**:
  - (d) **Embedding model upgrade**: Ada-002 → Cohere → BGE → etc. (각 dataset 의 동일 raw data 의 embedding 모델 변경)
  - (e) **Time-based drift**: timestamp 기반 cluster shift (예: news article 의 topic drift)
  - (f) **Mixed workload**: 50% DEEP + 50% SIFT (cross-dataset drift)
  - (g) **Workload skew change**: zipf parameter 변화 (skew 강도 변화)

**measurement**: 본 측정 1 과 동일 metric.

**file count**: 3 dataset × 4 추가 scenario × 4 method (Bernoulli + SRS + BIRCH + 본 Form 1) × 2 mode × 5 trial = **480 file** (cost ≈ 3-5h 서버 시간)

#### 2.1.5 측정 5 — Form 1 phase 2 group-aware Eq 3-6 augment (option, paper-grade)

**objective**: paper Eq 3-6 의 group-aware augment (옵션 B Agent C/D 영역, Form 1 phase 2).

**setup**:
- group-aware V_{j,t}: m_j = m (paper 0.9) 동일 유지, V_{j,t} = m · V_{j,t-1} + η_t · δ_j
- group-aware δ_j: paper δ formula 의 cluster-specific Q-error_j
- group-aware n_inc 분배: 본 Form 1 Component C Step 11 augment 와 동일

**measurement**:
- paper Eq 3-6 그대로 vs group-aware augment Δ%
- 3 dataset × 2 sf × 2 mode × 10 trial = 120 file (cost ≈ 1-2h 서버 시간)

**total cost (측정 1-5)**: 1440 + 540 + 600 + 480 + 120 = **3180 file** ≈ **20-30h 서버 시간** (자원 Max + 가속화)

### 2.2 작업 cost 산정 (시간 / 자원 / 코드 / 데이터)

| 영역 | cost (h) |
|---|---:|
| 알고리즘 구현 (Component A + B + C + D) | 30-40 |
| streaming simulation framework | 15-20 |
| BIRCH CF-tree 통합 (scikit-learn `Birch` API 활용) | 5-10 |
| concept drift scenario 구현 | 10-15 |
| 4-way baseline 구현 (SelNet + CE4HD + Ada-ef) | 20-30 |
| 측정 실행 (자원 Max + 가속화) | 20-30 |
| 분석 + paired Δ% + paradigm rollup | 15-20 |
| 5/27 deck + 6/11 보고서 + 부록 | 20-30 |
| **총 cost** | **135-195h** |

★ **자원 max 활용 시 가속**: 서버 (capstone2026) + 병렬 처리 + 자동화 script → 실 cost 100-150h 가능.

★ **5/27 timeline 가능 영역 (cost 50-80h)**:
- phase 1 한정: Component A + B + 측정 1 (streaming) + 측정 3 (4-way) partial (Bernoulli + 본 Form 1 only)
- 측정 2/4/5 + Component C (Eq 5 augment) + 측정 3 full 4-way = 6/11 보고서 영역으로 분담

### 2.3 우리 1001 file 활용 영역 (유지 vs 폐기 vs 재해석)

| 1001 file 카테고리 | 영역 | 본 Form 1 활용 |
|---|---|---|
| **B1 9 file** (paper Bernoulli) | RQ1 + 4-way 비교 baseline | ★ 유지 (재사용) |
| **CaseA 495 file** (단독 대체) | RQ3 단독 대체 결과 | △ 유지 (Form 1 와 boundary 영역 측정 으로 재해석: batch 환경 baseline 비교) |
| **CaseB 496 file** (결합) | RQ3 결합 결과 | △ 유지 (Form 1 ensemble axis 의 baseline 비교) |
| **A2-Fig8/9 multi-table** | 옵션 E 영역 | △ 유지 (future work 영역 명시) |
| **RQ2 5-way** | Neyman paradox | ★ 유지 (Form 1 의 Proportional 권장 결론의 정량 base) |
| **Pareto frontier** | 자원 효율 axis | ★ 유지 (Pareto Top 5 + reservoir 영역 별도 표시) |
| **40 폐기 method** | 자원 7 + audit 23 + 정합성 10 | △ 유지 (Form 1 의 정직 disclosure 영역) |

★★★ **재해석 axis**:
- 본 1001 file = **batch 환경 측정** (paper §V-B 동일 axis)
- 본 Form 1 = **streaming 환경 추가 측정** (paper §VI-B 영역 미수행 axis)
- 두 영역의 boundary 비교 = 본 Form 1 의 contribution 영역

### 2.4 데이터셋 준비 cost

| dataset | 현 상태 | streaming axis 추가 cost |
|---|---|---:|
| DEEP 96d | sf=100 ready | concept drift simulation 코드 작성 ~2h |
| SIFT 128d | sf=100 ready | 동일 ~2h |
| SSN 256d | sf=100 ready | 동일 ~2h |
| YFCC 192d | sf=10 (paper §VI-D) | 추가 download + indexing 가능 ~4h |
| WIKI 768d (high-dim) | 미준비 | full setup ~6-8h (★ paper §VI-E Limitation 1 영역) |

★ **추가 dataset 권장**: WIKI 768d (paper §VI-E high-dim 영역 정량 측정) + YFCC 192d (filtered vector search 영역, paper §VI-C Fig.7) — Form 1 의 generalization 영역 강화.

---

## 3. 5/27 발표 storyline (20 slide framework)

### 3.1 slide 구조 (20 slide 기준)

| slide | 영역 | 핵심 message |
|---|---|---|
| 1 | Title + Team + Date | 속도는벡터 / Capstone Final / 2026-05-27 |
| 2 | Problem (VAQ 영역) | VAQ + paper Exqutor §V-B 영역 + 잘못된 카디널리티 → 옵티마이저 plan 한계 |
| 3 | Paper Exqutor 핵심 메커니즘 | ECQO (인덱스 ON) + Adaptive Sampling (인덱스 OFF) + Eq 1-6 14-step framework |
| 4 | 본 연구 contribution scope (Form 1) | Streaming-aware Distribution-Conscious CE for VAQ + 4 측면 (대체+보완+개선+추가검증) + paper Eq 1 대체 vs Eq 2-6 통합/augment |
| 5 | paper §V-B Algorithm 1 14-step + 본 Form 1 통합 axis | 14-step 中 Step 11 augment + 본 Form 1 Component A+B+C+D |
| 6 | 본 Form 1 Component A (Stratified Reservoir Sampling) | algorithm pseudo-code + O(N×d) memory + streaming compatible |
| 7 | 본 Form 1 Component B (Online cluster maintenance, BIRCH) | CF-tree + σ_j² online 추정 + paper period P 50-query trigger 정합 |
| 8 | 본 Form 1 Component C (paper Eq 2-6 통합) | Step 11 group-aware n_inc 분배 + Eq 3-6 paper exact 유지 |
| 9 | 본 Form 1 Component D (Distribution-aware stratification) | Equal/Prop/Neyman/Anti-Neyman + L2-L4 정보 수준 axis |
| 10 | 측정 1: streaming workload simulation | concept drift (gradual / sudden / no) × 3 dataset × 4 method |
| 11 | 측정 1 결과 (paired Δ% vs paper §V-B Bernoulli) | shifting workload 영역 본 Form 1 Δ% 우위 정량 |
| 12 | 측정 3: 4-way 비교 (Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1) | paper §VI-D Fig.12 확장 + CE4HD VLDB 2024 + Ada-ef arxiv 2512.06636 |
| 13 | 측정 3 결과 (mean Q-error + inference latency + offline training cost) | 본 Form 1 = no training cost + Q-error 우위 |
| 14 | paper §VI 한계 보완 (L1 + L5 + L6) | paper L1 (shifting workload trajectory) + L5 (SelNet only) + L6 (sampling overhead 동적 axis) |
| 15 | RQ1/RQ2/RQ3 trilogy 통합 narrative (배치 환경 base + Form 1 streaming 확장) | 1001 file batch 측정 + Form 1 streaming 측정 = comprehensive coverage |
| 16 | Pareto frontier + 자원 효율 axis | Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) + 본 Form 1 = streaming 영역 추가 |
| 17 | 정직 disclosure (40 폐기 + byte-identical + scope limitation) | 자원 7 + audit 23 + 정합성 10 + 6 unique cells × 9 nominal |
| 18 | 본 Form 1 한계 + future work | online cluster accuracy 손실 / framework novelty / 1001 file batch axis / paper-grade future Eq 3-6 group-aware |
| 19 | paper-grade publication path | SIGMOD/VLDB workshop + EDBT short paper (Form 1 phase 1) + main paper (Form 1 phase 2) timeline |
| 20 | Conclusion + Q&A | streaming-aware + 분포 인지 통합 framework + paper §V-B 후속 연구 + 산업 적용 axis |

### 3.2 핵심 message (3-5 line)

**core message 1** (★ critical):
> "Exqutor paper §V-B Adaptive Sampling 의 Eq 1 (Bernoulli sample 추출 방식) 영역을 streaming-aware distribution-conscious 으로 대체하고, paper Eq 2-6 dynamic batch loop 는 paper exact 유지하면서 Step 11 (n_inc 분배) 만 group-aware augment 한다."

**core message 2** (★ critical):
> "본 연구는 paper §VI-B 가 명시한 'shifting workloads' 영역을 정량 측정하여 paper L1 한계를 보완하고, paper §VI-D Fig.12 의 SelNet 한정 비교를 4-way (Bernoulli + SelNet + CE4HD VLDB 2024 + Ada-ef arxiv 2512.06636 + 본 Form 1) framework 으로 확장하여 paper L5 한계를 보완한다."

**core message 3** (★ critical):
> "본 Form 1 의 novelty 는 framework axis (각 method 자체 신규 X) 이나, vector similarity range query + Adaptive Sampling framework + BIRCH CF-tree online cluster maintenance 의 통합 발현은 본 연구가 처음 도입한다. 학술 정직성 axis 명시 보강."

**core message 4** (★ Pareto):
> "본 Form 1 의 산업 contribution = streaming environment + O((N+K)×d) memory + paper §V-B Q-error 정확도 anchor 수준 동시 달성. RAG production / OLTP write-heavy / vector database insert stream 환경 직접 적용 가능."

**core message 5** (★ honest disclosure):
> "한계: 본 Form 1 phase 1 = paper Eq 1 대체 + Eq 5 group-aware augment 만 다룸. Eq 3 + Eq 4 group-aware augment 는 phase 2 (paper-grade future work). online cluster maintenance accuracy 손실 + framework novelty 명시 + 1001 file batch axis 의 streaming 영역 추가 측정 정직 표기."

### 3.3 시각 자료 (5 종 신규)

#### 3.3.1 시각 자료 1 — Streaming axis 시각화

**figure**: paper §VI-B Fig.6 (sample size trajectory) 와 동일 layout 으로 본 Form 1 streaming 환경 측정 결과 추가.
- x-axis: query number (0 ~ 5000)
- y-axis: sample size + Q-error
- lines: (a) paper §V-B Bernoulli batch, (b) 본 Form 1 SRS streaming (no drift), (c) 본 Form 1 SRS streaming (gradual drift), (d) 본 Form 1 SRS streaming (sudden drift)

#### 3.3.2 시각 자료 2 — 4-way 비교 결과

**figure**: paper §VI-D Fig.12 (Exqutor vs SelNet speedup) layout 확장.
- x-axis: dataset (DEEP / SIFT / SSN)
- y-axis: speedup over baseline (log scale)
- bars: Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1 SRS

#### 3.3.3 시각 자료 3 — Distribution shift simulation

**figure**: concept drift scenario 4 종 (gradual / sudden / embedding upgrade / time-based) 별 Q-error trajectory 비교.

#### 3.3.4 시각 자료 4 — Online cluster maintenance cost trade-off

**figure**: BIRCH threshold T_b × K_target grid heatmap (memory / latency / Q-error degradation).

#### 3.3.5 시각 자료 5 — RQ1/RQ2/RQ3 + Form 1 통합 trilogy

**figure**: 4-quadrant layout.
- (a) RQ1 batch baseline (1001 file)
- (b) RQ2 5-way allocation (Neyman paradox sel-dependency)
- (c) RQ3 단독/결합 (CaseA/CaseB)
- (d) Form 1 streaming-aware (본 Agent E 신규 측정)

---

## 4. 6/11 보고서 outline (학부 capstone + paper-grade 접근)

### 4.1 챕터 구조

```
§1 서론 (Introduction)
  1.1 동기 — VAQ + Adaptive Sampling + paper §V-B 영역
  1.2 문제 정의 — paper §V-B Bernoulli sample 추출 의 한계
       (high-dim overhead + shifting workload + dataset-dependent trajectory)
  1.3 본 연구 contribution scope (Form 1 4 측면)
       대체 + 보완 + 개선 + 추가검증
  1.4 보고서 구성

§2 배경 (Background)
  2.1 Vector-augmented Analytical Queries (VAQ) 영역
  2.2 paper Exqutor §V-A ECQO + §V-B Adaptive Sampling Eq 1-6 14-step
  2.3 Classical sampling theory (Cochran 1977 §4.5 + §5.5)
  2.4 Streaming algorithms (Vitter 1985 reservoir + Chao 1982 weighted reservoir)
  2.5 Online cluster maintenance (BIRCH 1996 + CluStream 2003 + mini-batch K-means)

§3 관련 연구 (Related Work)
  3.1 paper Exqutor 본 연구 영역
  3.2 SelNet (paper [74] reference)
  3.3 CE4HD SRCE/MRCE (VLDB 2024, Lan-Bao)
  3.4 Adaptive Bucket Probing (arxiv 2604.04603, HKUST 2025)
  3.5 Ada-ef Distribution-Aware HNSW (arxiv 2512.06636, Waterloo 2025)
  3.6 Stratified Reservoir Sampling (Al-Kateb-Lee-Wang SSDBM 2010 + ISJ 2014)
  3.7 본 연구 positioning + differentiation

§4 본 연구 방법론 (Streaming-aware Distribution-Conscious CE for VAQ)
  4.1 Form 1 main theme + 4 측면 design
  4.2 Component A — Stratified Reservoir Sampling (paper Eq 1 대체)
  4.3 Component B — Online cluster maintenance (BIRCH CF-tree)
  4.4 Component C — paper Eq 2-6 통합 (Step 11 group-aware augment)
  4.5 Component D — Distribution-aware stratification (Equal/Prop/Neyman)
  4.6 paper Eq 1-6 + 본 Form 1 통합 표 + Algorithm pseudo-code

§5 실험 환경
  5.1 시스템 (capstone2026 server)
  5.2 dataset (DEEP/SIFT/SSN/YFCC/WIKI)
  5.3 benchmark (TPC-H Q3 + concept drift simulation)
  5.4 baseline (paper §V-B Bernoulli + SelNet + CE4HD + Ada-ef)
  5.5 metrics (Q-error mean/std + latency + memory + offline training cost)

§6 측정 결과
  6.1 RQ1 paper baseline 재현 (1001 file batch 영역)
  6.2 RQ2 5-way 표본 할당 + Neyman paradox sel-dependency (★ sel=0.01 한정)
  6.3 RQ3 단독/결합 + 8 paradigm × 56 method
  6.4 Form 1 측정 1 — streaming workload simulation
  6.5 Form 1 측정 2 — online cluster maintenance cost
  6.6 Form 1 측정 3 — 4-way 비교 (paper §VI-D Fig.12 확장)
  6.7 Form 1 측정 4 — distribution shift simulation (4 종 시나리오)
  6.8 (option) Form 1 측정 5 — phase 2 group-aware Eq 3-6 augment

§7 자원 효율 Pareto frontier
  7.1 Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert)
  7.2 reservoir + Form 1 streaming 영역 별도 표시
  7.3 산업 적용 추천 (RAG / OLTP / vector database insert stream)

§8 paper 한계 보완 (L1 + L5 + L6)
  8.1 L1 (§VI-B "sample size trajectory varies depending on dataset") — Form 1 측정 1 정량 결과
  8.2 L5 (§VI-D SelNet 만 비교) — Form 1 측정 3 4-way 결과
  8.3 L6 (§VII Sampling 영역 dynamic optimization) — Form 1 Component C Step 11 group-aware

§9 본 Form 1 한계 + 정직 disclosure
  9.1 online cluster maintenance accuracy 손실
  9.2 framework axis novelty (각 method 자체 신규 X)
  9.3 1001 file batch axis + streaming axis 영역 boundary
  9.4 byte-identical (6 unique cells × 9 nominal)
  9.5 40 폐기 method 정직 분류 (자원 7 + audit 23 + 정합성 10)

§10 future work
  10.1 Form 1 phase 2 (Eq 3 + Eq 4 group-aware augment)
  10.2 multi-table generalization (옵션 E Centroid tuple K granularity grid)
  10.3 ECQO Q-error gap cell 별 paired (옵션 F)
  10.4 정보 수준 L1 method 개발 (옵션 D)
  10.5 TPC-DS §V-B 측정 (옵션 H)
  10.6 streaming framework 의 RAG production 적용

§11 결론
  11.1 paper §V-B 후속 연구 contribution 정리
  11.2 학부 capstone-grade ★★ 매우 강력
  11.3 paper-grade publication path (Form 1 phase 1 = workshop / short paper)

부록 A — paper §V-B Algorithm 1 14-step 의사코드 (reviewer defense)
부록 B — 본 Form 1 Component A+B+C+D 의사코드
부록 C — paper Eq 1-6 + 본 Form 1 통합 표
부록 D — 40 폐기 method 정직 분류
부록 E — byte-identical caveat (6 unique × 9 nominal)
부록 F — REPORT v11 1362 line raw data
```

### 4.2 paper-grade 접근 영역

**§4 본 연구 방법론** + **§6 측정 결과** + **§8 paper 한계 보완** = paper-grade 접근 영역.

**novelty 명시 (framework axis)**:
- Component A (SRS) = Al-Kateb-Lee-Wang ISJ 2014 base + vector similarity range query domain 의 정량 발현
- Component B (BIRCH online) = Zhang-Ramakrishnan-Livny 1996 SIGMOD base + paper §V-B Adaptive Sampling framework 통합
- Component C (paper Eq 2-6 통합) = paper Algorithm 1 14-step 의 Step 11 group-aware augment
- Component D (distribution-aware stratification) = Cochran 1977 + RQ2 Neyman paradox 의 자연 결론 (Proportional 권장)

★ **본 Form 1 의 framework axis novelty**: 위 4 component 의 통합 + paper §V-B framework + 4-way 비교 framework + paper L1+L5+L6 보완. **각 component 자체 novelty 약함, framework axis 가 본 연구 main**.

### 4.3 paper-grade publication 가능 venue + timeline

| venue | acceptance rate | submission deadline | 본 Form 1 적합성 |
|---|---:|---|---|
| **SIGMOD short paper** | ~20% | 11월 (next year) | ★ 가능 (Form 1 phase 1 만으로 fit, framework axis novelty + 4-way 비교) |
| **VLDB short paper / industry track** | ~25% | 4-6월 또는 11월 | ★★ 강력 (paper §V-B 후속 연구 + 산업 적용 axis) |
| **ICDE position paper / short paper** | ~25% | 10월 | ★ 가능 (framework axis 영역) |
| **CIKM short paper** | ~30% | 5-6월 | ★ 가능 (cardinality estimation + IR 영역) |
| **SoCC (Symposium on Cloud Computing)** | ~25% | 6월 | △ moderate (cloud + vector database 영역) |
| **DASFAA short paper** | ~35% | 9-10월 | ★ 가능 (full paper 어렵, short paper 가능) |
| **EDBT short paper** | ~30% | 10월 | ★ 가능 (database + sampling 영역) |
| **VLDB demo track** | ~50% | 4-6월 | △ moderate (demo 환경 추가 필요) |

★ **본 Agent E 권장**: **EDBT short paper (10월 deadline) + VLDB short paper / industry track (4월 또는 11월)**. EDBT short paper 가 acceptance rate 높고 database + sampling 영역 fit. VLDB short paper 가 가장 강력 venue but acceptance rate 25%.

**timeline 산정 (paper-grade future)**:
- **5/27 capstone 발표 → 6/11 보고서**: Form 1 phase 1 완료 (학부 capstone-grade)
- **6-7월**: 측정 보강 (5 측정 full + generalization measurement + cosine/Manhattan 확장)
- **8월**: paper draft 작성 (Form 1 phase 1 + phase 2 partial)
- **9-10월**: EDBT short paper / DASFAA short paper submission
- **11월**: VLDB short paper / SIGMOD short paper submission
- **2027 1-2월**: rebuttal + camera-ready
- **2027 3-6월**: paper presentation (학부생 + 박광현 + 임채림 co-author)

---

## 5. 5/15 박광현 review form (자료 + review 요청 항목 + 자세)

### 5.1 자료 구성 (1-2 page, 박광현 review 요청 form)

#### 5.1.1 자료 구성 표

| 영역 | 분량 | 내용 |
|---|---:|---|
| **§0 우리 결정 form** | 1/2 page | Form 1 main theme + 4 측면 (대체+보완+개선+추가검증) + 우리 narrative 합의 결과 |
| **§1 보완 paper 한계 L1+L5+L6** | 1/2 page | paper §VI-B + §VI-D + §VII verbatim 인용 + 본 Form 1 영역 align |
| **§2 측정 plan + cost** | 1/2 page | 5 측정 영역 + cost 산정 + 1001 file 활용 영역 |
| **§3 5/27 storyline** | 1/4 page | 20 slide 핵심 axis 요약 |
| **§4 6/11 outline** | 1/4 page | 11 §  + 6 부록 핵심 영역 요약 |
| **§5 review 요청 항목 6** | 1/2 page | Form 1 fit 만 선택, 박광현 자문 질문 6 영역 |
| **부록 A — Algorithm pseudo-code** | 1/2 page | Component A+B+C+D 의 pseudo-code (reviewer defense) |

#### 5.1.2 자료 content 구체

**§0 우리 결정 form (verbatim)**:
> "본 연구 main theme: **Streaming-aware Distribution-Conscious Cardinality Estimation for Vector-augmented Analytical Queries: Extending Exqutor's §V-B Framework**.
>
> 4 측면 (사용자 명시 + 14:00 디스코드 회의 합의):
> - **대체**: Bernoulli random → distribution-aware reservoir + online cluster (paper Eq 1 영역)
> - **보완**: paper §VI-D limitation framework (SelNet 만 비교 → 4-way: Bernoulli + SelNet + CE4HD + Ada-ef + 본)
> - **개선**: paper §V-B Eq 2-6 distribution shift augment (paper Step 11 augment)
> - **추가검증**: paper §VI-B 'shifting workloads' 정량 측정 (paper 미수행 영역)"

**§1 보완 paper 한계 L1+L5+L6 verbatim 인용**:
> "**L1 (paper §VI-B 우단, page 8 우측 verbatim)**:
> > 'The sample size trajectory varies depending on the dataset: for DEEP and SimSearchNet++, the sample size decreases over time as Q-error stabilizes... In contrast, for SIFT, the sample size increases to satisfy higher estimation demands due to its more complex distribution.'
> >
> > '... shifting workloads ...' (paper §VI-B 끝 단락)
>
> → 본 Form 1 영역: streaming workload simulation 정량 측정 + dataset-dependent trajectory mechanism 분석.
>
> **L5 (paper §VI-D 우단, page 11 우측 verbatim)**:
> > 'Comparison with learned cardinality estimator. Figure 12 compares Exqutor with SelNet [74], a learned estimator. Exqutor achieves speedups up to 16.1× speedup over SelNet.'
>
> → 본 Form 1 영역: 4-way 비교 framework (Bernoulli + SelNet + CE4HD + Ada-ef + 본).
>
> **L6 (paper §VII Related Work Sampling 영역 verbatim)**:
> > 'The method in [81] adjusts the sample size dynamically until a desired confidence level is reached, but does not consider sampling overhead or optimize it dynamically based on query characteristics.'
>
> → 본 Form 1 영역: streaming-aware 자체 + sampling overhead 동적 axis (paper Lipton-Naughton 1990 [81] differentiation 영역 보강)."

#### 5.1.3 자료 형식

★ **자료 형식 권장**:
- **단 1 PDF file** (1-2 page, 박광현 시간 절약)
- Chrome CDP PDF (md2pdf.py 사용) + Apple SD Gothic Neo
- callout box (success / warning / info) 활용
- table + verbatim quote 적극 사용

★ **자료 명**: `속도는벡터_박광현_5월15일_미팅_Form1_review_form.pdf`

### 5.2 review 요청 항목 (Agent C 6 + Agent D 7 = 13 항목 中 Form 1 fit 만 선택)

#### 5.2.1 자문 1 — Form 1 학술 정당성 (paper §V-B 후속 연구 form 적절성) (★★★ critical)

**질문 (verbatim 권장)**:
> "본 Form 1 의 contribution scope = paper §V-B Eq 1 대체 (Bernoulli → SRS + BIRCH online cluster) + Eq 5 group-aware augment + paper §VI-B/§VI-D/§VII 한계 L1+L5+L6 보완. paper §V-B 후속 연구 form 으로 적절한가?
>
> 학부 capstone-grade vs review-grade 측면 평가 부탁드립니다.
>
> 본 연구의 정직 disclosure: framework axis novelty (각 component 자체 신규 X), online cluster maintenance accuracy 손실 가능, 1001 file batch axis + streaming axis 영역 boundary."

**예상 답변**:
- 학부 capstone-grade: ★★ 매우 강력 (paper §V-B framework + 1001 file + 4-way framework + 한계 보완)
- review-grade: ★ paper §V-B 후속 연구 form 적절, 단 generalization 측정 보강 필요 (cosine / Manhattan / WIKI 768d / TPC-DS)

#### 5.2.2 자문 2 — streaming-aware + 분포 인지 통합 framework novelty (★★★ critical)

**질문**:
> "본 Form 1 의 novelty = framework axis (각 component 자체 신규 X). 구체적:
> - SRS = Al-Kateb-Lee-Wang ISJ 2014 base + vector similarity domain 의 정량 발현 (novel)
> - BIRCH online = Zhang-Ramakrishnan-Livny 1996 SIGMOD base + paper §V-B framework 통합 (novel)
> - 4-way 비교 = paper §VI-D Fig.12 영역 확장 (novel)
>
> 학술 paper-grade publication 측면 framework axis novelty 충분한가? challenge 가능 영역?"

**예상 답변**:
- framework axis novelty = paper-grade 가능 (단 generalization 측정 보강 필요)
- challenge 가능: "framework 자체로 novelty?" reviewer 의문 가능 → 답변 = paper §V-B framework 의 streaming axis 추가 + 4-way 비교 framework 자체가 paper §VI-D 확장 + vector similarity range query domain 의 정량 발현

#### 5.2.3 자문 3 — 측정 plan 적절성 (★★ major)

**질문**:
> "측정 plan: 5 영역 (streaming simulation + online cluster cost + 4-way 비교 + distribution shift + phase 2 group-aware) × 3 dataset × 2 sel × 다양한 시나리오 ≈ 3180 file. cost 100-150h (자원 Max + 가속화).
>
> 5/27 timeline (D-13) 까지 phase 1 (cost 50-80h) 완료 가능. 6/11 보고서 (D-29) 까지 phase 2 + generalization 측정 완료 가능. 적절한 plan 인가? 우선순위 추천?"

**예상 답변**:
- 측정 plan 적절 (paper-grade 접근)
- 우선순위: 측정 1 (streaming) > 측정 3 (4-way) > 측정 4 (distribution shift) > 측정 2 (online cluster cost) > 측정 5 (phase 2)
- 단 timeline 압박 → 측정 1 + 측정 3 partial (Bernoulli + 본 Form 1 only) 5/27 까지 + 측정 3 full + 측정 4 6/11 까지 + 측정 2 + 측정 5 future work

#### 5.2.4 자문 4 — 5/27 timeline 가능성 (★★ major)

**질문**:
> "5/27 발표 (D-13) 까지 Form 1 phase 1 (Component A + B + 측정 1 + 측정 3 partial) cost 50-80h. 자원 Max + 가속화 시 가능. 박광현 교수 추천 + BDAI 연구실 base 측면 추천?"

**예상 답변**:
- 자원 Max + 가속화 + paper exact 코드 재사용 + scikit-learn `Birch` API 활용 → 5/27 까지 phase 1 가능
- 단 risk = timeline 압박 + 4-way baseline 구현 (SelNet + CE4HD + Ada-ef) cost 20-30h 의 timeline 압박
- 박광현 추천: 4-way baseline 中 SelNet 만 5/27 까지 (paper 직접 비교), CE4HD + Ada-ef 6/11 까지

#### 5.2.5 자문 5 — paper-grade publication 가능성 (★ minor)

**질문**:
> "본 Form 1 phase 1 의 paper-grade publication 가능 venue: EDBT short paper / VLDB short paper / SIGMOD short paper / DASFAA short paper.
>
> 박광현 교수 + 임채림 + 박세은 + 강재현 + 조현빈 + 이동욱 co-author 가능. timeline 6-7월 측정 보강 + 8월 draft + 9-10월 submission. 박광현 교수 추천 venue 선호도 + co-author 의향?"

**예상 답변**:
- EDBT short paper (10월 deadline, acceptance rate ~30%) 가 가장 fit
- VLDB short paper / industry track (4월 또는 11월) 가 가장 강력 venue (acceptance rate ~25%)
- 박광현 교수 co-author 의향 + 임채림 corresponding author 의향 확인 권장
- 학부생 (조현빈 + 박세은 + 강재현 + 이동욱) co-author 참여 가능

#### 5.2.6 자문 6 — 박광현 본업 align 가능성 (★ minor)

**질문**:
> "박광현 BDAI 연구실 본업 paper list (BDAI conferences.html 2024-2026):
> - **Exqutor** (본 연구 base)
> - **RELOAD** (learned QO + ML/DB integration)
> - **DFLOP** (Differentiable Floating-Point Optimization)
> - **CANNON** (near-memory ANN)
> - **FaScalSQL** + **SPID-Join** (멀티모달 LLM pipeline)
>
> 본 Form 1 의 paper §V-B 후속 연구 + cardinality estimation module 영역과 박광현 본업 (특히 RELOAD learned QO) 의 align 가능성 + 결합 framework 추천?"

**예상 답변**:
- RELOAD learned QO + 본 Form 1 cardinality module = future paper 영역 (옵션 P Agent D)
- CANNON near-memory ANN + 본 Form 1 streaming reservoir = align 가능 영역
- 박광현 교수 + 임채림 + 본 학부생 collaboration 영역 확장 가능

### 5.3 자세 (사용자 = "공유 안 완성까지 fix")

**우리 결정 form 확정**:
- ★ **fix 모드** (사용자 명시): 공유 완성까지 변경 X
- 박광현 review = **확정 form 의 검증 + 추가 추천** form (변경 가능성 명시)
- ★ **박광현 추천 변경 가능 영역**:
  - 측정 plan 우선순위 (자문 3)
  - 5/27 timeline phase 1 영역 분담 (자문 4)
  - paper-grade publication venue (자문 5)
  - 박광현 본업 align 영역 (자문 6)
- ★ **박광현 추천 변경 불가 영역**:
  - main theme (Form 1, fix)
  - 4 측면 design (대체+보완+개선+추가검증, fix)
  - paper §V-B Eq 1 대체 + Eq 5 group-aware augment scope (fix)

★ **자료 마무리 문구 (verbatim 권장)**:
> "박광현 교수님, 본 Form 1 main theme + 4 측면 design + 보완 paper 한계 L1+L5+L6 영역은 5/14 18:00 ~ 19:00 디스코드 회의로 4 팀원 합의 + fix 결정 완료입니다. 본 review form 은 학술 정당성 + 측정 plan + 5/27 timeline + paper-grade publication 가능성 + 박광현 교수 본업 align 영역의 자문 부탁드립니다. 우선순위 + 변경 추천 영역은 박광현 교수님 자문 결과 반영 권장합니다. 5/15 14:00 ~ 15:00 미팅 시 자문 부탁드립니다."

---

## 6. paper-grade publication path (venue + timeline + co-author)

### 6.1 target venue list 비교

| venue | acceptance rate | deadline | review timeline | acceptance impact factor | 본 Form 1 fit |
|---|---:|---|---|---|---|
| **EDBT short paper** | ~30% | 10월 | 11-12월 | DB venue, well-respected | ★ 강력 fit (database + sampling) |
| **VLDB short paper** | ~25% | 4월 또는 11월 | 6-8월 또는 1-3월 | top DB venue | ★★ 강력 (paper §V-B 후속 연구) |
| **VLDB industry track** | ~30% | 4월 | 6-8월 | top DB venue, 산업 axis | ★★ 강력 (산업 적용 + RAG 영역) |
| **SIGMOD short paper** | ~20% | 11월 | 1-3월 | top DB venue | ★ moderate (acceptance rate 어려움) |
| **ICDE position paper / short** | ~25% | 10월 | 12-2월 | top DB venue | △ moderate (position paper 어려움) |
| **CIKM short paper** | ~30% | 5-6월 | 7-9월 | IR + DB | ★ moderate (cardinality estimation + IR 영역) |
| **DASFAA short paper** | ~35% | 9-10월 | 11-12월 | regional DB venue | ★ moderate (acceptance rate 높음) |
| **SoCC short paper** | ~25% | 6월 | 8-10월 | cloud computing | △ moderate (vector database + cloud) |
| **VLDB demo track** | ~50% | 4-6월 | 6-8월 | top DB venue demo | △ moderate (demo 환경 추가 필요) |

★★★ **Agent E 권장 venue path**:
1. **1st priority**: **EDBT short paper (10월 deadline)** — acceptance rate 30% + database + sampling 영역 fit + paper-grade publication 가능
2. **2nd priority**: **VLDB short paper / industry track (4월 또는 11월 deadline)** — top DB venue + 산업 axis + 학술 영역 매우 강력
3. **3rd priority**: **DASFAA short paper (9-10월 deadline)** — acceptance rate 35% + regional venue

### 6.2 timeline 산정 (학부 capstone 후 future paper 영역)

```
2026-05-27 (D-13)     : capstone 발표 (Form 1 phase 1 완료)
2026-06-11 (D-29)     : 최종 보고서 (Form 1 phase 1 + partial phase 2)
2026-06-12 ~ 2026-07-31 : 측정 보강 (full 5 measurement + generalization)
2026-08-01 ~ 2026-09-30 : paper draft 작성 (Form 1 phase 1 + phase 2 partial)
2026-10-15 (deadline) : EDBT short paper submission
2026-10-30 (deadline) : ICDE short paper submission
2026-11-15 (deadline) : VLDB short paper submission
2026-11-30 ~ 2027-02 : rebuttal + camera-ready
2027-03 ~ 2027-06    : paper presentation
```

★ **timeline risk**:
- 6-7월 측정 보강 = 학부생 4명 + 박광현 + 임채림 collaboration 필요 (학기 종료 후 여름 방학)
- 8-9월 draft 작성 = 박광현 교수 corresponding author + 임채림 first author 또는 co-first author 가능
- 10-11월 submission = EDBT + VLDB 동시 submission 가능 (다른 venue)

### 6.3 co-author 가능 영역

| author | role | contribution 영역 |
|---|---|---|
| **임채림 석사** | first author / co-first | paper §V-B 영역 main + framework design + 측정 + 분석 + draft 작성 |
| **박광현 교수** | corresponding author | paper §V-B framework 자문 + paper-grade venue 추천 + review + camera-ready |
| **조현빈** | co-author | RQ1/RQ2/RQ3 trilogy + 1001 file + Form 1 phase 1 측정 + 분석 + 보고서 작성 |
| **박세은 (팀장)** | co-author | Form 1 phase 1 측정 + Pareto frontier + 산업 적용 axis |
| **강재현** | co-author | Form 1 phase 1 BIRCH 구현 + 측정 + 분석 |
| **이동욱** | co-author | Form 1 phase 1 SelNet/CE4HD/Ada-ef baseline 구현 + 측정 |

★ **collaboration framework**:
- 학부생 4 명 + 박광현 교수 + 임채림 석사 = 6 co-author
- 박광현 corresponding + 임채림 first author 가 paper-grade convention 권장
- 학부생 4 명 = co-author (학부 capstone 결과 + Form 1 phase 1 측정)

---

## 7. 본 Form 1 의 한계 + future work 정직 disclosure

### 7.1 본 연구 한계 (★★★ critical disclosure)

#### 7.1.1 한계 1 — 우리 KM20 = batch / streaming 부합 X (전제)

**verbatim 명시**:
> "본 Form 1 의 design 은 paper §V-B Eq 1 대체 (Bernoulli → SRS + BIRCH online cluster) 와 paper Eq 5 Step 11 group-aware augment 한정. 본 연구의 RQ1/RQ2/RQ3 측정 portfolio 1001 file 은 **batch 환경 측정** (offline K-means K=20 + Bernoulli base + stratified sampling) 이며, Form 1 의 streaming 환경 측정 (BIRCH online cluster + reservoir) 은 본 연구가 추가 측정해야 할 영역."

**영역 align**:
- 1001 file = batch axis baseline (RQ1/RQ2/RQ3)
- Form 1 streaming axis = 추가 측정 영역 (측정 1-5)
- 두 영역의 boundary 비교 = 본 Form 1 의 contribution

#### 7.1.2 한계 2 — online cluster maintenance accuracy 손실 가능

**verbatim 명시**:
> "본 Form 1 Component B (BIRCH CF-tree online cluster maintenance) 는 단일 pass streaming 환경에서 cluster centroid + σ_j² 를 incremental 추정하므로, offline batch K-means K=20 와 비교 시 accuracy 손실 가능. 측정 2 (online cluster maintenance cost) 의 σ_j² estimation error 측정 결과 정직 보고 권장."

**대응**:
- 측정 2 의 BIRCH threshold T_b × K_target grid heatmap (memory / latency / Q-error degradation) 정량 결과 명시
- BIRCH 의 periodic K-means refinement (paper period P 50-query trigger 활용) 의 accuracy 회복 axis 명시

#### 7.1.3 한계 3 — 우리 측정 1001 file 中 streaming axis 측정 X (추가 측정 필요)

**verbatim 명시**:
> "본 1001 file 측정 portfolio 는 batch 환경 (offline K-means + paper §V-B Eq 1 대체 + Eq 2-6 paper exact 유지) 한정. streaming axis 측정 (Form 1 측정 1-5) 은 본 연구가 추가 측정해야 할 영역. 본 Form 1 phase 1 (5/27 + 6/11) 완료 시 추가 측정 file 약 3180 개 = 1001 file 의 3.18 배 portfolio 확장."

**대응**:
- 측정 1-5 의 cost 100-150h + 자원 Max + 가속화 + paper exact 코드 재사용
- 5/27 phase 1 = 측정 1 + 측정 3 partial 만 (cost 50-80h, 1500 file)
- 6/11 phase 2 = 측정 3 full + 측정 4 + 측정 2 (cost 추가 30-50h, 1500 file)
- 측정 5 (phase 2 group-aware Eq 3-6 augment) = future paper 영역

#### 7.1.4 한계 4 — 4-way 비교 framework axis novelty (각 method 자체 신규 X)

**verbatim 명시**:
> "본 Form 1 의 novelty 영역 = framework axis (각 component 자체 신규 X). 구체적:
> - **Component A (SRS)** = Al-Kateb-Lee-Wang ISJ 2014 base + vector similarity range query domain 의 정량 발현 (novel)
> - **Component B (BIRCH online)** = Zhang-Ramakrishnan-Livny 1996 SIGMOD base + paper §V-B framework 통합 (novel)
> - **Component C (paper Eq 2-6 통합)** = paper Algorithm 1 14-step Step 11 group-aware augment (paper main contribution 영역 augment)
> - **Component D (distribution-aware stratification)** = Cochran 1977 + RQ2 Neyman paradox 의 자연 결론 (Proportional 권장)
>
> 본 Form 1 의 framework axis novelty 명시 보강 + paper-grade publication 시 reviewer 의 framework novelty 의문 대비 권장."

**대응**:
- 박광현 자문 2 (streaming-aware + 분포 인지 통합 framework novelty) 의 답변 정리
- paper §VII Related Work + Cochran 1977 + Al-Kateb-Lee-Wang ISJ 2014 + BIRCH 1996 + CE4HD VLDB 2024 + Ada-ef arxiv 2512.06636 의 positioning + differentiation 명시

#### 7.1.5 한계 5 — byte-identical (6 unique cells × 9 nominal)

**verbatim 명시**:
> "본 연구 측정 cell 9 nominal 中 6 unique cells (byte-identical 3 쌍 = DEEP/SIFT sf=10 + DEEP sf=100/sel=0.1 + WIKI 768d sf=10). 본 Form 1 측정 의 cell coverage = 6 unique cells 의 streaming axis 확장. 정직 표기."

#### 7.1.6 한계 6 — 정합성 위반 10 method (paper N=385 budget 위반) + audit 23 + 자원 7 = 40 폐기 method

**verbatim 명시**:
> "본 1001 file 측정 portfolio = 17 method (paradigm anchor) + paper baseline B1. 폐기 method 40 (자원 7 + audit 23 + 정합성 10) 정직 분류. 본 Form 1 측정의 method coverage = 17 anchor + 폐기 method 의 정직 boundary 명시."

### 7.2 future work (5/27 + 6/11 미해결 영역)

| future work 영역 | 본 Form 1 의 phase | cost | 학술 가치 |
|---|---|---:|---|
| **Form 1 phase 2 — Eq 3 + Eq 4 group-aware augment** | phase 2 | 30-50h | ★★ paper main 영역 augment |
| **Multi-table generalization (옵션 E)** | future | 20-30h | ★★ paper §VI-C 영역 확장 |
| **ECQO Q-error gap cell 별 paired (옵션 F)** | future | 20-30h | ★ paper §V-A + §V-B boundary |
| **정보 수준 L1 method 개발 (옵션 D)** | future | 25-35h | ★ framework contribution |
| **TPC-DS §V-B 측정 (옵션 H)** | future | 50-70h | ★ benchmark coverage |
| **WIKI 768d high-dim 영역 (paper §VI-E L1)** | future | 15-25h | ★ paper future work explicit 영역 |
| **streaming framework 의 RAG production 적용 (옵션 G2)** | future | 30-50h | ★ 산업 적용 axis |
| **learned QO 통합 (RELOAD align, 옵션 P)** | long-term | 80-120h | ★★ 박광현 본업 align |

★ **본 Agent E 권장 future work 우선순위**:
1. **6/11 보고서 후 6-7월**: Form 1 phase 2 + 측정 4 full + WIKI 768d 측정 (paper-grade publication 준비)
2. **8-9월**: paper draft 작성 + multi-table generalization (옵션 E) + cosine/Manhattan 확장
3. **10-11월**: EDBT/VLDB short paper submission
4. **2027 long-term**: learned QO 통합 (RELOAD align, 박광현 본업 collaboration)

### 7.3 streaming-aware 고차원 영역 (paper §VI-E L1 직접 영역)

**verbatim 명시**:
> "paper §VI-E Limitation 1 (page 12 우단): 'In high-dimensional spaces, the overhead of sampling increases because of the higher cost of distance computations, which may reduce the efficiency of our adaptive sampling strategy.'
>
> 본 Form 1 phase 1 측정 = DEEP 96d + SIFT 128d + SSN 256d (low/medium-dim). 본 Form 1 phase 2 = WIKI 768d (paper §VI-E L1 explicit 영역) 측정 + Form 1 의 streaming-aware 영역의 high-dim 효율 axis 정량 검증."

### 7.4 multi-table 확장 (옵션 E 영역)

**verbatim 명시**:
> "본 Form 1 phase 1 = single-table KNN (paper §V-B 'specifically for KNN queries' 한정) 영역. multi-table joint distribution (paper §V-B 'single-table KNN only' 제약) 확장 = Form 1 phase 2 future work. 본 연구 A2-Fig9 Centroid tuple cheap 근사 (-7.37% Δ%) 의 streaming axis 확장 가능 영역."

### 7.5 learned query optimizer 통합 (RELOAD align, 옵션 P Agent D 영역)

**verbatim 명시**:
> "박광현 BDAI 연구실 본업 RELOAD (learned QO + ML/DB integration) 와 본 Form 1 cardinality estimation module 의 결합 framework = long-term future work. paper-grade publication 영역 가능 (SIGMOD/VLDB main paper). 박광현 corresponding author + 임채림 first author + 학부생 4 명 co-author collaboration."

---

## 8. main thread 종합 권장 사항

### 8.1 박광현 5/15 미팅 자료 핵심 항목 (★★★ critical)

1. **자료 형식**: 단 1 PDF file (1-2 page) + Apple SD Gothic Neo + callout box + verbatim quote
2. **자료 명**: `속도는벡터_박광현_5월15일_미팅_Form1_review_form.pdf`
3. **자료 위치**: `submission/_drafts/박광현_5월15일_미팅/속도는벡터_박광현_5월15일_미팅_Form1_review_form.pdf`
4. **자료 content**: §0 우리 결정 form (fix) + §1 paper 한계 L1+L5+L6 verbatim + §2 측정 plan + §3 5/27 storyline + §4 6/11 outline + §5 review 요청 6 항목 + 부록 A pseudo-code
5. **wording 정정 룰 ★ 필수 사용**: "5 단계 中 1 단계" → "Eq 1 대체 vs Eq 2-6 통합/augment" + Neyman paradox sel=0.01 한정 + σ_j range oracle interpretation + Pareto Top 5 + byte-identical 6 unique cells

### 8.2 5/27 발표 deck v7 핵심 update 항목 (현 v6 base + Form 1 axis 통합)

1. **slide 4 (본 연구 contribution scope)**: Form 1 main theme + 4 측면 (대체+보완+개선+추가검증) 명시
2. **slide 5-9 (Form 1 Component A+B+C+D)**: 4 component pseudo-code + 통합 axis 표
3. **slide 10-13 (Form 1 측정 1-5 결과)**: streaming simulation + 4-way 비교 + distribution shift + online cluster cost (phase 1 한정)
4. **slide 14 (paper §VI 한계 보완 L1+L5+L6)**: verbatim quote + Form 1 영역 align
5. **slide 15 (RQ1/RQ2/RQ3 + Form 1 통합 trilogy)**: 4-quadrant layout 시각 자료
6. **slide 16 (Pareto frontier + Form 1 streaming 영역 별도 표시)**: Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) + reservoir 영역 = 본 Form 1 main
7. **slide 17 (정직 disclosure)**: 40 폐기 method + byte-identical caveat + scope limitation
8. **slide 18 (본 Form 1 한계 + future work)**: online cluster accuracy 손실 + framework novelty + phase 2 영역
9. **slide 19 (paper-grade publication path)**: EDBT/VLDB short paper + timeline + co-author
10. **slide 20 (Conclusion + Q&A)**: streaming-aware + 분포 인지 통합 + paper L1+L5+L6 보완 + 산업 적용

### 8.3 6/11 보고서 outline 핵심 update 항목 (현 v2 base + Form 1 axis 통합)

1. **§1 서론 contribution scope 정정**: Form 1 main theme + 4 측면 + 보완 paper 한계 L1+L5+L6
2. **§2 배경 추가**: Streaming algorithms (Vitter 1985 + Chao 1982) + Online cluster maintenance (BIRCH 1996 + CluStream 2003)
3. **§3 관련 연구 추가**: SRS (Al-Kateb-Lee-Wang ISJ 2014) + CE4HD (Lan-Bao VLDB 2024) + Adaptive Bucket Probing (HKUST 2025) + Ada-ef (Waterloo 2025)
4. **§4 본 연구 방법론 신규**: Form 1 Component A+B+C+D + paper Eq 1-6 통합 표 + Algorithm pseudo-code
5. **§5 실험 환경 정정**: dataset + benchmark (TPC-H Q3 + concept drift) + baseline (Bernoulli + SelNet + CE4HD + Ada-ef) + metrics
6. **§6 측정 결과 신규 (6.4-6.8)**: Form 1 측정 1-5 결과
7. **§8 paper 한계 보완 신규**: L1 + L5 + L6 영역
8. **§9 본 Form 1 한계 + 정직 disclosure 신규**: 한계 5-6 영역
9. **§10 future work 정정**: Form 1 phase 2 + multi-table + ECQO gap + L1 method + TPC-DS + RELOAD align
10. **§11 결론 정정**: paper §V-B 후속 연구 + 학부 capstone-grade + paper-grade publication path

### 8.4 본 Agent E 의 종합 권장 path 1줄 요약 (★★★ critical)

★★★ **사용자 fix 결정 = Form 1 main theme (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ: Extending Exqutor's §V-B Framework) + 4 측면 (대체+보완+개선+추가검증) + paper 한계 L1+L5+L6 보완. 5/15 박광현 미팅 review form = 1-2 page 단 1 PDF + 6 review 요청 항목 + 부록 A pseudo-code. 5/27 발표 = phase 1 (Component A + B + 측정 1 + 측정 3 partial, cost 50-80h). 6/11 보고서 = phase 1 + phase 2 partial + 부록 6 종. paper-grade publication = EDBT short paper (10월 deadline) + VLDB short paper (4월 또는 11월) target, 박광현 corresponding + 임채림 first + 학부생 4 명 co-author.**

### 8.5 본 Agent E 의 정직 disclosure 종합

1. **streaming-aware stratified reservoir sampling** = Al-Kateb-Lee-Wang ISJ 2014 + SSDBM 2010 base 존재. vector similarity range query + cardinality estimation domain 의 정량 발현이 novel.
2. **online cluster maintenance** = BIRCH 1996 + CluStream 2003 + mini-batch K-means base 존재. 본 연구 contribution = paper §V-B Adaptive Sampling framework 통합 axis.
3. **4-way 비교 framework** (Bernoulli + SelNet + CE4HD + Ada-ef + 본) = paper §VI-D Fig.12 영역 확장. framework axis 자체가 novel.
4. **본 Form 1 phase 1** = 학부 capstone-grade ★★ 매우 강력. paper-grade ★ moderate (generalization 측정 보강 필요).
5. **paper-grade publication** = 6/11 보고서 후 6-9월 측정 보강 + draft 작성 + 10-11월 EDBT/VLDB short paper submission.

---

## 9. 부록 A — Component A+B+C+D pseudo-code (reviewer defense)

### A.1 Component A — Stratified Reservoir Sampling (paper Eq 1 대체)

```
Algorithm: Stratified Reservoir Sampling (SRS)
Input:  data stream D, query Q, sample budget N=385, cluster count K=20
Output: stratified sample R = ⋃_j R_j

1. Initialize:
   R_j ← [] for j = 1, ..., K
   C_j ← initial centroids (from first 5K samples)
   n_j ← N / K  # default Equal allocation, K=20 → n_j ≈ 20

2. For each x_t ∈ D:
   j* ← argmin_j ||x_t - C_j||₂  # closest cluster (L2 distance)

   if |R_{j*}| < n_{j*}:
     R_{j*}.append(x_t)
   else:
     r ← random_int(0, t-1)
     if r < n_{j*}:
       R_{j*}[r] ← x_t  # Vitter 1985 reservoir rule

   # Update CF-tree CF_{j*} (Component B)
   CF_{j*} ← (N_{j*} + 1, LS_{j*} + x_t, SS_{j*} + x_t ⊙ x_t)
   C_{j*} ← LS_{j*} / N_{j*}

3. Return: R = ⋃_j R_j
```

### A.2 Component B — BIRCH CF-tree Online Cluster Maintenance

```
Algorithm: BIRCH Online Cluster Maintenance
Input:  data stream D, BIRCH threshold T_b, target K=20
Output: cluster centroids C_j and variance σ_j²_j for j = 1, ..., K

1. Initialize:
   CF-tree T ← empty
   T_b ← 0.5 × min_distance_between_initial_centroids

2. For each x_t ∈ D:
   Find closest leaf CF_j = (N_j, LS_j, SS_j) in T
   if dist(x_t, C_j) ≤ T_b:
     CF_j ← (N_j + 1, LS_j + x_t, SS_j + x_t ⊙ x_t)  # absorb
   else:
     create new CF leaf for x_t

   if size(T) > M_target:
     Rebuild T with larger T_b  # standard BIRCH procedure

3. Periodically (every 50 queries, paper period P):
   K-means on leaf CFs → K=20 final clusters
   For j = 1, ..., K:
     C_j ← LS_j / N_j
     σ_j² ← SS_j / N_j − (LS_j / N_j)²

4. Return: {(C_j, σ_j²_j, N_j) for j = 1, ..., K}
```

### A.3 Component C — paper Algorithm 1 14-step (Step 11 augment)

```
Algorithm: paper §V-B Adaptive Sampling (14-step) + Form 1 Component C augment
Input:  workload W, paper hyperparameters (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, P=50)
Output: cardinality estimates Card_esti(q) for each q ∈ W

Step 1:  N ← ⌈z² · P̂ · (1 - P̂) / e²⌉ = 385  # paper Eq 1 유지
Step 2:  V_0 ← 0, η_0 ← 0.1, t ← 0
Step 3:  For each query q ∈ W:
Step 4:    S ← StratifiedReservoirSample(D, n_j, C_j, σ_j²_j)
                  # ★ 본 Form 1 Component A 대체 (paper Bernoulli random → SRS)
Step 5:    evaluate similarity over S → Card_esti(q)
Step 6:    observe Card_true(q)  # from query execution
Step 7:    Q-error_t ← max(Card_esti/Card_true, Card_true/Card_esti)  # paper Eq 2
Step 8:    if (t mod P) == 0:  # paper period P = 50 queries
Step 9:      δ_t ← α · (Q-error_t − β) − (100 − α) · sampling_ratio  # paper Eq 3
Step 10:     V_t ← m · V_{t-1} + η_t · δ_t  # paper Eq 4
Step 11:     n_inc ← N₀ · max(1, β · σ̂²_t / α)  # paper sampling_size update

             ★ 본 Form 1 augment (Step 11 augment):
             # Option 1: Proportional (★ 본 Form 1 권장)
             n_inc_j ← n_inc · N_j / Σ_k N_k

             # Option 2: Neyman (paper 미사용, RQ2 paradox)
             # n_inc_j ← n_inc · N_j · σ_j / Σ_k (N_k · σ_k)

             # 각 cluster j 별 reservoir n_inc_j tuple 추가
             For j = 1, ..., K:
               n_j ← n_j + n_inc_j

Step 12:     sampling_size_{t+1} ← sampling_size_t + V_t  # paper Eq 5
Step 13:     η_{t+1} ← γ · η_t  # paper Eq 6 (lr decay)
Step 14:   t ← t + 1
```

### A.4 Component D — Distribution-Aware Stratification (allocation rule)

```
Algorithm: Distribution-Aware Stratification
Input:  cluster {(C_j, σ_j²_j, N_j) for j = 1, ..., K}, total budget N=385
Output: cluster-specific budget n_j

# Equal allocation (L2 정보 수준, cluster boundary only)
n_j ← N / K

# Proportional allocation (L3 정보 수준, + N_j) ★ 본 Form 1 권장
n_j ← N · N_j / Σ_k N_k

# Neyman allocation (L4 정보 수준, + N_j + σ_j)
n_j ← N · (N_j · σ_j) / Σ_k (N_k · σ_k)

# Anti-Neyman allocation (L4 정보 수준, negative control)
n_j ← N · (N_j / σ_j) / Σ_k (N_k / σ_k)
```

---

## END

본 산출 file: `_internal/handoff/active/agent_E_Form_1_구체화_streaming_aware_20260515_0000.md`

main thread 가 본 Agent E 결과 + Agent A (78%) + Agent B (정정 7) + Agent C (8 옵션 + 추가 3) + Agent D (paper §VI/§VII 5 영역 + 경쟁 paper 5 + BDAI 6) 의 종합으로:
- 박광현 5/15 미팅 review form 단 1 PDF (1-2 page) 작성
- 5/27 발표 deck v7 update (10 영역)
- 6/11 보고서 outline update (10 영역)

수행 권장. **사용자 fix 결정 = Form 1 main theme + 4 측면 + paper 한계 L1+L5+L6**. 박광현 review = 변경 가능 영역 한정 (측정 plan 우선순위 + 5/27 phase 1 영역 분담 + paper-grade publication venue + 박광현 본업 align).

작성: 2026-05-15 00:00 KST · Agent E · paper PDF + Agent A/B/C/D 4 호출 종합 + WebSearch 4 건 (SRS Al-Kateb-Lee-Wang ISJ 2014 + SSDBM 2010 + CE4HD VLDB 2024 + Ada-ef arxiv 2512.06636) + 1001 file 재해석 + Form 1 phase 1 + phase 2 design 완료
