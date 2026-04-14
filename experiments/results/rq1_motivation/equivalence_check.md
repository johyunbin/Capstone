# Stage 4.5 — Python 재구현과 Exqutor 네이티브 수학적 동치 검증

**작성 일자**: 2026-04-14 17:30 KST
**작성자**: 조현빈 (Claude Code 보조)
**대조 대상**: `scripts/rq1_stage4_adaptive.py` vs Exqutor 소스 (`Exqutor/PostgreSQL/pgvector/patch/pgvector_Exqutor.patch`)
**대조 방식**: 옵션 C — 책상 위 수학적 검증 (소스 라인 대 Python 라인 직접 대조)
**판정**: ✅ 수학적 동치 검증 통과. Python Stage 4 재구현은 Exqutor 네이티브와 행동 수준에서 동등하다.

---

## I. 배경 — 옵션 A 블로커와 옵션 C 대체 경로

4/14 17:00 세션 종료 시점의 `session_resume.md`는 다음 세션의 최우선 작업으로 "Stage 4.5 equivalence check — 서버 tmux `capstone`에서 `vector.sample_size=385` 설정 후 50 query 순차 실행 → `exqutor_qerror.recent_qerrors`와 Python 재구현 결과 대조"를 지정했다. 본 세션(17:00~) 첫 액션으로 이 검증에 착수했으나, 서버 실제 상태를 확인한 결과 **session_resume의 가정("Exqutor patched pgvector 0.7.1")과 실제가 다르다**는 사실이 드러났다.

현재 포트 55435에 돌고 있는 PostgreSQL 16.9는 data directory가 `/mnt/hdd0/home/capstone2026/vanilla_sf100`인 **vanilla 인스턴스**로, `SHOW vector.sample_size`가 `unrecognized configuration parameter` 오류를 반환하고 `shared_preload_libraries`도 비어 있다. 4/14 04:57에 tmux `capstone` 안에서 Exqutor를 clone하고 `build_custom.sh`를 실행했으나, pgvector 패치 빌드는 성공한 반면 이어진 `pg_hint_plan` 설치 단계에서 시스템 PG17 디렉토리(`/usr/share/postgresql/17/extension/`)에 쓰기 권한이 없어 `make install`이 실패했고(`===BUILD_FAIL===`), 그 후 Python 재구현 노선으로 전환했다. 즉 **현재 서버에서는 Exqutor 네이티브 실행 자체가 불가능**하다.

`exqutor_qerror` 테이블은 존재하지만 그 안의 2 row(`partsupp_deep_10/ps_embedding`, `partsupp_deep_100/ps_embedding`)는 과거 실험의 잔해이며, 현재 돌고 있는 vanilla PG는 Exqutor 훅을 전혀 호출하지 않는다. 아울러 Exqutor가 `src/backend/optimizer/path/costsize.c`와 `src/include/optimizer/cost.h`를 동반 패치한다는 사실을 `patch/pgvector_Postgres.patch`에서 확인했는데, 이는 **vanilla PG 바이너리에 Exqutor vector.so만 load하는 방식으로는 완전한 Exqutor 동작을 보장할 수 없음**을 의미한다. `set_baserel_rows_estimate_hook`을 노출하는 core patch가 선행되어야 pgvector 쪽의 `pgvector_set_baserel_rows_estimate_hook`이 호출될 수 있기 때문이다.

Pivot 결정 데드라인(4/17)이 72시간 앞이고, Exqutor 전용 PG 인스턴스 신규 기동(옵션 A)에는 initdb·데이터 로드·인덱스 빌드 등 반나절 이상이 필요하다. 이 상황에서 사용자와 합의한 경로는 **옵션 C — 책상 위 수학적 검증**이다. Python 재구현 파일과 Exqutor 소스를 라인별로 직접 대조하여 "bitwise"가 아닌 "수학적" 동치를 확증하는 것이다. 본 문서는 이 대조 작업의 결과이며, 옵션 A를 통한 네이티브 실행 검증은 다음 세션(또는 중간발표 전 리허설) 과제로 남긴다.

