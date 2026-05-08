## §10.6 Multi 광범위 일반화 — 11-method paradigm framework + Adaptive Sampling 비교 (5/8 21:34 launch, 5/9 morning fill 예정)

본 절은 5/8 비대면 회의에서 박세은 팀장이 ⭐⭐⭐ 우선순위로 결정한 *Adaptive Sampling 본 논문 비교 + multi-table 4강 적용* 의 후속 측정인 **multi-vector / multi-table-join 광범위 비교** 의 실측 결과를 보고한다. 단일 cell 의 4강 (HDBSCAN / MB_partial / Hilbert / sparse_rp) 비교 (§10.4) 와 Adaptive Sampling head-to-head (§10.7) 가 모두 단일 한정으로 마감되었기 때문에, 본 §10.6 는 *5 paradigm × 11 method* 의 multi 환경 일반화 패턴 + *4강 vs Adaptive* 의 multi 환경 head-to-head 패턴 + *단일 → multi shrinkage chain* 을 통합 리포트한다.

### §10.6.1 Multi 11-method 측정 framework

5 paradigm framework (5/8 20:43 Deep Review + 20:48 user confirm) 의 representative 11 method 를 multi 환경에 그대로 적용한다.

**측정 spec**:

- **3 cell**: `partsupp_deep_sift_10` (4-way, deep 96d + sift 128d) / `partsupp_deep_wiki_10` (4-way, deep 96d + wiki 768d) / `multi_join_deep_wiki` (multi-table join, partsupp_deep_10 ⨝ part_wiki_10).
- **11 method**: P1 Cluster (HDBSCAN, MiniBatch, GMM) / P2 Spatial (Hilbert, faiss_ivf) / P3 Streaming (MB_partial, Reservoir) / P4 DimReduction (sparse_rp, PCA1D) / P5 Quasi-random (LSH, Sobol).
- **Replication**: 5 selectivity × 5 seed × 100 query = 2,500 paired pair / cell / method.
- **총 측정량**: 3 × 11 × 5 × 5 × 100 = **8,250 measurement**.

**Stratification 입력 (4강 측정과 동일)**: `concat([emb1 / ||emb1||̄, emb2 / ||emb2||̄])` norm-aware concat 단일 vector. 모든 11 method 가 동일 입력 위에서 fit + assign → BERN baseline (rq2_multi_5mode_*) 와 query_id × seed × selectivity paired alignment.

**Launch (PID 4100549, 5/8 21:34)** — ETA 5/9 03~05 (10h IO 1 budget, HDD 단일 점유 가정).

### §10.6.2 Multi 11-method paired Δ% 표 (sel=0.10 reference)

paired Δ% 정의 (단일 §10.2 와 동일):

  Δ% = (q_error[method] − q_error[bernoulli]) / q_error[bernoulli] × 100

부호 음수 = method 가 더 정확. 165 cell (3 cell × 11 method × 5 sel) 중 sel=0.10 reference 33 cell.

| Method (paradigm) | partsupp_deep_sift_10 | partsupp_deep_wiki_10 | multi_join_deep_wiki | mean of 3 cell |
|---|---|---|---|---|
| HDBSCAN (P1) | TBD | TBD | TBD | TBD |
| MiniBatch (P1) | TBD | TBD | TBD | TBD |
| GMM (P1) | TBD | TBD | TBD | TBD |
| Hilbert (P2) | TBD | TBD | TBD | TBD |
| faiss_ivf (P2) | TBD | TBD | TBD | TBD |
| MB_partial (P3) | TBD | TBD | TBD | TBD |
| Reservoir (P3) | TBD | TBD | TBD | TBD |
| sparse_rp (P4) | TBD | TBD | TBD | TBD |
| PCA1D (P4) | TBD | TBD | TBD | TBD |
| LSH (P5) | TBD | TBD | TBD | TBD |
| Sobol (P5) | TBD | TBD | TBD | TBD |
| **Win count (Δ% < 0)** | TBD/11 | TBD/11 | TBD/11 | – |
| **Sig. count (BH q < 0.05)** | TBD/11 | TBD/11 | TBD/11 | – |

\* p < 0.05  \*\* p < 1e-3  \*\*\* p < 1e-7   |  bold = paired Wilcoxon p < 0.05 (raw)
multiple comparison correction: 165 test (3 cell × 11 method × 5 sel) BH FDR q=0.05 / Bonferroni α=0.05/165=3.0e-4.

raw csv reference: `_internal/cache/multi_paradigm_paired/multi_paradigm_paired_summary.csv` + `multi_paradigm_paired_wilcoxon.csv` (5/9 morning analyze_multi_paradigm.py 산출).

### §10.6.3 5 paradigm 별 multi 일반화 패턴

각 paradigm 의 representative method 평균 |Δ%| 을 통해 paradigm 단위 일반화를 평가한다. 단일 §10.2 / §10.4 의 paradigm ranking 이 multi 환경에서도 보존되는지가 핵심 질문이다.

