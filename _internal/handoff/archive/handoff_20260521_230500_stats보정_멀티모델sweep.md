# handoff 20260521 23:05 — stats 파이프라인 보정 + 멀티모델 검증 sweep + 측정 sf=10 연장

> 이전 handoff(`_internal/handoff/archive/handoff_20260521_190000_pgvector평면확장_sequential재측정.md`) → 본 문서. 이 문서 하나로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 세션(5/21 20:46~23:05)은 — (1) measure 4병렬 sf=10 측정의 daemon 버그·고아 프로세스 정리, (2) **stats 파이프라인 보정** (Codex 2회 교차검증 → `analyze_latency.py`·`stats_poc_6_4_extended.py` 8개 수정·실측 테스트 통과), (3) **측정을 sf=10 48 cell 완결까지 연장** (DEADLINE 22:00 UTC·sf=1 단계 제거·midnight-stop 해제 — ~05:20 KST 완결 예상), (4) **멀티모델 검증 sweep** (Codex C1/C2/C3 + Gemini G1/G2 — v13 헤드라인 수치·6/11 보고서 framing의 실질 결함 발견), (5) AGENTS.md 심링크 단일화. → 다음 세션 = 측정분 회수·분석 확인 + T6 미팅자료·T7 슬라이드 + T11 v13 재검증 + Gemini 웹앱 자동화 → **5/22 14:00 박광현 미팅**.
>
> **★ 측정·T5 완료 (5/22 08:55 갱신)**: sf=10 측정 03:59 KST 종료 — **33/48 cell** (WIKI sf=10 12 cell 전체 + q3 sel0.1 ×3 누락 = honest exception). daemon T5 04:04 KST 완료 — `poc_6_4_extended/` 산출. **핵심 결과**: phase4_extension(SIFT/SSN/YFCC sf=10) B1 anchor plan 회복 91.5%·effect size 94.7% small·model3 condition %SS **0.00% (p=0.973)** → DEEP sf=10 결론이 SIFT/SSN/YFCC로 **일반화 확인** (보정된 파이프라인 산출). 상세 §3.2·§3.2.1.

---

