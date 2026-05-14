# Phase 2 Final — Cascade 통과 11 Method 상세 spec

> 작성: 2026-05-11 01:30 KST (Phase 4 별도 세션, 메인 chain bvf1k64kw 영향 0)
> Input: `_FILTER_ANALYSIS.md` Stage 7 결과
> 다음: Phase 3 implementation (사용자 confirm 후)

---

## 0. Final 11 method overview

| # | Code | method | reference | paradigm | 예상 Δ% | line | ETA / cell | priority |
|---|---|---|---|---|---|---|---|---|
| 1 | M1 | Chao weighted reservoir | Chao 1982 JRSS | P3 (weight) | -3 ~ -7% | ~50 | 30 min | **★ P0** |
| 2 | M2 | LPM1 (proper Grafström) | Grafström 2012 Biometrics | P2+P3 | -3 ~ -7% | ~250 | 1 h | **★ P0** (lpm2 misnomer rectify) |
| 3 | M3 | Cum-√f rule | Dalenius-Hodges 1959 JASA | P5+RQ2 | -2 ~ -5% | ~100 | 30 min | **★ P1** |
| 4 | M4 | Lavallée-Hidiroglou | Lavallée-Hidiroglou 1988 | P5+RQ2 | -2 ~ -5% | ~150 | 1 h | **★ P1** |
| 5 | M5 | iDistance | Jagadish-Ooi-Tan-Yu-Zhang TODS 2005 | P2 | -3 ~ -6% | ~100 | 30 min | **★ P0** |
| 6 | M6 | Z-order Morton | Morton IBM 1966 | P2 (anchor) | -3 ~ -7% | ~80 | 30 min | **★ P0** (paradigm anchor) |
| 7 | M7 | Skilling true high-D Hilbert | Skilling AIP 2004 | P2 (★3 rectify) | -3 ~ -7% | ~150 | 1 h | **★ P0** (Q1 (C)) |
| 8 | M8 | ICA FastICA | Hyvärinen NN 1999 | P4 | -2 ~ -6% | ~50 | 30 min | **★ P1** |
| 9 | M9 | KMeans + Neyman allocation | (synthesis Cochran §5 + Neyman 1934) | P1+RQ2 | -3 ~ -7% | ~100 | 30 min | **★ P0** (RQ2 plug-in) |
| 10 | M10 | RaBitQ stratification | Gao-Lin VLDB 2024 vol 17 p.3252 | P6 | -3 ~ -7% | ~150 | 1 h | **★ P1** (2024 fresh) |
| 11 | M11 | iDistance + Neyman | (synthesis Jagadish 2005 + Neyman 1934) | P2+RQ2 | -3 ~ -7% | ~100 | 30 min | **★ P0** (synthesis) |

총: ~1,330 line implementation, ~7 h smoke + 100 cells × 45 min × 11 = ~80 h measurement (병렬 시 12-15 h)

---

## 1. M1 — Chao weighted reservoir (Chao 1982)

### 1.1 Reference verbatim

Chao MT. "A general purpose unequal probability sampling plan." *Biometrika* 1982; 69(3):653-656.

### 1.2 Algorithm core

각 vector v_i 의 weight w_i (예: ||v_i||₂ or pca_proj_i) 를 priority queue 의 key 로 사용:

```
For each i ∈ [N]:
  u_i = uniform(0, 1)
  key_i = u_i^(1/w_i)   # exponential trick
Sample top-K by key_i
```

본 연구 weight 후보:
- (W1) ||v_i||₂ — L2 norm
- (W2) PCA1D projection (signed)
- (W3) iDistance from KM20 centroid

### 1.3 Complexity

- Time: O(N log K) priority queue insert
- Space: O(K)
- Dim: any (weight 만 univariate)

### 1.4 Chunked predict pattern (8M / 80M)

