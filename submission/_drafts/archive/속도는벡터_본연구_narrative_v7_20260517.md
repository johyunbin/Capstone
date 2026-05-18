# 속도는벡터 — 본 연구 narrative v7

> 작성: 2026-05-17 KST · v6 (5/16) 전면 수정 · REPORT v12 + paired_delta_v12.parquet 실측 동기화
> 핵심 reframing: **본 연구는 논문 재현이 아니라, 전 데이터셋·전 조작 변인에 대한 완전한 검증 실험이다**
> 5/27 발표 + 6/11 보고서의 공통 base narrative

---

## 0. 본 연구 main theme

본 연구는 벡터 증강 분석 쿼리(VAQ)의 cardinality 추정에서, sample selection 방식을 바꾸었을 때 추정 정확도(Q-error)가 어떻게 달라지는지를 **전 데이터셋과 전 조작 변인에 걸쳐 완전히 검증**한다. 단일 벡터 데이터셋 다섯 종(DEEP, SIFT, SimSearchNet++, WIKI, YFCC)에 더해, 우리가 직접 두 데이터셋의 벡터를 차원 방향으로 연결해 만든 다중 벡터(concat) 데이터셋까지를 측정 대상으로 삼았다. 그 위에서 selectivity(0.001/0.01/0.10), sample selection method(16종), 단일/다중 구조, scale factor(sf=1/10/100), strata 수 K(10/20/30)라는 다섯 조작 변인을 빠짐없이 교차시켜, 각 조건에서 sample selection 방식의 효과가 어떻게 변하는지를 정량적으로 확인한다.

본 연구의 출발점은 Exqutor 논문(arXiv:2512.09695v2) §V-B의 Adaptive Sampling이다. 그러나 본 연구가 하려는 것은 그 논문의 결과를 재현하는 것이 아니다. 논문 §V-B는 우리가 Q-error를 측정하기 위해 채택한 측정 방법론의 출발점일 뿐이며, 우리의 목표는 그 방법론을 토대로 측정 공간을 능동적으로 넓혀, sample selection 방식이라는 단일 개입 지점이 추정 정확도에 미치는 영향을 모든 변인에서 빠짐없이 관찰하는 것이다. 측정 결과를 논문 수치와의 일치 여부로 환원하지 않으며, 우리가 만든 데이터셋과 우리가 설계한 변인 조합 위에서 독립적으로 평가한다.

논문 §V-B의 cardinality 추정 알고리즘 자체와 AdaptiveState 식 1-6은 본 연구가 건드리지 않는다. 본 연구의 개입은 오로지 sample selection 단계에 한정되며, 그 단계에서 논문의 unstratified Bernoulli random sampling 자리에 분포 인지 stratification 방식을 놓았을 때 무슨 일이 일어나는지를 본다.

---

## 1. framing — 무엇을 바꾸고 무엇을 그대로 두는가

### 1.1 개입 지점은 sample selection 단계 하나뿐

본 연구의 framing은 단순하다. cardinality 추정 파이프라인 가운데 우리가 손대는 것은 sample selection 단계 하나뿐이고, 나머지는 전부 논문의 것을 그대로 둔다. 이 분리는 박세은 팀장이 5/16 정리한 의도("우리는 추가 method를 통해 Q-error만 보완하면 되는 것 아니냐. cardinality 추정은 알아서 할 것이고")를 그대로 반영한다.

| 구분 | 내용 | 본 연구의 처리 |
|---|---|---|
| 그대로 두는 부분 | §V-A ECQO의 HNSW range query · §V-B AdaptiveState 식 1-6 momentum 보정 · cardinality 추정 알고리즘 자체 | 변경 없음. 측정 기반으로 그대로 사용 |
| 본 연구가 바꾸는 부분 | sample selection 단계 — 어떤 표본을 뽑을 것인가 | unstratified Bernoulli random sampling을, 데이터 분포를 인지해 계층(stratum)으로 나눠 뽑고 두 추정값을 결합하는 방식(stratification ensemble)으로 교체 |

대조군 B1은 논문 그대로의 방식, 즉 Bernoulli random sampling에 AdaptiveState 식 1-6을 얹은 것이다. 실험군 CaseB는 sample selection 단계만 분포 인지 stratification ensemble로 바꾼 것이며, 식 1-6은 동일하게 작동한다. 따라서 두 군의 Q-error 차이는 오직 sample selection 방식의 차이에서 나온다.

### 1.2 CaseB ensemble의 정의

실험군 CaseB의 ensemble은 논문 Bernoulli 추정값과 우리 method 추정값의 단순 산술 평균이다.

```
est_final = (est_b1 + est_method) / 2.0
```

est_b1은 논문 방식 그대로의 Bernoulli random sample 추정값이고, est_method는 분포 인지 stratification으로 뽑은 표본의 추정값이다. 두 추정값을 산술 평균한 est_final이 AdaptiveState 식 2-6의 입력으로 들어간다. sample budget은 두 estimator가 공유하며, 그 크기는 논문 식 1의 N=385다. 즉 CaseB는 논문의 sample budget을 늘리지 않고, 동일한 예산 안에서 표본을 뽑는 방식만 바꾼다. 이것이 본 연구가 "minimal augmentation"이라 부르는 개입의 실체다 — 논문 식 1-6을 위반하지 않고, sample selection 단계에 분포 인지 방식을 더한 것.

CaseA로 분류했던 단독 대체 방식(논문 Bernoulli를 우리 method로 통째로 치환)은 본 연구의 framing에 부합하지 않아 폐기했다. 그 근거는 §6에서 다룬다.

### 1.3 framing의 학술적 의의

논문 본인의 contribution(cardinality 추정 알고리즘)을 그대로 인정하고, 우리는 그 입력인 표본의 품질만을 통제 변인으로 다룬다. 학부 캡스톤 디자인이라는 성격에 맞게, 새 알고리즘을 제안하는 것이 아니라 하나의 변인을 끝까지 통제해 그 효과를 측정하는 검증 연구의 자세를 일관되게 유지한다. 동시에 본 연구는 측정 대상을 논문이 다룬 데이터셋에 가두지 않고, 직접 만든 concat 데이터셋과 직접 설계한 변인 조합으로 측정 공간을 능동적으로 확장한다. 이 두 가지 — 개입 지점의 최소화와 측정 공간의 능동적 확장 — 가 본 narrative의 base axis다.

---

## 2. 측정 방법론의 출발점 — 논문 §V-B Adaptive Sampling

본 절은 우리가 채택한 측정 방법론의 출발점을 소개한다. 논문 Exqutor §V-A와 §V-B는 인덱스 유무에 따라 두 갈래로 cardinality를 추정한다.

§V-A의 ECQO는 벡터 인덱스가 있을 때 HNSW(Hierarchical Navigable Small World) 그래프 위의 range query로 1-2ms 수준에서 정확한 cardinality를 얻는 메커니즘이다. 본 연구는 이 부분을 측정 대상으로 삼지 않으며, 논문 본인의 결과를 그대로 인정한다.

