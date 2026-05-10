"""Production-ready stratification methods for RQ3 multi-vector cells.

Each Tier S / Tier A / Tier B module exposes a
``stratify_method(emb1, emb2, K=20, seed=0, **kwargs) -> np.ndarray`` that
produces a stratum id per paired-vector row, and is drop-in compatible with
``_internal/scripts/measure_multi_paradigm.py``. Tier C exposes adaptive
sampling state classes that emit a per-query sample size rather than per-row
stratum ids.

Tier S — multi-relation native sampling
---------------------------------------
``wander_join_strat``
    Wander Join (Li et al., SIGMOD 2016 / TODS 2019,
    DOI 10.1145/3284551).  Index-aware random walk on the join graph.

``ams_count_sketch_strat``
    AMS Count-Sketch (Alon et al., PODS 1999 / JCSS 2002,
    DOI 10.1145/303976.303984).  SimHash sign-bit signature of the
    concatenated emb1+emb2 vector reduced mod K.

Tier A — productionized stratification primitives
--------------------------------------------------
``pq_stratify``
    Product Quantization (Jegou-Douze-Schmid PAMI 2011,
    DOI 10.1109/TPAMI.2010.57).  M-way sub-vector K-means with hash fold.

``coreset_stratify``
    Lightweight Coresets (Bachem-Lucic-Krause ICML 2017,
    arXiv:1702.08249).  Sensitivity 1/N + d^2/Σd^2, quantile bins.

``dense_rp_stratify``
    Dense Gaussian Random Projection (Bingham-Mannila ICDM 2001,
    DOI 10.1145/502512.502546).  R ~ N(0, 1/d), 1-D projection, quantile.

``bandit_ucb1_stratify``
    Stratified bandit MC-UCB (Carpentier-Munos NeurIPS 2011,
    arXiv:1106.5853).  KMeans K=20 + UCB1 metadata for adaptive allocation.

``neuram_stratify``
    NeurAM autoencoder (Geraci et al. arXiv:2506.08921, 2026).  1-D latent
    bottleneck with O(S^{-2}) dim-invariant variance reduction guarantee.

Tier B — multi-vector aware joint stratification
-------------------------------------------------
``cca1d_strat`` / :class:`CCA1DMapper`
    CCA-1D projection stratification (Hotelling Biometrika 1936,
    DOI 10.1093/biomet/28.3-4.321). Joint canonical 1D projection of two
    row-aligned embedding views, quantile-binned. PCA-1D fallback for the
    single-table case.

``coclustering_nystrom_strat`` / :class:`CoClusteringNystromMapper`
    Co-clustering with Nystrom approximation (Dhillon KDD 2003,
    DOI 10.1145/956750.956764; Williams-Seeger NIPS 2001;
    Fowlkes et al. IEEE TPAMI 2004 DOI 10.1109/TPAMI.2004.1262185).
    Bipartite spectral co-clustering on the cross similarity graph,
    accelerated by Nystrom column sampling.

Tier C — single-table single-vector selectivity-aware adaptive sampling
-----------------------------------------------------------------------
:class:`ConditionalAdaptiveState`
    Selectivity-conditioned variant of Exqutor V-B Adaptive Sampling
    (arXiv:2512.09695v2). Equation (3) is augmented with a
    ``sel_term * log(sel)`` prior; equations (4)-(6) are unchanged. Emits a
    per-query ``sample_size`` rather than per-row stratum ids; *not*
    applicable to the multi-vector pipeline.
"""
from .adaptive_bucket_probing import (
    AdaptiveBucketProbing,
    stratify_method as adaptive_bucket_probing_strat,
)
from .ams_count_sketch import stratify_method as ams_count_sketch_strat
from .bandit_ucb1_strat import (
    UCBStrataMetadata,
    stratify_method as bandit_ucb1_stratify,
)
from .cc_sketch import (
    CCSketch,
    stratify_method as cc_sketch_strat,
)
from .epsilon_net_strat import (
    EpsilonNetMetadata,
    stratify_method as epsilon_net_strat,
)
from .factor_join import (
    FactorJoin,
    stratify_method as factor_join_strat,
)
from .hkbu_repsample_strat import (
    HKBURepSampleEstimator,
    stratify_method as hkbu_repsample_strat,
)
# HNSW-SS dropped 5/10 00:10 — narrative violation (uses HNSW vector index,
# but our scope is "vector index 없음" scenario). See _method_portfolio_v9.
# from .hnsw_ss_strat import (
#     HNSWStratifiedSampling,
#     stratify_method as hnsw_ss_strat,
# )
from .kdpp_strat import stratify_method as kdpp_strat
from .lhs_strat import stratify_method as lhs_strat
from .lpm2_strat import stratify_method as lpm2_strat
from .lp_bound import (
    LpBoundEstimator,
    stratify_method as lp_bound_strat,
)
from .mfmc_strat import (
    MFMCEstimator,
    stratify_method as mfmc_strat,
)
from .opq_strat import stratify_method as opq_strat
from .thompson_sampling_strat import (
    TSStrataMetadata,
    stratify_method as thompson_sampling_strat,
)
from .tucker_strat import (
    TuckerEstimator,
    stratify_method as tucker_strat,
)
from .vine_copula_strat import (
    VineCopulaEstimator,
    stratify_method as vine_copula_strat,
)
from .cca_strat import (
    CCA1DMapper,
    assign_cca1d,
    fit_cca1d_mapper,
    stratify_method as cca1d_strat,
)
from .coclustering_nystrom_strat import (
    CoClusteringNystromMapper,
    assign_coclustering_nystrom,
    fit_coclustering_nystrom_mapper,
    stratify_method as coclustering_nystrom_strat,
)
from .conditional_adaptive_strat import (
    DEFAULT_SAMPLE_SIZE as CONDITIONAL_ADAPTIVE_DEFAULT_SAMPLE_SIZE,
    DEFAULT_SEL_TERM as CONDITIONAL_ADAPTIVE_DEFAULT_SEL_TERM,
    ConditionalAdaptiveState,
)
from .coreset_strat import stratify_method as coreset_stratify
from .dense_rp_strat import stratify_method as dense_rp_stratify
from .neuram_strat import stratify_method as neuram_stratify
from .pq_strat import stratify_method as pq_stratify
from .wander_join import stratify_method as wander_join_strat

