# phase2 4-way latency 측정 — aggregate summary (2026-05-24 04:03 KST)

- cells: **12** (paired matched)

- variants: ['B1/-', 'CaseA/mean', 'CaseB/chao_weighted', 'CaseB/cum_sqrtf', 'CaseB/hilbert_real', 'CaseB/hyperloglog', 'CaseB/ica_fastica', 'CaseB/lavallee_hidiroglou', 'CaseB/mhist2', 'CaseB/pca1d', 'CaseB/rabitq_strat', 'CaseB/rsvd', 'CaseB/skilling_hilbert', 'CaseB/sparse_rp', 'CaseB/zorder_morton', 'CaseC/-', 'baseline/-', 'oracle/-']

- 출처: phase2 4-way launch 5/24


## 1. variant 별 cell-level trim latency 평균

| variant                   |    mean |   median |     std |     min |     max |   count |
|:--------------------------|--------:|---------:|--------:|--------:|--------:|--------:|
| CaseB/rabitq_strat        |  850.97 |   858.96 |   49.55 |  770.47 |  920.92 |      12 |
| oracle/-                  |  856.48 |   855.13 |   44.78 |  778.56 |  912.77 |      12 |
| CaseB/mhist2              |  856.75 |   859.89 |   43.11 |  782.98 |  913.03 |      12 |
| CaseB/rsvd                |  856.82 |   858.43 |   44.36 |  782.68 |  917.27 |      12 |
| CaseA/mean                |  857.16 |   866.54 |   47.61 |  781.93 |  920.4  |      12 |
| CaseB/cum_sqrtf           |  860.79 |   856.38 |   61.91 |  762.81 | 1000.16 |      12 |
| B1/-                      |  861.33 |   860.17 |   60.13 |  780.42 |  997.6  |      12 |
| CaseB/lavallee_hidiroglou |  861.88 |   863.48 |   61.6  |  773.81 |  996.69 |      12 |
| CaseB/chao_weighted       |  862    |   863.58 |   60.19 |  779.88 | 1000.38 |      12 |
| CaseB/zorder_morton       |  862.22 |   865.63 |   63.62 |  770.75 | 1010.56 |      12 |
| CaseC/-                   |  863.68 |   862.36 |   56.93 |  786.54 |  997.51 |      12 |
| CaseB/sparse_rp           |  863.74 |   862.96 |   58.15 |  778.99 |  995.57 |      12 |
| CaseB/pca1d               |  864.15 |   861.44 |   59.96 |  773.09 |  997.82 |      12 |
| CaseB/hyperloglog         |  864.19 |   868.35 |   58.9  |  782.63 |  998.4  |      12 |
| CaseB/hilbert_real        |  864.41 |   859.12 |   57.39 |  781.29 |  999.98 |      12 |
| CaseB/skilling_hilbert    |  865.48 |   863.91 |   58.46 |  783.81 |  998.43 |      12 |
| CaseB/ica_fastica         |  870.88 |   863.39 |   66.98 |  780.96 |  995.37 |      12 |
| baseline/-                | 4445.65 |  5289.93 | 1721.52 | 1589.35 | 5646.11 |      12 |

## 2. paired Δ% vs B1 (대조군)

> Δ% = (variant_exec − B1_exec) / B1_exec × 100. 음수 = variant 더 빠름.

> cell-level matched (같은 cell 안 paired).


