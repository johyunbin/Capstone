# Ensemble (4강 + 7 base) × Adaptive overlay — Mathematical Validity Audit

**작성**: 2026-05-08 KST | **대상**: `cache/rq3/run_ensemble_4kang_adaptive.py` (server v2, 581 lines, 11-method dispatch)

## 1. 11 method × ensemble 호환성 표

| Base method | Output K | Cluster size profile | Empty strata 가능성 | Determinism (fixed seed) | 호환 여부 |
|---|---|---|---|---|---|
| HDBSCAN | =20 (centroid + KMeans 보충) | imbalance (DEEP-SF1 cmin=18,380 / cmax=65,655) | ✗ (centroid+kmeans 로 -1 없이 K=20 보장) | ✓ | OK |
| MB_partial | =20 | imbalance 중간 (cmin/cmax ≈ 1:3) | ✗ | ✓ (random_state 고정) | OK |
| Hilbert | =20 (PCA→1D quantile bin) | 거의 균등 (cmin≈cmax) | ✗ | ✓ | OK |
| sparse_rp | =20 (1D projection + quantile) | 거의 균등 | ✗ | ✓ | OK |
| MiniBatch (KMeans) | =20 | KMeans 와 유사 imbalance | ✗ (n_clusters=20 강제) | ✓ | OK |
| GMM | =20 (predict argmax) | covariance_type='diag' → 안정 | ✗ (n_components=20) | ✓ (random_state 고정) | OK |
| faiss_ivf | =20 (IVF quantizer) | KMeans-like | ✗ (nlist=20, fallback MBKM) | ✓ | OK |
| Reservoir | =20 (NN to K random centroids) | random center → moderate imbalance | ✗ (NN 1-NN 보장) | ✓ | OK |
| PCA1D | =20 (1D quantile bin) | 균등 | ✗ | ✓ | OK |
| **LSH** | =20 (sign bits → mod 20) | **mod-20 collision: 8 buckets 2x density** | **이론적 ✗ but isotropy 깨지면 위험** | ✓ | ⚠️ 검증 필요 |
| Sobol | =20 (PCA→2D Sobol nearest) | low-discrepancy uniform | ✗ | ✓ (qmc Sobol seed) | OK |

## 2. Adaptive overlay logic (`run_ensemble_measurement`, 269–303)

매 query iteration:
1. `proportional_alloc_dynamic(sizes, total_budget=S_t)` — Adaptive S_t 를 N_i 비례 분배 (`s_i = round(N_i / N · S_t)`, min 1).
2. `stratified_estimate_dynamic(samples, sizes, alloc, qvec, D, rng)` — cluster 별 random sample → hits 카운트 → `est += hits × (N_i / s_i)`. **이는 정확히 표준 stratified HT estimator**, alloc 만 query 단위 동적.
3. 다음 query 의 budget = `state.step(qerr)` (V4 audit 에서 paper-식 일치 확인).

**Unbiased 보장 (Cochran 1977 §5.4)**: 각 cluster 내부 SRS without replacement 의 hits 가 unbiased 추정 → cluster sum 도 unbiased. alloc s_i 가 query 마다 변해도 each query 의 estimator 는 conditional unbiased (s_i 가 query 와 독립; query 와 무관한 prev qerror 만 의존). **단, s_i ≥ 1 보장 필요** — proportional_alloc_dynamic 의 `np.maximum(f.astype(int), 1)` 으로 충족.

## 3. 우려 항목 (3건)

**(A) LSH bucket imbalance**: ceil(log2(20))=5 hyperplanes → 32 raw buckets mod 20 → buckets 0~11 은 2 raw bucket 합집합 (≈2× density). Charikar 2002 cosine LSH 는 isotropic 가정에서 expected min ≈ N/40, max ≈ 2N/20. 실제 embedding 의 cosine isotropy 깨짐 → max/min ratio 5~10 가능. **그러나 모든 cluster ≥1 row 이면 estimator 는 여전히 unbiased** (variance 만 증가). 0-row cluster 발생 시 `sizes[sid]=0 → weight=0` → 그 cluster 자동 제외, bias 발생 X (population 도 0). 호환성 ✓.

**(B) HDBSCAN noise (-1) 처리**: `fit_hdbscan` 에서 `unique_labels = sorted(set(labels) - {-1})` → noise 제외 후 cluster 수 비교 → ≥K 면 KMeans 로 합침, <K 면 KMeans 새로 학습. 최종 `assign(vectors)` 은 **모든 vector 에 대해 nearest centroid argmin** → 결과 sids ∈ [0, 20). **-1 leakage 없음**. ✓

**(C) Sobol determinism**: `scipy.stats.qmc.Sobol(seed=...)` + PCA fit (random_state=seed) → 동일 seed/data 면 완전 결정론. learn_seed=42 고정 사용 → 모든 measurement reproducible. ✓

## 4. 종합 판정

| 항목 | 결과 |
|---|---|
| 11 method 모두 K=20 stratification 보장 | ✓ |
| stratified HT estimator unbiased | ✓ (Cochran 1977 §5.4 충족) |
| LSH bucket imbalance | unbiased 유지, variance 증가 — 11개 중 가장 보수적 결과 예상 |
| HDBSCAN noise label leak | ✗ (centroid+nearest assign 으로 차단) |
| Sobol seed reproducibility | ✓ |

**결론**: 11-method ensemble 결과는 **paper-valid**. 모든 base method 가 K=20 hard partition 을 출력하고, Adaptive overlay 의 동적 alloc 은 conditional-unbiased stratified HT 를 매 query 산출. 우려 LSH 는 unbiased 는 유지하나 variance 가 큼 → ensemble 11종 중 LSH 가 baseline 대비 약한 성능 보일 가능성 — 이는 narrative 에 "stratification quality matters" 보강 근거로 활용 가능.
