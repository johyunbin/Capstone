# Phase 0: 점검지침 제작 프롬프트

## 지침 개요

**점검 = 정적 품질 분석.** 프로젝트 파일을 읽고, 규칙을 검증하고, 이상을 보고한다.
서비스 실행이나 코드 수정은 하지 않는다.

## IS / IS NOT

**IS:**
- research/ 내 3종 세트(md/pdf/docx) 완성도 검증
- PDF 폰트 임베딩 확인 (Apple SD Gothic Neo / Unknown 체크)
- 파일명 규칙 준수 확인: `(번호) 제목_유형.확장자`, `[번호] 제목 총정리.확장자`
- orphan 파일(.tmp, .bak) 탐지
- research/papers/ 원논문 vs summaries/ 대응 확인
- 캡스톤 사이트(capstone.cs.yonsei.ac.kr) 공지사항 신규 확인
- 일정 3곳 동기화 상태 확인 (CLAUDE.md / 메모리 / 노션)

**IS NOT:**
- PDF 재생성 → 문서생성지침
- 논문 분석 문서 작성 → 논문분석지침
- 실험 환경 점검 → 실험지침
- 제출물 마감 관리 → 제출물지침

## 읽어야 할 프로젝트 파일

1. `CLAUDE.md` — 디렉토리 구조, 문서 규칙, 일정
2. `.claude/skills/project-health/` — 기존 project-health 스킬 (흡수 대상)
3. `.claude/agents/document-validator.md` — 기존 에이전트 (흡수 대상)
4. `scripts/md2pdf.py` — PDF 변환 스크립트 (점검 대상 이해)
5. `research/analysis/`, `research/summaries/` — 실제 파일 목록

## Phase 구성 가이드

### Phase 0: 인벤토리 수집 (2분)
- research/analysis/ 파일 수 (md, pdf 각각)
- research/summaries/ 파일 수 (md, pdf 각각)
- research/papers/ 원논문 수
- submission/ 제출물 수
- plans/ 문서 수

### Phase 1: 3종 완성도 검증 (3분)
- analysis/ 내 md에 대응하는 pdf 존재 여부
- summaries/ 내 md에 대응하는 pdf 존재 여부
- 누락 파일 목록 출력

### Phase 2: PDF 폰트 검증 (3분)
- 모든 생성 PDF(analysis/ + summaries/)에서 폰트 메타데이터 확인
- pypdf로 Unknown 폰트만 있는 파일 = 깨진 파일
- 정상/비정상 수 출력

### Phase 3: 파일명 규칙 검증 (2분)
- analysis/: `(번호) 제목.확장자` 패턴 검증
- summaries/: `[번호] 제목 총정리.확장자` 패턴 검증
- 비규격 파일 목록

### Phase 4: orphan 및 중복 검사 (2분)
- .tmp, .bak, .DS_Store 등 불필요 파일
- papers/ 와 다른 폴더 간 중복 PDF

### Phase 5: 일정 + 사이트 점검 (2분)
- 캡스톤 사이트 공지사항 새 항목 확인 (WebFetch)
- CLAUDE.md 일정표 vs 현재 날짜 비교 → 다음 마감 D-day
- 노션 일정 DB와 동기화 상태 확인

### Phase 6: 종합 리포트 (1분)
- 전 Phase 결과를 표 형태로 정리
- 즉시 조치 필요 항목 하이라이트

## 완료 조건
- 모든 Phase 체크리스트 완료
- 종합 리포트 출력
- 즉시 조치 항목이 있으면 담당 지침 안내
