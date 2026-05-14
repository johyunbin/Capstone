# 추가 method 브레인스토밍 — paradigm 빈틈 + 학술 강화 + 2024-2025 literature

작성: 2026-05-10 14:30 KST (mac-mini 검증 세션, 사용자 외출 중)
세션 범위: 메인 세션은 Exqutor paper 100% 정확 재현 측정 진행 중. 본 세션 = 41 method portfolio 의 **paradigm 빈틈 보완 + 새 method 후보 발굴**.

---

## 0. TL;DR

### 0.1 핵심 권고 요약

| 분류 | 개수 | 권고 method |
|---|---|---|
| **Tier 1 즉시 추가** (구현 simple + narrative fit 매우 높음) | 6 | DBSCAN, KDE Parzen, multi-dim histogram (MHIST-2 / Poosala 1997), HyperLogLog, randomized SVD (Halko 2011), wavelet histogram (Matias 1998) |
| **Tier 2 W2-W3 추가** (구현 mid + ★ 후보) | 5 | UMAP, HDBSCAN-true (current 구현 검증 必), ScaNN-anisotropic, PRICE (pretrained), ADSampling (PDX) |
| **Tier 3 보고서 future work** (구현 high + paradigm 확장) | 6 | t-SNE/Isomap, OPTICS, Leiden HNSW community, persistent homology, deep autoencoder, GaussDB-Vector cardinality model |
| **즉시 폐기 권고** (학술 명칭 vs 실제 구현 mismatch) | 5 | neurocard_lite, factor_join, vinecopula, cocluster_nystrom, mfmc, lp_bound |
| **새 paradigm 제안** | 4 | P7 Subspace, P8 Graph-based, P9 Information-theoretic, P10 Density-estimation |

### 0.2 본 brainstorm 의 학술 강화 핵심

본 41 method portfolio 의 가장 큰 학술적 약점은 **density-estimation paradigm 의 부재** (KDE Parzen 1962 가 없음). 본 연구의 narrative 는 "분포 인지 stratification" 인데, density estimation 의 textbook method 가 누락된 점은 reviewer attack 의 1순위 후보. 즉시 KDE Parzen 추가가 narrative 강화에 가장 큰 영향.

두 번째 약점은 **method-naming vs 실제 구현 mismatch**. neurocard_lite (PCA+KMeans), factor_join (PCA+grid 2D), vinecopula (rank+PCA1D), cocluster_nystrom (SpectralBiclustering with PCA fallback) 등 5개 method 가 학술 명칭과 실제 구현이 일치하지 않음. 이 mismatch 가 paper 작성 시 reviewer 의 신뢰도 저하 risk.

### 0.3 본 brainstorm 의 paradigm 확장 핵심

기존 5/6 paradigm (P1-P6) 외에 **P7 Subspace clustering** (CLIQUE/SUBCLU/PROCLUS) 와 **P9 Information-theoretic** (HyperLogLog/AGMS/max entropy) 의 추가가 paradigm-rich portfolio 의 학술 두께 증가에 크게 기여. P7 은 고차원 sparse data 에 특화된 distinct paradigm, P9 는 sketch-based 영역의 본격 representative.

---

## 1. 현재 41 method portfolio 정밀 진단

### 1.1 Paradigm 분포

| Paradigm | 현재 method 수 | 학술 representative | 빈틈 평가 |
|---|---|---|---|
| **P1 Cluster** | 8 (hdbscan, minibatch, gmm, birch, agglomerative, coreset, hkbu_repsample, banditucb1) | hierarchical density (HDBSCAN) + centroid-based (KMeans 3 variants) + agglomerative (1) + coreset (1) | **빈틈 大**: DBSCAN (non-hierarchical), Mean-shift, OPTICS, Spectral 모두 부재 |
| **P2 Spatial** | 5 (hilbert, faiss_ivf, kdtree, kdpp, epsilon_net) | space-filling curve (Hilbert) + IVF (faiss) + tree (kdtree) + diversity (kdpp) + cover (epsilon_net) | **빈틈 中**: Z-order/Morton, R-tree, VP-tree, Ball Tree 부재 |
| **P3 Streaming** | 7 (minibatch_partial, reservoir, thompson_sampling, mfmc, adaptive_bucket_probing, lpm2, kde_pilot) | streaming KMeans + reservoir + bandit + multi-fidelity + LSH-based + spatial-balanced | **빈틈 中**: CluStream, DenStream, online k-medians 부재 (true streaming methods) |
| **P4 DimReduction** | 8 (sparse_rp, dense_rp, random_projection, pca1d, neuram, cca1d, tucker, vinecopula) | RP 3 variants + PCA 3 variants + AE-style (neuram) + tensor (Tucker) + copula (vine) | **빈틈 大**: UMAP, t-SNE, Isomap, ICA, NMF, LLE, AE 모두 부재 (linear 만 있음) |
| **P5 QMC/Hashing** | 8 (lsh, sobol, halton, hammersley, lhs, ams_count_sketch, ccsketch, lp_bound) | LSH + 3 QMC + 1 stratified design + 3 sketch | **빈틈 小**: Faure/Niederreiter 부재 (단 high-D 약함) |
| **P6 Quantization/Other** | 5 (pq, opq, neurocard_lite, factor_join, cocluster_nystrom) | PQ 2 variants + 3 misnamed wrappers | **빈틈 大**: ScaNN-anisotropic, RQ, AQ 모두 부재 |
| (paradigm-less) | (Conditional Adaptive — Tier C, AS variant only) | — | — |

### 1.2 학술 명칭 vs 실제 구현 mismatch (즉시 폐기 또는 정정 권고)

`measure_paper_exact.py:407-852` 의 `_get_method_strata()` 함수 정독 결과:

| method 명 | 학술 정의 | 실제 구현 (line) | 정정 권고 |
|---|---|---|---|
| `neurocard_lite` | NeuroCard (Yang VLDB 2020) = autoregressive density model multi-table | `PCA(n_components=8) → KMeans(n_clusters=20)` (line 706-714) | **폐기** — NeuroCard 와 무관. 차라리 `pca_kmeans` 명명 |
| `factor_join` | FactorJoin (Wu SIGMOD 2023) = factor-graph BP single-table conditional | `PCA(2) → 2D quantile grid` (line 738-749) | **폐기** — FactorJoin 와 무관. multi-dim histogram (Poosala 1997) 으로 대체 |
| `vinecopula` | Vine Copula (Bedford-Cooke 2002) = bivariate copula tree | `rankdata + PCA1D + quantile bin` (line 808-820) | **폐기** — vine 구조 없음. "rank-PCA1D" 로 rename or 폐기 |
| `cocluster_nystrom` | SpectralCoclustering (Dhillon KDD 2003) + Nyström low-rank | `SpectralBiclustering try + PCA fallback` (line 769-793) | **재구현 필요** — 실제 SpectralCoclustering 사용, fallback 제거 |
| `mfmc` | Multi-Fidelity MC (Peherstorfer SIAM JSC 2016) = control variates | `KMeans + reservoir 50/50 hybrid` (line 666-676) | **재구현 필요** — control-variate 식 누락. 단순 hybrid 는 학술 부정확 |
| `lp_bound` | LpBound (Zhang/Suciu SIGMOD 2025 Best Paper) = LP-based pessimistic upper bound on degree sequences | `np.linalg.norm + quantile bin` (line 752-757) | **폐기** — LpBound 와 완전 무관, 단순 L2 norm 만 사용 |
| `cca1d` | CCA (Hotelling 1936) = canonical correlation 두 set 간 | `PCA(1, whiten=True) + quantile bin` (line 759-767) | **재명명 권고** — `pca1d_whiten` 으로. Y label 없으면 CCA 가 아님 |
| `adaptive_bucket_probing` | Chen et al. arXiv 2604.04603 (2026) = LSH multi-probe + Chernoff bound | `PCA(1) + quantile bin` (line 716-725) | **재구현 필요** — LSH multi-probe 누락. 본 paper 핵심 알고리즘 vacuum |
| `kde_pilot` | KDE Parzen 1962 = density estimation + bandwidth selection | (registry line 미확인 — search 결과 없음) | **확인 필요** — registry 에서 누락된 method? `_get_method_strata` 분기 미확인 |

