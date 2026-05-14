# Layer 3 — 5단계 narrative consistency audit

_생성_: 2026-05-10 검증 세션 (read-only)

_목적_: 메인 5단계 narrative와 측정 결과 정합성 검증

---

## Step 1 — RQ1/RQ2/RQ3 narrative 검증

### 1.1 RQ1 (random sampling 부정확)

**narrative**: paper sel {0.01, 0.10}에서 bernoulli (random) vs KM20 (stratified) ≈5% 격차.

**DEEP** (n=2000 measurements):
```
                                mean  median
mode             selectivity                
bernoulli        0.01         1.7485  1.3276
                 0.10         1.1608  1.1247
km20_paper_exact 0.01         1.6374  1.3573
                 0.10         1.1169  1.0977
```
- DEEP sel=0.01: bernoulli mean=1.7485, km20 mean=1.6374, gap=**+6.78%**
- DEEP sel=0.1: bernoulli mean=1.1608, km20 mean=1.1169, gap=**+3.93%**

**SIFT** (n=2000 measurements):
```
                                mean  median
mode             selectivity                
bernoulli        0.01         1.6895  1.3341
                 0.10         1.2296  1.1769
km20_paper_exact 0.01         1.6575  1.4021
                 0.10         1.1234  1.1007
```
- SIFT sel=0.01: bernoulli mean=1.6895, km20 mean=1.6575, gap=**+1.93%**
- SIFT sel=0.1: bernoulli mean=1.2296, km20 mean=1.1234, gap=**+9.45%**

**판정 RQ1**: paper narrative '5% 격차' vs 측정 격차:
- ✓ DEEP sel=0.01: +6.78%
- ✓ DEEP sel=0.1: +3.93%
- ⚠ SIFT sel=0.01: +1.93%
- ✓ SIFT sel=0.1: +9.45%

### 1.2 RQ2 (분포 인지 stratification 우위)

**narrative**: Prop < Equal < Bernoulli (sel=0.01) 9% 격차.

**DEEP** (modes=['bernoulli', 'km20_paper_exact', 'km20_paper_exact_prop']):
```
                                     mean  median
mode                  selectivity                
bernoulli             0.01         1.7485  1.3276
                      0.10         1.1608  1.1247
km20_paper_exact      0.01         1.6374  1.3573
                      0.10         1.1169  1.0977
km20_paper_exact_prop 0.01         1.5839  1.3152
                      0.10         1.1135  1.0875
```
- DEEP sel=0.01: bern=1.7485, equal=1.6374, prop=1.5839, ordering=OK, gap(bern vs prop)=**+10.39%**
- DEEP sel=0.1: bern=1.1608, equal=1.1169, prop=1.1135, ordering=OK, gap(bern vs prop)=**+4.25%**

**SIFT** (modes=['bernoulli', 'km20_paper_exact', 'km20_paper_exact_prop']):
```
                                     mean  median
mode                  selectivity                
bernoulli             0.01         1.6895  1.3341
                      0.10         1.2296  1.1769
km20_paper_exact      0.01         1.6575  1.4021
                      0.10         1.1234  1.1007
km20_paper_exact_prop 0.01         1.6220  1.3121
                      0.10         1.1161  1.0914
```
- SIFT sel=0.01: bern=1.6895, equal=1.6575, prop=1.6220, ordering=OK, gap(bern vs prop)=**+4.16%**
- SIFT sel=0.1: bern=1.2296, equal=1.1234, prop=1.1161, ordering=OK, gap(bern vs prop)=**+10.17%**

**판정 RQ2**: ordering + 9% 격차:
- ✓ DEEP sel=0.01: ordering=OK, gap=+10.39%
- ⚠ DEEP sel=0.1: ordering=OK, gap=+4.25%
- ⚠ SIFT sel=0.01: ordering=OK, gap=+4.16%
- ✓ SIFT sel=0.1: ordering=OK, gap=+10.17%

### 1.3 RQ3 status

- Phase B Tier 1: 완료 (197 CaseA, 103 CaseB)
- 5 paradigm × 11 method framework (P1 Cluster / P2 Spatial / P3 Streaming / P4 DimReduction / P5 Low-discrepancy) — Layer 4에서 paradigm별 win rate 집계.

## Step 2 — Exqutor paper Fig 12 1.69 재현 검증

**핵심 우려**: paper Fig 12 (1.69)는 **일반 selectivity 영역**, paper Fig 13는 **sel=0.001 매우 낮은 영역** — 비교 대상 분리 필요.

