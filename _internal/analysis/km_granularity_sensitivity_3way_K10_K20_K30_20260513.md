# Cluster Granularity Sensitivity — K=10 vs K=20 vs K=30 (5/13 03:00 3-way 완성)

> **분석 시점**: 2026-05-13 03:00 KST  
> **데이터**: paper_exact_km10 (40) + paper_exact (K=20 base) + paper_exact_km30 (40)  
> **scope**: 4 anchor × 5 cells (single 3 + multi 2) × 3 K values = 60 paired comparison  
> **목적**: 강재현 5/13 1:00 정량 답변 완성 — cluster granularity 가 method 의존적임을 3-way 입증

---

## 0. 3-way 비교 결과 (CaseB ensemble vs B1 paired Δ%)

각 cell 의 paper B1 baseline 대비 우리 method CaseB 의 Δ%. 음수 = 개선.

### sparse_rp (P4 차원 축소 anchor) — ★ U-shape K-sensitivity

| Cell | K=10 Δ% | K=20 Δ% | K=30 Δ% | K-range |
|---|---:|---:|---:|---:|
| A1-DEEP | +5.60 | **-11.20** | -9.95 | 16.81 |
| A1-SIFT | -1.28 | **-13.28** | -7.63 | 11.99 |
| A1-SSN | +2.80 | **-11.50** | -6.95 | 14.30 |
| A2-Fig7 (multi) | +7.19 | **-10.46** | -6.79 | 17.65 |
| A2-Fig9 (multi) | +10.93 | -6.58 | -2.61 | 17.51 |
| **mean** | **+5.05** | **-10.60** | **-6.78** | |

→ **K=20 sweet spot 확정**. K=10 (거친 분할) 평균 +5% 악화 → K=20 평균 -10.6% 강력 개선 → K=30 (미세 분할) 평균 -6.8% 약화. 명확한 U-shape sensitivity.

해석: sparse random projection 의 차원 축소 후 cluster 분할에서 K=20 이 정보 보존 sweet spot. K=10 의 거친 분할은 projection 정보 손실 보상 못함, K=30 의 미세 분할은 stratum 당 sample 부족.

### hilbert_real (P2 공간 분할 anchor) — K-robust + K=30 약간 우세

| Cell | K=10 Δ% | K=20 Δ% | K=30 Δ% | K-range |
|---|---:|---:|---:|---:|
| A1-DEEP | -12.37 | -10.91 | **-11.81** | 1.46 |
| A1-SIFT | -13.47 | -13.18 | **-15.42** | 2.24 |
| A1-SSN | -11.15 | -10.58 | **-11.01** | 0.57 |
| A2-Fig7 (multi) | **-11.41** | -11.52 | -11.10 | 0.42 |
| A2-Fig9 (multi) | -5.88 | -6.07 | **-6.96** | 1.08 |
| **mean** | **-10.86** | **-10.45** | **-11.26** | |

→ **K-robust** (range 0.42 ~ 2.24 매우 작음). Hilbert space-filling curve 의 locality 보존 효과가 cluster granularity 와 독립. K=30 가 약간 더 우수.

### hyperloglog (P9 정보 이론 anchor) — K-robust + K=30 약간 우세

| Cell | K=10 Δ% | K=20 Δ% | K=30 Δ% | K-range |
|---|---:|---:|---:|---:|
| A1-DEEP | -9.08 | -10.54 | **-11.62** | 2.55 |
| A1-SIFT | -12.14 | -12.20 | **-12.28** | 0.15 |
| A1-SSN | -10.11 | **-10.67** | -10.14 | 0.56 |
| A2-Fig7 (multi) | **-9.63** | -8.77 | -9.26 | 0.86 |
| A2-Fig9 (multi) | **-6.61** | -5.15 | -6.01 | 1.45 |
| **mean** | **-9.51** | **-9.47** | **-9.86** | |

→ K-robust (range 0.15 ~ 2.55). HyperLogLog hash 기반 distinct count 가 cluster granularity 와 독립적. K=30 약간 더 우수.

### chao_weighted (P3 스트리밍 anchor) — K=20 sweet spot

| Cell | K=10 Δ% | K=20 Δ% | K=30 Δ% | K-range |
|---|---:|---:|---:|---:|
| A1-DEEP | -10.43 | **-12.20** | -11.75 | 1.77 |
| A1-SIFT | -11.85 | **-14.80** | -13.20 | 2.95 |
| A1-SSN | -12.74 | **-15.28** | -10.70 | 4.57 |
| A2-Fig7 (multi) | -10.99 | **-11.77** | -10.48 | 1.29 |
| A2-Fig9 (multi) | **-7.13** | -6.00 | -5.83 | 1.30 |
| **mean** | **-10.63** | **-12.01** | **-10.39** | |

