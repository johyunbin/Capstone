# PHASE_STATE — 10_클로드코드활용지침

> run_id: 20260328_manual_6guidelines_v3
> 마지막 업데이트: 2026-03-28

## Phase 0: 현재 상태 진단 결과

### 1. CLAUDE.md 품질 평가

| 항목 | 프로젝트 CLAUDE.md (258줄) | 글로벌 CLAUDE.md (103줄) |
|------|--------------------------|------------------------|
| 길이 | 적정 (258줄) | 적정 (103줄) |
| 구조 | ✅ 섹션별 분리 잘 됨 | ✅ 간결한 규칙 모음 |
| 검증 루프 | ⚠️ 명시적 검증 루프 없음 | ⚠️ "자기 검증" 언급하나 구체 스크립트 없음 |
| Lazy Loading | ✅ guideline/ 분리 | ✅ 상세 별도 .md 분리 권고 |
| 규칙 중복 | ⚠️ Git 동기화·카카오톡 처리 양쪽 중복 | — |

**개선 포인트**:
- 프로젝트 CLAUDE.md에 검증 루프(테스트 명령, 빌드 확인 등) 섹션 추가 필요
- 글로벌↔프로젝트 간 Git 동기화/카카오톡 중복 정리 가능

### 2. 메모리 파일 감사

| 항목 | 결과 |
|------|------|
| 총 파일 수 | 22개 (MEMORY.md 포함) |
| 인덱스 정합성 | ✅ MEMORY.md 21항목 = 실제 21 .md 파일 |
| user 타입 | 1개 (user_profile) |
| feedback 타입 | 10개 |
| project 타입 | 5개 |
| reference 타입 | 5개 |
| 오래된/중복 | ⚠️ project_session_0328.md — 오늘 한정 세션 로그, 향후 불필요 |
| 내용 이슈 | project_notion_cleanup.md에 대량 페이지 ID — 실행 데이터 성격 |

### 3. 스킬 목록 (6개)

| 스킬 | 역할 | 비고 |
|------|------|------|
| paper-analysis | 논문 분석 3종 문서 생성 | guideline/01 흡수 |
| submission-prep | 제출물 준비 | guideline/03 흡수 |
| experiment-log | 실험 기록 | guideline/02 보조 |
| progress-brief | 진행 현황 브리핑 | 독립 유틸 |
| weekly-log | 주간 작업일지 | guideline/05 보조 |
| project-health | 헬스체크 | guideline/00 보조 |

→ 스킬 6개는 지침에 흡수되었으나 **하위호환용으로 유지 중** — 문제 없음

### 4. 에이전트 (1개)

- `document-validator.md` — 분석문서 3종(md/pdf/docx) 정합성 검증

### 5. MCP 서버

- 프로젝트 설정: **0개** (글로벌에서 관리)
- 컨텍스트 소비: 시스템 제공 MCP만 사용 중 (Notion, Slack 등 외부 통합)

### 6. Hooks (3개)

| Hook | 트리거 | 역할 |
|------|--------|------|
| session-init.sh | SessionStart | 프로젝트 상태 출력 |
| save-session-state.sh | PreCompact | 세션 상태 저장 |
| stop-save.sh | Stop | 종료 시 상태 저장 |

### 7. 권한 설정

- `defaultMode: bypassPermissions` — 전권 위임 ✅
- `skipDangerousModePermissionPrompt: true` ✅
- 24개 allow 패턴 — 충분

## Phase 1: CLAUDE.md 최적화 결과

### Lazy Loading 분리 계획 (약 -75줄)
1. **디렉토리 구조** (40줄) → 삭제 (코드에서 유추 가능)
2. **실험 설계 초안** (18줄) → 설계안 파일 참조 1줄로 대체
3. **수동 모드 상세 규칙** (12줄) → 2줄 요약으로 축약
4. **PDF 스타일 규칙 상세** (7줄) → 삭제 (스크립트에 구현됨)
5. **카카오톡 처리** (5줄) → 삭제 (글로벌 CLAUDE.md가 라우팅 담당)

### 검증 루프 추가 (신규)
- PDF 변환 검증: `python3 scripts/md2pdf.py <file> && open <file.pdf>`
- 문서 정합성: document-validator 에이전트
- Git 상태: `git status && git diff --stat`
- 실험 환경: pgvector 확장 확인 쿼리

### 글로벌↔프로젝트 중복 정리
- Git 명령어: 글로벌에서 Capstone 부분 축약
- 카카오톡: 글로벌이 라우팅 담당, 프로젝트에서 삭제

## Phase 2: 컨텍스트 전략 점검 결과

### 토큰 소비 분석
- 프로젝트 CLAUDE.md ~2,000 토큰 → Phase 1 계획대로 ~75줄 삭감 예정
- MCP deferred tools 300개+ → 글로벌 설정이라 프로젝트에서 제거 불가, deferred라 실제 낭비 제한적
- 메모리 인덱스 ~400 토큰 — 적정

