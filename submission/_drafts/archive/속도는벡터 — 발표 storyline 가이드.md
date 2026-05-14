# 속도는벡터 — 5/27 최종 발표 storyline 가이드

> **대상**: 강재현 (발표자) + 팀원 검토용  
> **발표 일시**: 2026-05-27 (화) 19:00 · 연세대학교  
> **발표 시간**: 20 분 + Q&A 10 분 (예상)  
> **deck**: `속도는벡터 · Capstone Final 5_27 (Keynote v4).pdf` (20 slide)

---

## 0. 발표 전체 흐름

발표는 네 부분으로 구성됩니다. **배경 (3분) — 연구 질문 (5분) — 알고리즘 portfolio 와 실험 (8분) — 핵심 결과와 결론 (4분)** 입니다. 각 부분의 핵심 메시지를 명확히 전달하고 청중이 마지막 climax 슬라이드에서 "단독 대체는 무효, 증강만 유효" 라는 한 줄을 가져가게 하는 것이 목표입니다.

발표자가 주의할 점은 **슬라이드 본문이 키워드 위주이고 자세한 설명은 발표자의 narrative 로 전달** 한다는 점입니다. 본 가이드의 각 슬라이드별 narrative 한 줄을 외워 두면 흐름이 자연스럽습니다.

---

## 1. 슬라이드별 발표 흐름

### Slide 1 — Cover (10초)

> "안녕하세요, 속도는벡터 팀의 캡스톤 최종 발표를 시작하겠습니다. 본 연구는 Exqutor 논문의 Adaptive Sampling 영역에 분포 인지형 stratification 을 결합 보강하는 접근의 정량적 가치를 검증한 결과입니다."

청중 메시지: **본 발표는 Exqutor 논문 기반의 sampling 개선 연구**

### Slide 2-4 — 배경 (3분)

**Slide 2 SectionDivider** — "첫 번째 부분, 배경입니다."

**Slide 3 Exqutor 논문 한계** — paper 자체가 명시한 한계 큰 인용문 강조

> "Exqutor 논문의 §V-B Adaptive Sampling 영역은 인덱스가 없을 때 무작위 sampling 으로 카디널리티를 추정합니다. 그러나 무작위 sampling 은 데이터 분포에 의존적이라는 한계가 있고, 이는 paper 자체에서도 명시하고 있습니다."

청중 메시지: **무작위 sampling 은 분포 의존적이라 불안정. 이것을 보강할 수 있을까**

**Slide 4 우리가 잡은 주제** — 한 줄 thesis

> "본 연구는 이 sampling 영역에 분포를 인지하는 보조 추정 방식을 결합해서 정확도를 개선할 수 있는가를 묻습니다."

### Slide 5-9 — 세 단계 연구 질문 (5분)

**Slide 5 SectionDivider** — "두 번째 부분, 세 단계 연구 질문입니다."

**Slide 6 RQ1·RQ2·RQ3 한 슬라이드 정리**

> "세 단계로 풀었습니다. RQ1 은 baseline 검증 — 무작위 sampling 이 얼마나 부정확한가. RQ2 는 분포를 알 때 어떤 분배 방식이 최적인가. RQ3 는 분포를 모를 때 어떤 알고리즘이 최적인가입니다."

청중 메시지: **세 단계 단계적 검증으로 가설을 강화**

**Slide 7 RQ1 결과** — MAX gap 8.64% 강조

> "RQ1 결과입니다. paper exact 측정 4 cells 에서 가장 극단 case 인 SIFT sel=0.10 cell 의 baseline 추정 오차는 1.230, 우리 분포 인지 방식은 1.123 — 차이 8.64 퍼센트, 정확도 1.095 배 향상입니다. 4 cells 평균으로는 5.17 퍼센트 격차로, 무작위 sampling 의 한계가 정량 확인됩니다."

청중 메시지: **무작위 sampling 의 부정확성이 측정 가능한 수준으로 드러남**

**Slide 8 RQ2 결과** — Proportional 최적

> "RQ2. 분포를 알 때 어떻게 분배할지 다섯 방식을 비교했습니다. Bernoulli 1.748 → 비례 분배 1.580 — 비례가 가장 안정적입니다."

청중 메시지: **분포 정보를 활용하면 추정이 안정화됨**

**Slide 9 RQ3 출발점** — 분포를 모르면

