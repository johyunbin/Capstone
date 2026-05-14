# Paradigm P3 Streaming — 7 method 알고리즘 검증

작성: 2026-05-10 KST · 검증자: P3 verification 세션 (Claude Opus 4.7 1M)
검증 대상: `_internal/scripts/measure_paper_exact.py:_get_method_strata()` + `experiments/code/rq3/kde/kde_pilot.py`
원전 cross-check: paper / handoff_v2 / V7 audit (`_internal/archive/2026_05_09_audit_archive/audit_method_correctness_20260508.md`)

---

## TL;DR

- **알고리즘 충실도 평균: 4.0 / 10** — 7 method 중 4 method가 naming misrepresentation 또는 KM20 leak 의심.
- **Critical naming misrepresentation 4건** (severity = critical, 보고서/논문 표기 즉시 정정 필요):
  1. `reservoir` — `rng.integers(0, n_strata, size=N)` 단순 random partition. **이는 Vitter 1985 reservoir sampling이 아니라 RANDOM20과 동일한 균등 random label.** V7 audit (5/8) 에서도 동일 finding 보고됨.
  2. `thompson_sampling` — Thompson posterior sampling 코드 X. 단순 MiniBatchKMeans 호출 후 cluster 결과를 stratum_id로 사용. Beta(1,1) prior 주석만 있고 실제 posterior 는 미적용. 즉 이 method는 P1 cluster (MiniBatch) 의 single-init 변종일 뿐.
  3. `lpm2` — Grafström 2012 Local Pivotal Method (auxiliary variable 기반 inclusion probability balancing) 와 완전히 다른 알고리즘. 본 구현은 Weiszfeld geometric median + radial distance quantile bin 으로, 학술적으로 distance-shell stratifier에 가까움.
  4. `mfmc` — Multi-Fidelity Monte Carlo (Peherstorfer et al. 2018 control-variate based estimator) 와 다른 알고리즘. 본 구현은 KMeans primary + random reservoir 의 50:50 binary mask 보간 hybrid 로, MFMC 의 fidelity hierarchy + control variate 구조 자체가 부재.

- **kde_pilot KM20 leak 확정**: `experiments/code/rq3/kde/kde_pilot.py:93-105` 에서 PG 테이블의 `stratum_id` column 을 직접 SELECT 함. 이 column 은 `_internal/scripts/prepare_cell.py:110-136` 에서 KMeans20 결과로 미리 채워짐. 따라서 kde_pilot은 KM20 cluster 위에서 동작 — V7 audit (§6) "kde_pilot KM20 cluster leak — 제외 정당" 와 일치. **데이터 누설 의혹 확정. RQ3 method 비교에 포함 시 invalid.**

- **즉시 조치 (priority 순)**:
  1. **`reservoir` 표기 정정** → "RANDOM20 (Reservoir proxy)" 또는 "Random Partition Baseline" 으로 변경. V7 audit + handoff_v1 에서 이미 인정된 사실. paper-style 보고서/슬라이드에 "Vitter 1985 reservoir sampling" 으로 인용 시 학술 misrepresentation 위험.
  2. **`thompson_sampling`, `lpm2`, `mfmc` 3건 표기 변경**: naming 정합성 audit. 만약 보고서에서 Thompson 1933 / Grafström 2012 / Peherstorfer 2018 인용 중이면 즉시 제거하거나 "name-only proxy" 명시.
  3. **`kde_pilot` 결과는 RQ3 paradigm 비교에서 제외** (V7 audit 결정 유지). 보고서에 등장 시 KM20 leak 명시.

- **Algorithm-correct 1.5건만 정상**: `minibatch_partial` (★2 4강) 은 ✓ Sculley 2010 + sklearn `partial_fit` 정통. `adaptive_bucket_probing` 은 학술 reference (Sigl & Strehl 2016) 와 다르나 implementation 자체는 mathematically valid (PCA1D quantile bin) — naming만 정정하면 OK.

---

## 1. minibatch_partial (★2 4강)

### 원전

* **Reference**: Sculley, "Web-Scale K-Means Clustering" (WWW 2010) + sklearn `MiniBatchKMeans.partial_fit` API
* **Algorithm 정의**:
  - Streaming centroid update: 매 mini-batch B_t 도착 시 centroid c_k 를 `c_k ← (1 − η_t) c_k + η_t · mean(B_t ∩ cluster k)` 로 incremental update
  - `partial_fit` API: warm-up `fit(initial_chunk)` 후 sequential `partial_fit(next_chunk)` 호출. internal counter 가 streaming sample count 누적, learning rate `η_t = 1/n_count` 로 자동 감쇠
  - Sculley 2010 의 "Web-Scale" 핵심: streaming + bounded memory + production OLTP-friendly

### 구현 위치

