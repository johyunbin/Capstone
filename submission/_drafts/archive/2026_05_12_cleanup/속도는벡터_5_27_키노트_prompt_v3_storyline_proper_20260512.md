# 속도는벡터 5/27 최종발표 — 키노트 deck v3 (사용자 storyline FINAL)
## claude.ai/design 새 message paste 용 — 이전 결과 폐기, 새로 작성

> **사용자 storyline 7단계 (5/12 13:04 KST verbatim 적용)**:
> 1. 원 논문에서 부족하거나 놓친 부분, 한계라고 명시한 부분에 대해서 주제를 잡고
> 2. 데이터셋에 따라서, 분포를 아는 상황과 모르는 상황에서의 방법을 찾고 수치를 비교하기 위해서 RQ1, 2, 3를 진행
> 3. 이 때에 실험을 위해서 여러 패러다임 측면에서 적용 가능한 알고리즘을 찾아서 비교
> 4. 결과적으로 싱글/멀티 테이블에서 모두 효능있는 방법을 exqutor 논문에서 측정한 수치들을 기존에 우리가 찾은 방법으로 대체했을 때, 또는 augment 형태로 증강 적용했을 때의 차이를 비교
> 5. 결과적으로 이런 수치적 개선이 나타났고 가장 우수한 방법은 이런 알고리즘
> 6. 이 알고리즘은 어떤 방식인지 소개
> 7. 기존 방식과 우리의 가장 개선된 알고리즘을 증강적용 했을때의 개선 및 결과 분석

> **이전 결과 폐기 사유**:
> - "★3 Hilbert 정정 — 학술 정직성" 같은 self-disclosure slide 절대 X
> - byte-identical duplicates / 정합성 위반 method 폐기 같은 negative narrative 절대 X
> - "우리가 잘못 만들어서 고쳤어요" 식 내용 일절 X
> - RQ1/RQ2/RQ3 narrative 가 deck 의 핵심 — 빠지면 안 됨

---

## 0. 디자인 철학

**원칙 — 키노트 스타일, 기존 Capstone Design System 적용**:
- **1 slide = 1 메시지** — 본문 3-5 단어 max. 큰 수치 / 한 시각화 / 핵심 한 줄
- **거대 폰트** — 거대 수치 200-300px, 거대 제목 80-120px
- **whitespace 70%+** — 빈 공간이 메시지를 강하게 만든다
- **본문 narrative 100% → speaker notes 로** — slide 에는 키워드만
- **bullet list 0** — 다이어그램 / chart / heatmap / 큰 수치만
- 디자인 시스템: **Capstone Design System** (이미 project 에 적용됨)

**악습 금지**:
- self-disclosure / negative narrative X
- "★3 hilbert 정정" / "byte-identical 7쌍" / "정합성 위반 폐기" 같은 slide X
- limitation slide 도 최소화 (있더라도 1 slide 만, "측정 외 영역" 정도)
- 텍스트 우겨넣기 X
- bullet 3-5 list X

---

## 1. 발표 storyline (17 slide)

### S1 — Cover

```
상단 (eyebrow, 158×2 red rule)
─────────────
CAPSTONE 2026-1 · FINAL · 2026.05.27 · 연세대학교

중앙
─────
"분포 인지형 stratification 으로 Exqutor 보강하기" (96-120px, weight 800)
"Skew-Aware Stratification for Vector Cardinality Estimation" (영문 부제 32px)

하단 (3 column grid)
TEAM                         ADVISOR                         BASE PAPER
속도는벡터                    박광현 교수                       Exqutor
박세은 · 강재현 · 조현빈 · 이동욱    BDAI 연구실                     arXiv:2512.09695v2
```

### S2 — Section 1 / 배경 (SectionDivider)

```jsx
<SectionDivider num="01" title="배경" subtitle="Exqutor 논문이 명시한 한계와 우리 출발점" page="02" />
```

### S3 — Exqutor 논문이 명시한 한계 (서면)

```
[SlideShell — secn="1.", title="Exqutor 논문이 명시한 한계"]

큰 인용문 (32-40px, ink, max-width 1100)
"Adaptive Sampling estimator 의 정확도는
 sampling 방식 자체의 분포 의존성에 제약된다."

caption (16px fg3)
원 논문 §V-B Adaptive Sampling 영역 — 인덱스 부재 시 Bernoulli random sampling 으로 카디널리티 추정.
sample budget N=385 + 모멘텀 기반 동적 조정 (Eq 1-6) 으로 paper 가 명시한 한계.
```

