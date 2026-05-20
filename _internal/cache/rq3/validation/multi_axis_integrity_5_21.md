# 통합 최종 검증 — 8축 multi-axis integrity 종합 verdict (5/20 12:30~13:00 KST)

> 본 보고서 = 8 sub-agent (α·β·γ·δ·ε·ζ·η·θ) 가 병렬 launch 되어 약 12분 만에 산출한 8 validation md 의 종합 verdict + fix log. 본 세션 plan(`~/.claude/plans/kind-rolling-falcon.md`, 8축 150 항목)의 step 4 산출물.

---

## 0. 종합 VERDICT

**전체**: WARN/FAIL — **critical 3 + major 11 + minor 8** = 총 22 fix 항목. 추가 실험 trigger 없음.

| 축 | sub-agent VERDICT | issue 수 | 산출 file |
|---|:---:|--:|---|
| α (Phase A vs prescan) | WARN | 1 major + 4 minor | `alpha_phase_a_vs_prescan.md` |
| β (보고서 §5 inline vs Phase 2) | WARN | 6 major + 3 minor | `beta_report_section5_inline.md` |
| γ (figure 3종 데이터 backing) | PASS (minor) | 0 major + 3 minor | `gamma_figures_backing.md` |
| δ (발표물 4종 cross-check) | **PASS** | 0 | `delta_4_artifacts_vs_report.md` |
| ε (보고서 cross-reference) | **FAIL** | 3 critical + 3 major | `epsilon_report_xref.md` |
| ζ (handoff 자체 정합성) | PASS (minor) | 0 + 2 minor | `zeta_handoff_self_integrity.md` |
| η (§4 + §4.7 + §5.6 + §6.4) | WARN | 1 major | `eta_section46_future_work.md` |
| θ (code vs §5.2 산문) | WARN | 1 major + 2 minor | `theta_code_vs_method_narrative.md` |

★ 다행: **정본 수치 (3-7× / 94.9% / 7/12 / 5.67× / 89.1% / −4.38% / 180/180 / 13/168) 모두 raw 정합 PASS**. 발견 issue 는 본문 산문 (β line 381/427/439) + figure 내부 stale title (ε C-2/C-3) + chapter shift carry 누락 (ε C-1, η, θ) 으로, 표·매트릭스·통계 자체는 견고하다.

★ 추가 실험 trigger 없음 — α 가 명시 (prescan 가설 7/8 strict + 8/8 partial PASS, q9 sel=0.1 honest exception 은 산문 보강으로 충분).

---

## 1. CRITICAL issue catalog (3건, 모두 ε 축)

