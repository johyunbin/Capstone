# 프레이밍 초안 — "Two-Level Decomposition of Stratified Sampling Benefit"

**작성일**: 2026-04-15 14:20 KST (RANDOM20 low-sel 실험 대기 중)
**목적**: RANDOM20 control 결과를 반영하면서 교수님 프레이밍을 유지하는 narrative 구조

---

## 핵심 발견의 재정리

**RANDOM20 control 결과 (s=0.500)**:
- KM20 strat vs BERN: +1.64% CI [1.25, 2.02]
- RANDOM20 strat vs BERN: +2.20% CI [1.45, 2.95]
- KM20 strat ≈ RANDOM20 strat (절대 Q-error 1.0339 vs 1.0340)

**시사점**: 개선의 원인을 두 수준으로 분해할 수 있다.

---

## Two-Level Decomposition

### Level 1 — Proportional Allocation Effect (메커니즘 수준)

> 어떤 partition이든, stratified sampling이 BERNOULLI보다 나은 이유

BERNOULLI: 각 행이 독립적으로 p 확률로 선택 → 표본 크기 자체가 확률 변수 (Binomial)
Stratified: 각 stratum에서 ceil(n × N_k/N) 행 선택 → 표본 크기 확정

이 "표본 크기 확정" 효과만으로 Var(ŷ_strat) ≤ Var(ŷ_SRS) 가 항상 성립. 이것은 survey sampling 이론의 고전적 결과이며, partition의 품질과 무관.

**실험적 증거**: RANDOM20 strat > BERN (+2.20%, p < 0.001)

### Level 2 — Spatial Awareness Effect (공간 인식 수준)

> 공간 구조를 반영한 partition이 무작위 partition보다 추가 이득을 제공하는가?

KM20은 데이터의 공간 밀도를 반영. 이론적으로, stratum 간 평균 차이(μ_k - μ)가 클수록 proportional allocation의 추가 이득이 있다. 이 추가 이득은:

- **query 결과의 cluster 집중도(HHI)가 높을 때** 발현 (저selectivity 영역)
- **query 결과가 고르게 분포할 때** 소멸 (고selectivity 영역)

**s=0.500에서**: HHI ≈ 0.067 ≈ 1/K → 거의 균일 → Level 2 효과 없음 → KM20 ≈ RANDOM20
**s=0.050에서**: HHI ↑ (예상) → Level 2 효과 발현 가능 → KM20 > RANDOM20? ← 진행 중

---

## 교수님 프레이밍과의 연결

### 교수님 원래 질문
> "데이터가 쏠려있을 때 → uniform sampling이 나빠지고 → 개선된 sampling으로 해결"

### 수정된 연결

1. **"데이터가 쏠려있다"** → ✅ (KM20 cluster ratio 3.1×, Gini 0.1275)

2. **"uniform sampling이 나빠진다"** → ✅ 재해석:
   - BERNOULLI는 확률적 행 선택 → 표본 크기가 확률 변수 → 추정 분산 증가
   - 이 문제는 쏠림과 무관하게 존재하나, **쏠린 데이터에서 더 심해질 수 있음** (저selectivity query에서 true matches가 소수 cluster에 집중 → 무작위 표본이 해당 영역을 놓칠 확률 증가)

3. **"개선된 sampling으로 해결"** → ✅ 두 수준:
   - **Level 1**: 구조적 sampling (proportional allocation) 자체가 BERNOULLI의 확률적 변동을 줄임
   - **Level 2**: 공간 인식 partition (KM20)이 추가 이점을 제공 (조건부: query 결과가 집중된 영역에서)

### 가장 강력한 프레이밍 (두 시나리오 공통)

> "Exqutor의 BERNOULLI sampling은 확률적 변동에 취약하며, 이는 데이터의 공간 밀도가 비균일하고 query가 밀집 영역을 타겟할 때 더 심해진다. Stratified sampling은 두 가지 메커니즘으로 이를 개선한다: (1) proportional allocation에 의한 표본 크기 안정화 (보편적 효과), (2) 공간 구조를 반영한 partition에 의한 밀도 편향 교정 (selectivity-dependent 효과). 우리의 RANDOM20 control 실험은 이 두 메커니즘을 최초로 분해하여, 각각의 기여를 정량화한다."

---

## 시나리오별 narrative

### 시나리오 A: s=0.050에서 KM20 > RANDOM20

> "Low selectivity에서 cluster 집중도가 높아지면, 공간 인식 partition이 추가 개선을 제공함을 확인. 즉, 교수님의 '쏠림 → 성능 저하 → 공간 인식 개선'은 query 결과가 집중되는 영역에서 직접 관찰된다."

이 경우의 기여:
- **메커니즘 분해**: proportional allocation vs spatial awareness 분리
- **조건 식별**: spatial awareness가 효과적인 조건 (HHI > threshold) 정량화
- **설계 함의**: 모든 selectivity에서 proportional allocation을 기본으로 적용하되, 저selectivity에서 공간 인식 partition이 추가 이점

### 시나리오 B: s=0.050에서도 KM20 ≈ RANDOM20

> "공간 인식 partition의 추가 이점은 본 실험 범위 내에서 관찰되지 않았으나, 이는 proportional allocation 자체의 강력한 효과를 확인하는 결과이다."

이 경우의 기여:
- **Negative finding의 학술적 가치**: "공간 인식이 불필요할 수 있다"는 실용적 함의 (partition 비용 절약)
- **프레이밍 수정**: "쏠림 → 확률적 변동 악화 → 구조적 sampling 개선" (공간 인식 불요)
- **설계 함의**: 단순한 proportional allocation (임의 partition)만으로 충분

---

## 중간발표 핵심 메시지 (양 시나리오 공통)

1. Exqutor의 uniform BERNOULLI sampling의 한계를 실증 (Phase 4~6)
2. **RANDOM20 control로 개선 메커니즘을 분해하여 정량화** — 이 자체가 기여
3. Phase 6 Step 4 +1.64% CI [1.25, 2.02] 는 유효한 개선 (5-seed, Bonferroni 생존)
4. 공간 인식 vs proportional allocation 분리는 **최종발표까지의 핵심 연구 질문**으로 격상

---

## TODO: 실험 결과 도착 후

- [ ] 시나리오 A/B 확정
- [ ] 연구 재설계안 v2 작성
- [ ] 중간보고서/슬라이드 반영
