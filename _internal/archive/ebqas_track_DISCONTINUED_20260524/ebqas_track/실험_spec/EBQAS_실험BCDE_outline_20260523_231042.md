# EB-QAS 실험 B~E outline — group key·label 분리 (Codex (d) concern 정정) + prequential evaluation

> 작성: 2026-05-23 23:10 KST. 출발 = 직전 222815 실험 B~E outline(`EBQAS_실험BCDE_outline_20260523_222815.md`) + Codex 적대 검증 결과 정제(`../codex_검증/codex_검증_20260523_225122.md` §2.4 (d) concern · 0.84 confidence). 본 문서는 직전 outline을 덮어쓰지 않고 신규 타임코드 파일로 분기하며, **§1.2 runtime group key vs benchmark analysis label 분리 + §1.2 threshold_bucket 결정 방식 명시 + §1.3 query stream 표기 정정 + §1.4 prequential evaluation 명시 + §1.4 Q-error assert** 5 patch를 반영한다. 직전 222815의 §0·§1.1·§1.5·§1.6·§1.7·§2·§3·§4·§5·§6·§7은 carry 유지(실험 C·D·E 부분 patch 없음 — Codex (d) concern은 실험 B group key가 핵심).

## 0. TL;DR

본 문서는 Codex (d) concern("현재 query true cardinality는 실행 후만 prior update, current sample double counting 금지, 전체 평균 selectivity prior 금지 룰은 명확. 다만 threshold_bucket을 dataset별 quantile로 만들거나 예시 group을 sel=0.001로 표기하는 부분은 위험 — 실제 optimizer가 모르는 target selectivity label을 group key에 넣으면 leakage")을 정정한다. 본 outline patch 5 항목.

| # | patch 위치 | 정정 내용 |
|---|---|---|
| §1.2 (1) | runtime group key vs benchmark analysis label 분리 명시 | runtime group key는 query metadata만 — `sel=...` label 절대 금지 |
| §1.2 (2) | threshold_bucket 결정 방식 명시 | log-scale D bucket (default) 또는 train-only quantile (option). dataset 전체 quantile 금지 |
| §1.3 | query stream 예시 표기 정정 | "Group 1: DEEP × sel=0.001 × Q1" → "Group 1: DEEP × threshold_bucket=B_low × Q1 (benchmark label = sel=0.001)" |
| §1.4 | prequential evaluation 명시 | query t 평가는 t−1까지의 history만 사용 — measure_ebqas 구현 invariant |
| §1.4 | Q-error assert 명시 | true cardinality는 query 실행 후만 — current query stop/update에 절대 사용 X assert |

직전 222815의 실험 C·D·E·hyperparam 권장 grid는 carry — 본 문서는 실험 B (online protocol)에 집중한다 (Codex (d) concern의 핵심 위치). 실험 C·D·E patch 필요 시 별도 신규 타임코드 파일.

---

## 1. 실험 B — 유사 query 반복 실행 online protocol (★ group key·label 분리 + prequential)

### 1.1 목적 — carry

EB-QAS는 정의상 history-aware다 — 정본 anchor §1 "이전 유사 query/predicate의 실행 결과"를 prior로 누적. 실험 A의 4-way matched(단발 query shuffle)는 cold-start·cell-내 누적까지만 검증하므로, 실험 B는 "유사 query가 sequential로 반복되는 online workload"에서 EB-QAS의 본의를 검증한다. Exqutor도 50-queries period로 sample size update를 trigger하므로, EB-QAS와 공정 비교를 위해 같은 query stream에서 양쪽 모두 history를 사용한다.

### 1.2 query group 정의 — ★ runtime group key vs benchmark analysis label 분리

직전 222815 §1.2는 runtime group key를 6-tuple로 정의하되 threshold_bucket의 결정 방식이 모호했다. Codex (d) finding 2 "threshold_bucket을 dataset별 quantile로 만들거나 예시 group을 sel=0.001로 표기하는 부분은 위험. 실제 optimizer가 모르는 target selectivity label을 group key에 넣으면 leakage" carry.

본 outline은 다음을 명시 분리한다.

#### (1) Runtime group key (planner가 사용 — leakage 금지)

```text
g_runtime = (
  table_id,
  vector_column,
  distance_metric,
  log_scale_threshold_bucket,           # ★ §1.2(2) 정의 — log-scale D bucket only
  template_id,
  normalized_scalar_predicate_signature # WHERE 절의 비-vector predicate 정규화
)
```