# Canonical name -> stratify function mapping (drop-in for measure_multi_paradigm)
STRATIFY_FUNCTIONS = {
    # Tier S
    "wander_join": wander_join_strat,
    "ams_count_sketch": ams_count_sketch_strat,
    # Tier A
    "pq": pq_stratify,
    "coreset": coreset_stratify,
    "dense_rp": dense_rp_stratify,
    "bandit_ucb1": bandit_ucb1_stratify,
    "neuram": neuram_stratify,
    # Tier B
    "cca1d": cca1d_strat,
    "coclustering_nystrom": coclustering_nystrom_strat,
    # ---- v8 (5/9 22:35) — Tier S+/A new methods (research agent dispatch) ----
    "thompson_sampling":       thompson_sampling_strat,    # Russo 2018 / Bao SIGMOD 2021
    "epsilon_net":             epsilon_net_strat,          # Haussler-Welzl SoCG 1986
    "adaptive_bucket_probing": adaptive_bucket_probing_strat,  # Chen arXiv 2604.04603
    "cc_sketch":               cc_sketch_strat,            # Heddes SIGMOD 2024
    "factor_join":             factor_join_strat,          # Wu SIGMOD 2023
    # ---- v9 (5/9 23:30) — extreme-mode 9 additional methods ----
    "lp_bound":                lp_bound_strat,             # Zhang/Suciu SIGMOD 2025 Best Paper
    "mfmc":                    mfmc_strat,                 # Peherstorfer SIAM JSC 2016
    "tucker":                  tucker_strat,               # Tucker 1966 / Mu CoDe 2025
    "vine_copula":             vine_copula_strat,          # Bedford-Cooke 2002
    # "hnsw_ss":               hnsw_ss_strat,             # DROPPED 5/10 00:10 — narrative violation
    "hkbu_repsample":          hkbu_repsample_strat,       # Wu et al. SIGMOD 2026 (HKBU)
    "lhs":                     lhs_strat,                  # McKay Technometrics 1979
    "kdpp":                    kdpp_strat,                 # Kulesza-Taskar ICML 2011
    "opq":                     opq_strat,                  # Ge CVPR 2013 / PAMI 2014
    "lpm2":                    lpm2_strat,                 # Grafstrom 2012 / arXiv:2305.02446 (probabilistic spatially-balanced)
}

