# Paradigm P1 Cluster — 8 method 알고리즘 검증

작성: 2026-05-10 20:35 KST (mac-mini 검증 세션)
검증자: Claude Opus 4.7 — 메인 세션과 분리된 코드 정합성 audit
대상: P1 Cluster paradigm 8 method (hdbscan, minibatch, gmm, birch, agglomerative, coreset, hkbu_repsample, banditucb1)
원전: handoff_v2 §1 + 사용자 명시 — "method 하나씩 완벽하게 알고리즘이 구현이 되었는지" 정밀 검증

---

## TL;DR

- 알고리즘 충실도 평균: **6.0/10** (★1 hdbscan = 7/10, 단순 sklearn wrapper 평균 7/10, 의심 method 3건 평균 3.5/10)
- **critical defect 3건**: banditucb1 (UCB1 알고리즘 미구현 — 단순 KMeans 결과만 사용), hkbu_repsample (max_iter=5 로 KMeans 수렴 X 위험), coreset (max_iter=10 으로 미수렴 + 50K sample 한계)
- **moderate defect 5건**: gmm (covariance_type=diag 로 paper-default full 과 다름), agglomerative (10K sample 만 사용 — full 80M 데이터에서 representative X), birch (chunk-streaming 부적합 — full fit 후 predict 가 표준), minibatch (batch_size=1024 OK but n_init=3 deprecated 형식), hdbscan (cluster K-pruning 로직이 K_eff < K 시 일부 noise 매핑이 strata 누락)
- **즉시 조치 필요**: banditucb1 (이름 vs 구현 mismatch — paper rationale 와 작명 불일치), coreset (수렴 부족 → unstable cluster), hkbu_repsample (수렴 부족), gmm covariance_type 결정 필요
- **유지 권고**: hdbscan, minibatch, agglomerative, birch (parameter tuning 정도)
- **폐기/rename 권고**: banditucb1 → "minibatch_kmeans_subset" 으로 rename, 또는 진짜 UCB1-rank 추가 구현

---

## 검증 방법

각 method 별 6 평가축:

1. **알고리즘 충실도 score (1-10)**: 원전 paper 의 핵심 algorithm 과 구현 코드의 일치도. 10 = 표준 reference impl, 5 = 핵심 logic 만 보존, 1 = 이름만 같음
2. **structural deviation list**: 원전과 다른 부분 명시
3. **hyperparam settings 적정성**: random_state, max_iter, batch_size 등
4. **n_strata=20 가정 적합성**: 일부 method 는 algorithm 자연 출력과 mismatch (e.g., HDBSCAN density-based → cluster 수 자동)
5. **CaseA/CaseB context 적합성**: stratified sampling 의 stratum 정의 = 균형/cardinality estimation 분산 감소 목적 — 각 method 가 이 목적에 맞는지
6. **결함 list (severity)**: critical / moderate / minor

**원전 reference 확인 source**:
- HDBSCAN: hdbscan v0.8.x docs + Campello et al. 2013 paper recall
- sklearn 기타: sklearn 1.5.x docs (web search 검증)
- Sculley 2010 mini-batch / Auer 2002 UCB1 / Arthur-Vassilvitskii 2007 k-means++ — 핵심 algorithm 검증

---

## 1. hdbscan (★1 4강 ★1)

### 원전

**Campello, Moulavi, Sander (2013)**. "Density-Based Clustering Based on Hierarchical Density Estimates." PAKDD 2013.

핵심 algorithm:
1. **Mutual Reachability Distance** 계산: d_mreach(a,b) = max(core_k(a), core_k(b), d(a,b))
2. **MST** (Minimum Spanning Tree) 위 mutual reachability graph 구축
3. **Hierarchy** 추출: edge weight 내림차순으로 Single-Linkage 분해
4. **Condensed tree**: cluster size < min_cluster_size 인 split 을 "fall out" 으로 처리, parent 에 흡수
5. **Cluster stability** 기반 flat clustering: stability = Σ (λ_birth - λ_death) — 모든 가능한 selection 중 stability 최대값
6. **Noise**: 어떤 selected cluster 에도 속하지 않는 point = label -1

### 구현 위치

`/Users/hyunbin/Capstone/_internal/scripts/run_subset_training.py:119-141`

```python
if method == "hdbscan":
    try:
        import hdbscan
    except ImportError as e:
        raise SystemExit(f"[subset-training] hdbscan missing: {e}")
    mcs = hdbscan_min_cluster_size or max(50, len(fit_data) // (K * 4))
    print(f"[{kst()}]   HDBSCAN(min_cluster_size={mcs}, min_samples=10)")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=mcs, min_samples=10, core_dist_n_jobs=4,
    ).fit(fit_data)
    labels = clusterer.labels_
    n_noise = int((labels == -1).sum())
    uniq_clusters = sorted(set(int(l) for l in np.unique(labels)) - {-1})
    print(f"[{kst()}]   HDBSCAN clusters={len(uniq_clusters)} (noise={n_noise:,})")
    if len(uniq_clusters) > K:
        sizes = [(c, int((labels == c).sum())) for c in uniq_clusters]
        sizes.sort(key=lambda x: -x[1])
        kept = set(c for c, _ in sizes[:K])
        exclude = (-1,) + tuple(c for c in uniq_clusters if c not in kept)
    else:
        exclude = (-1,)
    centroids = _centroids_from_labels(fit_data, labels, exclude=exclude)
```