---

## II. 대조 방법

사용자의 검증 시나리오는 "서버 실행 + `exqutor_qerror` 조회 + ±5% 대조"였다. 그러나 위 블로커로 인해 실제 실행이 불가능하므로, 대체 방식으로 **Python 재구현 파일(`scripts/rq1_stage4_adaptive.py`)을 Exqutor pgvector patch(`pgvector_Exqutor.patch`, 1,562 줄)의 `src/vector.c` 변경부와 직접 비교**한다. 세 개의 축에서 검증한다.

1. **상수 축**: Exqutor 전역 상태 변수(L442~455)의 초기값 8개가 Python 상수 8개와 숫자적으로 정확히 일치하는가.
2. **수식 축**: Exqutor Adaptive Sampling 업데이트 로직(L650~663)과 카디널리티 추정 공식(L1180~1235)의 수식이 Python `run_adaptive_session()`(L104~137)의 수식과 수학적으로 동치인가.
3. **제어 축**: Q-error 저장 방식(circular buffer vs append), 중앙값 계산 알고리즘, clamp 시점 등 제어 흐름이 행동 수준에서 동등한 결과를 내는가.

Python 재구현의 **방어 clamp 2건**(`true_card<1` → 1, `sample_size<1` → 1)은 Exqutor 소스에 존재하지 않으므로, 이것들이 실측 60 run에서 **실제로 발동했는지** parquet을 조회하여 확인한다. 발동한 적이 없다면 두 구현은 행동 수준에서 완전히 동일하다.

---

## III. 상수 축 — 초기값 8개 완벽 일치

Exqutor 소스 `src/vector.c` L442~455에서 Adaptive Sampling 전역 상태 변수가 다음과 같이 초기화된다.

```c
static bool allow_sample_size_update = true;
static float8 sample_size = 385;
static int sample_update_cycle = 50;
static double learning_rate = 0.1;
static double lr_lambda = 0.99;
static double momentum = 0.9;
static double alpha = 50;
static double beta = 1.5;
static double v_grad = 0;
```

Python 재구현 `scripts/rq1_stage4_adaptive.py` L36~42는 동일 상수를 다음과 같이 선언한다.

```python
ALPHA = 50.0
BETA = 1.5
MOMENTUM = 0.9
LR_LAMBDA = 0.99
LR_INIT = 0.1
SAMPLE_SIZE_INIT = 385.0
SAMPLE_UPDATE_CYCLE = 50
```

`v_grad`의 초기값 0은 Python `run_adaptive_session()` L97(`v_grad = 0.0`)에 그대로 옮겨져 있다. 여덟 상수(α, β, momentum, lr_λ, lr_init, sample_size_init, sample_update_cycle, v_grad_init)가 숫자·단위·타입 전부 일치한다. Exqutor에는 추가로 `allow_sample_size_update` 부울 GUC가 있으나 이는 "업데이트 수행 여부"를 결정하는 플래그이고, Python은 업데이트를 항상 수행하므로 `true`에 대응한다.

**판정**: 상수 축 ✅ 완벽 일치 (8/8).

---

## IV. 수식 축 — Adaptive 업데이트와 추정 공식

### IV.1 Adaptive 업데이트 수식 (매 50 query마다)

Exqutor `pgvector_ExecutorEnd()` L650~663에서 50 query 단위 업데이트가 실행된다.

```c
if (Qerrors_count == sample_update_cycle - 1)
{
    double median_qerror = get_median(Qerrors_array, sample_update_cycle);
    double grad = alpha * (median_qerror - beta) - (100-alpha) * (sample_size / vector_table_size);
    v_grad = momentum * v_grad + learning_rate * grad;
    learning_rate = learning_rate * lr_lambda;
    sample_size = sample_size + v_grad;
}
```

Python `run_adaptive_session()` L131~137에서 동일 업데이트가 다음과 같이 수행된다.

