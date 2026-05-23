# Codex measure_ebqas 코드·unit test review 결과 정제 (#5 세션 결과 회수)

> 작성: 2026-05-24 00:19 KST. 본 EB-QAS 트랙 5번째 세션의 산출물. Codex review 디스패치(2026-05-24 00:11 KST, prompt file + stdin /dev/null, Mac-mini.local, `b3sr3u3i6` 백그라운드)의 결과 회수·6 축 verdict 분류 정제본. **Codex 원본 응답은 본문 §3-§8에 verbatim carry** — 우리 해석을 verdict로 surrogate 금지(환각 회피 룰 carry).

## 0. 메타

| 항목 | 값 |
|---|---|
| 디스패치 시각 | 2026-05-24 00:11 KST (디스패치 명령 launching) |
| 종료 시각 | 2026-05-24 00:19 KST |
| 실행 시간 | ~8분 |
| 모델 | gpt-5.5 |
| reasoning effort | xhigh |
| sandbox | read-only |
| session id | `019e5565-fab1-79a2-ad9a-a214a254c288` |
| cwd | `/Users/hyunbin/Capstone` |
| 디스패치 명령 | `codex exec --sandbox read-only -o /tmp/codex_ebqas_review_001021.log "$(cat /tmp/codex_review_prompt_001021.txt)" < /dev/null` |
| prompt 파일 | `/tmp/codex_review_prompt_001021.txt` (직전 codex review spec §3.1 verbatim) |
| 결과 log 파일 | `/tmp/codex_ebqas_review_001021.log` (8,573 B, 64 lines) |
| task stdout stream | `/private/tmp/claude-501/.../tasks/b3sr3u3i6.output` (369,275 B, 4,956 lines) |
| 1차 시도 (실패) | `cat <<'EOF' ... EOF` heredoc command substitution → codex "Reading additional input from stdin..."에서 stuck → TaskStop |
| 2차 시도 (성공) | prompt file + `< /dev/null` stdin 차단 → 8분 후 정상 종료 (exit 0) |

## 1. 종합 verdict 및 6 축 verdict 요약 표

**★ 종합 verdict: concern**

> Codex 원본 (§3.0 첫 줄, verbatim):
>
> > 종합 verdict: **concern**. 8개 단독 unit test는 통과했습니다. 다만 `pytest`는 read-only sandbox에서 `FileNotFoundError: No usable temporary directory found ...`로 수집 전 실패했고, `python3 _internal/scripts/test_ebqas.py` 단독 실행은 `8/8 PASS`였습니다. "EB-QAS가 B1보다 낫다"는 측정 전 가설로만 유지해야 합니다.

### 6 축 verdict 표

| 축 | verdict | 신뢰도 | 핵심 finding 1줄 요약 |
|---|---|---|---|
| (a) 수학·산술 정확성 | **concern** | 0.86 | `EBQASParams.n_cap`이 dead param — `ebqas_estimate`가 `state.n_cap`만 사용. `q_log_floor`·`gamma`도 미반영 |
| (b) 안전장치 동작 | **concern** | 0.82 | explicit mode switch 자체는 구현 OK이나 **`no_history`가 실제로 history를 끄지 못함** — `ebqas_estimate`/`update_after_execution` 모두 prior_mode 무관하게 alpha/beta 사용·갱신. `EB-QAS-no-history` = "no-early-stop history posterior"에 가까움 |
| (c) paired 비교 통제·schema | **concern** | 0.78 | `assert_paired_join_invariant` key가 `(trial_idx, query_idx)`만 — cell·seed 미검증, `true_cardinality`도 1건만 비교. B1·CaseB schema 없으면 2-mode fallback인데 "4-way paired invariant 통과" 단언 X |
| (d) leakage 방지·prequential invariant | **concern** | 0.84 | read-only state·after-execution update 순서 prequential 원칙 OK. group key log-scale D bucket OK. 단 `template_id=q_row_idx`가 query identity면 history 누적 X (cold-start) — leakage 아니지만 EB-QAS 본의 약화 |
| (e) 5/23 평결 4축 호환성 | **pass-with-concern** | 0.87 | CaseB식 `(est_b1+est_method)/2` 없음, method library 미의존, latency 필드 없음 — 평결 호환. 단 `EB-QAS-no-history` label이 (b)와 같은 사유로 의미 불일치 |
| (f) Exqutor 인용·코드 주석 verbatim | **pass** | 0.90 | spec path·정본 anchor cross-ref·환각 회피 룰 정확. v2/v4 §V-B 동일성 OK. 단 stale param 주석(`q_log_floor`·`gamma`) 정리 권고 |

