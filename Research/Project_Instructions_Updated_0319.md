# Project Instructions — Filtered ANNS Benchmarking Thesis

## 1. Purpose & Context

조현빈 is an undergraduate student in a database/systems research lab working on a **graduation thesis focused on benchmarking and comparative analysis of vector database algorithms** — not developing new algorithms. The core research domain is **filtered Approximate Nearest Neighbor Search (ANNS)**, with particular emphasis on HNSW-based filtering approaches.

Work is conducted in Korean. The research team divides paper-reading tasks among members, with 조현빈 playing a coordinating role.

---

## 2. Project Phase

> **현재 단계: 본 논문(Exqutor) 중심 실행 단계**
>
> 초기 탐색 단계(HNSW 알고리즘 서베이, 개별 논문 분석)는 종료됨.
> 이번 학기 목표는 **본 논문을 중심으로** 실험 수행, 데이터 정리, 결과 보고, 보고서 작성 등 실행 작업에 집중하는 것.
> 새로운 주제 서칭은 하지 않으며, 주제는 본 논문(Exqutor)으로 확정됨.

---

## 3. Current State

### Completed Work
- **Exqutor paper** deep analysis 완료: ECQO + momentum-based adaptive sampling을 통한 VAQ 카디널리티 추정. 검증 gap 식별 완료 (ANN recall sensitivity, dynamic data, hyperparameter sensitivity, billion-scale, IVF compatibility).
- **Reference reading list** (~26 papers) organized into five tracks for team distribution. Track 1 (vector index and filtering papers) overlaps with work 조현빈 has already done.
- Individual paper analyses completed: ACORN, SeRF, iRangeGraph, FINGER, FlatNav, SHG, Patience in Proximity, Exqutor
- **[1], [13], [20] 심층분석 및 미팅 준비 문서 완료** (3/19 완료)
  - (09) [1] AnalyticDB-V 미팅준비 심층분석 (.md + .docx) — VAQ 개념 원조, Lambda 아키텍처, VGPQ, 정확도 인식 최적화, 카디널리티 추정 공백 분석
  - (10) [13] pgvector 미팅준비 심층분석 (.md + .docx) — 33.3% 고정 선택도 문제, HNSW/IVFFlat, planner hook, Exqutor 1000배 향상 근거
  - (11) [20] PostgreSQL 벡터한계 미팅준비 심층분석 (.md + .docx) — 5가지 한계 (버퍼풀/MVCC/공간증폭/구축시간/선택도), 근본 vs 구현 분류
  - (12) [1]+[13]+[20] 통합요약 + 문제정의 + 미팅대본 (.md + .docx) — 3편 연결고리, 문제 정의 공식화, 15분 미팅 전체 대본, 16개 Q&A
  - 각 문서에 총정리, 핵심 개념 해설, Exqutor 연결고리, Q&A 12~16개, 미팅 발표 대본 포함

### In Progress
- Team reading list distribution and coordination across five tracks
- 다음 단계: 팀 레퍼런스 리딩 완료 후 지식 통합 → 실험 설계 확정

### Not Yet Started
- Experimental design finalization (datasets, metrics, system combinations)
- Implementation and benchmark execution
- Thesis writing

---

## 4. Milestone Timeline

> 졸업논문 제출 마감: **6월 중**

| 마일스톤 | 목표 시기 | 상태 |
|---|---|---|
| 레퍼런스 핵심 논문 재독 + 문제 정의 | 3월 중순~말 | ✅ 완료 (3/19) |
| 팀 레퍼런스 리딩 완료 + 지식 통합 | 4월 초 | 🔄 진행 중 |
| 실험 설계 확정 (데이터셋, 메트릭, 시스템 조합) | 4월 중 | ⬜ 미착수 |
| 구현 + 벤치마크 실행 | 4월 중~5월 중 | ⬜ 미착수 |
| 결과 분석 + 시각화 | 5월 중~말 | ⬜ 미착수 |
| 논문 초고 작성 | 5월 말~6월 초 | ⬜ 미착수 |
| 최종 수정 + 제출 | 6월 중 | ⬜ 미착수 |

