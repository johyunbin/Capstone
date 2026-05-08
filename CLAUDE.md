# CLAUDE.md — Capstone Project Guide

## 프로젝트 개요

**팀명**: 속도는벡터 (연세대학교)
**주제**: Exqutor 논문 기반 벡터 증강 분석 쿼리(VAQ) 최적화 연구
**본 논문**: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2)
**학기**: 2026-1학기 캡스톤 디자인
**목표**: 비교 분석 및 실험 — 새 알고리즘 개발이 아닌 벤치마크/검증 중심

## 현재 단계

> **5/8 22:00 — Single 100% (10 cell × 5 mode) + Multi SF10/SF1 진행 + 6 audit ✅ + 자문 메일 v4 박성원 멘토 ready. 다음: 5/9 morning 4 측정 회수.**
> 5/8 21:10 RQ3 paradigm framework 확정 후 50분간 collateral sprint — Single Adaptive 분석 (Outcome A 판정, HDBSCAN 7/10 sig + sparse_rp 0/10 동등) + 자문 메일 v4 박성원 멘토 단독 (sparse_rp = paradigm anchor reframe) + 보고서 outline v2 (516 lines, 8 section ~40p) + 6 audit (V1 matrix / V2 data integrity / V3 §10.7 narrative / V4 algorithm fidelity Section VI exact / V5 extra experiments priority / V6 semantic Adaptive 직관 vs paper) 모두 ✅. ★4 sparse_rp = paradigm anchor reframe 적용 (standalone 우위 X 정직 reporting + paradigm coverage 가치). Adaptive 알고리즘 = Section VI hyperparam 정확 일치 + paper 의미론 (across-query 50-batch momentum update) 본 구현과 일치.
>
> **W1 sprint 종합 + 5/8 evening sprint 결과** (5/5~5/8 22:00, RQ1+RQ2+RQ3+Adaptive 100% 측정 + 6 audit):
> - **Single 매트릭스 49/50** (10 cell × {RQ1 km20 / RQ2 5-mode / K-sweep / RQ3 11 method / Adaptive} = 98%, 단일 결손 = YFCC_sf10 K-sweep 1 cell × 4 K → 22:00 launch 보강 진행 중, ~24:00 finalize)
> - **Multi 측정 진행 중**: SF10 paradigm 11 method (PID 4100549, ~5/9 03~05 finalize) + SF10 Adaptive (PID 4100548, ~22:00 finalize) + Multi SF1 setup (Agent W, ETA ~5/9 02:00)
> - **RQ3 paradigm framework** (5/8 20:48 confirm): **5 paradigm × 11 method** — P1 Cluster (HDBSCAN/MiniBatch/GMM) / P2 Spatial (Hilbert/faiss_ivf) / P3 Streaming (MB_partial/Reservoir) / P4 DimReduction (sparse_rp/PCA1D) / P5 Low-discrepancy (LSH/Sobol). **4강** = 5 paradigm 중 4 distinct representative: ★1 HDBSCAN -8.04 (P1) / ★2 MB_partial -7.63 (P3) / ★3 Hilbert -7.54 (P2) / ★4 **sparse RP -6.91 (P4, Achlioptas 2003)**.
> - **Single Adaptive paired Δ% (Outcome A + B 혼합)**: HDBSCAN 10/10 win + 7/10 sig (paired Wilcoxon p<0.05) / Hilbert 9/10 win + 6/10 sig / MB_partial 8/10 win + 6/10 sig (★1~★3 = Outcome A 우위) / **sparse_rp 4/10 win + 0/10 sig (Outcome B 동등)** → ★4 = paradigm P4 anchor + 학습 free production-friendly tier 가치 reframe (보고서 outline v2 4 outcome 정의: A=4강 우위, B=동등, C=Adaptive 우위 thesis fail, D=Hybrid)
> - **6 audit 모두 ✅** (V1~V6, narrative evidence integrity 보증) + 별표 tier inflation 8 cell + multiple comparison correction 1줄 disclaimer 권장
> - **자문 메일 v4 박성원 멘토 ready** (90% filled, Multi 결과 §2 도착 후 finalize → 5/15~5/20 발송)
> - **PDX (SIGMOD 2025) 학술 confirmation**: intrinsic_dim + skewness driven algorithm selection (본 thesis 와 정확 일치)
> - **Multi 일반화**: 3 cell × 4강 → 단일 sweet spot 17.13% → multi 0.67% (25× 약화) → "단일 정확성 = multi 정확성 *필요조건* 만"

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
- **설계안 히스토리**: v3 `plans/archive/연구제안서_20260403_162818.md` → v4 `plans/archive/2026_05_08_supersed/연구재설계안_20260415_131400.md` → v5 `submission/속도는벡터_중간보고서_20260417_0000.md` + `plans/archive/2026_05_08_supersed/RQ3설계안_20260416_213500.md` → **v6 (5/5) `plans/RQ재정립_20260505_2122.md`**
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
| **5/8 evening sprint** | 5/8 21:10~22:00 | **Single Adaptive 분석 + 자문 메일 v4 박성원 멘토 + 보고서 outline v2 + 6 audit (V1~V6) + Multi 측정 launch** | ✅ 완료 |
| **W2 자문/launch** | **5/9~5/15** | **5/9 morning 4 측정 회수 (Multi 11-method/Adaptive/YFCC K-sweep/Multi SF1) + master_v6 §10.6 fill + 자문 메일 v4 박성원 발송 ready** | ← **현재** |
| W3 | 5/16~5/21 | (자문 합의 후) Multi 광범위 + Ensemble + 발표자료 초안 | ⬜ |
| 미팅 | 5/22 | 교수님 미팅 | ⬜ |
| W4 | 5/23~5/26 | 발표자료 최종 마감 + supplementary slide (자문 결과) | ⬜ |
| 발표 | **5/27** | **★ 최종 발표 (D-19 from 5/8)** | ⬜ |
| 전시 | 5/28 | 전시회 자료 마감 | ⬜ |
| W5 | 5/29~6/4 | 최종보고서 drafting (8 section ~38p) | ⬜ |
| W6 | 6/5~6/10 | 최종보고서 finalize + 양식·검토 | ⬜ |
| 보고 | **6/11** | **★ 최종보고서 제출 (D-34 from 5/8)** | ⬜ |