## 0. 가장 먼저 — 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계. `active/`에 현행 1세트(본 문서 + 복붙 프롬프트)만.
- **★ 직전 handoff (carry)**: `_internal/handoff/archive/handoff_20260521_190000_pgvector평면확장_sequential재측정.md`.
- **★ 보고서 정본 (carry)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.{md,pdf,docx}` — ★ 본 세션 Codex C2가 framing·정합성 결함 9건 발견 (§7.2). 6/11 제출 전 개정 필요.
- **★ 5/22 박광현 미팅 사전보고**: `submission/_drafts/속도는벡터_5_22_박광현미팅_사전보고_20260520_2355.md` — §3.3 측정결과 placeholder 미충족 + **scope 정정 필요** (§4 task 2).
- **★ 멀티모델 findings 보존**: `_internal/cache/rq3/multimodel_findings_20260521/` — Codex C1/C2/C3·T4·T8 findings.json + Gemini G1/G2·meeting 리뷰 log + `stats_pipeline_fix.diff`.
- **★ 본 세션 plan (carry)**: `~/.claude/plans/mossy-fluttering-hennessy.md`.

## 1. 본 연구 framing (carry · 불변)

본 연구 = Exqutor 논문(arXiv:2512.09695v2) 의 표본 선택 단계 하나 (무작위 Bernoulli → 분포 인지 stratification) 개입의 효과를 전 변인에 걸쳐 검증. 3-way matched — B1(대조군, 논문 그대로 Bernoulli)·CaseA(완전 대체, 음성 대조군)·CaseB(결합 `(est_b1+est_method)/2`).

「엔진 적용 검증」 = 오프라인 검증된 카디널리티 추정치를 patched PostgreSQL(55435)에 주입 → "추정치 → 실행 계획 → end-to-end latency" 측정. 정본 phase2 = DEEP sf=10. PoC 평면 확장 = SIFT/SSN/WIKI/YFCC sf=10 일반화.

★ **측정 latency layer = 4 condition** (baseline/B1/oracle/CaseB) — CaseA는 latency 측정에 없음. 오프라인 추정 연구의 3-way(B1/CaseA/CaseB)와 측정 layer가 다름 (본 세션 T3·Codex 확인 — measure harness docstring 명시, 의도된 설계).

## 2. 본 세션(5/21 20:46~23:05)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| daemon 버그 fix | ✅ | `auto_post_bc_4par.sh` 대기루프 `grep -q active`가 "inactive" 부분일치 → 무한루프(자정 회수 영영 미발화). `grep -qx`식 정확매칭 + SSH 실패 robust 처리로 수정·재기동 |
| 고아 프로세스 정리 | ✅ | 이전 run 잔여 SSN q12 측정 프로세스(systemd reparent) kill — 5-way contention·write 충돌 위험 제거 |
| T3 기존 데이터 검증 | ✅ | estimates 13 parquet 정합 OK · seq vs 4par contention 정량 · variant 구조 해독 |
| T4+T8 stats 파이프라인 보정 | ✅ | Codex 2회 교차검증 → `analyze_latency.py`·`stats_poc_6_4_extended.py` 8개 수정 → 실측 파이프라인 테스트 통과 (§3.1) |
| 측정 sf=10 연장 | ✅ | 사용자 결정 "sf=10 완결까지" — `measure_4par_midnight.sh` DEADLINE 15:00→22:00 UTC·sf=1 단계 주석처리·`midnight-stop.timer` 해제·`phase4-4par` 재기동 (§3.2) |
| 멀티모델 검증 sweep | ✅ | Codex C1(v13 분석)·C2(6/11 보고서)·C3(repo hygiene) + Gemini G1(논문 대조)·G2(보고서 framing) — findings 보존·Claude 교차검증 (§7) |
| AGENTS.md 단일화 | ✅ | stale·sed 잔재 → `ln -s CLAUDE.md AGENTS.md` 심링크 (한 소스) |

## 3. ★★★ 핵심 결과

### 3.1 stats 파이프라인 보정 (T4+T8) — 완료·테스트 통과

Codex 교차검증(measure/gen/stats_extended 1차 + analyze_latency 2차 + diff 재검증 3차)이 발견한 결함을 보정. **두 파일 모두 수정·미커밋** — diff = `_internal/cache/rq3/multimodel_findings_20260521/stats_pipeline_fix.diff`.

- **`analyze_latency.py`**: ① `paired_stats` — injection_fired=False treatment variant 페어링 제외 / timeout pair는 `pairing_valid=False` 플래그 + paired 통계 NaN (양쪽 n_timeout=0일 때만 유효) / Holm family = 유효 p만. ② `_hedges_g_paired` — 소표본 보정 `4n-9`→`4n-5`(df=n-1) + sd=0·mean≠0 → nan. ③ `_cliffs_delta_paired` → `_rank_biserial_paired`(matched-pairs rank-biserial — paired 정식 효과크기). ④ `--output` 기본값 `<input>/figures` (stats_poc `PAIRED_P4` 경로 규약 일치 — 이전엔 daemon이 paired_stats.csv를 다른 곳에 써서 빈 분석 위험이었음).
- **`stats_poc_6_4_extended.py`**: ① `build_long_df` +`injection_fired`·`n_timeout` 컬럼. ② `poc3` — `(baseline OR injection_fired) AND n_timeout=0`만 fit. ③ `_collapse_caseb` — CaseB 13 method를 (cell,rep) 평균으로 접어 4 condition 균형(pseudo-replication 제거) + method 완전 group만 collapse. ④ `_try_fit` — 분산분해 %는 가산적 Type-I(순차) SS, partial p는 Type-III(`p_typ3`). ⑤ `main()` — `paired`에서 `pairing_valid=False` 행 제외. ⑥ summary.md·figure 라벨 Type-I 정정.
- **테스트**: 두 스크립트 실측 데이터(phase2/3 + phase4 7 cell)로 실행 — 무crash, sanity 전항 통과, poc3 필터·CaseB 집계·Type-I SS 작동 확인.
- **note**: phase2/3 paired_stats.csv는 기존(`4n-9`) 그대로 — phase4만 신규(`4n-5`). ~0.4% 차이, banding 무영향. phase2/3 재생성은 정본 carry 수치 미세변동 유발이라 보류.

### 3.2 측정 sf=10 + T5 — ✅ 완료 (5/22 갱신)

- **측정**: `phase4-4par`가 sf=10을 측정해 **2026-05-21 18:59 UTC (5/22 03:59 KST) 종료**. `measure_4par_midnight.sh` 수정본(DEADLINE 22:00 UTC·sf=1 제거) 정상 작동, `midnight-stop.timer` 해제로 자정에 안 끊김.
- **수확 = 33/48 cell**. 누락 15 = **WIKI sf=10 전체 12 cell**(q3/q9/q10/q12 × 3 sel — dim 768 → statement_timeout, honest exception) + **q3 sel=0.1 ×3**(SIFT/YFCC/SSN — 고selectivity q3 느림). 즉 **유효 측정 = SIFT/SSN/YFCC sf=10 (33 cell, q3 sel0.1만 일부 누락)**.
- **T5 daemon**: `auto_post_bc_4par.sh`가 측정 종료 감지 → rsync 33 cell + `analyze_latency.py` + `stats_poc_6_4_extended.py`(둘 다 수정본) → **04:04 KST "pipeline complete"**. 산출 = `_internal/cache/rq3/latency/poc_6_4_extended/`(summary.md + 9 CSV) + `experiments/figures/보고서_6_11/poc_6_4_extended/`. **수정된 stats 파이프라인이 timeout 섞인 풀 데이터에서 무crash·sanity 전항 통과 — 보정본 실데이터 검증 완료.**
- ★ measure 정합성 carry: 정본 phase2(DEEP sf=10)는 sequential, 평면확장은 4병렬 — 조건 차이는 honest limitation. contention = §3.3.

### 3.2.1 ★ T5 핵심 결과 (다음 세션 T6/T7 정본 — `poc_6_4_extended/summary.md`)

- **평면 비교 (B1 anchor)** — phase4_extension(SIFT/SSN/YFCC sf=10, 378 paired): plan 회복 **91.5%** · mean|g| **0.205** · small effect **94.7%** · p_holm<0.05 **0.0%**. cf. phase2(DEEP sf=10 carry): 회복 95.2%·small 86.9%. → **동일 패턴 일반화** (회복률 높고 latency effect size 작음).
- **dataset 비교 (B1 anchor, sf=10)**: DEEP 회복 93.2%·|g|0.34 / SIFT 94.2%·0.20 / SSN 92.9%·0.23 / YFCC 86.6%·0.19. → 4 dataset 모두 높은 회복·작은 effect.
- **분산분해 model3 (no-baseline, n=2115, R²=0.801)** — Type-I SS: sel 47.7% · qid 28.7% · query 3.7% · **condition 0.00% (Type-III p=0.973)** · 교호작용 ~0% · Residual 19.9%. → **"어느 추정치를 주입하든 latency 동등, condition은 변동을 0% 설명"이 보정된 파이프라인에서도 확정** (carry "0.00% p=0.866"과 동일 결론 — 단 이번엔 Type-I SS·injection 필터·CaseB 집계 보정본 산출이라 신뢰도 ↑).
- ★ **T6/T7 framing**: "pgvector sf=10에서 DEEP 외 SIFT/SSN/YFCC로 dataset 일반화 확인 — plan 회복 ~87-94%, condition이 latency 변동 0% 설명. WIKI sf=10(dim 768)은 statement_timeout honest exception. sf=1/sf=100/다중은 5/23+ 측정."

### 3.3 측정 contention 정량 (T3 — handoff 직전 세션 §8(5b) deliverable)

seq_backup 12 cell vs 4par의 동일 cell 7개 비교 — 4병렬이 절대 latency를 **중앙값 ~10-15%, 최대 +48%(q9_SIFT)** 부풀림. 단 seq(~19:00 KST)와 4par(~20:50 KST)는 측정 시각이 달라 contention과 배경부하가 섞임(순수 self-contention은 더 작을 수 있음). **핵심**: 본 연구 paired 비교(CaseB vs B1·plan 회복)는 cell 내 16 variant가 같은 contention 환경에서 측정돼 **within-cell paired는 contention에 강건** — contention은 cell 간 절대 latency 비교만 오염. T6 honest limitation으로 "4병렬 = 절대 latency ~10-15% 부풀림, paired 비교 강건" 정량 기술.

### 3.4 carry 정본 (직전 세션 그대로 — 단 §7.1 C1 경고 참조)

보고서 _171521 compact 15p · PoC DEEP sf=10 20 cell · 3-7× · 94.9% plan 회복 · 89.1% · 중앙값 −4.38% · model3 condition 0.00% p=0.866 · plan_signature 1-tuple · Q9 sel=0.1 honest exception · v2 PPTX. **★ 단 89.1%·−4.38%·model3 0.00%은 Codex C1이 산출 로직 결함 지적 — §7.1·T11 참조. 정성 결론은 살아남을 가능성 크나 정확한 수치는 재계산 필요.**

## 4. ★ 다음 세션 task (5/22 14:00 박광현 미팅 대비)

1. **[✅ 완료 — 5/22 아침 확인 끝] 측정·T5**: 측정 33/48 cell 종료·daemon T5 04:04 완료 (§3.2·§3.2.1). 정본 산출 = `_internal/cache/rq3/latency/poc_6_4_extended/summary.md` + 9 CSV, figure = `experiments/figures/보고서_6_11/poc_6_4_extended/`. → 다음 세션은 이 결과로 바로 T6/T7 진행. (수정 파이프라인 무crash·sanity 통과 확인됨.)
2. **[★ T6] 5/22 미팅 사전보고 §3.3 채움 + scope 정정**: 측정은 **sf=10만** (sf=1·sf=100·다중은 미측정 — 5/23+ 재개). 문서가 가정한 "160 cell·5/21 22:00 완료"는 부정확 → §3 scope를 "sf=10 단일 4종 dataset 일반화 검증"으로 정정. + Gemini meeting-doc 리뷰 5점(§7.4) + §3.3 contention honest limitation. md2pdf 변환.
3. **[★ T7] 발표 슬라이드 반영**: pgvector sf=10 dataset 일반화 결과 (정본 DEEP sf=10 + SIFT/SSN/WIKI/YFCC sf=10).
4. **[★ T11] v13 분석 재검증·재계산**: Codex C1 발견(§7.1) — `analyze_paper_exact.py`·`stats_poc_6_4.py`에 extended 파이프라인서 적용한 동일 fix(injection 필터·Type-I SS·CaseB 집계·paired 효과크기·index→key 페어링·NaN 분모) 보정 + finite Q-error 제외 편향 직접 검증 + v13 재집계 → 6/11 보고서 헤드라인 갱신. Claude+Codex 크로스체크.
5. **[6/11 보고서 개정]**: Codex C2(§7.2) + Gemini G1(§7.3)·G2(§7.4) findings 반영 — CaseB framing 정밀화·"equivalence" 과장 수정·수치 정합성·tone·고정비율 동기·CaseB 시너지.
6. **[다음 세션 — 사용자 명시] Gemini 웹앱 자동화**: Claude-in-Chrome MCP(macmini 브라우저, deviceId `644dba75-3349-4c8d-ba29-1507743d45a5`)로 gemini.google.com 구동 — 업로드·프롬프트·결과 회수 자동화 로직 구축. Claude Design은 토큰 한도로 보류.
7. **[다음 세션] Gemini로 미팅 최종 산출물**: 발표 슬라이드·보고서·미팅 내용(연구결과·pgvector 결과·6/11까지 일정·포스터 구성).
8. **[별도] repo hygiene**: Codex C3 11건(§7.5) — 루트 latency/ stale·CLAUDE.md 참조 정정·파일명 규칙·gitignore.

## 5. 산출물 경로 (본 세션 신규)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260521_230500_stats보정_멀티모델sweep.md` | 신규 |
| stats 파이프라인 보정 (2 파일) | `_internal/scripts/analyze_latency.py`·`stats_poc_6_4_extended.py` | 수정·**미커밋** |
| stats fix diff | `_internal/cache/rq3/multimodel_findings_20260521/stats_pipeline_fix.diff` | 신규 |
| 멀티모델 findings | `_internal/cache/rq3/multimodel_findings_20260521/` (codex C1/C2/C3/T4/T8 + gemini G1/G2/meeting) | 신규 |
| measure 스크립트 수정본 | server `cache/rq3/measure_4par_midnight.sh` (DEADLINE 22:00·sf=1 off) | 수정 (백업 `.bak_20260521_2207`) |
| auto_post daemon fix본 | `/tmp/auto_post_bc_4par.sh` (grep 버그 fix) | 수정 |
| AGENTS.md | `Capstone/AGENTS.md` → `CLAUDE.md` 심링크 | 신규 |
| 측정 raw (sf=10) | server·로컬 `cache/rq3/latency/phase4_extension/latency_*.json` | ✅ 33/48 cell (WIKI sf=10 honest exception) |
| ★ T5 산출물 | `_internal/cache/rq3/latency/poc_6_4_extended/` (summary.md + 9 CSV) · `experiments/figures/보고서_6_11/poc_6_4_extended/` | ✅ 신규 (04:04 KST) |

