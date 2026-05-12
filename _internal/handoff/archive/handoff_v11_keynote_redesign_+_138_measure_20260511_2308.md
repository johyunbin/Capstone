# Handoff v11 — 5/11 23:08 KST  
## 키노트 스타일 재설계 + 138 measurement 회수 + 팀원 공유

> **본 세션 5/11 21:00~23:08 전체 산출**: 6 design ref 분석 + 정밀 prompt 두 차례 적용 후 academic-deck 22 slide 완성. 그러나 **5/11 22:56 사용자 명시**: "이건 발표 PT가 아니야. 키노트 한다고 생각해봐" + "100% coverage 거짓" 지적 — academic-deck 텍스트 우겨넣기 학술 PDF 톤 → **Apple Keynote / Samsung Unpacked 스타일 재설계** + **138 measurement 미커버 launch** 완료.

---

## 0. TL;DR — 다음 세션 첫 30초

```bash
# 1. 측정 회수 — 138 measurement 진행 중
ssh capstone2026@165.132.140.240 "tmux ls && ls /mnt/hdd0/home/capstone2026/log/{fillgap_tier1,remaining_seq}_DONE.flag 2>/dev/null && ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*.json | wc -l"
# 예상: 972 + 138 = 1110 file (완료 시)

# 2. handoff_v11 (본 file) read

# 3. 다음 세션 핵심 mission
# - 측정 완료 회수 + analyze + REPORT v11
# - claude.ai/design 에서 **새 conversation 시작** — academic-deck 폐기
# - Wireframes 50 artboards base + 키노트 스타일 prompt 작성
# - 1 slide = 1 메시지 + 시각 위주 + 텍스트 최소
```

---

## 1. ★ 핵심 사용자 피드백 (5/11 22:56)

> "이건 진짜 너무 텍스트만 우겨넣고 이건 발표 pt가 아니야. 너 대기업에서 키노트하거나 할 때 이딴 식으로 하는거 봤어? 난 못봤어. 키노트 한다고 생각해봐 제발"

**사용자가 좋게 본 자료**:
- https://claude.ai/design/p/019ddd7f-0db4-714b-98bb-d518cc0e2734 (Capstone Animation)
- https://claude.ai/design/p/019ddd7e-92bb-7c48-bc54-ab9593c18287 (Capstone Wireframes)

**현재 academic-deck 폐기 필요**:
- https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2 — 텍스트 우겨넣은 학술 PDF 톤

---

## 2. 키노트 스타일 재설계 plan

### 2.1 디자인 철학 — 대기업 키노트 톤

**참조 (Apple Keynote / Samsung Unpacked / Google I/O)**:
- **1 slide = 1 메시지** — 3-5 단어 / 한 수치 / 한 시각화
- **거대 폰트** — 핵심 수치 100-300px (full screen 차지)
- **minimal text** — 본문 narrative 는 speaker notes 로 100%
- **whitespace 넉넉** — slide 70% 이상 빈 공간
- **시각 위주** — 다이어그램 / heatmap / chart 만, bullet list 0
- **단일 색 accent** — brand red `#DC2626` 만, 다른 색 minimal

### 2.2 Wireframes 50 artboards 활용 (Capstone Design System)

각 slide 타입별 5 variation 중 **키노트 친화 variation 선택**:

| Slide 타입 | Wireframe variation | 키노트 친화도 |
|---|---|:-:|
| **Cover** | Big-number / Editorial / Diagram | ★ Big-number / Diagram |
| **TOC** | Big numbers / Map / Two-col w context | ★ Big numbers |
| **Problem** | **Big-stat range** / Distribution / Pipeline diagram | ★ Big-stat range |
| **Background** | Two cards / Decision tree / Table / Annotated zoom / Sequence | ★ Sequence |
| **Approach** | Two-col / Pipeline circles / Equation / **Visual intuition** / Stack | ★ Visual intuition |
| **Results** | **Big chart** / Table hero / Grid stats / Single callout / Mixed | ★ Big chart / Single callout |
| **Section dividers** | **Big number** / Centered minimal / Red full-bleed / TOC / Quote | ★ Big number (이미 적용) |
| **Closer** | **Big thanks** / Recap / Centered / Contact / Next steps | ★ Big thanks |

### 2.3 18 slide 키노트 스타일 재구성 (proposed)

