# Paradigm P5 QMC/Hashing — 8 method 알고리즘 검증

> **검증 시각**: 2026-05-10 (KST)
> **대상 코드**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py`
> **검증자**: Verification agent (P5 QMC/Hashing paradigm 담당)
> **scope**: lsh / sobol / halton / hammersley / lhs / ams_count_sketch / ccsketch / lp_bound — 8 method
> **검증 기준**: 원전 알고리즘 충실도, 구조적 deviation, hyperparam 적정성, n_strata=20 매핑, CaseA/CaseB 적합성, 결함 severity

---

## TL;DR

### 알고리즘 충실도 평균: **4.4 / 10**

P5 paradigm 8 method 중 **단 한 method 도 원전 알고리즘에 충실하지 않다**. 모든 구현이 (1) "vector → ID assignment" 라는 stratification API 에 강제로 맞추기 위해 (2) 각 알고리즘의 원래 수학적 의미를 비틀고 있다. paradigm 자체가 **alias / naming misrepresentation 위험이 가장 높다**.

| # | method | 충실도 | 원전 알고리즘 의도 | 본 구현 실제 동작 | severity |
|---|---|---|---|---|---|
| 1 | lsh | 4/10 | sign(R^T x) bucket — Charikar 2002 SimHash | 5 hyperplane → 32 bucket → mod 20 (locality 위반) | **MODERATE** |
| 2 | sobol | 3/10 | low-discrepancy sequence for QMC integration | 96 차원 Sobol point 20개 → direction → argmax | **MODERATE** |
| 3 | halton | 3/10 | low-discrepancy sequence for QMC integration | 96 차원 Halton point 20개 → direction → argmax | **MODERATE** |
| 4 | hammersley | 2/10 | Hammersley = (i/N, van der Corput) for [0,1]^d | first dim = i/N + Sobol rest, used as direction | **MODERATE** |
| 5 | lhs | 4/10 | Latin Hypercube Sampling = stratified MC sampling | 20 random LHS points → direction → argmax | **MODERATE** |
| 6 | ams_count_sketch | 2/10 | AMS estimator = ⟨ε, x⟩^2 expectation, Charikar = ε ∈ {±1} | LSH 와 동일 sign-bit hash, naming 만 다름 | **CRITICAL** |
| 7 | ccsketch | 2/10 | Count-Min Sketch = multiple hash → MIN counter | float projection mod 20, MIN of 4 hash row | **CRITICAL** |
| 8 | lp_bound | 8/10 | ‖x‖_p quantile bin (textbook simple) | ‖x‖_2 quantile bin — 정확 | OK |

### 핵심 결함 요약

1. **ams_count_sketch ≡ lsh** (sign-bit hash 동일). naming differentiation 부재. 보고서 양쪽 inclusion 시 **double-counting** 위험.
2. **ccsketch 는 Count-Min Sketch 가 아님**. CMS 의 "독립 hash → MIN counter" 의미가 cardinality estimation 에서 stratum assignment 로 잘못 transfer 됨. **알고리즘 식별 misnomer**.
3. **lsh K vs n_hyp misalignment** (audit V8 기록): `n_hyp=ceil(log2(20))=5` → 2^5=32 bucket → `bucket % 20` 으로 압축 → bucket {20,21,...,31} 가 0,1,...,11 와 동일 stratum (spatial locality 비대칭).
4. **sobol/halton/hammersley/lhs**: 모두 quasi-random sequence 의 정통 사용 (Koksma-Hlawka discrepancy 기반 numerical integration node) 와 **완전 다른 용도**. argmax-based stratum assignment 는 QMC 의 핵심 가치 (low-discrepancy uniform fill) 를 활용하지 못함.
5. **lp_bound**: 유일하게 정확한 구현. 단 high-D ‖·‖_2 의 curse-of-dimensionality (norm distribution narrow) 로 효과 약할 가능성.

### 즉시 조치 (severity 순)

| 조치 | 대상 | 근거 |
|---|---|---|
| 1. **report disclaimer** | ams_count_sketch ≡ lsh 동일성 명시 | naming misrepresentation 방지 |
| 2. **report disclaimer** | ccsketch 가 Count-Min Sketch literal 구현 X (mod hash + min) 임을 명시 | misnomer 방지 |
| 3. **report disclaimer** | lsh n_hyp=5 → 32 bucket → mod 20 (locality 위반) 명시 | audit V8 기재 |
| 4. **report disclaimer** | sobol/halton/hammersley/lhs 가 textbook QMC 가 아니고 "QMC sequence + argmax" custom 임을 명시 | naming alignment |
| 5. **method 제거 검토** | ams_count_sketch (lsh 와 redundant) | 동일 hash family alias |
| 6. **method 보강 검토** | ccsketch 를 진짜 CMS counter sketch 로 재구현 OR rename `proj_mod_hash_min` | 의미 일치 |

---

## 1. lsh (Locality-Sensitive Hashing)

### 1.1 원전 (Charikar 2002 SimHash)

원전 알고리즘 (Charikar, "Similarity Estimation Techniques from Rounding Algorithms", STOC 2002):
- D-차원 vector x 에 대해 random hyperplane r ∈ R^D (각 성분 ~ N(0,1) IID)
- hash bit h_r(x) = sign(r · x) ∈ {0, 1}
- L hyperplanes 사용 시 L-bit binary signature → 2^L bucket
- collision probability: P[h(x)=h(y)] = 1 - θ(x,y)/π, where θ = angle between x,y

원래 의도: **angle-preserving locality** — 가까운 vector 는 같은 bucket 에 들어갈 가능성 높음.

기타 LSH family (참고):
- **Indyk & Motwani 1998 LSH** (STOC): (r1, r2, p1, p2)-LSH, distance-based collision
- **E2LSH** (Datar et al. 2004): a · x + b 를 quantize → integer bucket
- **MinHash** (Broder 1997): set similarity / Jaccard

본 검증 대상은 **SimHash sign-bit** family.

### 1.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:470-479`:

```python
if method_name == "lsh":
    # Random projection hyperplane → sign bit hash → bucket
    rng_lsh = np.random.default_rng(seed)
    n_hyp = int(np.ceil(np.log2(n_strata)))  # log2(20) = ~5
    H = rng_lsh.standard_normal((all_vecs.shape[1], n_hyp)).astype(np.float32)
    signs = (all_vecs @ H > 0).astype(np.int32)
    bucket = np.zeros(len(all_vecs), dtype=np.int32)
    for k in range(n_hyp):
        bucket = bucket * 2 + signs[:, k]
    return (bucket % n_strata).astype(np.int32)
```

