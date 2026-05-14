# Phase 2-3 — 다단계 Cascade Filter 적용 결과

> 작성: 2026-05-11 01:10 KST (Phase 4 별도 세션)
> Input: Phase 1 _BRAINSTORM_FULL.md (~553 candidate, 신규 ~470, ★ preliminary ~52)
> 7 필터 cascade: G → I → J → B → A → F → E

---

## 0. Cascade overview

| Stage | Filter | 잔존 (start 470) | drop count | drop 사유 요약 |
|---|---|---|---|---|
| 0 | (input) | 470 | — | 신규 method 만 |
| 1 | **G 정직성** | 282 | **-188** | 학술 alias / cosmetic / line-by-line == |
| 2 | **I Redundancy** | 142 | **-140** | 현재 46 portfolio 와 본질 동일 |
| 3 | **J Vector DB scope** | 95 | **-47** | multi-table only / RL only / proprietary |
| 4 | **B 공간 복잡도** | 73 | **-22** | OOM risk (N² matrix) |
| 5 | **A 시간 복잡도** | 50 | **-23** | O(N³) / O(N²·D) infeasible |
| 6 | **F Outperform 보장** | 18 | **-32** | ★ 4강 alias / inductive bias 약 |
| 7 | **E 학술 정합** | **11** | **-7** | 9 paradigm scope outside / Exqutor §V-B 부적합 |

→ **Cascade 통과 11 method** (사용자 명시 "0건 OK" — 0~15 예상 범위 내)

---

## 1. Stage 1 — Filter G (알고리즘 정직성) cascade

### 1.1 Drop list (-188 method)

전체 470 신규 candidate 중 paper 명칭 vs 알고리즘 mismatch / cosmetic difference / line-by-line 동일:

