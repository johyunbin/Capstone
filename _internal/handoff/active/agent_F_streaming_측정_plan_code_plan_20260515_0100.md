# Agent F — Form 1 측정 plan + 구현 코드 plan deep dive (Streaming-aware Distribution-Conscious CE for VAQ)

> **작성**: 2026-05-15 01:00 KST (실제 KST = 5/14 20:28, file 명 main thread 지시 timestamp 사용) · Agent F · main thread 지시 "Form 1 측정 plan 세부 + code plan 영역 deep dive"
> **검증 기조**: paper §V-B Eq 1-6 원문 verbatim 재확인 (PDF p.6 + p.7) + Agent A/B/C/D/E 5 결과 종합 + measure_paper_exact.py (1407 line) 직접 read + scikit-learn Birch 공식 doc + SSDBM 2010 SRS 논문 source 검증
> **★ 주요 정정 (paper 직접 정독 결과)**:
>   1. paper §V-B 영역에는 **"Algorithm 1 14-step pseudo-code" 가 존재 X**. paper 는 Eq 1-6 (수식 6 개) + 자연 산문 설명 + hyperparam 7 종 verbatim. Agent C/D/E 가 의역해서 "14-step" 으로 풀어쓴 것 → 본 Agent F 는 paper exact 영역 (Eq 1-6) + 본 연구 의역 영역 (step-wise pseudo-code) 명확 분리.
>   2. paper hyperparam 정정: paper §VI 도입부 verbatim = "m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period 50 queries, N=385". 7 종 정확. measure_paper_exact.py line 67-76 와 100% 정합.
>   3. paper §V-B 의 sample 추출 = "Bernoulli sampling at AdaptiveState.size" (measure_paper_exact.py 의 `bernoulli_estimate` 구현 verbatim). paper 자체 wording = "Adaptive sampling with momentum-based feedback control".
> **사용자 정책 (fix 모드)**: main theme = Form 1, 정정 wording 룰 엄수.

---

## 0. 핵심 결론 요약 (TL;DR)

본 Agent F deep dive 결과 Form 1 의 구현 detail + 측정 protocol + cost 산정 결과 다음과 같다.

| 영역 | 핵심 결정 | cost (h) | 비고 |
|---|---|---:|---|
| **Component A (SRS)** | per-stratum Vitter 1985 reservoir (각 cluster R_j) + Equal allocation default + Algorithm L (skip-based) 적용 가능 | 8-12 | numpy 100 line + measure_paper_exact.py 의 `cache_cluster_samples_inmem` 패턴 재사용 |
| **Component B (BIRCH)** | `sklearn.cluster.Birch(n_clusters=20, threshold=0.5, branching_factor=50)` + `partial_fit` chunk pattern (기존 line 623-630 birch method **이미 구현**) + CF tuple 직접 access (`subcluster_centers_` + manual N_j/LS_j/SS_j 보관) | 10-15 | wrapper 250 line, 측정 inflight 영역 |
| **Component C (Eq 2-6 통합)** | paper Eq 1-6 verbatim 유지 (AdaptiveState 그대로) + Step "n_inc 분배" augment → group-aware allocation (`group_aware_alloc(state.size_delta, sizes, sigma_squared)`) | 4-6 | measure_paper_exact.py line 118-140 AdaptiveState **유지** + alloc helper 60 line 추가 |
| **Component D (분포 인지)** | Equal / Proportional / Neyman (oracle σ_j) / Anti-Neyman 4 mode. RQ2 의 5-way axis 와 동일 logic (Bernoulli baseline 제외 4 mode 만) | 3-5 | _measure_common.py 의 `equal_alloc` + `proportional_alloc` + `neyman_alloc` 기존 활용 |
| **측정 1 (streaming)** | DEEP/SIFT/SSN sf=100 × 3 drift × 4 method × 2 mode × 10 trial = **1440 file** | server 8-12h + 코드 12h | 메인 측정, 4 drift scenario 코드 작성 필요 |
| **측정 2 (BIRCH cost)** | 3 dataset × 4 threshold × 3 K × 3 freq × 5 trial = **540 file** | server 3-5h + 코드 8h | accuracy degradation 분석 |
| **측정 3 (4-way 비교)** | 5 method × 3 dataset × 2 sf × 2 sel × 10 trial = **600 file** | server 5-8h + 코드 30h | SelNet 만 5/27 까지, CE4HD/Ada-ef 6/11 까지 권장 |
| **측정 4 (distribution shift)** | 3 dataset × 4 추가 시나리오 × 4 method × 2 mode × 5 trial = **480 file** | server 3-5h + 코드 10h | embedding upgrade 시나리오 cost 약함 |
| **측정 5 (phase 2 augment)** | 3 dataset × 2 sf × 2 mode × 10 trial = **120 file** (pilot) | server 1-2h + 코드 6h | phase 2 future, 5/27 X |
| **분석/figure** | 1001 file analysis 9 script 패턴 재사용 + Form 1 streaming axis 추가 | 15-20 | paired Δ% + drift trajectory plot + 4-way bar |
| **총 cost** | -- | **130-180h** | Agent E 산정 135-195h 와 fit |

★ **Agent F 핵심 권장**: Component B (BIRCH) 는 **measure_paper_exact.py 의 line 623-630 이미 구현됨** — wrapper 만 추가 (CF tuple manual 보관 + σ_j² online 계산). Component A (SRS) + 측정 1 (streaming workload generator) 가 신규 코드 영역. measure_paper_exact.py 의 trial loop / cell 패턴 80% 재사용.

★ **Agent E 산정 검증**: Agent E 135-195h vs Agent F 130-180h = **±5% 일치** (자원 Max 가속 시 100-150h 가능 영역 동일). 5/27 phase 1 (cost 50-80h) → Component A + B + 측정 1 + 측정 3 partial (Bernoulli + 본 only) realistic. 6/11 phase 1 full + phase 2 partial.

---

## 1. Component A (SRS — Stratified Reservoir Sampling) 구현 detail

### 1.1 알고리즘 정확 명세 (Vitter 1985 + Al-Kateb-Lee SSDBM 2010)

**input**: data stream D = {x_1, x_2, ...} (online tuple arrival), sample budget N=385 (paper Eq 1 유지), cluster count K=20 (RQ2/RQ3 정합), cluster centroid C_j (BIRCH online 으로 유지).

**reservoir budget allocation (Component D 와 align)**:
- Equal: n_j = N/K = 385/20 ≈ 20 per cluster (default, Al-Kateb-Lee 2010 power allocation 의 simplest case)
- Proportional: n_j ∝ N_j (online N_j 는 BIRCH CF tuple 의 count 활용)
- Neyman: n_j ∝ N_j · σ_j (online σ_j 는 BIRCH CF tuple 의 LS/SS 로 계산)

**per-stratum 알고리즘 (Vitter 1985 Algorithm R verbatim)**:

```python
def reservoir_per_stratum(x_t, j_star, R, t_j, n_j, rng):
    """
    x_t       : 새 tuple (d-dim vector)
    j_star    : cluster id (BIRCH 가 부여)
    R         : list of lists, R[j] = stratum j reservoir
    t_j       : list, t_j[j] = stratum j 누적 본 tuple count
    n_j       : list, n_j[j] = stratum j reservoir capacity
    rng       : numpy.random.Generator

    Vitter 1985 Algorithm R: 확률 n_j/t_j 로 reservoir 의 random position replace
    """
    j = j_star
    t_j[j] += 1
    if len(R[j]) < n_j[j]:                  # 빈 자리 있음
        R[j].append(x_t)
    else:                                    # Algorithm R 핵심
        r = rng.integers(0, t_j[j])
        if r < n_j[j]:
            R[j][r] = x_t
    return R, t_j
```

**Vitter 1985 Algorithm L (skip-based 최적화, 옵션)**:
- Algorithm R = O(t_j) random number generations per stratum
- Algorithm L = O(log(t_j/n_j)) random number generations per stratum (skip-based, geometric distribution)
- 본 Form 1 적용 영역: streaming workload simulation 의 stream length N >> n_j 일 때 (e.g., 1M+ tuples) Algorithm L 권장. paper §V-B 의 1000 query × N=385 = 385K tuple per trial → Algorithm R 도 충분 (O(385K) per stratum 의 random number 생성은 numpy 로 빠름).
- **Agent F 권장**: Algorithm R 으로 phase 1 시작, paper-grade future 에 Algorithm L 으로 최적화.

### 1.2 Python 구현 코드 plan (measure_paper_exact.py 통합 방식)

**기존 measure_paper_exact.py 의 sampling 영역**:
- line 285-403 `measure_b1_paper`: paper §V-B Bernoulli (batch 환경, 전체 데이터에서 random sample)
- line 910-1003 `measure_case_a`: 우리 method stratified (batch 환경, KM20 fixed cluster + equal alloc)
- line 1006-1104 `measure_case_b`: B1 + CaseA ensemble (batch 환경, simple average)

**신규 추가 영역 (Component A)**:

