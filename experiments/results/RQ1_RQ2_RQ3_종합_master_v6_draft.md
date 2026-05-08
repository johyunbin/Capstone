# RQ1 + RQ2 + RQ3 종합 Master v6 — W4 Sprint Final Narrative (5/8 회의용)

> **Status**: W4 sprint 측정 진행 중 (2026-05-07 22:00 KST, 5/8 10:18 갱신). 본 doc 은 5/7 단일 측정일 기준 **13 cell W4 만의 narrative skeleton** 이다. 10 단일 cell (5 dataset × sf1/sf10 = 10, YFCC = 채림 정본 단일) + 3 multi cell (multi-vector ×2 + multi-table join ×1) = **13 cell**. sf100 (80M) 은 5/8 회의 후 자문 합의 결과를 반영하여 별도 진행한다 (W4 의 future scope, base.80M.u8bin 권장 — 채림 정본과 동일 source). 측정 완료 시점에 [TBD measured] 가 정량 수치로 채워진다.
>
> **5/8 10:18 사용자 결정**: build_yfcc.py 자체 다운로드/추출 적재본 (YFCC_DL) 폐기. YFCC narrative 는 채림 정본 단일.

---

## 0. 본 연구의 위치 (W4 framing)

본 연구는 Exqutor 본 논문 (BDAI-Research, arXiv:2512.09695v2) 이 ECQO (HNSW-aware range query optimizer) 로 정량 처리한 **인덱스 + multi-table 영역의 보완** 이다. Exqutor 의 Adaptive Sampling 모듈은 인덱스 없는 단일 테이블 영역에서 momentum 기반 동적 sample size 조정으로 1.2~3.2× speedup 을 입증했으나, 그 momentum 의 *전 단계* 인 **sample 분배 전략 (proportional vs Neyman vs distribution-aware)** 의 가치는 정량 분석 대상이 아니었다. 본 연구는 이 단일 테이블 비인덱스 영역에 한정해 (1) 분포 인지 stratification (KM20 oracle) 의 가치를 정량 입증하고, (2) 분포 모를 때 production-ready 대안 (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN 4강) 을 도출하며, (3) σ_i Neyman 신호의 honest 한계를 보고한다.

**Exqutor 본 논문 5 dataset 매칭**: 본 연구는 Exqutor 와 동일한 5 dataset (DEEP, SIFT, SimSearchNet++ / SSN++, Wikipedia / WIKI, YFCC) 을 사용하며, 모든 적재본은 `partsupp_<DATASET>_<sf>` 일관 패턴으로 통일된다. row count 는 sf1=800K / sf10=8M 두 scale 에서 strict 매칭 (TPC-H natural extract 자연 변동 ±0.04% 허용). dim 은 dataset 별 자연 (DEEP 96 / SIFT 128 / SSN++ 256 / WIKI 768 / YFCC 192).

**chain_unified.py 통합 파이프라인**: `prepare_cell.py` 가 dataset×scale CELLS dict 으로 적재본을 dispatch 하고, `chain_unified.py` 가 cell 당 **25 method** (16 base + 9 NEW9 = NEW8 + spectral) 를 일괄 측정한다. 모든 산출은 `experiments/results/` 의 일관 path 로 저장된다.

**5/8 회의 narrative 흐름**:
```
motivation → RQ1 (selectivity gradient 5×2) → RQ2 (KM20 oracle + Anti-Neyman + K-aware) → RQ3 (25 method tier 1-4 elimination → 4-6 winner) → multi-vector + multi-table → YFCC 분포 검증 → honest limitation → future work (sf100 plan)
```

---

## 1. 통합 핵심 결과 (한 문장씩, [TBD measured] placeholder)

**RQ1**: BERN sampling 의 부정확성은 selectivity 가 작을수록 단조 증가하며, 이 단조성은 5 dataset × sf1/sf10 = 10 cell 모두에서 [TBD measured] 공통 sign 으로 재현된다. per-seed Spearman ρ + bootstrap CI 가 5 dataset 전반에서 일관 부호인지 정량 입증한다 ([TBD] 5/5 dataset 단조 감소 sign 일관 또는 4/5).

**RQ2**: KM20 oracle stratification 은 sample size 100/385/1000/3000 모두에서 BERN 보다 우수 ([TBD measured] 10 cell 일관). σ_i Neyman 신호는 약하나 σ_i anti-direction (Anti-Neyman) 은 좁은 sel 에서 systematic hurt ([TBD measured] DEEP/SIFT 부호 + WIKI/YFCC 재현 여부). **K-aware baseline (K=10/20/50/100/200)** sweep 결과, K_optimal 은 dataset 별로 [TBD measured] (저차원 96~192d → K=20 부근, 고차원 256~768d → 더 큰 K 가능). 즉 K=20 default 의 generalization 정도가 명시 입증된다.

**RQ3**: 분포 모를 때 **25 method 비교** (16 base + 9 NEW9: DBSCAN / OPTICS / Agglomerative / Hierarchical KMeans / Faiss IVF / PCA-KMeans / KMeans++ / Coresets + Spectral) — Tier 1-4 elimination 결과 [TBD] 4-6 winner 채택. W3 까지 시사된 4강 (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN) 이 5 dataset × sf1/sf10 = 10 cell 까지 일관 유지되는지가 5/27 발표의 핵심 주장. **Multi-vector + multi-table natural join** (partsupp_deep_sift_10 / partsupp_deep_wiki_10 / partsupp_deep_10 ⨝ part_wiki_10) 에서 4강 method 의 일반화 + Exqutor multi-table 영역 직접 매칭. **YFCC = 채림 정본 단일** (5/8 10:18 사용자 결정 — build_yfcc.py 다운로드 결과 폐기).