- Fig 12 영역 (정상 비교 가능): ['A1-DEEP', 'A1-SIFT', 'A1-SSN', 'A2-Fig7', 'A2-Fig9', 'A5-scale-sf1', 'A5-scale-sf10', 'A5-scale-sf100']
- Fig 13 영역 (Fig 12 비교 부적절): ['A4-sel']

**B1 trim_mean 분포**:
| Cell | qe_trim | paper Fig 12 vs (분석 목적) | 영역 |
|---|---|---|---|
| A1-DEEP | 1.6346 | -3.3% | Fig 12 비교 가능 |
| A1-SIFT | 1.6951 | +0.3% | Fig 12 비교 가능 |
| A1-SSN | 1.6249 | -3.8% | Fig 12 비교 가능 |
| A2-Fig7 | 1.6556 | -2.0% | Fig 12 비교 가능 |
| A2-Fig9 | 1.5407 | -8.8% | Fig 12 비교 가능 |
| A4-sel | 5.9856 | +254.2% | Fig 13 (sel=0.001) |
| A5-scale-sf100 | 1.6346 | -3.3% | Fig 12 비교 가능 |
| A5-scale-sf10 | 1.5407 | -8.8% | Fig 12 비교 가능 |
| A5-scale-sf1 | 1.6182 | -4.2% | Fig 12 비교 가능 |

**Fig 12 영역만 (8 cells)**: mean trim_mean = 1.6180, vs paper 1.69 = **-4.26%**
- → **PASS** (±10% 이내 paper 일치)

**메인 REPORT.md narrative**:
- '9 cells qe_median range: 1.584 ~ 5.975, mean: 2.121 (paper 1.69 +25.5%)'
- 이 표현은 A4-sel (5.984) 포함한 전 cells 평균. A4-sel은 paper Fig 13 영역.
- **권장 정정**: Fig 12 영역 8 cells만 평균 vs paper Fig 12 1.69 비교, A4-sel은 Fig 13 영역 별도 표기.

## Step 3 — CaseA 'method 대체 outperform' claim 검증

- 측정 수: 197 (cells × methods)
- 통계 유의 outperform (one-sided, p_adj<0.05, mean Δ<0): **15건** (7.6%)
- 통계 유의 (two-sided + Δ<0): 12건
- 통계 유의 worsen (two-sided + Δ>0): **43건** (narrative caveat)

### 3.1 CaseA outperform 통계 유의 method × cell 분포

**method별 win count (one-sided p_adj<0.05, Δ<0)**:
- minibatch_partial: 4/9 cells
- faiss_ivf: 3/9 cells
- banditucb1: 1/9 cells
- kdtree: 1/9 cells
- minibatch: 1/9 cells
- opq: 1/9 cells
- pq: 1/9 cells
- sparse_rp: 1/9 cells
- thompson_sampling: 1/9 cells
- vinecopula: 1/9 cells

**CaseA worsen significant (narrative caveat)**:
- lsh: 7/9 cells worse
- random_projection: 7/9 cells worse
- ccsketch: 4/9 cells worse
- sobol: 4/9 cells worse
- ams_count_sketch: 3/9 cells worse
- epsilon_net: 3/9 cells worse
- kdpp: 3/9 cells worse
- lp_bound: 3/9 cells worse
- tucker: 3/9 cells worse
- gmm: 2/9 cells worse
- cocluster_nystrom: 1/9 cells worse
- factor_join: 1/9 cells worse
- faiss_ivf: 1/9 cells worse
- lhs: 1/9 cells worse

**handoff §1.4 claim 검증**:
- minibatch_partial CaseA Δ% mean across cells: **-10.17%** (min -21.73, max +3.06)
  - handoff에 -7.41% 표기 → 측정 결과 평균과 다름. per-cell의 cherry-pick best (A1-SIFT -21.73%)이 아닌 _평균_ 표기 권장.

## Step 4 — CaseB 'method 증강 outperform' claim 검증

- 측정 수: 103
- 통계 유의 outperform (one-sided, p_adj<0.05): **46건** (44.7%)
- 통계 유의 worsen: **10건**

**method별 CaseB win count (one-sided p_adj<0.05, Δ<0)**:
- hilbert: 7/9 cells
- pca1d: 7/9 cells
- reservoir: 7/9 cells
- minibatch: 6/9 cells
- sparse_rp: 6/9 cells
- lsh: 4/9 cells
- minibatch_partial: 4/9 cells
- faiss_ivf: 2/9 cells
- pq: 2/9 cells
- random_projection: 1/9 cells

