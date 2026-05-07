# RQ3 Per-Query Method Ranking

각 query 마다 method 들을 q_error 로 ranking → 어떤 query 에서 어느 method 가
이기는지 분석. 박세은 5/5 의문 "DEEP system 절대값 큼" 에 대한 query-level 답변.

## 1. Method 가 Best (rank=1) 빈도

각 (dataset, sel, query) 조합에서 가장 작은 q_error 를 보인 method 의 빈도.

```
mode     birch  distance_shell  gmm  hdbscan  hilbert  hybrid  is_p200_clip  is_p200_noclip  is_p50_clip  is_p50_noclip  kde_pilot  kdtree  km20  lsh  minibatch  minibatch_partial  pca1d  pq  random20  random_proj  sobol  sparse_rp  spectral  zorder
dataset                                                                                                                                                                                                                                                  
DEEP        20               4   25       28       29      36             3               2           12              2         44      30    38   10         38                 45     27   9        14           11     14         16        18      25
SIFT        24               4   15       42       32      46             2               1           22              1         38      37    30   11         44                 34     27   7        16            4     10         16        11      26
TOTAL       44               8   40       70       61      82             5               3           34              3         82      67    68   21         82                 79     54  16        30           15     24         32        29      51
```

## 2. Method 별 평균 Rank

1=항상 best, 7+=항상 worst. query × sel 평균.

```
mode     birch  distance_shell   gmm  hdbscan  hilbert  hybrid  is_p200_clip  is_p200_noclip  is_p50_clip  is_p50_noclip  kde_pilot  kdtree  km20    lsh  minibatch  minibatch_partial  pca1d     pq  random20  random_proj  sobol  sparse_rp  spectral  zorder
dataset                                                                                                                                                                                                                                                        
DEEP     10.26           17.74  9.98     8.84     8.83    8.95         22.10           21.71        20.69          20.62       8.97   10.69  8.94  12.57       8.50               8.91   9.02  13.36     10.09        13.33  12.61      10.53     12.44    9.47
SIFT     10.49           18.04  9.35     8.27     8.00    7.94         20.82           21.45        18.89          20.48       9.37    8.80  8.26  13.94       8.12               8.97   9.31  15.43     11.62        15.10  14.59      10.88     12.34    8.59
```

## 3. Method Disagreement vs Query 난이도

query 별 method 간 q_error 분산 (best vs worst 차이) 의 BERN 난이도 (q_error) 와의
상관. 양수 → 어려운 query 에서 method 차이 큼.

```
         spread_vs_difficulty_corr  n_queries
dataset                                      
DEEP                         0.809      500.0
SIFT                         0.825      500.0
```

## 4. RQ3 narrative 결론

- **Best method 가 dataset/sel 별로 다름** → 본 연구의 7-way contribution 정당화.
- **Hilbert 가 best 비율 + Hilbert 의 평균 rank** 조합으로 "전반적 우위" 정량.
- **disagreement 가 BERN difficulty 와 양상관** 이면 "어려운 query 에서 method
  selection 의 가치 큼" → production 의 method routing 가능성.