> **Note**: 위 타임라인은 초안이며, 실제 랩 일정 및 교수 피드백에 따라 조정될 수 있음.

---

## 5. Paper Status Tracker

### 5.1 개별 분석 완료 논문

| Paper | Domain | Status | Key Takeaway |
|---|---|---|---|
| ACORN | Label filtering | ✅ Analyzed | Excels at label filtering; underperforms on range filtering vs SeRF |
| SeRF | Range filtering | ✅ Analyzed | Segment graph optimized for range conditions |
| iRangeGraph | Range filtering | ✅ Analyzed | — (재확인 필요) |
| FINGER | Traversal optimization | ✅ Analyzed | Optimizes traversal speed; untested in filtered environments |
| FlatNav | Flat graph (anti-hierarchy) | ✅ Analyzed | Argues hierarchy unnecessary in high dimensions |
| SHG | Learned shortcuts | ✅ Analyzed | Proposes learned shortcuts to optimize hierarchy |
| Patience in Proximity | — (재분류 필요) | ✅ Analyzed | — (재확인 필요) |
| Exqutor | Query optimization | ✅ Analyzed | ECQO + adaptive sampling for cardinality estimation |

### 5.2 미분석 / 팀 배분 대상 논문

| Paper | Domain | Status | 비고 |
|---|---|---|---|
| UNIFY | Filtered ANNS | 📋 To read | — |
| FilteredDiskANN | Disk-based filtered ANNS | 📋 To read | Exqutor ref [41] |
| NHQ | Attribute-constrained ANN | 📋 To read | Exqutor ref [18] |

> **Note**: "📋 To read" 상태의 논문은 조현빈이 직접 읽을 논문과 팀원에게 배분할 논문으로 나뉠 수 있음. 상태가 업데이트되면 반영할 것.

---

## 6. Exqutor Reference List (Full)

> 본 논문(Exqutor)의 전체 레퍼런스. **[1], [13], [20]은 심층분석 완료 (3/19)**.
> 5개 트랙 배분 매핑은 확정 후 반영할 것.

### A. Vector DB Systems & Architectures
| Ref# | Title / System | Venue/Year | 비고 |
|---|---|---|---|
| [1] | AnalyticDB-V: hybrid analytical engine for structured + unstructured data | VLDB 2020 | ✅ 심층분석 완료 (09) |
| [7] | SingleStore-V: integrated vector DB system | VLDB 2024 | — |
| [9] | AnDB: AI-native database for universal semantic analysis | arXiv 2025 | — |
| [10] | VBASE: unifying online vector similarity search and relational queries | OSDI 2023 | Exqutor 통합 대상 |
| [11] | Milvus: purpose-built vector data management system | SIGMOD 2021 | — |
| [12] | Qdrant | — | — |
| [13] | pgvector: open-source vector similarity search for PostgreSQL | 2021 | ✅ 심층분석 완료 (10), Exqutor 통합 대상 |
| [19] | DuckDB: embeddable analytical database | SIGMOD 2019 | Exqutor 통합 대상 |
| [20] | Fundamental limitations of vector data management in RDBMS (PostgreSQL) | ICDE 2024 | ✅ 심층분석 완료 (11) |
| [26] | Pinecone | — | — |
| [27] | Manu: cloud native vector DBMS | arXiv 2022 | — |
| [28] | Chroma | — | — |
| [30] | PASE: PostgreSQL ultra-high-dim ANN search extension | SIGMOD 2020 | — |
| [31] | DuckDB-VSS: vector similarity search extension | 2024 | — |
| [32] | Vespa.ai | — | — |
| [33] | Neo4j vector index and search | — | — |
| [34] | Redis vector database | — | — |

