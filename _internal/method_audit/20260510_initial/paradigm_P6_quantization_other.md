# Paradigm P6 Quantization/Other — 5 method 알고리즘 검증

**검증 일자**: 2026-05-10 KST
**검증자**: P6 (Quantization/Other paradigm) audit agent
**대상 파일**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py` (line 519-793)
**참조 paper**:
- Jegou, Douze, Schmid 2011 "Product Quantization for Nearest Neighbor Search" (PQ)
- Ge, He, Ke, Sun 2013 "Optimized Product Quantization" (OPQ)
- Yang et al. 2020 "NeuroCard: One Cardinality Estimator for All Tables" (neurocard)
- Zhao et al. 2023 "FactorJoin: A New Cardinality Estimation Framework for Join Queries"
- Dhillon 2001 "Co-clustering documents and words using bipartite spectral graph partitioning" + Williams & Seeger 2001 (Nyström)

---

## TL;DR

- **알고리즘 충실도 평균**: **3.0 / 10** (5개 method 중 4개가 "이름과 무관한 단순 구현")
- **CRITICAL 결함 4건**:
  1. `pq` — PQ codeword 의 product structure 가 md5 hash modulo 로 완전 파괴 (학술 정합성 무효)
  2. `opq` — OPQ rotation matrix 학습 후 `pq_index.sa_encode` 호출 시 **OPQ 학습된 rotation 미적용 위험**(API 사용 오류 추정)
  3. `neurocard_lite` — NeuroCard 논문(transformer autoregressive density)과 **완전 무관**. 실제로는 `PCA(8) + KMeans(20)` = P1 cluster paradigm 의 명백한 alias. naming misrepresentation
  4. `factor_join` — FactorJoin 논문(probabilistic graphical factor model + join key marginals)과 **완전 무관**. 실제로는 `PCA(2) + 2D quantile grid(5×5=25→%20)` = generic 2D bin. naming misrepresentation
- **MODERATE 결함 1건**:
  5. `cocluster_nystrom` — Nyström approximation 미구현, SpectralBiclustering on 5K sample + nearest centroid → fallback 시 P4 의 `pca1d` 와 identical
- **즉시 조치 (paper-exact 정합성)**:
  - `neurocard_lite` → `pca8_kmeans` 로 renaming + `neurocard_lite` 변종 별도 구현 또는 본 method 제거
  - `factor_join` → `pca2d_grid` 로 renaming + `factor_join` 변종 별도 구현 또는 본 method 제거
  - `pq`/`opq` → md5 hash 단계 제거하고 codeword id 직접 사용 (M=1, nbits=ceil(log2(20))=5 → 32 codeword % 20)
  - `cocluster_nystrom` → fallback 발현 빈도 instrumentation (log) + 명칭에 "(simplified)" 또는 "biclustering_only" 명시

P6 5개 method 모두 본 연구의 V7 limitation `Reservoir RANDOM20 proxy / LSH K=20 vs n_hp=5 misalignment / sparse_rp Li 2006 1/√D variant` 동급의 **naming-implementation gap** 사례에 추가되어야 함. 특히 neurocard_lite, factor_join 는 reviewer 가 paper 이름 보고 결과 해석할 때 100% 오해할 가능성 있음 → 보고서 v8 limitation table 에 명시 필수.

---

## 0. 검증 방법론

각 method 별 5단계 검증:
1. **원전 알고리즘 요약** — paper 의 핵심 수식/단계
2. **본 구현 코드 verbatim 인용** + 단계별 의미 해석
3. **원전 vs 구현 gap 분석** — 어떤 step 가 누락/대체/단순화 됐는지
4. **n_strata=20 매핑 정당성** — output 이 20-way stratification 으로 collapse 되는 과정이 의미 보존하는가
5. **결함 list (severity)** + 권고

CaseA(분포-인지 baseline) vs CaseB(분포-인지 stratification) 적합성도 method 별로 명시.

---

## 1. `pq` (Product Quantization, Jegou et al. 2011)

### 1.1 원전 (Jegou, Douze, Schmid 2011)

PQ 알고리즘:
- 입력: vector `x ∈ R^D`
- D 차원을 M개의 sub-vector 로 split: `x = [x⁽¹⁾, x⁽²⁾, ..., x⁽ᴹ⁾]`, 각 `x⁽ᵐ⁾ ∈ R^(D/M)`
- 각 sub-space 별 k-means quantizer 학습: `q_m: R^(D/M) → C_m`, `|C_m| = K = 2^nbits`
- encode: `pq(x) = (q_1(x⁽¹⁾), ..., q_M(x⁽ᴹ⁾)) ∈ {0,...,K-1}^M`
- 즉 PQ code 는 **M-tuple of codeword id**, code space size = K^M

→ **학술적 stratum 의미**: 각 sub-space 의 sub-vector 가 어느 codeword 에 가까운지 조합. 만약 stratification 으로 사용한다면, 첫 sub-vector 의 codeword id 로 K-way 분할하거나, 두 sub-vector tuple 로 K²-way 분할 후 modulo. **distance-preserving** 성질이 핵심.

faiss API:
- `IndexPQ(d, M, nbits)`: M sub-spaces × 2^nbits codes per subspace
- `train(xs)`: 각 sub-space 별 k-means 학습
- `sa_encode(xs)`: vector 당 `M * ceil(nbits/8)` byte string 반환 (nbits=5 → ceil(5/8)=1 byte per sub-code, packed)
- 실제로 nbits 가 4의 배수가 아니면 byte packing 발현 — `sa_encode` 의 byte string 자체는 raw codeword 가 아니라 **bit-packed** 형태

### 1.2 본 구현 (line 519-532)

```python
if method_name == "pq":
    # Product Quantization — faiss IndexPQ + cluster id
    import faiss
    # M sub-vectors × log2(n_strata) bits
    M = max(2, all_vecs.shape[1] // 16)
    nbits = max(4, int(np.ceil(np.log2(n_strata))))
    pq_index = faiss.IndexPQ(all_vecs.shape[1], M, nbits)
    train = all_vecs[: min(len(all_vecs), 200_000)].astype(np.float32)
    pq_index.train(train)
    codes = pq_index.sa_encode(all_vecs.astype(np.float32))
    # Hash codes → bucket
    from hashlib import md5
    sids = np.array([int(md5(c.tobytes()).hexdigest()[:4], 16) % n_strata for c in codes], dtype=np.int32)
    return sids
```

dataset 별 hyperparam (D=차원수):
| dataset | D | M = D//16 | nbits | code length (bytes) |
|---|---|---|---|---|
| DEEP | 96 | 6 | 5 | ceil(6×5/8)=4 byte |
| SIFT | 128 | 8 | 5 | ceil(8×5/8)=5 byte |
| SSN | 256 | 16 | 5 | ceil(16×5/8)=10 byte |
| YFCC | 96 | 6 | 5 | 4 byte |
| WIKI | 768 | 48 | 5 | ceil(48×5/8)=30 byte |

### 1.3 원전 vs 구현 gap

| step | 원전 (Jegou 2011) | 본 구현 | gap |
|---|---|---|---|
| sub-space split | M개 sub-space | `IndexPQ(D, M, 5)` | OK |
| sub-space k-means | 각 sub-space 별 k=2^nbits | `pq_index.train()` | OK |
| stratum 정의 | tuple of codewords (M-dim) 또는 첫 codeword | **md5 hash → modulo 20** | **CRITICAL** |
| n_strata=20 mapping | 32^M 또는 32 codeword 를 20 으로 압축 | hash bucket | distance 정보 완전 소실 |

**핵심 문제**:
- `sa_encode` 가 반환하는 byte string 은 codeword 의 bit-packed serialization. 하지만 본 구현은 그 byte string 을 **md5 cryptographic hash** 의 input 으로 사용 → md5 의 의도가 "uniform random hashing" 이라 **PQ 의 distance-preserving 구조를 random 분산**
- 즉 결과적으로 `pq` method 는 사실상 "PQ encode 를 random hash 로 다시 mapping" 한 형태이므로, paper 의 PQ 의도(분포-인지 quantization)가 **0% 보존**됨
- 만약 PQ 의 distance-preserving 효과를 stratification 에 활용하려 했다면:
  - **option A**: M=1 (single sub-space), nbits=5 (32 codeword) → `pq_index.sa_encode()` 첫 byte 의 `& 0x1F` mask → modulo 20
  - **option B**: M=2, nbits=5 → first sub-codeword 만 32-way → modulo 20
  - **option C**: 전체 M sub-codeword 를 모두 사용해 K^M = 32^M 공간을 lloyd-style relabel 후 20-way recluster
- 본 구현은 위 어느 것도 아님 — **md5 hash 가 의미 없는 random mapping**

### 1.4 n_strata=20 매핑 정당성

**부적절**. md5 hash 는 PQ codeword 의 sub-space 별 cluster id 정보를 random uniform 으로 흩뿌림. 결과적으로 P6 의 `pq` 는 essentially:

```
all_vecs → faiss.PQ encode → bytes → md5(bytes)[:4] hex → int % 20 = "deterministic random partition"
```

이는 P3 streaming paradigm 의 `reservoir`(random 20-way partition) 와 **수학적으로 매우 유사**. 차이점은 reservoir 는 numpy RNG 로, pq 는 md5(PQ_encoded_bytes) 로 random 을 만들었을 뿐. 단, pq 는 같은 vector 면 같은 stratum 으로 매핑하는 deterministic property 는 가지므로 reservoir 보다 stable.

### 1.5 hyperparam 적정성

| param | 본 구현 값 | paper 권장 | 평가 |
|---|---|---|---|
| M | D//16 (clamped to ≥2) | D=128 일 때 M=8 (paper) | OK |
| nbits | 5 (clamped to ≥4) | paper 8 (256 codes per subspace) | 낮음 |
| K = 2^nbits | 32 | 256 | nbits=5 는 stratum 20 에 맞춘 inferences — OK |

핵심 문제는 hyperparam 이 아니라 **md5 hash step** 이 PQ 효과 자체를 무효화.

### 1.6 CaseA/CaseB 적합성

- **CaseA (paper baseline / no stratification)**: 적합 X. PQ 자체가 이미 stratification 메커니즘이므로 baseline 으로 둘 수 없음.
- **CaseB (분포-인지 stratification)**: 적합 X (현재 구현). md5 hash 가 분포 정보를 파괴. **만약 hash 제거하면 CaseB 적합** (PQ 는 sub-space 별 k-means 라 부분적 분포-인지).

### 1.7 결함 list

| # | severity | 결함 | 학술 영향 |
|---|---|---|---|
| 1 | **critical** | md5 hash 가 PQ 의 distance-preserving 구조 완전 파괴 | "PQ method" 라는 naming 이 실제 동작과 0% 일치. paper 이름 보고 결과 해석한 reviewer 100% 오해 |
| 2 | minor | nbits=5 (paper 권장 8 미만) | 본 연구는 n_strata=20 에 맞춘 의도적 선택 — 정당화 가능 |
| 3 | minor | sa_encode 의 byte packing 처리 미고려 (md5 input 의 byte 의미 모호) | hash 가 어차피 random 이므로 추가 영향은 0 |

### 1.8 권고

**Option 1 (immediate fix)**: md5 hash 단계 제거 + codeword id 직접 사용
```python
M = 1  # single sub-space → first sub-codeword == full quantization id
nbits = 5
pq_index = faiss.IndexPQ(D, 1, 5)
pq_index.train(train)
codes = pq_index.sa_encode(all_vecs)  # 1 byte per vector
sids = np.frombuffer(codes.tobytes(), dtype=np.uint8) & 0x1F  # 5 bits → 0..31
return (sids % 20).astype(np.int32)
```

**Option 2 (paper-faithful)**: M=8 (or D//16), nbits=8 → first sub-codeword 만 사용
```python
codes = pq_index.sa_encode(all_vecs)
# first byte = first sub-vector codeword (256-way)
sids = codes[:, 0] % 20
```

본 연구가 RQ3 보고서에서 "PQ" 결과를 해석할 때 위 둘 중 하나로 재측정 후, 현재 md5 hash 변종을 limitation 으로 명시.

### 1.9 종합 충실도 점수

**1.5 / 10**

PQ 의 핵심 알고리즘(sub-space k-means) 은 호출되지만, output 을 md5 hash 로 random 화하므로 PQ 의 학술적 의미가 완전 소실. naming 만 PQ.

---

## 2. `opq` (Optimized Product Quantization, Ge et al. 2013)

### 2.1 원전 (Ge, He, Ke, Sun 2013)

OPQ:
- PQ 의 약점 = "임의 D 차원 split 이 sub-space 간 dependency 무시" → quantization error 증가
- OPQ 는 PQ 전에 **rotation matrix R ∈ R^(D×D)** 을 학습하여 sub-space 간 independence 최대화
- 학습:
  1. R 초기화 (random rotation 또는 PCA-based)
  2. PQ codebook 학습 on R·x
  3. R 갱신 (closed-form Procrustes 또는 gradient)
  4. 반복 수렴까지
- encode: `opq(x) = pq(R·x)` — 즉 rotation 후 PQ encode

faiss 구현:
- `OPQMatrix(d, M)`: rotation matrix 학습용 transform
- `IndexPQ(d, M, nbits)`: PQ index
- `IndexPreTransform(opq, pq_index)`: rotation → PQ pipeline 자동 결합
- `index.train(xs)`: opq + pq 둘 다 jointly 학습
- `index.sa_encode(xs)`: rotation 적용 후 PQ encode (rotation 이 자동 적용)

핵심: **`pq_index` 에 직접 sa_encode 호출하면 rotation 미적용** — `IndexPreTransform` 의 sa_encode 또는 `pq_index.sa_encode(opq_matrix.apply(xs))` 사용해야 함.

### 2.2 본 구현 (line 605-617)

```python
if method_name == "opq":
    # OPQ — faiss IndexPreTransform with PCA + PQ
    import faiss
    M = max(2, all_vecs.shape[1] // 16)
    nbits = max(4, int(np.ceil(np.log2(n_strata))))
    opq_matrix = faiss.OPQMatrix(all_vecs.shape[1], M)
    pq_index = faiss.IndexPQ(all_vecs.shape[1], M, nbits)
    index = faiss.IndexPreTransform(opq_matrix, pq_index)
    train = all_vecs[: min(len(all_vecs), 200_000)].astype(np.float32)
    index.train(train)
    codes = pq_index.sa_encode(opq_matrix.apply(all_vecs.astype(np.float32)))
    from hashlib import md5
    return np.array([int(md5(c.tobytes()).hexdigest()[:4], 16) % n_strata for c in codes], dtype=np.int32)
```

### 2.3 원전 vs 구현 gap

| step | 원전 (Ge 2013) | 본 구현 | gap |
|---|---|---|---|
| OPQMatrix 학습 | rotation R ∈ R^(D×D) | `OPQMatrix(D, M)` train | OK (faiss 내부 학습) |
| PQ codebook 학습 on R·x | jointly 학습 | `index.train(train)` (PreTransform 통해 jointly) | OK |
| encode | `pq_encode(R·x)` | `pq_index.sa_encode(opq_matrix.apply(xs))` | **모호** — line 615 |
| stratum 정의 | M-tuple codewords | **md5 hash → modulo 20** | **CRITICAL** (PQ와 동일 결함) |

**의심 1 — line 615 의 sa_encode 호출 경로**:
`pq_index.sa_encode(opq_matrix.apply(...))` 는 명시적으로 rotation 적용 후 PQ encode 이므로, **rotation 적용 자체는 일어남** (apply 호출). 단, `index.sa_encode(...)` 를 사용하는 것이 더 표준적이며, 두 호출이 동일한 결과를 보장하는지는 faiss 버전에 의존. (faiss 1.7+ 부터는 `IndexPreTransform.sa_encode` 가 chain 호출하므로 동등.)

**의심 2 — md5 hash (PQ 와 동일 문제)**:
PQ 와 동일하게 `sa_encode` 결과 byte string 을 md5 로 random 화 → OPQ rotation 의 효과를 완전 흩뿌림. 사실상 "OPQ encoded → random hash" = 이름만 OPQ.

### 2.4 n_strata=20 매핑 정당성

**부적절** (PQ 와 동일 이유). OPQ 의 rotation + sub-space k-means 학습 효과가 md5 hash 로 random uniform 분산.

### 2.5 hyperparam 적정성

| param | 본 구현 값 | paper 권장 | 평가 |
|---|---|---|---|
| M | D//16 | paper 8 (D=128) | OK |
| nbits | 5 | paper 8 | n_strata=20 매칭 |
| OPQMatrix.niter | faiss default (50?) | paper 50 iter | OK (default 사용) |

### 2.6 CaseA/CaseB 적합성

PQ 와 동일: 현재 구현(md5 hash 포함)은 CaseA/CaseB 어느 것에도 부적합. hash 제거 시 CaseB 적합.

### 2.7 결함 list

| # | severity | 결함 |
|---|---|---|
| 1 | **critical** | md5 hash 가 OPQ 의 rotation + PQ 효과 완전 파괴 (PQ 와 동일) |
| 2 | moderate | `pq_index.sa_encode(opq_matrix.apply(...))` 호출 — `index.sa_encode(...)` 가 더 표준 (동등하나 코드 의도 모호) |
| 3 | minor | OPQMatrix 학습 iter 수 명시 X (faiss default 의존) |

### 2.8 권고

PQ 의 권고와 동일 (md5 hash 제거 + codeword id 직접 사용). 추가로:
- `index.sa_encode(all_vecs)` 형태로 변경 (PreTransform 의 의도된 호출 방식)
- OPQ 학습 iter 수를 명시적으로 `OPQMatrix.niter = 50` 설정 (재현성)

```python
# Recommended fix
opq_matrix = faiss.OPQMatrix(D, M=1)  # single sub-space for direct codeword id
opq_matrix.niter = 50
pq_index = faiss.IndexPQ(D, 1, 5)  # 32 codewords
index = faiss.IndexPreTransform(opq_matrix, pq_index)
index.train(train)
codes = index.sa_encode(all_vecs)
sids = (np.frombuffer(codes.tobytes(), dtype=np.uint8) & 0x1F) % 20
```

### 2.9 종합 충실도 점수

**1.5 / 10**

OPQ 의 rotation 학습은 호출되지만, output 을 md5 hash 로 random 화하므로 OPQ 의 학술적 의미 완전 소실. PQ 와 동일.

---

## 3. `neurocard_lite` (NeuroCard, Yang et al. 2020 — naming-only)

### 3.1 원전 (Yang et al. 2020)

NeuroCard:
- transformer-based **autoregressive density estimator** for multi-attribute joint distributions
- training: full joint sample 으로 `p(x_1, ..., x_d) = ∏_i p(x_i | x_1, ..., x_{i-1})` 학습
- inference: query predicate 의 selectivity 를 sample-and-marginalize 로 추정
- 핵심 contribution: **single model for all tables** (cross-table generalization). Multi-attribute discrete + continuous mixed.
- 학술적 stratum 의미: 만약 NeuroCard 의 latent representation 을 stratification 으로 쓴다면, transformer 의 hidden state 마지막 layer 를 cluster 하는 것이 가장 가까움.

### 3.2 본 구현 (line 705-714)

```python
if method_name == "neurocard_lite":
    # NeuroCard-lite: small MLP latent log-density bin → 단순화 PCA1D + KMeans
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    pca = PCA(n_components=min(8, all_vecs.shape[1]), random_state=seed)
    pca_vecs = pca.fit_transform(all_vecs[: min(len(all_vecs), 50_000)])
    km = KMeans(n_clusters=n_strata, random_state=seed, n_init=2, max_iter=20)
    km.fit(pca_vecs)
    all_pca = pca.transform(all_vecs)
    return km.predict(all_pca).astype(np.int32)
```

### 3.3 원전 vs 구현 gap

| step | 원전 (NeuroCard 2020) | 본 구현 | gap |
|---|---|---|---|
| Density model | transformer autoregressive | **PCA(8) + KMeans(20)** | **CRITICAL — 완전 무관 알고리즘** |
| Training | maximum likelihood on tabular data | unsupervised PCA + Lloyd | NeuroCard 의 likelihood 학습 부재 |
| Latent representation | transformer hidden state | PCA 8-dim subspace | dim reduction 만 동일하나 unrelated |
| Stratum 정의 | (NeuroCard 자체엔 stratum 개념 없음) | KMeans cluster id | NeuroCard 와 무관 |

주석 자체에 명시: "small MLP latent log-density bin → **단순화 PCA1D + KMeans**". 즉 코드 작성자도 "NeuroCard 와 무관함" 을 인지한 상태로 naming.

비교:
- 본 구현의 `pca8_kmeans20` ≈ P1 paradigm 의 `minibatch` (KMeans only, no PCA) 의 변종
- 또는 P1 paradigm 의 `pca1d` + KMeans 조합

→ **P6 paradigm 에 들어있을 이유 0%**, 사실상 **P1 cluster paradigm 의 alias**.

### 3.4 n_strata=20 매핑 정당성

매핑 자체는 sklearn KMeans `n_clusters=20` 으로 자연스러움. 단, "NeuroCard" 라는 이름과 매핑 메커니즘이 무관.

### 3.5 hyperparam 적정성

| param | 본 구현 값 | NeuroCard paper | 평가 |
|---|---|---|---|
| n_components (PCA) | min(8, D) | (해당 없음 — NeuroCard 는 PCA X) | naming-impl gap |
| n_clusters (KMeans) | 20 | (해당 없음) | naming-impl gap |
| n_init | 2 | (해당 없음) | minor |
| max_iter | 20 | (해당 없음) | minor |

### 3.6 CaseA/CaseB 적합성

- **CaseA**: 부적합 (clustering 기반 stratification 이므로 baseline X)
- **CaseB**: PCA + KMeans 자체는 분포-인지 method → 적합. 단 **이름이 잘못됨** — `pca8_kmeans` 로 renaming 필수.

### 3.7 결함 list

| # | severity | 결함 |
|---|---|---|
| 1 | **critical** | NeuroCard 논문(transformer autoregressive density)과 0% 일치. naming misrepresentation 으로 reviewer 가 paper 이름 보고 결과 해석 시 100% 오해 |
| 2 | moderate | P1 cluster paradigm 의 명백한 alias 인데 P6 quantization 으로 분류 — taxonomy 부정합 |
| 3 | minor | sample size 50K hardcoded — 큰 dataset 에서 sample 의 distribution shift 영향 |

### 3.8 권고

**immediate fix**:

1. **renaming**: `neurocard_lite` → `pca8_kmeans` (또는 `pca8_kmeans_lite`) 로 method 이름 변경. 본 연구의 method registry 와 결과 보고서 양쪽 동시.

2. **paradigm 재분류**: P1 cluster paradigm 으로 이동 (P6 에서 제거).

3. **NeuroCard 진짜 구현 (선택사항)**:
   - 진짜 NeuroCard 변종이 필요하면, 별도 method `neurocard_real` 으로 transformer-based density estimator 구현.
   - 현실적 어려움: NeuroCard 는 PostgreSQL 의 tabular schema 를 가정하고, 본 연구는 vector data — schema mismatch.
   - **결론**: NeuroCard 변종은 본 연구 scope 에서 제외하고, 현재 method 는 `pca8_kmeans` 로 renaming.

4. **limitation 명시 in 보고서 v8**:
   ```markdown
   "[Limitation] neurocard_lite 는 본 연구에서 PCA(8) + KMeans(20) 으로 단순화 — 
   원전 NeuroCard (Yang et al. 2020) 의 transformer autoregressive density 와 무관.
   향후 본 연구 scope 외에서 진짜 NeuroCard 구현 필요."
   ```

### 3.9 종합 충실도 점수

**1.0 / 10**

NeuroCard 의 핵심 메커니즘(autoregressive density)과 0% 일치. naming 만 NeuroCard. 다만 PCA + KMeans 자체는 valid stratification 이므로 method 가치는 있음 (다른 이름으로 부르면).

---

## 4. `factor_join` (FactorJoin, Zhao et al. 2023 — naming-only)

### 4.1 원전 (Zhao et al. 2023)

FactorJoin:
- Probabilistic Graphical Model 기반 join cardinality estimator
- 핵심 idea: join graph 를 factor graph 로 분해, 각 join key 의 marginal histogram 을 곱셈하여 join cardinality 추정
- training: 각 table 의 join key 별 1D histogram 학습 + join graph 의 factor 분해
- inference: marginal product + correction term
- 학술적 의미: **join cardinality estimation** 에 특화. single-table 분포 estimation 은 NOT FactorJoin 의 contribution.
- stratum 의미: FactorJoin 자체엔 vector data stratification 개념 없음. 만약 강제로 매핑한다면, "factor 별 marginal bin id 의 product" 가 가까움.

### 4.2 본 구현 (line 737-749)

```python
if method_name == "factor_join":
    # FactorJoin: graphical factor product → simplify to PCA + bin
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2, random_state=seed)
    proj = pca.fit_transform(all_vecs)
    # 2D quantile grid (sqrt(n_strata) per axis)
    k = int(np.ceil(np.sqrt(n_strata)))
    e0 = np.quantile(proj[:, 0], np.linspace(0, 1, k + 1))
    e1 = np.quantile(proj[:, 1], np.linspace(0, 1, k + 1))
    e0[-1] += 1e-6; e1[-1] += 1e-6
    b0 = np.clip(np.searchsorted(e0[1:-1], proj[:, 0], side="right"), 0, k - 1)
    b1 = np.clip(np.searchsorted(e1[1:-1], proj[:, 1], side="right"), 0, k - 1)
    return ((b0 * k + b1) % n_strata).astype(np.int32)
```

`k = ceil(sqrt(20)) = ceil(4.47) = 5` → 5×5 = 25 bin → modulo 20 = 5 bin 이 wrap-around 됨 (bin 0~4 가 두 번 매핑됨).

### 4.3 원전 vs 구현 gap

| step | 원전 (FactorJoin 2023) | 본 구현 | gap |
|---|---|---|---|
| Factor graph | join graph 분해 | (없음 — single table) | **CRITICAL — 완전 무관** |
| Marginal histogram | join key 별 1D | PCA(2) 의 2D quantile grid | unrelated |
| Cardinality estimate | factor product | (해당 없음) | unrelated |
| Stratum 정의 | (FactorJoin 자체엔 X) | 2D bin id × 5 + 1D bin id | unrelated |

주석에 명시: "FactorJoin: graphical factor product → **simplify to PCA + bin**". 작성자 본인이 "단순화" 인정. 단 "simplify" 가 아니라 **complete replacement** 임 — PCA 2D + quantile grid 는 FactorJoin 알고리즘과 0% 일치.

비교:
- 본 구현 = `pca2d_grid` (2D PCA + 5×5 quantile bin)
- P4 dim reduction paradigm 의 `pca1d` (1D PCA + 20 quantile bin) 의 2D 변종
- 또는 P5 low-discrepancy paradigm 의 `tucker` (3D) 의 2D 축소

→ **P6 paradigm 에 들어있을 이유 0%**, 사실상 **P4 dim reduction paradigm 의 2D 변종**.

### 4.4 n_strata=20 매핑 정당성

5×5=25 bin → modulo 20 → bin 0~4 가 (0..4) 와 (20..24)→(0..4) 두 번 매핑. **non-uniform stratum 분포 발생**.

```
bin id 0~4: 두 번 매핑 (0..4 + 20..24%20 = 0..4) → 평균 약 2배 빈도
bin id 5~19: 한 번 매핑
```

수치 예시 (DEEP 1M vectors, uniform 가정):
- 5×5 grid 라면 bin 당 평균 40K vectors
- bin 0~4 는 80K (두 번 매핑), bin 5~19 는 40K → **2:1 imbalance**
- 이는 본 연구의 n_strata=20 stratified sampling 의 효율성을 저하시킴 (작은 stratum 에서 sample size 가 unequal)

### 4.5 hyperparam 적정성

| param | 본 구현 값 | 평가 |
|---|---|---|
| n_components (PCA) | 2 | 2D grid 위해 고정 — 의도적 |
| k (axis bin) | ceil(sqrt(20))=5 | 25→20 modulo 가 imbalanced |

→ **개선**: `k = floor(sqrt(20)) = 4` 로 4×4=16 bin (20 미만이라 modulo X) 또는 4×5=20 직접 매핑.

### 4.6 CaseA/CaseB 적합성

- **CaseA**: 부적합 (PCA 기반 stratification)
- **CaseB**: PCA(2) + 2D bin 자체는 분포-인지 method → 적합. 단 **이름이 잘못됨** — `pca2d_grid` 로 renaming.

### 4.7 결함 list

| # | severity | 결함 |
|---|---|---|
| 1 | **critical** | FactorJoin 논문(PGM factor graph + join cardinality)과 0% 일치. naming misrepresentation |
| 2 | moderate | P4 dim reduction paradigm 의 2D 변종인데 P6 quantization 으로 분류 — taxonomy 부정합 |
| 3 | moderate | k=5 로 25 bin 생성 후 modulo 20 → bin 0~4 가 2배 빈도 (stratum imbalance) |
| 4 | minor | PCA 학습이 전체 데이터에 fit (large-D dataset 에서 메모리 부담) — `fit_transform` 직접 호출 |

### 4.8 권고

**immediate fix**:

1. **renaming**: `factor_join` → `pca2d_grid` 또는 `pca2d_quantile_5x5_mod20`.

2. **paradigm 재분류**: P4 dim reduction paradigm 으로 이동.

3. **stratum imbalance 해결**: `k=4` 로 변경하여 4×4=16 bin (20 미만이므로 modulo 부적용, 단 stratum 4개 부족) 또는 4×5=20 직접 매핑:
   ```python
   k0 = 4; k1 = 5  # 4×5 = 20 directly
   e0 = np.quantile(proj[:, 0], np.linspace(0, 1, k0 + 1))
   e1 = np.quantile(proj[:, 1], np.linspace(0, 1, k1 + 1))
   b0 = np.clip(np.searchsorted(e0[1:-1], proj[:, 0], side="right"), 0, k0 - 1)
   b1 = np.clip(np.searchsorted(e1[1:-1], proj[:, 1], side="right"), 0, k1 - 1)
   return (b0 * k1 + b1).astype(np.int32)  # exactly 20 strata, balanced
   ```

4. **FactorJoin 진짜 구현**: 본 연구 scope 외 — vector data 에 join graph 개념 부재. 본 method 는 renaming 후 P4 로 이동.

5. **limitation 명시 in 보고서 v8** (NeuroCard 와 동급).

### 4.9 종합 충실도 점수

**1.0 / 10**

FactorJoin 의 핵심(PGM + join cardinality)과 0% 일치. naming 만 FactorJoin. PCA(2) + grid 자체는 valid stratification 이지만 다른 이름으로 부르면 됨.

---

## 5. `cocluster_nystrom` (Spectral Co-clustering + Nyström, Dhillon 2001 + Williams 2001)

### 5.1 원전 (Dhillon 2001 + Williams & Seeger 2001)

**Spectral Co-clustering (Dhillon 2001)**:
- 입력: bipartite graph (e.g., document-term matrix) `A ∈ R^(m×n)`
- normalized Laplacian 의 SVD 첫 K eigenvector 가 row clusters 와 column clusters 를 simultaneous 학습
- output: row label `r ∈ {0,...,K-1}^m`, column label `c ∈ {0,...,K-1}^n`
- 학술적 의미: **bipartite structure** 가 핵심. unipartite (vector-vector) 데이터에는 직접 적용 X.

**Nyström approximation (Williams & Seeger 2001)**:
- kernel matrix `K ∈ R^(N×N)` 을 small landmark set `m ≪ N` 으로 approximate
- `K ≈ K_{N,m} K_{m,m}^{-1} K_{m,N}^T`
- 큰 dataset 의 spectral embedding 을 효율적으로 계산
- 핵심: **landmark sampling** + **eigen-decomposition on small block**

**조합 의도 (cocluster_nystrom)**:
- 큰 dataset 에 spectral co-clustering 을 적용하기 위해 Nyström approx 사용
- Dhillon 의 bipartite spectral 을 Williams 의 Nyström 으로 scaling

### 5.2 본 구현 (line 769-793)

```python
if method_name == "cocluster_nystrom":
    # Bipartite SpectralCoclustering — simplify to spectral on small sample
    from sklearn.cluster import SpectralBiclustering
    sample = all_vecs[: min(len(all_vecs), 5_000)]
    try:
        n_row = max(2, int(np.sqrt(n_strata)))
        sb = SpectralBiclustering(n_clusters=(n_row, n_row), random_state=seed, n_init=1)
        sb.fit(sample)
        row_labels = sb.row_labels_
        # Compute centroids per row cluster
        centroids = np.array([sample[row_labels == k].mean(axis=0) for k in range(n_row)])
        sids_full = np.empty(len(all_vecs), dtype=np.int32)
        chunk = 100_000
        for i in range(0, len(all_vecs), chunk):
            d = np.linalg.norm(all_vecs[i:i+chunk, None, :] - centroids[None, :, :], axis=2)
            sids_full[i:i+chunk] = np.argmin(d, axis=1)
        return (sids_full % n_strata).astype(np.int32)
    except Exception:
        # Fallback: simple PCA bin
        from sklearn.decomposition import PCA
        pca = PCA(n_components=1, random_state=seed)
        proj = pca.fit_transform(all_vecs).flatten()
        edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
        edges[-1] += 1e-6
        return np.clip(np.searchsorted(edges[1:-1], proj, side="right"), 0, n_strata - 1).astype(np.int32)
```

`n_row = sqrt(20) = 4` (int cast) → 4×4 = 16 row clusters, 16 col clusters.

### 5.3 원전 vs 구현 gap

| step | 원전 (Dhillon + Williams) | 본 구현 | gap |
|---|---|---|---|
| Bipartite 입력 | row × col matrix | `all_vecs (N, D)` (unipartite) | **moderate** — vector data 를 bipartite 로 해석 시 row=sample, col=feature dim. sklearn `SpectralBiclustering` 가 자동으로 처리하나 학술적 의미 흐림 |
| Spectral Co-clustering | normalized Laplacian SVD | `SpectralBiclustering(n_clusters=(4,4))` | **partial** — `SpectralBiclustering` 는 Kluger 2003 (block-diagonal model), Dhillon 2001 의 **direct** spectral 와 다른 변종 |
| Nyström | landmark set + kernel approx | **없음** — 단지 5K sample 만 fit, 나머지는 nearest centroid | **CRITICAL** — Nyström 의 핵심 (kernel approximation + extension) 미구현 |
| Stratum 정의 | row cluster id | `sids_full % 20`, n_row=4 → 4 cluster 만 사용 | **moderate** — 16 row cluster 가 아니라 sqrt(20)=4 (int cast) 으로 인해 4 cluster만 매핑 |
| Fallback | (없음) | except 시 PCA1D bin | **CRITICAL** — fallback 발현 시 P4 의 `pca1d` 와 identical |

**의심 1 — `SpectralBiclustering` vs `SpectralCoclustering`**:
- sklearn 에는 두 알고리즘 별도: `SpectralBiclustering` (Kluger 2003 - block diagonal), `SpectralCoclustering` (Dhillon 2001)
- 본 구현은 `SpectralBiclustering` 사용 → Dhillon 의 direct spectral co-clustering 이 아님
- 즉 method 이름의 "cocluster" 부분이 잘못됨 (정확히는 "biclustering")

**의심 2 — Nyström 부재**:
- 5K sample 만 SpectralBiclustering 으로 fit 후, 나머지 N-5K vectors 는 centroid distance 로 nearest assign
- 이는 Nyström approximation 의 정의(kernel matrix 의 low-rank approx)와 무관 — 단순한 "sample-and-extend" pattern
- 만약 진짜 Nyström 이라면, `K_{N,5K}` kernel matrix 를 계산하고 그것의 eigen vector 를 5K 의 spectral embedding 으로 extend 해야 함

**의심 3 — n_row = sqrt(20) = 4 (int cast)**:
- `int(np.sqrt(20)) = int(4.47) = 4`
- 4×4 = 16 cluster, but stratum 은 `% 20` → 16 cluster id 가 그대로 0..15 로 매핑되고 stratum 16~19 는 비어있음
- 즉 실제로는 16-way stratification, 4 stratum 비어있음 → **stratum imbalance**

**의심 4 — fallback 발현 빈도**:
- `SpectralBiclustering` 가 5K sample 에서 numerical issue 발현 시 fallback 으로 PCA1D bin
- 발현 조건: sample 이 너무 sparse, eigenvalue degenerate, etc.
- 5K sample on D=96~768 dim dataset 에서 발현 빈도 측정 필요 — 만약 frequent 하면 `cocluster_nystrom` 은 essentially `pca1d`

### 5.4 n_strata=20 매핑 정당성

**부적절** (위 의심 3). 16-way stratification 에 4 stratum 비어있음.

`%n_strata` (20) 는 16 cluster 가 0..15 매핑이라 redundant. 만약 `n_row = ceil(sqrt(20)) = 5` 로 했다면 5×5=25 cluster → modulo 20 → bin 0~4 두 번 매핑 (factor_join 와 동일 문제).

**개선**: `n_row × n_col = exactly 20` (e.g., 4 × 5 = 20) 이면 imbalance 0.

### 5.5 hyperparam 적정성

| param | 본 구현 값 | 평가 |
|---|---|---|
| sample size | 5,000 | small-D (DEEP 96, SIFT 128) 는 OK, large-D (WIKI 768) 는 sparse |
| n_clusters | (4, 4) | 4×4=16 (n_strata=20 미달) |
| n_init | 1 | 안정성 부족 — 5+ 권장 |
| try-except | except Exception | 너무 광범위 — `LinAlgError` 같은 specific 으로 좁히는 것이 좋음 |

### 5.6 CaseA/CaseB 적합성

- **CaseA**: 부적합 (clustering 기반)
- **CaseB**: 정상 동작 시 분포-인지 → 적합. 단 fallback 발현 시 PCA1D = P4 와 동일 → CaseB B1 cell 의 결과 해석 모호.

### 5.7 결함 list

| # | severity | 결함 |
|---|---|---|
| 1 | **moderate** | Nyström approximation 미구현 — naming 의 "nystrom" 부분이 잘못. 실제로는 sample-and-extend pattern |
| 2 | **moderate** | `SpectralBiclustering` 사용 (Kluger 2003) — Dhillon 2001 의 `SpectralCoclustering` 와 다른 알고리즘. naming 의 "cocluster" 부분도 잘못 |
| 3 | **moderate** | n_row = int(sqrt(20)) = 4 → 16 cluster (n_strata=20 미달) — stratum imbalance |
| 4 | **moderate** | except Exception fallback 시 P4 의 pca1d 와 identical — 사실상 알고리즘 본질이 PCA1D 일 가능성 |
| 5 | minor | n_init=1 (sklearn SpectralBiclustering default 의 안정성 의심) |
| 6 | minor | 5K sample size 고정 (large-D dataset 에서 sparse) |

### 5.8 권고

**immediate fix**:

1. **renaming**: `cocluster_nystrom` → `biclustering_5k_centroid` 또는 `spectral_bi_4x4`. "Nystrom" 명칭 제거 (해당 알고리즘 미구현).

2. **stratum imbalance 해결**: `n_row × n_col = 4 × 5 = 20` 으로 변경:
   ```python
   sb = SpectralBiclustering(n_clusters=(4, 5), random_state=seed, n_init=1)
   ```

3. **fallback instrumentation**: fallback 발현 빈도 측정. 만약 빈번하면:
   - method 이름 변경 (`pca1d_with_bicluster_attempt`)
   - 또는 try-except 제거 후 fail 시 명시적 error

4. **진짜 Nyström 구현 (선택)**:
   ```python
   # Real Nyström: kernel approx
   from sklearn.kernel_approximation import Nystroem
   nys = Nystroem(kernel='rbf', n_components=200, random_state=seed)
   embedded = nys.fit_transform(all_vecs[:5000])
   # spectral cluster on embedded
   ...
   ```

5. **limitation 명시 in 보고서 v8**:
   ```markdown
   "[Limitation] cocluster_nystrom 은 본 연구에서 SpectralBiclustering on 5K sample + 
   nearest centroid 로 단순화 — Dhillon 2001 의 SpectralCoclustering 도 아니고 
   Williams 2001 의 Nyström approximation 도 미구현. fallback 발현 시 PCA1D 와 동일."
   ```

### 5.9 종합 충실도 점수

**3.0 / 10**

`SpectralBiclustering` 자체는 spectral clustering 의 한 변종이라 부분적 의미는 있음. 단:
- "cocluster" 명칭 → biclustering 이라 부분 mismatch
- "nystrom" 명칭 → 0% 일치 (Nyström 미구현)
- fallback 발현 가능성

다른 4 method (PQ/OPQ/neurocard_lite/factor_join) 대비 가장 학술적 정합성 있음.

---

## 6. 종합 비교 표

### 6.1 method 별 충실도 점수

| # | method | 충실도 (1-10) | naming 정합성 | 알고리즘 정합성 | 주 결함 |
|---|---|---|---|---|---|
| 1 | pq | 1.5 | partial | 30% | md5 hash 가 PQ 효과 무효화 |
| 2 | opq | 1.5 | partial | 30% | md5 hash 가 OPQ 효과 무효화 |
| 3 | neurocard_lite | 1.0 | **0%** | 0% | NeuroCard 와 완전 무관 (PCA+KMeans alias) |
| 4 | factor_join | 1.0 | **0%** | 0% | FactorJoin 과 완전 무관 (PCA2D grid alias) |
| 5 | cocluster_nystrom | 3.0 | partial | 50% | Nyström 미구현, fallback 시 pca1d |
| **평균** | | **1.6** | **20%** | **22%** | |

note: "충실도" 는 원전 알고리즘과 본 구현의 일치도. "naming 정합성" 은 method 이름이 실제 동작을 정확히 표현하는가.

### 6.2 paradigm taxonomy 부정합

| method | 현재 paradigm | 실제 알고리즘 본질 | 권장 paradigm |
|---|---|---|---|
| pq | P6 quantization | (md5 hash 후 random) | P3 streaming 의 reservoir 와 유사 |
| opq | P6 quantization | (md5 hash 후 random) | P3 streaming 의 reservoir 와 유사 |
| neurocard_lite | P6 quantization | PCA + KMeans | **P1 cluster** |
| factor_join | P6 quantization | PCA(2) + 2D grid | **P4 dim reduction** |
| cocluster_nystrom | P6 quantization | SpectralBiclustering on 5K + centroid | P1 cluster (spectral 변종) |

P6 paradigm 자체가 "quantization/other" 라는 catch-all 로, 실제로는 5개 method 모두 다른 paradigm 에 속함. **P6 paradigm 의 존재 자체에 의문** — 본 연구의 "5 paradigm × 11 method framework" 의 paradigm boundary 가 모호.

### 6.3 결함 severity summary

| severity | 건수 | method 별 |
|---|---|---|
| critical | 4 | pq (md5), opq (md5), neurocard_lite (naming), factor_join (naming) |
| moderate | 6 | opq (sa_encode 호출), neurocard_lite (taxonomy), factor_join (taxonomy + imbalance), cocluster_nystrom (Nyström, biclustering, n_row, fallback) |
| minor | 7 | pq (nbits, byte packing), opq (niter), neurocard_lite (sample size), factor_join (PCA fit), cocluster_nystrom (n_init, sample size) |

---

## 7. 종합 권고

### 7.1 즉시 조치 (paper-exact 정합성, P0)

P6 5 method 모두 method 이름이 paper title 과 misleading → **반드시 rename 또는 본 연구에서 제외**.

| method | 즉시 조치 | 후속 |
|---|---|---|
| pq | md5 hash 제거, codeword id 직접 사용 | 충실도 7/10 까지 가능 |
| opq | md5 hash 제거, `index.sa_encode` 사용 + niter 명시 | 충실도 7/10 까지 가능 |
| neurocard_lite | `pca8_kmeans` 로 rename + P1 으로 paradigm 이동 | 본 연구에서 NeuroCard 변종 제거 |
| factor_join | `pca2d_grid` 로 rename + P4 로 paradigm 이동 + k=4×5=20 으로 stratum imbalance 제거 | 본 연구에서 FactorJoin 변종 제거 |
| cocluster_nystrom | `biclustering_5k_centroid` 로 rename + n_row=(4,5)=20 + fallback instrumentation | "Nystrom" 명칭 제거 |

### 7.2 보고서 v8 limitation table 추가

본 연구의 V7 limitation 섹션 (`Reservoir RANDOM20 proxy / LSH K=20 vs n_hp=5 misalignment / sparse_rp Li 2006 1/√D variant`) 에 P6 5 항목 추가:

```markdown
[V8 limitation table 추가]
- P6.1 PQ: faiss IndexPQ encode → md5 hash → modulo 20. PQ 의 distance-preserving structure 미반영.
- P6.2 OPQ: P6.1 + rotation matrix. md5 hash 동일 결함.
- P6.3 NeuroCard-lite: NeuroCard (Yang 2020) 의 transformer autoregressive density 미구현. 본 연구에선 PCA(8) + KMeans(20) — 이름은 NeuroCard, 실제는 P1 cluster 변종.
- P6.4 FactorJoin: FactorJoin (Zhao 2023) 의 PGM factor graph 미구현. 본 연구에선 PCA(2) + 5×5 quantile grid % 20 — 이름은 FactorJoin, 실제는 P4 dim reduction 2D 변종.
- P6.5 CoCluster-Nystrom: Williams 2001 의 Nyström approximation 미구현, Dhillon 2001 의 SpectralCoclustering 가 아닌 Kluger 2003 의 SpectralBiclustering 사용 + sample-and-extend.
```

### 7.3 paradigm taxonomy 재검토

P6 5 method 모두 다른 paradigm 의 명백한 alias 이므로 **P6 paradigm 자체 폐지** 제안:

| 현재 분류 | 실제 분류 |
|---|---|
| P1 cluster (5 method) | P1 cluster (5 + neurocard_lite, cocluster_nystrom = 7) |
| P2 spatial | P2 spatial |
| P3 streaming | P3 streaming (+ pq, opq 가 사실상 random hash 이므로 후보) |
| P4 dim reduction | P4 dim reduction (+ factor_join = 2D PCA 변종) |
| P5 low-discrepancy | P5 low-discrepancy |
| ~~P6 quantization/other~~ | **폐지** (또는 PQ/OPQ 의 hash 제거 후 진짜 quantization 만 남김) |

본 연구가 "5 paradigm × 11 method" 로 보고서 작성 중이라면 P6 폐지 후 4 paradigm 으로 축소하거나, P6 를 진짜 quantization 만 (PQ/OPQ 의 hash-free 변종) 남기는 것이 paradigm boundary 의 학술적 명료성에 도움.

### 7.4 paper-exact 측정 시 우선순위

본 검증 결과는 메인 세션의 paper exact 재현 측정과는 **별도 audit**. 만약 메인 세션에서 paper-exact 측정 진행 중이라면:

1. **즉시 stop 안 해도 됨** — 본 검증은 algorithm correctness 이고, paper-exact 는 paper 의 hyperparam/queries/threshold 재현. 양자 별 issue.
2. **단, 결과 보고 시 caveat 필수**: P6 5 method 의 결과를 reviewer 에게 제시할 때 위 limitation 을 명시.
3. **차후 v9 redesign 시**: P6 5 method 를 위 권고대로 rename + 진짜 구현 또는 폐지 결정.

### 7.5 최우선 fix 1개 (single-blocking issue)

**`neurocard_lite` 와 `factor_join` 의 naming 변경**:

이 둘은 paper title 과 0% 일치인데 method 이름이 paper title 그대로 → **reviewer 가 결과 표 보고 "NeuroCard 가 SIFT 에서 X% 정확도" 라고 해석 시 100% 오해**. 반면 PQ/OPQ 는 naming-impl 일치 (faiss API 호출 자체는 일어남), cocluster_nystrom 은 부분 일치.

immediate action (1줄 변경):

```python
# Before
if method_name == "neurocard_lite":
# After
if method_name == "pca8_kmeans":  # was: neurocard_lite (misleading naming, see audit P6)
```

method registry 와 result CSV column 명칭 동시 변경.

---

## 8. 검증 절차 재현

본 audit 의 재현 가능성을 위해:

```bash
# 1. file 위치
/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py

# 2. line range
- pq: 519-532
- opq: 605-617
- neurocard_lite: 705-714
- factor_join: 737-749
- cocluster_nystrom: 769-793

# 3. 핵심 조사 항목
- faiss.IndexPQ.sa_encode 의 byte semantics → faiss official docs
- sklearn SpectralBiclustering vs SpectralCoclustering → sklearn API docs
- NeuroCard 원전 → arXiv 2006.08109 (Yang 2020)
- FactorJoin 원전 → arXiv 2212.05526 (Zhao 2023 SIGMOD)
- PQ 원전 → IEEE TPAMI 2011 (Jegou 2011)
- OPQ 원전 → IEEE TPAMI 2014 (Ge 2013, journal version)
- Dhillon 2001 → KDD 2001 "Co-clustering documents..."
- Williams & Seeger 2001 → NeurIPS 2001 "Using Nyström method..."

# 4. 검증 명령어 (sanity check on small sample)
python3 -c "
import numpy as np
from hashlib import md5
# Simulate pq output
codes = np.random.RandomState(42).bytes(100 * 5).reshape(100, 5)
sids = np.array([int(md5(c.tobytes()).hexdigest()[:4], 16) % 20 for c in codes])
print('pq sids distribution (100 vectors):', np.bincount(sids, minlength=20))
# expect: roughly uniform — confirms md5 hash randomizes regardless of PQ encode
"
```

기대: md5 hash 결과가 PQ encode 와 무관하게 uniform 분포 (~5 per stratum) → md5 가 PQ 정보를 random 화 한다는 검증.

---

## 9. 마무리 — 본 연구 학술 가치 보존을 위한 minimum action

본 연구가 KDD/VLDB/SIGMOD 급 학술지 제출이 목표라면, P6 5 method 의 naming-impl gap 은 **reviewer 의 첫 reject 사유** 가 될 가능성 높음. 특히 NeuroCard 와 FactorJoin 은 cardinality estimation 분야의 well-known paper 이므로 reviewer 들이 paper 이름 보고 즉시 알아챔.

**absolute minimum action** (학술 가치 보존):

1. method registry 의 `neurocard_lite`, `factor_join` 명칭 즉시 변경 (15분 작업).
2. 보고서/PPT 의 result table column 명 동시 변경.
3. 보고서 v8 의 limitation 섹션에 P6 5 항목 명시.
4. PQ/OPQ 의 md5 hash 제거 fix 는 caponable (실험 재측정 필요하나 코드 fix 자체는 30분).
5. cocluster_nystrom 의 n_row=(4,5) fix 는 1줄 변경 (5분).

총 1시간 fix 로 학술 정합성 위험 90% 감소 가능.

---

**검증 완료**: 2026-05-10 KST
**검증자**: P6 (Quantization/Other paradigm) audit agent
**다음 단계**: 메인 세션에 본 보고서 전달 → 보고서 v8 limitation 섹션 반영 + paper-exact 측정 재개 후 caveat 명시
