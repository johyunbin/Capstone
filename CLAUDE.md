# CLAUDE.md — Capstone Project Guide

## 프로젝트 개요

**팀명**: 속도는벡터 (연세대학교)
**주제**: Exqutor 논문 기반 벡터 증강 분석 쿼리(VAQ) 최적화 연구
**본 논문**: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2)
**학기**: 2026-1학기 캡스톤 디자인
**목표**: 비교 분석 및 실험 — 새 알고리즘 개발이 아닌 벤치마크/검증 중심

## 현재 단계

> **5/8 21:10 — RQ3 paradigm framework 확정 + Adaptive Sampling launch ready. 다음: 22:00 KST overnight launch (~5h).**
> 5/8 19:00 회의 후 Deep Review Agent (학술 정합성 검증) + 6 백그라운드 에이전트 병렬 산출 → 4 변경 사항 finalize: ① **P5 = "Low-discrepancy / Quasi-random"** 단일 inductive bias (Option B, LSH = Wave 0 fail limitation), ② **★4 = sparse RP** (Achlioptas 2003 PODS, data-independent, ARI #1, **Hybrid 대체**), ③ 누락 critical (Sketch / Mean-Shift / R-tree / MinHash) = limitation 명시, ④ 4강 narrative 변경 X. 박세은 20:38 교수님 카톡 brief draft 발송 예정. 자문 메일 v3 (formal) 은 Multi/Adaptive 결과 후 5/11~5/15 finalize. 다음 미팅 5/22 교수님, 최종발표 **5/27 (D-19)**, 최종보고서 **6/11 (D-34)**.
>
> **W1 sprint 종합 결과** (5/5~5/8, RQ1+RQ2+RQ3 100% 측정 완료):
> - **RQ1**: 13/13 cell ρ < 0 (10 single + 3 multi) — selectivity 작을수록 BERN 부정확 단조 증가, DEEP-KM20 ρ=-0.680 CI [-0.800, -0.440]
> - **RQ2**: 12 single cell × 5 mode × 5 sel → 51/52 paired CI 0 제외, σ-allocation 격차 < 1% (어느 mode 든 비슷, 균등도 충분)
> - **RQ3 paradigm framework** (5/8 20:48 confirm): **5 paradigm × 11 method** — P1 Cluster (HDBSCAN/MiniBatch/GMM) / P2 Spatial (Hilbert/faiss_ivf) / P3 Streaming (MB_partial/Reservoir) / P4 DimReduction (sparse_rp/PCA1D) / P5 Low-discrepancy (LSH/Sobol). **4강** = 5 paradigm 중 4 distinct representative: ★1 HDBSCAN -8.04 (P1) / ★2 MB_partial -7.63 (P3) / ★3 Hilbert -7.54 (P2) / ★4 **sparse RP -6.91 (P4, Achlioptas 2003)**.
> - **Multi 일반화**: 3 cell × 4강 → 단일 sweet spot 17.13% → multi 0.67% (25× 약화) → "단일 정확성 = multi 정확성 *필요조건* 만"
> - **PDX (SIGMOD 2025) 학술 confirmation**: intrinsic_dim + skewness driven algorithm selection (본 thesis 와 정확 일치)
> - **5/8 21:10 launch ready**: Adaptive code (chain_unified 패턴) + Multi paradigm wrapper (11 method) 모두 서버 dry-run 통과. Phase 1 (22:00~01:00 SF1 5 cell) + Phase 2 (01:00~03:00 DEEP/SIFT SF10) overnight.

- **연구 방향**: Exqutor 가 미작동하는 단일 테이블 영역에 대한 분포 정보의 가치 정량화. (단일 → 멀티 일반화는 future work, 단일 정확성은 멀티 정확성의 *필요조건*만 성립.)

### 새 RQ 구조 (5/5 확정)

| RQ | 질문 | 메인 실험 |
|---|---|---|
| **RQ1** | 기존 random sampling 이 skew 데이터셋에서 얼마나 부정확한가? | 2x2 (Block vs Row × Normal vs Skew) — DEEP/SIFT |
| **RQ2** | 분포 아는 상황에서 어떤 방식이 최적? | KM20 + Proportional / **Neyman** / **Anti-Neyman** 3-way ablation |
| **RQ3** | 분포 모르는 상황에서 어떤 방식이 최적? | 7-way 비교 (Offline 4 / Online 2 / Weight 1), Recovery Rate metric |

- **핵심 결과** (RQ1/RQ2 측정 완료분): DEEP 1M selectivity gradient 19.6%p (s=1%), SIFT +3.07~4.39% (DEEP 2배+), 8M +1.76% CONSISTENT
- **본 연구 contribution**: (1) Normal/Skew × Block/Row 정량 비교 (2) Selectivity Gradient (3) Two-Level Decomposition (4) Recovery Rate Framework
- **Limitation 4가지**: KM20 oracle (production X) / 사전 계산 one-time cost / OLTP 범위 외 / 단일→멀티 future work
- **설계안 히스토리**: v3 `plans/archive/연구제안서_20260403_162818.md` → v4 `plans/연구재설계안_20260415_131400.md` → v5 `submission/속도는벡터_중간보고서_20260417_0000.md` + `plans/RQ3설계안_20260416_213500.md` → **v6 (5/5) `plans/RQ재정립_20260505_2122.md`**
- **실험 정리**: `experiments/results/RQ1_RQ2 실험 결과 정리.md`
- **서버**: `165.132.140.240` (capstone2026), 작업 디렉토리 `/mnt/hdd0/home/capstone2026`, 상세는 `memory/reference_server.md`

### 실행 로드맵 (5/8 회의 후 update)

| 단계 | 기간 | 핵심 작업 | 상태 |
|------|------|----------|------|
| W0 | 4/4-4/16 | 환경 + RQ1/RQ2 실험 완료 | ✅ |
| 중간 | 4/17-4/30 | 중간보고서·발표 + 4/28 LearnUs 제출 + 4/30 발표 | ✅ |
| **W1 Sprint** | **5/5~5/8 19:00** | **RQ1+RQ2+RQ3 100% 측정 + 4강 도출 + multi 25× shrinkage + PDX confirmation** | ✅ 완료 |
| **5/8 회의** | 5/8 19:00~19:30 | 비대면 회의 — 결정 3가지 (Adaptive 비교 / 5/27 발표 / SF100) + 자문 outline 3줄 합의 | ✅ 완료 |
| **5/8 RQ3 finalize** | 5/8 19:30~21:10 | **Deep Review (학술 정합성) + 5 paradigm × 11 method + ★4 sparse RP + 6 에이전트 병렬 산출** | ✅ 완료 |
| **W2 자문/launch** | **5/9~5/15** | **22:00 Adaptive launch overnight + 5/9 Multi paradigm + 자문 메일 v3 발송 (Adaptive/Multi 결과 후)** | ← **현재** |
| W3 | 5/16~5/21 | (자문 합의 후) Multi 광범위 + Ensemble + 발표자료 초안 | ⬜ |
| 미팅 | 5/22 | 교수님 미팅 | ⬜ |
| W4 | 5/23~5/26 | 발표자료 최종 마감 + supplementary slide (자문 결과) | ⬜ |
| 발표 | **5/27** | **★ 최종 발표 (D-19 from 5/8)** | ⬜ |
| 전시 | 5/28 | 전시회 자료 마감 | ⬜ |
| W5 | 5/29~6/4 | 최종보고서 drafting (8 section ~38p) | ⬜ |
| W6 | 6/5~6/10 | 최종보고서 finalize + 양식·검토 | ⬜ |
| 보고 | **6/11** | **★ 최종보고서 제출 (D-34 from 5/8)** | ⬜ |

### 다음 단계 (5/8 21:10 RQ3 finalize 후)

1. **⭐⭐⭐ Adaptive Sampling baseline launch** (5/8 22:00 ~ 5/9 03:00, ~5h overnight)
   - Phase 1 (22:00~01:00): SF1 5 cell 순차 (DEEP/SIFT/SSN/WIKI/YFCC)
   - Phase 2 (01:00~03:00): SF10 DEEP+SIFT 병렬 (HDD ≤ 2)
   - Phase 3 (5/9 daytime): SF10 SSN/WIKI/YFCC deferred
   - 코드: `experiments/code/rq3/run_adaptive_sampling.py` + `launch_adaptive_phase1_2.sh` (chain_unified 패턴, 서버 dry-run 통과)

2. **⭐⭐⭐ Multi paradigm 광범위 launch** (5/9 저녁 ~ 5/10 새벽, ~10h)
   - 3 multi cell × 11 method × 5 sel × 5 seed × 100 query = 8250 measurement
   - 코드: `_internal/scripts/measure_multi_paradigm.py` (서버 `cache/rq3/` scp 완료)

3. **⭐⭐ 자문 메일 v3 finalize** (5/11~5/15)
   - 지도확인서 v3 base (`submission/_drafts/속도는벡터_연구지도확인서_20260508_v3.{md,pdf}`) + Adaptive/Multi 결과 통합
   - 채림 + 교수님 발송 (W2 마감)

4. **⭐⭐ 5/27 발표 준비** (W3~W4)
   - Slide redesign 안: `_internal/slide_redesign_v2_20260508.md` (16→18 page, S6.5/S10.5 신규)
   - 5/22 교수님 미팅 reflection

5. **⭐ SF100 (80M) 실험** — 시간 여유 시 (현실적 어려움, 자문 의견 대기)

### W1 Sprint 산출 (5/5~5/8) — 100% 완료 ✅

- **단일 10 cell × 30 method × 5 sel = 1500 measurement** (analyze_10cell_w4.py 재계산, query_id paired alignment)
- **Multi 3 cell × 4강 method × 5 sel = 60 measurement** (5/8 17:50 STAGE 3 finalize)
- **30 method 가지치기**: Tier 1 = 17종 / Tier 2 = 2종 (birch, kde_pilot) / Tier 3 = 1종 (pq) / Pruned = 7종 / Wave 0 = 3종
- **4강 selection** (5/8 21:10 paradigm framework finalize): HDBSCAN -8.04 (P1) / MB_partial -7.63 (P3) / Hilbert -7.54 (P2) / **sparse RP -6.91 (P4, Achlioptas 2003, Hybrid 대체)**
- **PDX (SIGMOD 2025) 학술 confirmation** 추가 (intrinsic_dim + skewness driven algorithm selection 본 thesis 일치)
- **RQ3 30 method 분포·인덱스 leak audit** 완료 (23 clean / 1 oracle / 1 suspect / 5 pending)

**산출물 위치**:
- master 분석본: `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.{md,pdf}`
- 발표 deck (현재): `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.pdf` (16 page)
- 발표 deck redesign 안 (5 paradigm): `_internal/slide_redesign_v2_20260508.md` (515 lines, 16→18 page)
- 지도확인서 v3 (5/8 21:10 finalize): `submission/_drafts/속도는벡터_연구지도확인서_20260508_v3.{md,pdf}` (paradigm naming 정정 4종 + 박세은 카톡 별첨)
- Deep Review (학술 정합성 backbone): `_internal/RQ3_paradigm_심층검증_20260508.md`
- Adaptive Sampling 분석: `_internal/Adaptive_Sampling_method_분석_20260508.md`
- handoff_v13: `_internal/handoff_v13_session_20260508_2110_RQ3확정완료_launch대기.md`

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

## 디렉토리 구조 (2026-04-27 재정비)

루트는 **팀원 핵심 5개 + 도구·양식 2개 + 내부용 1개** 로 정리됨. 팀원 진입 가이드는 루트 `README.md` 참조.

```
Capstone/
├── README.md              팀원 진입점
├── CLAUDE.md              이 파일 (Claude Code 컨텍스트)
│
├── submission/            ⭐ 우리 팀의 모든 공식 문서 — README 있음
│   ├── _drafts/           ⭐ 팀 공유 최신본 + archive — README 있음
│   │   ├── 속도는벡터_중간보고서_*.{docx,pdf}    4/28 마감 후보 (4/27 빌드, 17p)
│   │   ├── 속도는벡터_중간발표_*.{docx,pdf,pptx}  발표 자료 (4/17 v2)
│   │   ├── 팀원 온보딩_*.{md,pdf}                새 팀원 진입 자료
│   │   └── archive/       이전 버전 모음
│   └── 제출완료/          외부에 보낸 자료 (학교 공식 + 멘토 자문)
│
├── experiments/           ⭐ 실험 — README 있음
│   ├── code/rq1/          서버 실험 스크립트
│   ├── code/local_analysis/  로컬 분석 스크립트
│   ├── results/rq1_motivation, rq2_aware/
│   ├── figures/           시각화
│   └── config/            파라미터
│
├── plans/                 연구 설계안 (RQ3설계안 + 재설계안 + archive)
├── reference/              참고 자료 (papers 69편 + summaries 82편 + analysis)
├── templates/             캡스톤 학교 양식 샘플
│
└── _internal/             ⛔ 조현빈 개인 작업 (팀원 무시 OK)
    ├── records/           회의록 (kakaotalk + weekly)
    ├── scripts/           문서 빌드 도구 (md2pdf, _build_docx_v0 등)
    ├── guideline/         Claude Code 자동화 지침 (활성 5 + archive 6)
    ├── learning/          학습 자료
    └── session_state.json 세션 상태
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

## 핵심 일정 (2026-1학기)

| 마감 | 제출물 | 상태 |
|------|--------|------|
| 4/7~ | Exqutor 코드·데이터 수령 + 환경 세팅 | ✅ (4/14) |
| 4/16 | RQ1/RQ2 실험 완료 | ✅ |
| 4/28 23:59 | 중간보고서·발표 PDF 제출 (LearnUs) | ✅ (21:44 박세은) |
| 4/30 19:00 | 중간발표 (인종 A428, 강재현 단독) | ✅ |
| 5/5 20:00 | RQ 재정립 회의 (전원 비대면) | ✅ |
| 5/8 19:00 | RQ1+RQ2+RQ3 실험 마감 + 비대면 회의 | ✅ |
| 5/8 21:10 | RQ3 paradigm framework 확정 (5 paradigm × 11 method, ★4 sparse RP) + Adaptive launch ready | ✅ |
| **5/8 22:00** | **★ Adaptive Sampling overnight launch ← 다음** | ⬜ |
| 5/9 morning | Adaptive Phase 1+2 결과 회수 + 분석 | ⬜ |
| 5/9 daytime | Adaptive Phase 3 (SF10 SSN/WIKI/YFCC) launch | ⬜ |
| 5/9 저녁 | Multi paradigm 광범위 launch (~10h) | ⬜ |
| ~5/15 | 자문 요청 발송 (채림 석사 + 교수님) | ⬜ |
| ~5/21 | 발표자료 초안 마감 | ⬜ |
| 5/22 | 교수님 미팅 | ⬜ |
| 5/26 | 발표자료 최종 마감 | ⬜ |
| **5/27** | **★ 최종 발표 (D-22)** | ⬜ |
| 5/28 | 전시회 자료 마감 | ⬜ |
| **6/11** | **★ 최종 보고서 (D-37)** | ⬜ |
| **4/30 19:00** | **중간발표 (인종 A428, 강재현 주 발표자)** | ⬜ |
| 5/27~5/29 | 최종발표 + 전시회 마감 | ⬜ |
| 6/5 | 전시회 | ⬜ |
| **6/11** | **최종보고서 제출** | ⬜ |

## 카카오톡 회의록

카톡 대화 → `records/kakaotalk/YYYYMMDD_제목.md`

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

## 참고 링크

- 캡스톤: https://capstone.cs.yonsei.ac.kr/capstone/
- 양식: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=27
- 일정표: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=370
- Exqutor: https://github.com/BDAI-Research/Exqutor
- 팀 GitHub: https://github.com/johyunbin/Capstone
- 팀 Notion: https://www.notion.so/306db4d4869b8039affeca0b0fa4d2fa