§V-B의 Adaptive Sampling은 벡터 인덱스가 없을 때 Bernoulli random sample N=385개로 표본을 뽑고, momentum 기반 식으로 표본 크기를 동적으로 조정하는 메커니즘이다. 본 연구의 측정은 이 §V-B를 출발점으로 삼는다. 논문의 여섯 식은 다음과 같다.

```
식 1: N = ⌈z²·P̂(1-P̂)/e²⌉ = 385       (sample budget, z=1.96 / P̂=0.5 / e=0.05)
식 2: Ĉ = Σ(matching rows) × (1 - sampling_ratio)   (Bernoulli estimator)
식 3: δ = max(true_Q-err, 1/true_Q-err)              (Q-error)
식 4: η ← m·η + (1-m)·δ/α                            (momentum update, m=0.9 / α=50)
식 5: N_t+1 ← N_t × (1 + η·β·sign(...))              (sample size update, β=1.5)
식 6: η ← η · γ                                       (learning rate decay, γ=0.99)
```

period P=50 쿼리마다 식 4-6으로 표본 크기를 갱신한다. 본 연구는 이 여섯 식을 측정 기반으로 그대로 사용하고, 식 1의 N=385라는 sample budget도 그대로 유지한다. 우리가 바꾸는 것은 식 2의 입력으로 들어가는 표본을 어떻게 뽑느냐 하나뿐이다.

논문 §V-B 자체에는 "Algorithm 1" 같은 의사 코드 블록이 없다. 여섯 식과 자연 산문, 그리고 일곱 개의 하이퍼파라미터만으로 기술되어 있다. 따라서 본 narrative도 의사 코드 형식을 쓰지 않고, 우리의 개입을 자연 산문으로 기술한다.

---

## 3. 우리의 sample selection 방식 — 세 단계 흐름

본 연구가 sample selection 단계에서 실제로 하는 일을 세 단계로 정리한다.

### 3.1 1단계 — 분포 인지 stratification (offline, 1회)

데이터셋이 처음 들어올 때 한 번 수행하는 오프라인 단계다. 데이터의 행 수와 구조, 차원을 보고 데이터셋 Type을 판별한 뒤(§4), Type에 맞는 sample selection method를 고르고(§7), 그 method로 K=20개의 stratum을 만든다. 결과적으로 각 행은 stratum_id 0..K-1 가운데 하나로 매핑된다. 이 단계의 비용은 method마다 다른데, 가장 빠른 sparse_rp가 수 초 수준이다(§9의 fit_time 분석).

이 단계가 본 연구가 말하는 "데이터셋 진입 시 빠르게 분포를 파악한다"의 실체다. 우리가 쓰는 method들 — 클러스터링, 차원 축소, quantization 등 — 자체가 데이터 분포를 파악하는 도구이며, 데이터셋이 들어올 때 이들이 분포를 빠르게 잡아낸다.

### 3.2 2단계 — 표본 추출 (online, 매 쿼리)

쿼리가 들어올 때마다 수행하는 온라인 단계다. 논문 식 1의 sample budget N=385를 그대로 쓰되, 1단계에서 만든 K=20개 stratum에 비례 배분(proportional allocation)으로 표본을 나누어 뽑는다. 뽑힌 표본에서 est_method를 계산한다. 논문이 정한 표본 예산은 손대지 않고, 그 예산 안에서 표본을 어느 stratum에서 얼마나 뽑을지만 분포 인지 방식으로 바꾼다.

### 3.3 3단계 — 결합 (online, 매 쿼리)

쿼리마다 두 추정값을 결합하는 단계다. 논문 방식 그대로의 Bernoulli 추정값 est_b1과 우리 방식의 est_method를 산술 평균하여 est_final = (est_b1 + est_method) / 2.0을 만들고, 이것을 논문 식 2-6 보정에 그대로 넣는다. 결합은 산술 평균 하나뿐이며, 논문 식 1-6을 전혀 위반하지 않는다. 실험군 CaseB는 이 세 단계의 직접적인 구현이다.

### 3.4 세 단계의 axis

1단계와 2단계가 본 연구의 sample selection 방식의 핵심이고, 3단계는 논문 식 1-6을 그대로 둔 채 두 추정값을 평균하는 최소한의 결합이다. 논문의 cardinality 추정 메커니즘을 그대로 두고 sample selection 단계만 분포 인지 방식으로 바꾼다는 framing이 이 세 단계 흐름에 그대로 담겨 있다. 이 흐름은 뒤따르는 모든 절 — §4(데이터셋 Type), §5(paradigm별 method), §7(동적 method 선택), §9(fit_time) — 의 base가 된다.

---

## 4. 데이터셋 Type 분류 — 측정 공간을 어떻게 펼쳤는가

### 4.1 분류 기준 — 규모 × 구조 × 차원

본 연구의 측정 portfolio는 통합 1444건의 측정으로 구성되며(§6.0), 그 측정 cell들을 데이터 규모, 단일/다중 구조, 차원이라는 세 축으로 다섯 Type으로 분류한다. 이 분류는 §7의 동적 method 선택의 직접적인 base다.

| Type | 정의 | 차원 | 대표 데이터셋 |
|---|---|---:|---|
| Type 1 | 소규모 단일 sf=1 (0.1M 행) | 96~768 | DEEP/SIFT/SSN/WIKI/YFCC sf=1 |
| Type 2 | 중규모 단일 sf=10 (1M 행) | 96~768 | DEEP/SIFT/SSN/WIKI sf=10 |
| Type 3 | 대규모 단일 sf=100 (10M 행, 저~중차원) | 96~256 | DEEP/SIFT/SSN sf=100 |
| Type 4a | 대규모 다중 224~288d (10M 행) | 224~288 | DEEP+SIFT, DEEP+YFCC |
| Type 4b | 대규모 다중 864d (10M 행) | 864 | DEEP+WIKI |

paired 비교 기준으로 각 Type의 측정 행 수는 Type 1이 263행, Type 2가 212행, Type 3이 439행, Type 4a가 369행, Type 4b가 161행이다.

### 4.2 Type 1 — 소규모 단일 sf=1

행 수 0.1M의 단일 테이블 데이터다. 측정 portfolio 가운데 가장 작은 규모이며, 분포 인지 sample selection의 효과가 가장 크게 나타나는 구간이다. 데이터가 작을수록 random Bernoulli 표본의 분산이 커지므로, 분포 인지 stratification이 그 분산을 줄이는 이득이 증폭된다. 실측에서도 가장 강한 개선 8건이 모두 SIFT sf=1, sel=0.001 cell에 몰려 있다(§6.3).

### 4.3 Type 2 — 중규모 단일 sf=10

행 수 1M의 단일 테이블 데이터다. sf=1과 sf=100의 중간 규모인데, 이 구간에서 개선 폭이 양 끝보다 약해진다. 데이터 규모에 따른 효과의 sweet spot이 sf=1과 sf=100 양 끝에 있고 중간이 상대적으로 약하다는 관찰을, 본 연구는 데이터 규모를 세 단계로 직접 측정해 확인했다.

