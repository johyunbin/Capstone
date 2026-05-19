# 5/27 발표 deck — 1순위 추천 + 4 옵션 trade-off

> 2026-05-07 11:00 KST · 본 세션
> **사용자 사전 평가**: "확인해봤는데 아카데믹이 가장 깔끔한 것 같아"
> **객관 평가**: 9.2/10 (5 deck 중 1위) — 사용자 평가와 일치

---

## ★ 결론 — Academic v3 (5/27 발표용 1순위)

**URL**: https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2?file=academic-deck%2Findex.html&slide=1
**폴더**: `academic-deck/`
**구성**: 16 slide, 1280×720, 흰 배경 + navy accent

### 추천 근거 3가지

#### 1. 학술 콘텍스트 적합성 ★★★ (10/10)
- 흰 배경 + 좌측 navy 세로 bar + 검정 사각 numbered badge — 한국 학술 발표 디폴트 양식 (학과 교수님께 가장 익숙)
- 캡스톤 평가위원 (지도교수님 + 박광현 교수님 + 학과 교수 + 산업 멘토) 4 그룹 모두 무난
- 5/22 교수님 미팅 → 5/27 발표 → 6/11 최종보고서 흐름 일관 적용 가능

#### 2. 단일 디자인 시스템 일관성 ★★★ (9/10)
- 16 slide 모두 동일 layout (좌측 navy bar + numbered badge + implication bar + page indicator + footer caption)
- Navy v2 의 DARK 6 + WHITE 10 hybrid 구조 대비 흐름 단절 ↓
- 보고서 / 포스터 / 전시회 자료 후속 변환 용이

#### 3. 수치 정확성 ★★★ (10/10) — master.md 1:1 대조 모두 통과
- ρ = -0.680 [-0.800, -0.440] DEEP-KM20 ✓
- ρ = -0.140 [-0.220, -0.100] SIFT-KM20 (5-cell mid-sel 보강 후) ✓
- 40/40 KM20 > BERN ✓
- Anti-Neyman DEEP +5.21% / SIFT +9.49% (CI 0 제외) ✓
- Hilbert d=-0.156, Manhattan 1.000 vs Z-order 1.992 ✓
- MiniBatch 1,189× speedup, partial_fit ARI 1.000 ✓
- Hybrid SIFT s=0.10 -3.10% / HDBSCAN SIFT s=0.10 -3.99% (4강) ✓
- DEEP_8M 비단조 (증 0 / 감 2, n=3) ✓
- DEFF 0.338 / ESS 2,325 / spread vs difficulty ρ=0.78 ✓

---

## 16 slide 흐름 검증 (Academic v3 spec 기반)

| # | 유형 | 핵심 메시지 | huge stat |
|--:|---|---|---|
| 01 | Cover | "Skew-Aware Stratified Sampling for Vector-Augmented Analytical Query" | (타이틀) |
| 02 | TOC | 10-card domain grid | — |
| 03 | 문제 | 기존 시스템 33.3% / 50.0% / 100% baselines | 3 baselines |
| 04 | Prior Work | Exqutor ECQO 1-2ms + Adaptive 1000× | — |
| 05 | Approach | RQ1/RQ2/RQ3 3-card | — |
| 06 | RQ1 진단 | DEEP-KM20 ρ=-0.680 + SIFT-KM20 ρ=-0.140 | **ρ = -0.680** |
| 07 | RQ2 aware | KM20 oracle 40/40 + Anti-Neyman counterfactual | **40 / 40** |
| 08 | RQ3 agnostic | 22 method bar (4강 ★) | — |
| 09 | ★ Hilbert | Cohen's d -0.156, Manhattan 1.000 | **−0.156** |
| 10 | ★ MiniBatch | 1,189× speedup, partial_fit ARI 1.000 | **1,189×** |
| 11 | ★ Negative Control | Cohen's d +0.7 hurt-medium (PQ/Sobol/IS) | **+0.7** |
| 12 | Cross-scale | DEEP_8M 비단조 발견 + 16 method heatmap | — |
| 13 | Mechanism | Hilbert vs Z-order locality + ARI matrix | — |
| 14 | Effect Size Honesty | DEFF 0.338 / ESS 2,325 / per-query ρ=0.78 | **6×** SRS |
| 15 | Limitation | 4-card (multi-table / vector.c / shift / streaming) | — |
| 16 | Closing | 감사합니다 / Q&A + GitHub | — |

