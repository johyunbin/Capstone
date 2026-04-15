# [10] Claude Code 활용 지침 (AUTO)

> 대상: 모든 프로젝트 | 모드: 자동 실행 (전권 위임)
> 목적: Claude Code를 최대 효율로 활용하여 개발 생산성을 극대화
> 출처: 25개 한국어 + 31개 영문 영상 트랜스크립트 전문 분석
>       (Boris Cherny, Meta SE, 커서맛피아 최수민, Cal/Anthropic 등)

## 실행 방법

### A. Claude Code 대화형

"활용 자동" 또는 "CC 점검" 입력 → CLAUDE.md 트리거 → 이 파일 자동 로드 → Phase 순차 진행

---

## Phase 구성

### Phase 0: 현재 상태 진단 (3분)

현재 Claude Code 환경을 점검하고 개선점을 찾는다.

**자동 실행:**
1. CLAUDE.md 품질 평가
   - 길이 적정성 (~300줄 이하)
   - 구조: What/Why/How 3계층 존재 여부
   - 검증 루프 (빌드/테스트/린트) 명시 여부
   - "절대 하지 마"/"항상 해" 규칙 존재 여부
   - Lazy Loading 적용 여부 (상세는 별도 .md로 분리했는가?)
2. 메모리 파일 감사
   - `memory/MEMORY.md` 인덱스 정합성
   - 오래된/중복 메모리 식별
3. 스킬/에이전트 목록 확인
   - 등록된 스킬 수 및 활용도
   - 커스텀 에이전트 목록
4. MCP 서버 점검
   - `/mcp` 출력 확인
   - 불필요한 MCP 식별 (노션/리니어 등 토큰 과다 소비 주의)

**산출물:** `logs/claude_code_audit_YYYYMMDD.md`

---

### Phase 1: CLAUDE.md 최적화 (5분)

CLAUDE.md의 품질을 높여 모든 후속 작업의 기반을 강화한다.

**자동 실행:**
1. Progressive Disclosure (Lazy Loading) 적용
   - CLAUDE.md에 인덱스만 유지
   - 상세 내용은 `docs/` 하위 .md로 분리
   - 예: `docs/architecture.md`, `docs/style_guide.md`
   - "CLAUDE.md에 API 50개 나열 → 경로만 기재" (메타 엔지니어)
2. 검증 루프 강화
   ```
   # 반드시 포함:
   빌드: python3 -m pytest tests/ -v --tb=short
   린트: (있으면 명시)
   타입: (있으면 명시)
   ```
3. Self-modifying 패턴 확인 (봉리 학습)
   - "Claude가 잘못하면 → CLAUDE.md에 실수 기록" 메커니즘 존재 여부
   - "시간이 갈수록 프로젝트에 맞게 진화" — 보리스
4. 폴더별 CLAUDE.md 분리 여부
   - 프로젝트가 크면 `apps/api/CLAUDE.md`, `web/CLAUDE.md` 등 분리 검토
5. 불필요한 내용 제거
   - 코드에서 유추 가능한 내용 삭제
   - 중복 지시 통합

**산출물:** 업데이트된 CLAUDE.md + 분리된 .md 파일들

---

### Phase 2: 컨텍스트 전략 점검 (5분)

컨텍스트 윈도우 사용 효율을 점검하고 낭비를 줄인다.

**자동 실행:**
1. `/context` 실행 → 토큰 사용량 분석
2. MCP 토큰 소비량 확인 → 과다 소비 MCP 식별
   - CLI + Skills 조합 대안 검토
3. 세션 전략 검토
   - Plan → Clear → Execute 패턴 적용 여부
   - "한 세션 = 한 기능" 준수 여부
   - "신선한 컨텍스트가 부풀어진 컨텍스트보다 낫다"
4. 스킬 메타데이터 최적화
   - 트리거 설명 정확성 확인
   - 불필요한 상시 로딩 제거
5. 무거운 작업 오프로드 상태
   - 대용량 데이터 직접 처리 → 스크립트 오프로드로 전환했는가?

**산출물:** 컨텍스트 최적화 리포트

---

### Phase 3: 워크플로우 자동화 점검 (5분)

반복 작업을 스킬/커맨드/훅으로 자동화할 수 있는지 점검한다.

**자동 실행:**
1. 반복 패턴 식별
   - 최근 세션에서 자주 사용한 프롬프트/명령어 분석
   - 2회 이상 반복 → 커맨드화 (.claude/commands/)
   - 일관된 품질 필요 → 스킬화 (.claude/skills/)
2. Hooks 활용도 점검
   - PreToolUse/PostToolUse 훅 설정 확인
   - 자동 포맷/린트/가드레일 적용 여부
   - 완료 알림 훅 설정 여부 (병렬 작업 시 필수)
3. 병렬 개발 환경 점검
   - Git Worktree 활용 가능성
   - Sub-agent 설정 상태
   - "Sub-agents: 작업에 할당 (역할에 할당 금지)" — 보리스
4. 개선 제안 생성
   - 새 스킬 제안 (3개 이내)
   - 새 훅 제안 (2개 이내)
   - 새 커맨드 제안 (3개 이내)