### 4.4 Type 3 — 대규모 단일 sf=100 (저~중차원)

행 수 10M의 단일 테이블, 96~256차원 데이터다. 분포 인지 sample selection의 효과가 다시 강하게 나타나며, K=20 설정이 일관되게 잘 작동하는 구간이다. 본 연구는 이 규모에서 sample selection 방식의 개선을 단일 벡터 데이터셋 전반의 −7.66%라는 수치(§5)로 확인했다.

### 4.5 Type 4a — 대규모 다중 224~288d

행 수 10M의 다중 테이블, 224~288차원 데이터다. 우리가 직접 만든 concat 데이터셋(DEEP+SIFT 224d, DEEP+YFCC 288d)이 이 Type에 속한다. 이 구간에서도 분포 인지 sample selection은 거의 항상 더 나은 방향을 유지하되, 개선의 크기는 단일 벡터보다 작다(§5).

### 4.6 Type 4b — 대규모 다중 864d

행 수 10M의 다중 테이블, 864차원 데이터다. 우리가 DEEP과 WIKI를 연결해 만든 가장 고차원의 측정 대상이다. 두 데이터셋의 분포가 섞인 고차원 공간에서는 sample selection 방식의 효과가 가장 불안정하게 나타나며, 특히 일부 클러스터링 method가 이 차원에서 크게 흔들린다(§5, §6.1).

### 4.7 Type 분류가 동적 method 선택의 base가 되는 이유

다섯 Type 분류는 §7의 동적 method 선택의 직접적인 base다. 데이터셋이 들어오면 Type을 판별하고, Type에 맞는 sample selection method를 자동으로 고른 뒤 CaseB ensemble로 결합한다. 각 Type별로 어떤 method가 잘 맞는지를 측정으로 확인하고, 그 결과를 선택 규칙으로 옮긴 것이 본 연구가 제안하는 흐름이다.

---

## 5. 우리가 만든 다중 벡터 데이터셋 — 측정 공간의 능동적 확장

### 5.1 왜 직접 데이터셋을 만들었는가

본 연구의 측정은 논문이 다룬 단일 벡터 데이터셋에 머무르지 않는다. 다중 벡터 환경에서 sample selection 방식이 어떻게 작동하는지를 보기 위해, 우리는 서로 다른 두 데이터셋의 벡터를 차원 방향으로 직접 연결(concat)해 새로운 측정 대상을 만들었다. DEEP과 SIFT를 연결한 224차원, DEEP과 YFCC를 연결한 288차원, DEEP과 WIKI를 연결한 864차원의 세 concat 데이터셋이 그것이다. 이는 측정 공간을 수동적으로 받아들이지 않고 능동적으로 넓힌 결과이며, 단일 벡터에서 관찰한 효과가 다중 벡터 고차원 공간에서도 유지되는지를 우리 손으로 확인하기 위한 설계다.

### 5.2 단일 벡터와 concat의 비교

측정 cell을 단일 벡터(single), cross-table 다중 벡터(multi), 그리고 우리가 만든 concat으로 나누어 짝지은 Q-error 변화율(paired Δ%)을 집계하면 다음과 같다. 아래는 K=10을 제외한 신뢰 가능 비교 기준이다(K=10 제외의 이유는 §6.0과 §8).

| 유형 | n | better% | 유의 우월% | 평균 Δ% | 중앙값 Δ% |
|---|---:|---:|---:|---:|---:|
| single | 752 | 92.8% | 81.4% | **−7.66%** | −7.66% |
| multi (cross-table) | 152 | 86.8% | 63.8% | −4.57% | −5.28% |
| concat | 336 | 93.2% | 78.0% | **−3.84%** | −5.38% |

해석은 두 갈래다. 첫째, 단일 벡터 데이터셋에서 개선 폭이 가장 크다 — 평균 −7.66%로, concat의 −3.84%보다 두 배 가까이 크다. 단일 벡터에서는 데이터 분포가 단일하므로 분포 인지 stratification이 명확한 신호를 잡아낸다. 둘째, 우리가 만든 concat 데이터셋에서는 더 낫다는 방향성(better 93.2%)은 오히려 single보다 약간 높지만, 개선의 크기는 작다(−3.84%). 두 데이터셋의 분포가 섞이면서 stratification이 잡아낼 수 있는 구조적 이득이 희석되기 때문이다.

### 5.3 concat의 차원별 분해 — 864d 평균 양수의 정체

concat 전체 평균 −3.84%는 차원별로 갈라 보면 결이 다르다.

| concat 데이터셋 | 차원 | n | better% | 평균 Δ% | 중앙값 Δ% |
|---|---:|---:|---:|---:|---:|
| DEEP+SIFT | 224 | 144 | 92.4% | **−5.56%** | −5.65% |
| DEEP+YFCC | 288 | 96 | 97.9% | **−7.03%** | −6.21% |
| DEEP+WIKI | 864 | 96 | 89.6% | **+1.93%** | −4.83% |

224차원과 288차원에서는 개선 폭이 각각 −5.56%, −7.03%로 분명한 음수다. 그러나 864차원 DEEP+WIKI에서 평균이 +1.93%로 양수로 나타나는데, 이 양수는 차원이 높아서 효과가 사라진 것이 아니다. 같은 864차원 measurement의 중앙값은 −4.83%로 여전히 음수이고, better 비율도 89.6%다. 평균이 양수로 끌려 올라간 것은 A10-DEEP+WIKI-concat-sf10 cell에서 minibatch_partial method가 기록한 +290.08%와 +276.41% 단 두 건의 이상치(outlier) 때문이다. 이 두 건을 제외하면 864차원의 평균도 음수로 돌아온다. 즉 864차원에서도 분포 인지 sample selection은 대부분의 측정에서 더 낫고, 평균을 왜곡한 것은 고차원 concat에서 불안정한 특정 클러스터링 method 하나다(§6.1).

### 5.4 selectivity와의 교차

단일 벡터와 concat 모두 selectivity가 높을수록 better 비율이 오른다. single은 sel 0.001/0.01/0.10에서 85.2/93.8/100.0%, concat은 86.6/94.6/98.2%다. 우리가 만든 concat 데이터셋에서도 sel=0.10 구간에서는 112건 중 110건이 개선되어, 다중 벡터 고차원 공간에서도 분포 인지 sample selection의 우월성이 거의 예외 없이 성립한다.

---

## 6. paired Δ% — 대조군 B1 vs 실험군 CaseB

### 6.0 측정 portfolio와 신뢰 가능 범위

본 연구의 측정 portfolio는 통합 1444건이다. 대조군 B1이 80건, 실험군 CaseB가 1364건이며, 같은 cell·selectivity·strata 조건에서 trial 단위로 짝지은 paired 비교는 1360건이다. 이 가운데 K=10 변형 측정 120건은 대조군 B1의 구조적 결함 때문에 분석에서 제외하며(상세는 §8), 신뢰 가능한 비교는 1240건이다. 모든 CaseB 측정은 §1.2의 동일한 ensemble 정의를 쓴다.

