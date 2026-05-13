# 5월 27일 최종 발표 storyline (v1)

> **팀**: 속도는벡터 (박세은·강재현·조현빈·이동욱)
> **발표 일시**: 2026-05-27 (화) 19:00
> **분량**: 약 15분 (슬라이드 20장 안팎) + Q&A
> **작성**: 2026-05-13

---

## 들어가는 말

이 글은 5월 27일 최종 발표를 어떤 순서로, 어떤 흐름을 가지고 진행할지 정리한 발표용 시나리오다. 4월 28일 중간 보고서에서 정리한 RQ1·RQ2 결과를 바탕으로 5월 한 달 동안 진행한 RQ3 측정과 추가 분석을 발표 자리에서 자연스럽게 풀어 가는 데 초점을 두었다. 슬라이드 한 장 한 장의 문구가 아니라, "왜 이런 흐름이 필요한가"를 우리 팀 안에서 합의하기 위한 글이다. 발표 슬라이드는 이 문서를 기준으로 추후 정리한다.

발표 전체 흐름은 청자가 자연스럽게 따라올 수 있는 일곱 단계의 순차 흐름으로 잡았다. 먼저 우리가 들여다본 문제를 정의하고, 분포 인지 방법 56 개를 탐색하면서 어떤 것이 실제로 측정 가능한지를 정리한 다음, 단독 대체 가능성을 분석하고, 그 결과를 바탕으로 결합 framework 검토로 넘어가고, 자원 효율을 함께 살펴본 뒤, 마지막에 성능과 자원 사이의 경계에서 본 연구의 권장 design 을 추출하고, 발표를 마무리한다.

---

## 1. 문제 정의 — 우리가 들여다본 영역 (약 2분)

발표를 시작하면서 가장 먼저 청자에게 전달하고 싶은 것은 우리가 푼 문제의 위치다. 최근 데이터베이스 환경에서는 이미지나 텍스트를 임베딩 벡터로 바꿔서 검색하는 작업과, 날짜·가격 같은 일반적인 표 데이터를 SQL 로 분석하는 작업이 한 데이터베이스 안에서 동시에 일어난다. 이걸 벡터 증강 분석 쿼리 (VAQ, Vector-augmented Analytical Query) 라고 부른다. 우리 연구는 이런 쿼리를 잘 처리하려면 옵티마이저가 결과 행 수를 얼마나 정확히 추정하느냐, 즉 카디널리티 추정이 핵심이라는 점에서 시작한다.

문제는, pgvector, VBASE, DuckDB 같은 기존 시스템들이 벡터 조건의 선택도를 33.3%, 50%, 100% 같은 고정 비율로 둔다는 것이다. 실제 선택도는 데이터와 쿼리에 따라 0.001% 부터 100% 까지 크게 바뀐다. 잘못된 선택도 추정은 잘못된 실행 계획으로 이어지고, 잘못된 실행 계획은 최대 1만 배까지 느려지는 결과를 낳는다. 이 문제를 해결하기 위해 Exqutor 라는 논문 (arXiv:2512.09695v2, BDAI 연구실) 이 두 가지 방법을 제시한다. 인덱스가 있을 때는 HNSW range query 로 실제 카디널리티를 구하고 (ECQO), 인덱스가 없을 때는 적응적 샘플링 (Adaptive Sampling) 으로 추정한다.

우리 연구는 이 중에서 두 번째, 즉 인덱스가 없을 때 작동하는 적응적 샘플링 영역을 다룬다. 본 논문은 이 부분에서 베르누이 무작위 샘플링을 사용한다. 우리의 질문은 단순하다 — 데이터가 한쪽에 몰려 있을 때 (skew 분포), 이 무작위 샘플링이 충분히 정확한가? 그리고 더 정확하게 만들 수 있는 방법은 무엇인가? 이 출발점에서 RQ1 과 RQ2 가 자연스럽게 따라온다.

**RQ1 (약 1분 내 압축)**: PostgreSQL 의 두 표본 추출 방식 (SYSTEM 블록 단위 vs BERN 행 단위) 을 짝지어 비교한 결과, 모든 selectivity 구간에서 SYSTEM 이 BERN 보다 부정확하며, SIFT 의 selectivity 0.05 구간에서 최대 17.32% 격차다 (paired Wilcoxon p ≤ 10⁻⁴⁹). 본 논문이 사용한 베르누이가 이미 PostgreSQL 두 옵션 중 더 나은 쪽이지만, 베르누이조차 분포에 따라 정확도가 달라진다는 출발점이 된다.

