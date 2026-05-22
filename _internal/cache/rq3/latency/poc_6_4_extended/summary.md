# Phase 6 §6.4 통계 후속 PoC — **평면 확장 본** 실측 결과 요약

작성: 2026-05-21 KST · 스크립트 `_internal/scripts/stats_poc_6_4_extended.py`

**PoC 평면**: phase2 (DEEP sf=10 sel=0.001 12 cell) + phase3 (DEEP sf=10 sel=0.01·0.1 carry-over 8 cell) + **phase4_extension (단일 5 × sf=1/10 + 다중 2 sf=10 + sf=100 단일 3 부분)**.
§5.4 보고서 본문의 168/180/146 수치는 phase2 만의 부분 평면이며, 본 확장 PoC 는 3 평면 통합에서 평면·dataset·sf 일반화를 검증한다.

## 0. 환각 회피 sanity

- paired 평면 분포: {'phase4_extension': 783, 'phase2': 348, 'phase3': 232}
- legacy carry (phase2+phase3) — anchor=B1 합 = 280 (기대 280) · baseline 합 = 300 (기대 300)
- §5.4 carry (phase2 only) — anchor=B1 = 168 (기대 168) · |g|<0.5 = 146 (기대 146 = 86.9%)
- phase4_extension — paired 행 수 = 783 (0 = 측정 raw 미도착 또는 미적재)
- sanity: PoC 3 model1_cell_condition % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model2_factor_decomp % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model3_no_baseline % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model4_extended — fit 안 됨 (skip)
- plane_comparison: n_pairs 총합 = 1363 = anchor 2 (baseline + B1) × 평면 별 paired

## 1. PoC 1 — plan-level effect size 분층 (legacy carry, 3 평면 통합)

| anchor | plan_recovered | n | small (|g|<0.5) | medium | large (|g|≥0.8) | mean |g| | p_holm<0.05 |
|---|---|--:|--:|--:|--:|--:|--:|
| baseline | True | 646 | 151 (23.4%) | 27 (4.2%) | 468 (72.4%) | 4.733 | 416 (64.4%) |
| baseline | False | 59 | 6 (10.2%) | 2 (3.4%) | 51 (86.4%) | 5.247 | 51 (86.4%) |
| B1 | True | 607 | 560 (92.3%) | 32 (5.3%) | 15 (2.5%) | 0.245 | 13 (2.1%) |
| B1 | False | 51 | 45 (88.2%) | 1 (2.0%) | 5 (9.8%) | 0.450 | 5 (9.8%) |

## 2. PoC 2 — cluster paired bootstrap (B=2,000, cell 단위 resample)

| metric | point | naïve 95% CI | cluster 95% CI | width ratio (cluster/naïve) |
|---|--:|--:|--:|--:|
| mean_median_diff_ms_B1 | 12.240 | [-3.637, 28.882] | [-19.888, 50.733] | 2.172× |
| pct_p_holm_sig_B1 | 2.736 | [1.520, 4.103] | [0.152, 6.079] | 2.294× |

## 3. PoC 3 — variance decomposition (% SS = Type-I 순차 SS · p = Type-III partial, sum-coded contrasts)

n_obs (4 condition) = 2,910 · n_obs (no baseline) = 2,115
R² — 모델 1 (cell × condition) = 0.942 · 모델 2 (factor·4 cond) = 0.833 · 모델 3 (no baseline) = 0.801 · 모델 4 (extended, dataset+sf 추가) = nan

**모델 2 — query·qid·sel + 4 condition + 교호작용** (legacy)

| factor | df | SS(Type-I) | F | p(Type-III) | % SS |
|---|--:|--:|--:|--:|--:|
| C(query_str, Sum) | 3 | 53.952 | 178.512 | 3.902e-162 | 3.10% |
| C(qid_str, Sum) | 2 | 299.665 | 1487.262 | 1.688e-59 | 17.23% |
| C(sel_str, Sum) | 2 | 435.875 | 2163.288 | 0.000e+00 | 25.07% |
| C(cond_str, Sum) | 3 | 429.950 | 1422.586 | 0.000e+00 | 24.72% |
| C(query_str, Sum):C(cond_str, Sum) | 9 | 43.643 | 48.134 | 4.289e-60 | 2.51% |
| C(sel_str, Sum):C(cond_str, Sum) | 6 | 185.335 | 306.612 | 1.590e-304 | 10.66% |
| Residual | 2884 | 290.545 | nan | nan | 16.71% |

**모델 3 — baseline 제외 (B1·CaseB·oracle)** (legacy)

