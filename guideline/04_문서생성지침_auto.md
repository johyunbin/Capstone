# 문서생성지침 (AUTO)

> 대상: Capstone 프로젝트 | 모드: 자동 실행 (전권 위임)
> 마지막 실행: 2026-03-28 (전항목 정상, 누락 0건, 96/96 폰트 OK)

## 문서생성지침의 범위

**IS (이 지침이 하는 것):**
- md → HTML → Chrome CDP(headless) → PDF 변환 실행
- `scripts/md2pdf.py` 스크립트를 사용한 PDF 생성
- Apple SD Gothic Neo 폰트 렌더링 보장 확인
- 페이지 넘김 규칙 적용 (제목 뒤 본문 동반, 문단 내부 짤림 금지)
- 페이지 번호 꼬리말 정상 출력 확인
- 코드 블록/테이블 렌더링 품질 보장
- md 대비 pdf 누락 파일 자동 탐지 및 일괄 변환
- md2pdf.py 의존성(Python3, markdown, websocket-client) 확인
- 필요 시 pandoc 기반 md → docx 변환

**IS NOT (이 지침이 하지 않는 것 → 담당 지침):**
- md 내용 작성 (논문 분석 본문) → 논문분석지침
- md 내용 작성 (제출물 본문) → 제출물지침
- md 내용 작성 (주간보고 본문) → 주간보고지침
- PDF 폰트 검증만 수행 (생성 없이 검사만) → 점검지침
- fpdf2 사용 → **절대 금지** (한글 TTC/OTF 서브셋팅 깨짐)

---

## Phase 구성

### Phase 0: 환경 확인 (1분)

변환에 필요한 의존성과 도구가 정상 설치되어 있는지 확인한다.

- [ ] Python3 설치 확인
- [ ] `markdown` 라이브러리 설치 확인 (`python3 -c "import markdown"`)
- [ ] `websocket-client` 설치 확인 (`python3 -c "import websocket"`)
- [ ] Chrome 실행 파일 존재 확인: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- [ ] `scripts/md2pdf.py` 존재 확인
- [ ] pypdf 설치 확인 (PDF 검증용, 없으면 안내만)

환경 확인 스크립트:
```bash
cd ~/Capstone
python3 -c "import markdown; print('markdown OK')"
python3 -c "import websocket; print('websocket-client OK')"
[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && echo "Chrome OK" || echo "Chrome MISSING"
[ -f scripts/md2pdf.py ] && echo "md2pdf.py OK" || echo "md2pdf.py MISSING"
```

미설치 항목 발견 시 자동 설치:
```bash
pip3 install markdown websocket-client
```

---

### Phase 1: 누락 PDF 탐지 (2분)

research/analysis/와 research/summaries/에서 md는 있지만 대응 pdf가 없는 파일을 찾는다.

- [ ] research/analysis/ 내 md→pdf 누락 목록 생성
- [ ] research/summaries/ 내 md→pdf 누락 목록 생성
- [ ] plans/ 내 md→pdf 누락 목록 생성 (있을 경우)
- [ ] 전체 누락 파일 수 집계 및 목록 출력

탐지 로직:
```bash
cd ~/Capstone
MISSING=""

for d in research/analysis research/summaries plans; do
  [ ! -d "$d" ] && continue
  for f in "$d"/*.md; do
    [ ! -f "$f" ] && continue
    pdf="${f%.md}.pdf"
    [ ! -f "$pdf" ] && MISSING="$MISSING\n$pdf"
  done
done

echo -e "누락 PDF 목록:$MISSING"
```

누락 0건이면 Phase 2를 건너뛰고 Phase 3으로 이동.

---

### Phase 2: PDF 변환 실행 (5분)

Phase 1에서 발견된 누락 파일을 일괄 변환한다.

- [ ] 단일 파일 변환 테스트 (첫 번째 누락 파일로 검증)
- [ ] 테스트 성공 확인 후 나머지 일괄 변환
- [ ] 성공/실패 카운트 출력

