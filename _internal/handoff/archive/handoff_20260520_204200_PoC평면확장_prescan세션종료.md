# handoff 20260520 20:42 — PoC 평면 확장 prescan 단계 + 자문 메일 최신화 + 4 엔진 future work framing 확정

> 이전 handoff(`_internal/handoff/archive/handoff_20260520_185654_Phase6_PoC통계후속_실측.md`) → 본 문서. 이 문서 하나만 읽으면 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 세션(5/20 19:00~20:42)은 **PoC 평면 확장(handoff §4 task 8) 본격 실측 진입** — Phase A prescan 으로 DEEP sf=1 = PoC 무의미 확정 폐기, DEEP sf=100 prescan 33분+ (시간 risk 정량 확인, server background 진행 중, 다음 세션 회수), SIFT/SSN sf=10 prescan = sequential 대기. 사용자 결정으로 **4 엔진 통합 PoC = future work 정직 framing 확정 + Track B (Plan diff only) 폐기**. **자문 메일 (박성원 멘토님 3차) Phase 5 엔진 탑재 + Phase 6 PoC 결과 흡수 + 4 엔진 future work framing 으로 재구성**, 신규 본 `_202200.md/.pdf` (2 page · 278 KB · 미발송, 사용자 발송 대기). 직전 _185654 handoff anchor 그대로 carry (보고서 _171521 compact 15p 정본·PoC 1·2·3 phase2+phase3 결과 carry).

---

## 0. 가장 먼저 — 정본·진입점

- **★ 라우팅·구조 정본**: 루트 `CLAUDE.md`. anchor 본 handoff 로 갱신.
- **★ 보고서 신본 (정본 = compact 15p, carry 직전 세션)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.{md,pdf,docx}` — 15p · 1.60MB · §5.4 표 5-4·cluster bootstrap·§5.5 PoC bullet·§6.4 갱신 carry.
- **★ 보고서 readable 24p (carry)**: `..._171521_readable.pdf` (1.62MB · 내부 검토용).
- **★ 자문 메일 신규 본 (5/20 20:22 작성, 미발송)**: `submission/_drafts/속도는벡터_3차 자문요청_20260520_202200.md` + `.pdf` (2 page · 278 KB) — 박성원 멘토님 3차 자문, Phase 5/6 진행 흡수 + 자문 요청 3가지 재구성 + 4 엔진 future work framing. **사용자 발송 대기** (5/24 회신 일정).
- **★ 자문 메일 직전 본 (5/18, 미발송 → archive 이동)**: `submission/_drafts/archive/속도는벡터_3차 자문요청_20260518.{md,pdf}` (carry only, 본 세션 _202200 본으로 대체).
- **★ Phase 6 PoC 산출 (carry, 직전 세션)**: `_internal/scripts/stats_poc_6_4.py` (636 줄) + `_internal/cache/rq3/latency/poc_6_4/` (5 CSV + summary.md) + `experiments/figures/보고서_6_11/poc_6_4/` (2 figure pair).
- **★ 본 세션 plan file**: `~/.claude/plans/vectorized-stargazing-eagle.md` (Phase A prescan 검증 → Phase B 48 cell 측정 → Phase C analyze → Phase E 보고서 → Phase F close. **Track B 폐기**·**Phase A 진행 중**).
- **★ 본 세션 prescan 산출 (server 측, local 미회수)**:
  - server `/mnt/hdd0/home/capstone2026/cache/rq3/latency/phase4_prescan/`
    - `estimates_DEEP_sf1.parquet` (생성 15초 — 작은 테이블)
    - `estimates_DEEP_sf100.parquet` (생성 20분 — 큰 테이블 sampling 비싸다)
    - `estimates_SIFT_sf10.parquet` (생성 ~2분)
    - `estimates_SSN_sf10.parquet` (생성 ~3분)
    - `latency_tpc_h_q3_DEEP_sf1_sel0.001_qid0.json` (138 KB · ★ PoC 무의미 확정 — 모든 16 variant injection_fired=False, plan 동일, median 462-479ms variance ≈1%)
- **★ server background process** (본 세션 종료 후에도 자율 진행): pid 3587438 bash + 3587449 python3 `measure_latency_realengine.py --query q3 --dataset DEEP --sf 100 --sel 0.001 --query-id 0` (33분+ 진행 중, sf=100 1 cell ≈ 40-50 min 추정), 이어서 SIFT sf=10 → SSN sf=10 sequential. 다음 세션 시작 시 결과 회수.
- **★ 교수님 5/20 공지 정본 (carry)**: `_internal/state/캡스톤_교수님공지_20260520.md`.
- **★ 일정 정본 (carry)**: `_internal/state/_schedule.md`.
- **★ 직전 handoff (Phase 6 PoC 실측 — _171521 보고서 정본 source)**: `_internal/handoff/archive/handoff_20260520_185654_Phase6_PoC통계후속_실측.md` (archive 이동).
- **★ v3 polish prompt (carry, 토요일 일괄)**: `submission/_drafts/속도는벡터_발표deck_수정프롬프트_polish_20260520_144446.md` (archive 이동 — carry).
- **★ v2 PPTX (carry, 5/26 PPTX 마감·5/27+29 발표 base)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` (1.20MB, 21장 ship-ready).
- **★ 서버 backup (carry)**: `_internal/server_backup_20260520/` (2.6G · 22117 file).

