# 속도는벡터 — 본 연구 narrative 최종 정리 v4 draft

> 작성: 2026-05-15 20:45 KST · 박광현 5/15 D-Day 미팅 input 4 항목 (1, 2, 3, 6) 을 본문 axis 6 개로 직접 재구성
> base: v3 commit 4879999 + v4 outline commit f77cf57
> 박세은 + 임채림 정리본 도착 후 final 확정

v4 의 변경 (v3 대비): 본문 구조 axis 자체를 박광현 input 기준으로 재배열. v3 의 §4 (4 component) + §5 (paper Eq 1-6 통합) 는 §4 sub-section 으로 축소. v3 의 §8 (K granularity) + §9 (Neyman) 은 §3 / §5 의 evidence sub-section 으로 통합. input 4 (엔진 통합) + 5 (adversarial) 은 측정 evidence 없어 narrative 전체 제거.

---

## 0. 본 연구 main theme

본 연구의 main theme 은 **"Measurement-driven Distribution-aware Cardinality Estimation for Vector-augmented Analytical Queries"** 다.

본 theme 의 핵심 axis 는 세 가지로 정리된다.

**Axis 1 (measurement-driven)**: 본 연구의 출발점은 paper 의 framework 가 아니라 9 cell × 56 method × 2 mode × 10 trial = 1352 file 의 직접 측정 portfolio 다. paper Exqutor (arXiv:2512.09695v2) 의 §V-B Adaptive Sampling 은 본 연구의 base reference 이며, paper 의 hyperparam (m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period P=50 / N=385) 과 Eq 1-6 을 verbatim 으로 base 측정 환경에 반영한다. 본 연구의 결론은 paper framework 의 확장이 아니라 1352 file 실측 결과가 직접 가리키는 finding 이다.

**Axis 2 (distribution-aware)**: paper §V-B 의 Bernoulli random sampling 은 데이터 분포 정보를 활용하지 않는다. 본 연구는 8 paradigm (P1 Cluster / P2 Spatial / P3 Streaming / P4 DimReduction / P5 QMC / P6 Quantization / P9 InfoTheoretic / P10 Density) × 56 method 의 분포 인지 stratification 의 정량 가치를 측정한다.

**Axis 3 (cardinality estimation for VAQ)**: 본 연구의 범위는 vector-augmented analytical query (VAQ) 의 cardinality estimation 한정이다. paper Exqutor 는 §V-A ECQO (인덱스 있을 때 HNSW range query) 와 §V-B Adaptive Sampling (인덱스 없을 때 Bernoulli) 로 두 영역을 분리한다. 본 연구의 measurement 는 paper §V-B 의 base 환경에 align (sample budget N=385 verbatim).

---

## 1. 문제 + 측정 portfolio

VAQ cardinality estimation 에서 데이터 분포가 plan 결정에 결정적이다. plan 단계에서 cardinality 추정이 부정확하면 join 순서 / index 선택 / 자원 배분이 잘못 결정된다. paper Exqutor §V-B 의 Bernoulli random sampling 은 분포 정보를 활용하지 않기에, 분포 인지 sampling 의 정량 가치를 직접 측정으로 검증한다.

### 1.1 측정 portfolio (1352 file)

9 측정 환경 (DEEP / SIFT / SSN 단일 + DEEP+YFCC + DEEP+WIKI 다중 테이블 + A4 선택도 sweep + A5 scale sweep sf=1/10/100) × 56 method × 2 mode (CaseA 단독 대체 + CaseB 결합 ensemble) × 10 trial 의 매트릭스. nominal cell 수 = 504. 실측 portfolio = paper exact base 1001 file (B1 9 + CaseA 495 + CaseB 496) + 추가 측정 351 file = **1352 file**.

9 측정 환경은 paper §VI-A ~ §VI-D 의 dataset × selectivity × scale 조합 (paper Fig.6 + Fig.7 + Fig.9 + Fig.10 + Fig.11) 과 직접 align. paper baseline 정합: Fig 12 mean Q-error 1.69 → 우리 1.618 (-4.3% 재현).

### 1.2 8 paradigm rollup axis

56 method 를 8 paradigm 으로 분류:
- P1 클러스터링 / P2 공간 분할 / P3 스트리밍 / P4 차원 축소
- P5 준 무작위 / P6 양자화 / P9 정보 이론 / P10 밀도 추정

paradigm 별 결합 모드 Δ% mean 은 §3 에서 분포 유형별 method 적합성 evidence 로 정리.

### 1.3 폐기 40 method 정직 분류