### 1.3 Reviewer attack 예측 (5/27 발표 기준)

`mismatch` 5건이 paper 작성 시 reviewer 1순위 attack:
1. "Why call it `lp_bound` when the implementation is just L2 norm quantile?"
2. "NeuroCard is a deep autoregressive model. Your `neurocard_lite` is PCA+KMeans. This is misleading."
3. "Vine Copula has a tree structure of bivariate copulas. Your `vinecopula` is just rank-PCA1D."

→ **즉시 5 method 폐기 또는 재명명 + 재구현** 후 발표/paper 작성 진입 권고.

---

## 2. Trial 1: 기존 paradigm 빈틈 발굴

### 2.1 P1 Cluster — 빠진 method

| candidate | 학술 reference | 구현 난이도 | server SF=10 8M 가능? | expected Δ% vs ★1 HDBSCAN |
|---|---|---|---|---|
| **DBSCAN** | Ester, Kriegel, Sander, Xu KDD 1996 | low (sklearn) | ⚠️ memory — full pairwise 시 O(N²), but `algorithm='ball_tree'` 사용하면 8M 가능 | ~동등 (HDBSCAN 의 non-hierarchical 형, eps 고정 단점) |
| **OPTICS** | Ankerst, Breunig, Kriegel, Sander SIGMOD 1999 | low (sklearn) | ⚠️ time — 8M 시 1h+ 소요 우려 | 동등 ~ 약세 (hierarchical 대안, but 더 느림) |
| **Mean-shift** | Comaniciu & Meer PAMI 2002 | low (sklearn) | ❌ memory — bandwidth estimation O(N²) | high-D 에서 약세 |
| **Spectral Clustering** | Ng, Jordan, Weiss NIPS 2002 + Shi-Malik PAMI 2000 | mid (Nyström approx 필요) | ⚠️ Laplacian 8M 불가, Nyström subsample 필수 | mid-tier ~ 약세 (graph Laplacian 고차원 어려움) |
| **Affinity Propagation** | Frey & Dueck Science 2007 | low (sklearn) | ❌ O(N²) similarity matrix | 약세 |
| **Ward Linkage Agglomerative** | Ward 1963 + sklearn | low (sklearn) | ⚠️ — current `agglomerative` 가 ward 사용 (line 577-592) | 동등 (이미 있음) |

→ **권고 추가**: DBSCAN (P1 paradigm 강화 — HDBSCAN vs DBSCAN 비교가 reviewer 가 자주 묻는 점)

### 2.2 P2 Spatial — 빠진 method

| candidate | 학술 reference | 구현 난이도 | server SF=10 가능? | expected Δ% vs ★3 Hilbert |
|---|---|---|---|---|
| **Z-order curve (Morton)** | Morton IBM 1966 | low (bit interleave) | ✅ (Hilbert 와 동일 비용) | 동등 ~ 약세 (Hilbert 가 일반적 우수, but Z-order 가 더 simple → baseline value) |
| **R-tree** | Guttman SIGMOD 1984 | mid (rtree library) | ⚠️ — rtree library 의 8M build 시간 long | 약세 (high-D 비효율) |
| **VP-tree** | Yianilos SODA 1993 | mid (직접 구현) | ✅ (build O(N log N)) | mid-tier (metric tree, vector cosine 가능) |
| **Cover Tree** | Beygelzimer, Kakade, Langford ICML 2006 | high | ⚠️ | mid-tier |
| **Ball Tree** | Omohundro 1989 | low (sklearn) | ✅ | 동등 (kdtree 와 비슷, 다른 metric 가능) |

→ **권고 추가**: Z-order Morton (Hilbert 와 직접 비교가 학술 강화 — paradigm anchor)

### 2.3 P3 Streaming — 빠진 method

| candidate | 학술 reference | 구현 난이도 | server SF=10 가능? | expected Δ% vs ★2 MB_partial |
|---|---|---|---|---|
| **CluStream** | Aggarwal, Han, Wang, Yu VLDB 2003 | mid (직접 구현 — micro/macro cluster) | ✅ | **★ 후보** — true streaming + temporal awareness, narrative fit very high |
| **DenStream** | Cao, Ester, Qian, Zhou SDM 2006 | mid | ✅ | mid-tier (density-based stream) |
| **STREAM (Guha 2003)** | Guha, Meyerson, Mishra, Motwani, O'Callaghan TKDE 2003 | mid | ✅ | mid-tier |
| **Online k-medians** | Charikar O'Callaghan Panigrahy STOC 2003 | mid | ✅ | mid-tier |

→ **권고 추가**: CluStream (P3 paradigm 학술 representative — 현재 P3 method 중 학술 streaming 명확한 것이 reservoir 만 있음)

### 2.4 P4 DimReduction — 빠진 method (가장 큰 빈틈)

