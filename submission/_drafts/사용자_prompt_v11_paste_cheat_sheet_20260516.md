# 사용자 prompt v11 paste cheat sheet (5/16)

claude.ai/design Keynote_Capstone 영역에서 deck v11 generate 위해 3 part paste 절차.

## § 1. paste 순서

1. **Part 1** — `속도는벡터_5_27_키노트_prompt_v11_part1_framing_20260516_0050.md` (framing layer)
2. **Part 2** — `속도는벡터_5_27_키노트_prompt_v11_part2_slide1_15_20260516_0050.md` (slide 1-15)
3. **Part 3** — `속도는벡터_5_27_키노트_prompt_v11_part3_slide16_25_20260516_0050.md` (slide 16-25)

## § 2. paste 시 주의사항

- 각 Part paste 후 **응답 full reply generate 완료까지 대기** (도중 중단 X)
- 응답 완료 후 다음 Part paste — 직전 응답 wait 안 하면 context 누락
- Part 간 간격 message 추가 X (cold context 유지)

## § 3. claude.ai/design Keynote_Capstone 시작

- **새 message** 로 cold start (이전 deck v10 thread 이어가기 X)
- Keynote_Capstone project 영역 진입 후 첫 message = Part 1

## § 4. v10 → v11 핵심 변경 4건

1. **main theme**: "Distribution-aware Sample Selection for VAQ Cardinality Estimation" (cardinality 추정 → sample selection 전환)
2. **framing layer 분리**: slide 3 NEW (문제 framing 명시)
3. **slide 5**: Phase 1+2 우리 영역 자세히 + Phase 3 minimal
4. **slide 18**: Q-error → paired Δ% 92.5% 거대 수치

## § 5. deck v11 generate 후 검증 항목 (10)

- [ ] main theme = "Distribution-aware Sample Selection for VAQ Cardinality Estimation"
- [ ] cardinality 추정 표현 모두 제거 (sample selection 일관)
- [ ] framing layer 분리 slide 3 NEW
- [ ] slide 5 Phase 1+2 우리 영역 자세히 + Phase 3 minimal
- [ ] slide 8-15 paradigm 별 method 알고리즘 자세히
- [ ] slide 18 paired Δ% 92.5% 거대 수치
- [ ] footer 표기 X (모든 slide)
- [ ] 25 slide 정확
- [ ] speaker notes 영역 sample selection 일관
- [ ] Pareto Top 5 ★ 표시

## § 6. 다음 단계

deck v11 generate 완료 → 사용자가 본 세션에 알림 → 검증 항목 10건 자동 검사 + 피드백.