* **파일**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:460-468`
* **코드**:
  ```python
  if method_name == "minibatch_partial":
      # Streaming chunked minibatch — partial_fit 패턴
      from sklearn.cluster import MiniBatchKMeans
      km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=4096, n_init=1)
      # chunk 단위 partial_fit
      chunk = 100_000
      for i in range(0, len(all_vecs), chunk):
          km.partial_fit(all_vecs[i:i+chunk])
      return km.predict(all_vecs).astype(np.int32)
  ```
* **V7 audit 동일 method 별도 파일** (`cache/rq3/offline_simple/minibatch_partial.py`, 229 L): warm-up + drift summary 까지 측정. 본 paper_exact 구현은 server side production 코드의 simplified 버전.

### 알고리즘 충실도: 8/10

| 기준 | 평가 | 비고 |
|---|---|---|
| Sculley 2010 streaming centroid update | ✓ | sklearn 내부에 그대로 반영 |
| `partial_fit` API 사용 | ✓ | line 467 `km.partial_fit(all_vecs[i:i+chunk])` 정확 호출 |
| Sequential chunk 처리 | ✓ | chunk=100_000 으로 N=1M~8M dataset 을 10~80개 chunk 로 분할 |
| Warm-up `fit()` 부재 | ⚠️ | sklearn `partial_fit` 은 첫 호출 시 자동 init 하나, V7 audit 의 production code 는 명시적 `fit(samples[:warmup])` 으로 cold-start variance 완화. 본 구현은 첫 chunk 자체가 warm-up 역할이라 statistically OK 하나 reproducibility 약화 |
| `n_init=1` | △ | MiniBatchKMeans default `n_init=3` (multiple init 후 best 선택). `n_init=1` 으로 한 번만 init → cold-start variance 가능. minor |
| `predict(all_vecs)` 으로 hard assignment | ✓ | streaming partition 의 표준 wrap-up |

### Streaming 환경 가정 적합성

* **이론적 정합성**: ✓ — Sculley 2010 의 web-scale 원전과 일치. 단일 pass + bounded centroid memory.
* **실제 환경 mismatch**: 본 RQ3 measurement 는 batch 환경. `all_vecs` 가 in-memory N×D float32 array로 fully loaded → "streaming protocol 흉내" 일 뿐 진짜 streaming 입력 X. 이는 V7 audit 의 narrative ("partial_fit 의 *streaming protocol* 이 본질") 에서도 인정된 한계. 측정 결과 자체는 valid 하나, paper 에 "We measure streaming behavior" 로 작성 시 reviewer challenge 가능.
* **권고**: narrative 에 "we simulate streaming arrival via chunked `partial_fit` calls; the underlying data is in-memory but the centroid update protocol matches Sculley 2010 streaming variant" 로 명시.

### hyperparam 적정성

| Hyperparam | 값 | 평가 |
|---|---|---|
| `batch_size` | 4096 | ✓ sklearn default 1024 보다 4× 큼. N=1M~8M 에서 chunk 단위 stable update OK |
| `chunk` (외부 loop) | 100_000 | ✓ 1M = 10 chunk, 8M = 80 chunk. memory budget OK |
| `n_init` | 1 | ⚠️ default 3 보다 작음. 단일 cold-start. Sculley original 은 `n_init` 개념 없음 (streaming 이라 single pass) — 정합성 OK |
| `random_state=seed` | propagated | ✓ reproducibility 보장 |

### n_strata=20 매핑 정당성

* `n_clusters=n_strata=20` 직접 KMeans cluster 수로 사용. 추가 mod 또는 hash collision 없음. ✓

### 결함 list

| Severity | 결함 | 권고 |
|---|---|---|
| Minor | `n_init=1` 로 cold-start variance 가능 | `n_init=3` 또는 multiple seed 평균 |
| Minor | warm-up `fit()` 부재로 첫 chunk 가 init 역할 (cold-start centroid 가 final partition 영향) | 명시적 warm-up `fit(all_vecs[:warmup_size])` 추가 |
| Cosmetic | "streaming" naming 이 실제 batch in-memory 환경과 mismatch | narrative 에 "streaming protocol simulation" 으로 한정 |

### 종합

* **결론**: ✅ 알고리즘 정합성 정통. ★2 4강 후보로서 paradigm representative 자격 충분.
* **유일 우려**: narrative 에서 "streaming environment" 라는 강한 statement 만 약화하면 됨.

---

## 2. reservoir

### 원전 (Vitter 1985 Algorithm R)

* **Reference**: Vitter, "Random Sampling with a Reservoir" (TOMS 1985) — Algorithm R
* **진짜 reservoir sampling**:
  ```
  Initialize: reservoir[0..k-1] ← stream[0..k-1]
  For i = k, k+1, ..., N-1:
      j ← uniform(0, i)
      If j < k:
          reservoir[j] ← stream[i]
  ```
* **결과**: stream의 N elements 중 uniform random k-subset 보장. Single-pass + O(k) memory + 통계적 unbiased.

### 구현 vs 원전

* **파일**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:500-503`
* **코드**:
  ```python
  if method_name == "reservoir":
      # Reservoir sampling stratification — random 20-way partition (control)
      rng_r = np.random.default_rng(seed)
      return rng_r.integers(0, n_strata, size=len(all_vecs), dtype=np.int32)
  ```
* **분석**: `rng_r.integers(0, n_strata, size=N)` 는 N 개 row 각각에 0~19 균등 random label 부여. 이는:
  - Vitter Algorithm R의 single-pass selection logic 부재
  - `j < k` swap rule 부재
  - Stream 진행에 따른 inclusion probability decay (k/i) 부재
  - 단순히 `floor(uniform[0,1) * 20)` per row → **이는 Vitter reservoir 가 아니라 RANDOM20 (uniform random partition)** 과 동일

### V7 audit 일치 (5/8 archived)

```
파일: _internal/archive/2026_05_09_audit_archive/audit_method_correctness_20260508.md
line 43: "Reservoir (single cell run_reservoir.py): 구현이
  rng.integers(0, n_strata, size=n_rows) 으로 단순 random partition —
  이는 Vitter Algorithm R 가 아니라 RANDOM20 과 동일.
  코드 docstring 도 'random20 와 같은 알고리즘이지만 다른 seed' 로 인정."
line 61: "Reservoir single-cell vs multi-cell 알고리즘 불일치 —
  single 은 RANDOM20 proxy, multi 는 Vitter K-subset."
```

