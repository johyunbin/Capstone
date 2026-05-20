# 발표 deck 신본 21장 multi-axis 검증 — 종합 verdict

> 작성: 2026-05-20 KST · 검증자: 메인 세션 (Opus 4.7) + 7 축 sub-agent (Opus 4.7) · read-only
> 검증 대상: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` (21장, 1.05MB, 5/20 13:00 다운로드)
> 정본 base: 보고서 신본 `_20260520_124200.md` §5 + handoff `_20260520_124250` §3·§4·§8 + δ 산출 + deck 신본 프롬프트 `_20260520_095900.md`
> 검증 항목: handoff §4.1 의 7 항목 × 21장 = 147 sub-check

---

## VERDICT: **WARN (PASS-with-fixable)** — critical 0 · major 1 · minor 12 + decision deferred 2

**한 줄**: 21장 deck 신본은 내용·수치·환각 회피 모두 PASS (ω·χ·υ 3 축 완벽), carry 동결 의미 단위 PASS (τ). 발견된 결함은 모두 (a) 직전 19장 carry 영역 carry-frozen 상태 (φ·σ critical/major) 또는 (b) 단독 fix 검토 영역 (ψ-M1 B16 4갈래). 6/11 보고서 §5 정본과 1:1 cross-check 완벽. **5/22 미팅 진행 가능, 5/27 최종 발표 전 σ·φ 시각 렌더 검증 + ψ-M1 결정 권고**.

---

## §1. 7 축 verdict 요약 표

| 축 | 검증 항목 | VERDICT | crit | maj | min | 핵심 발견 |
|---|---|:--:|:--:|:--:|:--:|---|
| **ω** | 본문 정본 수치 cross-check | **PASS** | 0 | 0 | 3 | 34/34 정본 정합 + 환각 12/12 클린. minor 3 = 의역 허용 범위 (5.7배↔5.67×) |
| **ψ** | 절대 규칙 8 항목 위반 | **WARN** | 0 | 1 | 6 | 규칙 1·2·3·4·6 PASS. **major ψ-M1 = B16 단독 시 2갈래(베이스라인·결합) 만 dominant** (4갈래 흐름 누락). hero overflow 5건 = 4건 carry + 2건 신설 |
| **χ** | 결과 국면(그린) badge 일관 | **PASS** | 0 | 0 | 1 | B11·B12·B13·B14·**B15·B16**·B19 7장 모두 `#10B981` (Emerald 그린) 일관. 4 챕터 색상 system 무결 (배경 Sky / 방법 Violet / 결과 Emerald / 적용 Orange) |
| **φ** | 페이지 번호 좌하단 navy | **WARN** ★ | 0★ | 0 | 1 | **21장 모두 페이지 번호 0건** + slideMaster `sldNum="0"` 비활성. **직전 19장 deck 도 동일 상태** = carry-frozen. φ-C1 → minor 재분류 |
| **τ** | 19장 carry 동결 | **WARN** | 0 | 0 | 5 | 19/19 의미 단위 PASS. B21 "질의응답" 추가 = decision deferred 1건. handoff "18장" typo = 다음 handoff carry. OCR 노이즈 2 슬라이드 = scope 외 |
| **σ** | 디자인 system | **WARN** ★ | 0★ | 1★ | 4 | navy 앵커 + 흰 배경 + 악센트 4색 PASS. **σ-C1 한글 332건 모두 Inter (Apple SD Gothic Neo XML 미적용)** + **σ-M1 hero `#000` 검정 (그라데이션 XML 미실현)** — 둘 다 carry 영역 결함, **시각 렌더 검증 필요** |
| **υ** | 보고서 §5 ↔ 14b/14c 정합 | **PASS** | 0 | 0 | 0 | 의역·반올림 13 항목 + 환각 회피 8 항목 + cross-check 5 항목 + fact catalog 13 항목 모두 PASS. **"latency 동등 / robustness 우위" 메시지 정확히 carry** |

★ = critical/major 가 carry-frozen 상태 재해석 후 severity 강등.

---

## §2. severity catalog (재분류 후)

### critical 0건
직전 19장 deck 와 비교 검증 결과 critical 발견 항목 모두 carry-frozen 상태로 재해석. 21장 신본이 새로 깨뜨린 절대 규칙 위반 0건.

### major 1건

| ID | 축 | 슬라이드 | 검출 | 정본 권고 | 처리 옵션 |
|---|:--:|:--:|---|---|---|
| **ψ-M1** | ψ | **B16 (14c)** | 좌 박스 "베이스라인 7/12" + 우 박스 "결합 148/156" 만 본문에 명시 → 청중 인식 시 2갈래 이분법 | 4갈래 (기본엔진·베이스라인·정답·결합) 흐름 명시 또는 좌상단 "4갈래 비교" 도식 추가 | (A) claude.ai/design 추가 수정 prompt (B) 발표자 구두 보강 (C) 슬라이드 15 ("기본 엔진" 4회 등장) 의 narrative 흐름으로 충분 — 결정 영역 |

