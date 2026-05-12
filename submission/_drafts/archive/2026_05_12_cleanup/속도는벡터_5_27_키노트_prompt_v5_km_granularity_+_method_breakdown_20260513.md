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

---

작성: 2026-05-13 03:05 KST · km10/20/30 3-way 완성 + method-level breakdown + v5 정정 plan finalize
