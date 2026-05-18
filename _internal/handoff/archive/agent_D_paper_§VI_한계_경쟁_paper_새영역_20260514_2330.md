# Agent D — paper §V/§VI/§VII 한계 영역 재정독 + 경쟁 paper 새 영역 발굴

> **작성**: 2026-05-14 19:48 KST · Agent D · main thread 지시 "paper §VI 다른 한계 + 경쟁 paper 새 영역 발굴"
> **검증 기조**: paper PDF 전체 정독 (page 1 ~ 12 verbatim 모두 재정독, §I ~ §VIII) + Agent A (78%) + Agent B (정정 7) + Agent C (8 옵션 deep dive + I/J/K 추가) + **WebSearch 12 건 + WebFetch 4 건 (CE4HD VLDB 2024 PDF 직접 read + Ada-ef arxiv 2512.06636 + RELOAD arxiv 2604.14725 + BDAI conferences.html)**
> **★★★ wording 정정 룰 (Agent B critical 반영 — 필수 사용)**:
>   - ❌ 폐기: "5 단계 中 1 단계", "5 단계 알고리즘"
>   - ✓ 정정: "Eq 1 (Bernoulli) 대체 vs Eq 2-6 (dynamic batch loop = paper differentiation) 유지"
>   - Neyman paradox = sel=0.01 한정 명시 (sel=0.1 영역 역전)
>   - σ_j range = oracle interpretation 명시 (직접 측정 미완)
>   - Pareto Top 5 = "sparse_rp / chao_weighted / neuram / pca1d / hilbert" (reservoir 옵션 G)
>   - byte-identical = 6 unique cells (9 nominal)
>   - 학부 capstone = ★★ 매우 강력

---

## 0. 핵심 결론 요약 (TL;DR)

본 Agent D 의 paper §V/§VI/§VII 전체 verbatim 재정독 결과 Agent A/B/C 가 식별한 3 영역 (§VI-E + §V-B + §VII) 외에 **paper 자체 명시 한계 5 영역 추가 발굴** (§VI-A cost model ANN 미반영 / §VI-C Q20 lineitem dominant cost / §VI-D 우단 buffer pool space amplification / §VI-E 두 번째 Limitation = cost model 한계 / §VII 마지막 단락 = filtered single-relation only).

경쟁 paper literature search 결과 **본 연구 영역 직접 인접 5 편 발견**: (1) **CE4HD VLDB 2024 (Lan-Bao)** SRCE/MRCE = reference object 기반 learned cardinality estimation for vector similarity, (2) **Ada-ef arxiv 2512.06636 (Zhang-Miller Waterloo 2025)** = distribution-aware HNSW search 의 statistical distribution modeling, (3) **Adaptive Bucket Probing arxiv 2604.04603 (HKUST 2025)** = LSH + progressive sampling, (4) **Reservoir Sampling over Joins SIGMOD 2024 (Dai-Hu-Yi)** + arxiv 2508.15070 spatial join 확장, (5) **Filtered Vector Search VLDB 2025 tutorial (Caminal et al.)** 의 declarative recall axis.

**박광현 BDAI 연구실 paper list (BDAI conferences.html 2024-2026)**: **Exqutor** + **RELOAD** + **DFLOP** + **CANNON** + **FaScalSQL** + **SPID-Join** = ML/DB integration + 학습 query optimizer + near-memory ANN + 멀티모달 LLM pipeline. **본 연구 = Exqutor 의 §V-B sample 추출 부분 augment**.

| 추가 발굴 옵션 | 영역 | cost | novelty | review-grade | timeline |
|---|---|---:|---|---|---|
| **L** | §VI-A cost model ANN 미반영 영역 (Exqutor 의 explicit limitation 한계) | 10-15h | ★★ | paper-grade 가능 | 5/27 가능 |
| **M** | §VI-D Q20 lineitem dominant cost = ECQO 한계 한 영역 | 5-8h | ★ | review-grade | 5/27 안전 |
| **N** | CE4HD SRCE/MRCE vs 본 연구 비교 framework | 15-20h | ★★ | paper-grade 가능 | 5/27 가능 |
| **O** | Ada-ef statistical distribution modeling vs 본 연구 비교 | 10-15h | ★ | review-grade | 5/27 안전 |
| **P** | 박광현 RELOAD learned QO + 본 연구 cardinality module 결합 framework | 20-30h | ★★ | paper-grade 가능 | 5/27 빡빡 (~D-13) |

**Agent C hybrid (A+G1, A+B+F partial, A+C) + Agent D 새 옵션 (L, M, N, O, P) 의 종합 권장**: 본 Agent D 의 1순위 hybrid = **A + G1 + N (현 narrative + reservoir industry highlight + CE4HD/Ada-ef 비교 framework)**.

---

## 1. paper §V / §VI / §VII 영역 한계 verbatim 재정독 (8 영역 발굴)

### 1.1 §V-B 영역 (Agent A/B/C 가 식별, Agent D 재확인)

#### paper §V-B verbatim (page 5 우단 끝 단락)

> "When a VAQ lacks a vector index, the query optimizer must rely on either an index over structured attributes or perform a full sequential scan. In the case of a sequential scan, evaluating the similarity predicate requires computing distances between the query vector and all vectors in the dataset. This exhaustive KNN search is highly expensive, making it unsuitable for direct execution during query planning, unlike the approach used in ECQO. To address this, Exqutor adopts a sampling-based cardinality estimation approach specifically for KNN queries, where it approximates the number of qualifying tuples by evaluating similarity over a small subset of the data."

**한계 영역**: paper 가 "specifically for KNN queries" (single-table 한정) 명시. multi-table joint distribution 영역 미다룸 → 본 연구 A2-Fig7/8/9 Centroid tuple 영역 (옵션 E).

#### paper §V-B Algorithm 1 의사코드 = 14-step

paper §V-B 본문 Eq 1-6 의 14-step (Agent B 정정):
- **Step 1** (Eq 1): N = ⌈z²·P̂·(1−P̂) / e²⌉ = 385 fixed budget (z=1.96, P̂=0.5, e=0.05)
- **Step 2-6**: Bernoulli sample 추출 + similarity 평가 + Q-error 계산 (Eq 2)
- **Step 7-13** (Eq 3-6): δ adjustment + V_t momentum + sampling_size update + γ lr decay (paper differentiation)
- **Step 14**: 매 50 query 마다 update

**본 연구 영역**: **Step 11 ("Sample n_inc more rows via Bernoulli") 의 sample 추출 방식만 stratified KM20 으로 대체**. Eq 2-6 (dynamic batch loop) 유지.

### 1.2 §V-A 영역 (Agent C 옵션 F, Agent D 확인)

#### paper §V-A verbatim (page 5)

> "When a VAQ involves a vector similarity predicate and a corresponding index is available, Exqutor applies a strategy called ECQO. The key idea behind ECQO is to execute a lightweight vector index search during query planning to compute the exact number of vectors among the retrieved candidates that satisfy the similarity threshold."

**paper §V-A 한계**: 인덱스 ON 만 다룸. paper §V-A vs §V-B 영역 boundary 의 cell 별 paired Δ% 비교 안 수행.

### 1.3 ★★★ §VI-A 우단 (paper Q20 lineitem dominant cost + cost model ANN 미반영) — Agent D 신규 발굴

#### paper §VI-A 우단 끝 부분 verbatim (page 8)

> "Query characteristics also influence ECQO's effectiveness. Most evaluated queries benefit from better join ordering and early application of vector filters. However, in queries like Q20, where the dominant cost arises from a full scan of the lineitem table, ECQO's impact is limited. While ECQO improves join ordering, the total benefit is limited by the large fixed cost of scanning unrelated data. This suggests that ECQO is most effective when vector predicates contribute significantly to overall selectivity."

★★★ **Agent D 신규 발굴 한계**: paper 가 Q20 의 lineitem table dominant cost 영역에서 ECQO 의 효과 약화 명시. **본 연구 → 옵션 M 의 영역**: Q20 환경 (lineitem dominant) 에서 §V-B (sampling) + §V-A (ECQO) 결합 영역. 우리 측정 portfolio Q3 중심 (Fig.4 + Fig.5/6 + Fig.7/8/9) 와 Q20 영역 cell 의 cell-level paired 비교 가능.