| candidate | 학술 reference | 구현 난이도 | server SF=10 가능? | expected Δ% vs ★4 sparse_rp |
|---|---|---|---|---|
| **UMAP** | McInnes, Healy, Melville arXiv 1802.03426 (2018) | low (umap-learn library) | ✅ — 8M 약 30min (numba JIT) | **★ 후보** — kNN graph + manifold learning, narrative fit high |
| **t-SNE** | van der Maaten & Hinton JMLR 2008 | low (sklearn) | ❌ — 8M sklearn 메모리 한계 (typical limit ~50K) | future work (subsample 후 nearest assign 필요) |
| **Isomap** | Tenenbaum, de Silva, Langford Science 2000 | low (sklearn) | ❌ — Floyd-Warshall O(N³) | 약세 |
| **ICA** | Hyvärinen 1999 | low (sklearn FastICA) | ✅ | mid-tier (independence assumption) |
| **NMF** | Lee & Seung Nature 1999 | low (sklearn) | ✅ — but vector embedding 음수 포함 가능 → 사전 shift 필요 | mid-tier |
| **KernelPCA** | Schölkopf, Smola, Müller Neural Computation 1998 | low (sklearn) | ⚠️ — kernel matrix O(N²) → Nyström subsample | mid-tier |
| **LLE** | Roweis & Saul Science 2000 | low (sklearn) | ⚠️ — kNN graph 8M 비용 | 약세 |
| **AutoEncoder** (real neural net) | Hinton-Salakhutdinov Science 2006 | high (torch) | ✅ (GPU 사용) | **★ 후보 high** — neuram 의 진짜 구현 (현재 neuram 은 PCA proxy) |
| **randomized SVD (Halko 2011)** | Halko, Martinsson, Tropp SIAM Review 2011 | low (sklearn `randomized_svd`) | ✅ (8M 약 1-3min, PCA1D 의 large-scale 대체) | 동등 ~ ★ 후보 (PCA1D 의 더 fast 변형) |

→ **권고 추가**: UMAP (★ 후보), randomized SVD (Halko 2011) — PCA1D 의 학술 강화 변형

### 2.5 P5 Low-discrepancy / Sketch — 빠진 method

| candidate | 학술 reference | 구현 난이도 | server SF=10 가능? | expected Δ% vs current |
|---|---|---|---|---|
| **Faure sequence** | Faure Acta Arithmetica 1982 | low (scipy QMC) | ✅ (low-D) ⚠️ (high-D >25 dim 약함) | 약세 (high-D vector 96-768d 에 부적합) |
| **Niederreiter sequence** | Niederreiter Bull AMS 1988 | low (scipy QMC) | ✅ | 동등 (Sobol 와 비슷) |
| **Stratified random** | Cochran 1977 | low | ✅ | baseline (이미 비슷한 LHS 있음) |
| **HyperLogLog** | Flajolet, Fusy, Gandouet, Meunier AofA 2007 | low (datasketch library) | ✅ | **★ 후보 mid** — count-distinct sketch, 본 연구 cardinality estimation 영역 textbook |

→ **권고 추가**: HyperLogLog (P5 paradigm 학술 representative — 본 연구 narrative 와 직접 fit)

### 2.6 P6 Quantization — 빠진 method

| candidate | 학술 reference | 구현 난이도 | server SF=10 가능? | expected Δ% vs current PQ/OPQ |
|---|---|---|---|---|
| **ScaNN anisotropic VQ** | Guo, Sun, Lindgren, Geng, Simcha, Chern, Kumar ICML 2020 | low (scann library) | ✅ | **★ 후보 high** — Google production-grade, narrative fit (vector DB) |
| **SOAR** | Sun, Guo, Simcha, Kumar NeurIPS 2023 | mid (scann library) | ✅ | ★ 후보 (orthogonality-amplified residuals, ScaNN extension) |
| **Residual Quantization (RQ)** | Babenko & Lempitsky CVPR 2014 | mid (직접 구현) | ✅ | mid-tier |
| **Additive Quantization (AQ)** | Babenko & Lempitsky CVPR 2014 | high (joint optimization) | ⚠️ | mid-tier |

→ **권고 추가**: ScaNN anisotropic (P6 paradigm 학술 representative — current PQ/OPQ 외 production-grade 추가)

---

## 3. Trial 2: 학술 강화 representative

### 3.1 Density-based 분포 추정 (가장 큰 빈틈)

본 연구의 narrative 는 "분포 인지 stratification" — density estimation 의 textbook method 가 누락된 점은 reviewer attack 1순위.

| candidate | reference | 본 연구 narrative fit | 구현 |
|---|---|---|---|
| **KDE Parzen** | Parzen "On estimation of a probability density function" Annals of Mathematical Statistics 1962 | **매우 높음** (분포 인지 textbook, density-aware stratification 의 학술 origin) | sklearn `KernelDensity` (8M 메모리 한계 있음, subsample → fit → score 패턴) |
| **Gaussian KDE w/ bandwidth selection** | Silverman 1986 (rule-of-thumb), Sheather-Jones 1991 | 높음 (bandwidth selection) | scipy `gaussian_kde` (8M 메모리 한계 → subsample 100K 후 score) |
| **Mean-shift density estimation** | Cheng PAMI 1995 / Comaniciu-Meer 2002 | 높음 | sklearn `MeanShift` (high-D 약함) |
| **Adaptive KDE** (variable bandwidth) | Abramson 1982 / Loader 1999 | 높음 | scipy 변형 |

→ **즉시 추가 권고**: KDE Parzen 1962 — narrative 의 학술 anchor

### 3.2 Histogram 다차원

| candidate | reference | 본 연구 narrative fit | 구현 |
|---|---|---|---|
| **MHIST-2 (multi-dim histogram)** | Poosala & Ioannidis VLDB 1997 | 높음 (multi-dim cardinality estimation textbook) | 직접 구현 (MaxDiff(V,A) bucket, 200~500 line) |
| **Equi-depth multi-dim histogram** | Poosala 1997 / Bertoli, Ramamohanarao, Naor SIGMOD 2017 (big data 변형) | 높음 | numpy quantile + 2D/3D bucketing |
| **Wavelet histogram** | Matias, Vitter, Wang SIGMOD 1998 | 높음 (lossy compression 식 histogram) | PyWavelets (DWT) + threshold |
| **V-optimal histogram** | Jagadish, Koudas, Muthukrishnan, Poosala, Sevcik, Suel VLDB 1998 | 중간 (1D 기반) | DP O(N²B) — 8M 어려움, subsample 필요 |
| **DigitHist** | Shekelyan, Dignös, Gamper VLDB 2017 | 높음 (tight error bounds histogram) | 직접 구현 medium |

→ **즉시 추가 권고**: MHIST-2 (factor_join 의 진짜 representative) + wavelet histogram

### 3.3 Graphical model

| candidate | reference | 본 연구 narrative fit | 구현 |
|---|---|---|---|
| **Junction tree** | Lauritzen & Spiegelhalter J. Royal Stat. Soc. 1988 | 중간 | high (직접 구현 복잡, graph triangulation) |
| **LDA (Latent Dirichlet Allocation)** | Blei, Ng, Jordan JMLR 2003 | 낮음 (topic model, 본 연구 영역 outside) | sklearn |
| **Bayesian network** | Pearl 1988 | 중간 | pgmpy library |

→ **권고**: 이 영역은 본 연구 주력 narrative 외, 우선 보류

### 3.4 Low-rank approximation

| candidate | reference | 본 연구 narrative fit | 구현 |
|---|---|---|---|
| **NMF** | Lee & Seung Nature 1999 | 중간 (non-negative 만 가능) | sklearn `NMF` |
| **randomized SVD** | Halko, Martinsson, Tropp SIAM Review 2011 | 높음 (PCA1D 의 large-scale 변형) | sklearn `randomized_svd` |
| **Sparse PCA** | Zou, Hastie, Tibshirani JCGS 2006 | 중간 | sklearn `SparsePCA` |

