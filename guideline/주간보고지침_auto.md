# 주간보고지침 (AUTO)

> 대상: Capstone 프로젝트 | 모드: 자동 실행 (전권 위임)
> 마지막 실행: (미실행)

## 주간보고지침의 범위

**IS (이 지침이 하는 것):**
- git log 기반 이번 주(월~일) 작업 요약 생성
- research/ 내 새 분석 문서 추가/수정 파악
- 실험 진행 상황 반영 (experiments/ 또는 커밋 기반)
- 노션 DB 동기화 확인 (Study Archive, 캡스톤 일정 DB)
- 팀원 업무 분배 현황 정리
- 다음 주 계획 수립 및 우선순위 설정
- 주간 리포트 파일 출력 (records/weekly/)

**IS NOT (이 지침이 하지 않는 것 → 담당 지침):**
- 미팅 회의록 작성 → 미팅지침 (이 지침은 회의록을 "참조"만 함)
- 제출물 마감 관리, 양식 작성 → 제출물지침
- 문서 작성/md→PDF 변환 → 논문분석지침, 문서생성지침
- 캡스톤 사이트 공지 확인 → 점검지침
- 실험 환경 구축, 벤치마크 실행 → 실험지침

---

## Phase 구성

### Phase 0: 데이터 수집 (3분)

이번 주 작업 이력을 수집한다.

- [ ] git log로 이번 주 커밋 목록 추출
- [ ] research/ 내 최근 수정 파일 목록 확인
- [ ] records/meetings/ 이번 주 회의록 존재 여부 확인
- [ ] submission/ 내 이번 주 변경 파일 확인

수집 스크립트:
```bash
cd ~/Capstone

echo "=== 이번 주 커밋 ==="
git log --since="1 week ago" --oneline --no-merges

echo ""
echo "=== 이번 주 변경 파일 (research/) ==="
git log --since="1 week ago" --name-only --pretty=format:"" -- research/ | sort -u | grep .

echo ""
echo "=== 이번 주 변경 파일 (전체) ==="
git log --since="1 week ago" --stat --pretty=format:"%h %s"

echo ""
echo "=== 이번 주 회의록 ==="
ls records/meetings/ 2>/dev/null | tail -5

echo ""
echo "=== 미커밋 변경사항 ==="
git status --short
```

---

### Phase 1: 주간 요약 작성 (10분)

Phase 0 데이터를 기반으로 주간 요약을 구성한다.

- [ ] **완료 작업 정리**: 커밋 메시지 분류 (기능/문서/수정/동기화)
- [ ] **문서 변경 현황**: 새 분석 문서, 수정된 문서, 삭제된 문서
- [ ] **분석 진행률 계산**: summaries/ md 수 / 전체 목표(82편)
- [ ] **실험 진행 현황**: 실험 관련 커밋 또는 파일 유무
- [ ] **미팅 요약**: 이번 주 회의록이 있으면 핵심 결정사항 1~2줄 인용

분석 진행률 계산:
```bash
cd ~/Capstone/research
echo "총정리 md: $(ls summaries/*.md 2>/dev/null | wc -l) / 82"
echo "시리즈 md: $(ls analysis/*.md 2>/dev/null | wc -l)"
echo "원논문 pdf: $(ls papers/*.pdf 2>/dev/null | wc -l)"
```

커밋 분류 기준:
- `feat:` / `add:` → 새 기능/문서 추가
- `sync:` → 동기화/정리
- `fix:` → 수정
- `docs:` → 문서 업데이트

---

### Phase 2: 노션 동기화 확인 (5분)

주간 변경사항이 노션에 반영되었는지 확인한다.

- [ ] **Study Archive DB**: 이번 주 새로 추가된 분석 문서가 DB에 있는지 확인
- [ ] **캡스톤 일정 DB**: 완료된 마감 항목의 상태가 "완료"인지 확인
- [ ] **팀 페이지**: 이번 주 진행 현황이 팀 페이지에 반영되었는지 확인
- [ ] 미반영 항목이 있으면 업데이트 안내 또는 직접 실행

노션 확인 절차:
1. Study Archive DB 조회 → 이번 주 커밋에서 추가된 summaries/ 파일과 대조
2. 캡스톤 일정 DB 조회 → CLAUDE.md 일정표의 ✅ 항목과 대조
3. 불일치 시 사용자에게 안내

---

### Phase 3: 다음 주 계획 (3분)

CLAUDE.md 일정과 현재 진행 상황을 기반으로 다음 주 계획을 수립한다.

- [ ] CLAUDE.md 일정표에서 다음 마감 확인 + D-day 계산
- [ ] 우선순위 작업 목록 작성 (마감 임박 > 진행 중 > 신규)
- [ ] 팀원 역할 분담 제안 (4인 팀 기준)
- [ ] 이슈/블로커 정리

D-day 계산:
```python
from datetime import date
deadlines = {
    "연구제안서 + 수행계획서": date(2026, 4, 2),
    # CLAUDE.md의 ⬜ 항목에서 동적으로 추출
}
today = date.today()
for name, d in sorted(deadlines.items(), key=lambda x: x[1]):
    delta = (d - today).days
    status = f"D-{delta}" if delta > 0 else f"D+{abs(delta)} (초과)" if delta < 0 else "D-Day"
    print(f"  {name}: {status}")
```

---

### Phase 4: 리포트 출력 (2분)

주간 리포트를 파일로 저장하고 터미널에 출력한다.

- [ ] records/weekly/ 디렉토리 확인 (없으면 생성)
- [ ] 리포트 파일 작성: `records/weekly/주간보고_YYYY-MM-DD.md`
- [ ] 터미널에 리포트 전문 출력

리포트 형식:
```markdown
# 주간 작업일지 (YYYY-MM-DD ~ YYYY-MM-DD)

## 이번 주 요약
- [한 줄 핵심 요약]

## 완료 작업
1. [작업 1] — 커밋 해시
2. [작업 2] — 커밋 해시

## 문서 변경
| 문서 | 변경 유형 | 내용 |
|------|----------|------|
| (13) 새문서.md | 신규 | 논문 X 분석 |
| CLAUDE.md | 수정 | 일정 업데이트 |

## 논문 분석 현황
- 총정리: N/82편 (진행률 NN%)
- 시리즈: N편
- 원논문: N편

## 실험 진행
- [실험명]: [결과 요약] 또는 "미착수"

## 노션 동기화
- Study Archive: [동기화 상태]
- 일정 DB: [동기화 상태]

## 다음 주 계획
1. [계획 1] — 담당: [이름]
2. [계획 2] — 담당: [이름]

## 일정
- 다음 마감: [제출물명] (D-N)

## 이슈/블로커
- [있으면 기술, 없으면 "없음"]
```

---

## 완료 조건
- [ ] Phase 0~4 모든 체크리스트 완료
- [ ] 주간 리포트 파일 저장 (`records/weekly/주간보고_YYYY-MM-DD.md`)
- [ ] 터미널에 리포트 전문 출력
- [ ] 노션 동기화 확인 완료 (또는 미반영 안내)
- [ ] 다음 주 계획 수립 완료
- [ ] `> 마지막 실행:` 라인에 현재 날짜+시각 업데이트
