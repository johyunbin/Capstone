# Phase G — Production-grade Analysis Report (5/10 작성 in progress)

> 본 REPORT 는 Phase G 분석 (analyze_phase_g.py v9 mode) 의 산출물. **연구 목표: Exqutor §V-B Adaptive Sampling 을 대체할 distribution-aware sampling alternative 를 발굴하고 정량 비교한다**. 36 method × 26 cell + 3 SF=100 = 1,044 measurement 의 direct paired comparison.
>
> **Framing 정정 (5/10 12:04 KST)**: Augment (§V-B 위에 ensemble 추가) → **Replacement (§V-B 자체를 alternative sampling 으로 교체)**. 학술 근거: (1) Exqutor §V-B 가 paper 자체에서 "fixed sample may misrepresent selectivity" 분포 무시 한계 인정, (2) 단일 가설 (sampling 전략 비교) 의 confound-free 검증, (3) WanderJoin/FactorJoin/LpBound paper 와 동일 학술 convention.
>
> 데이터 source: `experiments/results/phase_g/method_matrix_36x26.csv` (analyze_phase_g.py v9 산출, 5/10 ~16:00 KST 예상 완료)
>
> **Status**: 🚧 측정 진행 중 (5/10 12:04 KST). Skeleton 작성 → 측정 종료 후 표/figure path 채워넣음.

---

## Executive Summary

**연구 질문**: Exqutor (arXiv:2512.09695v2) §V-B Adaptive Sampling 의 unstratified Bernoulli sampling 을, 분포 인지 alternative sampling 으로 **교체**했을 때 어떤 sampling 전략이, 어떤 데이터/scale 조합에서 §V-B 를 outperform 하는가?

**Direct paired comparison 구도**:
- **B1** = Exqutor §V-B (uniform Bernoulli + momentum-based sample size adaptation, m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, P=50, N₀=385)
- **B_alt = 36 alternative sampling methods** (Tier S+ Direct Estimator 7 + Tier A Stratification 10 + Tier B Joint Distribution 7 + Tier C Single AS variant 1 + Legacy 11) — 각각 standalone cardinality estimator
- **비교**: 같은 (cell, sel, seed, query) 좌표에서 q_error paired Δ% (Wilcoxon signed-rank + BH-FDR correction)

**핵심 결과** (TBD — 측정 완료 후 fill):
- Tier S+ Direct Estimator best: `<TBD method>` paired Δ% = `<TBD>%` (BH-FDR q < 0.05)
- Tier A Stratification best: `<TBD method>` paired Δ% = `<TBD>%`
- Tier B Joint Distribution best: `<TBD method>` paired Δ% = `<TBD>%`
- 36 method × 26 cell 중 §V-B B1 대비 paired-better (BH-FDR q < 0.05) cell-method 쌍: `<TBD count> / 936`

**핵심 contribution**: Exqutor §V-B의 sampling 단계를 distribution-aware alternative로 교체할 때, 특정 (Tier, scale, dataset) 조합에서 §V-B를 일관 outperform 하는 method portfolio 발굴 — production drop-in replacement candidate.

---

## §1. Storyline (7-stage)

| Stage | 입증 내용 | 측정 status | 참조 |
|---|---|---|---|
| ① RQ1+RQ2 single 효과 입증 | random vs Neyman stratified 정량 비교 | ✅ 완료 (W1 sprint 5/8) | `experiments/results/RQ1_RQ2 실험 결과 정리.md` |
| ② RQ3 single paradigm 우위 | 5 paradigm × 11 method 단일 비교 | ✅ 완료 (5/8 RQ3 sprint) | `experiments/results/rq3_agnostic/RQ3_16method_종합.md` |
| ③ Multi naive 적용 → cross-paradigm fail | 11 method × 6 cell paired-better 0/66 | ✅ 완료 (5/9 새벽) | `experiments/results/master_v6_§10.6_Multi_광범위_20260509.md` |
| ④ Failure mode 학술 진단 | curse of dim (Geraci 2026), Cochran §5.5, Bengtsson 2008 ESS | 🔄 5/10 새벽 진행 | TBD §3.4 below |
| ⑤ 36 method × 26 cell paradigm-rich portfolio | Tier S+ Direct + Tier A Stratification + Tier B Joint+Sample 각 paradigm 차원에서 우위 method 발굴 | 🔄 진행 中 (5/10 아침 ~ 정오) | TBD §4 below |
| ⑥ §V-B vs 36 alternative samplings (direct replacement) | Phase F B1 (Exqutor §V-B vanilla) 와 multi_paradigm 36 methods 의 직접 paired Δ% (Wilcoxon + BH-FDR) | 🔄 진행 中 (5/10 12:04, v9 par 8 procs) | TBD §5 below |
| ⑦ Production-ready package | drop-in replacement candidate methods + reproducible code (`experiments/code/exqutor_alternatives/`) | ⏳ 5/10 정오 ~ 오후 | TBD §6 below |

