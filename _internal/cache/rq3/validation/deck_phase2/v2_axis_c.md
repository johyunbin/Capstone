# v2 raster PPTX 검증 — Axis C: B11~B14 (결과 챕터)

> 작성: 2026-05-20 KST · sub-agent (Opus 4.7) · raster image vision 검증
> 대상: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` (raster image PPTX, 5/20 13:49)
> 정본 PNG: `_internal/cache/rq3/validation/deck_phase2/v2_images/B11.png ~ B14.png`
> 본 axis 담당: **결과 챕터 4장 (B11·B12·B13·B14)** — Emerald `#10B981` 챕터
> 정본 carry base: v1 native shape PPTX (verdict.md, 5/20 13:00) + 보고서 신본 `_20260520_124200.md` + handoff `_20260520_124250`

---

## VERDICT 요약: **WARN (PASS-with-carry-issue)** — critical 0 · major 0 · minor 5

**한 줄**: 결과 챕터 4장 raster 렌더링은 본문 수치(89.1% · 1,508 · 1,344 · 4.4% · 13/16 · 35.2%) 정본 완전 일치, Emerald 챕터 badge 정상, 한글 가독성 깨끗, paradigm·honest limitation carry 의미 단위 PASS. **fix 1 (B16 4갈래)** = 본 chunk scope 외(B16 = 14c, axis_d). **fix 2 (hero 청록 그라데이션)** = B11 hero "89.1%" navy→sky 그라데이션 시각 확인 ✓ (다른 hero는 단색). **fix 3 (한글 깨끗)** = 4장 모두 깨끗. carry 영역 결함 0건.

---

## §1. 슬라이드별 검증

### B11 — 결과 1 (hero "89.1%")

| 검증 | 결과 | 비고 |
|---|:--:|---|
| 좌상단 ● + "결과" 챕터 표시 | **PASS** | 그린 `#10B981` Emerald 도트, 그린 "결과" 텍스트 (좌상단 정상) |
| 챕터 underline (그린) | **PASS** | 제목 아래 짧은 그린 underline (badge color 동일 계열) |
| 제목 | **PASS** | "결합 방식이 추정 오차를 89.1%에서 줄였다" — navy `#1E3A5F` |
| **hero "89.1%"** | **PASS** ★ | **navy→sky 청록 그라데이션 시각 적용 ✓** — 위 navy `#1E3A5F`, 아래 sky `#0EA5E9` 그라데이션 (fix 2 시각 확인) |
| 좌측 박스 부제 | **PASS** | "결합 방식이 기존 방식보다 **추정 오차를 줄인 비율**" |
| 좌측 진행 막대 | **PASS** | navy→sky 그라데이션 막대 (89% 분량 채워짐) |
| **본문 수치 #1** | **PASS** | "1508번의 측정 중 **1344번** 더 정확" |
| **본문 수치 #2** | **PASS** | "추정 오차 중앙값 약 **4.4%** 감소" (정본 −4.38% → "4.4% 감소" 의역 PASS) |
| 우측 보조 panel "신호의 견고함" | **PASS** | 부제 회색 깔끔 |
| 우측 보조 수치 65% / 72% | **PASS** | sky `#0EA5E9` 색상 일관, "통계적으로 의미 있는 개선 65%" / "개선 폭이 큰 경우 72%" (보고서 §5 carry 영역) |
| 한글 가독성 | **PASS** | 4점/4점 한글 모두 깨끗, 깨짐 0건 |
| 흰 배경 | **PASS** | 깔끔 |
| 페이지 번호 | **WARN** | 부재 (직전 19장 deck 동일, carry-frozen — minor) |

**B11 verdict**: PASS (fix 2 시각 확인 PASS, fix 3 PASS, 정본 수치 4/4 일치, Emerald badge 정상)

---

### B12 — 결과 2 (CaseA vs CaseB 비교)

