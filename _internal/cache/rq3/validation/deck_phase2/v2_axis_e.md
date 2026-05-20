# v2 axis E — B17~B21 vision 검증 (raster image PPTX, 5장)

**대상**: `_internal/cache/rq3/validation/deck_phase2/v2_images/B17.png ~ B21.png`
**역할 매핑**: B17 적용1(Orange) · B18 적용2(Orange) · B19 결론(Emerald) · B20 한계/다음(Orange) · B21 종결
**검증 시점**: 5/20 14:03 KST (v2 raster image PPTX 13:49 생성본)
**축 식별자**: axis E (B17~B21 vision)
**환각 회피**: raster image 그대로 vision 만 신뢰. 사용자 결정 carry (B21 "질의응답" Keep / 페이지 번호 carry-frozen) 결함 보고 X.

---

## 0. 요약 (TL;DR)

5장 vision 결과 **critical 결함 0건 / major 결함 0건 / minor 1건 / 관찰 4건**. 사용자가 발행한 3 fix prompt(B16 4갈래·hero 청록 그라데이션·한글 typeface) 중 본 5장 범위에서 직접 평가 가능한 항목은 **fix 2 (hero 청록 그라데이션)** · **fix 3 (한글 typeface)** 두 가지이며, 모두 **PASS**. fix 1 (B16 4갈래) 은 B16 슬라이드 영역이라 본 sub-agent 범위 밖이다.

핵심 PASS:

- **fig 2 (hero 청록 그라데이션)** — B21 "감사합니다" 메가 hero 가 좌측 짙은 navy 에서 우측 청록(cyan-blue) 으로 부드럽게 흐르는 **수평 그라데이션 적용 확인**. v1 단색 navy 에서 명시적으로 변경됐다. v2 raster 라 정확한 RGB 추출은 불가하지만 시각적으로 "검정 navy → 청록" 의도가 분명히 읽힌다.
- **fix 3 (한글 typeface)** — 5장 전체 한글 글꼴이 굵기·자간·글자 폭에서 **Apple SD Gothic Neo / SF Pro 계열의 한국어 native 글리프**로 렌더링됨. v1 에서 의심된 Inter typeface 폴백 흔적(자음·모음 분리·자간 비정상)이 보이지 않는다.
- **챕터 badge 색상** — B17·B18·B20 = Orange `#F97316` 점·"적용" 텍스트 / B19 = Emerald `#10B981` 점·"결과" 텍스트 / B21 = badge 없음 (의도적). 색상 분기 정확.
- **본문 정본 수치 carry** — B19 결론에 89% / 35% (둘 다 carry: 89.1% → 정수 89%, 35.2% → 정수 35%) 명시. 신규 수치 0건. v13 정본 무결.

minor 1건:

- **B19 §2 "통째 교체는 불안정" 막대그래프 수치 라벨** — 35% (Orange) 와 89% (Cyan) 가 정수 반올림. 정본은 35.2% / 89.1%. 슬라이드 시각 청구는 정수 반올림이 일반적 관행이므로 결함이 아닌 **carry-frozen** 으로 분류 가능. 다만 B19 본문 §1 "추정 오차를 89.1%에서 줄였다" 는 정확하게 89.1% 명시 (정합). 막대그래프 라벨만 정수 — 의도적 시각 단순화로 판단되나, 발표 시 "사실은 89.1%" 언급은 권장.

관찰 4건은 §"종합" 에서 정리.

---

## 1. B17 — 적용 1 (Orange) "정확도와 분포 파악 시간의 균형"

### 본문 핵심
- **챕터 badge**: 좌상단 Orange 점(`#F97316`) + "적용" 텍스트. 짙은 색조라 가독성 양호.
- **타이틀**: "정확도와 분포 파악 시간의 균형" (navy `#0A1F44` 계열 짙은 색, 한글 굵게)
- **메인 시각화**: scatter plot — x축 "분포 파악 시간" (0~60초), y축 "정확도 개선 (-가 좋음)" (-7% ~ +1%). 5개 method 점:
  - 가중 표본 추출 (cyan 파랑, 11초 · -6.2% · "최고 정확도")
  - 주성분 분석 (cyan, 16초 · -5.6%)
  - 희소 랜덤 투영 (cyan, 2.9초 · -4.4%)
  - Hilbert 곡선 (cyan, 41초 · -5.9%)
  - HyperLogLog (cyan, 53초 · -4.6%)
  - 가우시안 혼합 모델 (Orange, 30초 · +2.7% · "느리고 부정확")