자원 한계 7 (Tier 2 6 + KDE 1, 17.5%) + reference audit 23 (5/10 코드 정독, 57.5%) + 정합성 위반 10 (paper N=385 budget 위반, 25%). 남은 16 사용 method 가 부록 §F 의 paradigm 별 표 source.

---

## 2. 분포 catch speed — fit_time 11.9× range

박광현 5/15 미팅 input 3 ("분포를 빠른 시간 안에 catch 하는 방식") 의 직접 evidence. 5/15 fit_time 직접 측정 (Pareto Top 5 method × 9 cell × 2 mode = 90 file 모두 fit_time_sec 정상 회수).

| Method | n | fit_time mean | range | cache_time mean |
|---|---:|---:|---|---:|
| sparse_rp | 18 | **3.67s** | 0.35 ~ 8.64s | 10.64s |
| neuram | 18 | 6.15s | 0.62 ~ 17.61s | 10.79s |
| chao_weighted | 18 | 9.40s | 0.12 ~ 28.34s | 10.11s |
| pca1d | 18 | 19.97s | 0.81 ~ 68.18s | 10.77s |
| hilbert_real | 18 | **43.50s** | 1.40 ~ 100.04s | 10.04s |

fit_time range = sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× 차이**. 분포를 catch 하는 method 의 speed 가 13× 가까이 차이.

cache_time mean 약 10s (method 무관, vector dimension 의존). 9 cell × 2 mode 직접 측정으로 SF=1 / SF=10 / SF=100 axis 모두 cover.

산업 환경에서 분포 catch 속도가 우선 제약일 때 sparse_rp (3.67s) 가 hilbert_real (43.50s) 대비 12× 빠르면서도 정확도는 동일 Pareto frontier (§6) 에서 동시 best 발현. 메모리는 모두 O(K × d) 이하, reservoir 는 데이터 크기와 무관한 상수 O(1).

박세은 5/14 9:27 자문 ("0.1~0.5초 매 query 런타임?") 답변: 본 fit_time 은 method 학습 시간이며 매 query 마다 fit 하는 것이 아니다 (paper period P=50 가정에서 P 회 query 마다 1 회 또는 데이터 변경 시 incremental fit).

---

## 3. 분포 유형별 method 적합성

박광현 5/15 미팅 input 1 ("데이터 분포별로 어떤 샘플링 방식을 적용할 수 있는지") 의 직접 evidence. 8 paradigm × 9 측정 환경 rollup 결과:

### 3.1 paradigm 8 의 결합 모드 Δ% mean

| paradigm | CaseB Δ% mean | n (file) | best method (Δ%) |
|---|---:|---:|---|
| P10 Density | −11.93% | 1 | (single method, weak n) |
| P9 InfoTheoretic | −7.60% | 9 | hyperloglog (−8.65%) |
| P3 Streaming | −6.63% | 44 | chao_weighted (−9.60%) |
| P4 DimReduction | −6.03% | 104 | neuram (−9.97%) |
| P2 Spatial | −5.57% | 107 | hilbert_real (−9.27%) |
| P5 QMC | +1.47% | 62 | (paradigm-level 만 보고, method 4 건 폐기) |
| P1 Cluster | +2.04% | 87 | minibatch_partial (CaseA −10.17%) |
| P6 Quantization | +8.44% | 53 | pq (−9.25%) |

분포 유형별 적합성 patterns: 5 paradigm (P10 / P9 / P3 / P4 / P2) 이 결합 모드 effect size −5 ~ −12% 우위. 3 paradigm (P5 / P1 / P6) 은 paradigm 평균이 positive (P5 QMC 는 정합성 위반으로 paradigm-level 만 보고).

### 3.2 K granularity SF axis 영역

method-dependent K best 패턴 (DEEP A5-scale × K=10/20/30 × 4 anchor × 2 mode = 48 file 추가 측정):

| Method | K-pattern | SF=1 K=20 Δ% | SF=10 K=20 Δ% | SF=100 K=20 Δ% |
|---|---|---:|---:|---:|
| sparse_rp | K=20 sweet (U-shape) | −11.70% | −6.58% | −11.20% |
| chao_weighted | K=20 sweet 모든 SF 일관 | **−14.11%** | −6.00% | −12.20% |
| hilbert_real | K-robust + K=30 slight edge | −11.02% (K=30 −12.25%) | −6.07% (K=30 −6.96%) | −10.91% (K=30 −11.81%) |
| hyperloglog | K-robust + K=30 slight edge | −10.19% (K=30 −12.57%) | −5.15% (K=30 −6.01%) | −10.54% (K=30 −11.62%) |