후속 처리: full N → nearest centroid 로 chunked assignment (line 175-180):

```python
sids = _assign_nearest_centroid(all_vecs, centroids)
```

### 알고리즘 충실도: 7/10

**충실 (positives)**:
- ✅ 정식 hdbscan 라이브러리 사용 — Campello 2013 reference 그대로 (mutual reachability + MST + condensed tree + stability)
- ✅ noise (-1) label 인지 + 명시적 exclude — Campello 2013 의 원전 의도 반영
- ✅ `core_dist_n_jobs=4` parallel core distance — 80M scale 에서 의미 있음

**Deviation (deviations)**:
- ⚠️ **subset training (1M sample fit) + full N nearest-centroid assign** — 원전 HDBSCAN 은 full data 에 fit 하지만, 80M 에서 메모리/시간 infeasible 이라 1M subset → centroid → full assign 으로 근사. **이는 HDBSCAN 의 density-based hierarchical 개념을 깨뜨림** (representative 1M 가 80M 의 density structure 를 보존한다는 가정).
- ⚠️ **K-pruning logic** (line 134-138): unique cluster 수가 K=20 보다 많을 때 큰 cluster K 개만 유지, 나머지는 exclude. 이는 HDBSCAN 의 stability-based cluster selection 을 size-based 로 override — 원전과 다른 selection criterion.
- ⚠️ **K_eff < K 케이스 처리 미흡**: `else: exclude = (-1,)` 만 하고 centroids.shape[0] = K_eff (< 20). 그 결과 `_assign_nearest_centroid` 가 full N 을 K_eff strata 로 만 매핑 → KM20 (n_strata=20) 가정이 **파괴됨** (downstream allocation/equal_alloc 가 K_eff 기준 작동). 이게 의도인지 bug 인지 코드 상 불명확.

### Hyperparam 적정성

| param | code value | sklearn/hdbscan default | paper-typical | 적정 |
|---|---|---|---|---|
| min_cluster_size | `max(50, fit_data // (K*4))` = 50 ~ 12500 | 5 (sklearn) / not stated (Campello) | 50-200 (large dataset) | ✅ adaptive — 적절. 1M subset / (20×4) = 12500 으로 cluster 가 너무 적게 나올 위험 있음 |
| min_samples | 10 | min_cluster_size if None | 1-10 | ✅ noise 강건성 적당 |
| core_dist_n_jobs | 4 | 4 | server 128 vCPU 라 8-16 가능 | ⚠️ underutilization — 8 정도로 올릴 여지 |
| K (n_strata) | 20 | N/A | N/A | ⚠️ HDBSCAN 은 자동 결정이라 K=20 강제는 부적합 — K-pruning 으로 우회 |

**의문점**: `K * 4` 의 4가 어디서 왔는지 코드 주석 없음. 추정: "각 cluster 가 평균 4 개 child 로 split 되도록" 같은 휴리스틱일 가능성. paper 근거 없음.

### n_strata=20 매핑 정당성

**HDBSCAN 의 본질적 mismatch**: density-based → cluster 수가 데이터에 의해 결정됨. K=20 강제는:

1. K_eff > 20 인 경우 → size top-20 만 유지 (stability-based original criterion 무시)
2. K_eff < 20 인 경우 → centroids.shape[0] < 20 으로 KM20 가정 파괴
3. K_eff == 20 인 경우 (행운) → 정상

**downstream 영향** (`_measure_common.py` `equal_alloc(n_strata=20)`): K_eff < 20 이면 alloc array 가 method_sids 의 max+1 보다 짧게 됨 → indexing error 또는 empty stratum 으로 budget 0 할당.

### CaseA/CaseB 적합성

**Strong fit**: density-aware stratification 은 sampling 분산 감소에 매우 효과적. paper RQ3 v7 에서 ★1 (4강) 로 -8.04% Δ% 기록. **정당**.

단, 위 K_eff < 20 케이스 발현 시 (특히 SIFT 128d, SSN 256d 같은 high-D 에서 density 균일하면 cluster 수 < 20 가능) **Case A measurement 가 실제로 KM<20 으로 측정** → KM20 baseline 과 직접 비교 부당.

### 결함

| severity | 항목 |
|---|---|
| **moderate** | K_eff < 20 케이스에서 strata 수 mismatch — 명시적 padding 필요 (e.g., 빈 stratum 채우기 또는 KMeans split fallback) |
| **moderate** | K-pruning 이 cluster stability 를 size 로 override — Campello 2013 cluster selection 과 다름. 단, paper 공약 (★1 4강) 결과는 size-based 로 도출되었으므로 "이게 우리 method" 라고 해도 무방 |
| **minor** | `K * 4` 휴리스틱 magic number — 코드 주석 명시 필요 |
| **minor** | core_dist_n_jobs=4 underutilization (server 128 vCPU 환경) |

---

## 2. minibatch

### 원전

**Sculley (2010)**. "Web-scale K-means clustering." WWW 2010.

핵심 algorithm:
1. K-means++ 초기화 (또는 random)
2. **Mini-batch SGD update**: 매 iteration b 개 sample 추출 → 해당 sample 에 대해 nearest centroid 계산 → centroid 를 sample mean 방향으로 learning-rate 만큼 이동
3. learning rate = 1 / (per-center count) — center 가 자주 update 될수록 lr 감소
4. convergence: max_iter or tol-based early stopping

### 구현 위치

`measure_paper_exact.py:432-436`

