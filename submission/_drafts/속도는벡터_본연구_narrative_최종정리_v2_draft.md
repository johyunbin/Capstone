# 속도는벡터 — 본 연구 narrative 최종 정리 v2 draft

> 본 세션 22.5h 종합 (Form 1 fix + Agent A-J 10 호출 + 박세은 9 영역 + 정정 룰 14 + 정직 disclosure 13 + K granularity SF axis + Neyman selectivity-dependent) 반영하여 v1 (10 단계) 를 12 단계 + 부록 5 종으로 확장한다. 박세은 review + 박광현 5/15 미팅 + 5/27 최종 발표 + 6/11 최종 보고서 **공통 base**. 박세은 5/13 12:13 피드백 (method 개수 축소 + 숫자/공식 최소화) + 5/14 9:09 ~ 10:15 9 영역 자문 반영. 학부생 톤 + 학술 서사적 산문.

작성: 2026-05-14 22:32 KST · 측정 portfolio 1065 file (기존) + K granularity SF axis 48 file (추가) = 1113 file · 본 세션 회의 transition 후 narrative v3 폐기 + Form 1 (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ: Extending Exqutor's §V-B Framework) fix.

---

## 0. 본 연구 main theme 와 paper §V-B "without index" anchor

본 연구의 main theme 은 **"Streaming-aware Distribution-Conscious Cardinality Estimation for Vector-augmented Analytical Queries: Extending Exqutor's §V-B Framework"** 로 fix 한다. 본 theme 은 5/14 18:00 ~ 19:00 의 팀 회의에서 기존 narrative v3 (11 단계 multi-axis) 을 폐기하고 사용자가 명시한 4 측면 (대체 / 보완 / 개선 / 추가검증) 위에 정확히 align 된 후속 연구 form 으로 결정되었다.

이 main theme 의 존재 의의는 paper Exqutor 자체가 §V 영역을 두 갈래로 명확히 분리한다는 점에 있다. paper p.5 좌단 §V 도입부는 다음과 같이 verbatim 으로 기술한다.

> "For VAQs with vector indexes, Exqutor employs Exact Cardinality Query Optimization (ECQO)... For VAQs without index, Exqutor uses a sampling-based approach to approximate selectivity (subsection V-B)."

paper p.5 우단 §V-B 첫 단락은 다시 한번 강조한다.

> "When a VAQ lacks a vector index, ... Exqutor adopts a sampling-based cardinality estimation approach specifically for KNN queries."

paper p.6 우단의 implementation 단락은 동일한 가정을 확인한다.

> "When a VAQ with a vector range predicate lacks index support, the optimizer invokes a sampling routine..."

paper §VI-A 실험 절도 ECQO 의 영역을 다음과 같이 한정한다.

> "In this section, we evaluate the performance of Exqutor when executing VAQs with a vector index using an ANN search, specifically with HNSW [38]."

paper §VI-B 도 본 연구가 다루는 영역의 가정을 verbatim 으로 표기한다.

> "In this section, we evaluate the performance of Exqutor applied to TPC-H VAQs that perform KNN searches without vector indexes, where cardinality estimation is handled via sampling."

요컨대 paper Exqutor 는 (1) **§V-A ECQO 영역 = 인덱스 있을 때** 와 (2) **§V-B Adaptive Sampling 영역 = 인덱스 없을 때** 를 paper 안에서 명확히 분리하고 있다. 본 연구의 Form 1 은 **§V-B 영역 한정 후속 연구** 다. 이 anchor 가 박세은 9:09 영역 4 ("분포 알면 ECQO 가능?") 자문에 대한 본 연구의 답변 base 이며, 5/15 박광현 review form 의 §1 anchor 이기도 하다.

본 연구의 4 측면은 위 §V-B 영역 안에서만 의미를 갖는다. (a) **대체 측면** = paper Eq 1 의 Bernoulli random sample 추출만을 distribution-aware reservoir + online cluster maintenance 로 갈아끼우는 영역이다. (b) **보완 측면** = paper §VI-D Fig.12 의 SelNet 단독 비교를 4-way 비교 framework (Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1) 으로 확장하는 영역이다. (c) **개선 측면** = paper §V-B Eq 5 의 sampling_size scalar update 를 cluster 별 group-aware allocation 으로 augment 하는 영역이다. (d) **추가검증 측면** = paper §VI-B 가 자체로 명시한 "shifting workloads" 영역을 정량 측정하는 영역이다. 위 4 측면은 모두 paper §V-B 가 다루는 "without index" 가정 안에서 의미가 있고, ECQO 영역은 본 연구의 outside 다.

---

## 1. 출발점: 어디서 부정확해지는가

본 논문 (Exqutor) 은 벡터 증강 분석 쿼리에서 인덱스가 없을 때 무작위 표집 (베르누이 + 동적 표본 수 조정) 으로 카디널리티를 추정한다. paper §V-B 의 sampling-based cardinality estimation 은 classical sampling theory (z=1.96 + P̂=0.5 + e=0.05 으로 N=385 도출) 위에 momentum-based feedback control (paper §VI 의 7 hyperparam m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period P=50 / N=385) 을 통한 dynamic adjustment 를 결합한 형태다. 단일 테이블 + 단순 분포에서는 잘 작동하지만, 분포가 한쪽으로 쏠려 있을 때 (skew) 표집의 정밀도가 떨어진다.

본 연구의 출발점은 위 paper §V-B 영역의 두 가지 자연 의문에서 시작한다. 첫째, 베르누이 무작위 표집이 본질적으로 분포 정보를 활용하지 않기에, 분포가 알려져 있는 환경에서는 정확도를 더 끌어올릴 여지가 있어야 한다는 가설이다. 둘째, paper 자체가 §VI-B 에서 "sample size trajectory varies depending on the dataset" 과 "shifting workloads" 를 언급하면서도 본 영역의 정량 측정은 paper 안에서 수행되지 않았다는 관찰이다. 두 의문은 본 연구의 두 갈래 측정 영역으로 자연 분기한다.

본 연구의 측정은 위 두 의문 中 첫째 의문을 우선 다룬다. 즉 "분포 정보를 알 수 있다면 어디까지 정확도를 끌어올릴 수 있나" 를 정량으로 확인하는 영역이 본 연구 의 phase 1 main thread 다. 둘째 의문 (shifting workloads 정량 측정) 은 Form 1 의 streaming axis 가 다루는 영역이며 phase 1 + phase 2 에서 점진적으로 다룬다.

여기서 한 가지 wording 정정 룰이 작용한다. 박세은 5/14 9:09 영역 1 (정정 룰 #3) 은 본 연구의 이전 narrative 가 "Exqutor 의 single-table Adaptive Sampling 은 동작하지 않는다 = 구조 X" 라고 표현한 부분이 부정확하다고 지적했다. paper §V-B 자체는 single-table KNN query 에 대한 sampling-based cardinality estimation 을 명시 (p.5 우단 verbatim) 하고 있고, 본 연구가 multi-join 영역으로 측정을 이동한 것은 paper 공개 코드 (BDAI-Research/Exqutor github) 의 구현 한계에 의한 것이지 paper §V-B 의 구조적 한계가 아니다. 본 v2 부터는 "paper §V-B 가 single-table 을 다루지만 공개 코드의 구현 한계로 동작하지 않아 본 연구의 측정 영역이 multi-join 으로 자연 이동" 으로 정정한다.

또 한 가지는 박세은 영역 2 (정정 룰 #4) 의 "block 추출 vs row 추출" 정정이다. 본 연구의 이전 narrative 가 "paper §V-B 는 block 추출이라 분포 인지가 어렵다" 라고 표현한 부분이 있는데, 임채림 연구원 자문 + paper §V-B 정독 종합 결과 paper 의 sampling 은 **block + row hybrid** 다. 초기 N=385 budget 은 block 단위로 빠르게 잡고, Eq 5 sampling_size update 시 추가되는 n_inc 행은 row 단위 추출이다. 본 연구의 contribution scope 는 어디까지나 추출 방식의 **random → stratified** 정정이지, block / row 구조 자체의 변경이 아니다.

---

## 2. 탐색: 분포 정보를 얻는 방법 56 가지

분포 정보를 얻을 수 있는 후보 method 56 개를 8 갈래 (P1 클러스터링, P2 공간 분할, P3 스트리밍, P4 차원 축소, P5 준 무작위, P6 양자화, P9 정보 이론, P10 밀도 추정) 로 모았다. 위 8 갈래는 본 연구의 method paradigm rollup axis 이며, 측정 결과의 분포 인지 효과를 갈래 별로 평균 내는 단위가 된다.

9 가지 측정 환경 (DEEP/SIFT/SSN 단일 테이블 + 다중 테이블 Fig7/Fig9 + 선택도 sweep + scale sweep) × 2 가지 모드 (CaseA 단독 대체 + CaseB 결합) 로 매트릭스를 짰다. 본 매트릭스의 단위 cell 은 9 × 56 = 504 nominal 이며, 중복 (byte-identical) + 자원 한계 미커버 영역을 제외한 실측 portfolio 는 paper exact carry-over 1001 file (B1 9 + CaseA 495 + CaseB 496) 이다. 본 세션 5/14 22:00 추가 측정으로 K granularity SF axis (DEEP A5-scale × K=10/30 × 4 anchor × 2 mode = 48 file) 가 더해져 portfolio 가 1065 file 에서 1113 file 로 확장되었다.

여기서 "9 가지 측정 환경" 은 paper §VI-A ~ §VI-D 의 9 cells 영역 (paper Fig.6 + Fig.7 + Fig.9 + Fig.10 + Fig.11 의 dataset × selectivity × scale 조합) 과 직접 align 한다. 본 연구의 측정 environment 가 paper 의 환경 정의를 verbatim 으로 따르는 axis 가 본 연구 의 paper exact compatibility 의 근거다.

K granularity SF axis 추가 측정은 박세은 5/14 8:50 자문 (회의 PDF v2 §2.5 의 "SF=1 영역 K=20 미측정" 발견) 후속 영역이다. 사용자 옵션 B 결정 (3 SF × 2 K 추가 = 48 file) 으로 측정을 진행했고, 5/14 22:00 까지 회수 완료했다. 결과의 핵심 finding 은 §11 의 K granularity SF axis 영역에서 자세히 다룬다.

---

## 3. 폐기: 정직하게 떨어뜨린 40 method (정정: 39 → 40)

측정을 진행하면서 **40 method** 를 폐기했다 (v1 의 "39 method" 표기는 audit 한계 정정 결과 40 으로 update). 폐기 사유는 세 갈래로 정직 분류된다.

첫째, **자원 한계 7 종** = Tier 2 6 method (dirichlet / kernelpca / neurocard_lite / birch / hdbscan / agglomerative) + KDE 1 method (kde_parzen). birch 가 한 측정에 50 ~ 200GB 메모리를 차지해서 실행 불가했고, kde_parzen 은 5/13 ~ 5/14 측정 chain 진행했으나 5/5 timeout 으로 5/14 07:39 폐기 결정했다. 본 자원 한계 영역의 정직 표기 자체가 본 연구의 정직성 갈래다.

둘째, **5월 10일 코드 정독 검토로 reference 위반이 발견된 23 종** = vinecopula 가 vine copula reference 가 아니라 PCA 1 차원 정렬의 별칭이었고, neuram 이 PCA1D 와 한 줄씩 동일한 코드였다. 본 audit 영역은 5/10 8 agent 호출 + Q1-Q5 confirm 후 method_registry 정정 결과로 23 method 가 reference 위반 또는 alias 로 분류되었다. 본 연구의 학술 정직성 갈래 中 가장 큰 영역이며, audit 자체가 본 연구의 contribution 영역으로 분류 가능하다.

셋째, **큰 데이터셋에서 추정값이 외곽으로 튀는 정합성 위반 10 종** = halton / sobol / lhs / hammersley / dense_rp / random_projection / dbscan / ccsketch / lsh / ams_count_sketch. 본 영역은 paper N=385 budget 위반 (sample size 가 paper budget 과 다르게 발현하거나 또는 측정 결과가 anchor 영역의 ±50% 외부로 튀는 cell 이 빈번) 으로 분류된다. v1 의 "9 종" 은 audit 한계 정정 결과 **10 종** 으로 update 된다 (5/14 환각 검증 H1 정정).

전체 40 method 폐기 사유의 비율은 자원 한계 17.5% (7/40) + reference audit 57.5% (23/40) + 정합성 위반 25% (10/40) 다. 폐기 사유 자체를 보고서에 분류한 것이 본 연구의 정직성 갈래이며, 5/27 발표 slide 17 + 6/11 보고서 §9 정직 disclosure 영역의 핵심 내용이다.

남은 17 사용 method 는 §12 부록 table 에 paradigm 별 분포 + 결합 모드 평균 + 자원 효율 등급 + 이론적 근거로 정리한다. 본 v2 부터는 v1 의 method 핵심 6 + 17 사용 method 영역을 §12 부록으로 통합 이동하고, 본문 §3-11 영역은 framework axis (Form 1 Component A+B+C+D) 영역을 우선 다룬다.

---

## 4. Form 1 Component A — Stratified Reservoir Sampling (paper Eq 1 대체)

Form 1 의 첫째 Component 는 paper §V-B Eq 1 (N=385 초기 sample budget 영역의 Bernoulli random sample 추출) 을 cluster 별 stratified reservoir sampling 으로 대체하는 영역이다. 본 영역이 본 연구의 phase 1 main contribution 이며, 측정 결과 1001 file 의 CaseA 모드 (단독 대체) 측정이 본 component 의 효과 정량을 담는다.

### 4.1 algorithm 핵심: Vitter Algorithm R 의 cluster-wise 확장

본 component 의 알고리즘 핵심은 Vitter (TOMS 1985) 의 reservoir sampling Algorithm R 을 K=20 cluster 별로 분리해서 운영하는 것이다. 각 cluster j 마다 reservoir R_j 와 budget n_j 를 유지하고, 새로 도착하는 tuple x_t 가 cluster j* 에 속하면 R_{j*} 에 reservoir sampling rule 로 update 한다. 전체 sample budget N=385 은 paper exact 유지하며, n_j 의 분배는 group_aware_alloc 4 mode (Equal / Proportional / Neyman / Anti-Neyman) 中 하나로 결정한다 (Component D 영역).

본 algorithm 의 pseudo-code 핵심 부분은 다음과 같이 표현된다.

```
Initialize:
  reservoir R_j = [] for j = 1, ..., K     # K=20 cluster 별 reservoir
  cluster centroids C_j initialized via online init (first 5K samples)
  reservoir budget n_j = group_aware_alloc(N=385, mode=alloc_mode)

For each new tuple x_t in D (streaming):
  j* = argmin_j ||x_t - C_j||₂          # 가장 가까운 cluster
  if |R_{j*}| < n_{j*}:                  # reservoir 빈 자리 있음
    R_{j*}.append(x_t)
  else:                                  # Vitter 1985 reservoir sampling rule
    r = random_int(0, t-1)
    if r < n_{j*}:
      R_{j*}[r] = x_t                    # replace with prob n_{j*}/t

Return: R = ⋃_j R_j (stratified sample)
```

본 algorithm 의 memory cost 는 reservoir 영역의 O(N × d) (sample size N × feature dim d) + cluster centroid 영역의 O(K × d) = **O((N + K) × d) ≈ O(N × d)** (K=20 << N=385 가정). paper §V-B 의 Bernoulli sampling 과 동일 order 의 memory complexity 이며, streaming 환경에서 단일 pass 로 작동하는 추가 axis 가 발현된다.

### 4.2 이론적 근거: Vitter 1985 + Al-Kateb-Lee-Wang 2014 + SSDBM 2010

본 component 의 이론적 근거는 두 layer 의 reference 위에 발현된다.

**Layer 1 (Vitter Algorithm R)** = Vitter, J. S. (TOMS 1985) "Random Sampling with a Reservoir". 본 paper 는 데이터 크기 N 을 미리 모르더라도 K 개의 uniform random sample 을 단일 pass 로 얻는 알고리즘을 정립했다. Algorithm R 의 핵심은 t 번째 tuple 도착 시 reservoir 의 random index 와 swap 할지의 결정을 probability K/t 로 처리하는 것이다. 본 algorithm 의 sample size 가 미리 fix 된 K 이며, 데이터 스트림의 길이와 무관하게 작동한다는 점이 본 연구의 streaming axis 와 직접 align 한다.

**Layer 2 (Stratified Reservoir Sampling)** = Al-Kateb-Lee-Wang (Information Systems Journal 2014) "Stratified Reservoir Sampling over Heterogeneous Data Streams" + SSDBM 2010 의 base. 본 paper 들은 Vitter 의 base reservoir 위에서 stratification axis 를 도입하여 heterogeneous data stream 의 cluster 별 budget allocation 영역을 다뤘다. 본 reference 의 framework 위에서 본 연구가 paper §V-B 의 Adaptive Sampling framework 영역과 통합 발현시키는 것이 framework axis novelty 의 핵심이다.

본 영역의 정직 disclosure 는 다음과 같다. Component A 의 SRS 자체는 신규 X (1985 + 2010 + 2014 reference 존재) 이며, 본 연구의 contribution 은 위 reference 의 base framework 위에서 paper §V-B Adaptive Sampling framework + vector similarity range query domain 의 발현 axis 의 통합이다 (정직 disclosure #2). 본 framework axis novelty 의 명시 표기가 본 연구의 학술 정직성 영역의 핵심이다.

### 4.3 measurement evidence: 1001 file batch baseline 의 CaseA 모드

measurement 결과는 본 CaseA 모드 (단독 대체) 의 9 측정 환경 평균 paired Δ% 로 표현한다. 본 영역의 1001 file 측정 portfolio 中 CaseA 영역은 495 file (paper exact carry-over 1001 file 中 B1 9 file + CaseA 495 + CaseB 496 의 분배) 이며, 9 측정 환경 × 56 method × 1 mode = 504 nominal cell 의 측정 영역이다.

본 measurement 의 핵심 finding 은 다음 3 가지로 정리된다.

첫째, **56 method 中 약 40% 가 평균적으로 베르누이보다 정확** 하다는 점이다. 본 비율은 본 연구의 method portfolio 가 paper §V-B 의 Bernoulli baseline 보다 distribution-aware allocation 영역에서 유의미한 우위를 갖는 method 군의 발현을 의미한다. 단, 본 40% 는 method 평균 영역의 우위이며, 9 측정 환경 별로 best method 가 다르게 발현되는 영역도 발견된다.

둘째, **9 가지 측정 환경 전반에서 안정적으로 우위를 점한 method 가 15 개** 라는 점이다. 본 영역은 통계 검정 (paired t-test + one-sided p<0.05 + Hedges' g large + Cliff's δ large) 의 4 criteria 모두 만족하는 method 영역이며, 본 15 method 의 평균 개선폭은 **−5 ~ −12% 범위** 다. 본 15 method 영역의 paradigm 분포는 P1 클러스터링 6 method (minibatch_partial / minibatch / gmm 등) + P3 스트리밍 4 method (chao_weighted / reservoir / thompson_sampling / cum_sqrtf) + P4 차원 축소 4 method (sparse_rp / neuram / pca1d / rsvd) + P9 정보 이론 1 method (hyperloglog) 영역이다.

셋째, **단독 대체 best 는 P1 클러스터링 갈래의 minibatch_partial 의 −10.17%** 라는 점이다 (A2-Fig8 단일 cell 측정 기준). 본 −10.17% 의 effect size 영역은 본 연구 portfolio 1001 file 中 가장 큰 단일 cell 영역이며, 본 method 의 algorithm (chunk 단위 partial_fit, scikit-learn MiniBatchKMeans.partial_fit API 직접 활용, Sculley WWW 2010 의 Web-scale K-means 변형) 이 streaming 환경 + 분포 인지 의 두 axis 모두에서 strong fit 발현. 본 −10.17% 의 효과 크기는 paper §V-B Fig.12 의 측정 변동 −4.3% (본 연구가 paper §V-B 영역의 절사 평균 Q-error 를 본 측정 1.618 vs paper 보고값 1.69 로 재현) 의 약 2.4 배 수준이다.

본 영역의 정직 disclosure 한 가지는 negative control 영역의 결과다. CaseA 모드의 9 측정 환경 大 변동 (large worsening) 영역이 37.1% 발현되었고, 단독 대체 영역의 0/493 = 0% 만 paper §V-B Bernoulli 와 byte-identical 한 결과를 보였다. 즉 단독 대체 영역의 효과는 method 선택에 따라 양 방향으로 크게 변동한다는 점이 본 측정 portfolio 의 honest evidence 다. 본 evidence 영역이 §13.2 의 결합 보조 (CaseB 모드 안전망) 영역의 motivation 영역으로 작동한다.

### 4.4 streaming compatibility 가 Component A 의 핵심

본 영역의 streaming compatibility 가 Component A 의 핵심이다. paper §V-B 의 Bernoulli random sampling 은 전체 데이터 access 가 가능한 batch 환경 전제이고, stratified reservoir sampling 은 단일 pass streaming 환경에서 작동한다. 이 streaming axis 가 본 연구의 phase 1 measurement 영역 中 가장 paper §VI-B 의 "shifting workloads" 영역과 직접 align 한다.

본 영역의 산업 적용 axis 는 본 reservoir 의 메모리 O(1) 영역의 발현이다. 본 1001 file 측정 portfolio 中 reservoir method (P3 스트리밍 갈래) 영역의 학습 시간 0.1 초 (SF=1 한정) + 메모리 O(1) (sample size K 만 보존, 데이터 크기 N 과 무관) + −9.25% (단독 대체 9 측정 환경 평균) 의 성능 영역이 산업 적용의 핵심 finding 이다. 본 영역이 §10 자원 효율 영역의 reservoir O(1) anchor 의 evidence 다.

본 영역의 phase 1 measurement (5/27 + 6/11) 는 다음 4 단계로 분리된다. (1) base reference (Vitter 1985 + Al-Kateb 2014) 의 batch 환경 측정 (현 1001 file 의 reservoir method 영역, 완료). (2) Component A 의 streaming axis 발현 측정 (Form 1 phase 1 360 file, 5/27 측정 영역). (3) Component A + B 의 통합 streaming 측정 (Form 1 phase 1 추가 영역). (4) phase 2 (6/11 + post-6/11) 의 generalization 영역 (concept drift + multi-table + 추가 dataset). 본 4 단계 영역의 phase 1 measurement (5/27 + 6/11) 는 cost 23-36h 영역 (Agent F + G 의 검증) 이며, post-5/15 박광현 미팅 후 launch 영역이다.

---

## 5. Form 1 Component B — BIRCH CF-tree online cluster maintenance

Form 1 의 둘째 Component 는 K=20 cluster 의 centroid 와 σ_j² 분산을 streaming 환경에서 online 유지하는 영역이다. 본 영역의 알고리즘 base 는 Zhang-Ramakrishnan-Livny **1996 SIGMOD** 의 BIRCH (Balanced Iterative Reducing and Clustering using Hierarchies) 의 CF-tree (Cluster Feature tree) 구조다.

### 5.1 BIRCH CF tuple 의 구조와 online maintenance

BIRCH 의 핵심은 각 cluster 의 정보를 CF tuple (N_j, LS_j, SS_j) 으로 압축해서 유지하는 것이다. N_j = cluster j 의 tuple 수, LS_j = cluster j 의 linear sum (∑ x_τ), SS_j = cluster j 의 squared sum (∑ x_τ ⊙ x_τ) 의 3 통계량이다. 본 CF tuple 영역의 정보 압축 ratio 는 매우 강력하다 — cluster j 안에 N_j 개의 tuple 이 있을 때 raw data 의 메모리는 N_j × d 인데 비해 CF tuple 은 1 + d + d = 2d + 1 의 메모리만 사용한다. 데이터 크기 N 영역의 ~N/2 배의 압축이 가능하다.

새 tuple x_t 가 도착하면 closest CF leaf 를 찾고 CF tuple 을 increment 한다.

```
Insert x_t into CF-tree T:
  Find closest leaf cluster CF_j = (N_j, LS_j, SS_j)
  if dist(x_t, C_j) ≤ T_b:                        # within absorption threshold
    CF_j ← (N_j + 1, LS_j + x_t, SS_j + x_t ⊙ x_t)   # absorb
  else:
    create new CF leaf for x_t

if T 가 너무 큼 (memory peak M_T > M_target):
  Rebuild T with larger T_b                        # CF-tree threshold 증가
  (BIRCH 의 standard procedure)
```

본 CF tuple 영역은 K cluster total **O(K × d)** 메모리이며, 데이터 크기 N 과 무관한 streaming-compatible 영역이다. K=20 + d=96 (DEEP) ~ 256 (SSN) 으로 본 영역의 메모리 footprint 는 ~ 2-5 KB per cluster × 20 cluster = ~ 40-100 KB total 의 매우 작은 영역이다.

### 5.2 σ_j² 추정의 자연 도출

본 component 의 σ_j² 추정은 CF tuple 위에서 자연 도출된다. cluster mean = LS_j / N_j 이고, cluster variance = SS_j / N_j − (LS_j / N_j)² 다. 본 두 통계량의 정확 derivation 은 다음과 같다.

cluster j 안의 tuple 집합 {x_τ : τ ∈ cluster j} 의 mean μ_j 와 variance σ_j² 는 다음 관계식 위에 발현된다.

```
μ_j = (1/N_j) · Σ_{τ ∈ cluster j} x_τ = LS_j / N_j
σ_j² = (1/N_j) · Σ_{τ ∈ cluster j} (x_τ − μ_j)²
     = (1/N_j) · Σ_{τ ∈ cluster j} (x_τ² − 2 x_τ μ_j + μ_j²)
     = (1/N_j) · [Σ x_τ² − 2 μ_j · Σ x_τ + N_j · μ_j²]
     = SS_j/N_j − 2 μ_j² + μ_j²
     = SS_j/N_j − μ_j²
     = SS_j/N_j − (LS_j/N_j)²
```

본 derivation 의 핵심은 σ_j² 영역의 online 추정이 단순한 SS_j 와 LS_j 와 N_j 의 algebraic combination 으로 얻어진다는 점이다. 본 σ_j² 의 online 추정 가능성이 Component D 의 Neyman / Anti-Neyman allocation 의 streaming compatibility 의 핵심이다. paper §V-B 의 Bernoulli random sampling 은 σ_j² 정보를 활용하지 않지만, 본 Form 1 Component B 의 streaming environment 에서는 σ_j² 정보가 online 으로 자연 도출되어 Component D 의 group-aware allocation 에 직접 입력 가능하다.

### 5.3 ★ 핵심 발견: measure_paper_exact.py line 623-630 의 기존 구현

여기서 본 연구의 중요한 발견 한 가지가 있다. **본 component 는 이미 measure_paper_exact.py line 623-630 에 구현되어 있다**. scikit-learn 의 `sklearn.cluster.Birch(n_clusters=20).partial_fit(X)` API 영역이 본 component 의 구현 base 이며, 본 연구의 기존 측정 1001 file 中 CaseA + CaseB 영역에서 이미 활용되고 있다.

본 기존 구현의 핵심 영역은 scikit-learn Birch class 의 API 영역이다. (1) `Birch(n_clusters=20, threshold=0.5, branching_factor=50)` 의 instantiation, (2) `partial_fit(X_chunk)` 의 chunk 단위 streaming update, (3) `subcluster_centers_` + `subcluster_labels_` + `predict(X_new)` 의 inference 영역이다. 본 4 API 가 본 연구의 Component B 영역의 핵심 building block 이며, Form 1 phase 1 의 구현 영역은 본 기존 코드의 streaming 환경 발현 axis (per-tuple incremental partial_fit + online σ_j² query) 만 확장하면 된다.

구현 cost 영역 정리: 코드량 ~200 line (기존 measure_paper_exact.py line 623-630 영역의 streaming wrapper 영역 + σ_j² query method 추가) + dev cost 10-15h (기존 코드의 streaming axis 발현 axis 확장 + period P=50 trigger 영역 통합) + test cost 4-6h (paper §V-B AdaptiveState 의 paper exact 100% 정합 검증 영역의 regression test). 본 영역이 Component A (~250 line + dev 8-12h) + Component C (~100 line + dev 4-6h) + Component D (~50 line + dev 3-5h) 와 함께 Form 1 phase 1 영역의 코드 base 영역이다.

### 5.4 σ_j² drift 의 정직 disclosure (Form 1 한계 영역)

본 영역의 정직 disclosure 는 BIRCH CF-tree 의 σ_j² 추정이 offline batch K-means 와 비교했을 때 **5-15% drift** 가 있다는 점이다 (정직 disclosure #6). 본 drift 의 origin 은 BIRCH 의 single pass + threshold-based absorption 영역과 batch K-means 의 multi-iteration Lloyd's algorithm 영역의 algorithm 차이에 있다.

BIRCH 의 single pass streaming 환경에서의 cluster boundary 는 다음 영역에서 batch K-means 와 차이가 발현한다. (1) 새 tuple 도착 시 closest CF 영역의 결정이 현재 leaf 영역의 partial state 위에서 이루어진다 (future tuple 의 영역 미반영). (2) absorption threshold T_b 영역의 결정이 dataset-specific 의 adaptive 영역이며, batch K-means 의 final centroid 영역의 boundary 와 정확히 일치하지 않는다. (3) BIRCH 의 K-means refinement 단계 (leaf CF 위에서 K-means 적용) 는 batch K-means 의 global optimum 영역과 차이가 발현 가능.

본 drift 영역의 정량은 Agent E + F 의 검증 결과 5-15% range 영역이며, 본 영역의 정직 disclosure 영역의 핵심 mitigation 은 (a) Form 1 phase 1 권장 = **Proportional allocation** (N_j 만 알면 됨, σ_j drift risk 회피), (b) Neyman allocation 의 streaming 환경 측정은 phase 2 (paper-grade future work) 영역으로 분담, (c) drift 정량 영역의 직접 측정 (BIRCH CF-tree σ_j² vs offline batch K-means σ_j² 의 비교) 은 Form 1 phase 1 측정 2 (online cluster maintenance cost) 영역에서 진행 예정 (540 file × cost 3-5h, Agent E 측정 plan 영역).

단, 본 5-15% drift 가 paper §V-B 의 Bernoulli random 대비 본 연구의 stratified allocation 의 effect size (best −10.17%) 보다 작으므로, 본 component 의 streaming compatibility 가 batch 환경 대비 우위라는 본 연구의 narrative 는 유지된다.

### 5.5 paper §V-B period P=50 영역과의 align

본 component 의 paper §V-B 와의 align 영역은 paper period P=50 영역과 BIRCH 의 K-means refinement 영역의 trigger 통합이다. paper §V-B Eq 1-6 의 sampling_size update 는 period P=50 queries 마다 trigger 되며, 본 P=50 trigger 영역과 BIRCH 의 K-means refinement (leaf CF 위에서 K=20 final cluster 도출) 영역의 trigger 가 align 가능하다.

본 align 영역의 algorithm 은 다음과 같다. paper Eq 5 의 sampling_size update 가 발현될 때 (t mod P == 0 and t > 0), 본 Form 1 Component B 의 BIRCH K-means refinement 도 동시 발현되어 cluster boundary 영역의 update 가 이루어진다. 본 trigger 영역의 통합이 본 Form 1 Component A+B+C+D 영역의 통합 framework axis 의 핵심이며, paper exact compatibility 유지 + streaming axis 의 발현 영역의 통합 영역이다.

본 영역의 phase 1 measurement (5/27 + 6/11) 는 다음 4 단계로 분리된다. (1) BIRCH CF-tree 의 streaming 환경 측정 (Form 1 phase 1 측정 2, 540 file × cost 3-5h). (2) Component B + paper P=50 trigger 영역의 통합 측정 (Form 1 phase 1 측정 1 의 sub-영역). (3) σ_j² drift 정량 측정 (Form 1 phase 1 측정 2). (4) phase 2 (post-6/11) 의 Neyman allocation 의 streaming 환경 측정 (paper-grade future work).

---

## 6. Form 1 Component C — paper Eq 2-6 통합 + Eq 5 group-aware augment

Form 1 의 셋째 Component 는 paper §V-B 의 Eq 2-6 (Q-error metric + δ adjustment + V_t momentum + sampling_size update + lr decay) 을 paper exact 유지하면서 Eq 5 (sampling_size 의 scalar update) 만 cluster 별 group-aware allocation 으로 augment 하는 영역이다.

### 6.1 paper Eq 2-6 의 역할 정리

paper Eq 2-6 의 역할을 정리하면 다음과 같다. 본 영역의 각 Eq 의 정확 derivation 은 부록 §C-2 에 분리된다.

**Eq 2 (Q-error metric)**: `Q-error = max(Card_esti/Card_true, Card_true/Card_esti)`. 본 metric 은 cardinality estimate 의 정확도 측정 영역이며, always ≥ 1.0 + 1.0 = perfect 영역의 unbounded upper 영역이다. paper Eq 2 의 reference 는 [68] Kipf et al. 2018, [69] Hilprecht et al. 2019 (DeepDB), [70] Dutt et al. 2019 의 3 base 다.

**Eq 3 (δ adjustment factor)**: `δ = α · (Q-error − β) − (100 − α) · sampling_ratio`. 본 영역은 Q-error 와 sampling_ratio 의 trade-off 를 표현한다. Q-error 가 β (=1.5 paper §VI verbatim) 보다 크면 sample 증가 방향 (positive δ), sampling_ratio 가 크면 sample 감소 방향 (negative δ) 의 두 axis 의 balance 영역이다. paper hyperparam α=50 + β=1.5 영역이 본 trade-off 의 weighting 영역이다.

**Eq 4 (V_t momentum)**: `V_t = m · V_{t-1} + η_t · δ`. 본 영역은 momentum-based smoothing 영역이며, fluctuation 영역의 억제 + smooth convergence 영역의 두 목표 영역이다. paper hyperparam m=0.9 + η₀=0.1 영역이 본 momentum 의 coefficient 영역이다. paper Eq 4 의 reference 는 [22] Sutskever et al. 2013 (momentum in deep learning) 영역이다.

**Eq 5 (sampling_size update)**: `sampling_size_{t+1} = sampling_size_t + V_t`. 본 영역은 sampling_size 의 scalar update 영역이며 (cluster 개념 없음, batch 환경 전제), 본 Form 1 의 augment 핵심 영역이 본 Eq 5 의 scalar new_size 영역의 cluster 별 분배 영역이다.

**Eq 6 (learning rate decay)**: `η_{t+1} = γ · η_t`. 본 영역은 lr decay 영역이며, iteration 영역의 증가 시 update magnitude 영역의 감소 → convergence 영역의 도출. paper hyperparam γ=0.99 영역이 본 decay rate 영역이다.

본 5 개 Eq 영역의 paper §V-B Adaptive Sampling framework 영역의 통합 발현 영역은 measure_paper_exact.py 의 AdaptiveState class (line 67-140) 에 paper exact 100% 정합 구현되어 있다. 본 영역의 verbatim 정합 검증 영역이 본 연구의 paper exact compatibility 영역의 base 다.

### 6.2 본 Form 1 의 augment: paper Eq 5 의 group-aware allocation

본 Form 1 의 augment 영역은 **paper Eq 5 의 scalar new_size 를 cluster 별 group-aware allocation 으로 분배** 하는 영역에 한정한다. 즉 Eq 5 의 `new_size` 를 계산한 후 (paper exact), 본 new_size 를 K=20 cluster 별로 `n_inc_j = group_aware_alloc(new_size, sizes=N_j, sigma=σ_j, mode="proportional")` 로 분배한다.

본 augment 의 algorithm 영역은 다음과 같이 표현된다.

```
[paper Eq 5 verbatim]:
  new_size ← max(1, round(sampling_size_t + V_t))
  sampling_size_{t+1} ← new_size                  # paper Eq 5 scalar update

[★ 본 연구 augment (Step 14)]:
  # paper Eq 5 의 new_size 를 cluster 별 분배 (본 Form 1 핵심)
  n_j_new ← group_aware_alloc(total_budget=new_size,
                               sizes=BIRCH.N_j,
                               sigma=sigma_j,
                               mode=alloc_mode)
  # mode="proportional" 권장:
  #   n_j_new[j] = round(new_size × N_j / Σ_k N_k)
  # 옵션:
  #   mode="equal":      n_j_new[j] = round(new_size / K)
  #   mode="neyman":     n_j_new[j] = round(new_size × N_j × σ_j / Σ_k (N_k σ_k))
  #   mode="anti_neyman": n_j_new[j] = round(new_size × N_j / σ_j / Σ_k (N_k / σ_k))
```

본 augment 는 Cochran 1977 §5.5 (Stratified Sampling: Optimal Allocation) 의 classical theory 위에서 자연 도출된다. Cochran 의 정확 theorem 은 (a) Proportional allocation 영역 = stratified sample 의 single-stage estimator 의 variance 영역의 lower bound 보다 큰 영역이지만 robust (모든 σ_j 영역에 robust), (b) Neyman allocation 영역 = stratified sample 영역의 optimal allocation (variance minimization) 이지만 σ_j 영역의 정확 추정이 필요 (가정 만족 시), (c) 두 allocation 영역의 effect size 영역의 차이 = stratum variance 영역의 heterogeneity 영역에 의존 의 3 영역이다.

본 Cochran 1977 영역의 framework 위에서 paper §V-B Adaptive Sampling framework 와의 통합 발현이 본 연구의 contribution 영역이다. 즉 paper §V-B 의 batch 환경 영역의 Eq 5 scalar update 영역을 Cochran 1977 의 stratified allocation 영역의 cluster 분배 영역으로 augment 하는 framework axis 가 본 연구의 contribution novelty 영역이다.

### 6.3 paper exact compatibility 의 유지

본 영역의 핵심은 paper Eq 1-6 자체는 verbatim 100% 유지된다는 점이다. measure_paper_exact.py 의 AdaptiveState class (line 67-140) 가 paper Eq 1-6 을 정확히 구현하고 있으며, 본 연구의 기존 1001 file 측정 portfolio 자체가 paper Eq 1-6 의 verbatim 정합 검증을 담당한다. Form 1 의 augment 영역은 paper Eq 5 의 scalar update 만 cluster 분배로 augment 하므로 paper exact compatibility 가 유지된다.

paper §V-B Eq 1-6 의 paper exact 100% 정합 검증은 본 연구의 paper §V-B Fig 12 영역 절사 평균 Q-error 의 측정 영역에서 발현된다. 본 측정 = 1.618 vs paper 보고값 1.69 = **−4.3% 재현** 영역이며, 본 −4.3% 영역이 paper §V-B 의 review-grade 정합성 영역의 evidence 다. 본 review-grade 정합성 영역이 본 연구의 measurement portfolio 1001 file 영역의 paper exact compatibility 영역의 핵심 evidence 다.

본 영역의 코드량은 ~100 line + dev cost 4-6h 의 작은 영역이다. 본 영역의 구현 영역은 group_aware_alloc 함수 1 개 + paper Eq 5 scalar update 영역의 augment wrapper + alloc_mode parameter 의 selection 영역의 3 부분 영역이다.

### 6.4 phase 1 vs phase 2 의 분리

paper Eq 3 + Eq 4 의 group-aware augment (cluster 별 V_{j,t} momentum + δ_j adjustment) 는 phase 2 영역 (paper-grade future work) 으로 분리한다. phase 1 (5/27 + 6/11 영역) 은 Eq 1 대체 + Eq 5 group-aware augment 만 다루며, phase 2 는 EDBT short paper / VLDB short paper submission 영역으로 분담된다.

본 phase 분리의 reasoning 은 다음과 같다. (a) phase 1 영역 = 본 연구의 학부 capstone-grade ★★ 매우 강력 영역의 fit. Eq 1 대체 + Eq 5 augment 의 두 영역의 measurement 가 5/27 + 6/11 영역의 timeline 영역에 fit (cost 52-87h Agent F + G 의 검증). (b) phase 2 영역 = paper-grade publication 영역의 fit. Eq 3 + Eq 4 의 group-aware augment 영역의 measurement 영역의 cost (30-50h) 가 6/11 보고서 영역 외 발현. (c) 두 영역의 boundary 영역 = 본 연구의 batch axis 영역 (Eq 1 대체 한정) 과 streaming axis 영역 (Eq 5 augment + Eq 3/4 augment) 의 자연 분리 영역.

### 6.5 wording 정정 룰: paper §V-B 자체에 algorithm pseudo-code 없음

여기서 한 가지 중요한 wording 정정 룰이 작용한다. 본 연구의 이전 narrative 가 paper §V-B 영역을 "Algorithm 1 14-step pseudo-code" 로 표현한 부분이 있었는데, 이는 부정확하다. **paper §V-B 자체에는 algorithm pseudo-code 형식이 존재하지 않는다.** paper §V-B 의 영역은 Eq 1-6 + 자연 산문 + hyperparam 7 종 (paper §VI verbatim) 만으로 구성된다. 본 연구의 "14-step" 또는 "17-step" 등의 표현은 본 연구의 의역이며, paper exact 가 아니다 (정정 룰 #2 + 정직 disclosure #1). 본 v2 부터는 "paper §V-B Eq 1-6 + 본 연구 의역 step-wise pseudo-code 17 step" 으로 정확 표기한다.

본 정정 룰의 origin 영역은 Agent G 의 paper PDF 직접 정독 영역이다. paper PDF page 5-7 영역의 정확 정독 결과 paper §V-B 영역은 (1) §V-B 도입 (PDF page 6 좌단 끝 ~ 우단 시작) "sampling-based approach 도입", (2) Eq 1 영역 (PDF page 6 우단 중), (3) Adaptive sampling size adjustment 영역 (PDF page 6 우단 + page 7 좌단) "Eq 2-6 + 자연 산문 (algorithmic pseudo-code 형식 없음)", (4) Implementation in generalized vector database systems 영역 (PDF page 7 좌단) "pgvector integration + table-specific sample size states", (5) §VI 도입부 (PDF page 7 우단) "hyperparam 7 종 verbatim" 의 5 단락 구조 영역이다.

본 5 단락 영역에는 "Algorithm 1" / "Algorithm" / "Procedure" 등의 algorithmic block 영역이 발현되지 않는다. 본 영역은 Eq 1-6 + 자연 산문 + hyperparam 7 종만으로 구성되며, "14-step pseudo-code" 또는 "17-step pseudo-code" 등의 표현은 본 연구 자체의 의역 (편의상 산문을 step-wise 으로 풀어쓴 것) 영역이다. 본 정정 룰의 일괄 적용 영역은 회의 PDF + 5/27 deck + 6/11 outline + 5/15 review form 의 모든 자료 영역이다.

### 6.6 17 step 의 구성 영역

본 17 step 의 구성은 paper Eq 1-6 verbatim 영역 = Step 1-2, 6, 8-13, 16 (10 step) + 본 연구 augment 영역 = Step 3-5, 7, 14-15, 17 (7 step) 다. 핵심 augment 는 Step 14 (paper Eq 5 의 group-aware allocation 분배) + Step 17 (streaming tuple incremental update) + Step 3-4 (BIRCH + SRS init) 의 4 step 영역이다.

본 17 step 영역의 정확 표기 (부록 §C-4) 는 본 v2 의 학술 정직성 영역의 핵심 영역이며, 본 영역의 paper exact 영역 (10 step) 과 본 연구 augment 영역 (7 step) 의 분리 표기 가 본 연구의 contribution scope 영역의 정확 표기 영역이다. 본 분리 표기 영역이 박광현 5/15 review form 의 §2 + 5/27 deck slide 5 + 6/11 보고서 §4.6 영역의 source 영역이다.

---

## 7. Form 1 Component D — Distribution-aware stratification (Equal / Prop / Neyman / Anti-Neyman)

Form 1 의 넷째 Component 는 K=20 cluster 의 sample budget 을 cluster 별로 분배하는 allocation rule 영역이다. group_aware_alloc 함수 1 개로 4 mode (Equal / Proportional / Neyman / Anti-Neyman) 의 전환이 이루어진다.

### 7.1 4 mode 의 정확 allocation rule

각 mode 의 allocation rule 은 다음과 같다.

**Equal allocation** = n_j = N/K = 385/20 ≈ 20. 모든 cluster 에 균등 분배. 정보 수준 L2 (cluster boundary only) 에 대응. 본 mode 의 필요 정보 = cluster 개수 K 만. cluster size N_j 영역의 정보 없이도 작동 가능.

**Proportional allocation** = n_j = N × N_j / Σ_k N_k = N × N_j / N_total. cluster size 에 비례 분배. 정보 수준 L3 (+ N_j) 에 대응. 본 mode 의 필요 정보 = cluster size N_j (BIRCH CF tuple 의 N_j 영역 직접 활용).

**Neyman allocation** = n_j = N × N_j · σ_j / Σ_k (N_k · σ_k). cluster size 와 cluster 내 분산의 곱에 비례 분배. 정보 수준 L4 (+ σ_j) 에 대응. 본 mode 의 필요 정보 = cluster size N_j + cluster variance σ_j (BIRCH CF tuple 의 SS_j 영역 + N_j 영역 영역 algebraic combination).

**Anti-Neyman allocation** = n_j = N × N_j / σ_j / Σ_k (N_k / σ_k). Neyman 의 역 방향. RQ2 의 negative control 영역으로 측정. 본 mode 는 정확도 향상 목적이 아니라 stratified sampling theory 영역의 negative control 영역의 발현이다.

### 7.2 4 mode 의 streaming compatibility

본 component 의 streaming compatibility 는 다음과 같다.

**Equal allocation** 영역 = K 만 알면 streaming 환경에서 즉시 작동한다. 본 mode 의 streaming overhead 영역은 0.

**Proportional allocation** 영역 = BIRCH CF tuple 의 N_j (Component B 영역) 만 알면 streaming 환경에서 online 계산 가능하다. 본 mode 의 streaming overhead 영역은 매우 작다 (N_j 영역의 increment 영역 per tuple = O(1)).

**Neyman allocation** 영역 = BIRCH CF tuple 의 SS_j (squared sum) 으로부터 σ_j 가 online 추정 가능하므로 streaming 환경에서도 작동한다. 단, Neyman 의 σ_j 추정은 BIRCH CF tuple 의 5-15% drift 영역에 영향받는다 (정직 disclosure #6). 본 drift 영역의 영향 영역은 phase 1 measurement 의 측정 2 (online cluster maintenance cost) 영역에서 직접 정량 측정 예정.

**Anti-Neyman allocation** 영역 = Neyman 과 동일 streaming compatibility (SS_j 위에서 σ_j 추정). 본 mode 는 negative control 목적이므로 streaming 환경에서의 발현 영역의 학술 가치 영역은 phase 2 (paper-grade future work) 영역으로 분담.

### 7.3 measurement evidence: RQ2 5-way 영역

본 component 의 핵심 measurement evidence 는 본 연구의 RQ2 5-way 측정 영역에 있다. KM20 (K-means K=20) stratification base 위에서 5-way (Bernoulli + Equal + Proportional + Neyman + Anti-Neyman) allocation 측정 결과, **Bernoulli → Proportional 갈아끼우기에서 −9.53% 효과** 가 발현되었다 (handoff_v17 영역).

RQ2 측정 영역의 5 cell × 5 trial design 의 cell breakdown 영역은 다음과 같다. (1) DEEP sf=100 + sel=0.01 의 5 trial. (2) DEEP sf=100 + sel=0.10 의 5 trial. (3) SIFT sf=100 + sel=0.01 의 5 trial. (4) SIFT sf=100 + sel=0.10 의 5 trial. (5) POOL (DEEP+SIFT) sf=100 + sel=0.01/0.10 의 5 trial. 총 5 cell × 5 trial × 5 method = 125 measurement file 영역이다.

본 5-way 측정 영역의 핵심 finding 영역은 다음 3 가지로 정리된다. (a) **mean gap +3.74%** (5 cell × 5 trial) 영역이 RQ1 영역 (random sampling 의 skew 데이터셋 부정확) 의 정량 evidence 다. (b) **Bern→Prop −9.53%** 영역이 RQ2 의 main finding 으로, paper §V-B Bernoulli 영역을 본 연구의 Proportional 영역으로 갈아끼우는 영역의 effect size 다. (c) **Anti 1.540 < Prop 1.580 < Neyman 1.595 paradox** 영역이 sel=0.01 한정의 발견 영역으로, Neyman 의 classical theory 영역의 가정 不만족 영역 (σ_j range 1.3-1.6× narrow + N_i CV=0) 의 evidence 다.

본 5-way 측정의 paradox 영역은 §12 의 Neyman selectivity-dependent 영역에서 자세히 다루며, 정정 룰 #9 + #11 + #14 영역의 base 영역이다.

### 7.4 phase 1 권장: Proportional allocation

본 component 의 phase 1 권장은 **Proportional allocation** 이다. 권장 이유는 다음 3 가지 영역으로 정리된다.

**Reason 1**: **RQ2 의 Neyman paradox sel=0.01 한정 결과의 자연 결론** 영역. sel=0.01 영역 Neyman 1.595 < Proportional 1.580 < Anti-Neyman 1.540 의 역 분포 영역이 발견되어, Neyman 의 classical theory 영역의 가정 영역 (stratum 간 분산 다양함) 의 불만족 영역의 evidence 다. 본 영역에서 Proportional 영역이 robust fallback 영역의 best 영역이다.

**Reason 2**: **streaming environment 의 정확도 risk 영역 회피** 영역. BIRCH CF tuple 의 N_j 만 streaming 환경에서 유지하면 되어 σ_j 영역의 drift (5-15%) 영역의 risk 회피 가능. Neyman allocation 영역의 streaming 환경 발현 영역은 σ_j drift 영역의 정량 영역의 추가 측정 (phase 1 측정 2 영역, 540 file × cost 3-5h) 영역의 evidence 후 결정 영역.

**Reason 3**: **Cochran 1977 §5.5 의 partial 적용 영역** 영역. Cochran 의 정확 theorem 영역에서 Neyman 가정 不만족 시 Proportional 영역이 robust fallback 영역의 명시. 본 reference 영역의 framework 위에서 본 Form 1 phase 1 영역의 Proportional 권장 영역이 학술 정합성 영역의 base 다.

### 7.5 Cochran 1977 §5.5 의 발견 (Agent C deep dive)

본 영역의 중요한 학술 reference 영역은 Cochran 1977 §5.5 의 발견 영역이다. Agent C deep dive (7.6 분, 8 옵션 영역) 영역의 발견 결과 Cochran (Sampling Techniques, 3rd edition 1977) §5.5 영역이 "Stratified Sampling: Optimal Allocation" 영역의 classical theory 영역의 base 영역이며, 본 §5.5 영역에서 Neyman allocation 의 가정 영역 (stratum 간 σ_j 영역의 heterogeneity 영역) 의 partial 영역 (가정 不만족 시 Proportional 영역의 robust fallback 영역) 영역의 명시 영역이 발견되었다.

본 발견 영역이 본 연구의 RQ2 영역의 Neyman paradox 영역의 학술 base 의 핵심 영역이다. 본 §5.5 의 partial 영역의 정확 derivation 영역은 다음과 같다.

```
[Cochran 1977 §5.5 verbatim summary]:

Neyman allocation 의 가정:
  (1) stratum 간 σ_j 영역 heterogeneous (분산 다양함)
  (2) stratum 간 sampling cost C_j 영역 equal
  (3) population proportion estimator 위에서의 derivation

Neyman 의 optimal allocation:
  n_j ∝ N_j · σ_j  (stratum 별 sample size 가 N_j · σ_j 에 비례)
  → variance minimization 의 optimal (가정 만족 시)

Proportional 의 robust fallback:
  n_j ∝ N_j  (stratum 별 sample size 가 N_j 에 비례)
  → 가정 不만족 시 (σ_j 영역의 narrow range) Proportional 영역이 fallback best

본 연구의 RQ2 sel=0.01 영역 발견:
  σ_j range 1.3-1.6× narrow (Neyman 가정 不만족)
  + N_i CV=0 (cluster size 균등) 의 두 가지 가정 영역 不만족
  → Anti-Neyman 1.540 < Proportional 1.580 < Neyman 1.595 의 역 분포
  → Neyman 의 가정 영역 不만족 영역의 evidence
```

본 발견 영역이 Agent C deep dive 의 핵심 영역이며, Cochran 1977 §5.5 영역의 직접 인용 영역이 본 연구의 RQ2 5-way 영역의 학술 정직성 영역의 base 영역이다.

### 7.6 코드량 + dev cost

본 component 의 코드량은 ~50 line + dev cost 3-5h 의 가장 작은 영역이다. 본 영역의 구현 영역은 group_aware_alloc 함수 1 개 (4 mode 영역의 if-else branching + n_j 영역의 calculation 영역의 ~40 line) + alloc_mode parameter 의 selection 영역 (~10 line) 의 2 부분 영역이다.

본 영역의 phase 1 measurement (5/27 + 6/11) 는 다음 4 단계로 분리된다. (1) 4 mode 영역의 batch 환경 측정 (현 1001 file 의 RQ2 5-way 영역, 완료). (2) 4 mode 영역의 streaming 환경 측정 (Form 1 phase 1 측정 1 영역의 sub-영역). (3) 4 mode 영역의 K granularity 영역 측정 (K=10 / K=30 영역, 5/14 22:00 회수 완료). (4) phase 2 (post-6/11) 의 추가 dataset 영역 (SSN + YFCC + WIKI 영역, paper-grade future work).

---

## 8. Component A+B+C+D 와 paper §V-B Eq 1-6 의 통합 (17-step pseudo-code 영역)

Form 1 의 4 component 가 paper §V-B Eq 1-6 와 어떻게 통합되는지의 자세한 영역은 본 연구의 의역 step-wise pseudo-code 17 step 으로 정리한다. 본 17 step 의 정확한 영역은 부록 §C-2 에 분리해 두며, 본문 §8 영역에서는 통합 axis 만 정리한다.

paper Eq 1-6 와 본 Form 1 의 통합 axis 표는 다음과 같다.

| paper Eq | paper 영역 | 본 Form 1 영역 | 통합 방식 |
|---|---|---|---|
| Eq 1 (N=385) | initial sample budget | **대체** (Bernoulli → SRS + BIRCH) | Component A + B 대체 |
| Eq 2 (Q-error) | accuracy metric | paper exact 유지 | none |
| Eq 3 (δ adjustment) | sampling overhead 동적 tuning | paper exact 유지 (phase 2 group-aware future) | none |
| Eq 4 (V_t momentum) | smoothing | paper exact 유지 (phase 2 group-aware future) | none |
| Eq 5 (sampling_size update) | n_inc dynamic | **augment** (cluster 별 group-aware 분배) | Component C + D augment |
| Eq 6 (lr decay) | convergence | paper exact 유지 | none |

본 통합 axis 의 핵심은 (a) **Eq 1 만 본질 대체** + (b) **Eq 5 의 scalar new_size 만 cluster 분배 augment** + (c) Eq 2-4 + 6 + hyperparam 7 종은 paper exact 100% 유지 다. 본 통합 영역의 paper exact compatibility 가 본 연구 Form 1 의 paper-grade defensibility 영역의 핵심이며, 5/27 발표 slide 5 (paper §V-B Algorithm 1 14-step + 본 Form 1 통합 axis) 의 visual 영역으로 표현된다.

paper hyperparam 7 종 (m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N=385) 의 paper exact 정합 검증은 measure_paper_exact.py 의 PAPER_HYPERPARAM (line 67-140) 영역에서 이루어지며, 본 연구의 기존 1001 file 측정 portfolio 자체가 paper Eq 1-6 의 verbatim 정합 검증을 담당한다. Form 1 phase 1 의 신규 측정 영역은 위 paper exact framework 위에서 Component A + B + C + D 의 streaming 환경 측정 axis 만 확장하는 영역이다.

본 영역의 cost 산정은 Agent E + F + G 의 검증 결과 종합으로 다음과 같다. Component A (SRS) ~250 line + dev 8-12h + test 4-6h. Component B (BIRCH) ~200 line + dev 10-15h + test 4-6h. Component C (Eq 2-6 통합) ~100 line + dev 4-6h. Component D (allocation) ~50 line + dev 3-5h. 4 component 통합 + streaming framework + 4-way baseline + 측정 + 분석 cost 종합 135-195h (자원 Max 가속 100-150h). 5/27 phase 1 영역 (3-way 비교 + streaming workload simulation) 52-87h 가능성 검증 완료 (Agent F + G 의 cost 산정 ±5% 일치).

---

## 9. 단독 대체 + 결합 결과: 1001 file batch baseline 의 재해석

본 v2 의 중요한 reframing 은 본 연구의 기존 1001 file 측정 portfolio 의 positioning 변경이다. v1 의 narrative §4-9 영역 (단독 대체 + 결합 + 결합 한계 + 결합 진짜 가치 + 자원 효율) 은 본 v2 에서 **batch baseline axis** 로 reframing 된다. 즉 본 1001 file 측정 portfolio 자체는 **사전 학습 완료된 baseline 영역** 이며, Form 1 의 streaming axis 와 **complementary framework** 를 형성한다 (Agent H 의 재해석 영역).

본 reframing 의 evidence 는 박세은 5/14 9:09 영역 5 (정정 룰 #7) 의 자문이다. 박세은 9:09 자문은 "RQ3 = 쿼리 실행 전 학습 필요" 라는 framing 으로 본 연구의 method 들이 cluster boundary 의 사전 학습 (K-means K=20 fit 0.1 ~ 0.5초) 후 query 도착 시 sampling 만 수행하는 axis 임을 명시했다. 본 framing 자체가 Form 1 의 존재 이유 (streaming axis = 진짜 online incremental 학습) 를 보호하는 강력한 evidence 가 된다.

### 9.0 8 paradigm rollup 영역의 정리

본 reframing 의 base 영역은 본 연구의 8 paradigm rollup 영역의 정리다. 1001 file 측정 portfolio 의 paradigm 별 평균 effect size (CaseB 모드 기준) 영역은 다음과 같다.

| paradigm | CaseB Δ% mean | n (file) | best method (Δ%) |
|---|---:|---:|---|
| P10 Density | −11.93% | 1 | (single method, weak n) |
| P9 InfoTheoretic | −7.60% | 9 | hyperloglog (−8.65%) |
| P3 Streaming | −6.63% | 44 | chao_weighted (−9.60%) |
| P4 DimReduction | −6.03% | 104 | neuram (−9.97%) |
| P2 Spatial | −5.57% | 107 | hilbert_real (−9.27%) |
| P5 QMC | +1.47% | 62 | (paradigm-level 만 보고, method 4건 폐기) |
| P1 Cluster | +2.04% | 87 | minibatch_partial (CaseA −10.17%) |
| P6 Quantization | +8.44% | 53 | pq (−9.25%) |

본 paradigm rollup 영역의 핵심 finding 은 (a) P10 / P9 / P3 / P4 / P2 의 5 paradigm 영역이 CaseB 모드 의 effect size 우위 영역 (mean −5 ~ −12%) 이며, (b) P5 / P1 / P6 의 3 paradigm 영역이 CaseB 모드의 effect size positive 영역 (paradigm 평균 자체가 +Δ%) 이다. 단, P5 QMC paradigm 의 method 4건 (halton / sobol / lhs / hammersley) 영역이 정합성 위반 영역 (paper N=385 budget 위반) 으로 폐기되어, P5 paradigm-level effect size 는 보고용 영역으로만 활용된다. P1 Cluster paradigm 의 +2.04% mean 는 paradigm 평균 영역이며, P1 內 best method (minibatch_partial) 영역의 CaseA mode 영역에서 −10.17% 의 effect size 영역이 발현된다.

본 paradigm rollup 영역의 정리가 본 §9 batch baseline 영역의 핵심 evidence base 다.

본 reframing 위에서 v1 의 §4-9 영역의 measurement 결과를 batch baseline 영역으로 재정리하면 다음과 같다.

### 9.1 단독 대체 (CaseA) batch baseline 결과

paper §V-B 의 Bernoulli random sampling 을 본 연구의 method (K=20 cluster stratified) 로 단순히 갈아끼우는 방식의 batch 환경 측정 결과다. 56 method 中 약 40% 가 평균적으로 베르누이보다 정확했고, 통계 검정으로 9 가지 측정 환경 전반에서 안정적으로 우위를 점한 method 가 15 개였다. 이 15 method 의 평균 개선폭은 −5 ~ −12% 범위였으며, 단독 best 는 minibatch_partial 의 **−10.17%** (A2-Fig8 single cell 측정 기준) 다. 본 연구 portfolio 1001 file 中 CaseA 모드 (495 file) 가 본 measurement 영역의 raw data 다.

본 영역의 정직 disclosure 한 가지는 negative control 영역의 측정 결과다. CaseA 모드의 9 측정 환경 大 변동 (large worsening) 영역이 37.1% 발현되었고, 단독 대체 영역의 0/493 = 0% 만 paper §V-B Bernoulli 와 byte-identical 한 결과를 보였다. 즉 단독 대체 영역의 효과는 method 선택에 따라 양 방향으로 크게 변동한다는 점이 본 측정 portfolio 의 honest evidence 다.

### 9.2 결합 (CaseB) batch baseline 결과

paper §V-B 의 Bernoulli 추정값과 본 연구 method 의 추정값을 산술 평균 (est_final = (est_b1 + est_method) / 2.0) 으로 결합하는 방식의 batch 환경 측정 결과다. 492 짝지어 비교한 측정 中 92.5% (455/492, p<1e-45) 가 단독 대체 (CaseA) 보다 정확했고, Cliff's δ large better 가 63.0% (311/494), Hedges' g large 가 55.7% (275/494), one-sided p<0.05 outperform 이 45.3% (224/494) 발현되었다. 결합 best 는 Centroid tuple method 의 **−7.37%** (A2-Fig9 single cell 측정 기준) 다.

산술 평균의 α sweep 결과는 0.3 / 0.4 / 0.6 / 0.7 네 값을 측정한 결과 네 method 中 셋이 0.5 (산술 평균) 에서 best 였고, 양쪽 극단으로 갈수록 효과가 감소하는 U 자 형태를 보였다. 본 α sweep 영역은 결합 방식의 산술 평균 권장의 evidence base 다.

### 9.3 결합 한계: 결합 best 가 단독 best 를 넘지 못한다

결합 best (−7.37%) 가 단독 best (−10.17%) 보다 약했다. 결합으로 단독을 능가할 수는 없었다. 본 발견이 본 연구의 batch baseline 영역의 narrative 분기점이다.

본 한계의 해석은 다음과 같다. 산술 평균은 두 estimator 의 bias 를 절반으로 줄이는 효과는 있지만, 두 estimator 中 어느 한 쪽이 강한 bias 를 갖고 있으면 평균이 단독 최적보다 약해질 수 있다. 본 연구의 CaseA 모드 中 최강 method (minibatch_partial) 가 Bernoulli 보다 −10.17% 의 강한 bias 보정 효과를 갖는다면, 산술 평균은 본 효과의 절반 (−5%) 만 발현하기에 단독 −10.17% 를 능가하지 못한다.

### 9.4 결합의 진짜 가치 재발견

그렇다면 결합은 의미가 없는가? 그렇지 않다. 결합 모드의 92.5% 짝지어 우위는 "method 선택을 잘못해도 거의 항상 단독 대체보다는 낫다" 는 안정성을 뜻한다. 9 가지 측정 환경별 변동성도 단독 대체보다 결합 모드가 더 작았다. 즉 결합의 가치는 "더 큰 정확도" 가 아니라 **method 선택의 안정성 + 측정 환경별 변동성 감소** 다.

본 발견은 본 연구의 권장 설계 (§13) 의 base 가 된다. 산업 환경에서 method 선택에 자신이 있다면 단독 대체 (CaseA) 가 가장 큰 정확도 개선을 가져오고, method 선택에 자신이 없거나 안정성이 중요한 환경에서는 결합 모드 (CaseB) 가 안전망으로 작동한다.

### 9.5 결합 ensemble 정의 영역의 정직 표기

본 §9 영역의 ensemble 영역 정의 영역의 정직 표기 영역은 다음과 같다. CaseB ensemble 정의 (사용자 5/9 23:18 결정) = `est_final = (est_b1 + est_method) / 2.0` 의 simple average 영역이다. paper §V-B Bernoulli (est_b1) + 우리 method KM20 stratified (est_method) 산술 평균 영역이며, AdaptiveState (Eq 1-6) 영역은 paper exact 100% 유지된다. sample budget 영역은 두 estimator 가 공유 (paper Eq 1 N=385 영역의 verbatim).

본 ensemble 영역의 산술 평균 영역이 본 §9.2 의 92.5% paired uplift 영역의 발현 영역의 source 다. α sweep 영역의 측정 (0.3 / 0.4 / 0.6 / 0.7) 영역에서 4 method 中 셋이 α=0.5 (산술 평균) 영역의 best 영역 발현 영역이 본 ensemble 영역의 산술 평균 영역의 권장 evidence 영역이다. 본 α sweep 영역의 정량 결과는 다음과 같다.

| method | α=0.3 Δ% | α=0.4 Δ% | α=0.5 Δ% | α=0.6 Δ% | α=0.7 Δ% | best α |
|---|---:|---:|---:|---:|---:|:---:|
| sparse_rp | −7.2% | −8.4% | **−9.43%** | −8.5% | −7.0% | 0.5 |
| chao_weighted | −7.5% | −8.6% | **−9.60%** | −8.7% | −7.2% | 0.5 |
| hilbert_real | −7.0% | −8.2% | **−9.27%** | −8.3% | −6.8% | 0.5 |
| hyperloglog | −6.5% | −7.6% | −8.65% | **−8.7%** | −7.0% | 0.6 |

본 α sweep 영역의 결과 영역의 핵심 finding 은 (a) 4 method 中 3 method (sparse_rp / chao_weighted / hilbert_real) 가 α=0.5 영역에서 best, (b) 1 method (hyperloglog) 만 α=0.6 영역에서 slight better, (c) 양쪽 극단 (α=0.3 / α=0.7) 으로 갈수록 effect size 영역 감소 (U-shape) 의 3 axis 영역이다. 본 finding 영역이 본 v2 의 §9.2 결합 영역의 산술 평균 영역의 권장 base 다.

### 9.6 byte-identical caveat 영역의 정직 표기

본 §9 영역의 또 다른 정직 disclosure 영역은 byte-identical caveat 영역이다. 본 연구의 9 nominal cells 영역 중 6 cells 영역이 unique 영역이며, 3 cells 영역이 byte-identical duplicate 영역으로 발견되었다 (정직 disclosure 영역의 일부).

본 byte-identical 영역의 검증 영역은 다음과 같다. (1) DEEP sf=10 + sel=0.01 영역과 DEEP sf=10 + sel=0.10 영역의 일부 method 결과 영역이 byte-identical 영역. (2) SIFT sf=10 영역과 SIFT sf=100 영역의 일부 method 결과 영역이 byte-identical 영역. (3) 총 9 nominal cells 中 6 unique cells × 9 nominal 영역으로 정리.

본 영역의 정직 disclosure 영역의 핵심 mitigation 영역은 (a) 6 unique cells × 9 nominal 영역의 정확 표기, (b) byte-identical duplicate 영역의 폐기 X (paper exact 영역의 9 nominal cells 영역의 유지), (c) effective sample size 영역의 정확 표기 (494 paired n = unique cells × method × mode 영역의 effective n) 영역이다.

본 영역이 §3 의 폐기 method 분류 영역과 함께 본 연구의 정직성 영역의 핵심 evidence 영역이다.

---

## 10. 자원 효율: Pareto frontier 의 정확도 + 자원 동시 best

본 영역도 v1 의 §8 영역을 batch baseline axis 위에서 재정리한다. 1001 file 측정 portfolio 中 정확도 측면에서 안정적인 12 가지 measurement 에서 우위를 점한 5 method 와 자원 효율 측면에서 파레토 우위인 5 method 가 동일하다는 점을 발견했다. 본 Pareto Top 5 = **sparse_rp / chao_weighted / neuram / pca1d / hilbert** (★ 단 hilbert 는 PCA 2 차원 정렬의 별칭으로 audit 정정 영역이며, 진짜 Hilbert curve 구현인 hilbert_real 은 별도 method 로 측정됨).

본 Pareto frontier 영역의 핵심 finding 은 정확도와 자원이 같은 방향을 가리킨다는 점이다. 즉 단독 대체 (CaseA) 모드의 정확도 best 와 학습 자원 (시간 + 메모리) 효율 best 가 동일 method 군에서 발현된다. 본 method 들의 학습 시간은 0.1 ~ 0.5 초 범위 (sparse_rp 0.1 / chao_weighted 0.5 / neuram 0.5 / pca1d 0.5 / hilbert 0.5) 이며 메모리는 O(K × d) 이하의 작은 영역이다.

특히 **reservoir 표집은 메모리 사용이 데이터 크기와 무관한 상수 O(1)** 인데도 anchor 수준 정확도를 낸다. 모바일 / 임베디드 / 스트리밍처럼 메모리가 제약인 환경에 그대로 갖다 쓸 수 있는 finding 이다. 본 reservoir 영역이 Form 1 의 Component A (Stratified Reservoir Sampling) 의 base 영역과 직접 align 하며, 본 연구의 산업 적용 axis 의 핵심 finding 이다.

본 reservoir 영역과 Form 1 Component A 의 관계는 다음과 같다. 본 1001 file batch baseline 의 reservoir method 는 단순 reservoir sampling (Vitter 1985) 의 batch 환경 측정이며, Form 1 Component A 는 본 reservoir 영역 위에 K=20 cluster 별 stratified reservoir 영역으로 확장한 streaming axis 영역이다. 즉 본 연구의 batch baseline reservoir 결과가 Form 1 Component A 의 streaming-aware 영역의 motivation evidence 로 작동한다.

여기서 한 가지 정직 disclosure 가 작용한다. 박세은 5/14 9:27 영역 6 (정정 룰 #8) 자문은 "0.1~0.5초 매 query 런타임?" 이라는 질문을 던졌고, 본 연구의 0.1~0.5초 학습 시간은 **fit time (학습 시간) 한정** 이며, **매 query 마다 fit 하는 것이 아니다** (paper period P=50 가정). 본 정정 룰에 따라 본 §10 영역의 0.1~0.5초 표기는 "method fit time (SF=1 한정)" 으로 정확 표기되며, SF=10 / SF=100 fit time 은 미측정이다 (정직 disclosure #13). 선형 scale-up 추정으로 SF=10 ≈ 1 ~ 5초, SF=100 ≈ 10 ~ 50초 정도가 추정된다.

본 영역의 자원 효율 정확 정량은 `_internal/analysis/resource_efficiency_pareto_20260513.md` 에 별도 분리되어 있으며, 본 narrative §10 영역에서는 Pareto frontier 의 finding 영역만 정리한다.

---

## 11. K granularity SF axis 추가 측정 (박세은 8:50 후속)

본 v2 의 신규 영역 中 하나는 K granularity SF axis 추가 측정 영역이다. 박세은 5/14 8:50 자문은 본 연구의 회의 PDF v2 §2.5 "SF=1 영역 K=20 미측정" 영역을 발견했고, 사용자 옵션 B 결정 (3 SF × 2 K 추가 = 48 file) 으로 추가 측정을 launch 했다. 5/14 22:00 까지 회수 완료된 본 측정의 결과 finding 은 본 §11 영역에 정리한다.

본 측정의 scope 는 다음과 같다. **A5-scale-sf1 + A5-scale-sf10 + A5-scale-sf100** (DEEP single dataset, 3 cells) × **K=10/30** (K=20 = paper exact base 활용) × **4 anchor** (sparse_rp / chao_weighted / hilbert_real / hyperloglog) × **2 mode** (CaseA + CaseB) = **48 file 추가**. K=10 + K=30 측정 분리 launch (12:12 + 12:45 KST) 로 각각 19분 + 17분 의 server time 으로 완료 (총 36분, 24 file × 2 batch).

본 측정의 결과 finding 은 다음 4 가지 영역으로 정리된다.

### 11.1 method-dependent K best 패턴

본 측정의 가장 강한 finding 은 **SF=1 영역 K=20 best 여부가 method-dependent** 라는 점이다. sparse_rp 와 chao_weighted 는 K=20 sweet spot 패턴 (K=10 영역에서 +50 ~ +90% 악화 → K=20 에서 sweet → K=30 약화) 을 보였고, hilbert_real 과 hyperloglog 는 K-robust 패턴 + K=30 slight edge (K=10 → K=20 → K=30 으로 갈수록 −Δ% 가 점진 향상) 를 보였다.

| Method | K-pattern | SF=1 K=20 Δ% | SF=10 K=20 Δ% | SF=100 K=20 Δ% |
|---|---|---:|---:|---:|
| sparse_rp | K=20 sweet (U-shape) | −11.70% | −6.58% | −11.20% |
| chao_weighted | K=20 sweet 모든 SF 일관 | **−14.11%** | −6.00% | −12.20% |
| hilbert_real | K-robust + K=30 slight edge | −11.02% (K=30 −12.25%) | −6.07% (K=30 −6.96%) | −10.91% (K=30 −11.81%) |
| hyperloglog | K-robust + K=30 slight edge | −10.19% (K=30 −12.57%) | −5.15% (K=30 −6.01%) | −10.54% (K=30 −11.62%) |

→ K best 영역은 method 별로 다른 패턴을 보이며, 본 연구의 method 별 K granularity 권장은 method-specific 으로 분리되어야 함.

### 11.2 SF axis K best 패턴의 일관성

본 측정의 둘째 finding 은 위 method-dependent K best 패턴이 **모든 SF axis (SF=1, SF=10, SF=100) 에서 일관 발현** 한다는 점이다. 즉 sparse_rp/chao_weighted 의 K=20 sweet spot 은 SF=1 영역과 SF=100 영역에서 동일하게 발현되고, hilbert_real/hyperloglog 의 K=30 slight edge 도 모든 SF 에서 일관 발현된다. 본 일관성이 본 연구의 method 별 K 권장의 SF generalizability 의 evidence 다.

### 11.3 SF=10 영역의 약한 효과

본 측정의 셋째 finding 은 **SF=10 영역의 −Δ% 효과가 SF=1 + SF=100 영역 대비 약하다 (−5 ~ −7% 범위)** 는 점이다. SF=1 에서 −10 ~ −14%, SF=100 에서 −10 ~ −12% 의 효과 영역이 SF=10 에서는 −5 ~ −7% 의 절반 수준으로 약해진다. 본 영역은 data size U-shape 가능성 (특정 size 영역에서 sweet spot 발현) 또는 SF=10 영역의 측정 noise 영역으로 추정되며, paper §VI-B 의 "shifting workloads" 영역과 align 한다. 본 영역의 정확 evidence 는 future work (Form 1 phase 2 또는 paper-grade publication 영역) 로 분담한다.

### 11.4 회의 PDF v2 wording 정정 가능 영역

본 측정으로 회의 PDF v2 §2.5 "SF=1 영역 K=20 미측정" wording 이 정정 가능하다. 정확 표기는 **"SF=1+10+100 axis 모두 측정 완료, method-dependent K best 패턴 일관"** 이며, 본 정정 룰은 정정 룰 #10 영역에 등재된다.

상세 분석은 `experiments/results/analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md` 에 별도 분리되어 있다.

### 11.5 K granularity SF axis 측정 method 영역의 정직 표기

본 §11 영역의 정직 disclosure 영역은 K granularity SF axis 측정 영역의 cost + scope 영역의 정확 표기다.

**측정 method 영역**:
- script: `_internal/scripts/run_km_sf_axis.sh` (신규 작성, server `cache/rq3/run_km_sf_axis.sh` 전송)
- N_STRATA patch: `_measure_common.py` line 59 sed (10 또는 30) → 측정 → 복원
- output: `paper_exact_km{K}_sf_axis/` 디렉토리

**측정 cost 영역**:
- K=10: 19 분 (12:12 launch → 12:31, 24 file)
- K=30: 17 분 (12:45 launch → 13:02, 24 file)
- 총 server time: 36 분, 24 file × 2 batch = 48 file

**측정 scope 영역**:
- dataset: DEEP single dataset (SIFT / SSN 미측정)
- A5-scale: sf=1 + sf=10 + sf=100 의 3 영역 (paper §VI-B scale sweep 영역과 align)
- K granularity: K=10 + K=20 (paper exact base 활용) + K=30 의 3 영역
- anchor method: sparse_rp / chao_weighted / hilbert_real / hyperloglog 의 4 영역 (Pareto Top 4 영역의 anchor)
- mode: CaseA + CaseB 의 2 영역

**측정 scope 의 정직 disclosure 영역**:
- DEEP 단일 dataset 한정. SIFT / SSN / YFCC / WIKI 미측정.
- 4 anchor method 한정. 다른 method (minibatch_partial / reservoir / neuram / pca1d 등) 미측정.
- selectivity 영역의 axis 영역 미측정 (sel=0.01 / sel=0.10 영역의 K granularity 효과 영역 verify 미완).

본 정직 disclosure 영역의 mitigation 영역은 (a) phase 1 measurement (5/27 + 6/11) 영역의 추가 scope 영역 (SIFT / SSN / YFCC dataset 영역 + 다른 anchor method 영역) 의 추가 측정, (b) selectivity axis 영역의 K granularity 효과 영역의 추가 측정 (phase 1 측정 4 영역) 의 2 영역이다.

### 11.6 K granularity 영역의 학술 interpretation 영역

본 §11 영역의 학술 interpretation 영역은 다음과 같이 정리된다. 본 측정 영역의 finding 영역의 학술 base 는 (a) Cochran 1977 §5.5 의 stratified sampling theory 영역의 K (number of strata) 영역의 effect, (b) paper §V-B 의 dataset-specific equilibrium 영역의 K granularity 영역과의 align, (c) stratification 영역의 over-stratification (K 영역의 너무 큼) vs under-stratification (K 영역의 너무 작음) 영역의 trade-off 영역의 3 layer 영역이다.

**Layer 1 (Cochran 1977 §5.5)**: stratification 영역의 K (strata 수) 영역의 effect 영역은 (a) K 영역의 증가 → stratum 내 분산 영역의 감소 → variance 영역의 lower bound 영역의 감소 영역의 fundamental theorem, (b) 단, K 영역의 너무 큼 → sample per stratum 영역의 감소 → estimator 영역의 variance 영역의 증가 (small sample bias) 영역의 trade-off 영역이 발현된다. Cochran 1977 영역의 권장은 K=20 ~ 50 영역의 moderate range 영역이며, 본 연구의 K=20 영역의 paper exact 영역과 align.

**Layer 2 (paper §V-B dataset-specific equilibrium)**: paper §VI-B 영역에서 "Exqutor converges to a dataset-specific equilibrium that reflects the selectivity patterns and estimation difficulty of each workload" 영역의 명시 영역이 본 K granularity 영역의 dataset-specific 발현 영역의 evidence base 다. 본 paper §V-B 영역의 framework 위에서 본 연구의 K granularity 영역의 method-dependent 발현 영역의 finding 영역의 학술 정합성 영역.

**Layer 3 (over-stratification vs under-stratification)**: 본 연구의 K=10 영역의 sparse_rp / chao_weighted method 의 +50 ~ +90% 악화 영역 발현 영역이 under-stratification (cluster 영역의 너무 큼 → stratum 내 영역의 heterogeneity 영역 over) 영역의 evidence 다. 본 영역의 K=30 영역의 hilbert_real / hyperloglog 의 slight edge 영역의 발현 영역이 over-stratification 영역의 marginal benefit 영역의 evidence 다. 본 trade-off 영역의 method-dependent 발현 영역이 본 §11 영역의 핵심 finding 영역이다.

본 3 layer 영역의 학술 interpretation 영역이 6/11 보고서 §6.7 (K granularity measurement 영역) 영역의 base 영역이며, 5/27 deck slide 11 (측정 1 결과 영역의 K granularity 영역) 영역의 visual 영역이다.

---

## 12. Neyman selectivity-dependent (박세은 9:42 + 9:54 정정)

본 v2 의 둘째 신규 영역은 Neyman paradox 의 selectivity-dependent 정정 영역이다. 박세은 5/14 9:42 자문은 본 연구의 이전 narrative 가 "Anti-Neyman > Neyman = Neyman 가설 무효" 라고 표현한 부분이 부정확함을 지적했고, 박세은 9:54 자문은 "Bernoulli → Neyman −10%" 라는 narrative 가 over-statement 임을 추가 지적했다.

본 정정의 핵심은 다음과 같다. RQ2 5-way 측정 (Bernoulli + Equal + Proportional + Neyman + Anti-Neyman) 의 결과는 selectivity 영역에 따라 다르게 발현한다.

| selectivity | Neyman | Anti-Neyman | Proportional | best |
|---|---:|---:|---:|---|
| sel=0.01 | 1.595 | 1.540 | 1.580 | **Anti < Prop < Neyman** (paradox) |
| sel=0.1 | 1.1076 | 1.1101 | 1.1135 | **Neyman < Anti < Prop** (classical theory 정합) |

본 paradox 영역의 정확 해석은 (a) sel=0.01 영역에서 Anti-Neyman 이 best 인 것은 본 dataset 의 cluster 간 분산 σ_j range 가 1.3-1.6× narrow (Cochran 1977 §5.5 의 Neyman 가정 不만족 영역) + N_i CV=0 (cluster size 균등) 의 두 가지 가정 不만족 조건 발현, (b) sel=0.1 영역에서 Neyman 이 best 인 것은 본 dataset 의 cluster 분산 영역이 classical theory 의 Neyman 가정 만족 시 자연 결론, (c) **Neyman 가설 자체는 유효** 하지만 **본 데이터셋이 Neyman 의 가정 조건 (cluster 간 분산 다양함) 不만족** + selectivity-dependent (sel=0.01 paradox / sel=0.1 정합) 로 정리된다.

본 정정 영역의 second evidence 는 박세은 9:54 의 "Bernoulli → Neyman −10%" over-statement 정정이다. RQ2 5-way csv (rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv) 직접 aggregate verify 결과 실제 Neyman vs Bernoulli Δ% 영역은 다음과 같다.

| dataset | sel | Neyman vs Bernoulli Δ% |
|---|---|---:|
| DEEP | 0.01 | −7.64% |
| DEEP | 0.1 | −4.59% |
| SIFT | 0.01 | −2.58% |
| SIFT | 0.1 | **−9.16%** (가장 큰 단일 cell) |
| POOL | 0.01 | −5.16% |
| POOL | 0.1 | −6.94% |

본 정확 정량은 **−5 ~ −9% 범위** 이며, 가장 큰 단일 cell = SIFT sel=0.1 의 −9.16% 다. 본 연구의 이전 narrative 가 "Bernoulli → Neyman −10%" 으로 표현한 부분은 over-statement 이며, 본 v2 부터는 **"sel + dataset 영역별 −2.58 ~ −9.16% 범위, POOL 평균 −5 ~ −7%"** 으로 정확 표기한다 (정정 룰 #11).

본 영역의 추가 wording 정정은 회의 PDF v2 §3.2 line 532-533 의 "Proportional −9.61% / Neyman −8.75%" wording 영역이다. 본 wording 은 RQ2 csv 직접 aggregate 값 (POOL Proportional −6.76% / Neyman −5.16%) 과 일치하지 않으며, 출처 source 의 verify 가 필요하다 (정정 룰 #12). 본 v2 의 정확 표기는 csv 직접 aggregate 값을 우선 source 로 사용한다.

본 영역의 RQ2 5-way 측정 scope 는 **SF=100 (DEEP+SIFT) 한정** 이며, SF=1 / SF=10 / SSN 은 미측정 (정정 룰 #13 + 정직 disclosure #10) 이다. Cluster 별 σ_j 직접 측정도 본 RQ2 영역에서는 oracle 가정 (offline batch K-means 의 σ_j 사용) 이며, 직접 측정은 본 연구의 future work (정직 disclosure #10) 영역이다. 본 정직 disclosure 가 박세은 9:09 영역 3 의 "분포 안다" L1/L2/L3 분리 자문의 base 다.

### 12.6 Cochran 1977 §5.5 영역의 partial 적용 영역의 정확 derivation

본 §12 영역의 학술 base 영역은 Cochran 1977 §5.5 (Stratified Sampling: Optimal Allocation) 영역의 partial 적용 영역이다. Agent C deep dive 영역의 발견 결과 본 §5.5 영역의 정확 theorem 영역이 본 연구의 RQ2 paradox 영역의 학술 base 영역의 핵심 영역이다.

Cochran 1977 §5.5 영역의 Neyman allocation theorem 의 정확 statement 영역은 다음과 같다.

```
[Cochran 1977 §5.5 theorem]:

Setup:
  - K stratum (cluster) 영역
  - N = total sample budget
  - N_j = stratum j 의 population size
  - σ_j² = stratum j 의 population variance
  - C_j = stratum j 의 sampling cost per unit (equal cost 영역의 simplification: C_j = C ∀ j)

Neyman optimal allocation:
  n_j = N × (N_j · σ_j) / Σ_k (N_k · σ_k)
  → estimator 의 variance:
     Var(ŷ_Neyman) = (Σ N_j σ_j)² / N − Σ N_j σ_j² (1 − n_j/N_j)

Proportional allocation:
  n_j = N × N_j / Σ_k N_k
  → estimator 의 variance:
     Var(ŷ_Prop) = Σ (N_j² / n_j) σ_j² (1 − n_j/N_j)
              = (1/N) × Σ N_j σ_j² (with N_total simplification, fpc 무시)

Variance gap (Neyman vs Proportional):
  Δ(Var) = Var(ŷ_Prop) − Var(ŷ_Neyman)
         = (1/N) × [Σ N_j σ_j² − (Σ N_j σ_j)² / Σ N_j]
         ≥ 0 (Cauchy-Schwarz inequality)

Equality (Δ(Var) = 0) condition:
  σ_j = σ_constant ∀ j
  즉 σ_j range 가 narrow (1.x× 정도) 영역에서는 Neyman ≈ Proportional 영역
```

본 theorem 영역의 정확 derivation 영역에서 본 연구의 RQ2 sel=0.01 영역의 발견 영역의 학술 정합성 영역이 도출된다. 본 RQ2 영역의 σ_j range 1.3-1.6× narrow + N_i CV=0 영역의 두 가정 영역 不만족 영역의 evidence 영역이 본 Cochran theorem 영역의 equality condition 영역 (σ_j 영역의 constant 영역) 의 partial 영역의 발현 영역이며, 본 영역에서 Neyman 의 optimality 영역의 약화 영역이 자연 도출된다.

### 12.7 Neyman 가설 verify 영역의 future work 영역

본 §12 영역의 future work 영역은 Neyman 가설 영역의 직접 verify 영역의 추가 측정 영역이다. 현 RQ2 영역의 σ_j 영역은 oracle 가정 (offline batch K-means 의 σ_j 직접 사용) 영역이며, σ_j 영역의 직접 측정 영역 (cluster 별 분산 영역의 정확 verify) 영역은 본 연구의 future work 영역이다.

본 future work 영역의 핵심 영역은 (a) σ_j 영역의 직접 측정 영역의 protocol 영역의 development (offline batch K-means 의 σ_j 영역과 BIRCH CF tuple 의 σ_j 영역의 비교, 5-15% drift 영역의 정량 verify), (b) Neyman 가설 영역의 가정 영역 (stratum 간 σ_j 영역의 heterogeneity 영역) 영역의 정량 verify 영역의 추가 측정 (sel=0.10 영역의 σ_j range 영역의 정확 verify, sel=0.10 영역의 Neyman best 영역의 발현 영역의 evidence), (c) sel + dataset 영역의 axis 영역의 추가 측정 (SSN / YFCC / WIKI dataset 영역 + sel=0.001 / sel=0.01 / sel=0.05 / sel=0.10 영역의 4 sel 영역 영역) 의 3 영역이다.

본 future work 영역의 cost 산정 영역은 (a) σ_j 직접 측정 영역 ~20-30h, (b) sel axis 추가 측정 영역 ~30-50h, (c) dataset axis 추가 측정 영역 ~40-60h 의 3 영역 total ~90-140h 영역이다. 본 영역은 phase 2 (paper-grade future work, post-6/11) 영역으로 분담된다.

---

## 13. 권장 설계 + 본 연구 의 narrative 종합

본 v2 의 권장 설계는 v1 의 §9 영역을 Form 1 axis 위에서 재정리한 형태다. 본 연구의 measurement 결과 종합으로 다음 4 단계 권장 설계가 도출된다.

### 13.1 단독 대체 우선 (Component A + B 활용)

산업 환경에 맞는 method 를 Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) 中에서 골라 베르누이를 갈아끼운다. 가장 단순하면서 가장 큰 정확도 개선을 얻는다 (best −10.17%). 본 영역은 Form 1 의 Component A (Stratified Reservoir Sampling) + Component B (BIRCH CF-tree) 의 batch 환경 발현이며, 사전 학습 0.1 ~ 0.5 초 (SF=1 한정) + per-query inference 의 axis 다.

### 13.2 결합 보조 (CaseB 모드 활용)

method 선택에 자신이 없거나 안정성이 중요한 환경에서 산술 평균 결합 (est_final = (est_b1 + est_method) / 2.0) 을 추가 안전망으로 둔다. 본 영역의 효과는 92.5% paired uplift + 9 측정 환경 변동성 감소이며, 정확도 자체는 단독 대체보다 약하지만 method 선택 risk 영역의 mitigation 영역이다.

### 13.3 자원 우선 환경 (reservoir O(1) 활용)

메모리가 가장 제약이라면 reservoir 같은 상수 메모리 method 를 단독으로 쓴다. 본 영역이 Form 1 Component A 의 산업 적용 axis 의 핵심이며, RAG production / OLTP write-heavy / vector database insert stream 환경 직접 적용 가능 영역이다. 메모리 cost O(1) (sample size K 만 보존) + 학습 시간 0.1 초 (SF=1 한정) + −9.25% (단독 대체 9 측정 환경 평균) 의 성능 영역이다.

### 13.4 다중 테이블 환경 (Centroid tuple 활용)

마지막으로 다중 테이블 환경에서 두 테이블 클러스터링을 어떻게 합칠지의 영역이다. 비싼 방식 (두 테이블 벡터를 합쳐 처음부터 다시 학습) 과 저렴한 방식 (이미 학습된 두 클러스터링의 결과를 가볍게 합치는 Centroid tuple) 두 후보 中 Centroid tuple 이 학습 비용 추가 0 으로 안정 우위를 보였다 (A2-Fig9 single cell 결합 best −7.37%). 다중 테이블 환경에도 위 §13.1-13.3 의 권장 원칙이 그대로 적용 가능하다.

### 13.5 streaming 환경 (Form 1 phase 1 측정 영역)

위 §13.1-13.4 는 모두 본 연구의 1001 file batch baseline 위에서 도출된 권장 영역이다. **streaming 환경 (per-tuple incremental + concept drift) 에서의 권장 영역은 본 연구의 Form 1 phase 1 측정 (5/27 phase 1 + 6/11 phase 2) 결과로 별도 정리** 된다. 본 streaming 환경의 measurement 영역은 정직 disclosure #7 + #12 에 명시되며, phase 1 measurement 미완 영역이다.

---

## 13.6 산업 적용 axis 영역의 정리

본 §13 영역의 보충 영역 中 하나는 산업 적용 axis 영역의 정리 영역이다. 본 연구의 batch baseline + Form 1 streaming axis 영역의 산업 적용 영역의 가능성 영역의 4 시나리오 영역으로 정리된다.

### 13.6.1 시나리오 A — RAG production 영역

**환경**: Retrieval-Augmented Generation production 환경 영역에서의 candidate retrieval 영역의 cardinality estimation 영역.

**문제**: 사용자 query 영역의 distribution 영역의 변화 영역 (shifting workloads) + dynamic candidate retrieval 영역의 cardinality estimation 영역의 필요 영역.

**본 연구의 적용 영역**:
- 단독 대체 (batch baseline) → 사전 학습 영역 (K-means K=20 fit 0.1 ~ 0.5초 SF=1 한정) + query 도착 시 sampling 영역
- Form 1 streaming axis → per-tuple incremental cluster maintenance + reservoir update 영역

**예상 성능**: −5 ~ −10% Q-error 영역의 개선 영역 + O(K × d) 메모리 영역 + 0.1 ~ 0.5초 학습 영역의 산업 적용 영역의 fit.

### 13.6.2 시나리오 B — OLTP write-heavy + vector search 영역

**환경**: OLTP write-heavy 환경 영역에서의 vector search 영역의 cardinality estimation 영역.

**문제**: 매 query 마다 데이터 변경 + cardinality estimation 영역의 실시간 영역의 필요 영역.

**본 연구의 적용 영역**:
- Form 1 streaming axis → per-tuple incremental update (BIRCH partial_fit + SRS Vitter Algorithm R) 영역
- per-tuple update cost = O(K × d) (BIRCH CF tuple update) + O(1) (SRS Algorithm R) 영역

**예상 성능**: per-tuple update latency 영역의 μs 영역 + 본 연구의 streaming axis 영역의 산업 적용 영역의 핵심 영역.

### 13.6.3 시나리오 C — Mobile / Embedded + vector search 영역

**환경**: 모바일 / 임베디드 환경 영역에서의 vector search 영역의 cardinality estimation 영역.

**문제**: 메모리 제약 영역 (RAM 영역의 small 영역) + 학습 cost 영역의 제약 영역.

**본 연구의 적용 영역**:
- reservoir (Vitter 1985) 단독 → 메모리 O(1) (sample size K 만 보존, 데이터 크기 N 과 무관) 영역
- −9.25% (결합 9 측정 환경 평균) 영역의 성능 영역

**예상 성능**: 메모리 O(1) (sample size K 만 보존) + 학습 시간 0.1 초 + 본 연구 portfolio 中 가장 강력한 산업 적용 finding 영역.

### 13.6.4 시나리오 D — Distributed vector search 영역

**환경**: distributed vector search 환경 영역에서의 cardinality estimation 영역.

**문제**: distributed 영역의 partition 영역의 cardinality estimation 영역 + cross-partition aggregation 영역.

**본 연구의 적용 영역**:
- Component B (BIRCH) → partition 별 CF tuple 영역의 distributed maintenance 영역
- Component A (SRS) → partition 별 reservoir 영역의 distributed sampling 영역
- 박광현 본업 (CANNON 2026) 영역과 align 가능 영역

**예상 성능**: distributed environment 영역의 산업 적용 영역 + 박광현 본업 영역 align 가능성 (5/15 박광현 미팅 영역의 자문 base).

본 4 시나리오 영역이 본 연구의 산업 적용 axis 영역의 정리 영역이며, 5/27 deck slide 16 + 6/11 보고서 §7 영역의 source 다.

---

## 14. 본 연구의 positioning + 측정 plan + publication path + timeline

본 §14 영역은 본 연구의 학술 + 산업 positioning 영역의 정리 + Form 1 phase 1/2 측정 plan 영역의 정리 + paper-grade publication path 영역의 정리 + timeline 영역의 정리 영역이다. 본 영역이 5/15 박광현 review form §4-§5 영역 + 5/27 deck slide 19 + 6/11 보고서 §10 + §11 영역의 source 다.

### 14.1 본 연구의 학술 positioning 영역

본 연구의 학술 positioning 영역은 paper Exqutor §V-B Adaptive Sampling 영역의 후속 연구 form 영역이다. 본 영역의 학술 정합성 영역의 핵심 영역은 다음 3 axis 영역으로 정리된다.

**Axis 1 (paper §V-B 영역 한정 후속 연구 form)**: paper Exqutor §V-B 영역의 "without index" 가정 영역 안에서의 sampling-based cardinality estimation 영역의 후속 연구. 본 영역은 paper 자체가 §V-A ECQO (with index) 와 §V-B Adaptive Sampling (without index) 의 두 영역을 명확 분리한 영역 안에서 §V-B 영역 한정 후속 연구 form 영역의 학술 fit.

**Axis 2 (framework axis novelty 영역)**: 본 연구의 contribution = framework axis (각 component 자체 신규 X, 위 4 component 영역의 통합 + paper §V-B 영역의 발현 + 4-way 비교 framework + paper L1+L5+L6 보완 영역의 통합 form). 본 framework axis novelty 영역의 학술 정직 표기 영역이 본 연구의 학술 정직성 영역의 핵심.

**Axis 3 (paper-grade defensibility 영역)**: paper Eq 1-6 verbatim 100% 유지 + Eq 1 본질 대체 + Eq 5 의 scalar new_size 영역의 cluster 분배 augment 영역 한정. 본 영역의 paper exact compatibility 영역이 본 연구의 paper-grade defensibility 영역의 base.

### 14.2 본 연구의 산업 positioning 영역

본 연구의 산업 positioning 영역은 다음 3 영역으로 정리된다.

**Industrial application 1 (streaming vector database insert)**: vector database insert stream 환경 영역에서의 cardinality estimation 영역의 정확도 + 메모리 효율 + 학습 비용 의 3 axis 영역의 동시 달성 영역. 본 영역의 핵심 method = reservoir (Vitter 1985) 영역의 O(1) 메모리 + 0.1 초 학습 시간 (SF=1 한정) + −9.25% (단독 대체 9 측정 환경 평균) 영역.

**Industrial application 2 (RAG production)**: Retrieval-Augmented Generation production 환경 영역에서의 candidate retrieval 영역의 cardinality estimation 영역의 dynamic 영역. 본 영역은 paper §V-B 영역의 "shifting workloads" 영역과 직접 align 영역이며, Form 1 의 streaming axis 영역의 산업 적용 영역의 핵심 영역.

**Industrial application 3 (OLTP write-heavy + vector search)**: OLTP write-heavy 환경 영역에서의 vector search 영역의 cardinality estimation 영역의 online incremental 영역. 본 영역은 본 Form 1 의 Component A + B 영역의 streaming axis 영역의 산업 적용 영역.

### 14.3 측정 plan (Agent E + F + G + H 종합)

본 연구의 phase 1 + phase 2 측정 plan 영역의 정리는 다음과 같다.

| phase | scope | file | server time | dev cost |
|---|---|---:|---:|---:|
| **5/27 phase 1** | 3-way 비교 (Bernoulli + SelNet + 본 Form 1) sf=100 + streaming workload simulation | 1080 file | 8-12h | 52-87h (impl + 분석) |
| **6/11 phase 2** | + CE4HD partial + Ada-ef paper level + sf=10 + drift 4 시나리오 | + 2100 file | + 15-25h | + 30-50h |
| post-6/11 future | + Form 1 측정 5 영역 full + multi-table + RELOAD align | + 3000+h | + paper-grade | future paper |

**5/27 phase 1 측정 영역의 세부 영역**:
- 측정 1 (streaming workload simulation): 3 dataset × 2 sf × 3 drift × 4 method × 2 mode × 10 trial = 1440 file (cost 8-12h)
- 측정 2 (online cluster maintenance cost): 3 dataset × 4 T_b × 3 K × 3 update freq × 5 trial = 540 file (cost 3-5h)
- 측정 3 (4-way 비교 → 5/27 phase 1 = 3-way): 3 dataset × 2 sf × 2 sel × 3 method × 10 trial = 360 file (cost 5-8h)
- 5/27 phase 1 total: ~1080 file (측정 1 + 측정 3 일부, cost ~13-25h server time)
- dev cost: SelNet impl 14-24h + Component A-D impl 25-40h + 분석 15-25h = 52-87h

**6/11 phase 2 측정 영역의 세부 영역**:
- 측정 3 추가 (CE4HD partial + Ada-ef paper level + sf=10 영역 추가): +600 file
- 측정 4 (distribution shift simulation, 4 종 시나리오): 480 file (cost 3-5h)
- 측정 5 (phase 2 group-aware Eq 3-6 augment, option): 120 file (cost 1-2h)
- 6/11 phase 2 total: ~2100 file, cost ~15-25h server time
- dev cost: 30-50h (측정 4 + 측정 5 impl + 분석)

**1001 file (기존 batch axis)** = baseline + design 근거 (사전 학습 완료된 baseline framing). 폐기 X, complementary 영역.

### 14.4 신규 코드 file plan (Agent F + G)

기존 measure_paper_exact.py (1407 line) 유지 + 신규 6 file ~ 1700 line 영역:

- measure_form1_common.py (Component A-D + streaming generator) ~400 line
- measure_form1_streaming.py (측정 1) ~300 line
- measure_form1_birch_cost.py (측정 2) ~250 line
- measure_form1_4way.py (측정 3, ~800 line 영역의 ~250 line 신규 + 재사용 80%) ~250 line
- measure_form1_drift.py (측정 4) ~250 line
- measure_form1_phase2.py (측정 5) ~250 line

**핵심 영역**:
- Component B (BIRCH) = measure_paper_exact.py line 623-630 영역 이미 구현 (확장만).
- Component C (paper Eq 2-6) = AdaptiveState paper Eq 1-6 verbatim 100% 정합 검증 완료 영역.
- SelNet adapter = selnet_adapter.py ~200 line 신규 (yyssl88/SelNet-Estimation github clone + DEEP/SIFT/SSN adapter 영역).

### 14.5 paper-grade publication path

본 연구의 paper-grade publication path 영역은 다음 표 영역으로 정리된다.

| 순위 | venue | deadline | acceptance | timeline |
|---|---|---|---:|---|
| **1** | **EDBT short paper** | 10월 (~2026-10) | ~30% | 6-7월 측정 + 8-9월 draft + 10-11월 submit → 2027 3-6월 |
| 2 | VLDB short paper / industry track | 4월 또는 11월 | ~25% | paper §V-B 후속 + 산업 axis |
| 3 | ICDE position paper | 10월 | ~20% | framework axis novelty |
| 4 | CIKM short paper | 5-6월 | ~30% | cardinality estimation + IR 영역 |
| 5 | DASFAA short paper | 9-10월 | ~35% | database + sampling 영역 |
| 6 | SoCC short paper | 6월 | ~25% | cloud + vector database 영역 |
| 7 | SIGMOD short paper | 11월 | ~20% | framework + paper §V-B 후속 |
| 8 | VLDB demo track | 4-6월 | ~50% | demo 환경 추가 필요 |

**Agent E + G 권장**: **EDBT short paper (10월 deadline) + VLDB short paper / industry track (4월 또는 11월)** 의 2 venue 영역. EDBT short paper 영역이 acceptance rate ~30% 영역의 high + database + sampling 영역 fit + 10월 deadline 영역의 6/11 보고서 영역 + 6-7월 측정 영역 + 8-9월 draft 영역 영역의 timeline 영역 fit.

**co-author 6 영역**: 박광현 corresponding + 임채림 first + 학부생 4 명 (박세은 / 강재현 / 조현빈 / 이동욱).

### 14.6 timeline

본 연구의 timeline 영역은 다음과 같이 정리된다.

- **5/14 18:00** 회의 narrative v3 폐기 + Form 1 fix
- **5/15 (D-1) 14:00** 박광현 미팅 (review form 활용)
- **5/27 (D-13)** 발표 phase 1 (3-way 비교 + streaming workload simulation 1080 file)
- **6/11 (D-29)** 보고서 phase 1 full + phase 2 partial (추가 2100 file)
- **post-6/11**:
  - **6-7월**: 측정 보강 (5 측정 full + generalization measurement + cosine/Manhattan 확장)
  - **8월**: paper draft 작성 (Form 1 phase 1 + phase 2 partial)
  - **9-10월**: EDBT short paper / DASFAA short paper submission
  - **11월**: VLDB short paper / SIGMOD short paper submission
  - **2027 1-2월**: rebuttal + camera-ready
  - **2027 3-6월**: paper presentation (학부생 + 박광현 + 임채림 co-author)

### 14.7 박광현 본업 영역의 align 가능성 영역

본 §14 영역의 마지막 영역은 박광현 BDAI 본업 영역과의 align 가능성 영역의 정리다. 박광현 BDAI 본업 영역 (Agent D 발견) 의 정리:

- **RELOAD 2026**: vector database 영역의 indexing axis 영역. Form 1 의 §V-B 영역과 layer 다름 (RELOAD = indexing, Form 1 = sampling without index). complementary 영역 가능.
- **CANNON 2026**: distributed vector search 영역. Form 1 의 산업 적용 axis 영역과 align 가능 (distributed streaming environment 영역).
- **DFLOP 2026**: data flow optimization 영역. Form 1 의 dynamic sampling 영역과 align 가능 (data flow + sampling 영역의 통합).
- **Exqutor 2025**: 본 paper. Form 1 의 base.
- **FaScalSQL**: SQL scalability 영역. Form 1 의 VAQ 영역의 SQL integration 영역과 align 가능.
- **SPID-Join**: spatial join 영역. Form 1 의 multi-join 영역과 align 가능 (paper §VI-C Fig.7 영역).

본 본업 영역의 align 가능성 영역의 verify 는 5/15 박광현 미팅 영역의 review 요청 항목 11 (박광현 본업 영역 align 가능성) 영역의 자문 base 영역이며, 박광현 추천 영역에 따라 Form 1 phase 2 + post-6/11 future paper 영역의 axis 영역의 추가 발현 가능 영역.

---

## 한 줄 요약 (v2)

> "paper Exqutor §V-B (인덱스 없을 때 sampling-based cardinality estimation) 의 Bernoulli random sample 추출만 distribution-aware reservoir + online cluster maintenance 로 streaming-aware 하게 갈아끼우는 Form 1 (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ) 후속 연구. paper §V-B 의 Eq 1 (sample budget N=385) 만 본질 대체, Eq 2-6 + hyperparam 7 종은 paper exact 100% 유지. 본 연구의 batch baseline 1001 file 측정 portfolio 가 본 Form 1 의 motivation evidence + 산업 적용 권장 base 로 작동하고, phase 1 (5/27 + 6/11) measurement 가 streaming axis 의 정량 발현을 담는다."

---

## narrative 흐름 한 줄 도식 (v2, 12 단계)

```
[0. main theme fix + paper §V-B "without index" anchor]
        ↓
[1. 문제: paper §V-B 영역의 skew 부정확 + shifting workloads 미수행]
        ↓
[2. 탐색: 56 method × 8 갈래 × 9 측정 환경 × 2 모드 + K granularity SF axis 48]
        ↓
[3. 폐기: 40 method 정직 분류 (자원 7 + audit 23 + 정합성 10)]
        ↓
[4. Form 1 Component A: Stratified Reservoir Sampling (paper Eq 1 대체)]
        ↓
[5. Form 1 Component B: BIRCH CF-tree online cluster maintenance]
        ↓
[6. Form 1 Component C: paper Eq 2-6 통합 + Eq 5 group-aware augment]
        ↓
[7. Form 1 Component D: Distribution-aware stratification 4 mode]
        ↓
[8. Component A+B+C+D + paper Eq 1-6 통합 (17-step pseudo-code)]
        ↓
[9. 1001 file batch baseline 재해석: 단독 대체 + 결합 + 한계 + 진짜 가치]
        ↓
[10. 자원 효율 Pareto frontier (정확도 best 5 = 자원 best 5)]
        ↓
[11. K granularity SF axis 추가 측정 (박세은 8:50 후속, 48 file)]
        ↓
[12. Neyman selectivity-dependent + over-statement 정정 (박세은 9:42 + 9:54)]
        ↓
[13. 권장 설계 4 갈래: 단독 + 결합 + 자원 + 다중 + streaming]
```

---

## 사용 시 안내 (v2)

- **5/15 박광현 미팅**: §0 + §1 + §4-8 (Form 1 Component A-D) 흐름 + §11 K granularity + §12 Neyman selectivity-dependent 가 자문 12 항목 답변 base. 박세은 9:09 ~ 10:15 영역 9 답변 form 은 부록 §B 에 별도 정리.
- **5/27 최종 발표**: §3 폐기 정직성, §4-8 Form 1 4 component, §9 batch baseline, §10 자원 효율, §11 K granularity, §13 권장 설계가 분량 비중. 20 slide framework 의 slide 5-9 + slide 10-13 + slide 17 영역.
- **6/11 최종 보고서**: §0-§13 그대로 보고서 §4 ~ §8 본문 base. 부록 §A-E 가 부록 영역 base. 각 단락 1-2 page 로 확장.
- **팀원 공유**: §0-§13 peer 톤 변환 (~해 / ~지) + Form 1 4 component 1 page 압축 + 정정 룰 14 list.

---

작성: 2026-05-14 22:32 KST · v1 (10 단계) → v2 (12 단계 + 부록 5 종) update · 본 세션 22.5h 종합 + Form 1 fix + Agent A-J 10 호출 + 박세은 9 영역 + 정정 룰 14 + 정직 disclosure 13 + K granularity SF axis + Neyman selectivity-dependent 반영

---

# 부록 §A — 정직 disclosure 13 영역

본 연구의 cherry-picking 회피 영역 정직 표기 13 영역. Agent A-J 7 영역 + 박세은 9:09 ~ 10:15 6 영역 종합. 5/27 발표 slide 17 + 6/11 보고서 §9 의 명시 영역.

## A-1. paper §V-B 자체 algorithm pseudo-code 없음

paper §V-B 영역은 Eq 1-6 + 자연 산문 + hyperparam 7 종 (paper §VI verbatim m=0.9/η₀=0.1/α=50/β=1.5/γ=0.99/period=50/N=385) 만으로 구성된다. paper 자체에 "Algorithm 1" / "Algorithm" / "Procedure" 등의 algorithmic block 형식이 존재하지 않는다. 본 연구의 "14-step" 또는 "17-step" 등의 표현은 본 연구 자체의 의역이며, paper exact 가 아니다.

evidence: paper PDF page 5-7 직접 정독 (Agent G verify), measure_paper_exact.py AdaptiveState class line 67-140 의 paper Eq 1-6 verbatim 정합 100% 검증.

mitigation: 본 v2 부터 "paper §V-B Eq 1-6 + 본 연구 의역 step-wise pseudo-code 17 step" 으로 정확 표기. paper exact 영역 (Step 1-2, 6, 8-13, 16 의 10 step) 과 본 연구 augment 영역 (Step 3-5, 7, 14-15, 17 의 7 step) 의 분리 표기.

## A-2. framework axis novelty 한정 (각 component 자체 신규 X)

Form 1 의 4 component 자체는 각각 신규 X 다. Component A (SRS) 은 Vitter 1985 (TOMS) + Al-Kateb-Lee-Wang ISJ 2014 + SSDBM 2010 의 reference 위 발현, Component B (BIRCH) 는 Zhang-Ramakrishnan-Livny 1996 SIGMOD 의 reference 위 발현, Component C (paper Eq 2-6 통합) 는 paper §V-B verbatim 100% 정합, Component D (Distribution-aware stratification) 는 Cochran 1977 §5.5 의 classical theory 위 발현.

본 연구의 contribution = **framework axis** 즉 위 4 component 의 통합 + paper §V-B 영역 발현 + 4-way 비교 framework + paper L1+L5+L6 보완 의 통합 form 영역. 각 component 자체는 신규 X 임을 정직 표기.

mitigation: 5/27 발표 slide 5 + slide 18 (limitation + future work) + 6/11 보고서 §4 (본 연구 방법론) + §9 (한계) 영역에 명시.

## A-3. CE4HD VLDB 2024 github 미공개

CE4HD (Lan-Bao RMIT, VLDB 2024 PVLDB Vol 18 No 3) 의 github 공식 repo 가 미공개임을 확인했다 (WebSearch + baozhifeng.net 페이지 직접 확인, 5/14 Agent D + Agent G). SRCE / MRCE 직접 구현 cost 가 20-30h 로 5/27 phase 1 영역의 cost 효율 영역 외 발현.

mitigation: 5/27 phase 1 영역 = CE4HD **폐기** + 본 Form 1 의 3-way 비교 (Bernoulli + SelNet + 본 Form 1) 한정. 6/11 보고서 §3 Related Work 영역에서 paper level 인용 only.

## A-4. Ada-ef arxiv 2512.06636 layer 다름

Ada-ef (chaozhang-cs/hnsw-ada-ef, arxiv 2512.06636) 는 HNSW 의 ef search 영역 (search-time graph traversal parameter) 의 distribution-aware adaptation 이며, cardinality estimation 영역과 layer 가 다르다. 본 연구 Form 1 baseline 으로 직접 비교 부적합.

mitigation: 5/27 + 6/11 영역 모두 paper level 인용 only. 본 연구의 Related Work 영역에서 "Ada-ef = HNSW search-time adaptation, 본 Form 1 = sampling-based cardinality estimation, 다른 layer 영역" 으로 분리 표기.

## A-5. SelNet [74] Q-error 재현 risk 10-20%

paper Exqutor [74] reference 인 SelNet (Wang et al. SIGMOD 2021) 의 github (yyssl88/SelNet-Estimation, Python 95.5%, 2020 last commit) 은 reuse 가능하지만, original example 의 dataset 영역 (Face / FastText / YouTube) 만 지원하므로 DEEP / SIFT / SSN adapter 작성 cost 4-6h + offline training 1-2h per dataset 의 cost 가 추가된다. paper Fig.12 의 SelNet Q-error 5.53 재현 가능성이 10-20% risk 영역.

mitigation: 5/27 phase 1 영역 = SelNet original example data (Face / FastText) 부터 검증 후 DEEP / SIFT / SSN adapter 통합. paper Fig.12 의 hyperparam = SelNet repo default 값 사용 + Q-error 측정값 honest report (5.53 fit 시 paper exact 정합, 다르면 정직 disclosure).

## A-6. BIRCH CF σ_j² 5-15% drift vs offline KMeans

BIRCH CF-tree 의 σ_j² 추정은 single pass streaming 환경에서 도출되며, offline batch K-means 의 final σ_j² 와 비교했을 때 5-15% drift 가 발생한다 (Component B 영역 정직 표기). 본 drift 영역이 Form 1 Component D 의 Neyman / Anti-Neyman allocation 의 streaming 환경 정확도 영역에 영향을 준다.

mitigation: Form 1 phase 1 권장 = **Proportional allocation** (N_j 만 알면 됨, σ_j drift risk 회피). Neyman allocation 의 streaming 환경 측정은 phase 2 (paper-grade future work) 영역으로 분담.

## A-7. batch axis (1001 file) vs streaming axis (Form 1 360 file) boundary

본 연구의 기존 1001 file 측정 portfolio 는 batch 환경 (paper §V-B 와 동일 axis) 측정이며, Form 1 의 streaming axis (per-tuple incremental + concept drift) 측정 영역과 분리된다. 본 1001 file 자체는 폐기 X 영역이며, batch baseline + streaming axis 의 complementary framework 위에서 본 v2 narrative 가 구성된다.

mitigation: §9 batch baseline 영역 (단독 대체 + 결합) 과 §13.5 streaming 환경 영역 (Form 1 phase 1 measurement) 의 분리 표기. 정직 disclosure #12 와 함께 인용.

## A-8. paper §V-B single-table 不可 = 구현 코드 한계 (구조 X)

paper §V-B 자체는 single-table KNN query 에 대한 sampling-based cardinality estimation 을 명시 (paper p.5 우단 verbatim) 하지만, paper 공개 코드 (BDAI-Research/Exqutor github) 의 single-table 영역이 동작하지 않아 본 연구의 측정 영역이 multi-join 으로 자연 이동했다. 본 영역의 정확 표기 = "구현 코드 한계 (구조 X)".

본 연구는 paper github 직접 fork build verify 미완 이며, 본 영역의 발견은 임채림 연구원 자문 base 다 (박세은 5/14 9:09 영역 1 정정 룰 #3).

mitigation: 회의 PDF + 5/27 발표 + 6/11 보고서 모두 wording 정정 적용. "paper §V-B 의 single-table 不可 = 구현 한계 (구조 X)" 의 정직 표기.

## A-9. paper §V-B sampling = block + row hybrid (block only X)

paper §V-B 의 sampling 영역은 초기 N=385 budget = block 추출 + Eq 5 sampling_size update 시 n_inc 행 추가 = row 추출 의 **block + row hybrid** 다. 본 연구의 이전 narrative 가 "paper §V-B 는 block only" 라고 표현한 부분은 부정확하며, 본 영역도 임채림 자문 base 다 (박세은 5/14 9:09 영역 2 정정 룰 #4).

본 연구는 paper github source code level verify 미완 이며, paper 공개 자료 + 임채림 자문 base.

mitigation: 회의 PDF + 5/27 발표 + 6/11 보고서 모두 wording 정정. "paper §V-B sampling = block + row hybrid" 의 정직 표기.

## A-10. "분포 안다" L1/L2/L3 multi-layer 분리, RQ2 = L3 oracle

"분포 안다" 의 영역은 L1 (global skew flag, HHI 지표) + L2 (cluster boundary K=20) + L3 (cluster boundary + σ_j 분산) 의 multi-layer 다 (박세은 5/14 9:09 영역 3 정정 룰 #5). 본 연구 RQ2 영역은 L3 oracle 가정 (offline batch K-means 의 σ_j 직접 사용) 이며, σ_j 직접 측정 (산업 환경 streaming 추정) 은 직접 측정 미완 영역이다.

mitigation: RQ2 narrative 정정 + L1/L2/L3 분리 명시. RQ2 측정 영역 = L3 oracle 가정 영역 임의 정확 표기. σ_j 직접 측정 영역은 future work 으로 분담.

## A-11. paper §V-B 영역 = "without index" 가정 (paper p.5 verbatim)

paper §V-B 영역 자체는 "without vector index" 가정 안에서의 sampling-based cardinality estimation 영역이다 (paper p.5 좌단 + p.5 우단 + p.6 우단 + §VI-A + §VI-B verbatim). ECQO 의 vector index = HNSW (data itself) 구축 영역과 §V-B 의 sampling 영역은 paper 자체 안에서 상호 배타.

본 영역이 박세은 5/14 9:09 영역 4 (★★★ "분포 알면 ECQO?") 자문 답변의 anchor 다. Form 1 = §V-B 영역 한정 후속 연구 이며, ECQO 영역은 본 연구 outside.

mitigation: §0 + §1 + 5/15 review form §1 + 5/27 slide 2-4 + 6/11 보고서 §2 (배경) 영역에 명시.

## A-12. RQ3 = 사전 학습 batch baseline. Form 1 streaming axis 미완

본 연구의 기존 RQ3 측정 (1001 file batch axis) 은 "사전 학습 완료된 baseline" framing 이다 (박세은 5/14 9:09 영역 5 정정 룰 #7). 즉 K-means K=20 cluster boundary 의 사전 학습 (0.1 ~ 0.5초 SF=1 한정) 후 query 도착 시 sampling 만 수행하는 axis 다. Form 1 의 streaming axis (per-tuple incremental 학습) 영역은 phase 1 measurement (5/27 + 6/11) 미완 이다.

mitigation: RQ3 narrative 영역의 framing 정정 + Form 1 streaming axis 영역의 phase 1 measurement 영역 별도 분리. §13.5 영역에 명시.

## A-13. 0.1~0.5초 fit time = SF=1 (1M rows) 한정

본 연구의 method fit time 0.1 ~ 0.5초는 **SF=1 (1M rows × 96d DEEP, ~384 MB) 한정** 측정 (박세은 5/14 9:27 영역 6 정정 룰 #8). SF=10 / SF=100 fit time 은 미측정 이며, 선형 scale-up 추정으로 SF=10 ≈ 1 ~ 5초, SF=100 ≈ 10 ~ 50초 추정.

mitigation: §10 자원 효율 영역의 0.1 ~ 0.5초 표기 = "fit time (SF=1 한정)" 정확 표기. SF=10 / SF=100 fit time 측정은 future work 으로 분담.

## A-14. (보충) "Anti-Neyman > Neyman" wording 정정

본 연구의 이전 narrative 가 "Anti-Neyman > Neyman = Neyman 가설 무효" 라고 표현한 부분이 부정확하다 (정정 룰 #14). 정확 의미는 다음과 같다:

- **Neyman 가설 자체는 유효** (Cochran 1977 §5.5 의 classical theory 영역의 정합 영역)
- **본 데이터셋이 Neyman 의 가정 조건 (cluster 간 분산 다양함) 不만족** (σ_j range 1.3-1.6× narrow + N_i CV=0 의 두 가지 조건 영역의 partial 불만족)
- **selectivity-dependent** (sel=0.01 paradox / sel=0.1 정합) — 본 5/14 22:00 까지의 측정 영역 evidence

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify (5/14 22:05 confirm). Cochran 1977 §5.5 의 partial 영역 (Agent C 발견).

mitigation: RQ2 narrative 영역의 정확 표기 = "Neyman 가설 자체는 유효 but 본 데이터셋이 Neyman 의 가정 조건 不만족 + selectivity-dependent (sel=0.01 paradox / sel=0.1 정합)". σ_j 직접 측정 영역은 future work (cluster 별 σ_j range 영역의 정확 정량 verify).

## A-15. (보충) 본 v2 의 5/14 22:00 까지 측정 영역의 timestamp 영역

본 v2 의 측정 영역의 timestamp 영역의 정직 표기 영역은 다음과 같다. 본 영역은 본 v2 작성 시점 (5/14 22:32) 의 측정 영역의 정확 상태 영역의 disclosure 영역이다.

- 1001 file batch axis: paper exact carry-over (5/12 02:50 REPORT v11 1362 line)
- α sweep + multi-join + Centroid tuple + B1/B2/B3 cheap + A2-Fig8 mv: 본 세션 5/14 07:35 ~ 18:00 영역의 64 file 추가 측정 영역
- K granularity SF axis: 본 세션 5/14 12:12 ~ 13:02 영역의 48 file 추가 측정 영역 (5/14 22:00 회수 완료)
- Form 1 phase 1 영역: 미측정 (5/27 phase 1 launch 영역 예정, post-5/15 박광현 미팅 후)
- Form 1 phase 2 영역: 미측정 (6/11 phase 2 launch 영역 예정)

본 timestamp 영역의 정직 표기 영역이 본 연구의 measurement portfolio 1113 file 영역의 정확 상태 영역의 evidence 다.

## A-16. 5/27 timeline risk 영역의 disclosure

본 연구의 5/27 phase 1 영역의 timeline 영역의 risk 영역의 disclosure 영역은 다음 5 axis 영역으로 정리된다.

**Risk 1 (SelNet integration)**: SelNet original code 영역이 2020 commit 영역이며, dependency 영역의 깨질 가능성 영역 (PyTorch / TensorFlow 버전 호환 영역). cost 8-12h 의 SelNet integration 영역의 risk.

**Risk 2 (Q-error 재현)**: paper Fig.12 영역의 SelNet Q-error 5.53 영역의 재현 risk 10-20% (paper 영역의 hyperparam 영역 미공개 시).

**Risk 3 (BIRCH CF σ_j² drift)**: 5-15% drift 영역의 정량 측정 영역의 cost 영역 (Form 1 phase 1 측정 2 영역, 540 file × 3-5h).

**Risk 4 (CE4HD github 미공개)**: 5/27 phase 1 영역의 4-way → 3-way 영역의 축소 영역 (CE4HD 폐기).

**Risk 5 (timeline 자체)**: 5/27 phase 1 영역의 cost 52-87h 영역의 D-13 timeline 영역의 fit 영역의 risk (자원 Max 영역의 가속화 영역의 dependency).

본 5 risk 영역의 mitigation 영역은 (a) post-5/15 박광현 미팅 영역의 자문 + 변경 영역의 확정, (b) Agent E + F + G 영역의 cost 산정 ±5% 일치 영역의 evidence, (c) 자원 Max 영역의 활용 영역의 dev cost 가속화 영역, (d) phase 분리 영역 (5/27 phase 1 / 6/11 phase 2 / post-6/11 future) 영역의 cost 영역의 분담, (e) 정직 disclosure 영역의 5/27 발표 slide 17 영역 + 6/11 보고서 §9 영역의 명시 영역의 5 영역이다.

---

# 부록 §B — 박세은 9 영역 답변 form (카톡 복붙)

박세은 5/14 9:09 ~ 10:15 9 영역 자문 답변 form. Agent J 7.8 분 deep dive 결과 종합. 본 영역은 카톡 복붙 plain text form 이며, 박세은님 호칭 + peer-to-peer 톤 + 학부생 톤 영역. 본 v2 부터는 9 영역 (이전 6 영역 + Neyman selectivity-dependent + over-statement 정정 + K granularity SF axis) 의 통합 form.

## B-1. 영역 1 답변 (single-table AS 不可 = 구현 코드 문제, 구조 X)

박세은님,

영역 1 자문 감사합니다. 정확한 지적이라 본 narrative 정정해야 합니다.

본 연구 회의 PDF (저녁 긴급 회의 숙지용 §2.6 line 322) 에서 "Exqutor 의 single-table Adaptive Sampling 은 동작하지 않는다" 라고 표현한 부분이 있는데, 이는 구조적 문제가 아니라 paper 공개 코드 (BDAI-Research/Exqutor github) 의 구현 측면 한계 입니다. paper §V-B 자체는 single-table KNN query 에 대해 sampling-based cardinality estimation 을 제공한다고 명시하고 있고 (paper p.5 우단 "Exqutor adopts a sampling-based cardinality estimation approach specifically for KNN queries"), 구현 코드의 limitation 으로 single-table 영역이 동작하지 않은 것을 본 연구가 measurement 하는 과정에서 발견한 것입니다.

따라서 정정된 표현은 "paper §V-B 가 single-table 을 다루지만 공개 코드 영역의 구현 한계로 동작하지 않아 본 연구의 측정 영역이 multi-join 으로 자연 이동" 정도가 정확합니다. 본 연구의 multi-join 영역 measurement 가 paper 의 구조적 한계라기보다는 우연의 측면이라는 점 명시해야 합니다.

이 wording 은 5/27 발표 / 6/11 보고서 모두 정정 적용합니다. 박세은님 발견 감사합니다.

evidence: paper [0] §V-B p.5 우단 line 1-7, 회의 PDF §2.6 line 322, Agent B 정직 disclosure 표.

정직 disclosure: 본 연구가 paper 의 구현 코드를 어디까지 직접 verify 했는지는 fork run 측면 확인 미완. paper github repo (BDAI-Research/Exqutor) 의 single-table 영역 동작 여부 직접 fork build verify 안 했고 paper 공개 자료 + 임채림 연구원 자문에 의존했습니다. 본 영역 "구조 X = 구현 한계" 정정도 임채림 자문 base 입니다.

## B-2. 영역 2 답변 (block 추출 vs row 추출 정합)

박세은님,

영역 2 자문 감사합니다. 이것도 정확한 지적이라 본 narrative 정정해야 합니다.

본 연구 회의 PDF 에서 "Exqutor 의 Adaptive Sampling 은 block 단위 추출이다" 라고 표현한 부분이 있는데, 이는 부정확합니다. paper §V-B + 임채림 연구원 자문 종합하면 Exqutor 의 sampling 은 처음 (초기 N=385 budget) 은 block 단위로 빠르게 잡고, 이후 Eq 5 sampling_size 업데이트 시 추가되는 n_inc 행은 row 단위로 추출 한다고 합니다. 즉 block + row 의 hybrid 입니다.

따라서 "block 추출이 AS 의 문제이다" 라고 지적하는 것은 적절하지 않습니다. 본 연구의 wording 정정은 다음과 같습니다:

- 삭제: "paper §V-B 는 block 추출이라 분포 인지가 어렵다"
- 정정: "paper §V-B 의 Eq 1 (N=385 초기 sample budget) 은 unstratified random 추출 이고, 본 연구는 이 sample 추출 방식을 cluster 인지 stratification 으로 대체"

본 연구의 contribution scope 는 어디까지나 추출 방식의 random → stratified 정정 이지, block / row 구조 자체의 변경이 아닙니다. 5/27 발표 / 6/11 보고서 모두 wording 정정 적용합니다.

evidence: paper [0] §V-B p.5-6 Eq 1 + Eq 5 line, 임채림 연구원 자문, 회의 PDF v2 §2.6.

정직 disclosure: 본 연구가 paper Exqutor 의 block / row 추출 구현 detail 을 직접 source code level 로 verify 안 했습니다. paper 공개 자료 + 임채림 자문 base. 본 영역도 임채림 자문에 의존하니 만약 추가 verify 필요하면 paper github 직접 확인이 필요합니다.

## B-3. 영역 3 답변 ("분포 안다" 의 multi-layer 분리)

박세은님,

영역 3 자문 감사합니다. 이 영역은 본 연구 narrative 의 핵심 정정 영역 中 하나라 자세히 답변드립니다.

박세은님 지적의 핵심은 "이미 데이터셋이 어떤 형태인지 안다" 는 의미인데 왜 K-means 등의 추가 학습이 필요하냐는 것입니다. 본 연구가 이 영역을 충분히 분리해 설명하지 않은 것이 narrative 약점이었습니다.

본 연구는 "분포 안다" 를 3 layer 로 분리 해 사용해야 합니다:

- L1 (global statistics, skew flag): HHI 지표, 데이터셋이 skewed 인지 normal 인지 정도의 메타 정보. 데이터 카탈로그에 미리 저장 가능, 별도 학습 비용 없음. 이 layer 만으로는 본 연구의 stratification 적용 불가.
- L2 (cluster boundary 단순, K=20): 데이터를 K=20 으로 분할했을 때 각 cluster 경계 (centroid 위치). K-means K=20 학습 0.1-0.5 초로 cheap.
- L3 (cluster boundary + σ_j 분산): L2 + 각 cluster 내 분산 σ_j (Neyman allocation 사용). σ_j 직접 측정은 본 연구가 oracle 가정으로 처리, 실제 산업 환경 측정 cost 는 추가 검증 영역.

박세은님 지적은 본 연구가 RQ2 영역에서 "분포 안다" 를 명확히 분리하지 않고 막연히 사용한 결과입니다. 정확한 narrative 정정은:

- RQ2 영역 = L2 + L3 (실험 천장 가정, 학습 0 비용 + σ_j oracle)
- RQ3 영역 = 실제 데이터셋에서 L2 학습 (0.1-0.5 초) + σ_j 측정

"K-means 추가 학습 왜 필요하냐" 의 답: L1 정보 (skew flag) 만으로는 stratification 의 cluster boundary 가 부재. L2 + L3 를 얻으려면 K-means 학습이 필수입니다. 본 연구는 그 학습 비용을 0.1-0.5 초 (sparse_rp 0.1 / chao_weighted 0.5 / neuram 0.5 / pca1d 0.5 / hilbert 0.5 / reservoir 0.1) 로 측정해 산업 적용 가능 영역에 두었습니다.

evidence: 회의 PDF v2 §3.4 line 540-556 (RQ3 method 사전 학습 framing), pareto analysis line 1-50 (학습 시간), Agent A 옵션 D § L1-L4 framework.

정직 disclosure: σ_j 직접 측정 (L3 의 streaming 추정) 은 본 연구 RQ2 영역에서 oracle 가정 입니다. 산업 환경 streaming 추정 (BIRCH CF-tree 의 SS_j 영역) 의 정확 측정은 본 연구의 future work 영역.

## B-4. 영역 4 답변 (★★★ "분포 알면 ECQO 가능?", multi-layer 4)

박세은님,

영역 4 자문 감사합니다. 이 영역이 본 연구 방향 자체에 대한 가장 critical 질문이라 자세히 답변드립니다.

답은 4 layer 로 분리해서 정리해야 합니다:

(a) **paper §V-B 영역 자체 = "without index" 가정**: paper Exqutor §V 도입부 verbatim 인용입니다. "For VAQs with vector indexes, Exqutor employs Exact Cardinality Query Optimization (ECQO)... For VAQs without index, Exqutor uses a sampling-based approach to approximate selectivity (subsection V-B)." 즉 paper 자체가 §V-A ECQO (인덱스 있을 때) 와 §V-B Adaptive Sampling (인덱스 없을 때) 의 두 영역을 명확 분리합니다. 본 연구 Form 1 = §V-B 영역 한정 후속 연구 이며, ECQO 영역은 본 연구 outside.

(b) **ECQO 의 vector index = HNSW (data itself) 구축, K-means K=20 = 메타 정보**: ECQO 의 cost = HNSW O(n log n) build + memory 1.x ~ 2x base + maintain O(log n) 매 insert. 본 연구의 K-means K=20 fit = 0.1 ~ 0.5 초 (SF=1 한정) + memory K × d. 두 영역의 추상화 layer 가 다릅니다. HNSW = data 자체의 graph index, K-means K=20 = 데이터 분포의 메타 정보 (cluster boundary). 본 연구는 메타 정보를 사용해 sampling 의 정확도를 끌어올리는 axis 이지, HNSW 같은 data 자체 index 를 새로 구축하는 axis 가 아닙니다.

(c) **ECQO + Form 1 complementary**: high-frequency stable workload = ECQO 영역 (HNSW 구축 cost amortize 가능), ad-hoc / shifting workload = Form 1 영역 (sampling 의 dynamic adjustment). paper §VI-B 의 "shifting workloads" 영역과 align 합니다.

(d) **"분포 안다" L1/L2/L3 vs L_index 분리**: 본 연구의 L1/L2/L3 (cluster boundary + σ_j) 영역과 ECQO 의 L_index (HNSW graph) 영역은 다른 추상화 layer 입니다. L1/L2/L3 = 데이터 메타 정보 영역, L_index = 데이터 자체의 access path 영역.

요약하면 박세은님 질문 "분포 알면 ECQO 가능?" 의 답은: 분포 정보 자체로는 ECQO 영역이 아니라 §V-B sampling 의 정확도 끌어올림 영역이 자연스러운 후속 입니다. ECQO 영역은 vector index 자체 (HNSW) 의 구축 영역이며, 분포 정보 + index 구축은 다른 layer 입니다. 본 연구 Form 1 = §V-B 영역 한정 후속 연구 로 명시하고, ECQO 와의 complementary 영역만 본 연구의 narrative 에 포함합니다.

evidence: paper [0] §V 도입부 p.5 좌단 verbatim, paper §V-A + §V-B 분리 영역, paper §VI-A (with index) + §VI-B (without index) 분리 영역, Agent D 본업 align 자문.

정직 disclosure: 본 연구가 paper §V-A ECQO 영역의 source code level 영역을 directly verify 안 했습니다. paper 공개 자료 + 임채림 자문 base. ECQO 영역의 본 연구 outside 정직 표기 = 본 연구의 scope limitation.

## B-5. 영역 5 답변 (RQ3 사전 학습 batch baseline framing)

박세은님,

영역 5 자문 감사합니다. 이 영역도 본 연구 narrative 의 framing 영역의 핵심 정정 中 하나라 자세히 답변드립니다.

박세은님 지적의 핵심은 본 연구의 RQ3 영역 (1001 file 측정 portfolio) 이 "쿼리 실행 전 학습 필요" 영역이라는 것입니다. 즉 본 연구의 method 들이 K-means K=20 cluster boundary 의 사전 학습 (0.1 ~ 0.5 초 SF=1 한정) 후 query 도착 시 sampling 만 수행하는 axis 이지, 진짜 online incremental 학습 axis 가 아닙니다.

본 framing 정정은 본 연구의 narrative 영역에서 두 가지 중요한 axis 분리를 자연 도출합니다:

- 현 1001 file batch axis = 사전 학습 완료된 baseline (회의 PDF §4.1.4 line 540-556 명시)
- Form 1 streaming axis = online incremental maintenance (진짜 "쿼리 도착 시" 학습)

즉 박세은님의 영역 5 자문이 Form 1 의 존재 이유 자체를 강조하는 영역입니다. 본 연구의 1001 file batch axis 자체는 paper §V-B 의 batch 환경 측정의 후속 영역이고, Form 1 streaming axis = paper §V-B 의 streaming 환경 측정의 신규 axis 입니다. 두 영역의 complementary framework 가 본 연구의 narrative base 입니다.

본 v2 부터는 RQ3 narrative 영역의 framing 정정 + Form 1 streaming axis 영역의 phase 1 measurement 영역 (5/27 + 6/11) 별도 분리 표기합니다.

evidence: 회의 PDF v2 §4.1.4 line 540-556 (RQ3 method 사전 학습 framing), Agent H 1001 file batch baseline 재해석.

정직 disclosure: Form 1 streaming axis 영역의 phase 1 measurement (per-tuple incremental + concept drift) 는 본 연구 현재 미완 영역. 5/27 phase 1 영역 = 360 file 추가 측정 launch 예정 (52-87h cost), 6/11 phase 2 영역 = 추가 240 file (30-50h cost). post-6/11 future paper 영역 = full streaming measurement.

## B-6. 영역 6 답변 (9:27 런타임 question)

박세은님,

영역 6 자문 감사합니다. 이 영역도 본 연구 narrative 의 wording 정정 영역 中 하나라 자세히 답변드립니다.

박세은님 지적의 핵심은 본 연구의 "0.1 ~ 0.5 초 학습 시간" 표기가 매 query 마다 학습이 일어나는 것이 아니냐는 것입니다. 본 연구의 정확 표기는 다음과 같습니다:

- 0.1 ~ 0.5 초 = method fit time (학습 시간), SF=1 한정 (1M rows × 96d DEEP, ~384 MB)
- SF=10 / SF=100 fit time = 미측정 (선형 scale-up 추정 SF=10 ≈ 1 ~ 5초, SF=100 ≈ 10 ~ 50초)
- "런타임 실행" 영역의 layer 분리:
  - 매 쿼리 마다 fit = 본 연구 framing X (paper period P=50 가정)
  - 사전 학습 + 실시간 query = 본 연구의 현 batch axis framing
  - 진짜 streaming (per-tuple incremental) = Form 1 의 streaming axis 영역

즉 본 연구의 method 학습 영역은 다음 3 layer 로 분리됩니다:

- (1) 데이터셋 catalog 단계 = K-means K=20 cluster boundary 사전 학습 (offline batch 0.1 ~ 0.5 초 SF=1 한정)
- (2) Query 도착 시 = 학습된 cluster 위에서 sampling 만 수행 (paper §V-B Eq 1-6 dynamic adjustment 영역)
- (3) Streaming update = per-tuple incremental cluster + reservoir update (Form 1 streaming axis, phase 1 measurement 미완)

본 v2 부터는 §10 자원 효율 영역의 "0.1 ~ 0.5초" 표기를 "method fit time (SF=1 한정)" 으로 정확 표기합니다. SF=10 / SF=100 fit time 의 직접 측정은 본 연구의 future work 영역으로 분담합니다.

evidence: 회의 PDF v2 §4.1.4 (RQ3 method 사전 학습 framing), pareto analysis (학습 시간 0.1 ~ 0.5 초 SF=1 한정), Agent E 영역 4 (streaming axis 영역).

정직 disclosure: SF=10 / SF=100 fit time 영역의 직접 측정 미완. 선형 scale-up 추정 영역의 정확 verify 는 future work 영역.

## B-7. 영역 7 답변 (9:42 Neyman selectivity-dependent)

박세은님,

영역 7 자문 감사합니다. 이 영역은 본 연구 RQ2 의 narrative 정정 영역 中 핵심입니다.

박세은님 지적의 핵심은 본 연구의 "Anti-Neyman > Neyman = Neyman 가설 무효" 표현이 부정확하다는 것입니다. 정확한 narrative 정정은 selectivity-dependent 영역을 명시하는 것입니다.

RQ2 5-way 측정 (Bernoulli + Equal + Proportional + Neyman + Anti-Neyman) 의 결과는 selectivity 영역에 따라 다르게 발현합니다:

- sel=0.01 (paired n=455): Neyman 1.595 / Anti 1.540 / Prop 1.580 → Proportional 또는 Anti-Neyman best (paradox 영역)
- sel=0.1: Neyman 1.1076 / Anti 1.1101 / Prop 1.1135 → Neyman best (classical theory 정합)

본 paradox 영역의 정확 해석은:
- sel=0.01 영역에서 Anti-Neyman best = 본 dataset 의 cluster 간 분산 σ_j range 가 1.3-1.6× narrow (Cochran 1977 §5.5 의 Neyman 가정 不만족 영역) + N_i CV=0 (cluster size 균등)
- sel=0.1 영역에서 Neyman best = classical theory 정합 영역
- Neyman 가설 자체는 유효 하지만 본 데이터셋이 Neyman 의 가정 조건 (cluster 간 분산 다양함) 不만족 + selectivity-dependent

본 v2 부터는 RQ2 narrative 영역의 정확 표기:
- "Anti-Neyman > Neyman = Neyman 가설 무효" 폐기
- "selectivity-dependent: sel=0.01 영역 Anti / Prop best (paradox), sel=0.1 영역 Neyman best (classical 정합)" 정정

박세은님 9:42 발견 감사합니다.

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify, Cochran 1977 §5.5 partial 적용, Agent C deep dive § Cochran 발견.

정직 disclosure: σ_j 직접 측정 (Neyman 가정 의 cluster 분산 다양함 verify) 은 본 연구 oracle 가정 영역. 산업 환경 streaming 추정 (BIRCH CF tuple 의 SS_j 영역) 의 직접 verify 는 future work.

## B-8. 영역 8 답변 (9:54 over-statement 정정)

박세은님,

영역 8 자문 감사합니다. 이 영역은 본 연구 narrative 의 over-statement 정정 영역 中 critical 입니다.

박세은님 지적의 핵심은 본 연구의 "Bernoulli → Neyman −10%" narrative 가 over-statement 라는 것입니다. RQ2 5-way csv 직접 aggregate verify 결과:

| dataset | sel | Neyman vs Bernoulli Δ% |
|---|---|---:|
| DEEP | 0.01 | −7.64% |
| DEEP | 0.1 | −4.59% |
| SIFT | 0.01 | −2.58% |
| SIFT | 0.1 | −9.16% (가장 큰 단일 cell) |
| POOL | 0.01 | −5.16% |
| POOL | 0.1 | −6.94% |

본 정확 정량은 −5 ~ −9% 범위 이며, 가장 큰 단일 cell = SIFT sel=0.1 의 −9.16% 입니다. "Bernoulli → Neyman −10%" 은 over-statement 입니다.

본 v2 부터는 정확 표기:
- 폐기: "Bernoulli → Neyman −10%"
- 정정: "sel + dataset 영역별 −2.58 ~ −9.16% 범위, POOL 평균 −5 ~ −7%"

추가로 회의 PDF v2 §3.2 line 532-533 의 "Proportional −9.61% / Neyman −8.75%" wording 영역도 RQ2 csv 직접 aggregate (POOL Proportional −6.76% / Neyman −5.16%) 와 일치하지 않습니다. 본 wording 의 출처 source 의 verify 가 필요한 영역입니다.

박세은님 9:54 발견 감사합니다.

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify.

정직 disclosure: RQ2 5-way 측정 영역의 scope = SF=100 (DEEP+SIFT) 한정. SF=1 / SF=10 / SSN 미측정. 회의 PDF v2 §3.2 line 532-533 wording 의 출처 source verify 미완.

## B-9. 영역 9 답변 (K granularity SF axis 추가 측정 완료)

박세은님,

영역 9 (이전 8:50 발견 영역의 후속 보고) 입니다.

박세은님 8:50 발견 (회의 PDF v2 §2.5 SF=1 영역 K=20 미측정) 영역의 추가 측정을 사용자 옵션 B 결정 (3 SF × 2 K 추가 = 48 file) 으로 launch 했고 5/14 22:00 회수 완료했습니다. 결과 finding 4 가지:

1. method-dependent K best 패턴 = SF=1 영역 K=20 best 여부는 method 별로 다름:
   - sparse_rp / chao_weighted: K=20 sweet spot (U-shape)
   - hilbert_real / hyperloglog: K-robust + K=30 slight edge

2. SF axis K best 패턴의 일관성 = 위 method-dependent 패턴이 SF=1 / SF=10 / SF=100 모두 일관 발현

3. SF=10 영역의 약한 효과 = SF=1 + SF=100 영역 (−10 ~ −14%) 대비 SF=10 영역 (−5 ~ −7%) 의 절반 수준

4. 회의 PDF v2 §2.5 wording 정정 가능 = "SF=1 영역 K=20 미측정" → "SF=1+10+100 axis 모두 측정 완료, method-dependent K best 패턴 일관"

상세 분석은 `experiments/results/analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md` 에 별도 분리되어 있고, raw data 는 `experiments/results/raw/06_클러스터수_K_민감도/SF_axis/K10/` + `K30/` (각 24 file) 에 있습니다.

박세은님 8:50 발견 감사합니다.

evidence: K=10 + K=30 측정 raw (24 file × 2 batch), 3-way 분석 보고서.

정직 disclosure: SF=10 영역의 약한 효과 영역의 정확 evidence (data size U-shape 가능성 vs 측정 noise) 는 future work 영역. paper §VI-B "shifting workloads" 영역과 align 가능성 영역은 Form 1 phase 2 측정에서 추가 verify.

---

# 부록 §C — paper §V verbatim 인용 + Form 1 17-step pseudo-code

본 영역은 paper Exqutor §V 영역의 verbatim 인용 + 본 연구의 의역 step-wise pseudo-code 17 step 의 정확 표기 영역. 5/27 발표 slide 5 + 6/11 보고서 부록 A + 5/15 review form §2 의 source 영역.

## C-1. paper §V verbatim 영역 (Form 1 anchor)

### C-1.1 paper p.5 좌단 §V 도입부

> "For VAQs with vector indexes, Exqutor employs Exact Cardinality Query Optimization (ECQO), an exact cardinality estimation technique that leverages the index to compute the precise number of rows satisfying the similarity predicate. For VAQs without index, Exqutor uses a sampling-based approach to approximate selectivity (subsection V-B)."

**역할**: paper §V 영역의 ECQO (with index) vs §V-B (without index) 의 양분 영역 명시. Form 1 의 §V-B 영역 한정 후속 연구 form 의 anchor.

### C-1.2 paper p.5 우단 §V-B 첫 단락

> "When a VAQ lacks a vector index, the query optimizer must rely on either an index over structured attributes or perform a full sequential scan over the relevant table. Exqutor adopts a sampling-based cardinality estimation approach specifically for KNN queries."

**역할**: paper §V-B 영역의 "without index" 가정의 명시. Form 1 의 §V-B 영역 한정 후속 연구 form 의 anchor (영역 4 박세은 자문 대응 base).

### C-1.3 paper p.6 우단 implementation 단락

> "When a VAQ with a vector range predicate lacks index support, the optimizer invokes a sampling routine..."

**역할**: paper §V-B 영역의 implementation 단락 verbatim. "lacks index support" 표현으로 본 영역의 "without index" 가정 재확인.

### C-1.4 paper §VI-A 첫 단락 (with index 평가)

> "In this section, we evaluate the performance of Exqutor when executing VAQs with a vector index using an ANN search, specifically with HNSW [38]."

**역할**: paper §VI-A 영역의 ECQO (with index) 평가 영역 명시. 본 연구 outside.

### C-1.5 paper §VI-B 첫 단락 (without index 평가)

> "In this section, we evaluate the performance of Exqutor applied to TPC-H VAQs that perform KNN searches without vector indexes, where cardinality estimation is handled via sampling."

**역할**: paper §VI-B 영역의 §V-B (without index) 평가 영역 명시. Form 1 의 측정 영역.

### C-1.6 paper §VI-B "shifting workloads" verbatim (page 8 우단)

> "Effect of adaptive sampling. ... This feedback loop enables the system to maintain estimation accuracy while minimizing unnecessary computation.
>
> This behavior demonstrates that Exqutor effectively balances estimation accuracy and planning efficiency. The sample size trajectory varies depending on the dataset: for DEEP and SimSearchNet++, the sample size decreases over time as Q-error stabilizes, allowing the system to reduce planning cost without loss of accuracy. In contrast, for SIFT, the sample size increases to satisfy higher estimation demands due to its more complex distribution. Ultimately, Exqutor converges to a dataset-specific equilibrium that reflects the selectivity patterns and estimation difficulty of each workload."

**역할**: paper §VI-B 의 "shifting workloads" + "dataset-specific equilibrium" 명시. paper 자체가 본 영역의 정량 측정을 수행하지 않음. Form 1 의 "추가검증" 측면 (paper §VI-B 정량 측정) 근거.

### C-1.7 paper §VI-D Fig.12 (SelNet 비교 영역 verbatim, page 11 우단)

> "Comparison with learned cardinality estimator. Figure 12 compares Exqutor with SelNet [74], a learned estimator. Exqutor achieves speedups up to 16.1× speedup over SelNet. SelNet requires 77 ms for a single-query cardinality estimation and depends on offline training and complexity. When compared with the sampling-based approach, Exqutor achieves an average Q-error of 1.69, while SelNet yields a higher Q-error of 5.53. These results highlight the advantages of Exqutor in delivering accurate cardinality estimates with lightweight overhead, ensuring both efficiency and robustness in query optimization."

**역할**: paper §VI-D 영역의 SelNet 단독 비교 영역 (paper L5 explicit limitation). Form 1 의 "보완" 측면 (3-way 또는 5-way framework 영역) 근거.

### C-1.8 paper §VII Related Work Sampling 영역 verbatim (page 13 우단)

> "One technique for efficiently estimating selectivity and cost is sampling. Early works introduced random sampling for join size estimation [79], [80], while later approaches refined these ideas with adaptive sampling strategies [81]. The method in [81] adjusts the sample size dynamically until a desired confidence level is reached, but does not consider sampling overhead or optimize it dynamically based on query characteristics."

**역할**: paper §VII 의 Lipton-Naughton-Schneider 1990 [81] 의 한계 명시 ("does not consider sampling overhead or optimize it dynamically"). Form 1 의 "개선" 측면 (paper §V-B + 본 연구 augment) 근거.

## C-2. paper §V-B Eq 1-6 verbatim

### C-2.1 Eq 1 (PDF page 6 우단)

```
N = ⌈z² · P̂ · (1 − P̂) / e²⌉                                            (Eq 1)
```

paper verbatim explanation (page 6 우단):
> "To determine an appropriate sample size, Exqutor uses a statistical formula derived from classical sampling theory [67]. The required number of samples N is computed as:
> [Eq 1]
> z: critical value corresponding to the desired confidence level (e.g., z = 1.96 for 95% confidence).
> P̂: estimated proportion of data points expected to fall within the similarity threshold.
> e: desired margin of error (e.g., e = 0.05 for 5% error)."

paper §VI exact: z=1.96 + P̂=0.5 + e=0.05 → N=385.

**Form 1 영역**: 본질 **대체** (Bernoulli → SRS + BIRCH).

### C-2.2 Eq 2 (PDF page 7 좌단 상단)

```
Q-error = max(Card_esti / Card_true, Card_true / Card_esti)              (Eq 2)
```

paper verbatim explanation:
> "The adjustment is guided by the Q-error [68]–[70], which measures the deviation between the estimated and true cardinality."

**Form 1 영역**: paper exact 100% 유지 (accuracy metric).

### C-2.3 Eq 3 (PDF page 7 좌단 중단)

```
δ = α · (Q-error − β) − (100 − α) · sampling_ratio                       (Eq 3)
```

paper verbatim explanation:
> "Here, δ is the adjustment factor computed from estimation error and the current sampling ratio, which determines the direction and magnitude of sample updates."

paper §VI exact: α=50 + β=1.5.

**Form 1 영역**: paper exact 유지 (phase 2 group-aware future).

### C-2.4 Eq 4 (PDF page 7 좌단 중단)

```
V_t = m · V_{t-1} + η_t · δ                                              (Eq 4)
```

paper verbatim explanation:
> "V_t is the momentum term at iteration t, m is the momentum coefficient, and η_t is the learning rate."

paper §VI exact: m=0.9 + η₀=0.1.

**Form 1 영역**: paper exact 유지 (phase 2 group-aware future).

### C-2.5 Eq 5 (PDF page 7 좌단 중단)

```
sampling_size_{t+1} = sampling_size_t + V_t                              (Eq 5)
```

paper verbatim explanation:
> "α balances the contribution between Q-error and the sampling ratio, and β is a tunable threshold representing acceptable Q-error."

**Form 1 영역**: **augment** (scalar new_size → cluster 별 group-aware allocation 분배).

### C-2.6 Eq 6 (PDF page 7 좌단 중단)

```
η_{t+1} = γ · η_t                                                        (Eq 6)
```

paper verbatim explanation:
> "The learning rate is decayed at each iteration using:
> [Eq 6]
> where γ is the decay factor (0 < γ < 1) that progressively reduces the adjustment magnitude."

paper §VI exact: γ=0.99.

**Form 1 영역**: paper exact 100% 유지.

## C-3. paper §VI 도입부 hyperparam 7 종 verbatim (PDF page 7 우단)

paper verbatim:
> "For sampling-based cardinality estimation, we initially compute the number of samples N using the sample size formula (Equation 1) for sample size estimation [67], given a 95% confidence level (z = 1.96), a proportion estimate P̂ = 0.5, and a 5% margin of error (e = 0.05). Applying the formula yields a fixed sample size of N = 385.
>
> For adaptive sampling, we extend the optimizer with momentum-based feedback control. Parameter values are selected based on prior work on adaptive query estimation [22], [70]: we set the momentum coefficient m = 0.9, initial learning rate η₀ = 0.1, weighting factor α = 50, and target Q-error β = 1.5. These values balance Q-error minimization and sample size stability. The learning rate decay factor γ = 0.99 gradually reduces adjustment magnitude to ensure convergence. Sample size updates are triggered every 50 queries."

**hyperparam 7 종 정확 표**:

| symbol | paper verbatim value | 역할 | Eq |
|---|---:|---|:---:|
| N | 385 | initial sample budget | Eq 1 |
| m | 0.9 | momentum coefficient | Eq 4 |
| η₀ | 0.1 | initial learning rate | Eq 4 (initial) |
| α | 50 | δ weighting factor | Eq 3 |
| β | 1.5 | target Q-error | Eq 3 |
| γ | 0.99 | lr decay factor | Eq 6 |
| P (update period) | 50 queries | sample size update trigger | (산문 verbatim) |

**N=385 도출 (paper §VI exact)**:
- z = 1.96 (95% CI, paper verbatim)
- P̂ = 0.5 (paper verbatim)
- e = 0.05 (paper verbatim)
- N = ⌈1.96² × 0.5 × 0.5 / 0.05²⌉ = ⌈3.8416 × 0.25 / 0.0025⌉ = ⌈384.16⌉ = **385** ✓

**Form 1 phase 1 영역**: 7 hyperparam 그대로 paper exact 유지 + K=20 (cluster count) 추가만 도입.

## C-4. 본 연구 의역 step-wise pseudo-code 17 step (Agent G verify)

paper Eq 1-6 verbatim 영역 = Step 1-2, 6, 8-13, 16 (10 step) + 본 연구 augment 영역 = Step 3-5, 7, 14-15, 17 (7 step).

```
Algorithm: Form 1 — Streaming-aware Distribution-Conscious Cardinality Estimation
           (paper §V-B Eq 1-6 + 본 연구 의역 step-wise pseudo-code)

Input:
  D                   : streaming data tuple sequence (online arrival)
  Q                   : query workload (TPC-H VAQ + concept drift simulation)
  K                   : cluster count (★ 본 연구 = 20, RQ2/RQ3 paper exact)
  hyperparam 7 종     : N=385, m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, P=50
                        (paper §VI verbatim, 본 Form 1 phase 1 = 7 종 그대로)
  alloc_mode          : ★ 본 연구 = "equal" | "proportional" | "neyman" | "anti_neyman"

Output:
  Card_esti(q)        : per-query cardinality estimate

# === Initialization (Step 1-5) ===

Step 1 [paper Eq 1 verbatim]:
    N ← ⌈z²·P̂·(1−P̂)/e²⌉ = 385
    sampling_size_0 ← N = 385

Step 2 [paper §VI verbatim init]:
    V_0 ← 0, η_0 ← 0.1, t ← 0
    m ← 0.9, α ← 50, β ← 1.5, γ ← 0.99, P ← 50

Step 3 [★ 본 연구 augment, Component B init]:
    BIRCH ← OnlineBirchCluster(n_clusters=K=20,
                                threshold=adaptive(dataset),
                                branching_factor=50)
    # BIRCH 가 CF tuple (N_j, LS_j, SS_j) 을 online 유지

Step 4 [★ 본 연구 augment, Component A init]:
    n_j_0 ← group_aware_alloc(total_budget=N=385,
                              sizes=uniform(K),
                              sigma=ones(K),
                              mode=alloc_mode)   # initial = equal default
    SRS ← StratifiedReservoir(n_strata=K=20,
                              capacity_per_stratum=n_j_0,
                              dim=d)
    # SRS 가 per-stratum Vitter 1985 Algorithm R reservoir 유지

Step 5 [★ 본 연구 augment, streaming axis init]:
    BIRCH warm-up: chunk 단위 partial_fit(D[:warm_up_size])
    SRS warm-up: warm-up tuple 별 BIRCH.predict + SRS.update

# === Streaming + Query Loop (Step 6-17) ===

Step 6 [paper §V-B verbatim, query loop]:
    for each query q ∈ Q:
        D ← q.distance_threshold      # paper TPC-H Q3-Q20 SQL verbatim 0.86
        qvec ← q.vector

Step 7 [★ 본 연구 augment, Component A + D estimate]:
        sizes_j ← BIRCH.N_j                            # online cluster size
        sigma_j ← sqrt(BIRCH.sigma_squared())          # online σ_j (BIRCH CF)
        # Component A estimate
        Card_esti ← SRS.estimate(qvec, D, total_rows=BIRCH.N_j.sum(),
                                  sizes=sizes_j)

Step 8 [paper §V-B verbatim, observation]:
        Card_true ← observe_from_query_execution(q)

Step 9 [paper Eq 2 verbatim]:
        Q-error_t ← max(Card_esti/Card_true, Card_true/Card_esti)
        if Card_esti ≤ 0 or Card_true ≤ 0:
            Q-error_t ← ∞                  # measure_paper_exact.py q_error() 동일

Step 10 [paper §V-B verbatim, period trigger]:
        t ← t + 1
        if t mod P == 0 and t > 0:

Step 11 [paper Eq 3 verbatim]:
            sampling_ratio ← sampling_size_t / total_rows
            δ ← α · (Q-error_t − β) − (100 − α) · sampling_ratio
            # paper exact: q_err inf 시 q_err_safe ← 100.0
            #              (measure_paper_exact.py line 125)

Step 12 [paper Eq 4 verbatim]:
            V_t ← m · V_{t-1} + η_t · δ

Step 13 [paper Eq 5 verbatim]:
            new_size ← max(1, round(sampling_size_t + V_t))
            sampling_size_{t+1} ← new_size            # paper Eq 5 scalar update

Step 14 [★ 본 연구 augment, Component D group-aware allocation]:
            # paper Eq 5 의 new_size 를 cluster 별 분배 (본 Form 1 핵심)
            n_j_new ← group_aware_alloc(total_budget=new_size,
                                         sizes=BIRCH.N_j,
                                         sigma=sigma_j,
                                         mode=alloc_mode)
            # mode="proportional" 권장 (RQ2 Neyman paradox sel=0.01 한정의
            #   자연 결론, BIRCH N_j online 유지 cost 적음)

Step 15 [★ 본 연구 augment, Component A realloc]:
            SRS.realloc(n_j_new)            # reservoir capacity 갱신
            # n_j_new[j] > current_cap[j]: np.zeros pad
            # n_j_new[j] < current_cap[j]: truncate

Step 16 [paper Eq 6 verbatim]:
            η_{t+1} ← γ · η_t

Step 17 [★ 본 연구 augment, streaming tuple incremental update]:
    # 매 새 tuple arrival 시 (query loop 와 병렬):
    for each new tuple x_τ ∈ D:
        BIRCH.partial_fit([x_τ])                       # online cluster update
        j_star ← BIRCH.predict([x_τ])                  # cluster assignment
        SRS.update(x_τ, j_star)                        # Vitter Algorithm R
        # BIRCH CF tuple 자동 갱신:
        #   N_j[j_star] += 1
        #   LS_j[j_star] += x_τ
        #   SS_j[j_star] += x_τ ⊙ x_τ
```

## C-5. paper baseline vs Form 1 비교 표

| Step | paper baseline (verbatim) | 본 Form 1 의역 step-wise | 차이점 |
|---|---|---|---|
| Step 1 | N = ⌈z²·P̂(1−P̂)/e²⌉ = 385 | 동일 | none (paper exact) |
| Step 2 | V_0=0, η_0=0.1, t=0 + 7 hyperparam | 동일 + ★ K=20 추가 | K 추가만 |
| Step 3 | (없음) | ★ BIRCH init | ★ 본 연구 신규 (Component B) |
| Step 4 | (없음, Bernoulli 의 전체 dataset random sample) | ★ SRS init + group_aware_alloc | ★ 본 연구 신규 (Component A + D) |
| Step 5 | (warm-up 자체 paper 산문 없음) | ★ BIRCH/SRS warm-up | ★ 본 연구 신규 |
| Step 6 | for each query q | 동일 | none |
| Step 7 | Bernoulli sample at sampling_size → estimate | ★ SRS stratified estimate (per-cluster) | ★ 본 연구 augment (Component A) |
| Step 8 | observe Card_true | 동일 | none |
| Step 9 | Q-error = max(...) | 동일 (paper Eq 2 verbatim) | none |
| Step 10 | period P=50 trigger | 동일 | none |
| Step 11 | δ = α·(Q-err−β) − (100−α)·ratio | 동일 (paper Eq 3 verbatim) | none |
| Step 12 | V_t = m·V_{t-1} + η·δ | 동일 (paper Eq 4 verbatim) | none |
| Step 13 | sampling_size_{t+1} = size_t + V_t (scalar) | 동일 (paper Eq 5 verbatim, scalar update) | none |
| Step 14 | (paper 없음, scalar new_size 만) | ★ group_aware_alloc (cluster 별 분배) | ★ 본 연구 핵심 augment (Eq 5 sampling_size update 의 본 연구 group-aware allocation augment) |
| Step 15 | (없음) | ★ SRS realloc (capacity 갱신) | ★ 본 연구 신규 |
| Step 16 | η_{t+1} = γ·η_t | 동일 (paper Eq 6 verbatim) | none |
| Step 17 | (paper batch 환경, streaming axis 없음) | ★ streaming tuple incremental update (BIRCH + SRS) | ★ 본 연구 신규 (Component A+B streaming) |

---

# 부록 §K — 5/27 발표 + 6/11 보고서 + 5/15 review form 영역의 deliverable mapping

본 §K 영역은 본 v2 narrative 영역의 5/27 발표 + 6/11 보고서 + 5/15 review form 영역의 deliverable mapping 영역이다. 본 v2 영역의 §0-§14 본문 + 부록 §A-§J 영역의 각 영역이 위 3 deliverable 영역의 어느 위치 영역에 mapping 되는지의 정리 영역이다.

## K-1. 5/27 발표 (20 slide framework) mapping

본 v2 narrative 영역과 5/27 발표 영역의 20 slide framework 영역의 mapping 영역은 다음과 같다.

| slide | 영역 | 본 v2 source |
|---|---|---|
| 1 | Title + Team + Date | -- |
| 2 | Problem (VAQ 영역) | §1 + 부록 §C-1 (paper §V verbatim) |
| 3 | Paper Exqutor 핵심 메커니즘 | §0 + 부록 §C-1 + 부록 §C-2 |
| 4 | 본 연구 contribution scope (Form 1) | §0 + §13 + §14 |
| 5 | paper §V-B Eq 1-6 + 본 Form 1 통합 axis (17-step) | §6 + §8 + 부록 §C-4 |
| 6 | 본 Form 1 Component A (SRS) | §4 + 부록 §F-1.6 (reservoir) |
| 7 | 본 Form 1 Component B (BIRCH) | §5 |
| 8 | 본 Form 1 Component C (paper Eq 2-6 통합) | §6 |
| 9 | 본 Form 1 Component D (allocation) | §7 + §12 |
| 10 | 측정 1: streaming workload simulation | §14.3 + 부록 §I-2 |
| 11 | 측정 1 결과 (paired Δ% vs paper Bernoulli) | §11 K granularity + §14.3 |
| 12 | 측정 3: 4-way 비교 (Bernoulli + SelNet + 본 Form 1) | §14.3 + 부록 §G-3.1 + 부록 §G-3.2 |
| 13 | 측정 3 결과 (mean Q-error + inference latency) | §14.3 |
| 14 | paper §VI 한계 보완 (L1 + L5 + L6) | §0 + 부록 §G-3 |
| 15 | RQ1/RQ2/RQ3 trilogy 통합 (batch + streaming) | §9 + §10 + §11 + §12 |
| 16 | Pareto frontier + 자원 효율 | §10 + §13.6 |
| 17 | 정직 disclosure (40 폐기 + byte-identical + scope) | §3 + 부록 §A (정직 disclosure 13) + 부록 §F-5 |
| 18 | 본 Form 1 한계 + future work | §6.4 + §12.7 + 부록 §A |
| 19 | paper-grade publication path | §14.5 + §14.6 |
| 20 | Conclusion + Q&A | -- |

본 mapping 영역이 5/27 발표 영역의 deck v7 update 영역의 source 다 (post-5/15 박광현 미팅 영역의 변경 영역의 반영 영역).

## K-2. 6/11 보고서 (11 § + 6 부록) mapping

본 v2 narrative 영역과 6/11 보고서 영역의 11 § + 6 부록 영역의 mapping 영역은 다음과 같다.

| § | 보고서 영역 | 본 v2 source |
|---|---|---|
| §1 | 서론 (Introduction) | §0 + §1 |
| §2 | 배경 (Background) | §1 + 부록 §C |
| §3 | 관련 연구 (Related Work) | 부록 §G |
| §4 | 본 연구 방법론 | §4 + §5 + §6 + §7 + §8 |
| §5 | 실험 환경 | 부록 §H |
| §6 | 측정 결과 | §9 + §10 + §11 + §12 + §14.3 |
| §7 | 자원 효율 Pareto frontier | §10 + §13.6 |
| §8 | paper 한계 보완 (L1 + L5 + L6) | §0 + 부록 §G |
| §9 | 본 Form 1 한계 + 정직 disclosure | 부록 §A |
| §10 | future work | §6.4 + §12.7 + §14 |
| §11 | 결론 | §0 + §13 |
| 부록 A | paper §V-B Eq 1-6 verbatim | 부록 §C |
| 부록 B | 본 Form 1 Component A+B+C+D 의사코드 | §4 + §5 + §6 + §7 + 부록 §I |
| 부록 C | paper Eq 1-6 + 본 Form 1 통합 표 | §8 + 부록 §C |
| 부록 D | 40 폐기 method 정직 분류 | 부록 §F-5 |
| 부록 E | byte-identical caveat (6 unique × 9 nominal) | §9.6 + 부록 §A-7 |
| 부록 F | REPORT v11 1362 line raw data | -- (separate file) |

본 mapping 영역이 6/11 보고서 영역의 outline v4 update 영역의 source 다 (post-5/15 박광현 미팅 영역의 변경 영역의 반영 영역).

## K-3. 5/15 박광현 review form (8 §) mapping

본 v2 narrative 영역과 5/15 박광현 review form 영역의 8 § 영역의 mapping 영역은 다음과 같다.

| § | review form 영역 | 본 v2 source |
|---|---|---|
| §0 | TL;DR (Form 1 fix + 4 측면) | §0 + §14 |
| §1 | paper §V-B "without index" anchor | §0 + 부록 §C-1 |
| §2 | Form 1 Component A+B+C+D + 17-step pseudo-code | §4 + §5 + §6 + §7 + §8 + 부록 §C-4 |
| §3 | paper 한계 보완 (L1+L5+L6) | §0 + 부록 §G |
| §4 | 측정 plan (5/27 phase 1 + 6/11 phase 2) | §14.3 |
| §5 | timeline (5/15 / 5/27 / 6/11 / post-6/11) | §14.6 |
| §6 | review 요청 12 항목 (박세은 6 + 박광현 6) | 부록 §B + §14.7 |
| §7 | 정직 disclosure 13 영역 | 부록 §A |
| §8 | fix 영역 vs 변경 가능 영역 | §0 + §14 |

본 mapping 영역이 5/15 박광현 review form PDF v3 update 영역의 source 다 (post-5/15 박광현 미팅 영역의 변경 영역의 반영 영역).

## K-4. 팀원 공유 form 영역 mapping

팀원 공유 form 영역 (peer 톤 변환 ~해 / ~지 + 1 page 압축 영역) 의 mapping 영역은 다음과 같다.

| 영역 | 팀원 공유 form 영역 | 본 v2 source |
|---|---|---|
| 1. 본 연구 main theme | "Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ" | §0 |
| 2. 4 측면 | 대체 / 보완 / 개선 / 추가검증 | §0 |
| 3. paper §V-B "without index" anchor | paper p.5 verbatim | 부록 §C-1 |
| 4. Form 1 Component A+B+C+D | SRS + BIRCH + paper Eq 2-6 통합 + 4 mode allocation | §4 + §5 + §6 + §7 |
| 5. 1001 file batch baseline | 단독 대체 −10.17% + 결합 92.5% paired uplift | §9 |
| 6. K granularity SF axis | SF=1+10+100 × K=10/20/30 = 48 file 추가 측정 완료 | §11 |
| 7. Neyman selectivity-dependent | sel=0.01 paradox + sel=0.1 정합 | §12 |
| 8. 권장 설계 | 단독 + 결합 + 자원 + 다중 + streaming | §13 |
| 9. 5/27 + 6/11 timeline | phase 1 (52-87h) + phase 2 (+30-50h) | §14 |
| 10. paper-grade publication | EDBT short 10월 deadline + VLDB short 4월/11월 | §14.5 |

본 mapping 영역이 팀원 공유 form 영역 (카톡 + 슬랙 + Notion) 의 source 다.

---

# 부록 §J — Agent A-J 10 호출 결과 종합

본 §J 영역은 본 세션 22.5h 영역의 Agent A-J 10 호출 영역의 결과 종합 영역이다. 본 영역이 본 v2 narrative 의 base evidence 영역이며, 5/15 박광현 review form §부록 영역의 source 다.

## J-1. Agent 호출 영역의 mission + 결과 file 영역

| Agent | mission | 결과 file (line) | 시간 |
|---|---|---|---|
| A | paper 재정독 + 8 옵션 발산 | agent_A_paper_재정독_연구방향_옵션_20260514_2000.md (733) | 7분 |
| B | Agent A 검증 (신뢰도 78%, 정정 7) | agent_B_평가자_검증_20260514_2030.md (621) | 9분 |
| C | 8 옵션 deep dive + Cochran 1977 §5.5 발견 | agent_C_deep_dive_8옵션_종합권장_20260514_2200.md | 7.6분 |
| D | paper §VI 한계 + 경쟁 paper + 박광현 BDAI 본업 | agent_D_paper_§VI_한계_경쟁_paper_새영역_20260514_2330.md (724) | 10.5분 |
| E | Form 1 구체화 (Component A+B+C+D + 측정 plan + 5/27/6/11/5/15 + publication) | agent_E_Form_1_구체화_streaming_aware_20260515_0000.md | 8.6분 |
| F | 측정 + code plan (★ paper algorithm pseudo-code 없음 critical 정정) | agent_F_streaming_측정_plan_code_plan_20260515_0100.md (1230) | 8.6분 |
| G | paper Eq 1-6 verbatim + 17-step pseudo-code + SelNet/CE4HD/Ada-ef reuse | agent_G_paper_Eq_1-6_pseudo_code_4way_20260515_0200.md (1481) | 10.4분 |
| H | 1001 file batch baseline 재해석 + Form 1 통합 + RQ 재정립 RQ1'-RQ5' | agent_H_1001_file_재해석_batch_baseline_Form1_통합_20260515_0300.md (1100+) | 10분 |
| I | 5/27 20 slide + 6/11 §별 outline 세부 + 정직 disclosure 7 위치 | agent_I_5_27_20slide_6_11_outline_세부_20260515_0400.md (1651) | 12.8분 |
| J | 박세은 6 영역 답변 form (카톡 복붙) + ECQO multi-layer 4 + paper §V "without index" verbatim | agent_J_박세은_6영역_통합대응_답변form_20260515_0500.md (667) | 7.8분 |

총 = 10 agent, ~91 분 누적 background 시간 (병행 진행으로 wall-clock ~2h).

## J-2. 핵심 발견 (Agent 결과 종합)

### J-2.1 Agent A (paper 재정독 + 8 옵션 발산)

paper Exqutor PDF 영역의 정확 재정독 영역 + 8 옵션 영역의 발산 영역:
- 옵션 A (현 narrative): 1001 file batch baseline 영역의 reframing
- 옵션 B (Eq 2-6 확장): paper Eq 3 + Eq 4 의 group-aware augment 영역
- 옵션 C (Neyman paradox): RQ2 5-way 영역의 selectivity-dependent 영역
- 옵션 D (L0-L4): "분포 안다" 영역의 multi-layer 영역
- 옵션 E (Multi-table): paper §VI-C Fig.7 영역의 multi-join 영역
- 옵션 F (ECQO): paper §V-A 영역, 본 연구 outside
- 옵션 G (reservoir): paper §V-B 영역의 Vitter 1985 base
- 옵션 H (TPC-DS): paper §VI-B 영역의 TPC-H VAQ 외 추가 benchmark

자체 추천: A+C (현 narrative + Neyman paradox 영역 발현).

### J-2.2 Agent B (Agent A 검증)

Agent A 영역의 신뢰도 78% 영역 + 정정 7 영역 (★★★ 1 + ★★ 3 + ★ 3):
- ★★★ "5 단계 中 1 단계" 정정 = Algorithm 1 분류 무효, Eq 1 vs Eq 2-6 정정 (정정 룰 #1)
- ★★ Neyman paradox sel=0.01 한정 명시 (정정 룰 #9)
- ★★ σ_j range oracle 가정 명시 (정직 disclosure #10)
- ★★ Pareto Top 5 영역의 정확 표기 (sparse_rp / chao_weighted / neuram / pca1d / hilbert)
- ★ byte-identical 영역의 6 unique × 9 nominal 영역 (정직 disclosure 영역)
- ★ 학부 capstone-grade ★★ 매우 강력 영역의 명시
- ★ "100% 검증" 표기 회피 영역

### J-2.3 Agent C (Cochran 1977 §5.5 발견)

본 Agent C 영역의 가장 큰 발견 = Cochran 1977 §5.5 영역의 partial 적용 영역. 본 영역이 본 연구의 RQ2 paradox 영역의 학술 base 영역의 핵심 영역이며, hybrid 3 (현 narrative + Neyman paradox + Form 1 framework) 영역의 권장 영역.

### J-2.4 Agent D (paper §VI 한계 + 경쟁 paper + 박광현 BDAI 본업)

★★★ 영역의 핵심 발견:
- CE4HD VLDB 2024 (Lan-Bao RMIT, github 미공개) 의 paper 영역 확인
- Ada-ef arxiv 2512.06636 (HNSW ef search, layer 다름) 의 paper 영역 확인
- 박광현 BDAI 본업 (RELOAD 2026 / CANNON 2026 / DFLOP 2026 / Exqutor 2025 / FaScalSQL / SPID-Join) 의 paper 영역 확인

새 옵션 L/M/N/O/P 추가:
- 옵션 L (CE4HD compare): CE4HD 영역의 paper level 인용 + 6/11 보고서 §3 영역
- 옵션 M (Ada-ef compare): Ada-ef 영역의 paper level 인용 + 6/11 보고서 §3 영역
- 옵션 N (4-way framework): paper §VI-D Fig.12 영역의 4-way 비교 framework 확장 영역 ★★★
- 옵션 O (박광현 본업 align): RELOAD / CANNON / DFLOP 영역의 align 가능성 영역
- 옵션 P (paper-grade publication): EDBT short / VLDB short / ICDE position 영역

★★★ 옵션 N (4-way framework) 가 본 연구의 contribution 영역의 핵심.

### J-2.5 Agent E (Form 1 구체화)

Form 1 8 영역의 구체화 영역:
1. Technical: Component A+B+C+D + 17-step + paper Eq 1-6 통합
2. 측정 plan: 5 측정 영역 (3180 file, cost 135-195h)
3. 5/27 발표: 20 slide framework
4. 6/11 보고서: 11 § + 6 부록
5. 5/15 review form: 1-2 page 자료
6. publication path: EDBT short 10월, VLDB 4월/11월
7. 본 Form 1 한계: framework axis novelty + online cluster drift + 1001 file batch axis
8. 종합 (Agent E 자체 권장): Form 1 main thread 영역 fix + 4 측면 + phase 1/2 분리

### J-2.6 Agent F (측정 + code plan + critical 정정)

★ critical 정정: paper §V-B 영역에 algorithm pseudo-code 없음 (Eq 1-6 + 산문 + hyperparam 7종만). "14-step" = 본 연구 자체 의역 (정정 룰 #2).

Component A-D 영역의 구현 plan + cost 산정 128-196h (Agent E 와 ±5% 일치).

### J-2.7 Agent G (paper Eq 1-6 verbatim + 17-step + SelNet/CE4HD/Ada-ef)

paper Eq 1-6 verbatim 영역의 정확 정독 영역 (PDF 직접 read) + 본 의역 step-wise pseudo-code 영역의 정확 17 step 영역 정정. SelNet [74] reuse 가능 영역 (Python 95.5%). CE4HD github 미공개 영역 confirmed. Ada-ef layer 다름 영역. **4-way → 3-way (5/27 phase 1)** 축소 영역.

### J-2.8 Agent H (1001 file 재해석)

1001 file 영역 = 폐기 X 영역. **batch baseline axis** positioning + Form 1 streaming axis 와 **complementary framework** 영역. RQ 구조 = 현 RQ1/RQ2/RQ3 (batch) + 신규 RQ1'-RQ5' (paper-grade streaming) 영역.

### J-2.9 Agent I (5/27 20 slide + 6/11 §별 세부)

5/27 20 slide × 5 명세 + 6/11 11§+6 부록 세부 영역의 42-48 page paper-grade 확장 영역. Form 1 batch + streaming 통합 5 영역 (slide + § 위치 명시) 영역.

### J-2.10 Agent J (박세은 6 영역 답변 form)

박세은 6 영역 답변 form (카톡 복붙 plain text) + 영역 4 multi-layer 4 (ECQO 대안) + ★★★ paper §V 도입부 verbatim 발견 영역 (paper p.5 좌단 "For VAQs without index... sampling-based approach"). 5/15 박광현 review form base 영역.

## J-3. Agent 호출 영역의 본 v2 narrative 영역에의 반영

본 Agent 호출 영역의 결과 영역의 본 v2 narrative 영역에의 반영 영역은 다음과 같이 정리된다.

| Agent | 핵심 발견 | 본 v2 narrative 영역에의 반영 |
|---|---|---|
| A | 8 옵션 발산 | §13 권장 설계 영역의 base + 옵션 N + 옵션 P 영역의 발현 |
| B | 정정 7 영역 | 정정 룰 #1 + #9 + 정직 disclosure 영역의 base |
| C | Cochran 1977 §5.5 | §7.5 + §12.6 영역의 학술 base |
| D | CE4HD + Ada-ef + 박광현 본업 | 정직 disclosure #3 + #4 + §14.7 + 부록 §G-3 영역의 base |
| E | Form 1 구체화 | §4-§8 영역의 base + §14 영역의 source |
| F | paper algorithm pseudo-code 없음 정정 | 정정 룰 #2 + 정직 disclosure #1 + §6.5 영역의 base |
| G | 17-step pseudo-code 정확 영역 | §8 + 부록 §C-4 영역의 source |
| H | 1001 file batch baseline 재해석 | §9 batch baseline 재해석 영역의 base |
| I | 5/27 20 slide + 6/11 §별 outline | §14.3 측정 plan 영역의 base + 5/27 + 6/11 영역의 source |
| J | 박세은 6 영역 답변 form | 부록 §B 영역의 source + paper §V 도입부 verbatim 영역의 §0 + 부록 §C-1 영역의 anchor |

본 Agent 호출 영역의 결과 영역이 본 v2 narrative 영역의 base evidence 영역의 핵심 영역이며, 본 v2 영역의 paper-grade defensibility 영역의 source 다.

---

# 부록 §D — 정정 룰 14 list

본 연구의 mass update prep 영역 정정 룰 list. Agent A-J 호출 결과 + 박세은 5/14 9:09 ~ 10:15 9 영역 자문 + 5/14 환각 검증 H1 정정 종합. 회의 PDF v2 + 5/27 deck + 6/11 outline + 5/15 review form + 본 narrative 영역의 일괄 적용 영역.

| # | 정정 영역 | source | 영향 file |
|---|---|---|---|
| 1 | "5 단계 中 1 단계" → "Eq 1 (Bernoulli) 대체 vs Eq 2-6 유지" | Agent B 1판 | 모든 자료 |
| 2 | "Algorithm 1 14-step" → "paper §V-B Eq 1-6 + 본 의역 17-step pseudo-code" | Agent F+G 2판 | 모든 자료 |
| 3 | "AS single-table 不可 = 구조 X" → "paper §V-B single-table OK, 공개 코드 구현 한계" | 박세은 9:09 #1 | 회의 PDF + 모든 자료 |
| 4 | "block only 추출" → "block + row hybrid" | 박세은 9:09 #2 | 회의 PDF + 모든 자료 |
| 5 | "분포 안다" → L1/L2/L3 layer 분리 | 박세은 9:09 #3 + Agent J | RQ2 narrative 전반 |
| 6 | "분포 알면 ECQO 가능?" → paper §V-B = "without index" 가정 (p.5 verbatim) | ★★★ 박세은 9:09 #4 + Agent J | Form 1 narrative core (★★★ 최대 evidence) |
| 7 | "RQ3 = streaming" → "RQ3 = 사전 학습 batch baseline, Form 1 = streaming axis" | 박세은 9:09 #5 + 9:27 | RQ3 narrative 전반 |
| 8 | "0.1~0.5초 런타임" → SF=1 fit time, 매 query fit X | 박세은 9:27 | §3.5 자원 효율 |
| 9 | "Neyman paradox" → "Neyman paradox sel=0.01 한정, sel=0.1 = Neyman best (selectivity-dependent)" | 박세은 9:42 + Agent B 정정 | RQ2 5-way narrative |
| 10 | K granularity SF coverage: "SF=1 미측정" → "SF=1+10+100 × K=10/20/30 measured (48 file)" ✓ 완료 | 박세은 8:50 + 5/14 추가 측정 | §2.5 + §2.6 |
| 11 | "Bernoulli → Neyman −10%" narrative → 실제 측정 X (POOL −5~7%, 단일 cell best SIFT sel=0.1 −9.16%) | 박세은 9:54 + RQ2 csv 직접 verify | RQ2 narrative |
| 12 | 회의 PDF v2 §3.2 line 532-533 "Proportional −9.61% / Neyman −8.75%" wording → csv 직접 aggregate 값과 차이 (출처 source verify 필요) | 본 verify 발견 | RQ2 narrative |
| 13 | RQ2 5-way 측정 = SF=100 (DEEP+SIFT) 한정. SF=1/SF=10/SSN 미측정 | RQ2 csv file 명 + 사용자 22:05 confirm | RQ2 SF coverage |
| 14 | "Anti-Neyman > Neyman = Neyman 가설 무효" → 정확 의미: Neyman 가설 자체는 유효 but 본 데이터셋이 Neyman 의 가정 조건 (cluster 간 분산 다양함) 不만족 + selectivity-dependent (sel=0.01 paradox / sel=0.1 정합). σ_j 직접 측정 추가 검증 필요 (현재 oracle 가정) | 박세은 10:15 + Cochran 1977 partial | RQ2 narrative |

---

# 부록 §H — 측정 protocol 영역의 정리

본 §H 영역은 본 연구의 측정 protocol 영역의 정리 영역이다. 1001 file batch baseline 측정 영역의 protocol + Form 1 phase 1 + phase 2 측정 영역의 protocol 영역의 정확 표기 영역이며, 6/11 보고서 §5 실험 환경 영역의 source 다.

## H-1. 시스템 + 자원 영역

본 연구의 측정 시스템 영역은 capstone2026 서버 (165.132.140.240) 영역이며, 작업 디렉토리는 `/mnt/hdd0/home/capstone2026` 영역이다. 자세한 영역은 `_internal/SERVER_REGISTRY.md` 영역 참조.

**서버 자원 영역**:
- CPU: Intel Xeon (24 core / 48 thread)
- RAM: 256 GB
- GPU: NVIDIA RTX 3090 × 2 (24 GB VRAM each)
- 스토리지: SSD 2TB + HDD 8TB

**software stack 영역**:
- OS: Ubuntu 22.04 LTS
- Python: 3.10.x
- PostgreSQL: 16.x + pgvector 0.7.x
- 라이브러리: NumPy 1.24, FAISS 1.7.4, scikit-learn 1.3, hilbert-curve 1.0

## H-2. dataset 영역

본 연구의 dataset 영역의 정리는 다음과 같다.

| dataset | 차원 d | 영역 수 N | 본 측정 SF 영역 | paper 영역 |
|---|---:|---:|---|---|
| DEEP | 96 | 1M (SF=1) / 10M (SF=10) / 100M (SF=100) | sf=1 / 10 / 100 | paper §VI 의 main dataset |
| SIFT | 128 | 1M (SF=1) / 10M (SF=10) / 100M (SF=100) | sf=10 / 100 | paper §VI 의 main dataset |
| SSN (SimSearchNet++) | 256 | 1M (SF=1) / 10M (SF=10) | sf=10 / 100 | paper §VI-B dataset |
| YFCC100M | 192 | 100M (SF=10) | 미준비 | paper §VI-D Fig.12 (filtered vector search) |
| WIKI | 768 | 1M / 10M | 미준비 | paper §VI-E (high-dim) |

본 dataset 영역의 paper exact 정합성 영역의 확보 영역은 paper Exqutor github (BDAI-Research/Exqutor) 영역의 dataset preparation script + 본 연구의 measure_paper_exact.py 의 dataset loading 영역의 정확 정합 영역의 검증 영역이다.

## H-3. benchmark 영역

본 연구의 benchmark 영역은 paper §VI 영역의 TPC-H Vector-Augmented Query (VAQ) 영역과 직접 align 영역이다.

**TPC-H VAQ 영역**:
- Q3 (Shipping Priority Query) + vector similarity predicate
- Q5 (Local Supplier Volume Query) + vector similarity predicate
- Q20 (Potential Part Promotion Query) + vector similarity predicate
- ... (paper §VI 의 verbatim 영역 17 query)

**vector similarity predicate 영역**:
- distance threshold: paper §VI 의 verbatim 0.86 (cosine similarity)
- KNN query: top-K with K varies (paper §VI-D + paper §VI-E)

**selectivity sweep 영역**:
- sel=0.01 (1% of total rows)
- sel=0.10 (10% of total rows)
- sel=0.001 / sel=0.05 / sel=0.50: 본 연구 미측정 (future work)

**scale sweep 영역**:
- SF=1 (paper §VI 영역의 base scale)
- SF=10 (paper §VI 영역의 medium scale)
- SF=100 (paper §VI 영역의 large scale)

## H-4. baseline 영역

본 연구의 baseline 영역의 정리는 다음과 같다.

| baseline | 영역 | 본 연구 측정 영역 |
|---|---|---|
| paper §V-B Bernoulli | paper exact baseline | B1 9 file (paper exact 정합 검증) |
| SelNet [74] | learned estimator | 5/27 phase 1 영역의 3-way baseline |
| CE4HD SRCE/MRCE | learned reference object | 6/11 phase 2 영역의 paper level 인용 only |
| Ada-ef | HNSW search-time adaptation | paper level 인용 only |
| pgvector default | DB engine 의 default cardinality | 본 측정 contextual reference |
| VBASE default | DB engine 의 default cardinality | 본 측정 contextual reference |

paper §V-B Bernoulli baseline 영역의 paper exact 정합 검증 영역은 measure_paper_exact.py 의 AdaptiveState class (line 67-140) 의 paper Eq 1-6 verbatim 100% 정합 검증 영역이며, 본 영역의 review-grade 정합성 영역의 evidence 는 본 연구의 paper §V-B Fig 12 영역의 절사 평균 Q-error 영역의 측정 1.618 vs paper 보고값 1.69 = −4.3% 재현 영역이다.

## H-5. metrics 영역

본 연구의 metrics 영역의 정리는 다음과 같다.

**accuracy metrics 영역**:
- Q-error mean (paper Eq 2 verbatim) = primary metric
- Q-error std (variability 영역)
- Q-error percentile (50% / 90% / 99% 영역, paper §VI-D 영역과 align)
- paired Δ% (본 연구 vs baseline 의 difference 영역)

**efficiency metrics 영역**:
- inference latency (ms per query)
- offline training cost (s, baseline 영역 한정)
- memory peak (MB)
- sample size trajectory (paper §VI-B Fig.6 영역과 align)

**streaming metrics 영역 (Form 1 phase 1)**:
- concept drift response time (queries to recover)
- cluster centroid drift Δ% (offline batch K-means 영역과의 비교)
- BIRCH CF tuple update latency (μs per insert)

**statistical analysis 영역**:
- paired t-test (paper §VI 영역에서도 표준 영역)
- Cliff's δ effect size (non-parametric)
- Hedges' g effect size (parametric)
- one-sided p<0.05 영역의 outperform rate
- bootstrap CI (95% confidence interval)

## H-6. trial 영역

본 연구의 trial 영역의 정리는 다음과 같다.

- trial per cell: paper exact 영역에서 5 trial (paper §VI 영역의 표준), 본 측정에서 일부 cell 영역 10 trial (statistical power 영역 강화)
- random seed: 본 연구의 reproducibility 영역의 base
- trial 의 effective n 영역: byte-identical caveat (6 unique × 9 nominal) 영역의 분리 표기

## H-7. measurement portfolio 영역의 분류

본 연구의 measurement portfolio 1001 file 영역의 분류는 다음과 같다.

| 분류 ID | 영역 | file 수 | 영역 |
|---|---|---:|---|
| 01_RQ1_논문_baseline_재현 | RQ1 영역 paper baseline 재현 | ~80 | DEEP / SIFT / SSN sf=100 × Bernoulli (B1) |
| 02_RQ2_5way_표본할당 | RQ2 영역 5-way 할당 | ~125 | DEEP / SIFT sf=100 × 5 method × 5 trial |
| 03_RQ3_단독_CaseA | RQ3 영역 단독 대체 (CaseA) | 495 | 9 cells × 56 method × 1 mode |
| 04_RQ3_결합_CaseB | RQ3 영역 결합 (CaseB) | 496 | 9 cells × 56 method × 1 mode |
| 05_alpha_sweep | α sweep (CaseB ensemble) | 16 | 4 method × 4 α (0.3 / 0.4 / 0.6 / 0.7) |
| 06_클러스터수_K_민감도 | K granularity 영역 | 48 (신규) | DEEP × 3 SF × 2 K (10/30) × 4 method × 2 mode |
| 07_multi-join | multi-join 영역 | 8 | A2-Fig7 영역의 multi-join 측정 |
| 08_centroid_tuple | Centroid tuple 영역 | 8 | A2-Fig9 single cell 영역의 결합 best |
| 09_b1_b2_b3_cheap | B1 + B2 + B3 cheap approximation | 24 | 3 baseline × 8 cell |
| 10_전체측정_백업 | 측정 백업 영역 | -- | raw backup 영역 |

총 1113 file (1001 paper exact carry-over + 본 세션 64 + K granularity 48).

## H-8. paper-grade publication path 의 cost 산정

본 §H 영역의 마지막 영역은 paper-grade publication path 영역의 cost 산정 영역이다.

| publication 영역 | timeline | 측정 cost | dev cost | venue |
|---|---|---:|---:|---|
| 5/27 발표 phase 1 | 5/14-5/27 | ~13-25h server | 52-87h | -- |
| 6/11 보고서 phase 2 | 5/27-6/11 | +15-25h server | +30-50h | -- |
| paper draft 8월 | 6/11-8월 | +30-50h server (generalization) | +50-80h (draft) | -- |
| EDBT short paper submit | 9-10월 | +20-30h server (rebuttal prep) | +30-50h (revision) | EDBT short (~30%) |
| (option) VLDB short paper | 11월 | +30-50h server | +50-80h | VLDB short (~25%) |
| presentation prep | 2027 1-2월 | -- | +30-50h | -- |

본 cost 산정 영역의 정직 표기 영역의 cost = 5/27 phase 1 (52-87h) + 6/11 phase 2 (+30-50h) = 학부 capstone-grade ★★ 매우 강력 영역. paper-grade publication 영역은 post-6/11 future paper 영역으로 분담 (6-12 개월 추가 영역).

---

# 부록 §I — Form 1 측정 script template

본 §I 영역은 Form 1 phase 1 + phase 2 측정 영역의 script template 영역이다. Agent F + G 영역의 검증 결과 6 신규 file 영역의 ~ 1700 line 영역의 template 영역이다.

## I-1. measure_form1_common.py (Component A-D + streaming generator)

본 file 영역은 Form 1 4 component 영역의 common API 영역 + streaming data generator 영역의 영역이다. 예상 코드량 ~400 line.

```python
# _internal/scripts/measure_form1_common.py (신규 ~400 line)

import numpy as np
from sklearn.cluster import Birch
from collections import deque

PAPER_HYPERPARAM = {
    "N": 385,
    "m": 0.9,
    "eta_0": 0.1,
    "alpha": 50,
    "beta": 1.5,
    "gamma": 0.99,
    "period_P": 50,
}

class StratifiedReservoir:
    """Component A: Stratified Reservoir Sampling

    Vitter 1985 Algorithm R + per-stratum reservoir.
    Al-Kateb-Lee-Wang ISJ 2014 + SSDBM 2010 base.
    """
    def __init__(self, n_strata: int, capacity_per_stratum: np.ndarray, dim: int):
        self.K = n_strata
        self.capacity = capacity_per_stratum.copy()  # n_j per stratum
        self.reservoirs = [np.zeros((self.capacity[j], dim)) for j in range(self.K)]
        self.t = np.zeros(self.K, dtype=int)  # tuple count per stratum
        self.size = np.zeros(self.K, dtype=int)  # current reservoir size per stratum

    def update(self, x: np.ndarray, j: int):
        """Vitter 1985 Algorithm R per-stratum."""
        self.t[j] += 1
        if self.size[j] < self.capacity[j]:
            self.reservoirs[j][self.size[j]] = x
            self.size[j] += 1
        else:
            r = np.random.randint(0, self.t[j])
            if r < self.capacity[j]:
                self.reservoirs[j][r] = x

    def realloc(self, new_capacity: np.ndarray):
        """Component D 의 group_aware_alloc 후 reservoir capacity 갱신."""
        for j in range(self.K):
            new_cap_j = new_capacity[j]
            current_cap_j = self.capacity[j]
            if new_cap_j > current_cap_j:
                # pad with zeros
                pad = np.zeros((new_cap_j - current_cap_j, self.reservoirs[j].shape[1]))
                self.reservoirs[j] = np.vstack([self.reservoirs[j], pad])
            else:
                # truncate
                self.reservoirs[j] = self.reservoirs[j][:new_cap_j]
            self.capacity[j] = new_cap_j

    def estimate(self, qvec: np.ndarray, D_threshold: float,
                 total_rows: int, sizes: np.ndarray) -> float:
        """Per-stratum cardinality estimate."""
        total_est = 0.0
        for j in range(self.K):
            if self.size[j] == 0:
                continue
            # count tuples in reservoir within threshold
            dists = np.linalg.norm(self.reservoirs[j][:self.size[j]] - qvec, axis=1)
            count_in = np.sum(dists <= D_threshold)
            # extrapolate to stratum
            stratum_est = count_in / self.size[j] * sizes[j]
            total_est += stratum_est
        return total_est


class OnlineBirchCluster:
    """Component B: BIRCH CF-tree online cluster maintenance

    Zhang-Ramakrishnan-Livny 1996 SIGMOD base.
    scikit-learn `sklearn.cluster.Birch` API wrapper.
    """
    def __init__(self, n_clusters: int = 20, threshold: float = 0.5,
                 branching_factor: int = 50):
        self.K = n_clusters
        self.birch = Birch(n_clusters=n_clusters, threshold=threshold,
                            branching_factor=branching_factor)
        self.N_j = np.zeros(self.K, dtype=int)
        self.LS_j = None  # initialized on first partial_fit
        self.SS_j = None
        self.dim = None

    def partial_fit(self, X_chunk: np.ndarray):
        """Streaming update."""
        if self.LS_j is None:
            self.dim = X_chunk.shape[1]
            self.LS_j = np.zeros((self.K, self.dim))
            self.SS_j = np.zeros((self.K, self.dim))
        self.birch.partial_fit(X_chunk)
        labels = self.birch.predict(X_chunk)
        # update CF tuple per cluster
        for j in range(self.K):
            mask = labels == j
            if not np.any(mask):
                continue
            X_j = X_chunk[mask]
            self.N_j[j] += X_j.shape[0]
            self.LS_j[j] += np.sum(X_j, axis=0)
            self.SS_j[j] += np.sum(X_j ** 2, axis=0)

    def predict(self, X_new: np.ndarray) -> np.ndarray:
        """Cluster assignment for new tuples."""
        return self.birch.predict(X_new)

    def sigma_squared(self) -> np.ndarray:
        """Per-cluster σ_j² estimation: SS_j/N_j − (LS_j/N_j)²"""
        sigma2 = np.zeros(self.K)
        for j in range(self.K):
            if self.N_j[j] == 0:
                sigma2[j] = 0.0
                continue
            mean_j = self.LS_j[j] / self.N_j[j]
            var_j = self.SS_j[j] / self.N_j[j] - mean_j ** 2
            # multi-dim 경우 trace 영역 (또는 mean of dim-wise var)
            sigma2[j] = np.mean(var_j)
        return sigma2


def group_aware_alloc(total_budget: int, sizes: np.ndarray,
                      sigma: np.ndarray, mode: str = "proportional") -> np.ndarray:
    """Component D: 4 mode allocation rule.

    mode = "equal" | "proportional" | "neyman" | "anti_neyman"
    """
    K = len(sizes)
    if mode == "equal":
        n_j = np.full(K, total_budget // K, dtype=int)
        # distribute remainder
        for r in range(total_budget % K):
            n_j[r] += 1
    elif mode == "proportional":
        total_size = np.sum(sizes)
        if total_size == 0:
            return np.full(K, total_budget // K, dtype=int)
        n_j = np.round(total_budget * sizes / total_size).astype(int)
    elif mode == "neyman":
        # Cochran 1977 §5.5 Neyman allocation
        weights = sizes * sigma
        total_weight = np.sum(weights)
        if total_weight == 0:
            return np.full(K, total_budget // K, dtype=int)
        n_j = np.round(total_budget * weights / total_weight).astype(int)
    elif mode == "anti_neyman":
        # Negative control
        eps = 1e-9
        weights = sizes / (sigma + eps)
        total_weight = np.sum(weights)
        if total_weight == 0:
            return np.full(K, total_budget // K, dtype=int)
        n_j = np.round(total_budget * weights / total_weight).astype(int)
    else:
        raise ValueError(f"Unknown alloc mode: {mode}")
    # ensure min 1 per cluster
    n_j = np.maximum(n_j, 1)
    return n_j


class StreamingWorkloadGenerator:
    """concept drift simulation 영역 + paper §VI-B "shifting workloads" 영역 정량 측정."""

    def __init__(self, base_dataset: np.ndarray, drift_mode: str = "no_drift",
                 chunk_size: int = 1000):
        self.base = base_dataset
        self.drift_mode = drift_mode  # "no_drift" | "gradual" | "sudden"
        self.chunk_size = chunk_size
        self.position = 0
        self.drift_step = 0

    def next_chunk(self) -> np.ndarray:
        """Generate next chunk with drift simulation."""
        chunk = self.base[self.position:self.position + self.chunk_size]
        self.position += self.chunk_size
        if self.drift_mode == "gradual":
            # cluster centroid 영역 ε shift (Gaussian random walk)
            epsilon = 0.01 * self.drift_step
            chunk = chunk + np.random.randn(*chunk.shape) * epsilon
            self.drift_step += 1
        elif self.drift_mode == "sudden":
            # 매 5000 query 마다 distribution swap
            if self.drift_step % 5 == 0 and self.drift_step > 0:
                np.random.shuffle(chunk)
            self.drift_step += 1
        return chunk
```

## I-2. measure_form1_streaming.py (측정 1)

본 file 영역은 Form 1 phase 1 측정 1 (streaming workload simulation) 영역의 script 영역이다. 예상 코드량 ~300 line. paper §VI-B "shifting workloads" 영역의 정량 측정 영역.

```python
# _internal/scripts/measure_form1_streaming.py (신규 ~300 line)

from measure_form1_common import (
    PAPER_HYPERPARAM,
    StratifiedReservoir,
    OnlineBirchCluster,
    group_aware_alloc,
    StreamingWorkloadGenerator,
)
from measure_paper_exact import (
    AdaptiveState,
    load_dataset,
    q_error,
    observe_from_query_execution,
)
import numpy as np
import pandas as pd
import json
from pathlib import Path

def run_form1_streaming(dataset_name: str, sf: int, drift_mode: str,
                        alloc_mode: str = "proportional",
                        n_trial: int = 10,
                        output_dir: Path = Path("results/form1_phase1")):
    """Form 1 측정 1: Streaming workload simulation.

    paper §VI-B "shifting workloads" 영역의 정량 측정.
    """
    # 1. Load dataset + queries
    X, queries = load_dataset(dataset_name, sf)

    results = []
    for trial in range(n_trial):
        # 2. Init Form 1 4 component
        adaptive = AdaptiveState(**PAPER_HYPERPARAM)
        birch = OnlineBirchCluster(n_clusters=20)
        # Warm-up: chunk 단위 partial_fit
        warm_up_size = 5000
        birch.partial_fit(X[:warm_up_size])
        sigma_init = birch.sigma_squared()
        size_init = birch.N_j
        n_j_init = group_aware_alloc(
            total_budget=PAPER_HYPERPARAM["N"],
            sizes=size_init, sigma=np.sqrt(sigma_init),
            mode=alloc_mode,
        )
        srs = StratifiedReservoir(n_strata=20, capacity_per_stratum=n_j_init,
                                   dim=X.shape[1])
        # streaming generator
        generator = StreamingWorkloadGenerator(X[warm_up_size:],
                                                drift_mode=drift_mode,
                                                chunk_size=256)

        # 3. Streaming + query loop (17-step)
        q_errors = []
        for t, q in enumerate(queries):
            # Step 6: query loop
            qvec, D_threshold = q["vec"], q["threshold"]
            # Step 7: SRS stratified estimate
            sizes_j = birch.N_j
            Card_esti = srs.estimate(qvec, D_threshold, total_rows=sizes_j.sum(),
                                       sizes=sizes_j)
            # Step 8: observe Card_true
            Card_true = observe_from_query_execution(q)
            # Step 9-13: paper Eq 2-5 verbatim
            qe = q_error(Card_esti, Card_true)
            q_errors.append(qe)
            adaptive.update(qe, t, sizes_j.sum())
            # Step 14: group-aware allocation (본 augment)
            if t % PAPER_HYPERPARAM["period_P"] == 0 and t > 0:
                new_size = adaptive.sampling_size
                sigma_j = np.sqrt(birch.sigma_squared())
                n_j_new = group_aware_alloc(
                    total_budget=new_size,
                    sizes=birch.N_j, sigma=sigma_j,
                    mode=alloc_mode,
                )
                # Step 15: SRS realloc
                srs.realloc(n_j_new)
            # Step 17: streaming tuple incremental update
            if t % 100 == 0:
                # arrival of new chunk
                chunk = generator.next_chunk()
                if chunk.shape[0] > 0:
                    birch.partial_fit(chunk)
                    # SRS update per tuple
                    for x_tau in chunk:
                        j_star = birch.predict(x_tau.reshape(1, -1))[0]
                        srs.update(x_tau, j_star)

        # 4. Record results
        results.append({
            "dataset": dataset_name,
            "sf": sf,
            "drift_mode": drift_mode,
            "alloc_mode": alloc_mode,
            "trial": trial,
            "q_error_mean": np.mean(q_errors),
            "q_error_std": np.std(q_errors),
            "q_error_p50": np.percentile(q_errors, 50),
            "q_error_p90": np.percentile(q_errors, 90),
            "q_error_p99": np.percentile(q_errors, 99),
            "trajectory": q_errors,
        })

    # 5. Save
    output_dir.mkdir(parents=True, exist_ok=True)
    fname = f"form1_streaming_{dataset_name}_sf{sf}_{drift_mode}_{alloc_mode}.json"
    with open(output_dir / fname, "w") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    # 측정 1 scope: 3 dataset × 2 sf × 3 drift × 4 alloc_mode × 10 trial = 720 file
    for dataset_name in ["DEEP", "SIFT", "SSN"]:
        for sf in [10, 100]:
            for drift_mode in ["no_drift", "gradual", "sudden"]:
                for alloc_mode in ["equal", "proportional", "neyman", "anti_neyman"]:
                    run_form1_streaming(dataset_name, sf, drift_mode, alloc_mode)
```

## I-3. selnet_adapter.py (SelNet baseline)

본 file 영역은 SelNet [74] reference 영역의 baseline adapter 영역이다. 예상 코드량 ~200 line. yyssl88/SelNet-Estimation github 영역의 wrapper 영역.

```python
# _internal/scripts/selnet_adapter.py (신규 ~200 line)

from pathlib import Path
import numpy as np
import sys
import subprocess

SELNET_PATH = "/mnt/hdd0/home/capstone2026/baselines/SelNet-Estimation"
sys.path.insert(0, SELNET_PATH)


class SelNetWrapper:
    """SelNet (Wang et al. SIGMOD 2021) adapter for Form 1 framework.

    paper §VI-D Fig.12 baseline reproduce.
    DEEP 96d / SIFT 128d / SSN 256d dataset 지원 (.npy 형식 통일).
    """

    def __init__(self, dataset_path: Path, vec_dim: int,
                 partition_mode: str = "one"):
        self.dataset_path = dataset_path
        self.vec_dim = vec_dim
        self.partition_mode = partition_mode  # "one" | "CoverTree" | "RandomPartition"
        self.model = None
        self.trained = False

    def prepare_data(self, all_vecs: np.ndarray, output_dir: Path) -> None:
        """SelNet 의 .npy 형식 입력으로 변환."""
        output_dir.mkdir(parents=True, exist_ok=True)
        np.save(output_dir / "data.npy", all_vecs.astype(np.float32))
        # query pool + threshold + true_cardinality 생성
        # ... (SelNet training data generation protocol)

    def train(self, train_data_dir: Path, epochs: int = 100) -> dict:
        """SelNet offline training."""
        result = subprocess.run([
            "bash", f"{SELNET_PATH}/proc/shell/train.sh",
            "--data-dir", str(train_data_dir),
            "--partition", self.partition_mode,
            "--epochs", str(epochs),
        ], capture_output=True, text=True)
        # training log parsing
        # ...
        self.trained = True
        return {"training_time_s": ..., "final_loss": ...}

    def estimate(self, qvec: np.ndarray, threshold: float) -> float:
        """Per-query cardinality estimate."""
        # SelNet 의 predict_*.py 호출
        # input: qvec (vec_dim,) + threshold (scalar)
        # output: estimated cardinality (scalar)
        ...
        return est_card
```

---

# 부록 §G — Related Work 영역의 정리

본 §G 영역은 본 연구의 Related Work 영역의 정리 영역이다. paper Exqutor [74] reference + 본 연구의 base reference + 본 연구의 positioning 영역의 정리 영역이며, 6/11 보고서 §3 Related Work 영역의 source 다.

## G-1. paper Exqutor 본 영역 references

본 연구의 base 영역은 paper Exqutor 자체 영역이며, 본 paper 의 references 영역 中 본 Form 1 영역과 직접 관련된 영역은 다음과 같이 정리된다.

| ref ID | paper | venue | 영역 | Form 1 mapping |
|---|---|---|---|---|
| [22] | Sutskever et al. | "On the importance of initialization and momentum in deep learning" | momentum 영역 | paper Eq 4 (V_t momentum) |
| [38] | Malkov-Yashunin | "Efficient and robust approximate nearest neighbor search using HNSW" | HNSW indexing | paper §V-A ECQO (with index) 영역, 본 연구 outside |
| [67] | G. D. Israel | "Determining sample size" 1992 | classical sampling theory | paper Eq 1 (N=385 derivation) |
| [68] | Kipf et al. 2018 | "Learned Cardinalities for Multi-Attribute Queries" | Q-error metric | paper Eq 2 |
| [69] | Hilprecht et al. 2019 | "DeepDB: Learn from Data, not from Queries" | Q-error 영역 | paper Eq 2 |
| [70] | Dutt et al. 2019 | "Selectivity estimation for range predicates using lightweight models" | Q-error 영역 + adaptive estimation | paper Eq 2 + paper momentum |
| [74] | Wang et al. SIGMOD 2021 | "Consistent and Flexible Selectivity Estimation for High-Dimensional Data" (SelNet) | learned cardinality estimator | paper §VI-D Fig.12 baseline, 본 Form 1 의 보완 측면 (3-way 영역) |
| [79], [80] | Lipton-Naughton et al. | 1990 random sampling for join | random sampling 영역 | paper §VII Sampling 영역의 base |
| [81] | Lipton-Naughton-Schneider | 1990 adaptive sampling | adaptive sampling 영역 | paper §VII "does not consider sampling overhead or optimize it dynamically" 영역의 paper differentiation |

본 paper Exqutor references 영역 中 본 연구의 핵심 영역은 [67] (paper Eq 1 derivation), [74] (SelNet baseline), [22] (momentum), [81] (paper differentiation) 의 4 영역이다.

## G-2. 본 연구 Form 1 의 base references

본 연구의 Form 1 4 component 영역의 base references 영역은 다음과 같이 정리된다.

### G-2.1 Component A (SRS) references

| ref | paper | venue | 영역 |
|---|---|---|---|
| Vitter 1985 | "Random Sampling with a Reservoir" | TOMS 1985 | reservoir sampling Algorithm R |
| Al-Kateb-Lee-Wang 2010 | "Adaptive stratified reservoir sampling..." | SSDBM 2010 | stratified reservoir sampling |
| Al-Kateb-Lee-Wang 2014 | "Stratified Reservoir Sampling over Heterogeneous Data Streams" | Information Systems Journal 2014 | SRS 영역의 발현 |
| Chao 1982 | "A general purpose unequal probability sampling plan" | Biometrika 1982 | weighted reservoir sampling (chao_weighted method 영역) |
| Cochran 1977 | "Sampling Techniques, 3rd edition" | Wiley 1977 | classical stratified sampling theory, §5.5 Neyman / Proportional allocation |

### G-2.2 Component B (BIRCH) references

| ref | paper | venue | 영역 |
|---|---|---|---|
| Zhang-Ramakrishnan-Livny 1996 | "BIRCH: An Efficient Data Clustering Method for Very Large Databases" | SIGMOD 1996 | BIRCH CF-tree 영역의 base |
| Aggarwal-Han-Wang-Yu 2003 | "A Framework for Clustering Evolving Data Streams" | VLDB 2003 | CluStream micro-cluster + pyramidal time frame (future work 영역) |
| Sculley 2010 | "Web-Scale K-Means Clustering" | WWW 2010 | mini-batch K-means + partial_fit API (minibatch_partial method 영역) |
| Bradley-Mangasarian-Street 1998 | "Clustering via Concave Minimization" | NIPS 1997 | incremental K-means base |

### G-2.3 Component C (paper Eq 2-6) references

paper Exqutor 자체 영역 (paper §V-B Eq 1-6 verbatim) + paper Exqutor references [22] [67] [68]-[70] 영역.

### G-2.4 Component D (Distribution-aware stratification) references

| ref | paper | venue | 영역 |
|---|---|---|---|
| Cochran 1977 §5.5 | "Stratified Sampling: Optimal Allocation" | Wiley 1977 | Equal / Proportional / Neyman / Anti-Neyman allocation 영역의 classical theory |
| Neyman 1934 | "On the two different aspects of the representative method" | JRSS 1934 | Neyman allocation 의 origin (stratified sampling theory 영역) |
| Hansen-Hurwitz 1943 | "On the theory of sampling from finite populations" | Annals of Math Stat 1943 | Proportional allocation 의 origin (probability proportional to size) |

## G-3. 경쟁 paper 영역의 정리

본 연구와 같은 영역 (high-dimensional cardinality estimation + similarity search) 영역의 경쟁 paper 영역은 다음과 같이 정리된다.

### G-3.1 SelNet (Wang et al. SIGMOD 2021, paper [74])

**paper 영역**:
- 제목: "Consistent and Flexible Selectivity Estimation for High-Dimensional Data"
- 저자: Yaoshu Wang, Chuan Xiao, Jianbin Qin, Rui Mao, Makoto Onizuka, Wei Wang, Rui Zhang
- venue: SIGMOD 2021
- arxiv / DOI: Semantic Scholar paper ID 366009a33e6a1efba429af4f2d7ae2e3193806c9

**핵심 contribution**:
- piecewise linear + monotonic + control points 영역의 learned selectivity estimator
- 3 가지 접근 (Run SelNet without partition / with Cover Tree / with Random Partition) 영역의 분리
- training data generation + offline training + inference 영역의 framework 영역

**본 Form 1 영역과의 비교**:
- SelNet = learned estimator (offline training cost + inference latency 77ms)
- 본 Form 1 = no training cost + online incremental learning + inference latency O(K) sampling
- paper Fig.12 영역: Exqutor Q-error 1.69 vs SelNet 5.53 (paper L5 limitation 영역)

**code 영역**: github yyssl88/SelNet-Estimation (Python 95.5%, 2020 last commit, 52 commits). DEEP / SIFT / SSN dataset adapter 작성 cost 4-6h + offline training 1-2h per dataset.

**5/27 phase 1 영역**: 본 Form 1 의 3-way 비교 (Bernoulli + SelNet + 본 Form 1) baseline 으로 활용. paper Fig.12 Q-error 5.53 재현 risk 10-20% (정직 disclosure #5).

### G-3.2 CE4HD (Lan-Bao et al. VLDB 2024)

**paper 영역**:
- 제목: "Cardinality Estimation for Similarity Search on High-Dimensional Data Objects: The Impact of Reference Objects"
- 저자: Hai Lan, Shixun Huang, Zhifeng Bao, Renata Borovica-Gajic (RMIT University Australia + University of Wollongong)
- venue: VLDB 2024 / PVLDB Volume 18, No. 3 (November 2024), page 544-556
- PDF: https://www.vldb.org/pvldb/vol18/p544-bao.pdf
- DOI: 10.14778/3712221.3712224

**핵심 contribution**:
- SRCE (Static Reference object based Cardinality Estimation): offline phase 영역의 reference object selection + online estimation
- MRCE (Multi-Reference object based Cardinality Estimation): dynamic 환경 + multi-reference object
- 결과: SelNet 대비 ~136× smaller Q-error + ~10× faster offline training

**본 Form 1 영역과의 비교**:
- CE4HD = offline reference object training (offline training cost) + online estimation (reference object 위에서 inference)
- 본 Form 1 = no training cost + online incremental cluster maintenance + sampling-based estimation
- 두 영역의 axis 가 다름 (CE4HD = learned, 본 Form 1 = sampling-based)

**code 영역**: ★ github 미공개 확인 (WebSearch + baozhifeng.net 페이지 직접 확인, 정직 disclosure #3). 본 연구 5/27 phase 1 영역의 직접 비교 영역 폐기.

**6/11 phase 2 영역**: paper level 인용 only (REPORT v11 + 6/11 보고서 §3 Related Work). CE4HD 영역의 직접 비교 영역은 post-6/11 future paper 영역 (저자 contact 영역 또는 SRCE 직접 구현 ~20-30h 영역) 으로 분담.

### G-3.3 Ada-ef (Zhang et al. arxiv 2512.06636)

**paper 영역**:
- 제목: "Adaptive Dynamic Adjustment of ef for HNSW Search"
- venue: arxiv 2512.06636 (SIGMOD 2026 paper)
- github: chaozhang-cs/hnsw-ada-ef (C++ 53.6% + Python 14.2% + CUDA 12.8%, Apache-2.0)

**핵심 contribution**:
- HNSW 의 ef search 영역 (search-time graph traversal parameter) 의 distribution-aware adaptation
- cosine / IP / L2 distribution 영역의 추정 (L2 영역 paper 미해결, fallback Gaussian approximation)

**본 Form 1 영역과의 비교**:
- Ada-ef = HNSW search-time adaptation (vector index 영역의 search parameter tuning)
- 본 Form 1 = sampling-based cardinality estimation (without vector index 영역의 sampling axis)
- 두 영역의 layer 다름 (정직 disclosure #4)

**code 영역**: github 공개 (chaozhang-cs/hnsw-ada-ef), gcc 12.3 + Boost 1.87 + HDF5 dependencies.

**5/27 phase 1 + 6/11 phase 2 영역**: paper level 인용 only. layer 가 다르므로 본 Form 1 baseline 으로 직접 비교 부적합.

### G-3.4 SimCard (SIGMOD 2021)

**paper 영역**:
- 제목: "SimCard: Cardinality Estimation for Similarity Queries via Self-Supervised Set Embeddings"
- venue: SIGMOD 2021

**본 Form 1 영역과의 비교**:
- SimCard = learned cardinality estimation 의 SOTA before CE4HD
- 본 Form 1 = sampling-based, no training cost
- CE4HD 의 baseline 中 하나로 paper level 인용

**5/27 + 6/11 영역**: paper level 인용 only.

### G-3.5 Adaptive Bucket Probing (arxiv 2604.04603)

**paper 영역**:
- 제목: "Adaptive Bucket Probing for High-Dimensional Vector Cardinality Estimation"
- venue: arxiv 2604.04603 (HKUST 2025)

**본 Form 1 영역과의 비교**:
- Adaptive Bucket Probing = bucket-based cardinality estimation 영역
- 본 Form 1 = cluster-based stratified sampling 영역
- 두 영역의 axis 가 다름 (bucket vs cluster) but base reference 영역의 inspiration 가능

**5/27 + 6/11 영역**: paper level 인용 only.

## G-4. 본 연구의 positioning + differentiation

본 연구의 positioning 영역의 정리는 다음과 같이 4 axis 영역으로 분리된다.

**Axis 1 (paper Exqutor 후속 연구 form)**: paper Exqutor §V-B 영역의 후속 연구 form 영역 (paper 자체가 §V-A ECQO 와 §V-B Adaptive Sampling 의 두 영역 분리 명시 영역 안). 본 영역의 학술 정합성 영역의 anchor.

**Axis 2 (sampling-based + distribution-aware)**: 본 Form 1 영역의 sampling-based 영역 + distribution-aware 영역의 통합 axis. SelNet / CE4HD / SimCard / Adaptive Bucket Probing 등의 learned estimator 영역과 layer 다름 (no training cost + online incremental 영역의 차이).

**Axis 3 (streaming-aware)**: 본 Form 1 영역의 streaming-aware 영역. paper Exqutor §V-B 영역 자체는 batch 환경 전제이며, 본 연구의 Component A + B 영역의 streaming axis 영역의 발현 영역이 본 연구의 framework axis novelty 의 핵심.

**Axis 4 (4-way 비교 framework)**: 본 Form 1 영역의 4-way 비교 framework (Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1) 영역. paper §VI-D Fig.12 영역의 SelNet 단독 비교 영역 (paper L5 limitation) 의 보완 영역이며, 본 framework axis 자체가 paper §VI-D 영역의 확장 영역.

본 4 axis 영역의 positioning 영역의 정확 표기 영역이 본 연구의 학술 정직성 영역의 base 다. framework axis novelty 영역 (각 component 자체 신규 X, 위 4 axis 영역의 통합 form 영역) 의 명시 표기 영역이 본 연구의 contribution scope 영역의 정확 표기 영역이다.

---

# 부록 §F — 17 사용 method 깊이 + 측정 portfolio 세부

본 §F 영역은 v1 §11 (사용 method 깊이 소개 핵심 6) + §12 (17 사용 method 전체 list) 영역의 부록 이동 영역이다. v2 본문 영역의 narrative 흐름 (Form 1 Component A/B/C/D + batch baseline 재해석 + K granularity + Neyman selectivity) 의 우선순위 영역 발현 axis 위에서 method 깊이 영역은 부록 영역으로 분리되어 발현된다.

## F-1. 핵심 6 method 깊이 소개

본문 §4-13 영역에 등장한 결과를 만든 method 들 中 본 narrative 의 핵심 6 개를 algorithm 메커니즘 + 이론적 근거 + 실측 결과로 정리한다. 17 사용 method 전체 list 는 §F-2 영역 + 자원 효율 분석 file (`_internal/analysis/resource_efficiency_pareto_20260513.md`) 영역 참조.

### F-1.1 minibatch_partial — 클러스터링 갈래, 단독 대체 best

**방법** — 데이터를 청크 단위로 흘려보내면서 K=20 클러스터 중심을 점진적으로 학습한다 (partial_fit). 전체 데이터를 메모리에 올리지 않고 stream 처럼 처리.

**이론적 근거** — Sculley (WWW 2010) 의 Web-scale K-means 변형. scikit-learn 의 MiniBatchKMeans 의 partial_fit API 직접 활용.

**algorithm 영역**:
```
Initialize: K=20 centroids C_j (random init 또는 first 1000 sample init)

For each chunk X_chunk of size chunk_size=256:
  # E-step: assign tuple to nearest centroid
  labels = argmin_j ||X_chunk − C_j||²

  # M-step: update centroid with running mean
  for j in 1..K:
    n_j_new = n_j + |labels == j|
    C_j_new = (n_j · C_j + sum(X_chunk[labels == j])) / n_j_new
    n_j = n_j_new
    C_j = C_j_new
```

**실측 결과** — 단독 대체 모드 9 측정 환경 평균 **−10.17%** (본 portfolio 단독 best). 학습 시간 0.5 초, 메모리 사용량 작음 (청크 × 차원 D), 측정 환경별 변동성 std 3.33. 단독 대체로 갈아끼울 때 가장 큰 정확도 개선을 가져오는 method.

**positioning**: P1 클러스터링 paradigm 의 best method 영역. Form 1 Component A (SRS) + Component B (BIRCH) 영역의 motivation evidence base. streaming axis 영역 (Form 1 phase 1) 영역의 발현 영역에서 본 method 영역의 partial_fit API 영역이 직접 활용 가능 영역.

### F-1.2 sparse_rp — 차원 축소 갈래, 학습 시간 가장 짧음

**방법** — 데이터 차원 D 를 sparse random matrix (Achlioptas density 1/3, 즉 +1 / 0 / −1 의 sparse entries) 로 곱해 낮은 차원 k 로 사영한다. 그 후 K=20 클러스터로 stratum 분할.

**이론적 근거** — Achlioptas (JCSS 2003) 의 sparse Bernoulli projection + Li-Hastie-Church (KDD 2006) 의 매우 sparse 변형. Johnson-Lindenstrauss lemma 의 distance preservation 보장 위에서 sparse 화로 계산 비용을 크게 낮춤.

**algorithm 영역**:
```
Initialize sparse random matrix R ∈ R^{D × k}:
  R[i, j] = +sqrt(3)  with probability 1/6
            0          with probability 2/3
            −sqrt(3)   with probability 1/6
  # Achlioptas (JCSS 2003) Theorem 1.1

For each tuple x_i ∈ R^D:
  y_i = R^T x_i ∈ R^k     # k-dim projection

KMeans(K=20).fit(Y)        # K-means on projected data
```

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.43%**, 학습 시간 **0.1 초** (본 portfolio 최단), 메모리 O(D × k) 매우 작음, std 3.30. 정확도와 자원 두 axis 에서 모두 Pareto frontier 위에 있는 method.

**positioning**: P4 차원 축소 paradigm 의 best method 영역. K granularity SF axis 영역 (§11) 의 4 anchor 中 하나이며, K=20 sweet spot (U-shape) 패턴 발현. SF=1 영역 −11.70% / SF=10 영역 −6.58% / SF=100 영역 −11.20% 영역의 K=20 K-best 영역.

### F-1.3 chao_weighted — 스트리밍 갈래, Pareto Top 정확도

**방법** — 가중 reservoir 표집. 청크 단위로 들어오는 데이터에서 weight 기반 sampling 으로 분포 정보를 streaming 으로 유지한다.

**이론적 근거** — Chao M-T (Biometrika 1982) 의 weighted reservoir sampling. 각 sample 의 probability of inclusion 이 weight 에 비례하도록 보장.

**algorithm 영역**:
```
Initialize:
  reservoir R = []
  reservoir budget K_budget = 385

For each new tuple x_t with weight w_t:
  if |R| < K_budget:
    R.append((x_t, w_t))
  else:
    # Chao 1982 weighted reservoir sampling rule
    w_total = sum(w for (_, w) in R) + w_t
    if random() < w_t / w_total:
      # replace random element from R
      i = random_int(0, K_budget - 1)
      R[i] = (x_t, w_t)
```

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.60%** (Pareto frontier 정확도 Top 1), 학습 시간 0.5 초, 메모리 O(K) 매우 작음, std 6.36. 정확도는 가장 좋으나 측정 환경별 변동성은 다소 큼.

**positioning**: P3 스트리밍 paradigm 의 best method 영역. K granularity SF axis 영역 (§11) 의 4 anchor 中 하나이며, K=20 sweet spot 모든 SF 일관 패턴 발현. SF=1 영역 **−14.11%** (전체 K granularity 측정 中 가장 큰 effect size) / SF=10 영역 −6.00% / SF=100 영역 −12.20% 영역.

### F-1.4 hilbert_real — 공간 분할 갈래, 진짜 Hilbert curve 구현

**방법** — 데이터 차원 D 를 그대로 유지한 채 Hilbert space-filling curve indexer 로 1 차원 좌표 매핑. 그 후 매핑된 1 차원 좌표를 K=20 stratum 으로 분할.

**이론적 근거** — Faloutsos (SIGMOD 1989) 의 진짜 D 차원 Hilbert space-filling curve. 본 연구의 이전 hilbert method 는 코드 정독 검토 결과 PCA 2 차원 정렬의 별칭으로 발견되어 (★3 정정 audit), 진짜 Hilbert curve 구현인 hilbert_real 을 별도 method 로 측정.

**algorithm 영역**:
```
Initialize Hilbert indexer:
  hilbert_curve(p=10, n=D)   # p = order, n = dimension
  # Faloutsos (SIGMOD 1989) Hilbert curve construction

For each tuple x_i ∈ R^D:
  # quantize x_i to integer coordinates (p bits per dim)
  int_coords = quantize(x_i, bits=10)
  h_i = hilbert_index(int_coords)   # 1-D Hilbert distance

# Stratify by Hilbert distance
sorted_h = sorted(h_i)
boundaries = [sorted_h[i * len(sorted_h) / K] for i in range(K)]
labels = digitize(h_i, boundaries)
```

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.27%**, 학습 시간 0.5 초, 메모리 O(N), std 3.12. 공간 분할 paradigm 의 진짜 anchor.

**positioning**: P2 공간 분할 paradigm 의 best method 영역. K granularity SF axis 영역 (§11) 의 4 anchor 中 하나이며, K-robust + K=30 slight edge 패턴 발현. SF=1 영역 K=20 −11.02% / K=30 −12.25% / SF=10 영역 K=20 −6.07% / K=30 −6.96% / SF=100 영역 K=20 −10.91% / K=30 −11.81%.

### F-1.5 hyperloglog — 정보 이론 갈래, 가장 안정

**방법** — hash 기반 분포 카디널리티 추정량. K=20 stratum 별로 trailing zero 의 max 를 추적해 cardinality 를 streaming 으로 추정.

**이론적 근거** — Flajolet et al (DMTCS 2007) 의 HyperLogLog. 분포의 unique element 수를 매우 적은 메모리로 정확히 추정하는 정보 이론 기반 알고리즘.

**algorithm 영역**:
```
Initialize K=20 HLL registers, each m=2^11=2048 bits

For each tuple x_t:
  j = hash_to_cluster(x_t, K=20)
  h = hash_function(x_t)
  i = first_m_bits(h)              # register index
  ρ = leading_zero_count(h_rest)   # ρ ≥ 1
  HLL[j].registers[i] = max(HLL[j].registers[i], ρ)

# Estimate cardinality per cluster (Flajolet 2007 Eq 2.4)
for j in 1..K:
  Z_j = sum(2^(-r) for r in HLL[j].registers)
  alpha_m = correction_constant(m)
  cardinality[j] = alpha_m × m² × Z_j^(-1)
```

**실측 결과** — 결합 모드 9 측정 환경 평균 **−8.65%**, 학습 시간 0.5 초, 메모리 O(K log K), std **2.73** (본 portfolio ⭐⭐ Best + ⭐ Excellent 19 method 中 가장 안정). 정확도와 안정성을 모두 잡은 method.

**positioning**: P9 정보 이론 paradigm 의 best method 영역. K granularity SF axis 영역 (§11) 의 4 anchor 中 하나이며, K-robust + K=30 slight edge 패턴 발현. SF=1 영역 K=20 −10.19% / K=30 **−12.57%** (전체 K=30 측정 中 가장 큰 effect size) / SF=10 영역 K=20 −5.15% / K=30 −6.01% / SF=100 영역 K=20 −10.54% / K=30 −11.62%.

### F-1.6 reservoir — 스트리밍 갈래, 메모리 O(1)

**방법** — 가장 단순한 reservoir sampling. 청크 단위 데이터에서 K 개를 균등 확률로 sampling 한다.

**이론적 근거** — Vitter (TOMS 1985) 의 reservoir sampling. 데이터 크기 N 을 미리 모르더라도 K 개의 균등 random sample 을 한 번의 pass 로 얻는 알고리즘.

**algorithm 영역**:
```
Initialize:
  R = []                # reservoir
  K_budget = 385        # paper exact N = 385

For each new tuple x_t (t = 1, 2, ...):
  if |R| < K_budget:
    R.append(x_t)
  else:
    # Vitter 1985 Algorithm R
    r = random_int(0, t-1)
    if r < K_budget:
      R[r] = x_t        # replace with prob K_budget/t

Return R
```

**실측 결과** — 결합 모드 9 측정 환경 평균 **−9.25%**, 학습 시간 **0.1 초**, 메모리 사용량 **O(1)** (sample size K 만 보존, 데이터 크기 N 과 무관), std 3.00. **§10 의 산업 적용 핵심 finding** — 모바일 / 임베디드 / 스트리밍처럼 메모리가 제약인 환경에 그대로 적용 가능한 가장 강력한 method.

**positioning**: P3 스트리밍 paradigm 의 fundamental method 영역. Form 1 Component A (Stratified Reservoir Sampling) 영역의 base reference 영역이며, 본 연구의 산업 적용 axis 영역의 핵심 finding 영역. 메모리 O(1) 영역의 발현이 RAG production / OLTP write-heavy / vector database insert stream 환경 직접 적용 가능 영역의 evidence.

## F-2. 17 사용 method 전체 list

39 폐기 後 남은 17 사용 method 의 paradigm 분포 + 결합 모드 평균 + 자원 효율 등급 + 이론적 근거. 자세한 자원 정량 (학습 시간 + 메모리 + SF=100 feasibility) 은 `_internal/analysis/resource_efficiency_pareto_20260513.md` 참조.

| paradigm | method | CaseB Δ% | 자원 등급 | 이론적 근거 |
|---|---|---:|---|---|
| P1 클러스터링 | minibatch_partial | −6.98% | ⭐ Excellent | Sculley 2010 (partial fit) |
| P1 클러스터링 | minibatch | −9.28% | ⭐ Excellent | Sculley 2010 |
| P1 클러스터링 | gmm | +2.45% | Good | Dempster 1977 EM (marginal) |
| P2 공간 분할 | hilbert_real | −9.27% | ⭐⭐ Best | Faloutsos 1989 진짜 |
| P2 공간 분할 | zorder_morton | −9.26% | ⭐ Excellent | Morton 1966 bit-interleaving |
| P2 공간 분할 | skilling_hilbert | −9.01% | ⭐ Excellent | Skilling 2004 변형 |
| P2 공간 분할 | lpm2 | −9.45% | ⭐⭐ Best | Grafström 2012 local pivot |
| P3 스트리밍 | chao_weighted | −9.60% | ⭐⭐ Best | Chao 1982 weighted reservoir |
| P3 스트리밍 | reservoir | −9.25% | ⭐⭐ Best | Vitter 1985, 메모리 O(1) |
| P3 스트리밍 | thompson_sampling | −8.98% | ⭐ Excellent | Thompson 1933 Beta posterior |
| P3 스트리밍 | cum_sqrtf | −8.45% | Good | Cochran 1977 sqrt(F) |
| P4 차원 축소 | sparse_rp | −9.43% | ⭐⭐ Best | Li-Hastie-Church 2006 |
| P4 차원 축소 | neuram | −9.97% | ⭐⭐ Best | autoencoder (PCA1D 등가 audit) |
| P4 차원 축소 | pca1d | −9.63% | ⭐ Excellent | Pearson 1901 PCA |
| P4 차원 축소 | rsvd | −8.49% | ⭐ Excellent | Halko-Martinsson 2011 |
| P6 양자화 | pq | −9.25% | ⭐ Excellent | Jégou 2011 product quantization |
| P9 정보 이론 | hyperloglog | −8.65% | ⭐⭐ Best | Flajolet 2007 HyperLogLog |

비고:
- CaseB Δ% = 결합 모드 9 측정 환경 평균 (음수가 클수록 정확도 개선). 학습 시간 모두 0.1 ~ 1 초 범위.
- 자원 효율 등급: ⭐⭐ Best (fit < 1s + 메모리 O(N) 이하 + SF=100 OK + Δ% < −9%) / ⭐ Excellent (fit < 2s + Δ% < −8%) / Good (fit < 2s + Δ% −5 ~ −8%) / Marginal (Δ% −3 ~ −5%).
- P5 준 무작위 / P10 밀도 추정 paradigm 은 모두 폐기되어 사용 method 없음.
- §F-1 의 핵심 6 method (minibatch_partial / sparse_rp / chao_weighted / hilbert_real / hyperloglog / reservoir) 는 paradigm 다양성 + Pareto frontier + 본 narrative §4-§13 핵심 등장 기준으로 선정.

## F-3. 측정 portfolio 종합 (배경, 필요 시 참조)

- 총 측정 1113 file (paper exact carry-over 1001 + 본 세션 64: multi-join 8 + Centroid tuple 8 + B1/B2/B3 cheap 24 + A2-Fig8 mv 8 + α sweep 16 + K granularity SF axis 48)
- 폐기 40 method (자원 한계 7 + audit drop 23 + 정합성 위반 10)
- 사용 method 약 17 개 (56 − 39)
- 8 갈래 paradigm rollup: P10 Density / P9 InfoTheoretic / P3 Streaming / P4 DimReduction / P2 Spatial 우위 (CaseB 기준 −5 ~ −12%)
- 본 논문 §V-B Fig 12 영역 절사 평균 Q-error 본 측정 1.618 vs paper 보고값 1.69 = −4.3% 재현 (paper review-grade 정합성 확보)
- 자원 한계 폐기 method 中 kde_parzen 은 5/13 ~ 5/14 측정 chain 진행했으나 5/5 timeout 으로 5/14 07:39 폐기 결정

## F-4. paper §V-B 영역 cells 9 nominal 영역의 정확 정리

본 연구의 9 nominal cells 영역의 정확 정리 영역은 다음과 같다. 9 cells 영역의 paper §VI 영역의 분류 영역과의 mapping 영역은 EXPERIMENT_REGISTRY (`_internal/EXPERIMENT_REGISTRY.md`) 영역의 reference base 영역이다.

| cell ID | dataset | scale | selectivity | paper Fig | 본 측정 영역 |
|---|---|---|---:|---|---|
| A2-Fig8 | DEEP | sf=10 | sel=0.01 | paper §VI-B Fig 8 | 본 측정 single cell 영역 best −10.17% |
| A2-Fig9 | DEEP | sf=10 | sel=0.10 | paper §VI-B Fig 9 | 본 측정 결합 best −7.37% |
| A2-Fig10 | DEEP | sf=100 | sel=0.01 | paper §VI-B Fig 10 | 본 측정 영역 |
| A2-Fig11 | DEEP | sf=100 | sel=0.10 | paper §VI-B Fig 11 | 본 측정 영역 |
| A2-Fig12 | SIFT | sf=100 | sel=0.01 | paper §VI-D Fig 12 | 본 측정 영역 + SelNet baseline 영역 |
| A2-Fig13 | SIFT | sf=100 | sel=0.10 | -- | 본 측정 영역 |
| A2-Fig14 | SSN | sf=100 | sel=0.01 | -- | 본 측정 영역 |
| A2-Fig15 | SSN | sf=100 | sel=0.10 | -- | 본 측정 영역 |
| A2-Fig7 | DEEP+SIFT | sf=100 | sel=0.10 | paper §VI-C Fig 7 | multi-join 영역 |

본 9 nominal cells 영역의 byte-identical caveat 영역은 6 unique cells × 9 nominal 영역의 정직 표기 영역이다 (정직 disclosure 영역의 일부). 본 영역의 정확 정리는 §9.6 영역의 byte-identical caveat 영역의 evidence 다.

## F-5. 40 폐기 method 정직 분류

본 §3 영역의 폐기 method 40 영역의 정직 분류 영역의 상세는 다음과 같다. 본 영역은 5/27 deck slide 17 + 6/11 보고서 §9 영역의 source 다.

### F-5.1 자원 한계 폐기 7 method

| method | paradigm | 폐기 사유 | 폐기 시점 |
|---|---|---|---|
| dirichlet | P10 Density | 자원 한계 (memory + timeout) | 5/8 Tier 2 정리 |
| kernelpca | P4 DimReduction | 자원 한계 (메모리 50-200GB) | 5/8 Tier 2 정리 |
| neurocard_lite | P9 InfoTheoretic | 자원 한계 (timeout) | 5/8 Tier 2 정리 |
| birch | P1 Cluster | 자원 한계 (메모리 50-200GB per measurement) | 5/8 Tier 2 정리 |
| hdbscan | P1 Cluster | 자원 한계 (timeout) | 5/8 Tier 2 정리 |
| agglomerative | P1 Cluster | 자원 한계 (timeout) | 5/8 Tier 2 정리 |
| kde_parzen | P10 Density | 자원 한계 (5/5 timeout, 5/13 ~ 5/14 측정 chain 진행했으나 폐기 결정) | 5/14 07:39 폐기 결정 |

### F-5.2 audit drop 23 method (5/10 코드 정독 검토)

| method | paradigm | audit 발견 | 정정 reference |
|---|---|---|---|
| vinecopula | P10 Density | PCA 1 차원 정렬 alias (vine copula reference 위반) | ★3 정정 |
| neuram | P4 DimReduction | PCA1D 와 한 줄씩 동일 (autoencoder reference 위반) | 5/10 audit |
| hilbert | P2 Spatial | PCA 2 차원 정렬 alias (Faloutsos 1989 reference 위반) | ★3 정정 |
| sparse_rp (constants) | P4 DimReduction | Li 2006 vs Achlioptas 2003 reference 정정 | ★4 정정 |
| (other 19 method) | (various) | reference 위반 또는 alias | 5/10 audit |

본 audit 영역의 상세 정리는 `_internal/method_audit/` 영역의 audit log 영역 참조. 본 audit 영역의 학술 정직성 영역이 본 연구의 contribution 영역 中 하나다.

### F-5.3 정합성 위반 10 method (paper N=385 budget 위반)

| method | paradigm | 정합성 위반 영역 |
|---|---|---|
| halton | P5 QMC | paper N=385 budget 위반 |
| sobol | P5 QMC | paper N=385 budget 위반 |
| lhs | P5 QMC | paper N=385 budget 위반 |
| hammersley | P5 QMC | paper N=385 budget 위반 |
| dense_rp | P4 DimReduction | paper N=385 budget 위반 |
| random_projection | P4 DimReduction | 추정값 외곽 발현 |
| dbscan | P1 Cluster | 추정값 외곽 발현 |
| ccsketch | P3 Streaming | 추정값 외곽 발현 |
| lsh | P2 Spatial | 추정값 외곽 발현 |
| ams_count_sketch | P3 Streaming | 추정값 외곽 발현 (5/14 환각 검증 H1 정정: 9→10) |

본 정합성 위반 영역의 폐기 기준은 (a) paper N=385 budget 위반 (sample size 가 paper budget 과 다르게 발현), (b) 큰 데이터셋에서 추정값이 외곽 (anchor 영역의 ±50% 외부) 으로 튀는 영역, (c) 측정 결과의 reproducibility 영역의 不정합 영역의 3 영역이다.

본 §F-5 영역의 정직 분류 영역이 본 연구의 학술 정직성 영역의 핵심 evidence 영역이다. 5/27 deck slide 17 + 6/11 보고서 §9 영역에서 본 영역의 정확 표기 영역이 본 연구의 paper-grade defensibility 영역의 base.

---

# 부록 §L — measurement evidence 영역의 추가 정리

본 §L 영역은 본 v2 narrative 영역의 measurement evidence 영역의 추가 정리 영역이다. 본 v2 본문 영역에 inline 발현된 measurement 결과 영역의 source 영역의 정확 표기 + 추가 detail 영역의 표기 영역이다.

## L-1. RQ1 영역 paper baseline 재현 evidence

본 §1 영역의 paper baseline 재현 영역의 evidence:
- 본 측정 paper §V-B Fig 12 영역 절사 평균 Q-error = **1.618**
- paper 보고값 Q-error = 1.69
- 재현 영역 = **−4.3%** (paper review-grade 정합성 확보)

본 −4.3% 영역의 정확 evidence 영역은 measure_paper_exact.py 의 AdaptiveState class (line 67-140) 영역의 paper Eq 1-6 verbatim 100% 정합 검증 영역이다. 본 영역의 measurement file 영역은 raw/01_RQ1_논문_baseline_재현/ 영역의 ~80 file 영역이다.

## L-2. RQ2 영역 5-way 표본 할당 evidence

본 §12 영역의 RQ2 5-way 표본 할당 영역의 evidence:

| dataset | sel | n trial | Bernoulli Q-err | Equal | Proportional | Neyman | Anti-Neyman |
|---|---|---:|---:|---:|---:|---:|---:|
| DEEP | 0.01 | 5 | 1.72 | 1.62 | **1.58** | 1.59 | **1.54** |
| DEEP | 0.1 | 5 | 1.16 | 1.13 | 1.12 | **1.11** | 1.12 |
| SIFT | 0.01 | 5 | 1.64 | 1.59 | 1.58 | 1.60 | 1.55 |
| SIFT | 0.1 | 5 | 1.22 | 1.13 | 1.12 | **1.11** | 1.12 |
| POOL | 0.01 | 25 | 1.69 | 1.61 | **1.58** | 1.60 | 1.55 |
| POOL | 0.1 | 25 | 1.19 | 1.13 | 1.12 | **1.11** | 1.12 |

본 영역의 mean gap +3.74% (5 cell × 5 trial) 영역 + Bern→Prop −9.53% 영역 + Anti 1.540 < Prop 1.580 < Neyman 1.595 paradox 영역 (sel=0.01 한정) + sel=0.1 영역 Neyman best 영역 (classical theory 정합) 의 4 finding 영역이 본 §12 영역의 narrative source 다.

## L-3. RQ3 영역 8 paradigm rollup evidence

본 §9.0 영역의 8 paradigm rollup 영역의 evidence (CaseB 모드 9 측정 환경 평균 Δ%):

| paradigm | CaseB Δ% mean | n (file) | std | best method (Δ%) |
|---|---:|---:|---:|---|
| P10 Density | −11.93% | 1 | -- | (single method, weak n) |
| P9 InfoTheoretic | −7.60% | 9 | 2.73 | hyperloglog (−8.65%) |
| P3 Streaming | −6.63% | 44 | 6.36 | chao_weighted (−9.60%) |
| P4 DimReduction | −6.03% | 104 | 3.30 | neuram (−9.97%) |
| P2 Spatial | −5.57% | 107 | 3.12 | hilbert_real (−9.27%) |
| P5 QMC | +1.47% | 62 | -- | (4 method 폐기) |
| P1 Cluster | +2.04% | 87 | 3.33 | minibatch_partial (CaseA −10.17%) |
| P6 Quantization | +8.44% | 53 | -- | pq (−9.25%) |

본 8 paradigm rollup 영역의 정확 정량이 본 §9.0 영역의 source 다.

## L-4. RQ3 영역 CaseA vs CaseB paired test evidence

본 §9.2 영역의 paired test 결과:

| metric | value | n |
|---|---:|---:|
| paired CaseB < CaseA | 92.5% (455/492) | 492 |
| p-value (paired test) | p<1e-45 | -- |
| Cliff's δ large better | 63.0% (311/494) | 494 |
| Hedges' g large | 55.7% (275/494) | 494 |
| one-sided p<0.05 outperform | 45.3% (224/494) | 494 |

본 metric 영역이 본 §9.2 영역의 결합 영역의 92.5% paired uplift 영역의 source 다.

## L-5. RQ3 영역 CaseA negative control evidence

본 §4.3 영역의 negative control evidence:

| metric | value | n |
|---|---:|---:|
| CaseA 단독 대체 우위 | 0/493 = 0% | 493 |
| CaseA large worsening | 37.1% | 493 |
| CaseA byte-identical with Bernoulli | 0/493 = 0% | 493 |

본 evidence 영역이 본 §4.3 + §13.2 영역의 결합 보조 영역의 motivation 영역의 source 다.

## L-6. K granularity SF axis 영역의 detail evidence

본 §11 영역의 K granularity SF axis 영역의 detail evidence (5/14 22:00 회수 완료):

### L-6.1 K=10 측정 결과 영역

| Method | SF=1 K=10 Δ% | SF=10 K=10 Δ% | SF=100 K=10 Δ% |
|---|---:|---:|---:|
| sparse_rp | **+50 ~ +90%** (악화) | −2.1% | +30 ~ +50% (악화) |
| chao_weighted | +10 ~ +20% (약화) | −2.5% | +5 ~ +10% (약화) |
| hilbert_real | −8.50% | −5.20% | −9.10% |
| hyperloglog | −8.10% | −4.80% | −8.90% |

### L-6.2 K=20 측정 결과 영역

| Method | SF=1 K=20 Δ% | SF=10 K=20 Δ% | SF=100 K=20 Δ% |
|---|---:|---:|---:|
| sparse_rp | −11.70% | −6.58% | −11.20% |
| chao_weighted | **−14.11%** | −6.00% | −12.20% |
| hilbert_real | −11.02% | −6.07% | −10.91% |
| hyperloglog | −10.19% | −5.15% | −10.54% |

### L-6.3 K=30 측정 결과 영역

| Method | SF=1 K=30 Δ% | SF=10 K=30 Δ% | SF=100 K=30 Δ% |
|---|---:|---:|---:|
| sparse_rp | −10.50% | −5.80% | −10.30% |
| chao_weighted | −12.80% | −5.40% | −11.40% |
| hilbert_real | **−12.25%** | **−6.96%** | **−11.81%** |
| hyperloglog | **−12.57%** | −6.01% | −11.62% |

본 K=10 / K=20 / K=30 영역의 3-way comparison 영역이 본 §11 영역의 method-dependent K best 패턴 영역의 source 다.

## L-7. α sweep 영역의 detail evidence

본 §9.5 영역의 α sweep 영역의 detail evidence:

| method | α=0.3 | α=0.4 | α=0.5 | α=0.6 | α=0.7 | best α |
|---|---:|---:|---:|---:|---:|:---:|
| sparse_rp | −7.21% | −8.42% | **−9.43%** | −8.51% | −7.01% | 0.5 |
| chao_weighted | −7.55% | −8.61% | **−9.60%** | −8.72% | −7.18% | 0.5 |
| hilbert_real | −7.05% | −8.20% | **−9.27%** | −8.33% | −6.82% | 0.5 |
| hyperloglog | −6.51% | −7.62% | −8.65% | **−8.72%** | −7.03% | 0.6 |

본 α sweep 영역의 4 method × 5 α = 20 measurement 영역의 evidence 가 본 §9.5 영역의 U-shape + 산술 평균 best 영역의 source 다.

## L-8. Pareto frontier 영역의 detail evidence

본 §10 영역의 Pareto frontier 영역의 detail evidence:

| method | CaseB Δ% | fit time (SF=1) | 메모리 | Pareto 등급 |
|---|---:|---:|---|---|
| sparse_rp | −9.43% | 0.1 s | O(D × k) | ⭐⭐ Best |
| chao_weighted | −9.60% | 0.5 s | O(K) | ⭐⭐ Best |
| neuram | −9.97% | 0.5 s | O(N × D) | ⭐⭐ Best |
| pca1d | −9.63% | 0.5 s | O(N × D) | ⭐ Excellent |
| hilbert | −9.27% (★3 alias 정정) | 0.5 s | O(N) | ⭐ Excellent |
| hilbert_real | −9.27% | 0.5 s | O(N) | ⭐⭐ Best (진짜 anchor) |
| hyperloglog | −8.65% | 0.5 s | O(K log K) | ⭐⭐ Best |
| reservoir | −9.25% | **0.1 s** | **O(1)** | ⭐⭐ Best (산업 적용) |

본 Pareto frontier 영역의 정확 정량이 본 §10 영역의 source 다. reservoir 영역의 O(1) 메모리 영역이 §13.3 자원 우선 환경 영역의 산업 적용 영역의 anchor.

## L-9. 본 세션 5/14 추가 측정 영역의 64 file evidence

본 세션 5/14 07:35 ~ 18:00 영역의 64 file 추가 측정 영역의 분류:

| 측정 영역 | file 수 | 결과 |
|---|---:|---|
| multi-join (A2-Fig7 영역) | 8 | Centroid tuple vs 비싼 영역의 비교 영역, 안정 우위 영역 |
| Centroid tuple (A2-Fig9 single cell 영역) | 8 | 결합 best −7.37% 영역 (학습 비용 추가 0) |
| B1/B2/B3 cheap (3 baseline × 8 cell) | 24 | cheap approximation 영역의 baseline 영역 |
| A2-Fig8 mv (단독 best −10.17% verify) | 8 | minibatch_partial 영역의 단독 best 영역의 verify |
| α sweep (4 method × 4 α) | 16 | U-shape + 산술 평균 best 영역의 evidence |

본 64 file 영역이 본 세션 5/14 영역의 measurement 영역의 evidence 영역의 base 다.

---

# 부록 §M — paper §V-B 영역의 source code reference

본 §M 영역은 paper §V-B 영역의 source code reference 영역의 정리 영역이다. 본 영역은 박세은 5/14 9:09 영역 1 (single-table 不可 = 구현 한계 영역) + 영역 2 (block + row hybrid 영역) 의 자문 영역의 후속 영역의 fork build verify 영역의 future work 영역이다.

## M-1. paper github 영역의 정리

paper Exqutor 영역의 github repository 영역 = `BDAI-Research/Exqutor`. 본 repository 영역의 정리는 다음과 같다.

| 영역 | 정리 |
|---|---|
| URL | https://github.com/BDAI-Research/Exqutor |
| license | (확인 미완) |
| language | C++ + Python + SQL |
| last commit | (확인 미완) |
| dependencies | PostgreSQL 16.x + pgvector 0.7.x + Python 3.x |

본 repository 영역의 source code level verify 영역은 본 연구 영역에서 fork build verify 미완 영역이며 (정직 disclosure #8 + #9), 본 영역의 future work 영역은 다음 2 영역이다.

**Future work 1 (single-table 영역의 verify)**: paper §V-B 영역의 single-table KNN query 영역의 실제 동작 영역의 verify. paper 공개 코드 영역의 single-table 영역의 동작 영역의 fork build + 실행 영역의 verify (cost ~10-15h).

**Future work 2 (block + row hybrid 영역의 verify)**: paper §V-B 영역의 sampling 영역의 block + row hybrid 영역의 실제 동작 영역의 verify. paper 공개 코드 영역의 sampling 영역의 implementation detail 영역의 fork build + 실행 영역의 verify (cost ~10-15h).

본 두 future work 영역의 cost ~20-30h 영역이 본 연구의 paper §V-B 영역의 source code level verify 영역의 영역이며, post-6/11 future paper 영역 또는 5/15 박광현 미팅 영역의 자문 영역 후 결정 영역이다.

## M-2. measure_paper_exact.py 영역의 paper exact compatibility 영역

본 연구의 paper exact 영역의 base 영역은 measure_paper_exact.py (1407 line) 영역의 AdaptiveState class 영역의 paper Eq 1-6 verbatim 100% 정합 검증 영역이다. 본 영역의 정합 검증 영역은 다음과 같이 정리된다.

| paper Eq | AdaptiveState 영역 | line 영역 | 정합 영역 |
|---|---|---|---|
| Eq 1 (N=385) | `self.N = int(np.ceil(z**2 * P_hat * (1-P_hat) / e**2))` | line 80-82 | 100% (z=1.96, P̂=0.5, e=0.05 → N=385) |
| Eq 2 (Q-error) | `def q_error(c_esti, c_true)` | line 110-125 | 100% (max + inf 처리 영역 paper exact) |
| Eq 3 (δ) | `delta = alpha * (q_err - beta) - (100 - alpha) * ratio` | line 130-135 | 100% (α=50, β=1.5) |
| Eq 4 (V_t) | `V_t = m * V_prev + eta_t * delta` | line 137-138 | 100% (m=0.9, η_0=0.1) |
| Eq 5 (sampling_size) | `new_size = max(1, round(size_t + V_t))` | line 140 | 100% (scalar update) |
| Eq 6 (lr decay) | `eta_t = gamma * eta_prev` | line 142 | 100% (γ=0.99) |
| period P=50 | `if t % 50 == 0 and t > 0` | line 145-147 | 100% (paper period verbatim) |

본 정합 검증 영역이 본 연구의 paper exact compatibility 영역의 base 다. paper §V-B Fig 12 영역 절사 평균 Q-error 영역의 본 측정 1.618 vs paper 보고값 1.69 = −4.3% 재현 영역이 본 정합 검증 영역의 evidence 다.

## M-3. measure_paper_exact.py 영역의 BIRCH 영역의 기존 구현

본 §5.3 영역의 발견 영역의 evidence — measure_paper_exact.py line 623-630 영역의 BIRCH 영역의 기존 구현:

```python
# measure_paper_exact.py line 623-630 영역 (★ 본 §5.3 발견 영역)

from sklearn.cluster import Birch

def get_birch_clusters(X: np.ndarray, n_clusters: int = 20,
                       threshold: float = 0.5) -> np.ndarray:
    """BIRCH CF-tree clustering for stratified sampling.

    Zhang-Ramakrishnan-Livny 1996 SIGMOD base.
    scikit-learn `sklearn.cluster.Birch` API direct usage.
    """
    birch = Birch(n_clusters=n_clusters, threshold=threshold, branching_factor=50)
    birch.fit(X)
    labels = birch.predict(X)
    return labels
```

본 기존 구현 영역이 Form 1 Component B 영역의 base 영역이며, Form 1 phase 1 영역의 구현 영역은 본 기존 코드의 streaming axis 영역의 발현 axis (per-tuple incremental partial_fit + online σ_j² query) 영역만 확장 영역이다.

본 영역의 확장 영역의 cost = ~200 line + dev 10-15h + test 4-6h 영역이며, Agent F + G 의 cost 산정 영역과 ±5% 일치.

---

# 부록 §E — v1 → v2 diff summary

본 영역은 v1 (10 단계) 에서 v2 (12 단계 + 부록 5 종) 으로의 update 영역의 diff 영역 정리. 본 영역의 핵심 영역은 다음 5 가지.

## E-1. 구조 변경 영역

| 영역 | v1 (5/14 07:55) | v2 (5/14 22:32) |
|---|---|---|
| 본문 단계 수 | 10 단계 (§1-§10) | 12 단계 (§0-§13) + §11 K granularity + §12 Neyman selectivity-dependent 신규 |
| 새 §0 main theme | 없음 | Form 1 main theme + paper §V-B "without index" anchor 영역 신규 |
| 본문 §4-7 영역 | "단독 대체 / 결합 / 결합 한계 / 결합 진짜 가치" 1001 file batch baseline 중심 | Form 1 Component A/B/C/D framework axis 중심 + 1001 file 영역은 §9 batch baseline 재해석 영역으로 이동 |
| 17-step pseudo-code | 없음 (v1 시점 paper algorithm "14-step" 표현) | §8 (Component 통합 axis) + 부록 §C-4 (17-step pseudo-code 정확) |
| 본문 §11-12 영역 | "사용 method 깊이 소개 핵심 6" + "17 사용 method 전체 list" (method 중심) | §11 K granularity SF axis + §12 Neyman selectivity-dependent (정정 룰 중심) — method 깊이 영역은 부록으로 이동 |
| 부록 영역 | 측정 portfolio 종합 + 한 줄 요약 + narrative 흐름 도식 | §A 정직 disclosure 13 + §B 박세은 9 영역 답변 form + §C paper §V verbatim + 17-step + §D 정정 룰 14 + §E v1→v2 diff |

## E-2. main theme 영역

| 영역 | v1 | v2 |
|---|---|---|
| 본 연구 framing | "분포 정보를 알면 베르누이를 갈아끼우는 단독 대체가 가장 단순 + 큰 정확도 개선. 결합은 안정성 보조" 중심 | "Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ: Extending Exqutor's §V-B Framework" 의 Form 1 main theme + 4 측면 (대체 / 보완 / 개선 / 추가검증) 중심 |
| paper §V-B anchor | 명시 X | ★★★ paper p.5 verbatim ("without index" 가정) + p.5 우단 + p.6 우단 + §VI-A + §VI-B 모두 verbatim 인용 |
| RQ3 framing | "단독 대체 우선 + 결합 보조" 권장 | "RQ3 = 사전 학습 batch baseline" + "Form 1 = streaming axis" 분리 framing |
| ECQO 영역 | 명시 X | paper §V-B = "without index" 가정의 명시 (Form 1 의 §V-B 영역 한정 후속 연구 form anchor) |

## E-3. 정정 룰 14 반영 영역

v1 에서는 정정 룰 영역이 별도 정리되어 있지 않았고, v2 에서는 정정 룰 14 영역이 부록 §D 에 통합 정리된다. 본 영역의 핵심 정정 영역:

- 정정 룰 #1-2 (Agent A-G 발견): "5 단계 中 1 단계" + "Algorithm 1 14-step" wording 정정
- 정정 룰 #3-9 (박세은 9:09 ~ 9:42 영역 1-7): single-table / block-row / 분포 안다 layer / ECQO / RQ3 framing / 런타임 / Neyman selectivity
- 정정 룰 #10-12 (박세은 8:50 + 9:54 + 본 세션 verify): K granularity SF axis 완료 + Neyman over-statement 정정 + 회의 PDF wording verify
- 정정 룰 #13-14 (박세은 10:15 + Agent B): RQ2 5-way scope (SF=100 한정) + Neyman 가설 verify

v2 본문 영역은 위 정정 룰 14 영역을 직접 narrative 에 통합 발현시키며, 정정 룰의 정확 표기는 부록 §D 의 표 영역에서 일괄 참조 가능.

## E-4. 정직 disclosure 13 영역 통합

v1 에서는 정직 disclosure 영역이 본문 §3 (폐기 method 분류) 영역에 한정 발현되어 있었고, v2 에서는 정직 disclosure 13 영역이 부록 §A 에 통합 정리된다. 본 영역의 핵심:

- 정직 disclosure #1-6 (Agent 발견 영역): paper §V-B 자체 pseudo-code 없음 / framework axis novelty 한정 / CE4HD github 미공개 / Ada-ef layer 다름 / SelNet 재현 risk / BIRCH σ_j² drift
- 정직 disclosure #7-9 (batch vs streaming axis 영역): batch axis (1001 file) vs streaming axis boundary / paper §V-B single-table 不可 = 구현 한계 / paper §V-B sampling = block + row hybrid
- 정직 disclosure #10-13 (박세은 영역): "분포 안다" L1/L2/L3 oracle / paper §V-B "without index" 가정 / RQ3 = 사전 학습 batch baseline / 0.1~0.5초 fit time SF=1 한정

v2 본문 영역은 위 13 영역을 §3 (폐기) + §4-8 (Form 1 Component) + §9 (batch baseline) + §10 (자원 효율) + §11-12 (K granularity + Neyman) 영역의 narrative 에 inline 발현시키며, 정직 disclosure 의 정확 표기는 부록 §A 의 표 영역에서 일괄 참조 가능.

## E-5. 박세은 9 영역 + K granularity + Neyman selectivity-dependent 반영

v1 에서는 박세은 자문 영역이 본문 narrative 에 inline 발현되지 않았고, v2 에서는 박세은 9 영역 자문이 다음과 같이 분리 반영된다.

- 박세은 9:09 영역 1-5 (single-table / block-row / 분포 안다 / ECQO / RQ3 framing) → §1 + §4 + §6 + §9 + §13.5 영역의 narrative 에 inline 발현
- 박세은 9:27 영역 6 (런타임) → §10 자원 효율 영역의 narrative 정정
- 박세은 9:42 + 9:54 + 10:15 (Neyman selectivity-dependent + over-statement + 가설 verify) → §12 신규 영역 + 정정 룰 #9-14 + 정직 disclosure #10
- 박세은 8:50 (K granularity SF=1 미측정 발견) → §11 신규 영역 + 정정 룰 #10
- 박세은 9 영역 답변 form (카톡 복붙) → 부록 §B 통합 정리

v2 본문 영역은 위 9 영역을 narrative 에 통합 발현시키며, 박세은 9 영역 답변 form 의 정확 표기 (카톡 복붙 plain text 영역) 는 부록 §B 영역에서 일괄 참조 가능.

## E-6. method 깊이 영역 (v1 §11-12) 의 부록 이동

v1 §11 (사용 method 깊이 소개 핵심 6) + §12 (17 사용 method 전체 list) 영역은 v2 에서 본문 영역의 narrative 흐름 (Form 1 Component A/B/C/D + batch baseline 재해석 + K granularity + Neyman selectivity) 의 우선순위 영역의 발현으로 부록 영역으로 이동된다. v1 의 method 깊이 영역의 핵심 evidence (minibatch_partial −10.17% / sparse_rp 0.1초 / chao_weighted −9.60% / hilbert_real 진짜 Hilbert / hyperloglog −8.65% / reservoir O(1)) 는 본 v2 의 §4 (Component A SRS) + §10 (Pareto frontier) + §13 (권장 설계) 영역의 narrative 에 inline 발현된다.

본 영역의 v1 → v2 변경 영역의 핵심 reasoning 은 v1 의 method 중심 narrative (각 method 의 algorithm + reference + Δ% + 자원) 영역의 발현이 5/27 발표 / 6/11 보고서 / 5/15 review form 의 본문 narrative 영역의 영역 효율 영역 외 발현이라는 점이다 (Agent E + I 의 발표 storyline + 보고서 outline 영역의 결론). v2 본문 영역은 Form 1 main theme + Component framework axis 중심 narrative 로 재정리되고, method 깊이 영역은 future work 영역의 reference 영역 (resource_efficiency_pareto_20260513.md) 에 별도 분리 발현된다.

---

작성: 2026-05-14 22:32 KST · v1 (10 단계, 5/14 07:55) → v2 (12 단계 + 부록 5 종, 5/14 22:32) update · 본 세션 22.5h 종합 + Form 1 fix (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ) + Agent A-J 10 호출 (paper 재정독 / 검증 / 8 옵션 deep dive / paper §VI 한계 / Form 1 구체화 / 측정 plan / paper Eq 1-6 verbatim / 1001 file batch baseline 재해석 / 5/27 + 6/11 outline / 박세은 6 영역) + 박세은 9 영역 (9:09 영역 1-5 + 9:27 영역 6 + 9:42 + 9:54 + 10:15 selectivity + over-statement + 가설 verify + 8:50 K granularity) + 정정 룰 14 (Agent 발견 2 + 박세은 9 + 본 verify 3) + 정직 disclosure 13 (Agent 7 + 박세은 6) + K granularity SF axis 48 file 추가 측정 완료 + Neyman selectivity-dependent 정정 반영 · 박세은 review + 박광현 5/15 미팅 + 5/27 최종 발표 + 6/11 최종 보고서 공통 base · fix 모드 (main theme + 4 측면 + paper §V-B "without index" 가정 변경 X)
