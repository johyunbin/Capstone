# 포스터 시각 자산 Nano Banana Pro brief (Gemini Ultra 활용)

> 작성 2026-05-24 01:00 KST · 대상: 발표 포스터 (900 × 1200 mm 세로 PDF) 의 시각 자산 보강
> 협업: Claude Design (layout · 16 단 grid · 4 섹션 · 5행 표) × Gemini Ultra Nano Banana Pro (illustration · 도식 · plan 트리) — 둘 다 활용
> 의존: 포스터 prompt (`속도는벡터_포스터_prompt_20260523_235540.md`) + storyline NEW v2 (`...storyline_NEW_v2_20260524_001301.md`)

---

## 사용법 (사용자 진행)

1. Gemini Ultra 웹앱 (또는 Whisk·Flow) 진입.
2. 아래 자산 1~5 각각의 Nano Banana Pro prompt 를 복붙 → 이미지 생성.
3. 생성 이미지를 다운로드 후 claude.ai/design 의 "포스터" 디렉토리 에 import.
4. Claude Design 이 포스터 layout 의 해당 위치에 자산 삽입.
5. PDF export 후 메인 세션이 5축 vision 검증.

**Why 협업** = Claude Design 은 layout · 정렬 · typography 정확하지만 illustration 생성 약함 / Nano Banana Pro 는 illustration · 이미지 내 텍스트 렌더링 1위 (Pro 보다 Ultra 한도 큼). 둘 다 활용 (사용자 5/24 명시: "어느 하나만으로 한다기 보다는 둘 다 활용").

---

## 자산 1 — VAQ 분석가 시나리오 illustration (섹션 ① 좌상단)

**위치**: 포스터 섹션 ① "왜 카디널리티 추정이 중요한가" 헤더 옆 (좌상단). 슬롯 약 80 × 80 mm.

**Nano Banana Pro prompt** (Gemini 웹앱 복붙):
```text
A modern data analyst sitting at a laptop, looking at a SQL query that combines vector similarity search and text analytics. Style: minimal, flat illustration, navy and cyan tones (matching navy #1E3A5F and cyan gradient). The laptop screen shows a SQL query with both "SELECT" keyword and a vector icon (small dotted points). On the side: small icons of image search, text reviews, time series — all merging into one query. Korean text label below: "VAQ — 한 SQL 안에 벡터 + 텍스트 + 시계열". Apple SD Gothic Neo font (Apple's San Francisco Korean rendering style). White background. Aspect ratio 1:1.

Style references:
- Clean academic illustration (not cartoonish)
- Navy primary, cyan accent
- No human face details (just shoulder/profile silhouette)
- Vector icons mixed with SQL text editor style
- Korean text rendering must be sharp (Nano Banana Pro 1위 강점 활용)

Do NOT include:
- Photorealistic faces
- English-heavy SQL syntax (keep minimal)
- Drop shadows or 3D effects (flat 2D only)
- "★" star symbol
```

**검증**:
- [ ] navy + cyan 컬러 일관 (포스터 design system)
- [ ] 한국어 텍스트 "VAQ — 한 SQL 안에 벡터 + 텍스트 + 시계열" 정확 렌더링
- [ ] 1:1 비율 (포스터 슬롯 80×80mm 맞춤)
- [ ] flat 2D · 학술 톤 (cartoonish X)

**Fallback**: 생성 실패 시 ICDE 원논문 슬라이드 3-9 의 RAG analyst 시나리오 캡처 또는 간단한 텍스트 박스 ("VAQ = 벡터 + SQL 분석가 시나리오").

---

## 자산 2 — plan 트리 비교 도식 (섹션 ③ 결과 영역)

**위치**: 포스터 섹션 ③ "결과 — 89% 우위의 진짜 메커니즘" 상단 또는 좌측. 슬롯 약 150 × 100 mm (가로 직사각형).

**Nano Banana Pro prompt**:
```text
A side-by-side comparison of two SQL execution plan trees. Left plan tree: marked in coral/red (#F97316 hint), with "Wrong cardinality estimate" Korean label "잘못된 카디널리티 추정". Right plan tree: marked in green/emerald (#10B981), with Korean label "올바른 추정". Both trees show:
- Top node: "Result" (큰 노드)
- Middle: Join + Filter operators
- Bottom: Table scans (with vector search icon for one leaf)
The arrows between nodes are thick on the left (slow) and thin on the right (fast). Below: "최대 1만 배 차이" (largest text), with smaller text "한 단계의 추정 실수가 전체 응답 시간을 결정".

Style:
- Academic infographic, minimal flat 2D
- Navy primary background labels
- Korean text Apple SD Gothic Neo style (sharp, readable at 1m distance)
- Coral and emerald subtle (not overwhelming)
- White background
- Aspect ratio 3:2 (horizontal)

Do NOT include:
- 3D perspective trees
- Excessive arrows
- English SQL keywords (keep abstract)
- Star (★) symbols
```