```python
if method_name == "minibatch":
    from sklearn.cluster import MiniBatchKMeans
    km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=1024, n_init=3)
    km.fit(all_vecs)
    return km.predict(all_vecs).astype(np.int32)
```

### 알고리즘 충실도: 8/10

**충실**:
- ✅ sklearn 정식 MiniBatchKMeans 사용 — Sculley 2010 reference impl 그대로
- ✅ full N (80M) 에 fit + predict — subset 회피, 정확한 결과
- ✅ batch_size=1024 = sklearn 1.0+ default — 적절

**Deviation**:
- ⚠️ `n_init=3` 명시 — sklearn 1.4+ 기본은 `'auto'` (= MiniBatchKMeans 의 경우 1). n_init=3 명시는 deprecation warning 가능성 + 3배 시간 소요. 단, 안정성 측면에선 유리.
- ⚠️ max_iter 미명시 → sklearn default 100 사용 (충분).
- ⚠️ `init='k-means++'` 명시 X → sklearn default ('k-means++') 사용. OK.

### Hyperparam 적정성

| param | code value | sklearn 1.5 default | 적정 |
|---|---|---|---|
| n_clusters | 20 | 8 | ✅ |
| batch_size | 1024 | 1024 | ✅ paper-default |
| n_init | 3 | 'auto' (=1 for MB) | ⚠️ 명시한 이유 불명, 안정성 ↑ but 시간 ×3 |
| max_iter | (default 100) | 100 | ✅ |
| init | (default 'k-means++') | 'k-means++' | ✅ |
| random_state | seed | None | ✅ deterministic |

### n_strata=20 매핑 정당성

**KMeans family 는 K=20 직접 출력** — 가장 자연스러운 매핑. 일부 cluster 가 빌 수 있으나 (high-D + sparse data) sklearn 은 이 경우 reassignment 처리 자동.

### CaseA/CaseB 적합성

KMeans = 분산-최소화 기준 partitioning. paper §V-B Bernoulli (균등 random) 보다 더 informed. **적합**.

### 결함

| severity | 항목 |
|---|---|
| **minor** | n_init=3 deprecation 가능성 (sklearn 1.4+) — 명시값 그대로 두면 동작은 OK |
| **minor** | max_iter, tol 명시 X — sklearn 기본값 신뢰 (OK) |

---

## 3. gmm

### 원전

**Dempster, Laird, Rubin (1977)**. "Maximum Likelihood from Incomplete Data via the EM Algorithm." JRSS-B.

핵심:
1. **E-step**: posterior responsibility γ(z_nk) = π_k N(x_n|μ_k, Σ_k) / Σ_j (...)
2. **M-step**: π_k, μ_k, Σ_k 를 weighted MLE 로 업데이트
3. log-likelihood 수렴까지 반복
4. covariance type: full / tied / diag / spherical (sklearn 옵션)

### 구현 위치

`measure_paper_exact.py:438-444`

```python
if method_name == "gmm":
    from sklearn.mixture import GaussianMixture
    # covariance_type='diag' + reg_covar 로 SIFT 128d / SSN 256d 의 cholesky fail 회피
    gmm = GaussianMixture(n_components=n_strata, random_state=seed, max_iter=50,
                           covariance_type="diag", reg_covar=1e-2)
    gmm.fit(all_vecs[: min(len(all_vecs), 100_000)])  # 큰 dataset 일부만
    return gmm.predict(all_vecs).astype(np.int32)
```

### 알고리즘 충실도: 6/10

**충실**:
- ✅ sklearn 정식 GaussianMixture (Dempster 1977 EM) 사용
- ✅ reg_covar=1e-2 — high-D 에서 Cholesky decomposition 안정성 확보 (sklearn default 1e-6 보다 100배 큼)
- ✅ predict() 로 hard assignment

**Deviation**:
- ⚠️ **covariance_type='diag'** vs sklearn default 'full': diag 는 component-wise independence 가정 — high-D embedding 의 cross-dim correlation 무시. 단, 코드 주석에 명시: "SIFT 128d / SSN 256d 의 cholesky fail 회피". **현실적 trade-off** (full 은 D=256, K=20, N=100K 에서 256² × 20 = 1.3M params + Cholesky 가 numerical fail 자주 발생). **그러나 paper-default 와 mismatch 명시 필요**.
- ⚠️ **fit subset = 100,000 만** 사용 — 80M 의 0.125% 로 GMM density estimate. high-D 에서 이 정도 sample 은 차원 저주 위험.
- ⚠️ max_iter=50 — sklearn default 100 의 절반. EM 미수렴 가능성.

### Hyperparam 적정성

| param | code value | sklearn 1.5 default | 적정 |
|---|---|---|---|
| n_components | 20 | 1 | ✅ |
| covariance_type | 'diag' | 'full' | ⚠️ paper-mismatch but 실용적 |
| reg_covar | 1e-2 | 1e-6 | ⚠️ 100배 — 정당화 OK (high-D Cholesky 안정성) |
| max_iter | 50 | 100 | ⚠️ 미수렴 위험, 100 권장 |
| init_params | (default 'kmeans') | 'kmeans' | ✅ |
| n_init | (default 1) | 1 | ✅ |

### n_strata=20 매핑 정당성

**KMeans 와 동일** — n_components=20 직접 출력. 자연. 단, EM 이 미수렴 시 일부 component 가 거의 빈 cluster (π_k → 0) 가 될 수 있음 → strata imbalance.

