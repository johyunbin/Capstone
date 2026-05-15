# experiments/results/raw/ — dataset 단일 기준 그룹화 (5/15 11:15 reorganize)

> **재정리 일자**: 2026-05-15 11:15 KST · **base**: 1352 file (json 1336 + csv 15 + REPORT 1) · **소스**: 서버 cache/rq3/paper_exact + 추가 측정
>
> **사용자 명시 reorganize**: dataset 단일 기준 그룹화 (handoff v23 의 dataset/sf/sel 영역 reorganize 정책 적용)
>
> **이전 구조**: 01_RQ1, 02_RQ2, ..., 10_paper_exact_base (RQ-별 / 측정 별 분류)
> **새 구조**: dataset 단일 기준 (DEEP/SIFT/SSN/YFCC/DEEP+WIKI/DEEP+CC3M/TPCDS), 측정 영역은 sub-folder 로 보존

---

## 1. dataset 매핑 (★ anchor)

| Dataset 디렉토리 | dimension | cells (paper Fig 매핑) | file 수 |
|---|---:|---|---:|
| **DEEP_96d/** | 96d | A1-DEEP (Fig 5/6/12) + A4-sel (Fig 13 sel=0.001) + A5-scale-sf{1,10,100} (Fig 14) | 694 |
| **SIFT_128d/** | 128d | A1-SIFT (Fig 5/6/12) | 149 |
| **SSN_256d/** | 256d | A1-SSN (Fig 5/6/12, SimSearchNet++) | 149 |
| **YFCC_192d/** | 192d | A2-Fig7 (Fig 7, YFCC) | 147 |
| **DEEP+WIKI_864d/** | 864d | A2-Fig9 (Fig 9 cross-table) + α sweep + cheap 근사 + multi-join | 215 |
| **DEEP+CC3M_multi-vector_scope외/** | (4 method 만) | A2-Fig8 (Fig 8 multi-vector, paper §V-A scope 외) | 12 |
| **TPCDS_ECQO_scope외/** | (REPORT csv 만) | A3-TPCDS (Fig 10/11 ECQO, paper §V-A scope 외) | 1 |
| **REPORT_분석/** | - | REPORT v11 + 5 csv (RQ1 paper exact summary) | 분석 |
| **_archived_RQ_README/** | - | 옛 RQ-별 디렉토리 README 보존 (5 file) | 보존 |
| **합계** | | | **1352 file** |

---

## 2. 각 dataset 디렉토리 내 sub-folder 구조

각 dataset 디렉토리는 cell × 측정 영역 sub-folder 로 정리됨:

### 2.1 DEEP_96d/
```
DEEP_96d/
├── B1_baseline_paper_exact/         (B1 baseline, A1-DEEP/A4-sel/A5-scale-sf{1,10,100} 각 cell × 1 trial)
├── A1-DEEP_paper_main/              (sf=100, sel=0.01, paper exact base)
│   ├── CaseA/                       (단독 대체 method × 56)
│   └── CaseB/                       (결합 method × 56)
├── A1-DEEP_RQ1_baseline/            (RQ1 paper baseline 재현)
├── A1-DEEP_RQ3_CaseA/               (단독 대체 detail + pareto Top 5)
├── A1-DEEP_RQ3_CaseB/               (결합 detail + pareto Top 5)
├── A1-DEEP_K_granularity/           (K=10/20/30, 5/12 paper exact base)
├── A4-sel_paper_main/               (sf=100, sel=0.001, paper Fig 13)
│   ├── CaseA/
│   └── CaseB/
├── A5-scale-sf1_paper_main/         (sf=1)
├── A5-scale-sf1_K_granularity/      (5/14 SF axis K=10/30)
├── A5-scale-sf10_*/                 (sf=10)
└── A5-scale-sf100_*/                (sf=100, scale)
```

### 2.2 DEEP+WIKI_864d/
```
DEEP+WIKI_864d/
├── B1_baseline_paper_exact/
├── A2-Fig9_paper_main/              (cross-table, paper Fig 9)
│   ├── CaseA/
│   └── CaseB/
├── A2-Fig9_RQ1_baseline/
├── A2-Fig9_RQ3_CaseA/
├── A2-Fig9_RQ3_CaseB/
├── A2-Fig9_K_granularity/           (K=10/20/30)
├── A2-Fig9_alpha_sweep/             (5/14, α=0.3/0.4/0.5/0.6/0.7)
│   ├── alpha_0.3/
│   ├── alpha_0.4/
│   ├── alpha_0.5_default/
│   ├── alpha_0.6/
│   └── alpha_0.7/
├── A2-Fig9_cheap_approximation/     (5/13, Centroid/Hash/PCA/Iter)
└── A2-Fig9_multi_join_restratification/  (5/13, carry-over A vs 재학습 B)
```

### 2.3 SIFT_128d / SSN_256d / YFCC_192d / DEEP+CC3M / TPCDS

```
SIFT_128d/
├── B1_baseline_paper_exact/
├── A1-SIFT_paper_main/{CaseA,CaseB}/
├── A1-SIFT_RQ1_baseline/
├── A1-SIFT_RQ2_5way_allocation/    (RQ2 csv)
├── A1-SIFT_RQ3_CaseA/
├── A1-SIFT_RQ3_CaseB/
└── A1-SIFT_K_granularity/