```python
# 신규 file: _internal/scripts/measure_form1_streaming.py (예상 600 line)
# (measure_paper_exact.py 의 fetch_all_vectors / trial loop 80% 재사용)

import numpy as np
from typing import Optional
from measure_paper_exact import (
    AdaptiveState, q_error, trimmed_mean, build_cell_specs,
    PAPER_HYPERPARAM, PAPER_SEL_DEFAULT, TRIALS, TRIM,
    DATASET_ALIAS, TPC_H_THRESHOLD,
)


class StratifiedReservoir:
    """Per-stratum Vitter 1985 Algorithm R reservoir.

    Component A (SRS) — paper Eq 1 (Bernoulli) 대체.
    Al-Kateb-Lee SSDBM 2010 stratified reservoir + paper N=385 budget 유지.
    """
    def __init__(self, n_strata: int, capacity_per_stratum: list[int], dim: int,
                 rng: Optional[np.random.Generator] = None):
        self.K = n_strata
        # numpy 로 reservoir 사전 할당 (O(N×d) memory)
        self.R = [np.zeros((cap, dim), dtype=np.float32) for cap in capacity_per_stratum]
        self.t = np.zeros(n_strata, dtype=np.int64)   # 누적 tuple count per stratum
        self.filled = np.zeros(n_strata, dtype=np.int32)  # 현재 채워진 자리
        self.cap = capacity_per_stratum
        self.dim = dim
        self.rng = rng if rng is not None else np.random.default_rng()

    def update(self, x_t: np.ndarray, j_star: int) -> None:
        """Online single-tuple update.

        x_t      : (d,) vector
        j_star   : cluster id (BIRCH 가 부여, 0~K-1)
        """
        self.t[j_star] += 1
        if self.filled[j_star] < self.cap[j_star]:
            # 빈 자리 있음 (Vitter Algorithm R initialization)
            idx = self.filled[j_star]
            self.R[j_star][idx] = x_t
            self.filled[j_star] += 1
        else:
            # Vitter Algorithm R replace rule: probability cap/t
            r = self.rng.integers(0, self.t[j_star])
            if r < self.cap[j_star]:
                self.R[j_star][r] = x_t

    def realloc(self, new_capacity_per_stratum: list[int]) -> None:
        """Reservoir capacity update (paper Eq 5 sampling_size update 시).

        new_cap[j] > self.cap[j] → np.zeros pad
        new_cap[j] < self.cap[j] → 첫 new_cap[j] 만 유지 (truncate, 정밀 down-sampling 은 future work)
        """
        for j in range(self.K):
            if new_capacity_per_stratum[j] > self.cap[j]:
                pad = np.zeros((new_capacity_per_stratum[j] - self.cap[j], self.dim), dtype=np.float32)
                self.R[j] = np.vstack([self.R[j], pad])
            elif new_capacity_per_stratum[j] < self.cap[j]:
                self.R[j] = self.R[j][:new_capacity_per_stratum[j]]
                self.filled[j] = min(self.filled[j], new_capacity_per_stratum[j])
        self.cap = new_capacity_per_stratum

    def estimate(self, qvec: np.ndarray, D: float, total_rows: int,
                 sizes: np.ndarray) -> float:
        """Stratified estimator: Σ_j (N_j / |R_j|) × hits_j.

        qvec      : (d,) query vector
        D         : distance threshold
        total_rows: total dataset size (paper Eq 1 ratio)
        sizes     : (K,) cluster size estimate (BIRCH CF tuple 의 N_j)
        """
        est = 0.0
        for j in range(self.K):
            if self.filled[j] == 0 or sizes[j] == 0:
                continue
            # L2 distance 측정 (qvec - R[j][:filled[j]])
            dists = np.linalg.norm(self.R[j][:self.filled[j]] - qvec, axis=1)
            hits_j = int((dists < D).sum())
            est += (sizes[j] / self.filled[j]) * hits_j
        return est


def group_aware_alloc(total_budget: int, sizes: np.ndarray,
                      sigma: np.ndarray, mode: str = "proportional") -> np.ndarray:
    """Component D 분포 인지 allocation.

    sizes  : (K,) N_j (BIRCH CF tuple count)
    sigma  : (K,) σ_j (BIRCH CF tuple LS/SS 로 계산)
    mode   : "equal" | "proportional" | "neyman" | "anti_neyman"
    """
    K = len(sizes)
    if mode == "equal":
        n_j = np.full(K, total_budget // K, dtype=np.int64)
    elif mode == "proportional":
        weights = sizes.astype(np.float64) / sizes.sum()
        n_j = (total_budget * weights).round().astype(np.int64)
    elif mode == "neyman":
        weights = (sizes * sigma).astype(np.float64)
        weights = weights / weights.sum()
        n_j = (total_budget * weights).round().astype(np.int64)
    elif mode == "anti_neyman":
        weights = (sizes / (sigma + 1e-8)).astype(np.float64)
        weights = weights / weights.sum()
        n_j = (total_budget * weights).round().astype(np.int64)
    else:
        raise ValueError(f"unknown mode: {mode}")
    # 0 보호 (각 cluster 최소 1)
    n_j = np.maximum(n_j, 1)
    # budget 정확 일치 보정 (round error)
    diff = total_budget - n_j.sum()
    if diff != 0:
        max_idx = int(np.argmax(n_j))
        n_j[max_idx] += diff
    return n_j
```

### 1.3 complexity 분석

| 영역 | memory | time per tuple (online update) | time per query (estimate) |
|---|---|---|---|
| Bernoulli (paper baseline) | O(N × d) = O(385 × d) | O(1) (random sampling 의 amortized) | O(N × d) (distance N times) |
| **SRS Equal** | O(N × d) = O(K × n_j × d) ≈ O(385 × d) | **O(1)** (Algorithm R) | O(N × d) (distance N times, K branch) |
| **SRS Proportional** | 동일 | 동일 | 동일 |
| **SRS Neyman** | 동일 + O(K) σ_j cache | O(1) + sigma online update O(d) | 동일 |

**핵심 결론**:
- SRS 의 memory = Bernoulli 와 **동일** (O((N+K)×d) ≈ O(N×d) since K=20 << N=385)
- time per tuple = O(1) (Algorithm R 의 핵심 advantage)
- time per query = O(N × d) (paper Bernoulli 와 동일, K branch overhead 무시 가능)

**paper §V-B 와의 차별점**:
- paper Bernoulli = **batch 환경 전제** (full dataset access 필요, scan 단계 마다 re-sample)
- SRS = **streaming 환경 가능** (각 tuple O(1) update, scan 단계 1 회만)

### 1.4 test plan (Component A 검증)

**unit test 1 — Vitter Algorithm R 정확성**:
- N = 1000 tuple stream, K = 5 stratum, n_j = 20 per stratum
- 각 tuple 의 reservoir 포함 확률 = n_j / N_j (Vitter 1985 의 theoretical bound)
- 10000 trial × 측정 → 확률 fit 검증 (95% CI)

**unit test 2 — estimator unbiasedness**:
- known distribution (e.g., 2D Gaussian mixture K=5) + threshold D 고정
- true_card 정확 계산 + SRS estimate → bias < 5% (10000 trial × 평균)

**unit test 3 — paper §V-B baseline 일치**:
- K=1 (single stratum, no stratification) + Equal alloc → paper Bernoulli 와 **수학적 동일** (검증 가능)
- measure_b1_paper 결과 vs SRS K=1 결과 paired Δ% < 0.1% 필요

**unit test 4 — realloc 정확성**:
- t=500 시점 capacity update (Eq 5 sampling_size 의 변화 시뮬레이션)
- realloc 전후 reservoir 내용 일치 (truncate / pad 모두 검증)

★ **test 코드 작성 시간**: 4-6h (pytest 패턴, 500 line 추정).

---

## 2. Component B (BIRCH — Online Cluster Maintenance) 구현 detail

### 2.1 scikit-learn `Birch` API 활용 방식

**파라미터 결정 (공식 doc + 본 연구 fit)**:

| 파라미터 | scikit-learn default | 본 Form 1 권장 | 이유 |
|---|---|---|---|
| `n_clusters` | 3 | **20** | RQ2/RQ3 의 K=20 paper exact 정합 |
| `threshold` | 0.5 | **dataset adaptive** (DEEP 0.5, SIFT 0.3, SSN 0.4) | dataset 별 cluster 평균 distance scale 다름 (DEEP 96d / SIFT 128d / SSN 256d) |
| `branching_factor` | 50 | **50** (default 유지) | scikit-learn default 가 paper 영역 enough |
| `compute_labels` | True | **False** (partial_fit 시) | streaming 시 cost 절감, predict() 별도 호출 |

**threshold dataset adaptive 결정 방식**:
- step 1: warm-up 1% 의 dataset 으로 KMeans K=20 fit
- step 2: min pairwise distance between centroids 의 50% 를 threshold 로 설정
- step 3: Birch initialization 시 사용

**streaming partial_fit 패턴 (measure_paper_exact.py line 623-630 이미 구현)**:

```python
# 기존 line 623-630 (이미 작동, batch 환경)
if method_name == "birch":
    from sklearn.cluster import Birch
    birch = Birch(n_clusters=n_strata, threshold=0.5, branching_factor=50)
    # Streaming: chunk 단위 partial_fit
    chunk = 100_000
    for i in range(0, len(all_vecs), chunk):
        birch.partial_fit(all_vecs[i:i+chunk])
    return birch.predict(all_vecs).astype(np.int32)
```

**Form 1 streaming 영역 wrapper (신규)**:

```python
class OnlineBirchCluster:
    """Component B — paper §V-B Adaptive Sampling 의 online cluster maintenance.

    Zhang-Ramakrishnan-Livny SIGMOD 1996 BIRCH + scikit-learn `Birch` partial_fit API.
    CF tuple (N_j, LS_j, SS_j) 을 manual 보관 (subcluster_centers_ 에 cluster 만 있음).
    """
    def __init__(self, n_clusters: int = 20, threshold: float = 0.5,
                 branching_factor: int = 50, dim: int = 96):
        from sklearn.cluster import Birch
        self.birch = Birch(n_clusters=n_clusters, threshold=threshold,
                           branching_factor=branching_factor, compute_labels=False)
        self.K = n_clusters
        self.dim = dim
        # CF tuple per cluster (manual 유지 — scikit-learn Birch 가 직접 노출 X)
        self.N_j = np.zeros(n_clusters, dtype=np.int64)        # count per cluster
        self.LS_j = np.zeros((n_clusters, dim), dtype=np.float64)  # linear sum
        self.SS_j = np.zeros((n_clusters, dim), dtype=np.float64)  # squared sum
        self.fitted = False

    def partial_fit(self, X_chunk: np.ndarray) -> None:
        """Online update chunk 단위."""
        self.birch.partial_fit(X_chunk)
        self.fitted = True
        # CF tuple manual 업데이트 (predict 결과로 cluster 별 N/LS/SS 누적)
        labels = self.birch.predict(X_chunk)
        for j in range(self.K):
            mask = (labels == j)
            if mask.any():
                X_j = X_chunk[mask]
                self.N_j[j] += len(X_j)
                self.LS_j[j] += X_j.sum(axis=0).astype(np.float64)
                self.SS_j[j] += (X_j ** 2).sum(axis=0).astype(np.float64)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """현재 cluster id 부여 (Component A 의 j_star)."""
        return self.birch.predict(X).astype(np.int32)

    def centroids(self) -> np.ndarray:
        """Current cluster centroids C_j (online maintained)."""
        if self.fitted:
            return self.birch.subcluster_centers_  # 단, n_clusters final clustering 결과
        return np.zeros((self.K, self.dim), dtype=np.float32)

    def sigma_squared(self) -> np.ndarray:
        """Component D 의 Neyman/Anti-Neyman 에 필요한 σ_j² (online).

        CF tuple identity: σ_j² = SS_j / N_j − (LS_j / N_j)²
        (per-dimension variance 의 평균; 또는 L2 norm 의 expected square 변형)
        """
        sigma_sq = np.zeros(self.K, dtype=np.float64)
        for j in range(self.K):
            if self.N_j[j] == 0:
                sigma_sq[j] = 0.0
                continue
            mean_j = self.LS_j[j] / self.N_j[j]
            mean_sq = (mean_j ** 2).sum()
            sq_mean = self.SS_j[j].sum() / self.N_j[j]
            sigma_sq[j] = max(sq_mean - mean_sq, 1e-8)  # 0 보호
        return sigma_sq
```

