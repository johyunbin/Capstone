# RQ1 Motivation 실험 파이프라인 — Skew vs Exqutor Adaptive Sampling

**작성일**: 2026-04-14 16:28 KST (v1) / 16:40 KST (v2 교정) / 17:00 KST (v2.1 실측 결과 반영)
**버전**: v2.1 — v2 파이프라인 단일 세션 완주 후 실측 결과를 §VIII로 요약. RQ1 가설 H1은 기각, Block bias는 실증. 설계안 pivot 후보 3개 제시 (팀 논의 필요)
**의존 문서**:
- `plans/연구 설계안_20260403_162818.md` (v3, 상위 연구 방향)
- `research/analysis/(01) Exqutor 상세분석.md` (논문 구조)
- `memory/reference_server.md` (서버 상태)
- `experiments/config/experiment_params.yaml` (파라미터 초안)

**목적**: RQ1("Exqutor의 adaptive sampling은 거리 분포의 skewness에 따라 추정 정확도가 얼마나 달라지는가?")을 서버 환경에서 실측·재현하기 위한 실행 명세. 본 문서는 설계안 v3의 1단계 Motivation 실험을 **코드 레벨로 구현 가능한 수준**까지 구체화한다.

---

## I. 배경 — Deep Review 결과 요약

### I.1 Exqutor Adaptive Sampling의 내부 구조

2026-04-14 오후 `PostgreSQL/pgvector/patch/pgvector_Exqutor.patch` (49 KB) 전수 분석으로 다음 사실을 확정했다.

**훅 등록 경로**. Exqutor는 PostgreSQL 코어에 `set_baserel_rows_estimate_hook`이라는 신규 훅을 추가하고(`pgvector_Postgres.patch`), pgvector 확장의 `_PG_init()`에서 이 훅에 `pgvector_set_baserel_rows_estimate_hook`을 register한다. 결과적으로 벡터 컬럼이 포함된 base relation의 카디널리티 추정이 플래너 단계에서 Exqutor의 통제 하로 들어간다. 호출 조건은 세 가지가 동시에 만족되어야 한다: (1) `has_vector_column()`이 참, (2) 첫 실행(`is_first_execution`), (3) ORDER BY로 정렬이 요구되고(`ordering_needed`) 샘플링 세션이 이미 활성화되어 있지 않음.

**ECQO vs Sampling 분기**. 플래너는 쿼리 플랜 내부에서 `collect_hnsw_nodes()`로 HNSW 인덱스 스캔 노드를 수집한다. 해당 노드가 발견되면 `CreatePlannedStmtForVectorSearchNodes()`로 HNSW range query를 **계획 단계에서 실제로 실행**하여 정확한 카디널리티를 얻고(**ECQO 경로**), 그 결과를 `vector_cardinality_results` 리스트에 저장한다. HNSW 노드가 없거나 PG 옵티마이저가 인덱스 스캔을 배제한 경우에는 `estimate_cardinality_with_sampling(total_rows)`가 호출된다(**샘플링 경로**). 따라서 **"HNSW 인덱스가 플랜에 포함되는가"가 두 경로를 가르는 단일 조건**이다.

**샘플링 메커니즘**. `estimate_cardinality_with_sampling()`은 SPI로 다음 SQL을 직접 실행한다:

```sql
SELECT COUNT(*)::float FROM (
  SELECT <vector_col> FROM <table>
  TABLESAMPLE SYSTEM(<sample_ratio_pct>)
) p
WHERE p.<vector_col> <dist_op> '<query_vector>' < <range_distance>
  [AND <other_filters>];
```

여기서 `sample_ratio_pct = sample_size / total_rows * 100`이다. **`TABLESAMPLE SYSTEM`은 페이지(블록) 단위 샘플링**이므로 블록 내 행들이 함께 뽑힌다. 벡터 데이터의 물리적 저장 순서와 거리 분포 사이에 상관이 있으면 이 블록 편향이 skew를 증폭할 수 있다. 이는 설계안 v3에서 예상하지 못했던 **새로운 가설의 축**을 제공한다(§VI에서 ablation으로 다룸).

**최종 추정 공식 (소스 L1232)**. 함수 반환값은 다음과 같이 스케일링된다.

```c
count_result = count_result / sample_ratio * 100;
// == count_result * total_rows / sample_size
```

즉 **분모가 `요청 sample_size`이지 `실제 반환된 샘플 행 수`가 아니다**. 이는 TABLESAMPLE SYSTEM이 블록 기반이라 실제 행 수가 요청과 다를 수 있음에도 구현은 이를 보정하지 않는다는 뜻이다. 또한 소스 L1228에는 **`count_result == 0이면 1로 치환`하는 clamp**가 있어 샘플 0 매칭 시 estimate가 `total_rows/sample_size`로 귀착된다. 우리 Python 재구현은 이 두 디테일을 정확히 재현해야 Exqutor와 동치가 된다.

**`true_cardinality` 원천 (소스 L1240~1268)**. Q-error 피드백의 기준이 되는 실측 카디널리티는 플래닝 단계의 별도 full scan이 아니라, **실행 직후(`ExecutorEnd`) `instrument->ntuples`** — 즉 해당 scan 노드가 실제로 생산한 행 수 — 로부터 얻는다. `SeqScan`, `IndexScan`, `BitmapHeapScan`에 대해 재귀적으로 planstate를 훑어 대상 테이블의 scan 노드를 찾고, 그 instrument의 튜플 카운트를 true cardinality로 쓴다. **즉 Q-error 측정은 "쿼리를 어차피 실행하니 무료"**이며 플래닝 오버헤드에 포함되지 않는다. `vector_table_size`는 `pg_class.reltuples`에서 로드(소스 L1286~)되므로 ANALYZE 기반 추정치이나, 실제 값과 보통 ±1% 이내로 차이가 미미하다.

**Adaptive 업데이트 수식**. 각 쿼리 실행 종료(`ExecutorEnd`) 시점에 `get_true_cardinality_for_vector_query()`로 실측 카디널리티를 얻고, Q-error를 `Qerrors_array`에 누적한다. `sample_update_cycle = 50` 주기마다 다음 규칙으로 샘플 크기를 갱신한다.

```
median_q = median(Qerrors_array[0..49])
grad     = α · (median_q − β) − (100 − α) · (sample_size / total_rows)
v_grad   = momentum · v_grad + lr · grad
lr       = lr · lr_λ
sample_size = sample_size + v_grad
```

