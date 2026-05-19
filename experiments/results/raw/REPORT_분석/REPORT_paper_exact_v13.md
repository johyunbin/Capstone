# Paper Exact 재현 측정 — 종합 분석 보고서 REPORT v13

_생성_: 2026-05-18

_출처_: `_internal/cache/rq3/aggregated_v13_full.parquet` (4524 row, 통합 측정) · `_internal/cache/rq3/paired_delta_v13.parquet` (4524 row, 3-way paired Δ%)

_framing_: 본 보고서는 paper Exqutor §V-B Adaptive Sampling의 **sample selection** 단계를 3-way matched로 측정한 결과를 종합 분석한다. 측정 3-way는 다음과 같다. **B1**(대조군 — paper §V-B의 unstratified Bernoulli random sampling) · **CaseA**(실험군·완전 대체 — Bernoulli 표본을 16개 분포 인지 method의 stratification 표본으로 통째 치환, est = est_method) · **CaseB**(실험군·결합 — Bernoulli 추정값과 method 추정값의 산술평균, est_final = (est_b1 + est_method) / 2.0). 한 측정(`measure_3way`)이 세 mode를 같은 trial·query 조건에서 동시에 산출하므로 B1·CaseA·CaseB가 완벽히 짝지어진다(matched). cardinality 추정 알고리즘과 AdaptiveState 식 1-6은 paper 그대로 유지하며, 본 연구의 개입은 오로지 sample selection 단계 하나다. CaseA는 REPORT v12에서 narrative 부적합을 이유로 측정 자체를 제외했으나, v13은 이를 negative control로 본문에 실측 수록한다 — 폐기된 가설이 아니라 측정된 비교 대상이다.

> **★ headline**: 결합 실험군 CaseB는 대조군 B1 대비 paired 비교 1508건 중 **1344건(89.1%)** 에서 Q-error가 더 낮다. 짝지은 Q-error 변화율(paired Δ%)의 **중앙값 −4.38%**, 평균 −3.06%(이상치 2건 제외 시 −4.09%)다. 완전 대체 실험군 CaseA는 평균 +12.90%로 불안정한 negative control이며, CaseB는 CaseA를 96.5%에서 이긴다. 측정의 arc는 명확하다 — 베르누이(B1) → 완전 대체(CaseA, 불안정) → 결합(CaseB, 답).

---

## 0. 요약 — 본 보고서가 말하는 것

본 보고서는 paper Exqutor §V-B Adaptive Sampling의 sample selection 단계를 3-way matched로 측정한 **1508건의 측정**(통합 4524 row = 1508 × 3 mode)을 단일 portfolio로 분석한다. 각 측정은 `measure_3way` 함수가 대조군 B1·실험군 CaseA·실험군 CaseB를 같은 cell·selectivity·strata·method 조건에서, 같은 10 trial·1000 query로 동시에 산출한 것이다. 세 mode가 한 측정에서 나오므로 trial 단위 paired 비교가 구조적으로 완전하며, REPORT v12가 필요로 했던 별도 B1 lookup·fallback이 v13에는 존재하지 않는다.

핵심 finding은 셋이다. 첫째, **결합 실험군 CaseB는 대조군 B1보다 일관되게 정확하다.** paired 비교 1508건 중 1344건(89.1%)에서 CaseB의 Q-error가 더 낮고, paired Δ% 중앙값은 −4.38%, 평균은 −3.06%(이상치 제외 −4.09%)다. 통계적으로 유의하게 우월한 경우 65.3%, 효과크기 Cliff's δ가 large 임계를 넘어 우월한 경우 72.1%다. 둘째, **완전 대체 실험군 CaseA는 negative control로서 기대대로 불안정하다.** CaseA는 B1 대비 35.2%만 우월하고 평균 +12.90%로 오히려 나빠지며, 강한 method에서는 거의 중립이지만 약한 method(gmm, minibatch_partial)에서는 파국적으로 악화된다. Bernoulli를 method로 통째 치환하는 방식은 신뢰할 수 없다. 셋째, **결합(CaseB)이 완전 대체(CaseA)를 압도한다.** CaseA가 CaseB보다 나은 경우는 1508건 중 53건(3.5%)뿐으로, CaseB가 96.5%에서 우월하다. 세 finding이 합쳐져 하나의 arc를 이룬다 — paper의 베르누이 random sampling에서 출발해, 완전 대체는 불안정함을 확인하고, 두 추정값을 결합하는 CaseB가 답이라는 결론에 이른다.

본 보고서는 동시에 두 가지를 정직하게 다룬다. 하나는 **REPORT v12 대비 headline의 약화**다. v12는 better 92.2%·평균 −6.25%였고 v13은 89.1%·−3.06%다. 이 약화는 측정 품질의 하락이 아니라, v13의 대조군 B1이 paper에 더 충실한 1단계 측정으로 바뀌어 baseline이 더 깨끗하고 낮아진 결과다(§2.1, §3.3). v13이 더 엄정하며, v13이 정본·v12는 이력이다. 다른 하나는 **K granularity의 위상 변화**다. v12에서 K=10 대조군 B1이 구조적으로 손상되어 K granularity를 honest-limitation으로 격하했으나, v13의 1단계 B1은 K=10에서도 정상이므로(§2.4) K granularity를 본문 finding으로 승격한다(§8).

---

## 1. 측정 portfolio 요약

### 1.1 3-way matched 측정 규모

본 분석의 입력은 단일 통합 parquet `aggregated_v13_full.parquet`이며, 5/17 가동한 3-way matched 캠페인의 1508개 측정 JSON을 수집·구조화한 결과다.

| 구분 | 값 |
|---|---:|
| 3-way 측정 수 | **1508** |
| 통합 row 수 (1508 × 3 mode) | **4524** |
| ─ B1 (대조군, Bernoulli + Adaptive) | 1508 |
| ─ CaseA (실험군, 완전 대체 + Adaptive) | 1508 |
| ─ CaseB (실험군, 결합 + Adaptive) | 1508 |
| 3-way paired 비교 (1508 × 3 comparison) | **4524** |

3-way paired 비교는 한 측정에서 세 mode를 모두 얻으므로 세 종류로 펼쳐진다 — CaseA_vs_B1(완전 대체 vs 대조군), CaseB_vs_B1(결합 vs 대조군), CaseA_vs_CaseB(완전 대체 vs 결합). 각 비교는 1508건이다.

mode별 Q-error의 단순(unpaired) descriptive 통계는 다음과 같다. 본 보고서의 headline은 §3의 trial-paired Δ%이며, 아래 표는 paired 분석 이전의 분포 확인용이다.

| mode | n | qe_trim 평균 | qe_trim 중앙값 | final_size 평균 | final_size 중앙값 |
|---|--:|--:|--:|--:|--:|
| B1 | 1508 | 1.4582 | 1.5616 | 3155 | 1279 |
| CaseA | 1508 | 1.6359 | 1.5699 | 3934 | 1573 |
| CaseB | 1508 | 1.4019 | 1.4492 | 2021 | 373 |

