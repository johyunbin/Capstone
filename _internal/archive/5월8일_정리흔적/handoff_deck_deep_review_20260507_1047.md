# [Handoff] Deck Deep/Ultra Review — 4 옵션 5/27 + W1 Sprint 팀원 공유용 종합 심사

> **새 세션 역할**: 본 세션이 만든 5개 deck (5/27 final 4 스타일 + W1 Sprint 1 버전) 에 대해 **딥리뷰 / 울트라리뷰** 진행.
> **금지**: 사용량 78% 도달 — Claude Design 새 deck 생성은 **최대 1개** 까지만 (Hybrid 미세조정 같은 경우). 나머지는 chat 으로 follow-up 만.
> **목표**: 사용자에게 정확하고 깊은 평가 보고 → 5/27 발표 deck 1개 결정 + W1 Sprint deck 보완 사항 확인.

---

## ★ 30초 진입 명령

```
1. ToolSearch 로 chrome MCP 로드 (mcp__Claude_in_Chrome__*)
2. tabs_context_mcp → 현재 chrome tab 확인 (5개 design tab 떠있어야 함)
3. master.md 읽기: experiments/results/RQ1_RQ2_RQ3_종합_master.md
4. RQ1_RQ2 실험 결과 정리.md 의 8M mid-sel 표 (line 290-303) 읽기
5. 새 todo: 5 deck × 6 차원 (디자인/수치/슬라이드 무게/speaker notes/접근성/일관성) 매트릭스 평가
```

---

## 1. 현재 상태 — 5 deck 모두 share-ready

### 1-1. 5/27 발표용 4 옵션 (16 slide each)

