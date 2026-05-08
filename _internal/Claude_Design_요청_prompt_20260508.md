# Claude Design 요청 prompt — 5/27 academic-deck v3 update

> 사용자가 회의 전 또는 회의 중 Claude Design ([link](https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2?file=academic-deck%2Findex.html)) 에 입력.
> 디자인 (white bg + navy accent + numbered badge + 16 slides) 그대로, 수치/narrative 만 W4 sprint finalize 결과 + multi-vector 4강 일반화 결과 반영.

---

## 입력 prompt v1 (Full)

```
[속도는벡터 5/27 발표용 academic deck v3 update — W4 sprint finalize 결과 + multi-vector 4강 일반화 반영]

# 변경 원칙
- 디자인 시스템 (white bg + navy accent + numbered badge + IBM Plex/Inter/Pretendard 폰트) 그대로
- 16 slide 구성 그대로 (S1~S16)
- 수치 + narrative + 표 + 차트 데이터만 update

# 핵심 narrative 변경 사항

## 단일 100% finalize (5/8 14:13)

### 1. 4강 method × 10 cell paired Δ% (sel=0.10) — Tier 4 winner
- ★1 HDBSCAN: avg Δ% **−8.04** (8/10 negative + 8/10 CI excludes 0)
- ★2 MB_partial: avg Δ% **−7.63** (8/10 negative + 9/10 CI excludes 0) — OLTP friendly 유일
- ★3 Hilbert: avg Δ% **−7.54** (8/10 negative + 9/10 CI excludes 0) — production sweet spot
- ★4 Hybrid (MB + Hilbert): avg Δ% **−7.13** (8/10 negative + 8/10 CI excludes 0) — mechanism narrative

### 2. SIFT_sf1 가장 강력
- HDBSCAN −32.63%, Hilbert −33.53%, Hybrid −30.46%, MB_partial −33.13%

### 3. SSN++ ceiling effect (positive direction, +1~+2%)
- cluster_ratio 1.29 + intrinsic_dim 0.88 = 분포 균형 → BERN baseline 자체 ceiling
- 본 연구의 outer boundary 정의

### 4. Tier 1 살아남기 17종 spread = 1.21%p
- HDBSCAN −8.04 ~ kdtree −6.83
- → method choice 부차, "분포 인지 vs 미인지 boundary" 결정적

### 5. Distribution Sweet Spot 정량 boundary
- **Sweet** (강력 improve): cluster_ratio > 1.4 + intrinsic_dim < 0.85 → −7~−32% improve
- **Ceiling** (effect 약): cluster_ratio < 1.4 + intrinsic_dim > 0.85 → method 효과 약 (boundary)

### 6. RQ1 단조성 (12 single cell × 5 selectivity)
- ρ < 0 sign 100% 일관 (-0.366 ~ -0.609)
- DEEP-KM20 ρ = -0.680 [-0.800, -0.440] (W1-A, 그대로 유지)

### 7. RQ2 5-mode (12 cell × 4 mode = 48 measurements)
- 51/52 (sel=0.10) CI 0 제외 → 분포 정보 활용 효과 강력
- σ-allocation (Neyman vs Anti-Neyman) 격차 < 1% in 7/12 cell
- → 단순 균등 stratification 충분

## Multi-vector 4강 일반화 (5/8 STAGE 1+2 완료)

### 8. 단일 → multi-vector magnitude shrinkage
- 단일 sweet spot 4강 평균 |Δ%| = **17.13%** (SIFT_sf1 / WIKI_sf1 / YFCC_sf1)
- multi-vector 4강 평균 |Δ%| = **0.67%**
- → **25.4× 약화** (magnitude shrinkage)
- 부호 일관성 (sel=0.10): 3/8 negative · 5/8 positive boundary (|Δ| 모두 < 1.5%)
- **해석**: 단일 정확성은 multi 정확성의 *필요조건*만 성립, 충분조건 X

### 9. multi 측정 cell (모두 sf10 = 10x scale, sf1 multi 측정 안 함)
- partsupp_deep_sift_10 (DEEP+SIFT 한 행, 96+128 dim) ✅
- partsupp_deep_wiki_10 (DEEP+WIKI 한 행, 96+768 dim) ✅
- partsupp_deep_10 ⨝ part_wiki_10 (multi-table natural join) ⏳ STAGE 3 측정 진행 중

### 10. multi-relation 일반화 future work
- joint-aware clustering 또는 multi-vector decomposition 별도 설계 필요

## 학술 confirmation

### 11. PDX (SIGMOD 2025, CWI Amsterdam, arXiv:2503.04422)
- Quote: "intrinsic_dim + skewness 가 algorithm selection 결정"
- 우리 thesis 와 정확 일치 → 학술적 정당성 확보
- **Complementary contribution**:
  - PDX = compute layer (data layout for fast similarity)
  - 본 연구 = pre-process layer (sampling/clustering for accurate cardinality)

# 슬라이드별 update 가이드

| Slide | 기존 | 새 (W4 finalize) |
|---|---|---|
| 01 Cover | (그대로 — 디자인 + 제목) | 부제 = "Single → Multi: 25.4× shrinkage" 추가 가능 |
| 02 TOC | 10-card grid | 그대로 (구조 유지) |
| 03 Problem | baseline gap | 그대로 |
| 04 Prior — Exqutor | 1-2 ms / 1000× | + PDX (SIGMOD 2025) 학술 confirmation 추가 |
| 05 Approach | 3-card | 그대로 (RQ1/RQ2/RQ3) |
| 06 RQ1 — 단조성 | DEEP-KM20 ρ=-0.680 | 12 cell ρ < 0 100% 일관 (-0.366~-0.609) 추가 |
| 07 RQ2 — distribution-aware | 40/40 cells | 51/52 (sel=0.10) CI ex + σ-allocation 격차 < 1% |
| 08 RQ3 — 4강 effect size | Hilbert d=-0.156 등 | 4강 method × 10 cell paired Δ% (-8.04 / -7.63 / -7.54 / -7.13) |
| 09 Contribution 1 — Hilbert | d=-0.156 + Manhattan 1.000 | 4강 ranking 표 + Tier 1 17종 spread 1.21%p 추가 |
| 10 Contribution 2 — MiniBatch | 1,189× speedup | MB_partial OLTP friendly + CI 9/10 강력 |
| 11 Contribution 3 — Negative Control | hurt-medium | Sweet Spot 정량 boundary (cluster_ratio 1.4 / intrinsic 0.85) |
| 12 Cross-scale | 1M → 8M heatmap | sf1 → sf10 cross-scale 4강 일관성 + sf100 자문 후 |
| 13 Mechanism — locality | Hilbert vs Z-order ARI | 그대로 + Multi-vector 일반화 25.4× shrinkage 추가 |
| 14 Effect Size Honesty | DEFF/ESS | + SSN++ ceiling honest reporting |
| 15 Limitation | 4-card | 8-card (PARTIAL/FUTURE/HONEST 분류) — multi future + sf100 + KM20 oracle 등 |
| 16 Closing | 감사합니다 | 그대로 + multi-table join (STAGE 3) 측정 결과 회의 후 보강 표기 |

# 추가 시각 자료 데이터

## 4강 method × 10 cell paired Δ% (sel=0.10)
DEEP_sf1: -1.84 / -1.36 / -0.43 / -1.06 (HDBSCAN/MB_p/Hilbert/Hybrid)
DEEP_sf10: -1.77 / -2.07 / -1.20 / -1.91
SIFT_sf1: -32.63 / -31.58 / -32.08 / -28.95
SIFT_sf10: -10.47 / -10.22 / -10.72 / -10.20
SSN_sf1: +1.56 / +1.73 / +2.34 / +1.35
SSN_sf10: +1.39 / +2.04 / +2.06 / +1.25
WIKI_sf1: -9.96 / -9.86 / -9.61 / -7.69
WIKI_sf10: -4.30 / -2.58 / -4.48 / -4.21
YFCC_sf1: -7.23 / -7.15 / -6.88 / -5.71
YFCC_sf10: -5.77 / -5.62 / -5.21 / -4.78

## Multi-vector 4강 (sel=0.10)
deep_sift_10: hdbscan -1.02 / hilbert -0.48 / hybrid +0.31 / mb_partial -1.30
deep_wiki_10: hdbscan +1.15 / hilbert +0.06 / hybrid +0.08 / mb_partial +0.99

# 디자인 시스템 (변경 없음 — 참고용)
- 배경: 전체 흰색 #FFFFFF
- accent: --brand-navy #1B3DAD
- numbered badge: #0B0F1C 검정 사각 + 흰 텍스트
- 폰트: Apple SD Gothic Neo (국문) / Inter (영문 수치) / JetBrains Mono (caption)
- footer: "속도는벡터 · STYLE A · ACADEMIC" / "CAPSTONE 2026 · FINAL · 2026.05.27"
- speaker notes: 16개 한국어 발표 대본 (슬라이드당 30~45초, 총 12~15분)

# 출력 요청
- 위 모든 수치 + narrative 반영한 16 slide 새 deck
- 디자인 시스템 그대로 (변경 X)
- 추가: speaker notes 도 update (4강 narrative + multi shrinkage 반영)
```