> "그러나 실제 환경에서는 분포를 모릅니다. 따라서 분포를 추정해주는 알고리즘이 필요합니다."

청중 메시지: **다음 단계는 분포 추정 알고리즘 search**

### Slide 10-11 — 알고리즘 portfolio (2분)

**Slide 10 SectionDivider** — "세 번째 부분, 알고리즘 portfolio 입니다."

**Slide 11 8 paradigm × 56 method**

> "8 paradigm — 밀도 추정, 정보 이론, 스트리밍, 차원 축소, 공간 분할, 균등 격자, 클러스터, 양자화 — 에서 총 56 개 알고리즘을 측정했습니다. 각 paradigm 은 작동 가정이 서로 다르며, 어떤 가정이 본 시나리오에 가장 잘 맞는지를 측정으로 비교하는 접근입니다. 총 1001 개 측정 파일을 paper exact 재현으로 확보했습니다."

청중 메시지: **광범위한 paradigm 비교 search**

### Slide 12-15 — 실험 framework + paper 재현 + paradigm 결과 (4분)

**Slide 12 SectionDivider** — "네 번째 부분, 실험 framework 입니다."

**Slide 13 paper 재현 검증**

> "본 측정의 정합성입니다. paper Fig.12 영역 8 cells 의 평균 추정 오차는 1.618 — paper 보고값 1.69 대비 -4.3 퍼센트, 측정 변동 범위 내 정확 일치입니다. paper 100 퍼센트 재현이 입증된 위에 본 연구의 contribution 이 추가됩니다."

청중 메시지: **paper 100% 재현 + 본 연구 contribution layer 추가 구조**

**Slide 14 대체 vs 증강 framework**

> "두 가지 적용 방식을 비교합니다. 대체는 paper Bernoulli 를 우리 method 로 단독 교체하는 방식, 증강은 산술 평균으로 결합하는 방식입니다. AdaptiveState 와 sample budget 은 paper exact 그대로 보존하며 차이는 최종 추정값 계산만에 있습니다."

청중 메시지: **두 방식의 차이는 결합 vs 대체**

**Slide 15 Paradigm rollup 결과**

> "8 paradigm 의 증강 효과를 baseline 1.748 대비 정렬했습니다. 밀도 추정 1.748 → 1.540 으로 정확도 1.135 배, 정보 이론 1.082 배, 스트리밍 1.071 배, 차원 축소 1.064 배, 공간 분할 1.059 배 향상. 다섯 paradigm 이 paper baseline 대비 통계적으로 압도합니다. 단일 알고리즘의 우연한 효과가 아닌 paradigm 차원에서 robust 한 개선임을 시사합니다."

청중 메시지: **다섯 paradigm 일관 개선 — robust evidence**

### Slide 16-18 — 핵심 결과와 결론 (3분)

**Slide 16 왜 replace 만으로는 안 되는가**

> "여기서 본 연구의 핵심 turning point 가 나옵니다. 왜 단독 대체는 안 되고 증강만 유효한가. 세 측면에서 분석됩니다. 첫째 sample budget 제약 — N=385 를 stratum 단독에 분배하면 stratum 당 평균 19 sample 로 variance 추정이 불안정합니다. 둘째 통계적 가정 — paper Eq 1-6 의 momentum 기반 update 가 무작위 sampling 의 i.i.d. 와 asymptotic normal 가정 위에 설계되어 stratified 통계 분포와 충돌합니다. 셋째 negative control 실측 — 493 cells 중 outperform 이 0 cell. random 을 stratified 로 대체하는 것은 통계적으로 불가능함이 실험적으로 입증됩니다."

청중 메시지: **단독 대체는 budget + 가정 + 실측 세 측면 모두 무효**

**Slide 17 가장 우수 알고리즘 5선**

> "다섯 paradigm 의 대표 알고리즘은 다음과 같습니다. Parzen KDE 는 데이터 점 주변 kernel 함수로 확률 밀도를 부드럽게 추정합니다. HyperLogLog 는 hash 의 leading-zero 분포로 1.5 킬로바이트 메모리만으로 distinct count 를 근사합니다. Chao 1982 weighted reservoir 는 스트림 환경에서 분포 비례 sampling 을 보장합니다. Sparse Random Projection 은 1/√D 희소 행렬로 고차원을 저차원으로 압축하면서 거리 정보를 보존합니다. Hilbert curve 와 Z-order 는 space-filling curve 로 고차원 공간을 1차원에 매핑하면서 인접성을 유지합니다."

