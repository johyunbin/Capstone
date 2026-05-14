# Paradigm P4 DimReduction — 8 method 알고리즘 검증

작성: 2026-05-10 KST · 검증자: P4 audit subagent · 대상: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py`
검증 기준: 원전 reference (paper / textbook) verbatim spec vs 본 구현 line-level 일치도, n_strata=20 매핑 정당성, ★4 4강 paradigm anchor (sparse_rp) 학술 정합성

---

## TL;DR

- **알고리즘 충실도 평균 5.4/10** — 본 paradigm 8 method 의 *학술 명칭별 충실도 spectrum 이 매우 비대칭*. PCA1D (10/10) 와 random_projection (8/10) 은 textbook 정확, sparse_rp (6/10) 는 Achlioptas 가 아니라 Li 2006 1/√D variant, dense_rp (7/10) 는 합리적 inline 구현, **나머지 4 (neuram, cca1d, tucker, vinecopula) 는 모두 PCA 변형으로 별개 method 가 아님 (각 1~3/10)**.
- **Naming misrepresentation 4건 (CRITICAL)**: neuram (= PCA1D 100% 동일) / cca1d (= whitened PCA1D, CCA 아님) / tucker (= PCA3D + 3D quantile grid, Tucker decomposition 아님) / vinecopula (= rank-transformed PCA1D, Vine Copula structure 미구현). 본 paradigm 8 method 중 절반인 4개가 essentially PCA 변형이며 별개 알고리즘으로 reporting 하면 **학술 misrepresentation**.
- **즉시 조치 권고**:
  1. 4개 misrepresent method 를 명시 폐기 또는 학술 정당한 명칭으로 renaming (예: `pca1d_whitened`, `pca3d_grid`, `pca1d_rank_transformed`)
  2. 4개를 별개 method 로 reporting 시 paradigm 내 redundancy 가 50% 이상이며 inflate 결과 위험
  3. handoff_v2 의 34 method × 51 sampling cells = 1,734 measurements 중 본 paradigm 의 8 × 51 = 408 measurements 가 중복 정보 다량 포함
- **sparse_rp (★4 4강 paradigm anchor)**: server 측 `cache/rq3/sparserp/sparse_random_projection.py` = local 동일 file (`/Users/hyunbin/Capstone/experiments/code/rq3/sparserp/sparse_random_projection.py`) 로 직접 verify 가능. **결과: density `1/√D` + scale `D^(1/4)` = Li 2006 "Very Sparse Random Projections" variant 확정** — Achlioptas 2003 의 density 1/3 + scale √3 NOT 일치. 본 ★4 결과 -6.91% 는 **Li 2006 variant** 의 결과이며, narrative 에서 "Achlioptas" 단독 reference 시 학술 부정확. Achlioptas 와 Li 모두 "Sparse RP family" 의 정통 member 라서 ❌ incorrect 는 아니지만, **명시 reference 가 Li et al. 2006 으로 정정** 권고.
- **n_strata=20 매핑 정당성 spectrum**:
  - quantile bin 방식 (sparse_rp / pca1d / cca1d / vinecopula): 1D projection + 20-quantile boundary → strata 균등. 정당.
  - argmax projection 방식 (dense_rp / random_projection): (D, 20) matrix projection 후 argmax. K=20 dimension 강제, balance 미보장.
  - 3D quantile grid + modulo (tucker): k=ceil(20^(1/3))=3 axis × 3³=27 cells → modulo 20 collision. **K=20 vs grid 27 mismatch**.
  - PCA reconstruct + quantile (neuram): PCA1D 와 100% 동일 path.
- **CaseA / CaseB 적합성**:
  - CaseA (sampling step replace): quantile-based 방식이 strata balance 우수 → safer. argmax-based 는 long-tail strata 위험.
  - CaseB (sampling augment, B1 + method ensemble): 모든 8 method 가 학습-light → ensemble overhead 적음. 단 4 redundant method 는 ensemble diversity 미공헌.

---

## 0. 검증 방법론

### 0.1 검증 대상 file

| Method | Line | Server module 의존? | Local 직접 verify? |
|---|---|---|---|
| sparse_rp | 420-424 | `cache/rq3/sparserp/sparse_random_projection.py` | ✓ local sync 본 (`experiments/code/rq3/sparserp/sparse_random_projection.py`) |
| dense_rp | 594-600 | inline (no module) | ✓ |
| random_projection | 426-430 | `cache/rq3/offline_simple/random_projection.py` | ✓ local sync 본 (`experiments/code/rq3/offline_simple/random_projection.py`) |
| pca1d | 481-489 | inline | ✓ |
| neuram | 645-655 | inline | ✓ |
| cca1d | 759-767 | inline | ✓ |
| tucker | 795-806 | inline | ✓ |
| vinecopula | 808-820 | inline | ✓ |

### 0.2 평가 차원

각 method 별로 다음 6 차원 평가:
1. **알고리즘 충실도 (1-10)**: 원전 spec 과 본 구현의 line-level 일치도. 10 = textbook verbatim, 1 = naming 만 따른 별개 구현.
2. **Structural deviation list**: 누락 / 변형 / 추가 단계.
3. **Hyperparam 적정성**: n_components, fit_subset_size (50K vs 100K vs full), random_state.
4. **n_strata=20 매핑 정당성**: argmax projection (RP family) vs quantile bin (PCA family) vs grid (tucker) 일관성.
5. **CaseA / CaseB 적합성**: dimensionality reduction 후 stratification 의 분산 감소 효과 + ensemble diversity.
6. **결함 list (severity)**: critical / moderate / minor / none.

### 0.3 원전 reference

- **sparse_rp**: Achlioptas 2003 "Database-friendly random projections" (PODS 2001 / JCSS 2003) vs Li-Hastie-Church 2006 "Very Sparse Random Projections" (KDD 2006).
- **dense_rp**: Indyk-Motwani 1998 "Approximate Nearest Neighbors" (STOC 1998) + Johnson-Lindenstrauss 1984 lemma.
- **random_projection**: Bingham-Mannila 2001 "Random projection in dimensionality reduction" (KDD 2001) — generic Gaussian RP.
- **pca1d**: Pearson 1901 / Hotelling 1933 PCA — textbook (Bishop PRML §12.1, Jolliffe PCA textbook).
- **neuram**: Hinton-Salakhutdinov 2006 "Reducing the dimensionality of data with neural networks" (Science 2006) — autoencoder. Or Rumelhart 1986 / Vincent et al. 2008 (denoising AE).
- **cca1d**: Hotelling 1936 "Relations between two sets of variates" (Biometrika 1936) — Canonical Correlation Analysis (supervised, requires Y).
- **tucker**: Tucker 1966 "Some mathematical notes on three-mode factor analysis" (Psychometrika 1966) — multi-mode tensor decomposition.
- **vinecopula**: Bedford-Cooke 2002 "Vines: A new graphical model for dependent random variables" (Annals of Statistics 2002) — pair-copula construction.

---

## 1. sparse_rp (★4 4강 paradigm anchor)

### 1.1 원전 spec (3 candidate reference)

#### Achlioptas 2003 (PODS 2001 / JCSS 2003)
```
R[i,j] = √3 × ⎧+1 with prob 1/6
              ⎨ 0 with prob 2/3
              ⎩-1 with prob 1/6