**RQ2 (약 1분 내 압축)**: 분포를 미리 안다는 가정 아래, 다섯 가지 할당 방식 (베르누이 / 동등 / 비례 / Neyman / 반(反) Neyman) 의 짝지어 비교 결과, "베르누이에서 비례 할당으로 바꾸면 평균 9.53% 정확도 개선" 이 한 줄 요약이다. Neyman 이 비례보다 약간 부정확한 역설 (1.595 vs 1.580) 은 PartSupp PK 의 클러스터 균등 분포 (CV=0) 와 좁은 σ 범위 (1.3~1.6 배) 가 만든 자연스러운 결과로, 분포를 알면 비례 할당이 답이지만 실제 운영에서는 분포를 모를 때가 많다는 점이 RQ3 로 이어지는 출발점이다.

---

## 2. 분포 인지 방법 56 개의 탐색 — 어떤 것이 측정 가능하고 어떤 것이 폐기되는가 (약 2.5분)

RQ3 의 첫 단계는 분포 정보를 얻으려는 후보 method 56 개를 8 패러다임 (클러스터링, 공간 분할, 스트리밍, 차원 축소, 정보 이론, 양자화, 준 무작위 (QMC), 밀도 추정) 으로 모아 9 cell 매트릭스 (DEEP·SIFT·SSN × sf=10/100 × single·multi) 에서 측정을 시도한 것이다. 측정을 진행하면서 일부 method 는 그대로 둘 수 없는 문제가 발견되어 폐기했는데, 그 사유를 측정 과정 그대로 풀어서 설명한다.

### 2.1 측정 과정에서 폐기된 method 들

**자원 한계로 실행이 어려운 method**

- **birch**: 클러스터를 트리 구조로 저장하는 CFNode 가 작은 데이터셋에서도 50 ~ 200GB 메모리를 차지하면서 측정 서버에서 실행이 불가능했다.
- **agglomerative**: SimSearchNet++ 256 차원 데이터셋에서 모든 점 쌍의 거리를 한꺼번에 계산하다가 메모리 부족으로 실행이 실패했다.
- **hdbscan**: 데이터셋 일부에서 알고리즘 내부 분기가 KMeans 로 fallback 되어, 사실상 KMeans 와 동등한 측정 결과를 내놓았다.
- **kde_parzen**: 한 cell 측정에 4 시간 이상의 timeout 이 필요해서 전체 측정 portfolio 9 cells × 56 method 를 마감 안에 완성할 수 없었다.
- **dirichlet, kernelpca, neuocard**: 자원이나 구현 안정성 문제로 9 cells 전부를 완료하지 못했다.

**알고리즘 구현 코드를 보니 paper 의도와 다른 것이 발견된 method 들**

- **kdtree**: 알고리즘 구현 코드를 보면 leaf 인덱스가 단순한 modular hash (`idx % n_strata`) 로 처리되어 있어서, 무작위 표집과 거의 동등하다. paper 가 의도한 kdtree 의 공간 분할 효과가 아니다.
- **vinecopula**: 코드 구현이 rank 변환 + PCA 1 차원 정렬의 별칭 (alias) 으로 되어 있어서, Bedford-Cooke 1986 의 진짜 vine copula 가 아니다.
- **neuram**: 코드 한 줄씩 검토한 결과 PCA1D 와 100% 동일하다.
- **ams_count_sketch**: lsh 와 코드가 한 줄씩 동일하다.
- 그 외 약 20 종도 같은 방식으로 reference 위반이나 알고리즘 잘못 표기가 5월 10일 8-agent 정독 검토에서 발견되어 폐기했다 — 총 23 method.

**큰 데이터셋에서 추정값이 극단으로 튀는 method 들**

