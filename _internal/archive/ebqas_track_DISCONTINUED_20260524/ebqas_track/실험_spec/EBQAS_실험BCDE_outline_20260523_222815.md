# EB-QAS 실험 B~E outline + hyperparam grid (한국어 학술 정제)

> 작성: 2026-05-23 22:28 KST. 출발 문서 = EB-QAS 정본 anchor `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` §16·§B·§C·§D·§E. 본 outline은 실험 A([실험 A spec](EBQAS_실험A_4way_matched_spec_20260523_222815.md)) 뒤에 이어 진행될 4 후속 실험과 hyperparam 권장 grid를 한국어 학술 산문으로 정제한다. **본 outline은 활성화 결정 후 별도 세션이 각 실험을 정식 spec으로 확장하기 위한 carry 문서다.**

## 0. TL;DR

| 실험 | 핵심 검증 | 핵심 산출물 |
|---|---|---|
| **B (online protocol)** | history-aware EB-QAS 본의: 유사 query 반복 시 sample 수 감소·Q-error 유지 또는 감소 | query index vs sample size·Q-error·κ_g·early stop rate 4 plot + cold/warm 분리 |
| **C (prior mismatch stress)** | 잘못된 group key·κ 과대·prior drift 시 EB-QAS 안전장치(κ cap·decay·mismatch reset)의 필요성 입증 | safe vs unsafe vs B1 paired 비교 + Q-error 폭발 case study |
| **D (latency 평가)** | Q-error 개선이 실제 latency 개선으로 이어지는지 — 전체 평균 X, plan-sensitive subset 한정 | 6 subset 분할 latency 비교 + injection_fired=True only subset paired |
| **E (ablation)** | EB-QAS 핵심 요소(prior history·early stopping·mismatch reset·κ cap) 각각의 기여 분리 | 6 variant paired 비교 + Cliff's δ + bootstrap CI |

본 outline은 정본 anchor §15·§B·§C·§D·§E를 한국어 학술 산문으로 정제하되, 실험 A([별도 spec](EBQAS_실험A_4way_matched_spec_20260523_222815.md))이 보장하는 4-way matched 기본 구조 위에서 추가되는 변형·통제·분할만 명시한다. 5/23 감사 평결 호환성(분포 사전 지식 X·CaseB식 평균 X·latency objective X·method library X)은 모든 실험에 일관 적용.

---

## 1. 실험 B — 유사 query 반복 실행 online protocol

### 1.1 목적

EB-QAS는 정의상 history-aware다 — 정본 anchor §1 “이전 유사 query/predicate의 실행 결과”를 prior로 누적. 실험 A의 4-way matched(단발 query shuffle)는 cold-start·cell-내 누적까지만 검증하므로, 실험 B는 “유사 query가 sequential로 반복되는 online workload”에서 EB-QAS의 본의를 검증한다. Exqutor도 50-queries period로 sample size update를 trigger하므로, EB-QAS와 공정 비교를 위해 같은 query stream에서 양쪽 모두 history를 사용한다.

### 1.2 query group 정의

```text
g = (
  dataset,
  vector_column,
  distance_metric,
  threshold_bucket,
  query_template,
  scalar_predicate_signature
)
```

threshold bucket·query template·scalar predicate signature 셋이 핵심 — 분포 사전 지식 없이 query metadata만으로 prior accumulation 가능. group key가 너무 세밀(query vector hash 포함)하면 모든 group이 cold-start, 너무 넓(dataset 전체)으면 서로 다른 selectivity가 섞여 prior 왜곡 → 실험 B는 §1.2의 6-tuple을 기본으로 사용.

### 1.3 query stream 구성

- 각 group당 **1000 queries sequential** 실행.
- query 순서: 4 mode(B1·EB-QAS·EB-QAS-no-history·CaseB) 동일 — paired 통제.
- 예시 group 구성:
  - Group 1: DEEP × sel=0.001 × query_template Q1
  - Group 2: DEEP × sel=0.01 × Q1
  - Group 3: SIFT × sel=0.01 × Q1
  - Group 4: WIKI × sel=0.01 × Q1