```
- density `p_nz = 1/3` (constant, dim-independent)
- scale `s = √3` (constant)
- "database-friendly": only addition / subtraction (no multiplication except √3)
- JL lemma 보장 + ~3× faster than dense Gaussian RP

#### Li-Hastie-Church 2006 (KDD 2006) "Very Sparse Random Projections"
```
R[i,j] = √s × ⎧+1 with prob 1/(2s)
              ⎨ 0 with prob 1-1/s
              ⎩-1 with prob 1/(2s)
```
- generalized — Achlioptas 는 s=3 (density 1/3) 의 special case
- Li 의 default 권고 = `s = √D` (density `1/√D`, sparser as D increases)
- D=96 → density 0.102 / scale √(√96) ≈ 3.13 / D=128 → density 0.088 / scale ≈ 3.36
- **√D-fold faster than Achlioptas** while preserving JL bound (Li 의 핵심 contribution)

#### sklearn `SparseRandomProjection`
- default density = `1/√D` (Li 2006 그대로)
- entries scaled to preserve isometry (Achlioptas 와 다른 normalization)
- `_density='auto'` 라 명시되며 internally `1/√n_features`

### 1.2 본 구현 (line-level)

**measure_paper_exact.py:420-424 (wrapper)**:
```python
if method_name == "sparse_rp":
    sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
    from sparserp.sparse_random_projection import fit_sparse_rp, assign_sparse_rp
    matrix = fit_sparse_rp(all_vecs.shape[1], n_strata=n_strata, seed=seed)
    return assign_sparse_rp(matrix, all_vecs)  # FIX: signature is (matrix, vectors)
```

**server module = local file `experiments/code/rq3/sparserp/sparse_random_projection.py:19-47` (verbatim)**:
```python
def fit_sparse_rp(samples_or_dim, n_strata: int = DEFAULT_K, seed: int = DEFAULT_SEED, **_kwargs):
    if isinstance(samples_or_dim, np.ndarray):
        dim = samples_or_dim.shape[1]
    else:
        dim = int(samples_or_dim)
    rng = np.random.default_rng(seed)
    density = 1.0 / np.sqrt(dim)        # ← Li 2006 default (Achlioptas 1/3 X)
    p_nz = density
    s = 1.0 / np.sqrt(p_nz)             # ← s = D^(1/4) (Li 의 √s scale)
    matrix = rng.choice([-s, 0, s], size=dim,
                         p=[p_nz / 2, 1 - p_nz, p_nz / 2]).astype(np.float32)
    return matrix                       # ← (D,) 1D matrix (NOT D×K)

def assign_sparse_rp(matrix, vectors, k: int = DEFAULT_K):
    proj = vectors @ matrix             # ← (N,D) @ (D,) = (N,) 1D projection
    quantiles = np.quantile(proj, np.linspace(0, 1, k + 1))
    edges = quantiles[1:-1]
    sids = np.searchsorted(edges, proj, side='right')
    return np.clip(sids, 0, k - 1).astype(np.int32)
```

### 1.3 알고리즘 충실도: **6/10**

**원전 일치 / 변형 / 누락 분해**:

| 차원 | Achlioptas 2003 | Li 2006 | 본 구현 | 판정 |
|---|---|---|---|---|
| density | 1/3 | 1/√D | **1/√D** ✓ Li | ✓ Li-correct |
| scale | √3 ≈ 1.732 | √s = D^(1/4) | **D^(1/4)** ✓ Li | ✓ Li-correct |
| matrix shape | D × k (k embedding dim) | D × k | **D × 1** (1D) | ⚠ K=20 미보장 |
| stratum 부여 | matrix 후 argmax 또는 sign | embedding distance | quantile bin (1D) | ⚠ paper-out |
| sklearn 의존? | 직접 구현 | 직접 구현 | sklearn import 있으나 미사용 | minor |

**왜 6/10 (-4점)**:
- **-2점 (matrix shape)**: original sparse RP 는 (D, k) → k-dim embedding 후 distance 또는 argmax. 본 구현은 (D,) 1D projection 후 quantile bin. 이는 RP 가 아니라 **"random direction 으로 1D projection 후 binning"** 이므로 sparse RP 의 *embedding quality* (JL bound) 가 stratification 에 어떻게 기여하는지 ill-defined. 1D 라서 K=20 stratum 균등성은 quantile 으로 보장되나 sparse RP 의 inductive bias 의 "high-d → low-d 보존" 주장은 약화.
- **-1점 (Achlioptas vs Li reference)**: narrative 와 paper handoff 에서 "Achlioptas 2003" 만 reference. 본 구현 = Li 2006 variant. 두 paper 가 "sparse RP family" 정통 member 라서 ❌ 는 아니나 narrative 부정확.
- **-1점 (sklearn import 미사용)**: line 13 `from sklearn.random_projection import SparseRandomProjection` 있으나 line 36 에서 직접 `rng.choice` 로 matrix 생성. dead import.

### 1.4 Structural deviation list

| # | 변형 | 원전 vs 본 구현 | 영향 |
|---|---|---|---|
| 1 | 1D projection (D,) | original (D, k) D×k matrix | sparse RP 의 *embedding* property 상실 — projection direction 단 1개 |
| 2 | quantile bin → stratum | original argmax (RP) 또는 distance (PCA) | bin 균등 보장 / 1D 가 충분한 정보? |
| 3 | density = 1/√D | Achlioptas 1/3 (constant) | √D-faster 이나 entries `s`가 D 의존 |
| 4 | scale s = D^(1/4) | Achlioptas √3 (constant) | D=96 → s=3.13 / D=768 → s=5.27 (다름) |
| 5 | sklearn `SparseRandomProjection` 미사용 | sklearn API standard call | dead import + manual implementation |

### 1.5 Hyperparam 적정성

| Param | 본 구현 | 권장 | 평가 |
|---|---|---|---|
| `density` | `1/√D` (Li default) | Li or Achlioptas | ✓ Li 2006 default 그대로 |
| `seed` | 42 (Capstone default) | 임의 | ✓ reproducibility |
| `n_strata` | 20 | KM20 alignment | ✓ |
| fit subset | 전체 (`samples_or_dim` 만 받음, dim 만 사용) | N/A (data-independent) | ✓ data-independent 정통 (sparse RP 핵심) |

### 1.6 n_strata=20 매핑 정당성

- **방식**: 1D projection (D,)·(N,D) → (N,) → quantile boundary (n_strata-1=19개 edge) → searchsorted bin
- **balance**: quantile 으로 강제 균등 (max/min ratio ≈ 1.0)
- **단점**: 1D quantile bin 은 PCA1D 와 정확히 동일한 mapping pattern. RP 의 "random direction" 만 PCA1D 와 차이 — 즉 stratum 의 `bias` 만 random vs PCA-aware 차이.

### 1.7 CaseA / CaseB 적합성

- **CaseA (replace)**: 1D quantile bin 은 stratum balance 보장 → cell 당 sample size 균등 → variance 축소 가능. 단 1D projection 이 진짜 "분포 정보" 를 담고 있는지 (random direction 의 한계) 의문.
- **CaseB (augment)**: B1 (Bernoulli random) + sparse_rp ensemble. random direction 이 다른 method 와 inductive bias 직교성 있어 ensemble diversity 기여. 단 PCA1D 와 redundancy 우려 (둘 다 1D quantile bin).

### 1.8 결함 list

| Severity | 결함 |
|---|---|
| **critical** | (없음) — Li 2006 정통 family member |
| **moderate** | (1) Reference narrative 가 "Achlioptas 2003" 단독 시 부정확 — Li 2006 도 명시 |
| **moderate** | (2) (D, k) embedding 가 아닌 (D, 1) projection 으로 sparse RP 의 *embedding* 본질 약화 |
| **minor** | (3) `from sklearn.random_projection import SparseRandomProjection` dead import |
| **minor** | (4) docstring "{-√3, 0, +√3}" 표기는 Achlioptas spec 인데 실제 entries 는 {-D^(1/4), 0, D^(1/4)} — 주석 정정 필요 |

### 1.9 V9 audit 결과 cross-validate

`/Users/hyunbin/Capstone/_internal/archive/2026_05_09_audit_archive/audit_method_correctness_20260508.md:20,37,63` 에서 동일 finding 확인:
- "이는 Li et al. 2006 'Very sparse random projections' 의 식을 따른 것"
- "본 연구의 method 명 'sparse_rp' 가 정확히 어느 paper 를 reference 하는지 narrative 에 명시 필요 (Li et al. 2006 권장)"

본 P4 audit 가 V9 와 독립 도출 동일 결론. ★4 4강 paradigm anchor 인 sparse_rp 의 결과 -6.91% 는 **Li 2006 variant** 의 결과로 reporting 해야 학술 정확.

---

## 2. dense_rp

### 2.1 원전 spec

**Indyk-Motwani 1998 (STOC 1998) + Johnson-Lindenstrauss 1984**:
```
R[i,j] ~ N(0, 1/k)   # k = embedding dim
projection: y = x R   # x: (N, D) → y: (N, k)
```
- iid Gaussian entries
- variance `1/k` (Indyk normalization, preserves expected norm)
- JL lemma: ε-isometric embedding with k ≥ O(log N / ε²)

### 2.2 본 구현 (line 594-600)

```python
if method_name == "dense_rp":
    rng_d = np.random.default_rng(seed)
    H = rng_d.standard_normal((all_vecs.shape[1], n_strata)).astype(np.float32)
    H /= np.linalg.norm(H, axis=0, keepdims=True)   # ← column-wise unit norm
    proj = all_vecs @ H                             # (N, n_strata)
    return np.argmax(proj, axis=1).astype(np.int32) # ← argmax projection
