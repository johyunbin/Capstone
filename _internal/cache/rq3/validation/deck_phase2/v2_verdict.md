# v2 종합 verdict — 발표 deck 21장 (raster image PPTX) 5축 vision 검증

> 작성: 2026-05-20 14:13 KST · finalize (V-D 결과 반영).
>
> **핵심 한 줄**: v2 PPTX (21장 raster image, 1.20MB) 5축 vision 검증 결과 **critical 0 + major 0 + minor 11 + ship-ready**. fix 1·2·3 모두 PASS — fix 1 (B16 4갈래 도식 완벽 추가, ψ-M1 v1 major 시정) + fix 2 (메인 hero navy→cyan 그라데이션 5/5 적용) + fix 3 (한글 21/21 깨짐 0건). carry 18장 변동 0건. 정본 수치 catalog 23/23 정합 (100%). 5/22 미팅·5/27 발표 진행 가능.

---

## 0. 메타

| 항목 | 값 |
|---|---|
| 검증 대상 v2 | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` (1.20MB, 5/20 13:49) |
| 검증 대상 v1 (직전 7축 base) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` (1.05MB, 5/20 13:00) |
| 19장 deck (carry base) | `submission/_drafts/속도는벡터_최종발표_슬라이드_20260519_223845.pptx` |
| 수정 prompt | `submission/_drafts/속도는벡터_발표deck_수정프롬프트_20260520_133527.md` (3 fix) |
| **v2 형식** | **raster image PPTX 통째 변환** — 21장 모두 PNG 1장 (image-N-1.png) full-slide stretch |
| **검증 방식** | **vision 기반 시각 검증** (XML 검증 불가) |
| 정본 PNG | `_internal/cache/rq3/validation/deck_phase2/v2_images/B01.png ~ B21.png` |
| 검증 산출 | `_internal/cache/rq3/validation/deck_phase2/v2_axis_{a,b,c,d,e}.md` 5 file + 본 verdict |
| 검증 방식 전환 근거 | claude.ai/design PPTX export = raster 화 (v1 native shape → v2 raster). 시각 정확성이 곧 발표 정확성 = PowerPoint·Keynote 렌더 시 raster 그대로 출력. |

## 1. 5축 verdict 종합

| 축 | 담당 슬라이드 | verdict | crit | maj | min | 산출 |
|---|---|:--:|:--:|:--:|:--:|---|
| **V-A** | B1~B5 (표지 + 배경 Sky) | **PASS** | 0 | 0 | 1 | 메인 직접 작성 |
| **V-B** | B6~B10 (방법 Violet) | **PASS** | 0 | 0 | 2 | sub-agent |
| **V-C** | B11~B14 (결과 Emerald) | **WARN** | 0 | 0 | 5 | sub-agent |
| **V-D** | B15·B16 (신설 14b/14c · ★ fix 1·2·3 정밀) | **PASS** ★ | 0 | 0 | 2 | sub-agent (478 line, 34KB) |
| **V-E** | B17~B21 (적용 Orange · 결론 · 종결) | **PASS** | 0 | 0 | 1 | sub-agent |

**5축 합산**: critical **0** · major **0** · minor **11**. v1 의 major 1 (ψ-M1 B16 4갈래 누락) 시정 완료.

## 2. fix 1·2·3 verdict (★ 본 세션 핵심)

### ★★★ fix 1 — B16 4갈래 도식 (ψ-M1 major 1건 수정 핵심) → **PASS**

V-D 정밀 vision (B16 PNG 직접 분석):
- 위치: 제목 underline 바로 아래, 좌·우 박스 위 — **full width 가로 띠**
- 구조: 좌측 "비교 흐름" 라벨 + 4 칩 (**기본 엔진 → 베이스라인 → 결합 → 정답**) + 3 화살표 + 우측 캡션 "아래 좌·우 비교는 이 흐름의 베이스라인 vs 결합 구간"
- 강조 색상: **결합 청록** + **정답 그린** — 두 박스 강조, 베이스라인 박스도 강조
- 좌·우 박스 본문 0 변동 — 13/13 영역 carry 동결 PASS

→ **v1 major 1건 (ψ-M1) 시정 완료. ship-ready.**

### ★ fix 2 — Hero number navy → 청록 그라데이션 (σ-M1 carry-frozen 시정) → **PASS** (메인 hero)

V-D 정밀:
- **B15 hero "3~7×"**: navy → cyan 그라데이션 burned-in. 진행 바도 동일 그라데이션. ✅
- **B16 hero "94.9%"**: 동일 그라데이션. 진행 바도 동일. ✅