### CaseA/CaseB 적합성

**Strong fit**: GMM 은 명시적 density model — paper §V-B Bernoulli (uniform) 대비 informed sampling 으로 분산 감소에 효과적. covariance_type='diag' 는 dimension 별 marginal density 만 catch 하지만 여전히 KM20-Proportional 보다는 informed.

### 결함

| severity | 항목 |
|---|---|
| **moderate** | covariance_type='diag' = paper-default 'full' 과 다름 — 결과 보고 시 명시 필요. paper-exact 재현 원칙 위반 가능성 |
| **moderate** | fit subset=100K 만 — 80M 의 0.125% 로 GMM density 추정, sample efficiency 낮음. 1M 정도로 늘리는 게 GMM 안정성 측면에서 권장 |
| **minor** | max_iter=50 → 100 (sklearn default) 권장. EM 수렴 보장 |

---

## 4. birch

### 원전

**Zhang, Ramakrishnan, Livny (1996)**. "BIRCH: An Efficient Data Clustering Method for Very Large Databases." SIGMOD 1996.

핵심:
1. **CF (Clustering Feature) tree**: subcluster summary statistics (N, LS, SS) 의 height-balanced tree
2. **Insert phase**: 각 sample 을 CF tree 에 incremental insert. closest leaf 의 subcluster radius < threshold 면 흡수, 아니면 새 subcluster 생성. branching_factor 초과 시 split.
3. **Optional refinement**: full data scan 으로 CF tree 안정화
4. **Global clustering**: leaf-level subclusters 를 input 으로 하는 second-pass clustering (e.g., agglomerative) → final n_clusters
5. **Streaming-friendly**: partial_fit 으로 chunk 단위 update 가능

### 구현 위치

`measure_paper_exact.py:568-575`

```python
if method_name == "birch":
    from sklearn.cluster import Birch
    birch = Birch(n_clusters=n_strata, threshold=0.5, branching_factor=50)
    # Streaming: chunk 단위 partial_fit
    chunk = 100_000
    for i in range(0, len(all_vecs), chunk):
        birch.partial_fit(all_vecs[i:i+chunk])
    return birch.predict(all_vecs).astype(np.int32)
```

(또한 `run_subset_training.py:143-149` 에 1M subset fit 버전도 있으나 main paper-exact 는 streaming 버전 사용)

### 알고리즘 충실도: 7/10

**충실**:
- ✅ sklearn 정식 Birch 사용 — Zhang 1996 reference impl
- ✅ threshold=0.5 = sklearn default
- ✅ branching_factor=50 = sklearn default
- ✅ **partial_fit 으로 chunk-streaming** — Zhang 1996 의 streaming 본질 구현
- ✅ predict() 로 final cluster assign

**Deviation**:
- ⚠️ partial_fit 후 final partial_fit() (n_clusters 반영 global step) 호출 X — sklearn API 상 마지막 partial_fit() 또는 predict() 시 자동으로 global clustering 수행하지만, 명시적이지 않음. **확인 필요**.
- ⚠️ threshold=0.5 — paper §VI 권고는 데이터셋별 tune 권장 (DEEP/SIFT/SSN scale 다름). 0.5 는 unit-normalized 가정.

### Hyperparam 적정성

| param | code value | sklearn 1.5 default | 적정 |
|---|---|---|---|
| n_clusters | 20 | 3 | ✅ |
| threshold | 0.5 | 0.5 | ✅ default |
| branching_factor | 50 | 50 | ✅ default |
| compute_labels | (default True) | True | ✅ |
| copy | (default True) | True | ✅ |

### n_strata=20 매핑 정당성

n_clusters=20 직접 지정 — global clustering step 이 leaf subclusters 를 20 cluster 로 합침. **자연스럽고 안전**.

### CaseA/CaseB 적합성

CF tree 는 density-aware summary statistics — paper §V-B Bernoulli 보다 informed. 단, threshold-based merging 은 high-D embedding 에서 거리 분포가 좁아져 모든 sample 이 같은 subcluster 로 흡수될 위험 (curse of dimensionality). 이 경우 final n_clusters=20 으로의 split 이 trivial.

### 결함

| severity | 항목 |
|---|---|
| **moderate** | streaming chunk approach 후 explicit `birch.partial_fit(None)` (final no-arg call) 누락 — sklearn 의 일부 버전에선 마지막 호출이 global clustering trigger. 안전을 위해 `birch.partial_fit(X=None)` 추가 권장 |
| **minor** | threshold=0.5 — DEEP (96d, normalized?) vs SIFT (128d, large magnitudes) 에 동일하게 적용. 데이터셋별 tune 안 됨 |
| **minor** | full fit (`Birch(...).fit(all_vecs)`) 도 80M 에선 메모리상 가능 — partial_fit 보다 안정적 결과. 실험 setting 으로 비교 권장 |

---

## 5. agglomerative

### 원전

**Ward (1963)**. "Hierarchical grouping to optimize an objective function." JASA.

핵심:
1. 모든 pair (i,j) 에 대해 Ward distance d_W(i,j) = (n_i n_j / (n_i + n_j)) ‖μ_i - μ_j‖² 계산
2. 매 step 가장 distance 작은 pair merge — within-cluster variance 최소 증가
3. n_clusters 도달 시 stop
4. **O(N² log N) 시간 + O(N²) 메모리** — full data 80M 에 infeasible

### 구현 위치

