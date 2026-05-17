# Paired Δ% 분석 v12 — B1 대조군 vs CaseB 실험군

_생성_: 2026-05-17 11:58

_framing_: B1 = Bernoulli random + Adaptive Eq 1-6 (대조군), CaseB = 16 method stratification ensemble + Adaptive (실험군). CaseA 폐기.

paired Δ% = (CaseB_qe − B1_qe) / B1_qe × 100, 같은 cell·sel·K, trial-paired 10 trial. **음수 = 실험군이 더 정확**.

---

## 0. 통합 데이터 규모

- 통합 측정 file (16 method 필터 + dedup 후): **1444** (B1 80 + CaseB 1364)
- paired 비교 (CaseB × B1 매칭): **1360**건
- cell 25개, method 16개, sel 3종 (0.001/0.01/0.10), K 3종 (10/20-default/30)
- B1 pairing: {'exact': 1280, 'fallback_K20': 80} (fallback_K20 = K10/K30 CaseB 가 paper-default B1 과 매칭된 케이스)

## 1. 전체 paired Δ% 핵심 수치

- **전체 1360건 中 CaseB better (Δ%<0): 1247건 (91.7%)**
- one-sided greater p_adj(BH-FDR)<0.05 유의 outperform: 1071건 (78.8%)
- Cliff's δ large (≥0.474) better: 1126건 (82.8%)
- 전체 mean Δ%: **-8.06%** / median Δ%: **-6.58%**

## 2. selectivity 효과 (sel 0.001 / 0.01 / 0.10)

| sel | n | better | better% | 유의 outperform% | mean Δ% | median Δ% | δ large% |
|---|--:|--:|--:|--:|--:|--:|--:|
| 0.001 | 448 | 383 | 85.5% | 68.1% | -6.97% | -6.48% | 70.3% |
| 0.01 | 480 | 435 | 90.6% | 70.2% | -8.42% | -9.19% | 79.6% |
| 0.1 | 432 | 429 | 99.3% | 99.3% | -8.79% | -5.43% | 99.3% |

## 3. single vs multi(cross-table) vs concat

| 유형 | n | better | better% | 유의 outperform% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|--:|
| single | 864 | 796 | 92.1% | 82.1% | -10.37% | -8.46% |
| multi | 160 | 138 | 86.2% | 62.5% | -4.46% | -5.29% |
| concat | 336 | 313 | 93.2% | 78.0% | -3.84% | -5.38% |

### 3.1 single vs concat — sel 별 교차

| 유형 | sel | n | better% | mean Δ% | median Δ% |
|---|---|--:|--:|--:|--:|
| single | 0.001 | 288 | 86.5% | -9.33% | -7.13% |
| single | 0.01 | 304 | 90.5% | -10.78% | -10.25% |
| single | 0.1 | 272 | 100.0% | -11.03% | -5.87% |
| concat | 0.001 | 112 | 86.6% | -2.34% | -6.35% |
| concat | 0.01 | 112 | 94.6% | -4.48% | -8.23% |
| concat | 0.1 | 112 | 98.2% | -4.70% | -4.80% |

## 4. cell × method paired Δ% 매트릭스 (mean Δ%, 전 sel·K aggregate)

> 셀 값 = 해당 cell × method 의 모든 (sel,K) 평균 Δ%. 음수 = CaseB 우위.

