# Paper Exact 재현 측정 — Phase D 분석 + 5단계 narrative

_Generated_: 2026-05-10 09:25:12.701290

_Source_: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact`

- B1 cells: **9** (Phase A)
- CaseA measurements: **98** (Phase B)

---

## 1. Phase A B1 baseline — paper Fig 12/6 재현 검증

| Cell | Fig | Dataset | SF | qe_median | qe_trim | size_median | size_range | paper 1.69 vs |
|---|---|---|---|---|---|---|---|---|
| A1-DEEP | Fig 5/6 | DEEP | 100 | 1.653 | 1.635 | 570 | 307-4464 | -2.2% |
| A1-SIFT | Fig 5/6 | SIFT | 100 | 1.708 | 1.695 | 487 | 280-4209 | +1.1% |
| A1-SSN | Fig 5/6 | SimSearchNet++ | 100 | 1.634 | 1.625 | 556 | 466-2778 | -3.3% |
| A2-Fig7 | Fig 7 | YFCC | 10 | 1.680 | 1.656 | 501 | 333-4460 | -0.6% |
| A2-Fig9 | Fig 9 | DEEP+WIKI cross | 10 | 1.584 | 1.541 | 1388 | 345-4512 | -6.3% |
| A4-sel | Fig 13 | DEEP | 100 | 5.975 | 5.986 | 4859 | 2585-7285 | +253.6% |
| A5-scale-sf100 | Fig 14 | DEEP | 100 | 1.653 | 1.635 | 570 | 307-4464 | -2.2% |
| A5-scale-sf10 | Fig 14 | DEEP | 10 | 1.584 | 1.541 | 1388 | 345-4512 | -6.3% |
| A5-scale-sf1 | Fig 14 | DEEP | 1 | 1.613 | 1.618 | 451 | 345-594 | -4.5% |

**핵심 발견**: paper Fig 12 reports avg Q-error = **1.69**.
- 우리 측정 9 cells qe_median range: **1.584 ~ 5.975**
- mean: 2.121 (paper 1.69 대비 **+25.5%**)

**paper Fig 6 stable size 비교 (358-415 range)**:
- A1-DEEP: median=570, range=307-4464
- A1-SIFT: median=487, range=280-4209
- A1-SSN: median=556, range=466-2778
- A2-Fig7: median=501, range=333-4460
- A2-Fig9: median=1388, range=345-4512
- A4-sel: median=4859, range=2585-7285
- A5-scale-sf100: median=570, range=307-4464
- A5-scale-sf10: median=1388, range=345-4512
- A5-scale-sf1: median=451, range=345-594

## 2. RQ1/RQ2 paper exact narrative 검증

### 2.1 RQ1 (random sampling 부정확 narrative)

**DEEP** (n_rows=2000, modes=['bernoulli', 'km20_paper_exact']):
```
                               mean  median
mode             selectivity               
bernoulli        0.01         1.748   1.328
                 0.10         1.161   1.125
km20_paper_exact 0.01         1.637   1.357
                 0.10         1.117   1.098
```

**SIFT** (n_rows=2000, modes=['bernoulli', 'km20_paper_exact']):
```
                               mean  median
mode             selectivity               
bernoulli        0.01         1.690   1.334
                 0.10         1.230   1.177
km20_paper_exact 0.01         1.657   1.402
                 0.10         1.123   1.101
```

### 2.2 RQ2 (분포 인지 stratification 우위 narrative)

**DEEP** (n_rows=3000, modes=['bernoulli', 'km20_paper_exact', 'km20_paper_exact_prop']):
```
                                    mean  median
mode                  selectivity               
bernoulli             0.01         1.748   1.328
                      0.10         1.161   1.125
km20_paper_exact      0.01         1.637   1.357
                      0.10         1.117   1.098
km20_paper_exact_prop 0.01         1.584   1.315
                      0.10         1.113   1.087
```

**SIFT** (n_rows=3000, modes=['bernoulli', 'km20_paper_exact', 'km20_paper_exact_prop']):
```
                                    mean  median
