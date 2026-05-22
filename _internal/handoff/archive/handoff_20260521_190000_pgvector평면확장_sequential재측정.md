# handoff 20260521 19:00 — pgvector 평면 확장 sequential 재측정 + DuckDB-vss 빌드 완료 + 자정 종료

> 이전 handoff(`_internal/handoff/active/handoff_20260520_204200_PoC평면확장_prescan세션종료.md`) → 본 문서. 이 문서 하나로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 세션(5/20 22:43~5/21 19:00)은 **PoC 평면 확장 본격 진행** — 사용자 결정으로 4 엔진 (Exqutor 논문 3 + Milvus) × RQ3 매트릭스 측정 plan 승인. 자원 watchdog v4 (free≥256GB·our_rss≤512GB·5초 주기) 구축, codex finding #1 (est_b1 2-stage→1-stage fix) 반영해 estimates 13 file 전수 재생성, **measure 4 병렬 → sequential 전환** (latency 격리 — 정본 phase2 와 동일 조건), **DuckDB-vss 빌드 완료** (binary + smoke ✓). 임채림 연구원 회신 = 서버 6/11까지·sudo 5/28. **5/21 자정에 measure+build 자동 종료** (5/22 다른 분 서버 사용). → 다음 세션 = 자정 측정분 로컬 회수 + 분석 + 최종발표 슬라이드 반영 → 5/22 14:00 박광현 미팅.

---

## 0. 가장 먼저 — 정본·진입점