| cell | minibatch_partial | gmm | faiss_ivf | hilbert_real | zorder_morton | skilling_hilbert | chao_weighted | sparse_rp | pca1d | rsvd | ica_fastica | cum_sqrtf | lavallee_hidiroglou | rabitq_strat | mhist2 | hyperloglog | row mean |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| A1-DEEP | -7.8 | -3.1 | -4.1 | -8.9 | -8.5 | -8.8 | -8.6 | -5.0 | -8.0 | -8.3 | -8.4 | -7.9 | -7.3 | -2.1 | -3.7 | -7.5 | -6.75 |
| A1-SIFT | -17.8 | -5.8 | -16.3 | -21.5 | -20.6 | -20.5 | -21.3 | -11.9 | -20.6 | -18.2 | -20.4 | -18.8 | -18.3 | -10.9 | -18.4 | -20.6 | -17.62 |
| A1-SSN | -15.5 | +5.1 | -13.5 | -17.8 | -17.0 | -18.4 | -19.3 | -8.9 | -17.2 | -16.4 | -17.3 | -14.9 | -15.5 | -16.2 | -17.1 | -17.7 | -14.85 |
| A10-DEEP+WIKI-concat-sf1 | -5.4 | +0.6 | -6.9 | -8.1 | -9.3 | -8.6 | -9.0 | -8.1 | -8.1 | -7.6 | -9.0 | -7.4 | -8.6 | -6.7 | -7.1 | -8.5 | -7.36 |
| A10-DEEP+WIKI-concat-sf10 | +188.2 | +17.5 | +29.7 | -5.3 | -5.6 | -5.2 | -4.7 | -4.6 | -5.1 | -4.4 | -4.0 | -4.3 | -3.9 | -1.1 | -2.7 | -4.9 | +11.22 |
| A11-DEEP+YFCC-concat-sf1 | -4.3 | -3.4 | -5.4 | -8.3 | -8.7 | -8.8 | -7.4 | -7.5 | -7.9 | -6.1 | -7.0 | -7.6 | -7.4 | -6.7 | -3.5 | -6.2 | -6.64 |
| A11-DEEP+YFCC-concat-sf10 | +1.4 | -4.8 | -4.5 | -9.6 | -9.3 | -9.8 | -9.6 | -9.9 | -9.2 | -7.3 | -10.4 | -9.7 | -9.5 | -2.3 | -5.7 | -8.5 | -7.42 |
| A2-Fig7 | -4.8 | +11.4 | -2.4 | -9.3 | -8.6 | -8.8 | -8.7 | -4.7 | -8.8 | -7.9 | -9.8 | -7.3 | -9.0 | -7.2 | -7.2 | -7.2 | -6.26 |
| A2-Fig9 | -3.6 | +2.0 | -1.3 | -4.9 | -5.3 | -3.6 | -4.3 | -1.0 | -5.8 | -4.5 | -4.6 | -5.5 | -4.1 | -0.5 | -0.4 | -3.8 | -3.20 |
| A4-sel | -1.2 | +1.9 | +9.2 | -3.2 | +10.0 | +6.1 | +5.4 | -2.0 | -3.3 | -4.8 | +7.4 | +8.4 | +8.3 | +7.5 | +3.1 | -4.5 | +3.02 |
| A5-scale-sf1 | -2.4 | +0.0 | -4.6 | -5.7 | -7.6 | -7.8 | -5.1 | +9.2 | -7.2 | -6.1 | -7.5 | -7.8 | -7.4 | -7.7 | -2.3 | -5.3 | -4.71 |
| A5-scale-sf1-SIFT | -26.0 | -9.2 | -24.8 | -27.1 | -28.2 | -27.9 | -27.2 | -27.1 | -27.6 | -27.4 | -27.6 | -25.9 | -26.3 | -26.8 | -25.9 | -28.5 | -25.85 |
| A5-scale-sf1-SSN | -7.5 | -6.7 | -6.4 | -6.0 | -6.9 | -5.7 | -5.9 | -7.4 | -6.6 | -6.6 | -5.8 | -4.9 | -4.4 | -7.1 | -6.6 | -6.1 | -6.29 |
| A5-scale-sf10 | -3.6 | +0.8 | -1.3 | -2.6 | -5.3 | -3.6 | -1.7 | +7.5 | -5.8 | -4.5 | -4.6 | -5.5 | -4.1 | -0.5 | -0.4 | -0.3 | -2.22 |
| A5-scale-sf10-SIFT | +0.1 | +7.8 | -10.0 | -12.6 | -12.4 | -10.8 | -11.0 | -11.7 | -12.1 | -9.2 | -12.6 | -10.3 | -10.3 | -8.3 | -10.8 | -11.8 | -9.12 |
| A5-scale-sf10-SSN | -2.7 | -2.6 | -4.7 | -3.6 | -3.6 | -3.9 | -4.9 | -4.7 | -5.2 | -3.3 | -4.2 | -2.5 | -1.7 | -3.3 | -2.2 | -3.5 | -3.54 |
| A5-scale-sf100 | -7.8 | -2.8 | -4.1 | -5.3 | -8.5 | -8.8 | -4.6 | +7.1 | -8.0 | -8.3 | -8.4 | -7.9 | -7.3 | -2.1 | -3.7 | -3.2 | -5.23 |
| A6-WIKI-sf1 | -6.9 | -3.8 | -10.0 | -12.7 | -13.1 | -12.9 | -12.2 | -12.3 | -12.7 | -10.6 | -12.4 | -11.4 | -10.8 | -12.2 | -11.1 | -10.3 | -10.95 |
| A6-WIKI-sf10 | +4.2 | +5.6 | +24.4 | -9.7 | -10.0 | -10.5 | -10.3 | -9.9 | -9.1 | -6.3 | -11.1 | -9.7 | -9.9 | -9.4 | -8.1 | -8.5 | -5.53 |
| A7-YFCC-sf1 | -4.4 | -1.7 | -1.0 | -10.6 | -9.2 | -11.5 | -10.0 | -10.1 | -9.5 | -10.3 | -9.3 | -10.9 | -10.0 | -8.5 | -9.3 | -9.2 | -8.47 |
| A8-DEEP+SIFT-sf10 | -3.6 | +0.5 | -1.3 | -5.0 | -5.5 | -3.4 | -3.9 | -5.8 | -5.8 | -4.5 | -4.4 | -5.8 | -3.7 | -1.6 | -0.4 | -2.9 | -3.56 |
| A9-DEEP+SIFT-concat-sf1 | -4.3 | -0.0 | -3.2 | -8.2 | -7.8 | -7.8 | -8.6 | -8.9 | -7.8 | -4.0 | -9.0 | -5.7 | -4.3 | -6.9 | -3.4 | -6.8 | -6.05 |
| A9-DEEP+SIFT-concat-sf10 | -1.2 | -1.1 | +1.2 | -8.1 | -7.2 | -6.8 | -7.3 | -7.4 | -8.1 | -3.7 | -7.3 | -4.9 | -4.7 | -5.1 | -3.3 | -5.5 | -5.04 |
| A9-DEEP+SIFT-concat-sf100 | -4.2 | -0.2 | -2.1 | -7.3 | -6.8 | -7.4 | -6.5 | -7.1 | -7.0 | -5.3 | -6.9 | -6.2 | -6.5 | -3.2 | -6.0 | -6.9 | -5.60 |
| **col mean** | **+2.5** | **+0.3** | **-2.6** | **-9.2** | **-9.0** | **-9.0** | **-8.6** | **-6.3** | **-9.5** | **-8.2** | **-8.9** | **-8.1** | **-7.8** | **-6.2** | **-6.5** | **-8.3** | **-6.58** |

