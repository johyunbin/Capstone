# ψ 축 — 절대 규칙 8 항목 위반 catalog

> 작성 2026-05-20 KST · 대상: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` (21 슬라이드)
> 정본 base: raw_dump.md · deck 프롬프트 line 22-35 · line 101-110 · δ 산출 §3 (line 70-105)
> 검증 범위: 21장 슬라이드 본문 텍스트 전수 (스피커 노트는 규칙 6 ★ 한정으로 OK)

---

## VERDICT: WARN (critical 0 · major 1 · minor 6)

핵심 신호:
- 슬라이드 본문 텍스트 전수 grep 결과 **규칙 1·2·3·4·6 모두 위반 0건**.
- 규칙 5(이분법) — 슬라이드 16(신설 14c)에서 4갈래 중 2갈래(베이스라인·결합)만 본문에 명시. 1건 major.
- 규칙 7(페이지 번호) — 21장 어디에도 좌하단 navy 페이지 번호 placeholder 없음. φ 축으로 위임 (catalog만).
- 규칙 8(텍스트 잘림/겹침) — 좌표 음수·100% 초과·박스 간 30%+ 중첩 = 모두 0건. hero number 박스(슬라이드 11·13·15·16·21) 5건에서 font line-height(110%×1.2 typical) > 박스 H 인 잠재 잘림 패턴 존재 → minor 5건 (단, 슬라이드 11·13·21 은 223845 슬라이드2복원본에서 이미 검증 통과한 패턴 carry).

---

## §1. 규칙 1 — 코드명 노출 금지

violation noun (deck 프롬프트 line 28): `B1`·`B-1`·`b1`·`CaseA`·`CaseB`·`Case A`·`Case B`·`case_a`·`case_b`·`oracle`·`Oracle`·`ORACLE`·`baseline`·`Baseline`·`BASELINE`·`est_b1`·`est_method`·`est_final`.

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| — | 위반 0건 | — | — | — |

검증 명령:
```bash
grep -nE 'B1|B-1|CaseA|CaseB|Case[ _-]A|Case[ _-]B|oracle|Oracle|ORACLE|baseline|Baseline|BASELINE|est_b1|est_method|est_final' raw_dump.md
# 결과: 한국어 '베이스라인 방식' (line 1000·1207) 만 검출 — 영문 코드명 0건.
```

**한글 "베이스라인 방식" 검토**: deck 프롬프트 line 28 정본 대체 라벨로 **"기본 엔진" / "베이스라인 방식" / "정답" / "결합 방식"** 이 명시되어 있음 → "베이스라인 방식"은 한국어 정본 대체 라벨로서 **위반 0**.

위반 0건. **PASS**.

---

## §2. 규칙 2 — "영역" 필러 금지

violation noun (deck 프롬프트 line 29): `검증 영역`·`결과 영역`·`분석 영역`·`측정 영역`·일반 패턴 `[명사] 영역`.

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| — | 위반 0건 | — | — | — |

검증 명령:
```bash
grep -nE '영역' raw_dump.md
# 결과: 슬라이드 본문에 '영역' 단어 자체가 0건.
```

위반 0건. **PASS**.

---

## §3. 규칙 3 — 수식 노출 금지

violation noun (deck 프롬프트 line 30): `est_final = (est_b1 + est_method) / 2.0`·`(A + B) / 2`·`/ 2.0`·`÷ 2`·`est_*` 변수명.

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| — | 위반 0건 | — | — | — |

검증 명령:
```bash
grep -nE 'est_b1|est_method|est_final|\(est|/ 2\.0|/2\.0|÷ 2|\(A \+ B\) / 2' raw_dump.md
# 결과: 0건.
```

신설 슬라이드 14b·14c(=15·16) 본문에서 "두 추정값을 평균"(line 5: line 250-252 슬라이드 5) / "결합 방식" 한국어 표현만 사용. 수식 0건. **PASS**.

---

## §4. 규칙 4 — 영문 메타 라벨 금지

violation noun (deck 프롬프트 line 31): `Phase 2`·`Phase A`·`Phase 3`·`Result matrix`·`Method comparison`·`INPUT`·`OUTPUT`·`STEP`·`PANEL`·일반 패턴 영문 NP 가 헤더·소제목·라벨에 등장.

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| — | 위반 0건 | — | — | — |

검증 명령:
```bash
grep -nE 'Phase [0-9A-Z]|Result matrix|Method comparison|^[[:space:]]+p0r[0-9]+ text="(INPUT|OUTPUT|STEP|PANEL)' raw_dump.md
# 결과: 0건.

