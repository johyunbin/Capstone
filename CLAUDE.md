# CLAUDE.md — Capstone Project Guide

## 프로젝트 개요

**팀명**: 속도는벡터 (연세대학교)
**주제**: Exqutor 논문 기반 벡터 증강 분석 쿼리(VAQ) 최적화 연구
**본 논문**: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2)
**학기**: 2026-1학기 캡스톤 디자인
**목표**: 비교 분석 및 실험 — 새 알고리즘 개발이 아닌 벤치마크/검증 중심

## 동적 state + 인계 (6/10 17:55 갱신 — 최종보고서 초초안 채움 전달 · 프로젝트 총정리 · 카톡 트리거 대기)

> CLAUDE.md = 라우팅 + 안정 룰. 동적 state·진행 수치는 handoff 정본에 있다 — 새 세션은 아래 anchor 하나로 0% loss 인계.

- **★ 새 세션 진입 anchor (0% loss)**: `@_internal/handoff/active/handoff_20260610_175500_프로젝트총정리_트리거대기.md` — 산출 작업 사실상 종결. **남은 트리거 2**(카톡 요청 오면 착수, 그 외 작업 벌이지 않음): ① 최종보고서 수정 요청(박세은이 172500본 기반 수정→인간 검수 진행 중) ② 산학멘토링 결과보고서(hwp 2p 요약, **6/11 목 23:59**, 강재현 담당·클로드 지원 제안됨, 박세은 초안.hwp 카톡 6/9).
- **★ 최종보고서 현행 base**: `submission/_drafts/속도는벡터_최종보고서_초안_20260610_172500.{md,docx,pdf}` (12p — 박세은 초초안 흐름 채움본, Codex spark 적대검증 합격 + fresh 게이트 합격, 6/10 17:34 카톡 전달). 기술 정본(수치 풀버전) = `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md` — ⚠️ 인용 시 **오기 3건 정정 적용** (6/10 데이터 역산 확정): DEEP **96차원**(256 아님) · 엔진 partsupp sf10 = **800만 행**(8천만 아님) · 오프라인 sf1/10/100 = **80만/800만/8,000만 행**(Type표 0.1M/1M/10M은 8× 축소 오기).
- **★ 정직한 프레이밍 의무 (5/23 감사 평결)**: 결합 89.1%(중앙값 −4.38%) 우위 = 두 독립 추정량 평균(앙상블) 효과 — 분포 인지 고유 기여 없음(통제군 CaseC가 결합을 95/95 −5.98% 이김) · latency 는 주입 variant 간 무개선(주입 자체는 기본 엔진 대비 평균 5.67×·plan 회복 94.9% vs 58%). "분포 인지가 개선했다" 단독 서사 금지. method 명칭 = 5/24 audit 정정명칭(pca2d_hilbert_xy2d 등).
- **수치 정본**: v13 1,508건 `@_internal/cache/rq3/v13_summary.md` · 엔진 추정 `_internal/cache/rq3/latency/estimates_DEEP_sf10.parquet` · latency 12 cell `_internal/cache/rq3/latency/phase2/` · 통제(CaseC) v14/v16 = 5/23 보고서 §4.2.1·§4.2.3. 보고서 그림+베이스 CSV = `experiments/figures/보고서_6_11/team_20260610/` (생성 스크립트 `_internal/scripts/build_team_report_figs_20260610.py`).
- **제출 완료 (동결)**: `submission/제출완료/` — 포스터·1~4차 자문내역서·참여도조사 등. 산학 4차 자문내역서·컨택내역 = 6/9 LearnUs 제출 완료.
- **기록**: 카톡·산학멘토링 3·4차 메일 스레드 = `_internal/records/kakaotalk/20260610_*.md`. 6/10 이전 발표·소개영상·QnA 산출물 일괄 아카이브 = `submission/_drafts/archive/2026_06_10_cleanup/` (소개영상 mp4 = git 미추적 유지).
- **도구**: md→pdf = `python3 _internal/scripts/md2pdf.py <md>` (compact 제출용) · md→docx = `pandoc <md> --resource-path="submission/_drafts" -o <docx>` · hwp = hwpx/hwp MCP.
- **핵심 일정**: `@_internal/state/_schedule.md` — 남은 마감 = 6/11 최종보고서 + 산학멘토링 결과보고서 (이후 학기 종료).
- **registry**: METHOD `@_internal/METHOD_REGISTRY.md` (⚠️ 5/11본 — method 명칭은 5/24 audit 정정이 우선) · SERVER `@_internal/SERVER_REGISTRY.md`
- **handoff 이력**: `@_internal/handoff/archive/`