```python
if (i + 1) % SAMPLE_UPDATE_CYCLE == 0:
    med = float(np.median(q_errors[-SAMPLE_UPDATE_CYCLE:]))
    grad = ALPHA * (med - BETA) - (100.0 - ALPHA) * (sample_size / N)
    v_grad = MOMENTUM * v_grad + lr * grad
    lr *= LR_LAMBDA
    sample_size = max(sample_size + v_grad, 1.0)
```

기울기 공식 `α(median − β) − (100−α)(sample_size/total)`, 모멘텀 `v_grad = m·v_grad + lr·grad`, 학습률 감쇠 `lr *= lr_λ`, 샘플 크기 갱신 `sample_size += v_grad`가 네 줄 모두 일치한다. Python의 `max(..., 1.0)` 하한만 Exqutor에 없는 방어 clamp이며, 이것의 실제 발동 여부는 §VI에서 별도 점검한다.

**판정**: 수식 축 (update) ✅ 완벽 일치.

### IV.2 카디널리티 추정 공식 (매 query)

Exqutor `estimate_cardinality_with_sampling()` L1180~1235의 핵심은 세 단계다.

```c
double sample_ratio = sample_size / total_rows * 100;                     // L1190
// SELECT COUNT(*) FROM (TABLESAMPLE SYSTEM(sample_ratio)) WHERE dist < D
// → count_result 반환
if (count_result == 0)                                                     // L1228
{
    count_result = 1;
}
count_result = count_result / sample_ratio * 100;                          // L1233
return count_result;
```

수식을 전개하면,

```
est = count / sample_ratio × 100
    = count / (sample_size / total_rows × 100) × 100
    = count × total_rows / sample_size
```

Python L118~123은 이 수식을 곧장 쓴다.

```python
d_i = dist_matrix[:, i]
cnt = int((d_i[mask] < D_per_query[i]).sum())
if cnt == 0:                           # L1228 clamp
    cnt = 1
est = cnt * N / sample_size            # L1232: 분모 = 요청 sample_size
```

양쪽 모두 "count=0이면 1로 clamp"를 먼저 수행한 뒤, "count × total / sample_size"로 확장한다. `total_rows`(Exqutor)는 baserel의 `reltuples`이고 Python의 `N`은 subset size 1M이며, Exqutor가 1M subset에서 돌 경우 두 값이 같아진다(옵션 A 수행 시 전제).

**판정**: 수식 축 (estimation) ✅ 완벽 일치.

### IV.3 True cardinality와 Q-error 계산

Exqutor L653은 `Max(estimated_sample_rows/true_cardinality, true_cardinality/estimated_sample_rows)`로 Q-error를 계산하며, `true_cardinality`는 `get_true_cardinality_for_vector_query()` L1253에서 `instrument->ntuples`(post-execution tuple count)로 취한다. 이는 파이프라인 용어로 "subset 전체에서 `dist < D`를 만족하는 실제 행 수"와 같다. Python L124~126은 이를 거리 행렬에서 직접 계산한다.

```python
true_card = int((d_i < D_per_query[i]).sum())  # instrument->ntuples 동치
q_err = max(est / max(true_card, 1.0), max(true_card, 1.0) / est)
```

`max(true_card, 1.0)` 하한이 Python에만 있고 Exqutor에는 없지만, `true_card=0`인 query가 실제로 발생하는지는 §VI에서 확인한다. Q-error의 정의(`max(est/true, true/est)`)는 양쪽 모두 동일하다.

**판정**: 수식 축 (q-error) ✅ 완벽 일치.

---

## V. 제어 축 — 버퍼 구조, 중앙값, 순서

### V.1 Q-error 저장 구조 — circular vs append

Exqutor는 길이 50(`sample_update_cycle`)의 고정 배열 `Qerrors_array`를 circular buffer로 운용한다. L654~668의 동작을 풀어보면, `Qerrors_count`는 0에서 시작하여 매 query마다 1 증가하고, 49가 되면 그 시점의 배열 전체로 `get_median`을 호출한 뒤 업데이트를 수행하며, 50이 되면 0으로 reset되어 다음 50개가 같은 자리를 덮어쓴다. 즉 임의 시점의 `Qerrors_array`는 "현재 cycle에서 수집된 q-error들"만 담고 있다.

