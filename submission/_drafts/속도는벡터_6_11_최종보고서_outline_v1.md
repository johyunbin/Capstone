# 6월 11일 최종 보고서 — Outline (v2, 4차 정정)

> **팀**: 속도는벡터 (박세은·강재현·조현빈·이동욱)
> **제출일**: 2026-06-11
> **분량 목표**: 본문 약 30 page (한국어, 학술 산문)
> **작성**: 2026-05-14 (5/13 v1 → 5/14 v2 4차 정정)

---

## 들어가는 말

본 문서는 6월 11일 최종 보고서의 outline 이다. 4월 28일 제출한 중간 보고서를 기반으로 두고, 5월 한 달 동안 진행한 RQ3 측정과 추가 분석을 어떻게 보고서에 통합할지를 정리했다. 중간 보고서는 12 page 였고, 최종 보고서는 측정 결과의 양이 늘어난 만큼 약 30 page 를 목표로 한다.

본 v2 의 핵심 변화 두 가지를 먼저 짚어 둔다. 첫째, 5월 14일 새벽까지 추가 측정 (가중치 변화 sweep 16 measurement + 저비용 결합 방식 4 후보 32 measurement + 자원 효율 Pareto 분석) 이 회수되면서 본 보고서의 narrative 가 확정되었다 — **단독 대체 가능 method 의 발견이 main finding 이고, 결합 framework 의 가치는 "더 큰 개선" 이 아니라 "안정성 보강 + 자원 효율" 이라는 정직한 narrative**. 둘째, 박세은 5월 13일 12:13 카톡 피드백 (method 개수 너무 많음 + 숫자/공식 최소화) 을 반영해서 본문에서는 핵심 method 5-6 개만 자세히 다루고, 폐기 method 명 전체 list 와 통계 검정 jargon 은 부록으로 분리했다.

본 보고서의 RQ3 결과는 청자가 자연스럽게 따라올 수 있는 일곱 단계의 순차 흐름으로 구성한다 — (1) 문제 정의, (2) 분포 인지 방법 56 개의 탐색과 폐기 분류, (3) 단독 대체 가능성 분석, (4) 결합 framework 검토 (산술 평균 + 가중치 sweep + 저비용 결합 방식), (5) 자원 효율 분석 (Pareto frontier + 산업 적용 3 영역), (6) 권장 design 추출, 그리고 (7) Method 메커니즘 분석 (부록).

핵심 변화는 (1) RQ3 결과 섹션의 7 단계 순차 흐름 구성과 대폭 확장, (2) 한계를 정직하게 짚어 두는 섹션의 추가, (3) 본 연구 권장 design 과 산업 적용 영역 섹션의 신규 추가, (4) 향후 확장 방향 (Data-aware ensemble framework 5 영역 + 일반 확장 5 영역) 의 추가, (5) Method-level consistency 와 3-axis sensitivity 분석 패턴을 부록 E 로 강화, 이 다섯 가지다.

---

## 보고서 전체 구조

```
Cover · Contents (2 page)
1. 해결하고자 하는 문제 (3 page)
2. 기존 연구의 현황 및 한계점 (3 page)
3. 기존 연구와의 차별성 및 제안하는 연구의 중요성 (3 page)
4. 연구 방법 및 결과 (15 page)
  4.1 RQ1 (2 page)
  4.2 RQ2 (3 page)
  4.3 RQ3 (10 page · 7 단계 순차 흐름)
5. 본 연구 권장 design 과 산업 적용 영역 (2 page)
6. 본 연구의 한계 및 향후 확장 (3 page)
7. 결론 (1 page)
참고문헌
부록 A ~ H (필요 시)
```

---

## 1. 해결하고자 하는 문제 (3 page)

중간 보고서의 1 장을 base 로 한다. 1.1 벡터·임베딩과 분석 쿼리, 1.2 카디널리티 추정과 옵티마이저의 두 소절을 유지하되, 중간 보고서에서 짧게 다룬 부분을 조금 더 풀어서 설명한다.

핵심은 두 가지다. 첫째, 최근 데이터베이스 환경에서 이미지·텍스트를 임베딩 벡터로 바꿔 검색하는 작업과 일반 표 데이터를 SQL 로 분석하는 작업이 한 시스템 안에서 함께 일어난다 (벡터 증강 분석 쿼리, VAQ). 둘째, 이런 쿼리를 잘 처리하려면 옵티마이저가 결과 행 수, 즉 카디널리티를 정확히 추정해야 한다. 카디널리티 추정이 잘못되면 인덱스 사용 여부, 조인 알고리즘 선택, 필터 순서 같은 실행 계획 전반이 비효율적으로 결정되고, 결과적으로 수행 시간이 최대 1만 배 이상 증가할 수 있다.

이 1 장에서 최종 보고서에 새로 추가할 부분은, "단일 테이블 검색의 경우" 에서 우리 연구가 §V-B 영역에 한정된 기여라는 점을 보다 명확하게 짚어 두는 것이다. 중간 보고서 시점에는 RQ3 가 아직 탐색 단계여서 기여의 정확한 범위가 정해지지 않았는데, 5월 한 달의 측정으로 우리 기여가 "본 논문 §V-B 베르누이 단계에 계층적 표집을 단독 대체 또는 산술 평균으로 결합하는 보강" 으로 좁혀졌다.

---

## 2. 기존 연구의 현황 및 한계점 (3 page)

중간 보고서의 2 장을 base 로 한다. 2.1 고정 비율 선택도 추정, 2.2 Exqutor 의 두 가지 보완책, 2.3 Exqutor 의 한계점 세 소절을 유지한다.

최종 보고서에서 보강할 부분은 2.3 의 한계점 분석이다. 중간 보고서에서는 "샘플링이 특정 영역의 데이터에 편중될 수 있어 데이터 분포에 따라 정확도가 달라진다" 라고 한 줄로 정리했는데, 최종 보고서에서는 이 부분을 두 가지 한계로 구분해 설명한다. 첫째, 블록 단위 표본 추출의 편향 (block sampling bias) — 디스크 페이지 단위로 행이 묶여 표본에 포함되므로 행 단위 균일성이 보장되지 않는다. 둘째, 데이터의 공간적 쏠림 (spatial skew) — 클러스터 크기와 클러스터 내 분산이 불균등하면 무작위 샘플링은 특정 영역을 누락하거나 과대 표집한다.

이 두 한계가 RQ2 와 RQ3 에서 어떻게 다뤄지는지의 도입부를 자연스럽게 만든다. RQ2 가 "분포를 알면" 어떻게 두 한계를 모두 해결하는지를 보여주고, RQ3 가 "분포를 모르면" 두 한계 중 적어도 공간적 쏠림의 효과를 어떻게 근사적으로 회복할 수 있는지를 보여준다.

---

## 3. 기존 연구와의 차별성 및 제안하는 연구의 중요성 (3 page)

중간 보고서 3 장의 두 가지 차별성 (단일 테이블 집중, 한계 분리 검증) 을 유지한다. 최종 보고서에서 추가할 것은 5월 측정 결과를 바탕으로 한 세 번째 차별성이다.