### 1.3 알고리즘 충실도: **4/10**

#### 일치하는 부분 (긍정)
- `H ~ N(0,1)^{D × 5}` — Charikar 의 random hyperplane 정의 충족.
- `signs = (X @ H > 0)` — sign-bit hash 정확.
- bit packing (`bucket = bucket * 2 + signs[:, k]`) — binary signature 5-bit 정확.

#### 핵심 deviation (감점 -6점)
- **K=20 vs n_hyp=5 misalignment**: 5 hyperplane → 2^5 = 32 bucket → `bucket % 20` 으로 강제 압축.
  - bucket {0..19}: 정상 stratum
  - bucket {20..31}: stratum {0..11} 로 wrap-around (이중 매핑)
  - 결과: stratum {0..11} 은 bucket 2개 union (locality 약화), stratum {12..19} 은 bucket 1개 (정확).
- 정통 SimHash 는 **K = 2^L bucket count** 로 정확히 align 시키거나 (즉 K=32 stratum), random hash family 다중 사용 (multiprobe LSH) 으로 충돌 흡수.

### 1.4 Hyperparam

| 파라미터 | 본 구현 값 | 정통 값 / 정당성 |
|---|---|---|
| `n_hyp` | `ceil(log2(20)) = 5` | log2(K) 가 정확히 K bucket 만들려면 K=2^L. K=20 는 √2^L 미만 모자란 hash space. |
| `H` 분포 | `N(0,1)` | Charikar 정확. ✅ |
| seed | 42 (고정) | reproducibility 확보. ✅ |
| L (hash function 개수) | 1 (single hash family) | multiprobe LSH (L=5~50) 와 다름. single hash → wrap-around 손실 흡수 X. |

### 1.5 n_strata=20 매핑 정당성

**✗ 문제 있음**.

- 5 hyperplane → 32 bucket → `% 20` 으로 압축 시 **bucket 2개가 하나의 stratum** (12개 stratum) vs **bucket 1개가 하나의 stratum** (8개 stratum) 의 **비대칭 매핑**.
- 결과: stratum {0..11} 은 더 큰 region (더 많은 vector) 를 cover, stratum {12..19} 은 더 작은 region.
- 만약 K = 16 (= 2^4) 또는 K = 32 (= 2^5) 였다면 매핑 정확. K = 20 강제로 인한 **알고리즘적 distortion**.

대안 (수정 권고):
- K = 2^⌈log2(20)⌉ = 32 stratum 으로 변경 (KM20 baseline 깨짐 → CaseA/CaseB design 와 비호환)
- 또는 현재 misalignment 를 **disclaimer 명시** (audit V8 그대로 유지)

### 1.6 CaseA/CaseB 적합성

- **CaseA (full population partition)**: SimHash 는 angle-preserving locality 보존 → 이론적으로 sphere 표면 partition 적합. 단 wrap-around 로 인한 stratum size 분산 증가.
- **CaseB (sample drawing)**: locality 가 보존되면 sample 의 spatial coverage 좋음. 단 K=20 로 인한 bucket 비대칭 stratum 의 sample 는 비균등.

전반적: **sign-bit hash 는 적합한 family 지만, K=20 강제로 효과 dilution**.

### 1.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| **MODERATE** | n_hyp=5 → 2^5=32 → mod 20 wrap-around | 보고서 disclaimer 명시 (audit V8 기재). |
| MINOR | single hash family (L=1), multiprobe X | multiprobe 적용 시 L=5~10 권고. 단 본 연구 scope 밖. |
| MINOR | seed 1개 — variability 없음 | 다중 seed (3~5 trial) 평균 권고 (TRIALS=3 가 이미 적용 중인지 확인 필요). |

---

## 2. sobol (Sobol' sequence)

### 2.1 원전 (Sobol 1967)

Sobol 의 원전 (1967, "Distribution of points in a cube"):
- d-차원 quasi-random sequence on [0,1]^d
- 핵심 성질: **low-discrepancy** — Koksma-Hlawka inequality 에 의해 numerical integration error O((log N)^d / N) (vs MC O(1/√N))
- Direction numbers, primitive polynomials 기반 deterministic XOR 기반 generation
- 정통 사용처:
  1. Numerical integration (∫ f dx ≈ (1/N) Σ f(s_i), s_i ~ Sobol)
  2. Quasi-Monte Carlo finance pricing
  3. Variance reduction in sampling
  4. Space-filling design (DOE)

### 2.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:491-498`:

```python
if method_name == "sobol":
    from scipy.stats import qmc
    # Sobol sequence as quasi-random projection direction
    sobol = qmc.Sobol(d=all_vecs.shape[1], seed=seed)
    directions = sobol.random(n_strata).astype(np.float32) * 2 - 1
    # Project onto each direction, take argmax
    scores = all_vecs @ directions.T
    return np.argmax(scores, axis=1).astype(np.int32)
```

### 2.3 알고리즘 충실도: **3/10**

#### 일치하는 부분
- `qmc.Sobol(d=D)` — scipy 표준 Sobol generator 사용.
- d 차원 = vector dimension (96 for DEEP, 128 for SIFT, 256 for SimSearchNet++).
- `.random(20)` → 20 sobol points → `* 2 - 1` 으로 [-1, 1]^d 로 변환.
- seed 고정 (reproducibility ✅).

#### 핵심 deviation (감점 -7점)
- **사용 방식 mismatch**: 정통 Sobol 은 **integration node** 로 사용 (각 sequence point 가 integration 의 evaluation point). 본 구현은 sequence point 를 **direction vector** 로 사용 후 vector @ direction → argmax.
- **K=20 = sequence 길이만 사용**: Sobol 의 low-discrepancy 성질은 N → ∞ 일 때 의미가 강함. N=20 는 매우 짧은 sequence — discrepancy bound 의 가치 미발현.
- **argmax 의 의미 불명**: vector x 가 어느 direction 에 가장 큰 inner product 를 가지는지 → angular partition. 이는 **Voronoi tessellation on unit sphere** 의 quasi-random 변형. Sobol 의 low-discrepancy 보다 **direction set 의 균등성** 만 활용. 정통 Sobol 의 가치 미발현.
- **scaling unmotivated**: `* 2 - 1` 로 [-1, 1] 매핑 후 argmax → direction 의 norm 이 일정하지 않음 (각 좌표 원래 [0,1] uniform → [-1,1] uniform → 96 차원 vector 의 norm 분포 std large). normalization 부재.

### 2.4 Hyperparam