소스에서 확인한 기본값은 `α = 50, β = 1.5, momentum = 0.9, lr_initial = 0.1, lr_λ = 0.99, sample_update_cycle = 50, sample_size_initial = 385`이다. 해석상 `α·(med_q − β)`는 "Q-error를 1.5에 수렴시키려는 힘"이고 `(100−α)·(sample/total)`은 "샘플 비율이 커질수록 브레이크를 거는 힘"이다. 두 힘의 가중치가 50:50으로 설정되어 있다.

**상태 저장소**. 갱신된 `sample_size, recent_qerrors, qerror_count, v_grad, learning_rate`는 `exqutor_qerror` 테이블에 `(table_name, column_name)` PK로 upsert된다. 세션이 끊겨도 다음 세션에서 `load_qerrors_array()`로 이어받는다. **즉 sampling 상태는 DB에 영구 저장되는 학습 상태이며, 실험 간 초기화가 필수다**.

### I.2 사전 실험 상태 증거 — `exqutor_qerror` 2행 해석

현재 서버 DB에는 BDAI 연구실 이전 실험자의 흔적 2행이 남아 있다.

| table | column | sample_size | qerror_count | v_grad | learning_rate |
|---|---|---|---|---|---|
| `partsupp_deep_10` | `ps_embedding` | **2754.74** | 1 | **601.46** | 0.0961 |
| `partsupp_deep_100` | `ps_embedding` | 385.00 | 3 | 0.00 | 0.1000 |

**Row 1 역산**. `v_grad = 0.9·v_prev + 0.1·grad`, 초기 `v_prev = 0`을 가정하면 `grad ≈ 6014.6`이다. 이를 수식에 대입하면 `50·(median_q − 1.5) ≈ 6014.6`, 즉 **이전 실험 50-쿼리 윈도우의 median Q-error ≈ 121.8**이 된다. `sample_size`가 초기 385에서 2754(7배)로 폭증하고 `lr_initial=0.1` → `0.0961`로 `0.99^4 ≈ 0.961`에 근접한 것을 보면, 최소 4회 이상의 갱신 주기가 돌았음을 알 수 있다. 

이 흔적은 **BDAI 랩 내부 실험에서도 `partsupp_deep_10`의 DEEP 96차원 벡터 위에서 Exqutor의 adaptive sampling이 수백 배 수준의 Q-error를 겪었다**는 1차 증거다. 이전 실험자가 어떤 쿼리 조건을 사용했는지는 기록에 남아 있지 않으나, 우리가 동일 테이블에서 skew-aware 실험을 재현하면 이 단서가 Motivation의 설득력을 강화한다.

**Row 2 해석**. `partsupp_deep_100`은 `sample_size` 초기값 385, `v_grad=0`, `qerror_count=3`로 초기화 직후 상태이며 3개 쿼리만 관찰된 채 세션이 끊긴 것으로 보인다. 이 테이블은 현재 DB에 존재하지 않아(sf100 전용) 실험 대상이 아니다.

**조치**: RQ1 실험 시작 전 clean slate 확보 필요 — `DELETE FROM exqutor_qerror;` + `pg_ctl restart`로 GUC/정적변수 초기화.

<div class="page-break"></div>

## II. 실험 통제 전략 결정

### II.1 왜 Python 재구현이 주력인가

서버의 모든 벡터 테이블(`customer_sift_10`, `part_wiki_10`, `partsupp_deep_*`)에는 이미 HNSW 인덱스가 붙어 있다. Exqutor의 `pgvector_set_baserel_rows_estimate_hook`은 HNSW 스캔 노드가 플랜에 포함되면 **ECQO 경로로 우선 분기**한다. 즉 기본 상태로는 Adaptive Sampling 경로 자체가 실행되지 않는다. 이 경로를 강제로 호출하려면 다음 중 하나가 필요하다.

| 옵션 | 방법 | 장점 | 단점 |
|---|---|---|---|
| A | `SET enable_indexscan=off; enable_indexonlyscan=off; enable_bitmapscan=off;` | 서버 그대로, 한 줄 설정 | HNSW가 플랜에 안 붙는지 `EXPLAIN`으로 1건 검증 필요 |
| B | HNSW 인덱스 DROP | 확실 | 5~31 GB 복구 비용, 팀 공용 환경이라 비권장 |
| C | 인덱스 없는 복사 테이블 생성 | 안전 | 15 GB 디스크 소모 |
| D | **Python 재구현** | 완전 통제, 결정론적 seed, 블록/무작위 샘플링 ablation 자유 | Exqutor 네이티브와의 동치 검증 필요 |

설계안 v3는 옵션 D를 "실험 환경" 섹션에 명시했다. 본 파이프라인도 **D를 주력**으로 하되, 옵션 A로 서버 네이티브 Adaptive Sampling을 한두 건 재현하여 Python 재구현이 서버 결과와 일치하는지 확인하는 **equivalence sanity check**를 Stage 4.5에서 수행한다.

### II.2 Python 재구현 책임 경계

Python 코드는 Exqutor 소스의 아래 로직을 1:1로 옮긴다. 샘플링 방식은 두 변형을 모두 지원하여 ablation이 가능하게 한다. **추정 공식·0-clamp·분모는 §I.1에서 확인한 Exqutor 구현과 bitwise 일치시켜야 equivalence check가 통과한다**.