#### paper §VI-A 우단 (page 8 우측 끝)

> "Despite these improvements, PostgreSQL's cost model remains insufficiently equipped to accurately reflect the performance characteristics of ANN-based vector indexes. In pgvector, although the index leverages PostgreSQL's internal buffer pool, ANN indexes typically incur high space amplification [72], often exceeding the size of the base table. At the same time, structures like HNSW achieve O(log Card(T)) sublinear search times [38], which the current cost model fails to capture."

★★★ **Agent D 신규 발굴 한계**: paper §VI-A 가 explicit 으로 cost model 의 ANN sublinear (O(log Card(T))) 미반영 + space amplification 한계 명시. **본 연구 → 옵션 L 의 영역**: cost model 영역의 ANN 한계 영역 적용 + 본 연구 sample 추출 augment 가 cost model 어떻게 align 되는지 contribution 영역.

#### paper §VI-A 우단 (Agent D 추가)

> "As a result, the optimizer may overestimate the cost of an HNSW index scan and fail to select it, even in cases where it would be the better access method [73]."

paper 가 cost model 이 잘못된 plan choice 영역 명시. **본 연구 영역 = sample 추출 정확도 augment 만 다룸. cost model 영역 X**.

### 1.4 §VI-B 영역 (Agent A/B 가 식별, Agent D 재확인)

#### paper §VI-B 우단 verbatim (page 8 우측, Fig.5 다음)

> "Adaptive sampling overcomes this limitation by modifying the sample size based on query feedback. It tracks Q-error over time and adjusts the number of sampled rows accordingly. When the error is high, indicating that the estimate diverges from observed cardinality, the sample size is increased to enhance accuracy. Conversely, when estimates stabilize, the sample size is reduced to conserve computation."

★ paper 본 differentiation = **Q-error feedback 의 sample size 동적 조정**. 우리가 안 건드림 → 옵션 B (Eq 2-6 distribution-aware augment).

#### paper §VI-B + Fig.6 dataset 의존 영역 (Agent C 옵션 B 의 정당성)

> "The sample size trajectory varies depending on the dataset: for DEEP and SimSearchNet++, the sample size decreases over time as Q-error stabilizes, allowing the system to reduce planning cost without loss of accuracy. In contrast, for SIFT, the sample size increases to satisfy higher estimation demands due to its more complex distribution."

★ paper 본인 명시: dynamic batch trajectory = **dataset 의 분포 (complexity) 의존**. 옵션 B 의 distribution-aware augment 가 정확히 이 영역.

### 1.5 §VI-C 영역 (Agent A/B 가 식별, Agent D 재확인)

#### paper §VI-C verbatim (page 10, Fig.7/8/9)

> "Multi-vector VAQs. We further evaluate Exqutor on multi-vector query workloads, where embeddings from multiple sources are integrated into queries. As shown in Figure 8, when both DEEP and WIKI datasets are stored in the partsupp table, we observe substantial performance improvements, with query execution times accelerated by factors ranging from 1.07× to 479.4×. Figure 9 illustrates the scenario where DEEP embeddings are stored in partsupp while WIKI embeddings are stored in the part table. Even in this more complex join setting, we still observe speedups from 1.07× to 254×."

★ paper 본 measurement = multi-vector 영역 다룸 but **ECQO context** (인덱스 ON). adaptive sampling context (§V-B, 인덱스 OFF) multi-table 측정 X → 옵션 E 의 영역 + 본 연구 A2-Fig9 Centroid tuple −7.37%.

#### paper §VI-C verbatim TPC-DS 영역 (Fig.10)

> "Evaluation on TPC-DS. To further validate the effectiveness of Exqutor on diverse workloads, we conducted experiments on the TPC-DS based Vector-augmented SQL analytics... As shown in Figure 10, the results demonstrate consistent performance improvements, with query execution times achieving speedups of up to 109.6×."

★ TPC-DS 측정 = ECQO context (Fig.10 = "pgvector vs pgvector+Exqutor with vector indexes"). adaptive sampling context (§V-B) TPC-DS 측정 X → 옵션 H 의 영역 (Agent C 폐기 권장).

### 1.6 §VI-D Discussion 영역 (Agent D 신규 발굴)

#### paper §VI-D Discussion (Query time analysis) verbatim (page 10 우단)

> "Query time analysis. Figure 11 illustrates the execution plans for Q3 on the DEEP dataset before and after applying Exqutor with ECQO on pgvector. The baseline pgvector plan relies heavily on full table scans and parallel hash joins, resulting in high scan and join costs, with total query time exceeding 52 seconds. In contrast, the optimized plan with Exqutor eliminates expensive join operations and replaces sequential scans with selective index scans, enabled by accurate cardinality feedback from ECQO."

#### paper §VI-D 우단 verbatim (page 11 우측 위)

> "These patterns consistently appear across other workloads such as TPC-DS, confirming that the benefits of Exqutor generalize beyond a single benchmark."

★ paper §VI-D 의 Discussion 핵심 = **§V-A ECQO 영역 conclusions** (Fig.11 Q3 execution plan visualization). §V-B (adaptive sampling) 영역의 execution plan visualization X. **본 연구 → 옵션 L 의 영역**: 본 연구 sample 추출 augment 의 execution plan visualization (paper §VI-D 와 비슷한 framework).

#### paper §VI-D 우단 verbatim (page 11 우측 위)

> "Comparison with learned cardinality estimator. Figure 12 compares Exqutor with SelNet [74], a learned estimator. Exqutor achieves speedups up to 16.1× speedup over SelNet. SelNet requires 77 ms for a single-query cardinality estimation and depends on offline training and complexity."

★★★ **Agent D 신규 발굴 한계**: paper §VI-D 가 SelNet 만 비교. **CE4HD VLDB 2024 (Lan-Bao) SRCE/MRCE** = SelNet 보다 ~136× smaller Q-error + ~10× faster. paper §VI-D 가 본 영역 비교 미수행 → **본 연구 → 옵션 N 의 영역**: SelNet 외 CE4HD SRCE/MRCE 와의 비교 framework.

### 1.7 §VI-E Limitations (Agent A/B/C 가 식별, Agent D 재확인 + 두 번째 한계 명시)

#### paper §VI-E Limitations 1번 verbatim (page 12 우단)

> "In high-dimensional spaces, the overhead of sampling increases because of the higher cost of distance computations, which may reduce the efficiency of our adaptive sampling strategy."

★ paper limitations 1번 = high-dim 환경 (WIKI 768d) 의 효율 axis → 본 연구 측정 Pareto frontier 와 직접 align (Agent C 옵션 A 의 학술 정당성).

#### paper §VI-E Limitations 2번 verbatim (page 12 우단, Agent D 신규 발굴)

> "Moreover, our approach relies on cost models that fail to fully capture the performance characteristics of ANN indexes, so even with accurate cardinality estimates the optimizer may still choose suboptimal plans. Addressing these issues through more efficient sampling in high dimensions and refined cost models for VAQ optimization remains an important direction for future work."

★★★ **Agent D 신규 발굴 한계**: paper §VI-E Limitations 2번 = **cost model 한계** explicit 명시. 옵션 L 의 영역 정당성. **paper future work explicit 명시 영역**: (1) more efficient sampling in high dimensions + (2) refined cost models for VAQ optimization → 본 연구 (1) 영역 partial.

### 1.8 §VII Related Work + §VIII Conclusion (Agent D 신규 발굴)

#### paper §VII Related Work 마지막 단락 verbatim (page 12 우단, Filtered vector search)

> "Filtered vector search. As vector similarity search becomes more prevalent, many systems [11], [12], [27] store vector embeddings alongside structured metadata, enabling filtered vector search. This trend has also emerged in ANN benchmarks [63], [75], highlighting the growing importance of efficient filtering techniques. Several studies have optimized filtered vector queries by restructuring ANN indexes to support filtering constraints more effectively. ACORN [76], SeRF [77], HQANN [78], and diskANN [41] enhance ANN search by integrating attribute filtering directly into the index structure, improving retrieval efficiency. However, these methods are limited to filtering within a single relation or collection, making them less effective for large-scale analytical workloads that involve complex joins across multiple datasets."