## 1. 본 연구 framing (carry · 불변)

본 연구는 Exqutor 논문(arXiv:2512.09695v2) 재현이 아니라 **표본 선택(sample selection) 단계 하나**의 개입(무작위 Bernoulli → 분포 인지 stratification)이 추정 오차(Q-error)에 미치는 영향을 전 변인에 걸쳐 검증한 완전 실험 — 3-way matched B1(기존)·CaseA(완전 대체, 음성 대조군)·CaseB(결합, 산술평균). 발표물은 코드명(B1/CaseA/CaseB)·"영역" 필러·영어 메타 라벨·수식 노출 금지. 보고서는 코드명 사용 OK.

「엔진 적용 검증」 = 오프라인 검증된 카디널리티 추정치(13종 method 결합 = CaseB ×13)를 패치된 PostgreSQL(서버 55435)에 주입해 "추정치 → 실행 계획 → end-to-end latency" 고리를 닫는 실험. 4조건: 기본엔진(baseline) / 베이스라인(B1) / 결합(CaseB ×13) / 오라클(true_card). 측정 platform 정본 = phase2 (sel=0.001) 12 cell × 16 variant × 15 rep = 2,880 회 + phase3 (sel=0.01·0.1) carry-over 8 cell × 16 variant × 15 rep = 1,920 회 = 총 4,800 trial · 20 cell · 580 paired.