```python
# exqutor_adaptive_sim.py — Exqutor bitwise 동치 재구현
ALPHA, BETA, MOMENTUM, LR_LAMBDA = 50.0, 1.5, 0.9, 0.99
SAMPLE_UPDATE_CYCLE = 50

def run_adaptive_session(dist_matrix, D_per_query, mode="bernoulli",
                          seed=0, rows_per_block=18):
    """
    dist_matrix: (Q=100, N) — query별 전체 N행에 대한 L2 거리 (Stage 2에서 사전 계산)
    D_per_query: (Q,)        — 각 query의 range threshold (Stage 3에서 선택도 역산)
    mode: "bernoulli"    — 행 단위 Bernoulli (블록 효과 제거, 수식 순수 검증용)
          "block_system" — PG TABLESAMPLE SYSTEM 블록 근사
    rows_per_block: Stage 1에서 측정된 partsupp_deep_10 평균 블록당 행 수 (~18)
    """
    rng = np.random.default_rng(seed)
    sample_size, lr, v_grad = 385.0, 0.1, 0.0
    total = dist_matrix.shape[1]
    q_errors = []

    for i in range(dist_matrix.shape[0]):
        # Exqutor L1190: sample_ratio = sample_size / total_rows * 100
        sample_ratio = sample_size / total  # fraction (0~1)

        if mode == "bernoulli":
            mask = rng.random(total) < sample_ratio
        elif mode == "block_system":
            # 블록 단위 선택 → 해당 블록의 모든 행을 mask에 포함
            n_blocks = (total + rows_per_block - 1) // rows_per_block
            block_mask = rng.random(n_blocks) < sample_ratio
            mask = np.repeat(block_mask, rows_per_block)[:total]

        # ====[ Exqutor 동치 핵심 4줄 ]====
        cnt = int((dist_matrix[i][mask] < D_per_query[i]).sum())
        if cnt == 0:                          # L1228: count==0 → 1 clamp
            cnt = 1
        est = cnt * total / sample_size       # L1232: 분모는 요청 sample_size (실제 mask.sum() 아님)
        true_card = int((dist_matrix[i] < D_per_query[i]).sum())  # instrument->ntuples 동치
        # =================================

        q_err = max(est / max(true_card, 1.0),
                    max(true_card, 1.0) / est)
        q_errors.append(q_err)

        # Exqutor L655~661: cycle 종료 시 momentum 업데이트
        if (i + 1) % SAMPLE_UPDATE_CYCLE == 0:
            med = float(np.median(q_errors[-SAMPLE_UPDATE_CYCLE:]))
            grad = ALPHA * (med - BETA) - (100.0 - ALPHA) * (sample_size / total)
            v_grad = MOMENTUM * v_grad + lr * grad
            lr *= LR_LAMBDA
            sample_size = max(sample_size + v_grad, 1.0)

    return dict(q_errors=q_errors, final_sample_size=sample_size,
                final_lr=lr, final_v_grad=v_grad)
```

**핵심 4줄의 의미**:
1. `cnt = (sample < D).sum()` — 서버의 `SELECT COUNT(*) FROM ... TABLESAMPLE`와 동치
2. `cnt == 0 → 1` — Exqutor L1228의 0-clamp. **빠뜨리면 극소 선택도에서 Q-error가 inf로 폭발**
3. `est = cnt × total / sample_size` — **분모가 `sample_size` (요청값)**. 실제 반환된 `mask.sum()` 아님. 이 차이가 equivalence check의 생사를 가름
4. `true_card = (dist < D).sum()` — 서버의 `instrument->ntuples`와 동치

*(추정 공식 편향 ablation을 추가하려면 `est_alt = cnt × total / mask.sum()`을 별도 컬럼으로 기록. 기본은 Exqutor 동치식.)*

이 뼈대는 §IV의 Stage 4에서 실험 entry point로 사용한다.

<div class="page-break"></div>

## III. 주력 데이터셋 및 Query 풀

### III.1 대상 테이블 선택

서버의 5개 벡터 테이블 중 RQ1 주력은 **`partsupp_deep_10`**으로 고정한다. 근거는 다음과 같다.

| 기준 | `customer_sift_10` | `part_wiki_10` | **`partsupp_deep_10`** | `partsupp_deep_sift_10` | `partsupp_deep_wiki_10` |
|---|---|---|---|---|---|
| 행수 | 1.5 M | 2.0 M | **8.0 M** | 8.0 M | 8.0 M |
| 차원 | 128 | 768 | **96** | 96 + 128 | 96 + 768 |
| 이전 실험 흔적 | 없음 | 없음 | **있음 (중요)** | 없음 | 없음 |
| 크기 | 2.3 GB | 23 GB | **15 GB** | 20 GB | 71 GB |
| 거리 계산 비용 (상대) | 1.0× | 6.0× | **0.75×** | 1.75× | 6.75× |
| RAM 적재 가능 (96d × 8M × 4B) | — | — | **≈ 3 GB** | — | — |

`partsupp_deep_10`은 (a) Row 1 흔적으로 **이미 Exqutor가 심한 Q-error를 겪었다는 증거가 있고**, (b) 96차원·8M이라는 실험 규모가 서버 RAM(1TB)에 전체 적재 가능(3 GB)하며, (c) 낮은 차원 덕에 거리 계산이 가장 빠르다. 설계안 v3의 일정(4/15~4/22 RQ1 완료)을 맞추려면 계산 비용이 결정적이다.

### III.2 Query Vector Pool — 완전 결정론적 선택

`partsupp_deep_10`에서 **재현 가능한 방식으로** query vector 100개를 추출한다. query 수 100은 설계안 v3의 "50~100" 중 상한을 택한 값이며, 이는 Exqutor의 `sample_update_cycle = 50` 기준 2 cycle 실행을 보장하여 **adaptive 갱신이 최소 1회는 관찰되도록** 하는 최소 요건이다.

**v1 초안의 `setseed(0.42) + ORDER BY random()` 방식은 폐기**했다. 이유는 (a) `setseed`는 세션 내부 상태이므로 여러 세션에 걸친 재현을 보장하려면 매번 동일 시퀀스가 필요하고, (b) `ORDER BY random()`은 같은 seed여도 테이블 물리 저장 순서가 VACUUM/INSERT로 변하면 결과 100개가 달라진다. 캡스톤 실험이 수 주에 걸쳐 진행되는 동안 이런 불안정성은 제거되어야 한다.

**대안**: Python `numpy.random.default_rng(seed=42)`로 `ps_partkey` 100개를 사전 결정한 뒤, 그 리스트를 SQL `WHERE ps_partkey IN (...)`로 조회한다. 이 방식은 서버 상태와 독립적이며 파이썬 난수 생성이 NumPy 기준 완전히 결정론적이다.

```python
# Stage 1 쿼리 풀 추출 — scripts/rq1_stage1_dump.py 내부
import numpy as np
rng = np.random.default_rng(seed=42)
# partsupp_deep_10 ps_partkey 분포: 1 ~ 2_000_000 (sf10 기준; 실측 후 확정)
key_ids = rng.choice(2_000_000, size=100, replace=False).tolist()
key_ids.sort()
```

```sql
SELECT ps_partkey, ps_suppkey, ps_embedding
FROM partsupp_deep_10
WHERE ps_partkey IN (<key_ids>)
ORDER BY ps_partkey;
```

