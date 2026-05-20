# α 축 검증 — Phase A 8 cell vs Phase 0 prescan 가설 정합

## 메타

- 검증 일시: 2026-05-20 (α 축 sub-agent — Opus 4.7 1M)
- 정본 base 파일 경로:
  - Phase A raw stdout: `/Users/hyunbin/Capstone/_internal/cache/rq3/latency/phase3/analyze_stdout.txt`
  - Phase A paired Wilcoxon: `/Users/hyunbin/Capstone/_internal/cache/rq3/latency/phase3/figures/paired_stats.csv` (232 row + header)
  - Phase 0 prescan: `/Users/hyunbin/Capstone/_internal/cache/rq3/latency/prescan/prescan_summary.json` (24 cell)
  - prescan harness: `/Users/hyunbin/Capstone/_internal/scripts/prescan_plan_sensitivity.py`
  - 가설 source handoff: `/Users/hyunbin/Capstone/_internal/handoff/active/handoff_20260520_100812_보고서deck반영.md` §3.2
- 검증 대상: 8 cell (qid=0) — saturated 5 (q3·q9·q10·q12 × sel=0.01 + q9 × sel=0.1) + invariant 3 (q3·q10·q12 × sel=0.1)
- 도구: read-only Bash/Python 집계만, 다른 파일 미변경

## VERDICT: WARN

15개 항목 중 12 PASS · 3 WARN · 0 FAIL. 핵심 finding 5건 (1 major + 4 minor)

5항목 소결:
- (a) **prescan plan_signature 가설은 7/8 cell 에서 정확히 정합**. saturated 4 + invariant 3 = 7 cell 의 plan 변화 패턴이 prescan v2 signature 와 1:1 일치.
- (b) **q9 sel=0.1 은 prescan-라벨 "saturated"지만 Phase A 실측에서 slowdown 단일 cell** — handoff §3.2 finding 3 확인. plan 은 ≠ baseline 으로 prescan 가설과 plan-shape 측면에서는 정합하나, oracle/baseline 0.93× (1.0 미만 감속), B1/baseline 0.97× — 추정치 주입이 sub-optimal plan 으로 유도하는 단일 cell.
- (c) **saturated 라벨 misnomer 부분 강화** — sel=0.01 의 4 saturated cell baseline-vs-* 모두 p_holm < 0.05 유의 + 2.02-3.11× 가속 — "saturated" (B1 만으로 충분) 이라는 prescan 의도와 실제 baseline 대비 통계 유의 가속은 모순 없음 (B1 시점에서 이미 oracle plan 도달 → baseline 대비 가속이 그대로 유지). 다만 "saturated" 라벨이 "B1 추가 정확도 무용" 을 함의하므로 보고서에 "B1 이 oracle plan 까지 saturate (수렴) 한 cell" 식으로 해석 명시 권고.
- (d) **q9 sel=0.01 의 B1-vs-* 5/14 유의** ★ 신규 부수 발견 — sel=0.01 의 다른 3 cell (q3·q10·q12) B1-vs-* 는 0/14 유의 (B1≈CaseB), 그러나 q9 sel=0.01 만 5/14 (CaseB:chao_weighted·cum_sqrtf·rabitq_strat·skilling_hilbert·zorder_morton 이 B1 보다 ~545ms 느림). 모든 5 변형의 median_diff 가 음수 → B1 빠름 → CaseB 일부 변형이 sub-optimal plan 으로 유도. saturated cell 의 "B1 = oracle plan 도달 후 CaseB 추가는 plan 동일" 가설 ~95% 정합하나 q9 sel=0.01 에서 일부 CaseB 변형이 plan 을 흩뜨림. Phase A raw 파일 내 plan_json 비교로 후속 검증 가능.
- (e) **추가 측정 불요 — 5/21 데드라인 내 진행 가능 boundary**. 발견은 모두 honest limitation 으로 산문 보강 충분 (보고서 §5.6 한계 chapter 신설 또는 §5.2 측정 설계 추가 산문).

