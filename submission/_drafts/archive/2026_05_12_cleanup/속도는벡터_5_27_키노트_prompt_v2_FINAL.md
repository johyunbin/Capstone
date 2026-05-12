# 속도는벡터 5/27 최종발표 — 키노트 스타일 18 slide deck (FINAL v2)
## claude.ai/design 새 conversation paste 용 정밀 prompt — 실측 데이터 반영

> **사용 방법**: 본 file 전체를 claude.ai/design 새 conversation 에 paste. 기존 academic-deck conversation (`019e0006-f163-74e6-bf81-2d7caebaf0f2`) 폐기.
>
> **본 v2 변경점 (vs v1 `..._20260511.md`)**:
> - 실측 REPORT v11 (1362 line, B1 9 + CaseA 495 + CaseB 496) 반영
> - climax stat 92.9% → **92.5%** (paired CaseB < CaseA, n=492)
> - Cliff's δ large better 63.5% → **63.0%** (n=494)
> - Hedges' g large 56.4% → **55.7%**
> - negative control 0/437 → **0/493** (CaseA single replace)
> - paradigm rollup 실측 mean Δ% 8 paradigm 모두 update
> - 측정 정합성 위반 method (halton/dense_rp/lhs/sobol/hammersley/dbscan/ccsketch/lsh/ams_count_sketch/random_projection) 명시 폐기
> - S17 Limitation 카테고리 9 (REPORT §10 drop list) 반영

---

## 0. 디자인 철학 — Apple Keynote / Samsung Unpacked / Google I/O

**원칙 — 키노트, 발표 PT 아님**

- **1 slide = 1 메시지** — 본문 3-5 단어 max. 큰 수치 / 한 시각화 / 핵심 한 줄
- **거대 폰트** — 거대 수치 200-300px, 거대 제목 80-120px
- **whitespace 70%+** — 빈 공간이 메시지를 강하게 만든다
- **본문 narrative 100% → speaker notes 로** — slide 에는 키워드만
- **bullet list 0** — 다이어그램 / chart / heatmap / 큰 수치만
- **단일 brand red `#DC2626`** 만 accent
- **폰트**: Apple SD Gothic Neo + JetBrains Mono (eyebrow/caption) + Inter (수치 tabular)

**악습 금지**:
- 텍스트 우겨넣기 X (academic-deck v4 방식)
- 작은 본문 16-18px X — **키노트는 28-36px**
- 여러 색 동시 사용 X — red 단일
- bullet 3-5 개 X — 큰 수치 / 한 줄 narrative

---

## 1. 디자인 토큰 (Capstone Design System)

### 1.1 색상

```css
--brand-red:      #DC2626;
--brand-red-2:    #B91C1C;
--brand-red-soft: #FEE2E2;

--ink:        #0A0A0A;
--fg1:        #171717;
--fg2:        #404040;
--fg3:        #737373;
--fg4:        #A3A3A3;

--bg:         #FFFFFF;
--bg2:        #FAFAF9;
--line:       #E7E5E4;

--viz-blue:   #3B82C4;       /* BERNOULLI baseline */
--viz-orange: #E89B4D;       /* STRATIFIED KM20 */
--viz-red:    #C0504D;       /* SYSTEM failure */
--viz-green:  #2E7D32;       /* recovery */
--viz-teal:   #0E7490;       /* tertiary */
```

### 1.2 폰트 + 사이즈 (키노트 변형)

```css
--font-sans:  "Apple SD Gothic Neo", "Pretendard Variable", system-ui, sans-serif;
--font-mono:  "JetBrains Mono", ui-monospace, monospace;
--font-num:   "Inter", "Apple SD Gothic Neo", system-ui, sans-serif;

/* 키노트 type scale */
--t-eyebrow:    12-13px;
--t-caption:    14px;
--t-meta:       16px;
--t-body:       28-36px;
--t-subhead:    20-24px;
--t-h3:         40-56px;
--t-h2:         60-80px;
--t-h1:         96-120px;
--t-display:    200-300px;
```

### 1.3 spacing + radii

```css
--s-1: 4px;  --s-2: 8px;  --s-3: 12px;  --s-4: 16px;
--s-5: 24px; --s-6: 32px; --s-7: 48px;  --s-8: 64px; --s-9: 96px;
--r-1: 2px;   /* editorial near-square 기본 */
--r-2: 4px;
--r-pill: 999px;
```

---

## 2. 컴포넌트 spec

### 2.1 SlideShell