### 4.1 method 별 rollup (전 cell·sel·K)

| method | paradigm | n | better% | mean Δ% | median Δ% | δ large% |
|---|---|--:|--:|--:|--:|--:|
| pca1d | P4 | 82 | 100.0% | -10.99% | -8.85% | 97.6% |
| skilling_hilbert | P2 | 82 | 95.1% | -10.88% | -8.99% | 90.2% |
| zorder_morton | P2 | 82 | 98.8% | -10.86% | -8.25% | 95.1% |
| ica_fastica | P4 | 82 | 98.8% | -10.78% | -9.00% | 90.2% |
| hilbert_real | P2 | 94 | 96.8% | -10.28% | -8.73% | 88.3% |
| chao_weighted | P3 | 94 | 95.7% | -9.99% | -8.45% | 87.2% |
| cum_sqrtf | P5 | 82 | 98.8% | -9.79% | -7.42% | 90.2% |
| rsvd | P4 | 82 | 100.0% | -9.58% | -6.62% | 92.7% |
| lavallee_hidiroglou | P5 | 82 | 93.9% | -9.50% | -7.54% | 82.9% |
| hyperloglog | P9 | 94 | 93.6% | -9.25% | -7.15% | 85.1% |
| mhist2 | P6 | 82 | 87.8% | -8.39% | -5.03% | 78.0% |
| rabitq_strat | P6 | 82 | 87.8% | -7.62% | -4.99% | 75.6% |
| sparse_rp | P4 | 94 | 93.6% | -5.86% | -7.30% | 86.2% |
| faiss_ivf | P2 | 82 | 79.3% | -4.72% | -4.19% | 68.3% |
| minibatch_partial | P1 | 82 | 87.8% | -0.26% | -4.36% | 69.5% |
| gmm | P1 | 82 | 57.3% | +0.19% | -0.73% | 45.1% |

### 4.2 paradigm 별 rollup

| paradigm | n_method | n_obs | better% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|
| P1 | 2 | 164 | 72.6% | -0.03% | -3.33% |
| P2 | 4 | 340 | 92.6% | -9.23% | -7.76% |
| P3 | 1 | 94 | 95.7% | -9.99% | -8.45% |
| P4 | 4 | 340 | 97.9% | -9.18% | -7.70% |
| P5 | 2 | 164 | 96.3% | -9.65% | -7.50% |
| P6 | 2 | 164 | 87.8% | -8.01% | -5.03% |
| P9 | 1 | 94 | 93.6% | -9.25% | -7.15% |

## 5. K granularity 효과 (K=10 / 20-default / 30)

