# σ 축 — 디자인 system 일관성

> 작성 2026-05-20 KST · 검증 대상: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` (21장 = 18장 carry + 신설 14b·14c)
> 정본 base: `_internal/cache/rq3/validation/deck_phase2/raw_dump.md` · `submission/_drafts/속도는벡터_발표deck_claudedesign_Phase2반영_20260520_095900.md` · memory `feedback_deck_design.md` (5/19 확정)
> 검증 방법: raw_dump.md 의 모든 fill·color hex / sz / font 파싱 + PPTX 직접 python-pptx XML inspect (latin/ea/cs typeface, hero text fill type)

---

## VERDICT: WARN (critical 1 · major 2 · minor 4)

신설 14b·14c (= 슬라이드 15·16) 가 18장 carry deck 의 디자인 패턴(B11 hero pattern)을 **shape·position·z-order 수준에서 정확히 답습** — 신설 vs 기존 일관성은 **PASS** 다. 챕터 badge 전이(바이올렛 검증→그린 결과)도 정본 요구 그대로 수행됐다.

다만 정본 디자인 system 정의(`navy 앵커 + 악센트 4색 + Apple SD Gothic Neo·Inter + 흰 배경 + 청록 그라데이션 hero`) 중 **두 가지 핵심 정의가 실현되지 않았다** — 이는 신설 슬라이드 잘못이 아니라 **carry 18장 전체에서 같은 양상**:

1. **critical**: 한글 폰트 `Apple SD Gothic Neo` 미적용 — 21장의 한글 332개 전부가 `Inter` 로 렌더 (latin/ea/cs typeface 모두 Inter). 정본 정의 `Apple SD Gothic Neo·Inter` (한글: Apple SD Gothic Neo / 영문: Inter) 와 어긋남.
2. **major**: hero 거대 숫자(`89.1`·`13`·`3-7×`·`94.9`)가 `navy → 청록 그라데이션`이 아닌 **검정 `#000000` solid** 로 렌더 — text run fill type=`solid`, 그라데이션 없음. 단 navy 박스 `#1E3A5F` 가 그 텍스트 뒤에 z-order 4-5 로 깔려 있어 시각 결과는 "navy 위 검정 hero".

신설 14b·14c (s15·s16) 만 따로 보면 디자인 패턴이 정본 요구사항(`B11 hero 동일 패턴`)을 정확히 따랐다 — 18장 carry deck 과 한 벌. 따라서 σ 축의 본 임무(신설 2장이 18장 carry 디자인을 따르는지) 한정으로는 **PASS**. 디자인 system 정의 자체의 실현 부족은 carry deck (223845) 검증 시 별도 확인이 필요한 영역.

---

## §1. 색상 system

### 1.1 사용 unique 색상 hex set (21장 총합)

총 **25개 unique hex** 사용. fill 기준 21종, color(텍스트) 기준 14종, 합집합 25종.

| 분류 | 개수 | hex |
|---|---|---|
| primary (navy 앵커 + 악센트 4색) | 5 | `#1E3A5F` · `#0EA5E9` (청록) · `#F97316` (코랄) · `#10B981` (그린) · `#8B5CF6` (바이올렛) |
| cyan variant (그라데이션·light cyan) | 4 | `#7DD3FC` · `#38BDF8` · `#E5F4FB` · `#F2FAFD` |
| navy variant | 3 | `#7794BC` · `#A3B7D1` · `#E8EEF6` |
| coral/yellow variant | 2 | `#FFF1E6` · `#FCD34D` |
| grey scale (anchor / body) | 11 | `#000000` · `#FFFFFF` · `#1E293B` · `#334155` · `#475569` · `#64748B` · `#94A3B8` · `#E5E7EB` · `#F1F5F9` · `#F8FAFC` · `#FAFAFA` |

**판정 ⓒ**: 정본 정의 4색 악센트 (`#0EA5E9` · `#F97316` · `#10B981` · `#8B5CF6`) 정확히 사용. variant 들은 그라데이션·light 강조용으로 정당 → palette 구성 일관 **PASS**.