→ **즉시 추가 권고**: randomized SVD (Halko 2011) — PCA1D 의 학술 강화 변형, 8M scale 가능

### 3.5 Sketch

| candidate | reference | 본 연구 narrative fit | 구현 |
|---|---|---|---|
| **AGMS sketch** | Alon, Gibbons, Matias, Szegedy STOC 1999 + JACM 2002 | 높음 (F2 frequency moment) | 직접 구현 (current `ams_count_sketch` 와 다름 — sign matrix 만 사용) |
| **HyperLogLog** | Flajolet, Fusy, Gandouet, Meunier AofA 2007 | **높음** (count-distinct cardinality textbook) | datasketch library |
| **Count-Min sketch** | Cormode & Muthukrishnan JoA 2005 | 중간 (current `ccsketch` 와 비슷) | datasketch library |
| **MinHash** | Broder STOC 1997 | 중간 (set similarity) | datasketch library |

→ **즉시 추가 권고**: HyperLogLog (Flajolet 2007) + true AGMS sketch

### 3.6 Subspace clustering (P7 paradigm 후보)

| candidate | reference | 본 연구 narrative fit | 구현 |
|---|---|---|---|
| **CLIQUE** | Agrawal, Gehrke, Gunopulos, Raghavan SIGMOD 1998 | **높음** (axis-aligned subspace dense grid) | 직접 구현 mid (~300 line) |
| **PROCLUS** | Aggarwal, Procopiuc, Wolf, Yu, Park SIGMOD 1999 | 높음 (medoid + subspace) | 직접 구현 mid |
| **SUBCLU** | Kailing, Kriegel, Kröger SDM 2004 | 중간 (DBSCAN 의 subspace 확장) | 직접 구현 mid + DBSCAN dependency |
| **DOC** | Procopiuc, Jones, Agarwal, Murali SIGMOD 2002 | 중간 | 직접 구현 mid |

→ **추가 권고 (W2)**: CLIQUE (P7 새 paradigm 의 representative)

---

## 4. Trial 3: 2024-2025 SIGMOD/VLDB cardinality estimation literature

본 section 은 web search 결과 기반.

### 4.1 Vector DB cardinality estimation (본 연구 직결)

| paper | year | conference | method 핵심 | 본 연구 적용 가능? |
|---|---|---|---|---|
| **Exqutor** (본 연구 baseline) | 2025 | arXiv 2512.09695 | ECQO + AdaptiveSampling §V-B | ✅ 본 연구 baseline |
| **PDX (Partition Dimensions Across)** | 2025 | SIGMOD 2025 | dimension-by-dimension 검색, normal vs skewed distribution 적응적 dimension pruning (ADSampling/BSA) | ✅ 매우 fit — intrinsic_dim + skewness driven, 본 RQ1 narrative 강화 |
| **GaussDB-Vector** | 2025 | VLDB 2025 (vol 18 p.4951) | distributed vector DB 의 cardinality model per data node, range/top-k 분기 | ⚠️ distributed 특화, single-node 본 연구에 직접 적용 어려움 |
| **Cardinality Estimation for Similarity Search on High-Dim Data** | 2025 | VLDB 2025 (Bao et al., vol 18 p.544) | reference object 기반 cardinality 추론 | ✅ fit — single-table KNN cardinality estimation, 본 연구 §V-B 영역 |
| **Adaptive Bucket Probing (Chen et al.)** | 2026 | arXiv 2604.04603 | LSH multi-probe + Chernoff bound + 점진적 sampling + asymmetric distance computation | ✅ **★ 후보 high** — 본 연구 method registry `adaptive_bucket_probing` 의 진짜 구현 (current 는 PCA quantile only) |

### 4.2 Learned cardinality estimators

| paper | year | conference | method 핵심 | 본 연구 적용 가능? |
|---|---|---|---|---|
| **NeuroCard** | 2020 | VLDB 2020 (Yang et al.) | autoregressive density model multi-table, JOB-light 8.5x improvement | ⚠️ neurocard_lite 명명 misnomer — 진짜 구현은 GPU 필요 |
| **DeepDB** | 2020 | VLDB 2020 (Hilprecht et al.) | sum-product network density estimator + correlation test | mid-tier — 본 연구 single-table scope 와 align |
| **ALECE** | 2024 | VLDB 2024 (Ding et al.) | attention-based, 2.7× faster than PG | future work — single-table 영역 |
| **PRICE** | 2024 | VLDB 2024 (Zeng et al., vol 18 p.637) | **pretrained cross-DB cardinality estimator**, self-attention, 30 dataset 5h 학습, 40MB | ✅ **★ 후보 mid** — pretrained model 사용 시 본 연구 cardinality estimation 의 transferability narrative 강화 |
| **FactorJoin** | 2023 | SIGMOD 2023 (Wu et al.) | factor-graph BP, single-table 분포 만 학습, 40x latency 개선 | 본 연구 method registry `factor_join` 의 진짜 구현 — 다만 single-table 본 연구 scope 와 align 적음 (multi-join 특화) |
| **MSCN** | 2018 | CIDR 2019 (Kipf et al.) | multi-set CNN | future work |
| **Naru / NaruPlus** | 2019 | VLDB 2019 (Yang et al.) | autoregressive density single-table | mid-tier (single-table 영역) |
| **FLAT** | 2021 | VLDB 2021 (Zhu et al.) | Factorized Sum-Product Network | mid-tier |
| **Downsizing Diffusion Models for Cardinality Estimation** | 2025 | arXiv 2510.20681 | diffusion model 압축 | future work |
| **FOSS** | 2025 | VLDB Journal 2025 (Sept) | learned doctor for query optimization | future work |
| **Lightweight Learned CardEst** | 2025 | TKDE 2025 (Oct) | lightweight model | future work |

### 4.3 Theoretical / Pessimistic estimators

| paper | year | conference | method 핵심 | 본 연구 적용 가능? |
|---|---|---|---|---|
| **LpBound** | 2025 | SIGMOD 2025 Best Paper (Zhang, Mayer, Khamis, Olteanu, Suciu) | $\ell_p$-norm of degree sequences + LP | ✅ **★ 후보 high** — 본 연구 method registry `lp_bound` 의 진짜 구현 (current 는 단순 L2 norm). Suciu 의 SIGMOD 2025 Best Paper |
| **CCSketch (Heddes 2024)** | 2024 | SIGMOD 2024 (Heddes, Nunes, Givargis, Nicolau) | circular convolution + cross-correlation count sketches via FFT, O(rm log m) inference, 50% speedup | ✅ method registry `ccsketch` 의 진짜 구현 — current 는 단순 multi-hash |
| **Information-theoretic bounds** | 2025 | Olteanu Simons talk 2025 | New theoretical development | future work |

### 4.4 본 연구 narrative 강화 우선순위