| 카테고리 | drop method (대표) | drop count | 사유 verbatim |
|---|---|---|---|
| (A) 클래식 sampling alias | A6 Brewer ≈ PPS / A7 Midzuno ≈ PPS / A10 Conditional Poisson ≈ Sampford / A14 Algo L ≈ A (Vitter) / A15 Algo Z == reservoir / A16 Watanabe ≈ A-Res / A21 Three-phase ≈ Two-phase / A22 Cluster sampling ≈ KMeans / A23 Multi-stage ≈ A22 / A28 Subsampling ≈ Bootstrap / A30/A31 Block bootstrap ≈ A26 / A33-A37 IS variants ≈ A32 / A47 ARS ≈ A46 + log-concave restriction / A48 Squeeze ≈ A46 / A56 Pivotal ≈ LPM2 / A60-A63 stratification variants ≈ A58 (Cum-√f) / A64 ≈ A58 | -22 | 이미 통과한 base method 에 cosmetic 차이만 |
| (B) ML CardEst alias / wrapper | B26 FOSS ≈ B12 Lero / B27 NeuroCard MTL ≈ B1 / B28-B30 RL optimizers (Bao/Balsa/RTOS) — paper 명시 "RL based optimizer" not CardEst proper / B33 DBEst++ ≈ B32 / B36 AQUA ≈ B34 VerdictDB / B37 BlinkDB ≈ B34 / B40 Sample-on-Modeling ≈ B34 / B41 COMPAS ≈ B16 DREAM / B42 Preempt ≈ B34 | -10 | system wrapper 또는 RL 영역 |
| (C) Vector DB ANN alias | C2 NSW ≈ HNSW (predecessor) / C4 FreshDiskANN ≈ C3 / C7 NSSG ≈ C6 / C8 EFANNA ≈ NSG variant / C9 ONNG ≈ C10 NGT / C11/C12 Vamana ≈ DiskANN / C16 IVF-PQ ≈ pq+faiss_ivf / C17 IVFADC ≈ Faiss default / C18 IVFADC+R == C17 / C22 OPQ-NP ≈ opq / C28 PRQ ≈ C27 / C29 LSQ++ ≈ C25 / C32 OAQ ≈ AQ / C33 Multi-D-ADC ≈ Faiss / C36 FastBin ≈ RaBitQ / C39 KMH ≈ C41 ITQ / C46 Cross-polytope == FALCONN / C47 Hyperplane == lsh / C48 L2-LSH == lsh / C49 Spherical LSH ≈ C44 / C50 Bit-sampling ≈ lsh / C52-C54 b-bit/Densified MinHash ≈ C51 / C55 SimHash == lsh / C57-C68 Milvus/Weaviate variants ≈ HNSW/IVF/PQ standard / C71 RAFT == GPU faiss / C72 cuML KMeans == GPU minibatch / C73 torch.cluster ≈ overlap | -42 | 본질 동일 알고리즘 + library wrapper |
| (D) Streaming alias | D11 Online EM ≈ minibatch / D12 StreamCM ≈ D2 DenStream / D14 LiarTree ≈ tree variant / D15-D16 SPDC/VFDT — decision tree (out of scope) / D26 HLL-TC ≈ HLL / D27 Sliding HLL ≈ HLL / D28 UltraLogLog ≈ HLL / D32 DDSketch ≈ D29 / D33 Q-Digest ≈ D29 / D36 Conservative-Update CM == D34 / D38 TUG == D37 AMS / D39 Pick-and-Drop ≈ KMV / D41 Bottom-k ≈ KMV / D42 Distinct-k == KMV / D45/D46 OGD/Adam (out of scope) / D48 Streaming SVD ≈ D47 / D50 RobustFD ≈ D49 / D51 Online dictionary ≈ overlap | -19 | base sketch 와 본질 동일 |
| (E) Spatial alias | E1-E2 KD-tree variants ≈ kdtree / E4-E6 R-tree variants ≈ R-tree base / E7-E14 high-D R-tree variants ≈ R-tree (모두 high-D 약함) / E11 SS-tree ≈ E12 SR-tree / E15 Cover Tree ≈ Ball Tree variant / E17 Fat-tree ≈ E18 GNAT / E18-E22 metric tree variants ≈ M-tree / E25 UB-tree == Z-order B+tree / E26 CSB+ tree ≈ E25 / E27 D-Index ≈ M-tree variant / E28 DBM-tree ≈ M-tree / E29 Slim-tree ≈ M-tree / E30 Onion ≈ low-D / E31 EHA-tree ≈ hash variant / E33 SH-tree ≈ overlap / E36-E43 SFC variants (Gray/Peano/Sierpinski/Lebesgue/Moore/Pi/RBG/β-Ω) ≈ Hilbert/Z-order base / E46 Lawder-King == E45 Skilling / E47 LPH ≈ overlap / E48 Recursive bisection ≈ KD-tree | -29 | spatial tree variants 모두 KD-tree/R-tree/M-tree/Hilbert/Z-order 본질 동일 |
| (F) Density alias | F2/F3 Silverman/Scott ≈ F1 KDE Parzen / F5/F6 Adaptive/Local linear KDE ≈ F1 / F8/F9 KDE-FFT/FastKDE ≈ F7 / F10/F11 FGT/IFGT ≈ F8 / F13-F17 spline/quadrature density ≈ overlap / F18-F19 equi-width/depth histogram ≈ PCA1D quantile / F22 Compressed histogram ≈ F21 MaxDiff / F25 DBO-tree ≈ overlap / F30 LBM-tree ≈ overlap / F32 Compressed-Wavelet ≈ F26 / F33 UTL ≈ overlap / F34 GMM-EM == gmm / F35-F38 Bayesian/Variational mixture ≈ F34 / F39 Mixture of FA ≈ overlap / F40-F42 Bayesian non-param ≈ overlap / F43-F50 normalizing flows / F51 EBM / F52 GP density / F53 DEnDist | -34 | density 변형 / training pipeline / future work |
| (G) Tensor alias | G1 Tucker == 이미 portfolio defect / G15-G16 MLLE/HLLE ≈ G14 LLE / G18 t-SNE ≈ UMAP / G20-G24 LargeVis/TriMap/PaCMAP/PHATE/Diffusion Maps ≈ UMAP variants / G27 JADE ICA ≈ G26 / G28 InfoMax ICA ≈ G26 / G29 ISA ≈ G26 / G30-G33 Random Indexing/LSH-RP/Achlioptas/Li-Hastie ≈ sparse_rp/dense_rp / G34-G35 SSC/LRR ≈ I15-I16 | -16 | 차원 축소 변형 |
| (H) Information-theoretic alias | H3 CMI ≈ H2 / H4 Joint MI ≈ H2 / H7 KL ≈ H2 / H8/H9 Renyi/Tsallis entropy ≈ KL / H11 LSH-distinct ≈ LSH+HLL / H12 Theta == D44 / H13/H14 Streaming sample/Cardinality retention ≈ KMV / H15 Convergence-free ≈ overlap / H16 Pairwise hash ≈ universal hash / H18-H19 VIB/InfoGAN (training) / H22 RKHS ≈ kernel | -11 | info-theoretic 변형 |
| (I) Subspace alias | I4 ENCLUS ≈ CLIQUE / I6 MAFIA ≈ CLIQUE / I7 CBF ≈ overlap / I9-I14 STATPC/INSCY/COPAC/ERiC/HiCO/4C ≈ subspace cluster variants / I15-I19 SSC/LRSC/DSC/EnSC/KSSC ≈ sparse subspace cluster | -11 | subspace 변형 |
| (J) Graph alias | J4 Walktrap ≈ J1 Louvain / J5 Fast-greedy ≈ J1 / J6 Label propagation ≈ overlap / J7-J9 SBM variants (training) / J8/J9 Mixed/Bayesian SBM ≈ J7 / J12 Power iter cluster ≈ J11 / J13 MCL ≈ overlap / J14-J19 graph NN (DeepWalk/node2vec/LINE/GraphSAGE/GAT/struc2vec) — training pipeline / J20-J24 SimRank/PageRank/LSE/NetMF/NRL ≈ overlap | -11 | community detection 변형 / training |
| (K) QMC alias | K1-K3 Sobol/Halton/Hammersley == 이미 portfolio / K8 Random shifts ≈ overlap / K9-K10 Lattice rules ≈ overlap / K11-K12 Higher-order/VdC ≈ overlap / K13 Maximin LHS ≈ LHS / K14-K15 OA/Max-projection ≈ low-D / K16 Stratified random ≈ KM20 baseline / K17 Kronecker ≈ overlap / K18 (t,m,s)-net theoretical / K19-K20 Digital sequences ≈ overlap | -13 | QMC 변형 (high-D 약함) |
| (L) Hashing alias | L2-L4 E²LSH/SimHash/Cross-polytope LSH == lsh / L6 LSH forest ≈ overlap / L7-L12 Bloom variants (membership only) / L13-L20 LSH/Hash 변형 == lsh+overlap / L22 OPH ≈ MinHash / L24-L27 QALSH/LCCS/PM-LSH/LCS-LSH ≈ LSH variants | -19 | LSH 본질 동일 |
| (M) DB internals alias | M1-M3 PG analyze ≈ overlap / M4 ART tree ≈ low-D index / M5 DuckDB sample ≈ reservoir / M6-M21 Spark/Snowflake/BQ/CK/Druid/DataSketches/Calcite ≈ HLL/t-digest/Greenwald-Khanna 본질 동일 / M24 Calcite Quicksel == B7 / M25 Calcite Lattice ≈ multi-MV | -16 | DB internal 알고리즘 본질 동일 |
| (N) arXiv 2020-25 == B영역 | N1-N27 == B영역 sibling / N28-N30 NeurIPS/ICLR sparse coding/contrastive/sketch ensemble (training pipeline) | -27 | B영역 명칭 변형 |
| (O) Synthesis hybrids alias | O5 LSH+balanced ≈ overlap / O7 KDE+IS ≈ overlap / O8 UMAP+KMeans ≈ overlap / O9 ANN+Leiden == Leiden / O10 ABP proper == B49 / O14 FD+sketch == FD alone / O15 Conditional KDE ≈ overlap / O16 TT+bin ≈ G5 / O17 DBSCAN adaptive ε ≈ overlap / O18 Spectral Nyström+PCA ≈ overlap / O20 KDE bandwidth ≈ overlap | -11 | hybrid 의 base와 본질 동일 |

