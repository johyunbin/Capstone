# Paradigm P2 Spatial — 5 method 알고리즘 검증

**작성**: 2026-05-10 21:00 KST (P2 Spatial 검증 agent)
**검증 대상**: `_internal/scripts/measure_paper_exact.py` `_get_method_strata()` line 446-693
**원전**: 본 학술 문헌 5건 (Faloutsos & Roseman 1989 / Sivic & Zisserman 2003 / Bentley 1975 / Kulesza & Taskar 2012 / Haussler & Welzl 1987)
**비교 대조**: server-side `experiments/code/rq3/hilbert/hilbert_curve.py` + `kdtree/kdtree_partition.py` (raw 별도 구현)

---

## TL;DR

- **알고리즘 충실도 평균**: **3.4 / 10** (P1 Cluster 보다 현저히 낮음 — registry 5 method 중 4 method가 원전과 의미적으로 다른 단순화 적용)
- **발견된 critical defect**: 4건
  1. **hilbert (★3 4강)**: registry 구현이 진짜 Hilbert curve가 아닌 **PCA 2D linear order proxy** (`pca[:,0]*1000 + pca[:,1]` argsort) — 별도 raw 구현 (`hilbert_curve.py`)이 존재함에도 미사용 → ★3 -7.54% 결과의 학술 근거 결손
  2. **kdpp == epsilon_net 사실상 동일**: 두 method (line 619-635, 678-693) 가 단지 random seed 처리 1줄 차이 외 코드 100% 동일. k-DPP는 본래 determinantal kernel 기반 **probabilistic** sampling이 본질이고, ε-net은 deterministic farthest-first cover. paradigm 분리 정합성 위반
  3. **kdtree bucket 매핑 결함**: KDTree `query` 결과는 nearest-neighbor index (0~N-1 row index)인데 `idx % n_strata` 로 modulo → spatial locality 완전 파괴. 진짜 leaf id를 사용하면 **bucket 수가 50K samples 기반에서 일정치 않음** (sklearn KDTree leaf는 leaf_size 단위로 결정), 별도 raw 구현 (`kdtree_partition.py`)이 더 정확함에도 미사용
  4. **faiss_ivf train sample size**: 200K subset 후 `quantizer.search`는 IVFFlat clustering의 **non-trained centroid**를 호출 가능 (FAISS API 정확성 검증 필요) — 일부 코드 path에서 `index.train(train)` 후 `quantizer` 직접 search는 동작하나 의미적으로 train된 centroid 사용 정합성 모호

- **즉시 조치 필요 method (priority order)**:
  - **P0 (critical)**: `hilbert` — raw `hilbert_curve.py` 사용으로 교체 (1줄: `from hilbert.hilbert_curve import fit_hilbert_mapper, assign_hilbert`) → ★3 결과의 학술 정당성 회복
  - **P1**: `kdpp` 와 `epsilon_net` 차별화 (kdpp = MCMC/EVD-based DPP sampling으로 변경 또는 paradigm reshuffle)
  - **P2**: `kdtree` — raw `kdtree_partition.py` 사용 또는 leaf id를 직접 추출하는 코드로 교체

---

## 1. hilbert (★3 4강) — line 446-458

### 1.1 원전

**Hilbert 1891** ("Über die stetige Abbildung einer Linie auf ein Flächenstück", *Mathematische Annalen* 38) — 본 학술 문헌 곡선 정의: 단위 정사각형을 [0, 1] 구간에 연속적으로 1대1 매핑하는 space-filling curve. 재귀적 U-shape 4분할 회전.

