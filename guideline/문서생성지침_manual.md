# 문서생성지침 (MANUAL)

> 사람이 직접 수행하거나 Claude에게 개별 요청할 때 참조

## 언제 실행하나?

- **논문 분석 md 완성 후** — 대응 PDF를 생성해야 할 때
- **제출물 md 작성 후** — PDF 또는 docx 배포본이 필요할 때
- **설계안/기획안 편집 후** — 타임스탬프가 갱신된 md를 PDF로 재변환
- **점검지침에서 누락 PDF 발견 시** — 재생성 요청을 받았을 때
- **PDF 폰트 깨짐 발견 시** — Chrome CDP로 재생성이 필요할 때

## 단계별 가이드

### Step 1: 환경 확인

변환 전 의존성이 설치되어 있는지 확인:

```bash
cd ~/Capstone
python3 -c "import markdown; import websocket; print('OK')"
[ -f scripts/md2pdf.py ] && echo "md2pdf.py OK"
```

미설치 시:
```bash
pip3 install markdown websocket-client
```

Chrome이 없으면 App Store 또는 공식 사이트에서 설치.

### Step 2: 단일 파일 변환

특정 md를 PDF로 변환:

```bash
cd ~/Capstone
python3 scripts/md2pdf.py research/summaries/[번호]\ 제목\ 총정리.md
```

출력 위치: 같은 디렉토리에 `.pdf` 확장자로 자동 생성.

Claude에게 요청할 경우:
> "research/summaries/[5] 제목 총정리.md를 PDF로 변환해줘"

### Step 3: 누락 파일 일괄 변환

md는 있는데 pdf가 없는 파일을 한꺼번에 변환:

```bash
cd ~/Capstone
for d in research/analysis research/summaries plans; do
  [ ! -d "$d" ] && continue
  for f in "$d"/*.md; do
    [ ! -f "$f" ] && continue
    pdf="${f%.md}.pdf"
    [ ! -f "$pdf" ] && python3 scripts/md2pdf.py "$f"
  done
done
```

Claude에게 요청할 경우:
> "누락된 PDF 전부 생성해줘" 또는 "문서생성지침 실행해줘"

### Step 4: 폰트 깨짐 PDF 재생성

점검지침에서 비정상 판정된 PDF가 있으면 재생성:

```bash
cd ~/Capstone
# 깨진 파일의 원본 md 경로 확인 후
python3 scripts/md2pdf.py research/analysis/\(01\)\ Exqutor_상세분석.md
```

**절대 fpdf2를 사용하지 않는다.** 한글 폰트 서브셋팅이 깨진다. 반드시 `scripts/md2pdf.py`(Chrome CDP)만 사용.

### Step 5: 강제 페이지 구분 삽입

긴 문서에서 특정 위치에 페이지를 나누고 싶을 때, md 파일에 아래를 삽입:

```html
<div class="page-break"></div>
```

이 태그는 Chrome CDP 렌더링 시 `page-break-before: always` 스타일로 처리된다.

### Step 6: docx 변환 (제출용)

일부 제출물은 docx 형식이 필요하다:

```bash
# pandoc 설치 (최초 1회)
brew install pandoc

# 변환
cd ~/Capstone
pandoc submission/연구제안서.md -o submission/연구제안서.docx
```

양식 템플릿이 있는 경우:
```bash
pandoc submission/연구제안서.md -o submission/연구제안서.docx \
  --reference-doc=templates/forms/참조양식.docx
```

### Step 7: 변환 결과 확인

생성된 PDF를 열어서 아래 항목 확인:

| 확인 항목 | 정상 기준 |
|-----------|----------|
| 한글 표시 | 깨짐 없이 정상 렌더링 |
| 폰트 | Apple SD Gothic Neo 계열 |
| 페이지 번호 | 하단 중앙에 표시 |
| 헤더 | 없음 (날짜/URL 없음) |
| 코드 블록 | 검정 배경, 가독성 확보 |
| 테이블 | 셀 경계선 정상, 짤림 없음 |
| 페이지 넘김 | 제목만 있고 본문 없는 페이지 없음 |

## 자주 하는 실수

| 실수 | 올바른 방법 |
|------|------------|
| fpdf2로 PDF 생성 | Chrome CDP만 사용 (`scripts/md2pdf.py`) |
| Chrome 없이 변환 시도 | Chrome 필수 — headless 모드로 렌더링 |
| 한글 파일명에 이스케이프 누락 | bash에서 `\(`, `\ `, `\[` 등 이스케이프 또는 따옴표 |
| 변환 후 확인 안 함 | 최소 1개는 열어서 한글/레이아웃 확인 |
| 여러 파일 동시 변환 시 Chrome 충돌 | 순차 실행 (병렬 X) — 포트 충돌 방지 |
| page-break 태그 없이 긴 문서 변환 | 섹션 경계에 `<div class="page-break"></div>` 삽입 |

## 관련 지침

| 지침 | 연동 관계 |
|------|----------|
| 점검지침 | PDF 폰트 검증 → 깨짐 발견 시 이 지침으로 재생성 요청 |
| 논문분석지침 | 분석 md 작성 후 → 이 지침으로 PDF 변환 |
| 실험지침 | 실험 결과 보고서 md → 이 지침으로 PDF 변환 |
| 제출물지침 | 제출용 문서 → 이 지침으로 PDF/docx 변환 |
| 주간보고지침 | 주간보고 md → 이 지침으로 PDF 변환 |