```python
import heapq
def chao_weighted_reservoir(vecs, K, weight_fn, seed):
    rng = np.random.default_rng(seed)
    heap = []  # min-heap of (key, idx)
    for i in range(0, len(vecs), 100_000):
        chunk = vecs[i:i+100_000]
        w = weight_fn(chunk)  # e.g. np.linalg.norm(chunk, axis=1)
        u = rng.random(len(chunk))
        key = u ** (1.0 / np.maximum(w, 1e-10))
        for j, k in enumerate(key):
            if len(heap) < K:
                heapq.heappush(heap, (k, i + j))
            elif k > heap[0][0]:
                heapq.heapreplace(heap, (k, i + j))
    return [idx for _, idx in heap]
```

### 1.5 본 narrative fit

- 현재 portfolio 의 reservoir (random20) 와 차별화: random uniform → weight-aware
- ★4 sparse_rp 의 distribution-agnostic 와 직교 (weight-aware bias)
- weight 선택 ablation → 3-way comparison (W1 norm / W2 PCA1D / W3 iDistance)

### 1.6 Redundancy check

- random20 (현재 reservoir): w_i = 1 동일 → distinct
- pca1d quantile: bin 기반 → distinct (continuous weighted)
- lpm2 (현재 misnomer): radial median → distinct

---

## 2. M2 — LPM1 proper Grafström (Local Pivotal Method)

### 2.1 Reference verbatim

Grafström A, Lundström NLP, Schelin L. "Spatially balanced sampling through the pivotal method." *Biometrics* 2012; 68(2):514-520.

### 2.2 Algorithm core

LPM1 = pairwise pivot 사이의 inclusion probability redistribution:

```
Initialize: π_i = K/N for all i (uniform inclusion prob)
While exists fractional π_i:
  Pick pair (i, j) with smallest Euclidean distance (spatially closest)
  Update π_i, π_j s.t. one is 0 or 1, other preserves sum:
    if π_i + π_j < 1: 
      with prob π_j/(π_i + π_j): π_i = π_i + π_j, π_j = 0
      else: π_j = π_i + π_j, π_i = 0
    else (>= 1):
      with prob (1-π_j)/(2-π_i-π_j): π_i = 1, π_j = π_i + π_j - 1
      else: π_j = 1, π_i = π_i + π_j - 1
```

### 2.3 Complexity

- Time: O(N²) pairwise (LPM1) → O(N log N) tree-based (LPM2 변형)
- Space: O(N) inclusion prob
- Dim: spatial Euclidean distance

본 연구는 8M scale → LPM2 tree-variant + chunk 적용:

```python
from sklearn.neighbors import BallTree  # high-D 가능
def lpm1_proper(vecs, K, seed):
    rng = np.random.default_rng(seed)
    pi = np.full(len(vecs), K / len(vecs))
    tree = BallTree(vecs[:50_000])  # subsample fit (spatial structure)
    selected = []
    fractional = list(range(len(vecs)))
    while fractional:
        # Pick random fractional + nearest
        idx_i = rng.choice(fractional)
        # ... (Grafström pivot redistribution)
    return selected
```

### 2.4 본 narrative fit

- 현재 lpm2 = Weiszfeld geometric median + radial bin (misnomer)
- LPM1 proper = pivot pair-wise redistribution (Grafström 본문)
- spatial well-spread + balanced inclusion prob — narrative fresh
- ★3 hilbert (PCA proxy) 와 다른 spatial bias

### 2.5 Redundancy check

- lpm2 (현재): radial bin — distinct (LPM 본문 부재)
- epsilon_net (== kdpp): farthest-first — distinct (cover 기반)
- distinct from M5 iDistance (1D distance) and M6/M7 SFC

---

## 3. M3 — Cum-√f rule (Dalenius-Hodges 1959)

### 3.1 Reference verbatim

Dalenius T, Hodges JL. "Minimum variance stratification." *Journal of the American Statistical Association* 1959; 54(285):88-101.

### 3.2 Algorithm core

univariate auxiliary variable y의 누적 √f(y) 를 K-1 등분으로 strata 경계:

```
1. Compute density f(y) histogram (M bins)
2. Cumulative √f: C(y) = ∫_{-∞}^y √f(t) dt
3. Strata bounds: y_h s.t. C(y_h) = h × C(max) / K, h=1..K-1
```

본 연구 응용: y = PCA1D(v_i) → Cum-√f bins 는 PCA1D quantile 보다 minimum variance 더 좋음 (paper 증명)

### 3.3 Complexity

- Time: O(N log N) sort + O(M) histogram + O(K) bin
- Space: O(N + M)
- Dim: univariate (PCA1D 후)

### 3.4 본 narrative fit

- pca1d (현재) = equi-quantile bin
- M3 Cum-√f = optimal minimum variance bin (Dalenius-Hodges proof)
- RQ2 + RQ3 anchor: optimal stratification + Neyman 결합 가능

### 3.5 Redundancy check

- pca1d 와 직교 (quantile vs cum-√f)
- M9 KMeans+Neyman 와 다른 axis (univariate optimal vs cluster-based)

---

## 4. M4 — Lavallée-Hidiroglou (take-all stratum + Neyman)

### 4.1 Reference verbatim

Lavallée P, Hidiroglou M. "On the stratification of skewed populations." *Survey Methodology* 1988; 14(1):33-43.

### 4.2 Algorithm core

extreme rare event (skew tail) 을 take-all stratum (1.0 inclusion prob) 으로 처리, 나머지는 Neyman:

```
1. Sort y_i descending
2. Take-all stratum: top T values (T 정도 small, e.g. 1-5%)
3. Remaining: K-1 strata via Cum-√f
4. Within remaining: Neyman allocation (n_h ∝ N_h × σ_h)
```

본 연구 응용: y = PCA1D — top 1% take-all + 19 strata Neyman

### 4.3 Complexity

- Time: O(N log N) sort + Cum-√f O(N) + Neyman O(N)
- Space: O(N)
- Dim: univariate

### 4.4 본 narrative fit

- skew dataset (SIFT, YFCC) 의 long-tail 처리 향상
- RQ2 Neyman 의 rare-event extension (selectivity 0.001)
- L-H paper 가 skew 분포 stratification textbook

### 4.5 Redundancy check

- Neyman (RQ2) 와 차별화: take-all 추가
- M3 Cum-√f 와 차별화: rare-event handling

---

## 5. M5 — iDistance (Jagadish 2005)

### 5.1 Reference verbatim

Jagadish HV, Ooi BC, Tan KL, Yu C, Zhang R. "iDistance: An adaptive B+-tree based indexing method for nearest neighbor search." *ACM Transactions on Database Systems* 2005; 30(2):364-397.

### 5.2 Algorithm core

reference 점 R_j (KMeans centroid 사용) 으로부터의 거리 d(v_i, R_j) 를 1D scalar 로 변환 + B+-tree 등 1D index:

```
1. Cluster vectors → K centroids R_1, ..., R_K
2. For each v_i: 
   y_i = j(v_i) × c + d(v_i, R_{j(v_i)})  # j: nearest centroid index, c: large constant
3. Stratify by y_i (quantile bin or Cum-√f)
```

본 연구 응용: K = n_strata = 20 centroids (KMeans20) + intra-cluster distance bin

### 5.3 Complexity

- Time: O(N·K) centroid distance + O(N log N) sort
- Space: O(N + K·D)
- Dim: any

### 5.4 본 narrative fit

- ★1 hdbscan (cluster) 와 차별화: distance-from-reference (continuous)
- pca1d (variance) 와 차별화: density/cluster-based 1D
- iDistance paper 는 high-D KNN search 에 효과 입증 → cardinality est. 직접 응용 신규

### 5.5 Redundancy check

- KMeans cluster id (minibatch/coreset) 와 차별화: continuous distance 추가
- pca1d 와 차별화: cluster-aware 1D

---

## 6. M6 — Z-order Morton (1966)