→ K=20 sweet spot (-12.01% 최적). K=10/K=30 비슷 (-10~-11%). chao_weighted 의 weighted reservoir 가 K=20 의 균등 분할에서 가장 효율적.

---

## 1. 핵심 narrative — cluster granularity sensitivity 는 method 의존적

**method 별 K-sensitivity 패턴 4 가지** 가 본 측정에서 명확히 드러남:

| Method | sensitivity | optimal K | 해석 |
|---|---|---|---|
| **sparse_rp** | ★ 매우 sensitive (U-shape) | K=20 sweet spot | random projection 차원 축소 + cluster 분할의 trade-off |
| **hilbert_real** | robust (range <2.3) | K=30 약간 우세 | space-filling curve 의 locality 보존 |
| **hyperloglog** | robust (range <2.6) | K=30 약간 우세 | hash 기반 distinct count, cluster 무관 |
| **chao_weighted** | 약간 sensitive | K=20 sweet spot | weighted reservoir 의 stratum 균등 활용 |

**multi-table cell (A2-Fig7/Fig9) 에서도 동일 패턴**:
- sparse_rp 만 큰 영향 (+7~+11% K=10 악화)
- 다른 anchor 들은 single cell 과 유사 sensitivity
- → 강재현 1번 의도 "stratification 수가 multi-join 시 cardinality 추정에 미치는 영향" 답변: **multi-join 환경에서도 method 의존적 sensitivity 패턴 유지**

---

## 2. v5 deck 정정 plan finalize

### 정정 1: 신규 slide — K-sensitivity by method

```
[SlideShell — secn="3.", title="cluster granularity sensitivity by method"]

중앙 grouped bar chart 또는 line chart (4 anchor × 3 K values)
─────────────
sparse_rp:    K=10 +5.05    K=20 -10.60   K=30 -6.78   (U-shape, K=20 sweet)
hilbert_real: K=10 -10.86   K=20 -10.45   K=30 -11.26  (robust, K=30 약간)
hyperloglog:  K=10 -9.51    K=20 -9.47    K=30 -9.86   (robust, K=30 약간)
chao_weighted:K=10 -10.63   K=20 -12.01   K=30 -10.39  (K=20 sweet)

caption: "cluster 수 K 의 효과는 method 의존적. sparse RP 만 K=20 sweet spot 결정적 (U-shape), 
다른 anchor 들은 cluster granularity 와 독립적 (range <2.6%)"
```

### 정정 2: paradigm rollup narrative 정정

기존 paradigm rollup slide 의 mean Δ% 가 **K=20 base** 측정 결과임을 명시. K=10/K=30 에서는 다른 패턴 (특히 sparse_rp). 또 method-level breakdown 옆에 K-sensitivity 표 추가.

### 정정 3: limitation 보강

"본 발표의 paradigm rollup 은 K=20 base 측정 결과. cluster 수 K 의 효과는 method 의존적이며, sparse_rp 는 K=20 sweet spot, 다른 anchor 들은 K-robust. 본 K-sensitivity 자체가 본 연구의 추가 finding."

### 정정 4: 신규 narrative — anchor method 일관성 강조

본 측정 결과 hilbert_real / hyperloglog / chao_weighted 3 anchor 가 K=10/20/30 모든 cluster granularity 에서 일관 -9~-12% 개선. **이 일관성이 본 연구의 진짜 contribution** — paradigm 분류는 categorization, 본질은 anchor method 의 robust 효과.

---

## 3. 5/15 박광현 미팅 confirm 추가 항목

- cluster granularity sensitivity 가 method 의존적이라는 발견 (sparse RP U-shape, 다른 anchor robust) 의 학술적 의미
- K=20 가 paper §V-B 영역의 sweet spot 인지 또는 dataset 별 dynamic K 선택이 학술적으로 필요한가
- multi-join cell 에서도 동일 sensitivity 패턴 — single 과 multi 의 K 효과는 method 특성에 의존

---

## 4. multi-join re-stratification framework — 다음 작업 결정

km granularity 측정 완료. 시간 여유 (~3-4시간, 5/13 morning 까지) 보고 multi-join re-stratification framework 작성 + launch 결정. 기존 carry-over (single table KM20 적용) vs re-stratified (join 결과 새 학습) paired 비교.

framework 작성 시간 estimate: 1-2시간 (PG join query + vector concat + stratification 학습 추가).

---

작성: 2026-05-13 03:00 KST · K=10/20/30 3-way 완성 + v5 deck plan finalize + multi-join framework 결정 대기