## 2. 본 세션(5/20 19:00~20:42)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| 직전 handoff (_185654) 정독 + 사용자 결정 (PoC 평면 확장) | ✅ | handoff_185654 흡수 + AskUserQuestion 으로 4 option (48 cell 전부·SIFT/SSN 우선·sf=1/sf=100 우선·prescan 1 cell 먼저) 중 **48 cell 전부** 결정 |
| 3 Explore 병렬 (Opus): server_backup 평면 inventory · 현재 raw + script 재사용 · 4 엔진 환경 | ✅ | 결론 = (a) server_backup 신규 raw 0건 (Q-error만), (b) measure_latency_realengine.py 단독 plan_signature 캡처 가능, (c) 4 엔진 24h 빌드 불가 (VBASE/DuckDB submodule 0B, build_custom 금지룰) |
| ultraplanning + ExitPlanMode 승인 | ✅ | plan file `~/.claude/plans/vectorized-stargazing-eagle.md` 작성 (Phase A~F) + 사용자 결정 (48 cell·Track B 후수행·§5.5 paragraph+표) 반영 |
| Phase A 진입 — TaskCreate 6 phase + server 환경 검증 + estimates 4 평면 생성 | ✅ | DEEP sf=1 estimates 15초 / SIFT sf=10 ~2분 / SSN sf=10 ~3분 / DEEP sf=100 **20분** (큰 테이블 sampling 비싸다 — 측정 시간 risk 정량 신호) |
| prescan 1 — DEEP sf=1 q3 sel=0.001 qid=0 측정 | ✅ | **★ 핵심 발견: PoC 무의미 확정** — 모든 16 variant injection_fired=False, plan 동일 (Gather Merge→Sort), median 462-479ms variance ≈1%. 작은 테이블이라 IndexScan 경로로 빠지고 SeqScan 분기 안 타서 injection mechanism 우회. 측정 2:29 |
| prescan 2/3/4 — DEEP sf=100/SIFT sf=10/SSN sf=10 q3 sel=0.001 qid=0 sequential background launch | 🔄 (server 자율 진행) | bash pid 3587438 + python pid 3587449 (DEEP sf=100 33분+ 진행 중, 다음 세션 회수). sf=100 1 cell ≈ 40-50 min 추정. SIFT/SSN ≈ 6 min each. **다음 세션 시작 시 server 결과 회수 + injection_fired 검증 + Track A 평면 확정** |
| 사용자 결정 (4 엔진 framing) | ✅ | "4 엔진 측정 내일까지 다 가능? 물리적 접근 제한 → pgvector 만 했고 향후 연구 확장 framing" 확정. **Track B (Plan diff only PoC) 폐기**, 보고서 §6.4 (3) 4 엔진 future work 정직 framing 만 |
| 자문 메일 (박성원 멘토님 3차) 최신화 | ✅ | 5/18 본 (archive carry, 미발송) base + Phase 5 엔진 탑재 (12 cell × 16 variant × 15 rep · 3-7배 가속 · 94.9% plan 회복 · latency 동등 분리) + Phase 6 PoC (plan-level g · cluster bootstrap · variance decomp model3 0.00% p=0.866) + Q9 sel=0.1 honest exception + 4 엔진 future work 정직 framing 흡수. 자문 요청 3가지 재구성 (메시지 framing · honest exception 위치 · 4 엔진 단일 한계 framing). 신규 본 `_202200.md/.pdf` (2 page · 278 KB), 사용자 발송 대기 |
| 종료 — handoff·archive·CLAUDE.md anchor·commit·push·맥북동기화 | (진행 중) | 본 file + 새세션 복붙 프롬프트 + 직전 _185654 archive + CLAUDE.md anchor + commit + push + gh run watch + rsync 맥북 |

## 3. ★★★ 본 세션 결과 — 다음 세션이 반드시 흡수할 정본

### 3.1 prescan 1 — DEEP sf=1 = PoC 무의미 확정 폐기

DEEP × sf=1 × q3 × sel=0.001 × qid=0 1 cell prescan (2:29 측정).

| variant | injection_fired | exec_ms_median | plan (top→children) |
|---|---|---|---|
| baseline | False (정상) | 470.5 | Gather Merge→[Sort] |
| B1 | **False (비정상)** | 471.7 | Gather Merge→[Sort] |
| oracle | **False (비정상)** | 473.3 | Gather Merge→[Sort] |
| CaseB × 13 method | **모두 False (비정상)** | 462-479 (variance ≈1%) | 모두 Gather Merge→[Sort] |

**원인**: measure_latency_realengine.py 헤더 주석 — "주입은 벡터 테이블이 pass-1 플랜에서 SeqScan 으로 접근될 때만 발동. pkey IndexScan 경로는 주입을 건너뛴다." sf=1 = 작은 테이블 → planner cost 가 IndexScan 또는 다른 path 가 저렴 → check_for_vector_search SeqScan 분기 안 타서 injection 우회.

**결론**: **DEEP sf=1 12 cell 측정 폐기**. PoC 1 (plan-level effect size) · PoC 2 (cluster bootstrap) · PoC 3 (variance decomposition) 모두 condition 효과 = 0 이므로 의미 없는 산출. 보고서 §5.5 또는 §6.4 에 "sf=1 은 plan-invariant — 작은 테이블 IndexScan 경로로 injection mechanism 우회됨 (honest exception)" 1 sentence carry 가능. 다음 세션 평면 = (sf=1 제외) SIFT sf=10 + SSN sf=10 + DEEP sf=100 부분 = **24 cell 또는 28 cell** 후보.