**`ps_partkey` 분포는 Stage 1에서 실측**(`SELECT min, max, count FROM ...`) 후 확정한다. TPC-H partsupp는 `ps_partkey × ps_suppkey` 복합키이므로 `ps_partkey` 하나가 여러 행에 중복 — 첫 매칭만 사용하거나 `DISTINCT ON (ps_partkey)`로 처리한다.

추출된 100개 (query_id, ps_partkey, ps_suppkey, embedding)는 `cache/query_pool.parquet`에 저장하여 이후 Stage 2~5 전부에서 재사용한다.

### III.3 Skewness 프로파일링 — 고차원 거리 집중에 대응한 다중 지표

각 query vector $q_k$에 대해 `partsupp_deep_10` 서브셋(1M)과의 L2 거리 분포 $D_k = \{\|v_i - q_k\|_2 : i = 1, \dots, N\}$를 계산한다. `scipy.spatial.distance.cdist(vectors, queries)` 한 번의 호출로 1M × 100 × 96 연산이 일괄 처리된다(단일 코어 약 20~40초, 멀티코어 활용 시 5초 이내).

**Fisher γ 단독 사용의 한계**. 96차원은 고차원 거리 집중(distance concentration) 현상이 있는 구간이라 대다수 query에서 $\gamma_k$가 0 근처로 수렴할 가능성이 있다. 이 경우 설계안 v3의 `|γ| > 1` 임계값이 너무 희소해서 skew 그룹 자체가 비어버린다. Deep Review 결과 이 위험은 실측 이전에 제거할 수 없으므로 **4개 지표를 동시 기록**하고 posthoc 분석으로 어느 지표가 Q-error와 가장 강한 상관을 보이는지 판단한다.

| 지표 | 정의 | 근거 |
|---|---|---|
| **Fisher γ** | $\gamma_k = \mathbb{E}[(X-\mu)^3] / \sigma^3$ | 설계안 v3 원 정의 |
| **Log-Fisher γ** | $\gamma^{\log}_k = \text{Fisher}(\log D_k)$ | 고차원에서 거리 분포는 근사 Gaussian — log 변환으로 꼬리 강조 |
| **Tail ratio P99/P50** | $\rho_k = \text{quantile}(D_k, 0.99) / \text{quantile}(D_k, 0.50)$ | Heavy-tail 검출, robust |
| **Bowley skewness** | $b_k = (Q_{0.75} + Q_{0.25} - 2Q_{0.5}) / (Q_{0.75} - Q_{0.25})$ | Quartile 기반 robust skew, outlier 무관 |

`scipy.stats.skew(D_k, bias=False)`, `scipy.stats.skew(np.log(D_k + ε), bias=False)`, quantile 기반 수식은 numpy 원시 연산으로 직접 계산한다.

결과 테이블 `query_skew.parquet`의 스키마:

```
(query_id, ps_partkey, fisher_gamma, log_gamma, tail_ratio_p99_p50,
 bowley, mean, std, min, max, p5, p50, p95, p99, histogram_bins[50], histogram_counts[50])
```

**그룹 분류**. 4개 지표 각각에 대해 quartile bin을 구성하고, 각 quartile을 hypothesis의 skew 강도 그룹(symmetric/moderate/skewed/extreme)에 매핑한다. 이렇게 하면 데이터 분포에 의존하지 않고 **각 그룹에 자동으로 25%씩 배분**되어 Stage 4에서 통계적 비교가 보장된다. 동시에 설계안 v3의 고정 임계값(`|γ| < 0.5` 등)을 "절대 기준 버전"으로도 기록해두어, 두 분류 방식의 결과를 모두 보고한다.

| 그룹명 | Fisher γ 절대기준 (v3) | 지표별 quartile (v2 추가) |
|---|---|---|
| symmetric | $|\gamma| < 0.5$ | 각 지표의 Q1 (하위 25%) |
| moderate | $0.5 \leq |\gamma| < 1.0$ | Q2 |
| skewed | $1.0 \leq |\gamma| < 2.0$ | Q3 |
| extreme | $|\gamma| \geq 2.0$ | Q4 (상위 25%) |

**실패 시 대응**. 절대 기준으로 extreme 그룹이 10개 미만이면 quartile 기준 결과만 주 판단에 사용하고, 절대 기준은 "부록 분석"으로 남긴다.

### III.4 선택도 타겟 → 범위 거리 역산

각 query $q_k$에 대해 선택도 타겟 $s \in \{0.001, 0.01, 0.05, 0.10, 0.30, 0.50\}$를 달성하는 임계 거리 $D_{k,s}$는 $D_k$의 $s$-quantile로 계산한다.

$$D_{k,s} = \text{quantile}(D_k, s)$$

이렇게 하면 `COUNT(dist < D_{k,s}) / N = s`가 **정확히** 성립하므로, true cardinality는 $\lfloor s \cdot N \rfloor$로 사전 결정된다. 결과 `query_selectivity.parquet`: `(query_id, selectivity, D_target, true_cardinality)`.

<div class="page-break"></div>

## IV. 실험 파이프라인 — 7 단계

### Stage 0 — 환경 초기화

```bash
# 서버 세션에서
PG_BIN=/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/psql/bin
$PG_BIN/psql -h /tmp -p 55435 -U wns41559 -d wns41559 <<'SQL'
DELETE FROM exqutor_qerror;
SQL
$PG_BIN/pg_ctl restart -D /mnt/hdd0/home/capstone2026/vanilla_sf100 \
                       -l /mnt/hdd0/home/capstone2026/log/postgres.log
```

재시작이 필수인 이유: `pgvector_Exqutor.patch`의 `static float8 sample_size = 385`를 비롯한 정적 변수들이 프로세스 수명 동안 유지되므로 `DELETE`만으로는 완전한 초기화가 안 된다.

### Stage 1 — Query Pool + 벡터 덤프 (로컬/서버 하이브리드)

서버의 `partsupp_deep_10` 전체 벡터를 parquet로 덤프한 뒤 python 분석 머신으로 전송한다. 또는 분석 자체를 서버 내 tmux에서 실행한다.

```bash
# 서버 tmux capstone 세션 내
python3 scripts/rq1_stage1_dump.py \
    --table partsupp_deep_10 --col ps_embedding \
    --out /mnt/hdd0/home/capstone2026/cache/partsupp_deep_10.parquet \
    --query-seed 0.42 --n-query 100
```

