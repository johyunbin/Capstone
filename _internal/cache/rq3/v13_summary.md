# REPORT v13 / narrative v8 수치 요약 — 3-way matched 캠페인

_생성_: 2026-05-18 20:17 · 출처 aggregated_v13_full.parquet (4524 row) + paired_delta_v13.parquet (4524 row)

## 1. 측정 portfolio
- 3-way 측정: **1508건** (각 측정 = B1·CaseA·CaseB matched). row 4524 = 1508×3
- cell 25 · method 16 · sf [1, 10, 100] · K [10, 20, 30] · sel [0.001, 0.01, 0.1]
- by sf: {1: 416, 10: 580, 100: 512}
- by K: {10: 192, 20: 1124, 30: 192}
- by sel: {0.001: 448, 0.01: 628, 0.1: 432}
- by single_multi: {'concat': 336, 'multi': 212, 'single': 960}

### 1.1 mode 별 qe_trim·final_size (descriptive)
| mode | n | qe_trim mean | qe_trim median | final_size mean |
|---|--:|--:|--:|--:|
| B1 | 1508 | 1.4582 | 1.5616 | 3155 |
| CaseA | 1508 | 1.6359 | 1.5699 | 3934 |
| CaseB | 1508 | 1.4019 | 1.4492 | 2021 |

## 2. B1 qe_trim by K — v12 K=10 결함 해소 검증
> v12: K=10 B1 qe_trim 2.2~3.3 손상 (2단계 STRATA_K 캐시 inf 폭증). v13 B1 = 1단계 → 검증.
| K | n | B1 qe_trim mean | min | max | n_inf_total mean (10 trial 합) |
|---|--:|--:|--:|--:|--:|
| 10 | 192 | 1.5132 | 1.1555 | 1.6457 | 261.9 |
| 20 | 1124 | 1.4402 | 1.1539 | 1.6560 | 382.6 |
| 30 | 192 | 1.5091 | 1.1554 | 1.6457 | 260.1 |

## 3. 3-way paired Δ% headline
> delta = (exp_qe − base_qe)/base_qe × 100, trial-paired 10 trial. 음수 = exp 우위.
> **better% 정의**: 측정별 delta_pct_mean(10 trial Δ% 평균)이 음수인 측정의 비율 — mean 기준이 정본. median 기준으로 세면 값이 달라지므로 혼용 금지.
| 비교 | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| CaseA_vs_B1 | 1508 | 531 | 35.2% | 6.8% | 13.5% | +12.90% | +1.09% |
| CaseB_vs_B1 | 1508 | 1344 | 89.1% | 65.3% | 72.1% | -3.06% | -4.38% |
| CaseA_vs_CaseB | 1508 | 53 | 3.5% | 0.0% | 1.3% | +13.92% | +7.02% |
- CaseA_vs_B1: Δ% 범위 [-16.86%, +6591.16%], outlier 제외 mean +3.82%
- CaseB_vs_B1: Δ% 범위 [-13.60%, +1043.19%], outlier 제외 mean -4.09%
- CaseA_vs_CaseB: Δ% 범위 [-17.22%, +3507.77%], outlier 제외 mean +9.12%

## 4. CaseB_vs_B1 상세 (결합 실험군 vs 대조군 — REPORT 핵심)

### 4.1 selectivity 별
| sel | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| sel=0.001 | 448 | 373 | 83.3% | 52.5% | 54.2% | -1.75% | -4.39% |
| sel=0.01 | 628 | 550 | 87.6% | 52.4% | 67.7% | -3.54% | -6.61% |
| sel=0.1 | 432 | 421 | 97.5% | 97.2% | 97.2% | -3.72% | -4.17% |

### 4.2 single / multi / concat 별
| 유형 | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| single | 960 | 855 | 89.1% | 64.5% | 72.2% | -4.12% | -4.38% |
| multi | 212 | 190 | 89.6% | 67.0% | 73.1% | -4.54% | -4.61% |
| concat | 336 | 299 | 89.0% | 66.4% | 71.4% | +0.92% | -4.31% |

### 4.3 single × sel 교차
| 유형 | sel | n | better% | mean Δ% | median Δ% |
|---|---|--:|--:|--:|--:|
| single | 0.001 | 288 | 83.0% | -2.91% | -4.39% |
| single | 0.01 | 400 | 88.0% | -5.31% | -6.63% |
| single | 0.1 | 272 | 97.1% | -3.67% | -4.12% |
| concat | 0.001 | 112 | 80.4% | +2.16% | -4.11% |
| concat | 0.01 | 112 | 88.4% | +4.40% | -6.38% |
| concat | 0.1 | 112 | 98.2% | -3.80% | -4.21% |