- **★ 라우팅·구조 정본**: 루트 `CLAUDE.md` — anchor 본 handoff 로 갱신.
- **★ 본 세션 plan**: `~/.claude/plans/mossy-fluttering-hennessy.md` — 4 엔진 × RQ3 매트릭스 plan (ExitPlanMode 5/20 23:38 승인 + 다회 carry update).
- **★ 직전 handoff (carry)**: `_internal/handoff/active/handoff_20260520_204200_PoC평면확장_prescan세션종료.md` — 본 세션 종료 시 archive 이동.
- **★ 보고서 정본 (carry)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.{md,pdf}` (compact 15p).
- **★ 5/22 박광현 미팅 사전보고 (본 세션 신규)**: `submission/_drafts/속도는벡터_5_22_박광현미팅_사전보고_20260520_2355.md` (136줄 — §3.3 표에 측정 결과 placeholder, 다음 세션이 채움).
- **★ 자문 메일 (박성원 멘토님 3차) — 5/20 22:34 박세은 발송 완료**: `submission/_drafts/속도는벡터_3차 자문요청_20260520_202200.pdf`.

## 1. 본 연구 framing (carry · 불변)

본 연구 = Exqutor 논문(arXiv:2512.09695v2) 의 표본 선택 단계 하나 (무작위 Bernoulli → 분포 인지 stratification) 개입의 효과를 전 변인에 걸쳐 검증. 3-way matched (B1 대조군·CaseA 완전 대체 음성 대조군·CaseB 결합 `(est_b1+est_method)/2`).

「엔진 적용 검증」 = 오프라인 검증된 카디널리티 추정치를 patched PostgreSQL(55435)에 주입 → "추정치 → 실행 계획 → end-to-end latency" 측정. RQ3 v13 오프라인 = 1508 측정 (89.1% better·중앙값 −4.38%). Phase 5 엔진 탑재 정본 = DEEP sf=10 20 cell·580 paired·4,800 trial (3-7× 가속·94.9% plan 회복·model3 condition 0.00% p=0.866).

**★ PoC 평면 확장 (본 세션 본격 진행)**: 정본 DEEP sf=10 단일 평면 → 단일 5종 (DEEP/SIFT/SSN/WIKI/YFCC) + sf 1/10/100 + 4 엔진 (pgvector·DuckDB-vss·VBASE·Milvus) 일반화. **4 엔진 = Exqutor 논문 통합 3 엔진 (pgvector·VBASE·DuckDB) 재현 + Milvus (대표 벡터 DB) 추가** (논문 자체는 3 엔진).

## 2. 본 세션(5/20 22:43~5/21 19:00)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| 사용자 결정 — PoC 평면 확장 본격 | ✅ | "4 엔진 + 모든 데이터셋·sf·sel 매트릭스 측정" (5/20 22:53) + "pgvector 완전 후 4 엔진" 순서 (5/20 23:54) |
| ultraplanning + ExitPlanMode 승인 | ✅ | plan `mossy-fluttering-hennessy.md` (3회 재작성 — 자원 점유·timeline·fail-safe 정교화 후 승인) |
| 자원 watchdog v4 구축 | ✅ | systemd service `capstone-watchdog` (Restart=always·5초 주기) — free<256GB OR our_rss>512GB OR other_cpu>6400% OR load>80 시 measure/build SIGSTOP |
| codex finding #1 — est_b1 2-stage cache | ✅ | `gen_latency_estimates.py` est_b1 = `bernoulli_estimate(..., all_vecs=all_vecs)` 1-stage fix (codex 교차검증 ✓). 2-stage 산출물 backup + estimates 13 file 전수 재생성 |
| measure 4 병렬 → sequential 전환 | ✅ | ★ 정본 phase2 = sequential 측정 (raw mtime 6-11분 순차) 확인 → 4 병렬 = latency contention 오염 → sequential 재측정. 4 병렬 측정값 64개 폐기 (backup) |
| DuckDB-vss 빌드 | ✅ 완료 | `Exqutor/DuckDB/duckdb-vss/build/release/duckdb` (40MB) + `vss.duckdb_extension` + smoke `SELECT 1`→1 ✓. ninja 562/562. sudo 불필요 (빌드 도구 다 구비) |
| 임채림 연구원 권한 회신 | ✅ | 서버 6/11까지 OK · sudo 권한 5/28 설정 후 메일 (5/28까지 연구실 실험) |
| 5/22 미팅 사전보고 자료 | ✅ | `속도는벡터_5_22_박광현미팅_사전보고_20260520_2355.md` (placeholder = 측정 결과 자리) |
| 자정 종료 설정 | ✅ | midnight-stop.timer (5/22 00:00 KST = UTC 15:00 — measure+build stop). 5/22 다른 분 서버 사용 |
| measure sf=10 sequential 진행 | 🔄 자정까지 | `phase4-midnight` service — sf=10 우선 (SIFT/YFCC/SSN/WIKI × q3/q9/q10/q12 × sel) 1 cell ~9분 |

## 3. ★★★ 핵심 결과 — 다음 세션이 흡수할 정본

### 3.1 estimates 13 file 1-stage 재생성 완료

`cache/rq3/latency/phase4_extension/estimates_{DEEP,SIFT,SSN,WIKI,YFCC}_sf{1,10,100}.parquet` — 단일 5종 × sf (WIKI/YFCC sf=100 미적재 제외) = **13 file**. **est_b1 1-stage** (codex finding #1 fix 반영, all_vecs 직접 random sample). 2-stage 본은 `phase4_extension_2stage_backup/`.

### 3.2 measure sequential 진행 (자정 종료)

- **sf=10 우선** (`measure_seq_midnight.sh`): SIFT→YFCC→SSN→WIKI × q3/q9/q10/q12 × sel 0.001→0.01→0.1. DEEP sf=10 은 정본 phase2 carry — 제외.
- 1 cell ≈ **9분** (SIFT sf=10 sel=0.001 실측). sel=0.01/0.1 더 김. WIKI sf=10 = dim 768 매우 느림 (plan capture statement_timeout 도달 빈번).
- 자정 (5/22 00:00 KST) 까지 ~5h → **sf=10 약 25-35 cell 측정 예상** (sel=0.001 위주 + sel=0.01 일부).
- sf=1 (plan-invariant 우려·작은 테이블 injection 우회) = 후순위. sf=100 (1 cell 30분+) = 자정 제약상 미측정.

### 3.3 DuckDB-vss 빌드 완료

`Exqutor/DuckDB/duckdb-vss/build/release/duckdb` (binary 40MB) + `extension/vss/vss.duckdb_extension`. smoke `INSTALL vss; LOAD vss; SELECT 1;` → `1` ✓. **4 엔진 중 2번째 (pgvector + DuckDB-vss) 빌드 완료**.

### 3.4 carry 정본 (직전 세션 그대로)

- 보고서 _171521 compact 15p · PoC 1·2·3 (DEEP sf=10 20 cell) · 3-7× · 94.9% plan 회복 (148/156) · 13/168 plan-saturated · 89.1% · 중앙값 −4.38% · model3 condition 0.00% p=0.866 · plan_signature 1-tuple · Q9 sel=0.1 honest exception · v2 PPTX ship-ready.

## 4. ★ 다음 세션 task (5/22 미팅 대비)

1. **[★ 즉시] server measure 자정 종료 + 로컬 데이터 회수 확인**:
   - `ssh capstone 'systemctl --user is-active phase4-midnight'` (inactive 면 자정 종료 완료)
   - `ssh capstone 'ls cache/rq3/latency/phase4_extension/latency_*.json | wc -l'` — sf=10 측정 cell 수
   - local `auto_post_bc_midnight` daemon (`/tmp/auto_post_bc_midnight.sh`) 이 measure 종료 감지 → rsync + analyze + stats 자동 실행. log = `_internal/cache/rq3/latency/phase4_extension/auto_post_bc_1stage.log`. 실행 됐는지 확인, 안 됐으면 수동:
     - `rsync -avz capstone:/mnt/hdd0/home/capstone2026/cache/rq3/latency/phase4_extension/ _internal/cache/rq3/latency/phase4_extension/`
     - `python3 _internal/scripts/analyze_latency.py --input _internal/cache/rq3/latency/phase4_extension`
     - `python3 _internal/scripts/stats_poc_6_4_extended.py`
2. **[★ 분석] pgvector 평면 확장 결과 정리**:
   - sf=10 측정 cell 의 injection_fired·plan 회복·condition % SS·Hedges' g — dataset 별 (SIFT/SSN/WIKI/YFCC) vs 정본 DEEP sf=10 비교
   - est_b1 1-stage vs 2-stage 비교 — `est_b1_compare.csv` (est-b1-compare daemon 산출, 또는 `compare_est_b1.py` 실행)
   - WIKI sf=10 honest exception (dim 768 query 느림 — plan capture timeout 빈번)
3. **[★ 최종발표 슬라이드 반영]**: pgvector 평면 확장 결과 (dataset 일반화) → 발표 슬라이드. framing = "정본 DEEP sf=10 외 SIFT/SSN/YFCC/WIKI sf=10 측정 → dataset 일반화 검증".
4. **[★ 5/22 미팅 자료]**: `속도는벡터_5_22_박광현미팅_사전보고_20260520_2355.md` §3.3 placeholder 채움 + md2pdf 변환. 미팅 14:00 — pgvector 평면 확장 결과 + 4 엔진 계획 보고.
5. **[5/28 이후] VBASE + Milvus 빌드**: sudo 권한 (임채림 5/28 메일) 후 `build_4engine.sh vbase` / Milvus. VBASE = PG dev 패키지 7개 (sudo apt install), Milvus = go/etcd/minio (sudo).
6. **[측정 재개]**: 5/22 다른 분 서버 사용 → 5/23+ 측정 재개. sf=1·sf=100·VBASE/DuckDB/Milvus 매트릭스. **measure 는 반드시 sequential** (latency 격리).

## 5. 산출물 경로 (본 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 세션 plan | `~/.claude/plans/mossy-fluttering-hennessy.md` | 신규 |
| ★ 5/22 미팅 사전보고 | `submission/_drafts/속도는벡터_5_22_박광현미팅_사전보고_20260520_2355.md` | 신규 (placeholder) |
| ★ estimates 13 file (1-stage) | server `cache/rq3/latency/phase4_extension/estimates_*.parquet` | 신규 |
| ★ measure raw JSON (sf=10) | server `cache/rq3/latency/phase4_extension/latency_*.json` | 자정까지 진행 |
| ★ DuckDB-vss binary | server `Exqutor/DuckDB/duckdb-vss/build/release/duckdb` | 신규 빌드 ✓ |
| gen_latency_estimates.py (1-stage fix) | `_internal/scripts/gen_latency_estimates.py` (+ server 동기화) | 신규 |
| measure_latency_realengine.py (9 dataset·timeout 180s·work_mem) | `_internal/scripts/measure_latency_realengine.py` (+ server) | 신규 |
| stats_poc_6_4_extended.py (1254줄) | `_internal/scripts/stats_poc_6_4_extended.py` | 신규 (agent 작성) |
| build_4engine.sh (750줄) | server `cache/rq3/build_4engine.sh` + `_internal/scripts/server_build/` | 신규 |
| measure_seq_midnight.sh | server `cache/rq3/measure_seq_midnight.sh` + `_internal/scripts/server_build/` | 신규 |
| resource_watchdog v4 | server `resource_watchdog.sh` + `_internal/scripts/server_build/resource_watchdog_v3.sh` | 신규 |
| compare_est_b1.py | server `cache/rq3/compare_est_b1.py` + `_internal/scripts/server_build/` | 신규 |
| 2-stage 측정값 backup | server `cache/rq3/latency/phase4_extension_2stage_backup/` (105) + `_4par_backup/` (64) | backup |
| 보고서 _171521 (carry) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.*` | carry |
| 자문 메일 _202200 (5/20 발송) | `submission/_drafts/속도는벡터_3차 자문요청_20260520_202200.pdf` | carry |