| ID | 파일 | 위치 | 환각/오류 | fix 권고 |
|---|---|---|---|---|
| **C-1** | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.md` | line 483 (§6.2 권장 첫 단락) | "5.1의 표" — chapter shift 후 §5.1 (도입) 에는 표 없음 | "5.1의 표" → "6.1의 표" (1-char edit) |
| **C-2** | `experiments/figures/보고서_6_11/fig6_1_dynamic_method_selection.{png,pdf}` | PNG 내부 embedded title | "그림 5-1. 동적 method 선택 4단계 흐름도" stale | 재렌더링: 내부 title "그림 6-1" 로 갱신 |
| **C-3** | `experiments/figures/보고서_6_11/fig7_1_gantt.{png,pdf}` | PNG 내부 embedded title | "그림 6-1. 캡스톤 연구 진행 일정" stale | 재렌더링: 내부 title "그림 7-1" 로 갱신 |

---

## 2. MAJOR issue catalog (11건)

| ID | 출처 축 | 파일 | line | 환각/오류 | fix |
|---|:---:|---|--:|---|---|
| M-β1 | β | 보고서 md | 381 | "B1 평균 1,005ms" (raw 968.7ms) | "B1 평균 969ms" |
| M-β2 | β | 보고서 md | 381 | "모든 cell에서 ... 3배 이상" (q9 qid1=2.81×, qid2=2.90× 미달) | "12 cell 중 10 cell에서 3배 이상이며 Q9의 두 cell(qid1·qid2)만 2.8~2.9× 가속에 머문다" |
| M-β3 | β | 보고서 md | 427 | "절반 이상이 베이스라인이 ... 더 빠른" (실제 5/13=38.5%, 절반 미만) | "13건 중 5건은 베이스라인이, 8건은 결합·정답이 더 빠른" |
| M-β4 | β·γ | 보고서 md | 427 | "Q12 4 method p_holm = 0.0034" (raw 0.0103) | "p_holm = 0.0103" |
| M-β5 | β | 보고서 md | 427 | "약 9~16ms 더 빠른" (raw 34~40ms) | "약 34~40ms 더 빠른" |
| M-β6 | β | 보고서 md | 439 | "12개 측정 모두 1.0 클램프" (4개 qid 0 만, qid 1·2 의 8개는 4156·10390 정상) | "core 4 cell × qid 0의 4개 측정에서 베이스라인 주입값(injected_card_seen)이 1.0으로 클램프되며 (qid 1·qid 2의 8개 측정에서는 베르누이 표본이 정상 적중하여 약 4,156·10,390 추정값이 주입된다)" |
| M-ε2 | ε | 보고서 md | 555 | "§5.5의 이론적 토대" (Cochran 책 §5.5 — 신본 §5.5(Wilcoxon)과 충돌) | "Cochran §5.5의 이론적 토대" |
| M-ε3 | ε | 보고서 md | 545 | "표 6-1" (위치 §7.2 안, chapter 번호 규칙 위반) | "표 7-1" |
| M-η1 | η | 보고서 md | 501 (§6.4 (1) 갈래 끝) | Phase A 8 cell carry 누락 | 마지막에 1-2 sentence 추가: "본 보고서 작성 시점에 8 cell × 16 variant × 15 rep 측정이 완료되어, sel=0.01 의 4 cell 은 모두 plan 변화 + 2~3× 가속, sel=0.1 의 q3·q10·q12 3 cell 은 plan 무변동 + 거의 동일 latency 로 prescan 가설과 정합한다. 단 q9 × sel=0.1 1 cell은 plan은 변화하면서 oracle/baseline 0.93× 의 감속이 관측되어 plan-invariant 분류와 부분 어긋난다 — qid·query 전수 확장이 후속 과제다." |
| M-η1b | η | 보고서 md | 443 (§5.6 셋째 한계) | saturated/invariant 분류 표현 정직성 | "(주로 sel=0.01) 또는 plan-invariant(주로 sel=0.1) — Q9의 일부 cell 등 예외 가능 — 로 분류하였다" |
| M-θ1 | θ | 보고서 md | 389 (§5.4) | "(Node Type, Relation/Index, Join Type) 의 pre-order 튜플" (실제 analyze_latency.py:plan_signature 는 Node Type 1-tuple 만) | "Node Type 의 pre-order 튜플" |
| M-α1 | α | 보고서 md | §5.6 또는 §5.2 끝부분 | q9 sel=0.1 honest exception 산문 미수록 (M-η1b 와 함께 처리되어 M-η1 의 §6.4 (1) 갈래 추가로 흡수됨) | M-η1 의 1-2 sentence 가 α1 도 커버 — 추가 fix 불요 |

---

## 3. MINOR issue catalog (8건)

| ID | 출처 축 | 파일 | line | 정정 |
|---|:---:|---|--:|---|
| m-β1 | β | 보고서 md | 404 | "14% 정도 과대 추정" → "약 12~30% 과대 추정 (Q3 qid0 의 hilbert_real 한정 표현 유지) — minor: 보고서 본 표현이 hilbert_real(1.124)에 가까우므로 carry 유지 가능. fix 의무 아님" |
| m-β2 | β | 보고서 md | 425 | "1/2^15 = 약 3.05e-5" → "2/2^15 = 약 6.1e-5 (양쪽꼬리 최소)" |
| m-β3 | β | 보고서 md | 441 | "12~30% 과대 추정" → "12~41% 과대 추정" |
| m-γ1 | γ | 보고서 md | 385 (캡션) | "2.9~7.5×" → "약 3~8×" (raw 범위 2.81~7.81×) |
| m-θ2 | θ | 보고서 md | 354 | "이 60건의 비-기본 variant" → "이 180건의 비-기본 variant" (12 × 15 = 180) |
| m-ε1 | ε | handoff | task brief | "PDF 44p" stale → 실제 46p (다음 handoff revision) |
| m-ζ1 | ζ | handoff | §3.2 표 헤더 | "speedup(orc/base)" 라벨 정정 (다음 handoff revision) |
| m-ζ2 | ζ | handoff | §3.2 paired Wilcoxon 요약 | "sel=0.01 B1-vs-* p_holm = 1.0" 단정 → "대부분 = 1.0 (5/56 = 8.9% 만 유의)" (다음 handoff revision) |

---

## 4. fix 실행 plan

### 4.1 보고서 md 직접 Edit (14 line 정정)

main 이 Edit 도구로 한 번에 하나씩 정정. critical C-1 + major 11 + minor 5 = 17 정정. handoff/figure 외 — 보고서 md 한 file 만 수정.

### 4.2 figure 2종 재렌더링 (C-2/C-3)

먼저 fig6_1, fig7_1 산출 코드 위치 추적 (Glob/Grep) → title 인자 수정 → 재실행 → PNG/PDF 갱신.

### 4.3 보고서 PDF/DOCX 재생성

`_internal/scripts/md2pdf.py` + `md2docx.py` 실행 — md fix + figure 재렌더링 반영. timecode 새로 (`_20260520_HHMMSS`) 또는 기존 `_20260520_093500` 유지 후 archive 이동 결정.

판단: **새 timecode** 로 산출. 기존 _093500 본은 archive 이동. 이력 보존.

### 4.4 handoff 보강본 작성

새 timecode handoff 작성. anchor CLAUDE.md 갱신. multi-axis 검증 결과 §3.X 추가, fix log carry, 다음 세션 task 갱신 (5/22·5/25·5/26·5/27·5/28).

---

## 5. 추가 실험 trigger — **NONE**

α 축의 강한 결론 (prescan 가설 7/8 strict PASS · 8/8 partial PASS): q9 sel=0.1 1 cell exception 은 honest limitation 산문 보강으로 충분. 추가 측정 불요. 5/21 서버 마감 안 마무리 가능 (보고서 fix + figure 재렌더링 + 재생성 + handoff 총 약 1.5시간).

---

## 6. 정합 ★ 항목 (carry 시 강조 — fix 와 무관하게 견고함)

- **표 5-1 12 cell × 5 컬럼 = 60 cell**: raw 와 1:1 정확 (β PASS)
- **표 5-2 plan 회복 매트릭스**: B1 7/12 + CaseB 148/156 = 94.9% — raw plan_json 시그니처 1:1 정확 (β + γ + θ PASS)
- **표 5-3 paired Wilcoxon**: baseline anchor 180/180 = 100% + B1 anchor 13/168 = 7.7% — raw paired_stats.csv 1:1 정확 (β + γ PASS)
- **평균 speedup 5.67× / oracle 평균 957ms / Q-error 1.124/1.310**: 정확 (β PASS)
- **§4 정본 89.1% / −4.38% / 1,508 / method 13/3**: v13 정본 완전 일치 (η PASS)
- **§4.7 5축 multi-axis fix 3건** (hilbert_real / sparse_rp / paired Pearson +0.008): 완전 반영 (η PASS)
- **발표물 4종 cross-consistency**: 24 cell + 5 보고서 cross-check + 절대 규칙 20 sub-항목 모두 PASS (δ PASS — 가장 깔끔)
- **handoff 자체 정합성**: 12 항목 11 PASS + 1 PASS+minor + 1 PASS+소수 보강 (ζ PASS)

---

## 7. 종합 결론

**6/11 보고서 제출 전 critical 3 + major 11 의 fix 가 필요하나, 정본 수치·표·매트릭스·통계 자체는 완전 견고하다.** β·η·θ 의 major 정정은 모두 본문 산문 표현 정합 (raw 자체는 그대로) 이며, ε critical 은 chapter shift 시 carry 누락 (figure title 2건 + 본문 5.1→6.1 1건). 발표물 4종 프롬프트는 그대로 사용자 claude.ai/design 입력 가능 (δ PASS).

다음 단계: main 이 보고서 md fix 17 line + figure 2종 재렌더링 + PDF/DOCX 재생성 + handoff 보강 진행.

---

_작성: 2026-05-20 12:50 KST · 8축 multi-axis integrity 종합 verdict_
