# Paper Exact v7 — 본 연구 측정 raw 데이터 (서버 → 로컬 동기화)

**작성일**: 2026-05-14
**소스**: `capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/`
**총 file 수**: 1304 json + 15 csv + 9 README.md = 1328 file
**총 size**: 8.9 MB

본 디렉토리는 캡스톤 2026-1 학기 본 연구 narrative (단독 best −10.17%, 결합 best −7.37%, Pareto Top 5) 의 모든 raw 측정 데이터를 담는다. 서버의 1066 file (paper_exact 1010 + 외 11 디렉토리 168) 을 본 narrative 의 의미 단위로 재조직 + 한국어 디렉토리 명명으로 file 명만 보고도 무엇인지 알 수 있게 정리.

---

## 본 연구 narrative anchor

본 raw 데이터가 직접 입증하는 핵심 결과 (출처: `_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` §10):

| 항목 | 정량 | 출처 raw |
|---|---|---|
| paper Fig 12 재현 | mean qe_trim **1.618** (paper 1.69 vs **−4.3%**) | `01_RQ1_논문_baseline_재현/` 9 B1 cell |
| RQ1 random sampling 부정확 | bernoulli mean=1.638 (sel 0.01) vs km20=1.582 | `01_RQ1_논문_baseline_재현/rq1_*.csv` |
| RQ2 5-way allocation 우위 | Bern→Prop **−9.53%** (paradox: Anti 1.540 < Prop 1.580 < Neyman 1.595) | `02_RQ2_5방식_표본할당/rq2_*.csv` |
| 단독 best (RQ3 CaseA) | minibatch_partial **−10.17%** (9-cell mean) | `03_RQ3_단독대체_CaseA/단독_best_minibatch_partial/` |
| 결합 best (RQ3 CaseB) | Centroid tuple sparse_rp **−7.37%** (A2-Fig9 cell) | `04_RQ3_결합_CaseB/결합_best_Centroid_tuple/` |
| 결합 평균 vs 단독 평균 | paired CaseB < CaseA **92.5%** (455/492, p<1e-45) | `10_전체측정_백업/REPORT_분석/` |
| Pareto Top 5 (정확도 + 자원 효율) | sparse_rp / chao_weighted / pca1d / hilbert_real / hyperloglog | `03/pareto_top5_5method/` + `04/pareto_top5_5method/` |
| α sweep 시나리오 B 확정 | α=0.5 default 가 4 α (0.3, 0.4, 0.5, 0.6, 0.7) 中 안정 | `05_결합비율_alpha_sweep/` |

---

## 디렉토리 구조

```
raw/
├── README.md  (본 file)
├── 01_RQ1_논문_baseline_재현/                     [9 B1 cell + 5 RQ1 csv]
├── 02_RQ2_5방식_표본할당/                    [2 csv = 5-way allocation 모드별 raw]
├── 03_RQ3_단독대체_CaseA/                     [Pareto Top 5 × 9 cell + minibatch_partial × 9 cell]
│   ├── pareto_top5_5method/                    [45 file = 5 method × 9 cell]
│   └── 단독_best_minibatch_partial/           [9 file = 9 cell CaseA]
├── 04_RQ3_결합_CaseB/                         [Pareto Top 5 × 9 cell + Centroid tuple]
│   ├── pareto_top5_5method/                    [45 file = 5 method × 9 cell]
│   └── 결합_best_Centroid_tuple/              [8 file = A2-Fig9 × 4 method × 2 mode]
├── 05_결합비율_alpha_sweep/                                 [16 file = 4 α × 4 method + 4 file alpha 0.5 default]
│   ├── alpha_0.3/  alpha_0.4/                  [shrinkage = paper default 보다 약함]
│   ├── alpha_0.5_default/                       [paper §V-B Eq 5 default (paper_exact_centroid_tuple 와 동일)]
│   └── alpha_0.6/  alpha_0.7/                   [shrinkage = paper default 보다 강함]
├── 06_클러스터수_K_민감도/                           [K=10/20/30 비교]
│   ├── K10/  K20_default_paper/  K30/          [120 file = 5 cell × 4 method × 2 mode × 3 K]
├── 07_저비용_근사_4후보/                       [Centroid + Hash B1 + PCA B2 + Iter B3]
│   ├── centroid_tuple/   hash_bucketing_B1/    [A2-Fig9 cell × 4 method × 2 mode = 8 file 각]
│   ├── pca_preprocessing_B2/  iterative_refinement_B3/
├── 08_다중조인_재학습/                       [8 file = mj_restrat A2-Fig9 4 method × 2 mode]
├── 09_다중벡터_A2_Fig8/                    [8 file = a2fig8_mv 4 method × 2 mode]
└── 10_전체측정_백업/           [전체 1009 file 백업 + REPORT.md + csv]
    ├── B1_baseline_9cell/                       [9 paper §V-B Bernoulli baseline]
    ├── CaseA_단독대체_495/                     [495 = 55 method × 9 cell - 미측정 5]
    ├── CaseB_결합_496/                          [496 = 55 method × 9 cell - 미측정 4 + 1 extra]
    └── REPORT_분석/                             [REPORT_paper_exact_v11.md 1362 line + rq1/rq2/A3-TPCDS csv 7]
```

---