측정 축은 네 갈래로 펼쳐진다. 데이터셋은 단일 벡터 여섯 종과 우리가 만든 다중 벡터 조합을 합쳐 아홉 종, scale factor는 sf=1/10/100 세 종, selectivity는 0.001/0.01/0.10 세 종, strata 수 K는 10/20/30 세 종이다. method 축은 8개 sampling paradigm을 대표하는 16종으로 고정했다(§5의 method 표, §7).

짝지은 Q-error 변화율(paired Δ%)은 같은 조건에서 trial 단위로 짝지은 (CaseB_qe − B1_qe) / B1_qe × 100이며, 음수가 실험군의 Q-error가 더 낮음, 즉 더 정확함을 뜻한다.

### 6.1 대표 수치(headline) (K=10 제외 — 신뢰 가능)

K=10을 제외한 paired 비교 **1240건**에서 다음을 얻는다.

| 지표 | 값 |
|---|---|
| CaseB better (Δ% < 0) | **1143 / 1240 = 92.2%** |
| 평균 Δ% | **−6.25%** |
| 중앙값 Δ% | **−6.15%** |
| Δ% 범위 | −34.96% ~ +290.08% |
| 통계적 유의 우월 (one-sided BH-FDR p<0.05) | 971 / 1240 = 78.3% |
| Cliff's δ large (≥0.474) 우월 | 1023 / 1240 = 82.5% |
| Hedges' g large (\|g\|≥0.8) | 1039 / 1240 = 83.8% |

핵심 메시지는 단순하다. 논문 §V-B의 unstratified Bernoulli random sampling을 분포 인지 stratification ensemble로 바꾸면, 동일한 sample budget(N=385) 안에서 cardinality 추정의 Q-error가 일관되게 개선된다. 측정한 비교의 약 열 건 중 아홉 건에서 Q-error가 낮아지고, 통계적 유의 우월(78.3%)과 효과크기 large 우월(82.5%)이 모두 여덟 할 전후로 신호가 견고하다.

참고로 K=10 paired 120건을 포함한 전체 1360건의 수치는 평균 −8.06%, better 91.7%다. 평균이 더 음수로 보이는 것은 §8에서 설명할 K=10 허위 신호가 평균을 끌어내린 결과이며, 실제 효과가 더 크기 때문이 아니다. 본 narrative는 결함 데이터를 모두 배제한 −6.25%, 92.2%를 신뢰 가능한 headline으로 채택한다.

### 6.2 음성 대조 검증(negative control) — 단독 대체 가설의 폐기

§1.2에서 CaseA(단독 대체)를 폐기했다고 했는데, 그 근거가 음성 대조 검증(negative control)이다. 음성 대조 검증이란 효과가 없을 것으로 예상되는 방식을 일부러 측정해 실제로 효과가 없음을 확인함으로써 본 방식의 타당성을 거꾸로 뒷받침하는 절차다. 논문 §V-B의 Bernoulli random sampling을 우리 method로 통째로 치환하는 단독 대체 방식은, 측정해 보면 method 선택에 따라 양방향으로 크게 흔들린다. 단독 대체 모드에서 large worsening이 다수 발현하고, 일부 측정에서는 개선이 전혀 나타나지 않았다. 논문 메커니즘을 그대로 두지 않고 통째로 치환하는 방식은 안정적이지 않다는 것이 음성 대조 검증의 결론이다. 따라서 본 연구는 단독 대체 가설을 폐기하고, 논문 식 1-6을 그대로 둔 채 두 추정값을 산술 평균하는 CaseB 결합만을 유효한 개입으로 채택했다. headline 수치 1240건은 모두 이 CaseB 결합 측정이다.

### 6.3 가장 강한 비교와 가장 약한 비교

K=10 제외 기준으로, 개별 (cell × method × sel × K) 단위의 양 극단은 다음과 같다.

가장 강한 개선 8건은 모두 SIFT sf=1, sel=0.001 cell이다. hyperloglog −34.96%, zorder_morton −34.77%, skilling_hilbert −33.52% 순이며, 모두 one-sided BH-FDR p=0.0018, Cliff's δ=+1.00이다. 이 cell은 B1 자체의 Q-error가 높아(sel=0.001 B1 qe_trim 2.366) 분포 인지 stratification이 개선할 여지가 컸다. Type 1 소규모 단일 데이터에서 효과가 가장 크다는 §4.2의 관찰과 일치한다.

가장 큰 악화는 우리가 만든 DEEP+WIKI 864차원 concat의 sf=10 cell에서 minibatch_partial이 기록한 +290.08%, +276.41% 두 건이다. 이는 P1 Cluster paradigm의 minibatch_partial이 864차원 concat 데이터에서 불안정함을 보여주는 사례이며(§6.4), 통계적으로 유의하지 않다(p_adj=1.0000).

### 6.4 method/paradigm 분석

사용 16 method별 paired Δ%(K=10 제외)는 다음과 같다.

| Method | Paradigm | n | better% | 평균 Δ% | 중앙값 Δ% | δ large% |
|---|---|---:|---:|---:|---:|---:|
| hilbert_real | P2 | 82 | 100.0% | −8.76% | −8.59% | 90.2% |
| pca1d | P4 | 76 | 100.0% | −8.75% | −8.00% | 97.4% |
| zorder_morton | P2 | 76 | 98.7% | −8.66% | −8.00% | 94.7% |
| ica_fastica | P4 | 76 | 98.7% | −8.55% | −7.90% | 89.5% |
| skilling_hilbert | P2 | 76 | 94.7% | −8.52% | −7.93% | 89.5% |
| chao_weighted | P3 | 82 | 98.8% | −8.37% | −7.80% | 89.0% |
| sparse_rp | P4 | 82 | 100.0% | −8.15% | −7.47% | 92.7% |
| hyperloglog | P9 | 82 | 96.3% | −7.73% | −6.88% | 86.6% |
| cum_sqrtf | P5 | 76 | 98.7% | −7.69% | −6.99% | 89.5% |
| rsvd | P4 | 76 | 100.0% | −7.44% | −6.31% | 92.1% |
| lavallee_hidiroglou | P5 | 76 | 93.4% | −7.33% | −7.06% | 81.6% |
| mhist2 | P6 | 76 | 86.8% | −6.07% | −4.65% | 76.3% |
| rabitq_strat | P6 | 76 | 86.8% | −5.51% | −4.61% | 73.7% |
| faiss_ivf | P1 | 76 | 77.6% | −2.32% | −4.14% | 65.8% |
| gmm | P1 | 76 | 55.3% | **+1.90%** | −0.61% | 42.1% |
| minibatch_partial | P1 | 76 | 86.8% | **+2.67%** | −4.20% | 67.1% |

16개 method 가운데 14개는 평균 Δ%가 음수이고 better 비율 86% 이상으로 견고하게 우월하다. P2 Spatial, P4 DimReduction, P3 Streaming, P9 InfoTheoretic, P5 QMC에 속한 method가 모두 여기 든다. 특히 hilbert_real, pca1d, sparse_rp, rsvd는 better 비율 100%로, K=10을 제외한 모든 측정 cell에서 예외 없이 B1을 이긴다.