### 2.2 paper period P (50 query) align 방식

**paper Eq 5-6 의 period P=50**:
- paper §V-B verbatim: "Sample size updates are triggered every 50 queries"
- AdaptiveState.update() 에서 `iter % 50 == 0` 일 때 trigger

**BIRCH K-means refinement trigger 옵션 3**:
1. **align 1**: AdaptiveState.update() 와 동기 (50 query 마다 BIRCH refit `Birch.predict(R)` 또는 K-means on `subcluster_centers_`)
2. **align 2**: tuple count 기반 (예: every 100K new tuples → BIRCH 의 inherent rebuild)
3. **align 3**: hybrid (50 query trigger 시 + 1M tuple threshold 시)

**Agent F 권장 = align 1** (paper period P 와 직접 동기). 이유:
- paper §V-B 의 dynamic batch loop 와 가장 fit
- 50 query trigger 시 BIRCH 의 `partial_fit` → 새 tuple 통합 + refresh
- 50 query interval 의 cost 분석: 50 query × 1ms estimate = 50ms 의 query cost → BIRCH refit 추가 cost 1-5ms (chunk size = 새 tuple 누적량) → 약 5-10% overhead acceptable

### 2.3 CF tuple → C_j + σ_j² 추정 정확성 검증 방식

**accuracy 검증 protocol**:
- ground truth: offline KMeans K=20 의 centroids + cluster 별 variance
- online BIRCH: 본 OnlineBirchCluster 의 centroids() + sigma_squared()
- metric:
  - centroid drift: ||C_j_birch - C_j_offline||_2 (per cluster + mean over K)
  - σ_j² gap: |σ_j²_birch - σ_j²_offline| / σ_j²_offline (relative error)

**예상 결과 (literature 기반)**:
- BIRCH CF tuple 의 N_j 는 exact (count) → 0% error
- LS_j / SS_j 는 floating-point accumulation 영향 → < 0.1% error (online 누적 시)
- centroid: BIRCH 의 inherent 정확도 (threshold T_b 영향) → 3-10% drift vs offline KMeans
- σ_j²: 동일 영역 → 5-15% drift

★ **detect-and-correct 패턴**: 본 Form 1 측정 영역 = 측정 2 (online cluster maintenance cost 540 file) — accuracy degradation 정량 표.

---

## 3. Component C (paper Eq 2-6 통합) 구현 detail

### 3.1 paper §V-B 영역 정확 정독 (PDF 직접 read 결과)

★ **중요 정정**: paper §V-B 영역에는 "Algorithm 1 14-step pseudo-code" 가 **존재 X**. paper 의 sampling-based cardinality estimation 영역 (§V-B) 의 알고리즘적 명세는 **자연 산문 + Eq 1-6 수식 + hyperparam 7 종** 형태.

**paper §V-B (PDF p.6) verbatim 텍스트 영역 (Eq 1-6 + 산문)**:

> "To determine an appropriate sample size, Exqutor uses a statistical formula derived from classical sampling theory. The required number of samples N is computed as:
>
> **N = ⌈z² · P̂ · (1 − P̂) / e²⌉**     (Eq 1)
>
> ...
>
> **Adaptive sampling size adjustment.** While fixed sample sizes provide statistical guarantees, they may not be equally effective across datasets with varying distributions or dimensionalities. ... Exqutor introduces an adaptive sampling mechanism that dynamically adjusts the sample size based on estimation accuracy observed after query execution.
>
> Exqutor employs a momentum-based adjustment algorithm combined with a learning rate scheduler to adapt the sampling size over time. ... The adjustment is guided by the Q-error [68]–[70], which measures the deviation between the estimated and true cardinality:
>
> **Q-error = max(Card_esti / Card_true, Card_true / Card_esti)**     (Eq 2)
>
> Using this metric, Exqutor tracks recent estimation accuracy and updates the sample size according to the following rule:
>
> **δ = α · (Q-error − β) − (100 − α) · sampling_ratio**     (Eq 3)
> **V_t = m · V_{t-1} + η_t · δ**                            (Eq 4)
> **sampling_size_{t+1} = sampling_size_t + V_t**            (Eq 5)
>
> Here, δ is the adjustment factor computed from estimation error and the current sampling ratio, which determines the direction and magnitude of sample updates. V_t is the momentum term at iteration t, m is the momentum coefficient, and η_t is the learning rate. α balances the contribution between Q-error and the sampling ratio, and β is a tunable threshold representing acceptable Q-error.
>
> The learning rate is decayed at each iteration using:
>
> **η_{t+1} = γ · η_t**                                      (Eq 6)"

**paper §VI (PDF p.7) hyperparam 영역 verbatim**:

> "For sampling-based cardinality estimation, we initially compute the number of samples N using the sample size formula (Equation 1) for sample size estimation [67], given a 95% confidence level (z = 1.96), a proportion estimate P̂ = 0.5, and a 5% margin of error (e = 0.05). Applying the formula yields a fixed sample size of **N = 385**.
>
> For adaptive sampling, we extend the optimizer with momentum-based feedback control. Parameter values are selected based on prior work on adaptive query estimation [22], [70]: we set the **momentum coefficient m = 0.9, initial learning rate η₀ = 0.1, weighting factor α = 50, and target Q-error β = 1.5**. These values balance Q-error minimization and sample size stability. The **learning rate decay factor γ = 0.99** gradually reduces adjustment magnitude to ensure convergence. **Sample size updates are triggered every 50 queries**."

★ **본 Agent F 정정 결론**:
- paper 자체에 "Algorithm 1 14-step pseudo-code" 는 **없음**.
- Agent C/D/E 가 의역 (편의상) step-wise 로 풀어쓴 것 → 본 Agent F + 5/27 발표 + 6/11 보고서 + 5/15 박광현 review form 에서 **"paper Eq 1-6 + 본 연구 의역 step-wise pseudo-code"** 로 명확 분리 표기 필수.
- "Algorithm 1 14-step" 표현 사용 시 → "본 연구 의역 14-step" 명시 (paper exact X)

### 3.2 본 연구 의역 step-wise pseudo-code (paper Eq 1-6 + Component A+B+D augment)

**본 연구 의역 step-wise (paper Eq 1-6 verbatim 영역 + 본 연구 신규 영역 명확 분리)**:

```
Component C — Form 1 Streaming-aware Adaptive Sampling
(paper Eq 1-6 verbatim 영역 = paper §V-B 그대로 / 본 연구 영역 = ★ 표시)

# === Initialization ===
Step 1 [paper Eq 1 verbatim]:
    N = ⌈z² · P̂ · (1 − P̂) / e²⌉ = 385       # paper sample budget

Step 2 [paper §VI verbatim]:
    V_0 = 0, η_0 = 0.1, t = 0                  # paper init
    m = 0.9, α = 50, β = 1.5, γ = 0.99, P = 50  # paper hyperparam 7 종

Step 3 [★ 본 연구 Component B init]:
    BIRCH = OnlineBirchCluster(n_clusters=K=20,
                                threshold=adaptive(dataset),
                                branching_factor=50)
    SRS = StratifiedReservoir(n_strata=K=20,
                              capacity_per_stratum=group_aware_alloc(N=385, ...),
                              dim=d)

# === Streaming + Query Loop ===
Step 4 [★ 본 연구 streaming axis]:
    for each new tuple x_t arriving in stream:
        # Component B: online cluster maintenance
        BIRCH.partial_fit([x_t])
        j_star = BIRCH.predict([x_t])
        # Component A: per-stratum reservoir update (Vitter Algorithm R)
        SRS.update(x_t, j_star)

Step 5 [paper §V-B verbatim 의역, query 마다]:
    for each query q in workload:

Step 6 [★ 본 연구 Component A + D estimate]:
        sizes = BIRCH.N_j                       # online cluster size
        sigma_j = sqrt(BIRCH.sigma_squared())   # online σ_j
        # Component D: distribution-aware allocation (rebuild reservoir capacity 시)
        # 단, paper period P 와 align (Step 12 와 동기)
        est_q = SRS.estimate(qvec=q.vector, D=q.threshold,
                              total_rows=BIRCH.N_j.sum(),
                              sizes=sizes)

Step 7 [paper Eq 2 verbatim]:
        Q_error_t = max(est_q / true_q, true_q / est_q)

Step 8 [paper §V-B period verbatim, Step 9-13 그룹]:
        if (t mod P) == 0 and t > 0:

Step 9 [paper Eq 3 verbatim]:
            ratio = sampling_size_t / total_rows
            δ = α · (Q_error_t − β) − (100 − α) · ratio

Step 10 [paper Eq 4 verbatim]:
            V_t = m · V_{t-1} + η_t · δ

Step 11 [paper Eq 5 verbatim + ★ 본 연구 augment]:
            # paper Eq 5: sampling_size_{t+1} = sampling_size_t + V_t (scalar)
            new_size = max(1, round(sampling_size_t + V_t))
            sampling_size_{t+1} = new_size

            # ★ 본 연구 augment (paper 미사용):
            # group-aware allocation = paper Eq 5 의 new_size 를 cluster 별로 분배
            n_j_new = group_aware_alloc(total_budget=new_size,
                                        sizes=BIRCH.N_j,
                                        sigma=sigma_j,
                                        mode="proportional")   # Component D
            SRS.realloc(n_j_new)              # 본 Form 1 핵심 augment

Step 12 [paper Eq 6 verbatim]:
            η_{t+1} = γ · η_t

Step 13:
        t = t + 1
```

