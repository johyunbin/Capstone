# handoff 20260520 07:51 — 엔진 적용 검증 Phase 0: plan 민감도 prescan 완료 + go/no-go

> 이전 handoff(`_internal/handoff/archive/handoff_20260520_021334_harness개편.md`) → 본 문서. 이 문서 하나만 읽으면 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: Phase 0 plan 민감도 prescan 완료 — 24 cell(8 TPC-H × DEEP × sf10 × 3 sel × qid=0) 분류 = **core 4 / plan-saturated 5 / plan-invariant 3 / injection-MISS 12 / capture-fail 0**. **GO 축소 Phase 2 (core cell 만)** 결정. 패턴이 매우 명확 — ① **4 쿼리(q5/q8/q11/q20)는 전 sel MISS** (partsupp pkey IndexScan 경로 → Exqutor SeqScan 한정 주입 skip) ② **나머지 4 쿼리(q3/q9/q10/q12)에서 sel↓=plan 민감도↑** — sel=0.001 = core (base≠B1≠oracle), sel=0.01 = saturated (B1=oracle≠base), sel=0.1 = invariant (oracle=base). 다음 세션 = Phase 2 축소 매트릭스 측정 — §4.

---

## 0. 가장 먼저 — 정본·진입점

- **★ 승인된 실험 plan**: `~/.claude/plans/sorted-twirling-cloud.md` (본 세션 Phase 0 plan, 5가지 stress-test 반영). 직전 세션 plan `~/.claude/plans/imperative-crafting-tome.md` 은 Phase 1 완결 — 폐기.
- **★ 라우팅·구조 정본**: 루트 `CLAUDE.md`. anchor 는 본 handoff 로 갱신 예정 (§6 참조).
- **★ Phase 0 산출물 정본**: `_internal/cache/rq3/latency/prescan/` (24 cell JSON + `prescan_summary.json`).
- **★ harness 정본 = 서버 배포본**: 서버 `/mnt/hdd0/home/capstone2026/cache/rq3/{measure_latency_realengine,gen_latency_estimates,analyze_latency,prescan_plan_sensitivity}.py` (repo `_internal/scripts/` 와 동일).
- **★ 추정치 정본**: 서버 `cache/rq3/latency/estimates_DEEP_sf10.parquet` (195행 = 5 qid × 3 sel × 13 method).
- **★ 패치된 vector.c (불변 — 건드리지 말 것)**: 서버 `/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector/src/vector.c`.

## 1. 본 연구 framing (불변 — 가장 먼저 내재화)

본 연구는 Exqutor 논문(arXiv:2512.09695v2) 재현이 아니라 **표본 선택(sample selection) 단계 하나**의 개입(무작위 Bernoulli → 분포 인지 stratification)이 추정 오차(Q-error)에 미치는 영향을 전 변인에 걸쳐 검증한 완전 실험 — 3-way matched B1(기존)·CaseA(완전 대체, 음성 대조군)·CaseB(결합, 산술평균). 발표물은 코드명(B1/CaseA/CaseB)·"영역" 필러·영어 메타 라벨·수식 노출 금지.

「엔진 적용 검증」 = 오프라인 검증된 카디널리티 추정치(method 13종 결합 = CaseB)를 패치된 PostgreSQL(서버 55435)에 주입해 "추정치 → 실행 계획 → end-to-end latency" 고리를 닫는 실험. 4조건: 기본엔진(baseline) / 베이스라인(B1) / 결합(CaseB×13) / 오라클(true_card).

## 2. 「엔진 적용 검증」 메커니즘 (불변 전제 — 직전 세션 recon 정본)

- **2-pass**: Exqutor 는 실행 시점 2-pass. planner_hook 는 pass-1(기본 selectivity) 만, `ExecutorRun` 훅이 벡터 술어 탐지·재plan 후 pass-2 실행. **순수 EXPLAIN 영원히 pass-1 만 봄** → plan 캡처는 `auto_explain`(`log_format=json`, `client_min_messages=log`).
- **SeqScan 한정 주입**: `check_for_vector_search`(vector.c L643-694) 는 SeqScan 분기에서만 `injected_card` 사용. pkey IndexScan 경로는 주입 skip → 측정마다 `injection_fired` 플래그 기록 필수.
- **세션 셋업**: 모든 세션 `LOAD 'vector'` 필수. plan capture 세션은 `LOAD 'auto_explain'` **먼저** (훅 체인 순서). `SET vector.update_sample_size=off` + `SET plan_cache_mode=force_custom_plan`.
- **테이블 명명**: 서버 전부 `<name>_<sf>` suffix. harness 는 세션마다 임시 VIEW(`partsupp_deep` + base 7종) 생성 → VAQ 템플릿 무수정 실행.
- **latency 측정**: 실쿼리 직접 실행 + `time.perf_counter()`(EXPLAIN ANALYZE 금지). 2-pass 오버헤드 포함 정직값.

