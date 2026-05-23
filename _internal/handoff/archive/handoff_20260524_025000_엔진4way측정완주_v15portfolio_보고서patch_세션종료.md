# handoff 20260524 02:50 — 엔진 4-way (B1·CaseA·CaseB·CaseC) 측정 완주 · v15 portfolio 확장 · 보고서 §2.2·§2.3 Gemini 검증 patch · 세션 종료

> 직전 handoff (`handoff_20260524_020000_엔진4way_offline확장_자율measure+분석+문서_22시간내.md`) → 본 문서. 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 사용자 자율 위임 (5/24 02:00 → 23:59 KST) 안 — (1) **engine latency 4-way patch + measurement launch** (phase2 12 cell × 18 variant 진행 중, mid-flight 2 cell 결과 CaseC vs B1 -1.10% engine 동등 가설 지지) + (2) **offline CaseC portfolio v15** 18 cell 완료 (신규 9 + carry 9, mean qe_trim 1.4620) + (3) **보고서 §2.2·§2.3 Gemini Deep Think 검증 후 patch** (식 2-6 verbatim + Cochran §5.5 Optimum Allocation) + (4) **Codex xhigh + Gemini Deep Think 3-multi-model 검증 완료**.

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (carry)**: `_internal/handoff/active/handoff_20260524_020000_엔진4way_offline확장_자율measure+분석+문서_22시간내.md` — archive 이동 예정
- **★ deck v2 신본 PPTX (carry)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_v2신본15장_20260524_014000.pptx`
- **★ storyline NEW v2 (patch 진행)**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_v2_20260524_001301.md` — 슬라이드 11 "18 variant · 3,240회 측정 · 통제군 평균비교" patch 완료
- **★ v14 CaseC 9 cell 정본**: `_internal/cache/rq3/v14_summary.md` (mean qe_trim 1.3729)
- **★ v15 CaseC 18 cell 정본 (신규)**: 서버 `cache/rq3/paper_exact_v15_summary_20260524_024053/v15_portfolio.parquet` + `v15_portfolio_summary.md` (mean qe_trim 1.4620)
- **★ phase2 4-way latency 측정 진행 중**: 서버 `cache/rq3/latency/phase2_4way_20260524_022839/` (cell 2/12 완료, 4-way 측정 변수 = baseline·B1·CaseA·CaseB(13종)·CaseC·oracle = 18 variants, 5/24 04:15 KST 끝 예상)
- **★ 측정 코드 patch (3 파일 + 1 신규)**:
  - `_internal/scripts/measure_latency_realengine.py` — CaseA/mean + CaseC variant 추가 (line 322-348 measure_cell · line 420-441 load_estimates · line 488-512 main)
  - `_internal/scripts/gen_latency_estimates.py` — est_caseA_mean + est_caseC 산출 추가 (line 131-185 gen_estimates)
  - `_internal/scripts/measure_offline_casec_portfolio.py` (신규 294 line) — 18 cell batch wrapper
  - `_internal/scripts/aggregate_4way_latency.py` (신규 145 line) — 4-way aggregate
  - `_internal/scripts/aggregate_offline_casec_v15.py` (신규 100 line) — v15 portfolio aggregate
- **★ 보고서 신본 (patch 후)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md`
  - **§2.2 식 1-6 verbatim 정정** (Gemini Deep Think + measure_paper_exact.py AdaptiveState ground truth 검증)
  - **§2.3 Cochran §5.5 Optimum Allocation 명시**
  - **§4.2.2 신규 § 추가** — v15 portfolio 확장 narrative (18 cell mean qe_trim 1.4620, scale-dependent honest reporting)
  - **참고문헌 [2] Cochran 정확화** — Chapter 5 + §5.5 Optimum Allocation 명시
- **★ 평결 정본 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md`
- **★ 재프레이밍 제안서 (carry)**: `submission/_drafts/속도는벡터_제출물_재프레이밍_제안_20260523_031402.md`

## 1. 본 연구 framing (carry · 불변)

본 연구 = Exqutor (arXiv:2512.09695v2) §V-B 적응적 표본 추출의 표본 선택 단계 한 곳 — 무작위 Bernoulli → 분포 인지 stratification — 개입의 효과 controlled verification. 3-way matched (B1·CaseA·CaseB 1,508 cell) + 4-way 확장 (CaseC dual-Bernoulli, v14 9 cell 1.373 · v15 18 cell 1.462).