| factor | df | SS(Type-I) | F | p(Type-III) | % SS |
|---|--:|--:|--:|--:|--:|
| C(query_str, Sum) | 3 | 43.087 | 128.851 | 2.227e-74 | 3.68% |
| C(qid_str, Sum) | 2 | 335.731 | 1506.021 | 6.600e-63 | 28.67% |
| C(sel_str, Sum) | 2 | 558.524 | 2505.423 | 0.000e+00 | 47.69% |
| C(cond_str, Sum) | 2 | 0.012 | 0.056 | 9.730e-01 | 0.00% |
| C(query_str, Sum):C(cond_str, Sum) | 6 | 0.011 | 0.016 | 9.999e-01 | 0.00% |
| C(sel_str, Sum):C(cond_str, Sum) | 4 | 0.158 | 0.355 | 8.409e-01 | 0.01% |
| Residual | 2095 | 233.515 | nan | nan | 19.94% |

**★ 모델 4 (extended) — dataset/sf factor 추가** (extended)

_(fit 실패 또는 dataset/sf unique <2 — skip)_

**모델 1 — cell × condition (단순 분해)** (legacy)

| factor | df | SS(Type-I) | F | p(Type-III) | % SS |
|---|--:|--:|--:|--:|--:|
| C(cell_str, Sum) | 52 | 988.120 | 514.851 | 0.000e+00 | 56.81% |
| C(cond_str, Sum) | 3 | 394.383 | 3561.819 | 0.000e+00 | 22.68% |
| C(cell_str, Sum):C(cond_str, Sum) | 156 | 256.460 | 44.542 | 0.000e+00 | 14.75% |
| Residual | 2716 | 100.243 | nan | nan | 5.76% |

## 4. ★ 신규 — 평면 비교 표 (phase2 vs phase3 vs phase4_extension)

| phase | anchor | n_pairs | plan_recovery_pct | mean |g| | small% | medium% | large% | p_holm<0.05% |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| phase2 | baseline | 180 | 92.8% | 13.054 | 0.0% | 0.0% | 100.0% | 100.0% |
| phase2 | B1 | 168 | 95.2% | 0.341 | 86.9% | 4.8% | 8.3% | 7.7% |
| phase3 | baseline | 120 | 90.8% | 2.177 | 47.5% | 2.5% | 50.0% | 50.0% |
| phase3 | B1 | 112 | 90.2% | 0.329 | 90.2% | 5.4% | 4.5% | 4.5% |
| phase4_extension | baseline | 405 | 91.4% | 1.868 | 24.7% | 6.4% | 68.9% | 56.0% |
| phase4_extension | B1 | 378 | 91.5% | 0.205 | 94.7% | 5.0% | 0.3% | 0.0% |

## 5. ★ 신규 — dataset × sf 비교 표 (anchor=B1)

| dataset | sf | n_pairs | plan_recovery_pct | mean |g| | large% | p_holm<0.05% | note |
|---|---|--:|--:|--:|--:|--:|---|
| DEEP | 10 | 280 | 93.2% | 0.336 | 6.8% | 6.4% |  |
| SIFT | 10 | 154 | 94.2% | 0.200 | 0.0% | 0.0% |  |
| SSN | 10 | 112 | 92.9% | 0.227 | 0.9% | 0.0% |  |
| YFCC | 10 | 112 | 86.6% | 0.190 | 0.0% | 0.0% |  |

## 6. ★ 신규 — sf scaling 표 (sf=1·10·100 condition 효과 변화, anchor=B1)

| sf | n_datasets | n_pairs | plan_recovery_pct | mean |g| | large% | p_holm<0.05% |
|---|--:|--:|--:|--:|--:|--:|
| 10 | 4 | 658 | 92.2% | 0.261 | 3.0% | 2.7% |

## 7. ★ 신규 — sf=100 censoring (statement_timeout 180s 도달 비율)

_(sf=100 raw 미도착 또는 censored=0 — 측정 후 갱신)_

## 8. 평면 일반화 결론 (template — 측정 결과 도착 후 갱신)

- **DEEP sf=10 단일 평면 결론 (carry)**: 94.9% plan 회복 · 86.9% small effect · model3 condition % SS = 0.00% (p=0.866) → latency 동등성 입증.
- **평면 확장 (phase4_extension) 일반화**: (측정 도착 후) 단일 5 dataset · sf=1·10 + 다중 2 + sf=100 부분에서 동일 효과 입증 또는 조건부 효과 (sf×condition 또는 dataset×condition 교호작용 검증).
- **honest exception**: DEEP sf=1 plan-invariant · WIKI/YFCC sf=100 미적재 · DEEP+CC3M 4건 한계 · sf=100 censoring 비율 — 각각 별도 paragraph.