본 outline은 4 group 최소 — 활성화 시 자원 여유 기준 8-16 group으로 확장.

### 1.4 leakage 방지 (정본 anchor §B.3 carry)

**금지**:
- 현재 query t의 true cardinality를 prior에 먼저 반영
- 전체 query set 평균 selectivity를 미리 계산해 prior로 사용
- test query 결과를 train prior에 사용

**허용**:
- query t 실행 전: query 1 ~ t−1 결과만 prior 반영
- query t 실행 중: current sample만 likelihood
- query t 실행 후: true cardinality를 query t+1 이후 prior에 반영

### 1.5 cold/warm 분리

각 group의 1000 queries를 다음 5 phase로 분할 분석:

- queries 1~50: cold-start
- queries 51~100: warm-up
- queries 101~200: early evaluation
- queries 201~500: mid evaluation
- queries 501~1000: stable evaluation

또는 단순히 1~100을 warm-up·101~1000을 evaluation으로 분리해도 무방. history가 쌓이면서 EB-QAS의 sample size와 Q-error가 어떻게 변하는지 plot으로 보고.

### 1.6 핵심 plot (6 figure)

본 outline의 plot은 활성화 후 별도 figure build 시 작성.

```text
Fig B.1  query index vs final sample size (B1 / EB-QAS / EB-QAS-no-history)
Fig B.2  query index vs Q-error moving average (window=50)
Fig B.3  query index vs posterior κ_g (EB-QAS only)
Fig B.4  query index vs early stop rate (window=50, EB-QAS·EB-QAS-no-history)
Fig B.5  selectivity별 Q-error boxplot (sel ∈ {0.001, 0.01, 0.10})
Fig B.6  latency vs method × subset (plan_changed·low-selectivity·high-dimensional)
```

### 1.7 환각 회피·평결 호환성

본 실험은 “EB-QAS가 history accumulation으로 sample 수를 줄인다”는 H1·H3 검증. 측정 전 “sample 수 감소가 보장된다” 단언 금지. 결과 해석 시 prior mismatch case(group key 부적절·workload drift)는 §2(실험 C)에서 별도 보강.

---

## 2. 실험 C — prior mismatch stress test

### 2.1 목적

EB-QAS의 가장 큰 위험은 잘못된 prior다(정본 anchor §14.2·H5). 실험 C는 prior mismatch를 의도적으로 유발해 EB-QAS-safe(κ cap·decay·mismatch reset)와 EB-QAS-unsafe(안전장치 무) 사이의 격차를 입증한다. 동시에 B1은 prior를 쓰지 않으므로 mismatch에 영향 받지 않음을 baseline으로 확인.

### 2.2 mismatch 유발 설계

**Case C.1 — group key 부적절**:
- 정상 grouping: threshold_bucket별 group 분리
- 잘못된 grouping (의도 유발): sel=0.001·sel=0.01·sel=0.10을 같은 group으로 묶음
- 또는: DEEP·SIFT·WIKI를 같은 group으로 묶음

**Case C.2 — workload drift**:
- query 1~500: sel=0.001 dominant → prior μ ≈ 0.001로 누적
- query 501~1000: sel=0.10 dominant → prior가 낡은 정보, mismatch reset 필요

### 2.3 비교 variant (3종)

```text
EB-QAS-safe:
  κ_max + decay ρ + mismatch reset(99% credible interval 기반) 모두 활성

EB-QAS-unsafe:
  κ 계속 누적·decay 무·mismatch reset 무
  → prior가 무한히 강해질 수 있음

B1:
  Exqutor §V-B adaptive sampling 그대로
  → prior 미사용·mismatch 무관
```

### 2.4 핵심 metric