| Paradigm | 단일 sweet spot 평균 |Δ%| | multi-vector 평균 |Δ%| | multi-join 평균 |Δ%| | Shrinkage |
|---|---|---|---|---|
| P1 Cluster (HDBSCAN/MiniBatch/GMM) | TBD | TBD | TBD | TBD× |
| P2 Spatial (Hilbert/faiss_ivf) | TBD | TBD | TBD | TBD× |
| P3 Streaming (MB_partial/Reservoir) | TBD | TBD | TBD | TBD× |
| P4 DimReduction (sparse_rp/PCA1D) | TBD | TBD | TBD | TBD× |
| P5 Quasi-random (LSH/Sobol) | TBD | TBD | TBD | TBD× |

**해석 (placeholder)**:

(1) **Paradigm ranking 보존 여부** — 단일에서 P1 Cluster ≈ P2 Spatial > P3 Streaming > P4 DimReduction > P5 Quasi-random 이었던 ranking 이 multi 에서 [TBD: 보존 / 부분 보존 / 거의 무작위]. (2) **Paradigm shrinkage 격차** — 단일 → multi shrinkage 비가 paradigm 간 격차 [TBD: 1차 dominant 단계 = vector 결합 (단일 → multi-vector) / 2차 = table 결합 (multi-vector → multi-join)]. (3) **분포 인지 강도 약화** — 분포 인지 약한 paradigm (P4/P5) 가 multi 에서 [TBD: BERN 동등 / hurt direction] 으로 약화되는지.

### §10.6.4 4강 vs 11-method full ranking (multi 환경)

단일 cell 의 4강 (production-friendly criteria 로 선정) 이 multi 환경에서도 11-method 중 상위 4 위 안에 보존되는지 검증한다. 보존된다면 4강 narrative 의 generalizability 가 multi 환경까지 확장됨을 증거 — 보존되지 않으면 *multi 환경에서 production-friendly tier 가 단일과 다른 method 조합* 임을 honest reporting.

| Cell | 단일 4강 ranking | multi 11-method top-4 (mean Δ%) | overlap (단일 4강 ∩ multi top-4) |
|---|---|---|---|
| partsupp_deep_sift_10 | HDBSCAN/MB_partial/Hilbert/sparse_rp | TBD | TBD/4 |
| partsupp_deep_wiki_10 | HDBSCAN/MB_partial/Hilbert/sparse_rp | TBD | TBD/4 |
| multi_join_deep_wiki | HDBSCAN/MB_partial/Hilbert/sparse_rp | TBD | TBD/4 |

**해석 (placeholder)**: overlap 평균 [TBD: 4/4 (완전 보존) / 2~3/4 (부분 보존) / 1/4 미만 (거의 무관)] — 단일에서 production-friendly 로 선정된 4 method 가 multi 일반화에서 [TBD: 일관성 강 / 약].

### §10.6.5 Multi Adaptive Sampling baseline + Multi 4강 paired 비교

5/8 회의 ⭐⭐⭐ 결정의 후속 — Multi Adaptive Sampling baseline (PID 4100548, ETA ~22:00) 과 4강 method 의 paired head-to-head Δ% 를 산출한다. 단일 §10.7 와 동일한 방식으로 query_id × seed × selectivity paired alignment 후 Wilcoxon two-sided p-value 를 계산한다.

paired Δ%_h2h 정의:

  Δ%_h2h = (q_error[method] − q_error[adaptive]) / q_error[adaptive] × 100

#### Cell-level head-to-head median Δ% 매트릭스 (3 cell × 4강)

| Cell | HDBSCAN | MB_partial | Hilbert | sparse_rp |
|---|---|---|---|---|
| partsupp_deep_sift_10 | TBD | TBD | TBD | TBD |
| partsupp_deep_wiki_10 | TBD | TBD | TBD | TBD |
| multi_join_deep_wiki | TBD | TBD | TBD | TBD |
| **Win count (median < 0)** | TBD/3 | TBD/3 | TBD/3 | TBD/3 |
| **Sig. count (Wilcoxon p < 0.05)** | TBD/3 | TBD/3 | TBD/3 | TBD/3 |
| **mean of cell median Δ%** | TBD | TBD | TBD | TBD |

raw csv reference: `_internal/cache/multi_paradigm_paired/multi_4kang_vs_adaptive_h2h.csv`.

#### 4 outcome 판정 (placeholder, fill 22:00 후)

(1) **Outcome A (4강 ≻ Adaptive in multi)** — 4강 method 의 평균 cell median Δ% 가 **음수 + Wilcoxon p < 0.05** in 다수 cell. 단일과 동일한 narrative.
(2) **Outcome B (Adaptive ≻ 4강 in multi)** — 4강 method 가 양수 + significant. multi 환경에서 Exqutor Adaptive 가 더 정확. 단일과 narrative 반대.
(3) **Outcome C (동등)** — 모든 method 의 Wilcoxon p > 0.05. multi 환경에서는 분포 정보 활용 효과 indistinguishable from Adaptive.
(4) **Outcome D (mixed)** — method 별로 outcome 다름. honest reporting 필요.

