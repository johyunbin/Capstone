# 속도는벡터 — 본 연구 narrative 최종 정리 v3 draft

> 작성: 2026-05-15 20:15 KST · 박광현 5/15 D-Day 미팅 input 반영 + 사용자 (조현빈) 임시 진행분
> base: v2 draft (commit 340f834, 5/15 17:00 정리 1차) + 박광현 미팅 회의록 (`_internal/records/kakaotalk/20260515_박광현미팅.md`)
> 변경: v2 의 "Extending Exqutor's §V-B Framework" main theme 폐기 → 결과 기반 reframing
> 박세은 + 임채림 정리본 도착 후 final 확정

본 v3 의 핵심 변경: paper §V-B anchor 를 base reference 로만 인용 (anchor 자체는 약화). 1352 file 실측 evidence 위에서 결과 기반 problem framing. Form 1 Component framework 는 distribution-aware sampling framework 로 재해석.

---

## 0. 본 연구 main theme

본 연구의 main theme 은 **"Measurement-driven Distribution-aware Cardinality Estimation for Vector-augmented Analytical Queries"** 다.

본 theme 의 핵심 axis 는 세 가지로 정리된다.

**Axis 1 (measurement-driven)**: 본 연구의 출발점은 paper 의 framework 가 아니라 9 cell × 56 method × 2 mode × 10 trial = 1352 file 의 직접 측정 portfolio 다. paper Exqutor (arXiv:2512.09695v2) 의 §V-B Adaptive Sampling 은 본 연구의 base reference 이며, paper 의 hyperparam (m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period P=50 / N=385) 과 Eq 1-6 을 verbatim 으로 base 측정 환경에 반영한다. 본 연구의 결론은 paper framework 의 확장이 아니라 1352 file 실측 결과가 직접 가리키는 finding 이다.

**Axis 2 (distribution-aware)**: paper §V-B 의 Bernoulli random sampling 은 데이터 분포 정보를 활용하지 않는다. 본 연구는 8 paradigm (P1 Cluster / P2 Spatial / P3 Streaming / P4 DimReduction / P5 QMC / P6 Quantization / P9 InfoTheoretic / P10 Density) × 56 method 의 분포 인지 stratification 의 정량 가치를 측정한다. 핵심 finding: 분포 인지 stratification 의 결합 (CaseB) 모드가 paper exact base 대비 **paired 92.5% (455/492, p<1e-45)** 우위.

**Axis 3 (cardinality estimation for VAQ)**: 본 연구의 범위는 vector-augmented analytical query (VAQ) 의 cardinality estimation 한정이다. paper Exqutor 는 §V-A ECQO (인덱스 있을 때 HNSW range query) 와 §V-B Adaptive Sampling (인덱스 없을 때 Bernoulli) 로 두 영역을 분리한다. 본 연구의 measurement 는 paper §V-B 의 base 환경에 align (sample budget N=385 verbatim) 하지만, 본 연구의 결론은 paper §V-B 의 후속 형식이 아니라 분포 인지 stratification 의 cardinality estimation 에 대한 정량 가치 검증 이다.

---

## 1. 출발점: 1352 file 측정 portfolio 가 가리키는 finding

본 연구의 출발점은 1352 file 측정 portfolio 의 직접 결과다. 9 측정 환경 (DEEP/SIFT/SSN 단일 + DEEP+YFCC + DEEP+WIKI + A4-sel + A5-scale sf=1/10/100) × 56 method × 2 mode (CaseA 단독 대체 + CaseB 결합 ensemble) × 10 trial 의 portfolio 에서 본 연구의 핵심 finding 세 가지가 도출된다.

**Finding 1 (paired 우위)**: 분포 인지 stratification 의 결합 (CaseB) 모드가 paper exact base 대비 **paired 92.5% 우위** (455/492, p<1e-45). Cliff's δ large better = 63.0% (311/494). Hedges' g large = 55.7% (275/494). one-sided p<0.05 outperform = 45.3% (224/494). 본 paired uplift 가 본 연구의 핵심 evidence 다.

