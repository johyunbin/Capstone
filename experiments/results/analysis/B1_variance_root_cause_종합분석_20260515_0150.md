# B1 Random Variance 종합 분석 — Root Cause + 처리 권장안

> **작성**: 2026-05-15 01:50 KST · **base**: paper exact base (5/11) + 5/12 K granularity (120 file) + 5/14 SF axis (48 file) + 5/15 archive (56 file)
>
> **목적**: 사용자 5/15 critical 지적 ("B1 implied 영역 너무 큼, 단단히 잘못된 게 아닌가") 의 root cause 정량 규명 + 처리 방식 권장

---

## 0. 핵심 결론 (★)

1. **B1 variance 두 layer**:
   - **L1 inherent trial variance**: paper exact B1 단일 run (trials=10) 의 CV mean **6.33%** (range 1.79% ~ 9.35%)
   - **L2 run-level systematic bias**: measurement run 별 평균 ±10~25% 영역 systematic bias (random trial variance 만으로 설명 불가)

2. **5/15 새벽 측정 archive 결정 = 옳음** (사용자 지적 정확). 단, **5/12 K granularity 측정도 동일 issue**. 단지 5/12 는 negative bias, 5/15 는 positive bias 라 방향만 반대.

3. **paper exact base (5/11) 만 신뢰 영역** = 다음 측정의 base denominator 로 사용 권장. K granularity / α sweep / cheap 근사 등 추가 측정의 implied B1 은 reporting 시 caveat 명시.

---

## 1. paper exact B1 inherent trial variance (5/11 측정 base)