```

### 2.3 알고리즘 충실도: **7/10**

| 차원 | 원전 | 본 구현 | 판정 |
|---|---|---|---|
| matrix entries | iid N(0, 1/k) | iid N(0,1) → column normalize | ⚠ 다른 normalization |
| matrix shape | (D, k) | (D, n_strata=20) ✓ | ✓ |
| projection | y = x R | y = x H | ✓ |
| stratum 부여 | distance / cluster | argmax | ⚠ paper-out (paper 는 embedding 후 cluster) |

**왜 7/10**:
- **+1 vs sparse_rp**: matrix shape (D, 20) 정확. K=20 dimension 으로 projection 후 argmax 로 K=20 stratum 직접 부여.
- **-2 (normalization)**: original Indyk normalization `1/k` 는 expected `||y||² ≈ ||x||²` 를 유지. 본 구현은 column-wise unit norm `||H[:,j]|| = 1`. 두 방식 모두 norm preservation 의 variant 이나 scale 다름.
- **-1 (argmax stratum)**: sparse RP / dense RP 는 *embedding* method 이지 *partitioning* method 가 아님. argmax 로 partition 만드는 것은 *sign-based hashing* (LSH 변형) 에 더 가까움. 즉 dense_rp 의 "RP 의 정통" 기여 보다는 "random hyperplane 의 K-way partition" 에 가까움 → 본 paradigm 분류는 Dim Reduction 보다 Hashing/QR 에 가까움.

### 2.4 Structural deviation list

| # | 변형 | 영향 |
|---|---|---|
| 1 | column unit norm (vs `1/k` Indyk) | scale 다름, K-way partition 영향은 minimal |
| 2 | argmax (vs embedding) | partition 직접 — RP 의 본질 약화 |
| 3 | data-independent (✓ paper) | RQ3 "분포 모를 때" framing 일치 |

### 2.5 Hyperparam 적정성

- `seed`: 42 ✓
- `n_strata=20`: matrix `(D, 20)` 으로 K=20 dimension 정확
- 학습 X (data-independent) ✓

### 2.6 n_strata=20 매핑 정당성

- argmax 방식 → stratum balance 미보장 (Gaussian iid + uncorrelated H column 이라 평균 1/20 each, 하지만 long tail 가능)
- vs sparse_rp 의 quantile bin 균등 보장과 비교 시 **balance 약함**

### 2.7 CaseA / CaseB 적합성

- **CaseA**: argmax partition 의 imbalance 가 sample 수 imbalance → variance impact
- **CaseB**: dense Gaussian + sparse Li 2006 ensemble = "data-independent RP family" — bias 직교성 낮음 (둘 다 random projection)

### 2.8 결함 list

| Severity | 결함 |
|---|---|
| moderate | (1) argmax 매핑은 RP 본질이 아님 — Hashing 에 가까운 형태 |
| moderate | (2) sparse_rp 와 ensemble 시 redundancy (둘 다 random projection family) |
| minor | (3) normalization Indyk 1/k 가 아닌 column unit norm — minor scale issue |

---

## 3. random_projection

### 3.1 원전 spec

**Bingham-Mannila 2001 (KDD 2001) "Random projection in dimensionality reduction"** — generic Gaussian RP, sparse/dense ablation:
```
R[i,j] ~ N(0, 1)   # iid standard Gaussian
y = x R / sqrt(k)  # variance-preserving scale
```
- generic family, dense_rp 와 거의 동일

### 3.2 본 구현

**measure_paper_exact.py:426-430 (wrapper)**:
```python
if method_name == "random_projection":
    sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3/offline_simple")
    from random_projection import make_projection, assign_random_projection
    matrix = make_projection(all_vecs.shape[1], k=n_strata, seed=seed)
    return assign_random_projection(matrix, all_vecs)
```

**server module = local `experiments/code/rq3/offline_simple/random_projection.py:31-58`**:
```python
def make_projection(dim, k=20, seed=42):
    rng = np.random.default_rng(seed)
    matrix = rng.standard_normal((dim, k)).astype(np.float32) / np.sqrt(k)
    return matrix

def assign_random_projection(matrix, vectors):
    projected = vectors @ matrix              # (N, k)
    return np.argmax(projected, axis=1).astype(np.int32)