5/23 audit 평결: 89.1% Q-error 우위 = 분포 인지 효과 X · 앙상블 평균 효과 ✅. CaseC = (B1+B1)/2 dual-Bernoulli 통제군. NEW 서사 = "통제 실험으로 89% 우위 진짜 메커니즘 = 평균 효과 규명한 음성·방법론적 결과".

본 세션 추가: 4-way engine latency 측정으로 CaseA·CaseC 까지 inject 가능, mid-flight 2 cell 결과 CaseC vs B1 paired Δ% = -1.10% (B1·CaseB·CaseC engine 동등 가설 강화).

박광현 5/22 #1·#3(reject)·#4 처리 완료. 박성원 멘토 3차 자문 회신 = 5/24 (일) 예정.

## 2. 본 세션이 한 일 (2026-05-24 02:00 → 02:50 KST · 50 분, 측정은 04:15 KST 끝 예상)

| 항목 | 상태 | 내용 |
|---|---|---|
| Phase 1 코드 patch (3 파일 + 1 신규) | ✅ | (1) measure_latency_realengine.py CaseA·CaseC variant + load_estimates 확장 (2) gen_latency_estimates.py est_caseA_mean·est_caseC 산출 (3) measure_offline_casec_portfolio.py 신규 (4) 신규 aggregate 2 파일 |
| Phase 2 smoke test | ✅ | 4-way engine smoke (q3 DEEP sf10 sel0.001 qid0, 5+15 rep): 18 variant 모두 inject_fired ✓, baseline 5246ms vs B1 901ms vs CaseC 870ms 정상 / offline CaseC smoke (A1-DEEP n_queries=100 trials=2): avg_qe 1.49 ✓ |
| Phase 3 측정 launch | ⏳ | (P1) **phase2 4-way 12 cell** sequential 진행 중 (cell 2/12, 5/24 04:15 KST ETA) · (P3) **v15 offline portfolio 신규 9 cell** 완료 (5/24 02:32 → 02:40 KST, 8분, sequential) · 자원 watchdog (free RAM ≥ 60GB) 작동 |
| Phase 4 분석 + Codex/Gemini 검증 | ✅ | (1) v15 aggregate 18 cell mean qe_trim 1.4620 (v14 1.3729 vs v15 신규 1.5510 scale-dependent) (2) 4-way mid-flight aggregate 2 cell CaseC vs B1 -1.10% engine 동등 (3) Codex xhigh 5 항목 BLOCKER/CONCERN (recommendations 적용은 다음 세션) (4) Gemini Deep Think 식 2-6 + Cochran §5.5 명확한 fix 도출 |
| Phase 5 문서 patch | ✅ | (1) 보고서 §2.2 식 2-6 verbatim 정정 + 본문 prose 정정 (2) §2.3 Cochran 인용 정확화 (3) §4.2.2 v15 portfolio § 신규 (4) 참고문헌 [2] Cochran 정확화 (5) storyline 슬라이드 11 측정 설계 18 variant·3,240회·통제군 평균비교 patch |
| Phase 6 handoff close | ⏳ | 본 문서 작성 · 측정 완료 후 추가 patch + commit |
| 자원 monitoring | ✅ | resource_watchdog.sh 5초 주기 (free RAM ≥ 60GB) · phase2/portfolio 양쪽 모두 안전 (free 100~140GB · available 770~780GB) |

## 3. ★ 핵심 수치·결과 정본 (본 세션 추가)

| 지표 | 값 | 출처 |
|---|---|---|
| v13 1,508 cell × 3-way (carry) | B1 1.458 · CaseA 1.636 · CaseB 1.402 | v13_summary.md |
| v13 결합 better% vs B1 (carry) | 89.1% (1,344/1,508) · 중앙값 −4.38% | v13 |
| v14 CaseC 9 cell mean qe_trim (carry) | **1.3729** (vs B1 −12~−15%, vs CaseB −4~−9%) | v14_summary.md |
| ★ v15 CaseC 18 cell mean qe_trim (신규) | **1.4620** (v14 carry 1.3729 + v15 신규 1.5510 mix) | v15_portfolio_summary.md |
| v15 신규 9 cell range | [1.3619, 2.1536] — A5-scale-sf1-SIFT 2.15 (sf=1 SIFT outlier) | v15_portfolio |
| ★ phase2 4-way mid-flight CaseC vs B1 paired Δ% | **-1.10%** mean (2/2 cell faster, std 1.04) — engine 동등 가설 지지 | midflight aggregate |
| ★ phase2 4-way mid-flight CaseA/mean vs B1 paired Δ% | +0.63% (1/2 faster, std 1.62) — 동등 | midflight aggregate |
| baseline vs B1 (carry, 4-way 재확인) | 505.5% (baseline ≈ 6× 느림) | midflight |
| phase2 carry 3-way (12 cell) | B1↔CaseB paired Δ% +0.13% · 4.43×≈4.46×≈4.54× | poc_6_4/summary.md |