### 3.2 prescan 2/3/4 — sf=100/SIFT sf=10/SSN sf=10 진행 중 (server 자율)

DEEP sf=100 q3 sel=0.001 qid=0 33분+ 진행 → estimates 20분 비례 추정 measure ≈ 40-50 min. 12 cell sf=100 = 12 × 평균 80-100 min = **16-20 시간** (sel 가중 평균). 24h budget 안에서 **sf=100 전체는 부담**.

대안 (다음 세션 결정):
- **sf=100 sel=0.001 만 4 cell** (~3h) — 단일 sel scale 일반화 입증
- **sf=100 전체 폐기** — dataset 일반화만 (SIFT + SSN sf=10 = 24 cell)
- **sf=100 q3 만 3 sel** (~2h) — 단일 query × sel sweep

SIFT sf=10 / SSN sf=10 prescan = sf=100 끝나야 sequential 시작 (~6 min each).

### 3.3 사용자 결정 (5/20) — 4 엔진 framing 확정

**사용자 명시 의도**: "4 엔진 측정 내일까지 가능? 물리적 접근 제한 → pgvector 만 했고 향후 연구에서 다른 DB 확장 framing 이 맞다."

**확정 사항**:
- **Track B (Plan diff only PoC) 폐기** — `reference/exqutor_query_plans/` + paper Fig 12 fixed-ratio 정성 비교 PoC 도 굳이 안 함. 4 엔진 통합은 단순 future work framing 만.
- **보고서 §6.4 (3) 갱신** — 박광현 교수님 제안 "4 엔진 통합 PoC" 를 "future work — 본 연구는 pgvector 단독, VBASE/DuckDB 통합은 빌드 환경/시간 제약 (15-25h) 으로 별도 question 으로 분리" framing.
- **자문 메일에 명시** — 세 번째 자문 요청 "4 엔진 단일 한계 framing 의 학부 캡스톤 평가 수용성" 으로 박성원 멘토님 의견 요청.

### 3.4 자문 메일 (박성원 멘토님 3차) 최신화 — _202200 본

| 요소 | 내용 |
|---|---|
| 신규 file | `submission/_drafts/속도는벡터_3차 자문요청_20260520_202200.{md,pdf}` (2 page · 278 KB · md 11 KB) |
| 직전 본 (미발송, archive) | `submission/_drafts/archive/속도는벡터_3차 자문요청_20260518.{md,pdf}` |
| 수신자 | 박성원 멘토님 (1·2차 자문 동일 수신자, "멘토님" 호칭) |
| 연구 경과 추가 | Phase 5 엔진 탑재 (12 cell × 16 variant × 15 rep = 2,880 + carry-over 8 cell = 20 cell · 580 paired · 4,800 trial) + Phase 6 PoC 통계 후속 (plan-level g · cluster bootstrap · variance decomp model3 condition 0.00% p=0.866) + Q9 sel=0.1 honest exception + 4 엔진 future work framing |
| 자문 요청 1 (재구성) | 엔진 탑재 메시지 framing — "94.9% plan 회복 + latency 동등 분리" 가 학부 청중에게 설득력 있는지 |
| 자문 요청 2 (재구성) | Q9 sel=0.1 honest exception 위치 — limitation vs condition-of-effect |
| 자문 요청 3 (재구성) | 4 엔진 단일 한계 framing — 학부 평가 약점 vs 학술적 절제 |
| 일정 | 5/24 회신 / 5/27·29 발표 / 5/28 12:00 포스터 / 6/11 보고서 |
| 발송 상태 | **미발송 — 사용자 직접 발송 (다음 세션 또는 직접)** |

### 3.5 핵심 carry 정본 (직전 세션 _185654, 본 세션에서도 변경 X)