### CRITICAL DEFECT (severity = critical)

* **naming misrepresentation**: 보고서 / 논문 / 슬라이드에서 "Reservoir" 또는 "Vitter 1985" 인용 시:
  - 학술 reviewer가 진짜 Vitter Algorithm R 으로 오해 → method comparison validity 의심
  - 사실상 측정한 것은 "stratification 없는 baseline" 인데 paradigm representative 로 표기 시 paradigm framework narrative 자체가 깨짐
* **실험 결과 해석**: reservoir 가 다른 stratification method 보다 약간 다른 Δ%를 보이면, 그것은 알고리즘 차이가 아니라 **단순히 다른 random seed**. RANDOM20 과 통계적 동치.

### 권고 (priority 순)

1. **즉시**: 보고서 / 슬라이드 / 발표자료에서 "Reservoir" 표기를 다음 중 하나로 변경:
   - "RANDOM20 (Reservoir proxy)" — V7 audit 권고 표기
   - "Random Partition Baseline" — 알고리즘 그대로 명시
   - "RANDOM20 (seed=42)" — 다른 seed 의 RANDOM20 으로 표기
2. **근본 fix**: 진짜 streaming Vitter implementation 으로 교체:
   ```python
   # Vitter Algorithm R — chunk-streamed K-subset
   reservoir = []
   sids = np.full(len(all_vecs), -1, dtype=np.int32)
   for sid in range(n_strata):
       # k = 1 element per stratum (centroid candidate)
       # streaming through all_vecs ...
   # 그 후 nearest-centroid assignment for full N
   ```
   V7 audit의 multi-cell 변종 `_fit_reservoir` (`measure_multi_paradigm.py`) 는 이미 `rng.choice(n, size=n_strata, replace=False)` + nearest-centroid 로 batch 동치 form을 구현. 이를 single-cell paper_exact 에 backport 권장.
3. **narrative 정정**: master report / outline_v2 §6 L11 정정 (V7 audit 5/8 에서 master_v6 §10.7 + outline v2 §6 L11 정정 완료라고 명시). 본 paper_exact registry 도 동일하게 정정 필요.

### 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | naming misrepresentation — Vitter 1985 algorithm 아님, RANDOM20 |
| Critical | 진짜 streaming reservoir 의 single-pass selection logic 자체가 부재 |
| Moderate | seed 만 다른 RANDOM20 duplicate 라서 실험 정보량 0 |

---

## 3. thompson_sampling

### 원전 (Thompson 1933)

* **Reference**: Thompson, "On the likelihood that one unknown probability exceeds another in view of the evidence of two samples" (Biometrika 1933)
* **진짜 Thompson sampling** (Beta-Bernoulli case):
  ```
  For each arm a ∈ {1, ..., K}:
      Posterior(p_a) ~ Beta(α_a + S_a, β_a + F_a)
      where S_a = successes, F_a = failures observed
  Sample p̂_a from posterior
  Choose a* = argmax_a p̂_a
  Update: pull a*, observe reward, update α_{a*} or β_{a*}
  ```
* **핵심**: posterior distribution sampling + sequential decision. Beta(1,1) prior 는 단순히 시작점 (uniform).

### 구현 vs 원전

* **파일**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:657-664`
* **코드**:
  ```python
  if method_name == "thompson_sampling":
      # Beta-Bernoulli posterior sample — random with prior
      rng_d = np.random.default_rng(seed)
      # KMeans 기반 cluster + Thompson posterior (prior=Beta(1,1))
      from sklearn.cluster import MiniBatchKMeans
      km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=4096)
      km.fit(all_vecs)
      return km.predict(all_vecs).astype(np.int32)
  ```
* **분석**:
  - 주석 (`# Beta-Bernoulli posterior sample — random with prior`) 은 Thompson 의도를 표명
  - 그러나 실제 코드:
    - `rng_d = np.random.default_rng(seed)` → 만들기만 하고 사용 X
    - `MiniBatchKMeans.fit(all_vecs).predict(all_vecs)` → **단순 KMeans clustering**
    - Beta posterior sampling 코드 없음
    - α, β counter 없음
    - reward / failure update loop 없음
    - argmax_a posterior sample 없음
  - **이것은 Thompson sampling 이 아니라 P1 cluster (MiniBatchKMeans) 의 single-init 변종.**

### CRITICAL DEFECT (severity = critical)

* **naming misrepresentation**: Thompson 1933 인용 시:
  - Bandit literature에서 Thompson sampling은 well-defined posterior sampling algorithm. 본 method 와 무관.
  - 학술 reviewer가 "How is Thompson posterior used for stratification?" 질문 시 답변 불가
  - 결과적으로 P1 (cluster-based) 의 redundant copy → paradigm framework 위배

* **MiniBatchKMeans와 비교**:
  ```python
  # paper_exact line 432-436 (minibatch)
  km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=1024, n_init=3)
  km.fit(all_vecs)
  return km.predict(all_vecs).astype(np.int32)

  # paper_exact line 660-664 (thompson_sampling)
  km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=4096)
  km.fit(all_vecs)
  return km.predict(all_vecs).astype(np.int32)
  ```
  차이: `batch_size` (1024 vs 4096), `n_init` (3 vs default=3) 만 다름. **알고리즘 본질 동일** — 통계적으로 minibatch 와 ARI ≈ 1.0 예상.

### 권고

1. **즉시**: thompson_sampling 의 표기를 다음 중 하나로 변경:
   - "MiniBatchKMeans (batch=4096)" — 사실 그대로
   - "P1 redundant" 표시 후 RQ3 7-way 비교에서 제외
   - 또는 진짜 Thompson posterior 구현으로 교체 (어렵고, RQ3 stratification 와 architectural mismatch)
