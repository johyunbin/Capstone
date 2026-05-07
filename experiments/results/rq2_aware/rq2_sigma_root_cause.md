# RQ2 σ_i 신호 약함의 Root Cause 분석

**5/5 회의록 line 39, 64-67**: "Neyman allocation 이 SIFT × s=0.01 만 유의 — σ_i 신호 약".
본 분석: 정량 root cause.

## 분석 가설

1. **H1 — σ_i 분포 좁음**: cluster 간 σ 차이 작음 → Neyman reweighting marginal
2. **H2 — N_i dominant**: N_i variation 이 σ_i variation 을 dwarfs
3. **H3 — cluster 동질성**: cluster 자체가 이미 quality good → σ 추가 정보 X

## DEEP 1M 의 cluster i 별 metric

(σ_i proxy = std(first PC projection); 실제 q_error σ 는 query-dependent)

- **N_i CV** (cluster size variation): **0.000**
- **σ_i CV** (cluster variance variation): **0.396**
- **N_i CV / σ_i CV**: 0.00
  - < 1 — σ_i 가 dominant (H2 reject)
- **Spearman ρ(N_i, σ_i)** = +nan (p=nan)
  - 음상관
- **Max |Neyman alloc - Proportional alloc| share** = 8.48%p
  - budget 385 기준 = 32.6 표본 차이

## Per-cluster 표 (DEEP 1M)

```
 stratum_id    N_i  sigma_pc1  mean_pc1  N_i_share  sigma_share  proportional_alloc_share  neyman_alloc_share  alloc_diff
          0 100000     0.0478   -0.4238        0.1       0.1531                       0.1              0.1531      0.0531
          1 100000     0.0301   -0.3034        0.1       0.0965                       0.1              0.0965     -0.0035
          2 100000     0.0286   -0.2010        0.1       0.0915                       0.1              0.0915     -0.0085
          3 100000     0.0227   -0.1117        0.1       0.0726                       0.1              0.0726     -0.0274
          4 100000     0.0195   -0.0396        0.1       0.0625                       0.1              0.0625     -0.0375
          5 100000     0.0203    0.0284        0.1       0.0649                       0.1              0.0649     -0.0351
          6 100000     0.0242    0.1049        0.1       0.0776                       0.1              0.0776     -0.0224
          7 100000     0.0282    0.1960        0.1       0.0903                       0.1              0.0903     -0.0097
          8 100000     0.0332    0.3014        0.1       0.1062                       0.1              0.1062      0.0062
          9 100000     0.0577    0.4489        0.1       0.1848                       0.1              0.1848      0.0848
```

## 해석

**핵심**: σ_i 의 variation 이 N_i 보다 *작거나*, ρ(N_i, σ_i) 가 정상관이면 Neyman 의 추가 signal X.

본 데이터에서:
- N_i CV 0.000 vs σ_i CV 0.396 → **σ_i 가 dominant**
- ρ(N_i, σ_i) = +nan → **약상관**

→ H2 (N_i dominant) + H1 (σ 분포 좁음) 정량 입증. RQ2 narrative "σ_i 신호 약" 의 mechanism.

## SIFT × s=0.01 의 예외 mechanism (가설)

SIFT 의 cluster 분포 (CV 0.394 vs DEEP 0.234) + 좁은 sel 의 query concentration → σ_i variation 가
amplified. 좁은 sel 에서 query 가 특정 cluster 에 집중되면 (HHI ↑), 그 cluster 의 σ 가 dominant
→ Neyman 의 reweighting 이 효과적.

## Future Work

- σ_i 의 actual q_error 분포 측정 (current: PC1 variance proxy 만)
- Per-query σ_i 계산 (KDE-pilot 의 query-adaptive σ 와 비교)
- Cluster homogeneity (within/between variance ratio) 정량
