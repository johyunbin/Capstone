# Phase 6 §6.4 통계 후속 PoC — **평면 확장 본** 실측 결과 요약

작성: 2026-05-21 KST · 스크립트 `_internal/scripts/stats_poc_6_4_extended.py`

**PoC 평면**: phase2 (DEEP sf=10 sel=0.001 12 cell) + phase3 (DEEP sf=10 sel=0.01·0.1 carry-over 8 cell) + **phase4_extension (단일 5 × sf=1/10 + 다중 2 sf=10 + sf=100 단일 3 부분)**.
§5.4 보고서 본문의 168/180/146 수치는 phase2 만의 부분 평면이며, 본 확장 PoC 는 3 평면 통합에서 평면·dataset·sf 일반화를 검증한다.

## 0. 환각 회피 sanity

- paired 평면 분포: {'phase4_extension': 870, 'phase2': 348, 'phase3': 232}
- legacy carry (phase2+phase3) — anchor=B1 합 = 280 (기대 280) · baseline 합 = 300 (기대 300)
- §5.4 carry (phase2 only) — anchor=B1 = 168 (기대 168) · |g|<0.5 = 146 (기대 146 = 86.9%)
- phase4_extension — paired 행 수 = 870 (0 = 측정 raw 미도착 또는 미적재)
- sanity: PoC 3 model1_cell_condition % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model2_factor_decomp % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model3_no_baseline % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model4_extended — fit 안 됨 (skip)
- plane_comparison: n_pairs 총합 = 1450 = anchor 2 (baseline + B1) × 평면 별 paired

## 1. PoC 1 — plan-level effect size 분층 (legacy carry, 3 평면 통합)

| anchor | plan_recovered | n | small (|g|<0.5) | medium | large (|g|≥0.8) | mean |g| | p_holm<0.05 |
|---|---|--:|--:|--:|--:|--:|--:|
| baseline | True | 691 | 172 (24.9%) | 40 (5.8%) | 479 (69.3%) | 4.462 | 416 (60.2%) |
| baseline | False | 59 | 6 (10.2%) | 2 (3.4%) | 51 (86.4%) | 5.247 | 51 (86.4%) |
| B1 | True | 649 | 598 (92.1%) | 36 (5.5%) | 15 (2.3%) | 0.245 | 13 (2.0%) |
| B1 | False | 51 | 45 (88.2%) | 1 (2.0%) | 5 (9.8%) | 0.450 | 5 (9.8%) |

## 2. PoC 2 — cluster paired bootstrap (B=2,000, cell 단위 resample)

| metric | point | naïve 95% CI | cluster 95% CI | width ratio (cluster/naïve) |
|---|--:|--:|--:|--:|
| mean_median_diff_ms_B1 | 14.506 | [-1.069, 30.994] | [-16.806, 49.925] | 2.081× |
| pct_p_holm_sig_B1 | 2.571 | [1.429, 3.714] | [0.143, 5.857] | 2.500× |

## 3. PoC 3 — variance decomposition (% SS = Type-I 순차 SS · p = Type-III partial, sum-coded contrasts)

n_obs (4 condition) = 3,090 · n_obs (no baseline) = 2,250
R² — 모델 1 (cell × condition) = 0.946 · 모델 2 (factor·4 cond) = 0.845 · 모델 3 (no baseline) = 0.827 · 모델 4 (extended, dataset+sf 추가) = nan

**모델 2 — query·qid·sel + 4 condition + 교호작용** (legacy)

| factor | df | SS(Type-I) | F | p(Type-III) | % SS |
|---|--:|--:|--:|--:|--:|
| C(query_str, Sum) | 3 | 94.550 | 326.192 | 6.584e-195 | 4.95% |
| C(qid_str, Sum) | 2 | 339.493 | 1756.841 | 9.936e-62 | 17.77% |
| C(sel_str, Sum) | 2 | 521.584 | 2699.143 | 0.000e+00 | 27.31% |
| C(cond_str, Sum) | 3 | 402.041 | 1387.013 | 0.000e+00 | 21.05% |
| C(query_str, Sum):C(cond_str, Sum) | 9 | 32.514 | 37.391 | 8.075e-61 | 1.70% |
| C(sel_str, Sum):C(cond_str, Sum) | 6 | 223.818 | 386.079 | 0.000e+00 | 11.72% |
| Residual | 3064 | 296.045 | nan | nan | 15.50% |

**모델 3 — baseline 제외 (B1·CaseB·oracle)** (legacy)