세 번째 차별성은 "단독 대체 가능 method 의 발견 + 결합 framework 의 안정성 보강" 이다. 우리는 본 논문의 베르누이 추정량을 우리의 분포 인지 추정량으로 단순 대체하거나, 두 추정값을 산술 평균으로 결합하는 두 방식을 측정했다. 단독 대체 모드의 측정에서 56 method 중 약 40% 가 평균적으로는 베르누이 baseline 보다 정확하고, 통계 검정으로 cell 전반에서 안정적으로 우위를 점한 method 는 7.6% (15/197) 정도였다. 이 15 method 의 평균 개선폭 -5 ~ -12% 는 paper 자체 재현 시 발생하는 측정 변동 (-4.3%) 보다 1.2 ~ 3 배 큰 의미 있는 개선이며, 단독 best 인 minibatch_partial 의 -10.17% 개선이 본 측정 portfolio 의 best 다. 결합 모드 (산술 평균) 의 492 짝지어 비교한 측정 중 92.5% 가 베르누이 baseline 보다 정확하지만, 결합 best (-7.37%) 는 단독 best (-10.17%) 보다 약하다.

본 차별성은 단순히 "어떤 method 가 좋다" 가 아니라 "단독 대체로 의미 있는 개선이 가능하고, 결합은 안정성 보강의 보조 역할" 이라는 정직한 narrative 다. 가중치 sweep 측정으로 산술 평균이 결합 방식 중 best 임이 정량 확정되었고, 4 cheap 근사 후보 측정으로 Centroid tuple 만 결합 모드 보편 우위임이 확정되었다.

---

## 4. 연구 방법 및 결과 (15 page)

### 4.1 RQ1 — 무작위 샘플링의 부정확성 정량화 (2 page)

중간 보고서의 RQ1 결과 (단일 테이블 사각지대 + Adaptive Sampling 강제 적용 시 정확성 문제) 를 base 로 한다. 다만 5월 13일 박세은의 결정으로 RQ1 narrative 가 두 가지로 보강된다.

기존 이야기 흐름은 "기존 적응적 샘플링 (Adaptive Sampling) 이 단일 테이블에서 작동하지 않고, 강제 적용 시 32 개 결과 같은 정확성 문제가 발생한다" 였다. 보강 이야기 흐름은 "PostgreSQL 의 두 표본 추출 방식 (TABLESAMPLE SYSTEM vs BERNOULLI) 자체가 skew 데이터셋에서 얼마나 부정확해지는가" 를 추가로 정량화하는 것이다.

5 selectivity × 2 dataset × 5 seed × 100 query 짝지어 비교한 측정 결과, SIFT 선택도 0.05 에서 SYSTEM 이 BERN 보다 최대 17.32% 더 부정확하고, 5 selectivity 전 구간에서 SIFT 가 DEEP 보다 격차가 더 크다 (cross-dataset 격차 +1.40 ~ +5.61%p). 본 논문이 사용한 베르누이가 이미 두 옵션 중 더 나은 쪽이라는 정량적 근거가 되며, 이후 RQ2 ~ RQ3 의 "그 베르누이조차도 어떻게 더 정확하게 만들 수 있는가" 의 출발점이 된다.

### 4.2 RQ2 — 분포 인지 계층적 표집 (3 page)

중간 보고서의 RQ2 (블록 단위 → 행 단위 베르누이 변경 + KM20 계층적 표본) 를 그대로 가져온다. 표 1 (selectivity 별 SYSTEM vs BERN Q-error 중앙값) 과 표 2 (세 데이터셋 KM20 추가 개선율) 도 유지한다. 그림 1 ~ 그림 6 (paired scatter, 분포 비교, Two-Level 분해, 클러스터 크기 분포) 역시 유지한다.

최종 보고서에서 추가할 부분은 5-way 비교 측정 결과다. 중간 보고서 시점에는 KM20 (분포 인지 계층적 표집) 와 BERN (블록 → 행 단위 변경) 의 두 가지 비교만 있었는데, 5월에 다섯 가지 할당 방식 (베르누이 / 동등 / 비례 / Neyman / 반(反) Neyman) 의 짝지어 비교가 추가되었다. 핵심 결과는 베르누이에서 비례 할당으로 바꾸면 평균 -9.53% 개선이라는 것과, Neyman 할당이 비례 할당보다 약간 부정확한 역설 (paradox, 1.595 vs 1.580) 이 발견되었다는 것이다.

이 역설은 측정 오류가 아니라 PartSupp PK 의 KM20 클러스터 균등 분포 (변동 계수 = 0) 와 클러스터 내 분산 범위 1.3 ~ 1.6 배의 좁은 분포에서 σ-가중 Neyman 이 proportional 과 통계적으로 동등이 되는 자연스러운 결과다. 이 역설의 해석이 RQ3 로의 자연 전환을 만든다 — "분포 알면 proportional 이 답이지만, 분산 range 가 큰 cluster imbalance 영역에서는 다른 답이 필요할 수 있다."

### 4.3 RQ3 — 분포를 모를 때의 계층적 표집 회복 (10 page · 7 단계 순차 흐름)

중간 보고서 시점에는 RQ3 가 약 1 page 분량의 "탐색 단계" 정도였다. 최종 보고서에서는 5월 한 달의 측정 결과를 바탕으로 약 10 page 로 확장한다. 본 4.3 절은 청자가 자연스럽게 따라올 수 있는 7 단계 순차 흐름으로 구성된다.

**4.3.1 단계 1 — 문제 정의 (0.5 page)**

RQ3 의 출발점은 "실제 운영 환경에서는 분포를 모를 때가 많다" 는 점이다. RQ2 의 결과가 "분포를 알면 비례 할당이 답" 이라는 것이었지만, multi-table 영역으로 확장하거나 클러스터 정보가 stale 한 환경에서는 분포 정보가 불완전하다. 본 RQ3 는 분포 정보를 근사하는 다양한 후보 method 56 개를 8 패러다임으로 모아 측정한다 — 클러스터링, 공간 분할, 스트리밍, 차원 축소, 준 무작위, 양자화, 정보 이론, 밀도 추정.

**4.3.2 단계 2 — 분포 인지 방법 56 의 탐색과 폐기 분류 (2 page · 정직성 축)**

8 paradigm × 56 method × 9 cells × 2 modes 매트릭스를 측정 대상으로 잡았다. cell 은 A1 (DEEP, SIFT, SSN single-table) × A2 (Fig7 multi-table DEEP+PartSupp, Fig9 multi-table cross DEEP+WIKI) × A4 (선택도 sweep) × A5 (scale sweep) 의 9 가지다. 두 가지 모드 중 CaseA 는 본 논문의 베르누이 추정량을 우리 method 의 추정값으로 단독 대체하는 모드이고, CaseB 는 산술 평균 모드 — 두 추정값의 산술 평균 — 다. 동적 sample size 조정과 sample budget 은 두 모드 모두 paper exact 로 유지한다.

측정을 진행하면서 일부 method 는 그대로 둘 수 없는 문제가 발견되어 폐기했다. 폐기 사유를 3 범주로 정리한다 (구체 method 명 list 는 부록 H 참조).

**(1) 자원 한계** — 측정 서버의 메모리 한계로 실행이 불가능하거나, 한 cell 측정에 4 시간 이상의 timeout 이 필요해서 전체 portfolio 마감을 맞추기 어려웠던 method. 가장 인상적인 birch 는 클러스터를 트리 구조로 저장하는 부분이 50 ~ 200GB 메모리를 차지해서 실행 자체가 불가능했고, agglomerative 는 256 차원 데이터셋에서 메모리 부족으로 실패했다. kde_parzen 은 한 cell 측정에 4 시간 이상의 timeout 이 필요했다.