변환 실행:
```bash
cd ~/Capstone

# 단일 파일 테스트
python3 scripts/md2pdf.py "첫번째_누락파일.md"

# 일괄 변환 루프
SUCCESS=0
FAIL=0
for d in research/analysis research/summaries plans; do
  [ ! -d "$d" ] && continue
  for f in "$d"/*.md; do
    [ ! -f "$f" ] && continue
    pdf="${f%.md}.pdf"
    if [ ! -f "$pdf" ]; then
      if python3 scripts/md2pdf.py "$f"; then
        SUCCESS=$((SUCCESS + 1))
      else
        FAIL=$((FAIL + 1))
        echo "FAIL: $f"
      fi
    fi
  done
done

echo "변환 완료: 성공 ${SUCCESS}건, 실패 ${FAIL}건"
```

실패 파일 발생 시:
1. 에러 메시지 확인 (Chrome 타임아웃, 포트 충돌 등)
2. Chrome 프로세스 정리: `pkill -f "chrome.*remote-debugging-port"`
3. 재시도

---

### Phase 3: 품질 검증 (3분)

생성된 PDF의 품질을 확인한다.

- [ ] 새로 생성된 PDF 페이지 수 확인 (0페이지 = 실패)
- [ ] 한글 폰트 정상 여부 (pypdf로 폰트 메타 확인)
- [ ] 페이지 번호 꼬리말 정상 여부 (PDF 뷰어에서 확인하기 어려우므로 페이지 수 > 0으로 간접 확인)
- [ ] 검증 결과: 정상 수 / 비정상 수 / 비정상 파일 목록

폰트 검증 스크립트:
```python
import glob, os
try:
    import pypdf
except ImportError:
    print("pypdf 미설치 — pip3 install pypdf")
    exit(0)

ok, bad, bad_list = 0, 0, []
for d in ['research/analysis', 'research/summaries', 'plans']:
    for p in sorted(glob.glob(f'{d}/*.pdf')):
        try:
            reader = pypdf.PdfReader(p)
            if len(reader.pages) == 0:
                bad += 1
                bad_list.append(f"{os.path.basename(p)} (0페이지)")
                continue
            fonts = set()
            for page in reader.pages:
                res = page.get('/Resources')
                if res and '/Font' in res:
                    for font in res['/Font'].values():
                        fo = font.get_object() if hasattr(font, 'get_object') else font
                        bf = str(fo.get('/BaseFont', 'Unknown'))
                        fonts.add(bf)
            has_real = any('Unknown' not in f for f in fonts) if fonts else False
            if has_real:
                ok += 1
            else:
                bad += 1
                bad_list.append(os.path.basename(p))
        except Exception as e:
            bad += 1
            bad_list.append(f'{os.path.basename(p)} (err: {e})')

print(f'정상: {ok}, 비정상: {bad}')
for f in bad_list:
    print(f'  WARNING: {f}')
```

비정상 PDF 발견 시: 해당 md를 md2pdf.py로 재생성 시도.

---

### Phase 4: docx 변환 (선택) (5분)

제출용 docx가 필요한 경우에만 실행한다.

- [ ] pandoc 설치 확인 (`pandoc --version`)
- [ ] 대상 md 파일 지정 (사용자 입력 또는 submission/ 내 md)
- [ ] `pandoc input.md -o output.docx` 실행
- [ ] 생성된 docx 확인

미설치 시:
```bash
brew install pandoc
```

변환:
```bash
pandoc submission/대상.md -o submission/대상.docx --reference-doc=templates/forms/참조양식.docx
```

이 Phase는 사용자가 docx를 요청했을 때만 실행. 기본은 건너뜀.

---

### Phase 5: 종합 리포트 (1분)

전 Phase 결과를 테이블로 출력한다.

- [ ] 리포트 테이블 생성
- [ ] 실패/비정상 항목에 대한 조치 안내

출력 형식:
```
| 항목            | 상태 | 상세                           |
|-----------------|------|--------------------------------|
| 환경            | ✅   | Python3, markdown, Chrome OK   |
| 누락 탐지       | ✅   | 3건 발견                       |
| PDF 변환        | ✅   | 성공 3건, 실패 0건             |
| 품질 검증       | ✅   | 전체 정상, 한글 폰트 OK        |
| docx 변환       | ⏭️   | 미요청 (건너뜀)                 |
| 종합            | ✅   | 전체 완료                      |
```

---

## 완료 조건
- [ ] Phase 0~3 모든 체크리스트 완료
- [ ] 대상 md 전부 PDF 변환 완료 (누락 0건)
- [ ] 한글 폰트 정상 확인 (비정상 0건)
- [ ] 종합 리포트 테이블 출력
- [ ] `> 마지막 실행:` 라인에 현재 날짜+시각 업데이트