★★★ **Agent D 신규 발굴 한계**: paper 가 ACORN/SeRF/HQANN/diskANN 의 한계 = **"limited to filtering within a single relation"** 명시. **본 연구 → 옵션 N 의 영역 보강**: ACORN (SIGMOD 2024, paper [76] reference) 와 본 연구 multi-table 영역 (Centroid tuple A2-Fig9) 의 직접 비교 가능성.

#### paper §VII Related Work (Query optimization in generalized vector database systems) verbatim (page 12 우단)

> "Query optimization in generalized vector database systems. Several generalized vector database systems have extended traditional query processing techniques to support vector operations. AnalyticDB [1] optimizes filtered vector searches using a cost-based model, while SingleStore [7] integrates filters directly into vector index scans to improve retrieval efficiency. However, these optimizations primarily target simple filter queries rather than complex analytical workloads involving multi-way joins and nested queries. As a result, they do not effectively address the challenges of optimizing VAQs, where inaccurate cardinality estimation can severely degrade query performance."

★ paper 가 AnalyticDB-V / SingleStore-V 의 한계 = single filter queries only. multi-way joins / nested queries 영역 미다룸. 본 연구 영역 = Exqutor 와 동일 (multi-table 직접 본 연구 측정 A2-Fig9 가 paper 명시 영역 한정 보강).

#### paper §VII Related Work (Sampling) verbatim (page 12 우단)

> "One technique in query optimization for efficiently estimating selectivity and cost is sampling. Early works introduced random sampling for join size estimation [79], [80], while later approaches refined these ideas with adaptive sampling strategies [81]. The method in [81] adjusts the sample size dynamically until a desired confidence level is reached, but does not consider sampling overhead or optimize it dynamically based on query characteristics."

★ paper differentiation 영역 = Lipton-Naughton 1990 [81] 과의 differentiation. **adaptive sampling 의 sampling overhead 영역 + dynamic optimization 영역**이 paper 의 contribution. 본 연구 → 옵션 B 의 정당성 강력.

#### paper §VIII Conclusion verbatim (page 12 우단)

> "Through integration with pgvector, VBASE, and DuckDB, Exqutor extends the ability of generalized vector database systems to efficiently handle vector-augmented analytical queries, contributing to the optimization of emerging data science pipelines like retrieval-augmented generation (RAG)."

★ paper main goal = RAG 영역 query optimization. **본 연구 → 옵션 G 의 산업 적용 axis 보강** (reservoir streaming = RAG production 시나리오).

### 1.9 paper 한계 영역 종합 표

| 한계 영역 | paper 인용 page | 우리 공략 가능성 | 추가 측정 cost | novelty | 박광현 review-grade | 5/27 timeline |
|---|---|---|---:|---|---|---|
| **§V-B Eq 1 sample 추출** | p.5 우단 | ✓ 우리 영역 (옵션 A 의 base) | 0h (현 1001 file) | ★ partial (vector domain 한정) | 학부 capstone ★★ | ★ 안전 |
| **§V-B Eq 2-6 dynamic batch** | p.6 + Fig.6 | △ partial 가능 (옵션 B) | 25-35h | ★★ paper main 영역 augment | review-grade ★★ | △ 가능 (가속) |
| **§V-A ECQO** | p.5 + Fig.4 | △ partial 가능 (옵션 F) | 20-30h | ★ weak (paper 의 결합 비교) | review-grade ★ | △ 가능 |
| **§VI-A cost model ANN 미반영** | p.8 + Fig.4 우단 | ✓ 옵션 L 신규 | 10-15h | ★★ paper limitation 직접 영역 | paper-grade 가능 | ★ 안전 |
| **§VI-A Q20 lineitem dominant** | p.8 우단 | ✓ 옵션 M 신규 | 5-8h | ★ niche | review-grade | ★ 안전 |
| **§VI-B Q-error feedback dataset 의존** | p.8 + Fig.6 | △ 옵션 B 의 evidence 보강 | 0h (현 측정 evidence) | ★★ paper 명시 영역 | review-grade | ★ 안전 |
| **§VI-C single-vector single-table 한정** | p.5 + p.10 | ✓ 옵션 E partial (A2-Fig9 확장) | 15-25h | ★★ paper boundary | review-grade | ★ 안전 |
| **§VI-C TPC-DS adaptive sampling 영역 미측정** | p.10 + Fig.10 | ✗ 옵션 H 폐기 (cost 50-70h) | 50-70h | weak | weak | ✗ 무리 |
| **§VI-D SelNet 만 비교 (CE4HD 미비교)** | p.11 + Fig.12 | ✓ 옵션 N 신규 | 15-20h | ★★ vector domain 직접 영역 | paper-grade 가능 | ★ 가능 |
| **§VI-E high-dim sampling overhead** | p.12 우단 | △ 옵션 A 의 정당성 보강 | 0h | ★ partial | review-grade | ★ 안전 |
| **§VI-E cost model 한계** | p.12 우단 | ✓ 옵션 L 의 영역 | 10-15h | ★★ paper future work 영역 | paper-grade 가능 | ★ 안전 |
| **§VII Filtered ANN single-relation 한정** | p.12 우단 | ✓ 옵션 N 의 영역 보강 | 0h | ★ paper 명시 영역 | review-grade | ★ 안전 |
| **§VII Sampling 영역 dynamic optimization** | p.12 우단 | △ 옵션 B 의 정당성 보강 | 0h | ★★ paper differentiation 영역 | review-grade ★ | ★ 안전 |
| **§VIII RAG 영역** | p.12 우단 | △ 옵션 G 의 산업 적용 | 0h | ★ partial | review-grade | ★ 안전 |

---

## 2. Distribution-Aware HNSW (arxiv 2512.06636 Ada-ef) 핵심 정독 + 우리 연구 관계

### 2.1 paper 핵심 contribution

**제목**: "Distribution-Aware Exploration for Adaptive HNSW Search"
**저자**: Chao Zhang, Renée J. Miller (University of Waterloo)
**연도**: 2025-12 (arxiv preprint)

**핵심 contribution**:
1. **Ada-ef**: HNSW 의 ef parameter 를 query 별 동적 조정 → declarative target recall 달성 + over/under-search 회피
2. **two-phase runtime strategy**:
   - Phase 1 (Distance Collection): ef=∞ 으로 graph 탐색, 2-hop reachable nodes 거리 수집
   - Phase 2 (Adaptive Search): pre-computed dataset statistics (mean + covariance matrix) 로 estimator function 계산 → ef 결정
3. **theoretical foundation**: cosine / inner product / cosine distance 의 distance distribution = normal approximation in high-dim
4. **query scoring model**: distance distribution 의 quantile-based bins → query score 계산 → offline ef-estimation table lookup
5. **datasets**: GloVe-100 / DeepImage / MS MARCO V1+V2.1 (Ada-002 + Cohere) / LAION + Uniform Cluster + Zipfian Cluster (synthetic)
6. **baselines**: LAET / DARTH / PiP / HNSWlib / FAISS
7. **개선**: DARTH 대비 50× offline efficiency