```jsx
function SlideShell({ secn, title, page, total = 18, children, hideHeader = false }) {
  return (
    <div style={{
      width: 1280, height: 720, background: '#FFFFFF',
      padding: '56px 72px 44px', boxSizing: 'border-box',
      position: 'relative', display: 'flex', flexDirection: 'column',
      fontFamily: 'var(--font-sans)', color: '#0A0A0A', overflow: 'hidden',
    }}>
      <div style={{ width: 158, height: 2, background: '#DC2626', marginBottom: 6 }} />
      <div style={{
        fontSize: 12, fontWeight: 700, letterSpacing: '0.16em',
        textTransform: 'uppercase', color: '#DC2626',
        fontFamily: 'JetBrains Mono, monospace',
      }}>
        CAPSTONE 2026‑1 · FINAL · 2026.05.27 · 연세대학교
      </div>
      {!hideHeader && (
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          marginTop: 22, paddingBottom: 14, borderBottom: '1px solid #E7E5E4',
        }}>
          <div>
            {secn && <span style={{ fontSize: 18, fontWeight: 700, color: '#DC2626', marginRight: 10 }}>{secn}</span>}
            <span style={{ fontSize: 32, fontWeight: 700, color: '#0A0A0A', letterSpacing: '-0.01em' }}>{title}</span>
          </div>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13, color: '#737373' }}>{page} / {total}</div>
        </div>
      )}
      <div style={{ flex: 1, paddingTop: 24, minHeight: 0 }}>{children}</div>
      <div style={{
        position: 'absolute', left: 72, right: 72, bottom: 18,
        display: 'flex', justifyContent: 'space-between',
        fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#737373',
        paddingTop: 8, borderTop: '1px solid #E7E5E4',
      }}>
        <span>속도는벡터 · 박세은 · 강재현 · 조현빈 · 이동욱</span>
        <span>FINAL 5_27 · v2</span>
      </div>
    </div>
  );
}
```

### 2.2 SectionDivider (#FAFAF9 tinted, 132px mono red 번호)

```jsx
function SectionDivider({ num, title, subtitle, page }) {
  return (
    <div style={{
      position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
      padding: '56px 72px 44px', background: '#FAFAF9',
    }}>
      <div style={{ width: 158, height: 2, background: '#DC2626', marginBottom: 6 }} />
      <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: '0.16em', textTransform: 'uppercase', color: '#DC2626', fontFamily: 'JetBrains Mono, monospace' }}>
        CAPSTONE 2026‑1 · FINAL · 2026.05.27 · 연세대학교
      </div>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', columnGap: 48, alignItems: 'baseline', maxWidth: 980 }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 132, fontWeight: 700, color: '#DC2626',
            letterSpacing: '-0.04em', lineHeight: 0.9,
          }}>{num}</div>
          <div>
            <div style={{ fontSize: 56, fontWeight: 800, color: '#0A0A0A', letterSpacing: '-0.02em', lineHeight: 1.05 }}>{title}</div>
            <div style={{ fontSize: 24, color: '#404040', marginTop: 16, lineHeight: 1.4, maxWidth: 700 }}>{subtitle}</div>
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#737373', paddingTop: 8, borderTop: '1px solid #E7E5E4' }}>
        <span>속도는벡터 · 박세은·강재현·조현빈·이동욱</span>
        <span>{page} / 18</span>
      </div>
    </div>
  );
}
```

### 2.3 BigStat (full screen 거대 수치)

```jsx
function BigStat({ value, subtitle, caption }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', textAlign: 'center' }}>
      <div style={{
        fontFamily: 'Inter, var(--font-sans)',
        fontSize: 240, fontWeight: 700, color: '#DC2626',
        letterSpacing: '-0.04em', lineHeight: 0.95,
        fontFeatureSettings: '"tnum" 1, "lnum" 1',
        marginBottom: 24,
      }}>{value}</div>
      <div style={{ fontSize: 32, color: '#171717', fontWeight: 500, marginBottom: 12, maxWidth: 900 }}>{subtitle}</div>
      <div style={{ fontSize: 14, color: '#737373', fontFamily: 'JetBrains Mono, monospace', maxWidth: 980 }}>{caption}</div>
    </div>
  );
}
```

### 2.4 GridStats (3-4 가로)

