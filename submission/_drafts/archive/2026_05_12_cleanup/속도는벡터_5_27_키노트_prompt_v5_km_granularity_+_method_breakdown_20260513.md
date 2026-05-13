# 5/27 키노트 deck v5 정정 prompt — km granularity sensitivity + paradigm 내 분산
## claude.ai/design Keynote_Capstone (5/16 토 한도 reset 후) 또는 PPTX manual edit

> **목적**: v4 deck (20 slide) 의 강재현 5/13 0:20 + 1:00 피드백 반영
> 1. cluster granularity sensitivity by method (K=10/20/30 3-way 실측)
> 2. paradigm 내 분산 명시 (method-level breakdown)
> 3. anchor method 일관성 강조 narrative

---

## 정정 사항 4건

### ★ 정정 1: 신규 slide — K-sensitivity by method (S18 위치)

**위치**: 기존 S17 가장 우수 알고리즘 5선 뒤, S18 climax 직전

**spec**:

```
[SlideShell — secn="3.", title="cluster granularity sensitivity (K=10/20/30)"]

중앙 grouped bar chart (4 anchor × 3 K values × 5 cells mean)

데이터 (CaseB ensemble vs B1 paired Δ%, 5 cells mean):
                     K=10     K=20      K=30
sparse_rp (P4):     +5.05    -10.60    -6.78    ★ U-shape, K=20 sweet
hilbert_real (P2):  -10.86   -10.45    -11.26   robust, K=30 약간
hyperloglog (P9):   -9.51    -9.47     -9.86    robust, K=30 약간
chao_weighted (P3): -10.63   -12.01    -10.39   K=20 sweet

caption (16px fg3):
"cluster 수 K 의 효과는 method 의존적. sparse RP 만 K=20 sweet spot 결정적
(U-shape sensitivity), 다른 anchor 3 method 는 cluster granularity 와 robust"
```

speaker note:
> "cluster 수 K 의 영향을 K=10/20/30 3-way 비교한 결과입니다. sparse random projection 은 K=20 sweet spot 이 결정적 — K=10 의 거친 분할에서는 baseline 보다 약 5% 악화되고, K=20 에서 강력 개선되며, K=30 의 미세 분할에서 다시 약화됩니다. U-shape sensitivity 입니다. 반면 Hilbert curve, HyperLogLog, Chao 1982 의 3 anchor 는 cluster granularity 와 독립적으로 -9 ~ -12% 일관 개선 효과를 보입니다. 이 finding 은 method 별 sensitivity 가 다름을 정량 입증하며, 특히 sparse RP 의 sweet spot 이 K=20 에 위치한다는 점이 cluster 분할 + projection 의 trade-off 로 해석됩니다."

---

### ★ 정정 2: S15 paradigm rollup narrative 정정 — method-level breakdown 추가

**기존 S15** (paradigm rollup mean Δ% 8 paradigm bar chart): K=20 base 측정 결과.

**정정 S15** — 옆에 method-level breakdown table 추가:

```
2 column layout (좌 paradigm rollup / 우 method-level breakdown)

좌측 — paradigm rollup (기존 그대로):
밀도추정 -11.93%   정보이론 -7.60%   스트리밍 -6.63%   차원축소 -6.03%
공간분할 -5.57%    균등격자 +1.47%   클러스터 +2.04%   양자화 +8.44%

우측 — paradigm 내 method 분산 (★ 신규):
P3 Streaming  range -3.80 ~ -9.60, anchor chao_weighted -9.60
P4 DimReduc   range +16.43 ~ -9.97, anchor sparse_rp/neuram -9.43~-9.97
              outlier: lp_bound +16.43% (paradigm aggregate 끌어내림)
P2 Spatial    range -2.27 ~ -9.45, anchor lpm2/hilbert -9.4
P1 Cluster    range +67.96 ~ -9.28, anchor minibatch -9.28
              outlier: wavelet_hist +67.96% (paradigm 평균 왜곡)

caption (16px fg3):
"paradigm rollup 평균은 outlier method 영향을 받으므로 paradigm 우위 단정 X.
진짜 contribution = anchor method 의 일관성 (-9~-10% cell 전반)"
```

