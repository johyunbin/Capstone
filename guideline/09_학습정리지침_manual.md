# 학습정리지침 (MANUAL)

> 수동 참조용. 자동 실행은 `09_학습정리지침_auto.md` 참조.

## 언제 사용하나?

- learning/ 폴더에 새 스크립트가 추가되었을 때
- 유튜브/블로그 등 외부 학습 자료를 정리하고 싶을 때
- Claude Code 사용법을 체계적으로 정리하고 싶을 때

## 핵심 원칙

1. **전수 읽기**: 대충 읽거나 키워드만 보지 않는다. 모든 글자를 읽는다.
2. **출처 보존**: 누가 말했는지, 어떤 스크립트에서 나왔는지 기록한다.
3. **구체적 보존**: 명령어, 설정값, 경로 등 구체적 정보는 추상화하지 않는다.
4. **주제별 분리**: 하나의 거대한 문서가 아닌 주제별로 분할 저장한다.

## 저장 위치

| 대상 | 위치 |
|------|------|
| 주제별 정리 | Apple Notes > Claude 폴더 (Trading 양식) |
| 참조 메모리 | memory/reference_claude_code_kr_mastery.md |
| 전역 원칙 | ~/.claude/CLAUDE.md "Claude Code 활용 원칙" 섹션 |

## Apple Notes 양식 (Trading 폴더 기준)

```
제목: 이모지 + 짧은 제목
h1:   <b><span style="font-size: 16px">이모지 제목</span></b>
부제: <i><font face="Courier-Oblique"><span style="font-size: 8px">설명</span></font></i>
섹션: <b><span style="font-size: 12px">이모지 섹션명</span></b>
본문: <font face="Courier"><span style="font-size: 8px"><tt>내용</tt></span></font>
```

## 분류 체계

| 코드 | 주제 | 핵심 키워드 |
|------|------|------------|
| A | 핵심 철학 + 병렬 | Boris Cherny, CEO 마인드셋, Opus, 15세션 |
| B | CLAUDE.md + 컨텍스트 | Lazy Loading, /memory, 토큰, MCP 관리 |
| C | 워크플로우 + Plan | TDD, WAT, SDD, TODO.md, 교차 AI |
| D | Skills + Subagents | 스킬 구조, 에이전트, Ralph Loop |
| E | 커맨드 + Hooks + 단축키 | 커스텀 커맨드, 훅, 키보드 |
| F | Cowork + MCP + 고급 | 음성입력, VS Code, NotebookLM |