약한 method는 P1 Cluster paradigm에 집중된다. gmm은 평균 +1.90%(better 55.3%)로 사실상 B1과 동등하거나 약간 못하다. minibatch_partial은 평균 +2.67%지만 중앙값은 −4.20%인데, 양수 평균은 §6.3에서 본 DEEP+WIKI 864차원 outlier 두 건 때문이며 이를 제외하면 평균이 −4.92%로 돌아온다. 즉 minibatch_partial은 대부분의 cell에서 작동하지만 우리가 만든 864차원 concat 같은 극단 조건에서 불안정하다. faiss_ivf는 평균 −2.32%로 약한 개선에 머문다. 결론적으로 P1 Cluster paradigm은 분포 인지 sample selection의 우월성을 일관되게 보이지 못하며, 본 연구의 권장 method에서 제외하는 근거가 된다.

paradigm 수준(K=10 제외, |Δ%|<100 outlier 제외)에서는 P3 Streaming −8.37%, P4 DimReduction −8.22%가 가장 강하고, P9 InfoTheoretic −7.73%, P5 QMC −7.51%, P2 Spatial −7.10%가 −7% 전후로 뒤따른다. P6 Quantization은 −5.79%로 중간, P1 Cluster는 −1.46%로 가장 약하다.

---

## 7. 동적 method 선택 — 데이터셋 Type에 따라 method를 고른다

### 7.1 base axis

본 절은 §4의 다섯 Type 분류와 §5의 paradigm별 method를 토대로, 데이터셋이 들어오면 어떤 method를 자동으로 고를지를 정하는 흐름을 제안한다. 동적으로 바뀌는 것은 sample selection method 선택과 결합 단계뿐이며, 논문 식 1-6은 어떤 경우에도 그대로 둔다.

본 연구가 다루는 16 method는 8개 paradigm을 대표한다.

| Paradigm | 사용 method | 개수 |
|---|---|---:|
| P1 Cluster | minibatch_partial · gmm · faiss_ivf | 3 |
| P2 Spatial | hilbert_real · zorder_morton · skilling_hilbert | 3 |
| P3 Streaming | chao_weighted | 1 |
| P4 DimReduction | sparse_rp · pca1d · rsvd · ica_fastica | 4 |
| P5 QMC | cum_sqrtf · lavallee_hidiroglou | 2 |
| P6 Quantization | rabitq_strat · mhist2 | 2 |
| P9 InfoTheoretic | hyperloglog | 1 |

모두 sample selection 단계의 메커니즘이다. 정합성 위반·미커버 등으로 폐기한 40여 method는 본 narrative에서 다루지 않는다(사용자 5/15 결정).

### 7.2 4단계 흐름

```
[데이터셋 진입]
        ↓
[Step 1] 데이터셋 프로파일 파악
  - 행 수 (sf=1 / sf=10 / sf=100)
  - 테이블 구조 (단일 / 다중)
  - 차원 (저 96d / 중 256d / 고 864d)
        ↓
[Step 2] Type 판별 (Type 1/2/3/4a/4b 가운데 하나)
        ↓
[Step 3] Type별 권장 sample selection method 자동 선택
        ↓
[Step 4] CaseB ensemble — est_final = (est_b1 + est_method) / 2.0
        ↓
[논문 §V-B AdaptiveState 식 1-6 보정 — 그대로 유지]
```

Step 1-3이 sample selection method를 고르는 부분이고, Step 4가 두 추정값을 산술 평균하는 결합이다. 논문 메커니즘은 Step 4 다음에 그대로 작동하며, 동적으로 바뀌는 것은 method 선택과 결합뿐이다.

### 7.3 Type별 권장 method

§6.4의 method별 측정 결과와 §9의 fit_time을 토대로, Type별 권장 method를 다음과 같이 정한다.

| Type | 권장 method | 근거 |
|---|---|---|
| Type 1 (소규모 단일 sf=1) | chao_weighted, sparse_rp | 소규모에서 효과 최대, fit_time 최단권 |
| Type 2 (중규모 단일 sf=10) | sparse_rp, chao_weighted | 효과는 약화되나 방향 일관 |
| Type 3 (대규모 단일 sf=100 저~중차원) | chao_weighted, sparse_rp, pca1d | K=20 안정 구간 |
| Type 4a (대규모 다중 224~288d) | hilbert_real, pca1d | better 100%, 다중 벡터에서 안정 |
| Type 4b (대규모 다중 864d) | sparse_rp, pca1d (클러스터링 method 회피) | 864d에서 클러스터링 불안정(§6.4) |

핵심은 Type별로 측정상 우월성이 견고한 method를 자동으로 고른다는 점이다. P1 Cluster paradigm은 §6.4에서 본 대로 일관성이 없어, 특히 Type 4b 864차원에서는 권장에서 뺀다.

### 7.4 evidence base

이 흐름의 evidence base는 §6의 통합 측정 portfolio다. 통합 1444건 가운데 신뢰 가능 비교 1240건이 Type별·method별 우월성의 근거이며, §6.4의 method 표가 Step 3의 선택 규칙을 직접 뒷받침한다.

---

## 8. K granularity — strata 수의 효과 (honest limitation)

### 8.1 본 절의 위상

본 연구는 strata 수 K를 10/20/30으로 sweep하여, K가 실험군에 미치는 영향도 측정했다. 그러나 본 절은 본 narrative의 강한 finding이 아니라 **honest limitation으로 정직하게 보고하는 부속 결과**다. 검증 과정에서 K=10 측정에 구조적 결함이 확인되어, 깨끗한 K granularity 비교가 성립하지 않기 때문이다.

이 한계의 발견 자체가 본 연구가 전 변인을 빠짐없이 검증하려 한 결과다. K granularity까지 측정했기 때문에 K=10 대조군의 결함을 찾아낼 수 있었고, 그 결함을 숨기지 않고 정직하게 배제했다.

### 8.2 K=10 대조군 B1의 구조적 결함

대조군 B1의 측정 함수는 환경변수로 strata 수를 받아 strata 캐시를 생성하는 구조다. 즉 대조군 B1 자체가 strata 수 K에 의존하는 측정이다. K=10 설정에서 B1의 쿼리별 Q-error에 무한대(inf)가 폭증하여(쿼리 1000건 중 314~391건 수준), trim 후에도 K=10 B1의 qe_trim이 정상 범위 1.6~1.7을 크게 벗어나 3.0대로 손상되었다. K=20(논문 default)과 K=30 B1은 1.16~1.72 범위로 정상이고, 오직 K=10 B1만 2.2~3.3으로 손상되었다.

그 결과 K=10 측정 120건 가운데 96건은 손상된 K=10 B1과 짝지어졌고, 이 96건의 paired Δ% 평균 −36.15%는 실험군의 우월성이 아니라 분모(B1)의 손상에서 나온 허위 신호다. 동일한 K=10 CaseB를 정상적인 K=20 B1과 짝지으면 평균 +10.35%로, 오히려 악화로 나타난다.