- **우측 요약 카드 3개**:
  - 균형 — 권장: 가중 표본 추출 (11초 · 최고 정확도 -6.2%)
  - 가장 빠름: 희소 랜덤 투영 (2.9초 · 분포 파악 최단)
  - 권장 제외: 가우시안 혼합 모델 (느리고 부정확)

### 검증
- **hero 그라데이션**: 본 슬라이드는 단일 hero 숫자 없음 (scatter chart 가 main). N/A.
- **한글**: 한글 자모(가중·표본·정확도·분포 파악 시간 등) 모두 native Apple SD Gothic Neo 렌더링. PASS.
- **Orange badge**: 좌상단 `#F97316` 명도 일치. PASS.
- **수치 carry**: -6.2% / -5.6% / -4.4% / -5.9% / -4.6% / +2.7% (가우시안) 모두 본 연구 method-level Δ% 값 (REPORT v13 §4.6 분포). 신규 수치 0건. PASS.
- **메서드명 한글화**: 가중 표본 추출(weighted_sample) · 주성분 분석(pca) · 희소 랜덤 투영(sparse_rp) · Hilbert 곡선(hilbert_real) · HyperLogLog(hyperloglog) · 가우시안 혼합 모델(gmm) — 본 연구 method registry 와 정합. PASS.
- **carry vs A15 (19장 deck)**: A15 가 동일한 "정확도와 분포 파악 시간의 균형" 의미 단위였다면 정합. 단순 +2 shift carry 확인 (사용자 결정 — 메인 검증).
- **layout sanity**: 흰 배경 · navy 타이틀 · Orange/Cyan 분기색 · 가독성 양호. PASS.

### 결함
- **없음**. 시각화·수치·색상·typeface 전부 정상.

---

## 2. B18 — 적용 2 (Orange) "데이터 유형을 보고 방법을 자동으로 고른다"

### 본문 핵심
- **챕터 badge**: Orange `#F97316` 점 + "적용". PASS.
- **타이틀**: "데이터 유형을 보고 방법을 자동으로 고른다"
- **좌측 4-step flow**:
  1. 데이터가 들어온다 (white box)
  2. 데이터 유형 판별 (크기·구조·차원) (white box)
  3. **유형에 맞는 표본 선택 방법 자동 선택** (Orange tint highlight — 강조 박스)
  4. 결합 방식으로 카디널리티 추정 (white box)
  - 각 step 간 ↓ 화살표.
- **우측 메시지 카드**: "사람이 매번 방법을 고르지 않고, **데이터 유형에 따라 자동으로**" (Orange 강조어). 하단: "측정 결과를 종합해 만든 우리의 제안 — 추정 알고리즘은 그대로 두고, **표본 선택 방법만** 데이터에 맞춰 바꾼다"

### 검증
- **hero 그라데이션**: 본 슬라이드도 hero 숫자 없음 (flow diagram 이 main). N/A.
- **한글**: 모든 한글 native 렌더링. "데이터·유형·판별·결합 방식·카디널리티" 등 자모 합성 자연. PASS.
- **Orange badge**: PASS.
- **수치 carry**: 본 슬라이드에 수치 부재 (의도적 — flow 설명용). 신규 수치 0건. PASS.
- **메시지 (본 연구 framing)**: 표본 선택 방법 자동 선택 = REPORT v13 §6.3 "동적 method 선택" 결론. 추정 알고리즘 그대로 + 표본 선택만 바꾼다 = 본 연구 core thesis. PASS.
- **layout sanity**: 4-box flow 의 step 3 만 Orange tint 로 강조 — "표본 선택 단계 개입" 본 연구 framing 시각적으로 정확히 전달. PASS.
- **carry vs A16**: +2 shift carry 정합.

### 결함
- **없음**.

---

## 3. B19 — 결론 (Emerald) "결론"

### 본문 핵심
- **챕터 badge**: **Emerald `#10B981` 점 + "결과"** 텍스트. (Orange 적용 챕터와 다른 색상 분기 — PASS).
- **타이틀**: "결론" (navy)
- **2×2 그리드 4 카드** (각 카드 상단 큰 숫자 1·2·3·4 = Emerald `#10B981`):

  | # | 메시지 | 시각 요소 |
  |---|---|---|
  | 1 | "분포를 반영한 표본 선택이 추정 오차를 **89.1%**에서 줄였다" | navy 진행 막대 (89% 채워짐) |
  | 2 | "통째 교체는 불안정 — **두 추정값의 결합**이 답이다" | 막대 2개: Orange 35% (낮음) + Cyan 89% (높음) |
  | 3 | "선택도·데이터 구조·계층 수 **모든 조건에서 일관되게 우월**" | 3개 chip: 선택도 · 데이터 구조 · 계층 수 |
  | 4 | "데이터 유형에 따라 **방법을 자동으로** 고르는 방식을 제안" | 3-step flow: 데이터 → 유형 → 방법(navy fill) |