## 3. 이 세션(5/20 07:00~07:51)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| 직전 handoff 정독·plan 수립 | ✅ | `imperative-crafting-tome.md` Phase 1 결과 → 새 plan `sorted-twirling-cloud.md` (5 stress-test 반영 후 승인). |
| `prescan_plan_sensitivity.py` 신규 | ✅ | 256줄. harness 함수(`_capture_plan`·`temp_view_ddls`·`load_estimates`) library import. **plan_signature_v2** = `(Node Type, Relation/Index, Join Type)` pre-order tuple (analyze_latency.plan_signature 강화판 — Hash Join build/probe swap·SeqScan↔IndexScan 분간). **classify 5-way** + go/no-go decision. |
| 로컬 dry-run 검증 | ✅ | plan_signature_v2 unit·classify 7 분기·8쿼리×3 sel×3 cond 변환 72건·VIEW DDL·go/no-go matrix 전수 통과. |
| 서버 scp + 1 cell sanity probe | ✅ | q3·sel0.01·qid0 — base sig n=12(Hash Join 일색) ≠ oracle sig n=11(Nested Loop + IndexScan lineitem_10) — 직전 세션 probe §4.5 와 byte-수준 동일 패턴. B1·oracle card_seen 정확 일치. classification=plan-saturated. |
| 24 cell 본 prescan | ✅ | 서버 nohup 8분 12초. **분류 분포 매우 깔끔**(§4 표). |
| 결과 회수·분류·go/no-go | ✅ | 24 cell JSON + summary 로컬 mirror. **GO 축소 Phase 2** 결정. |

## 4. ★★ Phase 0 결과 — 다음 세션이 반드시 흡수할 정본

### 4.1 분류 분포 (24 cell)

| 분류 | 갯수 | cells |
|---|--:|---|
| **core ★** | **4** | q3·q9·q10·q12 × **sel=0.001** |
| plan-saturated | 5 | q3·q9·q10·q12 × sel=0.01, q9 × sel=0.1 |
| plan-invariant | 3 | q3·q10·q12 × sel=0.1 |
| **injection-MISS** | **12** | q5·q8·q11·q20 × 전 sel (3개씩 × 4 쿼리) |
| capture-fail | 0 | — |

### 4.2 핵심 패턴 — 2축 stratification

**축 1 — 쿼리**: 8 TPC-H 쿼리가 정확히 2그룹으로 분리.
- **SeqScan 그룹 (q3·q9·q10·q12)**: partsupp 가 pass-1 플랜에서 Parallel SeqScan 경로 → `injection_fired=True`. 12/12 cell 모두 fired.
- **IndexScan 그룹 (q5·q8·q11·q20)**: partsupp 가 pkey IndexScan(nested-loop inner) 경로 → `injection_fired=False`. 12/12 cell 모두 MISS. true_card 와 무관하게 baseline=B1=oracle sig (주입 미발동).

**축 2 — selectivity (SeqScan 그룹 내)**: sel↓ = plan 민감도↑. 같은 4 쿼리에서:
- **sel=0.001** (true_card=7,603): **core**. base sig ≠ B1 sig ≠ oracle sig 모두 다름. 예: q3 base n=12 → B1 n=9 → oracle n=9 (서로 다른 9-노드 sig). B1 추정치가 oracle 과 다른 플랜을 유도 → CaseB ×13 method 의 추가 정확도가 의미 있을 cell.
- **sel=0.01** (true_card=79,727): **plan-saturated**. B1 sig = oracle sig ≠ base sig. B1 의 Bernoulli 추정만으로도 oracle 과 같은 pass-2 플랜에 도달 → CaseB ×13 의 추가 정확도는 **플랜 변화에는 무용**(다만 latency 분산은 측정 가치 있음).
- **sel=0.1** (true_card=788,333): **plan-invariant**(q3·q10·q12) 또는 saturated(q9). 행 수가 커서 플래너가 base/B1/oracle 모두 동일 SeqScan+Hash Join 선택 → 카디널리티 정확해도 플랜 무변.