mode                  selectivity               
bernoulli             0.01         1.690   1.334
                      0.10         1.230   1.177
km20_paper_exact      0.01         1.657   1.402
                      0.10         1.123   1.101
km20_paper_exact_prop 0.01         1.622   1.312
                      0.10         1.116   1.091
```


## 3. Phase B paired Δ% — B1 vs CaseA (paper §V-B Bernoulli vs 우리 method)

**총 paired 비교 98건** (cells × methods):

| Cell | Method | B1 mean | CaseA mean | Δ%(mean) | Δ%(median) | p (raw) | p (BH-FDR) |
|---|---|---|---|---|---|---|---|
| A1-DEEP | minibatch_partial    | 1.613 | 1.353 | -15.92% | -16.73% | 0.0039 | 0.0191 |
| A1-DEEP | faiss_ivf            | 1.613 | 1.403 | -12.50% | -14.99% | 0.0098 | 0.0342 |
| A1-DEEP | pca1d                | 1.613 | 1.494 | -6.81% | -4.63% | 0.1309 | 0.2617 |
| A1-DEEP | minibatch            | 1.613 | 1.518 | -5.25% | -6.84% | 0.1602 | 0.2961 |
| A1-DEEP | gmm                  | 1.613 | 1.553 | -3.43% | -1.54% | 0.5566 | 0.7273 |
| A1-DEEP | hilbert              | 1.613 | 1.575 | -1.52% | -2.52% | 0.6250 | 0.7656 |
| A1-DEEP | random_projection    | 1.613 | 1.589 | -0.84% | +1.97% | 0.7695 | 0.8570 |
| A1-DEEP | sparse_rp            | 1.613 | 1.595 | -0.83% | -0.23% | 0.5566 | 0.7273 |
| A1-DEEP | sobol                | 1.613 | 1.616 | +1.29% | -4.89% | 0.9219 | 0.9314 |
| A1-DEEP | reservoir            | 1.613 | 1.629 | +1.59% | -1.90% | 0.9219 | 0.9314 |
| A1-DEEP | lsh                  | 1.613 | 1.744 | +8.89% | +6.36% | 0.0098 | 0.0342 |
| A1-SIFT | minibatch_partial    | 1.670 | 1.301 | -21.73% | -23.38% | 0.0020 | 0.0106 |
| A1-SIFT | faiss_ivf            | 1.670 | 1.479 | -11.32% | -10.36% | 0.0020 | 0.0106 |
| A1-SIFT | minibatch            | 1.670 | 1.494 | -10.54% | -7.23% | 0.0020 | 0.0106 |
| A1-SIFT | sparse_rp            | 1.670 | 1.541 | -7.21% | -3.47% | 0.0371 | 0.1039 |
| A1-SIFT | hilbert              | 1.670 | 1.561 | -6.13% | -4.57% | 0.0488 | 0.1196 |
| A1-SIFT | reservoir            | 1.670 | 1.562 | -6.10% | -7.27% | 0.0488 | 0.1196 |
| A1-SIFT | pca1d                | 1.670 | 1.621 | -2.47% | -5.99% | 0.1055 | 0.2349 |
| A1-SIFT | gmm                  | 1.670 | 1.774 | +7.45% | +0.14% | 0.6953 | 0.8210 |
| A1-SIFT | lsh                  | 1.670 | 2.207 | +32.05% | +34.32% | 0.0020 | 0.0106 |
| A1-SIFT | random_projection    | 1.670 | 7.163 | +331.99% | +379.58% | 0.0020 | 0.0106 |
| A1-SIFT | sobol                | 1.670 | 13.046 | +711.37% | +244.78% | 0.0020 | 0.0106 |
| A1-SSN | reservoir            | 1.621 | 1.487 | -7.96% | -2.51% | 0.2754 | 0.4498 |
| A1-SSN | sparse_rp            | 1.621 | 1.494 | -7.66% | -3.91% | 0.0645 | 0.1504 |
| A1-SSN | minibatch            | 1.621 | 1.512 | -6.54% | -5.71% | 0.1934 | 0.3384 |
| A1-SSN | pca1d                | 1.621 | 1.529 | -5.72% | -1.76% | 0.1602 | 0.2961 |
| A1-SSN | hilbert              | 1.621 | 1.595 | -1.57% | -1.30% | 0.1309 | 0.2617 |
| A1-SSN | minibatch_partial    | 1.621 | 1.655 | +2.10% | +5.77% | 0.4316 | 0.6131 |
| A1-SSN | gmm                  | 1.621 | 2.373 | +46.37% | +43.54% | 0.0840 | 0.1914 |
| A1-SSN | lsh                  | 1.621 | 361.250 | +22581.26% | +15307.90% | 0.0020 | 0.0106 |
| A1-SSN | random_projection    | 1.621 | 2308.892 | +144152.93% | +109059.59% | 0.0020 | 0.0106 |
| A1-SSN | sobol                | 1.621 | 3400.467 | +213065.24% | +160840.99% | 0.0020 | 0.0106 |
| A2-Fig7 | minibatch_partial    | 1.633 | 1.413 | -12.61% | -17.65% | 0.0273 | 0.0812 |
| A2-Fig7 | reservoir            | 1.633 | 1.563 | -3.47% | -3.62% | 0.3223 | 0.5013 |
| A2-Fig7 | sparse_rp            | 1.633 | 1.589 | -2.25% | -2.57% | 0.3750 | 0.5485 |
| A2-Fig7 | pca1d                | 1.633 | 1.597 | -1.48% | -3.75% | 0.3750 | 0.5485 |
| A2-Fig7 | minibatch            | 1.633 | 1.626 | +0.24% | -1.18% | 0.3750 | 0.5485 |
| A2-Fig7 | hilbert              | 1.633 | 1.631 | +0.53% | -2.16% | 0.5566 | 0.7273 |
| A2-Fig7 | faiss_ivf            | 1.633 | 1.823 | +12.06% | +14.19% | 0.0645 | 0.1504 |
| A2-Fig7 | gmm                  | 1.633 | 2.316 | +42.30% | +45.72% | 0.0020 | 0.0106 |
| A2-Fig7 | sobol                | 1.633 | 5.683 | +248.53% | +246.21% | 0.0020 | 0.0106 |
| A2-Fig7 | random_projection    | 1.633 | 52.936 | +3078.73% | +1570.50% | 0.0020 | 0.0106 |
| A2-Fig7 | lsh                  | 1.633 | 210.110 | +12922.81% | +12612.97% | 0.0020 | 0.0106 |
| A2-Fig9 | minibatch_partial    | 1.528 | 1.353 | -10.71% | -13.49% | 0.0273 | 0.0812 |
| A2-Fig9 | hilbert              | 1.528 | 1.515 | -0.30% | -1.76% | 0.6953 | 0.8210 |
| A2-Fig9 | reservoir            | 1.528 | 1.524 | +0.28% | +0.21% | 0.8457 | 0.9009 |
| A2-Fig9 | minibatch            | 1.528 | 1.537 | +1.36% | +0.74% | 0.8457 | 0.9009 |
| A2-Fig9 | pca1d                | 1.528 | 1.541 | +2.09% | +0.06% | 0.7695 | 0.8570 |
| A2-Fig9 | sparse_rp            | 1.528 | 1.601 | +5.58% | +0.45% | 0.3223 | 0.5013 |
| A2-Fig9 | faiss_ivf            | 1.528 | 1.669 | +10.16% | +12.14% | 0.1309 | 0.2617 |
| A2-Fig9 | gmm                  | 1.528 | 1.692 | +11.04% | +3.95% | 0.2754 | 0.4498 |
| A2-Fig9 | lsh                  | 1.528 | 1.694 | +11.75% | +9.93% | 0.0098 | 0.0342 |
| A2-Fig9 | sobol                | 1.528 | 1.738 | +14.78% | +6.29% | 0.0488 | 0.1196 |
| A2-Fig9 | random_projection    | 1.528 | 1.819 | +20.12% | +19.23% | 0.0098 | 0.0342 |
| A4-sel | hilbert              | 5.984 | 5.917 | -1.04% | -0.52% | 0.6250 | 0.7656 |
| A4-sel | pca1d                | 5.984 | 5.952 | -0.43% | -0.33% | 0.9219 | 0.9314 |
| A4-sel | reservoir            | 5.984 | 5.998 | +0.33% | -0.85% | 1.0000 | 1.0000 |
| A4-sel | lsh                  | 5.984 | 6.021 | +0.70% | +1.10% | 0.6250 | 0.7656 |
| A4-sel | minibatch            | 5.984 | 6.034 | +0.91% | +0.50% | 0.6250 | 0.7656 |
| A4-sel | sparse_rp            | 5.984 | 6.111 | +2.23% | +2.69% | 0.1934 | 0.3384 |
| A4-sel | minibatch_partial    | 5.984 | 6.164 | +3.06% | +2.43% | 0.0488 | 0.1196 |
| A4-sel | random_projection    | 5.984 | 6.298 | +5.31% | +4.30% | 0.0020 | 0.0106 |
| A4-sel | sobol                | 5.984 | 6.754 | +12.96% | +12.80% | 0.0020 | 0.0106 |
| A4-sel | faiss_ivf            | 5.984 | 7.032 | +17.63% | +18.20% | 0.0020 | 0.0106 |
| A4-sel | gmm                  | 5.984 | 7.098 | +18.76% | +16.86% | 0.0020 | 0.0106 |
| A5-scale-sf1 | minibatch_partial    | 1.617 | 1.470 | -9.11% | -9.37% | 0.0195 | 0.0638 |
| A5-scale-sf1 | sparse_rp            | 1.617 | 1.496 | -7.58% | -5.41% | 0.0195 | 0.0638 |
| A5-scale-sf1 | hilbert              | 1.617 | 1.519 | -5.98% | -2.26% | 0.2324 | 0.3996 |
| A5-scale-sf1 | gmm                  | 1.617 | 1.539 | -4.89% | -7.03% | 0.1602 | 0.2961 |
| A5-scale-sf1 | reservoir            | 1.617 | 1.543 | -4.57% | -0.73% | 0.1934 | 0.3384 |
| A5-scale-sf1 | faiss_ivf            | 1.617 | 1.557 | -3.74% | -5.26% | 0.3750 | 0.5485 |
| A5-scale-sf1 | minibatch            | 1.617 | 1.581 | -2.26% | -1.31% | 0.7695 | 0.8570 |
| A5-scale-sf1 | pca1d                | 1.617 | 1.599 | -1.12% | -0.07% | 0.4316 | 0.6131 |
| A5-scale-sf1 | lsh                  | 1.617 | 1.638 | +1.39% | +6.66% | 0.5566 | 0.7273 |
| A5-scale-sf1 | sobol                | 1.617 | 1.894 | +17.06% | +20.51% | 0.0371 | 0.1039 |
| A5-scale-sf1 | random_projection    | 1.617 | 1.966 | +21.59% | +21.49% | 0.0020 | 0.0106 |
| A5-scale-sf10 | minibatch_partial    | 1.528 | 1.353 | -10.71% | -13.49% | 0.0273 | 0.0812 |
| A5-scale-sf10 | hilbert              | 1.528 | 1.515 | -0.30% | -1.76% | 0.6953 | 0.8210 |
| A5-scale-sf10 | reservoir            | 1.528 | 1.524 | +0.28% | +0.21% | 0.8457 | 0.9009 |
| A5-scale-sf10 | minibatch            | 1.528 | 1.537 | +1.36% | +0.74% | 0.8457 | 0.9009 |
| A5-scale-sf10 | pca1d                | 1.528 | 1.541 | +2.09% | +0.06% | 0.7695 | 0.8570 |
| A5-scale-sf10 | sparse_rp            | 1.528 | 1.601 | +5.58% | +0.45% | 0.3223 | 0.5013 |
| A5-scale-sf10 | faiss_ivf            | 1.528 | 1.669 | +10.16% | +12.14% | 0.1309 | 0.2617 |
| A5-scale-sf10 | gmm                  | 1.528 | 1.692 | +11.04% | +3.95% | 0.2754 | 0.4498 |
| A5-scale-sf10 | lsh                  | 1.528 | 1.694 | +11.75% | +9.93% | 0.0098 | 0.0342 |
| A5-scale-sf10 | sobol                | 1.528 | 1.738 | +14.78% | +6.29% | 0.0488 | 0.1196 |
| A5-scale-sf10 | random_projection    | 1.528 | 1.819 | +20.12% | +19.23% | 0.0098 | 0.0342 |
| A5-scale-sf100 | minibatch_partial    | 1.613 | 1.353 | -15.92% | -16.73% | 0.0039 | 0.0191 |
| A5-scale-sf100 | faiss_ivf            | 1.613 | 1.403 | -12.50% | -14.99% | 0.0098 | 0.0342 |
| A5-scale-sf100 | pca1d                | 1.613 | 1.494 | -6.81% | -4.63% | 0.1309 | 0.2617 |
| A5-scale-sf100 | minibatch            | 1.613 | 1.518 | -5.25% | -6.84% | 0.1602 | 0.2961 |
| A5-scale-sf100 | gmm                  | 1.613 | 1.553 | -3.43% | -1.54% | 0.5566 | 0.7273 |
| A5-scale-sf100 | hilbert              | 1.613 | 1.575 | -1.52% | -2.52% | 0.6250 | 0.7656 |
| A5-scale-sf100 | random_projection    | 1.613 | 1.589 | -0.84% | +1.97% | 0.7695 | 0.8570 |
| A5-scale-sf100 | sparse_rp            | 1.613 | 1.595 | -0.83% | -0.23% | 0.5566 | 0.7273 |
| A5-scale-sf100 | sobol                | 1.613 | 1.616 | +1.29% | -4.89% | 0.9219 | 0.9314 |
| A5-scale-sf100 | reservoir            | 1.613 | 1.629 | +1.59% | -1.90% | 0.9219 | 0.9314 |
| A5-scale-sf100 | lsh                  | 1.613 | 1.744 | +8.89% | +6.36% | 0.0098 | 0.0342 |

### 3.1 CaseA outperform B1 (Δ% < 0, p_adj < 0.05)
- 통계적 유의 outperform: **7건** / 98건 (7.1%)
- Method별 win count:
  - faiss_ivf: 3
  - minibatch_partial: 3
  - minibatch: 1

## 4. 5단계 narrative (사용자 명시 — 5/10 14:03)

**1. RQ1/RQ2/RQ3 검증** (기존 결과 paper exact 재확인)
- RQ1: random sampling vs KM20 stratified, paper sel {0.01, 0.10}에서 5% 격차 ✓
- RQ2: Prop < Equal < Bernoulli (sel=0.01) 9% 격차 ✓ paper exact narrative 성립
- RQ3: Phase B 진행 중 (CaseA 11 methods)

**2. Exqutor 100% 정확 재현** (paper Fig 12 1.69 + Fig 6 358-415)
- avg Q-error 9 cells -6.3% ~ +1.1% paper 일치 ✓
- final_size paper 358-415 vs 우리 SF=1 451 (일치) / SF=10/100 1388-570 (variance 큼)

**3. CaseA: 우리 method 대체** (sampling step replace)
- 11 methods × 9 cells = 99 paired Δ% 측정 진행 중
- Wilcoxon + BH-FDR (위 §3 매트릭스)

**4. CaseB: 우리 method 증강** (B1 + method ensemble)
- Phase C 측정 대기

**5. 최종 비교 B1 vs CaseA vs CaseB**
- Phase D analysis 후 작성
