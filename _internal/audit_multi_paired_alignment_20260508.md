# Multi Paired Alignment Integrity Audit

**작성**: 2026-05-08 23:25 KST
**검증자**: 백그라운드 에이전트 V8
**대상**: Multi-table cell 의 4-way measurement paired key alignment
**범위**: 5 cell × 4 measurement source (4kang + 5mode + paradigm + adaptive)

---

## 1. 검증 목적

Multi narrative ("4강 vs Adaptive" + "11-method paradigm distribution") 의 evidence backing 을 위해, 4 measurement source 가 동일 (selectivity, seed, query_id) tuple 위에서 paired Δ% 계산이 가능한지 정량 검증.

기대치: 5 sel × 5 seed × 100 query = **2500 unique tuples** per cell × method.

---

## 2. Schema 확인

5 measurement source 모두 공통 paired key column **(selectivity, seed, query_id)** 보유. 부가 컬럼:

| Source | Rows/cell | Methods | Key cols | Extra cols |
|---|---|---|---|---|
| `multi_4kang_*` | 10,000 = 4 method × 2,500 | 4 (hilbert/hybrid/mb_partial/hdbscan) | (sel, seed, qid) | est, q_error, true_card |
| `rq2_multi_5mode_*` | 12,500 = 5 mode × 2,500 | 5 (bernoulli/equal/proportional/neyman/anti_neyman) | (sel, seed, qid) | est, q_error, true_card |
| `multi_paradigm_*` | 27,500 = 11 method × 2,500 | 11 (HDBSCAN/MiniBatch/GMM/Hilbert/faiss_ivf/MB_partial/Reservoir/sparse_rp/PCA1D/LSH/Sobol) | (sel, seed, qid) | est, q_error, paradigm tag |
| `multi_adaptive_*` | 2,500 = 1 mode × 2,500 | 1 (adaptive_sampling) | (sel, seed, qid) | est, q_error, sample_size_t1, sample_size_t2 |

5-tuple identifier 동일 (sel ∈ {0.01, 0.05, 0.1, 0.3, 0.5}, seed ∈ {0.1, 0.2, 0.3, 0.4, 0.5}, query_id 100 unique), table 컬럼은 cell 별 단일 값.

---

## 3. Per-cell N-way intersection

| Cell | 4kang | 5mode | paradigm | adaptive | N-way intersection | Status |
|---|---|---|---|---|---|---|
| `partsupp_deep_sift_10` (SF10) | 2,500 | 2,500 | 2,500 | 2,500 | **2,500** | ✅ PERFECT |
| `partsupp_deep_sift_1` (SF1) | 2,500 | 2,500 | 2,500 | 2,500 | **2,500** | ✅ PERFECT |
| `partsupp_deep_wiki_10` (SF10) | 2,500 | 2,500 | (없음) | 2,500 | **2,500** (3-way) | ✅ paradigm pending |
| `partsupp_deep_wiki_1` (SF1) | 2,500 | 2,500 | 2,500 | 2,500 | **2,500** | ✅ PERFECT |
| `multi_join_deep_wiki_1` (SF1) | 2,500 | 2,500 | 2,500 | 2,500 | **2,500** | ✅ PERFECT |
| `multi_join_deep_wiki` (SF10) | 2,500 | 2,500 | (없음) | 2,500 | **2,500** (3-way) | ✅ paradigm pending |

**모든 cell 의 4-way (또는 3-way 가능 cell) intersection = 2,500** — 0 row loss.

또한 4kang 의 method (hdbscan/mb_partial/hilbert) 와 paradigm 의 동명 method (HDBSCAN/MB_partial/Hilbert) est 이 **2,500/2,500 row 모두 정확 일치** (rtol=1e-3, mean diff = 0.0000) 측정 일관성 확인.

---

## 4. SF10 vs SF1 cross-paired alignment

| 비교 | SF10 query_id range | SF1 query_id range | qid intersection |
|---|---|---|---|
| `partsupp_deep_sift` | [25,058 — 7,938,046] | [2,505 — 793,779] | **0 / 100** |
| `partsupp_deep_wiki` | [25,058 — 7,938,046] | [2,505 — 793,779] | **0 / 100** |
| `multi_join_deep_wiki` | [25,058 — 7,938,046] | [2,505 — 793,779] | **0 / 100** |

**SF10 ↔ SF1 query pool 은 disjoint** — query_id 가 PG OID 기반 row identifier 이므로 SF1 (~80만 rows) 과 SF10 (~800만 rows) 의 query 가 완전히 별개.

→ SF10 vs SF1 cross-paired Δ% 계산 **불가능**, only **within-SF paired comparison** valid.

---

## 5. 결론

### Paired Δ% 계산이 valid 한 비교

✅ **YES** — within-cell, within-SF 의 모든 pairwise Δ% 계산 정확 가능:
- 4강 method (HDBSCAN/MB_partial/Hilbert/Hybrid) vs 11-method paradigm — 2,500 paired rows
- 4강/paradigm method vs Adaptive — 2,500 paired rows
- 5mode (bern/equal/prop/ney/anti) vs 4강/paradigm/adaptive — 2,500 paired rows

Spot check: HDBSCAN (paradigm) vs Adaptive (within `partsupp_deep_sift_10`) → paired Δ% = +10.561% (HDBSCAN q_error 가 adaptive 보다 10.6% 큼, paired t-test 가능).

### Paired Δ% 계산이 invalid 한 비교

❌ **NO** — SF10 vs SF1 cross-paired Δ% 불가:
- query_id pool disjoint → unpaired aggregate 비교만 가능 (independent samples).
- 만약 SF scaling effect 를 보고 싶다면, **per-SF 통계 (mean q_error)** 를 비교하되 paired t-test 는 사용 불가, two-sample test (Welch 등) 사용 권장.

### 다음 cell (paradigm SF10 wiki + multi_join SF10) 측정 완료 후

`partsupp_deep_wiki_10` 과 `multi_join_deep_wiki` (SF10) 의 paradigm csv 가 아직 미존재 (SF10 paradigm 은 SF10 sift 만 측정됨). 이 두 cell 은 4kang + 5mode + adaptive 의 3-way intersection 으로 검증되며, paradigm 측정 launch 시 동일 query pool 사용 보장 시 4-way 도 perfect align 예상 (`measure_multi_paradigm.py` 가 동일 query_pool parquet 사용 확인 필요).

### 산출

- 모든 within-cell paired Δ% 계산 **green light** — narrative evidence backing 안전.
- SF10 ↔ SF1 비교는 **per-SF aggregate** 만 valid, paired 절대 불가 (narrative 작성 시 명시).
- 4강 method 의 4kang vs paradigm est duplicate 검증 ✅ (2,500/2,500 정확 일치) — 측정 코드 재현성 확인.

---

## 6. 권고 사항

1. Multi 4강 vs Adaptive narrative 작성 시 within-cell (sel, seed, qid) paired t-test / paired CI 사용 가능 — 통계검정 확정.
2. SF1 vs SF10 비교는 "scale effect" 라는 frame 으로 unpaired aggregate 만 보고 (e.g., "SF10 에서는 mean q_error 가 SF1 대비 X% 변화").
3. paradigm SF10 wiki + join SF10 측정이 완료되는 즉시 동일 검증 재실행 권장 (이 audit 와 동일 4-way intersection 기대).