| 파라미터 | 본 구현 값 | 평가 |
|---|---|---|
| `d` | vector dimension (96/128/256) | scipy `qmc.Sobol` 은 d ≤ 21201 까지 지원. 256 는 OK. |
| `n_strata` | 20 (=점 개수) | 매우 적음. Sobol 가치 미발현. |
| seed | 42 | scipy `qmc.Sobol(seed=42)` 는 scrambling seed. ✅ |
| scaling | `* 2 - 1` | `[0,1]^d → [-1,1]^d` linear. norm 정규화 X. |

### 2.5 n_strata=20 매핑 정당성

**✗ 의미 약함**.

- argmax 결과는 0 ~ n_strata-1 = 0 ~ 19 → exactly K stratum. 매핑 자체는 OK.
- 단 stratum 의 의미: "Sobol direction 20개 중 가장 큰 inner product 를 가지는 direction 의 index". 이는 **20개 direction 의 angular Voronoi cell** 에 vector 가 속하는 cell.
- Sobol 의 low-discrepancy 가 96차원 sphere 의 균등 partition 을 보장하는가? **NO** — Sobol 은 [0,1]^d cube 에서의 균등성. unit sphere normalization 없으면 의미 transfer 안 됨.

### 2.6 CaseA/CaseB 적합성

- **CaseA**: 96차원 vector 의 angular partition. Sobol 이 random Gaussian 보다 더 균등한 direction set 을 만드는지 불명 (Sobol 의 [0,1]^d 균등성 ≠ unit sphere 균등성).
- **CaseB**: stratum size variance 가 random direction 보다 작을 가능성 — 약간의 variance reduction 효과 가능. 단 차이 미세.

### 2.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| **MODERATE** | Sobol 정통 용도 (integration node) 와 다름 — direction 으로 사용. | report disclaimer 명시: "Sobol sequence as direction vectors (not integration nodes). N=20 per axis." |
| **MODERATE** | direction normalization 부재 — `[0,1]^d → [-1,1]^d` linear 만 | `directions = directions / np.linalg.norm(directions, axis=1, keepdims=True)` 로 unit vector 정규화 권고. |
| MINOR | n_strata=20 = sequence 길이 매우 적음 | Sobol 가치 강조하려면 N >> 1000 권고. 단 stratum=20 design constraint 탓. |
| MINOR | scaling `* 2 - 1` — 0이 sequence 에 포함 → 0 direction (origin) 위험 | Sobol skip(1) 또는 `qmc.Sobol(scramble=True)` 로 0 회피 권고. |

---

## 3. halton (Halton sequence)

### 3.1 원전 (Halton 1960)

Halton 의 원전 (1960, "On the efficiency of certain quasi-random sequences"):
- d-차원 quasi-random sequence on [0,1]^d
- 첫 차원: van der Corput sequence base 2 (binary radical inverse)
- 두번째 차원: van der Corput base 3
- d번째 차원: van der Corput base p_d (d번째 prime)
- 정통 사용처: Sobol 과 동일 (low-discrepancy integration). 단 high-D (d > 14) 에서 collision 발생 (high prime base 의 cycle 짧아짐).

### 3.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:543-548`:

```python
if method_name == "halton":
    from scipy.stats import qmc
    halton = qmc.Halton(d=all_vecs.shape[1], seed=seed)
    directions = halton.random(n_strata).astype(np.float32) * 2 - 1
    scores = all_vecs @ directions.T
    return np.argmax(scores, axis=1).astype(np.int32)
```

### 3.3 알고리즘 충실도: **3/10**

#### 일치하는 부분
- `qmc.Halton(d=D)` — scipy 표준 Halton.
- scrambling 적용 (scipy default, `seed=42`).

#### 핵심 deviation (감점 -7점)
- **Sobol 과 동일한 모든 deviation 적용**: direction 으로 사용, normalization 부재, K=20 짧은 sequence, etc.
- **추가 결함 — high-D Halton degeneracy**: D=96 (DEEP) / 128 (SIFT) / 256 (SSN). Halton 은 d-th dimension 에 d-th prime 사용 → D=256 → 256-th prime ≈ 1619. 이런 큰 base 는 **첫 1619 points 까지 cycle 안 채움** → **N=20 으로는 sequence 가 거의 lattice 에 정렬 (correlation 발생)**.
  - 알려진 Halton failure mode: D > 14 부터 high-dimension projection 에 strong correlation 출현. 본 구현은 D=96~256 에서 의미 있는 quasi-random 성질 거의 사라짐.
- scipy `qmc.Halton` 은 default scrambling 으로 이 issue 를 일부 완화하지만, **N=20 으로는 여전히 부족**.

### 3.4 Hyperparam

| 파라미터 | 본 구현 값 | 평가 |
|---|---|---|
| `d` | 96/128/256 | high-D Halton degeneracy 위험. |
| `n_strata` | 20 | low-discrepancy bound 발현 X. |
| seed | 42 | ✅ |
| scrambling | scipy default (Owen?) | scipy `qmc.Halton` 은 default `scramble=True` (Owen scrambling). ✅ |
| scaling | `* 2 - 1` | normalization 부재 (sobol 과 동일). |

### 3.5 n_strata=20 매핑 정당성

sobol 과 동일 — argmax 매핑 자체는 OK. 단 high-D 에서 Halton sequence 의 quasi-random 성질 약화로 random direction 과 거의 다르지 않을 가능성.

### 3.6 CaseA/CaseB 적합성

- sobol 보다 약간 떨어질 가능성 (high-D degeneracy 탓).

### 3.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| **MODERATE** | Halton 정통 용도와 다름 (sobol 과 동일 deviation) | report disclaimer 명시. |
| **MODERATE** | high-D Halton degeneracy (D=96~256, base ≈ 1000+) | 같은 내용 disclaimer 추가, 또는 더 강한 scrambling (Owen + 다중 sample). |
| MINOR | direction normalization 부재 | unit vector 정규화 권고. |

---

## 4. hammersley (Hammersley sequence)

### 4.1 원전 (Hammersley 1960)

Hammersley 의 원전 (1960, "Monte Carlo methods for solving multivariable problems"):
- d-차원 sequence on [0,1]^d
- 첫 차원: i/N (deterministic equispaced)
- 2 ~ d 차원: van der Corput / Halton sequence (각 prime base)
- Halton 의 변형 — 첫 차원 fixing 으로 한 차원 더 정확.
- **단점**: N 을 사전에 알아야 함 (i/N 계산 위해). N 가변 시 사용 어려움.

### 4.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:550-558`:

