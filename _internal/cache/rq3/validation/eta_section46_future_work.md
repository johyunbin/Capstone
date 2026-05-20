# η 축 검증 — §4 정본 수치 / §4.7·§5.6 honest 한계 / §6.4 향후 작업 (Phase A carry)

_생성_: 2026-05-20 12:30 KST · sub-agent η · read-only verification

**기준 파일** (read-only):
- 보고서 정본: `/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.md` (line 199-510)
- v13 수치 정본: `/Users/hyunbin/Capstone/_internal/cache/rq3/v13_summary.md`
- v13 종합 보고서: `/Users/hyunbin/Capstone/experiments/results/raw/REPORT_분석/REPORT_paper_exact_v13.md`
- Phase A latency 결과: `/Users/hyunbin/Capstone/_internal/cache/rq3/latency/phase3/analyze_stdout.txt` (8 cell × 16 variant × 15 rep)

---

## VERDICT: **WARN**

- §1·§2·§3 정본 수치·한계 모두 PASS (v13 정본·5축 multi-axis fix 완전 반영).
- §4 §6.4 (1) 갈래는 Phase A 측정 결과 (saturated/invariant 패턴 + q9 sel=0.1 새 발견)를 **추상적 "향후 작업"으로만 기술**하고 측정 데이터를 carry 하지 않음 — **major issue 1건**.
- §4 §6.4 나머지 3 갈래는 PASS.

---

## §1. §4 정본 수치 정합 (5 항목)

| # | 항목 | 보고서 §4 | v13 정본 | 정합 |
|---|---|---|---|:---:|
| 1 | **89.1%** (CaseB vs B1 better) | line 41·205·209·226·231·406·485·493 (총 7곳) | `v13_summary.md` §3 line 34: `CaseB_vs_B1: 1344/1508 = 89.1%` | ✓ |
| 2 | **−4.38%** (CaseB vs B1 median Δ%) | line 41·211·226·493 (총 4곳) | `v13_summary.md` §3 line 34: `median Δ% −4.38%` | ✓ |
| 3a | **−3.06%** (mean Δ%, 이상치 포함) | line 210·226·493 (총 3곳) | `v13_summary.md` §3 line 34: `mean Δ% -3.06%` | ✓ |
| 3b | **−4.09%** (mean Δ%, 이상치 제외) | line 210·215·320·493 (총 4곳) | `v13_summary.md` §3 line 37: `outlier 제외 mean -4.09%` | ✓ |
| 4 | method **13 강한 / 3 클러스터링 제외** (gmm·minibatch_partial·faiss_ivf) | line 256·258·322·471·473·483 (총 6곳) | `v13_summary.md` §4.4 line 82-84 + §4.5 line 95 | ✓ |
| 5 | **portfolio 1,508 = 1,508 trio × 3 mode = 4,524 row** | line 41·175·195·201·205·306·318·493·521·533·542·547 (총 12곳) | `v13_summary.md` §1 line 6: `1508건 (각 측정 = B1·CaseA·CaseB matched). row 4524 = 1508×3` | ✓ |

추가 검증 — **CaseA 음성 대조군 수치** (line 225·229·485·493): `35.2%` · `+12.90%` · `+1.09%` — 모두 v13 정본 line 33 일치.

추가 검증 — **K granularity** (line 290-298): K=10 better 83.6% / K=20 89.8% / K=30 85.9% — v13 정본 line 130-132 일치.

추가 검증 — **selectivity sweep** (line 270-274): sel=0.001 83.3% / sel=0.01 87.6% / sel=0.10 97.5% — v13 정본 line 45-47 일치.

추가 검증 — **method × cell top 8 winner** (line 260): A1-SSN hilbert_real −13.60%·A2-Fig9 skilling_hilbert −13.45%·... — v13 정본 §8.1 line 172-179 일치.

**§1 verdict**: **PASS** — 정본 수치 5개 + 추가 cross-check 4종 모두 v13 일치.

---

## §2. §4.7 honest 한계 (6 항목, 5축 multi-axis fix 반영 포함)

§4.7는 line 316-332 (17 줄, 6 sub-paragraph).