청중 메시지: **각 paradigm 의 대표 알고리즘 의미와 작동 원리**

**Slide 18 ★ Climax — 대체 vs 증강**

> "본 연구의 결정적 비교입니다. 대체 (CaseA) 는 493 cells 중 outperform 이 0 cell — 단 하나도 paper baseline 을 이기지 못합니다. 단독 대체는 무효입니다. 반면 증강 (CaseB) 은 492 cells 중 455 cells 에서 paper baseline 우위 — 92.5 퍼센트로 paper review-grade 통계 우위입니다. 이 negative control 이 본 연구의 핵심 결론을 명확히 합니다. 단독 대체는 무효, 증강 적용만 유효합니다."

청중 메시지: **★ 핵심 결론. 청중이 가져갈 한 줄.**

### Slide 19-20 — 한계와 마무리 (1분)

**Slide 19 Limitation**

> "본 연구가 측정하지 않은 영역을 명시합니다. multi-table 영역은 paper §V-A scope 외로 본 연구 범위 외입니다. ensemble augment 의 latency 와 memory overhead 는 본 측정에 포함되지 않아 향후 측정 영역으로 남깁니다."

청중 메시지: **honest limitation — 학술적 정직성**

**Slide 20 Closer**

> "감사합니다. 질문 환영합니다."

청중 메시지: **발표 종료 + Q&A 진입**

---

## 2. 시간 분배 정리

| 부분 | 시간 | 슬라이드 |
|---|---:|---|
| Cover | 0:10 | S1 |
| 1. 배경 | 3:00 | S2-S4 |
| 2. 연구 질문 | 5:00 | S5-S9 |
| 3. Portfolio | 2:00 | S10-S11 |
| 4. 실험 framework + paper 재현 + paradigm rollup | 4:00 | S12-S15 |
| 5. ★ 핵심 결론 (replace 분석 + 5선 + Climax) | 4:30 | S16-S18 |
| 6. 한계 + Closer | 1:20 | S19-S20 |
| **합계** | **20분** | |

Q&A 10 분은 별도. `자주 묻는 질문` 자료를 사전 숙지하면 대응이 용이합니다.

---

## 3. 발표자 (강재현) 가 주의할 포인트

첫째, **청중의 한 줄 메시지** 가 마지막 climax 슬라이드의 "단독 대체는 무효, 증강만 유효" 임을 명확히 전달합니다. 다른 슬라이드들은 이 한 줄에 도달하기 위한 supporting evidence 라는 점을 강조합니다.

둘째, **paper 100% 재현** 을 강조합니다. 본 연구가 paper 의 결과를 그대로 인정한 위에 새 contribution 을 추가했다는 점이 학술적 정직성과 신뢰성을 보장합니다.

셋째, **숫자의 의미** — 92.5%, 0/493, 1.135× 등 — 를 단순 수치로 읽지 말고 **"통계적 압도", "단독 대체는 0", "1.135 배 정확도 향상"** 같은 해석 표현으로 전달합니다.

넷째, **paradigm 별 가정** 은 청중이 익숙하지 않을 수 있으므로, 각 paradigm 의 작동 가정을 한 줄로 풀어 설명합니다. (예: "Parzen KDE 는 데이터 점 주변에 kernel 을 배치해 확률 밀도를 추정하는 방식입니다.")

다섯째, **paradox 부분 (RQ2 의 Anti < Prop < Neyman) 은 깊이 들어가지 않습니다.** 슬라이드는 "분포 알면 비례 분배가 답" 까지만 강조하고 paradox 의 정밀한 원인 분석은 Q&A 에서 다룹니다.

---

## 4. Q&A 예상 질문 (별도 자료 `자주 묻는 질문` 참조)

- Q-error / qe_trim 이 무엇인가
- Bernoulli baseline 정의
- 왜 ensemble augment 인가
- paradigm 8 개가 왜 그것들인가
- replace 가 안 되는 이유 (slide 16 에서 다루지만 더 자세히)
- multi-table 처리 방식
- ensemble 비용 측정 X 이유

---

작성: 2026-05-12 KST · 5/27 발표 D-15 시점  
관련 자료: 같은 폴더의 `한 페이지 요약` / `팀원 종합 가이드` / `자주 묻는 질문` / 키노트 v4 deck PDF
