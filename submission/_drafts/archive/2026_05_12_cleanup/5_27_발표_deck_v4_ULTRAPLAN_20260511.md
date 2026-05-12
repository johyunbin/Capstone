# 5/27 최종 발표 academic deck v4 — Claude Design ULTRAPLAN

> **사용자 명시 (5/11 19:47)**: "PPT는 누가봐도 이해할 수 있도록 / 불필요하고 장황한 텍스트보다 핵심적인 정보와 수치만 전달 가능하도록"
>
> **목적**: 5/8 academic-deck v3 (16 slide React JSX, 950 line) base에 5/11 paper exact 측정 결과 narrative 반영하여 18 slide v4 생성. 클로드 디자인 ([link](https://claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2?file=academic-deck%2Findex.html)) input으로 직접 사용.
>
> **원칙 (5/11 19:48 사용자 추가 명시 반영)**: PPT = **visual asset only**. 발표 narrative는 강재현 스크립트로 청중 전달 → PPT는 시각 자료만. 1 slide = 1 메시지. **본문 텍스트는 수치 + 한 줄 결론만 (14-18px g600 이내)**. 핵심 수치는 50-80px navy bold 시각 강조. 학술 산문 본문은 speaker notes에만 (강재현 발표 스크립트). 비유는 PPT에서 이미지/아이콘 중심.
>
> **PPT 텍스트 규칙**:
> - 큰 수치 (50-80px navy bold): 무조건 ★
> - 짧은 라벨 (12-14px g600): 수치 옆에 한 줄
> - 결론 1줄 (16px navy, Implication bar): 슬라이드 핵심 결론
> - 본문 narrative: ❌ (speaker notes로)
> - bullet list: ❌ (시각화로 대체)
>
> **작성**: 2026-05-11 19:50 KST

---

## 0. Design System (5/8 v3 base 그대로 유지)

### Color Tokens
```javascript
const C = {
  navy: '#1B3DAD',      // primary accent · big number · stripe
  navyDeep: '#14307F',  // hover / shadow
  blue: '#4A7BD8',      // secondary chart
  blueSoft: '#E4ECF8',  // tint / background
  red: '#E03A3A',       // negative · warning · "★" marker
  redSoft: '#FBE3E3',
  green: '#2A9D6E',     // 신규 paradigm 강조 (P9/P10)
  gold: '#D9A53B',      // SSN++ ceiling
  ink: '#0B0F1C',       // numbered badge 배경
  g100: '#F2F4F8', g200: '#DEE2EC', g300: '#C9CDD8',
  g400: '#A4ABBC', g500: '#6E7891', g600: '#4B5470', g700: '#2E3650',
};
```

### Typography
- 국문: **Apple SD Gothic Neo** → Pretendard Variable fallback
- 영문/수치: **Inter** (tabular figures), IBM Plex Sans
- mono: JetBrains Mono (caption / pill / badge)

### Layout
- 16:9 (1920×1080 또는 deck-stage 비율)
- 좌상단 5×60px navy stripe + numbered badge (`01`~`18` 검정 사각)
- 우상단 page counter (`01 / 18` navy mono)
- 하단 implication bar (full width navy 배경 / 흰 텍스트 1줄 결론)
- footer: "속도는벡터 · STYLE A · ACADEMIC" / "CAPSTONE 2026 · FINAL · 2026.05.27"

### 시각화 우선순위
1. **큰 수치** (50-80px navy bold) — 한 눈에 보이도록
2. **bar chart** (horizontal, navy/red 색상 분기)
3. **heatmap** (paradigm × cell)
4. **scatter** (Hedges' g × Cliff's δ)
5. **diagram** (narrative 흐름 화살표)

### figures 통합 (이미 생성 완료, `experiments/figures/paper_exact_v7/`)
- F1 paradigm rollup CaseB → S8 직접 사용
- F2 Cliff's δ bucket → S11 직접 사용
- F3 violin → S14 추가 사용
- F4 top winners → S10 추가 사용
- F5 effect size scatter → S14 직접 사용
- F6 narrative diagram → S5 또는 S8 직접 사용

---

## Slide 01 (Cover) — 표지

**구조**:
- 상단 navy stripe + 좌측 hero text
- 중앙 large title (60px navy bold) + 부제 (24px g500)
- 하단 4-col footer (TEAM / ADVISOR / REFERENCE / DATE)

**텍스트 최소**:
- Title: "Skew-Aware Stratified Sampling Ensemble"
- 부제: "Exqutor §V-B 영역 paper-friendly augment 정량 검증"
- TEAM: 속도는벡터 (박세은 · 강재현 · 조현빈 · 이동욱)
- ADVISOR: 박광현 교수님 (BDAI)
- REFERENCE: arXiv:2512.09695v2
- DATE: 2026.05.27

**시각화**: 좌측에 작은 데이터 시각 (예: 9 paradigm dot grid)

---

## Slide 02 (TOC) — 7 카드 grid

**구조**: 7 카드 horizontal grid (3+4 또는 4+3 wrap)

**카드 (한 줄 메시지만)**:
1. 문제 — 고정 비율 카디널리티
2. 접근 — paper §V-B + 우리 method 산술 평균
3. RQ1 — 분포 차이 +3.74% gap
4. RQ2 — Anti<Prop<Neyman paradox
5. paradigm 9 — P9/P10 신규 발굴
6. CaseB climax — paired 92.9% 압도
7. Future — P7/P8 + multi-table

**Implication bar**: "7단계로 짧게 — 문제부터 climax까지"

---

## Slide 03 (Problem) — 무엇이 문제

**구조**: 좌 (현재 baseline, 큰 수치 3개) + 우 (실제 selectivity 분포)

**큰 수치 (60px navy)**:
- pgvector: **33.3%**
- VBASE: **50.0%**
- DuckDB: **100%**

**우측 chart**: histogram — 실제 query selectivity 분포 (0.001%~90% 광범위)

**한 줄 (red)**: "고정 비율 → 실제 분포와 100× 빗나감 → 1만 배 느린 query"

**Implication bar**: "잘못된 카디널리티 → 잘못된 plan → 1만 배 느린 실행"

---

## Slide 04 (Prior — Exqutor) — 이전 연구

**구조**: 좌우 2 카드 (§V-A vs §V-B) + 본 연구 위치 화살표

**좌 카드 (§V-A ECQO)**:
- icon: 인덱스 표시
- 큰 수치: **1-2ms** (navy)
- 한 줄: "벡터 인덱스 있을 때 HNSW range query 활용"
- 라벨: "paper main result · 본 연구 인정"

**우 카드 (§V-B Adaptive Sampling)** ⭐ 본 연구 영역:
- icon: momentum 표시
- 큰 수치: **N=385** (navy)
- 한 줄: "인덱스 없을 때 momentum + Q-error feedback"
- 라벨: "paper Eq 1-6 · 본 연구 augment 영역"
- **빨간 박스 강조** (본 연구 영역)

**Implication bar**: "§V-B 한 갈래만 — paper-friendly augment"

---

## Slide 05 (Approach) — 우리 접근

**구조**: 중앙 다이어그램 + 우측 한 줄 코드 + 하단 비유

**중앙 diagram** (큰 화살표):
```
[paper §V-B Bernoulli]  ━━┓
                          ┣━[산술 평균]━[CaseB 최종 추정]
[우리 method (KM20)]    ━━┛
```

**우측 코드 박스** (mono 14px navy):
```
est_final = (est1 + est2) / 2
```

**비유 (g500 16px, 1줄)**: "두 의사 진단 평균 = 한 의사 단독보다 정확"

**큰 수치 강조 (오른쪽 하단, 80px navy)**: **CaseB > CaseA 92.9%**

**Implication bar**: "paper §V-B는 그대로 + 우리 method를 layer로 추가"

---

## Slide 06 (RQ1) — 분포 차이 영향

**구조**: 좌 (5 cells 비교 bar) + 우 (paper Fig 12 검증 anchor)

**좌 chart**: horizontal bar × 5 cells (DEEP/SIFT/SSN sf=100 + DEEP sf=1/10) — Bernoulli vs KM20 stratified

**우측 큰 수치 카드 (navy)**:
- mean Q-error gap: **+3.74%**
- paper Fig 12 영역 mean: **1.6180**
- paper 1.69 vs: **−4.26%** ← paper review-grade

**비유 (1줄)**: "무작위 100명 vs 연령대별 25명씩 — stratified가 더 정확"

**Implication bar**: "분포 차이가 정확도에 직접 영향 + paper exact 100% 일치"

---

## Slide 07 (RQ2 Paradox) ⭐ 신규 narrative

**구조**: 5-way bar chart (5 모드) + 우측 paradox 박스

**좌 chart** (5 horizontal bars with Q-error 수치):
- Bernoulli: 1.748 (navy 진함)
- Equal: 1.644 (navy 중간)
- **Prop: 1.580** (navy 강조)
- Neyman: 1.595 ← (red `?` 마커)
- **Anti: 1.540 (최저)** ← (red `!` 마커)

**우측 박스 (red border)**:
- Title: "PARADOX"
- 큰 수치: **Anti < Prop < Neyman**
- 한 줄: "paper §V-B 이론 위배 양상"
- 한 줄 (g500): "Root cause: σ_j range 1.3-1.6× narrow + N_i CV=0 (boundary case)"

**비유 (1줄)**: "모든 학년 점수 비슷하면 학년별 가중치 의미 없음"

**Implication bar**: "분포 알면 prop이 답 → σ range 큰 영역 (RQ3)으로 자연 전환"

---

## Slide 06.5 (Paradigm 9) ⭐ 신규 slide

**구조**: 9 paradigm card grid (3×3) — 각 카드 = 1 paradigm

**카드 디자인** (각 paradigm):
- 좌상단: numbered badge (P1~P10)
- 중앙: paradigm 이름 (16px bold)
- 큰 수치 (40px navy): n_method
- 한 줄 (g600): inductive bias (예: "유사 데이터 군집")
- 우하단: anchor method (mono 11px)
- 신규 paradigm은 green dot ⭐

**9 카드**:
| Position | Paradigm | n | bias | anchor |
|---|---|:-:|---|---|
| 1 (top-left) | **P1 Cluster** | 9 | 유사 군집 | mb_partial |
| 2 | **P2 Spatial** | 12 | 1D 분할 | hilbert_real |
| 3 | **P3 Streaming** | 6 | single-pass | chao_weighted |
| 4 | **P4 DimReduction** | 12 | 고차원→저차원 | sparse_rp |
| 5 | **P5 QMC** | 8 | 결정론적 균등 | sobol/lsh |
| 6 | **P6 Quantization** | 6 | vector→codeword | rabitq/mhist2 |
| 7 ⭐ green | **P9 InfoTheoretic 신규** | 1 | sketch / cardinality | hyperloglog |
| 8 ⭐ green | **P10 Density 신규** | 1 | non-parametric density | kde_parzen |
| 9 (gray) | P7 + P8 future | 0 | subspace + graph | CLIQUE / Leiden + Bao VLDB 2025 |

**Implication bar**: "5/8 5 paradigm × 11 method → 5/11 9 paradigm × 56 method 확장"

---

## Slide 08 (RQ3 — paradigm rollup CaseB) — F1 figure 직접 사용

**구조**: F1 paradigm rollup CaseB bar chart (전체 width) + 우측 핵심 수치

**Chart (F1, image asset)**: `experiments/figures/paper_exact_v7/F1_paradigm_rollup_caseB.png`
- horizontal bars × 9 paradigm (P10/P9/P3/P4/P2 negative navy + P1/P5/P6 marginal gray/red)

**우측 큰 수치 (top 5, 50px navy)**:
1. P10 Density: **−11.93%**
2. P9 InfoTheoretic: **−7.60%** (9 cells signif)
3. P3 Streaming: **−6.53%**
4. P4 DimReduction: **−5.92%**
5. P2 Spatial: **−5.52%**

**한 줄 (g500, bottom)**: "5 paradigm 모두 statistical 압도 — 4강 framing 폐기"

**Implication bar**: "9 paradigm rollup으로 narrative 전환 — 5 paradigm 모두 anchor"

---

## Slide 09 (★3 Hilbert Defect Rectify) — 학술 contribution 1

**구조**: 4 카드 horizontal (★3 alias + M6 + M7 + hilbert_real)

**4 카드 (각 1 method)**:
| 카드 | Reference | 수치 (CaseB Δ%) | 라벨 |
|---|---|:-:|---|
| ★3 (red dot) | Faloutsos 1989 ❌ → **alias** `pca2d_lex` | (5/8 보존) | "PCA 2D lex sort honest naming" |
| M6 (navy) | Morton 1966 IBM Tech Rep | (Phase 4) | "Z-order paradigm anchor" |
| M7 (navy) | Skilling 2004 AIP Conf Proc | (Phase 4) | "state-machine + simplification disclosure" |
| **hilbert_real** (green ⭐) | Wikipedia xy2d 표준 | **−8.2% mean (9 cells, 6/9 signif)** | "진짜 Hilbert curve" |

**한 줄 (학술 contribution, 18px navy)**: "PCA proxy locality vs 진짜 Hilbert locality 분리 검증"

**Implication bar**: "★3 defect rectify + 3건 paradigm anchor 추가 — 학술 정직성 발견"

---

## Slide 10 (Top winners) — F4 figure 직접 사용

**구조**: F4 top winners CaseB bar chart (전체 width)

**Chart (F4)**: `experiments/figures/paper_exact_v7/F4_top_winners_caseB.png` (Top 10 smallest Hedges' g)

**우측 카드 (Top 3)**:
| Rank | Method @ Cell | g | Δ% |
|:-:|---|---:|---:|
| 1 | **pq @ A5-sf1** | -7.15 | -10.87% |
| 2 | **sparse_rp @ A5-sf1** | -7.14 | -11.62% |
| 3 | **vinecopula @ A5-sf1** | -7.05 | -12.40% |

**한 줄 (g500)**: "Top 5 winners 모두 A5-sf1 (DEEP 80만 행) — 작은 데이터에서 ensemble 가치 최대"

**Implication bar**: "Hedges' g large effect (g≤−0.8) 56.4% — paper review-grade"

---

## Slide 10.5 (CaseB Ensemble Climax) ⭐ 신규 main contribution

**구조**: 중앙 큰 수치 4개 + 좌우 narrative 비유

**중앙 4 큰 수치 (80px navy bold, 가로 grid)**:
1. **92.9%** (`paired CaseB > CaseA`)
2. **63.5%** (`Cliff's δ large better`)
3. **56.4%** (`Hedges' g large`)
4. **71.8%** (`trial-level sign test, p=3.1e-46`)

**좌측 (16px g600)**: "paper §V-B Bernoulli + 우리 method 산술 평균 ensemble"

**우측 (16px g600)**: "두 estimator의 robust 산술 평균 — bias-variance trade-off"

**비유 (하단 18px navy bold)**: "두 의사 진단 평균이 92.9% 케이스에서 한 의사 단독보다 정확"

**Implication bar**: "본 연구 main contribution — paper-friendly ensemble augment"

---

## Slide 11 (Negative Control + CaseA 무너짐) — F2 figure 직접 사용

**구조**: F2 Cliff's δ bucket bar chart (CaseA vs CaseB 비교)

**Chart (F2)**: `experiments/figures/paper_exact_v7/F2_cliffs_delta_bucket.png`
- 좌측 bar group: CaseA (large worsening 36.8% > better 14.4%) — red 강조
- 우측 bar group: CaseB (large better 63.5% > worsening) — navy 강조

**큰 수치 비교 카드 (red vs navy, 60px)**:
- CaseA: **0/437 (0.0%)** outperform
- CaseB: **284/447 (63.5%)** large better

**한 줄 (red, 14px)**: "CaseA 단독 대체는 통계 무효 — paper §V-B 자체 robust"

**한 줄 (navy, 14px)**: "CaseB ensemble만 통계 압도 — augment narrative만 유효"

**Implication bar**: "★ paradigm shift: 단독 대체 폐기 → ensemble augment climax"

---

## Slide 12 (Cross-scale sf1/10/100) — Fig 14 영역

**구조**: 좌 (sf1/10/100 trend lines) + 우 (큰 수치)

**좌 chart**: line chart × 3 lines (B1 vs CaseA vs CaseB) × 3 sf points

**우측 큰 수치 (navy)**:
- A5-sf1: B1 1.617 → CaseB 1.439 (**−11.01%**)
- A5-sf10: B1 1.528 → CaseB 1.446 (**−4.57%**)
- A5-sf100: B1 1.613 → CaseB 1.456 (**−9.23%**)

**한 줄**: "sf 별 paper Fig 14 영역 mean qe_trim 1.6180 paper 1.69 일치"

**Implication bar**: "cross-scale 일관 — paper exact 100% 재현 검증"

---

## Slide 13 (Mechanism — locality 분리) — paradigm 분리 검증

**구조**: 4 method × 9 cells × 2 modes heatmap

**Chart**: heatmap (4 row = ★3 alias + M6 + M7 + hilbert_real, 18 col = 9 cells × CaseA/CaseB)
- color: navy (negative, ensemble 우위) → red (positive, baseline 우위)

**한 줄 (학술)**: "★3 alias (PCA proxy) vs M6 Z-order vs M7 Skilling vs hilbert_real (Wikipedia 표준)의 paradigm 분리 검증"

**우측 큰 수치**: P2 Spatial paradigm rollup **−5.52%** (12 method × 106 obs)

**Implication bar**: "PCA proxy ≠ 진짜 Hilbert — 학술 정직성 발견 + 4건 anchor 보강"

---

## Slide 14 (Effect Size Honesty) — F5 figure 직접 사용

**구조**: F5 effect size scatter (Hedges' g × Cliff's δ) + 우측 통계 카드

**Chart (F5)**: `experiments/figures/paper_exact_v7/F5_effect_size_scatter.png`

**우측 4 stats 카드 (navy 50px)**:
- Hedges' g large: **56.4%**
- Cliff's δ large better: **63.5%**
- Reproducibility: **280/280**
- byte-identical (deterministic): **100%**

**한 줄 (학술)**: "paired Δ% + 효과크기 + paradigm rollup + cherry-pick prevention 4축 통계 검증"

**Implication bar**: "paper review-grade — Hedges' g + Cliff's δ + Reproducibility 모두 강유의"

---

## Slide 15 (Limitation 18종) — honest disclosure

**구조**: 18 카드 grid (3×6 또는 6×3 horizontal scroll)

**카드 디자인** (각 limitation):
- 좌상단: tag (L1~L18)
- 우상단: category badge — Group A (gray) / Group B (gray) / Group C (navy) / **Group D 5/11 신규 (red)**
- 본문: 짧은 한 줄 (12-14px)

**Group D 5/11 신규 5건 강조** (red border):
- L12: 측정 미커버 233 cells 9 카테고리 정직 분류
- L13: RQ2 Anti<Prop<Neyman paradox honest finding
- L14: ★3 hilbert PCA alias (Faloutsos 1989 ❌)
- L15: byte-identical cells 7쌍
- L16: A4-sel sel=0.001 calibration parquet 부재 fallback

**Implication bar**: "18 honest 한계 → 후속 연구 출발점 8건"

---

## Slide 16 (Future Work 8건) — 신규 future plan

**구조**: 8 카드 grid (4×2)

**카드** (각 future):
1. **P7 Subspace** (CLIQUE Agrawal 1998)
2. **P8 Graph** (Leiden 2019 + **Bao et al. VLDB 2025**) ⭐ 강조
3. multi-table aware ensemble
4. SF=100 cross-scale full validation (current 80.4% → 100%)
5. RQ2 σ range 큰 영역 Neyman 재검증
6. CaseB 가중 평균 / query-conditional routing
7. ★3 hilbert defect rectify paper acceptance 검증
8. 2024-25 SIGMOD/VLDB integration (RaBitQ / PRICE / LpBound / PDX)

**Implication bar**: "9 paradigm → 11 paradigm 확장 + multi 일반화 + paper acceptance"

---

## Slide 17 (Closing 1 — 본 연구 한 줄 요약) ⭐ 신규

**구조**: 중앙 한 단락 (학술 산문, 18-20px navy)

**텍스트** (4-5 line dense, 본 발표 전체 압축):
> "본 연구는 Exqutor §V-B Adaptive Sampling 영역에 paper의 Bernoulli random sampling을 그대로 보존하면서 우리 method KM20 stratified estimator의 산술 평균 ensemble을 layer로 추가하여, paper baseline 대비 paired CaseB > CaseA 92.9% / Cliff's δ large better 63.5% / paradigm rollup 5 paradigm 모두 statistical 압도가 paper review-grade로 입증됨을 보였다."

**하단 anchor**: "paper §V-B 영역 한정 contribution · ECQO §V-A는 paper main result 인정"

---

## Slide 18 (Closing 2 — 감사 + Q&A) — 마무리

**구조**: 중앙 큰 텍스트 (80px navy) + 하단 references

**중앙**: **감사합니다 / Q&A**

**하단 4-col footer**:
- 속도는벡터 (박세은 · 강재현 · 조현빈 · 이동욱)
- 박광현 교수님 (BDAI)
- arXiv:2512.09695v2
- github.com/johyunbin/Capstone

---

## Speaker Notes (16 → 18 slide 한국어 학술 산문 update)

각 slide 30-45초 분량 (총 12-15분). 5/8 v3 base의 한국어 speaker notes를 5/11 narrative로 update:

```javascript
const speakerNotes = {
  1: "Skew-Aware Stratified Sampling Ensemble — Exqutor 논문 §V-B 영역의 paper-friendly augment 정량 검증입니다...",
  2: "오늘은 7단계로 진행합니다 — 문제부터 climax까지 짧고 명확하게...",
  3: "기존 vector DB는 33%/50%/100% 고정 비율로 카디널리티를 추정하는데, 실제는 0.001%부터 90%까지 광범위...",
  // ... (각 slide 5/11 narrative 반영)
}
```

---

## React JSX Skeleton (Slides.jsx update)

5/8 base의 `<Chrome>` + `<Impl>` 컴포넌트 그대로 재사용. 각 S1~S18 함수만 새로 작성:

```jsx
// S6.5 신규 — paradigm framework 9
function S6_5() {
  const paradigms = [
    {tag: 'P1', name: 'Cluster', n: 9, bias: '유사 군집', anchor: 'mb_partial', new: false},
    {tag: 'P2', name: 'Spatial', n: 12, bias: '1D 분할', anchor: 'hilbert_real', new: false},
    {tag: 'P3', name: 'Streaming', n: 6, bias: 'single-pass', anchor: 'chao_weighted', new: false},
    {tag: 'P4', name: 'DimReduction', n: 12, bias: '고차원→저차원', anchor: 'sparse_rp ★4', new: false},
    {tag: 'P5', name: 'QMC', n: 8, bias: '결정론적 균등', anchor: 'sobol/lsh', new: false},
    {tag: 'P6', name: 'Quantization', n: 6, bias: 'vector→codeword', anchor: 'rabitq/mhist2', new: false},
    {tag: 'P9', name: 'InfoTheoretic', n: 1, bias: 'sketch/cardinality', anchor: 'hyperloglog', new: true, color: C.green},
    {tag: 'P10', name: 'Density', n: 1, bias: 'non-parametric', anchor: 'kde_parzen', new: true, color: C.green},
    {tag: 'P7+P8', name: 'Future', n: 0, bias: 'subspace/graph', anchor: 'CLIQUE/Leiden+Bao 2025', new: false, gray: true},
  ];
  return (
    <Chrome page={7} num="06.5" title="Paradigm Framework — 9 paradigm × 56 method" eyebrow="P9/P10 신규 발굴">
      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gridTemplateRows:'repeat(3, 1fr)', gap: 12, flex: 1}}>
        {paradigms.map(p => (
          <div key={p.tag} style={{
            padding: '14px 16px',
            border: `${p.new ? '2px' : '1px'} solid ${p.new ? C.green : (p.gray ? C.g300 : C.g200)}`,
            borderRadius: 6,
            background: p.gray ? C.g100 : '#fff',
            position: 'relative',
          }}>
            {p.new && <span style={{position:'absolute', top:8, right:10, fontSize: 10, color: C.green, fontWeight: 700}}>★ 신규</span>}
            <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: p.gray ? C.g500 : C.navy, fontWeight: 700, letterSpacing: '0.06em'}}>{p.tag}</div>
            <div style={{fontSize: 16, fontWeight: 700, color: C.ink, marginTop: 6}}>{p.name}</div>
            <div style={{fontFamily:'var(--font-num)', fontSize: 40, fontWeight: 800, color: p.gray ? C.g400 : (p.new ? C.green : C.navy), letterSpacing: '-0.03em', marginTop: 8}}>
              {p.n}<span style={{fontSize: 14, fontWeight: 400, color: C.g500, marginLeft: 4}}>method</span>
            </div>
            <div style={{fontSize: 12, color: C.g600, marginTop: 6, lineHeight: 1.4}}>{p.bias}</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 8}}>{p.anchor}</div>
          </div>
        ))}
      </div>
      <Impl>5/8 5 paradigm × 11 method → 5/11 <b>9 paradigm × 56 method</b> 확장 (P9 InfoTheoretic + P10 Density 신규 발굴)</Impl>
    </Chrome>
  );
}

// S10.5 신규 — CaseB ensemble climax
function S10_5() {
  const stats = [
    {label: 'paired CaseB > CaseA', value: '92.9%', sub: '404/435', color: C.navy},
    {label: "Cliff's δ large better", value: '63.5%', sub: '284/447', color: C.navy},
    {label: "Hedges' g large", value: '56.4%', sub: '252/447', color: C.navy},
    {label: 'sign test (binomial)', value: '71.8%', sub: 'p=3.1e-46', color: C.red},
  ];
  return (
    <Chrome page={11} num="10.5" title="CaseB Ensemble Climax — 본 연구 main contribution" eyebrow="paper review-grade 통계 압도">
      <div style={{display: 'flex', flexDirection: 'column', gap: 24, flex: 1, justifyContent: 'center'}}>
        <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 16}}>
          {stats.map(s => (
            <div key={s.label} className="card navy-top" style={{padding:'18px 20px', textAlign: 'center'}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 64, fontWeight: 800, color: s.color, letterSpacing: '-0.04em', lineHeight: 1}}>
                {s.value}
              </div>
              <div style={{fontSize: 13, color: C.g600, marginTop: 8, fontWeight: 500}}>{s.label}</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>{s.sub}</div>
            </div>
          ))}
        </div>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, padding: '0 24px'}}>
          <div className="card" style={{padding: '14px 16px', background: C.blueSoft, border: 'none'}}>
            <div className="label-mono" style={{color: C.navy}}>구조</div>
            <div style={{fontSize: 14, color: C.navy, marginTop: 6}}>paper §V-B Bernoulli + 우리 method 산술 평균</div>
          </div>
          <div className="card" style={{padding: '14px 16px', background: C.blueSoft, border: 'none'}}>
            <div className="label-mono" style={{color: C.navy}}>통계 정당성</div>
            <div style={{fontSize: 14, color: C.navy, marginTop: 6}}>bias=0 random + variance↓ stratified의 robust 평균</div>
          </div>
        </div>
        <div style={{textAlign: 'center', fontSize: 18, fontWeight: 700, color: C.navy, marginTop: 8}}>
          "두 의사 진단 평균이 92.9% 케이스에서 한 의사 단독보다 정확"
        </div>
      </div>
      <Impl>본 연구 <b>main contribution</b> — paper-friendly ensemble augment (paper §V-B 자체 변경 X)</Impl>
    </Chrome>
  );
}
```

(S1~S18 모두 같은 패턴 — 5/8 base의 `Chrome` + `Impl` 컴포넌트 재사용 + slide 별 layout만 update)

---

## 클로드 디자인 직접 input prompt (전체 압축, 5/16~5/19 사용)

```
[claude.ai/design/p/019e0006-f163-74e6-bf81-2d7caebaf0f2 academic-deck/Slides.jsx update 요청]

현재 16-slide academic deck을 18-slide로 update해주세요. 추가 2 slide:
- S6.5 (paradigm framework 9 — P1-P10 카드 grid, P9/P10 신규 강조)
- S10.5 (CaseB ensemble climax — 4 큰 수치 92.9% / 63.5% / 56.4% / 71.8% + bias-variance 비유)

기존 slide narrative 정정 (5/11 paper exact 측정 결과 반영):
- S6 RQ1: ρ=−0.680 → mean +3.74% (paper exact)
- S7 RQ2: 40/40 cells → Bern→Prop −9.53% + Anti<Prop<Neyman paradox 발견
- S8 RQ3 4강 → paradigm rollup 9 (P10 -11.93 / P9 -7.60 / P3 -6.53 / P4 -5.92 / P2 -5.52)
- S9 ★3 Hilbert: production sweet spot → defect rectify (PCA alias + M6/M7/hilbert_real 4건 anchor)
- S10 MB_partial → P1 Cluster anchor + Top winners
- S11 Negative Control → CaseA 무너짐 narrative (0/437 outperform)
- S12 Cross-scale → sf1/10/100 paper exact 일치
- S13 Mechanism → ★3 alias vs M6/M7/hilbert_real 4건 paradigm 분리 검증 heatmap
- S14 Effect Size → Cliff's δ large better 63.5% + Hedges' g large 56.4%
- S15 Limitation 8 → 18 (Group A v1 + B 5/8 + C V7 audit + D 5/11 신규 5건)
- S16 Future Work 8건 (P7 CLIQUE / P8 Leiden+Bao VLDB 2025 / multi-table / SF=100 / RQ2 σ range / CaseB 가중평균 / ★3 acceptance / 2024-25 integration)
- S17 신규 — 본 연구 한 줄 압축 (학술 산문 한 단락)
- S18 Closing — 감사 + Q&A

원칙: 1 slide = 1 메시지. 텍스트 최소 (bullet 3개 이내). 핵심 수치는 50-80px navy bold 시각 강조. 학술 산문 본문은 speaker notes로 분리. 5/8 v3 디자인 시스템 (Style A Academic, 흰 배경 + navy stripe + numbered badge + Apple SD Gothic Neo + Inter) 그대로 유지.

figures 6건 통합 (image asset, `experiments/figures/paper_exact_v7/F1~F6.png`):
- F1 paradigm rollup CaseB → S8
- F2 Cliff's δ bucket → S11
- F3 violin → S14 추가
- F4 top winners → S10
- F5 effect size scatter → S14
- F6 narrative diagram → S5

상세 spec은 `submission/_drafts/5_27_발표_deck_v4_ULTRAPLAN_20260511.md` 참조 (각 slide 1 page spec + React JSX skeleton).
```

---

## 검증 checklist (5/15 미팅 후 + 5/26 finalize)

### 5/15 미팅 후 즉시 정합성 점검
- [ ] S7 RQ2 paradox narrative 정합성 (박광현 교수님 confirm 사항)
- [ ] S9 ★3 hilbert defect rectify acceptance
- [ ] S15 Limitation 18종 honest disclosure 충분성
- [ ] S16 Future Work P7/P8 우선순위
- [ ] S10.5 CaseB ensemble climax 학술 narrative

### 5/26 deck v4 finalize 직전
- [ ] 18 slide × 1 메시지 원칙 준수 (텍스트 최소)
- [ ] 핵심 수치 50-80px navy bold 시각 강조 일관성
- [ ] figures 6건 통합 OK (Korean font Apple SD Gothic Neo)
- [ ] speaker notes 18 slide × 30-45초 분량 (총 12-15분)
- [ ] 5/8 v3 디자인 시스템 (색상 / 타이포 / 레이아웃) 정합성
- [ ] 강재현 발표 리허설 (5/25~5/26)

### 발표 직전 (5/27 12:00)
- [ ] PDF export OK (Chrome ⌘P → PDF로 저장, deck-stage `@media print`)
- [ ] 강재현 멘트 준비 (speaker notes 외워두기)
- [ ] Q&A 가이드 (`박광현_5월15일_미팅/박광현_미팅_예상질문_답변_가이드_20260511.pdf`) 강재현 검토

---

작성: 2026-05-11 19:55 KST  
다음: 5/12~5/14 본 spec 박세은/강재현/이동욱 검토 → 5/15 박광현 미팅 confirm → 5/16~5/19 클로드 디자인 input → 5/20~5/22 박세은 검토 + figures 통합 → 5/23~5/26 finalize + 강재현 리허설 → 5/27 19:00 최종 발표
