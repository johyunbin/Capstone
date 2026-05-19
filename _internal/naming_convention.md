# naming_convention.md — File Naming 규칙

> 작성: 2026-05-11 01:55 KST · 갱신: 2026-05-19 (타임코드 우선 원칙 명문화 · handoff/submission 패턴 현행화 · 디렉토리 총 정리 반영)  
> 출처: CLAUDE.md (project) + 사용자 명시 + 5/11·5/19 정리 작업 통합

---

## 0. 핵심 원칙

**구조적 경계는 `_`, 제목 내부는 공백**.

| 디렉토리 | 패턴 | 예시 |
|---|---|---|
| `plans/` | `문서명_YYYYMMDD_HHMMSS.ext` | `연구설계안_20260403_162818.md` |
| `records/kakaotalk/` | `YYYYMMDD_제목.md` | `20260403_교수님미팅 샘플링방향전환.md` |
| `records/weekly/` | `주간보고_YYYY-MM-DD.md` | `주간보고_2026-03-28.md` |
| `reference/analysis/` | `(NN) 제목.ext` | `(01) Exqutor 상세분석.md` |
| `reference/summaries/` | `[N] Title Case 논문제목 총정리.ext` | `[13] pgvector Open-Source ... 총정리.md` |
| `submission/` | `팀명_문서명_YYYYMMDD_HHMMSS.ext` | `속도는벡터_6_11_최종보고서_20260519_135021.md` |

- `_` 용도: 이름↔날짜, 날짜↔시간, 팀명↔문서명 등 **논리적 경계**
- 공백 용도: 제목·문서명 내 자연어 띄어쓰기
- 영문 논문 제목: **Title Case** (관사·전치사·접속사 소문자, 약어 대문자)
- 시스템/약어: 원표기 유지 (`pgvector`, `DuckDB`, `HNSW`, `GPU`, `LSH`)

### 타임코드 우선 (★ 버전 분기 규칙)

작업 산출물의 버전 분기는 **타임코드 `_YYYYMMDD_HHMMSS`** 로만 한다.

- ❌ `v{N}`·`ver`·`wave`·`phase` 를 파일명 분기자로 쓰지 않는다 — 혼용 시 선후 관계 파악·장기 재활용 불가.
- 수정 시 덮어쓰기보다 새 타임코드 파일 생성 — 이력 보존.
- 최종 제출 확정본만 타임코드를 수동 제거 (예: `속도는벡터_최종발표_슬라이드.pptx`).
- handoff·plan·submission 등 모든 작업 산출물에 적용.

---

## 1. _internal/ naming (5/11 정리 작업 신규)

### 1.1 단일 진입점 (대문자 prefix)

핵심 산출물 = 모두 **대문자 + underscore**:

- `METHOD_REGISTRY.md` — method paradigm 분류
- `SERVER_REGISTRY.md` — server 자원 inventory
- `CHANGELOG.md` — timeline
- `README.md` — `_internal/` 안내

> 2026-05-19 archive: `MASTER_README.md`·`MASTER_HANDOFF.md`·`EXPERIMENT_REGISTRY.md` 는 5/11 시점 문서로 측정 완료(v13) 후 `archive/2026_05_11_옛_정본문서/` 로 이동. 현 진입점은 루트 `CLAUDE.md` + `handoff/active/` 최신 handoff.

### 1.2 handoff/

```
handoff/
├── active/    (현재 세션 즉시 read 권고)
│   ├── handoff_v2_paper_verbatim_decisions_20260510_1418.md
│   ├── handoff_v4_session_20260510_2144.md
│   ├── handoff_v5_phase4_brainstorm_20260511_0110.md
│   ├── handoff_main_session_FULL_STATE_20260510_2045.md
│   └── handoff_back_validation_20260510_2046.md
└── archive/   (이전 단계, 보존)
    ├── handoff_v0_FINAL_SCOPE_20260510_0125.md
    ├── handoff_v0_FINAL_SCOPE_20260510_0125.bak.md
    ├── handoff_v1_NEW_SESSION_20260510_1336.md
    ├── handoff_v3_method_verification_20260510_2030.md
    └── handoff_validation_statistics_20260510_2030.md
```