### B. ANN Search Algorithms & Indexes
| Ref# | Title / System | Venue/Year | 비고 |
|---|---|---|---|
| [18] | NHQ: efficient ANN search with attribute constraint | NeurIPS 2023 | 미분석, 팀 배분 대상 |
| [38] | HNSW: hierarchical navigable small world graphs | IEEE TPAMI 2018 | 핵심 기반 알고리즘 |
| [39] | NSG: fast ANN search with navigating spreading-out graphs | VLDB 2019 | — |
| [40] | SONG: ANN search on GPU | ICDE 2020 | — |
| [41] | Filtered-DiskANN: graph algorithms for ANN search with filters | WWW 2023 | 미분석, 핵심 비교 대상 |
| [42] | PM-LSH: fast and accurate LSH framework | VLDB 2020 | — |
| [43] | Neighbor-sensitive hashing | VLDB 2015 | — |
| [44] | FLANN: scalable NN algorithms for high-dim data | IEEE TPAMI 2014 | — |
| [45] | VHP: ANN via virtual hypersphere partitioning | VLDB 2020 | — |
| [46] | Annoy (Spotify) | 2013 | — |
| [47] | Product quantization for NN search | IEEE TPAMI 2011 | — |
| [48] | FAISS | 2017 | 실험 인프라 |
| [49] | Billion-scale similarity search with GPUs | IEEE TBD 2019 | — |

### C. Query Optimization & Cardinality Estimation
| Ref# | Title | Venue/Year | 비고 |
|---|---|---|---|
| [4] | Accelerating ML inference with probabilistic predicates | SIGMOD 2018 | — |
| [50] | Exact cardinality query optimization with bounded execution cost | SIGMOD 2019 | ECQO 원논문 |
| [51] | Learned cardinality estimation for similarity queries | SIGMOD 2021 | — |
| [52] | Kepler: robust learning for parametric query optimization | SIGMOD 2023 | — |
| [53] | ECQO for optimizer testing | VLDB 2009 | — |
| [54] | Analyzing query optimizer performance with/without cardinality estimates | arXiv 2023 | — |

### D. Analytics, Benchmarks & Surveys
| Ref# | Title | Venue/Year | 비고 |
|---|---|---|---|
| [5] | Analytical engines with context-rich processing | ICDE 2023 | — |
| [6] | Context-enhanced relational operators with vector embeddings | arXiv 2023 | — |
| [8] | High-throughput vector similarity search in knowledge graphs | SIGMOD 2023 | — |
| [14] | ClickHouse | VLDB 2024 | — |
| [16] | Scalable similarity search for big data | 2015 | — |
| [17] | Spider 2.0: text-to-SQL evaluation | arXiv 2024 | — |
| [23] | TPC benchmarks (TPC-H) | 2000 | 벤치마크 기반 |
| [24] | The making of TPC-DS | VLDB 2006 | 벤치마크 기반 |
| [25] | Vector database management techniques and systems (tutorial) | SIGMOD 2024 | — |
| [29] | Survey of vector database management systems | VLDB Journal 2024 | — |

### E. Foundations & Miscellaneous
| Ref# | Title | Venue/Year | 비고 |
|---|---|---|---|
| [2] | Hybrid RAG for IoMT | IEEE IoT Journal 2024 | — |
| [3] | Tree-based RAG-agent recommendation | arXiv 2025 | — |
| [15] | Blended RAG | MIPR 2024 | — |
| [21] | DNA Sequence Classification with Milvus | 2024 | 응용 사례 |
| [22] | On the importance of initialization and momentum in deep learning | ICML 2013 | Momentum-based sampling 배경 |
| [35] | K-nearest neighbor (기초) | Scholarpedia 2009 | — |
| [36] | Review of k-NN query processing techniques | 2011 | — |
| [37] | Generalized k-NN rules | 1986 | — |

> **5개 트랙 배분 매핑**: 위 카테고리(A~E)는 논문의 성격에 따른 분류이며, 팀 내부의 5개 트랙 배분과는 다를 수 있음. 실제 팀 트랙 배분이 확정되면 각 논문에 트랙 번호를 추가할 것.

---

## 7. Experimental Design (Draft)

> 이 섹션은 아직 확정되지 않은 초안 상태. 대화를 통해 구체화해 나갈 것.

