# φ 축 — 페이지 번호 좌하단 navy 일관성

> 검증자: φ 축 sub-agent (Opus 4.7) · read-only
> 검증 대상: 21장 deck 신본 `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx`
> 정본 base: `submission/_drafts/속도는벡터_발표deck_claudedesign_Phase2반영_20260520_095900.md` line 34 · 107 · 130
> raw quote 출처: `_internal/cache/rq3/validation/deck_phase2/raw_dump.md`
> 보조 검증: pptx XML 직접 unzip 정밀 검사 (`/tmp/pptx_extract/ppt/slides/slide{1..21}.xml`, `ppt/slideMasters/slideMaster1.xml`, `ppt/notesSlides/notesSlide{1..21}.xml`)
> 검증 일시: 2026-05-20

---

## VERDICT: **FAIL** (critical 1 · major 0 · minor 0)

deck 프롬프트의 절대 규칙 line 34 "**페이지 번호 위치 고정: 좌하단 navy `#1E3A5F`. 18장의 기존 위치와 동일.**" 을 정본 base 로 21장 본 슬라이드(ppt/slides/slide{1..21}.xml)에 페이지 번호 shape 가 존재하는지 검사했다. 결과:

- 21장 본 슬라이드 **모두 페이지 번호 0건** (좌하단·우하단·기타 위치 어디에도 없음).
- slideMaster1.xml 에서 `<p:hf sldNum="0" hdr="0" ftr="0" dt="0"/>` — **슬라이드 번호 기능이 마스터 수준에서 비활성**.
- 단, 노트 슬라이드(ppt/notesSlides/notesSlide{1..21}.xml)에는 21장 모두 `<a:fld type="slidenum">` 페이지 번호 fld 1개씩이 들어있어 노트 인쇄 시에만 페이지 번호가 보이는 구조.

이는 절대 규칙 line 34·107·130 의 "좌하단 navy" 정본 위치 유지 요구를 충족하지 않는다 — 발표 본 슬라이드 화면에 페이지 번호가 표시되지 않으므로 청중·교수가 슬라이드 진행도를 시각적으로 파악할 수 없다.

| severity | 개수 | 비고 |
|---|---|---|
| critical | 1 | 21장 본 슬라이드에 페이지 번호 shape 0건 (정본 좌하단 navy 위치에 부재) |
| major | 0 | — |
| minor | 0 | — |

---

## §1. 21장 페이지 번호 추출

본 슬라이드(ppt/slides/slide*.xml) 직접 검사 결과:

| 슬라이드 | 페이지 번호 텍스트 | 위치 (top%·left%·W%·H%) | 색상 hex | 폰트 크기 | 폰트 이름 | 비고 |
|:---:|---|---|:---:|:---:|---|---|
| B01 | **없음** | — | — | — | — | <a:fld type="slidenum"> 검출 0, 좌하단(T>85% & L<30%) 영역에 짧은 숫자 텍스트 0건 |
| B02 | **없음** | — | — | — | — | 동일 |
| B03 | **없음** | — | — | — | — | 동일 |
| B04 | **없음** | — | — | — | — | 동일 |
| B05 | **없음** | — | — | — | — | 동일 |
| B06 | **없음** | — | — | — | — | 동일 |
| B07 | **없음** | — | — | — | — | 동일 |
| B08 | **없음** | — | — | — | — | 동일 |
| B09 | **없음** | — | — | — | — | 동일 |
| B10 | **없음** | — | — | — | — | 동일 |
| B11 | **없음** | — | — | — | — | 동일 |
| B12 | **없음** | — | — | — | — | 동일 |
| B13 | **없음** | — | — | — | — | 동일 |
| B14 | **없음** | — | — | — | — | 동일 |
| B15 (신설 14b) | **없음** | — | — | — | — | 신설 14b에도 페이지 번호 부재 |
| B16 (신설 14c) | **없음** | — | — | — | — | 신설 14c에도 페이지 번호 부재 |
| B17 | **없음** | — | — | — | — | 동일 |
| B18 | **없음** | — | — | — | — | 동일 |
| B19 | **없음** | — | — | — | — | 동일 |
| B20 | **없음** | — | — | — | — | 동일 |
| B21 | **없음** | — | — | — | — | 동일 |

### 페이지 번호 후보 추출 휴리스틱 (검증 절차에 명시된 3개 휴리스틱 적용 결과)