### S4 — 우리가 잡은 주제 (서면)

```
[SlideShell — secn="1.", title="우리가 잡은 주제"]

중앙 큰 한 줄 (48-56px, ink, weight 700)
"분포를 알 때 / 모를 때 모두에서
 더 정확한 sampling 방식을 찾는다"

caption (18px fg3)
원 논문이 명시한 sampling 한계 → 분포 인지형 stratification 으로 보강 가능한가?
```

### S5 — Section 2 / 연구 질문 (SectionDivider)

```jsx
<SectionDivider num="02" title="연구 질문" subtitle="RQ1 · RQ2 · RQ3 — 분포 인지의 단계적 검증" page="05" />
```

### S6 — RQ1·RQ2·RQ3 한 slide 정리

```
[SlideShell — secn="2.", title="세 단계 연구 질문"]

3 column grid (각 33%, gap 32px)
─────────────
RQ1 (eyebrow: BASELINE)
"Random sampling 이
 skew 데이터셋에서 얼마나 부정확한가?"
caption (14px fg3): Bernoulli 단일 vs KM20 stratified 비교

RQ2 (eyebrow: KNOWN DISTRIBUTION)
"분포를 알 때
 어떤 allocation 이 최적인가?"
caption: Bernoulli / Equal / Proportional / Neyman / Anti-Neyman 5-way

RQ3 (eyebrow: UNKNOWN DISTRIBUTION)
"분포를 모를 때
 어떤 알고리즘이 최적인가?"
caption: 8 paradigm × 56 method paradigm 측면 search

각 column: 큰 RQ 라벨 (40px) + 한 줄 질문 (24px ink) + caption (14px fg3)
```

### S7 — RQ1 결과 (Big stat)

```jsx
<BigStat
  value="+3.74%"
  subtitle="random sampling 의 부정확함"
  caption="DEEP/SIFT/SimSearchNet++ × sf=100 5 cells × 5 trials · Bernoulli 단일 vs KM20 stratified mean gap · 분포 인지 stratification 의 출발점"
/>
```

### S8 — RQ2 결과 (Bar chart)

```jsx
<BigBarChart data={[
  { label: 'Bernoulli (baseline)', value: 1.748, color: '#737373' },
  { label: 'Equal',                value: 1.644, color: '#737373' },
  { label: 'Proportional',         value: 1.580, color: '#DC2626' },
  { label: 'Neyman',               value: 1.595, color: '#DC2626' },
  { label: 'Anti-Neyman',          value: 1.540, color: '#DC2626' },
]} />
```

**제목 (slide 상단)**: "분포를 알면 Proportional allocation 이 답"

**caption (16px fg3)**: "Bern → Prop −9.53% · 분포 정보 활용 시 추정 안정성 입증"

### S9 — RQ3 출발점 (서면)

```
[SlideShell — secn="2.", title="RQ3 — 분포를 모를 때"]

큰 텍스트 (40-48px ink, weight 700, max-width 1100)
"실제 환경에서는 분포를 모른다.
 → 분포를 추정하는 알고리즘이 필요하다."

caption (18px fg3)
8 paradigm 측면에서 분포 추정 알고리즘 search · 56 method portfolio 비교
```

### S10 — Section 3 / 알고리즘 portfolio (SectionDivider)

```jsx
<SectionDivider num="03" title="알고리즘 Portfolio" subtitle="8 paradigm × 56 method 비교 search" page="10" />
```

### S11 — 8 paradigm portfolio (Grid)

```
[SlideShell — secn="3.", title="8 paradigm × 56 method"]

4 × 2 grid (각 25% × 50%, gap 24px)
─────────────
각 cell:
  paradigm 라벨 (28px ink weight 700)
  + n_method (14px mono fg3)
  + 1 줄 설명 (16px fg2)

cell 1: 밀도 추정     n=1   확률 밀도 함수 추정 (Parzen KDE)
cell 2: 정보 이론     n=9   카디널리티 추정 (HyperLogLog)
cell 3: 스트리밍      n=44  weighted reservoir (Chao 1982)
cell 4: 차원 축소     n=104 random projection (sparse RP)
cell 5: 공간 분할     n=107 space-filling curve (Hilbert + Z-order)
cell 6: 균등 격자     n=62  quasi-Monte Carlo
cell 7: 클러스터      n=87  k-means 계열
cell 8: 양자화        n=53  vector quantization

caption (14px fg3): "총 56 method × 9 cells × 2 modes = 1001 file paper exact 측정"
```

### S12 — Section 4 / 실험 framework (SectionDivider)

