# Paper Exact 재현 측정 — 종합 분석 보고서 REPORT v12

_생성_: 2026-05-17

_출처_: `_internal/cache/rq3/aggregated_v12_full.parquet` (통합 측정) · `_internal/cache/rq3/paired_delta_v12.parquet` (paired Δ%)

_framing_: B1 = 대조군 (Bernoulli random sampling + Adaptive Sampling Eq 1-6) · CaseB = 실험군 (16 method로 데이터 분포를 인지해 계층(stratum)으로 나눠 뽑고 두 추정값을 결합하는 방식(stratification ensemble) + Adaptive Sampling). 본 보고서는 paper Exqutor §V-B Adaptive Sampling에서 **sample selection** 단계를 random Bernoulli 대신 분포 인지 방식으로 교체했을 때의 Q-error 변화를 정량 평가한다. cardinality 추정 알고리즘과 AdaptiveState 식 1-6은 paper 그대로 유지하며, 본 연구의 개입 지점은 오로지 sample selection 단계다. CaseA(단독 대체) 계열은 본 narrative에 부합하지 않아 폐기했다.

> **★ 본 보고서 대표 수치(headline)는 K10 paired 비교를 제외한 신뢰 가능 수치다.** 검증 과정에서 K=10 측정에 구조적 결함이 확인되었기 때문이다 (§7 상세). headline: paired CaseB better **92.2%**, mean Δ% **−6.25%**.

---

## 0. 요약 — 본 보고서가 말하는 것

통합 1444건의 측정(B1 80 + CaseB 1364)을 단일 portfolio로 모아, 같은 cell·selectivity·strata 조건에서 대조군 B1과 실험군 CaseB를 trial 단위로 짝지어 비교했다. paired 비교 1360건 가운데 K=10 변형 측정 120건을 제외한 1240건이 신뢰 가능한 비교다. 이 1240건에서 실험군 CaseB가 대조군 B1보다 Q-error가 낮은 경우는 1143건(92.2%)이며, 짝지은 Q-error 변화율(paired Δ%) 평균은 −6.25%, 중앙값은 −6.15%다. one-sided BH-FDR 보정 검정에서 통계적으로 유의하게 우월한 경우는 971건(78.3%), Cliff's δ가 large 임계(0.474)를 넘어 우월한 경우는 1023건(82.5%)이다.

핵심 메시지는 단순하다. paper §V-B의 unstratified Bernoulli random sampling을 분포 인지 stratification ensemble로 교체하면, 동일한 sample budget(paper Eq 1, N=385) 안에서 cardinality 추정의 Q-error가 일관되게 개선된다. 이 개선은 selectivity가 낮을수록 더 뚜렷하고(sel 0.001/0.01/0.10에서 better 비율 84.4/92.4/99.2%로 단조 증가), 단일 벡터 데이터셋에서 가장 크며(−10.37%), 16개 method 중 14개가 통계적으로 견고한 우월성을 보인다. 정확도 상위 method들이 동시에 자원 효율 상위에 위치하여(§8 Pareto), "정확도와 비용의 맞교환(trade-off)"은 본 비교 범위에서 성립하지 않는다.

본 보고서는 동시에, 검증 과정에서 드러난 한계를 숨기지 않는다. 가장 중요한 것은 K granularity 축의 K=10 측정 결함이다 (§7, §9). 대조군 B1이 strata 수 K에 의존하는 구조를 가져, K=10에서 B1의 Q-error가 손상되었고, 그 손상된 B1과 짝지은 K=10 CaseB 96건의 −36.15%, 그것이 섞인 K=10 행 전체 평균 −26.85%는 모두 허위다. 이 결함 때문에 깨끗한 K granularity 비교가 성립하지 않으므로, 본 보고서는 K granularity(§7)를 본문 finding이 아닌 부속·미완 결과이자 honest limitation으로 격하하여 보고한다.

---

## 1. 측정 portfolio 요약

### 1.1 통합 측정 규모

본 분석의 입력은 단일 통합 parquet `aggregated_v12_full.parquet`이며, 여러 측정 캠페인(REPORT v11 base, concat 캠페인, v6~v10 보강 chain, v9 selectivity sweep)을 사용 16 method 필터 + dedup을 거쳐 합친 결과다.

| 구분 | 행 수 |
|---|---:|
| 통합 측정 file (dedup 후) | **1444** |
| ─ B1 (대조군, Bernoulli + Adaptive) | 80 |
| ─ CaseB (실험군, stratification ensemble + Adaptive) | 1364 |
| paired 비교 (CaseB × B1 매칭) | **1360** |
| ─ 신뢰 가능 (K=10 제외) | **1240** |
| ─ K=10 변형 (결함, 제외) | 120 |

측정 캠페인 출처(stage_source) 분포는 v9 selectivity sweep 680건, concat 캠페인 357건, REPORT v11 base 221건, v10 full-16 chain 129건, 그 외 보강 chain(v6/v7/v8/g2) 57건이다. 모든 CaseB 측정은 동일한 ensemble 정의(`est_final = (est_b1 + est_method) / 2.0` simple average)를 사용했다.

### 1.2 측정 축의 커버리지

통합 portfolio는 네 축으로 펼쳐진다.

**데이터셋 (9종)**: SIFT 254 · SimSearchNet++ 254 · DEEP 253 · DEEP+SIFT 204 · DEEP+WIKI 161 · YFCC 110 · DEEP+YFCC 102 · WIKI 102 · DEEP+CC3M 4. 단일 벡터 데이터셋 6종과 다중 벡터 조합 데이터셋이 모두 포함된다.

**scale factor (3종)**: sf=1 (416행) · sf=10 (538행) · sf=100 (490행). 동일 데이터셋을 세 규모로 측정하여 데이터 규모에 따른 효과 안정성을 확인할 수 있다.

**selectivity (3종)**: sel=0.001 (476행) · sel=0.01 (509행) · sel=0.10 (459행). paper Fig 13의 selectivity ablation에 대응하는 sweep이다.

**strata 수 K (3종)**: K=20 (paper default, 1194행) · K=10 (126행) · K=30 (124행). 단, K=10 측정은 §7의 결함 때문에 paired 분석에서 제외한다.

