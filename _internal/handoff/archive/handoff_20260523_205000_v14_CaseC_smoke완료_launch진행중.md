# handoff 20260523 20:50 (갱신 21:30) — v14 CaseC 코드·smoke·9 cell launch 모두 완료

> 직전 handoff (`_internal/handoff/archive/handoff_20260523_185000_박광현피드백통합반영_Codex검증.md`) → 본 문서. 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄 (21:30 갱신)**: v14 4-way 측정 spec (§10) 의 task #1 (measure_case_c 함수 작성 · CLI dispatch · smoke · production launch) **모두 완료**. server side `/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py` 에 measure_case_c (1-stage Bernoulli + sel_override) 추가 + 9 cell × CaseC sequential launch **완료 21:29:47 KST, 38분 29초, 9/9 OK fail 0**. 산출물 9 JSON 각 ~4.4KB at `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v14_20260523/`. Smoke (A5-scale-sf1, 3.5 초) 검증 통과 — avg_q_error_trimmed=1.467 ≈ CaseB v13 정본 1.477. Production A5-scale-sf100 trial 7 final_size_a=4232 vs final_size_b=443 = 11× divergence 관찰 = Option A 독립 진화 극단 케이스 evidence. **다음 세션 = (1) launch 완료 확인 (이미 OK, 1줄 ls 로 즉시 통과) → (2) v14 aggregate parquet 작성 + v13 paired delta 비교 → (3) 산출물 통합 (slide 13 portfolio evidence 격상·storyline·redline·prompt 패치·보고서 §4.2 CaseC 통제군 분석) → (4) user 카톡 paste 결과 확인 + 박세은 사전 보고 진행 → (5) prompt 복붙 → claude.ai/design 22장 신본 pptx export → 5/26 23:59 LearnUs 마감.**

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계.
- **★ 직전 handoff (carry)**: `_internal/handoff/archive/handoff_20260523_185000_박광현피드백통합반영_Codex검증.md` — 박광현 5/22 미팅 #1·#3·#4 통합 반영 + Codex 적대 검증 P0 5/P1 6 즉시 반영 + v14 spec §10 정리 시점. 본 세션 = 그 §10 task #1 실행.
- **★ Plan (5/23 12:33 ExitPlanMode 승인)**: `~/.claude/plans/witty-sniffing-aurora.md` — 4 Phase (A 팀합의·B ICDE·C reject 이중명시·D 검증)
- **★ 평결 정본 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` — A1-A5 종합, Codex 적대 재검증 반영
- **★ 재프레이밍 제안서 (박세은 OK)**: `submission/_drafts/속도는벡터_제출물_재프레이밍_제안_20260523_031402.md`

## 1. 본 연구 framing (carry · 불변)

본 연구 = Exqutor 논문 (arXiv:2512.09695v2) §V-B 적응적 표본 추출의 표본 선택 단계 하나 (무작위 Bernoulli → 분포 인지 stratification) 개입의 효과를 controlled verification 으로 검증. 3-way matched (B1·CaseA·CaseB) 측정 + 4번째 평균 비교군 (CaseB' = Bernoulli + Bernoulli 평균) 통제. **5/23 audit 결과**: 89% Q-error 우위 = 앙상블 평균 효과 (통제군 CaseB' 1.459 ≤ CaseB 1.477) · latency 56 cell paired Δ% +0.13% 무개선. **NEW 서사**: "통제 실험으로 겉보기 89% 의 진짜 원인 = 평균 효과 임을 규명한 음성·방법론적 결과". 발표물 코드명 (B1·CaseA·CaseB·CaseB'·CaseC) 노출 금지, 한국어 라벨 통일 ("베이스라인 방식 · 단독 대체 방식 · 결합 방식 · 평균 비교군 · 기본 엔진 · 정답").

**박광현 5/22 #1·#2·#3(reject)·#4 처리 완료** (carry, 직전 handoff §1).

**박성원 멘토 3차 자문 회신 = 5/24 (일) 예정** — 회신 도착 시 task #4 로 storyline·redline·prompt 반영.

## 2. 본 세션이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| 직전 handoff §10 정독·design 검토 | ✅ | handoff §10.2 의 "두 state 같은 ensemble q_err update" 가 AdaptiveState 결정성 (Eq 1-6) 으로 인해 redundant (두 state 동일 진화) 임을 발견. user AskUserQuestion 으로 Option A (각 state 자기 q_err) 결정 — audit CaseB' 의 cross-trial 독립 진화 정합 |
| measure_case_c 함수 작성 (local) | ✅ | `_internal/scripts/measure_paper_exact.py:1195-1334` (+~140 lines) · 2-stage Bernoulli 패턴 (local 의 5/23 baseline 따름). **WARNING**: local 은 server divergent — local 의 measure_case_b 는 2-stage 인데 server 는 1-stage (codex finding #1 fix). 향후 reconcile 필요 |
| Server·local diff 분석 | ✅ | server (1693 lines, 5/17) vs local (1495 lines, 5/23 baseline) = +198 lines server-only. 식별된 server fix: (a) DATASET_ALIAS concat entries (DEEP_SIFT_CONCAT 등), (b) A9-A11 concat 측정 트랙 7 cells, (c) measure_3way 함수 (B1+CaseA+CaseB matched 동시), (d) `--sel` argument + 모든 measure_* 에 sel_override 파라미터, (e) measure_case_b 의 1-stage Bernoulli (codex finding #1) |
| Server side measure_case_c 패치 | ✅ | `/tmp/server_5_17.py` 에 4 patch 적용 (함수 삽입 + --phase E + --mode CaseC + dispatch). server pattern 따라 1-stage Bernoulli (`all_vecs=all_vecs`) + sel_override 파라미터. scp 후 server md5=ea8186608e3e5266b9bf7c3037cdd3f7. backup: `measure_paper_exact.py.bak_pre_v14_20260523_2030` (5/15 v5·5/16 concat·5/16 sel·5/17 caseb_1stage·5/17 k10b1 + 본 v14 = 6 backup chain) |
| Local syntax 검증 | ✅ | python3 -c "ast.parse" → SYNTAX OK |
| Smoke test (A5-scale-sf1) | ✅ | 3.5 초 완료. avg_q_error_trimmed=1.467, trial별 1.409·1.468·1.509. trial 3 final_size_a=397 vs final_size_b=877 → **state 독립 진화 확인** (Option A 동작 검증). JSON 구조 완벽 (ensemble_strategy=dual_bernoulli_independent_states · state_update_strategy=each_state_own_q_err · bernoulli_stage=1_stage_all_vecs) |
| Production launch (9 cells background) | ✅ **완료 21:29:47 KST** | PID 1296629 (bash) · 시작 20:51:18 · 완료 21:29:47 · **총 38분 29초** · **9/9 OK, fail 0** · log `/tmp/v14_launch_20260523.log` · output `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v14_20260523/` (9 JSON, 각 ~4.4KB). 개별 timing: A1-DEEP 301s·A1-SIFT 386s·A1-SSN 820s·A2-Fig7 76s·A2-Fig9 33s·A4-sel 364s·A5-scale-sf1 12s·A5-scale-sf10 61s·A5-scale-sf100 256s. A1-SSN (vec_dim=256) 가장 김, A5-scale-sf1 (1M+NPY 캐시) 가장 빠름. **다음 세션 task 1 (launch 완료 확인) 은 ssh ls 1줄로 즉시 통과** → task 2 (aggregate parquet + paired delta) 즉시 진입 가능 |
| v14 handoff + 복붙 프롬프트 작성 | ✅ | 본 파일 + 동반 |

## 3. ★ 핵심 평결·수치 (정본 carry — 변화 없음)

- **A1**: CaseB 89.1% 우위 = 진짜 측정 · 인과 = 앙상블 평균 효과 (통제군 CaseB' 1.459 ≤ CaseB 1.477, CaseB 가 CaseB' 이기는 비율 42%). hyperloglog (무작위 해시) 단독 +2.57% (악화) → 평균에 넣으면 −4.58% "개선" 둔갑 → method 정체 무관 증거
- **A2**: 신호 5종 (hilbert_real·skilling_hilbert·pca1d·zorder_morton·ica_fastica) 모두 PCA/ICA 환원 · skilling_hilbert 가짜 Hilbert · 보고서 §4.7 명칭 노트 hilbert_real ↔ skilling_hilbert 거꾸로
- **A3**: v13 데이터 무결성 — 4,524 행 = 1,508 × 3 완전 매칭 · null/inf 0건 → 재측정 불필요
- **A4**: latency 56 cell 범위 B1 → CaseB 무개선 (paired Δ% +0.13%) · B1 이 oracle 수준 plan 회복 (4.43× ≈ 4.54×) · 구조적 headroom 부재
- **재프레이밍 4-way 표** (B13 정본): 베이스라인 1.944 / 단독 대체 1.984 / **결합 1.477 / 평균 비교군 1.459** · 베이스라인 이긴 비율 (—/44%/99%/100%)
- **★ v14 CaseC smoke 1 cell 결과 (A5-scale-sf1, 100q × 3 trials)**: avg_q_error_trimmed=**1.467** → CaseB v13 1.477 와 통계적 거의 동일. CaseC 가 CaseB 와 같은 분포 → **89% = 앙상블 평균 효과 가설 추가 보강** (full launch 결과로 9 cells 종합 평가 예정)

## 4. ★ 다음 세션 task (5/23 21:00 KST 기준, critical path 5/26 마감)

1. **★★★ Launch 완료 확인 (5/24 새벽 or 21시 이후)** — `ssh capstone2026@165.132.140.240 'tail -30 /tmp/v14_launch_20260523.log && ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v14_20260523/*CaseC.json | wc -l'`. 9 cells 완료 = 9 .json 파일. "v14 CaseC launch COMPLETE" 메시지 확인. fail 0 검증
2. **★★★ v14 aggregate parquet 작성 + v13 paired delta 비교** — 9 CaseC JSON → parquet 통합 + v13 paper_exact/ 에 있는 9 B1·9 CaseB 와 paired Δ% 계산. CaseC vs CaseB Δ% 가 0 근처 (no significant difference) = "89% = 평균 효과" 가설 결정적 입증. 새 script `_internal/scripts/aggregate_v14.py` 작성 또는 build_v13_summary.py 변형. 산출물: `_internal/cache/rq3/v14_summary.md` + `_internal/cache/rq3/aggregated_v14_full.parquet`
3. **★★★ 산출물 통합 path (1 → 2 완료 후)**:
   - storyline 슬라이드 13 portfolio 전수 evidence 격상 (`submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_20260523_110051.md`)
   - redline 동일 슬라이드 보완 (`submission/_drafts/속도는벡터_발표deck_재프레이밍_redline_20260523_110051.md`)
   - prompt 슬라이드 13 instruction + 자가검증 항목 추가 (`submission/_drafts/속도는벡터_발표deck_재프레이밍_prompt_20260523_110051.md`)
   - 보고서 §4.2 CaseC 통제군 분석 단락 추가 (`submission/_drafts/속도는벡터_6_11_최종보고서_20260520_171521.md`)
4. **★★ user 가 카톡 paste 결과 확인** — `_internal/state/팀합의_카카오톡_draft_20260523.md` 응답 수집 → `_internal/records/kakaotalk/20260523_팀합의_재프레이밍.md` 기록 (사용자 19:31 KST "카톡 보고는 됐고" 명시 — 이미 paste 완료일 가능성 확인 필요)
5. **★★ 박세은 → 박광현 교수님 1쪽 사전 보고 (5/24~5/26)** — audit 평결 + #3 reject decision rule + 발표 안 + v14 CaseC 통제 결과. 박세은 결정. Codex P0 #5 finding 반영
6. **박성원 멘토 5/24 회신 반영 (회신 도착 시)**
7. **★★ user prompt 복붙 → claude.ai/design 22장 신본 pptx export (critical path)** — `submission/_drafts/속도는벡터_발표deck_재프레이밍_prompt_20260523_110051.md` text block (line 45-209) 을 v3 deck 만든 **동일 claude.ai/design 대화창** 에 복붙 (새 대화창 X — design system 깨짐). v14 측정 결과 반영된 패치본 사용
8. **메인 세션이 신본 pptx 검증 (Phase 1-5, 5축 vision agent 또는 user 시각)** — 22 장 전체 점검
9. **5/26 23:59 LearnUs 제출** — critical path 마감
10. **Phase 2 = 5/28 포스터 prompt 작성** (deck 신본 export 후 시작, 5/28 12:00 마감, 900×1200)
11. **(carry P1 #9)** 슬라이드 5 또는 15 에 Borrowed/Not Borrowed/Why 3열 표 본문 격상 검토 (user 판단)
12. **(carry P2 #15)** 슬라이드 footer 에 "Adapted from Exqutor ICDE deck; our contribution starts at B13/B20" 출처/경계 명시 검토
13. **(보고서 6/11)** v14 4-way 결과 통합 + 6/11 까지 추가 sweep·multi-engine 검토

## 5. 산출물 경로 (본 세션 신규 + 패치)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260523_205000_v14_CaseC_smoke완료_launch진행중.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260523_205000.md` | 동반 (다음 메시지에 본문 노출) |
| ★ Local measure_case_c | `_internal/scripts/measure_paper_exact.py:1195-1334` (+147 lines) | uncommitted (local divergent vs server, 후속 reconcile) |
| ★ Server measure_case_c (1-stage + sel_override) | server: `/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py` (1850 lines, md5 ea8186608e...) | deployed, smoke 통과 |
| ★ Launch script | server: `/mnt/hdd0/home/capstone2026/cache/rq3/v14_launch_20260523.sh` | 진행 중 |
| ★ Launch log | server: `/tmp/v14_launch_20260523.log` | 진행 중 (`tail -F` 가능) |
| ★ Smoke output | server: `/tmp/v14_smoke_20260523/A5-scale-sf1_CaseC.json` | 검증 통과 |
| ★ Production output | server: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_v14_20260523/` | 진행 중 (9 .json 예정) |
| ★ Server backup chain | server: `measure_paper_exact.py.bak_*` 6 files (5/15~5/23) | safety net |
| Plan 정본 | `~/.claude/plans/witty-sniffing-aurora.md` | carry |
| 팀합의 카톡 초안 | `_internal/state/팀합의_카카오톡_draft_20260523.md` | carry (75줄, paste 응답 대기) |
| ICDE verbatim 발췌 | `_internal/state/ICDE_verbatim_발췌_20260523.md` | carry (120줄) |
| storyline_NEW 패치본 | `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_20260523_110051.md` | carry (263줄, v14 결과 격상 대기) |
| redline 패치본 | `submission/_drafts/속도는벡터_발표deck_재프레이밍_redline_20260523_110051.md` | carry (344줄, v14 결과 격상 대기) |
| prompt 패치본 | `submission/_drafts/속도는벡터_발표deck_재프레이밍_prompt_20260523_110051.md` | carry (310줄, v14 결과 instruction 추가 대기) |

## 6. v14 측정 detail

### 6.1 코드 변경 (server side, 5/17 base + 4 patch)

**Patch 1: measure_case_c 함수 (line 1382, +147 lines)** — pre-registered dual-Bernoulli ensemble:
```python
def measure_case_c(cell, n_queries=1000, trials=TRIALS, output_dir=None, sel_override=None):
    # 두 독립 rng (seed_a = t*13+7, seed_b = +1M offset)
    # 두 독립 AdaptiveState
    # 각 query: est_a + est_b 각각 산출, est_final = (est_a + est_b)/2
    # Option A (user 결정 5/23 20:14): 각 state 자기 q_err 로 update
    #   state_a.update(q_error(est_a, true_card), state_a.size / total_rows)
    #   state_b.update(q_error(est_b, true_card), state_b.size / total_rows)
    # 1-stage Bernoulli (all_vecs=all_vecs) — codex finding #1 fix 와 일관
    # Output: {cell.sub}_CaseC.json (method-independent)