grep -nE 'p0r[0-9]+ text="[A-Za-z]' raw_dump.md | head -30
# 검출된 영문 텍스트: pgvector·DuckDB·Exqutor·DEEP·SIFT·YFCC·SimSearchNet++·WIKI·CC3M·Hilbert·Z-order·IVF·RaBitQ·HyperLogLog·Lavallée-Hidiroglou·TPC-H·PostgreSQL·Q3·Q9·Q10·Q12 — 모두 시스템·약어·논문명·고유명사.
```

본문에 등장한 영문은 모두 시스템·데이터셋·약어·논문명 (deck 프롬프트 규칙 4 정본 대체 라벨 "엔진 적용 검증" 등 한국어 헤더 일관). 영문 메타 라벨 0건. **PASS**.

---

## §5. 규칙 5 — 이분법 금지

violation noun (deck 프롬프트 line 32): `B1 vs CaseB`·`베이스라인 vs 결합`만 강조 (4갈래 누락 시).

정본 (deck 프롬프트 line 32): **4갈래(기본엔진·베이스라인·정답·결합)** 흐름을 명시.

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| 슬라이드 16 (=신설 14c) | **2갈래(베이스라인·결합)만 본문 노출 — 4갈래 누락** | 좌 패널: `text="베이스라인 방식"` `text="7"` `text="/12"` `text="정답 계획 회복 (58%)"`. 우 패널: `text="결합 방식 13종 평균"` `text="148"` `text="/156"` `text="정답 계획 회복 (94.9%)"`. **"기본 엔진"·"정답" 갈래는 슬라이드 본문 텍스트에 없음** (정답은 회복률 평가 기준일 뿐, 4갈래의 한 항목으로 명시 안 됨). | Text 17 (L45.0%T21.1%) + Text 26 (L70.7%T21.1%) — 좌·우 2-panel 대조 패턴 | **major** |

분석:
- deck 프롬프트 line 32 정본 = "4갈래(기본엔진·베이스라인·정답·결합) 의 흐름을 명시" — 이 4갈래가 슬라이드 본문에 모두 노출되어야 함.
- 슬라이드 16의 좌·우 대조 박스(Text 17·26)에 노출된 갈래는 **"베이스라인 방식"** + **"결합 방식 13종 평균"** 만 → 2갈래.
- "정답 계획"은 회복률 평가 기준이지 4갈래의 항목이 아님.
- "기본 엔진" 갈래는 슬라이드 16 본문 텍스트에 0회 등장 (스피커 노트 line 1207 도 "두 방식이 거의 같다" 만 언급, "기본 엔진" 명시 안 함).
- 디자인 의도: 슬라이드 16은 plan recovery (=정답 계획 회복) 한정 비교 — execution time speedup 은 슬라이드 15(=14b) 가 담당 (Q3 7×·Q9 3×·Q10 6×·Q12 6× + "기본 엔진" 4회 등장).
- 즉 슬라이드 15·16 합쳐 보면 4갈래 모두 deck 전체 narrative 에 등장: 슬라이드 15에서 "기본 엔진" + "결합 방식", 슬라이드 16에서 "베이스라인 방식" + "결합 방식", 그리고 두 슬라이드 본문 헤더·메시지에 "정답 계획" 명시.
- 그러나 슬라이드 16 본문 단독으로 보면 **2갈래만 강조** = 규칙 5 정의 "두 대립 항목만 강조하는 이분법 표현" 패턴에 가까움.
- severity: major (deck 전체에서 4갈래 narrative 는 유지되지만, 슬라이드 16 단독 시각 인식 시 2-panel 대조가 dominant → 청중이 "베이스라인 vs 결합" 이분법으로 인식할 가능성).

수정 권고:
- 슬라이드 16 좌·우 대조 박스 위에 작은 문맥 라벨 "**기본 엔진**(33%·100% 고정 추정) → **베이스라인 방식**(7/12) vs **결합 방식**(148/156) — **정답 계획** 기준" 의 4갈래 흐름 도식 추가.
- 또는 슬라이드 14b(=15) 의 4단계 "추정치 → PostgreSQL 주입 → 실행 계획 변화 → 시간 측정" 도식(line 884-909) 처럼 슬라이드 16에도 좌상단에 "기본 엔진 → 베이스라인 → 결합 → 정답 회복률 비교" 4단계 도식 추가.

---

## §6. 규칙 6 — ★ 별표 금지

violation noun (deck 프롬프트 line 33): `★` (U+2605)·`☆`·`✦`·`✧`·강조 패턴 `★ [명사]` 또는 `[명사] ★`.

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| — | 위반 0건 | — | — | — |

검증 명령:
```bash
grep -nE '★|☆|✦|✧' raw_dump.md
# 결과: 슬라이드 본문·스피커 노트 모두 0건.
```

신설 슬라이드 본문에서도 ★ 별표 0건. 강조는 그라데이션(navy → 청록)·badge·navy 굵은 글씨로 처리 (예: 슬라이드 15·16 hero box `#1E3A5F` 배경 + `bold=B` + color=`#000000`/`#0EA5E9`). **PASS**.