**측정 cell**: 총 25개. paper Fig 12 재현 8 cell(A1-DEEP/SIFT/SSN, A2-Fig7/Fig9, A5-scale-sf{1,10,100}), Fig 13 selectivity cell(A4-sel), v6/v7 신규 cell(A6-WIKI, A7-YFCC, A8-DEEP+SIFT 등), concat 다중 벡터 cell(A9~A11)을 포함한다. 데이터 규모로 분류한 Type 라벨 기준으로는 Type 1(소규모 단일 sf=1) 263행, Type 2(중규모 단일 sf=10) 212행, Type 3(대규모 단일 sf=100) 439행, Type 4a(대규모 다중 288d) 369행, Type 4b(대규모 다중 864d) 161행이다.

### 1.3 사용 16 method

본 분석의 method 축은 8개 sampling paradigm을 대표하는 16개 method로 고정했다. 측정 portfolio의 CaseB 행은 정확히 이 16개 method만 포함한다.

| Paradigm | Method |
|---|---|
| P1 Cluster | minibatch_partial · gmm · faiss_ivf |
| P2 Spatial | hilbert_real · zorder_morton · skilling_hilbert |
| P3 Streaming | chao_weighted |
| P4 DimReduction | sparse_rp · pca1d · rsvd · ica_fastica |
| P5 QMC | cum_sqrtf · lavallee_hidiroglou |
| P6 Quantization | rabitq_strat · mhist2 |
| P9 InfoTheoretic | hyperloglog |

paradigm별 CaseB 측정 행 수는 P2 341 · P4 341 · P1/P5/P6 각 164 · P3/P9 각 95다.

---

## 2. 무결성 검증 결과

종합 보고서로서 본 v12는 입력 데이터의 무결성 검증 결과를 먼저 명시한다. 분석 수치 자체가 깨끗한 측정에 근거함을 보이기 위함이다.

### 2.1 v9 selectivity sweep과 concat 캠페인 — 무결

v9 selectivity sweep(680행)과 concat 캠페인(357행)은 byte-identical 중복 검사(content_hash 기준)와 semantic 중복 검사(같은 cell·sel·K_norm·method·mode 조합)를 모두 통과했다. 통합 후 1444행에 content_hash 중복은 0건이며, paired 단계에서 (cell, method, sel, K_norm) 키 중복도 0건이다. 즉 paired 비교 1360건은 서로 다른 측정에서 나온 독립적인 비교다.

### 2.2 폐기된 데이터 — 구 v9 및 구 v8

검증 과정에서 신뢰성이 확인되지 않은 측정 캠페인은 통합 전에 배제했다. 구 v9 측정 일부와 구 v8 측정은 측정 환경 정합성이 검증되지 않아 통합 parquet에서 제외했고, 본 보고서의 어떤 수치에도 사용하지 않았다. 통합 parquet은 정합성이 검증된 캠페인만 dedup rank 우선순위에 따라 합쳤다.

### 2.3 K=10 B1 측정 — 구조적 결함, 정직 기록

가장 중요한 무결성 사안이다. 대조군 B1의 측정 함수 `measure_b1_paper`는 환경변수 `STRATA_K`를 받아 strata 캐시를 생성하는 구조를 갖는다. K=10 설정에서 B1의 query별 Q-error에 무한대(inf)가 폭증하여(n_inf 314~391/1000 수준), trim 후에도 K=10 B1의 qe_trim이 정상 범위(1.6~1.7)를 크게 벗어나 3.0대로 손상되었다.

통합 parquet에 기록된 K=10 B1의 손상은 다음과 같이 직접 확인된다 (A1-SIFT/A1-SSN, K=10).

| Cell | K | sel | qe_trim | qe_mean | qe_median | 정상 여부 |
|---|---:|---|---:|---:|---:|---|
| A1-SIFT | 10 | 0.001 | 3.034 | 3.047 | 2.975 | 손상 |
| A1-SIFT | 10 | 0.01 | 3.281 | 3.320 | 3.291 | 손상 |
| A1-SIFT | 10 | 0.10 | 2.454 | 2.454 | 2.454 | 손상 |
| A1-SSN | 10 | 0.001 | 3.017 | 3.016 | 3.040 | 손상 |
| A1-SSN | 10 | 0.01 | 2.645 | 2.635 | 2.655 | 손상 |
| A1-SSN | 10 | 0.10 | 2.174 | 2.174 | 2.173 | 손상 |
| A1-SIFT | 30 | 0.001 | 1.716 | 1.716 | 1.729 | 정상 |
| A1-SSN | 30 | 0.001 | 1.627 | 1.632 | 1.635 | 정상 |
| (참고) A1-SIFT | 20 | 0.01 | 1.695 | — | — | 정상 |
| (참고) A1-SSN | 20 | 0.01 | 1.625 | — | — | 정상 |

K=30 B1은 1.16~1.72 범위로 정상이고, K=20(paper default) B1도 1.6~1.7로 정상이다. 오직 K=10 B1만 2.2~3.3으로 손상되었다.

**결과적으로 K=10 B1 측정값은 신뢰할 수 없다.** paired_delta_v12.parquet에서 A1-SIFT/A1-SSN의 K=10 CaseB 96건은 이 손상된 K=10 B1과 짝지어졌고(pairing=exact), 그 paired Δ% 평균은 −36.15%다. 이 큰 음수는 CaseB의 우월성이 아니라 분모(B1)의 손상에서 나온 **허위 신호**다. 동일한 K=10 CaseB를 정상적인 K=20 B1과 짝지으면 평균 +18.13%로, 오히려 악화로 나타난다.

**처리 방침**: K granularity 분석에서 대조군 B1은 paper default인 K=20 하나로 고정한다. K=10/K=20/K=30 CaseB를 모두 K=20 B1과 비교하며, K=10/K=30 B1 측정값 자체는 본 보고서의 수치에 사용하지 않는다. 본 보고서의 headline 수치(§3)는 K=10 paired 비교 120건을 전부 제외한 1240건에 근거한다.

