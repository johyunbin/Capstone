## §10.7 Adaptive Sampling (Exqutor) Paired 비교 (Single 10 cell, 5/8 21:34 finalize)

본 절은 5/8 비대면 회의에서 박세은 팀장이 ⭐⭐⭐ 우선순위로 결정한 *Adaptive Sampling 본 논문 비교* 의 실측 결과를 보고한다. Exqutor §V-B (식 1~6) 의 Adaptive Sampling 알고리즘을 Section VI hyperparameter 사양 (모멘텀 m = 0.9, learning rate η₀ = 0.1, period = 50, expansion factor α = 50, decay β = 1.5, momentum-attenuation γ = 0.99, 초기 표본 N₀ = 385) 으로 그대로 재현하여 단일 10 cell × 5 selectivity × 5 seed × 100 query = 2,500 paired measurement 를 21:30~21:34 (49 초 + 31 초) 에 완료하였다. 본 연구의 4강 method (HDBSCAN / MB_partial / Hilbert / sparse_rp) 와 query_id + seed + selectivity 정확 paired alignment 를 통해 head-to-head Δ% 와 paired Wilcoxon signed-rank test 를 산출한다.

### 측정 framework

paired Δ% 정의:

  Δ%ₕ₂ₕ = (q_error[method] − q_error[adaptive]) / q_error[adaptive] × 100

부호 음수 = method 가 더 정확. 각 cell × method 당 N = 2,484 ~ 2,500 paired pair (NaN q_error 16개 미만 drop). paired Wilcoxon signed-rank two-sided p-value 로 통계적 유의성을 검증한다.

### Cell-level head-to-head median Δ% 매트릭스 (10 cell × 4 method)

| Cell | HDBSCAN | MB_partial | Hilbert | sparse_rp |
|---|---|---|---|---|
| DEEP_sf1 | **-0.53\*** | **-0.69\*** | **-0.50\*** | -0.12 |
| DEEP_sf10 | **-0.67\*** | **-0.33\*** | -0.22 | +0.21 |
| SIFT_sf1 | **-1.16\*\*\*** | **-0.82\*** | **-1.11\*\*\*** | +0.01 |
| SIFT_sf10 | **-1.12\*\*\*** | **-1.14\*\*\*** | **-1.15\*\*\*** | -0.13 |
| SSN_sf1 | -0.06 | +0.09 | +0.05 | +0.18 |
| SSN_sf10 | -0.35 | -0.23 | -0.08 | -0.03 |
| WIKI_sf1 | -0.31 | -0.24 | -0.36 | +0.37 |
| WIKI_sf10 | **-0.37\*** | +0.30 | **-0.32\*** | +0.05 |
| YFCC_sf1 | **-0.97\*\*** | **-0.69\*\*\*** | **-0.40\*** | +0.05 |
| YFCC_sf10 | **-0.62\*\*** | **-0.57\*\*** | **-0.69\*\*** | -0.05 |
| **Win count (median < 0)** | **10/10** | **8/10** | **9/10** | 4/10 |
| **Sig. count (Wilcoxon p < 0.05)** | **7/10** | **6/10** | **6/10** | **0/10** |
| **mean of cell median Δ%** | **-0.62** | -0.43 | -0.48 | +0.05 |

\* p < 0.05  \*\* p < 1e-3  \*\*\* p < 1e-7

### 4 outcome 판정 — A (4강 ≻ Adaptive Sampling)

(1) **HDBSCAN 은 10/10 cell win, 7/10 cell statistically significant.** SIFT 양 scale (sf1/sf10) 에서 Wilcoxon p < 1e-7 의 highly significant 우위, YFCC sf1/sf10 도 p < 1e-3 로 동일 trend. SSN 와 WIKI sf1 의 ceiling 영역에서만 p > 0.05 로 marginal. (2) **Hilbert 는 9/10 win, 6/10 sig**, MB_partial 8/10 win 6/10 sig 으로 **HDBSCAN 보다 약간 약하나 trend 일관**. (3) **sparse_rp 는 4/10 win 0/10 sig** — Adaptive Sampling 과 사실상 통계적 동등 (mean of cell median Δ% = +0.05%, "본 연구 contribution 강도 = 약").

**Multiple comparison correction (40 test = 10 cell × 4 method) — Outcome 판정 불변.** Bonferroni (α = 0.00125): HDBSCAN 6/10, MB_partial 4/10, Hilbert 3/10, sparse_rp 0/10. Benjamini-Hochberg FDR (q = 0.05): HDBSCAN 7/10, MB_partial 5/10, Hilbert 6/10, sparse_rp 0/10. 두 보정 모두 **★1~★3 의 paired 우위** + **★4 의 동등** 결론은 안정적이며, 단지 magnitude tier (`*` / `**` / `***`) 가 raw p 기준 표시이므로 critical reviewer 검토 시 BH/Bonferroni 결과를 보조 evidence 로 함께 제시한다.

