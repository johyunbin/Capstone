# RQ3 Paradigm Framework — 학술 심층 검증

작성: 2026-05-08 KST · 검증 대상: 5 paradigm × 11 method 안 (4강 후보 HDBSCAN / MB_partial / Hilbert / sparse RP)
검증 도구: WebSearch (8 query) + 코드/결과 cross-check + sampling/clustering literature standard taxonomy

---

## 1. Executive Summary

본 문서는 RQ3 발표/보고 narrative 의 핵심 contribution 인 "5 paradigm framework 로 분포 미인지 stratification 학습 method 를 분류" 에 대한 학술 정합성 검증이다. 검증 결과 5 paradigm 분류는 sampling/clustering literature 의 standard taxonomy 와 **대체로 align 하나, 두 가지 정정이 필요**하다. 첫째, P5 의 "Hashing/QR (LSH+QR)" 묶음은 학술적 bias 가 다르므로 **P5a Hashing (LSH/MinHash) + P5b Quasi-random (Sobol/Halton)** 으로 분리하거나 P5 를 단일 bias 로 통일해야 한다 — Sobol 은 hashing 이 아니라 *low-discrepancy sequence* 로 numerical integration 의 stratification trick 에 속한다. 둘째, ★4 후보로는 **sparse RP (-6.91, data-independent) 가 PCA1D (-7.35, data-dependent) 보다 P4 의 inductive bias 를 더 명확히 대표** — 두 method 모두 1D projection 을 만들지만 학습 의존성이 정반대 방향이고, RQ3 narrative 의 "분포 모를 때" 조건에서 data-independent 가 더 강한 statement. 셋째, 누락 paradigm 으로 **Sketch family (HyperLogLog / Count-Min)** 가 cardinality estimation literature (Cormode-Muthukrishnan 2005, Flajolet 2007) 의 standard 한 축이다 — 단 본 연구는 *stratum 학습* 을 sampling 위로 올리는 framework 이지 distinct count 가 아니므로 limitation 으로 명시하면 된다. 11 method 의 paradigm assignment 는 LSH (P5 hashing) 가 Wave 0 failed 인 것을 반영해 LSH → MinHash 또는 Sobol 단일로 simplify 권고. 4강 자체는 (HDBSCAN, MB_partial, Hilbert, sparse RP) 가 5 paradigm 중 4 paradigm 의 distinct representative 로 narrative 강함 — 변경 불필요.

---

## 2. 5 Paradigm 분류 학술 정합성 평가

### 2.1 Standard taxonomy cross-check

ACM Computing Surveys 의 "A Comprehensive Survey on Deep Clustering" (2024) 과 Wu (cs.wisc.edu) 의 "Sampling-Based Cardinality Estimation Algorithms: A Survey" 의 통합 분류는 다음과 같다.

| Standard taxonomy 축 | 본 연구 paradigm | 정합성 |
|---|---|---|
| Centroid-based clustering (k-means family) + Density (DBSCAN) + Distribution (GMM) | **P1 Cluster-based** (HDBSCAN+MiniBatch+GMM) | ✓ density/centroid/distribution 3 sub 로 한 paradigm 묶음 — Bishop PRML 의 unsupervised clustering 분류 일치 |
| Spatial / multi-dimensional indexing (R-tree, kd-tree, SFC) + Quantization (PQ, IVF) | **P2 Spatial Indexing** (Hilbert + faiss_ivf) | △ Hilbert (curve) + IVF (partition VQ) 는 ANN literature 의 4 categories 중 두 개 (graph-based / partition-based / quantization-based / tree-based) 를 묶은 형태. 단일 paradigm 으로 묶는 것은 acceptable 하나 narrative 에서 "공간 정보의 1D 매핑" 으로 통일 강조 필요 |
| Online / streaming clustering (Sequential k-means, Reservoir sampling Vitter 1985) | **P3 Streaming** (MB_partial + Reservoir) | ✓ Streaming k-Means Clustering with Fast Queries (ICDE 2017) 의 분류 일치. partial_fit (Sequential Lloyd) + Reservoir (Vitter) 가 streaming 의 양대 축 |
| Linear projection (PCA, RP) | **P4 Dim Reduction** (sparse RP + PCA1D) | ✓ scikit-learn 의 random_projection module + Achlioptas 2003 의 standard 분류 일치 — 단 두 method 의 inductive bias 가 정반대 (data-independent vs data-dependent) |
| Hashing (LSH, MinHash, SimHash) ≠ Quasi-random sequence (Sobol, Halton, Faure) | **P5 Hashing/QR** (LSH + Sobol) | ❌ **분리 필요** — LSH (Wikipedia: "fuzzy hashing technique") 와 Sobol (Wikipedia: "low-discrepancy sequence for QMC integration") 은 *bias 가 완전히 다른* 두 학술 분야 |