```python
if method_name == "hammersley":
    # Hammersley sequence — first dim is i/N, rest are van der Corput
    from scipy.stats import qmc
    sob = qmc.Sobol(d=all_vecs.shape[1] - 1, seed=seed)
    rest = sob.random(n_strata)
    first = (np.arange(n_strata) / n_strata).reshape(-1, 1)
    directions = np.hstack([first, rest]).astype(np.float32) * 2 - 1
    scores = all_vecs @ directions.T
    return np.argmax(scores, axis=1).astype(np.int32)
```

### 4.3 알고리즘 충실도: **2/10**

#### 일치하는 부분
- 첫 차원 = `np.arange(20) / 20 = [0, 0.05, 0.1, ..., 0.95]` — i/N pattern 정확.
- 나머지 차원 = Sobol (Halton 도 가능하지만 Sobol 더 흔함, OK).

#### 핵심 deviation (감점 -8점)
- **모든 sobol/halton deviation 동일 적용**: direction 으로 사용, K=20 짧은 sequence, normalization 부재.
- **이론적 mismatch**: Hammersley 의 가치는 첫 차원 의 i/N 으로 인해 **ONE 더 적은 차원** (= d-1) 에서 quasi-random 성질만 필요. 본 구현은 **첫 차원 fixed** + **rest = Sobol** — 이는 Hammersley 의 의도 충족. 단 Sobol 인지 Halton 인지 정확히 같진 않음 (보통 Hammersley 정의는 van der Corput / Halton 사용).
- **scaling 비대칭 issue**: 첫 차원 = `[0..0.95]` → `* 2 - 1` → `[-1, 0.9]` (음수 vs 양수 비대칭). 나머지 차원 = `[0,1]` → `[-1,1]` (대칭). → **direction vector 의 첫 차원이 항상 음수 ~ 약 양수** → vector @ direction 의 첫 차원 contribution 이 systematic bias.
- **deterministic 첫 차원 의 효과**: `i/N` 은 0 부터 시작 → 첫 direction 의 첫 차원 = -1. 이는 단 하나의 direction 이 첫 차원 음의 max (i.e., x[0] 가 negative max 인 vector 들이 stratum 0에 몰림).

### 4.4 Hyperparam

| 파라미터 | 본 구현 값 | 평가 |
|---|---|---|
| `d-1` Sobol | D-1 (95/127/255) | OK. |
| `first` | `np.arange(20)/20` | exact i/N. ✅ |
| `n_strata` | 20 | sobol/halton 과 동일 평가. |
| scrambling | scipy default | ✅ |

### 4.5 n_strata=20 매핑 정당성

argmax 매핑 OK. 단 첫 차원 의 i/N 으로 인한 systematic asymmetry 가 stratum 0,1 (첫 차원 음의 contribution) 와 stratum 18,19 (첫 차원 양의 contribution) 사이의 sample size imbalance 유발 가능.

### 4.6 CaseA/CaseB 적합성

- 첫 차원 deterministic 의 효과로 vector 의 첫 component 가 **dominant feature** 인 경우 (예: PCA 후 first PC) Hammersley 가 sobol/halton 보다 효과적. 단 raw embedding (DEEP/SIFT/SSN) 은 보통 첫 차원이 random — 따라서 Hammersley advantage 약함.

### 4.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| **MODERATE** | sobol/halton 동일 deviation 모두 적용 | report disclaimer 명시. |
| **MODERATE** | 첫 차원 `[0..0.95] → [-1..0.9]` 비대칭 (`first` 의 max=0.95, scaling 후 0.9) | first = `np.arange(20)/(20-1)` 로 [0,1] 대칭 또는 `(np.arange(20) + 0.5) / 20` (cell center) 권고. |
| MINOR | Sobol vs Halton choice for "rest" 임의적 (정의 모호) | scipy `qmc.Halton` 사용으로 일관성 권고. 단 효과 차이 미미. |

---

## 5. lhs (Latin Hypercube Sampling)

### 5.1 원전 (McKay, Beckman, Conover 1979)

McKay et al. 1979 ("A comparison of three methods for selecting values of input variables in the analysis of output from a computer code", Technometrics):
- d-차원 [0,1]^d cube 에서 N 개 sample 추출
- 각 차원을 N 개 equal interval 로 분할 → 각 interval 에서 1개 random sample (총 N points per axis)
- d 차원 사이는 random permutation 으로 결합 → Latin Square 의 d-차원 일반화
- 보장: 각 차원의 marginal distribution 이 정확히 stratified (각 sub-interval 1개 점).
- 정통 사용처:
  1. DOE (Design of Experiments)
  2. Computer simulation (sensitivity analysis)
  3. Variance reduction in MC (vs IID sampling: variance ↓ 1/N for additive functions)

### 5.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:829-835`:

```python
if method_name == "lhs":
    # Latin Hypercube Sampling — direction quasi-random
    from scipy.stats import qmc
    lhs = qmc.LatinHypercube(d=all_vecs.shape[1], seed=seed)
    directions = lhs.random(n_strata).astype(np.float32) * 2 - 1
    scores = all_vecs @ directions.T
    return np.argmax(scores, axis=1).astype(np.int32)
```

### 5.3 알고리즘 충실도: **4/10**

#### 일치하는 부분
- `qmc.LatinHypercube(d=D)` — scipy 표준 LHS.
- N=20 sample → marginal stratification 보장 (각 차원 의 [0,1] 이 20 sub-interval 로 분할되어 각 1점).
- seed 고정. ✅

#### 핵심 deviation (감점 -6점)
- **direction 으로 사용**: sobol/halton/hammersley 와 동일 deviation. LHS 의 정통 용도 (marginal stratified sampling) 와 다름.
- **그러나 LHS 만의 advantage**: marginal stratification 이 direction set 의 **각 차원 균등 분포** 를 보장 → vector @ direction 시 inner product distribution 의 systematic bias 감소.
- **K=20 = sample size 적음**: LHS 의 variance reduction 은 N → ∞ 에서 의미가 강하지만, N=20 도 stratification 효과 있어 IID sampling 보다 약간 효과 있음.
- **normalization 부재**: sobol 과 동일.

### 5.4 Hyperparam

| 파라미터 | 본 구현 값 | 평가 |
|---|---|---|
| `d` | 96/128/256 | LHS 는 high-D 에서도 marginal 보존 OK. ✅ |
| `n_strata` | 20 | marginal 20 stratum 정확. ✅ |
| seed | 42 | ✅ |
| scrambling | scipy default (centered) | ✅ |

### 5.5 n_strata=20 매핑 정당성