halton, sobol, lhs, hammersley, dense_rp, random_projection, dbscan, ccsketch, lsh, ams_count_sketch — 이 9 종은 측정 결과가 SSN sf=100 같은 큰 dataset 에서 +145,483%, +213,065% 등의 외곽 값으로 나타났다. paper 가 정의한 N=385 sample budget 안에서 estimator 가 안정적이지 않다는 뜻이라서 정합성 위반으로 폐기했다.

이 과정을 거치고 남은 측정 가능한 method 는 약 43 개다. 이들이 본 연구의 비교 실험군이며, 8 패러다임 분류 위에서 측정 결과를 정리한다.

### 2.2 남은 43 method 의 paradigm 별 평균 결과 — 어떤 패러다임이 좋은가

남은 method 의 결과를 8 패러다임으로 묶어 평균 효과 (CaseB 산술 평균 모드 기준) 를 보면 다음과 같다.

| paradigm | 평균 Δ% (CaseB) | 대표 anchor method |
|---|---:|---|
| 밀도 추정 (Density) | -11.93% (n=1 caveat) | Parzen KDE |
| 정보 이론 (Information Theoretic) | -7.60% (n=9) | HyperLogLog |
| 스트리밍 (Streaming) | -6.63% | Chao 1982 weighted reservoir |
| 차원 축소 (Dimension Reduction) | -6.03% | Sparse Random Projection |
| 공간 분할 (Spatial) | -5.57% | Hilbert curve, Z-order |

이 표만 보면 "어떤 패러다임이 가장 좋은가" 에 대한 답이 보이지만, paradigm 평균이 일부 method 의 극단값에 끌려가는 경우가 있다 (예: P1 클러스터링 안의 wavelet_hist 가 +68%). 그래서 본 연구는 paradigm 평균을 보조 정보로 두고, 다음 단계에서 단독 대체 가능성을 method 단위로 살펴본다.

---

## 3. 단독 대체 가능성 분석 — paper 의 베르누이를 우리 method 로 바꿔도 되는가 (약 2분)

다음 질문은 자연스럽다. 남은 43 method 의 추정값을 본 논문의 베르누이 대신 그대로 갈아 끼우면 (CaseA 단독 대체 모드) 어떻게 되는가?

측정 결과를 정직하게 풀어 정리하면 다음과 같다.

- **평균 우위 약 40%**: 56 방법 중 약 40% 가 평균적으로는 베르누이 기준선보다 정확했다.
- **통계 일관 우위 7.6% (15/197)**: 그러나 같은 method 라도 데이터셋과 cell 마다 효과의 편차가 컸다. 통계 검정 (BH-FDR 보정 + paired Wilcoxon p<0.05) 으로 cell 전반에서 안정적으로 베르누이를 우위로 누른 method 는 7.6% 정도다.
- **15 method 의 평균 개선폭 -5 ~ -12%**: 단독 대체로 통계 일관 우위인 15 method 의 평균 개선폭은 -5 ~ -12% 다. 이는 paper 자체 재현 시 발생하는 측정 변동 (paper Fig 12 영역 -4.3%) 보다 1.2 ~ 3 배 큰 의미 있는 개선이다. 즉 단독 대체로도 noise floor 를 넘는 실제 개선이 가능한 method 가 존재한다.
- **selectivity / dataset 별 일관성**: 일관 우위 15 method 중에서도 selectivity 0.01 같은 작은 쿼리와 0.10 같은 큰 쿼리에서 효과가 다르고, DEEP / SIFT / SSN 사이에서도 효과가 다르다.

결론은 이렇게 정리된다. **단독 대체로 noise floor 를 넘는 개선이 가능한 method 가 일부 존재하지만 (15/197 = 7.6%), 56 방법 전체에 걸쳐 산업 적용을 보장할 만한 압도적 우위는 아니다.** 그리고 이 안정성 부족 자체가 다음 단계 — 결합 framework 검토 — 의 motivation 이다.

---

## 4. 결합 framework 검토 — 산술 평균이 효과적인가 (약 2분)

단독 대체의 안정성 부족을 보완하기 위해 다음으로 검토한 방향이 두 추정값을 결합 (combine) 하는 framework 다. 처음에는 가장 단순한 결합 방식 — 산술 평균 (0.5 / 0.5) — 으로 측정을 진행했다.