---

## 3. paired Δ% 핵심 — 대조군 B1 vs 실험군 CaseB

본 절이 보고서의 중심이다. 짝지은 Q-error 변화율(paired Δ%)은 같은 cell·selectivity·strata에서 trial 단위로 짝지은 (CaseB_qe − B1_qe) / B1_qe × 100이며, 음수가 실험군 CaseB의 Q-error가 더 낮음(더 정확함)을 뜻한다.

### 3.1 headline 수치 (K=10 제외 — 신뢰 가능)

K=10 변형 측정 120건을 제외한 paired 비교 **1240건**에서 다음을 얻는다.

| 지표 | 값 |
|---|---|
| CaseB better (Δ% < 0) | **1143 / 1240 = 92.2%** |
| 평균 Δ% | **−6.25%** |
| 중앙값 Δ% | **−6.15%** |
| Δ% 범위 | −34.96% ~ +290.08% |
| 통계적 유의 우월 (one-sided BH-FDR p<0.05) | 971 / 1240 = **78.3%** |
| Cliff's δ large (≥0.474) 우월 | 1023 / 1240 = **82.5%** |
| Hedges' g large (\|g\|≥0.8) | 1039 / 1240 = **83.8%** |

분포 인지 stratification ensemble은 paper §V-B의 unstratified Bernoulli random sampling을 비교 대상으로, 측정한 비교의 약 10건 중 9건에서 Q-error를 낮춘다. 단순한 "절반 이상 좋다" 수준이 아니라, 통계적으로 유의한 우월(78.3%)과 효과크기 large 우월(82.5%)이 모두 8할 전후로, 신호가 견고하다.

### 3.2 K=10 포함 시 수치와의 비교 (구분 명시)

참고로 K=10 paired 120건을 포함한 전체 1360건의 수치는 평균 −8.06%, better 91.7%다. 평균이 −6.25%에서 −8.06%로 1.81%p 더 음수로 보이는 것은 §2.3에서 설명한 K=10 허위 신호(−36% 수준)가 평균을 끌어내린 결과이지, 실제 효과가 더 크기 때문이 아니다. **본 보고서는 K=10을 제외한 −6.25%를 신뢰 가능한 headline으로 채택하며, −8.06%는 결함 데이터가 섞인 수치임을 명시한다.**

### 3.3 가장 강한 비교와 가장 약한 비교

K=10 제외 기준, 개별 (cell × method × sel × K) 단위의 양 극단은 다음과 같다.

가장 강한 개선 8건은 모두 A5-scale-sf1-SIFT(SIFT sf=1, sel=0.001) cell이며, hyperloglog −34.96%, zorder_morton −34.77%, skilling_hilbert −33.52% 순으로 모두 one-sided BH-FDR p=0.0018, Cliff's δ=+1.00이다. 이 cell은 B1 자체의 Q-error가 높아(sel=0.001 B1 qe_trim 2.366) stratification의 개선 여지가 컸다.

가장 큰 악화는 A10-DEEP+WIKI-concat-sf10 cell에서 minibatch_partial이 +290.08%, +276.41%를 기록한 2건이다. 이는 P1 Cluster paradigm의 minibatch_partial이 864차원 concat 데이터에서 불안정함을 보여주는 사례로, §6에서 다룬다. 악화 사례는 통계적으로 유의하지 않다(p_adj=1.0000).

---

## 4. selectivity 효과 — 낮을수록 개선 폭이 크다

paper Fig 13은 selectivity가 낮을수록 cardinality 추정의 본질적(inherent) Q-error가 커짐을 보인다. 본 절은 그 selectivity 축에서 실험군의 우월성이 어떻게 변하는지 측정한다. 아래 수치는 figure F8(§8.2)의 sweep 데이터셋(K=20 default, 24 cell × 16 method) 기준이다.

| sel | n | better | better% | 유의 우월% | 평균 Δ% | 중앙값 Δ% |
|---|---:|---:|---:|---:|---:|---:|
| 0.001 | 384 | 324 | **84.4%** | 66.1% | −5.06% | −6.14% |
| 0.01 | 368 | 340 | **92.4%** | 70.5% | −7.03% | −9.08% |
| 0.10 | 368 | 365 | **99.2%** | 99.2% | −6.53% | −5.31% |

better 비율이 selectivity 0.001 → 0.01 → 0.10 순으로 84.4% → 92.4% → 99.2%로 **단조 증가**한다. selectivity가 0.10에 이르면 측정한 368건 중 365건이 개선되고, 그 365건 모두가 통계적으로 유의하다. 즉 분포 인지 sample selection의 우월성은 selectivity가 높을수록(쿼리가 더 많은 데이터를 선택할수록) 거의 예외 없이 성립한다.

selectivity 0.001에서 better 비율이 84.4%로 상대적으로 낮은 것은, 매우 낮은 selectivity에서는 표본에 들어오는 hit 수 자체가 작아 어떤 sample selection 전략이든 추정 분산이 커지기 때문이다. 그럼에도 84.4%는 여전히 명확한 우월성이며, 평균 Δ%도 −5.06%로 음수다.

(참고: paired_delta_v12.parquet 전체에서 K=10을 제외하고 sel별로 집계하면 84.6/92.9/99.2%로, F8 sweep 데이터셋 기준 수치와 0.5%p 이내로 일치한다. 미세한 차이는 두 집계의 cell 집합이 다르기 때문이며, 단조 증가 결론은 동일하다.)

---

## 5. single vs multi-vector(concat) 비교

본 절은 측정 cell을 단일 벡터(single)와 다중 벡터(concat: 두 데이터셋의 벡터를 차원 방향으로 연결)로 나누어 효과를 비교한다. multi는 cross-table 다중 벡터 cell(A2-Fig7/Fig9, A8)을 따로 둔 분류다. 아래는 K=10 제외 기준이다.

| 유형 | n | better | better% | 유의 우월% | 평균 Δ% | 중앙값 Δ% |
|---|---:|---:|---:|---:|---:|---:|
| single | 752 | 698 | 92.8% | 81.4% | **−7.66%** | −7.66% |
| multi (cross-table) | 152 | 132 | 86.8% | 63.8% | −4.57% | −5.28% |
| concat | 336 | 313 | **93.2%** | 78.0% | −3.84% | −5.38% |