### 4.4 method 별 (mean Δ% 오름차순)
| method | paradigm | n | better% | 유의% | δlarge% | mean Δ% | mean(outlier제외) | median Δ% |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| hilbert_real | P2 | 95 | 98.9% | 86.3% | 87.4% | -6.54% | -6.54% | -5.91% |
| skilling_hilbert | P2 | 94 | 100.0% | 76.6% | 87.2% | -6.34% | -6.34% | -5.75% |
| chao_weighted | P3 | 95 | 100.0% | 83.2% | 87.4% | -6.30% | -6.30% | -6.22% |
| ica_fastica | P4 | 94 | 100.0% | 83.0% | 87.2% | -6.13% | -6.13% | -5.69% |
| pca1d | P4 | 94 | 97.9% | 84.0% | 92.6% | -6.05% | -6.05% | -5.55% |
| zorder_morton | P2 | 94 | 98.9% | 75.5% | 76.6% | -5.87% | -5.87% | -4.89% |
| hyperloglog | P9 | 95 | 100.0% | 75.8% | 80.0% | -5.75% | -5.75% | -4.58% |
| cum_sqrtf | P5 | 94 | 97.9% | 66.0% | 73.4% | -5.14% | -5.14% | -4.53% |
| lavallee_hidiroglou | P5 | 94 | 94.7% | 69.1% | 73.4% | -4.82% | -4.82% | -4.40% |
| rsvd | P4 | 94 | 91.5% | 58.5% | 70.2% | -4.36% | -4.36% | -4.10% |
| sparse_rp | P4 | 95 | 84.2% | 68.4% | 74.7% | -3.69% | -3.69% | -4.37% |
| mhist2 | P6 | 94 | 88.3% | 47.9% | 60.6% | -3.16% | -3.16% | -3.41% |
| rabitq_strat | P6 | 94 | 84.0% | 43.6% | 56.4% | -2.67% | -2.67% | -3.56% |
| faiss_ivf | P2 | 94 | 69.1% | 43.6% | 53.2% | -0.69% | -0.69% | -2.70% |
| gmm | P1 | 94 | 40.4% | 29.8% | 31.9% | +4.63% | +4.63% | +2.68% |
| minibatch_partial | P1 | 94 | 79.8% | 52.1% | 61.7% | +14.06% | -2.52% | -3.58% |

### 4.5 paradigm 별
| paradigm | n_method | n | better% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|
| P3 | 1 | 95 | 100.0% | -6.30% | -6.22% |
| P9 | 1 | 95 | 100.0% | -5.75% | -4.58% |
| P4 | 4 | 377 | 93.4% | -5.05% | -4.72% |
| P5 | 2 | 188 | 96.3% | -4.98% | -4.43% |
| P2 | 4 | 377 | 91.8% | -4.86% | -4.66% |
| P6 | 2 | 188 | 86.2% | -2.91% | -3.52% |
| P1 | 2 | 188 | 60.1% | +9.34% | -1.40% |