### 4.3 honest 관찰·한계

- **4/24 = 16.7%만 core** — "추정치→플랜 변화" 검증 가능 cell 이 좁다. 4 cell 전부 동일 sel=0.001 — selectivity 일반화 X.
- **12/24 = 50% MISS** — Exqutor 의 SeqScan-only 주입 제약이 실험 가능 영역을 절반 차단. 8 쿼리 중 4가 우리 패치 외부.
- **B1 가 sel=0.01 에서 이미 saturating** — 결합 CaseB 가 정확도를 더 높여도 플랜은 안 바뀐다. CaseB > B1 우열을 보일 가장 강력한 cell 은 **sel=0.001 의 core 4** — 여기서 B1 부정확이 oracle 과 다른 플랜을 골랐고, CaseB 가 oracle 쪽으로 끌어당겨야 한다.
- **probe sanity 결과(q3 sel0.01)**: plan-saturated 분류 — 직전 세션 1 cell probe(2.6~3.5× speedup)도 **이 saturated cell** 의 latency 차이였다. 즉 "B1 만으로도 oracle 플랜 → latency 단축"이 일어난 것 — CaseB 추가 우위는 별개 검증 필요.

### 4.4 핵심 수치 (정본 — prescan_summary.json)

| cell | n_base | n_b1 | n_orcl | true_card | oracle card_seen | class |
|---|--:|--:|--:|--:|--:|---|
| q3 sel0.001 | 12 | 9 | 9 | 7,603 | 7,603 ✓ | core ★ |
| q3 sel0.01 | 12 | 11 | 11 | 79,727 | 79,727 ✓ | saturated |
| q3 sel0.1 | 12 | 12 | 12 | 788,333 | 788,333 ✓ | invariant |
| q9 sel0.001 | 20 | 17 | 18 | 7,603 | 7,603 ✓ | **core ★** |
| q9 sel0.01 | 20 | 20 | 20 | 79,727 | 79,727 ✓ | saturated |
| q9 sel0.1 | 20 | 21 | 21 | 788,333 | 788,333 ✓ | saturated |
| q10 sel0.001 | 15 | 11 | 12 | 7,603 | 7,603 ✓ | **core ★** |
| q10 sel0.01 | 15 | 13 | 13 | 79,727 | 79,727 ✓ | saturated |
| q10 sel0.1 | 15 | 15 | 15 | 788,333 | 788,333 ✓ | invariant |
| q12 sel0.001 | 8 | 7 | 7 | 7,603 | 7,603 ✓ | **core ★** |
| q12 sel0.01 | 8 | 7 | 7 | 79,727 | 79,727 ✓ | saturated |
| q12 sel0.1 | 8 | 8 | 8 | 788,333 | 788,333 ✓ | invariant |
| q5/q8/q11/q20 × 3 sel | 동일 sig × 3 | (모두 baseline=B1=oracle, fired=F) | | | — | **MISS × 12** |

## 5. ★ 다음 세션 task

1. **[최우선] Phase 2 — 축소 매트릭스 측정 (core 4 cell)**:
   - **core cells**: q3·q9·q10·q12 × DEEP × sf10 × sel=0.001 × qid=0 (4 cell)
   - **variants**: baseline / B1 / oracle + CaseB ×13 method = 16 variant
   - **반복**: 15 timed + 1 warmup, statement_timeout=600s, 캐시 셔플 (harness 기본값)
   - 실행: `python3 measure_latency_realengine.py --query q3 --dataset DEEP --sf 10 --sel 0.001 --query-id 0 --estimates latency/estimates_DEEP_sf10.parquet --output latency/phase2 --n-timed 15` × 4 쿼리. 각 cell 약 16 variant × 16 rep ≈ 256 query exec — ~15-25분/cell, 4 cell = **1-1.5시간**.
   - 산출: `latency_tpc_h_<q>_DEEP_sf10_sel0.001_qid0.json` × 4. 셀별 plan_json·injection_fired·exec_ms trimmed/median/IQR.