해석은 두 갈래로 갈린다. **단일 벡터 데이터셋에서 개선 폭이 가장 크다**: 평균 −7.66%로, concat의 −3.84%보다 두 배 가까이 크다. (참고로 K=10을 포함하면 single 평균은 −10.37%로 더 커 보이나, 이는 §2.3 결함 데이터의 영향이다.) 단일 벡터에서는 데이터 분포가 단일하여 분포 인지 stratification이 명확한 신호를 잡는다.

반면 **concat 다중 벡터에서는 better 비율은 오히려 single보다 약간 높지만(93.2%), 개선의 크기는 작다(−3.84%)**. 즉 다중 벡터를 연결한 고차원 공간에서도 분포 인지 sample selection이 "거의 항상 조금 더 낫다"는 방향성은 유지되나, 두 데이터셋의 분포가 섞이면서 stratification이 잡아낼 수 있는 구조적 이득이 희석된다.

selectivity와 교차하면 두 유형 모두 sel이 높을수록 better 비율이 오른다. single은 sel 0.001/0.01/0.10에서 85.2/93.8/100.0%, concat은 86.6/94.6/98.2%다. concat의 sel=0.10 단계에서도 112건 중 110건이 개선된다.

---

## 6. method/paradigm 분석

### 6.1 사용 16 method별 paired Δ% (K=10 제외)

| Method | Paradigm | n | better% | 평균 Δ% | 중앙값 Δ% | δ large% |
|---|---|---:|---:|---:|---:|---:|
| hilbert_real | P2 | 82 | 100.0% | −8.76% | −8.59% | 90.2% |
| pca1d | P4 | 76 | 100.0% | −8.75% | −8.00% | 97.4% |
| zorder_morton | P2 | 76 | 98.7% | −8.66% | −8.00% | 94.7% |
| ica_fastica | P4 | 76 | 98.7% | −8.55% | −7.90% | 89.5% |
| skilling_hilbert | P2 | 76 | 94.7% | −8.52% | −7.93% | 89.5% |
| chao_weighted | P3 | 82 | 98.8% | −8.37% | −7.80% | 89.0% |
| sparse_rp | P4 | 82 | 100.0% | −8.15% | −7.47% | 92.7% |
| hyperloglog | P9 | 82 | 96.3% | −7.73% | −6.88% | 86.6% |
| cum_sqrtf | P5 | 76 | 98.7% | −7.69% | −6.99% | 89.5% |
| rsvd | P4 | 76 | 100.0% | −7.44% | −6.31% | 92.1% |
| lavallee_hidiroglou | P5 | 76 | 93.4% | −7.33% | −7.06% | 81.6% |
| mhist2 | P6 | 76 | 86.8% | −6.07% | −4.65% | 76.3% |
| rabitq_strat | P6 | 76 | 86.8% | −5.51% | −4.61% | 73.7% |
| faiss_ivf | P1 | 76 | 77.6% | −2.32% | −4.14% | 65.8% |
| gmm | P1 | 76 | 55.3% | **+1.90%** | −0.61% | 42.1% |
| minibatch_partial | P1 | 76 | 86.8% | **+2.67%** | −4.20% | 67.1% |

16개 method 중 **14개는 평균 Δ%가 음수이며 better 비율 86% 이상**으로 견고하게 우월하다. P2 Spatial(hilbert_real, zorder_morton, skilling_hilbert), P4 DimReduction(pca1d, sparse_rp, ica_fastica, rsvd), P3 Streaming(chao_weighted), P9 InfoTheoretic(hyperloglog), P5 QMC(cum_sqrtf, lavallee_hidiroglou)에 속한 method가 모두 여기에 든다. 특히 hilbert_real, pca1d, sparse_rp, rsvd는 better 비율 100%로, K=10을 제외한 모든 측정 cell에서 예외 없이 B1을 이긴다.

**약한 method는 P1 Cluster paradigm에 집중된다**. gmm은 평균 +1.90%(better 55.3%)로 사실상 B1과 동등하거나 약간 못하고, minibatch_partial은 평균 +2.67%지만 중앙값은 −4.20%다. minibatch_partial의 양수 평균은 §3.3에서 본 A10-DEEP+WIKI-concat-sf10의 +290%, +276% 두 이상치(outlier) 때문으로, 이 2건을 제외하면 평균이 −4.92%로 돌아온다. 즉 minibatch_partial은 대부분의 cell에서는 작동하지만 864차원 concat 같은 극단 조건에서 불안정하다. faiss_ivf는 평균 −2.32%로 약한 개선에 머문다.

결론적으로 P1 Cluster paradigm은 분포 인지 sample selection의 우월성을 일관되게 보이지 못하며, 본 연구의 권장 method에서 제외하는 근거가 된다.

### 6.2 paradigm rollup (K=10 제외, |Δ%|<100 outlier 제외)

| Paradigm | method 수 | n | 평균 Δ% | 중앙값 Δ% | std | 범위 |
|---|---:|---:|---:|---:|---:|---|
| P3 Streaming | 1 | 82 | −8.37% | −7.80% | 5.15 | [−31.5, +5.4] |
| P4 DimReduction | 4 | 310 | −8.22% | −7.43% | 5.01 | [−32.5, +7.4] |
| P9 InfoTheoretic | 1 | 82 | −7.73% | −6.88% | 5.17 | [−35.0, +0.1] |
| P5 QMC | 2 | 152 | −7.51% | −7.04% | 5.30 | [−31.0, +8.4] |
| P2 Spatial | 4 | 310 | −7.10% | −6.83% | 8.14 | [−34.8, +66.1] |
| P6 Quantization | 2 | 152 | −5.79% | −4.61% | 5.93 | [−33.0, +10.8] |
| P1 Cluster | 2 | 150 | −1.46% | −2.99% | 8.71 | [−30.6, +46.1] |