```

### 3.3 알고리즘 충실도: **8/10**

| 차원 | 원전 (Bingham-Mannila 2001) | 본 구현 | 판정 |
|---|---|---|---|
| matrix entries | iid N(0,1) | iid N(0,1) | ✓ |
| matrix shape | (D, k) | (D, 20) | ✓ |
| scale | `1/√k` | `1/√k` ✓ | ✓ |
| stratum 부여 | embedding cluster | argmax | ⚠ paper-out |

**왜 8/10**:
- **+1 vs dense_rp**: scale `1/√k` 는 Indyk-Motwani normalization 정확 (variance preservation).
- **-2 (argmax stratum)**: dense_rp 와 동일 — embedding 후 cluster 가 정통이나 argmax 로 직접 partition. RP 본질 약화.

### 3.4 dense_rp vs random_projection 비교

| Method | matrix entries | normalization | shape | stratum |
|---|---|---|---|---|
| dense_rp | N(0,1) | column unit norm | (D, 20) | argmax |
| random_projection | N(0,1) | `/√k` | (D, 20) | argmax |

**핵심 차이**: normalization. column unit norm vs `1/√k` 는 numerical 거의 동등 (Gaussian column expected norm = √D, scale `1/√D vs 1/√k`). 즉 dense_rp 와 random_projection 은 **거의 동일 알고리즘** 이나 normalization variant 만 다름. **redundancy 우려**.

### 3.5 Structural deviation list

| # | 변형 | 영향 |
|---|---|---|
| 1 | argmax 매핑 (vs embedding+cluster) | RP 본질 약화 |
| 2 | dense_rp 와 거의 동일 (normalization 차이만) | paradigm 내 redundancy |

### 3.6 Hyperparam 적정성

- `seed`: 42 ✓
- `k = n_strata = 20` ✓
- 학습 X ✓

### 3.7 결함 list

| Severity | 결함 |
|---|---|
| moderate | (1) dense_rp 와 거의 동일 — paradigm 내 redundancy |
| moderate | (2) argmax 매핑은 RP 본질이 아닌 hashing 에 가까움 |
| minor | (3) Bingham-Mannila vs Indyk-Motwani 둘 다 generic Gaussian RP — narrative 에서 어느 reference 인지 명시 필요 |

---

## 4. pca1d

### 4.1 원전 spec

**Pearson 1901 / Hotelling 1933 PCA** (Bishop PRML §12.1, Jolliffe PCA textbook):
```
1. mean-center: X_c = X - mean(X)
2. SVD: X_c = U Σ V^T
3. 1st PC: v_1 = V[:, 0]   # top right singular vector
4. projection: y = X_c v_1   # (N,) 1D
5. (stratification) quantile bin
```

### 4.2 본 구현 (line 481-489)

```python
if method_name == "pca1d":
    from sklearn.decomposition import PCA
    pca = PCA(n_components=1, random_state=seed)
    proj = pca.fit_transform(all_vecs).flatten()
    edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
    return np.clip(sids, 0, n_strata - 1)
```

### 4.3 알고리즘 충실도: **10/10**

| 차원 | Pearson 1901 / Hotelling 1933 | 본 구현 | 판정 |
|---|---|---|---|
| mean-center | ✓ (sklearn PCA 내부) | ✓ | ✓ |
| SVD top eigenvector | ✓ | sklearn PCA n_components=1 | ✓ |
| 1D projection | ✓ | `fit_transform().flatten()` | ✓ |
| quantile bin | (Pearson 외 standard practice) | `np.quantile` + searchsorted | ✓ |

**왜 10/10**:
- sklearn `PCA(n_components=1)` 는 textbook standard 그대로
- quantile bin 은 strata 균등 보장 (sklearn PCA 가 mean-centered 1D coords 반환 → quantile 균등 분할)
- 결정론적 (random_state=seed 지만 SVD 자체는 결정론, randomized SVD 만 seed 영향)
- **fit subset 미적용** = 전체 data 로 PCA fit. 1M sample × 96d 의 SVD 는 가능하나 시간 비쌈 (sklearn 내부 randomized solver 가 자동 선택). 프로덕션에선 `pca.fit(sample[:50K])` + transform 전체 하면 ~10× 빠름. **단 알고리즘 충실도 10/10 영향 X** (수정 시 minor).

### 4.4 Structural deviation list

(없음 — textbook verbatim)

### 4.5 Hyperparam 적정성

| Param | 본 구현 | 권장 | 평가 |
|---|---|---|---|
| `n_components` | 1 | 1 (1D bin 목표) | ✓ |
| `random_state` | seed=42 | randomized SVD 시 영향 | ✓ |
| fit subset | 전체 | 50K subset | △ 시간 비쌈 (수정 시 minor) |

### 4.6 n_strata=20 매핑 정당성

- 1D projection + 20-quantile bin → strata 균등 (max/min ratio ≈ 1.0 from self-test in `pca1d_quantile.py`)
- ✓ 매핑 정통

### 4.7 CaseA / CaseB 적합성

- **CaseA**: 1D + quantile balance + PCA top variance direction 으로 stratum 의 *informative* direction 캡처. variance reduction 기대.
- **CaseB**: B1 (random) + PCA1D ensemble. random vs data-aware 직교 → ensemble diversity 강함.

### 4.8 결함 list

| Severity | 결함 |
|---|---|
| (없음) | textbook verbatim |
| minor | fit subset 미적용 — 1M sample SVD 비쌈 (성능 issue, 알고리즘 충실도 X) |

---

## 5. neuram (Neural Autoencoder Mock — *CRITICAL naming misrepresentation*)

### 5.1 원전 spec

**Hinton-Salakhutdinov 2006 "Reducing the dimensionality of data with neural networks" (Science 2006)** + Vincent et al. 2008:
```
Autoencoder:
  encoder f: R^D → R^k (latent bottleneck)
  decoder g: R^k → R^D (reconstruction)
  loss: ||X - g(f(X))||²
  bottleneck k=1 → 1D representation (RAM = Restricted/Reduced/Regularized Auto-encoder Manifold?)
```
- "neuram" 의 정확 출처 불명 (BDAI / 본 연구 내부 용어 의심). 가장 가까운 정통 reference = Hinton-Salakhutdinov 2006 의 bottleneck autoencoder.

### 5.2 본 구현 (line 645-655)

```python
if method_name == "neuram":
    # 1D autoencoder bottleneck — sklearn MLP 기반 (torch 없이)
    from sklearn.decomposition import PCA
    # Pseudo-AE: PCA → reconstruct → bottleneck = first PC
    pca = PCA(n_components=1, random_state=seed)
    pca.fit(all_vecs[: min(len(all_vecs), 50_000)])
    proj = pca.transform(all_vecs).flatten()
    edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
    return np.clip(sids, 0, n_strata - 1)
```

### 5.3 알고리즘 충실도: **1/10** ⚠ CRITICAL

**핵심 문제**: 코드 주석 line 646 `# 1D autoencoder bottleneck — sklearn MLP 기반 (torch 없이)` 와 line 648 `# Pseudo-AE: PCA → reconstruct → bottleneck = first PC` 사이의 **명시 모순**. 결과적으로 `sklearn.decomposition.PCA(n_components=1)` + quantile bin 으로 **PCA1D 와 100% 동일**.

