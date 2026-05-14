# Multi-cell Stratification 학습 방식 간접 비교 (5/13 12:00)

> **분석 시점**: 2026-05-13 12:00 KST  
> **데이터**: paper_exact/ 기존 1001 file 안 A2-Fig7 / A2-Fig9 multi-table cell  
> **목적**: 강재현 5/13 1:00 의도 "multi-join 후 stratification 학습" 효과의 간접 정량화  
> **방법**: 기존 측정 안 KM-based learning 을 자체 수행하는 method (minibatch / agglomerative 등) 와 KM20 carry-over 방식 anchor (sparse_rp / hilbert_real 등) 결과 비교

---

## 0. 배경 — 진정한 multi-join re-stratification 측정 한계

5/13 0:20 강재현이 제기한 "벡터 테이블 multi-join 한 이후에 stratification 학습해서 하는 것" 측정은 PG 16 server binary 부재로 새 framework launch 가 보류된 상태다 (5/13 11:47 박세은이 임채림 박사에게 메일 발송, 채림님 응답 wait). 본 분석은 그 사이 기존 측정 1001 file 안에서 multi-table cell 의 stratification 학습 방식 차이를 간접 정량화한 결과다.

---

## 1. 두 가지 학습 방식의 분류

multi-table cell (A2-Fig7 / A2-Fig9) 의 stratification 학습 방식을 본 측정 framework 안에서 두 가지로 분류할 수 있다.

**carry-over (현행 방식)**: A2-Fig9 cell 의 partsupp_deep_10 테이블이 가진 stratum_id column 을 그대로 사용. 이 stratum_id 는 별도 시점에 partsupp_deep 의 vector 분포로 학습된 KM20 cluster 라벨이며, sparse_rp / hilbert_real / hyperloglog / chao_weighted 같은 anchor method 들이 이 stratum_id 위에서 작동한다.

**자체 K-means 학습**: minibatch / minibatch_partial / kmeans_neyman / gmm / agglomerative / faiss_ivf 같은 method 들은 fetch 된 partsupp_deep_10 vector 자체에 자기 K-means (또는 GMM/agglomerative) 학습을 수행하여 stratum 을 새로 만든다. 즉 carry-over 가 아니라 cell 별 vector 분포로 자체 학습하는 방식이다.

두 학습 방식의 결과 차이는 강재현 1번 의도와 직접 관련된다 — 비록 두 테이블을 join 한 후의 진정한 re-stratification 은 아니지만, "single table 의 KM20 cluster 를 multi-table cell 에 적용 vs cell 의 vector 분포로 자체 학습" 의 비교 evidence 가 된다.

---

## 2. 측정 결과 비교

| Method | A2-Fig7 Δ% | A2-Fig9 Δ% | 학습 방식 |
|---|---:|---:|---|
| **minibatch** | **-8.30** | **-7.25** | 자체 K-means |
| minibatch_partial | -6.83 | -4.48 | 자체 K-means (partial) |
| mhist2 | -10.29 | +0.50 | 자체 hist 학습 |
| agglomerative | -1.23 | -0.89 | 자체 hierarchical 학습 |
| faiss_ivf | -3.73 | +1.21 | 자체 IVF index 학습 |
| kmeans_neyman | +1.94 | +3.17 | 자체 K-means + Neyman alloc |
| gmm | +10.96 | +1.88 | 자체 GMM 학습 |
| cocluster_nystrom | +24.20 | +17.36 | 자체 co-clustering |
| | | | |
| **sparse_rp** (anchor) | -10.46 | -6.58 | KM20 carry-over |
| **hilbert_real** (anchor) | -11.52 | -6.07 | KM20 carry-over |
| **chao_weighted** (anchor) | -11.77 | -6.00 | KM20 carry-over |
| **hyperloglog** (anchor) | -8.77 | -5.15 | KM20 carry-over |

---

## 3. 핵심 finding — 학습 방식보다 method 자체 특성이 결정적

