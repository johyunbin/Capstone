# CLAUDE.md — Capstone Project Guide

## 프로젝트 개요

**팀명**: 속도는벡터 (연세대학교)
**주제**: Exqutor 논문 기반 벡터 증강 분석 쿼리(VAQ) 최적화 연구
**본 논문**: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2)
**학기**: 2026-1학기 캡스톤 디자인
**목표**: 비교 분석 및 실험 — 새 알고리즘 개발이 아닌 벤치마크/검증 중심

## 현재 단계

> **실험 준비 단계** — 설계안 v3 확정 (4/3), 환경 수령 대기, 4/28 중간발표까지 24일

- **연구 방향**: Skew-Aware Sampling — skewed 거리 분포에서 카디널리티 추정 정확도 개선
  - Track A (Distribution-Aware): 분포를 알 때 → 층화 샘플링
  - Track B (Distribution-Agnostic): 분포를 모를 때 → KDE-pilot 기반 자동 층화
- **설계안**: `plans/연구 설계안_20260403_162818.md` (v3)
- **실험 파라미터**: `experiments/config/experiment_params.yaml`
- **대기 중**: 랩서버 접근 + Exqutor 코드/데이터 (4/7 주 수령 예정)
- **완료**: 논문 분석 82/82편 (100%) + 시리즈 12편 + 연구제안서/수행계획서 제출

### 실행 로드맵

| 주차 | 기간 | 핵심 작업 |
|------|------|----------|
| W1 | 4/4-4/11 | 환경 수령 + 세팅 + Baseline 재현 |
| W2-3 | 4/11-4/25 | RQ1 Motivation → RQ2 Aware → RQ3 Agnostic |
| W4 | 4/25-4/28 | **★ 중간발표 + 중간보고서** |
| W5-8 | 4/28-5/27 | 심화 실험 + 최종발표/포스터 |
| W9-10 | 5/27-6/11 | **최종보고서** |

## 세션 시작 체크리스트

1. `git fetch origin && git status` → 뒤처져 있으면 `git pull --no-rebase origin main`
2. SessionStart hook이 자동으로 상태 출력 (브랜치, 미커밋, 문서 수)
3. 캡스톤 홈페이지 공지 확인 → 새 일정 있으면 3곳 동시 업데이트

### 3곳 동시 업데이트 규칙

일정/상태 변경 시: **CLAUDE.md** + **메모리** (`project_schedule.md`) + **노션** `캡스톤 일정` DB

### 동기화

> "동기화" = git + rsync + Claude 세팅 전부 실행. 상세는 글로벌 CLAUDE.md 참조.

- **팀 공유 파일** (research, records, plans, experiments, submission, templates, scripts): git
- **개인 파일** (.claude, guideline, PHASE_STATE.json, session_state.json): rsync
- .gitignore에 개인 파일 제외 완료 — git에는 팀 공유분만 올라감

## 디렉토리 구조

```
Capstone/
├── CLAUDE.md              이 파일
├── experiments/           실험 코드/결과/분석
│   ├── config/            실험 파라미터
│   ├── results/           RQ별 결과 (rq1_motivation, rq2_aware, rq3_agnostic)
│   └── figures/           시각화
├── research/
│   ├── analysis/          시리즈 분석 (01)~(12) — 완료
│   ├── papers/            원논문 PDF 69편
│   └── summaries/         논문 총정리 82편 — 완료
├── plans/                 연구 설계안/제안서/수행계획서
├── records/
│   ├── meetings/          회의록
│   └── weekly/            주간보고
├── submission/            실제 제출물
├── templates/             양식+샘플
├── scripts/               md2pdf.py, md2docx.py
└── guideline/             활성 5 + archive/ 보관 6 (각 auto.md + manual.md + .sh)
```

## 지침 시스템

guideline/ 폴더에 활성 지침 5개, 각 3파일 세트 (auto.md + manual.md + .sh).

| 키워드 | 지침 | 용도 |
|--------|------|------|
| "실험" | 01_실험지침 | 벤치마크/EXPLAIN ANALYZE |
| "제출" | 02_제출물지침 | 마감별 제출물 생성 |
| "PDF" | 03_문서생성지침 | md → HTML → Chrome CDP → PDF |
| "미팅" | 04_미팅지침 | 카톡 회의록 + 노션 업데이트 |
| "발표" | 05_발표지침 | PPT/포스터/슬라이드 |

보관 (guideline/archive/): 00점검→skill, 01논문분석(완료), 05주간보고→skill, 08설계(완료), 09학습(완료), 10CC활용(완료)

**실행**: `{키워드}` (자동) / `{키워드} 수동` (Phase별 정지) / `./guideline/NN_*_실행.sh`
**수동 모드**: Phase 완료 → 정지 → `/clear` → "다음 phase 이어가자"로 재개. 절대 자동 진행 금지.

## 핵심 일정 (2026-1학기)

| 마감 | 제출물 | 상태 |
|------|--------|------|
| 4/3 | 교수님 미팅 — Skew-Aware Sampling 방향 확정 | ✅ |
| 4/2 | 연구제안서 + 수행계획서 제출 | ✅ |
| 4/7~ | Exqutor 코드·데이터 수령 + 환경 세팅 | ⬜ |
| **4/28** | **중간발표 + 중간보고서 제출** | ⬜ |
| 5/27~5/29 | 최종발표 + 전시회 마감 | ⬜ |
| 6/5 | 전시회 | ⬜ |
| **6/11** | **최종보고서 제출** | ⬜ |

## Exqutor 핵심

- **문제**: pgvector(33.3%), VBASE(50%), DuckDB(100%) — 고정 비율 카디널리티 추정 → 잘못된 실행 계획
- **ECQO**: 인덱스 있을 때 HNSW range query → 정확한 카디널리티 (1~2ms)
- **Adaptive Sampling**: 인덱스 없을 때 모멘텀 기반 동적 샘플링
- **우리의 공략점**: Adaptive Sampling이 **skewed 분포에서 정확도 저하** — 이를 층화 샘플링으로 개선

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
| `plans/` | `문서명_YYYYMMDD_HHMMSS.ext` | `연구 설계안_20260403_162818.md` |
| `records/meetings/` | `YYYYMMDD_제목.md` | `20260403_교수님미팅 샘플링방향전환.md` |
| `records/weekly/` | `주간보고_YYYY-MM-DD.md` | `주간보고_2026-03-28.md` |
| `research/analysis/` | `(NN) 제목.ext` | `(01) Exqutor 상세분석.md` |
| `research/summaries/` | `[N] Title Case 논문제목 총정리.ext` | `[13] pgvector Open-Source ... 총정리.md` |
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

## 참고 링크

- 캡스톤: https://capstone.cs.yonsei.ac.kr/capstone/
- 양식: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=27
- 일정표: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=370
- Exqutor: https://github.com/BDAI-Research/Exqutor
- 팀 GitHub: https://github.com/johyunbin/Capstone
- 팀 Notion: https://www.notion.so/306db4d4869b8039affeca0b0fa4d2fa