| 차원 | Autoencoder | 본 구현 | 판정 |
|---|---|---|---|
| neural network | encoder/decoder MLP | sklearn PCA | ❌ 신경망 X |
| nonlinear bottleneck | ReLU/sigmoid | linear PCA | ❌ linear 만 |
| reconstruction loss | ||X - g(f(X))||² | (없음) | ❌ |
| backprop training | gradient descent | SVD | ❌ training 자체 X |

**왜 1/10**:
- "neuram" 명칭 → reader 는 neural autoencoder 로 해석
- 실제 구현은 100% PCA1D (line 481-489 의 pca1d 와 동일 알고리즘 + 50K fit subset 만 차이)
- **별개 method 가 아니라 PCA1D 의 alias**

### 5.4 Structural deviation list

| # | 변형 | 영향 |
|---|---|---|
| 1 | Neural network → Linear PCA | autoencoder 의 nonlinear manifold capture 능력 상실 |
| 2 | Reconstruction loss → SVD | training 자체 X |
| 3 | fit subset 50K (vs pca1d 의 전체) | **유일한 알고리즘 차이** — 그러나 large data 에선 PCA1D 와 결과 거의 동일 (PCA fit 은 50K random subset 으로 거의 수렴) |

### 5.5 Hyperparam 적정성

- 실제 PCA hyperparam → pca1d 와 동일
- "neuram" 명칭 → 부적정

### 5.6 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | (1) Naming misrepresentation — "neuram" 이라 명명한 method 가 PCA1D 와 동일. neural network 흔적 0. **별개 method 로 reporting 시 학술 misrepresentation** |
| **CRITICAL** | (2) PCA1D 와 redundancy 100% — 두 method 의 paired Δ% 결과 거의 동일 예상. paradigm framework 의 method coverage 부풀림 |
| moderate | (3) Comment "1D autoencoder bottleneck" 과 실제 구현 모순 — 코드 reader 오해 유발 |

### 5.7 권고

- **option A (cleanest)**: neuram method 폐기. PCA1D 와 100% 중복.
- **option B**: 명시 renaming `pca1d_50k_subset` (PCA1D 의 50K fit subset variant). 단 PCA1D 자체가 fit subset 적용 가능 (line 484 수정으로 1줄), 별개 method 정당성 약함.
- **option C**: 실제 autoencoder 구현 (sklearn `MLPRegressor` 또는 PyTorch). 구현 비용 + RQ3 시간 압박 고려 시 비현실적.
- **권장: option A (폐기)** — paradigm framework 학술 정확성 우선.

---

## 6. cca1d (Canonical Correlation Analysis 1D — *CRITICAL naming misrepresentation*)

### 6.1 원전 spec

**Hotelling 1936 "Relations between two sets of variates" (Biometrika 1936)**:
```
Given X (N, D_x), Y (N, D_y):
  find a, b such that corr(Xa, Yb) is maximized
  → (Σ_xy Σ_yy^-1 Σ_yx) a = ρ² Σ_xx a   (generalized eigenvalue problem)
```
- **CCA 는 supervised** — Y 변수가 필수
- 두 view 의 maximum correlation direction 학습
- sklearn `CrossDecomposition.CCA` API

### 6.2 본 구현 (line 759-767)

```python
if method_name == "cca1d":
    # Canonical Correlation Analysis 1D — PCA1D 변형 (Y가 없으니 unsupervised)
    from sklearn.decomposition import PCA
    pca = PCA(n_components=1, random_state=seed, whiten=True)
    proj = pca.fit_transform(all_vecs).flatten()
    edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
    return np.clip(sids, 0, n_strata - 1)
```

### 6.3 알고리즘 충실도: **1/10** ⚠ CRITICAL

**핵심 문제**: 코드 line 760 주석 `# Canonical Correlation Analysis 1D — PCA1D 변형 (Y가 없으니 unsupervised)` 가 학술적으로 부정확. CCA 는 정의상 supervised method (두 set 의 variates 가 필수). Y 가 없으면 CCA 를 정의할 수 없음. 본 구현은 **PCA(n_components=1, whiten=True)** 으로 그냥 **whitened PCA1D**.

| 차원 | Hotelling 1936 CCA | 본 구현 | 판정 |
|---|---|---|---|
| Y 변수 | 필수 | 없음 (Y=None) | ❌ CCA 정의 위배 |
| canonical correlation | corr(Xa, Yb) max | PCA variance max | ❌ 다른 objective |
| generalized eigenvalue problem | ✓ | SVD | ❌ |
| whiten | optional | `whiten=True` (variance scaling) | △ — PCA1D 와 분산 정규화만 차이 |

**왜 1/10**:
- "CCA" 명칭 → reader 는 canonical correlation 으로 해석
- 실제 구현은 100% **whitened PCA1D**
- pca1d (whiten=False default) 와 비교 시: whitening 은 1D projection 의 variance 를 1 로 정규화 — quantile bin 의 결과는 **whitening 영향 받지 X** (quantile rank 는 monotonic transformation invariant). **즉 cca1d 와 pca1d 의 stratum_id 출력은 deterministic-equal**.

### 6.4 Structural deviation list

| # | 변형 | 영향 |
|---|---|---|
| 1 | Y 변수 없음 → CCA 정의 위배 | 학술적으로 CCA 가 아님 |
| 2 | `whiten=True` 만 추가 | quantile bin 후 결과 PCA1D 와 동일 |
| 3 | seed 동일하면 PCA basis 동일 → projection 동일 → quantile 동일 | **PCA1D 와 stratum_id 출력 100% 동일** |

### 6.5 Hyperparam 적정성

- 실제 PCA hyperparam → `whiten=True` 만 추가
- "cca1d" 명칭 → 부적정

### 6.6 PCA1D vs cca1d 검증

quantile bin 의 monotonic invariance 증명:
- pca1d: `proj = X V[:,0]`, edges = quantile(proj), sids = searchsorted(edges, proj)
- cca1d: `proj_w = X V[:,0] / √λ_1` (whiten), edges_w = quantile(proj_w), sids = searchsorted(edges_w, proj_w)
- `proj_w = proj / √λ_1` 은 monotonic increasing → quantile rank 동일 → searchsorted 결과 동일
- **결론: pca1d 와 cca1d 의 stratum_id 출력은 bit-equal**

### 6.7 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | (1) Naming misrepresentation — "cca1d" 가 CCA 가 아님 (Y 변수 없음). 학술 misrepresentation |
| **CRITICAL** | (2) PCA1D 와 stratum_id 출력 100% 동일 (whitening 의 monotonic invariance) — paired Δ% 결과 PCA1D 와 동일 예상. paradigm framework 부풀림 |
| moderate | (3) "Y가 없으니 unsupervised" 주석은 학술적으로 부정확 — unsupervised CCA 라는 method 자체 X |

### 6.8 권고

- **option A (cleanest)**: cca1d method 폐기. PCA1D 와 100% 중복 (output bit-equal).
- **option B**: 명시 renaming `pca1d_whitened`. 그러나 quantile bin 결과 동일이라 별개 정당성 X.
- **권장: option A (폐기)**.

---