**CaseB 산술 평균 모드의 측정 결과**: `est_final = (est_bernoulli + est_method) / 2.0` 로 두 추정값을 단순 평균한 결과, 492 개의 짝지어 비교한 (paired) 측정 중 455 개 (92.5%) 에서 베르누이 단일 baseline 보다 더 정확하다. paired Wilcoxon p < 10⁻⁴⁵, Cliff's δ large better 63.0%, 효과크기 지표 Hedges' g 기준 large 55.7% 다. anchor method 12 종 (lpm2, hilbert, sparse_rp, hilbert_real, minibatch, chao_weighted, neuram, pca1d, reservoir, thompson_sampling, hyperloglog, opq, pq) 은 cell 전반에서 -9 ~ -10% 의 일관된 개선과 2 ~ 3 의 안정적 표준편차를 보인다.

**왜 산술 평균이 효과적인가**: 베르누이 무작위 샘플링은 편향 (bias) 이 0 이지만 분산 (variance) 이 크다. 클러스터 기반 계층적 표집 추정량은 분포 가정이 맞을 때는 분산이 작지만, 가정이 빗나가면 편향이 생길 수 있다. 두 추정값을 산술 평균하면 한 쪽이 실패할 때 다른 쪽이 보완해 주는 안정적인 구조가 된다. 즉 "단일 추정량의 안정성 한계를 결합으로 보강한다" 가 본 연구의 핵심 narrative 다.

**산술 평균이 best 인가**: 다만 산술 평균이 가장 좋은 결합 방식인지는 아직 모른다. 가중치 평균 (w·est_bernoulli + (1-w)·est_method), 기하 평균, 분산 기반 결합 (inverse variance weighting) 같은 다른 결합 방식과의 비교는 future work 다. 발표 자리에서는 "산술 평균 결합이 단독 대체보다 안정적이라는 점은 분명하다, 다만 best 결합 방식 비교는 향후 연구" 라고 정직하게 짚는다.

---

## 5. 자원 효율 분석 — 학습 비용을 고려하면 어떤 method 가 실용적인가 (약 2분)

성능 (정확도) 만으로는 산업 적용을 결정할 수 없다. 학습 시간, 메모리 사용, 차원 한계가 method 마다 다르기 때문이다. 5 단계는 자원 효율을 정량적으로 정리한다.

### 5.1 43 method 의 학습 비용 비교

폐기되지 않은 43 method 의 학습 비용을 비교하면 차이가 매우 크다.

- **가벼운 method**: sparse_rp (0.3 sec), kmeans 계열 (0.5 ~ 2 sec), reservoir 계열 (스트리밍 즉시).
- **중간 method**: HyperLogLog (메모리 KB 단위, 한 번 학습 후 재사용 가능), Hilbert curve (좌표 계산만).
- **무거운 method**: birch (50 ~ 200GB RSS 폭증, 폐기), agglomerative (256 차원에서 OOM, 폐기).

### 5.2 cheap 근사 — Centroid tuple 의 "더 싸고 더 좋은" 패턴

multi-table cell (예: DEEP + WIKI cross) 에서 계층적 표집을 어떻게 할지의 문제가 있다. 두 가지 후보가 있다.

- **비싼 multi-join 재학습**: 두 벡터를 864 차원으로 합친 후 KM20 을 처음부터 다시 학습. 학습 시간이 single-table 의 2 배 + 추가 disk I/O.
- **cheap 근사 (Centroid tuple)**: 두 single-table 의 클러스터 결과를 (s_A, s_B) tuple 로 합쳐서 그대로 사용. 학습 비용 0 추가.

8 measurement 결과를 비교하면, CaseB 산술 평균 모드에서 4 method 모두 (sparse_rp, chao_weighted, hilbert_real, hyperloglog) cheap 근사가 비싼 재학습보다 평균 -0.84%p 정확도가 더 좋다. 즉 **"더 싸고 더 좋은"** best of both worlds 결과로, multi-table 영역 확장의 cheap 근사 가능성을 보여 준다.

### 5.3 단독 대체 vs 결합의 자원 비교