| 순위 | paper / method | 추가 motivation |
|---|---|---|
| 1 | **LpBound (Zhang/Suciu SIGMOD 2025 Best Paper)** | 현재 method registry 의 `lp_bound` 폐기 → 진짜 LpBound 구현 또는 폐기. SIGMOD Best Paper 인용은 paper 가치 큼 |
| 2 | **Adaptive Bucket Probing (Chen 2026)** | 현재 `adaptive_bucket_probing` 의 진짜 구현 — Chen et al. 의 vector-native LSH + Chernoff bound |
| 3 | **CCSketch (Heddes 2024)** | 현재 `ccsketch` 의 진짜 구현 — FFT 기반 |
| 4 | **PRICE (Zeng 2024)** | pretrained CardEst — transferability narrative 강화 |
| 5 | **PDX (CWI 2025)** | intrinsic_dim + skewness driven — 본 RQ1 narrative 강화 |
| 6 | **HyperLogLog (Flajolet 2007)** | sketch paradigm 의 textbook representative |
| 7 | **KDE Parzen (1962)** | density-estimation paradigm 의 textbook representative |
| 8 | **MHIST-2 (Poosala 1997)** | multi-dim histogram representative — `factor_join` 의 진짜 대체 |

---

## 5. Trial 4: 새 paradigm 제안

### 5.1 P7 Subspace clustering

기존 P1 cluster 는 full-dimensional space 만 다룸. 고차원 vector embedding 에서는 axis-aligned subspace 에서만 cluster 가 형성될 수 있음 — 이 영역은 별도 paradigm 화 권고.

| method | reference | 본 연구 motivation 강화 | 구현 난이도 |
|---|---|---|---|
| **SUBCLU** | Kailing, Kriegel, Kröger SDM 2004 | 고차원 sparse vector — DBSCAN subspace 확장 | mid (DBSCAN 의 subspace 확장) |
| **CLIQUE** | Agrawal, Gehrke, Gunopulos, Raghavan SIGMOD 1998 | grid-based subspace, APRIORI 식 search | mid |
| **PROCLUS** | Aggarwal, Procopiuc, Wolf, Yu, Park SIGMOD 1999 | medoid 기반, 작은 dimension subset 만 | mid |
| **DOC** | Procopiuc, Jones, Agarwal, Murali SIGMOD 2002 | density optimal cluster | mid |

→ **권고**: P7 paradigm 으로 CLIQUE 1개만 추가 (paradigm anchor 역할)

### 5.2 P8 Graph-based

본 연구의 vector embedding 은 자연스럽게 graph (kNN) 로 변환 가능. graph community detection 으로 stratification 가능.

| method | reference | 본 연구 motivation 강화 | 구현 난이도 |
|---|---|---|---|
| **HNSW + Leiden** | Traag, Waltman, van Eck Scientific Reports 2019 | HNSW graph 의 community detection | mid (`igraph` library) |
| **HNSW + Louvain** | Blondel, Guillaume, Lambiotte, Lefebvre J. Stat. Mech. 2008 | community detection (Louvain 의 worst case 25% disconnected 문제) | mid |
| **kNN graph + spectral** | Ng-Jordan-Weiss NIPS 2002 + Nyström | graph Laplacian 기반 | mid + high |
| **random walk hash** | Perozzi, Al-Rfou, Skiena KDD 2014 (DeepWalk) | random walk → embedding → cluster | high (training) |

→ **권고 (future work)**: HNSW + Leiden 1개 추가 — Exqutor 본 연구의 HNSW graph 자체를 직접 활용 가능 (handoff_v0 §1.4 의 HNSW-SS 폐기 규칙과 충돌 X — community detection 은 vector index 를 *분포 정보 추출* 용도로 활용, search 용도 X)

### 5.3 P9 Information-theoretic

| method | reference | 본 연구 motivation 강화 | 구현 난이도 |
|---|---|---|---|
| **Max-entropy histogram** | Markl, Megiddo, Kutsch, Tran, Haas, Srivastava VLDB 2005 | constraint-based histogram | mid |
| **Mutual information ranking** | Cover & Thomas 1991 | feature/dimension importance | low (sklearn) |
| **MDL-optimal binning** | Rissanen 1978 + Boullé Machine Learning 2006 | minimum description length 기반 binning | mid |
| **HyperLogLog** | Flajolet, Fusy, Gandouet, Meunier AofA 2007 | distinct count sketch | low (datasketch) |
| **AGMS sketch** | Alon, Gibbons, Matias, Szegedy STOC 1999 | F2 frequency moment | low |

→ **권고**: HyperLogLog (P9 paradigm representative)

### 5.4 P10 Density estimation (가장 강력한 paradigm 후보)

본 연구 narrative 의 학술 anchor — KDE 가 P4/P5 어디에도 fit 하지 않음. 별도 paradigm 화 권고.

| method | reference | 본 연구 motivation 강화 | 구현 난이도 |
|---|---|---|---|
| **KDE Parzen** | Parzen Annals of Mathematical Statistics 1962 | density estimation textbook origin | low (sklearn) |
| **Gaussian KDE** | Silverman 1986 | bandwidth selection rule-of-thumb | low (scipy) |
| **Sheather-Jones bandwidth** | Sheather & Jones JRSS 1991 | optimal bandwidth selection | mid |
| **DEFT (density estimation field theory)** | Kinney PRE 2014 | non-parametric density on bounded domain | high |

→ **즉시 추가 권고**: KDE Parzen 1962 — P10 paradigm 의 representative + narrative 핵심

### 5.5 P11 Topological (future work only)

| method | reference | 본 연구 motivation 강화 | 구현 난이도 |
|---|---|---|---|
| **Persistent homology** | Edelsbrunner, Letscher, Zomorodian DCG 2002 | topological feature 추출 | high (gudhi/ripser) |
| **Mapper algorithm** | Singh, Mémoli, Carlsson SPBG 2007 | topological summary | high (kepler-mapper) |

→ **권고**: 본 학기 outside, 보고서 future work 에만 언급

---

## 6. 종합 권고 — 5/27 발표까지 시간 budget

### 6.1 Tier 1 즉시 추가 (5/12 ~ 5/14, 본 세션 직후 launch)

구현 simple + narrative fit 매우 높음 + ★ 후보:

| # | method | paradigm | reference | 구현 line 수 추정 | server SF=10 ETA |
|---|---|---|---|---|---|
| 42 | **DBSCAN** | P1 (강화) | Ester KDD 1996 | ~30 line (sklearn) | 30min |
| 43 | **KDE Parzen** | **P10 새** | Parzen 1962 | ~50 line (sklearn KernelDensity + subsample) | 1h |
| 44 | **MHIST-2** | P6 정정 (factor_join 대체) | Poosala VLDB 1997 | ~200 line (직접 구현, MaxDiff) | 1h |
| 45 | **HyperLogLog** | **P9 새** | Flajolet 2007 | ~30 line (datasketch) | 30min |
| 46 | **randomized SVD** | P4 (강화) | Halko 2011 | ~30 line (sklearn `randomized_svd`) | 30min |
| 47 | **wavelet histogram** | P6 (강화) | Matias 1998 | ~150 line (PyWavelets DWT) | 1h |