**(2) 알고리즘 구현 결함** — 5월 10일에 8-agent 정독 검토로 발견된 reference 위반이나 알고리즘 잘못 표기. 가장 인상적인 사례는 vinecopula 의 코드 구현이 rank 변환 + PCA 1 차원 정렬의 별칭으로 되어 있어서 Bedford-Cooke 1986 의 진짜 vine copula 가 아니라는 점, 그리고 neuram 이 코드 한 줄씩 검토한 결과 PCA1D 와 100% 동일하다는 점이다. kdtree 의 알고리즘 구현 코드를 보면 leaf 인덱스가 단순한 modular hash (`idx % n_strata`) 로 처리되어 있어서 무작위 표집과 거의 동등 — paper 가 의도한 kdtree 의 공간 분할 효과가 아니다. 그 외 약 20 종도 같은 방식으로 reference 위반이나 알고리즘 잘못 표기가 발견되어 폐기했다.

**(3) 정합성 위반** — 큰 데이터셋에서 추정값이 +145,483%, +213,065% 같은 외곽 값으로 나타나서 paper 가 정의한 sample budget 안에서 estimator 의 정합성을 보장하지 못하는 method.

폐기를 거치고 남은 측정 가능한 method 는 약 43 개다. 이들이 본 연구의 비교 실험군이며, 8 패러다임 분류 위에서 측정 결과를 정리한다. 본 연구의 비교 실험군은 9 cells × 2 modes 가 모두 완료된 method 한정이다.

**4.3.3 단계 3 — 단독 대체 가능성 분석 (★ main finding, 1.5 page)**

남은 43 method 의 추정값을 본 논문의 베르누이 대신 그대로 갈아 끼우는 단독 대체 모드 (CaseA) 의 측정 결과를 정직하게 풀이한다.

- **평균 우위 약 40%**: 56 방법 중 약 40% 가 평균적으로는 베르누이 기준선보다 정확.
- **통계 일관 우위 7.6%**: 같은 method 라도 데이터셋과 cell 마다 효과의 편차가 컸다. 통계 검정으로 cell 전반에서 안정적으로 베르누이를 우위로 누른 method 는 7.6%.
- **★ 15 method 의 평균 개선폭 -5 ~ -12%**: 단독 대체로 통계 일관 우위인 15 method 의 평균 개선폭은 -5 ~ -12% 다. paper 자체 재현 시 발생하는 측정 변동 (-4.3%) 보다 1.2 ~ 3 배 큰 의미 있는 개선이다.
- **단독 best**: 본 측정 portfolio 의 단독 best 는 minibatch_partial 의 -10.17% 개선이다.

★ **단독 대체 가능 핵심 5-6 method** — 본 보고서에서 자세히 다루는 method 는 sparse_rp (차원 축소 paradigm, 학습 cheap + anchor 수준 정확도), chao_weighted (스트리밍 paradigm, 메모리 매우 적음), minibatch_partial (클러스터링 paradigm, 단독 best), hilbert_real (공간 분할 paradigm, 진짜 Hilbert curve), hyperloglog (정보 이론 paradigm), 그리고 ★ reservoir (스트리밍 paradigm, 메모리 O(1) — 본 측정 portfolio 최저). 각 method 의 알고리즘 메커니즘은 부록 E 에서 자세히 다룬다.

다만 단독 대체는 cell 별 spread 가 커서 산업 적용 보장에는 안정성 부족 — 이 안정성 부족이 결합 framework 검토의 motivation 이다.

**4.3.4 단계 4 — 결합 framework 검토 (2 page · 결합 방식 축의 후반)**

단독 대체의 안정성 부족을 보완하기 위해 검토한 다음 방향이 두 추정값을 결합하는 framework 다. 처음에는 가장 단순한 결합 방식 — 산술 평균 — 으로 측정을 진행했다.

**(1) 산술 평균 결합의 측정 결과**: 결합 모드 (산술 평균) 의 492 짝지어 비교한 측정 중 92.5% 가 베르누이 baseline 보다 더 정확하다. 통계 검정에서도 분명한 차이. 12 anchor method 는 cell 전반에서 -9 ~ -10% 의 일관된 개선과 안정적인 spread 를 보인다.

**왜 산술 평균이 효과적인가**: 베르누이 무작위 샘플링은 편향이 0 이지만 분산이 크다. 클러스터 기반 계층적 표집 추정량은 분포 가정이 맞을 때는 분산이 작지만, 가정이 빗나가면 편향이 생길 수 있다. 두 추정값을 산술 평균하면 한 쪽이 실패할 때 다른 쪽이 보완해 주는 안정적인 구조가 된다.

**(2) 가중치 sweep 결과 (5/14 새벽 회수)**: 베르누이 가중치 0.3 / 0.4 / 0.5 / 0.6 / 0.7 다섯 값으로 가중 평균을 측정한 결과, 4 anchor method 중 3 개가 가중치 0.5 (산술 평균) 에서 best, 양쪽 극단 (0.3 / 0.7) 에서 효과 감소. **산술 평균이 결합 방식 중 best 이며 가중치 변화로 더 큰 개선 어렵다**.

**(3) 저비용 결합 방식 4 후보 결과 (5/14 새벽 회수)**: 산술 평균 외 다른 결합 방식 후보 — Centroid tuple / Hash bucketing / PCA preprocessing / Iterative refinement — 의 32 measurement 회수 결과, **Centroid tuple 만 결합 모드 4 method 모두에서 보편 우위** (평균 -0.84%p 추가 정확도). 학습 비용 추가 0 + 더 좋은 정확도의 "더 싸고 더 좋은" 패턴. 나머지 3 후보 (Hash / PCA / Iterative) 는 method × mode 별로 spread 크거나 일부 영역에서 marginal/harmful.

**(4) 결합 framework 의 진짜 위치 — 정직 disclosure**: 가중치 sweep + 4 cheap 근사 후보 측정을 종합한 결과 본 연구의 결합 framework 의 정확한 위치가 드러난다 — **단독 best (-10.17% minibatch_partial) > 결합 best (-7.37% sparse_rp Centroid tuple)**. **결합으로 단독 best 능가 불가** — 이것이 본 연구의 정직한 disclosure 다. **결합의 진짜 가치 = method 선택 robustness + cell spread 줄임** ("더 큰 개선" 이 아님).

8 paradigm 의 평균 효과를 보면 다섯 개가 평균적으로 의미 있는 우위를 보였다. 평균 개선폭 순으로 밀도 추정 (-11.93%, n=1), 정보 이론 (-7.60%, n=9), 스트리밍 (-6.63%), 차원 축소 (-6.03%), 공간 분할 (-5.57%) 이다. paradigm 평균이 일부 method 의 극단값에 끌려가는 경우가 있어서 본 보고서는 paradigm 평균을 보조 정보로 두고 method 단위 분석을 부록 E 에서 상세히 다룬다.

**4.3.5 단계 5 — 자원 효율 분석 (★ 산업 적용 핵심, 2 page)**

성능만으로 산업 적용을 결정할 수 없다. 학습 시간, 메모리 사용, 차원 한계가 method 마다 다르기 때문이다.