단독 대체는 우리 method 만 사용하므로 학습 비용 = 우리 method 학습 비용 그대로다. 결합은 베르누이 (paper 본문) 와 우리 method 두 estimator 의 합인데, paper 의 sample budget (N=385) 을 두 estimator 가 공유하므로 query 시 추가 시간은 거의 없다. 즉 결합의 자원 추가 부담은 측정 시간 기준 무시 가능하다. 학습 단계에서는 우리 method 만 학습하면 되므로 단독 대체와 동일하다.

---

## 6. 성능과 자원 사이의 경계 — 본 연구의 권장 design (약 1.5분)

성능 (산술 평균 결합의 92.5% 안정적 우위) 과 자원 (cheap 근사로 0 학습 비용 추가) 사이의 균형 영역에서 본 연구가 권장하는 design 을 추출하면 다음 세 원칙의 조합이다.

1. **산술 평균 결합** — 본 논문 베르누이 추정량과 분포 인지 계층적 추정량을 산술 평균 (`est_final = (est_bernoulli + est_method) / 2.0`) 으로 합쳐서 한 쪽 추정량의 실패를 다른 쪽이 보완하는 안정적인 구조를 만든다.
2. **cheap 근사 사용** — multi-table cell 에서는 비싼 864 차원 재학습 대신 두 single-table 클러스터 결과의 (s_A, s_B) tuple folding 으로 0 학습 비용에 더 좋은 정확도를 얻는다.
3. **method-aware 적용** — 12 anchor method 중에서도 cell 별 K-민감도와 quality-민감도 패턴이 다르므로, sparse_rp 와 chao_weighted 에는 정밀 처리 (K=20 + multi-join 재학습), Hilbert curve 와 HyperLogLog 에는 단순 처리 (cheap 근사 + carry-over) 를 선택적으로 적용한다.

산업 적용 영역은 두 가지다. (1) PostgreSQL pgvector 의 default sampling 메커니즘에 우리 method 의 stratified estimator 를 산술 평균으로 추가하면 옵티마이저 카디널리티 추정의 안정성이 향상된다. (2) Exqutor 의 §V-B 모듈에 우리 안 (산술 평균 + cheap 근사 + method-aware) 을 통합하면 paper 본문 성과 (1만 배 속도 개선) 위에 추가적인 정확도 layer 를 얹을 수 있다.

본 연구는 또한 추가 가설 두 가지 — multi-table 재계층화의 정확도 영향과 저비용 근사 가능성 — 도 정량 검증하였다. 측정 결과 method 가 환경 변화에 보이는 민감도 패턴이 method 의 내부 메커니즘 차이를 반영하는 부수 발견도 정리하였다 (자세한 내용은 부록 참조).

---

## 7. 마무리 — 한계와 향후 연구 (약 1.5분)

발표의 마지막은 우리 연구의 한계를 정직하게 짚고, 6월 11일 최종 보고서에서 어떤 부분을 추가로 정리할지를 공유한다.

가장 중요한 한계는 측정 범위다. 9 cells × 56 method × 2 modes 의 매트릭스에서 비교 실험군에 해당하는 method 는 9 cells × 2 modes 모두 완료했지만, 미커버 영역을 9 가지 카테고리로 정직하게 분류한다. 가장 큰 비중은 자원 한계 (birch 메모리 50-200GB 폭증, A1-SSN cell 의 80GB NPY fetch timeout), 알고리즘 정독 검토 (5월 10일 8-agent code audit 으로 발견한 reference 위반 23 method 폐기), 그리고 본 논문 §V-A multi-table 영역과의 경계 (우리는 §V-B 영역에 한정) 다.

본 연구는 산술 평균이라는 가장 단순한 결합 방식부터 측정을 시작하여 결합 framework 자체의 효과를 baseline 수준에서 입증하였다. 실제 산업 적용을 위해서는 데이터셋의 분포 특성, 차원, 질의 선택도에 따라 결합 방식이 동적으로 결정되는 data-aware ensemble framework 가 필요하다. 본 연구의 산술 평균 결과는 그 framework 의 출발점이며, 향후 연구는 두 그룹으로 나뉜다.

