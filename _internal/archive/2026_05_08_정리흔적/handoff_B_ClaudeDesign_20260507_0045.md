# [Handoff B] Claude Design 발표/팀원공유 자료 세션 — 2026-05-07 00:45 KST

> **새 세션의 역할**: Claude Design (chrome MCP) 으로 5/27 발표 deck + 팀원 공유용 deck 두 가지 분리 작업.
> **실험/분석** 작업은 **Handoff A** 세션에서 별도 진행 (chrome MCP 충돌 회피).

---

## ★ 30초 진입 명령

```
1. ToolSearch 로 mcp__Claude_in_Chrome 도구 로드
2. tabs_context_mcp 로 현재 chrome tab 확인
3. claude.ai/design tab 확인 → 진행 중인 5/27 deck 상태 screenshot
```

---

## 1. 이전 세션 진행 상태

### 1-1. Claude Design URL
- 메인 작업 design: **속도는벡터 Capstone Design System**
- URL: `https://claude.ai/design/p/019ddd6e-3d8f-750b-be4e-68d97453d486`
- 사용자 chrome 에 이미 접속됨 — chrome MCP 로 control

### 1-2. 기존 Capstone 디자인 5종 (이미 존재)
- `Capstone_High fidelity` (6 days ago)
- `Capstone_Animation` (6 days ago)
- `Capstone_Wireframe` (6 days ago)
- `Capstone_Slide deck` (6 days ago)
- `속도는벡터 Capstone Design System` ★ 메인 작업 (6 days ago, design system + Midterm 12-slide deck)

### 1-3. 본 design system 의 Midterm Slide Deck (이미 완성)
- 12-slide editorial deck — cover, TOC, problem, results, roadmap, closer
- 제목: \"Skew-Aware Stratified Sampling 을 이용한 Vector Cardinality 추정 정확도 개선 연구\"
- 다음 단계 명시: \"최종발표용 데크 분기 (5/27~)\"

### 1-4. 이전 세션에서 발송한 prompt (진행 중)
- 본 design system 의 chat 에 14-slide editorial deck (5/27 발표용) 생성 요청
- 진행 상태: \"Updating design system... Creating S13Future\" — slide 13/14 까지 작성. 곧 완성.
- **사용자 의도와 약간 부합 X**: prompt 가 14-slide *모두 텍스트 포함* 으로 작성됨. 사용자는 \"텍스트 최소화\" 원함.

---

## 2. 사용자의 요청 (이전 세션 마지막 메시지)

### 2-1. 두 가지 deck 분리

**A. 팀원 공유용 deck**:
- 깔끔한 PPT
- 어떤 실험 + 어떤 발견 직관 전달
- 팀원이 텍스트만 으로 다 이해 어려운 부분 보완
- 실험 detail + 발견 narrative 풍부

