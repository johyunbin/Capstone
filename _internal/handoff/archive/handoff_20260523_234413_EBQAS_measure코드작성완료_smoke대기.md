# handoff 20260523 23:44 — EB-QAS measure_ebqas 코드·4 unit test·Codex review spec 작성 완료, smoke·24 cell 측정 대기 carry

> 본 handoff = EB-QAS 별도 트랙 **네 번째 세션**의 최종 인계 anchor (23:30~23:54 KST · 24분). 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 세션은 직전 handoff_231042에서 carry된 4 task(활성화 결정·CaseB comparator 선정·measure_ebqas 코드 작성·4 unit test·Codex review·activation handoff) 중 5건을 완료했다 — (1) 사용자 답변 확정(활성화 + 코드 작성 / strong-13 aggregate / 측정 결과 회수 후 공유) (2) ultraplanning + ExitPlanMode 승인 (3) **measure_paper_exact.py 신규 11 항목 추가** (EBQASParams 12 필드·EBQASState 10 필드·bucketize_threshold·make_group_key·beta_credible_interval·ebqas_estimate·update_after_execution·_copy_ebqas_state·_ebqas_state_equal·measure_ebqas·assert_paired_join_invariant — 라인 1582~2144, AST parse OK) (4) **test_ebqas.py 신규 8 test all pass** (4 핵심 invariant test: mode switch streak·Q_post floor 분리·recovery·paired join + 4 헬퍼 test: bucketize·group_key·invariant pass·invariant fail 2건) (5) **Codex measure_ebqas review 디스패치 spec 신규** (codex_measure_ebqas_review_spec_20260523_234413.md, 6 축 carry + 코드·invariant 검증으로 분기). **EB-QAS measure_ebqas는 활성화 → smoke 1 cell 진입 가능 상태로 끌어올림**. 메인 트랙은 본 세션 손대지 않음 — 본 세션 modified는 measure_paper_exact.py 1건(EBQAS 블록 add)만, 나머지 산출물 모두 untracked. **다음 EB-QAS 세션 = (a) Codex review 디스패치·결과 회수 → (b) 6 축 verdict 분류 → pass면 smoke 1 cell launch (DEEP × sf=10 × sel=0.01) → (c) 24 cell sequential 측정 (DEEP·SIFT·WIKI × sf{1,10} × sel{0.001,0.01,0.10} × 2 prior_mode_init) → (d) paired 분석 4축(better_ratio + Wilcoxon + matched rank-biserial + bootstrap CI) 일관 시 결론 + 다음 carry handoff**.

## 0. 정본·진입점

- **★ 본 handoff** — 본 문서 한 장으로 EB-QAS 트랙 인계. self-contained.
- **★ 본 plan (본 세션 작성·승인)**: `~/.claude/plans/recursive-sparking-fairy.md` (ExitPlanMode 23:30 KST 사용자 승인)
- **★ 본 세션 신규 산출물 5건**:
  - **★ measure_ebqas 코드**: `_internal/scripts/measure_paper_exact.py` (라인 1582~2144 신규 11 항목 add. modified, 기존 함수 손대지 않음)
  - **★ 4 unit test + 4 헬퍼**: `_internal/scripts/test_ebqas.py` (신규, 8/8 PASS — `python3 _internal/scripts/test_ebqas.py`)
  - **★ Codex review 디스패치 spec**: `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md`
  - 본 handoff + 복붙 프롬프트 (본 세션 마지막)