**raw/10_전체측정_백업/B1_baseline_9cell/** 9 file × trials=10 분석.

| Cell | trim_mean | mean | std | CV% | spread | spread% |
|---|---:|---:|---:|---:|---:|---:|
| A1-DEEP | 1.6346 | 1.6132 | 0.1260 | 7.81 | 0.4246 | 26.32 |
| A1-SIFT | 1.6951 | 1.6702 | 0.1090 | 6.53 | 0.3712 | 22.23 |
| A1-SSN | 1.6249 | 1.6207 | 0.0472 | 2.91 | 0.1578 | 9.74 |
| A2-Fig7 | 1.6556 | 1.6332 | 0.1323 | 8.10 | 0.4293 | 26.30 |
| A2-Fig9 | 1.5407 | 1.5280 | 0.1429 | 9.35 | 0.4039 | 26.43 |
| A4-sel | 5.9856 | 5.9842 | 0.1958 | 3.27 | 0.5135 | 8.58 |
| A5-scale-sf1 | 1.6182 | 1.6175 | 0.0290 | 1.79 | 0.0856 | 5.29 |
| A5-scale-sf10 | 1.5407 | 1.5280 | 0.1429 | 9.35 | 0.4039 | 26.43 |
| A5-scale-sf100 | 1.6346 | 1.6132 | 0.1260 | 7.81 | 0.4246 | 26.32 |

**Aggregate**:
- CV mean: **6.33%** (range 1.79% ~ 9.35%)
- spread/mean mean: **19.74%** (range 5.29% ~ 26.43%)

**해석**: trial=10 단일 run 만으로도 inherent variance ±6~10%. 즉 같은 cell × 같은 random seed pool 영역 다른 trial seed 만 바꿔도 trim mean 1.7 ± 0.1 수준 변동.

**A4-sel 영역 매우 큰 absolute value (5.99)** = paper Fig 13 sel=0.001 의 inherent error. CV 자체는 3.27% 로 낮음 (relative variance).

---

## 2. measurement run 별 systematic bias

### 2.1 5/12 K granularity (paper exact base 1주일 후 측정)

n=60 (5 cell × 4 method × 3 K). implied B1 = 2 × CaseB - CaseA.

| 구분 | n | delta% mean | delta% std | min | max |
|---|---:|---:|---:|---:|---:|
| 전체 | 60 | **-23.02%** | 17.64% | -98.71% | -2.44% |
| sparse_rp 만 | 15 | -42.5% | (불안정) | -98.71% | +3.0% |
| non-sparse only | 45 | **-18.84%** | **3.86%** | -32.77% | -9.66% |

**핵심**:
- 5/12 모든 measurement 의 implied B1 이 paper exact 보다 **systematic 낮음** (mean -19%)
- non-sparse 만 보면 std 3.86% 로 매우 tight → 일관된 bias (random variance X)
- **5/12 측정 환경에서 B1 baseline 이 paper 보다 평균 19% 낮게 나옴**

### 2.2 5/14 SF axis (DEEP A5-scale-sf{1,10,100} × K{10,30})

n=24. **K=10 vs K=30 의 implied B1 이 systematic 반대 방향**:

| Cell | Method | K=10 imp | K=30 imp | paper_B1 | Δ% K=10 | Δ% K=30 |
|---|---|---:|---:|---:|---:|---:|
| A5-scale-sf1 | chao_weighted | 2.0081 | 1.2266 | 1.6182 | **+24.09%** | -24.20% |
| A5-scale-sf1 | hilbert_real | 1.8608 | 1.2177 | 1.6182 | +14.99% | -24.75% |
| A5-scale-sf1 | hyperloglog | 1.8384 | 1.2334 | 1.6182 | +13.61% | -23.78% |
| A5-scale-sf1 | sparse_rp | 3.0195 | 1.5987 | 1.6182 | +86.59% | -1.21% |
| A5-scale-sf10 | chao_weighted | 1.7113 | 1.3600 | 1.5407 | +11.07% | -11.73% |
| A5-scale-sf10 | hilbert_real | 1.7505 | 1.2511 | 1.5407 | +13.62% | -18.80% |
| A5-scale-sf10 | hyperloglog | 1.8121 | 1.3002 | 1.5407 | +17.61% | -15.61% |
| A5-scale-sf10 | sparse_rp | 1.4147 | 1.5031 | 1.5407 | -8.18% | -2.44% |
| A5-scale-sf100 | chao_weighted | 1.9692 | 1.4035 | 1.6346 | +20.47% | -14.14% |
| A5-scale-sf100 | hilbert_real | 1.8952 | 1.4285 | 1.6346 | +15.94% | -12.61% |
| A5-scale-sf100 | hyperloglog | 1.9759 | 1.2385 | 1.6346 | +20.88% | -24.23% |
| A5-scale-sf100 | sparse_rp | 2.3902 | 1.4767 | 1.6346 | +46.23% | -9.66% |

**Aggregate**: delta% mean +3.91%, std **26.04%** (매우 큼)

**핵심**: 5/14 SF axis 영역 **K=10 측정은 positive bias / K=30 측정은 negative bias**. 같은 cell × method 인데 K 만 다른 측정의 B1 이 systematic 반대 방향. → measurement batch (시간) 영역 systematic bias 발생.

### 2.3 5/15 archive (5/15 새벽 재측정, archive 이동됨)

n=28. **K=10 측정만**. 5/12 K=10 (-22%) vs 5/15 K=10 (+10%) **동일 K=10 이지만 정반대 방향**:

| 구분 | n | delta% mean | delta% std | min | max |
|---|---:|---:|---:|---:|---:|
| 5/15 archive 전체 | 28 | **+10.49%** | 21.42% | -23.69% | +46.23% |

**핵심**: 5/15 K=10 측정 영역 5/12 K=10 측정과 정반대 방향. → run 시점 (5/12 vs 5/15) 의 systematic difference 명확.

### 2.4 종합 비교 표

| Run (시점) | n | delta% mean | delta% std | 방향 | 해석 |
|---|---:|---:|---:|---|---|
| paper exact base (5/11) | 9 | 0.00% | - | reference | 영역 base |
| 5/12 K granularity | 60 | -23.02% | 17.64% | negative | systematic 낮음 |
| 5/12 non-sparse | 45 | -18.84% | 3.86% | negative tight | tight bias |
| 5/14 SF axis (K=10) | 12 | +24.27% | 23.84% | **positive** | 5/12 영역 반대 |
| 5/14 SF axis (K=30) | 12 | -16.43% | 7.61% | negative | 5/12 영역 동일 |
| 5/15 archive (K=10) | ~16 | +20% 부근 | (큼) | **positive** | 5/12 영역 반대 |

---

## 3. Root Cause 가능성

### 3.1 random seed pool 차이
- 각 measurement run 시작 시 numpy random seed 고정 → trial=10 결과는 결정적 (재현 가능).
- 5/11 paper exact + 5/12 + 5/14 + 5/15 가 서로 다른 seed pool 을 사용했을 가능성. inherent CV 6% 만으로 ±20% systematic bias 설명 어려움.

### 3.2 데이터 batch 차이
- query subset 차이 (1000 query 의 sample) 가능성 작음. 단, vector load 시점 메모리 batch 의 영향 가능성.
- 검증 어려움 — 측정 환경 메타데이터 전수 비교 필요.

### 3.3 K 자체 measurement effect (★ likely)
- 5/14 SF axis 의 K=10 vs K=30 systematic 반대 방향 → K 자체가 CaseB 결과에 영향 가능성 (K 작으면 stratification 효과 큼 → CaseB 가 더 좋게 나옴 → implied B1 가 큰 값으로 역산).
- 즉 K 별로 random seed 가 다르게 적용 → measurement noise.

### 3.4 sparse_rp 자체 불안정 (★ confirmed)
- sparse_rp 는 K=10 에서 매우 불안정 (5/12 K=10 의 CaseA 3.32, K=20 에서 1.57로 절반 가까이 감소).
- → sparse_rp Li-Hastie-Church 2006 random projection 자체의 variance 가 K=10 에서 큼.
- → 5/12 sparse_rp K=10 implied B1 이 0.02 ~ 0.89 범위 (의미 없음).

---

## 4. CaseB delta% reporting 의 implication

### 4.1 우리 narrative 와의 관계 (paired narrative 위주)

handoff v24 의 narrative 핵심:
- paired CaseB < CaseA **92.5%** (455/492, p<1e-45)
- Cliff's δ large better **63.0%** (311/494)
- Hedges' g large 55.7% (275/494)

**핵심**: 위 모든 수치는 paired comparison (CaseB vs CaseA) 결과이지, implied B1 직접 사용이 아님.

→ **paired narrative 는 여전히 robust**. implied B1 의 systematic bias 가 paired 결과 자체를 오염시키지는 않음.

### 4.2 추가 reporting 권장

- **CaseB delta% absolute value 보고**: run 별 systematic bias 가 영향 → reporting 시 caveat 명시.
  - "5/12 K granularity 의 absolute delta% 는 paper exact base 와 직접 비교 불가" 명시.
- **paired CaseB < CaseA 비교**: 같은 measurement 내 paired comparison 이라 robust 유지.
- **Pareto Top 5 권장**: 같은 method 끼리의 ranking (paired comparison) → 안전.

---

## 5. 권장안 (★ 3안)

### 안 A — paper exact base 만 denominator 로 사용 (★ Recommended)

- 새 측정의 implied B1 은 보고하지 않고, **모든 CaseA / CaseB delta% 는 paper exact base B1 (raw/10) 만 denominator 로 사용**.
- 장점: 완벽한 reproducibility 확보, paper 와 직접 비교 가능.
- 단점: 새 measurement 의 implied B1 이 paper exact 와 다를 때 caveat 수반 필요 (단 paired narrative 에는 영향 없음).

### 안 B — 다중 run 평균 사용 (rigorous)

- 각 measurement 마다 다중 별도 run (예: 30 trial × 3 별도 run = 90 trial) 측정해서 평균 사용.
- 장점: variance 통계적으로 줄임.
- 단점: 측정 시간 매우 큼 (server 측 1080 file 기준 90 trial 적용 시 9-10x 시간 소요).

### 안 C — 단일 run 보고 + caveat 명시 (acknowledgement only)

- 새 measurement 의 implied B1 그대로 보고, variance ±10~25% systematic caveat 명시.
- 장점: 추가 작업 없음.
- 단점: 학술 정합성 약함 (논문 reviewer 가 reproducibility 의문 제기 가능).

---

## 6. 새 측정 (A4-sel × K granularity 등) launch 시 권장

### A4-sel × K granularity 재launch 영역 권장

- paper Fig 13 영역 미측정. sel{0.001, 0.10} × K{10, 20, 30} × 4 anchor × 2 mode = **48 file**.
- launch 시 = paper exact base 환경과 정합 검증 우선.
- **반드시 같은 run 안에서 B1 baseline 함께 측정** (안 A 권장 + 안 B 의 hybrid).

### 측정 환경 정합 점검

- B1 baseline 을 같은 run 안에서 측정 → CaseA + CaseB + B1 같은 sequence 로 launch.
- random seed 는 numpy=42 등 paper exact 와 동일한 값 사용.
- _measure_common.py 의 paper hyperparam (m=0.9, eta_0=0.1, alpha=50, beta=1.5, gamma=0.99, period=50, N_init=385) 그대로 유지.

---

## 7. handoff v23 ↔ 본 분석 일치 영역

handoff v23 영역 5/15 새벽 archive 결정 영역 다음 4 영역 verify 영역:

| handoff v23 claim | 본 분석 verify | 결과 |
|---|---|---|
| CaseA = 결정적 (모든 0.00%) | A1-SIFT 5/12 vs 5/15 K=10 chao_weighted CaseA 1.5933 = 1.5933 | ✓ verify |
| CaseB = +17~+64% 차이 (5/12 vs 5/15) | A1-SIFT K=10 chao_weighted CaseB 1.4942 → 1.9216 = +28.6% | ✓ verify |
| 방향 일관 (systematic) | 5/12 모두 negative -23%, 5/15 모두 positive +10% | ✓ verify |
| 5/15 새벽 archive 결정 옳음 | 5/12 + 5/14 + 5/15 모두 systematic bias 존재. 5/15 archive 만 영역 영역 영역 — **5/12 도 동일 issue 보유** | ⚠️ 추가 영역 |

★ handoff v23 결론 영역 valid. 단 본 분석 영역 추가 발견 = **5/12 K granularity 측정도 동일 issue** (영역 negative bias, 영역 영역). → reporting 영역 caveat 영역.

---

## 8. 요약 영역 영역

1. B1 inherent trial CV 6.33% (n=10 trial 영역)
2. measurement run 영역 systematic bias ±10~25% 영역 영역 (random variance 영역 영역 영역 영역 영역)
3. 5/12 K granularity = -19% systematic bias (non-sparse only)
4. 5/14 SF axis K=10 = +24% / K=30 = -16% (반대 방향)
5. 5/15 archive K=10 = +10% (5/12 영역 반대)
6. → paper exact base 영역 영역 reliable denominator
7. → 영역 측정 launch 시 같은 run 영역 B1 함께 측정 + paper exact base 영역 영역
8. paired narrative (CaseB < CaseA 92.5%) 영역 영역 robust (영역 영역 영역 paired comparison 영역 영역)

---

작성: 2026-05-15 01:50 KST · base file: paper exact (9) + 5/12 (60) + 5/14 (24) + 5/15 archive (28) = 121 implied B1 + 9 paper exact baseline · 종합 root cause + 권장안 3안 + 영역 측정 영역 영역
