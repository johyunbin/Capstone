# experiments/ — 본 연구 측정 (2026-05-19 갱신)

> **현 단계**: 3-way matched 캠페인 완료 — **1508 측정** (B1·CaseA·CaseB 각 1508). 결합(CaseB) vs 대조군(B1) 추정오차 개선 측정 **89.1%** (중앙값 Δ% −4.38%). 측정 종료, 6/11 최종보고서 작성 단계.

본 연구는 Exqutor 논문(arXiv:2512.09695v2) §V-B Adaptive Sampling 의 **표본 선택(sample selection) 단계** 하나만 — 무작위 Bernoulli → 분포 인지 stratification — 으로 바꾸는 개입의 효과를 전 데이터셋·전 조작 변인에 걸쳐 검증한다. 카디널리티 추정 알고리즘·식 1-6·표본 예산 N=385 는 논문 그대로.

## 디렉토리 구조

```
experiments/
├── README.md                   본 파일
├── config/
│   └── experiment_params.yaml   실험 파라미터 정의
├── code/
│   ├── README.md
│   └── archive/2026_04_W1_W4_초기실험_scripts/   초기 sprint script (활성 측정·도구는 _internal/scripts/)
├── figures/
│   ├── paper_exact_v13/         v13 측정 figure (F7/F8)
│   ├── 보고서_6_11/             ★ 6/11 최종보고서 figure (fig1~6)
│   └── archive/                 구 figure (paper_exact_v7·v8 · W1~W4 초기)
└── results/                     측정 데이터 — 상세는 results/README.md
    ├── 01_baseline_paper재현/   B1 baseline
    ├── 02_single_vector_본실험/ ★ CaseB 16-method single 벡터
    ├── 03_selectivity_sweep/    sel 민감도
    ├── 04_multi_vector_concat/  다중 벡터 concat
    ├── 05_K_granularity/        K 민감도
    ├── 06_부가측정/             α sweep 등
    ├── _summary/ · analysis/    집계·분석 산출물
    ├── raw/                     원본 측정 (절대 미변경 — 본 트랙의 원천)
    └── archive/                 구버전·범위 외·초기 sprint 측정
```

## 측정 정본

- **수치 정본**: `_internal/cache/rq3/v13_summary.md`
- **종합 REPORT**: `experiments/results/raw/REPORT_분석/REPORT_paper_exact_v13.md`
- **측정 데이터 사전**: `experiments/results/README.md` (변인·cell·파일명 규칙 — 외부 공개용)
- **figure**: `figures/보고서_6_11/` (6/11 보고서) · `figures/paper_exact_v13/`

## 핵심 결과 (v13)

- 3-way matched **1508 측정** (B1 대조군 · CaseA 완전 대체 · CaseB 결합).
- **결합(CaseB) vs B1**: better **89.1%** (1344/1508) · 중앙값 Δ% **−4.38%** · 평균 −3.06%.
- **완전 대체(CaseA) vs B1**: better 35.2% (negative control — 대체는 불안정).
- 측정 method 16종 중 강한 **13** / 클러스터링 계열 3(gmm·minibatch_partial·faiss_ivf) 제외.

## 코드

활성 측정·분석·문서 빌드 script 는 `_internal/scripts/` 에 있다(조현빈 측정 운영 — `_internal/` 은 팀원 무시 OK). 초기 W1~W4 sprint script 는 `code/archive/2026_04_W1_W4_초기실험_scripts/` 에 보존. 상세는 `code/README.md`.

---

작성: 2026-05-19 · 디렉토리 총 정리(figure v7/v8 archive 격리 · results archive 일원화 · v13 기준 갱신). 이전 README(5/14 시점)는 git history 보존.