**산출물:** 자동화 개선 제안서

---

### Phase 4: 구현 (10분)

Phase 0-3에서 발견된 개선점을 즉시 적용한다.

**자동 실행:**
1. CLAUDE.md 수정 적용
2. 새 스킬 생성 (제안된 것 중 우선순위 상위)
3. 훅 설정 추가
4. 불필요한 MCP 제거
5. 메모리 정리 (오래된/중복 삭제)
6. 커스텀 커맨드 생성

**산출물:** 변경된 파일 목록 + diff 요약

---

### Phase 5: 검증 + 기록 (3분)

변경사항이 정상 동작하는지 확인하고 기록한다.

**자동 실행:**
1. Claude Code 새 세션에서 CLAUDE.md 로딩 테스트
2. 수정된 스킬 트리거 테스트
3. 훅 동작 확인
4. 결과 기록
   - 메모리 업데이트
   - 변경 로그 작성
5. 커밋 (사용자 요청 시)

**산출물:** 검증 결과 + 변경 로그

---

## 핵심 원칙 (전 Phase 공통)

### A. Boris Cherny (Head of Claude Code) — 직접 언급

**5대 원칙:**
1. **스스로 확인하게 해라** — 검증 수단 제공 → 품질 2~3배 향상
2. **계획을 먼저 세워라** — Plan 모드 80% 사용
3. **동시에 여러 개 돌려라** — 로컬 5 + 웹 10 = 15세션
4. **CLAUDE.md에 투자해라** — 실수 기록 = 봉리 학습
5. **단축 명령어를 써라** — 2회+ 반복 → 커맨드/스킬

**철학:**
- "Simple Thing That Works" — 스캐폴딩 최소화, 모델에게 도구+목표만 제공
- "Build for the Model 6 Months Out" — 현재가 아닌 미래 모델 기준 설계
- "The Bitter Lesson" — 범용 모델 > 특수 솔루션
- "기본 설정이 놀랍도록 그대로. 맞춤은 필요할 때만"

### B. 컨텍스트 관리

- 50% 초과 시 품질 저하 → `/compact` 또는 새 세션
- MCP는 필요한 것만 (컨텍스트 윈도우 폭파 주의)
- 빙산 기법: 상시 로드 최소화, 나머지는 도구로 접근
- Lazy Loading: CLAUDE.md에 경로만, 상세는 별도 .md
- 무거운 데이터 → 스크립트 작성 → 결과만 받기

### C. 프롬프팅

- Plan Mode로 시작 (Boris: 80% Plan Mode)
- Ask User Question Tool로 요구사항 정밀 인터뷰
- Escape = 최고의 도구 (잘못된 방향 즉시 중단)
- `think hard` / `ultra think`으로 사고 깊이 제어
- 에러 로그 → 해석 없이 스택 트레이스 통째로 전달
- Thinking 과정에서 잘못된 가정 → 즉시 Escape

### D. 병렬 개발

- 다중 인스턴스 (iTerm/tmux) — 완료 알림 훅 필수
- Git Worktrees로 독립 작업
- Sub-agents: 작업에 할당 (역할에 할당 금지)
- CEO 마인드셋 — 기획/프론트/백엔드/QA를 에이전트로 분담 (커서맛피아)

### E. 실전 패턴

- **TDD 루프**: 변경 → 테스트 → 커밋 → 반복 (안전망)
- **Ralph Loop**: 코드→테스트→실패→수정 무한 반복 (될 때까지)
- **TODO.md**: 프로젝트 전체 작업 관리, 세션 종료 시 업데이트
- **SDD**: 코드 전에 설계서(spec) 먼저, "이대로 만들어줘"
- **WAT**: Workflow(글로 정의) + Agents(병렬) + Tools(작은 스크립트)
- **교차 AI**: Claude 계획을 GPT/Gemini에 비평 요청

### F. 고급 패턴

- Auto-Research: 가설→실험→측정→승자→변형 루프
- Sub-Agent Verification: 작성→리뷰(fresh)→해결
- Prompt Contract: Goal/Constraints/Format/Failure 4섹션
- Whisper Flow: 음성 입력으로 풍부한 컨텍스트 전달

---

## 단축키 레퍼런스

```
Shift+Tab     모드 전환 (Normal/Auto-accept/Plan)
Ctrl+J        줄바꿈
Escape 1회    중단 / 2회 포크
Ctrl+C ×2     종료
@             파일 참조
#             CLAUDE.md에 추가
Shift+드래그  파일/이미지 업로드
```

```
/init     CLAUDE.md 생성    /clear    초기화
/compact  압축              /context  토큰 확인
/model    모델 변경         /mcp      MCP 관리
/memory   메모리 관리       /rename   세션 이름
/permissions  권한 관리     /ide      IDE 연동
```

```
claude              새 세션
claude --continue   마지막 이어가기
claude --resume     히스토리에서 선택
```

---

## 참조

- kr 분석: `memory/reference_claude_code_kr_mastery.md`
- us 분석: `memory/reference_claude_code_mastery.md`
- Apple 메모: Claude 폴더 (6+6 노트)
- 원본: `learning/kr/` (25개) + `learning/claude-code/us/` (31개)