**(1) Pareto frontier Top 5**: 학습 시간과 정확도 개선폭의 두 axis 로 Pareto frontier 를 도출하면 다음 5 method 가 frontier 상에 위치한다.

| Method | 학습 시간 | 정확도 개선 | 메모리 |
|---|---:|---:|---|
| sparse_rp | 0.1초 | -9.43% | O(D·k) |
| chao_weighted | 0.5초 | -9.60% | O(K) (최저) |
| neuram | 0.5초 | -9.97% (최고) | O(K·D) |
| pca1d | 0.5초 | -9.63% | O(N) |
| hilbert / hilbert_real | 0.1-0.5초 | -9.27 ~ -9.41% | O(N) |

이 5 method 는 12 anchor 일관성 명단과도 일치한다.

**(2) 산업 적용 3 영역 추천 — ★ reservoir O(1) finding**:

- **영역 A (일반 OLAP server, Best of Both Worlds)**: sparse_rp 또는 chao_weighted. 학습 cheap + 정확도 anchor 수준 + 메모리 작음.
- **영역 B (정확도 우선)**: neuram. 본 측정 portfolio 정확도 최고.
- **★ 영역 C (모바일/embedded/streaming, Resource-First)**: **reservoir — 메모리 O(1) + 학습 0.1초 + 정확도 anchor 수준**. **이 발견이 본 연구의 가장 강력한 산업 적용 finding** 이다.

**(3) cheap 근사 — Centroid tuple 의 "더 싸고 더 좋은" 패턴**: multi-table cell 에서 계층적 표집을 어떻게 할지에 대한 두 가지 후보가 있다. 비싼 multi-join 재학습 (두 벡터를 864 차원으로 합친 후 KM20 재학습) 과 cheap 근사 (Centroid tuple, 두 single-table 의 클러스터 결과를 tuple 로 합쳐서 그대로 사용, 학습 비용 0 추가).

8 measurement 결과로, 결합 모드에서 4 method 모두 (sparse_rp, chao_weighted, hilbert_real, hyperloglog) cheap 근사가 비싼 재학습보다 평균 -0.84%p 정확도가 더 좋다. "더 싸고 더 좋은" best of both worlds 결과로, multi-table 영역 확장의 cheap 근사 가능성을 보여 준다.

**(4) 단독 대체 vs 결합의 자원 비교**: 단독 대체는 우리 method 만 사용하므로 학습 비용 = 우리 method 학습 비용 그대로다. 결합은 베르누이 (paper 본문) 와 우리 method 두 estimator 의 합인데, paper sample budget 을 두 estimator 가 공유하므로 query 시 추가 시간은 거의 없다. 학습 단계에서도 우리 method 만 학습하면 되므로 단독 대체와 동일. 즉 결합의 자원 추가 부담은 무시 가능.

**(5) multi-join 재학습 — quality-sensitive vs quality-robust 분기**: 8 measurement 의 결과는 method 별로 분기된다. sparse_rp 와 chao_weighted (quality 의존적인 두 method) 는 CaseA 단독 대체 모드에서 864 차원 concat 재학습이 single-table carry-over 보다 추가 개선을 보인다. Hilbert curve 와 HyperLogLog (quality 안정적인 두 method) 는 거의 차이가 없다. 결합 모드에서는 4 method 모두 거의 차이가 없다 — 우리 핵심 기여인 산술 평균의 학습 방식 변경에 대한 안정성 입증.

**4.3.6 단계 6 — 권장 design 추출 (1 page)**

성능 (단독 대체 -5 ~ -12% + 결합 92.5% 안정성) 과 자원 (cheap 근사로 0 학습 비용 추가) 사이의 균형 영역에서 본 연구가 권장하는 design 을 추출한다. 자세한 내용은 5 장에서 다룬다. 이 4.3.6 절은 측정 결과로부터 도출한 권장 design 의 골격을 짧게 정리한다.

**4.3.7 단계 7 — 통계 검정 정합성과 paper 재현 정합성 (1 page · 정직성 축)**

전체 RQ3 결과의 통계 검정 정합성을 정리한다. 짝지어 비교 검정 + 효과크기 분석 + 다중 비교 FDR 보정을 모두 적용했다. 본 연구의 측정 portfolio 가 충분한 sample size 를 갖추어 통계적 안정성이 확보된다.

paper 재현 정합성은 paper §V-B Fig 12 영역의 절사 평균 Q-error 가 본 측정 vs paper 보고값에서 -4.3% 차이, 즉 측정 변동 범위 안에서 일치한다. paper 의 동적 sample size 조정 식과 모든 hyperparameter 가 코드 한 줄씩 일치한다. 결정론적 재현성 검증과 JSON 산출물 전수 검사에서 결손 없음이 확인된다.

본 paper 재현 정합성은 우리 결과가 "paper 재현으로서 충분한 baseline" 임을 보장한다. 이후 우리가 추가한 계층적 표집 산술 평균의 효과는 이 baseline 위에서 짝지어 비교로 측정된다. method 의 내부 sampling 메커니즘 axis 분석은 부록 E 에서 상세히 다룬다.

---

## 5. 본 연구 권장 design 과 산업 적용 영역 (2 page)

본 5 장은 본 보고서에서 신규로 추가되는 섹션이다. 5월 측정 결과를 종합하여 본 연구가 권장하는 design 과 산업 적용 영역을 정리한다.

### 5.1 권장 design — 세 원칙의 조합 (★ v2 narrative 갱신)

본 연구가 권장하는 design 은 다음 세 가지 원칙의 조합이다 (v2 의 단독 대체 우선 + 결합 보조 narrative 반영).

1. **단독 대체 적용 우선** — 단독 대체 가능 5-6 method (sparse_rp / chao_weighted / minibatch_partial / hilbert_real / hyperloglog / reservoir) 중 산업 환경에 맞는 method 선택 후 paper 베르누이를 우리 method 의 추정값으로 갈아 끼우는 가장 단순한 방식. 평균 -5 ~ -12% 의 의미 있는 정확도 개선 가능.

2. **결합 framework 보조 사용** — 단독 대체의 cell 별 spread 가 산업 적용에 부담될 때, 산술 평균 결합으로 안정성 보강. 92.5% 짝지어 비교 우위로 cell spread 줄어들고 method 선택 robustness 확보. multi-table 영역에서는 Centroid tuple 저비용 결합 방식이 학습 비용 추가 0 으로 추가 정확도 개선 제공.

3. **method-aware 선택적 적용** — 12 anchor method 중에서도 cell 별 K-민감도와 quality-민감도 패턴이 다르므로, sparse_rp 와 chao_weighted (quality-sensitive group) 에는 정밀 처리 (K=20 + multi-join 재학습), Hilbert curve 와 HyperLogLog (quality-robust group) 에는 단순 처리 (cheap 근사 + carry-over) 를 선택적으로 적용. 이 분류 axis 의 본질적 근거는 부록 E (Method 메커니즘 분석) 에서 다룬다.

### 5.2 산업 적용 영역 — 3 영역 추천 (★ 자원 효율 axis 통합)

본 자원 효율 axis 분석으로 도출된 산업 적용 3 영역의 method 추천:

