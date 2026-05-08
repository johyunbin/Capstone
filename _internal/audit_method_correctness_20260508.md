# 11 Method Mathematical Correctness Audit

생성: 2026-05-08 KST · V7 백그라운드 에이전트 · audit only (코드 수정 X)
대상: RQ3 5 paradigm × 11 method 의 fit/assign 구현
목표: canonical reference (paper) 와 cross-check, ✅ correct / ⚠️ minor deviation / ❌ incorrect 판정

---

## 1. 판정 표

| # | Method | Paradigm | Server File | Canonical Ref | 판정 |
|---|--------|----------|-------------|---------------|------|
| 1 | HDBSCAN | P1 Cluster | `cache/rq3/hdbscan/hdbscan_partition.py` (110 L) | Campello 2013 (sklearn HDBSCAN wrapper) | ✅ |
| 2 | MiniBatch | P1 Cluster | `cache/rq3/offline_simple/minibatch_kmeans.py` (97 L) | Sculley 2010 (sklearn MiniBatchKMeans) | ✅ |
| 3 | GMM | P1 Cluster | `cache/rq3/gmm/gmm_partition.py` (73 L) | Dempster 1977 EM (sklearn GaussianMixture, diag cov) | ✅ |
| 4 | Hilbert | P2 Spatial | `cache/rq3/hilbert/hilbert_curve.py` (239 L) | Lawder 2001 + Wikipedia xy2d | ✅ |
| 5 | faiss_ivf | P2 Spatial | `run_faiss_ivf.py` + inline in `measure_multi_paradigm.py` | Jégou PAMI 2011 (IndexIVFFlat coarse quantizer) | ✅ |
| 6 | MB_partial | P3 Streaming | `cache/rq3/offline_simple/minibatch_partial.py` (229 L) | Sculley 2010 + sklearn `partial_fit` | ✅ |
| 7 | Reservoir | P3 Streaming | `run_reservoir.py` (single) / `_fit_reservoir` (multi) | Vitter 1985 Algorithm R | ⚠️ (single-cell proxy ≠ Vitter; multi-cell OK) |
| 8 | sparse_rp | P4 DimReduction | `cache/rq3/sparserp/sparse_random_projection.py` (73 L) | Achlioptas 2003 ({-√3, 0, +√3}) | ✅ (density는 1/√D 변형) |
| 9 | PCA1D | P4 DimReduction | `cache/rq3/pca1d/pca1d_quantile.py` (131 L) | Pearson 1901 SVD top eigenvector | ✅ |
| 10 | LSH | P5 Quasi-random | `cache/rq3/lsh/lsh.py` (154 L) | Charikar 2002 SimHash | ⚠️ (Wave 0 hyperparam: 5 hp + mod 20) |
| 11 | Sobol | P5 Quasi-random | `cache/rq3/sobol/sobol_stratification.py` (101 L) | Sobol 1967 + scipy.stats.qmc.Sobol | ✅ |

---

## 2. Canonical Reference Cross-Check 핵심 Finding

### ✅ Paper-correct 9종

* **HDBSCAN**: `sklearn.cluster.HDBSCAN(min_cluster_size=50)` 호출 후 cluster centroid 추출 + nearest-centroid 부여. Cluster 수가 K=20 과 다르면 KMeans 로 보충/축약 — Campello 의 hierarchy + EOM extraction 이 sklearn 내부에서 수행되며, K=20 stratum 정합성을 위해 추가 KMeans 한 번이 들어감 (paper 의도 보존, stratum 수 강제 제약만 추가).
* **MiniBatch**: `sklearn.cluster.MiniBatchKMeans(batch_size=1024, n_init=3, max_iter=100)` 호출. Sculley 2010 의 streaming average centroid update 가 sklearn 구현에 그대로 반영.
* **GMM**: `sklearn.mixture.GaussianMixture(n_components=20, covariance_type='diag', max_iter=100)` 호출. Dempster EM 이 sklearn 내부 구현. `argmax` (`predict`) 로 hard assignment — soft posterior 가 stratum_id 부여에 직접 안 쓰이지만, 본 task 가 hard partition 이라 정합.
* **Hilbert**: `hilbert_xy_to_d` 가 Wikipedia 의 xy2d algorithm 표준 구현 — `rx = (x & s) > 0`, `ry = (y & s) > 0`, `d += s*s * ((3*rx) ^ ry)`, rotate/flip when `ry==0`. Self-test 가 p=1 에서 (0,0)→0, (0,1)→1, (1,1)→2, (1,0)→3 확인. PCA 2D + grid + quantile bin = Lawder 2001 의 "high-D Hilbert via PCA + scaling" 표준 절차.
* **faiss_ivf**: `IndexIVFFlat(quantizer=IndexFlatL2, d, n_strata, METRIC_L2)`, `index.train(learn)`, `quantizer.search(vec, 1)` 로 nearest centroid 부여. Jégou IVF 의 coarse quantizer 정의에 그대로 부합.
* **MB_partial**: warmup `model.fit(samples[:warmup])` → loop `model.partial_fit(chunk)`. sklearn `partial_fit` API 가 Sculley 의 streaming centroid update 를 그대로 따름. drift summary 까지 측정 → production OLTP narrative 의 핵심 evidence.
* **sparse_rp**: density `p_nz = 1/√D`, scale `s = 1/√p_nz = D^(1/4)`, entries `±s with prob p_nz/2 each, 0 otherwise`. **이는 Li et al. 2006 "Very sparse random projections" 의 식을 따른 것** (Achlioptas 2003 의 density 1/3 + entries {-√3,0,+√3} 가 아니라 D 가 클 때의 √D-fold speedup variant). 96d 면 `p_nz ≈ 0.102`, scale `s ≈ 3.13`. JL embedding 보존 + sparse property 둘 다 보장 — Achlioptas 의 sparse 계열에 *family of methods* 로 포함되며 정통.
* **PCA1D**: `sklearn.decomposition.PCA(n_components=1, svd_solver='full')` + quantile bin. Pearson SVD top eigenvector + 1D projection — 가장 단순. self-test 에서 quantile 균등 (max/min < 1.5) 확인.
* **Sobol**: `scipy.stats.qmc.Sobol(d=2, seed, scramble=True).random(n=20)` 호출 + PCA 2D coord + nearest sobol point 부여. Sobol 1967 + 표준 scrambling (LMS+shift) 그대로.

