# [00] 점검지침 (MANUAL)

> 대상: Capstone 프로젝트 | 모드: 수동 (Phase별 정지, 사용자 확인 후 진행)
> 마지막 실행: 2026-03-28 — Phase 0~7 전체 완료

## 사용법

1. Claude Code에서 "점검 수동" 입력
2. Phase 0 실행 → 결과 보고 → **정지**
3. 사용자가 `/clear` 또는 `/compact` 실행
4. "Phase N 이어가줘" 입력 → guideline/PHASE_STATE_00_점검.md 읽고 다음 Phase

### /clear vs /compact

| | /clear | /compact |
|---|---|---|
| 컨텍스트 | 100% 확보 | ~70% 확보 |
| 이전 맥락 | 완전 삭제 | 요약 유지 |
| 추천 용도 | **Phase 전환** (추천) | Phase 내부 보조 |

**추천:** Phase 전환마다 `/clear`. Phase 내에서 컨텍스트 부족하면 `/compact`.

---

## Phase 체크리스트

> Phase 번호는 `00_점검지침_auto.md`와 동일. 상세 스크립트는 auto 참조.

### Phase 0: 인벤토리 수집 (2분)
- [ ] research/analysis/ — md 수, pdf 수
- [ ] research/summaries/ — md 수, pdf 수
- [ ] research/papers/ — 원논문 PDF 수
- [ ] submission/ — 제출물 파일 수
- [ ] plans/ — 문서 수 및 파일명 형식 확인
- [ ] guideline/PHASE_STATE_00_점검.md 생성

✅ Phase 0 완료 → 결과 보고 → 정지
→ 사용자: `/clear` 후 "Phase 1 이어가줘"

### Phase 1: 2종 세트 완성도 검증 (3분)
- [ ] analysis/ 내 모든 .md에 대해 동일 이름 .pdf 존재 확인
- [ ] summaries/ 내 모든 .md에 대해 동일 이름 .pdf 존재 확인
- [ ] 누락 파일 목록 출력
- [ ] PHASE_STATE 업데이트

✅ Phase 1 완료 → 정지
→ 사용자: `/clear` 후 "Phase 2 이어가줘"

### Phase 2: PDF 폰트 검증 (3분)
- [ ] pypdf 설치 확인
- [ ] analysis/ + summaries/ PDF 폰트 검사
- [ ] 결과: 정상 수 / 비정상 수 / 비정상 파일 목록
- [ ] PHASE_STATE 업데이트

✅ Phase 2 완료 → 정지
→ 사용자: `/clear` 후 "Phase 3 이어가줘"

### Phase 3: 파일명 규칙 검증 (2분)
- [ ] analysis/: `(번호) 제목.확장자` 패턴
- [ ] summaries/: `[번호] 제목 총정리.확장자` 패턴
- [ ] 비규격 파일 목록 출력
- [ ] PHASE_STATE 업데이트

✅ Phase 3 완료 → 정지
→ 사용자: `/clear` 후 "Phase 4 이어가줘"

### Phase 4: orphan 및 중복 검사 (2분)
- [ ] .tmp, .bak, .swp 파일 탐지
- [ ] .DS_Store 수 카운트 + .gitignore 포함 확인
- [ ] papers/ 와 다른 폴더 간 PDF 중복 확인
- [ ] PHASE_STATE 업데이트

✅ Phase 4 완료 → 정지
→ 사용자: `/clear` 후 "Phase 5 이어가줘"

### Phase 5: 원논문 ↔ 총정리 대응 확인 (2분)
- [ ] summaries/ 번호 목록 추출
- [ ] 번호 범위 내 빈 번호(gap) 확인
- [ ] papers/ 파일 수 vs summaries/ 고유 번호 수 비교
- [ ] PHASE_STATE 업데이트

✅ Phase 5 완료 → 정지
→ 사용자: `/clear` 후 "Phase 6 이어가줘"

### Phase 6: 일정 + 사이트 점검 (2분)
- [ ] 캡스톤 사이트 공지사항 확인 → 새 항목 유무
- [ ] CLAUDE.md 일정표에서 다음 마감 + D-day 계산
- [ ] 메모리와 CLAUDE.md 일정 일치 여부 확인
- [ ] PHASE_STATE 업데이트

✅ Phase 6 완료 → 정지
→ 사용자: `/clear` 후 "Phase 7 이어가줘"

### Phase 7: 종합 리포트 (1분)
- [ ] 전 Phase 결과 테이블 생성
- [ ] 즉시 조치 필요 항목에 담당 지침 안내
- [ ] PHASE_STATE 최종 업데이트 (완료 시각, 총 발견/수정)
- [ ] git commit + push (선택)

✅ **점검 완료**

---

## Phase 합치기 가이드

컨텍스트 여유가 있으면 합쳐서 실행:
- **Phase 0+1**: 인벤토리 + 2종세트 (~5분)
- **Phase 2+3**: PDF폰트 + 파일명 (~5분)
- **Phase 4+5**: orphan + 원논문대응 (~4분)
- **Phase 6+7**: 일정 + 종합 (~3분)

## 지난 실행 이력

| 날짜 | 결과 | 발견/수정 |
|------|------|-----------|
| 2026-03-28 | ✅ 전체 완료 (Phase 0~7) | PDF 9건 재생성 (NotoSansKR→AppleSDGothicNeo) |

## 상세 참조

모듈별 상세 스크립트 필요 시:
```
Read guideline/00_점검지침_auto.md 의 해당 Phase 섹션
```

## 관련 지침

| 지침 | 연동 관계 |
|------|----------|
| 문서생성지침 | PDF 깨짐 발견 → 재생성 요청 |
| 논문분석지침 | 2종 세트 누락 발견 → 분석 문서 작성 요청 |
| 제출물지침 | 일정 마감 임박 발견 → 제출물 준비 요청 |
| 주간보고지침 | 점검 결과를 주간 보고에 반영 |