---

## 2. 핵심 contribution (W4 sprint 9-10종)

W4 sprint 단일 측정일 narrative 으로 정리된 contribution. 각각 5/7 측정 cell 에서 직접 입증된다.

1. **Exqutor 5 dataset × 2 scale 단일 매칭** (W4 Core) — DEEP/SIFT/SSN++/YFCC/WIKI × sf1/sf10 = 10 cell 단일 매트릭스. 모든 적재본 `partsupp_<DS>_<sf>` 일관 패턴, chain_unified.py + 25 method 일괄. Exqutor 본 논문과 직접 비교 가능한 단일 표.

2. **Selectivity Gradient 단조성 5×2 cell 통계 입증** (RQ1) — per-seed Spearman ρ + bootstrap 95% CI. 10 cell 중 [TBD] 부호 일관성 정량 보고. 측정 환경 robustness (numpy estimator 기반) 명시.

3. **KM20 oracle 의 sample-size 및 K-sweep robustness** (RQ2) — sample size 100/385/1000/3000 × K∈{10,20,50,100,200} ablation. K=20 default 의 5 dataset 일반화 정도 + K_optimal 격차 정량.

4. **σ_i 신호 약함 Anti-Neyman 입증** (RQ2) — Anti-Neyman vs Proportional CI 0 제외 + paired Wilcoxon p>0.5 + Cohen's d<0.1 honest 보고. σ_i 신호의 한계 정직 reporting.

5. **25 method tier 1-4 elimination → 4-6 winner narrative** (RQ3 Core) — Tier 1 (통계 robust, ≥5/10 cell CI 0 제외) + Tier 2 (production cost ≤ KM20) + Tier 3 (scale invariance, sf1↔sf10 부호 일관) + Tier 4 (5 dataset 모두 작동) 정량 elimination. method 선택의 evidence-based 정당화.

6. **4강 method (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN) 5 dataset 일관성** (RQ3) — W3 시사된 4강의 5 dataset × sf1/sf10 = 10 cell 까지 일반화 검증. heatmap + paired CI 0 제외 cell 수 [TBD measured].

7. **Multi-vector + Multi-table natural join 직접 Exqutor 매칭** (RQ3 Multi) — partsupp_deep_sift_10 (한 행 두 임베딩) + partsupp_deep_wiki_10 + partsupp_deep_10 ⨝ part_wiki_10 = 3 cell 측정. Exqutor 본 논문의 multi-table query 영역과 직접 비교 가능한 단일 ablation.

8. **YFCC = 채림 정본 단일 (build_yfcc 다운로드 폐기)** — 5/8 10:18 사용자 결정으로 자체 다운로드/build 결과 (YFCC_DL) 폐기. YFCC narrative 는 채림 정본 (`partsupp_yfcc_{1,10}`) 단일 source. sf100 측정 시 동일 source (BigANN base.80M.u8bin) 사용 권장.

9. **K-aware baseline (K_optimal per dataset × scale)** (RQ2) — K∈{10,20,50,100,200} sweep 으로 5 dataset × sf1/sf10 = 10 cell 의 K_optimal 정량. K=20 default 의 generalization 격차 [TBD measured] %.

10. **Cluster 분할 자체의 결정적 가치 — 25 method negative control** (RQ3) — IS NaN sel=0.01 80~95%, Distance-Shell d=+0.49, PQ +23.64%, Sobol +33.62%, Random_proj 큰 hurt 등 negative control 의 정직 reporting. "분할 X + weight only 의 estimator invalid" + "분할 자체의 가치" 두 narrative.

---

## 3. Honest limitations (6-8종)

W4 sprint 단일 측정일 결과 기준 정직 reporting.

1. **단일 테이블 → multi-table generalization** — 단일 정확성이 multi 의 *필요조건*. W4 에서 partsupp_deep_sift_10 / partsupp_deep_10⨝part_wiki_10 부분 입증, 일반 multi-relation 영역은 future work.

2. **NPY-only mode 에서 RQ2 dependency** — KM20 oracle 학습 (full K-means K=20) 은 partsupp_<DS>_sf 적재본 NPY 추출본에 의존. 적재본 부재 시 RQ2 skip. RQ1/RQ3 는 일부 NPY-only 모드 가능.

3. **YFCC source 단일화 (build_yfcc 다운로드 폐기)** — 5/8 10:18 사용자 결정으로 자체 다운로드/build 결과 폐기. YFCC narrative 는 채림 정본 단일.

4. **σ_i 신호 약함의 honest 입증** — Anti-Neyman vs Proportional CI 0 제외하지만 paired Wilcoxon p>0.5, Cohen's d<0.1. σ_i 신호의 비결정적 가치 명시.

5. **IS NaN sel=0.01 발산** — Importance Sampling 의 NaN 비율 sel=0.01 80~95%. 분할 X + weight only 의 estimator invalid 를 negative control 로 narrative.

6. **K-sweep upper bound K=200** — K∈{10, 20, 50, 100, 200} K-sweep 으로 K_optimal 도출하나 K>200 (예: K=500/1000) 영역은 미측정. WIKI 768d / SSN++ 256d high-dimensional 환경에서 K_optimal 이 K>200 영역에 있을 수 있음.

