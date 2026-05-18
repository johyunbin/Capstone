# CLAUDE.md — Capstone Project Guide

## 프로젝트 개요

**팀명**: 속도는벡터 (연세대학교)
**주제**: Exqutor 논문 기반 벡터 증강 분석 쿼리(VAQ) 최적화 연구
**본 논문**: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2)
**학기**: 2026-1학기 캡스톤 디자인
**목표**: 비교 분석 및 실험 — 새 알고리즘 개발이 아닌 벤치마크/검증 중심

## 동적 state + 인계 (5/18 13:30 update — handoff_v37, task I·deck v13·3차 자문요청 완료)

> CLAUDE.md = 라우팅 + 안정 룰. 새 세션은 **handoff_v37 read 로 0% loss 인계** (self-contained).

- **★ 새 세션 진입 anchor (0% loss)**: `@_internal/handoff/active/handoff_v37_5_18_taskI_deckv13_3차자문_20260518_1330.md` (5/18 13:30 — task I(REPORT v13·narrative v8)·5/27 발표 deck v13(키노트 prompt 3-part + 보조자료)·3차 자문요청 완료 + figure 세션 통합 · 다음 세션 = 업데이트된 deck(PDF) 검토 + 3차 자문요청 점검)
- **★ 본 연구 narrative (5/27 발표 + 6/11 보고서 공통 base)**: `@submission/_drafts/속도는벡터_본연구_narrative_v8_20260518.md` (논문 재현 아님 — sample selection 단계 개입의 전 변인 검증; 측정 3-way B1/CaseA/CaseB. v7은 이력)
- **핵심 일정** (학기 전체): `@_internal/state/_schedule.md`
- **측정 portfolio + 분석** (3-way matched 1508 측정 = B1·CaseA·CaseB 각 1508): `@_internal/cache/rq3/aggregated_v13_full.parquet` · `v13_summary.md` · 종합 보고서 `@experiments/results/raw/REPORT_분석/REPORT_paper_exact_v13.md` (v12는 이력)
- **handoff 통합** (v0~v34 archive): `@_internal/handoff/archive/`
- **57 method × 9 paradigm**: `@_internal/METHOD_REGISTRY.md`
- **9 cells × 56 method × 3 modes matrix**: `@_internal/EXPERIMENT_REGISTRY.md`
- **server 자원 + tmux**: `@_internal/SERVER_REGISTRY.md`
- **★ 5/27 발표 키노트 prompt v13 (3 part) + 발표 보조자료**: `@submission/_drafts/속도는벡터_5_27_키노트_prompt_v13_part{1,2,3}_20260518.md` · `@submission/_drafts/속도는벡터_5_27_발표보조자료_v13_20260518.md` (v12는 이력)
- **5/27 발표 storyline v2**: `@plans/5_27_storyline_draft_20260511_1410.md`
- **6/11 보고서 outline v2** (5/8 base) + **v3 update plan**: `@plans/최종보고서_outline_v2_20260508.md`, `@plans/6_11_보고서_outline_v3_update_plan_20260511.md`
- **5/22 박광현 미팅 자료**: `@submission/_drafts/박광현_5월22일_미팅/`
- **팀원 카톡 v2 (발송용)**: `@submission/_drafts/팀원_카톡_5_27_finalize_20260511.md`

## 새 RQ 구조 (5/5 확정 + 5/12 02:50 paper exact 실측 REPORT v11 반영)