종합 정리: **fail 축 0건**, **concern 축 4건** (a·b·c·d) + **pass-with-concern 1건** (e) + **pass 1건** (f). 결과적으로 smoke 1 cell은 함수 호출 진행 가능하지만, **24 cell sequential 측정 진입 전에는 (a)(b)(c) 3건 필수 정정**이 codex 결론.

직전 #2 (codex_검증_20260523_225122.md) 비교: (b) **fail 0.91 → concern 0.82** 개선 (explicit mode switch · return update skip 정정 효과). 그러나 (a)(c)(d) 모두 concern 신규 — (a) dead param 발견·(c) invariant 약화 발견·(d) cold-start risk 발견. **#3 spec patch 5건 후에도 4 축 concern 잔존** — 코드 단계 정정 필요.

---

## 2. 원본 Codex 응답 verbatim (§3-§8)

본 §은 Codex CLI 응답을 verbatim carry. 본문은 한국어 학술 산문, 영문 path 인용(`measure_paper_exact.py:NNNN`). 본 정제본 사용자의 해석으로 verdict 변경·축약 X.

### 3. 축 (a) — 수학·산술 정확성, concern 0.86

> **Finding**: `beta_credible_interval`, posterior `alpha+s / beta+n-s`, `c_hat = total_rows * p_hat`, EB update 식 자체는 spec과 일치합니다.
> 인용 위치: [measure_paper_exact.py:1662](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1662), [measure_paper_exact.py:1725](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1725), [measure_paper_exact.py:1814](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1814)
>
> **Finding**: `EBQASParams.n_cap`은 선언·출력되지만 실제 cap에는 반영되지 않습니다. `ebqas_estimate`는 `params.n_cap`이 아니라 `state.n_cap`만 씁니다. `params.n_cap=10` probe에서도 sample size가 385로 나왔습니다.
> 인용 위치: [measure_paper_exact.py:1594](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1594), [measure_paper_exact.py:1700](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1700)
>
> **Finding**: `q_log_floor`와 EB-QAS용 `gamma`는 파라미터로 노출되지만 현재 계산에 쓰이지 않습니다. 특히 `q_log_floor` 주석은 "inf 대신 사용"이라고 되어 있으나 코드는 `inf`를 반환합니다.
> 인용 위치: [measure_paper_exact.py:1593](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1593), [measure_paper_exact.py:1735](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1735)
>
> **정정 권고**: `params.n_cap`을 state 생성 시 주입하거나 파라미터에서 제거하십시오. `q_log_floor`·`gamma`는 실제 로직에 반영하거나 dead param으로 명시 제거하고, `params.n_cap != 385` 회귀 테스트를 추가하는 것이 맞습니다.

### 4. 축 (b) — 안전장치 동작, concern 0.82

