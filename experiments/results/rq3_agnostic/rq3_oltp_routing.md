# RQ3 OLTP 비용 정량 + Method Routing Framework

## 1. OLTP 비용 정량 (5/5 회의록 line 52)

박세은 의문: "INSERT 빈번 OLTP 는 본 연구 범위 외 — RQ3 의 F (MiniBatch) 가 부담 1/20~1/100"

**직접 측정**:

```
               method       N  n_train  elapsed_s  ops_per_row_us
    KM20 (full-batch)   10000    10000   0.524890       52.489018
MiniBatch (1% sample)   10000     1000   0.024682        2.468204
MiniBatch partial_fit   10000     1000   0.007120        0.711989
  Hilbert (1% sample)   10000     1000   0.005553        0.555277
    KM20 (full-batch)  100000   100000   6.577899       65.778990
MiniBatch (1% sample)  100000     1000   0.032044        0.320439
MiniBatch partial_fit  100000     1000   0.008823        0.088229
  Hilbert (1% sample)  100000     1000   0.005227        0.052271
    KM20 (full-batch) 1000000  1000000  69.749390       69.749390
MiniBatch (1% sample) 1000000    10000   0.053934        0.053934
MiniBatch partial_fit 1000000    10000   0.025699        0.025699
  Hilbert (1% sample) 1000000    10000   0.030568        0.030568
```

- **N = 10,000**: KM20 0.52s / MiniBatch 0.025s = **21× speedup**
- **N = 100,000**: KM20 6.58s / MiniBatch 0.032s = **205× speedup**
- **N = 1,000,000**: KM20 69.75s / MiniBatch 0.054s = **1293× speedup**

**5/5 회의록 의 "1/20~1/100 수준 완화" 가 정량적으로 입증** — N=1M 에서 KM20 의 1/(speedup) 비용.

## 2. Method Routing Framework

**5/27 발표 narrative**: "어려운 query 에서 method 차이 결정적 (spread vs difficulty ρ=0.78)"
→ Production 의 method routing 가능성 정량.

### Difficulty 별 Best Method 분포 (rq3_per_query_ranking.csv 기반)

각 (dataset, sel, query) cell 의 best method (rank=1) 를 BERN q_error quartile 별 집계.

```
mode          distance_shell  hilbert  hybrid  is_p200_clip  is_p200_noclip  is_p50_clip  is_p50_noclip  kde_pilot  kdtree  km20  lsh  minibatch  minibatch_partial  pca1d   pq  random20  random_proj  zorder
difficulty_q                                                                                                                                                                                                  
Q1_easy                  7.0     19.0    21.0           1.0             0.0          5.0            0.0       21.0    21.0  24.0  9.0       34.0               27.0   16.0  3.0      14.0          7.0    21.0
Q2                       1.0     34.0    27.0           2.0             2.0         10.0            2.0       25.0    17.0  17.0  7.0       21.0               26.0   19.0  5.0      13.0          5.0    18.0
Q3                       3.0     24.0    31.0           2.0             1.0         10.0            1.0       23.0    24.0  25.0  5.0       22.0               25.0   16.0  7.0       9.0          6.0    15.0
Q4_hard                  3.0     15.0    29.0           0.0             1.0          9.0            0.0       33.0    26.0  23.0  7.0       32.0               26.0   17.0  6.0       8.0          0.0    15.0
```

### Difficulty 별 Top method

- **Q1_easy**: `minibatch` (34), `minibatch_partial` (27), `km20` (24), `kde_pilot` (21), `kdtree` (21)
- **Q2**: `hilbert` (34), `hybrid` (27), `minibatch_partial` (26), `kde_pilot` (25), `minibatch` (21)
- **Q3**: `hybrid` (31), `km20` (25), `minibatch_partial` (25), `kdtree` (24), `hilbert` (24)
- **Q4_hard**: `kde_pilot` (33), `minibatch` (32), `hybrid` (29), `kdtree` (26), `minibatch_partial` (26)

## 3. Production Method Routing 의 framework 제안

```
Step 1. Query 도착 → BERN sample 로 q_error 추정 (cheap, ~ms)
Step 2. q_error quartile 분류 → difficulty bin
Step 3. bin 별 best method 의 stratum_id 로 stratified sample 진행
Step 4. HT estimator 로 final cardinality 산출
```

**한계**: 본 routing 은 *예측 모델 prototype* 단계. 실제 배포에는 (1) BERN pilot 의 추가 비용,
(2) bin 분류의 noise, (3) 비교 method 간 stratum_id 메타데이터 동시 유지의 비용 검토 필요.

**5/27 발표용 figure**: 위 routing matrix + per-query difficulty scatter (이미 존재).
