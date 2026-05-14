# K granularity sensitivity — SF=1 / SF=10 / SF=100 axis (5/15 추가 측정)

> **분석 시점**: 2026-05-14 22:10 KST
> **데이터**: paper_exact_km{10,30}_sf_axis (server, 48 file) + paper_exact base K=20 (raw/10_전체측정_백업, 24 file) + B1 baseline (raw/10_전체측정_백업/B1_baseline_9cell, 3 file)
> **scope**: A5-scale-sf{1,10,100} (DEEP single 3 cells) × 4 anchor × K=10/20/30 × CaseA/CaseB = 72 measurement
> **trigger**: 박세은 8:50 카톡 발견 (회의 PDF v2 §2.5 SF=1 미측정 명시) + 사용자 옵션 B 결정

---

## 0. B1 baseline (paper Bernoulli, trim10 mean)

| Cell | B1 trim10 |
|---|---:|
| A5-scale-sf1 (DEEP sf=1) | 1.6182 |
| A5-scale-sf10 (DEEP sf=10) | 1.5407 |
| A5-scale-sf100 (DEEP sf=100) | 1.6346 |

paper Bernoulli baseline 의 trim10 mean. DEEP single dataset 의 3 SF axis.

---

## 1. CaseB ensemble — K granularity × SF axis paired Δ% (★ main)

각 cell × method × K 의 CaseB trim10 mean → B1 baseline 대비 paired Δ%.

### 1.1 SF=1 (DEEP sf=1, 1M rows)

| Method | K=10 trim | K=20 trim | K=30 trim | Δ% K=10 | Δ% K=20 | Δ% K=30 | best K |
|---|---:|---:|---:|---:|---:|---:|---|
| sparse_rp | 2.8718 | 1.4288 | 1.4887 | **+77.47%** | **−11.70%** | −8.01% | K=20 |
| chao_weighted | 1.7990 | 1.3899 | 1.4229 | +11.17% | **−14.11%** | −12.07% | K=20 |
| hilbert_real | 1.7258 | 1.4399 | 1.4200 | +6.65% | −11.02% | **−12.25%** | K=30 |
| hyperloglog | 1.7311 | 1.4534 | 1.4148 | +6.97% | −10.19% | **−12.57%** | K=30 |

### 1.2 SF=10 (DEEP sf=10, 10M rows)

| Method | K=10 trim | K=20 trim | K=30 trim | Δ% K=10 | Δ% K=20 | Δ% K=30 | best K |
|---|---:|---:|---:|---:|---:|---:|---|
| sparse_rp | 2.3719 | 1.4393 | 1.5006 | +53.95% | **−6.58%** | −2.61% | K=20 |
| chao_weighted | 1.6401 | 1.4483 | 1.4509 | +6.45% | **−6.00%** | −5.83% | K=20 |
| hilbert_real | 1.6313 | 1.4471 | 1.4335 | +5.88% | −6.07% | **−6.96%** | K=30 |
| hyperloglog | 1.7061 | 1.4613 | 1.4481 | +10.74% | −5.15% | **−6.01%** | K=30 |

### 1.3 SF=100 (DEEP sf=100, 100M rows)

| Method | K=10 trim | K=20 trim | K=30 trim | Δ% K=10 | Δ% K=20 | Δ% K=30 | best K |
|---|---:|---:|---:|---:|---:|---:|---|
| sparse_rp | 2.7099 | 1.4514 | 1.4720 | +65.79% | **−11.20%** | −9.95% | K=20 |
| chao_weighted | 1.7964 | 1.4352 | 1.4425 | +9.90% | **−12.20%** | −11.75% | K=20 |
| hilbert_real | 1.7171 | 1.4562 | 1.4416 | +5.05% | −10.91% | **−11.81%** | K=30 |
| hyperloglog | 1.8306 | 1.4623 | 1.4445 | +11.99% | −10.54% | **−11.62%** | K=30 |

---

## 2. 핵심 finding 4

### Finding 1 — sparse_rp U-shape K-sensitivity 모든 SF 에서 유지

| SF | K=10 Δ% | K=20 Δ% | K=30 Δ% |
|---|---:|---:|---:|
| 1 | **+77.47%** (악화) | −11.70% | −8.01% |
| 10 | +53.95% (악화) | −6.58% | −2.61% |
| 100 | +65.79% (악화) | −11.20% | −9.95% |

→ **모든 SF 에서 sparse_rp K=10 = 강한 악화** + K=20/K=30 strong improvement. SF=1/10/100 axis 안 sensitivity 패턴 일관.