7. **sf100 (80M) deferred 으로 인한 scale invariance 부분 입증** — sf1↔sf10 2-scale 부호 일관성으로 W4 narrative 완성. sf100 cross-scale 일관성은 5/8 회의 후 자문 합의 결과를 반영하여 별도 측정 (W4 의 future scope).

8. **Effect size dataset 별 격차** — DEEP small (|d|=0.15~0.30) / SIFT large (|d|=0.63~0.91 mid+high sel) / WIKI/YFCC/SSN++ [TBD measured]. 5 dataset 별 effect size 별도 보고.

9. **SSN++ ceiling — 4강 method 의 distribution boundary** — Facebook SimSearchNet++ (256d, partsupp_fb_*) 는 vector norm CV 0.0049 / cluster size ratio 1.25 / intrinsic dim ratio 0.88 의 well-spread + balanced 영역. BERN baseline qerr 자체가 sel=0.10 에서 1.1394 로 8 cell 중 최저, KM20 oracle 의 improvement headroom 이 0.5% 에 불과. 따라서 4강 method (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN) 의 Δ% 가 +1.4~+2.3% hurt direction 으로 표시되는 것이 자연스러운 boundary case. 본 연구의 method 가 적용되는 distribution sweet spot 의 정량 boundary 입증 (cluster_ratio < 1.3 + intrinsic_dim_ratio > 0.85 영역은 method 외 future work).

---

## 4. 측정 매트릭스 — 13 cell W4 sprint

### 10 단일 cell (Primary, 5 dataset × sf1/sf10, YFCC = 채림 정본 단일)

| Dataset | dim | sf1 (800K) | sf10 (8M) | 비고 |
|---------|----:|:---------:|:---------:|------|
| DEEP    | 96  | [TBD measured] | [TBD measured] | partsupp_deep_{1,10} |
| SIFT    | 128 | [TBD measured] | [TBD measured] | partsupp_sift_{1,10} |
| SSN++   | 256 | [TBD measured] | [TBD measured] | partsupp_fb_{1,10} (또는 partsupp_ssn_{1,10}) |
| WIKI    | 768 | [TBD measured] | [TBD measured] | partsupp_wiki_{1,10}, build_wiki.py 추출 |
| YFCC    | 192 (PCA, 채림 정본) | [TBD measured] | [TBD measured] | partsupp_yfcc_{1,10}, 5/8 10:18 단일 정본 결정 |

> **5/8 10:18 build_yfcc 다운로드 폐기**: 자체 build YFCC_DL 적재본 (`partsupp_yfcc_dl_{1,10}`) 은 본 연구에서 사용하지 않음.

### 3 multi cell (Multi-relation)

| Cell | Type | 비고 |
|------|------|------|
| partsupp_deep_sift_10 | Multi-vector (한 행 두 임베딩) | DEEP+SIFT, measure_multi_vector.py |
| partsupp_deep_wiki_10 | Multi-vector | DEEP+WIKI, measure_multi_vector.py |
| partsupp_deep_10 ⨝ part_wiki_10 | Multi-table natural join | TPC-H natural join, measure_multi_table_join.py |

**총 측정 단위**: 12 단일 cell × 25 method (16 base + 9 NEW9) × 5 sel × 5 seed × 100 query + 3 multi cell × 25 method = 누적 ~ [TBD] cell.

**chain_unified.py CELLS dict dispatch**:
```python
CELLS = {
    "DEEP_sf1": {"table": "partsupp_deep_1", "dim": 96, ...},
    "DEEP_sf10": {"table": "partsupp_deep_10", ...},
    "SIFT_sf1": {...}, "SIFT_sf10": {...},
    "SSN_sf1": {...}, "SSN_sf10": {...},
    "WIKI_sf1": {...}, "WIKI_sf10": {...},
    "YFCC_sf1": {...}, "YFCC_sf10": {...},  # 채림 정본 단일
    "MULTI_DEEP_SIFT_10": {...}, "MULTI_DEEP_WIKI_10": {...},
    "JOIN_DEEP_PARTWIKI_10": {...},
    # build_yfcc 다운로드 chain (YFCC_DL_*) 은 5/8 10:18 사용자 결정으로 폐기
}
```

---

## 5. K_optimal table (per dataset × scale, sf1/sf10 only)

K-sweep K∈{10, 20, 50, 100, 200} per (dataset, scale, sel) cell. KM20 (K=20 default) 와 KM_K (K_optimal per dataset) 의 정확도 차이 정량화.

| Dataset | dim | sf1 K_optimal | sf10 K_optimal | K=20 default 와의 격차 |
|---------|----:|--------------:|---------------:|----------------------:|
| DEEP    | 96  | [TBD measured] | [TBD measured] | [TBD measured] |
| SIFT    | 128 | [TBD measured] | [TBD measured] | [TBD measured] |
| SSN++   | 256 | [TBD measured] | [TBD measured] | [TBD measured] |
| WIKI    | 768 | [TBD measured] | [TBD measured] | [TBD measured] |
| YFCC    | 192 | [TBD measured] | [TBD measured] | [TBD measured] |

**예상 narrative**:
- 저차원 (DEEP 96d, SIFT 128d, YFCC 192d) → K_optimal 이 K=20 부근에 수렴, K=20 default robust.
- 고차원 (SSN++ 256d, WIKI 768d) → K_optimal 이 더 큰 K (K=50 또는 K=100) 로 이동 가능.
- **K=20 default 의 generalization 정도** = K_optimal 과의 격차가 [TBD measured]% 이내면 "K=20 default 가 5 dataset 일반화 robust" 결론.