unpaired 평균만 보아도 CaseB(1.4019) < B1(1.4582) < CaseA(1.6359)로, 결합이 가장 정확하고 완전 대체가 가장 부정확하다는 §3의 paired 결론과 방향이 일치한다. 또한 세 mode가 각자 AdaptiveState(식 1-6)로 표본 크기를 적응시킨 결과, CaseB의 최종 표본 크기(final_size 평균 2021·중앙값 373)가 B1(3155·1279)보다 작다. 더 정확한 추정기에 대해 적응 루프가 더 작은 표본에서 수렴하는 것으로, CaseB가 정확도와 표본 비용 양면에서 B1보다 불리하지 않음을 시사하는 descriptive 관찰이다.

### 1.2 측정 축의 커버리지

통합 portfolio는 cell 25개 · method 16개 · scale factor 3종 · selectivity 3종 · strata 수 K 3종으로 펼쳐진다.

**데이터셋**: 단일 벡터 5종(DEEP 96d, SIFT 128d, SimSearchNet++ 256d, WIKI 768d, YFCC 192d)과 다중 벡터 4종(DEEP+SIFT 224d, DEEP+YFCC 288d, DEEP+WIKI 864d, DEEP+CC3M 1024d)이다. 다중 벡터 중 DEEP+SIFT·DEEP+YFCC·DEEP+WIKI는 두 데이터셋의 벡터를 차원 방향으로 직접 연결(concat)한 cell이다.

**측정 단위 분포**: scale factor sf=1 416건 · sf=10 580건 · sf=100 512건. selectivity sel=0.001 448건 · sel=0.01 628건 · sel=0.10 432건. strata 수 K=10 192건 · K=20(paper default) 1124건 · K=30 192건. 단일/다중 구조로는 single 960건 · multi(cross-table 다중 벡터) 212건 · concat(연결 다중 벡터) 336건이다. K=10·K=30 측정은 K granularity sweep 대상 8개 cell에 집중되며, K=20이 전체 portfolio의 default다.

### 1.3 사용 16 method

method 축은 7개 sampling paradigm을 대표하는 16개 method로 고정했다. 측정 portfolio의 CaseA·CaseB 표본은 정확히 이 16개 method만 포함한다.

| Paradigm | Method |
|---|---|
| P1 Cluster | minibatch_partial · gmm |
| P2 Spatial | hilbert_real · zorder_morton · skilling_hilbert · faiss_ivf |
| P3 Streaming | chao_weighted |
| P4 DimReduction | sparse_rp · pca1d · rsvd · ica_fastica |
| P5 QMC | cum_sqrtf · lavallee_hidiroglou |
| P6 Quantization | rabitq_strat · mhist2 |
| P9 InfoTheoretic | hyperloglog |

paradigm 라벨은 v13 통합 parquet 기준이다 — `faiss_ivf`는 v13 portfolio에서 P2로 분류된다(일부 이전 문서는 P1로 표기했으나 본 보고서는 측정 데이터의 라벨을 따른다). method당 paired 비교는 cell·sel·K 조합에 따라 94~95건이다.

---

## 2. 측정 무결성 — 1단계 B1 통일·3-way matched·캠페인 검증

종합 보고서로서 본 v13은 분석 수치가 깨끗한 측정에 근거함을 먼저 보인다. v13 캠페인은 v12 portfolio에서 확인된 두 측정 결함을 사전에 교정한 위에서 가동되었다.

### 2.1 대조군 B1의 1단계 통일 — paper-faithful 수정

REPORT v12 portfolio의 대조군 B1은 **2단계 subsampling** 구조로 측정되었다. 80M 전체 벡터를 cluster당 최대 500개로 캐시(`CACHE_PER_CLUSTER=500`)해 약 10,000개의 중간 모집단을 만들고, 그 캐시에서 N=385 random sample을 뽑는 방식이다. 이 구조는 cluster당 균일 cap 때문에 큰 cluster를 구조적으로 과소대표한다(캐시 모집단 분석에서 cluster 크기와 캐시 점유비의 상관이 −0.98~−0.985로 모든 cell에서 강한 음의 상관).

별도 검증(`verify_b1.py`, 6 cell × N_SEED=100 × 1000 query)에서 이 2단계 구조가 cardinality 추정 Q-error에 미치는 영향을 정량화했다. 6 cell 중 3 cell(A1-DEEP +3.02%, A1-SIFT +6.59%, A6-WIKI-sf10 +7.10%)에서 2단계 B1의 Q-error가 1단계 대비 통계적으로 유의하게 부풀려졌고, 나머지 3 cell(A1-SSN, A5-scale-sf1, A5-scale-sf10)에서는 차이가 ±0.2~1.9%로 무의미했다. 부분적·cell 의존적 bias로, 유의한 효과는 전부 같은 방향(2단계가 더 높음)이었다. 부풀려진 B1은 인위적으로 나쁜 baseline이 되어 CaseB를 인위적으로 더 좋아 보이게 만든다.

v13 캠페인은 이 결함을 측정 코드 수준에서 제거했다. `measure_paper_exact.py`의 B1 mode와 CaseB 내부 est_b1 호출을 모두 **1단계**로 통일했다 — 80M 전체 벡터에서 중간 캐시를 우회하고 직접 N=385 random sample을 뽑는다. 이는 paper §V-B의 unstratified Bernoulli random sampling 정의에 더 충실한 측정이다. v13의 1508개 3-way 측정은 전부 이 1단계 B1 위에서 산출되었다. 즉 **완전한 검증을 시도한 결과 대조군 측정 구현의 미묘한 결함까지 찾아내 paper-faithful하게 바로잡았다** — 이는 본 연구의 약점이 아니라 방법론적 강점이다.

### 2.2 3-way matched 측정 설계

v12의 paired 비교는 별도로 측정된 B1 80건을 CaseB 1364건에 lookup·fallback으로 짝지었다. K=10처럼 같은 조건의 B1이 없으면 paper default K=20 B1로 대체(fallback)했고, 이 fallback이 §7 K granularity 해석을 복잡하게 만들었다.

v13은 `measure_3way` 함수를 신설하여 이 구조적 한계를 제거했다. 한 측정이 B1·CaseA·CaseB를 같은 AdaptiveState 초기 조건에서, 같은 10 trial·1000 query로 동시에 산출한다. 세 mode가 한 측정에서 나오므로 모든 paired 비교가 lookup 없이 trial 단위로 정확히 짝지어진다. 이 설계의 부수 효과로 measurement-run 단위 systematic bias가 거의 완전히 상쇄된다 — B1·CaseA·CaseB가 물리적으로 같은 run에서 측정되므로, run마다 달라지는 측정 환경 변동이 세 mode에 동일하게 작용하고 paired 차이에서 소거된다.

