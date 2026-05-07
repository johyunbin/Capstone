# RQ3 OLTP 비용 정량 + Method Routing Framework

## 1. OLTP 비용 정량 (5/5 회의록 line 52)

박세은 의문: "INSERT 빈번 OLTP 는 본 연구 범위 외 — RQ3 의 F (MiniBatch) 가 부담 1/20~1/100"

**직접 측정**:

```
               method       N  n_train  elapsed_s  ops_per_row_us
    KM20 (full-batch)   10000    10000   0.543081       54.308105
MiniBatch (1% sample)   10000     1000   0.023532        2.353215
MiniBatch partial_fit   10000     1000   0.007745        0.774503
  Hilbert (1% sample)   10000     1000   0.007061        0.706100
    KM20 (full-batch)  100000   100000   6.596969       65.969689
MiniBatch (1% sample)  100000     1000   0.039185        0.391850
MiniBatch partial_fit  100000     1000   0.009421        0.094211
  Hilbert (1% sample)  100000     1000   0.005634        0.056341
    KM20 (full-batch) 1000000  1000000  72.044681       72.044681
MiniBatch (1% sample) 1000000    10000   0.057205        0.057205
MiniBatch partial_fit 1000000    10000   0.024066        0.024066
  Hilbert (1% sample) 1000000    10000   0.030678        0.030678
```

- **N = 10,000**: KM20 0.54s / MiniBatch 0.024s = **23× speedup**
- **N = 100,000**: KM20 6.60s / MiniBatch 0.039s = **168× speedup**
- **N = 1,000,000**: KM20 72.04s / MiniBatch 0.057s = **1259× speedup**

**5/5 회의록 의 "1/20~1/100 수준 완화" 가 정량적으로 입증** — N=1M 에서 KM20 의 1/(speedup) 비용.

## 2. Method Routing Framework

**5/27 발표 narrative**: "어려운 query 에서 method 차이 결정적 (spread vs difficulty ρ=0.78)"
→ Production 의 method routing 가능성 정량.

### Difficulty 별 Best Method 분포 (rq3_per_query_ranking.csv 기반)

각 (dataset, sel, query) cell 의 best method (rank=1) 를 BERN q_error quartile 별 집계.

```
mode          birch  distance_shell   gmm  hdbscan  hilbert  hybrid  is_p200_clip  is_p200_noclip  is_p50_clip  is_p50_noclip  kde_pilot  kdtree  km20  lsh  minibatch  minibatch_partial  pca1d   pq  random20  random_proj  sobol  sparse_rp  spectral  zorder
difficulty_q                                                                                                                                                                                                                                                    
Q1_easy         9.0             4.0  14.0     17.0     13.0    16.0           1.0             0.0          5.0            0.0       19.0    17.0  16.0  6.0       22.0               20.0   12.0  3.0       9.0          5.0   10.0       11.0       6.0    15.0
Q2             13.0             1.0  10.0     18.0     20.0    18.0           2.0             2.0         10.0            2.0       21.0    11.0  14.0  6.0       14.0               19.0   15.0  4.0       9.0          5.0    4.0        8.0       9.0    16.0
Q3              7.0             2.0  12.0     14.0     17.0    28.0           2.0             1.0         10.0            1.0       17.0    19.0  20.0  4.0       20.0               18.0   12.0  4.0       6.0          5.0    6.0        8.0       8.0     8.0
Q4_hard        15.0             1.0   4.0     21.0     11.0    20.0           0.0             0.0          9.0            0.0       25.0    20.0  18.0  5.0       26.0               22.0   15.0  5.0       6.0          0.0    4.0        5.0       6.0    12.0
```

### Difficulty 별 Top method

- **Q1_easy**: `minibatch` (22), `minibatch_partial` (20), `kde_pilot` (19), `hdbscan` (17), `kdtree` (17)
- **Q2**: `kde_pilot` (21), `hilbert` (20), `minibatch_partial` (19), `hdbscan` (18), `hybrid` (18)
- **Q3**: `hybrid` (28), `km20` (20), `minibatch` (20), `kdtree` (19), `minibatch_partial` (18)
- **Q4_hard**: `minibatch` (26), `kde_pilot` (25), `minibatch_partial` (22), `hdbscan` (21), `hybrid` (20)

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