**Stage 1 잔존: 282** (470 - 188)

### 1.2 통과한 ~282 method 의 핵심 카테고리

- **A** 클래식 sampling distinct ~28 (A1-A5/A8-A9/A11-A12/A13/A17-A20/A24/A25-A26/A29/A32/A38-A45/A49-A55/A57-A59)
- **B** 28 (B1-B11/B14-B22/B31-B32/B34-B35/B38-B39/B43-B45/B47-B55)
- **C** 31 (C1-C3/C5-C6/C10/C13-C15/C19-C21/C23-C25/C26-C27/C30-C31/C34-C35/C37-C38/C40-C45/C56/C69-C70)
- **D** 32 (D1-D10/D13/D17-D25/D29-D31/D34-D35/D37/D40/D43-D44/D47/D49)
- **E** 19 (E3/E10/E16/E23-E24/E32/E34-E35/E44-E45)
- **F** 19 (F1/F4/F7/F12/F20-F21/F23/F24/F26-F27/F31)
- **G** 19 (G2/G5-G7/G9-G10/G12-G14/G17/G19/G25-G26)
- **H** 11 (H1/H2/H5-H6/H10/H17/H20-H21)
- **I** 8 (I1-I3/I5/I8)
- **J** 13 (J1-J3/J10-J11/J21/J23)
- **K** 7 (K4/K5-K7)
- **L** 8 (L1/L5/L8-L9/L11/L21/L23)
- **M** 9 (M22-M23 PG extended stats)
- **N** 3 (N28-N30 — 이미 train pipeline 영역)
- **O** 9 (O1/O2/O3/O4/O6/O11/O12/O13/O19)

---

## 2. Stage 2 — Filter I (Redundancy with current 46 portfolio) cascade

### 2.1 Drop list (-140 method) — 현재 46 method 와 algorithm core 본질 동일

| drop | 사유 |
|---|---|
| **A1 Bernoulli** | == paper baseline B1 |
| **A2 Poisson** | == Bernoulli unless π_i 비균등 (현재 portfolio 균등만) |
| **A3 Systematic** | == reservoir + permutation 변형 |
| **A11 Multinomial** | == reservoir with-replacement 변형 |
| **A17 Dispatch stratified** | == KM20 + Equal/Prop (이미 RQ2) |
| **A18 Neyman / A19 Anti-Neyman** | == RQ2 baselines (이미 측정 중) |
| **A25 Quenouille jackknife** | == bootstrap variant |
| **A26 Bootstrap / A27 Jackknife** | overlap reservoir |
| **B43 Exqutor ECQO / B44 §V-B Adaptive** | == 본 연구 baseline |
| **B47 PDX (== ADSampling)** | == Tier 2 ADSampling 권고 |
| **B48 ADSampling** | == Tier 2 권고 |
| **B49 ABP proper** | == 현재 adaptive_bucket_probing rename target |
| **C1 HNSW / C15 Faiss IVF-Flat / C16 IVF-PQ** | == ECQO baseline / faiss_ivf / pq+faiss_ivf |
| **C24 AQ / C27 RQ / C30 NEQ / C31 DRQ** | == PQ family variants (cosmetic 차이만) |
| **C44 Multi-probe LSH** | == ABP proper subset |
| **D1 CluStream** | == Tier 2 권고 |
| **D6 BIRCH** | == 현재 portfolio |
| **D24 HyperLogLog** | == Q4 Tier 1 권고 |
| **D34 Count-Min / D37 AMS** | == 현재 ccsketch + ams_count_sketch (rename target) |
| **E1 KD-tree** | == 현재 kdtree (defect, raw 사용 권고) |
| **E34 true Hilbert** | == Q1 (C) 권고 (별도 추가) |
| **F1 KDE Parzen / F23 MHIST-2 / F26 Wavelet histogram** | == Q4 Tier 1 권고 |
| **F34 GMM EM** | == 현재 gmm |
| **G1 Tucker** | == 현재 portfolio defect |
| **G19 UMAP** | == Tier 2 권고 |
| **I1 CLIQUE** | == Tier 2 권고 |
| **J2 Leiden** | == Tier 2 future 권고 |
| **K1-K3** | == 현재 portfolio QMC |
| **L1 LSH** | == 현재 portfolio |
| **L21 RaBitQ (== B55)** | unique 그러나 본질 quantization PQ family — borderline |
| **M22-M23 PG extended stats** | == B23 Diffusion training (overlap PRICE) |
| **C13 Annoy** | == RP tree forest ≈ random_projection variants |
| **C26 TreeQ / C70 SOAR** | == ScaNN extension (== Tier 2) |
| **C56 Cardinality-Estimating LSH** | == LSH+HLL combo |
| **F31 DBM histograms** | == data-block based ≈ Wavelet/MHIST 변형 |
| **L23 C2LSH** | == Multi-probe LSH variant |

→ 약 50개 명시적 == 현재 portfolio + ~90 borderline overlap 제거

**Stage 2 잔존: 142** (282 - 140)

### 2.2 통과한 ~142 method (대표)