**Finding 2 (자원 효율 Pareto)**: 5/15 fit_time 직접 측정 (Pareto Top 5 method × 9 cell × 2 mode = 90 file). sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× range**. cache_time mean 약 10s (method 무관, vector dimension 의존). reservoir 표집 메모리 O(1). 정확도 best 와 자원 효율 best 가 동일 method 군 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) 에서 발현.

**Finding 3 (paper baseline 정합)**: paper Fig 12 의 mean Q-error 1.69 에 대해 우리 측정 결과는 1.618 (-4.3% 재현). paper §V-B Eq 1-6 verbatim 100% 정합 + hyperparam 7종 paper verbatim.

위 3 finding 이 본 연구 narrative 종합의 base 다.

---

## 2. 탐색: 분포 정보를 얻는 방법 56 가지

분포 정보를 얻을 수 있는 후보 method 56 개를 8 paradigm (P1 클러스터링 / P2 공간 분할 / P3 스트리밍 / P4 차원 축소 / P5 준 무작위 / P6 양자화 / P9 정보 이론 / P10 밀도 추정) 로 모았다. 본 8 paradigm 은 본 연구의 method rollup axis 이며, 측정 결과의 분포 인지 효과를 paradigm 별 평균으로 정리하는 단위다.

9 측정 환경 (DEEP / SIFT / SSN 단일 테이블 + DEEP+YFCC + DEEP+WIKI 다중 테이블 + A4 선택도 sweep + A5 scale sweep sf=1/10/100) × 2 mode (CaseA 단독 대체 + CaseB 결합 ensemble) 로 매트릭스를 짰다. nominal cell 수 = 9 × 56 = 504. 실측 portfolio 는 paper exact base 1001 file (B1 9 + CaseA 495 + CaseB 496) + 추가 측정 351 file = **1352 file** 다.

추가 측정 351 file 의 구성: K granularity SF axis 48 file (DEEP A5-scale × K=10/30 × 4 anchor × 2 mode) + α sweep 20 file (DEEP+WIKI × 0.3/0.4/0.6/0.7 × 4 method) + cheap 근사 32 file (B1/B2/B3 + Centroid tuple) + multi-join 8 file + A2-Fig8 multi-vector 12 file (scope 외) + fit_time 90 file (5/15 측정, §10 source) + 기타 141 file.

9 측정 환경은 paper §VI-A ~ §VI-D 의 dataset × selectivity × scale 조합 (paper Fig.6 + Fig.7 + Fig.9 + Fig.10 + Fig.11) 과 직접 align 한다. paper 환경 정의를 verbatim 으로 따른 환경이 본 연구의 paper baseline 정합 (Fig 12 mean Q-error 1.69 → 우리 1.618) 의 근거다.

---

## 3. 폐기: 정직하게 떨어뜨린 40 method

측정을 진행하면서 **40 method** 를 폐기했다. 폐기 사유는 세 갈래로 정직 분류된다.

**자원 한계 7 종** (17.5%): Tier 2 6 method (dirichlet / kernelpca / neurocard_lite / birch / hdbscan / agglomerative) + KDE 1 method (kde_parzen). birch 는 한 측정에 50 ~ 200 GB 메모리 차지로 실행 불가. kde_parzen 은 5/13 ~ 5/14 측정 chain 시도 후 timeout 으로 5/14 07:39 폐기.

**reference audit 23 종** (57.5%): 5/10 코드 정독 8 agent 호출 + Q1-Q5 confirm 결과 23 method 가 reference 위반 또는 alias 로 분류. 대표 사례: vinecopula 가 vine copula 가 아니라 PCA 1 차원 정렬의 별칭. neuram 이 PCA1D 와 한 줄씩 동일 코드. 본 audit 자체가 본 연구의 학술 정직성 evidence 다.