**패턴 (현행)**: `handoff_YYYYMMDD_HHMMSS_키워드.md` + 동반 `새세션_복붙_프롬프트_YYYYMMDD_HHMMSS.md`

- `active/` 에는 **현행 1세트만** 둔다 — 새 세션 종료 시 이전 세트는 `archive/` 로 이동.
- 타임코드 `YYYYMMDD_HHMMSS` 로 선후 구분 (`v{N}` 식별자 금지).
- 위 트리는 5/10 시점 예시 — 현재 `active/` 는 `handoff_20260519_154301_*` 형식 1세트.
- 상세 인계 규칙: `~/.claude/rules/handoff.md`.

### 1.3 method_audit/

```
method_audit/
├── 20260510_initial/   (5/10 8 agent 1차 audit, 11 file)
│   ├── _SUMMARY.md
│   ├── _HANDOFF_PROMPT_for_main_session.md
│   ├── additional_methods_brainstorm.md
│   ├── paradigm_P1_cluster.md ~ P6_quantization_other.md (6 file)
│   └── sf_feasibility_matrix.md
└── 20260511_phase4/    (5/11 phase 4 brainstorm, 5 file)
    ├── _BRAINSTORM_FULL.md
    ├── _BRAINSTORM_REPORT.md
    ├── _FILTER_BRAINSTORM.md
    ├── _FILTER_ANALYSIS.md
    └── _FINAL_LIST.md
```

**패턴**: `YYYYMMDD_{단계식별자}/`

- `_` prefix file = meta / report / summary
- paradigm file = `paradigm_P{n}_{이름}.md`

### 1.4 scripts/

```
scripts/
├── (active 32건)
│   ├── measure_paper_exact.py
│   ├── _measure_common.py
│   ├── analyze_paper_exact.py
│   ├── compute_stratum_sigma_paper_exact.py
│   ├── method_phase4_extra.py
│   ├── method_tier1_p9_p10.py
│   ├── method_hilbert_real.py
│   ├── PATCH_phase4_registry.md
│   ├── PATCH_hilbert_real_registry.md
│   ├── measure_multi_vec_patch.md
│   ├── run_phase_a2fig8_tier1.sh
│   ├── run_phase_b_phase4.sh
│   ├── run_phase_b_q1q4.sh
│   ├── md2pdf.py
│   ├── md2pdf_academic.py
│   ├── md2docx.py
│   ├── _build_docx_v1.py
│   ├── methods/  (extra2 20 method 별 module)
│   └── midterm_pptx/  (4/28 발표 산출)
└── archive/   (43건 이전 측정 끝난 script)
    ├── analyze_*.py (5건)
    ├── build_*.py (8건)
    ├── chain_unified.py
    ├── finalize_5_9_morning.sh
    ├── launch_sf100_safe.sh
    ├── master_v6_fill_partial.py
    ├── measure_*.py (8건 — 이전 multi 측정)
    ├── measure_exqutor_replication_DRAFT.py
    ├── prepare_cell.py
    ├── parallel_download.sh
    ├── plot_w4_partial.py
    ├── run_*.py / .sh (10건 — 단일 method launch)
    ├── setup_multi_sf1.py
    ├── watch_*.sh (3건)
    └── analyze_phase_g.py.bak_v8_20260509_2341
```

**패턴**:
- 측정: `measure_{대상}_{방식}.py` (`measure_paper_exact`, `measure_multi_paradigm`, `measure_phase_f_baselines`)
- 분석: `analyze_{대상}.py` (`analyze_paper_exact`, `analyze_ensemble`, `analyze_failure_modes`)
- 빌더: `build_{대상}.py` (`build_FB_single_ensemble`, `build_charts_5_8`)
- launcher: `run_{단계}_{식별자}.sh` (`run_phase_b_q1q4`, `run_phase_a2fig8_tier1`)
- method module: `method_{식별자}.py` 또는 `methods/{이름}_strat.py`
- patch instruction: `PATCH_{대상}_{영역}.md` (`PATCH_phase4_registry`)
- watch / monitor: `watch_{대상}.sh`
- backup: `{원본}.bak_v{버전}_{YYYYMMDD_HHMM}` (`analyze_phase_g.py.bak_v8_20260509_2341`)

