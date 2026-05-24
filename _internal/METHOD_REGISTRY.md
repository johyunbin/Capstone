# METHOD_REGISTRY.md — 57 Method Paradigm 분류

> 작성: 2026-05-11 01:30 KST  
> ★ **5/24 carry note (3-multi-AI audit 결과 반영)**: 본 registry 의 P2.1 `hilbert_real` description ("진짜 Hilbert curve") 은 PCA 2D 환원 후 Wikipedia xy2d Hilbert curve 적용을 의미 — high-D Hilbert 아님. 본 연구의 발표·보고서·임채림 연구원 전달용 자료에서는 정정 후 명칭 (`pca2d_hilbert_xy2d` 등 8 method rename + paradigm P9→P5b·P5→P5 Classical Stratification 재분류) carry. 정정 list 와 사유는 `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.md` §4.7 verbatim + `submission/_drafts/속도는벡터_채림님_전달용_구체적_데이터_v2_재구성_20260524_233327.md` §7 carry.
> 목적: Tier S/A/B/Q1/Q4/Phase 4 분류 폐기 → **paradigm (P1-P10)** 단일 분류  
> 사용자 명시 (5/11 01:15): "여러 세션 작업물 뒤엉킴 — Tier S/A/B/Q1/Q4/Phase 4 분류 의미 X."  
> 출처: handoff_v5 §2 + method_verification_20260510 _SUMMARY + handoff_v3 §1 + measure_paper_exact.py line 416-880

---

## 0. TL;DR — 57 method × 10 paradigm 분포

| Paradigm | 활성 method | 폐기/rename | 합 | ★ 후보 |
|---|---|---|---|---|
| **P1 Cluster** | minibatch / gmm / mb_partial / birch / agglo / coreset / dbscan / kmeans_neyman M9 | hkbu_repsample / banditucb1 (rename) | 8 + 2 | ★1 hdbscan (V8 후보, 측정 X) / ★2 mb_partial |
| **P2 Spatial** | hilbert_real / skilling_hilbert M7 / zorder_morton M6 / idistance M5 / idistance_neyman M11 / faiss_ivf / lpm1_proper M2 / epsilon_net | hilbert (rename `pca2d_lex`) / kdtree (raw 권고) / kdpp (≡ epsilon_net 폐기) | 8 + 3 | **★3 hilbert** (defect → M6/M7 rectify) |
| **P3 Streaming** | chao_weighted M1 | reservoir (rename `random20`) / thompson_sampling / mfmc / ams_count_sketch / ccsketch (모두 폐기) | 1 + 5 | (없음) |
| **P4 DimReduction** | sparse_rp / random_projection / pca1d / rsvd / ica_fastica M8 | dense_rp (≡ rp) / neuram (≡ PCA1D 폐기) / cca1d (≡ PCA1D 폐기) / tucker (rename) / vinecopula (rename) / factor_join (rename) / adaptive_bucket_probing (≡ PCA1D 폐기) / neurocard_lite (rename + P1 이동) | 5 + 8 | **★4 sparse_rp** (Li 2006 reference 정정) |
| **P5 QMC/Hashing** | lsh / sobol / halton / hammersley / lhs / cum_sqrtf M3 / lavallee_hidiroglou M4 | lp_bound (rename `l2_quantile`) | 7 + 1 | (없음) |
| **P6 Quantization** | rabitq_strat M10 / mhist2 / wavelet_hist | pq / opq (md5 fix) | 3 + 2 | (paradigm 회복 anchor M10) |
| **P9 InfoTheoretic** | hyperloglog | — | 1 | (Q4 신규 paradigm) |
| **P10 Density** | kde_parzen | — | 1 | (Q4 narrative anchor) |
| **P7 Subspace** | (future work — CLIQUE) | — | 0 | future |
| **P8 Graph-based** | (future work — Leiden) | — | 0 | future |
| **합계** | **34 활성** | **23 폐기/rename** | **57** | 4 + future |

* `★` = 4강 후보 (handoff_v0 V8 audit), 단 ★3 hilbert는 fraud risk 발견 후 M6/M7 paradigm anchor 로 rectify.

---

## 1. P1 Cluster (밀도/cluster 기반, 8 활성 + 2 폐기/rename)