**검증**:
- [ ] 좌 red (잘못)·우 green (올바른) 명확 구분
- [ ] 한국어 "최대 1만 배 차이" 큰 글씨 렌더링
- [ ] 화살표 두께 차이 (좌 굵게·우 가늘게)
- [ ] 1m 거리 가독

**Fallback**: ICDE 원논문 슬라이드 25 "Q3 plan comparison" 캡처 + 한국어 라벨 overlay.

---

## 자산 3 — Exqutor §V-B 표본 선택 한 단계 highlight (섹션 ② 또는 본문)

**위치**: 포스터 섹션 ② "측정 설계 — 네 방식의 짝 비교" 상단 또는 본문 안. 슬롯 약 120 × 80 mm.

**Nano Banana Pro prompt**:
```text
A flow diagram showing Exqutor §V-B Adaptive Sampling step-by-step. Five horizontal boxes connected by arrows: "데이터 진입" → "표본 추출 (빨간 사각형 강조)" → "추정 계산" → "모멘텀 보정" → "최종 카디널리티". Only the second box "표본 추출" is highlighted with a thick red outline (#F97316) — others are faded gray. Below the highlighted box, a callout: "이 한 단계만 통제 실험으로 들여다봤습니다".

Style:
- Academic infographic
- Navy + cyan + coral highlight
- Apple SD Gothic Neo Korean text
- Flat 2D, white background
- Aspect ratio 3:2 (horizontal)

Korean text rendering must be sharp.
```

**검증**:
- [ ] 5 box 흐름 + "표본 추출" 단 한 곳 highlight (coral · 굵은 outline)
- [ ] 한국어 텍스트 5 라벨 + 1 callout 정확 렌더링
- [ ] 다른 4 box faded gray (시각 우선순위)

**Fallback**: 단순 텍스트 그래프 (Claude Design 자체 SVG 로 생성 가능).

---

## 자산 4 — 4 갈래 도식 동등 시각 (섹션 ③ 결과 — latency 부분)

**위치**: 포스터 섹션 ③ "결과" 하단 또는 우측. 슬롯 약 130 × 70 mm.

**Nano Banana Pro prompt**:
```text
A horizontal 4-step arrow flow diagram: "기본 엔진" (gray) → "베이스라인" (navy) → "결합" (cyan) → "정답" (emerald #10B981). All four arrows between steps are the SAME thickness (visual equality — IMPORTANT). Above the diagram: "베이스라인 4.43× ≈ 결합 4.46× ≈ 정답 4.54× — 동등". Below: "결합 방식과 베이스라인 모두 정답 수준 plan 회복" (smaller, navy bold).

Style:
- Academic infographic, flat 2D
- Apple SD Gothic Neo
- White background
- Aspect ratio 13:7 (horizontal)

CRITICAL: All three arrows (베이스라인→결합, 결합→정답, 기본 엔진→베이스라인) must be the same thickness. Do NOT emphasize 결합→정답 alone — this would mislead viewers into thinking 결합 is uniquely close to 정답.
```

**검증**:
- [ ] 4 단계 카드 색 (gray·navy·cyan·emerald) 정합
- [ ] 화살표 3 개 모두 동일 굵기 (★ 비-차별 시각)
- [ ] 한국어 본문 "4.43× ≈ 4.46× ≈ 4.54× — 동등" 정확 렌더링
- [ ] navy 굵게 강조 박스 ("결합·베이스라인 모두 정답 수준 plan 회복")

**Fallback**: Claude Design SVG 자체 생성 (단 화살표 동일 굵기 명시).

---

## 자산 5 — 본 연구 기여 4 카드 아이콘 (섹션 ④)

**위치**: 포스터 섹션 ④ "본 연구의 기여 + Future Work" 의 본 연구 기여 4 카드 각각 헤더 옆. 슬롯 약 30 × 30 mm × 4 개 (작은 사이즈).