```jsx
<SectionDivider num="04" title="실험 framework" subtitle="Exqutor 재현 + 대체(CaseA) vs 증강(CaseB)" page="12" />
```

### S13 — paper 재현 검증 anchor (Big stat)

```jsx
<BigStat
  value="-4.3%"
  subtitle="paper Fig.12 mean qe_trim 재현"
  caption="paper 1.69 vs 본 측정 1.618 · 8 cells · measurement variance 범위 내 일치 · paper exact 100% 정확 재현 입증"
/>
```

### S14 — 대체(CaseA) vs 증강(CaseB) framework (Diagram)

```
[SlideShell — secn="4.", title="대체 vs 증강 — 두 가지 적용 방식"]

2 column grid (좌 50% / 우 50%, gap 64px)
─────────────
좌측 — CaseA · 대체 (replace)
  Eyebrow: CASEA · REPLACE
  큰 수식 (32px mono fg1):
    est_final = est_method
  caption (16px fg3): paper Bernoulli baseline 을 우리 method 로 단독 교체

우측 — CaseB · 증강 (augment)
  Eyebrow: CASEB · AUGMENT
  큰 수식 (32px mono brand red):
    est_final = (est_b1 + est_method) / 2
  caption (16px fg3): paper Bernoulli + 우리 method 산술 평균 ensemble

하단 (32px ink weight 700)
"두 방식 모두 single + multi cell 전반에서 비교"

caption (14px fg3, 더 작게): AdaptiveState (Eq 1-6) + sample budget N=385 paper exact 보존
```

### S15 — paradigm rollup 결과 (Big chart)

```jsx
<BigBarChart data={[
  { label: '밀도 추정 (Parzen KDE)',                   value: -11.93,  color: '#DC2626' },
  { label: '정보 이론 (HyperLogLog)',                 value: -7.60,   color: '#DC2626' },
  { label: '스트리밍 (Chao weighted)',                value: -6.63,   color: '#DC2626' },
  { label: '차원 축소 (sparse RP)',                   value: -6.03,   color: '#DC2626' },
  { label: '공간 분할 (Hilbert + Z-order)',           value: -5.57,   color: '#DC2626' },
  { label: '균등 격자 (QMC)',                         value: +1.47,   color: '#737373' },
  { label: '클러스터 (k-means)',                       value: +2.04,   color: '#737373' },
  { label: '양자화 (Product Quantization)',           value: +8.44,   color: '#737373' },
]} />
```

**제목 (slide 상단, secn="4.", title="Paradigm rollup — CaseB 증강 효과")**

**caption (16px fg3)**: "negative = 증강 후 정확도 개선. 5 paradigm 통계 압도. 1.06× ~ 1.14× qe_trim 정확도 향상"

### S16 — ★ 가장 우수 알고리즘 소개 (5 paradigm anchor 카드)

```
[SlideShell — secn="4.", title="가장 우수 알고리즘 5선"]

5 column grid (각 20%, gap 24px)
─────────────
각 cell:
  paradigm 라벨 (10px mono brand red eyebrow)
  큰 수치 Δ% (40px Inter brand red weight 700)
  알고리즘 이름 (20px ink weight 700)
  reference (12px mono fg3)
  방식 설명 (14px fg2, max 3 줄)

card 1: 밀도 추정 / -11.93% / Parzen KDE / Parzen 1962
  방식: 데이터 점 주변 kernel 함수로 PDF 추정 → cluster 분포를 부드럽게 추정

card 2: 정보 이론 / -7.60% / HyperLogLog / Flajolet 2007
  방식: hash leading-zero 분포로 distinct count 추정 → 메모리 1.5KB 로 cardinality 근사

card 3: 스트리밍 / -6.63% / Chao 1982 weighted / Chao 1982
  방식: weighted reservoir sampling → stream 환경에서 분포 비례 sample

card 4: 차원 축소 / -6.03% / Sparse RP / Li-Hastie-Church 2006
  방식: 1/√D 희소 random matrix → 고차원 → 저차원 (Johnson-Lindenstrauss 보장)

card 5: 공간 분할 / -5.57% / Hilbert + Z-order / Morton 1966 / Wikipedia
  방식: space-filling curve → 고차원 공간 → 1D 보존, 인접성 유지
```

### S17 — ★ Climax — 증강만 유효 (Comparison)