### 다음 단계 (5/9 morning trigger checklist)

1. **⭐⭐⭐ 5/9 morning 4 측정 회수 + 분석** (~30분, 본 §0 진입 즉시)
   - flag 점검: `ssh capstone "ls /tmp/*_done.flag"` (4 flag 기대)
   - 결과 회수: Multi paradigm 11 method (33 csv) + Multi SF10 Adaptive + YFCC sf10 K-sweep (4 parquet) + Multi SF1 setup (3-6 parquet)
   - `analyze_multi_paradigm.py` 실행 → master_v6 §10.6 fill (agent 위임)
   - master_v6 §10.5 의 YFCC sf10 row update (K-sweep 보강)

2. **⭐⭐⭐ 자문 메일 v4 박성원 멘토 finalize + 발송 ready** (~10분, 5/9 morning)
   - `submission/_drafts/속도는벡터_자문메일_박성원멘토_20260508_v4.md` 의 §2 Multi 결과 fill
   - PDF 변환: `python3 scripts/md2pdf.py`
   - 사용자 review → 5/15~5/20 박성원 멘토 발송 결정

3. **⭐⭐ P1 즉시 task 4종** (5/10 일, ~3h 합산)
   - MinHash 측정 (P5 hashing 보강, ~0.5h) — LSH Wave 0 fail 의 직접 보강
   - per-stratum BERN per-K 재분석 (~2h, 분석만, 기존 cache 재사용)
   - Tier 2 (birch, kde_pilot) narrative 정정 (~0h, 문서만) — 강재현 audit 결과 kde_pilot KM20 leak
   - Adaptive 회수 + 4강 paired Δ% 점검 (~10분)

4. **⭐⭐ 5/27 발표 준비** (W3~W4, 5/13 ~ 5/26)
   - Slide redesign 안 적용: `_internal/slide_redesign_v2_20260508.md` (515 lines, 16→18 page, S6.5/S10.5 신규)
   - Adaptive×4강 Ensemble (matched-budget mode B, ~5h, 5/13 evening)
   - K-aware sweep 확장 (SIFT/SSN/WIKI/YFCC × 2 SF × 4K = 32 cell, ~15h, 자문 회신 후)
   - 5/22 박광현 교수님 미팅 reflection

5. **⭐ SF100 (80M) 실험 = scope 제외** (5/8 22:16 사용자 결정) — SF1/SF10 만으로 본 연구 narrative 완결, SF100 은 future work 으로 보고서 limitation 명시

6. **⭐ 6/11 최종보고서 drafting** (W5~W6, 5/29 ~ 6/10, ~40h)
   - Outline v2 base (`plans/최종보고서_outline_v2_20260508.md`, 516 lines)
   - 4 팀원 분담 (박세은 통합 / 조현빈 §3 §4.1 / 이동욱 §2 §4.2 / 강재현 §4.3)