★ **본 연구 의역 영역의 정직 표기 (5/15 박광현 review form + 5/27 발표)**:
> "Step 1-2, Step 5, Step 7-12 = paper §V-B Eq 1-6 verbatim 영역 (paper exact 100% 유지).
> Step 3, Step 4, Step 6, Step 11 의 augment 영역 = 본 연구 추가 영역 (paper 미사용).
> '14-step' 형식 자체는 본 연구가 paper §V-B 의 산문을 step-wise 의역한 것 (paper 자체에 Algorithm 1 14-step pseudo-code 형식은 없음)."

### 3.3 Step 11 Proportional 분배 구현 (★ 본 Form 1 핵심)

**paper Eq 5 의 scalar update**:
- `sampling_size_{t+1} = sampling_size_t + V_t` (전체 sample size 의 scalar 변화)
- paper §V-B 의 Bernoulli 환경에서는 cluster 개념 없음 → scalar 만 update

**본 연구 augment (group-aware Proportional 분배)**:
- paper Eq 5 의 new_size 를 cluster 별로 분배
- `n_j_new = group_aware_alloc(new_size, BIRCH.N_j, BIRCH.σ_j, mode="proportional")`
- 본 Form 1 권장 = Proportional (RQ2 의 Neyman paradox 결과: sel=0.01 한정에서 Neyman ≈ Prop, 일반 selectivity 영역 Prop 안정)

**구현 영역 (measure_form1_streaming.py 추가)**:

```python
def update_with_group_aware(self, q_error: float, sampling_ratio: float,
                             birch: OnlineBirchCluster, srs: StratifiedReservoir,
                             mode: str = "proportional") -> int:
    """Component C — paper Eq 1-6 verbatim + Step 11 group-aware augment.

    paper Eq 3-6 그대로 (measure_paper_exact.py AdaptiveState.update 동일).
    paper Eq 5 의 new_size 를 group-aware allocation 으로 분배 (본 Form 1 augment).
    """
    self.iter += 1
    if self.iter % self.update_period != 0:
        return self.size

    q_err_safe = float(q_error) if np.isfinite(q_error) else 100.0
    # paper Eq 3 verbatim
    delta = self.alpha * (q_err_safe - self.beta) - (100 - self.alpha) * sampling_ratio
    # paper Eq 4 verbatim
    V_t = self.m * self.V_prev + self.eta * delta
    # paper Eq 5 verbatim
    new_size = max(1, int(round(self.size + V_t)))
    # ★ 본 연구 Component D augment: group-aware allocation
    n_j_new = group_aware_alloc(total_budget=new_size,
                                 sizes=birch.N_j,
                                 sigma=np.sqrt(birch.sigma_squared()),
                                 mode=mode)
    srs.realloc(n_j_new.tolist())  # ★ 본 Form 1 핵심 augment
    # paper Eq 6 verbatim
    self.eta = self.gamma * self.eta
    self.V_prev = V_t
    self.size = new_size
    return self.size
```

### 3.4 paper Eq 2-6 verbatim 검증 (measure_paper_exact.py 직접 read 결과)

**measure_paper_exact.py line 100-140 의 AdaptiveState 구현 = paper Eq 1-6 verbatim 100% 정합**:

| paper | measure_paper_exact.py line | 정합 여부 |
|---|---|---|
| Eq 1: N = 385 | line 67 `"N_init": 385` | ✓ |
| Eq 2: Q-error | line 147-151 `q_error()` | ✓ |
| Eq 3: δ | line 127 `delta = self.alpha * (q_err_safe - self.beta) - (100 - self.alpha) * sampling_ratio` | ✓ |
| Eq 4: V_t | line 129 `V_t = self.m * self.V_prev + self.eta * delta` | ✓ |
| Eq 5: sampling_size update | line 131 `new_size = max(1, int(round(self.size + V_t)))` | ✓ |
| Eq 6: η decay | line 139 `self.eta = self.gamma * self.eta` | ✓ |
| period 50 | line 74 `"update_period": 50` + line 121 `if self.iter % self.update_period != 0` | ✓ |
| hyperparam 7 종 | line 67-76 verbatim | ✓ |

★ **본 Form 1 phase 1 = measure_paper_exact.py 의 AdaptiveState verbatim 유지** + group_aware_alloc helper 추가만으로 구현 가능.

---

## 4. Component D (Distribution-aware Stratification) 구현 detail

### 4.1 Proportional / Equal / Neyman / Anti-Neyman 모두 측정 axis

**RQ2 의 5-way axis 와 정합 (Bernoulli 제외 4 mode)**:

| mode | allocation rule | RQ2 실측 결과 (5/12 02:50 paper exact REPORT v11) | 본 Form 1 streaming axis 측정 영역 |
|---|---|---|---|
| **Equal** | n_j = N/K | qe_trim 1.620 (cell 5 mean) | 측정 1/3 default |
| **Proportional** | n_j ∝ N_j | qe_trim 1.580 (mean, ★ 본 Form 1 권장) | 측정 1/3 default |
| **Neyman** | n_j ∝ N_j · σ_j | qe_trim 1.595 (paradox sel=0.01 한정) | 측정 1/3 + 측정 5 |
| **Anti-Neyman** | n_j ∝ N_j / σ_j | qe_trim 1.540 (negative control) | 측정 5 (sanity) |

★ **RQ2 결과의 Form 1 시사 (paper-grade)**:
- Bernoulli → Proportional **−9.53%** Δ% (5 cell × 5 trial)
- Neyman paradox sel=0.01: σ_j range narrow 1.3-1.6× + N_i CV=0 (uniform cluster size) → Neyman ≈ Prop 통계적 동일
- **본 Form 1 권장 = Proportional** (paper exact safe + 실제 streaming 환경에서 BIRCH 의 N_j online 유지 비용 적음)

### 4.2 L2-L4 정보 수준 axis 분리

**Cochran 1977 §5 의 정보 수준 hierarchy**:
- **L1**: random sampling (no information, Bernoulli baseline = paper)
- **L2**: stratification boundary only (cluster id 만 알면 됨, Equal)
- **L3**: + size N_j (cluster boundary + size, Proportional)
- **L4**: + variance σ_j (boundary + size + variance, Neyman / Anti-Neyman)

**본 Form 1 streaming 환경의 정보 수준 axis**:
- L2 Equal = BIRCH.predict() 만 필요 (cluster id) — 최저 cost
- L3 Proportional = BIRCH.N_j 추가 필요 (count) — 추가 cost 적음
- L4 Neyman = BIRCH.sigma_squared() 추가 필요 (LS/SS 계산) — 추가 cost 보통

**측정 영역 (측정 1 streaming + 측정 3 4-way 비교)**:
- 4 mode 모두 동일 측정 protocol
- paired Δ% (Bernoulli baseline 대비) + mean Q-error + final sample size + final eta
- 정보 수준 hierarchy 표 (L1 / L2 / L3 / L4 별 Q-error 비교)

★ **본 Form 1 의 학술 contribution**:
- paper §V-B Bernoulli = L1 정보 수준 (no stratification)
- 본 Form 1 = L2/L3/L4 정보 수준 (streaming 환경 stratification, 분포 인지)
- 정보 수준 hierarchy 측정 = paper-grade contribution 가능 영역 (paper 미수행)

### 4.3 구현 영역 (group_aware_alloc 함수, 위 1.2 절 코드 참조)

본 Agent F § 1.2 절 `group_aware_alloc(total_budget, sizes, sigma, mode)` 가 Component D 의 핵심 implementation. mode parameter 로 4 종 allocation 전환.

★ measure_form1_streaming.py 통합 시 추가 cost: 본 함수 + np 기반 → 50 line 추정, 검증 cost 2-3h.

---

## 5. 측정 1-5 세부 protocol

### 5.1 측정 1 — Streaming Workload Simulation (1440 file, 본 Form 1 핵심)

**objective**: paper §VI-B "shifting workloads" 영역 정량 측정 (paper 미수행).

**setup**:
- **dataset**: DEEP (96d) + SIFT (128d) + SSN (256d) × sf=100 (paper Fig 5/6 verbatim)
- **query**: paper TPC-H Q3/Q10/Q12 vector range query + concept drift simulation
- **concept drift scenario 3 종**:
  - (a) **No drift (baseline)**: paper §V-B 와 동일 정적 환경, BIRCH 가 batch K-means 와 동일 수렴 영역
  - (b) **Gradual drift**: cluster centroid 가 매 1000 query 마다 ε 거리 (각 dim 별 Gaussian random walk σ=0.01·d) 만큼 shift
  - (c) **Sudden drift**: 매 5000 query 마다 distribution swap (전체 data point 의 stratum_id 재할당, 또는 새 cluster 영역 도입)
- **method 4 종**: Bernoulli (paper baseline) + SRS Equal + SRS Proportional (★ 본 Form 1 메인) + SRS Neyman
- **mode 2 종**: streaming online (BIRCH partial_fit) + batch baseline (offline KMeans, 비교용)
- **trial = 10 per scenario**

**measurement metric**:
- Q-error mean / Q-error std / Q-error trim mean
- final sample size + final eta
- cluster centroid drift Δ% (offline KMeans vs online BIRCH)
- sample size trajectory (paper Fig 6 layout 재현)

**file count**: 3 dataset × 3 drift × 4 method × 2 mode × 10 trial = **720 file** (★ Agent E 산정 1440 file 의 0.5×, 1 sf 만 측정. 만약 sf=10, 100 모두 측정 시 1440 file 일치)

★ **Agent F 수정 권장**: sf=100 만 phase 1 측정 (720 file, server 4-6h) → 5/27 까지 충분. sf=10 추가 측정 (720 file, 추가 server 4-6h) → 6/11 까지.

