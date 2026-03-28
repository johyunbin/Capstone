# Phase 4: 문서생성지침 제작 프롬프트

## 지침 개요

**문서생성 = md → HTML → PDF 변환 파이프라인 운영.** scripts/md2pdf.py를 사용하여
Chrome headless 기반으로 한글 PDF를 생성한다. 폰트, 페이지 넘김, 번호 규칙을 관리.

## IS / IS NOT

**IS:**
- md → HTML → Chrome headless → PDF 변환 실행
- scripts/md2pdf.py 유지보수 및 개선
- Apple SD Gothic Neo 폰트 렌더링 보장
- 페이지 넘김 규칙 (제목 뒤 본문 동반, 문단 내부 짤림 금지)
- 페이지 번호 꼬리말
- 코드 블록/테이블 렌더링 품질
- md → docx 변환 (필요 시)

**IS NOT:**
- md 내용 작성 → 논문분석지침, 제출물지침, 주간보고지침 등
- PDF 폰트 검증 → 점검지침
- fpdf2 사용 → **금지** (한글 TTC/OTF 서브셋팅 깨짐)

## 읽어야 할 프로젝트 파일

1. `CLAUDE.md` — 문서 작성 규칙, MD→PDF 변환 환경 섹션
2. `scripts/md2pdf.py` — 현재 변환 스크립트 전체
3. `research/analysis/` — 변환 대상 파일 예시
4. `research/summaries/` — 변환 대상 파일 예시

## Phase 구성 가이드

### Phase 0: 환경 확인 (1분)
- Python3 + markdown 라이브러리 설치 확인
- Chrome 경로 확인: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- md2pdf.py 존재 확인

### Phase 1: 단일 파일 변환 (2분)
- 대상 md 파일 지정 (사용자 입력 또는 누락 PDF 자동 탐지)
- `python3 scripts/md2pdf.py research/analysis/대상.md` 실행
- 생성된 PDF 확인

### Phase 2: 일괄 변환 (5분)
- md 대비 pdf 누락 파일 목록 생성
- 일괄 변환 루프 실행
- 성공/실패 카운트 출력

### Phase 3: 품질 검증 (3분)
- 생성 PDF 페이지 수 확인
- 한글 깨짐 여부 (pypdf 폰트 메타 체크)
- 페이지 번호 정상 여부

### Phase 4: docx 변환 (선택) (5분)
- 제출용 docx 필요 시 pandoc 사용
- `pandoc input.md -o output.docx`

## 완료 조건
- 대상 md 전부 PDF 변환 완료
- 한글 폰트 정상 확인
- 점검지침 호출 시 폰트 검증 통과