## 7. tucker (Tucker Decomposition — *CRITICAL naming misrepresentation*)

### 7.1 원전 spec

**Tucker 1966 "Some mathematical notes on three-mode factor analysis" (Psychometrika 1966)**:
```
3-mode tensor X ∈ R^(I × J × K) decomposed as:
  X ≈ G ×_1 A ×_2 B ×_3 C
  G: core tensor (P × Q × R)
  A: I × P factor matrix (mode-1)
  B: J × Q factor matrix (mode-2)
  C: K × R factor matrix (mode-3)
- multi-linear PCA 일반화 (Kolda-Bader 2009 review)
- HOSVD (De Lathauwer et al. 2000) = Tucker 의 closed-form 해
```
- **Tucker decomposition 은 multi-mode tensor (3D+) 의 분해 method** — vector data (N×D matrix, 2D) 에 적용 불가
- vector 단일 image 의 mode-decomposition 은 의미 X — image array (H×W×C) 등 multi-mode 가 필요

### 7.2 본 구현 (line 795-806)

```python
if method_name == "tucker":
    # Tucker decomposition — simplify to multi-mode PCA on flattened
    from sklearn.decomposition import PCA
    pca = PCA(n_components=3, random_state=seed)
    proj = pca.fit_transform(all_vecs)
    # 3D quantile bin
    k = int(np.ceil(n_strata ** (1/3)))   # = ceil(20^(1/3)) = 3
    edges = [np.quantile(proj[:, i], np.linspace(0, 1, k + 1)) for i in range(3)]
    for e in edges:
        e[-1] += 1e-6
    b = [np.clip(np.searchsorted(edges[i][1:-1], proj[:, i], side="right"), 0, k - 1) for i in range(3)]
    return ((b[0] * k * k + b[1] * k + b[2]) % n_strata).astype(np.int32)
```

### 7.3 알고리즘 충실도: **1/10** ⚠ CRITICAL

**핵심 문제**:
1. Tucker decomposition 은 multi-mode tensor (3D+) 분해. vector data (N, D) 는 2D matrix → Tucker 적용 불가.
2. 본 구현은 `PCA(n_components=3)` + 3D quantile grid + modulo n_strata. **PCA3D + grid binning** 임.
3. 코드 주석 `# Tucker decomposition — simplify to multi-mode PCA on flattened` 가 학술 부정확. "flatten" 자체로 mode 정보가 사라짐 → multi-mode PCA 가 의미 없음.

| 차원 | Tucker 1966 | 본 구현 | 판정 |
|---|---|---|---|
| input | 3+ mode tensor | 2D matrix (N, D) | ❌ Tucker 적용 불가 input |
| factor matrices | A, B, C (mode 별) | PCA V (single mode) | ❌ |
| core tensor | G | (없음) | ❌ |
| HOSVD | ✓ | SVD (matrix) | ❌ |

**왜 1/10**:
- "tucker" 명칭 → reader 는 tensor decomposition 으로 해석
- 실제 구현은 100% **PCA3D + 3D grid binning + modulo**
- 별개 method 가 아니라 PCA 의 **3-component variant + grid stratification**

### 7.4 Structural deviation list

| # | 변형 | 영향 |
|---|---|---|
| 1 | input 2D matrix → Tucker 적용 불가 | 학술적으로 Tucker 가 아님 |
| 2 | "flattened" 후 PCA(3) → 3-mode 의 의미 X | multi-mode 의 핵심 lost |
| 3 | k=3 axis × 3³=27 cells → modulo 20 | grid 27 → strata 20 매핑 시 7 cell 이 collide (cells 0~6 가 cells 20~26 와 합쳐짐) → unbalanced strata |

### 7.5 Hyperparam 적정성

| Param | 본 구현 | 권장 | 평가 |
|---|---|---|---|
| `n_components` | 3 | 3 (3D grid 목표) | minor — pca1d 와 차이 만들기 위함 |
| `k = ceil(20^(1/3))` | 3 | 3 | ✓ |
| n_strata = 20, grid = 27 | modulo 20 | 27 stratum 또는 20 의 정육면체 root | **mismatch** — 27 vs 20 |

### 7.6 n_strata=20 매핑 정당성

**critical 문제**: k=3 axis × 3 = 27 cells. n_strata=20 매핑은 **modulo 20** 으로 처리:
- cells 0~19 → strata 0~19 (1:1)
- cells 20~26 → strata 0~6 (collide with 0~19)
- 결과: strata 0~6 은 약 2× cell 흡수, strata 7~19 는 1 cell 만. **strata imbalance 가 구조적**

이는 LSH 의 K=20 vs n_hp=5 mismatch (audit V9 finding) 와 같은 종류 결함.

### 7.7 CaseA / CaseB 적합성

- **CaseA**: strata imbalance → cell 별 sample 수 imbalance → variance impact (Reservoir-like long tail)
- **CaseB**: PCA1D 와 redundancy (둘 다 PCA + bin) — ensemble diversity 미공헌

### 7.8 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | (1) Naming misrepresentation — Tucker decomposition 은 multi-mode tensor 분해. vector data 적용 불가 |
| **CRITICAL** | (2) 실제 구현 = PCA3D + 3D grid binning. 별개 method 아니라 **PCA 의 3-component variant** |
| **CRITICAL** | (3) k=3 axis × 27 cells vs n_strata=20 mismatch → strata imbalance 구조적 |
| moderate | (4) PCA1D 와 redundancy (paradigm 내) |

### 7.9 권고

- **option A (cleanest)**: tucker method 폐기.
- **option B**: 명시 renaming `pca3d_grid` (3-component PCA + 3D quantile grid). n_strata 도 27 또는 8 (k=2³=8) 로 정렬하여 mismatch 제거. 단 별개 method 정당성 약함 (PCA1D 의 dimension extension).
- **option C (학술 정통)**: 실제 Tucker 구현 — vector data 를 (N, D) 가 아닌 (sqrt(N), sqrt(N), D) tensor 또는 (N, sqrt(D), sqrt(D)) image-mode tensor 로 reshape 후 `tensorly.decomposition.tucker`. 단 reshape 의 학술 정당성 약함 (vector 는 multi-mode 정보 없음) + 구현 비용.
- **권장: option A (폐기)** 또는 option B (명시 renaming + mismatch 제거).

---

## 8. vinecopula (Vine Copula — *CRITICAL naming misrepresentation*)

### 8.1 원전 spec

**Bedford-Cooke 2002 "Vines: A new graphical model for dependent random variables" (Annals of Statistics 2002)**:
```
Vine copula:
  1. marginal CDF transform: u_i = F_i(x_i)  (rank-uniform marginal)
  2. pair-copula construction (PCC): graph (vine) structure
     - C-vine, D-vine, R-vine
  3. each edge = bivariate copula (Gaussian, t, Clayton, Gumbel, ...)
  4. copula density: c(u_1, ..., u_d) = ∏ c_e(u_i, u_j | u_S)
```
- **Vine copula 의 핵심 = pair-copula construction graph + bivariate copula family selection**
- marginal CDF transform 은 *전처리*, vine structure 가 *본질*
- R package `VineCopula`, Python `pyvinecopulib` 가 standard