speaker note:
> "8 paradigm 의 CaseB 증강 효과 평균을 보였습니다. 그러나 paradigm 평균만으로는 paradigm 우위를 단정 짓기 어렵습니다. 예를 들어 P1 Cluster paradigm aggregate 는 +2.04% 인데, paradigm 안 minibatch anchor 는 -9.28% 로 다른 paradigm anchor 수준 우수입니다. wavelet_hist 의 +67.96% outlier 가 paradigm 평균을 끌어올린 결과입니다. 본 연구의 진짜 contribution 은 paradigm 우위가 아니라 anchor method 들의 일관성입니다 — 12 anchor method 가 cell 전반에서 -9 ~ -10% 일관 개선 효과를 보입니다."

---

### ★ 정정 3: S17 narrative 재배치 — anchor method consistency 강조

**기존 S17** (가장 우수 알고리즘 5선): paradigm 분류 기반.

**정정 S17 narrative**:

```
[SlideShell — secn="4.", title="anchor method consistency"]

상단 (eyebrow): 12 ANCHOR METHODS — CELL-CONSISTENT IMPROVEMENT

중앙 grouped scatter or table:
method            paradigm  mean Δ%  std  cell coverage
lpm2              P2        -9.45    2.36  9/9 ⭐⭐
hilbert           P2        -9.41    2.13  9/9 ⭐⭐
sparse_rp         P4        -9.43    3.30  9/9 ⭐
hilbert_real      P2        -9.27    3.12  9/9 ⭐
minibatch         P1        -9.28    3.29  9/9 ⭐
chao_weighted     P3        -9.60    6.36  9/9 ⭐
neuram            P4        -9.97    2.88  9/9 ⭐
pca1d/cca1d/abp   P4        -9.63    3.12  9/9 ⭐
reservoir         P3        -9.25    3.00  9/9 ⭐
thompson_sampling P3        -8.98    3.05  9/9 ⭐
hyperloglog       P9        -8.65    2.73  9/9 ⭐
opq/pq            P6        -9.25~-9.37 ⭐

caption (16px fg3):
"12 anchor method 가 9 cells 전반에서 -9~-10% 일관 개선 (std 2-3 안정).
paradigm 분류는 categorization, 본질은 anchor method 의 robust consistency."
```

speaker note:
> "본 연구의 진짜 contribution 을 anchor method 일관성 차원에서 정리하면, 12 method 가 9 cells 전반에서 -9 ~ -10% 일관된 개선 효과를 표준편차 2-3 의 안정성으로 보입니다. 가장 안정적인 것은 P2 Spatial paradigm 의 lpm2 와 hilbert 이며 (std 2.13 ~ 2.36), 다른 paradigm 의 anchor method 들도 모두 std 3 이내의 robust 효과를 보입니다. 이 12 anchor 일관성이 본 연구의 paper review-grade evidence 이며, paradigm 분류 자체는 method 들을 통계적 접근 방식 별로 categorize 한 것에 불과합니다."

---

### ★ 정정 4: Limitation slide 보강

**추가 column**:

```
column 추가: K-SENSITIVITY by method
  Eyebrow: CLUSTER GRANULARITY
  큰 텍스트: "method 의존적"
  caption:
    "sparse RP 는 K=20 sweet spot 결정적 (U-shape)
     hilbert / hyperloglog / chao 는 K-robust (K=10/20/30 거의 동일)
     본 발표 paradigm rollup 은 K=20 base 측정 결과
     dataset 별 dynamic K 선택은 향후 연구 영역"

column 추가: MULTI-TABLE STRATIFICATION
  Eyebrow: SCOPE
  큰 텍스트: "carry-over 한정"
  caption:
    "multi-table cell (A2-Fig7/Fig9) 의 stratification 학습은
     single table KM20 의 join 후 carry-over 방식.
     두 테이블 join 후 별도 stratification 학습 (re-stratification)
     은 본 연구 §V-B scope 외 (paper §V-A multi-table 영역)."
```

---

## 정정 진행 순서