> **Finding**: explicit mode switch 자체는 구현되어 있습니다. 3회 mismatch 시 `no_history`, Beta(1,1), `early_stop=False`, update skip으로 전환됩니다.
> 인용 위치: [measure_paper_exact.py:1794](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1794)
>
> **Finding**: 그러나 `no_history`가 실제로 history를 끄지는 않습니다. `ebqas_estimate`는 `prior_mode`와 무관하게 `state.alpha/beta`를 사용하고, `update_after_execution`도 `no_history` 상태에서 계속 alpha/beta/kappa를 갱신합니다. 즉 `EB-QAS-no-history`는 "no-history"가 아니라 "no-early-stop history posterior"에 가깝습니다.
> 인용 위치: [measure_paper_exact.py:1725](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1725), [measure_paper_exact.py:1812](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1812)
>
> **Finding**: unit test는 `w_mismatch=0` override로 mode switch mechanics만 검증합니다. default `w_mismatch=1`에서 drift/fallback 의미가 유지되는지, 그리고 `no_history`에서 prior가 중립으로 유지되는지는 검증하지 않습니다.
> 인용 위치: [test_ebqas.py:66](/Users/hyunbin/Capstone/_internal/scripts/test_ebqas.py:66)
>
> **정정 권고**: `prior_mode=="no_history"`일 때 추정 prior를 Beta(1,1)로 고정하거나 update를 shadow/recovery counter로 분리하십시오. `EB-QAS-no-history`가 alpha/beta를 누적하지 않는 테스트를 추가해야 합니다.

### 5. 축 (c) — paired 비교 통제·row schema, concern 0.78

> **Finding**: `measure_ebqas`의 seed와 query 순서는 기존 B1/CaseB와 맞습니다. `query_results` 필수 17필드도 들어 있습니다.
> 인용 위치: [measure_paper_exact.py:1904](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1904), [measure_paper_exact.py:1994](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1994)
>
> **Finding**: `assert_paired_join_invariant`는 spec보다 약합니다. key가 `(trial_idx, query_idx)`뿐이라 `cell`과 `seed`를 보지 않고, `true_cardinality`도 임의 1건의 EB-QAS vs no-history만 비교합니다. 로컬 probe에서 B1 true-card mismatch, seed mismatch, cell mismatch가 모두 통과했습니다.
> 인용 위치: [measure_paper_exact.py:2090](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:2090), [measure_paper_exact.py:2123](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:2123)
>
> **Finding**: B1·CaseB에 `query_results`가 없으면 invariant가 graceful fallback으로 2-mode 검사만 합니다. 이 상태로는 "4-way paired invariant 통과"라고 말하면 안 됩니다.
> 인용 위치: [measure_paper_exact.py:2085](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:2085)
>
> **정정 권고**: invariant key를 `(cell, trial_idx, seed, query_idx 또는 query_id)`로 확장하고 모든 mode의 모든 row에서 true_cardinality를 비교하십시오. B1/CaseB schema 확장 전에는 결과 문구를 "EB-QAS 2-mode invariant"로 낮추십시오.

### 6. 축 (d) — leakage 방지·prequential invariant, concern 0.84

> **Finding**: query-time state read-only assert와 after-execution update 순서는 prequential 원칙과 맞습니다.
> 인용 위치: [measure_paper_exact.py:1953](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1953), [measure_paper_exact.py:1971](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1971)
>
> **Finding**: group key는 selectivity label을 받지 않고 log-scale D bucket만 씁니다. leakage 방지 관점에서는 pass입니다.
> 인용 위치: [measure_paper_exact.py:1625](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1625), [measure_paper_exact.py:1934](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1934)
>
> **Finding**: 다만 `template_id=q_row_idx`는 query vector id에 가까워 group key가 과도하게 세밀해질 수 있습니다. query pool이 1000개이고 n_queries가 1000이면 history가 거의 누적되지 않는 cold-start 실험이 됩니다. leakage는 아니지만 EB-QAS의 본의를 약화합니다.
> 인용 위치: [measure_paper_exact.py:1940](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1940)
>
> **정정 권고**: smoke 결과에 `n_groups / n_queries`를 launch gate로 기록하고, 24 cell 전에 `q_row_idx`가 정말 template인지 아니면 query identity인지 확정하십시오.

### 7. 축 (e) — 5/23 평결 4축 호환성, pass-with-concern 0.87

