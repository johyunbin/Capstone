# [04] 문서생성지침 (MANUAL)

> 대상: Capstone 프로젝트 | 모드: 수동 (Phase별 정지, 사용자 확인 후 진행)
> 마지막 실행: —

## 사용법

1. "문서생성 수동" 입력
2. Phase 0 실행 → 결과 보고 → **정지**
3. `/clear` 후 "Phase N 이어가줘"

### /clear vs /compact

| | /clear | /compact |
|---|---|---|
| 컨텍스트 | 100% 확보 | ~70% 확보 |
| 추천 용도 | **Phase 전환** (추천) | Phase 내부 보조 |

---

## Phase 체크리스트

> 상세 스크립트는 `04_문서생성지침_auto.md` 참조.

### Phase 0: 환경 확인 (1분)
- [ ] markdown + websocket-client 설치 확인
- [ ] scripts/md2pdf.py 존재 확인
- [ ] Chrome 설치 확인
- [ ] guideline/PHASE_STATE_04_문서생성.md 생성

✅ Phase 0 완료 → 결과 보고 → 정지
→ 사용자: `/clear` 후 "Phase 1 이어가줘"

### Phase 1: 누락 PDF 탐지 (2분)
- [ ] analysis/ md↔pdf 대응 확인
- [ ] summaries/ md↔pdf 대응 확인
- [ ] plans/ md↔pdf 대응 확인
- [ ] 누락 목록 출력
- [ ] PHASE_STATE 업데이트

✅ Phase 1 완료 → 정지
→ 사용자: `/clear` 후 "Phase 2 이어가줘"

### Phase 2: PDF 변환 실행 (5분)
- [ ] 누락 파일 순차 변환 (`scripts/md2pdf.py`)
- [ ] 변환 성공/실패 리포트
- [ ] PHASE_STATE 업데이트

> **절대 fpdf2 사용 금지** — Chrome CDP만 사용

✅ Phase 2 완료 → 정지
→ 사용자: `/clear` 후 "Phase 3 이어가줘"

### Phase 3: 품질 검증 (3분)
- [ ] 생성된 PDF 폰트 검사 (AppleSDGothicNeo 확인)
- [ ] 한글 렌더링 정상 여부
- [ ] 페이지 번호/헤더 스타일 확인
- [ ] PHASE_STATE 업데이트

✅ Phase 3 완료 → 정지
→ 사용자: `/clear` 후 "Phase 4 이어가줘"

### Phase 4: docx 변환 (선택, 5분)
- [ ] 제출용 docx 필요 시 pandoc 변환
- [ ] 양식 템플릿 적용 (있으면)
- [ ] PHASE_STATE 업데이트

✅ Phase 4 완료 → 정지
→ 사용자: `/clear` 후 "Phase 5 이어가줘"

### Phase 5: 종합 리포트 (1분)
- [ ] 변환 결과 테이블 (성공/실패/스킵)
- [ ] PHASE_STATE 최종 업데이트

✅ **문서생성 완료**

---

## 자주 하는 실수

| 실수 | 올바른 방법 |
|------|------------|
| fpdf2로 PDF 생성 | Chrome CDP만 사용 (`scripts/md2pdf.py`) |
| 여러 파일 동시 변환 | 순차 실행 (Chrome 포트 충돌 방지) |
| 변환 후 확인 안 함 | 최소 1개는 열어서 한글/레이아웃 확인 |
| 한글 파일명 이스케이프 누락 | bash에서 따옴표 또는 `\` 사용 |

## 관련 지침

| 지침 | 연동 관계 |
|------|----------|
| 점검지침 | PDF 폰트 검증 → 깨짐 발견 시 재생성 요청 |
| 논문분석지침 | 분석 md 작성 후 PDF 변환 |
| 제출물지침 | 제출용 문서 PDF/docx 변환 |
| 주간보고지침 | 주간보고 PDF 변환 |