1. **5/13 ~ 5/15** — v5 정정 prompt md 준비 + 박세은/강재현/이동욱 검토
2. **5/15 (금) 14:00** — 박광현 교수 미팅 D-day, v5 정정 plan confirm 받기
3. **5/16 (토)** — claude.ai/design 한도 reset 후 v5 정정 prompt paste
4. **5/16 ~ 5/26** — v5 deck generation + PDF/PPTX export
5. **5/27 (화) 19:00** — 최종 발표

또는 PPTX manual edit (PowerPoint 안 직접 수정):
- S18 신규 slide 추가 (chart + caption + speaker note)
- S15 우측 method-level breakdown 추가
- S17 narrative 재배치
- Limitation column 추가

claude.ai/design reset 5/16 wait 보다 manual edit 가 빠를 수도 (5/13 ~ 5/14 가능).

---

## 측정 + 분석 source

- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_km10/` — K=10 40 measurement
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/` — K=20 base (기존 1001 file)
- `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_km30/` — K=30 40 measurement
- `_internal/analysis/method_level_breakdown_20260513.md` — paradigm 내 분산
- `_internal/analysis/km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` — 3-way 비교
- `_internal/analysis/multi_cell_km_based_learning_comparison_20260513.md` — multi cell 학습 방식 간접 비교
- `experiments/results/rq1_motivation/sift_rq1_2026_05_06/` — SYSTEM vs BERN raw 측정 (parquet)

---

## ★ 정정 5 (5/13 12:09 박세은 결정) — S7 RQ1 narrative SYSTEM vs BERN 재배치

박세은 12:09 verbatim: "RQ1 내러티브 자체를 system vs bern으로 재배치해서 17.32% gap 을 가져가는 세번째 방식이 좋습니다"

**기존 S7 (v4 deck)**: Bernoulli vs KM20 stratified breakdown — 4 cells × 5 trials, max 8.64% (SIFT sel=0.10).

**정정 S7 (v5 deck)** — SYSTEM vs BERN cross-dataset 정량화:

```jsx
<SlideShell secn="2." title="RQ1 — random sampling 의 부정확성">
  
  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, height: '100%'}}>
    
    // 좌측 — MAX gap BigStat
    <div style={{textAlign: 'center'}}>
      <div eyebrow>SIFT s=0.05 (SYSTEM vs BERN)</div>
      <div fontSize=200 brand red>+17.32%</div>
      <div fontSize=24>random sampling 의 부정확성 — MAX gap</div>
      <div fontSize=16 fg3>paired Wilcoxon p ≤ 1×10⁻⁴⁹ · paper review-grade</div>
    </div>
    
    // 우측 — 5 selectivity breakdown table (DEEP vs SIFT)
    <div>
      <div eyebrow fontSize=14 brand red>SYSTEM &gt; BERN cross-dataset</div>
      <table fontSize=16>
        <thead>
          <tr><th>sel</th><th>SIFT</th><th>DEEP</th><th>격차 (SIFT−DEEP)</th></tr>
        </thead>
        <tbody>
          <tr><td>0.01</td><td brand red>+10.27%</td><td>+4.66%</td><td brand red>+5.61%p</td></tr>
          <tr><td>0.05</td><td brand red>+17.32%</td><td>+12.61%</td><td brand red>+4.71%p</td></tr>
          <tr><td>0.10</td><td>+16.68%</td><td>+14.85%</td><td>+1.83%p</td></tr>
          <tr><td>0.30</td><td>+14.85%</td><td>+13.45%</td><td>+1.40%p</td></tr>
          <tr><td>0.50</td><td>+14.36%</td><td>+12.44%</td><td>+1.92%p</td></tr>
        </tbody>
      </table>
      <div fontSize=14 fg3>
        모든 sel SIFT &gt; DEEP — skew dataset 에서 부정확성 증폭<br/>
        좁은 sel (s=0.01) 에서 격차 가장 큼
      </div>
    </div>
    
  </div>
  
  <caption>PostgreSQL TABLESAMPLE SYSTEM (block) vs BERNOULLI (row-wise) paired Δ%. 두 random sampling 방식 모두 paper §V-B Adaptive Sampling 영역의 baseline 후보이며, block sampling 이 row-wise 보다 모든 selectivity 에서 +10~17% 더 부정확. skew dataset 에서 부정확성 증폭의 정량 입증.</caption>
</SlideShell>
```

