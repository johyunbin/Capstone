# [05] 주간보고지침 (MANUAL)

> 대상: Capstone 프로젝트 | 모드: 수동 (Phase별 정지, 사용자 확인 후 진행)
> 마지막 실행: —

## 사용법

1. "주간보고 수동" 입력
2. Phase 0 실행 → 결과 보고 → **정지**
3. `/clear` 후 "Phase N 이어가줘"

### /clear vs /compact

| | /clear | /compact |
|---|---|---|
| 컨텍스트 | 100% 확보 | ~70% 확보 |
| 추천 용도 | **Phase 전환** (추천) | Phase 내부 보조 |

---

## Phase 체크리스트

> 상세 스크립트는 `05_주간보고지침_auto.md` 참조.

### Phase 0: 데이터 수집 (3분)
- [ ] 이번 주 커밋 확인 (`git log --since="1 week ago"`)
- [ ] 문서 변경 확인 (`-- research/` 필터)
- [ ] 분석 진행률 확인 (summaries/analysis/papers 수)
- [ ] 회의록 확인 (records/meetings/)
- [ ] guideline/PHASE_STATE_05_주간보고.md 생성

✅ Phase 0 완료 → 결과 보고 → 정지
→ 사용자: `/clear` 후 "Phase 1 이어가줘"

### Phase 1: 주간 요약 작성 (10분)
- [ ] 커밋 기반 핵심 작업 정리
- [ ] 문서 현황 수치
- [ ] 주요 성과/결정 사항
- [ ] PHASE_STATE 업데이트

✅ Phase 1 완료 → 정지
→ 사용자: `/clear` 후 "Phase 2 이어가줘"

### Phase 2: 노션 동기화 확인 (5분)
- [ ] Study Archive DB — 새 분석 문서 등록 여부
- [ ] 캡스톤 일정 DB — 완료 마감 상태
- [ ] 미반영 항목 업데이트
- [ ] PHASE_STATE 업데이트

✅ Phase 2 완료 → 정지
→ 사용자: `/clear` 후 "Phase 3 이어가줘"

### Phase 3: 다음 주 계획 (3분)
- [ ] CLAUDE.md 일정표에서 다음 마감 확인
- [ ] 우선순위 작업 나열
- [ ] 팀원 역할 분담
- [ ] 블로커 기술
- [ ] PHASE_STATE 업데이트

✅ Phase 3 완료 → 정지
→ 사용자: `/clear` 후 "Phase 4 이어가줘"

### Phase 4: 리포트 출력 (2분)
- [ ] `records/weekly/주간보고_YYYY-MM-DD.md` 저장
- [ ] PHASE_STATE 최종 업데이트

✅ **주간보고 완료**

---

## 자주 하는 실수

| 실수 | 올바른 방법 |
|------|------------|
| git log 기간 미지정 | `--since="1 week ago"` 필수 |
| 노션 동기화 건너뜀 | Study Archive + 일정 DB 둘 다 확인 |
| 다음 주 계획 누락 | 반드시 계획까지 포함 |
| 팀원 역할 분담 누락 | 4인 팀 기준으로 분담 명시 |

## 관련 지침

| 지침 | 연동 관계 |
|------|----------|
| 미팅지침 | 회의록을 주간보고에서 참조 |
| 점검지침 | 문서 현황 수치 활용 |
| 제출물지침 | 마감 일정을 다음 주 계획에 반영 |
| 논문분석지침 | 분석 진행률 포함 |