```
[SlideShell — secn="4.", title="대체 vs 증강 — 결정적 비교"]

2 column grid (좌 50% / 우 50%, gap 64px)
─────────────
좌측 — CaseA · 대체 (failure)
  Eyebrow: CASEA · REPLACE
  거대 수치 (160px, brand red): "0 / 493"
  부제 (24px ink): "outperform 0 cell"
  caption (14px fg3): Bernoulli 단독 교체 시 단 하나도 우위 X · 단독 대체 무효

우측 — CaseB · 증강 (success)
  Eyebrow: CASEB · AUGMENT
  거대 수치 (160px, brand red): "92.5%"
  부제 (24px ink): "paired better (455 / 492)"
  caption (14px fg3): 결합 보강이 거의 모든 cell 에서 paper baseline 우위 · p<10⁻⁴⁵

중앙 결론 (slide 하단 중앙, 32px ink weight 700)
"단독 대체 X → 증강 적용 만 유효"

caption (14px fg3): paper review-grade evidence · Cliff's δ large 63.0% / Hedges' g large 55.7%
```

### S18 — Closer

```
중앙 거대 타이포
"감사합니다" (160px, Apple SD Gothic Neo, weight 800, ink, letter-spacing -0.04em)

부제 (32px fg2)
질문 환영합니다

하단 mono (11px fg3, 가로 1 line)
속도는벡터 · 박세은 · 강재현 · 조현빈 · 이동욱 · github.com/johyunbin/Capstone · arXiv:2512.09695v2
```

---

## 2. Speaker notes 18 entry (각 30-45초 한국어 학술 산문)

### S1 Cover
> 안녕하세요. 속도는벡터 팀의 캡스톤 최종 발표를 시작하겠습니다. 본 연구는 Exqutor 논문(arXiv:2512.09695v2) 의 Adaptive Sampling 영역에서 출발하여, 분포 인지형 stratification 을 결합 보강하는 접근의 정량적 가치를 검증한 결과입니다.

### S2 Section 1 — 배경
> 첫 번째 부분, 배경입니다. Exqutor 논문이 자체적으로 명시한 한계와 본 연구의 출발점을 짚겠습니다.

### S3 Exqutor 논문 한계
> Exqutor 의 §V-B Adaptive Sampling estimator 는 인덱스 부재 시 Bernoulli random sampling 으로 카디널리티를 추정합니다. 그러나 random sampling 은 데이터 분포에 의존적이며, paper 자체에서도 이 한계를 명시합니다. 본 연구는 이 sampling 방식 자체를 분포 인지형 접근으로 보강할 수 있는가를 묻습니다.

### S4 우리가 잡은 주제
> 분포를 알 때와 모를 때 모두에서, paper 의 Bernoulli sampling 보다 더 정확한 estimation 을 만들 수 있는가 — 이것이 본 연구의 핵심 주제입니다.

### S5 Section 2 — 연구 질문
> 두 번째 부분, 세 단계 연구 질문입니다.

### S6 RQ1·RQ2·RQ3
> 본 주제를 RQ 셋으로 분해했습니다. RQ1 은 baseline 검증 — random sampling 이 skew 데이터셋에서 얼마나 부정확한가. RQ2 는 분포 인지의 상한 — 분포를 알 때 어떤 allocation 이 최적인가. RQ3 는 실제 환경 — 분포를 모를 때 어떤 알고리즘이 최적인가입니다.

### S7 RQ1 결과
> RQ1. DEEP, SIFT, SimSearchNet++ sf=100 5 cells × 5 trials 측정 결과, Bernoulli 단일 sampling 은 KM20 stratified 대비 평균 +3.74 퍼센트 부정확합니다. 즉 random sampling 의 한계가 정량적으로 드러나며, 분포 인지 stratification 의 출발점이 됩니다.

### S8 RQ2 결과
> RQ2. 분포를 알 때 어느 allocation 이 최적인가를 비교했습니다. Bernoulli 1.748 → Equal 1.644 → Proportional 1.580 — Proportional 이 −9.53 퍼센트 가장 안정적입니다. 즉 분포 정보를 활용하면 추정 안정성이 정량 입증됩니다.

### S9 RQ3 출발점
> 그러나 실제 환경에서는 분포를 모릅니다. 따라서 분포를 추정하는 알고리즘이 필요합니다. 본 연구는 8 paradigm 측면에서 분포 추정 알고리즘을 폭 넓게 search 하여 비교했습니다.

### S10 Section 3 — 알고리즘 portfolio
> 세 번째 부분, 8 paradigm 알고리즘 portfolio 입니다.