| # | 한계 | 보고서 §4.7 위치 | 5축 fix 반영 여부 | 정합 |
|---|---|---|---|:---:|
| 6 | **다중 벡터 측정 극단 이상치 2건** (A10-DEEP+WIKI-concat-sf10 minibatch_partial +1043.19% / +510.62%) | line 320 (첫째 한계) | v13_summary §8.2 line 184-185 일치 — 1단계 정본 carry | ✓ |
| 7 | **P1 Cluster paradigm 비일관성** (gmm·minibatch_partial·faiss_ivf) | line 322 (둘째 한계) | v13 정본 §4.5 line 95 P1=+9.34% paradigm carry | ✓ |
| 8 | **concat sf=100 부분 미측정** (DEEP+SIFT만 sf=100, DEEP+WIKI·DEEP+YFCC 미측정) | line 324 (셋째 한계) | v13 정본 portfolio §1 line 8 sf=100 512건 = DEEP/SIFT/SSN single + DEEP+SIFT concat | ✓ |
| 9 | **hilbert_real = PCA 2D lex sort alias** (5축 검증 C fix 반영) | line 330 (여섯째 한계) | REPORT v13 §10 line 352 = "hilbert_real은 실제로 PCA 2D lexicographic sort 기반이고(Faloutsos 1989의 정통 Hilbert curve가 아님)" — 정직 명시 carry | ✓ |
| 10 | **sparse_rp = Li-Hastie-Church 2006** (5축 검증 C fix 반영) | line 330 (여섯째 한계) + line 579 ([14] reference) | REPORT v13 §10 line 352 = "sparse_rp는 Achlioptas 2003이 아닌 Li-Hastie-Church 2006 variant다" + 보고서 [14] 신규 reference 항목 — Li/Hastie/Church 1/√D variant 명시 | ✓ |
| 11 | **paired Pearson 상관 v13 재계산 +0.008** (5축 검증 E fix 반영) | line 328 (다섯째 한계) | "B1과 실험군의 trial 사이 Pearson 상관이 본 v13 측정 캠페인 1,508건 전수에서 평균 +0.008로 사실상 0에 수렴" + 직전 캠페인 −0.013과의 정합 carry | ✓ |

**5축 multi-axis fix 추가 검증**:
- **§4.7 다섯째 paired Pearson 갱신** — 직전 보고서 본 _20260519_135021 (archive) 은 v12 −0.013 만 carry / 현 _20260520_093500 은 **+0.008 v13 정본 추가** (fix E 적용 확인).
- **§4.7 여섯째 한계 신설** (hilbert_real / sparse_rp 명칭·출처) — fix C 적용 확인. line 330 의 sub-paragraph 자체가 _20260520 본에서 새로 신설된 것으로 보임.
- **§8 [14] Li 2006 reference** — line 579: `[14] Li, P., Hastie, T. J., and Church, K. W. "Very Sparse Random Projections." ... (KDD '06)` — fix C 의 reference book-keeping 일치.

**§2 verdict**: **PASS** — 6 한계 + 5축 fix 3종 모두 반영 정합.

---

## §3. §5.6 honest 한계 (Phase 2 엔진 적용 검증, 4 항목)

§5.6는 line 435-449 (15 줄, 5 sub-paragraph). 검증 task 는 4 항목만 지정하므로 1~4번째 검증.

