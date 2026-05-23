# handoff 20260524 00:20 — EB-QAS Codex measure_ebqas review 결과 회수 완료, **concern 분기(4.B) 정정 plan 작성 carry**

> 본 handoff = EB-QAS 별도 트랙 **다섯 번째 세션**의 최종 인계 anchor (2026-05-24 00:03~00:20 KST · 17분). 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 #5 세션은 직전 #4 handoff_20260523_234413에서 carry된 4 task(Codex review 디스패치·결과 회수·6 축 verdict 분류·다음 carry handoff)를 완료. measure_ebqas 코드 + 4 unit test에 대한 Codex xhigh 6 축 적대 검증을 디스패치(`codex exec --sandbox read-only`, prompt file + stdin /dev/null, Mac-mini.local, session `019e5565-fab1`) → 8분 후 정상 종료(exit 0) → 결과 회수 → **종합 verdict = concern** (fail 0건, concern 4건 a·b·c·d, pass-with-concern 1건 e, pass 1건 f). 6 축 = (a) 수학 concern 0.86 `n_cap`·`q_log_floor`·`gamma` dead param / (b) 안전장치 **fail→concern** 0.82 `no_history`가 실제로 history 끄지 못함 / (c) paired concern 0.78 invariant key 약함·4-way fallback 2-mode / (d) leakage concern 0.84 `template_id=q_row_idx` cold-start risk / (e) 평결 호환성 pass-with-concern 0.87 / (f) 외부 인용 pass 0.90. Codex 결론: **smoke 1 cell은 함수 호출 진행 가능, 24 cell sequential 측정 진입 전에는 (a)(b)(c) 3건 필수 정정**. 결과 정제는 `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md`. **다음 EB-QAS 세션 task = 4.B 정정 plan 작성 → 코드 정정 6 항목(우선순위 1~3) → 재디스패치 또는 smoke 단독 launch**. 메인 트랙(handoff_20260523_230914 박성원 5/24 회신·5/26 LearnUs critical path)은 본 세션 손대지 않음.

## 0. 정본·진입점