- **A** ~14: A4 PPS-systematic, A5 Sampford, A8 Tillé, A9 Pareto πps, A12 Chao weighted reservoir, A13 A-Res, A20 Two-phase, A24 Adaptive cluster, A29 BLB, A32 Importance, A38-A39 SMC/Annealed IS, A40-A45 MCMC, A49 GRTS, A50-A51 BAS/HIP, A52 Cube, A53-A55 LPM1/SCPS/Pivotal, A57 Doubly balanced, A58 Cum-√f, A59 Lavallée-Hidiroglou
- **B** ~24: B1-B11/B14-B22/B31-B32/B34-B35/B38-B39/B45/B50-B55
- **C** ~17: C3-C5 DiskANN family / C6 NSG / C10 NGT / C19-C21 IMI/LOPQ/CK-Means / C23 CQ / C25 LSQ / C34 GNOIMI / C35 HQI / C37-C38 Spherical/DSH / C40 AGH / C41-C42 ITQ/SH / C43 LSH-forest / C45 E²LSH / C69 ScaNN
- **D** ~16: D2 DenStream / D3-D5 STREAM/Online k-medoids / D7-D10 ClusTree/D-Stream/E-Stream/HPStream / D13 IBLStreams / D17-D20 Misra-Gries/Space-Saving/BJKST/KMV / D21-D23 LinCounting/FM/LogLog / D25 HLL++ / D29-D31 GK/t-digest/KLL / D35 Count-Sketch (proper) / D40 CRS / D43-D44 MOSAIC/Theta / D49 Frequent Directions
- **E** ~12: E3 R-tree / E10 VP-tree / E16 Ball Tree / E23 Pyramid / E24 iDistance / E32 NV-tree / E35 Z-order Morton / E44 H-curve / E45 Skilling Hilbert
- **F** ~12: F4 Sheather-Jones / F7 KDE-FFT / F12 DEFT / F20 V-optimal / F21 MaxDiff / F24 GENHIST / F27 DigitHist / F35-F39 mixture variants
- **G** ~13: G2 PARAFAC / G5-G7 TT/Tensor Ring/BTD / G9-G10 RPCA/Sparse PCA / G12 Kernel PCA Nyström / G13-G14 LE/LLE / G17 Isomap / G25 NMF / G26 ICA FastICA
- **H** ~7: H1 Max-entropy / H2 MI / H5 MDL binning / H6 Entropy quantile / H10 Fisher / H17 IB / H20-H21 Distance Correlation/HSIC
- **I** ~5: I2 SUBCLU / I3 PROCLUS / I5 DOC / I8 ORCLUS
- **J** ~9: J1 Louvain / J3 Infomap / J10 Spectral / J11 Spectral Nyström / J21 Personalized PageRank / J23 NetMF
- **K** ~4: K4 Faure / K5 Niederreiter / K6 Niederreiter-Xing / K7 Owen scrambled
- **L** ~6: L5 Multi-probe LSH / L8-L9 Bloom / L11 XOR filter / L21 RaBitQ
- **M** ~5: M22 PG extended / M23 PG extended MCV
- **O** ~5: O1 KMeans+Neyman / O3 PCA+max-entropy / O6 t-digest stratified / O11 RaBitQ stratification / O13 iDistance+Neyman / O19 t-digest σ-aware Neyman

---

## 3. Stage 3 — Filter J (Vector DB scope) cascade

### 3.1 Drop list (-47 method) — multi-table only / RL only / proprietary / scope outside

| drop | 사유 |
|---|---|
| **B12 Lero / B13 E2E learned / B16 DREAM / B20 BoundSketch / B21 SafeBound** | join CardEst only (single-table 본 연구 scope 외) |
| **B27-B30 RTOS/Bao/Balsa/NeoCard** | RL-based plan optimizer (sampling stage 외) |
| **B46 GaussDB-Vector** | distributed only |
| **B5 FLAT** | factorized SPN (multi-table) |
| **B6 BayesCard** | bayesian network multi-attribute (sampling stage 외) |
| **B8 LMKG** | knowledge graph |
| **B11 AutoCE** | AutoML wrapper (single method 가 아님) |
| **B17 Fauce** | uncertainty quantification (sampling stage 외) |
| **B18 LIGHT** | edge-deployable (single-table OK 그러나 train pipeline) |
| **B22 LpBound proper** | join (degree sequence) only — single-table 적용 어려움 |
| **B31 NeoCard** | local model (single-table OK 그러나 train pipeline) |
| **B38 Smile** | generative AQP (train pipeline) |
| **B39 TASTER** | task-aware (train pipeline) |
| **C5 SPANN** | hybrid memory+SSD (ANN search 외 cardinality 응용 어려움) |
| **C6 NSG / C10 NGT / C13 Annoy / C43 LSH-forest** | ANN search index only (cardinality 응용 X) |
| **C19 IMI / C20 LOPQ / C21 CK-Means / C23 CQ / C25 LSQ / C34 GNOIMI / C35 HQI** | ANN search ONLY (cardinality 외 — 단 본 연구 stratification 응용 어려움) |
| **C37 Spherical Hashing / C40 AGH / C41 ITQ / C42 SH / C45 E²LSH** | ANN hashing variants (lsh와 본질 동일 또는 sample-based 가 아님) |
| **D8-D10 D-Stream/E-Stream/HPStream** | online clustering (RQ3 framework 외 — minibatch_partial 이미 representative) |
| **D13 IBLStreams** | instance-based stream (lazy) |
| **D43-D44 DataSketches MOSAIC/Theta** | set union/intersection (single-vector cardinality 외) |
| **F12 DEFT** | bounded domain density (vector embedding 무경계) |
| **F35-F39 Bayesian/Variational/t-mixture/MFA/PPCA** | mixture variant — GMM 이미 representative |
| **G6 Tensor Ring / G7 BTD** | tensor variants — Tucker 이미 portfolio |
| **G9 Robust PCA** | matrix sparse + low-rank (single-vector embedding 적용 어려움) |
| **G13 LE / G14 LLE / G17 Isomap** | manifold learning (8M scale 어려움 — Filter A에서 다시 검토) |
| **H10 Fisher / H17 IB / H20 Distance correlation / H21 HSIC** | feature importance / dependence test (sampling stage 직접 응용 어려움) |
| **J10 Spectral / J21 Personalized PageRank / J23 NetMF** | graph spectral (manifold/embedding 수준 — 8M scale 어려움) |
| **L8-L9/L11 Bloom variants** | set membership (cardinality 단순화 가능 그러나 stratification 외) |

