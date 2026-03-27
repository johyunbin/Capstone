# Exqutor 레퍼런스 논문 발표 스크립트

> 담당 논문: [1], [6], [7], [10], [11], [20]
> 본 논문(Exqutor)과의 관계를 중심으로 설명

---

## [1] AnalyticDB-V — A Hybrid Analytical Engine Towards Query Fusion for Structured and Unstructured Data

**저자:** Chuangxian Wei, Bin Wu, Sheng Wang 외 (Alibaba Group)
**학회:** VLDB 2020

---

이 논문은 Exqutor가 풀려고 하는 문제의 출발점이 되는 논문입니다. Alibaba에서 만든 AnalyticDB-V라는 시스템인데요, 핵심은 "벡터 유사도 검색을 SQL에 통합하자"는 것입니다. 기존에는 이미지·텍스트 같은 비구조화 데이터를 검색하려면 별도의 벡터 엔진을 써야 했는데, 이걸 하나의 SQL 쿼리로 처리 가능하게 만든 겁니다.

주요 기여:

1. 벡터 검색을 ANNS라는 SQL 물리적 연산자로 구현해서, SELECT 문 안에서 직접 벡터 유사도 검색을 호출할 수 있게 했습니다.
2. ANN 검색의 정확도-속도 트레이드오프를 옵티마이저가 자동 관리하는 Accuracy-Aware CBO를 도입했습니다.

그런데 핵심적인 빈틈이 있습니다. 옵티마이저가 벡터 검색 결과의 카디널리티를 추정할 때 **고정 선택도 10%를 가정**합니다. 실제로는 쿼리마다 결과 건수가 완전히 다른데, 일괄적으로 10%로 가정하니까 추정 오류가 20배까지 벌어질 수 있고, 이러면 완전히 비효율적인 실행 계획을 세우게 됩니다.

결론적으로, AnalyticDB-V는 VAQ 개념을 최초로 산업 규모에서 구현한 중요한 논문이지만, 카디널리티 추정 문제는 해결하지 못했습니다. Exqutor의 ECQO가 바로 이 고정 선택도 가정을 버리고, 실제 인덱스를 탐색해서 정확한 카디널리티를 얻는 방법을 제안합니다.

---

## [6] Context-Enhanced Relational Operators with Vector Embeddings

**저자:** Sanca, Chatzakis, Ailamaki (EPFL)
**학회:** VLDB 2025

---

이 논문은 "관계형 연산자에 벡터 임베딩을 결합하자"는 제안입니다. E-Operator와 E-Join이라는 새로운 개념을 정의하는데, 기존 관계형 연산자를 임베딩으로 확장한 것입니다.

주요 기여:

1. E-Operator는 "의미적으로 유사한 것"이라는 조건을 관계형 대수의 공식 연산자로 정의합니다. E-Join은 키 값이 아니라 벡터 유사도 기반으로 두 테이블을 결합합니다.
2. Prefetch 최적화로 E-Join의 모델 호출을 O(|R|×|S|)에서 O(|R|+|S|)로 줄이고, Tensor Join으로 GPU 활용 시 약 100배 속도 향상을 달성합니다.

Exqutor와 연결되는 핵심 발견이 있습니다. 이 논문이 실험적으로 보여준 것인데, **최적의 실행 전략이 선택도에 따라 완전히 달라진다**는 것입니다. 결과가 적으면 인덱스 스캔이, 많으면 풀 스캔이 유리합니다. 그런데 정작 그 선택도를 정확히 추정하는 방법은 제시하지 않았습니다.

결론적으로, 아무리 좋은 E-Operator와 E-Join을 만들어도 옵티마이저가 카디널리티를 모르면 올바른 전략을 선택할 수 없습니다. Exqutor의 ECQO가 이 선택도를 정확히 제공해서, [6] 같은 새로운 연산자들이 실제로 제대로 활용될 수 있는 토대를 만들어줍니다.

---

## [7] SingleStore-V — An Integrated Vector Database System in SingleStore

**저자:** Chen, Jin, Zhang 외 (SingleStore / Univ. of Waterloo)
**학회:** VLDB 2024

---

이 논문은 상용 DB인 SingleStore에 벡터 검색을 통합한 시스템입니다.

주요 기여:

1. `ORDER BY similarity LIMIT k` 패턴을 전용 Top() 물리적 연산자로 처리해서 단일 테이블 top-k 검색을 최적화합니다.
2. 세그먼트 기반 인덱스 구조로 데이터 추가 시 전체 인덱스를 재구축하지 않고, Faiss·HNSW·DiskANN 등 플러거블 인덱스를 지원합니다.

한계는 명확합니다. SingleStore-V는 **단일 테이블 top-k 검색**에 특화되어 있어서, 여러 테이블을 조인하면서 벡터 검색도 함께 수행하는 복잡한 VAQ 처리에는 한계가 있습니다.

결론적으로, SingleStore-V가 단일 테이블 top-k를 잘 처리한다면, Exqutor는 그 위에서 다중 테이블 조인 최적화를 담당하는 셈입니다. 여러 테이블 조인이 포함된 VAQ에서 벡터 연산의 카디널리티를 정확히 추정하고 최적의 조인 순서를 결정하는 것 — 이게 Exqutor가 해결하는 문제입니다.

---

## [10] VBASE — Unifying Online Vector Similarity Search and Relational Queries via Relaxed Monotonicity