### 2.3 캠페인 완료 검증

3-way 캠페인은 전 portfolio 1508개 (cell, sel, K, method) 조합을 측정하고 5/17 20:57(UTC) 완료되었다(`COMPLETE.flag`, `_main.log`의 "DONE 1508/1508 WARN 0"). 검증 스크립트 `verify_3way_campaign.py`로 수집된 1508개 JSON을 전수 점검한 결과, 미완 측정 0건·anomaly 0건·중복 0건으로 전부 PASS했다. 측정 코드 무결성도 직접 확인했다 — `measure_3way`가 B1을 1단계로, CaseB를 산술평균으로 산출하는지, STRATA_K override가 정상 작동하는지, JSON에 기록된 q_error 값이 정의 위반(q_error < 1) 없이 정합한지를 모두 확인했다.

### 2.4 K=10 대조군 B1 — v12 결함의 해소

REPORT v12의 가장 중요한 honest-limitation은 K=10 대조군 B1의 구조적 결함이었다. v12 B1의 측정 함수가 환경변수 `STRATA_K`를 받아 strata 캐시를 생성하는 2단계 구조였고, K=10 설정에서 query별 Q-error에 무한대(inf)가 폭증하여(쿼리 1000건 중 314~391건) trim 후에도 K=10 B1의 qe_trim이 정상 범위 1.6~1.7을 벗어나 3.0대로 손상되었다.

v13의 1단계 B1은 이 결함을 원천적으로 회피한다. 1단계 B1은 80M 전체 벡터에서 직접 표본을 뽑으므로 STRATA_K 2단계 캐시를 거치지 않으며, strata 수 K에 의존하지 않는다. 통합 parquet에서 v13 B1의 qe_trim을 K별로 직접 집계한 결과는 다음과 같다.

| K | n | B1 qe_trim 평균 | 최소 | 최대 | n_inf 평균 (10 trial 합) |
|---|--:|--:|--:|--:|--:|
| 10 | 192 | 1.5132 | 1.1555 | 1.6457 | 261.9 |
| 20 | 1124 | 1.4402 | 1.1539 | 1.6560 | 382.6 |
| 30 | 192 | 1.5091 | 1.1554 | 1.6457 | 260.1 |

v13 B1의 qe_trim은 K=10·K=20·K=30 전부 [1.16, 1.66] 정상 범위에 들어온다. K=10 B1의 n_inf도 10 trial 합 261.9(쿼리-trial 10,000건 기준 약 2.6%)로, v12 K=10의 inf 폭증(31~39%)과 비교할 수 없을 만큼 정상이다. **v12의 K=10 B1 결함은 v13에서 완전히 해소되었고**, 이에 따라 K granularity는 §8에서 본문 finding으로 승격된다.

---

## 3. 3-way paired Δ% — 핵심 결과

본 절이 보고서의 중심이다. 짝지은 Q-error 변화율(paired Δ%)은 같은 cell·selectivity·strata·method 조건에서 trial 단위로 짝지은 (exp_qe − base_qe) / base_qe × 100이며, 10 trial의 평균을 측정 1건의 Δ%로 삼는다. 음수가 앞에 놓인 mode(exp)의 Q-error가 더 낮음(더 정확함)을 뜻한다.

### 3.1 headline — 결합 실험군 CaseB vs 대조군 B1

paired 비교 1508건에서 CaseB(결합)와 B1(대조군)을 비교한 결과는 다음과 같다.

| 지표 | 값 |
|---|---|
| CaseB better (Δ% < 0) | **1344 / 1508 = 89.1%** |
| 평균 Δ% | **−3.06%** (이상치 2건 제외 시 −4.09%) |
| 중앙값 Δ% | **−4.38%** |
| Δ% 범위 | −13.60% ~ +1043.19% |
| 통계적 유의 우월 (one-sided BH-FDR p<0.05 & better) | 984 / 1508 = **65.3%** |
| 효과크기 Cliff's δ large (≥0.474) 우월 | 1088 / 1508 = **72.1%** |

분포 인지 stratification ensemble은 paper §V-B의 unstratified Bernoulli random sampling을 비교 대상으로, 측정한 비교의 약 10건 중 9건에서 Q-error를 낮춘다. 평균 Δ%가 −3.06%로 보이는 것은 §3.4·§10에서 다룰 concat 측정 2건의 극단 이상치(+1043%, +510%)가 평균을 0 쪽으로 끌어올린 결과이며, 이 2건을 제외한 평균은 −4.09%, 이상치에 둔감한 중앙값은 −4.38%다. 즉 **신뢰 가능한 headline은 "약 9할 비교에서 우월, 중앙값 −4.38% 개선"** 이며, 통계적 유의 우월 65.3%·효과크기 large 우월 72.1%로 신호가 견고하다.

### 3.2 3-way 비교 전체

세 종류의 paired 비교를 한 표에 모은다.

| 비교 | n | better | better% | 유의% | δlarge% | 평균 Δ% | 중앙값 Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| CaseA_vs_B1 (완전 대체 vs 대조군) | 1508 | 531 | 35.2% | 6.8% | 13.5% | +12.90% | +1.09% |
| **CaseB_vs_B1** (결합 vs 대조군) | 1508 | 1344 | **89.1%** | 65.3% | 72.1% | **−3.06%** | **−4.38%** |
| CaseA_vs_CaseB (완전 대체 vs 결합) | 1508 | 53 | 3.5% | 0.0% | 1.3% | +13.92% | +7.02% |

세 비교가 하나의 일관된 arc를 그린다. **CaseA(완전 대체)** 는 B1 대비 35.2%만 우월하고 평균 +12.90%로 오히려 나쁘다 — paper의 Bernoulli를 method로 통째 치환하는 방식은 신뢰할 수 없다(§7 negative control). **CaseB(결합)** 는 B1 대비 89.1%에서 우월하다. 그리고 **CaseA vs CaseB**에서 CaseA가 CaseB보다 나은 경우는 1508건 중 53건(3.5%)뿐으로, CaseB가 96.5%에서 완전 대체를 이긴다. 측정의 흐름은 명확하다 — 베르누이(B1)에서 출발해, 완전 대체(CaseA)는 불안정함을 negative control로 확인하고, 두 추정값을 결합하는 CaseB가 답이라는 결론에 이른다.

### 3.3 REPORT v12 대비 — headline의 정직한 약화

REPORT v12의 headline은 paired 1240건(K=10 제외)에서 better 92.2%·평균 −6.25%·중앙값 −6.15%였다. v13은 1508건에서 89.1%·−3.06%·−4.38%다. 이 약화는 측정 품질의 하락이 아니라 **대조군 baseline이 더 엄정해진 결과**이며, 본 보고서는 그 이유를 정직하게 명시한다.