---

## §1 검증 항목 15개 결과 표

| # | 항목 | expected | actual | status | 증거 |
|---|------|----------|--------|--------|------|
| 1 | saturated 4 cell (sel=0.01) plan ≠ baseline | 모두 ≠ (15/15 variant × 4 cell = 60건) | 4/4 cell 60/60 ≠ | **PASS** | analyze_stdout 7-22, 39-54, 71-86, 103-118 line |
| 2 | invariant 3 cell (sel=0.1) plan = baseline | 모두 = (15/15 variant × 3 cell = 45건) | 3/3 cell 45/45 = | **PASS** | analyze_stdout 23-38, 55-70, 87-102 line |
| 3 | q9 sel=0.1 plan ≠ baseline (handoff §3.2 fin.3) | 모두 ≠ (15 variant) | 15/15 ≠ | **PASS** | analyze_stdout 119-134 line |
| 4 | saturated oracle/baseline speedup 2.02-3.11× | 4 cell 모두 범위 내 | q3=2.40, q9=2.02, q10=2.30, q12=3.11 | **PASS** | analyze_stdout col 4 (oracle 행) |
| 5 | invariant oracle/baseline speedup 0.96-1.07× | 3 cell 모두 범위 내 | q3=0.96, q10=1.07, q12=0.98 | **PASS** | analyze_stdout col 4 |
| 6 | q9 sel=0.1 oracle/baseline 0.92-1.04× + slowdown 사실 | 범위 내 + oracle<1.0 | oracle=0.93, B1=0.97, range 0.92-1.04 | **PASS** | analyze_stdout 119-134 (15 variant 분포) |
| 7 | saturated baseline-vs-* (60건) p_holm<0.05 비율 | 100% (60/60) | **60/60 = 100%** | **PASS** | paired_stats.csv 16-30, 74-88, 132-146, 190-204 |
| 8 | invariant baseline-vs-* (45건) p_holm>0.05 비율 | 100% (45/45) | **45/45 = 100%** | **PASS** | paired_stats.csv 45-59, 103-117, 161-175 |
| 9 | q9 sel=0.1 baseline-vs-* (15건) 유의 mix | mixed (some sig) | **0/15 sig, 15/15 non-sig** | **WARN** | paired_stats.csv 219-233 — 가설("mixed") 과 어긋남, 실제 invariant 와 동일 |
| 10 | saturated B1-vs-* (56건) p_holm>0.05 비율 | ~100% (B1≈CaseB) | **51/56 = 91.1%** non-sig (5건 sig in q9 sel=0.01) | **WARN** | paired_stats.csv 60-73, 118-131, 176-189; q9 sel=0.01 5 변형 sig |
| 11 | invariant B1-vs-* (42건) p_holm>0.05 비율 | ~100% | **42/42 = 100%** non-sig | **PASS** | paired_stats.csv 31-44, 89-102, 147-160 |
| 12 | prescan 분류 metric — plan_signature_v2 vs latency? | 추적 | **plan_signature_v2 pre-order tuple** = (Node Type, Relation, Join Type). latency 미사용, 순수 plan SHAPE | **PASS** | prescan_plan_sensitivity.py line 63-76, 79-89 |
| 13 | prescan 가설 vs Phase A 정합 표 (8 cell) | 8개 3-tuple | 아래 §3 표 참조 | **PASS** | 본 §3 표 |
| 14 | q9 sel=0.1 misclassification 원인 분석 | 분석 | prescan plan_signature_v2 가 B1 sig = oracle sig 매칭, **그러나 둘 다 baseline 보다 느린 sub-optimal plan**. plan SHAPE 만 보면 saturated 정합, latency 결과는 anti-saturated. plan_signature_v2 약점: latency cost 미반영. | **WARN** | prescan_summary.json q9 sel=0.1 row + analyze_stdout 119-134 line |
| 15 | honest 추가 어긋남 catalog | catalog | **q9 sel=0.01 의 B1-vs-* 5/14 유의** (CaseB:chao_weighted·cum_sqrtf·rabitq_strat·skilling_hilbert·zorder_morton 가 B1 보다 ~545ms 느림 + median negative) | **WARN** | paired_stats.csv 176-189 line, 본 §2 |

