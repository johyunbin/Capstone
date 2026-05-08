# Adaptive Sampling 의미론 audit — 사용자 직관 vs paper 동작

**작성**: 2026-05-08, 백그라운드 에이전트 V6 (V4 audit 보완)
**근거**: arXiv:2512.09695v2 HTML/abstract WebFetch + WebSearch 인용 + 본 구현 코드 line-by-line
**핵심 질문**: "Adaptive Sampling 은 일정 값에 수렴할 때까지 적응형 샘플링 하는 방식 아니냐?"

---

## 1. WebFetch 결과 — paper 의 정확한 동작 설명

WebFetch (`/html/2512.09695v2`) + WebSearch 가 일관되게 다음을 인용:

> "Sample size updates are triggered every 50 queries."
> "...dynamically adjusts the sample size based on estimation accuracy observed *after query execution*."
> "When estimation remains accurate with low Q-error, the sample size is reduced... higher Q-error triggers an increase."
> "Exqutor adopts a sampling-based cardinality estimation approach... approximates the number of qualifying tuples by *evaluating similarity over a small subset* of the data."

→ paper 의 Adaptive Sampling 은 **(a) 매 incoming query 마다 1회 random sample 추출 → estimate 산출 → 결과 사용** + **(b) 50개의 분리된 query 가 누적되면 그 때 다음 batch 의 sample_size 를 momentum 으로 갱신**. 단일 query 안에서 sample 을 누적하며 convergence 까지 반복 X. WebFetch 가 명시한 batch flow:

> Each batch of 50 queries: Draw sample size N_t → estimate → query plan → measure actual cardinality → compute Q-error → update N_{t+1} for next batch

## 2. 식 1~6 의미 재해석

- **식 1 (N=385)**: **initial value**. "we initially compute the number of samples N... yields a fixed sample size of N=385" 후 "subsequently modified by Equations 3-5". 단일 query 의 fixed budget 이 아닌, momentum 이 아직 0 인 첫 batch 의 시작점.
- **식 5 sample_size_{t+1}**: subscript `t` 는 **batch index** (= 50-query batch 의 index), 단일 query iteration 이 아님. "_{t+1}" 은 다음 50-query batch 가 사용할 sample_size.
- **식 3 의 sampling_ratio**: across-batch 갱신에서 현 N 의 비율 (overhead penalty).
- **식 6 (γ decay)**: batch 마다 η 가 0.99 배 감소 → 후반 batch 는 작은 step.
- **수렴 의미**: per-batch (50 queries 평균 Q-error) 가 β=1.5 근처에 도달하면 V_t → 0 으로 수렴, sample_size 가 안정화. **단일 query 안의 수렴이 아닌 batch 시퀀스의 수렴**. Figure 6 도 "sample sizes stabilize after several update *cycles*" — cycle = batch.

## 3. 본 연구 구현의 실제 동작 vs paper 의도

`run_adaptive_sampling.py` (line 309-342) + `measure_multi_adaptive_sampling.py` (line 150-176):

| paper 동작 | 본 구현 | 일치 |
|---|---|---|
| 매 query 1회 random sample | line 320 `adaptive_bernoulli_estimate(...)` 1회 호출, line 219-225 single `rng.choice(n, size=s, replace=False)` | ✅ |
| 50 query 마다 sample_size 갱신 | `AdaptiveState.step()` line 181 `if self.n_total % self.update_period == 0` (update_period=50) | ✅ |
| 갱신 식 3~5 (momentum + δ + V_t) | line 184-194 정확 매핑 (V4 audit §2 line-by-line 검증 완료) | ✅ |
| η decay 식 6 | line 195-196 `self.learning_rate = self.gamma * self.learning_rate` | ✅ |
| 첫 query: N=385 | line 303 `sample_size = SAMPLE_SIZE` | ✅ |
| Per-table separate state | multi line 275-276 `state1 / state2` 독립 instance | ✅ |
| 단일 query 안 sample 누적/iteration | **없음** (paper 도 없음 — 1-shot) | ✅ |

본 구현 = paper 동작 정확 일치. 사용자 직관 (per-query convergence iteration) 은 paper 의 알고리즘이 **아니다**.

### 측정 셋업 nuance (V4 audit 미포착)

본 연구는 paired comparison framework — `(seed, sel)` 별 새 `AdaptiveState` instance 생성 (line 299-302). paper 는 production stream (sel 무관 시간순) 이지만 본 연구는 selectivity gradient 격자에서 paired Δ% 를 위한 분리. 이는 paper 의 "operational deployment" trajectory 를 sel × seed 별로 독립 reset 하는 것. **연구 narrative 에서 명시 권장**: "본 연구는 paper 의 across-query update 알고리즘을 (cell × seed × selectivity) 격자에 적용 — 각 (seed, sel) sub-trajectory 가 paper 의 operational batch 시퀀스와 동일 동작."

## 4. 결론 — (a) 일치

**본 연구 구현이 paper 와 일치**. 사용자 직관 ("일정 값에 수렴할 때까지 적응형 샘플링") 은 paper 의 알고리즘이 아닌 다른 패러다임 (sequential sampling with within-query stopping rule, e.g. Hoeffding-style adaptive stopping) 과 혼동된 것으로 추정. paper 의 "adaptive" 는 **across-query momentum-based sample size adjustment** 이지 within-query stopping 이 아니다.

**본 연구 narrative valid**:
- W2 자문 메일 / 5/27 발표 deck 의 "Exqutor Adaptive Sampling 본 논문 비교" 표현 그대로 유지 가능
- 4강 vs Adaptive paired Δ% 측정 (10 cell × 5 sel) 결과의 학술적 정합성 보증
- 재구현 / 재측정 불필요

**작은 narrative 보강 권장** (필수 X): paper 의 adaptive 가 "across-query batch update" 임을 발표 1슬라이드에 1줄 명시 — 청중 (특히 산업계 panel) 이 사용자와 같은 직관 ("convergence iteration") 으로 오해 시 질문 대응 자료. 5/27 deck Q&A backup slide 후보.

**Audit 정합**: V4 ("hyperparam + 식 line-by-line valid reproduction") 결론 유지. V6 는 V4 가 다루지 않은 의미론 차원 (per-query vs across-query) 을 추가 검증 — 동일 결론.