- Case C.1: 잘못된 grouping 하에서 EB-QAS-unsafe의 p95·p99 Q-error vs EB-QAS-safe vs B1
- Case C.2: drift 발생 직후(query 501~600) Q-error 폭발 case study + κ_g·μ_g·mismatch_count trajectory

### 2.5 예상 결과 (정본 anchor §C.4 carry — 측정 전 가설)

- EB-QAS-unsafe: prior 틀린 case에서 Q-error 폭발 가능
- EB-QAS-safe: mismatch 감지 후 κ 감소 → B1 수준 동작으로 복귀
- B1: prior 미사용 → mismatch 무관, 단 stable workload에서는 EB-QAS-safe보다 sample 수 많이 사용

### 2.6 환각 회피·평결 호환성

본 실험은 “안전장치가 필요한 이유”를 통계적으로 보이는 음성·방법론적 결과 후보. EB-QAS-unsafe 악화는 “EB-QAS가 나쁘다”가 아니라 “안전장치 없는 EB-QAS는 위험하다”로 frame. 발표·보고서(활성화 후)에 함께 보고하는 H5 정직성.

---

## 3. 실험 D — latency 평가

### 3.1 목적

Q-error 개선이 실제 latency 개선으로 이어지는지 확인. 단 5/23 감사 평결 §4(56 cell B1→CaseB paired Δ% +0.13%·r=−0.007)와 정본 anchor §13.2(plan-sensitive subset 한정)에 따라 **전체 평균만 보지 않는다**. injection_fired=True 미만 case는 invalid 처리.

### 3.2 비교 대상 (5 mode)

```text
baseline:
  no injection / DB default cardinality estimate

B1:
  Exqutor adaptive sampling estimate injection

CaseB:
  arithmetic mean estimate injection (5/23 평결 carry)

EB-QAS:
  proposed empirical-Bayes estimate injection

oracle:
  true cardinality injection (upper bound)
```

oracle은 메인 트랙 latency PoC(§6.4)에서 4.43× ≈ 4.54×로 측정된 “구조적 plan 회복 상한”. EB-QAS가 B1 대비 oracle에 더 가까워지면 의미.

### 3.3 latency metric (9개 — 실험 A §3.3 carry)

`exec_ms_trimmed`·`exec_ms_median`·`speedup_vs_baseline`·`speedup_vs_B1`·`speedup_vs_CaseB`·`plan_changed_vs_baseline`·`plan_changed_vs_B1`·`injection_fired`·`timeout_count`

Exqutor 논문(arXiv:2512.09695v2) §VI carry: warm-up execution 제외, 10회 실행 trimmed mean.

### 3.4 subset 분할 (6분할 — 5/23 평결 §4 carry)

전체 평균만 보면 안 됨. 다음 6 subset에서 별도 분석:

```text
1. all queries (전체 평균 — reference)
2. injection_fired=True only (MISS 제거)
3. plan_changed_vs_B1=True
4. low-selectivity sel=0.001
5. high-dimensional WIKI / concat
6. high-Q-error-reduction subset (top quartile by EB-QAS Q-error 감소)
```

### 3.5 예상 결과 (정본 anchor §D.4 carry — 측정 전 가설)

5/23 평결 §4 carry: B1이 이미 oracle 수준 plan 회복 → 구조적 headroom 부재. 따라서 EB-QAS도 전체 평균 latency에서 큰 차이 없을 가능성 큼. 그러나 다음 중 하나라도 보이면 의미:

```text
- Q-error는 B1과 비슷한데 sample size 감소 → sampling overhead 감소
- plan_changed subset에서 latency 개선
- low-selectivity subset에서 latency 개선
- high-dimensional subset에서 sample 감소가 distance computation 감소로 이어져 sampling overhead 감소
```

본 실험은 latency 개선을 “보장” 주장 X — 정직한 음성·부분 양성 결과 가능성 carry.