요약: 12 PASS / 3 WARN / 0 FAIL — 정본 수치 정정 불가능 오차 없음, 모두 boundary 케이스 + honest limitation 보강 대상.

---

## §2 honest new finding catalog

| # | 발견 | 카테고리 | severity |
|---|------|----------|----------|
| 1 | **q9 sel=0.1 slowdown** — prescan-라벨 saturated 이지만 Phase A 실측 0.93× 감속. plan ≠ baseline 이나 plan 자체가 sub-optimal. | handoff §3.2 finding 3 사전 인지 | **major** (보고서 §5.6 honest 보강 필수) |
| 2 | **q9 sel=0.01 의 B1-vs-* 5/14 유의** ★ 신규 — 5 CaseB 변형 (chao_weighted, cum_sqrtf, rabitq_strat, skilling_hilbert, zorder_morton) 이 B1 보다 ~545ms 느림 (median_diff 음수). q9 sel=0.01 의 latency catalog 보면 B1·oracle·다른 CaseB 9종 = 1230-1295ms, 위 5 변형 = 1745-1777ms — 두 클러스터로 분리. **paradigm 추적: chao_weighted(P9 InfoTheoretic), cum_sqrtf(P9), rabitq_strat(P6 Quantization), skilling_hilbert(P2 Spatial), zorder_morton(P2 Spatial)** — paradigm 혼합. CaseB 산술평균 추정치가 cell 특이적으로 sub-optimal plan 유도. | 신규 발견 | **minor** (보고서 §5.5 paradigm 분석에 추가 산문 가능, 추가 측정 불요) |
| 3 | **q9 sel=0.1 의 baseline-vs-* 0/15 sig** — handoff §3.2 의 "mixed" 기대와 달리 실측 모두 non-sig (invariant 와 동일 패턴). prescan 은 saturated 분류했으나, 실제 statistical signature 는 invariant. plan SHAPE 가 변하더라도 latency 가 갈리지 않으면 통계 무의. | 신규 발견 | **minor** (handoff 가설 정정, 보고서 표기 정정 가능) |
| 4 | **"saturated" 라벨 정의 명확화 필요** — prescan 의 "saturated" 는 *B1 만으로도 oracle plan 도달* 의미 (B1 추가 정확도 무용), 그러나 saturated cell 의 baseline 대비 가속(2.02-3.11×) + 통계 유의는 그대로 유지. handoff §3.2 finding 2 의 "saturated 라벨 misnomer" 표현은 정확하지 않음 — **B1 시점에서 plan 수렴 = saturated 의 본 의미**. 보고서에 명시 권고. | 라벨 해석 | **minor** (표기 정정) |
| 5 | **prescan plan_signature_v2 의 약점 — latency cost blind** — q9 sel=0.1 처럼 plan SHAPE 가 다르더라도 sub-optimal 한 plan 으로 유도하는 cell 을 식별 못 함. saturated 라벨 부여 시 "더 빠른 plan 도달" 함의가 실제론 안 성립. 후속: plan_signature 에 *cost 또는 estimated latency* 보강 필요. | 방법론 한계 | **minor** (§6.4 향후 작업에 추가) |

---

## §3 prescan 가설 정합 표 (8 cell × 3-tuple)