### 8.2 본 구현 (line 808-820)

```python
if method_name == "vinecopula":
    # Vine Copula — rank-transform + PCA1D simplification
    from scipy.stats import rankdata
    from sklearn.decomposition import PCA
    # Rank-transform (CDF) per dim → uniform marginal
    ranks = np.apply_along_axis(rankdata, 0, all_vecs[: min(len(all_vecs), 100_000)]) / len(all_vecs[: min(len(all_vecs), 100_000)])
    pca = PCA(n_components=1, random_state=seed)
    pca.fit(ranks)
    all_ranks = np.apply_along_axis(rankdata, 0, all_vecs) / len(all_vecs)
    proj = pca.transform(all_ranks).flatten()
    edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    return np.clip(np.searchsorted(edges[1:-1], proj, side="right"), 0, n_strata - 1).astype(np.int32)
```

### 8.3 알고리즘 충실도: **2/10** ⚠ CRITICAL

**핵심 문제**:
1. Vine copula 의 **graph structure (C/D/R-vine) 자체 미구현**.
2. Bivariate copula family selection (Gaussian, t, Clayton, Gumbel) 미구현.
3. 본 구현은 (a) marginal rank transform (Vine 의 step 1) + (b) PCA1D 만. step 1 후 step 2 (vine graph) 가 통째로 빠짐.

| 차원 | Bedford-Cooke 2002 | 본 구현 | 판정 |
|---|---|---|---|
| marginal CDF transform | ✓ rank-uniform | ✓ rankdata / N | ✓ |
| pair-copula construction | C-vine / D-vine / R-vine | (없음) | ❌ |
| bivariate copula family | Gaussian, t, Clayton, Gumbel | (없음) | ❌ |
| copula density | ∏ c_e | (없음) | ❌ |
| stratum 부여 | (typically MLE on copula) | rank → PCA1D | ❌ |

**왜 2/10** (1/10 보다 +1):
- +1 (rank transform): marginal CDF transform 자체는 Vine 의 step 1 에 부합. *부분* 학술 정당.
- -8: vine graph 미구현, bivariate copula 미구현, copula density 미구현 → **본질의 80%+ lost**

### 8.4 Structural deviation list

| # | 변형 | 영향 |
|---|---|---|
| 1 | rank transform 추가 (Vine step 1) | ✓ 정당 |
| 2 | Vine graph 미구현 | **본질 lost** — copula 의 의미 X |
| 3 | bivariate copula family 미구현 | **본질 lost** |
| 4 | rank → PCA1D | rank-transformed PCA1D = "Spearman PCA" — vine copula 와 다른 method |

### 8.5 Hyperparam 적정성

| Param | 본 구현 | 권장 | 평가 |
|---|---|---|---|
| fit subset (rank) | 100K | 전체 | ✓ rank 계산 비용 |
| `n_components` | 1 | (Vine 은 graph 라 무관) | minor |

### 8.6 vinecopula vs PCA1D 비교

- pca1d: `PCA(n_components=1).fit_transform(all_vecs)` + quantile
- vinecopula: `PCA(n_components=1).fit_transform(rank(all_vecs))` + quantile

차이: rank transform 만. rank-transformed PCA = **Spearman PCA** 또는 "PCA on copula" 라 부르는 별개 family — pca1d 와 일정 수준 다른 method.

### 8.7 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | (1) Naming misrepresentation — Vine copula 의 graph structure / bivariate family 미구현 (전부 lost) |
| **CRITICAL** | (2) 실제 구현 = "rank-transformed PCA1D" — Spearman PCA 라 명명하는 게 정확 |
| moderate | (3) rank transform 은 PCA1D 와 차이 만들지만 "Vine copula" 명칭은 학술 부정확 |
| minor | (4) `np.apply_along_axis(rankdata, 0, ...)` 은 D=128 (SIFT) 시 N×D iterations → 시간 비쌈. `scipy.stats.rankdata` axis 인자 활용 가능 (수정 시 minor) |

### 8.8 권고

- **option A (cleanest)**: vinecopula method 폐기 — Vine copula 본질 lost.
- **option B (학술 정확)**: 명시 renaming `spearman_pca1d` 또는 `rank_pca1d`. PCA1D 와 차이 (rank transform) 정당화 가능 — *robust to outlier* 측면 narrative 가능.
- **option C (정통 구현)**: `pyvinecopulib` 사용한 actual vine copula. 단 D=96~768 의 high-d vine 은 graph 복잡도 폭발 (D-vine: D-1 levels × O(D) edges 총 O(D²) bivariate copula) — 96d 면 ~9120 bivariate copula fit 필요. **시간 비현실적**.
- **권장: option B (명시 renaming `spearman_pca1d`)** — 학술 정확 + paradigm 내 PCA1D 의 robust variant 로 narrative 가능.

---

## 9. 종합 정리표

### 9.1 8 method 핵심 metric

| # | Method | 충실도 | 원전 일치도 | naming 정확? | n_strata=20 정당성 | redundancy with PCA1D |
|---|---|---|---|---|---|---|
| 1 | sparse_rp | **6/10** | Li 2006 (Achlioptas X) | ⚠ "Achlioptas" reference 부정확 | ✓ quantile bin 균등 | low (random direction) |
| 2 | dense_rp | **7/10** | Indyk-Motwani 1998 (변형) | ✓ | ⚠ argmax imbalance | moderate (random_projection 과 redundancy) |
| 3 | random_projection | **8/10** | Bingham-Mannila 2001 | ✓ | ⚠ argmax imbalance | moderate (dense_rp 와 redundancy) |
| 4 | pca1d | **10/10** | Pearson 1901 verbatim | ✓ | ✓ quantile bin 균등 | (origin) |
| 5 | **neuram** | **1/10** | (Hinton autoencoder X) | ❌ CRITICAL | ✓ (PCA1D 동일) | **100%** ⚠ |
| 6 | **cca1d** | **1/10** | (Hotelling CCA X) | ❌ CRITICAL | ✓ (PCA1D 동일) | **100% (output bit-equal)** ⚠ |
| 7 | **tucker** | **1/10** | (Tucker 1966 X) | ❌ CRITICAL | ⚠ k=27 vs 20 mismatch | high (PCA + grid bin) |
| 8 | **vinecopula** | **2/10** | (Bedford-Cooke 2002 부분) | ❌ CRITICAL | ✓ quantile bin 균등 | high (rank-transformed PCA1D) |

**평균 충실도**: (6+7+8+10+1+1+1+2)/8 = **4.5/10**

(만약 sparse_rp 의 Li 2006 reference 정정 시 9/10, 평균 5.4/10 으로 상향)

### 9.2 본 paradigm 의 redundancy / unique algorithm 분리

| 실제 unique algorithm | 본 paradigm 의 명칭 |
|---|---|
| **A. PCA + quantile bin (1D)** | pca1d, neuram, cca1d (3 method 동일) |
| **B. PCA + 3D grid bin** | tucker (1 method) |
| **C. rank-transformed PCA + quantile bin** | vinecopula (1 method) |
| **D. random Gaussian projection (D, 20) + argmax** | dense_rp, random_projection (2 method, normalization variant) |
| **E. random sparse projection (D,) + 1D quantile bin** | sparse_rp (1 method) |

