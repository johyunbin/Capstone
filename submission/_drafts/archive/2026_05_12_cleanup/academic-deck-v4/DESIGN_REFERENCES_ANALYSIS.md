# 디자인 레퍼런스 6건 분석 + 차용 포인트

> **사용자 피드백** (5/11 21:04): "현재 deck 약간 너무 PPT 느낌 → 좀 더 디테일하게. wireframe 느낌도 발표 자료로 적절. 여러 장점 취합."

## 1. 검토한 6 design URL

| # | Name | Type | 주요 강점 |
|:-:|---|---|---|
| 1 | **Capstone Wireframes** | 50 artboards (10 type × 5 var) | 10 slide types × 5 variations, brand red, paper texture, sticky note, **chapter dividers Big Number/Centered/Red full-bleed/TOC/Quote** |
| 2 | **Capstone Midterm Deck** | 22 slide (4/30 final) | **CAPSTONE 2026-1 · MIDTERM PRESENTATION · 연세대학교** 헤더, **3 column (팀/지도/분석 대상)**, **#DC2626 단일 red accent**, **챕터 전 큰 빨간 번호 divider**, footer 정증 정보 |
| 3 | **W1 Sprint Detailed** | 22 slide (W1 narrative) | tournament 구조 narrative (22-method → 4강 paired CI), Mechanism RQ3 본문 흡수, Cross-Scale 비단조 |
| 4 | **Samsung Research style** | 16 slide | **blue stripe, dot tag rows, 4-card grids, Implication outline boxes**, 13px mono labels + 17px lead text |
| 5 | **Capstone Animation** | 95초 motion, 7 scene | Cover → Problem (selectivity 0.71% vs 68.4%) → Sampling 비교 → Pipeline (Query→Sample→Estimate→Plan) → Results 카운트업 → Stats (CI 막대 + ρ heatmap) → Closer |
| 6 | **Capstone High fidelity microsite** | 12 section scroll | Custom SVG charts: Spearman ρ heatmap (diverging RdBu_r), paired Q-error scatter with hover, KM20 CI-whisker bars with significance markers, Tweaks (KO/EN, density compact/normal/roomy) |

## 2. 차용할 디자인 요소 7가지

### A. 상단 헤더 작은 빨간 텍스트 (Midterm Deck)
- 현재: header right "속도는벡터 · CAPSTONE 2026"
- 변경: 좌측 상단 작은 빨간 mono 텍스트 **"CAPSTONE 2026-1 · FINAL PRESENTATION · 연세대학교"** 추가 — 학교/세션 명시
- 학술 발표 톤 강화

### B. Cover 3 column 정보 grid (Midterm Deck)
- 현재: 4 column (TEAM / ADVISOR / REFERENCE / DATE)
- 변경: 3 column (TEAM / ADVISOR / REFERENCE) — DATE 는 위 헤더에 통합
- 더 깔끔 + 정보 압축

### C. 챕터 전 section divider (Wireframes + Midterm Deck)
- 현재: 4 chapter (배경/검증 설계/결과/한계 향후) sub로 인식만 (S2 목차 only)
- 변경: 4 chapter section divider 슬라이드 4개 신설 또는 chapter heading 시각 강화
- 옵션 A: 18 → 22 slide (S2.5, S5.5, S8.5, S16.5 신설) — chapter divider 슬라이드
- **옵션 B (권장)**: 18 slide 유지, 챕터 시작 slide 의 numbered badge 옆에 chapter 번호 (I/II/III/IV) 작게 추가
- 옵션 C: 챕터 시작 slide eyebrow 앞에 "CHAPTER I · 배경" 형식

### D. dot tag rows (Samsung)
- 현재: label-mono 영문 mono letterspacing
- 변경: label-mono 앞에 작은 navy/red dot 마커 추가 (•) — 시각 hierarchy
- 카드 / 카테고리 / chapter heading 에 일관 적용