> **Finding**: EB-QAS 코드 안에는 CaseB식 `(est_b1 + est_method) / 2`가 없고, posterior mean 기반 대체 구조입니다.
> 인용 위치: [measure_paper_exact.py:1749](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1749)
>
> **Finding**: method library나 distribution-aware strata를 호출하지 않고 KM20/B1 sample cache만 사용합니다. latency 필드도 산출하지 않아 objective 혼동은 없습니다.
> 인용 위치: [measure_paper_exact.py:1895](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1895)
>
> **Finding**: 단 `EB-QAS-no-history` label은 현재 구현과 불일치합니다. 이것을 "history 제거 ablation"으로 해석하면 5/23 평결식 통제군 엄밀성이 흔들립니다.
> 인용 위치: [measure_paper_exact.py:1863](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1863)
>
> **정정 권고**: no-history 의미를 코드로 보장하거나 label을 `EB-QAS-no-stop`류로 바꾸십시오. 분석 문서에서는 측정 전 우위 단언을 계속 금지해야 합니다.

### 8. 축 (f) — Exqutor 인용·코드 주석 verbatim, pass 0.90

> **Finding**: 헤더의 spec path와 정본 anchor cross-ref는 현재 파일 구조와 일치합니다.
> 인용 위치: [measure_paper_exact.py:1558](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1558)
>
> **Finding**: 직전 Codex (b)(c)(d)(f) 정정 내역과 환각 회피 룰은 코드 헤더에 반영되어 있고, "EB-QAS가 B1보다 낫다"는 단언도 없습니다.
> 인용 위치: [measure_paper_exact.py:1565](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1565)
>
> **Finding**: v2/v4 Exqutor §V-B hyperparam·식 동일성은 별도 source map과 일치합니다. 다만 코드 내부 stale param 주석(`q_log_floor`, `gamma`)은 위 (a) 권고대로 정리하는 편이 인용 hygiene에도 안전합니다.
>
> **정정 권고**: 헤더는 유지 가능하되, dead/stale param 주석만 정리하십시오.

### 9. Codex 종합 결론 (마지막 단락 verbatim)

> 결론적으로 smoke 1 cell은 직접 함수 호출 기준으로 진행 가능하지만, **24 cell sequential 측정 진입 전에는 `params.n_cap`, `no_history` 의미, paired invariant 3건은 고치는 편이 맞습니다.** 특히 4-way paired invariant는 현재 테스트가 주장하는 만큼 강하지 않습니다.

---

## 10. 우리 해석·다음 세션 분기 권고 (별도 §, Codex 본문과 분리)

본 §은 Codex 본문의 verbatim carry와 분리. 사용자·다음 세션이 분기 판단에 사용. 단 우리 해석으로 Codex verdict를 surrogate 금지(환각 회피 룰).

### 10.1 verdict 분기 — concern 분기 (4.B) 선정

본 #5 review = fail 0건 + concern 4건(a·b·c·d) + pass-with-concern 1건(e) + pass 1건(f). plan 분기 표 기준 "concern (1-3 축 concern, fail 0)" 보다 concern 수가 많지만, fail 분기(4.C)가 아니라 concern 분기(4.B)에 해당. 단 Codex 결론은 "smoke는 진행 가능, 24 cell 진입 전 (a)(b)(c) 필수 정정"으로 분기를 명시 — **4.B 분기 안에서도 hybrid 진행** (smoke OK + 24 cell 전 정정 필수).

### 10.2 정정 우선순위 (Codex 결론 carry)

1. **★ 우선순위 1** — (a) `params.n_cap` dead param 정정. `ebqas_estimate`가 `params.n_cap`을 honor하도록 수정하거나 `params.n_cap` 제거 후 `state.n_cap`만 유지. 회귀 test 추가 (`test_n_cap_param_honored`).
2. **★ 우선순위 1** — (b) `no_history` 의미 코드 보장. `ebqas_estimate`·`update_after_execution`에서 `state.prior_mode=="no_history"` 분기 시 alpha/beta=Beta(1,1) 고정 또는 shadow update로 분리. 회귀 test 추가 (`test_no_history_keeps_alpha_beta_neutral`).
3. **★ 우선순위 1** — (c) `assert_paired_join_invariant` key 확장 `(cell, trial_idx, seed, query_idx)` + `true_cardinality` 전 row 비교. B1·CaseB schema 확장 전에는 문구 "EB-QAS 2-mode invariant"로 명시.
4. **★ 우선순위 2** — (d) smoke 시 `n_groups / n_queries` 측정·기록. `q_row_idx`가 template인지 query identity인지 확정 (현재 코드는 `q_row_idx = q_idx % len(qp)`로 query identity에 가까움) → template/group 의미 명시.
5. **★ 우선순위 3** — (e) `EB-QAS-no-history` label을 `EB-QAS-no-stop`으로 변경 또는 (b) 정정 완료 시 의미 보존.
6. **★ 우선순위 3** — (f) `q_log_floor`·`gamma` dead param 주석 정리 (실제 로직 반영 또는 명시 제거).

