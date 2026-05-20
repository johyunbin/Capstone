# Phase 6 §6.4 통계 후속 PoC — 실측 결과 요약

작성: 2026-05-20 KST · 스크립트 `_internal/scripts/stats_poc_6_4.py`

**PoC 평면**: phase2 (sel=0.001, 12 cell × qid 3) + phase3 (sel=0.01·0.1 carry-over, 4 query × qid=0 × 2 sel = 8 cell) = **20 cell**.
§5.4 보고서 본문의 168/180/146 수치는 phase2 만의 부분 평면이며, PoC 는 phase3 확장까지 포함한 280/300 평면에서 수행한다.

## PoC 1 — plan-level effect size 분층

anchor=B1 280 비교의 Hedges' g 분포를 plan 회복 여부로 분층 (anchor=baseline 300 비교 동시 보고):

| anchor | plan_recovered | n | small (|g|<0.5) | medium | large (|g|≥0.8) | mean |g| | p_holm<0.05 |
|---|---|--:|--:|--:|--:|--:|--:|
| baseline | True | 276 | 57 (20.7%) | 3 (1.1%) | 216 (78.3%) | 8.611 | 216 (78.3%) |
| baseline | False | 24 | 0 (0.0%) | 0 (0.0%) | 24 (100.0%) | 9.763 | 24 (100.0%) |
| B1 | True | 261 | 233 (89.3%) | 14 (5.4%) | 14 (5.4%) | 0.298 | 13 (5.0%) |
| B1 | False | 19 | 14 (73.7%) | 0 (0.0%) | 5 (26.3%) | 0.858 | 5 (26.3%) |

## PoC 2 — cluster paired bootstrap (B=2,000, cell 단위 resample)

| metric | point | naïve 95% CI | cluster 95% CI | width ratio (cluster/naïve) |
|---|--:|--:|--:|--:|
| mean_median_diff_ms_B1 | 7.542 | [-4.141, 20.589] | [-24.996, 40.349] | 2.642× |
| pct_p_holm_sig_B1 | 6.429 | [3.571, 9.286] | [0.714, 13.929] | 2.312× |

## PoC 3 — variance decomposition (Type-III SS, sum-coded contrasts)

n_obs (4 condition) = 4,800 · n_obs (no baseline) = 4,500
R² — 모델 1 (cell × condition) = 0.959 · 모델 2 (factor·4 cond) = 0.937 · 모델 3 (no baseline·B1·CaseB·oracle) = 0.927

**모델 2 — query·qid·sel·condition (4 levels) + 교호작용**

| factor | df | SS | F | p | % SS |
|---|--:|--:|--:|--:|--:|
| C(query_str, Sum) | 3 | 57.463 | 613.211 | 0.000e+00 | 7.50% |
| C(qid_str, Sum) | 2 | 1.815 | 29.048 | 2.890e-13 | 0.24% |
| C(sel_str, Sum) | 2 | 256.173 | 4100.573 | 0.000e+00 | 33.42% |
| C(cond_str, Sum) | 3 | 157.624 | 1682.071 | 0.000e+00 | 20.56% |
| C(query_str, Sum):C(cond_str, Sum) | 9 | 17.146 | 60.991 | 3.037e-106 | 2.24% |
| C(sel_str, Sum):C(cond_str, Sum) | 6 | 127.291 | 679.183 | 0.000e+00 | 16.60% |
| Residual | 4774 | 149.122 | nan | nan | 19.45% |

**모델 3 — baseline 제외 (B1·CaseB·oracle 3 levels) — §5.4 의 B1↔CaseB↔oracle 동등성 직접 검증**

| factor | df | SS | F | p | % SS |
|---|--:|--:|--:|--:|--:|
| C(query_str, Sum) | 3 | 26.883 | 283.604 | 1.496e-168 | 4.61% |
| C(qid_str, Sum) | 2 | 1.689 | 26.734 | 2.872e-12 | 0.29% |
| C(sel_str, Sum) | 2 | 412.842 | 6533.044 | 0.000e+00 | 70.78% |
| C(cond_str, Sum) | 2 | 0.009 | 0.144 | 8.660e-01 | 0.00% |
| C(query_str, Sum):C(cond_str, Sum) | 6 | 0.173 | 0.911 | 4.854e-01 | 0.03% |
| C(sel_str, Sum):C(cond_str, Sum) | 4 | 0.131 | 1.038 | 3.859e-01 | 0.02% |
| Residual | 4480 | 141.552 | nan | nan | 24.27% |

**모델 1 — cell × condition (between-cell vs between-condition 단순 분해)**

| factor | df | SS | F | p | % SS |
|---|--:|--:|--:|--:|--:|
| C(cell_str, Sum) | 19 | 379.506 | 972.238 | 0.000e+00 | 37.13% |
| C(cond_str, Sum) | 3 | 393.944 | 6391.752 | 0.000e+00 | 38.55% |
| C(cell_str, Sum):C(cond_str, Sum) | 57 | 151.552 | 129.418 | 0.000e+00 | 14.83% |
| Residual | 4720 | 96.969 | nan | nan | 9.49% |

## 환각 회피 sanity

- PoC plane (phase2+phase3) — anchor=B1 합 = 280 (기대 280) · anchor=baseline 합 = 300 (기대 300)
- §5.4 합치 (phase2 only) — anchor=B1 = 168 (기대 168) · baseline = 180 (기대 180)
- §5.4 합치 (phase2 only) — anchor=B1 small (|g|<0.5) = 146 (기대 146 = 86.9%) · baseline large (|g|≥0.8) = 180 (기대 180 = 100%)
- sanity: PoC 3 model1 % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model2 % SS 합 = 100.00% (기대 100.0%)
- sanity: PoC 3 model3 % SS 합 = 100.00% (기대 100.0%)
- key finding: model3 (no baseline) condition % SS = 0.00% — §5.4 latency 동등성 정량
- sanity: PoC 2 cluster/naïve width ratio — mean_diff=2.642, %sig=2.312