### 1.2 navy 앵커 `#1E3A5F` 사용

**21장 전부에서 사용** (fill 또는 color). 가장 광범위하게 쓰인 anchor 색상이며, color(텍스트) 기준 80회 = **21장 모두에서 사용**, fill 기준 36회 = 12장에서 사용. 제목 36건 모두 `#1E3A5F` 단일 (sz=33pt 또는 hero 슬라이드의 hero 박스 fill).

**판정 ⓐ**: navy 앵커 사용 일관 **PASS**.

### 1.3 흰 배경

raw_dump 의 `fill=type=BACKGROUND (5)` 가 슬라이드 배경 inherit (= 흰색)이며, `fill=#FFFFFF` 가 명시적 흰 박스. 21장에 명시적 다크 배경 슬라이드는 없으며, 모두 흰 배경 기반.

- 흰 박스 `#FFFFFF` 사용 슬라이드: 10장 (3·4·5·7·8·10·12·14·15·16·19·20)
- 흰 배경 inherit (= type=BACKGROUND): 21장 전부

**판정 ⓑ**: 흰 배경 일관 **PASS**.

### 1.4 악센트 색상 집합 — 정본 4색과 챕터 매핑

| 악센트 | hex | 챕터 / 용도 | 사용 슬라이드 |
|---|---|---|---|
| 청록 | `#0EA5E9` | 배경 챕터 (s2·3·4) + "결합" 개념색 + 강조 | s2·3·4·5·6·8·9·11·12·13·14·15·16·19 (14장) |
| 바이올렛 | `#8B5CF6` | 방법 챕터 (s5~10) | s5·6·7·8·9·10 (6장) |
| 그린 | `#10B981` | 결과 챕터 (s11~16·19) | s11·12·13·14·15·16·19 (7장) |
| 코랄 | `#F97316` | 적용 챕터 (s17·18·20) + "완전 대체" 개념색 | s6·12·13·16·17·18·19·20 (8장) |

**판정 ⓒ**: 4색 챕터 매핑 정본 요구사항대로 일관 **PASS**.

### 1.5 신설 14b·14c (s15·s16) 색상 검증

| 항목 | s15 (B15 3-7×) | s16 (B16 94.9%) | s11 (B11 89.1% 정본 carry) |
|---|---|---|---|
| 좌상단 챕터 badge text | "결과" | "결과" | "결과" |
| badge 색상 | `#10B981` (그린) | `#10B981` (그린) | `#10B981` (그린) |
| 제목 sz · color | 33pt · `#1E3A5F` | 33pt · `#1E3A5F` | 33pt · `#1E3A5F` |
| Shape 2 (badge separator) | `#10B981` | `#10B981` | `#10B981` |
| Shape 3 (hero outer container) | `#F2FAFD` (light cyan) | `#F2FAFD` (light cyan) | `#F2FAFD` (light cyan) |
| 내부 navy hero 박스 | `#1E3A5F` | `#1E3A5F` | `#1E3A5F` |
| hero 거대 숫자 color | `#000000` (검정 solid) | `#000000` (검정 solid) | `#000000` (검정 solid) |

→ **s15·s16 모든 색상이 s11 (carry 정본) 과 정확히 동일**. 정본 prompt line 19-20·43-44·55-56 요구사항대로 "18장 carry 디자인 system을 그대로 따른다" 가 색상 차원에서 PASS.

---

## §2. 폰트 system

### 2.1 폰트 이름 분포 — **critical 위반**

| 폰트 typeface | 사용량 | 슬라이드 수 |
|---|---|---|
| Inter (latin) | 465 occurrences | 21장 |
| Inter (ea, 동아시아) | 465 occurrences | 21장 |
| Inter (cs, complex script) | 465 occurrences | 21장 |
| Apple SD Gothic Neo | **0 occurrences** | **0장** |