**Nano Banana Pro prompt** (4 개 아이콘 한 번에 batch):
```text
Generate 4 minimalist flat icons in a 2×2 grid, each 256×256 px, with white background and navy + cyan + emerald accents:

1. Icon "메커니즘 분리": A magnifying glass over a 5-row table (the control table). Korean label below: "메커니즘 분리".
2. Icon "음성 대조": A bar chart with one bar significantly lower (35.2%) and arrow pointing down. Korean label: "음성 대조".
3. Icon "구조적 한계": Two parallel arrows of equal length (baseline ≈ oracle visual). Korean label: "구조적 한계".
4. Icon "측정 엔지니어링": A wrench + circuit board pattern (engineering). Korean label: "엔지니어링".

Style:
- Flat 2D, minimal
- Navy primary, cyan/emerald accent
- Apple SD Gothic Neo Korean labels (sharp)
- Each icon distinct but visually cohesive set
- White background, no drop shadows

Do NOT include:
- 3D effects
- Photorealistic elements
- English text
- Star (★) symbols
```

**검증**:
- [ ] 4 아이콘 시각 일관 (set 으로 보이게)
- [ ] 각 한국어 라벨 정확 렌더링
- [ ] 256×256 px 각각, 포스터 30×30mm 슬롯 다운스케일 가독

**Fallback**: 단순 emoji 또는 numbered circle (1·2·3·4).

---

## 검증 체크리스트 (5 자산 생성 후 메인 세션 또는 Gemini Vision)

### 자산별
- [ ] 자산 1 분석가 illustration — 한국어 텍스트 sharp · navy/cyan
- [ ] 자산 2 plan 트리 비교 — 색 구분 명확 · "1만 배" 큰 글씨
- [ ] 자산 3 §V-B highlight — 한 단계만 강조 · 4 단계 faded
- [ ] 자산 4 4 갈래 도식 — 화살표 동일 굵기 (★ 비-차별)
- [ ] 자산 5 4 아이콘 — set 일관 · 한국어 라벨

### 일관성 (5 자산 공통)
- [ ] design system carry — navy #1E3A5F · cyan #0EA5E9 · 악센트 4 색 (배경·방법·결과·적용)
- [ ] Apple SD Gothic Neo 한국어 일관
- [ ] flat 2D · 학술 톤 · cartoonish X
- [ ] 흰 배경 · 텍스트 잘림 0

### 포스터 import 후
- [ ] 16 단 grid 슬롯에 정합 (자산 비율 일치)
- [ ] 1m 거리 가독 (자산 + 텍스트 본문 모두)
- [ ] 시각적 무게중심 = 섹션 ③ 결과 (5행 표 + 강조 박스) 유지 — 자산 보조

---

## 다음 단계 (사용자 진행)

1. **자산 1~5 Gemini 웹앱 (Nano Banana Pro) 에서 각각 생성** — 위 prompt 복붙. AI Ultra 한도 풍부 — 한 번에 5 자산 batch 생성 가능.
2. **다운로드** — 각 자산 PNG 형식 저장 (`/tmp/poster_asset_1.png` ~ `_5.png`).
3. **claude.ai/design "포스터" 디렉토리 import** — 포스터 prompt 본문 (`속도는벡터_포스터_prompt_20260523_235540.md`) 본문 다 복붙한 다음, 자산 5 개를 추가 upload.
4. **Claude Design 이 자산을 포스터 16 단 grid 의 정해진 위치에 삽입**.
5. **PDF export** → `속도는벡터_포스터_<TS>.pdf`.
6. **메인 세션 5축 검증** — Gemini Vision (시각) + Codex 텍스트 + 직접 확인.
7. **QR 코드 placeholder → 영상 YouTube URL 회수 후 갱신** (Phase 5 영상 업로드 후).

산출물:
- 본 brief = `submission/_drafts/속도는벡터_포스터_시각자산_Nano_Banana_Pro_brief_20260524_010021.md`
- 자산 5 PNG = Gemini 웹앱 생성 후 사용자가 `/tmp/` 또는 `submission/_drafts/` 저장
- 포스터 final PDF = `submission/_drafts/속도는벡터_포스터_<TS>.pdf`

---

작성: 2026-05-24 01:00 KST · Claude Design × Gemini Ultra 협업 패턴 · Nano Banana Pro 5 자산 brief · 5/28 12:00 포스터 마감