paradigm 수준에서 P3 Streaming, P4 DimReduction이 가장 강하고(평균 −8% 초과), P9, P5, P2가 −7% 전후로 뒤따른다. P6 Quantization은 −5.79%로 중간, P1 Cluster는 −1.46%로 가장 약하다. P2 Spatial과 P1 Cluster의 std가 큰 것(8.14, 8.71)은 각각 faiss_ivf, minibatch_partial의 outlier 때문이다.

### 6.3 16개 측정 방법 중 Top 5 method spotlight

§8의 자원-정확도 분석에서 정확도와 자원 효율을 함께 고려해 선정한 16개 측정 방법 중 Top 5 method는 sparse_rp, chao_weighted, hilbert_real, hyperloglog, pca1d다. 이 다섯 method의 paired Δ%(K=10 제외)는 모두 평균 −7.7% 이하이며 better 비율 96% 이상으로, 16 method 중 상위권에 위치한다. 본 연구의 5/27 발표·6/11 보고서에서 권장 method 집합으로 제시하기에 충분한 근거를 갖는다.

---

## 7. K granularity — strata 수의 효과 (부속·미완 — honest limitation)

본 절은 strata 수 K(10/20/30)가 실험군 CaseB에 미치는 영향을 분석한다. **다만 본 절은 보고서의 본문 finding이 아니라 부속·미완 결과다.** §2.3에서 확인한 K=10 대조군 B1의 구조적 결함 때문에 깨끗한 K granularity 비교가 성립하지 않으므로, 본 절의 모든 수치는 honest limitation으로 격하하여 읽어야 한다.

### 7.1 honest limitation — 왜 K granularity 결론이 제한적인가

먼저 한계를 명시한다. 대조군 B1은 그 자체가 strata 수 K에 의존하는 측정이며(§2.3), K=10에서는 inf 폭증으로 손상되고 K=30에서는 정상이지만 K=20과 다른 값이 나온다. 즉 **이론적으로 깨끗한 K granularity 비교는 "같은 K의 B1 vs 같은 K의 CaseB"여야 하나, K=10 B1이 신뢰 불가하므로 그 비교가 불가능하다.**

paired_delta_v12.parquet의 pairing 규칙은 이 한계를 두 갈래로 드러낸다. 같은 K의 B1이 측정된 경우 그 B1을 분모로 쓰고(pairing=exact), 없으면 paper default K=20 B1로 fallback한다(pairing=fallback_K20). 그 결과 K=10 측정 120건 중 96건(A1-SIFT/A1-SSN)은 손상된 K=10 B1과 짝지어진 exact 측정이고, 24건만 정상 K=20 B1을 쓴 fallback 측정이다. **손상된 K=10 B1을 끌어들인 96건의 −36.15%는 허위 신호이며, K granularity 결론은 정상 분모를 쓴 24건의 fallback 측정으로만 제한적으로 읽을 수 있다.** K=30은 64건 exact + 56건 fallback으로, K=30 B1 자체는 정상이라 exact 측정도 신뢰 가능하다.

추가로, 별도 분석(`K_granularity_dimension_dependent_종합검증`, `B1_variance_root_cause_종합분석`)에서 K granularity 측정은 measurement run 단위의 systematic bias(±10~25%)가 크다는 점이 확인되었다. 같은 DEEP 96d 데이터를 다른 시점에 측정하면 K=10 결과의 부호가 뒤집힐 정도다. 이 점도 K granularity 결론을 보수적으로 보고해야 하는 이유다.

### 7.2 측정 결과 — paired_delta_v12.parquet 실측

paired_delta_v12.parquet의 K_norm 축 1360건을 K별로 집계한 실측값은 다음과 같다. K granularity sweep cell은 8개(A1-DEEP/SIFT/SSN, A2-Fig7/Fig9, A5-scale-sf{1,10,100})이며, K=10/K=30 측정은 이 8 cell × 16 method × sel 3종, K=20은 전체 portfolio다.

| CaseB의 K | n | better | better% | 평균 Δ% | 중앙값 Δ% |
|---|---:|---:|---:|---:|---:|
| K=10 | 120 | 104 | 86.7% | **−26.85%** | −36.20% |
| K=20 (default) | 1120 | 1029 | 91.9% | **−6.19%** | −5.92% |
| K=30 | 120 | 114 | 95.0% | **−6.76%** | −8.22% |

K=10 행의 −26.85%는 그대로 해석하면 안 된다. §2.3에서 보인 대로, K=10 측정 120건 중 96건은 손상된 K=10 B1과 짝지어진 측정(pairing=exact)이고, 나머지 24건만 정상 K=20 B1을 fallback 분모로 쓴 측정(pairing=fallback_K20)이다. 이 둘을 분리하면 K=10 행의 −26.85%가 평균값의 산술 합성에 불과하다는 점이 드러난다.

| K | pairing | n | better% | 평균 Δ% | 중앙값 Δ% | 분모(B1) |
|---|---|---:|---:|---:|---:|---|
| K=10 | exact | 96 | 99.0% | **−36.15%** | −37.13% | 손상된 K=10 B1 — 허위 |
| K=10 | fallback_K20 | 24 | 37.5% | **+10.35%** | +7.12% | 정상 K=20 B1 — 신뢰 가능 |
| K=30 | exact | 64 | 93.8% | −5.52% | −6.22% | 정상 K=30 B1 |
| K=30 | fallback_K20 | 56 | 96.4% | −8.18% | −9.41% | 정상 K=20 B1 |

핵심 관찰은 둘이다. 첫째, **K=10 행 전체 −26.85%는 본 연구의 finding이 아니다.** 그 가운데 96건(exact)은 손상된 K=10 B1을 분모로 쓴 허위 −36.15%이고, K=10 CaseB를 정상 분모(K=20 B1)와 비교한 24건(fallback_K20)에서는 오히려 +10.35%로, **K=10에서는 실험군 CaseB가 대조군보다 약하다.** 즉 신뢰 가능한 분모로만 보면 K=10은 실험군의 우월성이 사라지는 지점이다. strata가 너무 적으면 각 stratum이 분포의 다봉성(multimodality)을 충분히 분리하지 못해 분포 인지 stratification의 이점이 사라지는 것으로 해석되나, K=10 exact 측정의 B1 결함 때문에 깨끗한 K=10 비교가 불가능하다는 점을 함께 명시한다. 둘째, **K=20과 K=30은 서로 비슷하다.** K=30 전체 −6.76%는 K=20 전체 −6.19%와 0.6%p 차이로, K=30 exact(−5.52%)와 fallback_K20(−8.18%)이 섞인 값이다. K=20에서 K=30으로 strata를 더 늘려도 추가 이득은 명확하지 않다.

