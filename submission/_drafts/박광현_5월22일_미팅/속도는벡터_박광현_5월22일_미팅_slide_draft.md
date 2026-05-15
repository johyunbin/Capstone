# 속도는벡터 — 5/22 박광현 미팅 slide draft (v11 framing 반영)

> 작성: 2026-05-16 KST · 박세은 framing 단순화 의도 (5/15 + 5/16 00:18 카톡) 완전 반영 · prompt v11 (5/16 00:50) base · "cardinality 추정" 표현 모두 제거 + "Sample Selection" 영역 일관 통일
> 본 영역 N2 (4 file 中 slide draft 영역) · 5/22 박광현 미팅 영역 4-5 장 발표 영역 markdown text + speaker notes + reference

---

## 0. 본 slide 영역 base + 1 page 요약 (under 250 words)

본 5/22 박광현 미팅 영역 slide draft 는 **5/27 발표 deck v11** (25 slide) 영역 핵심 5 영역만 추려 4-5 장 영역 미팅 자료 영역 정리한 영역. 5/27 발표 D-5 영역 framing reframing 의 정합성을 박광현 교수님 영역 사전 검증 받기 위한 영역 목적이다.

핵심 변경 (v10 → v11) 영역 박세은 framing 단순화 의도 ("우리는 추가 method 통해서 Q-error 만 보완하면 되는 게 아니냐. 카디널리티 추정은 알아서 할거고") 의 직접 반영이다. paper Exqutor §V-B Adaptive Sampling 영역 cardinality 추정 mechanism 은 **paper 본인 contribution** 영역 그대로 유지하고, 우리 영역은 그 estimation 의 input 인 **sample selection 영역만** 정량 검증한다. 두 layer 의 명확 분리 영역 본 발표 톤 정확 영역 base 다.

slide 1 영역 main theme 은 "Distribution-aware Sample Selection for VAQ Cardinality Estimation" 영역 변경 (v10 영역 "Cardinality Estimation 우리 영역 contribution" 영역 모호 표현 → v11 영역 "Sample Selection 우리 영역 + Cardinality Estimation paper 영역" 영역 명확 분리). slide 2 영역 framing layer 분리 다이어그램, slide 3 영역 16 sample selection method × 7 paradigm matrix, slide 4 영역 Pareto Top 5 cell × method best 매핑 + dynamic 할당 mechanism flow, slide 5 영역 Q-error 영역 paired Δ% 92.5% evidence + 5/27 발표 D-5 영역 risk mitigation. 본 4-5 장 영역 박광현 교수님 영역 5/27 발표 framing 정합성 영역 사전 검증 영역 받기 위한 영역.

---

## Slide 1 — 제목 + main theme reframing

### 본문 (slide 위)

```
v11 framing reframing
─────────────────────
Distribution-aware Sample Selection for VAQ
```

sub: "based on Exqutor §V-B Adaptive Sampling — 박세은 framing 단순화 의도 반영 (5/16 00:18)"

### Layout

