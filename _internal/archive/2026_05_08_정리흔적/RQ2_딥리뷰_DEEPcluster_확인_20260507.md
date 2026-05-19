# RQ2 딥리뷰 보강 — DEEP cluster 수 (10 vs 20) PG 직접 확인

작성: 2026-05-07 11:10 KST · `_internal/RQ2_딥리뷰_20260507.md` §2.4 + §5.1 + 종합문서 §self-review (2) 의 W2 보강 작업

---

## 결론 (TL;DR)

| 항목 | 값 | 출처 |
|---|---|---|
| **DEEP 1M 실제 cluster 수** | **20** (stratum_id 0–19) | PG `partsupp_deep_10_subset_1m` 직접 조회 |
| **DEEP 8M 실제 cluster 수** | **20** (stratum_id 0–19) | PG `partsupp_deep_10_phase7_8m_subset` |
| **SIFT 1.5M 실제 cluster 수** | **20** (stratum_id 0–19) | PG `customer_sift_10_phase7_noidx_subset` |
| `rq2_alloc_python.py` `N_STRATA = 20` | 정확 | 모든 dataset 와 일치 |
| `rq2_sigma_signal_metrics.csv` 의 10 row | **별개 분석 결과** (RQ1 PCA, 10-cluster 분할) | RQ2 stratification 과 무관 |
| **PG `vector_stratum_sigma` 현재 상태** | 8M 만 (DEEP 1M / SIFT σ 없음) | reproducibility 이슈 — 그러나 결과는 valid |

**RQ2 narrative 영향**: 🟢 **무영향** — 측정 결과 valid, alloc 코드 정확. 단, RQ2 딥리뷰 §2.4 의 "DEEP cluster=10" 추정은 **정정 필요** (10 row CSV 가 다른 분석 산출).

---

## §1. PG 직접 query 결과

### 1.1 stratum_id 분포 (3 dataset)

```sql
SELECT 'DEEP_1M' AS dataset, COUNT(DISTINCT stratum_id) AS n_strata,
       MIN(stratum_id), MAX(stratum_id), COUNT(*) AS rows
FROM partsupp_deep_10_subset_1m
UNION ALL
SELECT 'DEEP_8M', COUNT(DISTINCT stratum_id), MIN(stratum_id), MAX(stratum_id), COUNT(*)
FROM partsupp_deep_10_phase7_8m_subset
UNION ALL
SELECT 'SIFT_1.5M', COUNT(DISTINCT stratum_id), MIN(stratum_id), MAX(stratum_id), COUNT(*)
FROM customer_sift_10_phase7_noidx_subset;
```

| dataset | n_strata | min_sid | max_sid | rows |
|---|---|---|---|---|
| DEEP_1M | **20** | 0 | 19 | 1,000,000 |
| DEEP_8M | **20** | 0 | 19 | 8,000,000 |
| SIFT_1.5M | **20** | 0 | 19 | 1,500,000 |

→ 모든 테이블이 **20 strata** (KM20 baseline 과 일치). `N_STRATA = 20` 하드코딩은 정확.

### 1.2 σ table (`vector_stratum_sigma`) 현재 상태

```sql
SELECT table_name, COUNT(DISTINCT stratum_id) AS unique_strata,
       SUM(n_i) AS total_n
FROM vector_stratum_sigma GROUP BY table_name;
```

| table_name | unique_strata | total_n |
|---|---|---|
| partsupp_deep_10_phase7_8m_subset | 20 | 8,000,000 |

⚠️ **DEEP 1M, SIFT 1.5M 의 σ row 없음** — 현재 PG 에 8M σ 만 보존.

---

## §2. `rq2_sigma_signal_metrics.csv` 출처 추적

### 2.1 생성 스크립트

`experiments/code/local_analysis/rq2_sigma_signal_root_cause.py` line 42:

```python
df = pd.read_parquet(RQ1 / "data_side_strata_pca.parquet")
```

→ RQ2 σ_i 를 PG 에서 읽지 **않고**, RQ1 의 `data_side_strata_pca.parquet` (PCA 분석) 에서 cluster 를 그룹핑.

### 2.2 σ_i proxy 정의

스크립트 line 48-50:
```python
cluster = df.groupby("stratum_id").agg(
    N_i=("row_idx", "count"),
    sigma_pc1=("first_pc_proj", "std"),
    mean_pc1=("first_pc_proj", "mean"),
)
```

→ σ_i 는 **first PC projection 의 std** (PCA proxy), 실제 query-dependent σ_i 가 아님.

### 2.3 10 row 의 의미

`data_side_strata_pca.parquet` 가 **10 cluster KM 분할** 의 PCA 결과 (RQ1 의 별도 data-side 분석 산출). RQ2 의 KM20 stratification 과는 **별개의 분석**.

→ CSV 의 10 row 는 RQ2 의 cluster 수가 아니라, **RQ1 PCA proxy 분석의 10-cluster 분할** 결과.

---

## §3. RQ2 딥리뷰 §2.4 정정

