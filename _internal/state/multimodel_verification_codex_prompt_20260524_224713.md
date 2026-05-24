# Codex (xhigh) 적대 검증 prompt — 속도는벡터 storyline v3 정정 정본 수치 검증

> 작성: 2026-05-24 22:47 KST · target: GPT-5.5 xhigh effort
> 검증 결과 critical: 5/27 최종 발표 슬라이드 deck + 채림님(BDAI 연구실) 보고용

## 0. 임무

당신은 **데이터·통계 정합성을 적대적으로 검증하는 평가자**다. 연세대 캡스톤 팀 "속도는벡터" 의 정본 측정 수치와 정정 항목의 정확성을 **0 환각·0 오차**로 검증한다. 의심·결함·불일치 모두 priority 분류 + evidence 명시.

## 1. 본 연구 framing (검증 context)

- **목적**: Exqutor 논문 (arXiv:2512.09695v2) §V-B Adaptive Sampling 의 **표본 선택 단계 하나만** 통제 변인으로 controlled verification
- **개입**: 무작위 베르누이 → 분포 인지 층화 표본 추출 (paper §V-B momentum 식 1-6 · 표본 예산 N=385 carry, 표본 선택 방식만 변경)
- **세 mode (3-way matched)**: B1 (대조군, 베르누이) · CaseA (음성 대조군, 단독 대체) · CaseB (결합, 두 추정값 산술 평균)
- **사전 등록 통제군** (5/23 v14 ~ 5/24 v16): CaseC (dual-Bernoulli ensemble) — 분포 인지 효과 vs 평균 효과 분리 입증용
- **engine 적용**: 패치된 PostgreSQL pgvector 에 카디널리티 inject

## 2. 정본 측정 데이터 (raw 검증 대상)

### 2.1 v13 paired_delta_v13.parquet (4,524 row = 1,508 cell × 3 comparison)

**mode 별 qe_trim** (1,508 cell B1·CaseA·CaseB matched):

| mode | n | mean | median | std | min | max |
|---|--:|--:|--:|--:|--:|--:|
| B1 | 1508 | 1.4582 | 1.5616 | 0.1925 | 1.1539 | 1.6560 |
| CaseA | 1508 | 1.6359 | 1.5699 | 2.7976 | 1.1357 | 96.7868 |
| CaseB | 1508 | 1.4019 | 1.4492 | 0.4666 | 1.1017 | 15.7658 |

**3-way paired Δ% (CaseB_vs_B1 anchor)**:

| 비교 | n | better% (Δ%<0) | mean Δ% | median Δ% | 유의% | δlarge% |
|---|--:|--:|--:|--:|--:|--:|
| CaseB_vs_B1 | 1508 | 1344 / 1508 = **89.1%** | **−3.06%** | **−4.38%** | 65.3% | 72.1% |
| CaseA_vs_B1 | 1508 | 531 / 1508 = **35.2%** | **+12.90%** | +1.09% | 6.8% | 13.5% |
| CaseA_vs_CaseB | 1508 | 53 / 1508 = 3.5% | +13.92% | +7.02% | 0.0% | 1.3% |

**측정 portfolio (25 cell × 16 method × 3 sel × 3 K 구조화)**:
- K=20: 1124 (74.5%) · K=10: 192 (12.7%) · K=30: 192 (12.7%)
- sel=0.01: 628 (41.6%) · sel=0.001: 448 (29.7%) · sel=0.1: 432 (28.6%)
- Type 1·2·3·4a·4b: 272·224·464·368·180 = 1,508
- A2-Fig8 (DEEP+CC3M sf=10): 4 method 측정 (희소 cell, 보고서 §4.7 carry "단독 finding 인용 X")
- A4-sel 희소 cell carry

### 2.2 v14 aggregated_v14.parquet (사전 등록 통제군, 9 cell)

- mode=CaseC dual-Bernoulli ensemble (paper §V-B verbatim, two independent AdaptiveState)
- 9 cell × sel=0.01 (A4-sel만 0.001) · K=20 default
- mean qe_trim = **1.3729** (range [1.3452, 1.3948])
- 동일 9 cell v13 베이스라인 평균 = **1.5843**, 결합 평균 = **1.4734**
- 9/9 cell 모두 CaseC < CaseB (통제군이 결합보다 정확)
- Δ% vs B1 = **−13.31%**, Δ% vs CaseB = **−6.74%**

### 2.3 v16 paper_exact_v16_full95_paired.parquet (95 tuple 전수)

- 25 cell × 3 sel × 3 K 평면의 v13 paired row 실재 95 (cell × sel × K) tuple
- BLOCKER E fix 후 rng stream 완전 분리 (보고서 §4.6.1 carry):
  - rng (method 전용) = default_rng(20260520)
  - rng_b1 = default_rng(20260520 + 4_000_000)
  - rng_caseC_a = default_rng(20260520 + 2_000_000)
  - rng_caseC_b = default_rng(20260520 + 3_000_000)