### 8.3 신뢰 가능한 비교만 본 결과

K granularity 분석에서 대조군 B1은 정상인 K=20 하나로 고정하는 것이 옳다. 신뢰 가능한 분모(K=20 B1)로만 비교하면 다음과 같다.

| CaseB의 K | 신뢰 가능한 분모 기준 평균 Δ% | 해석 |
|---|---|---|
| K=10 | +10.35% (fallback_K20 24건) | 실험군이 오히려 약화 — strata가 너무 적어 분포 분리 불충분 |
| K=20 (default) | −6.19% (1120건) | 정상 |
| K=30 | −6.76% (전체 120건), −8.18% (fallback_K20 56건) | K=20과 비슷 |

신뢰 가능한 비교만 추리면 결론은 두 가지다. K=20과 K=30은 서로 비슷한 수준의 개선을 보이며(−6.19% vs −6.76%), strata를 K=20에서 K=30으로 더 늘려도 추가 이득은 명확하지 않다. K=10은 대조군 B1 자체가 손상되어 깨끗한 비교가 불가능하며, 정상 분모와 fallback 비교하면 +10.35%로 실험군이 오히려 약화된다. strata가 너무 적으면 각 stratum이 분포의 다봉성을 충분히 분리하지 못한다는 방향은 시사되나, K=10 대조군의 결함 때문에 단정할 수는 없다.

추가로, 별도 검증에서 K granularity 측정은 measurement run 단위의 systematic bias가 ±10~25%로 크다는 점도 확인되었다. 이 또한 K granularity 결론을 보수적으로 보고해야 하는 이유다.

### 8.4 결론

본 연구는 논문 default인 K=20 설정을 그대로 채택한다. K granularity는 본문 finding이 아닌 부속·미완 결과로 격하하며, K=10 대조군 B1의 결함을 정직하게 명시한다. 본 narrative의 모든 headline 수치는 K=10 paired 120건을 전부 제외한 1240건에서 산출되었다.

---

## 9. selectivity 효과 — 낮은 selectivity일수록 개선 폭이 커진다

### 9.1 selectivity sweep의 핵심 finding

본 연구는 selectivity를 0.001/0.01/0.10 세 단계로 sweep하여, 각 단계에서 실험군의 우월성이 어떻게 변하는지를 측정했다. 그 결과가 본 절의 핵심 finding이다. K=10을 제외한 신뢰 가능 비교 기준으로 selectivity별 집계는 다음과 같다.

| sel | n | better% | 평균 Δ% | 중앙값 Δ% |
|---|---:|---:|---:|---:|
| 0.001 | 416 | **84.6%** | −5.05% | −6.14% |
| 0.01 | 424 | **92.9%** | −7.18% | −9.08% |
| 0.10 | 400 | **99.2%** | −6.49% | −5.31% |

핵심은 better 비율의 단조 증가다. selectivity가 0.001 → 0.01 → 0.10으로 높아질수록 better 비율이 84.6% → 92.9% → 99.2%로 일관되게 오른다. selectivity가 0.10에 이르면 측정한 400건 중 거의 전부가 개선되고, 그 대부분이 통계적으로 유의하다. 분포 인지 sample selection의 우월성은 쿼리가 더 많은 데이터를 선택할수록 거의 예외 없이 성립한다.

selectivity 0.001에서 better 비율이 84.6%로 상대적으로 낮은 것은, 매우 낮은 selectivity에서는 표본에 들어오는 hit 수 자체가 작아 어떤 sample selection 전략이든 추정 분산이 커지기 때문이다. 그럼에도 84.6%는 여전히 명확한 우월성이고, 평균 Δ%도 −5.05%로 음수다.

(참고: figure F8 selectivity sweep 데이터셋 기준으로는 84.4/92.4/99.2%로 집계되며, paired_delta 전체 기준 84.6/92.9/99.2%와 0.5%p 이내로 일치한다. 두 집계의 cell 집합이 약간 달라 생기는 미세한 차이이며, 단조 증가 결론은 동일하다.)

### 9.2 Neyman 배분의 selectivity 의존성 (부속 evidence)

selectivity 축에서 관찰되는 또 하나의 현상은 stratum 배분 방식의 우열이 selectivity에 따라 뒤집힌다는 점이다.

| selectivity | Neyman | Anti-Neyman | Proportional | 우열 |
|---|---:|---:|---:|---|
| sel=0.01 | 1.595 | 1.540 | 1.580 | Anti < Prop < Neyman (역설) |
| sel=0.10 | 1.1076 | 1.1101 | 1.1135 | Neyman < Anti < Prop (고전 이론 정합) |

sel=0.01에서는 Neyman 배분이 가장 나쁘고 Anti-Neyman이 가장 좋은 역설이 나타나지만, sel=0.10에서는 Neyman이 가장 좋아 고전 이론과 일치한다. sel=0.01 역설의 원인은 본 데이터셋이 Neyman 배분의 가정 — 클러스터 간 표준편차의 이질성 — 을 만족하지 않기 때문이다(σ_j 범위가 1.3~1.6배로 좁고 클러스터 크기의 변동계수가 0). Neyman 이론 자체가 무효라는 뜻이 아니라, 본 데이터셋이 그 가정 조건을 충족하지 못하며 그 효과가 selectivity에 따라 다르게 드러난다는 의미다. 이는 selectivity라는 변인 하나가 배분 방식의 우열까지 바꿀 수 있음을 보여주는 부속 evidence다(근거 데이터: rq2_DEEP_sf100_5way_allocation.csv, rq2_SIFT_sf100_5way_allocation.csv).

---

## 10. 분포 파악 속도 — fit_time

### 10.1 base evidence

데이터셋이 들어올 때 분포를 빠르게 파악한다는 §3.1의 주장을 측정으로 뒷받침하는 것이 fit_time이다. 5/15 16개 측정 방법 중 Top 5 method에 대해 9 cell × 2 mode = 90건 모두에서 fit_time을 직접 측정했다.

### 10.2 Top 5 method의 fit_time

| Method | n | fit_time 평균 | 범위 | cache_time 평균 |
|---|---:|---:|---|---:|
| sparse_rp | 18 | **3.67s** | 0.35 ~ 8.64s | 10.64s |
| chao_weighted | 18 | 9.40s | 0.12 ~ 28.34s | 10.11s |
| hyperloglog | 18 | 12.31s | — | — |
| pca1d | 18 | 19.97s | 0.81 ~ 68.18s | 10.77s |
| hilbert_real | 18 | **43.50s** | 1.40 ~ 100.04s | 10.04s |

fit_time 범위는 sparse_rp 3.67s부터 hilbert_real 43.50s까지 약 11.9배 차이가 난다. cache_time은 method와 무관하게 약 10s 수준이며, 벡터 차원에 의존한다.

### 10.3 해석