---

## 입력 prompt v2 (압축, 한도 부족 시)

```
[속도는벡터 5/27 deck v3 update]

기존 16 slide deck (white bg + navy accent + numbered badge) 그대로 유지. 수치/narrative 만 W4 sprint finalize 결과로 update:

1. 4강 method ranking (단일 10 cell avg Δ% sel=0.10):
   ★1 HDBSCAN -8.04 / ★2 MB_partial -7.63 / ★3 Hilbert -7.54 / ★4 Hybrid -7.13

2. Tier 1 살아남기 17종, spread 1.21%p — method choice 부차, 분포 인지 boundary 결정적

3. Sweet Spot 정량 boundary: cluster_ratio > 1.4 + intrinsic_dim < 0.85

4. SSN++ ceiling: cluster_ratio 1.29 / intrinsic 0.88 → +1~+2% (boundary)

5. SIFT_sf1 가장 강력: -32~-33% (4강 모두)

6. Multi-vector 일반화 (5/8 STAGE 1+2 완료):
   - 단일 sweet spot 17.13% → multi 0.67% = 25.4× 약화
   - 단일 정확성 = multi 정확성 *필요조건*만 (충분조건 X)
   - multi-table join (STAGE 3) 측정 진행 중 (회의 후 추가)

7. PDX (SIGMOD 2025, CWI Amsterdam) 학술 confirmation:
   "intrinsic_dim + skewness 가 algorithm selection 결정" — 우리 thesis 일치
   Complementary: PDX (compute) vs 본 연구 (pre-process)

8. RQ1: 12 cell ρ < 0 100% 일관 (-0.366~-0.609). DEEP-KM20 ρ=-0.680 [-0.800, -0.440] (그대로)

9. RQ2: 51/52 CI ex (sel=0.10), σ-allocation 격차 < 1% in 7/12 cell

각 슬라이드에 위 수치 정확 반영. 디자인 변경 X.
```

---

## 사용자 진행 절차

1. **회의 전 (~18:00)** 또는 **회의 중 (~19:30)**: Claude Design link 열기
2. v1 (Full) 또는 v2 (압축) 입력
3. Claude Design 이 16 slide 새 deck 생성
4. 결과 download (PDF + zip source)
5. submission/_drafts/academic_deck_v3_source/ 또는 새 폴더에 저장
6. 5/27 발표 자료로 활용 (자문 회신 5/15+ 후 v2 추가 update 가능)

---

## 비상 plan (Claude Design 한도 초과 시)

- Slides.jsx 직접 수정 (로컬 파일 편집)
- `/Users/hyunbin/Capstone/submission/_drafts/academic_deck_v3_source/academic-deck/Slides.jsx` 의 16 React component 수정
- 수치 hardcoded 위치만 update (디자인 그대로)