**(1) 영역 A — Best of Both Worlds (일반 OLAP 데이터베이스 server)**: sparse_rp 또는 chao_weighted 단독 대체 + 산술 평균 결합 보조. 학습 0.1-0.5 초 cheap + 정확도 anchor 수준 + 메모리 작음. PostgreSQL pgvector 의 default sampling 메커니즘에 우리 method 의 stratified estimator 를 추가하는 통합 영역.

**(2) 영역 B — Quality-First (정확도 절대 우선)**: neuram 단독 대체 + 산술 평균 결합. 본 측정 portfolio 정확도 최고. 학술 연구 영역이나 정확도 절대 우선 application 에 적합.

**(3) ★ 영역 C — Resource-First (모바일/embedded/streaming)**: **reservoir 단독 대체**. **메모리 O(1)** + 학습 0.1초 + 정확도 anchor 수준. 자원 제약이 매우 큰 환경 (메모리 < 100MB, 학습 시간 < 100ms) 에 가장 적합. 본 연구의 가장 강력한 산업 적용 finding.

### 5.3 통합 영역 — Exqutor §V-B 모듈 통합

Exqutor 의 Adaptive Sampling 모듈에 우리 세 원칙 조합 (단독 대체 우선 + 결합 보조 + cheap 근사 + method-aware) 을 통합하면 paper 본문 성과 (1만 배 속도 개선) 위에 추가적인 정확도 layer 를 얹을 수 있다. 단일 테이블에서는 단독 대체 또는 결합, multi-table cell 에서는 Centroid tuple cheap 근사 + 결합. method 는 cell 특성에 따라 dynamic 선택.

본 두 산업 적용 영역은 실제 production workload 에서의 정확도 vs 자원 절충 측정을 통한 추가 검증이 필요하며, 이는 향후 연구 (6.3 절) 에서 다룬다.

---

## 6. 본 연구의 한계 및 향후 확장 (3 page)

### 6.1 측정 미커버 9 카테고리 정직 분류 (1.5 page)

본 연구는 측정 portfolio 9 cells × 56 method × 2 modes 매트릭스에서 비교 실험군에 해당하는 method 는 9 cells × 2 modes 모두 완료. 미커버 영역을 9 카테고리로 정직하게 분류한다.

(1) **알고리즘 정독 검토로 폐기한 23 method** — 5월 10일 8-agent 정독 검토에서 reference 위반이나 알고리즘 잘못 표기가 발견된 method 들. 예를 들어 vinecopula 는 rank + PCA 1 차원 정렬의 별칭으로 구현되어 있어서 Bedford-Cooke 1986 의 진짜 vine copula 가 아니다. neuram 은 코드 한 줄씩 검토한 결과 PCA1D 와 100% 동일하다. kdtree 는 leaf 인덱스가 단순한 modular hash (`idx % n_strata`) 로 처리되어 무작위 표집과 거의 동등하다. ams_count_sketch 는 lsh 와 코드가 한 줄씩 동일하다. 이런 알고리즘 본질적 결함은 학술 정직성 위반이므로 보고서에서 제외한다.

(2) **자원 한계로 실행이 어려운 7 method** — birch CFNode tree 가 SF=100 cell 에서 50 ~ 200GB RSS 폭증, agglomerative 가 256d 차원에서 OOM, hdbscan 이 데이터셋 일부에서 KMeans 로 fallback, kde_parzen 이 한 cell 측정 4 시간 timeout, dirichlet/kernelpca/neuocard 가 자원이나 구현 안정성 문제. A1-SSN cell 의 80GB NPY fetch 가 method 당 37 ~ 88 분 소요로 timeout 인 점도 같은 카테고리.

(3) **정합성 위반 9 method** — halton, sobol, lhs, hammersley, dense_rp, random_projection, dbscan, ccsketch, lsh, ams_count_sketch. 큰 데이터셋에서 추정값이 외곽 값으로 나타나서 paper 의 sample budget 안에서 estimator 정합성을 보장하지 못한다.

(4) **paper §V-A 범위 외** — A2-Fig8 multi-vector AND predicate, A3-TPCDS 는 paper §V-A multi-table 영역으로 우리 §V-B 샘플링 영역과 별개.

(5) **Wrapper 설계 결함** — Q1+Q4 batch 에서 timeout 부재로 hung process 발생, 자체 검증으로 fix.

(6) **사용자 결정 제외** — hdbscan 은 sklearn 1.7.2 에서 KMeans fallback 과 등가로 측정 제외.

(7) **Byte-identical 중복 7쌍** — 동일 결과를 내는 method 짝.

(8) **method 단위 정직 disclosure 두 건** — (a) hilbert method 가 PCA 2D 정렬로 구현되어 있는 점 (Faloutsos 1989 의 진짜 Hilbert curve 가 아님). 별칭으로 `pca2d_lex` 라고 명명하고, 진짜 Hilbert curve (Wikipedia 표준의 hilbert_real) 를 별도 9 cells × 2 modes 로 따로 측정. (b) sparse_rp 의 Li-Hastie-Church 2006 reference 정정.

(9) **RQ2 Neyman 역설** — Neyman 할당이 비례 할당보다 약간 부정확한 역설 (1.595 vs 1.580) 은 측정 오류가 아니라 PartSupp PK 의 좁은 분포 특성이 만든 자연스러운 결과.

### 6.2 통계 검정의 한계 (0.5 page)

짝지어 비교 검정의 p-value 가 매우 작은 것은 측정 file 수가 많기 때문에 가능한 수치다. 같은 짝지어 비교를 더 작은 sample size 에서 보면 cell 별 p-value 가 분산되고 약 절반의 cell 에서만 통계적 유의성이 확보된다. 따라서 우리 결과의 "92.5% paired better" 는 전체 portfolio 차원에서는 분명한 근거지만, 개별 cell 차원에서는 method 별 안정성이 다르다는 점을 명시한다.

또한 단독 대체의 통계 일관 우위 7.6% (15/197) 도 같은 맥락에서 해석되어야 한다. FDR 보정으로 다중 비교를 통제한 결과이므로 cell 전반의 안정적 우위 기준은 보수적이다. 평균 우위 (약 40%) 와 통계 일관 우위 (7.6%) 의 격차는 method 별 cell 편차의 산물이며, 이 편차 자체가 산술 평균 결합 framework 의 motivation 이 된다.

### 6.3 향후 확장 — Data-aware ensemble framework + 일반 확장 (1 page)

본 연구는 산술 평균이라는 가장 단순한 결합 방식부터 측정을 시작하여 결합 framework 자체의 효과를 baseline 수준에서 입증하였다. 실제 산업 적용을 위해서는 데이터셋의 분포 특성, 차원, 질의 선택도에 따라 결합 방식이 동적으로 결정되는 data-aware ensemble framework 가 필요하다. 본 연구의 산술 평균 결과는 그 framework 의 출발점이며, 향후 연구는 두 그룹으로 나뉜다.

#### 6.3.1 Data-aware ensemble framework — 핵심 5 영역

(A1) **Distribution-aware ensemble** — skew / dense 데이터셋에 따라 결합 가중치 동적 결정.

(A2) **Dimensionality-aware ensemble** — 차원 별 결합 방식 선택. 본 연구의 측정 차원 (96, 128, 256) 외 더 다양한 차원에서 결합 효과의 일관성과 차원별 best 결합 방식의 차이를 측정.