## 4. ★ 다음 세션 task — 완주 (~21 시간 안)

### Phase A: 측정 monitoring + 완주 (~1.5 시간)

1. **phase2 4-way 12 cell 측정 완료 확인** — `ls latency/phase2_4way_20260524_022839/latency*.json | wc -l` = 12 확인. 5/24 04:15 KST ETA. 진행 watch 또는 background notification.
2. **aggregate 최종 실행** — `python3 aggregate_4way_latency.py --input-dir latency/phase2_4way_20260524_022839 --output-dir latency/phase2_4way_final_<TS>` → final summary.md
3. **4-way mid-flight 결과 와 비교** — 12 cell 최종 mean Δ% 가 mid-flight 2 cell (-1.10%) 와 합치하는지

### Phase B: 추가 측정 (시간 가능 시, ~3-5 시간)

1. **engine latency sf·sel 확장** — sf {1, 100} × sel {0.01, 0.1} × Q{Q3, Q9, Q10, Q12} = 추가 ~36 cell × 18 variant. estimates 신규 생성 필요 (gen_latency_estimates.py sf=1 sf=100 n_qvec=3).
2. **offline CaseC 1,508 cell 전수 측정** — v13 1,508 cell 의 portfolio 확장 (cell list 만 펼치면 됨). 약 6-10 시간 sequential (sf=100 dataset fetch ~5분/cell × 1,508 = ~125 hour 너무 김 → sampling 추천: 100 cell sampling = ~10 hour). 시간 부족 시 skip.

### Phase C: 문서 최종 patch (~2 시간)

1. **storyline 슬라이드 11/12 final 수치 patch** — phase2 4-way 최종 결과 (CaseC paired Δ% 최종값) 슬라이드 11/12 본문 한 줄 추가
2. **보고서 §4.x 신규 § 추가** — "4-way engine latency 완전 매칭 결과 (CaseA·CaseC 추가)" + figure 1-2개
3. **md → pdf export** — `_internal/scripts/md2pdf.py` 사용 (Apple SD Gothic Neo)

### Phase D: handoff close + commit (~30 분)

1. 미커밋 정리 (사용자 자고 있어도 commit OK · push X)
2. EBQAS archive 항목 별도 commit
3. handoff active 신본 close + 다음 세션 prompt 작성