sparse_rp / chao_weighted = K=20 sweet spot. hilbert_real / hyperloglog = K=30 slight edge. K best 가 method 별로 다른 패턴 — 분포 유형별 method-K granularity 적합성 axis 의 evidence.

---

## 4. 정확도 evidence — paired 92.5%

본 §4 는 1001 file paper exact base 측정 portfolio 의 단독 대체 (CaseA) + 결합 (CaseB) paired 비교 직접 evidence.

### 4.1 단독 대체 (CaseA) 결과

paper §V-B 의 Bernoulli random sampling 을 본 method (K=20 cluster stratified reservoir) 로 단순 대체. 56 method 中 약 40% 가 평균적으로 Bernoulli 보다 정확. 9 측정 환경 전반 안정 우위 15 method 의 평균 개선폭 −5 ~ −12%. 단독 best = **minibatch_partial −10.17%** (A2-Fig8).

negative control: CaseA 모드의 large worsening = 37.1% 발현. 단독 대체 효과는 method 선택에 따라 양 방향 큰 변동.

### 4.2 결합 (CaseB) 결과

paper §V-B Bernoulli 추정값과 본 method 추정값을 산술 평균 (est_final = (est_b1 + est_method) / 2.0) 으로 결합. 492 paired 비교 中 **92.5% (455/492, p<1e-45)** 가 CaseA 보다 정확. Cliff's δ large better = 63.0% (311/494). Hedges' g large = 55.7% (275/494). one-sided p<0.05 outperform = 45.3% (224/494). 결합 best = **Centroid tuple −7.37%** (A2-Fig9).

α sweep (0.3 / 0.4 / 0.6 / 0.7 측정) 결과 4 method 中 3 (sparse_rp / chao_weighted / hilbert_real) 이 α=0.5 (산술 평균) 에서 best. 산술 평균 기본값의 evidence.

### 4.3 method base (4 component)

본 연구의 분포 인지 sampling framework 는 4 component 의 통합:

- **Component A (Stratified Reservoir Sampling)**: Vitter 1985 + Al-Kateb-Lee-Wang 2014. paper §V-B Eq 1 의 Bernoulli random 추출을 K cluster 별 reservoir 로 대체. 메모리 O(1).
- **Component B (BIRCH CF-tree)**: Zhang-Ramakrishnan-Livny 1996. streaming 환경 K cluster boundary online maintenance + σ_j² 추정. 본 연구 batch axis 에서 BIRCH 자체는 자원 한계로 폐기, CF tuple 형식만 Component C 의 입력 source.
- **Component C (paper Eq 2-6 통합)**: paper §V-B Eq 1-6 verbatim 100% 정합. AdaptiveState class 의 momentum + learning rate + period control. 본 연구 augment = Eq 5 sampling_size update 를 cluster 별 group-aware allocation 으로 확장.
- **Component D (Distribution-aware stratification)**: Cochran 1977 §5.5 (Optimal Allocation) 의 4 mode (Equal / Proportional / Neyman / Anti-Neyman).

---

## 5. plan robustness across environment variability

박광현 5/15 미팅 input 6 ("순서가 바뀌지 않을 정도라는 거도 사실 정의하기 쉽지 않음 — 테이블 사이즈, 숫자 등 변수가 너무 많음") 의 본 연구 측정 evidence.

### 5.1 plan robustness 의 본 연구 정의

본 연구의 plan robustness 정의: **9 측정 환경 (dataset / sf / sel / dimension / multi-table) × 56 method 의 paired CaseB < CaseA 안정성**.

9 측정 환경 = DEEP/SIFT/SSN sf=100 (3) + DEEP+YFCC (1) + DEEP+WIKI (1) + A4 sel sweep (1) + A5 scale sf=1/10/100 (3) = 9 cell. 각 환경은 paper §VI-A ~ §VI-D 의 dataset / selectivity / scale 조합 verbatim. 환경 variability 의 정량 base.

### 5.2 결합 모드 안정성 evidence

paired CaseB < CaseA = 92.5% (455/492) — 환경 / method 가 어떻게 변하든 약 92.5% 의 확률로 결합 모드가 단독 대체보다 우위. Cliff's δ large better = 63.0% (311/494) 는 환경 / method 변동에도 effect size 가 large 한 영역이 63%.

비교: 단독 대체 (CaseA) 의 large worsening = 37.1% — 환경 / method 선택에 따라 양 방향 큰 변동. 결합 모드의 변동성 감소가 plan robustness 의 직접 evidence.

### 5.3 Neyman selectivity-dependent 영역

plan robustness 의 sub-finding: RQ2 5-way 측정 (Bernoulli + Equal + Prop + Neyman + Anti-Neyman) 의 selectivity 별 paradox.