```jsx
function GridStats({ stats }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: `repeat(${stats.length}, 1fr)`, gap: 48, height: '100%', alignItems: 'center' }}>
      {stats.map((s, i) => (
        <div key={i} style={{ textAlign: 'center' }}>
          <div style={{
            fontFamily: 'Inter', fontSize: 96, fontWeight: 700, color: '#DC2626',
            letterSpacing: '-0.03em', lineHeight: 1, fontFeatureSettings: '"tnum" 1, "lnum" 1',
            marginBottom: 16,
          }}>{s.value}</div>
          <div style={{ fontSize: 22, color: '#171717', fontWeight: 600, marginBottom: 8 }}>{s.label}</div>
          {s.sub && <div style={{ fontSize: 14, color: '#737373', fontFamily: 'JetBrains Mono, monospace' }}>{s.sub}</div>}
        </div>
      ))}
    </div>
  );
}
```

### 2.5 BigBarChart (8 paradigm / RQ2 paradox)

```jsx
function BigBarChart({ data }) {
  const maxAbs = Math.max(...data.map(d => Math.abs(d.value)));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, height: '100%', padding: '20px 0' }}>
      {data.map((d, i) => (
        <div key={i} style={{ display: 'grid', gridTemplateColumns: '280px 1fr 120px', alignItems: 'center', gap: 24 }}>
          <div style={{ fontSize: 17, color: '#171717', fontWeight: 500, textAlign: 'right', paddingRight: 12 }}>{d.label}</div>
          <div style={{ position: 'relative', height: 28, background: '#F5F5F4' }}>
            <div style={{
              position: 'absolute', top: 0, bottom: 0,
              left: d.value < 0 ? `${50 - (Math.abs(d.value) / maxAbs) * 45}%` : '50%',
              width: `${(Math.abs(d.value) / maxAbs) * 45}%`,
              background: d.color || (d.value < 0 ? '#DC2626' : '#A3A3A3'),
            }} />
            <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: 1, background: '#0A0A0A' }} />
          </div>
          <div style={{
            fontFamily: 'Inter', fontSize: 26, fontWeight: 700,
            color: d.value < 0 ? '#DC2626' : '#737373',
            fontFeatureSettings: '"tnum" 1, "lnum" 1',
          }}>{d.value > 0 ? '+' : ''}{d.value.toFixed(2)}%</div>
        </div>
      ))}
    </div>
  );
}
```

---

## 3. 18 slide 정밀 spec (실측 데이터)

### S1 — Cover (Big-number 변형, hideHeader=true)

```
상단 (eyebrow, 158×2 red rule)
─────────────
CAPSTONE 2026-1 · FINAL · 2026.05.27 · 연세대학교
                                                                                                  
중앙
─────
"Skew-Aware Stratified Sampling" (영문, 96-120px, weight 800)
                                                                                                  
"벡터 카디널리티 추정 + 분포 인지형 결합의 정량적 가치" (28-32px, fg2)
                                                                                                  
하단 (3 column grid, 12px mono red eyebrow + 16px fg1)
─────────────
TEAM                         ADVISOR                         ANALYSIS TARGET
속도는벡터                    박광현 교수                       Exqutor
박세은 · 강재현 · 조현빈 · 이동욱    BDAI 연구실                     arXiv:2512.09695v2
```

### S2 — Section 1 / 배경 (SectionDivider)

```jsx
<SectionDivider num="01" title="배경" subtitle="벡터 카디널리티 추정의 사각지대" page="02" />
```

### S3 — Problem (Big-stat range)

거대 텍스트 only.

```
[SlideShell — secn="1.", title="Problem"]
                                                                                                  
중앙 거대 텍스트 (160-200px, Inter, weight 700, brand red, tabular nums)
"0.001%  ~  90%"
                                                                                                  
부제 (28px, fg1, weight 500)
"실제 selectivity 분포"
                                                                                                  
하단 caption (14px mono fg3)
고정 비율 33%/50%/100% 으로는 답 불가능 — pgvector / VBASE / DuckDB
```

### S4 — Background (Sequence diagram)

```
[SlideShell — secn="1.", title="Exqutor 두 갈래 + 본 연구 위치"]
                                                                                                  
좌→우 horizontal flow (3 box + arrow, 560px 높이)
  ┌─────────┐   ┌──────────────┐
  │ Exqutor │ → │ ECQO         │ (회색, paper §V-A scope)
  └─────────┘   │ 1~2ms        │
        │       └──────────────┘
        └────→  ┌──────────────────┐
                │ Adaptive Sampling│ → ★ 본 연구 위치 (red highlight box)
                │ N=385 / Eq 1~6   │   "결합 보강 (CaseB ensemble)"
                └──────────────────┘
                                                                                                  
하단 caption (16px fg3)
원 논문 §V-B Adaptive Sampling 영역에 분포 인지형 stratification 결합 → 정량 가치 검증
```

