# 제출물지침 (AUTO)

> 대상: Capstone 프로젝트 | 모드: 자동 실행 (전권 위임)
> 마지막 실행: 2026-05-08 22:00

## 본 연구 framing (5/16 단순화 — 제출물에 담는 연구 내용)

제출물(보고서·발표자료·자문내역서 등)에 연구 내용을 쓸 때는 현재 framing 을 따른다. 본 연구는 Exqutor 논문 재현이 아니라, **sample selection 단계 개입이 cardinality 추정 Q-error 에 미치는 영향을 전 데이터셋·전 조작 변인에 걸쳐 검증하는 실험**이다. 측정은 **B1(대조군) / CaseA(완전 대체) / CaseB(결합)** 3-way 로 짝지어 진행하며, 개입 지점은 sample selection 단계 한 곳이다(cardinality 추정 알고리즘과 AdaptiveState 식 1-6 은 paper 그대로 유지). 자세한 framing 은 `submission/_drafts/속도는벡터_본연구_narrative_v7_20260517.md` 를 base 로 한다.

## 자문 메일 발송 패턴

자문 메일 발송 시 **단독 vs 다중 분기**를 명확히 구분한다:

- **단독 발송**: 박성원 멘토 (임채림 석사) — 전문 자문 1인.
- **교수님 별도 발송**: 박광현 교수님 — 미팅 사전 brief. 최신 미팅 자료는 `submission/_drafts/박광현_5월22일_미팅/` 참조.

발송 전 체크리스트가 있으면 `submission/_drafts/` 의 자문메일 관련 문서를 참조한다.

## 제출물지침의 범위

**IS (이 지침이 하는 것):**
- 연구제안서, 수행계획서, 중간/최종 보고서 작성
- 연구지도확인서, 자문내역서, 자문컨택내역 작성 (**자문 메일 v4 박성원 멘토 단독 case 포함**)
- 물품구매/회의비 양식 작성
- templates/forms/ 양식 확인 및 적용
- templates/samples/ 예시 참조 (포맷, 분량, 내용 수준)
- 마감 D-day 계산 및 알림
- 일정 3곳 동기화 (CLAUDE.md 일정표 + 메모리 project_capstone.md + 노션 일정 DB)
- 캡스톤 사이트 제출 페이지(page_id=27) 양식 확인
- 기존 제출물(submission/) 스타일 참조
- 제출 완료 시 CLAUDE.md 일정표 상태 ✅ 업데이트

**IS NOT (이 지침이 하지 않는 것 → 담당 지침):**
- 중간/최종 발표 PPT, 포스터 → 발표지침
- 논문 분석 문서(총정리/시리즈) 작성 → 논문분석지침
- md→PDF 변환 실행 → 문서생성지침
- 사이트 공지 모니터링, 파일 무결성 점검 → 점검지침
- 실험 환경 구축, 벤치마크 실행 → 실험지침
- 카카오톡 회의록 작성 → 미팅지침

---

## Phase 구성

### Phase 0: 일정 확인 + 다음 마감 식별 (2분)

오늘 날짜 기준으로 CLAUDE.md 일정표를 파싱하여 가장 가까운 미완료 마감을 찾는다.

- [ ] CLAUDE.md `핵심 일정` 테이블 읽기
- [ ] ⬜ 상태인 항목 중 날짜순 정렬
- [ ] 가장 가까운 마감에 대해 D-day 계산
- [ ] 대상 제출물 식별 및 사용자에게 보고

D-day 계산:
```python
from datetime import date
# CLAUDE.md에서 ⬜ 항목 추출 후
deadlines = {
    "연구제안서 + 수행계획서": date(2026, 4, 2),
    # 추가 항목은 CLAUDE.md에서 동적 파싱
}
today = date.today()
for name, d in sorted(deadlines.items(), key=lambda x: x[1]):
    delta = (d - today).days
    status = f"D-{delta}" if delta > 0 else ("D-DAY" if delta == 0 else f"D+{abs(delta)} (지남)")
    print(f"{name}: {status}")
```

결정: 가장 임박한 제출물을 이번 실행의 대상으로 설정한다.

---

### Phase 1: 양식 확인 (3분)

해당 제출물에 필요한 양식을 확보한다.

- [ ] templates/forms/ 에서 해당 양식 검색
- [ ] 양식이 없으면 캡스톤 사이트에서 확인

```bash
cd ~/Capstone
ls templates/forms/
# 양식 zip이 있으면 해제
```

사이트 확인:
```
WebFetch: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=27
→ 해당 제출물 양식 링크 추출
```

- [ ] templates/samples/ 에서 유사 예시 확인
- [ ] 양식 요구사항 정리: 파일 형식(hwp/pdf), 필수 항목, 분량

```bash
ls templates/samples/
# 예시 파일: 2분반_Reward_연구제안서.pdf, 람다람쥐_자문내역서-수정본.pdf 등
```

---

### Phase 2: 기존 자료 수집 (5분)

제출물 내용에 필요한 프로젝트 자료를 수집한다.