산출물: `partsupp_deep_10.parquet` (96 × 8M float32 ≈ 3 GB), `query_pool.parquet` (100 × 96 float32 ≈ 40 KB).

### Stage 2 — Skewness Profiling

```bash
python3 scripts/rq1_stage2_skew.py \
    --data partsupp_deep_10.parquet --query query_pool.parquet \
    --out query_skew.parquet
```

산출물: 위 §III.3의 `query_skew.parquet`. 각 query에 대해 히스토그램도 함께 저장하여 시각화에 재사용.

### Stage 3 — Selectivity → D 역산

```bash
python3 scripts/rq1_stage3_selectivity.py \
    --data partsupp_deep_10.parquet --query query_pool.parquet \
    --selectivities 0.001,0.01,0.05,0.10,0.30,0.50 \
    --out query_selectivity.parquet
```

산출물: `query_selectivity.parquet` (600행 = 100 query × 6 선택도).

### Stage 4 — Adaptive Sampling 시뮬레이션 (Python 재구현)

```bash
python3 scripts/rq1_stage4_adaptive.py \
    --data partsupp_deep_10.parquet \
    --skew query_skew.parquet --sel query_selectivity.parquet \
    --mode bernoulli --seed 0 --repeats 5 \
    --out results/rq1_motivation/adaptive_bernoulli_seed0.parquet
```

각 (query × 선택도) 쌍에 대해 §II.2의 `run_adaptive_session`을 5회 반복 실행하여 **Q-error의 중앙값과 분포**를 기록한다. 샘플링 모드는 `bernoulli`(행 단위)와 `block_system`(TABLESAMPLE SYSTEM 근사) 두 가지를 모두 돌려 ablation한다.

산출물 스키마: `(query_id, selectivity, mode, seed, repeat, q_errors[100], final_sample_size, final_lr, final_v_grad)`.

### Stage 4.5 — 서버 네이티브 Equivalence Check

Python 재구현이 Exqutor 네이티브와 같은 결과를 내는지 1 query, 1 선택도로 대조한다.

```sql
-- 서버에서 enable_indexscan off로 샘플링 경로 강제
SET vector.sample_size = 385;
SET vector.update_sample_size = on;
SET enable_indexscan = off;
SET enable_indexonlyscan = off;
SET enable_bitmapscan = off;

-- 50개 쿼리를 연속 실행 (1 cycle) 후
SELECT * FROM exqutor_qerror WHERE table_name='partsupp_deep_10';
```

`recent_qerrors`와 Python 재구현 결과의 Q-error 시퀀스가 일치(±5% 이내)하면 동치성 확보. 불일치 시 TABLESAMPLE SYSTEM의 블록 크기 가정 혹은 추정 공식(`est = cnt/ratio` vs `est = cnt * total/sample_rows`)을 교차 확인한다.

### Stage 5 — 분석 + 시각화

```bash
python3 scripts/rq1_stage5_analyze.py \
    --in results/rq1_motivation/adaptive_*.parquet \
    --skew query_skew.parquet \
    --out-figs figures/rq1/
```

산출 Figure 목록:

| ID | 차트 | x축 | y축 | 그룹화 | 판단용도 |
|---|---|---|---|---|---|
| F1 | Skewness vs Q-error scatter | γ | median Q-error (5 repeat) | selectivity 색상 | **핵심 — 상관성 시각화** |
| F2 | Skew group × selectivity Q-error heatmap | selectivity | skew group | 셀 = median Q-error | 취약 구간 식별 |
| F3 | Skew group별 Q-error boxplot | skew group | Q-error (log scale) | selectivity facet | 통계 유의성 |
| F4 | Sample size 궤적 | cycle index | sample_size | skew group | Adaptive 수렴 거동 |
| F5 | Bernoulli vs Block Q-error 비교 | skew group | median Q-error | mode | **TABLESAMPLE ablation** |

### Stage 6 — 결과 저장 + 중간발표 소재 확정

`experiments/results/rq1_motivation/` 아래에 단계별 parquet + figure + 요약 `summary.md` 배치. summary.md는 RQ1 판단 기준(`|γ|>1` 그룹 Q-error가 `|γ|<0.5` 대비 2배↑)의 통과 여부와 주요 수치를 5줄 이내로 기록.

<div class="page-break"></div>

## V. 판단 기준 및 성공/실패 분기

### V.1 RQ1 주 판단 기준

설계안 v3 §III.1의 판단 기준을 그대로 적용한다.

> `|γ| > 1`인 query 그룹의 median Q-error가 `|γ| < 0.5` 그룹 대비 2배 이상이면 **통과** → RQ2/RQ3 진행.

통계적으로는 Mann-Whitney U test (양측, α=0.05)로 두 그룹의 Q-error 분포 차이 유의성을 함께 보고한다.

### V.2 보조 판단 기준

| ID | 기준 | 의미 |
|---|---|---|
| A | 선택도가 작을수록(예: 0.001) Q-error가 커지는 단조 경향 | extreme quantile에서 샘플링의 구조적 한계 |
| B | Block vs Bernoulli에서 block이 더 큰 Q-error를 보이는 skew 그룹 존재 | TABLESAMPLE SYSTEM이 skew 증폭 |
| C | `partsupp_deep_10`에서 최종 `sample_size`가 500 이상으로 수렴 | 이전 흔적(2754)과 정합 |

A, B, C 중 1개 이상이 성립하면 **Motivation의 설명력이 유의미하게 강화**된다. B는 설계안 v3에 없던 새 기여축이므로 최종 보고서에 별도 소절로 편입 후보.

### V.3 실패 대응

RQ1이 통과하지 못할 경우(주 판단 기준 미달):

1. **선택도 구간 재조정**: 극단 구간(0.0001, 0.8)을 추가해 skew에 민감한 꼬리 영역 탐색
2. **합성 skew query 보조 추가**: 자연 skew가 부족하면 query vector를 데이터 cluster center에서 의도적으로 멀리 배치하여 right-skew를 유도
3. **차원 교체**: `customer_sift_10` (128d SIFT)이나 `part_wiki_10` (768d WIKI)로 이전 — 고차원일수록 거리 분포가 집중되어 skew 측정이 민감
4. **Skew 정의 확장**: Fisher γ 외에 heavy-tail 지수(Hill estimator), kurtosis를 보조 지표로 추가