**Group A — Data-aware ensemble framework 5 방향**: (A1) Distribution-aware ensemble — skew / dense 데이터셋에 따라 결합 가중치 동적 결정, (A2) Dimensionality-aware ensemble — 차원 별 결합 방식 선택 (예: 차원 큰 → PCA preprocessing 결합), (A3) Estimator-confidence-aware (BLUE, Best Linear Unbiased Estimator) — 각 estimator 의 분산 추정 기반 분산 최소화 가중치, (A4) Query-aware ensemble — selectivity 별 결합 방식 변경, (A5) Meta-learning adaptive ensemble — 측정 환경 feature 를 입력으로 ML 모델로 결합 가중치 학습.

**Group B — 일반 확장 6 방향**: (B1) 다른 데이터셋 일반화 — YFCC, GLOVE 등에서 동일 패턴 검증, (B2) 논문 동적 framework 와 완전 정합 — Q-error 신호 source 명시, (B3) 이론적 분산 분해 — Cochran 1977 §11.10 composite estimator 적용, (B4) 다른 결합 방식 비교 — 가중치 sweep, 기하 평균, 분산 기반 결합 (Group A 의 baseline 비교), (B5) 다른 cheap 근사 후보 — PCA preprocessing, Iterative refinement, Hash bucketing, (B6) 실제 시스템 적용 — pgvector 또는 Exqutor 의 prototype 통합 측정.

가까운 시일의 일정은 두 가지다. 5월 28일 임채림 박사님과의 SAP 미팅에서 본 연구 결과를 추가 검증한다. 6월 11일 최종 보고서에서 위 두 그룹 (Group A 5 방향 + Group B 6 방향) 의 향후 방향 중에서 다음 분기에 우선순위로 둘 영역을 명시한다.

---

## 부록 — Method 메커니즘 분석 (Q&A 참조용)

이 부록은 발표 본문에서 한 줄로만 짚은 method-level consistency 와 3-axis sensitivity 분석 (2 axis 일치 + 1 axis 다른 분류) 패턴을 풀어 둔 것이다. 청자가 Q&A 에서 묻거나, 박광현 교수님 / 임채림 박사님 같은 도메인 전문가가 본 연구의 method 분류 axis 에 대해 질문할 경우의 참조용이다.

### 부록 A — Method-level consistency

본 연구의 결과를 paradigm 단위로만 보면 paradigm 우위를 단정 짓기 어렵다. paradigm 안에 wavelet_hist (P1 클러스터링, +68% 더 나빠짐), lp_bound (P4 차원 축소, +16% 더 나빠짐) 같은 극단값 method 가 평균을 끌어 올리거나 끌어 내리기 때문이다. 진짜 finding 은 12 개의 anchor method 가 다양한 환경 (데이터셋, cell, 선택도) 에서 모두 비슷한 정도로 (cell 전반에서 -9 ~ -10%) 일관되게 개선한다는 것이다. paradigm 분류 자체보다는 method 안의 internal sampling 메커니즘 — 클러스터 quality 에 얼마나 의존하는지, hash 기반인지 space-filling curve 기반인지 — 이 더 본질적인 분류 기준이라는 시사점이다.

### 부록 B — 3-axis sensitivity 분석 (2 axis 일치 + 1 axis 다른 분류)

5월 12 ~ 13 일에 진행한 세 가지 추가 측정 영역에서 method 별 민감도 패턴을 측정했다.

(1) **K granularity 민감도**: 클러스터 개수 K 를 10, 20, 30 으로 바꾼 측정. sparse_rp 는 K=20 에서 -10.6%, K=10 에서 +5.05% (더 나빠짐), K=30 에서 -6.78% 의 U 모양을 보인다 (K-sensitive). chao_weighted 는 K=20 sweet spot 패턴. 반면 hilbert_real 과 hyperloglog 두 method 는 K 값에 거의 영향을 받지 않는다 (K-robust).

(2) **multi-join 재학습 민감도**: 두 벡터 테이블을 864 차원으로 합쳐서 KM20 재학습한 8 measurement. sparse_rp 와 chao_weighted 는 CaseA 모드에서 -2.6 ~ -3.5%p 추가 개선 (multi-jn sensitive), hilbert_real 과 hyperloglog 는 거의 차이 없음 (robust). CaseB 산술 평균 모드에서는 4 method 모두 차이 없음 (평균 -0.12%p).

