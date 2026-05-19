# Capstone Hygiene Plan — 2026-05-09

작성: 백그라운드 에이전트 (5/9 01:00 KST)
참고 패턴: Trading 5/9 00:32~01:00 정리 (CLAUDE.md 224→32 인덱스 + 5 분야별 파일 분리)

**원칙**: inventory + plan only. 실제 실행은 main session 사용자 동의 후.

---

## A. CLAUDE.md 분리 plan

현재 **289 lines** (Trading 112의 2.6배). 라우팅 + 핵심 룰만 ~110 lines 유지하고, 동적/상세 영역은 분리.

| 현재 section | lines | 분리 대상 | 새 file path |
|---|---|---|---|
| `## 현재 단계` (인용 블록 포함 narrative) | 11~26 | ⭕ 분리 | `_internal/state/current_phase_20260509.md` |
| `### 새 RQ 구조` | 28~41 | ⭕ memory 로 이동 | `memory/project_capstone.md` 갱신 (이미 존재, 통합) |
| `### 실행 로드맵` 표 | 43~61 | ⭕ 분리 | `_internal/state/roadmap_20260509.md` |
| `### 다음 단계` checklist | 63~92 | ⭕ 분리 | `_internal/state/next_steps_20260509.md` |
| `### W1 Sprint 산출` 부속 | 94~107 | ⭕ archive | `_internal/archive/2026_05_09_state/w1_sprint_results.md` |
| `### 산출물 위치` (5/8 finalize) | 108~140 | ⭕ archive (영구 자료는 별도) | `_internal/archive/2026_05_09_state/deliverables_20260508.md` |
| `## 세션 시작 체크리스트` | 132~148 | ✅ 유지 (라우팅) | — |
| `## 디렉토리 구조` | 150~184 | ✅ 유지 (참조 빈도 高) | — |
| `## 지침 시스템` | 186~201 | ✅ 유지 (라우팅) | — |
| `## 핵심 일정` 표 | 203~228 | ⭕ 분리 (동적) | `_internal/state/schedule_20260509.md` |
| `## 카카오톡 / Exqutor / 문서 규칙 / 파일명 규칙` | 230~265 | ✅ 유지 (안정 룰) | — |
| `## 도구 / 팀 / 참고 링크` | 267~289 | ✅ 유지 (간단) | — |

**예상 결과**: CLAUDE.md 289 → **약 110 lines** (라우팅 + 안정 룰만), 동적 5 file 분리.

---

## B. memory/ status

- **MEMORY.md**: 23 lines — Trading 32보다 가벼움, **분리 불필요** ✅
- **14 active files** 평가:
  - `project_capstone.md` 316 lines, 5/8 22:09 update → 매우 활성, 유지
  - `reference_document_templates.md` 367 lines, 5/5 update → reference 문서, 유지
  - `reference_server.md` 169 lines, 5/5 → 유지
  - 나머지 11 file 모두 17~66 lines, 적정 ✅
- **stale candidates 없음** — 가장 오래된 file 도 5/5 (4일 전, 2주 한도 내)
- **결론**: 14 file fragmentation 적정. 변경 권장 사항 **없음**.

---

## C. _internal/ archive plan

현재 31 file (디렉토리 제외). 5/8 회의/세션 종료 → 9 audit + handoff_v12 = **10 file archive 후보**.

| 항목 | 파일 수 | 사유 | archive path |
|---|---|---|---|
| `audit_*_20260508.md` | 9 | 5/8 회의/세션 종료, V1~V9 결과 master_v6 §10.7 + 자문 메일 v4 반영 완료 | `_internal/archive/2026_05_09_audit_archive/` |
| `handoff_v12_*.md` | 1 | v13/v14/v15 chain 으로 superseded | `_internal/archive/2026_05_09_handoff_archive/` |
| `Z2_final_sanity_check_20260508.md` | 1 | 5/8 commit 0db9760 으로 fix 적용 완료 | `_internal/archive/2026_05_09_audit_archive/` |
| `자문메일_v4_format_검증_20260509.md` | 1 | commit 9c1c282 verify 결과 반영 완료 | `_internal/archive/2026_05_09_audit_archive/` |
| `ultra_review_*_20260508.md` | 5 | 5/8 22:30 reviews, 결과 적용됨 | `_internal/archive/2026_05_09_audit_archive/` |
| `the_end_review_checklist_20260508.md` | 1 | 5/8 종료 checklist | `_internal/archive/2026_05_09_audit_archive/` |
| `multi_subagent_prompt_20260508.md` | 1 | 5/8 사용 종료 | `_internal/archive/2026_05_09_audit_archive/` |
| `Claude_Design_요청_prompt_20260508.md` | 1 | 산출물 storyline 으로 superseded | `_internal/archive/2026_05_09_audit_archive/` |
| `20260508_회의직전_카톡_초안.md` | 1 | 5/8 회의 종료 | `_internal/archive/2026_05_09_audit_archive/` |
| `setup_multi_sf1_20260508.md` | 1 | 5/8 setup 적용 완료 | `_internal/archive/2026_05_09_audit_archive/` |
| `자문메일_발송체크리스트_20260508.md` | 1 | superseded by v4 verify | `_internal/archive/2026_05_09_audit_archive/` |

**유지 (active)**:
- `handoff_v13_session_20260508_2110_*.md` — 진입점
- `handoff_v14_session_20260508_2200_*.md` — 진입점
- `handoff_v15_template_20260508.md` — 5/9 morning rename 대기
- `Adaptive_Sampling_method_분석_20260508.md` — 영구 reference
- `RQ3_paradigm_심층검증_20260508.md` — 영구 reference
- `slide_redesign_v2_20260508.md` — 5/27 발표 사용 예정
- `claude_design_prompt_storyline_20260508.md` — 5/15 자문 결과 wait
- `팀원공유_업데이트_template_20260508.md` — 재사용 template
- `README.md`, `session_state.json` — meta
- `yfcc_compare_20260508.log` — 영구 reference

**예상 archive**: **23 file** → `_internal/archive/2026_05_09_audit_archive/` (1 directory).

---

## D. 권장 실행 순서

1. **_internal/ archive** (가장 안전, 영향 범위 최소)
   - `mkdir -p _internal/archive/2026_05_09_audit_archive`
   - `mv` 23 files (위 표 참조)
2. **CLAUDE.md 분리** (Trading 패턴 따름)
   - `mkdir -p _internal/state`
   - 5 file 추출 (current_phase / roadmap / next_steps / schedule + archive 2)
   - CLAUDE.md slim 재작성 → 약 110 lines
3. **memory/MEMORY.md update 불필요** (23 lines, 분리 한도 미달)
4. **검증**:
   - `wc -l CLAUDE.md` — 110 line 근방 확인
   - `ls _internal/ | wc -l` — 23 → 8 정도로 감소
   - `git diff --stat` — 변경 범위 확인
5. **commit**: `chore: hygiene cleanup 5/9 — _internal archive 23 + CLAUDE.md 분리`

---

## E. 비가역 작업 체크

- 모든 archive = **디렉토리 이동 (`mv`)**, 삭제 (`rm`) 없음 ✅
- CLAUDE.md 분리 = **split, not delete**, 기존 내용은 분리된 파일에 보존 ✅
- memory/ 변경 없음 ✅
- 사용자 동의 받기 전 위 작업 모두 **실행 보류** ✅
- 롤백 가능: `mv` 역순 복원 + CLAUDE.md git revert ✅

**Trading 5/9 패턴과 일치**: 디렉토리 이동만, rm 없음, 사용자 동의 후 진행.