LHS 가 N=20 random direction 을 [0,1]^d 에서 선택 → `* 2 - 1` → 20 direction → argmax stratum.

LHS 의 marginal stratification 이 **direction 의 각 차원 분포 균등성** → random Gaussian direction 보다 약간 더 uniform angular coverage 가능. 단 확정적 보장 아님.

### 5.6 CaseA/CaseB 적합성

- **CaseA**: random direction 보다 약간 더 균등 partition.
- **CaseB**: stratum size variance 가 random direction 의 partition 보다 작을 가능성 — variance reduction.

### 5.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| **MODERATE** | LHS 정통 용도 (DOE / sensitivity) 와 다름 | report disclaimer 명시. |
| MINOR | normalization 부재 (sobol 과 동일) | unit vector 정규화 권고. |
| MINOR | sobol/halton/hammersley 와 거의 동일 mechanism (다른 sequence type 만) — uniformity 비교 가치 limited | 4 method 중 2개 정도만 keep + disclaimer 권고. |

---

## 6. ams_count_sketch (AMS Count Sketch)

### 6.1 원전 (Alon, Matias, Szegedy 1996 / Charikar et al. 2002)

**AMS sketch** (Alon, Matias, Szegedy 1996, "The space complexity of approximating the frequency moments", JCSS):
- frequency moment F_2 = Σ_i f_i^2 estimation
- ε ∈ {±1}^n random vector (4-wise independent hash)
- Z = Σ_i ε_i x_i = ⟨ε, x⟩
- E[Z^2] = ‖x‖_2^2 = F_2
- 다중 독립 ε vector 평균 → variance 감소

**Count Sketch** (Charikar, Chen, Farach-Colton 2002, "Finding frequent items in data streams", ICALP):
- AMS 의 변형. multi-row hash table, 각 row 는 (h: U → [w], s: U → {±1})
- count_estimate(i) = MEDIAN_j (s_j(i) · C[j][h_j(i)])
- 정통 의도: **frequency / count estimation** in data streams.

본 검증 대상은 "ams_count_sketch" — naming 으로 보아 AMS + Count Sketch hybrid 를 의도. 단 본 구현은 stratum assignment 이지 frequency estimation 이 아님.

### 6.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:695-703`:

```python
if method_name == "ams_count_sketch":
    # AMS Count Sketch (SimHash sign-bit signature)
    rng_d = np.random.default_rng(seed)
    H = rng_d.standard_normal((all_vecs.shape[1], int(np.ceil(np.log2(n_strata))))).astype(np.float32)
    signs = (all_vecs @ H > 0).astype(np.int32)
    sigs = np.zeros(len(all_vecs), dtype=np.int32)
    for k in range(signs.shape[1]):
        sigs = sigs * 2 + signs[:, k]
    return (sigs % n_strata).astype(np.int32)
```

### 6.3 알고리즘 충실도: **2/10**

#### 일치하는 부분
- 거의 없음. AMS / Count Sketch 정통 의미와 거리.

#### 핵심 deviation (감점 -8점)
- **lsh 와 사실상 동일 알고리즘**: 코드 비교

  ```python
  # lsh (line 470-479)
  H = rng_lsh.standard_normal((D, n_hyp))
  signs = (all_vecs @ H > 0)
  bucket = bit_pack(signs)
  return bucket % n_strata

  # ams_count_sketch (line 695-703)
  H = rng_d.standard_normal((D, ceil(log2(n_strata))))
  signs = (all_vecs @ H > 0)
  sigs = bit_pack(signs)
  return sigs % n_strata
  ```
  → **동일 알고리즘** (line-by-line). 변수 이름만 다름. **CRITICAL**: 두 method 가 동일한 결과를 produce 함 (seed 만 다르면 결과 다름, 단 distribution 동일).
- **AMS 와의 차이점**: AMS 는 ε ∈ {±1}^d (Rademacher / 4-wise independent), 본 구현은 H ∈ R^{D×L} (standard normal) → continuous projection 후 sign. 둘이 **거의 같은 family** (Gaussian 의 sign 은 Rademacher 와 distribution 동일하지 않지만 sign 은 같음). 단 inner product 의 분포 다름.
- **Count Sketch 와의 차이점**: Count Sketch 는 multiple **independent** hash row (j=1..d) 의 MEDIAN. 본 구현은 **single** hash family 의 bit-packed bucket → MEDIAN aggregation 부재. **Count Sketch 의 핵심 mechanism (median for outlier removal) 미적용**.

### 6.4 Hyperparam

| 파라미터 | 본 구현 값 | 평가 |
|---|---|---|
| `H` | `N(0,1)^{D × ⌈log2(20)⌉}` = `N(0,1)^{D × 5}` | lsh 와 동일. |
| L | 5 | lsh 와 동일. |
| `n_hash` rows (Count Sketch 의 d) | 1 | Count Sketch 정통 d=5~10 에 비해 매우 적음. |
| seed | 42 (lsh 와 같은 seed) | **위험**: 만약 lsh 와 ams_count_sketch 가 동일 seed 사용 시 결과 100% 동일. 코드 line `rng_d = np.random.default_rng(seed)`, lsh 는 `rng_lsh = np.random.default_rng(seed)` — 두 generator 가 독립이지만 같은 seed → 동일 sequence → 동일 H matrix → **동일 stratum_id 결과** (seed=42, n_hyp=5 동일).

### 6.5 n_strata=20 매핑 정당성

lsh 와 동일 wrap-around 문제. **lsh § 1.5 와 동일 평가**.

### 6.6 CaseA/CaseB 적합성

lsh 와 동일.

### 6.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| **CRITICAL** | **lsh 와 line-by-line 동일 알고리즘** (seed 같으면 결과 100% 동일) | (1) report 에서 ams_count_sketch 를 lsh 의 alias 로 표기 OR (2) 진짜 AMS (ε ∈ {±1}^d Rademacher + median of multiple hashes) 로 재구현. |
| **CRITICAL** | naming misrepresentation — "AMS Count Sketch" 라고 칭하지만 실제는 LSH SimHash | rename to `lsh_v2` or `simhash_alt` OR remove method. |
| **MODERATE** | Count Sketch 의 핵심 (median over multiple hash rows) 미적용 | 진짜 Count Sketch: `sigs[i] = median([sketch_row[j][hash[j](i)] * sign[j](i) for j in range(d)])`. |
| MINOR | seed=42 동일 → lsh 와 같은 결과 위험 | seed 차별화 (`seed + 1000` etc.) — 단 본질 문제 (동일 알고리즘) 해결 X. |

