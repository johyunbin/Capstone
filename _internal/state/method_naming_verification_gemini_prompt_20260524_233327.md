# Gemini Ultra 적대 검증 prompt — 16 method 명칭·문헌·paradigm 학술 정합성

> 작성: 2026-05-24 23:33 KST · target: Gemini 3.1 Pro
> 검증 결과 critical: 5/27 발표·6/11 보고서·채림님 자료 학술 정직성
> Multi-model verification — Codex (code 직접 read) 와 병렬, Gemini 강점: 문헌·paper reference·academic naming convention

## 0. 임무

당신은 **학술 명칭·paper reference·paradigm 분류의 정합성을 적대 검증하는 평가자**다. 16 method 의 (a) 현재 표명 명칭이 학술 standard 와 부합하는가, (b) 표명 reference 가 정본 출처인가, (c) paradigm 분류가 학술 taxonomy (ACM Computing Surveys 2024·VLDB cardinality estimation surveys) 와 align 하는가를 0 환각 0 오차로 검증한다.

## 1. Context

연세대 캡스톤 "속도는벡터" 의 RQ3 measurement (1,508 cell × 16 method × 3-way matched) 에 사용한 method 명칭 정직성. Claude 자체 audit 결과 11 method 명칭·algorithm·reference 부분 불일치 발견. Codex (병렬 dispatch) 가 code 측 audit 진행 중. 당신은 **학술 reference 측 audit** 주력.

## 2. 16 method (현재 표명 vs 의심)

### Group A — 학술 정합 (검증 필요 5)
1. **chao_weighted** — Chao 1982 JRSS 69:653 *A general purpose unequal probability sampling plan*
2. **cum_sqrtf** — Dalenius-Hodges 1959 JASA 54:88 *Minimum variance stratification*
3. **idistance** — Jagadish-Ooi-Tan-Yu-Zhang 2005 TODS 30:364 *iDistance: An adaptive B+-tree based indexing method for nearest neighbor search*
4. **ica_fastica** — Hyvärinen 1999 IEEE NN 10:626 *Fast and robust fixed-point algorithms for independent component analysis*
5. **rsvd** — Halko-Martinsson-Tropp 2011 SIAM Review *Finding structure with randomness*

### Group B — 의심 항목 (11)