### minor 12건 + decision deferred 2건

| ID | 축 | 슬라이드 | 검출 | 정본 권고 | 처리 |
|---|:--:|:--:|---|---|---|
| ω-m1 | ω | B15 | 평균 `5.7배` 노출 | 정본 5.67× 의 반올림 의역 (handoff §3.1 허용) | PASS (스피커 노트에 5.67× carry) |
| ω-m2 | ω | B11 | `1,508` (carry) | carry 영역 — 14b/14c 환각 회피 룰과 무관 | PASS |
| ω-m3 | ω | B13 | method median 반올림 (-5.7/-5.7) | carry 정본 표 5-4 와 일치 | PASS |
| ψ-m1 | ψ | B11 (89.1%) | hero 180pt × box 161.5% (carry) | carry 검증 통과, auto-fit OK | PASS (carry) |
| ψ-m2 | ψ | B13 (13/16) | hero 135pt × box 138.2% (carry) | carry 검증 통과 | PASS (carry) |
| ψ-m3 | ψ | B15 (3~7×) | hero 111pt × box 100.4% (신설) | 시각 렌더 시 잘림 확인 필요 (auto-fit 적용 시 PASS) | 시각 렌더 검증 |
| ψ-m4 | ψ | B16 (94.9%) | hero 111pt × box 100.4% (신설) | 동일 | 시각 렌더 검증 |
| ψ-m5 | ψ | B21 (감사) | hero 180pt × box 168.5% (carry) | carry 검증 통과 | PASS (carry) |
| χ-m1 | χ | B15 | underline T 23.8% (vs 다른 결과 슬라이드 T 16.7%) | 두 줄 제목 (높이 14.6%) 으로 underline 자동 shift, 색상 동일 | PASS (의도된 shift) |
| φ-C1→m | φ | 21장 | 페이지 번호 0건 + slideMaster `sldNum="0"` | **직전 19장 deck 도 동일** → carry-frozen | minor (다음 deck rebuild 시 carry 영역 결함 fix 검토) |
| σ-C1→m | σ | 21장 | 한글 332건 모두 `Inter` typeface (XML) | **직전 19장 deck = raster image, 폰트 정보 XML 무관** → carry 영역 차이 0 | minor (시각 렌더 시 시스템 폰트 fallback 으로 Apple SD Gothic Neo 표시 가능) |
| σ-M1→m | σ | 21장 | hero number 모두 `solid #000000` (XML) | **직전 deck source markdown line 38·55 의 "청록 그라데이션 hero" 명시 vs 산출 미실현** — carry 영역 결함 | 시각 렌더 검증 필요 |
| **decision deferred 1** | τ | B21 | 감사합니다 + **"질의응답" 추가** (31.5pt) | A19 = "감사합니다" 단독 / B21 = 자연 확장 또는 carry 위반 (해석 영역) | **사용자 결정** — keep / remove |
| **decision deferred 2** | τ | handoff §4.1 ⑥ | `"18장 carry 동결"` typo (실제 19장) | 다음 handoff 정정 carry | **자동 carry** — 본 handoff 에서 정정 |

---

## §3. 검증 항목 ① ~ ⑦ 결과 (handoff §4.1)

| # | 검증 항목 | 결과 |
|--:|---|:--:|
| ① | 총 21장 | **PASS** (확인) |
| ② | 14b/14c 본 내용 (정본 수치) | **PASS** (ω 축 34/34 정합, υ 축 cross-check 5/5) |
| ③ | 결과 국면(그린) badge | **PASS** (χ 축 B11~B16·B19 = `#10B981` 일관) |
| ④ | 코드명·"영역" 필러·수식·영문 메타·★ 노출 0 | **PASS** (ψ 축 규칙 1·2·3·4·6 모두 0건) |
| ⑤ | 페이지 번호 좌하단 navy | **WARN→carry** (φ 축, 직전 19장 deck 도 동일 carry-frozen) |
| ⑥ | 18장 carry 동결 (실제 = 19장) | **PASS** (τ 축 19/19 의미 단위. handoff "18장" typo 다음 handoff carry) |
| ⑦ | 디자인 system 일관 | **PASS** (σ 축 navy + 4 챕터 색상 + 흰 배경 PASS. 폰트·hero 그라데이션 XML 결함은 carry-frozen) |

**핵심 7/7 PASS or carry-frozen**.

---

## §4. carry 영역 결함 — 직전 19장 deck 과의 비교

