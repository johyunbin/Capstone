# 속도는벡터 — 5/8 W4 Sprint 회의 자료 (v3 · Academic, static)

학술 콘텍스트 적합도가 가장 높았던 **Style A (Academic)** 디자인 언어로 본 5/8 19:00 W4 sprint 회의용 15 slide static HTML deck. v3 academic deck 의 design system 을 그대로 따른다.

## 디자인 시스템 — Academic (v3 동일)

### Surface
- **배경**: 전체 흰색 #FFFFFF (다크 슬라이드 없음)
- **상단 navy bar**: 좌상단 5px × 60px 굵은 navy bar (`#1B3DAD`) — 타이틀 앞 세로 강조
- **하단 implication bar**: 풀 너비 navy 배경 / 흰 텍스트 1줄 결론

### Typography
- **국문**: Apple SD Gothic Neo → Pretendard Variable fallback
- **영문 / 수치**: Inter (tabular figures), IBM Plex Sans
- **mono**: JetBrains Mono (caption / pill / badge)

### 절 제목
- 검정 사각 박스 (`#0B0F1C` 배경 / 흰 텍스트) `01` `02` … `10` numbered badge

### Color tokens
| token | hex | 용도 |
|---|---|---|
| `--brand-navy` | `#1B3DAD` | primary accent · big number · stripe |
| `--brand-navy-deep` | `#14307F` | hover / shadow |
| `--brand-blue` | `#4A7BD8` | secondary chart |
| `--brand-blue-soft` | `#E4ECF8` | tint / background |
| `--brand-red` | `#E03A3A` | negative · warning |
| `--ink` | `#0B0F1C` | numbered badge 배경 |

### 페이지 메타
- **우상단**: `01 / 15` navy mono, page counter
- **footer**: 좌측 "속도는벡터 · STYLE A · ACADEMIC", 우측 "W4 SPRINT · 2026.05.08"

## 15 Slide 구성 (W4 narrative)

| # | 제목 | 핵심 |
|---|---|---|
| 01 | Cover | "Skew-Aware …" + W4 Sprint Meeting 2026.05.08 |
| 02 | TOC | 10-card grid (Motivation / Matrix / RQ1 / RQ2 / RQ3 / 4강 Heatmap / Distribution / Multi / Honesty / 자문) |
| 03 | §01 Motivation | Exqutor 가 미해결한 단일 테이블 비인덱스 분포 영역 |
| 04 | §02 W4 Matrix | 12 단일 + 3 multi = 15 cell · 25 method (16 base + 9 NEW9) |
| 05 | §03 RQ1 Diagnostic | 5 dataset × 2 scale forest plot (DEEP-KM20 ρ=−0.680 anchor) |
| 06 | §04 RQ2 Aware | KM20 7/8 cell 우수 + K-aware K_optimal + Anti-Neyman counterfactual |
| 07 | §05 RQ3 Tier | 25 method tier 1-4 elimination → 4 winner (Hilbert · MiniBatch_p · Hybrid · HDBSCAN) |
| 08 | §06 4강 Heatmap | 5 dataset × sf1/sf10 paired Δ% vs BERN (sel=0.10) |
| 09 | §07 Distribution | sweet spot — DEEP/SIFT/WIKI/YFCC improve, SSN++ honest hurt |
| 10 | §08 Multi-relation | partsupp_deep_sift_10 / partsupp_deep_wiki_10 / partsupp_deep_10 ⨝ part_wiki_10 |
| 11 | §09 Honesty | 8종 honest limitation + YFCC PCA basis caveat |
| 12 | (보강) Production | Hilbert/MiniBatch_p/Hybrid/HDBSCAN production 특성 비교 |
| 13 | §10 자문 | 자문 메일 초안 (채림 + 지도교수) + sf100 plan |
| 14 | (보강) Future | sf100 launch timing + Exqutor multi-table 영역 + DuckDB native |
| 15 | 5/27 narrative | 12 slide mapping + 5/8 deliverable |

## 수치 반영 (W4 partial)

- **RQ1**: DEEP-KM20 ρ=−0.680 [−0.800, −0.440] anchor 유지 + W4 partial 7/8 cell CI 0 제외
- **RQ2 Anti-Neyman**: DEEP +5.21% / SIFT +9.49% (W3 확정), SSN++/WIKI/YFCC 진행중
- **RQ3 4강 (sel=0.10) — master_v6_draft FILL_4KANG_TABLE**:
  - DEEP_sf1: Hilbert −0.43% / Hybrid −1.06% / MB_p −1.36% / HDBSCAN −1.84%
  - DEEP_sf10: Hilbert −1.20% / Hybrid −1.91% / MB_p −2.07% / HDBSCAN −1.77%
  - SIFT_sf1: Hilbert −32.08% / Hybrid −28.95% / MB_p −31.58% / HDBSCAN −32.63%
  - SIFT_sf10: Hilbert −10.72% / Hybrid −10.20% / MB_p −10.22% / HDBSCAN −10.47%
  - SSN_sf1: +2.34% / +1.35% / +1.73% / +1.56% (honest hurt)
  - SSN_sf10: +2.06% / +1.25% / +2.04% / +1.39% (honest hurt)
  - WIKI_sf1: −9.61% / −7.69% / −9.86% / −9.96%
  - YFCC_sf1: −6.88% / −5.71% / −7.15% / −7.23%
- **Mechanism**: Hilbert inverse Manhattan 1.000 vs Z-order 1.992 (locality)
- **MiniBatch_partial**: 1,189× speedup, ARI 1.000 (production)

## 파일

```
academic_deck_5월8일회의/
├── index.html          ← static HTML, 15 slides, browser preview / scrolled deck
├── index-print.html    ← static HTML + auto window.print() — Chrome PDF export 용
├── figures/            ← 외부 첨부 이미지 (사용 시 path 참조)
└── README.md           ← 이 파일
```

## PDF 출력 절차

1. `index-print.html` 을 Chrome 으로 열기 → 자동 print dialog
2. Destination: "Save as PDF"
3. Paper size: 1280×720 (custom) 또는 16:9 landscape
4. Margins: None (또는 default)
5. Background graphics: ✓
6. Save: `submission/_drafts/속도는벡터_5월8일회의_v1.pdf`

## v3 5/27 deck 와의 차이점

- 18 slide → 15 slide (Q&A + Closing 합침, Cross-Scale + Mechanism + Effect Honesty 통합)
- "FINAL · 2026.05.27" → "W4 SPRINT · 2026.05.08"
- 4강 method narrative: W3 22 method 기준 → W4 25 method tier elimination 기준
- RQ1 single ρ → 5 dataset × 2 scale forest plot (8 cell)
- 4강 method 5 dataset 일관성 heatmap 추가 (sel=0.10 paired Δ%)
- sf100 plan + 자문 메일 초안 슬라이드 신설

> v3 Academic style (static) — white background, navy accent, 15 slide, W4 sprint narrative