### 7.1 Target Datasets (Candidates)
- **Small-scale**: SIFT1M, GloVe-100
- **Medium-scale**: Deep10M, GIST1M
- **Large-scale**: Deep1B, SIFT1B (if feasible given hardware)
- 각 데이터셋에 대해 synthetic filter 생성 필요 (label, range, compound)

### 7.2 Core Evaluation Metrics
- **Search quality**: Recall@k (k=1, 10, 100)
- **Search speed**: QPS (queries per second), latency (p50, p99)
- **Build cost**: Index build time, memory overhead
- **Scalability**: Performance degradation curve as dataset grows

### 7.3 Comparison Axes
- **Selectivity sweep**: 0.1%, 1%, 10%, 50%, 90% selectivity에서의 성능 변화
- **Filter type**: Label equality, range predicate, compound (label + range)
- **Algorithm families**: Pre-filtering, post-filtering, hybrid (in-filter) approaches

### 7.4 Target Systems (Candidates)
- ACORN, SeRF, iRangeGraph, FilteredDiskANN
- Baselines: pgvector, VBASE, brute-force filtered search
- 오픈소스 구현 여부 및 Python/FAISS 호환성이 실질적 선택 기준

### 7.5 Experimental Conditions (미확정 — 후보)
- **Distance metric**: L2 (Euclidean), Cosine similarity, Inner product — 데이터셋별로 적합한 metric 선택 필요
- **Query set**: 쿼리 수 (e.g., 1K, 10K), 생성 방식 (데이터셋에서 랜덤 샘플 vs held-out set)
- **Reproducibility**: 반복 측정 횟수 (e.g., 3~5회), warm-up run 포함 여부, cold/warm cache 조건 구분
- **Parallelism**: Single-thread vs multi-thread QPS 측정 여부

### 7.6 Hardware & Environment
- (미정 — 랩 서버 스펙 확인 필요)
- CPU, RAM, SSD/HDD, GPU 유무 등 명시 필요
- OS, Python version, FAISS version 등 소프트웨어 환경도 기록할 것

---

## 8. Key Learnings & Research Landscape

### Filtering Methods
- **ACORN**: Label filtering에 강점, range filtering에서는 SeRF 대비 약세
- **SeRF**: Range condition에 최적화된 segment graph 구조
- **FINGER**: Traversal 속도 최적화에 집중, filtered 환경에서의 검증 부재

### Open Research Tensions (2025)
- **FlatNav vs SHG**: Hierarchy 불필요론 (FlatNav) vs Learned shortcut으로 hierarchy 최적화 (SHG) — 논문 포지셔닝에 참고
- **Filtering methods vs Search improvement methods**: 서로 직교적 문제를 다루며, 조합은 아직 미개척 영역

### Recurring Gaps in Literature
- Billion-scale validation 부족
- Dynamic indexing (insert/delete) 지원 미비
- Filter type 다양성 부족 (대부분 label filtering만 실험)
- Selectivity 극단값(매우 높거나 매우 낮은)에서의 행태 미보고

### [1]+[13]+[20] 심층분석에서 도출된 핵심 인사이트 (3/19)
- **AnalyticDB-V [1]**: VAQ 개념의 원형 제시. 벡터 검색을 SQL 물리 연산자로 통합하고 정확도 인식 비용 최적화를 도입했으나, 카디널리티 추정은 "고정 선택도" 가정에 의존 → Exqutor의 근본 동기
- **pgvector [13]**: PostgreSQL의 벡터 검색 확장. 핵심 한계는 **고정 선택도 33.3%** 문제 — 실제 선택도와 최대 1000배 이상 괴리. Exqutor의 adaptive sampling이 이를 직접 해결
- **PostgreSQL 한계 [20]**: RDBMS에서 벡터 관리의 5가지 한계 식별 (버퍼풀 래치 경합, MVCC 오버헤드, 8KB 페이지 공간증폭, WAL 인덱스 구축 지연, 고정 선택도). 이 중 선택도 문제(한계5)는 "구현 개선 가능"으로 분류되며, Exqutor가 정확히 이 지점을 해결
- **3편의 연결 구조**: AnalyticDB-V가 VAQ 개념 제시 → pgvector가 RDBMS 통합 시도하나 선택도 추정 실패 → [20]이 이를 포함한 구조적 한계 체계화 → **Exqutor가 선택도 추정 문제를 ECQO + adaptive sampling으로 해결**