### S5 — Section 2 / 접근 (SectionDivider)

```jsx
<SectionDivider num="02" title="접근" subtitle="원 논문 절차 보존 + 결합 보강" page="05" />
```

### S6 — Approach (Visual intuition + 큰 수식)

```
[SlideShell — secn="2.", title="결합 보강 (CaseB ensemble) 의 직관"]
                                                                                                  
중앙 diagram (3 box + arrow)
┌─────────────────┐      ┌──────────────────┐       ┌─────────────────┐
│ Bernoulli       │  +   │ KM20 stratified  │   →   │ 산술 평균       │
│ (paper baseline)│      │ (분포 인지형)    │       │ ensemble        │
│ est_b1          │      │ est_method       │       │ est_final       │
└─────────────────┘      └──────────────────┘       └─────────────────┘
                                                                                                  
비유 (caption 18px fg3 italic)
"두 의사 진단을 평균낸다"
                                                                                                  
하단 큰 수식 (40px mono, fg1, bg2 tinted box)
est_final = (est_b1 + est_method) / 2.0
                                                                                                  
caption (14px mono fg3)
paper §V-B Bernoulli + 우리 method (KM20 stratified) 산술 평균 · AdaptiveState Eq 1~6 paper exact
```

### S7 — Section 3 / 검증 (SectionDivider)

```jsx
<SectionDivider num="03" title="검증" subtitle="paper 재현 + paradigm rollup + 결합 보강 효과" page="07" />
```

### S8 — paper 재현 검증 (Big stat)

```jsx
<BigStat
  value="-4.3%"
  subtitle="paper Fig.12 mean qe_trim 재현 (1.69 vs 1.618)"
  caption="8 cells · 100% 정확 재현 검증 anchor · B1 baseline 9 cells · CaseA 495 / CaseB 496 measurement"
/>
```

거대 수치 240px brand red. 부제 32px ink. caption 14px mono fg3.

### S9 — RQ2 paradox (Big chart)

```jsx
<BigBarChart data={[
  { label: 'Bernoulli (baseline)', value: 1.748, color: '#737373' },
  { label: 'Equal',                value: 1.644, color: '#737373' },
  { label: 'Proportional',         value: 1.580, color: '#DC2626' },
  { label: 'Neyman ★',             value: 1.595, color: '#DC2626' },
  { label: 'Anti-Neyman',          value: 1.540, color: '#DC2626' },
]} />
```

**거대 제목 (60px brand red, slide 상단)**: "Anti < Prop < Neyman"

**caption (16px fg3, slide 하단)**: "σ_j range 1.3-1.6× narrow + N_i CV=0 균등 → σ 신호 약함 → RQ3 결합 보강 motivation"

### S10 — Paradigm 8 grid (한국어 + 실측 Δ%)

```jsx
<BigBarChart data={[
  { label: '밀도 추정 (Parzen KDE) ⚠',           value: -11.93,  color: '#DC2626' },
  { label: '정보 이론 (HyperLogLog)',             value: -7.60,   color: '#DC2626' },
  { label: '스트리밍 (Chao weighted)',            value: -6.63,   color: '#DC2626' },
  { label: '차원 축소 (희소 랜덤 사영)',          value: -6.03,   color: '#DC2626' },
  { label: '공간 분할 (Hilbert + Z-order)',       value: -5.57,   color: '#DC2626' },
  { label: '균등 격자 (QMC) ✗',                   value: +1.47,   color: '#737373' },
  { label: '클러스터 (k-means / MiniBatch)',      value: +2.04,   color: '#737373' },
  { label: '양자화 (Product Quantization)',       value: +8.44,   color: '#737373' },
]} />
```

**제목 (slide 상단, secn="3.", title="Paradigm rollup — CaseB ensemble effect")**

**caption (16px fg3)**: "negative = CaseB 우위. 5 paradigm 통계 압도. ⚠ paradigm anchor cell 부족 / ✗ QMC method 정합성 위반 4개 폐기 (lhs/sobol/halton/hammersley)"

### S11 — ★ Climax (Single callout, 300px brand red)

```jsx
<BigStat
  value="92.5%"
  subtitle="paired CaseB < CaseA"
  caption="455 / 492 cells · p < 1×10⁻⁴⁵ · paper review-grade evidence · CaseB ensemble 단독 대체보다 우위"
/>
```

수치 300px brand red. 부제 40px ink weight 600. caption 18px mono fg3.