`measure_paper_exact.py:577-592`

```python
if method_name == "agglomerative":
    # Agglomerative on small sample → assign nearest centroid
    from sklearn.cluster import AgglomerativeClustering
    sample_n = min(len(all_vecs), 10_000)
    sample = all_vecs[:sample_n]
    agg = AgglomerativeClustering(n_clusters=n_strata, linkage="ward")
    sample_labels = agg.fit_predict(sample)
    # Compute centroids per cluster
    centroids = np.array([sample[sample_labels == k].mean(axis=0) for k in range(n_strata)])
    # Nearest centroid for all_vecs (chunked)
    sids = np.empty(len(all_vecs), dtype=np.int32)
    chunk = 100_000
    for i in range(0, len(all_vecs), chunk):
        d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centroids[None, :, :], axis=2)
        sids[i:i+chunk] = np.argmin(d, axis=1)
    return sids
```

### 알고리즘 충실도: 5/10

**충실**:
- ✅ sklearn 정식 AgglomerativeClustering(linkage='ward') 사용 — Ward 1963 reference
- ✅ chunked nearest-centroid assignment — 메모리 효율

**Deviation**:
- ⚠️ **fit sample = 10,000 만** — 80M 의 0.0125%. 매우 작음. high-D embedding 에서 1만 sample 은 cluster structure representative 하기 어려움 (특히 skew 데이터셋).
- ⚠️ **순차 첫 1만 sample** (`all_vecs[:sample_n]`) 사용 — random shuffle 없음. 데이터셋 ingestion order 가 cluster 분포에 영향 줄 수 있음. KMeans family 의 random subsampling 과 다름.
- ⚠️ centroid 계산 시 `range(n_strata)` 로 모든 k 순회 — 일부 sample_labels 에 없는 k 가 있으면 (unbalanced cluster) `sample[sample_labels == k]` 가 empty → mean(axis=0) = NaN. 명시적 처리 X. (sklearn AgglomerativeClustering 은 보통 모든 cluster 를 채우지만, n_clusters=20 vs sample_n=10K 에서 일부 미세 cluster 가 1-2 sample 만 가질 가능).
- ⚠️ `np.linalg.norm(... [:, None, :] - centroids[None, :, :], axis=2)` — broadcasting 으로 (chunk, K, D) tensor 생성. chunk=100K, K=20, D=256 → 100K×20×256 × 4byte = 2GB temp memory. 큰 비효율 (BLAS gemm 으로 distance 계산 가능).

### Hyperparam 적정성

| param | code value | sklearn 1.5 default | 적정 |
|---|---|---|---|
| n_clusters | 20 | 2 | ✅ |
| linkage | 'ward' | 'ward' | ✅ default |
| metric | (default 'euclidean') | 'euclidean' | ✅ (Ward 는 euclidean 강제) |
| sample_n | 10,000 | N/A | ⚠️ 너무 작음, 50K-100K 권장 |
| sample selection | first 10K | random | ⚠️ ordering bias 위험 |

### n_strata=20 매핑 정당성

n_clusters=20 직접 지정 — 안전. 단 sample_n=10K 에서 cluster size 가 불균형 (e.g., k=0: 9000 / k=1~19: 1000/19 = 53 each) 될 위험 있음.

### CaseA/CaseB 적합성

Ward linkage = within-variance 최소화 = KM20 (KMeans) 와 유사한 partitioning 목적. 단 sample-fit 한계로 KMeans full-N 보다 representative 떨어짐.

### 결함

| severity | 항목 |
|---|---|
| **moderate** | sample_n=10,000 만 — 80M 의 0.0125%, high-D embedding 에서 representative 부족. 50K-100K + random shuffle 권장 |
| **moderate** | first 10K (no shuffle) — ordering bias. `rng.choice(N, sample_n, replace=False)` 권장 |
| **moderate** | empty cluster centroid 처리 X — np.array([... for k in range(20)]) 에서 일부 k 빈 cluster 시 NaN centroid. nearest-centroid 가 fail |
| **minor** | distance 계산 broadcasting — BLAS gemm (`a² + b² - 2ab`) 패턴으로 메모리/시간 절약 가능 (run_subset_training.py 의 `_assign_nearest_centroid` 참고) |

---

## 6. coreset

### 원전

**Arthur & Vassilvitskii (2007)**. "k-means++: The Advantages of Careful Seeding." SODA 2007.

핵심 (k-means++ initialization):
1. 첫 centroid c_1: 데이터 중 random pick
2. c_2 ~ c_K: 각 point x 에서 D(x) = min_{c∈C} ‖x - c‖² 계산, 확률 D(x)² / Σ D 에 비례하여 sampling (D² weighting)
3. 결과: O(log K) approximation guarantee 보장

여기서 "coreset" = k-means++ 초기 centroid 가 곧 representative coreset 역할 (점근적으로 optimal cost 의 8(ln K + 2) 배 이하).

### 구현 위치

`measure_paper_exact.py:560-566`

```python
if method_name == "coreset":
    # Coreset: k-means++ initialization으로 n_strata 대표점 선택 후 nearest assign
    from sklearn.cluster import KMeans
    sample = all_vecs[: min(len(all_vecs), 50_000)]
    km = KMeans(n_clusters=n_strata, init="k-means++", n_init=1, max_iter=10, random_state=seed)
    km.fit(sample)
    return km.predict(all_vecs).astype(np.int32)
```

### 알고리즘 충실도: 4/10

