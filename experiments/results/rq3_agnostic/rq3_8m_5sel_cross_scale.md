# RQ3 Cross-Scale 5 Selectivity 종합 — DEEP 1M ↔ 8M
> **W2 sprint 2026-05-07 산출** — 19 method × 5 selectivity × DEEP 1M↔8M 외적 타당성 매듭
## 1. 측정 커버리지
| Scale | Methods | Selectivities | Source |
|---|---|---|---|
| 1M | 19 | [0.01, 0.05, 0.1, 0.3, 0.5] | 기존 측정 (rq3_*.parquet) |
| 8M | 19 | [0.01, 0.05, 0.1, 0.3, 0.5] | base ({0.10, 0.30}) + sel_expand ({0.01, 0.05, 0.50}) |

## 2. 19 method × 5 sel × 2 scale mean q_error

```
scale                    1M                                      8M                                
sel                    0.01    0.05    0.10    0.30    0.50    0.01    0.05    0.10    0.30    0.50
method                                                                                             
birch                1.7719  1.2044  1.1298  1.0629  1.0415  1.7492  1.2078  1.1284  1.0607  1.0405
distance_shell       1.6873  1.3403  1.3001  1.2148  1.1246  1.6666  1.3058  1.2799  1.1994  1.1158
gmm                  1.6313  1.1863  1.1247  1.0643  1.0435  1.5807  1.1995  1.1245  1.0617  1.0420
hdbscan              1.6407  1.1851  1.1143  1.0604  1.0363  1.6647  1.1855  1.1190  1.0534  1.0409
hilbert              1.6016  1.1742  1.1229  1.0580  1.0368  1.6150  1.1752  1.1175  1.0549  1.0382
hybrid               1.6360  1.1820  1.1091  1.0598  1.0386  1.6550  1.1822  1.1232  1.0559  1.0377
importance_sampling  2.3481  2.3069  2.2794  1.2776  1.1452  2.5996  2.2476  2.2733  1.2388  1.1296
kde_pilot            1.6529  1.1979  1.1360  1.0637  1.0379  3.3807  1.6309  1.2919  1.0849  1.0441
kdtree               1.7136  1.2189  1.1341  1.0671  1.0401  1.6720  1.2019  1.1245  1.0600  1.0382
lsh                  1.9323  1.2583  1.1671  1.0741  1.0477  1.7368  1.2505  1.1576  1.0784  1.0485
minibatch            1.5930  1.1862  1.1165  1.0535  1.0369  1.6420  1.1946  1.1185  1.0579  1.0360
minibatch_partial    1.5942  1.1789  1.1158  1.0590  1.0381  1.6503  1.1823  1.1206  1.0548  1.0376
pca1d                1.5861  1.2132  1.1240  1.0584  1.0347  1.6429  1.1947  1.1272  1.0602  1.0381
pq                   2.3528  1.2901  1.1765  1.0757  1.0506  2.0723  1.2675  1.1625  1.0684  1.0468
random_proj          1.9702  1.2766  1.1673  1.0756  1.0514  1.9828  1.2643  1.1713  1.0818  1.0509
sobol                3.3612  1.2584  1.1608  1.0721  1.0510  7.7854  1.2707  1.1681  1.0837  1.0545
sparse_rp            1.6004  1.2093  1.1434  1.0688  1.0446  1.6519  1.2330  1.1324  1.0626  1.0406
spectral             2.0197  1.2737  1.1688  1.0735  1.0480  2.0993  1.2457  1.1514  1.0710  1.0484
zorder               1.6647  1.1999  1.1270  1.0580  1.0370  1.6764  1.2037  1.1289  1.0570  1.0383
```

## 3. Spearman ranking 일관성 (1M vs 8M, sel 별)

| Selectivity | n_methods | Spearman ρ | p-value | 해석 |
|---|---|---|---|---|
| 0.01 | 19 | +0.8632 | 0.0000 | **강함** — 1M ranking이 8M에서 잘 보존됨 |
| 0.05 | 19 | +0.8333 | 0.0000 | **강함** — 1M ranking이 8M에서 잘 보존됨 |
| 0.10 | 19 | +0.8767 | 0.0000 | **강함** — 1M ranking이 8M에서 잘 보존됨 |
| 0.30 | 19 | +0.8109 | 0.0000 | **강함** — 1M ranking이 8M에서 잘 보존됨 |
| 0.50 | 19 | +0.8126 | 0.0000 | **강함** — 1M ranking이 8M에서 잘 보존됨 |

## 4. Selectivity 별 1M vs 8M Top-5 method

### sel = 0.01

| Rank | 1M method | 1M q_error | 8M method | 8M q_error |
|---|---|---|---|---|
| 1 | pca1d | 1.5861 | gmm | 1.5807 |
| 2 | minibatch | 1.5930 | hilbert | 1.6150 |
| 3 | minibatch_partial | 1.5942 | minibatch | 1.6420 |
| 4 | sparse_rp | 1.6004 | pca1d | 1.6429 |
| 5 | hilbert | 1.6016 | minibatch_partial | 1.6503 |

### sel = 0.05

| Rank | 1M method | 1M q_error | 8M method | 8M q_error |
|---|---|---|---|---|
| 1 | hilbert | 1.1742 | hilbert | 1.1752 |
| 2 | minibatch_partial | 1.1789 | hybrid | 1.1822 |
| 3 | hybrid | 1.1820 | minibatch_partial | 1.1823 |
| 4 | hdbscan | 1.1851 | hdbscan | 1.1855 |
| 5 | minibatch | 1.1862 | minibatch | 1.1946 |

### sel = 0.10

| Rank | 1M method | 1M q_error | 8M method | 8M q_error |
|---|---|---|---|---|
| 1 | hybrid | 1.1091 | hilbert | 1.1175 |
| 2 | hdbscan | 1.1143 | minibatch | 1.1185 |
| 3 | minibatch_partial | 1.1158 | hdbscan | 1.1190 |
| 4 | minibatch | 1.1165 | minibatch_partial | 1.1206 |
| 5 | hilbert | 1.1229 | hybrid | 1.1232 |

### sel = 0.30

| Rank | 1M method | 1M q_error | 8M method | 8M q_error |
|---|---|---|---|---|
| 1 | minibatch | 1.0535 | hdbscan | 1.0534 |
| 2 | zorder | 1.0580 | minibatch_partial | 1.0548 |
| 3 | hilbert | 1.0580 | hilbert | 1.0549 |
| 4 | pca1d | 1.0584 | hybrid | 1.0559 |
| 5 | minibatch_partial | 1.0590 | zorder | 1.0570 |

### sel = 0.50

| Rank | 1M method | 1M q_error | 8M method | 8M q_error |
|---|---|---|---|---|
| 1 | pca1d | 1.0347 | minibatch | 1.0360 |
| 2 | hdbscan | 1.0363 | minibatch_partial | 1.0376 |
| 3 | hilbert | 1.0368 | hybrid | 1.0377 |
| 4 | minibatch | 1.0369 | pca1d | 1.0381 |
| 5 | zorder | 1.0370 | hilbert | 1.0382 |

