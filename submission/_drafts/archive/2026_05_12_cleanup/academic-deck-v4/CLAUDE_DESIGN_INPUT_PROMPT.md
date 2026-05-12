# Claude.ai/Design 직접 Input Prompt — v4 academic deck

> **용도**: claude.ai/design 에 그대로 복사-붙여넣기로 사용. 본 세션에서 작성한 18 slide React JSX (Slides.jsx) 와 index.html + deck-stage.js + figures/F1~F6.png 모두 input 으로 사용.
>
> **참조**: `submission/_drafts/5_27_발표_deck_v4_ULTRAPLAN_20260511.md` (각 slide 상세 spec)
>
> **작업 시점**: 5/16 ~ 5/19 (5/15 박광현 미팅 confirm 후 minor 정정만)

---

## 단계 0 — 사전 준비 (5/16 morning)

1. claude.ai/design 접속 → 기존 그룹 진입 또는 새 design 생성
   - 기존 그룹: https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2?file=academic-deck%2Findex.html
   - 또는 새 design 생성 (api.anthropic.com/v1/design/h/...)
2. 본 디렉토리 4 file 모두 input attach:
   - `index.html` (18 slide deck-stage + speaker notes + CSS 디자인 시스템)
   - `Slides.jsx` (S1~S18 React 컴포넌트, 954 line)
   - `deck-stage.js` (v3 base 그대로, scaling + nav + ⌘P print)
   - `figures/` 폴더 6 PNG (F1~F6 paper exact 측정 결과)

---

## 단계 1 — 첫 input prompt (복사-붙여넣기)

```
5/27 캡스톤 최종 발표용 18 slide academic deck v4 를 클로드 디자인에서 시각 finalize 해줘.

## 현재 상태
- 18 slide React JSX (Slides.jsx, 954 line, S1~S18)
- deck-stage 1280×720 16:9
- 디자인 시스템: 흰 배경 + navy stripe + numbered badge + IBM Plex Sans KR + Inter + JetBrains Mono
- Color tokens: navy #1B3DAD primary / red #E03A3A negative / green #2A9D6E 신규 / gold #D9A53B paradox
- 5/8 v3 base Chrome + Impl 컴포넌트 그대로 재사용

## 18 slide 구성
01 Cover (Skew-Aware Stratified Sampling Ensemble + paper exact subtitle)
02 TOC (7-card grid: Problem / Prior / Approach / RQ1 / Paradigm 9 / RQ2 / CaseB Climax)
03 Problem (pgvector 33.3 / VBASE 50 / DuckDB 100% + 실제 0.001~90% 분포)
04 Prior Exqutor §V-A ECQO + §V-B Adaptive (본 연구 영역)
05 Approach (ensemble avg 다이어그램: est_b1 + est_method / 2.0)
06 RQ1 distribution gap (+3.74%)
07 Paradigm 9 framework (9 paradigm card grid 3×3, P9/P10 green ★ 신규)
08 RQ2 Paradox (Anti 1.540 < Prop 1.580 < Neyman 1.595)
09 RQ3 Paradigm Rollup CaseB (P10 -11.93 / P9 -7.60 / P3 -6.53 / P4 -5.92 / P2 -5.52)
10 ★3 Hilbert defect rectify (4 anchor card)
11 Top winners (Top 5 @ A5-sf1)
12 CaseB Ensemble Climax ★ main contribution (92.9% / 63.5% / 56.4% / 71.8%)
13 Negative Control · CaseA broken (0/437 vs 284/447 좌우 대비)
14 Cross-scale sf 1/10/100
15 Mechanism locality 분리 (4 anchor × 9 cell heatmap)
16 Effect Size honesty (4축 통계)
17 Limitation 18종 (Group A/B/C/D 4 column)
18 Future Work 8 + Closing (감사 + Q&A)

## 핵심 원칙
- 1 slide = 1 메시지 — 텍스트 최소
- 핵심 수치는 50-80px navy bold 시각 강조
- 학술 산문 본문은 speaker notes 로 분리
- bullet list ❌ → 시각화 / 카드 / 다이어그램으로 대체
- 5/8 v3 Academic 디자인 시스템 그대로 유지

## 검토 우선순위
1. S7 Paradigm 9 — P9/P10 신규 강조 (green border + ★ 마커)
2. S12 CaseB Climax — 4 큰 수치 + bias-variance 비유 + 의사 비유
3. S10 ★3 hilbert defect rectify — PCA proxy vs 진짜 Hilbert 4 anchor 분리 검증
4. S17 Limitation 18종 — Group D 5/11 신규 5건 red border
5. S18 Future 8건 + 본 연구 한 줄 요약 + 감사 + Q&A

## 기대 산출
- 18 slide deck visual finalize
- PDF export (Chrome ⌘P, 1280×720 비율, 배경 그래픽 체크)
- speaker notes 한국어 학술 산문 18 entry 점검

상세 spec: 첨부 `5_27_발표_deck_v4_ULTRAPLAN_20260511.md` 참조.
```