각각의 대응은 실험 1일 이내 추가 소요가 예상된다.

<div class="page-break"></div>

## VI. 리스크와 결정 대기 항목

### VI.1 리스크

| ID | 리스크 | 영향 | 완화책 |
|---|---|---|---|
| R1 | `partsupp_deep_10`의 자연 skew가 작음 | RQ1 failure | 합성 query 추가 (§V.3.2) |
| R2 | Python 재구현과 Exqutor 네이티브 불일치 | 결과 신뢰도 하락 | Stage 4.5 equivalence check 우선 수행 |
| R3 | TABLESAMPLE SYSTEM 블록 모델 근사 오차 | F5 ablation 해석 오류 | PG 블록 크기 8KB + 평균 row width 측정으로 정확히 반영, 또는 block 모델 없이 bernoulli만 보고 |
| R4 | Stage 1 parquet 덤프 중 디스크 부족 | 파이프라인 중단 | 서버 HDD 여유 2 TB 확인됨 (memory/reference_server.md), 3 GB 덤프는 안전 |
| R5 | 벡터 8M × 96d 전체 계산 시간 초과 | 일정 지연 | `partsupp_deep_10` 전체 vs 랜덤 1M 서브셋 선택 가능. 1M 서브셋은 통계적 의미는 유지하되 계산 10배 절약 |

### VI.2 결정 확정 (2026-04-14 16:40 Self-Review)

v2 개정 시점에 다음 결정들이 self-review로 확정되었다. 팀 피드백으로 번복 가능하나 기본값은 아래와 같다.

| ID | 결정 사항 | **확정값** | 근거 |
|---|---|---|---|
| **D1** | 대상 규모 | **1M 서브셋** | 단일 세션 완주 우선. Row 1 증거는 역산으로 이미 확보됐으므로 8M 재현 필요성 낮음. 필요 시 부록에서 8M로 재실행 |
| **D2** | Stage 4 반복 횟수 | **5회** | 통계 견고성과 계산 비용의 균형점. Mann-Whitney U test는 각 그룹 ≥ 10 sample이면 검정력 충분 |
| **D3** | Equivalence check (Stage 4.5) | **수행** | Python 재구현과 Exqutor 네이티브의 동치성 없으면 RQ1 결과 자체가 reviewer 공격 대상. 필수 |
| **D4** | Stage 1 실행 위치 | **서버 tmux** | 데이터 원천이 서버에 있고 3GB 덤프를 네트워크로 끌어올 이유 없음. tmux 세션 `capstone`에 이미 Python 환경 확인 필요 |
| **D5** | Block sample ablation | **포함** | `TABLESAMPLE SYSTEM`이 skew 증폭의 원인인지 분리 검증 가능. 설계안 v3에 없던 새 기여축이라 학술적 가치 높음 |
| D6 | 실험 실행 주체 | **조현빈 단독** | 4/14 단톡 공지로 팀 합의 완료 |
| **D7 (신규)** | Skewness 지표 | **4개 병기** (Fisher γ, log γ, tail ratio, Bowley) | Deep Review §III.3에서 96차원 거리 집중 위험 식별 |
| **D8 (신규)** | Query pool 생성 방식 | **Python RNG `ps_partkey` 사전 결정** | Deep Review에서 `setseed + random()` 재현성 불안정 발견 |
| **D9 (신규)** | 추정 공식 | **`est = cnt × total / sample_size`** (Exqutor 동치) | Deep Review §II.2 교정. `mask.sum()` 분모 아님. `cnt==0 → 1` clamp 포함 |

**공간 복잡도 검증** (1M 서브셋 기준):
- 원본 vector 캐시: 1M × 96 × 4B = **384 MB**
- 거리 행렬 $D_k \in \mathbb{R}^{100 \times 10^6}$: 100 × 1M × 4B = **400 MB**
- 합계 약 800 MB — 서버 1TB RAM의 0.08%, 여유 충분

**시간 복잡도 검증**:
- Stage 1 (덤프): 1M × 96 float을 psql binary COPY로 읽기 → 약 30 초
- Stage 2 (distance matrix + skew): cdist 1M × 100 × 96 ≈ 10^10 연산 → scipy 병렬 20~40 초 + skew 계산 5초
- Stage 3 (selectivity → D): quantile 계산 100 × 6 = 600건 → 1 초
- Stage 4 (bernoulli + block, 5회 반복 × 2 모드 = 10 run × 100 query cycle): 각 run당 수 초, 총 1 분 이내
- Stage 4.5 (서버 equivalence): 서버에서 50 쿼리 순차 실행 + qerror table 읽기 → 약 5 분 (HNSW off + SeqScan 강제로 쿼리당 5~10초)
- Stage 5 (시각화): 10 초

**총 예상 시간**: Stage 1~5 전체 10분 이내, Stage 4.5 equivalence 5분 추가. **단일 세션 내 완주 가능**.

<div class="page-break"></div>

## VII. 본 세션 직후 진행 순서 (원래 계획)

본 문서 v2 기준 바로 다음 실행 순서는 다음과 같다.

1. `scripts/rq1_stage1_dump.py` 작성 (1M 서브셋 덤프 + query pool 100개 ps_partkey 결정)
2. 서버 tmux `capstone`에서 Stage 1 실행 → `subset_1m.parquet` + `query_pool.parquet`
3. `scripts/rq1_stage2_skew.py` 작성 (4개 skew 지표 계산)
4. Stage 2 실행 → `query_skew.parquet` + 히스토그램 몇 개 육안 확인
5. 결과 육안 검증 — Fisher γ 분포가 0 근처에 뭉쳤는지, Bowley 기준 quartile이 의미있는지
6. 결과에 따라 Stage 3~5 진행 여부 판단

→ 1~5 모두 완료. 6은 본 문서 v2.1 §VIII에 반영.

<div class="page-break"></div>

## VIII. 실측 결과 및 교훈 (2026-04-14 17:00 KST 시점)

세부 수치와 분석 절차는 `experiments/results/rq1_motivation/summary.md`에 별도 기록.

### VIII.1 실행 개요

- Stage 1~5 전체를 단일 세션(약 3분)에 완주. 서버 tmux `capstone` 안에서 Python 3.10 + numpy/scipy/pandas/pyarrow/psycopg로 실행.
- 대상: `partsupp_deep_10` 의 1M 서브셋 (`DISTINCT ON (ps_partkey) WHERE ps_partkey BETWEEN 1 AND 1_000_000`).
- 결과는 `cache/rq1/` 아래 parquet로 저장되고, `subset_1m.parquet`(374 MB)을 제외한 나머지가 로컬 `experiments/results/rq1_motivation/`로 복사됨.

