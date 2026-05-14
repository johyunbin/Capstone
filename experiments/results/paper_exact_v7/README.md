# experiments/results/paper_exact_v7/ — 본 연구 실험 결과 통합 (5/14 정리)

> **본 연구 (Exqutor §V-B 재현 + 분포 인지 stratification ensemble augment) 의 모든 실험 결과 + 분석 file + figure 통합**. 5/15 박광현 미팅 + 5/27 최종 발표 + 6/11 보고서 base.

## 디렉토리 구조

```
paper_exact_v7/
├── README.md                                [본 파일]
├── analysis/                                [9 분석 file, 5/13~5/14]
│   └── (9 *.md file, 본 narrative source)
├── figures/                                 [위치: experiments/figures/paper_exact_v7/]
│   └── (F1~F6 6 figure, 5/27 발표 anchor)
└── raw/                                     [server 측정 raw, 5/14 정리 진행]
    └── (server 1065 file 中 핵심 file 가져온 결과)
```

## analysis/ — 9 분석 file (5/13~5/14)

본 연구 narrative 의 정량 수치 source. 각 file 의 핵심 finding:

| File | 작성 | 핵심 finding |
|---|---|---|
| `multi_join_restratification_results_20260513.md` | 5/13 16:20 | 시나리오 A.5 (Hybrid). single carry-over (A) vs multi-join 재학습 (B). CaseA 모드에서 sparse_rp + chao_weighted 만 B 가 우위 (−2.63 ~ −3.55%p) |
| `centroid_tuple_cheap_approximation_results_20260513.md` | 5/13 19:57 | ★ 새 method axis "Cheap 근사 친화도". Centroid tuple 학습 비용 0 + CaseB 보편 우위 (4 method 모두 평균 −0.84%p 추가) |
| `resource_efficiency_pareto_20260513.md` | 5/13 23:56 | 자원 효율 Pareto frontier. Top 5 = sparse_rp / chao_weighted / neuram / pca1d / hilbert. 산업 적용 3 영역 + reservoir O(1) 산업 적용 핵심 |
| `alpha_sweep_results_20260514.md` | 5/14 00:13 | ★ 시나리오 B 확정. α sweep 16 measurement. α=0.5 (산술 평균) best, U-shape sensitivity. 결합 best −7.37% < 단독 best −10.17% |
| `cheap_approximation_extended_results_20260514.md` | 5/14 07:05 | cheap 근사 4 후보 (Centroid tuple / Hash / PCA / Iter). Centroid tuple 만 robust. 나머지 spread/marginal/harmful |
| `multi_cell_km_based_learning_comparison_20260513.md` | 5/13 | KM 기반 학습 multi-cell 비교 |
| `km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` | 5/13 03:00 | K granularity 3-way (K=10/20/30) × 4 anchor × 5 cells = 60 paired. sparse_rp + chao_weighted K=20 sweet spot, hilbert_real + hyperloglog K-robust |
| `km_granularity_sensitivity_K10_vs_K20_20260513.md` | 5/13 | K=10 vs K=20 비교 (이전 시점) |
| `method_level_breakdown_20260513.md` | 5/13 | method-level breakdown 9-cell paired Δ% (각 method 의 mean / std / 일관성) |

## figures/ — 6 figure (위치: experiments/figures/paper_exact_v7/)

5/27 최종 발표 anchor. 본 연구의 narrative 흐름 시각화.

| File | 내용 |
|---|---|
| F1_paradigm_rollup_caseB.png | 8 paradigm CaseB Δ% bar chart |
| F2_cliffs_delta_bucket.png | Cliff's δ effect size 분포 |
| F3_caseA_vs_caseB.png | 단독 대체 vs 결합 mode 비교 |
| F4_top_winners.png | 안정 우위 method top winners |
| F5_effect_size.png | Hedges' g + Cliff's δ |
| F6_narrative_diagram.png | 본 연구 narrative 흐름 도식 |

## raw/ — server 측정 raw (5/14 정리 진행 중)

server `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact*/` 의 1065 file 中 narrative 핵심 file 가져옴.

구조 (실험 데이터 정리 agent 진행 후 update):
```
raw/
├── 01_RQ1_paper_baseline/
├── 02_RQ2_5way_allocation/
├── 03_RQ3_CaseA_단독대체/
├── 04_RQ3_CaseB_결합/
├── 05_α_sweep/
├── 06_K_granularity/
├── 07_cheap_근사_4후보/
├── 08_multi_join_재학습/
└── 09_A2-Fig8_multi_vector/
```

각 sub-dir 에 README.md (file 명 → 내용 매핑).

## 본 narrative 와의 매핑

| narrative 단계 | source file |
|---|---|
| §3 폐기 39 method | `_internal/METHOD_REGISTRY.md` + 사용자 정책 분류 |
| §4 단독 대체 best −10.17% | `method_level_breakdown_20260513.md` + REPORT v11 (server) |
| §5 결합 시도 best −7.37% | `centroid_tuple_cheap_approximation_results_20260513.md` + `alpha_sweep_results_20260514.md` |
| §6 결합 < 단독 한계 | `alpha_sweep_results_20260514.md` |
| §7 결합 진짜 가치 | `method_level_breakdown_20260513.md` |
| §8 자원 효율 Pareto Top 5 + reservoir O(1) | `resource_efficiency_pareto_20260513.md` |
| §10 다중 테이블 Centroid tuple | `multi_join_restratification_results_20260513.md` + `centroid_tuple_cheap_approximation_results_20260513.md` |
| K granularity 부록 | `km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` |

## 정리 이력

- **5/13 ~ 5/14**: 9 분석 file 작성 시점 (위치: `_internal/analysis/`)
- **5/14 16:00**: 본 디렉토리 (`experiments/results/paper_exact_v7/analysis/`) 로 이동, 통합 README 작성

## 다른 자료 위치

- 측정 script: `_internal/scripts/measure_paper_exact.py` (1100 line)
- handoff: `_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md`
- 본 narrative 산문: `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v1.md`
- 종합 이해 v2 (저녁 회의): `submission/_drafts/속도는벡터_프로젝트_종합이해_v2.md`
- METHOD_REGISTRY (57 method paradigm 분류): `_internal/METHOD_REGISTRY.md`
- EXPERIMENT_REGISTRY (9 cells × 56 method × 3 modes): `_internal/EXPERIMENT_REGISTRY.md`
- REPORT v11 (server 1001 file 자동 생성, 1362 line): `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md` (server)

---

작성: 2026-05-14 16:00 KST · 사용자 명시 "실험 결과 디렉토리 results 로 이동 + 지침 정리"
