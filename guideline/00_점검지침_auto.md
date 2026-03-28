# 점검지침 (AUTO)

> 대상: Capstone 프로젝트 | 모드: 자동 실행 (전권 위임)
> 마지막 실행: (미실행)

## 점검지침의 범위

**IS (이 지침이 하는 것):**
- research/analysis/ 내 md↔pdf 2종 세트 완성도 검증
- research/summaries/ 내 md↔pdf 2종 세트 완성도 검증
- PDF 폰트 임베딩 확인 (Apple SD Gothic Neo 정상 여부, Unknown만 있으면 깨짐)
- 파일명 규칙 준수 검증: analysis `(번호) 제목.확장자`, summaries `[번호] 제목 총정리.확장자`
- orphan 파일(.tmp, .bak, .DS_Store 등) 탐지
- research/papers/ 원논문 vs summaries/ 번호 대응 확인
- 캡스톤 사이트(capstone.cs.yonsei.ac.kr) 공지사항 신규 확인
- 일정 3곳 동기화 상태 확인 (CLAUDE.md / 메모리 project_schedule / 노션 캡스톤 일정 DB)
- plans/ 문서 존재 및 타임스탬프 형식 검증

**IS NOT (이 지침이 하지 않는 것 → 담당 지침):**
- PDF 재생성, md→PDF 변환 실행 → 문서생성지침
- 논문 분석 문서 신규 작성 → 논문분석지침
- 실험 환경(pgvector, DuckDB) 상태 점검 → 실험지침
- 제출물 마감 관리, 양식 작성 → 제출물지침
- 코드 수정, 서비스 실행, 데이터 변경 — 수행하지 않음

---

## Phase 구성

### Phase 0: 인벤토리 수집 (2분)

디렉토리별 파일 수를 집계한다.

- [ ] research/analysis/ — md 수, pdf 수 각각 카운트
- [ ] research/summaries/ — md 수, pdf 수 각각 카운트
- [ ] research/papers/ — 원논문 PDF 수
- [ ] submission/ — 제출물 파일 수 및 목록
- [ ] plans/ — 문서 수 및 파일명 형식(`연구_*_YYYYMMDD_HHMMSS.*`) 확인

집계 방법:
```bash
cd ~/Capstone
echo "analysis md: $(ls research/analysis/*.md 2>/dev/null | wc -l)"
echo "analysis pdf: $(ls research/analysis/*.pdf 2>/dev/null | wc -l)"
echo "summaries md: $(ls research/summaries/*.md 2>/dev/null | wc -l)"
echo "summaries pdf: $(ls research/summaries/*.pdf 2>/dev/null | wc -l)"
echo "papers: $(ls research/papers/*.pdf 2>/dev/null | wc -l)"
echo "submission: $(ls submission/ 2>/dev/null | wc -l)"
echo "plans: $(ls plans/ 2>/dev/null | wc -l)"
```

---

### Phase 1: 2종 세트 완성도 검증 (3분)

각 md 파일에 대응하는 pdf가 존재하는지 확인한다.

- [ ] analysis/ 내 모든 .md에 대해 동일 이름 .pdf 존재 확인
- [ ] summaries/ 내 모든 .md에 대해 동일 이름 .pdf 존재 확인
- [ ] 누락 파일 목록 출력 (md만 있고 pdf 없는 파일)

검증 로직:
```bash
cd ~/Capstone/research/analysis
for f in *.md; do
  pdf="${f%.md}.pdf"
  [ ! -f "$pdf" ] && echo "MISSING: $pdf"
done

cd ~/Capstone/research/summaries
for f in *.md; do
  pdf="${f%.md}.pdf"
  [ ! -f "$pdf" ] && echo "MISSING: $pdf"
done
```

---

### Phase 2: PDF 폰트 검증 (3분)

생성된 PDF(analysis/ + summaries/)의 폰트 메타데이터를 확인한다.
Unknown 폰트만 있는 PDF = Chrome CDP가 아닌 다른 방식으로 생성된 깨진 파일.

- [ ] pypdf 설치 확인 (`pip3 install pypdf` 필요 시)
- [ ] analysis/ 내 모든 PDF 폰트 검사
- [ ] summaries/ 내 모든 PDF 폰트 검사
- [ ] 결과: 정상 수 / 비정상 수 / 비정상 파일 목록

검증 스크립트:
```python
import pypdf, glob, os
dirs = ["research/analysis", "research/summaries"]
ok, bad, bad_list = 0, 0, []
for d in dirs:
    for pdf_path in sorted(glob.glob(f"{d}/*.pdf")):
        try:
            reader = pypdf.PdfReader(pdf_path)
            fonts = set()
            for page in reader.pages:
                if "/Resources" in page and "/Font" in page["/Resources"]:
                    for font in page["/Resources"]["/Font"].values():
                        bf = font.get("/BaseFont", "Unknown")
                        fonts.add(str(bf))
            # Apple SD Gothic Neo → 정상, Unknown만 → 깨짐
            has_real = any("Unknown" not in f for f in fonts) if fonts else False
            if has_real:
                ok += 1
            else:
                bad += 1
                bad_list.append(os.path.basename(pdf_path))
        except Exception as e:
            bad += 1
            bad_list.append(f"{os.path.basename(pdf_path)} (읽기 실패: {e})")
print(f"정상: {ok}, 비정상: {bad}")
for f in bad_list:
    print(f"  ⚠️ {f}")
```