### VIII.2 가설 H1에 대한 판정 — 기각

4 skew 지표(Fisher γ, Log γ, Tail ratio P99/P50, Bowley) × 6 selectivity × 2 mode = 48 조합 전부에서 `|γ| > 1` 그룹의 median Q-error가 `|γ| < 0.5` 그룹 대비 2배 미만이다. 대부분 ratio ≈ 1.0이며 Mann-Whitney U 검정 p-value도 유의수준 0.05를 통과하지 못한다. Spearman 상관도 4 지표 × 6 selectivity의 24 조합에서 `|ρ|`가 모두 0.22 미만이다.

**결론**: `partsupp_deep_10`의 1M 서브셋에서는 Exqutor Adaptive Sampling의 Q-error가 거리 분포 skewness에 의존하지 않는다. H1이 주장한 설명 축이 실측에서 성립하지 않는다.

### VIII.3 그러나 두 개의 강력한 대체 신호

**신호 A — 선택도 효과**. Adaptive Sampling은 극소 선택도에서 구조적으로 취약하다.

| selectivity | bernoulli med_qe | block_system med_qe |
|---|---|---|
| 0.001 | 2.597 | 2.597 |
| 0.010 | 1.353 | 1.404 |
| 0.050 | 1.148 | 1.214 |
| 0.100 | 1.116 | 1.188 |
| 0.300 | 1.066 | 1.149 |
| 0.500 | 1.054 | 1.150 |

`s = 0.001`에서 median Q-error 2.6, max 8.2 (5 seed 평균). 이는 옵티마이저 플랜 선택에 영향을 주는 수준의 오차다.

**신호 B — Block sampling bias (새 기여축)**. `TABLESAMPLE SYSTEM`이 행 단위 Bernoulli 대비 Q-error를 일관되게 키운다. Wilcoxon signed-rank test 결과:

| s | median diff | p | block > bern query count |
|---|---|---|---|
| 0.050 | 0.057 | 0.001 | **59 / 100** |
| 0.100 | 0.053 | < 0.001 | **70 / 100** |
| 0.300 | 0.078 | < 0.001 | **83 / 100** |
| 0.500 | 0.102 | < 0.001 | **89 / 100** |

선택도가 클수록 블록 편향이 더 뚜렷해진다. Exqutor의 `estimate_cardinality_with_sampling()`이 `TABLESAMPLE SYSTEM`을 사용한다는 사실(§I.1에서 확인) 자체가 카디널리티 추정의 구조적 약점을 만든다는 해석이 가능하다. 이는 설계안 v3에서 예상하지 못한 축이다.

### VIII.4 RQ 구조 pivot — **Pivot A + C 병합 확정** (2026-04-14 17:35 KST)

**결정**: 팀 논의 결과 정확도 기준 최적 노선으로 **Pivot A (fair baseline 도구) + Pivot C 재설계 version (본선 기여)**을 확정. Pivot B(선택도 적응형 β)는 원래 연구 방향(Skew-Aware)과 직교하므로 본선에서 배제, 부차 기여로만 여지 남김. 상세 근거는 `experiments/results/rq1_motivation/summary.md` §III.3 참조.

**2단계 분할 전략**: 중간발표(4/28)는 Phase 1~5(환경 복구 + Pivot A 네이티브 + Local skew 지표 + 단일 dataset 부분 실증)까지, 최종보고서(6/11)는 Phase 6~8(Stratified Sampling 함수 구현 + 3 dataset × 20 seed × 1000 query 전면 ablation + Track B KDE-pilot)로 나눈다.

**정확도 기준 재배치**: 본 세션 결과는 원래 연구의 **전 단계 관찰**에 해당하며, Skew-Aware Stratified Sampling 자체의 정확도는 아직 측정된 바 없다. Pivot C의 "local skew 지표 + stratified 실제 구현"이 본선이며, Pivot A는 그 실험의 block bias 교란을 제거하는 baseline 인프라로 기능한다.

### VIII.4-legacy — 초기 후보 3안 (참고용 보관)

본 실험이 Deep 96차원 1M 서브셋 단일 테이블에서 나온 결과이므로, 즉시 방향을 틀기 전에 equivalence check와 다른 테이블 재현이 필요하다. 그 전제 위에서 세 가지 방향을 제시한다.

| 후보 | 내용 | 장점 | 단점 |
|---|---|---|---|
| **Pivot A** — Block → Bernoulli | `TABLESAMPLE BERNOULLI` 교체만으로 Q-error 개선을 주장 | 극단적으로 단순, 구현 1줄, 강력한 paired 결과 | 기여의 폭이 좁음, 기존 skew 중심 RQ2/RQ3 대부분 폐기 |
| **Pivot B** — 선택도 적응형 β | `s`별로 `β` 타겟을 바꿔 극소 선택도 수렴 가속 | Adaptive 루프 내부 미세 개선, 기존 구조 유지 | 기여의 독창성이 약함, 실질 Q-error 감소 폭 검증 필요 |
| **Pivot C** — Skew 재정의 확장 | Fisher γ 외 local modality, cluster density, PCA 스펙트럼 등 탐색 | 설계안 v3 골격 유지 | RQ1 반증을 회피하는 인상, 일정 리스크 큼 |

현 시점의 잠정 선호 순위는 **A > B > C**. A가 가장 실증적이고 단순하다. 다만 A를 채택할 경우 RQ2/RQ3의 타이틀이 "Distribution-aware stratified"에서 "Sampling scheme ablation"에 가까워질 수 있어 학술적 범주 조정이 필요하다.

### VIII.5 다음 세션 우선 작업 (재정렬)

1. **Stage 4.5 equivalence check** — 최우선. 서버 네이티브 Adaptive Sampling과 Python 재구현의 Q-error 시퀀스 일치 검증. 불일치하면 본 결과 자체가 뒤집힐 수 있음.
2. **다른 테이블 재현** — `customer_sift_10` (128d), `part_wiki_10` (768d)에서 동일 파이프라인 실행. Block bias와 선택도 효과의 차원·데이터 독립성 확인.
3. **시각화 Stage 5b** — matplotlib 설치 후 4~5개 figure 생성. 수치만으로는 학술 문서에 싣기 어려움.
4. **팀/사용자 논의** — Pivot A/B/C 중 선택. 늦어도 4/17까지 방향 결정 필요 (중간발표 4/28).
5. **sf10 원본(8M) 재현** — 1M 서브셋이 원본 대비 편향되지 않았는지 확인. 시간 여유 있으면.