| RQ | 질문 | 메인 실험 | 핵심 결과 (5/12 02:50 실측) |
|---|---|---|---|
| **RQ1** | random sampling 이 skew 데이터셋에서 얼마나 부정확한가? | DEEP/SIFT/SSN sf=100 × Bernoulli vs KM20 stratified × sel{0.01, 0.10} | mean gap **+3.74%** (5 cell × 5 trial) |
| **RQ2** | 분포 아는 상황에서 어떤 방식이 최적? | KM20 5-way: Bernoulli / Equal / Proportional / Neyman / Anti-Neyman | Bern→Prop **−9.53%** ✓. Anti 1.540 < Prop 1.580 < **Neyman 1.595 paradox** (σ_j range 1.3-1.6× narrow + N_i CV=0) → "분포 알면 prop allocation 답" + RQ3 자연 전환 |
| **RQ3** | 분포 모르는 상황에서 어떤 방식이 최적? | 8 paradigm × 56 method × 9 cells × 2 modes (**1001 file**: B1 9 + CaseA 495 + CaseB 496, REPORT v11) | **paired CaseB < CaseA 92.5%** (455/492, p<1e-45) + **Cliff's δ large better 63.0%** (311/494) + Hedges' g large 55.7% (275/494) + one-sided p<0.05 outperform 45.3% (224/494). negative control: CaseA 단독 대체 **0/493 = 0%** (large worsening 37.1%). Fig.12 mean qe_trim 1.618 vs paper 1.69 = -4.3% 재현 ✓ |

- **연구 방향**: Exqutor §V-B Adaptive Sampling 영역 paper exact 재현 + 분포 인지 stratification ensemble augment 의 정량적 가치 검증. ECQO §V-A 영역은 paper main result 그대로 인정.
- **CaseB ensemble 정의** (사용자 5/9 23:18): `est_final = (est_b1 + est_method) / 2.0` simple average. paper §V-B Bernoulli (est_b1) + 우리 method KM20 stratified (est_method) 산술 평균. AdaptiveState (Eq 1-6) 그대로 paper exact 유지. sample budget 두 estimator 공유 (paper Eq 1 N=385).
- **paradigm rollup 8 (CaseB mean Δ%, 실측 REPORT v11)**: P10 Density **−11.93** (n=1, 약함) / P9 InfoTheoretic **−7.60** (n=9) / P3 Streaming **−6.63** (n=44) / P4 DimReduction **−6.03** (n=104) / P2 Spatial **−5.57** (n=107) / P5 QMC +1.47 (n=62, paradigm-level 만 보고, method 4건 폐기) / P1 Cluster +2.04 (n=87) / P6 Quantization +8.44 (n=53)
- **사용자 정책 폐기 method** (발표 자료 X, future work X): **정합성 위반 10** (halton/sobol/lhs/hammersley/dense_rp/random_projection/dbscan/ccsketch/lsh/ams_count_sketch — paper N=385 budget 위반, 5/14 환각 검증 H1 정정: 9→10) + **측정 미커버 7** (Tier 2 6: dirichlet/kernelpca/neurocard_lite/birch/hdbscan/agglomerative + KDE 1: kde_parzen, 5/14 07:39 kde_chain 폐기 결정) + **algorithm audit drop 23 method**
- **Honest limitation**: 측정 portfolio 1001 file 외 미커버 cells 9 카테고리 정직 분류 (REPORT §10) + byte-identical duplicates 7쌍 (REPORT §11) + ★3 hilbert PCA 2D lex sort alias (Faloutsos 1989 ❌, hilbert_real 별도 측정 9 cells × 2 modes) + ★4 sparse_rp Li-Hastie-Church 2006 reference 정정
- **설계 history**: `plans/archive/RQ_재정립_과거_버전/` (5/5 + 5/9 evidence)
- **서버**: `165.132.140.240` (capstone2026), 작업 디렉토리 `/mnt/hdd0/home/capstone2026`, 상세는 `_internal/SERVER_REGISTRY.md`

## 세션 시작 체크리스트

1. `git fetch origin && git status` → 뒤처져 있으면 `git pull --no-rebase origin main`
2. SessionStart hook이 자동으로 상태 출력 (브랜치, 미커밋, 문서 수)
3. 캡스톤 홈페이지 공지 확인 → 새 일정 있으면 3곳 동시 업데이트

### 3곳 동시 업데이트 규칙

일정/상태 변경 시: **CLAUDE.md** + **메모리** (`project_schedule.md`) + **노션** `캡스톤 일정` DB

### 동기화

> "동기화" = git + rsync + Claude 세팅 전부 실행. 상세는 글로벌 CLAUDE.md 참조.