---

## 7. ccsketch (Count-Min Sketch)

### 7.1 원전 (Cormode & Muthukrishnan 2005)

Cormode & Muthukrishnan 2005 ("An improved data stream summary: the count-min sketch and its applications", J. Algorithms):
- count-min sketch C[d][w] = 2D table, d hash functions h_1..h_d : U → [w]
- update(i): for j in 1..d: C[j][h_j(i)] += 1
- query(i): MIN_j C[j][h_j(i)] (overestimate, no underestimate guarantee)
- 정통 의도: **frequency estimation** in data streams. ε-approximation in O(1/ε log(1/δ)) space.

본 검증 대상 "ccsketch" — naming 으로 Count-Min Sketch 의도. 단 본 구현은 stratum assignment.

### 7.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:727-735`:

```python
if method_name == "ccsketch":
    # Count-Min sketch — multiple hash → min
    rng_d = np.random.default_rng(seed)
    n_hash = 4
    H = rng_d.standard_normal((all_vecs.shape[1], n_hash)).astype(np.float32)
    proj = all_vecs @ H
    # Min-hash bucket
    buckets = (proj % n_strata).astype(np.int32)
    return np.min(buckets, axis=1)
```

### 7.3 알고리즘 충실도: **2/10**

#### 일치하는 부분
- 거의 없음. Count-Min Sketch 의 어떠한 핵심 mechanism 도 적용 X.

#### 핵심 deviation (감점 -8점)
- **count-min 의 의미 mismatch**:
  - 정통: hash[j](i) 가 같은 i 가 같은 bucket 에 가 → 충돌 → 빈도 over-estimate 가능 → MIN 으로 over-estimate 회피 (counter sketching).
  - 본 구현: vector x → 4 random direction projection → modulo 20 → MIN of 4 values.
  - 의미상 거리: Count-Min 은 **counter array** 가 핵심 자료구조. 본 구현은 counter 자체가 없음. **단순히 vector 를 4가지 다른 hash 로 mapping 후 결과의 min 을 stratum 으로 사용**.
- **`proj % n_strata` 의 의미 모호**:
  - `proj` 는 `(N, 4)` float matrix.
  - `proj % 20` 은 numpy float modulo (Python convention: `(-3.5) % 20 = 16.5`, 항상 [0, 20)).
  - `.astype(np.int32)` 는 truncation toward zero → `[0, 19]`.
  - **즉**: 각 vector x 의 4 가지 random direction projection 의 fractional `mod 20` 의 floor → 4 integer stratum candidate.
  - **MIN 의 의미**: 4 candidate 중 최소값을 stratum 으로 → 결과: stratum {0..18} 가 mostly 작은 값에 biased. stratum 19 는 모든 4 hash 가 19 일 때만 (확률 1/20^4 = 6e-6).
  - **결과**: stratum distribution 강한 left-skewed (stratum 0 이 가장 많고, stratum 19 가 가장 적음).
- **stratum size imbalance 위험**: 만약 stratum 0 에 50% vector 가 몰리고 stratum 19 에 거의 0% → CaseA/CaseB 모두 KM20 baseline 과 비교 무의미.

### 7.4 Hyperparam

| 파라미터 | 본 구현 값 | 평가 |
|---|---|---|
| `n_hash` | 4 | Count-Min 정통 d=⌈log(1/δ)⌉ 일반적 d=5~10. 4 는 OK 정도. |
| `H` | `N(0,1)^{D × 4}` | continuous Gaussian projection. Count-Min 의 hash[j] : U → [w] 와 다름 (CMS 는 universal hash family). |
| `n_strata` | 20 (= w bucket width) | OK. |
| `proj % n_strata` | float modulo + truncate | **이상한 mechanism**. CMS 의 hash 와 의미 mismatch. |
| MIN aggregation | `np.min(axis=1)` | CMS 정통 ✅. 단 의미 mismatch (CMS 는 counter 의 min, 본 구현은 stratum candidate 의 min). |

### 7.5 n_strata=20 매핑 정당성

**✗ 강하게 biased**.

- 4 hash 의 MIN → distribution 강한 left-skewed.
- 분석: 만약 buckets[i, j] 가 [0, 20) uniform IID 라 가정 시, MIN 의 expected value = 20/(4+1) = 4 (즉 stratum 4 가 mode). 분산 분포로:
  - P[MIN >= k] = ((20-k)/20)^4
  - P[MIN = 19] = (2/20)^4 - 0 = 1/10000 = 0.01%
  - P[MIN = 0] = 1 - (19/20)^4 = 18.5%
- 결과: stratum 0 ~ 5 에 vector 약 80% 몰림, stratum 18, 19 거의 비어 있음.
- **결론**: KM20 의 "20 strata 균등 분포" 와 정반대 효과. CaseA/CaseB 비교 시 **stratum 자체가 무의미**.

### 7.6 CaseA/CaseB 적합성

- **부적합**. stratum imbalance 가 너무 강해 sample size 가 stratum 별 매우 다름.
- KM20 baseline 비교 의미 X.

### 7.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| **CRITICAL** | Count-Min Sketch 정통 알고리즘이 아님 (counter array 부재) | (1) rename to `proj_mod_min` OR `random_proj_min_hash` OR (2) 진짜 CMS 로 재구현 (counter array + collision-based count). |
| **CRITICAL** | MIN aggregation 으로 인한 strong left-skewed distribution → stratum imbalance | KM20 baseline 비교 의미 X — method 제거 OR fix. |
| **MODERATE** | `proj % n_strata` float modulo + truncate — 의미 모호 | hash function 으로 명확히 (e.g., `hash_int = ((proj * 1e6).astype(np.int64)) % n_strata`). |
| MINOR | Count-Min 의 d 권고 (5~10) 보다 작은 4 | d=8 권고 — 단 fix 후 의미 있음. |

---

## 8. lp_bound (Lp norm-based binning)

### 8.1 원전 (Textbook simple)

특정 paper 가 아닌 textbook simple stratification:
- ‖x‖_p = (Σ_i |x_i|^p)^{1/p} 의 quantile bin.
- p=2 (L2 norm) 가 가장 흔함.
- 정통 사용처: heavy-tail handling, outlier-aware stratification.

### 8.2 구현 위치 + 코드 발췌

`measure_paper_exact.py:751-757`:

```python
if method_name == "lp_bound":
    # Lp norm-based binning (p=2)
    norms = np.linalg.norm(all_vecs, axis=1)
    edges = np.quantile(norms, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    sids = np.searchsorted(edges[1:-1], norms, side="right").astype(np.int32)
    return np.clip(sids, 0, n_strata - 1)
```