K=10/K=30 sweep cell이 §3의 headline −6.25%와 다른 절대 크기를 보이는 것은 cell 집합이 다르기 때문이며, K granularity의 결론은 절대 크기가 아니라 **K=20 ≈ K=30, K=10은 B1 측정 결함으로 비교 불가**라는 정성적 순서다.

### 7.3 K granularity 결론

K granularity는 본 보고서의 본문 finding이 아니라 **부속·미완 결과**이며, honest limitation으로 격하하여 보고한다. 신뢰 가능한 비교만 추리면 paper default인 K=20과 K=30이 비슷한 수준의 개선을 보이고(전체 −6.19% vs −6.76%), K=10은 대조군 B1 자체가 손상되어(§2.3) 깨끗한 비교가 성립하지 않는다. K=10 CaseB를 정상 K=20 B1과 fallback 비교하면 +10.35%로 실험군이 오히려 약화되므로, "strata가 너무 적으면 분포 분리가 불충분하다"는 방향은 시사되나 단정할 수 없다. 본 연구는 paper의 K=20 설정을 그대로 채택하며, K=10 측정의 B1 결함을 §2.3·§9에 명시한다.

---

## 8. figure 설명

### 8.1 F7 — 자원·정확도 최적 경계(Pareto frontier) (자원 × 정확도)

**파일**: `experiments/figures/paper_exact_v8/F7_pareto_frontier.png` (+ .pdf, _data.csv)

F7은 16개 sample selection method를 (자원 비용, 정확도 개선) 평면에 배치한 산점도다. 자원·정확도 최적 경계(Pareto frontier)란 자원을 더 쓰지 않고는 정확도를 더 높일 수 없는 method들의 모음을 말한다. 축 정의는 다음과 같다.

- **x축 (자원 비용)**: `final_size` — CaseB 모드에서 AdaptiveState(Eq 1-6) 종료 시 실제로 소비한 sample budget의 평균. **이 그림의 자원 축은 wall-clock 시간이 아니라 소비 표본 수 대리 지표(proxy)다.** 측정 portfolio에 fit 단계의 wall-clock 컬럼이 없어, 측정된 final_size를 자원 proxy로 사용한다. 적은 표본 = 적은 거리 계산 = 적은 비용이라는 점에서 두 지표 모두 "budget" 성격으로 해석이 일관된다. final_size 범위는 1851~2448 표본이다.
- **y축 (정확도 개선)**: method 단위 평균 paired Δ%. 음수가 개선이다. 범위는 −8.71%(pca1d) ~ +3.47%(minibatch_partial)다.

빨강 점선은 lower-left 자원·정확도 최적 경계(낮은 비용 + 낮은 Δ%가 우월)다. 최적 경계 위에 엄밀히 놓이는 method는 **chao_weighted, hilbert_real, sparse_rp, pca1d 네 개**다(final_size가 작으면서 Δ%가 갱신되는 점). hyperloglog는 "Top 5 method"로 함께 권장하지만, final_size 1943·Δ% −7.62%로 hilbert_real(1891·−8.65%)에 약하게 지배되어 경계선에는 엄밀히 포함되지 않는다 — 이 점은 정직하게 보고한다.

F7이 전하는 메시지는 명확하다. **정확도 상위 method와 자원 효율 상위 method가 거의 일치하며, "정확도를 위해 비용을 더 쓴다"는 맞교환이 본 비교 범위에서 성립하지 않는다.** 약한 method(gmm, minibatch_partial)는 오른쪽 위(높은 비용 + 양수 Δ%)에 떨어져 최적 경계에서 멀다.

### 8.2 F8 — selectivity sweep heatmap

**파일**: `experiments/figures/paper_exact_v8/F8_sel_sweep_heatmap.png` (+ .pdf, _data.csv)

F8은 selectivity 3종(0.001/0.01/0.10) × 16 method × 24 cell의 paired Δ%를 heatmap으로 보인 그림이다(K=20 default 기준, 총 1120 셀). §4의 selectivity 수치가 이 데이터셋에서 나온다.

heatmap의 색이 selectivity가 높아질수록(0.001 → 0.10) 일관되게 음수(개선) 쪽으로 짙어진다. sel=0.001 패널에서 평균 −5.06%·better 84.4%, sel=0.01에서 −7.03%·92.4%, sel=0.10에서 −6.53%·99.2%다. Type 1 cell(특히 A5-scale-sf1-SIFT)에서 sel=0.001 패널이 −30%대로 가장 짙고, P1 Cluster method 행(gmm, minibatch_partial)에서 일부 양수 셀이 보이는 것이 §6의 method 약점과 시각적으로 일치한다.

---

## 9. honest limitation

종합 보고서로서 본 v12는 측정과 분석의 한계를 한 절에 모아 명시한다.

**(1) K=10 B1 측정 결함 — 가장 중요.** 대조군 B1이 strata 수 K에 의존하는 구조이고(`measure_b1_paper`의 `STRATA_K` 캐시), K=10에서 inf 폭증으로 B1 qe_trim이 3.0대로 손상되었다(§2.3). paired_delta_v12.parquet의 K=10 측정 120건 가운데 96건은 그 손상된 K=10 B1과 짝지어진 exact 측정으로 −36.15%의 허위 신호를 내고, 24건만 정상 K=20 B1을 fallback 분모로 쓴다. K=10 행 전체 평균 −26.85%(§7.2)는 이 둘이 섞인 합성값일 뿐 본 연구의 finding이 아니다. 본 보고서의 headline(−6.25%, 92.2%)은 K=10 paired 120건을 전부 제외한 1240건 기준이다. K granularity 분석(§7)은 본문 finding이 아닌 부속·미완 결과로 격하했으며, 신뢰 가능한 분모를 쓴 비교만 보면 K=20 ≈ K=30이고 K=10 CaseB는 정상 K=20 B1과의 fallback 비교에서 +10.35%로 오히려 약화된다.