| # | 키노트 슬라이드 | 핵심 시각 |
|:-:|---|---|
| 01 | (Cover) "벡터 데이터베이스의 카디널리티 추정" — 한 줄 + 팀명 + 일자 | 빅 타이포 only |
| 02 | (Section 1) "01 / 배경" — 큰 빨간 번호 | divider |
| 03 | (Problem) "**0.001% ~ 90%**" 거대 수치 + "고정 비율로 답 안 됨" 한 줄 | Big-stat range |
| 04 | (Background) Exqutor → 두 갈래 (ECQO / Adaptive) → 본 연구 위치 | Sequence diagram |
| 05 | (Section 2) "02 / 접근" | divider |
| 06 | (Approach) "Bernoulli + KM20 = 산술 평균" diagram | Visual intuition |
| 07 | (Section 3) "03 / 검증" | divider |
| 08 | (RQ1) "**+3.74%**" 거대 수치 only | Big stat |
| 09 | (RQ2) "Anti < Prop < Neyman" 거대 텍스트 + bar 5개 | Big chart |
| 10 | (Paradigm) 8 paradigm grid + 한국어 이름 + Δ% 큰 수치 | Big chart |
| 11 | (★ Climax) "**92.9%**" 거대 단일 수치 — full screen | Big number Single callout |
| 12 | (Climax 보조) "63.5% / 56.4% / 71.8%" 3 stats | Grid stats |
| 13 | (Negative Control) "0 / 437" CaseA vs "284 / 447" CaseB | Comparison |
| 14 | (Hilbert 정정) Before "★3 hilbert" → After "Hilbert 곡선 + Z-order + Skilling" | Diagram |
| 15 | (Cross-scale) sf=1/10/100 trend chart | Big chart |
| 16 | (Section 4) "04 / 한계와 향후" | divider |
| 17 | (Limitation) 4 group 카테고리 카드 + 18 항목 | Mixed grid |
| 18 | (Closer) "감사합니다" 거대 타이포 + Q&A | Big thanks |

**텍스트 분량 / slide**:
- 본문: 3-5 단어 + 큰 수치 + 시각화
- speaker notes: 30-50초 분량 한국어 산문

### 2.4 색상 / 폰트 / 사이즈

**색상** (Wireframes colors_and_type.css):
- Brand red `#DC2626` 단일 accent (큰 수치 / section number / underline)
- Ink `#0A0A0A` (제목)
- FG2 `#404040` (부제)
- BG `#FFFFFF` (배경) + BG2 `#FAFAF9` (divider tinted)

**폰트** (Wireframes 기준):
- 국문: Apple SD Gothic Neo / Pretendard Variable
- 영문/숫자: Inter (tabular figures)
- mono: JetBrains Mono (eyebrow / caption)

**사이즈** (키노트 스타일):
- **거대 수치**: 200-300px (full screen 차지)
- **거대 제목**: 80-120px
- **본문**: 28-36px (학술 deck 16-18px → 키노트 28-36px)
- **부제**: 20-24px
- **eyebrow**: 12-13px (Wireframes 11px → 키노트 12-13px)

---

## 3. 138 measurement 진행 상황

### 3.1 launch 완료 (2 tmux sequential 진행 중)

**pb_fillgap** (Tier 1 — 13 measurement, 시작 13:55:19 UTC):
- 1 missing 7개: factor_join (A1-SIFT CaseA) / opq (A1-SIFT CaseB) / lhs (A5-scale-sf100 CaseA) / kdpp (A1-SSN CaseA) / lp_bound (A1-SSN CaseA) / neurocard_lite (A1-SSN CaseA) / thompson_sampling (A1-SSN CaseB)
- 2 missing 6개: coreset / dense_rp / halton × A1-SSN CaseA/CaseB
- timeout 7200s/cell
- ETA 5-10시간

**pb_remaining_seq** (Tier 3 + Tier 2 + KDE — 125 measurement, 시작 13:58:53 UTC):
- Tier 3 (19): agglomerative 2 / vinecopula 5 / kdtree 4 / dbscan 8
- Tier 2 (90): dirichlet 18 / kernelpca 18 / neuocard 18 / birch 18 / hdbscan 18 (각 18 cell-mode)
- KDE (16): kde_parzen × 8 cells × 2 modes
- timeout 172800s (48h) /cell
- ETA 5-15일

### 3.2 KDE drop 결정 취소

**이전 (잘못)**: "KDE 측정 비현실 → drop + limitation"
**수정 (5/11 23:00)**: KDE 도 paper exact mode (1000 q × 10 trials) 으로 sequential 측정 진행. 며칠 걸려도 OK. timeout 48시간/cell. 18/18 완료 시 발표 사용, 미완 시 발표에서 제외 (사용자 정책).

### 3.3 회수 방법 (다음 세션)

```bash
ssh capstone2026@165.132.140.240 "ls /mnt/hdd0/home/capstone2026/log/{fillgap_tier1,remaining_seq}_DONE.flag 2>/dev/null && cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 analyze_paper_exact.py 2>&1 | tail -20 && ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*.json | wc -l"
```

---

## 4. 다음 세션 mission (5/12 ~ 5/16)

### 4.1 (D-0) 측정 회수 + REPORT v11
- pb_fillgap + pb_remaining_seq 회수 확인 (DONE flag)
- analyze_paper_exact.py 재실행 → REPORT v11
- 18/18 완료 method 만 발표 자료 채택
- 18/18 미완료 method 는 limitation 으로 정직 명시

### 4.2 ★ 키노트 스타일 새 deck 생성