- 정본 17/17 + 교수님 12/12 + PoC 실측 (직전 세션) 그대로 carry
- 보고서 _171521 compact 15p · readable 24p
- PoC 1·2·3 (phase2+phase3 = 20 cell · 580 paired · 4,800 trial) summary.md
- plan_signature = Node Type pre-order 1-tuple
- B1 plan 회복 7/12 qid 의존 fragile
- CaseB > B1 latency 우열 없음 (model3 condition % SS = 0.00% p=0.866 정량 확정)
- Q9 sel=0.1 honest exception (plan ≠ baseline 인데 0.93× 감속)
- v2 PPTX ship-ready

## 4. ★ 다음 세션 task

1. **[★ 시급·session 시작 즉시] server 측 prescan 결과 회수**:
   - SSH 로 `ls -la /mnt/hdd0/home/capstone2026/cache/rq3/latency/phase4_prescan/*.json` — sf=100/SIFT sf=10/SSN sf=10 3개 cell 완료 여부 확인
   - 각 raw JSON inspect — `injection_fired=True` 확인 + plan_signature 정상 캡처 (jq · Node Type 키)
   - sf=100 1 cell 실제 측정 시간 (start/end log) 정량
2. **[★ Track A 평면 확정 — sf=100 risk 결정]**:
   - SIFT sf=10 + SSN sf=10 = 24 cell (확정 — 시간 ~5h)
   - DEEP sf=100 → 사용자 결정 옵션: (a) 전체 12 cell (~16-20h, 24h budget 위험), (b) sel=0.001 만 4 cell (~3h), (c) q3 만 3 sel (~2h), (d) 폐기
   - AskUserQuestion 으로 사용자 결정 받기 (prescan 실측 시간 base)
3. **[★ Phase B 본격 측정 launch]**:
   - phase4_extension/{SIFT_sf10,SSN_sf10,DEEP_sf100_부분} 디렉토리 server 생성
   - measure_latency_realengine.py launch (sel=0.001 → 0.01 → 0.1 order, background, Monitor)
   - 5/21 (수) 서버 권한 종료 cutoff 안 cutoff 안 안전 margin 확보
4. **[Phase C — analyze + PoC 재실행]**:
   - 측정 완료 후 local 로 raw JSON rsync (작은 파일, 빠름)
   - local `analyze_latency.py --input phase4_*/` 로 각 평면 paired_stats.csv 생성
   - 신규 `stats_poc_6_4_extended.py` 작성 (legacy 카피 + PHASE_DIRS 확장 + 평면 일반화 비교 표 함수) → PoC 1·2·3 재실행 → `_internal/cache/rq3/latency/poc_6_4_extended/`
   - 평면 간 condition % SS / mean |g| / large % 비교 표 산출
5. **[Phase E — 보고서 §5.5 갱신 + PDF 재빌드]**:
   - §5.5 마지막에 신규 paragraph + 표 1개 (5 평면 비교 + sf=1 plan-invariant honest exception 언급)
   - §6.4 (3) 4 엔진 future work framing 정리 (Track B 폐기 반영)
   - md2pdf compact + readable 재빌드 (compact ≤ 22p 학교 양식 충족 확인)
6. **[Phase F — Close]**:
   - 신규 handoff + 새세션 복붙 프롬프트
   - 직전 _204200 archive
   - CLAUDE.md anchor 갱신
   - commit + push + gh run watch + 맥북 sync
7. **[★ 사용자 직접 — 자문 메일 발송]**:
   - `submission/_drafts/속도는벡터_3차 자문요청_20260520_202200.pdf` 박성원 멘토님께 메일 발송
   - 본문 = md 본 복사 또는 PDF 첨부
   - 회신 5/24경 base (5/27·29 발표 반영)
8. **[★ 5/22 박광현 교수님 미팅] — 사전보고 자료 carry**:
   - 보고서 _171521 compact 15p (정본 carry)
   - PoC 1·2·3 결과 (carry summary.md)
   - prescan 결과 (sf=1 폐기·sf=100 시간 risk·SIFT/SSN sf=10 추가 측정) 진행 상황 공유
   - 4 엔진 future work framing 사전 안내