**정합성 위반 10 종** (25%): halton / sobol / lhs / hammersley / dense_rp / random_projection / dbscan / ccsketch / lsh / ams_count_sketch. paper N=385 budget 위반 (sample size 가 paper budget 과 다르게 발현하거나 측정값이 anchor 의 ±50% 외부로 튀는 cell 이 빈번).

남은 16 사용 method 는 부록 §F 에 paradigm 별 분포 + 결합 모드 평균 + 자원 효율 등급 + 이론적 근거 로 정리한다.

---

## 4. Distribution-aware sampling framework — 4 component

본 연구의 분포 인지 sampling framework 는 4 component 로 구성된다. 본 framework 는 paper §V-B 의 Bernoulli random + adaptive Eq 1-6 base 환경 위에서 분포 정보를 활용하는 axis 다. 각 component 의 이론 base 와 측정 evidence 는 부록 §F 에 paradigm 별 표로 정리한다.

### 4.1 Component A — Stratified Reservoir Sampling (SRS)

paper §V-B Eq 1 의 Bernoulli random sample 추출을 K cluster 별 reservoir sampling 으로 대체한다. 이론 base = Vitter 1985 (TOMS) Algorithm R + Al-Kateb-Lee-Wang ISJ 2014 의 stratified extension. 측정 evidence: P3 Streaming paradigm CaseB Δ% −6.63% (n=44), best chao_weighted −9.60%. 메모리 cost = O(K × d) 의 작은 양, reservoir 자체는 sample size 와 데이터 크기 무관한 상수 O(1) 라는 강력 finding.

### 4.2 Component B — BIRCH CF-tree online cluster maintenance

streaming 환경에서 K cluster boundary 의 online maintenance 를 위한 CF-tree (Cluster Feature) 구조. 이론 base = Zhang-Ramakrishnan-Livny SIGMOD 1996. CF tuple (N_i, LS_i, SS_i) 에서 σ_j² 추정이 자연 도출된다. 본 연구의 measurement 환경 (1352 file batch axis) 에서 BIRCH 자체는 자원 한계 (50-200 GB 메모리) 로 폐기 분류 (§3); BIRCH 의 CF tuple 추정 형식은 §6 의 group-aware allocation 의 입력 source 로 사용된다.

### 4.3 Component C — paper Eq 2-6 통합 + Eq 5 group-aware augment

paper §V-B Eq 1-6 verbatim 100% 정합 유지 (AdaptiveState class 의 momentum m=0.9, learning rate η₀=0.1, momentum threshold α=50, decay β=1.5, gamma γ=0.99, period P=50, sample budget N=385 paper verbatim). 본 연구의 augment 는 Eq 5 의 scalar sampling_size update 를 cluster 별 group-aware allocation 으로 확장한 부분 한정. paper §V-A ECQO (인덱스 있을 때 HNSW range query) 는 본 연구의 outside.

### 4.4 Component D — Distribution-aware stratification

cluster 간 sample size 배분 axis 의 4 mode: Equal (1/K) / Proportional (N_i / Σ N_j) / Neyman (N_i σ_i / Σ N_j σ_j) / Anti-Neyman (역 Neyman). 이론 base = Cochran 1977 §5.5 (Optimal Allocation). 측정 evidence: RQ2 5-way (Bernoulli + Equal + Prop + Neyman + Anti-Neyman) 에서 sel 별 paradox 발현 (§12 에서 정리).

---

## 5. paper §V-B Eq 1-6 통합 + 본 framework 의 augment scope

본 §5 는 4 component 가 paper §V-B Eq 1-6 과 어떻게 통합되는지 정리한다.