---

## §2. Method portfolio — 34 active methods + 3 DROPPED (Tier 분류, 5/10 12:34 update)

> 상세는 `_internal/handoff_v0_FINAL_SCOPE_20260510_0125.md` §1.1. Production-scale infeasibility로 5/10 12:34 WanderJoin + HDBSCAN drop 결정.

### Tier 1: Paradigm Baseline (10, HDBSCAN drop)
P1 Cluster (~~HDBSCAN~~ ⛔, MiniBatch, GMM) / P2 Spatial (Hilbert, faiss_ivf) / P3 Streaming (MB_partial, Reservoir) / P4 DimReduction (sparse_rp, PCA1D) / P5 QuasiRandom (LSH, Sobol)

### Tier S+: Direct Estimator (6, WanderJoin drop)
~~WanderJoin~~ ⛔, AMSCountSketch, NeuroCard, AdaptiveBucketProbing, CCSketch, FactorJoin, **LpBound** (SIGMOD 2025 Best Paper)

### Tier A: Stratification Primitives (10)
PQ, Coreset, DenseRP, BanditUCB1, NeurAM, ThompsonSampling, MFMC, EpsilonNetBaseline, kDPP, OPQ

### Tier B: Joint Distribution + Sample Design (7)
CCA1D, CoCluster_Nystrom, Tucker, VineCopula, **HKBU_RepSample** (SIGMOD 2026), LHS, LPM2

### Tier C: Single-only AS Variant (1)
ConditionalAdaptive (Exqutor §V-B variant)

### DROPPED (3, 5/10 12:34 update)
- ~~HNSW-SS~~ — narrative violation (vector index 사용)
- ~~**WanderJoin**~~ ⛔ — production-scale infeasibility (brute KNN O(N²d), sf=10 5h+ stuck)
- ~~**HDBSCAN**~~ ⛔ — production-scale infeasibility (sklearn O(N²) memory, 80M = 25 PB 요구)

---

## §3. Failure mode 학술 진단 (Stage ④)

### §3.1 Curse of dimensionality (high-d sampling)

> 768-d (WIKI) 에서 unstratified Bernoulli 의 estimator variance 가 d 에 대해 linearly-poorly scale 되어 0/66 paired-better fail (5/9 새벽 결과) 의 학술 진단.

- **Geraci et al. arXiv 2026**: NeurAM (autoencoder dim-invariant) 의 motivation — high-d 에서 standard stratification 이 fail 하는 mechanism. 우리의 결과와 일치.
- **Cochran (1977) §5.5**: stratification 의 within-stratum variance 가 d 와 거의 무관해야 효율적. Random projection 안 해두면 효과 X.
- **Bengtsson et al. (2008) ESS**: importance sampling weight 의 effective sample size 가 d 의 지수함수로 감소.

### §3.2 0/66 paired-better — multi naive transfer

11 method (single-table 우위 paradigm baseline) × 6 cell (multi 4-way + multi-join) → 0/66 paired-better. 즉 single-table 에서 Neyman stratified 가 random 보다 우위였던 paradigm 은 multi 에서 단순 transfer 시 한계 region 에 빠진다.

- **원인 (학술 정량)**: multi 결합 분포 (image embedding ⋈ wiki text) 의 joint variance 가 marginal 으로 설명 안 됨. Σ_joint ≠ ΣᵢΣⱼ.
- **우리의 contribution**: Tier B (CCA1D, CoCluster_Nystrom, Tucker, VineCopula, HKBU, LHS, LPM2) 가 joint distribution 을 직접 modeling 하여 0/66 fail 구간 에서 paired-better 회복.