# Paper-display name -> canonical name (per measure_multi_paradigm METHOD_MAP convention)
TIER_A_METHOD_MAP = {
    "PQ": "pq",
    "Coreset": "coreset",
    "DenseRP": "dense_rp",
    "BanditUCB1": "bandit_ucb1",
    "NeurAM": "neuram",
}

TIER_B_METHOD_MAP = {
    "CCA1D": "cca1d",
    "CoCluster_Nystrom": "coclustering_nystrom",
}

# Tier C does not produce a stratify_method (no per-row stratum id);
# this map is provided for symmetry / documentation only.
TIER_C_STATE_CLASSES = {
    "ConditionalAdaptive": ConditionalAdaptiveState,
}

# Reference citations (for meta.json provenance trail)
TIER_A_REFERENCES = {
    "pq": "Jegou-Douze-Schmid PAMI 2011 (DOI 10.1109/TPAMI.2010.57)",
    "coreset": "Bachem-Lucic-Krause ICML 2017 (arXiv:1702.08249)",
    "dense_rp": "Bingham-Mannila KDD/ICDM 2001 (DOI 10.1145/502512.502546)",
    "bandit_ucb1": "Carpentier-Munos NeurIPS 2011 (arXiv:1106.5853)",
    "neuram": "Geraci et al. 2026 (arXiv:2506.08921)",
}

TIER_B_REFERENCES = {
    "cca1d": "Hotelling Biometrika 1936 (DOI 10.1093/biomet/28.3-4.321)",
    "coclustering_nystrom": (
        "Dhillon KDD 2003 (DOI 10.1145/956750.956764) + "
        "Williams-Seeger NIPS 2001 + "
        "Fowlkes-Belongie-Chung-Malik PAMI 2004 (DOI 10.1109/TPAMI.2004.1262185)"
    ),
}

TIER_C_REFERENCES = {
    "conditional_adaptive": (
        "Lim et al. arXiv:2512.09695v2 (Exqutor V-B) + "
        "Cochran 1977 + Neyman 1934 (DOI 10.2307/2342192)"
    ),
}

__all__ = [
    # Tier S
    "wander_join_strat",
    "ams_count_sketch_strat",
    # Tier A
    "UCBStrataMetadata",
    "pq_stratify",
    "coreset_stratify",
    "dense_rp_stratify",
    "bandit_ucb1_stratify",
    "neuram_stratify",
    # Tier B - CCA-1D
    "CCA1DMapper",
    "fit_cca1d_mapper",
    "assign_cca1d",
    "cca1d_strat",
    # Tier B - Co-clustering Nystrom
    "CoClusteringNystromMapper",
    "fit_coclustering_nystrom_mapper",
    "assign_coclustering_nystrom",
    "coclustering_nystrom_strat",
    # Tier C - Conditional Adaptive
    "ConditionalAdaptiveState",
    "CONDITIONAL_ADAPTIVE_DEFAULT_SAMPLE_SIZE",
    "CONDITIONAL_ADAPTIVE_DEFAULT_SEL_TERM",
    # Registries
    "STRATIFY_FUNCTIONS",
    "TIER_A_METHOD_MAP",
    "TIER_B_METHOD_MAP",
    "TIER_C_STATE_CLASSES",
    "TIER_A_REFERENCES",
    "TIER_B_REFERENCES",
    "TIER_C_REFERENCES",
]
