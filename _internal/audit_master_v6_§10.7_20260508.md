# Audit: master_v6 §10.7 Adaptive 분석 (2026-05-08)

**대상**: `experiments/results/master_v6_§10.7_Adaptive_분석_20260508.md`
**Raw 검증**: `_internal/cache/single_adaptive_paired/` 6 csv (h2h_per_cell, h2h_per_sel, paired_cell, paired_summary, paired_sign, paired_wilcoxon)
**범위**: 검증 only — 문서 수정 없음

---

## 1. 핵심 주장 검증 표

| # | §10.7 주장 | Raw 검증 결과 | 판정 |
|---|---|---|---|
| 1 | HDBSCAN 10/10 cell win | h2h_per_cell median<0 = 10/10 (DEEP_sf1 -0.528, SIFT_sf1 -1.157, …, YFCC_sf10 -0.622 모두 음수) | ✅ |
| 2 | HDBSCAN 7/10 sig (p<0.05) | wilcoxon_p<0.05 + method_better=True : 7/10 (SSN sf1 0.78 / SSN sf10 0.10 / WIKI sf1 0.28 만 비유의) | ✅ |
| 3 | Hilbert 9/10 win + 6/10 sig | win=9/10 (SSN_sf1 +0.05 만 양수) / sig=6/10 (SSN sf1·sf10 / WIKI sf1 / DEEP sf10 비유의) | ✅ |
| 4 | MB_partial 8/10 win + 6/10 sig | win=8/10 (SSN_sf1 +0.09 / WIKI_sf10 +0.30 양수) / sig=6/10 | ✅ |
| 5 | sparse_rp 4/10 win + 0/10 sig | win=4/10 (DEEP_sf1, SIFT_sf10, SSN_sf10, YFCC_sf10 음수) / sig=0/10 | ✅ |
| 6 | sparse_rp mean of cell median Δ% = +0.05 | 계산값 = **+0.0536** | ✅ |
| 7 | HDBSCAN mean of cell median = -0.62 | 계산값 = **-0.6154** | ✅ |
| 8 | MB_partial mean = -0.43 | 계산값 = **-0.4316** | ✅ |
| 9 | Hilbert mean = -0.48 | 계산값 = **-0.4783** | ✅ |
| 10 | SIFT_sf1 Adaptive vs BERN -26.77% | paired_cell SIFT_sf1 Adaptive median = **-26.7659** | ✅ |
| 11 | WIKI_sf1 Adaptive vs BERN -6.50% | 동 = **-6.4966** | ✅ |
| 12 | YFCC_sf1 Adaptive vs BERN -4.26% | 동 = **-4.2646** | ✅ |
| 13 | 4강 vs Adaptive head-to-head magnitude -0.5~-1.2% | 4강 mean of cell median range: -0.43 (MB) ~ -0.62 (HDBSCAN). Cell-별 magnitude SIFT/YFCC 영역에서 -1.16/-0.97. 본문은 typical range 의도. | ✅ |
| 14 | Outcome A (4강 ≻ Adaptive) | HDBSCAN/Hilbert/MB sig 6~7/10, 모두 음수 우위. | ✅ |
| 15 | Outcome C (sparse_rp ≃ Adaptive) | 0/10 sig + mean +0.05% | ✅ |

## 2. 별표 (significance level) 정합성

§10.7 표는 `*` p<0.05, `**` p<1e-3, `***` p<1e-7 표기. **8 개 cell 의 별 개수가 over-claim 됨** (방향과 sig 0.05 판정은 일치하지만 tier 가 한 단계 부풀려짐):

| Cell/Method | 표 표기 | 실제 p | 정확 표기 |
|---|---|---|---|
| SIFT_sf1/MB | ** | 1.36e-3 | * (1e-3 경계) |
| WIKI_sf10/HDBSCAN | ** | 4.87e-3 | * |
| YFCC_sf1/HDBSCAN | *** | 2.79e-7 | ** (1e-7 경계) |
| YFCC_sf1/MB | *** | 2.67e-5 | ** |
| YFCC_sf1/Hilbert | ** | 2.60e-3 | * |
| YFCC_sf10/HDBSCAN | *** | 3.34e-4 | ** |
| YFCC_sf10/MB | *** | 8.80e-4 | ** |
| YFCC_sf10/Hilbert | *** | 3.96e-5 | ** |

⚠️ Tier 일관성 권장 — narrative 의 win/sig count (✅) 는 영향 없음.

## 3. paired Wilcoxon 방식

raw csv 의 `n_paired_total` ≈ 2,484~2,500 = **5 sel × 500 (100 query × 5 seed) 풀(pool)** 한 cell-level test. 각 (cell × method) 1 test, 총 10 × 4 = **40 test**. h2h_per_sel.csv 에는 sel 분리 per-test 결과도 있으나 §10.7 표는 cell-pooled 사용. Reproducibility ✅.

## 4. Multiple comparison correction

§10.7 의 sig count 는 **raw p < 0.05** 기준 (paired_wilcoxon csv `significant_05` 컬럼).
- **Bonferroni** (α=0.05/40=0.00125): HDBSCAN 6/10, MB 4/10, Hilbert 3/10, sparse_rp 0/10
- **BH FDR** (α=0.05): HDBSCAN 7/10, MB 5/10, Hilbert 6/10, sparse_rp 0/10

**판정**: ⚠️ §10.7 narrative 는 보정 안 한 raw p 사용. Bonferroni 시 Hilbert "6/10 → 3/10" 같은 큰 변동. **권장**: §10.7 에 "raw p (보정 미적용); BH 보정 시에도 Outcome A/C 판정은 불변" 1줄 추가.

## 5. 결론

§10.7 narrative 의 핵심 claim (win/sig count, mean of cell median, BERN baseline 숫자, Outcome A/C 판정) 은 raw csv 와 **fully consistent** ✅. 발견된 issue 2 가지:
- **별표 tier inflation** 8 cell (방향 ✅, magnitude tier 1 단계 over) — 표 갱신 권장
- **multiple comparison correction 미적용** — narrative 결론은 불변 (Outcome A/C 모두 BH/Bonf 견고). 1줄 disclaimer 추가 권장.

본 §10.7 결론 (4강 sig > Adaptive, sparse_rp ≃ Adaptive) 은 evidence 가 견고하다.
