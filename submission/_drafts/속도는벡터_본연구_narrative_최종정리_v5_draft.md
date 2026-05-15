# 속도는벡터 — 본 연구 narrative 최종 정리 v5 draft

> 작성: 2026-05-15 21:00 KST · 박세은 5/15 20:49 정리본 + 박광현 5/15 D-Day 미팅 input 종합
> base: v4 commit ad8bc43 + v5 outline commit 6f5892a
> 핵심 변경: 박세은 정리 3 axis 직접 반영 (binary 폐기 / 빠른 catch / 분류 + 매핑)

박세은 정리 (5/15 20:49):
1. 분포 안다/모른다 binary 폐기 — 우리 method 자체가 분포 파악 도구
2. 데이터셋 진입 시 빠르게 분포 catch + 대응
3. 분포 분류 2-3 type + 분류별 적합 sampling 매핑

v5 구조: §0 main theme reframing + §3 데이터셋 4 type + dynamic method selection 핵심. 엔진 통합 (박광현 input 4) 은 post-narrative 사용자 향후 실험 진행 영역, 본 v5 안 포함.

---

## 0. 본 연구 main theme

본 연구의 main theme 은 **"Measurement-driven Distribution-aware Cardinality Estimation for Vector-augmented Analytical Queries"** 다.

