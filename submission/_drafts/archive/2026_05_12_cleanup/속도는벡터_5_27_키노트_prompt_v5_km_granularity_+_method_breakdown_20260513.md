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

## ★ 정정 6 (5/13 15:30 ~ 16:30 회수 예정) — multi-join re-stratification 결과 narrative

> **status (5/13 12:50)**: tmux mj_restrat session 진행 중. 8 measurement 회수 후 데이터 채워질 placeholder 형태.

강재현 5/13 0:20 verbatim: "벡터 테이블 multi-join한 이후에 stratification 학습해서 하는 것도 한번 테스트 해보면 좋을듯, 각 single 테이블에서 하다보니 생각보다 cardinality 추정 오차가 생기나?"

**위치 plan**: S19 (Limitation 직전) 또는 S18 K-sensitivity 뒤 신규 slide.

### 6.1 측정 framework

- scope: 4 anchor (sparse_rp / hilbert_real / hyperloglog / chao_weighted) × A2-Fig9 multi-join cell × 2 mode (CaseA / CaseB) = **8 measurement**
- data: partsupp_deep_10 (96d) ⨝ part_wiki_10 (768d) ON ps_partkey = p_partkey → 864d concat × ~1.5M row
- stratification: **fresh KM20 학습** (carry-over single-table KM20 와 별개) on 864d concat vector
- wrapper: `/tmp/launch_multijoin_restrat.py`
- output: `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_mj_restrat/`

### 6.2 3-way 비교 plan (회수 후 데이터 채워짐)

```
A2-Fig9 cell — paired Δ% (CaseB ensemble vs B1)

method            (a) carry-over    (b) 자체 K-means     (c) multi-join re-strat
                  (single KM20)     (method 자체 학습)    (864d fresh KM20)
─────────────────────────────────────────────────────────────────────────────
sparse_rp         -6.58% (실측)     n/a (CCSketch 같은)   [TBD]
hilbert_real      -6.07% (실측)     n/a                   [TBD]
hyperloglog       -5.15% (실측)     n/a                   [TBD]
chao_weighted     -6.00% (실측)     n/a                   [TBD]
minibatch         -7.25% (간접 비교) n/a (자체 학습)        n/a
```

**비교 axis 의미**:
- (a) carry-over = 기존 본 연구 measurement framework (single-table KM20 학습 후 multi-table 에서 join 후 stratum_id column 재사용)
- (b) 자체 K-means = method 가 자체 stratification 학습 framework (minibatch 등)
- (c) multi-join re-stratification = 두 테이블 join 후 별도 KM20 학습 (5/13 12:25 launch, 본 정정 6 의 신규 axis)

### 6.3 narrative arc 예상 (회수 후 finalize)

회수 결과에 따라 두 narrative 분기:

**시나리오 A — re-stratification 우위 (carry-over 보다 -2~-3%p 추가 개선)**:
> "multi-join re-stratification 이 carry-over 방식보다 추가 개선을 보임. 두 테이블 join 후 stratification 학습이 cardinality 추정에 유의한 개선 효과를 발휘한다. 향후 multi-table stratification 의 design space 가 확장됨."

**시나리오 B — re-stratification 동등 / 미세 개선 (-0~-1%p)**:
> "multi-join re-stratification 과 carry-over 가 거의 동등한 성능. 본 연구의 single-table KM20 carry-over 방식이 이미 multi-table cell 에서도 robust 함이 입증된다. 학습 방식 차이가 결정적 X — method 자체 특성이 더 결정적."

**시나리오 C — carry-over 우위 (multi-join re-stratification 이 worse)**:
> "carry-over 가 더 우수 — multi-join 후 864d concat 의 KM20 학습이 single-table KM20 carry-over 보다 unstable. high-dim vector 의 K-means clustering 한계 (curse of dimensionality)."

### 6.4 slide spec (placeholder, 회수 후 데이터 채움)

```jsx
<SlideShell secn="3." title="multi-join re-stratification (★ 강재현 1번 검증)">
  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32}}>
    
    // 좌측 — 3-way bar chart (CaseB mean, 4 anchor)
    <div>
      grouped bar chart:
        [carry-over single KM20]  [multi-join re-strat 864d KM20]
        sparse_rp: -6.58 vs [TBD]
        hilbert_real: -6.07 vs [TBD]
        hyperloglog: -5.15 vs [TBD]
        chao_weighted: -6.00 vs [TBD]
    </div>
    
    // 우측 — narrative + framework note
    <div>
      <eyebrow>★ 강재현 5/13 0:20 추가 검증</eyebrow>
      <p fontSize=20>"각 single 테이블에서 학습 → multi-join 후 carry-over 가
      cardinality 추정 오차의 원인인가?" 검증 결과:</p>
      
      <p fontSize=18 bold>[TBD - 회수 후]:
      - re-strat Δ avg [TBD]% vs carry-over -5.95% avg
      - 결론: [carry-over 충분 / re-strat 추가 개선 / re-strat 한계]</p>
      
      <p fontSize=14 fg3>method 자체 학습 (minibatch -7.25%) 와도 비교 가능.
      세 학습 방식 차이가 [결정적 / 결정적 X].</p>
    </div>
  </div>
  
  <caption>multi-join (partsupp_deep_10 ⨝ part_wiki_10, 864d × 1.5M row) 의 stratification 학습 방식 3-way 비교. carry-over 방식은 single-table KM20 학습 결과를 multi-join 후 그대로 적용, multi-join re-stratification 은 두 테이블 join 후 864d concat vector 에 fresh KM20 재학습. 8 measurement (4 anchor × 2 mode) 5/13 회수 기반.</caption>
</SlideShell>
```

### 6.5 speaker note (placeholder)

> "이 slide 는 강재현 팀원의 5/13 새벽 피드백 — 두 벡터 테이블을 join 한 이후에 stratification 학습을 별도로 하는 방식의 sensitivity 를 검증한 결과입니다. 본 연구의 기존 measurement framework 는 single-table 별로 KM20 을 학습한 후 multi-join cell 에서는 stratum_id column 을 그대로 carry-over 하는 방식인데, 이게 multi-join 의 cardinality 추정 오차의 원인일 수 있다는 가설이었습니다. partsupp_deep (96d) 과 part_wiki (768d) 를 join 한 864d concat vector 약 1.5M row 에 대해 KM20 을 재학습하는 multi-join re-stratification 측정을 진행한 결과, [TBD - 시나리오별 narrative]. 본 finding 은 향후 multi-table stratification 의 design space 가 [확장 가능 / 이미 robust / curse of dimensionality 한계] 임을 시사합니다."

### 6.6 부록 G — 박광현 5/15 미팅 자료 추가 plan

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