### VIII.6 Stage 4.5 Phase 1 수학적 검증 결과 (2026-04-14 17:00~17:40 KST, 본 세션 이후 추가)

서버 현황 확인 중 **session_resume의 "Exqutor patched" 가정이 실제와 다르다는 사실**이 드러났다. 포트 55435의 PG는 `data_directory = /mnt/hdd0/home/capstone2026/vanilla_sf100`인 vanilla 인스턴스였으며, `SHOW vector.sample_size`가 `unrecognized configuration parameter` 오류를 반환했다. 4/14 04:57의 `build_custom.sh` 실행에서 pgvector 패치 빌드는 성공했으나 이어진 `pg_hint_plan` 설치 단계가 시스템 PG17 디렉토리 쓰기 권한 부족(`/usr/share/postgresql/17/extension/: Permission denied`)으로 실패(`===BUILD_FAIL===`)했고, 그 직후 Python 재구현 노선으로 전환하면서 네이티브 검증 경로가 사실상 차단되어 있었다.

이 블로커 때문에 원래 계획된 "서버 `SET vector.sample_size=385` → 50 query 실행 → `exqutor_qerror.recent_qerrors` 대조"는 수행할 수 없어, 사용자와 합의한 대체 경로인 **옵션 C(책상 위 수학적 검증)**를 진행했다. 세부 절차와 판정은 `experiments/results/rq1_motivation/equivalence_check.md` 참조. 요약하면 다음과 같다.

- **상수 축**: Python 8개 상수(α=50, β=1.5, momentum=0.9, lr_λ=0.99, lr_init=0.1, sample_size_init=385, sample_update_cycle=50, v_grad_init=0)가 Exqutor `src/vector.c` L442~455의 전역 초기값과 전부 일치.
- **수식 축**: 업데이트 수식(grad / v_grad / lr / sample_size 갱신 4줄)과 추정 공식(`est = cnt × total / sample_size`)이 Exqutor L650~663 및 L1180~1235와 수학적으로 동치.
- **제어 축**: Q-error circular buffer ↔ append-only 리스트는 메모리 레이아웃 차이일 뿐 매 cycle의 median 계산 대상 50개가 동일. 중앙값 알고리즘도 qsort+middle ↔ `np.median`으로 일치. 업데이트 타이밍(50, 100번째 query)도 동일.
- **방어 clamp 2건**: Python의 `sample_size<1`과 `true_card<1` 하한은 60 run 전체에서 **한 번도 발동하지 않음**(trajectory 최저값 382.729, q_errors에 inf/nan 0건). 즉 두 구현의 결과는 실측 수준에서 완전히 동일.
- **Bernoulli mode의 정체 판별**: Exqutor 소스에서 `TABLESAMPLE SYSTEM`만 호출되며 `BERNOULLI`는 단 한 번도 등장하지 않음. Python Stage 4의 `mode="bernoulli"`는 **Exqutor에 존재하지 않는 counterfactual 시뮬레이션**이며, 이 사실은 §VIII.3의 "Block sampling bias" 서술을 "SYSTEM 독점 사용 → Bernoulli 교체 시 3.8~9.1%p 개선 여지"로 재해석해야 함을 뜻한다. `summary.md` §II.5/§III.2/§III.3는 이에 맞게 업데이트 완료.

**판정**: Python 재구현 ≈ Exqutor 네이티브 (수학적 동치 검증 통과). 본 문서 §VIII.2~VIII.4의 결론(H1 기각, 선택도 효과, SYSTEM의 구조적 약점)을 구현 오류 의심 없이 Pivot 논의 근거로 사용 가능. 단, end-to-end 네이티브 재현(옵션 A)은 **다음 세션 과제**로 남으며 `build_custom.sh`의 `pg_hint_plan` 설치 타겟을 Exqutor prefix(`psql/`)로 수정하는 것이 첫 스텝이다. 옵션 A 완료 전까지 본 결과는 "1차 검증 통과, 2차 검증 대기" 상태로 간주한다.

## 부록 A — 파라미터 요약 (experiment_params.yaml 업데이트 대상)

| 항목 | 기존 값 | 변경 값 | 근거 |
|---|---|---|---|
| `datasets` | SIFT1M/GloVe/Deep10M/GIST (파일 경로 미정) | `partsupp_deep_10 @ server` (단일) | 서버 실상 반영, 4/28 일정 집중 |
| `query_count` | 100 | **100** (유지) | 2 cycle 보장 |
| `selectivity_ranges` | `[0.001, 0.01, 0.05, 0.10, 0.30, 0.50]` | **유지** | 판단 기준 변화 없음 |
| `skewness_bins` | symmetric/moderate/skewed/extreme | **유지** | 설계안 v3 정합 |
| `rq1_motivation.method` | `exqutor_adaptive_sampling` | `python_reimpl + bernoulli + block_system` | §II 결정 |
| `rq1_motivation.success_criterion` | `skewed group Q-error ≥ 2x symmetric group` | **유지** | 판단 기준 변화 없음 |
| `adaptive_params` (신규) | — | `α=50, β=1.5, momentum=0.9, lr=0.1, lr_λ=0.99, cycle=50, init_sample=385` | Exqutor 소스 추출 |
| `server_context` (신규) | — | `host=165.132.140.240, pg_port=55435, table=partsupp_deep_10 (8M × 96d)` | reference_server.md |

## 부록 B — 참고 지점

- **Exqutor 소스 경로**: `/mnt/hdd0/home/capstone2026/Exqutor/PostgreSQL/pgvector/patch/pgvector_Exqutor.patch` — `estimate_cardinality_with_sampling()` L1180~, `pgvector_set_baserel_rows_estimate_hook()` L693~, adaptive update L650~670
- **설계안 v3**: `plans/연구 설계안_20260403_162818.md` §III.1 RQ1 판단 기준 부분 복사 인용
- **서버 접속**: `memory/reference_server.md` §접속·§제약·§함정 3건
- **이전 실험 흔적 해석 원 계산**: 본 문서 §I.2