| # | 한계 | 보고서 §5.6 위치 | 정본 정합 |
|---|---|---|:---:|
| 12 | **B1 클램프 노출 (MIN_INJECT=1.0)** | line 439 (첫째 한계) | Phase 2 정본 carry — "core 4 cell의 12개 측정 모두에서 베이스라인의 주입값이 1.0으로 클램프되며" / "13종 강한 method 가운데 sel=0.001에서 0을 뽑는 경우는 본 측정에서 관찰되지 않았다" 명시 | ✓ |
| 13 | **Q3 만 정확도 미달 method (8건)** | line 441 (둘째 한계) | §5.4 plan 회복 매트릭스 line 394-398 8/156 결합 미달 = qid0 hilbert_real / qid1 sparse_rp / qid2 6 method split — 모두 Q3 만 발생 명시. "Q9·Q10·Q12에서는 결합 13종 × 3 qid = 39회의 plan 회복 기회가 모두 성공" carry | ✓ |
| 14 | **sel=0.001 한정** (Phase A carry-over for §6.4) | line 443 (셋째 한계) | "본 §5의 측정 평면은 그 가운데 core 4 cell만을 대상으로 한다. saturated·invariant cell의 latency 분산 측정은 §6.4의 향후 작업에서 carry-over로 다룬다" — §6.4 link 명시 | ✓ |
| 15 | **DEEP·sf=10 단일 데이터셋** | line 445 (넷째 한계) | "본 §5의 12 cell은 모두 DEEP 256차원·sf=10(8천만 행) 위에서 측정된다. SIFT·SSN·다중 벡터 데이터셋과 sf=1·sf=100 규모의 엔진 적용 검증은 측정 시간이 다중적으로 늘어 본 보고서의 작성 일정 안에 완료할 수 없었다" — §6.4 link 명시 | ✓ |

§5.6 보너스 — **다섯째 한계 plan signature 정밀도** (line 447) 도 견고하게 노출됨.

**§3 verdict**: **PASS** — 4 한계 모두 정본 carry + §6.4 link 명시.

---

## §4. §6.4 향후 작업 4갈래 정합 (Phase A carry 검증)

§6.4는 line 497-507 (11 줄, 4 sub-paragraph).

### (1) 엔진 적용 측정 평면 확장 — line 501 ★ MAJOR ISSUE

**보고서 본문 (line 501)**:
> 첫째는 엔진 적용 검증의 측정 평면 확장이다. Ch.5의 본 검증은 DEEP·sf=10·sel=0.001의 12 cell — Phase 0의 사전 탐색이 plan 변화의 핵심 cell로 분류한 core 4 cell × 질의 벡터 3개 — 에 한정되었다. plan이 추정값 변동과 무관하게 같은 형태를 유지하는 saturated·invariant cell의 latency 분산이 어떻게 분포하는지, 그리고 SIFT·SSN·다중 벡터 데이터셋과 sf=1·sf=100 규모로 데이터셋·scale을 펼쳤을 때 같은 plan 회복 robustness가 유지되는지가 첫째 갈래의 과제다. 한 cell당 약 6분의 측정 시간이 드는 본 검증 구조 위에서, 측정 평면을 한 단계씩 넓혀 가는 carry-over 측정으로 이 과제를 다룬다.

**Phase A 결과 (analyze_stdout.txt) 가 실제로 보여 주는 것**:
- **8 cell 측정 완료** = 4 query(q3·q9·q10·q12) × 2 sel(0.01·0.1) × qid0 = 8 cell × 16 variant × 15 rep
- **saturated 5 cell** (sel=0.01 4 cell + q10/q12 sel=0.1 2 cell — 단 sel=0.1 6 cell 중 5 cell): 모든 variant 가 baseline 과 같은 plan 유지 (`전 조건 동일 플랜`).
- **invariant 3 cell** (q10/q12 sel=0.1 2 cell + 추정): plan 미변화 + speedup ≈ 1.0× 로 estimation 변화의 latency 영향 미미.
- **★ q9 sel=0.1 = 새 발견** (line 149 of analyze_stdout): `tpc_h/q9 DEEP sf10 sel0.1 qid0 변화 → B1, oracle, CaseB:hilbert_real, ...` — **모든 비-baseline variant 에서 plan 변화 (≠)** 가 발생. sel=0.1 이 "plan-invariant" 라는 §5.6 셋째 한계의 분류와 모순되는 새 발견.