**금지**:
- `sel=0.001` 식 target selectivity label — optimizer가 planning 시점에 알 수 없음
- dataset 전체 quantile bucket — test query의 true selectivity 분포가 group boundary 결정에 leak
- query vector hash — 거의 매 query 새 group, history 누적 X
- raw float threshold — 같은 query group으로 묶이지 못함

**허용**:
- threshold bucket — §1.2(2) 정의 (log-scale D bucket 또는 train-only quantile)
- template_id — 정형 query template (TPC-H Q3 변형 등)
- scalar predicate signature — 정규화된 형태

#### (2) threshold_bucket 결정 방식 — ★ leakage-free option 2종

| Option | 정의 | leakage 여부 | 권장 시점 |
|---|---|---|---|
| **log-scale D bucket (default)** | distance threshold D의 log-scale 구간 — 예: `bucket = floor(log10(D))`. boundary는 dataset과 무관 | leakage X — query 자체 D만 사용 | 본 실험 B default |
| **train-only quantile (option)** | train query set의 D 분포로 quantile bucket boundary 결정 → test query는 동일 boundary 적용 | train·test 분리 시 leakage X. 단 train query가 실제 workload representative여야 | 사용자 명시 결정 시·long-running workload |
| ~~dataset 전체 quantile~~ | dataset의 vector 분포에서 quantile bucket 도출 | **leakage** (target selectivity label과 동치) | **금지** |

본 outline default는 `log-scale D bucket`. measure_ebqas 구현 시 `bucketize_threshold(threshold)` 함수가 본 정의를 따른다.

#### (3) Benchmark analysis label (보고용 — runtime group key X)

```text
benchmark_label = (dataset, scale_factor, selectivity_target)   # 예: (DEEP, sf=10, sel=0.001)
```

`sel=0.001`은 plot·table·summary 등 **analysis 단·보고용**으로만 사용. measure_ebqas의 `state[g_runtime]`에는 절대 사용 X.

본 분리로 group key는 leakage-free, benchmark label은 보고 편의성 유지.

### 1.3 query stream 구성 — ★ 예시 표기 정정

- 각 group당 **1000 queries sequential** 실행.
- query 순서: 4 mode(B1·EB-QAS·EB-QAS-no-history·CaseB) 동일 — paired 통제.
- 예시 group 구성 (★ 표기 정정 — §1.2(3) carry):

```text
Group 1: DEEP × threshold_bucket=B_low × Q1   (benchmark label = sel=0.001)
Group 2: DEEP × threshold_bucket=B_mid × Q1   (benchmark label = sel=0.01)
Group 3: SIFT × threshold_bucket=B_mid × Q1   (benchmark label = sel=0.01)
Group 4: WIKI × threshold_bucket=B_mid × Q1   (benchmark label = sel=0.01)
```

`B_low`·`B_mid`는 §1.2(2) log-scale D bucket — 예: DEEP의 L2 distance에서 `B_low = floor(log10(D)) = -2`(sel ≈ 0.001 영역), `B_mid = -1`(sel ≈ 0.01 영역). 실제 boundary는 measure_ebqas 구현 시 dataset별 calibration table로 정확 결정 (그러나 group key 자체는 boundary와 무관, query 자체 D 값만 사용).

`benchmark label`은 보고 단에서만 사용 — measure_ebqas의 runtime group key에는 절대 들어가지 않는다.

본 outline은 4 group 최소 — 활성화 시 자원 여유 기준 8-16 group으로 확장.

### 1.4 leakage 방지 — ★ prequential evaluation + Q-error assert 명시

직전 222815 §1.4 carry + 다음 추가.

#### (1) Prequential evaluation (Codex (d) finding 3 carry)

**원칙**: query t 평가는 t−1까지의 history만 사용 — train·test 분리가 sequential stream에서는 prequential evaluation으로 대체된다.

```text
for t in 1, 2, ..., 1000:
    # planning time (current state at end of step t-1)
    estimate_t = ebqas_estimate(query_t, state_g[g_runtime(query_t)], params)
    execute_query(query_t)
    true_cardinality_t = get_true_cardinality(query_t)
    q_error_t = max(estimate_t / true_cardinality_t, true_cardinality_t / estimate_t)

    # after execution (update state for query t+1 and beyond)
    update_after_execution(state_g[g_runtime(query_t)], true_cardinality_t, ...)
```