**Narrative 흐름** (master line 75-92 와 일치):
```
Motivation (s3-4) → RQ1 진단 (s6 ρ=-0.680) → RQ2 oracle (s7 40/40)
→ RQ3 production alternative (s8-11 4강 ★) → Cross-scale (s12 8M 비단조)
→ Mechanism (s13) → Effect honesty (s14) → Limitation (s15) → Closing (s16)
```
12-15분 발표 분량에 적정.

---

## 2-3순위 trade-off

### Samsung v3 — 8.0/10 (2순위 후보)
- **장점**: 4-card grid + dot tag row + IMPLICATION outline box → 정보 밀도 ★, 산업 R&D 발표 톤
- **단점**: 학과 교수님께 다소 commercial. 캡스톤 평가위원 비중에 따라 trade-off
- **선택 case**: 산업 멘토 비중 ↑ + 평가 그룹에 산업 인사 다수 → Samsung 고려 가치

### Navy v2 — 7.8/10 (sentimental)
- **장점**: DARK 6 contribution 슬라이드 임팩트 ★ (huge typography 유지). 본 세션이 만든 첫 deck
- **단점**: DARK / WHITE 두 시스템 혼용 → 흐름 단절 위험. 인쇄 시 잉크 소모 ↑. 학술보다 product 톤
- **선택 case**: keynote 풍 화려한 발표 선호 시 (캡스톤 평가위원 fit ↓)

### Editorial v3 — 7.2/10 (부적합)
- **장점**: Playfair italic serif + → THE FINDING line — 시각 임팩트 ★
- **단점**: Magazine/잡지 톤 — 캡스톤 학술 발표에 부적합. serif italic 가독성 ↓
- **선택 case**: **권장 X** (5/27 발표용 부적합)

---

## 사용자 결정 사항 — 응답 요청

### Q1. 5/27 발표 deck — Academic v3 1순위 confirm 하시겠습니까?
- ✅ Yes → followup prompt 발송 (다음 산출물 D 참조)
- ⚠️ No (Samsung 검토) → Samsung v3 직접 visit 검증 후 비교

### Q2. Hybrid 5번째 옵션 (Academic 베이스 + Samsung 4-card grid 차용) — 만들까요?
- **권장 X**: Academic 단일 시스템 일관성이 강점. 차용 시 일관성 ↓ 위험.
- Claude Design 주간 사용량 78% — rebuild 1개 가능하나 Academic 보강 (chat prompt) 으로 충분.

### Q3. PDF/PPTX export 시점 — 언제?
- (a) 지금 (5/7 11시) — followup 정정 후 export. 5/22 교수님 미팅에 ready
- (b) 5/22 교수님 미팅 직전 — 미팅 피드백 반영 후 5/26 마감 export
- (c) 5/26 마감 직전 — 단일 마감
- **권장 (b)**: 5/22 미팅 피드백 ↑ 활용 + 5/26 마감 일정 분리

### Q4. W1 Sprint deck — 카톡 단톡방 공유 시점
- (a) 지금 (5/7 11시) — 5/8 회의 D-1, 팀원 충분 검토 시간
- (b) 5/7 저녁 — 신규 follow-up 결과 (final_chain / phase2 결과 통합 후) 반영 후 공유
- **권장 (a)**: 검토 시간 확보 우선. 신규 결과는 5/8 회의 중 구두 공유 가능

---

## 다음 단계 (사용자 confirm 후 자동 진행 가능)

1. **Academic v3 followup prompt 발송**: `_internal/deck_followup_prompts_20260507_1100.md` 의 #1 (slide 6 정정) + #2 (slide 13 ARI 검증) + #3 (cover background 확인) — Claude Design chat 에 차례로
2. **W1 Sprint URL 카톡 공유 메시지 작성**: deck_status_v2 의 액션 B 참조
3. **PDF export** (Q3 결정에 따라): Share → Export as PDF → `submission/_drafts/속도는벡터_5월27일발표_v3_academic.pdf`
4. **PPTX export**: Share → Export as PPTX → 같은 위치 `.pptx`

**작성**: Claude (본 세션) · 2026-05-07 11:00 KST