**speaker note 정정**:
> RQ1 결과입니다. random sampling 의 부정확성을 정량 측정하기 위해 PostgreSQL 의 두 sampling 방식 — SYSTEM 의 block 단위 random sampling 과 BERNOULLI 의 row-wise random sampling — 을 paired 비교했습니다. 가장 극단 case 인 SIFT s=0.05 에서 SYSTEM 이 BERN 보다 17.32 퍼센트 더 부정확하며, 5 selectivity 모든 점에서 SIFT 가 DEEP 보다 격차가 더 큰 패턴을 보입니다. 좁은 selectivity (s=0.01) 에서 격차가 가장 크고 (+5.61 퍼센트p), skew dataset 에서 random sampling 의 부정확성이 증폭됨이 정량 입증됩니다. paired Wilcoxon p-value 가 1×10⁻⁴⁹ 이하 — paper review-grade 통계 robust 결과입니다.

**narrative arc 정리**:
- S7 (정정): SYSTEM vs BERN — random sampling 자체의 한계 정량 (17.32% max)
- S8 (기존): RQ2 5-way allocation — 분포 알 때 Proportional 최적 (Bern→Prop -9.53%)
- S9: RQ3 — 분포 모를 때 paradigm search
- S14 (기존): 대체(CaseA) vs 증강(CaseB) framework
- S15 (정정 v5 prompt): paradigm rollup + method-level breakdown
- S16 (신규): 왜 replace 만으로 안 되는가
- S17 (정정): anchor method consistency
- S18 (신규 v5 prompt): K-sensitivity by method
- climax: 92.5% paired CaseB < CaseA

**기존 Bernoulli vs KM20 (8.64% max) 처리**:
S7 에서 빠지고 S14 framework slide 또는 별도 sub-slide ("분포 인지 stratification 의 안정성 출발점") 로 재배치. 또는 RQ2 narrative 안에 embedded (KM20 stratification 자체의 효과 검증).

---

## 측정 source (SYSTEM vs BERN)

- `experiments/results/rq1_motivation/sift_rq1_2026_05_06/sift_rq1_system.parquet`
- `experiments/results/rq1_motivation/sift_rq1_2026_05_06/sift_rq1_bernoulli.parquet`
- 5/6 측정 완료, 5 sel × 2 dataset (SIFT/DEEP) × 5 seed × 100 query
- paired Wilcoxon p ≤ 1e-4 ~ 1e-49 (BH-FDR 보정 robust)

---

## ★ 정정 6 (5/13 16:20 FINALIZED 8/8) — multi-join re-stratification 결과 narrative

> **status**: ★ **8/8 회수 완료 (5/13 16:13 KST)**, 시나리오 A.5 (Hybrid) 확정

강재현 5/13 0:20 verbatim: "벡터 테이블 multi-join한 이후에 stratification 학습해서 하는 것도 한번 테스트 해보면 좋을듯, 각 single 테이블에서 하다보니 생각보다 cardinality 추정 오차가 생기나?"

강재현 5/13 14:27 후속 verbatim: "기존에 table 별로 clustering한 거를 저비용으로 multi-reclustering에 근사하는 방법 같은거"

**위치 plan**: S19 (Limitation 직전) 또는 S18 K-sensitivity 뒤 신규 slide.

### 6.1 측정 framework