## 연구 구조 (RQ + 측정)

| RQ | 질문 | 메인 실험 | 핵심 결과 |
|---|---|---|---|
| **RQ1** | random sampling 이 skew 데이터셋에서 얼마나 부정확한가? | DEEP/SIFT/SSN sf=100 × Bernoulli vs KM20 stratified × sel{0.01, 0.10} | mean gap **+3.74%** (중간보고서) |
| **RQ2** | 분포 아는 상황에서 어떤 방식이 최적? | KM20 5-way: Bernoulli / Equal / Proportional / Neyman / Anti-Neyman | Bern→Prop **−9.53%** ✓ · Anti < Prop < **Neyman paradox** → "분포 알면 prop allocation 답" (중간보고서) |
| **RQ3** | 분포 모르는 상황에서 표본 선택 개입이 추정 오차에 미치는 효과 | 16 method × 5 데이터셋 × 5 조작변인 — **3-way matched 1508 측정** (B1·CaseA·CaseB 각 1508) | 결합 **CaseB vs B1 better 89.1%** (1344/1508) · 중앙값 Δ% **−4.38%** · 완전 대체 CaseA better 35.2% (negative control) |

- **연구 방향**: Exqutor §V-B Adaptive Sampling 의 표본 선택(sample selection) 단계 하나만 — 무작위 Bernoulli → 분포 인지 stratification — 으로 바꾸는 개입의 효과를 전 변인에 걸쳐 검증. §V-A ECQO·식 1-6·표본 예산 N=385 는 논문 그대로(minimal augmentation).
- **3-way 측정**: B1(대조군, 논문 그대로 Bernoulli) · CaseA(완전 대체 — Bernoulli 표본을 method 표본으로 통째 치환, 음성 대조군) · CaseB(결합 — `est_final = (est_b1 + est_method) / 2.0` 산술평균). 한 측정이 세 mode 를 동일 조건에서 동시 산출(matched).
- **method**: 측정 16 method 중 강한 **13** / 클러스터링 계열 3(gmm·minibatch_partial·faiss_ivf) 제외. paradigm 강→약(중앙값 Δ%) = P3 Streaming > P4 DimReduction > P2 Spatial > P9 InfoTheoretic > P5 QMC > P6 Quantization > P1 Cluster. method 선정·폐기(정합성·커버리지·audit) 상세는 `_internal/METHOD_REGISTRY.md`·`_internal/method_audit/`.
- **honest limitation**: 다중 벡터 측정 극단 이상치 2건 · P1 Cluster paradigm 비일관성 · concat sf=100 부분 미측정 · ★ hilbert_real = PCA 2D lex sort alias / sparse_rp = Li-Hastie-Church 2006 — 상세 REPORT v13 §4.7·§10.
- **수치 정본**: 진행·측정 수치는 모두 `_internal/cache/rq3/v13_summary.md`·보고서 정본 기준. 옛 handoff·문서의 v11/v12 수치(92.2%/−6.25%·1001 file 등)는 이력 — carry 금지.
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

## 디렉토리 구조 (2026-05-19 총 정리)

루트는 **팀원 핵심 4개 + 도구·양식 2개 + 내부용 1개**. 팀원 진입 가이드는 루트 `README.md`, 각 디렉토리 상세는 그 안의 `README.md` 참조.