| 검증 | 결과 | 비고 |
|---|:--:|---|
| 좌상단 ● + "결과" 챕터 표시 | **PASS** | 그린 `#10B981` Emerald 도트, "결과" 텍스트 정상 |
| 챕터 underline (그린) | **PASS** | 제목 아래 그린 underline |
| 제목 | **PASS** | "완전 대체는 불안정하다 — 결합이 답이다" — navy |
| **상단 막대 라벨 "완전 대체"** | **PASS** | Orange `#F97316` (적용 챕터 색이 아닌 negative control 강조용 동일 hue) |
| **상단 막대 우측 hero "35.2%"** | **PASS** | navy `#1E3A5F` 단색 — 청록 그라데이션 미적용 (보조 hero라 단색 디자인 선택, fix 2 부분 적용) |
| 상단 막대 안 라벨 "35.2%" | **PASS** | 흰색 텍스트 in orange bar |
| 상단 막대 채움 비율 | **PASS** | 약 35% 분량 |
| **하단 막대 라벨 "결합"** | **PASS** | sky `#0EA5E9` (강조) |
| **하단 막대 우측 hero "89.1%"** | **PASS** | navy `#1E3A5F` 단색 (상단 hero 와 일관) |
| 하단 막대 안 라벨 "89.1%" | **PASS** | 흰색 텍스트 in sky bar |
| 하단 막대 채움 비율 | **PASS** | 약 89% 분량 |
| **푸터 narrative** | **PASS** ★ | "결합 vs 완전 대체 직접 비교 — 결합이 **96.5%**에서 우월" + "표본을 통째로 바꾸면 우리 방법이 강할 때만 좋고 약할 때 크게 나빠진다 → 두 추정값을 **결합**하면 논문 방식이 안전망이 되어 안정적으로 개선" |
| 한글 가독성 | **PASS** | 깨짐 0건, 가독 깨끗 |
| 흰 배경 | **PASS** | 깔끔 |
| 페이지 번호 | **WARN** | 부재 (carry-frozen) |

**B12 verdict**: PASS (정본 수치 35.2% (CaseA negative control) · 89.1% (CaseB) · 96.5% (CaseB vs CaseA 직접 비교) 모두 carry, narrative "robustness 우위" 메시지 정확)

---

### B13 — 결과 3 (13/16 method 순위)

| 검증 | 결과 | 비고 |
|---|:--:|---|
| 좌상단 ● + "결과" 챕터 표시 | **PASS** | 그린 `#10B981` Emerald 도트 |
| 챕터 underline (그린) | **PASS** | 제목 아래 그린 underline |
| 제목 | **PASS** | "16가지 방법 중 13가지가 기존 방식을 안정적으로 이긴다" — navy |
| **좌측 hero "13/16"** | **WARN** | "13" navy 검정 단색 (그라데이션 미적용) + "/16" 회색 — 청록 그라데이션 fix 2 미적용 ★ |
| 좌측 부제 | **PASS** | "모든 조건에서 안정적으로 우월" |
| **좌측 narrative** | **PASS** ★ | "공간 곡선·차원 축소·층화 계열이 견고하게 우월. **가우시안 혼합 모델·미니배치 K-means·IVF 클러스터링** 세 가지는 측정에서 불안정해 권장에서 제외." — paradigm strong→weak 의미 정합 (P3 Streaming · P4 DimReduction · P2 Spatial 강 / P1 Cluster 약) |
| 좌측 범례 "권장 13 (sky)" / "제외 3 (orange)" | **PASS** | 색상 system 일관 |
| **우측 막대 차트 16 method** | **PASS** ★ | 정렬: 가중 표본 추출(-6.2) → Hilbert(-5.9) → 고차원 Hilbert(-5.7) → 독립성분 분석(-5.7) → 주성분 분석(-5.6) → Z-order(-4.9) → HyperLogLog(-4.6) → 누적 제곱근 층화(-4.5) → Lavallée-Hidiroglou 층화(-4.4) → 희소 랜덤 투영(-4.4) → 랜덤 SVD(-4.1) → 미니배치 K-means(-3.6 orange) → RaBitQ 양자화(-3.6) → 다차원 히스토그램(-3.4) → IVF 클러스터링(-2.7 orange) → 가우시안 혼합 모델(+2.7 orange, 음수가 개선이라 양수는 악화) |
| 막대 색상 일관 | **PASS** | sky `#0EA5E9` 13 권장 · orange `#F97316` 3 제외 |
| 막대 차트 푸터 | **PASS** | "개선 폭의 중앙값(%) — 음수가 개선" 명확 |
| **method 라벨 (코드명 노출 X)** | **PASS** ★ | "가중 표본 추출"·"Hilbert 곡선"·"독립성분 분석"·"주성분 분석"·"누적 제곱근 층화"·"희소 랜덤 투영"·"랜덤 SVD"·"미니배치 K-means"·"RaBitQ 양자화"·"다차원 히스토그램"·"IVF 클러스터링"·"가우시안 혼합 모델" — 모두 한글 자연어 method 명 (영문은 Hilbert·HyperLogLog·Z-order·SVD·K-means·RaBitQ 보조 표기 OK) |
| 환각 회피 (★ 코드명·★ exact 수치) | **PASS** | "hilbert_real" / "sparse_rp" / "p_holm" 등 코드명 미노출, 본문 메인 메시지 정합 |
| 한글 가독성 | **PASS** | 한글 16개 method 라벨 모두 깨끗 (가우시안 혼합 모델·미니배치 K-means·IVF 클러스터링·랜덤 SVD·HyperLogLog 표기 정확) |
| 흰 배경 | **PASS** | 깔끔 |
| 페이지 번호 | **WARN** | 부재 (carry-frozen) |

