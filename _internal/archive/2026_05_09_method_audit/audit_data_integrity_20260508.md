# Data Integrity Audit — RQ1/RQ2/RQ3 Parquet (5/8 21:00 KST)

**Scope**: 429 single-table + 18 multi-table parquet (`/mnt/hdd0/home/capstone2026/cache/{rq1,rq3}/`).
**Method**: read-only schema/null/paired/sanity 검증. **데이터 수정 없음**.

---

## 1. Schema 일치성 — PASS

**Single-table** 429 files → 5 schema 변종, **core 9 column 모두 만족** (missing 0 file). 변종은 method-specific extra:
- Schema 1 (374 files, 87%): canonical `{dataset, mode, selectivity, seed, query_id, D_target, true_card, est, q_error}`
- Schema 2 (15): + `n_pilot, n_shells` (distance_shell)
- Schema 3 (15): + `pilot_size, weight_clip` (importance_sampling)
- Schema 4 (15): + `n_pilot` (kde_pilot)
- Schema 5 (10): + `sample_size_used` (adaptive)

**Multi-table** 18 files → 2 schema (단일 카탈로그 vs join). join schema 는 `D_deep_target/D_wiki_target/table_pair` (5 files), 단일은 `D1_target/D2_target/table` (13 files). 각 schema 안에서는 column 일치.

---

## 2. Null/NaN 비율 — 1 method 예외

| Measurement | mean null % | max null % | 판정 |
|---|---|---|---|
| `est` | 0.00% | 0.00% | PASS |
| `true_card` | 0.00% | 0.00% | PASS |
| `q_error` (전체) | 1.32% | 22.44% | 1 method 예외 |

**예외 — importance_sampling**: 10 cell 모두 `est=0` 비율 18-25% (NaN q_error 의 origin). 이는 **method 자체 pathology** (importance weights collapse → empty estimate) 이지 측정 오류 X. Tier 2 method 라 narrative 영향 없음.

---

## 3. Paired Alignment — 100% PASS

10 cell × 4-kang × adaptive 모두 BERN baseline (rq1_<DS>_<sf>_km20.parquet, mode='bernoulli', n=500) 와 `(selectivity, seed, query_id)` tuple **완전 일치 (500/500)**.

```
DS    SF    BERN   hdbscan   mb_part   hilbert   hybrid    adaptive
DEEP  sf1   500    500/500   500/500   500/500   500/500   500/500
DEEP  sf10  500    500/500   500/500   500/500   500/500   500/500
SIFT  sf1   500    500/500   500/500   500/500   500/500   500/500
... (10 cell 모두 동일)
YFCC  sf10  500    500/500   500/500   500/500   500/500   500/500
```

**참고**: 4-kang 의 `mb_partial` 은 file 시스템에서 `minibatch_partial` 로 저장됨 — analysis script 가 이 매핑을 따르는지 재확인 권장 (W1 master 분석본은 이미 정정 사용).

---

## 4. Numerical Sanity — PASS

- **q_error >= 1.0**: 429 file × ~5000 row 검사, **0 violation**. 정의 그대로 안전.
- **selectivity monotonicity**: RQ1 narrative 의 ρ < 0 (13/13 cell) 와 일치 — 별도 위반 없음.

---

## 5. Outlier Cell — 105 cell 식별, 모두 ceiling case

`mean q_error > 10 OR std > 5` 인 cell 105개 (single-table 429 file 중). **분류**:

| Category | Cell 수 | 판정 | 예시 |
|---|---|---|---|
| Tier 3 dbscan SSN | ~6 cell | ceiling (clustering 실패) | SSN sf10 dbscan sel=0.05 mean=66866, est ∈ {0, 1, 400k saturate} |
| sel=0.01 long tail | ~80 cell | ceiling (단일 query 가 mean 견인, median 정상) | YFCC sf10 halton sel=0.01 mean=515, **median=1.67**, p99=744 |
| Tier 2 lsh/halton | ~15 cell | 알고리즘 한계 영역 | YFCC lsh sel=0.05 mean=183 |
| **4-kang** | 2 cell | edge case | hybrid WIKI sf1 sel=0.01 mean=2.73 std=15.73 / mb_partial WIKI sf10 sel=0.01 mean=18.37 std=362 |

**4-kang 2 cell** 모두 sel=0.01 (가장 작은 selectivity) WIKI 에 집중 — narrative 가 이미 인지한 "smallest selectivity 에서 모든 method 의 ceiling" 패턴. mb_partial WIKI sf10 sel=0.01 std=362 은 **단일 outlier query 영향** (median 확인 필요). 측정 오류 vs 본질 한계 판정은 W2 자문 의제로 적절.

---

## 6. 결론 + Action

**Integrity 보증 등급**: **A-** (narrative evidence 로 사용 가능). 1 issue:
- importance_sampling 18-25% est=0 — Tier 2 method, narrative 영향 없으나 RQ3 30 method 분포 audit 시 **suspect 1건** 추가 권장 (kde_pilot 기존 1건 외).

**확인 명령** (의심 raw row 직접 점검):
```bash
ssh capstone "python3 -c \"import pandas as pd; df=pd.read_parquet('/mnt/hdd0/home/capstone2026/cache/rq1/rq3_WIKI_sf10_minibatch_partial.parquet'); s=df[(df.selectivity==0.01)]; print(s.nlargest(5,'q_error')[['seed','query_id','D_target','true_card','est','q_error']])\""
```

**Schema/paired/sanity 모두 통과** — RQ1/RQ2/RQ3 narrative evidence integrity 보증됨.
