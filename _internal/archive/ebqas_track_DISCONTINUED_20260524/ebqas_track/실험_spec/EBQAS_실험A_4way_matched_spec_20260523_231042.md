# EB-QAS 실험 A spec — CaseB comparator 사전 고정 + paired effect size 교체 (Codex (c) concern 정정)

> 작성: 2026-05-23 23:10 KST. 출발 = 직전 222815 실험 A spec(`EBQAS_실험A_4way_matched_spec_20260523_222815.md`) + Codex 적대 검증 결과 정제(`../codex_검증/codex_검증_20260523_225122.md` §2.3 (c) concern · 0.82 confidence). 본 문서는 직전 spec을 덮어쓰지 않고 신규 타임코드 파일로 분기하며, **§1.1 CaseB comparator 사전 고정 + §4.2 paired effect size 교체 + §5.3 output JSON 보강 (query-level row + join invariant unit test) 3 patch**를 반영한다. 직전 222815의 §0·§1.2·§2·§3·§4.1·§4.3·§5.1·§5.2·§5.4·§6·§7·§8·§9는 carry 유지.

## 0. TL;DR

본 문서는 Codex (c) concern("4-way matched 구조와 동일 seed/query_set/trial_idx/query_idx 통제는 잘 잡혀 있으나 CaseB가 method_name을 필요로 하는데 어느 method의 CaseB인지 고정 X, Cliff's δ는 paired 설계에 약간 어긋남")을 정정한다. 본 spec patch 3 항목.

| # | patch 위치 | 정정 내용 |
|---|---|---|
| §1.1 | CaseB comparator 사전 고정 | strong-13 aggregate (default) / 대표 method (option) / v14 CaseC dual-Bernoulli (option) 중 사전 고정 |
| §4.2 | paired effect size 교체 | Cliff's δ → matched rank-biserial 또는 sign-based effect size |
| §5.3 | output JSON 보강 | query-level row 저장 (`cell·trial_idx·query_idx` join invariant) + 4 mode paired join + invariant unit test |

직전 222815 spec의 나머지(데이터셋 축·metric 20개·paired Δ% 식·measure cycle 구조·leakage 방지·환각 회피·시간 견적·다음 단계)는 그대로 carry — 본 문서는 carry 원본을 가리키되 patch만 명시한다.

---

## 1. 비교 대상 (mode 정의) — §1.1 patch

### 1.1 필수 4 mode (★ CaseB comparator 사전 고정)

직전 222815는 표에서 CaseB의 method를 명시하지 않았다. Codex (c) finding 2 "CaseB가 `method_name`을 필요로 하는데 실험 A의 'CaseB'가 어느 method의 CaseB인지 고정되어 있지 않다 (`measure_paper_exact.py:1087`)" — 비교 baseline이 흔들릴 위험이 있다.

본 spec은 CaseB의 method를 다음 3 옵션 중 사전 고정한다.

| Comparator 옵션 | 정의 | 선정 근거 | 권장 시점 |
|---|---|---|---|
| **strong-13 aggregate (default)** | strong-13 method(P3 Streaming·P4 DimReduction·P2 Spatial·P9 InfoTheoretic·P5 QMC·P6 Quantization 계열) 13종의 trial-level Q-error 산술평균을 CaseB estimate로 사용 — 한 method가 portfolio bias를 결정하지 않게 분산 | 5/23 평결 §0 호환 (분포 인지 효과 X 검증 base) + portfolio 평균 효과 추적 (CaseB의 통계적 정체를 그대로 보임) | 본 실험 A 활성화 시 default |
| **대표 method (option)** | 사용자 명시 결정 시 선정한 단일 method (예: cs_pca·skilling_hilbert) | 단일 method 비교가 필요할 때 — 특정 paradigm 효과 분리 | 사용자 결정 시 |
| **v14 CaseC dual-Bernoulli (option)** | v14 CaseC dual-Bernoulli 통제군 (메인 트랙) — `est_final = (est_B1 + est_B1') / 2` 형식의 무작위 해시 ensemble | 메인 트랙 v14 paused 해소 후 활성화 시 — CaseB의 "앙상블 평균 효과" 정체를 정량 비교 | v14 재개 후 |