### 1.5 state/

```
state/
├── _current.md         (활성 상태)
├── _next.md            (다음 단계 trigger)
├── _roadmap.md         (전체 로드맵)
├── _schedule.md        (학기 일정)
├── _artifacts.md       (산출물 위치)
├── _consolidation_YYYYMMDD_HHMM.md  (특정 시점 통합)
├── _data_scope_decision_YYYYMMDD_HHMM.md  (특정 결정)
├── _kakaotalk_narrative_method_table_YYYYMMDD_HHMM.md  (특정 시점 narrative)
├── _method_portfolio_v{N}_{식별자}_YYYYMMDD_HHMM.md  (versioned portfolio)
└── archive/   (이전 portfolio v8 등)
```

**패턴**: `_{영역}_{선택 시간}.md` (`_` prefix = state 식별자)

### 1.6 validation/

```
validation/
├── audit_{layer}.py    (audit script — paired_delta, wilcoxon_bh_fdr, narrative_consistency, cherrypicking)
├── {layer}_audit.md    (audit 결과 — paired_delta_audit, wilcoxon_bh_fdr_audit, ...)
├── audit_data_{식별자}.csv  (audit data)
├── SUMMARY_validation.md (종합)
└── data/   (server read-only rsync, 319 항목)
```

---

## 2. plans/ naming

```
plans/
├── 연구설계안_YYYYMMDD_HHMMSS.md
├── RQ재정립_YYYYMMDD_HHMM.md
├── 최종보고서_outline_v{N}_YYYYMMDD.md
├── {회의명}_outline.md
└── archive/
    └── {원본}.md.bak_{식별자}_YYYYMMDD_HHMMSS
```

**패턴**: 한국어 문서명 + `_YYYYMMDD_HHMMSS` 또는 `_YYYYMMDD_HHMM`

---

## 3. records/ naming

### 3.1 records/kakaotalk/

**패턴**: `YYYYMMDD_제목.md`
- 제목 내 공백 OK (`20260403_교수님미팅 샘플링방향전환.md`)
- 같은 날 여러 회의: 시간 추가 가능 (`20260427_2125_보고서표2 CI 정정 지시.md`)

### 3.2 records/weekly/

**패턴**: `주간보고_YYYY-MM-DD.md` (대시 사용 — 다른 patterns 와 차별)

### 3.3 records/kakaotalk/raw_export/

원본 카톡 export 그대로 보존 (구조 변경 X).

---

## 4. submission/ naming

```
submission/
├── _drafts/   (팀 공유 최신본 + archive)
└── 제출완료/   (외부 발송 자료)
    └── 속도는벡터_{문서명}.{md,pdf,docx}
```

**패턴**: `속도는벡터_{문서명}_{YYYYMMDD_HHMMSS}.{ext}` (팀명 prefix + 타임코드)

- 작업본은 타임코드로 버전 분기. 최종 제출 확정본만 타임코드 수동 제거.
- ext 우선순위: `.md` (편집) → `.docx`·`.pdf`·`.hwpx` (제출·배포)
- `제출완료/` 는 외부 발송 완료 기록 — 리네임·이동 금지(동결).

---

## 5. reference/ naming

### 5.1 reference/papers/

**패턴**: 원본 PDF 파일명 그대로 (인용 보존)
- 정렬: `[N] {Title Case 논문제목}.pdf`
- arXiv: `{arxiv_id}_v{버전}.pdf` 가능

### 5.2 reference/summaries/

**패턴**: `[N] {Title Case 논문제목} 총정리.{md,pdf}`
- N = 인용 번호
- "총정리" suffix 통일

### 5.3 reference/analysis/

**패턴**: `(NN) 제목.{md,pdf}`
- NN = 2자리 번호 zero-padding
- 제목 = 한국어 OK

### 5.4 reference/exqutor_query_plans/