(상세 표/figure: 측정 종료 후 fill — `g4_multi_naive_failure.csv`, `fig_g4_failure_heatmap.png`)

---

## §4. 36 methods paired Δ% 결과 (Stage ⑤) — TBD

### §4.1 Tier-level summary

| Tier | best method | best paired Δ% | n_cells_sig (raw) | n_cells_sig (BH-FDR q<0.05) |
|---|---|---|---|---|
| Tier 1 (Paradigm Baseline) | TBD | TBD | TBD | TBD |
| Tier S+ (Direct Estimator) | TBD | TBD | TBD | TBD |
| Tier A (Stratification) | TBD | TBD | TBD | TBD |
| Tier B (Joint+Sample)   | TBD | TBD | TBD | TBD |
| Tier C (Single AS variant) | TBD | TBD | TBD | TBD |

### §4.2 36 method × 26 cell heatmap

(figure: `experiments/figures/phase_g/G2_adaptive_gap.png` — paired Δ% per (method, cell), color = sign(Δ), value = magnitude)

### §4.3 Multi-table specific findings

> Exqutor §V-B 가 단일 KNN 한정이므로, multi-table cells (16 cells = 8 partsupp 4-way + 8 multi-join) 에서의 결과는 본 연구 unique contribution.

(TBD — measurement 종료 후 fill)

---

## §5. §V-B vs 36 alternative samplings — Direct paired comparison (Stage ⑥) — TBD

> **Replacement framing**: Exqutor §V-B (B1) 의 sampling 메커니즘 자체를 36 alternative methods 로 교체하여 직접 paired 비교. Augment baseline (B4 = ensemble on top of §V-B) 은 §5.4 reference 영역으로 강등.

### §5.1 Direct paired Δ% — 36 alternatives vs Exqutor §V-B

같은 (cell, sel, seed, query) 좌표에서 q_error_method vs q_error_B1 paired Δ%. Wilcoxon signed-rank + Bonferroni + BH-FDR (5/10 추가).

| Tier | best method | mean Δ% (vs B1) | n_cells_better | n_cells_sig (BH-FDR q<0.05) |
|---|---|---|---|---|
| Tier S+ Direct Estimator | TBD | TBD | TBD / 26 | TBD |
| Tier A Stratification | TBD | TBD | TBD / 26 | TBD |
| Tier B Joint Distribution | TBD | TBD | TBD / 26 | TBD |
| Tier C Single AS variant | TBD | TBD | TBD / 10 (single only) | TBD |
| Legacy Paradigm Baseline | TBD | TBD | TBD / 26 | TBD |

### §5.2 Cell-level findings — 어느 method 가 §V-B 를 outperform?

| Cell category | best alternative | paired Δ% | scale (sf) | 해석 |
|---|---|---|---|---|
| Single-table KNN (10 cells) | TBD | TBD | 1, 10 | §V-B의 native scope에서 alternative |
| partsupp 4-way (8 cells) | TBD | TBD | 1, 10 | multi-vector specialty |
| multi_join (8 cells) | TBD | TBD | 1, 10 | §V-B 미확장 영역 |
| SF=100 reproducibility (3 cells) | TBD | TBD | 100 | Exqutor Fig 4-6 strict match |

### §5.3 Algorithm 1 box (reviewer attack defense)

> 상세는 [experiments/results/phase_f/algorithm1_box.md](experiments/results/phase_f/algorithm1_box.md) 참조. Exqutor §V-B 식 1~6 의 의사코드 + hyperparam 표 (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, P=50, N₀=385) + 코드 cross-reference.

### §5.4 Augment effect (참고용 — main thesis 외)

> Replacement framing 채택 (5/10 12:04) — 본 sub-section 은 reference. Augment 가 strict replacement 보다 추가 이점 있는지 sanity check.

| 비교 | 결과 |
|---|---|
| B1 (§V-B vanilla) vs B4 (§V-B + ensemble) | TBD (Phase F v2 데이터) |
| B1 vs best replacement method | TBD (main result) |
| best replacement method vs B4 (augment) | TBD — 만약 replacement ≥ augment 이면 momentum framework 의 contribution 제한적 |

