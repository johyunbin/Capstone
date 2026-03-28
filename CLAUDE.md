# CLAUDE.md — Capstone Project Guide

## 프로젝트 개요

**팀명**: 속도는벡터 (연세대학교)
**주제**: Exqutor 논문 기반 벡터 증강 분석 쿼리(VAQ) 최적화 연구
**본 논문**: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2)
**학기**: 2026-1학기 캡스톤 디자인
**목표**: 비교 분석 및 실험 — 새 알고리즘 개발이 아닌 벤치마크/검증 중심

## 세션 시작 체크리스트

**새 대화를 시작할 때:**
1. `git fetch origin && git status`로 최신 상태 점검 → 뒤처져 있으면 `git pull --no-rebase origin main` 자동 실행
2. SessionStart hook이 자동으로 프로젝트 상태(브랜치, 미커밋, 문서 수) 출력
3. 모든 Run/Write/Bash 명령어 확인 프롬프트 없이 자동 실행

### Git 동기화 명령어

**"git에 올려줘" (commit + push):**
```bash
cd ~/Capstone && git add -A && git commit -m "sync: 설명" && git push origin main
```

**"git에서 받아줘" (pull):**
```bash
cd ~/Capstone && git pull --no-rebase origin main
```

**워크트리에서 작업 후:**
```bash
# 워크트리에서 commit → push branch → 메인레포에서 merge
git push origin claude/nice-bassi && cd ~/Capstone && git merge claude/nice-bassi && git push origin main
```

## 현재 단계

> **실행 단계** — 연구 방향 설계안 확정, 연구제안서 작성 및 환경 구축 진행 중

- 연구 방향: **Cascaded Vector Similarity Decomposition** (재현 아이디어 기반 3단계 실험)
- 설계안 확정: `plans/연구_설계안_20260328_141451.md` + `.pdf` (RQ4개, 데이터셋5, 지표4, 비교축4)
- 논문 분석: **82/82편 완료 (100%)** + 시리즈 12편 + 원논문 69편
- 지침 시스템: 9대 지침 첫 실행 완료 (00점검/04문서/05주간/06미팅/08설계)
- 다음 마감: **4/2 연구제안서 + 수행계획서**
- 환경 구축(pgvector + Exqutor 패치 빌드) 시작 전
- 자문위원(박성원) 피드백: 데이터셋 선정, 대조군 설정, 평가 지표 구체화 → 설계안에 반영 완료

## 세션 루틴

