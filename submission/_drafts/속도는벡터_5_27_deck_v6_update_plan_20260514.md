# 5/27 deck v6 update plan — narrative v1 (시나리오 B 확정) 기준

> **base**: v4 keynote deck (5/12 23:07 export, 20 slide) + v3 정정 v2 (5/12 22:50 archive)
> **상위 base**: `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v1.md` (5/14 07:55 + §11 + §12 추가 08:25)
> **작성 시점**: 2026-05-14 10:50 KST · 5/16 (토) claude.ai/design 한도 reset 후 prompt paste 또는 5/16 ~ 5/26 PPTX manual edit 진행

---

## 1. 본 update plan 의 motivation

v4 deck (5/12 23:07) 은 시나리오 B 확정 전 narrative — "12 anchor method 의 일관 −9 ~ −10% 개선" 중심. 본 세션 (5/13 ~ 5/14) 측정 80 건 회수 (multi-join 8 + Centroid tuple 8 + B1/B2/B3 cheap 24 + A2-Fig8 mv 8 + α sweep 16) + 시나리오 B 확정 (단독 대체 best −10.17% > 결합 best −7.37%) + 자원 효율 Pareto + reservoir O(1) finding 으로 narrative 가 크게 update 됐다.

이 plan 은 v4 deck 의 20 slide 위에서 v6 update 항목을 slide 별로 정리한다.

---

## 2. v6 핵심 update 5 영역

### 영역 1 — 시나리오 B 확정 narrative (가장 큰 변화)

**v4 narrative**: 12 anchor method 의 일관 −9 ~ −10% 개선 (단독 vs 결합 분리 X).
**v6 narrative**: 단독 대체 best (−10.17% minibatch_partial) > 결합 best (−7.37% Centroid tuple). 결합으로 단독 능가 불가. 결합의 진짜 가치 = "method 선택 안정성 + 측정 환경별 변동성 감소" (더 큰 정확도 X).

**영향 slide**: S2 (요약) + S3 ~ S4 (도입) + S11 ~ S13 (결과) + S17 ~ S18 (마무리). 거의 모든 narrative slide.

### 영역 2 — 핵심 6 method 깊이 소개 (강재현 5/14 08:10 요청 반영)

**v4**: 12 anchor method list 만 표기, 깊이 소개 X.
**v6**: 핵심 6 method (minibatch_partial / sparse_rp / chao_weighted / hilbert_real / hyperloglog / reservoir) 의 알고리즘 메커니즘 + 이론적 근거 + 실측 결과 1 slide.

**신규 slide**: S12.5 (핵심 6 method 깊이 소개, 2 column layout: 좌 method 이름 + paradigm + 이론 reference / 우 1 줄 메커니즘 + Δ%).

### 영역 3 — 자원 효율 Pareto + reservoir O(1) 산업 적용 (5/13 ~ 5/14 finding)

**v4**: 자원 효율 axis X 또는 약함.
**v6**: 자원 효율 Pareto Top 5 (sparse_rp / chao_weighted / neuram / pca1d / hilbert) = 12 anchor consistency 일치. **reservoir 메모리 O(1) + anchor 수준 정확도 → 모바일 / 임베디드 / 스트리밍 산업 적용 가능**.

**신규 slide**: S15.5 (Pareto Top 5 table + reservoir O(1) callout box).

### 영역 4 — 결합 framework 의 진짜 가치 재정의 (5/14 새벽 finding)

**v4**: 결합 모드 92.5% paired outperform 만 표기.
**v6**: 결합의 진짜 가치 = 더 큰 정확도 X + method 선택 안정성 + cell spread 감소. α=0.5 (산술 평균) best, U-shape sensitivity (양쪽 극단 0.3 / 0.7 효과 감소). cheap 근사 4 후보 측정 = Centroid tuple 만 robust.

**영향 slide**: S14 (결합 framework) + S15 (가중치 sweep + cheap 근사).

### 영역 5 — 폐기 39 method 정직 disclosure 강화 (박세은 12:13 피드백 반영)

**v4**: 폐기 method 11 ~ 12 종 일부만 표기.
**v6**: 폐기 39 method 3 범주 분류 (자원 7 + audit 23 + 정합성 9) 부록 slide 분리. 본문 slide 는 핵심 5 ~ 6 method 만.