**Faloutsos & Roseman 1989** ("Fractals for Secondary Key Retrieval", *PODS '89*) — DB에 Hilbert 도입한 본 학술 문헌. multidimensional → 1D mapping 시 **locality 보존 우수**. z-order 대비 spatial proximity 회복률 ~30% 우수.

**Lawder & King SIGMOD 2001** ("Querying Multi-dimensional Data Indexed Using the Hilbert Space-Filling Curve") — DB SIGMOD에서 Hilbert curve 인덱싱 표준 정립. n-D 좌표 → Hilbert distance algorithm: 2^p × 2^p grid에서 quadrant 회전/flip 으로 distance 계산.

**핵심 알고리즘** (Wikipedia Hilbert curve verbatim):
```
n = 2^p
function xy2d(x, y, p):
    d = 0
    s = n / 2
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s * ((3 * rx) XOR ry)
        if ry == 0:
            if rx == 1: x = s - 1 - x; y = s - 1 - y
            swap(x, y)
        s = s / 2
    return d
```

### 1.2 구현 위치 + 코드 발췌

**registry (`measure_paper_exact.py` line 446-458)**:
```python
if method_name == "hilbert":
    sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/hilbert")
    # run_hilbert.py 의 PCA + Hilbert curve assignment
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2, random_state=seed)
    pca_vecs = pca.fit_transform(all_vecs)
    # Hilbert curve order에 매핑
    hilbert_order = np.argsort(pca_vecs[:, 0] * 1000 + pca_vecs[:, 1])  # simple proxy
    sids = np.zeros(len(all_vecs), dtype=np.int32)
    chunk_size = (len(all_vecs) + n_strata - 1) // n_strata
    for i, idx in enumerate(hilbert_order):
        sids[idx] = min(i // chunk_size, n_strata - 1)
    return sids
```

**별도 raw 구현 (`experiments/code/rq3/hilbert/hilbert_curve.py` line 36-95)**:
```python
def hilbert_xy_to_d(x, y, p):
    """Wikipedia 표준 Hilbert curve algorithm (xy → distance), NumPy vectorized."""
    n = 1 << p
    x = np.asarray(x, dtype=np.int64).copy()
    y = np.asarray(y, dtype=np.int64).copy()
    d = np.zeros_like(x)
    s = n >> 1
    while s > 0:
        rx = ((x & s) > 0).astype(np.int64)
        ry = ((y & s) > 0).astype(np.int64)
        d += s * s * ((3 * rx) ^ ry)
        flip = (ry == 0) & (rx == 1)
        x[flip] = n - 1 - x[flip]
        y[flip] = n - 1 - y[flip]
        mask = (ry == 0)
        x_swap = x[mask].copy()
        x[mask] = y[mask]
        y[mask] = x_swap
        s >>= 1
    return d
```

`hilbert_curve.py` 의 `assign_hilbert(mapper, vectors)` 호출 → PCA 2D coords → 2^10 × 2^10 grid (1024×1024) → Wikipedia Hilbert algorithm → quantile-based bucket. 이는 **진짜 Hilbert curve mapping**.

`run_hilbert.py` 는 이 모듈을 import 해서 사용하나, `measure_paper_exact.py` 의 registry 는 **path만 sys.path에 추가하고 실제로 import 하지 않음** (`# run_hilbert.py 의 PCA + Hilbert curve assignment` 주석은 misleading) — 그 대신 inline에서 PCA 후 `pca[:,0] * 1000 + pca[:,1]` argsort 라는 **단순 sort proxy**를 사용.

### 1.3 알고리즘 충실도: **2 / 10**

**Critical deviation**: 이 코드는 Hilbert curve가 아니라 **2D PCA의 1번째 축 우선 + 2번째 축 보조 lexicographic sort**임.

#### 왜 진짜 Hilbert가 아닌가?

`pca[:,0] * 1000 + pca[:,1]` 는:
- pca[:, 0]에 1000을 곱함 → 1번째 축 변동이 dominant ordering 결정
- pca[:, 1]은 거의 무시 (1번째 축이 같을 때만 사용)

이는 본질적으로 **PCA 1D quantile binning과 동등** — 사실상 P4 DimReduction paradigm 의 `pca1d` (line 481-489) 와 거의 같은 stratification 결과.

**locality 보존 측면**: 진짜 Hilbert curve는 (x, y) 평면의 인접 grid cell이 1D distance에서 인접하도록 **회전+flip** 으로 quadrant 간 jump 제거. 본 구현은 (PCA[1])이 매우 다른 두 점이 (PCA[0])이 같으면 인접 stratum 으로 매핑됨 — Hilbert는 이를 명시적으로 회피하나, lexicographic sort는 이를 회피 못함.

#### 1000 magic number의 의미

`pca[:,0] * 1000 + pca[:,1]` 의 1000은:
- DEEP/SIFT의 PCA 분포에서 PC1 range가 **PC2 range × 1000 보다 크다**고 가정
- 만약 PCA[0]의 표준편차가 σ_0, PCA[1]의 표준편차가 σ_1 이라 할 때 1000 × σ_0 ≫ max(PCA[1]) 일 때만 PCA[0]이 lexicographic primary key 역할
- DEEP 96d Gaussian-like 분포에서 σ_0/σ_1 ratio는 보통 1.05~1.5 정도 (PCA explained variance 첫 두 성분 비율). 즉 σ_0 × 1000 ≈ 1.2 × 1000 = 1200. 만약 PC2 max 가 ~10이면 1000 충분, ~100이면 부족.

**이 magic number는 fragile** — 다른 dataset (SSN++ 256d, YFCC 192d) 에서 PCA range가 다르면 정렬이 깨질 수 있음. 즉 dataset-dependent 비결정 행동.

### 1.4 Hyperparam

| Hyperparam | 값 | 적정성 |
|---|---|---|
| n_components (PCA) | 2 | 정상 (Hilbert도 2D 평면 사용) |
| sort key magic | 1000 | **불안정 — 데이터셋별 PC range 의존** |
| chunk_size 매핑 | (N + 19) // 20 | 균등 quantile (정상) |

### 1.5 n_strata=20 매핑

```python
chunk_size = (len(all_vecs) + n_strata - 1) // n_strata
for i, idx in enumerate(hilbert_order):
    sids[idx] = min(i // chunk_size, n_strata - 1)
```

- argsort 결과를 20등분 → quantile bucket
- 매핑 자체는 균등 (각 stratum 정확히 N/20 ± 1)
- 단 **stratum의 의미가 "Hilbert distance bucket"이 아니라 "PCA 1번째 축 quantile + 2번째 축 tiebreak bucket"**

`hilbert_curve.py` 의 `assign_hilbert()` 는 완전히 다른 quantile 결정:
1. learn_samples (1% 학습 sample)에서 PCA fit + grid_min/grid_max 결정
2. learn_samples의 Hilbert distance 계산 → quantile boundary edges 결정
3. 새 vec 도 같은 grid + PCA로 변환 → searchsorted(edges)

이는 **"학습 sample의 Hilbert distance 분포에 맞춘 bucket"** 으로, 진짜 spatial locality bucket. 매우 다름.

### 1.6 CaseA / CaseB 적합성

- **CaseA (replace)**: 우리 method가 Bernoulli sampling 직접 대체. PCA quantile bucket으로 stratified sampling. **stratification 자체는 바이어스 감소 효과 있음**, 단 spatial locality 효과는 미미.
- **CaseB (augment)**: B1 + method ensemble (50/50 weighted average). Hilbert가 진짜 spatial이라면 cardinality 추정 보완 효과 큼, 본 PCA proxy는 PCA1D와 비슷한 효과.

**ECQO 영역 외**: ECQO는 HNSW range query 기반 (vector index 활용)이라 본 method 적용 X (handoff_v2 §1 Decision 4).

### 1.7 결함 list

| Severity | 결함 | Fix 권고 |
|---|---|---|
| **CRITICAL** | 진짜 Hilbert curve 미사용 — PCA 2D lexicographic sort가 Hilbert로 명명됨 | `from hilbert.hilbert_curve import fit_hilbert_mapper, assign_hilbert` import + 1% learn sample fit + assign |
| **CRITICAL** | 1000 magic number는 dataset-specific PCA range 의존 → SSN++ 256d / YFCC 192d 에서 정렬 misalignment 가능 | 진짜 Hilbert로 교체 시 자동 해결 |
| **HIGH** | ★3 4강 결과 (-7.54%) 의 학술 정당성 — "Hilbert curve의 locality 효과"라고 보고하면 학술 fraud 위험 | 보고서에서 "PCA 2D linear order quantile binning" 으로 명명, Faloutsos & Roseman 1989 인용 폐기 또는 method를 진짜 Hilbert로 교체 후 재측정 |
| **MEDIUM** | `sys.path.insert("/mnt/hdd0/home/capstone2026/cache/rq3/hilbert")` 추가하나 import 안 함 → dead code | `from hilbert_curve import fit_hilbert_mapper, assign_hilbert` 명시 |
| **MEDIUM** | run_hilbert.py 가 라이브러리/data 종속성 측면 (1024×1024 grid + quantile)에서 더 정교 — registry 가 이를 미사용 | 진짜 구현 활용 |
| **LOW** | 별도 path insert 후 사용 안 함 → server에 hilbert directory 미존재 시 silent 실패 | path validation 추가 |

**★3 4강 학술 신뢰도 영향**: 만약 본 연구가 "Hilbert curve의 spatial locality가 stratification에 효과적" 이라고 주장한다면, **본 PCA 2D linear order에는 spatial locality 효과가 부분적**으로만 있음 (PCA 1번째 축 변동이 클러스터 분리에 기여하는 만큼만). Hilbert curve의 진짜 효과 (회전/flip으로 인접 grid 보존)는 본 구현에 없음 — 따라서 contribution 주장이 약화될 수 있음.

**즉시 조치 권고**: server-side `cache/rq3/hilbert/hilbert_curve.py` 가 이미 검증된 raw 구현이므로 registry의 hilbert를 다음과 같이 교체:

```python
if method_name == "hilbert":
    sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/hilbert")
    from hilbert_curve import fit_hilbert_mapper, assign_hilbert
    # 1% learn sample
    n_learn = max(int(len(all_vecs) * 0.01), n_strata * 50)
    rng = np.random.default_rng(seed)
    learn_idx = rng.choice(len(all_vecs), size=n_learn, replace=False)
    mapper = fit_hilbert_mapper(all_vecs[learn_idx], n_strata=n_strata, p=10, seed=seed)
    return assign_hilbert(mapper, all_vecs).astype(np.int32)
```

이 교체로 ★3 결과 재측정 시 -7.54% → 유사 범위 (-5% ~ -10%) 가 나올 가능성 높음. **단 결과가 일치하지 않을 수 있으니 사용자 confirm 필요**.

---

## 2. faiss_ivf — line 505-516

### 2.1 원전

**Sivic & Zisserman 2003** ("Video Google: A Text Retrieval Approach to Object Matching in Videos", *ICCV 2003*) — IVF (Inverted File) 의 vision retrieval 도입. visual word vocabulary (k-means cluster centroid).

**Jégou, Douze, Schmid 2011** ("Product Quantization for Nearest Neighbor Search", *PAMI*) — 본 학술 문헌 IVF + PQ 결합. IVFFlat은 IVF + flat 거리 계산 (PQ 없이) variant. 본 구현이 대상.

**핵심 알고리즘**: 
1. n_strata 개의 quantizer centroid로 k-means
2. 각 vector를 가장 가까운 centroid로 assign (Voronoi partition)

### 2.2 구현 위치 + 코드 발췌

```python
if method_name == "faiss_ivf":
    try:
        import faiss
        quantizer = faiss.IndexFlatL2(all_vecs.shape[1])
        index = faiss.IndexIVFFlat(quantizer, all_vecs.shape[1], n_strata)
        # train on subset
        train = all_vecs[: min(len(all_vecs), 200_000)].astype(np.float32)
        index.train(train)
        _, assign = index.quantizer.search(all_vecs.astype(np.float32), 1)
        return assign.flatten().astype(np.int32)
    except ImportError:
        raise NotImplementedError("faiss not available")
```

### 2.3 알고리즘 충실도: **6 / 10**

**Pros**:
- FAISS의 표준 IVFFlat 사용 → centroid 학습 (k-means)는 faiss internally 정확
- `quantizer.search(vec, 1)` = nearest centroid index 반환 (Voronoi partition) — 표준 IVF assignment
- 200K train subset은 충분 (paper IVF 표준 train 50K~1M 사이)

**Cons / Concerns**:
- `index.quantizer` 는 IVFFlat의 quantizer (IndexFlatL2 wrapper). `index.train()` 후 quantizer가 centroid update되었는지 FAISS 내부 동작 확인 필요. 일반적으로 IVFFlat.train() 호출 시 quantizer 도 train되지만 명시적 검증 부재.
- FAISS의 IVFFlat은 본래 train 시 random subsampling을 하므로 seed 미고정 시 결정적 X. `seed` 파라미터 unused.
- 첫 200K rows는 `[: 200_000]` slice — random sample 아닌 **첫 200K 행** 사용. 만약 `all_vecs` 가 정렬돼 있으면 (예: KM20 stratum 순) bias 가능.

### 2.4 Hyperparam

| Hyperparam | 값 | 적정성 |
|---|---|---|
| nlist (= n_strata) | 20 | 적정 (Voronoi cell 수) |
| train sample | min(200K, N) | 적정 (Sivic & Zisserman 표준) |
| seed | 미사용 | **결함 — FAISS 내부 random init 결정적 X** |
| metric | L2 | 표준 (IVFFlat default) |

### 2.5 n_strata=20 매핑

`assign.flatten()` → 직접 0..19 centroid index 반환. 매핑 자체는 정확.

각 stratum 크기는 Voronoi partition으로 **균등하지 않음** — DEEP/SIFT 의 cluster 구조가 분포 영향. paper IVFFlat은 보통 max/min ratio 1.5~3 정도.

### 2.6 CaseA / CaseB 적합성

- **CaseA**: IVF Voronoi partition은 정확한 spatial cluster. stratification 효과 우수 (k-means과 유사하나 더 fast).
- **CaseB**: B1 + IVF 평균. cardinality 추정 보완 효과 있음 (centroid 기반 spatial locality).

### 2.7 결함 list

| Severity | 결함 | Fix |
|---|---|---|
| **MEDIUM** | seed parameter 미사용 → FAISS 내부 random init 결정적 X (재현성 저하) | `faiss.normalize_L2(...)` 후 `index.cp.seed = seed` 설정 |
| **MEDIUM** | train sample이 첫 200K row → all_vecs 정렬에 bias 가능 | `rng.choice(N, 200000, replace=False)` 으로 random sample |
| **LOW** | 200K hardcode — 작은 dataset (SF=1, ~150K rows) 에선 모두 사용 (적정) | 변경 불필요 |
| **LOW** | `_, assign = quantizer.search(...)` 의 `_` 는 distance — quantizer search가 train된 centroid를 사용하는지 명시적 verify 부재 | self-test 추가 권고 |

**알고리즘 신뢰도**: P2 method 중 가장 정확하게 구현됨. 단 seed/train_sample randomness 보강 권고.

---

## 3. kdtree — line 534-541

### 3.1 원전

**Bentley 1975** ("Multidimensional Binary Search Trees Used for Associative Searching", *CACM 18(9)*) — KDTree 본 학술 문헌. 재귀 axis-aligned median split.

**핵심 알고리즘**:
1. 분산 가장 큰 axis 선택
2. 해당 axis의 median 으로 split → left/right
3. 재귀 (depth = log2(K))
4. leaf 가 stratum

### 3.2 구현 위치 + 코드 발췌

**registry (`measure_paper_exact.py` line 534-541)**:
```python
if method_name == "kdtree":
    from sklearn.neighbors import KDTree
    # KDTree leaf order → bucket
    sample = all_vecs[: min(len(all_vecs), 50_000)]
    tree = KDTree(sample, leaf_size=max(2, len(sample) // n_strata))
    # Query 모든 vectors with k=1 nearest leaf
    _, idx = tree.query(all_vecs, k=1)
    return (idx.flatten() % n_strata).astype(np.int32)
```

**별도 raw 구현 (`experiments/code/rq3/kdtree/kdtree_partition.py` line 74-105)**:
```python
def _build_kdtree(samples, target_leaves, leaf_id_counter):
    if target_leaves <= 1 or len(samples) < 2:
        leaf_id = leaf_id_counter[0]
        leaf_id_counter[0] += 1
        return KDNode(is_leaf=True, leaf_id=leaf_id)

    var = samples.var(axis=0)
    axis = int(np.argmax(var))
    threshold = float(np.median(samples[:, axis]))

    left_mask = samples[:, axis] < threshold
    if left_mask.sum() == 0 or left_mask.sum() == len(samples):
        # degenerate split — leaf fallback
        ...
    left_target = target_leaves // 2
    right_target = target_leaves - left_target
    left_node = _build_kdtree(samples[left_mask], left_target, ...)
    right_node = _build_kdtree(samples[~left_mask], right_target, ...)
```

이 raw 구현은 **명시적 leaf id 부여** (root → ... → leaf_id ∈ {0, ..., n_strata-1}). variance 큰 axis median split 재귀 → ceil(log2(20))=5 depth → 정확히 n_strata leaf.

### 3.3 알고리즘 충실도: **3 / 10**

**Critical deviation**: registry 구현은 **KDTree를 nearest-neighbor index로 사용**하고, leaf id 가 아닌 **nearest sample row index** 를 반환 후 `idx % n_strata` modulo 로 강제 매핑.

#### 왜 잘못됐는가?

```python
_, idx = tree.query(all_vecs, k=1)
# idx ∈ {0, ..., 49999} — sample 중 nearest row의 index
return (idx.flatten() % n_strata).astype(np.int32)
```

- `tree.query(vec, k=1)` 는 sample 50K rows 중 가장 가까운 row의 index 반환 (즉 nearest neighbor's row id)
- `idx % n_strata` = "nearest row의 row index mod 20" = **거의 무작위 hash**
  - 만약 sample이 random shuffle된 상태라면 → 거의 reservoir 와 동등 (uniform 0..19)
  - 만약 sample이 sorted (예: KM20 stratum 순) 라면 → bias 있는 hash

**spatial locality 0**: KDTree leaf id가 아닌 nearest neighbor row index를 사용 → 인접 vector가 인접 stratum이라는 보장 X.

#### sklearn KDTree의 leaf 추출

sklearn KDTree는 `tree.get_tree_stats()`, `tree.dual_tree()` 등으로 내부 정보 노출하나, 직접 leaf id 추출 API는 없음. raw `kdtree_partition.py` 의 path tree (axis/threshold 직접 따라가기) 방식이 정답.

#### leaf_size 의도

`leaf_size = max(2, len(sample) // n_strata) = 2500` (50K // 20). 이는 sklearn KDTree의 leaf 노드 크기 (한 leaf당 row 수) 결정. 즉 **sklearn KDTree는 leaf_size 단위로 leaf 생성**, 50K samples / 2500 = 20 leaf 가 의도. 만약 정확히 leaf id를 추출했다면 n_strata = 20 leaf 와 일치하나, 본 구현은 leaf id 미사용.

### 3.4 Hyperparam

| Hyperparam | 값 | 적정성 |
|---|---|---|
| sample size | 50K | 적정 (KDTree fit 시간 ~5s) |
| leaf_size | sample/20 = 2500 | 의도는 정확 (20 leaf 생성), 단 leaf id 추출 미흡 |
| seed | 미사용 | sklearn KDTree는 결정론 — 문제 없음 |

### 3.5 n_strata=20 매핑 정당성

**현재 구현**: `idx % n_strata` — 거의 random hash, spatial locality 파괴.
**정확한 매핑**: leaf id를 0..19로 부여 후 직접 사용. raw `kdtree_partition.py` 가 이를 구현.

### 3.6 CaseA / CaseB 적합성

- **CaseA**: 현재 구현은 거의 random partition (reservoir 와 유사). stratification 효과 미미.
- **CaseB**: B1 + 거의 random method 평균 → 노이즈만 추가. 효과 부정적 가능.

### 3.7 결함 list

| Severity | 결함 | Fix |
|---|---|---|
| **CRITICAL** | KDTree leaf id 미사용, `idx % n_strata` 로 row index modulo → spatial locality 0, 사실상 random partition | raw `kdtree_partition.py` 의 `fit_kdtree_partition` + `assign_kdtree` 사용 (1% learn sample) |
| **HIGH** | sklearn KDTree는 leaf id 직접 노출 X — 본 alternative path 가 잘못된 방향 | raw recursive split tree 구현으로 교체 |
| **MEDIUM** | leaf_size = 50000 // 20 = 2500 의 의도는 좋으나 leaf id 미접근으로 무의미 | raw 구현 활용 |
| **LOW** | 50K sample 크기 hardcode — DEEP 1M+ rows에선 5% 미만 → 학습 sample 부족 가능 | 1% learn sample (10K) 또는 100K 까지 허용 |

**즉시 조치 권고**:
```python
if method_name == "kdtree":
    sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/kdtree")
    from kdtree_partition import fit_kdtree_partition, assign_kdtree
    n_learn = max(int(len(all_vecs) * 0.01), n_strata * 50)
    rng = np.random.default_rng(seed)
    learn_idx = rng.choice(len(all_vecs), size=n_learn, replace=False)
    tree = fit_kdtree_partition(all_vecs[learn_idx], n_strata=n_strata, seed=seed)
    return assign_kdtree(tree, all_vecs).astype(np.int32)
```

---

## 4. kdpp — line 619-635

### 4.1 원전

**Kulesza & Taskar 2012** ("Determinantal Point Processes for Machine Learning", *Foundations and Trends in ML*) — k-DPP의 본 학술 문헌. **probabilistic** sampling 방법.

#### 진짜 k-DPP 알고리즘 (요약)
1. Kernel matrix K_{ij} = q_i q_j ⟨φ(i), φ(j)⟩ (positive semi-definite)
2. Eigendecomposition K = ΣV V^T
3. P(Y = y) = det(K_y) / det(K + I) for k-subset y of size k
4. 효율적 sampling: dual representation (V_J, J ⊂ eigenvectors) sample → conditional Gram-Schmidt
5. **결과: probabilistic — 동일 input + 다른 random seed → 다른 sample**

#### 본 학술 문헌의 핵심
- **Diversity bias**: det(K) maximize → 서로 멀리 떨어진 k 점 high probability
- **Quality bias**: q_i (importance) 가중치
- determinant 계산 = 모든 k-subset 동시 고려 (NP-hard naive, dual representation으로 polynomial time)

### 4.2 구현 위치 + 코드 발췌

```python
if method_name == "kdpp":
    # k-DPP greedy farthest-point selection — k=n_strata 대표점 + nearest
    rng_d = np.random.default_rng(seed)
    sample = all_vecs[: min(len(all_vecs), 50_000)]
    # Greedy farthest-first on sample
    idx0 = int(rng_d.integers(0, len(sample)))
    centers = [sample[idx0]]
    for _ in range(n_strata - 1):
        d = np.min(np.linalg.norm(sample[:, None, :] - np.array(centers)[None, :, :], axis=2), axis=1)
        centers.append(sample[np.argmax(d)])
    centers = np.array(centers, dtype=np.float32)
    sids = np.empty(len(all_vecs), dtype=np.int32)
    chunk = 100_000
    for i in range(0, len(all_vecs), chunk):
        d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centers[None, :, :], axis=2)
        sids[i:i+chunk] = np.argmin(d, axis=1)
    return sids
```

### 4.3 알고리즘 충실도: **2 / 10**

**Critical deviation**: 이 코드는 **k-DPP가 아니라 greedy farthest-point clustering (Gonzalez 1985 algorithm)**.

#### 왜 k-DPP가 아닌가?

진짜 k-DPP:
- determinantal kernel 계산 (kernel matrix K)
- eigendecomposition
- probabilistic sampling (det(K_y) / det(K + I) 비례)

본 구현:
- random initial point (1점)
- max-min distance argmax 으로 다음 centroid 선택
- 반복 — 100% deterministic given seed

이는 **Gonzalez 1985** ("Clustering to Minimize the Maximum Intercluster Distance", *Theoretical Computer Science 38*) 의 farthest-first traversal algorithm. 또한 **2-approximation k-center clustering**.

#### 진짜 k-DPP는 deterministic 하지 않음

본 구현은 seed 고정 시 동일 centers 산출 → deterministic. 이는 진짜 DPP의 본질 (probabilistic diversity sampling)와 정반대.

#### 학술 명명 정합성 critical

본 method가 paper에 "k-DPP" 로 보고된다면 **학술 명명 부정확**. Kulesza & Taskar 2012의 본 학술 문헌은 randomized sampling이 핵심 contribution이고, 본 구현은 그 contribution 무시.

### 4.4 epsilon_net과의 동등성 검증

`epsilon_net` (line 678-693):
```python
if method_name == "epsilon_net":
    rng_d = np.random.default_rng(seed)
    sample = all_vecs[: min(len(all_vecs), 50_000)]
    idx0 = int(rng_d.integers(0, len(sample)))
    centers = [sample[idx0]]
    for _ in range(n_strata - 1):
        d = np.min(np.linalg.norm(sample[:, None, :] - np.array(centers)[None, :, :], axis=2), axis=1)
        centers.append(sample[np.argmax(d)])
    centers = np.array(centers, dtype=np.float32)
    sids = np.empty(len(all_vecs), dtype=np.int32)
    chunk = 100_000
    for i in range(0, len(all_vecs), chunk):
        d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centers[None, :, :], axis=2)
        sids[i:i+chunk] = np.argmin(d, axis=1)
    return sids
```

#### diff 비교 (kdpp vs epsilon_net)

```diff
- # k-DPP greedy farthest-point selection — k=n_strata 대표점 + nearest
+ # Greedy ε-net — farthest-point until k=n_strata
  rng_d = np.random.default_rng(seed)
  sample = all_vecs[: min(len(all_vecs), 50_000)]
- # Greedy farthest-first on sample
  idx0 = int(rng_d.integers(0, len(sample)))
  centers = [sample[idx0]]
  for _ in range(n_strata - 1):
      d = np.min(np.linalg.norm(sample[:, None, :] - np.array(centers)[None, :, :], axis=2), axis=1)
      centers.append(sample[np.argmax(d)])
  centers = np.array(centers, dtype=np.float32)
  sids = np.empty(len(all_vecs), dtype=np.int32)
  chunk = 100_000
  for i in range(0, len(all_vecs), chunk):
      d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centers[None, :, :], axis=2)
      sids[i:i+chunk] = np.argmin(d, axis=1)
  return sids
```

**완전 동일** — 주석 1줄 차이 외 코드 100% 동일. **같은 seed로 측정 시 같은 stratum_ids 반환** (verifiable: 두 method를 같은 input으로 실행 시 `np.array_equal(kdpp_sids, epsilon_net_sids) == True` 보장).

이는 **paradigm 분리 정합성 critical 위반**. P2 spatial paradigm 안에서 두 method가 distinct 하지 않으면 ablation 비교 불가.

### 4.5 Hyperparam

| Hyperparam | 값 | 적정성 |
|---|---|---|
| sample size | 50K | 적정 (50K × 50K distance matrix는 메모리 큼 — 사실 본 구현은 sample × centers, 50K × 19 = 약 9.5M 부담 적음) |
| n_strata | 20 | 적정 |
| seed | 사용 | 단 random idx0 만, 이후 deterministic |

### 4.6 n_strata=20 매핑

`np.argmin(d, axis=1)` — 가장 가까운 centroid index 부여. Voronoi partition. **n_strata = 20 = number of centers = number of strata** — 깔끔.

### 4.7 CaseA / CaseB 적합성

- **CaseA**: farthest-first centroid는 spatial diversity 큰 partition. stratification 효과 우수 (실제로 k-center의 well-known 좋은 partition).
- **CaseB**: B1 + farthest-first 평균. 효과 양호.

### 4.8 결함 list

| Severity | 결함 | Fix |
|---|---|---|
| **CRITICAL** | k-DPP가 아닌 greedy farthest-first (Gonzalez 1985) — 학술 명명 부정확 | method 명을 `farthest_first` 또는 `kcenter_2approx` 로 rename, 또는 진짜 k-DPP (eigendecomposition + dual) 구현 |
| **CRITICAL** | epsilon_net과 코드 100% 동일 (주석 외) → paradigm ablation 불가 | kdpp를 진짜 DPP로 차별화, 또는 둘 중 하나 폐기 |
| **HIGH** | 학술 보고 시 "Kulesza & Taskar 2012 인용" 부적절 — 실제는 Gonzalez 1985 / Hochbaum & Shmoys 1985 | reference 정정 |
| **MEDIUM** | sample 50K rows → 메모리 부담 (50K × dim × 4byte). DEEP 96d 면 19MB, SSN++ 256d 면 51MB. 정상 범위 | 변경 불필요 |
| **LOW** | random idx0 외 deterministic → seed의 영향이 첫 점 선택에만 한정 | 정상 (Gonzalez 1985 표준) |

**즉시 조치 권고**: kdpp 와 epsilon_net 둘 중 하나만 남기거나, kdpp를 진짜 DPP 구현으로 교체.

#### 진짜 k-DPP 구현 옵션 (sketchy)
```python
if method_name == "kdpp":
    # Genuine k-DPP via dual representation
    sample = all_vecs[: min(len(all_vecs), 5_000)]  # smaller for kernel matrix
    K = sample @ sample.T  # linear kernel (or RBF)
    eigvals, eigvecs = np.linalg.eigh(K)
    # Sample J ⊂ eigenvectors, |J| = k
    rng = np.random.default_rng(seed)
    probs = eigvals / (eigvals + 1)
    J_mask = rng.random(len(probs)) < probs
    # Iteratively sample k points (Gram-Schmidt-like)
    # ... (see Kulesza & Taskar Algorithm 1)
    # 결과: k = n_strata indices, 각각이 stratum centroid
    centers = sample[selected_idx]
    # Voronoi assign
    ...
```

이는 ~50줄 정도의 본 학술 문헌-grade DPP sampling 코드 필요. 또는 **dppy** 라이브러리 (`pip install dppy`) 사용 가능.

---

## 5. epsilon_net — line 678-693

### 5.1 원전

**Haussler & Welzl 1987** ("Epsilon-Nets and Simplex Range Queries", *Discrete & Computational Geometry 2*) — ε-net의 본 학술 문헌. range space (X, R) 에서 small N ⊂ X 가 모든 R ∈ R 에 대해 |R ∩ N| / |N| ≈ |R| / |X| 가 되도록.

**Greedy farthest-point clustering** (Gonzalez 1985, Hochbaum & Shmoys 1985) — k-center 2-approximation. ε-net 의 **deterministic constructive** 변형.

#### 학술 정합성

ε-net은 본질적으로:
- ε-cover: 모든 X ∈ V 에 대해 d(X, N) ≤ ε
- 가장 작은 N (covering radius ε)
- learning theory에서 PAC bound 도구

본 구현은 k-center clustering (k 고정, ε 자동 결정) — 완전히 동일하진 않으나 **연관 깊음** (k-center optimal solution은 동시에 minimal covering radius). 즉 **practical equivalence**.

### 5.2 구현 위치 + 코드 발췌

이미 §4.4에서 epsilon_net 코드 표시. **kdpp 와 100% 동일 코드** (주석 1줄 차이만).

### 5.3 알고리즘 충실도: **5 / 10**

(kdpp 처럼 greedy farthest-first 와 동일하나, ε-net 명명은 **practical equivalence** 관점에서 그래도 정당화 가능 — kdpp 명명보다 학술적으로 덜 부정확)

**Pros**:
- ε-net과 farthest-first가 closely related (Gonzalez 1985's k-center 2-approximation = (2ε)-net)
- deterministic farthest-first 는 ε-net 의 **constructive variant**

**Cons**:
- 본래 ε-net은 ε 가 fixed parameter (covering radius) — 본 구현은 k 고정, ε 자동 결정. 의미가 약간 다름.
- 학술 보고 시 "Haussler & Welzl 1987 ε-net" 인용은 partial overlap만 — 더 정확한 인용은 "Gonzalez 1985 farthest-first 2-approximation k-center".

### 5.4 Hyperparam

§4.5와 동일.

### 5.5 n_strata=20 매핑

§4.6과 동일.

### 5.6 CaseA / CaseB 적합성

§4.7과 동일.

### 5.7 결함 list

| Severity | 결함 | Fix |
|---|---|---|
| **CRITICAL** | kdpp 와 100% 동일 코드 → paradigm ablation 불가 | kdpp 또는 epsilon_net 둘 중 하나 폐기 |
| **MEDIUM** | "ε-net" 명명은 practical equivalence (k-center) 이나 정확히 학술 ε-net과 다름 | 명명 정정 ("greedy_farthest_first" or "k_center_2approx") |
| **LOW** | 학술 보고 시 Haussler & Welzl 인용은 partial overlap → Gonzalez 1985 함께 인용 권고 | reference 추가 |

---

## 종합 권고

### A. 즉시 조치 (P0 — 학술 정합성 critical)

| 우선순위 | Action | 영향 |
|---|---|---|
| **P0-1** | **hilbert를 raw `hilbert_curve.py` 사용으로 교체** — 진짜 Hilbert curve algorithm | ★3 4강 결과의 학술 신뢰도 회복. 재측정 -7.54% → 다른 값 가능, 사용자 confirm 필요 |
| **P0-2** | **kdpp 와 epsilon_net 차별화** — 둘 중 하나 폐기 또는 kdpp를 진짜 DPP로 변경 | paradigm ablation 정합성 회복. 만약 폐기 시 P2 spatial 5 → 4 method |
| **P0-3** | **kdtree를 raw `kdtree_partition.py` 사용으로 교체** — 진짜 KD-tree leaf id 부여 | spatial locality 효과 회복, 현재 거의 random partition |

### B. 단기 조치 (P1)

| 우선순위 | Action | 영향 |
|---|---|---|
| **P1-1** | hilbert / kdtree / kdpp / epsilon_net의 학술 보고서 명명/인용 재검토 | 학술 fraud 위험 회피 |
| **P1-2** | faiss_ivf seed 고정 + train sample random | 재현성 향상 |

### C. paradigm 분류 재검토

| 현재 | 실제 algorithmic family | 권고 |
|---|---|---|
| hilbert (P2) | PCA 1D linear order quantile (proxy) | **진짜 Hilbert로 교체**, 그렇지 않으면 P4 DimReduction (pca1d) 와 사실상 동일 — paradigm 분리 의미 없음 |
| faiss_ivf (P2) | k-means Voronoi (P1 cluster paradigm) | **재분류 고려** — IVF는 본질적으로 k-means quantizer + flat search, P1 cluster와 paradigm 동일. 단 KMeans/MiniBatch와 구분 위해 P2 spatial 유지도 가능 (FAISS optimization differentiator) |
| kdtree (P2) | (현재) row index modulo hash → 사실상 P3 streaming reservoir와 동등; **(raw 구현 사용 시)** axis-aligned recursive split tree | **raw 구현 활용 시 P2 정당** |
| kdpp (P2) | greedy farthest-first | **이름이 잘못됨 — 진짜 DPP 가 아님** |
| epsilon_net (P2) | greedy farthest-first | **kdpp 와 동일 코드 → 차별화 필요** |

### D. ★3 4강 결과 학술 정당성 검토

본 검증의 가장 큰 발견은 **★3 hilbert -7.54% 결과가 진짜 Hilbert curve의 contribution이 아닌 PCA 1D quantile 효과** 일 가능성. 5/8 paradigm framework 보고서 (`audit_extra_experiments_20260508.md`, `RQ3_paradigm_심층검증_20260508.md`) 에서 "Hilbert curve의 spatial locality" 라고 주장한다면 학술 fraud 위험.

**해결 옵션**:
1. **option A — 진짜 Hilbert로 교체 후 재측정**: server 측 raw `hilbert_curve.py` 활용. 결과 -7.54% 와 비슷한 범위 나오면 학술 정당성 유지. 1.5h 정도 측정 시간 추가 필요.
2. **option B — method 명명 정정**: registry의 hilbert를 "pca2d_lex" 또는 "pca_quantile_2d" 로 rename. 보고서에서 "PCA 2D linear order quantile binning (Hilbert curve의 단순 proxy)" 으로 명시. 학술 contribution 약화.
3. **option C — 별도 method 추가**: 현재 hilbert를 "pca2d_lex"로 rename + 진짜 hilbert 별도 추가. 비교 ablation 결과 (PCA proxy vs 진짜 Hilbert) 자체가 **interesting finding** 이 됨 — "Hilbert curve의 진짜 locality 효과 vs PCA 단순 proxy의 효과" 분리 검증.

**option C 권고**: 학술 contribution 강화. 5/8 paradigm framework의 "Hilbert curve의 locality 가 stratification 에 효과적" 가설을 직접 검증할 수 있는 추가 method (`hilbert_real`) 측정으로 paradigm framework 자체의 학술 가치 향상.

### E. P2 paradigm overall evaluation

- **검증 통과 method (≥ 7/10)**: 1개 (faiss_ivf, 6/10 — borderline)
- **부분 검증 통과 (3-5/10)**: 2개 (epsilon_net 5/10, kdtree 3/10)
- **학술 정합성 critical (< 3/10)**: 2개 (hilbert 2/10, kdpp 2/10)

**P2 spatial paradigm 평균 충실도**: (2 + 6 + 3 + 2 + 5) / 5 = **3.6 / 10**

P1 cluster paradigm (P1 agent 결과 평균 추정 7-8 / 10)에 비해 매우 낮음. 이는 **spatial method들이 "spatial" 명명만 하고 실제 spatial locality 알고리즘을 구현하지 않음**을 의미. 즉시 조치 시 raw 구현 (hilbert_curve.py, kdtree_partition.py, zorder_curve.py) 활용으로 평균 5+ 로 회복 가능.

### F. 추가 발견 — server side raw 구현체의 활용도

server-side `experiments/code/rq3/{hilbert, kdtree, zorder, sparserp, gmm, pq}/` 디렉토리에 **검증된 raw 구현체** (self-test 포함) 가 존재하나, `measure_paper_exact.py` registry 가 이 중 일부만 활용 (sparse_rp, random_projection만). 다른 method들 (hilbert, kdtree, zorder, gmm, pq) 은 inline 단순화 구현 사용.

**권고**: registry를 raw 구현체 활용 우선으로 재작성. 코드 중복 제거 + 알고리즘 정합성 향상.

```python
# Suggested refactor for measure_paper_exact.py registry

RAW_IMPLEMENTATIONS = {
    "hilbert": ("hilbert", "hilbert_curve", "fit_hilbert_mapper", "assign_hilbert"),
    "kdtree": ("kdtree", "kdtree_partition", "fit_kdtree_partition", "assign_kdtree"),
    "zorder": ("zorder", "zorder_curve", "fit_zorder_mapper", "assign_zorder"),
    "sparse_rp": ("sparserp", "sparse_random_projection", "fit_sparse_rp", "assign_sparse_rp"),
    # ... 등
}

def _get_method_strata(method_name, all_vecs, n_strata=20, seed=42):
    if method_name in RAW_IMPLEMENTATIONS:
        sub_dir, mod, fit_fn, assign_fn = RAW_IMPLEMENTATIONS[method_name]
        sys.path.insert(0, f"/mnt/hdd0/home/capstone2026/cache/rq3/{sub_dir}")
        m = __import__(mod, fromlist=[fit_fn, assign_fn])
        # 1% learn sample
        n_learn = max(int(len(all_vecs) * 0.01), n_strata * 50)
        rng = np.random.default_rng(seed)
        learn_idx = rng.choice(len(all_vecs), size=n_learn, replace=False)
        mapper = getattr(m, fit_fn)(all_vecs[learn_idx], n_strata=n_strata, seed=seed)
        return getattr(m, assign_fn)(mapper, all_vecs).astype(np.int32)
    # ... inline methods
```

이 refactor로 algorithmic fidelity 보장 + 코드 50줄 감소.

---

## H. END

작성: 2026-05-10 21:00 KST (P2 spatial agent)
파일: `/Users/hyunbin/Capstone/_internal/method_verification_20260510/paradigm_P2_spatial.md`

**핵심 메시지**: P2 paradigm 의 5 method 중 **3개 (hilbert, kdtree, kdpp)** 가 학술 명명과 실제 알고리즘이 critical mismatch. **즉시 조치 (raw 구현 활용 + paradigm 분리)** 권고. 특히 **★3 4강 hilbert 결과의 학술 정당성** 이 본 검증의 가장 큰 발견.

**P2 paradigm 평균 충실도**: 3.6 / 10 (P1 cluster 추정 7+ 대비 현저히 낮음).

**즉시 조치 시 fix 가능 (raw 구현 존재)**: hilbert (raw exists), kdtree (raw exists). kdpp (별도 작성 필요).
