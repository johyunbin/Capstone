# Codex measure_ebqas 재review 결과 정제 (#5b 세션 — 정정 후 재검증)

> 작성: 2026-05-24 00:53 KST. 본 EB-QAS 트랙 #5b 세션 산출물. #5 결과 정제(`codex_review_결과_001021.md`)의 Codex 6 항목 정정 권고를 코드에 반영한 후, 동일 spec으로 Codex review 재디스패치한 결과의 정제본. **Codex 원본 응답은 본문 §3-§8에 verbatim carry** — 우리 해석을 verdict로 surrogate 금지(환각 회피 룰 carry).

## 0. 메타

| 항목 | 값 |
|---|---|
| 디스패치 시각 | 2026-05-24 00:44 KST |
| 종료 시각 | 2026-05-24 00:52 KST |
| 실행 시간 | ~8분 |
| 모델 | gpt-5.5 |
| reasoning effort | xhigh |
| sandbox | read-only |
| cwd | `/Users/hyunbin/Capstone` |
| 디스패치 명령 | `codex exec --sandbox read-only -o /tmp/codex_ebqas_review_rerun_004456.log "$(cat /tmp/codex_review_prompt_001021.txt)" < /dev/null` |
| prompt 파일 | `/tmp/codex_review_prompt_001021.txt` (#5와 동일 — 정정 전후 동일 spec 재사용) |
| 결과 log 파일 | `/tmp/codex_ebqas_review_rerun_004456.log` (6,614 B, 46 lines) |
| task stdout stream | `/private/tmp/claude-501/.../tasks/ba82uw2td.output` (6,252+ lines, 메모리·chronicle·diff 분석 단계 포함) |
| 정정 carry | #5b 단계 5·6 코드 정정 6 항목 (a·b·c·d·e·f) + 단계 7 unit test 10/10 PASS |

## 1. 종합 verdict 및 6 축 verdict 요약 표

**★ 종합 verdict: concern (#5와 동일)**

> Codex 원본 (§3.0 첫 줄, verbatim):
>
> > 종합 verdict: **concern**. 단독 smoke 1 cell은 직접 함수 호출 기준으로는 가능하지만, 24 cell sequential 진입 전에는 recovery 의미, paired invariant, 주석/spec 불일치 3축은 정리하는 편이 맞습니다. "EB-QAS가 B1보다 낫다"는 여전히 측정 전 가설입니다.
>
> 검증 실행: `python3 _internal/scripts/test_ebqas.py`는 **10/10 PASS**. `pytest`는 코드 실패가 아니라 read-only sandbox의 temp dir 부재로 수집 전 실패.

### 6 축 verdict 표 (#5 → #5b 비교)

| 축 | #5 verdict (신뢰도) | **#5b verdict (신뢰도)** | 변화 | 핵심 finding (#5b) |
|---|---|---|---|---|
| (a) 수학·산술 정확성 | concern 0.86 | **concern 0.86** | 동일 | `params.n_cap` honor 확인. 그러나 `q_log_floor` finite floor vs spec inf 불일치 + `gamma` 여전히 unused |
| (b) 안전장치 동작 | concern 0.82 | **concern 0.84** | ↑0.02 | explicit mode switch OK. **recovery 도달 불가능** — `no_history return` 으로 `stable_query_count >= n_recovery` 분기 실행 X. test 의미 변경 OK이나 spec recovery 검증 X |
| (c) paired 비교 통제·schema | concern 0.78 | **concern 0.80** | ↑0.02 | seed/cell 키에 포함했으나 top-level 누락 시 fail 안 함. B1·CaseB schema 없으니 실제 4-way 불가 (fallback 상태) |
| (d) leakage 방지·prequential invariant | concern 0.84 | **pass-with-concern 0.84** | concern→pass-with-concern ✓ | read-only state·after-execution update prequential OK. `template_id="default"` 정정 효과 — 단 group이 과도하게 넓어질 수 있어 smoke n_groups 기록 필요 |
| (e) 5/23 평결 4축 호환성 | pass-with-concern 0.87 | **pass-with-concern 0.87** | 동일 | CaseB식 평균 X·분포 사전 지식 X·latency objective X. 단 EB-QAS-no-history는 "B1 exact"가 아닌 Beta(1,1) smoothing — 통제군 의미 정확화 권고 |
| (f) Exqutor 인용·코드 주석 verbatim | pass 0.90 | **concern 0.82** | pass→concern ↓ | header path/anchor OK. **(b) 정정으로 주석 모순 발생** — recovery 말하면서 "자동 회복 안 됨" 동시. `q_log_floor` spec inf vs 코드 finite floor 갈림 |

종합: fail 0건 (동일), **concern 5건 a·b·c·f·(추가) + pass-with-concern 2건 d·e**. #5는 4 concern + 1 pass-with-concern + 1 pass였으나 #5b는 (d) 1축 명확 개선·(f) 1축 악화·(b)(c) 미세 개선. **부분 개선 + 부분 악화**.

직전 Codex 결론: **"24 cell sequential 진입 전 recovery 의미·paired invariant·주석/spec 불일치 3축 정리 필요"** — 단 본 결정 carry: 24 cell launch 이미 진행 중(서버 nohup), 본 finding은 추가 정정 plan으로 다음 세션 미룸 (사용자 시간 압박 carry).

추가 운영 finding (verbatim): `main()` CLI에는 `EB-QAS` mode가 아직 연결되어 있지 않습니다 — smoke는 직접 함수 호출로 하거나 CLI mode 추가 필요.

---

## 2. 원본 Codex 응답 verbatim (§3-§8)

본 §은 Codex CLI 응답을 verbatim carry.

### 3. 축 (a) — 수학·산술 정확성, concern 0.86

> **Finding 1**: `beta_credible_interval`, posterior `alpha+s / beta+n-s`, `c_hat = total_rows * p_hat`, EB update 식은 spec과 대체로 일치합니다.
> 인용: [measure_paper_exact.py:1662](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1662), [1731](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1731), [1827](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1827)
>
> **Finding 2**: `L_log`/`L_stop` 분리는 되어 있지만, T1은 `L_raw=0`에서 `q_post_log = inf`를 요구하는 반면 코드는 `q_log_floor`로 유한값을 반환합니다.
> 인용: [measure_paper_exact.py:1741](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1741)
>
> **Finding 3**: `params.n_cap`은 현재 코드에서 honor됩니다. 다만 `gamma`는 공개 hyperparam인데 실제 로직에서는 unused입니다.
> 인용: [measure_paper_exact.py:1599](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1599)
>
> **정정 권고**: `q_post_log`를 진짜 `inf`로 돌릴지, finite logging floor를 새 spec으로 확정할지 하나로 통일하십시오. `gamma`는 제거하거나 실제 감쇠 의미를 구현해야 합니다.

### 4. 축 (b) — 안전장치 동작, concern 0.84

> **Finding 1**: explicit mode switch 자체는 구현되어 있습니다. 연속 mismatch threshold 도달 시 `no_history`, Beta(1,1), `early_stop=False`, update skip으로 전환됩니다.
> 인용: [measure_paper_exact.py:1807](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1807)
>
> **Finding 2**: 그러나 recovery는 현재 코드상 도달 불가능합니다. `prior_mode == "no_history"`면 함수 초입에서 return하므로, 뒤의 `stable_query_count >= n_recovery` 분기는 실행되지 않습니다.
> 인용: [measure_paper_exact.py:1789](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1789), [1818](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1818)
>
> **Finding 3**: `test_recovery_after_stable_streak`는 자동 recovery 대신 "수동 history 전환" 테스트로 의미가 바뀌어 T1의 recovery 요구를 검증하지 않습니다.
> 인용: [test_ebqas.py:194](/Users/hyunbin/Capstone/_internal/scripts/test_ebqas.py:194)
>
> **정정 권고**: `no_history`에서도 stable counter만 shadow update하거나, recovery를 공식 폐기하고 spec/test 이름을 바꾸십시오. default `w_mismatch=1` drift test도 추가하는 것이 좋습니다.

### 5. 축 (c) — paired 비교 통제·schema, concern 0.80

> **Finding 1**: EB-QAS의 seed와 query 순서는 기존 B1/CaseB 패턴과 맞습니다.
> 인용: [measure_paper_exact.py:1917](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1917)
>
> **Finding 2**: EB-QAS `query_results`는 핵심 필드를 담지만, B1/CaseB 기존 JSON에는 query-level row가 없어 실제 4-way invariant는 fallback 상태입니다.
> 인용: [measure_paper_exact.py:2164](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:2164)
>
> **Finding 3**: invariant가 cell/seed를 key에 넣기는 하지만, 값이 누락되어도 실패하지 않습니다. 현재 pass 테스트도 top-level `cell`·`seed` 없이 통과합니다.
> 인용: [test_ebqas.py:341](/Users/hyunbin/Capstone/_internal/scripts/test_ebqas.py:341)
>
> **정정 권고**: EB-QAS 두 mode는 `cell`·`seed` 필수로 assert하고, B1/CaseB schema 확장 전에는 "4-way invariant 통과"가 아니라 "EB-QAS 2-mode invariant"로 표기하십시오.

### 6. 축 (d) — leakage 방지·prequential invariant, **pass-with-concern 0.84** (개선)

> **Finding 1**: `ebqas_estimate` 전 state snapshot, read-only assert, 실행 후 update 순서는 prequential 원칙과 맞습니다.
> 인용: [measure_paper_exact.py:1971](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1971)
>
> **Finding 2**: `true_cardinality`는 estimation 결과 dict에 들어가지 않고, Q-error 계산 및 update 이후에만 쓰입니다.
>
> **Finding 3**: group key는 `sel` label을 쓰지 않고 log-scale D bucket을 사용합니다. 다만 `template_id="default"`라 group이 과도하게 넓어질 수 있으므로 smoke에서 `n_groups / n_queries`를 기록해야 합니다.
>
> **정정 권고**: smoke launch gate에 group 수, bucket별 true selectivity 분포, mode switch event를 포함하십시오.

### 7. 축 (e) — 5/23 평결 4축 호환성, pass-with-concern 0.87

> **Finding 1**: 코드에는 CaseB식 `(est_b1 + est_method) / 2`가 없습니다.
>
> **Finding 2**: method library나 분포 사전 지식 호출도 없습니다. latency objective 필드도 없습니다.
>
> **Finding 3**: 단 `EB-QAS-no-history`는 "B1 exact"가 아니라 Beta(1,1) smoothing을 쓰는 no-history posterior입니다. 해석을 B1 fallback과 혼동하면 통제군 의미가 흐려집니다.
>
> **정정 권고**: label 또는 설명을 `Beta(1,1) no-history / no-stop ablation` 수준으로 좁히십시오.

### 8. 축 (f) — Exqutor 인용·코드 주석 verbatim, **concern 0.82** (악화)

> **Finding 1**: 헤더의 spec path, 정본 anchor, 환각 회피 룰은 현재 파일 구조와 일치합니다.
>
> **Finding 2**: 그러나 코드 주석은 recovery를 말하면서 동시에 "자동 회복 안 됨"을 말합니다. 이 상태는 verbatim cross-ref로 안전하지 않습니다.
> 인용: [measure_paper_exact.py:1780](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:1780)
>
> **Finding 3**: `q_post_log`도 spec/test doc은 `inf`, 코드는 finite floor라 주석과 동작이 갈립니다.
>
> **정정 권고**: header는 유지 가능하되, recovery와 `q_log_floor` 관련 주석/test명을 실제 정책에 맞춰 다시 고정하십시오.

### 9. Codex 추가 운영 finding (verbatim)

> `main()` CLI에는 `EB-QAS` mode가 아직 연결되어 있지 않습니다.
> 인용: [measure_paper_exact.py:2238](/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:2238)
>
> smoke는 직접 함수 호출로 하거나 CLI mode를 추가해야 합니다.

---

## 10. 우리 해석·다음 세션 분기 권고 (별도 §, Codex 본문과 분리)

### 10.1 verdict 분기 — concern 잔존, 다음 세션 추가 정정 task

본 #5b 재review = fail 0건 + concern 5건(a·b·c·f·+추가) + pass-with-concern 2건(d·e). #5 (concern 4 + pass-with-concern 1 + pass 1)와 비교 시:
- **개선 1축**: (d) leakage concern → pass-with-concern (template_id="default" cold-start 해결 효과)
- **악화 1축**: (f) 외부 인용 pass → concern (본 정정으로 주석·코드 모순 발생)
- **개선 미미**: (b)(c) 신뢰도 +0.02 (recovery 의미 명확화·invariant key 확장 효과)
- **동일**: (a)(e)

→ **24 cell sequential launch 그대로 진행** (사용자 시간 압박 carry, plan §확장 결정). 결과 회수 후 다음 세션 추가 정정.

### 10.2 다음 세션 추가 정정 우선순위

1. **★★ (b) recovery 결정** — 두 옵션:
   - (b.A) `no_history`에서도 streak 카운터만 shadow update → `stable_query_count >= n_recovery` 시 history 회복 (자동)
   - (b.B) recovery 공식 폐기 → spec T1 §4.2 갱신 + test 이름·docstring 정정
   - 선택은 사용자 결정 (b.B가 더 깔끔, b.A가 spec 일관)
2. **★★ (c) cell/seed top-level assert** — `assert_paired_join_invariant`에서 EB-QAS·EB-QAS-no-history JSON의 top-level `cell`·`seed` 필수 (None이면 fail). test_paired_join_invariant_* 3건도 cell/seed 포함하도록 확장
3. **★★ (f) 주석/spec 정합성** — recovery 관련 주석 갱신 (no_history return으로 자동 회복 불가 명시) + `q_log_floor` spec inf vs finite floor 결정 후 통일
4. **★ (a) q_log_floor 결정** — spec inf vs finite floor 결정 후 통일 (위 (f)와 동시)
5. **★ (a) gamma 정리** — 제거 or 실제 감쇠 의미 구현 (spec T1 §4.5 cross-ref)
6. **★ (e) EB-QAS-no-history label 정확화** — `Beta(1,1) no-history posterior` 수준으로 docstring·정본 anchor 갱신
7. **★ 추가 운영** — `main()` CLI에 EB-QAS mode 연결 (argparse `--mode EBQAS` 추가, smoke·24 cell launch도 CLI 호출로 가능)

### 10.3 본 #5b 코드의 측정 사용 가능성

본 review 결과는 코드가 "측정 진행 가능 단계"임을 인정 (Codex 결론: "smoke 1 cell은 직접 함수 호출 기준으로는 가능"). 24 cell sequential launch도 같은 함수 호출 패턴이므로 진행 가능. 본 측정 결과는 본 #5b 코드의 정합성 한도 내에서 해석. **본 review concern 5건은 다음 세션 추가 정정 + 재re-review 대상**이지만, 본 24 cell 측정 자체의 유효성을 부정하지 않는다.

특히 (d) leakage·prequential pass-with-concern은 측정 결과 신뢰성에 직접 영향 (leakage 없음 = paired 비교 가능). 다른 4 concern은 ablation 통제군 의미·recovery·invariant·주석 정합성이라 측정 자체보다는 분석·해석 단계 영향.

---

## 11. #5 vs #5b verdict 비교 표 (자세히)

| 축 | #5 verdict | #5 신뢰도 | **#5b verdict** | **#5b 신뢰도** | Δ | 정정 효과 |
|---|---|---|---|---|---|---|
| (a) 수학 | concern | 0.86 | concern | 0.86 | 0 | `params.n_cap` honor ✓, but `q_log_floor` finite floor / `gamma` unused 잔존 |
| (b) 안전장치 | concern | 0.82 | concern | 0.84 | +0.02 | mode switch 명확 ✓, `no_history` 의미 보장 ✓, but recovery 도달 불가 신규 발견 |
| (c) paired | concern | 0.78 | concern | 0.80 | +0.02 | invariant key 4-tuple 확장 ✓, 전수 비교 ✓, but cell/seed top-level assert 약함 잔존 |
| (d) leakage | concern | 0.84 | **pass-with-concern** | 0.84 | **개선** | `template_id="default"` cold-start 해결 ✓ |
| (e) 평결 호환성 | pass-with-concern | 0.87 | pass-with-concern | 0.87 | 0 | EB-QAS-no-history Beta(1,1) smoothing 명확화 권고 (#5와 동일) |
| (f) 외부 인용 | pass | 0.90 | **concern** | 0.82 | **악화** | 본 정정으로 주석·코드 모순 발생 (recovery 자동 회복 안 됨이 헤더 주석과 unresolved) |

종합: 6 항목 정정 중 **(d) 1축 명확 개선 + (b)(c) 미세 개선 + (a)(e) 동일 + (f) 1축 악화**. 4 항목 정정 즉시 spec/주석 갱신을 동반하지 않은 결과.

---

작성: 2026-05-24 00:53 KST. 본 결과 정제 = #5b 세션 산출물. 다음 EB-QAS 세션 = §10.2 추가 정정 우선순위 + re-review (또는 24 cell 결과 받은 후 진행). 결과 정제 .md 단독으로 6 축 검토 가능.
