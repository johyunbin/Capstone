# Adaptive Sampling 측정 코드 fidelity audit — Exqutor 본 논문 §V-B/§VI 대비

**작성**: 2026-05-08, 백그라운드 에이전트 V4 (검증 only — 코드 수정 X)
**Source 검증**: WebFetch 로 arXiv:2512.09695v2 HTML 직접 정독 + Agent E 분석 doc 교차
**대상 코드**:
- `experiments/code/rq3/run_adaptive_sampling.py` (단일, 544 lines)
- `_internal/scripts/measure_multi_adaptive_sampling.py` (multi, 649 lines)

---

## 1. Section VI hyperparameter exact match

| Hyperparameter | 본 논문 §VI | run_adaptive_sampling.py | measure_multi | 검증 |
|----------------|------------|--------------------------|---------------|------|
| m (momentum) | 0.9 | 0.9 (line 158, 277, 445) | 0.9 (line 141, 532) | ✅ |
| η₀ (initial LR) | 0.1 | 0.1 (line 157, 278, 446) | 0.1 (line 142, 533) | ✅ |
| α (Q-error 가중치) | 50 | 50.0 (line 159, 279, 447) | 50.0 (line 143, 534) | ✅ |
| β (target Q-error) | 1.5 | 1.5 (line 160, 280, 448) | 1.5 (line 144, 535) | ✅ |
| γ (LR decay) | 0.99 | 0.99 (line 161, 281, 449) | 0.99 (line 145, 536) | ✅ |
| update period | 50 queries | 50 (line 162, 282, 450) | 50 (line 146, 537) | ✅ |
| 초기 N | 385 (식 1) | 385 (line 155 = `SAMPLE_SIZE` from `_measure_common`) | 385 (line 137, 82) | ✅ |
| min/max clip | 명시 X | 50 / 5000 (line 163-164) | 50 / 5000 (line 146-147) | ⚠️ paper 명시 X — 운영상 추가 (발산 방지). 본 논문 reproduction 범위 내 — 정상 운영 trajectory (DEEP ~358, SIFT ~415) 가 [50, 5000] 안. |

전 항목 paper 와 정확 일치. min/max clip 만 본 논문 명시 X — 안전 가드로만 작동, 본 논문 보고된 수렴 범위 내에서는 trigger X.

---

## 2. 식 1~6 implementation 검증

**식 1 — N = ⌈z²·P̂(1-P̂)/e²⌉ = 385**
- `_measure_common.SAMPLE_SIZE = 385` 상수 (단일/multi 공통).  
- 단일 line 155 / 303, multi line 82 / 137 / 278-279 모두 첫 query 의 sample_size 로 N=385 사용. ✅

**식 2 — Q-error = max(est/true, true/est)**
- 단일 line 321-324, multi line 308-311. 양쪽 모두 정확히 max(est/tc, tc/est), est=0 또는 true=0 시 None 반환. ✅

**식 3 — δ = α·(Q-error - β) - (100-α)·sampling_ratio**
- 단일 line 184-186, multi line 162-164. 둘 다 `delta = alpha * (mean_qe - beta) - (100.0 - alpha) * sampling_ratio` 정확. sampling_ratio = `sample_size / max(max_size, 1)` (line 183 / 161). ✅
- 주의: 본 논문은 `sampling_ratio` 의 분모 정의를 명시하지 않음. 본 구현은 `max_size = 5000` 으로 정규화 — α=50 이므로 δ 의 sampling_ratio 항 max contribution 은 -50·1.0 = -50 (sample_size = max_size 일 때), Q-error 항 contribution 은 50·(qe - 1.5). β=1.5 around equilibrium 에서 두 항 balance. **본 논문 의도와 일치할 가능성 높음** (paper 의 "sampling_ratio" 변수가 분명한 정의 없이 나오므로 확정 불가, 그러나 reasonable interpretation).

**식 4 — V_t = m·V_{t-1} + η_t·δ**
- 단일 line 187-189, multi line 165-167. 정확. ✅

