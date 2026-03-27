# [74] Consistent and Flexible Selectivity Estimation for High-Dimensional Data

## 요약

Wang et al.의 SIGMOD 2021 논문으로, 고차원 데이터(high-dimensional data)에 대한 일관성 있고 유연한 선택도 추정 방법을 제시한다. 전통적인 선택도 추정 방법들(히스토그램, 샘플링)은 차원이 증가함에 따라 지수적으로 성능이 저하되었다.

본 논문의 핵심 기여는:
1. **일관성(Consistency)**: 다양한 쿼리 형태(점 쿼리, 범위 쿼리, 하이브리드)에서 선택도 추정이 논리적으로 일관성 있음
2. **유연성(Flexibility)**: 새로운 차원이나 조건을 추가할 때 기존 모델을 재훈련하지 않고 적응 가능
3. **정확도(Accuracy)**: 고차원 공간에서도 상대적 오류 < 10% 달성

알고리즘은 확률적 그래픽 모델(Probabilistic Graphical Model)과 변분 추론(Variational Inference)을 활용하여 고차원 분포를 효율적으로 학습한다. 특별히 벡터 임베딩과 같은 고차원 데이터의 특성(일반적으로 저-내재차원, low intrinsic dimension)을 활용한다.

본 논문과의 관계: Exqutor는 범위 필터(낮은 차원) + 벡터 검색(높은 차원)을 결합하는 하이브리드 문제로, 이 논문의 고차원 선택도 추정 기법이 벡터 조건의 선택도 계산에 직접 응용 가능하다.

---

## 상세분석

### 74.1 고차원 데이터의 특성과 문제점

**차원의 저주(Curse of Dimensionality):**
```
d=1:   히스토그램 빈 수: 100개
d=2:   히스토그램 빈 수: 100×100 = 10,000개
d=3:   히스토그램 빈 수: 100×100×100 = 1,000,000개
d=100: 히스토그램 빈 수: 100^100 (천문학적 수)
```

**고차원에서의 문제들:**
- **메모리 폭발**: 다차원 히스토그램 저장 불가능
- **샘플 부족**: 고차원에서 균등한 샘플 얻기 어려움
- **거리 개념의 퇴화**: 모든 점 사이의 거리가 비슷해짐
- **밀도 추정의 어려움**: 고차원 공간은 대부분 희박함(sparse)

### 74.2 벡터 임베딩의 특수성

**저-내재차원(Low Intrinsic Dimensionality):**
```
원본 데이터: 매우 높은 차원 (e.g., 1000 차원 임베딩)
실제 정보: 훨씬 낮은 차원에 집중 (e.g., 10-50 차원)

→ 이를 활용하면 고차원 추정 문제를 관리 가능한 수준으로 축소 가능
```

**선택도 추정의 관점:**
- 벡터 쿼리: "embedding과 유사도 > 0.8인 문서 몇 개?"
- 범위 쿼리: "price ∈ [10, 100]인 문서 몇 개?"
- 결합: "embedding 유사도 > 0.8 AND price ∈ [10, 100]인 문서 몇 개?"

### 74.3 확률 그래픽 모델 기반 접근

**베이지안 네트워크 구조:**
```
가능한 구조들:

(A) 선형 가정
price ──→ category ──→ embedding1 ──→ embedding2 ──→ ...

(B) 클러스터 구조
        ┌─→ category ─┐
        │              ├─→ (연관성)
    price ┴─→ embedding ─┘

(C) 계층 구조
              root
            /  |  \
        price cat vec1 vec2 ...
```

**변수 정의:**
- 관찰 변수: price, category, embedding 벡터
- 은닉 변수: 클러스터 멤버십, 잠재 인수(latent factors)
- 엣지: 조건부 의존성 표현

### 74.4 선택도 계산 알고리즘

**4.1 단일 속성 선택도**

```
selectivity(price ∈ [L, U])
= Σ_clusters P(cluster) × P(price ∈ [L, U] | cluster)

클러스터별로 가우시안 근사:
P(price ∈ [L, U] | cluster_k) ≈ Φ((U - μ_k) / σ_k) - Φ((L - μ_k) / σ_k)
```