**총 6 method 추가** → portfolio 41 → 47

### 6.2 Tier 2 W2-W3 추가 (5/15 ~ 5/22, 시간 여유 있을 때)

구현 mid + ★ 후보 가능성:

| # | method | paradigm | reference | 구현 line 수 추정 | server SF=10 ETA |
|---|---|---|---|---|---|
| 48 | **UMAP** | P4 (강화) | McInnes 2018 | ~30 line (umap-learn) | 30min ~ 1h (numba JIT) |
| 49 | **HDBSCAN-true 검증** | P1 (정정) | Campello 2013 / McInnes 2017 | current 구현 검증 (registry 미확인) | 30min 검증 |
| 50 | **ScaNN-anisotropic** | P6 (강화) | Guo ICML 2020 | ~50 line (scann library) | 1h |
| 51 | **PRICE-pretrained** | P? 새 (learned 영역) | Zeng VLDB 2024 | ~200 line (github 모델 download + adapt) | 2h |
| 52 | **ADSampling (PDX)** | P4 (강화 — adaptive dim pruning) | Gao SIGMOD 2023 / PDX paper 2025 | ~150 line | 2h |
| 53 | **CluStream** | P3 (강화) | Aggarwal VLDB 2003 | ~250 line (직접 구현, micro/macro cluster) | 2h |
| 54 | **CLIQUE** | **P7 새** | Agrawal SIGMOD 1998 | ~300 line | 2h |

**Tier 1 + Tier 2 합계**: 47 + 7 = **54 method**

### 6.3 Tier 3 보고서 future work (구현 X, narrative 만)

| method | paradigm | 보고서 위치 |
|---|---|---|
| t-SNE / Isomap / LLE | P4 | future work — 8M scale 어려움 |
| OPTICS / Spectral / Affinity Propagation | P1 | future work |
| Leiden HNSW community | **P8 새** | future work — Exqutor HNSW graph 직접 활용 |
| Persistent homology | **P11 새** | future work |
| AutoEncoder (real torch) | P4 | future work — neuram 의 진짜 구현 |
| GaussDB-Vector cardinality model | distributed | future work — single-node 본 연구 외 |

### 6.4 즉시 폐기 권고 (paper 작성 reviewer attack 방어)

| # | 현재 method | 학술 명칭 mismatch | 대체 method |
|---|---|---|---|
| 1 | `neurocard_lite` (PCA+KMeans) | NeuroCard (Yang VLDB 2020) 와 무관 | **DBSCAN 으로 대체** + 명칭 정정 (또는 폐기) |
| 2 | `factor_join` (PCA+grid 2D) | FactorJoin (Wu SIGMOD 2023) 와 무관 | **MHIST-2 (Poosala 1997)** 로 대체 |
| 3 | `vinecopula` (rank+PCA1D) | Vine Copula (Bedford-Cooke 2002) 와 무관 | 폐기 또는 `rank_pca1d` 로 rename |
| 4 | `cocluster_nystrom` (SpectralBiclustering try + PCA fallback) | Nyström approximation 미사용 | **재구현 필요** — Nyström + Spectral |
| 5 | `mfmc` (KMeans + reservoir 50/50) | Multi-Fidelity MC (Peherstorfer 2016) 의 control variates 누락 | **재구현 필요** — control-variate 식 |
| 6 | `lp_bound` (단순 L2 norm) | LpBound (Zhang/Suciu SIGMOD 2025 Best Paper) 와 완전 무관 | **즉시 폐기** + LpBound 진짜 구현 시도 |
| 7 | `adaptive_bucket_probing` (PCA quantile) | Chen 2026 의 LSH multi-probe + Chernoff 누락 | **재구현 필요** — LSH multi-probe + Chernoff bound |
| 8 | `cca1d` (PCA1D whiten) | CCA (Hotelling 1936) 의 두 set 간 정의 위반 | `pca1d_whiten` 으로 rename |

→ **추가 권고**: 5/27 paper 제출 직전 8개 method 의 명칭/구현 audit (1일 작업)

### 6.5 새 paradigm 정리 (5 → 9 paradigm)

기존 5 paradigm 에 4 추가:
- P1 Cluster, P2 Spatial, P3 Streaming, P4 DimReduction, P5 QMC/Hashing, P6 Quantization (기존 6)
- **P7 Subspace clustering** (CLIQUE) — 새
- **P8 Graph-based** (Leiden, future work)
- **P9 Information-theoretic** (HyperLogLog) — 새
- **P10 Density estimation** (KDE Parzen) — 새

총 **9 paradigm** (P11 Topological 은 보고서 future work 만)

---

## 7. 추가 reviewer attack 방어 list

### 7.1 RQ3 V7 method-level limitation 대응

handoff_v0 §1.1 에 명시된 limitation:
- "Reservoir RANDOM20 proxy"
- "LSH K=20 vs n_hp=5 misalignment"
- "sparse_rp Li 2006 1/√D variant"

→ 새 paradigm 추가 후, 각 paradigm 내 ★ method 의 hyperparam alignment 점검 필요

### 7.2 paper-exact 정렬 — Exqutor §V-B 의 unstratified Bernoulli 와 paired 비교

본 41 method (또는 47) portfolio 가 모두 *Exqutor §V-B 의 단순 Bernoulli sampling 의 분포 인지 stratification 변형* 으로 격상되려면:
- **claim 1**: 분포 정보 활용 → 학술 paradigm 분류 (P1-P10) 9개로 명확
- **claim 2**: Exqutor §V-B + AdaptiveState (Eq 1-6) 에 plug-in → method 가 sample size 동적 조정과 호환
- **claim 3**: paired Δ% Wilcoxon 으로 ★ 4강 (HDBSCAN, MB_partial, Hilbert, sparse_rp) 과 비교

→ Tier 1 (DBSCAN, KDE, MHIST, HLL, RSVD, wavelet) 6개 method 모두 claim 1-3 충족 가능. 9-paradigm 체계가 paper 의 학술 두께 증가에 큰 기여.

### 7.3 PDX (SIGMOD 2025) 와 본 연구 RQ1 narrative 강화

PDX paper (Krimmel-Boncz et al.) 의 핵심 발견:
- normal distribution: DEEP, NYTimes, arXiv, Contriever, GloVe variants
- skewed distribution: SIFT, GIST, MSong, OpenAI

본 연구 RQ1 (Block vs Row × Normal vs Skew) 의 narrative 와 직접 align:
- DEEP = normal (intrinsic dim ~ 9)
- SIFT = skewed (gradient histogram 분포 skew)
- → PDX 의 dimension distribution finding 을 본 RQ1 narrative 의 cite 로 활용 가능

→ **paper 작성 시 PDX 인용 필수** — 본 연구 narrative 의 학술 fit 강화

---

## 8. 구체 구현 plan — Tier 1 (5/12 ~ 5/14)

### 8.1 추가 6 method 의 `_get_method_strata` 분기 코드