**식 5 — sample_size_{t+1} = sample_size_t + V_t**
- 단일 line 190-194, multi line 168-172. clip [min_size, max_size] 추가 외 paper 와 동일. ✅

**식 6 — η_{t+1} = γ·η_t**
- 단일 line 195-196, multi line 173-174. 정확. ✅

**update period = 50 queries trigger**
- 단일 line 181, multi line 159. `if self.n_total % self.update_period == 0 and self.qerror_window` — 정확히 매 50 query 마다 한 번 갱신. ✅

식 1~6 전부 line-by-line 본 논문 일치.

---

## 3. AdaptiveState transition logic

매 query 단계 (`step` 메서드, 단일 line 168-199 / multi line 150-176):

1. `n_total += 1` — 누적 query count.
2. q_error 가 finite 이면 window 에 push (None / non-finite 는 제외 — 식 3 mean 계산 안정성 보장).
3. `n_total % 50 == 0` 이면:
   - mean_qe = window 평균
   - sampling_ratio = sample_size / max_size
   - 식 3 → δ
   - 식 4 → V_t (이전 V_{t-1} 보존, m=0.9 누적)
   - 식 5 → sample_size + V_t, [50, 5000] clip
   - 식 6 → η *= γ (decay)
   - window clear (다음 50 queries 평가 준비)
4. 다음 query 의 `int(round(sample_size))` 반환.

velocity / learning_rate state 가 step 사이에 정확히 carry-over (dataclass instance attribute) — momentum 의 핵심인 V_{t-1} 보존 verified. ✅

---

## 4. Multi-table per-table separate state

본 논문 §V-B 명시: "the optimizer maintains separate sample size states for each table".

`measure_multi_adaptive_sampling.py`:
- line 275-276: `state1 = _make_state(...)` / `state2 = _make_state(...)` — cell × seed 마다 두 인스턴스 독립 생성.
- line 278-279: `s1_next = SAMPLE_SIZE` / `s2_next = SAMPLE_SIZE` — 각 table 의 첫 query sample_size 독립 N=385.
- line 296-301: per-table 독립 random sample (rng 한 개 공유 — sequential consumption 으로 두 sample 이 비-overlapping).
- line 346-347: `state1.step(qe_for_state)` / `state2.step(qe_for_state)` — 매 query 두 state 동시 갱신.

⚠️ 주의: `qe_for_state = qerr_joint` (line 317) — 두 table 에 동일 joint q_error feedback. 본 논문 multi-table feedback 정책 명시 X 이나, 코드 주석 "per-table feedback 이 어차피 joint planning loss 로 driving 된다" — reasonable interpretation. marginal q_error 분리 불가 (marginal true cardinality 를 별도 측정 안 함) → 운영적으로 합리적 선택. ✅

per-table state 분리 자체는 본 논문 그대로. ✅

---

## 5. 결론 — 학술적 valid 인가?

**Yes, valid Exqutor reproduction**.

Section VI 의 7개 hyperparameter 가 전부 정확 일치, 식 1~6 가 line-by-line 동일 구현, AdaptiveState transition 이 momentum + LR decay + window-based update 모두 paper-faithful. multi-table per-table separate state 정책도 §V-B 명시대로.

**Audit caveat 2가지** (모두 학술적 valid 범위):
1. min/max clip [50, 5000] — paper 명시 X, 발산 방지 운영 가드. paper 의 보고 trajectory (DEEP ~358, SIFT ~415) 안에서 trigger X → reproduction fidelity 영향 0.
2. multi-table joint q_error 를 두 state 에 동일 feedback — paper 가 multi-table feedback 정책 명시 X 인 영역에 합리적 default. Δ% 비교 narrative 의 fidelity 보증에 충분.

본 연구의 4강 vs Adaptive paired Δ% 비교 narrative 는 **Exqutor reproduction 으로 valid** — paper 보고된 알고리즘 그대로 동일 query × seed × selectivity 격자에서 측정 가능. Sanity check 권장: `--fixed-size 385` 모드로 BERN baseline 과 paired Δ < 0.5%p verification (단일 line 315-316 / fixed_size CLI arg).
