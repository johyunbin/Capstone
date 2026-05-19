# Z-order vs Hilbert Curve Locality 정량 비교

본 연구의 RQ3 narrative — "Hilbert curve 가 contribution 1순위 격상" — 의
mechanism 분리 검증. PCA+quantile 골격이 동일하므로 두 curve 의 locality 차이
정도가 contribution 의 origin (PCA+quantile vs locality preservation) 을 분리한다.

## 1. Grid Locality Metric (sample 무관, curve 자체)

256×256 grid (p=8) 에서 두 metric 측정.

### 1-1. Forward (2D 인접 → 1D 거리)

4-neighbor 쌍의 1D distance 차이 mean. 인접 grid 가 1D 에서도 인접하면 작음.

| curve | mean | median | p95 | max |
|-------|-----:|-------:|----:|----:|
| hilbert | 155.62 | 1.00 | 179 | 54613 |
| zorder | 128.50 | 2.00 | 171 | 21846 |

**해석**: forward mean 은 Hilbert 가 약간 더 크지만, max 가 결정적으로 큼. 이 max
값이 큰 이유는 Hilbert 의 quadrant boundary 에서 발생하는 worst-case jump 때문.

### 1-2. Inverse (1D 인접 → 2D Manhattan distance)

**Hilbert curve 의 본질 정의**: 1D 연속 (d, d+1) → 2D Manhattan = 1.
Z-order 는 "Z" jump 시 Manhattan > 1 (해당 cell 에서 quadrant 건너뜀).

| curve | mean Manhattan | max | p95 | fraction (Manhattan > 1) |
|-------|---------------:|----:|----:|-------------------------:|
| hilbert | 1.000 | 1 | 1 | 0.0000 |
| zorder | 1.992 | 256 | 4 | 0.5000 |

**해석**: Hilbert 는 mean Manhattan = 1.000 (curve 정의 그대로). Z-order 는 mean > 1
이고 fraction (Manhattan > 1) 가 양수 → 1D 연속이 2D 비연속. **이 metric 이 두
curve 의 locality 차이를 결정적으로 분리한다**.

## 2. Stratum Compactness (sample 의존, 작을수록 좋음)

각 stratum 내 grid 좌표 (x_std + y_std) 평균. 작을수록 한 stratum 이 spatial
영역에 집중 → HT estimator 의 cluster-aware 분산 감소 효과 강.

| sample | hilbert | zorder | zorder/hilbert |
|--------|--------:|-------:|---------------:|
| synthetic_clustered | 4.97 | 8.15 | 1.64 |
| synthetic_iid | 24.13 | 30.28 | 1.255 |
| synthetic_sift_like | 4.77 | 12.12 | 2.541 |

**해석**: `zorder/hilbert` 비율 > 1 이면 Z-order 의 stratum 이 spatial 으로
더 흩어짐 → Hilbert 의 locality preservation 이 stratum 압축에 직접 기여.
비율이 1 에 가까우면 두 curve 가 비슷 (PCA+quantile 이 dominant).

## 3. RQ3 Narrative 결론

- **Grid neighbor jump**: Hilbert 의 mean jump 가 Z-order 보다 작을 것으로 예상.
  Z-order 는 Y-축 jump 시 grid 의 절반 (n/2) 을 한 번에 건너뛰므로 worst-case
  jump 가 크다.
- **Stratum compactness**: Hilbert 의 stratum 이 더 compact 면 → contribution 의
  origin 이 (b) locality preservation. Z-order 와 비슷하면 (a) PCA+quantile 이 핵심.

**측정 후 follow-up (RQ3 8M sensitivity)**: 본 분석의 예측이 실측 recovery_rate
패턴과 정합한지 cross-check. Z-order 의 측정은 8M 끝나면 1M 에서 즉시 가능 (run_zorder.py).