---

## 9. Approach & Communication Patterns

### Analysis Style
- **Staged, structured analysis**: 이론 → 실험 로직 → 참고문헌/함의 순서로 진행
- Cross-paper 비교는 각 논문 분석이 완료된 후에만 수행
- 한 번에 하나의 논문에 집중, 맥락 전환 최소화

### Output Format Preferences
- **서사적 한국어 학술 산문** 선호 (bullet point 나열 지양)
- 배경 맥락 → 핵심 아이디어 → 번호 매긴 최적화 기법(O1, O2...) → 번호 매긴 후속 질문 구조
- 부속 절은 ~~ 기호로 표시
- 한국어로 작업; 학술 글쓰기 및 팀 지식 공유 용도

### Technical Detail Expectations
- 데이터셋, 하드웨어 스펙, baseline, 핵심 메트릭, build time, memory overhead, 이론적 보장 — 모두 기본 포함 사항
- 피상적 요약 지양, 실험 조건과 한계까지 다룰 것

---

## 10. Tools & Resources

- **Implementation**: Python, NumPy, FAISS
- **Key Venues**: SIGMOD, VLDB, ICML 및 관련 시스템/ML 학회
- **Knowledge Management**: 팀 기반 논문 분담 체계
- **Target Systems**: pgvector, VBASE, DuckDB (참고용)

---

## 11. Practical Constraints

- 오픈소스 구현이 있는 논문 우선
- Python/FAISS 호환성 필수
- 졸업논문 일정 고려 (구현 복잡도 vs 비교 범위의 트레이드오프)
- 새 알고리즘 개발이 아닌 **비교 분석**이 목표 — 실험 설계의 공정성과 체계성이 핵심 기여
- 본 논문(Exqutor)의 프레임워크 안에서 작업 — 새 주제 탐색 단계는 종료됨

---

## 12. 생성 문서 인덱스

> 프로젝트 진행 과정에서 생성된 분석/요약 문서 전체 목록. 각 문서는 .md + .docx 형태로 존재.

### 시리즈 A: Exqutor + 레퍼런스 분석/요약 (기존)
| 번호 | 문서명 | 설명 |
|---|---|---|
| (01) | Exqutor 상세분석 | 본 논문 상세 분석 |
| (02) | Exqutor 통합요약 | 본 논문 요약 |
| (03) | 레퍼런스 6편 상세분석 | 초기 6편 개별 분석 |
| (04) | 레퍼런스 6편 통합요약 | 초기 6편 요약 |
| (05) | 레퍼런스 24편 상세분석 | 24편 개별 분석 |
| (06) | 레퍼런스 24편 통합요약 | 24편 요약 |
| (07) | 레퍼런스 81편 상세분석 | 81편 개별 분석 |
| (08) | 레퍼런스 81편 통합요약 | 81편 요약 |

### 시리즈 B: [1]+[13]+[20] 심층분석 + 미팅 준비 (3/19 생성)
| 번호 | 문서명 | 설명 |
|---|---|---|
| (09) | [1] AnalyticDB-V 미팅준비 심층분석 | VAQ 원형, 카디널리티 추정 공백, Q&A 12개, 미팅 대본 |
| (10) | [13] pgvector 미팅준비 심층분석 | 고정 선택도 33.3%, HNSW/IVFFlat, Q&A 14개, 미팅 대본 |
| (11) | [20] PostgreSQL 벡터한계 미팅준비 심층분석 | 5가지 한계, 근본 vs 구현, Q&A 12개, 미팅 대본 |
| (12) | [1]+[13]+[20] 통합요약+문제정의+미팅대본 | 3편 연결, 문제 정의 공식화, Q&A 16개, 15분 발표 대본 |

### 기타 개별 논문 총정리
- [0]~[81] 개별 논문 총정리 문서 (.md + .docx + .pdf) — 각 레퍼런스별 상세 분석