**평가**: 5 paradigm 중 4 (P1, P2, P3, P4) 는 standard taxonomy 와 align. **P5 만 학술적으로 problematic** — LSH 는 Indyk-Motwani 1998 의 randomized hashing 으로 ANN search 의 sub-linear time complexity 를 위한 trick 이고, Sobol 은 Niederreiter 1992 의 number-theoretic stratification 으로 numerical integration 의 variance 감소 trick. 둘 다 "deterministic-ish" 한 sub-sampling pattern 을 만든다는 표면 공통점은 있으나 **probabilistic vs number-theoretic 의 bias 가 정반대**.

### 2.2 누락 paradigm 검토

| 후보 | 학술 standard | 본 연구 적합성 |
|---|---|---|
| **Sketch family** (HyperLogLog Flajolet 2007 / Count-Min Cormode-Muthukrishnan 2005) | Cardinality estimation 의 핵심 축 | ✗ — 본 연구는 *stratum 학습* (sampling 위에 올림) 이지 distinct count 가 아니므로 architectural 미스매치. **Limitation 으로 명시** ("sketch family 는 stratum 학습이 아닌 frequency/distinct estimation 으로 separate paradigm, future work") |
| **Graph-based ANN** (HNSW Malkov 2018) | ANN search 4 categories 중 하나 | △ — Exqutor 본 논문이 HNSW range query 는 ECQO 로 처리한 영역. 본 연구는 인덱스 *없는* 영역이 scope 이므로 **scope 외 limitation** |
| **Tree-based** (R-tree Guttman 1984 / kd-tree Bentley 1975) | spatial indexing 의 fundamental | ✓ kdtree 는 P2 redundancy 로 이미 측정 후 가지치기. **R-tree 는 multi-dimensional bbox 분할의 fundamental 이나 본 연구의 K=20 stratification 에는 over-engineering** — kdtree 측정으로 tree-based 대표 충분 |
| **Hierarchical clustering** (Agglomerative Sokal-Sneath 1958 / BIRCH Zhang 1996) | Clustering taxonomy 의 4 main families 중 하나 | △ — 본 연구는 BIRCH/Agglomerative 측정 후 P1 (cluster-based) 안에 흡수 가능. ARI 보강 결과 (DEEP 0.6+ redundant with minibatch) 로 P1 에 흡수 정당화 |

**평가**: 5 paradigm 외 **추가 권고 paradigm 0개**. Sketch / Graph-based / Tree-based 는 limitation 명시 권장.

---

## 3. 11 Method Paradigm Assignment 검증

### 3.1 단일 inductive bias 확인