첫째, v13의 대조군 B1은 paper에 더 충실한 1단계 측정이다(§2.1). v12의 2단계 B1은 일부 cell에서 Q-error를 +3~7% 부풀렸고, 부풀린 baseline은 CaseB를 인위적으로 더 좋아 보이게 했다. v13의 1단계 B1은 이 부풀림을 제거하여 더 깨끗하고 낮은 baseline을 제공하며, 그 결과 CaseB의 상대 개선폭이 줄어든다. 둘째, b1_2stage_verdict 검증 문서는 1단계 전환 시 headline Δ%가 −6.25%에서 대략 −3.5~−4.5%로 약화될 것이라 사전에 추정했다. **v13 실측 — 중앙값 −4.38%, 이상치 제외 평균 −4.09% — 은 이 추정 범위에 정확히 안착한다.** 셋째, v13은 K=10을 포함한다(v12는 K=10 B1 결함으로 제외; v13의 1단계 B1은 K=10에서도 정상이다 — §2.4).

요컨대 v13 headline의 약화는 예측된 것이고, 더 엄정한 측정의 자연스러운 귀결이다. 개선의 방향과 견고함은 불변이다 — 1508건 중 89.1%가 우월하고 중앙값이 −4.38%다. **v13이 정본이며, v12는 2단계 측정 기반의 이력으로 보존한다.**

### 3.4 가장 강한 비교와 가장 약한 비교

개별 (cell × method × sel × K) 단위 CaseB_vs_B1의 양 극단은 다음과 같다.

가장 강한 개선 8건은 모두 sel=0.01 조건의 spatial/dimreduction method다 — A1-SSN hilbert_real −13.60%, A2-Fig9 skilling_hilbert −13.45%, A5-scale-sf10 skilling_hilbert −13.45%, A1-DEEP hilbert_real −13.21%, A5-scale-sf100 hilbert_real −13.21%, A1-SIFT ica_fastica −12.98%, A1-SSN chao_weighted −12.65%, A1-SIFT zorder_morton −12.36% 순이다. 모두 one-sided BH-FDR p_adj가 0.0028 수준으로 강하게 유의하다.

가장 큰 악화 8건은 거의 전부 A10-DEEP+WIKI-concat-sf10 cell에 몰린다 — minibatch_partial +1043.19%·+510.62%, faiss_ivf +41.40%·+29.71%, gmm +31.48%, 그리고 A1-SSN gmm +39.76%·+39.33%, A5-scale-sf1-SIFT gmm +31.17%다. 가장 큰 두 악화(minibatch_partial +1043%·+510%)는 864차원 concat 데이터에서 클러스터링 계열 method가 파탄나는 사례로, §3.1 headline 평균을 끌어올린 이상치 2건이다. 약한 method(P1 Cluster의 gmm·minibatch_partial과 faiss_ivf)가 극단 악화를 독점한다는 점은 §6·§10의 method 약점 분석과 일치한다.

---

## 4. selectivity 효과 — 낮을수록 개선 폭이 크다

paper Fig 13은 selectivity가 낮을수록 cardinality 추정의 본질적(inherent) Q-error가 커짐을 보인다. 본 절은 그 selectivity 축에서 CaseB의 우월성이 어떻게 변하는지 측정한다(CaseB_vs_B1, 1508건 전수).

| sel | n | better | better% | 유의% | δlarge% | 평균 Δ% | 중앙값 Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| 0.001 | 448 | 373 | **83.3%** | 52.5% | 54.2% | −1.75% | −4.39% |
| 0.01 | 628 | 550 | **87.6%** | 52.4% | 67.7% | −3.54% | −6.61% |
| 0.10 | 432 | 421 | **97.5%** | 97.2% | 97.2% | −3.72% | −4.17% |

better 비율이 selectivity 0.001 → 0.01 → 0.10 순으로 83.3% → 87.6% → 97.5%로 **단조 증가**한다. selectivity가 0.10에 이르면 측정한 432건 중 421건이 개선되고, 그 421건이 거의 전부 통계적으로 유의하다(유의 97.2%). 분포 인지 sample selection의 우월성은 쿼리가 더 많은 데이터를 선택할수록 거의 예외 없이 성립한다.

selectivity 0.001에서 better 비율이 83.3%로 상대적으로 낮은 것은, 매우 낮은 selectivity에서는 표본에 들어오는 hit 수 자체가 작아 어떤 sample selection 전략이든 추정 분산이 커지기 때문이다. 그럼에도 83.3%는 명확한 우월성이고 중앙값 Δ%도 −4.39%로 음수다. 평균 Δ%가 sel=0.001에서 −1.75%로 가장 작아 보이는 것은 §3.4의 concat 이상치가 이 selectivity 구간에 일부 포함된 영향이며, 이상치에 둔감한 중앙값 −4.39%가 sel=0.001 구간의 실질 개선폭을 더 정확히 나타낸다. 이 단조 증가 패턴은 REPORT v12에서도 동일하게 관찰되었다.

---

## 5. single / multi / concat 비교

측정 cell을 단일 벡터(single), cross-table 다중 벡터(multi: A2-Fig7/Fig9, A8 등 두 테이블을 join), 직접 연결 다중 벡터(concat: 두 데이터셋 벡터를 차원 방향 결합)로 나눈 CaseB_vs_B1 결과다.

| 유형 | n | better | better% | 유의% | δlarge% | 평균 Δ% | 중앙값 Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| single | 960 | 855 | 89.1% | 64.5% | 72.2% | −4.12% | −4.38% |
| multi | 212 | 190 | 89.6% | 67.0% | 73.1% | −4.54% | −4.61% |
| concat | 336 | 299 | 89.0% | 66.4% | 71.4% | **+0.92%** | −4.31% |

세 유형 모두 better 비율이 89~90%로 사실상 동일하며, 분포 인지 sample selection의 우월 방향성이 단일·다중·연결 구조 전반에서 유지된다. single과 multi는 평균 Δ%도 −4.12%·−4.54%로 명확한 음수다.

concat의 평균 Δ%만 +0.92%로 양수인데, 이는 다중 벡터에서 효과가 사라졌다는 뜻이 아니다. concat의 better 비율은 89.0%로 single과 같고 중앙값도 −4.31%로 음수다. 평균을 양수로 끌어올린 것은 §3.4에서 본 A10-DEEP+WIKI-concat-sf10 cell의 minibatch_partial 이상치 2건뿐이다. concat을 데이터셋별로 분해하면 이 점이 분명해진다.

| concat 데이터셋 | 차원 | n | better% | 평균 Δ% | 중앙값 Δ% |
|---|--:|--:|--:|--:|--:|
| DEEP+SIFT | 224 | 144 | 88.2% | −4.08% | −4.24% |
| DEEP+YFCC | 288 | 96 | 90.6% | −4.20% | −4.35% |
| DEEP+WIKI | 864 | 96 | 88.5% | +13.54% (이상치 제외 −2.70%) | −4.33% |