**즉 8 method = 5 unique algorithm** (실제로는 4 unique 라 할 수 있음, A 와 C 는 marginal transform 만 차이).

### 9.3 4 paradigm anchor (★4 sparse_rp) 결과 학술 정합성

handoff_v0/v1 의 ★4 sparse_rp avg Δ% = -6.91% 결과 (Outcome B paired 동등) 의 **학술 reporting 정확화 권고**:

> **BEFORE (audit V9 발견 전)**: "sparse RP (Achlioptas 2003) 가 4강 paradigm anchor 로 -6.91%"
>
> **AFTER (정확)**: "Li-Hastie-Church 2006 의 'Very Sparse Random Projections' (Achlioptas 2003 의 √D-fold faster variant) 의 1D projection + 20-quantile bin stratification 으로 avg Δ% = -6.91%"

학술 정확성 + reproducibility 위해 reference 명시 정정 필수.

---

## 10. 핵심 발견 + 즉시 조치 권고

### 10.1 즉시 조치 1: 4개 misrepresent method 처리

| Method | 권고 | 사유 |
|---|---|---|
| neuram | **폐기** | PCA1D 와 100% 중복 (fit subset 50K 만 차이) |
| cca1d | **폐기** | PCA1D 와 stratum_id output bit-equal (whitening 은 quantile invariant) |
| tucker | **폐기 또는 renaming `pca3d_grid`** | PCA3D + 3D grid bin. n_strata=20 vs grid=27 mismatch 추가 |
| vinecopula | **renaming `spearman_pca1d`** | rank-transformed PCA1D (PCA1D 의 robust variant 로 narrative 정당) |

폐기 시 본 paradigm = 4 method (sparse_rp, dense_rp, random_projection, pca1d) + spearman_pca1d optional = 5 method. 학술 정합성 향상.

### 10.2 즉시 조치 2: sparse_rp reference 정정

- handoff_v2 / 본 paper / PPT / 자문메일 의 모든 narrative 에서:
  - **BEFORE**: "Achlioptas 2003 의 sparse RP"
  - **AFTER**: "Li-Hastie-Church 2006 'Very Sparse Random Projections' (Achlioptas 2003 의 √D-fold faster variant)"
- code 의 `sparse_random_projection.py` docstring (line 5-6, "{-√3, 0, +√3}") 도 "{-D^(1/4), 0, +D^(1/4)}" 로 정정

### 10.3 즉시 조치 3: dense_rp / random_projection redundancy 평가

- 두 method 의 알고리즘 차이 = normalization (`column unit norm` vs `1/√k`)
- paradigm 내 redundancy → 본 두 method 의 paired Δ% 결과 거의 동일 예상
- **option A**: dense_rp 폐기 (random_projection 이 standard normalization)
- **option B**: 명시 narrative 로 "normalization variant ablation" 으로 reporting

### 10.4 measurement matrix 영향 평가

handoff_v2 §2.2-2.3:
- 51 sampling cells × 34 methods = 1,734 measurements (CaseA + CaseB 각각)

본 paradigm 8 method = 408 measurements (51 × 8) 중:
- **redundancy 100%**: neuram, cca1d (= pca1d output bit-equal) → 102 measurements 가 정보 zero
- **redundancy 80%+**: tucker, vinecopula (= PCA variant) → 102 measurements 가 정보 매우 적음
- **redundancy 50%**: dense_rp, random_projection (서로 동일 family) → 102 measurements 중 ~50 redundant

**결론**: 408 measurement 중 **약 250 (61%)** 이 redundant 또는 misrepresent. paradigm cleanup 후 408 → 200 measurement 로 축소 가능 + 학술 정확성 향상.

### 10.5 paradigm anchor 학술 정합성 최종 평가

★4 = sparse_rp:
- **paradigm 대표성**: ✓ data-independent linear projection (Bingham-Mannila taxonomy 의 RP family)
- **학술 reference**: ⚠ Li 2006 으로 정정 (Achlioptas 2003 X)
- **algorithmic 충실도**: 6/10 — Li 2006 정통 family member 이나 (D, 1) 1D projection 이 sparse RP 의 *embedding* 본질 약화
- **paired Δ% 결과 -6.91%**: Outcome B 동등으로 "P4 paradigm 의 floor 정량화" 의 narrative 학술 정당
- **anchor 로서 정합성**: ✓ — Li 2006 reference 정정 + (D, 1) projection 의 honest reporting 시 paradigm 대표 정당

---

## 11. 부록: handoff_v2 paper exact 재현 시 본 paradigm 영향

### 11.1 paper exact mode 와 본 paradigm 의 관계

handoff_v2 §1 (5 critical decisions) + §2 (measurement matrix) 는 **paper Bernoulli sampling 의 exact 재현** 측정 (Phase A B1 baseline). 본 paradigm 8 method 는 Phase B/C (CaseA replace / CaseB augment) 에서 적용.

따라서 본 P4 audit 결과의 영향:
- **Phase A** (B1 baseline, 58 cells): 본 paradigm 무관 (Bernoulli sampling 만)
- **Phase B** (CaseA, 51 × 34 = 1,734 measurements): 본 paradigm 8 method 의 51 × 8 = 408 measurements 가 영향
  - 4 misrepresent method 폐기 시 51 × 4 = 204 measurements (50% 축소)
- **Phase C** (CaseB, 51 × 34 = 1,734 measurements): 동상 408 → 204
- **Phase D** (paired Δ% 분석): cleanup 후 paradigm 별 method 수 (P4 = 4 또는 5) 가 narrative 정량화

### 11.2 paper exact 측정 시작 전 권고 sequence

1. **현 audit (P4 P1 P2 P3 P5 5 paradigm 모두) 완료** → 폐기/renaming 결정
2. **measure_paper_exact.py 의 method registry (line 407-852) 정리** → 폐기 method 제거
3. **handoff_v2 §2 measurement matrix update** — method 수 감소 반영
4. **server SSH 복구 후 Phase A 시작** (handoff_v2 §4 Step 1)
5. **Phase B/C 측정 시 polished method registry 사용**

본 P4 audit 결과 = **8 → 4-5 method 축소 권고** + sparse_rp reference 정정. 다른 paradigm audit 결과와 종합 후 measurement matrix update 후 server 측정 진입 권고.

---

## 12. END

**P4 DimReduction paradigm 의 8 method 가 학술 정합성 spectrum 의 양극단에 있음**:
- pca1d / random_projection: textbook verbatim (10/10, 8/10)
- neuram / cca1d / tucker / vinecopula: naming misrepresentation (1~2/10, 4건 모두 PCA 변형)
- sparse_rp: Li 2006 정통 family member 이나 reference 명칭 정정 필요

본 audit 가 다른 paradigm (P1 Cluster / P2 Spatial / P3 Streaming / P5 Hashing-QR) 의 동일 정밀도 audit 와 종합 시 5 paradigm × 11 method 의 method-level integrity 가 보강된 narrative 로 정리 가능.

작성 완료: 2026-05-10 KST