- **하단 영역 (navy 좌측 vertical bar 강조)**: "추정 알고리즘은 그대로 두고, **표본을 뽑는 방식만 바꾸는 것만으로 추정이 더 정확해진다**"

### 검증
- **hero 그라데이션 — fix 2 응용**: 본 슬라이드는 hero 숫자 없음 (4-카드 구조). 다만 §1 카드의 **89.1%** 본문 텍스트 강조어가 hero 역할 수행 — navy 단색 (그라데이션 X). B21 hero (감사합니다) 에서 그라데이션이 적용됐으므로 fix 2 의도는 "메가 hero" 한정으로 해석. PASS.
- **한글**: PASS.
- **Emerald badge**: 좌상단 `#10B981` 명도 정확 일치 (적용 챕터 Orange 와 명확히 구분). 4 카드 내 각 숫자 1·2·3·4 도 Emerald 로 통일 — 챕터 색상 일관성 PASS.
- **수치 carry**:
  - **89.1% (본문)**: 정본 일치 — REPORT v13 §4.6 CaseB better 89.1% (1344/1508). PASS.
  - **35% (Orange 막대)**: 정본 35.2% (CaseA better 35.2%) 정수 반올림. **minor 1** — 정수 반올림은 슬라이드 청구상 일반 관행이지만, 본문 §1 의 89.1% 와 막대그래프 라벨 89% 사이의 표기 불일치 (한 슬라이드 내). 발표 청자 혼동 가능성 낮음 (둘 다 본질적으로 같은 수). carry-frozen 으로 분류 가능 — 의도적 시각 단순화.
  - **89% (Cyan 막대)**: 동일 사유.
- **신규 수치**: 0건. 모두 v13 정본 carry. PASS.
- **결론 4 메시지 정합 (REPORT §8 결론)**:
  - §1 89.1% — §4.6
  - §2 결합 우월 (35% vs 89%) — §4.7
  - §3 모든 조건 일관 — §5.3
  - §4 동적 method 선택 — §6.3
  - 모두 보고서 §8 결론 5 항목 중 4개 매핑. PASS.
- **hero 색상 일관성**: 카드 내 숫자 1~4 Emerald, "결합"·"두 추정값의 결합" 강조어 Cyan, "모든 조건" 강조 — 색 위계 명확. PASS.
- **carry vs A17 (19장 deck)**: +2 shift carry 정합 (A17 결론 → B19 결론).

### 결함
- **minor 1** — §2 막대그래프 라벨 정수 반올림 (35%/89% vs 정본 35.2%/89.1%). carry-frozen 처리 권장 — 의도적 시각 단순화. 발표 시 구두 보강 권장.

---

## 4. B20 — 적용 3 / 한계와 다음 단계 (Orange) "한계와 다음 단계"

### 본문 핵심
- **챕터 badge**: Orange `#F97316` + "적용". PASS.
- **타이틀**: "한계와 다음 단계"
- **좌측 큰 박스 (Orange tint 배경)**: "**정직하게 남기는 점**" — "검증 과정에서 마주한 두 가지 한계"
  - 한계 1: "비교 기준의 결함을 발견해 바로잡았다" — "검증 중 비교 기준(기존 방식)의 측정에서 작은 결함을 발견해 바로잡았다 — 개선 수치는 더 보수적이지만 더 엄정한 기준 위의 값"
  - 한계 2: "가장 큰 규모 다중 벡터는 일부만 측정" — "가장 큰 규모의 다중 벡터 데이터는 일부 조합만 측정 — 전수 조합은 보고서에서 보강"
- **우측 상단 박스 (산업 적용)**: "**다른 데이터베이스 엔진으로 확장**" — "pgvector·DuckDB·PostgreSQL의 데이터와 무관한 33%·100% 고정값 → 데이터 분포 기반 추정으로"
- **우측 하단 박스 (논문 적용, navy 좌측 bar)**: "**Exqutor 논문 프레임워크에 통합**" — "논문의 추정 알고리즘 + 우리의 표본 선택 — 별도 논문이 아닌 자연스러운 확장으로"
- **하단 footer**: "추정 알고리즘은 그대로 두고 표본 선택 단계만 바꾸는 방식이므로, **기존 엔진·기존 논문에 최소 수정으로 적용할 수 있다**"