### 4.6 cell 별 (mean Δ% 오름차순)
| cell | dataset | 유형 | n | better% | mean Δ% | median Δ% |
|---|---|---|--:|--:|--:|--:|
| A2-Fig8 | DEEP+CC3M | multi | 4 | 100.0% | -9.46% | -9.36% |
| A5-scale-sf10-SSN | SimSearchNet++ | single | 48 | 100.0% | -5.63% | -4.77% |
| A5-scale-sf1-SSN | SimSearchNet++ | single | 48 | 95.8% | -5.39% | -4.46% |
| A5-scale-sf100 | DEEP | single | 80 | 90.0% | -5.36% | -5.51% |
| A1-DEEP | DEEP | single | 80 | 90.0% | -5.32% | -5.27% |
| A6-WIKI-sf1 | WIKI | single | 48 | 95.8% | -4.98% | -4.66% |
| A8-DEEP+SIFT-sf10 | DEEP+SIFT | multi | 48 | 93.8% | -4.75% | -4.38% |
| A2-Fig9 | DEEP+WIKI | multi | 80 | 88.8% | -4.72% | -4.52% |
| A5-scale-sf10 | DEEP | single | 80 | 88.8% | -4.68% | -4.52% |
| A4-sel | DEEP | single | 16 | 81.2% | -4.57% | -4.42% |
| A11-DEEP+YFCC-concat-sf1 | DEEP+YFCC | concat | 48 | 95.8% | -4.49% | -4.23% |
| A7-YFCC-sf1 | YFCC | single | 48 | 91.7% | -4.43% | -4.38% |
| A9-DEEP+SIFT-concat-sf100 | DEEP+SIFT | concat | 48 | 89.6% | -4.38% | -4.21% |
| A9-DEEP+SIFT-concat-sf1 | DEEP+SIFT | concat | 48 | 89.6% | -4.28% | -4.27% |
| A2-Fig7 | YFCC | multi | 80 | 87.5% | -3.98% | -5.03% |
| A5-scale-sf1-SIFT | SIFT | single | 48 | 89.6% | -3.93% | -4.36% |
| A11-DEEP+YFCC-concat-sf10 | DEEP+YFCC | concat | 48 | 85.4% | -3.90% | -4.47% |
| A10-DEEP+WIKI-concat-sf1 | DEEP+WIKI | concat | 48 | 95.8% | -3.86% | -4.37% |
| A5-scale-sf1 | DEEP | single | 80 | 87.5% | -3.85% | -4.61% |
| A1-SIFT | SIFT | single | 144 | 86.1% | -3.71% | -4.36% |
| A9-DEEP+SIFT-concat-sf10 | DEEP+SIFT | concat | 48 | 85.4% | -3.60% | -4.26% |
| A1-SSN | SimSearchNet++ | single | 144 | 91.0% | -3.21% | -4.14% |
| A5-scale-sf10-SIFT | SIFT | single | 48 | 79.2% | -2.85% | -4.03% |
| A6-WIKI-sf10 | WIKI | single | 48 | 77.1% | -0.92% | -3.64% |
| A10-DEEP+WIKI-concat-sf10 | DEEP+WIKI | concat | 48 | 81.2% | +30.94% | -4.24% |

## 5. K granularity — CaseB_vs_B1 (8 K-gran cell × sel=0.01, matched 3-way)
> v12 와 달리 v13 은 각 측정이 자체 B1(1단계) 보유 → K=10 도 깨끗한 비교.
| K | n | better | better% | 유의% | δlarge% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|--:|--:|
| K=10 | 128 | 107 | 83.6% | 55.5% | 65.6% | -5.26% | -6.47% |
| K=20 | 128 | 115 | 89.8% | 53.1% | 67.2% | -5.55% | -7.12% |
| K=30 | 128 | 110 | 85.9% | 47.7% | 69.5% | -4.96% | -6.02% |
- (K-gran subset cells: A1-DEEP, A1-SIFT, A1-SSN, A2-Fig7, A2-Fig9, A5-scale-sf1, A5-scale-sf10, A5-scale-sf100)

## 6. CaseA_vs_B1 — 완전 대체 실험군 (negative control)

### 6.1 selectivity 별
| sel | n | better% | 유의% | mean Δ% | median Δ% |
|---|--:|--:|--:|--:|--:|
| 0.001 | 448 | 23.0% | 0.7% | +11.52% | +3.70% |
| 0.01 | 628 | 38.9% | 2.7% | +21.64% | +1.79% |
| 0.1 | 432 | 42.6% | 19.2% | +1.62% | +0.16% |

### 6.2 method 별 (mean Δ% 오름차순) — 완전 대체의 불안정성
| method | paradigm | n | better% | mean Δ% | mean(outlier제외) | median Δ% |
|---|---|--:|--:|--:|--:|--:|
| hilbert_real | P2 | 95 | 62.1% | -0.42% | -0.42% | -1.05% |
| ica_fastica | P4 | 94 | 60.6% | +0.03% | +0.03% | -0.35% |
| skilling_hilbert | P2 | 94 | 59.6% | +0.06% | +0.06% | -0.40% |
| chao_weighted | P3 | 95 | 46.3% | +0.22% | +0.22% | +0.09% |
| zorder_morton | P2 | 94 | 56.4% | +0.36% | +0.36% | -0.23% |
| pca1d | P4 | 94 | 53.2% | +0.58% | +0.58% | -0.09% |
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