| selectivity | Neyman | Anti-Neyman | Proportional | best |
|---|---:|---:|---:|---|
| sel=0.01 | 1.595 | 1.540 | 1.580 | **Anti < Prop < Neyman** (paradox) |
| sel=0.10 | 1.1076 | 1.1101 | 1.1135 | **Neyman < Anti < Prop** (classical 정합) |

sel=0.01 paradox 해석: 본 dataset 의 cluster 간 σ_j range 1.3-1.6× narrow (Cochran 1977 §5.5 Neyman 가정 不만족) + N_i CV=0 (cluster size 균등) 의 두 가정 不만족. selectivity 환경 variability 가 plan 결정을 변동시키는 직접 evidence.

---

## 6. Pareto frontier — 정확도 + 자원 동시 best

본 §6 은 §2 (fit_time) + §4 (paired accuracy) evidence 를 통합한 Pareto frontier 정리.

**Pareto Top 5 method** = sparse_rp / chao_weighted / neuram / pca1d / hilbert (★ hilbert 는 PCA 2 차원 정렬 별칭, 진짜 Hilbert curve 구현인 hilbert_real 은 별도 측정).

정확도 측면 안정 우위 5 method 와 자원 효율 측면 파레토 우위 5 method 가 동일하다는 finding. 단독 대체 (CaseA) 모드 정확도 best 와 학습 자원 (시간 + 메모리) 효율 best 가 동일 method 군에서 발현.

| Method | fit_time mean | 메모리 | CaseB Δ% (P3 paradigm) | CaseA best Δ% |
|---|---:|---|---:|---:|
| sparse_rp | 3.67s | O(1) reservoir | (P3 −6.63%) | (각 paradigm 별) |
| chao_weighted | 9.40s | O(K) | -9.60% | (P3) |
| neuram | 6.15s | O(K × d) | (P4 −6.03%) | -9.97% (P4) |
| pca1d | 19.97s | O(K × d) | (P4) | (P4 best 영역) |
| hilbert_real | 43.50s | O(K × d) | (P2 −9.27%) | (P2) |

reservoir 표집 (sparse_rp base) 은 메모리 사용이 데이터 크기와 무관한 상수 O(1) 인데도 anchor 수준 정확도. 모바일 / 임베디드 / 스트리밍 환경 직접 적용 가능 finding.

---

## 7. 권장 설계 4 단계

본 §7 은 1352 file 측정 portfolio 의 종합 결과에서 도출된 권장 설계. 측정 evidence 위에서만 직접 권장.

### 7.1 단독 대체 우선 (정확도 best)

산업 환경에 맞는 method 를 Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) 中에서 골라 Bernoulli 를 대체한다. 가장 단순하면서 가장 큰 정확도 개선 (best minibatch_partial -10.17%). 사전 학습 fit_time 은 sparse_rp 3.67s ~ hilbert_real 43.50s.

### 7.2 결합 보조 (plan robustness)

method 선택에 자신이 없거나 측정 환경 variability 가 큰 환경에서 산술 평균 결합 (est_final = (est_b1 + est_method) / 2.0) 을 안전망으로 둔다. 92.5% paired uplift + 9 측정 환경 변동성 감소. 정확도는 단독보다 약하지만 method 선택 risk mitigation.

### 7.3 자원 우선 (reservoir O(1))

메모리가 가장 제약이라면 reservoir 같은 상수 메모리 method 를 단독으로 쓴다. 메모리 cost O(1) + fit_time sparse_rp 3.67s + 정확도 평균 −9.25% (단독 대체 9 측정 환경). 모바일 / 임베디드 / vector database insert stream 환경 직접 적용.

### 7.4 다중 테이블 (Centroid tuple)

다중 테이블 환경에서 두 테이블 클러스터링을 합치는 방식. 비싼 방식 (두 테이블 벡터를 합쳐 처음부터 다시 학습) vs 저렴한 방식 (이미 학습된 두 클러스터링의 결과를 가볍게 합치는 Centroid tuple). 측정 결과 Centroid tuple 이 학습 비용 추가 0 으로 안정 우위 (A2-Fig9 결합 best -7.37%).

---

## 8. 결론

본 연구는 paper Exqutor §V-B 의 Adaptive Sampling base 환경 위에서 분포 인지 stratification 의 cardinality estimation 정량 가치를 1352 file 직접 측정으로 검증했다.

핵심 finding 4 가지:

**Finding 1 (분포 catch speed)**: 5/15 fit_time 직접 측정 90 file 에서 Pareto Top 5 method 의 catch speed 가 sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× 차이**. 산업 환경 분포 catch 속도 선택의 정량 evidence.