### 6.1 Reference verbatim

Morton GM. "A computer Oriented Geodetic Data Base; and a New Technique in File Sequencing." *IBM Ltd. Technical Report* (1966).

### 6.2 Algorithm core

low-D (≤8 dim) 좌표를 bit-interleave 하여 1D Z-order:

```
1. PCA-2D 또는 -3D 로 dim reduction
2. Each axis quantize to B bits (e.g. B=10, total 20-30 bits)
3. Interleave bits: z_i = bit(x_axis[0], y_axis[0], x_axis[1], y_axis[1], ...)
4. Sort z_i → strata
```

본 연구 응용: PCA-2D + 10-bit quantize per axis

### 6.3 Complexity

- Time: O(N·D) PCA + O(N) bit interleave
- Space: O(N)
- Dim: low-D (PCA reduction)

### 6.4 본 narrative fit

- ★3 hilbert (PCA 2D lex sort, defect) 와 직접 비교 paradigm anchor
- Z-order paradigm anchor: SFC 영역의 simplest baseline
- Hilbert 의 진짜 locality 효과 vs Z-order proxy 효과 분리 검증

### 6.5 Redundancy check

- ★3 hilbert (defect, lex sort) 와 distinct (interleave vs lex)
- M7 Skilling true Hilbert 와 distinct (Morton vs Hilbert recursion)

---

## 7. M7 — Skilling true high-D Hilbert curve (Skilling 2004)

### 7.1 Reference verbatim

Skilling J. "Programming the Hilbert curve." *AIP Conference Proceedings* 2004; 707:381-387.

### 7.2 Algorithm core

high-D Hilbert curve 의 state machine algorithm (Skilling Algorithm 137):

```
For each axis i ∈ [D]:
  Quantize v_i to B bits → x_i ∈ [0, 2^B)
For each step in Hilbert recursion:
  Apply state-machine transitions (rotate, reflect)
Output: Hilbert index h_i ∈ [0, 2^(B·D))
Sort by h_i → strata
```

본 연구 응용: high-D 직접 (no PCA 사전 reduction), DEEP 96d / SIFT 128d / SSN 256d

단, B (per-axis bit) 는 작게 (e.g. B=4) → 96d × 4 = 384 bit Hilbert key

### 7.3 Complexity

- Time: O(N·D·B) bit operations
- Space: O(N + 2^(B·D)) — borderline, B=4 D=96 = 2^384 ❌ — bin 개수 limit
- 실용: B=2 + dim=8 (PCA 후) = 256 bin OK

### 7.4 본 narrative fit

- Q1 (C) 권고: ★3 hilbert (PCA 2D lex sort, fraud risk) 정정
- Skilling true Hilbert vs PCA proxy 비교 = "Hilbert curve 의 진짜 locality 효과 vs PCA proxy 효과" 분리 검증 = 학술 contribution
- 단 high-D 8M scale infeasible → PCA-8 + Skilling 4-bit 조합 권고

### 7.5 Redundancy check

- ★3 hilbert (현재 PCA 2D lex sort) 와 distinct (true SFC vs lex sort)
- M6 Z-order Morton 와 distinct (Hilbert recursion vs bit interleave)

---

## 8. M8 — ICA FastICA (Hyvärinen 1999)

### 8.1 Reference verbatim

Hyvärinen A. "Fast and robust fixed-point algorithms for independent component analysis." *IEEE Transactions on Neural Networks* 1999; 10(3):626-634.

### 8.2 Algorithm core

PCA 와 다른 inductive bias: independence (kurtosis 또는 negentropy 최대화):

```
1. Whiten data: x = E[xx^T]^(-1/2) x
2. Initialize w (D-dim unit vector)
3. Repeat (until convergence):
   w_new = E[x g(w^T x)] - E[g'(w^T x)] w   # g = nonlinear (e.g., tanh, exp(-u^2/2))
   w_new = w_new / ||w_new||
4. y_i = w^T x_i (1D ICA projection)
5. Stratify y_i by quantile or Cum-√f
```

