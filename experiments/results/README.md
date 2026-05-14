# experiments/results/ — 본 연구 실험 결과 (5/14 정리)

> **본 연구** (Exqutor §V-B Adaptive Sampling 재현 + 분포 인지 stratification ensemble augment) **의 모든 측정 결과 + 분석 + 부속 자료**. 5/15 박광현 미팅 + 5/27 최종 발표 + 6/11 보고서 base.

## 디렉토리 구조 (★ 사용자 정리 후, 5/14 16:00)

```
results/
├── README.md                                [본 파일]
│

│
├── analysis/                                [9 분석 file, 5/13 ~ 5/14]
│   ├── README.md                             [analysis 인덱스]
│   └── (9 *.md, 본 narrative 정량 source)
│
├── raw/                                     [server 측정 raw, 1304 json + 15 csv + 12 md]
│   ├── README.md                             [raw 종합 인덱스]
│   ├── 01_RQ1_논문_baseline_재현/                [paper §V-B B1 baseline 9 cell + RQ1 5 csv]
│   ├── 02_RQ2_5방식_표본할당/               [Bernoulli/Equal/Proportional/Neyman/Anti 5-way]
│   ├── 03_RQ3_단독대체_CaseA/                [단독 best minibatch_partial −10.17% (9-cell)]
│   ├── 04_RQ3_결합_CaseB/                    [결합 best Centroid tuple −7.37% (A2-Fig9)]
│   ├── 05_결합비율_alpha_sweep/                           [α=0.3/0.4/0.5/0.6/0.7, ★ 시나리오 B 확정]
│   ├── 06_클러스터수_K_민감도/                     [K=10/20/30, method 별 sensitivity]
│   ├── 07_저비용_근사_4후보/                  [Centroid + Hash + PCA + Iterative]
│   ├── 08_다중조인_재학습/                 [A2-Fig9 multi-join 864d concat]
│   ├── 09_다중벡터_A2_Fig8/              [A2-Fig8 single-table multi-column]
│   └── 10_전체측정_백업/     [전체 1009 file 백업 + REPORT_v11.md + 7 csv]
│
└── archive/                                 [W1~W4 sprint archive, 4/16 ~ 5/8]
    ├── 2026_05_08_cleanup/
    └── w1_w4_sprint_results/                 [master_drafts + rq1_motivation + rq2_aware + rq3_agnostic + cache_rq1 등]
```

> **figures**: `experiments/figures/paper_exact_v7/` (6 figure, 5/27 발표 anchor) — 별도 위치

## 활성 vs archive 분류

**활성** (현 5/27 발표 + 6/11 보고서 직접 인용):
- `analysis/` 9 분석 file
- `raw/` 1304 json + 15 csv (server 측정)
- `연구_한계점_4종_명시_5월5일회의록_기반.md` + `Exqutor_§V-B_Adaptive_Sampling_의사코드.md` (학술 명시)
- `experiments/figures/paper_exact_v7/` 6 figure

**archive** (W1~W4 sprint, paper-exact 전 4/16~5/8 측정):
- `archive/w1_w4_sprint_results/` 의 master_drafts + rq1_motivation + rq2_aware + rq3_agnostic + cache_rq1 (총 ~800 file)
- archive 인덱스: `archive/README.md`

## 본 narrative 와의 매핑

| narrative 단계 | source |
|---|---|
| §1 paper §V-B 위치 | `Exqutor_§V-B_Adaptive_Sampling_의사코드.md` (Algorithm 1 의사코드) |
| §3 폐기 39 method | `_internal/METHOD_REGISTRY.md` |
| §4 단독 대체 best −10.17% | `analysis/method_level_breakdown_20260513.md` + `raw/03_RQ3_단독대체_CaseA/` |
| §5 결합 best −7.37% | `analysis/centroid_tuple_cheap_approximation_results_20260513.md` + `raw/04_RQ3_결합_CaseB/` |
| §5 α sweep 시나리오 B 확정 | `analysis/alpha_sweep_results_20260514.md` + `raw/05_결합비율_alpha_sweep/` |
| §6 결합 < 단독 한계 | `analysis/alpha_sweep_results_20260514.md` |
| §7 결합 진짜 가치 | `analysis/method_level_breakdown_20260513.md` |
| §8 Pareto Top 5 + reservoir O(1) | `analysis/resource_efficiency_pareto_20260513.md` |
| §10 다중 테이블 Centroid tuple | `analysis/multi_join_restratification_results_20260513.md` + `raw/07_저비용_근사_4후보/` |
| K granularity 부록 | `analysis/km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` + `raw/06_클러스터수_K_민감도/` |
| 한계 (RQ_Limitation) | `연구_한계점_4종_명시_5월5일회의록_기반.md` |