- **팀 공유 파일** (research, records, plans, experiments, submission, templates, scripts): git
- **개인 파일** (.claude, guideline): rsync
- .gitignore에 개인 파일 제외 완료 — git에는 팀 공유분만 올라감

## 디렉토리 구조 (2026-05-11 정리 후)

루트는 **팀원 핵심 5개 + 도구·양식 2개 + 내부용 1개** 로 정리됨. 팀원 진입 가이드는 루트 `README.md` 참조.

```
Capstone/
├── README.md              팀원 진입점 (5/11 update — paper exact 결과 + 5/15 박광현 미팅)
├── CLAUDE.md              이 파일 (Claude Code 컨텍스트, 라우팅 + 안정 룰)
│
├── submission/            ⭐ 우리 팀의 모든 공식 문서
│   ├── _drafts/           팀 공유 최신본 (발표 v3 + 자문메일 v5 + 연구지도확인서 v3 + 팀원 자료 3건)
│   │   └── archive/       이전 버전 한글 폴더 12종 (5/11 정리: 발표자료_v3_source / 자문메일_v1_v2_초안 / 중간보고서_4월28일_source 등)
│   └── 제출완료/          외부에 보낸 자료 (학교 공식 + 멘토 자문)
│
├── experiments/           ⭐ 실험
│   ├── code/              실험 스크립트 (rq1/rq2/rq3/local_analysis)
│   ├── results/           RQ1·RQ2·RQ3 measurement
│   ├── figures/paper_exact_v7/  ⭐ 6 figure (5/11 신규)
│   ├── figures/archive/W1_W4_초기실험_figure/  이전 figure 8 dir (5/11 정리)
│   └── config/            파라미터
│
├── plans/
│   ├── 5_27_storyline_draft_20260511_1410.md  ⭐ 5/27 발표 storyline v2 (5/11 정정)
│   ├── 최종보고서_outline_v2_20260508.md       ⭐ 6/11 보고서 outline base
│   └── archive/RQ_재정립_과거_버전/ + 회의_outline_과거/
├── reference/             참고 자료 (papers 69편 + summaries 82편 + exqutor_query_plans/)
├── templates/             캡스톤 학교 양식 샘플
│
└── _internal/             ⛔ 조현빈 개인 작업 (팀원 무시 OK)
    ├── handoff/active/handoff_v8_*.md  ⭐ 새 세션 인계 anchor (1 file 0% loss)
    ├── handoff/archive/   v0~v6 + validation_statistics
    ├── MASTER_README.md / MASTER_HANDOFF.md / METHOD_REGISTRY.md / EXPERIMENT_REGISTRY.md / SERVER_REGISTRY.md / CHANGELOG.md / naming_convention.md
    ├── state/_schedule.md + _next.md + archive/
    ├── records/           회의록 (kakaotalk + weekly)
    ├── scripts/           문서 빌드 도구 + 측정 script (active 32 + archive 43)
    ├── guideline/         Claude Code 자동화 지침 (활성 5 + archive 6)
    ├── method_audit/      method 검증 (5/10 P1-P6 audit + 5/11 Phase 4)
    ├── validation/        4-layer audit + data/319
    ├── learning/, cache/  학습 자료 + 분석 cache
    └── 문서_archive/       5/11 정리 (이전_handoff/ + 5_8_시점_outdated_docs/ + state_과거_시점/ + 정리작업_log/)
```

## 지침 시스템

`_internal/guideline/` 폴더에 활성 지침 5개, 각 3파일 세트 (auto.md + manual.md + .sh).

| 키워드 | 지침 | 용도 |
|--------|------|------|
| "실험" | 01_실험지침 | 벤치마크/EXPLAIN ANALYZE |
| "제출" | 02_제출물지침 | 마감별 제출물 생성 |
| "PDF" | 03_문서생성지침 | md → HTML → Chrome CDP → PDF |
| "미팅" | 04_미팅지침 | 카톡 회의록 + 노션 업데이트 |
| "발표" | 05_발표지침 | PPT/포스터/슬라이드 |