**문제점**: §6.4 (1) 갈래는 **이미 측정된 Phase A 8 cell 결과**를 carry 하지 않고 "측정 평면을 한 단계씩 넓혀 가는 carry-over 측정으로 이 과제를 다룬다" 는 추상적 향후 표현으로만 남김. 특히:
- **q9 sel=0.1 plan 변화** 라는 새 발견 (saturated/invariant 가설을 깨는 결과) 가 본문에 carry 되지 않음.
- §5.6 셋째 한계 (line 443) 는 "saturated(주로 sel=0.01) 또는 plan-invariant(sel=0.1)" 로 분류했으나 Phase A 가 그 분류 자체를 부분 부정함 — 한계 sub-section 의 분류 표현 자체가 새 측정 결과로 보정 필요.
- Phase A 8 cell 의 saturated/invariant 패턴 (q10/q12 sel=0.1 plan 미변화 + B1 speedup ≈ 1.0×) 도 새 발견인데 명시 carry 되지 않음.

**severity = major** (정본 수치 89.1% 류 critical 은 아니지만, 검증 ETA task 가 명시한 "Phase A carry" 자체가 누락).

### (2) 통계 보강 — line 503

**보고서 본문**:
> 둘째는 통계 검증 도구의 확장이다. Ch.5의 짝지은 Wilcoxon 검정은 p_holm으로 유의성을 보고하고 plan 회복 매트릭스로 cell 수준의 robustness를 정리하였으나, 효과 크기를 정량화하는 Cohen's d·Cliff's δ나 부트스트랩 95% 신뢰구간 같은 보조 통계가 더해지면 결합 방식의 가치를 더 풍부한 축에서 비교할 수 있다. 통계 산출 도구(analyze_latency.py)에 이 보조 통계를 추가하고, Ch.5의 12 cell × 16 variant × 15 rep 측정값을 같은 짝지은 비교 구조에서 다시 정리하는 것이 둘째 갈래의 과제다.

**정합**: ✓ Cohen's d / Cliff's δ / 부트스트랩 CI 정확히 명시. 도구 (analyze_latency.py) + 측정 모집단 (12 cell × 16 variant × 15 rep) 정확.

### (3) 4 엔진 통합 PoC — line 505

**보고서 본문**:
> 셋째는 박광현 교수님이 제안한 4 엔진 통합 개념 증명(proof of concept)이다. ... PostgreSQL의 pgvector, VBASE, DuckDB, 그리고 vector.c 기반 PostgreSQL 네 가지 서로 다른 벡터 데이터베이스 엔진을 하나의 측정 틀로 통합하여, 분포 인지 층화로의 개입이 어느 엔진에서도 동일하게 추정 오차를 개선하는지를 검증하는 것이 셋째 과제다.

**정합**: ✓ 4 엔진 (pgvector / VBASE / DuckDB / vector.c PostgreSQL) 명시. 교수님 제안 출처 함께 carry.

### (4) 측정 공간 추가 확장 — line 507

**보고서 본문**:
> 넷째는 측정 공간의 추가 확장이다. 본 연구는 단일 벡터 다섯 종과 직접 합성한 다중 벡터 세 종으로 측정 공간을 능동적으로 넓혔으나, 실제 응용 환경은 그보다 다양하다. 더 폭넓은 다중 모달(multi-modal) 벡터 조합으로 데이터셋의 다양성을 키우고, 합성 측정을 넘어 실제 작업 부하(real workload) 환경에서 표본 선택 방식의 효과를 검증하는 것이 넷째 과제다.

**정합**: ✓ multi-modal / real workload 명시. (1) 갈래의 SIFT·SSN·다중 벡터·sf 확장과 구분되어 — (1) 은 엔진 적용 검증 평면 확장 / (4) 는 측정 공간 자체 확장 (multi-modal·real workload) — sub-task 분리 정합.

**§4 verdict**: **WARN** — 4 갈래 중 (2)·(3)·(4) PASS, (1) 갈래에서 **Phase A 8 cell 측정 결과 carry 누락 = 1 major issue**.

---

## §5. 발견 issue catalog