원본 Exqutor github 구조 그대로 (`tpc_h/q*.sql`, `tpc_ds/q*.sql`).

---

## 6. memory/ naming (~/.claude/projects/-Users-hyunbin-Capstone/memory/)

```
memory/
├── MEMORY.md   (index, 50 line 이내)
├── user_{영역}.md
├── project_{영역}.md
├── feedback_{영역}.md
├── reference_{영역}.md
└── archive/
    └── {원본}_{식별자}_YYYYMMDD_HHMM.md
```

**패턴**: `{type}_{영역}.md` (type = user/project/feedback/reference)

---

## 7. 측정 결과 naming (server `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/`)

### 7.1 B1/CaseA/CaseB

**패턴**: `{Cell}_{Mode}_{method}_{ensemble?}.json`

- Cell: `A1-DEEP`, `A1-SIFT`, `A1-SSN`, `A2-Fig7`, `A2-Fig9`, `A4-sel`, `A5-scale-sf{1,10,100}`
- Mode: `B1` / `CaseA_{method}` / `CaseB_{method}_{ensemble}`
- 예: `A1-DEEP_B1.json`, `A1-DEEP_CaseA_minibatch_partial.json`, `A1-DEEP_CaseB_sparse_rp_simple_average.json`

### 7.2 RQ1/RQ2 csv

**패턴**: `rq{1,2}_paper_exact_{Dataset}_sf{N}.csv`
- 예: `rq1_paper_exact_DEEP_sf100.csv`, `rq2_paper_exact_SIFT_sf100.csv` (5-way after chain)

### 7.3 REPORT

**패턴**: `REPORT_paper_exact.md` (자동 생성, analyze_paper_exact.py 갱신)

### 7.4 NPY cache (`cache/rq1/`)

**패턴**: `{table}_{vectors,strata,pks}.npy`
- 예: `partsupp_deep_100_vectors.npy`, `partsupp_fb_10_strata.npy`

### 7.5 query_pool / query_selectivity parquet

**패턴**: `query_{pool,selectivity}_{Dataset}_sf{N}.parquet`
- 예: `query_pool_DEEP_sf100.parquet`, `query_selectivity_SSN_sf10.parquet`

### 7.6 log

**패턴**: `{단계}_{식별자}_{YYYYMMDD_HHMM}.log`
- 예: `paper_exact_phase_b_extra_20260510_1450.log`, `sigma_build_paper_exact_20260510_1240.log`, `rq2_paper_exact_5way_20260510_2330.log`

---

## 8. method 명명 (paradigm 분류 적용)

### 8.1 활성 method (paradigm primary)

| Paradigm | method | 명명 규칙 |
|---|---|---|
| P1 Cluster | minibatch / gmm / mb_partial / birch / agglomerative / coreset / dbscan / kmeans_neyman | `{알고리즘}_{변형}` |
| P2 Spatial | hilbert_real / skilling_hilbert / zorder_morton / idistance / idistance_neyman / faiss_ivf / lpm1_proper / epsilon_net | `{공간기법}_{변형}` |
| P3 Streaming | chao_weighted | `{알고리즘}_{변형}` |
| P4 DimReduction | sparse_rp / random_projection / pca1d / rsvd / ica_fastica | `{알고리즘}_{차원}` 또는 `{축약}` |
| P5 QMC/Hashing | lsh / sobol / halton / hammersley / lhs / cum_sqrtf / lavallee_hidiroglou | `{알고리즘}` |
| P6 Quantization | rabitq_strat / mhist2 / wavelet_hist | `{알고리즘}_{변형}` |
| P9 InfoTheoretic | hyperloglog | (sketch lib 이름) |
| P10 Density | kde_parzen | `{기법}_{창안자}` |

### 8.2 폐기 method (handoff_v3 권고 적용)

**rename only** (코드 변경 X, 결과 보존):