---

## 단계 2 — Iteration 1 (5/16 afternoon)

첫 렌더 결과 확인 후 정정 요청:

```
1차 렌더 확인했어. 다음 사항 정정해줘:
- S{N}: {구체적 문제}
- S{N}: {구체적 문제}
- 전반: {시각 hierarchy / 색상 / 간격 등}
```

각 slide 별 체크리스트:
- [ ] S1 Cover — title 60px, 부제 18px, 4-col footer 정렬
- [ ] S2 TOC — 7-card grid 균형 (3+4 또는 4+3)
- [ ] S3 Problem — 33.3/50/100% navy bold + 0.001~90% 강조
- [ ] S4 Prior — §V-A vs §V-B 좌우 대비 (red 박스 §V-B 강조)
- [ ] S5 Approach — ensemble avg 다이어그램 중앙 + 비유 1줄
- [ ] S6 RQ1 — +3.74% 큰 수치 + 1.6180 vs 1.69 paper exact
- [ ] S7 Paradigm 9 — 3×3 grid + P9/P10 green border ★ 신규
- [ ] S8 RQ2 Paradox — 5-way bar + red border PARADOX 카드
- [ ] S9 RQ3 Rollup — 9 paradigm Δ% bar + Top 5 anchor
- [ ] S10 Hilbert rectify — 4 anchor card 가로 균등
- [ ] S11 Top winners — Top 5 ranking + A5-sf1 dominance
- [ ] S12 CaseB Climax — **4 큰 수치 시각 임팩트 최대** ⭐ 가장 중요
- [ ] S13 Negative Control — CaseA red vs CaseB navy 좌우 대비
- [ ] S14 Cross-scale — sf 별 trend + paper Fig 14 anchor
- [ ] S15 Mechanism heatmap — 4 anchor × 9 cell 색상 gradient
- [ ] S16 Effect Size — 4축 통계 카드 + 4축 검증 설명
- [ ] S17 Limitation — 4 column + Group D red border 강조
- [ ] S18 Future + Closing — 4×2 future + 본 연구 한 줄 요약 + 감사

---

## 단계 3 — Iteration 2 ~ 4 (5/17 ~ 5/19)

- 2차: figures 6건 통합 (F1~F6 image asset)
- 3차: speaker notes 18 entry × 30-45초 분량 검증 (총 12-15분)
- 4차: visual hierarchy 최종 점검 (수치 크기 / 색상 / 간격 통일)
- 5차 (선택): PDF export visual 일치 확인

---

## 단계 4 — PDF Export (5/20)

1. claude.ai/design 에서 최종 deck preview
2. ⌘P (Mac) / Ctrl+P (Windows)
3. 인쇄 대상 → "PDF로 저장"
4. 페이지 크기: A4 가로 또는 16:9 사용자 정의 (1280×720 비율)
5. 여백: 없음
6. 배경 그래픽: 체크 (필수)
7. 저장 → `submission/_drafts/속도는벡터 — Academic v4 · Final 5_27.pdf`
8. PPTX 변환 (선택, Adobe / pandoc / online converter)

---

## 단계 5 — 5/15 박광현 미팅 후 정정 (5/16 ~)

미팅 confirm 결과에 따라 minor 정정만:
- S8 RQ2 paradox 표현 (만약 narrative 변경 시)
- S17 Limitation 추가 또는 정정
- S18 Future Work 우선순위 조정

미팅 자료: `submission/_drafts/박광현_5월15일_미팅/`

---

## 단계 6 — 5/26 finalize 직전 (5/25 ~ 5/26)

- [ ] 18 slide × 1 메시지 원칙 준수
- [ ] 핵심 수치 50-80px navy bold 일관성
- [ ] figures 6건 통합 (Korean font)
- [ ] speaker notes 30-45초 분량 (총 12-15분)
- [ ] PDF export OK
- [ ] 강재현 발표 리허설 (5/25~5/26)
- [ ] Q&A 가이드 강재현 검토

---

작성: 2026-05-11 20:11 KST  
다음: 5/15 박광현 미팅 → 5/16 claude.ai/design input → 5/19 iteration finalize → 5/20 PDF export → 5/26 강재현 리허설 → 5/27 19:00 최종 발표