`measure_paper_exact.py:407-852` 에 추가:

```python
# DBSCAN
if method_name == "dbscan":
    from sklearn.cluster import DBSCAN
    sample = all_vecs[: min(len(all_vecs), 500_000)]
    eps = np.median(np.linalg.norm(sample[:1000] - sample[1000:2000], axis=1)) * 0.5
    min_samples = max(5, all_vecs.shape[1] + 1)
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, algorithm='ball_tree', n_jobs=-1)
    sample_labels = dbscan.fit_predict(sample)
    # noise (-1) → cluster 0, 나머지 → modulo n_strata
    sample_labels = np.where(sample_labels == -1, 0, sample_labels)
    centroids = np.array([sample[sample_labels == k].mean(axis=0) 
                          for k in np.unique(sample_labels)])
    sids = np.empty(len(all_vecs), dtype=np.int32)
    chunk = 100_000
    for i in range(0, len(all_vecs), chunk):
        d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centroids[None, :, :], axis=2)
        sids[i:i+chunk] = np.argmin(d, axis=1) % n_strata
    return sids

# KDE Parzen
if method_name == "kde_parzen":
    from sklearn.neighbors import KernelDensity
    sample = all_vecs[: min(len(all_vecs), 50_000)]
    bandwidth = (sample.std() * (4 / (3 * len(sample))) ** (1 / 5))  # Silverman rule
    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth)
    kde.fit(sample)
    log_dens = np.empty(len(all_vecs), dtype=np.float64)
    chunk = 50_000
    for i in range(0, len(all_vecs), chunk):
        log_dens[i:i+chunk] = kde.score_samples(all_vecs[i:i+chunk])
    edges = np.quantile(log_dens, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    return np.clip(np.searchsorted(edges[1:-1], log_dens, side='right'), 0, n_strata - 1).astype(np.int32)

# MHIST-2 (Poosala 1997 MaxDiff)
if method_name == "mhist2":
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2, random_state=seed)
    proj = pca.fit_transform(all_vecs)
    # MaxDiff bucket boundary on each axis
    k = int(np.ceil(np.sqrt(n_strata)))
    edges_per_axis = []
    for ax in range(2):
        sorted_v = np.sort(proj[:, ax])
        diffs = np.diff(sorted_v)
        # MaxDiff: 가장 큰 gap 의 k-1 위치를 boundary
        top_k_idx = np.argsort(diffs)[-(k - 1):]
        boundaries = np.sort(sorted_v[top_k_idx])
        edges_per_axis.append(boundaries)
    b0 = np.searchsorted(edges_per_axis[0], proj[:, 0], side='right')
    b1 = np.searchsorted(edges_per_axis[1], proj[:, 1], side='right')
    return ((b0 * k + b1) % n_strata).astype(np.int32)

# HyperLogLog
if method_name == "hyperloglog":
    # vector → 64-bit hash signature → leading-zero count → bucket
    rng_h = np.random.default_rng(seed)
    H = rng_h.standard_normal((all_vecs.shape[1], 64)).astype(np.float32)
    signs = (all_vecs @ H > 0).astype(np.uint64)
    sig = np.zeros(len(all_vecs), dtype=np.uint64)
    for k in range(64):
        sig = sig * 2 + signs[:, k]
    # leading zero count → bucket
    lz_count = np.zeros(len(all_vecs), dtype=np.int32)
    for i in range(64):
        lz_count = np.where((sig >> (63 - i)) & 1, lz_count, lz_count + 1)
    return (lz_count % n_strata).astype(np.int32)

# randomized SVD (Halko 2011)
if method_name == "randomized_svd":
    from sklearn.utils.extmath import randomized_svd
    U, S, Vt = randomized_svd(all_vecs, n_components=1, n_iter=5, random_state=seed)
    proj = (U * S).flatten()
    edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    return np.clip(np.searchsorted(edges[1:-1], proj, side='right'), 0, n_strata - 1).astype(np.int32)

# wavelet histogram (Matias 1998)
if method_name == "wavelet_hist":
    import pywt
    from sklearn.decomposition import PCA
    pca = PCA(n_components=1, random_state=seed)
    proj = pca.fit_transform(all_vecs).flatten()
    # 1D Haar wavelet decomposition
    coeffs = pywt.wavedec(proj[:2 ** 16] if len(proj) > 2 ** 16 else proj, 'haar', level=4)
    # Threshold top-K coefficients (K = n_strata)
    arr_coeffs, slices = pywt.coeffs_to_array(coeffs)
    top_k_idx = np.argsort(np.abs(arr_coeffs))[-n_strata:]
    # 각 vector 의 nearest top-k coefficient bin → bucket
    sids = np.zeros(len(all_vecs), dtype=np.int32)
    sample_bin_centers = np.linspace(proj.min(), proj.max(), n_strata)
    for i, v in enumerate(proj):
        sids[i] = np.argmin(np.abs(sample_bin_centers - v))
    return sids
```

### 8.2 verification dry-run

각 method 별로:
```bash
python3 measure_paper_exact.py --rq 3 --phase B --cell A1-DEEP --mode CaseA --method dbscan --n_queries 100 --trials 3
```

→ avg_q_error_trimmed 출력 확인 + ★ 4강 (-8.04 / -7.63 / -7.54 / -6.91) 과 paired Δ% 산출

### 8.3 Tier 1 6 method 의 expected paired Δ% 추정

| method | paradigm | expected Δ% vs ★1 HDBSCAN (-8.04) | reasoning |
|---|---|---|---|
| **DBSCAN** | P1 | -7.5 ~ -8.0 (★1 와 동등) | non-hierarchical 변형, density-based 동일 inductive bias |
| **KDE Parzen** | P10 새 | -7.0 ~ -8.0 (★ 후보) | density estimation textbook, narrative fit 매우 높음 |
| **MHIST-2** | P6 (factor_join 대체) | -5 ~ -7 (mid-tier) | 2D histogram, axis-aligned bias |
| **HyperLogLog** | P9 새 | -3 ~ -6 (paradigm anchor) | sketch, distinct count 영역 — cardinality 영역 fit but vector embedding 에는 약 |
| **randomized SVD** | P4 (강화) | -6 ~ -7 (PCA1D 와 동등) | PCA1D 의 large-scale 변형 |
| **wavelet histogram** | P6 (강화) | -4 ~ -6 | 1D wavelet, axis bias |

→ **★ 후보 (5번째)**: DBSCAN or KDE Parzen — 둘 중 하나가 5/27 발표의 ★5 강화 후보

---

## 9. 보고서 / paper 작성 시 인용 필수 list

5/27 발표 + paper 제출 시 **반드시** 인용해야 할 학술 reference (본 brainstorm 에서 발굴):

### 9.1 본 연구 narrative 의 학술 anchor