### E. footer 디테일 (Midterm Deck)
- 현재: 좌 "속도는벡터 · CAPSTONE 2026" + 우 "2026.05.27"
- 변경: 좌 "속도는벡터 · 박세은 강재현 조현빈 이동욱" + 우 "최종발표 · 18 slides · 2026.05.27" 또는 단순 페이지 번호 (모듈 옵션)
- 학술 정보 명시

### F. Implication bar variation (Samsung)
- 현재: 모든 slide 하단 navy fill + red left border + 흰 텍스트 implication bar
- 변경: chapter heading slide 와 closing slide 는 outline 변형 (흰 배경 + navy border + navy 텍스트), 본문 slide 는 fill 유지
- 시각 변화 + chapter 구분 강조

### G. 발표 자료 디테일 (Wireframe 감성)
- 종이 톤 (paper texture) X — 발표 학술 톤 유지
- Kalam 손글씨 X — 발표 학술 톤 X
- 다만 다음은 차용:
  - **margin / padding 여백 증가** — breathing room 확보 (현재 약간 빡빡)
  - **카드 corner border-radius 0** — 학술 톤 (현재 2px 유지 OK)
  - **sub-note / annotation** — 일부 큰 수치 옆에 작은 helper text (예: "p < 0.001" 같은)
  - **figure caption + source attribution** — 차트/heatmap 아래 작은 caption (예: "Source: 자체 측정 5/11")

## 3. 현재 deck 디테일 향상 영역

### S1 Cover
- 좌상단 헤더 작은 빨간 텍스트 추가 → "CAPSTONE 2026-1 · FINAL PRESENTATION · 연세대학교"
- 4 column → 3 column (TEAM / ADVISOR / REFERENCE), DATE 헤더로
- 부제 padding 증가
- 분석 대상 column 추가 (Exqutor / arXiv:2512.09695v2)

### S2 목차
- 4 chapter card 안 sub-slide list margin 증가
- chapter 번호 시각 강화 (현재 "I / II / III / IV" 작음 → 큰 빨간 navy number)

### Chapter divider 추가 검토 (4 신설 또는 시각 강화)
- Option B 권장: chapter 시작 slide eyebrow "CHAPTER I · 배경" 추가

### Body slides
- 큰 수치 옆 sub-note 추가 (예: S12 92.9% 옆 "p < 1e-45")
- 카드 padding 미세 증가
- figure 아래 caption 추가 (예: F1 paradigm rollup 의 경우 "9 paradigm × 56 method × 9 cell")

### S17 한계
- 4 column 카테고리 좀 더 breathing
- "원천 한계 · 확장 검증 한계 · 측정 정밀화 한계 · 최근 발견된 한계" 카테고리 명 그대로 OK

### S18 마무리
- 본 연구 한 줄 요약 카드 padding 증가
- 감사 / Q&A 영역 좀 더 강조

## 4. 차용 NOT 권장 요소

- Wireframe 의 Kalam 손글씨 — 학술 톤 X
- Paper texture — 학술 톤 X
- Sticky note rationale — 발표 deck 톤 X
- Microsite scroll format — 발표 deck 과 별개 format
- Animation 95초 motion — 별도 piece (발표 사이 끼우기 가능)

## 5. 우선순위 prompt 핵심 7가지

1. 상단 헤더 "CAPSTONE 2026-1 · FINAL PRESENTATION · 연세대학교" 빨간 mono 작은 텍스트 추가
2. Cover 4 → 3 column (TEAM / ADVISOR / REFERENCE), DATE 헤더 통합
3. Chapter heading 시각 강화 — 챕터 시작 slide eyebrow 앞에 "CHAPTER I · 배경" 형식 + 큰 chapter 번호
4. label-mono 앞 dot 마커 (•) 추가
5. footer 좀 더 detail — "속도는벡터 · 박세은 강재현 조현빈 이동욱 · 최종발표"
6. 큰 수치 옆 sub-note 추가 (p-value, sample size 등 statistical detail)
7. figure caption + source attribution (각 chart 아래 작은 mono 텍스트)

---

작성: 2026-05-11 21:10 KST