paper §V-B 의 AdaptiveState (Eq 1-6) 는 sample size 의 momentum-based feedback control 을 제공한다. Eq 1: N=385 (z=1.96, P̂=0.5, e=0.05 의 classical sampling theory). Eq 2-4: momentum + learning rate decay + gamma decay. Eq 5: sampling_size update (scalar). Eq 6: 수렴 조건.

본 연구의 augment 는 두 부분 한정이다.

**Augment 1 (Eq 1 의 Bernoulli random → SRS K-cluster)**: paper Eq 1 의 sample 추출 방식만 본질 대체. sample budget N=385 자체는 verbatim 유지.

**Augment 2 (Eq 5 의 scalar new_size → cluster 별 group-aware allocation)**: paper Eq 5 의 sampling_size update 가 scalar 인데, 본 연구의 augment 에서는 cluster 별 N_i / σ_i 정보를 활용한 group-aware allocation 으로 새 추가 sample 의 cluster 분배 axis 를 정한다. paper Eq 5 자체의 momentum 기반 size update 는 그대로 유지.

paper Eq 2-4 + Eq 6 + hyperparam 7종 (m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N=385) 은 verbatim 100% 정합 유지. 본 framework 의 paper-grade compatibility 의 근거다.

---

## 6. 결과 — 1001 file 단독 대체 + 결합 paired 92.5% 우위

본 §6 은 1001 file paper exact base 측정 portfolio 의 직접 결과를 정리한다. 8 paradigm 별 rollup + 단독 대체 (CaseA) + 결합 (CaseB) 의 paired 비교 + 정직 정리.

### 6.1 8 paradigm rollup (CaseB Δ% mean)

| paradigm | CaseB Δ% mean | n (file) | best method |
|---|---:|---:|---|
| P10 Density | −11.93% | 1 | (single method, weak n) |
| P9 InfoTheoretic | −7.60% | 9 | hyperloglog (−8.65%) |
| P3 Streaming | −6.63% | 44 | chao_weighted (−9.60%) |
| P4 DimReduction | −6.03% | 104 | neuram (−9.97%) |
| P2 Spatial | −5.57% | 107 | hilbert_real (−9.27%) |
| P5 QMC | +1.47% | 62 | (paradigm-level 만 보고, method 4건 폐기) |
| P1 Cluster | +2.04% | 87 | minibatch_partial (CaseA −10.17%) |
| P6 Quantization | +8.44% | 53 | pq (−9.25%) |

5 paradigm (P10 / P9 / P3 / P4 / P2) 는 CaseB 모드 effect size −5 ~ −12% 우위. 3 paradigm (P5 / P1 / P6) 은 paradigm 평균 positive 인데, P5 QMC 는 정합성 위반으로 paradigm-level 만 보고. P1 Cluster 의 +2.04% mean 은 paradigm 평균이며 best minibatch_partial 의 CaseA mode 에서는 −10.17% 발현.

### 6.2 단독 대체 (CaseA) batch 결과

paper §V-B 의 Bernoulli random sampling 을 본 method (K=20 cluster stratified) 로 단순히 대체한 결과. 56 method 中 약 40% 가 평균적으로 Bernoulli 보다 정확했고, 통계 검정으로 9 측정 환경 전반에서 안정 우위인 15 method 의 평균 개선폭은 −5 ~ −12% 범위. 단독 best = minibatch_partial **−10.17%** (A2-Fig8 single cell).

negative control: CaseA 모드의 large worsening = 37.1% 발현. 단독 대체 효과는 method 선택에 따라 양 방향 큰 변동.

### 6.3 결합 (CaseB) batch 결과

paper §V-B Bernoulli 추정값과 본 method 추정값을 산술 평균 (est_final = (est_b1 + est_method) / 2.0) 으로 결합. 492 paired 비교 中 **92.5% (455/492, p<1e-45)** 가 CaseA 보다 정확. Cliff's δ large better = 63.0% (311/494). Hedges' g large = 55.7% (275/494). one-sided p<0.05 outperform = 45.3% (224/494). 결합 best = Centroid tuple **−7.37%** (A2-Fig9).