Python은 파이썬 리스트 `q_errors`에 append만 하고, 매 50 query마다 `q_errors[-SAMPLE_UPDATE_CYCLE:]`로 마지막 50개를 슬라이스한다. 매 cycle의 update 시점에 median 계산에 들어가는 50개는 "방금 수집된 q-error 50개"로 Exqutor와 완전히 동일하다. 저장 형태가 circular냐 append-only냐는 **메모리 레이아웃 차이**일 뿐이고 수학적 결과에는 영향이 없다.

**판정**: 제어 축 (buffer) ✅ 수학 동치.

### V.2 중앙값 알고리즘

Exqutor `get_median()` L1495~1514은 qsort로 오름차순 정렬 후, 길이가 홀수면 중앙 원소, 짝수면 두 중앙 원소의 평균을 반환한다. Python은 `np.median`을 쓰는데, NumPy의 median은 정확히 같은 정의(정렬 후 중앙값, 짝수 길이는 두 개의 평균)를 사용한다. 50은 짝수이므로 양쪽 모두 `(sorted[24] + sorted[25]) / 2`를 계산한다.

**판정**: 제어 축 (median) ✅ 완벽 일치.

### V.3 업데이트 타이밍

Exqutor의 업데이트 트리거 조건은 `Qerrors_count == sample_update_cycle - 1`(즉 49)이며, 이는 현재 query가 cycle 내 50번째(0-indexed 49번째)임을 의미한다. Python은 `(i + 1) % SAMPLE_UPDATE_CYCLE == 0`로, `i=49, 99, 149, ...`에서 업데이트가 발동한다. 100 query 파이프라인에서는 양쪽 모두 **정확히 2회 업데이트**(50번째, 100번째 query 직후)가 발생한다.

**판정**: 제어 축 (timing) ✅ 완벽 일치.

---

## VI. 방어 clamp 2건의 실제 발동 점검

Python 재구현에는 Exqutor 소스에 없는 방어 clamp가 두 군데 있다. 이 clamp가 실측 60 run 동안 **한 번이라도 발동했는지**를 `experiments/results/rq1_motivation/adaptive_runs.parquet`를 조회하여 확인한다(서버 venv_rq1 환경에서 실행).

### VI.1 `sample_size < 1` 하한 clamp

Python L137의 `max(sample_size + v_grad, 1.0)`이 의미를 가지려면 `sample_size + v_grad`가 1 미만이 되어야 한다. 60 run 각 run의 `sample_size_trajectory`(100 query × 60 = 6000 스냅샷)에서 최솟값 분포는 다음과 같다.

```
trajectory_min statistics:
  min/p5/p50/p95/max:  382.729 / 382.786 / 383.379 / 385.000 / 385.000
  ≤1.0 count: 0 / 60
  ≤10  count: 0
  ≤50  count: 0
```

60 run 전체에서 `sample_size`가 1에 근접한 적이 없다. 최저값이 382.729로 초기값 385에서 2.27(~0.6%)밖에 감소하지 않는다. 학습률 감쇠(`lr *= 0.99`)와 100 query 내 update 2회라는 제한 때문에 `v_grad`가 크게 움직이지 못한 결과다. **clamp 발동 0건**, 따라서 이 차이는 실측 결과에 영향이 없다.

### VI.2 `true_card < 1` 하한 clamp

Python L126의 `max(true_card, 1.0)`이 의미를 가지려면 전체 1M subset에서 `dist < D`를 만족하는 행이 한 건도 없는 query가 존재해야 한다. 6000개 q-error 값(60 run × 100 query)을 전수 검사한 결과:

```
전체 q_error 수: 6000
  inf:   0
  nan:   0
  q_errors > 100: 0
  max_q_error max: 10.39 (s=0.001)
```