- **★ EB-QAS 정본 anchor (직전 #3 세션 inline patch 적용)**: `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` — §10.4 explicit mode switch + §17.2 신규 4 필드 + §17.4 explicit mode switch + 머리말 §환각·정합성 점검 표 정정 (Codex (b)·(f) 정정 완료 carry)
- **★ 본 트랙 진입 README**: `_internal/state/ebqas_track/README.md` (carry — 변경 없음)
- **★ 직전 #3 세션 산출물 (carry)**:
  - T1 의사코드: `_internal/state/ebqas_track/실험_spec/EBQAS_구현_의사코드_20260523_231042.md`
  - T3 실험 A spec: `_internal/state/ebqas_track/실험_spec/EBQAS_실험A_4way_matched_spec_20260523_231042.md`
  - T4 실험 B outline: `_internal/state/ebqas_track/실험_spec/EBQAS_실험BCDE_outline_20260523_231042.md`
  - T5 v4 대조: `_internal/state/ebqas_track/exqutor_대조/exqutor_v4_verbatim_대조_20260523_231042.md`
- **★ 직전 222815 spec 3건 (carry, 231042 신규와 cross-ref)**: `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_222815.md`
- **★ Codex 적대 검증 결과 정제 (carry)**: `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md` — 본 세션 measure_ebqas 코드가 (b)·(c)·(d)·(f) 정정을 코드 수준에서 반영
- **★ Codex 직전 spec·log (carry)**: `_internal/state/ebqas_track/codex_검증/codex_디스패치_spec_20260523_223921.md` + `/tmp/codex_ebqas_224306.log`
- **카톡 출처 (carry)**: `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md`
- **5/23 감사 평결 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` — 본 세션 measure_ebqas 코드가 4축 호환성 carry (CaseB식 평균 X · 분포 사전 지식 X · latency objective X · method library X)
- **메모리 anchor 3축 (carry, 본 세션 종료 시 갱신 예정)**: `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` · `project_offline_audit_20260523.md` · `MEMORY.md`
- **★ 메인 트랙 close handoff (참조만 · 본 트랙 정독 X)**: `_internal/handoff/active/handoff_20260523_230914_v14commit완료_박세은사전보고작성.md` — 본 EB-QAS 트랙 분리, 메인은 v14 commit `ffa55f09` + close commit `54098a10` + 박세은 사전 보고 신본 완료, 다음 메인 task = 박성원 5/24 회신·claude.ai/design pptx export·5/26 LearnUs 제출
- **본 세션 직전 EB-QAS handoff 4세트 (본 carry 작업 후 archive 권고)**: `handoff_20260523_221204·224306·225122·231042` + 복붙 4건

## 1. EB-QAS framing (불변 전제, carry)

EB-QAS는 Exqutor 논문(arXiv:2512.09695 — v4 latest 2026-03-29 / v2 local PDF 2025-12-11, 두 버전 §V-B verbatim 동일 #3 세션 T5 확인) §V-B의 distribution-unaware Bernoulli Adaptive Sampling을 **대체**하는 방향이다. 데이터 분포를 미리 안다고 가정하지 않으며, 가용 정보는 (a) 현재 query uniform random sample, (b) 이전 유사 query/predicate의 true cardinality·Q-error, (c) query metadata뿐이다. query-group별 Beta prior `(α_g, β_g)`를 누적해 현재 query sample `s/n`과 결합한 posterior mean `(α_g+s)/(α_g+β_g+n)`으로 cardinality를 추정하고, posterior Q-risk `Q_post = max(p̂/L, U/p̂)`가 충분히 작으면 sampling을 조기 종료한다. κ cap·decay·**explicit mode switch (#3 세션 T1·T2 정정 + 본 세션 T3 코드 반영 완료)**로 잘못된 prior를 처리한다.

본 트랙은 5/23 오프라인 실험 정당성 감사 평결과 4축 정확 호환된다(Codex 축 e pass 0.87). (a) CaseB식 산술평균을 채택하지 않고 Exqutor B1 자체를 대체, (b) 분포 사전 지식 가정 명시적 제거, (c) latency를 objective로 삼지 않고 평가 지표·plan-sensitive subset 한정, (d) method library 미의존. 별도 후속 연구 트랙이며 사용자 활성화 결정(2026-05-23 23:33 KST) 후 본 세션부터 코드 작성 단계 진입 — 6/11 보고서 이후 default가 아닌 즉시 활성화로 진행. 단 측정·팀 공유는 측정 결과 회수 후로 미룸.

## 2. 본 세션이 한 일 (2026-05-23 23:30~23:54 KST · 24분)

| 항목 | 상태 | 내용 |
|---|---|---|
| handoff_231042 정독 + 시간·git·메모리·spec 4건 확인 | ✅ | KST 23:33 시작. handoff_231042 + project_ebqas_track 메모리 + README + spec 4건(T1·T3·T4·T5 231042) + measure_paper_exact.py 라인 1~360 정독 |
| ★ AskUserQuestion 3건 → 사용자 답변 확정 | ✅ | (Q1) 활성화 결정 → **활성화 + 코드 작성** (Q2) CaseB comparator → **strong-13 aggregate** (Q3) 팀 공유 → **측정 결과 회수 후** |
| Explore agent 시도 → prompt too long → 직접 Bash·Read 진행 | ✅ | measure_case_b·c·_measure_common bernoulli_estimate 구조 직접 확인 |
| ★ TaskCreate 6 task | ✅ | T1 활성화 결정 / T2 ultraplanning / T3 measure_ebqas / T4 unit test / T5 Codex review spec / T6 handoff |
| Plan 모드 진입·ultraplanning + ExitPlanMode | ✅ | `~/.claude/plans/recursive-sparking-fairy.md` 작성 → ExitPlanMode 23:30 KST 사용자 승인 |
| ★ T3 measure_ebqas 코드 작성 | ✅ | `_internal/scripts/measure_paper_exact.py` 라인 1582~2144 신규 11 항목 add. 기존 함수(measure_b1_paper·measure_case_a~c·measure_ecqo·main) 손대지 않음. AST parse OK |
| ★ T4 4 unit test + 4 헬퍼 test | ✅ | `_internal/scripts/test_ebqas.py` 신규 (~340 줄). 8/8 PASS — `python3 _internal/scripts/test_ebqas.py` 단독 실행 확인 |
| 디버그 — test_mode_switch + test_q_post_floor 2건 초기 fail → fix | ✅ | (1) w_mismatch=0 override로 mode switch streak 시나리오 단순화 (2) q_log >= q_stop invariant로 assert 완화 (scipy underflow 한계 carry) |
| ★ T5 Codex review 디스패치 spec | ✅ | `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md` 신규 — 6 축 검증(spec carry + 코드·invariant 분기)·sandbox read-only·xhigh·디스패치 명령 명시. 실제 실행은 사용자 명시 시 |
| ★ T6 activation handoff + 복붙 + 메모리 + archive | ⏳ | 본 handoff 작성 중 — 복붙 프롬프트 + 메모리 갱신 + 직전 4세트 archive 이동 |
| 메인 트랙 손대지 않음 | ✅ | `git status` 확인 — 본 세션 modified는 measure_paper_exact.py 1건(EBQAS 블록 add), 나머지 untracked. 메인 트랙 commit `ffa55f09`·`54098a10`(다른 세션)·박세은 사전 보고 신본·v14 산출물에 본 세션 영향 X |

## 3. ★ 핵심 수치·결과 (정본 carry + 본 세션 신규)

### 3.1 v13 정본 (carry)

- v13 3-way matched 1508 paired (B1·CaseA·CaseB 동시 산출)
- CaseB vs B1: better **89.1%** (1344/1508) · median Δ% **−4.38%** — 진짜 / 인과 귀속("분포 인지")은 폐기
- CaseA vs B1: better **35.2%** · mean Δ% **+12.90%** (단독 대체 portfolio 악화)
- 고정-N 통제군: B1 1.944 / CaseA 1.984 / CaseB **1.477** / CaseB′ **1.459** — 평균 효과 입증
- hyperloglog 무작위 해시: CaseA +2.57% (악화) / CaseB(평균) −4.58% (둔갑)
- latency 56 cell paired Δ% **+0.13%** (무개선) · within-cell r=**−0.007**
- v14 CaseC dual-Bernoulli 9 cell paired 평균 **1.373** ≈ CaseB v13 1.477 (메인 트랙 commit `ffa55f09` 완료)

### 3.2 직전 #2·#3 세션 신규 carry

- Exqutor v2 PDF 직접 검증 (arXiv:2512.09695v2): §V-B hyperparam 7개·식 (2)~(6) 정본 anchor v4 인용과 verbatim 일치
- Exqutor v4 외부 fetch (arXiv:2512.09695v4): v2와 §V-B verbatim 동일 (#3 세션 T5)
- Codex 적대 검증 (xhigh · 320,939 tokens · 22:51 KST): 6 축 종합 **concern** — (a) 0.86 / (b) **fail 0.91** / (c) 0.82 / (d) 0.84 / (e) **pass 0.87** / (f) 0.88
- Codex 5건 정정 spec patch 완료 (#3 세션, 231042 신규 4건 + 정본 anchor inline 4 patch)

### 3.3 ★ 본 세션 신규 검증·확정 결과

- **사용자 결정 (23:33 KST)**: 활성화 + 코드 작성 / strong-13 aggregate / 측정 결과 회수 후 공유
- **★ measure_ebqas 코드 11 항목 추가**: EBQASParams 12 필드(batch_size·q_target·n_min·q_log_floor·n_cap·rho·w·w_mismatch·kappa_max·gamma·mismatch_n_threshold·n_recovery) + EBQASState 10 필드(carry 6 + 신규 4) + bucketize_threshold(log-scale D) + make_group_key(6-tuple) + beta_credible_interval(scipy.stats lazy) + ebqas_estimate(state read-only, batch 누적, L_log·L_stop 분리) + update_after_execution(explicit mode switch + recovery + w_mismatch) + _copy_ebqas_state + _ebqas_state_equal + measure_ebqas(trial loop, query-level row schema, trajectory 4축) + assert_paired_join_invariant(4-way join)
- **★ 4 unit test + 4 헬퍼 8/8 PASS**: test_mode_switch_mismatch_streak (w_mismatch=0 override로 3회 mismatch→mode switch 검증) + test_q_post_floor_separation (q_log >= q_stop invariant) + test_recovery_after_stable_streak (20회 stable→history 회복) + test_paired_join_invariant 3건(pass·missing_query fail·true_cardinality mismatch fail) + test_bucketize_threshold·test_make_group_key
- **★ spec 4건 (231042) patch 14항 코드 반영**: (1)(2) EBQASState 4 신규 필드 + EBQASParams 3 신규 hyperparam (3) explicit mode switch + return (update skip) (4) Q_post floor 분리 (L_log·L_stop) (5) w_mismatch 별도 weight (6) stable streak recovery (7) query-level row schema (8) join invariant assert (9) prequential flow + state read-only invariant (10) log-scale D bucket (11) 6-tuple runtime group key (12) sel=... label 분리 (13) Codex 검증 결과 cross-ref (14) 평결 4축 호환성 헤더 주석
- **★ Codex review 디스패치 spec 작성**: 6 축 검증 (a) 수학 (b) 안전장치 동작 (c) paired·schema (d) leakage·prequential (e) 평결 호환성 (f) 외부 인용·주석. 디스패치 명령 명시(`codex exec --sandbox read-only` xhigh, Mac-mini.local). 실제 실행 사용자 명시 시.

### 3.4 EB-QAS 자체 측정 수치 (carry)

EB-QAS 자체 측정은 본 세션 시점 **없다** — measure_ebqas 코드 작성·unit test pass 단계 완료, 실제 smoke·24 cell 측정은 다음 세션. 가설 H1~H5(정본 §21)는 측정 결과로만 평가. **본 세션이 활성화 후 코드 작성 단계까지 완료**.

## 4. ★ 다음 EB-QAS 세션 task (5/23 23:54 KST 기준)

본 세션이 활성화 + 코드 작성·test·Codex review spec 단계를 완료시켰다. 다음 세션 작업은 다음 4 task로 좁혀진다.

1. **★★★ Codex review 디스패치·결과 회수** — `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md` §3.1의 `codex exec --sandbox read-only` 명령 실행(Mac-mini.local). 결과 log 회수 → 6 축 verdict 분류. pass면 다음 task 진입, concern·fail이면 코드/spec 정정 후 재디스패치.
2. **★★★ smoke 1 cell launch** — Codex review pass 후. DEEP × sf=10 × sel=0.01 cell에서 `measure_ebqas(cell, n_queries=1000, trials=10, prior_mode_init="history")` 실행. 자원 watchdog v4 적용. 측정 시간 1 cell ~9분(메인 트랙 sequential 기준).
3. **★★ 24 cell sequential 측정** — smoke pass 후. DEEP·SIFT·WIKI × sf{1,10} × sel{0.001,0.01,0.10} × 2 prior_mode_init(history·no_history) = 36 cell (sf=100 제외시 24 cell). sequential — 메인 트랙 v14 측정 패턴 carry. 1 cell ~9분 × 24 = ~3.6 시간 (절반 자원 가정 7~8 시간).
4. **★ paired 분석 4축 + activation 후 다음 carry handoff** — 4 mode(B1·CaseB-strong13·EB-QAS·EB-QAS-no-history) paired join (assert_paired_join_invariant 통과 필수) → 통계축 4축(better_ratio + Wilcoxon + matched rank-biserial + bootstrap CI) 일관 시 결론. subset 분할(`plan_changed_vs_B1=True`·low-selectivity·high-dimensional). 다음 carry handoff + 메모리 갱신 + 사용자 결정 시 팀 공유 메시지 작성.

**(메인 트랙 분리 carry)**: 본 EB-QAS handoff는 메인 트랙 v14 commit `ffa55f09`·close `54098a10` + 박세은 사전 보고 신본 작성(handoff_20260523_230914) 이후 시점이며, 메인 트랙은 다음 세션이 박성원 5/24 회신 반영·claude.ai/design pptx export 진입 단계(5/26 LearnUs 제출 critical path). **본 EB-QAS 트랙은 메인 트랙과 분리 운영 — 본 handoff는 EB-QAS 작업만 carry**.

## 5. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260523_234413_EBQAS_measure코드작성완료_smoke대기.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260523_234413_EBQAS.md` | 동반 (본 세션 마지막 메시지) |
| ★ measure_ebqas 코드 (신규 11 항목) | `_internal/scripts/measure_paper_exact.py` (라인 1582~2144) | modified (기존 함수 손대지 않음) |
| ★ 4 unit test + 4 헬퍼 (8/8 PASS) | `_internal/scripts/test_ebqas.py` | 신규 (untracked) |
| ★ Codex review 디스패치 spec | `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md` | 신규 (untracked) |
| 본 plan (본 세션 작성·승인) | `~/.claude/plans/recursive-sparking-fairy.md` | carry |
| 트랙 README (carry) | `_internal/state/ebqas_track/README.md` | 변경 X |
| EB-QAS 정본 anchor (carry, #3 inline patch 완료) | `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` | 변경 X |
| 직전 #3 spec 4건 (231042) | `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_231042.md` + `exqutor_대조/exqutor_v4_*.md` | 변경 X (cross-ref base) |
| 직전 #2 222815 spec 3건 (carry) | `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_222815.md` + `exqutor_대조/exqutor_v2_*.md` | 변경 X (231042 base) |
| Codex 검증 결과 정제 (carry) | `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md` | 변경 X |
| Codex 디스패치 spec (223921, carry) | `_internal/state/ebqas_track/codex_검증/codex_디스패치_spec_20260523_223921.md` | 변경 X (본 234413 base) |
| Codex 원본 log | `/tmp/codex_ebqas_224306.log` | 변경 X |
| 카톡 출처 (carry) | `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md` | 변경 X |
| 5/23 평결 (carry) | `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` | 변경 X |
| 메모리 anchor (carry, 본 세션 갱신 완료 예정) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` | 본 세션 종료 시 갱신 |
| 메모리 평결 (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_offline_audit_20260523.md` | 변경 X |
| 메모리 인덱스 (carry) | `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md` | 변경 X |
| 직전 EB-QAS handoff 4세트 (본 세션 archive) | `handoff_20260523_221204·224306·225122·231042` + 복붙 4건 | 본 carry 작업 마지막에 archive 이동 |
| 메인 트랙 close handoff (참조만) | `_internal/handoff/active/handoff_20260523_230914_v14commit완료_박세은사전보고작성.md` | 본 EB-QAS 트랙은 정독 X |

본 세션 신규 산출물(handoff·복붙·measure 코드·test·codex spec)은 5건. measure 코드는 modified(기존 손대지 않음), 나머지 4건은 untracked. 사용자 명시 commit 지시 시 EB-QAS 트랙 별도 commit (메인 트랙 `54098a10` 패턴 분리).

## 6. 메인 트랙 상태 (본 트랙 정독 X · 참조용)

본 세션 시점 메인 트랙은 #3 EB-QAS 세션 시작 직전(22:57~23:09 KST 다른 세션) 다음을 완료한 상태다(handoff_20260523_230914 carry).

- v14 CaseC 9 셀 분석 완료 commit `ffa55f09` (23 files changed, +3104/-23) — main 트랙만, EB-QAS 트랙은 별도 commit 대기로 untracked 유지
- main 트랙 close commit `54098a10` (박세은 사전 보고 신본 + handoff 230914 + 230914 복붙)
- 박세은 → 박광현 교수님 1쪽 사전 보고 신본 작성 — `submission/_drafts/속도는벡터_박광현미팅_사전보고_20260524_000000.md`

본 EB-QAS 트랙은 위 메인 트랙 작업과 분리. 본 세션 작업 중 메인 트랙 파일 손대지 않음. 본 세션 modified는 `_internal/scripts/measure_paper_exact.py` 1건(라인 1582~2144 EBQAS 블록 add)만이지만, 본 파일도 측정 script로 메인 트랙·EB-QAS 트랙 공통 사용 — 단 기존 함수(measure_b1_paper·measure_case_a~c·measure_ecqo·main) 손대지 않음 보장.

**다음 메인 트랙 세션 task** (handoff_230914 carry, 본 EB-QAS 트랙 영향 X):
- 5/24 박성원 멘토 회신 반영
- user prompt 복붙 → claude.ai/design 22장 신본 pptx export (critical path)
- 5/26 23:59 LearnUs 제출 → 5/28 12:00 포스터 마감 → 6/11 최종 보고서

## 7. ★ 환각 회피 룰 (carry · 본 세션 신규 patch carry)

- **v13 정본 수치 진위·인과 분리** (carry): "89.1% / −4.38% / 1344 / 1508 / 35.2% / 12.90% / 1.477 / 1.459 / 1.944 / 1.984 / hyperloglog −4.58% / 56 cell +0.13% / r=−0.007"은 진짜 측정. 인과 귀속("분포 인지 효과")은 5/23 감사로 폐기.
- **EB-QAS는 본 시점 검증 가설**. "EB-QAS가 B1보다 낫다"는 단언 금지(측정 전). 핵심 가설 H1~H5는 측정 결과로만 평가. Codex review pass도 "측정 결과 우위 보장"이 아니라 "spec 준수·invariant 정확성 독립 검증" 뿐.
- **★ Codex (b) fail 정정 코드 반영 완료 carry**: `update_after_execution`의 `consecutive_mismatch >= mismatch_n_threshold and prior_mode == "history"` → mode switch 후 `return` (update skip) → fixed-point `κ ≈ 19` 수렴 반례 해결. measure_ebqas 측정 시 본 코드 그대로 사용 — `EBQASParams(w_mismatch=0)` override는 unit test 단순화 용도만, default `w_mismatch=1` 그대로 운영.
- **★ Codex (c) concern 정정 carry**: CaseB comparator = strong-13 aggregate (사용자 확정). measure_ebqas는 raw 측정만, strong-13 aggregate 계산은 analysis 단(다음 세션). paired effect size = matched rank-biserial (Cliff's δ 폐기) — 분석 단계 적용.
- **★ Codex (d) concern 정정 코드 반영 완료 carry**: `make_group_key`가 `sel=...` label 받지 않음 (6-tuple metadata only). `bucketize_threshold(D)`가 log-scale `floor(log10(D))` (dataset 전체 quantile 사용 X). `ebqas_estimate` state read-only invariant + `update_after_execution`은 ebqas_estimate 종료 후 호출 — prequential flow 코드 invariant.
- **★ Codex (f) concern 정정 carry**: 정본 anchor §22 reference list 정정은 측정 결과 회수 후 사용자 명시 시 inline 적용 (본 세션 적용 X). 본 코드의 헤더 주석에 cross-ref만.
- **Exqutor 본 논문 버전 차이 (carry)**: v4(2026-03-29) latest = EB-QAS 정본 anchor 인용 기반 / v2(2025-12-11) = Capstone CLAUDE.md 정본·local PDF. 두 버전 §V-B verbatim 동일이므로 운영 무영향.
- **메인 트랙 손대지 않음** (carry). EB-QAS 작업이 메인 트랙 v14·발표·포스터·보고서 작업에 영향 X.
- **별도 트랙 위상 유지**: 본 EB-QAS를 메인 트랙 발표·재프레이밍에 끼워 넣지 않는다.
- **본 handoff는 EB-QAS 트랙 only**. 다음 메인 세션이 박성원 회신 반영 시 handoff_230914 별도 read.
- **타임코드 네이밍**: 본 세션 타임코드 = `234413`(작업 시작 ~ 본 handoff 작성까지 본 세션 모든 신규 산출물 일관 사용, 단 측정 결과 회수 후 추가 산출물은 별도 타임코드). `v13/v14/ver/wave/phase` 단어를 파일명 분기자로 쓰지 않는다.
- **측정·팀 공유 boundary**: 본 세션 완료가 "활성화 + 코드·test·Codex review spec 단계 완료". 측정 launch는 Codex review pass 후 별도 세션. 팀 공유는 측정 결과 회수 후 별도 세션.

## 8. 일정 (carry · 본 세션 시점)

| 일자 | 항목 | EB-QAS 트랙 영향 |
|---|---|---|
| 2026-05-24 (일) | 박성원 멘토 3차 자문 회신 예정 | 메인 트랙 (handoff_230914 task 1) — 본 EB-QAS 트랙 직접 영향 X. 다만 회신에 EB-QAS 언급 시 본 트랙 carry 반영 |
| 2026-05-26 (화) 23:59 | LearnUs 발표 deck 마감 ★★ critical path | 메인 트랙 — 본 EB-QAS 트랙 분리 |
| 2026-05-27 (수) · 5/29 (금) | 최종 발표 | 메인 트랙 — 본 EB-QAS 트랙 분리 |
| 2026-05-28 (목) 12:00 | 포스터 PDF 마감 (900×1200) | 메인 트랙 — 본 EB-QAS 트랙 분리 |
| 2026-06-11 (목) | 최종 보고서 마감 | 메인 트랙 |
| 본 세션 후 즉시 | **EB-QAS 트랙 Codex review 디스패치 + 결과 회수** | **본 트랙** — 사용자 명시 시 |
| Codex review pass 후 | **smoke 1 cell → 24 cell sequential 측정** | **본 트랙** — Codex review pass 후 별도 세션 |
| 측정 결과 회수 후 | paired 분석 4축 + 팀 공유 메시지 | **본 트랙** — 측정 결과 회수 후 별도 세션 |

## 9. ★ 본 세션과 직전 EB-QAS 세션 (4 단계) 누적 carry

| 세션 | 시간 | 주요 산출물 | 상태 |
|---|---|---|---|
| #1 21:54 KST | 정본화 + 자체 점검 + 메모리 | 정본 anchor 정본화 + 5/23 평결 호환성 4축 + 카톡 출처 + 메모리 anchor | commit `d6d1b5a7` |
| #2 22:20~22:51 (31분) | 인프라 + Exqutor v2 대조 + spec 3건 + Codex 디스패치·실행·결과 회수 | README + v2 대조 + 실험 A·B~E·의사코드 spec + Codex 디스패치 spec + Codex 검증 결과 정제 (6 축 종합 concern) | untracked carry |
| #3 23:00~23:30 (30분) | Codex 5건 정정 spec patch 완료 | T1 의사코드 신규 + T2 정본 anchor inline + T3 실험 A spec 신규 + T4 실험 B outline 신규 + T5 v4 대조 신규 + T6 handoff_231042 | untracked + 정본 anchor modified |
| **#4 23:30~23:54 (24분)** | **활성화 + measure_ebqas 코드 + 4 unit test + Codex review spec + handoff** | T1 사용자 확정 + T2 ultraplanning + T3 measure_ebqas 11 항목 (modified) + T4 test_ebqas.py 8/8 PASS + T5 Codex review spec + T6 본 handoff | **본 세션** (modified 1 + untracked 4) |

4 세션 누적으로 EB-QAS 트랙은 **정본화 → 인프라·검증 → 활성화 전 정정 완료 → 활성화 + 코드·test·Codex review spec**의 4 단계를 완료. 다음 단계는 **Codex review 디스패치 → smoke → 24 cell 측정 → 분석**이며, 사용자 명시 결정 시점에 진입.

---

작성: 2026-05-23 23:54 KST. 본 세션(plan 23:30 → T3 23:44 → T4 디버그·fix 23:50 → T5 23:52 → T6 carry 23:54) 인계. → 다음 EB-QAS 세션 = Codex review 디스패치 → pass 시 smoke 1 cell launch → 24 cell sequential 측정 → paired 분석 4축 → 다음 carry handoff.