(3) **Centroid tuple cheap 근사 친화도**: 비싼 multi-join 재학습 대신 single-table 클러스터의 (s_A, s_B) tuple folding 으로 cheap 근사. CaseB 산술 평균 모드에서 4 method 모두 평균 -0.84%p 추가 정확도이지만, 친화도 분류는 method 별로 다르다 — hyperloglog 와 chao_weighted 가 가장 큰 추가 개선 (Friendly), sparse_rp 는 중간 (Indifferent), hilbert_real 은 CaseA 단독 대체에서 harmful (Hostile).

3-axis 분류 매트릭스:

| Method | K granularity sensitivity | Multi-jn sensitivity | Cheap 근사 친화도 |
|---|---|---|---|
| sparse_rp | K-sensitive (U-shape) | sensitive (-3.55p) | Indifferent |
| chao_weighted | K=20 sweet | sensitive (-2.63p) | **Friendly** |
| hilbert_real | K-robust | robust | Hostile (CaseA harmful) |
| hyperloglog | K-robust | robust | **Friendly** |

본 연구는 K granularity 변화와 multi-table 재계층화 두 측정에서 method 별 민감도 패턴이 일치 (sparse_rp + chao_weighted sensitive vs hilbert_real + hyperloglog robust) 함을 확인하였다. 그러나 저비용 근사 친화도는 다른 분류 패턴 (Friendly: hyperloglog + chao_weighted) 을 보였다. 즉 method 의 내부 메커니즘이 측정 영역에 따라 다른 영향을 미친다. 3 axis 중 2 axis 일치는 본 연구의 method-level consistency 의 evidence 이지만, 1 axis 다른 분류는 method 의 메커니즘 차이가 단순 sensitivity 분류로 환원되지 않음을 시사한다.

---

## Q&A 예상 질문 대비

발표 후 Q&A 에서 나올 수 있는 질문을 미리 정리해 둔다. 답변은 모두 정직하게 한계를 인정하고 측정 결과로 답하는 톤이다.

**Q1. 왜 CaseB 산술 평균이 효과적인가? 이론적으로 어떤 근거가 있는가?**
베르누이 무작위 샘플링은 편향 (bias) 이 0 이지만 분산 (variance) 이 크다. 클러스터 기반 계층적 표집 추정량은 분포 가정이 맞을 때는 분산이 작지만, 가정이 빗나가면 편향이 생길 수 있다. 두 추정값을 산술 평균하면 한 쪽이 실패할 때 다른 쪽이 보완해 주는 안정적인 구조가 된다. 측정 결과로는 92.5% 의 cell 에서 단일 베르누이보다 더 정확하다. 다만 산술 평균이 가장 좋은 결합 방식인지는 아직 모르며, 가중치 평균이나 기하 평균과의 비교는 future work 다.

**Q2. CaseA 단독 대체의 효과는 어떻게 보아야 하는가?**
56 방법 중 약 40% 가 평균적으로는 베르누이 기준선보다 정확했다. 그러나 같은 method 라도 데이터셋과 cell 마다 효과의 편차가 컸다. 통계 검정 (BH-FDR 보정 + paired Wilcoxon p<0.05) 으로 cell 전반에서 안정적으로 베르누이를 우위로 누른 method 는 7.6% (15/197) 정도였다. 이 15 method 의 평균 개선폭은 -5 ~ -12% 인데, paper 자체 재현 시 발생하는 측정 변동 (-4.3%) 보다 1.2 ~ 3 배 큰 의미 있는 개선이다. 즉 단독 대체로도 noise floor 를 넘는 실제 개선이 가능한 method 가 일부 존재하지만, 산업 적용을 위한 안정성은 부족하다. 이 안정성 부족이 CaseB (산술 평균) 검토의 motivation 이다.

**Q3. paradigm 평균이 극단값에 의해 영향을 받는다면, 우리 결과의 정직성은 어떻게 확보되는가?**
이 점은 5월 13일 새벽에 강재현이 지적한 부분이다. 우리는 paradigm 평균과 함께 12 개의 각 paradigm 대표 방법 (anchor method) 별로 -9 ~ -10% 의 일관된 개선폭과 2 ~ 3 의 안정적 표준편차를 보여주는 method 단위 분석을 별도로 제시한다. 즉 "paradigm 우위" 보다 "anchor method 일관성" 이 우리의 진짜 결과다.

