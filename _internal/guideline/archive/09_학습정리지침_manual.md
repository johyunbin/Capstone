# [09] 학습정리지침 (MANUAL)

> 대상: Capstone 프로젝트 | 모드: 수동 (Phase별 정지, 사용자 확인 후 진행)
> 마지막 실행: —

## 사용법

1. "학습정리 수동" 입력
2. Phase 0 실행 → 결과 보고 → **정지**
3. `/clear` 후 "Phase N 이어가줘"

### /clear vs /compact

| | /clear | /compact |
|---|---|---|
| 컨텍스트 | 100% 확보 | ~70% 확보 |
| 추천 용도 | **Phase 전환** (추천) | Phase 내부 보조 |

---

## Phase 체크리스트

> 상세 스크립트는 `09_학습정리지침_auto.md` 참조.

### Phase 0: 인벤토리 수집 (1분)
- [ ] learning/ 폴더 파일 수 확인
- [ ] 기존 정리 상태 확인 (Apple Notes, 메모리)
- [ ] guideline/PHASE_STATE_09_학습정리.md 생성

✅ Phase 0 완료 → 결과 보고 → 정지
→ 사용자: `/clear` 후 "Phase 1 이어가줘"

### Phase 1: 전수 읽기 (10~15분)
- [ ] 대상 스크립트/자료 전문 읽기
- [ ] 핵심 인사이트 추출
- [ ] 출처 기록
- [ ] PHASE_STATE 업데이트

✅ Phase 1 완료 → 정지
→ 사용자: `/clear` 후 "Phase 2 이어가줘"

### Phase 2: 주제별 분류 및 핵심 추출 (5분)
- [ ] A~F 분류 체계 적용
- [ ] 구체적 정보 보존 (명령어, 설정값, 경로)
- [ ] 추상화하지 않음
- [ ] PHASE_STATE 업데이트

✅ Phase 2 완료 → 정지
→ 사용자: `/clear` 후 "Phase 3 이어가줘"

### Phase 3: Apple Notes 저장 (3분)
- [ ] 주제별 노트 생성/업데이트
- [ ] Trading 양식 준수 (h1/부제/섹션/본문 스타일)
- [ ] PHASE_STATE 업데이트

✅ Phase 3 완료 → 정지
→ 사용자: `/clear` 후 "Phase 4 이어가줘"

### Phase 4: 메모리 + 전역 지침 반영 (2분)
- [ ] memory/reference 파일 업데이트
- [ ] ~/.claude/CLAUDE.md 활용 원칙 반영 (해당 시)
- [ ] PHASE_STATE 업데이트

✅ Phase 4 완료 → 정지
→ 사용자: `/clear` 후 "Phase 5 이어가줘"

### Phase 5: 완료 보고 (1분)
- [ ] 정리 결과 요약
- [ ] PHASE_STATE 최종 업데이트

✅ **학습정리 완료**

---

## 핵심 원칙

1. **전수 읽기**: 모든 글자를 읽는다
2. **출처 보존**: 누가 말했는지, 어떤 스크립트에서 나왔는지
3. **구체적 보존**: 명령어/설정값/경로 추상화 금지
4. **주제별 분리**: 거대한 단일 문서가 아닌 주제별 분할

## 분류 체계

| 코드 | 주제 |
|------|------|
| A | 핵심 철학 + 병렬 |
| B | CLAUDE.md + 컨텍스트 |
| C | 워크플로우 + Plan |
| D | Skills + Subagents |
| E | 커맨드 + Hooks + 단축키 |
| F | Cowork + MCP + 고급 |