**캡스톤 작업 시 매번 확인:**
1. 캡스톤 홈페이지(https://capstone.cs.yonsei.ac.kr/capstone/) 공지사항 확인 → 새 일정 있으면 노션 일정 DB 업데이트
2. 일정/상태 변경 시 **3곳 동시 업데이트**: CLAUDE.md + 메모리(`project_schedule.md`) + 노션 `캡스톤 일정` DB

## 지침 시스템

guideline/ 폴더에 11대 지침이 auto.md + manual.md + .sh 3파일 세트로 존재.
사용자가 아래 키워드를 입력하면 해당 지침의 auto.md를 읽고 Phase 순서대로 자동 실행.

| 키워드 | 지침 파일 |
|--------|-----------|
| "점검", "헬스체크", "무결성" | guideline/00_점검지침_auto.md |
| "논문 분석", "총정리", "시리즈" | guideline/01_논문분석지침_auto.md |
| "실험", "벤치마크", "EXPLAIN" | guideline/02_실험지침_auto.md |
| "제출", "보고서", "마감", "연구제안서" | guideline/03_제출물지침_auto.md |
| "PDF", "문서 변환", "md2pdf" | guideline/04_문서생성지침_auto.md |
| "주간", "보고", "이번 주" | guideline/05_주간보고지침_auto.md |
| "미팅", "회의", "브리핑", "카톡" | guideline/06_미팅지침_auto.md |
| "발표", "PPT", "포스터", "슬라이드" | guideline/07_발표지침_auto.md |
| "설계", "기획", "연구 방향" | guideline/08_연구설계지침_auto.md |
| "학습 정리", "스크립트 분석", "learning" | guideline/09_학습정리지침_auto.md |
| "활용", "CC 팁", "CC 점검" | guideline/10_클로드코드활용지침_auto.md |

수동 실행: `{지침명} 자동` 또는 `./guideline/NN_{지침명}_실행.sh`

## 디렉토리 구조

```
/                               # 프로젝트 루트
├── CLAUDE.md                   # 이 파일
├── README.md                   # GitHub README
├── .gitignore                  # papers/, tmp, bak 등 제외
│
├── plans/                      # 연구 방향 기획 및 설계 문서
│   ├── 연구_기획안_YYYYMMDD_HHMMSS.md/pdf  # 연구 방향 후보 brainstorming (A~J)
│   └── 연구_설계안_YYYYMMDD_HHMMSS.md/pdf  # Cascade Decomposition 설계안
│
├── research/                   # 분석 문서 + 원논문
│   ├── analysis/               # 시리즈 분석 (01)~(12) — md+pdf
│   ├── summaries/              # 개별 논문 총정리 [0]~[81] (82편 × md/pdf)
│   └── papers/                 # 원논문 PDF 69편
│
├── guideline/                  # 9대 지침 시스템
│   ├── prompts/                # 지침 제작 프롬프트 (원본)
│   ├── NN_{지침명}_auto.md      # 자동 실행용 (9개, 00~08)
│   ├── NN_{지침명}_manual.md    # 수동 참조용 (9개, 00~08)
│   └── NN_{지침명}_실행.sh      # bash 오케스트레이터 (9개, 00~08)
│
├── records/                    # 회의록 + 주간보고
│   ├── meetings/               # 회의록 (YYYYMMDD_제목.md)
│   └── weekly/                 # 주간 작업일지 (주간보고_YYYY-MM-DD.md)
│
├── submission/                 # 실제 제출물 (자문내역서, 연구지도확인서 등)
│
├── templates/                  # 캡스톤 제출물 양식 및 예시
│   ├── forms/                  # 양식 (연구지도확인서, 결과보고서, 회의록 등)
│   └── samples/                # 샘플 (중간발표/보고서/포스터/최종보고서)
│
└── .claude/                    # Claude Code 설정
    ├── settings.json           # 권한 + hooks
    ├── hooks/                  # session-init, save-session-state
    ├── skills/                 # 6개 (→ guideline/ 지침에 흡수됨, 하위호환용 유지)
    └── agents/                 # document-validator
```

## 핵심 일정 (2026-1학기)

| 마감 | 제출물 | 상태 |
|------|--------|------|
| ~3/26 | 연구지도 확인서 1~4회차 | ✅ |
| 3/26 | 1차 자문내역서 + 자문컨택내역 (런어스 제출) | ✅ |
| 3/28 | 교수님 미팅 (방향 확정) | ✅ |
| 4/1 | 세미나 (초청 강연, 전해곤 교수님) | ⬜ |
| 4/2 | 연구제안서 + 수행계획서 제출 | ⬜ |
| 4월 중 | 실험 설계 확정 | ✅ (설계안 3/28 확정) |
| 5월 | 중간발표 + 중간보고서 | ⬜ |
| 6월 | 최종발표 + 최종보고서 + 전시회 | ⬜ |

## 본 논문(Exqutor) 핵심 요약

- **문제**: pgvector(33.3%), VBASE(50%), DuckDB(100%) — 벡터 연산 카디널리티를 고정 비율로 추정 → 잘못된 실행 계획
- **해법 1 — ECQO**: 인덱스가 있을 때 HNSW로 range query를 실행해 정확한 카디널리티 획득 (1~2ms 오버헤드)
- **해법 2 — Adaptive Sampling**: 인덱스 없을 때 모멘텀 기반 동적 샘플링으로 추정
- **성과**: pgvector 최대 1000배, VBASE 10000배, DuckDB 1.5~37배 속도 향상
- **벤치마크**: TPC-H/TPC-DS 확장 VAQ 벤치마크 (range query 기반)

## 실험 설계 (초안 — 미확정)

### 데이터셋 후보
- Small: SIFT1M, GloVe-100
- Medium: Deep10M, GIST1M
- Large: Deep1B (하드웨어 허용 시)

### 평가 지표
- Recall@k, QPS, latency (p50/p99), 실행 계획 비용 추정 오차

### 비교축
- 선택도 sweep: 0.1% → 1% → 10% → 50% → 90%
- 필터 유형: label, range, compound
- 전략: pre-filter, post-filter, hybrid

### 대상 시스템
- pgvector (baseline), VBASE, DuckDB
- Exqutor 적용 전/후 비교

## 문서 작성 규칙

### 언어 및 스타일
- **한국어** 기본. 학술 용어는 영어 병기 가능
- 서사적 학술 산문 선호 (bullet 나열 지양)
- 구조: 배경 맥락 → 핵심 아이디어 → 번호 매긴 기법 → 후속 질문

### 기술적 상세
- 데이터셋, 하드웨어 스펙, baseline, 핵심 메트릭 — 항상 포함
- 피상적 요약 지양. 실험 조건과 한계까지 다룰 것
- EXPLAIN ANALYZE 결과는 반드시 첨부

### 파일 포맷
- 분석 문서: .md (원본) + .pdf (배포용)
- PDF 생성 시 **Apple SD Gothic Neo** 폰트 사용 (Chrome headless 렌더링)
- 번호 체계: `(번호) 제목_유형.확장자` — 예: `(01) Exqutor_상세분석.md`
- 연구 방향 문서: `연구_설계안_YYYYMMDD_HHMMSS.md` / `연구_기획안_YYYYMMDD_HHMMSS.md` 형식 (편집 시 타임스탬프 갱신)

## 도구

- **DB**: pgvector (PostgreSQL), DuckDB
- **라이브러리**: Python, NumPy, FAISS
- **분석**: EXPLAIN ANALYZE, pg_hint_plan
- **제출물 양식**: Templates/ 디렉토리 참조

### MD → PDF 변환 환경

**중요: fpdf2 사용 금지** — 한글 폰트 깨짐. Chrome CDP(DevTools Protocol) 방식만 사용.

```
방식: md → HTML(markdown) → Chrome CDP (Page.printToPDF) → PDF
변환 스크립트: scripts/md2pdf.py
의존성: pip install markdown websocket-client, Google Chrome 설치 필요
Chrome 경로: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
폰트: Apple SD Gothic Neo (시스템 폰트, Chrome이 직접 렌더링)
```

**사용법**:
```bash
python3 scripts/md2pdf.py research/summaries/문서이름.md
# → research/summaries/문서이름.pdf 자동 생성
```

**PDF 스타일 규칙**:
- 헤더: CDP `headerTemplate: "<span></span>"` — 날짜/URL 완전 제거
- 꼬리말: CDP `footerTemplate`로 페이지 번호만 가운데 표시
- 페이지 시작 라인 통일: `.page-break + * { margin-top: 0 }`
- 제목(h1~h4) 뒤에는 반드시 본문이 함께 (page-break-after: avoid)
- 문단/리스트/코드 블록 내부 짤림 금지 (page-break-inside: avoid)
- 강제 페이지 구분: `<div class="page-break"></div>` (마크다운에 직접 삽입)

## 카카오톡 대화 처리

사용자가 카카오톡 대화를 붙여넣으면 `records/meetings/YYYYMMDD_제목.md`에 구조화된 회의록으로 저장:
- 날짜, 참석자, 주요 논의, 결정사항, 후속 과제
- 저장 후 Notion 팀 회의록 DB 업데이트 여부 확인

## 팀 운영

- 4인 팀, 2명×2그룹 편성 가능
- 주 단위 진행 공유
- 논문 리딩은 팀원 분담 체계
- 조현빈: 코디네이터 역할

| 이름 | 역할 | GitHub |
|------|------|--------|
| 조현빈 | 코디네이터 | johyunbin |
| 박세은 | 팀원 | triangle-park |
| 강재현 | 팀원 | newagency |
| 이동욱 | 팀원 | dlee004 |

## 참고 링크

- 캡스톤 사이트: https://capstone.cs.yonsei.ac.kr/capstone/
- 제출물 양식: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=27
- 학기 일정표: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=370
- Exqutor GitHub: https://github.com/BDAI-Research/Exqutor
- 팀 GitHub: https://github.com/johyunbin/Capstone
- 팀 Notion: https://www.notion.so/306db4d4869b8039affeca0b0fa4d2fa