2. **manuscript 정정**: 만약 발표 / 보고서 / 논문에서 "Thompson 1933" 또는 "posterior sampling" 인용 중이면 즉시 제거.
3. **결과 해석**: thompson_sampling Δ% 가 minibatch Δ% 와 거의 동일하면 (ARI ~ 1.0 예상), 이는 method 차이가 아니라 hyperparameter 차이. 결과 reporting 시 별도 entry 가 아닌 minibatch (variant) 로 합치 권장.

### 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | naming misrepresentation — Thompson posterior sampling 코드 없음 |
| Critical | `rng_d` 변수 만들고 사용 X (dead code) |
| Critical | P1 (MiniBatchKMeans) 의 hyperparameter variant 일 뿐 — paradigm independent representative 아님 |
| Moderate | bandit literature와 architectural mismatch (sequential decision X, stratum partition O) |

---

## 4. mfmc (Multi-Fidelity Monte Carlo)

### 원전 (Peherstorfer et al. 2018)

* **Reference**: Peherstorfer-Willcox-Gunzburger, "Survey of Multifidelity Methods in Uncertainty Propagation, Inference, and Optimization" (SIAM Review 2018) — 또는 그 이전 origin Giles 2008 (Multilevel MC)
* **진짜 MFMC algorithm**:
  ```
  Models: f_1 (high fidelity, expensive), f_2, ..., f_K (low fidelity, cheap)
  Estimator: μ_MFMC = m_1·E[f_1] + Σ_{k=2}^K α_k · (E[f_k] − E[f_k|x_low])
  where α_k = optimal control variate coefficient (cov(f_1, f_k) / var(f_k))
  Sample budget: optimize n_k subject to total cost
  ```
* **핵심**: control variate + fidelity hierarchy + variance reduction via correlation

### 구현 vs 원전

* **파일**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:666-676`
* **코드**:
  ```python
  if method_name == "mfmc":
      # Multi-Fidelity MC — KMeans (high) + reservoir (low) 결합
      from sklearn.cluster import MiniBatchKMeans
      km = MiniBatchKMeans(n_clusters=n_strata, random_state=seed, batch_size=4096)
      km.fit(all_vecs[: min(len(all_vecs), 50_000)])
      primary = km.predict(all_vecs)
      rng_d = np.random.default_rng(seed + 1)
      reservoir = rng_d.integers(0, n_strata, size=len(all_vecs))
      # Hybrid: 50% primary + 50% reservoir
      mask = rng_d.random(len(all_vecs)) < 0.5
      return np.where(mask, primary, reservoir).astype(np.int32)
  ```
* **분석**:
  - 주석 ("KMeans (high) + reservoir (low) 결합") 은 fidelity hierarchy 를 흉내내는 의도 표명
  - 그러나 실제 구현:
    - Control variate 계수 α_k 계산 X
    - Covariance / variance estimate X
    - Cost-aware budget allocation X
    - 단순히 binary mask 50:50 으로 KMeans 또는 reservoir 결과 random switch
  - **이것은 MFMC 가 아니라 KMeans + RANDOM20 의 row-level binary mixture.**

### CRITICAL DEFECT (severity = critical)

* **naming misrepresentation**: Peherstorfer 2018 또는 MFMC literature 인용 시:
  - Control variate coefficient α 가 알고리즘의 핵심 — 그것이 없으면 MFMC 가 아님
  - Variance reduction 효과 자체가 control variate 에서 나오는데 본 구현은 그것 없이 단순 mixture → variance 감소 없음, 오히려 variance 증가 가능
  - 학술 reviewer 가 "How does the mixture coefficient relate to the variance ratio between high/low fidelity?" 질문 시 답변 불가
* **실제 알고리즘 정체**: `KMeans + RANDOM20` 의 binary mixture. 50% 의 row 는 KMeans cluster 가 부여되고 50% 의 row 는 random label. 이는 KMeans cluster 의 50% noise injection 으로 stratum quality 약화 효과만 있을 뿐 fidelity hierarchy 와 무관.

### 권고

1. **즉시**: mfmc 의 표기를 변경:
   - "KMeans + RANDOM20 mixture (50:50)" — 사실 그대로
   - 또는 "P1 + control" hybrid 로 reframe (단 학술 reference 없이)
2. **manuscript 정정**: Peherstorfer 2018 또는 Multi-Fidelity 인용 즉시 제거.
3. **paradigm 정체성**: P3 streaming 이 아니라 **P1 + RANDOM 의 ad-hoc mixture**. P3 representative 자격 X.

### 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | naming misrepresentation — MFMC 의 control variate 부재 |
| Critical | Cost-aware budget allocation 없음 |
| Critical | Fidelity hierarchy 자체가 아키텍처 부재 (KMeans 와 reservoir 가 fidelity 가 아님 — 둘 다 같은 stratification cost) |
| Moderate | P3 streaming paradigm 정체성 부재 — KMeans 는 batch, reservoir 는 partition. 둘 다 streaming 아님 |
| Moderate | binary mask 가 reproducibility 약화 (`rng_d.random()` 의 50% threshold) |

---

## 5. adaptive_bucket_probing

### 원전

* **Reference**: 사용자 task description 에 "Sigl & Strehl 2016?" 로 의문부호. Adaptive histogram literature 의 standard reference 는:
  - Aboulnaga & Chaudhuri, "Self-tuning histograms" (SIGMOD 1999)
  - Sigl & Strehl 2016 은 DB literature 에서 standard 한 paper 가 아님 (verifiable reference 부재)
* **Adaptive histogram의 핵심** (어떤 reference 든):
  - Bucket boundaries 가 *data-adaptive* — 단순 quantile 이 아닌 query workload feedback 기반 update
  - Online refinement: query 결과 (residual error) 에 따라 bucket split / merge
  - "Adaptive" 의 본질 = workload-aware feedback loop

### 구현 vs 원전

* **파일**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:716-725`
* **코드**:
  ```python
  if method_name == "adaptive_bucket_probing":
      # Variance-based adaptive binning on first PC
      from sklearn.decomposition import PCA
      pca = PCA(n_components=1, random_state=seed)
      proj = pca.fit_transform(all_vecs).flatten()
      # Density-aware quantile (bin proportional to variance)
      edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
      edges[-1] += 1e-6
      sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
      return np.clip(sids, 0, n_strata - 1)
  ```
