# Codex measure_ebqas 코드·unit test review 디스패치 spec

> 작성: 2026-05-23 23:44 KST. 본 EB-QAS 트랙 4번째 세션의 산출물. 직전 디스패치 spec(`codex_디스패치_spec_20260523_223921.md`)의 6 축 검증 base를 carry하면서, **본 세션 신규 산출물(measure_ebqas 코드 + 4 unit test)에 대한 review** 디스패치 spec으로 분기한다. 실제 Codex 실행은 사용자 명시 지시 시(본 세션 또는 다음 세션).

## 0. 디스패치 환경

| 항목 | 값 |
|---|---|
| Host | Mac-mini.local (codex 전용 머신 룰 `~/.claude/rules/multi-model.md` carry) |
| codex CLI | codex-cli 0.132.0 (`/opt/homebrew/bin/codex`) |
| 인증 | ChatGPT 로그인 (`codex login status` Logged in OK) |
| 모델 | gpt-5.5 (`~/.codex/config.toml` `model = "gpt-5.5"`) |
| reasoning effort | xhigh (전체 트랙 일관 사용) |
| sandbox | read-only (검증만 — 파일 수정 X) |
| cwd | `/Users/hyunbin/Capstone` |
| 디스패치 명령 | `codex exec --sandbox read-only` (foreground 또는 background) |
| 예상 토큰 | 직전 6 축 디스패치 320,939 tokens 대비 본 코드 review 중심 → ~200,000 tokens 예상 |

## 1. 입력 정본 (10 파일)

본 디스패치가 검증하는 산출물 묶음. 모두 cwd 기준 상대 경로.