**영향 slide**: S10 (portfolio) + 부록 slide 신규.

---

## 3. 20 slide 별 update 항목 (v4 → v6)

| Slide | v4 내용 | v6 update 항목 | priority |
|---|---|---|:---:|
| S1 표지 | 속도는벡터 + Capstone Final 5_27 | 부제 추가 — "분포 인지 표집으로 베르누이 갈아끼우기" | LOW |
| S2 요약 | 4 main finding | **시나리오 B 확정** (단독 best −10.17% > 결합 best −7.37%) + reservoir O(1) 산업 적용 finding 추가 | HIGH |
| S3 도입 1 | Exqutor 위치 | 본 연구 §V-B Adaptive Sampling 영역 한정 명시 + ECQO §V-A 영역은 paper main result 그대로 인정 | LOW |
| S4 도입 2 | skew 영역 부정확 | narrative §1 산문 흐름 그대로 활용 | LOW |
| S5 RQ 구조 | RQ1/RQ2/RQ3 | 변동 X | - |
| S6 RQ1 RQ2 | breakdown | 변동 X (이미 v3 정정 v2 에서 reflected) | - |
| S7 RQ1 detail | cell × sel breakdown | 박세은 옵션 C SYSTEM vs BERN 17.32% (이미 v3 정정 v2) | - |
| S8 RQ2 | paired CI | 변동 X | - |
| S9 RQ3 motivation | 분포 unknown | narrative §2 "56 method × 8 갈래 × 9 측정 환경" 흐름 | LOW |
| S10 portfolio | method matrix | **폐기 39 method 3 범주 정직 분류** (자원 7 + audit 23 + 정합성 9) + 부록 list 분리 (박세은 12:13 피드백) | HIGH |
| S11 paradigm rollup | 8 paradigm bar chart | 변동 X | - |
| S12 단독 대체 (CaseA) | 12 anchor consistency | **단독 best minibatch_partial −10.17%** 강조 + "본 portfolio 단독 best" 명시 | HIGH |
| **S12.5 신규** | - | **핵심 6 method 깊이 소개** (minibatch_partial / sparse_rp / chao_weighted / hilbert_real / hyperloglog / reservoir) 2 column layout | HIGH |
| S13 결합 (CaseB) | 92.5% paired outperform | **결합 best −7.37% Centroid tuple** + "결합 < 단독" 정직 disclosure | HIGH |
| S14 결합 framework | 산술 평균 + 결합 가치 | **결합의 진짜 가치 재정의** — 안정성 + cell spread 감소 (더 큰 정확도 X) | HIGH |
| S15 가중치 sweep + cheap 근사 | (v4 X) | **신규** — α sweep 5 값 (0.3 ~ 0.7) + 산술 평균 α=0.5 best + U-shape + cheap 근사 4 후보 (Centroid tuple 만 robust) | HIGH |
| **S15.5 신규** | - | **자원 효율 Pareto Top 5** + reservoir O(1) 산업 적용 callout | HIGH |
| S16 "왜 replace 만으로는 안 되는가" | v3 정정 v2 기 반영 | **권장 design 통합** — 단독 대체 우선 + 결합 보조 + method-aware (narrative §9) | MEDIUM |
| S17 다중 테이블 | (v4 약함) | **multi-join 시나리오 A.5 (Hybrid) + Centroid tuple cheap 근사** (5/13 ~ 5/14 finding) | MEDIUM |
| S18 마무리 | 4 finding 요약 | **시나리오 B 확정 한 줄 요약** (narrative v1 한 줄 요약 활용) | HIGH |
| S19 한계 + 향후 연구 | 미커버 9 카테고리 | **future work 5 + 5 (Data-aware ensemble + 일반 확장)** + 측정 미커버 9 카테고리 (kde_chain 폐기 추가) | MEDIUM |
| S20 Q&A | - | **예상 질문 list 5 ~ 7** (v3 정정 v2 기 일부) + 시나리오 B 확정 narrative 대비 추가 | MEDIUM |
| 부록 A | (v4 X) | **폐기 39 method 전체 list** 3 범주 분류 slide (자원 7 + audit 23 + 정합성 9) | HIGH |
| 부록 B | (v4 X) | **17 사용 method 부록 table** (paradigm × Δ% × 자원 등급 × 이론 reference, narrative §12) | MEDIUM |