**Finding 2 (분포 유형별 method 적합성)**: 8 paradigm rollup 에서 5 paradigm (P10/P9/P3/P4/P2) 결합 모드 우위 (−5 ~ −12%) + 3 paradigm 약화. method-dependent K granularity 패턴 (sparse_rp/chao_weighted K=20 sweet vs hilbert_real/hyperloglog K=30 slight edge) 가 SF axis 일관.

**Finding 3 (정확도 evidence)**: paired CaseB < CaseA = **92.5%** (455/492, p<1e-45). Cliff's δ large = 63%, Hedges' g large = 56%. 단독 best −10.17% + 결합 best −7.37%.

**Finding 4 (plan robustness)**: 9 측정 환경 (dataset / sf / sel / dimension / multi-table) variability 에서 결합 모드의 안정성 92.5%. 단독 대체 negative control = large worsening 37.1% 대비 결합 모드 안전망. selectivity-dependent paradox (sel=0.01 Anti < Prop < Neyman vs sel=0.10 정합) 가 환경 variability 가 plan 결정을 변동시키는 evidence.

paper §V-B Eq 1-6 + hyperparam 7종 verbatim 100% 정합 유지. paper Fig 12 mean Q-error 1.69 → 우리 1.618 (-4.3% 재현). 본 연구는 paper §V-B 의 후속 형식이 아니라 1352 file 실측 결과가 직접 가리키는 distribution-aware sampling 의 정량 가치 evidence 다.

---

# 부록 §A — 정정 룰 7 (paper §V-B 정독 + 임채림 자문)

## A-1. paper §V-B 자체 algorithm pseudo-code 없음

paper §V-B 는 Eq 1-6 + 자연 산문 + hyperparam 7 종 만으로 구성. "Algorithm 1" / "Procedure" 등 algorithmic block 형식이 paper 에 없다. 본 연구의 "17-step" 표현은 본 연구 자체의 의역.

## A-2. framework axis novelty 한정

본 연구의 4 component 자체는 각각 신규 X. Component A = Vitter 1985 + Al-Kateb 2014, Component B = Zhang SIGMOD 1996, Component C = paper §V-B verbatim, Component D = Cochran 1977 §5.5. 본 연구의 contribution = framework axis (4 component 통합 + paper §V-B 위에서의 발현 + paradigm rollup + paired uplift 정량 evidence).

## A-3. paper §V-B single-table = 구현 코드 한계

paper §V-B 자체는 single-table KNN query 에 대한 sampling-based cardinality estimation 명시 (paper p.5 우단 verbatim). paper 공개 코드 (BDAI-Research/Exqutor github) 의 single-table 영역이 동작하지 않아 본 연구의 측정이 multi-join 으로 자연 이동. 임채림 연구원 자문 base.

## A-4. paper §V-B sampling = block + row hybrid

paper §V-B sampling 은 초기 N=385 budget = block 추출 + Eq 5 sampling_size update 시 n_inc 행 추가 = row 추출 의 block + row hybrid. 이전 narrative "block only" 표현은 부정확. 임채림 자문 base.

## A-5. "분포 안다" L1/L2/L3 multi-layer

"분포 안다" 는 L1 (global skew flag) + L2 (cluster boundary K=20) + L3 (cluster boundary + σ_j 분산) 의 multi-layer. 본 연구 RQ2 는 L3 oracle 가정 (offline batch K-means 의 σ_j 직접 사용).

## A-6. paper §V-B = "without index" 가정

paper §V-B 자체는 "without vector index" 가정 안에서의 sampling-based cardinality estimation (paper p.5 좌단 + p.5 우단 + p.6 우단 + §VI-A + §VI-B verbatim). ECQO 의 vector index = HNSW (data itself) 구축과 §V-B sampling 은 paper 자체 안에서 상호 배타.

## A-7. "Anti-Neyman > Neyman" wording 정정 → selectivity-dependent

이전 narrative "Anti-Neyman > Neyman = Neyman 가설 무효" 는 부정확. 정확 의미:
- Neyman 가설 자체는 유효 (Cochran 1977 §5.5 classical theory 정합)
- 본 데이터셋이 Neyman 가정 조건 (cluster 간 σ_j heterogeneity) 不만족 (σ_j range 1.3-1.6× narrow + N_i CV=0)
- selectivity-dependent (sel=0.01 paradox / sel=0.10 정합)

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify.

---

작성: 2026-05-15 20:50 KST · 박광현 5/15 D-Day 미팅 input 4 항목 본문 axis 재구성 · 박세은 + 임채림 정리본 도착 후 final 확정