본 theme 의 핵심 reframing (박세은 정리 #1 반영): paper Exqutor §V-B 의 "분포 모름 → Bernoulli random" framing 자체가 부정확하다. **우리 method (클러스터링 / 차원 축소 / quantization 등) 자체가 분포를 파악하는 도구** 이며, "분포 안다 / 모른다" 의 binary 구분은 의미 없다. 본 연구의 새 axis 는 다음 세 단계로 정리된다.

**Axis 1 (measurement-driven)**: 본 연구의 출발점은 paper 의 framework 가 아니라 9 cell × 56 method × 2 mode × 10 trial = **1352 file 직접 측정** portfolio. paper Exqutor (arXiv:2512.09695v2) 의 §V-B Adaptive Sampling 은 본 연구의 base reference 이며, paper 의 hyperparam 과 Eq 1-6 을 verbatim 으로 측정 환경에 반영한다.

**Axis 2 (distribution-aware via measurement)**: 우리 method 자체가 분포 파악 도구. 데이터셋 진입 시 method 가 빠르게 분포를 catch 한다 — fit_time 직접 측정으로 method 별 catch speed 가 11.9× 차이 (§2).

**Axis 3 (cardinality estimation for VAQ with dynamic selection)**: 본 연구의 범위는 vector-augmented analytical query (VAQ) 의 cardinality estimation 한정. 데이터셋 특성 (scale / structure / dimension) 별 분류 + Type 별 적합 method 매핑이 본 §3-§7 의 axis.

---

## 1. 출발점 + 측정 portfolio

VAQ cardinality estimation 에서 데이터 분포는 plan 결정에 결정적이다. paper Exqutor §V-B 의 Bernoulli random sampling 은 분포 정보를 활용하지 않고 random 추출 후 adaptive 보정만 진행한다. 본 연구는 paper §V-B base 환경 (sample budget N=385 verbatim) 위에서 **분포 인지 method (8 paradigm × 56 method) 의 정량 가치를 1352 file 직접 측정으로 검증** 한다.

### 1.1 측정 portfolio (1352 file)

9 측정 환경 (DEEP / SIFT / SSN 단일 + DEEP+YFCC + DEEP+WIKI 다중 테이블 + A4 선택도 sweep + A5 scale sweep sf=1/10/100) × 56 method × 2 mode (CaseA 단독 대체 + CaseB 결합 ensemble) × 10 trial. nominal cell 수 = 504. 실측 portfolio = paper exact base 1001 file + 추가 측정 351 file = **1352 file**.

9 측정 환경은 paper §VI-A ~ §VI-D 의 dataset × selectivity × scale 조합 (paper Fig.6 + Fig.7 + Fig.9 + Fig.10 + Fig.11) 과 직접 align. paper baseline 정합: Fig 12 mean Q-error 1.69 → 우리 1.618 (-4.3% 재현).

### 1.2 8 paradigm rollup axis

56 method 를 8 paradigm 으로 분류: P1 클러스터링 / P2 공간 분할 / P3 스트리밍 / P4 차원 축소 / P5 준 무작위 / P6 양자화 / P9 정보 이론 / P10 밀도 추정.

### 1.3 폐기 40 method 정직 분류

자원 한계 7 (17.5%) + reference audit 23 (57.5%) + 정합성 위반 10 (25%). 남은 16 사용 method 가 부록 §F base.

---

## 2. 분포 catch speed — fit_time 11.9× range

박세은 정리 #2 ("데이터셋 진입 시 빠르게 분포 catch") + 박광현 input 3 ("분포를 빠른 시간 안에 catch") 의 직접 evidence. 5/15 fit_time 직접 측정 (Pareto Top 5 method × 9 cell × 2 mode = 90 file 모두 fit_time_sec 정상 회수).

| Method | n | fit_time mean | range | cache_time mean |
|---|---:|---:|---|---:|
| sparse_rp | 18 | **3.67s** | 0.35 ~ 8.64s | 10.64s |
| neuram | 18 | 6.15s | 0.62 ~ 17.61s | 10.79s |
| chao_weighted | 18 | 9.40s | 0.12 ~ 28.34s | 10.11s |
| pca1d | 18 | 19.97s | 0.81 ~ 68.18s | 10.77s |
| hilbert_real | 18 | **43.50s** | 1.40 ~ 100.04s | 10.04s |

fit_time range = sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× 차이**. cache_time mean 약 10s (method 무관, vector dimension 의존). 9 cell × 2 mode 직접 측정으로 SF=1 / SF=10 / SF=100 axis 모두 cover.

산업 환경 분포 catch 속도 제약 시 sparse_rp (3.67s) 가 hilbert_real (43.50s) 대비 12× 빠르면서도 정확도는 동일 Pareto frontier (§6) 에서 동시 best 발현. 메모리는 모두 O(K × d) 이하, reservoir 는 데이터 크기와 무관한 상수 O(1).

박세은 5/14 9:27 자문 답변: 본 fit_time 은 method 학습 시간이며 매 query 마다 fit 하는 것이 아니다 (paper period P=50 가정에서 P 회 query 마다 1 회 또는 데이터 변경 시 incremental fit).

---

## 3. 데이터셋 특성별 분류 4 type + Type 별 적합 method (★ 박세은 정리 #3 + 박광현 input 1)

본 §3 은 본 연구의 핵심 contribution axis 다. 1352 file 측정 portfolio 의 9 cell 을 데이터셋 특성 (scale × structure × dimension) 기준으로 **4 type 으로 분류** + 각 type 별 적합 method 를 매핑한다. 본 axis 가 **dynamic method selection** 의 base 다.

### 3.1 분류 기준 — scale × structure × dimension

| Type | 정의 | 1352 file cell | row 수 | structure |
|---|---|---|---:|---|
| **Type 1** | small single (sf=1) | A5-scale-sf1 = 1 cell | 0.1M | single-table |
| **Type 2** | medium single (sf=10) | A5-scale-sf10 = 1 cell | 1M | single-table |
| **Type 3** | large single (sf=100, 저-중차원) | A1-DEEP/SIFT/SSN + A4-sel + A5-sf100 = 5 cells | 10M | single-table 96~256d |
| **Type 4** | large multi-table (sf=100) | A2-Fig7 + A2-Fig9 = 2 cells | 10M | multi-table 288d/864d |

Type 4 는 dimension 에 따라 sub-type 으로 분리:
- **Type 4a**: multi-table 중차원 (288d, DEEP+YFCC, A2-Fig7)
- **Type 4b**: multi-table 고차원 (864d, DEEP+WIKI, A2-Fig9)

### 3.2 Type 별 적합 method (CaseB best 기준)

| Type | 적합 method (CaseB best) | fit_time | 핵심 finding |
|---|---|---:|---|
| **Type 1** (small single sf=1) | **chao_weighted K=20 −14.11%** ★ 최강 / sparse_rp K=20 −11.70% | 3.67 ~ 9.40s | small data 영역 분포 인지 효과 가장 강력 |
| **Type 2** (medium single sf=10) | chao_weighted K=20 −6.00% (약함) / sparse_rp K=20 −6.58% | 3.67 ~ 9.40s | sf=10 영역 sweet spot 약화 (paper §VI-B "shifting workloads" align) |
| **Type 3** (large single sf=100 저-중차원) | chao_weighted K=20 −12.20% / sparse_rp K=20 −11.20% / neuram | 3.67 ~ 19.97s | large single 영역 K=20 sweet spot 일관 |
| **Type 4a** (large multi 288d) | hilbert_real K=30 slight edge / Pareto Top 5 中 선택 | 43.50s | multi-table 중차원 영역 hilbert_real K=30 우위 |
| **Type 4b** (large multi 864d) | **Centroid tuple −7.37%** (학습 비용 추가 0) | (Centroid 영역) | 고차원 multi-table 영역 학습 비용 0 의 Centroid tuple 안정 best |

### 3.3 K granularity SF axis evidence (Type 1/2/3 일관)

A5-scale × K=10/30 × 4 anchor × 2 mode = 48 file 추가 측정 결과:

| Method | K-pattern | SF=1 K=20 Δ% | SF=10 K=20 Δ% | SF=100 K=20 Δ% |
|---|---|---:|---:|---:|
| sparse_rp | K=20 sweet (U-shape) | −11.70% | −6.58% | −11.20% |
| chao_weighted | K=20 sweet 모든 SF 일관 | **−14.11%** | −6.00% | −12.20% |
| hilbert_real | K-robust + K=30 slight edge | −11.02% | −6.07% | −10.91% |
| hyperloglog | K-robust + K=30 slight edge | −10.19% | −5.15% | −10.54% |

method-dependent K best 패턴이 SF=1/10/100 axis 모두에서 일관 발현. Type 1/2/3 의 K 권장 patterns evidence.

### 3.4 sf=10 sweet spot 약화 — 데이터 크기 sweet spot

★ **Type 2 (sf=10) 의 분포 인지 효과 약화** (−5 ~ −7% 범위) 가 Type 1 (sf=1) + Type 3 (sf=100) 의 −10 ~ −14% 대비 절반 수준. 데이터 크기 sweet spot 가 sf=1 와 sf=100 양 끝에 있다는 evidence. paper §VI-B 의 "sample size trajectory varies depending on the dataset" 명시와 align.

---

## 4. 정확도 evidence — paired 92.5%

본 §4 는 1001 file paper exact base 측정 portfolio 의 단독 대체 (CaseA) + 결합 (CaseB) paired 비교 직접 evidence.

### 4.1 단독 대체 (CaseA) 결과

paper §V-B 의 Bernoulli random sampling 을 본 method (K=20 cluster stratified reservoir) 로 단순 대체. 9 측정 환경 전반 안정 우위 15 method 의 평균 개선폭 −5 ~ −12%. 단독 best = **minibatch_partial −10.17%** (A2-Fig8).

negative control: CaseA 모드의 large worsening = 37.1% 발현. 단독 대체 효과는 method 선택에 따라 양 방향 큰 변동.

### 4.2 결합 (CaseB) 결과

paper §V-B Bernoulli 추정값과 본 method 추정값을 산술 평균 (est_final = (est_b1 + est_method) / 2.0) 으로 결합. 492 paired 비교 中 **92.5% (455/492, p<1e-45)** 가 CaseA 보다 정확. Cliff's δ large better = 63.0% (311/494). Hedges' g large = 55.7% (275/494). 결합 best = **Centroid tuple −7.37%** (A2-Fig9, Type 4b).

α sweep evidence: 4 method 中 3 (sparse_rp / chao_weighted / hilbert_real) 이 α=0.5 (산술 평균) 에서 best.

### 4.3 method base — 4 component framework

본 연구의 분포 인지 sampling framework 는 4 component 통합:
- **Component A (Stratified Reservoir Sampling)**: Vitter 1985 + Al-Kateb 2014. paper §V-B Eq 1 Bernoulli 대체. 메모리 O(1).
- **Component B (BIRCH CF-tree)**: Zhang SIGMOD 1996. CF tuple 의 σ_j² 추정. batch axis 자원 한계로 폐기, CF tuple 형식만 Component C 입력.
- **Component C (paper Eq 2-6 통합)**: paper §V-B Eq 1-6 verbatim 100% 정합. AdaptiveState momentum + learning rate + period control. 본 augment = Eq 5 sampling_size 를 cluster 별 group-aware allocation.
- **Component D (Distribution-aware stratification)**: Cochran 1977 §5.5. 4 mode (Equal / Proportional / Neyman / Anti-Neyman).

---

## 5. plan robustness across environment variability (★ 박광현 input 6)

박광현 5/15 미팅 input 6 ("순서 바뀌지 않을 정도 정의 어려움 — 테이블 사이즈, 숫자 등 변수가 너무 많음") 의 본 연구 측정 evidence.

본 연구의 plan robustness 정의: **9 측정 환경 (dataset / sf / sel / dimension / multi-table) × 56 method 의 paired CaseB < CaseA 안정성**.

paired CaseB < CaseA = 92.5% (455/492) — 환경 / method 가 어떻게 변하든 약 92.5% 의 확률로 결합 모드가 단독 대체보다 우위. 단독 대체 (CaseA) 의 large worsening = 37.1% 대비 결합 모드의 변동성 감소가 plan robustness 의 직접 evidence.

### 5.1 Neyman selectivity-dependent paradox (sub-evidence)

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

reservoir 표집 (sparse_rp base) 은 메모리 사용이 데이터 크기와 무관한 상수 O(1) 인데도 anchor 수준 정확도. 모바일 / 임베디드 / 스트리밍 환경 직접 적용 가능 finding.

---

## 7. 권장 설계 — Dynamic method selection by dataset Type

본 §7 은 §3 의 4 type 분류 + Type 별 적합 method 매핑 base 위에서 **dynamic method selection flow** 를 제안한다.

### 7.1 Dynamic method selection flow

```
데이터셋 진입
  ↓
[Step 1] dataset profile 파악
  - row 수 (sf=1 / sf=10 / sf=100)
  - table 구조 (single / multi)
  - dimension (저 / 중 / 고)
  ↓
[Step 2] Type 판별 (Type 1/2/3/4a/4b 中 결정)
  ↓
[Step 3] Type 별 권장 method 적용
  - Type 1 (small single sf=1) → chao_weighted K=20 (-14.11%)
  - Type 2 (medium single sf=10) → chao_weighted K=20 (단, sweet spot 약함)
  - Type 3 (large single sf=100, 저-중차원) → chao_weighted / sparse_rp K=20
  - Type 4a (large multi 288d) → hilbert_real K=30
  - Type 4b (large multi 864d) → Centroid tuple (학습 비용 0)
  ↓
[Step 4] CaseB ensemble (결합) 또는 CaseA (단독) 결정
  - 환경 variability 큰 경우 → CaseB (plan robustness 92.5%)
  - method 선택 자신 있는 경우 → CaseA (정확도 best -10.17%)
```

### 7.2 Type 판별 fit_time cost

Type 판별 자체의 fit_time cost 는 매 query 가 아니라 데이터셋 진입 시 1 회 (paper period P=50 가정). sparse_rp 3.67s 로 fast profiling 후 Type 결정 가능. Type 별 권장 method 의 fit_time 도 3.67s ~ 43.50s range.

---

## 8. 결론

본 연구는 paper Exqutor §V-B Adaptive Sampling base 환경 위에서 분포 인지 stratification 의 cardinality estimation 정량 가치를 1352 file 직접 측정으로 검증했다. 박세은 정리 (5/15 20:49) + 박광현 5/15 미팅 input 종합 결과 본 연구의 axis 가 정리된다.

핵심 finding 5 가지:

**Finding 1 (분포 catch speed)**: fit_time 90 file 직접 측정에서 Pareto Top 5 method catch speed = sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× 차이**. 산업 환경 분포 catch 속도 axis 정량 evidence.

**Finding 2 (데이터셋 4 type + dynamic method selection)**: 데이터셋 특성 (scale × structure × dimension) 기준 4 type 분류 + Type 별 적합 method 매핑:
- Type 1 small single → chao_weighted K=20 (-14.11%)
- Type 2 medium single → sweet spot 약화
- Type 3 large single → chao_weighted / sparse_rp K=20
- Type 4a multi 288d → hilbert_real K=30
- Type 4b multi 864d → Centroid tuple (학습 비용 0)

**Finding 3 (정확도 evidence)**: paired CaseB < CaseA = **92.5%** (455/492, p<1e-45). Cliff's δ large = 63%, Hedges' g large = 56%. 단독 best -10.17% / 결합 best -7.37%.

**Finding 4 (plan robustness)**: 9 측정 환경 variability 에서 결합 모드 안정성 92.5%. selectivity-dependent paradox (sel=0.01 vs sel=0.10) 가 환경 variability 가 plan 결정을 변동시키는 evidence.

**Finding 5 (Pareto frontier)**: 정확도 best + 자원 효율 best 가 동일 method 군 (Pareto Top 5). reservoir 메모리 O(1).

paper §V-B Eq 1-6 + hyperparam 7종 verbatim 100% 정합 유지. 본 연구는 paper §V-B 후속 형식이 아니라 1352 file 실측 결과가 직접 가리키는 distribution-aware sampling 의 정량 가치 evidence 이며, 데이터셋 type 별 dynamic method selection 의 base 다.

---

# 부록 §A — 정정 룰 7 (paper §V-B 정독 + 임채림 자문)

## A-1. paper §V-B 자체 algorithm pseudo-code 없음

paper §V-B 는 Eq 1-6 + 자연 산문 + hyperparam 7 종 만으로 구성. "Algorithm 1" / "Procedure" 등 algorithmic block 형식이 paper 에 없다. 본 연구의 "17-step" 표현은 본 연구 자체의 의역.

## A-2. framework axis novelty 한정

본 연구의 4 component 자체는 각각 신규 X. Component A = Vitter 1985 + Al-Kateb 2014, Component B = Zhang SIGMOD 1996, Component C = paper §V-B verbatim, Component D = Cochran 1977 §5.5. 본 연구의 contribution = framework axis (4 component 통합 + paper §V-B 위에서의 발현 + 4 type 분류 + dynamic method selection + paired uplift 정량 evidence).

## A-3. paper §V-B single-table = 구현 코드 한계

paper §V-B 자체는 single-table KNN query 에 대한 sampling-based cardinality estimation 명시 (paper p.5 우단 verbatim). paper 공개 코드 (BDAI-Research/Exqutor github) 의 single-table 영역이 동작하지 않아 본 연구의 측정이 multi-join 으로 자연 이동. 임채림 연구원 자문 base.

## A-4. paper §V-B sampling = block + row hybrid

paper §V-B sampling 은 초기 N=385 budget = block 추출 + Eq 5 sampling_size update 시 n_inc 행 추가 = row 추출 의 block + row hybrid. 이전 narrative "block only" 표현은 부정확. 임채림 자문 base.

## A-5. "분포 안다 / 모른다" binary 폐기 (★ 박세은 5/15 20:49 정리 #1)

이전 narrative 의 "분포 안다 (L1/L2/L3 multi-layer) / 모른다" 영역 binary 구분은 부정확. 우리 method (클러스터링 / 차원 축소 / quantization 등) 자체가 분포를 파악하는 도구이며, 데이터셋 진입 시 method 가 빠르게 분포를 catch 한다. 본 binary 구분 자체가 paper §V-B 의 "without index" 가정을 잘못 해석한 것.

## A-6. paper §V-B = "without index" 가정

paper §V-B 자체는 "without vector index" 가정 안에서의 sampling-based cardinality estimation (paper p.5 좌단 + p.5 우단 + p.6 우단 + §VI-A + §VI-B verbatim). ECQO 의 vector index = HNSW (data itself) 구축과 §V-B sampling 은 paper 자체 안에서 상호 배타. 단 "without index" 는 인덱스 없음을 의미하며, 분포 정보 자체의 부재를 의미하지는 않는다 (정정 #5 와 align).

## A-7. "Anti-Neyman > Neyman" wording 정정 → selectivity-dependent

이전 narrative "Anti-Neyman > Neyman = Neyman 가설 무효" 는 부정확. 정확 의미:
- Neyman 가설 자체는 유효 (Cochran 1977 §5.5 classical theory 정합)
- 본 데이터셋이 Neyman 가정 조건 (cluster 간 σ_j heterogeneity) 不만족 (σ_j range 1.3-1.6× narrow + N_i CV=0)
- selectivity-dependent (sel=0.01 paradox / sel=0.10 정합)

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify.

---

작성: 2026-05-15 21:00 KST · 박세은 5/15 20:49 정리 + 박광현 5/15 미팅 input 종합 · 핵심: 데이터셋 4 type + dynamic method selection
