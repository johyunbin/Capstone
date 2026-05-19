# _archive_미사용method — 본 분석 비사용 측정 (보존)

본 연구 분석은 정합성을 통과한 **16 method** 만 사용한다. 이 폴더는 그 외 측정을
**삭제하지 않고 보존**한 것이다 (재현·감사 목적).

| 분류 | 내용 |
|---|---|
| 16종 외 40 method | halton, sobol, lhs, hammersley, dbscan, lsh, reservoir, dense_rp, ccsketch 등. 정합성 위반(paper N=385 budget 위반)·중복·측정 미커버 사유 |
| CaseA (단독 대체) | paper Bernoulli 를 method 로 단독 대체한 negative control. 본 연구는 CaseB(결합)만 분석 |
| stale 사본 | α sweep 구조화 이전 loose 사본 (`06_부가측정/alpha_sweep/_stale_pre5_15_loose/`) |

- 하위 구조는 본 트랙(02~06)을 그대로 미러링 — `02_single_vector_본실험/`,
  `03_selectivity_sweep/`, `04_multi_vector_concat/`, `05_K_granularity/`, `06_부가측정/`
- 폐기 method 의 구체적 사유는 `_internal/METHOD_REGISTRY.md` 참조

> 발표 자료·최종 보고서에는 쓰지 않는다. 측정 portfolio 의 정직한 disclosure 차원에서 보존.
