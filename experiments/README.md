# experiments/ — 본 연구 측정 (5/14 update)

> **현 단계** (2026-05-14): paper exact 측정 1001 file (server-only) + 본 세션 추가 64 file = **총 1065 file portfolio**. 단독 best −10.17% (minibatch_partial, 9-cell mean) + 결합 best −7.37% (Centroid tuple sparse_rp, A2-Fig9). 5/15 박광현 D-1 + 5/27 최종 발표 D-13 + 6/11 보고서 D-28.

## 활성 디렉토리

```
experiments/
├── README.md                                [본 파일, 5/14 update]
├── _DROPPED_README.md                       [dropped scope audit log]
├── config/
│   └── experiment_params.yaml               [YAML 파라미터 정의, 4/16 기준]
├── plans/
│   └── RQ1_motivation_pipeline_20260414_162857.md  [W1 RQ1 motivation 설계]
│
├── figures/
│   ├── paper_exact_v7/                      [★ 활성 6 figure, 5/27 발표 anchor]
│   │   ├── F1_paradigm_rollup_caseB.png
│   │   ├── F2_cliffs_delta_bucket.png
│   │   ├── F3_caseA_vs_caseB.png
│   │   ├── F4_top_winners.png
│   │   ├── F5_effect_size.png
│   │   └── F6_narrative_diagram.png
│   └── archive/                             [W1~W4 sprint 옛 figure 8 sub-dir]
│
├── results/                                 [활성 3 건만, W1~W4 sprint 는 archive 로]
│   ├── RQ_Limitation_4종_명시.md            [★ 5/5 회의록 line 122-126, Limitation 4종 표준]
│   ├── phase_f/
│   │   └── algorithm1_box.md                [B1 baseline Algorithm 1 의사코드, reviewer attack defense]
│   └── archive/                             [W1~W4 sprint 정리됨, 5/14]
│       ├── README.md
│       ├── w1_w4_sprint_results/            [신규 archive, 5/14]
│       │   ├── master_drafts/               [W1~W4 master draft 5 건]
│       │   ├── 10cell_narrative/            [5/8 회의 자료]
│       │   ├── w2_sprint/                   [W2 5/7 sprint 종합]
│       │   ├── rq1_motivation/              [97 file, W1 4/16 RQ1 motivation]
│       │   ├── rq2_aware/                   [14 file, W3 5/6-5/7 KM20 alloc]
│       │   ├── rq3_agnostic/                [245 file, W4 5/8 RQ3 16 method]
│       │   ├── cache_rq1/                   [434 file, 5/8-5/9 server mirror]
│       │   └── phase_g/                     [REPORT.md (5/10, paper-exact 직전)]
│       └── 2026_05_08_cleanup/              [기존 archive, 5/7 옛 km/opq/reservoir 등]
│
└── code/                                    [활성 측정 script 없음 — paper-exact 는 _internal/scripts/]
    ├── README.md
    └── archive/
        └── w1_w4_scripts/                   [W1~W4 sprint script 4 subdir]
            ├── rq1/                         [27 file]
            ├── rq2/                         [5 file]
            ├── rq3/                         [43 file]
            └── local_analysis/              [42 file, figure generation]
```

## 본 연구 핵심 자료 위치

### 1. 측정 portfolio (server-only)

paper exact 측정 raw json 은 server `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/` 에 1001 file. 본 세션 추가 회수 64 file 는 별도 디렉토리:

- `paper_exact_mj_restrat/` (8) — multi-join 재계층화
- `paper_exact_centroid_tuple/` (8) — Centroid tuple cheap 근사
- `paper_exact_b1_hash/` (8) — Hash bucketing
- `paper_exact_b2_pca/` (8) — PCA preprocessing
- `paper_exact_b3_iter/` (8) — Iterative refinement
- `paper_exact_a2fig8_mv/` (8) — A2-Fig8 multi-vector
- `paper_exact_alpha_sweep/` (16) — α sweep 4×4

server 접속: `ssh capstone2026@165.132.140.240`.

### 2. 분석 file (local, `_internal/analysis/`)

- `multi_join_restratification_results_20260513.md` (시나리오 A.5 Hybrid)
- `centroid_tuple_cheap_approximation_results_20260513.md` (★ 새 method axis)
- `resource_efficiency_pareto_20260513.md` (Pareto + reservoir O(1))
- `alpha_sweep_results_20260514.md` (★ 시나리오 B 확정)
- `cheap_approximation_extended_results_20260514.md` (cheap 4 후보 종합)
- `multi_cell_km_based_learning_comparison_20260513.md`
- `km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` (K=10/20/30)
- `km_granularity_sensitivity_K10_vs_K20_20260513.md`
- `method_level_breakdown_20260513.md`