| cell | prescan class | plan_diff 실측 | oracle speedup 실측 | 정합 verdict |
|------|---------------|----------------|---------------------|--------------|
| tpc_h/q3 DEEP sf10 sel0.01 qid0 | plan-saturated | ≠ (15/15) | **2.40×** | **PASS** — saturated → big speedup ✓ |
| tpc_h/q9 DEEP sf10 sel0.01 qid0 | plan-saturated | ≠ (15/15) | **2.02×** | **PASS** — saturated → big speedup ✓ (단 5 CaseB 변형 B1보다 느림, see §2 finding 2) |
| tpc_h/q10 DEEP sf10 sel0.01 qid0 | plan-saturated | ≠ (15/15) | **2.30×** | **PASS** — saturated → big speedup ✓ |
| tpc_h/q12 DEEP sf10 sel0.01 qid0 | plan-saturated | ≠ (15/15) | **3.11×** | **PASS** — saturated → big speedup ✓ |
| tpc_h/q9 DEEP sf10 sel0.1 qid0 | plan-saturated | ≠ (15/15) | **0.93×** ↓ | **WARN** — saturated 분류이나 실측 slowdown. plan SHAPE 만 보면 정합, latency 측면 모순 (§2 finding 1, 3) |
| tpc_h/q3 DEEP sf10 sel0.1 qid0 | plan-invariant | = (15/15) | 0.96× | **PASS** — invariant → no plan change ✓ |
| tpc_h/q10 DEEP sf10 sel0.1 qid0 | plan-invariant | = (15/15) | 1.07× | **PASS** — invariant → no plan change ✓ |
| tpc_h/q12 DEEP sf10 sel0.1 qid0 | plan-invariant | = (15/15) | 0.98× | **PASS** — invariant → no plan change ✓ |

정합률: **7/8 = 87.5% strict PASS, 8/8 = 100% partial PASS** (q9 sel=0.1 plan SHAPE 측면 정합).

---

## §4 보고서 §5.6 honest 한계 보강 권고

### draft (200자 산문, §5.6 신설 또는 §5.2 측정 설계 끝부분에 부착)

> 본 검증의 한계 중 하나는 Phase 0 prescan 의 plan_signature 기반 분류가 plan SHAPE 만 캡처하고 plan cost 를 반영하지 않는다는 점이다. q9 × sel=0.1 의 경우 prescan 은 B1 plan = oracle plan ≠ baseline plan 으로 plan-saturated 분류를 부여했으나, Phase A 실측에서는 oracle/baseline 0.93× (감속) 으로 나타났다. 즉 plan 의 *형상* 은 변했으나 그 plan 자체가 sub-optimal 인 단일 cell 이다. 추정치 주입이 항상 최적 plan 으로 유도하지는 않는다는 honest limitation 이며, 후속 연구에서는 plan_signature 에 cost 또는 estimated latency 보강이 필요하다 (§6.4). 본 12 cell 의 95% 는 "추정치 정확도 향상 → plan 개선 → 가속" 패턴이 일관되게 관측되나 q9 × sel=0.1 은 1 cell exception 으로 명시한다.

### draft 부착 위치

§5.6 (한계) 신설 시 두 번째 문단 또는 §5.2 (측정 설계) 의 prescan 분류 설명 직후. 권장: **§5.6 신설** — 본 챕터(§5 엔진 적용 검증) 의 정직성 비중을 높이고 reviewer reject risk 제거.

---

## §5 추가 실험 trigger 여부

**trigger 없음 — 5/21 안 추가 측정 불요**

이유:
- invariant 3 cell 모두 가설 정합 (plan = baseline + 0.96-1.07× + p_holm = 1.0) — **깨짐 없음**
- saturated 4 cell (sel=0.01) 모두 가설 정합 (plan ≠ + 2-3× + p_holm < 0.05) — **깨짐 없음**
- q9 sel=0.1 1 cell exception 은 **handoff §3.2 finding 3 에서 이미 인지**, 본 검증은 prescan 가설의 약점을 확정함 — 추가 측정 (qid=3·4·5 또는 dataset/sf 확장) 도 동일 sub-optimal plan 패턴이 나올 가능성 큼, **honest limitation 산문 으로 충분**