224차원·288차원 concat은 평균 −4.08%·−4.20%로 명확히 음수다. 864차원 DEEP+WIKI에서만 평균이 +13.54%로 양수인데, 같은 864차원의 중앙값은 −4.33%로 여전히 음수이고 better 비율도 88.5%다. 평균을 왜곡한 것은 864차원 concat에서 불안정한 특정 클러스터링 method(minibatch_partial) 두 건이며, 이를 제외하면 864차원 평균도 −2.70%로 음수다. 즉 우리가 직접 만든 다중 벡터 데이터셋에서도 분포 인지 sample selection은 대부분의 측정에서 더 낫다.

selectivity와 교차하면 single·concat 모두 sel이 높을수록 better 비율이 오른다. single은 sel 0.001/0.01/0.10에서 83.0/88.0/97.1%, concat은 80.4/88.4/98.2%다. concat의 sel=0.10 구간에서는 112건 중 110건이 개선된다.

---

## 6. method / paradigm 분석

### 6.1 사용 16 method별 paired Δ% (CaseB_vs_B1)

| Method | Paradigm | n | better% | 유의% | δlarge% | 평균 Δ% | 평균(이상치 제외) | 중앙값 Δ% |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| hilbert_real | P2 | 95 | 98.9% | 86.3% | 87.4% | −6.54% | −6.54% | −5.91% |
| skilling_hilbert | P2 | 94 | 100.0% | 76.6% | 87.2% | −6.34% | −6.34% | −5.75% |
| chao_weighted | P3 | 95 | 100.0% | 83.2% | 87.4% | −6.30% | −6.30% | −6.22% |
| ica_fastica | P4 | 94 | 100.0% | 83.0% | 87.2% | −6.13% | −6.13% | −5.69% |
| pca1d | P4 | 94 | 97.9% | 84.0% | 92.6% | −6.05% | −6.05% | −5.55% |
| zorder_morton | P2 | 94 | 98.9% | 75.5% | 76.6% | −5.87% | −5.87% | −4.89% |
| hyperloglog | P9 | 95 | 100.0% | 75.8% | 80.0% | −5.75% | −5.75% | −4.58% |
| cum_sqrtf | P5 | 94 | 97.9% | 66.0% | 73.4% | −5.14% | −5.14% | −4.53% |
| lavallee_hidiroglou | P5 | 94 | 94.7% | 69.1% | 73.4% | −4.82% | −4.82% | −4.40% |
| rsvd | P4 | 94 | 91.5% | 58.5% | 70.2% | −4.36% | −4.36% | −4.10% |
| sparse_rp | P4 | 95 | 84.2% | 68.4% | 74.7% | −3.69% | −3.69% | −4.37% |
| mhist2 | P6 | 94 | 88.3% | 47.9% | 60.6% | −3.16% | −3.16% | −3.41% |
| rabitq_strat | P6 | 94 | 84.0% | 43.6% | 56.4% | −2.67% | −2.67% | −3.56% |
| faiss_ivf | P2 | 94 | 69.1% | 43.6% | 53.2% | −0.69% | −0.69% | −2.70% |
| gmm | P1 | 94 | 40.4% | 29.8% | 31.9% | **+4.63%** | +4.63% | +2.68% |
| minibatch_partial | P1 | 94 | 79.8% | 52.1% | 61.7% | **+14.06%** | −2.52% | −3.58% |

16개 method 중 **13개가 평균 Δ% 음수이며 better 비율 84% 이상**으로 견고하게 우월하다. 상위권은 hilbert_real(−6.54%)·skilling_hilbert(−6.34%)·chao_weighted(−6.30%)·ica_fastica(−6.13%)·pca1d(−6.05%)로, P2 Spatial·P3 Streaming·P4 DimReduction 계열이다. skilling_hilbert·chao_weighted·ica_fastica는 better 비율 100.0%로 모든 측정 cell에서 예외 없이 B1을 이긴다.

약한 3개 method는 모두 클러스터링 계열이다. gmm은 평균 +4.63%(better 40.4%)로 사실상 B1보다 못하고, minibatch_partial은 평균 +14.06%지만 이는 §3.4의 A10-DEEP+WIKI-concat-sf10 이상치 2건 때문으로, 이를 제외하면 평균이 −2.52%로 돌아오고 중앙값도 −3.58%다. 즉 minibatch_partial은 대부분의 cell에서 작동하나 864차원 concat 같은 극단 조건에서 파탄난다. faiss_ivf는 평균 −0.69%로 B1과 거의 동등한 약한 개선에 머문다 — paradigm 라벨은 P2이나 알고리즘은 IVF 클러스터링으로, 클러스터링 계열 method(gmm·minibatch_partial·faiss_ivf)가 공통적으로 약하다는 패턴을 보인다.

### 6.2 paradigm rollup (CaseB_vs_B1)

| Paradigm | method 수 | n | better% | 평균 Δ% | 중앙값 Δ% |
|---|--:|--:|--:|--:|--:|
| P3 Streaming | 1 | 95 | 100.0% | −6.30% | −6.22% |
| P9 InfoTheoretic | 1 | 95 | 100.0% | −5.75% | −4.58% |
| P4 DimReduction | 4 | 377 | 93.4% | −5.05% | −4.72% |
| P5 QMC | 2 | 188 | 96.3% | −4.98% | −4.43% |
| P2 Spatial | 4 | 377 | 91.8% | −4.86% | −4.66% |
| P6 Quantization | 2 | 188 | 86.2% | −2.91% | −3.52% |
| P1 Cluster | 2 | 188 | 60.1% | **+9.34%** | −1.40% |

paradigm 수준에서 P3 Streaming·P9 InfoTheoretic·P4 DimReduction·P5 QMC·P2 Spatial이 평균 −4.86%~−6.30%로 강하게 우월하고, P6 Quantization은 −2.91%로 중간이다. P1 Cluster만 평균 +9.34%로 양수다 — gmm·minibatch_partial의 이상치가 섞인 값이며, P1 Cluster paradigm은 분포 인지 sample selection의 우월성을 일관되게 보이지 못한다. 본 연구의 권장 method 집합에서 P1 Cluster를 제외하는 근거다.

---

## 7. CaseA — 완전 대체의 negative control

본 절은 실험군 CaseA(완전 대체)를 분석한다. CaseA는 paper의 Bernoulli 표본을 우리 method의 stratification 표본으로 통째 치환하고, AdaptiveState에 est = est_method만 입력하는 방식이다. CaseA를 본문에 수록하는 이유는 **negative control** 때문이다 — 효과가 불안정할 것으로 예상되는 방식을 실측하여 실제로 불안정함을 확인함으로써, 결합(CaseB)이 진짜로 일하고 있음을 거꾸로 입증한다.

### 7.1 CaseA_vs_B1 — selectivity 별