### 1.1 활성 (8건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 (audit) | 비고 |
|---|---|---|---|---|---|
| P1.1 | minibatch | Sculley D. *WWW* 2010 (Web-scale K-means) | Tier 1 | 8/10 | 견조 |
| P1.2 | gmm | Dempster-Laird-Rubin *JRSS* 1977 (EM) | Tier 1 | OK (covariance_type='diag' + reg_covar=1e-2 fix) | SIFT 128d / SSN 256d cholesky fail 회피 |
| P1.3 | minibatch_partial | Sculley D. *WWW* 2010 — partial fit | Tier 1 | **8/10 ★2** | 4강 strong replace (-7.41% → method-mean -10.17%) |
| P1.4 | birch | Zhang T. *SIGMOD* 1996 | extra | OK (small subset 5K) | spectralBiclustering 변형 가능 |
| P1.5 | agglomerative | Ward Jr JH. *JASA* 1963 | extra | OK (subset 10K) | O(n²) memory subset 우회 |
| P1.6 | coreset | Bachem-Lucic-Krause 2017 | extra | warning (max_iter=10 어중간) | 결정 필요: max_iter=0 또는 100+ |
| P1.7 | dbscan | Ester-Kriegel-Sander-Xu *KDD* 1996 | **Q4 Tier 1** | NEW (구현 5/10) | HDBSCAN 직접 비교 |
| P1.8 | kmeans_neyman M9 | Cochran 1977 §5 + Neyman 1934 *JRSS* | **Phase 4** | NEW (Phase 4 cascade 통과) | RQ2 plug-in 직접 강화 |

### 1.2 폐기/rename (2건)

| code | method_name | 결함 | 권고 |
|---|---|---|---|
| P1.D1 | hkbu_repsample | coreset 본질 중복 + max_iter=5 미수렴 | **폐기 OR max_iter ↑** |
| P1.D2 | banditucb1 | UCB1 미구현, 단순 KMeans wrapper (코드 주석에서 본인 인정) | **폐기 OR rename `kmeans_subset_100k`** |

### 1.3 ★1 hdbscan 별도 note

- handoff_v0 V8 audit 4강 ★1 (`-8.04` paired Δ%)
- paper exact 측정에 미포함 (현재 39 method registry 외)
- 충실도 7/10 — minor tuning OK (K_eff<20 padding 명시, stability vs size pruning disclaimer)
- Campello 2013 *Density-based clustering based on hierarchical density estimates*
- 5/27 narrative 강화 시 Tier 1 추가 권고 (handoff_v3 P2 권고 list)

---

## 2. P2 Spatial (공간/SFC/grid 기반, 8 활성 + 3 폐기/rename)

### 2.1 활성 (8건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 |
|---|---|---|---|---|
| P2.1 | **hilbert_real** | Faloutsos *SIGMOD* 1989 — Hilbert curve indexing (raw `experiments/code/rq3/hilbert/hilbert_curve.py` Wikipedia 표준) | **Q1 (C) rectify** | NEW (★3 defect 정정) |
| P2.2 | **skilling_hilbert M7** | Skilling J. *AIP Conf Proc* 2004; 707:381-387 — Programming the Hilbert curve (state-machine algorithm) | **Phase 4** | NEW (true high-D Hilbert) |
| P2.3 | **zorder_morton M6** | Morton GM. *IBM Tech Rep* 1966 — Z-order space-filling curve | **Phase 4** | NEW (paradigm anchor) |
| P2.4 | **idistance M5** | Jagadish-Ooi-Tan-Yu-Zhang. *TODS* 2005; 30(2):364-397 | **Phase 4** | NEW (1D scalar from KMeans20 centroids) |
| P2.5 | **idistance_neyman M11** | Jagadish 2005 + Neyman 1934 synthesis | **Phase 4** | NEW (cluster-aware Neyman) |
| P2.6 | faiss_ivf | Johnson-Douze-Jégou *FAISS* 2017 — IndexIVF | Tier 1 | 6/10 (seed 미고정 minor) |
| P2.7 | **lpm1_proper M2** | Grafström-Lundström-Schelin. *Biometrics* 2012; 68(2):514-520 — LPM | **Phase 4** | NEW (proper Grafström rectify, lpm2 misnomer) |
| P2.8 | epsilon_net | Bachem 2017 farthest-first | extra2 | warning (kdpp 와 line-by-line 동일) |