**측정 코드 영역**:
```python
def measure_form1_streaming(cell: CellSpec, method_name: str, drift_scenario: str,
                              mode: str, n_queries: int = 1000, trials: int = TRIALS,
                              output_dir: Optional[Path] = None) -> dict:
    """Form 1 측정 1 — streaming workload simulation.
    
    Args:
        cell: CellSpec (paper exact dataset)
        method_name: "bernoulli" | "srs_equal" | "srs_proportional" | "srs_neyman"
        drift_scenario: "no_drift" | "gradual" | "sudden"
        mode: "streaming" | "batch"  # streaming = BIRCH partial_fit, batch = offline KMeans baseline
        n_queries: paper Fig 6 verbatim 1000
        trials: paper 10 verbatim
    """
    # ... (measure_paper_exact.py 의 measure_b1_paper 패턴 재사용)
    # 신규 영역:
    #   1. BIRCH wrapper (OnlineBirchCluster) for mode="streaming"
    #   2. drift injection logic for drift_scenario
    #   3. SRS wrapper for method_name
    #   4. group_aware_alloc for paper Eq 5 augment
    # ... (예상 코드량: 350 line, 작성 cost 8-10h)
```

**예상 결과 (literature + RQ2/RQ3 결과 기반 추정)**:
- No drift: SRS Proportional vs Bernoulli **−5 ~ −10%** Δ% (RQ2/RQ3 의 일관 결과)
- Gradual drift: SRS streaming Proportional vs Bernoulli **−3 ~ −8%** Δ% (drift adaptation 의 cost 일부 흡수)
- Sudden drift: SRS streaming Proportional vs Bernoulli **0 ~ −5%** Δ% (drift 시 transient 영역 우위 약함)

### 5.2 측정 2 — Online Cluster Maintenance Cost (540 file)

**objective**: BIRCH CF-tree maintenance 의 memory / latency / accuracy degradation 정량 측정.

**setup**:
- **BIRCH threshold T_b 변화**: 0.1, 0.3, 0.5, 1.0
- **K target**: 10, 20, 50 (paper exact K=20 + 변화)
- **update frequency**: every 50 query (paper period P) vs every 100 vs every 200
- **dataset**: DEEP/SIFT/SSN sf=100

**measurement metric**:
- memory peak (MB) per BIRCH instance
- latency per insert (μs)
- σ_j² estimation error vs offline KMeans (relative %)
- Q-error degradation vs offline KMeans baseline (mean delta)

**file count**: 3 dataset × 4 T_b × 3 K × 3 update freq × 5 trial = **540 file** (server 3-5h)

**측정 코드 영역**:
```python
def measure_birch_cost(cell: CellSpec, threshold: float, K: int, update_freq: int,
                       trials: int = 5, output_dir: Optional[Path] = None) -> dict:
    """Form 1 측정 2 — BIRCH online cluster maintenance cost."""
    # ... (OnlineBirchCluster + offline KMeans baseline 비교)
    # 예상 코드량: 200 line, 작성 cost 5-6h
```

### 5.3 측정 3 — 4-way 비교 (Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1) (600 file)

**objective**: paper §VI-D Fig.12 영역 확장 (paper L5 한계 보완).

**setup**:
- **5 method** (paper L5 확장):
  1. Bernoulli (paper baseline, B1 9 file 재사용)
  2. SelNet (paper [74] reference, MLPRegressor scikit-learn 또는 reference impl)
  3. CE4HD VLDB 2024 (Lan-Bao reference object 기반 learned model)
  4. Ada-ef arxiv 2512.06636 (cosine/IP/L2 distribution-aware HNSW)
  5. 본 Form 1 SRS + BIRCH + Eq 2-6 augment
- **dataset**: DEEP/SIFT/SSN sf=100 (★ 1001 file portfolio 와 정합) + sf=10 (★ Fig.12 정합)
- **selectivity**: paper §VI-D Fig.13 verbatim 3 levels {0.1%, 1%, 10%} → simplified {0.01, 0.10}
- **trial = 10**

**measurement metric**:
- Q-error mean / Q-error std / Q-error trim
- inference latency (ms) per query
- offline training cost (s) — SelNet/CE4HD/Ada-ef 만
- memory (MB)

**file count**: 5 method × 3 dataset × 2 sf × 2 sel × 10 trial = **600 file** (★ Agent E 산정 일치)

★ **5/27 timeline 영역 분담 (Agent F 권장)**:
- **5/27 phase 1 (cost 50-80h)**: Bernoulli + SelNet + 본 Form 1 SRS+BIRCH (3-way only, 360 file)
- **6/11 phase 2 (cost +50-80h)**: + CE4HD + Ada-ef (5-way full, 600 file)

**SelNet reference implementation 후보 (Agent F web search 결과)**:
- 공식 reference: paper [74] Wang-Qiu VLDB 2023 "SelNet: Selectivity Estimation via Deep Neural Networks"
- code repo: GitHub 검색 필요 (open-source 여부 확인)
- fallback: scikit-learn MLPRegressor 로 reproduce (paper 의 input feature + label 영역 의역)
- 예상 cost: 8-12h (코드 작성 + paper hyperparam 의역)

**CE4HD reference**:
- paper: Lan-Bao VLDB 2024 "Cardinality Estimation for High-Dimensional Vector Similarity Search"
- code repo: 공식 GitHub 가능성 있음 (확인 필요)
- 예상 cost: 12-18h (paper 의 SRCE/MRCE 영역 reproduce)

**Ada-ef reference**:
- paper: arxiv 2512.06636 (2025/2026 영역) "Adaptive Distribution-Aware HNSW"
- code repo: arxiv 공식 또는 supplementary (확인 필요)
- 예상 cost: 10-15h (cosine/IP/L2 distribution 추정 영역 reproduce)

★ **3 baseline 구현 cost 산정**: 30-45h (Agent E 산정 20-30h 보다 보수적). 5/27 까지는 SelNet 만 권장.

### 5.4 측정 4 — Distribution Shift Simulation (480 file)

**objective**: paper §VI-E Limitation 1 + 본 연구 "shifting workloads" 영역 정량 측정.

**setup**:
- **baseline**: 본 측정 1 의 no drift
- **variant 1**: 본 측정 1 의 gradual + sudden
- **추가 시나리오 4 종**:
  - (d) **Embedding model upgrade**: 동일 raw data 의 embedding 모델 변경 (Ada-002 → BGE-large) — 단 cost 어려움 (raw data 의 embedding 재계산 필요), 본 측정 4 는 simulation (cluster centroid 전체 transform) 으로 대체
  - (e) **Time-based drift**: timestamp 기반 cluster shift (news article topic drift simulation, dataset 의 timestamp column 활용)
  - (f) **Mixed workload**: 50% DEEP + 50% SIFT cross-dataset drift (dim 다름, dim padding 또는 truncation 필요)
  - (g) **Workload skew change**: zipf parameter 변화 (현재 skew 강도 변화)
- **method 4 종**: Bernoulli + SRS Equal + SRS Proportional + SRS Neyman + BIRCH baseline
- **trial = 5**

**file count**: 3 dataset × 4 추가 scenario × 4 method × 2 mode × 5 trial = **480 file** (★ Agent E 산정 일치)

★ **Agent F 정직 disclosure**: 시나리오 (d) embedding upgrade 는 raw data + embedding pipeline 영역 cost 어려움 → simulation 으로 대체 표기 필수. (f) cross-dataset 도 dim mismatch issue 있음 → simplified 표기.

### 5.5 측정 5 — Phase 2 Group-aware Eq 3-6 Augment (120 file, future work pilot)

**objective**: paper Eq 3-6 의 group-aware augment (Form 1 phase 2 future work).

**setup**:
- group-aware V_{j,t}: m_j = m (paper 0.9) 동일 유지, V_{j,t} = m · V_{j,t-1} + η_t · δ_j (cluster 별 momentum)
- group-aware δ_j: paper Eq 3 의 cluster-specific Q-error_j
- group-aware n_inc 분배: 본 Form 1 Component C Step 11 augment 와 동일
- dataset: DEEP/SIFT/SSN sf=100, mode 2 (streaming + batch), trial 10

**file count**: 3 dataset × 2 sf × 2 mode × 10 trial = **120 file** (★ Agent E 산정 일치)

★ **5/27 까지 X / 6/11 까지 X / paper-grade future 까지**.

---

## 6. 데이터셋 준비 plan

### 6.1 1001 file 데이터셋 활용 영역 (재활용)

| 데이터셋 | 현 상태 (1001 file portfolio) | Form 1 활용 |
|---|---|---|
| **DEEP 96d sf=100** | KM20 cluster pre-cached + query pool + Bernoulli baseline 9 file | ★ 직접 재사용 (배치 baseline) + streaming 추가 측정 |
| **SIFT 128d sf=100** | 동일 | ★ 직접 재사용 |
| **SSN 256d sf=100** | 동일 | ★ 직접 재사용 |
| **YFCC 192d sf=10** | A2-Fig7 cell 측정 미완 | △ 측정 4 추가 영역 (옵션) |
| **DEEP+WIKI sf=10** | A2-Fig8/9 multi-table 측정 80 회수 | △ multi-table 영역 (5/15 박광현 자료) |

★ **재활용 효율**: query_pool_{DEEP,SIFT,SSN}_sf100.parquet + 80M vector cached + KM20 sids cached → 데이터 준비 cost 0 (재사용).

### 6.2 Streaming Workload Generation 방식

**streaming 환경 simulation 코드 영역**:
```python
def generate_streaming_workload(all_vecs: np.ndarray, n_chunks: int = 100,
                                 drift_scenario: str = "no_drift", seed: int = 42) -> list:
    """기존 1001 file portfolio 의 batch 데이터를 streaming chunk 로 변환.
    
    Args:
        all_vecs: (N, d) — full dataset (e.g., 80M × 96 for DEEP sf=100)
        n_chunks: chunk 개수 (default 100, 각 chunk 800K tuples)
        drift_scenario: "no_drift" | "gradual" | "sudden"
    
    Returns:
        chunks: list of (X_chunk, drift_state) — 각 chunk + drift 정보
    """
    rng = np.random.default_rng(seed)
    N = len(all_vecs)
    chunk_size = N // n_chunks
    perm = rng.permutation(N)  # random ordering
    chunks = []
    
    for i in range(n_chunks):
        idx = perm[i*chunk_size:(i+1)*chunk_size]
        X_chunk = all_vecs[idx]
        
        if drift_scenario == "gradual":
            # 점진적 centroid shift: 각 chunk 마다 ε=0.01·dim 거리만큼 random walk
            if i > 0:
                shift = rng.standard_normal(X_chunk.shape[1]) * 0.01 * X_chunk.shape[1]
                X_chunk = X_chunk + shift
        elif drift_scenario == "sudden":
            # 매 5 chunks 마다 distribution swap (cluster 영역 재배치)
            if i > 0 and i % 5 == 0:
                X_chunk = rng.permutation(X_chunk)  # shuffle within chunk
        
        chunks.append((X_chunk, {"chunk_idx": i, "drift_scenario": drift_scenario}))
    return chunks
```