SSN_256d/  ← A1-SSN 영역 영역 동일 구조
YFCC_192d/ ← A2-Fig7 영역 영역 동일 구조
DEEP+CC3M_multi-vector_scope외/  ← A2-Fig8, paper §V-A scope 외
TPCDS_ECQO_scope외/  ← A3-TPCDS REPORT csv 만
```

---

## 3. 본 연구 narrative anchor (출처: handoff v17/v25)

| 항목 | 정량 | 출처 raw |
|---|---|---|
| paper Fig 12 재현 | mean qe_trim **1.618** (paper 1.69 vs −4.3%) | `*/B1_baseline_paper_exact/` 9 cell |
| RQ1 random sampling 부정확 | bernoulli mean=1.638 vs km20=1.582 (sel 0.01) | `DEEP_96d/A1-DEEP_RQ1_baseline/`, `SIFT_128d/.../RQ1_baseline/`, `SSN_256d/.../RQ1_baseline/` |
| RQ2 5-way allocation | Bern→Prop −9.53% (paradox: Anti 1.540 < Prop 1.580 < Neyman 1.595) | `DEEP_96d/A1-DEEP_RQ2_*/`, `SIFT_128d/A1-SIFT_RQ2_*/` |
| 단독 best (RQ3 CaseA) | minibatch_partial **−10.17%** (9-cell mean) | `DEEP_96d/A1-DEEP_RQ3_CaseA/단독_best_minibatch_partial/` (외 9 cell) |
| 결합 best (RQ3 CaseB) | Centroid tuple sparse_rp **−7.37%** (A2-Fig9) | `DEEP+WIKI_864d/A2-Fig9_cheap_approximation/centroid_tuple/` |
| paired CaseB < CaseA | **92.5%** (455/492, p<1e-45) | `REPORT_분석/REPORT_paper_exact_v11.md` §3 |
| Pareto Top 5 cross-validation | 9 cell × 5 method = 100% coverage, paired 97.78% | `analysis/Pareto_Top5_method_cell_cross_validation_20260515_0250.md` |
| α sweep 시나리오 B 확정 | α=0.5 default 가 안정 | `DEEP+WIKI_864d/A2-Fig9_alpha_sweep/` |

---

## 4. 본 연구 외 측정 정직 disclosure

| 분류 | 디렉토리 | 이유 |
|---|---|---|
| paper §V-A multi-vector scope 외 | `DEEP+CC3M_multi-vector_scope외/` | A2-Fig8 (paper Fig 8). 본 연구 §V-B 단일 테이블 contribution 영역 외 |
| paper §V-A ECQO scope 외 | `TPCDS_ECQO_scope외/` | A3-TPCDS (paper Fig 10/11). 본 연구 §V-B 외 |
| 5/15 새벽 측정 (B1 variance archive) | `experiments/results/archive/06_K_민감도_5_15_repeat_B1_variance/` | B1 random variance 영역 큰 영역, archive 이동. 자세는 `analysis/B1_variance_root_cause_종합분석_20260515_0150.md` |

---

## 5. 분석 보고서 위치

raw/ 의 정량 분석 결과는 `experiments/results/analysis/` 에 위치 (총 14 분석 file, 5/13 ~ 5/15):

| 분석 file | 핵심 finding |
|---|---|
| `B1_variance_root_cause_종합분석_20260515_0150.md` | B1 inherent CV 6% + run-level bias ±10-25% |
| `측정_미커버_영역_종합_inventory_20260515_0205.md` | 9 cell × 56 method 98.2% cover + 미커버 우선순위 |
| `Pareto_Top5_method_cell_cross_validation_20260515_0250.md` | Pareto Top 5 paired 97.78% (★) |
| `K_granularity_dimension_dependent_종합검증_20260515_0310.md` | dim-K 가설 약함 + run-level bias |
| 외 10 분석 file (5/13 base) | (analysis/README.md 참조) |

---

## 6. 옛 디렉토리 → 새 dataset 매핑 (5/15 reorganize)

| 옛 디렉토리 (~5/14) | 새 위치 (5/15 11:15~) |
|---|---|
| `01_RQ1_논문_baseline_재현/` | 각 dataset 디렉토리 안 `*_RQ1_baseline/` |
| `02_RQ2_5방식_표본할당/` | `DEEP_96d/A1-DEEP_RQ2_*/`, `SIFT_128d/A1-SIFT_RQ2_*/` |
| `03_RQ3_단독대체_CaseA/` | 각 dataset 디렉토리 안 `*_RQ3_CaseA/` |
| `04_RQ3_결합_CaseB/` | 각 dataset 디렉토리 안 `*_RQ3_CaseB/` |
| `05_결합비율_alpha_sweep/` | `DEEP+WIKI_864d/A2-Fig9_alpha_sweep/` |
| `06_클러스터수_K_민감도/` | 각 dataset 디렉토리 안 `*_K_granularity/` |
| `07_저비용_근사_4후보/` | `DEEP+WIKI_864d/A2-Fig9_cheap_approximation/` |
| `08_다중조인_재학습/` | `DEEP+WIKI_864d/A2-Fig9_multi_join_restratification/` |
| `09_다중벡터_A2_Fig8/` | `DEEP+CC3M_multi-vector_scope외/A2-Fig8_multi_vector_paper_main/` |
| `10_전체측정_백업/B1_baseline_9cell/` | 각 dataset 디렉토리 안 `B1_baseline_paper_exact/` |
| `10_전체측정_백업/CaseA_단독대체_495/` | 각 dataset 디렉토리 안 `*_paper_main/CaseA/` |
| `10_전체측정_백업/CaseB_결합_496/` | 각 dataset 디렉토리 안 `*_paper_main/CaseB/` |
| `10_전체측정_백업/REPORT_분석/REPORT_paper_exact_v11.md` | `REPORT_분석/REPORT_paper_exact_v11.md` |
| `10_전체측정_백업/REPORT_분석/*.csv` | 각 dataset 디렉토리 안 `REPORT_분석/` |

---

## 7. archive

5/15 새벽 measurement (B1 variance issue) 56 file:
- `experiments/results/archive/06_K_민감도_5_15_repeat_B1_variance/_run_5_15_repeat/`

자세는 `analysis/B1_variance_root_cause_종합분석_20260515_0150.md` 참조.

---

작성: 2026-05-15 11:15 KST · 사용자 명시 dataset 단일 기준 reorganize 진행 (handoff v23 의 reorganize 정책 적용) · 1352 file git mv 보존 · paper Fig 매핑 + 측정 영역 sub-folder + narrative anchor + 정직 disclosure