2. **[권장] qid 확장 — core cell stability**:
   - core 4 cell × qid {1, 2} 추가 (4 × 2 = 8 cell × 16 variant ≈ 30분-1시간). qid 분산이 plan 변화 패턴 흔드는지 검증. plan-saturated 가 qid 따라 core 로 변하거나 그 반대인 cell 이 있는지.

3. **[권장] saturated cell 의 latency 측정 (참고용, 코어 외)**:
   - plan-saturated 5 cell — B1 만으로 plan 도달했지만 **latency 분산은 측정 가치 있음** (CaseB 가 plan 변화 없이도 분산 줄이는지). 단 우선순위는 낮음.

4. **[보고] injection-MISS 12 cell — honest limitation**:
   - 보고서 §honest_limitations 에 "Exqutor SeqScan-only 주입 제약으로 8 TPC-H 쿼리 중 4 (q5·q8·q11·q20)는 실험 외" 명시. 6/11 최종 보고서 §4.7 (또는 신규 §) 에 카탈로그.

5. **Phase 3 — analyze + figure**: `analyze_latency.py` + paired Wilcoxon (4 cell × 16 variant), 플랜 변화 카탈로그 (core 4 cell 의 base vs CaseB×13 vs oracle), Q-error → 플랜 → latency 사슬. ⚠️ 서버 matplotlib 미설치 — figure 는 로컬 또는 서버 설치.

6. **Phase 5 — 6/11 보고서 반영**: Phase 0 분류·core 4 latency·honest limitation 반영. deck·포스터는 5/26·28 마감이라 **시간 촉박** — Phase 2 매트릭스 측정 → 결과 통합을 5/25 까지 끝내야 함.

## 6. 서버 접속·실행 (carry-forward, 불변)

- 접속: `ssh capstone` (165.132.140.240, capstone2026, 무암호). PG: `PGPASSWORD=wns41559 psql -h localhost -p 55435 -U wns41559 -d wns41559` (DB·user·pw 모두 `wns41559`, superuser).
- 55435 = 우리 패치 바이너리. datadir `/mnt/hdd0/home/capstone2026/vanilla_sf100`. `vector.injected_card` 기본 −1 = 평소 동작 → dormant 안전.
- 서버 작업 dir `/mnt/hdd0/home/capstone2026/cache/rq3/`: harness 3종 + prescan + 측정 백엔드 `_measure_common.py`·`measure_paper_exact.py` + 산출물 `latency/`.
- ⚠️ **`build_custom.sh`/`apply_patch.sh` 절대 금지** — `git checkout v0.7.1` 후 재패치라 팀의 stratified 모드 + 주입 패치가 파괴됨. 재빌드 필요 시: `cd /mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/pgvector && export PG_CONFIG=/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin/pg_config && make && make install` 후 `pg_ctl restart`.
- 포트 정책: 55435 만 우리 작업.

## 7. 산출물 경로

| 산출물 | 경로 | 상태 |
|---|---|---|
| 승인 Phase 0 plan | `~/.claude/plans/sorted-twirling-cloud.md` | 정본 (Context+Approach+Verification 5섹션) |
| prescan script | repo `_internal/scripts/prescan_plan_sensitivity.py` + 서버 `cache/rq3/` | 256줄·신규 |
| prescan 결과 24 cell + summary | `_internal/cache/rq3/latency/prescan/` (로컬 mirror) + 서버 `cache/rq3/latency/prescan/` | 25 JSON |
| prescan 실행 log | `_internal/cache/rq3/latency/prescan_24cell_20260519_224045.log` (서버 UTC 파일명) | — |
| 1 cell sanity probe (q3 sel0.01) | 서버 `cache/rq3/latency/prescan_sanity/cell_q3_DEEP_sf10_sel0.01_qid0.json` | — |
| harness 3종 (확정) | repo `_internal/scripts/{measure_latency_realengine,gen_latency_estimates,analyze_latency}.py` + 서버 동일 | 미커밋 (직전 세션 carry) |
| 추정치 parquet (정본) | 서버 `cache/rq3/latency/estimates_DEEP_sf10.parquet` | 195행 13 method |
| 직전 세션 probe (q3 sel0.01) | 서버 `cache/rq3/latency/latency_tpc_h_q3_DEEP_sf10_sel0.01_qid0.json` | 1 cell 실증 |
| 패치 vector.c | 서버 `/mnt/hdd0/.../pgvector/pgvector/src/vector.c` | 불변 |
| 수치 정본(오프라인 v13) | `_internal/cache/rq3/v13_summary.md` | 불변 |
| 6/11 최종 보고서 | `submission/_drafts/속도는벡터_6_11_최종보고서_20260519_135021.{md,pdf,docx}` | 정본 |
| 발표 deck (커밋) | `submission/_drafts/속도는벡터_최종발표_슬라이드_20260519_223845.pptx` | 커밋 82f5eca |

