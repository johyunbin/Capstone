# Academic v3 deck — Follow-up Prompts (Claude Design chat)

> 2026-05-07 11:00 KST · 본 세션
> **deck URL**: https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2?file=academic-deck%2Findex.html&slide=1
> **사용량 제약**: Claude Design 주간 78% — chat prompt 무제한 OK, 새 deck rebuild 1개만 가능
> **사용 방식**: 사용자가 위 URL 접속 → 우상단 chat 입력란에 prompt 복사 붙여넣기 → 차례로 발송

---

## 우선순위 1 (필수, 5/8 회의 전 발송)

### Prompt #1 — Slide 6 "6 selectivity bins" 정정

```
slide 6 의 stat box 캡션에 "n=5 seeds × 6 selectivity bins" 라고 적혀있는데, 실제 측정은 5 selectivity bins (50%, 30%, 10%, 5%, 1%) 입니다. "6" → "5" 로 정정해주세요.

캡션 정확한 표현은:
"95% bootstrap CI [-0.800, -0.440] · DEEP-KM20 · n=5 seeds × 5 selectivity bins · 0 not in CI"

근거: experiments/results/RQ1_RQ2_RQ3_종합_master.md line 56, RQ1_RQ2 실험 결과 정리.md line 290-303 (5sel × 3 dataset gradient 표).
```

### Prompt #2 — Slide 13 ARI matrix 값 검증 요청

```
slide 13 의 ARI matrix 4 offline methods (Hilbert / KM20 / MiniBatch / HDBSCAN) 값들이 정확한지 검증해주세요. 현재 spec 에 1.00 / 0.74 / 0.73 / 0.62 등 값이 명시되어 있는데, 출처 파일은 experiments/results/rq3_agnostic/rq3_method_redundancy_ari.md 입니다.

검증 후 정확한 값으로 update 부탁드립니다. 만약 ARI matrix 가 4-method 가 아닌 다른 method 조합으로 측정되어 있다면, 가장 의미있는 4-method (4강 = Hilbert / MiniBatch / Hybrid / HDBSCAN) 로 재구성 권장.
```

### Prompt #3 — Cover slide background 흰색 유지 확인

```
slide 1 (Cover) 의 background 가 spec 에 "전체 흰 #FFFFFF (다크 슬라이드 없음)" 라고 적혀있는데, preview 화면에서 검정 배경으로 보이는 가능성이 있습니다.

확인해주시고:
- 의도된 검정 배경이라면 → spec ("다크 슬라이드 없음") 와 모순. WHITE 배경 + navy 타이틀로 재조정 권장.
- 단순 preview 로딩 이슈라면 → 그대로 두되 PDF export 시 WHITE 가 정상 출력되는지 확인.

Academic 디자인 시스템의 일관성 (16 slide 모두 WHITE) 유지가 중요합니다.
```

---

## 우선순위 2 (선택, 시간 여유 시)

### Prompt #4 — Slide 8 22-method bar 가독성 보강

```
slide 8 의 22-method effect size bar 에서 4강 ★ (Hilbert / MiniBatch / Hybrid / HDBSCAN) 의 color-coded category 를 더 명시적으로 강조해주세요.

현재 spec: "color-coded by category: learning-free / learned offline / online weight / oracle / negative / baseline"

보강:
- 4강 ★ 4 bar 에 outline 또는 ★ marker 추가 (다른 18 method 와 시각적 분리)
- legend 에 category 별 색상 + ★ = "paired CI 0 제외 4강" 명시
- bar 높이 기존 대비 1.3-1.5× 확대 (가독성 ↑)
```

### Prompt #5 — Slide 12 8M 비단조 narrative 강조

```
slide 12 (Cross-scale) 의 "DEEP_8M ✗ 비단조 (증 0 / 감 2, n=3)" 발견을 narrative 측면에서 더 강조해주세요.

현재 implication bar: "ranking 은 일관, gradient 패턴은 규모에 따라 미묘"

보강안:
"1M 의 단조성 결론이 8M 으로 자동 이전되지 않음 — sample_size=385 한계 + Q-error 자체가 6-8× 로 신호 < 잡음 영역. ★ honest limitation 으로 발표 강조."

이 honest limitation 명시가 캡스톤 평가위원에게 신뢰성 ↑ 효과. 5/27 발표에서 강재현 발표자가 "limitation 도 정량적으로 관측" narrative 가능.
```

---

## 우선순위 3 (선택, 학술 콘텍스트 보강)

### Prompt #6 — Speaker notes 톤 점검

```
16 slide 의 speaker notes 한국어 대본을 빠르게 검토해주세요. 검토 포인트:
1. 슬라이드당 30-45초 분량 적정한가
2. 한국어 자연스러움 (일본어식 직역 / 영어식 어순 없는지)
3. 핵심 수치 (ρ -0.680, 1,189×, -0.156 등) 의 한국어 발음 자연스러움
4. 발표자 (강재현 주발표) 가 외울 수 있는 분량인가
5. 박세은 / 조현빈 / 이동욱 분담 시 톤 일관성

문제 지점 1-2개 만 알려주시면 그 부분만 수정합니다.
```

### Prompt #7 — Limitation slide (15) 4-card 분류 검증

```
slide 15 Limitation 의 4-card grid:
- L1 Multi-table
- L2 vector.c integration
- L3 Distribution shift
- L4 Online streaming

이 4 분류가 master.md line 27-32 의 4 limitation:
1. 단일 테이블 (multi-table future work)
2. KM20 oracle (production 학습 부담, partial_fit + Hilbert 가 replacement)
3. Effect size practical small (Hilbert d=-0.156)
4. vector.c Python 시뮬레이션 (memory leak)

과 매핑이 일치하는지 검증해주세요. 만약 #3 effect size 가 빠져있고 #4 가 두 번 들어있다면 정정 권장.
```

---

## 발송 순서 권장

```
지금 (5/7 11:00 KST) → Prompt #1 발송 (slide 6 정정, 1분)
                   → Prompt #2 발송 (slide 13 ARI 검증, 5-10분 응답)
                   → Prompt #3 발송 (cover background 확인, 1-2분)

5/7 14:00 ~ 18:00 → Prompt #4 / #5 (선택, 시간 여유 시)

5/8 회의 (19:00) 직전 → Prompt #6 / #7 (선택, 학술 콘텍스트 보강)
```

---

## 사용량 알림

- Claude Design 주간 78% — 토 오전 1:00 KST 리셋 (5/9 (토) 01:00)
- 5/7 ~ 5/9 사이 chat prompt 는 무제한 OK
- 새 deck rebuild 는 토 리셋 후 (5/9 (토) 01:00 이후) 가능
- 즉 5/27 발표 전 하나의 새 deck 가능 시점: 5/9 (토) 01:00 ~ 5/16 사용량 한계 도달 전

---

**작성**: Claude (본 세션) · 2026-05-07 11:00 KST
