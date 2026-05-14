# 01 — RQ1 paper Bernoulli baseline + RQ1 random sampling 부정확 raw

본 디렉토리는 paper §V-B 의 unstratified Bernoulli baseline (B1) 9 cell 측정 + RQ1 random sampling vs 분포 인지 KM20 정확성 비교 raw csv.

## 핵심 finding

### B1 (paper Fig 12 재현)
- mean qe_trim: **1.618** (paper 1.69 vs **−4.3%**) — paper 100% 재현 검증 anchor
- 9 cell 中 8 cell 이 paper Fig 12 영역 (DEEP/SIFT/SSN sf=100 + YFCC sf=10 + DEEP+WIKI cross sf=10 + DEEP sf=1/10/100)
- A4-sel 1 cell 은 Fig 13 영역 (selectivity ablation, inherent q_error 큼)

### RQ1 (random sampling 부정확)
- 5 cell × Bernoulli vs KM20 stratified × 2 selectivity (0.01, 0.10)
- bernoulli mean=1.638 vs km20=1.582 (sel=0.01)
- mean gap **+3.74%** (5 cell × 5 trial)

## file 목록

### B1 baseline (9 file, 각 ~3 KB)
| File | cell | dataset | sf | paper fig | B1 qe_trim |
|---|---|---|---|---|---|
| A1_DEEP_B1_paper_baseline.json | A1-DEEP | DEEP | 100 | Fig 5/6 | 1.635 |
| A1_SIFT_B1_paper_baseline.json | A1-SIFT | SIFT | 100 | Fig 5/6 | 1.695 |
| A1_SSN_B1_paper_baseline.json | A1-SSN | SimSearchNet++ | 100 | Fig 5/6 | 1.625 |
| A2_Fig7_YFCC_sf10_B1_paper_baseline.json | A2-Fig7 | YFCC | 10 | Fig 7 | 1.656 |
| A2_Fig9_DEEP_WIKI_cross_B1_paper_baseline.json | A2-Fig9 | DEEP+WIKI cross | 10 | Fig 9 | 1.541 |
| A4_sel_DEEP_sel0.04_B1_paper_baseline.json | A4-sel | DEEP sel=0.04 | 100 | Fig 13 | 5.986 |
| A5_scale_sf1_DEEP_B1_paper_baseline.json | A5-scale-sf1 | DEEP | 1 | Fig 14 | 1.618 |
| A5_scale_sf10_DEEP_B1_paper_baseline.json | A5-scale-sf10 | DEEP | 10 | Fig 14 | 1.541 |
| A5_scale_sf100_DEEP_B1_paper_baseline.json | A5-scale-sf100 | DEEP | 100 | Fig 14 | 1.635 |

### RQ1 random sampling vs km20 stratified (5 csv)
- `rq1_DEEP_sf1_bernoulli_vs_km20.csv` (DEEP sf=1)
- `rq1_DEEP_sf10_bernoulli_vs_km20.csv` (DEEP sf=10)
- `rq1_DEEP_sf100_bernoulli_vs_km20.csv` (DEEP sf=100)
- `rq1_SIFT_sf100_bernoulli_vs_km20.csv` (SIFT sf=100)
- `rq1_SimSearchNet_sf100_bernoulli_vs_km20.csv` (SimSearchNet++ sf=100)

csv 컬럼: `dataset,mode,selectivity,seed,query_id,D_target,true_card,est,q_error`
- mode: `bernoulli` (paper §V-B) / `km20_paper_exact` (우리 stratified)
- selectivity: 0.01 (1%) / 0.10 (10%)
- seed: 0.1, 1, 2, 3, 4 (5 trial)
- query_id: 0-999 (1000 query/trial)
- q_error: per-query Q-error