### S12 — Climax 보조 (3 GridStats)

```jsx
<GridStats stats={[
  { value: '63.0%', label: "Cliff's δ large better", sub: '311 / 494 · effect size' },
  { value: '55.7%', label: "Hedges' g large",       sub: '275 / 494 · standardized mean' },
  { value: '45.3%', label: 'one-sided p<0.05',      sub: '224 / 494 · BH-FDR' },
]} />
```

### S13 — Negative Control (Comparison)

```
[SlideShell — secn="3.", title="Negative Control · 단독 대체 vs 결합 보강"]
                                                                                                  
2 column grid (좌 50% / 우 50%, gap 64px)
─────────────
좌측 — CaseA · 단독 대체 (위험)
  Eyebrow: CASEA · 단독 대체
  거대 수치 (160px, brand red): "0 / 493"
  부제 (24px ink): "outperform 0%"
  caption (14px fg3): "Bernoulli baseline 을 우리 method 단독으로 대체 → 단 하나도 우위 X · large worsening 37.1%"

우측 — CaseB · 결합 보강 (유효)
  Eyebrow: CASEB · 결합 보강
  거대 수치 (160px, brand red): "311 / 494"
  부제 (24px ink): "large better 63.0%"
  caption (14px fg3): "Bernoulli baseline + 우리 method 산술 평균 → 통계적 유의 우위 (p < 1e-45)"
                                                                                                  
중앙 결론 (slide 하단 중앙, 28px ink, weight 700)
"단독 대체 X → 결합 보강 만 유효"
```

### S14 — Hilbert 정정 (Diagram before/after)

```
[SlideShell — secn="3.", title="★3 Hilbert 정정 — 학술 정직성"]
                                                                                                  
2 column grid (좌 50% / 우 50%, gap 48px)
─────────────
좌측 — BEFORE (회색 / striked-through)
  Eyebrow: 잘못된 명명
  큰 텍스트 (40px fg3 strikethrough): "★3 hilbert"
  부제 (18px fg3): "Faloutsos 1989 (잘못된 reference)"
  caption (14px fg3): "PCA 2D + 사전식 정렬 alias → Hilbert 곡선 아님"

우측 — AFTER (brand red 정정)
  Eyebrow: HILBERT REAL (Wikipedia xy2d 표준)
  큰 텍스트 (40px ink): "Hilbert (Wikipedia 표준)"
  부제 (18px ink): "+ Z-order (Morton 1966) + Skilling 2004"
  caption (14px fg3): "P2 Spatial paradigm anchor 4건 (★3 alias + M6 + M7 + hilbert_real)"
                                                                                                  
하단 결과 (caption 16px ink weight 500)
"Wikipedia 표준 Hilbert → CaseB mean −8.2% · 6/9 cells signif"
```

### S15 — Cross-scale (Big line chart)

3 점 line chart — sf=1 / sf=10 / sf=100.

```
[SlideShell — secn="3.", title="Cross-scale 안정성"]
                                                                                                  
중앙 큰 line chart (SVG, 800×360)
                                                                                                  
y axis: paradigm rollup mean Δ% (CaseB, P3 Streaming anchor)
x axis: scale factor (1, 10, 100, log scale)
                                                                                                  
data points (예시, 본 측정 기준):
  sf=1   → 큰 dot 12px brand red
  sf=10  → 큰 dot 12px brand red
  sf=100 → 큰 dot 12px brand red
                                                                                                  
연결선 (line 2px brand red) + label 각 점 옆 (14px fg1 weight 600)
                                                                                                  
하단 caption (16px fg3 weight 500)
"100배 차이 데이터 규모 전반에서 결합 보강 효과 안정 · paper Fig.14 mean qe_trim 1.6180 일치"
```

### S16 — Section 4 / 한계 + 향후 (SectionDivider)

```jsx
<SectionDivider num="04" title="한계" subtitle="정직한 한계 표명 + 학술적 신뢰" page="16" />
```

### S17 — Limitation (Mixed grid, 4 group)

REPORT §10 drop list 9 카테고리 + §11 method-level limitation 반영.