9. **[5/25 팀원 검토 + 5/26 11:59 PM PPTX Learnus + 5/27+5/29 발표 + 5/28 12:00 포스터 + 6/5 전시회 + 6/10 박광현 마지막 세미나 + 6/11 보고서·상호평가]** — carry 일정

## 5. 서버 접속·실행 (★ 5/21 권한 종료)

- 접속: `ssh capstone` (165.132.140.240). PG: `PGPASSWORD=wns41559 psql -h localhost -p 55435 -U wns41559 -d wns41559`.
- ⚠️ **`build_custom.sh`/`apply_patch.sh` 절대 금지** carry.
- ★ **서버 권한 5/21 (수) 까지** — 본 세션이 prescan + 측정 1 cell (DEEP sf=1) 추가. 본 세션 종료 후에도 server bash pid 3587438 + python pid 3587449 sequential 진행 중. 다음 세션 시작 시 결과 회수 + Phase B 본격 측정 launch.
- 서버 prescan 데이터 위치: `/mnt/hdd0/home/capstone2026/cache/rq3/latency/phase4_prescan/` (4 estimates parquet + 1 raw JSON + 측정 진행 중 추가 raw JSON).
- 측정 raw JSON local 회수 패턴 (Phase C 직전): `rsync -avz capstone:/mnt/hdd0/home/capstone2026/cache/rq3/latency/phase4_*/ _internal/cache/rq3/latency/`

## 6. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| **★ 자문 메일 신규 본 (5/20 20:22, 미발송)** | `submission/_drafts/속도는벡터_3차 자문요청_20260520_202200.{md,pdf}` | 신규 (11 KB md / 2 page 278 KB pdf) |
| 자문 메일 직전 본 (5/18, 미발송, archive) | `submission/_drafts/archive/속도는벡터_3차 자문요청_20260518.{md,pdf}` | archive (carry) |
| ★ 본 세션 plan file | `~/.claude/plans/vectorized-stargazing-eagle.md` | 신규 (Track B 폐기·Phase A 진행 중 상태 반영) |
| **★ 본 세션 prescan (server 측, local 미회수)** | server `/mnt/hdd0/home/capstone2026/cache/rq3/latency/phase4_prescan/` | server only (estimates 4 + raw 1 + 측정 진행 중) |
| ★ 보고서 신본 _171521 (compact 15p · readable 24p) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.{md,pdf,docx,readable.pdf}` | carry (직전 세션 정본) |
| Phase 6 PoC 산출 5 CSV + summary | `_internal/cache/rq3/latency/poc_6_4/` | carry |
| Phase 6 PoC 2 figure pair | `experiments/figures/보고서_6_11/poc_6_4/` | carry |
| stats_poc_6_4.py (636 줄) | `_internal/scripts/stats_poc_6_4.py` | carry |
| md2pdf.py + md2pdf_readable.py (filename fix) | `_internal/scripts/` | carry |
| analyze_latency.py (figure 한글 폰트 + paired stats) | `_internal/scripts/analyze_latency.py` | carry |
| measure_latency_realengine.py · gen_latency_estimates.py | `_internal/scripts/` + server `cache/rq3/` | carry |
| 일정 정본 + 교수님 공지 (carry) | `_internal/state/{_schedule.md,캡스톤_교수님공지_20260520.md}` | carry |
| v2 PPTX ship-ready (carry) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` | carry (1.20MB · 21장) |
| v3 polish prompt (carry) | `submission/_drafts/archive/속도는벡터_발표deck_수정프롬프트_polish_20260520_144446.md` | archive carry |
| 서버 backup (carry) | `_internal/server_backup_20260520/` | carry (2.6G · 22117 file) |
| archive 이동 (본 세션 + 누적) | `_internal/handoff/archive/handoff_20260520_185654_*` + `새세션_복붙_프롬프트_20260520_185654.md` | 이동 (본 세션) |

CLAUDE.md anchor 갱신: 본 handoff (`handoff_20260520_204200_PoC평면확장_prescan세션종료.md`) + 자문 메일 _202200 본.

## 7. carry-forward / 보류 / 미커밋 (본 세션 직후)