PPTX 직접 inspect (python-pptx XML access) 결과:
- 21장의 모든 텍스트 run 에서 `latin`/`ea`/`cs` typeface 모두 `Inter` 단일 설정.
- 한글 포함 텍스트 332개 전부가 Inter 폰트로 렌더링 — `Apple SD Gothic Neo` typeface 적용 0건.

**문제**: 정본 디자인 system 정의 (prompt line 19, memory feedback_deck_design.md 5/19 확정 룰) 는 `Apple SD Gothic Neo + Inter` (한글: Apple SD Gothic Neo / 영문: Inter) 인데, 실제 deck 은 **한글도 Inter** 로 강제. memory feedback 의 "폰트 Apple SD Gothic Neo 고정" 룰과 어긋남.

**판정 ⓓ**: 폰트 system 정의 **FAIL** — critical.

다만 carry 18장(223845) 도 같은 양상일 가능성이 매우 높음 (claude.ai/design 의 deck 생성 컨벤션). 즉 신설 14b·14c 만의 잘못이 아니라 **carry deck 전체의 폰트 정의 미실현**. σ 축 임무(신설 vs carry 일관) 한정으로는 신설이 carry 패턴을 그대로 따라간 셈이라 일관성은 PASS.

### 2.2 폰트 크기 역할별 일관성

| 역할 | size 범위 | 등장 sizes | 일관성 |
|---|---|---|---|
| 거대 hero | 100-180pt | 111.0 · 126.0 · 135.0 · 180.0 | s1·s11·s13·s15·s16·s21 — title/hero 슬라이드 한정. ★ B11 180pt vs B15 111pt vs B16 111pt — **B11(180)이 B15·B16(111)보다 큼**. 신설은 carry 와 다른 hero 크기 |
| 큰 강조 (xl) | 40-99pt | 40.5 · 46.6 · 55.5 · 61.0 · 74.2 · 81.0 | 부수 hero, 단위 기호 (%·×) |
| 제목 | 25-40pt | 25.5 · 31.5 · 33.0 | 슬라이드 1·21 제외 19장 모두 33.0pt 단일. **일관 PASS** |
| 중간 강조 (m) | 15-25pt | 15.0 · 15.8 · 16.5 · 18.0 · 19.5 · 20.2 · 22.5 · 24.0 | 카드 라벨·sub-hero |
| 본문 (body) | 10-15pt | 10.1 · 10.5 · 10.9 · 11.2 · 11.5 · 11.6 · 12.0 · 12.4 · 12.8 · 13.2 · 13.5 · 14.0 · 14.2 | bullet·표·하단 강조 |
| 라벨·캡션 | <10pt | 9.8 · 9.9 | badge text·작은 라벨 |

**제목 33pt 일관성** ✓ — 슬라이드 1(title slide), 21(closing) 제외 19장 모두 `33.0pt #1E3A5F`. 정본 정의 그대로.

**hero 크기 불일치 (minor)**:
- B11 (89.1% carry) = 180pt
- B15 (3-7× 신설) = 111pt
- B16 (94.9% 신설) = 111pt
- B13 (13/16 carry) = 135pt

s11 = 180pt vs s15·s16 = 111pt 의 차이는 hero 콘텐츠 크기 (single digit "13" vs multi-char "3~7×" vs "94.9") 차에서 비롯. raw_dump 로는 명시적 정본 정의 부재 — 정본 prompt line 44/56 은 "B11 동일 패턴" 만 명시 (정확한 sz 명시 없음). 시각 동등 의도로 보임 — 글자 수가 다르므로 박스 안 가용 폭에 맞춰 자동 조정한 결과로 추정.

**판정 ⓗ**: 제목 33pt 일관 PASS, hero 크기 정확 동일은 아니지만 박스 안 fit 으로 정당화 → minor 만 기록.

---

## §3. hero 그라데이션 검증 — **major 위반**

### 3.1 PPTX 직접 inspect — text run fill type