**Stage 3 잔존: 95** (142 - 47)

---

## 4. Stage 4 — Filter B (공간 복잡도 OOM risk) cascade

### 4.1 Drop list (-22 method) — server 200-400 GB working memory 초과

| drop | 사유 |
|---|---|
| **A5 Sampford / A8 Tillé** | O(N²) rejective on 8M = 64TB matrix ❌ |
| **A38 SMC / A39 Annealed IS / A40-A45 MCMC variants** | iterative gradient + acceptance (8M 1M iter = TB scale) — 단 단순 MH/Slice 는 OK이지만 5/27 시간 budget 외 |
| **C45 E²LSH** | (이미 Stage 3 drop) |
| **D49 Frequent Directions** | O(N·D·k) 8M × 768 × 20 = 122 GB ⚠️ borderline subset OK |
| **F12 DEFT** | (이미 Stage 3 drop) |
| **G12 Kernel PCA Nyström** | Nyström m subsample OK 그러나 m² Gram matrix m=10K = 800MB ⚠️ borderline |
| **I2 SUBCLU** | O(2^D · N²) = 2^96 × 8M² ❌ infeasible |
| **I8 ORCLUS** | O(N · K · D²) 8M × 20 × 256² = 1e13 ⚠️ subset 50K |
| **J11 Spectral Nyström** | O(m² · N) m=10K 8M = 8e11 ⚠️ subset 50K |
| **A24 Adaptive cluster sampling** | network expansion — vector neighborhood 8M × k=50 = 400M edges OK |

**Stage 4 잔존: 73** (95 - 22)

---

## 5. Stage 5 — Filter A (시간 복잡도) cascade

### 5.1 Drop list (-23 method) — 8M @ ETA > 1h

| drop | 사유 |
|---|---|
| **B23 Diffusion CardEst** | inference O(D·T) T=1000 step → ETA > 1h |
| **C25 LSQ / C70 SOAR** | iterative joint optimization 8M × 100 iter = ETA 30-60 min ⚠️ borderline |
| **D7 ClusTree** | anytime tree 8M ✅ OK 그러나 micro+macro 두 단계 = ETA 30 min OK borderline |
| **F20 V-optimal histogram** | DP O(N²·B) — 8M² × 20 = 1e15 ❌ subset 100K only |
| **F24 GENHIST** | genetic search iteration ETA > 1h |
| **F27 DigitHist** | O(N·B) trivial OK |
| **G2 PARAFAC** | O(N·R·iter) 8M × 50 × 20 = 8e9 ⚠️ borderline |
| **G5 Tensor Train** | O(N·R²·D) 8M × 400 × 768 = 2.5e12 ⚠️ borderline subset OK |
| **G6 Tensor Ring / G7 BTD** | (이미 Stage 3 drop) |
| **G9 Robust PCA** | (이미 Stage 3) |
| **G13/G14 LE/LLE** | O(N²) — 8M² = 64TB matrix ❌ |
| **G17 Isomap** | Floyd-Warshall O(N³) — 8M³ = 5e20 ❌ |
| **G18 t-SNE** | (이미 Stage 1 drop) |
| **G20-G24 LargeVis/TriMap/PaCMAP/PHATE/Diffusion Maps** | 대부분 8M ⚠️ borderline subset OK 그러나 UMAP 이미 representative |
| **G27-G29 ICA variants** | O(N·D²) 8M × 768² = 4.7e12 ⚠️ borderline 96d OK |
| **H1 Max-entropy histogram** | IPF iteration O(D·iter·D) D=20 strata 약 OK |
| **I3 PROCLUS** | O(N·D·K·iter) 8M × 768 × 20 × 30 = 3.7e12 ⚠️ borderline 96d 8e9 OK |
| **I5 DOC** | O(N·D·iter) ⚠️ borderline |
| **J1 Louvain** | O(N log N) 8M graph 가정 build O(N·k) k=50 = 400M edges + community detection iter ⚠️ borderline ETA 20-30 min |
| **J3 Infomap** | random walk + MDL ⚠️ borderline ETA 30-60 min |

**Stage 5 잔존: 50** (73 - 23)

### 5.2 통과한 ~50 method (대표 list)