본 연구 응용: 1-component ICA (FastICA(n_components=1, fun='logcosh'))

### 8.3 Complexity

- Time: O(N·D·iter) iter ~10-50
- Space: O(N + D²)
- Dim: any (D < 1000 권고)

### 8.4 본 narrative fit

- pca1d (variance) 와 직교: ICA 는 independence (non-Gaussian) bias
- DEEP/SIFT (skew) 환경에서 PCA1D 보다 high-order moment capture 우수 가능성
- non-Gaussian distribution detection narrative

### 8.5 Redundancy check

- pca1d 와 distinct (variance vs independence)
- cca1d (== PCA1D whiten, defect) 와 distinct (FastICA non-Gaussian objective)
- neuram (== PCA1D, defect) 와 distinct

---

## 9. M9 — KMeans + Neyman allocation

### 9.1 Reference verbatim

Synthesis: Cochran 1977 *Sampling Techniques* §5 (Neyman allocation) + MacQueen 1967 (KMeans). Specific synthesis: Lohr 2010 *Sampling: Design and Analysis* §3-§4.

### 9.2 Algorithm core

KMeans20 cluster 내 σ_h 계산 후 Neyman allocation:

```
1. KMeans(K=20) → cluster id c_i ∈ [0, 20)
2. Per cluster h: σ_h = std(D_target(v_i) for i in cluster h)
   where D_target = paper 정의 query selection threshold distance
3. Neyman: n_h = (N_h × σ_h) / Σ_h (N_h × σ_h) × n_total
4. Sample n_h from cluster h
```

본 연구 응용: 현재 RQ2 Neyman 은 KM20 baseline에서 수행 — KMeans + Neyman 직접 비교

### 9.3 Complexity

- Time: O(N·K·D) KMeans + O(N) σ_h
- Space: O(N + K·D)
- Dim: any

### 9.4 본 narrative fit

- RQ2 (Neyman) + RQ3 (cluster) 직접 결합
- ★1 hdbscan vs ★ KMeans + Neyman 비교 → cluster method × allocation 의 2D ablation
- handoff_main §11.5 사용자 명시 "RQ2 Neyman/Anti-Neyman paper exact 추가" 와 align

### 9.5 Redundancy check

- minibatch (cluster id only) 와 distinct (Neyman σ allocation 추가)
- O1 hybrid 와 동일 → consolidate to M9

---

## 10. M10 — RaBitQ stratification (Gao-Lin 2024)

### 10.1 Reference verbatim

Gao J, Lin C. "RaBitQ: Quantizing high-dimensional vectors with a theoretical error bound for approximate nearest neighbor search." *Proc. VLDB Endow.* 2024; 17(11):3252-3265.

### 10.2 Algorithm core

각 vector를 1-bit code로 압축 (provable bound):

```
1. Center: c = mean(vecs)
2. For each v_i:
   r_i = v_i - c   # centered residual
   b_i = sign(P r_i)   # 1-bit code, P = random rotation matrix (D × D)
3. Stratify by b_i ∈ {-1, +1}^D (Hamming weight or first-K bits)
```

본 연구 응용: D=96 1-bit code → 96-bit string; first-log2(K) bits 사용 → bucket id

### 10.3 Complexity

- Time: O(N·D·D) rotation P (full)
- Space: O(N·D bit) very compact
- Dim: any (paper paper test up to 768d)

### 10.4 본 narrative fit

- 2024 VLDB recent → narrative fresh
- pq/opq (현재 portfolio defect — md5 hash) 와 차별화: provable bit code
- RQ3 paradigm P6 anchor 강화 (현재 P6 audit 결과 1.6/10 폐지 권고 — RaBitQ 가 P6 회복)

### 10.5 Redundancy check

- pq/opq 와 distinct (1-bit RaBitQ vs PQ codeword)
- LSH (sign-bit) 와 distinct: RaBitQ 는 centered residual + provable bound, LSH 는 random hyperplane