### MCP 과다 소비
- Capstone에서 실사용 MCP: Notion, Apple Notes, Google Calendar (3개)
- 나머지 다수(Spotify, Figma, Canva, HubSpot 등)는 글로벌 설정 — 프로젝트 조치 불가

### 세션 전략
- Plan → Clear → Execute 패턴 ✅ 지침 시스템이 구조적으로 보장
- 한 세션 = 한 기능 ✅
- 50% 초과 시 /compact ✅

### 오프로드 상태
- MD→PDF, 논문 배치, git 작업 — 모두 스크립트/훅으로 오프로드 완료
- 실험 단계 진입 시 데이터셋/벤치마크 스크립트 추가 필요

### 결론
- 컨텍스트 전략 **양호** — 구조적 개선 여지 적음
- Phase 4에서 CLAUDE.md 축약 적용

## Phase 3: 워크플로우 자동화 점검 결과

### 반복 패턴 → 자동화 후보
1. **지침 Phase 재개** — 매번 PHASE_STATE 경로 찾기 반복 → `/resume` 커맨드 후보
2. **git sync** — add+commit+push 수동 → `/sync` 커맨드 후보
3. 논문 분석/MD→PDF/제출물 — 이미 스킬+스크립트로 자동화 완료

### Hooks 점검
- `session-init.sh`: ✅ 잘 동작
- `save-session-state.sh` / `stop-save.sh`: ⚠️ **경로 버그** — `Research` (대문자) → 실제 `research/summaries` (소문자)
- Notification 훅: 미설정 (선택적 추가 가능)

### 병렬 환경
- Worktree/Agent 권한 ✅ 준비 완료
- 실험 단계에서 pgvector 빌드 + 벤치마크를 Worktree 격리로 활용 예정

### 개선 제안 요약
- **커맨드 2개**: `/resume` (Phase 재개), `/sync` (git 원클릭)
- **훅 수정 2개**: 경로 버그 수정, Notification 추가 (선택)
- **스킬 추가 불필요** — 기존 6개 충분, 실험 시 experiment-log 업데이트 정도

## Phase 4: 구현 결과

### CLAUDE.md 축약 (258줄 → 184줄, −74줄)
- ✅ 디렉토리 구조 삭제 (40줄)
- ✅ 실험 설계 초안 → 설계안 참조 1줄
- ✅ 수동 모드 상세 → 2줄 요약
- ✅ PDF 스타일 규칙 상세 삭제
- ✅ 카카오톡 처리 삭제 (글로벌에서 라우팅)
- ✅ 검증 루프 섹션 신규 추가

### 훅 경로 버그 수정
- ✅ `save-session-state.sh`: `Research` → `research/summaries`
- ✅ `stop-save.sh`: `Research` → `research/summaries`

### 커맨드 생성
- ✅ `/resume` — Phase 재개 (PHASE_STATE.json 기반 자동 감지)
- ✅ `/sync` — git add+commit+push 원클릭

### MCP 정리
- ⏭️ 글로벌 설정이라 프로젝트에서 조치 불가 — 스킵

## Phase 진행 상태

| Phase | 내용 | 상태 |
|-------|------|------|
| 0 | 현재 상태 진단 | ✅ 완료 |
| 1 | CLAUDE.md 최적화 | ✅ 완료 |
| 2 | 컨텍스트 전략 점검 | ✅ 완료 |
| 3 | 워크플로우 자동화 점검 | ✅ 완료 |
| 4 | 구현 | ✅ 완료 |
| 5 | 검증 + 기록 | ✅ 완료 |

## Phase 5: 검증 + 기록 결과

### 검증 항목

| 항목 | 결과 |
|------|------|
| CLAUDE.md 줄 수 | 184줄 (258→184, −74줄) ✅ |
| 글로벌 CLAUDE.md | 103줄 ✅ |
| `/resume` 커맨드 | 존재, 내용 정상 ✅ |
| `/sync` 커맨드 | 존재, 내용 정상 ✅ |
| 훅 경로 버그 | `research/summaries` 수정 완료 ✅ |
| 검증 루프 섹션 | CLAUDE.md 154줄에 존재 ✅ |

### 10_클로드코드활용지침 전체 완료 요약

- Phase 0: 현재 상태 진단 — CLAUDE.md/메모리/스킬/MCP/훅/권한 전수 점검
- Phase 1: CLAUDE.md 최적화 — Lazy Loading 분리 계획 (−75줄), 검증 루프 추가 설계
- Phase 2: 컨텍스트 전략 점검 — 토큰 소비 분석, MCP 과다 식별, 세션 전략 확인
- Phase 3: 워크플로우 자동화 — 반복 패턴→커맨드 2개, 훅 경로 버그 발견
- Phase 4: 구현 — CLAUDE.md 축약, 훅 수정, `/resume`+`/sync` 커맨드 생성
- Phase 5: 검증 — 전 항목 정상 동작 확인