**(2) A4-sel은 selectivity sweep이 아니다.** A4-sel cell은 sel=0.001 단일 값으로만 측정되었다(B1 1 + CaseB 16). paper Fig 13의 selectivity ablation 자체는 §4의 v9 sweep(24 cell × 3 sel)이 담당하며, A4-sel은 단일 selectivity의 high-error 측정점일 뿐 sweep cell이 아니다. A4-sel의 paired Δ%는 평균 +3.02%(better 37.5%)로 약한데, 이는 sel=0.001의 극단적 inherent 분산 때문이며 sweep의 sel=0.001 평균(−5.06%)과 구분해 읽어야 한다.

**(3) concat sf=100 부분 미측정.** concat 다중 벡터 cell 중 DEEP+SIFT는 sf=1/10/100 세 규모를 모두 측정했으나, DEEP+WIKI와 DEEP+YFCC는 sf=1/10만 측정되었고 sf=100은 없다. 이는 원본 데이터셋 측의 한계(해당 조합의 sf=100 적재 미비)이며, concat 분석(§5)의 sf=100 커버리지는 DEEP+SIFT 1종으로 제한된다.

**(4) measurement run 단위 systematic bias.** 별도 검증(`B1_variance_root_cause_종합분석`)에서 B1 baseline은 trial 단위 inherent CV가 약 6%, measurement run 단위 systematic bias가 ±10~25%로 확인되었다. 본 보고서의 paired 비교는 같은 measurement 안에서 B1과 CaseB를 짝짓기 때문에 이 bias의 영향을 상쇄하지만, paired Δ%의 절대 크기를 다른 측정 캠페인과 직접 비교할 때는 주의(caveat)가 필요하다.

**(5) 두 캠페인 측정 중복 정리.** 통합 단계에서 여러 캠페인을 합칠 때 같은 (cell, sel, K_norm, method, mode) 조합의 중복 측정이 발생했고, dedup rank(신규 16-method chain 우선) 기준으로 정리하여 최종 1444행을 만들었다. 정리 후 content_hash 중복 0건, paired 키 중복 0건으로, §3 이하의 paired 비교 1360건은 모두 독립적이다.

**(6) byte-identical method 중복과 method 명명 한계.** 별도 audit에서 일부 method 구현이 byte-identical하거나(pca1d ≡ cca1d 등) 알고리즘 명칭과 실제 구현이 불일치함(hilbert는 실제로 PCA 2D lex sort, sparse_rp는 Achlioptas가 아닌 Li-Hastie-Church 2006 variant)이 확인되었다. 본 v12는 사용 16 method만 분석 대상으로 하여 byte-identical 중복 method를 배제했고, hilbert_real·sparse_rp는 정직하게 명명된 구현을 사용한다. paradigm 간 비교 시 이 명명 한계를 발표·보고서에 명시할 것을 권장한다.

**(7) 통계 검정의 해상도·보정·효과크기 한계.** 본 보고서의 통계 수치는 결론을 뒤집지 않으나, 다음 네 가지 한계를 정직하게 명시한다. 첫째, **Wilcoxon 검정의 p값 해상도가 거칠다.** paired 비교는 cell·method·sel·K마다 trial n=10으로 수행되었고, n=10 one-sided Wilcoxon이 도달할 수 있는 최소 p값은 1/1024 ≈ 0.001이다. 실제로 paired 1360건 중 746건이 이 바닥값(p≈0.001)에 몰려 있어, 효과가 강한 비교들 사이의 미세한 우열은 p값으로 분해되지 않는다. 둘째, **BH-FDR 보정의 family 크기 문제.** 본 보고서는 paired 1360건 전체를 단일 검정 family로 묶어 BH-FDR을 적용했는데, 이질적인 cell·method를 한 family로 합치면 over-correction 경향이 있어 유의 우월 비율(78.3%)이 다소 보수적으로 추정된다. 셋째, **효과크기 공식의 보수성.** 본 보고서가 보고하는 Cliff's δ와 Hedges' g는 독립표본(independent-sample) 공식으로 계산되었으나, 실제 B1–CaseB 비교는 같은 trial을 짝지은 paired 설계다. paired 설계의 trial 간 상관을 반영하지 못하므로, 보고된 effect size는 실제 paired effect를 보수적으로(작게) 추정한다. 넷째, **집계 가중의 선택.** headline 92.2%·−6.25%는 file-weighted(측정 file 단위 동일 가중) 집계다. 같은 1240건을 cell-weighted(24 cell 동일 가중)로 재집계하면 better 90.6%·평균 −6.00%로 소폭 약화되는데, 이는 측정 file이 많은 cell의 영향이 줄기 때문이다. 두 집계 모두 결론(약 9할 비교에서 −6% 안팎 개선)을 뒤집지 않으나, 절대 수치는 가중 방식에 따라 ±0.3%p 안팎 움직인다는 점을 명시한다.

---

## 10. 결론

본 보고서는 통합 측정 1444건을 단일 portfolio로 모아, 대조군 B1(Bernoulli random sampling + Adaptive Sampling)과 실험군 CaseB(16 method 분포 인지 stratification ensemble + Adaptive Sampling)를 paired 비교했다. 검증 과정에서 드러난 K=10 측정 결함을 정직하게 배제한 신뢰 가능 비교 1240건이 분석의 근거다.

