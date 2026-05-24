# phase2 4-way latency 측정 — aggregate summary (2026-05-24 02:47 KST)

- cells: **2** (paired matched)

- variants: ['B1/-', 'CaseA/mean', 'CaseB/chao_weighted', 'CaseB/cum_sqrtf', 'CaseB/hilbert_real', 'CaseB/hyperloglog', 'CaseB/ica_fastica', 'CaseB/lavallee_hidiroglou', 'CaseB/mhist2', 'CaseB/pca1d', 'CaseB/rabitq_strat', 'CaseB/rsvd', 'CaseB/skilling_hilbert', 'CaseB/sparse_rp', 'CaseB/zorder_morton', 'CaseC/-', 'baseline/-', 'oracle/-']

- 출처: phase2 4-way launch 5/24


## 1. variant 별 cell-level trim latency 평균

| variant                   |    mean |   median |   std |     min |     max |   count |
|:--------------------------|--------:|---------:|------:|--------:|--------:|--------:|
| CaseB/hilbert_real        |  888.45 |   888.45 | 25.32 |  870.55 |  906.36 |       2 |
| CaseC/-                   |  889.25 |   889.25 | 22.88 |  873.07 |  905.43 |       2 |
| CaseB/rabitq_strat        |  893.6  |   893.6  | 25.59 |  875.51 |  911.7  |       2 |
| CaseB/mhist2              |  894.25 |   894.25 | 17.16 |  882.12 |  906.38 |       2 |
| CaseB/cum_sqrtf           |  895.3  |   895.3  | 22.46 |  879.42 |  911.18 |       2 |
| CaseB/chao_weighted       |  896    |   896    | 18.98 |  882.58 |  909.42 |       2 |
| B1/-                      |  899.11 |   899.11 | 13.71 |  889.41 |  908.8  |       2 |
| CaseB/hyperloglog         |  899.33 |   899.33 | 12.81 |  890.28 |  908.39 |       2 |
| CaseB/sparse_rp           |  899.81 |   899.81 |  0.76 |  899.27 |  900.35 |       2 |
| CaseB/skilling_hilbert    |  900.3  |   900.3  |  7.55 |  894.96 |  905.64 |       2 |
| CaseB/zorder_morton       |  900.55 |   900.55 |  9.97 |  893.5  |  907.59 |       2 |
| CaseB/rsvd                |  902.91 |   902.91 |  7.37 |  897.7  |  908.12 |       2 |
| oracle/-                  |  903.72 |   903.72 | 12.64 |  894.77 |  912.66 |       2 |
| CaseB/lavallee_hidiroglou |  903.8  |   903.8  |  4.66 |  900.51 |  907.1  |       2 |
| CaseA/mean                |  904.69 |   904.69 |  0.79 |  904.13 |  905.25 |       2 |
| CaseB/pca1d               |  908.44 |   908.44 | 21.4  |  893.31 |  923.57 |       2 |
| CaseB/ica_fastica         |  938.63 |   938.63 | 71.44 |  888.11 |  989.15 |       2 |
| baseline/-                | 5443.07 |  5443.07 |  3.05 | 5440.92 | 5445.23 |       2 |

## 2. paired Δ% vs B1 (대조군)

> Δ% = (variant_exec − B1_exec) / B1_exec × 100. 음수 = variant 더 빠름.

> cell-level matched (같은 cell 안 paired).


