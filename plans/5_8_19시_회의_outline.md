# 5/8 (목) 19:00 비대면 회의 outline

> W1 Sprint 마감 직후 회의. 5/6 진행한 RQ1+RQ2 결과를 전원 공유하고, RQ3 (7-way distribution-agnostic) 진행 계획과 채림 석사·지도교수님께 보낼 자문 요청을 합의한다.
>
> 작성: 조현빈 · 2026-05-06 17:49 KST

---

## 1. 회의 개요

| 항목 | 내용 |
|---|---|
| 일시 | 2026-05-08 (목) 19:00~20:30 (90분 예정) |
| 형식 | 비대면 (Discord 또는 Zoom) |
| 참석 | 박세은(팀장), 강재현, 조현빈, 이동욱 |
| 의제 | (1) RQ1+RQ2 W1 sprint 결과 종합 (2) RQ3 진행 계획 (3) 자문 초안 합의 (4) W2 분담 |
| 산출물 | 회의록, 자문 발송 초안 (5/15 발송), W2 분담표 |

---

## 2. RQ1+RQ2 결과 1-pager (W1 Sprint, 5/6 측정)

### 2.1 RQ1 — H1 정량 입증 ★ (실험 #1, commit `cce2246`)

박세은 팀장이 5/5 회의에서 제기한 "Normal vs Skew BERN baseline 직접 비교 부재" 의문에 대한 정량 답변. SIFT × SYSTEM(block) baseline 측정으로 RQ1 의 2x2 표 마지막 한 cell 을 채워 모든 셀이 완성되었다. 핵심 결과는 **모든 selectivity 에서 SIFT(skew) 의 SYSTEM-BERN 격차가 DEEP(normal) 의 격차보다 크다**는 것이며, 좁은 selectivity 영역 (s=1%) 에서 격차가 +5.61%p 로 가장 두드러진다.

| sel | SIFT(skew) Δ% | DEEP(normal) Δ% | (SIFT − DEEP) |
|---|---|---|---|
| 0.01 | +10.27% | +4.66% | **+5.61%p** |
| 0.05 | +17.32% | +12.61% | **+4.71%p** |
| 0.10 | +16.68% | +14.76% | +1.92%p |
| 0.30 | +14.85% | +14.05% | +0.80%p |
| 0.50 | +14.36% | +12.59% | +1.77%p |

paired Wilcoxon p-value 는 SIFT 5 sel 모두 1e-4 ~ 1e-49 수준으로 매우 강한 유의 신호이며, BH-FDR 보정 후에도 모두 유의 유지된다. 부수 sanity 회복으로 5/6 오전 의심된 PG `setseed` 비작동 의혹은 query 별 raw q_error 분석으로 해소되었다 (`setseed` 정상, median 의 우연한 일치는 좁은 sel 에서 q_error 가 매우 discrete 한 데이터 특성).

→ **인용 그림**: `experiments/figures/rq1_rq2_w1_sprint/fig1_rq1_cross_dataset_gradient.png` (SIFT vs DEEP Δ% gradient).

### 2.2 RQ2 — Allocation 5-way 비교 (실험 #2+#3, commit `9d08e82`)

기존 KM20 stratified 가 사실상 Equal Allocation 이었음을 vector.c 코드 점검으로 확인하고, 그 위에 Proportional/Neyman/Anti-Neyman 3 mode 를 추가하여 5-way 비교 (BERN baseline 포함) 를 수행하였다. DEEP/SIFT × 5 sel × 5 seed × 100 query × 5 mode = 25,000 rows. 측정 17.1초 (Python 시뮬레이션, vector.c 패치 buggy 라 우회).

핵심 결과 4가지:

(가) **모든 stratified > BERN** (DEEP -1.3 ~ -7.0%, SIFT -3.7 ~ -10.5%, p ≤ 1e-7 ~ 1e-50). SIFT 의 effect size (Cohen's d) 가 DEEP 의 2 배 이상 — cluster 비균질성에서 stratified 의 가치가 정통 통계와 일치.

(나) **Neyman vs Equal — 부분 입증 (H2-N)**: SIFT × 좁은 sel 에서만 통계적 유의 (s=0.01 -11.91%, p_BH=0.024; s=0.05 -3.07%, p_BH=0.010). DEEP 에서는 모두 비유의. σ_i 단일 정의의 한계가 다중 비교 보정 결과에서 직접 드러난 셈이며, 이는 RQ3 의 query-aware Online (B/G) 영역으로 미루는 근거가 된다.

(다) **Anti-Neyman vs Proportional — 반증 (H2-AN)**: 모든 case 에서 통계적 유의 X (DEEP p=0.193~0.846, SIFT p=0.205~0.994). σ_i 신호가 N_i 보다 약해 ablation 효과가 통계 noise 안에 묻혔다.

(라) **새 발견 — SIFT × Equal × s=0.01 anomaly**: Equal Allocation 의 q_error (1.8463) 가 BERN baseline (1.6925) 보다도 부정확. cluster 크기 변동이 큰 SIFT 에서 Equal 의 균등 배분 (385/20 ≈ 19 표본/cluster) 이 큰 cluster (148K) 에서 sample 부족 → 부정확. **"Equal 은 normal 데이터엔 OK, skew 에서는 Proportional 이상 필요"** narrative 의 직접 증거.

→ **인용 그림**: `fig2_rq2_5mode_per_dataset.png` (5-mode q_error 비교), `fig3_rq2_cluster_heterogeneity.png` (N_i × σ_i scatter), `fig5_rq2_sift_equal_anomaly.png` (anomaly 막대).

### 2.3 RQ2 — Sample size sensitivity (실험 #4, commit `0f48f18` + 5sel 보강 `336171c`)

5/5 회의의 비판 "Exqutor 대비 효과 약함" 에 대한 직접 답변. KM20-Proportional 의 BERN 대비 개선이 sample_size 에 어떻게 의존하는지 측정. 4 ssize × 2 dataset × 5 sel × 5 seed × 100 query × 2 mode = 40,000 rows. 측정 51.1초.

가설 H2-S (sample_size 작을수록 KM20 효과 큼) 는 DEEP s=0.05 에서만 부분 단조이며 다른 case 는 non-monotonic — **미입증**. 그러나 **새 발견** 이 더 가치 있다: 모든 40 조합에서 KM20 > BERN 일관 (Δ% -1.09 ~ -13.50%). sample_size 30 배 차이 (100 ~ 3000) 에 걸쳐 **KM20 의 가치가 robust 하게 유지** 된다. production 관점에서는 "어느 sample_size 영역에서도 KM20 가치 유지" 라는 cost-tunable narrative 가 H2-S 단조성보다 오히려 강한 메시지가 된다.

→ **인용 그림**: `fig4_rq2_size_sensitivity.png` (5sel × 4ssize matrix).

### 2.4 보강 작업 — BH-FDR + DEEP query difficulty (commit `336171c`)

다중 비교 false discovery rate 통제를 위한 Benjamini-Hochberg 보정을 RQ1 SIFT (5 비교), RQ2 stratified vs BERN (40 비교), RQ2 Neyman vs Equal (10 비교) 의 세 영역에 적용하였다. **모든 핵심 결과가 BH-FDR 보정 후에도 robust** 하며, 특히 SIFT × {s=0.01, s=0.05} 에서의 Neyman 가치는 다중 비교 보정 후에도 명확히 검출된다 (p_BH = 0.010~0.024).

추가로 박세은 팀장의 4/30 직후 질문 "DEEP × SYSTEM 의 절대값이 SIFT 보다 클 때가 있는데?" 에 대한 정량 답변을 정리하였다. DEEP × s=0.01 에서 mean q_error 는 1.6185 로 SIFT (1.9205) 보다 작으나, **q_error > 2 query 비율이 DEEP 9% vs SIFT 39.4%** 로 본질적 query difficulty 는 SIFT 가 4 배 이상 크다. DEEP × s=0.01 의 max q_error 가 가끔 SIFT 보다 큰 것은 BERN sampling 의 small-sample fallback artifact 이며 본질적 difficulty 와는 다른 차원의 현상이다.

---

## 3. RQ3 진행 계획 — 7-way distribution-agnostic 비교

### 3.1 핵심 metric — Recovery Rate

```
recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20)
```

- 1.0 → KM20 oracle 수준 회수
- 0.0 → RANDOM20 (공간 인식 없음) 수준
- 분모 붕괴 (`|KM20 − RANDOM20| ≤ 1%p`) 시 절대 Q-error (방법X − BERN) 으로 fall back

### 3.2 7-way 실험 — 우선순위 순

총 ~27h 분량. 5/8 19:00 회의 후 5/11 까지 ~50h 가용 시간 안에서 1~3 순위 (F, C, E) 절대 사수, 4~7 순위는 가능한 선까지 수행. 모든 실험은 5/6 검증된 Python 시뮬레이션 패턴 (`experiments/code/rq2/rq2_alloc_python.py`) 그대로 활용 — cluster 별 LIMIT 500 sample 캐시, fresh conn per cluster (메모리 누수 회피), HT estimator 동일. 방법별 차이는 stratum_id 부여 알고리즘뿐이다.

| # | 실험 | 패러다임 | 시간 | 우선순위 | 기대 recovery |
|---|------|---------|------|---------|--------|
| #8 | F. MiniBatch K-means | Offline (학습 1~5%) | ~1h | ★★★ 1순위 | 75~95% |
| #5 | C. Random Projection | Offline (단순 하한) | ~2h | ★★ 2순위 | 10~40% |
| #7 | E. Hilbert Curve | Offline (결정론) | ~4h | ★★ 3순위 | 20~60% (contribution 후보) |
| #6 | A. LSH | Offline (확률) | ~4h | ★ 4순위 | 30~60% |
| #10 | B. KDE-pilot | Online (정교) | ~6h | ★ 5순위 | 50~80% (이론 상한) |
| #9 | G. Distance-Shell | Online (단순) | ~4h | ★ 6순위 | 25~50% |
| #11 | H. Importance Sampling | 비분할 (가중치) | ~6h | ★ 7순위 (2x2 factorial) | 30~70% |

### 3.3 그림 자리 (W2 측정 후 채울 placeholder)

회의 자료 + 자문 첨부 + 최종 발표 슬라이드의 **3 곳에서 동일 그림이 재사용** 되도록 pre-define:

- `fig6_rq3_recovery_comparison.png` — 7 method × 2 dataset × 5 sel matrix (heatmap). RQ3 의 핵심 그림.
- `fig7_rq3_paradigm_tradeoff.png` — Offline vs Online vs Weight 패러다임의 cost-recovery scatter (x축 사전 학습 비용, y축 recovery rate).
- `fig8_rq3_method_ranking.png` — 7 method 의 boxplot (5 sel × 5 seed × 100 query 분포), 정렬 기준 평균 recovery rate.
- `fig9_rq3_minibatch_vs_oracle.png` (가설용) — 1~5% 학습 비용에서 KM20 oracle 의 75~95% 회수 가능성 입증 그림.

### 3.4 위험 요인 + Plan B

(1) **MiniBatch K-means 가 KM20 의 95% 이상 회수하면** RQ3 의 narrative 가 "production 솔루션은 MiniBatch 면 충분" 으로 강한 메시지가 됨. 반대로 60% 미만 회수면 Hilbert Curve 의 결정론적 장점을 contribution 후보로 격상.

(2) **Online (B/G) 의 query-aware σ_i 가 RQ2 Neyman 의 약한 신호를 강하게 해주면** Limitation 4의 "단일 → 멀티 일반화" 보다 contribution 가 강해질 수 있음. 측정 후 우선순위 재조정 가능성 있음.

(3) **시간 부족 시 W2 (5/12~5/18) 로 #9~#11 이월** — 5/8 회의에서 이 분담을 합의해야 함.

---

## 4. 자문 요청 핵심 질문

5/15 발송 예정 자문 문서 (`submission/_drafts/속도는벡터_채림자문_20260507.md`) 에 포함될 검토 요청. 5/8 회의에서 전원 합의 필요.

### 4.1 채림 석사님께

(1) **Neyman Allocation 의 σ_i 정의 적절성** — 본 측정에서 σ_i 를 sel=0.10 D_target anchor 로 단일 정의하였는데, 이로 인해 SIFT × 좁은 sel 에서만 Neyman 효과가 검출되었다 (BH-FDR 보정 후 p=0.010~0.024). σ_i 를 query-aware 로 정교화하면 더 강한 신호를 검출할 수 있을지, 아니면 RQ3 의 Online (B/G) 영역으로 미루는 것이 더 학술적으로 정당한지의 판단을 요청드린다.

(2) **Anti-Neyman 반증의 의미 해석** — H2-AN 이 모든 case 에서 통계적으로 유의하지 않게 나온 것 (DEEP p=0.193~0.846, SIFT p=0.205~0.994) 이 (a) σ_i 신호 부족 때문인지 (b) Anti-Neyman 의 이론적 손해가 본 데이터에서는 N_i 신호에 의해 상쇄되어 nullify 되는 것인지의 통계학적 해석 의견.

(3) **"실험 #4 H2-S 미입증 → robustness 발견" narrative 전환의 적절성** — H2-S 의 sample_size 단조 감소 가설이 미입증된 후, KM20 robustness 라는 새 narrative 로 전환하였다. 이 narrative 전환이 (a) 사후 합리화 (post-hoc rationalization) 의 위험을 갖는지 (b) production 관점의 가치 메시지로 정당한지의 판단.

### 4.2 지도교수님께

(1) **본 연구의 positioning** — "Exqutor 가 미작동하는 단일 테이블 영역에 대한 분포 정보의 가치 정량화" framing 의 적절성. 단일 → 멀티 일반화 Limitation 명시 방향.

(2) **RQ3 의 ranking 자체가 contribution 인가, 아니면 ranking 위에 새 method 가 필요한가** — 7-way 비교 자체로 학부 캡스톤 contribution 이 충분한지, Hilbert Curve 의 결정론적 장점 같은 부분에서 추가 method 를 제안해야 할지의 방향 결정.

(3) **5/27 최종 발표까지의 일정** — W2 (5/12~5/18) RQ3 Online + Weight 측정, W3 (5/19~5/22) cross-analysis 의 압축 일정 현실성.

---

## 5. W2 (5/12~5/18) 분담 (안)

| 영역 | 1차 책임 | 2차 책임 | 비고 |
|---|---|---|---|
| RQ3 측정 #5~#8 (Offline 4종) | 조현빈 | 이동욱 | W1 측정 인프라 재활용 |
| RQ3 측정 #9~#11 (Online 2 + Weight 1) | 강재현 | 조현빈 | 6h+6h+6h, 시간 압박 큼 |
| 자문 메일 발송 + 회신 정리 | 박세은 | — | 5/15 발송, 5/22 미팅 전 회신 수렴 |
| Recovery Rate cross-analysis | 박세은 | 조현빈 | W3 (5/19~5/22) |
| 발표 자료 초안 | 강재현 | 박세은 | W3 마감 (~5/21) |

---

## 6. 다음 일정

| 마감 | 산출 | 비고 |
|---|---|---|
| **5/8 (목) 19:00** | **★ 본 회의 + 자문 발송 합의** | **D-2** |
| 5/11 | RQ3 #5~#8 측정 마감 (Offline) | 조현빈 |
| ~5/15 | 자문 발송 (채림 석사 + 교수님) | 박세은 |
| 5/18 | RQ3 #9~#11 측정 마감 (Online + Weight) | 강재현 |
| ~5/21 | 발표자료 초안 + Recovery Rate cross-analysis | 강재현·박세은 |
| 5/22 | 교수님 미팅 | 전원 |
| 5/26 | 발표자료 최종 마감 | 전원 |
| **5/27** | **★ 최종 발표** | **D-21** |
| 5/28 | 전시회 자료 마감 | — |
| **6/11** | **★ 최종 보고서** | **D-36** |

---

## 7. 첨부 자료 (회의 시 공유)

- 본 outline: `plans/5_8_19시_회의_outline.md`
- RQ 재정립 설계안 (5/5 확정): `plans/RQ재정립_20260505_2122.md`
- RQ3 7-way 상세 설계: `plans/RQ3설계안_20260416_213500.md`
- RQ1+RQ2 결과 정리: `experiments/results/RQ1_RQ2 실험 결과 정리.md`
- 측정 raw 데이터:
  - RQ1 SIFT SYSTEM: `experiments/results/rq1_motivation/sift_rq1_2026_05_06/`
  - RQ2 5-mode: `experiments/results/rq2_aware/2026_05_06_alloc/rq2_alloc.parquet`
  - RQ2 sample size: `experiments/results/rq2_aware/2026_05_06_alloc/rq2_size_sensitivity_5sel.parquet`
- W1 figures (5종): `experiments/figures/rq1_rq2_w1_sprint/`
- 5/5 회의록: `_internal/records/kakaotalk/20260505_RQ재정립_회의.md`
- 자문 초안: `submission/_drafts/속도는벡터_채림자문_20260507.md`

---

*본 outline 은 5/8 19:00 비대면 회의 진행을 위한 작성 자료이며, 회의 종료 후 회의록 (`_internal/records/kakaotalk/20260508_W1결과_RQ3계획_자문합의.md`) 으로 별도 정리한다.*