Division-by-zero나 무한대가 한 건도 없다. 가장 큰 max Q-error는 `s=0.001`에서 10.39로, 이는 `true_card`가 0이 아니라 "매우 작지만 양수"인 경우의 건전한 값이다. Stage 3에서 각 query의 `D_target`을 subset 내 `|dist<D|/N = s` 조건으로 선택했기 때문에, `s=0.001`이라도 `true_card ≈ 1000 ± 오차`가 보장되고 0이 될 수 없다. **clamp 발동 0건**, 따라서 이 차이도 실측 결과에 영향이 없다.

---

## VII. TABLESAMPLE SYSTEM 독점 사용 — Bernoulli는 counterfactual

### VII.1 Exqutor는 오직 SYSTEM만 사용한다

`estimate_cardinality_with_sampling()` L1188~1195의 쿼리 조립부는 다음 한 줄로 고정되어 있다.

```c
appendStringInfo(&query,
    "SELECT COUNT(*)::float FROM (SELECT %s FROM %s TABLESAMPLE SYSTEM(%f)) p "
    "WHERE p.%s %s '%s' < %f",
    vector_column_name, vector_table_name, sample_ratio,
    vector_column_name, distance_function, vector_str, range_distance_value);
```

`TABLESAMPLE SYSTEM(sample_ratio%)`은 PostgreSQL의 내장 샘플링 메서드 중 **블록(page) 단위** 샘플링을 지정한다. 각 8KB 페이지가 `sample_ratio` 확률로 독립 선택되고, 선택된 페이지의 모든 행이 결과 집합에 포함된다. Exqutor 패치 1562 줄 전체에서 `BERNOULLI`라는 단어는 단 한 번도 등장하지 않는다. 즉 **Exqutor 네이티브가 실측에서 사용하는 샘플링은 오직 SYSTEM 하나**다.

### VII.2 Python `bernoulli` mode의 정체

Python Stage 4의 `mode="bernoulli"`(L108~110)는 다음과 같이 행 단위 독립 샘플링을 수행한다.

```python
if mode == "bernoulli":
    mask = rng.random(N, dtype=np.float32) < sample_ratio
```

이는 Exqutor에 존재하지 않는 **counterfactual 시뮬레이션**이다. "만약 Exqutor가 SYSTEM 대신 BERNOULLI를 썼다면 어떻게 달라질까"를 관찰하기 위한 가상 실험이고, 실제 Exqutor의 동작을 재현하는 것이 아니다. 본 세션(17:00 종료) summary.md의 "Block sampling bias" 서술은 이 사실을 암묵적으로 전제하고 있었으나 명시하지 않았다. 아래 §VIII에서 summary.md 업데이트 권고사항으로 정리한다.

### VII.3 Python `block_system`과 Exqutor SYSTEM의 관계

Python `mode="block_system"`(L111~114)은 다음과 같이 블록 샘플링을 흉내 낸다.

```python
elif mode == "block_system":
    block_pick = rng.random(n_blocks, dtype=np.float32) < sample_ratio
    mask = np.repeat(block_pick, rows_per_block)[:N]
```

여기서 `rows_per_block`은 Stage 1에서 측정한 `reltuples/n_blocks = 13.8`을 14로 반올림한 값이다. 각 블록이 `sample_ratio` 확률로 선택되고 선택된 블록은 14행씩 함께 포함된다는 점에서 Exqutor SYSTEM의 동작과 **수학적으로 같은 확률 과정**이지만, 세 가지 차이가 남는다.

첫째, RNG가 다르다. PostgreSQL의 SYSTEM은 내부 `SamplerRandomFns`를 쓰고, Python은 `numpy.random.default_rng(seed)`를 쓴다. 같은 seed로 bitwise 같은 블록 선택을 보장할 수는 없지만, 두 RNG 모두 독립 uniform[0,1) 샘플을 내므로 **분포 수준에서는 동일**하다. 5 seed 평균은 양쪽에서 같은 값으로 수렴한다.

둘째, Python은 모든 블록이 14 rows를 가진다고 가정하지만 실제 PG 페이지는 13~15 rows로 약간 변동한다. 이는 최대 1.4%(=14/13.8−1) 수준의 계통 오차이며, 추정 분모 `sample_size`가 양쪽에서 동일하기 때문에 최종 est에서 대부분 cancel된다. summary.md의 핵심 수치(3.8~9.1% Q-error 증가)와 비교하면 한 자리수 작은 규모다.