### 3.6 환각 회피·평결 호환성

5/23 평결 §4와 일관: latency를 EB-QAS의 objective로 삼지 않음. 평가 지표·subset 한정 보고. injection_fired=True 미만 case 제외. plan_changed_vs_baseline·plan_changed_vs_B1 양쪽 보고 — “B1이 이미 oracle 수준 plan 회복” base 위에서 추가 개선 가능 subset만 한정.

---

## 4. 실험 E — ablation study

### 4.1 목적

EB-QAS의 핵심 요소 각각의 기여를 분리. 정본 anchor §E carry.

### 4.2 variant (6종)

```text
B1:
  Exqutor §V-B Bernoulli Adaptive Sampling (baseline)

EB-QAS-full:
  prior history + posterior mean + early stopping + κ cap + decay + mismatch reset (모두 활성)

EB-QAS-no-history:
  Beta(1,1) only, history prior 미누적
  → Bayesian formula 자체 효과(weak prior shrinkage)와 history-aware prior 효과 분리

EB-QAS-no-stop:
  posterior mean 사용하되 early stopping 없음, n_cap까지 항상 sampling
  → posterior mean의 Q-error 효과와 sample 수 감소 효과 분리

EB-QAS-no-reset:
  mismatch reset 없음 (κ cap·decay는 활성)
  → mismatch reset의 안정성 기여 분리

EB-QAS-large-kappa:
  κ_max = 1000 (default 100보다 크게)
  → over-shrinkage 위험 정량화

EB-QAS-small-kappa:
  κ_max = 10 (default 100보다 작게)
  → prior 효과가 너무 약하면 B1과 동등 수렴 검증
```

본 outline은 6 variant 모두 정의 — 활성화 시 자원 여유 기준 priority(full·no-history·no-stop·no-reset 4종 우선)로 선별.

### 4.3 핵심 paired 비교

```text
EB-QAS-full vs EB-QAS-no-history    → history prior 기여
EB-QAS-full vs EB-QAS-no-stop       → early stopping 기여
EB-QAS-full vs EB-QAS-no-reset      → mismatch reset 기여 (실험 C와 cross-check)
EB-QAS-full vs EB-QAS-large-kappa   → κ 상한의 over-shrinkage 위험
EB-QAS-full vs EB-QAS-small-kappa   → prior 효과 하한
```

### 4.4 해석 가이드

| 관찰 | 해석 |
|---|---|
| EB-QAS-full > EB-QAS-no-history | history prior가 Q-error 또는 sample 수 측면에서 기여 |
| EB-QAS-full ≈ EB-QAS-no-history | history prior 효과 미미 — Bayesian formula 자체 효과만 있음 |
| EB-QAS-full > EB-QAS-no-stop | early stopping이 sample 수 감소 효과 |
| EB-QAS-full > EB-QAS-no-reset | mismatch reset이 안정성 효과 (실험 C와 cross-check) |
| large-kappa 악화 | over-shrinkage 위험 정량화 |
| small-kappa ≈ B1 | prior 효과가 약하면 B1으로 수렴 |

### 4.5 환각 회피·평결 호환성

본 실험은 “EB-QAS의 어느 요소가 효과를 만드는가”를 분리하는 정직한 ablation. 결과가 “전부 무효”라도 carry — 5/23 평결의 정직성 원칙 적용. 특히 `EB-QAS-full ≈ EB-QAS-no-history`로 나오면 “history accumulation 효과 없음”으로 frame하고 실험 B의 결과와 cross-check.

---

## 5. hyperparam 권장 grid (정본 anchor §16 정제)

활성화 후 measure_ebqas params로 grid search 가능한 영역.

### 5.1 batch_size b (sampling 단위)

- 권장: 16 · 32 · 64
- default: 32
- 너무 작으면 posterior update 빈도 ↑ → overhead 증가. 너무 크면 early stop 해상도 ↓.