**금지**:
- query t의 true_cardinality를 query t planning에 사용
- 전체 query set 평균 selectivity를 사전에 prior로 사용 (test query 결과의 train prior leakage)
- query t의 sample 결과로 prior update를 한 뒤 같은 sample을 likelihood로 사용 (double counting)

**measure_ebqas 구현 invariant**: 위 3 금지 패턴을 unit test로 assert.

#### (2) Q-error assert (Codex (d) finding 3 carry)

```python
def _assert_no_true_cardinality_leakage(query_state_before, query_state_after, true_cardinality):
    """Q-error는 true cardinality 이후만 계산. current query stop/update에 절대 사용 X."""
    # query_state_before: ebqas_estimate 진입 시 state 스냅샷
    # query_state_after: ebqas_estimate 종료 시 state 스냅샷
    # ebqas_estimate는 state를 변경하지 않아야 함 — query-time estimation은 read-only
    assert query_state_before == query_state_after, \
        "ebqas_estimate가 state 변경 — current query에서 update 발생 (leakage)"

    # Q-error는 true_cardinality 사용 — query 실행 후만 계산
    # ebqas_estimate 반환 dict에 true_cardinality 키 X (실행 전이므로)
    assert "true_cardinality" not in estimate_result, \
        "ebqas_estimate 반환에 true_cardinality 키 — leakage (실행 전 cardinality 사용)"
```

본 assert는 measure_ebqas 구현 시 unit test로 적용. **invariant 위반 시 measure_ebqas launch 금지** — Codex (d) concern은 spec patch로만 해결 X, 구현 시 invariant 보장 필수.

#### (3) 직전 222815 §1.4 carry

**금지** (carry):
- 현재 query t의 true cardinality를 prior에 먼저 반영
- 전체 query set 평균 selectivity를 미리 계산해 prior로 사용
- test query 결과를 train prior에 사용

**허용** (carry):
- query t 실행 전: query 1 ~ t−1 결과만 prior 반영
- query t 실행 중: current sample만 likelihood
- query t 실행 후: true cardinality를 query t+1 이후 prior에 반영

### 1.5 cold/warm 분리 — carry

직전 222815 §1.5 그대로. 5 phase 분할 분석.

### 1.6 핵심 plot — carry + ★ 신규 plot 1개

직전 222815 §1.6 6 figure carry + 다음 1 plot 신규.

```text
Fig B.1  query index vs final sample size (B1 / EB-QAS / EB-QAS-no-history)
Fig B.2  query index vs Q-error moving average (window=50)
Fig B.3  query index vs posterior κ_g (EB-QAS only)
Fig B.4  query index vs early stop rate (window=50, EB-QAS·EB-QAS-no-history)
Fig B.5  selectivity별 Q-error boxplot (sel ∈ {0.001, 0.01, 0.10} benchmark label)
Fig B.6  latency vs method × subset (plan_changed·low-selectivity·high-dimensional)
★ Fig B.7  query index vs prior_mode trajectory (history/no_history) + mode_switch_events markers (EB-QAS only)
```

Fig B.7은 본 spec patch T1·T4 영향 — explicit mode switch가 실제 workload에서 언제 발동되는지 시각화. 실험 C (prior mismatch stress)와 cross-check.

### 1.7 환각 회피·평결 호환성 — carry + ★ 본 patch carry

직전 222815 §1.7 carry. 추가로 본 patch:
- **runtime group key vs benchmark label 분리 (§1.2 patch)**: leakage-free group key 보장 — 5/23 평결 §A.4(paired 비교 통제)·정본 anchor §B.3(leakage 방지)와 일관.
- **threshold_bucket log-scale D 명시 (§1.2(2) patch)**: dataset 전체 quantile leakage 차단.
- **prequential evaluation 명시 (§1.4 patch)**: train·test 분리 invariant.
- **Q-error assert (§1.4 patch)**: measure_ebqas 구현 시 unit test로 invariant 보장.

본 patch 후에도 "EB-QAS가 B1보다 낫다" 단언 X — 측정 결과로만 평가.

---

## 2. 실험 C — prior mismatch stress test — carry (직전 222815 §2 그대로)

직전 222815 §2 전체 carry. 본 spec patch 영향:
- 실험 C의 EB-QAS-safe variant는 본 spec T1 (`EBQAS_구현_의사코드_20260523_231042.md` §4.2)의 explicit mode switch를 base로 사용. Case C.1·C.2 모두 mode switch 발동 시점·B1 cap fallback 동작을 실증.
- EB-QAS-unsafe variant (κ cap·decay·mismatch reset 모두 비활성)와의 격차가 Codex (b) fail 정정 효과의 직접 검증.