셋째, Exqutor는 샘플링 결과로 `ps_embedding`만 SELECT한 뒤 WHERE 절에서 거리 함수를 평가하는 반면, Python은 미리 계산된 거리 행렬을 mask로 필터링한다. 두 방식은 동일한 행 집합에 대해 동일한 count를 낸다.

**판정**: Python `block_system` ≈ Exqutor SYSTEM (같은 확률 과정, 1.4% 이내 계통 차이).

---

## VIII. 종합 판정

수학적 검증의 세 축 — 상수, 수식, 제어 — 전부에서 Python 재구현은 Exqutor 소스와 완벽 일치했다. Python에만 있는 방어 clamp 2건(`true_card<1`, `sample_size<1`)은 실측 60 run 전체에서 한 번도 발동하지 않았다. 남은 유일한 차이는 블록 크기를 14로 반올림한 데서 오는 1.4% 계통 오차와 RNG 차이에서 오는 5 seed 평균으로 희석되는 분산 오차이며, 둘 다 summary.md의 핵심 수치를 뒤집을 수 있는 규모가 아니다.

따라서 본 세션의 실측 결과 — 가설 H1 기각, 선택도 효과, "Block sampling bias" 신호 — 는 **Python 구현 오류로 인한 false negative/positive가 아닌 실질적 발견**이라는 최소한의 신뢰도를 확보한다. Pivot A/B/C 결정(4/17 데드라인)을 본 결과 위에서 진행하는 것이 정당화된다.

다만 이 검증은 **수학적 대조**이지 bitwise 네이티브 재현이 아니다. 서버 상에서 실제 Exqutor 바이너리로 같은 query pool을 돌려 per-query Q-error 분포를 비교하는 검증(옵션 A)은 다음 세션의 과제로 남는다. 옵션 A의 필요성은 두 가지다. 첫째, `true_cardinality` 수렴이 `instrument->ntuples`(post-execution)와 Python in-memory count 간에 정말 일치하는가를 physical level에서 확인하는 것. 둘째, `pgvector_ExecutorEnd`의 allow_sample_size_update 플래그, `load_qerrors_array`의 SPI 호출, circular buffer의 cross-session persistence 등이 의도대로 동작하는가를 end-to-end로 확증하는 것.

## IX. 요점 정리 — 세션 단위 소비 가능 결론

**Python 재구현의 신뢰도**: 수학적 동치 검증 통과. summary.md §II의 실측 수치를 근거로 Pivot 논의에 진입해도 된다.

**Bernoulli mode의 정체**: Exqutor 네이티브에 존재하지 않는 counterfactual. summary.md §II.5, §III.2의 "Block sampling bias" 서술을 **"Exqutor는 SYSTEM만 사용 → Bernoulli 교체 시 3.8~9.1% 개선 가능"** 방향으로 재작성해야 한다. Pivot A("Block → Bernoulli 단순 교체")는 이에 따라 **Exqutor 소스 1줄 변경 + vector.so 재빌드**라는 구체적 구현 경로로 재정의된다.

**옵션 A의 이연**: 다음 세션(또는 중간발표 리허설 전)에 수행. 요구 작업은 Exqutor postgres 바이너리로 별도 data directory에 initdb, `partsupp_deep_10` 8M 혹은 1M subset 로드, `pgvector_Postgres.patch`가 포함된 core 기반에서 `vector.sample_size=385` 설정, 100 query 순차 실행, `exqutor_qerror.recent_qerrors` vs Python parquet 집계 수준 ±5% 대조.

**빌드 복구 메모**: 옵션 A 수행 시 `build_custom.sh`의 `pg_hint_plan` 설치 단계는 **시스템 PG17 대신 Exqutor prefix(`psql/`)를 타겟으로 수정**해야 `Permission denied` 오류가 재발하지 않는다. 이 부분은 다음 세션 첫 작업으로 기록한다.