| # | 스타일 | URL | 폴더 | 디자인 한 줄 |
|---|---|---|---|---|
| **1** | **navy v2 (기존 hybrid)** | [link](https://claude.ai/design/p/019ddd6e-3d8f-750b-be4e-68d97453d486?file=final-deck%2Findex.html&slide=1) | `final-deck/` | DARK 6 (cover/TOC/Hilbert/MiniBatch/Negative/Closing) + WHITE 10 (body) |
| **2** | **Academic v3** | [link](https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2?file=academic-deck%2Findex.html&slide=1) | `academic-deck/` | 흰 + 좌측 navy bar + 검정 숫자 박스 (01-16) + navy implication 바 |
| **3** | **Editorial v3** | [link](https://claude.ai/design/p/019e000b-b89a-7d25-95eb-2dab34c77989?file=editorial-deck%2Findex.html&slide=1) | `editorial-deck/` | 흰 + 좌측 빨간 bar + Playfair italic serif + → THE FINDING line |
| **4** | **Samsung Research v3** | [link](https://claude.ai/design/p/019e0010-8186-75e4-b834-720fdab38632?file=samsung-deck%2Findex.html&slide=1) | `samsung-deck/` | 흰 + 상단 파란 stripe + dot tag row + 4-card grid + IMPLICATION outline box |

### 1-2. W1 Sprint 팀원 공유용 (22 slide)

| URL | 폴더 | 한 줄 |
|---|---|---|
| [link](https://claude.ai/design/p/019dfdfa-ba60-7508-856b-42496e1a67f2?file=deck%2FW1_Sprint_Detailed_Deck.html&slide=1) | `deck/W1_Sprint_Detailed_Deck.html` | 흰 + 빨간 breadcrumb + 좌 60% chart / 우 40% 해석/의미/제약 narrative |

W1 Sprint v2 가 5/7 03:23 이후 신규 실험 (HDBSCAN/Hybrid/8M-mid) 모두 반영함. 단 이후 추가 follow-up 안 됨.

### 1-3. 프로토타입 (참고용)

| URL | 폴더 | 한 줄 |
|---|---|---|
| [link](https://claude.ai/design/p/019dffa7-1b0d-7273-9e66-99bdea00edc4?file=3-style-prototype.html&slide=1) | `3-style-prototype.html` | 12 slide = 4 × 3 styles (Academic 1-4, Editorial 5-8, Samsung 9-12) — 이미 참조용 |

---

## 2. 실험 데이터 정확성 체크리스트 (master.md 출처)

새 세션은 각 deck 의 모든 수치를 master.md 에 대조. **수치 틀림이 있다면 follow-up prompt 로 정정 요청** (Claude Design chat 에서).

### 2-1. RQ1 — Selectivity Gradient 단조성

| 데이터셋 | metric | 값 | 95% CI | 출처 line |
|---|---|---|---|---|
| DEEP-KM20 (1M) | per-seed Spearman ρ | **−0.680** | [-0.800, -0.440] | master.md line 9, 정리.md line 600+ |
| DEEP-RAND (1M) | per-seed Spearman ρ | **+0.560** | [+0.320, +0.840] | master.md line 56 |
| SIFT-KM20 (1.5M, 5-cell) | per-seed Spearman ρ | **−0.140** | [-0.220, -0.100] | 정리.md line 600+ (5/7 mid-sel 추가 후) |

**중요 SIFT 5-cell 패턴** (정리.md line 600~640):
| sel | KM20 mean diff% | 비고 |
|-----|---|---|
| 0.01 | −0.53% | tie |
| 0.05 | +4.39% | |
| **0.10** | **−8.85%** | ★ mid-sel 강 |
| **0.30** | **−7.26%** | ★ mid-sel 강 |
| 0.50 | +3.07% | |

### 2-2. RQ2 — KM20 Oracle + Anti-Neyman

| metric | 값 | 출처 |
|---|---|---|
| 40 / 40 cells KM20 > BERN | ✓ 100% 일관 | master.md line 11, line 59 |
| Anti-Neyman DEEP s=0.01 (vs Prop) | **+5.21%** [+1.36, +9.16] CI 0 제외 | master.md line 60 |
| Anti-Neyman SIFT s=0.01 (vs Prop) | **+9.49%** [+4.66, +11.75] CI 0 제외 | master.md line 61 |

### 2-3. RQ3 — 22-method (4강 + Negative)

| method | 값 | 출처 |
|---|---|---|
| **Hilbert (avg)** | Cohen's d **−0.156** [-0.336, -0.041] | master.md line 62 |
| Hilbert vs Z-order (synthetic) | inverse Manhattan **1.000** vs **1.992** | master.md line 63 |
| **MiniBatch K-means** (N=1M) | **1,189×** speedup | master.md line 22 |
| MiniBatch partial vs full | ARI **1.000** | master.md line 64 |
| **Hybrid** (MiniBatch+Hilbert) SIFT s=0.10 | **−3.10%** [-4.61, -1.19] | master.md line 13 |
| **HDBSCAN** SIFT s=0.10 | **−3.99%** [-5.34, -2.12] (mid-sel 가장 강) | master.md line 13 |
| **Negative** PQ / Sobol / IS | 모두 CI 0 제외 hurt direction | master.md line 13 |
| IS p200_clip avg | Cohen's d **+0.704** medium hurt | master.md line 66 |
| spread vs difficulty (Q4_hard) | Spearman ρ **+0.78** | master.md line 65 |

### 2-4. 8M Cross-Scale (5/7 03:23 신규)

3 데이터셋 × 5 selectivity gap 표 (정리.md line 290-303):

| sel | DEEP 1M (KM gap) | SIFT 1.5M (KM gap) | DEEP 8M (KM gap) |
|-----|---|---|---|
| 50% | +1.64% (gap −0.6%) | +3.07% (gap +2.1%) | +1.76% (gap +0.7%) |
| 30% | +2.62% (gap +2.4%) | — | +1.60% |
| 10% | +4.19% (gap +2.5%) | — | −0.41% |
| 5% | +1.85% (gap +1.1%) | +4.39% (gap +4.4%) | +0.55% (gap +0.4%) |
| 1% | +8.93% (gap +19.6%) | −0.53% (gap +11.6%) | −0.71% (gap −11.8%) |

**단조성 판정** (정리.md line 300-303):
- DEEP_1M: ~ 부분 단조 (반례 1건) (n=5)
- SIFT_1.5M: ✓ 엄격 단조 ↑ (n=3 → 5 with mid-sel)
- **DEEP_8M: ✗ 비단조** (증 0 / 감 2) (n=3) **★ 핵심 신규 발견**

### 2-5. Effect Size Honesty

| metric | 값 | 출처 |
|---|---|---|
| Hilbert DEFF | **0.338** | master.md line 24 (5/8 1-page summary) |
| Hilbert ESS | **2,325** (= SRS 의 6×) | 동상 |
| KM20 DEFF | 0.281 | rq3_bootstrap_effect_size.md |

---

## 3. 딥리뷰 / 울트라리뷰 — 6 차원 매트릭스

새 세션은 5 deck × 6 차원 = **30 평가 셀** 매트릭스를 작성. 각 셀은 (점수 0-10 + 코멘트 + 권장 follow-up).

### 차원 1: 디자인 미학 (Aesthetic Quality)
- 시각적 임팩트 / 일관성 / 한국 학술 발표 fit / Apple 풍 / 트렌디 정도
- Cover slide 첫인상 / contribution slide 임팩트 / closing slide 마무리감

### 차원 2: 수치 정확성 (Data Accuracy)
- 모든 수치를 master.md 와 1:1 대조
- 수치 틀림 / CI 빠짐 / 단위 부정확 / 출처 미명시
- **체크리스트** (각 deck 마다):
  - [ ] ρ = -0.680 [-0.800, -0.440] DEEP-KM20 정확
  - [ ] ρ = -0.140 [-0.220, -0.100] SIFT-KM20 (있으면) 정확
  - [ ] 40/40 KM20>BERN 정확
  - [ ] Anti-Neyman +5.21% / +9.49% 정확
  - [ ] Hilbert -0.156 [-0.336, -0.041] 정확
  - [ ] MiniBatch 1,189× + ARI 1.000 정확
  - [ ] Hybrid -3.10% [-4.61, -1.19] (있으면) 정확
  - [ ] HDBSCAN -3.99% [-5.34, -2.12] (있으면) 정확
  - [ ] DEEP_8M 비단조 ✗ (있으면) 정확
  - [ ] DEFF 0.338 / ESS 2,325 (있으면) 정확
  - [ ] spread vs difficulty ρ=0.78 (있으면) 정확

### 차원 3: 슬라이드 무게감 (Slide Weight Balance)
- 각 슬라이드 정보 밀도 적절한가
- 너무 비어있는 / 너무 과밀한 슬라이드는?
- contribution slide 가 강조되었는가
- transition / setup slide 가 너무 길지 않은가
- 12-15분 발표 분량으로 적절한가

### 차원 4: Speaker Notes 품질 (For 5/27 deck only — W1 Sprint 는 speaker notes 없음)
- 슬라이드당 30-45초 분량 적절한가
- 한국어 자연스러운가
- 핵심 메시지 명확한가
- 제약/한계 honestly 다루는가
- 발표자 (강재현 주발표) 가 외울만한 양인가

### 차원 5: 접근성 / 가독성 (Accessibility / Readability)
- 텍스트 크기 (13px-15px body, 24-32px h2) 적절
- 색상 대비 충분 (WCAG AA 이상)
- 차트 라벨 가독성
- 한국어/영어 폰트 mix 일관성
- 화면 / 인쇄 / 모바일 모두 가능?

### 차원 6: 학술 콘텍스트 적합성 (Academic Context Fit)
- 캡스톤 평가위원 (학과 교수, 산업 멘토) 에게 적합한가
- 박세은(팀장) / 강재현(주발표) / 조현빈 / 이동욱 분담 톤에 맞는가
- 5/8 회의 → 5/22 교수님 미팅 → 5/27 발표 흐름에 맞는가
- 보고서 / 포스터 / 전시회 자료로 후속 변환 용이한가

---

## 4. 평가 산출물 (새 세션 작성)

새 세션은 다음 4 산출물을 작성:

### A. `_internal/deck_review_matrix_20260507_XXXX.md`
5 deck × 6 차원 매트릭스 (점수 + 코멘트 + 권장)

### B. `_internal/deck_review_5_27_winner_20260507_XXXX.md`
5/27 발표 deck 4 옵션 비교 + 1순위 추천 + 2-3 follow-up 사항

### C. `_internal/deck_review_W1_Sprint_findings_20260507_XXXX.md`
W1 Sprint deck 단일 옵션의 강/약점 + 5/8 회의 전 보강할 것 (있다면)

### D. (선택) `_internal/deck_followup_prompts_20260507_XXXX.md`
필요한 follow-up 미세조정 prompt 모음 (각 deck 의 chat 에 보낼 수 있는 형식)

---

## 5. 검증 방법

### 5-1. URL 직접 접속
각 URL 접속 → 우상단 **Present** → **In this tab** → Home 키 → 화살표로 16/22 슬라이드 모두 확인

### 5-2. 슬라이드 직접 navigation (URL 파라미터)
```
?file=academic-deck%2Findex.html&slide=1
?file=academic-deck%2Findex.html&slide=2
...
?file=academic-deck%2Findex.html&slide=16
```
각 slide=1~16 (5/27 deck) 또는 slide=1~22 (W1 Sprint) 로 변경

### 5-3. Speaker notes 확인
Present 모드 들어가지 않아도 페이지 하단 "SPEAKER NOTES Slide X / 16" 부분에 한국어 대본 표시

### 5-4. master.md 대조
```bash
grep -n "수치값" /Users/hyunbin/Capstone/experiments/results/RQ1_RQ2_RQ3_종합_master.md
grep -n "DEEP_8M" "/Users/hyunbin/Capstone/experiments/results/RQ1_RQ2 실험 결과 정리.md"
```

---

## 6. 후속 follow-up 권장 (사용량 제약 고려)

Claude Design 주간 사용량 78% 도달 — 토 오전 1:00 리셋 (KST). 그 전까지:

### 가능한 follow-up
- 각 deck chat 에 미세 조정 prompt (예: "slide 8 의 22-method bar 가 너무 작아서 가독성 떨어짐 — bar 높이 1.5배")
- 수치 정정 prompt (예: "slide 6 의 ρ 값이 -0.68 인데 -0.680 으로 정정")
- speaker notes 보강 (예: "slide 11 negative control 대본 좀 더 자세히")

### 제약 작업
- 새 deck 전체 rebuild — 사용량 큰 작업, 1개만 가능 (Hybrid 같은 5번째 옵션 작업 시)
- 절대 안 됨: 5 deck 전체 재작 (사용량 한계 초과)

---

## 7. 컨텍스트 (master.md 외 참조 자료)

### 핵심 자료
- `experiments/results/RQ1_RQ2_RQ3_종합_master.md` — 핵심 수치 종합
- `experiments/results/RQ1_RQ2 실험 결과 정리.md` — 8M mid-sel 비단조 자세
- `submission/_drafts/속도는벡터_5월27일발표_slide_outline_20260506.md` — 발표 outline
- `submission/_drafts/속도는벡터_5월8일회의_1page_summary_20260506.md` — 1-page 종합
- `_internal/deck_status_v2_20260507_0830.md` — 본 세션 navy v2 상태 보고서

### 디자인 참조
- `submission/_drafts/archive/중간발표/templates/속도는벡터_중간발표_navy.pdf` — Navy 템플릿 (이미 검토 — Academic 의 영감)
- `submission/_drafts/archive/중간발표/templates/속도는벡터_중간발표_academic.pdf` — Academic 템플릿
- `submission/_drafts/archive/중간발표/templates/속도는벡터_중간발표_editorial.pdf` — Editorial 템플릿
- `submission/_drafts/archive/중간발표/templates/속도는벡터_중간발표_soft.pdf` — Soft 템플릿
- `/Users/hyunbin/Research/ETC/Portfolio_HyunInJo_Final.pdf` — 조현인 (가족) Samsung Research 포트폴리오 (Samsung 스타일 영감)

### 본 세션 산출 보고서
- `_internal/deck_status_final_20260507_0200.md` — 1차 (navy v1) 보고서
- `_internal/deck_status_v2_20260507_0830.md` — 2차 (navy v2 + W1 v2) 보고서
- 본 문서 — 핸드오프

---

## 8. 사용자 결정 사항 (새 세션 사용자에게 질의)

새 세션은 평가 후 사용자에게:

1. **5/27 발표 deck 4 옵션 중 1개 선택**
   - 1순위 추천 명확히
   - 2-3순위 와의 trade-off 설명
2. **W1 Sprint deck 보강 사항** (있다면)
3. **Hybrid 5번째 옵션 만들지 여부** (사용량 1개 남은 상태)
   - 예: Academic 베이스 + Samsung 의 4-card grid 차용
4. **PDF/PPTX export 시점** — 5/22 교수님 미팅 전 / 5/26 마감 전
5. **W1 Sprint 팀 공유 시점** — 5/8 19:00 회의 전 카톡 link 공유

---

## 9. 일정 (5/8 회의 D-1)

| 마감 | 작업 | 상태 |
|---|---|---|
| 5/7 (오늘) | 5/27 deck 1개 결정 + W1 Sprint 보강 | ⏳ 진행 중 |
| 5/8 19:00 | 비대면 회의 (전원) | ⬜ |
| ~5/15 | 자문 메일 발송 | ⬜ |
| ~5/21 | 발표자료 초안 마감 | ⬜ |
| 5/22 | 교수님 미팅 | ⬜ |
| 5/26 | 발표자료 최종 마감 | ⬜ |
| **5/27** | **★ 최종 발표 (D-20)** | ⬜ |

---

## ★ 새 세션 진입 prompt (복사 붙여넣기용)

```
@_internal/handoff_deck_deep_review_20260507_1047.md 읽고 5 deck 딥리뷰 작업 이어가자.

[자동 진행]
1. ToolSearch 로 chrome MCP 로드 + tabs_context_mcp
2. master.md + 정리.md 읽기 (수치 체크리스트 확보)
3. 5 deck × 6 차원 매트릭스 작성 (Academic / Editorial / Samsung / navy v2 / W1 Sprint × 디자인/수치/무게/SN/접근성/콘텍스트)
4. 각 deck 의 모든 슬라이드 Present 모드로 직접 검증
5. 산출물 4종 작성 (matrix / winner / W1 findings / followup prompts)
6. 1순위 추천 + 사용자 결정 요청

[제약]
- Claude Design 주간 사용량 78% — 새 deck rebuild 1개만 가능 (있어야 한다면)
- chat follow-up prompt 는 무제한 OK
- 사용량은 토 오전 1:00 리셋

참고:
- experiments/results/RQ1_RQ2_RQ3_종합_master.md
- experiments/results/RQ1_RQ2 실험 결과 정리.md (8M mid-sel)
- _internal/deck_status_v2_20260507_0830.md
```

---

**작성**: Claude (본 세션) · 2026-05-07 10:47 KST
**다음 트리거**: 새 Claude 세션 → `cat _internal/handoff_deck_deep_review_20260507_1047.md`
**예상 작업 시간**: 1-2시간 (5 deck × 16~22 slide × 6 차원 = ~500 평가 포인트)