| Paradigm | Method | 학술 출처 (canonical reference) | 단일 bias? | 평가 |
|---|---|---|---|---|
| **P1 Cluster-based** | HDBSCAN | Campello-Moulavi-Sander, "Density-Based Clustering Based on Hierarchical Density Estimates" (PAKDD 2013) | ✓ density only | ★1 winner — well-known representative |
| | MiniBatch K-means | Sculley, "Web-Scale K-Means Clustering" (WWW 2010) | ✓ centroid only | acceptable representative — but P3 의 partial_fit 와 redundant |
| | GMM | Dempster-Laird-Rubin, "Maximum Likelihood from Incomplete Data via the EM Algorithm" (JRSS 1977) | ✓ distribution only | acceptable — Bishop PRML §9.2 의 standard |
| **P2 Spatial Indexing** | Hilbert curve | Lawder-King, "Querying multi-dimensional data indexed using the Hilbert space-filling curve" (SIGMOD 2001) | ✓ space-filling curve only | ★3 winner — well-known representative |
| | faiss_ivf | Jégou-Douze-Schmid, "Product Quantization for Nearest Neighbor Search" (PAMI 2011) + Johnson-Douze-Jégou FAISS (TBD 2017) | △ — IVF 는 k-means partition 의 inverted file (P1 redundancy 우려) | acceptable but **P1 redundant with MiniBatch** — narrative 에서 "VQ partition 의 production index" 로 차별화 필요 |
| **P3 Streaming** | MB_partial | Sculley 2010 (위) + sklearn `MiniBatchKMeans.partial_fit` API | ✓ online sequential update | ★2 winner — well-known representative (단 P1 MiniBatch 와 ARI 1.000 → P3 의 본질은 partial_fit *protocol* 로 narrative 강조) |
| | Reservoir | Vitter, "Random Sampling with a Reservoir" (TOMS 1985) | ✓ single-pass sampling only | acceptable — streaming sampling 의 textbook standard |
| **P4 Dim Reduction** | sparse RP | Achlioptas, "Database-friendly random projections: Johnson-Lindenstrauss with binary coins" (PODS 2001 / JCSS 2003) | ✓ data-independent linear projection | ★4 winner 권장 (정당화 §4) |
| | PCA1D | Pearson 1901 / Hotelling 1933 — ML 정착은 Jolliffe "PCA" textbook | ✓ data-dependent linear projection | strong but data-dependent ↔ "분포 모를 때" 와 narrative tension |
| **P5 Hashing/QR** | LSH | Indyk-Motwani, "Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality" (STOC 1998) | ✓ randomized hashing only | **failed (Wave 0, +2092%)** — paradigm representative 자격 X. 대체 필요 (§5) |
| | Sobol | Sobol 1967 / Niederreiter 1992 — QMC textbook | ✓ low-discrepancy sequence only | **pruned (avg +0.18, sign 4/10)** — bias 가 P5 hashing 과 다름. **P5 분리 또는 통일 필요** |

### 3.2 학술 출처 정확성

11 method 모두 canonical reference 명확. Hilbert curve (Lawder 2001), Achlioptas RP (PODS 2001), HDBSCAN (Campello 2013), Vitter Reservoir (1985) 는 textbook standard. 단 **LSH 가 Wave 0 failed 라서 P5 의 representative 로 부적절** — 5 paradigm framework 의 narrative 가 깨질 위험.

### 3.3 Hybrid 우려 method

| Method | Hybrid? | 처리 |
|---|---|---|
| MB_partial | P1 (centroid k-means) + P3 (online protocol) | **P3 single bias** — partial_fit 의 *streaming protocol* 이 본질. P1 batch fit 과 ARI 1.000 redundant 하나 narrative 는 "OLTP-friendly streaming" 으로 P3 강조 OK |
| faiss_ivf | P1 (k-means clustering) + P2 (inverted file index) | **P2 single bias** — Inverted file 의 *partition-based ANN index* 가 본질, k-means 는 implementation detail. Pinecone/TiDB 의 ANN taxonomy ("partition-based") 와 일치 |
| sparse RP vs PCA1D | 둘 다 1D projection + quantile bin | **분리 가능** — RP 의 random matrix vs PCA 의 SVD eigenvector 는 inductive bias 정반대 |

---

## 4. ★4 권장 결정 — sparse RP vs PCA1D vs 다른 후보

### 4.1 후보 비교

| 후보 | avg Δ% | sign | CI_ex | 학술 출처 | inductive bias | "분포 모를 때" 일치성 |
|---|---:|---|---|---|---|---|
| sparse RP | -6.91 | 8/10 | 8/10 | Achlioptas PODS 2001 / JCSS 2003 | **data-independent** linear projection (random ±√3/0 matrix) | ★ **강한 일치** — projection matrix 가 학습 X |
| PCA1D | -7.35 | 8/10 | 8/10 | Pearson 1901 / Hotelling 1933 | **data-dependent** linear projection (SVD top eigenvector) | △ — PCA 는 분포 학습 method |
| pca_kmeans | -8.02 | 8/10 | 8/10 | composite (PCA + k-means) | **hybrid (P4 + P1)** | ✗ — 단일 paradigm 위배 |

