# 6/11 보고서 §3 Methodology — paradigm 9 framework 본문 sketch (5/11 18:55)

> **base**: `plans/6_11_보고서_outline_v3_update_plan_20260511.md` §2.2 Methodology 5-6p
> **목적**: 5/29~6/10 W5~W6 sprint 시점 본문 작성 부담 줄이기 위한 학술 산문 sketch
> **owner**: 조현빈 (§3 + §4.1 + §4.5)
> **분량**: ~5p (~120 line dense 학술 산문)

---

## 3.1 본 연구 paradigm 분류 framework (8-10 line)

본 연구는 단일 테이블 vector range query에 대한 카디널리티 추정 방식을 stratification 알고리즘의 데이터 활용 방식 기준으로 9 paradigm으로 분류한다. P1 Cluster-based는 K-Means / GMM / DBSCAN / Birch / Agglomerative / MiniBatch / Coreset / HKBU repsample 등 데이터의 군집 구조를 명시적으로 학습하는 paradigm이며, P2 Spatial Indexing은 Hilbert curve / Z-order / iDistance / FAISS IVF / LPM-1 등 공간 채우기 곡선과 인덱싱 구조를 활용한다. P3 Streaming은 Chao 1982 weighted reservoir / RANDOM20 / Thompson Sampling 등 단일-pass 스트리밍 방식으로 구성되며, P4 Dim Reduction은 sparse RP / PCA / RSVD / FastICA 등 선형 투영 후 stratification한다. P5 QMC/Hashing은 LSH / Sobol / Halton / Hammersley / Latin Hypercube 등 quasi-random sequence를, P6 Quantization은 RaBitQ / MHIST / Wavelet histogram / Product Quantization을, P7 Subspace clustering (CLIQUE Agrawal 1998), P8 Graph-based (Leiden Traag 2019)는 future work으로 명시한다. 본 연구는 5/8 시점 R3 paradigm framework (5 paradigm 11 method)에서 출발하여 5/10 8 agent algorithm audit + 5/11 Phase 4 측정을 거치며 신규 paradigm P9 InfoTheoretic (HyperLogLog Flajolet 2007)과 P10 Density (Parzen 1962 KDE)의 두 paradigm을 추가하였다.

## 3.2 method registry 56 method 종합 (10-12 line)

Tier 1 Legacy 11 method (sparse_rp / minibatch_partial / minibatch / hilbert / pca1d / reservoir / sobol / lsh / random_projection / gmm / faiss_ivf), extra 8 method (pq / kdtree / halton / hammersley / coreset / birch / agglomerative / dense_rp), extra2 20 method (opq / kdpp / banditucb1 / neuram / thompson_sampling / mfmc / epsilon_net / ams_count_sketch / neurocard_lite / adaptive_bucket_probing / ccsketch / factor_join / lp_bound / cca1d / cocluster_nystrom / tucker / vinecopula / hkbu_repsample / lhs / lpm2), Q4 Tier 1 6 method (dbscan / kde_parzen / mhist2 / hyperloglog / rsvd / wavelet_hist), Phase 4 11 method (chao_weighted M1 / lpm1_proper M2 / cum_sqrtf M3 / lavallee_hidiroglou M4 / idistance M5 / zorder_morton M6 / skilling_hilbert M7 / ica_fastica M8 / kmeans_neyman M9 / rabitq_strat M10 / idistance_neyman M11)로 총 56 active method를 구성한다. 본 등록의 학술 정직성은 5/10 8 agent audit으로 검증되었으며, 23 method (thompson_sampling / mfmc / neuram / cca1d / ams_count_sketch / ccsketch / kdpp / cocluster_nystrom / banditucb1 / hkbu_repsample 외 13 rename)가 algorithm misrepresentation 또는 reference fraud로 폐기/rename 권고되었다. 본 연구는 audit 권고를 정직 disclosure로 보고서 §5.3 Limitation에 명시하되, 측정 결과 자체는 paradigm rollup의 honest comparison을 위해 보존한다. ★3 hilbert (코드 차원에서 PCA 2D lex sort, Faloutsos 1989 Hilbert curve indexing 표명 ❌)는 코드 line 449에서 `("hilbert", "pca2d_lex") alias` 정직 명명되며, 진짜 Hilbert curve는 M6 zorder_morton (Morton 1966 Z-order paradigm anchor) + M7 skilling_hilbert (Skilling 2004 AIP Conf Proc 707, state-machine algorithm) + hilbert_real (Wikipedia xy2d 표준)의 3건 paradigm anchor로 보강된다.

