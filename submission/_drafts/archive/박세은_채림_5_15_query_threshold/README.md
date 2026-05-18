# 박세은 5/15 요청 — 임채림 연구원용 query vector + threshold 자료

> **요청자**: 박세은 (팀장) → 임채림 (지도연구원, 박광현 교수님 BDAI 연구실)
> **작성**: 2026-05-15 11:42 KST · **준비**: 조현빈
>
> 박세은 5/15 11:34 메시지: "실험에서 사용했던 쿼리 벡터(쿼리 보낼때 쓴 '이거랑 비슷한 거 찾아줘'의 '이거')랑 threshold 보내주실 수 있나요? 채림님께서 요청해서요!"

---

## 1. 자료 종합 (★)

본 패키지 = 본 연구 (Form 1) 의 paper exact 측정에서 사용한 query vector + threshold 정보.

| dataset | dim | sf | n_query | query vector file | threshold file |
|---|---:|---:|---:|---|---|
| DEEP | 96 | 100 | 100 | `query_vectors_DEEP_96d_sf100.npy` | `query_selectivity_DEEP_96d_sf100.csv` |
| SIFT | 128 | 100 | 100 | `query_vectors_SIFT_128d_sf100.npy` | `query_selectivity_SIFT_128d_sf100.csv` |
| SimSearchNet++ (SSN) | 256 | 100 | 100 | `query_vectors_SSN_256d_sf100.npy` | `query_selectivity_SSN_256d_sf100.csv` |
| YFCC | 192 | 10 | 100 | `query_vectors_YFCC_192d_sf10.npy` | `query_selectivity_YFCC_192d_sf10.csv` |
| WIKI | 768 | 10 | 100 | `query_vectors_WIKI_768d_sf10.npy` | (DEEP+WIKI cross 시 DEEP query 사용) |

각 dataset 마다 100 query vector + 500 (= 100 query × 5 selectivity) D_target threshold.

---

## 2. query vector format

### 2.1 사용법 (Python numpy)

```python
import numpy as np
qvecs = np.load("query_vectors_DEEP_96d_sf100.npy")  # shape (100, 96)
qids = np.load("query_ids_DEEP_96d_sf100.npy")       # shape (100,) int64

# query 0 vector (96d float32)
print(qvecs[0])
print(f"norm: {np.linalg.norm(qvecs[0]):.4f}")
```

### 2.2 dataset 별 vector 정규화 특성 (★ 주의)

| dataset | norm 영역 | format |
|---|---|---|
| DEEP 96d | 1.0 (normalized) | L2-normalized embedding |
| SIFT 128d | ~500 (raw integer) | SIFT descriptor (8-bit) |
| SSN 256d | ~2000 (raw integer-like) | SimSearchNet feature |
| YFCC 192d | ~1800 (raw integer-like) | YFCC visual descriptor |
| WIKI 768d | ~2.4 (mostly normalized) | text embedding (768d) |

**reproducibility**: dataset 마다 normalization 다름. distance metric 동일하지만 absolute distance 의 scale 이 다름.

---

## 3. threshold 정보

### 3.1 paper verbatim threshold (TPC-H queries)

본 측정 영역 사용한 paper §V-B verbatim threshold:

| query | threshold | source |
|---|---:|---|
| q3, q5, q8, q9, q10, q11, q12, q20 (TPC-H 8 queries) | **0.86** | reference/exqutor_query_plans/tpc_h/*.sql verbatim |

→ **모든 TPC-H query 영역 fixed threshold 0.86** (paper §IV verbatim, 영역 query 영역 동일).

### 3.2 paper verbatim threshold (TPC-DS queries, A3-TPCDS cell only)

A3-TPCDS cell (paper Fig 10/11 ECQO 영역) 영역 영역:

| query | threshold |
|---|---:|
| q07, q12, q20, q72 | 1.08 |
| q19, q42 | 1.20 |
| q98 | 1.30 |

(본 연구 영역 우리 §V-B 영역 영역 X. paper §V-A ECQO 영역 영역.)

### 3.3 per-query D_target (selectivity 별 threshold)

위 paper verbatim threshold 외에 **selectivity 별 calibrated threshold** = `D_target` field (csv 영역).

각 csv file 영역 schema:
```
query_id, selectivity, D_target, true_cardinality, actual_sel
```

**D_target 의 의미**:
- 각 query × selectivity 쌍 영역 영역, 그 query 영역 ground-truth top-k% (selectivity) 를 영역 distance threshold
- 영역: query_id=0, selectivity=0.01 → top 1% nearest neighbor 영역 distance 가 D_target = 1.049 (DEEP normalized)
- → distance ≤ D_target 영역 vector 영역 = top selectivity % 영역 ground truth

**D_target sample** (DEEP 96d sf=100, query 0):

| selectivity | D_target | true_cardinality | actual_sel |
|---:|---:|---:|---:|
| 0.01 | 1.049 | 787,904 | 0.00985 |
| 0.05 | 1.195 | 3,976,314 | 0.04970 |
| 0.10 | 1.258 | 7,932,641 | 0.09916 |
| 0.30 | 1.408 | 23,800,000+ | ~0.30 |
| 0.50 | 1.510 | 39,700,000+ | ~0.50 |

(전체 csv 영역 100 query × 5 selectivity = 500 row)

### 3.4 paper §V-B 영역 selectivity sweep

본 측정 영역 paper Fig 13 sel sweep 영역 영역 영역 영역:
- A1-DEEP (sel=0.01): D_target ~ 1.0~1.3 (DEEP 96d normalized)
- A4-sel (sel=0.001): D_target 영역 더 낮음 (top 0.1% 영역)
- (sel=0.10 영역 영역 측정, paper Fig 13 영역 두 selectivity 만 cover)

---

## 4. 본 연구 (Form 1) 영역 query 영역 어떻게 사용?

### 4.1 paper §V-B Adaptive Sampling 의 query 처리

```python
for q_idx in range(n_queries):
    qvec = qvecs[q_idx]  # (dim,) float32
    D = qs_full.iloc[q_idx]["D_target"]  # threshold for this query
    true_card = qs_full.iloc[q_idx]["true_cardinality"]

    # method-specific stratified Bernoulli sampling
    alloc = mc.equal_alloc(n_strata=20, budget=state.size)
    est = mc.stratified_estimate(samples, sizes, alloc, qvec, D, rng)

    # estimator 영역 cardinality 추정
    q_err = q_error(est, true_card)

    # AdaptiveState update (paper Eq 1-6)
    ratio = state.size / total_rows
    state.update(q_err, ratio)
```

→ 각 query 영역 `qvec + D` 사용 → range query (distance ≤ D) cardinality 추정.

### 4.2 본 연구 측정 영역 selectivity 영역 영역

본 paper exact 측정 영역 selectivity 5단계: `[0.01, 0.05, 0.10, 0.30, 0.50]`
- **default cell (A1-DEEP/SIFT/SSN, A2-Fig7/9, A5-scale-sf{1,10,100})**: sel=0.01 영역 영역 측정 (paper Fig 12 default)
- **A4-sel**: sel=0.001 영역 영역 측정 (paper Fig 13 영역 영역 selectivity)

---

## 5. 박광현 미팅 5/15 14:00 영역 활용 가능 영역

본 자료는 박광현 교수님 + 임채림 연구원이 본 연구의 query input + threshold 영역 학술 정합성 verify 영역 영역.

가능한 review 영역:
1. **query vector 영역 paper exact base 정합성**: paper §V-B Adaptive Sampling 영역 query input format 영역 일치하는지
2. **D_target threshold 영역 calibration**: 각 query 영역 ground-truth selectivity 정확도
3. **dataset 영역 normalization 영역 distance metric 영역 일관성**: SIFT raw vs DEEP normalized 영역 distance 영역 영역 영역
4. **selectivity 5단계 영역 본 연구 paper Fig 12/13 cover scope**

---

## 6. 기타 reference

- 본 연구 narrative: `submission/_drafts/속도는벡터_본연구_narrative_최종정리_v2_draft.md`
- 본 연구 paper exact REPORT: `experiments/results/raw/REPORT_분석/REPORT_paper_exact_v11.md`
- paper verbatim hyperparam (Eq 1-6): `_internal/handoff/active/handoff_v17_*.md` 의 paper hyperparam
- paper Fig 6 영역 paper p.7 영역 verbatim: 1000 query iterations × N_init=385 budget

---

작성: 2026-05-15 11:42 KST · 박세은 (팀장) → 임채림 (지도연구원) 요청 응답 · 5 dataset (DEEP/SIFT/SSN/YFCC/WIKI) × 100 query × 5 selectivity threshold + paper TPC-H/TPC-DS verbatim threshold 종합
