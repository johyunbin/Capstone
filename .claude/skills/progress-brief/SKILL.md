---
name: progress-brief
description: "프로젝트 진행 현황 브리핑 — 일정/제출물/논문분석 상태 종합 (현황, 브리핑, 상태, progress)"
---

# Progress Brief — 프로젝트 진행 브리핑

캡스톤 프로젝트 전체 진행 현황을 한눈에 파악하는 브리핑 생성.

## 점검 항목

### 1. 제출물 일정 체크
CLAUDE.md의 핵심 일정표 기준으로 다음 마감을 확인:
- 다음 제출 마감일과 D-day
- 미완료 제출물 목록
- Templates/ 양식 존재 여부 확인

### 2. 논문 분석 현황
```bash
# Research/ 내 분석문서 현황
echo "=== 시리즈 문서 ===" && ls Research/(*.md 2>/dev/null | wc -l
echo "=== 총정리 문서 ===" && ls Research/*총정리.md 2>/dev/null | wc -l
echo "=== 원논문 ===" && ls Research/papers/*.pdf 2>/dev/null | wc -l
```

### 3. 3종 세트 완성도
각 .md 파일에 대해 .pdf와 .docx가 모두 존재하는지 확인.
누락된 파일이 있으면 경고.

### 4. Git 상태
- 미커밋 변경사항
- 최근 커밋 이력
- 원격 동기화 상태

### 5. 실험 진행 (향후)
- Experiments/ 디렉토리 존재 여부
- 최근 실험 로그

## 출력 형식

```
=== 캡스톤 진행 브리핑 (YYYY-MM-DD) ===

📅 일정
  다음 마감: 연구제안서 (4월 초) — D-7
  완료: 4/6 (연구지도확인서 1~4차)

📄 문서 현황
  시리즈 분석: 12편 (md+pdf+docx 완성)
  총정리: 82편 (md+pdf+docx 완성)
  원논문: 69편
  3종 누락: 0건

🔬 실험
  실험 로그: 0건 (미착수)

🔄 Git
  브랜치: main
  미커밋: 3건
  최근: "sync: 디렉토리 정리" (2h ago)
```