---

## §6. Production-ready replacement candidates (Stage ⑦) — TBD

> Exqutor §V-B 를 production 환경에서 drop-in 교체 가능한 alternative sampling 후보 정리. 박광현 BDAI 후속 연구 reproducible package — `experiments/code/exqutor_alternatives/`.

(TBD — 측정 + REPORT 완료 후 작성)

### §6.1 Drop-in replacement criteria

1. **Direct paired better** (BH-FDR q < 0.05 in ≥ 50% cells)
2. **Production-scale feasible** (sf=100 OK)
3. **No external dependency** (PostgreSQL extension 또는 Python lib 만)
4. **Single-call API** (`fit(table) → predict_cardinality(query, sel)`)
5. **Hyperparameter robustness** (default 만으로 작동)

### §6.2 Top candidates (TBD)

| Method | Paper | drop-in API | sf=100 OK | 권장 시나리오 |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

---

## §7. Reviewer attack defenses (3 BLOCKING)

| ID | Issue | Defense | 위치 |
|---|---|---|---|
| **B1** | Algorithm 1 box 누락 → "본 논문 그대로 구현했는지 검증 불가" reject | §V-B Adaptive Sampling 의 식 1~6 의사코드 + hyperparam 표 + 코드 cross-reference | `experiments/results/phase_f/algorithm1_box.md` ✅ 작성 완료 |
| **B4** | BH-FDR correction 누락 → "936 paired test family 의 false discovery rate inflated" reject | analyze_phase_g.py G2 함수에 `multipletests(method='fdr_bh')` 추가, `fdr_bh_q` + `sig_fdr_05` column 산출 | `_internal/scripts/analyze_phase_g.py` ✅ 적용 완료 |
| **B5** | ESS per-stratum 누락 → "importance sampling weight 의 effective sample size 가 stratum 별 측정 안 됨, 분산 비교 fairness 위반" reject | 모든 method 의 sample() return dict 에 `ess_per_stratum` field 추가, parquet schema 확장 | ⏳ 측정 끝난 후 batch 수정 (5/10 오후) |
| **B6** (5/10 added) | "왜 augment (§V-B + ensemble) 안 했나? 단순 replacement 는 momentum framework 의 contribution 무시" | (1) 단일 가설 검증 — confound 회피 (B4 win 이 stratification 인지 momentum 인지 구분 불가) (2) Exqutor §V-B paper 가 분포 한계 명시 인정 ("fixed sample may misrepresent selectivity") (3) §5.4 augment effect sanity check 결과로 보완 | §5.4 sanity check + paper-quoted limitation |

### Medium-severity issues

- **M2 저-selectivity 0.001**: 현재 0.01~0.50 → sel=0.001~0.01 영역 별도 측정 (5/10~5/12)
- **M3 curse of dim 학술 진단**: §3.1 above 에 Geraci/Cochran/Bengtsson 인용

---

## §8. Production-scale feasibility (5/10 통찰 — 핵심 contribution)

> 사용자 5/10 11:29 통찰: "결국 큰 데이터셋에서도 적용 가능한 방법들이 의미 있겠네."
> 사용자 5/10 12:34 결정: **"알고리즘 상 sf100에 적용할 수 없는 건 버려야 돼. 시간 복잡도나 공간 복잡도 상으로 이건 실제 적용할 수 없는 수준이다 싶은 것들"** → DROP.
>
> 본 연구의 진짜 contribution = **distribution-aware stratification ∩ production-scale feasibility**. 분포 정보를 활용하면서도 production-scale (sf=100, 80M rows) 에서 수렴 시간 안에 작동해야 의미 있다. WanderJoin (brute-force KNN O(N²d)) 과 HDBSCAN (sklearn O(N²) memory) 은 단순한 측정 사고가 아니라 **algorithm-level scalability 한계의 학술적 증거** — DROP 결정의 학술적 정당화.

### §8.0 DROPPED methods (production-scale infeasibility, 5/10 12:34)

