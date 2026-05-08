# 속도는벡터 — 5/27 발표용 최종 deck (v3 · Academic)

학술 콘텍스트 적합도가 가장 높았던 **Style A (Academic)** 디자인 언어로 본 5/27 발표용 16 slide 전체 deck.

## 디자인 시스템 — Academic

### Surface
- **배경**: 전체 흰색 #FFFFFF (다크 슬라이드 없음)
- **상단 navy bar**: 좌상단 5px × 60px 굵은 navy bar (`#1B3DAD`) — 타이틀 앞 세로 강조
- **하단 implication bar**: 풀 너비 navy 배경 / 흰 텍스트 1줄 결론

### Typography
- **국문**: Apple SD Gothic Neo → Pretendard Variable fallback
- **영문 / 수치**: Inter (tabular figures), IBM Plex Sans
- **mono**: JetBrains Mono (caption / pill / badge)

### 절 제목
- 검정 사각 박스 (`#0B0F1C` 배경 / 흰 텍스트) `01` `02` … `10` numbered badge — 학술 academic.pdf 패턴

### Color tokens
| token | hex | 용도 |
|---|---|---|
| `--brand-navy` | `#1B3DAD` | primary accent · big number · stripe |
| `--brand-navy-deep` | `#14307F` | hover / shadow |
| `--brand-blue` | `#4A7BD8` | secondary chart |
| `--brand-blue-soft` | `#E4ECF8` | tint / background |
| `--brand-red` | `#E03A3A` | negative · warning · "★" marker |
| `--ink` | `#0B0F1C` | numbered badge 배경 |
| `--gray-{100…600}` | warm slate | hairline / caption |

### 페이지 메타
- **우상단**: `01 / 16` navy mono, page counter
- **footer**: 좌측 caption "속도는벡터 · STYLE A · ACADEMIC", 우측 "CAPSTONE 2026 · FINAL · 2026.05.27"

### Chart palette
- navy `#1B3DAD` primary
- light blue `#E4ECF8` secondary
- crimson `#E03A3A` negative
- gray `#6E7891` caption

## 16 Slide 구성

| # | 제목 | 핵심 |
|---|---|---|
| 01 | Cover | "Skew-Aware Stratified Sampling …" + subtitle + 4-col footer (TEAM / ADVISOR / REFERENCE / DATE) |
| 02 | TOC — 오늘의 구성 | 10-card grid (Problem / Prior / Approach / RQ1 / RQ2 / RQ3 / Cross-Scale / Mechanism / Effect / Future) |
| 03 | 1. 해결하고자 하는 문제 | 좌 33.3 / 50 / 100% baseline + 우 0.001~90% 광범위 실분포 |
| 04 | 2. 이전 연구 — Exqutor | ECQO 1–2 ms + Adaptive Sampling 1000× + plan cost gap bar |
| 05 | 3. 우리의 접근 — Skew-Aware | RQ1 진단 / RQ2 aware / RQ3 agnostic 3-card |
| 06 | 4. RQ1 진단 — 단조성 | ρ = −0.680 [−0.800, −0.440] DEEP-KM20 + scatter |
| 07 | 5. RQ2 — distribution-aware | 40 / 40 cells + Anti-Neyman counterfactual + heatmap |
| 08 | 6. RQ3 — 22 method | effect size bar (★ Hilbert / MiniBatch / Hybrid / HDBSCAN 4강) |
| 09 | ★ Contribution 1 — Hilbert Curve | −0.156 Cohen's d + inverse Manhattan 1.000 vs 1.992 |
| 10 | ★ Contribution 2 — MiniBatch K-means | 1,189× speedup + ARI 1.000 |
| 11 | ★ Contribution 3 — Negative Control | +0.7 hurt-medium + Distance-Shell / IS bar |
| 12 | 7. Cross-scale Sensitivity | 1M → 8M heatmap + DEEP_8M mid-sel ✗ 비단조 |
| 13 | 8. Mechanism — locality + redundancy | Hilbert vs Z-order + ARI matrix |
| 14 | 9. Effect Size Honesty | DEFF 0.338 / ESS 2,325 / per-query routing ρ = 0.78 |
| 15 | 10. Limitation · Future Work | L1~L4 4-card grid |
| 16 | Closing | 감사합니다 / Q&A + GitHub + arXiv |

## Speaker Notes
16개 한국어 발표 대본 (`<script id="speaker-notes">` JSON). 슬라이드당 30~45초 → 총 12~15분.

## 수치 정확 반영
- RQ1: ρ = −0.680 [−0.800, −0.440] DEEP-KM20, ρ = −0.140 [−0.220, −0.100] SIFT-KM20
- RQ2: 40/40 cell, Anti-Neyman DEEP +5.21% [+1.36, +9.16] / SIFT +9.49% [+4.66, +11.75]
- RQ3 4강: Hilbert d=−0.156 / MiniBatch 1,189× / Hybrid SIFT s=0.10 −3.10% [−4.61, −1.19] / HDBSCAN SIFT s=0.10 −3.99% [−5.34, −2.12]
- 8M mid-sel: 단조 증가 0 / 감소 2 (n=3) — sample_size=385 검증력 한계
- DEFF Hilbert 0.338, ESS 2,325 (SRS 6× effective sample)
- per-query routing: spread vs difficulty ρ = 0.78

## 파일

```
academic-deck/
├── index.html          ← deck-stage host + Academic style block + speaker notes
├── Slides.jsx          ← 16 React 컴포넌트 (S1 … S16)
├── deck-stage.js       ← starter component (scaling + nav + print-to-PDF)
└── README.md           ← 이 파일
```

> v3 Academic style — white background, navy accent, 16 slide
