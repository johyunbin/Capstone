# 점검지침 (MANUAL)

> 사람이 직접 수행하거나 Claude에게 개별 요청할 때 참조

## 언제 실행하나?

- **매 세션 시작 시** — 파일 상태가 이전 세션과 달라졌을 수 있음
- **문서 대량 생성 후** — 논문 분석/PDF 변환 후 누락 확인
- **제출 마감 전** — 일정 확인 + 파일 완성도 최종 점검
- **git pull 직후** — 팀원 변경사항 반영 후 무결성 확인

## 단계별 가이드

### Step 1: 빠른 인벤토리 확인

아래 명령어로 현재 파일 수를 한눈에 확인:

```bash
cd ~/Capstone
echo "analysis: $(ls research/analysis/*.md | wc -l) md, $(ls research/analysis/*.pdf | wc -l) pdf"
echo "summaries: $(ls research/summaries/*.md | wc -l) md, $(ls research/summaries/*.pdf | wc -l) pdf"
echo "papers: $(ls research/papers/*.pdf | wc -l)"
echo "submission: $(ls submission/ | wc -l)"
```

md 수와 pdf 수가 동일하면 2종 세트 완성. 불일치 시 Step 2로.

### Step 2: 누락 파일 찾기

```bash
cd ~/Capstone/research/analysis
for f in *.md; do [ ! -f "${f%.md}.pdf" ] && echo "누락: ${f%.md}.pdf"; done

cd ~/Capstone/research/summaries
for f in *.md; do [ ! -f "${f%.md}.pdf" ] && echo "누락: ${f%.md}.pdf"; done
```

누락된 PDF가 있으면 Claude에게 요청:
> "research/summaries/[번호] 제목 총정리.md를 PDF로 변환해줘"

이 작업은 **문서생성지침** 범위이므로 해당 지침 참조.

### Step 3: PDF 폰트 확인

pypdf가 설치되어 있어야 한다:
```bash
pip3 install pypdf
```

간단 확인 (Python):
```python
import pypdf
reader = pypdf.PdfReader("파일경로.pdf")
page = reader.pages[0]
fonts = page["/Resources"].get("/Font", {})
for name, font in fonts.items():
    print(name, font.get("/BaseFont", "Unknown"))
```

- `AppleSDGothicNeo` 계열 → 정상 (Chrome CDP로 생성)
- `Unknown`만 있음 → 깨진 파일 (fpdf2 등으로 잘못 생성)

깨진 PDF 발견 시: `python3 scripts/md2pdf.py 해당파일.md`로 재생성.

### Step 4: 파일명 규칙 확인

| 디렉토리 | 패턴 | 예시 |
|----------|------|------|
| analysis/ | `(번호) 제목.확장자` | `(01) Exqutor_상세분석.md` |
| summaries/ | `[번호] 제목 총정리.확장자` | `[0] Exqutor_... 총정리.md` |
| plans/ | `연구_유형_YYYYMMDD_HHMMSS.확장자` | `연구_설계안_20260328_141451.md` |

비규격 파일은 이름을 수정하거나, 의도적 예외인지 확인.

### Step 5: orphan 파일 정리

```bash
cd ~/Capstone
find . -name "*.tmp" -o -name "*.bak" -o -name "*.swp" | grep -v .git
```

발견되면 내용을 확인한 뒤 삭제. `.DS_Store`는 `.gitignore`에 포함되어 있으면 무시 가능.

### Step 6: 일정 확인

1. 캡스톤 사이트 접속: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=370
2. CLAUDE.md의 `핵심 일정` 테이블과 비교
3. 새 일정이 있으면 아래 3곳 동시 업데이트:
   - CLAUDE.md 일정 테이블
   - 메모리 `project_schedule.md`
   - 노션 `캡스톤 일정` DB

Claude에게 요청할 경우:
> "캡스톤 사이트 일정 확인하고 CLAUDE.md 업데이트해줘"

## 자주 하는 실수

| 실수 | 올바른 방법 |
|------|------------|
| fpdf2로 PDF 생성 | Chrome CDP만 사용 (`scripts/md2pdf.py`) |
| 폰트 깨진 PDF를 그대로 방치 | 발견 즉시 재생성 |
| summaries 번호가 papers와 1:1이라 가정 | summaries는 82편, papers는 69편 — 일부 논문은 PDF 없이 분석 |
| .DS_Store를 커밋 | .gitignore에 포함 확인 |
| 일정을 한 곳만 업데이트 | 반드시 3곳(CLAUDE.md, 메모리, 노션) 동시 |
| 점검 중 파일 수정 시도 | 점검은 읽기 전용 — 수정은 담당 지침으로 |

## 관련 지침

| 지침 | 연동 관계 |
|------|----------|
| 문서생성지침 | PDF 깨짐 발견 → 재생성 요청 |
| 논문분석지침 | 2종 세트 누락 발견 → 분석 문서 작성 요청 |
| 제출물지침 | 일정 마감 임박 발견 → 제출물 준비 요청 |
| 주간보고지침 | 점검 결과를 주간 보고에 반영 |