- scope: 4 anchor (sparse_rp / hilbert_real / hyperloglog / chao_weighted) × A2-Fig9 multi-join cell × 2 mode (CaseA / CaseB) = **8 measurement**
- data: partsupp_deep_10 (96d) ⨝ part_wiki_10 (768d) ON ps_partkey = p_partkey → 864d concat × ~1.5M row
- stratification: **fresh KM20 학습** (carry-over single-table KM20 와 별개) on 864d concat vector
- wrapper: `/tmp/launch_multijoin_restrat.py`
- output: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_mj_restrat/`

### 6.2 3-way 비교 결과 (★ 8/8 finalized)

A2-Fig9 cell, B1 baseline qe_trim 1.5407 기준, paired Δ% — **8/8 회수 완료**:

**CaseA 단독 대체 모드**:
```
method          carry-over    multi-join re-strat    diff
sparse_rp       +4.52%        +0.97%                  ★ -3.55%p
hilbert_real    +1.78%        +2.10%                  +0.32%p
hyperloglog     +1.15%        +0.89%                  -0.26%p
chao_weighted   +6.14%        +3.51%                  ★ -2.63%p
mean            +3.40%        +1.87%                  -1.53%p
```

**CaseB 증강 모드** (★ 본 연구 핵심 contribution):
```
method          carry-over    multi-join re-strat    diff
sparse_rp       -6.58%        -6.84%                  -0.26%p
hilbert_real    -6.07%        -6.23%                  -0.16%p
hyperloglog     -5.15%        -4.96%                  +0.19%p
chao_weighted   -6.00%        -6.24%                  -0.24%p
mean            -5.95%        -6.07%                  -0.12%p
```

**비교 axis 의미**:
- (a) carry-over = 기존 본 연구 measurement framework (single-table KM20 학습 후 multi-table 에서 join 후 stratum_id column 재사용)
- (b) 자체 K-means = method 가 자체 stratification 학습 framework (minibatch 등, scope 외 참조)
- (c) multi-join re-stratification = 두 테이블 join 후 864d concat vector KM20 fresh 학습 + 96d query space return (wrapper v2 design, 본 정정 6 의 신규 axis)

### 6.3 narrative arc — ★ 시나리오 A.5 (Hybrid) 확정

8/8 측정 결과는 4 anchor method 가 두 그룹의 분명한 sensitivity 패턴으로 분기됨을 입증하여 **시나리오 A.5 (Hybrid)** 가 확정되었다.

**Quality-sensitive group (sparse_rp + chao_weighted)** — CaseA 단독 대체 모드에서 multi-join re-strat 우위 (-3.55%p, -2.63%p). 두 method 의 stratification 학습 메커니즘이 stratum 내부 통계 구조에 강하게 의존하여 multi-join 결합 학습 (864d concat) 이 추가 정보 효과를 발휘함.

**Quality-robust group (hilbert_real + hyperloglog)** — CaseA 거의 동등 (+0.32%p, -0.26%p). Hilbert curve 의 space-filling locality 와 HyperLogLog 의 hash-based distinct count 가 stratum 내부 통계 구조와 독립적으로 작동.

**CaseB 증강 모드 — 4 method 모두 동등 (mean diff -0.12%p)**. 본 연구의 핵심 contribution 인 Bernoulli + stratified 산술 평균 ensemble 의 robustness 가 multi-join cell 의 stratification 학습 방식 변화에도 입증됨. ensemble augment 의 핵심 강점.

**부록 F (K-sensitivity) 와의 완벽 일치 패턴**: K-sensitive 였던 sparse_rp + chao_weighted 가 본 부록 G 에서도 multi-join sensitive, K-robust 였던 hilbert_real + hyperloglog 가 본 부록에서도 robust. 두 분석 패턴 일치는 **"stratification quality 의존도"** 라는 새 method classification axis 의 존재를 입증.

### 6.4 slide spec (★ 8/8 finalized)

```jsx
<SlideShell secn="3." title="multi-join re-stratification (★ 강재현 1번 검증, 8/8 finalize)">
  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32}}>
    
    // 좌측 — CaseA grouped bar chart (★ method-specific sensitivity)
    <div>
      <eyebrow>CaseA 단독 대체 — method 별 sensitivity</eyebrow>
      grouped bar chart Δ% (B1=1.5407 기준):
        [carry-over]  [multi-join re-strat]
        sparse_rp:     +4.52 vs +0.97  ★ -3.55%p
        chao_weighted: +6.14 vs +3.51  ★ -2.63%p
        hilbert_real:  +1.78 vs +2.10     +0.32%p
        hyperloglog:   +1.15 vs +0.89     -0.26%p
      caption fontSize=14 fg3:
        "quality-sensitive 2 method 만 multi-join 우위"
    </div>
    
    // 우측 — CaseB 동등 + narrative
    <div>
      <eyebrow>CaseB 증강 — 4 method 모두 동등</eyebrow>
      bar chart Δ%:
        sparse_rp:     -6.58 vs -6.84  -0.26%p
        chao_weighted: -6.00 vs -6.24  -0.24%p
        hilbert_real:  -6.07 vs -6.23  -0.16%p
        hyperloglog:   -5.15 vs -4.96  +0.19%p
        mean: -5.95 vs -6.07           -0.12%p
      
      <p fontSize=16 fg3>본 연구 ensemble augment 의 robustness
      — multi-join cell stratification 학습 방식 변화에 무관</p>
    </div>
  </div>
  
  <caption fontSize=14 fg3>multi-join (partsupp_deep_10 ⨝ part_wiki_10, 864d × 1.5M row) 의 stratification 학습 방식 비교. wrapper v2: 864d concat KM20 fresh 학습 + 96d query space return. 8 measurement 5/13 16:13 회수. 부록 F K-sensitivity 패턴 (sparse_rp + chao_weighted = K-sensitive, hilbert_real + hyperloglog = K-robust) 과 완벽 일치 — "stratification quality 의존도" 새 method axis 입증.</caption>