보관 (`_internal/guideline/archive/`): 00점검→skill, 01논문분석(완료), 05주간보고→skill, 08설계(완료), 09학습(완료), 10CC활용(완료)

**실행**: `{키워드}` (자동) / `{키워드} 수동` (Phase별 정지) / `./_internal/guideline/NN_*_실행.sh`
**수동 모드**: Phase 완료 → 정지 → `/clear` → "다음 phase 이어가자"로 재개. 절대 자동 진행 금지.

## 카카오톡 회의록

카톡 대화 → `records/kakaotalk/YYYYMMDD_제목.md`

## Exqutor 핵심

- **문제**: pgvector(33.3%), VBASE(50%), DuckDB(100%) — 고정 비율 카디널리티 추정 → 잘못된 실행 계획
- **ECQO**: 인덱스 있을 때 HNSW range query → 정확한 카디널리티 (1~2ms)
- **Adaptive Sampling**: 인덱스 없을 때 모멘텀 기반 동적 샘플링 (Section V-B 식 1~6, hyperparam m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N=385)
- **우리의 공략점**: Adaptive Sampling 의 *unstratified Bernoulli* vs 본 연구 4강의 *분포 인지 stratification* paired Δ% 비교 → ★1~★3 = Outcome A 우위 / ★4 = Outcome B 동등 (paradigm anchor)

## 문서 규칙

- **한국어** 기본, 학술 용어 영어 병기
- 서사적 학술 산문 (bullet 나열 지양)
- PDF: Chrome CDP만 사용 (**fpdf2 금지** — 한글 깨짐)
- 변환: `python3 scripts/md2pdf.py <file.md>` → 같은 위치에 .pdf 생성
- 폰트: Apple SD Gothic Neo (Chrome 렌더링)

### 파일명 규칙

**핵심 원칙**: 구조적 경계는 `_`, 제목 내부는 공백

| 디렉토리 | 패턴 | 예시 |
|----------|------|------|
| `plans/` | `문서명_YYYYMMDD_HHMMSS.ext` | `연구설계안_20260403_162818.md` |
| `records/kakaotalk/` | `YYYYMMDD_제목.md` | `20260403_교수님미팅 샘플링방향전환.md` |
| `records/weekly/` | `주간보고_YYYY-MM-DD.md` | `주간보고_2026-03-28.md` |
| `reference/analysis/` | `(NN) 제목.ext` | `(01) Exqutor 상세분석.md` |
| `reference/summaries/` | `[N] Title Case 논문제목 총정리.ext` | `[13] pgvector Open-Source ... 총정리.md` |
| `submission/` | `팀명_문서명.ext` | `속도는벡터_연구제안서.docx` |

- `_` 용도: 이름↔날짜, 날짜↔시간, 팀명↔문서명 등 **논리적 경계**
- 공백 용도: 제목·문서명 내 자연어 띄어쓰기
- 영문 논문 제목: **Title Case** (관사·전치사·접속사 소문자, 약어 대문자)
- 시스템/약어: 원표기 유지 (`pgvector`, `DuckDB`, `HNSW`, `GPU`, `LSH`)

## 도구

- **DB**: pgvector (PostgreSQL), DuckDB
- **라이브러리**: Python, NumPy, FAISS
- **분석**: EXPLAIN ANALYZE, pg_hint_plan

## 팀

| 이름 | 역할 | GitHub |
|------|------|--------|
| 박세은 | 팀장 | triangle-park |
| 강재현 | 팀원 | newagency |
| 조현빈 | 팀원 | johyunbin |
| 이동욱 | 팀원 | dlee004 |

지도교수: **박광현 교수님** (BDAI 연구실) / 지도연구원: **임채림 석사** / 멘토: **박성원** (삼성전자 AI센터)

## 참고 링크

- 캡스톤: https://capstone.cs.yonsei.ac.kr/capstone/
- 양식: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=27
- 일정표: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=370
- Exqutor: https://github.com/BDAI-Research/Exqutor
- 팀 GitHub: https://github.com/johyunbin/Capstone
- 팀 Notion: https://www.notion.so/8110e4b8d680833a90bf01032872b1eb