### 5.2 target posterior Q-risk τ (early stopping 임계)

- 권장: 1.1 · 1.2 · 1.3 · 1.5
- default: 1.3
- 작으면 stricter stop(sample 수 ↑·Q-error ↓). 크면 looser stop(sample 수 ↓·Q-error ↑ 위험).

### 5.3 prior update weight w (after-execution update)

- 권장: 1 · 5 · 10 · 20
- default: 10
- 크면 새 query feedback 반영 빠름(drift 적응). 작으면 prior 안정.

### 5.4 decay ρ (oldness 감쇠)

- 권장: 0.90 · 0.95 · 0.98
- default: 0.95
- 작으면 prior 빠르게 흐려짐(drift 강함). 크면 prior 누적 강함(mismatch 위험 ↑).

### 5.5 κ_max (prior strength 상한)

- 권장: 20 · 50 · 100 · 200
- default: 100
- 정본 anchor §9 — κ 무한 키우면 prior에 현재 sample을 무시. 100 default 권고.
- 실험 E의 large-kappa(1000)·small-kappa(10) variant로 hyperparam 효과 정량화.

### 5.6 mismatch reset 감쇠 γ

- 권장: 0.25 · 0.5
- default: 0.5
- mismatch 감지 시 κ를 γ배로 축소. 작을수록 reset 강함.

### 5.7 n_min·n_cap

- n_min (최소 sample 수, early stop 발동 전): 32 · 64. default 64.
- n_cap (최대 sample 수, EB-QAS도 Exqutor outer cap 유지): B1의 현재 adaptive sample size, 또는 385·512·1024. default B1 adaptive cap 동기화.

### 5.8 default 조합 (초기 실험)

```text
batch_size = 32
τ = 1.3
w = 10
ρ = 0.95
κ_max = 100
γ = 0.5
n_min = 64
n_cap = B1 adaptive cap (또는 385)
```

활성화 후 5.1~5.7 grid 중 1-2축씩 sweep — 한 번에 전체 grid는 자원 낭비. 우선 default 조합 단일 측정으로 기준선 확립.

---

## 6. 본 outline의 활성화 시 정식 spec 확장 절차

본 outline은 실험 B·C·D·E의 핵심 변형·통제·분할만 정리한 carry 문서다. 활성화 결정 시 다음 4 정식 spec으로 확장:

1. `EBQAS_실험B_online_protocol_spec_<타임코드>.md` — query group 정의·stream·leakage·cold/warm·6 plot 정식 spec.
2. `EBQAS_실험C_prior_mismatch_stress_spec_<타임코드>.md` — mismatch 유발 case 2종·3 variant·예상 결과 분석 spec.
3. `EBQAS_실험D_latency_spec_<타임코드>.md` — 5 mode·9 metric·6 subset 분할 spec + 메인 트랙 latency PoC와 cross-ref.
4. `EBQAS_실험E_ablation_spec_<타임코드>.md` — 6 variant·5 paired·해석 가이드 spec.

확장 시 본 outline은 base 문서로 cross-ref 유지(덮어쓰기 X).

## 7. 환각 회피·트랙 위상 (carry)

본 outline은 다음을 일관 적용:

- “EB-QAS가 B1보다 낫다” 단언 금지 — 측정 전이며 모든 결과는 paired 비교 + 통계 3축 일관 시에만 결론.
- 5/23 평결 4축(분포 사전 지식 X·CaseB식 평균 X·latency objective X·method library X) 일관 호환.
- 메인 트랙(v14·발표·보고서·포스터) 발표·재프레이밍에 본 실험 B~E 결과를 끼워 넣지 않음.
- 본 EB-QAS 트랙 활성화 default = 6/11 최종 보고서 마감 이후 또는 향후 연구 트랙 후보.
- 타임코드 네이밍: `v13/v14/ver/wave/phase` 단어를 파일명 분기자로 쓰지 않음.