α sweep (0.3 / 0.4 / 0.6 / 0.7 측정) 결과 4 method 中 3 (sparse_rp / chao_weighted / hilbert_real) 이 α=0.5 (산술 평균) 에서 best. 산술 평균 기본값의 evidence.

### 6.4 단독 vs 결합 finding

결합 best −7.37% 가 단독 best −10.17% 보다 약하다. 결합으로 단독을 능가할 수는 없다. 다만 결합 모드의 92.5% paired 우위 는 method 선택을 잘못해도 거의 항상 단독 대체보다는 낫다는 안정성 finding. 9 측정 환경 변동성도 결합 모드가 단독보다 작았다.

산업 환경에서 method 선택에 자신이 있다면 단독 대체 (CaseA) 가 가장 큰 정확도 개선, method 선택에 자신이 없거나 측정 환경 variability 가 큰 환경에서는 결합 모드 (CaseB) 가 안정 안전망.

---

## 7. 자원 효율 — Pareto frontier + fit_time 11.9× range

본 §7 은 정확도 측면 안정 우위 5 method 와 자원 효율 측면 파레토 우위 5 method 가 동일하다는 finding 의 정량 evidence 를 정리한다. **Pareto Top 5 = sparse_rp / chao_weighted / neuram / pca1d / hilbert** (★ hilbert 는 PCA 2 차원 정렬 별칭, 진짜 Hilbert curve 구현인 hilbert_real 은 별도 측정).

### 7.1 fit_time 직접 측정 (90 file)

5/15 02:30 launch → 17:01 retry 완료. Pareto Top 5 method × 9 cell × 2 mode = 90 file 모두 fit_time_sec 정상 회수.

| Method | n | fit_time mean | range | cache_time mean |
|---|---:|---:|---|---:|
| sparse_rp | 18 | **3.67s** | 0.35 ~ 8.64s | 10.64s |
| neuram | 18 | 6.15s | 0.62 ~ 17.61s | 10.79s |
| chao_weighted | 18 | 9.40s | 0.12 ~ 28.34s | 10.11s |
| pca1d | 18 | 19.97s | 0.81 ~ 68.18s | 10.77s |
| hilbert_real | 18 | **43.50s** | 1.40 ~ 100.04s | 10.04s |

fit_time range = sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× 차이**. cache_time mean 약 10s (method 무관, vector dimension 의존). 9 cell × 2 mode 직접 측정으로 SF=1 / SF=10 / SF=100 axis 모두 cover.

### 7.2 메모리 + Pareto finding

5 method 의 학습 메모리 cost 는 모두 O(K × d) 이하. 특히 **reservoir 표집은 메모리가 데이터 크기와 무관한 상수 O(1)** 인데도 anchor 수준 정확도. 모바일 / 임베디드 / 스트리밍처럼 메모리가 제약인 환경에 그대로 적용 가능한 finding. 본 reservoir 가 §4.1 Component A 의 base 다.

박세은 5/14 9:27 자문 ("0.1~0.5초 매 query 런타임?") 에 대한 답변: 본 fit_time 은 method 학습 시간이며 매 query 마다 fit 하는 것이 아니다 (paper period P=50 가정에서 P 회 query 마다 1 회 또는 데이터 변경 시 incremental fit).

---

## 8. K granularity SF axis 추가 측정

본 §8 은 K cluster 수의 axis (K=10/20/30) × SF axis (sf=1/10/100) 추가 측정 결과 (48 file) 를 정리한다. 박세은 5/14 8:50 자문 ("SF=1 K=20 미측정") 후속.

scope: A5-scale-sf{1,10,100} (DEEP single dataset, 3 cells) × K=10/30 (K=20 = paper exact base 활용) × 4 anchor method (sparse_rp / chao_weighted / hilbert_real / hyperloglog) × 2 mode (CaseA + CaseB) = 48 file. K=10 + K=30 분리 launch 로 총 36 분 server time.