## 6. server·환경 상태

- **측정**: ✅ 완료 — sf=10 33/48 cell, 03:59 KST 종료. `phase4-4par` inactive. ★ 5/22 다른 분 서버 사용 — 측정 재개(sf=1·sf=100·WIKI 재시도·다중)는 협의 후.
- **로컬 daemon**: `auto_post_bc_4par` — T5 완료 후 역할 종료 (재기동 불필요).
- **접속**: `ssh capstone`. PG: `PGPASSWORD=wns41559 psql -h localhost -p 55435 -U wns41559 -d wns41559`.
- **권한**: 서버 6/11까지 · sudo 5/28 (임채림 연구원). 5/22 다른 분 서버 사용 — 측정은 sf=10 완결(~05:20) 후 종료라 충돌 회피.
- **멀티모델 CLI**: `codex` 0.132.0(맥미니 전용, gpt-5.5 xhigh) · `gemini` 0.42.0(`-m gemini-3.1-pro-preview`). Codex 헤비 동시실행은 순차.

## 7. ★ 멀티모델 검증 sweep — findings 상세 (다음 세션이 act)

원본 = `_internal/cache/rq3/multimodel_findings_20260521/`.

### 7.1 Codex C1 — v13 분석 스크립트 (`codex_C1_v13.json`) ★★ 중대