## file 명 규칙

### CaseA / CaseB (RQ3 단독대체 / 결합)
- 형식: `{cell}_{mode}_{method}.json`
- cell: `A1_DEEP`, `A1_SIFT`, `A1_SSN`, `A2_Fig7`, `A2_Fig9`, `A4_sel`, `A5_sf1`, `A5_sf10`, `A5_sf100`
- mode: `CaseA` = paper §V-B Bernoulli **단독 대체**, `CaseB` = paper Bernoulli + 우리 method **산술 평균 결합** (`est_final = (est_b1 + est_method) / 2.0`)
- method: 영어 원표기 (`sparse_rp`, `chao_weighted`, `hilbert_real`, `hyperloglog`, `pca1d`, `minibatch_partial` 등)

### B1 (paper §V-B Bernoulli baseline)
- 형식: `{cell}_B1.json` 또는 `{cell}_B1_paper_baseline.json` (`01_RQ1_논문_baseline_재현/` 에서)
- paper Eq 1-6 의 unstratified Bernoulli 추정 (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, N=385)

### α sweep
- 형식: `A2-Fig9_CaseB_{method}.json` (디렉토리 명이 α 값)
- α = paper Eq 5 의 cube root shrinkage 계수 (default 0.5)

### K granularity
- 형식: `{cell}_{mode}_{method}.json` (디렉토리 명이 K 값)
- K = stratification 분할 수 (paper default K=20)

---

## json 구조 (sample)

```json
{
  "cell": "A1-DEEP",
  "fig": "Fig 5/6",
  "dataset": "DEEP",
  "sf": 100,
  "mode": "CaseA",
  "method": "minibatch_partial",
  "n_queries": 1000,
  "trials": 10,
  "avg_q_error_trimmed": 1.353,    ← CaseA Δ% 계산 시 분자
  "trial_results": [
    {"trial": 0, "avg_q_error_finite": 1.5, "final_size": 568, "final_eta": 0.082, ...},
    ...
  ]
}
```

CaseA / CaseB Δ% = (avg_q_error_trimmed - B1.avg_q_error_trimmed) / B1.avg_q_error_trimmed × 100

---

## 핵심 finding 요약 (REPORT_paper_exact_v11.md 발췌)

### Phase B (CaseA = 단독 대체) Δ% 정리

| Cell | best method | B1 | CaseA | Δ% |
|---|---|---:|---:|---:|
| A1-DEEP | **minibatch_partial** | 1.613 | **1.353** | **−15.92%** |
| A1-SIFT | **minibatch_partial** | 1.670 | **1.301** | **−21.73%** |
| A1-SSN | sparse_rp | 1.621 | 1.494 | −7.66% |
| A2-Fig7 | **minibatch_partial** | 1.633 | **1.413** | **−12.61%** |
| A2-Fig9 | **minibatch_partial** | 1.528 | **1.353** | **−10.71%** |
| A4-sel | pca1d | 5.984 | 5.952 | −0.43% |
| A5-scale-sf1 | **minibatch_partial** | 1.617 | **1.470** | **−9.11%** |
| A5-scale-sf10 | **minibatch_partial** | 1.528 | **1.353** | **−10.71%** |
| A5-scale-sf100 | **minibatch_partial** | 1.613 | **1.353** | **−15.92%** |
| **9-cell mean** | minibatch_partial | 2.090 | **1.877** | **−10.17%** ★ |

### Phase C (CaseB = 결합) Δ% 정리

| Cell | best method | B1 | CaseB | Δ% |
|---|---|---:|---:|---:|
| A1-DEEP | **chao_weighted** | 1.613 | **1.436** | **−10.58%** |
| A1-SIFT | **chao_weighted** | 1.670 | **1.446** | **−13.04%** |
| ... | (생략, REPORT §4) | | | |
| **A2-Fig9 Centroid sparse_rp** (★) | | 1.528 | **1.416** | **−7.37%** ★ |

### Pareto Top 5

| Method | paradigm | fit 시간 | 9-cell CaseA Δ% mean | 9-cell CaseB Δ% mean |
|---|---|---:|---:|---:|
| **sparse_rp** | 차원 축소 (Li-Hastie-Church 2006) | 0.1s | TBD | TBD |
| **chao_weighted** | 스트리밍 (Chao 1982) | 0.5s | TBD | TBD |
| **pca1d** | 차원 축소 (Pearson 1901) | 0.5s | TBD | TBD |
| **hilbert_real** | 공간 분할 | 0.1-0.5s | TBD | TBD |
| **hyperloglog** | 정보 이론 (Flajolet 2007) | 0.5s | TBD | TBD |

TBD: REPORT §10 자원 효율 Pareto frontier 에서 정량 확인.

---

## 검증 자료

- `10_전체측정_백업/REPORT_분석/REPORT_paper_exact_v11.md` (1362 line) — Phase A/B/C/D 전체 분석 + Wilcoxon + Cliff's δ + Hedges' g
- `_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` §10 — 본 세션 18.5h 종합

## 출처 + 재현

서버 측정 script: `_internal/scripts/measure_paper_exact.py` + `figures_paper_exact.py`
파라미터: `experiments/config/paper_exact_hyperparam.yaml` (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, N=385, K=20)
서버 작업 디렉토리: `capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/`