* **분석**:
  - Workload feedback 없음
  - Online refinement loop 없음
  - 단순히 PCA 1D projection + uniform-quantile 20-way bin
  - **이는 PCA1D method 와 거의 동일** (paper_exact line 481-489 와 비교):
    ```python
    # pca1d:
    pca = PCA(n_components=1, random_state=seed)
    proj = pca.fit_transform(all_vecs).flatten()
    edges = np.quantile(proj, np.linspace(0, 1, n_strata + 1))
    edges[-1] += 1e-6
    sids = np.searchsorted(edges[1:-1], proj, side="right").astype(np.int32)
    return np.clip(sids, 0, n_strata - 1)
    ```
    완전히 같은 8-line 코드. 주석에 "Density-aware quantile (bin proportional to variance)" 라고 적혀 있으나 실제 quantile bin 은 uniform spacing 으로 variance-weighting 자체가 부재.

### MODERATE DEFECT (severity = moderate)

* **PCA1D duplicate**: adaptive_bucket_probing 결과 = PCA1D 결과. ARI ~ 1.0 예상.
* **naming misrepresentation (mild)**: "adaptive" 가 실제 algorithm 에 부재. 단 학술 standard reference 가 명확하지 않아 critical 보다는 moderate.

### 권고

1. **즉시**: paper_exact registry 에서 adaptive_bucket_probing 을 PCA1D 로 통합 또는 명시적 alias 처리.
2. **만약 RQ3 7-way 비교에서 별도 entry 로 보고 중이면**: PCA1D 와 redundancy 표시 필요.
3. **만약 adaptive_bucket_probing 이 "adaptive" property 를 가지길 원하면**: 진짜 workload feedback loop 추가 (query result residual 기반 bin split). 단 이는 large refactor.

### 결함 list

| Severity | 결함 |
|---|---|
| Moderate | PCA1D 와 algorithmically identical (variance-weighted 은 주석만, 코드는 uniform quantile) |
| Moderate | "adaptive" naming 이 실제 코드에 부재 (workload feedback 없음) |
| Minor | learn 단계 cost 가 PCA1D 와 동일 — paradigm-level 차별성 없음 |

---

## 6. lpm2 (Local Pivotal Method)

### 원전 (Grafström 2012)

* **Reference**: Grafström, "Spatially balanced sampling: Local Pivotal Method" (Journal of Statistical Planning and Inference 2012, 또는 Grafström & Tillé 2013 in Environmetrics)
* **진짜 LPM (Local Pivotal Method)**:
  ```
  Goal: Spatially balanced sample of size n from population N
  Inclusion probability π_i (auxiliary variable based)
  Iterate:
      Pick two units i, j with smallest pairwise distance
      Probabilistic decision:
        If π_i + π_j < 1: with prob π_j/(π_i+π_j), set π_i ← 0; else π_j ← 0
        Else: similar logic for the other side
      Continue until all π_i ∈ {0, 1}
  ```
* **핵심**: pairwise pivoting + auxiliary variable (e.g., spatial coords) 기반 inclusion probability balancing → spatial coverage 균등 보장.
* **LPM2 (Local Pivotal Method 2)**: `lpm2` 는 LPM 의 variant 로, pivoting unit 선정 시 nearest-neighbor 만 고려 (LPM1 은 모든 pair). 즉 **algorithmically nearest-neighbor based balancing**.

### 구현 vs 원전

* **파일**: `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py:837-850`
* **코드**:
  ```python
  if method_name == "lpm2":
      # Lp-Median (L2 Weiszfeld) — geometric median + radial bin
      sample = all_vecs[: min(len(all_vecs), 10_000)]
      # Approximate geometric median via Weiszfeld iter
      med = sample.mean(axis=0)
      for _ in range(10):
          d = np.linalg.norm(sample - med, axis=1) + 1e-9
          w = 1 / d
          med = (sample * w[:, None]).sum(axis=0) / w.sum()
      # Bin by distance from median
      dist = np.linalg.norm(all_vecs - med, axis=1)
      edges = np.quantile(dist, np.linspace(0, 1, n_strata + 1))
      edges[-1] += 1e-6
      return np.clip(np.searchsorted(edges[1:-1], dist, side="right"), 0, n_strata - 1).astype(np.int32)
  ```
* **분석**:
  - 코드 주석은 "Lp-Median (L2 Weiszfeld)" 으로 **이름 자체가 다른 알고리즘** (geometric median estimation via Weiszfeld 1937)
  - Pairwise pivoting 부재
  - Inclusion probability π_i 계산 없음
  - Probabilistic decision rule 없음
  - 실제 알고리즘:
    1. Weiszfeld iteration 으로 geometric median μ 추정
    2. 모든 vec 에 대해 `||v − μ||` 계산
    3. distance quantile 20-way bin
  - **이것은 LPM 이 아니라 distance-shell stratifier (radial bin)**.