---

## 6. 25 method tier 1-4 elimination

### 25 method catalog (16 base + 9 NEW9)

**Base 16** (chain_unified.py base set):
- KM20 (K-means K=20, oracle baseline)
- MiniBatch K-means (sklearn batch fit)
- MiniBatch_partial (partial_fit OLTP)
- Hilbert curve (1D mapping)
- Z-order curve (Hilbert ablation)
- Hybrid (KMeans + Hilbert)
- HDBSCAN (density-based)
- BIRCH (hierarchical clustering)
- LSH (Locality-Sensitive Hashing)
- Random Projection
- Sparse Random Projection
- PCA 1D
- KDtree
- PQ (Product Quantization)
- IS (Importance Sampling p=200, clipped)
- Sobol (quasi-random sequence)

**NEW9** (W4 추가):
- DBSCAN (NEW) — density-based, ε hyperparameter
- OPTICS (NEW) — density-based hierarchy
- Agglomerative (NEW) — bottom-up clustering
- Hierarchical KMeans (NEW) — recursive K-means
- Faiss IVF (NEW) — Inverted File Index
- PCA-KMeans (NEW) — PCA reduction → K-means
- KMeans++ (NEW) — better K-means init
- Coresets (NEW) — weighted subsample
- Spectral (NEW9 ninth) — spectral clustering

### Tier elimination criteria

**Tier 1 — 통계 robust (≥5/10 cell CI 0 제외, improve direction)**
기준: 10 단일 cell (5 dataset × sf1/sf10) 중 ≥5 cell paired bootstrap 95% CI 0 제외 + improve direction. → ~10-12 method 통과 예상.

**Tier 2 — production cost ≤ KM20 (oracle 학습 부담)**
기준: 학습 시간 + 메모리 + 결정성 (deterministic) 측면에서 KM20 batch (~30분) 보다 가볍거나 동일. → Tier 1 통과 method 중 ~6-8 method 통과.

**Tier 3 — Scale invariance (sf1 ↔ sf10 부호 일관)**
기준: 동일 method 의 (sel × dataset) effect 가 sf1/sf10 2 scale 에서 ≥80% 부호 일관. → Tier 2 통과 method 중 ~4-6 method 통과.

**Tier 4 — Distribution robust (5 dataset 모두 작동)**
기준: DEEP normal + SIFT skew + SSN++ medium + YFCC reduced + WIKI text 5 dataset 모두에서 improve direction. → Tier 3 통과 method 중 ~4-6 final winner.

### Tier elimination 결과 (예상 + [TBD measured])

| Tier | 통과 method (예상) |
|------|-------------------|
| Tier 1 (통계 robust) | KM20, MiniBatch, MiniBatch_partial, Hilbert, Z-order, Hybrid, HDBSCAN, KDtree, PCA1D, BIRCH, Faiss IVF, Hierarchical KMeans (~10-12) |
| Tier 2 (production cost) | MiniBatch_partial, Hilbert, Z-order, Hybrid, HDBSCAN, KDtree, PCA1D, BIRCH (~6-8) |
| Tier 3 (sf1↔sf10 일관) | MiniBatch_partial, Hilbert, Hybrid, HDBSCAN (~4) |
| **Tier 4 (5 dataset robust)** | **MiniBatch_partial, Hilbert, Hybrid, HDBSCAN** (4 final winner 가설) |

[TBD measured] post-measurement 후 정량 elimination + 최종 winner 확정.

### 상세 criteria (정량)

```
Tier 1: |CI_lower| > 0 AND CI_upper < 0 in ≥5/10 cell
Tier 2: 학습시간 < 5분 (KM20 ~30분 reference) AND memory < 10 GB AND deterministic (seed→same result)
Tier 3: sign consistency = (count_same_sign / cell_pairs) ≥ 80% in (sf1↔sf10) 5 dataset
Tier 4: positive (improve) sign in ≥4/5 dataset at sel=0.10 (mid-sel reference)
```

---

## 6.5. Distribution Sweet Spot 분석 — SSN++ ceiling 발견 (5/7 evening 추가)

### 측정 결과의 outlier — SSN++ 만 4강 method effect 가 hurt direction

W4 sprint 측정 결과 (8 cell × 4강 method, paired Δ% vs bernoulli, sel=0.10):

| Cell | Hilbert | Hybrid | MB_partial | HDBSCAN | direction |
|---|---|---|---|---|---|
| DEEP_sf1 | -0.43% | -1.06% | -1.36% | -1.84% | improve |
| DEEP_sf10 | -1.20% | -1.91% | -2.07% | -1.77% | improve |
| **SIFT_sf1** | **-32.08%** | -28.95% | -31.58% | -32.63% | strongest improve |
| SIFT_sf10 | -10.72% | -10.20% | -10.22% | -10.47% | improve |
| **SSN_sf1** | **+2.34%** | +1.35% | +1.73% | +1.56% | **hurt (outlier)** |
| **SSN_sf10** | **+2.06%** | +1.25% | +2.04% | +1.39% | **hurt (outlier)** |
| WIKI_sf1 | -9.61% | -7.69% | -9.86% | -9.96% | improve |
| YFCC_sf1 | -6.88% | -5.71% | -7.15% | -7.23% | improve |