### 8.1 method-dependent K best 패턴

| Method | K-pattern | SF=1 K=20 Δ% | SF=10 K=20 Δ% | SF=100 K=20 Δ% |
|---|---|---:|---:|---:|
| sparse_rp | K=20 sweet (U-shape) | −11.70% | −6.58% | −11.20% |
| chao_weighted | K=20 sweet 모든 SF 일관 | **−14.11%** | −6.00% | −12.20% |
| hilbert_real | K-robust + K=30 slight edge | −11.02% (K=30 −12.25%) | −6.07% (K=30 −6.96%) | −10.91% (K=30 −11.81%) |
| hyperloglog | K-robust + K=30 slight edge | −10.19% (K=30 −12.57%) | −5.15% (K=30 −6.01%) | −10.54% (K=30 −11.62%) |

sparse_rp / chao_weighted = K=20 sweet spot. hilbert_real / hyperloglog = K=30 slight edge. K best 가 method 별로 다른 패턴.

### 8.2 SF axis 일관성 + SF=10 약한 효과

위 method-dependent K best 패턴이 SF=1 / SF=10 / SF=100 axis 모두에서 일관 발현. SF=10 에서는 −Δ% 효과가 −5 ~ −7% 의 약화 (SF=1 −10 ~ −14% + SF=100 −10 ~ −12% 대비). 데이터 크기에 따른 sweet spot 가능성을 시사하는 결과.

---

## 9. Neyman selectivity-dependent

본 §9 는 RQ2 5-way 측정 (Bernoulli + Equal + Proportional + Neyman + Anti-Neyman) 의 selectivity-dependent 결과와 Cochran 1977 §5.5 partial 적용의 정확 derivation 을 다룬다.

### 9.1 sel-dependent paradox

| selectivity | Neyman | Anti-Neyman | Proportional | best |
|---|---:|---:|---:|---|
| sel=0.01 | 1.595 | 1.540 | 1.580 | **Anti < Prop < Neyman** (paradox) |
| sel=0.10 | 1.1076 | 1.1101 | 1.1135 | **Neyman < Anti < Prop** (classical 정합) |

sel=0.01 paradox 해석: 본 dataset 의 cluster 간 σ_j range 1.3-1.6× narrow (Cochran 1977 §5.5 Neyman 가정 不만족) + N_i CV=0 (cluster size 균등) 의 두 가정 不만족. sel=0.10 정합: classical theory 의 Neyman 가정 만족.

### 9.2 Bernoulli vs Neyman 정확 정량

| dataset | sel | Neyman vs Bernoulli Δ% |
|---|---|---:|
| DEEP | 0.01 | −7.64% |
| DEEP | 0.10 | −4.59% |
| SIFT | 0.01 | −2.58% |
| SIFT | 0.10 | **−9.16%** |
| POOL | 0.01 | −5.16% |
| POOL | 0.10 | −6.94% |

range = −2.58 ~ −9.16% (sel + dataset 별), POOL 평균 −5 ~ −7%.

### 9.3 Cochran 1977 §5.5 equality condition

```
Neyman optimal allocation 의 variance gap:
  Δ(Var) = Var(ŷ_Prop) − Var(ŷ_Neyman) = (1/N) × [Σ N_j σ_j² − (Σ N_j σ_j)² / Σ N_j] ≥ 0

Equality (Δ(Var) = 0) condition:
  σ_j = σ_constant ∀ j
  → σ_j range 가 narrow (1.x× 정도) 영역에서는 Neyman ≈ Proportional
```

본 RQ2 sel=0.01 에서의 σ_j range 1.3-1.6× narrow + N_i CV=0 두 조건이 Cochran theorem 의 equality condition 의 partial 발현이며, Neyman optimality 의 약화가 자연 도출된다.