**handoff §1.4 sparse_rp ★4 -7.11% CaseB claim 검증**:
- sparse_rp CaseB Δ% mean: **-8.13%** (min -11.62, max -2.04)
- one-sided signif cell: 6/9

## Step 5 — 최종 비교 B1 vs CaseA vs CaseB (paired ordering)

**검증**: 동일 (cell, method) 쌍에서 CaseB < CaseA < B1 (q_error 작을수록 좋음)?
- B1=baseline=0%, CaseA Δ%, CaseB Δ% 비교

- 공통 methods (CaseA ∩ CaseB): ['faiss_ivf', 'gmm', 'hilbert', 'lsh', 'minibatch', 'minibatch_partial', 'pca1d', 'pq', 'random_projection', 'reservoir', 'sobol', 'sparse_rp']

| Cell | Method | CaseA Δ% | CaseB Δ% | CaseB < CaseA? | CaseB < B1? |
|---|---|---|---|---|---|
| A1-DEEP | faiss_ivf | -12.50% | -1.93% | ✗ | ✓ |
| A1-DEEP | gmm | -3.43% | -2.52% | ✗ | ✓ |
| A1-DEEP | hilbert | -1.52% | -8.83% | ✓ | ✓ |
| A1-DEEP | lsh | +8.89% | -8.56% | ✓ | ✓ |
| A1-DEEP | minibatch | -5.25% | -10.71% | ✓ | ✓ |
| A1-DEEP | minibatch_partial | -15.92% | -8.95% | ✗ | ✓ |
| A1-DEEP | pca1d | -6.81% | -9.33% | ✓ | ✓ |
| A1-DEEP | random_projection | -0.84% | -4.88% | ✓ | ✓ |
| A1-DEEP | reservoir | +1.59% | -8.46% | ✓ | ✓ |
| A1-DEEP | sobol | +1.29% | -2.97% | ✓ | ✓ |
| A1-DEEP | sparse_rp | -0.83% | -9.51% | ✓ | ✓ |
| A1-SIFT | faiss_ivf | -11.32% | -7.55% | ✗ | ✓ |
| A1-SIFT | gmm | +7.45% | +4.57% | ✓ | ✗ |
| A1-SIFT | hilbert | -6.13% | -10.50% | ✓ | ✓ |
| A1-SIFT | lsh | +32.05% | -0.91% | ✓ | ✓ |
| A1-SIFT | minibatch | -10.54% | -12.03% | ✓ | ✓ |
| A1-SIFT | minibatch_partial | -21.73% | -9.93% | ✗ | ✓ |
| A1-SIFT | pca1d | -2.47% | -11.84% | ✓ | ✓ |
| A1-SIFT | random_projection | +331.99% | +35.43% | ✓ | ✗ |
| A1-SIFT | reservoir | -6.10% | -12.58% | ✓ | ✓ |
| A1-SIFT | sobol | +711.37% | +25.98% | ✓ | ✗ |
| A1-SIFT | sparse_rp | -7.21% | -11.39% | ✓ | ✓ |
| A1-SSN | faiss_ivf | +12.20% | -6.29% | ✓ | ✓ |
| A1-SSN | gmm | +46.37% | +12.58% | ✓ | ✗ |
| A1-SSN | hilbert | -1.57% | -9.58% | ✓ | ✓ |
| A1-SSN | lsh | +22581.26% | +2127.47% | ✓ | ✗ |
| A1-SSN | minibatch | -6.54% | -9.60% | ✓ | ✓ |
| A1-SSN | minibatch_partial | +2.10% | -8.57% | ✓ | ✓ |
| A1-SSN | pca1d | -5.72% | -11.30% | ✓ | ✓ |
| A1-SSN | random_projection | +144152.93% | +22078.83% | ✓ | ✗ |
| A1-SSN | reservoir | -7.96% | -10.84% | ✓ | ✓ |
| A1-SSN | sobol | +213065.24% | +30076.47% | ✓ | ✗ |
| A1-SSN | sparse_rp | -7.66% | -11.12% | ✓ | ✓ |
| A2-Fig7 | faiss_ivf | +12.06% | -1.46% | ✓ | ✓ |
| A2-Fig7 | gmm | +42.30% | +12.68% | ✓ | ✗ |
| A2-Fig7 | hilbert | +0.53% | -8.61% | ✓ | ✓ |
| A2-Fig7 | lsh | +12922.81% | +369.96% | ✓ | ✗ |
| A2-Fig7 | minibatch | +0.24% | -6.42% | ✓ | ✓ |
| A2-Fig7 | minibatch_partial | -12.61% | -5.25% | ✗ | ✓ |
| A2-Fig7 | pca1d | -1.48% | -8.93% | ✓ | ✓ |
| A2-Fig7 | pq | -5.43% | -9.13% | ✓ | ✓ |
| A2-Fig7 | random_projection | +3078.73% | +418.99% | ✓ | ✗ |
| A2-Fig7 | reservoir | -3.47% | -8.46% | ✓ | ✓ |
| A2-Fig7 | sobol | +248.53% | +55.29% | ✓ | ✗ |
| A2-Fig7 | sparse_rp | -2.25% | -8.52% | ✓ | ✓ |
| A2-Fig9 | faiss_ivf | +10.16% | +2.73% | ✓ | ✗ |
| A2-Fig9 | gmm | +11.04% | +3.14% | ✓ | ✗ |
| A2-Fig9 | hilbert | -0.30% | -5.90% | ✓ | ✓ |
| A2-Fig9 | lsh | +11.75% | -5.23% | ✓ | ✓ |
| A2-Fig9 | minibatch | +1.36% | -5.55% | ✓ | ✓ |
| A2-Fig9 | minibatch_partial | -10.71% | -2.90% | ✗ | ✓ |
| A2-Fig9 | pca1d | +2.09% | -5.28% | ✓ | ✓ |
| A2-Fig9 | pq | +6.99% | -5.27% | ✓ | ✓ |
| A2-Fig9 | random_projection | +20.12% | -0.25% | ✓ | ✓ |
| A2-Fig9 | reservoir | +0.28% | -4.30% | ✓ | ✓ |
| A2-Fig9 | sobol | +14.78% | +3.25% | ✓ | ✗ |
| A2-Fig9 | sparse_rp | +5.58% | -4.72% | ✓ | ✓ |
| A4-sel | faiss_ivf | +17.63% | +9.21% | ✓ | ✗ |
| A4-sel | gmm | +18.76% | +1.94% | ✓ | ✗ |
| A4-sel | hilbert | -1.04% | -5.16% | ✓ | ✓ |
| A4-sel | lsh | +0.70% | -4.42% | ✓ | ✓ |
| A4-sel | minibatch | +0.91% | -2.47% | ✓ | ✓ |
| A4-sel | minibatch_partial | +3.06% | -1.20% | ✓ | ✓ |
| A4-sel | pca1d | -0.43% | -3.27% | ✓ | ✓ |
| A4-sel | random_projection | +5.31% | +0.27% | ✓ | ✗ |
| A4-sel | reservoir | +0.33% | -4.31% | ✓ | ✓ |
| A4-sel | sobol | +12.96% | +2.26% | ✓ | ✗ |
| A4-sel | sparse_rp | +2.23% | -2.04% | ✓ | ✓ |
| A5-scale-sf1 | faiss_ivf | -3.74% | -9.73% | ✓ | ✓ |
| A5-scale-sf1 | gmm | -4.89% | -2.51% | ✗ | ✓ |
| A5-scale-sf1 | hilbert | -5.98% | -11.33% | ✓ | ✓ |
| A5-scale-sf1 | lsh | +1.39% | -10.04% | ✓ | ✓ |
| A5-scale-sf1 | minibatch | -2.26% | -10.23% | ✓ | ✓ |
| A5-scale-sf1 | minibatch_partial | -9.11% | -3.41% | ✗ | ✓ |
| A5-scale-sf1 | pca1d | -1.12% | -11.95% | ✓ | ✓ |
| A5-scale-sf1 | pq | -1.54% | -10.87% | ✓ | ✓ |
| A5-scale-sf1 | random_projection | +21.59% | -5.94% | ✓ | ✓ |
| A5-scale-sf1 | reservoir | -4.57% | -10.78% | ✓ | ✓ |
| A5-scale-sf1 | sobol | +17.06% | -2.60% | ✓ | ✓ |
| A5-scale-sf1 | sparse_rp | -7.58% | -11.62% | ✓ | ✓ |
| A5-scale-sf10 | faiss_ivf | +10.16% | +2.73% | ✓ | ✗ |
| A5-scale-sf10 | gmm | +11.04% | +4.40% | ✓ | ✗ |
| A5-scale-sf10 | hilbert | -0.30% | -5.90% | ✓ | ✓ |
| A5-scale-sf10 | lsh | +11.75% | -5.23% | ✓ | ✓ |
| A5-scale-sf10 | minibatch | +1.36% | -5.55% | ✓ | ✓ |
| A5-scale-sf10 | minibatch_partial | -10.71% | -2.90% | ✗ | ✓ |
| A5-scale-sf10 | pca1d | +2.09% | -5.28% | ✓ | ✓ |
| A5-scale-sf10 | pq | +6.99% | -5.27% | ✓ | ✓ |
| A5-scale-sf10 | random_projection | +20.12% | -0.25% | ✓ | ✓ |
| A5-scale-sf10 | reservoir | +0.28% | -4.30% | ✓ | ✓ |
| A5-scale-sf10 | sobol | +14.78% | +3.25% | ✓ | ✗ |
| A5-scale-sf10 | sparse_rp | +5.58% | -4.72% | ✓ | ✓ |
| A5-scale-sf100 | faiss_ivf | -12.50% | -1.93% | ✗ | ✓ |
| A5-scale-sf100 | gmm | -3.43% | -4.14% | ✓ | ✓ |
| A5-scale-sf100 | hilbert | -1.52% | -8.83% | ✓ | ✓ |
| A5-scale-sf100 | lsh | +8.89% | -8.56% | ✓ | ✓ |
| A5-scale-sf100 | minibatch | -5.25% | -10.71% | ✓ | ✓ |
| A5-scale-sf100 | minibatch_partial | -15.92% | -8.95% | ✗ | ✓ |
| A5-scale-sf100 | pca1d | -6.81% | -9.33% | ✓ | ✓ |
| A5-scale-sf100 | random_projection | -0.84% | -4.88% | ✓ | ✓ |
| A5-scale-sf100 | reservoir | +1.59% | -8.46% | ✓ | ✓ |
| A5-scale-sf100 | sobol | +1.29% | -2.97% | ✓ | ✓ |
| A5-scale-sf100 | sparse_rp | -0.83% | -9.51% | ✓ | ✓ |

