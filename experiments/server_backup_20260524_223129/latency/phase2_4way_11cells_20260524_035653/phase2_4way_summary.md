# phase2 4-way latency 측정 — aggregate summary (2026-05-24 03:56 KST)

- cells: **11** (paired matched)

- variants: ['B1/-', 'CaseA/mean', 'CaseB/chao_weighted', 'CaseB/cum_sqrtf', 'CaseB/hilbert_real', 'CaseB/hyperloglog', 'CaseB/ica_fastica', 'CaseB/lavallee_hidiroglou', 'CaseB/mhist2', 'CaseB/pca1d', 'CaseB/rabitq_strat', 'CaseB/rsvd', 'CaseB/skilling_hilbert', 'CaseB/sparse_rp', 'CaseB/zorder_morton', 'CaseC/-', 'baseline/-', 'oracle/-']

- 출처: phase2 4-way launch 5/24


## 1. variant 별 cell-level trim latency 평균

| variant                   |    mean |   median |     std |     min |     max |   count |
|:--------------------------|--------:|---------:|--------:|--------:|--------:|--------:|
| CaseB/rabitq_strat        |  844.61 |   847.4  |   46.55 |  770.47 |  911.7  |      11 |
| CaseB/cum_sqrtf           |  848.12 |   846.69 |   45.79 |  762.81 |  911.18 |      11 |
| CaseB/zorder_morton       |  848.74 |   851.68 |   45.29 |  770.75 |  907.59 |      11 |
| B1/-                      |  848.94 |   850.36 |   44.17 |  780.42 |  908.8  |      11 |
| CaseB/chao_weighted       |  849.42 |   846.42 |   43.55 |  779.88 |  909.42 |      11 |
| CaseB/lavallee_hidiroglou |  849.62 |   848.86 |   46.81 |  773.81 |  907.1  |      11 |
| CaseB/rsvd                |  851.32 |   846    |   42.03 |  782.68 |  908.12 |      11 |
| oracle/-                  |  851.36 |   841.19 |   43.13 |  778.56 |  912.66 |      11 |
| CaseA/mean                |  851.41 |   848.4  |   45.36 |  781.93 |  905.25 |      11 |
| CaseC/-                   |  851.51 |   851.75 |   40.13 |  786.54 |  905.43 |      11 |
| CaseB/mhist2              |  851.64 |   848.3  |   41.22 |  782.98 |  906.38 |      11 |
| CaseB/sparse_rp           |  851.75 |   857.86 |   42.69 |  778.99 |  900.35 |      11 |
| CaseB/pca1d               |  851.99 |   844.88 |   44.77 |  773.09 |  923.57 |      11 |
| CaseB/hyperloglog         |  851.99 |   851.55 |   43.02 |  782.63 |  908.39 |      11 |
| CaseB/hilbert_real        |  852.09 |   847.7  |   40.22 |  781.29 |  906.36 |      11 |
| CaseB/skilling_hilbert    |  853.39 |   845.33 |   42.79 |  783.81 |  905.64 |      11 |
| CaseB/ica_fastica         |  859.56 |   844.15 |   56.96 |  780.96 |  989.15 |      11 |
| baseline/-                | 4346.73 |  5138.95 | 1769.41 | 1589.35 | 5646.11 |      11 |

## 2. paired Δ% vs B1 (대조군)

> Δ% = (variant_exec − B1_exec) / B1_exec × 100. 음수 = variant 더 빠름.

> cell-level matched (같은 cell 안 paired).