- **★ 본 handoff** — 본 문서 한 장으로 EB-QAS 트랙 #5 인계. self-contained.
- **★ 본 #5 plan**: `~/.claude/plans/vectorized-tickling-boole.md` (ExitPlanMode 00:09 KST 사용자 승인 — Recommended 옵션 = 디스패치 + 결과까지 본 세션)
- **★ Codex review 결과 정제 (본 세션 신규)**: `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md` — Codex log를 verbatim carry + 6 축 verdict 표·각 축 finding·정정 권고·신뢰도 정제
- **★ Codex log 원본**: `/tmp/codex_ebqas_review_001021.log` — codex exec `-o` 출력 파일
- **★ Codex 디스패치 spec (본 review base, carry)**: `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md`
- **★ 직전 #4 measure_ebqas 코드 (review 1차 대상, carry)**: `_internal/scripts/measure_paper_exact.py` (라인 1582~2144)
- **★ 직전 #4 4 unit + 4 헬퍼 test (review 2차 대상, carry)**: `_internal/scripts/test_ebqas.py` (417 lines, 8/8 PASS)
- **★ EB-QAS 정본 anchor (#3 inline patch 적용, carry)**: `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md`
- **★ #3 spec 4건 (231042, carry)**: `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_231042.md` + `exqutor_대조/exqutor_v4_verbatim_대조_20260523_231042.md`
- **★ 직전 #2 6 축 검증 결과 정제 (carry, 본 review base 비교 대상)**: `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md`
- **★ 트랙 README (carry)**: `_internal/state/ebqas_track/README.md`
- **★ 5/23 평결 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md`
- **★ 카톡 출처 (carry)**: `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md`
- **★ 메모리 anchor (carry, 본 세션 종료 시 갱신)**: `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` · `project_offline_audit_20260523.md` · `MEMORY.md`
- **★ 메인 트랙 close handoff (참조만 · 본 트랙 정독 X)**: `_internal/handoff/active/handoff_20260523_230914_v14commit완료_박세은사전보고작성.md` — 본 EB-QAS 트랙 분리, 메인은 v14 commit `ffa55f09` + close commit `54098a10` + 박세은 사전 보고 신본 완료
- **★ 직전 #4 handoff (본 세션 마지막 archive)**: `_internal/handoff/active/handoff_20260523_234413_EBQAS_measure코드작성완료_smoke대기.md` + `새세션_복붙_프롬프트_20260523_234413_EBQAS.md`

## 1. EB-QAS framing (불변 전제, carry)

EB-QAS는 Exqutor 논문(arXiv:2512.09695 — v4 latest 2026-03-29 / v2 local PDF 2025-12-11, 두 버전 §V-B verbatim 동일 #3 세션 T5 확인) §V-B의 distribution-unaware Bernoulli Adaptive Sampling을 **대체**하는 방향이다. 데이터 분포를 미리 안다고 가정하지 않으며, 가용 정보는 (a) 현재 query uniform random sample, (b) 이전 유사 query/predicate의 true cardinality·Q-error, (c) query metadata뿐이다. query-group별 Beta prior `(α_g, β_g)`를 누적해 현재 query sample `s/n`과 결합한 posterior mean `(α_g+s)/(α_g+β_g+n)`으로 cardinality를 추정하고, posterior Q-risk `Q_post = max(p̂/L, U/p̂)`가 충분히 작으면 sampling을 조기 종료한다. κ cap·decay·**explicit mode switch (#3 세션 T1·T2 정정 + #4 세션 T3 코드 반영 + 본 #5 세션 Codex review 검증)**로 잘못된 prior를 처리한다.

본 트랙은 5/23 오프라인 실험 정당성 감사 평결과 4축 정확 호환된다(Codex 축 e pass 0.87, #2 세션). (a) CaseB식 산술평균을 채택하지 않고 Exqutor B1 자체를 대체, (b) 분포 사전 지식 가정 명시적 제거, (c) latency를 objective로 삼지 않고 평가 지표·plan-sensitive subset 한정, (d) method library 미의존. 별도 후속 연구 트랙이며 사용자 활성화 결정(2026-05-23 23:33 KST) 이후 #4 세션부터 코드 작성 단계 진입, 본 #5 세션이 Codex 독립 검증을 통과·정정 단계.

## 2. 본 #5 세션이 한 일 (2026-05-24 00:03~00:20 KST · 17분)

| 항목 | 상태 | 내용 |
|---|---|---|
| handoff_234413 정독 + KST 시각·git·환경 검증 | ✅ | KST 00:03 시작. Mac-mini.local 확인, codex 0.132.0 Logged in, spec·코드·test 모두 존재, test 8/8 PASS 재현 |
| TaskCreate 6 task | ✅ | T1 환경 검증 / T2 ultraplan + ExitPlanMode / T3 Codex 디스패치 / T4 결과 회수·분류 / T5 verdict 분기 / T6 carry handoff |
| Plan 모드 진입·ultraplanning + ExitPlanMode | ✅ | `~/.claude/plans/vectorized-tickling-boole.md` 작성 → AskUserQuestion 본 세션 진행 범위 확인 (Recommended = 디스패치 + 결과까지 본 세션) → ExitPlanMode 00:09 KST 사용자 승인 |
| ★ Codex review 디스패치 | ✅ | 1차 시도(heredoc command substitution) → "Reading additional input from stdin..." 에서 stuck → TaskStop. 2차 시도 = prompt 파일(/tmp/codex_review_prompt_001021.txt) + `< /dev/null` stdin 차단 → background ID `b3sr3u3i6` launch (00:11 KST). session id `019e5565-fab1-79a2-ad9a-a214a254c288`. xhigh + gpt-5.5 + sandbox read-only |
| Codex 정상 종료 알림 수신 | ✅ | 00:19 KST 알림 (exit 0, 8분 소요). codex log 파일 8,573 B / 64 lines, task stdout stream 369,275 B / 4,956 lines |
| ★ Codex 결과 회수 | ✅ | log 파일 Read → 종합 verdict = **concern** 추출. 6 축 각 verdict + finding + 정정 권고 + 신뢰도 모두 verbatim 추출. Codex 결론 = "smoke 1 cell은 함수 호출 진행 가능, 24 cell 진입 전 (a)(b)(c) 3건 필수 정정" |
| ★ 6 축 verdict 분류 + 결과 정제 .md 작성 | ✅ | `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md` 신규 작성 — Codex log verbatim §3-§8 carry + 6 축 verdict 표 §1 + 우리 해석·분기 권고 §10 분리 + #2(225122) 비교 §11 |
| ★ Verdict 분기 결정 | ✅ | **concern 분기 (4.B)** — fail 0건이지만 concern 축 4건(a·b·c·d)이므로 4.A pass 분기 불가. concern 4건은 plan 분기 표 "1-3 축 concern"에서 초과하지만 fail 0이므로 4.B 선정. Codex 결론 hybrid (smoke OK + 24 cell 전 정정 필수) carry |
| ★ 본 handoff 최종화 + 복붙 + 메모리 + archive | ✅ | 본 handoff verdict placeholder 채움, 복붙 프롬프트 verdict별 분기 정리, 메모리 5세션 누적 표 갱신, 직전 #4 handoff 4세트 archive 이동, /tmp codex log·prompt를 `_internal/state/ebqas_track/codex_검증/`으로 backup |
| 메인 트랙 손대지 않음 | ✅ | `git status` 확인 — 본 세션 modified는 0건(메인 repo 기준 신규 파일 = handoff·복붙·결과 정제·prompt backup·log backup 5건만, 모두 EB-QAS 트랙). 메인 트랙 v14·발표·포스터·보고서 무영향 |

## 3. ★ 핵심 수치·결과 (정본 carry + 본 세션 신규)

### 3.1 v13 정본 (carry)

- v13 3-way matched 1508 paired (B1·CaseA·CaseB 동시 산출)
- CaseB vs B1: better **89.1%** (1344/1508) · median Δ% **−4.38%** — 진짜 / 인과 귀속("분포 인지")은 폐기
- CaseA vs B1: better **35.2%** · mean Δ% **+12.90%** (단독 대체 portfolio 악화)
- 고정-N 통제군: B1 1.944 / CaseA 1.984 / CaseB **1.477** / CaseB′ **1.459** — 평균 효과 입증
- hyperloglog 무작위 해시: CaseA +2.57% (악화) / CaseB(평균) −4.58% (둔갑)
- latency 56 cell paired Δ% **+0.13%** (무개선) · within-cell r=**−0.007**
- v14 CaseC dual-Bernoulli 9 cell paired 평균 **1.373** ≈ CaseB v13 1.477 (메인 트랙 commit `ffa55f09`)

### 3.2 직전 #2·#3·#4 세션 carry

- Exqutor v2 PDF 직접 검증 (arXiv:2512.09695v2): §V-B hyperparam 7개·식 (2)~(6) verbatim 일치
- Exqutor v4 외부 fetch (arXiv:2512.09695v4): v2와 §V-B verbatim 동일 (#3 세션 T5)
- Codex 적대 검증 #2 (xhigh · 320,939 tokens · 22:51 KST): 6 축 종합 **concern** — (a) 0.86 / (b) **fail 0.91** / (c) 0.82 / (d) 0.84 / (e) **pass 0.87** / (f) 0.88
- Codex 5건 정정 spec patch 완료 (#3 세션, 231042 신규 4건 + 정본 anchor inline 4 patch)
- #4 measure_ebqas 코드 11 항목 + test 8/8 PASS

### 3.3 ★ 본 #5 세션 신규 검증 결과

- **★ Codex review 메타**: session id `019e5565-fab1-79a2-ad9a-a214a254c288`, log size 8,573 B (64 lines), task stdout 369,275 B (4,956 lines, 메모리·chronicle 분석 단계 포함), 실행 시간 ~8분(00:11~00:19 KST), exit code 0.
- **★ 종합 verdict**: **concern** (fail 0건, concern 4건, pass-with-concern 1건, pass 1건).
- **★ 6 축 verdict 표**:

| 축 | verdict | 신뢰도 | 핵심 finding 1줄 요약 |
|---|---|---|---|
| (a) 수학·산술 정확성 | **concern** | 0.86 | `EBQASParams.n_cap`이 dead param — `ebqas_estimate`가 `state.n_cap`만 사용. `q_log_floor`·`gamma`도 미반영, `q_log_floor` 주석 "inf 대신 사용" verbatim 위배 |
| (b) 안전장치 동작 | **concern** | 0.82 | explicit mode switch 자체는 구현 OK이나 **`no_history`가 실제로 history를 끄지 못함** — `ebqas_estimate`/`update_after_execution` 모두 prior_mode 무관하게 alpha/beta 사용·갱신. `EB-QAS-no-history` = "no-early-stop history posterior"에 가까움 |
| (c) paired 비교 통제·schema | **concern** | 0.78 | `assert_paired_join_invariant` key가 `(trial_idx, query_idx)`만 — cell·seed 미검증, `true_cardinality`도 1건만 비교. B1·CaseB schema 없으면 2-mode fallback인데 "4-way paired invariant 통과" 단언 X. 로컬 probe에서 B1 true-card mismatch·seed mismatch·cell mismatch 모두 통과 |
| (d) leakage 방지·prequential invariant | **concern** | 0.84 | read-only state·after-execution update 순서 prequential 원칙 OK. group key log-scale D bucket leakage 방지 pass. 단 `template_id=q_row_idx`(measure_paper_exact.py:1940)가 query identity면 history 누적 X (cold-start) — leakage 아니지만 EB-QAS 본의 약화 |
| (e) 5/23 평결 4축 호환성 | **pass-with-concern** | 0.87 | CaseB식 `(est_b1+est_method)/2` 없음, method library 미의존, latency 필드 없음 — 평결 호환. 단 `EB-QAS-no-history` label이 (b)와 같은 사유로 의미 불일치 |
| (f) Exqutor 인용·코드 주석 verbatim | **pass** | 0.90 | spec path·정본 anchor cross-ref·환각 회피 룰 정확. v2/v4 §V-B 동일성 OK. 단 stale param 주석(`q_log_floor`·`gamma`) 정리 권고 |

- **★ 정정 권고 통합** (우선순위별 6 항목, 결과 정제 .md §10.2 carry):
  1. (a) 우선순위 1 — `params.n_cap`을 state 생성 시 주입 또는 파라미터에서 제거. 회귀 test (`test_n_cap_param_honored`) 추가
  2. (b) 우선순위 1 — `prior_mode=="no_history"`일 때 추정 prior를 Beta(1,1)로 고정 또는 update를 shadow/recovery counter로 분리. 회귀 test (`test_no_history_keeps_alpha_beta_neutral`) 추가
  3. (c) 우선순위 1 — invariant key를 `(cell, trial_idx, seed, query_idx 또는 query_id)`로 확장 + 모든 mode 모든 row에서 true_cardinality 비교. B1/CaseB schema 확장 전에는 결과 문구를 "EB-QAS 2-mode invariant"로 낮춤
  4. (d) 우선순위 2 — smoke 결과에 `n_groups / n_queries`를 launch gate로 기록. 24 cell 전 `q_row_idx` template/query identity 확정
  5. (e) 우선순위 3 — no-history 의미 코드 보장 또는 label을 `EB-QAS-no-stop`류로 변경 ((b) 정정 시 자동 해결)
  6. (f) 우선순위 3 — 헤더 유지 + dead/stale param 주석만 정리

- **★ Codex 종합 결론 (verbatim)**: "결론적으로 smoke 1 cell은 직접 함수 호출 기준으로 진행 가능하지만, **24 cell sequential 측정 진입 전에는 `params.n_cap`, `no_history` 의미, paired invariant 3건은 고치는 편이 맞습니다.** 특히 4-way paired invariant는 현재 테스트가 주장하는 만큼 강하지 않습니다."

- **★ #2(225122) vs #5(001021) 비교** (결과 정제 .md §11 carry):
  - (b) **fail 0.91 → concern 0.82** 개선 (explicit mode switch + return update skip 정정 효과 — fixed-point κ≈19 반례 해결)
  - (f) **concern 0.88 → pass 0.90** 개선 (#3 v4 외부 fetch + 12 entry clean source map 효과)
  - (a)(c)(d) 신뢰도 동일하거나 -0.04, finding 변경 — spec patch (#3) 해결분 + 코드 단계 신규 발견 (dead param·invariant key 약함·cold-start)
  - (e) 동일 (pass-with-concern, no-history label 잔존)

- **★ 결과 정제 .md 상세**: `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md` 참조 — 각 축 finding 3건·정정 권고 1-3건·신뢰도·verbatim 인용 보존.

### 3.4 EB-QAS 자체 측정 수치 (carry)

EB-QAS 자체 측정은 본 세션 시점 **없다** — measure_ebqas 코드 작성·unit test pass·Codex review 단계 완료. 실제 smoke·24 cell 측정은 본 review pass 후 별도 세션. 가설 H1~H5(정본 §21)는 측정 결과로만 평가.

## 4. ★ 다음 EB-QAS 세션 task — **concern 분기 (4.B) 진입**

본 #5 세션 Codex review 결과 = **종합 verdict concern** (fail 0, concern 4 a·b·c·d, pass-with-concern 1 e, pass 1 f). plan 분기 표 기준 4.A pass 분기는 minor concern≤1 조건이라 부적합. fail 0이므로 4.C fail 분기도 부적합. **4.B concern 분기 진입이 정합**. 단 Codex 결론 hybrid (smoke OK + 24 cell 전 정정 필수)이므로 4.B 안에서도 smoke 단독 launch가 함수 호출 기준 가능.

### 4.B 진행 task 카드 (다음 세션 진입 = 본 우선순위 순서)

1. **★★★ 정정 plan 작성** — `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md` §3-§8 각 축 finding 정독 → 정정 plan `~/.claude/plans/<slug>.md` 작성 → ExitPlanMode 승인. plan 구조: 6 항목(우선순위 1~3) × (대상 파일·라인·정정 방향·회귀 test·검증). 본 plan 작성 시 spec 정정도 필요 시 동반(`EBQAS_*_20260523_231042.md` patch).
2. **★★★ 코드/spec 정정 진행 (우선순위 1 — 3 항목)**:
   - (a) `params.n_cap` honor: `_internal/scripts/measure_paper_exact.py:1700` `ebqas_estimate`에서 `state.n_cap` → `params.n_cap` (또는 state init 시 params.n_cap 주입). 회귀 test `test_n_cap_param_honored` 추가
   - (b) `no_history` 의미 코드 보장: `ebqas_estimate`(라인 1725)에서 `state.prior_mode=="no_history"` 분기 시 `alpha=beta=1.0` 임시 override 또는 `update_after_execution`(라인 1812)에서 `no_history` 시 update skip. 회귀 test `test_no_history_keeps_alpha_beta_neutral` 추가
   - (c) `assert_paired_join_invariant`(라인 2090) key 확장 `(cell, trial_idx, seed, query_idx)` + 모든 mode 모든 row true_cardinality 비교. 또는 B1/CaseB schema 확장 (query_results 도입). 후자가 더 깔끔하지만 cost 큼 — plan 작성 시 선택
3. **★★ 코드 정정 진행 (우선순위 2 — 1 항목)**:
   - (d) smoke 시 `n_groups / n_queries` launch gate 기록. `q_row_idx`(라인 1940) template vs query identity 명시 (현재 `q_row_idx = q_idx % len(qp)`는 query identity 패턴)
4. **★★ 코드 정정 진행 (우선순위 3 — 2 항목)**:
   - (e) (b) 정정 시 자동 해결 또는 `EB-QAS-no-history` label을 `EB-QAS-no-stop`으로 변경
   - (f) `q_log_floor`·`gamma` dead param 정리: 실제 로직 반영 또는 명시 제거 + 주석 갱신
5. **★ 정정 후 본 review 재디스패치** — 같은 spec(`codex_measure_ebqas_review_spec_20260523_234413.md` 또는 본 세션 정정 spec) 사용 → 새 log path `/tmp/codex_ebqas_review_<HHMMSS>.log` → 결과 회수·분류 → pass면 본 §4.A 진입
6. **★ 또는 smoke 단독 launch (병행 OK)** — Codex 결론 "smoke 1 cell은 함수 호출 진행 가능"이므로 EB-QAS mode 단독 smoke (DEEP × sf=10 × sel=0.01)는 정정 완료 전 launch 가능. 단 `EB-QAS-no-history` mode 비교는 정정 후로 미룸. smoke 결과로 `n_groups / n_queries` (d) launch gate 사전 확보 가능

### 4.A pass 분기 (참조용 — 본 세션 미적용)

정정 후 재디스패치에서 6 축 모두 pass 시 진입. carry:
1. smoke 1 cell launch (DEEP × sf=10 × sel=0.01, n_queries=1000, trials=10, prior_mode_init="history"). 1 cell ~9분
2. 24 cell sequential 측정 (DEEP·SIFT·WIKI × sf{1,10} × sel{0.001,0.01,0.10} × 2 prior_mode_init = 36 cell, sf=100 제외시 24 cell). 1 cell ~9분 × 24 = ~3.6 시간
3. paired 분석 4축 (better_ratio + Wilcoxon + matched rank-biserial + bootstrap CI) + subset 분할 → 다음 carry handoff + 팀 공유

### 4.C fail 분기 (참조용 — 본 세션 미적용)

본 review 재디스패치에서 fail 발견 시 진입. 코드 즉시 fix + spec 재작성 + 재디스패치.

**(메인 트랙 분리 carry)**: 본 EB-QAS handoff는 메인 트랙 v14 commit `ffa55f09`·close `54098a10` + 박세은 사전 보고 신본 작성(handoff_20260523_230914) 이후 시점이며, 메인 트랙은 다음 세션이 박성원 5/24 회신 반영·claude.ai/design pptx export 진입 단계(5/26 LearnUs 제출 critical path). **본 EB-QAS 트랙은 메인 트랙과 분리 운영 — 본 handoff는 EB-QAS 작업만 carry**.

## 5. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260524_001021_EBQAS_codexreview결과_concern_정정필요.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260524_001021_EBQAS.md` | 동반 |
| ★ Codex review 결과 정제 (본 세션 신규) | `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md` | 신규 (untracked) |
| Codex log 원본 | `/tmp/codex_ebqas_review_001021.log` | /tmp (휘발성, 본 세션 종료 후 backup 권고 — `cp /tmp/codex_ebqas_review_001021.log _internal/state/ebqas_track/codex_검증/codex_review_log_001021.txt`) |
| Codex prompt 파일 | `/tmp/codex_review_prompt_001021.txt` | /tmp (휘발성, backup 권고) |
| ★ 본 #5 plan | `~/.claude/plans/vectorized-tickling-boole.md` | carry |
| ★ 직전 #4 코드 본진 (review 1차 대상) | `_internal/scripts/measure_paper_exact.py` (라인 1582~2144) | carry (변경 X) |
| ★ 직전 #4 test (review 2차 대상) | `_internal/scripts/test_ebqas.py` (8/8 PASS) | carry (변경 X) |
| ★ Codex review 디스패치 spec | `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md` | carry (변경 X) |
| 트랙 README | `_internal/state/ebqas_track/README.md` | carry (변경 X) |
| EB-QAS 정본 anchor | `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` | carry (변경 X) |
| #3 spec 4건 (231042) | `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_231042.md` + `exqutor_대조/exqutor_v4_*.md` | carry (변경 X) |
| 직전 #2 222815 spec 3건 | `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_222815.md` + `exqutor_대조/exqutor_v2_*.md` | carry (변경 X) |
| Codex 직전 검증 결과 정제 | `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md` | carry (변경 X) |
| Codex 직전 디스패치 spec | `_internal/state/ebqas_track/codex_검증/codex_디스패치_spec_20260523_223921.md` | carry (변경 X) |
| Codex 직전 log | `/tmp/codex_ebqas_224306.log` (460KB, 4995 lines) | carry (변경 X) |
| 카톡 출처 | `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md` | carry (변경 X) |
| 5/23 평결 | `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` | carry (변경 X) |
| 메모리 anchor | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` | 본 세션 종료 시 갱신 |
| 메모리 평결 | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_offline_audit_20260523.md` | 변경 X |
| 메모리 인덱스 | `~/.claude/projects/-Users-hyunbin-Capstone/memory/MEMORY.md` | 변경 X (project_ebqas_track 인덱스 기존) |
| 직전 #4 handoff | `_internal/handoff/active/handoff_20260523_234413_EBQAS_*.md` + 복붙 | 본 carry 작업 마지막에 archive 이동 |
| 메인 트랙 close handoff (참조만) | `_internal/handoff/active/handoff_20260523_230914_v14commit완료_박세은사전보고작성.md` | 본 EB-QAS 트랙은 정독 X |

본 세션 신규 산출물 = handoff·복붙·결과 정제 .md 3건 (모두 untracked). measure_paper_exact.py·test_ebqas.py·spec 4건은 모두 변경 X (review 대상이고 코드 수정은 verdict별 분기 시 다음 세션). 사용자 명시 commit 지시 시 본 EB-QAS 트랙 별도 commit.

## 6. 메인 트랙 상태 (본 트랙 정독 X · 참조용)

본 #5 세션 시점 메인 트랙 상태는 직전 #4 handoff_20260523_234413와 동일 (본 #5 세션은 메인 트랙 손대지 않음).

- v14 CaseC 9 셀 분석 완료 commit `ffa55f09` (23 files changed, +3104/-23) — main 트랙
- main 트랙 close commit `54098a10` (박세은 사전 보고 신본 + handoff 230914 + 230914 복붙)
- 박세은 → 박광현 교수님 1쪽 사전 보고 신본 — `submission/_drafts/속도는벡터_박광현미팅_사전보고_20260524_000000.md`

**다음 메인 트랙 세션 task** (handoff_230914 carry, 본 EB-QAS 트랙 영향 X):
- 5/24 박성원 멘토 회신 반영
- user prompt 복붙 → claude.ai/design 22장 신본 pptx export (critical path)
- 5/26 23:59 LearnUs 제출 → 5/28 12:00 포스터 마감 → 6/11 최종 보고서

## 7. ★ 환각 회피 룰 (carry · 본 #5 세션 신규 patch carry)

- **v13 정본 수치 진위·인과 분리** (carry): "89.1% / −4.38% / 1344 / 1508 / 35.2% / 12.90% / 1.477 / 1.459 / 1.944 / 1.984 / hyperloglog −4.58% / 56 cell +0.13% / r=−0.007"은 진짜 측정. 인과 귀속("분포 인지 효과")은 5/23 감사로 폐기.
- **EB-QAS는 본 시점 검증 가설**. "EB-QAS가 B1보다 낫다"는 단언 금지(측정 전). 핵심 가설 H1~H5는 측정 결과로만 평가. **본 Codex review pass도 "측정 결과 우위 보장"이 아니라 "spec 준수·invariant 정확성 독립 검증" 뿐**.
- **★ Codex review 결과 인용 시 verbatim**: 본 handoff §3.3·결과 정제 .md에서 Codex 결과를 인용할 때 verbatim. 우리 해석을 verdict로 surrogate 금지.
- **★ Codex (b) fail 정정 코드 반영 carry**: `update_after_execution`의 `consecutive_mismatch >= mismatch_n_threshold and prior_mode == "history"` → mode switch 후 `return` (update skip) → fixed-point `κ ≈ 19` 수렴 반례 해결. measure_ebqas 측정 시 본 코드 그대로 사용 — `EBQASParams(w_mismatch=0)` override는 unit test 단순화 용도만, default `w_mismatch=1` 그대로 운영.
- **★ Codex (c) concern 정정 carry**: CaseB comparator = strong-13 aggregate (사용자 확정). measure_ebqas는 raw 측정만, strong-13 aggregate 계산은 analysis 단(다음 세션). paired effect size = matched rank-biserial (Cliff's δ 폐기) — 분석 단계 적용.
- **★ Codex (d) concern 정정 코드 반영 carry**: `make_group_key`가 `sel=...` label 받지 않음 (6-tuple metadata only). `bucketize_threshold(D)`가 log-scale `floor(log10(D))` (dataset 전체 quantile 사용 X). `ebqas_estimate` state read-only invariant + `update_after_execution`은 ebqas_estimate 종료 후 호출 — prequential flow 코드 invariant.
- **★ Codex (f) concern 정정 carry**: 정본 anchor §22 reference list 정정은 측정 결과 회수 후 사용자 명시 시 inline 적용 (본 세션 적용 X). 본 코드의 헤더 주석에 cross-ref만.
- **Exqutor 본 논문 버전 차이 (carry)**: v4(2026-03-29) latest = EB-QAS 정본 anchor 인용 기반 / v2(2025-12-11) = Capstone CLAUDE.md 정본·local PDF. 두 버전 §V-B verbatim 동일이므로 운영 무영향.
- **메인 트랙 손대지 않음** (carry). EB-QAS 작업이 메인 트랙 v14·발표·포스터·보고서 작업에 영향 X.
- **별도 트랙 위상 유지**: 본 EB-QAS를 메인 트랙 발표·재프레이밍에 끼워 넣지 않는다.
- **본 handoff는 EB-QAS 트랙 only**. 다음 메인 세션이 박성원 회신 반영 시 handoff_230914 별도 read.
- **타임코드 네이밍**: 본 세션 타임코드 = `001021`(작업 시작 시점). measure 코드·spec 변경 시 새 타임코드 파일 생성. `v13/v14/ver/wave/phase` 단어를 파일명 분기자로 쓰지 않는다.
- **측정·팀 공유 boundary**: 본 #5 세션 완료가 "Codex review 디스패치·결과 회수·분류 단계 완료". 측정 launch는 review pass 후 별도 세션. 팀 공유는 측정 결과 회수 후 별도 세션.

## 8. 일정 (carry · 본 세션 시점)

| 일자 | 항목 | EB-QAS 트랙 영향 |
|---|---|---|
| 2026-05-24 (일) | 박성원 멘토 3차 자문 회신 예정 | 메인 트랙 (handoff_230914 task 1) — 본 EB-QAS 트랙 직접 영향 X. 다만 회신에 EB-QAS 언급 시 본 트랙 carry 반영 |
| 2026-05-26 (화) 23:59 | LearnUs 발표 deck 마감 ★★ critical path | 메인 트랙 — 본 EB-QAS 트랙 분리 |
| 2026-05-27 (수) · 5/29 (금) | 최종 발표 | 메인 트랙 — 본 EB-QAS 트랙 분리 |
| 2026-05-28 (목) 12:00 | 포스터 PDF 마감 (900×1200) | 메인 트랙 — 본 EB-QAS 트랙 분리 |
| 2026-06-11 (목) | 최종 보고서 마감 | 메인 트랙 |
| 본 세션 후 즉시 | **EB-QAS 트랙 verdict별 분기 진입** (4.A/4.B/4.C) | **본 트랙** — 사용자 명시 시 |
| Codex review pass 후 | **smoke 1 cell → 24 cell sequential 측정** | **본 트랙** — review pass 후 별도 세션 |
| 측정 결과 회수 후 | paired 분석 4축 + 팀 공유 메시지 | **본 트랙** — 측정 결과 회수 후 별도 세션 |

## 9. ★ 5 세션 누적 진행 표

| 세션 | 시간 (KST) | 주요 산출물 | 상태 |
|---|---|---|---|
| #1 21:54 | 정본화 + 자체 점검 + 메모리 | 정본 anchor 정본화 + 5/23 평결 호환성 4축 + 카톡 출처 + 메모리 anchor | commit `d6d1b5a7` |
| #2 22:20~22:51 (31분) | 인프라 + Exqutor v2 대조 + spec 3건 + Codex 디스패치·실행·결과 회수 | README + v2 대조 + 실험 A·B~E·의사코드 spec + Codex 디스패치 spec + Codex 검증 결과 정제 (6 축 종합 concern) | untracked carry |
| #3 23:00~23:30 (30분) | Codex 5건 정정 spec patch 완료 | T1 의사코드 신규 + T2 정본 anchor inline + T3 실험 A spec 신규 + T4 실험 B outline 신규 + T5 v4 대조 신규 + T6 handoff_231042 | untracked + 정본 anchor modified |
| #4 23:30~23:54 (24분) | 활성화 + measure_ebqas 코드 + 4 unit test + Codex review spec + handoff | T1 사용자 확정 + T2 ultraplanning + T3 measure_ebqas 11 항목 (modified) + T4 test_ebqas.py 8/8 PASS + T5 Codex review spec + T6 handoff_234413 | modified 1 + untracked 4 |
| **#5 00:03~00:20 KST (17분)** | **Codex review 디스패치 + 결과 회수 + 6 축 verdict 분류 → concern 4건 → 4.B 분기 + handoff** | T1 환경 검증 + T2 ultraplanning + T3 Codex 디스패치 (1차 stdin stuck → 2차 prompt file + /dev/null, 8분) + T4 결과 회수·정제 (종합 concern, 6 축 a·b·c·d concern·e pass-with-concern·f pass) + T5 4.B 분기 결정 + T6 본 handoff | **본 세션** (untracked 5 — handoff·복붙·결과 정제·codex log backup·prompt backup) |

5 세션 누적으로 EB-QAS 트랙은 **정본화 → 인프라·검증 → 활성화 전 정정 완료 → 활성화 + 코드·test·Codex review spec → Codex review 디스패치·결과·concern 분류**의 5 단계를 완료. 다음 단계는 **4.B concern 분기 진입** — 정정 plan 작성 → 코드 정정 6 항목(우선순위 1~3) → 재디스패치 → 4.A 진입(smoke → 24 cell → paired 분석)이며, 사용자 명시 결정 시점에 진입. smoke 단독 launch는 정정 전에도 함수 호출 기준 가능(Codex 결론 carry).

---

작성: 2026-05-24 00:10 KST skeleton → 00:20 KST 최종화. 본 세션(plan 00:09 → 디스패치 00:11 → 결과 회수 00:19 → 정제·분기·handoff 00:20) 인계. → 다음 EB-QAS 세션 = 4.B concern 분기(정정 plan 작성 → 코드 정정 6 항목 → 재디스패치 또는 smoke 단독 launch) → pass 시 4.A 진입 → 측정 → paired 분석 → 결론.