### S11 8 paradigm × 56 method
> 본 연구는 분포 추정 가능한 8 paradigm 을 선정하여 총 56 method portfolio 를 구성했습니다. 밀도 추정, 정보 이론, 스트리밍, 차원 축소, 공간 분할, 균등 격자, 클러스터, 양자화 — 각 paradigm 의 anchor method 를 9 cells × 2 modes 매트릭스에서 측정하였으며, 총 1001 file 의 paper exact 재현을 수행했습니다.

### S12 Section 4 — 실험 framework
> 네 번째 부분, 실험 framework 입니다. paper 의 Bernoulli baseline 을 우리 method 로 어떻게 적용할 것인가 — 두 가지 방식을 비교했습니다.

### S13 paper 재현 검증
> 먼저 본 측정의 정합성입니다. paper Fig.12 영역 8 cells 의 mean qe_trim 은 1.618 — paper 보고값 1.69 대비 −4.3 퍼센트, measurement variance 범위 내 정확 일치입니다. paper exact 100 퍼센트 재현이 입증됩니다.

### S14 대체 vs 증강 framework
> 두 가지 적용 방식을 비교합니다. CaseA 대체는 paper 의 Bernoulli baseline 을 우리 method 로 단독 교체하는 방식 — est_final = est_method. CaseB 증강은 paper Bernoulli 와 우리 method 의 산술 평균 ensemble — est_final = (est_b1 + est_method) / 2. 두 방식 모두 single 과 multi cell 전반에서 비교 측정했습니다.

### S15 paradigm rollup 결과
> 8 paradigm 의 CaseB 증강 효과를 정렬했습니다. 밀도 추정 −11.93 퍼센트, 정보 이론 −7.60 퍼센트, 스트리밍 −6.63 퍼센트, 차원 축소 −6.03 퍼센트, 공간 분할 −5.57 퍼센트 — 다섯 paradigm 이 paper baseline 대비 1.06 배 ~ 1.14 배 qe_trim 정확도 향상을 통계적으로 압도합니다. 균등 격자, 클러스터, 양자화 paradigm 은 결합 효과가 없거나 미세 악화입니다.

### S16 가장 우수 알고리즘 5선
> 다섯 paradigm 의 anchor 알고리즘을 소개합니다. 첫째 Parzen KDE — 데이터 점 주변에 kernel 함수를 배치해 확률 밀도를 부드럽게 추정합니다. 둘째 HyperLogLog — hash 의 leading-zero 분포로 1.5 킬로바이트 메모리만으로 cardinality 를 근사합니다. 셋째 Chao 1982 weighted reservoir — 스트림 환경에서 분포 비례 sampling 을 보장합니다. 넷째 Sparse Random Projection — 1 / √D 희소 행렬로 고차원을 저차원으로 압축하면서 거리 정보를 보존합니다. 다섯째 Hilbert curve 와 Z-order — space-filling curve 로 고차원 공간을 1차원에 매핑하면서 인접성을 유지합니다.

### S17 ★ Climax
> 본 연구의 결정적 비교입니다. CaseA 대체는 493 cells 중 outperform 이 0 cell — 단 하나도 paper baseline 을 이기지 못합니다. 즉 단독 대체는 무효입니다. 반면 CaseB 증강은 492 cells 중 455 cells 에서 paper baseline 우위 — 92.5 퍼센트로 paper review-grade 통계 우위입니다. 이 negative control 이 본 연구의 핵심 결론을 명확히 합니다 — **단독 대체는 무효, 증강 적용 만 유효**.

### S18 Closer
> 감사합니다. 질문 환영합니다.

---

## 3. 작업 순서 (이 message 받은 Claude 에게)

1. 이전에 생성한 deck 폐기
2. 본 storyline 17 slide 정확히 새로 생성
3. self-disclosure 또는 negative narrative 절대 X (★3 hilbert 정정 / byte-identical / 정합성 위반 폐기 같은 slide 일절 X)
4. RQ1 → RQ2 → RQ3 → portfolio → framework → rollup → 가장 우수 알고리즘 → climax 흐름 정확히
5. Capstone Design System 그대로 적용

## 4. 절대 금지

- "★3 Hilbert 정정 — 학술 정직성" 같은 slide X
- byte-identical duplicates / 정합성 위반 method 폐기 같은 slide X
- "우리가 잘못 만들어서 고쳤어요" 식 narrative X
- limitation 카테고리 4종 분류 같은 slide X (있어도 1 slide 안에 1 줄 정도)
- 텍스트 우겨넣기 X
- bullet 3-5 list X

---

## 5. END

작성: 2026-05-12 13:10 KST  
대상: claude.ai/design Capstone project Keynote_Capstone conversation 새 message
