# task A — B1 2단계 subsampling 동등성 검증 verdict

_생성_: 2026-05-17 · _측정_: `verify_b1.py` 6 cell × N_SEED=100 × 1000 query
_원자료_: `_internal/cache/rq3/b1verify_5_17/result_*.json` · _분석_: `_internal/scripts/analyze_b1verify_5_17.py`

---

## 1. 배경 — 무엇을 검증했나

대조군 B1(paper §V-B Bernoulli random sampling)의 측정에 **2단계 subsampling** 구조가 있었다.

- **2단계 (OLD, 기존 portfolio 측정 방식)**: 80M 전체 벡터 → cluster당 최대 500개씩 캐시(`CACHE_PER_CLUSTER=500`) ≈ 10,000개 중간 캐시 → 그 캐시에서 N=385 random sample.
- **1단계 (NEW, paper-faithful 수정본)**: 80M 전체 벡터에서 직접 N=385 random sample. `bernoulli_estimate` 에 `all_vecs` 인자를 전달하면 중간 캐시를 우회한다.

2단계는 cluster당 500개 균일 cap 때문에 큰 cluster를 구조적으로 과소대표한다(캐시 모집단 분석에서 `corr(cluster_size, 캐시점유비) = −0.98 ~ −0.985` — 모든 cell에서 강한 음의 상관 확인). 문제는 이 모집단 왜곡이 cardinality 추정 Q-error에 실질적 bias로 이어지는가다.

REPORT v12의 측정 portfolio 전체(B1 80건 + CaseB 1364건)는 2단계 방식으로 측정됐다. 따라서 이 검증 결과가 REPORT v12 수치의 신뢰성을 좌우한다.

---

## 2. 측정 — verify_b1.py

6 cell(데이터셋·scale 축을 대표)에서 각각 OLD 2단계 / NEW 1단계 B1을 N_SEED=100, 1000 query로 측정. `seed_base = s*13+7`로 trial s를 양 경로 공통 seed로 잡아 paired 비교 가능.

cell: A5-scale-sf1(DEEP sf1) · A5-scale-sf10(DEEP sf10) · A6-WIKI-sf10(WIKI sf10) · A1-DEEP(DEEP sf100) · A1-SIFT(SIFT sf100) · A1-SSN(SSN sf100).

---

## 3. 결과

| cell | OLD 2단계 mean | NEW 1단계 mean | diff% (OLD−NEW)/NEW | OLD CV% | paired t p | Wilcoxon p | d_paired | 판정 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| A1-DEEP | 1.6086 | 1.5615 | **+3.02%** | 6.9% | 0.0071 | 0.0008 | +0.275 | 유의 |
| A1-SIFT | 1.6699 | 1.5666 | **+6.59%** | 5.4% | <0.0001 | <0.0001 | +0.619 | 유의 |
| A6-WIKI-sf10 | 1.6480 | 1.5387 | **+7.10%** | 8.4% | <0.0001 | <0.0001 | +0.537 | 유의 |
| A1-SSN | 1.5358 | 1.5658 | −1.91% | 10.4% | 0.1367 | 0.2070 | −0.150 | 무의미 |
| A5-scale-sf1 | 1.5697 | 1.5473 | +1.45% | 6.9% | 0.2321 | 0.8852 | +0.120 | 무의미 |
| A5-scale-sf10 | 1.5714 | 1.5738 | −0.15% | 8.5% | 0.8981 | 0.9945 | −0.013 | 무의미 |

- |diff%| 평균 3.37%, 최대 7.10%. 부호: OLD>NEW 4 / OLD<NEW 2.
- paired t-test 유의(p<0.05): 3/6. 유의한 3 cell은 **전부 같은 방향(OLD 2단계가 더 높음)**, 효과크기 small~medium(d 0.28~0.62).

---

## 4. 판정 — 부분적·cell 의존 bias

순수 노이즈도, 균일한 체계적 bias도 아니다.

- **3/6 cell**(A1-DEEP, A1-SIFT, A6-WIKI-sf10)에서 2단계가 Q-error를 **+3~7% 유의하게 부풀린다**. 유의한 효과가 전부 같은 방향이라는 점은 — 만약 순수 노이즈였다면 부호가 무작위였을 것이므로 — 실재하는 체계적 성분임을 뜻한다.
- **3/6 cell**(A1-SSN, A5-scale-sf1, A5-scale-sf10)에서는 차이가 ±0.2~1.9%로 무의미. 2단계 캐시의 모집단 왜곡(corr −0.98)이 cardinality 추정 bias로 항상 이어지지는 않는다 — cluster 멤버십과 query hit 패턴의 상관 여부에 따라 cell마다 다르게 발현한다.
- scale 단순 의존도, 데이터셋 단순 의존도 아니다(WIKI sf10은 발현, DEEP sf10은 미발현; SIFT sf100 크게 발현, SSN sf100 미발현).