| variant                   |   n_cells |   delta_pct_mean |   delta_pct_median |   delta_pct_std |   delta_pct_min |   delta_pct_max |   n_faster |   n_slower |
|:--------------------------|----------:|-----------------:|-------------------:|----------------:|----------------:|----------------:|-----------:|-----------:|
| CaseB/rabitq_strat        |        11 |           -0.524 |             -0.282 |           0.659 |          -1.564 |           0.319 |          8 |          3 |
| CaseB/cum_sqrtf           |        11 |           -0.1   |             -0.431 |           1.365 |          -2.256 |           3.262 |          6 |          5 |
| CaseB/zorder_morton       |        11 |           -0.028 |             -0.126 |           0.854 |          -1.289 |           1.285 |          6 |          5 |
| CaseB/lavallee_hidiroglou |        11 |            0.067 |             -0.176 |           0.656 |          -0.846 |           1.247 |          6 |          5 |
| CaseB/chao_weighted       |        11 |            0.069 |             -0.069 |           1.432 |          -1.587 |           3.699 |          6 |          5 |
| CaseA/mean                |        11 |            0.293 |             -0.231 |           1.357 |          -1.352 |           3.2   |          6 |          5 |
| oracle/-                  |        11 |            0.297 |              0.424 |           1.109 |          -1.078 |           2.841 |          5 |          6 |
| CaseB/rsvd                |        11 |            0.297 |             -0.075 |           1.022 |          -0.652 |           2.802 |          6 |          5 |
| CaseC/-                   |        11 |            0.332 |              0.163 |           1.278 |          -1.837 |           3.505 |          4 |          7 |
| CaseB/mhist2              |        11 |            0.341 |              0.083 |           1.289 |          -0.82  |           3.929 |          4 |          7 |
| CaseB/sparse_rp           |        11 |            0.347 |              0.273 |           1.331 |          -1.429 |           3.509 |          5 |          6 |
| CaseB/pca1d               |        11 |            0.366 |              0.438 |           1.446 |          -1.88  |           2.883 |          4 |          7 |
| CaseB/hyperloglog         |        11 |            0.373 |              0.239 |           1.151 |          -1.624 |           2.448 |          3 |          8 |
| CaseB/hilbert_real        |        11 |            0.4   |              0.429 |           1.309 |          -2.121 |           3.319 |          4 |          7 |
| CaseB/skilling_hilbert    |        11 |            0.538 |              0.434 |           1.095 |          -0.591 |           3.179 |          4 |          7 |
| CaseB/ica_fastica         |        11 |            1.211 |              0.235 |           2.687 |          -0.73  |           8.84  |          4 |          7 |
| baseline/-                |        11 |          405.629 |            480.163 |         198.298 |          98.206 |         591.729 |          0 |         11 |

## 3. ★ CaseC 가설 검증

- CaseC vs B1 paired Δ% mean = 0.33% (median 0.16%, std 1.28)

- 빠른 cells: 4/11, 느린 cells: 7/11

- 해석: |Δ%| < 2% → ★ CaseC 도 engine 에서 동등 (B1·CaseB·CaseC 모두 ≈ 평균 효과 가설 지지)


## 4. injection sanity

| variant                   |   sum |   count |   fired_rate |
|:--------------------------|------:|--------:|-------------:|
| B1/-                      |    11 |      11 |            1 |
| CaseA/mean                |    11 |      11 |            1 |
| CaseB/chao_weighted       |    11 |      11 |            1 |
| CaseB/cum_sqrtf           |    11 |      11 |            1 |
| CaseB/hilbert_real        |    11 |      11 |            1 |
| CaseB/hyperloglog         |    11 |      11 |            1 |
| CaseB/ica_fastica         |    11 |      11 |            1 |
| CaseB/lavallee_hidiroglou |    11 |      11 |            1 |
| CaseB/mhist2              |    11 |      11 |            1 |
| CaseB/pca1d               |    11 |      11 |            1 |
| CaseB/rabitq_strat        |    11 |      11 |            1 |
| CaseB/rsvd                |    11 |      11 |            1 |
| CaseB/skilling_hilbert    |    11 |      11 |            1 |
| CaseB/sparse_rp           |    11 |      11 |            1 |
| CaseB/zorder_morton       |    11 |      11 |            1 |
| CaseC/-                   |    11 |      11 |            1 |
| oracle/-                  |    11 |      11 |            1 |