### 3. 측정 script (local, `_internal/scripts/`)

paper exact 측정 main script:
- `measure_paper_exact.py` — paper §V-B 재현 + 우리 method 측정 (1100 line)
- `_measure_common.py` — 공통 측정 library + N_STRATA=20 default
- `analyze_paper_exact.py` — 측정 결과 분석
- `figures_paper_exact.py` — paper_exact_v7/F1~F6.png 생성

### 4. handoff (현재 상태)

`_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` — 5/14 07:21 finalize, 본 세션 18.5h 종합.

### 5. narrative (저녁 회의 base)

- `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v1.md` (5/14, 10 단계 산문 + §11 핵심 6 method + §12 17 사용 method)
- `submission/_drafts/속도는벡터_프로젝트_종합이해_v1.md` (5/14, 종합 이해 문서 733 line)
- `submission/_drafts/속도는벡터_5_15_박광현미팅_핵심정리_v1.md` (5/15 미팅 자료)
- `submission/_drafts/속도는벡터_5_27_최종발표_storyline_v1.md` (5/27 발표 storyline)
- `submission/_drafts/속도는벡터_6_11_최종보고서_outline_v1.md` (6/11 보고서 outline)
- `submission/_drafts/속도는벡터_팀원_상황공유_v1.md` (팀원 공유)
- `submission/_drafts/속도는벡터_5_27_deck_v6_update_plan_20260514.md` (5/27 deck v6 plan)

## 정리 history

- **4/16 ~ 5/8**: W1~W4 sprint (RQ1 motivation + RQ2 KM20 + RQ3 16 method 비교) → archive
- **5/9 ~ 5/14**: paper exact 측정 framework launch + 1065 file portfolio 회수
- **5/14 15:42**: 본 정리 작업 (회의 의견 #9 반영, archive 디렉토리 신규 생성 + W1~W4 sprint 결과 이동 + README 3 건 작성)

## 활성 vs archive 분류 기준

- **활성**: 5/27 최종 발표 + 6/11 보고서에 직접 인용되는 자료 (paper_exact_v7 6 figure + RQ_Limitation + phase_f algorithm1 + _DROPPED_README)
- **archive**: 중간 발표 (4/28) 시점 자료 + paper exact 측정으로 superseded 된 W1~W4 sprint 산출물

archive 안 자료는 paper exact REPORT v11 (server) + 본 narrative v1 으로 superseded 되어 직접 인용은 안 되지만, 측정 변천 timeline 의 reference 로 보존.

## 본 연구 narrative 요약

본 연구는 Exqutor 논문 (arXiv:2512.09695v2) 의 §V-B Adaptive Sampling 영역 (인덱스 부재 시 Bernoulli + 모멘텀 기반 동적 sample size) 에 대해 paper exact 재현 + 분포 인지 stratification ensemble augment 의 정량 가치를 검증.

핵심 narrative 흐름 (10 단계):
1. 문제: skew 영역 베르누이 부정확
2. 탐색: 56 method × 8 갈래 × 9 측정 환경
3. 폐기: 39 method (자원 7 + audit 23 + 정합성 9)
4. 단독 대체: best minibatch_partial −10.17% (CaseA, 9-cell mean)
5. 결합 시도: best Centroid tuple −7.37% (CaseB, A2-Fig9)
6. 결합 한계: 결합 < 단독
7. 결합 진짜 가치: method 선택 안정성 + cell spread 줄임
8. 자원 효율: Pareto Top 5 = 12 anchor consistency 일치, reservoir O(1) 산업 적용
9. 권장: 단독 대체 우선 + 결합 보조 + method-aware
10. 다중 테이블: Centroid tuple 로 원칙 그대로 적용

자세한 내용은 `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v1.md` 또는 `submission/_drafts/속도는벡터_프로젝트_종합이해_v1.md` 참조.

---

작성: 2026-05-14 15:42 KST · 회의 의견 #9 반영 archive 정리 완료 (W1~W4 sprint → archive, paper exact 시점 narrative 로 update)
이전 README (W1 시점 narrative) 는 git history 에 보존.