| 기존 | 신 명칭 | 이유 |
|---|---|---|
| hilbert | `pca2d_lex` | PCA 2D lex sort, 진짜 Hilbert curve 아님 |
| reservoir | `random20` | RANDOM20 random partition, Vitter 1985 아님 |
| lpm2 | `radial_quantile` | Weiszfeld median + radial bin, Grafström LPM 아님 |
| tucker | `pca3d_grid` | PCA(3) + 3D grid + modulo, Tucker 1966 아님 |
| vinecopula | `spearman_pca1d` | rank+PCA1D, Bedford-Cooke 2002 아님 |
| factor_join | `pca2d_grid` | PCA(2)+5×5 grid, Zhao 2023 FactorJoin 아님 |
| neurocard_lite | `pca8_kmeans` | PCA(8)+KMeans, Yang 2020 NeuroCard 아님 |
| lp_bound | `l2_quantile` | SIGMOD 2025 LpBound 명칭 충돌 회피 |
| cocluster_nystrom | `biclustering_5k_centroid` | Nyström 미구현 |

**폐기** (결과 보존, 보고서 limitation 명시):

thompson_sampling / mfmc / neuram / cca1d / ams_count_sketch / ccsketch / kdpp / banditucb1 / hkbu_repsample (or coreset)

### 8.3 reference 정정만 (명칭 그대로)

- sparse_rp: Achlioptas 2003 ❌ → **Li-Hastie-Church 2006** ⭕

---

## 9. version + backup naming

### 9.1 versioning

**원칙**: 같은 의미 file 의 새 버전 = 새 file 생성 (덮어쓰기 X)

- **타임코드 단일 규칙**: `{원본}_{YYYYMMDD_HHMMSS}.{ext}`
- ❌ `v{N}`·`ver`·`wave`·`phase` 를 분기자로 쓰지 않는다 (§0 타임코드 우선 참조).

### 9.2 backup

**패턴**: `{원본}.bak_{식별자}_{YYYYMMDD_HHMM}`

- 예: `analyze_phase_g.py.bak_v8_20260509_2341`
- 예: `RQ재정립_v7_evidence_20260509_1820.md.bak_narrative_pre_correction_20260509_235722`

### 9.3 archive

archive 디렉토리 = 활성 영역에서 분리된 history 보존:

- `_internal/archive/{YYYYMMDD_식별자}/` (예: `2026_05_07_dawn_chain`, `2026_05_08_cleanup`, `2026_05_09_audit_archive`)
- `_internal/archive/handoff_v0_to_v18/` (legacy handoff)
- `plans/archive/`
- `submission/_drafts/archive/`

---

## 10. 한국어 vs 영어

### 10.1 한국어 우선
- 문서 본문 (학술 용어 영어 병기)
- 회의록 (records/kakaotalk/)
- 주간보고
- 자체 작성 plan / spec
- 발표 자료

### 10.2 영어 우선
- 코드 + 코드 주석 (Python/SQL)
- file 명 prefix (MASTER_, METHOD_, CHANGELOG)
- 측정 결과 schema (column 명)
- paper 관련 식별자 (Q3, Fig 5, A1-DEEP)

### 10.3 혼용 (한국어 + 영어)
- 한국어 핵심 + 영어 식별자: `중간보고서_v2_paper_exact.md` 가능
- file 명에 한국어 + 영어 OK: `RQ재정립_v7_evidence_20260509_1820.md`

---

## 11. 절대 금지

- ❌ 공백 + 특수문자 mix (예: `file (1).md`, `file_v1 final.md`)
- ❌ 시간 정보 없는 versioning (`file_v1.md` 가능 but `_YYYYMMDD` 권장)
- ❌ 폐기/archive 와 활성 file 같은 디렉토리 혼재
- ❌ 같은 file 다른 위치 중복 (active + archive 양쪽 X)
- ❌ Tier S/A/B/Q1/Q4 prefix (사용자 명시 5/11 01:15 폐기)
- ❌ session-id / random hash file 명 (사람이 못 찾음)

---

## 12. END

작성: 2026-05-11 01:55 KST  
다음 단계: MASTER_README.md 작성  

**핵심 검증**: 새 세션이 본 file 1건 read 만으로 모든 디렉토리·파일 명명 규칙 + paradigm method 명명 + versioning + backup 규칙 모두 파악 가능.