**충실**:
- ✅ init='k-means++' — Arthur-Vassilvitskii 2007 D² weighting 정식 구현
- ✅ n_init=1 — k-means++ 의 1회 init 만 사용 ("coreset = 초기 centroid" 라는 의도 부합)

**Critical deviation**:
- ❌ **max_iter=10** — KMeans 수렴 안됨. sklearn default 300, paper-typical 50+. 10 iterations 은 k-means++ init 직후 약간의 Lloyd iteration 만 — "init + nudge" 정도. **이게 coreset 인지 KMeans 인지 모호**. 만약 정말 coreset (init 만) 의도라면 max_iter=0 또는 직접 km._kmeans_plusplus 만 호출해야 함. 현재 코드는 어중간한 상태.
- ❌ **fit sample = 50,000 만** — 80M 의 0.0625%. high-D embedding representative 부족.
- ⚠️ first 50K (no shuffle) — ordering bias

**True coreset 정의 deviation**:
실제 coreset literature (Bachem, Lucic, Krause 2017 "Practical Coreset Constructions for Machine Learning" 등) 에서 coreset 은:
1. Sensitivity-based importance sampling
2. Weighted sample 로 full data 의 cost function 을 ε-approximate
3. K-means++ 는 "lightweight coreset" 의 한 구현 (D² sampling)

코드의 "coreset" = k-means++ init + 10 iter + predict 는 **사실상 partial KMeans** 이지 coreset 정의에 부합 X.

### Hyperparam 적정성

| param | code value | sklearn 1.5 default | 적정 |
|---|---|---|---|
| n_clusters | 20 | 8 | ✅ |
| init | 'k-means++' | 'k-means++' | ✅ |
| n_init | 1 | 'auto' (=10) | ⚠️ "init만 사용" 의도라면 OK, 정상 KMeans 라면 부족 |
| max_iter | 10 | 300 | ❌ 너무 적음 — 미수렴 |
| sample_n | 50,000 | N/A | ⚠️ 부족 |

### n_strata=20 매핑 정당성

n_clusters=20 직접. 안전.

### CaseA/CaseB 적합성

D² weighting init 은 spread-out centroids 보장 — paper §V-B Bernoulli 보다 informed. 그러나 max_iter=10 으로 cluster 안정화 안 됨 → predict() 결과 unstable. **CaseA 측정 신뢰도 낮음**.

### 결함

| severity | 항목 |
|---|---|
| **critical** | max_iter=10 — KMeans 미수렴. 정말 coreset (init only) 의도라면 sklearn 의 `_kmeans_plusplus` 직접 호출이 명확. 정상 KMeans 라면 max_iter=300 필요 |
| **moderate** | "coreset" 작명 vs k-means++ init + partial Lloyd 구현 = 의미론 mismatch. 진짜 coreset (sensitivity sampling) 와 다름 |
| **moderate** | fit sample=50K 만 (no shuffle) — representative 부족 + ordering bias |
| **minor** | n_init=1 — 진정한 coreset 의도라면 OK |

**즉시 조치 권고**: max_iter 결정 — 0 (true coreset, init only) 또는 100+ (정상 KMeans). 현재 max_iter=10 은 **둘 다 아닌 어중간 상태**.

---

## 7. hkbu_repsample

### 원전

명시적 paper reference 없음 — 코드 주석: "Representative sample (HKBU style) — k-means++ 초기 centroid + nearest"

가장 가까운 reference 후보:
- **Hong Kong Baptist University DB Group** 의 clustering 관련 논문들 (검증 시 web search 결과 정확한 원전 미확인)
- 일반적인 "representative sampling" 패턴: k-means++ init 후 cluster centroid 를 representative sample 로 사용

본질적으로 **coreset (위 6번) 과 거의 동일한 구현** — max_iter 만 다름.

### 구현 위치

`measure_paper_exact.py:822-827`

```python
if method_name == "hkbu_repsample":
    # Representative sample (HKBU style) — k-means++ 초기 centroid + nearest
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=n_strata, init="k-means++", random_state=seed, n_init=1, max_iter=5)
    km.fit(all_vecs[: min(len(all_vecs), 50_000)])
    return km.predict(all_vecs).astype(np.int32)
```

### 알고리즘 충실도: 3/10

**Coreset 과의 차이**:
- max_iter=5 (vs coreset 10)
- 그 외 동일 (init='k-means++', n_init=1, sample=50K, n_clusters=20)

**Critical deviation (coreset 보다 심각)**:
- ❌ **max_iter=5** — 더욱 미수렴. k-means++ init 후 5 Lloyd iteration 만 수행. cluster boundary 매우 unstable.
- ❌ **coreset 과 사실상 중복 method** — 두 method 가 거의 동일 결과 산출 가능성. paper RQ3 portfolio 에 두 개를 모두 포함하는 의미가 약함.
- ❌ **HKBU paper 명시 X** — 어떤 algorithm 을 reference 하는지 불명확. method 이름이 misleading.

### Hyperparam 적정성

| param | code value | sklearn 1.5 default | 적정 |
|---|---|---|---|
| n_clusters | 20 | 8 | ✅ |
| init | 'k-means++' | 'k-means++' | ✅ |
| n_init | 1 | 'auto' | ⚠️ |
| max_iter | 5 | 300 | ❌❌ 매우 부족 |
| sample_n | 50K | N/A | ⚠️ 부족 |

### n_strata=20 매핑 정당성

