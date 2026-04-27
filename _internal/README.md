# _internal — 내부용 (팀원은 들어오지 않아도 됨)

이 폴더는 **조현빈 개인의 작업 파일과 세션 상태**를 모은 곳이다. 팀 공유가 필요 없는 자료들이며, 팀원이 보아야 할 것은 루트의 `README.md` 가 안내한다.

## 무엇이 들어 있나

| 하위 | 무엇 | 누가 쓰나 |
|---|---|---|
| `guideline/` | Claude Code 자동화 지침 (실험·제출물·문서·미팅·발표) — `01_*` ~ `05_*` 의 auto/manual/실행 3 파일 세트 | 조현빈 (Claude Code 워크플로우) |
| `learning/` | Claude Code 활용 학습 자료, 한국어/영어 공부 노트 | 조현빈 |
| `session_state.json` | Claude Code 세션 상태 파일 | 시스템 |

## 왜 따로 모았나

`Capstone/` 루트에 디렉토리가 너무 많아 어떤 폴더를 봐야 하는지 헷갈린다는 피드백(2026-04-15 강재현)을 해소하기 위해, 팀 공유가 필요 없는 자료를 `_internal/` 하위로 모아 루트의 인지 부담을 줄였다. 팀원이 직접 들어와야 하는 디렉토리는 `submission/`, `experiments/`, `records/`, `plans/`, `reference/` 다섯이며, 그 외에 `templates/`(양식)와 `scripts/`(빌드 도구)는 필요할 때만 사용한다.

## 동기화 규칙

`guideline/`, `learning/`, `session_state.json` 의 일부 파일은 git 추적 대상이 아니다. PC 간에는 `~/.claude/rules/hygiene.md` 의 동기화 규칙에 따라 rsync 로 옮겨진다. 자세한 사항은 `~/.claude/rules/hygiene.md` 참조.