| Mode | 정의 | 출처 |
|---|---|---|
| **B1** | Exqutor §V-B Bernoulli Adaptive Sampling 그대로 | Capstone 기존 `measure_b1_paper` (라인 361) |
| **CaseB** | **strong-13 aggregate (default)** — `est_final = (est_B1 + est_aggregate) / 2`. `est_aggregate = mean(est_method_i for i in strong_13)` | Capstone 기존 `measure_case_b` (라인 1087) + analysis 단 aggregate |
| **EB-QAS** | empirical-Bayes posterior mean. query group prior 누적·posterior Q-risk 조기 종료·**explicit mode switch fallback (b 정정)** | 신규 `measure_ebqas` (의사코드 신규 spec `EBQAS_구현_의사코드_20260523_231042.md`) |
| **EB-QAS-no-history** | EB-QAS와 동일하나 `prior_mode="no_history"` 강제. ablation | 신규 `measure_ebqas`의 `prior_mode="no_history"` 옵션 |

**activation note**: 측정 launch 시점에 CaseB comparator 옵션 1건을 명시 선정(default = strong-13 aggregate). 결정 결과를 measure_ebqas launch 직전 본 spec §1.1에 inline 기록 + activation handoff에 명시.

### 1.2 선택 5 ablation variant — carry

| Variant | 정의 | 역할 |
|---|---|---|
| EB-QAS-no-stop | posterior mean은 사용하되 n_cap까지 항상 sampling. early stopping 효과 분리 | sample size 감소 효과 분리 |
| EB-QAS-fixed-kappa | κ를 고정하고 update X | 안전장치 효과 분리 |
| EB-QAS-large-kappa | κ_max 100 → 1000 | over-shrinkage 위험 확인 |
| EB-QAS-small-kappa | κ_max 100 → 10 | prior 효과 하한 확인 |
| CS-EBQAS | confidence sequence guard 추가 | sequential stopping 이론적 안전성 |

선택 variant는 활성화 시 자원 여유 기준 선별 — 직전 222815 carry.

## 2. 데이터셋·변인 축 — carry

직전 222815 §2 그대로. 8 dataset × 3 sf × 3 selectivity = 72 cell. sf=100 concat 부분 미측정은 honest limitation 그대로.

## 3. 핵심 metric (20개) — carry

직전 222815 §3 그대로. accuracy 6 + sampling cost 5 + latency 9. 단 §3.2 `early_stop_rate`는 본 spec patch에 따라 `state.early_stop=True` 였던 query 비율로 정밀화 (mode switch 후 false로 강제된 query는 분모 제외 또는 별도 추적).

## 4. paired 비교 정의

### 4.1 paired Δ% 식 — carry

직전 222815 §4.1 그대로. 같은 cell·sel·trial·query 조건에서 4 mode 동시 측정 → 4 mode 사이 paired Δ%:

```
Δ% = 100 · (Q_method − Q_B1) / Q_B1
```

핵심 4 paired pair:
- EB-QAS vs B1
- EB-QAS vs CaseB
- EB-QAS-no-history vs B1
- EB-QAS-no-history vs EB-QAS

### 4.2 통계량 (각 pair 별) — ★ paired effect size 교체

직전 222815는 Cliff's δ를 ordinal effect size로 사용했다. Codex (c) finding 3 "Cliff's δ는 독립 표본 효과크기로 쓰이는 경우가 많아 paired 설계와 약간 어긋난다 — paired delta 분포에는 matched rank-biserial 또는 sign-based effect size가 더 직접적이다" carry.

본 spec patch는 통계량을 다음 4축으로 정리한다.