CLAUDE.md anchor 갱신 필요: 현재 anchor 가 직전 handoff(`handoff_20260520_021334_harness개편.md`) 가리킴 → **본 handoff 로 갱신**.

## 8. carry-forward / 보류 / 미커밋

- **★ 미커밋 변경**: 본 세션 — `_internal/scripts/prescan_plan_sensitivity.py` 신규 + `_internal/cache/rq3/latency/prescan/` 산출물 25개 + handoff 2종. **세션 시작 전부터** — harness 3종(`_internal/scripts/`) 개편(직전 세션) + `submission/_drafts/` archive 이동 잔여(이전 세션). 본 세션 커밋 안 함 — 사용자 복귀 후 검토·커밋 권장.
- **6/11 보고서 .md 만 archive 이동되고 .pdf/.docx 잔존** → CLAUDE.md anchor 불일치 가능 (carry, 영향 미미 — 정본 위치는 .pdf/.docx 가 잡고 있음).
- **deck**: 슬라이드2복원본(223845) 검증·커밋 완료(`82f5eca`) — 5/22 교수님 미팅 ready. **5/26 PPTX 마감·5/27 발표·5/28 포스터** 임박 — Phase 2 측정 결과를 5/25 까지 반영해야 deck/포스터에 들어감.
- **3차 자문메일**: 미발송 (`submission/_drafts/archive/속도는벡터_3차 자문요청_20260518.{md,pdf}`).
- **deferred tool 로드 패턴**: 새 세션은 `ToolSearch select:TaskCreate,EnterPlanMode,ExitPlanMode,Monitor` 로 선제 로드.

## 9. ★ 환각 회피 룰 (필독)

- 주입 메커니즘 정본 = 이전 handoff `handoff_20260520_021334_harness개편.md` §4 + 본 handoff §2. **순수 EXPLAIN 무효**, plan capture 는 auto_explain, 모든 세션 `LOAD 'vector'` 필수, 테이블 `<name>_<sf>` → 임시 VIEW.
- harness 는 측정마다 `injection_fired` 기록 — **false 면 그 측정 무효**. Phase 0 prescan 에서 12 cell (q5/q8/q11/q20) 가 전부 fired=F 인 것 확인 — 이들은 Phase 2 측정도 의미 없음.
- **core 4 cell 은 sel=0.001 한정** — sel 일반화 금지. 다른 sel 은 saturated/invariant.
- **prescan 의 plan-saturated 분류는 "B1 만으로 oracle 플랜 도달"** 의미 — 카디널리티 추가 정확도가 플랜 변화에는 무용. 다만 latency 분산은 별개. CaseB > B1 우열을 보일 가장 강한 cell 은 core 4.
- **q3 sel0.01 probe(2.6~3.5×)는 plan-saturated cell** — B1 만으로도 일어난 latency 단축. "CaseB 가 더 빠르다" 주장으로 generalize 금지.
- 수치는 prescan_summary.json + v13_summary.md 실측. 핸드오프 본문 §4.4 표 정확값.
- TPC-DS 사장 — 코어 TPC-H 8 (그 중 4 valid).
- vector.c·`build_custom.sh`/`apply_patch.sh` 손대지 말 것 — Phase 2 도 코드 무수정.

---

작성: 2026-05-20 07:51 KST — Phase 0 prescan 완료, GO 축소 Phase 2 결정. → 다음 = Phase 2 매트릭스 측정 (core 4 cell × 16 variant × 15 timed ≈ 1-1.5시간), §5.
