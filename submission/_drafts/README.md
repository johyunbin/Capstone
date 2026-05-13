# 속도는벡터 · 발표 / 보고 자료 안내 (5/14 07:25 finalize)

> **5/15 박광현 교수 미팅 + 5/27 캡스톤 최종 발표 + 5/28 임채림 박사 SAP 미팅 + 6/11 최종 보고서 용**  
> **팀**: 박세은(팀장) · 강재현 · 조현빈 · 이동욱  
> 연세대학교 2026-1 학기 · 박광현 교수님 지도 (BDAI 연구실)

---

## ★ 현재 최신 자료 (5/14 07:25 4차 정정 + PDF 4종)

본 연구의 5/13 ~ 5/14 측정 결과 (multi-join + Centroid tuple + cheap 근사 4 후보 + α sweep + A2-Fig8) 와 박세은 5/14 12:13 피드백 (method 개수 줄임 + 숫자 최소화) 까지 모두 반영된 4 종 자료. **시나리오 B 확정 (단독 대체 narrative + 결합 robustness 강화) + reservoir O(1) 산업 적용 finding** 포함.

### 처음 보시는 분 — 다음 순서로 읽으세요

#### 1 단계 — 팀원 빠른 공유 (5분)

📄 **`속도는벡터_팀원_상황공유_v1.pdf`** (233 line, 598KB)

팀원 (박세은 / 강재현 / 이동욱) 대상 peer-to-peer 톤 빠른 공유 자료. 본 연구 핵심 결과 + 시나리오 B 확정 + 자원 효율 + 산업 적용 3 영역 종합.

#### 2 단계 — 5/15 박광현 교수 미팅 자료 (D-1)

📄 **`속도는벡터_5_15_박광현미팅_핵심정리_v1.pdf`** (293 line, 633KB)

박광현 교수님 미팅 사전 보고용. 측정 portfolio + 단독 대체 가능 method + 결합 framework + 자원 효율 + 교수님 자문 항목 5 가지. 5/15 14:00 미팅 D-1 시점 finalize.

박광현 5/15 미팅 자료 영역 (이전 작성, 5/13 16:30 finalize): 
- `박광현_5월15일_미팅/` 디렉토리 안 5 file (slide_draft 895KB / 간결 1page 455KB / 2page 요약 / 예상질문 답변 / 5_27 update plan)

#### 3 단계 — 5/27 최종 발표 storyline (10분)

📄 **`속도는벡터_5_27_최종발표_storyline_v1.pdf`** (280 line, 626KB)

5/27 캡스톤 최종 발표 storyline. 7 단계 narrative 흐름 (문제 정의 → 56 탐색·폐기 → 단독 대체 → 결합 framework → 자원 효율 → 권장 design → 마무리) + Q&A 5건 예상 답변 + 발표 시간 배분 (15분 기준).

#### 4 단계 — 6/11 최종 보고서 outline (20분)

📄 **`속도는벡터_6_11_최종보고서_outline_v1.pdf`** (389 line, 733KB)

6/11 최종 보고서 작성용 outline. 중간 보고서 12 page → 최종 30 page 확장 전략 + 7 장 구조 + 부록 8 종 (가중치 sweep / cheap 근사 / Pareto / 산업 적용 / 폐기 list 등).

---

## archive — 이전 작성 자료 (참고용)

`archive/` 디렉토리 안에는 5/12 이전 작성된 자료들이 보존되어 있습니다. 본 5/14 신규 4 file 이 시나리오 B 확정 + 박세은 피드백 반영으로 더 정확하므로, 5/15 박광현 미팅 + 6/11 보고서 작성 시에는 신규 4 file 을 base 로 진행하고 archive 는 reference 로 활용.

- `archive/속도는벡터 · Capstone Final 5_27 (Keynote v4).{pdf,pptx,html}` — 5/12 23:07 export, 20 slide v4 (시나리오 B 확정 이전 narrative)
- `archive/속도는벡터 — 한 페이지 요약.{md,pdf}` — 5/11 작성 1page
- `archive/속도는벡터 — 팀원 종합 가이드.{md,pdf}` — 5/11 작성 종합 가이드
- `archive/속도는벡터 — 발표 storyline 가이드.{md,pdf}` — 5/11 작성 storyline
- `archive/속도는벡터 — 자주 묻는 질문.{md,pdf}` — 5/11 작성 Q&A 12 건
- `archive/2026_05_12_cleanup/` — 5/12 ~ 5/13 정정 prompt v3 / v4 / v5 + 정정 history

---

## 자료의 분리 이유

5/14 07:25 finalize 시점에 두 axis 의 자료를 분리 보관:

| 영역 | 자료 |
|---|---|
| **5/14 신규 4 file (★ 최신)** | 팀원 공유 + 박광현 미팅 + 5/27 storyline + 6/11 보고서 outline |
| archive 5/12 작성 자료 | 한 페이지 요약 + 팀원 종합 가이드 + 발표 storyline + 자주 묻는 질문 + Capstone Final v4 |
| `박광현_5월15일_미팅/` | 박광현 미팅 자료 5 file (slide_draft + 1page + 2page + 예상질문 + update plan) |

신규 4 file 이 본 연구의 5/13 ~ 5/14 측정 결과 + 시나리오 B 확정 + 박세은 피드백 반영의 가장 최신 form 이며, 박광현 5/15 미팅 + 5/27 발표 + 6/11 보고서 작성의 base 입니다. archive 자료는 narrative 흐름의 history 참고용으로 보존.

---

작성: 2026-05-14 07:25 KST · 4차 정정 + PDF 4종 finalize 시점