종합하면 Outcome 의 혼합 — ★1~★3 (HDBSCAN/Hilbert/MB_partial) 은 **A (4강 > Adaptive, paired 우위)**, ★4 sparse_rp 는 **B (동등, paired CI 0 포함)**. 보고서 outline v2 §4.4 의 4 outcome 정의 기준: A=4강 우위, B=동등, C=Adaptive 우위 (thesis fail), D=Hybrid. 4강 method 중 *분포-인지 강도가 강한 3종* (HDBSCAN, Hilbert, MB_partial) 이 Adaptive Sampling 에 paired statistical significance 를 가지고 우월하며, *production-friendly random projection* (sparse_rp) 은 Adaptive Sampling 과 통계적 indistinguishable.

### 본 연구 contribution 강도 평가

4강 vs BERN (§10.4) 의 sweet spot 에서의 magnitude 가 -7~-32% 였던 것에 비해, 4강 vs Adaptive 의 head-to-head magnitude 는 -0.5~-1.2% 로 한 자릿수 작다. 이는 **Adaptive Sampling 자체가 BERN 대비 일정 이득** 을 가져오기 때문이다 — Adaptive 의 cell-level median Δ% vs BERN 은 SIFT_sf1 -26.77%, WIKI_sf1 -6.50%, YFCC_sf1 -4.26% 로 본 4강과 동일 부호·동일 region 에서 효과가 발생한다. 그럼에도 불구하고 4강의 *분포 인지* 가 Adaptive Sampling 의 *모멘텀-기반 동적 표본 확장* 보다 같은 sweet spot 에서 추가 0.5~1.2%p improvement 를 paired-significantly 가져온다는 것은 **분포 정보 활용의 marginal value** 를 정량 입증한다. 본 연구의 narrative ("Exqutor 가 미작동하는 단일 테이블 영역에 대한 분포 정보의 가치") 는 paired Wilcoxon 유의 7/10 cell 으로 강화되며, sparse_rp 같은 production-friendly tier 에 대해서는 honest reporting 으로 "동등" 을 보고한다.

### Limitation 및 multi 환경 placeholder

본 결과는 단일 테이블 한정이다. §10.6 의 25× shrinkage chain (단일 17.13% → multi-vector 0.67%) 이 보여준 바, multi 환경에서는 4강 vs BERN 자체가 ±1% marginal 영역으로 약화되므로 4강 vs Adaptive head-to-head 도 indistinguishable 가능성이 높다. **Multi-vector + multi-table-join 3 cell × Adaptive Sampling baseline** 측정은 5/9 morning 도착 예정이며, 결과 도착 후 본 §10.7 에 multi 비교 표를 추가한다 (placeholder). 단일 정확성이 multi 정확성의 *필요조건만* 성립한다는 §10.6 narrative 와 정합하므로, 4강의 head-to-head 우위가 multi 에서는 약화될 것이라는 가설을 사전에 명시한다.

### Method-level limitation (V7 audit)

본 연구의 11 method paired 비교는 9/11 paper-correct + 2/11 minor deviation:

- **Reservoir (V7 finding)**: single-cell `run_reservoir.py` 는 `rng.integers(0, K, size=N)` 로 RANDOM20 proxy 구현 (Vitter Algorithm R 가 아님). multi-cell `_fit_reservoir` 는 `rng.choice(N, K, replace=False)` + nearest-centroid 으로 Vitter 통계 동치. 즉 P3 streaming sub-paradigm 의 representative 로서는 multi-cell 측정만 valid 하며, single-cell 결과는 RANDOM20 variant 로 해석한다.
- **LSH (V7 finding)**: Charikar 2002 sign(W·v) random projection 자체는 정확. 그러나 K=20 vs n_hyperplanes=5 의 misalignment 로 mod 20 collision 발생 (buckets 0~11 의 ~2× over-density), Wave 0 +2092% fail 의 algorithmic origin. K=2^n_hp (K=16 또는 K=32) 정합 시 자연스러우나 본 연구는 K=20 fixed 로 honest limitation.
- **sparse_rp (V7 finding)**: Achlioptas 2003 PODS 의 density 1/3 가 아니라 Li et al. 2006 KDD 의 1/√D variant 구현. 두 reference 모두 본 연구 narrative 에 명시.