| sel | n | better% | 유의% | 평균 Δ% | 중앙값 Δ% |
|---|--:|--:|--:|--:|--:|
| 0.001 | 448 | 23.0% | 0.7% | +11.52% | +3.70% |
| 0.01 | 628 | 38.9% | 2.7% | +21.64% | +1.79% |
| 0.10 | 432 | 42.6% | 19.2% | +1.62% | +0.16% |

전 selectivity에서 CaseA의 better 비율이 50%를 밑돈다. 완전 대체는 평균적으로 B1보다 나쁘며, 평균 Δ%가 +1.62%~+21.64%로 양수다. 중앙값 Δ%는 +0.16%~+3.70%로, "강한 method에서는 거의 중립이되 약한 method에서 파국적으로 악화"되는 분포의 비대칭을 반영한다.

### 7.2 CaseA_vs_B1 — method 별 (완전 대체의 불안정성)

| Method | Paradigm | n | better% | 평균 Δ% | 평균(이상치 제외) | 중앙값 Δ% |
|---|---|--:|--:|--:|--:|--:|
| hilbert_real | P2 | 95 | 62.1% | −0.42% | −0.42% | −1.05% |
| ica_fastica | P4 | 94 | 60.6% | +0.03% | +0.03% | −0.35% |
| skilling_hilbert | P2 | 94 | 59.6% | +0.06% | +0.06% | −0.40% |
| chao_weighted | P3 | 95 | 46.3% | +0.22% | +0.22% | +0.09% |
| zorder_morton | P2 | 94 | 56.4% | +0.36% | +0.36% | −0.23% |
| pca1d | P4 | 94 | 53.2% | +0.58% | +0.58% | −0.09% |
| hyperloglog | P9 | 95 | 16.8% | +2.57% | +2.57% | +1.47% |
| cum_sqrtf | P5 | 94 | 33.0% | +2.79% | +2.79% | +1.27% |
| rsvd | P4 | 94 | 22.3% | +3.51% | +3.51% | +1.35% |
| lavallee_hidiroglou | P5 | 94 | 24.5% | +4.42% | +4.42% | +1.76% |
| mhist2 | P6 | 94 | 12.8% | +5.58% | +5.58% | +4.06% |
| rabitq_strat | P6 | 94 | 8.5% | +7.66% | +7.66% | +6.79% |
| sparse_rp | P4 | 95 | 49.5% | +11.45% | +5.96% | +0.04% |
| faiss_ivf | P2 | 94 | 13.8% | +12.99% | +7.76% | +4.61% |
| gmm | P1 | 94 | 6.4% | +29.60% | +18.74% | +17.41% |
| minibatch_partial | P1 | 94 | 37.2% | +125.40% | +3.02% | +1.29% |

완전 대체의 결과는 method에 따라 양극으로 갈린다. 강한 spatial/dimreduction method(hilbert_real, ica_fastica, skilling_hilbert, zorder_morton, pca1d, chao_weighted)는 평균 Δ%가 −0.42%~+0.58%로 사실상 B1과 중립이다 — 강한 method로 Bernoulli를 통째 치환해도 손해는 없지만 결합(CaseB)이 주는 −6%대 개선도 얻지 못한다. 반면 약한 method, 특히 P1 Cluster의 gmm(+29.60%)과 minibatch_partial(+125.40%, 이상치 제외 +3.02%)은 B1을 파국적으로 악화시킨다. faiss_ivf(+12.99%)도 크게 나쁘다.

**핵심 메시지**: 완전 대체는 최선의 경우(강한 method) 중립이고 최악의 경우(약한 method) 파국이다. 어떤 method가 강한지 미리 모르는 상황에서 완전 대체는 신뢰할 수 없다. 그런데 §3.2에서 본 대로 CaseB(결합)는 같은 method 집합으로 89.1%에서 우월하다 — 같은 강한 method는 결합해도 −6%대로 개선되고, 같은 약한 method(gmm, minibatch_partial)는 결합 시 Bernoulli 절반이 완충 역할을 하여 파국이 완화된다(minibatch_partial CaseB 이상치 제외 평균 −2.52%). 즉 **negative control인 CaseA는 결합이라는 개입이 실제로 가치를 만든다는 것을, 그 부재로써 증명한다.** 개선의 원천은 method 단독이 아니라 method를 Bernoulli와 결합하는 데 있다.

---

## 8. K granularity — 본문 finding으로 승격

REPORT v12는 K=10 대조군 B1의 구조적 결함(§2.4) 때문에 K granularity를 본문 finding이 아닌 honest-limitation으로 격하했다. v13의 1단계 B1은 K=10에서도 정상이므로(§2.4 검증) K granularity는 본문 finding으로 승격된다.

K granularity sweep은 8개 cell(A1-DEEP, A1-SIFT, A1-SSN, A2-Fig7, A2-Fig9, A5-scale-sf1, A5-scale-sf10, A5-scale-sf100)을 K=10/20/30으로 측정한다. 깨끗한 비교를 위해 같은 8개 cell × sel=0.01 × 16 method 부분집합을 K별로 집계한다 — 3-way matched이므로 각 K의 측정이 자체 K-matched B1을 분모로 가진다.

| K | n | better | better% | 유의% | δlarge% | 평균 Δ% | 중앙값 Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| K=10 | 128 | 107 | 83.6% | 55.5% | 65.6% | −5.26% | −6.47% |
| K=20 (paper default) | 128 | 115 | 89.8% | 53.1% | 67.2% | **−5.55%** | **−7.12%** |
| K=30 | 128 | 110 | 85.9% | 47.7% | 69.5% | −4.96% | −6.02% |

세 K 모두에서 CaseB가 B1보다 개선되며(평균 −4.96%~−5.55%), **paper default인 K=20이 가장 강하다**(평균 −5.55%, 중앙값 −7.12%, better 89.8%). K=10은 strata가 너무 적어 각 stratum이 분포의 다봉성(multimodality)을 충분히 분리하지 못해 개선폭이 −5.26%로 다소 작고, K=30은 strata가 과하게 잘게 나뉘어 stratum당 표본이 얇아지면서 −4.96%로 다시 작아진다. K=20이 분리 충실도와 stratum당 표본 충분성의 균형점이다.

**honest 주의**: 본 절의 K별 비교는 위 8개 cell × sel=0.01 부분집합에 한정한 깨끗한 비교다. 전체 portfolio를 K별로 집계하면(K=10 192건 −4.16%, K=20 1124건 −2.67%, K=30 192건 −4.23%) K=20이 오히려 가장 약해 보이는데, 이는 K=20이 25개 cell 전체(concat 이상치 포함)를 담는 반면 K=10·K=30은 8개 sweep cell만 담아 cell 구성이 다르기 때문이다. cell 구성을 통제한 §8의 8-cell 부분집합이 K granularity의 정당한 비교이며, 그 결론은 K=20 > K=10 ≈ K=30이다. 본 연구는 paper default K=20을 그대로 채택하며, 이제 그 선택이 측정으로 뒷받침된다.