**저자:** Qianxi Zhang, Shuotao Xu, Qi Chen 외 (Microsoft Research Asia)
**학회:** VLDB 2023

---

이 논문은 Exqutor가 실험에서 직접 비교한 시스템이고, Exqutor가 **최대 10,000배 성능 향상**을 달성한 대상입니다. 왜 그런 극적인 차이가 나는지 이해하려면 VBASE를 알아야 합니다.

주요 기여:

1. Relaxed Monotonicity(완화된 단조성) 개념을 도입합니다. 벡터 검색은 기존 DB 연산자의 단조성을 만족하지 않는데, 이 제약을 완화해서 벡터 검색 결과도 관계형 파이프라인에서 처리할 수 있게 합니다.
2. 전통적인 Volcano iterator 모델에 벡터 검색을 자연스럽게 통합합니다.

핵심적인 한계가 있습니다. VBASE는 벡터 연산에 대한 통계가 없어서 **고정 선택도 33.3%~50%를 사용**합니다. 실제 결과가 100건인데 옵티마이저가 330,000건으로 추정하면, 해시 조인을 선택하지만 실제로는 인덱스 네스티드 루프 조인이 훨씬 빠른 상황이 됩니다. 이 추정 오류가 수천~만 배의 실행 시간 차이를 만듭니다.

결론적으로, VBASE는 이론적으로 우아하지만 옵티마이저에 벡터 통계를 제공하지 못합니다. Exqutor의 ECQO가 정확한 카디널리티를 제공하는 것만으로 최대 10,000배 성능 향상을 달성한 것은, "옵티마이저에게 정확한 정보를 주는 것"이 얼마나 중요한지를 극적으로 보여줍니다.

---

## [11] Milvus — A Purpose-Built Vector Data Management System

**저자:** Jianguo Wang, Xiaomeng Yi, Rentong Guo 외 (Zilliz / Texas A&M)
**학회:** SIGMOD 2021

---

이 논문은 벡터 전용 DB인 Milvus에 대한 것입니다. Exqutor가 왜 전용 벡터 DB가 아니라 범용 관계형 DB를 개선하는 방향을 택했는지를 이해하기 위해 필요합니다.

주요 특징:

1. 처음부터 벡터 유사도 검색을 위해 설계되어 벡터 검색 성능 자체는 최고 수준입니다.
2. 클라우드 네이티브 아키텍처로 수십억 벡터까지 스케일링 가능하고, IVF·HNSW·DiskANN 등 거의 모든 ANN 알고리즘을 지원합니다.

근본적 제약은, **복잡한 SQL 분석을 지원하지 않는다**는 것입니다. 여러 테이블 JOIN, GROUP BY, 서브쿼리 같은 기능이 없어서, 벡터 검색 결과를 분석 쿼리와 결합하려면 애플리케이션 레벨에서 따로 처리해야 합니다.

결론적으로, 이것이 Exqutor가 Milvus 대신 pgvector·VBASE·DuckDB 같은 범용 DB를 대상으로 연구한 이유입니다. 범용 DB는 이미 강력한 SQL 기능을 갖고 있고 여기에 벡터 기능이 추가되는 추세인데, 문제는 옵티마이저가 벡터 연산을 이해하지 못한다는 것이고, Exqutor의 ECQO가 바로 이걸 해결합니다.

---

## [20] Are There Fundamental Limitations in Supporting Vector Data Management in Relational Databases?

**저자:** Yiwen Zhang, Yingfeng Liu, Jianbin Wang 외 (East China Normal University)
**학회:** VLDB 2025

---

이 논문은 "관계형 DB에서 벡터 데이터를 지원하는 데 근본적인 한계가 있는가?"라는 질문을 다룹니다.

주요 문제점:

1. 옵티마이저가 벡터 연산에 대한 통계를 전혀 갖고 있지 않아서, 고정 선택도(33.3% 등)를 사용합니다.
2. 이로 인해 실행 계획이 최적이 아닌 경우가 빈번합니다.
3. 벡터 인덱스가 관계형 인덱스와 근본적으로 다른 구조여서, 기존 비용 모델이 적용되지 않습니다.

결론은, 한계는 "근본적"이 아니라 "구현적"이라는 것입니다. 관계형 DB의 프레임워크 자체는 벡터를 지원할 수 있지만, 옵티마이저가 벡터 연산의 특성을 모르기 때문에 성능이 떨어집니다. Exqutor의 ECQO가 바로 이 빈틈을 메워서, 관계형 DB 위에서도 벡터 연산을 효율적으로 처리할 수 있게 만듭니다.

---

## 전체 연결 정리

6편을 관통하는 핵심 메시지는 이겁니다:

[1] AnalyticDB-V와 [7] SingleStore-V는 "벡터를 SQL에 통합하자"는 방향을, [6]은 벡터를 관계형 연산으로 격상시켰고, [10] VBASE는 Volcano 모델 통합의 이론적 기반을 놓았습니다. [11] Milvus는 전용 벡터 DB의 SQL 한계를 보여주며 범용 DB 개선의 필요성을 드러냈고, [20]은 근본적 한계는 없지만 구현적 한계가 있다고 진단했습니다.

이 모든 연구에서 공통적으로 미해결인 문제: **옵티마이저가 벡터 연산의 카디널리티를 모른다.** 고정 선택도 사용이 실행 계획을 망가뜨리고, Exqutor의 ECQO가 실제 인덱스 프로빙으로 이 근본 문제를 해결합니다.