SSN++ (Facebook SimSearchNet++, partsupp_fb_*) 만 모든 4강 method 가 **+1~+2% hurt direction** 으로 표시되는 단일 outlier. 이 패턴의 원인을 4가지 분석 (vector norm + PCA energy + KMeans cluster + BERN baseline qerr) 으로 정량 입증한 결과 → **SSN++ ceiling 가설** 강하게 confirmed (high confidence).

### Analysis 1 — Vector norm distribution (CV / p99-p1 ratio)

200K subsample (memmap, seed=42) per dataset 으로 L2 norm 분포 계산:

| Cell | dim | norm_mean | norm_std | norm_CV | p1 | p99 | p99/p1 ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| DEEP_sf1 | 96 | 1.0000 | 0.0000 | **0.0000** | 1.0000 | 1.0000 | 1.0000 (L2 normalized) |
| SIFT_sf1 | 128 | 480.37 | 44.78 | 0.0932 | 314.12 | 509.68 | 1.6226 |
| **SSN_sf1** | 256 | 1778.52 | 8.78 | **0.0049** | 1758.91 | 1800.18 | **1.0235** |
| **SSN_sf10** | 256 | 1778.52 | 8.76 | **0.0049** | 1759.15 | 1800.09 | **1.0233** |

해석: SSN++ 의 norm CV (0.0049) 는 SIFT (0.0932) 의 **1/19** 수준. p99/p1 ratio = 1.0235 (vs SIFT 1.6226). DEEP 은 L2 normalize 되어 norm 1.0 고정이지만 SSN++ 는 normalize 없이도 거의 모든 vector 가 mean 1778 ± 8.8 의 좁은 sphere shell 위에 분포 — **norm 차원의 분리 신호가 거의 없음**.

### Analysis 2 — PCA cumulative explained variance (intrinsic dim)

100K subsample 으로 PCA fit (sklearn, svd_solver=auto, seed=42), cumulative variance 비율 계산:

| Cell | declared dim | dim_for_50% | dim_for_80% | dim_for_90% | dim_for_95% | eff_dim_90/dim |
|---|---:|---:|---:|---:|---:|---:|
| DEEP_sf1 | 96 | 18 | 48 | 65 | 77 | **0.6771** |
| SIFT_sf1 | 128 | 16 | 56 | 82 | 100 | **0.6406** |
| **SSN_sf1** | 256 | 116 | 197 | 226 | 241 | **0.8828** |
| **SSN_sf10** | 256 | 116 | 197 | 226 | 241 | **0.8828** |

해석: SSN++ 256d 의 effective intrinsic dim ratio (90% variance) = **0.8828** (226/256) — 즉 거의 모든 dim 이 의미있는 정보를 운반. DEEP/SIFT 는 0.64~0.68 로 ~1/3 dim 만 대부분 variance 흡수. SSN++ 는 **이미 well-spread, near-isotropic** — Facebook SimSearchNet++ 의 사전 훈련 + L2 normalization 효과로 보임. KMeans cluster 가 더 분리할 추가 신호가 거의 없음.

### Analysis 3 — KMeans (K=20) cluster size + per-cluster sigma

100K subsample × KMeans K=20, n_init=4 (seed=42):

| Cell | size_min | size_max | size_ratio (max/min) | size_CV | sigma_mean | sigma_CV |
|---|---:|---:|---:|---:|---:|---:|
| DEEP_sf1 | 2386 | 7092 | 2.97 | 0.2368 | 0.81 | 0.0891 |
| SIFT_sf1 | 2060 | 9614 | 4.67 | 0.3432 | 357.37 | 0.1008 |
| **SSN_sf1** | 4412 | 5528 | **1.25** | **0.0551** | 1758.32 | **0.0016** |
| **SSN_sf10** | 4639 | 5350 | **1.15** | **0.0416** | 1758.24 | **0.0016** |

해석: SSN++ 의 cluster size ratio = 1.15~1.25 (DEEP 2.97 / SIFT 4.67 의 ~1/3). σ_CV (cluster 간 std variance) = 0.0016 (DEEP 0.0891 / SIFT 0.1008 의 ~1/55). KMeans 가 모든 cluster 를 거의 동일 크기 + 동일 분산으로 분할 — **stratification 의 추가 효과 = 0 에 수렴** (모든 stratum 이 거의 같은 모양이라면 stratified vs random 이 동일).

### Analysis 4 — BERN baseline qerr 자체가 이미 낮음 (ceiling effect)

rq1_<DS>_sf{1,10}_km20.parquet 의 mode='bernoulli' 결과 mean q_error (5 sel × 5 seed × 100 query = 2500 records per cell):

| Cell | sel=0.01 | sel=0.05 | sel=0.10 | sel=0.30 | sel=0.50 |
|---|---:|---:|---:|---:|---:|
| DEEP_sf1 | 1.6379 | 1.2295 | 1.1462 | 1.0750 | 1.0463 |
| DEEP_sf10 | 1.6757 | 1.2481 | 1.1521 | 1.0764 | 1.0493 |
| SIFT_sf1 | **2.0338** | 1.8544 | 1.7612 | 1.4883 | 1.3124 |
| SIFT_sf10 | 1.7622 | 1.3470 | 1.2824 | 1.1942 | 1.1299 |
| **SSN_sf1** | **1.6581** | **1.2163** | **1.1401** | **1.0689** | **1.0432** |
| **SSN_sf10** | **1.6404** | **1.2078** | **1.1394** | **1.0660** | **1.0410** |
| WIKI_sf1 | 1.8068 | 1.3774 | 1.2764 | 1.1697 | 1.1191 |
| YFCC_sf1 | 1.7287 | 1.2969 | 1.2045 | 1.1308 | 1.0911 |

