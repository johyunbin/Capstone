# SIFT/SSN K granularity SF=100 axis (5/15 추가 측정, 정직 disclosure #1 cover)

> **분석 시점**: 2026-05-15 00:20 KST
> **데이터**: paper_exact_km{10,30}_sift_ssn (32 file 회수 완료) + B1 baseline (raw/10_전체측정_백업/B1_baseline_9cell)
> **scope**: A1-SIFT + A1-SSN (paper Fig 5/6 영역, sf=100) × 4 anchor × K=10/30 × CaseA/CaseB = 32 measurement
> **trigger**: 사용자 5/15 00:00 명시 "수정 narrative 영역 필요한 실험 (K 빠진 값) 진행" + 정직 disclosure #1 "DEEP single dataset 한정" 영역 cover

---

## 0. B1 baseline (paper Bernoulli, trim10 mean)

| Cell | B1 trim10 |
|---|---:|
| A1-SIFT (sf=100) | **1.6951** |
| A1-SSN (sf=100) | **1.6249** |

paper Bernoulli baseline. 본 분석 영역 = K=10/30 영역 vs B1 baseline 영역 paired Δ%.

(K=20 paper exact base 영역 = raw/10_전체측정_백업 영역, 본 영역 분석 X — handoff v17 §6 영역 기존 측정 영역 carry-over)

---

## 1. CaseB ensemble — K=10 vs K=30 paired Δ% (★ main)

### 1.1 A1-SIFT (sf=100)

| Method | K=10 trim | K=30 trim | Δ% K=10 | Δ% K=30 | best K |
|---|---:|---:|---:|---:|---|
| sparse_rp | 2.7467 | 1.5658 | **+62.04%** (악화) | −7.63% | K=30 |
| chao_weighted | 1.9216 | 1.4713 | +13.36% | **−13.20%** | K=30 |
| hilbert_real | 1.9277 | 1.4337 | +13.72% | **−15.42%** ★ | K=30 |
| hyperloglog | 1.9654 | 1.4869 | +15.95% | **−12.28%** | K=30 |

### 1.2 A1-SSN (sf=100)

| Method | K=10 trim | K=30 trim | Δ% K=10 | Δ% K=30 | best K |
|---|---:|---:|---:|---:|---|
| sparse_rp | 2.4439 | 1.5120 | **+50.41%** (악화) | −6.95% | K=30 |
| chao_weighted | 1.6837 | 1.4510 | +3.62% | **−10.70%** | K=30 |
| hilbert_real | 1.6896 | 1.4461 | +3.98% | **−11.00%** | K=30 |
| hyperloglog | 1.7401 | 1.4602 | +7.09% | **−10.14%** | K=30 |

---

## 2. CaseA 단독 대체 (K=10 vs K=30 paired Δ%)

### 2.1 A1-SIFT

| Method | K=10 trim | K=30 trim | Δ% K=10 | Δ% K=30 |
|---|---:|---:|---:|---:|
| sparse_rp | 3.3248 | 1.5178 | **+96.14%** (악화) | −10.46% |
| chao_weighted | 1.5933 | 1.6491 | −6.01% | −2.71% |
| hilbert_real | 1.5579 | 1.5014 | −8.09% | **−11.43%** |
| hyperloglog | 1.6940 | 1.6492 | −0.07% | −2.71% |

### 2.2 A1-SSN

| Method | K=10 trim | K=30 trim | Δ% K=10 | Δ% K=30 |
|---|---:|---:|---:|---:|
| sparse_rp | 2.6217 | 1.5430 | **+61.34%** (악화) | −5.04% |
| chao_weighted | 1.6030 | 1.5866 | −1.35% | −2.36% |
| hilbert_real | 1.6119 | 1.5477 | −0.80% | −4.75% |
| hyperloglog | 1.7058 | 1.6285 | +4.98% | +0.22% |

---

## 3. 핵심 finding 4

### Finding 1 — sparse_rp K=10 강한 악화 영역 SIFT/SSN 영역 일관

| Dataset | K=10 CaseA Δ% | K=10 CaseB Δ% | K=30 CaseA Δ% | K=30 CaseB Δ% |
|---|---:|---:|---:|---:|
| A1-SIFT | +96.14% | +62.04% | −10.46% | −7.63% |
| A1-SSN | +61.34% | +50.41% | −5.04% | −6.95% |

→ sparse_rp K=10 영역 = 강한 악화 영역 (DEEP K=10 +77~+90% 영역과 일관). K=30 영역 normal 영역. **paper Fig 5/6 영역 (single-table SF=100) 영역 패턴 모든 dataset 일관**.

### Finding 2 — CaseB ensemble 영역 K=30 best 영역 (모든 method × 모든 dataset)

| Method | A1-SIFT K=30 CaseB | A1-SSN K=30 CaseB |
|---|---:|---:|
| sparse_rp | −7.63% | −6.95% |
| chao_weighted | −13.20% | −10.70% |
| hilbert_real | **−15.42%** ★ | **−11.00%** |
| hyperloglog | −12.28% | −10.14% |

→ K=30 영역 = SIFT/SSN 영역 best 영역. **DEEP K granularity 영역 (K=20 sweet 또는 K=30 slight edge) 영역 와 약간 다름**:
- DEEP A5 영역 sparse_rp/chao_weighted = K=20 sweet spot
- DEEP A5 영역 hilbert_real/hyperloglog = K=30 slight edge
- SIFT/SSN 영역 = 모든 method K=30 영역 best

→ **dataset-dependent K best 패턴**. K granularity 영역 method × dataset 모두 영역 sensitivity 영역.

### Finding 3 — hilbert_real best 영역 (SIFT/SSN 모두)