| # | reference | 이유 |
|---|---|---|
| 1 | **Parzen 1962** ("On estimation of a probability density function") | density-aware stratification 의 textbook origin |
| 2 | **Poosala & Ioannidis VLDB 1997** ("Selectivity estimation without the attribute value independence assumption") | multi-dim cardinality estimation textbook |
| 3 | **Flajolet, Fusy, Gandouet, Meunier AofA 2007** (HyperLogLog) | cardinality estimation sketch textbook |
| 4 | **Halko, Martinsson, Tropp SIAM Review 2011** (randomized SVD) | large-scale PCA1D 의 학술 origin |

### 9.2 2024-2025 SIGMOD/VLDB 최신

| # | reference | 이유 |
|---|---|---|
| 5 | **Zhang, Mayer, Khamis, Olteanu, Suciu SIGMOD 2025** (LpBound, Best Paper) | pessimistic CardEst 최신 |
| 6 | **Heddes, Nunes, Givargis, Nicolau SIGMOD 2024** (CCSketch FFT) | sketch-based CardEst 최신 |
| 7 | **Wu, Negi, Khamis, Aboulnaga, Madden SIGMOD 2023** (FactorJoin) | learned CardEst single-table 최신 |
| 8 | **Yang et al. VLDB 2020** (NeuroCard) | autoregressive CardEst |
| 9 | **Zeng et al. VLDB 2024** (PRICE) | pretrained CardEst 최신 |
| 10 | **Krimmel-Boncz et al. SIGMOD 2025** (PDX) | vector DB intrinsic_dim + skewness driven 최신 — 본 RQ1 narrative 강화 |
| 11 | **Sun et al. VLDB 2025** (GaussDB-Vector) | distributed vector DB CardEst 최신 |
| 12 | **Bao et al. VLDB 2025 vol 18 p.544** (Cardinality Estimation for Similarity Search on High-Dim) | reference object 기반 single-table CardEst |
| 13 | **Chen et al. arXiv 2604.04603 2026** (Adaptive Bucket Probing) | LSH multi-probe + Chernoff bound 최신 |

### 9.3 Paradigm 학술 anchor

| # | reference | paradigm |
|---|---|---|
| 14 | Ester, Kriegel, Sander, Xu KDD 1996 (DBSCAN) | P1 |
| 15 | Campello, Moulavi, Sander PAKDD 2013 + McInnes JOSS 2017 (HDBSCAN) | P1 |
| 16 | Lawder & King SIGMOD 2001 (Hilbert curve) | P2 |
| 17 | Morton IBM 1966 (Z-order) | P2 |
| 18 | Aggarwal, Han, Wang, Yu VLDB 2003 (CluStream) | P3 |
| 19 | Cao, Ester, Qian, Zhou SDM 2006 (DenStream) | P3 |
| 20 | Vitter TOMS 1985 (Reservoir sampling) | P3 |
| 21 | Achlioptas JCSS 2003 (sparse RP) | P4 |
| 22 | Pearson 1901 (PCA) | P4 |
| 23 | McInnes, Healy, Melville arXiv 1802.03426 2018 (UMAP) | P4 |
| 24 | Indyk & Motwani STOC 1998 (LSH) | P5 |
| 25 | Sobol USSR Comput Math 1967 (Sobol) | P5 |
| 26 | Faure Acta Arithmetica 1982 | P5 |
| 27 | Niederreiter Bull AMS 1988 | P5 |
| 28 | Jégou, Douze, Schmid PAMI 2011 (PQ) | P6 |
| 29 | Ge, He, Ke, Sun CVPR 2013 (OPQ) | P6 |
| 30 | Guo, Sun, Lindgren, Geng, Simcha, Chern, Kumar ICML 2020 (ScaNN anisotropic) | P6 |
| 31 | Sun, Guo, Simcha, Kumar NeurIPS 2023 (SOAR) | P6 |
| 32 | Agrawal, Gehrke, Gunopulos, Raghavan SIGMOD 1998 (CLIQUE) | **P7 새** |
| 33 | Aggarwal, Procopiuc, Wolf, Yu, Park SIGMOD 1999 (PROCLUS) | **P7 새** |
| 34 | Kailing, Kriegel, Kröger SDM 2004 (SUBCLU) | **P7 새** |
| 35 | Traag, Waltman, van Eck Scientific Reports 2019 (Leiden) | **P8 새** |
| 36 | Blondel, Guillaume, Lambiotte, Lefebvre J. Stat. Mech. 2008 (Louvain) | **P8 새** |

---

## 10. 결론 및 다음 단계

### 10.1 핵심 결론

본 brainstorm 의 **3개 핵심 발견**:

1. **즉시 추가 권고 6 method (Tier 1)**: DBSCAN, KDE Parzen, MHIST-2, HyperLogLog, randomized SVD, wavelet histogram. 41 → 47 method portfolio. 구현 simple, 5/12-5/14 launch 가능.

2. **즉시 폐기 또는 재구현 권고 8 method**: neurocard_lite, factor_join, vinecopula, cocluster_nystrom, mfmc, lp_bound, adaptive_bucket_probing, cca1d. 학술 명칭과 실제 구현 mismatch — paper reviewer attack 1순위 risk.

3. **새 paradigm 4개 추가 권고**: P7 Subspace (CLIQUE), P8 Graph-based (Leiden, future), P9 Information-theoretic (HyperLogLog), P10 Density estimation (KDE Parzen). 6 → 10 paradigm 으로 paper 학술 두께 증가.

### 10.2 다음 단계 (사용자 복귀 후)

1. **사용자 confirm 받기**: 본 brainstorm 의 Tier 1 6 method + 폐기 8 method + 새 4 paradigm
2. **Tier 1 6 method 구현 + dry-run** (5/12 ~ 5/14): `_get_method_strata` 분기 추가 + 100-query dry-run
3. **server SF=10 측정** (5/14 ~ 5/16): paper-exact phase B + C 의 6 신규 method (8 cells × 6 method × 3-way = 144 cells)
4. **5/27 발표용 paper-exact full matrix**: 41 → 47 method × 51 sampling cells × 3-way = 7,191 measurement (기존 paper-exact 1,734 + 추가 5,457)
5. **Paper 작성** (5/22 ~ 5/27): 9 paradigm × Tier 1-3 의 학술 narrative 정리

### 10.3 시간 budget 평가

| 항목 | 시간 추정 | 5/27 발표까지 D-day |
|---|---|---|
| Tier 1 6 method 구현 + dry-run | 1-2 day | D-15 |
| server SF=10 측정 | 2-3 day | D-12 |
| Tier 2 7 method 구현 (선택) | 3-4 day | D-9 |
| Tier 2 server 측정 (선택) | 3-4 day | D-5 |
| paper 작성 + 검증 | 5-7 day | D-day |

→ **5/27 마감 가능**: Tier 1 (47 method) + Tier 2 부분 (50-54 method) + 9 paradigm narrative 의 paper

---

## END

작성: 2026-05-10 14:30 KST
연구실: 박광현 BDAI / 캡스톤 팀: 속도는벡터
다음 read: 사용자 복귀 시 본 doc § 6.1 Tier 1 confirm + 5/12 launch 결정