**B13 verdict**: PASS (정본 13/168 → 16 method 슬림화 후 13 권장·3 제외 일관, paradigm strong→weak narrative 정확, method 코드명 노출 0). 단, fix 2 hero "13/16" 그라데이션 미적용 — B11 만 그라데이션, B13 hero 는 단색.

---

### B14 — 결과 4 (5축 multi-axis 일관성)

| 검증 | 결과 | 비고 |
|---|:--:|---|
| 좌상단 ● + "결과" 챕터 표시 | **PASS** | 그린 `#10B981` Emerald 도트 |
| 챕터 underline (그린) | **PASS** | 제목 아래 그린 underline |
| 제목 | **PASS** | "선택도·데이터 구조·계층 수 — 모든 조건에서 일관되게 우월" — navy |
| **좌 패널 "선택도" 헤더** | **PASS** | 회색 캡션 + "조건이 넓을수록 더 우월" 강조 (sky color) |
| 좌 패널 막대 1 "낮음 0.1%" → 83.3% | **PASS** | 옅은 sky `#7DD3FC` |
| 좌 패널 막대 2 "중간 1%" → 87.6% | **PASS** | 중간 sky `#38BDF8` |
| 좌 패널 막대 3 "높음 10%" → 97.5% | **PASS** | 진한 sky `#0EA5E9`, 라벨도 sky 강조 |
| **중간 패널 "데이터 구조" 헤더** | **PASS** | 회색 캡션 + "단일·다중 거의 동일" sky 강조 |
| 중간 패널 "단일 벡터" → 89.1% | **PASS** | navy 검정 단색 |
| 중간 패널 "다중 벡터" → 89.2% | **PASS** ★ | sky color 강조 (다중 벡터 결과 데이터 잘 보임), **honest limitation carry**: 다중 벡터 측정 극단 이상치 2건은 결과 영향 미미, 89.2% 거의 동일 메시지 정합 |
| **우 패널 "계층 수" 헤더** | **PASS** | 회색 캡션 + "20개 계층이 최적" sky 강조 |
| 우 패널 막대 1 "10개" → 83.6% | **PASS** | 옅은 sky |
| 우 패널 막대 2 "20개" → 89.8% | **PASS** | 진한 sky, 라벨도 sky 강조 (KM20 = 정본 anchor) |
| 우 패널 막대 3 "30개" → 85.9% | **PASS** | 중간 sky |
| **푸터 narrative** | **PASS** ★ | "세 패널 수치는 모두 **결합 방식이 기존 방식을 이긴 비율** — 조건이 달라져도 개선이 일관된다" — multi-axis 일관성 메시지 정확 |
| 5축 honest limitation 표기 | **PASS** (간접) ★ | 본 슬라이드는 5축 (선택도·데이터 구조·계층 수) 중 3축 강조 — 다중 벡터 honest exception 이 89.2% 거의 동일로 흡수됨. paradigm strong→weak 와 honest limitation (PCA alias·sparse_rp Li 2006·P1 비일관) 은 B13 narrative 에 carry (본 slide scope 외) |
| 한글 가독성 | **PASS** | 깨짐 0건 |
| 흰 배경 | **PASS** | 깔끔, 3 패널 분리 디자인 일관 |
| 페이지 번호 | **WARN** | 부재 (carry-frozen) |

