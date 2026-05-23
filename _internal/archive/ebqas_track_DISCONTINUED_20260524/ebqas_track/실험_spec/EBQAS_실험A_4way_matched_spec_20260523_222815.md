# EB-QAS 실험 A — 4-way matched 측정 spec (한국어 학술 정제)

> 작성: 2026-05-23 22:28 KST. 출발 문서 = EB-QAS 정본 anchor `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` §15·§A. 본 spec은 정본 anchor의 실험 A를 한국어 학술 산문으로 정제하고, 본 EB-QAS 세션 plan(`~/.claude/plans/abstract-jumping-crab.md`)이 발견한 정정 사항(현 measure 코드는 `measure_3way` 단일 함수가 없고 `measure_b1_paper`·`measure_case_a/b/c` 4분리 구조)을 반영한다. **본 spec은 측정 코드 patch 지침이 아니라 측정 spec 문서다 — 구현·launch는 활성화 결정 후 별도 세션.**

## 0. TL;DR

본 실험 A는 본 연구의 기존 3-way matched(B1·CaseA·CaseB) 측정 구조를 4-way matched(B1·CaseB·EB-QAS·EB-QAS-no-history)로 확장한다. 같은 cell·selectivity·strata·trial·query 조건에서 4 mode를 동시에 산출해 paired 비교(Δ%·Wilcoxon·Cliff's δ·bootstrap CI)로 EB-QAS의 Q-error·sample size·sampling overhead·latency 효과를 통계적으로 검증한다. CaseA(완전 대체, 음성 대조군)는 5/23 감사 평결로 portfolio 악화가 이미 입증됐으므로 본 실험 A에는 포함하지 않으나, 평결 호환성 재확인 차원에서 ablation variant로 EB-QAS-no-history(Beta(1,1) only)를 포함해 prior history 효과를 분리한다.

- 비교 대상: 4 mode(필수) + 5 ablation variant(선택)
- 데이터셋 축: 8 dataset × 3 sf × 3 selectivity = 72 cell (단, sf=100 concat 일부는 본 plan 시점 미측정 자원)
- 핵심 metric: accuracy 6 + sampling cost 5 + latency 9 = 20개
- 측정 cycle: 신규 `measure_ebqas` 함수 + 기존 `measure_b1_paper`·`measure_case_b` 호출을 trial loop에서 같은 trial/query 조건으로 묶어 4-way matched 산출
- 측정 일정: 활성화 결정 후 별도 (default 6/11 이후 — 본 spec은 구현·launch 지침 X, spec 문서)

## 1. 비교 대상 (mode 정의)

### 1.1 필수 4 mode

| Mode | 정의 | 출처 |
|---|---|---|
| **B1** | Exqutor §V-B Bernoulli Adaptive Sampling 그대로. momentum·LR scheduler·N=385 fixed 또는 adaptive cap. | Capstone 기존 `measure_b1_paper` (라인 361) — 메인 트랙 측정과 동일 |
| **CaseB** | `est_final = (est_B1 + est_method) / 2` 산술평균. 5/23 평결로 “분포 인지가 아닌 앙상블 효과”로 재해석된 결합 mode. | Capstone 기존 `measure_case_b` (라인 1087) |
| **EB-QAS** | empirical-Bayes posterior mean `p̂ = (κ_g/(κ_g+n))μ_g + (n/(κ_g+n))(s/n)`. query group prior 누적·posterior Q-risk 조기 종료·κ cap·decay·mismatch reset. | 신규 `measure_ebqas` (본 spec 정의, 측정 코드 patch는 활성화 후 별도 세션) |
| **EB-QAS-no-history** | EB-QAS와 동일하나 prior history 미누적. `Beta(1,1)`만 사용해 Bayesian formula 자체 효과(shrinkage 무·약 prior)와 history-aware prior 효과 분리. ablation 핵심. | 신규 `measure_ebqas`의 `prior_mode="no_history"` 옵션 |

### 1.2 선택 5 ablation variant

| Variant | 정의 | 역할 |
|---|---|---|
| **EB-QAS-no-stop** | posterior mean은 사용하되 n_cap까지 항상 sampling. early stopping 효과 분리. | sample size 감소 효과 분리 |
| **EB-QAS-fixed-kappa** | κ를 고정하고 update X. κ cap·decay·mismatch reset 비활성. | 안전장치 효과 분리 |
| **EB-QAS-large-kappa** | κ_max를 100 → 1000으로 확대. over-shrinkage 위험 확인. | prior strength 한계 확인 |
| **EB-QAS-small-kappa** | κ_max를 100 → 10으로 축소. prior 효과 약화 시 B1과 동등 수렴 검증. | prior 효과 하한 확인 |
| **CS-EBQAS** | EB-QAS에 confidence sequence guard(Kuchibhotla 2021 PMLR v139) 추가. optional stopping 문제 보강. | sequential stopping 이론적 안전성 |

선택 variant는 활성화 시 자원 여유 기준 선별 — 본 spec은 4 mode를 baseline, 5 variant를 ablation으로 분류한다.

## 2. 데이터셋·변인 축

### 2.1 dataset (8종)

본 연구 메인 트랙과 동일 — Capstone 기존 측정 portfolio를 그대로 따른다.

- 단일: DEEP / SIFT / SimSearchNet++(SSN) / YFCC / WIKI
- concat 3종: DEEP+WIKI / DEEP+SIFT / DEEP+YFCC

본 트랙 활성화 시 sf=100 concat 일부 미측정 cell(메인 트랙 honest limitation §10에 carry)은 본 실험 A에서도 그대로 부분 적용.

### 2.2 scale factor (sf)

- sf ∈ {1, 10, 100}

sf=10은 박광현 5/22 미팅 핵심 평면(메인 트랙 측정 base). sf=100은 메인 트랙 honest limitation — 본 실험 A에서도 일관.

### 2.3 selectivity

- sel ∈ {0.001, 0.01, 0.10}

본 연구 핵심 3 평면. low-selectivity(0.001)에서 EB-QAS의 prior shrinkage가 zero-hit 완화로 작동하는지 H2 검증.

### 2.4 mode

§1.1의 4 필수 mode. 선택 5 variant는 활성화 시 별도 결정.

### 2.5 cell 수 견적

기본 72 cell(8 × 3 × 3). 활성화 시 자원 여유 기준 priority subset:
- **우선 (24 cell)**: DEEP·SIFT·WIKI × sf{1,10} × sel{0.001,0.01,0.10} + concat 미포함 (cold-start·warm-start 분리 가능 핵심 데이터셋)
- **다음 (24 cell)**: SSN·YFCC × sf{1,10} × sel + WIKI sf=100
- **나머지 (24 cell)**: concat × sf{10,100} (sf=100 일부 honest limitation 그대로)

## 3. 핵심 metric (20개)

### 3.1 Accuracy (6)

| Metric | 정의 | 출처 |
|---|---|---|
| `q_error_mean_trimmed` | TRIM(0.05)·trimmed mean Q-error | 메인 트랙 v13 정본 metric |
| `q_error_median` | 중앙값 Q-error | 〃 |
| `q_error_p95` | 95-percentile Q-error | 정본 anchor §13.1 |
| `q_error_p99` | 99-percentile Q-error | 〃 |
| `extreme_q_error_count` | Q-error > 10 카운트 | 정본 anchor §13.1 (extreme 완화 H2) |
| `zero_estimate_count` | C_hat = 0 카운트 | 정본 anchor §13.1 (zero-hit 완화 H2) |

### 3.2 Sampling cost (5)

| Metric | 정의 | 출처 |
|---|---|---|
| `final_size_mean` | 평균 최종 sample 수 | 정본 anchor §13.1·H3 |
| `final_size_median` | 중앙값 최종 sample 수 | 〃 |
| `final_size_std` | 최종 sample 수 표준편차 | 〃 |
| `actual_distance_computations` | 실제 distance 계산 횟수(N=385 기준 — adaptive cap 사용 시 ↓) | 정본 anchor §11.4·§13.2 |
| `early_stop_rate` | posterior Q-risk ≤ τ로 조기 종료 비율 | 신규(EB-QAS·EB-QAS-no-history만) |

### 3.3 Latency (9)

| Metric | 정의 | 출처 |
|---|---|---|
| `exec_ms_trimmed` | trimmed mean 실행 시간 | 메인 트랙 latency PoC |
| `exec_ms_median` | 중앙값 실행 시간 | 〃 |
| `speedup_vs_B1` | B1 대비 speedup | 정본 anchor §A.4 |
| `speedup_vs_CaseB` | CaseB 대비 speedup | 〃 |
| `speedup_vs_baseline` | injection 없음 대비 speedup | latency PoC `analyze_latency.py` |
| `plan_changed_vs_baseline` | baseline plan vs current plan 변경 여부 | 〃 |
| `plan_changed_vs_B1` | B1 plan vs current plan 변경 여부 | 〃 |
| `injection_fired` | cardinality estimate injection 실제 적용 여부 | 〃 (5/23 평결 §4 carry — MISS 시 제외) |
| `timeout_count` | timeout query 수 | 〃 |

본 실험 A는 **Q-error·sample size·sampling overhead를 우선**으로 보고, latency는 plan-sensitive subset에 한정해 보고한다(정본 anchor §13.2·§D.4·H4 carry).

## 4. paired 비교 정의

### 4.1 paired Δ% 식

같은 cell·sel·trial·query 조건에서 4 mode를 동시 측정 → 4 mode 사이 paired Δ%:

```
Δ% = 100 · (Q_method − Q_B1) / Q_B1
```

- Δ% < 0 → method가 B1보다 Q-error 낮음
- Δ% > 0 → method가 B1보다 Q-error 높음

본 spec 핵심 4 paired pair:

```
EB-QAS vs B1
EB-QAS vs CaseB
EB-QAS-no-history vs B1
EB-QAS-no-history vs EB-QAS
```

추가 (선택 variant 활성화 시):

```
EB-QAS-no-stop vs EB-QAS
EB-QAS-fixed-kappa vs EB-QAS
EB-QAS-large-kappa vs EB-QAS
EB-QAS-small-kappa vs EB-QAS
CS-EBQAS vs EB-QAS
```

### 4.2 통계량 (각 pair 별)

- `better_count` — Δ% < 0인 paired 측정 수
- `better_ratio` — better_count / total_paired
- `median_delta_percent`
- `mean_delta_percent`
- `Wilcoxon signed-rank p-value`
- `Cliff's δ` (effect size, ordinal)
- `bootstrap 95% CI` (median Δ%, n_resample = 10000)

5/23 평결 §1.1 carry: 단순 better_ratio만으로 “우위” 단언 금지 — Wilcoxon + Cliff's δ + bootstrap CI 3축이 모두 일관될 때만 결론. EB-QAS가 “B1보다 낫다”는 단언은 **측정 결과로만 평가**(정본 anchor 환각 회피 룰 + 본 트랙 README §8).

### 4.3 subset paired 비교

`plan_changed_vs_B1=True`·low-selectivity(sel=0.001)·high-dimensional(WIKI·concat) subset에서 paired Δ% 별도 산출 → H4(plan-sensitive subset latency 개선 가능성) 검증. 전체 평균만 보지 않는다는 5/23 평결 §4 carry.

## 5. 측정 cycle 구조

### 5.1 현 measure 코드 구조 (2026-05-23 22:28 시점)

본 plan 탐색에서 발견한 정정 사항 — 정본 anchor §A.2의 “`measure_paper_exact.py:1312 measure_3way` 구조”는 현재 코드에 단일 함수로 존재 X. 실제 구조:

| 함수 | 라인 | 역할 |
|---|---|---|
| `measure_b1_paper` | 361~ | B1 Exqutor §V-B Bernoulli Adaptive Sampling 측정 |
| `measure_case_a` | 986~ | CaseA 완전 대체 측정 (음성 대조군 — 5/23 평결로 portfolio 악화 확정) |
| `measure_case_b` | 1087~ | CaseB 산술평균 측정 |
| `measure_case_c` | 1195~ | v14 CaseC dual-Bernoulli 통제군 측정 (5/23 21:30 launch) |

3-way matched(B1·CaseA·CaseB 동시)는 함수 단이 아니라 **측정 cycle/runner 단**에서 같은 trial/query 조건으로 위 3 함수를 묶어 호출하는 구조다. v14 CaseC도 같은 패턴으로 추가됐다.

### 5.2 EB-QAS 측정 함수 spec (`measure_ebqas` 신규)

신규 함수 시그니처(spec — 구현 X):

```python
def measure_ebqas(
    cell: CellSpec,
    n_queries: int = 1000,
    trials: int = TRIALS,
    output_dir: Optional[Path] = None,
    *,
    prior_mode: Literal["history", "no_history", "fixed", "large_kappa", "small_kappa"] = "history",
    early_stop: bool = True,
    confidence_sequence: bool = False,
    params: EBQASParams = DEFAULT_EBQAS_PARAMS,
) -> dict:
    """
    EB-QAS measurement.

    Args:
        cell: 측정 cell spec (dataset·sf·selectivity·sub·fig)
        n_queries: cell당 query 수 (기본 1000, online protocol 호환)
        trials: trial 반복 수
        output_dir: JSON 저장 디렉토리
        prior_mode: "history" (full EB-QAS) | "no_history" (Beta(1,1) only — ablation) |
                    "fixed" (κ update X) | "large_kappa" (κ_max=1000) | "small_kappa" (κ_max=10)
        early_stop: posterior Q-risk τ로 조기 종료 (False면 EB-QAS-no-stop variant)
        confidence_sequence: True면 CS-EBQAS variant
        params: EB-QAS hyperparam (batch_size·τ·w·ρ·κ_max·γ·n_min·n_cap)

    Returns:
        dict (기존 measure_case_* 반환 형식과 호환 + EB-QAS 전용 키 추가)
    """
```

반환 dict 핵심 키 (기존 측정 dict 호환 + 신규):

```python
{
    "cell": cell.sub,
    "fig": cell.fig,
    "dataset": cell.dataset,
    "sf": cell.sf,
    "mode": "EB-QAS" | "EB-QAS-no-history" | "EB-QAS-no-stop" | ...,
    "prior_mode": prior_mode,
    "early_stop": early_stop,
    "confidence_sequence": confidence_sequence,
    "params": dataclasses.asdict(params),
    "n_queries": n_queries,
    "trials": trials,
    # accuracy (기존 호환)
    "avg_q_error_trimmed": ...,
    "q_error_median": ...,
    "q_error_p95": ...,
    "q_error_p99": ...,
    "extreme_q_error_count": ...,
    "zero_estimate_count": ...,
    # sampling cost
    "final_size_mean": ...,
    "final_size_median": ...,
    "final_size_std": ...,
    "actual_distance_computations_mean": ...,
    "early_stop_rate": ...,        # EB-QAS·EB-QAS-no-history만
    # latency (선택 — latency 평면 측정 시)
    "exec_ms_trimmed": ...,
    "exec_ms_median": ...,
    # EB-QAS 전용
    "posterior_kappa_trajectory": [...],   # query별 κ_g 변화
    "posterior_mu_trajectory": [...],      # query별 μ_g 변화
    "mismatch_count_total": ...,           # mismatch reset 발동 횟수
    "trial_results": [...],
    "paper_hyperparam": PAPER_HYPERPARAM,
    "kst": mc.kst(),
}
```

### 5.3 측정 runner 4-way matched 호출

본 실험 A의 측정 cycle은 trial loop에서 4 mode 함수를 같은 trial/query 조건으로 호출하는 구조다. 의사 코드(spec — 구현은 활성화 후 별도):

```python
for trial_idx in range(trials):
    seed = base_seed + trial_idx
    query_set = generate_queries(cell, seed=seed, n_queries=n_queries)  # 동일 query set

    result_b1 = measure_b1_paper(cell, query_set=query_set, seed=seed, ...)
    result_case_b = measure_case_b(cell, method_name=method, query_set=query_set, seed=seed, ...)
    result_ebqas = measure_ebqas(cell, query_set=query_set, seed=seed, prior_mode="history", ...)
    result_ebqas_no_history = measure_ebqas(cell, query_set=query_set, seed=seed, prior_mode="no_history", ...)

    # paired 비교는 같은 query_idx·trial_idx에서 4 mode 동시 추출 → analysis 단에서 결합
```

**핵심 제약 (5/23 평결 §A.4 carry)**:
- 동일 `seed`·동일 `query_set`·동일 `trial_idx`에서 4 mode 측정 — paired 비교 통제.
- query 순서를 4 mode 사이에서 일관 — sequential history 사용(실험 B online protocol)도 동일 순서 보장.
- output JSON은 mode별 1 파일 (`<cell.sub>_B1.json`·`<cell.sub>_CaseB.json`·`<cell.sub>_EBQAS.json`·`<cell.sub>_EBQAS-no-history.json`) → analysis 단에서 paired join.

### 5.4 leakage 방지 (정본 anchor §B.3·§18.1·§18.2 carry)

- 현재 query의 true cardinality는 **query 실행 후만** state update에 사용. planning 시점에는 prior + current sample만 사용.
- prior에 현재 query의 sample 결과를 likelihood로 사용하면서 동시에 prior update에도 넣지 않는다 — double counting 금지.
- 전체 query set의 평균 selectivity를 사전에 prior로 사용하지 않는다 — test query 결과의 train prior leakage 금지.
- 본 실험 A는 단발 query shuffle 측정 — online history는 실험 B에서 검증. 본 실험 A에서 EB-QAS는 cold-start 또는 cell 단위 누적 prior로 동작.

## 6. 환각 회피·5/23 평결 호환성 재확인

본 spec은 EB-QAS 정본 anchor 환각 회피 룰 + 5/23 감사 평결 4축과 일관된다.

- **CaseB 89.1% 우위 인과 귀속 금지**: 본 실험 A의 paired 비교는 EB-QAS vs B1·EB-QAS vs CaseB 모두 통계량 3축(better_ratio + Wilcoxon + Cliff's δ + bootstrap CI) 일관 시에만 결론. CaseB는 본 spec에서 “산술평균의 앙상블(분산 감소) 효과”로 frame.
- **분포 사전 지식 가정 X**: EB-QAS는 query group key(table·column·distance metric·threshold bucket·query template·scalar predicate signature)만 사용 — vector table 전체 CDF·clustering·density map·histogram 미사용.
- **latency 평가 한정**: 전체 평균 latency만 보지 않음. plan_changed·low-selectivity·high-dimensional subset 분할(§4.3) + injection_fired=True only subset(메인 트랙 latency PoC 호환).
- **method library 미의존**: EB-QAS posterior는 prior mean과 sample proportion 가중평균 한 줄 — method 정체(P1~P10 paradigm 어디든)와 무관. CaseB는 method estimate를 평균에 사용하지만, 본 실험 A에서 CaseB는 baseline carry로만 측정(method library 무결성은 메인 트랙 §4.7과 동일 honest limitation 적용).

본 spec은 “EB-QAS가 B1보다 낫다” 단언 X — 측정 결과로만 평가(가설 H1~H5, 정본 anchor §21).

## 7. 측정 일정·자원 견적 (활성화 후 별도)

### 7.1 일정 (default)

- **본 spec 작성 시점 (2026-05-23 22:28 KST)**: spec 문서만, 측정 X.
- **활성화 결정 시점**: 사용자 명시 결정 — default 6/11 최종 보고서 마감 이후.
- **활성화 후**: `measure_ebqas` 구현 → 단일 cell smoke 1건 → 우선 24 cell 측정 → 분석 → 발표·보고서 반영(별도 트랙 산출물로 carry, 메인 트랙 재프레이밍에 끼워 넣지 않음).

### 7.2 자원 견적

- 1 cell × 4 mode × 1000 query × TRIALS 기준, 메인 트랙 v14 측정과 유사 — 1 cell ~9-15분 sequential(latency 측정 포함 시).
- 우선 24 cell × 4 mode = 4-6시간 sequential.
- 전체 72 cell × 4 mode = 12-18시간 sequential (자원 여유 시 일부 cell skip).
- 자원 watchdog v4 (메인 트랙과 동일) 적용 — free ≥ 256GB·our_rss ≤ 512GB·5초 주기.

### 7.3 산출물 (활성화 후)

- 측정 JSON: `_internal/cache/rq3/<EBQAS_타임코드>/<cell.sub>_<mode>.json`
- 집계 parquet: `_internal/cache/rq3/aggregated_EBQAS_<타임코드>.parquet`
- 분석 보고서: `_internal/cache/rq3/EBQAS_summary_<타임코드>.md` (v13_summary·v14_summary 패턴 호환)
- figure: `experiments/figures/EBQAS_<타임코드>/` (활성화·팀 공유 결정 후)

### 7.4 본 spec 적용 boundary

- 본 spec은 **측정 spec 문서**다. 측정 코드 patch·launch·분석 보고서·figure는 활성화 후 별도 세션이 수행.
- 본 spec 자체의 patch(추가 mode·metric·dataset)는 활성화 전 사용자 명시 결정 시 진행. 본 세션에서는 정본 anchor §15·§A를 정제·정정한 상태로 carry.

## 8. 본 spec과 정본 anchor 사이 정정 사항 (carry)

본 spec은 정본 anchor §A.2의 “`measure_paper_exact.py:1312 measure_3way` 구조” 표현을 §5.1에서 정정했다. 정본 anchor 본문 inline 수정은 사용자 명시 지시 시 별도(권고: 활성화 시점에 §A.2의 “`measure_3way`” → “`measure_b1_paper`·`measure_case_a/b/c` 4분리”로 정정). 그 외 정본 anchor 본문은 본 spec과 일관되어 인용 변경 사항 없음.

## 9. 다음 단계

본 실험 A spec은 활성화 결정 후 다음 순서로 사용된다.

1. 활성화 결정(사용자 명시) → `measure_ebqas` 구현 spec 확정.
2. `measure_ebqas` 구현 (별도 commit·codex review·smoke 1 cell).
3. 우선 24 cell sequential 측정.
4. paired 비교 분석 + 본 spec §3·§4 metric 산출.
5. 결과 보고서 작성(본 트랙 산출물, 메인 트랙 발표·보고서에 직접 인용 X).
6. 실험 B (online protocol) 진입 — 별도 spec(`EBQAS_실험BCDE_outline_20260523_222815.md` §1) 활용.

본 spec은 활성화 시점까지 carry — 변경 사항 발생 시 새 타임코드 파일로 갱신(덮어쓰기 X).