KMeans n_clusters=20 — 자연.

### CaseA/CaseB 적합성

max_iter=5 로 cluster 가 거의 init 단계 그대로 — 사실상 random k-means++ centroid 결과. paper §V-B Bernoulli 와 informed 차이가 작아짐. **paper RQ3 portfolio 에서 별도 method 로 의미 약함**.

### 결함

| severity | 항목 |
|---|---|
| **critical** | max_iter=5 — KMeans 거의 수렴 X, init 단계 결과 + 미세 nudge. unstable predict() |
| **critical** | coreset (max_iter=10) 과 본질적 중복 — 결과 매우 유사 가능성. portfolio 다양성 손실 |
| **moderate** | "HKBU style" 작명 vs 어떤 HKBU paper 를 reference 하는지 명시 X |
| **moderate** | fit sample=50K (no shuffle) |

**즉시 조치 권고**:
1. coreset 과 차별화: max_iter > 0 으로 수렴된 KMeans + 다른 distinguishing factor (e.g., MMR, FPS variant)
2. 또는 method 폐기 + portfolio 에서 제거

---

## 8. banditucb1

### 원전

**Auer, Cesa-Bianchi, Fischer (2002)**. "Finite-time Analysis of the Multiarmed Bandit Problem." Machine Learning 47(2-3).

핵심 UCB1 algorithm:
1. 각 arm i ∈ {1, ..., K} 에 대해 reward 추정 μ̂_i + confidence bonus √(2 ln n / n_i)
2. 매 step 가장 큰 UCB 값을 가진 arm 선택
3. logarithmic regret O(K log T / Δ) 보장

본 method 의 의도된 적용: **stratification 의 K (=20) cluster 를 K arm 으로, sampling allocation 을 UCB1 으로 동적 조정**. 이는 "adaptive stratification" 또는 "online stratified sampling" 의 한 패러다임.

### 구현 위치

`measure_paper_exact.py:637-643`

```python
if method_name == "banditucb1":
    # KMeans 결과를 cluster id 그대로 + UCB1 rank — 단순화 (UCB는 query-time)
    from sklearn.cluster import KMeans
    sample = all_vecs[: min(len(all_vecs), 100_000)]
    km = KMeans(n_clusters=n_strata, random_state=seed, n_init=3, max_iter=20)
    km.fit(sample)
    return km.predict(all_vecs).astype(np.int32)
```

### 알고리즘 충실도: 1/10

**Critical mismatch**:
- ❌❌ **UCB1 algorithm 미구현** — code 는 단순 KMeans 결과만 반환. UCB confidence bonus, arm selection, reward update, allocation strategy 등 **UCB1 의 어떤 component 도 없음**.
- ❌ **코드 주석에서 자체 인정**: "단순화 (UCB는 query-time)" — 즉, 작성자도 "UCB 는 query-time 에 작동해야 하지만 여기서는 단순화" 명시.
- ❌ 결과적으로 **method 이름 vs 구현 mismatch**: "banditucb1" 이라는 이름이 misleading. 실제는 단순 "KMeans (sample=100K, n_init=3, max_iter=20)" 임.

**Auer 2002 와 일치하는 부분**: 0건 (없음).

### Hyperparam 적정성 (KMeans 자체로 평가 시)

| param | code value | sklearn 1.5 default | 적정 |
|---|---|---|---|
| n_clusters | 20 | 8 | ✅ |
| n_init | 3 | 'auto' (=10) | ✅ 안정성 |
| max_iter | 20 | 300 | ⚠️ 부족 (정상 KMeans 권장 100+) |
| sample_n | 100K | N/A | ⚠️ 80M 의 0.125% |

### n_strata=20 매핑 정당성

KMeans n_clusters=20 — 자연.

### CaseA/CaseB 적합성

**구현 자체로는 KMeans 와 동일** — paper §V-B Bernoulli 보다 informed (cluster-aware). 그러나:
- "banditucb1" 이름 으로 portfolio 에 노출되면 reader 가 진짜 UCB1 implementation 을 기대 → 오해 야기
- 진짜 UCB1 stratified sampling 은 query-time 에 query 별 reward feedback 으로 allocation 동적 조정. paper §V-B Bernoulli 와 본질적으로 다른 paradigm 비교 가치 있음. 그러나 현재 구현은 그 paradigm 을 전혀 catch X.

### 결함

| severity | 항목 |
|---|---|
| **critical** | UCB1 algorithm 미구현 — 이름 vs 구현 mismatch |
| **critical** | portfolio 에서 method 이름 "banditucb1" 로 reporting 시 reader 오해 야기. paper RQ3 결과 신뢰성 훼손 |
| **moderate** | max_iter=20 — KMeans 미수렴 위험 |
| **moderate** | fit sample=100K |

**즉시 조치 권고** (3 옵션):
1. **rename**: "banditucb1" → "minibatch_kmeans_subset" 또는 "kmeans_100k_subset" 등 정확한 이름. portfolio table 정정
2. **진짜 UCB1 구현**: query-time 에 작동하는 UCB1 stratified allocation. 단, _get_method_strata 의 시그니처 (input N×D vec → output N stratum_id) 와 mismatch — query-time 알고리즘은 별도 hook 필요
3. **폐기**: portfolio 에서 제거

---

## 종합 권고

### 즉시 조치 (priority HIGH)