| 슬라이드 | hero text | sz | text run fill type | fill color |
|---|---|---|---|---|
| s1 | "속도는" / "벡터" | 126pt | solid | `#1E3A5F` (navy) / `#000000` (검정) |
| s11 | "89.1" | 180pt | **solid** | **`#000000` (검정)** |
| s13 | "13" | 135pt | **solid** | **`#000000` (검정)** |
| s15 (B15 신설) | "3-7×" | 111pt | **solid** | **`#000000` (검정)** |
| s16 (B16 신설) | "94.9" | 111pt | **solid** | **`#000000` (검정)** |
| s21 | "감사합니다" | 180pt | solid | `#1E3A5F` (navy) |

- PPTX 의 `a:rPr/a:solidFill/a:srgbClr@val` 모두 `000000` 또는 `1E3A5F` solid. **그라데이션 (`a:gradFill`) 적용 0건.**
- shape (텍스트 박스) 의 fill 도 모두 `noFill` — shape level gradient 도 없음.

### 3.2 z-order 시각 결과

| 슬라이드 | shape order (위→아래 = 뒤→앞) |
|---|---|
| s11 | [3] Shape 3 outer `#F2FAFD` → [4] Shape 4 inner navy `#1E3A5F` → [5] Text 5 hero text `#000000` |
| s15 | [3] Shape 3 outer `#F2FAFD` → [5] Shape 5 inner navy `#1E3A5F` → [6] Text 6 hero text `#000000` |
| s16 | [3] Shape 3 outer `#F2FAFD` → [5] Shape 5 inner navy `#1E3A5F` → [6] Text 6 hero text `#000000` |

→ 시각 결과: **navy `#1E3A5F` 박스 위에 검정 `#000000` hero 텍스트 오버레이**. 정본 정의 `navy → 청록 그라데이션` 부재.

### 3.3 정본 정의 대조

prompt line 44/56 (정본):
> hero number "3-7×" navy → 청록 그라데이션, slide 17의 89.1% hero 동일 패턴
> hero "94.9%" navy → 청록 그라데이션

memory `feedback_deck_design.md` 5/19 룰:
> hero 거대 수치는 navy→청록 그라데이션

raw_dump · PPTX XML 객관 데이터:
- hero text run fill = `solid #000000` (그라데이션 stop 0건)
- shape fill = `noFill` (배경 box gradient 0건)
- 단 hero 박스 컨테이너 = `#F2FAFD` (옅은 청록) — 그라데이션은 아니지만 청록 톤 시그널