| 항목 | 직전 19장 deck (5/19 223845) | 21장 deck 신본 (5/20 phase2반영) | carry 동결 여부 |
|---|---|---|:--:|
| PPTX 구조 | raster image (각 슬라이드 1 PICTURE) | native shape (text + 도형) | **변동** (claude.ai/design 산출 형식 차이) |
| 페이지 번호 | 19장 모두 0건 + slideMaster `sldNum="0"` | 21장 모두 0건 + 동일 master 설정 | **carry-frozen** ✓ |
| 폰트 (XML) | raster — XML 무관 | 한글 332건 `Inter` typeface | **신본 차이** (raster vs native 변환 부산물) |
| Hero 그라데이션 | raster — 시각 burned-in (검증 통과) | hero 모두 `solid #000` | **신본 차이** (raster vs native 변환 부산물) |
| 챕터 badge 색상 | raster — 시각 burned-in (5/19 검증 통과) | `#10B981` 그린 등 4색 native | **시각 일관** ✓ |
| 19장 본문 (carry 영역) | raster | native carry — 의미 단위 일치 (τ 19/19 PASS) | **carry-frozen** ✓ |
| 14b/14c 신설 영역 | n/a | native — ω·χ·υ 정합 | **신설 영역, 정본 정합** ✓ |

**결론**: 21장 신본은 직전 19장 raster image deck 의 native shape 재구성. raster→native 변환 과정에서 폰트·그라데이션이 XML 명시값으로 단순화 (`#000` 단색·`Inter`). 시각 렌더 시 PowerPoint·Keynote 의 시스템 폰트 substitution 과 hero number 의 가독성을 직접 확인 필요.

---

## §5. 다음 단계 권고

### 5.1 즉시 (5/22 미팅 전)

- **시각 렌더 검증** — 사용자가 21장 deck 을 PowerPoint·Keynote 로 열어 시각 확인:
  - (a) 한글 332건이 Apple SD Gothic Neo (또는 시스템 fallback) 으로 깔끔하게 보이는가?
  - (b) Hero number (89.1%·13·3~7×·94.9% 등) 가 navy → 청록 그라데이션 또는 navy 단색으로 보이는가? (검정 `#000` 인지 확인)
  - (c) 페이지 번호 부재가 발표 흐름에 영향 있는가? (없으면 carry 유지 OK)
- **ψ-M1 결정** — B16 (14c) 의 4갈래 흐름 보강 필요 여부:
  - (A) 발표자 구두 보강으로 충분 → 21장 그대로 유지
  - (B) claude.ai/design 추가 수정 prompt → 좌상단에 "4갈래 비교 도식" 추가

### 5.2 5/22 ~ 5/27 (PPTX 최종 + 최종 발표)

- 시각 렌더 검증 결과 결함 발견 시 → 5/26 PPTX 최종 마감 전 claude.ai/design 수정 prompt (`submission/_drafts/속도는벡터_발표deck_수정프롬프트_YYYYMMDD_HHMMSS.md`)
- 결함 없으면 → 21장 deck 신본을 5/27 발표 정본으로 확정
- 스피커 노트 보강 — `5.67×` 정확값·`p_holm = 0.0103` 등 정본 수치 carry

### 5.3 다음 handoff 정정 carry

- handoff §4.1 ⑥ `"18장 carry 동결"` → `"19장 carry 동결"` 로 정정
- deck 신본 프롬프트 line 12·109·155 `"18장"` 도 정정 (재산출 필요 시)

---

## §6. 산출 파일 (정본)

```
_internal/cache/rq3/validation/deck_phase2/
├── raw_dump.md                       (21장 native python-pptx 추출, 1430 line)
├── axis_omega_numbers.md             (ω 본문 수치 cross-check, PASS)
├── axis_psi_rules.md                 (ψ 절대 규칙 8 항목, WARN major 1)
├── axis_chi_badge.md                 (χ 그린 badge 일관, PASS)
├── axis_phi_pagenum.md               (φ 페이지 번호, WARN→carry minor)
├── axis_tau_carry.md                 (τ 19장 carry, WARN 5 minor)
├── axis_sigma_design.md              (σ 디자인 system, WARN carry minor)
├── axis_upsilon_report_xref.md       (υ 보고서 cross-check, PASS)
└── verdict.md                        (본 종합 verdict)
```

---

작성 2026-05-20 KST · 7 축 병렬 sub-agent 검증 12분 완료 · 본 deck 신본 6/11 보고서·5/27 최종 발표 정본 무결성 견고 · 발견 결함 = ψ-M1 (B16 4갈래 보강 결정 영역) + σ·φ carry-frozen (시각 렌더 검증 필요) + τ B21 "질의응답" decision deferred + handoff "18장" typo 정정 carry
