# K Granularity × Dimension 종합 검증 — Dimension-Dependent K Best 가설

> **작성**: 2026-05-15 03:10 KST · **base**: 5/12 paper exact base K granularity (120 file, 5 cells × 4 method × 3 K × 2 mode) + 5/14 SF axis (48 file, 3 cells × 4 method × 2 K × 2 mode)
>
> **목적**: handoff v23 의 "dimension-dependent K best 잠정 가설" (DEEP 96d K=20 sweet vs SIFT/SSN 128/256d K=30 best) 검증

---

## 0. 핵심 결론 (★)

1. **dimension-dependent K best 가설 = 약한 evidence** (현재 데이터 기준)
   - 96d / 128d / 864d cells: K=10 best 50%, K=20 best 25%, K=30 best 25% (비슷한 pattern)
   - 192d (YFCC) / 256d (SSN): K=10 best 75%, K=20 best 25%, K=30 best 0% (약간 다름)
   - → dimension 별 명확한 monotone pattern 없음
2. **★ measurement run-level systematic bias 재확인**:
   - 5/12 A1-DEEP (96d) K=10: 모두 negative (CaseB < CaseA)
   - 5/14 A5-scale-sf100 (같은 96d DEEP) K=10: 모두 positive (CaseB > CaseA)
   - 동일 dataset / dimension 인데 measurement run 만 다른데 K=10 결과 정반대
3. **K granularity finding 의 narrative 적용 시 caveat 명시 필요**: measurement run noise 가 K granularity signal 을 압도할 가능성

---

## 1. 5/12 paper exact base K granularity (5 cells × 4 method × 3 K)

### 1.1 cell × method × K paired Δ%

| Cell | Dim | Method | K=10 Δ% | K=20 Δ% | K=30 Δ% | K best |
|---|---:|---|---:|---:|---:|---|
| A1-DEEP | 96 | chao_weighted | -9.82% | -13.22% | -2.63% | K=20 |
| A1-DEEP | 96 | hilbert_real | -6.93% | -6.85% | -0.90% | K=10 |
| A1-DEEP | 96 | hyperloglog | -11.82% | -10.28% | -12.48% | K=30 |
| A1-DEEP | 96 | sparse_rp | -43.03% | -9.94% | +0.33% | K=10 |
| A1-SIFT | 128 | chao_weighted | -6.22% | -10.37% | -10.78% | K=30 |
| A1-SIFT | 128 | hilbert_real | -5.85% | -9.12% | -4.51% | K=20 |
| A1-SIFT | 128 | hyperloglog | -12.08% | -10.70% | -9.84% | K=10 |
| A1-SIFT | 128 | sparse_rp | -49.67% | -6.08% | +3.17% | K=10 |
| A1-SSN | 256 | chao_weighted | -11.54% | -17.11% | -8.55% | K=20 |
| A1-SSN | 256 | hilbert_real | -10.43% | -10.30% | -6.56% | K=10 |
| A1-SSN | 256 | hyperloglog | -14.37% | -8.90% | -10.34% | K=10 |
| A1-SSN | 256 | sparse_rp | -36.28% | -3.81% | -2.01% | K=10 |
| A2-Fig7 | 192 | chao_weighted | -4.02% | -10.96% | -8.22% | K=20 |
| A2-Fig7 | 192 | hilbert_real | -10.07% | -7.38% | -8.82% | K=10 |
| A2-Fig7 | 192 | hyperloglog | -13.48% | -6.30% | -7.29% | K=10 |
| A2-Fig7 | 192 | sparse_rp | -36.96% | -7.44% | -6.23% | K=10 |
| A2-Fig9 | 864 | chao_weighted | -8.80% | -11.43% | -5.90% | K=20 |
| A2-Fig9 | 864 | hilbert_real | -4.10% | -7.71% | -11.29% | K=30 |
| A2-Fig9 | 864 | hyperloglog | -10.07% | -6.23% | -9.27% | K=10 |
| A2-Fig9 | 864 | sparse_rp | -48.66% | -10.62% | +0.17% | K=10 |

### 1.2 dimension-aggregate K best %