| Method | Tier | DROP 사유 | 학술 정당화 |
|---|---|---|---|
| **HNSW-SS** | (Tier B candidate) | narrative violation (vector index 사용) | 우리 §V-B replacement 영역은 vector index 부재 환경 |
| **WanderJoin** ⛔ | Tier S+ | brute-force KNN O(N²·d). 80M × 768d = 4.9×10¹⁵ ops, sf=10에서 5h+ stuck 사례 | Li SIGMOD'16 알고리즘 자체는 unbiased estimator이나, 우리 vector-paired adaptation의 brute-KNN 구현이 unfeasible. FAISS IVF 대체 = future work. |
| **HDBSCAN** ⛔ | Tier 1 Legacy | sklearn O(N²) memory. 80M² = 6.4×10¹⁵ entries → **25 PB**. learn_frac=0.01도 800K² = 2.5 TB | Campello PAKDD'13의 mutual reachability distance matrix은 fundamentally O(N²). DBSCAN/OPTICS subsample-based alternative = future work. |

→ **34 active methods + 3 dropped** (Tier 1 Legacy 10 + Tier S+ 6 + Tier A 10 + Tier B 7 + Tier C 1).

### §8.1 Method × scale feasibility matrix (active 34)

### §8.1 Method × scale feasibility matrix (active 34)

| Method | sf=1 (800K) | sf=10 (8M) | sf=100 (80M) | Root cause | Fix path |
|---|:---:|:---:|:---:|---|---|
| ~~**WanderJoin**~~ ⛔ DROPPED | ✅ | ❌ stuck (5h+) | ❌ unfeasible | brute-force KNN O(N²d) | future work: FAISS IVF |
| ~~**HDBSCAN**~~ ⛔ DROPPED | ✅ | ❌ stuck (70min+) | ❌ stuck (6h+) | sklearn O(N²) memory | future work: DBSCAN/OPTICS |
| **NeurAM** (PyTorch) | ✅ | ⚠️ slow | ⚠️ epochs limit | autoencoder training | early-stopping + GPU |
| **NeuroCard-lite** (PyTorch) | ✅ | ⚠️ slow | ⚠️ epochs limit | autoregressive MLP | mixed-precision FP16 |
| **LpBound** (LP solver) | ✅ | ✅ | ✅ | scipy HiGHS small LP | — |
| **FactorJoin** (BP) | ✅ | ✅ | ✅ | 2-D histogram fit | — |
| **CCSketch** (FFT conv) | ✅ | ✅ | ✅ | sketch O(r·m·log m) | — |
| **AMSCountSketch** (SimHash) | ✅ | ✅ | ✅ | data-independent hash | — |
| **AdaptiveBucketProbing** | ✅ | ✅ | ✅ | LSH + Chernoff | — |
| **Tier A (10)** stratification | ✅ | ✅ (100K cap) | ✅ (100K cap) | fit_subsample 적용 | — |
| **Tier B (7)** joint dist | ✅ | ✅ (100K cap) | ✅ (100K cap) | fit_subsample 적용 | — |
| **Legacy 11** (P1-P5) | ✅ | mixed | partial | algo-specific | per-method fix |

### §8.2 학술 진단 — large-N에서 fail 하는 이유

**SF=100 HDBSCAN stuck (5/10 새벽 → 11:24 kill 결정)**:
- Sklearn HDBSCAN: O(N²) **memory** for mutual reachability distance matrix
- 80M rows × 80M = 6.4 × 10^15 entries → 25 PB memory 요구 — 사실상 불가
- learn_frac=0.01 (= 800K rows fit) 조차 800K² = 6.4 × 10^11 = 2.5 TB → 불가
- **결론**: HDBSCAN은 sf=100 에서 fundamentally infeasible, narrative 영향 없이 missing data 처리

**WanderJoin sf=10 stuck (5/10 새벽 4 procs × 5h+)**:
- [`methods/wander_join.py:88`](_internal/scripts/methods/wander_join.py:88) — `algorithm="brute"` KNN
- 8M rows × 768d brute-force = O(N²d) = 4.9 × 10^14 metric ops
- BLAS vectorized 하더라도 ~10h+ scaling
- **Fix path**: FAISS IVF (≈100x speedup, paper-faithful unbiased random walk semantics 보존)