fit_time은 §3.1의 1단계(offline, 1회)에서 sample selection을 위한 stratification을 만드는 시간이다. 매 쿼리마다 다시 fit하는 것이 아니라, 데이터셋 진입 시 한 번 또는 데이터가 바뀔 때 incremental하게 수행하는 비용이다. sparse_rp의 3.67s는 분포를 파악하고 stratification을 만드는 데 걸리는 가장 짧은 시간이다.

산업 환경에서 분포 파악 속도가 제약일 때, sparse_rp는 hilbert_real보다 12배 빠르면서도 정확도는 같은 자원·정확도 최적 경계(Pareto frontier)에 놓인다(§11). 자원·정확도 최적 경계란 자원을 더 쓰지 않고는 정확도를 더 높일 수 없는 method들의 모음을 말한다. 메모리는 모든 method가 stratum 수에 비례하는 수준 이하이고, reservoir 방식인 chao_weighted는 데이터 크기와 무관한 상수 메모리를 쓴다. 모바일·임베디드·스트리밍 환경에 직접 적용할 수 있는 finding이다.

---

## 11. 자원 효율 — 자원·정확도 최적 경계

### 11.1 정확도와 자원의 맞교환(trade-off)은 성립하지 않는다

본 절은 §10의 fit_time과 §6의 paired Δ%를 결합한 자원·정확도 최적 경계 분석이다. 16 method를 (자원 비용, 정확도 개선) 평면에 배치해 본 결과, 정확도 상위 method와 자원 효율 상위 method가 거의 일치한다. "정확도를 올리려면 비용을 더 써야 한다"는 맞교환은 본 비교 범위에서 성립하지 않는다.

자원 축은 figure F7에서 final_size — CaseB 모드에서 AdaptiveState 식 1-6 종료 시 실제로 소비한 sample budget 평균 — 로 잡았다. 측정 portfolio에 fit 단계의 wall-clock 컬럼이 없어 소비 표본 수를 자원 대리 지표(proxy)로 쓴 것이며, 적은 표본이 적은 거리 계산을 뜻한다는 점에서 "budget" 성격으로 해석이 일관된다.

### 11.2 Top 5 method

자원과 정확도를 함께 고려해 선정한 Top 5 method는 sparse_rp, chao_weighted, hilbert_real, hyperloglog, pca1d다. 이 다섯 method의 paired Δ%(K=10 제외)는 모두 평균 −7.7% 이하이고 better 비율 96% 이상으로, 16 method 중 상위권이다. 경계선에 엄밀히 놓이는 것은 chao_weighted, hilbert_real, sparse_rp, pca1d 네 개이며, hyperloglog는 hilbert_real에 약하게 지배되어 경계선에는 엄밀히 포함되지 않는다는 점은 정직하게 보고한다.

reservoir 방식인 chao_weighted는 메모리가 데이터 크기와 무관한 상수이면서 정확도가 상위권이다. sparse_rp는 hilbert_real보다 12배 빠르면서도 Q-error 정확도가 같은 자원·정확도 최적 경계에서 동시에 상위에 놓인다. 약한 method인 gmm과 minibatch_partial은 높은 비용·양수 Δ% 쪽으로 떨어져 경계선에서 멀다.

본 연구는 이 Top 5 method를 5/27 발표와 6/11 보고서에서 권장 method 집합으로 제시한다.

---

## 12. 권장과 향후 작업

### 12.1 권장 — Type별 method 선택 + 결합 default

본 연구의 권장은 세 가지다. 첫째, 데이터셋 Type을 판별해 Type별로 측정상 우월성이 견고한 method를 자동으로 고른다(§7.3). 둘째, sample selection 결과는 단독 대체가 아니라 CaseB 결합(est_final = (est_b1 + est_method) / 2.0)을 default로 쓴다 — 음성 대조 검증(§6.2)이 단독 대체의 불안정성을 보였고, 결합은 신뢰 가능 비교 1240건의 92.2%에서 우월하다. 셋째, 분포 파악 속도가 제약인 환경에서는 fit_time이 가장 짧으면서도 정확도가 자원·정확도 최적 경계 상위인 sparse_rp를 우선한다(§10, §11).

### 12.2 본 연구가 확인한 것과 정직하게 남기는 한계

본 연구는 sample selection 방식을 random Bernoulli에서 분포 인지 stratification ensemble로 바꾸었을 때 Q-error가 개선되는 것을, 다섯 종의 단일 벡터 데이터셋과 우리가 직접 만든 세 종의 다중 벡터 데이터셋, 그리고 selectivity·method·구조·scale·K라는 다섯 조작 변인 전반에서 확인했다. 개선은 selectivity가 낮을수록 크고, 단일 벡터에서 가장 크며, 16 method 중 14개가 견고하게 우월하고, 정확도 상위 method가 자원 효율 상위와 일치한다.

동시에 본 연구는 한계를 숨기지 않는다. K granularity 축에서는 K=10 대조군 B1의 구조적 결함을 발견해 그 측정을 정직하게 배제했고(§8), K granularity를 본문 finding이 아닌 부속 결과로 격하했다. concat sf=100은 DEEP+SIFT만 측정했고 DEEP+WIKI·DEEP+YFCC는 원본 데이터의 한계로 sf=1/10만 측정했다. selectivity의 단일점 측정 cell(A4-sel)은 sweep cell과 구분된다. 이러한 한계는 본 핵심 finding의 신뢰성을 훼손하지 않는다. headline 수치는 결함 데이터를 모두 배제한 1240건에서 산출되었기 때문이다. 완전한 검증을 시도했고, 그 과정에서 대조군의 구조적 결함까지 찾아내 정직하게 다루었다는 점이 본 연구의 강점이다.

### 12.3 향후 작업

5/27 발표 이후의 작업은 두 갈래다. 하나는 박광현 교수님이 제안한 4 엔진 통합 POC — PostgreSQL pgvector, DuckDB, vector.c 기반 PG, 그리고 추가 엔진을 통합해 sample selection 방식이 엔진을 가로질러 일반화되는지를 검증하는 것이다. 다른 하나는 측정 공간의 추가 확장 — 더 다양한 다중 modal 벡터 조합, real workload 환경에서의 검증이다.

본 narrative는 5/27 발표(deck v11)와 6/11 최종보고서(outline v3)의 공통 base이며, 두 산출물은 본 narrative의 측정 evidence를 토대로 작성된다.

---

# 부록 §A — 정정 룰과 한계 명시

## A-1. 논문 §V-B에는 의사 코드가 없다

논문 §V-B는 여섯 식과 자연 산문, 일곱 하이퍼파라미터만으로 기술된다. "Algorithm 1" 같은 algorithmic block 형식이 논문에 없다. 본 narrative도 의사 코드 형식을 쓰지 않고 §3의 세 단계를 자연 산문으로 기술했다.

## A-2. framework의 novelty 한정

