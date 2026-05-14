# 10 — Full Portfolio Backup (전체 1009 file + REPORT.md + 7 csv)

본 디렉토리는 server `paper_exact/` 전체 1010 file 의 로컬 백업. 본 연구 narrative 외 archive 가치 + REPORT.md 의 분석 anchor.

## 디렉토리 구조

```
10_전체측정_백업/
├── B1_baseline_9cell/                       [9 file = paper §V-B Bernoulli baseline]
├── CaseA_단독대체_495/                     [495 file = 55 method × 9 cell - 미측정 5]
├── CaseB_결합_496/                          [496 file = 55 method × 9 cell - 미측정 4 + 1 extra]
└── REPORT_분석/                             [REPORT.md 1362 line + 7 csv]
```

## 측정 portfolio

총 1009 file (REPORT.md `Phase A 9 + Phase B 495 + Phase C 496 = 1000` + B1 9 = 1009)

### B1 (9 file, Phase A)
- `A1-DEEP_B1.json`, `A1-SIFT_B1.json`, `A1-SSN_B1.json`
- `A2-Fig7_B1.json`, `A2-Fig9_B1.json`
- `A4-sel_B1.json`
- `A5-scale-sf1_B1.json`, `A5-scale-sf10_B1.json`, `A5-scale-sf100_B1.json`

### CaseA (495 file, Phase B) — 단독 대체
- 9 cell × 55 method = 495 file
- 미측정 cell-method 페어 5 (정합성 위반 method 폐기로)
- 9 cell = A1-DEEP, A1-SIFT, A1-SSN, A2-Fig7, A2-Fig9, A4-sel, A5-scale-sf1, A5-scale-sf10, A5-scale-sf100
- 55 method = paradigm 8 × 평균 7 method (Cluster + Spatial + Streaming + DimRed + QMC + Quantization + Density + InfoTheoretic + 외 method)

### CaseB (496 file, Phase C) — 결합 산술 평균
- 9 cell × 55 method = 495 + 1 extra = 496 file
- est_final = (est_b1 + est_method) / 2.0

## REPORT_분석 (REPORT.md + 7 csv)

| File | Size | 내용 |
|---|---:|---|
| `REPORT_paper_exact_v11.md` | 1362 line | Phase A/B/C/D 전체 분석 + Wilcoxon + Cliff's δ + Hedges' g + paradigm rollup |
| `rq1_paper_exact_DEEP_sf1.csv` | ~180 KB | RQ1 bernoulli vs km20 DEEP sf=1 |
| `rq1_paper_exact_DEEP_sf10.csv` | ~180 KB | RQ1 bernoulli vs km20 DEEP sf=10 |
| `rq1_paper_exact_DEEP_sf100.csv` | ~180 KB | RQ1 bernoulli vs km20 DEEP sf=100 |
| `rq1_paper_exact_SIFT_sf100.csv` | ~180 KB | RQ1 bernoulli vs km20 SIFT sf=100 |
| `rq1_paper_exact_SimSearchNet++_sf100.csv` | ~200 KB | RQ1 bernoulli vs km20 SimSearchNet++ sf=100 |
| `rq2_paper_exact_DEEP_sf100.csv` | TBD | RQ2 5-way allocation DEEP sf=100 |
| `rq2_paper_exact_SIFT_sf100.csv` | TBD | RQ2 5-way allocation SIFT sf=100 |
| `A3-TPCDS_ECQO_detail.csv` | TBD | A3-TPCDS ECQO detail (separate cell) |

## 핵심 통계 결과 (REPORT §3+§4)

### Phase B (CaseA 단독 대체) paired Δ%
- minibatch_partial 9-cell mean: **−10.17% ★**
- 통계 일관 우위 5/9 cell (p<0.05)
- 단독 best method 15 개 (−5% ~ −12% 범위)

### Phase C (CaseB 결합) paired Δ%
- paired CaseB < CaseA **92.5%** (455/492, p<1e-45)
- Cliff's δ large better **63.0%** (311/494)
- Hedges' g large **55.7%** (275/494)
- one-sided p<0.05 outperform **45.3%** (224/494)
- negative control: CaseA 단독 대체 **0/493 = 0%**

### Paradigm rollup (CaseB mean Δ%)

| Paradigm | n | mean Δ% | 비고 |
|---|---:|---:|---|
| P10 Density | 1 | −11.93 | n=1, 약함 |
| P9 InfoTheoretic | 9 | −7.60 | hyperloglog |
| P3 Streaming | 44 | −6.63 | chao_weighted |
| P4 DimReduction | 104 | −6.03 | sparse_rp, pca1d |
| P2 Spatial | 107 | −5.57 | hilbert_real |
| P5 QMC | 62 | +1.47 | paradigm-level 만 보고 |
| P1 Cluster | 87 | +2.04 | |
| P6 Quantization | 53 | +8.44 | |

## 사용자 정책 폐기 method (REPORT §10)

### 정합성 위반 9
halton / sobol / lhs / hammersley / dense_rp / random_projection / dbscan / ccsketch / lsh / ams_count_sketch
- paper N=385 budget 위반 (각 method 가 자체 sampling 으로 추가 sample 사용)

### 측정 미커버 7
Tier 2 6: dirichlet / kernelpca / neuocard / birch / hdbscan / agglomerative
+ KDE 1: kde_parzen (5/14 07:39 kde_chain 폐기 결정)

### Algorithm audit drop 23 method
- 5/10 P1-P6 audit + 5/11 Phase 4 audit 의 결과
- ★3 hilbert PCA-alias (Faloutsos 1989 ❌)
- ★4 sparse_rp Li-Hastie-Church 2006 reference 정정

## Honest limitation (REPORT §10)

- 측정 portfolio 1009 file 외 미커버 cells 9 카테고리 정직 분류 (REPORT §10)
- byte-identical duplicates 7쌍 (REPORT §11)
- 평균적 method 의 paper 재현 변동 −4.3% 가 본 portfolio 추정 변동성과 동일 자릿수임 인정

## 출처

서버: `capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/`
REPORT: `_internal/validation/data/REPORT_paper_exact.md` (서버 → 로컬 sync v11)
handoff: `_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md`