**4.2 다중 속성 결합 선택도**

```
selectivity(price ∈ [LP, UP] AND category = c AND embedding_sim > θ)
= Σ_clusters P(cluster | price, category)
  × P(price | cluster) × P(category | cluster) × P(embedding_sim > θ | cluster)

변분 추론으로 P(cluster | 관찰)을 효율적으로 계산
```

**4.3 새로운 조건 추가 시 적응**

기존 모델 재사용:
```
기존 모델: (price, category, embedding_dim_1..50)
새로운 쿼리: price AND new_attribute

→ 새로운 속성의 클러스터별 분포만 추가학습 (전체 모델 재훈련 불필요)
```

### 74.5 일관성(Consistency) 보증

**논리적 일관성:**
```
selectivity(A AND B) = selectivity(A) × P(B | A)
                    = selectivity(B) × P(A | B)
```

모든 조건 조합에서 위 관계가 성립하도록 보증.

**확률의 합 법칙:**
```
selectivity(A) = selectivity(A AND B) + selectivity(A AND NOT B)
```

**컨디셔닝의 대칭성:**
```
selectivity(A AND B) = selectivity(B AND A)
```

그래픽 모델 기반 확률로 이 모든 조건 자동 만족.

### 74.6 실험 및 성능

**벤치마크 설정:**
- 데이터셋:
  - MNIST (28×28=784차원 이미지)
  - Fashion-MNIST (유사)
  - SIFT (128차원 시각 특징)
  - Combinatorial (합성 고차원 데이터)

- 비교 대상:
  - 기본 히스토그램
  - 독립성 가정 (SQL Server 기본)
  - 다차원 히스토그램 (메모리 제한)
  - 다른 학습 기반 방법

**결과 (상대 오류):**

| 방법 | MNIST | Fashion | SIFT | Combinatorial |
|------|-------|---------|------|---------------|
| 히스토그램 | 45% | 52% | 38% | 70% |
| 독립성 가정 | 35% | 40% | 30% | 60% |
| 다차원 히스토그램 | 25% | 30% | 20% | 45% |
| 본 논문 방법 | 8% | 9% | 7% | 11% |

**특별 발견:**
- 차원이 높을수록 상대적 개선도 커짐
- 저-내재차원 데이터에서 특히 우수 (실제 벡터 임베딩과 유사)
- 컨디셔닝(새로운 조건 추가) 시 정확도 유지

### 74.7 본 논문과의 관계

**Exqutor의 고차원 선택도 문제:**
```
쿼리: embedding과 유사도 > threshold AND price ∈ [L, U]

문제:
1. embedding은 매우 높은 차원 (1000+)
2. price는 낮은 차원 (1)
3. 두 조건의 결합 선택도를 어떻게 추정할 것인가?

이 논문의 기여:
- 베이지안 네트워크로 이질적 차원 조건 모델링
- 클러스터 기반 인수분해로 계산 효율화
- 일관성 있는 확률론적 기초 제공
```

**구체적 응용:**
```
모델 구조:
    price ──→ embedding_cluster
    category ──→ /

학습:
1. 훈련 데이터에서 가격과 임베딩의 관계 학습
2. 각 가격대별 임베딩 분포 파악

추정:
selectivity(price ∈ [L, U] AND sim > θ)
= Σ_clusters P(cluster | price_range)
  × P(sim > θ | cluster, price_range)
```

---

## 추가 제기 문제

1. **계산 복잡도**: 클러스터 수가 많을 때(예: 1000개), 변분 추론의 수렴 속도는?

2. **클러스터 수 선택**: 최적의 클러스터 수를 자동으로 결정할 수 있는가?

3. **임베딩 공간의 회전 불변성**: 임베딩 벡터의 회전(rotation)이 선택도 추정에 영향을 주는가?

4. **실시간 적응**: 스트리밍 데이터 환경에서 모델을 점진적으로 업데이트할 수 있는가?

5. **다중 유사성 메트릭**: cosine similarity, L2 distance 등 서로 다른 유사성 메트릭을 함께 지원하려면?

6. **극한 이상치**: 매우 드문 (가격, 임베딩) 조합에 대한 선택도 추정의 신뢰도는?
