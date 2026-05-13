# _internal — 내부용 (팀원은 들어오지 않아도 됨)

이 폴더는 **조현빈 개인의 작업 파일과 세션 상태**를 모은 곳이다. 팀 공유가 필요 없는 자료들이며, 팀원이 보아야 할 것은 루트의 `README.md` 가 안내한다.

> **마지막 update**: 2026-05-14 07:25 KST — multi-join 8/8 + Centroid tuple 8/8 + cheap 근사 4 후보 32 + α sweep 16 + A2-Fig8 8 측정 완료, 시나리오 B 확정, _drafts/ 4 file 4차 정정 + PDF 4종 finalize.

## 새 세션 진입 anchor (1 file read 만으로 0% loss)

- **`handoff/active/handoff_v17_session_finalize_20260514_0721.md`** (5/14 07:21, 본 세션 18.5h 종합 + 시나리오 B 확정 + _drafts 4 file 4차 정정 + PDF 4종)
- **`handoff/active/handoff_v16_km_granularity_+_multijoin_inflight_20260513_1238.md`** (5/13 12:38, multi-join in-flight 시점 reference)

## 분석 file 5건 (5/13 ~ 5/14 신규)

| File | 내용 |
|---|---|
| `analysis/multi_join_restratification_results_20260513.md` | multi-join 8/8 finalize, 시나리오 A.5 (Hybrid) |
| `analysis/centroid_tuple_cheap_approximation_results_20260513.md` | Centroid tuple 8/8 + 새 method axis (Cheap 근사 친화도) |
| `analysis/resource_efficiency_pareto_20260513.md` | Pareto Top 5 + 산업 적용 3 영역 + reservoir O(1) finding |
| `analysis/alpha_sweep_results_20260514.md` | α sweep 16, 시나리오 B 확정 |
| `analysis/cheap_approximation_extended_results_20260514.md` | cheap 근사 4 후보 32 종합 |

## 핵심 file (active 9건, root)

| File | 내용 |
|---|---|
| `MASTER_README.md` | 단일 진입점 + measurement 진행 + 5단계 narrative + 일정 |
| `MASTER_HANDOFF.md` | handoff v0~v6 + validation + Phase 4 통합 |
| `METHOD_REGISTRY.md` | 57 method × 10 paradigm 분류 + 폐기/rename 권고 |
| `EXPERIMENT_REGISTRY.md` | 9 cells × 56 methods × 3 modes matrix |
| `SERVER_REGISTRY.md` | server SSH / 작업 dir / NPY cache / log / tmux / 자원 룰 |
| `CHANGELOG.md` | 5/10~5/11 핵심 결정/측정/정리 timeline |
| `naming_convention.md` | file naming 규칙 |
| `README.md` | 이 file |

## 무엇이 들어 있나

| 하위 | 무엇 |
|---|---|
| `handoff/{active,archive}/` | 새 세션 인계 anchor (active v8/v9) + 이전 v0~v6 archive 5건 |
| `state/{_next, _schedule, archive}/` | 동적 state (다음 단계 + 일정) + 5/9 이전 archive |
| `method_audit/{20260510_initial, 20260511_phase4}/` | method 검증 (5/10 8 agent audit 11 file + 5/11 Phase 4 5 file) |
| `validation/` | 4-layer audit + data/319 |
| `scripts/{active, archive/5월8일_scripts_정리}/` | 문서 빌드 도구 (md2pdf 등) + 측정 script (analyze_paper_exact / figures_paper_exact / method_phase4_extra 등) |
| `cache/` | 분석 결과 cache (multi_paradigm_raw / rq3 / single_ensemble_raw / phase_g_analysis 등 67M) |
| `guideline/` | Claude Code 자동화 지침 (활성 5 + archive 6) |
| `learning/` | 학습 자료 (kr/us + 클로드코드활용지침) |
| `records/` | 회의록 (kakaotalk + weekly + raw_export) |
| `archive/` | 이전 시점 history — `5월7일_dawn_chain_분석/` + `5월8일_정리흔적/` + `5월9일_method_audit/` + `handoff_v0_v18_초기_세션/` |
| `문서_archive/` | 5/11 정리 작업 archive — `이전_handoff/` + `5_8_시점_outdated_docs/` + `state_과거_시점/` + `정리작업_log/` |
| `server_wrappers_backup_20260507/` | 5/7 server wrapper backup (8KB) |

## 디렉토리 분리 이유 (2026-04-15 강재현 피드백 해소)

`Capstone/` 루트에 디렉토리가 너무 많아 어떤 폴더를 봐야 하는지 헷갈린다는 피드백을 해소하기 위해, 팀 공유가 필요 없는 자료를 `_internal/` 하위로 모았다. 팀원이 직접 들어와야 하는 디렉토리는 `submission/`, `experiments/`, `records/`, `plans/`, `reference/` 다섯이며, 그 외에 `templates/`(양식)와 `scripts/`(빌드 도구)는 필요할 때만 사용한다.

## 동기화 규칙

`guideline/`, `learning/`, `cache/` 의 일부 파일은 git 추적 대상이 아니다. PC 간에는 `~/.claude/rules/hygiene.md` 의 동기화 규칙에 따라 rsync 로 옮겨진다.