`analyze_paper_exact.py`(v13 헤드라인 산출)·`stats_poc_6_4.py`(§6.4 legacy) 10 finding. **헤드라인 89.1%·−4.38%·model3 0.00%를 그대로 신뢰하기 어렵다**:
- P0: finite Q-error만 비교 → inf/NaN(실패 케이스) 제외 → 89.1%·Δ% 과대평가 가능 (신규 — 직접 검증 필요) / model3 Type-III SS는 가산 분해 아님 / model3가 20-cell matched(cell 고정효과) 미보존.
- P1: CaseB pseudo-replication · exec_ms rep 독립관측 OLS · trial 페어링이 seed/id 아닌 JSON 순서 의존 · paired 설계에 unpaired 효과크기 공식 · NaN 분모 잔존 · 89.1%/−4.38% 산출 정의가 스크립트에 reproducible하게 안 잠김.
- ★ P1 다수 = Claude가 extended/analyze_latency에서 이미 검증·수정한 결함 클래스가 legacy에도 존재 (일관 = 신뢰). → **T11**.

### 7.2 Codex C2 — 6/11 보고서 (`codex_C2_report.json`)

9 finding — 보고서 핵심 주장 결함: CaseB framing(결합 추정기인데 "표본 선택 단계 하나"로 귀속) · "latency 동등성 확정" TOST 없이 과장 · 5.67× speedup oracle 기준인데 결합 성과처럼 읽힘 · N=385 "한 톨도 안 늘림" 주장 충돌 · 데이터셋 개수(5/8/9) 불일치 · carry-over cell 수(19/20·280/580) 불일치 · 식 2 카디널리티 추정식 재현 불가 · sf=10 행수(1M/8천만) 충돌.