**B. 5/27 최종 발표용 deck**:
- 중간발표 피드백 반영 (교수님: \"텍스트 너무 많거나 PT만 보고 읽는 느낌\")
- 텍스트 최소화 — **핵심 지표/수치만 huge typography** (대기업 PT 스타일)
- 나머지는 대본/발표로 청중에게 전달
- \"눈에 확 들어오는 정보\" 위주

### 2-2. 디자인 트렌드
- Apple + Figma 느낌
- 세련 + 트렌디
- Claude Design 깔끔 스타일

### 2-3. 활용 가능 양식
- `submission/_drafts/archive/중간발표/templates/` 9 스타일 (academic/bold/editorial/gemini/glass/hub/navy/soft/swiss)
- `~/Research/` 디렉토리

---

## 3. 새 세션 진행 priority

### Priority 1 — 진행 중인 5/27 deck 점검 + 결과 평가

```
1. ToolSearch select:mcp__Claude_in_Chrome__tabs_context_mcp,browser_batch,read_page,computer
2. tabs_context_mcp 호출
3. claude.ai/design 의 tab 으로 navigate (또는 기존 tab 사용)
4. screenshot → 진행 상태 확인
5. \"Updating design system\" 종료 됐으면 결과 deck 검토
```

### Priority 2 — 5/27 deck 텍스트 최소화 follow-up

이전 prompt 의 14-slide 가 텍스트 많음. 추가 prompt 발송:

```
\"방금 만든 deck 의 텍스트를 대폭 줄여줘. 대기업 PT 스타일 (Stripe / Linear / Vercel)
- 각 슬라이드 큰 핵심 수치 1-2 개 huge typography
- 보조 라벨 minimal (10 자 이내)
- 부연 설명은 speaker notes 로 이동
- 시각화 (recharts) 비중 ↑

특히 contribution 슬라이드 (slide 7/8/9):
- Slide 7: \"−0.156\" 또는 \"1.000\" huge → \"Hilbert Curve\" / \"Manhattan Continuity\" 만
- Slide 8: \"1,189×\" huge → \"MiniBatch Speedup\"
- Slide 9: \"+0.7\" huge → \"Negative Control\"

각 slide 의 speaker notes (대본) 도 같이 만들어줘.\"
```

### Priority 3 — 팀원 공유용 deck 별도 분기

이전 design system 의 chat 또는 \"+ New design\" 으로 별도 design 시작:

```
\"팀원 공유용 detailed deck 새로 만들어줘. 5/27 발표용 deck 과 별개.

목적: 팀원이 PPT 만 봐도 W1 sprint 의 모든 실험 + 발견 이해 가능.

스타일: 깔끔한 editorial 느낌 (notion / figma 트렌드). 텍스트 OK 풍부함.

20 slide 분량:
1-2. 인트로 + RQ 구조
3-7. RQ1 진단 (5 cell × 5 seed × 100 query 측정 detail + 단조성 통계)
8-12. RQ2 ablation (5-mode + sample-size sensitivity 40 cell)
13-17. RQ3 16-method (각 method paradigm + 학습 비용 + 결과)
18. Mechanism 분석 (Hilbert vs Z-order, ARI redundancy)
19. Effect size honest (Cohen's d, DEFF, ICC, per-query)
20. 5/27 발표 narrative 합의 사항 + W2 분담

각 slide 좌측 시각화, 우측 텍스트 narrative — 발견의 \"왜\" 도 포함.\"
```

### Priority 4 — 결과 export 후 PPT 변환

Claude Design 의 React artifact → 사용자가 직접:
1. design 페이지에서 \"Export\" 또는 screenshot
2. 또는 React 코드 export → 별도 PowerPoint 변환

또는 본 chrome MCP 로 deck 의 각 slide screenshot → 합본 PDF 생성.

---

## 4. chrome MCP tool 목록 (deferred)

```
mcp__Claude_in_Chrome__tabs_context_mcp
mcp__Claude_in_Chrome__browser_batch
mcp__Claude_in_Chrome__navigate
mcp__Claude_in_Chrome__read_page
mcp__Claude_in_Chrome__find
mcp__Claude_in_Chrome__get_page_text
mcp__Claude_in_Chrome__computer (screenshot/click/type/key/scroll)
mcp__Claude_in_Chrome__list_connected_browsers
mcp__Claude_in_Chrome__tabs_create_mcp
```

각각 deferred 라 ToolSearch 로 로드 필요.

---

## 5. 참고 자료 위치

| 자료 | 경로 |
|------|------|
| 종합 master narrative | `experiments/results/RQ1_RQ2_RQ3_종합_master.md` |
| RQ3 16-method 종합 | `experiments/results/rq3_agnostic/RQ3_16method_종합.md` |
| 5/27 slide outline (text) | `submission/_drafts/속도는벡터_5월27일발표_slide_outline_20260506.md` |
| 5/8 1-page summary | `submission/_drafts/속도는벡터_5월8일회의_1page_summary_20260506.md` |
| 팀원 이해도 doc | `_internal/팀원이해도_RQ_직관설명_20260507.md` |
| HTML prototype (offline standalone) | `submission/_drafts/발표prototype/RQ_interactive_prototype.html` |
| 기존 9 스타일 PPT | `submission/_drafts/archive/중간발표/templates/속도는벡터_중간발표_*.{pdf,pptx}` |

---

## 6. 핵심 결과 (deck 작성용 reference)

```
contribution 3종 (각 한 슬라이드 huge typography):
1. Hilbert Curve 1순위 — \"−0.156\" + \"1.000\" Manhattan
2. MiniBatch — \"1,189×\" speedup + \"1.000\" ARI
3. Negative control — \"+0.7\" Distance-Shell/IS hurt-medium

지표 한 표:
- ρ = -0.680 (RQ1 단조성)
- 40/40 cell KM20 > BERN
- Hilbert DEFF 0.338, ESS 2,325 (SRS 6× 효과)
- Best 빈도: Hilbert 200 > MiniBatch 190 > KM20 172
- Spread vs difficulty 0.78 (어려운 query routing 가치)
```

---

## 7. 진행 시 주의사항

- chrome MCP 의 Cloudflare 통과 X — 사용자가 미리 chrome 에서 claude.ai 에 로그인 되어 있어야
- 진행 중인 chat 에 추가 prompt 보내면 처리 충돌 가능 — 작업 끝날 때까지 wait
- Korean 폰트는 Apple SD Gothic Neo 사용 (matplotlib 도 동일)
- React artifact 를 PPT 로 export 시 design 의 \"Slide deck\" 모드 활용

---

**작성**: 조현빈 · 2026-05-07 00:45 KST
**다음 트리거**: 새 Claude 세션 → `cat _internal/handoff_B_ClaudeDesign_20260507_0045.md`

---

## ★ 새 세션 진입 prompt (복사 붙여넣기 용)

```
@_internal/handoff_B_ClaudeDesign_20260507_0045.md 읽고 Claude Design 작업 이어가자.

[자동 진행]
1. ToolSearch 로 chrome MCP 로드 → claude.ai/design 진행 상태 확인
2. 진행 중인 5/27 deck 완성 됐으면 follow-up:
   - 텍스트 최소화 + 핵심 수치 huge typography (대기업 PT 스타일)
   - 각 contribution slide 핵심 1-2 수치만, 부연 설명 speaker notes
3. 팀원 공유용 별도 deck 분기 (20 slide, detailed, editorial 스타일)
4. 두 deck 의 React artifact → screenshot/PDF/PPT export 가이드

[제약]
- 실험/분석 작업은 Handoff A 세션에서 별도 진행 (서버 PG / 측정 분석)
- 본 세션은 chrome MCP + Claude Design 만, ssh / python 분석 X

참고 자료:
- experiments/results/RQ1_RQ2_RQ3_종합_master.md
- submission/_drafts/속도는벡터_5월27일발표_slide_outline_20260506.md
- submission/_drafts/archive/중간발표/templates/ (9 스타일 reference)
```