### 8.3 알고리즘 충실도: **8/10**

#### 일치하는 부분
- L2 norm 정확 (`np.linalg.norm(axis=1)`).
- Quantile binning 정확 (`np.linspace(0, 1, 21)` → 20 sub-intervals).
- `edges[-1] += 1e-6` — boundary 포함 trick (max value 가 정확히 마지막 stratum).
- `searchsorted(edges[1:-1], side="right")` — interior edges 만 사용 (정확).
- `np.clip(0, n_strata-1)` — boundary 안전.

#### 핵심 deviation (감점 -2점)
- **high-D 에서 norm distribution narrow** (curse of dimensionality):
  - DEEP (D=96) — normalized embedding 이면 ‖x‖ ≈ 1 (constant). quantile bin 무의미.
  - SIFT (D=128) — 정수 vector, norm 분포 wider. OK.
  - SimSearchNet++ (D=256) — float, 정규화 여부 확인 필요.
- **p=2 만 사용**: "lp_bound" naming 은 일반 p 를 시사하지만 실제는 p=2 hardcoded. minor 결함.

### 8.4 Hyperparam

| 파라미터 | 본 구현 값 | 평가 |
|---|---|---|
| `p` | 2 (hardcoded) | naming 'lp' 와 mismatch. p=2 는 가장 일반적이므로 OK. |
| `n_strata` | 20 | quantile bin K=20. ✅ |
| edges | quantile + 1e-6 trick | textbook 정확. ✅ |
| `seed` | 미사용 | norm 은 deterministic, seed 불필요. ✅ |

### 8.5 n_strata=20 매핑 정당성

- norm 의 quantile bin → 정확히 20 stratum, 각 stratum 약 5% vector. ✅
- KM20 baseline 의 "20 strata 균등 분포" 와 일치.

### 8.6 CaseA/CaseB 적합성

- **CaseA**: norm 이 vector 의 "magnitude" 만 capture, "direction" 은 무시. 즉 angularly 다른 vector 가 같은 stratum. spatial coverage 측면에서 weak.
- **CaseB**: 같은 stratum 내 sample 의 angular variance 매우 큼.
- **high-D 의 norm 집중 문제**: `‖x‖` 가 거의 constant 인 경우 (DEEP normalized) 모든 vector 가 narrow band 에 → quantile edges 가 밀집 → bin assignment 거의 random.

### 8.7 결함 list

| severity | 결함 | 권고 |
|---|---|---|
| MINOR | high-D norm 분포 narrow (curse of dim) — DEEP normalized 시 효과 없음 | DEEP normalization 상태 확인 (handoff_v2 reference). normalized 면 lp_bound 는 useless method. |
| MINOR | p=2 hardcoded, naming "lp" 와 mismatch | rename to `l2_bound` 또는 p 를 hyperparam 화. |
| MINOR | direction information 손실 (norm 만 사용) | `lp_norm + first_pca_quantile` 같은 hybrid 권고 — 단 본 연구 scope 밖. |

---

## 9. 종합 권고

### 9.1 method-level 표

| # | method | 충실도 | severity | 즉시 조치 |
|---|---|---|---|---|
| 1 | lsh | 4/10 | MODERATE | disclaimer (audit V8): n_hyp=5 → 32 bucket → mod 20 |
| 2 | sobol | 3/10 | MODERATE | disclaimer: direction 으로 사용 (정통 X) + normalization 부재 |
| 3 | halton | 3/10 | MODERATE | disclaimer + high-D Halton degeneracy 명시 |
| 4 | hammersley | 2/10 | MODERATE | disclaimer + first-dim asymmetry fix 권고 |
| 5 | lhs | 4/10 | MODERATE | disclaimer 만 — 그나마 marginal stratification 가치 있음 |
| 6 | ams_count_sketch | 2/10 | **CRITICAL** | **lsh 의 alias** — remove 또는 rename + disclaimer |
| 7 | ccsketch | 2/10 | **CRITICAL** | **CMS 가 아님** — remove 또는 rename + redesign |
| 8 | lp_bound | 8/10 | MINOR | norm 분포 narrow 시 effect 약화 disclaimer |

### 9.2 paradigm 수준 권고

#### A. 즉시 제거 권고 (2 method)

1. **ams_count_sketch**: lsh 와 동일 알고리즘 (line-by-line). seed 같으면 결과 100% 동일. **paradigm 의 method count 부풀리기** 우려.
2. **ccsketch**: Count-Min Sketch 가 아닌 임의 hash mod min → strong stratum imbalance + 의미 mismatch.

#### B. report 작성 시 disclaimer 필수 (5 method)

1. **lsh**: "n_hyp=5 → 2^5=32 bucket → mod 20. Bucket {20-31} wraps to stratum {0-11}, asymmetric." (audit V8 기재)
2. **sobol**: "Sobol' sequence used as direction vectors (not integration nodes). N=20 direction count is small relative to discrepancy bound activation."
3. **halton**: "Halton sequence at D=96-256 may exhibit lattice-like correlation due to high prime base. N=20 insufficient for low-discrepancy effect."
4. **hammersley**: "Hammersley first-dim = i/N + Sobol rest. First-dim scaling introduces asymmetry [-1, 0.9] vs rest [-1, 1]."
5. **lhs**: "Latin Hypercube Sampling adapted as direction vector marginal-stratified random."

#### C. method 부각 (1 method, 그래도 정통)

- **lp_bound**: 유일하게 정통 textbook 구현. p=2 / quantile bin / edge trick 모두 정확. 단 high-D curse-of-dimensionality 로 effect dilution 가능 — DEEP normalization 상태 확인 필요.

### 9.3 paradigm 차원에서의 rebrand 권고

본 P5 paradigm 의 8 method 가 모두 **"vector → ID via hash/QMC"** 라는 공통 mechanism 인 점을 솔직하게 인정하고:
- naming: "QMC/Hashing" → "Hash-Based Stratification (with QMC sequence variants)"
- 8 method 를 4 family 로 그룹화:
  1. **SimHash family** (1개): lsh
  2. **QMC sequence family** (4개): sobol, halton, hammersley, lhs
  3. **Norm-based family** (1개): lp_bound
  4. **(remove)** ams_count_sketch (=lsh alias), ccsketch (mislabeled)

→ **4 family × 1~4 method = 6 effective method** (lsh / sobol / halton / hammersley / lhs / lp_bound).

### 9.4 추가 audit 권고