**진행 단계**:
1. **claude.ai/design 새 conversation 시작** (academic-deck 폐기)
2. Wireframes (`/tmp/capstone_refs/wireframe/`) Capstone Design System 토큰 + primitives 직접 import
3. Midterm Deck (`/tmp/capstone_refs/midterm/`) SectionDivider 컴포넌트 차용
4. 키노트 스타일 prompt 작성 (1 slide = 1 메시지 + 시각 위주 + 텍스트 최소)
5. 18 slide 키노트 스타일 생성
6. 핵심 slide visual 검증 (S1 / S3 SectionDivider / S11 Climax / S18 Closer)
7. PDF export → `submission/_drafts/속도는벡터 — Final 5_27 키노트.pdf`

### 4.3 팀원 공유

**준비 자료**:
- 측정 완료 결과 (REPORT v11)
- 18/18 method 별 Δ% summary
- 키노트 deck PDF
- 핵심 narrative 한 페이지 (팀원 외우는 용도)

**공유 채널**:
- 카톡 (속도는벡터 그룹)
- Notion (Capstone 작업 페이지)
- GitHub Capstone (push)

**팀원 메시지 (제안)**:
```
팀원들 측정 마무리 + 발표 deck 키노트 스타일 새로 만들었어. 
- 측정: 1100+ file 완료 (Tier 1 + Tier 2 + Tier 3 + KDE 모두 / 18 method 18/18 완료)
- 발표 deck: Wireframes Capstone Design System + 키노트 스타일
- 5/15 박광현 교수 미팅 자료 / 5/27 최종 발표 deck

각자 확인 + 5/15 미팅 준비:
- 박세은 팀장: 전체 narrative 검토
- 강재현: 발표 스크립트 (speaker notes 외우기)
- 조현빈: 측정 결과 / 디자인
- 이동욱: limitation / future work 정리
```

---

## 5. 본 세션 산출 파일

### 5.1 디자인 ref source
- `/tmp/capstone_refs/wireframe/` — 9 file (colors_and_type.css / wireframe-primitives.jsx / slides-cover.jsx / slides-toc-problem.jsx / slides-method-results-divider-closer.jsx / slides-code-approach-roadmap.jsx / design-canvas.jsx / tweaks-panel.jsx / Capstone Wireframes.html)
- `/tmp/capstone_refs/midterm/` — 5 file (slides.jsx 1006 line / 22 speaker notes / colors_and_type.css / deck-stage.js / tweaks-panel.jsx)
- `/tmp/capstone_refs/samsung/samsung-deck/` — 2 file

### 5.2 분석 / plan 문서
- `submission/_drafts/academic-deck-v4/DESIGN_REFERENCES_ANALYSIS.md` (6 design ref 분석)
- `submission/_drafts/academic-deck-v4/REVAMP_PLAN.md` (8 카테고리 진단, 이전 라운드)
- `submission/_drafts/academic-deck-v4/CLAUDE_DESIGN_INPUT_PROMPT.md` (claude.ai/design 단계별 input)
- `_internal/handoff/active/handoff_v10_kde_drop_+_design_finalize_20260511_2245.md` (이전 handoff, KDE drop 결정 정정 필요)
- `_internal/handoff/active/handoff_v11_keynote_redesign_+_138_measure_20260511_2308.md` (본 file)

### 5.3 academic-deck v4 (폐기 예정, reference 보관만)
- `submission/_drafts/academic-deck-v4/` — 18 slide JSX + index.html (텍스트 우겨넣은 학술 PDF 톤, 키노트 X)
- claude.ai/design URL: https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2 (폐기)

### 5.4 서버 측정
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/` — 972+ file (138 measurement 추가 진행 중)
- `/mnt/hdd0/home/capstone2026/log/{fillgap_tier1,remaining_seq}_DONE.flag` — 완료 flag (대기 중)

---

## 6. 핵심 사용자 verbatim (본 세션)

| 일시 | verbatim |
|---|---|
| 5/11 22:00 | "와이어프레임 보니까 발표 자료 디자인으로 더 적절. 여러 장점 취합" |
| 5/11 22:39 | "텍스트 겹치고 처음 본 사람들이 이해 못함. 미커버 셀 없이. 서버 자원 체크. 병렬 X 순차. 미커버 없이" |
| 5/11 22:53 | "실험 진짜?" — 100% coverage 거짓 의심 정확 |
| 5/11 22:56 | "이거 며칠째 뭐하는 짓. 모든 cell 커버 못한 method 는 발표 자료 활용 안할 거. 순차적으로 하나씩. 멈춘 거 아냐 이따구로 생각 안하게. 서버 자원 많아" |
| 5/11 23:04 | "이건 진짜 너무 텍스트만 우겨넣고. 키노트 한다고 생각해봐. Wireframes / Animation 자료 템플릿이 더 나았어. 대기업 키노트 본 적 있어?" |

---

## 7. END

작성: 2026-05-11 23:10 KST  
다음 세션: 5/12 morning  
- 측정 회수 (138 measurement, 5-15일 진행 중)
- 키노트 스타일 새 deck 생성 (Wireframes Capstone Design System + 1 slide 1 메시지 + 시각 위주)
- 팀원 공유 자료
- 5/15 박광현 교수 미팅 D-4 / 5/26 finalize 마감 / 5/27 최종 발표 D-16