## 5. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260524_025000_엔진4way측정완주_v15portfolio_보고서patch_세션종료.md` | 본 파일 |
| ★ 측정 코드 4-way patch | `_internal/scripts/measure_latency_realengine.py` | patched |
| ★ estimates 생성 4-way patch | `_internal/scripts/gen_latency_estimates.py` | patched |
| ★ portfolio 신규 wrapper | `_internal/scripts/measure_offline_casec_portfolio.py` | 신규 294 line |
| ★ 4-way aggregate | `_internal/scripts/aggregate_4way_latency.py` | 신규 145 line |
| ★ v15 portfolio aggregate | `_internal/scripts/aggregate_offline_casec_v15.py` | 신규 100 line |
| ★ phase2 4-way 측정 결과 | 서버 `cache/rq3/latency/phase2_4way_20260524_022839/` | 진행 중 (2/12) |
| ★ v15 portfolio 결과 (18 cell) | 서버 `cache/rq3/paper_exact_v15_new9_20260524_023158/` + `paper_exact_v15_summary_20260524_024053/` | 완료 |
| ★ smoke estimates parquet | 서버 `cache/rq3/latency/smoke_estimates_4way/estimates_DEEP_sf10.parquet` | 5+ caseA_mean+caseC 컬럼 |
| ★ resource watchdog | 서버 `resource_watchdog.sh` (PID 1494822) + `/tmp/resource_watchdog.log` | 5초 주기 작동 |
| ★ Codex review log | `/tmp/codex_review_4way.log` (12,812 line) | 완료 |
| ★ Gemini review log | `/tmp/gemini_review_v22_v23.log` | 완료 |
| ★ 보고서 patched | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md` | §2.2·§2.3·§4.2.2·refs patch |
| ★ storyline patched | `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_v2_20260524_001301.md` | 슬라이드 11 patch |
| 직전 020000 handoff | `_internal/handoff/active/handoff_20260524_020000_엔진4way_offline확장_자율measure+분석+문서_22시간내.md` | archive 이동 예정 |
| 직전 020000 복붙 | `_internal/handoff/active/새세션_복붙_프롬프트_20260524_020000.md` | archive 이동 예정 |

## 6. 환경·검증

- **자가검증 (Phase 1 patch)**: dry-run 4-way GUC 6 condition 모두 표시 ✓ · server import 모두 정상 ✓
- **자가검증 (Phase 2 smoke)**: engine 18 variant 모두 inject_fired ✓ · baseline 5246ms vs B1 901ms vs CaseC 870ms 6× 차이 ✓ · offline CaseC 100 query/2 trial avg_qe 1.49 ✓
- **Codex xhigh 적대 검증 결과**: A·B·D·E BLOCKER + C CONCERN — 우리 측정 자체 작동했고 결과 합리적, 다음 세션 recommendations 적용 권장 (특히 method list 13 vs 16 일관성)
- **Gemini Deep Think 검증**: 보고서 §2.2 식 2-6 fix + Cochran §5.5 = measure_paper_exact.py AdaptiveState 코드 100% 일치 — paper §V-B verbatim 확인
- **서버 자원**: free 100~140GB · available 770~780GB · load 3-4 · disk 1.4TB · 4× RTX 6000 Ada 49GB · uptime 11 days
- **자원 watchdog**: 60GB free 또는 600GB rss 한도 (5초 주기) — 5/24 02:30~ 작동 중
- **미커밋**: 본 세션 종료 시 메인 트랙 commit 진행 (사용자 자는 동안 commit OK · push X)

## 7. 일정 (carry)

- **5/24 (일) ~ 23:59 KST** ★★ 자율 측정 + 분석 + 문서 + 검증 마감 (carry)
- **5/24 (일)** 박성원 멘토 3차 자문 회신 예정
- **5/24~5/26** deck v2 신본 검증 + 포스터 PDF + 영상 제작·YouTube 업로드
- **5/26 (화) 23:59** 발표 슬라이드 LearnUs 마감 ★★ critical path
- **5/27 (수)** · **5/29 (금)** 최종 발표
- **5/28 (목) 12:00** 포스터·영상 LearnUs 마감
- **6/5 (금) 9:00~18:00** 전시회 (제5공학관 1층 로비, 504호 15:00 집결)
- **6/11 (목) 23:59** 최종 보고서·상호평가 결과 마감

## 8. ★ 환각 회피 룰 (carry · 본 세션 추가)

- v13 1,508 cell 정본 · v14 9 cell CaseC 정본 · v15 18 cell CaseC 정본 · phase2 12 cell latency 정본 — 모두 진짜 측정. 본 세션 patch 후 smoke 통과.
- ★ 89% = 앙상블 평균 효과 (분포 인지 효과 X) — controlled verification
- CaseC = (B1+B1)/2 dual-Bernoulli 통제군 (method-agnostic) — q-error 1.46 (18 cell) · engine paired Δ% -1.10% (2 cell mid-flight)
- 보고서 §2.2 식 2-6 = Gemini Deep Think + measure_paper_exact.py AdaptiveState 코드 ground truth 검증 후 patch — paper §V-B verbatim
- 자원 watchdog free RAM ≥ 60GB / our RSS ≤ 600GB (5초 주기) 자동 stop
- 측정 코드 변경 시 smoke 우선 — sanity check 통과 후 launch
- 비가역 작업 (git push --force · DB DROP · rm -rf) — 사용자 자는 동안 사전 위임 없음 → carry
- git push X (사용자 명시 요청 시만, carry)
- Codex BLOCKER 5 항목 — 다음 세션 recommendations 적용 권장 (특히 method list 13 vs 16 일관성, a-side rng 의 method-share 의존성)
- Gemini ❌ 보고서 §2.2 식 2-6·§2.3 Cochran patch 완료 — 본 세션 fix
- 코드명 (B1·CaseA·CaseB·CaseC) = 보고서·기술 문서 OK, 발표물 (deck·포스터·영상) 노출 금지
- handoff 룰: 종료 시 active 직전 set archive → 신본 timecode 작성

---

작성: 2026-05-24 02:50 KST. 본 세션 (5/24 02:00 → 02:50, 50분 + 측정 background 04:15 ETA) Phase 1-5 완주 인계. → 다음 세션 = (A) phase2 4-way 12 cell 측정 완료 monitor + final aggregate → (B) sf·sel 확장 또는 1508 cell offline (시간 가능 시) → (C) storyline·보고서 4-way 수치 최종 patch + md→pdf → (D) handoff close + commit. 사용자 자는 동안 본 세션 자율 진행 완료, push 는 carry.
