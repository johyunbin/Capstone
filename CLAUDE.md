# CLAUDE.md — Capstone Project Guide

## 프로젝트 개요

**팀명**: 속도는벡터 (연세대학교)
**주제**: Exqutor 논문 기반 벡터 증강 분석 쿼리(VAQ) 최적화 연구
**본 논문**: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2)
**학기**: 2026-1학기 캡스톤 디자인
**목표**: 비교 분석 및 실험 — 새 알고리즘 개발이 아닌 벤치마크/검증 중심

## 세션 시작 체크리스트

**새 대화를 시작할 때:**
1. SessionStart hook이 자동으로 프로젝트 상태(브랜치, 미커밋, 문서 수) 출력
2. 모든 Run/Write/Bash 명령어 확인 프롬프트 없이 자동 실행

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
- 설계안 최종: `plans/연구_설계안_YYYYMMDD_HHMMSS.md` + `.pdf`
- 다음 마감: **4/2 연구제안서 + 수행계획서**
- 환경 구축(pgvector + Exqutor 패치 빌드) 시작 전
- 자문위원(박성원) 피드백: 데이터셋 선정, 대조군 설정, 평가 지표 구체화

## 세션 루틴

**캡스톤 작업 시 매번 확인:**
1. 캡스톤 홈페이지(https://capstone.cs.yonsei.ac.kr/capstone/) 공지사항 확인 → 새 일정 있으면 노션 일정 DB 업데이트
2. 일정 변경/추가 시 노션 `캡스톤 일정` DB에 반영

## 디렉토리 구조

```
/                               # 프로젝트 루트
├── CLAUDE.md                   # 이 파일
├── README.md                   # GitHub README
├── .gitignore                  # papers/, tmp, bak 등 제외
│
├── plans/                      # 연구 방향 기획 및 설계 문서
│   ├── 연구_기획안_YYYYMMDD_HHMMSS.md      # 연구 방향 후보 brainstorming (A~J)
│   └── 연구_설계안_YYYYMMDD_HHMMSS.md/pdf  # Cascade Decomposition 설계안
│
├── research/                   # 분석 문서 + 원논문
│   ├── analysis/               # 시리즈 분석 문서
│   │   ├── (01),(02),(07),(08)  # 핵심 분석 (Exqutor + 81편 종합)
│   │   └── archive/            # 중간 산출물 (03~06, 09~12)
│   ├── summaries/              # 개별 논문 총정리 [0]~[81] (82편 × md/pdf/docx)
│   └── papers/                 # 원논문 PDF 69편
│
├── learning/                   # Claude Code 학습 자료
│   ├── kr/                     # 한국어 튜토리얼/팁 (유튜브 스크립트 등)
│   └── us/                     # 영어 튜토리얼/팁
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
    ├── skills/                 # paper-analysis, submission-prep 등 6개
    └── agents/                 # document-validator
```

## 핵심 일정 (2026-1학기)

| 마감 | 제출물 | 상태 |
|------|--------|------|
| ~3/26 | 연구지도 확인서 1~4회차 | ✅ |
| 3/28 | 교수님 미팅 (방향 확정) | ✅ |
| 4/1 | 세미나 | ⬜ |
| 4월 초 | 연구제안서 | ⬜ |
| 4월 중 | 실험 설계 확정 | ⬜ |
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
- 분석 문서: .md (원본) + .pdf (배포용) + .docx (제출용)
- PDF 생성 시 **NanumSquare OTF** 폰트 사용 (한글 임베딩 필수)
- 번호 체계: `(번호) 제목_유형.확장자` — 예: `(01) Exqutor_상세분석.md`
- 연구 방향 문서: `연구_설계안_YYYYMMDD_HHMMSS.md` 형식

## 도구

- **DB**: pgvector (PostgreSQL), DuckDB
- **라이브러리**: Python, NumPy, FAISS
- **분석**: EXPLAIN ANALYZE, pg_hint_plan
- **제출물 양식**: Templates/ 디렉토리 참조

### MD → PDF 변환 환경

```
라이브러리: fpdf2 v2.8.7 (pip install fpdf2)
변환 스크립트: scripts/md2pdf.py
```

**사용 가능 폰트 (로컬 확인 완료)**:
| 폰트 | 경로 | 용도 |
|------|------|------|
| Apple SD Gothic Neo | `/System/Library/Fonts/AppleSDGothicNeo.ttc` | 본문 (Regular + Bold, TTC 직접 로드 가능) |
| NanumSquareOTF | `~/Library/Fonts/NanumSquareOTF_ac*.otf` | 대체 본문 (R/B/EB/L 4종) |
| NanumSquare | `~/Library/Fonts/NanumSquare*.otf` | 대체 본문 (R/B/EB/L 4종) |
| D2Coding | **미설치** — 코드 블록용, 필요시 `brew install font-d2coding` |

**사용법**:
```bash
python3 scripts/md2pdf.py Research/문서이름.md
# → Research/문서이름.pdf 자동 생성 (NanumSquare OTF 고정)
```

**fpdf2 한글 주의사항**:
- Courier 등 core font는 한글 불가 → 코드 블록도 한글 폰트 사용
- TTC 파일 직접 로드 가능 (fpdf2 2.5.1+)
- `uni=True` 파라미터는 deprecated (자동 처리됨)
- D2Coding 미설치 시 코드 블록도 본문 폰트 fallback

## 팀 운영

- 4인 팀, 2명×2그룹 편성 가능
- 주 단위 진행 공유
- 논문 리딩은 팀원 분담 체계
- 조현빈: 코디네이터 역할

## 참고 링크

- 캡스톤 사이트: https://capstone.cs.yonsei.ac.kr/capstone/
- 제출물 양식: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=27
- 학기 일정표: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=370
- Exqutor GitHub: https://github.com/BDAI-Research/Exqutor
- 팀 Notion: https://www.notion.so/306db4d4869b8039affeca0b0fa4d2fa