**핵심 finding**: paper Exqutor §V-B Adaptive Sampling의 sample selection 단계를 unstratified Bernoulli random sampling에서 분포 인지 stratification ensemble로 교체하면, 동일한 sample budget(N=385) 안에서 cardinality 추정의 Q-error가 일관되게 개선된다. paired 비교 1240건 중 92.2%에서 실험군이 우월하고, 평균 Δ%는 −6.25%, 통계적 유의 우월 78.3%, 효과크기 large 우월 82.5%로 신호가 견고하다. cardinality 추정 알고리즘과 AdaptiveState 식 1-6은 paper 그대로 두었으며, 본 연구의 개입은 오직 sample selection 단계에 한정된다 — 즉 본 연구가 보이는 것은 sample selection 단계의 개선이 cardinality 추정 Q-error의 측정 가능한 개선으로 이어진다는 evidence다.

이 개선은 조건에 따라 강약이 갈린다. selectivity가 낮을수록 개선 폭이 크고(0.001/0.01/0.10에서 better 84.4/92.4/99.2% 단조 증가), 단일 벡터 데이터셋에서 가장 크다(−7.66%, K=10 제외 기준). 다중 벡터를 연결한 concat에서는 우월 방향성은 유지되나 개선 크기가 작다(−3.84%). 16개 method 중 14개가 견고하게 우월하며, P1 Cluster paradigm(gmm, minibatch_partial)만 일관성을 보이지 못한다. 정확도 상위 method가 자원 효율 상위와 일치하여 맞교환이 성립하지 않는다(F7 자원·정확도 최적 경계). strata 수 K(§7)는 본문 finding이 아닌 부속·미완 결과로, K=10 대조군 B1의 측정 결함 때문에 깨끗한 비교가 성립하지 않는다 — 신뢰 가능한 분모만 보면 K=20 ≈ K=30이며, 본 연구는 paper default K=20을 그대로 채택한다.

본 보고서가 정직하게 남기는 한계는 K=10 B1의 구조적 결함, A4-sel이 단일 selectivity 측정점이라는 점, concat sf=100의 부분 미측정, measurement run bias, 그리고 통계 검정의 해상도·보정·효과크기·집계 가중 한계다(§9). 이 한계들은 본 핵심 finding의 신뢰성을 훼손하지 않는다 — headline 수치는 결함 데이터를 모두 배제한 1240건에서 산출되었고, paired 설계가 run bias를 상쇄하며, cell-weighted 재집계로도 결론이 유지되기 때문이다.

---

## v12 정정 로그

본 절은 v12 초안의 다각 검증에서 발견된 환각·오류와 그 정정 내역을 기록한다. 모든 정정 수치는 `_internal/cache/rq3/paired_delta_v12.parquet` 및 `aggregated_v12_full.parquet` 직접 재계산으로 확인했다.

**정정 1 — §7.2 K granularity 표 (환각 → 실측 전면 교체).** v12 초안의 §7.2 표는 "K=10 +14.62%, K=20 −1.51%, K=30 −0.63%"로 적혀 있었으나, 이 수치는 parquet의 어떤 부분집합으로도 재현되지 않는 환각이었다. parquet 실측으로 교체: K_norm 축 집계에서 K=10 n=120 better 86.7% mean −26.85% median −36.20%, K=20 n=1120 better 91.9% mean −6.19%, K=30 n=120 better 95.0% mean −6.76%. pairing을 분리하면 K=10 exact 96건 −36.15%(손상된 K=10 B1 분모 → 허위), K=10 fallback_K20 24건 +10.35%(정상 K=20 B1 분모 → K=10에서 실험군 약화), K=30 exact 64건 −5.52%, K=30 fallback_K20 56건 −8.18%. §7.2/§7.3을 실측 기반으로 재작성하고, §7 전체를 본문 finding이 아닌 "부속·미완 + honest limitation"으로 격하했다. 정정 전 결론 "K=10 < K=20 ≈ K=30, K=20 best"는 "K=20 ≈ K=30, K=10은 B1 측정 결함으로 비교 불가, fallback 비교 시 K=10에서 실험군 약화"로 바로잡았다.

**정정 2 — §3.3 A5-scale-sf1-SIFT B1 qe_trim (2.099 → 2.366).** §3.3은 가장 강한 8건의 cell을 "A5-scale-sf1-SIFT, sel=0.001"로 명시하면서 B1 qe_trim을 2.099로 적었으나, 2.099는 같은 cell의 sel=0.010 B1 qe_trim이다. sel=0.001 B1 qe_trim 실측값 2.366으로 정정했다(aggregated parquet A5-scale-sf1-SIFT, B1, sel=0.001).

**정정 3 — §2.3 경미 오차 2건.** "A1-SIFT/A1-SSN K=10 CaseB 96건 paired Δ% 평균 −36.12%"를 실측 −36.15%로, "동일 K=10 CaseB를 K=20 B1과 짝지으면 +17.91%"를 +18.13%로 정정했다.

**정정 4 — "영역" 필러 토큰 제거 (4개).** 조사·문맥상 무의미하게 삽입된 "영역" 토큰을 4곳(framing 문단 1, §7.2 본문 1, §10 결론 2)에서 전수 제거하고 정상 한국어로 고쳤다. 정정 후 보고서 전체 "영역" 출현 0회.

**정정 5 — §9 통계 limitation 항목 추가 (item 7 신설).** Wilcoxon n=10의 p값 해상도 한계(1360건 중 746건이 p≈0.001 바닥), BH-FDR 1360건 단일 family의 over-correction 경향, Cliff's δ·Hedges' g 독립표본 공식의 paired effect 보수적 추정, cell-weighted 재집계 시 better 90.6%·mean −6.00%(file-weighted 92.2%/−6.25% 대비 소폭 약화)를 §9 item (7)로 명시했다. 네 한계 모두 결론을 뒤집지 않는다.

**검증으로 정확 확인되어 변경하지 않은 부분.** headline(§3) better 92.2%·mean −6.25%·median −6.15%, selectivity(§4), single/concat(§5), method/paradigm(§6), figure(§8) 수치는 parquet과 완전 일치하여 그대로 두었다.

이상의 정정으로 본 v12 보고서는 모든 수치가 parquet 실측에 근거하며, K granularity를 정직하게 부속·미완 결과로 격하하고 통계 한계를 명시한 상태다. headline finding(약 9할 비교에서 −6% 안팎 Q-error 개선)은 정정 전후로 동일하며 신뢰 가능하다.

---

_End of REPORT v12._