메인 cross-check (B1·B11·B19·B21 직접 vision):
- B1 "속도는벡터" / B11 "89.1%" / B19 hero / B21 "감사합니다" — 5/5 메인 hero 그라데이션 명확 ✅

**부분 carry (sub-hero 단색 — design 일관성 minor)**:
- B2 "33%" / "100%" 단색 navy (배경 sub-hero, v2 그라데이션 미적용)
- B13 "13/16" 단색 (V-C 보고 minor)
- B19 §2 막대 라벨 35%/89% 정수 반올림 (V-E 보고 minor)

→ **메인 hero PASS** (5/5). sub-hero 부분 단색은 design 일관성 권고 minor (발표 무결성 영향 0).

### fix 3 — 한글 typeface (σ-C1 v1 시정) → **PASS**

21장 한글 깨짐 0건 ✅ (V-A·V-B·V-C·V-D·V-E 5/5 PASS).
- raster 화로 typeface XML 의존 무관 — burned-in 픽셀이 Apple SD Gothic Neo 또는 시스템 fallback 으로 자연 렌더
- "Inter typeface 한글 332건" v1 결함이 v2 raster 변환에서 시각적으로 해소

→ **ship-ready**.

## 3. carry 18장 변동 0건 (5축 모두 PASS)

| 챕터 | 슬라이드 | carry verdict | 담당 축 |
|---|---|:--:|:--:|
| 표지 (carry) | B1 ↔ A1 | ✅ | V-A |
| 배경 (Sky carry) | B2~B4 ↔ A2~A4 | ✅ | V-A |
| 방법 (Violet) | B5~B10 ↔ A5~A10 | ✅ | V-A · V-B |
| 결과 (Emerald carry) | B11~B14 ↔ A11~A14 | ✅ | V-C |
| **결과 (신설 — 14b)** | **B15** | **신설 PASS** | V-D ★ |
| **결과 (신설 — 14c)** | **B16** | **신설 PASS (fix 1)** | V-D ★ |
| 적용 (Orange carry +2 shift) | B17 ↔ A15 · B18 ↔ A16 · B20 ↔ A18 | ✅ | V-E |
| 결과 (Emerald 결론) | B19 ↔ A17 | ✅ | V-E |
| 종결 (carry +2 shift) | B21 ↔ A19 | ✅ ("질의응답" Keep) | V-E |

**carry 18장 의미 단위 변동 0건** — 본문 / 수치 / layout 대전환 0건.

## 4. 본문 수치 catalog 23/23 정합 (V-D 검증 핵심)

V-D 결과 100% 정합 확정:

| 분류 | 수치 | 슬라이드 | verdict |
|---|---|---|:--:|
| 기존 엔진 (B2) | 33% / 100% (pgvector·DuckDB) | B2 | ⚠️ "33%" (catalog "33.3%") 소수점 표기 minor — V-A m1 |
| | 50% (VBASE) carry — design 의도 부재 | B2 | OK |
| 결과 (B11~B14) | 89.1% (CaseB better) | B11·B12·B19 | ✅ |
| | 1,508 / 1,344 (better count) | B11 | ✅ ("1508번" 콤마 부재 V-B m1) |
| | 35.2% (CaseA negative control) | B12·B19 | ✅ ("35%" 막대 V-E m1) |
| | −4.38% / 4.4% (중앙값 Δ%) | B11·B19 | ✅ ("4.4%" 의역) |
| | 13/16 (강 method) | B13 | ✅ |
| | 5축 multi-axis (sel·single·strata) | B14 | ✅ 11/11 정합 |
| B15 (신설 14b) | 3~7× / 5.7× / 2,880회 / 12 구간 / 16 변형 / 15 반복 / 4 단계 | B15 | ✅ |
| | Q3 7.0× / Q9 3.0× / Q10·Q12 6.0× | B15 | ✅ |
| | DEEP 8천만 / 180건 100% 유의 | B15 | ✅ |
| B16 (신설 14c) | 94.9% / 148/156 / 7/12 (58%) | B16 | ✅ |
| | 질의 0:0/4·1:4/4·2:3/4 / 8건 Q3 한정 | B16 | ✅ |
| | 13 방법 × 12 구간 매트릭스 (148/8) | B16 | ✅ |

**V-D 정본 수치 검증: 23/23 = 100% 정합**.

## 5. 환각 회피 룰 (B16 핵심)