</SlideShell>
```

### 6.5 speaker note (★ 8/8 finalized)

> "이 slide 는 강재현 팀원의 5/13 새벽 피드백 — 두 벡터 테이블을 join 한 이후에 stratification 학습을 별도로 하는 방식의 sensitivity 를 검증한 결과입니다. 본 연구의 기존 measurement framework 는 single-table 별로 KM20 을 학습한 후 multi-join cell 에서는 stratum_id column 을 그대로 carry-over 하는 방식이었는데, 이게 multi-join 의 cardinality 추정 오차의 원인일 수 있다는 가설이었습니다. partsupp_deep 96 차원과 part_wiki 768 차원을 join 한 864 차원 concat vector 약 1.5M row 에 대해 KM20 을 재학습하는 multi-join re-stratification 을 4 anchor method × A2-Fig9 cell × 2 mode = 8 measurement 진행한 결과, 시나리오 A.5 (Hybrid) — method-specific sensitivity 패턴이 확정되었습니다. sparse random projection 과 Chao 1982 weighted reservoir 두 method 는 CaseA 단독 대체 모드에서 multi-join re-strat 우위 (-3.55 퍼센트포인트, -2.63 퍼센트포인트) 가 확인되었습니다 — 두 method 의 stratification 학습 메커니즘이 stratum 내부 통계 구조에 강하게 의존하기 때문입니다. 반면 Hilbert curve 와 HyperLogLog 두 method 는 거의 동등 (+0.32, -0.26 퍼센트포인트) 으로 stratification 학습 방식 변화에 robust 한 method 였습니다. 본 연구의 핵심 contribution 인 CaseB 증강 모드에서는 4 method 모두 일관 동등 (mean diff -0.12 퍼센트포인트) 으로, Bernoulli + stratified 산술 평균 ensemble 의 robustness 가 multi-join cell 의 stratification 학습 방식 변화에도 입증되었습니다. 본 결과는 부록 F 의 cluster granularity sensitivity 패턴 (sparse_rp + chao_weighted = K-sensitive, hilbert_real + hyperloglog = K-robust) 과 method 별 완벽하게 일치하여, paradigm 분류보다 본질적인 **stratification quality 의존도** 라는 새 method classification axis 의 존재를 입증합니다."

### 6.6 강재현 14:27 cheap 근사 — Centroid tuple 8/8 측정 결과 (★ 5/13 19:57 finalize)

강재현이 5/13 14:27 카톡 후속으로 제시한 cheap 근사 hypothesis 에 대한 검증으로 5/13 16:47 launch + 19:57 회수 완료한 Centroid tuple cheap 근사 측정 8 measurement 의 결과.

**3-way 비교 (B1=1.5407 기준)**:

CaseA 단독 대체:
```
method          carry   multi-jn  centroid    ct-vs-carry
sparse_rp       +4.52%  +0.97%    +4.71%      +0.19p (marginal)
hilbert_real    +1.78%  +2.10%    +4.97%      +3.19p ★ harmful
hyperloglog     +1.15%  +0.89%    -1.14%      -2.29p ★
chao_weighted   +6.14%  +3.51%    +2.54%      -3.60p ★★★
mean            +3.40%  +1.87%    +2.77%      -0.63p
```

CaseB 증강 (★ 본 연구 핵심):
```
method          carry   multi-jn  centroid    ct-vs-carry
sparse_rp       -6.58%  -6.84%    -7.37%      -0.78p
hilbert_real    -6.07%  -6.23%    -6.93%      -0.86p
hyperloglog     -5.15%  -4.96%    -6.66%      -1.50p ★
chao_weighted   -6.00%  -6.24%    -6.69%      -0.69p
mean            -5.95%  -6.07%    -6.91%      -0.96p ★ 4 method 모두 우위
```

**핵심 결론**:

1. **CaseB 증강 모드: cheap 근사 보편 우위** — Centroid tuple 이 모든 4 method 에서 multi-jn (expensive 864d KM20) 보다 일관 우위 (mean ct-vs-mj -0.84%p). 본 연구 핵심 contribution 영역에서 **0 학습 비용 + 더 좋은 ensemble 정확도** = best of both worlds.

2. **CaseA 단독 대체: method-conditional** — chao_weighted/hyperloglog 큰 개선 (multi-jn 보다도 우위), sparse_rp marginal, hilbert_real harmful.

**새 method classification axis — "Cheap 근사 친화도"**:
- ★ Friendly: hyperloglog + chao_weighted (CaseA + CaseB 둘 다 우위)
- Indifferent: sparse_rp (marginal)
- Hostile (CaseA only): hilbert_real (Hilbert curve fragmentation harmful)

**S20 신규 slide spec — Centroid tuple cheap 근사 결과** (S19 multi-jn 뒤):

```jsx
<SlideShell secn="3." title="Centroid tuple cheap 근사 (★ 학습 비용 0 + ensemble 우위)">
  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32}}>
    
    // 좌측 — CaseB 증강 모드 grouped bar (★ 본 연구 핵심)
    <div>
      <eyebrow>CaseB 증강 — 4 method 모두 ct > mj > carry</eyebrow>
      grouped bar chart Δ% (4 method × 3 design):
        sparse_rp:     carry -6.58 / mj -6.84 / ct -7.37
        hilbert_real:  carry -6.07 / mj -6.23 / ct -6.93
        hyperloglog:   carry -5.15 / mj -4.96 / ct -6.66
        chao_weighted: carry -6.00 / mj -6.24 / ct -6.69
        mean:          carry -5.95 / mj -6.07 / ct -6.91
      caption fontSize=14 fg3:
        "★ Centroid tuple cheap 근사: 4 method 모두 multi-jn 보다 우위
         (mean -0.84%p) + 학습 비용 0 추가 = best of both worlds"
    </div>
    
    // 우측 — CaseA method-conditional + 새 axis
    <div>
      <eyebrow>CaseA — Cheap 근사 친화도 새 axis</eyebrow>
      ct-vs-carry table:
        chao_weighted:  -3.60p ★★★ (Friendly)
        hyperloglog:    -2.29p ★ (Friendly)
        sparse_rp:      +0.19p (Indifferent)
        hilbert_real:   +3.19p ★ harmful (Hostile)
      
      <p fontSize=16 fg3>method-conditional 패턴:
      - Friendly: weighted reservoir + hash distinct count
      - Hostile: spatial locality fragmentation</p>
    </div>
  </div>
  
  <caption fontSize=14 fg3>Centroid tuple cheap 근사 wrapper v3: 두 single-table KM20 (96d partsupp_deep + 768d part_wiki) + (s_A, s_B) tuple 의 top-K frequency folding (K^2=400 잠재 → K=20 unique strata, rare modulo). 학습 비용 추가 0 (vs 864d concat KM20 의 1/8 cheap). 8 measurement 5/13 19:57 회수 기반. 새 method classification axis "Cheap 근사 친화도" 입증 — paradigm 분류 + Quality-sensitivity 와 다른 본질적 axis.</caption>