(A3) **Estimator-confidence-aware** — 각 estimator 의 분산 추정 기반 분산 최소화 가중치. 본 연구의 산술 평균이 보편적 best 가 아닌 special case 일 가능성이 있으며, paper estimator 와 method estimator 의 분산 비율에 따른 dynamic 가중치 결정.

(A4) **Query-aware ensemble** — 선택도 별 결합 방식 변경.

(A5) **Meta-learning adaptive ensemble** — 측정 환경 특성을 입력으로 ML 모델로 결합 가중치 학습. 본 연구의 측정 데이터를 training set 으로 활용 가능.

#### 6.3.2 일반 확장 5 영역

(B1) **다른 데이터셋 일반화** — YFCC, GLOVE 등 다른 임베딩 특성의 데이터셋에서 동일 패턴이 재현되는지 확인.

(B2) **이론적 분산 분해** — Cochran 1977 §11.10 composite estimator 의 이론적 분산 분해를 우리 산술 평균에 적용. 산술 평균이 어떤 조건에서 가중치 평균보다 robust 한지 이론적 근거 정립.

(B3) **논문 동적 framework 와 완전 정합** — Q-error 신호 source 의 명시적 정의와 우리 산술 평균 estimator 와의 연동 검증.

(B4) **실제 시스템 적용** — pgvector 또는 Exqutor 의 prototype 통합. 실제 production workload (TPC-H, TPC-DS) 에서의 정확도 vs 자원 절충 측정.

(B5) **다른 결합 방식 추가 비교** — 본 연구의 가중치 sweep + 4 cheap 근사 후보 측정으로 결합 framework 의 위치는 확정되었으나, 더 다양한 결합 방식 (기하 평균, 분산 기반 등) 의 추가 비교 측정.

#### 6.3.3 우선순위 명시

가까운 시일 (5월 ~ 6월) 의 우선순위는 (B1) YFCC 다른 데이터셋 검증과 (A3) Estimator-confidence-aware 두 가지로 둔다. (A5) meta-learning adaptive 는 본 연구의 측정 portfolio 를 training set 으로 활용 가능한 영역으로 6/11 보고서 이후의 다음 분기 영역으로 명시한다. (B2) 이론 분해와 (B4) 실제 시스템 통합은 보고서 이후의 장기 영역.

---

## 7. 결론 (1 page)

본 연구는 Exqutor 논문 §V-B 적응적 샘플링 영역에서 두 가지 방향을 측정했다. 첫째, **단독 대체 방향** — 본 논문의 베르누이 추정량을 우리의 분포 인지 추정량으로 갈아 끼우는 방식. 15 method 가 통계적으로 일관 우위를 보였고 평균 개선폭 -5 ~ -12% 로 paper 자체 재현 변동의 1.2 ~ 3 배 큰 의미 있는 개선이며, 단독 best 는 minibatch_partial 의 -10.17% 다. 둘째, **결합 방향** — 두 추정값을 산술 평균으로 결합하는 방식. 짝지어 비교한 측정 92.5% 가 베르누이 baseline 보다 정확하지만 결합 best (-7.37%) 는 단독 best (-10.17%) 보다 약하다. **결합으로 단독 best 능가 불가** 가 본 연구의 정직한 disclosure 이며, 결합의 진짜 가치는 "더 큰 개선" 이 아닌 **"안정성 보강 + cell spread 줄임"** 이다.

본 연구는 결과를 7 단계의 순차 narrative 로 정리한다. 단계 2 에서 자원 한계 / 알고리즘 정독 결함 / 정합성 위반의 3 범주 폐기 분류로 본 연구의 정직성을 확보하고, 단계 3 에서 단독 대체 가능 method 15 의 발견을 main finding 으로 제시하고, 단계 4 에서 결합 framework 의 안정성 보강 가치를 정리하고, 단계 5 에서 자원 효율 axis 분석으로 산업 적용 3 영역을 추출하고, 단계 6 에서 세 원칙 (단독 대체 우선 + 결합 보조 + method-aware) 의 권장 design 을 추출한다. paper §V-B Fig 12 영역의 절사 평균 Q-error 가 본 측정 vs paper 보고값으로 -4.3% 차이로 재현되어 paper 재현 정합성도 확보했다.

본 연구의 가장 강력한 산업 적용 finding 은 자원 효율 axis 분석에서 도출된 **영역 C (Resource-First)** 영역의 **reservoir method** — **메모리 O(1)** + 학습 0.1초 + 정확도 anchor 수준 (-9.25%) — 의 결합이다. 모바일/embedded/streaming 환경의 자원 제약이 매우 큰 application 에 가장 적합한 권장 method 다.

부수 발견으로, 12 anchor method 가 다양한 환경에서 -9 ~ -10% × 안정적인 spread 의 일관된 개선을 보이며, K granularity 와 multi-join 두 측정 영역에서는 method 분류 패턴이 일치 (sparse_rp + chao_weighted 동시 sensitive, hilbert_real + hyperloglog 동시 robust) 하지만 cheap 근사 친화도는 다른 분류 (Friendly: hyperloglog + chao_weighted) 를 보였다. 본 연구는 팀원 강재현이 5월 13일 카톡으로 제기한 후속 가설 두 가지를 정량 검증한 결과이며, 2 axis 일치 + 1 axis 다른 분류 패턴이 method 의 내부 메커니즘이 paradigm 분류보다 본질적임을 시사하는 evidence 다. 자세한 분석은 부록 E 에 정리한다.

본 연구가 권장하는 design 은 단독 대체 우선 + 결합 보조 + cheap 근사 + method-aware 적용의 세 원칙 조합이며, 산업 적용 영역으로 PostgreSQL pgvector 통합과 Exqutor §V-B 모듈 통합 두 가지를 제시한다. 다만 본 연구의 산술 평균은 가장 단순한 baseline 결합 방식이며, 실제 산업 적용을 위해서는 data-aware ensemble framework 가 필요하다. 향후 연구는 Group A (Data-aware ensemble framework 5 영역) 와 Group B (일반 확장 5 영역) 로 정리한다.

---

## 참고문헌

중간 보고서의 5 건 (Exqutor, pgvector, VBASE, DuckDB, Lloyd k-means) 에 더해 다음을 추가한다. Parzen 1962 (KDE), Flajolet-Fusy-Gandouet-Meunier 2007 (HyperLogLog), Chao 1982 (weighted reservoir), Li-Hastie-Church 2006 (Sparse Random Projection), Morton 1966 (Z-order curve), Faloutsos 1989 (Hilbert curve indexing), Skilling 2004 (Hilbert curve state machine algorithm), Wikipedia (Hilbert curve xy2d 표준 reference implementation), Sculley 2010 (Mini-batch K-means), Vitter 1985 (simple reservoir), Grafström 2012 (LPM, local pivotal method), Jagadish 2005 (iDistance), Gao-Lin 2024 VLDB (RaBitQ quantization), Bao et al. 2025 VLDB (HNSW 분포 정보 활용), Cochran 1977 §11.10 (composite estimator), 그리고 통계 분석 reference (Cliff 1993 effect size, Hedges 1981 g, Benjamini-Hochberg 1995 FDR).

---

## 부록

부록은 본문 분량을 맞추는 데 따라 조정한다.

### 부록 A — 측정 portfolio 의 9 cells × 56 method 매트릭스 cell 별 결과

cell 별 paired Δ% 표와 통계 검정 결과.

