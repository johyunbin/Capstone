# 06_부가측정 — α sweep · 저비용 근사 · 다중 조인 재학습

본실험을 보조하는 3종 부가 측정. 모두 DEEP+WIKI sf=10 (A2-Fig9 cell) 에서 수행.

| 하위 폴더 | file | 내용 |
|---|---:|---|
| `alpha_sweep/` | 16 | 결합 비율 α 를 0.3/0.4/0.5/0.6 로 바꿔 측정 (각 4 method). `est = α·est_B1 + (1−α)·est_method`. 시나리오 B (α=0.5 default) 안정성 확인. 원본의 `alpha_0.7/` 는 빈 디렉토리였음 |
| `cheap_approximation/` | 16 | 저비용 근사 4후보 (centroid_tuple · hash_bucketing · pca_preprocessing · iterative_refinement). 결합 best −7.37% anchor |
| `multi_join_restratification/` | 4 | 다중 조인 시 carry-over A vs 재학습 B 비교 |

- 구조: `{측정종류}/DEEP+WIKI_sf10/[변종]/{mode}/{파일}.json`
- α sweep 의 변종 폴더는 `alpha_0.3` ~ `alpha_0.6`

> α sweep 구조화(5/15) 이전의 stale loose 사본 4건은 `archive/미사용method_측정/06_부가측정/alpha_sweep/_stale_pre5_15_loose/` 에 격리.