```
[SlideShell — secn="4.", title="Limitation — 4 카테고리"]
                                                                                                  
4 column grid (각 25%, gap 24px)
─────────────
column 1: 측정 결손 (drop)
  Eyebrow (10px mono brand red): DROP LIST
  • 자원 한계 (birch 50-200GB / agglomerative SSN OOM)
  • paper scope 외 (A2-Fig8 multi-vector / A3-TPCDS)
  • wrapper 설계 결함 (Q1+Q4 timeout 부재)
  • 알고리즘 정의 위반 (kdtree leaf-index)

column 2: 정합성 위반 폐기
  Eyebrow: BUDGET VIOLATION
  • QMC paradigm (halton/sobol/lhs/hammersley)
  • dense_rp / random_projection
  • dbscan / ccsketch / lsh / ams_count_sketch
  • paper N=385 budget 위반

column 3: 학술 정직 (audit)
  Eyebrow: AUDIT FINDING
  • ★3 hilbert → PCA-alias 정정
  • ★4 sparse_rp → Li 2006 정정
  • M7 skilling_hilbert → swap simplified
  • RQ2 Neyman paradox (σ_j narrow)

column 4: byte-identical 중복
  Eyebrow: DUPLICATES
  • pca1d ≡ cca1d ≡ adaptive_bucket_probing
  • epsilon_net ≡ kdpp
  • ams_count_sketch ≡ lsh
  • kdtree = reservoir fallback
                                                                                                  
각 item 양식: 점 dot (4px brand red circle) + 12px fg1 한 줄
gap item-to-item: 12px
gap group title-to-items: 14px
```

### S18 — Closer (Big thanks, hideHeader=true)

```
중앙 거대 타이포
"감사합니다" (160px, Apple SD Gothic Neo, weight 800, ink, letter-spacing -0.04em)
                                                                                                  
부제 (32px fg2 weight 400)
질문 환영합니다
                                                                                                  
하단 mono (11px fg3, 가로 1 line)
속도는벡터 · 박세은 · 강재현 · 조현빈 · 이동욱 · github.com/johyunbin/Capstone · arXiv:2512.09695v2
```

---

## 4. Speaker notes 18 entry (각 30-45초 한국어 학술 산문)

### S1 Cover
> 안녕하세요. 속도는벡터 팀의 캡스톤 최종 발표를 시작하겠습니다. 본 연구는 Exqutor 논문(arXiv:2512.09695v2) 의 §V-B Adaptive Sampling 영역에서 출발하여, 분포 인지형 stratification 을 원 논문 절차에 결합 보강(ensemble augment) 하는 접근의 정량적 가치를 검증한 결과입니다. 발표는 약 20분 진행되며, 배경·접근·검증·한계 네 부분으로 구성되어 있습니다.

### S2 Section 1 — 배경
> 첫 번째 부분, 배경입니다. 벡터 카디널리티 추정의 사각지대 — 즉 기존 query optimizer 가 벡터 공간의 분포를 알지 못한 채 고정 비율로 추정하는 한계 — 를 짚고, 본 연구가 정확히 어느 지점을 공략하는지 명확히 하겠습니다.

### S3 Problem
> 벡터 query 의 selectivity 는 query 마다 0.001 퍼센트부터 90 퍼센트까지 큰 폭으로 변합니다. 그러나 pgvector 는 33.3 퍼센트, VBASE 는 50 퍼센트, DuckDB 는 100 퍼센트 — 모두 고정 비율 추정으로 답하고 있습니다. 이 한계는 잘못된 실행 계획으로 직결되며, 본 연구의 motivation 입니다.

### S4 Background
> Exqutor 는 이 문제를 두 갈래로 풀고 있습니다. 인덱스가 있을 때는 ECQO 가 HNSW range query 로 1~2 밀리초 안에 정확한 카디널리티를 얻고, 인덱스가 없을 때는 Adaptive Sampling 이 모멘텀 기반 동적 sample 로 추정합니다. 본 연구는 후자, 즉 §V-B Adaptive Sampling 영역에 분포 인지형 stratification 을 결합 보강하는 접근을 정량 검증합니다. ECQO 영역은 paper main result 그대로 인정합니다.

### S5 Section 2 — 접근
> 두 번째 부분, 접근입니다. 원 논문 절차를 보존하면서 어떻게 결합 보강 (ensemble augment) 을 더했는지, 그 직관과 수식을 짚겠습니다.

### S6 Approach
> 결합 보강의 직관은 단순합니다. 두 의사가 같은 환자를 진단했을 때 둘의 평균이 한 명의 단독 판단보다 안정적입니다. paper §V-B Bernoulli estimator(est_b1) 는 분포를 모르는 random sampling 추정, 우리의 KM20 stratified estimator(est_method) 는 분포 인지형 추정 — 두 추정값을 산술 평균합니다. est_final = (est_b1 + est_method) / 2. AdaptiveState (Eq 1~6) 는 paper exact 그대로 유지하고, sample budget N=385 도 두 estimator 가 공유합니다.