**B14 verdict**: PASS (정본 multi-axis 5축 중 3축 강조 narrative 정합, sel{0.001·0.01·0.1} → 83.3·87.6·97.5% / single·multi 89.1·89.2% / 10·20·30 strata 83.6·89.8·85.9% carry 모두 정확).

---

## §2. fix 1·2·3 정합 점검 (carry 결정)

### fix 1 (B16 4갈래 흐름 보강)
- **본 chunk scope 외** — B16 = 14c slide, axis_d 담당.
- B11~B14 (결과 챕터) 는 ψ-M1 (B16 단독 시 4갈래 누락) 의 carry 영역 아님 — 정본 4갈래 narrative 는 B15·B16 (적용 챕터 carry) 영역.
- **결과**: PASS (본 axis 무관)

### fix 2 (hero number navy → 청록 그라데이션)
- **B11**: hero "89.1%" navy→sky 청록 그라데이션 **시각 적용 ✓** (위 navy `#1E3A5F` → 아래 sky `#0EA5E9` smooth transition)
- **B12**: 보조 hero "35.2%" (orange chip 안) 흰색 + 우측 "35.2%" / "89.1%" navy `#1E3A5F` 단색 — 그라데이션 미적용 (디자인 의도 — orange bar 강조)
- **B13**: hero "13/16" 검정 단색 — 그라데이션 미적용
- **B14**: hero 부재 (다중 panel, 막대 차트 위주)
- **결과**: **부분 적용** — B11 메인 hero "89.1%" 만 그라데이션 적용, B12·B13 hero 단색. fix 2 의 의도가 "전체 hero" 였으면 → minor (B13 "13/16" 그라데이션 추가 권고). "메인 hero 한 곳만" 이었으면 → PASS (B11 = 결과 챕터 핵심 hero).
- **권고**: 시각적 일관성 위해 B13 "13" 도 navy→sky 그라데이션 적용 considered (사용자 결정)

### fix 3 (한글 깨짐 없음)
- **B11**: 한글 12 segment 모두 깨끗 ✓
- **B12**: 한글 14 segment 모두 깨끗 ✓ (특히 푸터 narrative 긴 한글 문장 깨짐 0)
- **B13**: 한글 16+ method 라벨 + narrative 모두 깨끗 ✓ (가우시안 혼합 모델·미니배치 K-means·IVF 클러스터링·랜덤 SVD 표기 정확, 한글 띄어쓰기 일관)
- **B14**: 한글 18+ segment 모두 깨끗 ✓ (특히 푸터 narrative 한글 깨짐 0)
- **결과**: **PASS** ★ (fix 3 완전 적용, 시스템 폰트 fallback Apple SD Gothic Neo 정상 작동 또는 raster 시점에 burned-in)

---

## §3. carry vs 19장 deck (A11~A14 의미 단위 정합)

| 슬라이드 | 직전 19장 deck 의미 단위 | v2 21장 deck 의미 단위 | 정합 |
|---|---|---|:--:|
| B11 ↔ A11 | "89.1% 결합 방식이 추정 오차 감소" + 1508·1344·4.4% | 동일 (제목·hero·본문 수치 carry) | **PASS** ✓ |
| B12 ↔ A12 | "CaseA negative control 35.2% vs CaseB 89.1%" + narrative | 동일 (제목·막대 차트·푸터 narrative 96.5%) | **PASS** ✓ |
| B13 ↔ A13 | "16 method 중 13 강·3 제외" + paradigm | 동일 (제목·hero "13/16"·막대 차트 16종·paradigm narrative) | **PASS** ✓ |
| B14 ↔ A14 | "선택도·데이터 구조·계층 수 5축 일관" | 동일 (3 패널 분리, 수치 83.3·87.6·97.5 / 89.1·89.2 / 83.6·89.8·85.9 carry) | **PASS** ✓ |