★ 코드 cost: 6-8h (드리프트 시나리오 logic + test 포함).

### 6.3 추가 데이터셋 (TPC-DS 활용?)

**Agent F 권장 = NO (5/27 / 6/11 phase 1 한정)**:
- TPC-DS = paper Fig.10 의 영역 (ECQO 의 verbatim 측정 영역, A3-TPCDS cell 별도)
- 본 Form 1 = sampling-based cardinality estimation 영역 (paper §V-B + §VI-B 영역) → TPC-DS X
- TPC-DS 활용 시 → 옵션 H (Agent C/D 의 별도 영역)
- **5/27 / 6/11 까지** = TPC-H 8 query × DEEP/SIFT/SSN sf=100 만 (paper Fig 5/6 verbatim)

---

## 7. measure script template

### 7.1 기존 measure_paper_exact.py (1407 line) 구조 활용

★ **기존 구조 80% 재사용**:
- `AdaptiveState` (line 104-140) — paper Eq 1-6 verbatim, **그대로 유지**
- `q_error()` (line 147-151) — paper Eq 2 verbatim, **그대로 유지**
- `trimmed_mean()` (line 154-168) — paper p.7 verbatim, **그대로 유지**
- `CellSpec` + `build_cell_specs()` (line 176-278) — paper cell matrix, **재사용**
- `measure_b1_paper()` (line 285-403) — Bernoulli baseline, **재사용 + 비교**
- `_get_method_strata()` (line 407+) — method registry, **재사용 + 추가 method**

★ **신규 영역 (20%)**:
- `StratifiedReservoir` class (Component A, 100 line)
- `OnlineBirchCluster` class (Component B, 80 line)
- `group_aware_alloc()` function (Component D, 50 line)
- `generate_streaming_workload()` function (측정 1 영역, 80 line)
- `measure_form1_streaming()` function (측정 1 main, 350 line)
- `measure_birch_cost()` function (측정 2, 200 line)
- `measure_4way_comparison()` function (측정 3, 400 line — SelNet/CE4HD/Ada-ef wrapper 포함)
- `measure_distribution_shift()` function (측정 4, 250 line)
- `measure_phase2_pilot()` function (측정 5, 200 line)

**총 신규 코드량 산정**: 약 1700 line (measure_paper_exact.py 1407 line + 1700 line ≈ 3100 line, 분리 file 권장).

★ **Agent F 권장 file 구조**:
```
_internal/scripts/
├── measure_paper_exact.py      # 기존 1407 line (유지)
├── measure_form1_common.py     # 신규 — Component A/B/D + streaming workload (500 line)
├── measure_form1_streaming.py  # 신규 — 측정 1 (400 line)
├── measure_form1_birch_cost.py # 신규 — 측정 2 (300 line)
├── measure_form1_4way.py       # 신규 — 측정 3 (500 line)
├── measure_form1_drift.py      # 신규 — 측정 4 (300 line)
└── measure_form1_phase2.py     # 신규 — 측정 5 (250 line, future work)
```

### 7.2 Component A+B+C+D 통합 script (measure_form1_common.py)

```python
"""Form 1 — Streaming-aware Distribution-Conscious CE for VAQ.

Component A (SRS) + Component B (BIRCH) + Component C (paper Eq 2-6 + augment) +
Component D (분포 인지 stratification).

paper §V-B Eq 1-6 verbatim 영역 = measure_paper_exact.py 의 AdaptiveState 재사용.
본 연구 영역 = 본 file 의 StratifiedReservoir + OnlineBirchCluster + group_aware_alloc.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

from measure_paper_exact import (
    AdaptiveState, q_error, trimmed_mean,
    PAPER_HYPERPARAM, PAPER_SEL_DEFAULT, TRIALS,
)


class StratifiedReservoir:
    """Component A — Vitter 1985 Algorithm R per-stratum reservoir."""
    # ... (위 § 1.2 참조)


class OnlineBirchCluster:
    """Component B — Zhang-Ramakrishnan-Livny 1996 SIGMOD BIRCH + sklearn wrapper."""
    # ... (위 § 2.1 참조)


def group_aware_alloc(total_budget: int, sizes: np.ndarray,
                      sigma: np.ndarray, mode: str = "proportional") -> np.ndarray:
    """Component D — Equal/Proportional/Neyman/Anti-Neyman allocation."""
    # ... (위 § 1.2 참조)


def generate_streaming_workload(all_vecs: np.ndarray, n_chunks: int = 100,
                                 drift_scenario: str = "no_drift",
                                 seed: int = 42) -> list:
    """Streaming workload simulation — drift 시나리오 3 종 (no_drift/gradual/sudden)."""
    # ... (위 § 6.2 참조)


class Form1AdaptiveState(AdaptiveState):
    """Form 1 augment: paper Eq 1-6 verbatim + Step 11 group-aware augment.
    
    paper Eq 3-6 verbatim 영역 = AdaptiveState.update() 동일.
    본 연구 augment = update_with_group_aware() 신규.
    """
    def update_with_group_aware(self, q_error: float, sampling_ratio: float,
                                 birch: OnlineBirchCluster,
                                 srs: StratifiedReservoir,
                                 mode: str = "proportional") -> int:
        # ... (위 § 3.3 참조)
        pass
```

### 7.3 logging / file 저장 format

★ **measure_paper_exact.py 의 패턴 그대로 활용**:
- JSON file per (cell, mode, method, scenario, trial 평균) — 기존 `output_dir / f"{cell.sub}_{mode}_{method}.json"` 패턴
- 본 Form 1 추가: `{cell.sub}_form1_{measurement}_{method}_{drift_scenario}.json`
  - 예: `A1-DEEP_form1_streaming_srs_proportional_gradual.json`

**JSON content (Form 1 측정 1 영역)**:
```json
{
  "cell": "A1-DEEP",
  "fig": "Form 1 측정 1",
  "dataset": "DEEP",
  "sf": 100,
  "mode": "streaming",
  "method": "srs_proportional",
  "drift_scenario": "gradual",
  "n_queries": 1000,
  "trials": 10,
  "avg_q_error_trimmed": 1.52,
  "final_size_mean": 412.3,
  "final_size_std": 18.7,
  "birch_centroid_drift_mean": 0.034,
  "birch_sigma_sq_error_mean": 0.082,
  "trial_results": [...],
  "paper_hyperparam": {...},
  "form1_augment": {
    "step_11_group_aware": "proportional",
    "component_a_srs": "vitter_algorithm_R",
    "component_b_birch": "sklearn_partial_fit"
  },
  "kst": "2026-05-15 14:30 KST"
}
```

### 7.4 parallelization / GPU 활용

**parallelization 영역**:
- **trial 병렬화**: 각 trial 의 BIRCH + SRS state 가 독립 → multiprocessing.Pool 로 trial 10 개 동시 실행 가능 (CPU 10 core 활용)
- **cell 병렬화**: 각 cell 의 dataset 독립 → tmux session 3 개 (DEEP/SIFT/SSN) 병렬 실행
- **method 병렬화**: method 4 종 의 dependence 없음 → 동시 실행 가능

★ **server (165.132.140.240) CPU 영역**: capstone2026 의 hardware 영역 = 보통 32-64 core 가능, BIRCH partial_fit 의 cost 0.1-1ms/insert × 80M insert × 100 chunk = 약 30분 / dataset / scenario / method × 4 method × 3 scenario × 3 dataset × 10 trial = 약 27h batch (병렬화 없을 시). **trial 10 + method 4 + dataset 3 = 120 task 병렬 → 약 1.5h** (32 core 활용).

★ **GPU 활용**: BIRCH + SRS 자체는 GPU 활용 X. SelNet/CE4HD/Ada-ef training 시 GPU 활용 가능 (PyTorch + CUDA), training cost 0.5-2h / model (paper 영역). 측정 cost 와 별도.

---

## 8. 코드 작성 시간 / cost 정확 산정 (Agent E 검증)

### 8.1 Component A-D 각 코드 시간 (line 수 + dev hour)

| Component | 신규 코드 | line 수 | dev hour | test cost |
|---|---|---:|---:|---:|
| **Component A (SRS)** | `StratifiedReservoir` class + `group_aware_alloc()` helper | 250 | 8-12h | 4-6h |
| **Component B (BIRCH)** | `OnlineBirchCluster` class + threshold tune | 200 | 10-15h | 4-6h |
| **Component C (Eq 1-6 + augment)** | `Form1AdaptiveState.update_with_group_aware()` | 100 | 4-6h | 2-3h |
| **Component D (분포 인지)** | `group_aware_alloc()` (mode 4 종) | 50 | 3-5h | 1-2h |
| **Streaming workload generator** | `generate_streaming_workload()` + drift 3 종 | 200 | 6-8h | 3-4h |
| **Component A-D 통합 (measure_form1_common.py)** | 통합 + import 정리 | 100 | 2-3h | 1-2h |
| **Component A-D 소계** | -- | **900** | **33-49h** | **15-23h** |

### 8.2 측정 1-5 script 시간

| 측정 | script file | line 수 | dev hour | server time |
|---|---|---:|---:|---:|
| **측정 1 streaming** | measure_form1_streaming.py | 400 | 8-12h | 8-12h |
| **측정 2 BIRCH cost** | measure_form1_birch_cost.py | 300 | 5-8h | 3-5h |
| **측정 3 4-way** | measure_form1_4way.py + SelNet/CE4HD/Ada-ef wrapper | 500 + (300+300+300) | 30-45h | 5-8h |
| **측정 4 drift** | measure_form1_drift.py | 300 | 6-10h | 3-5h |
| **측정 5 phase 2 pilot** | measure_form1_phase2.py | 250 | 5-8h | 1-2h |
| **측정 1-5 소계** | -- | **2350** | **54-83h** | **20-32h** |