minibatch (자체 K-means 학습) 가 multi cell 에서 -8.30 / -7.25 퍼센트 효과를 보이며, 이는 KM20 carry-over 방식의 anchor method 들 (sparse_rp -10.46/-6.58, hilbert_real -11.52/-6.07, chao_weighted -11.77/-6.00, hyperloglog -8.77/-5.15) 과 동등 수준이다. 즉 stratification 학습 방식의 차이가 multi cell 의 결과 차이를 결정짓지 않는다. 자체 K-means 학습 (minibatch) 도, carry-over (anchor) 도 모두 multi cell 에서 -6~-12 퍼센트 범위의 robust 한 개선 효과를 보인다.

반면 학습 방식이 같은 자체 K-means 인데 kmeans_neyman (+1.94/+3.17) 과 gmm (+10.96/+1.88) 은 효과가 약하거나 악화된다. 또 cocluster_nystrom 은 +24.20/+17.36 의 극단 outlier 다. 즉 **학습 방식 (carry-over vs 자체 학습) 보다는 method 자체의 통계 특성 (sampling allocation 방식, weighting 함수 등)** 이 multi cell 의 효과를 결정짓는다.

이 finding 은 강재현 1번 가설에 대한 간접 답변이다. "두 테이블 join 후 새 stratification 학습" 의 효과를 본 framework 한계 안에서 직접 측정하지는 못했지만, 자체 K-means 학습 (minibatch) 결과가 carry-over (anchor) 와 동등 수준이라는 점에서 "multi cell 의 cardinality 추정에 stratification 학습 방식 자체의 영향은 제한적" 이라는 narrative 가 가능하다.

---

## 4. 진정한 multi-join re-stratification 측정 plan (PG 시작 후)

진정한 multi-join re-stratification — 두 테이블 (partsupp_deep_10 + part_wiki_10) 을 join 한 후 join 결과 row 의 vector 분포로 KM20 학습 — 은 PG 16 instance 시작 후 framework 작성 + 측정 plan 이다. 본 측정이 완료되면 다음 비교가 가능해진다.

| 비교 axis | 학습 방식 | 측정 status |
|---|---|---|
| anchor method on KM20 carry-over | partsupp_deep_100 의 KM20 cluster 적용 | ✅ 측정 완료 (paper_exact/) |
| minibatch on 자체 학습 | partsupp_deep_10 vector 자체 K-means 학습 | ✅ 측정 완료 (paper_exact/) |
| anchor method on multi-join re-stratification | partsupp_deep_10 + part_wiki_10 join 결과 vector 자체 KM20 학습 | ⏳ PG 시작 후 |
| anchor method on cluster K 변화 (km10/km30) | KM20 carry-over with K=10 / K=30 | ✅ 측정 완료 (km10/km30 dir) |

진정한 multi-join re-stratification 결과가 carry-over 와 큰 차이가 있으면 강재현 가설이 정량 입증되고, 큰 차이가 없으면 본 간접 분석의 narrative 가 확정된다.

---

## 5. v5 deck 정정 plan 추가

본 간접 비교 결과를 v5 deck Limitation slide 또는 신규 sub-slide 에 추가 가능하다.

```
Multi-table cell stratification 학습 방식 비교
(현행 framework 한계 안 간접 비교, 진정한 multi-join re-stratification 은 향후 측정 영역):

carry-over (anchor):     sparse_rp -10.46/-6.58, hilbert_real -11.52/-6.07
자체 K-means (minibatch): -8.30 / -7.25

→ 학습 방식의 차이가 multi cell 의 효과를 결정짓지 않음 (둘 다 -6~-12% 범위).
→ multi-join 환경에서도 method 자체 특성이 stratification 학습 방식보다 더 결정적.
```

---

작성: 2026-05-13 12:05 KST · 강재현 1:00 의도 간접 정량 + PG 시작 후 진정한 multi-join re-stratification 측정 plan