| variant                   |   n_cells |   delta_pct_mean |   delta_pct_median |   delta_pct_std |   delta_pct_min |   delta_pct_max |   n_faster |   n_slower |
|:--------------------------|----------:|-----------------:|-------------------:|----------------:|----------------:|----------------:|-----------:|-----------:|
| CaseB/rabitq_strat        |        12 |           -1.12  |             -0.315 |           2.161 |          -7.687 |           0.319 |          9 |          3 |
| oracle/-                  |        12 |           -0.436 |              0.16  |           2.752 |          -8.503 |           2.841 |          6 |          6 |
| CaseB/rsvd                |        12 |           -0.399 |             -0.076 |           2.6   |          -8.052 |           2.802 |          7 |          5 |
| CaseB/mhist2              |        12 |           -0.394 |              0.066 |           2.827 |          -8.478 |           3.929 |          5 |          7 |
| CaseA/mean                |        12 |           -0.377 |             -0.254 |           2.655 |          -7.739 |           3.2   |          7 |          5 |
| CaseB/cum_sqrtf           |        12 |           -0.07  |             -0.19  |           1.306 |          -2.256 |           3.262 |          6 |          6 |
| CaseB/lavallee_hidiroglou |        12 |            0.054 |             -0.134 |           0.628 |          -0.846 |           1.247 |          7 |          5 |
| CaseB/zorder_morton       |        12 |            0.082 |              0.014 |           0.9   |          -1.289 |           1.299 |          6 |          6 |
| CaseB/chao_weighted       |        12 |            0.086 |             -0     |           1.367 |          -1.587 |           3.699 |          6 |          6 |
| CaseB/sparse_rp           |        12 |            0.301 |              0.045 |           1.279 |          -1.429 |           3.509 |          6 |          6 |
| CaseC/-                   |        12 |            0.303 |              0.106 |           1.222 |          -1.837 |           3.505 |          5 |          7 |
| CaseB/pca1d               |        12 |            0.338 |              0.282 |           1.382 |          -1.88  |           2.883 |          4 |          8 |
| CaseB/hyperloglog         |        12 |            0.348 |              0.19  |           1.101 |          -1.624 |           2.448 |          3 |          9 |
| CaseB/hilbert_real        |        12 |            0.386 |              0.333 |           1.248 |          -2.121 |           3.319 |          4 |          8 |
| CaseB/skilling_hilbert    |        12 |            0.5   |              0.263 |           1.053 |          -0.591 |           3.179 |          4 |          8 |
| CaseB/ica_fastica         |        12 |            1.092 |              0.152 |           2.595 |          -0.73  |           8.84  |          5 |          7 |
| baseline/-                |        12 |          409.719 |            477.483 |         189.599 |          98.206 |         591.729 |          0 |         12 |

## 3. ★ CaseC 가설 검증

- CaseC vs B1 paired Δ% mean = 0.30% (median 0.11%, std 1.22)

- 빠른 cells: 5/12, 느린 cells: 7/12

- 해석: |Δ%| < 2% → ★ CaseC 도 engine 에서 동등 (B1·CaseB·CaseC 모두 ≈ 평균 효과 가설 지지)


## 4. injection sanity

| variant                   |   sum |   count |   fired_rate |
|:--------------------------|------:|--------:|-------------:|
| B1/-                      |    12 |      12 |            1 |
| CaseA/mean                |    12 |      12 |            1 |
| CaseB/chao_weighted       |    12 |      12 |            1 |
| CaseB/cum_sqrtf           |    12 |      12 |            1 |
| CaseB/hilbert_real        |    12 |      12 |            1 |
| CaseB/hyperloglog         |    12 |      12 |            1 |
| CaseB/ica_fastica         |    12 |      12 |            1 |
| CaseB/lavallee_hidiroglou |    12 |      12 |            1 |
| CaseB/mhist2              |    12 |      12 |            1 |
| CaseB/pca1d               |    12 |      12 |            1 |
| CaseB/rabitq_strat        |    12 |      12 |            1 |
| CaseB/rsvd                |    12 |      12 |            1 |
| CaseB/skilling_hilbert    |    12 |      12 |            1 |
| CaseB/sparse_rp           |    12 |      12 |            1 |
| CaseB/zorder_morton       |    12 |      12 |            1 |
| CaseC/-                   |    12 |      12 |            1 |
| oracle/-                  |    12 |      12 |            1 |