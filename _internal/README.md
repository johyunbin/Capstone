# _internal — 내부용 (팀원은 들어오지 않아도 됨)

이 폴더는 **조현빈 개인의 작업 파일과 세션 상태**를 모은 곳이다. 팀 공유가 필요 없는 자료들이며, 팀원이 보아야 할 것은 루트 `README.md` 가 안내한다.

> 마지막 정리: 2026-05-19 — 디렉토리 총 정리(옛 정본 문서 archive 격리 · archive 일원화 · 완료 캠페인 script 격리 · 네이밍 현행화).

## 새 세션 진입 anchor (0% loss)

- **`handoff/active/handoff_20260519_154301_변환sprint표지요약본.md`** — 현행 세션 인계 anchor. 이 1 file read 로 0% loss 인계.
- 동반 `handoff/active/새세션_복붙_프롬프트_20260519_154301.md` — 새 세션 첫 입력용.
- `handoff/active/` 에는 **현행 1세트만** — 이전 세트는 `handoff/archive/`.

## 핵심 정본 (현행)

| 위치 | 내용 |
|---|---|
| `cache/rq3/v13_summary.md` | ★ 측정 수치 정본 (3-way matched 1508) |
| `cache/rq3/aggregated_v13_full.parquet` | v13 집계 raw |
| `METHOD_REGISTRY.md` | method paradigm 분류 + 폐기/rename 이력 |
| `SERVER_REGISTRY.md` | server SSH / 작업 dir / 자원 룰 |
| `naming_convention.md` | 파일 네이밍 규칙 (타임코드 우선) |
| `state/_schedule.md` | 학기 핵심 일정 |
| `CHANGELOG.md` | 작업 timeline |

## 하위 디렉토리

| 하위 | 무엇 |
|---|---|
| `handoff/{active,archive}/` | 세션 인계 — active 현행 1세트 + archive 이전 세트 |
| `cache/rq3/` | v13 측정 집계·분석 (구버전 v8/v12 는 `cache/rq3/archive_v8_v12/`) |
| `scripts/` | 문서 빌드 도구(md2pdf 등) + 측정·분석 script. 완료 캠페인 orchestration 은 `scripts/archive/` |
| `state/` | 동적 state (`_next` · `_schedule` · 제출공지) |
| `method_audit/` | method 검증 (5/10 audit + 5/11 phase4) |
| `validation/` | 4-layer audit + data |
| `guideline/` | Claude Code 자동화 지침 — 인덱스 `guideline/README.md` |
| `records/` | 회의록 (kakaotalk + weekly) |
| `learning/` | 학습 자료 |
| `포스터영상_build/` | 5/28 포스터·소개영상 build 산출 |
| `archive/` | 이전 시점 history — 단일 archive (5/19 `문서_archive` 흡수, 한글날짜 → YYYYMMDD) |

## 디렉토리 분리 이유 (2026-04-15 강재현 피드백 해소)

`Capstone/` 루트에 디렉토리가 너무 많다는 피드백을 해소하기 위해, 팀 공유가 필요 없는 자료를 `_internal/` 하위로 모았다. 팀원 진입 디렉토리는 루트 `README.md` 참조.

## 동기화 규칙

`guideline/`·`learning/`·`cache/` 의 일부 파일은 git 추적 대상이 아니다. PC 간에는 `~/.claude/rules/hygiene.md`·`sync.md` 의 규칙에 따라 동기화한다.

---

작성: 2026-04-15 · 갱신: 2026-05-19 (디렉토리 총 정리). 이전 README 는 git history 보존.