| 통계량 | 정의 | 직전 222815 → 본 patch |
|---|---|---|
| `better_count`·`better_ratio` | Δ% < 0인 paired 측정 수·비율 | carry |
| `median_delta_percent`·`mean_delta_percent` | paired Δ% 중앙값·평균 | carry |
| `Wilcoxon signed-rank p-value` | paired 비교 비모수 검정 | carry |
| ★ `matched rank-biserial r_rb` | paired delta 분포의 effect size — `r_rb = (W+ − W−) / (W+ + W−)` (Wilcoxon W+·W− 기반) | **신규** (Cliff's δ 대체) |
| ★ `sign-based effect size` | `2 · (better_ratio − 0.5)` 또는 Hodges-Lehmann median 기반 | **신규** (선택, matched rank-biserial 보강) |
| `bootstrap 95% CI` | median Δ%의 paired bootstrap CI (n_resample = 10000) | carry |

본 spec patch는 Cliff's δ를 폐기하고 matched rank-biserial을 default effect size로 채택한다. **결론 단언 기준**: `better_ratio + Wilcoxon p-value + matched rank-biserial + bootstrap 95% CI` 4축이 모두 일관(better_ratio > 0.6 + Wilcoxon p < 0.05 + |r_rb| > 0.2 + CI가 0을 포함하지 않음) 시에만 결론. 5/23 평결 §1.1 carry — 단순 better_ratio만으로 "우위" 단언 금지.

**aggregate 처리**: CaseB의 method가 strong-13 aggregate일 때, paired delta는 `Q_CaseB(trial, query) − Q_B1(trial, query)`로 계산 — aggregate는 estimate 단에서만 산술평균, paired delta는 query-level 일대일 통제. trial-level aggregate에서 분산이 줄어드는 효과는 별도 ablation으로 보고 (CaseB 통제군 CaseB′ = (B1+B1')/2와 동일 구조).

### 4.3 subset paired 비교 — carry

직전 222815 §4.3 그대로. `plan_changed_vs_B1=True`·low-selectivity(sel=0.001)·high-dimensional(WIKI·concat) subset에서 paired Δ% 별도 산출 → H4 검증.

## 5. 측정 cycle 구조

### 5.1 현 measure 코드 구조 — carry

직전 222815 §5.1 그대로. measure 코드 4분리 구조: `measure_b1_paper`(361)·`measure_case_a`(986)·`measure_case_b`(1087)·`measure_case_c`(1195). 측정 cycle/runner 단에서 trial loop로 묶어 호출.

### 5.2 EB-QAS 측정 함수 spec — carry + ★ 신규 필드 4개

직전 222815 §5.2 carry. 추가로 신규 의사코드(`EBQAS_구현_의사코드_20260523_231042.md` §2.2) patch에 따라 measure_ebqas 반환 dict에 다음 4 키 추가 명시.

```python
{
    # 직전 222815 carry 키 + 다음 신규 키
    "prior_mode_trajectory": [...],          # 신규 — query별 prior_mode ("history"|"no_history") trajectory
    "consecutive_mismatch_trajectory": [...],# 신규 — query별 consecutive_mismatch streak
    "stable_query_count_trajectory": [...],  # 신규 — query별 stable_query_count streak
    "mode_switch_events": [...],             # 신규 — (query_idx, "no_history"|"history") 발동 시점 list
    # 기존 222815 carry
    "posterior_kappa_trajectory": [...],
    "posterior_mu_trajectory": [...],
    "mismatch_count_total": ...,
    ...
}
```

mode switch trajectory는 실험 C (prior mismatch stress) 분석의 핵심 데이터 — Codex (b) 정정의 효과 실증 base.

### 5.3 측정 runner 4-way matched 호출 — ★ output JSON 보강 (query-level row + join invariant)

직전 222815 §5.3 carry + 다음 patch.

직전 222815 §5.3은 mode별 1 파일(`<cell.sub>_B1.json`·`<cell.sub>_CaseB.json`·`<cell.sub>_EBQAS.json`·`<cell.sub>_EBQAS-no-history.json`) → analysis 단에서 paired join이었다. 본 patch는 paired join 정확성을 측정 단에서 보장하기 위해 query-level row를 명시 저장한다.

**query-level row schema** (각 mode JSON 안):

```json
{
  "cell": "DEEP_sf10_sel0.01_K10",
  "fig": "fig5_3",
  "dataset": "DEEP",
  "sf": 10,
  "selectivity": 0.01,
  "mode": "EB-QAS",
  "prior_mode_initial": "history",
  "trials": [
    {
      "trial_idx": 0,
      "seed": 42,
      "query_results": [
        {
          "query_idx": 0,
          "query_id": "DEEP_sf10_sel0.01_K10_t0_q0",
          "true_cardinality": 1234,
          "estimated_cardinality": 1198.7,
          "q_error": 1.029,
          "sample_size": 128,
          "hits": 12,
          "posterior_alpha": 13.0,
          "posterior_beta": 117.0,
          "posterior_q_risk_log": 1.21,
          "posterior_q_risk_stop": 1.21,
          "early_stopped": true,
          "prior_mode_at_query": "history",
          "consecutive_mismatch_after": 0,
          "stable_query_count_after": 1,
          "exec_ms": 12.7
        },
        ...
      ]
    },
    ...
  ],
  "summary": {
    "avg_q_error_trimmed": ...,
    "q_error_median": ...,
    ...
  }
}
```

**join invariant**: 4 mode JSON에서 query-level row를 `(cell, trial_idx, query_idx)` 3-tuple로 join 시 row 수가 4 mode에서 정확히 일치 — 측정 단 invariant.

**invariant unit test** (analysis 단 진입 전):

```python
def assert_paired_join_invariant(json_b1, json_caseb, json_ebqas, json_ebqas_no_history):
    """4-way paired join invariant assert.

    1. (cell, trial_idx, query_idx) 3-tuple 일대일 매칭
    2. mode 라벨 {"B1", "CaseB", "EB-QAS", "EB-QAS-no-history"}
    3. seed 일관 (4 mode 같은 trial_idx에서 같은 seed)
    4. true_cardinality 일관 (4 mode 같은 query_id에서 같은 true value)
    """
    keys_b1 = {(r["trial_idx"], q["query_idx"]) for r in json_b1["trials"] for q in r["query_results"]}
    keys_caseb = {(r["trial_idx"], q["query_idx"]) for r in json_caseb["trials"] for q in r["query_results"]}
    keys_ebqas = {(r["trial_idx"], q["query_idx"]) for r in json_ebqas["trials"] for q in r["query_results"]}
    keys_ebqas_nh = {(r["trial_idx"], q["query_idx"]) for r in json_ebqas_no_history["trials"] for q in r["query_results"]}

    assert keys_b1 == keys_caseb == keys_ebqas == keys_ebqas_nh, \
        f"4-way paired join 실패: {keys_b1 ^ keys_ebqas}"

    # seed·true_cardinality 일관 검증 (단순 sample 1건씩)
    for trial_idx, query_idx in keys_b1:
        b1_row = _find(json_b1, trial_idx, query_idx)
        caseb_row = _find(json_caseb, trial_idx, query_idx)
        ebqas_row = _find(json_ebqas, trial_idx, query_idx)
        ebqas_nh_row = _find(json_ebqas_no_history, trial_idx, query_idx)

        assert b1_row["true_cardinality"] == caseb_row["true_cardinality"] == \
               ebqas_row["true_cardinality"] == ebqas_nh_row["true_cardinality"], \
            f"trial={trial_idx}, query={query_idx} true_cardinality 불일치"
```

**핵심 제약 (5/23 평결 §A.4 carry · Codex (c) finding 1 carry)**:
- 동일 `seed`·동일 `query_set`·동일 `trial_idx`에서 4 mode 측정 — paired 비교 통제.
- query 순서 4 mode 동일.
- output query-level row JSON → analysis 단에서 `(cell, trial_idx, query_idx)` join.

### 5.4 leakage 방지 — carry

직전 222815 §5.4 그대로. 본 spec patch는 `prior_mode_at_query`·`consecutive_mismatch_after` 등 신규 필드를 query-level row에 명시 — leakage 검출 가능성 ↑.

## 6. 환각 회피·5/23 평결 호환성 재확인 — carry + ★ 본 patch carry

직전 222815 §6 carry. 본 patch 3 항목이 추가로 평결 4축 호환성에 미치는 영향.

- **CaseB comparator 사전 고정 (§1.1 patch)**: strong-13 aggregate default로 "CaseB의 통계적 정체는 portfolio 평균 효과"를 frame 그대로 유지 — 5/23 평결 §0 carry. 단일 method comparator는 사용자 결정 시에만.
- **paired effect size 교체 (§4.2 patch)**: matched rank-biserial은 paired delta 분포에 직접 — Cliff's δ 독립표본 가정 X. "EB-QAS가 B1보다 낫다" 단언 기준이 더 엄격해짐 (4축 일관 시만 결론).
- **output JSON 보강 (§5.3 patch)**: query-level row + join invariant unit test — paired 비교의 측정 단 invariant. paired delta가 측정 오류로 흔들리지 않게 보장.

"EB-QAS가 B1보다 낫다" 단언 X — 본 spec은 측정 결과 평가의 토대일 뿐.

## 7. 측정 일정·자원 견적 — carry

직전 222815 §7 carry. **본 spec 활성화는 다음 3 조건 모두 충족 시**:
1. Codex (b) fail 정정 완료 — `EBQAS_구현_의사코드_20260523_231042.md` §4.2 patch 본 spec carry ✓
2. Codex (c) concern 정정 완료 — 본 spec §1.1·§4.2·§5.3 patch ✓
3. 사용자 명시 활성화 결정 — default 6/11 이후, CaseB comparator 옵션 1건 선정

위 3 조건 충족 후 measure_ebqas 코드 작성·smoke·24 cell 측정 단계 진입 가능.

## 8. 본 spec과 정본 anchor 사이 정정 사항 — carry

직전 222815 §8 carry. 본 spec patch는 정본 anchor 본문 inline 수정 X — spec 단 patch만.

## 9. 다음 단계 — carry + ★ 본 patch carry

직전 222815 §9 carry. 추가로 본 spec patch가 다음 단계에 미치는 영향.

1. **활성화 결정 시점**: CaseB comparator 옵션(strong-13 aggregate / 대표 method / v14 CaseC dual-Bernoulli) 사용자 명시 결정 — activation handoff에 inline 기록.
2. **measure_ebqas 구현 시**: `EBQAS_구현_의사코드_20260523_231042.md` §2.2 신규 4 필드 + §3.2 Q_post floor 분리 + §4.2 mode switch + §4.5 hyperparam 7개 사용. 본 spec §5.2 신규 4 trajectory 키 산출.
3. **분석 단계 진입 시**: §5.3 invariant unit test 통과 → §4.2 통계량 4축 일관 시만 결론 단언.
4. **실험 B 진입 시**: 본 spec §5.3 query-level row schema와 호환되도록 실험 B outline 신규 (`EBQAS_실험BCDE_outline_20260523_231042.md`) §1.4 prequential evaluation invariant 사용.

본 spec은 활성화 시점까지 carry — 변경 사항 발생 시 새 타임코드 파일로 갱신(덮어쓰기 X).

## 10. 본 신규 spec과 222815 사이 변경 요약

| 위치 | 222815 | 본 신규 (231042) | 정정 근거 |
|---|---|---|---|
| §1.1 CaseB comparator | method 명시 X | strong-13 aggregate (default) / 대표 method / v14 CaseC dual-Bernoulli 중 사전 고정 — default = strong-13 aggregate | Codex §2.3 (c) finding 2 + 권고 1 |
| §1.1 EB-QAS 정의 | (직전) | + **explicit mode switch fallback (b 정정)** 명시 — `EBQAS_구현_의사코드_20260523_231042.md` cross-ref | T1 carry |
| §3.2 early_stop_rate | (직전) | `state.early_stop=True` 였던 query 비율 — mode switch 후 false로 강제된 query는 별도 추적 | T1 patch carry |
| §4.2 paired effect size | Cliff's δ | matched rank-biserial r_rb (default) + sign-based effect size (선택) | Codex §2.3 (c) finding 3 + 권고 3 |
| §4.2 결론 단언 기준 | better_ratio + Wilcoxon + Cliff's δ + bootstrap CI 3축 일관 | better_ratio + Wilcoxon + matched rank-biserial + bootstrap CI 4축 일관 (이상 더 엄격) | 본 patch + 5/23 평결 §1.1 |
| §5.2 measure_ebqas 반환 dict | 기존 trajectory 키 | + `prior_mode_trajectory·consecutive_mismatch_trajectory·stable_query_count_trajectory·mode_switch_events` 4 신규 키 | T1 patch carry |
| §5.3 output JSON | mode별 1 파일 → analysis 단 paired join | query-level row schema 명시 + invariant unit test (`assert_paired_join_invariant`) | Codex §2.3 (c) 권고 2 |
| §1.2·§2·§3·§4.1·§4.3·§5.1·§5.4·§6·§7·§8·§9 | (직전) | carry (변경 없음 또는 cross-ref 추가만) | — |

222815는 carry로 유지. 본 신규 231042는 measure_ebqas 코드 작성 시 base spec — CaseB comparator 옵션·invariant unit test·paired effect size 4축 모두 적용.