### Finding 2 — chao_weighted K=20 sweet spot (모든 SF)

| SF | K=10 Δ% | K=20 Δ% | K=30 Δ% |
|---|---:|---:|---:|
| 1 | +11.17% | **−14.11%** ★ | −12.07% |
| 10 | +6.45% | **−6.00%** ★ | −5.83% |
| 100 | +9.90% | **−12.20%** ★ | −11.75% |

→ K=20 sweet spot 일관. SF=1 + SF=100 강 (−12~−14%), SF=10 약함 (−6%).

### Finding 3 — hilbert_real / hyperloglog K=30 약간 우세 (모든 SF)

| Method | SF | K=20 Δ% | K=30 Δ% | gap |
|---|---|---:|---:|---:|
| hilbert_real | 1 | −11.02% | **−12.25%** | 1.23 |
| hilbert_real | 10 | −6.07% | **−6.96%** | 0.89 |
| hilbert_real | 100 | −10.91% | **−11.81%** | 0.90 |
| hyperloglog | 1 | −10.19% | **−12.57%** | 2.38 |
| hyperloglog | 10 | −5.15% | **−6.01%** | 0.86 |
| hyperloglog | 100 | −10.54% | **−11.62%** | 1.08 |

→ K=30 일관 우세, gap 1-2.4% 수준. K-robust + K=30 slight edge.

### Finding 4 — ★ SF=10 영역 K=20/K=30 효과 약화 (특이 패턴)

SF=10 (DEEP sf=10, 10M rows) 영역에서 모든 method 가 SF=1 + SF=100 보다 약한 −5~−7% 수준. 원인 추정:
- SF=1 (1M rows) = paper baseline 의 변동성이 가장 크고 stratification 효과 강함 (−11~−14%)
- SF=100 (100M rows) = paper baseline 의 skew 정량 효과 maximal (−11~−12%)
- **SF=10 (10M rows) = 중간 영역 — stratification 효과 약함** (−5~−7%)

paper §VI-B "sample size trajectory varies depending on the dataset" 영역과 정합. SF (data size) 의 effect 가 monotonic 아니라 U-shape 가능성.

---

## 3. Per-method 3-way K granularity 종합 (3 SF mean)

### 3.1 CaseA 단독 대체

| Method | K=10 mean Δ% | K=20 mean Δ% | K=30 mean Δ% | range | K-best |
|---|---:|---:|---:|---:|---|
| sparse_rp | +89.92% | −1.22% | −9.27% | 99.19 | K=30 |
| chao_weighted | −0.19% | +2.39% | −3.08% | 5.47 | K=30 |
| hilbert_real | −3.13% | −2.65% | −1.96% | 1.17 | K=10 |
| hyperloglog | +2.43% | +2.12% | +1.07% | 1.37 | K=30 |

### 3.2 CaseB 결합 ensemble (★ main contribution)

| Method | K=10 mean Δ% | K=20 mean Δ% | K=30 mean Δ% | range | K-best |
|---|---:|---:|---:|---:|---|
| sparse_rp | +65.73% | **−9.83%** | −6.85% | 75.56 | K=20 |
| chao_weighted | +9.18% | **−10.77%** | −9.88% | 19.94 | K=20 |
| hilbert_real | +5.86% | −9.33% | **−10.34%** | 16.20 | K=30 |
| hyperloglog | +9.90% | −8.63% | **−10.07%** | 19.97 | K=30 |

---

## 4. 박세은 8:50 답변 영역

박세은 8:50 카톡 발견:
> "긴급회의 자료 11페이지에서는 K=20이 제일 좋다는 게 SF 1을 제외한 상황에서 검증되었다고 적혀있는데..."

회의 PDF v2 §2.5 line 322 verbatim:
> "K 변화 측정은 SF=100 (A1) + SF=10 (A2) 범위에서만 진행했다. **SF=1 영역에서 K=20 이 best 인지는 미측정**. 회의 의견 #2 반영 향후 실험 영역."

본 5/14 추가 측정 = **SF=1 영역 K granularity 측정 완료** + SF=10 single + SF=100 single (A5 axis):

### 4.1 SF=1 영역 K=20 best 여부

| Method | CaseB best K (SF=1) |
|---|---|
| sparse_rp | **K=20** (Δ −11.70%) |
| chao_weighted | **K=20** (Δ −14.11%) |
| hilbert_real | K=30 (Δ −12.25%) |
| hyperloglog | K=30 (Δ −12.57%) |