### CRITICAL DEFECT (severity = critical)

* **naming misrepresentation**: 본 method 의 코드는:
  - Grafström 2012 LPM 의 spatial balancing logic 부재
  - Weiszfeld 1937 geometric median + radial quantile bin 으로 완전히 다른 알고리즘
  - 본질적으로 "distance from center" 기반 stratification (spherical shell)
* **distance_shell 와 redundancy**: V7 audit 에서 distance_shell 은 "5 paradigm 외" 로 제외됨. lpm2 는 distance_shell 의 variant (median-centered) — 학술적으로 **manuscript 에 lpm2 = distance_shell 으로 합치 또는 제외 권장**.

### 권고

1. **즉시**: lpm2 의 표기를 다음 중 하나로 변경:
   - "Geometric Median Radial Bin (Weiszfeld)" — 사실 그대로
   - "Distance-Shell (median-centered)" — V7 distance_shell 의 변종
   - 또는 RQ3 method 비교에서 제외 (V7 audit 의 distance_shell 와 동일 처리)
2. **manuscript 정정**: Grafström 2012 또는 LPM 인용 즉시 제거.
3. **paradigm 정체성**: P3 streaming 이 아니라 **P2 spatial 의 radial variant**. P2 와 redundancy 검토 필요.

### 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | naming misrepresentation — Grafström LPM 의 spatial balancing logic 부재 |
| Critical | Pairwise pivoting + inclusion probability 자체가 아키텍처 부재 |
| Critical | 실제 알고리즘은 distance-shell — V7 에서 "5 paradigm 외" 로 제외된 것과 동일 |
| Moderate | sample size 10_000 cap (Weiszfeld 가 N=1M 에서 expensive) — N=1.5M~8M 의 large dataset 에서 median estimate variance 증가 |
| Minor | Weiszfeld iter 10 회로 충분한가 (default convergence threshold 부재) |

---

## 7. kde_pilot

### 원전

* **Reference**: 사용자 task description "KDE-pilot estimator (Davies et al. 2018?)" 의문부호. KDE-pilot literature 의 standard reference:
  - Wasserman, "All of Nonparametric Statistics" (Springer 2006) §6 KDE
  - Silverman, "Density Estimation for Statistics and Data Analysis" (Chapman 1986)
  - Pilot bandwidth 는 Sheather-Jones 1991 또는 Silverman's rule
* **진짜 KDE-pilot**:
  ```
  Pilot phase: rough density estimate → adaptive bandwidth h_i = c · n_i^{-1/5}
  Main phase: weighted kernel sum with adaptive bandwidth
  ```
* **본 연구의 의도** (kde_pilot.py header 주석 line 5-17):
  - per query q with target distance D
  - Pilot: cluster i 마다 n_pilot sample → distance d_ij computation
  - Silverman bandwidth: `h_i = 1.06 × std(d_ij) × n_pilot^(-1/5)`
  - KDE-based hit probability: `p_i = (1/n_pilot) Σ_j Φ((D − d_ij) / h_i)`
  - Bernoulli σ estimate: `σ_i = sqrt(p_i × (1 − p_i))`
  - Neyman main allocation: `n_main_i ∝ N_i × σ_i`
  - Main phase: cluster i 에서 추가 sample
  - HT estimator: `Σ_i (pilot_hits + main_hits) × N_i / (n_pilot_i + n_main_i)`

### 구현 위치

* **파일**: `/Users/hyunbin/Capstone/experiments/code/rq3/kde/kde_pilot.py:1-300`
* **server side**: `/mnt/hdd0/home/capstone2026/cache/rq1/` 에 `rq3_kde_pilot.parquet` output. Server side path 는 `chain_unified.py:159-162` 에서 `__import__('run_kde_pilot_8m')` 또는 `import kde_pilot as runner` 로 dispatch.
* **paper_exact registry 에 등록 X**: `measure_paper_exact.py:_get_method_strata()` 에 kde_pilot entry 부재. kde_pilot 은 별도 standalone script 로 측정됨.

### KM20 Leak 분석 (핵심)

* **Stratum 부여 방식**:
  ```python
  # kde_pilot.py:90-97
  with psycopg.connect(host="/tmp", port=PORT, dbname=DB, user=USER, autocommit=True) as c:
      cu = c.cursor()
      cu.execute(
          f"SELECT stratum_id::int, count(*)::bigint FROM {ds['table']} "
          f"GROUP BY stratum_id ORDER BY stratum_id"
      )
      for sid, n in cu.fetchall():
          sizes[sid] = int(n)
  ```
  + line 100-111:
  ```python
  for sid in range(N_STRATA):
      with psycopg.connect(...) as c:
          cu = c.cursor()
          cu.execute(
              f"SELECT {ds['embed_col']}::real[] FROM {ds['table']} "
              f"WHERE stratum_id = {sid} LIMIT {CACHE_PER_CLUSTER}"
          )
          rows = [np.asarray(r[0], dtype=np.float32) for r in cu.fetchall()]
  ```

* **Stratum_id 가 어디서 왔는가**:
  - PG 테이블 `partsupp_deep_10_subset_1m` / `customer_sift_10_phase7_noidx_subset` 의 `stratum_id` column 에서 직접 SELECT
  - 이 column 은 `_internal/scripts/prepare_cell.py:110-136` 에서 ALTER TABLE + UPDATE 로 채워짐
  - `prepare_cell.py:8` 주석: "ALTER TABLE ADD COLUMN IF NOT EXISTS stratum_id smallint"
  - 다른 곳 (`server_wrappers_backup_20260507/sift_1m_kmeans_strata.py`, `sift_8m_kmeans_strata_v2.py`) 에서 KMeans20 결과를 PG 에 UPDATE 함
  - 즉 **PG 테이블의 stratum_id = KMeans20 cluster id**