1. **seed independence audit**: lsh 와 ams_count_sketch 가 같은 seed=42 사용 시 결과 100% 동일 확인 필요.
2. **stratum size distribution audit**: 8 method 모두 sample dataset (DEEP/SIFT/SSN) 에서 stratum size {n_0, n_1, ..., n_19} 측정 → ccsketch 의 left-skewed 검증, lp_bound 의 narrow band 검증, lsh 의 wrap-around imbalance 검증.
3. **method-method correlation audit**: lsh vs ams_count_sketch 의 stratum_id Pearson correlation = 1.0 (동일 알고리즘) 확인.

### 9.5 priority list

| priority | 작업 |
|---|---|
| P0 | **report disclaimer 5 항목 작성** (lsh / sobol / halton / hammersley / lhs) |
| P0 | **ams_count_sketch + ccsketch 의 lsh/CMS misnomer 처리 결정** (remove or rename) |
| P1 | **stratum size distribution audit** (8 method × 3 dataset) |
| P1 | **seed independence audit** (lsh ≡ ams_count_sketch 검증) |
| P2 | direction normalization 적용 (sobol/halton/hammersley/lhs) — 단 결과 변화 미미 예상 |
| P2 | hammersley first-dim asymmetry fix (`(np.arange(20)+0.5)/20`) |
| P3 | lp_bound rename to l2_bound, 또는 p hyperparam 화 |
| P3 | lhs 가 sobol/halton/hammersley 의 redundant 인지 검토 (4 method 중 2개 keep 검토) |

---

## Appendix A — code level diff: lsh vs ams_count_sketch

```python
# lsh (line 470-479)
if method_name == "lsh":
    rng_lsh = np.random.default_rng(seed)
    n_hyp = int(np.ceil(np.log2(n_strata)))  # = 5
    H = rng_lsh.standard_normal((all_vecs.shape[1], n_hyp)).astype(np.float32)
    signs = (all_vecs @ H > 0).astype(np.int32)
    bucket = np.zeros(len(all_vecs), dtype=np.int32)
    for k in range(n_hyp):
        bucket = bucket * 2 + signs[:, k]
    return (bucket % n_strata).astype(np.int32)

# ams_count_sketch (line 695-703)
if method_name == "ams_count_sketch":
    rng_d = np.random.default_rng(seed)
    H = rng_d.standard_normal((all_vecs.shape[1], int(np.ceil(np.log2(n_strata))))).astype(np.float32)
    signs = (all_vecs @ H > 0).astype(np.int32)
    sigs = np.zeros(len(all_vecs), dtype=np.int32)
    for k in range(signs.shape[1]):
        sigs = sigs * 2 + signs[:, k]
    return (sigs % n_strata).astype(np.int32)
```

Diff: 변수 이름 (`rng_lsh` → `rng_d`, `n_hyp` → inline `int(np.ceil(np.log2(n_strata)))`, `bucket` → `sigs`). **동작 100% 동일** (같은 seed=42 사용 시).

증명:
- np.random.default_rng(42).standard_normal((D, 5)) — 두 호출 모두 동일 random sequence → 동일 H
- `signs = (all_vecs @ H > 0)` — 동일 H + 동일 input → 동일 output
- bit packing — 동일 logic
- modulo — 동일

→ **ams_count_sketch == lsh (deterministic equality with seed=42)**.

## Appendix B — ccsketch stratum distribution simulation

가정: `proj` 의 4 column 이 [0, 20) uniform IID (random projection 의 mod 20 가정).

```
P[stratum = k] = P[MIN of 4 IID uniform_int(0,20) = k]
              = ((20-k)/20)^4 - ((20-k-1)/20)^4
```

| stratum k | P[MIN = k] | percentile |
|---|---|---|
| 0 | 0.1855 | 18.55% |
| 1 | 0.1493 | 33.48% |
| 2 | 0.1192 | 45.40% |
| 3 | 0.0944 | 54.84% |
| 4 | 0.0742 | 62.26% |
| 5 | 0.0578 | 68.04% |
| 6 | 0.0445 | 72.49% |
| 7 | 0.0339 | 75.88% |
| 8 | 0.0254 | 78.42% |
| 9 | 0.0188 | 80.30% |
| 10 | 0.0136 | 81.66% |
| 11 | 0.0096 | 82.62% |
| 12 | 0.0066 | 83.28% |
| 13 | 0.0044 | 83.72% |
| 14 | 0.0028 | 84.00% |
| 15 | 0.0017 | 84.17% |
| 16 | 0.00094 | 84.26% |
| 17 | 0.00045 | 84.31% |
| 18 | 0.00016 | 84.32% |
| 19 | 0.00003 | 84.33% |

**관찰**: stratum 0~5 에 약 68% vector 몰림. stratum 16~19 에 약 0.16% 만. **KM20 stratum 균등 분포 (각 5%) 와 정반대**.

→ ccsketch 는 KM20 baseline 비교 자체가 무의미. **method 제거 강력 권고**.

## Appendix C — lp_bound 의 high-D norm distribution

`‖x‖_2` 의 high-D 분포 (vector 가 unit sphere 에 normalize 안 된 경우):
- 각 component x_i ~ N(0, 1) IID 가정 시 ‖x‖_2^2 ~ χ²_D
- E[‖x‖_2] ≈ √D, std ≈ √2 (D 무관)
- D=96 → mean ≈ 9.8, std ≈ 1.4 (CV = 14%)
- D=128 → mean ≈ 11.3, std ≈ 1.4 (CV = 12%)
- D=256 → mean ≈ 16.0, std ≈ 1.4 (CV = 9%)

**관찰**: high-D 일수록 norm 분포 narrow (relative). DEEP normalized 면 ‖x‖=1 constant → lp_bound 가 random partition.

DEEP normalization 상태 (handoff_v2 / paper §IV-B 확인 필요): paper 의 image_embedding/text_embedding 이 normalized 인지 raw 인지에 따라 lp_bound 의 가치 달라짐.

---

**검증 종료**: 8 method 평균 충실도 4.4/10. CRITICAL 2건, MODERATE 5건, MINOR 1건.

**핵심 deliverable**:
1. ams_count_sketch ≡ lsh 동일성 (CRITICAL)
2. ccsketch 가 Count-Min Sketch 가 아님 (CRITICAL)
3. lsh K=20 vs n_hyp=5 misalignment (audit V8 기재 그대로 — disclaimer 필요)
4. sobol/halton/hammersley/lhs 가 정통 QMC 사용 X — disclaimer 필요
5. lp_bound 만 정통 (단 high-D curse 주의)