### 부록 B — K granularity 민감도 3-way 표 (K=10, K=20, K=30)

12 anchor method × 3 K 값의 평균 Δ% 와 paired Wilcoxon p-value.

### 부록 C — multi-join 재계층화 8 measurement 원자료

4 anchor (sparse_rp, chao_weighted, hilbert_real, hyperloglog) × 2 mode (CaseA, CaseB) 의 학습 비용과 평균 Δ%.

### 부록 D — 가중치 sweep + Cheap 근사 4 후보 결과 (5/14 회수)

(1) **가중치 sweep 16 measurement**: 베르누이 가중치 0.3 / 0.4 / 0.5 / 0.6 / 0.7 × 4 anchor method. 산술 평균 (0.5) 이 결합 방식 중 best 임이 정량 확정. (2) **Cheap 근사 4 후보 32 measurement**: Centroid tuple / Hash bucketing / PCA preprocessing / Iterative refinement × 4 anchor × 2 mode. Centroid tuple 만 결합 모드 보편 우위.

### 부록 E — Method 메커니즘 분석 (도메인 전문가 자문 영역)

본 부록은 본 연구의 핵심 주장 중에서도 학술적 정밀도가 가장 필요한 부분으로, 박광현 교수님 / 임채림 박사님 / 박성원 멘토 자문이 도움이 되는 영역이다. 본문에서는 한 줄로 짚었지만 본 부록에서 풀어 둔다.

**E.1 paradigm 평균의 한계**: 8 paradigm 평균을 보면 paradigm 안의 일부 method 가 극단값 (wavelet_hist +68%, lp_bound +16%) 으로 평균을 끌어 올리거나 끌어 내릴 수 있다.

**E.2 12 anchor method 의 일관성**: 본 연구가 제안하는 12 anchor 는 9 cells 전반에서 -9 ~ -10% 의 일관된 개선과 안정적인 spread 를 보인다.

**E.3 3-axis sensitivity 분석 (2 axis 일치 + 1 axis 다른 분류)**

본 연구는 팀원 강재현이 5월 13일 카톡으로 제기한 후속 가설 두 가지 — multi-table 재계층화의 정확도 영향과 저비용 근사 가능성 — 를 정량 검증하였다.

(1) **K granularity 민감도**: K 를 10, 20, 30 으로 바꿔 보았을 때 sparse_rp 는 K=20 sweet spot 의 U 모양. 반면 Hilbert curve, HyperLogLog, Chao 의 세 method 는 K 값에 거의 영향 없음.

(2) **multi-join 재학습**: 8 measurement 결과로 sparse_rp 와 chao_weighted 는 CaseA 모드에서 추가 개선, Hilbert curve 와 HyperLogLog 는 거의 차이 없음. 결합 모드에서는 4 method 모두 차이 없음.

(3) **Centroid tuple cheap 근사**: 8 measurement 결과로 결합 모드에서 4 method 모두 비싼 재학습보다 평균 -0.84%p 추가 정확도.

**E.4 세 축 분석이 시사하는 본질적 분류 — 2 axis 일치 + 1 axis 다른 패턴**

3-axis 분류 매트릭스로 정리하면 다음과 같다.

| Method | K granularity | Multi-jn | Cheap 근사 친화도 |
|---|---|---|---|
| sparse_rp | K-sensitive (U-shape) | sensitive | Indifferent |
| chao_weighted | K=20 sweet | sensitive | **Friendly** |
| hilbert_real | K-robust | robust | Hostile (CaseA harmful) |
| hyperloglog | K-robust | robust | **Friendly** |

K granularity 변화와 multi-table 재계층화 두 측정에서 method 별 민감도 패턴이 일치 (sparse_rp + chao_weighted sensitive vs hilbert_real + hyperloglog robust) 함을 확인하였다. 그러나 저비용 근사 친화도는 다른 분류 패턴 (Friendly: hyperloglog + chao_weighted) 을 보였다. paradigm 분류보다 method 의 클러스터 quality 의존도와 cheap 근사 결합 친화도 두 axis 가 더 본질적인 method 분류 기준이 될 수 있다.

**E.5 핵심 6 method 의 알고리즘 메커니즘 + 이론적 근거 + 실측 결과 (narrative v1 §11 산문 base)**

본문 §4.3.3 의 핵심 5-6 method 의 메커니즘과 이론적 근거를 method 단위로 정리한다.

**minibatch_partial (P1 클러스터링 갈래, 단독 대체 best)** — 데이터를 청크 단위로 흘려보내면서 K=20 클러스터 중심을 점진적으로 학습 (partial_fit). 전체 데이터를 메모리에 올리지 않고 stream 처럼 처리. Sculley (WWW 2010) 의 Web-scale K-means 변형 + scikit-learn 의 MiniBatchKMeans 의 partial_fit API 직접 활용. 단독 대체 모드 9 측정 환경 평균 −10.17% (본 portfolio 단독 best). 학습 시간 0.5 초, 메모리 사용량 작음 (청크 × 차원 D), 측정 환경별 변동성 std 3.33.

**sparse_rp (P4 차원 축소 갈래, 학습 시간 가장 짧음)** — 데이터 차원 D 를 sparse random matrix (Achlioptas density 1/3, 즉 +1 / 0 / −1 의 sparse entries) 로 곱해 낮은 차원 k 로 사영. 그 후 K=20 클러스터로 stratum 분할. Achlioptas (JCSS 2003) 의 sparse Bernoulli projection + Li-Hastie-Church (KDD 2006) 의 매우 sparse 변형. Johnson-Lindenstrauss lemma 의 distance preservation 보장 위에서 sparse 화로 계산 비용을 크게 낮춤. 결합 모드 9 측정 환경 평균 −9.43%, 학습 시간 0.1 초 (본 portfolio 최단), 메모리 O(D × k) 매우 작음, std 3.30.

**chao_weighted (P3 스트리밍 갈래, Pareto Top 정확도)** — 가중 reservoir 표집. 청크 단위로 들어오는 데이터에서 weight 기반 sampling 으로 분포 정보를 streaming 으로 유지. Chao M-T (Biometrika 1982) 의 weighted reservoir sampling 으로, 각 sample 의 probability of inclusion 이 weight 에 비례하도록 보장한다. 결합 모드 9 측정 환경 평균 −9.60% (Pareto frontier 정확도 Top 1), 학습 시간 0.5 초, 메모리 O(K) 매우 작음, std 6.36.

**hilbert_real (P2 공간 분할 갈래, 진짜 Hilbert curve 구현)** — 데이터 차원 D 를 그대로 유지한 채 Hilbert space-filling curve indexer 로 1 차원 좌표 매핑. 그 후 매핑된 1 차원 좌표를 K=20 stratum 으로 분할. Faloutsos (SIGMOD 1989) 의 진짜 D 차원 Hilbert space-filling curve. 본 연구의 이전 hilbert method 는 코드 정독 검토 결과 PCA 2 차원 정렬의 별칭으로 발견되어 (★3 정정), 진짜 Hilbert curve 구현인 hilbert_real 을 별도 method 로 측정. 결합 모드 9 측정 환경 평균 −9.27%, 학습 시간 0.5 초, 메모리 O(N), std 3.12.