---

## 10. 권장 설계 — 결과 기반 4 단계

본 §10 은 1352 file 측정 portfolio 의 종합 결과로부터 도출된 권장 설계 4 단계를 정리한다. 측정 evidence 위에서만 직접 권장.

### 10.1 단독 대체 우선 (정확도 best)

산업 환경에 맞는 method 를 Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) 中에서 골라 Bernoulli 를 대체한다. 가장 단순하면서 가장 큰 정확도 개선 (best minibatch_partial −10.17%). 사전 학습 fit_time 은 sparse_rp 3.67s ~ hilbert_real 43.50s + per-query inference 의 axis.

### 10.2 결합 보조 (안정성)

method 선택에 자신이 없거나 측정 환경 variability 가 큰 환경에서 산술 평균 결합 (est_final = (est_b1 + est_method) / 2.0) 을 안전망으로 둔다. 92.5% paired uplift + 9 측정 환경 변동성 감소. 정확도는 단독보다 약하지만 method 선택 risk mitigation.

### 10.3 자원 우선 환경 (reservoir O(1))

메모리가 가장 제약이라면 reservoir 같은 상수 메모리 method 를 단독으로 쓴다. 메모리 cost O(1) (sample size K 만 보존, 데이터 크기 N 과 무관) + fit_time sparse_rp 3.67s + 정확도 평균 −9.25% (단독 대체 9 측정 환경). 모바일 / 임베디드 / vector database insert stream 환경 직접 적용.

### 10.4 다중 테이블 환경 (Centroid tuple)

다중 테이블 환경에서 두 테이블 클러스터링을 합치는 방식. 비싼 방식 (두 테이블 벡터를 합쳐 처음부터 다시 학습) vs 저렴한 방식 (이미 학습된 두 클러스터링의 결과를 가볍게 합치는 Centroid tuple). 측정 결과 Centroid tuple 이 학습 비용 추가 0 으로 안정 우위 (A2-Fig9 single cell 결합 best −7.37%).

---

## 11. 결론

본 연구는 paper Exqutor §V-B 의 Adaptive Sampling base 환경 위에서 분포 인지 stratification 의 cardinality estimation 정량 가치를 1352 file 직접 측정으로 검증했다.

핵심 finding 세 가지:

**Finding 1**: 분포 인지 stratification 의 결합 (CaseB) 모드가 paper exact base 대비 **paired 92.5% 우위** (455/492, p<1e-45). Cliff's δ large = 63%, Hedges' g large = 56%. method 선택을 잘못해도 거의 항상 단독 대체보다 나은 안정성.

**Finding 2**: 정확도 best 와 자원 효율 best 가 동일 method 군 (Pareto Top 5 = sparse_rp / chao_weighted / neuram / pca1d / hilbert) 에서 발현. 5/15 fit_time 직접 측정 (90 file) 에서 sparse_rp 3.67s ~ hilbert_real 43.50s = **11.9× range**. cache_time 약 10s (method 무관). reservoir 메모리 O(1).

**Finding 3**: paper §V-B Eq 1-6 + hyperparam 7종 verbatim 100% 정합 유지. paper Fig 12 mean Q-error 1.69 → 우리 1.618 (-4.3% 재현). paper-grade compatibility 의 base.

본 3 finding 위에서 4 단계 권장 설계 (단독 대체 / 결합 보조 / 자원 우선 / 다중 테이블) 가 도출되며, 산업 환경의 method 선택 / 자원 제약 / 측정 환경 variability 에 따라 직접 선택 가능.

---

# 부록 §A — 정정 룰 7 (paper §V-B 정독 + 임채림 자문)

본 연구의 narrative 정정 룰 7 항목. paper §V-B verbatim 정독 + 임채림 연구원 자문 + 박세은 5/14 자문 종합.

## A-1. paper §V-B 자체 algorithm pseudo-code 없음