- **휴리스틱 1** (texts ≤3 문자·숫자 위주): 본 슬라이드 21장 전체 본문 텍스트 검사 결과, "1·2·3·4·7·13·3·7·6·6·5.7·5.67·100·180·148·156·89.1·94.9·11·12·14·15·16" 등 짧은 숫자 텍스트는 모두 본문 본질 수치 (가속 배율·hero number·단계 번호 등). 페이지 번호로 해석 가능한 후보 0건.
- **휴리스틱 2** (shape name 에 `page`/`pageNumber`/`slideNumber` 포함): 21장 전체 shape name 검사 — 매치 0건. 모든 shape name 은 `Text N` / `Shape N` 형식.
- **휴리스틱 3** (좌표 좌하단 영역 L<30% & T>85%): 21장 전체 검사 결과 다음 좌하단 영역 텍스트만 검출:
  - B01 L=7.5% T=86.8% "속도는벡터" (팀명, 13.5pt #475569) — 페이지 번호 아님
  - B04 L=7.9% T=88.0% "단계마다 측정 범위가 넓어지며..." (산문, 11.2pt) — 페이지 번호 아님
  - B09 L=5.9% T=89.3% "분포를 반영하면..." (산문, 12.0pt) — 페이지 번호 아님
  - B10·B12·B13·B19·B20: 좌하단 영역 산문/카드 박스 — 모두 페이지 번호 아님
  - 그 외 슬라이드는 좌하단 (L<30% & T>85%) 영역에 텍스트 자체가 0건

### XML 직접 검사 (휴리스틱 보완)

```
[ppt/slides/slide{1..21}.xml] <a:fld type="slidenum"> 검출 카운트:
  slide1.xml = 0     slide8.xml  = 0    slide15.xml = 0
  slide2.xml = 0     slide9.xml  = 0    slide16.xml = 0
  slide3.xml = 0     slide10.xml = 0    slide17.xml = 0
  slide4.xml = 0     slide11.xml = 0    slide18.xml = 0
  slide5.xml = 0     slide12.xml = 0    slide19.xml = 0
  slide6.xml = 0     slide13.xml = 0    slide20.xml = 0
  slide7.xml = 0     slide14.xml = 0    slide21.xml = 0

[ppt/notesSlides/notesSlide{1..21}.xml] <a:fld type="slidenum"> 검출:
  notesSlide1.xml  = 1 (value=1)      ...    notesSlide21.xml = 1 (value=21)
  (21장 모두 노트 슬라이드에는 페이지 번호 fld 1개씩 정상 삽입)

[ppt/slideMasters/slideMaster1.xml]
  <p:hf sldNum="0" hdr="0" ftr="0" dt="0"/>  ← 슬라이드 번호 기능 마스터 비활성
```

§1 결과: **본 슬라이드 21장 전체에 페이지 번호 shape 부재 confirm**. 노트 슬라이드에만 21장 모두 페이지 번호 fld 존재 (1~21 순서).

---

## §2. 위치 일관성

평가 불가 — 21장 모두 페이지 번호 부재이므로 위치 좌표 비교 대상 자체가 0개.

- 정본 위치 (deck 프롬프트 line 34): 좌하단 navy `#1E3A5F` — L < 30% · T > 85% 영역
- 실제 dump: 21장 모두 해당 영역에 페이지 번호 shape 0개
- 위치 표준편차: N/A (관측치 0)

---

## §3. 색상 일관성

평가 불가 — 21장 모두 페이지 번호 부재이므로 색상 비교 대상 자체가 0개.

- 정본 색상 (deck 프롬프트 line 34): navy `#1E3A5F`
- 실제 dump: 21장 모두 페이지 번호 색상 데이터 0건
- navy 매치 여부: N/A

---

## §4. 크기·폰트 일관성

평가 불가 — 21장 모두 페이지 번호 부재이므로 크기/폰트 비교 대상 자체가 0개.

- 정본 폰트 (deck 프롬프트 line 34·107): "18장의 기존 위치·크기와 동일"
- 실제 dump: 21장 모두 페이지 번호 폰트 크기·이름 데이터 0건

---

## §5. 페이지 번호 진행

평가 불가 — 21장 모두 페이지 번호 부재. 1~21 진행도 / "14b·14c" 라벨 / "B15·B16" 라벨 등 어떤 표기로도 페이지 번호 0건.

단 노트 슬라이드(스피커 노트 인쇄 페이지)에는 21장 모두 1~21 순서로 정상 페이지 번호 fld 존재 — 노트 인쇄 시에만 페이지 번호 노출되는 구조.

---

## §6. severity 종합

| ID | severity | 슬라이드 | 검출 | 정본 권고 |
|:---:|:---:|---|---|---|
| φ-1 | **critical** | B01~B21 (21장 전부) | 본 슬라이드 어디에도 페이지 번호 shape 0건. ppt/slides/slide{1..21}.xml 의 `<a:fld type="slidenum">` = 0건/슬라이드. slideMaster1.xml `<p:hf sldNum="0"/>` = 페이지 번호 기능 마스터 비활성. | 정본 deck 프롬프트 line 34 "좌하단 navy `#1E3A5F`. 18장의 기존 위치와 동일" 충족하지 않음. **수정 요청 필요** — 21장 모두 좌하단 (L≈5~10%·T≈92~95% 추정) 에 페이지 번호 텍스트 박스 신설, 색상 navy `#1E3A5F`, 폰트 Inter (또는 Apple SD Gothic Neo), 9.8~12pt 추정, 텍스트 "01/21"~"21/21" 또는 "1"~"21" 둘 중 일관된 형식 적용. <br><br>참고: 직전 18장 (223845 slide2복원본) 의 정본 페이지 번호 위치를 확인하려면 `submission/_drafts/속도는벡터_최종발표_슬라이드_20260519_223845.pptx` raw dump 가 필요. 직전 deck 도 같은 부재 상태였다면 절대 규칙 line 34 "기존 18장과 동일 위치" 가 사실상 "기존 18장도 페이지 번호 없음" 을 의미할 가능성도 있음 — 이 경우 deck 정본의 정합성 자체에 의문 — 정본 base 재해석 필요. |

### 보조 진단

claude.ai/design 의 deck 생성 동작 추정:
- claude.ai/design 은 본 슬라이드 본문에 페이지 번호를 명시 삽입하지 않음 (default behavior).
- 노트 슬라이드의 페이지 번호 fld 는 PowerPoint 의 노트 슬라이드 master 가 기본 제공.
- slideMaster1.xml 의 `<p:hf sldNum="0"/>` 으로 보아 deck 의 마스터 자체가 페이지 번호 OFF 로 설정됨 — claude.ai/design 출력의 일관된 패턴일 가능성 高.

### 정정 옵션 3가지 (수정 요청 우선순위)

1. **옵션 A (정본 충족 — 강제 권고)**: 21장 모두 좌하단 navy `#1E3A5F` 페이지 번호 텍스트 박스 신설. 18장 carry slide 와 신설 14b·14c 가 동일 위치·크기·색상. 형식 통일 (예: "1/21" / "01/21" / "1" 중 택일 후 21장 일관).
2. **옵션 B (마스터 활성)**: slideMaster1.xml `<p:hf sldNum="1"/>` 으로 변경 + slideLayout1.xml 에 슬라이드 번호 placeholder 추가. PowerPoint 표준 동작에 의존 — 색상/위치 마스터 default 사용 (navy 색상 명시 필요).
3. **옵션 C (정본 재해석)**: 직전 18장 deck (223845 슬라이드2복원본) 의 페이지 번호 상태 재확인. 만약 직전 18장도 페이지 번호 0건 이었다면 절대 규칙 line 34 의 "기존 18장과 동일 위치" 가 "기존 18장과 동일하게 페이지 번호 없음" 을 의미 — 이 경우 본 deck 의 페이지 번호 부재는 정본 충족 (PASS 로 verdict 변경). 정본 base 자체의 재해석 필요.

---

## §7. 환각 회피 룰 (handoff §6 carry — 검증자 자체 적용)

- 위치 좌표·색상·shape name 은 모두 raw_dump.md / 직접 XML 파싱 quote 그대로 (없는 것은 명시 "없음")
- navy `#1E3A5F` 의 허용 범위는 RGB 차이 ±5 이내로 정의 — 그러나 본 검증에서는 페이지 번호 자체 부재로 색상 비교 미실행
- 페이지 번호 부재는 추정이 아니라 confirm — XML 직접 검사 `grep -c '<a:fld[^>]*type="slidenum"' ppt/slides/slide${i}.xml` 결과로 검증 (21장 모두 0)
- 환각 catalog: "1/21" / "01" / "21" / "<page>" / "<#>" / `slideNumber` placeholder / "Page X of 21" 등 — 21장 본 슬라이드에서 검색 결과 모두 0건
- δ 산출물 §1·§2 (사용자 claude.ai/design 입력 준비 완료) carry 와의 정합성: δ 는 신설 14b·14c 의 본질 수치/구조 검증이며 본 φ 축은 21장 전 페이지 번호 검증 — scope 상호 보완. δ 검증 PASS 와 무관하게 본 φ 축은 critical FAIL.

---

## §8. 정본 base 인용 (verification trace)

`submission/_drafts/속도는벡터_발표deck_claudedesign_Phase2반영_20260520_095900.md` 인용:

- **line 34** (절대 규칙 7): `7. **페이지 번호 위치 고정**: 좌하단 navy '#1E3A5F'. 18장의 기존 위치와 동일.`
- **line 107** (수정 지시 코드블록 내부): `- 페이지 번호 좌하단 navy, 기존 18장과 동일 위치·크기.`
- **line 130** (검증 체크리스트 마지막 항목): `- [ ] 페이지 번호 좌하단 navy, 위치·크기 기존과 동일.`

3 출처가 모두 "좌하단 navy `#1E3A5F`" 위치를 정본으로 명시. claude.ai/design 출력은 이 3 출처를 모두 충족하지 못함 — critical FAIL.

---

## §9. 결론 한 줄

**21장 본 슬라이드에 페이지 번호 shape 0건** — deck 프롬프트 절대 규칙 line 34 "좌하단 navy `#1E3A5F`" 정본 충족 못함. critical 1건 (φ-1).

다음 action (사용자 claude.ai/design 재입력 시): 21장 모두 좌하단 (L≈5~10% · T≈92~95%) 에 페이지 번호 navy `#1E3A5F` 신설 — 직전 18장 deck (223845) 의 페이지 번호 상태 확인 후 정본 형식 ("1/21" 또는 "01/21" 또는 "1") 결정. 또는 정본 base 재해석 (옵션 C — 직전 18장도 페이지 번호 없었다면 본 deck 의 부재가 carry 정본).