### 7.3 Gemini G1 — narrative ↔ Exqutor 논문 (`gemini_G1_paper.log`)

narrative가 논문을 **정확히 대표 (왜곡 없음)**. 개선 2: ① 고정비율 카디널리티 추정 동기(pgvector 33.3%·VBASE 50%·DuckDB 100%)가 narrative 본문에 누락 → §0/§2 추가 ② CaseB 시너지 명시 — "논문=표본 크기(N) 동적 조정, 본 연구=표본 질(분포 대표성) 향상, 결합(CaseB)=동일 예산서 가장 안정적".

### 7.4 Gemini G2 + meeting-doc 리뷰 (`gemini_G2_report.log`·`gemini_meeting_review.log`)

- G2 (6/11 보고서): ① emotive 산문 톤다운("파탄난다"·"한 톨도"·"honest limitation"→"연구의 한계") ② §6.1 제안모델을 Ch5 엔진검증 발견과 연결 ③ §5.3-5.4에 "B1 58% vs 결합 94.9% 회복인데 왜 latency 동등?" 해석 1-2문장.
- meeting-doc 리뷰 (5/22 사전보고): ① §4.3 4엔진을 "generalizability 검증"으로 framing ② §6 4·5항 "(첨부 보고서 기준)" ③ §3.3 sf=100 censoring 예고 ④ jargon 순화 ⑤ §4.2 build script TMI 제거.