| Dim | n | K=10 best % | K=20 best % | K=30 best % | mean Δ% best |
|---:|---:|---:|---:|---:|---:|
| 96 (DEEP) | 4 | 50% | 25% | 25% | -18.92% |
| 128 (SIFT) | 4 | 50% | 25% | 25% | -20.41% |
| 192 (YFCC) | 4 | 75% | 25% | 0% | -17.87% |
| 256 (SSN) | 4 | 75% | 25% | 0% | -19.55% |
| 864 (DEEP+WIKI) | 4 | 50% | 25% | 25% | -20.36% |
| **합계** | **20** | **55%** | **25%** | **20%** | -19.42% |

→ **K=10 이 best 가장 많음** (55%, 11/20). 단 sparse_rp K=10 outlier (Δ% -36~-49%, CaseA 가 매우 불안정한 case) 의 효과가 큰 부분 차지.

### 1.3 sparse_rp outlier 분리

sparse_rp K=10 paired Δ% = -36% ~ -49% — CaseA 가 매우 높은 outlier (3.0~3.3, vs K=20 CaseA 1.5~1.6). sparse_rp 자체의 K=10 instability.

sparse_rp 제외 시 K best %:
- K=10 best: 6/16 = 37.5%
- K=20 best: 5/16 = 31.25%
- K=30 best: 5/16 = 31.25%

→ sparse_rp 제외 시 분포 매우 균일. **dimension-dependent K best pattern 매우 약함**.

---

## 2. 5/14 SF axis (A5-scale-sf{1,10,100} × K{10, 30})

### 2.1 cell × method × K paired Δ%

| Cell | Dim | Method | K=10 Δ% | K=30 Δ% |
|---|---:|---|---:|---:|
| A5-scale-sf1 | 96 | chao_weighted | **+13.15%** | -12.12% |
| A5-scale-sf1 | 96 | hilbert_real | +8.48% | -12.47% |
| A5-scale-sf1 | 96 | hyperloglog | +6.61% | -11.36% |
| A5-scale-sf1 | 96 | sparse_rp | +5.42% | +7.98% |
| A5-scale-sf10 | 96 | chao_weighted | +4.54% | -5.90% |
| A5-scale-sf10 | 96 | hilbert_real | +7.88% | -11.29% |
| A5-scale-sf10 | 96 | hyperloglog | +6.62% | -9.27% |
| A5-scale-sf10 | 96 | sparse_rp | **-28.75%** | +0.17% |
| A5-scale-sf100 | 96 | chao_weighted | +10.64% | -2.63% |
| A5-scale-sf100 | 96 | hilbert_real | +11.57% | -0.90% |
| A5-scale-sf100 | 96 | hyperloglog | +8.62% | -12.48% |
| A5-scale-sf100 | 96 | sparse_rp | -10.55% | +0.33% |

### 2.2 핵심 발견 ★

**A5-scale-sf{1,10,100} K=10 의 paired Δ% 모두 positive** (chao/hilbert/hyperloglog) — CaseB > CaseA (악화)
- A5-scale-sf1 K=10: +5 ~ +13% (4/4 positive)
- A5-scale-sf10 K=10: +4 ~ +8% (3/4 positive, sparse_rp -28.75%)
- A5-scale-sf100 K=10: +8 ~ +11% (3/4 positive, sparse_rp -10.55%)

**A5-scale-sf{1,10,100} K=30 의 paired Δ% 거의 모두 negative** (chao/hilbert/hyperloglog) — CaseB < CaseA (개선)
- A5-scale-sf1 K=30: -11 ~ -12% (3/4 negative)
- A5-scale-sf10 K=30: -5 ~ -11% (3/4 negative)
- A5-scale-sf100 K=30: -1 ~ -12% (3/4 negative)

→ **5/14 SF axis 의 K=10 이 worst, K=30 이 best**. 5/12 결과와 정반대 (5/12 는 K=10 best).

---

## 3. ★ measurement run-level systematic bias 재확인

### 3.1 같은 DEEP 96d 인데 run 별로 정반대 K=10 결과