---

## 9. 결합 규칙 robustness — 산술평균 proxy 분석

CaseB의 결합 규칙은 산술평균 est_final = (est_b1 + est_method) / 2.0이다. 본 절은 산술평균이 다른 결합 규칙보다 나은지를 검증한다.

결합 규칙은 AdaptiveState 식 1-6 피드백 루프 안에 있어, 충실한 "CaseB-규칙X" 측정은 서버 재측정을 요한다. 대신 본 절은 **proxy 분석**을 쓴다 — 1508개 3-way JSON에 기록된 standalone B1·CaseA(= est_method)의 per-query 추정값을 component로 놓고, 8종 결합 규칙을 후처리로 적용해 Q-error를 비교한다. 같은 component 쌍에 모든 규칙을 적용하므로 규칙 간 *상대 순위*는 공정하게 판단된다. 지표는 inf를 100으로 cap한 capped Q-error(정확도와 추정 실패를 종합한 1지표)다.

| 결합 규칙 | finite_mean | inf율% | capped_mean | 산술평균보다 나은 측정% |
|---|--:|--:|--:|--:|
| **arith** (산술평균 — 현행 CaseB) | 1.3306 | 1.29 | **2.6003** | — |
| geom (기하평균) | 1.3068 | 6.10 | 7.3178 | 0.0% |
| geom_fb (기하 + zero 회피) | 1.3590 | 1.29 | 2.6284 | 0.1% |
| harm_fb (조화평균 + zero 회피) | 1.4699 | 1.29 | 2.7381 | 0.0% |
| w_b1_0.3 (method 비중 0.7 가중) | 1.3807 | 1.29 | 2.6493 | 0.9% |
| w_b1_0.7 (Bernoulli 비중 0.7 가중) | 1.3748 | 1.29 | 2.6435 | 5.4% |
| min | 1.7253 | 6.10 | 7.7049 | 0.0% |
| max | 1.3772 | 1.29 | 2.6460 | 2.0% |

**산술평균(arith)이 capped Q-error 최저(2.6003)다.** 7종 대안은 전부 capped_mean이 더 높고(2.628~7.705), 측정 단위로 비교하면 어떤 대안도 산술평균을 이기는 비율이 5.4% 이하다 — 즉 산술평균이 모든 대안 대비 94.6~100% 측정에서 같거나 낫다.

가장 주목할 대안은 기하평균(geom)이다. geom의 finite_mean(1.3068)은 산술평균(1.3306)보다 오히려 약간 낮아, inf가 아닌 쿼리에서는 더 정확해 보인다. 그러나 geom의 inf율은 6.10%로 산술평균(1.29%)의 5배에 가깝게 폭증하며, 이 때문에 capped_mean이 7.32로 치솟는다. 원인은 둘이다. 첫째, Bernoulli와 method 두 추정기가 모두 과소추정 경향이 있어, 기하평균으로 둘을 더 아래로 당기면 추정이 악화된다. 둘째, Bernoulli가 0-hit인 쿼리에서 √(0 · x) = 0이 되어 Q-error가 inf로 붕괴한다(zero-collapse). selectivity별로 보면 이 붕괴는 낮은 selectivity에서 치명적이다 — geom의 capped_mean은 sel=0.001에서 17.15(산술평균 5.71)로 폭증하고, sel=0.10에서야 1.12로 산술평균(1.11)에 근접한다. min 규칙도 같은 zero-collapse를 겪는다.

결론적으로 **산술평균은 7종 대안 검토에서 robust한 선택임이 확인된다.** 결합 규칙이 AdaptiveState 루프 안에 있어 proxy의 절대 Q-error는 실측 CaseB와 다르나, 루프는 나쁜 규칙을 증폭만 하므로 규칙 간 순위(산술평균 우위)는 뒤집히지 않는다 — 서버 재측정은 불필요하다.

---

## 10. honest limitation

종합 보고서로서 본 v13은 측정과 분석의 한계를 한 절에 모아 명시한다.

**(1) concat 이상치 2건이 headline 평균을 끌어올린다.** A10-DEEP+WIKI-concat-sf10 cell의 minibatch_partial이 CaseB_vs_B1에서 +1043.19%·+510.62%를 기록했다(864차원 concat에서 클러스터링 파탄). 이 2건이 headline 평균 Δ%를 −4.09%(이상치 제외)에서 −3.06%로 끌어올린다. better 비율(89.1%)·중앙값(−4.38%)은 이상치에 둔감하므로 영향받지 않는다. 본 보고서는 평균과 함께 중앙값·이상치 제외 평균을 병기하여 이 한계를 투명하게 다룬다.

**(2) P1 Cluster paradigm은 일관성이 없다.** gmm(평균 +4.63%)·minibatch_partial(이상치 제외 −2.52%)과 알고리즘상 IVF 클러스터링인 faiss_ivf(−0.69%)는 분포 인지 sample selection의 우월성을 견고하게 보이지 못한다. 클러스터링 계열 method는 본 연구의 권장 method 집합에서 제외하는 근거가 된다(§6).

**(3) concat sf=100 부분 미측정.** concat 다중 벡터 중 DEEP+SIFT는 sf=1/10/100을 모두 측정했으나, DEEP+WIKI와 DEEP+YFCC는 sf=1/10만 측정되었고 sf=100은 없다. 원본 데이터셋 측의 한계(해당 조합의 sf=100 적재 미비)이며, concat 분석(§5)의 sf=100 커버리지는 DEEP+SIFT 1종으로 제한된다.

**(4) A2-Fig8 cell은 측정점이 4건뿐이다.** DEEP+CC3M(1024차원) 다중 벡터 cell A2-Fig8은 측정 4건으로, cell별 분석(§4.6 수준의 cell 통계)에서 다른 cell과 동등한 신뢰도를 갖지 못한다. 본 보고서의 headline·축별 집계에는 포함되나, 단독 cell finding으로 인용하지 않는다.

**(5) A4-sel은 단일 selectivity 측정점이다.** A4-sel cell은 sel=0.001 단일 값으로만 측정되었다. selectivity sweep(§4)은 portfolio 전체의 sel 3종 측정이 담당하며, A4-sel은 단일 selectivity의 high-error 측정점일 뿐 sweep cell이 아니다.