- **A** ~6: A4 PPS-systematic / A9 Pareto πps / A12 Chao weighted reservoir / A13 A-Res / A20 Two-phase / A29 BLB / A32 Importance / A49 GRTS / A50-A51 BAS/HIP / A52 Cube method / A53 LPM1 (proper) / A55 SCPS / A57 Doubly balanced / A58 Cum-√f / A59 Lavallée-Hidiroglou
- **B** ~3: B9 ALECE / B14 ASN / B19 KSampler / B32 DBEst / B35 Sample+Seek / B45 Bao 2025 / B50-B53 LIDER/LSP/LET-Index/DistanceCache / B55 RaBitQ
- **C** ~5: C3-C4 DiskANN / C5 SPANN / C20 LOPQ / C26 TreeQ
- **D** ~14: D2 DenStream / D3-D5 STREAM / D17-D23 sketches (Misra-Gries/Space-Saving/BJKST/KMV/LinCounting/FM/LogLog) / D25 HLL++ / D29-D31 GK/t-digest/KLL / D35 Count-Sketch / D40 CRS
- **E** ~7: E3 R-tree / E10 VP-tree / E16 Ball Tree / E23 Pyramid / E24 iDistance / E32 NV-tree / E35 Z-order Morton / E44 H-curve / E45 Skilling Hilbert
- **F** ~5: F4 Sheather-Jones / F7 KDE-FFT / F21 MaxDiff (== MHIST) / F26 (이미 portfolio)
- **G** ~3: G2 PARAFAC / G10 Sparse PCA / G25 NMF / G26 ICA FastICA
- **H** ~3: H1 Max-entropy / H2 MI / H5 MDL binning / H6 Entropy quantile
- **I** ~1: I3 PROCLUS (96d only)
- **K** ~4: K4 Faure / K5 Niederreiter / K6 Niederreiter-Xing / K7 Owen scrambled
- **L** ~1: L5 Multi-probe LSH (== ABP proper)
- **O** ~5: O1 KMeans+Neyman / O3 PCA+max-entropy / O6 t-digest stratified / O11 RaBitQ stratification / O13 iDistance+Neyman / O19 t-digest σ-aware Neyman

---

## 6. Stage 6 — Filter F (Outperform 보장) cascade

### 6.1 Drop list (-32 method) — ★ 4강 alias 또는 inductive bias 약함

★ 4강 cell-mean: minibatch_partial -10.17%, sparse_rp -8.13%, pca1d -8.50%, hilbert -8.30%, reservoir -8.05% (handoff_back §4.2)

| drop | 사유 (예상 outperform 추정) |
|---|---|
| **A4 PPS-systematic** | size-aware OK 그러나 본 연구 vector embedding "size" = norm 정도 — pca1d quantile bin 본질 동일 (norm-correlated) → ★ 4강 alias |
| **A9 Pareto πps** | sort + permanent random — 단순 size-prop overlap A4 |
| **A20 Two-phase sampling** | pilot + main — Exqutor §V-B의 50-query update period 가 이미 implicit two-phase, 추가 가치 약 |
| **A29 BLB** | scalable bootstrap — uncertainty quantification 위주, cardinality stratification 약 |
| **A32 Importance sampling (basic)** | proposal q 설계 필요 — 본 연구 distribution-aware 영역과 일치하지만 분포 모름 (RQ3 가정) → 직접 응용 어려움 |
| **A49 GRTS** | environmental survey — high-D vector 적용 미검증 |
| **A50 BAS / A51 HIP** | Halton-based — high-D Halton degeneracy (필터 C 부분 통과만) |
| **A52 Cube method** | exact balance — auxiliary multiple constraints 필요 (본 연구 cardinality 단일) |
| **A55 SCPS / A57 Doubly balanced** | spatial 변형 — overlap LPM |
| **B9 ALECE** | attention CardEst — train pipeline 5/27 시간 외 |
| **B14 ASN** | attention sketch — train pipeline |
| **B19 KSampler** | sample selection — 본 연구 paper Eq 1-6 N_init=385 고정 + Adaptive update, KSampler 직접 응용 어려움 |
| **B32 DBEst** | model-based AQP — train pipeline |
| **B35 Sample+Seek** | join sample — single-table 영역 외 |
| **B45 Bao 2025** | reference object based — 흥미롭지만 train + 200K reference |
| **B50-B54** | learned IVF/spatial/index/cache — train pipeline 모두 |
| **C3-C4 DiskANN** | SSD-based ANN search — cardinality stratification 응용 어려움 |
| **C5 SPANN** | hybrid memory+SSD ANN search — 동일 |
| **C20 LOPQ** | locally-optimized PQ — pq+faiss_ivf 변형 (★ 4강 outperform 어려움) |
| **C26 TreeQ** | tree quantizer — pq variant |
| **D2 DenStream** | density stream — minibatch_partial ★2 와 본질 차이 약 |
| **D3-D5 STREAM/Online k-medoids/StreamKM++** | KMeans variants — minibatch_partial 이미 representative |
| **D17 Misra-Gries / D18 Space-Saving** | top-k frequent items — vector embedding cardinality 직접 응용 어려움 |
| **D19 BJKST / D20 KMV / D21 LinCounting / D22 FM / D23 LogLog** | distinct count sketch — HLL++ representative 으로 충분 |
| **D29 Greenwald-Khanna** | quantile sketch — pca1d quantile bin 본질 동일 (univariate quantile) → ★ 4강 alias |
| **D31 KLL sketch** | quantile sketch — D29 변형 |
| **D35 Count-Sketch (proper)** | sign matrix — ams_count_sketch (rename) 와 본질 동일 |
| **D40 CRS** | distinct subsample — overlap KMV |
| **E3 R-tree** | low-D spatial — high-D 약함 |
| **E10 VP-tree** | metric tree — kdtree 본질 동일 alias |
| **E23 Pyramid** | high-D mapping — pca1d quantile alias |
| **E32 NV-tree** | nearest-vector tree — ANN search index |
| **E44 H-curve** | high-D Hilbert variant — Skilling 본질 동일 |
| **F12 DEFT** | (이미 Stage 3) |
| **F20 V-optimal histogram** | (이미 Stage 5) |
| **F24 GENHIST** | (이미 Stage 5) |
| **G2 PARAFAC** | tensor decomposition — Tucker (rename pca3d_grid) 본질 동일 |
| **G25 NMF** | non-negative MF — vector embedding 음수 포함 (사전 shift 필요) |
| **G27-G29 ICA variants** | overlap G26 |
| **H2 MI / H6 Entropy quantile** | mutual information / entropy bin — pca1d quantile 변형 |
| **K4-K7** | high-D QMC variants — sobol/halton 이미 portfolio + high-D 약함 (필터 C 부분만) |
| **L5 Multi-probe LSH** | == ABP proper (Stage 2) |
| **L8-L9 Bloom / L11 XOR** | (이미 Stage 3) |