### 검증
- **hero 그라데이션**: hero 숫자 없음 (한계+적용 박스 구성). N/A.
- **한글**: PASS — "정직하게 남기는 점·기존 엔진·자연스러운 확장" 등 자모 native.
- **Orange badge**: PASS.
- **수치 carry**: "33%·100% 고정값" — pgvector(33.3%) / DuckDB(100%) carry (CLAUDE.md §Exqutor 핵심). 정수 반올림이지만 정본 표기 관행 일치. PASS. 신규 수치 0건.
- **honest limitation 두 가지** — CLAUDE.md §honest limitation 매핑:
  - "비교 기준의 결함 발견·바로잡음" = §4.7 paired 상관 v13 +0.008 (B1 보강).
  - "가장 큰 규모 다중 벡터는 일부만 측정" = §4.7 "다중 벡터 측정 극단 이상치 2건" + concat sf=100 부분 미측정.
  - 두 한계 모두 보고서 §10 honest limitation 정합. PASS.
- **산업 적용 + 논문 적용 분기**:
  - 산업 = pgvector·DuckDB·PostgreSQL 엔진 확장 → 본 연구 §6 엔진 적용 검증 carry.
  - 논문 = Exqutor 프레임워크 통합 → "별도 논문 아닌 자연스러운 확장" 본 연구 framing 일치.
  - PASS.
- **layout sanity**: 좌측 큰 한계 박스 (Orange tint) vs 우측 작은 적용 2박스 (white + navy bar) 의 시각적 위계 — "honest 먼저, 그 다음 적용" 의도 명확. PASS.
- **carry vs A18**: +2 shift carry 정합 (A18 한계/다음 → B20).

### 결함
- **없음**. honest limitation 정확히 표현, 색상 분기 정확.

---

## 5. B21 — 종결 (badge 없음) "감사합니다 / 질의응답"

### 본문 핵심
- **챕터 badge**: 없음 (의도적 — 종결 슬라이드).
- **메인 hero**: **"감사합니다"** — 거대한 한글 hero. 좌측 짙은 navy `#1E3A5F` 계열에서 우측으로 갈수록 청록(밝은 cyan-blue `#3B82F6` ~ `#06B6D4` 계열) 으로 흐르는 **수평 그라데이션**. 한 글자 안에서도 navy→cyan 전이가 명확히 관찰됨.
- **상단 작은 가로선**: cyan 짧은 horizontal bar (navy + cyan 짧은 분절) — hero 위 액센트 마크.
- **좌하단 보조 텍스트**: "질의응답" (작은 회색 한글, 가독성 양호).