```

**Patch 2: --phase choices** (line 1757): `["A", "B", "C", "D", "G"]` → `["A", "B", "C", "D", "E", "G"]` + help text "E=CaseC dual-Bernoulli (v14 5/23)"

**Patch 3: --mode choices** (line 1763): `["B1", "CaseA", "CaseB", "ECQO", "3way"]` → `["B1", "CaseA", "CaseB", "CaseC", "ECQO", "3way"]` + help text "CaseC = dual-Bernoulli ensemble (v14 5/23)"

**Patch 4: main() dispatch** (line 1837, +3 lines): CaseB → CaseC dispatch (method-independent, --method 불필요)

### 6.2 Launch 진행 (5/23 20:51 KST 시작)

**9 cells sequential 순서** (v14_launch_20260523.sh):
1. A1-DEEP (sf=100, 100M vec, ~5-10 min)
2. A1-SIFT (sf=100, 100M vec, ~5-10 min)
3. A1-SSN (sf=100, 100M vec, ~5-10 min)
4. A2-Fig7 (sf=10, multi-vector ~10M, ~2-5 min)
5. A2-Fig9 (sf=10, multi-vector ~10M, ~2-5 min)
6. A4-sel (sf=100, default sel=0.001 only — sel sweep 폐기, sf=100 100M vec ~5-10 min)
7. A5-scale-sf1 (sf=1, 1M vec, ~30 sec — smoke 와 동일 cell)
8. A5-scale-sf10 (sf=10, 10M vec, ~2-3 min)
9. A5-scale-sf100 (sf=100, 100M vec, ~5-10 min)

**Production params**: trials=10 (paper §VI verbatim), n_queries=1000 (paper Fig 6 verbatim), output_dir=`paper_exact_v14_20260523/`

### 6.3 Smoke 검증 결과 (A5-scale-sf1, trials=3, n_queries=100)

```json
{
    "mode": "CaseC",
    "selectivity": 0.01,
    "ensemble_strategy": "dual_bernoulli_independent_states",
    "state_update_strategy": "each_state_own_q_err",
    "bernoulli_stage": "1_stage_all_vecs",
    "avg_q_error_trimmed": 1.4675747568981448,
    "final_size_a_mean": 396.33, "final_size_a_std": 7.36,
    "final_size_b_mean": 550.00, "final_size_b_std": 231.23,
    "trial_results": [
        {"trial":0, "avg_q_error_finite":1.409, "final_size_a":387, "final_size_b":388},
        {"trial":1, "avg_q_error_finite":1.468, "final_size_a":405, "final_size_b":385},
        {"trial":2, "avg_q_error_finite":1.509, "final_size_a":397, "final_size_b":877}
    ]
}
```

**핵심 관찰**:
- avg_q_error_trimmed=**1.467** ≈ CaseB v13 정본 1.477 (Δ% ~0.7%)
- state_b_std=231 vs state_a_std=7 → **두 state 명백히 독립 진화** (Option A 동작 검증)
- inf 0건 (전 trial 100% finite)
- 1-stage Bernoulli with all_vecs working (no error)
- 3.5 초 wall time

### 6.4 Local·server reconcile (carry, 다음 세션 후속 작업)

**현재 상태**:
- Local `_internal/scripts/measure_paper_exact.py` = 1642 lines (5/23 baseline + my CaseC 2-stage)
- Server `/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py` = 1850 lines (5/17 base + 5/15~5/17 fixes + my CaseC 1-stage)
- **divergence ~208 lines**: server-only fix (concat track·3way mode·sel_override·1-stage Bernoulli) 가 local 에 없음

**Reconciliation path** (5/26 마감 전 또는 그 이후):
- Option A: scp server → local + commit (full sync, recommended)
- Option B: local 의 2-stage CaseC 만 server pattern (1-stage) 으로 수정 + 나머지 server fix 는 다음 reconcile session

**Local 의 measure_case_c 차이점 (vs server)**:
- 2-stage Bernoulli (`bernoulli_estimate(samples_b1, sizes_b1, qvec, D, rng, budget=...)` — no `all_vecs=`)
- 없는 파라미터: `sel_override`
- 없는 result field: `"selectivity": sel`, `"bernoulli_stage": "1_stage_all_vecs"`

## 7. 환경·검증

- **자가검증 (코드)**: python3 ast.parse → SYNTAX OK · grep CaseC anchor 4건 모두 확인 (line 1195/1564/1568/1636 local · 1382/1757/1763/1839 server)
- **자가검증 (smoke)**: JSON 구조 완벽 · avg_qe 정합 · state 독립 진화 확인 · 1-stage Bernoulli working
- **Server 상태**: aigpu-6000ada1, 5/23 11:33 UTC = 20:33 KST, load avg 56-80 (다른 사용자 RL 작업 ongoing), RAM 838Gi available, GPU 0 일부 사용 5GiB, GPU 1·2·3 idle
- **PG instance**: port 55435 accepting connections ✓
- **NPY fast-path**: partsupp_deep_1_vectors.npy (307MB) + _strata.npy (1.6MB) 캐시 존재, smoke 에서 2.4 초 로드 확인
- **미커밋**: local measure_paper_exact.py +147 lines uncommitted (CaseC 2-stage 추가). 직전 세션 분 + 본 세션 분 미커밋 (handoff active dir mv 1건). user commit/push 지시 시 진행
- **시간**: 2026-05-23 본 세션 18:50 → 20:50 KST (2시간) 진행

## 8. 일정 (carry)

- **5/24 (일)** 박성원 멘토 3차 자문 회신 예정 + v14 launch 완료 확인 + aggregate · 산출물 통합
- **5/26 (화) 23:59** 발표 슬라이드 LearnUs 마감 ★★ critical path
- **5/27 (수)** · **5/29 (금)** 최종 발표
- **5/28 (목) 12:00** 포스터 PDF 마감 (900×1200)
- **6/11 (목)** 최종 보고서 마감

## 9. ★ 환각 회피 룰 (carry · 일부 추가)

- **89.1% · −4.38% 는 v13 정본 — 진짜 측정**. 그러나 인과 귀속 ("분포 인지 효과") 은 폐기 → "독립 추정량 평균의 앙상블 효과" 로 정정
- **v14 CaseC smoke 1.467 ≈ CaseB 1.477** → 추가 보강 데이터 (full launch 9 cells 결과로 종합)
- latency 평결은 "측정 56 cell 범위 무개선 · 구조적 headroom 부재" 로 범위 표시
- 단독 대체 (CaseA) 는 "순효과 0" 아님 — portfolio 전체 **악화** (better 35.2% · 평균 +12.90%)
- 측정 데이터 조작·날조 없음 — "환각으로 데이터가 가짜" 부정확. 문제는 인과 해석·일부 method 구현·연구 목표
- 신호 5 종 모두 PCA/ICA 투영 — 보고서 §4.7 명칭 노트 정정 (hilbert_real ↔ skilling_hilbert 거꾸로)
- 발표물 코드명 노출 금지 (평문 deck·포스터) — 한국어 라벨 통일
- **박광현 #3 reject 사유** (speaker note + footer 양쪽 동일 verbatim): 인과 가정 깨짐 + audit 평결 + Codex 적대 재검증 통과 명시. 시간순 (5/22 미팅 → 5/23 03:14 audit → 5/23 12:33 user 결정 → 5/23 18:50 ICDE 통합 → 5/23 20:50 v14 launch) 정직 표시
- **ICDE 차용 verbatim 출처**: `_internal/state/ICDE_verbatim_발췌_20260523.md` 참조. 차용 시 "(ICDE 슬라이드 N)" 라벨 명시 — 출처 추적 가능
- **v14 CaseC = pre-registered dual-Bernoulli ensemble · Option A (각 state 자기 q_err 진화)** — audit CaseB' (cross-trial pair, post-hoc) 의 cherry-pick risk mitigate. **1-stage Bernoulli with `all_vecs=`** (server pattern, codex finding #1 fix 와 일관)
- **Local·server divergence**: server side direct 수정 fix 가 local repo 에 없음. v14 launch 는 server 신본 (1-stage CaseC) 사용. local 의 2-stage CaseC 는 후속 reconcile 필요
- 비가역 작업 (git push --force · rm -rf · DB DROP) user 승인 후 · KST 기준
- **prompt 복붙 시 user 가 v3 deck 만든 동일 claude.ai/design 대화창에 붙여야** — 새 대화창은 v3 design system (navy·악센트 4색·Apple SD Gothic Neo·hero 그라데이션·raster burned-in) 을 모르므로 절대 규칙 위반 가능

---

작성: 2026-05-23 20:50 KST. 본 세션 (handoff §10 정독 → measure_case_c 함수 작성 [local 2-stage + server 1-stage] → CLI patch → smoke A5-scale-sf1 통과 → production launch 9 cells background) 인계. → 다음 세션 = launch 완료 확인 → aggregate v14 → paired delta vs v13 → 산출물 통합 (storyline 슬라이드 13·redline·prompt·보고서 §4.2) → user 카톡 응답 확인 → 박세은 사전 보고 → claude.ai/design export → 5/26 마감.