## 6. server 측 상태 (다음 세션 시작 시 확인)

- **자정 (5/22 00:00 KST) 자동 종료**: `midnight-stop.timer` → `phase4-midnight` (measure) + `duckdb-build` stop. 22일 측정 X.
- **systemd --user units**: `capstone-watchdog` (watchdog v4, 계속 유지 OK — 부담 0) / `phase4-midnight` (measure, 자정 stop) / `est-b1-compare` (estimates 비교 daemon).
- **local daemon**: `auto_post_bc_midnight` (`/tmp/auto_post_bc_midnight.sh`) — measure 종료 감지 → rsync + analyze + stats.
- **접속**: `ssh capstone`. PG: `PGPASSWORD=wns41559 psql -h localhost -p 55435 -U wns41559 -d wns41559`.
- **권한**: 6/11까지. sudo = 5/28 (임채림 메일).

## 7. ★ 환각 회피 룰 (carry + 본 세션 신규)

- **★ measure 는 sequential 필수** — 정본 phase2 가 sequential (raw mtime 6-11분 순차). 4 병렬 = latency contention 오염. estimates 생성만 4 병렬 OK (CPU 계산).
- **★ est_b1 = 1-stage** — codex finding #1. `bernoulli_estimate(all_vecs=...)`. 2-stage (cluster 500 cap) 는 큰 cluster 과소대표 (corr −0.98). 평면 확장 estimates 13 = 1-stage 재생성본.
- **★ Exqutor 논문 = 3 엔진** (pgvector·VBASE·DuckDB). Milvus 는 논문 밖 (대표 벡터 DB 추가). "4 엔진" = 3 재현 + Milvus.
- **★ multi sf=10 honest exception** — partsupp_deep_sift/wiki_10 의 ps_embedding 컬럼 분리 (deep+sift/wiki 별도) → measure harness 불일치. multi 측정 보류 (concat view/GENERATED 검토).
- **★ DEEP sf=1 plan-invariant** carry — 작은 테이블 IndexScan injection 우회. sf=1 = plan-invariant 우려.
- **★ WIKI sf=10 dim 768** — query 느림, plan capture statement_timeout(180s) 도달 빈번. honest exception 후보.
- **★ 자원 룰** — free RAM ≥ 256GB·우리 측 ≤ 512GB (watchdog v4 강제). sf=100 측정 3 병렬 (단 measure 는 sequential 이라 사실상 1). 8 병렬 sf=100 = 서버 멈춤 사고 (carry).
- 측정 정본 carry: 89.1%·−4.38%·94.9%·148/156·13/168·model3 0.00% p=0.866·plan_signature 1-tuple·Q9 honest exception.
- 발표물 코드명 (B1/CaseA/CaseB) 노출 금지 / 보고서 OK. "영역" 무의미 토큰 금지.
- 비가역 작업 (kill·rm) 사용자 명시 승인 후. KST 기준 시간 (server 는 UTC — +9h).