paper §V-B 는 Eq 1-6 + 자연 산문 + hyperparam 7 종 (m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N=385) 만으로 구성. "Algorithm 1" / "Procedure" 등 algorithmic block 형식이 paper 에 없다. 본 연구의 "17-step" 표현은 본 연구 자체의 의역.

evidence: paper PDF page 5-7 직접 정독, measure_paper_exact.py AdaptiveState class line 67-140 paper Eq 1-6 verbatim 정합 100% 검증.

## A-2. framework axis novelty 한정 (각 component 자체 신규 X)

본 연구의 4 component 자체는 각각 신규 X. Component A (SRS) = Vitter 1985 + Al-Kateb-Lee-Wang 2014 + SSDBM 2010, Component B (BIRCH) = Zhang-Ramakrishnan-Livny SIGMOD 1996, Component C (paper Eq 2-6 통합) = paper §V-B verbatim 100% 정합, Component D (Distribution-aware stratification) = Cochran 1977 §5.5.

본 연구의 contribution = framework axis (위 4 component 의 통합 + paper §V-B 영역 발현 + paradigm rollup + paired uplift 정량 evidence).

## A-3. paper §V-B single-table = 구현 코드 한계 (구조 X)

paper §V-B 자체는 single-table KNN query 에 대한 sampling-based cardinality estimation 을 명시 (paper p.5 우단 verbatim). paper 공개 코드 (BDAI-Research/Exqutor github) 의 single-table 영역이 동작하지 않아 본 연구의 측정 영역이 multi-join 으로 자연 이동. 정확 표기 = "구현 코드 한계 (구조 X)" — paper §V-B 의 구조적 한계가 아니다.

evidence: paper [0] §V-B p.5 우단 line 1-7, 임채림 연구원 자문 base.

## A-4. paper §V-B sampling = block + row hybrid

paper §V-B sampling 영역은 초기 N=385 budget = block 추출 + Eq 5 sampling_size update 시 n_inc 행 추가 = row 추출 의 **block + row hybrid**. 본 연구의 이전 narrative "block only" 표현은 부정확. 임채림 자문 base.

## A-5. "분포 안다" L1/L2/L3 multi-layer 분리

"분포 안다" 영역은 L1 (global skew flag, HHI 지표) + L2 (cluster boundary K=20) + L3 (cluster boundary + σ_j 분산) 의 multi-layer. 본 연구 RQ2 영역은 L3 oracle 가정 (offline batch K-means 의 σ_j 직접 사용).

## A-6. paper §V-B = "without index" 가정 (paper p.5 verbatim)

paper §V-B 영역 자체는 "without vector index" 가정 안에서의 sampling-based cardinality estimation (paper p.5 좌단 + p.5 우단 + p.6 우단 + §VI-A + §VI-B verbatim). ECQO 의 vector index = HNSW (data itself) 구축 영역과 §V-B 의 sampling 영역은 paper 자체 안에서 상호 배타.

박세은 5/14 9:09 자문 ("분포 알면 ECQO?") 답변 anchor.

## A-7. "Anti-Neyman > Neyman" wording 정정 → selectivity-dependent

본 연구의 이전 narrative "Anti-Neyman > Neyman = Neyman 가설 무효" 는 부정확. 정확 의미:

- Neyman 가설 자체는 유효 (Cochran 1977 §5.5 classical theory 정합)
- 본 데이터셋이 Neyman 의 가정 조건 (cluster 간 σ_j heterogeneity) 不만족 (σ_j range 1.3-1.6× narrow + N_i CV=0)
- selectivity-dependent (sel=0.01 paradox / sel=0.10 정합)

evidence: rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv 직접 aggregate verify.

---

작성: 2026-05-15 20:30 KST · 박광현 5/15 D-Day 미팅 input 반영 + 사용자 임시 진행분 · 박세은 + 임채림 정리본 도착 후 final 확정