---

## §7. 규칙 7 — 페이지 번호 좌하단 navy 위치 고정

정본 (deck 프롬프트 line 34): 좌하단 navy `#1E3A5F`. 18장의 기존 위치와 동일.

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| 슬라이드 1~21 전체 | **페이지 번호 placeholder 자체가 21장 어디에도 존재 안 함** | grep `p0r0 text="[0-9]"` 결과 모두 큰 hero 숫자(89.1·13·3~7·94.9·1·2·3·4 단계 라벨 등) — 좌하단 navy 작은 페이지 번호 0건 | — | **catalog only — φ 축 위임** |

분석:
- raw_dump.md 좌하단(L0~15%, T85~95%) 영역에 페이지 번호 box 0건 — 모두 결론 박스(`#FAFAFA`·`#1E3A5F`)·하단 메시지 텍스트만 존재.
- 즉 21장 전체에 페이지 번호 placeholder 가 부재.
- 다만 deck 프롬프트 line 34 의 "18장의 기존 위치와 동일" 조건 충족 여부 = 18장(223845 슬라이드2복원본)도 페이지 번호 없을 가능성 → φ 축에서 18장 carry 정합성 확인 후 종합 판단 필요.
- ψ 축은 위반 noun 검출 한정 — φ 축으로 위임.

**여기는 catalog 만**: 페이지 번호 위반 0/21 (위치·색상 검증) — 단, 박스 부재 자체는 carry 확인 필요.

---

## §8. 규칙 8 — 텍스트 잘림/겹침 금지

정본 (deck 프롬프트 line 35): 텍스트 box 가 슬라이드 경계 안 / 두 텍스트 box 좌표 비중첩 / 글자가 박스·다른 텍스트와 겹치지 않음.

### §8.1 슬라이드 경계 밖 (좌표 음수 또는 100% 초과)

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| — | 위반 0건 | — | — | — |

검증 명령:
```python
# raw_dump.md 의 모든 pos=L%T%W%H% 추출하여 L<0 or T<0 or L+W>100.5 or T+H>100.5 검사
# 결과: 21장 전체 0건 (모든 box 가 슬라이드 경계 내부).
```

### §8.2 텍스트 박스 간 30%+ 중첩

| 슬라이드 | 검출 | quote | 위치 | severity |
|--:|---|---|---|:--:|
| — | 위반 0건 (>30% 중첩) | — | — | — |

검증 명령:
```python
# 21장 × 모든 Text* box 쌍에 대해 IoU-style 작은 box 면적 대비 30%+ 중첩 검사
# 결과: 21장 전체 0건.
```

### §8.3 hero number box line-height vs box-height 잠재 잘림

대형 hero number 텍스트(font size 100~180pt)가 박스 H 보다 큰 line-height(font × 1.2 typical) 를 갖는 경우 시각적 잘림 가능성. typical pptx auto-fit 으로 처리되나 carry 검증 필요.

| 슬라이드 | font | box H | line-H | 차이 | 위치 | severity |
|--:|--:|--:|--:|--:|---|:--:|
| 슬라이드 11 | 180pt (`89.1`) | 161.5pt | 216pt | +54.5pt | Text 5 (L8.0%T28.9%W42.6%H29.9%) | **minor (carry from 223845)** |
| 슬라이드 13 | 135pt (`13`) | 138.2pt | 162pt | +23.8pt | Text 3 (L5.9%T30.7%W34.0%H25.6%) | **minor (carry from 223845)** |
| 슬라이드 15 (신설 14b) | 111pt (`3~7×`) | 100.4pt | 133pt | +32.6pt | Text 6 (L7.8%T33.4%W32.2%H18.6%) | **minor (신설)** |
| 슬라이드 16 (신설 14c) | 111pt (`94.9%`) | 100.4pt | 133pt | +32.6pt | Text 6 (L7.8%T26.4%W32.2%H18.6%) | **minor (신설)** |
| 슬라이드 21 | 180pt (`감사합니다`) | 168.5pt | 216pt | +47.5pt | Text 1 (L7.5%T29.8%W87.5%H31.2%) | **minor (carry from 223845)** |