- paper §V-B verbatim all_vecs random sample 경로 (strata-independent)

**v16 모든 mode statistic (95 tuple)**:

| mode | n | mean | median |
|---|--:|--:|--:|
| qe_trim_B1 | 95 | 1.4595 | 1.5740 |
| qe_trim_CaseA | 95 | 1.6351 | 1.6182 |
| qe_trim_CaseB | 95 | 1.4022 | 1.4725 |
| qe_trim_CaseC_v16 | 95 | **1.3060** | 1.3663 |

**v16 paired Δ%**:
- CaseC vs B1: 95/95 = **100% better**, mean Δ% = −10.05%, median Δ% = **−11.32%**
- CaseC vs CaseB: 95/95 = **100% better**, mean Δ% = −6.08%, median Δ% = **−5.98%**

### 2.4 Engine latency raw (3 평면 56 cell)

**phase2 (DEEP sf=10 sel=0.001, 12 cell × 16 variant × 15 rep = 2,880 측정)**:

| variant | 12 cell exec_ms_median 평균 | 12 cell mean gain (baseline/variant) | median gain |
|---|--:|--:|--:|
| baseline | 5,677.7 ms | 1.0× (기준) | — |
| B1 | 977.6 ms | **5.772×** | 6.374× |
| CaseB_mean (13 method) | 983.5 ms | **5.703×** | 6.378× |
| oracle | 992.3 ms | **5.651×** | 6.223× |

**보고서 §5.2 verbatim 표 5-1 trim mean**:
- B1 12 cell 평균: 969 ms · oracle: 957 ms
- 12 cell oracle gain 평균: **5.67×** (range 2.93× ~ 7.40×, Q3 7배대 / Q9 2배대)

**Plan 회복 (B1 anchor)**:
- B1 정답 plan 회복: **7/12 = 58.3%** (cell 단위, qid 0/4·1: 4/4·2: 3/4)
- CaseB 13 method 정답 plan 회복: **148/156 = 94.9%**
- 결합 실패 8건 모두 Q3

**paired Wilcoxon + Holm 보정 (anchor=B1, 168 비교)**:
- p_holm<0.05: **13/168 = 7.7%** 만 유의
- Hedges' g small (|g|<0.5): **146/168 = 86.9%**
- Hedges' g large (|g|≥0.8): 14/168 = 8.3%
- Cliff's δ large: 29/168 = 17.3%
- bootstrap CI ∌ 0: 44/168 = 26.2%

**paired Wilcoxon (anchor=baseline, 180 비교)**:
- p_holm<0.05: **180/180 = 100%**
- Hedges' g large: 180/180 = 100%
- Cliff's δ large: 180/180 = 100%

**Variance decomposition** (두 평면):

(1) poc_6_4 (legacy, 20 cell, 580 paired, n=4500, R²=0.927):
- condition (B1·CaseB·oracle) % SS = **0.00%**, p_typ3 = **0.866**
- sel main effect 70.8% 지배

(2) poc_6_4_extended (3 평면 통합, 56 cell, n=2250, R²=0.827):
- factor 별 pct_ss / p_typ3:
  - sel: 49.11% / 0
  - qid: 28.05% / 1.80e-65
  - query: 5.50% / 3.45e-96
  - **cond (B1·CaseB·oracle)**: **0.000773%** / **p=0.9452**
  - residual: 17.33%

**plan_level_effect_size.csv (3 평면 통합, 700 paired B1 anchor)**:
- plan_recovered=True: 649 paired = **92.7%**
- plan_recovered=False: 51 paired = **7.3%**

**dataset_comparison.csv (B1 anchor, sf=10)**:
- DEEP: 280 paired, 93.21% recovery, mean |g| 0.336
- SIFT: 168 paired, 94.64% recovery, mean |g| 0.203
- SSN: 126 paired, 93.65% recovery
- YFCC: 126 paired, 88.10% recovery

**4-way 확장 (5/24 04:03, 12 cell × 18 variant × 15 rep, 보고서 §5.6)**:
- CaseC vs B1 paired: mean Δ% = **+0.30%**, median +0.11%, std 1.22, 5/12 faster
- CaseA/mean vs B1 paired: mean Δ% = −0.38%, median −0.25%
- oracle vs B1 paired: mean Δ% = −0.44%
- 17 inject variant 모두 |Δ%| ≤ **1.12%**
- baseline vs B1: mean +**409.7%**, median +477.5% (4-5× 느림)
- injection_fired: 17 × 12 = **204/204 = 100%**

## 3. 검증 임무 (적대적 cross-check)

다음 6 갈래에 대해 priority 0 (critical) · 1 (major) · 2 (minor) 분류 + evidence 명시:

### Task A — 수치 상호 일치성
1. v13 B1 mean=1.4582 (1508 cell) vs v16 qe_trim_B1 mean=1.4595 (95 paired tuple) — paired subset 정합?
2. v13 §4.2.1 9 cell B1 평균 1.5843 vs v13 전체 mean 1.4582 — cell subset 차이 정합?
3. 두 variance decomp 평면의 p_typ3 0.866 (legacy) vs 0.945 (extended) — 두 평면 모두 valid?
4. plan 92.7%/7.3% (3 평면 700 paired) vs phase2 cell 단위 7/12=58.3% (B1) — 두 metric 호환?
5. paired Δ% +0.30% (4-way 5/24) vs +0.11% median 정합?

### Task B — 통계 검정 정합성
1. paired Wilcoxon + Holm 보정 + Hedges' g (n=15) + Cliff's δ + cluster paired bootstrap (B=2000) 절차 정확?
2. trial=10·n_queries=1000 → 한쪽 꼬리 최소 p값 1/1024≈0.001 — 통계 검정 floor 적용 정합?
3. Type-III SS 분해 % SS 정의 (Type-I 순차 SS·p Type-III partial 혼용) 정합?
4. cluster paired bootstrap CI 가 naïve CI 대비 너비 ratio 2.081× / 2.500× — within-cell 상관 보정 효과 정합?

### Task C — 측정 평면 완전성
1. 1,508 cell = 25 cell × 16 method × 3 sel × 3 K 의도 portfolio vs 의도 max 3,600 측정 (42% 의도 측정) — 통계 일반화 정합?
2. A2-Fig8 4/16 method + A4-sel 희소 cell — 의도된 부분 측정 의 통계적 영향?
3. engine 평면 56 cell (DEEP·SIFT·SSN·YFCC sf=10) 의 sf=1·sf=100 미측정 — Future Work carry 정합?
4. WIKI sf=10 engine timeout (768d SeqScan) 의 honest exception 정합?

### Task D — 89% 우위 메커니즘 narrative
1. v14 9 cell CaseC=1.3729 < v13 9 cell CaseB=1.4734 → "method (분포 인지) 가 평균 효과 위에 음의 잡음 추가" 정합?
2. v16 95 tuple CaseC=1.3060 mean 의 두 효과 분리 (앙상블 분산 감소 + 분포 인지 검정) 정합 — 보고서 §4.7 Gemini Deep Think 적대 검증 후 carry?
3. paired Δ% vs B1 −11.32% (v16) 의 (a) 분산 감소 효과 + (b) method 검정 의 합 해석 정합?
4. v16 CaseC K-independent 설계 (paper §V-B verbatim all_vecs) 와 v13 B1·CaseB 의 K-dependence 비대칭 비교 fairness 한계 정합?

### Task E — 잠재적 결함·환각 발견
1. storyline v3 의 잘못된 carry (B1=1.944·1.984/CaseB=1.477 ❌, 가속 4.43×/4.46×/4.54× ❌, 24% 더 정확 ❌) 정정 후 잔여 결함?
2. BLOCKER E rng stream fix (4 generator 분리) 후 v16 95 tuple 재현성 정합?
3. measure_case_c·gen_latency_estimates·measure_offline_casec_portfolio 의 3 carry item (query-sel miss raise, concat prefix mismatch, DEFAULT_PORTFOLIO 18 vs 25) — v16 95 tuple 측정 영향?
4. method 명칭 정직성 (hilbert_real=PCA 2D lex sort alias, sparse_rp=Li-Hastie-Church 2006) 의 narrative 영향?

### Task F — slide·세은님 자료 정정 권고
1. storyline v3 정정 후 slide 9 trim mean 표시: 1.4582 → 1.4019 ≈ 3.86% 더 정확 vs median 1.5616 → 1.4492 ≈ 7.20% 더 정확 — 어느 metric 권고?
2. slide 10 가속 배수: phase2 median 직접 5.77×/5.70×/5.65× vs 보고서 §5.2 trim mean 5.67× — 어느 metric 권고?
3. slide 10 variance p-value: poc_6_4 legacy 0.866 vs extended 0.945 — 어느 평면 권고?
4. 채림님 전달용 자료에 들어가야 할 추가 검증 수치 권고?

## 4. 응답 형식

```
# 검증 결과

## Summary
- 신뢰도 점수 (0-100):
- Priority 0 (critical) 발견: N건
- Priority 1 (major) 발견: N건
- Priority 2 (minor) 발견: N건
- pass / conditional pass / fail 판정:

## Priority 0 발견 사항
1. [발견]
   - Evidence:
   - Affected: (storyline·세은님 자료·슬라이드·보고서 영향 항목)
   - 권고:

(이하 동일 형식)

## Priority 1 / Priority 2 동일

## Task A-F 별 세부 검증 결과

## 권고 사항 종합
```

언어: 한국어 (수치·통계 용어는 영문/숫자 그대로).
응답 길이: 자세히 (1000-3000 자), 발견된 모든 결함·의심 명시. 신뢰도 점수는 cell·method 의 정합성·통계 검정 정확성·narrative 일관성을 종합 평가.