### 7.5 Codex C3 — repo hygiene (`codex_C3_hygiene.json`)

11 P1/P2 (데이터 오류 아님 — repo 정리): 루트 `latency/` stale figure · CLAUDE.md active 참조 불일치(deck PPTX·narrative가 실파일/archive와 어긋남) · 파일명 규칙 위반(HHMM·title 내부 날짜·phase·v 분기) · v13 금지룰 자기모순 · `.agents`/`.claude`/`.codex` gitignore 누락 · `_internal/server_backup` archive 미분리 · 한글 NFD/NFC 혼용.

## 8. ★ 환각 회피 룰 (carry + 본 세션 신규)

- **★ `pkill -f <pattern>` self-match 주의** — ssh로 보내는 블록 텍스트에 pattern 문자열이 있으면 `pkill -f`가 자기 셸을 죽임 (본 세션 measure 재기동 시 1회 사고 → 측정 일시 중단·복구). 프로세스 종료는 PID 기반 우선.
- **★ stats 파이프라인 보정본 미커밋** — `analyze_latency.py`·`stats_poc_6_4_extended.py` 수정은 검증·테스트 완료했으나 미커밋. daemon이 자정에 수정본으로 실행 — daemon 로그 확인 후 커밋 판단.
- **★ v13 헤드라인 수치 재계산 필요** — 89.1%·−4.38%·model3 0.00%은 Codex C1이 산출 로직 결함 지적. T11 전까지 "잠정"으로 취급.
- **★ measure latency layer = 4 condition** (baseline/B1/oracle/CaseB) — CaseA는 latency 측정에 없음. 오프라인 3-way와 layer 구분.
- **★ 측정 contention** — 4병렬 = 절대 latency ~10-15% inflation. within-cell paired는 강건. honest limitation.
- **★ measure 4병렬** (사용자 5/21 20:35 결정) — 정본 phase2는 sequential. 측정 조건 차이 honest limitation.
- carry: 비가역 작업(kill·rm) 사용자 명시 승인 후. KST 기준(server UTC +9h). 발표물 코드명(B1/CaseA/CaseB) 노출 금지·보고서 OK. "영역" 무의미 토큰 금지.

---

작성: 2026-05-21 23:05 KST · **5/22 08:55 KST 측정·T5 결과 갱신** (§3.2·§3.2.1·§4 task 1). 본 세션(stats 파이프라인 보정 + 멀티모델 검증 sweep + 측정 sf=10 연장·완료) 인계. **측정 33/48 cell 완료 → daemon T5 04:04 완료 — sf=10 dataset 일반화 확인 (SIFT/SSN/YFCC, WIKI honest exception).** → 다음 세션 = T6 미팅자료·T7 슬라이드(이미 나온 T5 결과 사용) + T11 v13 재검증 + 6/11 보고서 개정 + Gemini 웹앱 자동화 → 5/22 14:00 박광현 미팅.