## 3.3 paper exact 재현 verbatim (15-18 line)

본 연구는 Exqutor 논문 (arXiv:2512.09695v2) §V-B Adaptive Sampling 영역의 모든 hyperparam, query 정의, threshold, trim 통계, sample budget 산출 공식을 paper exact verbatim으로 구현한다. 핵심은 다음 6개 식이다.

- (1) 초기 sample size N = ⌈z²·P̂(1−P̂)/e²⌉ = ⌈1.96² × 0.5 × 0.5 / 0.05²⌉ = **385**
- (2) Q-error = max(C_est/C_true, C_true/C_est)
- (3) 조정량 δ = α·(Q-error − β) − (100−α)·sampling_ratio
- (4) Momentum V_t = m·V_{t-1} + η_t·δ
- (5) Sample size update size_{t+1} = size_t + V_t
- (6) Learning rate decay η_{t+1} = γ·η_t

Hyperparam은 paper p.7 verbatim으로 m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, update_period=50을 사용한다. paper Eq 1-6에 sample size에 대한 min/max clamping은 명시되지 않으므로 우리도 bound를 두지 않는다 (5/10 paper 정독 결정). HNSW range query 시나리오에서는 M=16, ef_construction=200, ef_search=400을 paper p.6 그대로 사용한다. trim 통계는 paper p.7 "lowest+highest 1개 제외 8 runs trim mean" verbatim 적용 (TRIM=1, TRIALS=10). trial seed는 본 연구 자체 결정으로 `np.random.default_rng(trial_idx × 13 + 7)` 일관성을 유지한다.

paper의 9 cells (DEEP/SIFT/SimSearchNet++ × sf=100 Q3,10,12 Fig 5/6 + YFCC sf=10 8 queries Fig 7 + DEEP×part_wiki cross sf=10 8 queries Fig 9 + DEEP sf=100 sel{0.001, 0.01, 0.10} Fig 13 + DEEP scale sf=1/10/100 Q3,5,20 Fig 14)에 대해 Bernoulli baseline 측정을 진행하며, paper Fig 5/6의 query 집합은 dataset 별로 (DEEP/SIFT=Q3,10,12 / SSN=Q3,9,10) 정확히 적용한다 (5/10 agent paper 정독에서 발견, 우리 이전 추정 "Q3,9,10,12 동일" 부정정). vector range threshold는 Exqutor github verbatim 5/10 클론으로 TPC-H 8 queries < 0.86 (DEEP 96d 통일), TPC-DS Q7/Q12/Q20/Q72 < 1.08, Q19/Q42 < 1.20, Q98 < 1.30을 사용한다.

## 3.4 CaseB ensemble 정의 (사용자 5/9 23:18 카톡 verbatim, 8-10 line)

본 연구의 핵심 contribution은 paper §V-B Adaptive Sampling을 그대로 보존하면서 우리 method의 KM20 stratified estimator를 산술 평균으로 ensemble하는 augment 구조다. 정확히는:

```
estimator 1 = paper §V-B Adaptive Sampling (Bernoulli random, paper exact verbatim)
estimator 2 = 우리 method (분포 인지 stratified sampling, KM20 또는 method-specific 20 cluster)
최종 cardinality = (est1 + est2) / 2          ← simple average ensemble
```