| # | 명칭 | 표명 algorithm·reference | 실제 구현 (Claude audit) | 의심 |
|:--:|---|---|---|---|
| 6 | **hilbert_real** | "real Hilbert curve" / Faloutsos 1989 SIGMOD *Fastmap and other multidimensional indexing methods* | PCA 2D 환원 + Wikipedia xy2d Hilbert curve | Faloutsos 의 high-D Hilbert ≠ PCA 2D 환원 후 Hilbert |
| 7 | **skilling_hilbert** | "true high-D Hilbert" / Skilling AIP 2004 707:381 *Programming the Hilbert curve* | PCA(4) 환원 + Skilling 4-axis × 8-bit | Skilling 의 state-machine algorithm 은 native high-D, PCA 환원 simplification |
| 8 | **zorder_morton** | "Morton bit-interleave" / Morton IBM 1966 | PCA(2) 환원 + Morton + quantile | Morton native multidim, PCA 환원 명시 X |
| 9 | **lpm1_proper** | "proper Grafström LPM" / Grafström-Lundström-Schelin 2012 Biometrics 68:514 *Spatially balanced sampling through the pivotal method* | KMeans + BallTree + 근사 pivot | "proper" 표명 — 실제 simplification |
| 10 | **lavallee_hidiroglou** | "Lavallée-Hidiroglou Take-all + Neyman" / Lavallée-Hidiroglou 1988 Survey Method 14:33 *On the stratification of skewed populations* | take-all + cum-√f only (**Neyman σ_h 적용 X**) | Lavallée 의 핵심인 Neyman allocation 미적용 |
| 11 | **kmeans_neyman** | "KMeans + Neyman allocation" / Cochran 1977 *Sampling Techniques* §5 + Neyman 1934 JRSS *On the two different aspects of the representative method* | KMeans cluster id only (σ_h 계산 but boundary 적용 X) | "neyman" 명칭 — 실제 적용 X |
| 12 | **rabitq_strat** | "RaBitQ 1-bit code" / Gao-Lin VLDB 2024 17:3252 *RaBitQ: Quantizing high-dimensional vectors with a theoretical error bound for approximate nearest neighbor search* | center + QR + sign bits (full RaBitQ codebook 적용 X, 1-bit partition only) | full RaBitQ ≠ 1-bit partition |
| 13 | **idistance_neyman** | "iDistance + Neyman σ_h" / Jagadish 2005 + Neyman 1934 | iDistance + σ_h Neyman approximation re-bin | approximation 사용 |
| 14 | **mhist2** | "MHIST-2 multi-dim histogram" / Poosala-Ioannidis 1997 VLDB *Selectivity estimation without the attribute value independence assumption* | PCA(2) + 2D **equi-depth** grid (Poosala MaxDiff X) | MHIST-2 의 핵심 MaxDiff bucketing 미사용 |
| 15 | **kde_parzen** | "Parzen KDE high-D" / Parzen 1962 *On estimation of a probability density function and mode* Annals of Math Statistics | PCA 1D 환원 + 1D KDE Silverman | Parzen 의 high-D KDE ≠ PCA 1D 환원 |
| 16 | **hyperloglog** | "HyperLogLog InfoTheoretic" / Flajolet-Fusy-Gandouet-Meunier 2007 AofA *Hyperloglog: the analysis of a near-optimal cardinality estimation algorithm* | md5 hash → leading p bits **partitioning only** (cardinality estimator 미사용) | HLL 의 핵심 cardinality estimator (harmonic mean, bias correction) 미사용 |
| (carry) | **wavelet_hist** | "Wavelet histogram Matias 1998" / Matias-Vitter-Wang 1998 SIGMOD *Wavelet-based histograms for selectivity estimation* | PCA 1D + Haar wavelet on density profile + boundary | Matias 의 wavelet 의 일부 |
| (carry) | **dbscan** | "DBSCAN Ester 1996" / Ester-Kriegel-Sander-Xu 1996 KDD *A density-based algorithm for discovering clusters in large spatial databases with noise* | subset DBSCAN + centroid + nearest assign | subset training + non-DBSCAN assign |

### 외부 file (4)
- **pca1d** (Pearson 1901 *On lines and planes of closest fit*)
- **gmm** (Dempster-Laird-Rubin 1977 JRSS-B 39:1 *Maximum likelihood from incomplete data via the EM algorithm*)
- **minibatch_partial** (Sculley 2010 WWW *Web-scale K-means clustering* — partial_fit)
- **faiss_ivf** (Johnson-Douze-Jégou 2017 *Billion-scale similarity search with GPUs* — IVF index)
- **sparse_rp** (현재 정정 carry: Li-Hastie-Church 2006 KDD *Very sparse random projections*. 이전 표명 Achlioptas 2003 PODS *Database-friendly random projections* ❌)

## 3. 검증 임무 (Gemini 강점 활용)

### Task A — 학술 reference 정합성
각 method 의 표명 paper 가 실제 구현된 algorithm 의 정본 출처인가? simplification·approximation 사용 시 명시되어야 할 추가 reference 가 있는가?

특히:
1. **hilbert_real** — Faloutsos 1989 (high-D Hilbert) vs Wikipedia xy2d (2D Hilbert) — 실제 PCA 2D 환원 후 Hilbert 의 정본 reference 는?
2. **skilling_hilbert** — Skilling 2004 algorithm 137 (high-D Hilbert state machine) 의 PCA 환원 변형의 정본 reference?
3. **lavallee_hidiroglou** — Lavallée 1988 의 핵심 = take-all + Neyman. Neyman 미적용 시 partial 표명 권고?
4. **mhist2** — Poosala 1997 MHIST-2 의 핵심 = MaxDiff bucketing. equi-depth 사용 시 MHIST-2 명칭 부적합?
5. **hyperloglog** — Flajolet 2007 의 핵심 = harmonic mean cardinality estimator. partition only 시 HLL 명칭 부적합?