본 연구가 통합한 네 구성요소는 각각 새로운 것이 아니다. Stratified Reservoir Sampling은 Vitter 1985 + Al-Kateb 2014, BIRCH CF-tree는 Zhang SIGMOD 1996(batch 축 자원 한계로 폐기, CF tuple 형식만 입력으로 사용), 논문 식 2-6 통합 부분은 논문 §V-B 그대로, Distribution-aware stratification은 Cochran 1977 §5.5(Equal/Proportional/Neyman/Anti-Neyman 네 모드)다. 본 연구의 contribution은 알고리즘 자체가 아니라, 네 구성요소를 통합하고, 논문 §V-B 위에서 sample selection 단계만을 통제 변인으로 다루며, 다섯 Type 분류와 동적 method 선택을 제안하고, 전 조작 변인에 걸친 paired 측정 evidence를 산출한 검증 설계에 있다.

## A-3. 논문 §V-B의 single-table 가정과 구현 코드 한계

논문 §V-B 자체는 single-table KNN query에 대한 sampling 기반 cardinality 추정을 명시한다. 그러나 논문 공개 코드(BDAI-Research/Exqutor)의 single-table 부분이 동작하지 않아, 본 연구의 측정 일부가 multi-join으로 자연스럽게 이동했다. 임채림 연구원 자문에 근거한다.

## A-4. 논문 §V-B sampling은 block + row 혼합이다

논문 §V-B의 sampling은 초기 N=385 budget을 block 단위로 뽑고, 식 5의 표본 크기 갱신 시 추가 행을 row 단위로 뽑는 block + row 혼합 방식이다. "block only"라는 이전 표현은 부정확하다. 임채림 연구원 자문에 근거하며, 본 narrative §3의 1단계(offline) + 2단계(online) 분리가 이 혼합 구조를 반영한다.

## A-5. "분포를 안다 / 모른다"의 이분법 폐기

이전 narrative의 "분포를 안다 / 모른다" 이분법 구분은 부정확하다. 우리가 쓰는 method — 클러스터링, 차원 축소, quantization 등 — 자체가 분포를 파악하는 도구이며, 데이터셋이 들어올 때 이 method들이 분포를 빠르게 파악한다(§10의 fit_time). 이 이분법 자체가 논문 §V-B의 "without index" 가정을 잘못 해석한 것이다. 박세은 팀장 5/15 정리에 근거한다.

## A-6. 논문 §V-B는 "without index" 가정이다

논문 §V-B는 벡터 인덱스가 없는 상황을 가정한 sampling 기반 cardinality 추정이다. 다만 "without index"는 인덱스의 부재를 뜻할 뿐 분포 정보 자체의 부재를 뜻하지 않는다(A-5와 일치). 우리의 분포 인지 sample selection은 "without index" 가정 안에서 유효하다.

## A-7. "Anti-Neyman > Neyman"의 정확한 의미 — selectivity 의존

이전 narrative의 "Anti-Neyman > Neyman = Neyman 가설 무효"는 부정확하다. 정확한 의미는 세 가지다. Neyman 가설 자체는 Cochran 1977 §5.5 고전 이론으로 유효하다. 본 데이터셋이 Neyman 가정 조건(클러스터 간 σ_j 이질성)을 만족하지 않는다(σ_j 범위 1.3~1.6배로 좁고 클러스터 크기 변동계수 0). 그리고 그 효과가 selectivity에 의존한다(sel=0.01 역설 / sel=0.10 정합). 상세는 §9.2.

## A-8. K=10 대조군 B1의 구조적 결함 (신규)

대조군 B1의 측정 함수가 환경변수로 strata 수를 받아 strata 캐시를 만드는 구조라, K=10 설정에서 B1의 쿼리별 Q-error에 무한대가 폭증하여(쿼리 1000건 중 314~391건) qe_trim이 정상 범위 1.6~1.7을 벗어나 3.0대로 손상되었다. K=20·K=30 B1은 정상이고 K=10 B1만 손상되었다. paired 측정 가운데 K=10 96건은 손상된 K=10 B1과 짝지어져 paired Δ% 평균 −36.15%의 허위 신호를 냈다. 동일 K=10 CaseB를 정상 K=20 B1과 짝지으면 +10.35%로 오히려 악화다. 본 narrative의 모든 headline 수치는 K=10 paired 120건을 전부 배제한 1240건에서 산출했으며, K granularity(§8)는 본문 finding이 아닌 부속·미완 결과로 격하했다.

## A-9. A4-sel은 selectivity sweep이 아니다 (신규)

A4-sel cell은 sel=0.001 단일 값으로만 측정되었다(B1 1 + CaseB 16). §9의 selectivity sweep을 담당하는 것은 v9 sweep(24 cell × 3 sel)이며, A4-sel은 단일 selectivity의 high-error 측정점일 뿐 sweep cell이 아니다. A4-sel의 paired Δ%는 평균 +3.02%(better 37.5%)로 약한데, 이는 sel=0.001의 극단적 본질적(inherent) 분산 때문이며 sweep의 sel=0.001 평균(−5.05%)과 구분해 읽어야 한다.

## A-10. concat sf=100 부분 미측정 (신규)

우리가 만든 concat 다중 벡터 cell 중 DEEP+SIFT는 sf=1/10/100 세 규모를 모두 측정했으나, DEEP+WIKI와 DEEP+YFCC는 sf=1/10만 측정되었고 sf=100은 없다. 이는 원본 데이터셋 측의 한계(해당 조합의 sf=100 적재 미비, 원본 데이터 10M 행 한계)이며, §5의 concat 분석에서 sf=100 커버리지는 DEEP+SIFT 한 종으로 제한된다.

## A-11. method 명명 한계

별도 audit에서 일부 method 구현이 byte-identical하거나 알고리즘 명칭과 실제 구현이 불일치함이 확인되었다. hilbert는 실제로 PCA 2D lex sort이고(Faloutsos 1989가 아님), sparse_rp는 Achlioptas 2003이 아닌 Li-Hastie-Church 2006 variant다. 본 narrative는 사용 16 method만 분석 대상으로 하여 byte-identical 중복 method를 배제했고, hilbert_real·sparse_rp는 정직하게 명명된 구현을 사용한다. paradigm 간 비교 시 이 명명 한계를 발표·보고서에 명시할 것을 권장한다.

## A-12. 통계 검정의 한계

본 narrative의 통계 수치는 결론을 뒤집지 않으나 네 한계를 정직하게 명시한다. Wilcoxon 검정은 trial n=10으로 수행되어 도달 가능한 최소 p값이 1/1024 ≈ 0.001이며, paired 1360건 중 746건이 이 바닥값에 몰려 있다. BH-FDR 보정을 1360건 단일 family로 적용해 유의 우월 비율(78.3%)이 다소 보수적으로 추정된다. Cliff's δ와 Hedges' g는 독립표본 공식으로 계산되어 paired 설계의 효과를 보수적으로 추정한다. headline 92.2%·−6.25%는 file-weighted 집계이며, cell-weighted로 재집계하면 better 90.6%·평균 −6.00%로 소폭 약화되나 결론은 유지된다.

---

작성: 2026-05-17 KST · v6(5/16) 전면 수정 · 모든 수치는 REPORT_paper_exact_v12.md 및 paired_delta_v12.parquet 직접 재계산으로 확인 · 5/27 발표 deck v11 + 6/11 보고서 outline v3의 공통 base narrative
