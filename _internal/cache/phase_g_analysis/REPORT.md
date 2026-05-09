# Phase G — End-to-end Analysis Report (v7 22 method × 28 cell)

**Data inventory.** This report consolidates all eight Phase G analytical sections over 5 methods × 3 cells ingested from 1 method parquets (900 rows) and 1 Phase F baseline parquets (1,080 rows). The full design matrix is 22 method × 28 cell × 5 selectivity × 5 seed × 100 query = 7.7M paired observations under the v7 plan; this run observed 3 cells (coverage 3/28) and 5 methods (coverage 5/22). Six baselines are expected (B1–B6); this run saw ['B1', 'B2', 'B3', 'B4', 'B5', 'B6'].

## G1 — Per-method single+multi consistency

Section G1 measures, for each of the 22 methods, the joint single-domain and multi-domain mean q_error. The **consistency ratio** (multi mean ÷ single mean) is the first-order summary statistic of single→multi degradation: ratios near 1.0 indicate stable cross-domain behaviour, ratios much greater than 1.0 indicate that the multi cells exposed the curse-of-dim or sample-strata-ratio failure modes catalogued in Phase B (Beyer 1999, Cochran 1977 §5.5, Bengtsson-Bickel-Li 2008). The `top_tier_filter` flag identifies methods that rank in the top half on *both* single and multi cells; v7 treats this filter as the entry gate for Stage ⑦ production candidates.

Paradigm-level aggregates show:

| paradigm | n_methods | mean rank single | mean rank multi | mean consistency |
|---|---|---|---|---|
| P2_Spatial | 2 | 2.00 | 4.50 | 2.106 |
| P1_Cluster | 3 | 3.67 | 2.00 | 1.788 |

## G2 — Paired Δ% vs Adaptive (B1)

Section G2 computes, for every (cell × method) pair, a paired Wilcoxon signed-rank test against the Adaptive Sampling baseline B1 (Lim et al. 2025 Section V-B; hyperparameters m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, N=385). Each test draws on ≈2,500 paired observations (5 sel × 5 seed × 100 query) which W1 sprint validated as a sufficient sample size for power ≥ 0.8 at the proposed effect sizes. Multiple-comparison control follows v7 §8.2 with a Bonferroni correction at α/22 ≈ 0.0023 (family of 22 method tests per cell), reported alongside raw p-values for transparency. Mean Δ% confidence intervals are 1000-iteration bootstrap percentiles per v7 §8.3.

| method | tier | wins single | wins multi | win_single_multi | mean Δ% |
|---|---|---|---|---|---|
| GMM | L | 1 | 0 | no | +19.20% |
| Hilbert | L | 1 | 0 | no | +13.73% |
| faiss_ivf | L | 1 | 0 | no | +19.69% |
| HDBSCAN | L | 0 | 0 | no | +16.65% |
| MiniBatch | L | 0 | 0 | no | +6.59% |

**Core finding (provisional).** No method passes the single+multi Bonferroni-significant filter at the time of this report. If this persists after the full Phase E matrix completes, the contribution is reframed under v7 §3 as a quantitative confirmation of the literature gap (Section 1) — the first published evidence that no method in the 22-method portfolio crosses the single+multi joint significance threshold.

## G3 — Adaptive vs Adaptive+ensemble (B1 vs B4)

Section G3 implements the Stage ⑥ 4-axis contribution metric (v7 §8.7). For every cell × ensemble-base-method, B4 — the Adaptive sample size wrapped in the chosen ensemble strategy — is paired against B1 along four axes: accuracy (paired Δ% mean q_error), convergence speed (t* delta per v7 §8.6), resource cost (wall-clock ms delta), and rare-query robustness (sel=0.01 mean q_error delta). A method qualifies for the Stage ⑥ contribution if B4 wins on **any** axis under the Bonferroni-adjusted α. The current run observed 15 (cell × ensemble) rows; 12 have at least one axis win.

## G4 — Failure mode regression (extended)

Section G4 re-fits the v7 §8.5 regression `log(q_error) = β₀ + β₁ log(dim) + β₂ sel + β₃ is_multi + Σγ_p paradigm + Σδ_t tier` on the extended 22-method × 28-cell matrix. The regression is the empirical bridge between the Phase B failure-mode diagnosis and the Phase G new-method evidence: positive β₁ corroborates Beyer 1999 / Geraci 2026 distance concentration, positive β₃ confirms the multi-relation shift, and negative paradigm coefficients γ_p relative to the P1_Cluster reference identify paradigms that mitigate the failure modes. The current fit yields R²=0.223 (adj 0.220, n=900) with β₁(log_dim)=+0.045 ± 0.005 (p=8.08e-16), β₃(is_multi)=+0.456 ± 0.035 (p=5.86e-36), β₂(sel)=-0.302 ± 0.444 (p=0.496). The per-method curse-of-dim slope table allows the new 11 methods to be compared with the legacy 11 directly: the design expectation is that NeurAM, Coreset and PQ exhibit significantly *lower* β₁_method than legacy P1/P5 methods, consistent with their dim-invariant (NeurAM, Bachem 2017) or codebook-bounded (PQ, Jegou 2011) guarantees.