| # | severity | issue | 위치 | 권고 |
|---|---|---|---|---|
| ISSUE-η-01 | **major** | §6.4 (1) 갈래에 **Phase A 측정 8 cell 결과 carry 누락**. 특히 (i) q9 sel=0.1 모든 variant plan 변화 (≠) — sel=0.1 = "invariant" 라는 §5.6 셋째 한계의 분류와 모순되는 새 발견. (ii) q10/q12 sel=0.1 5 cell 의 plan-invariant + speedup ≈ 1.0× 패턴 carry 없음. | 보고서 line 443 (§5.6 셋째 한계 분류) + line 501 (§6.4 (1) 갈래) | (a) §6.4 (1) 갈래 마지막에 "**[Phase A 진행분]** 본 보고서 작성 시점에 8 cell × 16 variant × 15 rep 측정이 완료되었으며 (q3·q9·q10·q12 × sel∈{0.01,0.1} × qid0), saturated 패턴 5 cell + invariant 패턴 2 cell + q9 sel=0.1 새 plan 변화 1 cell 이 확인되었다. 이 결과는 sel=0.1 도 일부 query 에서 plan-invariant 가 아닐 수 있음을 시사하며, qid·query 전수 확장이 필요하다." 1-2 sentence 추가. (b) §5.6 셋째 한계 분류 표현 ("plan-invariant(sel=0.1)") 을 "주로 plan-invariant(sel=0.1) — q9 등 일부 query 예외 가능" 로 약간 보정. |
| ISSUE-η-02 | minor | §6.4 (1) 갈래 본문에 "한 cell당 약 6분의 측정 시간" 표기 — Phase A 측정 분당 시간 정합 검증 시 정확한 출처 확인 필요. | line 501 | 본 issue 는 보정 불요 — 측정 시간 표현은 carry-over 측정 의도 표시이며 critical 아님. |

---

## §6. fix 권고 (실행 우선순위)

1. **PRIORITY 1 (major)** — ISSUE-η-01 (a)·(b) 양쪽:
   - §6.4 (1) 갈래 마지막에 Phase A 8 cell carry 1-2 sentence 추가 (saturated 5 / invariant 2 / q9 sel=0.1 plan 변화 1 의 새 발견 명시).
   - §5.6 셋째 한계 (line 443) 의 saturated/invariant 분류 표현을 Phase A 결과로 약간 보정.
   - 위 두 위치를 함께 패치하면 본 검증 task 가 명시한 "Phase A 결과 (1) 갈래 반영" 100% 통과.

2. **PRIORITY 2 (none — 정합 유지)** — 정본 수치 5 항목 (§1) + §4.7 6 한계 (§2) + §5.6 4 한계 (§3) 모두 PASS, 보정 불요.

---

## 부록 — 5축 multi-axis fix 검증 (cross-reference)

검증 task 가 명시한 "5축 multi-axis fix" 의 §4.7 반영 여부를 별도 cross-check:

| fix axis | 내용 | §4.7 반영 | line |
|---|---|---|---|
| C-1 hilbert_real | PCA 2D lexicographic sort alias 명시 | ✓ | line 330 (여섯째 한계 신설) |
| C-2 sparse_rp | Li-Hastie-Church 2006 정본 출처 명시 | ✓ | line 330 + line 579 ([14] reference) |
| E paired Pearson | v13 +0.008 추가 명시 (v12 −0.013 정합) | ✓ | line 328 (다섯째 한계 갱신) |
| (기타 5축 fix 가 §4.7 적용 대상 외) | — | — | — |

5축 검증 결과 (C·E) 가 §4.7 신설 6번째 + 다섯째 갱신 으로 완전 반영. fix C 의 sparse_rp 의 [14] reference 도 §8 line 579 carry — book-keeping 완전.

---

## 종합

- **§1 정본 수치 5 항목**: PASS — v13 정본 완전 일치.
- **§2 §4.7 6 한계 (5축 fix 포함)**: PASS — 5축 multi-axis fix (C·E) 완전 반영.
- **§3 §5.6 4 한계 (Phase 2 검증)**: PASS — Phase 2 정본 수치 carry.
- **§4 §6.4 4 갈래 (Phase A carry)**: **WARN** — (2)·(3)·(4) PASS, (1) 갈래에서 Phase A 8 cell 측정 결과 carry 누락 (major).
- **종합 verdict**: **WARN** — 1 major issue (ISSUE-η-01). 정본 수치·5축 fix·Phase 2 한계 정합은 완전.

---

_검증 종료: 2026-05-20 12:30 KST · η 축 sub-agent_