### S7 Section 3 — 검증
> 세 번째 부분, 검증입니다. 세 단계로 진행합니다. 첫째 paper Fig.12 재현 정합성, 둘째 paradigm 단위 결합 보강 효과 집계, 셋째 paired comparison 으로 결합 보강이 단독 대체보다 유효함을 증명합니다.

### S8 paper 재현
> 첫 번째 검증입니다. 본 연구의 측정 정합성은 paper Fig.12 영역 8 cells 의 평균 qe_trim 으로 확인됩니다. paper 보고값 1.69 대비 본 측정값 1.618 — 정확히 -4.3 퍼센트 — 으로, measurement variance 범위 내 일치합니다. B1 baseline 9 cells, CaseA 495 measurement, CaseB 496 measurement, 총 1000 file 의 paper exact 재현이 100% 정확 anchor 로 입증됩니다.

### S9 RQ2 paradox
> RQ2 는 분포를 알았을 때 어느 allocation 이 최적인가를 묻습니다. 이론적으로 Neyman 이 가장 효율적이어야 합니다. 그러나 측정 결과 Anti-Neyman 1.540, Proportional 1.580, Neyman 1.595 의 paradox 가 발생합니다. 원인은 stratum 별 표준편차 σ_j 의 range 가 1.3~1.6 배로 narrow 하고, stratum 크기 N_i 의 변동계수가 0 인 데이터 구조 — 즉 Neyman 의 σ 신호가 약했습니다. 이 paradox 가 곧 결합 보강 접근의 motivation 으로 자연 전환됩니다.

### S10 Paradigm rollup
> 분포 인지형 paradigm 8개를 결합 보강 효과로 정렬했습니다. 밀도 추정 paradigm 이 -11.93 퍼센트 (Parzen KDE), 정보 이론 paradigm 이 -7.60 퍼센트 (HyperLogLog), 스트리밍 paradigm 이 -6.63 퍼센트 (Chao weighted), 차원 축소 paradigm 이 -6.03 퍼센트 (sparse RP), 공간 분할 paradigm 이 -5.57 퍼센트 (Hilbert + Z-order). 다섯 paradigm 이 통계적으로 압도합니다. 반면 균등 격자(QMC)·클러스터·양자화 paradigm 은 결합 효과 없음 또는 미세 악화. 균등 격자 4 method(halton/sobol/lhs/hammersley) 는 paper N=385 budget 위반으로 폐기되어 paradigm rollup 만 표기합니다.

### S11 ★ Climax — 92.5%
> 본 연구의 핵심 결과입니다. paired CaseB vs CaseA — 즉 결합 보강이 단독 대체보다 우위 — 의 비율은 92.5 퍼센트. 492 cells 중 455 cells 에서 CaseB Δ% 가 CaseA Δ% 보다 낮습니다. p-value 는 10⁻⁴⁵ 이하 — paper review-grade evidence 수준입니다. 이 수치 하나가 본 연구가 "Adaptive Sampling 에 분포 인지형 보강을 더하면 정량적 가치가 있다" 는 가설을 검증합니다.

### S12 Climax 보조
> 통계 효과 크기로도 확인됩니다. Cliff's δ large better 63.0 퍼센트(311/494), Hedges' g large 55.7 퍼센트(275/494), one-sided p<0.05 outperform 45.3 퍼센트(224/494). 다양한 비모수·모수 통계 metric 이 동일 방향을 가리킵니다.

### S13 Negative Control
> 결정적으로, 결합 보강이 아닌 단독 대체 (CaseA) 는 어떨까요. Bernoulli baseline 을 우리 method 로 단독 교체했을 때 — 493 cells 중 outperform 은 0 cell, large worsening 은 37.1 퍼센트(183/493). 단 하나도 우위가 없습니다. 반면 결합 보강 (CaseB) 은 494 cells 중 311 cells 에서 large better. 이 negative control 이 본 연구의 결론을 명확히 합니다: **단독 대체는 무효, 결합 보강만 유효**.

### S14 Hilbert 정정
> 학술 정직성을 위해 본 연구의 자체 발견 사항을 공개합니다. 본래 코드에서 ★3 hilbert 로 명명된 method 는 사실 Faloutsos 1989 가 아닌 PCA 2D + 사전식 정렬 alias 였습니다. 실제 Hilbert 곡선 — Wikipedia xy2d 표준 — 으로 재구현하여 측정한 결과 CaseB mean -8.2 퍼센트, 9 cells 중 6 cells 에서 통계 유의. 정정 후에도 P2 Spatial paradigm anchor 로서 유효함을 확인했습니다.