## 본 연구 핵심 수치 (사용 source 와 연결)

| 항목 | 정량 | 출처 |
|---|---|---|
| paper Fig 12 재현 | mean qe_trim **1.618** vs paper 1.69 (**−4.3%**) | `raw/01_RQ1_논문_baseline_재현/` 9 B1 cell |
| RQ1 random sampling 부정확 | Bern sel=0.01 **1.748** → KM20 **1.637** (−6.35%) | `raw/01_RQ1_논문_baseline_재현/rq1_*.csv` |
| RQ2 Bern → Proportional | Bern → Prop **−9.38% ~ −9.53%** | `raw/02_RQ2_5방식_표본할당/rq2_*.csv` |
| RQ2 Neyman paradox | Anti 1.540 < Prop 1.580 < **Neyman 1.595** | `raw/02_RQ2_5방식_표본할당/` |
| RQ3 단독 best (9-cell mean) | minibatch_partial **−10.17%** | `raw/03_RQ3_단독대체_CaseA/단독_best_minibatch_partial/` |
| RQ3 결합 best (A2-Fig9 single) | Centroid tuple sparse_rp **−7.37%** | `raw/04_RQ3_결합_CaseB/결합_best_Centroid_tuple/` |
| α=0.5 best (산술 평균) | 4 method 中 3 method 가 α=0.5 best | `raw/05_결합비율_alpha_sweep/alpha_0.5_default/` |
| Pareto Top 5 | sparse_rp / chao_weighted / neuram / pca1d / hilbert | `analysis/resource_efficiency_pareto_20260513.md` |
| reservoir O(1) memory | 메모리 O(1) + −9.25% Δ% (anchor 수준) | `analysis/resource_efficiency_pareto_20260513.md` |

## 정리 history

- **4/16 ~ 5/8**: W1~W4 sprint 측정 (RQ1 motivation + RQ2 KM20 + RQ3 16 method)
- **5/9 ~ 5/14**: paper exact 측정 framework launch + 1065 file portfolio 회수
- **5/14 15:00**: W1~W4 sprint → `archive/w1_w4_sprint_results/` 이동
- **5/14 16:00**: `_internal/analysis/` (9 file) → `analysis/` + server raw (1304 file) → `raw/` (한국어 10 sub-dir)
- **5/14 16:05**: 사용자 추가 정리 — `paper_exact_v7/` 제거하고 `results/` 직속으로 통합
- **5/14 16:10**: 중복 `algorithm1_box.md` 제거 (`Exqutor_§V-B_Adaptive_Sampling_의사코드.md` 와 동일)

## 다른 자료 위치

| 영역 | 위치 |
|---|---|
| 측정 script | `_internal/scripts/measure_paper_exact.py` (1100 line) |
| handoff | `_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` |
| 본 narrative 산문 | `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v1.md` |
| 종합 이해 v2 (저녁 회의 base) | `submission/_drafts/속도는벡터_프로젝트_종합이해_v2.md` |
| METHOD_REGISTRY (57 method) | `_internal/METHOD_REGISTRY.md` |
| EXPERIMENT_REGISTRY | `_internal/EXPERIMENT_REGISTRY.md` |
| REPORT v11 (server, 1362 line) | server `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md` (로컬 backup: `raw/10_전체측정_백업/REPORT_paper_exact_v11.md`) |
| figures (6 figure) | `experiments/figures/paper_exact_v7/` |

---

작성: 2026-05-14 16:10 KST · 사용자 정리 후 (paper_exact_v7 제거, results 직속 통합) 반영 + narrative 매핑 + 핵심 수치 출처 명시