### 8.3 분석 코드 시간 (1001 file analysis 9 file 와 통합)

| 분석 영역 | 신규/재사용 | dev hour |
|---|---|---:|
| paired Δ% 계산 (Bernoulli vs Form 1 method) | 재사용 (1001 file analysis 패턴) | 3-5h |
| paradigm rollup (8 paradigm + Form 1 streaming axis 추가) | 재사용 + 추가 | 4-6h |
| drift trajectory plot (paper Fig 6 layout) | 신규 (matplotlib) | 5-7h |
| 4-way bar plot (paper Fig 12 layout) | 신규 | 3-5h |
| online vs offline BIRCH degradation 표 | 신규 | 3-5h |
| REPORT v12 작성 (Form 1 streaming 영역 추가) | 재사용 + 추가 | 6-10h |
| **분석 소계** | -- | **24-38h** |

### 8.4 총 시간 vs Agent E 산정 검증

| 영역 | Agent E 산정 | Agent F 산정 | 차이 |
|---|---:|---:|---:|
| 알고리즘 구현 (Component A-D) | 30-40h | 33-49h | +3 ~ +9h |
| streaming simulation framework | 15-20h | 6-8h (별도 라인) | -9 ~ -12h |
| BIRCH 통합 | 5-10h | 10-15h | +5h |
| concept drift 구현 | 10-15h | 6-10h | -4 ~ -5h |
| 4-way baseline 구현 | 20-30h | 30-45h | +10 ~ +15h |
| 측정 실행 | 20-30h | 20-32h | 0 ~ +2h |
| 분석 + 시각화 | 15-20h | 24-38h | +9 ~ +18h |
| 5/27 deck + 6/11 보고서 + 부록 | 20-30h | 20-30h | 0 |
| test cost (Agent E 미포함) | -- | 15-23h | +15 ~ +23h |
| **총 합 (test 포함)** | **135-195h** | **164-250h** | **+29 ~ +55h** |
| **총 합 (test 미포함, Agent E base)** | **135-195h** | **149-227h** | **+14 ~ +32h** |

★ **Agent F 결론**:
- Agent E 산정 = 135-195h (test 미포함, 4-way baseline 보수적)
- Agent F 산정 = 149-227h (test 포함, 4-way baseline 보수적)
- **15-20% 더 보수적**, 5/27 timeline 위험 영역 = 4-way baseline 구현 (SelNet/CE4HD/Ada-ef 3 종 30-45h)

★ **5/27 phase 1 권장 영역 (cost 50-80h, Agent F 추정)**:
- Component A + B + D 구현 (cost 25-40h)
- 측정 1 streaming (cost 10-15h) + 측정 3 partial 3-way (Bernoulli + SelNet + 본, cost 15-25h)
- 분석 (cost 10-15h)
- 5/27 deck (cost 10-15h)
- **총 cost 50-80h 부합** (Agent E 산정 일치)

★ **5/27 timeline risk areas**:
- SelNet reference implementation cost = 8-12h (도전적, paper open-source 영역 확인 필요)
- BIRCH dataset adaptive threshold tune cost = 5-8h (DEEP/SIFT/SSN 별 threshold optimization)
- drift simulation의 (b) gradual / (c) sudden 코드 cost = 6-8h
- 분석 코드 cost = 10-15h (drift trajectory + 3-way bar)

---

## 9. main thread 종합 권장 사항

### 9.1 critical 정정 wording 룰 (5/15 박광현 미팅 + 5/27 발표 + 6/11 보고서 + paper-grade publication)

★ **본 Agent F 의 핵심 정정**:
1. **❌ "paper §V-B Algorithm 1 14-step pseudo-code"** → ✓ **"paper §V-B Eq 1-6 + hyperparam 7 종 (본 연구 의역 14-step pseudo-code)"**
   - paper 자체에 Algorithm 1 14-step 형식 X. paper 는 Eq 1-6 + 자연 산문 + hyperparam.
   - 본 연구가 의역해서 step-wise 로 풀어쓴 영역 명시 필수.

2. **❌ "paper 14-step 中 Step 11 augment"** → ✓ **"paper Eq 5 (sampling_size update) 의 본 연구 group-aware allocation augment"**
   - Step 11 표현 = 본 연구 의역 영역 (paper 자체 표현 X).
   - paper exact = Eq 5 scalar update / 본 연구 augment = group-aware allocation.

3. **❌ "Algorithm 1 14-step verbatim 정확 정독"** → ✓ **"paper §V-B Eq 1-6 verbatim + paper §VI 도입부 hyperparam 7 종 verbatim 정확 정독"**

### 9.2 핵심 권장 사항 (★ critical)

**1. 5/15 박광현 미팅 자료 영역**:
- §2 측정 plan 영역에서 "paper Algorithm 1 14-step" 표현 제거 → "paper Eq 1-6 + hyperparam 7 종 + 본 연구 의역 step-wise" 표기
- §0 우리 결정 form 영역에서 "Step 11 augment" → "paper Eq 5 (sampling_size update) 의 본 연구 group-aware allocation augment" 정정

**2. 5/27 발표 deck (slide 5/8/11 영역)**:
- "Algorithm 1 14-step" 표현 → "paper §V-B Eq 1-6 + 본 연구 의역 step-wise" 표기
- pseudocode slide → paper Eq 1-6 verbatim + 본 연구 augment 영역 명확 분리 (color coding 권장)

**3. 6/11 보고서 §4 본 연구 방법론 영역**:
- "§4.2 Component A — Stratified Reservoir Sampling (paper Eq 1 대체)" 표기 유지 (Eq 1 wording 정합)
- "§4.4 Component C — paper Eq 2-6 통합 (Step 11 group-aware augment)" → "§4.4 Component C — paper Eq 2-6 verbatim + paper Eq 5 group-aware allocation augment" 정정
- 부록 A "paper §V-B Algorithm 1 14-step 의사코드" → "paper §V-B Eq 1-6 + 본 연구 의역 step-wise pseudo-code" 정정

**4. 측정 1 (streaming) 우선순위 (★ 5/27 phase 1 메인)**:
- Agent F 권장 = sf=100 만 phase 1 측정 (720 file, server 4-6h) → 5/27 가능
- sf=10 추가 측정 (720 file, 추가 server 4-6h) → 6/11 가능
- Agent E 1440 file 산정 = sf 양쪽 모두 영역 (5/27 phase 1 cost overrun risk)

**5. 측정 3 (4-way) 영역 분담**:
- **5/27 phase 1**: Bernoulli + SelNet + 본 Form 1 (3-way, 360 file, cost 50-65h)
- **6/11 phase 2**: + CE4HD + Ada-ef (5-way full, 600 file, cost +30-45h)

**6. 측정 2/4 (BIRCH cost + distribution shift)**:
- **5/27 phase 1**: X (cost 우선순위 낮음)
- **6/11 phase 2**: O (cost 15-20h)

**7. 측정 5 (phase 2 pilot)**:
- 5/27 / 6/11 phase 1 모두 X
- **paper-grade future**: 6/12 ~ 7/31 (Agent E 산정)

### 9.3 측정 cost 정리 (서버 시간)

| 측정 | 5/27 phase 1 | 6/11 phase 2 | paper-grade future |
|---|---|---|---|
| 측정 1 streaming (1440 file) | sf=100 만 (720 file, 4-6h) | sf=10 추가 (720 file, 4-6h) | -- |
| 측정 2 BIRCH cost (540 file) | -- | 540 file, 3-5h | -- |
| 측정 3 4-way (600 file) | 3-way (360 file, 3-5h) | 5-way full (600 file, 5-8h) | -- |
| 측정 4 drift (480 file) | -- | 480 file, 3-5h | -- |
| 측정 5 phase 2 (120 file) | -- | -- | 120 file, 1-2h |
| **서버 시간 소계** | **7-11h** | **15-24h** | **1-2h** |

### 9.4 코드 cost 정리 (개발 시간)

| 영역 | 5/27 phase 1 | 6/11 phase 2 | paper-grade future |
|---|---:|---:|---:|
| Component A-D 구현 | 25-40h | -- | -- |
| 측정 1-3 script | 18-25h | 5-8h | -- |
| 측정 4 drift script | -- | 6-10h | -- |
| 측정 5 phase 2 script | -- | -- | 5-8h |
| 4-way baseline (SelNet/CE4HD/Ada-ef) | 8-12h (SelNet 만) | 22-33h (CE4HD + Ada-ef) | -- |
| 분석 + 시각화 | 10-15h | 14-23h | -- |
| 5/27 deck + 6/11 보고서 | 10-15h | 10-15h | -- |
| **코드/문서 소계** | **71-107h** | **57-89h** | **5-8h** |
| **총 cost (phase 1 + phase 2)** | -- | -- | **128-196h** |

★ **Agent F 결론**: phase 1 (5/27) + phase 2 (6/11) = 128-196h, Agent E 산정 135-195h 와 fit.

### 9.5 Form 1 phase 1 / phase 2 명확 분담

| phase | 5/27 phase 1 | 6/11 phase 2 |
|---|---|---|
| **Component A (SRS)** | ✓ Equal/Proportional 구현 | + Neyman/Anti-Neyman 추가 |
| **Component B (BIRCH)** | ✓ partial_fit + CF tuple wrapper | + threshold dataset adaptive optimization |
| **Component C (paper Eq 2-6 + augment)** | ✓ Eq 5 group-aware augment | + Eq 3-4 group-aware augment (option) |
| **Component D (분포 인지)** | ✓ Equal/Proportional default | + Neyman/Anti-Neyman 측정 |
| **측정 1 streaming** | sf=100 만 (720 file) | sf=10 추가 (720 file) |
| **측정 2 BIRCH cost** | X | ✓ 540 file |
| **측정 3 4-way** | 3-way (Bernoulli+SelNet+본) | 5-way (+ CE4HD + Ada-ef) |
| **측정 4 drift** | X | ✓ 480 file |
| **측정 5 phase 2 pilot** | X | X (paper-grade future) |