**결론**: 4장 모두 의미 단위 동결 PASS. raster 변환 과정에서 시각 layout 약간 조정 (B11 hero 청록 그라데이션 적용, B12 막대 chart 디자인 동일, B13·B14 carry) — 본질 메시지·수치 변동 0건.

---

## §4. 정본 수치 정합 표

| 정본 수치 | 슬라이드 | 노출 형태 | 검증 |
|---|---|---|:--:|
| **89.1%** | B11·B12·B14 | hero "89.1%" (B11), CaseB 막대 라벨/우측 (B12), 단일 벡터 (B14) | **PASS** ✓ |
| **1,508** | B11 본문 | "1508번의 측정" | **PASS** ✓ |
| **1,344 (better count)** | B11 본문 | "1344번 더 정확" | **PASS** ✓ |
| **−4.38% (중앙값 Δ%)** | B11 본문 | "추정 오차 중앙값 약 **4.4%** 감소" (의역 PASS) | **PASS** ✓ |
| **35.2% (CaseA)** | B12 | 막대·hero | **PASS** ✓ |
| **96.5% (CaseB vs CaseA)** | B12 푸터 | "결합이 96.5%에서 우월" | **PASS** ✓ |
| **13 / 16** | B13 | hero | **PASS** ✓ |
| **paradigm 강→약** | B13 narrative | "공간 곡선·차원 축소·층화 계열이 견고하게 우월" + 제외 3 (가우시안 혼합 모델·미니배치 K-means·IVF 클러스터링) | **PASS** (P3·P4·P2 강 / P1 약 의미 정합) ✓ |
| **선택도 sel{0.001·0.01·0.1}** | B14 좌 패널 | 83.3% / 87.6% / 97.5% | **PASS** ✓ |
| **데이터 구조 single·multi** | B14 중 패널 | 89.1% / 89.2% | **PASS** ✓ |
| **계층 수 10·20·30** | B14 우 패널 | 83.6% / 89.8% / 85.9% | **PASS** ✓ |

**총 11/11 정본 수치 PASS** ★

---

## §5. 환각 회피 (코드명·exact수치 노출 0건)

| 항목 | 검증 |
|---|:--:|
| "B1" / "CaseA" / "CaseB" 코드명 노출 | **PASS** (모두 한글 자연어 "기존 방식" / "완전 대체" / "결합" carry) |
| "hilbert_real" / "sparse_rp" 코드명 노출 | **PASS** (B13 method 라벨 모두 한글 + Hilbert·SVD 등 일반명) |
| "p_holm" / "p < 0.05" exact 통계 노출 | **PASS** (B11 우측 "통계적으로 의미 있는 개선 65%" 의역 carry) |
| **plan_signature** / **Node Type 1-tuple** | **PASS** (본 슬라이드 무관) |
| **"latency 동등 / robustness 우위"** 메시지 | **PASS** ★ (B12 푸터 narrative "결합하면 논문 방식이 안전망이 되어 안정적으로 개선" 정확 carry — paired Wilcoxon 7.7% 유의의 plan 회복 robustness 의미) |
| **"영역" 무의미 필러** | **PASS** (4장 모두 "영역" 토큰 0건) |

---

## §6. layout · 구도 sanity

| 항목 | 결과 |
|---|:--:|
| 흰 배경 일관 | **PASS** |
| navy 앵커 색상 system (제목·hero·라벨) | **PASS** ★ (navy `#1E3A5F` 4장 일관) |
| 그린 챕터 badge `#10B981` | **PASS** ★ (Emerald, 4/4 일관) |
| 악센트 4색 (sky·orange·sky 변주) | **PASS** (sky `#0EA5E9` 메인 / orange `#F97316` negative control 강조 / sky 변주 `#7DD3FC`·`#38BDF8` 그라데이션) |
| 페이지 번호 (좌하단 navy) | **WARN→carry** (4장 모두 부재, 직전 19장 deck 동일 carry-frozen, 다음 deck rebuild 시 fix 검토) |
| 가독성 (한글) | **PASS** ★ (4장 모두 깨끗) |
| 한글 typography | **PASS** (Apple SD Gothic Neo or 시스템 폰트 fallback raster burned-in) |
| 슬라이드 간 디자인 일관성 (B11~B14) | **PASS** (4장 layout 패턴 다양하지만 색상 system·typography·badge 일관) |