## 7. CaseA_vs_CaseB — 완전 대체 vs 결합
- n=1508, CaseA better(Δ%<0)=53 (3.5%), mean Δ%=+13.92%, median=+7.02% → CaseB 우위

## 8. CaseB_vs_B1 Top winner / loser (개별 cell×method×sel×K)

### 8.1 Top 8 winner (smallest Δ%)
| cell | method | sel | K | Δ% | p_adj(BH,greater) | Cliff δ |
|---|---|--:|--:|--:|--:|--:|
| A1-SSN | hilbert_real | 0.01 | 10 | -13.60% | 0.0028 | +1.000 |
| A2-Fig9 | skilling_hilbert | 0.01 | 10 | -13.45% | 0.0028 | +1.000 |
| A5-scale-sf10 | skilling_hilbert | 0.01 | 10 | -13.45% | 0.0028 | +1.000 |
| A1-DEEP | hilbert_real | 0.01 | 10 | -13.21% | 0.0028 | +1.000 |
| A5-scale-sf100 | hilbert_real | 0.01 | 10 | -13.21% | 0.0028 | +1.000 |
| A1-SIFT | ica_fastica | 0.01 | 30 | -12.98% | 0.0028 | +1.000 |
| A1-SSN | chao_weighted | 0.01 | 10 | -12.65% | 0.0028 | +0.980 |
| A1-SIFT | zorder_morton | 0.01 | 20 | -12.36% | 0.0028 | +1.000 |

### 8.2 Top 8 loser (largest Δ%)
| cell | method | sel | K | Δ% | p_adj(BH) | Cliff δ |
|---|---|--:|--:|--:|--:|--:|
| A10-DEEP+WIKI-concat-sf10 | minibatch_partial | 0.01 | 20 | +1043.19% | 0.0053 | -0.820 |
| A10-DEEP+WIKI-concat-sf10 | minibatch_partial | 0.001 | 20 | +510.62% | 0.0053 | -1.000 |
| A10-DEEP+WIKI-concat-sf10 | faiss_ivf | 0.001 | 20 | +41.40% | 0.0053 | -1.000 |
| A1-SSN | gmm | 0.001 | 10 | +39.76% | 0.0092 | -0.900 |
| A1-SSN | gmm | 0.001 | 20 | +39.33% | 0.0053 | -1.000 |
| A10-DEEP+WIKI-concat-sf10 | gmm | 0.001 | 20 | +31.48% | 0.0053 | -1.000 |
| A5-scale-sf1-SIFT | gmm | 0.001 | 20 | +31.17% | 0.0053 | -1.000 |
| A10-DEEP+WIKI-concat-sf10 | faiss_ivf | 0.01 | 20 | +29.71% | 0.0053 | -1.000 |

## 9. method별 fit_time / cache_time (분포 파악 비용)
> fit_time_sec·cache_time_sec 는 측정 단위 값(3 mode 공통). B1 mode 1508 측정 기준 method별 집계, fit_time mean 오름차순.
| method | n | fit_time mean | fit_time median | cache_time mean |
|---|--:|--:|--:|--:|
| sparse_rp | 95 | 2.91s | 1.43s | 8.17s |
| mhist2 | 94 | 6.69s | 2.81s | 8.98s |
| rsvd | 94 | 6.85s | 3.08s | 9.37s |
| rabitq_strat | 94 | 8.87s | 3.38s | 9.28s |
| chao_weighted | 95 | 11.03s | 4.25s | 9.79s |
| cum_sqrtf | 94 | 15.26s | 6.75s | 9.87s |
| lavallee_hidiroglou | 94 | 15.57s | 6.92s | 9.58s |
| pca1d | 94 | 15.92s | 6.07s | 8.96s |
| minibatch_partial | 94 | 16.99s | 6.99s | 9.12s |
| faiss_ivf | 94 | 17.75s | 6.80s | 9.53s |
| ica_fastica | 94 | 20.94s | 11.74s | 8.47s |
| zorder_morton | 94 | 24.62s | 8.96s | 8.46s |
| gmm | 94 | 29.57s | 18.77s | 9.21s |
| hilbert_real | 95 | 40.66s | 15.31s | 9.24s |
| hyperloglog | 95 | 53.22s | 18.45s | 8.85s |
| skilling_hilbert | 94 | 53.92s | 17.41s | 9.25s |
- cache_time (전 1508 측정): 평균 9.13s · 중앙값 2.88s