**사전 가설** (§10.7 narrative 와 정합): §10.6.6 의 25× shrinkage chain 이 multi 환경에서 4강 vs BERN 자체를 ±1% marginal 로 약화시키므로, 4강 vs Adaptive head-to-head 도 **Outcome C (동등) 가능성 우세** — 단일 정확성이 multi 정확성의 *필요조건만* 성립한다는 §10.6.6 narrative 와 정합.

#### Multiple comparison correction

12 test (3 cell × 4 method, sel pool 통합) 또는 60 test (3 cell × 4 method × 5 sel breakdown) 에 BH FDR + Bonferroni 적용. 단일 §10.7 의 40 test 보정 결과 (HDBSCAN BH 7/10, Bonferroni 6/10) 가 multi 에서 [TBD: 유지 / 약화] 를 확인한다.

### §10.6.6 단일 → multi shrinkage chain 재계산 (sparse_rp 추가)

W2 sprint 에서 4강 (HDBSCAN / MB_partial / Hilbert / Hybrid) 기준으로 산출한 단일 → multi shrinkage chain 은 **단일 sweet spot 17.13% → multi-vector 0.67% → multi-join 0.68%** (sel=0.10 평균 |Δ%|, 25.4×) 였다. 본 §10.6.6 는 4강 production-friendly 재선정 (Hybrid 제외 + sparse_rp 추가, 5/8 14:13 finalize) 후의 shrinkage chain 을 11-method 측정 결과로 재계산한다.

#### 재계산 shrinkage chain

| 단계 | cell pool | 4강 평균 |Δ%| | 단일 대비 shrinkage |
|---|---|---|---|
| 단일 sweet spot | 4 dataset (SIFT/WIKI/YFCC/DEEP, sf1+sf10) | 17.13 | 1.0× (baseline) |
| Multi-vector (avg of 2) | partsupp_deep_sift_10 + partsupp_deep_wiki_10 | TBD | TBD× |
| Multi-table-join | multi_join_deep_wiki | TBD | TBD× |

raw csv reference: `_internal/cache/multi_paradigm_paired/multi_shrinkage_table.csv`.

#### 11-method 전체 shrinkage 비교 (paradigm 별)

11 method 전체로 shrinkage 측정 시, *분포 인지 강도가 강한 paradigm* (P1 Cluster, P2 Spatial) 의 shrinkage 가 *분포 인지 약한 paradigm* (P5 Quasi-random) 의 shrinkage 보다 [TBD: 더 큼 / 비슷 / 더 작음]. 가장 큰 shrinkage 를 보이는 paradigm 을 식별하면 *multi 환경의 정확성 보존* 을 위한 후속 method 의 후보 paradigm 이 도출된다 (future work, joint-aware clustering / multi-vector decomposition).

#### narrative 정정

기존 §10.6 narrative 의 "shrinkage 의 발생 지점 = vector 수 증가 단계, table join 단계는 추가 약화 없음" 이 11-method 측정으로 [TBD: 보존 / 정정] 된다. sparse_rp 추가로 4강 평균 |Δ%| 가 [TBD: 증가 / 감소] 하므로 17.13% → multi 0.67% 의 25× 격차도 [TBD: 26× / 24× / 동일 수준] 으로 update.

#### 단일 정확성 = multi 정확성 *필요조건만* (재확인)

단일 sweet spot 17.13% 의 4강 magnitude 가 multi 에서 [TBD: shrinkage_x×] 로 약화된다는 사실은 다음을 함의한다 — (1) 단일 cell 에서 method 가 BERN 대비 strong improvement 를 가지지 못한다면 multi 에서도 거의 확실히 marginal. (2) 그러나 단일 strong improvement 를 가지더라도 multi 에서는 shrinkage 가 발생하므로 단일 정확성은 **충분조건이 아님**. → multi 환경의 method 선정은 단일 측정과는 *별개의 framework* 가 필요함을 정량 입증.

이 narrative 는 5/27 발표의 limitation slide + supplementary slide (자문 결과) 에 포함되어 *future work 의 명확한 방향* (multi-relation joint-aware clustering 또는 ECQO + 분포 인지 ensemble) 을 제시한다.

---

**산출 위치** (5/9 morning fill 후):

- raw csv (analyze_multi_paradigm.py 산출):
  - `_internal/cache/multi_paradigm_paired/multi_paradigm_paired_summary.csv`
  - `_internal/cache/multi_paradigm_paired/multi_paradigm_paired_wilcoxon.csv`
  - `_internal/cache/multi_paradigm_paired/multi_4kang_vs_adaptive_h2h.csv`
  - `_internal/cache/multi_paradigm_paired/multi_shrinkage_table.csv`
- 측정 source (서버):
  - `/mnt/hdd0/home/capstone2026/cache/rq3/multi_paradigm/multi_paradigm_<cell>.csv` (3 cell)
  - `/mnt/hdd0/home/capstone2026/cache/rq3/multi_adaptive/multi_adaptive_<cell>.csv` (3 cell)
  - `/mnt/hdd0/home/capstone2026/cache/rq3/rq2_multi_5mode_<cell>.parquet` (BERN baseline 기존)
- master_v6 통합: 본 skeleton 을 `RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` §10.6 위치로 merge (기존 §10.6 25× shrinkage placeholder 대체).
