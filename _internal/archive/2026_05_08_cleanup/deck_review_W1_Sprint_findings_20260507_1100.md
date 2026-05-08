# W1 Sprint deck v2 검토 — 5/8 회의 전 강/약점 + 보강 사항

> 2026-05-07 11:00 KST · 본 세션
> **deck URL**: https://claude.ai/design/p/019dfdfa-ba60-7508-856b-42496e1a67f2?file=deck%2FW1_Sprint_Detailed_Deck.html&slide=1
> **폴더**: `deck/W1_Sprint_Detailed_Deck.html`
> **구성**: 22 slide (chart 60% / narrative 40% 균형)
> **종합 평가**: **8.4/10** (검토용 deck 으로 ★)

---

## 강점 5종

### 1. 신규 실험 모두 반영 ✅ (deck_status_v2 line 65-76 검증)

| 항목 | 위치 | 상태 |
|---|---|---|
| 22 method 측정 | Slide 13/14/19 | ✅ |
| HDBSCAN 4강 진입 (SIFT s=0.10 -3.99%) | Slide 17 (NEW) | ✅ |
| Hybrid 4강 진입 (직교성 검증) | Slide 18 (NEW) | ✅ |
| 8M sensitivity 16 method | Slide 20 | ✅ |
| 8M mid-sel 비단조 (DEEP_8M 증 0/감 2) | Slide 20 (NEW) | ✅ |
| SIFT-KM20 ρ=-0.140 5-cell | Slide 5 (UPDATE) | ✅ |
| PQ / Sobol / IS Negative | Slide 13 family 분류 | ✅ |

### 2. 정보 밀도 ★ (chart 60% / narrative 40%)
- 검토용 deck 으로 적정 분량 (5/8 회의 전 팀원 자가 검토)
- 박세은(팀장) / 강재현 / 조현빈 / 이동욱 4명 분담표 slide 22 명시

### 3. 수치 master 1:1 일치 (10/10)
- 모든 핵심 수치 RQ1_RQ2_RQ3_종합_master.md / RQ1_RQ2 실험 결과 정리.md 와 대조 완료
- W1 Sprint 보강 작업 (W1-A ~ W1-E, 정리.md line 597-683) 모두 반영

### 4. SIFT mid-sel 신규 narrative 명시
- 정리.md line 614-621 의 SIFT 5-cell 패턴 (s=0.10 -8.85%, s=0.30 -7.26% mid-sel 가장 강 KM20) 반영
- 5/27 발표에서 SIFT-specific 결과로 강조 가능한 narrative 출구

### 5. 가독성 ★ (8/10)
- 흰 + 빨간 breadcrumb — 챕터 navigation 명확
- 좌 60% chart / 우 40% narrative 분리 — 검토 시 chart 와 해석 동시 보기 가능

---

## 약점 3종 + 5/8 회의 전 보강

### 약점 1: Speaker notes 없음 (검토용 → 5/8 회의 발표용 부적합)
- W1 Sprint deck 은 팀원 자가 검토용으로 설계 (deck_status_v2 line 73)
- 5/8 19:00 비대면 회의에서 강재현/박세은 발표 시 별도 대본 또는 화면 공유 + 구두 설명 필요
- **보강 권장**: 5/8 회의 30분 전, 핵심 슬라이드 (5, 13-20) 의 발표자 talking points 1-2 줄씩 별도 정리

### 약점 2: 22 slide 분량 — 5/8 회의 시간 제약
- 5/8 19:00 비대면 회의 분량 (보통 1-1.5시간) 에 22 slide 전부 detail 보기 어려움
- **보강 권장**: 회의 진행 시 3 단계로 분리
  - Stage 1 (15분): Slide 1-12 — RQ 구조 + 기존 결과 review
  - Stage 2 (20분): Slide 13-21 — 22 method + 4강 신규 (HDBSCAN/Hybrid) + 8M 비단조
  - Stage 3 (10분): Slide 22 — W2 분담 합의 + 자문 메일 초안 합의

### 약점 3: 5/7 03:23 이후 신규 결과 (final_chain / phase2) 미반영 가능성
- master.md line 47-48: final_chain (8 method) + phase2 (4 method) ETA 10:00~11:00 KST
- 본 검토 시점 (11:00 KST) 에 결과 도착 여부 불확실
- **보강 권장**:
  - (a) 결과 도착 + 4강 변동 → W1 Sprint deck slide 13/19/20 즉시 update
  - (b) 결과 도착 + 4강 변동 없음 → 5/8 회의 중 구두 공유 ("phase2/final_chain 결과 도착, 4강 변동 없음 confirm")
  - (c) 결과 도착 안 함 → 5/8 회의 중 status 보고 + 후속 검토

---

## 5/8 회의 전 액션 (사용자 결정 + 본 세션 가능 작업)

### 사용자 결정 필요
- **Q1**: W1 Sprint URL 카톡 단톡방 공유 시점 — (a) 지금 11시 / (b) 저녁 (final_chain 결과 통합 후)
- **Q2**: Speaker talking points 보강 — 본 세션에서 별도 작성 / 강재현 본인 작성

### 본 세션 작업 가능 (사용자 confirm 후)
1. final_chain / phase2 결과 도착 시 → W1 Sprint slide 13/19/20 update follow-up prompt 작성
2. 5/8 회의 talking points 1-2 줄씩 작성 (slide 5, 13, 17, 18, 20, 21, 22 핵심 7개)
3. 카톡 단톡방 공유 메시지 작성 (deck URL + 검토 요청 메시지)

---

## 산출물 위치 매핑

| 자료 | 위치 |
|---|---|
| W1 Sprint deck v2 (22 slide) | https://claude.ai/design/p/019dfdfa-ba60-7508-856b-42496e1a67f2 |
| 5/8 회의 1-page summary | submission/_drafts/속도는벡터_5월8일회의_1page_summary_20260506.md |
| 5/27 slide outline | submission/_drafts/속도는벡터_5월27일발표_slide_outline_20260506.md |
| 자문 메일 초안 (2종) | submission/_drafts/속도는벡터_자문메일초안_*.md |
| RQ1+RQ2+RQ3 종합 master | experiments/results/RQ1_RQ2_RQ3_종합_master.md |
| W1 Sprint 보강 정리 | experiments/results/RQ1_RQ2 실험 결과 정리.md (W1-A~E section) |
| 8 figures (한글 폰트) | experiments/figures/rq3_supplementary/ |

---

**작성**: Claude (본 세션) · 2026-05-07 11:00 KST
**다음 액션**: 사용자 결정 (Q1 카톡 공유 시점 / Q2 talking points 작성 위임 여부)