* HIGH = 즉시 정정 / MEDIUM = 5/16 ~ 5/20 진행 / LOW = 5/21 ~ 5/26 finalize.
* 신규 slide 3 (S12.5 핵심 6 method + S15.5 Pareto + S15 가중치 sweep + cheap 근사) → v6 deck 총 20 → 23 slide 추정. 또는 일부 slide 압축으로 20 slide 유지.

---

## 4. 박광현 5/15 미팅 자문 항목과의 연계

박광현 미팅 자문 5 ~ 9 항목 (`submission/_drafts/속도는벡터_5_15_박광현미팅_핵심정리_v1.md` §10) 의 자문 결과가 v6 deck 의 narrative 분기에 영향 가능:

- 자문 항목 1 (paper §V-B narrative 적절성) → S3 도입 1 narrative 분기
- 자문 항목 2 (단독 우선 + 결합 보조 narrative) → S12 ~ S15 + S18 narrative 핵심
- 자문 항목 3 (paradigm vs method-level) → S11 paradigm rollup vs S12 method-level
- 자문 항목 4 (reservoir 산업 적용) → S15.5 Pareto + S18 마무리
- 자문 항목 5 (추가 측정 우선순위) → S19 future work

5/15 미팅 후 자문 결과 반영해서 v6 deck 의 narrative 분기 결정 가능. 따라서 v6 deck finalize 는 **5/16 (토) claude.ai/design 한도 reset 후** 진행이 타이밍 best.

---

## 5. v6 prompt 작성 시 base file 안내

claude.ai/design Keynote_Capstone conversation 에 paste 할 v6 prompt 는 다음 base 위에 작성:

1. **narrative v1** (`속도는벡터_본연구_narrative_최종정리_v1.md`) — §1 ~ §12 전체 흐름이 v6 deck 의 narrative base
2. **박광현 핵심 정리 v1** (`속도는벡터_5_15_박광현미팅_핵심정리_v1.md`) — 자문 항목 + 정직 disclosure 영역
3. **자원 효율 분석** (`_internal/analysis/resource_efficiency_pareto_20260513.md`) — S15.5 Pareto Top 5 table + reservoir O(1) callout
4. **알파 sweep 분석** (`_internal/analysis/alpha_sweep_results_20260514.md`) — S15 가중치 sweep + U-shape
5. **cheap 근사 종합** (`_internal/analysis/cheap_approximation_extended_results_20260514.md`) — S15 cheap 근사 4 후보 + Centroid tuple robust
6. **v3 정정 v2** (`archive/2026_05_12_cleanup/속도는벡터_5_27_키노트_prompt_v3_정정v2_20260512_2250.md`) — slide-level 정정 history 10 건 (S7 / S15 / S16 / S10 / S8/S13 / Limitation / Multi-table / SF=100 / 성능 표현 통일 / storyline 흐름)

위 6 base 의 정보를 종합한 v6 prompt 는 claude.ai/design 에 paste 후 v4 deck → v6 deck 전환 1 turn 진행 가능.

---

## 6. PPTX manual edit option (claude.ai/design 한도 부족 시)

claude.ai/design 한도가 5/16 (토) reset 후 부족하면 PPTX manual edit 으로 진행 가능. archive 의 v4 PPTX (`속도는벡터 · Capstone Final 5_27 (Keynote v4).pptx`) base 위에서 slide 별 manual edit:

1. HIGH priority slide 7 건 (S2 / S10 / S12 / S12.5 / S13 / S14 / S15 / S15.5 / S18 + 부록 A) 우선 edit
2. MEDIUM priority slide 5 건 (S16 / S17 / S19 / S20 / 부록 B) 다음 진행
3. LOW priority slide 3 건 (S1 / S3 / S4 / S9) 마지막 미세 정정

총 manual edit 분량 = 약 15 ~ 20 시간 추정 (1 slide 약 30 min ~ 1 h).

---

작성: 2026-05-14 10:50 KST · v4 deck (5/12 23:07) → v6 deck (5/27 14:00 finalize) update plan
다음 단계: 5/15 박광현 미팅 자문 결과 반영 → 5/16 (토) claude.ai/design 한도 reset 후 v6 prompt paste 또는 PPTX manual edit