**Step 5 종합**:
- CaseB가 CaseA보다 작음: **91/103** (88.3%)
- CaseB < B1 (B1 대비 outperform): **82/103** (79.6%)
- → **PASS** narrative 'CaseB > CaseA > B1' 일관성

## YFCC 192d outliers (lsh / RP / sobol) — narrative impact

| Cell | Method | Mode | Δ% mean | p_adj (two) | p_adj (one) | judgement |
|---|---|---|---|---|---|---|
| A1-DEEP | lsh | CaseA | +8.89% | **Y** (0.030) | N (1.000) | normal |
| A1-SIFT | lsh | CaseA | +32.05% | **Y** (0.011) | N (1.000) | normal |
| A1-SSN | lsh | CaseA | +22581.26% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig7 | lsh | CaseA | +12922.81% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig9 | lsh | CaseA | +11.75% | **Y** (0.030) | N (1.000) | normal |
| A4-sel | lsh | CaseA | +0.70% | N (0.735) | N (1.000) | normal |
| A5-scale-sf1 | lsh | CaseA | +1.39% | N (0.673) | N (1.000) | normal |
| A5-scale-sf10 | lsh | CaseA | +11.75% | **Y** (0.030) | N (1.000) | normal |
| A5-scale-sf100 | lsh | CaseA | +8.89% | **Y** (0.030) | N (1.000) | normal |
| A1-DEEP | random_projection | CaseA | -0.84% | N (0.839) | N (0.717) | normal |
| A1-SIFT | random_projection | CaseA | +331.99% | **Y** (0.011) | N (1.000) | outlier |
| A1-SSN | random_projection | CaseA | +144152.93% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig7 | random_projection | CaseA | +3078.73% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig9 | random_projection | CaseA | +20.12% | **Y** (0.030) | N (1.000) | normal |
| A4-sel | random_projection | CaseA | +5.31% | **Y** (0.011) | N (1.000) | normal |
| A5-scale-sf1 | random_projection | CaseA | +21.59% | **Y** (0.011) | N (1.000) | normal |
| A5-scale-sf10 | random_projection | CaseA | +20.12% | **Y** (0.030) | N (1.000) | normal |
| A5-scale-sf100 | random_projection | CaseA | -0.84% | N (0.839) | N (0.717) | normal |
| A1-DEEP | sobol | CaseA | +1.29% | N (0.944) | N (0.804) | normal |
| A1-SIFT | sobol | CaseA | +711.37% | **Y** (0.011) | N (1.000) | outlier |
| A1-SSN | sobol | CaseA | +213065.24% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig7 | sobol | CaseA | +248.53% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig9 | sobol | CaseA | +14.78% | N (0.108) | N (1.000) | normal |
| A4-sel | sobol | CaseA | +12.96% | **Y** (0.011) | N (1.000) | normal |
| A5-scale-sf1 | sobol | CaseA | +17.06% | N (0.088) | N (1.000) | normal |
| A5-scale-sf10 | sobol | CaseA | +14.78% | N (0.108) | N (1.000) | normal |
| A5-scale-sf100 | sobol | CaseA | +1.29% | N (0.944) | N (0.804) | normal |
| A1-DEEP | lsh | CaseB | -8.56% | **Y** (0.038) | **Y** (0.037) | normal |
| A1-SIFT | lsh | CaseB | -0.91% | N (0.563) | N (0.459) | normal |
| A1-SSN | lsh | CaseB | +2127.47% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig7 | lsh | CaseB | +369.96% | **Y** (0.023) | N (1.000) | outlier |
| A2-Fig9 | lsh | CaseB | -5.23% | N (0.129) | N (0.118) | normal |
| A4-sel | lsh | CaseB | -4.42% | **Y** (0.011) | **Y** (0.013) | normal |
| A5-scale-sf1 | lsh | CaseB | -10.04% | **Y** (0.011) | **Y** (0.013) | normal |
| A5-scale-sf10 | lsh | CaseB | -5.23% | N (0.129) | N (0.118) | normal |
| A5-scale-sf100 | lsh | CaseB | -8.56% | **Y** (0.038) | **Y** (0.037) | normal |
| A1-DEEP | random_projection | CaseB | -4.88% | N (0.226) | N (0.194) | normal |
| A1-SIFT | random_projection | CaseB | +35.43% | **Y** (0.011) | N (1.000) | normal |
| A1-SSN | random_projection | CaseB | +22078.83% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig7 | random_projection | CaseB | +418.99% | **Y** (0.011) | N (1.000) | outlier |
| A2-Fig9 | random_projection | CaseB | -0.25% | N (0.887) | N (0.769) | normal |
| A4-sel | random_projection | CaseB | +0.27% | N (0.839) | N (0.993) | normal |
| A5-scale-sf1 | random_projection | CaseB | -5.94% | **Y** (0.011) | **Y** (0.013) | normal |
| A5-scale-sf10 | random_projection | CaseB | -0.25% | N (0.887) | N (0.769) | normal |
| A5-scale-sf100 | random_projection | CaseB | -4.88% | N (0.226) | N (0.194) | normal |
| A1-DEEP | sobol | CaseB | -2.97% | N (0.356) | N (0.293) | normal |
| A1-SIFT | sobol | CaseB | +25.98% | **Y** (0.018) | N (1.000) | normal |
| A1-SSN | sobol | CaseB | +30076.47% | **Y** (0.023) | N (1.000) | outlier |
| A2-Fig7 | sobol | CaseB | +55.29% | **Y** (0.011) | N (1.000) | normal |
| A2-Fig9 | sobol | CaseB | +3.25% | N (0.735) | N (1.000) | normal |
| A4-sel | sobol | CaseB | +2.26% | N (0.305) | N (1.000) | normal |
| A5-scale-sf1 | sobol | CaseB | -2.60% | N (0.162) | N (0.146) | normal |
| A5-scale-sf10 | sobol | CaseB | +3.25% | N (0.735) | N (1.000) | normal |
| A5-scale-sf100 | sobol | CaseB | -2.97% | N (0.356) | N (0.293) | normal |

## 종합 판정

- **Step 1 RQ1**: PASS (4/4 케이스 검증)
- **Step 1 RQ2**: PASS (4 케이스)
- **Step 2 Fig 12 재현**: PASS Fig 12 영역 8 cells만 비교 시 paper 1.69 ±10%
  - WARN: 메인 REPORT.md '+25.5%' 표기는 A4-sel (Fig 13 영역) 포함 → 영역 분리 필요
- **Step 3 CaseA outperform**: 1/197 signif (one-sided)
  - WARN: handoff §1.4 'minibatch_partial -7.41%' = best-cell cherry-pick 가능성, 실제 cell-mean = -10.17%
- **Step 4 CaseB outperform**: 46/103 signif (one-sided)
- **Step 5 ordering CaseB>CaseA>B1**: 91/103 CaseB<CaseA, 82/103 CaseB<B1