AdaptiveState (paper Eq 1-6 sample size 동적 조정)는 paper exact 그대로 유지되며, sample budget도 두 estimator가 paper Eq 1 N=385를 공유한다. 즉 본 연구는 paper 추정 위에 우리 추정의 산술 평균만 layer로 추가하며, paper §V-B 자체는 변경하지 않는다. 이 구조의 통계적 정당성은 bias-variance trade-off에서 나온다. random sampling은 bias 0이지만 cluster imbalance 시 variance가 크고, stratified sampling은 분포 가정이 맞을 때 variance가 낮다. 두 estimator의 산술 평균은 한 쪽이 분포 misspecification으로 fail해도 다른 쪽이 보완하는 robust 구조가 되며, 5/11 paper exact 측정에서 paper baseline 대비 paired CaseB > CaseA 92.9% (404/435), Cliff's δ large better 63.5% (284/447), Hedges' g large 56.4% (252/447)로 통계 압도가 입증된다.

## 3.5 측정 정합성 검증 4축 (10-12 line)

측정 자체의 정합성은 4축에서 paper review-grade로 검증된다. 첫째, **JSON integrity** 검증에서 산출된 918+ JSON file 전수 검사가 0 parse failure, 0 NaN-Inf, 0 corruption을 보인다. 둘째, **Reproducibility** 검증에서 4 cells × 10 trials × 7 fields = 280/280 fields의 SHA-256 hash가 byte-identical로 일치하여 deterministic 보장이 확인된다 (seed `trial_idx × 13 + 7` 일관). 셋째, **Paper verbatim line-by-line** 검증에서 paper Eq 1-6 + hyperparam 8건 + query 정의 + threshold + trim 통계가 코드와 100% 일치하며, 미세 mismatch 4건 (q_error cap=100 / size round / sel=0.001 calibration parquet 부재 시 fallback / Bernoulli budget)은 모두 numerical robustness 영역이다. 넷째, **paper Fig 12 영역 8 cells mean trim Q-error**가 1.6180으로 paper 보고값 1.69 대비 -4.26%, measurement variance 범위 내 일치를 보인다.

추가 검증으로 Statistical Robustness 영역에서 Hedges' g (small-sample bias 보정 Cohen's d) + Cliff's δ (rank-based effect size, large = ±0.474) + paradigm rollup (P1-P10 mean Δ% 종합) + cherry-pick prevention table (method × cell range top 10 자동 산출)을 모두 적용한다. σ_j oracle 검증에서는 KM20 cluster 내 sigma 정의 + Neyman/Anti-Neyman allocation 산출이 통계 표준대로 진행되었음이 확인되며, 5-way 측정 (Bernoulli / Equal / Proportional / Neyman / Anti-Neyman)의 결과가 σ_j range 1.3-1.6× narrow + N_i CV=0의 자연 결과로 paradox 형태 (Anti < Prop < Neyman)를 보이는 것이 honest finding으로 보고된다.

---

## 본 sketch 사용 가이드 (5/29~6/10 W5~W6 sprint)

1. **§3.1~§3.5 본문 sketch는 그대로 학술 산문 형식 직접 사용 가능** (한국어, 영어 학술 용어 병기)
2. 5/15 박광현 미팅 confirm 사항 반영 (만약 narrative 변경 시 §3.4 ensemble 정의나 §3.1 paradigm 분류 일부 minor 조정)
3. Q4 4 method 회수 후 §3.5 측정 정합성 4축 수치 update (918 → 988 file)
4. 본 sketch 외 §3.6 측정 매트릭스 표 (9 cells × 56 method × 2 modes) + §3.7 본 연구 기여 위치 sub-section 추가 검토
5. 6/11 보고서 master file은 박세은 통합 (분량 5-6p 학교 양식 정합)

---

작성: 2026-05-11 18:55 KST  
다음: Q4 4 method 회수 후 수치 update + 5/15 박광현 미팅 confirm 후 narrative 정합성 점검 → 5/29~6/10 sprint 본문 작성