**hyperloglog (P9 정보 이론 갈래, 가장 안정)** — hash 기반 분포 카디널리티 추정량. K=20 stratum 별로 trailing zero 의 max 를 추적해 cardinality 를 streaming 으로 추정. Flajolet et al (DMTCS 2007) 의 HyperLogLog 로, 분포의 unique element 수를 매우 적은 메모리로 정확히 추정하는 정보 이론 기반 알고리즘이다. 결합 모드 9 측정 환경 평균 −8.65%, 학습 시간 0.5 초, 메모리 O(K log K), std 2.73 (본 portfolio Best / Excellent 19 method 중 가장 안정).

**reservoir (P3 스트리밍 갈래, 메모리 O(1) — 산업 적용 핵심)** — 가장 단순한 reservoir sampling. 청크 단위 데이터에서 K 개를 균등 확률로 sampling. Vitter (TOMS 1985) 의 reservoir sampling 으로, 데이터 크기 N 을 미리 모르더라도 K 개의 균등 random sample 을 한 번의 pass 로 얻는 알고리즘이다. 결합 모드 9 측정 환경 평균 −9.25%, 학습 시간 0.1 초, 메모리 사용량 O(1) (sample size K 만 보존, 데이터 크기 N 과 무관), std 3.00. 본 §4.3.5 의 산업 적용 reservoir O(1) finding 의 핵심 method — 모바일 / 임베디드 / 스트리밍처럼 메모리가 제약인 환경에 그대로 적용 가능하다.

**E.6 17 사용 method 전체 list (paradigm × CaseB Δ% × 자원 등급 × 이론적 근거)**

39 폐기 후 남은 17 사용 method 의 paradigm 분포 + 결합 모드 평균 + 자원 효율 등급 + 이론적 근거 reference. 자세한 자원 정량 (학습 시간 + 메모리 + SF=100 feasibility) 은 자원 효율 분석 file (`_internal/analysis/resource_efficiency_pareto_20260513.md`) 참조.

| paradigm | method | CaseB Δ% | 자원 등급 | 이론적 근거 |
|---|---|---:|---|---|
| P1 클러스터링 | minibatch_partial | −6.98% | ⭐ Excellent | Sculley 2010 partial fit |
| P1 클러스터링 | minibatch | −9.28% | ⭐ Excellent | Sculley 2010 |
| P1 클러스터링 | gmm | +2.45% | Good | Dempster 1977 EM (marginal) |
| P2 공간 분할 | hilbert_real | −9.27% | ⭐⭐ Best | Faloutsos 1989 진짜 |
| P2 공간 분할 | zorder_morton | −9.26% | ⭐ Excellent | Morton 1966 bit-interleaving |
| P2 공간 분할 | skilling_hilbert | −9.01% | ⭐ Excellent | Skilling 2004 변형 |
| P2 공간 분할 | lpm2 | −9.45% | ⭐⭐ Best | Grafström 2012 local pivot |
| P3 스트리밍 | chao_weighted | −9.60% | ⭐⭐ Best | Chao 1982 weighted reservoir |
| P3 스트리밍 | reservoir | −9.25% | ⭐⭐ Best | Vitter 1985, **메모리 O(1)** |
| P3 스트리밍 | thompson_sampling | −8.98% | ⭐ Excellent | Thompson 1933 Beta posterior |
| P3 스트리밍 | cum_sqrtf | −8.45% | Good | Cochran 1977 sqrt(F) |
| P4 차원 축소 | sparse_rp | −9.43% | ⭐⭐ Best | Li-Hastie-Church 2006 |
| P4 차원 축소 | neuram | −9.97% | ⭐⭐ Best | autoencoder (PCA1D 등가 audit) |
| P4 차원 축소 | pca1d | −9.63% | ⭐ Excellent | Pearson 1901 PCA |
| P4 차원 축소 | rsvd | −8.49% | ⭐ Excellent | Halko-Martinsson 2011 |
| P6 양자화 | pq | −9.25% | ⭐ Excellent | Jégou 2011 product quantization |
| P9 정보 이론 | hyperloglog | −8.65% | ⭐⭐ Best | Flajolet 2007 HyperLogLog |

CaseB Δ% 는 결합 모드 9 측정 환경 평균 (음수가 클수록 정확도 개선). 학습 시간 모두 0.1 ~ 1 초 범위. 자원 효율 등급 정의 — ⭐⭐ Best (fit < 1s + 메모리 O(N) 이하 + SF=100 OK + Δ% < −9%) / ⭐ Excellent (fit < 2s + Δ% < −8%) / Good (fit < 2s + Δ% −5 ~ −8%). P5 준 무작위 / P10 밀도 추정 paradigm 은 모두 폐기되어 사용 method 없음.

### 부록 F — 알고리즘 정독 검토로 폐기한 23 method 결정 근거 정리

5월 10일 8-agent 정독 검토 결과의 method 별 발견 사항의 코드 line 수준 정리.

### 부록 G — 자원 효율 axis 분석 — Pareto frontier + 산업 적용 3 영역 상세

학습 시간과 정확도 개선폭의 산점도 + Pareto frontier 상 5 method + 산업 적용 3 영역 (A / B / C) 의 method 추천 근거 + reservoir O(1) memory finding 의 상세 분석.

### 부록 H — 폐기 method 전체 list (박세은 5/13 12:13 피드백 반영)

본문에 핵심 method 만 짚고 폐기 method 명 전체 list 는 이 부록으로 분리.

**자원 한계 폐기 7 종**: birch, agglomerative, hdbscan, kde_parzen, dirichlet, kernelpca, neuocard.

**알고리즘 구현 결함 폐기 23 종**: 5월 10일 8-agent code audit 발견. 주요 사례 — kdtree (`idx % n_strata` 와 등가), vinecopula (rank+PCA1D 별칭), neuram (PCA1D 100% 동일), ams_count_sketch (lsh 와 한 줄씩 동일) 등. 자세한 method 별 발견 사항은 부록 F 참조.

**정합성 위반 폐기 9 종**: halton, sobol, lhs, hammersley, dense_rp, random_projection, dbscan, ccsketch, lsh, ams_count_sketch.

---

## 일정 — 5월 14일 ~ 6월 11일 작업 흐름

본 outline 을 기준으로 다음 일정을 잡는다.

| 기간 | 작업 내용 |
|---|---|
| 5월 14일 ~ 17일 | 박광현 미팅 (5/15) 결과 반영, 본 outline v3 update |
| 5월 18일 ~ 24일 | 4 장 본문 작성 (RQ1·RQ2·RQ3 측정 결과 정리) |
| 5월 25일 ~ 5월 27일 | 5월 27일 최종 발표 마무리 + 발표 |
| 5월 28일 | 임채림 박사 SAP 미팅 (보고서 방향 확인) |
| 5월 29일 ~ 6월 4일 | 1 ~ 3 장 본문 작성 (도입, 기존 연구, 차별성) |
| 6월 5일 ~ 6월 9일 | 5 ~ 7 장 작성 (권장 design, 한계와 향후 확장, 결론) + 그림·표 정리 + 부록 정리 |
| 6월 10일 | 전체 검토 + PDF 변환 |
| 6월 11일 | 제출 |

---

작성: 2026-05-14 KST · v2 4차 정정 (5/14 새벽 측정 회수 반영 + 박세은 피드백 반영) · 5월 15일 박광현 미팅 후 v3 update 예정