```
Capstone/
├── README.md              팀원 진입점 (v13 결과 + 새 구조)
├── CLAUDE.md              이 파일 (Claude Code 컨텍스트, 라우팅 + 안정 룰)
│
├── submission/            ⭐ 공식 문서
│   ├── _drafts/           팀 공유 작업본 활성 16건 (보고서·발표 deck·포스터·소개영상·표지/요약본·3차 자문메일)
│   │   └── archive/       이전 버전 (키노트_prompt_history·narrative_history·주제별 폴더 + 2026_05_19_cleanup)
│   └── 제출완료/          외부 발송 완료 자료 — 동결(미변경)
│
├── experiments/           ⭐ 실험 (상세 experiments/README.md)
│   ├── results/           측정 데이터 — 01~06 트랙 + raw 원천 + 데이터 사전 README + archive
│   ├── figures/           보고서_6_11 + paper_exact_v13 + archive(v7·v8)
│   ├── code/              초기 sprint archive (활성 측정 도구는 _internal/scripts/)
│   └── config/            실험 파라미터
│
├── plans/                 5_27_storyline + 6_11_보고서_outline (정본) + archive/
├── reference/             원논문 69편 + 총정리 82편 + 심층분석 + exqutor_query_plans
├── templates/             캡스톤 학교 양식 (forms/ + samples/)
│
└── _internal/             ⛔ 조현빈 개인 작업 (팀원 무시 OK — 상세 _internal/README.md)
    ├── handoff/active/    ⭐ 새 세션 인계 anchor — 현행 1세트(handoff + 복붙 프롬프트)
    ├── handoff/archive/   이전 세션 handoff
    ├── METHOD_REGISTRY.md / SERVER_REGISTRY.md / naming_convention.md / CHANGELOG.md / README.md
    ├── cache/rq3/         v13 측정 집계·분석 (v13_summary.md 수치 정본)
    ├── scripts/           문서 빌드 도구 + 측정 script (완료 캠페인은 scripts/archive/)
    ├── state/ · records/ · method_audit/ · validation/ · guideline/ · learning/ · 포스터영상_build/
    └── archive/           이전 시점 history — 단일 archive (5/19 문서_archive 흡수, MASTER_*·EXPERIMENT_REGISTRY 격리)
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
- 변환: `python3 _internal/scripts/md2pdf.py <file.md>` → 같은 위치에 .pdf 생성
- 폰트: Apple SD Gothic Neo (Chrome 렌더링)

### 파일명 규칙

**핵심 원칙**: 구조적 경계는 `_`, 제목 내부는 공백

**버전 분기는 타임코드로** — `v13/v14` 식 버전 넘버나 `ver`/`wave`/`phase` 단어를 파일명 분기자로 쓰지 않는다 (혼용 시 선후 관계 파악·장기 재활용 불가). 모든 작업 산출물은 `<문서명>_YYYYMMDD_HHMMSS.ext` 타임코드로 분기한다. 수정 시 덮어쓰기보다 새 타임코드 파일을 생성해 이력을 보존하고, 최종 제출 확정본만 타임코드를 수동 제거한다.

| 디렉토리 | 패턴 | 예시 |
|----------|------|------|
| `plans/` | `문서명_YYYYMMDD_HHMMSS.ext` | `연구설계안_20260403_162818.md` |
| `submission/` | `팀명_문서명_YYYYMMDD_HHMMSS.ext` | `속도는벡터_3차자문요청_20260518_162300.md` |
| `_internal/handoff/` | `handoff_YYYYMMDD_HHMMSS_키워드.md` · `새세션_복붙_프롬프트_YYYYMMDD_HHMMSS.md` | `handoff_20260518_164701_deckv16검증.md` |
| `records/kakaotalk/` | `YYYYMMDD_제목.md` | `20260403_교수님미팅 샘플링방향전환.md` |
| `records/weekly/` | `주간보고_YYYY-MM-DD.md` | `주간보고_2026-03-28.md` |
| `reference/analysis/` | `(NN) 제목.ext` | `(01) Exqutor 상세분석.md` |
| `reference/summaries/` | `[N] Title Case 논문제목 총정리.ext` | `[13] pgvector Open-Source ... 총정리.md` |

- `_` 용도: 이름↔날짜, 날짜↔시간, 팀명↔문서명 등 **논리적 경계**
- 공백 용도: 제목·문서명 내 자연어 띄어쓰기
- 영문 논문 제목: **Title Case** (관사·전치사·접속사 소문자, 약어 대문자)
- 시스템/약어: 원표기 유지 (`pgvector`, `DuckDB`, `HNSW`, `GPU`, `LSH`)
- 상세 원본: `_internal/naming_convention.md`

## 도구

- **DB**: pgvector (PostgreSQL), DuckDB
- **라이브러리**: Python, NumPy, FAISS
- **분석**: EXPLAIN ANALYZE, pg_hint_plan

## Multi-Model Workflow (Gemini Ultra 적극 활용 · 2026-05-24 강화)

본 캡스톤은 **Claude + Codex + Gemini Ultra 3-way 협업**. 상세 룰 `@~/.claude/rules/multi-model.md` carry. 본 프로젝트 적용 핵심:

- **발표 deck** = Claude Design (layout · navy 앵커 · hero 그라데이션 · chapter badge · 5행 표) × Gemini **Nano Banana Pro** (illustration · 도식 — 이미지 내 한국어 텍스트 1위 강점) **둘 다 활용**. 사용자 5/24 명시 ("어느 하나만으로 한다기 보다는 둘 다 활용").
- **포스터 (900×1200 mm 세로 PDF)** = Claude Design 16 단 grid × Nano Banana Pro 5 자산 (VAQ 분석가 시나리오 · plan 트리 비교 · §V-B highlight · 4 갈래 도식 · 본 연구 기여 4 아이콘). brief 정본 `submission/_drafts/속도는벡터_포스터_시각자산_Nano_Banana_Pro_brief_20260524_010021.md`.
- **소개영상 (300 초)** = Claude Design 슬라이드 PNG × Gemini **Veo 3.1** (인트로 hero · 5행 표 reveal transition · 마무리 close clip 3 개, 총 15 초 cinematic · 네이티브 동기화 오디오) + ElevenLabs 한국어 TTS narration. brief 정본 `submission/_drafts/속도는벡터_소개영상_Veo_3_1_brief_20260524_010021.md`.
- **보고서 figure** = Claude 정합 표 × Nano Banana Pro figure 보강 (측정 환경 도식·통제 실험 설계).
- **문헌 교차검증** = Gemini **Deep Research** (Ultra 한도 사실상 자유) — 보고서 §2.2 Exqutor 식·§2.3 Cochran §5.5/§11.10 verbatim 대조.
- **Codex** = 통계 코드 검증 + 보고서 수치·로직 적대 재검증 (xhigh).
- **메모리**: 협업 패턴 상세 `@~/.claude/projects/-Users-hyunbin-Capstone/memory/feedback_design_x_gemini_collab.md`.

본 룰 = 매 응답마다 Gemini Ultra 강점 활용 가능성 검토. (사용자 영구 위임 2026-05-24)

## Chrome MCP — macmini 무조건 (영구 위임 2026-05-24)

`list_connected_browsers` 결과에 macmini + macbook 둘 다 있어도 **사용자 명시 선택 없이 macmini (deviceId `644dba75-3349-4c8d-ba29-1507743d45a5`) 자동 선택**. 사용자 영구 위임 (2026-05-24 "맥미니로 연결해 그냥 무조건 · 항상"). 메모리: `@~/.claude/projects/-Users-hyunbin-Claude/memory/feedback_chrome_browser_choice.md`.

claude.ai/design "최종발표" 대화창 = `/p/019e1a41-701c-7134-9ce1-1247262c1563` carry. design system 깨짐 방지를 위해 새 대화창 X · 동일 대화창에 복붙.

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