### 10.3 smoke 1 cell launch 가능성 평가

Codex 결론 "smoke 1 cell은 직접 함수 호출 기준으로 진행 가능"은 코드가 measurement 자체는 실행 가능함을 의미. 그러나 다음 세션이 smoke launch를 결정할 때는 다음 carry 인지 필요:
- `params.n_cap`이 영향 없음 → smoke는 default `state.n_cap=385`로 진행 (n_cap 변경 실험 X)
- `EB-QAS-no-history` mode는 history 끄지 않음 → smoke 결과의 EB-QAS-no-history는 ablation으로 해석 X
- paired invariant 약함 → smoke는 단일 mode·단일 cell이라 invariant 무관

→ **smoke는 EB-QAS mode 단독 launch는 가능**. 다만 EB-QAS-no-history와의 mode 차이 검증은 정정 후로 미룸.

### 10.4 24 cell sequential 진입 전 필수 gate

Codex 결론 그대로 — (a)(b)(c) 3건은 24 cell 진입 전 정정 필수. 정정 완료 후 본 review를 재디스패치하거나, 정정 plan을 별도 spec으로 작성해 codex re-review.

---

## 11. 본 결과 정제와 직전 #2 결과 비교

| 축 | #2 (225122) | #5 (001021) | 변화 |
|---|---|---|---|
| (a) 수학 | concern 0.86 (5 항목 우려) | **concern 0.86** (dead param 발견) | 신뢰도 동일, finding 변경 — spec 정정으로 5 항목 해결되나 코드 실현에서 dead param 신규 발견 |
| (b) 안전장치 | **fail 0.91** (fixed-point κ≈19 반례) | **concern 0.82** (no_history 의미 미보장) | **fail → concern 개선** — explicit mode switch + return update skip 정정 효과. 그러나 no_history mode 의미 잔존 concern |
| (c) paired | concern 0.82 (CaseB comparator 미고정) | **concern 0.78** (invariant key 약함·4-way fallback 2-mode) | 신뢰도 약간 하락 — spec patch (strong-13 aggregate 사전 고정 / matched rank-biserial)로 일부 해결되나 code-level invariant 발견 |
| (d) leakage | concern 0.84 (group key·threshold leakage 우려) | **concern 0.84** (cold-start risk) | 신뢰도 동일, finding 변경 — make_group_key·bucketize_threshold 정정으로 leakage 해결, 그러나 template_id=query_id 잔존 concern |
| (e) 평결 호환성 | pass 0.87 | **pass-with-concern 0.87** | 동일 — no-history label 잔존 |
| (f) 외부 인용 | concern 0.88 (Exqutor v4 외부 fetch 누락) | **pass 0.90** (v4 외부 fetch + clean source map) | **concern → pass 개선** — #3 spec patch (v4 외부 fetch + 12 entry clean source map) 효과 |

종합 평가: #3 spec patch 5건 + #4 코드 작성으로 **(b) fail → concern·(f) concern → pass 2건 개선**. 그러나 코드 단계 진입으로 (a)(c)(d) finding이 spec → 코드 dead/leakage 잔존 형태로 transition. **정정 plan 별도 작성 + 코드 정정 + 재디스패치**가 다음 세션 task.

---

작성: 2026-05-24 00:19 KST. 본 결과 정제 = #5 세션 산출물. 다음 EB-QAS 세션 = 본 §10 분기 권고 따라 진행. 결과 정제 .md만 단독으로 6 축 검토 가능 (Codex log read 없이도).
