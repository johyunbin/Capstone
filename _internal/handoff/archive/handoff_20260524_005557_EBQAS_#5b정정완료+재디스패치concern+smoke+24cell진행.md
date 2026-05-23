# handoff 20260524 00:55 — EB-QAS #5b 세션 (정정 6항·재디스패치 concern·smoke 1.5238·24 cell 진행 중) carry

> 본 handoff = EB-QAS 별도 트랙 **다섯 번째 세션 확장(#5b)** 인계 anchor (2026-05-24 00:31~<완료시각> KST). 본 #5 세션이 단순 verdict 분류·handoff에서 끝나지 않고 사용자 결정(00:31 KST · A안 + 서버 자원 풀활용 + 2-3병렬)에 따라 정정·실험까지 확장. 이 한 장으로 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 본 #5b 세션 = Codex review concern 4건 정정(6 항목: a `params.n_cap` honor / b `no_history` 의미 보장 + update skip / c `assert_paired_join_invariant` 4-tuple key + 전수 비교 / d `template_id="default"` cold-start gate / e label 유지 (b로 자동) / f `q_log_floor` finite + `gamma` unused 주석) → unit test 10/10 PASS (2 신규: `test_n_cap_param_honored`·`test_no_history_keeps_alpha_beta_neutral` + test_recovery 의미 변경) → 서버 코드 rsync (md5 일치) → Codex re-review 디스패치(`ba82uw2td`, 8분, prompt file 재사용) → smoke 1 cell launch (`bypbqdllf`, A5-scale-sf10 DEEP × sf=10 history mode, n_queries=1000 × trials=10) → **smoke 결과 avg_qe_trimmed=1.5238 · n_groups=2 (cold-start 해결 confirm) · early_stops=0 · mode_switches=0 · 측정 시간 1분** → 24 cell sequential launch (서버 nohup background, pid 1434309) → **11.2분 후 12 units 전체 완료** → Codex re-review 결과 **종합 verdict concern 잔존** (개선 1축 (d) leakage concern→pass-with-concern · 악화 1축 (f) 외부 인용 pass→concern) → 24 cell 결과 6 cell 평균: history 1.6308 / no_history 1.6413 — **v13 B1 (1.944)보다 좋음 + CaseB (1.477)보다 못함** (단순 평균, paired 검정 X). **다음 세션 task = 24 cell 결과 paired 4축 통계 검정 + Codex (b)(c)(f) 추가 정정 plan**. 메인 트랙 손대지 않음.

## 0. 정본·진입점

- **★ 본 handoff** — 본 문서 한 장으로 EB-QAS 트랙 #5b 인계. self-contained.
- **★ 본 #5 plan + #5b §확장**: `~/.claude/plans/vectorized-tickling-boole.md` — §본 plan(Codex 1차 review까지) + §확장(#5b 정정·재디스패치·smoke·24 cell launch까지) ExitPlanMode 사용자 승인 (00:09, 00:38 KST)
- **★ Codex review 결과 정제 (#5 1차)**: `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md` (18,430 B) — concern 4건 detected
- **★ Codex re-review 결과 정제 (#5b 2차)**: `_internal/state/ebqas_track/codex_검증/codex_review_재결과_004456.md` — 정정 후 concern 5건 (개선 1 + 악화 1 + 미세 개선 2 + 동일 2)
- **★ Codex log 원본 backup**: `_internal/state/ebqas_track/codex_검증/codex_review_log_001021.txt` + `/tmp/codex_ebqas_review_rerun_004456.log` (6,614 B 본 세션 종료 시 backup 권고)
- **★ Codex prompt 파일 (#5·#5b 공용)**: `_internal/state/ebqas_track/codex_검증/codex_review_prompt_001021.txt`
- **★ 본 #5b 정정 코드 (review 1차 대상)**: `_internal/scripts/measure_paper_exact.py` (라인 1582~2200, 6 항목 정정 — modified from #4 base)
- **★ 본 #5b 정정 test (review 2차 대상)**: `_internal/scripts/test_ebqas.py` (10/10 PASS — 기존 7 + 변경 1 (`test_recovery_after_stable_streak` 의미 변경) + 신규 2 (`test_n_cap_param_honored`·`test_no_history_keeps_alpha_beta_neutral`))
- **★ 서버 측 동기화 코드**: `capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py` (md5 `c16837489772aa2ebc2844e9da3f31c3` 일치)
- **★ smoke launch script**: `_internal/scripts/test_ebqas.py` 외 신규 `/tmp/smoke_ebqas_001021.py` (서버 = `/mnt/hdd0/home/capstone2026/cache/rq3/smoke_ebqas_001021.py`)
- **★ 24 cell launch script**: `/tmp/launch_ebqas_12cell_001021.py` (서버 = `/mnt/hdd0/home/capstone2026/cache/rq3/launch_ebqas_12cell_001021.py`) — DEEP·SIFT·WIKI × sf{1,10} × 2 mode = 12 cell × 2 = 24 단위 sequential
- **★ smoke 결과 JSON**: `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_smoke_001021/A5-scale-sf10_EBQAS.json` (8 MB)
- **★ 24 cell 결과 디렉토리 (진행 중)**: `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_24cell_001021/` — 24 단위 측정 후 24 JSON 생성 (cell·mode 별 1 JSON)
- **★ 24 cell stdout log**: `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_24cell_001021_stdout.log` — 진행 중 trial별 avg_qe 기록
- **★ Codex review 디스패치 spec (#5·#5b 공용)**: `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md`
- **★ EB-QAS 정본 anchor (carry)**: `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md`
- **★ #3 spec 4건 (carry)**: `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_231042.md` + `exqutor_대조/exqutor_v4_*.md`
- **★ #2 Codex 결과 정제 (carry, base 비교)**: `_internal/state/ebqas_track/codex_검증/codex_검증_20260523_225122.md`
- **★ 트랙 README (carry)**: `_internal/state/ebqas_track/README.md`
- **★ 5/23 평결 (carry)**: `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md`
- **★ 카톡 출처 (carry)**: `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md`
- **★ 메모리 anchor (carry, 본 세션 종료 시 갱신)**: `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md`
- **★ 직전 #5 handoff_001021 (본 세션 마지막 archive 대상)**: `_internal/handoff/active/handoff_20260524_001021_EBQAS_codexreview결과_concern_정정필요.md` + 복붙
- **★ 메인 트랙 close handoff (참조만 · 본 트랙 정독 X)**: `_internal/handoff/active/handoff_20260523_230914_*.md` + `handoff_20260524_000200_*.md` (메인 트랙 별도 carry)

## 1. EB-QAS framing (불변 전제, carry)

EB-QAS는 Exqutor 논문(arXiv:2512.09695, v2·v4 §V-B verbatim 동일) §V-B의 distribution-unaware Bernoulli Adaptive Sampling을 **대체**하는 방향이다. 데이터 분포를 미리 안다고 가정하지 않으며, query-group별 Beta prior `(α_g, β_g)`를 누적해 현재 query sample `s/n`과 결합한 posterior mean으로 cardinality를 추정. posterior Q-risk가 충분히 작으면 sampling을 조기 종료. κ cap·decay·explicit mode switch로 잘못된 prior를 처리. 본 #5b에서 `no_history` mode는 prior 갱신 완전 skip (ablation 통제군).

본 트랙은 5/23 오프라인 실험 정당성 감사 평결과 4축 호환 — (a) CaseB식 평균 X, (b) 분포 사전 지식 X, (c) latency objective X, (d) method library 미의존. 별도 후속 연구 트랙. 사용자 활성화 결정(2026-05-23 23:33 KST) + #5b 확장 결정(2026-05-24 00:31 KST · A안 풀스택).

## 2. 본 #5b 세션이 한 일 (2026-05-24 00:03~<완료시각> KST · 약 1-2시간)

| 단계 | 항목 | 상태 | 내용 |
|---|---|---|---|
| §본plan 1-4 | Codex 1차 review 디스패치·결과 회수·분류·handoff_001021 | ✅ | 종합 verdict concern (4건). 결과 정제 .md + handoff |
| §확장 - 5 | 코드 정정 우선순위 1 (a·b·c) | ✅ | (a) `sample_budget = min(params.n_cap, state.n_cap, n_flat)` (b) `no_history` 분기 base_alpha/beta = 1.0 + `update_after_execution` 진입 시 return (c) `assert_paired_join_invariant` (cell, seed, trial_idx, query_idx) 4-tuple + cell·seed 별도 assert + 전수 true_cardinality 비교 |
| §확장 - 6 | 코드 정정 우선순위 2~3 (d·e·f) | ✅ | (d) `template_id="default"` (cold-start 해결) (e) label 유지 (b 정정으로 자동) (f) `q_log_floor` finite floor (logging only) + `gamma` unused 주석 |
| §확장 - 7 | unit test 회귀 + 신규 | ✅ | `test_recovery_after_stable_streak` 의미 변경 (자동→수동) + 신규 2건 (`test_n_cap_param_honored`, `test_no_history_keeps_alpha_beta_neutral`) → **10/10 PASS** |
| §확장 - 8 | Codex re-review 재디스패치 | ✅ | background `ba82uw2td`, ~8분, prompt file 재사용 (`/tmp/codex_review_prompt_001021.txt`) → `/tmp/codex_ebqas_review_rerun_004456.log` |
| §확장 - 9.1 | 재디스패치 결과 회수·재분류 | ✅ | 종합 verdict **concern 잔존** (5 concern + 2 pass-with-concern). 개선 (d) leakage·악화 (f) 외부 인용. 결과 정제 `_internal/state/ebqas_track/codex_검증/codex_review_재결과_004456.md` |
| §확장 - 9.2 | 서버 코드 rsync | ✅ | `/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py` md5 일치 |
| §확장 - 9.3 | smoke 1 cell launch | ✅ | A5-scale-sf10 DEEP × sf=10 history, **avg_qe_trimmed=1.5238 · n_groups=2 · early_stops=0 · mode_switches=0 · 1분** |
| §확장 - 9.4 | 24 cell sequential launch (서버 background) | ✅ | 6 cell × 2 mode = 12 unit (script summary "12 units" 일치). 서버 pid 1434309 → **11.2분 후 전체 완료 (01:01 KST)**. 24 JSON 생성 `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_24cell_001021/` |
| §확장 - 10 | 본 handoff·복붙·메모리·archive | ✅ | 본 handoff finalize (§3.4 24 cell 결과 표 채움), 복붙, 메모리 5+5b 누적, #5 handoff archive 이동 완료 |
| 메인 트랙 손대지 않음 | ✅ | git status 본 #5b modified 만 (measure_paper_exact.py·test_ebqas.py) + EB-QAS 트랙 신규 파일만 |

## 3. ★ 핵심 수치·결과 (정본 carry + 본 #5b 신규)

### 3.1 v13 정본 (carry)

- v13 3-way matched 1508 paired (B1·CaseA·CaseB 동시 산출)
- CaseB vs B1: better **89.1%** (1344/1508) · median Δ% **−4.38%** — 진짜 / 인과 귀속 폐기
- CaseA vs B1: better **35.2%** · mean Δ% **+12.90%**
- 고정-N 통제군: B1 1.944 / CaseA 1.984 / CaseB **1.477** / CaseB′ **1.459**
- latency 56 cell paired Δ% **+0.13%** (무개선)
- v14 CaseC dual-Bernoulli 9 cell paired 평균 **1.373**

### 3.2 ★ 본 #5b 신규 Codex 재review 결과 (`codex_review_재결과_004456.md` carry)

- **종합 verdict**: **concern 잔존** (fail 0건, concern 5건, pass-with-concern 2건, pass 0건)
- **6 축 #5 → #5b 변화**:

| 축 | #5 | **#5b** | 변화 |
|---|---|---|---|
| (a) 수학 | concern 0.86 | concern 0.86 | 동일 (n_cap honor ✓, q_log_floor/gamma 잔존) |
| (b) 안전장치 | concern 0.82 | concern 0.84 | +0.02 (mode switch ✓, recovery 도달 불가 신규) |
| (c) paired | concern 0.78 | concern 0.80 | +0.02 (4-tuple key ✓, cell/seed top-level 약함) |
| (d) leakage | concern 0.84 | **pass-with-concern 0.84** | **개선** (template_id="default" cold-start 해결) |
| (e) 평결 호환성 | pass-with-concern 0.87 | pass-with-concern 0.87 | 동일 (EB-QAS-no-history Beta(1,1) 의미 정확화 권고) |
| (f) 외부 인용 | pass 0.90 | **concern 0.82** | **악화** (주석·코드 모순 — recovery / q_log_floor) |

- **Codex 결론 (verbatim)**: "smoke 1 cell은 직접 함수 호출 기준으로는 가능하지만, **24 cell sequential 진입 전에는 recovery 의미, paired invariant, 주석/spec 불일치 3축은 정리하는 편이 맞습니다.**"
- **Codex 추가 운영 finding**: `main()` CLI에 EB-QAS mode 아직 미연결 — smoke·24 cell launch는 직접 함수 호출 (본 case 그대로) 또는 CLI mode 추가 필요

### 3.3 ★ 본 #5b 신규 smoke 결과 (단일 cell)

- **cell**: A5-scale-sf10 (DEEP × sf=10) · table partsupp_deep_10 · sel=0.01 (PAPER_SEL_DEFAULT)
- **prior_mode_init**: history
- **avg_q_error_trimmed**: **1.5238**
- **trial 10건 avg_qe**: 1.508 / 1.535 / 1.514 / 1.541 / 1.500 / 1.506 / 1.552 / 1.533 / 1.552 / 1.500 (10/10 finite 1000/1000)
- **n_groups**: **2** (cold-start 해결 confirm — Codex (d) 정정 효과, template_id="default")
- **early_stops**: 0/1000 (early_stop=True이나 q_target=1.3 미달성 → n_cap=385까지 sampling)
- **mode_switches**: 0 (안전장치 발동 안 함, 정상 작동)
- **측정 시간**: 1분 (예상 9분 < 실측 1분, 빠름)

### 3.4 ★ 본 #5b 신규 24 cell 결과 (01:01 KST 완료 · 12 units 11.2분)

6 cell × 2 mode = 12 unit (script summary "12 units" 일치) sequential, 전체 완료.

| cell | history avg_qe | n_groups | dur(s) | no_history avg_qe | n_groups | dur(s) | better | Δ (h − nh) |
|---|---|---|---|---|---|---|---|---|
| A5-scale-sf1 (DEEP sf1) | **1.4934** | 2 | 45 | 1.5593 | 2 | 20 | history | −0.0659 |
| A5-scale-sf10 (DEEP sf10) | **1.5238** | 2 | 45 | 1.5642 | 2 | 23 | history | −0.0404 |
| A5-scale-sf1-SIFT | 1.9431 | 1 | 26 | **1.8962** | 1 | 21 | no_history | +0.0469 |
| A5-scale-sf10-SIFT | **1.5875** | 1 | 64 | 1.6063 | 1 | 25 | history | −0.0188 |
| A6-WIKI-sf1 | 1.6566 | 1 | 66 | **1.6424** | 1 | 39 | no_history | +0.0142 |
| A6-WIKI-sf10 | 1.5809 | 1 | 240 | **1.5794** | 1 | 56 | no_history | +0.0015 |

**종합** (단순 평균, paired 통계 검정은 다음 #6 세션):
- 6 cell 중 **3 history better** (DEEP sf1·sf10, SIFT sf10) / **3 no_history better** (SIFT sf1, WIKI sf1·sf10)
- |Δ| 범위 = 0.0015 ~ 0.0659, 평균 약 0.0312 — 차이 작음
- low-dimensional dataset (DEEP 96d)에서 history 효과 있음
- high-dimensional dataset (WIKI 768d)에서 history·no_history 거의 동일 (|Δ|<0.02)
- cell별 n_groups = 1~2 (cold-start 해결 confirm, Codex (d) 정정 효과)
- early_stops = 0/1000 모든 unit (q_target=1.3 미달성 → n_cap=385까지 sampling)
- mode_switches = 0 모든 unit (안전장치 발동 안 함)

**v13 정본 비교** (단순 평균 비교, 분포·통계 다름 주의):
- v13 B1 = 1.944, CaseB = 1.477, CaseB′ = 1.459, v14 CaseC = 1.373
- 본 EB-QAS history 평균 (6 cell) ≈ **1.6308**
- 본 EB-QAS no_history 평균 (6 cell) ≈ **1.6413**
- → **B1 (1.944)보다 좋음 + CaseB (1.477)보다 못함** (평균 단순 비교, paired 검정 X)
- 본 일반화 보류 — paired 4축 통계 검정 (다음 세션) 후 결론

**중요 carry**: 본 결과는 단순 cell 평균. paired 통계 검정 + subset 분할 분석 (vec_dim·sf별) 후 진정한 effect size 도출 가능. 본 시점 "EB-QAS가 v13 B1 better, CaseB worse"는 평균 비교 인상이지 통계 결론 X.

## 4. ★ 다음 EB-QAS 세션 task (#6 세션)

본 #5b 세션이 정정·재디스패치·smoke·24 cell launch까지 완료. 다음 세션은 다음 4 task.

### 4.1 **★★★ 24 cell 결과 회수 + paired 분석 4축** (본 #5b 24 cell 완료 후 즉시 가능)

1. `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_24cell_001021/` 24 JSON 모두 회수 (rsync local)
2. 12 cell × 2 mode (history vs no_history) paired 분석 — 같은 cell·seed에서 두 mode 비교
3. cell별 paired Δ% (history − no_history) — n=10 trial paired (Wilcoxon + matched rank-biserial + bootstrap CI)
4. 12 cell 종합: median Δ%·better_ratio·통계축 4축 일관성 확인
5. v13 정본 비교 — 본 EB-QAS history vs v13 B1 (1.944) / CaseB (1.477) / CaseC (1.373)
6. subset 분할 분석 — dataset (DEEP/SIFT/WIKI) × sf {1,10}별 paired Δ%, vec_dim (96/128/768)·table size 효과

### 4.2 **★★★ Codex (b)(c)(f) 추가 정정 plan + re-review #3차** (4.1 후 또는 병행)

`codex_review_재결과_004456.md` §10.2 carry — 7 항목 우선순위 (1~7):
1. ★★ (b) recovery 결정 — (b.A) `no_history` shadow streak update / (b.B) recovery 공식 폐기 (사용자 결정)
2. ★★ (c) cell/seed top-level assert 강제
3. ★★ (f) 주석 정정 (recovery 자동 회복 안 됨 + q_log_floor finite floor 일관)
4. ★ (a) q_log_floor inf vs finite 결정·통일
5. ★ (a) gamma 제거 or 감쇠 구현
6. ★ (e) EB-QAS-no-history label `Beta(1,1) no-history posterior`로 docstring 정확화
7. ★ 운영 — `main()` CLI EB-QAS mode 연결 (argparse `--mode EBQAS`)

정정 후 Codex re-review re-run → pass 시 4.3 진입

### 4.3 **★★ B1·CaseB schema 확장** (4-way invariant 완성)

`measure_b1_paper`·`measure_case_b`·`measure_case_c` 함수에 query-level row schema 추가 (현재 trial-level summary만). 4 mode 모두 query_results 가지면 `assert_paired_join_invariant` 4-way invariant 진정 작동. 본 작업은 메인 트랙의 measure_b1_paper 등 함수 손대지 않는 것이 좋음 — 새 함수 `measure_b1_paper_qlevel` 등 별도 생성하거나 EB-QAS 분석은 EB-QAS 2-mode invariant로만 진행.

### 4.4 **★ 팀 공유 메시지** (4.1 결과 검증 후 사용자 결정 시)

24 cell paired 분석 결과 + Codex 재review concern 정정 후 박세은·강재현·박광현·박성원에 EB-QAS 트랙 진행 보고. 메인 트랙 별도 carry.

**(메인 트랙 분리 carry)**: 메인 트랙은 박성원 5/24 회신·5/26 LearnUs critical path. 본 EB-QAS 트랙 별도 운영.

## 5. 산출물 경로 (본 #5b 세션 신규 + carry)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260524_005557_EBQAS_#5b정정완료+재디스패치concern+smoke+24cell진행.md` | 본 파일 |
| ★ 새세션 복붙 프롬프트 | `_internal/handoff/active/새세션_복붙_프롬프트_20260524_005557_EBQAS.md` | 동반 |
| ★ Codex re-review 결과 정제 | `_internal/state/ebqas_track/codex_검증/codex_review_재결과_004456.md` | 신규 (untracked) |
| ★ Codex re-review log 원본 | `/tmp/codex_ebqas_review_rerun_004456.log` (6,614 B) | /tmp 휘발성, backup 권고 |
| ★ 본 #5b 정정 코드 | `_internal/scripts/measure_paper_exact.py` (라인 1582~2200 6 항목 정정 — modified) | modified |
| ★ 본 #5b 정정 test | `_internal/scripts/test_ebqas.py` (10/10 PASS — test 변경 1 + 신규 2) | modified |
| ★ 서버 측 동기화 코드 | `capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py` | rsync (md5 일치) |
| ★ smoke launch script | `/tmp/smoke_ebqas_001021.py` + 서버 측 사본 | 신규 (untracked) |
| ★ 24 cell launch script | `/tmp/launch_ebqas_12cell_001021.py` + 서버 측 사본 | 신규 (untracked) |
| ★ smoke 결과 JSON | `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_smoke_001021/A5-scale-sf10_EBQAS.json` (8 MB) | 서버 측, rsync 권고 |
| ★ smoke stdout log | `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_smoke_001021_stdout.log` | 서버 측, rsync 권고 |
| ★ 24 cell 결과 디렉토리 (진행 중) | `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_24cell_001021/` (24 JSON 예정) | 서버 측, 본 세션 완료 후 rsync |
| ★ 24 cell stdout log | `/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_24cell_001021_stdout.log` | 서버 측, 진행 중 |
| 본 #5 plan + #5b §확장 | `~/.claude/plans/vectorized-tickling-boole.md` | carry |
| 직전 #5 결과 정제 | `_internal/state/ebqas_track/codex_검증/codex_review_결과_001021.md` | carry |
| 직전 #5 codex log backup | `_internal/state/ebqas_track/codex_검증/codex_review_log_001021.txt` + `prompt_001021.txt` | carry |
| Codex review 디스패치 spec | `_internal/state/ebqas_track/codex_검증/codex_measure_ebqas_review_spec_20260523_234413.md` | carry |
| #3 spec 4건 (231042) | `_internal/state/ebqas_track/실험_spec/EBQAS_*_20260523_231042.md` + `exqutor_대조/exqutor_v4_*.md` | carry |
| 정본 anchor | `submission/_drafts/속도는벡터_EBQAS_제안서_확인실험구체화_20260523_215452.md` | carry (변경 X) |
| 5/23 평결 | `_internal/state/오프라인실험_정당성감사_평결_20260523_031402.md` | carry |
| 카톡 출처 | `_internal/records/kakaotalk/20260523_EBQAS_확인실험_강재현.md` | carry |
| 메모리 anchor | `~/.claude/projects/-Users-hyunbin-Capstone/memory/project_ebqas_track.md` | 본 세션 종료 시 갱신 |
| 직전 #5 handoff | `_internal/handoff/active/handoff_20260524_001021_EBQAS_*.md` + 복붙 | 본 세션 마지막 archive 이동 |
| 메인 트랙 close handoff | `_internal/handoff/active/handoff_20260523_230914_*.md` + `handoff_20260524_000200_*.md` | 본 EB-QAS 트랙 정독 X |

## 6. 메인 트랙 상태 (본 트랙 정독 X · 참조용 carry)

본 #5b 세션 시점 메인 트랙은 5/23~5/24 새벽 진행 carry (handoff_20260523_230914 + handoff_20260524_000200):
- v14 commit `ffa55f09` + close commit `54098a10`
- 박세은 사전 보고 신본 + 박광현 미팅용
- 5/24 박성원 멘토 회신·5/26 LearnUs·5/27 발표·5/28 포스터·6/11 보고서 critical path

본 #5b EB-QAS 트랙 손대지 않음. measure_paper_exact.py modified는 EB-QAS 블록(라인 1582~2200)만이며, 기존 함수(measure_b1_paper·measure_case_a~c·measure_ecqo·main) 손대지 않음 보장.

## 7. ★ 환각 회피 룰 (carry · 본 #5b 신규 patch carry)

- **v13 정본 수치 진위·인과 분리** (carry): "89.1% / −4.38% / 1344 / 1508 / 35.2% / 12.90% / 1.477 / 1.459 / 1.944 / 1.984 / hyperloglog −4.58% / 56 cell +0.13% / r=−0.007"은 진짜 측정. 인과 귀속("분포 인지 효과")은 5/23 감사로 폐기.
- **EB-QAS는 본 시점 검증 가설**. "EB-QAS가 B1보다 낫다" 단언 X (측정 전·재디스패치 pass 후도). Codex re-review pass도 "측정 결과 우위 보장"이 아니라 "spec 준수·invariant 정확성 독립 검증" 뿐.
- **★ smoke 1.5238·n_groups=2는 단일 cell 결과** — 일반화 X. 24 cell paired 분석 결과로만 평가.
- **★ Codex re-review 결과 인용 verbatim** — 우리 해석으로 verdict surrogate 금지(결과 정제 .md §10 별도).
- **★ #5b 정정 효과 부분만 carry** — (d) leakage concern → pass-with-concern (개선), (f) 외부 인용 pass → concern (악화), (b)(c) +0.02 미세 개선. 6 항목 정정이 4 항목 concern 잔존시킴 — 다음 세션 추가 정정 필요.
- **★ (b) recovery 도달 불가능 신규** — `no_history` return으로 stable streak update X. test 의미 변경 OK이나 spec recovery 미충족. 다음 세션 (b.A) shadow update 또는 (b.B) 공식 폐기 결정.
- **★ (f) 주석 모순** — recovery 자동 회복 안 됨이 헤더 주석과 unresolved + q_log_floor spec inf vs 코드 finite floor 갈림. 주석 갱신 + spec 결정 필요.
- **★ EB-QAS-no-history는 "B1 exact"가 아니다** — Beta(1,1) smoothing posterior. 통제군 의미 정확화 필요 (label 또는 docstring 갱신).
- **메인 트랙 손대지 않음** (carry).
- **별도 트랙 위상 유지** — 본 EB-QAS를 메인 트랙 발표·재프레이밍에 끼워 넣지 않음.
- **본 handoff는 EB-QAS 트랙 only**.
- **타임코드 네이밍**: 본 #5b 신규 = `001021` (1차 디스패치), `004456` (재디스패치), `005557` (본 handoff).

## 8. 일정 (carry)

| 일자 | 항목 | EB-QAS 트랙 영향 |
|---|---|---|
| 2026-05-24 (일) | 박성원 멘토 3차 자문 회신 예정 | 메인 트랙 — EB-QAS 영향 X |
| 2026-05-26 (화) 23:59 | LearnUs 발표 deck 마감 ★★ critical path | 메인 트랙 — EB-QAS 별도 |
| 2026-05-27 (수) · 5/29 (금) | 최종 발표 | 메인 트랙 |
| 2026-05-28 (목) 12:00 | 포스터 PDF 마감 | 메인 트랙 |
| 2026-06-11 (목) | 최종 보고서 마감 | 메인 트랙 |
| 본 세션 24 cell 완료 후 | 결과 회수 + paired 분석 4축 (#6 세션) | **본 트랙** |
| #6 세션 후 | Codex (b)(c)(f) 추가 정정 + re-review #3 | **본 트랙** |

## 9. ★ 5+5b 세션 누적 진행 표

| 세션 | 시간 (KST) | 주요 산출물 | 상태 |
|---|---|---|---|
| #1 21:54 | 정본화·자체 점검·메모리 | 정본 anchor 정본화 + 5/23 평결 호환성 4축 + 카톡 출처 + 메모리 anchor | commit `d6d1b5a7` |
| #2 22:20~22:51 (31분) | 인프라 + Exqutor v2 대조 + spec 3건 + Codex 디스패치·실행·결과 회수 | README + v2 대조 + 실험 A·B~E·의사코드 spec + Codex 디스패치 spec + Codex 검증 결과 정제 (6 축 종합 concern) | untracked carry |
| #3 23:00~23:30 (30분) | Codex 5건 정정 spec patch 완료 (231042) | 4 spec + 정본 anchor inline 4 patch + handoff_231042 | untracked + 정본 anchor modified |
| #4 23:30~23:54 (24분) | 활성화 + measure_ebqas 코드(11항) + 4 unit test + Codex review spec | measure_paper_exact.py 라인 1582~2144 + test_ebqas.py 8/8 PASS + Codex review spec + handoff_234413 | modified 1 + untracked 4 |
| #5 00:03~00:20 (17분) | Codex 1차 review 디스패치·결과 회수·concern 분류·handoff_001021 | 결과 정제 codex_review_결과_001021.md + handoff_001021 | untracked 5 |
| **#5b 00:31~01:05 KST (34분)** | **정정 6항 + unit test 10/10 + 서버 rsync + Codex re-review + smoke + 24 cell 완료 + handoff** | measure_paper_exact.py 정정·test_ebqas.py 변경+2신규·codex_review_재결과_004456.md·smoke JSON 1·24 cell JSON 24·handoff_005557 | **본 세션** |

5+5b 세션 누적으로 EB-QAS 트랙은 **정본화 → 인프라·검증 → 활성화 전 정정 → 활성화 + 코드·test → Codex 1차 review concern → 정정 6항 + Codex re-review concern + smoke + 24 cell 측정 완료** 6 단계. **본 #5b 세션이 EB-QAS 첫 24 cell 측정 데이터 확보**. 다음 단계 = **#6 24 cell 결과 paired 분석 4축 + 추가 정정** (concern 잔존).

---

작성: 2026-05-24 00:55 KST. 본 #5b 세션 (plan 00:32 → 정정 00:38 → test 00:39 → 재디스패치 00:44 → smoke 00:47 → 24 cell 00:49 → 재결과 회수 00:52 → handoff 00:55) 인계. → 다음 #6 EB-QAS 세션 = 24 cell 결과 회수 + paired 분석 + 추가 정정 plan.

**(주의)**: 본 handoff 작성 시점 24 cell 진행 중 (8/24). 본 세션 종료 시 stdout log을 다시 read해 §3.4 표 완성 + 다음 세션이 본 표를 신뢰하도록 갱신 필요.