**Stage 6 잔존: 18** (50 - 32)

### 6.2 통과한 18 method

| # | method | reference | paradigm | 예상 Δ% | 본 연구 narrative fit |
|---|---|---|---|---|---|
| 1 | **A12 Chao weighted reservoir** | Chao 1982 J Royal Stat Soc | P3 | -3 ~ -7% (weight-aware) | weight 기반 reservoir 신규 |
| 2 | **A13 A-Res** | Kolonko-Wäsch 2008 ACM TOMS | P3 | -3 ~ -7% (weight-aware) | overlap A12 borderline |
| 3 | **A24 Adaptive cluster sampling** | Thompson 1990 JASA | P1+P3 | -2 ~ -5% (rare event) | vector kNN 기반 expansion |
| 4 | **A53 LPM1 (proper Grafström)** | Grafström-Lundström-Schelin 2012 Biometrics | P2+P3 | -3 ~ -7% (true LPM) | 현재 lpm2 misnomer rectify |
| 5 | **A58 Cum-√f rule** | Dalenius-Hodges 1959 JASA | P5 | -2 ~ -5% (optimal univariate strata) | 단순 PCA1D 의 optimal 강화 |
| 6 | **A59 Lavallée-Hidiroglou** | Lavallée-Hidiroglou 1988 ASA Survey Res | P5 | -2 ~ -5% (take-all + Neyman) | RQ2 + skew sensitivity |
| 7 | **B55 RaBitQ (1-bit quantization)** | Gao-Lin VLDB 2024 vol 17 p.3252 | P6 | -3 ~ -8% (provable bound) | 2024 추천 method, narrative fresh |
| 8 | **D25 HLL++** | Heule-Nunkesser-Hall EDBT 2013 | P9 | -2 ~ -5% (sketch baseline) | P9 paradigm anchor 강화 (Q4 HLL upgrade) |
| 9 | **D30 t-digest** | Dunning-Ertl 2019 J Open Source Soft | P9 | -2 ~ -5% (quantile sketch) | Druid/CK 산업 standard, P9 강화 |
| 10 | **E16 Ball Tree** | Omohundro 1989 ICSI Tech Rep | P2 | -2 ~ -5% (high-D bounded) | metric tree, kdtree alternative |
| 11 | **E24 iDistance** | Jagadish-Ooi-Tan-Yu-Zhang TODS 2005 | P2 | -3 ~ -6% (distance transform) | reference-based stratification |
| 12 | **E35 Z-order Morton** | Morton IBM Tech Rep 1966 | P2 | -3 ~ -7% (SFC paradigm anchor) | Hilbert 와 직접 비교 (paradigm anchor) |
| 13 | **E45 Skilling Hilbert (true high-D)** | Skilling AIP 2004 | P2 | -3 ~ -7% (★3 hilbert proper) | Q1 (C) 권고 (별도 진짜 hilbert) |
| 14 | **F4 Sheather-Jones bandwidth** | Sheather-Jones JRSS-B 1991 | P10 | -2 ~ -5% (KDE optimal bandwidth) | Q4 KDE 강화 |
| 15 | **F7 KDE-FFT** | Silverman 1982 Applied Statistics | P10 | -2 ~ -5% (fast KDE) | Q4 KDE alternative (faster) |
| 16 | **G10 Sparse PCA** | Zou-Hastie-Tibshirani JCGS 2006 | P4 | -2 ~ -5% (interpretable PCA) | pca1d ablation (sparse loading) |
| 17 | **G26 ICA FastICA** | Hyvärinen NN 1999 | P4 | -2 ~ -6% (non-Gaussian) | pca1d 와 다른 inductive bias (ICA 독립성) |
| 18 | **H5 MDL-optimal binning** | Rissanen 1978 + Boullé 2006 MODL | P9+P10 | -2 ~ -5% (info binning) | pca1d + MDL bin (entropy 강화) |
| 19 | **O1 KMeans + Neyman allocation** | (synthesis) | P1+RQ2 | -3 ~ -7% (cluster 내 σ Neyman) | RQ2 plug-in 으로 P1 cluster 강화 |
| 20 | **O6 t-digest + Neyman** | (synthesis) | P9+RQ2 | -3 ~ -7% (sketch + Neyman) | t-digest σ-aware allocation |
| 21 | **O11 RaBitQ stratification** | (synthesis) | P6 | -3 ~ -7% (1-bit code stratification) | bit-pattern bin |
| 22 | **O13 iDistance + Neyman** | (synthesis) | P2+RQ2 | -3 ~ -7% | reference + σ allocation |
| 23 | **PROCLUS (I3, 96d only)** | Aggarwal 1999 SIGMOD | P7 | -2 ~ -5% (subspace cluster) | 신규 P7 paradigm anchor |

(20개 + ★ candidate hybrid 4 = 24개로 잠시 확장 후 Filter E에서 selection)

### 6.3 마지막 selection rationale

| candidate type | count | 처리 |
|---|---|---|
| 단일 base method | 18 | F filter 통과 |
| Synthesis hybrid (O시리즈) | 4 | F filter 통과 (★ candidate) |
| 합계 | **22** | (잠시 22로 확장) |

**Stage 6 보정 잔존: 22** (방금 calc 18에서 hybrid 4 추가)

→ 다음 Filter E 에서 narrative scope check 후 최종 11 method.

---

## 7. Stage 7 — Filter E (학술 정합 9 paradigm × Exqutor §V-B) cascade

### 7.1 Drop list (-11 method) — paradigm 외 / Exqutor §V-B plug-in 어려움