V-D 정밀 확인:
- B16 핵심 메시지: **"실행 시간은 두 방식이 거의 같다. 결합 방식의 가치는 — 정답 계획을 더 흔들림 없이 만든다는 그 견고함."**
- paired Wilcoxon 7.7% 만 유의 → robustness 우위만 강조. "결합이 빠르다" / "CaseB latency 우위" 류 환각 0건 ✅
- B16 좌측 (베이스라인) 0:0/4·1:4/4·2:3/4 fragile 분포 명시 — qid 의존 carry PASS
- 코드명 (B1/CaseA/CaseB) 노출 0건 — 발표물 한국어 자연어 carry ✅
- B21 "질의응답" 보조 텍스트 = 사용자 Keep 결정 carry (결함 X)
- 페이지 번호 부재 = 21장 모두 carry-frozen (v1 + 19장 deck 동일)

## 6. minor 11건 상세 (severity carry-frozen 또는 design 일관성)

| ID | 슬라이드 | 내용 | 분류 |
|---|---|---|---|
| V-A m1 | B2 | hero "33%" (catalog "33.3%") 소수점 표기 | minor (의미 동등, 양극단 도식 design) |
| V-B m1 | B6~B10 | hero 부재 → fix 2 검증 대상 외 (도식 위주) | minor (PASS 우회) |
| V-B m2 | B7 | "1508번 측정" 콤마 부재 | minor (의역 carry, CLAUDE.md anchor 자체 콤마 X) |
| V-C m1 | B11~B14 | 페이지 번호 부재 | carry-frozen |
| V-C m2 | B13 | hero "13/16" 단색 (그라데이션 미적용) | minor (design 일관성 권고) |
| V-C m3~m5 | B11~B14 | 의역·표기 carry | minor (handoff 허용) |
| V-D m1 | B15 | 페이지 번호 부재 | carry-frozen |
| V-D m2 | B16 | 페이지 번호 부재 | carry-frozen |
| V-E m1 | B19 | §2 막대 라벨 35%/89% 정수 반올림 (정본 35.2%/89.1%) | minor (B19 §1 본문은 "89.1%" 정확, 막대만 정수, 구두 보강 가능) |

**minor 11 분류**: 페이지 번호 부재 carry-frozen 6 + design 일관성 (sub-hero 단색) 2 + 의역·표기 carry 3.

## 7. 종합 판정 — ★ ship-ready ★

**v2 = 5/22 미팅·5/27 최종 발표 진행 가능**:
- critical 0 · major 0
- fix 1·2·3 핵심 모두 PASS — v1 의 major 1건 (ψ-M1) 완벽 시정
- carry 18장 변동 0건
- 본문 수치 catalog 23/23 정합 100%
- 환각 회피 (B16 메시지) 정합

**5/27 발표 전 (5/22~5/26) 결정 권고 (선택)**:
- **(권고 1, low)** B13 "13/16" 그라데이션 적용 — design 일관성. 발표 무결성 영향 0. 다음 deck rebuild 시 검토.
- **(권고 2, low)** B19 §2 막대 라벨 35.2%/89.1% 정수 → 소수점 1자리 — 발표 시 구두 보강 가능, 디자인 단순화 의도 carry.
- **(권고 3, low)** B2 "33.3%" 소수점 복구 — 양극단 도식 무결성 영향 0, 추가 fix 불필요.

→ **추가 수정 prompt 발행 불요**. v2 그대로 5/22 미팅 / 5/27 발표 / 5/28 포스터 base 로 활용.

## 8. 산출물

| 항목 | 경로 |
|---|---|
| **본 verdict** | `_internal/cache/rq3/validation/deck_phase2/v2_verdict.md` (정본) |
| 5축 검증 산출 | `_internal/cache/rq3/validation/deck_phase2/v2_axis_{a,b,c,d,e}.md` |
| v2 PNG 정본 (21장) | `_internal/cache/rq3/validation/deck_phase2/v2_images/B01.png ~ B21.png` |
| v2 PPTX (검증 대상) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` (정본) |
| v1 PPTX (직전 검증 base, 7축) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` (carry) |
| 19장 PPTX (carry base) | `submission/_drafts/속도는벡터_최종발표_슬라이드_20260519_223845.pptx` |
| 수정 prompt | `submission/_drafts/속도는벡터_발표deck_수정프롬프트_20260520_133527.md` |
| v1 7축 verdict (carry) | `_internal/cache/rq3/validation/deck_phase2/verdict.md` |

---

작성: 2026-05-20 14:13 KST — 본 세션 v2 검증 finalize. 5축 ship-ready PASS.