### 3.1 원래 추정 (RQ2 딥리뷰 line 142-149)

> `experiments/results/rq2_aware/rq2_sigma_signal_metrics.csv`:
> - 10 rows (stratum_id 0–9), N_i = 100,000 each, total = 1M
> - 즉 **DEEP 1M 의 실제 cluster 수 = 10** (vector.c 의 KMeans 가 10-strata 를 사용한 것으로 보임)

### 3.2 정정

- DEEP 1M 의 실제 cluster 수 = **20** (PG 직접 조회 확인)
- σ_signal CSV 의 10 row 는 **RQ1 PCA proxy 분석 (10-cluster)** 의 산출 — RQ2 stratification 무관
- vector.c 의 KMeans 도 **20** strata 를 사용 (rq1_motivation 의 KM20 baseline 과 일치)

### 3.3 §5.1 narrative 정정

> ~~`rq2_anti_neyman_cell_analysis.py` line 84: `p_BH_005` → `p_bonferroni_005` 로 명칭 정정~~ (이건 유효, 별건)
> ~~`N_STRATA` 하드코딩: rq2_alloc_python.py 가 20 사용 — 실제 cluster 수가 다를 경우 cache_cluster_samples 단계 crash 가능~~

→ **하드코딩 20 은 모든 dataset 와 일치하므로 crash risk 없음**. 그러나 동적 결정은 여전히 코드 robustness 차원에서 권고 (W2).

---

## §4. σ table reproducibility 이슈 (별건 발견)

### 4.1 현상

`compute_stratum_sigma.py` line 69:
```python
cur.execute("DELETE FROM vector_stratum_sigma")
```

→ 매 실행마다 모든 row 삭제 후 INSERT. 마지막 실행이 8M 만 처리했기 때문에 DEEP 1M / SIFT σ 가 wiped.

### 4.2 측정 결과는 valid

`rq2_alloc.parquet` 의 DEEP s=0.01 5-mode q_error mean 비교 (5/6 측정 시):

| mode | mean q_error |
|---|---|
| equal | 1.6541 |
| neyman | 1.6070 |
| proportional | 1.6268 |
| anti_neyman | 1.6339 |
| bernoulli | 1.7034 |

→ **neyman ≠ equal, anti_neyman ≠ proportional** → 측정 시점에는 σ 가 정상 존재. (만약 σ 가 비어있으면 `allocate_samples` 의 fallback 으로 neyman==equal, anti_neyman==proportional 이 됨)

### 4.3 W2 권고

1. `compute_stratum_sigma.py` 의 DELETE 를 conditional (table 별) 로 변경:
   ```python
   cur.execute(f"DELETE FROM vector_stratum_sigma WHERE table_name = '{table}'")
   ```
2. DEEP 1M, SIFT σ 재생성 (5/8 회의 후 W2 작업) — reproducibility 회복

---

## §5. 5/8 회의 narrative 영향

### 5.1 변경 사항: 없음

- RQ2 결과 (Anti-Neyman vs Proportional median CI vs Wilcoxon p 격차, Proportional MK p=0.027 등) 모두 **valid**
- N_STRATA = 20 정확, alloc 코드 정상 동작
- σ_signal CSV 의 PCA proxy 분석은 별건 — narrative 에서 σ_i 신호 약함 root cause 로 인용 시 **"PC1 variance proxy 기준 (실제 σ_i 와 다름)"** 명시 권고 (RQ2 딥리뷰 §4.1 와 동일)

### 5.2 정정 필요 사항

- **딥리뷰 §2.4 의 "DEEP cluster=10" 추정 삭제**: 본 보강 결과로 cluster=20 확정
- **종합문서 §self-review (2) 의 "검증 미완료" → "확정: 20 strata"** 로 수정

### 5.3 자문 메일 영향

채림 석사 자문 요청 시:
- ✓ "RQ2 의 KM20 stratification" 표현 정확
- ✓ Anti-Neyman ablation 의 σ_i sensitivity 분석 결과 그대로 인용 가능

---

## §6. 검증 방법 (재현 가능)

```bash
# 1. PG cluster 수 확인 (서버에서)
ssh capstone "/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin/psql \
    -h /tmp -p 55436 -U wns41559 -d wns41559 -c \
    \"SELECT 'DEEP_1M', COUNT(DISTINCT stratum_id) FROM partsupp_deep_10_subset_1m \
      UNION ALL SELECT 'SIFT_1.5M', COUNT(DISTINCT stratum_id) FROM customer_sift_10_phase7_noidx_subset \
      UNION ALL SELECT 'DEEP_8M', COUNT(DISTINCT stratum_id) FROM partsupp_deep_10_phase7_8m_subset;\""

# 2. σ table 현재 상태 확인
ssh capstone "/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin/psql \
    -h /tmp -p 55436 -U wns41559 -d wns41559 -c \
    \"SELECT table_name, COUNT(DISTINCT stratum_id) FROM vector_stratum_sigma GROUP BY table_name;\""
```

→ 본 결과 모두 재현 가능.
