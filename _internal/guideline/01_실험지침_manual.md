# [02] 실험지침 (MANUAL)

> 대상: Capstone 프로젝트 | 모드: 수동 (Phase별 정지, 사용자 확인 후 진행)
> 마지막 실행: —

## 사용법

1. "실험 수동" 입력
2. Phase 0 실행 → 결과 보고 → **정지**
3. `/clear` 후 "Phase N 이어가줘"

### /clear vs /compact

| | /clear | /compact |
|---|---|---|
| 컨텍스트 | 100% 확보 | ~70% 확보 |
| 추천 용도 | **Phase 전환** (추천) | Phase 내부 보조 |

---

## Phase 체크리스트

> 상세 스크립트는 `01_실험지침_auto.md` 참조.

### Phase 0: 환경 확인 (3분)
- [ ] PostgreSQL + pgvector 버전 확인
- [ ] DuckDB 버전 확인
- [ ] Python 패키지 확인 (numpy, faiss, matplotlib 등)
- [ ] Exqutor 디렉토리 확인
- [ ] guideline/PHASE_STATE_01_실험.md 생성

✅ Phase 0 완료 → 결과 보고 → 정지
→ 사용자: `/clear` 후 "Phase 1 이어가줘"

### Phase 1: 환경 구축 (첫 실행 시만, 30분)
- [ ] pgvector 설치 + 확장 활성화
- [ ] DuckDB 설치
- [ ] Exqutor 패치 빌드
- [ ] PHASE_STATE 업데이트

✅ Phase 1 완료 → 정지
→ 사용자: `/clear` 후 "Phase 2 이어가줘"

### Phase 2: 데이터셋 준비 (15분)
- [ ] 설계안에서 데이터셋 목록 확인
- [ ] 다운로드 + 검증 (행 수/차원/형식)
- [ ] DB 적재 + 인덱스 생성
- [ ] VACUUM ANALYZE
- [ ] PHASE_STATE 업데이트

✅ Phase 2 완료 → 정지
→ 사용자: `/clear` 후 "Phase 3 이어가줘"

### Phase 3: 벤치마크 실행 (30분+)
- [ ] 선택도 sweep: 0.001 ~ 0.9
- [ ] EXPLAIN ANALYZE 캡처
- [ ] warmup 실행 후 반복 측정
- [ ] CSV로 결과 저장
- [ ] PHASE_STATE 업데이트

✅ Phase 3 완료 → 정지
→ 사용자: `/clear` 후 "Phase 4 이어가줘"

### Phase 4: 결과 수집 + 분석 (15분)
- [ ] CSV 집계
- [ ] Exqutor 전/후 비교 (speedup ratio)
- [ ] 통계 요약
- [ ] PHASE_STATE 업데이트

✅ Phase 4 완료 → 정지
→ 사용자: `/clear` 후 "Phase 5 이어가줘"

### Phase 5: 시각화 + 로그 기록 (10분)
- [ ] 차트 생성 (matplotlib/seaborn)
- [ ] 실험 로그 작성 (`experiments/logs/YYYYMMDD_제목.md`)
- [ ] 환경 정보 기록 (PG 버전, HW 스펙 등)
- [ ] PHASE_STATE 최종 업데이트

✅ **실험 완료**

---

## 자주 하는 실수

| 실수 | 올바른 방법 |
|------|------------|
| 인덱스 없이 벤치마크 | 인덱스 생성 후 VACUUM ANALYZE |
| cold cache에서 측정 | 첫 실행은 warmup으로 버림 |
| 결과 수동 메모 | CSV/JSON으로 구조화 저장 |
| 환경 정보 미기록 | 실험 로그에 버전/HW 스펙 필수 |

## 관련 지침

| 지침 | 연동 관계 |
|------|----------|
| 연구설계지침 | 실험 설계서를 받아서 실행 |
| 문서생성지침 | 실험 결과 보고서 PDF 변환 |
| 제출물지침 | 실험 결과를 보고서에 편입 |
| 주간보고지침 | 실험 진행 상태 반영 |