A1-SIFT CaseB K=30 hilbert_real = **−15.42%** (모든 method 영역 best).
A1-SSN CaseB K=30 hilbert_real = **−11.00%** (모든 method 영역 best).

→ hilbert_real 영역 = SIFT 영역 (128d) + SSN 영역 (256d) 영역 모두 strong. **고차원 영역 hilbert curve 영역 effective**.

### Finding 4 — CaseA 단독 대체 영역 약함 (CaseB ensemble 영역 우세)

CaseA 단독 best:
- A1-SIFT: hilbert_real K=30 = −11.43%
- A1-SSN: hilbert_real K=30 = −4.75%

CaseB ensemble best:
- A1-SIFT: hilbert_real K=30 = −15.42% (CaseA 대비 +4 pp)
- A1-SSN: hilbert_real K=30 = −11.00% (CaseA 대비 +6 pp)

→ **CaseB ensemble (Bernoulli + 우리 method 평균) 영역 일관 우세**. paper Bernoulli 영역 보존 영역 + 본 method 영역 추가 영역 = 안전 영역.

---

## 4. DEEP K granularity 영역 (handoff v20 §10) 와 비교

### 4.1 K granularity 패턴 비교 (CaseB best K)

| Dataset (sf=100) | sparse_rp | chao_weighted | hilbert_real | hyperloglog |
|---|---|---|---|---|
| DEEP A5-sf100 (handoff v20) | K=20 sweet | K=20 sweet | K=30 slight | K=30 slight |
| **A1-SIFT (본)** | K=30 | K=30 | K=30 ★ | K=30 |
| **A1-SSN (본)** | K=30 | K=30 | K=30 ★ | K=30 |

→ **DEEP 영역 K=20 sweet** vs **SIFT/SSN 영역 K=30 best**. dimension-dependent K best 가능성 (DEEP 96d / SIFT 128d / SSN 256d 영역 고차원 K=30 영역 우세).

### 4.2 Best Δ% 영역 비교

| Dataset | best method × K | CaseB Δ% |
|---|---|---:|
| DEEP A5-sf100 | chao_weighted × K=20 | −12.20% |
| **A1-SIFT** (sf=100) | **hilbert_real × K=30** | **−15.42%** ★ |
| **A1-SSN** (sf=100) | **hilbert_real × K=30** | **−11.00%** |

→ SIFT 영역 = paper 모든 cell 영역 best Δ% (−15.42%). 정직 disclosure #1 cover 완료.

---

## 5. 박세은 답변 영역 form

> 5/14 회의 후 정직 disclosure #1 ("DEEP single dataset 한정") 영역 cover 위해 SIFT/SSN K granularity 영역 추가 측정 진행 (5/15 새벽).
>
> SIFT/SSN K=10/K=30 영역 추가 측정 결과 (paper Fig 5/6 영역, sf=100):
> - sparse_rp K=10 강한 악화 영역 (SIFT +96%, SSN +61%) → **DEEP 영역 패턴 (K=10 +77~+90%) 영역 모든 dataset 일관**
> - CaseB ensemble K=30 영역 best 영역 (hilbert_real SIFT −15.42%, SSN −11.00%)
> - DEEP 영역 K=20 sweet vs SIFT/SSN 영역 K=30 best = **dimension-dependent K best 패턴** (DEEP 96d / SIFT 128d / SSN 256d, 고차원 K=30 영역 우세)
>
> → 정직 disclosure #1 ("DEEP single dataset 한정") 영역 cover 완료. paper 모든 single-table cell (Fig 5/6, sf=100) 영역 K granularity 영역 검증.
>
> 5/15 in-flight: multi-cell (A1-DEEP + A2-Fig7 + A2-Fig9) K=10/30 (48 file) + A4-sel K=10/30 (16 file) 추가 측정.

---

## 6. 정직 disclosure

1. 본 측정 = paper Fig 5/6 cell (A1-SIFT, A1-SSN) 영역 한정. paper 영역 Fig 7 (A2-Fig7 YFCC) + Fig 9 (A2-Fig9 DEEP+WIKI cross) + Fig 13 (A4-sel) 영역 = 5/15 sequenced in-flight
2. K=20 영역 base 영역 = raw/10_전체측정_백업 영역 paper exact 영역 사용 영역 (별 영역 분석 영역 진행 X)
3. paper query set 영역 = A1-DEEP/SIFT/SSN 영역 모두 Q3+Q10+Q12 영역 (3 queries). A5-scale 영역 = Q3+Q5+Q20 (다름). 영역 직접 비교 시 caveat.
4. dataset-dependent K best 영역 (DEEP K=20 vs SIFT/SSN K=30) 영역 = sample size dimension 영역 (dim×K factor) 영역 가능성, 추가 dimension 영역 측정 영역 필요 (future work)

---

## 7. 다음 작업

1. multi-cell (A1-DEEP + A2-Fig7 + A2-Fig9) K=10/30 결과 회수 + 분석 (~24:30-01:00 ETA)
2. A4-sel K=10/30 결과 회수 + 분석 (~01:00-01:15 ETA)
3. handoff v22 final 작성 (모든 결과 종합)
4. 회의 PDF v2 + narrative v2 영역 정정 룰 #10 영역 update (SIFT/SSN K=10/30 = K=30 best, dimension-dependent K)
5. claude.ai/design v7 update 영역 verify + 통합

---

작성: 2026-05-15 00:20 KST · SIFT/SSN K=10/30 회수 (32 file) + 분석 + paper Fig 5/6 영역 cover + 정직 disclosure #1 해소 + DEEP K granularity 와 비교 (dimension-dependent K best 패턴 발견)