| K | n | better% | 유의 outperform% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|
| 10 | 120 | 86.7% | 83.3% | -26.85% | -36.20% |
| 20 (default) | 1120 | 91.9% | 77.7% | -6.19% | -5.92% |
| 30 | 120 | 95.0% | 84.2% | -6.76% | -8.22% |

## 6. cell 별 요약

| cell | dataset | 유형 | n | better% | mean Δ% | best method (Δ%) |
|---|---|---|--:|--:|--:|---|
| A1-DEEP | DEEP | single | 56 | 98.2% | -6.85% | skilling_hilbert (-11.97%) |
| A1-SIFT | SIFT | single | 144 | 94.4% | -17.62% | hilbert_real (-55.44%) |
| A1-SSN | SimSearchNet++ | single | 144 | 95.1% | -14.85% | chao_weighted (-46.39%) |
| A10-DEEP+WIKI-concat-sf1 | DEEP+WIKI | concat | 48 | 97.9% | -7.36% | chao_weighted (-13.01%) |
| A10-DEEP+WIKI-concat-sf10 | DEEP+WIKI | concat | 48 | 81.2% | +11.22% | skilling_hilbert (-7.39%) |
| A11-DEEP+YFCC-concat-sf1 | DEEP+YFCC | concat | 48 | 100.0% | -6.64% | zorder_morton (-11.54%) |
| A11-DEEP+YFCC-concat-sf10 | DEEP+YFCC | concat | 48 | 95.8% | -7.42% | ica_fastica (-14.85%) |
| A2-Fig7 | YFCC | multi | 56 | 92.9% | -6.44% | ica_fastica (-12.33%) |
| A2-Fig9 | DEEP+WIKI | multi | 56 | 82.1% | -3.24% | sparse_rp (-7.30%) |
| A4-sel | DEEP | single | 16 | 37.5% | +3.02% | rsvd (-4.82%) |
| A5-scale-sf1 | DEEP | single | 56 | 87.5% | -4.28% | chao_weighted (-13.57%) |
| A5-scale-sf1-SIFT | SIFT | single | 48 | 100.0% | -25.85% | hyperloglog (-34.96%) |
| A5-scale-sf1-SSN | SimSearchNet++ | single | 48 | 97.9% | -6.29% | minibatch_partial (-12.08%) |
| A5-scale-sf10 | DEEP | single | 56 | 76.8% | -1.80% | sparse_rp (-7.30%) |
| A5-scale-sf10-SIFT | SIFT | single | 48 | 91.7% | -9.12% | ica_fastica (-16.90%) |
| A5-scale-sf10-SSN | SimSearchNet++ | single | 48 | 91.7% | -3.54% | chao_weighted (-6.73%) |
| A5-scale-sf100 | DEEP | single | 56 | 92.9% | -4.70% | skilling_hilbert (-11.97%) |
| A6-WIKI-sf1 | WIKI | single | 48 | 100.0% | -10.95% | pca1d (-14.83%) |
| A6-WIKI-sf10 | WIKI | single | 48 | 87.5% | -5.53% | skilling_hilbert (-14.36%) |
| A7-YFCC-sf1 | YFCC | single | 48 | 93.8% | -8.47% | skilling_hilbert (-15.63%) |
| A8-DEEP+SIFT-sf10 | DEEP+SIFT | multi | 48 | 83.3% | -3.56% | sparse_rp (-7.30%) |
| A9-DEEP+SIFT-concat-sf1 | DEEP+SIFT | concat | 48 | 89.6% | -6.05% | sparse_rp (-11.30%) |
| A9-DEEP+SIFT-concat-sf10 | DEEP+SIFT | concat | 48 | 91.7% | -5.04% | pca1d (-11.43%) |
| A9-DEEP+SIFT-concat-sf100 | DEEP+SIFT | concat | 48 | 95.8% | -5.60% | lavallee_hidiroglou (-11.46%) |

## 7. 빠진 조합 리포트

전체 (cell, sel, K) 조합 95개 中 불완전 15개:

| cell | sel | K | B1 | CaseB method수 | 빠진 method |
|---|---|--:|--:|--:|---|
| A1-DEEP | 0.01 | 10 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A1-DEEP | 0.01 | 30 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A1-SIFT | 0.01 | 30 | 0 | 16 | (B1만 결손) |
| A1-SSN | 0.01 | 30 | 0 | 16 | (B1만 결손) |
| A2-Fig7 | 0.01 | 10 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A2-Fig7 | 0.01 | 30 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A2-Fig8 | 0.01 | 20 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A2-Fig9 | 0.01 | 10 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A2-Fig9 | 0.01 | 30 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A5-scale-sf1 | 0.01 | 10 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A5-scale-sf1 | 0.01 | 30 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A5-scale-sf10 | 0.01 | 10 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A5-scale-sf10 | 0.01 | 30 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A5-scale-sf100 | 0.01 | 10 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |
| A5-scale-sf100 | 0.01 | 30 | 0 | 4 | cum_sqrtf, faiss_ivf, gmm, ica_fastica, lavallee_hidiroglou, mhist2 … |