### 2.2 폐기/rename (3건)

| code | method_name | 결함 | 권고 |
|---|---|---|---|
| P2.D1 | **hilbert** (★3 4강) | PCA 2D lex sort, Faloutsos 1989 ❌ — **학술 fraud risk** | **rename `pca2d_lex` (현재 결과 보존) + M6/M7 paradigm anchor 추가** (handoff_v5 §2 Q1 (C)) |
| P2.D2 | kdtree | `idx % n_strata` = spatial locality 0 (random hash 등가) | **raw `kdtree_partition.py` 사용** OR 폐기 |
| P2.D3 | kdpp | epsilon_net 와 line-by-line 동일 (주석 1줄 차이) | **폐기 OR 진짜 DPP 재구현** |

### 2.3 핵심 narrative

- **★3 hilbert defect rectify** = M6 zorder_morton (paradigm anchor) + M7 skilling_hilbert (true high-D Hilbert)
- "Hilbert curve 의 진짜 locality 효과 vs PCA proxy 효과 분리 검증" = paper 학술 finding (handoff_v5 §9.1)

---

## 3. P3 Streaming (online/reservoir, 1 활성 + 5 폐기)

### 3.1 활성 (1건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 |
|---|---|---|---|---|
| P3.1 | **chao_weighted M1** | Chao MT. *Biometrika* 1982; 69(3):653-656 — A general purpose unequal probability sampling plan | **Phase 4** | NEW (priority queue, weight-aware) |

### 3.2 폐기 (5건)

| code | method_name | 결함 | 권고 |
|---|---|---|---|
| P3.D1 | reservoir | Vitter 1985 ❌ — RANDOM20 random partition | **rename `random20`** (계속 control variate baseline 으로 사용) |
| P3.D2 | thompson_sampling | Thompson 1933 ❌ — MiniBatchKMeans (Beta posterior 부재) | **폐기** |
| P3.D3 | mfmc | Peherstorfer 2018 ❌ — KMeans+RANDOM20 mask (control variate 부재) | **폐기** |
| P3.D4 | ams_count_sketch | Alon-Matias-Szegedy 1996 ❌ — line-by-line lsh 동일 | **폐기** |
| P3.D5 | ccsketch | Cormode-Muthukrishnan 2005 ❌ — float mod + np.min skewed | **폐기** |

### 3.3 paradigm 평균 충실도 3.4/10 (P6 다음으로 낮음)

P3 의 미래 = M1 chao_weighted (단일 활성) + RANDOM20 control variate baseline. RQ2 + RQ3 결합 narrative anchor 부재.

---

## 4. P4 DimReduction (PCA/embedding, 5 활성 + 8 폐기/rename)

### 4.1 활성 (5건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 |
|---|---|---|---|---|
| P4.1 | **sparse_rp ★4 4강** | **Li-Hastie-Church 2006** ⭕ (Achlioptas 2003 ❌ → 정정) — Very sparse random projection | Tier 1 | **6/10 ★4 paradigm anchor** |
| P4.2 | random_projection | Achlioptas D. *PODS* 2001 — Database-friendly random projections | extra | OK |
| P4.3 | pca1d | Pearson K. *Phil Mag* 1901 | Tier 1 | **10/10 textbook** |
| P4.4 | rsvd | Halko-Martinsson-Tropp *SIAM Rev* 2011 — Randomized SVD | **Q4 Tier 1** | NEW (PCA1D large-scale) |
| P4.5 | **ica_fastica M8** | Hyvärinen A. *IEEE NN* 1999; 10(3):626-634 — FastICA | **Phase 4** | NEW (non-Gaussian independence) |

### 4.2 폐기/rename (8건)

