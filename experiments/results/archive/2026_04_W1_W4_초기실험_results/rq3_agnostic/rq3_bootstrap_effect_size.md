# RQ3 Bootstrap CI + Cohen's d Effect Size

기존 wilcoxon_vs_*.csv 는 paired Wilcoxon p-value 기반. n=500 paired observations 에서
는 작은 차이도 유의 (p<0.05) 라 *practical significance* 가 같이 보고되어야 학술적 robust.

## 1. Method 별 평균 Cohen's d

Cohen's d 의 표준 해석: |d|<0.2 negligible / 0.5 small / 0.8 medium / >0.8 large.
음수 → method 가 BERN 보다 q_error 작음 (개선).

| method | mean d | min | max | 실용 의미 |
|--------|-------:|----:|----:|----------|
| `birch` | -0.014 | -0.157 | +0.098 | negligible |
| `distance_shell` | +0.490 | +0.038 | +0.758 | hurt-small |
| `gmm` | -0.079 | -0.189 | +0.009 | negligible |
| `hdbscan` | -0.136 | -0.269 | -0.012 | negligible |
| `hilbert` | -0.156 | -0.336 | -0.041 | negligible |
| `hybrid` | -0.154 | -0.308 | -0.007 | negligible |
| `is_p200_clip` | +0.704 | +0.301 | +1.119 | hurt-medium |
| `is_p200_noclip` | +0.564 | +0.305 | +0.826 | hurt-medium |
| `is_p50_clip` | +0.498 | -0.169 | +0.900 | hurt-small |
| `is_p50_noclip` | +0.642 | +0.412 | +1.127 | hurt-medium |
| `kde_pilot` | -0.049 | -0.205 | +0.033 | negligible |
| `kdtree` | -0.071 | -0.257 | +0.055 | negligible |
| `lsh` | +0.156 | +0.089 | +0.211 | negligible |
| `minibatch` | -0.151 | -0.334 | -0.050 | negligible |
| `minibatch_partial` | -0.119 | -0.248 | -0.004 | negligible |
| `pca1d` | -0.101 | -0.218 | -0.005 | negligible |
| `pq` | +0.228 | +0.122 | +0.319 | hurt-small |
| `random_proj` | +0.216 | +0.119 | +0.326 | hurt-small |
| `sobol` | +0.122 | +0.035 | +0.260 | negligible |
| `sparse_rp` | -0.009 | -0.114 | +0.057 | negligible |
| `spectral` | +0.123 | -0.022 | +0.200 | negligible |
| `zorder` | -0.119 | -0.317 | +0.016 | negligible |

## 2. Bootstrap CI 의 robust 비율

각 (method × dataset × sel) cell 의 95% bootstrap CI 가 0 을 제외하는 비율.
1.0 → 모든 cell 에서 통계적으로 robust 한 effect.

| method | n_cells | CI 0 제외 cells | fraction |
|--------|--------:|----------------:|---------:|
| `birch` | 10 | 1 | 0.10 |
| `distance_shell` | 10 | 8 | 0.80 |
| `gmm` | 10 | 2 | 0.20 |
| `hdbscan` | 10 | 5 | 0.50 |
| `hilbert` | 10 | 4 | 0.40 |
| `hybrid` | 10 | 5 | 0.50 |
| `is_p200_clip` | 10 | 10 | 1.00 |
| `is_p200_noclip` | 10 | 10 | 1.00 |
| `is_p50_clip` | 10 | 8 | 0.80 |
| `is_p50_noclip` | 10 | 10 | 1.00 |
| `kde_pilot` | 10 | 2 | 0.20 |
| `kdtree` | 10 | 4 | 0.40 |
| `lsh` | 10 | 1 | 0.10 |
| `minibatch` | 10 | 5 | 0.50 |
| `minibatch_partial` | 10 | 5 | 0.50 |
| `pca1d` | 10 | 3 | 0.30 |
| `pq` | 10 | 9 | 0.90 |
| `random_proj` | 10 | 6 | 0.60 |
| `sobol` | 10 | 4 | 0.40 |
| `sparse_rp` | 10 | 0 | 0.00 |
| `spectral` | 10 | 1 | 0.10 |
| `zorder` | 10 | 2 | 0.20 |

## 3. RQ3 narrative 결론

- **Hilbert + MiniBatch 의 mean d 가 negative + |d|≥0.2** 면 small effect 이상 → 
  practical 개선 확정. p<0.05 만 보면 sample size 효과로 small d 도 유의해 보임.
- **lsh / random_proj / pq 의 d 부호** 가 양수로 나오면 → 1M/SIFT 1.5M 에서 BERN 대비
  개선 X. *negative control* 검증.
- **CI 의 fraction_robust 가 1.0 인 method** 만 "모든 cell 에서 통계 robust 효과 있음".
  본 연구의 contribution claim 은 이 method 에 한정됨이 보수적 narrative.