| # | 파일 | 역할 |
|---|---|---|
| 1 | `_internal/scripts/measure_paper_exact.py` (라인 1582~2144, 신규 11 항목) | **본 review 1차 대상** — measure_ebqas 코드 본진 |
| 2 | `_internal/scripts/test_ebqas.py` (신규) | **본 review 2차 대상** — 4 unit test + 헬퍼 test |
| 3 | `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` | 정본 anchor (직전 #3 세션 inline patch 4건 적용 완료) |
| 4 | `_internal/state/ebqas_track/실험_spec/EBQAS_구현_의사코드_20260523_231042.md` | T1 의사코드 spec (Codex (b) fail 정정) |
| 5 | `_internal/state/ebqas_track/실험_spec/EBQAS_실험A_4way_matched_spec_20260523_231042.md` | T3 실험 A spec (Codex (c) concern 정정) |
| 6 | `_internal/state/ebqas_track/실험_spec/EBQAS_실험BCDE_outline_20260523_231042.md` | T4 실험 B outline (Codex (d) concern 정정) |
| 7 | `_internal/state/ebqas_track/exqutor_대조/exqutor_v4_verbatim_대조_20260523_231042.md` | T5 v4 외부 fetch (Codex (f) concern 정정) |
| 8 | `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` | 5/23 본 연구 오프라인 실험 정당성 감사 평결 (A1~A5) |
| 9 | `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md` | 직전 6 축 종합 검증 결과 정제 |
| 10 | `_internal/state/ebqas_track/README.md` | 본 EB-QAS 트랙 진입 anchor (격리·평결 호환성 4축) |

## 2. 검증축 6개 (carry + 본 review 신규 항목)

본 디스패치는 다음 6 축에서 적대적 검증을 요구한다. 각 축에서 (i) verdict ∈ {pass · concern · fail} (ii) 핵심 finding 3 이내 (iii) 정정 권고 1-3 항목 (iv) 신뢰도 0~1을 출력한다. **본 review는 spec 검증이 아니라 코드·test 검증**이므로 각 축의 검증 항목이 spec(직전 6 축)과 다르게 코드 동작·invariant·test 정합성에 초점.

### 축 (a) — 수학·산술 정확성

대상: `measure_paper_exact.py` 신규 11 항목 + `test_ebqas.py` 8 test.

검증 항목:
- `beta_credible_interval(alpha, beta, confidence)` — `scipy.stats.beta.ppf((1-c)/2, alpha, beta)`·`ppf((1+c)/2, alpha, beta)` 호출이 정본 anchor §11.3·§7 식과 일관한지. argument 순서·confidence default 0.95.
- `ebqas_estimate`의 posterior_alpha = state.alpha + s / posterior_beta = state.beta + n − s 계산이 정본 anchor §3 식과 일관한지. p_hat = a_post / (a_post + b_post) 가중평균 표현 정확성.
- `update_after_execution`의 empirical-Bayes update — `new_kappa = min(kappa_max, rho·kappa + w_effective)`·`new_mu = (rho·kappa·mu + w_effective·p_true) / (rho·kappa + w_effective)` 가 정본 anchor §10.4 식·spec T1 §4.4 식과 일관한지.
- `c_hat = total_rows * p_hat` 산출이 정본 anchor §3 cardinality 정의와 일관한지.
- L_log·L_stop 분리 — `L_stop = max(L_raw, 1/(10·total_rows))` floor가 spec T1 §3.3 정의와 일관한지(`1/(10·N)` notation).

### 축 (b) — 안전장치 동작

대상: `update_after_execution` mode switch + recovery + w_mismatch + `_copy_ebqas_state`·`_ebqas_state_equal` invariant.

검증 항목:
- explicit mode switch 발동 조건 — `consecutive_mismatch >= mismatch_n_threshold and prior_mode == "history"` 정확.
- mode switch 동작 — `prior_mode="no_history"` + `alpha=beta=1.0` + `kappa=2.0` + `mu=0.5` + `early_stop=False` + **return (update skip)** 4 step.
- recovery 조건 — `prior_mode=="no_history" and stable_query_count >= n_recovery` 정확. recovery 시 alpha/beta/kappa는 Beta(1,1) base 유지 (재초기화 X) 의도.
- w_mismatch 분기 — `w_effective = w_mismatch if mismatch else w` 정확. mismatch query에서 update step 진입 — `return`은 mode switch 시점에만.
- `test_mode_switch_mismatch_streak`이 `w_mismatch=0` override로 prior 학습을 차단해 mode switch까지 가는 단순 시나리오 — default `w_mismatch=1`에서 mode switch가 발동하는 시나리오(workload drift)도 spec T1 §5.5 carry. 본 test가 default 동작이 아닌 mode switch 자체 invariant 검증임을 명확히 표시(코드 주석에 있음).
- ★ Codex 직전 (b) fail에서 지적한 fixed-point `κ ≈ 19` 수렴 반례가 본 코드에서 해결됐는지 — mode switch가 `return`으로 update skip 보장 + recovery시 Beta(1,1) base.

### 축 (c) — paired 비교 통제·query-level row schema

대상: `measure_ebqas` trial loop + query-level row schema + `assert_paired_join_invariant`.

검증 항목:
- 4 mode(B1·CaseB·EB-QAS·EB-QAS-no-history) 동일 trial/query/seed — `measure_ebqas`의 `rng = np.random.default_rng(trial_idx * 13 + 7)`이 기존 `measure_b1_paper`·`measure_case_b`·`measure_case_c`와 정확히 동일한지(라인 408·1130·1216 carry).
- query 순서 동일 — `for q_idx in range(n_queries): q_row_idx = q_idx % len(qp)` 패턴이 기존 3 mode와 동일.
- query-level row schema — `query_results[]`의 필수 17 필드(query_idx·query_id·q_row_idx·true_cardinality·estimated_cardinality·q_error·sample_size·hits·posterior_alpha·posterior_beta·posterior_q_risk_log·posterior_q_risk_stop·early_stopped·prior_mode_at_query·consecutive_mismatch_after·stable_query_count_after·group_key_repr) 모두 포함.
- `assert_paired_join_invariant` — (cell, trial_idx, query_idx) 3-tuple 일관·mode label 검증·true_cardinality 일관 sample 1건 검증. B1·CaseB가 query-level row schema 없을 때 graceful fallback(if 분기) 정확.
- CaseB comparator 옵션 사전 고정 — strong-13 aggregate (default, 사용자 확정) — measure_ebqas는 자체 측정만 산출, comparator 처리는 analysis 단(다음 세션). 본 코드에서 CaseB strong-13 aggregate 계산 로직이 의도적으로 없는 것이 정확한 분리인지(measure는 raw, analysis는 aggregate).

### 축 (d) — leakage 방지·prequential invariant

대상: `measure_ebqas` query loop + `ebqas_estimate` state read-only + `_copy_ebqas_state`·`_ebqas_state_equal` + `update_after_execution` 시점.

검증 항목:
- prequential flow 정확성 — `(1) make_group_key` → `(2) group_states.setdefault` → `(3) state_before = _copy_ebqas_state` → `(4) ebqas_estimate (state read-only)` → `(5) assert _ebqas_state_equal` → `(6)(7) update_after_execution` 7 step.
- ebqas_estimate state read-only — 함수 내부에서 state.alpha·beta·kappa·mu·prior_mode·early_stop·... 어디에도 assignment 없음 (read만). `_ebqas_state_equal` 통과로 검증.
- runtime group key vs benchmark label 분리 — `make_group_key`가 `sel=...` label을 받지 않음. `cell.selectivities[0]`은 query loop 안에서만 사용(true_cardinality lookup용)이지 group key 생성에는 안 들어감.
- threshold_bucket leakage-free — `bucketize_threshold(D)`가 dataset 전체 quantile 사용 X (log-scale `floor(log10(D))` only).
- true_cardinality 사용 시점 — `update_after_execution`은 ebqas_estimate 종료 후 호출, 다음 query부터 영향(현재 query stop·update에 미사용).
- double counting 금지 — 현재 query sample(`ebqas_estimate` 안 sampling)이 prior update에 들어가지 X. posterior_alpha = state.alpha + s는 ebqas_estimate 내부 임시값으로만 사용, state.alpha 자체는 update_after_execution이 true_cardinality 기반으로 별도 갱신.

### 축 (e) — 5/23 평결 4축 호환성

대상: `measure_paper_exact.py` 신규 헤더 주석(라인 1561~1577) + `measure_ebqas` 자체 코드.

검증 항목:
- CaseB식 산술평균 채택 X — `ebqas_estimate`의 estimated_cardinality는 posterior mean의 가중평균(prior + sample proportion)이지 두 독립 추정량 평균이 아님. 코드에서 `(est_b1 + est_method) / 2` 패턴 없음.
- 분포 사전 지식 가정 X — `ebqas_estimate`·`update_after_execution`·`make_group_key` 어디에도 vector 분포·CDF·clustering·density map·histogram 미사용. group key 6-tuple metadata only.
- latency objective X — `measure_ebqas`의 trial_results·query_results에 latency 측정 X(estimated_cardinality·q_error만). exec_ms 등 latency 필드 없음 — spec T3 §5.3 query-level row schema의 exec_ms는 선택 필드.
- method library 미의존 — `ebqas_estimate`·`update_after_execution`이 `_get_method_strata` 호출 X. samples_b1·sizes_b1만 사용(`measure_b1_paper`와 동일 KM20 cache).

### 축 (f) — Exqutor 외부 인용·코드 주석 verbatim

대상: 신규 헤더 주석(라인 1561~1581) + 정본 anchor §V-B·§22 reference list.

검증 항목:
- 헤더 주석의 spec 4건 cross-ref path가 정확(`EBQAS_*_20260523_231042.md`).
- 헤더 주석의 정본 anchor cross-ref 정확.
- 헤더 주석의 Codex (b)·(c)·(d)·(f) 정정 내용이 직전 검증 결과(`codex_검증_20260523_225122.md`)와 일관.
- 헤더 주석의 환각 회피 룰 4항(v13 수치 carry·"EB-QAS가 B1보다 낫다" 단언 X·latency objective X·CaseB식 평균 X)이 5/23 평결과 일관.

## 3. 디스패치 명령 (사용자 명시 시)

### 3.1 background 디스패치 (recommended)

```bash
# Mac-mini.local 에서
cd /Users/hyunbin/Capstone

codex exec --sandbox read-only \
  -o /tmp/codex_ebqas_review_$(date +%H%M%S).log \
  "$(cat <<'EOF'
EB-QAS 트랙 measure_ebqas 코드 · 4 unit test review 요청.

검증 대상: _internal/scripts/measure_paper_exact.py (라인 1582~2144 신규 11 항목)
         _internal/scripts/test_ebqas.py (신규 4 unit test + 4 헬퍼 test)

검증 base spec:
- _internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md (본 spec)
- _internal/state/ebqas_track/실험_spec/EBQAS_구현_의사코드_20260523_231042.md (T1)
- _internal/state/ebqas_track/실험_spec/EBQAS_실험A_4way_matched_spec_20260523_231042.md (T3)
- _internal/state/ebqas_track/실험_spec/EBQAS_실험BCDE_outline_20260523_231042.md (T4)
- submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md (정본 anchor)
- _internal/state/오프라인실험_정당성감사_평결_20260523_031402.md (5/23 평결)
- _internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md (직전 6 축 결과)
- _internal/state/ebqas_track/README.md (트랙 진입 anchor)

6 검증축 (각 축에서 verdict + finding 3건 + 정정 권고 1-3건 + 신뢰도 0~1):
(a) 수학·산술 정확성 — beta_credible_interval·ebqas_estimate·update_after_execution·L_log/L_stop 분리
(b) 안전장치 동작 — explicit mode switch·recovery·w_mismatch·κ ≈ 19 fixed-point 반례 해결
(c) paired 비교 통제·query-level row schema — 4 mode 동일 seed·query 순서·invariant
(d) leakage 방지·prequential invariant — read-only state·threshold_bucket·true_cardinality 시점
(e) 5/23 평결 4축 호환성 — CaseB식 평균 X·분포 사전 지식 X·latency objective X·method library X
(f) Exqutor 외부 인용·코드 주석 verbatim — 헤더 주석 cross-ref·환각 회피 룰

출력 형식: 한국어 학술 산문. 각 축마다 (verdict, finding, 정정 권고, 신뢰도).
종합 verdict: pass / concern / fail.

본 review의 목적: 활성화 → smoke 1 cell → 24 cell sequential 측정 진입 전 코드·invariant
독립 검증. 환각 회피: "EB-QAS가 B1보다 낫다" 단언 X (측정 전 가설). spec 정정이 코드에
정확히 반영됐는지 + leakage·invariant가 spec 룰과 일관한지 만 검증.
EOF
)"
```

### 3.2 structured 디스패치 (선택)

JSON schema 출력으로 분석 자동화 시(직전 spec §3 carry):

```bash
codex exec --sandbox read-only \
  --output-schema /Users/hyunbin/Capstone/_internal/state/ebqas_track/codex_검증/schema_review.json \
  -o /tmp/codex_ebqas_review_structured.json \
  "<위 prompt>"
```

schema는 별도 작성 시 다음 구조 권장:
```json
{
  "type": "object",
  "properties": {
    "verdict_overall": {"enum": ["pass", "concern", "fail"]},
    "axes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "axis": {"enum": ["a", "b", "c", "d", "e", "f"]},
          "verdict": {"enum": ["pass", "concern", "fail"]},
          "findings": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
          "recommendations": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
          "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    }
  }
}
```

본 schema는 본 spec 작성 시점에는 미작성 — 사용자 명시 시 별도 작성.

## 4. 디스패치 후 처리 절차

본 디스패치 실행·결과 회수 후 절차(다음 EB-QAS 세션):

1. log 파일 회수(`/tmp/codex_ebqas_review_*.log`) — exit code·token count·verdict 확인.
2. 6 축 verdict 분류:
   - 6 축 모두 pass → measure_ebqas 코드·test 활성화 OK, smoke 1 cell 진입 가능.
   - 일부 concern → 해당 축 finding 정독 → 코드/test 정정 → 본 review 재디스패치.
   - 일부 fail → 코드 fix 필수, 본 spec 재작성 후 재디스패치.
3. 결과를 `_internal/state/ebqas_track/codex_검증/codex_review_결과_<HHMMSS>.md`로 정제.
4. 정정 plan을 별도 spec(`codex_review_정정plan_<HHMMSS>.md`) 작성 → 사용자 승인 → 진행.

## 5. 환각 회피·트랙 위상

- 본 review는 코드·invariant 검증만 — "EB-QAS가 B1보다 낫다" 단언 X(측정 전).
- 본 review 결과로 측정 결과를 미리 예단 X — measure_ebqas 자체 측정 후 paired 4축 분석 결과로만 평가.
- 본 디스패치는 codex 전용 머신(Mac-mini.local)에서 수행 — `~/.claude/rules/multi-model.md` carry. 맥북에서 codex 실행 금지(refresh token 회전 충돌).
- 본 review 결과는 메인 트랙(handoff_230914 박성원 5/24 회신·5/26 LearnUs·5/28 포스터·6/11 보고서)과 분리 — 본 review의 어떤 finding도 메인 트랙 산출물에 inline 적용 X.
- 본 spec은 사용자 명시 디스패치 결정 시까지 carry — 변경 사항 발생 시 새 타임코드 파일(덮어쓰기 X).

## 6. 본 spec과 직전 codex_디스패치_spec_223921 사이 차이

| 위치 | 223921 (spec review) | 본 234413 (코드 review) | 차이 근거 |
|---|---|---|---|
| 입력 정본 | 7 파일 (spec·정본·README) | 10 파일 (+ 신규 코드·test·v4 대조·직전 결과) | 본 review 1차 대상이 코드 |
| 검증 대상 | 정본 anchor + spec 3건 + 평결 + 트랙 README + v2 대조 | measure_paper_exact.py 신규 11 항목 + test_ebqas.py 8 test + spec 4건(231042) + 정본 anchor + 평결 + 트랙 README + v4 대조 + 직전 결과 | 코드·test가 1차, spec은 2차 |
| 6 축 항목 | spec 수식·문장 검증 | 코드 동작·invariant 검증 | 본 review는 코드 단계 |
| 정정 권고 | spec patch | 코드/test fix | 본 review는 코드 fix |
| 후처리 | spec patch 5건 (231042 carry 완료) | 측정 진입 가능 verdict | 본 review는 launch gate |
| 디스패치 명령 | (직전 명령) | 본 §3 carry + 본 spec path 명시 | 본 spec 경로 추가 |

## 7. 본 review 결과 활용

- **6 축 모두 pass + 종합 verdict pass** → 활성화 완료, 다음 EB-QAS 세션에서 smoke 1 cell launch 가능.
- **일부 concern** → 본 세션 또는 다음 세션에서 코드/test 정정 후 본 review 재디스패치(같은 spec 사용 또는 정정 spec 별도 작성).
- **일부 fail** → 코드 즉시 fix + 본 spec 재작성 + 재디스패치.

본 review 결과는 measure_ebqas의 spec 준수성·invariant 정확성을 독립 검증할 뿐, EB-QAS의 측정 결과 우위/열위를 단정하지 않는다. 측정은 review pass 후 별도 단계 진입.