| factor | df | SS(Type-I) | F | p(Type-III) | % SS |
|---|--:|--:|--:|--:|--:|
| C(query_str, Sum) | 3 | 75.474 | 236.081 | 3.451e-96 | 5.50% |
| C(qid_str, Sum) | 2 | 384.618 | 1804.619 | 1.798e-65 | 28.05% |
| C(sel_str, Sum) | 2 | 673.437 | 3159.750 | 0.000e+00 | 49.11% |
| C(cond_str, Sum) | 2 | 0.011 | 0.050 | 9.452e-01 | 0.00% |
| C(query_str, Sum):C(cond_str, Sum) | 6 | 0.013 | 0.020 | 1.000e+00 | 0.00% |
| C(sel_str, Sum):C(cond_str, Sum) | 4 | 0.151 | 0.354 | 8.416e-01 | 0.01% |
| Residual | 2230 | 237.640 | nan | nan | 17.33% |

**★ 모델 4 (extended) — dataset/sf factor 추가** (extended)

_(fit 실패 또는 dataset/sf unique <2 — skip)_

**모델 1 — cell × condition (단순 분해)** (legacy)

| factor | df | SS(Type-I) | F | p(Type-III) | % SS |
|---|--:|--:|--:|--:|--:|
| C(cell_str, Sum) | 55 | 1157.044 | 593.222 | 9.272e-01 | 60.57% |
| C(cond_str, Sum) | 3 | 367.045 | 3450.067 | 9.272e-01 | 19.21% |
| C(cell_str, Sum):C(cond_str, Sum) | 165 | 283.934 | 48.525 | 9.272e-01 | 14.86% |
| Residual | 2884 | 102.274 | nan | nan | 5.35% |

## 4. ★ 신규 — 평면 비교 표 (phase2 vs phase3 vs phase4_extension)

| phase | anchor | n_pairs | plan_recovery_pct | mean |g| | small% | medium% | large% | p_holm<0.05% |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| phase2 | baseline | 180 | 92.8% | 13.054 | 0.0% | 0.0% | 100.0% | 100.0% |
| phase2 | B1 | 168 | 95.2% | 0.341 | 86.9% | 4.8% | 8.3% | 7.7% |
| phase3 | baseline | 120 | 90.8% | 2.177 | 47.5% | 2.5% | 50.0% | 50.0% |
| phase3 | B1 | 112 | 90.2% | 0.329 | 90.2% | 5.4% | 4.5% | 4.5% |
| phase4_extension | baseline | 450 | 92.2% | 1.737 | 26.9% | 8.7% | 64.4% | 50.4% |
| phase4_extension | B1 | 420 | 92.4% | 0.209 | 94.3% | 5.5% | 0.2% | 0.0% |

## 5. ★ 신규 — dataset × sf 비교 표 (anchor=B1)

| dataset | sf | n_pairs | plan_recovery_pct | mean |g| | large% | p_holm<0.05% | note |
|---|---|--:|--:|--:|--:|--:|---|
| DEEP | 10 | 280 | 93.2% | 0.336 | 6.8% | 6.4% |  |
| SIFT | 10 | 168 | 94.6% | 0.203 | 0.0% | 0.0% |  |
| SSN | 10 | 126 | 93.7% | 0.226 | 0.8% | 0.0% |  |
| YFCC | 10 | 126 | 88.1% | 0.199 | 0.0% | 0.0% |  |

## 6. ★ 신규 — sf scaling 표 (sf=1·10·100 condition 효과 변화, anchor=B1)

| sf | n_datasets | n_pairs | plan_recovery_pct | mean |g| | large% | p_holm<0.05% |
|---|--:|--:|--:|--:|--:|--:|
| 10 | 4 | 700 | 92.7% | 0.260 | 2.9% | 2.6% |

## 7. ★ 신규 — sf=100 censoring (statement_timeout 180s 도달 비율)

_(sf=100 raw 미도착 또는 censored=0 — 측정 후 갱신)_

## 8. 평면 일반화 결론 (template — 측정 결과 도착 후 갱신)

- **DEEP sf=10 단일 평면 결론 (carry)**: 94.9% plan 회복 · 86.9% small effect · model3 condition % SS = 0.00% (p=0.866) → latency 동등성 입증.
- **평면 확장 (phase4_extension) 일반화**: (측정 도착 후) 단일 5 dataset · sf=1·10 + 다중 2 + sf=100 부분에서 동일 효과 입증 또는 조건부 효과 (sf×condition 또는 dataset×condition 교호작용 검증).
- **honest exception**: DEEP sf=1 plan-invariant · WIKI/YFCC sf=100 미적재 · DEEP+CC3M 4건 한계 · sf=100 censoring 비율 — 각각 별도 paragraph.