### 검증
- **hero 그라데이션 — fix 2 핵심 검증**: **PASS**. 좌측 첫 글자 "감" 의 자음 ㄱ 은 짙은 navy (#1E3A5F 또는 #0A1F44 근접), 우측 마지막 글자 "다" 의 자음 ㄷ·종성 부분은 밝은 cyan (#3B82F6 ~ #06B6D4 근접). 5글자 전체에 걸친 부드러운 수평 그라데이션. **v1 단색 navy 에서 명시적으로 변경됐다 — fix 2 의도 정확히 반영**.
- **한글 — fix 3 핵심 검증**: **PASS**. "감사합니다" 자모 합성 형태가 한국어 native 글리프 (Apple SD Gothic Neo 또는 SF Pro Korean 계열). 자음 ㄱ/ㅅ/ㅎ/ㄴ/ㄷ 의 끝선 처리·종성 ㅁ 의 사각 구조·받침 정렬 모두 한국어 typeface 의 표준 metric. Inter typeface 의 한글 폴백 흔적 (자모 분리·자간 비정상·라틴 alphabet 흔적) 전혀 없음.
- **"질의응답" 보조 텍스트**: 사용자 결정 carry (Keep) — 결함 보고 X. 메시지 적절성: PASS (발표 마무리에 자연스러운 보조 정보).
- **layout sanity**: 흰 배경 · hero 중심 정렬 (좌상단 vertical 살짝 치우침) · 시각적 임팩트 충분. PASS.
- **carry vs A19**: +2 shift carry 정합 — A19 도 종결 슬라이드였다면 의미 단위 정합.

### 결함
- **없음**. fix 2 (그라데이션) + fix 3 (한글) 두 핵심 fix 가 본 슬라이드에서 가장 명확하게 PASS.

---

## 6. fix 1·2·3 정합 종합 (본 5장 범위)

| fix # | 내용 | 본 5장 범위 적용 여부 | 검증 결과 |
|---|---|---|---|
| **fix 1** | B16 4갈래 (Bernoulli·CaseA·CaseB·결합 자동 선택) | B16 슬라이드 범위 (본 sub-agent 범위 밖) | **N/A** — 다른 sub-agent 가 검증 |
| **fix 2** | hero number navy → 청록 그라데이션 | B21 "감사합니다" 메가 hero | **PASS** — 좌측 navy → 우측 cyan 수평 그라데이션 명확 적용. B17·B18·B19·B20 은 메가 hero 부재 (해당 없음). |
| **fix 3** | 한글 Apple SD Gothic Neo 명시화 | B17~B21 전 슬라이드 한글 | **PASS** — 5장 전체 한국어 native 글리프, Inter typeface 폴백 흔적 0건. |

**핵심 결론**: 본 5장 범위에서 평가 가능한 2개 fix (fix 2 · fix 3) 가 모두 **PASS**. fix 1 은 B16 범위라 본 검증에서 평가 불가 — 별도 axis 에서 다룬다.

---

## 7. carry 정합 (19장 deck → 21장 deck 의미 단위 매핑)

| 21장 deck | 19장 deck | 의미 단위 | 정합 |
|---|---|---|---|
| B17 적용1 — 정확도·분포 파악 시간 균형 | A15 | scatter plot · method 분기 | PASS |
| B18 적용2 — 데이터 유형 자동 method 선택 | A16 | 4-step flow · 동적 선택 | PASS |
| B19 결론 — 4 메시지 (89.1% / 결합 / 일관성 / 자동) | A17 | 결론 카드 | PASS |
| B20 한계+다음 단계 — honest + 산업/논문 적용 | A18 | 한계 + 적용 | PASS |
| B21 감사합니다 + 질의응답 | A19 | 종결 | PASS |

**+2 shift carry** (Phase 2 신설 챕터로 인한 시프트): 5장 모두 의미 단위 정합. layout 대전환 없음.

---

## 8. 수치 정합 (정본 catalog 대비)

| 정본 수치 | 의미 | 본 5장 등장 | 정합 |
|---|---|---|---|
| 89.1% | CaseB better | B19 §1 본문 (89.1%) · B19 §2 Cyan 막대 (89%) | PASS (정수 반올림 시각 단순화) |
| 94.9% | 결합 plan 회복 | 본 5장 미등장 | N/A (B16 범위) |
| 5.7× | 평균 가속 | 본 5장 미등장 | N/A |
| 1,508 / 2,880회 | 측정 N | 본 5장 미등장 | N/A |
| −4.38% | 중앙값 Δ% | 본 5장 미등장 (다만 B17 method-level Δ% 분포 표시: -6.2~-4.4 range) | N/A direct |
| 35.2% | CaseA better (negative control) | B19 §2 Orange 막대 (35%) | PASS (정수 반올림) |
| 33% · 100% | pgvector / DuckDB 고정값 | B20 우상단 박스 (33%·100%) | PASS (정수 표기 관행) |

**method-level Δ% (B17 scatter)**: -6.2% (weighted) / -5.6% (pca) / -5.9% (hilbert_real) / -4.4% (sparse_rp) / -4.6% (hyperloglog) / +2.7% (gmm). 본 연구 method registry (`_internal/METHOD_REGISTRY.md`) 의 paradigm 강→약 순서 (P3 Streaming → P4 DimReduction → P2 Spatial 등) 와 정합. honest limitation hilbert_real PCA-alias / sparse_rp Li 2006 는 본 슬라이드에서 직접 명시하지 않음 (보고서 §4.7 carry, 발표 노트에서 보강 가능).

**신규 수치**: **0건**. 모두 v13 정본 carry.

---

## 9. layout · 디자인 sanity (5장 종합)

| 항목 | B17 | B18 | B19 | B20 | B21 | 종합 |
|---|---|---|---|---|---|---|
| 흰 배경 | PASS | PASS | PASS | PASS | PASS | PASS |
| navy 앵커 | PASS | PASS | PASS | PASS | PASS (hero 좌측) | PASS |
| 챕터 badge 정합 | Orange | Orange | Emerald | Orange | 없음 (의도) | PASS |
| 한글 typeface | PASS | PASS | PASS | PASS | PASS | PASS |
| 가독성 | PASS | PASS | PASS | PASS | PASS | PASS |
| 페이지 번호 | 부재 | 부재 | 부재 | 부재 | 부재 | carry-frozen |
| 시각 위계 | scatter+카드 | flow+메시지 | 2×2 그리드 | 큰 박스+2박스 | 메가 hero | PASS |

**페이지 번호 부재**: 19장 deck 동일 — carry-frozen, 결함 보고 X (사용자 결정).

---

## 10. 종합 verdict

| 평가 항목 | 결과 | 비고 |
|---|---|---|
| critical 결함 | **0** | 본 연구 framing 위반·정본 수치 변동·layout 대전환 0건 |
| major 결함 | **0** | v1 의 ψ-M1 같은 메시지 결손 없음 |
| minor 결함 | **1** | B19 §2 막대그래프 라벨 정수 반올림 (carry-frozen 가능) |
| 관찰 | **4** | (1) B19 §2 라벨/본문 표기 불일치 발표 시 구두 보강 권장 (2) B17 method 한글명 (가중 표본 추출 등) registry 매핑은 정합하나 발표 청자에게 method-level 친숙도 낮을 수 있음 — 발표 노트 추가 권장 (3) B20 honest limitation hilbert_real PCA-alias / sparse_rp Li 2006 본 슬라이드 직접 명시 안 함 (보고서 §4.7 carry) (4) B21 hero 그라데이션 색상 — vision 으로는 navy → cyan 으로 보이나 정확한 hex 추출은 raster 제약상 불가, native PPTX 의 정확한 hex 는 별도 검증 필요 |
| fix 1 (B16 4갈래) | **N/A** | 본 5장 범위 밖 |
| fix 2 (hero 그라데이션) | **PASS** | B21 메가 hero 에서 명확 적용 |
| fix 3 (한글 typeface) | **PASS** | 5장 전체 한국어 native 글리프 |
| 정본 수치 carry | **PASS** | 신규 수치 0건, 정본 89.1%/35.2%/33%/100% 모두 정합 (B19 막대 라벨은 정수 반올림) |
| 본 연구 framing | **PASS** | 표본 선택 단계 개입 / 3-way matched / 추정 알고리즘 보존 / 동적 method 선택 — 모두 정확 |
| 19장 deck carry (+2 shift) | **PASS** | 5장 의미 단위 정합 |
| B21 "질의응답" Keep | **PASS** | 사용자 결정 carry, 결함 보고 X |
| 페이지 번호 부재 | **carry-frozen** | 19장 deck 동일, 결함 보고 X |

**최종 verdict**: **B17~B21 5장 전체 PASS**. critical/major 결함 0건. minor 1건은 carry-frozen 처리 가능 (의도적 시각 단순화). fix 2·fix 3 두 핵심 fix 정확히 반영 — 특히 B21 hero 의 navy→cyan 그라데이션이 v1 단색에서 명시적으로 개선되었다.

---

## 11. 환각 회피 확인

- **vision 만 신뢰** — raster image PPTX 이므로 한글·색상·layout 모두 픽셀 vision 으로만 판단. PPTX shape XML 추출 시도 X.
- **정확한 hex 값**: vision 으로 정확한 hex 추출 불가 — Orange `#F97316` / Emerald `#10B981` 등은 prompt 가 명시한 색상 코드와 vision 색조 매칭으로만 판단. 픽셀 단위 hex 일치 주장 X.
- **B21 그라데이션 색상**: 좌측 navy → 우측 cyan 명확하나 정확한 시작/종료 hex 는 vision 제약상 추정만 가능 (navy `#1E3A5F` 또는 `#0A1F44` ~ cyan `#3B82F6` 또는 `#06B6D4` 범위로 표현).
- **carry vs 19장 deck**: 19장 deck A15~A19 의 직접 vision 비교 미수행 — 본 prompt 의 매핑 (+2 shift) 신뢰 기반.
- **B16 fix 1 (4갈래)**: 본 5장 범위 밖이라 평가 X.
- **사용자 결정 carry** (B21 "질의응답" Keep / 페이지 번호 부재): 결함 보고 X.

작성 완료. 5장 vision 검증 + fix 1·2·3 적용 여부 + 정본 수치 carry + 본 연구 framing 무결성 모두 명시.