* **결과**: kde_pilot 은 자기 자신의 stratification 을 만드는 것이 아니라, **이미 KM20 으로 stratified 된 partition 위에서 cluster-aware Neyman allocation 을 수행**. 이는:
  - kde_pilot 단독으로 P3 paradigm representative 자격 없음 — 본질이 P1 (KM20) + Neyman allocation
  - V7 audit (5/8) §6 line 145: "kde_pilot | KM20 cluster leak | ✓ pilot 이 KM20 partition 사용으로 data leak — 제외 정당" 일치

### CRITICAL DEFECT (severity = critical)

* **KM20 leak 확정**: PG 테이블의 stratum_id 가 KMeans20 결과 → kde_pilot 은 KM20 cluster 위에서 동작.
* **paradigm misclassification**: kde_pilot 을 P3 streaming 으로 분류 시:
  - 본질은 "KMeans20 stratification + Neyman allocation with KDE-based σ estimation"
  - 즉 P1 (KM20 partition) + RQ2 의 Neyman allocation variant (online σ estimation)
  - P3 (streaming) 의 inductive bias 부재
* **실험 결과 해석**:
  - kde_pilot 가 다른 method 보다 좋은 Δ% 보이면, 그것은 KDE pilot algorithm 의 효과가 아니라 **이미 KM20 으로 잘 stratified 되어 있기 때문**
  - 다른 method (e.g., reservoir, LSH) 들과 fair comparison 불가능

### 권고

1. **즉시**: kde_pilot 결과를 RQ3 paradigm 비교에서 **제외** (V7 audit 5/8 결정 유지).
2. **manuscript 정정**: 만약 kde_pilot 이 보고서 / 슬라이드에 method 로 등장 중이면:
   - "kde_pilot uses KM20 stratification (not its own)" 명시
   - 또는 P5 (allocation variant) 로 재분류 — 단 이는 RQ2 와 redundancy
3. **올바른 비교 변종 만들기** (만약 kde_pilot 의 진가를 증명하고 싶으면):
   - kde_pilot 자체적으로 stratification 만들기 (KMeans 호출 직접)
   - 또는 KDE 기반 stratification (kernel mean shift cluster) 로 변경
   - 단 이는 large refactor + new method 이고 본 RQ3 7-way 에는 부적합

### 결함 list

| Severity | 결함 |
|---|---|
| **CRITICAL** | KM20 leak — 자기 자신의 stratification 부재, PG 테이블의 KMeans20 결과를 사용 |
| Critical | P3 streaming paradigm 정체성 부재 — Neyman allocation 은 RQ2 의 분포-aware variant |
| Critical | RQ3 paradigm comparison 에서 fair comparison 불가능 (다른 method 들은 자기 stratification 만드는데 kde_pilot 만 KM20 사용) |
| Moderate | n_pilot=5 → cluster 당 5 sample 만 → KDE bandwidth estimate variance 큼 (Silverman rule 의 small-n breakdown) |
| Moderate | "online" 이라 표명하나 KM20 사전 계산 (offline) 필요 — strict streaming 아님 |
| Minor | bandwidth h 의 floor 부재 (`if m < 2 or sd < 1e-9` fallback 만 있음) |

---

## 종합 권고

### 알고리즘 충실도 점수 합계

| Method | 점수 / 10 | naming OK? | KM20 leak? | severity |
|---|---:|---|---|---|
| `minibatch_partial` | **8** | ✓ Sculley 2010 일치 | X | OK (★2 4강 자격 OK) |
| `reservoir` | **2** | ✗ Vitter 1985 와 무관 (RANDOM20) | X | **CRITICAL** |
| `thompson_sampling` | **2** | ✗ Thompson 1933 무관 (MiniBatchKMeans) | X | **CRITICAL** |
| `mfmc` | **2** | ✗ Peherstorfer 2018 무관 (KMeans + RANDOM20 mixture) | X | **CRITICAL** |
| `adaptive_bucket_probing` | **5** | △ "adaptive" naming mild misrep, PCA1D 와 dup | X | Moderate |
| `lpm2` | **2** | ✗ Grafström 2012 LPM 무관 (distance-shell) | X | **CRITICAL** |
| `kde_pilot` | **3** | △ KDE-pilot 의도 OK, but KM20 leak | **✓ KM20 leak** | **CRITICAL** |
| **평균** | **3.4** | 7건 중 4 critical naming + 1 KM20 leak | | |

### 즉시 조치 (priority 순)

1. **`reservoir` 표기 정정** — V7 audit (5/8) 에서 이미 "RANDOM20 proxy" 인정. 모든 RQ3 보고서/슬라이드/manuscript 에서 통일:
   - "RANDOM20 (Reservoir proxy)" 또는 "Random Partition Baseline"
   - "Vitter 1985 reservoir sampling" 인용 즉시 제거

2. **`thompson_sampling` 표기 정정** — Thompson 1933 인용 즉시 제거. method 자체를 RQ3 비교에서 제외하거나 "MiniBatchKMeans variant" 로 표기.

3. **`mfmc` 표기 정정** — Peherstorfer 2018 또는 Multi-Fidelity 인용 즉시 제거. method 자체를 "KMeans + RANDOM20 mixture (50:50)" 로 표기 또는 RQ3 비교에서 제외.