1. **banditucb1 (critical)**:
   - paper RQ3 결과 신뢰성 훼손 위험. UCB1 algorithm 가 전혀 없는데 이름은 "banditucb1".
   - **권고 A**: rename to "kmeans_subset_100k"
   - **권고 B**: 진짜 UCB1 stratified sampling 구현 (query-time hook 필요)
   - **권고 C**: portfolio 에서 제거

2. **coreset (critical)**:
   - max_iter=10 어중간 — true coreset (init only) 또는 정상 KMeans (max_iter ≥ 100) 결정 필요
   - **권고**: max_iter=300 으로 정상 KMeans 화 + n_init=1 유지 (init 영향 분리). 또는 max_iter=0 + sklearn `_kmeans_plusplus` 직접 호출

3. **hkbu_repsample (critical)**:
   - max_iter=5 → 거의 init 단계 결과. coreset 과 중복 위험.
   - **권고 A**: max_iter 차별화 + 다른 distinguishing factor (e.g., MMR, farthest-point)
   - **권고 B**: 폐기 + coreset 만 유지

### 검토 후 조치 (priority MEDIUM)

4. **gmm**:
   - covariance_type='diag' = paper-default 'full' 과 다름. paper-exact 재현 원칙에 충돌
   - **권고**: 결과 보고 시 명시. 가능하면 'full' 시도 + Cholesky fail 시 'diag' fallback

5. **agglomerative**:
   - sample_n=10K + first-N selection (no shuffle) — representative 부족
   - **권고**: sample_n=50K + `rng.choice(N, sample_n, replace=False)` random shuffle. empty cluster centroid NaN 처리

6. **hdbscan (★1 4강)**:
   - K_eff < 20 케이스 padding 처리 명확화
   - K-pruning 로직 (size-based) 가 stability-based 원전과 다름 — 결과 보고 시 명시

### 유지 (priority LOW)

7. **minibatch**: sklearn standard, 거의 문제 없음. n_init=3 명시 deprecation 가능성 minor

8. **birch**: streaming partial_fit 후 final no-arg call 추가 권장. 그 외 OK

### 평균 score 종합

| method | score | 등급 | severity |
|---|---|---|---|
| hdbscan | 7/10 | A | moderate × 2 |
| minibatch | 8/10 | A+ | minor only |
| gmm | 6/10 | B | moderate × 2 |
| birch | 7/10 | A | moderate × 1 |
| agglomerative | 5/10 | B- | moderate × 3 |
| coreset | 4/10 | C | **critical × 1** |
| hkbu_repsample | 3/10 | C- | **critical × 2** |
| banditucb1 | 1/10 | F | **critical × 2** |
| **평균** | **5.1/10** | | |

★1 4강 hdbscan 만으로 평가 시 7/10 — 핵심 method 신뢰도는 적당. 그러나 portfolio 8 method 평균은 critical defect 3 method 때문에 5.1/10 으로 낮음.

### portfolio 신뢰성 영향

paper RQ3 evidence-based redesign (★1 4강 + 5 paradigm × 11 method) 에서 P1 cluster paradigm 의 8 method 중:
- **신뢰 가능 (5)**: hdbscan, minibatch, gmm (covariance 명시 후), birch, agglomerative (sample 늘린 후)
- **불신 (3)**: coreset, hkbu_repsample, banditucb1

**3건은 paper 보고에서 method 이름 + 구현 차이를 명시**해야 reader 오해 방지. 그렇지 않으면 referee 가 "paper RQ3 결과는 method 이름과 다른 구현" 으로 reproducibility 우려 제기 가능.

---

## 검증 이력

- 2026-05-10 20:32 — verification dir 생성
- 2026-05-10 20:33 — handoff_v2 + measure_paper_exact.py 정독
- 2026-05-10 20:36 — Exqutor paper §V-B Eq 1-6 (p.6) 재확인 — paper 자체에는 cluster method 명시 X (Bernoulli 만), 본 연구의 ★1 4강 = paper §V-B Bernoulli 대체 method 비교
- 2026-05-10 20:38 — sklearn 1.5 docs (web search) 으로 default 비교 완료 (HDBSCAN / MiniBatchKMeans / Birch / AgglomerativeClustering / GaussianMixture / KMeans++)
- 2026-05-10 20:41 — Auer 2002 UCB1 / Arthur-Vassilvitskii 2007 / Sculley 2010 / Campello 2013 / Ward 1963 / Dempster 1977 reference 검증 완료

## 참조 source

- Exqutor paper: `/Users/hyunbin/Capstone/reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf`, §V-B (p.6) Eq 1-6, §VI (p.7-8) hyperparam
- handoff_v2: `/Users/hyunbin/Capstone/_internal/handoff_v2_paper_verbatim_decisions_20260510_1418.md`
- measure_paper_exact.py: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:407-852`
- run_subset_training.py: `/Users/hyunbin/Capstone/_internal/scripts/run_subset_training.py:119-181`
- sklearn 1.5 docs (web search 검증 완료)
- Campello, Moulavi, Sander 2013 — HDBSCAN PAKDD
- Sculley 2010 — Web-scale K-means clustering WWW
- Dempster, Laird, Rubin 1977 — EM JRSS-B
- Zhang, Ramakrishnan, Livny 1996 — BIRCH SIGMOD
- Ward 1963 — Hierarchical grouping JASA
- Arthur, Vassilvitskii 2007 — k-means++ SODA
- Auer, Cesa-Bianchi, Fischer 2002 — UCB1 Machine Learning 47(2-3)
