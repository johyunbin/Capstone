# [10] Claude Code 활용 지침 (MANUAL)

> 대상: 모든 프로젝트 | 모드: 수동 (Phase별 정지, 사용자 확인 후 진행)
> 목적: Claude Code를 최대 효율로 활용하여 개발 생산성을 극대화
> 출처: 25개 한국어 + 31개 영문 영상 트랜스크립트 전문 분석
> 마지막 실행: —

## 사용법

1. "활용 수동" 입력
2. Phase 0 실행 → 결과 보고 → **정지**
3. `/clear` 후 "Phase N 이어가줘"

### /clear vs /compact

| | /clear | /compact |
|---|---|---|
| 컨텍스트 | 100% 확보 | ~70% 확보 |
| 추천 용도 | **Phase 전환** (추천) | Phase 내부 보조 |

---

## Phase 체크리스트

> 상세 스크립트는 `10_클로드코드활용지침_auto.md` 참조.

### Phase 0: 현재 상태 진단 (3분)
- [ ] CLAUDE.md 품질 평가 (길이/구조/검증루프/규칙/Lazy Loading)
- [ ] 메모리 파일 감사 (인덱스 정합성, 오래된/중복)
- [ ] 스킬/에이전트 목록 확인
- [ ] MCP 서버 점검
- [ ] guideline/PHASE_STATE_10_활용.md 생성

✅ Phase 0 완료 → 결과 보고 → 정지
→ 사용자: `/clear` 후 "Phase 1 이어가줘"

### Phase 1: CLAUDE.md 최적화 (5분)
- [ ] Progressive Disclosure (Lazy Loading) 적용 계획
- [ ] 검증 루프 강화 방안
- [ ] 불필요 내용 제거 목록
- [ ] PHASE_STATE 업데이트

✅ Phase 1 완료 → 정지
→ 사용자: `/clear` 후 "Phase 2 이어가줘"

### Phase 2: 컨텍스트 전략 점검 (5분)
- [ ] `/context` 토큰 분석
- [ ] MCP 과다 소비 식별 + CLI 대안
- [ ] 세션 전략 (한 세션 = 한 기능)
- [ ] PHASE_STATE 업데이트

✅ Phase 2 완료 → 정지
→ 사용자: `/clear` 후 "Phase 3 이어가줘"

### Phase 3: 워크플로우 자동화 점검 (5분)
- [ ] 반복 패턴 식별 (커맨드/스킬 후보)
- [ ] Hooks 활용도 점검
- [ ] 병렬 개발 환경 점검 (Worktree/Sub-agent)
- [ ] 개선 제안 (스킬 3, 훅 2, 커맨드 3 이내)
- [ ] PHASE_STATE 업데이트

✅ Phase 3 완료 → 정지
→ 사용자: `/clear` 후 "Phase 4 이어가줘"

### Phase 4: 구현 (10분)
- [ ] CLAUDE.md 수정 (diff 표시 후 승인)
- [ ] 스킬 생성 (내용 확인 후 승인)
- [ ] 훅 설정 (설정값 확인 후 승인)
- [ ] MCP 정리 (제거 대상 확인 후 승인)
- [ ] PHASE_STATE 업데이트

> **각 변경마다 사용자 확인 대기**

✅ Phase 4 완료 → 정지
→ 사용자: `/clear` 후 "Phase 5 이어가줘"

### Phase 5: 검증 + 기록 (3분)
- [ ] CLAUDE.md 로딩 테스트
- [ ] 스킬 트리거 테스트
- [ ] 훅 동작 확인
- [ ] 결과 기록
- [ ] PHASE_STATE 최종 업데이트

✅ **활용 점검 완료** → 커밋 여부 사용자 결정

---

## 빠른 참조: 보리스 5대 원칙

| # | 원칙 | 핵심 |
|---|------|------|
| 1 | 스스로 확인하게 해라 | 검증 수단 제공 → 품질 2~3배 |
| 2 | 계획을 먼저 세워라 | Plan 모드 80% |
| 3 | 동시에 여러 개 돌려라 | 15세션 + 알림 훅 |
| 4 | CLAUDE.md에 투자해라 | 봉리 학습 |
| 5 | 단축 명령어를 써라 | 커맨드/스킬화 |

## 참조

- kr 분석: `memory/reference_claude_code_kr_mastery.md`
- Apple 메모: Claude 폴더 (6+6 노트)
- 원본: `learning/kr/` (25개) + `learning/claude-code/us/` (31개)