분석:
- 5건 모두 hero number 디자인 패턴 — auto-fit 또는 line-height 110% 적용 시 시각적으로 박스 내 정상 표시 가능.
- 슬라이드 11·13·21 = 223845 슬라이드2복원본의 기존 hero 패턴 carry — 이미 검증 통과 (handoff 0054 §3 carry 명시).
- 슬라이드 15·16 = 신설 hero — 동일 디자인 패턴 사용 → carry 동등 안전성 추정. 실제 PPTX 렌더링 시 글자가 박스 위·아래로 살짝 튀어나오는지는 사용자 시각 확인 필요.
- severity: minor (산출물 품질 영향 최소 — pptx auto-fit 으로 자동 처리될 가능성 높음).

수정 권고 (옵션):
- 슬라이드 15·16 hero box H 를 18.6% → 22%~24% 로 증가 (= 박스 높이 100.4pt → 119pt~130pt) — line-height 133pt 와 매칭.
- 또는 font size 111pt → 95pt 로 축소.
- 또는 PPTX 내부 `<a:bodyPr>` 의 `wrap="none"` + 텍스트 box 좌표를 hero 박스 좌표보다 좀 더 크게 (offset −5pt) 설정.

---

## §9. severity 종합

| ID | severity | 규칙 | 슬라이드 | quote | 정본 권고 |
|--:|:--:|--:|:--:|---|---|
| ψ-1 | **major** | 규칙 5 이분법 | 슬라이드 16 (=신설 14c) | `text="베이스라인 방식"` (L45.0%T21.1%) + `text="결합 방식 13종 평균"` (L70.7%T21.1%) — 4갈래 중 2갈래만 본문 노출 | 슬라이드 16 좌상단에 "기본 엔진 → 베이스라인 → 결합 → 정답 회복률" 4단계 도식 추가 또는 4갈래 흐름 문맥 라벨 추가 |
| ψ-2 | minor | 규칙 7 페이지 번호 부재 | 21장 전체 | placeholder 자체 0건 (catalog only) | φ 축에서 18장 carry 정합성 검증 후 종합 판단 |
| ψ-3 | minor | 규칙 8 hero font overflow | 슬라이드 11 | Text 5 (L8.0%T28.9%H29.9%) font 180pt vs box 161.5pt | 223845 carry — auto-fit 검증 |
| ψ-4 | minor | 규칙 8 hero font overflow | 슬라이드 13 | Text 3 (L5.9%T30.7%H25.6%) font 135pt vs box 138.2pt | 223845 carry — 매칭 |
| ψ-5 | minor | 규칙 8 hero font overflow | 슬라이드 15 (=신설 14b) | Text 6 (L7.8%T33.4%H18.6%) font 111pt vs box 100.4pt | 신설 — auto-fit 검증 또는 box H 22%로 증가 |
| ψ-6 | minor | 규칙 8 hero font overflow | 슬라이드 16 (=신설 14c) | Text 6 (L7.8%T26.4%H18.6%) font 111pt vs box 100.4pt | 신설 — auto-fit 검증 또는 box H 22%로 증가 |
| ψ-7 | minor | 규칙 8 hero font overflow | 슬라이드 21 | Text 1 (L7.5%T29.8%H31.2%) font 180pt vs box 168.5pt | 223845 carry — auto-fit 검증 |

---

## §10. 본문 영역 vs 메타 영역 분리 (δ 산출 §3 패턴 carry)

- **본문 영역** = 슬라이드 1~21 의 모든 paragraph·run 텍스트 + 스피커 노트(규칙 6 ★ 한정).
- **메타 영역** = pptx 슬라이드 마스터·테마 이름·layout placeholder name·shape `name='Text 17'` 등 — ψ 축에서 관용.
- 한국어 본문 안에 영문 단어 자연 혼용 (`pgvector`·`DuckDB`·`PostgreSQL`·`Exqutor`·`TPC-H`·`Q3`·`Q9`·`Q10`·`Q12`·`DEEP`·`SIFT`·`YFCC`·`WIKI`·`CC3M`·`SimSearchNet++`·`Hilbert`·`Z-order`·`IVF`·`RaBitQ`·`HyperLogLog`·`Lavallée-Hidiroglou`) = 시스템·약어·고유명사 = **위반 0**.

---

## §11. PASS / WARN / FAIL 판정 근거

**VERDICT: WARN (critical 0 · major 1 · minor 6)**