| code | method_name | 결함 | 권고 |
|---|---|---|---|
| P4.D1 | dense_rp | random_projection normalization 차이만 | **폐기 OR ablation narrative 명시** |
| P4.D2 | neuram | autoencoder ❌ — PCA1D 100% 동일 | **폐기** |
| P4.D3 | cca1d | Hotelling 1936 CCA ❌ — PCA(whiten=True), Y 부재 | **폐기** (PCA1D bit-equal) |
| P4.D4 | tucker | Tucker 1966 tensor ❌ — PCA(3) + 3D grid + modulo | **rename `pca3d_grid`** |
| P4.D5 | vinecopula | Bedford-Cooke 2002 ❌ — rank+PCA1D (vine graph 부재) | **rename `spearman_pca1d`** |
| P4.D6 | factor_join | Zhao 2023 FactorJoin ❌ — PCA(2)+5×5 grid (PGM 부재) | **rename `pca2d_grid` + paradigm 이동 (P6 → P4)** |
| P4.D7 | adaptive_bucket_probing | PCA1D 와 8-line identical (variance 주석만) | **폐기 OR 진짜 variance-aware bin 재구현** |
| P4.D8 | neurocard_lite | Yang 2020 NeuroCard ❌ — PCA(8)+KMeans (transformer 부재) | **rename `pca8_kmeans` + paradigm 이동 (P6 → P1)** |

### 4.3 ★4 sparse_rp 핵심 update

- 표명 "Achlioptas 2003" ❌ → 실제 Li 2006 1/√D variant (V9 audit + 5/10 8-agent audit 일치)
- **reference 정정만, 코드 변경 X** (이미 측정한 결과 그대로 보존)
- paper / 보고서 / PPT 모두 "Li-Hastie-Church 2006" 표기 통일

---

## 5. P5 QMC/Hashing (uniform / low-discrepancy, 7 활성 + 1 rename)

### 5.1 활성 (7건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 |
|---|---|---|---|---|
| P5.1 | lsh | Indyk-Motwani *STOC* 1998 | Tier 1 | warning (YFCC 192d outlier) |
| P5.2 | sobol | Sobol IM. *USSR Math Phys* 1967 | Tier 1 | warning (argmax 매핑 — QMC 정통 X) |
| P5.3 | halton | Halton JH. *Numer Math* 1960 | extra | warning (high-D degeneracy) |
| P5.4 | hammersley | Hammersley JM. *NYAS* 1960 | extra | warning (first-dim asymmetry) |
| P5.5 | lhs | McKay-Beckman-Conover *Technometrics* 1979 — Latin Hypercube | extra2 | warning (normalization 부재) |
| P5.6 | **cum_sqrtf M3** | Dalenius T, Hodges JL. *JASA* 1959; 54(285):88-101 — Minimum variance stratification | **Phase 4** | NEW (P5+RQ2 anchor) |
| P5.7 | **lavallee_hidiroglou M4** | Lavallée P, Hidiroglou M. *Survey Methodology* 1988; 14(1):33-43 — Take-all stratum + Neyman | **Phase 4** | NEW (skew long-tail handling) |

### 5.2 rename (1건)

| code | method_name | 결함 | 권고 |
|---|---|---|---|
| P5.D1 | **lp_bound** | **SIGMOD 2025 Best Paper "LpBound" (Zhang/Suciu) 명칭 충돌** — naming fraud risk | **rename `l2_quantile`** (8/10 audit, 알고리즘은 견조) |

### 5.3 paradigm 평균 충실도 4.4/10

low-discrepancy method (sobol/halton/hammersley/lhs)는 모두 disclaimer 추가 권고 — high-D vector skew 분포 부적합.

---

## 6. P6 Quantization (3 활성 + 2 fix)

### 6.1 활성 (3건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 |
|---|---|---|---|---|
| P6.1 | **rabitq_strat M10** | Gao J, Lin C. *Proc VLDB Endow* 2024; 17(11):3252-3265 — RaBitQ | **Phase 4** | NEW (paradigm 회복 anchor, 2024 fresh) |
| P6.2 | mhist2 | Poosala V. *VLDB* 1997 — MHIST | **Q4 Tier 1** | NEW (real alternative to factor_join defect) |
| P6.3 | wavelet_hist | Matias Y, Vitter JS, Wang M. *SIGMOD* 1998 — Wavelet histogram | **Q4 Tier 1** | NEW |

### 6.2 fix (2건)

| code | method_name | 결함 | 권고 |
|---|---|---|---|
| P6.F1 | pq | `IndexPQ.sa_encode → md5 hash → mod 20` — codeword distance 무효 (사실상 reservoir 등가) | **md5 제거 → codeword id 직접 사용** |
| P6.F2 | opq | pq 동일 (md5 destroys OPQ 효과) | **md5 제거 + niter 명시** |

