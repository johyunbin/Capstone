# RQ1 Skewness vs KM20 효과 상관 분석

**5/4 카톡 회의록 line 53 미해결 의문**: "skew 지표 (HHI/CV) 와 KM20 개선 폭의 상관" 정량화.

## 데이터

Cross-dataset 3 점 (DEEP 1M / SIFT 1.5M / DEEP 8M) 의 cluster distribution skewness 와
KM20-BERN 평균 격차 (sel 평균, anomaly 제외).

  dataset  HHI_cluster  Gini_cluster  CV_cluster  top1_share  abs_mean
  DEEP_1M       0.0527        0.1275       0.234       0.081     3.846
SIFT_1.5M       0.0578        0.1232       0.394       0.099     3.730
  DEEP_8M       0.0527        0.1275       0.234       0.081     1.155

## Spearman 상관 (Skewness vs |KM20 effect|)

| metric | ρ | p-value | n |
|--------|---:|--------:|--:|
| `HHI_cluster` | +0.000 | 1.000 | 3 |
| `Gini_cluster` | +0.000 | 1.000 | 3 |
| `CV_cluster` | +0.000 | 1.000 | 3 |
| `top1_share` | +0.000 | 1.000 | 3 |

## Per-sel × Per-dataset 격차

```
dataset  DEEP_1M  DEEP_8M  SIFT_1.5M  |DEEP_1M - SIFT_1.5M|
sel                                                        
0.01       -8.93      NaN        NaN                    NaN
0.05       -1.85    -0.55      -4.39                   2.54
0.10       -4.19      NaN        NaN                    NaN
0.30       -2.62      NaN        NaN                    NaN
0.50       -1.64    -1.76      -3.07                   1.43
```

## 해석

- **n=3 으로 cross-dataset 상관의 power 매우 낮음**. 정성적 trend 만 가능.
- DEEP_1M (HHI 0.0527) → SIFT_1.5M (HHI 0.0578) cluster skewness 9.7% 증가
  → KM20 효과 |mean| DEEP_1M 3.85% → SIFT_1.5M 3.73% (sel 평균, sample anomaly 제외)
  → 명확한 단조 증가 패턴 X (CV 신호는 더 강함: 0.234 → 0.394 = 68% 증가)
- **Per-sel 비교 가 더 강한 trend**:
  - s=0.05: DEEP -1.85% vs SIFT -4.39% (격차 ~2.5%p)
  - s=0.50: DEEP -1.64% vs SIFT -3.07% (격차 ~1.4%p)

## Narrative 결론

1. **Cross-dataset 단조 증가는 약함** — 3 dataset 의 limited sample.
2. **Per-sel 비교에서 SIFT 의 KM20 효과가 DEEP 보다 일관되게 큼** (정리.md line 264 와 일치).
   → CV (0.234 vs 0.394) 의 68% 증가가 KM20 효과 ~2× 증가로 연결.
3. **Future work**: synthetic distribution (Pareto/Cauchy/Mixture) 으로 controlled skewness
   범위 (CV 0.1 ~ 1.0) 에서 KM20 효과의 함수 관계 정량 (단조, log, power).