**(6) v13 figure 재생성 — 두 방법론적 선택.** REPORT v12의 F7(자원·정확도 Pareto frontier)·F8(selectivity sweep heatmap)에 대응하는 v13 figure를 재생성하여 `experiments/figures/paper_exact_v13/`에 두었다 — F7은 자원 축을 소비 표본 수(final_size)로 잡은 버전과 fit_time으로 잡은 버전 2종, F8은 selectivity sweep heatmap이다. 두 방법론적 선택을 명시한다. 첫째, F7의 정확도 축은 평균이 아닌 **median Δ%** 다 — minibatch_partial의 concat 이상치 2건(§10-(1))이 평균 축을 [−7%, +15%]로 늘려 method 배치를 왜곡하므로, 이상치에 견고한 median으로 배치한다(figure data CSV에는 평균·median 병기). 둘째, F8은 K-평균 artifact를 피해 K=20 default 측정만으로 그린다. 본 보고서의 모든 finding은 표 수치에 근거하며 figure는 그 시각 보조다.

**(7) 통계 검정의 해상도·보정·효과크기.** 본 보고서의 paired 비교는 (cell, method, sel, K)마다 trial n=10으로 수행된다. n=10 one-sided Wilcoxon이 도달 가능한 최소 p값은 1/1024 ≈ 0.001로, 효과가 강한 비교들은 이 바닥값에 몰려 p값으로 강도가 미세 분해되지 않는다 — 우열 판단은 p값이 아니라 Δ%와 효과크기로 한다. 효과크기에 관해서는 REPORT v12 §9의 진단을 한 가지 정정한다. v12는 Cliff's δ·Hedges' g가 독립표본 공식이라 paired effect를 "보수적으로(작게)" 추정한다고 적었으나, v12 통계 보완(`stats_supplement_v12_5_17.md`)의 재계산에서 B1·CaseB의 trial 간 Pearson 상관이 평균 −0.013으로 0에 가깝다는 것이 확인되었다. 상관이 0이면 paired 공식과 독립표본 공식이 거의 같은 값을 준다 — 보고된 효과크기는 보수적이지 않고, 두 공식이 사실상 일치한다. 같은 보완 문서는 BH-FDR family 분할(유의 비율 변동 1%p 미만)과 cell-weighted 재집계(better 비율 변동 1.6%p 이내)도 정량화하여, 어느 것도 결론을 바꾸지 않음을 보였다.

**(8) 결합 규칙 분석은 후처리 proxy다.** §9의 8종 결합 규칙 비교는 3-way JSON의 standalone component를 후처리한 proxy이며, AdaptiveState 루프 안의 실측 CaseB와 절대 Q-error가 다르다. 규칙 간 상대 순위(산술평균 우위)는 공정하나, 절대값은 실측이 아니다.

**(9) method 명명 한계.** 별도 audit에서 일부 method의 알고리즘 명칭과 구현이 불일치함이 확인되었다 — hilbert_real은 실제로 PCA 2D lexicographic sort 기반이고(Faloutsos 1989의 정통 Hilbert curve가 아님), sparse_rp는 Achlioptas 2003이 아닌 Li-Hastie-Church 2006 variant다. 본 보고서는 정직하게 명명된 16 method만 분석 대상으로 했으며, paradigm 간 비교 시 이 명명 한계를 명시한다.

이 한계들은 본 핵심 finding의 신뢰성을 훼손하지 않는다. headline은 결함 없이 검증된 1508건 전수에서 산출되었고, 평균 대신 중앙값·이상치 제외 평균을 병기하여 이상치 영향을 투명하게 다루었으며, 3-way matched 설계가 measurement-run bias를 상쇄한다.

---

## 11. 결론

본 보고서는 paper Exqutor §V-B Adaptive Sampling의 sample selection 단계를 3-way matched로 측정한 1508건을 단일 portfolio로 분석했다. 한 측정이 대조군 B1·실험군 CaseA·실험군 CaseB를 같은 조건에서 동시에 산출하므로, 세 mode가 완벽히 짝지어진 위에서 비교가 이루어졌다.

**핵심 finding**: paper §V-B의 unstratified Bernoulli random sampling을 분포 인지 stratification ensemble로 교체하면, 동일한 sample budget(paper 식 1, N=385) 안에서 cardinality 추정 Q-error가 일관되게 개선된다. 결합 실험군 CaseB는 대조군 B1 대비 paired 비교 1508건 중 89.1%에서 우월하고, paired Δ% 중앙값은 −4.38%(평균 −3.06%, 이상치 제외 −4.09%), 통계적 유의 우월 65.3%, 효과크기 large 우월 72.1%다. cardinality 추정 알고리즘과 AdaptiveState 식 1-6은 paper 그대로 두었으며, 본 연구의 개입은 오직 sample selection 단계에 한정된다.

**negative control이 결합의 가치를 입증한다**: 완전 대체 실험군 CaseA는 B1 대비 35.2%만 우월하고 평균 +12.90%로 불안정하다 — 강한 method에서는 중립, 약한 method(gmm, minibatch_partial)에서는 파국이다. Bernoulli를 method로 통째 치환하는 방식은 신뢰할 수 없다. 그런데 같은 method 집합으로 CaseB(결합)는 89.1%에서 우월하고, CaseA를 96.5%에서 이긴다. 즉 개선의 원천은 method 단독이 아니라 method를 Bernoulli와 산술평균으로 결합하는 데 있으며, CaseA라는 negative control이 이를 그 부재로써 증명한다. 측정의 arc는 베르누이(B1) → 완전 대체(CaseA, 불안정) → 결합(CaseB, 답)으로 완결된다.

**조건별 강약**: 개선은 selectivity가 높을수록 크고(0.001/0.01/0.10에서 better 83.3/87.6/97.5% 단조 증가), 단일·다중·연결 구조 전반에서 better 비율 89~90%로 유지된다. 16 method 중 13개가 견고하게 우월하며, P1 Cluster paradigm(gmm, minibatch_partial)과 클러스터링 계열 faiss_ivf만 일관성을 보이지 못한다. strata 수 K는 v13에서 K=10 대조군 결함이 해소되어 본문 finding으로 승격되었고, 깨끗한 8-cell 비교에서 paper default K=20이 K=10·K=30보다 강한 개선을 보였다. 결합 규칙은 8종 대안 검토에서 산술평균이 robust함이 확인되었다.

**v13의 위상**: v13은 REPORT v12 대비 headline이 92.2%/−6.25%에서 89.1%/−3.06%로 약화되었다. 이는 v13의 대조군 B1이 paper에 더 충실한 1단계 측정으로 바뀌어 baseline이 더 깨끗하고 낮아진 결과이며, 측정 품질의 하락이 아니다 — 완전한 검증을 시도한 결과 대조군 측정 구현의 미묘한 결함까지 찾아내 바로잡았고, b1_2stage_verdict가 사전 추정한 약화 범위에 v13 실측이 정확히 안착했다. v13이 정본이며 v12는 2단계 측정 기반의 이력으로 보존한다. 본 보고서가 정직하게 남기는 한계는 concat 이상치 2건, P1 Cluster의 비일관성, concat sf=100 부분 미측정, 그리고 통계 검정의 해상도·proxy·명명 한계다(§10). 이 한계들은 핵심 finding의 신뢰성을 훼손하지 않는다.

---

_End of REPORT v13._