**핵심 한계 (저자 explicit 명시)**:
- "**The Euclidean (L2) case remains open due to the squared terms in its formulation.**" — L2 distance 영역 미해결
- i.i.d. dimensional assumption 의 한계 (Lindeberg's condition 으로 relaxation)

### 2.2 우리 연구와 overlap / 차별점

**Overlap**:
- 둘 다 distribution-aware 의 axis 활용 (Ada-ef = 거리 분포 normal approximation, 본 연구 = K-means stratification σ_j range)
- 둘 다 paper main mechanism (Ada-ef = HNSW ef, 본 연구 = Exqutor Eq 1 sample) 영역 augment
- 둘 다 declarative axis (Ada-ef = target recall declarative, 본 연구 = target Q-error declarative gap 측정)

**차별점**:
- **layer 다름**: Ada-ef = HNSW index 영역 (ANN search), 본 연구 = Exqutor §V-B 영역 (cardinality estimation for query optimizer)
- **methodology 다름**: Ada-ef = statistical distribution modeling (normal approximation), 본 연구 = empirical sampling (K-means stratification)
- **target 다름**: Ada-ef = recall guarantee, 본 연구 = Q-error reduction
- **measurement portfolio 다름**: Ada-ef = 6 real-world + 2 synthetic, 본 연구 = DEEP + SIFT + SSN sf=100 / sf=10 + Q3 / A2-Fig9

### 2.3 학습 / 차용 가능 영역

★★★ **Ada-ef 의 contribution 中 본 연구 적용 가능 axis**:
1. **declarative axis** (★★ 가장 강력): Ada-ef 의 "target recall declarative" 처럼 우리는 "target Q-error declarative" 영역 명시 가능 → 옵션 N 의 영역 보강
2. **statistical distribution modeling**: σ_j range 의 oracle interpretation 대신 normal approximation 영역 적용 가능 → 옵션 C 의 메커니즘 보강
3. **offline-online split**: 우리 K-means pre-computation 도 offline 영역, sampling 은 online 영역 → 옵션 L 의 영역
4. **paper boundary 영역 발굴 axis**: Ada-ef 가 L2 영역 explicit 명시 미해결 → 우리 K-means (L2) + L2 vector similarity range query 영역 본 연구 영역의 정당성 보강

### 2.4 새 옵션 도출 (옵션 O — Ada-ef 비교 framework)

**옵션 O — Ada-ef statistical distribution modeling vs 본 연구 K-means stratification 비교**:
- 영역: HNSW ef adaptation (Ada-ef) vs cardinality estimation sample (본 연구) 의 두 영역 比 직접 비교 + 두 영역 결합 framework 가능성
- cost: 10-15h (literature review + 비교 framework + ECQO 의 HNSW probe 영역과의 align 분석)
- novelty: ★ moderate (vector similarity domain 同一, but layer 다름)
- review-grade: review-grade ★, paper level 어려움 (layer 다름 explicit 명시 필요)
- timeline: 5/27 ★ 안전

---

## 3. 경쟁 paper 추가 발굴 (5-10 편, 우리 위치 비교)

### 3.1 CE4HD: Cardinality Estimation for Similarity Search on High-Dimensional Data Objects (VLDB 2024) ★★★ 핵심

**제목**: "Cardinality Estimation for Similarity Search on High-Dimensional Data Objects: The Impact of Reference Objects"
**저자**: Hai Lan (RMIT), Shixun Huang (Wollongong), Zhifeng Bao (RMIT, corresponding), Renata Borovica-Gajic (Melbourne)
**연도**: 2024-12 (PVLDB Vol.18 No.3)
**DOI**: 10.14778/3712221.3712224

**핵심 contribution**:
- **CE4HD (Cardinality Estimation for High-Dimensional Data Objects)** = 본 연구와 정확히 동일 영역
- **SRCE (Single-Reference Cardinality Estimation)**: 단일 reference object 의 cardinality function 으로 query object 의 cardinality 추정
- **MRCE (Multi-Reference Cardinality Estimation)**: 여러 reference objects 의 weighted sum (learned weights) 로 cardinality 추정
- **SOTA 비교**: SimCard (SIGMOD 2021) vs SelNet (2023) vs **본 연구 SRCE/MRCE**
- **개선**: SimCard 대비 ~136× smaller Q-error, SelNet 대비 ~3.2× smaller Q-error, 2× faster offline
- **datasets**: ECG (timeseries) + FACE (embedding) + 등 5 datasets
- **3 research gap**: Comprehensive Efficiency / Query Robustness / Data Robustness

**우리 위치 비교**:
- **layer 同일**: 둘 다 cardinality estimation for vector similarity range query
- **기법 다름**: CE4HD = reference object + learned model (offline training), 본 연구 = K-means stratification (offline training 학습 비용 0)
- **datasets 다름**: CE4HD = ECG + FACE (저차원 256d 이하), 본 연구 = DEEP 96d + SIFT 128d + SSN 256d (paper exact)
- **baseline 다름**: CE4HD = SelNet + SimCard, 본 연구 = paper §V-B Bernoulli

★★★ **Agent D 신규 발굴 axis**: **CE4HD + paper §V-B Bernoulli + 본 연구 K-means stratification** 의 **3-way 비교 framework**. CE4HD 가 paper §VI-D Fig.12 (SelNet 비교) 영역 너머 발견. **옵션 N 의 영역 정당성 매우 강력**.

### 3.2 Adaptive Bucket Probing (arxiv 2604.04603, HKUST 2025)

**제목**: "Cardinality Estimation for High Dimensional Similarity Queries with Adaptive Bucket Probing"
**저자**: Zhonghan Chen, Qintian Guo, Ruiyuan Zhang, Xiaofang Zhou (HKUST + HKGAI)
**연도**: 2025

**핵심 contribution**:
- LSH 기반 hash bucket partitioning + adaptive bucket probing
- "k-step neighboring-based probing": hamming distance k=1,2,3... 의 bucket 점진 탐색
- Two stopping conditions: (a) confidence ≥ tolerance ε, or (b) upper error bound < ε
- product quantization (PQ) 로 distance acceleration
- **baselines**: SimCard (2021) + MRCE (2024) + Uniform sampling + MRCE-10%
- **datasets**: SIFT 128d + GloVe 300d + FastText 300d + GIST 960d + YouTube 1770d
- **한계 명시**: PQ approximation 의 distribution shift 영역 (GloVe / FastText) 약함

**우리 위치 비교**:
- **layer 同일**: cardinality estimation for vector similarity query
- **기법 다름**: HKUST = LSH + PQ + adaptive bucket probing, 본 연구 = K-means stratification (학습 비용 0)
- **본 연구 영역의 정합성 위반 method (lsh, dense_rp, sparse_rp, halton, sobol, lhs, hammersley) 와의 차이**: HKUST 의 LSH 는 cardinality estimation 영역에서 valid (LSH 가 main mechanism), 본 연구의 LSH 는 paper N=385 budget 위반 (정합성 위반 폐기). **즉 본 연구 폐기 method 가 다른 framework 에서 valid 일 수 있음을 explicit 명시 가능** (옵션 N 의 영역 보강).

### 3.3 Filtered Vector Search VLDB 2025 (Caminal et al.) 핵심 tutorial

**제목**: "Filtered Vector Search: State-of-the-art and Research Opportunities"
**venue**: PVLDB Vol.18 No.12, 2025

**핵심 contribution**:
- filtered vector search (FVS) 의 tutorial paper
- 3 primary filtered search methods over tree-based / graph-based indices
- **stable recall declarative axis** 의 importance 명시
- open research challenges identification

**우리 위치 비교**:
- **layer 다름**: FVS = ANN index 영역의 filter handling, 본 연구 = query optimizer 영역의 cardinality estimation
- **declarative axis 同일**: FVS 의 declarative recall = 본 연구 의 declarative Q-error gap → 옵션 N 의 영역 보강

### 3.4 Reservoir Sampling over Joins (SIGMOD 2024, Dai-Hu-Yi)

**제목**: "Reservoir Sampling over Joins"
**저자**: Binyang Dai (HKUST), Xiao Hu (Waterloo), Ke Yi (HKUST)
**venue**: PACMOD SIGMOD 2024 + SIGMOD Record 2025
**arxiv**: 2404.03194

**핵심 contribution**:
- streaming setting 의 join sample maintenance
- acyclic join 의 O(N) index build + O(1) sample draw
- insertion-only streams 영역
- generalized reservoir sampling + dynamic index for join

**우리 위치 비교**:
- **layer 同일**: streaming + reservoir 영역
- **target 다름**: Dai-Hu-Yi = join result sampling, 본 연구 = cardinality estimation 의 sample 추출
- **기법 同일**: 본 연구의 P3 Streaming paradigm (reservoir / chao_weighted) 의 base
- ★★ **옵션 G 의 산업 적용 axis 정당성 매우 강력**: Dai-Hu-Yi 의 streaming + reservoir 가 SIGMOD 2024 published → 본 연구의 reservoir industry highlight 영역 timely

### 3.5 ACORN (SIGMOD 2024, Patel-Kraft-Guestrin-Zaharia Stanford FutureData)

**제목**: "ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data"
**저자**: Liana Patel, Peter Kraft, Carlos Guestrin, Matei Zaharia (Stanford)
**venue**: SIGMOD 2024 (paper [76] reference in Exqutor)

**핵심 contribution**:
- predicate-agnostic ANN index over vector + structured data
- HNSW-based subgraph traversal
- arbitrary / unbounded predicate sets
- 2-1000× higher throughput at fixed recall

**우리 위치 비교**:
- **layer 다름**: ACORN = ANN index 영역, 본 연구 = query optimizer 영역
- **scope 同일**: hybrid query (vector + structured) 영역
- ★ paper §VII (filtered vector search) 영역 인용 reference [76] = ACORN. 본 연구 multi-table A2-Fig9 영역 ACORN 비교 가능.

### 3.6 PSDSS (2025, Index-Based Progressive Sampling + Dynamic Sample Selection)

**제목**: "Cardinality estimation with index-based progressive sampling and dynamic sample selection"
**venue**: Journal of Intelligent Information Systems 2025

**핵심 contribution**:
- multi-table join cardinality estimation
- index-based progressive sampling + dynamic sample selection
- 기존 sampling 의 empty join + 높은 overhead 영역 해결

**우리 위치 비교**:
- **layer 同일**: cardinality estimation
- **scope 다름**: PSDSS = relational join, 본 연구 = vector similarity range query
- **기법 同일**: progressive sampling = 본 연구의 Eq 2-6 dynamic batch loop 의 base
- ★ 옵션 B 의 정당성 보강 (multi-table join 영역의 progressive sampling 영역 동향)

### 3.7 RELOAD (arxiv 2604.14725, BDAI Park 2025) ★★★ 박광현 본업

**제목**: "RELOAD: A Robust and Efficient Learned Query Optimizer for Database Systems"
**저자**: Seokwon Lee, Jaeyoung Sim, Sihyun Kim, Yuhsing Li (Yonsei BDAI), Yiwen Zhu (Microsoft Gray Systems), Kwanghyun Park (Yonsei BDAI, corresponding)
**venue**: arxiv 2604.14725 (2025)

**핵심 contribution**:
- RL-based learned query optimizer 의 robustness 영역 (Plateau + Rebound 두 failure mode)
- experience-aware knowledge retention (prioritized experience replay)
- complexity-aware knowledge transfer (MAML)
- 2.4× higher robustness + 3.1× faster convergence over RL baselines
- **baselines**: Bao + LOGER + Balsa + LIMAO
- **datasets**: JOB + TPC-DS + SSB

**우리 위치 비교**:
- **layer 多름**: RELOAD = plan selection (RL-based), 본 연구 = cardinality estimation
- **complement axis 매우 강력**: RELOAD 가 plan selection + 본 연구 cardinality module = end-to-end optimizer framework
- ★★★ **옵션 P 의 영역**: RELOAD learned QO + 본 연구 cardinality module 결합 framework. 박광현 본업 영역 직접 align.

### 3.8 박광현 BDAI 연구실 paper list 종합 (2024-2026)

**BDAI conferences.html 2024-2026 paper list 발굴**:

| year | paper | venue | 저자 | 본 연구 align |
|---|---|---|---|---|
| **2026** | **DFLOP**: Data-driven Framework for Multimodal LLM Training Pipeline Optimization | SIGMOD | An, Kim, Lim, Kim, Sen, Jung, Lee, Kim, Yu, Jeong, Kim, **Park** + SK Telecom + Microsoft | ★ ML training pipeline 영역, 본 연구 align partial |
| **2026** | **CANNON**: CXL-Based Near-Memory Processing for ANN | DAC | Kim, An, Kim, Sen, Park, Baek, Shin, Joo, **Park** + SK hynix + Microsoft | ★★ ANN 직접 영역 hardware/system, 본 연구 algorithm 영역 |
| **2026** | **RELOAD**: Robust and Efficient Learned Query Optimizer | arxiv preprint | Lee, Sim, Kim, Li, Zhu (Microsoft), **Park** | ★★★ 직접 영역, plan selection layer |
| **2025** | **Exqutor**: Extended Query Optimizer for VAQs | ICDE | Kim, Lim, An, Sen (Microsoft), **Park** | ★★★ 본 연구의 base paper |
| **2025** | **FaScalSQL**: GPU-Accelerated SQL Query Engine | ICDE | Lim, Lee, Choi, **Park**, Lee, Kim, Kim | ★ GPU acceleration 영역, 본 연구 algorithm 영역 |
| **2024** | **SPID-Join**: Skew-resistant Processing-in-DIMM Join Algorithm | SIGMOD | Lee, Lim, Choi, Choi, Lee, Park, **Park**, Kim, Kim | ★ DIMM-level join, 본 연구 algorithm 영역 |
| **2024** | Pushing ML Predictions into DBMSs | ICDE | Paganelli, Sottovia, **Park**, Interlandi, Guerra | ★ ML-DB integration, 본 연구 partial align |

**박광현 본업 영역 종합**:
- **ML/DB integration** (DFLOP / Pushing ML Predictions)
- **학습 query optimizer** (RELOAD)
- **near-memory ANN** (CANNON)
- **GPU acceleration** (FaScalSQL)
- **DIMM-level join** (SPID-Join)
- **vector-augmented query optimization** (Exqutor) ← 본 연구의 base

★★★ **박광현 본업 align axis** (5/15 미팅 시 valuable):
1. RELOAD + 본 연구 = end-to-end learned QO framework (옵션 P 의 영역)
2. CANNON + 본 연구 = ANN hardware + algorithm 결합
3. Exqutor (본 연구 base) + DFLOP (RAG pipeline) = RAG 영역의 end-to-end optimization

### 3.9 추가 발굴 paper (참고)

- **Quake: Adaptive Indexing for Vector Search** (USENIX OSDI 2025) — adaptive partition selection, partitioned index 동적 변경
- **HARMONY: Scalable Distributed Vector Database** (MIT 2025) — distributed query assignment + adaptive index
- **UNIFY: Range Filtered ANN Search** (PVLDB Vol.18) — graph + hierarchical hybrid index
- **SIEVE: Effective Filtered Vector Search** (arxiv 2507.11907) — collection of indexes
- **TKHist: Cardinality Estimation for Join Queries via Histograms** (CIKM 2025) — multi-table join cardinality estimation 영역

---

## 4. 박광현 BDAI 연구실 paper 살피기 종합

### 4.1 박광현 Google Scholar 핵심 영역 (research focus)

**핵심 paper (Google Scholar 발굴)**:
- "End-to-end optimization of machine learning prediction queries" (SIGMOD 2022, 73 citations)
- "Froid: Optimization of imperative programs in a relational database" (VLDB 2017, 134 citations)
- "Optimizing data pipelines for machine learning in feature stores" (2023)
- US Patent 12,242,493 (2025): "Query processing with machine learning"

**박광현 venues**:
- SIGMOD (2022, 2013, 2024 SPID-Join, 2026 DFLOP)
- VLDB (2017, 2019, 2022, 2023)
- ICDE (2021, 2024 Pushing ML, 2025 Exqutor + FaScalSQL)
- FAST (2021, 2022)
- DAC (2026 CANNON)

**박광현 research focus 종합**:
1. **ML/DB integration** (primary): ML prediction queries + feature stores + DFLOP
2. **query optimization** (secondary): Froid + Exqutor + RELOAD
3. **hardware-software co-design** (tertiary): Optane SSD + persistent memory + CXL CANNON
4. **GPU + DIMM acceleration**: FaScalSQL + SPID-Join

### 4.2 박광현 본업 = "Microsoft Gray Systems Lab" alumni (former)

**Microsoft Gray Systems Lab** 의 핵심 영역 = data + ML platform integration. 박광현 = ex-Microsoft engineer + 현 Yonsei assistant professor + BDAI Lab head.

★★★ **5/15 미팅 시 자문 axis (paper-driven)**:
1. **Exqutor 의 §V-B sample 추출 영역 augment** (본 연구) 가 박광현 본업 (ML/DB + QO) 의 어느 영역에 위치?
2. **RELOAD + 본 연구** 의 end-to-end framework 가능성?
3. **DFLOP RAG pipeline + 본 연구** 의 alignment?
4. **CANNON ANN hardware + 본 연구 algorithm** 의 결합 가능성?

---

## 5. 새 옵션 발산 (L, M, N, O, P)

### 5.1 옵션 L — paper §VI-A + §VI-E cost model ANN 미반영 영역 (★★★ Agent D 신규)

**영역 정의**:
- paper §VI-A 우단 + §VI-E Limitations 2번 의 **cost model 한계** 영역
- paper explicit 명시: "PostgreSQL's cost model remains insufficiently equipped to accurately reflect the performance characteristics of ANN-based vector indexes" + "Moreover, our approach relies on cost models that fail to fully capture the performance characteristics of ANN indexes, so even with accurate cardinality estimates the optimizer may still choose suboptimal plans"
- **본 연구의 sample 추출 augment 가 cost model 영역에 미치는 영향**: 본 연구 가 cardinality estimation 정확도 향상만 다룸, cost model 자체 영역 미다룸 → 본 연구 의 boundary 영역 정직 명시 + cost model 의 ANN 한계 영역 explicit 명시 + future work 영역 영구화

**추가 측정 / 작업 cost**:
- 측정: 0 (현 1001 file 의 cell 별 paired Δ% 분석 재해석)
- 분석: paper §VI-A cost model 영역 + §VI-E Limitations 2번 영역 verbatim 인용 + 본 연구 boundary 영역 명시 = **1 일 (8h)**
- 문서화: 5/27 deck + 6/11 보고서 추가 section = **0.5 일 (4h)**
- **총 cost: 약 10-15h** (옵션 A 와 결합 시 효율)

**학술 novelty**:
- ★★ paper-grade 가능 axis (paper limitation 영역 explicit 영구화 + 본 연구 boundary 영역 정직 명시)
- vector similarity domain 자체는 paper 가 이미 명시 → novelty = boundary 영역 정형화

**박광현 review-grade 가치**:
- ★★ positive 강함: paper limitation 영역 정직 분류 + 본 연구 boundary 영역 정직 명시 = BDAI 연구실 (DB rigor) 기조 일치
- **5/15 미팅 자문 항목**: "본 연구가 cost model 영역 안 다룸 → 학부 capstone 충분?" + "RELOAD + 본 연구 결합 가능?"

**1001 file 결과 활용 영역**:
- 현 측정 cell 별 paired Δ% = sample 추출 정확도 영역 evidence
- cost model 영역 측정 X (boundary 영역 정직 명시)

**5/27 / 6/11 timeline 적합성**:
- 5/27 발표: ★ 안전 (cost 10-15h)
- 6/11 보고서: ★ 안전

### 5.2 옵션 M — paper §VI-A Q20 lineitem dominant cost 영역 (Agent D 신규)

**영역 정의**:
- paper §VI-A 우단 명시 한계: "in queries like Q20, where the dominant cost arises from a full scan of the lineitem table, ECQO's impact is limited"
- 본 연구 측정 Q3 중심 (Fig.4 + Fig.5/6 + Fig.7/8/9) → Q20 환경 (lineitem dominant) 의 sample 추출 augment 영역 미측정
- 본 연구의 sample 추출 augment 가 Q20 환경에서 어떻게 작용?

**추가 측정 / 작업 cost**:
- 측정: 1 cell (Q20-DEEP sf=100) × 4 anchor method × 2 mode × 5 trial = 40 file ≈ **1-2h 서버 시간**
- 분석: Q3 vs Q20 paired Δ% 비교 + dominant cost 영역의 sample 추출 영향 = **0.5 일 (4h)**
- 문서화: 5/27 deck Q20 mini-section + 6/11 보고서 = **0.5 일 (4h)**
- **총 cost: 약 5-8h**

**학술 novelty**:
- ★ niche (paper 본인 명시 한계 영역의 정량 보강)
- review-grade 가능

**박광현 review-grade 가치**:
- review-grade ★ moderate (paper 본인 명시 영역의 정량 측정)

**1001 file 결과 활용 영역**:
- Q3 측정 (현 portfolio) 와 Q20 측정 (추가) 의 paired Δ% 비교

**5/27 / 6/11 timeline 적합성**:
- 5/27 발표: ★ 안전 (cost 5-8h)

### 5.3 옵션 N — CE4HD SRCE/MRCE + Ada-ef + paper §V-B + 본 연구 4-way 비교 framework (★★★ Agent D 신규 핵심)

**영역 정의**:
- paper §VI-D Fig.12 가 SelNet 만 비교 (Q-error 1.69 vs 5.53)
- **CE4HD VLDB 2024 (Lan-Bao) SRCE/MRCE** = SelNet 보다 ~136× smaller Q-error + ~10× faster
- **Ada-ef (Zhang-Miller 2025) Adaptive-ef** = HNSW ef adaptation + declarative target recall
- 본 연구의 K-means stratification = 학습 비용 0 + −10.17% 정확도 향상
- **4-way 비교 framework**: paper §V-B Bernoulli (baseline) vs SelNet (paper §VI-D 비교 한정) vs CE4HD SRCE/MRCE (VLDB 2024 SOTA, paper 미비교) vs Ada-ef (2025 distribution-aware, layer 다름) vs 본 연구 K-means stratification (학습 비용 0)

**추가 측정 / 작업 cost**:
- 측정: 0 (현 1001 file 그대로 활용, CE4HD/Ada-ef 는 paper level 인용)
- 분석: 4-way 비교 framework + 본 연구 위치 명시 + paper §VI-D 영역 보강 = **1-2 일 (10-15h)**
- 문서화: 5/27 deck framework slide + 6/11 보고서 framework section = **0.5 일 (4h)**
- **총 cost: 약 15-20h**

**학술 novelty**:
- ★★ paper-grade 가능 axis: vector similarity cardinality estimation 의 SOTA 4-way 비교 (paper §VI-D 영역 정직 보강)
- vector domain 정량 발현 novelty 명시 가능

**박광현 review-grade 가치**:
- ★★ positive 강함: paper §VI-D 영역 정직 보강 + CE4HD/Ada-ef 와의 본 연구 위치 명시 = paper-grade narrative

**1001 file 결과 활용 영역**:
- 100% 활용 (CE4HD/Ada-ef 는 paper level 인용 추가)

**5/27 / 6/11 timeline 적합성**:
- 5/27 발표: ★ 가능 (cost 15-20h)
- 6/11 보고서: ★ 안전

### 5.4 옵션 O — Ada-ef 비교 framework (Agent D 신규)

(위 §2.4 참조, 옵션 N 의 sub-component)

### 5.5 옵션 P — RELOAD + 본 연구 end-to-end learned QO framework (★★★ Agent D 신규)

**영역 정의**:
- RELOAD (BDAI Park 2025) = RL-based learned query optimizer (plan selection layer)
- 본 연구 = cardinality estimation augment (cardinality module layer)
- **결합 framework**: RELOAD plan selection 의 input 으로 본 연구 cardinality estimation 결과 활용
- 박광현 본업 영역 직접 align (5/15 미팅 시 직접 자문)

**추가 측정 / 작업 cost**:
- 측정: 0 (framework 영역, 실제 결합 측정은 future work)
- 분석: RELOAD architecture + 본 연구 cardinality module 결합 framework 설계 = **2-3 일 (16-24h)**
- 문서화: 5/27 deck framework slide + 6/11 보고서 framework section = **0.5-1 일 (4-8h)**
- **총 cost: 약 20-30h**

**학술 novelty**:
- ★★ paper-grade 가능 axis: end-to-end learned QO + cardinality module 결합 framework
- 박광현 본업 직접 영역

**박광현 review-grade 가치**:
- ★★ positive 강함: 박광현 본업 영역 직접 align, 5/15 미팅 자문 가능
- paper-grade 가능 (단 실제 결합 measurement future work)

**1001 file 결과 활용 영역**:
- cardinality module 의 input 으로 본 연구 결과 활용

**5/27 / 6/11 timeline 적합성**:
- 5/27 발표: △ 빡빡 (cost 20-30h)
- 6/11 보고서: ★ 가능

### 5.6 옵션 발산 종합 표

| 옵션 | 영역 | cost (h) | novelty | review-grade | timeline | hybrid 결합 |
|---|---|---:|---|---|---|---|
| L (Agent D 신규) | cost model ANN 미반영 한계 영역 boundary 정직 명시 | 10-15 | ★★ | paper-grade | ★ 안전 | A + L (★★ 권장) |
| M (Agent D 신규) | Q20 lineitem dominant cost 영역 paired 보강 | 5-8 | ★ | review-grade | ★ 안전 | A + M |
| **N** (Agent D 신규 핵심) | CE4HD/Ada-ef/SelNet/본 연구 4-way 비교 framework | 15-20 | **★★** | **paper-grade** | ★ 가능 | **A + G1 + N** (★★★ 본 1순위) |
| O (Agent D 신규) | Ada-ef statistical distribution modeling 비교 | 10-15 | ★ | review-grade | ★ 안전 | N 의 sub-component |
| **P** (Agent D 신규) | RELOAD + 본 연구 end-to-end learned QO framework | 20-30 | **★★** | **paper-grade** | △ 빡빡 | A + B + P (review-grade) |

---

## 6. paper-grade publication 가능성 평가

### 6.1 학술 paper level 가능성 비교 (Agent D 종합)

| 옵션 | 영역 | paper venue 가능성 | reasoning |
|---|---|---|---|
| A (Agent A/B/C base) | 현 narrative 유지 + 정직 disclosure | 학부 capstone ★★ / paper level ✗ | reproducibility + ablation type 영역 |
| B (Agent A/B/C) | Eq 2-6 dynamic batch loop 확장 | paper level △ (workshop / short paper 가능) | paper main 영역 augment + generalization 측정 필요 |
| C (Agent A/B/C) | Neyman paradox σ_j 메커니즘 일반화 | paper level ✗ (Cochran 1977 §5.5 part 포함) | known mechanism + vector domain 정량 한정 |
| D (Agent C 폐기) | L0-L4 framework | paper level ✗ (timeline + framework 한정) | framework novelty 단독 약함 |
| E (Agent C 폐기) | Multi-table + Centroid tuple main | paper level △ (vector domain novelty) | FactorJoin / TKHist 와의 differentiation 명시 필요 |
| F (Agent B/C) | ECQO 영역 비교 | paper level ✗ (paper 본인의 결합 비교 axis) | weak novelty |
| G (Agent B/C) | Reservoir streaming industry | paper level △ (G2 streaming framework 측정 시) | Reservoir over Joins SIGMOD 2024 와 alignment 필요 |
| **L** (Agent D 신규) | cost model ANN 미반영 boundary | **paper level ★★ (paper limitation 영역 영구화)** | paper future work axis 정량 보강 |
| M (Agent D 신규) | Q20 lineitem dominant 영역 | paper level ✗ (niche) | paper 본인 명시 영역의 정량 한정 |
| **N** (Agent D 신규) | CE4HD/Ada-ef/SelNet/본 연구 4-way 비교 framework | **paper level ★★ (vector domain SOTA 비교)** | paper §VI-D 영역 정직 보강 |
| **P** (Agent D 신규) | RELOAD + 본 연구 end-to-end framework | **paper level ★★ (BDAI 본업 영역)** | end-to-end learned QO framework |

### 6.2 paper-grade venue 가능성 종합 권장

★★★ **본 Agent D 의 권장 paper-grade publication path**:
1. **vector domain venue (CIKM / EDBT / SIGMOD workshop)**: 옵션 A + N (CE4HD/Ada-ef/SelNet 4-way 비교)
2. **DB workshop venue (VLDB workshop / SIGMOD undergraduate)**: 옵션 A + L (cost model boundary)
3. **future paper (post-capstone, 박광현 자문)**: 옵션 A + B + P (RELOAD 결합 framework)

### 6.3 학부 capstone 적합성 axis 권장

★★★ **본 Agent D 의 권장 학부 capstone path**:
1. **★ 가장 안전 (5/27 + 6/11 안전 100%)**: 옵션 A + G1 (현 narrative + reservoir industry)
2. **★★ paper-grade 접근 (5/27 가능, 6/11 안전)**: 옵션 A + G1 + N (4-way 비교 framework)
3. **★★ review-grade 강함 (5/27 빡빡, 6/11 가능)**: 옵션 A + B + L (Eq 2-6 + cost model boundary)
4. **★★★ paper-grade (5/27 무리, 6/11 가능)**: 옵션 A + B + P (RELOAD 결합 framework)

### 6.4 박광현 교수 paper-grade publication 가능성 평가

★★★ **박광현 본업 영역 정리**:
- 박광현 publications = ML/DB integration + 학습 query optimizer + near-memory ANN + GPU/DIMM acceleration
- Exqutor (2025) + RELOAD (2025) = 박광현 본업 학습 query optimizer 직접 영역
- **본 연구 = Exqutor 의 sample 추출 augment** = 박광현 본업 영역의 sub-component

**박광현 paper-grade publication 가능성 학술 reasoning**:
1. 옵션 A 의 정직 disclosure + 1001 file portfolio = BDAI 연구실 (DB rigor) 기조 일치
2. 옵션 L 의 cost model 영역 boundary 정직 명시 = paper future work axis 정량 보강
3. 옵션 N 의 4-way 비교 framework = paper §VI-D 영역 정직 보강
4. 옵션 P 의 RELOAD 결합 framework = 박광현 본업 영역 직접 align
5. **단, 옵션 P 의 실제 결합 measurement 는 future paper 영역** (학부 capstone 의 scope 너머)

★★★ **결론**: 박광현 본업 영역 직접 align axis = **옵션 P** (장기 paper-grade publication path), **옵션 N** (학부 capstone scope 내 paper-grade publication 가능), **옵션 L** (학부 capstone scope 내 paper future work axis 보강).

---

## 7. 5/15 박광현 자문 항목 재정립 (paper-driven, Agent D 종합)

### 7.1 Agent C 6 항목 (Agent D 검증 + 보강)

| # | 자문 항목 | Agent D 검증 |
|---|---|---|
| 1 | 옵션 A 학부 capstone 충분성 | ★ 유지 (옵션 A + G1 → ★★ 매우 강함) |
| 2 | 옵션 B 5/27 timeline 가능성 | ★ 유지 (cost 25-35h, 가속 필요) |
| 3 | 옵션 C Cochran 1977 §5.5 challenge 대응책 | ★ 유지 (vector domain 정량 발현 axis) |
| 4 | 옵션 G reservoir industry positioning | ★ 유지 + Dai-Hu-Yi SIGMOD 2024 alignment 추가 명시 |
| 5 | 옵션 F ECQO 비교 | ★ 유지 |
| 6 | hybrid 1/2/3 박광현 추천 | ★ 유지 |

### 7.2 Agent D 추가 자문 항목 (★ 새 7 항목)

| # | 자문 항목 | Agent D reasoning |
|---|---|---|
| 7 | **옵션 L (paper §VI-A + §VI-E cost model ANN 미반영 boundary)** = 학부 capstone 적합? paper-grade publication 가능? | paper limitation 영역 직접 정량 보강 |
| 8 | **옵션 M (Q20 lineitem dominant cost paired 보강)** = 측정 가능? | Q20 환경 (lineitem dominant) 영역 추가 측정 필요 |
| 9 | **옵션 N (CE4HD/Ada-ef/SelNet/본 연구 4-way 비교 framework)** = paper-grade publication 가능? venue 추천? | paper §VI-D 영역 정직 보강 |
| 10 | **옵션 O (Ada-ef statistical distribution modeling 비교)** = 본 연구와 layer 다름 명시 OK? | HNSW ef (Ada-ef) vs cardinality estimation (본 연구) 비교 framework |
| 11 | **옵션 P (RELOAD + 본 연구 end-to-end learned QO framework)** = 학부 capstone scope? future paper-grade publication path? | 박광현 본업 영역 직접 align |
| 12 | **CE4HD VLDB 2024 (Lan-Bao)** + paper §VI-D Fig.12 (SelNet 만 비교) = 본 연구 위치? | 4-way 비교 framework 의 정당성 |
| 13 | **paper §VII Filtered ANN single-relation 한정** vs 본 연구 multi-table A2-Fig9 영역 = ACORN 비교? | paper [76] reference ACORN 영역 |

### 7.3 5/15 미팅 자문 권장 우선순위 (Agent D 종합)

★★★ **본 Agent D 권장 자문 우선순위 (시간 한정 시)**:
1. **(★★★ 1순위)** 옵션 N 의 4-way 비교 framework + 옵션 L 의 cost model boundary = paper §VI-D + §VI-A + §VI-E 영역 정직 보강
2. **(★★ 2순위)** 옵션 P 의 RELOAD + 본 연구 결합 framework = 박광현 본업 영역 직접 align
3. **(★ 3순위)** 옵션 A + G1 (현 base) + 옵션 C (Cochran 1977 §5.5 challenge 대응책) = Agent C 권장 1순위
4. **(★ 4순위)** 옵션 B 의 Eq 2-6 dynamic batch 영역 + 5/27 timeline 가능성 = paper differentiation 영역

---

## 8. main thread 종합 권장 사항

### 8.1 본 Agent D 최종 권장 hybrid

★★★ **본 Agent D 종합 권장 hybrid path** (Agent A/B/C 의 1-3 순위 + Agent D 의 L/M/N/O/P 종합):

| 우선순위 | hybrid | 한 줄 요약 | 학술 가치 | cost (h) | 5/27 timeline |
|---|---|---|---|---:|---|
| **★★★ 1순위 (5/15 자문 결과 따라 결정)** | **A + G1 + N** | 현 narrative + reservoir industry highlight + 4-way 비교 framework (paper §VI-D 보강) | ★★ 학부 capstone + paper-grade 접근 | 25-35 | ★ 가능 |
| **★★ 2순위 (review-grade)** | **A + G1 + L** | 현 narrative + reservoir industry + cost model boundary 정직 명시 | ★★ review-grade + paper future work 영역 영구화 | 20-30 | ★ 안전 |
| **★★ 3순위 (5/27 안전)** | **A + G1** (Agent C 1순위) | 현 narrative + reservoir industry | ★★ 학부 capstone 매우 강력 | 10-15 | ★ 매우 안전 |
| **★ 4순위 (long-term, post-capstone)** | **A + B + P** | 현 narrative + Eq 2-6 확장 + RELOAD 결합 framework | ★★★ paper-grade publication path | 50-70 | 6/11 가능 (5/27 무리) |

### 8.2 본 Agent D 최종 권장 (1순위 A + G1 + N 선택 시) 의 5/27 발표 storyline 정형화

★★★ **본 Agent D 권장 5/27 발표 storyline (옵션 A + G1 + N)**:

§1. **문제 정의**: skew 영역 베르누이 부정확 + paper §V-B Eq 1 single sample 추출 영역
§2. **paper §V-B Algorithm 1 재현 (14-step)**: Eq 1 Bernoulli sample 추출 + Eq 2-6 dynamic batch loop (paper differentiation, 본 연구 미건드림)
§3. **본 연구 영역**: Eq 1 sample 추출 방식만 stratified K-Means K=20 으로 대체 (CaseA 단독) 또는 산술 평균 (CaseB 결합). Eq 2-6 유지.
§4. **정량 결과 trilogy (RQ1/RQ2/RQ3)**: 1001 file portfolio (B1 9 + CaseA 495 + CaseB 496). 단독 best −10.17% (paper Fig.12 mean qe 1.69 vs 1.618 = -4.3% 재현 ✓). 결합 92.5% paired CaseB < CaseA.
§5. **자원 효율 Pareto frontier**: Top 5 = sparse_rp / chao_weighted / neuram / pca1d / hilbert. reservoir industry highlight (Dai-Hu-Yi SIGMOD 2024 alignment).
§6. **★★★ 새 영역 (Agent D 추가)** — **vector similarity cardinality estimation 4-way 비교 framework**:
   - paper §V-B Bernoulli (baseline)
   - SelNet (paper §VI-D Fig.12 비교 한정, paper Q-error 5.53)
   - **CE4HD VLDB 2024 (Lan-Bao) SRCE/MRCE** (★ paper 미비교, SelNet 보다 ~136× Q-error smaller)
   - **Ada-ef arxiv 2512.06636** (★ HNSW ef adaptation, layer 다름 explicit 명시)
   - **본 연구 K-means stratification** (학습 비용 0 + −10.17%)
§7. **honest limitation**: Eq 2-6 영역 미건드림 + cost model 영역 미건드림 (paper §VI-A + §VI-E Limitations 1-2번 영역 정직 명시) + Cochran 1977 §5.5 영역 partial novelty 명시 + ★3 hilbert PCA-alias 명시

### 8.3 본 Agent D 결정적 disclosure

★★★ **본 Agent D 의 정직 disclosure (최종)**:
1. **옵션 N 의 학술 novelty 정직 명시**: CE4HD/Ada-ef/SelNet 4-way 비교 framework 의 novelty = framework axis (vector domain SOTA 비교 정형화) 한정. CE4HD + Ada-ef 자체가 본 연구 후보 method 아님 (paper level 인용).
2. **옵션 L 의 학술 novelty 정직 명시**: cost model ANN 미반영 boundary 영역 = paper limitation 영역 정량 보강 한정. 본 연구의 cost model 영역 측정 X.
3. **옵션 P 의 timeline 정직 명시**: RELOAD + 본 연구 end-to-end framework 의 실제 결합 measurement = future paper 영역. 학부 capstone scope 너머.
4. **★3 hilbert PCA-alias + ★4 sparse_rp Li-Hastie-Church 2006 reference**: 본 Agent D 가 추가 검증 안 함, Agent A/B/C 영역.

### 8.4 본 Agent D 5/27 발표 + 6/11 보고서 timeline 종합 권장

★★★ **본 Agent D 최종 종합 권장 (시간 한정)**:

**5/27 발표 (D-13)**:
- 1순위 hybrid: **A + G1 + N** (cost 25-35h)
- 2순위 hybrid: **A + G1 + L** (cost 20-30h)
- 3순위 hybrid (안전): **A + G1** (Agent C 1순위, cost 10-15h)

**6/11 보고서 (D-28)**:
- 5/27 발표 storyline 그대로 + 옵션 P (RELOAD framework) 의 future paper-grade publication path 영역 영구 명시
- 5/27 안 다룬 옵션 (B / C / F / E) 의 future work 영역 영구 명시

**★ 박광현 미팅 (5/15 14:00, D-1)**:
- 자문 우선순위 §7.3 참조
- 박광현 본업 영역 align axis = 옵션 P (RELOAD 결합) + 옵션 N (4-way 비교) + 옵션 L (cost model boundary)

---

작성: 2026-05-14 19:48 KST · Agent D · paper §V/§VI/§VII 전체 verbatim 재정독 (8 영역 발굴) + 경쟁 paper 5+ 편 발굴 (CE4HD VLDB 2024 + Ada-ef arxiv 2512.06636 + Adaptive Bucket Probing 2604.04603 + Reservoir Sampling over Joins SIGMOD 2024 + Filtered Vector Search VLDB 2025 tutorial) + 박광현 BDAI 본업 영역 정리 (RELOAD + DFLOP + CANNON + Exqutor + FaScalSQL + SPID-Join) + 새 옵션 5 (L/M/N/O/P) + paper-grade publication 가능성 평가 + 5/15 자문 항목 재정립 (Agent C 6 + Agent D 7)