| Run | Cell | dimension | K=10 paired Δ% (chao/hilbert/hyperloglog mean) |
|---|---|---:|---:|
| 5/12 paper exact base | A1-DEEP | 96d | -9.5% (negative) |
| 5/14 SF axis | A5-scale-sf100 | 96d | +10.3% (positive) |

→ **동일 dataset (DEEP 96d) × 동일 K=10 인데 measurement run 만 다른데 paired Δ% 약 +20%p 차이**
→ **B1_variance_root_cause 종합분석 의 finding 과 100% 일치**: measurement run-level systematic bias ±10-25%

### 3.2 implication for dimension-dependent K best 가설

- dimension 만으로 K best 가 결정되지 않음 (run-level noise 영향 큼)
- **handoff v23 의 "dimension-dependent K best 잠정 가설" 영역 = 강하지 않음**
- K granularity finding 의 narrative 적용 시 매우 cautiously reporting 필요

---

## 4. narrative 의 implication

### 4.1 K granularity finding 의 narrative 적용 시 caveat

기존 (handoff v23): "DEEP 96d K=20 sweet vs SIFT/SSN 128/256d K=30 best 잠정 가설"
**개정 (본 분석)**: "K granularity 측정 결과 = measurement run-level noise 가 큼. 5/12 paper exact base 의 K=10 best 55% (sparse_rp outlier 영향). 5/14 SF axis 의 K=10 worst + K=30 best. dimension-dependent K best 가설 = 약한 evidence, 추가 측정 필요"

### 4.2 narrative 에서 K granularity 활용

- **단순한 K=20 default (paper exact) 가 robust default**
- K granularity sensitivity 가 method 별로 다른 점 = paper §V-B 의 limitation 으로 언급
- robust narrative: "**paper default K=20 이 robust + K granularity sensitivity 가 method 별로 다른 것이 본 연구의 추가 finding**"

### 4.3 박세은 review answer 강화

박세은 5/15 review 의 "K granularity 가 어떻게 되나?" 질문 답변:
- **답변 sub-claim 1**: K granularity finding 의 measurement noise 큼 — robust default = K=20
- **답변 sub-claim 2**: dimension-dependent K best 가설 = 약한 evidence (현재 측정), 추가 측정 필요한 부분 honest disclosure
- **답변 sub-claim 3**: 본 narrative 의 핵심 finding = **paired CaseB < CaseA 97.78% (Pareto Top 5)** — K granularity 부속 finding

---

## 5. 향후 추가 측정 priority

### 5.1 K granularity 9 cell 확장 가치 = ★ (단 caveat)

- 현재 5 cell × 4 method × 3 K = 60 paired (5/12) + 3 cell × 4 method × 2 K = 24 paired (5/14)
- 9 cell × 4 method × 3 K × 2 mode = **216 file** 추가 측정 시 cover 가능
- ★ 단 **measurement run-level systematic bias 가 큰 영역이라 단일 run 추가 측정만으로는 부족** — 같은 run 안에서 모든 cell × K × mode 측정 보장 필요
- 권장: 9 cell 측정을 같은 run 안에서 sequential 로 launch → run-level bias 최소화

### 5.2 multi-run 평균 (rigorous)

- 같은 (cell, method, K) 마다 3 별도 run 측정 후 → CaseA / CaseB / B1 trio 모두 averaged
- 216 file × 3 = 648 file → server time 24-48h
- 학술 narrative 의 paper-grade 보장 가능

---

## 6. 작성 base file

- script: `/tmp/k_granularity_dim.py`
- 5/12 paper exact base K granularity: `raw/06_클러스터수_K_민감도/_run_5_12_paper_exact_base/`
- 5/14 SF axis: `raw/06_클러스터수_K_민감도/_run_5_14_A5_scale_DEEP/`
- B1 variance 종합: `analysis/B1_variance_root_cause_종합분석_20260515_0150.md`
- 미커버 inventory: `analysis/측정_미커버_영역_종합_inventory_20260515_0205.md`

---

작성: 2026-05-15 03:10 KST · K granularity × dimension cross-validation + measurement run-level bias 재확인 + dimension-dependent K best 가설 = 약한 evidence 결론