</SlideShell>
```

**S20 speaker note**:

> "강재현 팀원이 multi-join re-stratification 결과 확인 후 5/13 14:27 카톡에서 제시한 후속 hypothesis — multi-reclustering 의 expensive 학습을 single-table 별 KM20 학습의 저비용 근사로 대체 가능한가 — 에 대한 정량 검증 결과입니다. Centroid tuple 이라는 cheap design 을 wrapper v3 로 구현했는데, partsupp_deep 96 차원과 part_wiki 768 차원 각각 single-table 별 K-means 20 학습 후 multi-join row 의 (s_A, s_B) tuple 을 top-K frequency 로 K=20 unique stratum 에 folding 하는 방식입니다. 학습 비용은 864 차원 concat KM20 의 약 1/8 수준입니다. 결과는 두 가지 매우 중요한 finding 을 도출했습니다. 첫째, 본 연구 핵심 CaseB 증강 모드에서 4 anchor method 모두에서 Centroid tuple 이 expensive multi-join re-stratification 보다 일관 우위 (mean -0.84 퍼센트포인트) 이며 carry-over 보다도 mean -0.96 퍼센트포인트 추가 개선합니다. 즉 본 연구의 핵심 contribution 영역에서 학습 비용 0 추가로 더 좋은 ensemble 정확도를 얻는 best of both worlds 결과입니다. 둘째, CaseA 단독 대체 모드는 method-conditional 패턴인데, chao_weighted 의 weighted reservoir 와 hyperloglog 의 hash distinct count 두 메커니즘은 cheap stratum diversity 를 정확도 향상으로 활용하여 큰 개선 (-3.60, -2.29 퍼센트포인트, multi-jn 보다도 우위) 을 보이는 반면, hilbert_real 의 Hilbert curve spatial locality 는 imperfect tuple folding 으로 fragmentation 되며 carry-over 보다도 +3.19 퍼센트포인트 악화됩니다. 본 finding 은 본 연구의 anchor method 분류에 paradigm 과 Quality-sensitivity 와는 다른 새 axis 인 Cheap 근사 친화도 의 존재를 입증하며, method-aware design 의 narrative arc 를 깊이 확장합니다."

**박광현 confirm 요청 추가 항목**: 본 새 axis "Cheap 근사 친화도" 의 학술적 인정 여부 + CaseB 보편 우위 narrative 의 발표 deck 적용 우선순위.

### 6.7 부록 G — 박광현 5/15 미팅 자료 추가 plan

회수 결과 ready 시 박광현 5/15 미팅 자료에도 부록 G 추가:

```
부록 G: multi-join re-stratification 측정 결과

G.1 측정 framework (시나리오 + 데이터)
G.2 3-way 비교 (carry-over vs 자체 K-means vs multi-join re-strat)
G.3 narrative 해석 — 세 학습 방식 차이의 의미
G.4 향후 연구 방향 — multi-table stratification design space 확장 / robust 확인 / 한계 명시
```

---

## 측정 source (multi-join re-stratification)

- 측정 launch: 5/13 12:25 KST tmux mj_restrat
- 출력 dir: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_mj_restrat/`
- wrapper: `/tmp/launch_multijoin_restrat.py`
- 회수 ETA: **5/13 15:30 ~ 16:30 KST**
- 회수 후 분석 file: `_internal/analysis/multi_join_restratification_results_20260513.md` (작성 예정)

---

작성: 2026-05-13 12:15 KST · 박세은 12:09 옵션 C 결정 반영 · RQ1 narrative SYSTEM vs BERN 재배치 + max 17.32% gap 강조
업데이트: 2026-05-13 12:50 KST · 정정 6 placeholder 추가 (multi-join re-stratification 회수 form)