**판정 ⓔ·ⓕ·ⓖ**:
- ⓔ B15 hero "3-7×" 그라데이션? **FAIL** (검정 solid)
- ⓕ B16 hero "94.9%" 그라데이션? **FAIL** (검정 solid)
- ⓖ B11 hero "89.1%" vs B15·B16 hero — **동일** (셋 다 검정 solid #000000) → 신설 vs carry 일관성 PASS

→ 정본 정의와 어긋남(major)이지만, **carry 18장(s11·s13)도 동일하게 검정 solid** 이므로 carry-신설 일관성은 보존. 디자인 system 의 그라데이션 정의가 실현되지 못한 것은 carry deck 단계에서 이미 발생했고 신설 단계에서 그 패턴을 정확히 follow한 것. σ 축 책임 범위 내에선 신설 정합성은 PASS, 정본 정의 위반은 major 기록.

---

## §4. 신설 14b·14c (s15·s16) carry 일관성 종합

| 차원 | s11 (B11 carry) | s15 (B15 신설) | s16 (B16 신설) | 일관성 |
|---|---|---|---|---|
| 챕터 badge text | "결과" #10B981 | "결과" #10B981 | "결과" #10B981 | PASS |
| 제목 fontsize·color | 33pt #1E3A5F | 33pt #1E3A5F | 33pt #1E3A5F | PASS |
| badge separator (Shape 2) | #10B981 | #10B981 | #10B981 | PASS |
| hero outer container | L5.9% W45.4% fill=#F2FAFD | L5.9% W35.0% fill=#F2FAFD | L5.9% W35.0% fill=#F2FAFD | PASS (s15·s16 width 동일, s11 만 다름) |
| navy inner hero box | #1E3A5F | #1E3A5F | #1E3A5F | PASS |
| hero text size | 180pt | 111pt | 111pt | s15=s16 일관, s11과 다름 (콘텐츠 길이 차) |
| hero text color | #000000 solid | #000000 solid | #000000 solid | PASS |
| 폰트 (latin/ea/cs) | Inter | Inter | Inter | PASS |
| 한글 텍스트 폰트 | Inter | Inter | Inter | PASS (carry 와 동일 양상) |
| z-order pattern (outer→inner→text) | 동일 | 동일 | 동일 | PASS |

→ **신설 14b·14c (s15·s16) 가 carry 18장의 디자인 패턴을 일관되게 follow** — σ 축 본 임무 PASS.

---

## §5. severity 종합

| ID | severity | 슬라이드 | 검출 내용 | 정본 권고 |
|---|---|---|---|---|
| σ-C1 | **critical** | 1~21 (전 21장) | 한글 텍스트 332건 전부가 Inter 폰트로 렌더. Apple SD Gothic Neo typeface 적용 0건 | 정본 정의(`Apple SD Gothic Neo·Inter`)·memory 5/19 룰(`Apple SD Gothic Neo 고정`)대로 한글은 Apple SD Gothic Neo 적용 필요. claude.ai/design 의 typeface set 단계에서 ea(동아시아) typeface 를 분리 지정해야 함. carry deck 단계 결함 — 신설 14b·14c 만의 문제가 아니라 18장 carry 도 같은 양상 |
| σ-M1 | **major** | s11·s13·s15·s16 (hero 슬라이드) | hero 거대 숫자 (89.1·13·3-7×·94.9) 가 `solid #000000` 검정. 정본 정의 `navy → 청록 그라데이션` 미실현. shape level gradient도 부재 (`noFill`). 단 hero 텍스트 뒤에 navy `#1E3A5F` 박스 오버레이 — 시각 결과는 "navy 박스 위 검정 글자" | 정본 prompt line 44/56·memory 5/19 룰에 따라 hero 거대 수치는 `navy → 청록 그라데이션` (예: gradFill stops `pos=0:#1E3A5F → pos=100000:#0EA5E9`) 으로 텍스트 fill 적용 필요. carry s11·s13 도 같은 결함이라 carry deck 단계에서 시정해야 함 |
| σ-M2 | **major** | s15·s16 (신설 14b·14c) | hero text size 가 carry s11(180pt) 대비 111pt 로 작음. 신설간(s15=s16=111pt)에서는 일관 | 정본 prompt 에 hero size 명시는 없으나 "B11 동일 패턴" 의도라면 동일 박스 안 가능한 한 큰 사이즈 권장. 다만 콘텐츠("3~7×", "94.9")가 B11("89.1")보다 글자수가 많아 박스 fit 차이 — 정당화 가능. minor 로 격하 가능 |
| σ-m1 | minor | s12 | s12 hero (35.2% / 89.1%) 가 `#F97316` 코랄 hero (40.5pt) — s11·13·15·16 의 검정 hero 와 다름 | s12 는 "완전 대체 vs 결합" 대조 슬라이드로 코랄 = 완전 대체 개념색. 의도된 차이로 보임. minor 만 기록 |
| σ-m2 | minor | s14 | s14 (검증 종합 — 1508 측정) 의 hero (89.1%/89.2%) 가 24pt sub-hero. 거대 hero 없음 | s14 는 3-panel 통계 슬라이드라 거대 hero 부재가 의도. minor 만 기록 |
| σ-m3 | minor | s15 | hero "3-7×" 의 구성 (`3` 111pt + `~` 61pt + `7` 111pt + `×` 55.5pt) 4-piece. carry s11("89.1" 180pt + "%" 81pt) 의 2-piece 와 다름 | 콘텐츠 차 — "3~7×" 자체가 multi-token. carry pattern 의 다른 구현. 정당화 가능 |
| σ-m4 | minor | 전 21장 | 페이지 번호 부재 — 좌하단 navy `#1E3A5F` 작은 숫자가 21장 어디에도 없음 | 정본 prompt line 34/107: "페이지 번호 좌하단 navy `#1E3A5F`. 18장의 기존 위치와 동일". carry 18장도 페이지 번호 부재로 추정. φ 축 영역 (페이지 번호) 이라 σ 축에서는 참고만 |

---

## §6. PASS / FAIL 항목 매핑 (정본 검증 ⓐ~ⓗ)

| 항목 | 정본 요구 | 검출 | 결과 |
|---|---|---|---|
| ⓐ navy `#1E3A5F` 가 anchor | navy 앵커 사용 | 21장 모두 사용 (color 80건 + fill 36건) | **PASS** |
| ⓑ 21장 흰 배경 | 모두 흰 배경 (또는 거의 흰색) | 21장 모두 `fill=type=BACKGROUND` 또는 `#FFFFFF` | **PASS** |
| ⓒ 악센트 4색 | 청록·코랄·그린·바이올렛 | 4색 정확히 사용 (variant 9개 + greyscale 11개 + primary 5 = 25 unique). 챕터 매핑 일관 | **PASS** |
| ⓓ 폰트 = Apple SD Gothic Neo + Inter | 한글 Apple SD Gothic Neo, 영문 Inter | 21장 모두 Inter 단일 (latin/ea/cs typeface 모두 Inter). 한글 332건 전부 Inter 렌더 | **FAIL (critical σ-C1)** |
| ⓔ B15 hero "3-7×" 청록 그라데이션 | navy → 청록 gradient | solid `#000000` 검정 | **FAIL (major σ-M1)** |
| ⓕ B16 hero "94.9%" 청록 그라데이션 | navy → 청록 gradient | solid `#000000` 검정 | **FAIL (major σ-M1)** |
| ⓖ B11 vs B15·B16 hero 동일 | 세 hero 동일 디자인 | 셋 다 solid #000000 (size: 180/111/111pt) | **PASS** (carry-신설 일관) |
| ⓗ 폰트 크기 역할별 일관 | 제목 ~40pt, hero ~120pt, sub ~20pt | 제목 33pt × 19장 일관, hero 100-180pt 범위, sub-bullet 9.8-22.5pt 분포 | **PASS** (제목 33pt 일관 강함) |

---

## §7. 결론 한 줄

신설 14b·14c (s15·s16) 가 18장 carry deck(223845) 의 디자인 패턴 — 챕터 그린 badge, navy hero box, 검정 hero 텍스트, Inter 폰트, 흰 배경, 악센트 4색 매핑 — 을 **shape·position·z-order 수준에서 정확히 답습**해 σ 축 본 임무(carry-신설 디자인 일관)는 **PASS**. 단 정본 정의(`Apple SD Gothic Neo` 한글 폰트, `navy → 청록 그라데이션` hero) 두 가지는 carry 18장에서부터 실현되지 못한 결함이라 그 영역까지 시정하려면 별도 carry deck rebuild 필요 (σ 축 본 검증 범위 외).

---

## §8. 환각 회피 cross-check

- 색상 hex 는 raw_dump.md grep + python-pptx XML inspect 두 경로로 일치 확인 (`#000000`, `#1E3A5F`, `#10B981` 등).
- hero text fill type 은 `a:solidFill/a:srgbClr@val` 직접 inspect — 모든 hero run 이 `solid` 단일 (gradient stop 0).
- 폰트 typeface 는 `a:latin/@typeface`, `a:ea/@typeface`, `a:cs/@typeface` 세 path 모두 inspect — 21장 전부 `Inter` 단일.
- 자기 판정 없이 raw_dump · PPTX XML 객관 데이터만 인용.