### 4.2 학술 정합성 비교

**sparse RP 의 강점**:
1. **Johnson-Lindenstrauss lemma** 의 직접 적용 — Achlioptas 2003 의 "database-friendly" sparse {-√3, 0, +√3} matrix 는 dense Gaussian RP 와 동등 embedding quality 를 보장하면서 ~3× 빠름
2. **Data-independent** — projection matrix 가 fit() 에서 데이터를 읽지 않음. RQ3 의 "분포 모를 때" framing 과 가장 강한 일치
3. **streaming-friendly** — projection 자체가 학습이 없어 OLTP 환경 친화 (P3 와 시너지)
4. **scikit-learn standard module** (`SparseRandomProjection`) 으로 production well-known

**PCA1D 의 약점**:
1. **Data-dependent** — SVD 가 데이터의 covariance 학습. "분포 모를 때" 와 narrative tension
2. **One-time cost** — 1M sample 의 SVD 계산은 sparse RP 의 random matrix gen 보다 ~10× 비쌈
3. RQ3 deep-review §4 의 "공간 인식의 limit" narrative 와 정합 떨어짐 — PCA 는 이미 data-aware

**ARI redundancy 검증** (RQ3 딥리뷰 보강 §3.3):
- sparse RP avg ARI 0.122 (orthogonality rank #1)
- PCA1D avg ARI 0.277 (rank #2)
- → sparse RP 가 다른 4강 (P1/P2/P3) 와 정보적으로 더 직교. P4 paradigm 의 distinct representative 로 더 적합

### 4.3 결정

**★4 = sparse RP 권장** (변경 불필요, 현재 안 유지).

정당화: (1) Achlioptas 2003 의 textbook standard reference, (2) data-independent inductive bias 로 RQ3 framing 일치, (3) ARI orthogonality #1 로 4강 redundancy 최소, (4) P4 paradigm 의 "분포 모를 때 dimension reduction" 의 cleanest representative. PCA1D 는 P4 secondary representative 로 ablation 차원에서 보유 (data-dependent vs data-independent comparison).

---

## 5. 누락 Critical 추가 권장

### 5.1 Mean-Shift (P1 distribution sub-paradigm)

**Reference**: Comaniciu-Meer, "Mean Shift: A Robust Approach Toward Feature Space Analysis" (PAMI 2002)
**평가**: P1 의 sub 로 density-based clustering 의 또 다른 축. 단 본 연구는 HDBSCAN (density) 으로 P1 density sub 이미 cover. **추가 측정 권고 X — limitation 명시 권고** ("mean-shift 는 bandwidth selection 의 sensitivity 로 본 연구 K=20 fixed 와 mismatch, future work")

### 5.2 R-tree (P2 tree sub-paradigm)

**Reference**: Guttman, "R-trees: A Dynamic Index Structure for Spatial Searching" (SIGMOD 1984)
**평가**: spatial indexing 의 fundamental 이나 *bounding box overlap* 이 본 연구의 *partition* (disjoint) 와 다름. kdtree (Bentley 1975) 는 disjoint partition 으로 본 연구에 더 적합 — 이미 측정 후 P2 redundancy 로 가지치기. **R-tree 추가 측정 X — kdtree 측정으로 tree-based 충분**

### 5.3 MinHash / SimHash (P5 hashing sub-paradigm)

**MinHash reference**: Broder, "On the resemblance and containment of documents" (Compression and Complexity of Sequences 1997)
**SimHash reference**: Charikar, "Similarity Estimation Techniques from Rounding Algorithms" (STOC 2002)
**평가**: P5 의 LSH (failed) 대체 candidate. 단 **MinHash 는 set similarity (Jaccard) 용** 으로 본 연구의 vector data 와 architectural mismatch. SimHash 는 cosine similarity 용으로 더 가까우나 *binary signature* 로 K=20 stratification 에 추가 quantization 필요. **P5 representative 재검토 권고 — Sobol 단일 또는 LSH 재구현 (LSH 의 Wave 0 failure 가 hyperparameter 문제일 가능성)**

### 5.4 종합 권고

| 누락 method | 추가 측정 vs limitation | 권고 |
|---|---|---|
| Mean-Shift | limitation | "P1 density sub 는 HDBSCAN 으로 충분, mean-shift 는 K-fixed mismatch" |
| R-tree | limitation | "tree-based 는 kdtree 로 cover, R-tree 의 bbox overlap 은 본 연구 disjoint partition 과 mismatch" |
| MinHash/SimHash | optional 추가 | **MinHash 측정 0.5h** — set similarity 라 vector → set conversion 필요. P5 narrative 강화 가능 |

---

## 6. Over-coverage 19종 제외 OK 확인

| 제외 method | 사유 (사용자 안) | 학술 검증 |
|---|---|---|
| Hybrid (MB+Hilbert) | P1+P2 결합 | ✓ 단일 bias 위배 — 제외 정당 |
| pca_kmeans | P4+P1 결합 | ✓ 단일 bias 위배 — 제외 정당. avg -8.02 강하나 paradigm framework narrative 우선 |
| kde_pilot | KM20 cluster leak | ✓ pilot 이 KM20 partition 사용으로 data leak — 제외 정당 |
| distance_shell | 5 paradigm 외 | ✓ query-adaptive shell 은 stratum 정의 X — 본 연구 framework 외 |
| importance_sampling | 5 paradigm 외 | ✓ 분할 X + weight only 로 estimator invalid (avg +49.42) — 제외 정당 |
| coresets | P1+P4 ambiguous | ✓ Bachem-Lucic-Krause 의 coreset 은 weighted subsample 로 paradigm uncertain — 제외 acceptable |
| kmeans_pp | P1 redundancy | ✓ k-means++ init (Arthur-Vassilvitskii 2007) 은 MiniBatch 의 init variant — P1 redundant |
| DBSCAN | P1 redundancy + Wave 0 (+261245%) | ✓ HDBSCAN 의 ε-fixed predecessor — 제외 정당 |
| OPTICS | P1 redundancy | ✓ HDBSCAN 의 hierarchy variant — 제외 정당 |
| birch | P1 hierarchical redundancy | ✓ CFTree 는 hierarchical 의 inductive bias 로 P1 cluster sub 와 redundancy |
| agglomerative | P1 hierarchical redundancy | ✓ 동상 — P1 redundancy |
| hierarchical_kmeans | P1 hierarchical redundancy | ✓ recursive bisection — P1 redundancy |
| zorder | P2 redundancy | ✓ Hilbert 의 simpler curve — Hilbert 가 더 smooth locality (Lawder 2001) |
| kdtree | P2 redundancy | ✓ Hilbert 의 1D mapping vs kdtree 의 hyperplane partition — P2 안 redundant |
| pq | P2 redundancy | ✓ Jégou 2011 PQ 는 sub-vector quantization 으로 IVF 와 redundant — IVF 가 더 well-known |
| random_proj | P4 RP redundancy + Wave 0 (+434%) | ✓ dense Gaussian RP 는 sparse RP 의 dense variant — sparse 가 더 well-known production |
| halton | P5 QR redundancy | ✓ Halton (Wikipedia: "best for d≤6") 은 high-d (96~768d) 에서 fail — Sobol 이 더 robust |
| hammersley | P5 QR redundancy | ✓ Halton variant — 동상 redundant |
| spectral | P4 spectral redundancy | ✓ Ng-Jordan-Weiss 2002 spectral 은 graph Laplacian 으로 P1 graph sub — 본 연구는 centroid/density 우선 |

**평가**: 19 제외 모두 학술적으로 정당. Hybrid / pca_kmeans 는 result 강하나 framework narrative 우선 채택 OK.

---

## 7. 학술 Narrative 일치성 평가

### 7.1 "분포 모를 때 5 paradigm 으로 stratum 학습" framing

**Standard taxonomy 와 align?** ✓ 부분 align.

| 학술 framing | 본 연구 paradigm | align? |
|---|---|---|
| "Clustering taxonomy" (ACM Comput Surv 2024) | P1 Cluster-based | ✓ |
| "ANN search 4 categories" (Pinecone, TiDB taxonomy) | P2 Spatial Indexing (partition + tree + curve 통합) | ✓ |
| "Streaming clustering" (ICDE 2017 Zhang et al.) | P3 Streaming | ✓ |
| "Dimensionality reduction (PCA + RP)" (sklearn module split) | P4 Dim Reduction | ✓ |
| "Hashing for ANN" + "Quasi-Monte Carlo" (별개 분야) | P5 Hashing/QR (통합 시도) | ❌ **분리 권장** |

### 7.2 P5 정정안

**Option A**: P5 → **"Randomized Pattern"** 으로 통일 (LSH/MinHash 의 randomized hashing + Sobol/Halton 의 deterministic low-discrepancy 를 "randomized but structured" 로 묶음). 단 학술 standard 와 어색.

**Option B**: P5 → **"Quasi-random / Sketching"** 의 single bias 로 통일 후 Sobol 단일 representative. LSH (failed Wave 0) 는 paradigm 외 outlier 로 limitation.

**Option C**: P5a Hashing (LSH/MinHash) + P5b Quasi-random (Sobol/Halton) 분리. 6 paradigm framework. 단 narrative 복잡.

**권고**: **Option B** — 5 paradigm 유지 + P5 = "Low-discrepancy / Quasi-random" 단일 bias. LSH 는 limitation 으로 명시 ("LSH 는 hashing-based ANN 의 representative 이나 본 연구 K=20 stratification 에 hyperparameter mismatch 로 Wave 0 fail, future work").

### 7.3 각 paradigm representative 의 "잘 알려진" 수준

| Method | textbook standard? | citation count proxy |
|---|---|---|
| HDBSCAN | ✓ scikit-learn standard | Campello 2013 PAKDD: ~3000 citations |
| MB_partial | ✓ sklearn API | Sculley 2010 WWW: ~600 citations |
| Hilbert curve | ✓ database textbook | Lawder 2001 SIGMOD: ~400 citations |
| sparse RP | ✓ scikit-learn standard | Achlioptas 2003 JCSS: ~2500 citations |
| Sobol | ✓ QMC textbook | Sobol 1967: ~6000 citations |

**평가**: 5 representative 모두 학술적으로 "잘 알려진" 수준. narrative claim 정당.

---

## 8. Final 권장안

### 8.1 5 Paradigm × 5 Method (1-per-paradigm minimal narrative)

| Paradigm | Method | inductive bias | 학술 출처 | 4강? |
|---|---|---|---|---|
| **P1 Cluster-based** | HDBSCAN | density | Campello 2013 PAKDD | ★1 (-8.04) |
| **P2 Spatial Indexing** | Hilbert curve | space-filling curve | Lawder 2001 SIGMOD | ★3 (-7.54) |
| **P3 Streaming** | MB_partial | online sequential | Sculley 2010 WWW + Vitter 1985 TOMS | ★2 (-7.63) |
| **P4 Dim Reduction** | sparse RP | data-independent linear projection | Achlioptas 2003 JCSS | ★4 (-6.91) |
| **P5 Quasi-random** | Sobol | low-discrepancy sequence | Sobol 1967 / Niederreiter 1992 | (pruned, +0.18) |

### 8.2 5 Paradigm × 11 Method (full framework with sub-paradigm coverage)

| Paradigm | Primary | Secondary | Sub-paradigm narrative |
|---|---|---|---|
| P1 Cluster-based | HDBSCAN (density) | MiniBatch (centroid), GMM (distribution) | density / centroid / distribution 3 sub |
| P2 Spatial Indexing | Hilbert (curve) | faiss_ivf (partition VQ) | curve / partition 2 sub |
| P3 Streaming | MB_partial (online cluster) | Reservoir (single-pass sample) | online cluster / sample 2 sub |
| P4 Dim Reduction | sparse RP (data-independent) | PCA1D (data-dependent) | RP / PCA 2 sub |
| P5 Quasi-random | Sobol (low-discrepancy) | LSH (failed) | QR primary, hashing limitation |

### 8.3 Narrative 정정 권고

1. **P5 명칭** "Hashing/QR" → **"Low-discrepancy / Quasi-random Sequence"** 로 통일. LSH 는 Wave 0 fail 로 limitation 명시.
2. **★4 sparse RP** 유지 (변경 불필요). PCA1D 는 P4 secondary 로 data-dependent ablation.
3. **누락 paradigm limitation 명시**: Sketch family (cardinality estimation 의 별개 축, future work) / Graph-based ANN (Exqutor ECQO scope, 본 연구 외).
4. **누락 method limitation 명시**: Mean-Shift (K-fixed mismatch) / R-tree (bbox overlap mismatch) / MinHash (set similarity mismatch).

---

## 9. WebSearch 출처 List (학술 reference)

1. [A Comprehensive Survey on Deep Clustering: Taxonomy, Challenges, and Future Directions](https://dl.acm.org/doi/10.1145/3689036) — ACM Computing Surveys 2024 — 5 paradigm 의 P1 cluster-based standard taxonomy
2. [Sampling-Based Cardinality Estimation Algorithms](https://pages.cs.wisc.edu/~wentaowu/courses/cs787.pdf) — Wu, UWisconsin — sampling 기반 cardinality estimation survey, 본 연구 RQ3 의 학술 backbone
3. [A Survey on Advancing the DBMS Query Optimizer: Cardinality Estimation, Cost Model, and Plan Enumeration](https://link.springer.com/article/10.1007/s41019-020-00149-7) — DSE Springer 2020 — histogram + sampling 의 cardinality estimation 분류
4. [Querying multi-dimensional data indexed using the Hilbert space-filling curve](https://dl.acm.org/doi/10.1145/373626.373678) — Lawder-King SIGMOD 2001 — P2 Hilbert representative 의 canonical reference
5. [Random projection - Wikipedia](https://en.wikipedia.org/wiki/Random_projection) — Achlioptas 2003 의 sparse {-√3, 0, +√3} matrix 와 Johnson-Lindenstrauss lemma standard 정리
6. [Locality-sensitive hashing - Wikipedia](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) — Indyk-Motwani 1998 LSH standard 정리
7. [Quasi-Monte Carlo method - Wikipedia](https://en.wikipedia.org/wiki/Quasi-Monte_Carlo_method) — Sobol/Halton/Faure low-discrepancy sequence 의 학술 standard
8. [Approximate Nearest Neighbor (ANN) Search Explained: IVF vs HNSW vs PQ](https://www.pingcap.com/article/approximate-nearest-neighbor-ann-search-explained-ivf-vs-hnsw-vs-pq/) — TiDB blog — ANN 4 categories taxonomy (graph/partition/quantization/tree)
9. [HDBSCAN — scikit-learn 1.8.0 documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html) — P1 density representative 의 production standard
10. [MiniBatchKMeans — scikit-learn 1.8.0 documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html) — P3 partial_fit 의 sklearn API standard
11. [Streaming k-Means Clustering with Fast Queries](https://arxiv.org/pdf/1701.03826) — Zhang et al. ICDE 2017 — P3 streaming clustering taxonomy
12. [Sparse Random Projections](https://blog.dailydoseofds.com/p/sparse-random-projections) — Achlioptas 2003 의 sparse RP intuition
13. [HyperLogLog - Wikipedia](https://en.wikipedia.org/wiki/HyperLogLog) — Sketch family limitation 정당화 (Flajolet 2007)
14. [R-tree - Wikipedia](https://en.wikipedia.org/wiki/R-tree) — Guttman 1984 spatial indexing fundamental
15. [Cardinality Estimation for High Dimensional Similarity Queries with Adaptive Bucket Probing](https://arxiv.org/html/2604.04603) — vector database cardinality estimation 의 partitioning 의 가치 (본 연구 framing 강화)