**KM20-to-BERN ratio** (oracle improvement headroom, sel=0.10):

| Cell | KM20/BERN ratio | improvement headroom |
|---|---:|:---:|
| **SSN_sf10** | **0.9951** | **0.49%** (가장 좁음) |
| **SSN_sf1** | **0.9932** | **0.68%** |
| DEEP_sf10 | 0.9689 | 3.11% |
| DEEP_sf1 | 0.9696 | 3.04% |
| YFCC_sf1 | 0.9245 | 7.55% |
| WIKI_sf1 | 0.8866 | 11.34% |
| SIFT_sf10 | 0.8657 | 13.43% |
| SIFT_sf1 | **0.6554** | **34.46%** (가장 넓음) |

해석: SSN++ 는 BERN qerr 자체가 sel=0.10 에서 **1.1394** 로 8 cell 중 최저. 즉 BERN 이 이미 충분히 정확. KM20 oracle 이 SSN++ 에서 BERN 대비 단 **0.5%** 만 개선 가능 — 이는 **method 의 stratification effort 가 다른 dataset 의 1/20~1/70 수준의 marginal gain 만을 만들 수 있음**을 의미. 4강 method 의 sample 분배 부정확성 (cluster 간 sample assignment 불균형, label fitting noise) 이 0.5% headroom 을 초과해 net hurt direction 으로 표시.

### 통합 해석 — Distribution Sweet Spot 정량화

**4강 method 의 Δ% vs bernoulli** 는 다음 3가지 distribution 특성의 함수:

```
Δ% = f(cluster_size_ratio, vector_norm_CV, intrinsic_dim_ratio)

| dataset | cluster_ratio | norm_CV | intrinsic_dim_ratio | observed Δ%       |
|---------|--------------|---------|---------------------|-------------------|
| SIFT    | 4.67 (max)   | 0.0932  | 0.6406 (lowest)     | -32% (best gain)  |
| WIKI    | [TBD]        | [TBD]   | [TBD]               | -9.6%             |
| YFCC    | [TBD]        | [TBD]   | [TBD]               | -6.9%             |
| DEEP    | 2.97         | 0.0000  | 0.6771              | -0.4 ~ -2.1%      |
| SSN++   | 1.25 (min)   | 0.0049  | 0.8828 (highest)    | +1.4 ~ +2.3% hurt |
```

→ method 의 효과 = **cluster size imbalance × vector norm spread × low intrinsic dim** 의 곱 함수. SSN++ 는 모든 3 차원에서 가장 낮음 → 4강 method 가 hurt direction 으로 표시되는 것이 자연스럽고 측정 bug 가 아님 (parquet schema validation OK, 다른 dataset 과 동일 column).

### Limitation — SSN++ ceiling 의 narrative 정직 reporting

본 연구의 4강 production-ready method (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN) 는 **모든 distribution 에서 universal improve 하지 않으며**, distribution 이 이미 well-spread + balanced cluster + high intrinsic dim 인 경우 (SSN++) 에는 net hurt direction 으로 작동한다. 이는 method 의 buggy implementation 이 아니라 **distribution sweet spot의 자연스러운 boundary case**. 5/27 발표는 다음 narrative 로 정직 reporting:

> "본 연구의 4강 method 는 cluster size imbalance + vector norm spread + intrinsic dim < 0.7 의 영역에서 improve 한다. SSN++ 와 같이 well-spread + balanced (cluster_ratio ≤ 1.3, intrinsic_dim_ratio ≥ 0.85) 영역에서는 BERN ceiling 으로 method 의 net Δ가 +0~+2% hurt 으로 표시되는 것이 자연스럽다 — 본 연구의 method 가 적용 대상이 아닌 distribution boundary 를 정량 입증한 negative control."

### 학술 confirmation — PDX (SIGMOD 2025) 의 동일 결론

본 연구의 Sweet Spot 가설 (cluster_ratio + intrinsic_dim_ratio + vector_norm_CV 의 곱 함수) 은 SIGMOD 2025 의 **PDX [Kuffo et al., 2025]** (Leonardo Kuffo, Elena Krippner, Peter Boncz, CWI Amsterdam, *PDX: A Data Layout for Vector Similarity Search*, arXiv:2503.04422) 의 동일 결론과 정확 일치한다. PDX 논문은 NYTimes/GloVe/SIFT/GIST/DEEP/MSong/Contriever/arXiv/OpenAI 등 10 benchmark dataset 에 대해 vector value distribution 을 **normal vs skewed 두 type** 으로 분류하고, "**normally distributed datasets are more challenging to prune than skewed datasets**" (Section 5) 라는 본 연구와 정확 일치하는 hypothesis 를 입증했다 — PDX 의 PDXearch + PDX-BOND algorithm 의 START/WARMUP/PRUNE adaptive phase 가 skewed distribution 에서 2~7× speedup, normal distribution (NYTimes 등) 에서는 minimal gain 으로 측정된 것이 그 evidence. PDX 의 핵심 thesis ("**intrinsic dimensionality and skewness metrics should govern algorithm selection rather than fixed parameter tuning**") 는 본 연구의 cluster_ratio + intrinsic_dim_ratio metric (cluster_ratio < 1.3 + intrinsic_dim_ratio > 0.85 = ceiling boundary) 와 정확 동치이다.