- 중앙 거대 폰트 "**v11 framing reframing**" (200px, navy #1e3a5f)
- 다음 줄 "**Distribution-aware Sample Selection for VAQ**" (120px, navy)
- 그 아래 sub: "based on Exqutor §V-B Adaptive Sampling" (Inter Light, 32px, 회색)
- 하단 우측: "박광현 교수님 미팅 · 2026.05.22 · 속도는벡터"
- 배경: 흰색
- 시각: 우상단 mini accent line (navy, 4px, 100px)

### speaker notes

> 5/22 박광현 교수님 미팅 영역 본 발표 영역 = 5/27 발표 D-5 영역 framing reframing 사전 검증 영역. 박세은 5/15 + 5/16 00:18 카톡 영역 framing 단순화 의도 ("우리는 추가 method 통해서 Q-error 만 보완하면 되는 게 아니냐. 카디널리티 추정은 알아서 할거고") 의 직접 반영. 본 reframing 의 핵심 영역 = "cardinality 추정" 표현 모두 제거 + "Sample Selection" 영역 일관 통일. paper Exqutor §V-B Adaptive Sampling 영역 cardinality 추정 mechanism 은 paper 본인 contribution 영역 그대로 유지 + 우리 영역 = 그 estimation 의 input 인 sample selection 영역만 augment. 본 미팅 영역 framing 의 정합성 영역 박광현 교수님 영역 사전 검증 영역.

### reference

- v11 prompt Part 1/3 §0.1-0.2 (slide 2 main theme + framing layer 분리)
- handoff v32 §2.2 (박세은 framing 단순화 의도)
- narrative v6 §0 main theme + §1.1 framing layer 분리

---

## Slide 2 — framing layer 분리 (paper 영역 vs 우리 영역, 2 column 다이어그램)

### 본문 (slide 위)

```
framing layer 분리
─────────────────
paper 영역 (그대로)        우리 영역 (sample selection augment)
                ↓
        cardinality 추정 = paper 영역
        sample selection = 우리 영역
```

### Layout (2 column 다이어그램)

- 상단 제목: "**framing layer 영역 분리**" (Inter Bold, 80px, navy)
- 좌측 column (50%, 회색 배경 #f5f5f5):
  - 제목: "**paper 영역 (그대로)**"
  - bullet 1: "§V-A ECQO HNSW range query"
  - bullet 2: "§V-B Adaptive Sampling Eq 1-6"
  - bullet 3: "**cardinality 추정 mechanism**"
  - 하단 라벨: "→ 본 발표 = 간단 소개"
- 우측 column (50%, navy 배경 #1e3a5f, 흰 텍스트):
  - 제목: "**우리 영역 (sample selection augment)**"
  - bullet 1: "Phase 1 분포 인지 stratification"
  - bullet 2: "Phase 2 sample 추출"
  - bullet 3: "Phase 3 결합 minimal (산술 평균)"
  - 하단 라벨: "→ 본 발표 = 핵심 영역"
- 두 column 사이 가운데 화살표 (navy, "augment" 표현)
- 하단 한 줄 (전체 폭, navy 강조): "**cardinality 추정 = paper 영역 / sample selection = 우리 영역**"

### speaker notes

> 본 발표 영역 framing 두 layer 의 명확 분리. **좌측 = paper 영역 (그대로 유지)** = Exqutor §V-A ECQO HNSW range query + §V-B Adaptive Sampling Eq 1-6 + cardinality 추정 mechanism 자체. paper 본인 contribution 영역 = 그대로 인정 + 본 발표 = 간단 소개. **우측 = 우리 영역 (sample selection augment)** = Phase 1 분포 인지 stratification + Phase 2 sample 추출 + Phase 3 결합 minimal (산술 평균). 영역 핵심 룰 = "cardinality 추정 mechanism 영역 우리 영역 contribution X" — sample selection 영역만 우리 영역. 박광현 교수님 영역 본 framing 의 학술 정합성 영역 검증 부탁. 학부 capstone 이론 검증 자세 영역 일관 + paper 본인 contribution 영역 인정 + 우리 영역 = 정직한 학부 영역 sample selection augment 만.

### reference

- v11 prompt Part 1/3 §3 (slide 3 framing layer 분리 다이어그램 verbatim)
- narrative v6 §1.1-1.3 (framing layer 분리 + 표현 통일 + 학술 의의)
- 박세은 5/16 00:18 카톡 (framing 단순화 의도)

---

## Slide 3 — sample selection 16 method overview (7 paradigm matrix)

### 본문 (slide 위)

```
사용 16 sample selection method
─────────────────────────────
P1 Cluster (3) | P2 Spatial (3) | P3 Streaming (1) | P4 DimReduction (4)
P5 QMC (2)     | P6 Quantization (2) | P9 InfoTheoretic (1)
─────────────────────────────
모두 sample selection 영역 mechanism (cardinality 추정 algorithm 영역 X)
```

### Layout (7 paradigm 매트릭스)

- 상단 제목: "**paradigm 별 사용 16 sample selection method**" (Inter Bold, 80px, navy)
- 7 paradigm matrix 표 영역:

| paradigm | method (사용 영역) | count | Pareto Top 5 |
|---|---|---:|---|
| **P1 Cluster** | minibatch_partial / gmm / faiss_ivf | 3 | — |
| **P2 Spatial** | hilbert_real ★ / zorder_morton / skilling_hilbert | 3 | hilbert_real |
| **P3 Streaming** | chao_weighted ★ | 1 | chao_weighted |
| **P4 DimReduction** | sparse_rp ★ / pca1d ★ / rsvd / ica_fastica | 4 | sparse_rp / pca1d |
| **P5 QMC** | cum_sqrtf / lavallee_hidiroglou | 2 | — |
| **P6 Quantization** | rabitq_strat / mhist2 | 2 | — |
| **P9 InfoTheoretic** | hyperloglog ★ | 1 | hyperloglog |

- 하단 ★ 라벨 (작은 회색): "★ = Pareto Top 5 (정확도 best = 자원 best)"
- 우측 박스 (navy 배경, 흰 텍스트): "**모두 sample selection 영역 mechanism**"
- 작은 footnote (회색): "폐기 40 method (정합성 위반 + algorithm audit drop + 측정 미커버) 영역 narrative 미언급"

### speaker notes

> 본 발표 영역 사용 16 sample selection method. 7 paradigm 영역 covering — P1 Cluster (3) / P2 Spatial (3) / P3 Streaming (1) / P4 DimReduction (4) / P5 QMC (2) / P6 Quantization (2) / P9 InfoTheoretic (1). ★ 5 영역 = Pareto Top 5 (정확도 best 동시 자원 best) — chao_weighted (Type 1 small sf=1 best −14.11%) / sparse_rp (fit_time 3.67s 최단) / hyperloglog (메모리 O(m·log log n) 최compact) / pca1d (textbook 10/10 audit pass) / hilbert_real (★3 PCA-2D-lex sort alias 정정 후 raw Hilbert curve 표준 구현). **모두 sample selection 영역 mechanism** — cardinality 추정 algorithm 영역 X. 폐기 40 method 영역 narrative 미언급 (정합성 위반 10 + algorithm audit drop 23 + 측정 미커버 7).

### reference

- v11 prompt Part 2/3 Slide 8 (paradigm 별 사용 16 method overview)
- v11 prompt Part 2/3 Slide 9-15 (paradigm 별 method 알고리즘 step diagram)
- handoff v32 §3 (사용 16 method 확정)
- narrative v6 §5 (16 method × 7 paradigm matrix)

---

## Slide 4 — Pareto Top 5 cell × method best 매핑 + dynamic 할당 mechanism flow

### 본문 (slide 위)

```
Pareto Top 5 — Type 별 best sample selection method
────────────────────────────────────────────────
Type 1 → chao_weighted K=20    Δ% −14.11% ★
Type 4b → Centroid 결합        Δ% −7.37% ★
────────────────────────────────────────────────
dynamic 할당 mechanism — sample selection 영역만 dynamic
(paper Adaptive Eq 1-6 영역 그대로 유지)
```

### Layout (상단 표 + 하단 flow)

**상단: Pareto Top 5 cell × method best 매핑 표 (50% 영역)**

| Type | best sample selection method | Δ% (실험군 vs 대조군 paired) |
|---|---|---:|
| **Type 1** small sf=1 | **chao_weighted K=20** | **−14.11%** ★ |
| **Type 2** medium sf=10 | (sweet spot 약함) | −6.00% |
| **Type 3** large sf=100 | chao_weighted / sparse_rp K=20 | −11~−12% |
| **Type 4a** multi 224-288d | hilbert_real K=30 | (Pareto 中 선택) |
| **Type 4b** multi 864d | Centroid tuple 결합 | **−7.37%** ★ |

**하단: dynamic 할당 mechanism flow (50% 영역, 세로 flow)**

```
[데이터셋 진입]
       ↓
Step 1: dataset profile (row / structure / dim)
       ↓
Step 2: Type 판별 (Type 1/2/3/4a/4b 中 1)
       ↓
Step 3: Type 별 권장 sample selection method 자동 선택
       ↓
Step 4: CaseB ensemble — est_final = (b1 + method) / 2
       ↓
[paper §V-B Adaptive Eq 1-6 보정 (그대로 유지, paper 영역)]
```

- 우상단 navy 박스 (작은): "★ sample selection 영역만 dynamic"
- 우하단 회색 박스 (작은): "paper Adaptive Eq 1-6 영역 = 그대로 유지 (dynamic X)"

### speaker notes

> 본 발표 영역 핵심 contribution = Pareto Top 5 cell × method best 매핑 + dynamic 할당 mechanism flow. **상단 표** = Type 별 best sample selection method 매핑 (Type 1 small sf=1 → chao_weighted K=20 영역 best −14.11%, Type 4b multi 864d → Centroid tuple 결합 영역 best −7.37%). **하단 flow** = 데이터셋 진입 → profile → Type 판별 → Type 별 sample selection method 자동 선택 → CaseB ensemble → paper Adaptive Eq 1-6 보정 (그대로). **영역 핵심 주의 = dynamic 영역 = sample selection 영역만**. paper Adaptive Eq 1-6 영역 = 그대로 유지 (dynamic X). 두 영역 명확 분리 영역 박광현 교수님 영역 검증 부탁. 학술 정합성 영역 = paper §V-B Eq 1-6 verbatim 100% 유지 + 우리 영역 = sample selection 영역만 augment.

### reference

- v11 prompt Part 3/3 Slide 16 (Pareto Top 5 cell × method best 매핑)
- v11 prompt Part 3/3 Slide 17 (dynamic 할당 mechanism flow)
- handoff v32 §4.1 chain 영역 새 구조 (v10_full16 진행 중 → 5/16 02:30 ETA)
- narrative v6 §6 Pareto Top 5 + §7 dynamic 할당 mechanism

---

## Slide 5 — Q-error paired Δ% 92.5% evidence + 5/27 발표 D-5 risk mitigation

### 본문 (slide 위)

```
sample selection 영역 Q-error 개선 evidence
───────────────────────────────────────
paired Δ%      92.5%   (455/492, p < 1e-45)
Cliff's δ      63.0%   large better (311/494)
Hedges' g      55.7%   large effect size (275/494)
one-sided p<0.05  45.3%  outperform (224/494)
───────────────────────────────────────
negative control: CaseA 단독 대체 = 0/493 = 0% (대체 가설 폐기)
```

### Layout (상단 거대 수치 + 하단 risk mitigation)

**상단: Q-error paired Δ% 92.5% evidence (60% 영역)**

- 중앙 거대 수치 "**paired Δ% 92.5%**" (Inter Bold, 250px, navy)
- 그 아래 sub: "sample selection vs random Bernoulli — Q-error 영역 개선"
- 하단 표 영역 (4 row):

| metric | 결과 | 의미 |
|---|---:|---|
| paired CaseB < CaseA | **92.5%** (455/492) | p < 1e-45 |
| Cliff's δ large better | **63.0%** (311/494) | effect size large |
| Hedges' g large | **55.7%** (275/494) | effect size large |
| one-sided p<0.05 outperform | **45.3%** (224/494) | 통계 유의 |

- 우상단 navy 박스 (작은): "★ 본 연구 핵심 evidence"
- 우하단 회색 박스 (작은): "negative control: CaseA 단독 대체 = 0/493 = 0% (대체 가설 폐기)"

**하단: 5/27 발표 D-5 risk mitigation (40% 영역, 3 박스)**

- **Risk 1**: framing 모호 (v10 영역) → **mitigation**: v11 reframing 영역 layer 분리 + sample selection 일관 (slide 2 + slide 3 영역 적용)
- **Risk 2**: Pareto Top 5 cell 영역 cover 부족 → **mitigation**: chain 영역 v10_full16 + v9_sel_sweep 영역 진행 중 (5/17 새벽 COMPLETE 영역 ETA + 약 2039 file 영역 portfolio + Pareto Top 5 영역 모두 cover)
- **Risk 3**: paper §V-B exact 영역 위반 의혹 → **mitigation**: Phase 3 결합 영역 = 산술 평균 minimal (paper Eq 1-6 verbatim 100% 유지 + augment 영역만, 대체 X)

### speaker notes

> 본 발표 영역 핵심 evidence + risk mitigation. **상단 = Q-error paired Δ% 92.5% evidence** — sample selection 영역 우리 method 가 random Bernoulli 대비 Q-error 영역 paired Δ% 92.5% 개선 (455/492, p < 1e-45). Cliff's δ large better 63.0% + Hedges' g large 55.7% + one-sided p<0.05 outperform 45.3%. negative control: CaseA 단독 대체 가설 = 0/493 = 0% (단독 대체 X, **augment 영역만 valid**). 영역 주의 = "cardinality 추정 algorithm 우리 영역 개선" 표현 사용 X — Q-error 영역 = sample selection 영역 input 영역 quality 영역. **하단 = 5/27 발표 D-5 risk mitigation** — Risk 1 framing 모호 (v10) → v11 reframing 영역 layer 분리 + sample selection 일관 / Risk 2 Pareto Top 5 cell 영역 cover 부족 → chain 영역 v10_full16 + v9_sel_sweep 영역 진행 중 (5/17 새벽 COMPLETE 영역 ETA) / Risk 3 paper §V-B exact 위반 의혹 → Phase 3 결합 영역 = 산술 평균 minimal (paper Eq 1-6 verbatim 100% 유지 + augment 영역만). 박광현 교수님 영역 본 evidence + risk mitigation 영역 검증 부탁.

### reference

- v11 prompt Part 3/3 Slide 18 (Q-error paired Δ% 92.5% evidence)
- handoff v32 §4 chain 영역 새 구조 (v10_full16 + v9_sel_sweep 진행 중)
- handoff v32 §6 prompt v11 paste 대기
- narrative v6 §8 Q-error paired Δ% evidence + §13 5/27 발표 D-5 risk mitigation

---

## ★ 본 slide draft 영역 5/22 박광현 미팅 영역 활용 영역

본 5 장 영역 = 5/22 박광현 미팅 영역 약 15-20 분 영역 발표 영역. 각 slide 영역 3-4 분 + Q&A 5 분 영역. 박광현 교수님 영역 검증 부탁 영역 핵심 3 영역:

1. **framing 의 학술 정합성** (slide 2 + slide 4 영역) — paper 영역 vs 우리 영역 layer 분리 영역 학부 capstone 영역 정직 자세 + 학술 정합성 검증
2. **Pareto Top 5 cell × method 매핑 영역 dynamic 할당 mechanism** (slide 4) — Type 별 best method 자동 선택 영역 base + paper Adaptive 영역 그대로 유지 영역 검증
3. **Q-error paired Δ% 92.5% evidence 영역 통계 검정 영역** (slide 5) — sample selection 영역 Q-error 영역 개선 영역 통계 유의성 검증 + risk mitigation 영역 5/27 발표 D-5 영역 ready 영역 검증

본 미팅 영역 박광현 교수님 영역 input 영역 → 5/27 발표 D-5 영역 reframing 영역 final lock 영역 base.

---

## ★ 본 slide draft 영역 file 위치 + commit 룰

- 위치: `submission/_drafts/박광현_5월22일_미팅/속도는벡터_박광현_5월22일_미팅_slide_draft.md`
- 본 file 영역 = 5/22 박광현 미팅 영역 N2 (4 file 中 slide draft 영역)
- 함께 작성 예정 (본 작업 영역 외):
  - N1: `속도는벡터_박광현_5월22일_미팅_사전보고.md` (사전보고 영역 5/22 미팅 의제 + 핵심 영역 사전 정리)
  - N3: `속도는벡터_박광현_5월22일_미팅_review_form.md` (review form 영역 박광현 input 영역 caputre form)
  - N4: `속도는벡터_박광현_5월22일_미팅_예상질문.md` (예상질문 + 답변 영역 사전 준비)

작성: 2026-05-16 KST · v11 framing reframing (sample selection 일관 + cardinality 추정 표현 모두 제거) 완전 반영 · 박세은 5/16 00:18 framing 단순화 의도 + handoff v32 + prompt v11 (3 part) base · 5 slide × 3-4 분 영역 박광현 교수님 영역 5/27 발표 D-5 framing 정합성 사전 검증 영역