### Task B — Naming convention (학술 standard)
명칭에 "real"·"proper"·"true"·"neyman" 같은 표명을 붙일 때, 학술 convention 상 실제 algorithm 이 그 표명을 100% 만족해야 하는가? 부분 만족 시 어떤 suffix·prefix 가 적절한가?

예시:
- `hilbert_real` → `hilbert_pca2d` 또는 `hilbert_xy2d_pca2d` (PCA 환원 명시)?
- `lpm1_proper` → `lpm1_approx_kmeans_balltree` 또는 `lpm1_simplified`?
- `kmeans_neyman` → `kmeans_cluster_id` (Neyman 적용 X)?
- `rabitq_strat` → `rabitq_1bit_partition` (full RaBitQ X)?

### Task C — Paradigm 분류 학술 taxonomy
ACM Computing Surveys 2024 (high-dimensional indexing taxonomy) 또는 VLDB/SIGMOD cardinality estimation surveys 와 align 하는가?

- **PCA 환원 후 다른 algorithm 적용 method 9 개** (hilbert_real, skilling_hilbert, zorder_morton, mhist2, rsvd, kde_parzen, wavelet_hist, cum_sqrtf, lavallee_hidiroglou) 는 학술 standard 상 **DimReduction (P4)** vs **주된 algorithm paradigm** 어디로?
- **hyperloglog** (P9 InfoTheoretic) — partition only 시 InfoTheoretic 부적합, P5 Hashing 권고?
- **rabitq_strat** (P6 Quantization) — 1-bit partition only 시 P5 Hashing 권고?

### Task D — 정정 권고 (학술 정직성)
각 의심 항목에 대해 학술 정직성·misleading prevention 차원에서:
1. **rename**: 정확한 명칭 권고
2. **reference 정정·추가**: 정본 출처 또는 추가 paper
3. **docstring·논문 표기 명시**: "PCA 환원" "approximation" "partial implementation" 명시
4. **paradigm 재분류**: 학술 taxonomy align

### Task E — 학술 자료 영향 (보고서·채림님 자료)
정정 시 학술 narrative 에 어떤 영향?
1. 보고서 6/11 §3.6 paradigm 분류 표 — Group B 11 method 모두 영향
2. 보고서 §4.4 method 별 ranking — hilbert_real 1위 etc 의 명칭 영향
3. 채림님 전달용 자료 — BDAI 연구실 학술 입장에서 misleading 위험

특히:
- **hilbert_real 1위 (−6.54%)** 가 PCA 2D + Hilbert 라는 dim-reduction-based simplification 인데 "Hilbert" 명칭 만으로 "공간 곡선의 효과" 주장 시 학술 부정직?
- **skilling_hilbert 2위 (−6.34%)** 도 PCA(4) 환원 — true high-D Hilbert 결론으로 발표 시 misleading?

## 4. 응답 형식

```
# 검증 결과 (Gemini axis — 학술 정직성)

## Summary
- 학술 reference 정합성 점수:
- naming convention 점수:
- paradigm taxonomy align 점수:
- 종합 신뢰도:
- pass / conditional pass / fail:

## Task A 발견 — 학술 reference
## Task B 발견 — naming convention
## Task C 발견 — paradigm taxonomy
## Task D 정정 권고 (rename·reference·docstring·paradigm)
## Task E 영향 분석 (보고서·자료)

## 종합 권고 — 학술 정직성 보장 위한 우선순위 정정
```

언어: 한국어 (paper 명·algorithm 용어 영문 그대로).
응답 길이: 자세히 (2000-4000 자). 학술 정직성·academic fraud prevention 차원에서 발견된 모든 의심 명시. 점수는 16 method 전수 평균.