| variant                   |   n_cells |   delta_pct_mean |   delta_pct_median |   delta_pct_std |   delta_pct_min |   delta_pct_max |   n_faster |   n_slower |
|:--------------------------|----------:|-----------------:|-------------------:|----------------:|----------------:|----------------:|-----------:|-----------:|
| CaseB/hilbert_real        |         2 |           -1.195 |             -1.195 |           1.309 |          -2.121 |          -0.269 |          2 |          0 |
| CaseC/-                   |         2 |           -1.104 |             -1.104 |           1.036 |          -1.837 |          -0.372 |          2 |          0 |
| CaseB/rabitq_strat        |         2 |           -0.622 |             -0.622 |           1.331 |          -1.564 |           0.319 |          1 |          1 |
| CaseB/mhist2              |         2 |           -0.544 |             -0.544 |           0.391 |          -0.82  |          -0.267 |          2 |          0 |
| CaseB/cum_sqrtf           |         2 |           -0.431 |             -0.431 |           0.979 |          -1.124 |           0.261 |          1 |          1 |
| CaseB/chao_weighted       |         2 |           -0.35  |             -0.35  |           0.591 |          -0.768 |           0.068 |          1 |          1 |
| CaseB/hyperloglog         |         2 |            0.026 |              0.026 |           0.101 |          -0.046 |           0.097 |          1 |          1 |
| CaseB/sparse_rp           |         2 |            0.09  |              0.09  |           1.611 |          -1.049 |           1.229 |          1 |          1 |
| CaseB/skilling_hilbert    |         2 |            0.138 |              0.138 |           0.687 |          -0.348 |           0.624 |          1 |          1 |
| CaseB/zorder_morton       |         2 |            0.163 |              0.163 |           0.419 |          -0.133 |           0.46  |          1 |          1 |
| CaseB/rsvd                |         2 |            0.428 |              0.428 |           0.712 |          -0.075 |           0.932 |          1 |          1 |
| oracle/-                  |         2 |            0.513 |              0.513 |           0.126 |           0.424 |           0.603 |          0 |          2 |
| CaseB/lavallee_hidiroglou |         2 |            0.53  |              0.53  |           1.014 |          -0.187 |           1.247 |          1 |          1 |
| CaseA/mean                |         2 |            0.633 |              0.633 |           1.623 |          -0.514 |           1.781 |          1 |          1 |
| CaseB/pca1d               |         2 |            1.031 |              1.031 |           0.839 |           0.438 |           1.625 |          0 |          2 |
| CaseB/ica_fastica         |         2 |            4.347 |              4.347 |           6.355 |          -0.147 |           8.84  |          1 |          1 |
| baseline/-                |         2 |          505.458 |            505.458 |           9.572 |         498.69  |         512.227 |          0 |          2 |

## 3. ★ CaseC 가설 검증

- CaseC vs B1 paired Δ% mean = -1.10% (median -1.10%, std 1.04)

- 빠른 cells: 2/2, 느린 cells: 0/2

- 해석: |Δ%| < 2% → ★ CaseC 도 engine 에서 동등 (B1·CaseB·CaseC 모두 ≈ 평균 효과 가설 지지)


## 4. injection sanity

| variant                   |   sum |   count |   fired_rate |
|:--------------------------|------:|--------:|-------------:|
| B1/-                      |     2 |       2 |            1 |
| CaseA/mean                |     2 |       2 |            1 |
| CaseB/chao_weighted       |     2 |       2 |            1 |
| CaseB/cum_sqrtf           |     2 |       2 |            1 |
| CaseB/hilbert_real        |     2 |       2 |            1 |
| CaseB/hyperloglog         |     2 |       2 |            1 |
| CaseB/ica_fastica         |     2 |       2 |            1 |
| CaseB/lavallee_hidiroglou |     2 |       2 |            1 |
| CaseB/mhist2              |     2 |       2 |            1 |
| CaseB/pca1d               |     2 |       2 |            1 |
| CaseB/rabitq_strat        |     2 |       2 |            1 |
| CaseB/rsvd                |     2 |       2 |            1 |
| CaseB/skilling_hilbert    |     2 |       2 |            1 |
| CaseB/sparse_rp           |     2 |       2 |            1 |
| CaseB/zorder_morton       |     2 |       2 |            1 |
| CaseC/-                   |     2 |       2 |            1 |
| oracle/-                  |     2 |       2 |            1 |