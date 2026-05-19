# Academic v3 deck — Follow-up Prompts (Claude Design chat)

> 2026-05-07 11:00 KST · 본 세션 (12:12 갱신: #A/#B/#C/#D 추가 — Worker A 핸드오프)
> **deck URL**: https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2?file=academic-deck%2Findex.html&slide=1
> **사용량 제약**: Claude Design 주간 78% — chat prompt 무제한 OK, 새 deck rebuild 1개만 가능
> **사용 방식**: 사용자가 위 URL 접속 → 우상단 chat 입력란에 prompt 복사 붙여넣기 → 차례로 발송

---

## 우선순위 0 (5/7 narrative 정정 후 — 최우선, 5/8 회의 전 발송)

> 5/7 narrative 정정 (commit 74d6aea) 반영 — 옵션 2 정직 reporting + contribution 7종 + Limitations 6종.
> 본 4 prompt (#A/#B/#C/#D) 발송 후 PPTX/PDF export → `submission/_drafts/속도는벡터_5월27일발표_v3_academic.{pptx,pdf}`.

### Prompt #A — Slide 6 (RQ1 진단) Phase 6/7 dual narrative

```
Slide 6 (RQ1 진단) 의 큰 수치 "ρ = -0.680" 옆에
"Phase 6 (SQL D, vector.c hook, production-near)" footnote 한 줄 추가해주세요.

하단 secondary stat row 에 추가 한 줄:
"Phase 7 (numpy D, simulation): ρ = +0.240 [-0.061, +0.480] CI 0 포함
— measurement methodology robustness sub-contribution honest 별도 보고"

polish only, layout 변경 X. 큰 -0.680 stat 자체는 유지.

근거: experiments/results/RQ1_RQ2_RQ3_종합_master.md (5/7 narrative 정정)
+ 5/8 회의 합의 옵션 2 정직 reporting.
```

### Prompt #B — Slide 11/12 사이에 5번째 contribution 슬라이드 추가 (HDBSCAN)

```
현재 16 slide 에 5번째 contribution 슬라이드 추가 (slide 11 negative control 직전 또는 직후):

타이틀: "RQ3 핵심 contribution 5: HDBSCAN — Density-Based Clustering 의 가치"

huge stat (좌측 navy bar 강조):
"−3.99% [−5.34, −2.12]"
"SIFT mid-sel (s=0.10), 모든 22 method 중 1위"

핵심 narrative:
- HDBSCAN density-based clustering: SIFT 의 더 큰 skew 환경에서 mid-sel
  가장 강한 effect (−3.99%, paired CI 0 제외)
- mid-sel (s=0.10) 의 sweet spot — 1% 너무 좁아 noise, 50% 너무 넓어 약화
- 4강 (Hilbert / MiniBatch / Hybrid / HDBSCAN) 의 마지막 핵심

implication bar (하단):
"density 인식 분할이 high-skew 환경의 mid-sel 에서 oracle 에 근접한 효과"

layout: 일관 유지 (좌측 navy bar + huge stat + implication bar + page indicator).
근거: experiments/results/rq3_agnostic/rq3_hdbscan_results.md
```

### Prompt #C — Slide 15 Limitation 4-card → 6-card 확장

```
Slide 15 Limitation 4-card 를 6-card 로 확장. 2×3 grid 또는 6-card row 로 layout.
card 별 1 line label + 1 line short description.

L1: Single-table only
    "multi-table 은 Exqutor main scope, 단일 정확성이 multi 의 필요조건 (future work)"

L2: KM20 oracle 학습 부담
    "full K-means ~30분, partial_fit (OLTP) + Hilbert (learning-free) 가 production replacement"

L3: Effect size practical small
    "모든 RQ3 method |d| < 0.8, p<0.05 는 sample size 효과 별도 보고. 어려운 query routing 가치 (spread 0.78)"

L4: numpy estimator sampling-population scope (NEW)
    "≤10K row 캐시 + HT weight 만 N=1M. 절대 q-error 인용 시 명시, 상대 비교 보존"

L5: RQ1 measurement methodology robustness (NEW)
    "Phase 6 (SQL D, vector.c hook) vs Phase 7 (numpy D) 5-cell 격차. 핵심 수치 Phase 6 production-near 기준"

L6: σ_i 신호 약함의 honest 입증 (NEW)
    "Anti-Neyman vs Proportional CI 0 제외, paired Wilcoxon p>0.5, Cohen's d<0.1. RQ3 distribution-agnostic 추구의 정직 motivation"

근거: experiments/results/RQ1_RQ2_RQ3_종합_master.md line 27-32 + 5/8 narrative 합의.
기존 4-card (Multi-table / vector.c / Distribution shift / Online streaming) 의 분류는 본 6-card 로 전면 교체.
```

### Prompt #E — Slide 4 (RQ1 결과) Phase 6/7 figure sidebar 삽입

> **D 결과 반영** (Worker D 5/7 12:15 figure 완료 — `phase6_vs_phase7_5sel.png` 2969×1782).
> 본 prompt 발송 전 사용자가 Claude Design 좌측 panel 에 figure 를 drag-drop upload 필요.

```
방금 upload 한 phase6_vs_phase7_5sel.png 를 Slide 4 (RQ1 결과) 우측 1/3 영역에
sidebar 형태로 삽입해주세요. (또는 Slide 6 RQ1 진단 footnote 옆 작게)

위치: Slide 4 우측 1/3 (제목 아래, page indicator 위)
크기: slide 1/3 폭 × 1/2 높이
caption (figure 하단 한 줄):
"Phase 6/7 5-cell 격차 — methodology robustness 정량 입증"
slide layout 일관 유지.

근거: 5/7 W2 Worker D 분석. Phase 6 (SQL D, vector.c hook, ρ=−0.680 CI 0 제외)
vs Phase 7 (numpy D, simulation, ρ=+0.240 CI 0 포함) 의 measurement
methodology robustness 시각화. Slide 12 L5 limitation 의 visual evidence.
```

### Prompt #D — Slide 14 (Q&A) Q6 추가 (Phase 6/7 origin)

```
Slide 14 (Q&A) 에 Q6 추가 (현재 Q1-Q5 5개 → Q6 추가 후 6개):

Q6: "Phase 6 (SQL D) 와 Phase 7 (numpy D) 격차의 origin 은?
     왜 단조성 결론이 환경 의존적인가?"

A: 격차의 origin 두 가지 —
   (1) numpy estimator 가 ≤10K row 캐시에서 추출하고 HT weight 만 N=1M 적용
       → sampling-population scope 가 SQL `tablesample` (full table) 와 다름.
   (2) vector.c hook 의 production env 측정 path 가 numpy 시뮬레이션 측정 path 와 다름.
   본 연구는 Phase 6 production-near 결과 핵심 인용, Phase 7 결과 honest 별도 보고.
   5-cell 격차 자체를 measurement methodology robustness sub-contribution 으로 격상.
   채림 석사 자문 사항 (5/15 메일 발송 예정).

근거: 5/7 W2 발견 + outline 정정 (line 257-258).
layout 일관 유지. Q1-Q6 모두 1 line question + 2-3 line answer.
```

---

## 우선순위 1 (필수, 5/8 회의 전 발송)

### Prompt #1 — Slide 6 "6 selectivity bins" 정정

```
slide 6 의 stat box 캡션에 "n=5 seeds × 6 selectivity bins" 라고 적혀있는데, 실제 측정은 5 selectivity bins (50%, 30%, 10%, 5%, 1%) 입니다. "6" → "5" 로 정정해주세요.

캡션 정확한 표현은:
"95% bootstrap CI [-0.800, -0.440] · DEEP-KM20 · n=5 seeds × 5 selectivity bins · 0 not in CI"

근거: experiments/results/RQ1_RQ2_RQ3_종합_master.md line 56, RQ1_RQ2 실험 결과 정리.md line 290-303 (5sel × 3 dataset gradient 표).
```

### Prompt #2 — Slide 13 ARI matrix 값 검증 요청

```
slide 13 의 ARI matrix 4 offline methods (Hilbert / KM20 / MiniBatch / HDBSCAN) 값들이 정확한지 검증해주세요. 현재 spec 에 1.00 / 0.74 / 0.73 / 0.62 등 값이 명시되어 있는데, 출처 파일은 experiments/results/rq3_agnostic/rq3_method_redundancy_ari.md 입니다.

검증 후 정확한 값으로 update 부탁드립니다. 만약 ARI matrix 가 4-method 가 아닌 다른 method 조합으로 측정되어 있다면, 가장 의미있는 4-method (4강 = Hilbert / MiniBatch / Hybrid / HDBSCAN) 로 재구성 권장.
```

### Prompt #3 — Cover slide background 흰색 유지 확인

```
slide 1 (Cover) 의 background 가 spec 에 "전체 흰 #FFFFFF (다크 슬라이드 없음)" 라고 적혀있는데, preview 화면에서 검정 배경으로 보이는 가능성이 있습니다.

확인해주시고:
- 의도된 검정 배경이라면 → spec ("다크 슬라이드 없음") 와 모순. WHITE 배경 + navy 타이틀로 재조정 권장.
- 단순 preview 로딩 이슈라면 → 그대로 두되 PDF export 시 WHITE 가 정상 출력되는지 확인.

Academic 디자인 시스템의 일관성 (16 slide 모두 WHITE) 유지가 중요합니다.
```

---

## 우선순위 2 (선택, 시간 여유 시)

### Prompt #4 — Slide 8 22-method bar 가독성 보강

```
slide 8 의 22-method effect size bar 에서 4강 ★ (Hilbert / MiniBatch / Hybrid / HDBSCAN) 의 color-coded category 를 더 명시적으로 강조해주세요.

현재 spec: "color-coded by category: learning-free / learned offline / online weight / oracle / negative / baseline"

보강:
- 4강 ★ 4 bar 에 outline 또는 ★ marker 추가 (다른 18 method 와 시각적 분리)
- legend 에 category 별 색상 + ★ = "paired CI 0 제외 4강" 명시
- bar 높이 기존 대비 1.3-1.5× 확대 (가독성 ↑)
```

### Prompt #5 — Slide 12 8M 비단조 narrative 강조

```
slide 12 (Cross-scale) 의 "DEEP_8M ✗ 비단조 (증 0 / 감 2, n=3)" 발견을 narrative 측면에서 더 강조해주세요.

현재 implication bar: "ranking 은 일관, gradient 패턴은 규모에 따라 미묘"

보강안:
"1M 의 단조성 결론이 8M 으로 자동 이전되지 않음 — sample_size=385 한계 + Q-error 자체가 6-8× 로 신호 < 잡음 영역. ★ honest limitation 으로 발표 강조."

이 honest limitation 명시가 캡스톤 평가위원에게 신뢰성 ↑ 효과. 5/27 발표에서 강재현 발표자가 "limitation 도 정량적으로 관측" narrative 가능.
```

---

## 우선순위 3 (선택, 학술 콘텍스트 보강)

### Prompt #6 — Speaker notes 톤 점검

```
16 slide 의 speaker notes 한국어 대본을 빠르게 검토해주세요. 검토 포인트:
1. 슬라이드당 30-45초 분량 적정한가
2. 한국어 자연스러움 (일본어식 직역 / 영어식 어순 없는지)
3. 핵심 수치 (ρ -0.680, 1,189×, -0.156 등) 의 한국어 발음 자연스러움
4. 발표자 (강재현 주발표) 가 외울 수 있는 분량인가
5. 박세은 / 조현빈 / 이동욱 분담 시 톤 일관성

문제 지점 1-2개 만 알려주시면 그 부분만 수정합니다.
```

### Prompt #7 — Limitation slide (15) 4-card 분류 검증 ⚠️ **#C 로 SUPERSEDED (5/7 12:12)**

> 본 prompt 는 4-card 검증용. 5/7 narrative 정정 (옵션 2 + 6-Limitations) 후 #C 가 4→6 확장으로 전면 교체. 발송 금지.

```
slide 15 Limitation 의 4-card grid:
- L1 Multi-table
- L2 vector.c integration
- L3 Distribution shift
- L4 Online streaming

이 4 분류가 master.md line 27-32 의 4 limitation:
1. 단일 테이블 (multi-table future work)
2. KM20 oracle (production 학습 부담, partial_fit + Hilbert 가 replacement)
3. Effect size practical small (Hilbert d=-0.156)
4. vector.c Python 시뮬레이션 (memory leak)

과 매핑이 일치하는지 검증해주세요. 만약 #3 effect size 가 빠져있고 #4 가 두 번 들어있다면 정정 권장.
```

---

## 발송 순서 권장

```
지금 (5/7 12:12 KST) ★ 우선순위 0 (narrative 정정, 5/8 회의 전 필수)
                   → Prompt #A 발송 (Slide 6 Phase 6/7 dual narrative, 2-3분)
                   → Prompt #B 발송 (Slide 11/12 5번째 contribution HDBSCAN, 5-10분)
                   → Prompt #C 발송 (Slide 15 Limitation 4 → 6-card, 3-5분)
                   → Prompt #D 발송 (Slide 14 Q6 추가, 2-3분)
                   → [phase6_vs_phase7_5sel.png drag-drop upload 후]
                     Prompt #E 발송 (Slide 4 figure sidebar, 3-5분)
                   → 5 prompt 응답 후 PPTX/PDF export (Share → Export)

기존 우선순위 1 (시간 여유 시 추가 발송, 5/8 전 발송 가능)
                   → Prompt #1 발송 (slide 6 "6 sel" → "5 sel" typo, 1분)
                   → Prompt #2 발송 (slide 13 ARI 검증, 5-10분 응답)
                   → Prompt #3 발송 (cover background 확인, 1-2분)

5/7 14:00 ~ 18:00 → Prompt #4 / #5 (선택, 시간 여유 시)

5/8 회의 (19:00) 직전 → Prompt #6 (선택, 학술 콘텍스트 보강)
                       (#7 은 #C 로 superseded — 발송 금지)
```

## Export 절차 (Step 4 — Worker A 핸드오프)

#A/#B/#C/#D 4 prompt 응답 confirm 후:

```
1. Claude Design 우상단 Share → Export as PPTX
   → submission/_drafts/속도는벡터_5월27일발표_v3_academic.pptx

2. Claude Design 우상단 Share → Export as PDF
   → submission/_drafts/속도는벡터_5월27일발표_v3_academic.pdf

3. 한글 폰트 검증 (Apple SD Gothic Neo) — Slide 1, Slide 12, Slide 15 문장 단위 확인
   ⚠️ 깨짐 시 Claude Design chat 으로 "Apple SD Gothic Neo (또는 Noto Sans KR) 폰트 강제 적용" 재발송

4. 검증 후 git commit:
   git add submission/_drafts/속도는벡터_5월27일발표_v3_academic.{pptx,pdf}
   git commit -m "5/27 발표 deck Academic v3 v1 export — 옵션 2 narrative + contribution 7종 + Limitations 6종"
   git push
```

검증 기준 (worker A §4):
- [ ] Slide 6 dual narrative 표기 (Phase 6 main + Phase 7 honest)
- [ ] Slide 11/12 사이 HDBSCAN 5번째 contribution slide 등장 (총 17 slide 가능)
- [ ] Slide 14 Q6 추가 (Q1-Q6 6개)
- [ ] Slide 15 Limitations 6-card 확장 (L1-L6)
- [ ] Slide 4 (또는 6) Phase 6/7 figure sidebar 등장 (#E 발송 후)
- [ ] PPTX/PDF 한글 폰트 깨짐 X (Apple SD Gothic Neo)
- [ ] Master 1:1 수치 일관 — ρ=−0.680 / d=−0.156 / ARI=1.000 / HDBSCAN −3.99% / inverse Manhattan 1.000

## Worker D figure 의존성

- Slide 4 또는 6 sidebar 의 figure source: `experiments/figures/rq1_motivation/phase6_vs_phase7_5sel.png`
- ✅ **2026-05-07 12:15 KST D figure 완료** (2969×1782, 200KB) — Prompt #E 로 즉시 반영 가능
- Worker A 의 Step 2 (Slide 4 footnote 보강) → text-only 우회 불필요. #E 발송으로 figure 즉시 sync.

---

## 사용량 알림

- Claude Design 주간 78% — 토 오전 1:00 KST 리셋 (5/9 (토) 01:00)
- 5/7 ~ 5/9 사이 chat prompt 는 무제한 OK
- 새 deck rebuild 는 토 리셋 후 (5/9 (토) 01:00 이후) 가능
- 즉 5/27 발표 전 하나의 새 deck 가능 시점: 5/9 (토) 01:00 ~ 5/16 사용량 한계 도달 전

---

**작성**: Claude (본 세션) · 2026-05-07 11:00 KST