## 8. ★ 5/21 20:40 carry update (본 세션 추가 결정 — handoff 갱신)

본 handoff 작성(19:00) 후 사용자 추가 결정:

1. **measure 4 병렬 재개** (사용자 5/21 20:35) — §7 의 "measure sequential 필수" 정정. sf=10 = 테이블 12-21GB → server free 894GB OS page cache 캐싱 + 128 core 여유 → 4 query 동시여도 CPU bound 라 contention 작을 것으로 판단. `measure_4par_midnight.sh` (sf=10 4 병렬, 자정 deadline) — `phase4-4par` service. **단 정본 phase2(DEEP sf=10)는 sequential 측정 — 측정 조건 차이는 honest limitation**.
2. **sequential 12 cell backup** — `latency/phase4_extension_seq_backup/` (sequential 측정분, 다음 세션 Codex/Gemini 가 sequential vs 4 병렬 latency 비교 → contention 정량 검증용).
3. **watchdog v5** — our_rss 512 cap 제거 (사용자 "256기가만 남기고 512 말고"). server free RAM ≥ 256GB 기준만. measure 는 메모리 무관 (our_rss=0~2GB 입증).
4. **자정 종료** — `midnight-stop.timer` 가 `phase4-4par`+`duckdb-build` 5/22 00:00 KST(UTC 15:00) stop. local daemon = `auto_post_bc_4par` (phase4-4par 감지 → rsync+analyze+stats).
5. **★ 다음 세션 = 본 세션 후속·연장 + 추가 검증** (사용자 5/21 20:35):
   - (a) 자정 4 병렬 측정분 로컬 회수 + 분석 + 최종발표 슬라이드 반영 (§4 task 1~4)
   - (b) **Codex/Gemini 교차검증** — 측정 정합성·잘못 측정된 cell 없는지 (multi-model `~/.claude/rules/multi-model.md`). 특히 4 병렬 contention 영향 = `phase4_extension_seq_backup/` (sequential) vs 4 병렬 동일 cell latency 비교.
   - (c) 3 에이전트 병렬 검증 + 추가 모니터링
   - (d) measure 진행 모니터링 (자정 종료 확인)

§7 환각 회피 룰 정정: "measure sequential 필수" → "**measure 5/21 20:35 사용자 결정으로 sf=10 4 병렬 재개**. 정본 phase2 는 sequential — 측정 조건 차이 honest limitation. 다음 세션 Codex/Gemini 가 contention 정량 검증 (sequential 12 cell backup vs 4 병렬 비교)".

---

작성: 2026-05-21 19:00 KST (20:40 carry update) — 본 세션 (PoC 평면 확장 본격 + watchdog v5 + codex est_b1 1-stage fix + measure 4 병렬 + DuckDB-vss 빌드 완료) 종료. **measure 4 병렬 자정까지 자율 → 5/22 00:00 자동 종료 → auto_post_bc_4par daemon rsync+analyze**. → 다음 세션 = 자정 측정분 회수·분석 + Codex/Gemini 교차검증 (잘못 측정 cell·contention 정량) + 최종발표 슬라이드 반영 → 5/22 14:00 박광현 미팅 + 5/24 자문 회신 + 5/27·29 발표 + 5/28 sudo 후 VBASE/Milvus + 6/11 보고서.