### 6.3 paradigm 평균 충실도 1.6/10 (가장 낮음)

handoff_v3 § P6 권고: paradigm 폐지 vs P9/P10 신규 → **(B) 9 paradigm 확장 권고** (P9 InfoTheoretic + P10 Density 신규). M10 RaBitQ 가 P6 회복 anchor.

cocluster_nystrom (Williams 2001 Nyström 미구현 → rename `biclustering_5k_centroid`) 별도 paradigm 이동.

---

## 7. P9 InfoTheoretic (신규 paradigm, 1건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 |
|---|---|---|---|---|
| P9.1 | hyperloglog | Flajolet-Fusy-Gandouet-Meunier *AofA* 2007 — HyperLogLog | **Q4 Tier 1** | NEW (sketch textbook anchor) |

handoff_v3 §1.3 권고로 paradigm 신규 도입. PDX SIGMOD 2025 narrative align.

---

## 8. P10 Density (신규 paradigm, 1건)

| code | method_name | reference verbatim | 출처 단계 | 충실도 |
|---|---|---|---|---|
| P10.1 | kde_parzen | Parzen E. *Ann Math Statist* 1962 — KDE (Kernel Density Estimation) | **Q4 Tier 1** | NEW (narrative learning anchor) |

handoff_v3 §1.3 권고. KDE Parzen 가 본 연구 "분포 인지 stratification"의 textbook anchor — 5/27 발표 paper origin.

⚠️ kde_pilot (V7 audit) = `stratum_id` column SELECT (KMeans20 결과) — KM20 oracle leak 으로 RQ3 paradigm 비교에서 제외 유지. 본 P10.1 kde_parzen 는 별도 (raw KernelDensity sklearn).

---

## 9. P7 Subspace + P8 Graph (future work, 0건)

- **P7 Subspace**: CLIQUE (Agrawal 1998), DOC, ENCLUS — high-D subspace clustering
- **P8 Graph-based**: Leiden (Traag 2019), Louvain (Blondel 2008) — community detection

5/27 발표 후 추가 권고 (handoff_v3 §2.3). 현재 측정 scope 외.

---

## 10. 메인 paradigm × dataset fit 매트릭스 (handoff_v3 §3.3 verbatim)

| Paradigm category | DEEP (mod skew) | SIFT (high skew) | SSN (balanced) | YFCC (very skew) | WIKI (low intrinsic) |
|---|---|---|---|---|---|
| **A: PCA-based** (P4 5건) | ✓✓ | ✓✓✓ | ✗ | ✓✓✓ | ✓ |
| **B: density/cluster** (P1 8건 + P10 1건) | ✓✓ | ✓✓✓ | ✗ | ✓✓✓ | ✓ |
| **C: QMC uniform** (P5 7건) | ✗ | ✗✗ | ✓✓✓ | ✗✗✗ | ✗ |
| **D: distribution-agnostic** (P3 1건 + P9 1건) | ◎ | ◎ | ◎ | ◎ | ◎ |
| **E: VQ/centroid** (P2 8건 + P6 3건) | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓✓ |

---

## 11. 5/27 발표 narrative 강화 (handoff_v5 §9 verbatim + paradigm 분류 통합)

| storyline 단계 (사용자 명시 5/9 18:27) | 핵심 paradigm × method |
|---|---|
| 1 단일 random sampling skew 무너짐 (RQ1) | RANDOM20 (reservoir rename) baseline + chao_weighted M1 (P3 weight-aware) |
| 2 분포 알면 Neyman 답 (RQ2) | **kmeans_neyman M9 (P1+RQ2) / cum_sqrtf M3 (P5) / lavallee_hidiroglou M4 (P5) / idistance_neyman M11 (P2+RQ2)** |
| 3 분포 모르니까 추정 활용 (RQ3) | sparse_rp ★4 (P4 anchor) / minibatch_partial ★2 (P1) / lpm1_proper M2 (P2) / idistance M5 (P2) / zorder_morton M6 (P2) |
| 4 단일 -8% 격차 입증 | minibatch_partial -10.17% method-mean / sparse_rp -8.13% CaseB ensemble |
| 5 multi-table 0/66 | (이전 narrative — multi 측정 진행 중) |
| **6 신규 method 발굴** | **Phase 4 11 method (M1-M11) 모두 P0/P1** + Q4 Tier 1 6 (DBSCAN/KDE/MHIST-2/HLL/RSVD/wavelet) |
| **7 Adaptive vs Adaptive+ensemble climax** | **M9/M11 RQ2 plug-in 직접 강화** + ★4 sparse_rp paradigm anchor |