---

### Phase 3: 파일명 규칙 검증 (2분)

- [ ] analysis/: `(번호) 제목.확장자` 패턴 — 정규식 `^\(\d+\) .+\.(md|pdf)$`
- [ ] summaries/: `[번호] 제목 총정리.확장자` 패턴 — 정규식 `^\[\d+\] .+ 총정리\.(md|pdf)$`
- [ ] 비규격 파일 목록 출력

검증 로직:
```python
import re, os
analysis_pat = re.compile(r'^\(\d+\) .+\.(md|pdf)$')
summary_pat = re.compile(r'^\[\d+\] .+ 총정리\.(md|pdf)$')

for f in sorted(os.listdir("research/analysis")):
    if not analysis_pat.match(f):
        print(f"analysis 비규격: {f}")

for f in sorted(os.listdir("research/summaries")):
    if not summary_pat.match(f):
        print(f"summaries 비규격: {f}")
```

---

### Phase 4: orphan 및 중복 검사 (2분)

- [ ] .tmp, .bak, .swp 파일 탐지 (프로젝트 루트 전체)
- [ ] .DS_Store 파일 수 카운트 (정보용, .gitignore에 포함 확인)
- [ ] papers/ 와 다른 폴더 간 동일 파일명 PDF 중복 확인

검사 방법:
```bash
cd ~/Capstone
# orphan 파일
find . -name "*.tmp" -o -name "*.bak" -o -name "*.swp" | grep -v .git
# DS_Store
find . -name ".DS_Store" | grep -v .git | wc -l
# .gitignore에 .DS_Store 포함 확인
grep -q "DS_Store" .gitignore && echo "OK: .gitignore에 포함" || echo "WARN: .gitignore에 미포함"
```

---

### Phase 5: 원논문 ↔ 총정리 대응 확인 (2분)

summaries/의 `[번호]`와 papers/의 원논문 매핑 상태를 확인한다.

- [ ] summaries/에서 사용된 번호 목록 추출
- [ ] 번호 범위 내 빈 번호(gap) 확인
- [ ] papers/ 파일 수(69) vs summaries/ 고유 번호 수 비교

```bash
cd ~/Capstone/research/summaries
ls *.md | grep -oP '^\[\K\d+' | sort -n | uniq
```

---

### Phase 6: 일정 + 사이트 점검 (2분)

- [ ] 캡스톤 사이트 공지사항 WebFetch로 확인 → 새 항목 유무
- [ ] CLAUDE.md 일정표에서 다음 마감 항목 추출 + D-day 계산
- [ ] 메모리 project_schedule.md와 CLAUDE.md 일정 일치 여부 확인

사이트 확인:
```
WebFetch: https://capstone.cs.yonsei.ac.kr/capstone/?page_id=370
→ 새 공지 항목 추출
```

D-day 계산:
```python
from datetime import date
deadlines = {
    "연구제안서 + 수행계획서": date(2026, 4, 2),
    # CLAUDE.md에서 ⬜ 항목 추출
}
today = date.today()
for name, d in deadlines.items():
    delta = (d - today).days
    print(f"{name}: D{'-' if delta >= 0 else '+'}{abs(delta)}")
```

---

### Phase 7: 종합 리포트 (1분)

전 Phase 결과를 아래 표 형태로 출력한다.

- [ ] 리포트 테이블 생성
- [ ] 즉시 조치 필요 항목에 담당 지침 안내 포함

출력 형식:
```
| 항목                  | 상태 | 상세                          |
|-----------------------|------|-------------------------------|
| 인벤토리              | ✅   | analysis 12×2, summaries 82×2 |
| 2종 세트              | ✅   | 누락 0건                       |
| PDF 폰트              | ✅   | 94/94 정상                     |
| 파일명 규칙           | ⚠️   | 비규격 2건                     |
| orphan 파일           | ✅   | 0건                            |
| 원논문↔총정리 대응    | ✅   | 69 papers, 82 summaries       |
| 일정 동기화           | ✅   | D-5 연구제안서                  |
| 사이트 공지           | ✅   | 새 항목 없음                    |
| 종합                  | ⚠️   | 1건 주의 → 문서생성지침 참조    |
```

---

## 완료 조건
- [ ] Phase 0~7 모든 체크리스트 완료
- [ ] 종합 리포트 테이블 출력
- [ ] 즉시 조치 항목이 있으면 담당 지침명 안내
- [ ] `> 마지막 실행:` 라인에 현재 날짜+시각 업데이트