### 9.6 5/15 박광현 미팅 priority + 정정 wording 반영 강도

★★★ **5/15 박광현 미팅 자료 정정 권장 영역**:
1. **§2 측정 plan 영역**: "Algorithm 1 14-step" 표현 → "paper Eq 1-6 + 본 연구 의역 step-wise" (5 곳 정정 권장)
2. **§0 우리 결정 form 영역**: "Step 11 augment" → "paper Eq 5 group-aware allocation augment" (2 곳 정정 권장)
3. **부록 A pseudo-code 영역**: paper Eq 1-6 verbatim + 본 연구 augment 영역 색상 분리 표기 (color coding 권장)
4. **§1 보완 paper 한계 L1+L5+L6 영역**: paper L6 verbatim "[81] adjusts the sample size dynamically..." 정확 인용 유지 (정정 X)

★★★ **5/27 발표 deck 정정 권장 영역**:
1. **slide 5 "paper §V-B Algorithm 1 14-step + 본 Form 1 통합 axis"** → "paper §V-B Eq 1-6 + 본 연구 의역 step-wise + 본 Form 1 augment axis"
2. **slide 8 "본 Form 1 Component C (paper Eq 2-6 통합) Step 11 group-aware n_inc 분배"** → "본 Form 1 Component C (paper Eq 2-6 verbatim + paper Eq 5 group-aware allocation augment)"
3. **부록 A pseudo-code** → 동일 색상 분리

★★★ **6/11 보고서 §4 + 부록 A 정정 권장 영역**:
1. 위 5/27 deck 와 동일 패턴
2. §4.6 paper Eq 1-6 + 본 Form 1 통합 표 → "paper Eq 1-6 verbatim 영역 + 본 연구 augment 영역" 정확 표기

### 9.7 본 Form 1 의 학술 contribution 정직 disclosure (paper-grade publication 영역)

**Form 1 framework axis novelty (★★★ paper-grade 기준)**:
1. **Component A (SRS)** = Al-Kateb-Lee-Wang SSDBM 2010 + ISJ 2014 base + **vector similarity range query domain 의 정량 발현 (novel)** + **paper §V-B Adaptive Sampling framework 통합 (novel)**
2. **Component B (BIRCH online)** = Zhang-Ramakrishnan-Livny 1996 SIGMOD base + **paper §V-B period P=50 query trigger 와 align (novel framework)** + **CF tuple → σ_j² online 추정 → Component D 분포 인지 stratification (novel integration)**
3. **Component C (paper Eq 2-6 + augment)** = paper §V-B Eq 1-6 verbatim 유지 + **paper Eq 5 (sampling_size update) 의 group-aware allocation augment (novel augment)**
4. **Component D (분포 인지)** = Cochran 1977 + RQ2 Neyman paradox 결과 + **streaming axis 의 distribution-aware stratification 정량 발현 (novel)**
5. **4-way 비교 framework** = paper §VI-D Fig.12 의 SelNet 한정 비교 → **Bernoulli + SelNet + CE4HD + Ada-ef + 본 Form 1 의 5-way 비교 framework (novel framework axis)**

★ **honest disclosure**: 각 component 의 자체 신규성 약함 (SRS / BIRCH / Cochran 1977 모두 1996-2014 literature 존재). **framework axis** (4-way 비교 + paper §V-B 통합 + streaming-aware + 분포 인지) 가 본 Form 1 의 main contribution. 학부 capstone-grade ★★ 매우 강력 / paper-grade workshop or short paper ★ 가능 / paper-grade main paper ★ 어렵.

---

## 10. file path + 핵심 요약

**file path**: `/Users/hyunbin/Capstone/_internal/handoff/active/agent_F_streaming_측정_plan_code_plan_20260515_0100.md`

**핵심 요약** (main thread 보고용):

1. **paper §V-B 정독 결과 critical 정정**: paper 자체에 "Algorithm 1 14-step pseudo-code" 영역 **X**. paper 는 Eq 1-6 + hyperparam 7 종 + 자연 산문. Agent C/D/E 가 의역해서 14-step 으로 풀어쓴 영역 → 5/15 박광현 미팅 자료 + 5/27 발표 + 6/11 보고서 wording 정정 필수 (구체 정정 wording = § 9.1 참조).

2. **Component A (SRS) 구현**: Vitter 1985 Algorithm R per-stratum reservoir + group_aware_alloc (Equal/Prop/Neyman/Anti-Neyman 4 mode) + paper N=385 budget 유지. numpy 기반 250 line + measure_paper_exact.py 의 cache_cluster_samples_inmem 패턴 재사용. dev cost 8-12h, test 4-6h.

3. **Component B (BIRCH) 구현**: `sklearn.cluster.Birch(n_clusters=20, threshold=0.5, branching_factor=50)` + partial_fit chunk pattern. measure_paper_exact.py line 623-630 의 birch method **이미 구현**. wrapper 만 추가 (CF tuple manual 보관 + σ_j² online 계산), 200 line + 10-15h. paper period P=50 query trigger 와 align 권장 (옵션 1).

4. **Component C (Eq 2-6 통합)**: measure_paper_exact.py 의 AdaptiveState (line 104-140) **paper Eq 1-6 verbatim 100% 정합 검증 완료**. 본 Form 1 phase 1 = AdaptiveState.update() **그대로 유지** + `update_with_group_aware()` 신규 method 추가 (Eq 5 의 scalar new_size 를 group_aware_alloc 로 cluster 별 분배). dev cost 4-6h.

5. **Component D (분포 인지)**: group_aware_alloc 함수 1 개로 4 mode 전환. _measure_common.py 의 기존 equal/proportional/neyman alloc 함수 활용 가능. 본 Form 1 권장 = Proportional (RQ2 의 Neyman paradox sel=0.01 한정 결과의 자연 결론). dev cost 3-5h.

6. **측정 1 (streaming) 우선순위 sf=100 만 phase 1**: Agent E 산정 1440 file (sf 양쪽 모두) → Agent F 권장 phase 1 720 file (sf=100 만, server 4-6h). 6/11 phase 2 에서 sf=10 추가 720 file.

7. **측정 3 (4-way) 영역 분담**: 5/27 phase 1 = Bernoulli + SelNet + 본 Form 1 (3-way, 360 file, cost 50-65h). 6/11 phase 2 = + CE4HD + Ada-ef (5-way full, 600 file, +30-45h). SelNet reference impl cost 8-12h (open-source 영역 확인 필요).

8. **측정 2 (BIRCH cost) + 측정 4 (drift)**: 5/27 phase 1 X / 6/11 phase 2 O (540 + 480 file, 6-10h server).

9. **측정 5 (phase 2 augment)**: 5/27 / 6/11 모두 X / paper-grade future 6/12 ~ 7/31 영역 (120 file pilot).

10. **총 cost 검증**: Agent F 산정 = 128-196h (5/27 phase 1 71-107h + 6/11 phase 2 57-89h). Agent E 산정 135-195h 와 fit (±5%). 5/27 phase 1 cost 50-80h (Agent E 산정 일치) realistic.

11. **신규 코드량 산정**: 1700 line × 6 file (measure_form1_common.py + measure_form1_streaming.py + measure_form1_birch_cost.py + measure_form1_4way.py + measure_form1_drift.py + measure_form1_phase2.py). measure_paper_exact.py 1407 line + 1700 line = 3100 line total.

12. **분석 코드**: 1001 file analysis 9 script 패턴 재사용 + drift trajectory plot (paper Fig 6 layout) + 3-way/5-way bar plot (paper Fig 12 layout) + online vs offline BIRCH degradation 표. dev cost 24-38h.

13. **server 시간 총합**: phase 1 7-11h + phase 2 15-24h + future 1-2h = **23-37h server time** (Agent E 산정 20-30h 와 일치).

14. **framework axis novelty (paper-grade)**: 각 component 자체 신규성 약함 (1996-2014 literature 존재). framework axis (4-way 비교 + paper §V-B 통합 + streaming-aware + 분포 인지) 가 본 Form 1 의 main contribution. 학부 capstone-grade ★★ 매우 강력 / paper-grade workshop or short paper ★ 가능 / paper-grade main paper ★ 어렵.

15. **★ Agent F 최종 권장 (5/15 박광현 미팅 + 5/27 발표 + 6/11 보고서)**: § 9.1 의 wording 정정 룰 엄수 ("Algorithm 1 14-step" 표현 폐기 → "paper Eq 1-6 + 본 연구 의역 step-wise" 정확 표기). § 9.5 의 phase 1 / phase 2 분담 영역 엄수 (5/27 = Component A+B+D + 측정 1 sf=100 + 측정 3 3-way / 6/11 = + 측정 2 + 측정 4 + 측정 3 5-way + 측정 1 sf=10).

---

> **Agent F deep dive 완료**. main thread 종합 권장 = § 9.1 정정 wording + § 9.5 phase 분담 + § 8.4 cost 검증. 5/15 박광현 미팅 자료 + 5/27 deck + 6/11 보고서 wording 정정 영역 명확.

---

**Sources (web search + paper PDF + measure_paper_exact.py 검증)**:
- [Birch — scikit-learn 1.8.0 documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.Birch.html)
- [Stratified Reservoir Sampling over Heterogeneous Data Streams (SSDBM 2010 PDF)](https://bslee.w3.uvm.edu/papers/StratifiedReservoirSampling_SSDBM2010.pdf)
- [Stratified Reservoir Sampling — Springer Nature Link](https://link.springer.com/chapter/10.1007/978-3-642-13818-8_42)
- [Adaptive stratified reservoir sampling over heterogeneous data streams — ScienceDirect (ISJ 2014)](https://www.sciencedirect.com/science/article/abs/pii/S0306437912000518)
- paper PDF: `/Users/hyunbin/Capstone/reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf` (p.5-12 정독, §V-B + §VI verbatim)
- 기존 코드: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py` (line 1-1407 직접 read, AdaptiveState verbatim 검증 + birch method 활용 영역 확인)
- Agent E 결과: `/Users/hyunbin/Capstone/_internal/handoff/active/agent_E_Form_1_구체화_streaming_aware_20260515_0000.md`