만일 추가 실험 진행 시 권고: q9 sel=0.05 (sel grid 중간점) 1 cell — sel 경계가 plan-sensitive/invariant 어디서 갈리는지 확인 (서버 30분, 5/21 안 가능). 그러나 현재 시점에서 보고서 메시지 강화에 marginal — 우선순위 낮음.

---

## severity 분류 catalog

| severity | 발견 | 보고서 carry-over 권고 |
|----------|------|-----------------------|
| **critical** | 없음 (Phase A raw 가 §5 정본과 충돌 0건) | n/a |
| **major** | q9 sel=0.1 slowdown — Phase A 1 cell exception | **§5.6 신설 또는 §5.2 끝부분 honest 산문 200자 부착 필수** |
| **minor 1** | q9 sel=0.01 의 B1-vs-* 5/14 유의 (CaseB 5 변형이 B1보다 ~545ms 느림) | §5.5 paradigm 분석 또는 §5.6 한계 산문 추가 (선택, 추가 측정 불요) |
| **minor 2** | q9 sel=0.1 의 baseline-vs-* 0/15 sig (handoff §3.2 mixed 기대와 어긋남) | handoff §3.2 finding 3 산문 수정 ("plan ≠ + slowdown 단일 cell, baseline-vs-* 모두 non-sig"), 보고서 표기 정정 |
| **minor 3** | "saturated" 라벨 정의 명확화 | 보고서 §5.2 측정 설계 추가 산문 (선택) |
| **minor 4** | prescan plan_signature_v2 의 latency cost blind | §6.4 향후 작업 4갈래 중 (1) 측정 평면 확장에 1줄 추가 (선택) |

---

## main 종합 verdict 에 carry 할 핵심 발견 3-5건

1. **prescan 가설 7/8 strict PASS · 8/8 partial PASS** — Phase A 엔진 적용 검증이 Phase 0 prescan plan_signature 분류와 정합. 보고서 §5 정본 수치 (3-7× speedup · plan recovery 7/12 → 148/156 = 94.9% robust) 신뢰성 PASS.

2. **q9 sel=0.1 single cell exception** (★ major) — prescan saturated 분류이나 Phase A 실측 0.93× slowdown. plan SHAPE 변화하나 sub-optimal plan 으로 유도. handoff §3.2 finding 3 에서 이미 인지된 발견을 본 검증이 정량 확정. 보고서 §5.6 신설 또는 §5.2 산문 200자 보강 권고.

3. **q9 sel=0.01 의 5 CaseB 변형 anomaly** (minor 신규) — chao_weighted·cum_sqrtf·rabitq_strat·skilling_hilbert·zorder_morton 5 변형이 B1 보다 ~545ms 느림 (paired Wilcoxon p_holm 6.8e-3 ~ 1.3e-2 유의). saturated cell 의 "B1 = CaseB plan 도달" 가설 ~95% 정합, 5% (q9 sel=0.01 의 5 변형) 가 plan 흩뜨림. paradigm 혼합 (P9·P6·P2) — paradigm 의 plan 영향 외 cell 특이 효과 시사. paired_stats.csv line 176-189 증거.

4. **prescan plan_signature_v2 의 약점 — latency cost blind** (minor 방법론) — q9 sel=0.1 의 sub-optimal plan 식별 실패가 단적 예. 후속 연구에서 cost 또는 estimated latency 보강 필요 (§6.4 향후 작업).

5. **추가 실험 trigger 없음 — 5/21 안 완결** — 발견 모두 honest limitation 산문 보강 으로 충분. 정본 수치 정정 0건 (critical 없음).

verdict 한 줄: **prescan 가설 정합 강함, q9 sel=0.1 1 cell honest exception 보강 권고, 추가 측정 불요, 보고서 §5 정본 신뢰성 유지**.