### W1 Sprint 산출 (5/5~5/8) — 100% 완료 ✅

- **단일 10 cell × 30 method × 5 sel = 1500 measurement** (analyze_10cell_w4.py 재계산, query_id paired alignment)
- **Multi 3 cell × 4강 method × 5 sel = 60 measurement** (5/8 17:50 STAGE 3 finalize)
- **30 method 가지치기**: Tier 1 = 17종 / Tier 2 = 2종 (birch, kde_pilot) / Tier 3 = 1종 (pq) / Pruned = 7종 / Wave 0 = 3종
- **4강 selection** (5/8 21:10 paradigm framework finalize): HDBSCAN -8.04 (P1) / MB_partial -7.63 (P3) / Hilbert -7.54 (P2) / **sparse RP -6.91 (P4, Achlioptas 2003, Hybrid 대체)**
- **PDX (SIGMOD 2025) 학술 confirmation** 추가 (intrinsic_dim + skewness driven algorithm selection 본 thesis 일치)
- **RQ3 30 method 분포·인덱스 leak audit** 완료 (23 clean / 1 oracle / 1 suspect / 5 pending)

**산출물 위치** (5/8 22:00 기준):

분석 본체:
- master 분석본: `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.{md,pdf}` — §10.5 sweet spot + §10.6 Multi placeholder + §10.7 Single Adaptive
- §10.7 Adaptive: `experiments/results/master_v6_§10.7_Adaptive_분석_20260508.md` (Outcome A 판정)
- 10cell narrative: `experiments/results/10cell_narrative_종합_20260508.{md,pdf}`

자료 / 문서 (5/8 finalize):
- 자문 메일 v4 박성원 멘토 (5/9 fill 대기): `submission/_drafts/속도는벡터_자문메일_박성원멘토_20260508_v4.md`
- 지도확인서 v3 (5/8 21:10 finalize): `submission/_drafts/속도는벡터_연구지도확인서_20260508_v3.{md,pdf}`
- 발표 deck (현재): `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.pdf` (16 page)
- 발표 deck redesign 안 (5 paradigm): `_internal/slide_redesign_v2_20260508.md` (515 lines, 16→18 page, S6.5/S10.5 신규)
- 보고서 outline v2: `plans/최종보고서_outline_v2_20260508.md` (516 lines, 8 section ~40p, v1 → v2 변경 5종)
- Deep Review (학술 정합성): `_internal/RQ3_paradigm_심층검증_20260508.md`
- Adaptive 분석: `_internal/Adaptive_Sampling_method_분석_20260508.md`

6 audit reports (5/8 21:48 ~ 22:04, 모두 ✅):
- `_internal/audit_matrix_20260508.md` — 측정 매트릭스 49/50 single + Multi 진행 중
- `_internal/audit_data_integrity_20260508.md` — A- 등급, schema/null/paired 100% PASS
- `_internal/audit_master_v6_§10.7_20260508.md` — narrative fully consistent ✅
- `_internal/audit_adaptive_algorithm_20260508.md` — Section VI exact + 식 1~6 line-by-line
- `_internal/audit_extra_experiments_20260508.md` — P1/P2/P3 priority 권장
- `_internal/audit_adaptive_semantic_20260508.md` — across-query batch update, 본 구현 일치

handoff chain:
- `_internal/handoff_v13_session_20260508_2110_RQ3확정완료_launch대기.md`
- `_internal/handoff_v14_session_20260508_2200_FullExperimentLaunch.md` ← **다음 세션 진입점**

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
| 5/8 22:00 | Single Adaptive 분석 + 자문 메일 v4 + 보고서 outline v2 + 6 audit (V1~V6) + Multi 측정 launch | ✅ |
| **5/9 morning** | **★ 4 측정 회수 (Multi 11-method/Adaptive/YFCC K-sweep/Multi SF1) + master_v6 §10.6 fill ← 다음** | ⬜ |
| 5/9 daytime | Adaptive Phase 3 (SF10 SSN/WIKI/YFCC) launch + 자문 메일 v4 박성원 finalize | ⬜ |
| 5/10 | P1 task 4종 (MinHash + per-K 재분석 + Tier 2 정정 + Adaptive 회수) | ⬜ |
| 5/15~5/20 | 자문 메일 v4 박성원 멘토 발송 + 회신 대기 | ⬜ |
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