4. **`lpm2` 표기 정정** — Grafström 2012 LPM 인용 즉시 제거. method 자체를 "Distance-Shell (Weiszfeld median-centered)" 로 표기. V7 audit 의 distance_shell 와 redundancy 검토 후 제외 가능.

5. **`kde_pilot` 결과 제외 유지** — V7 audit (5/8) §6 의 결정 ("KM20 cluster leak — 제외 정당") 유지. 만약 보고서에 결과 포함 중이면 즉시 제거하거나 "KM20 + Neyman allocation variant" 명시.

6. **`adaptive_bucket_probing` PCA1D 와 통합** — 구현이 PCA1D 와 동일. RQ3 7-way 에서 별도 entry 라면 redundancy 표시.

7. **`minibatch_partial` 만 ★2 4강 자격 유지** — 7 method 중 유일하게 paper-correct + paradigm representative.

### Paradigm framework 영향 분석

* **P3 Streaming paradigm 의 representative 부족 문제**:
  - 7 method 중 1 (minibatch_partial) 만 P3 정통
  - reservoir 는 RANDOM20 proxy → P3 representative 자격 X
  - thompson_sampling 은 P1 redundant
  - mfmc 는 P1 + RANDOM mixture
  - lpm2 는 P2 redundant (distance-shell)
  - adaptive_bucket_probing 은 P4 redundant (PCA1D)
  - kde_pilot 은 KM20 leak

* **권고**: P3 paradigm 의 representative 를 minibatch_partial 1개로 한정. 다른 6개는 paradigm reassign 또는 제외.

* **보고서 narrative 영향**:
  - "5 paradigm × 11 method framework" 에서 P3 method count 가 (현재) 7 → (audit 후) 1 또는 2 (Reservoir 를 RANDOM20 baseline 으로 reframe 하면 2)
  - 이는 RQ3 의 "각 paradigm 별 inductive bias 비교" narrative 에 큰 영향 — paradigm 간 method 수 imbalance 명시 필요

### 학술 무결성 (academic integrity)

* **Critical naming misrepresentation 4건은 학술 출판 시 reviewer / 외부 자문 (박성원 멘토 등) 으로부터 challenge 받을 가능성 매우 높음**:
  - Vitter 1985, Thompson 1933, Peherstorfer 2018, Grafström 2012 는 standard textbook reference. 코드 inspection 으로 즉시 발견 가능
  - 본 연구의 contribution claim (특히 "5 paradigm framework" 의 학술 정합성) 자체가 약화될 위험
* **5/10 paper exact 측정 시 시점에서 정정 가능**: 현재 진행 중인 측정 결과 reporting 단계에 정정 적용. 측정 자체는 invalidate 하지 않고, **표기와 narrative 만 정정** 하면 학술 무결성 회복 가능.

### 최우선 단일 조치

본 7 method 중 P3 paradigm representative 로 narrative 에 강하게 등장하는 것은 **minibatch_partial (★2 4강)** 하나. 이것 하나는 algorithm-correct + paradigm-correct + ★2 자격 OK. 나머지 6 method 는 RQ3 7-way 에서 제외하거나 다른 paradigm 으로 reassign 하면 P3 narrative 자체는 minibatch_partial 1개로도 유지 가능.

만약 RQ3 method count 가 줄어드는 것을 피하고 싶다면:
1. **`reservoir` 만 "RANDOM20 baseline" 으로 reframe** (V7 audit 권고 그대로) 하여 P3 paradigm 의 control baseline 으로 narrative 추가
2. 나머지 5 method (thompson_sampling, mfmc, adaptive_bucket_probing, lpm2, kde_pilot) 은 제외

이 시나리오에서 P3 paradigm = `minibatch_partial` (★2 4강 winner) + `RANDOM20` (control baseline) = 2 method 로 깔끔. RQ3 7-way 비교에서 P3 가 다른 paradigm 들과 fair comparison 가능.

---

## 검증 자료 출처

* `/Users/hyunbin/Capstone/_internal/scripts/measure_paper_exact.py` (line 460-468, 500-503, 657-664, 666-676, 716-725, 837-850)
* `/Users/hyunbin/Capstone/experiments/code/rq3/kde/kde_pilot.py` (line 1-300)
* `/Users/hyunbin/Capstone/experiments/code/rq3/_measure_common.py` (line 116-151)
* `/Users/hyunbin/Capstone/_internal/scripts/prepare_cell.py` (line 110-136 — KMeans20 stratum_id UPDATE)
* `/Users/hyunbin/Capstone/_internal/archive/2026_05_09_audit_archive/audit_method_correctness_20260508.md` (V7 audit, line 18-19, 43, 61, 145)
* `/Users/hyunbin/Capstone/_internal/RQ3_paradigm_심층검증_20260508.md` (5 paradigm framework standard taxonomy cross-check)
* paper / handoff_v2: `/Users/hyunbin/Capstone/_internal/handoff_v2_paper_verbatim_decisions_20260510_1418.md`
* canonical references (학술 출처):
  - Sculley 2010 (WWW): MiniBatchKMeans + partial_fit
  - Vitter 1985 (TOMS): Reservoir Algorithm R
  - Thompson 1933 (Biometrika): Posterior sampling
  - Peherstorfer-Willcox-Gunzburger 2018 (SIAM Review): Multi-Fidelity Monte Carlo
  - Grafström 2012 (JSPI): Local Pivotal Method (LPM2)
  - Silverman 1986 (Chapman): KDE bandwidth
  - Aboulnaga & Chaudhuri 1999 (SIGMOD): Self-tuning histograms (closest match for "adaptive bucket probing")