- **★ 본 세션 commit 대상**:
  - `submission/_drafts/속도는벡터_3차 자문요청_20260520_202200.{md,pdf}` (신규 — 자문 메일)
  - `submission/_drafts/속도는벡터_3차 자문요청_20260518.pdf` (활성에서 archive 이동)
  - `submission/_drafts/archive/속도는벡터_3차 자문요청_20260518.{md,pdf}` (archive 신규 — git untracked)
  - 활성 → archive 이동 일괄 (보고서 timecode 본들 _124200·_144446·_162500·_171521_readable / 발표 deck prompt / 포스터·팜플렛·소개영상 prompt / PPTX 등 ~20건 — rsync 결과로 활성에서 deleted + archive 에 untracked)
  - `_internal/handoff/active/handoff_20260520_204200_*.md` (신규 — 본 handoff)
  - `_internal/handoff/active/새세션_복붙_프롬프트_20260520_204200.md` (신규)
  - `_internal/handoff/archive/handoff_20260520_185654_*` (이동)
  - `CLAUDE.md` (anchor 갱신)
- **★ git push + gh run watch** (사용자 명시 동의)
- **★ 맥북 sync** (rsync push macbook)
- **★ 본 세션 server background 진행** (sf=100 prescan + SIFT/SSN sequential): 본 PC 세션 종료해도 server pid 3587438/3587449 자율 진행. 다음 세션이 결과 회수.
- **메모리 갱신** (별도)

## 8. ★ 환각 회피 룰 (carry, 본 세션 신규 추가)

- 정본 수치 정합 = `_internal/cache/rq3/latency/{phase2,phase3}/figures/paired_stats.csv` (15 컬럼) + 보고서 §5.4 표 5-3·5-4 + §5.5 PoC bullet + figure 5-5 (carry) + PoC fig `fig_plan_level_g`·`fig_variance_decomp`.
- **B1 plan 회복은 qid 의존 fragile (7/12)** carry — qid=0 만으로 generalize 금지.
- **CaseB > B1 latency 측면 우열은 없음** carry — model3 condition % SS = 0.00% (p=0.866) 정량 확정.
- **Q12 qid 0 large effect (g ≈ −1.5)** carry.
- **core 4 cell sel=0.001 한정 → phase3 carry-over sel=0.01·0.1** carry.
- **plan_signature 정의 = Node Type pre-order 1-tuple** carry.
- **q9 sel=0.1 honest exception** carry (plan ≠ baseline 인데 speedup < 1.0 (0.93×)).
- **교수님 공지 (carry)**: 전시회 6/5 금 / 발표 5/27+5/29 양일 / 자료 PPTX 5/26 11:59 PM Learnus / 포스터 5/28 12:00 정오 / 무단결석 0점 / 가산점=질문.
- **PoC 평면 (carry)** = phase2+phase3 = 20 cell · 580 paired · 4,800 trial.
- **plan-level effect size 분층 (carry)**: plan 회복 True 그룹 large 5.4% vs False 그룹 26.3% (5배 차이).
- **md2pdf_readable.py output fix (carry)**: `_readable.pdf` 분리 출력.
- **★ 본 세션 신규 carry — DEEP sf=1 = PoC 무의미 확정**: 모든 16 variant injection_fired=False, plan 동일 (Gather Merge→Sort), median variance ≈1%. sf=1 작은 테이블 IndexScan 경로로 SeqScan 분기 안 타서 injection mechanism 우회. **PoC 평면 확장에서 sf=1 폐기**.
- **★ 본 세션 신규 carry — sf=100 시간 risk 정량**: estimates 20분, 측정 추정 40-50 min/cell, 12 cell × 평균 80-100 min ≈ 16-20h. 24h budget 안에 부분 측정 (sel=0.001 만 4 cell 또는 q3 만 3 sel) 권장.
- **★ 본 세션 신규 carry — 4 엔진 통합 PoC = future work 정직 framing 확정**: pgvector 단독, VBASE/DuckDB 빌드 15-25h vs 5/21 권한 종료. 본 연구 범위 밖. Track B (Plan diff only) 도 폐기 확정.
- **★ 본 세션 신규 carry — 자문 메일 _202200 본**: 박성원 멘토님 3차 자문, Phase 5/6 진행 흡수 + 자문 요청 3가지 재구성. 5/18 본 (archive carry) 미발송이라 본 세션 본으로 대체. **사용자 발송 대기** (5/24 회신 일정).
- 보고서 코드명(B1/CaseA/CaseB) 사용 OK / 발표물 코드명 노출 금지 — v2 검증 결과 0건 carry.
- v2 = raster image PPTX carry — v3 polish 도 raster image PPTX 형식 예상.