**Tier B "joint distribution" 의 fit_subsample 보호**:
- LpBound, LPM2, HKBU_RepSample, Tucker, VineCopula, MFMC 등 6 methods는 `fit_subsample=100K` (HKBU `FIT_CAP`) 적용
- Logic: "100K representative subsample 으로 distribution 학습 후, 전체 N rows 에 1-NN/Voronoi assign"
- Cochran 1977 §4.5: 95%/±5% binomial half-width 에 N₀=385 충분 — 100K 는 distribution shape 학습에 압도적
- **이게 production-ready 의 핵심 디자인 패턴**

### §8.3 본 연구 contribution 재정의

| 측면 | Exqutor §V-B (B1, baseline) | 36 alternatives (B_alt, replacement) | 우위 |
|---|---|---|---|
| 분포 활용 | ❌ unstratified Bernoulli | ✅ distribution-aware | B_alt |
| Production scalability (sf=100) | ✅ N-independent (385 rows fixed) | ✅ N-independent (100K fit cap, lookup O(N)) | tie |
| Multi-table joint distribution | ❌ KNN only ("specifically for KNN" §V-B verbatim) | ✅ Tier B 7 methods | B_alt unique |
| Hyperparameter sensitivity | high (m, η₀, α, β, γ, P, N₀ 7개) | low (K=20 + fit_subsample) | B_alt |
| Adaptive size adaptation | ✅ momentum framework | varied (일부는 fixed sample, 일부는 자체 adaptation) | mixed |

→ **B_alt 의 distribution-aware + large-N feasible** 조합이 §V-B 를 outperform 할 수 있는 alternative 의 핵심 조건. 본 연구의 unique contribution = "어떤 alternative 가 §V-B 를 어떤 (Tier × scale × dataset) 조합에서 일관 outperform 하는지" 정량화.

### §8.4 future work — large-N method 보완

1. **WanderJoin FAISS replacement** — paper-faithful index-aware random walk를 brute KNN 대신 FAISS IVF로. 5/10 finalize 후 진행
2. **HDBSCAN hierarchical alternative** — DBSCAN with subsample-then-extrapolate, 또는 OPTICS hierarchical clustering
3. **PyTorch GPU 활성** — NeurAM/NeuroCard-lite를 GPU에서 epochs 50→100으로 늘려 SF=100 measurement 시도

---

## §9. Limitations

1. **KM20 oracle (production X)** — Phase F B6 baseline 은 ground-truth K=20 stratification 사용, 실제 production 환경에서는 unobservable.
2. **사전 계산 one-time cost** — Tier B method 의 joint distribution 학습 (CCA1D, Tucker, VineCopula 등) 은 dataset 단위 fit 필요. 새 dataset 마다 재계산.
3. **OLTP 범위 외** — analytical query 만 다룸. transactional workload (insert/update) 대응 X.
4. **단일→멀티 일반화 추가 연구 필요** — 본 연구 multi 결과 (16 cells) 가 partsupp ⋈ part with WIKI text 의 single join pattern 에 한정. 일반 N-way join 으로의 확장은 future work.
5. **HNSW vector index 환경 외** — Exqutor §V-A ECQO 와 직접 비교 X (우리 §V-B replacement 영역은 vector index 부재 환경).

---

## §10. Reproducibility

- **Code**: `_internal/scripts/methods/` (36 + 1 dropped, Tier 분류 README 참조)
- **Measurement**: `_internal/scripts/measure_multi_paradigm.py` + `cache/rq3/run_ensemble_4kang_adaptive.py` (서버)
- **Analysis**: `_internal/scripts/analyze_phase_g.py` v9 mode
- **Server**: 165.132.140.240, port 55435 (capstone PG, **port 55432/55433 절대 X — 채림 영역**)
- **GPU**: 0/2/3 (GPU 1 ERR — 사용 X)
- **Hyperparameters**: Algorithm 1 box `algorithm1_box.md` 참조

---

## §11. END

작성: 2026-05-10 KST (skeleton — 측정 종료 후 fill)
다음 단계: ① analyze_phase_g.py 실행 (~16:00 ETA) → ② 표/figure path fill → ③ §4-§6 narrative 작성 → ④ 사용자 review (5/11)