---

## 11. M11 — iDistance + Neyman allocation

### 11.1 Reference verbatim

Synthesis: Jagadish HV, Ooi BC, Tan KL, Yu C, Zhang R. "iDistance" *TODS* 2005 + Neyman 1934 *JRSS*.

### 11.2 Algorithm core

M5 iDistance 1D scalar y_i 후, quantile bin → Neyman σ_h allocation:

```
1. M5 iDistance: y_i = j(v_i) × c + d(v_i, R_{j(v_i)})
2. Quantile bin: 20 bins on y_i
3. Per bin h: σ_h = std(D_target(v_i) in bin h)
4. Neyman: n_h ∝ N_h × σ_h
```

### 11.3 본 narrative fit

- M5 iDistance + RQ2 Neyman 결합
- KMeans (cluster id) + Neyman (M9) 와 직교: cluster id 가 아닌 continuous distance 후 Neyman
- 2D ablation: cluster-method × continuous-distance × Neyman

### 11.4 Redundancy check

- M5 iDistance (no Neyman) 와 distinct
- M9 KMeans+Neyman 와 distinct (continuous y vs discrete cluster id)

---

## 12. 11 method summary 및 paradigm 분포

### 12.1 Paradigm 강화 분포

| Paradigm | 신규 method | 현재 ★ 후보 |
|---|---|---|
| **P1 Cluster** | M9 KMeans+Neyman | ★1 hdbscan |
| **P2 Spatial** | M5 iDistance / M6 Z-order Morton / M7 Skilling Hilbert / M11 iDistance+Neyman | ★3 hilbert (defect) |
| **P3 Streaming** | M1 Chao weighted reservoir / M2 LPM1 proper | ★2 mb_partial |
| **P4 DimReduction** | M8 ICA FastICA | ★4 sparse_rp |
| **P5 QMC/Hashing** | M3 Cum-√f / M4 Lavallée-Hidiroglou (RQ2 응용) | (sobol 등 현재 portfolio) |
| **P6 Quantization** | M10 RaBitQ | (pq/opq defect) |

→ 9 paradigm 중 6 paradigm 강화. P7 Subspace (Q4 future), P8 Graph (future), P9 InfoTheoretic (Q4 HLL), P10 Density (Q4 KDE) 는 별도 Q4 권고 활용.

### 12.2 5/27 발표 narrative 강화 영역

- M9 KMeans+Neyman: Step 2 (분포 알면 Neyman) + Step 7 (Adaptive ensemble) 직접 강화
- M5/M6/M7 (P2 spatial 3개): Step 6 (신규 method 발굴) + ★3 hilbert defect rectify
- M1 Chao weighted: Step 1 (random sampling skew) 의 weight-aware alternative
- M3/M4 (Cum-√f / Lavallée-Hidiroglou): Step 2 (Neyman) optimal stratification 강화
- M10 RaBitQ: Step 6 (신규 method) + 2024 SIGMOD/VLDB 최신 인용

### 12.3 Implementation priority

| priority | method | 사유 |
|---|---|---|
| **P0 (5/12 launch)** | M1 Chao / M5 iDistance / M6 Z-order / M7 Skilling Hilbert / M9 KMeans+Neyman / M11 iDistance+Neyman | 구현 simple + paradigm anchor 즉시 |
| **P1 (5/14 launch)** | M2 LPM1 / M3 Cum-√f / M4 Lavallée-Hidiroglou / M8 ICA / M10 RaBitQ | mid 구현 + ablation depth |

---

## 13. END

작성: 2026-05-11 01:35 KST
다음 단계: Phase 3 — Implementation + smoke + server scp (사용자 confirm 후)

**핵심**: 11 method 통과, 모두 distinct (현재 46 portfolio 와 본질 다른 algorithm core), 6 paradigm 강화, 5/27 narrative 7단계 모두 fit. 구현 ~1,330 line + ETA 12-15 h server measurement.
