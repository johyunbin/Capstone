# Phase B Failure-Mode Regression Analysis

**Data**: 110 single-table parquets (275,000 rows)
+ 6 multi-relation csvs (165,000 rows).

## 1. OLS regression (n=438,124, R²=0.193, adj-R²=0.193)

We regress ``log q_error`` on the three failure-mode covariates plus paradigm
fixed effects (full spec).  In the joint model — which carries the binary
multi-relation indicator alongside ``log dim`` — the dimension slope is
**β₁ = +0.000 ± 0.000** (p=0.32); the multi-relation
indicator absorbs the cross-domain shift with
**β₃ = +0.023 ± 0.001** (p=4.23e-170); the selectivity
slope is **β₂ = -0.582 ± 0.002** (p=0).  Because
``is_multi`` partitions the support of ``log dim``, the two regressors are
informationally collinear (Belsley, Kuh & Welsch, 1980).  Dropping the
indicator (``regression_dim_only.csv``) recovers the unconfounded curse
slope **β₁ᵒⁿˡʸ = +0.008 ± 0.000** (p=6.83e-85),
the analytical signature of distance concentration (Beyer et al., 1999) and
consistent with the curse-of-dimensionality prediction of Geraci et al.
(2026): as embedding dimensionality grows, stratification's discriminative
power decays and estimator variance inflates.

## 2. Per-method curse-of-dim slope

The strongest curse signal is **Reservoir**
(β = +0.026, p = 1.97e-52, R² =
0.01).  Table ``curse_of_dim.csv`` ranks all 11 methods.

## 3. Sample-strata ratio collapse (Cochran, 1977 §5.5)

Holding the budget at N = 385, raising K from 20 to 80 collapses
``n_h = N/K`` from 19.25 to 4.81 — well below Cochran's stability rule of
``n_h ≥ 10``.  The simulated variance-inflation factor at K = 80 is
**5.05×** the K = 20
baseline, providing a quantitative ceiling for any "more strata" remediation.

## 4. Importance-sampling collapse (Bengtsson, Bickel & Li, 2008)

The effective sample-size ratio drops from
**0.875** in single-table cells to **0.770** under
multi-relation concatenation — the ESS collapse signature predicted in
high-dimensional particle-filter theory (Bengtsson et al., 2008).

## 5. Paradigm ranking — single → multi degradation

| rank | paradigm | mean degradation ratio |
|---|---|---|
| 1 | P4_DimReduction | 1.002 |
| 2 | P2_Spatial | 1.011 |
| 3 | P1_Cluster | 1.031 |
| 4 | P3_Streaming | 1.088 |
| 5 | P5_Quasi-random | 2.257 |

**Most robust**: P4_DimReduction (1.002×).
**Most fragile**: P5_Quasi-random (2.257×).

At the method level, **Hilbert** retains the lowest
degradation ratio (0.997×) while
**Sobol** collapses to 3.471×.

## 6. Boundary identification

Triangulating the regression (β₁ on ``log dim``), the ESS gap, and the
Cochran K-sweep, the failure mode dominates when **(i)** dim ≳ 800,
**(ii)** the cell is multi-relation (concatenated 864-d feature space),
and **(iii)** strata count is held at K = 20 so per-stratum sample size
remains marginally above the Cochran threshold.  Mitigation must therefore
attack dimensionality (paradigm P4) rather than allocation
(K-sweep cannot recover variance once n_h < 10).

## References
- Bengtsson, T., Bickel, P., & Li, B. (2008). *IMS Collections* 2, 316.
- Beyer, K., Goldstein, J., Ramakrishnan, R., & Shaft, U. (1999). *ICDT*.
- Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). Wiley.
- Geraci, F. et al. (2026). Working paper.