- [ ] plans/ — 연구 설계안/기획안 (연구 목표, 방법론, 일정)
- [ ] reference/analysis/ — 관련 시리즈 분석 문서 (기술 배경)
- [ ] reference/summaries/ — 핵심 논문 총정리 (선행 연구)
- [ ] submission/ — 기존 제출물 (스타일, 팀명 표기, 형식 참조)
- [ ] CLAUDE.md — 프로젝트 개요, 팀원 정보, 현재 단계

수집 체크:
```bash
cd ~/Capstone
echo "설계안: $(ls plans/연구_설계안_* 2>/dev/null | wc -l)건"
echo "기획안: $(ls plans/연구_기획안_* 2>/dev/null | wc -l)건"
echo "분석 시리즈: $(ls reference/analysis/*.md 2>/dev/null | wc -l)건"
echo "총정리: $(ls reference/summaries/*.md 2>/dev/null | wc -l)건"
echo "기존 제출물: $(ls submission/ 2>/dev/null | wc -l)건"
```

---

### Phase 3: 제출물 작성 (20분+)

양식에 맞춰 내용을 작성한다. 이 Phase가 핵심이며 제출물 유형별로 다르게 진행한다.

- [ ] 양식 필수 항목 리스트 작성
- [ ] 각 항목별 내용 작성

#### 제출물 유형별 핵심 내용

**연구제안서:**
- 연구 제목, 팀명(속도는벡터), 지도교수
- 연구 배경 및 필요성 (Exqutor 논문 핵심 문제 — 고정 비율 cardinality 추정)
- 연구 목표 (sample selection 단계 개입의 Q-error 영향 검증)
- 연구 방법 (B1/CaseA/CaseB 3-way paired 측정)
- 기대 효과
- 참고문헌

**수행계획서:**
- 주차별 세부 계획
- 역할 분담 (4인: 조현빈, 박세은, 강재현, 이동욱)
- 필요 장비/소프트웨어

**중간보고서:**
- 진행 현황 (계획 대비 실적)
- 실험 중간 결과
- 향후 계획

**연구지도확인서:**
- 날짜, 지도 내용, 교수 서명란

**자문내역서:**
- 자문위원 정보, 자문 일시, 질의/응답 내용

작성 규칙:
- 한국어 학술 산문 스타일
- 기존 submission/ 파일의 팀명 표기 방식 준수 (`속도는벡터`)
- hwp 양식이 필요한 경우: 사용자에게 별도 안내 (Claude는 hwp 직접 편집 불가)

---

### Phase 4: 검증 + 최종본 저장 (5분)

- [ ] 필수 항목 누락 체크 (Phase 3의 리스트 대조)
- [ ] 파일 형식 확인
  - pdf 필요 → 문서생성지침 위임 (Chrome CDP)
  - hwp 필요 → 사용자에게 수동 변환 안내
- [ ] submission/ 폴더에 최종본 저장

저장 규칙:
```
submission/속도는벡터_{제출물명}.{확장자}
예: submission/속도는벡터_연구제안서.pdf
```

- [ ] 기존 파일과 중복 시 버전 확인 후 덮어쓰기 또는 번호 부여

---

### Phase 5: 일정 동기화 (2분)

제출 완료 또는 작성 완료 시 일정 상태를 업데이트한다.

- [ ] CLAUDE.md `핵심 일정` 테이블: 해당 항목 ⬜ → ✅ 변경
- [ ] 메모리 project_capstone.md: 제출 상태 반영
- [ ] 노션 일정 DB 업데이트 안내 (노션 MCP 사용 가능 시 직접 업데이트)

```python
# CLAUDE.md 업데이트 예시
# "| 4/2 | 연구제안서 + 수행계획서 제출 | ⬜ |"
# → "| 4/2 | 연구제안서 + 수행계획서 제출 | ✅ |"
```

---

### Phase 6: 결과 보고 (1분)

- [ ] 작성한 제출물 요약 출력
- [ ] 파일 위치 안내
- [ ] 다음 마감 D-day 안내

출력 형식:
```
| 항목                  | 상태 | 상세                              |
|-----------------------|------|-----------------------------------|
| 대상 제출물           | ✅   | 연구제안서 + 수행계획서            |
| 양식 확인             | ✅   | 캡스톤 사이트 양식 적용            |
| 내용 작성             | ✅   | 한국어 학술 산문, 필수 항목 충족   |
| 최종본 저장           | ✅   | submission/속도는벡터_연구제안서.pdf |
| 일정 동기화           | ✅   | CLAUDE.md ✅ + 메모리 업데이트     |
| 다음 마감             | ⬜   | D-28 중간발표 (5월 예정)           |
```

---

## 완료 조건
- [ ] Phase 0~6 모든 체크리스트 완료
- [ ] 제출물 파일 submission/에 저장됨
- [ ] 양식 필수 항목 전부 충족
- [ ] 일정 3곳 동기화 완료
- [ ] 결과 보고 테이블 출력
- [ ] `> 마지막 실행:` 라인에 현재 날짜+시각 업데이트