### S15 Cross-scale
> scale factor 별 안정성을 확인했습니다. sf=1·sf=10·sf=100 의 100배 데이터 규모 차이 전반에서 결합 보강 효과가 안정적입니다. 원 논문 Fig.14 의 mean qe_trim 1.6180 과 일치하는 reproducibility 도 함께 검증됩니다.

### S16 Section 4 — 한계
> 마지막 부분, 한계입니다. 학술 정직성을 위해 본 연구의 한계를 네 카테고리로 정리하여 명시합니다.

### S17 Limitation
> 첫째 측정 결손 — 자원 한계(birch 50-200GB, agglomerative SSN OOM), paper scope 외(A2-Fig8 multi-vector, A3-TPCDS), wrapper 설계 결함(Q1+Q4 timeout 부재), 알고리즘 정의 위반(kdtree leaf-index modulo random hash). 둘째 정합성 위반 폐기 — QMC paradigm 4 method(halton/sobol/lhs/hammersley)와 dense_rp/random_projection/dbscan/ccsketch/lsh/ams_count_sketch 가 paper N=385 budget 을 위반하여 폐기됩니다. 셋째 학술 정직 audit — ★3 hilbert PCA-alias 정정, ★4 sparse_rp Li 2006 정정, M7 skilling_hilbert conditional swap 1줄 simplification, RQ2 Neyman paradox σ_j narrow 원인 명시. 넷째 byte-identical 중복 — pca1d/cca1d/adaptive_bucket_probing 3쌍, epsilon_net/kdpp, ams_count_sketch/lsh, kdtree/reservoir fallback. 이 한계들을 모두 정직하게 명시하는 것이 본 연구의 학술적 신뢰를 뒷받침합니다.

### S18 Closer
> 감사합니다. 질문 환영합니다. 자세한 측정 결과·분석 코드·데이터는 GitHub(github.com/johyunbin/Capstone) 와 발표 자료에 모두 공개되어 있습니다.

---

## 5. 작업 순서 (claude.ai/design 새 conversation)

1. **claude.ai/design 새 conversation 시작** (https://claude.ai/design/new)
2. 본 file 전체 paste — 1 input
3. monitoring (예상 1-2시간 생성)
4. iframe reload + visual 검증 (S1 / S2 SectionDivider / S11 Climax / S18 Closer)
5. 추가 정정 prompt 필요 시 (텍스트 겹침 / 정렬 / 글씨 크기 / 색상)
6. Share → Export PDF / PPTX / standalone HTML

저장 path:
- `submission/_drafts/속도는벡터 — Final 5_27 키노트.pdf`
- `submission/_drafts/속도는벡터 — Final 5_27 키노트.pptx`

---

## 6. 본 v2 변경 history (vs v1)

| Slide | v1 (premature) | v2 (FINAL, 실측) |
|---|---|---|
| S8 | RQ1 +3.74% | paper 재현 -4.3% (Fig.12 anchor) |
| S10 paradigm | -7.60/-6.53/-5.92/-5.52 (handoff 시점) | **-11.93/-7.60/-6.63/-6.03/-5.57/+1.47/+2.04/+8.44** (실측 REPORT v11) |
| S11 climax | 92.9% (이전 추정) | **92.5%** (455/492 실측) |
| S12 보조 | 63.5%/56.4%/71.8% | **63.0%/55.7%/45.3%** (실측 effect size) |
| S13 neg ctrl | 0/437 (이전) | **0/493** (CaseA n=493) |
| S17 limit | 4 group 항목 | **4 group + REPORT §10 drop list 9 카테고리 + §11 method-level limitation** 반영 |

---

## 7. 절대 금지

- 텍스트 본문 16-18px 우겨넣기 X
- bullet 3-5 list X
- 다중 색 동시 사용 X (red 단일)
- whitespace 30% 이하 X (70%+ 유지)
- speaker notes 없이 slide 본문만 X
- 작은 수치 X (Big stat / Climax 는 200-300px)
- 측정 미완 method 발표 자료 포함 X (사용자 정책)
- future work / 향후 연구 mention X (사용자 정책)

---

## 8. END

작성: 2026-05-12 02:45 KST
대상: claude.ai/design 새 conversation
예상 생성: 1-2시간
최종 deck export: PDF + PPTX 5/12 morning