| 규칙 | 결과 | 종합 |
|--:|:--:|---|
| 1 코드명 노출 | PASS | 영문 코드명 0건. 한글 "베이스라인 방식" = 정본 대체 라벨 |
| 2 "영역" 필러 | PASS | "영역" 단어 0건 |
| 3 수식 노출 | PASS | est_*·/2.0 0건 |
| 4 영문 메타 라벨 | PASS | Phase 2·Result matrix·INPUT 등 0건. 본문 영문 = 모두 시스템·약어 |
| 5 이분법 | **WARN** | 슬라이드 16 단독 시 2갈래(베이스라인·결합) dominant — major 1건 |
| 6 ★ 별표 | PASS | ★·☆·✦·✧ 0건 |
| 7 페이지 번호 | catalog | placeholder 부재 — φ 축 위임 |
| 8 텍스트 잘림/겹침 | minor 5건 | hero font line-height > box H 패턴 (4건 223845 carry, 2건 신설 동등 안전성) |

**critical 0 · major 1 · minor 6** — 신설 슬라이드 2장 본문에서 핵심 절대 규칙 8 중 7개 PASS, 1건 major(이분법 규칙 5) 보완 권고 + 5건 minor(hero font overflow) carry/검증 권고.

---

## §12. 검증 명령 carry (재현용)

```bash
cd /Users/hyunbin/Capstone/_internal/cache/rq3/validation/deck_phase2

# 규칙 1 코드명
grep -nE 'B1|B-1|CaseA|CaseB|Case[ _-]A|Case[ _-]B|oracle|Oracle|ORACLE|baseline|Baseline|BASELINE|est_b1|est_method|est_final' raw_dump.md

# 규칙 2 "영역"
grep -nE '영역' raw_dump.md

# 규칙 3 수식
grep -nE 'est_b1|est_method|est_final|\(est|/ 2\.0|/2\.0|÷ 2|\(A \+ B\) / 2' raw_dump.md

# 규칙 4 영문 메타
grep -nE 'Phase [0-9A-Z]|Result matrix|Method comparison' raw_dump.md
grep -nE 'p0r[0-9]+ text="[A-Za-z]' raw_dump.md  # 시스템·약어 화이트리스트 검토

# 규칙 5 이분법 (4갈래 흐름)
grep -nE '완전 대체|결합|기존 방식|베이스라인|정답|기본 엔진' raw_dump.md

# 규칙 6 ★
grep -nE '★|☆|✦|✧' raw_dump.md

# 규칙 7·8 좌표 분석 (Python)
# §8.1 경계 밖 검출: pos=L(\d)%T(\d)%W(\d)%H(\d)% → L<0 or T<0 or L+W>100.5 or T+H>100.5
# §8.2 박스 중첩: 모든 Text* 쌍에 대해 작은 box 면적 대비 30%+ 중첩 검출
```

---

## §13. 환각 회피 — quote 무결성 확인

모든 quote 는 raw_dump.md 원문 verbatim 확인:
- line 1000: `    p0r0 text="베이스라인 방식" sz=9.8pt font=Inter bold=B color=#F97316` ✓ ψ-1
- line 1018: `    p0r0 text="148" sz=25.5pt font=Inter bold=B color=#0EA5E9` ✓ ψ-1 (대조 박스 우측)
- line 555-557: `    p0r0 text="89.1" sz=180.0pt ... p0r1 text="%" sz=81.0pt` ✓ ψ-3
- line 644-645: `    p0r0 text="13" sz=135.0pt ... p0r1 text="/ 16" sz=74.2pt` ✓ ψ-4
- line 868-871: `    p0r0 text="3" sz=111.0pt ... p0r3 text="×" sz=55.5pt` ✓ ψ-5
- line 983-984: `    p0r0 text="94.9" sz=111.0pt p0r1 text="%" sz=46.6pt` ✓ ψ-6
- line 1424: `    p0r0 text="감사합니다" sz=180.0pt` ✓ ψ-7

자기 판정 0건 — 모든 위반 raw_dump quote + 위반 noun 직접 매칭.

---

## §14. 끝맺음

ψ 축 검증 종합: 21장 deck 신본은 절대 규칙 8 항목 가운데 **7개 PASS · 1개 WARN (규칙 5 이분법, 슬라이드 16)** + **5건 minor (규칙 8 hero font overflow, 4건 223845 carry / 2건 신설)**.

다음 단계:
- main 세션이 사용자 시각 확인으로 슬라이드 11·13·15·16·21 hero number 렌더링 검증 (PPTX 또는 PDF 렌더 후 visual check).
- 슬라이드 16 의 4갈래 흐름 보완 (claude.ai/design 에 추가 수정 지시 또는 다음 deck 신본 빌드 시 반영).
- φ 축에서 페이지 번호 carry 정합성 (223845 슬라이드2복원본 18장 vs 신설 2장) 종합 판정.