## 3. 실험 D — latency 평가 — carry (직전 222815 §3 그대로)

직전 222815 §3 전체 carry. 본 spec patch 영향:
- 실험 D의 6 subset 분할 중 `injection_fired=True only`·`plan_changed_vs_B1=True` subset에서 mode switch 발동 query는 별도 분류 (mode switch 후 sample size·latency 변화).

## 4. 실험 E — ablation study — carry (직전 222815 §4 그대로)

직전 222815 §4 전체 carry. 본 spec patch 영향:
- 실험 E의 variant 6종(특히 `EB-QAS-no-reset`·`EB-QAS-large-kappa`)이 본 spec T1 mode switch와 비교 base — `EB-QAS-no-reset`은 mode switch 없는 variant로 정의하고 `EB-QAS-full`과 paired 비교.

## 5. hyperparam 권장 grid — carry + ★ 신규 hyperparam 3개

직전 222815 §5 carry + 다음 3개 신규.

### 5.0 본 spec T1 신규 hyperparam (Codex (b) 정정 carry)

| Hyperparam | 정의 | 권장 | default |
|---|---|---|---|
| `w_mismatch` | mismatch query 시 별도 update weight | 0·1·2·5 | 1 |
| `mismatch_n_threshold` | mode switch 발동 연속 mismatch streak | 2·3·5·10 | 3 |
| `n_recovery` | history 회복 발동 연속 stable streak | 10·20·50·∞ (회복 X) | 20 |

### 5.1~5.8 carry

직전 222815 §5.1~5.8 그대로. `batch_size`·`τ`·`w`·`ρ`·`κ_max`·`γ`·`n_min`·`n_cap` 권장 grid + default 조합.

---

## 6. 본 outline의 활성화 시 정식 spec 확장 절차 — carry

직전 222815 §6 carry. 실험 B 정식 spec 확장 시 본 신규 outline §1.2~1.4 patch 그대로 반영.

## 7. 환각 회피·트랙 위상 — carry + ★ 본 patch carry

직전 222815 §7 carry. 추가로 본 patch:
- runtime group key는 leakage-free — `sel=...` label 절대 사용 X.
- threshold_bucket은 log-scale D bucket (default) 또는 train-only quantile (option) — dataset 전체 quantile 금지.
- benchmark label은 보고용 only — measure_ebqas runtime state에 들어가지 않음.
- prequential evaluation·Q-error assert는 measure_ebqas 구현 시 unit test로 invariant 보장.

본 patch 완료가 "실험 B group key·label 분리 spec patch 완료"를 의미 — measure_ebqas 코드 작성 단계 진입 가능 (T1·T3 patch와 함께).

## 8. 본 신규 outline과 222815 사이 변경 요약

| 위치 | 222815 | 본 신규 (231042) | 정정 근거 |
|---|---|---|---|
| §1.2 group key | 6-tuple 명시 (threshold_bucket·template_id·scalar_predicate_signature) | (1) runtime group key (planner 사용) + (2) threshold_bucket 결정 방식 (log-scale D default / train-only quantile option / dataset 전체 quantile **금지**) + (3) benchmark analysis label (보고용 only) 3 항목 분리 | Codex §2.4 (d) finding 2 + 권고 1·2 |
| §1.3 query stream 예시 | "Group 1: DEEP × sel=0.001 × Q1" | "Group 1: DEEP × threshold_bucket=B_low × Q1 (benchmark label = sel=0.001)" | Codex §2.4 (d) 권고 1 |
| §1.4 leakage 방지 | 금지·허용 list 4 항목 | + prequential evaluation 명시 + Q-error assert 코드 예시 + measure_ebqas 구현 invariant 명시 | Codex §2.4 (d) finding 3 + 권고 3 |
| §1.6 핵심 plot | 6 figure | + Fig B.7 (prior_mode trajectory + mode_switch_events markers) 신규 | T1 patch carry |
| §5.0 신규 hyperparam | (없음) | w_mismatch·mismatch_n_threshold·n_recovery 3개 신규 (default 1·3·20) | T1 patch carry |
| §1.1·§1.5·§1.7·§2·§3·§4·§5.1~5.8·§6 | (직전) | carry (변경 없음 또는 cross-ref 추가만) | — |

222815는 carry로 유지. 본 신규 231042는 measure_ebqas 코드 작성 시 base outline — 실험 B의 group key·label 분리·prequential evaluation·Q-error assert 모두 적용.