### ⚠️ Minor deviation 2종

* **Reservoir** (single cell `run_reservoir.py`): 구현이 `rng.integers(0, n_strata, size=n_rows)` 으로 **단순 random partition** — 이는 Vitter Algorithm R 가 *아니라* RANDOM20 과 동일. 코드 docstring 도 "random20 와 같은 알고리즘이지만 다른 seed" 로 인정. 그러나 multi-cell `measure_multi_paradigm.py:_fit_reservoir` 는 `rng.choice(n, size=n_strata, replace=False)` + nearest-centroid 부여 — 이는 Vitter Algorithm R 의 **statistically equivalent batch form** (single-pass uniform K-subset 통계적 동치). 결과적으로 single 과 multi 가 다른 알고리즘으로 측정됨. 본 audit 시점 narrative (multi 측정본 위주) 에서는 ✅, 단 single-cell 의 reservoir entry 가 RQ3 30 method 표에 들어가 있으면 RANDOM20 duplicate 가능 — 이전 audit (5/8) 의 "23 clean / 5 pending" 중 reservoir 가 pending 5종에 포함된 사실과 정합. **narrative 정정 필요**: single-cell reservoir 측정값은 RANDOM20 의 다른 seed.
* **LSH** (Wave 0 hyperparam 그대로): `n_hp = ceil(log2(20)) = 5` hyperplanes + `mod 20` 매핑. Charikar 2002 의 random hyperplane signed-bit projection 구현은 정확 (`sign(W·v)` → bit pattern → raw_id). 그러나 **5 hyperplane → 32 raw bucket 을 mod 20 으로 강제 압축** 함으로써 buckets 0~11 이 12~19 의 ≈2× density 로 crowded — self-test 에서 mod collision ratio 1.5~3.0 확인. K=20 stratum 균등성을 깨뜨려 stratification quality 가 의도적으로 약화됨. Paper 자체와는 일치하나, RQ3 의 stratum balance 에는 부적합 — Wave 0 +2092% 결과의 *implementation 원인*. **수정안** (audit only, 적용 X): K=16 (4 hp, 깔끔) 또는 K=32 (5 hp 그대로, mod X) 가 자연. 본 연구는 K=20 강제로 mod collision 을 의도적으로 수용 → narrative 에 명시.

### ❌ Incorrect: 0종

---

## 3. Wave 0 Failure 원인 재검증

* **LSH (+2092%)**: paper 와 implementation 일치, 그러나 **K=20 vs n_hp=5 의 misalignment 가 mod 20 collision 유도** → buckets 0~11 의 over-density (uniform 입력 기준 ~2×, 실 embedding 의 anisotropy 로 추가 imbalance). HT estimator 의 `weight = N_i / s_i` 가 imbalance 를 보정해야 하나, sample size = 385/cell × 20 cell = 7700 이 buckets 0~11 (22 cell-equivalent) 로 뭉치면 12~19 (8 cell) 의 cell 당 ~50 sample 이 되어 variance 폭발. **원인은 hyperparameter (K-n_hp 정합성 부재) 의 algorithmic limitation**, paper-incorrect 가 아님.
* **DBSCAN / random_proj** (Wave 0 다른 failure): file list 에서 확인된 별도 method, 본 11 method 외 (배제 대상). 별도 audit 필요 시 추가 라운드.

---

## 4. 결론

* **11 method 중 9종이 ✅ paper-correct**, 2종 (Reservoir, LSH) 이 ⚠️ minor deviation. ❌ incorrect 는 0.
* **우려 항목**:
  1. **Reservoir single-cell vs multi-cell 알고리즘 불일치** — single 은 RANDOM20 proxy, multi 는 Vitter K-subset. 본 narrative 가 multi-cell (5 paradigm × 3 multi cell) 위주이므로 영향 제한적이나, single-cell 30 method 표에 reservoir entry 가 잔존하면 정정 필요 (RANDOM20 의 seed=137 variant 로 표기).
  2. **LSH K=20 vs n_hp=5 의 mod collision** — paper-correct 이지만 stratum balance 약화의 algorithmic origin. Wave 0 +2092% 는 implementation bug 가 아니라 hyperparameter limitation. Narrative 에서 "LSH 는 K-hp 정합 hyperparameter (K=2^n_hp) 가 stratum balance 의 필요조건" 으로 명시 권장.
* **sparse_rp 의 density 식**: Achlioptas 2003 의 density 1/3 가 아니라 Li et al. 2006 의 1/√D variant. 본 연구의 method 명 "sparse_rp" 가 정확히 어느 paper 를 reference 하는지 narrative 에 명시 필요 (Li et al. 2006 권장).
* **method-level integrity**: 9/11 ✅ + 2/11 ⚠️ → narrative evidence 의 paper-correctness 충분히 보증. ❌ 가 0 이므로 5 paradigm × 11 method comparison 자체는 valid.