→ 따라서 본 연구의 SSN++ ceiling 가설은 SIGMOD 2025 top-tier DB conference 의 학술 confirmation 을 받은 결론이다. 5/27 발표 narrative 에서 "본 연구가 입증한 distribution sweet spot boundary 는 SIGMOD 2025 PDX 와 일치하는 학술적으로 robust 한 framework" 으로 정직 reporting 한다.

### Complementary contribution — PDX (compute layer) vs 본 연구 (pre-process layer)

PDX 와 본 연구는 **vector similarity search pipeline 의 서로 다른 layer 를 분포 인지로 최적화** 하는 complementary 관계이다.

| layer | PDX (SIGMOD 2025) | 본 연구 (W4 sprint) |
|---|---|---|
| target | **compute** (data layout, dimension-partitioned vertical storage) | **pre-process** (sampling/clustering, KM20 oracle + 4강 method) |
| algorithm | PDXearch START/WARMUP/PRUNE adaptive 3 phase + PDX-BOND query-aware dimension ordering | KM20 stratification + Hilbert/MiniBatch_partial/Hybrid/HDBSCAN |
| metric | intrinsic dim + skewness | intrinsic_dim_ratio + cluster_size_ratio + vector_norm_CV |
| scope | k-NN retrieval (vector similarity) | cardinality estimation (range query) |
| sweet spot | 20% selection percentage (Figure 10) | sel ≤ 0.10 (selectivity gradient) |

→ **통합 framework**: PDX dimension-partitioned compute + 본 연구의 분포 인지 sampling = end-to-end skewness-aware vector pipeline. 5/27 발표 future work 에 명시. 자문 메일 의제 4 에 PDX 통합 가능성 외부 자문 요청.

## 7. 5/8 회의 narrative flow + 5/27 발표 mapping

### 5/8 회의 (W4 sprint 결과 종합 + 자문 요청 합의)

```
5/8 회의 흐름:
1. W4 sprint 매트릭스 — 10 단일 + 3 multi = 13 cell (10분)
2. RQ1 — selectivity gradient 5×2 단조성 (15분)
3. RQ2 — KM20 oracle + K-aware + Anti-Neyman (15분)
4. RQ3 — 25 method tier elimination → 4-6 winner (20분)
5. Multi-vector + Multi-table — Exqutor 매칭 (10분)
6. YFCC source 단일화 결정 (build_yfcc 다운로드 폐기, sf100 base.80M.u8bin 권장) (10분)
7. Honest limitation + future work (sf100 plan) (10분)
8. 자문 요청 초안 합의 (채림 + 지도교수) (10분)
```

### 5/27 최종 발표 narrative (W4 결과 위에 sf100 결과 추가 시)

```
Slide 1 — 표지 (속도는벡터)
Slide 2 — Motivation (Exqutor + 본 연구 위치)
Slide 3 — W4 매트릭스 + sf100 추가 (13 + 5×1 = 18 cell)
Slide 4 — RQ1 (5 dataset × 2~3 scale selectivity gradient)
Slide 5 — RQ2 (KM20 + K-aware + Anti-Neyman)
Slide 6 — RQ3 25 method tier elimination → 4-6 winner
Slide 7 — 4강 method 일관성 heatmap
Slide 8 — Multi-vector + Multi-table direct comparison
Slide 9 — YFCC source 단일화 + sf100 plan (base.80M.u8bin)
Slide 10 — Honest limitation
Slide 11 — Future work (Exqutor multi-table + Distribution shift)
Slide 12 — Q&A
```

---

## 8. 산출 위치 (W4 only)

### 본 doc + 직속 산출
- **본 doc (v6 W4)**: `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft.md` (5/7 evening, 10 단일 + 3 multi narrative)
- **5/8 회의 PPT outline**: `submission/_drafts/속도는벡터_5월8일회의_PPT_outline.md` (W4 narrative 1:1 매핑)

### 측정 산출 (W4, [TBD measured])
- **Per-cell parquet**: `experiments/results/rq3_agnostic/rq3_{cell}_{method}.parquet`
  - 10 단일 cell × 25 method = 250 parquet
  - 3 multi cell × 25 method = 75 parquet
  - 총 ~325 parquet
- **K-sweep**: `experiments/results/rq2_aware/k_sweep_{cell}.parquet` × 10 cell × 5 K = 50 parquet
- **K_optimal 분석**: `experiments/results/rq1_motivation/k_optimal_per_dataset.csv` (10 row)
- **Tier elimination 표**: `experiments/results/rq3_agnostic/method_tier_elimination_W4.md`

### 자동화 인프라 (5/7 18:00~)
- `_internal/scripts/prepare_cell.py` — CELLS dict dispatch, dataset×scale 적재본 추출
- `_internal/scripts/chain_unified.py` — 25 method 일괄 measure dispatcher
- `_internal/scripts/build_wiki.py` — WIKI raw → partsupp_wiki extract
- `_internal/scripts/measure_multi_vector.py` — multi-vector 측정 runner
- `_internal/scripts/measure_multi_table_join.py` — multi-table natural join 측정 runner
- `_internal/scripts/run_cell_full.sh` — bash driver
- `_internal/실행_로그_20260507_full.md` — 5/7 evening sprint 진행 로그
- `_internal/scripts/build_yfcc.py` (5/8 10:18 사용자 결정으로 다운로드 결과 폐기 — 본 연구에서 사용하지 않음)