**해석**:
- `B1만 결손` (CaseB 16 완비, B1=0): K=10/30 변형 cell — 측정 시 paper-default(K=20) B1 대비 paired 측정. 분석에서 K=20 B1 fallback 적용 (정상).
- `CaseB method수=4` (chao_weighted/hilbert_real/hyperloglog/sparse_rp만): raw K-sweep 5/12 partial run — A1-DEEP/A2-Fig7/A2-Fig9/A5-DEEP 계열 K10/K30 은 4 method만 측정. A1-SIFT/A1-SSN 만 16 method K-chain 완비.
- A2-Fig8 (DEEP+CC3M multi-vector): paper §V-A multi-table scope 외 (C5 cascade drop) — 4 method만, 분석 참고용.

## 8. Top winner / loser (개별 cell×method×sel×K)

### 8.1 Top 10 CaseB winner (smallest Δ%)

| cell | method | sel | K | Δ% | p_adj(BH) | Cliff δ | Hedges g |
|---|---|---|--:|--:|--:|--:|--:|
| A1-SIFT | hilbert_real | 0.01 | 10 | -55.44% | 0.0018 | +1.000 | -9.187 |
| A1-SIFT | chao_weighted | 0.01 | 10 | -54.82% | 0.0018 | +1.000 | -9.159 |
| A1-SIFT | hyperloglog | 0.01 | 10 | -54.80% | 0.0018 | +1.000 | -9.105 |
| A1-SIFT | sparse_rp | 0.01 | 10 | -49.29% | 0.0018 | +1.000 | -8.099 |
| A1-SSN | chao_weighted | 0.01 | 10 | -46.39% | 0.0018 | +1.000 | -11.175 |
| A1-SSN | skilling_hilbert | 0.001 | 10 | -45.66% | 0.0018 | +1.000 | -22.344 |
| A1-SSN | hilbert_real | 0.01 | 10 | -45.03% | 0.0018 | +1.000 | -11.663 |
| A1-SSN | hyperloglog | 0.01 | 10 | -44.63% | 0.0018 | +1.000 | -11.359 |
| A1-SIFT | skilling_hilbert | 0.01 | 10 | -43.51% | 0.0018 | +1.000 | -7.261 |
| A1-SSN | chao_weighted | 0.001 | 10 | -43.46% | 0.0018 | +1.000 | -20.538 |

### 8.2 Top 10 CaseB loser (largest Δ%)

| cell | method | sel | K | Δ% | p_adj(BH) | Cliff δ | Hedges g |
|---|---|---|--:|--:|--:|--:|--:|
| A10-DEEP+WIKI-concat-sf10 | minibatch_partial | 0.001 | 20 | +290.08% | 0.0035 | -1.000 | +1.767 |
| A10-DEEP+WIKI-concat-sf10 | minibatch_partial | 0.01 | 20 | +276.41% | 0.0063 | -0.820 | +0.536 |
| A5-scale-sf1 | sparse_rp | 0.01 | 10 | +77.16% | 0.0035 | -1.000 | +27.352 |
| A5-scale-sf100 | sparse_rp | 0.01 | 10 | +68.33% | 0.0035 | -1.000 | +10.246 |
| A6-WIKI-sf10 | faiss_ivf | 0.001 | 20 | +66.07% | 0.0357 | -0.580 | +0.698 |
| A5-scale-sf10 | sparse_rp | 0.01 | 10 | +56.19% | 0.0035 | -1.000 | +7.535 |
| A10-DEEP+WIKI-concat-sf10 | faiss_ivf | 0.001 | 20 | +52.90% | 0.0035 | -1.000 | +3.854 |
| A1-SSN | gmm | 0.001 | 20 | +46.06% | 0.0035 | -1.000 | +2.633 |
| A10-DEEP+WIKI-concat-sf10 | gmm | 0.001 | 20 | +31.62% | 0.0035 | -1.000 | +4.301 |
| A10-DEEP+WIKI-concat-sf10 | faiss_ivf | 0.01 | 20 | +29.04% | 0.0035 | -1.000 | +3.468 |