---

## 5. REPORT v12 함의 — headline 결론은 유지

REPORT v12의 paired Δ%는 (CaseB_qe − B1_qe)/B1_qe이고, portfolio의 B1은 2단계로 측정됐다. 2단계가 일부 cell에서 B1의 Q-error를 부풀린다면, 그 cell의 B1 기준선이 인위적으로 높아(나빠) CaseB가 인위적으로 더 좋아 보인다.

그러나 **headline 결론(CaseB가 92.2%에서 우월, 평균 Δ% −6.25%)은 뒤집히지 않는다**:

1. bias가 modest(부분적 3/6 cell, +3~7%)하고 전부 같은 방향이다 — 측정된 개선폭을 *약간 줄일* 뿐, 우월/열등을 *뒤집지* 않는다.
2. CaseB 내부 `est_b1`도 2단계다(현 코드의 1단계 fix는 B1 mode에만 적용, CaseB est_b1 미적용). 즉 기존 portfolio는 B1·CaseB 양 arm이 모두 2단계로 **내부 정합적**이다. 2단계 bias는 B1(est_b1 100%)에 CaseB(est_b1 50%)보다 더 크게 작용하므로 paired 차이에서 완전히 상쇄되지는 않으나, 부분 상쇄된다.
3. REPORT v12 §9 (4)는 B1 baseline의 measurement-run 단위 systematic bias가 본래 ±10~25%라 명시했다 — 2단계 vs 1단계 차이(평균 3.4%)는 그보다 작다.

추정: B1을 1단계로 교체하면 portfolio 평균 B1이 ~2~3.5% 낮아져 headline Δ%가 약 2~3%p 덜 음수가 될 수 있다(−6.25% → 대략 −3.5~−4.5% 추정). **여전히 명확한 개선, better 비율도 견고**(대부분의 Δ%가 0에서 충분히 떨어져 있어 2~3%p 이동으로 부호가 바뀌지 않음).

---

## 6. 결정 — 취한 조치 (사용자 지시 반영)

사용자가 "정확한 산출물 우선, 수지타산 따지지 말고 필요하면 전수 재측정하라"고 지시 — handoff §5의 "bias" 분기를 완전 적용했다.

1. **measure 코드 1단계 통일** — `measure_case_b`의 내부 est_b1 호출(L1197 부근)에 `all_vecs` 전달. B1 mode는 직전 세션에 이미 1단계. → B1·CaseB의 Bernoulli 성분이 전부 paper-faithful 1단계로 통일. 백업 `.bak_caseb_1stage_5_17`.
2. **`measure_3way` 함수 신규** — 사용자 지시("B1·CaseA·CaseB를 같이 실험, 셋의 coverage·건수 동일")대로, 한 측정에서 세 mode를 각자 AdaptiveState로 같은 trial·query 조건에서 matched 산출하는 `--mode 3way` 추가.
3. **3-way matched 캠페인 가동** — 전 portfolio 1508 (cell,sel,K,method)를 3-way로 측정(`launch_3way_campaign_5_17.sh`, 서버 tmux `campaign`, ~26h). B1·CaseA·CaseB가 한 측정에서 나와 완벽히 matched.

즉 §5에서 "추정"으로 적은 "1단계 전환 시 headline Δ% 약화"는 새 3-way 캠페인 실측으로 확정된다.

---

## 7. task I(REPORT v13 / narrative v8) 권고

3-way 캠페인 완료 후:
- 1508개 3-way JSON의 B1·CaseA·CaseB를 통합 → matched paired Δ% 재계산 (CaseA vs B1, CaseB vs B1, CaseA vs CaseB). 한 측정에서 나와 완벽히 짝지어짐.
- 기존 REPORT v12(2단계 측정 기반)는 새 1단계 3-way 결과로 대체. v12는 이력 보존.
- **honest limitation**: 본 verdict 문서 §1~5(2단계 subsampling 메커니즘, verify_b1 검증, cell 의존 +3~7% 효과)를 REPORT v13에 수록.

핵심 메시지: 완전한 검증을 시도한 결과 대조군 측정 구현의 미묘한 결함까지 찾아내 1단계로 바로잡았다 — 본 연구의 강점으로 서술한다.