---

## §7. severity catalog (B11~B14 chunk)

### critical 0건

### major 0건

### minor 5건

| ID | 슬라이드 | 검출 | 정본 권고 | 처리 |
|---|:--:|---|---|---|
| **C-m1** | B11·B12·B13·B14 | 페이지 번호 좌하단 navy 부재 (4장 모두) | carry-frozen — 직전 19장 deck 동일 상태 | minor (다음 deck rebuild 시 fix 검토) |
| **C-m2** | B13 | hero "13/16" navy→sky 청록 그라데이션 미적용 (단색) | fix 2 메인 hero (B11 "89.1%") 만 그라데이션, B13 보조 hero 는 단색 — 디자인 의도 영역 | minor (시각적 일관성 위해 B13 그라데이션 적용 considered) |
| **C-m3** | B12 | 우측 보조 hero "35.2%" / "89.1%" navy 단색 (그라데이션 미적용) | 의도된 design — orange bar 강조와 navy 단색 hero 조합 | PASS (디자인 의도) |
| **C-m4** | B11 본문 | "4.4% 감소" (정본 −4.38% 의역) | handoff §3.1 의역 허용 범위 (5.67×→5.7배 와 동일 패턴) | PASS (carry) |
| **C-m5** | B11·B12·B14 | "1508" / "89.1%" / "35.2%" / "89.2%" / "97.5%" / "89.8%" / "96.5%" 등 정본 carry 영역 수치 | 14b/14c 환각 회피 룰과 무관, carry 정본 표 §5 와 일치 | PASS (carry) |

### decision deferred 0건

---

## §8. 종합 verdict

### B11~B14 result

| 슬라이드 | VERDICT | 핵심 결과 |
|---|:--:|---|
| **B11** | **PASS** ★ | fix 2 hero "89.1%" 청록 그라데이션 시각 적용 ✓ · 정본 수치 4/4 정합 · Emerald badge 정상 |
| **B12** | **PASS** | CaseA 35.2% vs CaseB 89.1% + 96.5% direct 비교 narrative · honest robustness 메시지 정확 |
| **B13** | **PASS** | 16 method 중 13 강·3 제외 정렬·paradigm narrative 정합 · method 코드명 노출 0 · hero "13/16" 그라데이션 미적용 (minor) |
| **B14** | **PASS** | 5축 multi-axis (선택도·데이터 구조·계층 수) 일관성 메시지 + 11 수치 carry 정합 |

### 5/22 미팅·5/27 발표 ready

- **B11~B14 결과 챕터 4장 v2 raster PPTX = PASS** (critical 0 · major 0 · minor 5)
- fix 1 (B16 4갈래) = 본 chunk scope 외, axis_d 담당
- fix 2 (hero 청록 그라데이션) = 메인 hero (B11 "89.1%") 시각 적용 ✓, 보조 hero (B13 "13/16") 단색 — 디자인 일관성 차원에서 B13 도 그라데이션 적용 권고 (사용자 결정 영역)
- fix 3 (한글 깨끗) = 4장 모두 깨끗 ✓
- carry 의미 단위 = 4/4 PASS (직전 19장 deck A11~A14 와 동결 PASS)
- 정본 수치 11/11 정합 = ★ 환각 회피 PASS · 본문 메시지 (latency 동등 / robustness 우위) 정확 carry

**5/22 교수님 미팅에서 결과 챕터 4장 발표 가능, 5/27 최종 발표 직전 B13 hero "13/16" 그라데이션 적용 여부 결정만 권고.**

---

작성 2026-05-20 KST · sub-agent (Opus 4.7) raster image vision · B11~B14 (결과 챕터) chunk · ω·χ·τ·υ 4 축 통합 검증 · PASS-with-carry-issue (페이지 번호 carry-frozen + B13 hero 그라데이션 미적용 minor)