**Q4. multi-table 영역으로의 확장은 어떻게 가능한가?**
8 measurement 의 multi-join 재학습 결과로 method 마다 민감도가 다르다는 것을 확인했다. quality 의존적인 두 method (sparse_rp, chao_weighted) 에는 비싼 재학습이 -2.6 ~ -3.5%p 추가 개선을 주지만, quality 안정적인 두 method (Hilbert curve, HyperLogLog) 에는 차이가 없다. 또한 Centroid tuple cheap 근사가 비싼 재학습보다 산술 평균 모드에서 더 좋은 결과를 주기 때문에 (4 method 모두 평균 -0.84%p 추가 개선), 학습 비용 추가 없이 multi-table 영역으로 확장 가능하다.

**Q5. paper 의 결과 (mean qe_trim 1.69) 와 우리 측정값 (1.618) 의 차이는?**
-4.3% 차이는 측정 변동 (measurement variance) 범위 내다. paper 가 100 query × 5 trial 의 절사 평균 (trim mean, top/bottom 10% 제거) 으로 보고하는데, seed 와 query 집합이 다르면 이 정도 변동은 일반적이다. 같은 hyperparameter (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, N=385) 와 같은 query 정의 (TPC-H Q3·Q10·Q12 + selectivity 구간) 를 사용했고, JSON 산출물 전수 검사에서 0 parse failure 가 확인된다.

**Q6. 산업에 어떻게 적용 가능한가?**
두 가지 방향이 있다. (1) PostgreSQL pgvector 의 default sampling 메커니즘에 우리 stratified estimator 를 산술 평균으로 추가하면 옵티마이저 카디널리티 추정의 안정성이 향상된다. (2) Exqutor 의 §V-B 모듈에 산술 평균 결합 + cheap 근사 + method-aware 의 세 원칙 조합을 통합하면 paper 본문 성과 (1만 배 속도 개선) 위에 추가 정확도 layer 를 얹을 수 있다. 다만 실제 production workload 에서의 정확도 vs 자원 절충 측정은 future work 다.

**Q7. 폐기된 method 가 23 + 9 + 6 = 38 개나 되는데, 본 연구의 결과 신뢰도는 어떻게 보아야 하는가?**
폐기 사유가 측정 과정에서 명확하게 드러나는 사유다. 자원 한계 (birch 의 메모리 50-200GB 폭증, agglomerative 의 OOM, kde_parzen 의 4 시간 timeout) 는 측정 서버의 물리적 제약, 알고리즘 정독 검토에서 발견된 reference 위반 (kdtree 의 단순 hash, vinecopula 의 PCA1D 별칭, neuram = PCA1D 100% 동일) 은 학술 정직성 위반, 정합성 위반 9 종 (halton, sobol 등) 은 큰 데이터셋에서 +145,483% 같은 외곽 값이 나오는 안정성 문제다. 폐기를 명시적으로 보고서에 분류한 것이 본 연구의 정직성 axis 다.

---

## 마치며

이 발표 시나리오는 4월 28일 중간 보고서를 기준점으로 잡고, 5월 한 달의 RQ3 측정과 추가 분석을 7 단계 순차 흐름 (문제 정의 → 분포 인지 방법 56 탐색과 폐기 분류 → 단독 대체 가능성 → 결합 framework → 자원 효율 → 권장 design → 마무리) 으로 발표 자리에서 풀어 가는 정리다. 발표 시간이 약 15분이라는 점을 고려해서 도입과 RQ1·RQ2 에 3분, 분포 인지 방법 탐색에 2.5분, 단독 대체 가능성에 2분, 결합 framework 에 2분, 자원 효율에 2분, 권장 design 에 1.5분, 마무리와 Q&A 에 2분 정도를 배분했다.

다음 단계는 이 흐름대로 슬라이드 20 장을 정리하고, 5월 28일 임채림 박사님 미팅 전에 한 차례 리허설을 진행하는 것이다. 슬라이드 시안은 keynote v4 (5월 12일 작성) 가 있고, v5 정정 사항 (RQ1 narrative 재배치 + 7 단계 순차 흐름 + method 분류 부록 분리) 을 반영해서 v6 로 최종 정리한다.

작성: 2026-05-13 KST