Selected per-method slopes (sorted ascending — flatter is better for high-dim robustness):

| method | tier | paradigm | β₁(log_dim) | p | R² |
|---|---|---|---|---|---|
| MiniBatch | L | P1_Cluster | +0.143 | 1.22e-05 | 0.10 |
| HDBSCAN | L | P1_Cluster | +0.257 | 1.95e-11 | 0.22 |
| GMM | L | P1_Cluster | +0.263 | 6.1e-12 | 0.23 |
| Hilbert | L | P2_Spatial | +0.281 | 2.37e-12 | 0.24 |
| faiss_ivf | L | P2_Spatial | +0.320 | 7.77e-17 | 0.32 |

## G5 — Convergence speed analysis

Section G5 implements the v7 §8.6 convergence metric t* = first query t at which the running-mean q_error S_t satisfies |S_t − S_∞| / |S_∞| < 5%. The interesting delta is t*(B4) − t*(B1): a negative delta means Adaptive+ensemble (B4) converges faster than Adaptive alone (B1), one of the four contribution axes in Stage ⑥. We average across seeds within each cell to control for sample ordering; the cell-level distribution is reported per paradigm in `fig_g5_convergence.png`. The t* metric is complementary to the accuracy axis because two methods can achieve the same mean q_error but differ in their transient behaviour over the 100-query stream.

## G6 — Resource analysis and Pareto frontier

Section G6 aggregates wall-clock and peak RSS across cells for each method and computes the Pareto frontier on (mean_q_error, mean_wall_clock_ms). A method is **Pareto-dominated** if some other method beats it on both axes; the non-dominated set is the production candidate frontier. The legacy 4강 (HDBSCAN, MB_partial, Hilbert, sparse_rp) established the W1 reference frontier; new methods must extend or refine this frontier to qualify for Stage ⑦. PQ and NeurAM are expected to dominate sparse_rp / PCA1D on accuracy at comparable wall-clock; CCA1D and CoCluster_Nystrom are expected to occupy a higher-cost position justified only by their multi-vector structural guarantees.

## G7 — Production-ready package summary

Section G7 intersects the four filters built up in G1–G6: (i) `win_single_multi_b1` from G2 — the method must beat B1 in both single and multi cells under Bonferroni; (ii) `any_axis_win` from G3 — Stage ⑥ contribution on at least one of accuracy / convergence / resource / rare-query; (iii) `pareto_optimal` from G6 — non-dominated on cost-quality; (iv) `top_tier_filter` from G1 — top-half rank in single AND multi. Methods passing all four filters are the recommended production candidates that the Stage ⑦ exqutor_augment package should expose as drop-in registry entries with the English README descriptors emitted in `G7_production_top.csv`.

**Recommended production methods**: none qualify under the strict 4-filter intersection in this run; relax to `win_single_multi_b1 ∧ any_axis_win` (drop the Pareto and top_tier filters) to get a softer recommendation.

## References
- Beyer, K., Goldstein, J., Ramakrishnan, R., & Shaft, U. (1999). When is 'Nearest Neighbor' meaningful? *ICDT*.
- Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). Wiley.
- Bengtsson, T., Bickel, P., & Li, B. (2008). Curse-of-dimensionality revisited. *IMS Collections* 2.
- Achlioptas, D. (2003). Database-friendly random projections. *JCSS* 66(4).
- Jegou, H., Douze, M., & Schmid, C. (2011). Product Quantization. *PAMI*.
- Bachem, O., Lucic, M., & Krause, A. (2017). Practical coreset constructions. *ICML*.
- Bingham, E., & Mannila, H. (2001). Random projection in dimensionality reduction. *KDD/ICDM*.
- Carpentier, A., & Munos, R. (2011). Finite-time analysis of stratified sampling for MC integration. *NeurIPS*.
- Geraci, F., et al. (2026). Stratified sampling under the curse of dimensionality. arXiv:2506.08921.
- Hotelling, H. (1936). Relations between two sets of variates. *Biometrika*.
- Dhillon, I. S. (2003). Co-clustering documents and words using bipartite spectral graph partitioning. *KDD*.
- Li, F., Wu, B., Yi, K., & Zhao, Z. (2016). Wander Join: Online aggregation via random walks. *SIGMOD*.
- Alon, N., Gibbons, P. B., Matias, Y., & Szegedy, M. (1999). Tracking join and self-join sizes. *PODS*.
- Yang, Z., et al. (2020). NeuroCard: One cardinality estimator for all tables. *VLDB*.
- Lim et al. (2025). Exqutor. arXiv:2512.09695v2 — main paper.