→ **SF=1 영역 K=20 best 여부 = method-dependent**. sparse_rp + chao_weighted = K=20 sweet spot 유지. hilbert_real + hyperloglog = K=30 약간 우세.

기존 회의 PDF v2 §2.5 결과 (SF=100 + SF=10 multi-table) 와 정합: sparse_rp + chao_weighted = K=20 sweet spot, hilbert_real + hyperloglog = K-robust + K=30 slight edge.

### 4.2 박세은 carry-over 가능 form

> "SF=1 영역 K granularity 추가 측정 결과 보고드릴게요. A5-scale-sf1 (DEEP sf=1) × K=10/20/30 × 4 anchor × CaseA/CaseB = 24 file 추가 측정.
>
> SF=1 영역 K=20 best 여부 = method-dependent 결과:
> - sparse_rp: K=20 sweet spot (Δ −11.70% best)
> - chao_weighted: K=20 sweet spot (Δ −14.11% best)
> - hilbert_real: K=30 약간 우세 (Δ −12.25%, K=20 −11.02% 와 gap 1.23%)
> - hyperloglog: K=30 약간 우세 (Δ −12.57%, K=20 −10.19% 와 gap 2.38%)
>
> SF=10 (A5-scale-sf10) 추가 측정 결과도 함께. 기존 회의 PDF v2 §2.5 패턴 (sparse_rp/chao_weighted = K=20 sweet spot, hilbert_real/hyperloglog = K-robust) **모든 SF axis (1/10/100) 에서 일관 유지**.
>
> 회의 PDF v2 §2.5 line 322 의 'SF=1 영역 K=20 best 미측정' wording 정정 가능: 'SF=1+10+100 axis 모두 측정 완료, method-dependent K best 패턴 일관'."

---

## 5. 정정 룰 list update (10 → 13)

handoff v20 §4 의 정정 룰 10 list 에 추가:

| # | 정정 영역 | source |
|---|---|---|
| 10 (update) | **K granularity SF coverage = SF=1+10+100 × K=10/20/30 measured** (5/14 추가 측정 완료) | 박세은 8:50 + 본 분석 |

K granularity SF axis = future work 영역에서 **현 측정 영역**으로 이동. 회의 PDF v2 §2.5 line 322 + §8.1 "K=20 SF=10 검증 (의견 #2)" wording 정정.

---

## 6. 5/27 발표 + 6/11 보고서 narrative 통합

### 5/27 phase 1 slide 안 위치

- **Slide 11-13 측정 결과 RQ2/RQ3 sub** = K granularity SF axis 표 추가
  - "K granularity sensitivity 가 모든 SF axis (1/10/100) 에서 method-dependent 패턴 일관"
  - sparse_rp U-shape (K=10 +66%~+90%) + K=20 sweet spot
  - chao_weighted K=20 sweet spot
  - hilbert_real / hyperloglog K-robust + K=30 slight edge

### 6/11 보고서 §6 batch axis K granularity sub

- 본 file (km_granularity_sf_axis_SF1_SF10_SF100_20260515.md) 통합
- 기존 §6 K granularity 영역 (A1+A2 cells) + 본 §6 K granularity SF axis (A5 cells) → 두 axis complementary

---

## 7. 정직 disclosure

1. 본 측정 = DEEP single dataset 한정 (SIFT/SSN sf=1/10/100 미측정)
2. A5-scale-sf1 = paper Fig.14 영역, Q3/Q5/Q20 (3 query, paper exact). A1-DEEP = Q3/Q10/Q12. 쿼리 다름 → 직접 비교 시 caveat.
3. 4 anchor 한정 (sparse_rp / chao_weighted / hilbert_real / hyperloglog). 다른 method (예: minibatch_partial −10.17% 단독 best) K granularity SF axis 영역 미측정.
4. SF=10 영역 약한 효과 (−5~−7%) 원인 추가 검증 필요 (data size U-shape 가능성, future work).

---

## 8. 다음 작업

1. raw/06 SF_axis README 작성
2. handoff v20 §10 K granularity 영역 update
3. 회의 PDF v2 §2.5 line 322 정정 영역 (mass update 시)
4. 5/27 deck v7 + 6/11 outline v4 통합
5. 박세은 carry-over 시 활용

---

작성: 2026-05-14 22:10 KST · K=10/30 회수 완료 (48 file) + 3-way K granularity SF=1/10/100 분석 + 박세은 8:50 답변 영역 + 5/27 + 6/11 narrative 통합 plan