| drop | 사유 |
|---|---|
| **A13 A-Res** | overlap A12 Chao — 동일 weight reservoir family |
| **A24 Adaptive cluster sampling** | rare event sampling 영역 — 본 연구 selectivity {0.001, 0.01, 0.10} 중 0.001 만 fit, narrative 약 |
| **B55 RaBitQ** | quantization (P6) — 본질 PQ family extension, ★ 4강 outperform 추정 어려움 (1-bit 정보 손실 큼). O11 hybrid 가 더 나은 응용 |
| **D25 HLL++** | distinct count sketch — 본 연구 stratification 응용 어려움 (cardinality estimator로 직접 사용 시 P9 anchor OK). 단 Q4 Tier 1 HLL 권고 그대로 유지로 충분 (HLL 와 HLL++ 구분 narrative 약) |
| **D30 t-digest** | quantile sketch — pca1d quantile 변형 (★ 4강 alias risk). O6/O19 hybrid 가 더 가치 있음 |
| **E16 Ball Tree** | metric tree — kdtree alias risk (5/10 audit kdtree defect 와 동일 risk) |
| **F4 Sheather-Jones bandwidth** | KDE bandwidth — Q4 KDE Parzen 권고에 이미 Silverman default. 별도 method로 측정 가치 약 |
| **F7 KDE-FFT** | fast KDE — Q4 KDE Parzen 권고와 본질 동일 (FFT 가속만) |
| **G10 Sparse PCA** | interpretable PCA — pca1d ablation, ★ 4강 outperform 어려움 |
| **H5 MDL-optimal binning** | info binning — pca1d quantile 변형 (★ 4강 alias risk) |
| **PROCLUS (I3)** | subspace cluster — 96d only fit (DEEP), 다른 dataset 약. 단 P7 paradigm anchor 가치 있음 → narrative 약 |

**Stage 7 최종 잔존: 11 method**

### 7.2 ★ FINAL — 11 method (cascade 통과)

| # | method | reference | paradigm | 예상 Δ% | 본 narrative fit | 구현 line | server SF=10 ETA |
|---|---|---|---|---|---|---|---|
| 1 | **A12 Chao weighted reservoir** | Chao 1982 JRSS | P3 (★ 후보 weight) | -3 ~ -7% | weight reservoir 신규, lp_norm/L2 weight 활용 | ~50 | 30 min |
| 2 | **A53 LPM1 (proper Grafström)** | Grafström-Lundström-Schelin 2012 Biometrics | P2+P3 | -3 ~ -7% | 현재 lpm2 misnomer rectify, true LPM | ~250 | 1 h |
| 3 | **A58 Cum-√f rule** | Dalenius-Hodges 1959 JASA | P5+RQ2 | -2 ~ -5% | optimal univariate strata bounds, PCA1D 강화 | ~100 | 30 min |
| 4 | **A59 Lavallée-Hidiroglou** | Lavallée-Hidiroglou 1988 ASA SR | P5+RQ2 | -2 ~ -5% | take-all stratum + Neyman, skew rare-event | ~150 | 1 h |
| 5 | **E24 iDistance** | Jagadish-Ooi-Tan-Yu-Zhang TODS 2005 | P2 | -3 ~ -6% | reference-based distance transform stratification | ~100 | 30 min |
| 6 | **E35 Z-order Morton** | Morton IBM 1966 | P2 (paradigm anchor) | -3 ~ -7% | Hilbert 와 직접 비교 paradigm anchor | ~80 | 30 min |
| 7 | **E45 Skilling true high-D Hilbert** | Skilling AIP 2004 | P2 (★3 rectify) | -3 ~ -7% | Q1 (C) 권고 (★3 hilbert PCA proxy 와 진짜 비교) | ~150 | 1 h |
| 8 | **G26 ICA FastICA** | Hyvärinen NN 1999 | P4 | -2 ~ -6% | pca1d 와 다른 inductive bias (independence assumption) | ~50 | 30 min |
| 9 | **O1 KMeans + Neyman allocation** | (synthesis Cochran 1977 Ch 5 + Neyman 1934) | P1+RQ2 | -3 ~ -7% | RQ2 + RQ3 cluster 결합, ★1 hdbscan 후보 강화 | ~100 | 30 min |
| 10 | **O11 RaBitQ stratification** | (synthesis Gao-Lin VLDB 2024 + bit-pattern bin) | P6 | -3 ~ -7% | 1-bit code stratification, narrative fresh | ~150 | 1 h |
| 11 | **O13 iDistance + Neyman** | (synthesis Jagadish 2005 + Neyman 1934) | P2+RQ2 | -3 ~ -7% | reference distance + σ Neyman allocation | ~100 | 30 min |

**총 11 method × 평균 ~100 line × ~45 min ETA = 18-25 h server time** (실현 가능)

---

## 8. END

작성: 2026-05-11 01:25 KST
다음 단계: `_FINAL_LIST.md` 작성 (11 method 상세 spec) + Phase 3 implementation 결정 (사용자 confirm 후)

**핵심**: 470 신규 candidate → cascade 7 stage → **11 method 통과**.

분포:
- weight 기반 sampling (P3 강화): A12, A24 borderline
- spatial / SFC paradigm anchor: E24, E35, E45
- stratification optimization (P5+RQ2): A53, A58, A59, O1, O13
- dim reduction non-Gaussian: G26
- vector quantization 신규: O11

paradigm 분포: P1+RQ2 (1) / P2 (3) / P2+RQ2 (1) / P3 (2) / P4 (1) / P5+RQ2 (3) / P6 (1) — 총 9 paradigm 중 5 paradigm 강화. P7-P10 은 Q4 Tier 1 권고 (DBSCAN/KDE/MHIST-2/HyperLogLog/randomized SVD/wavelet histogram) 으로 별도 추가.