---

작성: 2026-05-20 20:42 KST — 본 세션 (PoC 평면 확장 Phase A prescan + 자문 메일 _202200 최신화 + 4 엔진 future work framing 확정) 종료. **핵심 = (1) DEEP sf=1 PoC 무의미 폐기, (2) DEEP sf=100 시간 risk 정량 (server background 진행 중, 다음 세션 회수), (3) Track B 폐기, (4) 자문 메일 사용자 발송 대기**. → 다음 = server prescan 결과 회수 + Track A 평면 확정 (사용자 결정) + Phase B 측정 launch + 5/22 박광현 미팅 + 5/24 자문 회신 + 5/26 PPTX + 5/27+29 발표 + 5/28 12:00 포스터 + 6/5 전시회 + 6/10 박광현 마지막 세미나 + 6/11 보고서·상호평가.

---

## ★ 5/21 00:00 carry update (다음 세션 — pgvector 평면 확장 본격 launch)

본 handoff 의 일부 carry 가 5/20 22:00 이후 사용자 결정으로 변경됨:

1. **자문 메일 _202200**: ~~미발송·사용자 발송 대기~~ → **5/20 22:34 박세은 발송 완료** (보고서/슬라이드/포스터/팜플렛/표지 첨부, 5/24 회신 base).

2. **4 엔진 통합 PoC framing**: ~~future work 정직 framing~~ → **본격 실측 진행** (사용자 5/20 22:53/23:54 명시). 단 순서 = (1) pgvector 완전 (측정+분석+자료) → (2) 4 엔진 빌드/측정. 5/27 발표 = pgvector 단독, 6/11 보고서 = pgvector + 4 엔진 통합.

3. **DEEP sf=100 1 cell**: ~~12h hang~~ → 자연 종료. Phase B/C 평면 확장 launch.

4. **측정 매트릭스**: RQ3 v13 1508 수준 — 단일 5종 (DEEP/SIFT/SSN/WIKI/YFCC) + 다중 2종 (DEEP+SIFT/DEEP+WIKI sf=10) × sf 1/10/100 × 4 q × 3 sel = 160 신규 cell × 4 엔진. 자원 cap (systemd-run MemoryMax=50G × 4 병렬·watchdog 5min) 양보 정책 적용.

5. **권한 연장**: ~~5/21 cutoff~~ → **6/11 까지 박세은 5/20 23:46 카톡 발송** (5/21 응답 base).

6. **신규 plan**: `~/.claude/plans/mossy-fluttering-hennessy.md` (ExitPlanMode 5/20 23:38 승인, framing 단순화 + 자원 4 병렬 적극 + 6/11 권한 base).

7. **신규 측정·빌드 산출 (5/21 00:00 시점 진행 중)**:
   - `latency/phase4_extension/` (server, estimates 진행 중 ~5/21 01:20 ETA)
   - `launch_phase4_measure.sh` (B2/B3/C/B4 wrap, 4 병렬·sf=100 2 병렬)
   - `auto_launch_b2_after_b1.sh` (B1 종료 → B/C sequential auto-launch daemon)
   - `resource_watchdog.sh` (5min 주기 SIGSTOP/SIGCONT daemon)
   - `measure_latency_realengine.py` + `gen_latency_estimates.py` 9 dataset 확장 (md5 동기화)

본 _204200 본은 5/21 신규 handoff 생성 시 archive 이동 예정.