---

## 12. 학술 contribution claim (handoff_v5 §9.1 verbatim)

1. **★3 hilbert defect rectify** = M6 zorder_morton (paradigm anchor) + M7 skilling_hilbert (true high-D Hilbert)
   - "Hilbert curve 의 진짜 locality 효과 vs PCA proxy 효과 분리 검증" = paper 학술 finding
2. **RQ2 + RQ3 결합 4건** (M9/M11 + M3/M4) = "분포 정보 추정 방식 × Neyman σ allocation" 2D ablation
3. **2024-25 SIGMOD/VLDB 인용**: 
   - M10 RaBitQ (Gao-Lin VLDB 2024)
   - Q4 PRICE (Zeng VLDB 2024)
   - LpBound rename (lp_bound → l2_quantile, SIGMOD 2025 Best Paper LpBound 충돌 회피)
   - PDX SIGMOD 2025 (intrinsic_dim + skewness — RQ1 narrative align)

---

## 13. 폐기 method 종합 list (Q2 audit 권고)

**10건 폐기 권고** (handoff_v3 §1.3 일치):
1. thompson_sampling (P3 defect)
2. mfmc (P3 defect)
3. neuram (P4 defect)
4. cca1d (P4 defect)
5. ams_count_sketch (P3/P5 defect)
6. ccsketch (P3 defect)
7. kdpp (P2 defect — ≡ epsilon_net)
8. cocluster_nystrom (P6 → 별도 paradigm rename `biclustering_5k_centroid`)
9. banditucb1 (P1 defect — UCB1 미구현)
10. hkbu_repsample (P1 defect — max_iter=5) **OR** coreset (max_iter=10 어중간)

**rename only** (코드 변경 X, 8건):
1. hilbert → `pca2d_lex` (★3 defect, 결과 보존)
2. reservoir → `random20` (RANDOM20 baseline)
3. lpm2 → `radial_quantile` (Weiszfeld median + radial)
4. tucker → `pca3d_grid`
5. vinecopula → `spearman_pca1d`
6. factor_join → `pca2d_grid` (P6 → P4 이동)
7. neurocard_lite → `pca8_kmeans` (P6 → P1 이동)
8. lp_bound → `l2_quantile` (SIGMOD 2025 LpBound 명칭 충돌 회피)
9. kdtree (raw `kdtree_partition.py` 권고)

**reference only** (1건):
- sparse_rp: Achlioptas 2003 ❌ → Li-Hastie-Church 2006 ⭕

---

## 14. 사용자 confirm 상태 (5/11 01:05 KST 기준)

| Q | 권고 | confirm |
|---|---|---|
| Q1 | ★3 hilbert: (C) `pca2d_lex` rename + 진짜 hilbert 별도 추가 | ✅ confirmed (5/11 01:05) — handoff_v5 §0 verbatim "ㅇㅋ. 모두 다 진행할거라서. 순서대로 해도 무관." |
| Q2 | 10건 폐기 권고 모두 폐기 | ✅ confirmed |
| Q3 | (B) 9 paradigm 확장 (P9 + P10 신규) | ✅ confirmed |
| Q4 | Tier 1 6 method 추가 (DBSCAN/KDE/MHIST-2/HLL/RSVD/wavelet) | ✅ confirmed (handoff_v5 §7 통합 launch) |
| Q5 | handoff_v2 5 paper exact decisions | ✅ confirmed (handoff_main §6.2 5단계 narrative + paper exact 진행 中) |

---

## 15. END

작성: 2026-05-11 01:30 KST  
다음 단계: EXPERIMENT_REGISTRY.md (cell × method × mode matrix) 작성  

**핵심 원칙**: Tier S/A/B/Q1/Q4/Phase 4 분류 폐기 → **paradigm P1-P10 단일 분류**. 새 세션이 본 file 1건 read 만으로 57 method 의 paradigm + 출처 + 폐기/rename 의사결정 모두 파악 가능.