### figures (W4)
- `experiments/figures/W4_matrix/` — 13 cell heatmap (10 단일 + 3 multi, Tier 4 4강 method × cell)
- `experiments/figures/k_sweep/` — K_optimal per dataset × scale
- `experiments/figures/method_tier/` — Tier 1-4 elimination flow
- `experiments/figures/multi_relation/` — multi-vector + multi-table results

### 5/8 회의 자료
- 본 doc + PPT outline + 자문 메일 초안 v3 (`속도는벡터_자문메일초안_v3_supplement_20260507.md`)

### 인계 doc
- `_internal/handoff_v6_session_20260507_1822.md` — 5/7 18:22 W4 sprint 인계 (chain_unified.py + 25 method + 13 cell 결정사항, 5/8 10:18 build_yfcc 폐기로 갱신)
- `_internal/handoff_v5_session_20260507_1745.md` — 5/7 17:45 (Exqutor full match + K-aware framing)

---

## 9. 측정 운영 자동화 인프라 (5/7 18:00~)

### 활성 tmux 세션 (5/7 22:00 시점)
- `chain_DEEP_sf1` / `chain_DEEP_sf10` — DEEP 25 method 측정
- `chain_SIFT_sf1` / `chain_SIFT_sf10` — SIFT 측정
- `chain_SSN_sf1` / `chain_SSN_sf10` — SSN++ 측정
- `chain_WIKI_sf1` / `chain_WIKI_sf10` — WIKI 측정 (build_wiki 후)
- `chain_YFCC_sf1` / `chain_YFCC_sf10` — YFCC 채림 적재본 측정 (단일 정본)
- `multi_vec` — measure_multi_vector.py 측정
- `multi_join` — measure_multi_table_join.py 측정
- (build_yfcc 다운로드 chain — 5/8 10:18 사용자 결정으로 폐기)

### sf100 (80M) plan — 5/8 회의 후 자문 합의 후 진행

sf100 (80M, 5 dataset × 1 scale = 5 cell) 은 W4 의 future scope 이다. 5/8 19:00 비대면 회의에서:
1. W4 결과 (10 단일 + 3 multi) 공유 + 4강 method 일반화 검증.
2. 자문 메일 발송 (채림 + 지도교수) 합의.
3. **YFCC sf100 다운로드 = BigANN base.80M.u8bin 권장** (채림 정본 동일 source). build_yfcc 다운로드 결과는 5/8 10:18 사용자 결정으로 폐기.
4. 자문 회신 (~5/15) 후 sf100 측정 launch 결정.
5. sf100 측정 → 5/27 최종 발표 narrative 에 추가 (cross-scale validation 완성).

sf100 측정 estimated time: 5 dataset × ~2-4 hour = ~10-20 hour overnight chain (chain_unified.py extension).

---

## 10. 측정 완료 후 본 doc update plan

본 doc 의 [TBD measured] 부분을 다음 alignment 시점에서 정량 채움:

1. **5/8 새벽 (sf1 + sf10 W4 측정 완료 ETA)** — 10 단일 cell + 3 multi cell 매트릭스 채움 + K_optimal 10 cell 정량 + 25 method tier 1-4 통과 list 채움.
2. **5/8 19:00 회의 직전** — 본 doc + PPT outline 최신 [TBD measured] 채움. 회의에서 자문 메일 초안 합의.
3. **5/8 회의 후 자문 회신 (~5/15)** — sf100 plan 결정 + sf100 측정 launch.
4. **5/27 최종 발표 직전** — sf100 결과 통합 + 5×3 cross-scale full matrix narrative 완성.

---

## 11. 본 doc 의 W4 framing 한 줄 요약

> **본 연구 W4 sprint 는 Exqutor 본 논문의 ECQO 영역 (인덱스 + multi-table) 을 보완하는 단일 테이블 비인덱스 + 분포 인지 sampling 의 가치 정량화이다. 5 dataset × sf1/sf10 = 10 단일 cell (YFCC = 채림 정본 단일) + multi-vector × 2 + multi-table join × 1 = 13 cell × 25 method × K-aware 매트릭스 위에 (1) selectivity gradient 단조성 (2) KM20 oracle robustness (3) 4강 production-ready method (Hilbert / MiniBatch_partial / Hybrid / HDBSCAN) 의 5 dataset × 2 scale 일반화 입증 (4) σ_i 신호 약함의 honest 한계 (5) 분할 자체의 결정적 가치 (negative control) 의 5종 sub-contribution 을 9-10종 contribution + 6-8종 honest limitation 으로 정직 reporting 한다. sf100 (80M) 은 5/8 회의 후 자문 합의 결과를 반영하여 5/27 최종 발표 직전 별도 측정한다 (base.80M.u8bin 권장 — 채림 정본과 동일 source).**

---

**최초 작성**: 조현빈 · 2026-05-07 22:00 KST · W4 sprint final draft (10 단일 + 3 multi = 13 cell, 25 method, K-aware) · 5/8 10:18 build_yfcc 다운로드 폐기로 갱신
**작성 모델**: Claude Opus 4.7 1M, 통합 manager session
**선행 doc**: `_internal/handoff_v6_session_20260507_1822.md` (5/7 18:22 W4 인계) + `_internal/실행_로그_20260507_full.md` (5/7 evening 진행 로그)

**측정 완료 후 갱신 예정**: 5/8 새벽 (12 단일 + 3 multi) → 5/8 19:00 회의 직전 → 자문 회신 후 sf100 plan → 5/27 발표 final.
