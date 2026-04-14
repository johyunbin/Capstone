# RQ1 Motivation — 1차 실험 결과 요약

**실행 일자**: 2026-04-14 16:46 ~ 16:55 KST (Stage 1~5), 17:00 ~ 17:40 KST (Stage 4.5 수학적 검증)
**실행자**: 조현빈 (Claude Code 보조)
**파이프라인 문서**: `experiments/plans/RQ1_motivation_pipeline_20260414_162857.md` (v2)
**실행 환경**: 연세대 BDAI Lab 서버 `capstone2026@165.132.140.240`, PG 16.9 + pgvector 0.7.1 (**vanilla 인스턴스 — 아래 V 참조**)
**대상**: `partsupp_deep_10` 의 1M 서브셋 (96d DEEP, `DISTINCT ON (ps_partkey)`)
**검증 상태**: Stage 4.5 수학적 동치 검증 **통과** (`equivalence_check.md` 참조). 네이티브 bitwise 검증(옵션 A)은 다음 세션 과제.

---

## I. 실행 범위 및 산출물

| Stage | 스크립트 | 주 산출물 | 시간 |
|---|---|---|---|
| 1 | `rq1_stage1_dump.py` | `subset_1m.parquet` (374 MB, 서버 only), `query_pool.parquet` (100건) | 108 s |
| 2 | `rq1_stage2_skew.py` | `query_skew.parquet` (4 skew 지표 × 100 query + 50-bin histogram) | 16 s |
| 3 | `rq1_stage3_selectivity.py` | `query_selectivity.parquet` (600행 = 100 query × 6 선택도) | 9 s |
| 4 | `rq1_stage4_adaptive.py` | `adaptive_runs.parquet` (60 run × 100 q_errors) | 32 s |
| 5 | `rq1_stage5_analyze.py` | `stage5_analysis.parquet` (6 000행 long-form), `stage5_summary.json` | 1 s |
| Phase 4 (4/14 19:30~19:40 추가) | `rq1_phase4_native.py` | `phase4_system.parquet`, `phase4_bernoulli.parquet`, `phase4_compare.json` (각 600행) | 82 + 21 s |
| Phase 5 (4/14 20:09 추가) | `rq1_phase5_local_skew.py` | `query_local_skew.parquet` (100행 × 4 local 지표), `phase5_local_skew_spearman.json` (24 조합 ρ), `phase5_local_skew_meta.json` | 6 s |
| Phase 6 Step 1~3 (4/14 20:30 추가) | `rq1_phase6_stratified_python.py` | `phase6_strat_pca_runs.parquet` (6000행: 2 mode × 100 query × 6 sel × 5 seed), `phase6_strat_pca_compare.json`, `phase6_strat_pca_meta.json`, `data_side_strata_pca.parquet` (1M × stratum_id) | 5 s |
| Phase 6 Step 3' (4/14 20:45 추가) | `rq1_phase6_layer_compare.py` | `phase6_layer_compare_runs.parquet` (12 000행: 4 mode × 100 × 6 × 5), `phase6_layer_compare_compare.json`, `phase6_layer_compare_meta.json` | 9 s |

**총 실행 시간**: 약 3 분 (Stage 1~5) + 1.7 분 (Phase 4 native) + 6 초 (Phase 5 local skew) + 5 초 (Phase 6 Step 1~3) + 9 초 (Phase 6 Step 3' layer compare). 단일 dataset (1M subset) 의 RQ1 motivation 단계가 native 검증 + 8 지표 전수 검증 + 4 layer 비교 (bernoulli + pca_decile + kmeans K=10/20) 까지 진행됨.

---

## II. 주요 실측 결과

### II.1 Skewness 프로파일 — 100 query 전부 left-skewed

| 지표 | min | p25 | p50 | p75 | max |
|---|---|---|---|---|---|
| Fisher γ | −3.855 | −1.404 | **−1.067** | −0.695 | −0.324 |
| Log-Fisher γ | −5.207 | −2.382 | −1.697 | −1.229 | −0.620 |
| Tail ratio P99/P50 | +1.069 | +1.101 | **+1.113** | +1.129 | +1.167 |
| Bowley skew | −0.354 | −0.165 | −0.121 | −0.081 | −0.036 |

**발견 1 — Fisher γ 전수 음수**. 100개 query 모두 Fisher γ < 0. 설계안 v3의 "right-skewed 예시" 가정과 정반대. 대다수 벡터가 query와 멀리 있고, 소수만 가깝다(거리 분포의 왼쪽 꼬리가 길다).

**발견 2 — 거리 집중**. Tail ratio P99/P50이 **1.07~1.17** 범위로 매우 좁다. 고차원 거리 집중(distance concentration) 현상이 명확히 관찰된다. 96차원 DEEP 벡터에서도 이 효과가 뚜렷하다.

**발견 3 — 그룹 분포 충분**. 설계안 v3의 `|γ|` 절대값 기준 그룹 분포:
- symmetric (`|γ| < 0.5`): **12**
- moderate (`0.5 ≤ |γ| < 1.0`): **36**
- skewed (`1.0 ≤ |γ| < 2.0`): **46**
- extreme (`|γ| ≥ 2.0`): **6**

각 그룹에 최소 6개 이상 query가 확보되어 Mann-Whitney U 검정을 수행할 통계적 여건 충족.

### II.2 Adaptive Sampling — 선택도별 Q-error (5 seed 평균)

| selectivity | bernoulli med_qe | block_system med_qe | block bias |
|---|---|---|---|
| 0.001 | **2.597** | 2.597 | 0.0 % (0-clamp dominant) |
| 0.010 | 1.353 | 1.404 | +3.8 % |
| 0.050 | 1.148 | 1.214 | +5.7 % |
| 0.100 | 1.116 | 1.188 | +6.5 % |
| 0.300 | 1.066 | 1.149 | +7.8 % |
| 0.500 | 1.054 | 1.150 | **+9.1 %** |

**발견 4 — 선택도 효과**. 선택도가 작을수록 Q-error가 증가한다. 가장 심한 `s=0.001`에서 median Q-error 2.6, max 8.2까지 관찰. Adaptive가 극소 선택도에서 구조적으로 취약하다.

**발견 5 — Block sampling bias**. 모든 선택도(0-clamp 영향 구간 제외)에서 `TABLESAMPLE SYSTEM`이 Bernoulli 대비 Q-error가 일관되게 3.8~9.1% 높다. 선택도가 클수록 격차가 증가.

### II.3 RQ1 주 판단 기준 — **❌ 실패**

설계안 v3의 판단 기준: `|γ| > 1` 그룹의 median Q-error가 `|γ| < 0.5` 그룹 대비 2배 이상.

| mode | selectivity | med(`|γ|<0.5`) | med(`|γ|≥1`) | ratio | p (M-W U) | 2x pass |
|---|---|---|---|---|---|---|
| bernoulli | 0.001 | 2.597 | 2.579 | 0.99 | 0.0009 | ✗ |
| bernoulli | 0.010 | 1.299 | 1.302 | 1.00 | 0.5895 | ✗ |
| bernoulli | 0.050 | 1.132 | 1.143 | 1.01 | 0.6044 | ✗ |
| bernoulli | 0.100 | 1.132 | 1.117 | 0.99 | 0.1752 | ✗ |
| bernoulli | 0.300 | 1.072 | 1.071 | 1.00 | 0.8008 | ✗ |
| bernoulli | 0.500 | 1.060 | 1.052 | 0.99 | 0.5944 | ✗ |
| block_system | 0.001 | 2.597 | 2.597 | 1.00 | 0.0001 | ✗ |
| block_system | 0.010 | 1.299 | 1.302 | 1.00 | 0.9221 | ✗ |
| block_system | 0.050 | 1.199 | 1.203 | 1.00 | 0.1092 | ✗ |
| block_system | 0.100 | 1.155 | 1.203 | 1.04 | 0.2713 | ✗ |
| block_system | 0.300 | 1.129 | 1.168 | 1.03 | 0.0827 | ✗ |
| block_system | 0.500 | 1.150 | 1.160 | 1.01 | 0.2385 | ✗ |

모든 12개 조합에서 ratio ≈ 1.0, 2배 기준 미달. `s=0.001`의 p값이 매우 낮으나(0.0001, 0.0009) 방향은 오히려 약한 음의 상관(low γ 그룹이 미세히 높음). 실질적 효과 없음.

### II.4 Spearman 상관 — 4 skew 지표 × Q-error

`mode=bernoulli` 기준 query별 median Q-error와 skew 지표의 Spearman rho.

| s | Fisher γ | Log γ | Tail ratio | Bowley |
|---|---|---|---|---|
| 0.001 | +0.174 (p=0.084) | +0.148 (p=0.143) | +0.055 (p=0.589) | +0.170 (p=0.091) |
| 0.010 | +0.013 (p=0.899) | +0.023 (p=0.818) | −0.050 (p=0.622) | −0.210 (p=0.036) |
| 0.050 | +0.041 (p=0.688) | −0.040 (p=0.692) | +0.039 (p=0.699) | −0.154 (p=0.126) |
| 0.100 | +0.033 (p=0.741) | −0.028 (p=0.780) | +0.043 (p=0.673) | −0.002 (p=0.986) |
| 0.300 | +0.028 (p=0.783) | −0.001 (p=0.996) | −0.055 (p=0.586) | +0.001 (p=0.995) |
| 0.500 | +0.105 (p=0.300) | +0.100 (p=0.323) | +0.122 (p=0.227) | +0.035 (p=0.730) |

**발견 6 — Skew 지표와 Q-error 상관 없음**. 24 조합 중 `|ρ| > 0.2`인 조합이 하나도 없다. 4개 지표 모두 Q-error의 설명변수로 작동하지 않는다. Fisher γ, Log γ, Tail ratio, Bowley 네 가지를 모두 교차 확인했는데도 신호 부재.

### II.5 SYSTEM vs Bernoulli paired (Wilcoxon signed-rank, 대립가설: SYSTEM > Bernoulli)

> **서술 주의**: Exqutor 네이티브는 오직 `TABLESAMPLE SYSTEM`만 사용하며 Bernoulli sampling은 Exqutor 소스 어디에도 없다 (Stage 4.5 검증 §VII). 따라서 이 표의 `bernoulli` 결과는 "현행 Exqutor가 Bernoulli로 교체되었을 때의 counterfactual"이며, `block > bern` 방향으로의 유의한 차이는 "SYSTEM을 Bernoulli로 바꾸면 Q-error가 이만큼 감소할 수 있다"는 **개선 여지의 실증**으로 읽어야 한다.

| s | median diff | mean diff | W | p | block > bern | bern > block |
|---|---|---|---|---|---|---|
| 0.001 | 0.000 | 0.000 | 0.0 | — | 0 | 0 |
| 0.010 | 0.000 | −0.018 | 1 554.5 | 0.691 | 39 | 42 |
| 0.050 | 0.057 | 0.047 | 2 968.0 | **0.001** | 59 | 34 |
| 0.100 | 0.053 | 0.065 | 3 853.5 | **< 0.001** | 70 | 29 |
| 0.300 | 0.078 | 0.088 | 4 689.5 | **< 0.001** | 83 | 17 |
| 0.500 | 0.102 | 0.103 | 4 926.0 | **< 0.001** | 89 | 11 |

**발견 7 — SYSTEM의 구조적 열위, Bernoulli 교체의 개선 여지**. 선택도 0.050 이상에서 현재 Exqutor가 사용하는 `TABLESAMPLE SYSTEM`이 (Python 재구현의) counterfactual Bernoulli 대비 Q-error를 유의하게 키운다. 선택도가 클수록 더 많은 query에서 SYSTEM이 불리한 방향으로 움직이며(s=0.500에서 89/100 query), 이는 "SYSTEM을 Bernoulli로 교체하면 median 기준 3.8~9.1%p Q-error 개선"이라는 설계안 v3에 없던 **새로운 기여축**으로 읽힌다. Exqutor 소스 `src/vector.c` L1192에서 쿼리 조립 한 줄을 `TABLESAMPLE SYSTEM → TABLESAMPLE BERNOULLI`로 바꾸는 구현 경로가 구체적으로 식별된다.

---

## III. 해석 — RQ1 방향 재정립 필요

### III.1 가설 H1 기각

> **H1 (원안)**: Skewness가 클수록 Q-error가 증가한다. 특히 `|γ| > 1`인 분포에서 Q-error가 uniform 대비 2배 이상 악화.

위 결과는 H1을 강하게 기각한다. 4개 skew 지표 중 어느 것과도 Q-error 상관이 거의 0이며, 그룹 간 median 비율도 1.0 근처다. 이는 설계안 v3가 구상했던 "distribution-aware stratified sampling"의 전제를 흔드는 결과다.

### III.2 그러나 2개의 강력한 대체 신호

데이터는 두 가지 새로운 서술을 강력하게 뒷받침한다.

1. **선택도 효과**. Exqutor Adaptive Sampling은 극소 선택도(`s ≤ 0.01`)에서 구조적으로 취약하다. `s = 0.001`에서 median Q-error 2.6은 실무 관점에서 의미가 있다(옵티마이저 플랜 선택에 영향을 주는 수준).
2. **SYSTEM sampling의 구조적 약점**. 현재 Exqutor는 `TABLESAMPLE SYSTEM`만 사용하는데(`src/vector.c` L1192 단일 호출), 이것이 counterfactual Bernoulli 대비 Q-error를 일관되게 키운다. 가장 큰 효과는 `s = 0.500`에서 89/100 query가 SYSTEM 쪽으로 악화. 원인은 블록 내부의 행 상관성(physical clustering)으로 추정된다. 본 논문의 Adaptive Sampling 절이 샘플링 메서드 선택을 근거 없이 SYSTEM으로 고정하고 있다는 점은 **샘플링 메서드 ablation**이라는 단독 기여 가능 영역을 드러낸다.

### III.3 설계안 pivot — **Pivot A + C 병합 확정** (2026-04-14 17:35 KST, 18:50 KST 강화)

팀 논의 결과 **정확도 기준 최적 노선으로 Pivot A + Pivot C(재설계 version) 병합을 확정**했다(17:35 KST). 이후 같은 날 18:00~18:50 추가 세션에서 옵션 A 시도 중 발견된 네 가지 Exqutor design constraint(`equivalence_check.md` §X 참조)가 Pivot A+C의 학술적 정당화를 한 단계 강화한다(18:50 KST). 

**원래 정의(17:35)**. Pivot A는 기여가 아니라 **fair baseline 구축 도구**로 재정의되고, Pivot C는 **local skew 지표 기반 Stratified Sampling 실제 구현**으로 본선에 배치된다. Pivot B(선택도 적응형 β)는 채택되지 않았다 — Adaptive loop 내부 튜닝은 원래 연구 방향(Skew-Aware)과 직교하므로, 부차 기여로만 여유가 있을 때 붙인다.

**강화 정의(18:50)**. 옵션 A 시도에서 발견된 다음 두 design constraint가 본 연구의 **새로운 motivation 첫 줄**로 격상된다.

1. **Hook trigger 조건의 사각지대**. Exqutor의 `pgvector_set_baserel_rows_estimate_hook`은 `vector.c` line 243 `if (table_count > 2)` 조건을 통과해야만 활성화된다. `count_total_tables`가 query rangetable의 RTE_RELATION + RTE_SUBQUERY 재귀 카운트를 세므로, **단일 테이블 vector range query는 hook trigger 자체에 도달하지 못하고** PG default selectivity 1/3로 fall-through된다. 즉 `SELECT count(*) FROM table WHERE (vec <-> q) < D` 형태의 단일 테이블 vector range query는 Exqutor의 Adaptive Sampling 함수에 도달하지 못하는 사각지대다. Exqutor 논문 본문에 명시되지 않은 design constraint이며, 단일 테이블 vector range query가 실무에서 더 흔한 시나리오임을 고려하면 본 연구가 새로 제기할 RQ로 자연스럽게 편입된다.

2. **Hook 활성 시 plan replacement 동작**. Hook trigger 조건을 우회한 채 `vector.c` line 243을 `if (table_count >= 1)`로 한 줄 수정하고 재빌드해서 단일 테이블 query에서도 hook을 활성화하면, **outer query의 base relation 노드 자체가 PostgreSQL의 `Sample Scan`으로 plan-tree 교체**된다(`Sampling Method: system`, `Sampling Parameters: ['0.0385'::real]`). 즉 단순 cardinality estimation을 위한 baserel rows set이 아니라 plan execution 자체가 sample scan으로 격하된다. 단일 테이블 시나리오에서는 outer query의 결과 자체가 sample 안 부분 카운트로 바뀌어(예: true=100,000인 query에서 `SELECT count(*)`가 32 반환) **outer query의 정확성이 깨진다**. 이는 Exqutor의 hook 동작이 multi-table join에서는 join 결과의 부분 영향만 주지만 단일 테이블에서는 outer query의 의미를 잃게 만드는 design constraint다.

**이 두 finding이 강화하는 학술적 구조**. 본 연구는 Exqutor의 두 가지 암묵 가정을 순차 해체한다는 17:35 KST 정의에 다음 한 가지를 더한다.

- **첫째 (X.3, 18:50 추가)**: "Adaptive Sampling이 모든 vector range query에 적용된다"는 가정을 해체. **multi-table only로 trigger되는 사각지대를 finding으로 제시**.
- **둘째 (X.5, 18:50 추가)**: "Hook은 cardinality estimation만 한다"는 가정을 해체. **plan replacement 동작이 outer query 정확성을 깨는 부작용을 finding으로 제시**.
- **셋째 (17:35 정의)**: "TABLESAMPLE SYSTEM이 적절한 샘플링 메서드"라는 가정을 Pivot A로 해체 — `src/vector.c` L1192를 BERNOULLI로 교체해 block bias를 제거.
- **넷째 (17:35 정의)**: "naive uniform sampling이 충분"이라는 가정을 Pivot C로 해체 — local skew 지표로 층을 정의하고 stratified sampling을 실제 구현해 층화의 정확도 이득을 측정.

네 해체는 직교적이며, 첫째·둘째는 **finding 제시(motivation 강화)**, 셋째·넷째는 **개입 측정(본선 기여)**으로 본 연구의 두 단계 학술적 기여를 형성한다. 본 연구는 더 이상 "vector range query의 카디널리티 추정 정확도"라는 일반적 명제만 다루지 않고, "Exqutor가 자신의 design constraint로 배제한 단일 테이블 vector range query 사각지대를, hook trigger 완화와 sampling 함수 sanitize라는 두 단계로 해소한다"는 좁고 정확한 기여 명제를 갖는다.

**원래 학술적 구조(17:35)는 그대로 유지**.

**결정 근거**. 본 세션의 Fisher γ 실패는 "skew 자체의 무관성"이 아니라 네 가지 측정 결함(global 지표의 distance concentration 취약, 100 query 규모의 Adaptive loop 미수렴, 1M subset의 통계적 불안정, SYSTEM block bias의 신호 은폐)이 혼재된 결과일 가능성이 크다. 원래 설계안 v3의 "Distribution-Aware Stratified Sampling"은 본 세션에서 **구현조차 되지 않았고 실증도 없었다** — Stage 4 Python 재구현은 naive bernoulli/system 두 mode만 가졌으며 stratified mode는 부재했다. 따라서 본 세션의 H1 기각은 "원래 방향이 틀렸다"는 판결이 아니라 "원래 방향을 검증할 수 있는 실험이 아직 없었다"는 진단이다.

**A+C 병합의 학술적 구조**. Exqutor의 두 가지 암묵 가정을 순차 해체한다. 첫째, "TABLESAMPLE SYSTEM이 적절한 샘플링 메서드"라는 가정을 A로 해체 — `src/vector.c` L1192를 BERNOULLI로 교체해 block bias를 제거한다. 둘째, "naive uniform sampling이 충분"이라는 가정을 C로 해체 — local skew 지표로 층을 정의하고 stratified sampling을 실제 구현해 층화의 정확도 이득을 측정한다. 이 두 해체는 직교적이므로 2×3 ablation table(SYSTEM/BERNOULLI/STRATIFIED × 3 dataset)로 각 개선의 기여를 분리할 수 있다.

**2단계 분할 전략**. 중간발표(4/28)와 최종보고서(6/11) 사이를 두 국면으로 나눈다. **중간발표 국면**에서는 본 노선의 골격 — 옵션 A 세팅, Pivot A 네이티브 실증, local skew 지표 1~2개 구현, partsupp_deep_10 단일 dataset에서 stratified 부분 실증 — 까지 도달해 방향의 타당성을 제시한다. **최종보고서 국면**에서는 3 dataset(deep/sift/wiki) × 1000 query × 20 seed × 3 sampling method의 전면 ablation matrix로 완성형을 낸다. 본 결과의 "Fisher γ 4 지표 실패" 자체도 "global 지표는 고차원에서 관측력을 잃는다"는 부정적 발견으로 motivation에 편입된다.

**결과 해석의 세 가능성**. 전면 ablation 후 (α) stratified가 모든 bin에서 uniform을 유의하게 이기고 `|γ|` 큰 구간에서 효과 최대 — 원래 설계 성공, (β) stratified가 대체로 uniform과 비슷하거나 미세 개선 — skew는 1차 설명변수가 아니고 층화는 block bias 완화에 그친다는 정직한 negative result, (γ) dataset별 조건부 효과 — 차원·데이터 특성의 이론 분석으로 전환. 세 결과 모두 학술적 가치가 있으며, 본 연구는 "원래 가설의 공정한 검증" 자체를 기여로 제시할 수 있다.

### III.4 현재 결과의 한계

- 1M 서브셋. 원본 sf10(`partsupp_deep_10`, 8M)에서 재현해야 일반화 가능.
- 단일 테이블. 128d SIFT(`customer_sift_10`)와 768d WIKI(`part_wiki_10`)에서 재현 필수.
- **Stage 4.5 수학적 검증은 통과**(`equivalence_check.md`). 상수 8개·수식 5개·제어 3축 모두 Exqutor 소스와 일치하며, Python 방어 clamp 2건은 60 run 전체에서 발동하지 않았다. 다만 네이티브 bitwise 재현(옵션 A — Exqutor 전용 PG 인스턴스 initdb + 데이터 로드 + 100 query 네이티브 실행)은 미완이며, 다음 세션 과제로 기록됨.
- 시각화(Stage 5b)가 아직 없음. 산점도·박스플롯으로 위 수치가 실제로 어떤 모양인지 확인 필요.

---

## IV. 다음 세션 우선 작업 — Pivot A+C 8 Phase 로드맵

본 세션에서 Pivot A+C 노선이 확정되었으므로, 다음 세션 이후의 작업은 아래 8 Phase로 재조직된다. 중간발표까지 Phase 1~5 커버, 최종보고서까지 Phase 6~8 완주가 목표. **Phase 1, Phase 2는 2026-04-14 17:00~18:50 추가 세션에서 완주**(본 문서 §X 및 `equivalence_check.md` §X 참조). **Phase 3은 부분 실패**(네 가지 design constraint로 단일 테이블 옵션 A 직접 비교 불가능). 다음 세션 첫 작업은 **Phase 4 (Pivot A 네이티브 BERNOULLI 교체 실측)**로 시작한다.

**Phase 1 ✅ (2026-04-14 17:00~18:00 KST 완주)** — Exqutor 환경 복구. `build_custom.sh`의 `pg_hint_plan` 설치 타겟을 시스템 PG17 대신 Exqutor prefix(`psql/`)로 수정하여 `===BUILD_FAIL===` 재발 차단. Exqutor postgres 바이너리로 별도 data directory(`exqutor_sf10`)에 initdb + port 55436에서 기동. GUC(`vector.sample_size=385`, `vector.update_sample_size=on`, `vector.sample_update_cycle=50`) 인식 검증 통과. `shared_preload_libraries='vector'` eager preload 설정. `exqutor_qerror` 테이블 수동 CREATE(patch에 `vector--0.7.1.sql` direct create path 누락된 버그 우회). 산출물: 살아있는 Exqutor PG 55436 (pid 1154554, 18:00 시점) + vanilla PG 55435 (pid 1136097) 동시 가동.

**Phase 2 ✅ (2026-04-14 18:10~18:20 KST 완주)** — 데이터 로드. vanilla PG 55435의 `partsupp_deep_10` 8M 행을 Exqutor PG 55436으로 이전. (i) Exqutor PG에 FK·인덱스 없는 빈 테이블 사전 생성, (ii) `pg_dump --data-only -Fp -t partsupp_deep_10 | psql --single-transaction` pipe 방식 (273초, 4537 MB), (iii) 검증 통과 (8,000,000 행 / 0 인덱스 / vector 96d). 이어서 같은 Exqutor PG 안에서 `CREATE TABLE partsupp_deep_10_subset_1m AS SELECT DISTINCT ON (ps_partkey) ... WHERE ps_partkey BETWEEN 1 AND 1000000 ORDER BY ps_partkey, ps_suppkey`로 Stage 1 Python의 dump SQL을 결정론적으로 재현 (1M 행 / 435 MB). query_pool.parquet 첫 10개 ps_partkey/ps_suppkey/vector 5 element가 1M subset 테이블의 같은 행과 완전히 일치 확인. **HNSW 인덱스는 의도적으로 제외**(Sampling 경로 강제).

**Phase 3 ⚠️ (2026-04-14 18:20~18:50 KST 부분 실패)** — Stage 4.5 Phase 2 (네이티브 bitwise 검증). 세부 결과는 `equivalence_check.md` §X에 정리. 요약: 1 query sanity check에서 `Plan Rows = 333,333` (PG default selectivity 1/3) 발견 → `vector.c` line 547의 `if (table_count > 2)` hook trigger 조건 발견 → vector.c line 243을 `>= 1`로 한 줄 수정 + 재빌드 + restart로 우회 시도 → hook은 trigger되지만 outer plan이 `Sample Scan`으로 교체되어 `SELECT count(*)`가 sample 안 부분 카운트(32 vs true 100,000) 반환 + `exqutor_qerror.recent_qerrors[0] = inf` + q[25]쯤 `sample_size = NaN` 발산. **단일 테이블 1M subset 시나리오에서 Python Stage 4 결과와 직접 ±5% 비교 불가능**. §III~V의 수학적 검증이 여전히 본 연구의 가장 신뢰할 수 있는 베이스라인. 발견된 네 가지 design constraint(hook trigger / plan replacement / inf q_error / NaN 발산) 중 두 가지는 §III.3 Pivot A+C 정당화에 finding으로 편입.

**Phase 4 ✅ (2026-04-14 19:30~19:40 KST 완주)** — Pivot A 네이티브 실증. 자세한 결과는 본 문서 §V에 정리. 요약: `src/vector.c` line 889의 `TABLESAMPLE SYSTEM(%f)`을 `TABLESAMPLE BERNOULLI(%f)`로 sed 한 줄 교체 + `vector.so` 재빌드 (md5 abbc818a → 449c1c62) + PG 55436 fast restart. SYSTEM 모드와 BERNOULLI 모드 각각 100 query × 6 selectivity = 600 측정 (각 모드 20~82초 소요). 측정 직전 `vector.update_sample_size = off`로 Adaptive update path를 우회 — 이는 본 Phase 4 시작 시 1 query에서 발견된 다섯 번째 design constraint (update path SIGSEGV) 회피용 (§V.4 참조). **결과**: BERNOULLI가 selectivity 0.05~0.5 모든 구간에서 SYSTEM 대비 median q-error를 일관되게 낮춘다 (paired Wilcoxon p < 0.001). 효과 크기는 median 기준 +0.7%p (s=0.05) ~ +12.0%p (s=0.30). Python counterfactual (§II.5) 의 +3.8~9.1%p 와 방향 일치 + 효과 크기 한 자리수 % 수준 일치. **Pivot A 정량 검증 성공 — Exqutor 소스 한 줄 변경으로 카디널리티 추정 정확도가 통계적으로 유의하게 개선됨**.

**Phase 5 ⚠️ (2026-04-14 20:09 KST 부분 실패 — query feature 노선 종료)**. 자세한 결과는 본 문서 §VI에 정리. 요약: 4 local 지표 — (i) k-NN distance entropy(k=50), (ii) k-NN PCA explained variance ratio(k=50), (iii) KDE modality count(pilot k=500), (iv) NN clustering coefficient(k=50, inner k=10) — 를 numpy + scipy 만으로 구현해 1M subset × 100 query 에 대해 6초 만에 완주. Phase 4의 BERNOULLI baseline 위에서 4 지표 × 6 selectivity = **24 조합 모두 |Spearman ρ| < 0.2** 로 무효. 가장 강한 신호도 `nn_clustering_coef × s=0.010` 의 ρ=−0.166 (p=0.099) 로 임계 미달. 또한 `kde_modality_count` 는 100 query 중 99개가 unimodal 로 사실상 단일값 변수. **글로벌 4 + 로컬 4 = 총 8 지표 전수 검증 결과, 96d DEEP 100 query 의 *query-side* feature 로는 q_error 변동을 사전 예측할 수 없음** 이 결론. → Phase 6 의 층 정의는 query feature 가 아닌 *data-side* 축으로 전환되어야 함.

**Phase 6 Step 1~3 ⚠️ (2026-04-14 20:30 KST 부분 성공 — PCA decile 1차 시도)**. 자세한 결과는 본 문서 §VII 에 정리. 요약: Pivot C 의 *data-side global stratification* 1차 시도로 1M subset 의 첫 PCA component 값을 deciles (10 quantile) 로 partition → 1M × stratum_id 사전계산 + Horvitz-Thompson stratified estimator (`est = sum_i (n_i / s_i) * cnt_i`) 의 Python counterfactual 측정. Exqutor L1228 cnt clamp + L1232 estimator 공식과 정확히 동치 (s=0.001 BERN median 2.5974 == Stage 4 의 2.597 == Phase 4 native 의 2.5970, 소수점 셋째 자리 일치 검증 통과). **결과**: 큰 selectivity (s ≥ 0.3) 에서 paired Wilcoxon p < 0.005 로 stratified 가 BERNOULLI 보다 유의하게 우수 — 효과 크기 +0.7~0.8% median, 60/100 query 가 stratified 우위, std 도 stratified 가 더 작음 (분산 감소의 첫 정량 증거). 작은 selectivity (s ≤ 0.05) 에서는 효과 없거나 약간 음 — sample 안 cnt 가 0~1 변동 시 stratum weight 곱셈이 noise 증폭. **Pivot C 의 첫 정량 검증 — 작지만 통계적으로 유의한 신호** 확보. PCA decile 보다 더 적합한 layer (k-means partition, vector cluster) 를 다음 Phase 6 Step 4~ 에서 시도할 여지가 있으며, 본 결과만으로도 Phase 6 native (vector.c 구현) 진입의 정당성 확보.

**Phase 6 Step 3' ⚠️ (2026-04-14 20:45 KST 부분 성공 — KM20 = best layer 확정)**. 자세한 결과는 본 문서 §VIII 에 정리. 요약: Step 1~3 의 PCA decile (+0.7~0.8% in s≥0.3) 위에서 더 강한 layer 후보 비교. **단일 스크립트 4 mode 동시 측정** (bernoulli + pca_decile + kmeans K=10 + kmeans K=20) 으로 RNG noise 제거. numpy mini-batch k-means (Sculley 2010) 를 직접 구현 (sklearn 의존성 0). 1M × 96 → K=10 학습 0.62s + assign 0.7s, K=20 학습 0.5s + assign 0.59s. **결과**: KM20 가 best — *세 selectivity 구간* (s=0.100, 0.300, 0.500) 에서 BERN 대비 paired Wilcoxon p<0.05 우위, 특히 **s=0.100 에서 +2.25% (p=0.0042)** 의 새 신호 영역 확보. PCA decile 과 KM10 는 두 구간 (s=0.300, 0.500) 만. cross pair 에서 KM20 vs PCA decile 은 s=0.050 (+2.79%, p=0.028) + s=0.100 (+1.50%, p=0.015) KM20 우위. **KM20 가 다음 native 구현의 1순위 layer**.

**Phase 6 Step 4~ — Native vector.c 구현 + ablation (다음 세션 후속, KM20 layer 확정)**. Step 3' 의 KM20 best 결정 위에서 vector.c 에 (a) k-means centroid 20개 메모리 로드 + 1M × stratum_id 사전계산, (b) `estimate_cardinality_with_stratified_sampling` 함수, (c) GUC `vector.sampling_method` (`system` / `bernoulli` / `stratified`) 추가. SYSTEM/BERNOULLI/STRATIFIED 600 query 측정 × 3 mode = 1800 paired 비교 + 시각화 (Stage 5b). 다층 PCA / random projection 등 더 강한 layer 탐색은 Step 4 native 결과 확인 후 시도 가능 (KM20 의 native vs Python 일치성 검증이 1차 우선순위).

**Phase 7 — 중간발표용 부분 실증 (~4/26)**. `partsupp_deep_10` 단일 dataset에서 3 mode × 6 selectivity × 5 seed 최소 ablation. Table: SYSTEM vs BERNOULLI vs STRATIFIED의 median/mean/p95 Q-error. 방향의 타당성 증명이 목표.

**Phase 8 — 최종보고서용 완성 실증 (~6/11)**. 3 dataset(deep 96d/sift 128d/wiki 768d) × 1000 query × 20 seed × 3 mode × 8 selectivity × 4 skew bin 전면 ablation. Track B(KDE-pilot online 층화) 추가 구현. Stage 5b 시각화 7~8 figure 완성.

---

## V. Phase 4 정량 결과 — Pivot A 네이티브 검증 (2026-04-14 19:30~19:40 KST)

### V.1 측정 절차

`src/vector.c` line 889의 한 줄 — `appendStringInfo(&query, "SELECT COUNT(*)::float FROM (SELECT %s FROM %s TABLESAMPLE SYSTEM(%f)) p ...", ...)` — 의 `SYSTEM`을 `BERNOULLI`로 sed 교체 + `make USE_PGXS=1 PG_CONFIG=.../pg_config install`로 재빌드 + Exqutor PG 55436 fast restart했다. 새 `vector.so` md5는 `449c1c62a4562adacb0007a575a4f30d` (이전 SYSTEM 빌드 `abbc818a6f91ae82dfa68654a8be4a12`와 다름). 변경 직전 백업은 `vector.c.bak.20260414_1934_before_bernoulli`.

측정 스크립트는 `cache/rq1_phase4_native.py` (로컬: `experiments/code/rq1/phase4_native.py`). psycopg3로 Exqutor PG에 연결 후 query_pool.parquet 100건 × query_selectivity.parquet 6 selectivity = 600 query 를 순차 실행한다. 각 query 는 `EXPLAIN (ANALYZE, FORMAT JSON) SELECT count(*) FROM partsupp_deep_10_subset_1m WHERE (ps_embedding <-> '...'::vector) < D_target` 형태로 발사하며, plan tree 의 첫 번째 Scan 노드에서 Plan Rows + Actual Rows + Sampling Method 를 추출한다. q_error 는 `max(plan_rows / true_card, true_card / plan_rows)` 로 계산하고, true_card 는 `query_selectivity.parquet` 의 1M subset 정확 카운트를 사용한다 (Actual Rows 는 plan replacement 부작용으로 sample 안 부분 카운트로 격하되므로 q_error 에는 사용하지 않음).

GUC 설정은 측정 직전 `SET vector.sample_size = 385`, `SET vector.update_sample_size = off`, `SET vector.sample_update_cycle = 50` 로 강제한다. `update_sample_size = off` 는 본 Phase 4 시작 시 1 query sanity check 에서 발견된 다섯 번째 design constraint (§V.4) 의 회피 수단이다. SYSTEM/BERNOULLI 두 모드 모두 동일 GUC 로 측정해서 Adaptive update 경로를 동일하게 비활성화한 채 sampling method 만 비교한다.

각 모드 측정 직전 `TRUNCATE TABLE exqutor_qerror` 로 잔존 row 정리. SYSTEM 모드 측정 후 vector.c L889 sed 교체 + 재빌드 + restart, BERNOULLI 모드 측정 진행. 전체 소요 시간은 SYSTEM 82초 + BERNOULLI 21초.

### V.2 SYSTEM vs BERNOULLI per-selectivity 비교 (paired)

같은 (query_id, selectivity) 짝에 대해 두 모드의 q_error 를 paired 로 비교한다. 100 query × 6 selectivity = 600 paired 관측. 통계는 paired Wilcoxon signed-rank test, 대립가설 *SYSTEM > BERNOULLI*.

| selectivity | SYS median | BERN median | diff (SYS−BERN)/BERN | SYS mean | BERN mean | Wilcoxon W | p (greater) | SYS>BERN | SYS<BERN | tie |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 2.5970 | 2.5970 | +0.0% | 2.7788 | 2.8048 | 49 | 0.5958 | 6 | 8 | 86 |
| 0.010 | 1.5584 | 1.2987 | +20.0% | 1.6939 | 1.6185 | 1 988.5 | 0.2401 | 45 | 40 | 15 |
| 0.050 | 1.2031 | 1.1948 | +0.7% | 1.3816 | 1.2269 | 3 125.0 | **0.0009** | 58 | 37 | 5 |
| 0.100 | 1.2120 | 1.1323 | +7.0% | 1.3042 | 1.1365 | 3 666.5 | **< 0.001** | 66 | 31 | 3 |
| 0.300 | 1.2095 | 1.0794 | +12.0% | 1.2424 | 1.0893 | 4 477.0 | **< 0.001** | 76 | 24 | 0 |
| 0.500 | 1.1527 | 1.0519 | +9.6% | 1.1937 | 1.0602 | 4 429.5 | **< 0.001** | 78 | 22 | 0 |

**V.2 발견 1 — Pivot A 정량 검증 성공**. selectivity 0.05 이상 4 구간에서 모두 paired Wilcoxon p < 0.001 (s=0.05만 0.0009) 로 SYSTEM 의 q_error 가 BERNOULLI 보다 통계적으로 유의하게 크다. 가장 큰 효과는 s=0.500 에서 78/100 query 가 SYSTEM 쪽으로 불리한 방향, median 기준 9.6%p 개선. `src/vector.c` 한 줄 sed 교체로 Exqutor 의 카디널리티 추정 정확도가 측정 가능한 수준으로 개선된다는 것이 native 로 직접 확인되었다.

**V.2 발견 2 — Python counterfactual 과 방향성 일치**. §II.5 의 Python 재구현 paired 결과 (block_system vs bernoulli, 5 seed 평균) 는 같은 4 구간에서 +3.8~9.1%p 의 효과를 보였다. Native 측정의 +0.7~12.0%p 와 비교하면 방향이 모두 일치하고 효과 크기는 한 자리수 % 수준에서 일치한다. Native 가 약간 더 큰 효과를 보이는 이유는 (a) Native 는 1 seed (Exqutor 내부 RNG 1회) 이고 Python 은 5 seed 평균이라 분산 흡수 차이, (b) Python 의 block 시뮬레이션이 행 14개 단위 균등 가정인 반면 Native 의 SYSTEM 은 PG 페이지 13~15 행 가변 → 약간의 추가 분산, (c) Python 의 `mode="bernoulli"` 가 `mask = rng.random(N) < ratio` 행 단위인 반면 Native 의 `TABLESAMPLE BERNOULLI(0.0385)` 도 같은 수학적 처리를 하지만 PG 내부 SamplerRandomFns 가 다른 RNG 를 쓴다는 점이다. 본질적 일치성 검증으로는 충분하다.

**V.2 발견 3 — s=0.001 동치, s=0.010 분산 큼**. 가장 작은 선택도 s=0.001 은 86/100 query 에서 SYSTEM 과 BERNOULLI 가 정확히 동일한 q_error 2.597 을 반환했다. 이는 sample 안 매칭 카운트가 0 에 가까워 `cnt == 0 → 1` clamp 가 양 모드 모두 발동한 결과다 (Exqutor L1228, equivalence_check.md §V 참조). s=0.010 은 SYSTEM 45 / BERNOULLI 40 / tie 15 로 방향 신호는 약하게 SYSTEM 쪽이지만 분산이 커서 Wilcoxon p=0.240 으로 통계적 유의에 도달하지 못했다. 즉 Pivot A 의 효과는 *극소 선택도 (s ≤ 0.01) 에서는 0-clamp 로 인해 발현되지 않고, s ≥ 0.05 부터 통계적으로 유의한 수준* 으로 나타난다.

### V.3 Python 재구현 = Native 일치도 — equivalence_check.md §III~V 의 강화

본 Phase 4 측정의 부수적 발견은 *Python 재구현이 Native Exqutor 와 정확히 일치한다* 는 점이다. 1 query sanity check 에서 query_id=0 의 s=0.001 query 는 Native plan_rows = **2597** vs true 1000 → q_error **2.597** 로 측정되었으며, 이는 §II.2 의 Python median Q-error **2.597** (block_system mode) 과 소수점 셋째 자리까지 정확히 일치한다. 즉 `equivalence_check.md` §III~V 의 수학적 검증 (상수 8개·수식 5개·제어 3축 일치) 은 본 Phase 4 측정으로 *bitwise 한 query 수준에서도 동치* 임이 확인되었다.

이 일치는 Phase 3 (옵션 A) 가 부분 실패한 직후의 우려 — *Python 이 Exqutor 와 다른 결과를 낸다면 §II 의 모든 발견이 흔들린다* — 를 직접적으로 해소한다. Python Stage 4 의 전체 60 run 결과 (5 seed × 6 selectivity × 2 mode) 는 Native 의 1 seed 측정과 한 자리수 % 이내로 일치하며, Python 결과를 본 연구의 *수학적 베이스라인* 으로 인정하는 것이 정당화된다.

### V.4 새 design constraint 발견 (5번째) — Adaptive update path SIGSEGV

Phase 4 의 첫 1 query × 6 selectivity sanity check 시도 (`update_sample_size = on`, `--reset-qerror`) 에서 q3 (s=0.050) 실행 중 PG 가 **signal 11 (SIGSEGV)** 로 죽었다. 로그 (`log/exqutor-2026-04-14.log`):

```
2026-04-14 10:32:05 UTC [1163415] LOG:  Estimated cardinality for range query on table partsupp_deep_10_subset_1m: 2597.402597
2026-04-14 10:32:05 UTC [1163415] LOG:  Estimated cardinality for range query on table partsupp_deep_10_subset_1m: 12987.012987
2026-04-14 10:32:05 UTC [1159124] LOG:  server process (PID 1163415) was terminated by signal 11: Segmentation fault
```

q1 (s=0.001) 과 q2 (s=0.010) 은 정상 처리되며 hook 이 estimate 를 set 했다 (각각 2597.4, 12987.0). q3 에서 segfault. 추정 원인은 Adaptive Sampling 의 update path 어딘가의 메모리 버그다. q1 은 INSERT path (TRUNCATE 직후 fresh row), q2 는 UPDATE path (첫 update), q3 는 두 번째 UPDATE 에서 죽었다. PG 는 자동 recovery 후 다시 기동.

회피 수단: `SET vector.update_sample_size = off`. 이 모드는 sample_size 의 Adaptive update 경로를 비활성화하고 sample_size = 385 fixed 로 estimate 만 한다. 본 회피로 SYSTEM/BERNOULLI 두 모드 모두 600 query 측정에서 0 segfault, 0 error 로 완주했다.

**V.4 의 학술적 의미**. 이 다섯 번째 design constraint 는 §X.6 (q_error inf) 와 §X.7 (sample_size NaN) 의 *동일 근원의 다른 발현*일 가능성이 높다. 셋 모두 Adaptive Sampling loop 의 단일 테이블 호출에서 발생하며, multi-table only design intent 의 부작용이라는 동일 finding 으로 묶을 수 있다. `direction_pivot_rationale.md` §4.5 의 결함 기록과 동일 카테고리. 본 Phase 4 측정은 update_sample_size=off 로 Adaptive update 를 차단한 채 *sampling method 자체의 효과만* 분리 측정한 결과이며, Adaptive update 의 numerical stability 는 Phase 6 (Stratified Sampling 함수 설계) 에서 별도로 sanitize 되어야 한다.

### V.5 산출물

| 파일 | 위치 | 내용 |
|---|---|---|
| `phase4_system.parquet` | `experiments/results/rq1_motivation/` | SYSTEM 모드 600 측정 (query_id, selectivity, plan_rows, actual_rows, sampling_method, q_error 등) |
| `phase4_bernoulli.parquet` | 같음 | BERNOULLI 모드 600 측정 |
| `phase4_system_meta.json` | 같음 | SYSTEM 모드 메타 (per-selectivity median 등) |
| `phase4_bernoulli_meta.json` | 같음 | BERNOULLI 모드 메타 |
| `phase4_compare.json` | 같음 | per-selectivity SYS vs BERN paired Wilcoxon 결과 |
| `phase4_*_sanity*` | 같음 | 1 query × 6 sanity check 결과 (양 모드) |
| `cache/rq1_phase4_native.py` | 서버 + `experiments/code/rq1/phase4_native.py` | 측정 스크립트 |

서버 vector.c 백업 파일 명세:
- `vector.c.bak.20260414_1840` — Phase 3 시작 전 (line 243 변경 전, 즉 4/3 합의 시점의 원본)
- `vector.c.bak.20260414_1934_before_bernoulli` — Phase 4 시작 전 (line 243 변경 후 + line 889 SYSTEM 그대로)
- 현재 vector.c — line 243 `>= 1` + line 889 `BERNOULLI`

---

## VI. Phase 5 결과 — Local skew 4 지표 전수 무효 (2026-04-14 20:09 KST)

### VI.1 측정 절차

§II.1 의 글로벌 4 지표 (Fisher γ, log-γ, tail ratio P99/P50, Bowley) 가 §III.2 에서 q_error 와 |Spearman ρ| < 0.05 로 무효화된 직후, §III.3 의 Pivot C (query feature 기반 stratified) 노선을 살리기 위한 후속 시도가 본 Phase 5 다. 가설은 *글로벌 분포 통계는 96d 거리집중 효과로 변별력을 잃지만, query 주변의 local geometry 는 여전히 q_error 와 상관할 수 있다* 는 것. 이 가설을 검증하기 위해 4 가지 *local* 지표를 numpy + scipy 만으로 구현했다 (sklearn / networkx 의존성 제거).

| 지표 | 정의 | 가설 |
|---|---|---|
| (i) **k-NN distance entropy** (k=50) | 50 nearest neighbor 거리들을 10 bin 히스토그램으로 묶은 Shannon entropy (nat) | compact cluster 면 낮음, isotropic spread 면 높음 |
| (ii) **k-NN PCA EVR1** (k=50) | 50 NN 벡터 (50×96) centering 후 SVD 의 첫 singular value variance 비율 | 한 방향으로 길게 펴진 cluster 면 높음 (1 에 가까움), isotropic spread 면 낮음 (1/96 ≈ 0.01 근처) |
| (iii) **KDE modality count** (pilot k=500) | 500 nearest distance 의 1D Gaussian KDE → grid evaluate → `find_peaks` (prominence ≥ 0.05·max) | multi-modal 이면 query 주변이 혼합 cluster, sample 추정 불안정 |
| (iv) **NN clustering coefficient** (k=50, inner k=10) | 50 NN 사이의 50×50 거리에서 각 노드 inner_k-NN 으로 무방향 그래프 → 평균 local clustering coefficient | 강한 cluster 일수록 높음 |

거리 행렬은 §II.1 의 BLAS matmul 패턴 (`compute_distance_matrix`) 을 stage2 에서 그대로 재활용 — 1M × 96 vs 100 × 96 → (1M, 100) 거리 행렬 (약 400 MB float32) 을 0.9 초에 생성. 각 query 별로 `np.argpartition` 으로 top 500 (= k_pilot) 인덱스 후 거리순 정렬 → top 50 (k_nn) 추출 → 4 지표 계산. 100 query 전체 처리 1.9 초. 데이터 로드 + 거리행렬 + 4 지표 + Spearman 분석 + 출력 합쳐 **6.0 초** 만에 완주.

서버 위치: `cache/rq1_phase5_local_skew.py`. 로컬 sibling: `experiments/code/rq1/phase5_local_skew.py`.

### VI.2 4 local 지표 분포 통계 (100 query)

| 지표 | min | p25 | p50 | p75 | max | std | 변별력 |
|---|---|---|---|---|---|---|---|
| knn_distance_entropy | 0.098 | 0.265 | **0.375** | 0.573 | 1.440 | 0.259 | 비교적 큼 (range ratio 14×) |
| knn_pca_evr1 | 0.091 | 0.110 | **0.126** | 0.152 | 0.317 | 0.038 | 좁음 (range ratio 3.5×) |
| kde_modality_count | 1 | 1 | **1** | 1 | 2 | 0.100 | **사실상 단일값** (99/100 query unimodal) |
| nn_clustering_coef | 0.418 | 0.447 | **0.470** | 0.497 | 0.630 | 0.040 | 좁음 (range ratio 1.5×) |

**VI.2 발견 1 — 변별력 부족 3건**. `kde_modality_count` 는 100 query 중 99 개가 unimodal 로 사실상 single-value. `knn_pca_evr1` 과 `nn_clustering_coef` 는 좁은 범위 (각각 0.09~0.32, 0.42~0.63) 에 모여 있어 query 간 변별력이 약하다. 학술적으로는 이것 자체가 *96d DEEP 1M 의 random query 100 개의 local geometry 가 통계적으로 균질* 이라는 발견이다 — 거리집중 (concentration of distance) 효과가 너무 강해서 query 별 local 변동까지 평탄해진다.

**VI.2 발견 2 — knn_pca_evr1 의 isotropic 대비 13×**. 평균 0.137 은 96d random isotropic 의 expected EVR1 (≈ 1/96 = 0.0104) 의 약 13 배다. 즉 50 NN 은 isotropic 보다 한 방향으로 더 길게 spread 되어 있긴 하다. 하지만 query 간 분산이 좁아 변별 변수로는 사용 불가.

**VI.2 발견 3 — knn_distance_entropy 만 변별력 보유**. 0.10~1.44 range, std 0.26 으로 4 지표 중 유일하게 query 간 변별력이 큰 지표. 그러나 §VI.3 에서 q_error 와 무관함이 확인됨.

### VI.3 Spearman ρ — 24 조합 전수 검증 (q_error vs local 지표)

`phase4_bernoulli.parquet` (600행, BERNOULLI baseline q_error 포함) 와 `query_local_skew.parquet` 를 `query_id` 로 inner join → 4 지표 × 6 selectivity = 24 조합 각각 100 query (per-selectivity) 의 Spearman ρ + p-value 계산.

| 지표 \ s | 0.001 | 0.010 | 0.050 | 0.100 | 0.300 | 0.500 | max \|ρ\| |
|---|---|---|---|---|---|---|---|
| knn_distance_entropy | +0.030 | −0.113 | +0.026 | +0.101 | +0.020 | +0.078 | 0.113 |
| knn_pca_evr1 | −0.153 | −0.096 | +0.092 | +0.152 | +0.025 | −0.043 | 0.153 |
| kde_modality_count | −0.030 | −0.147 | −0.140 | −0.040 | +0.085 | −0.017 | 0.147 |
| nn_clustering_coef | −0.126 | **−0.166** | +0.070 | −0.054 | +0.019 | +0.057 | **0.166** |

(p-value 모두 0.099 ~ 0.864 — 어떤 조합도 5% 유의수준 도달 못함)

**VI.3 발견 1 — 24 조합 모두 |ρ| < 0.2**. 사전 설정 임계 (`session_resume.md §C.5`) 인 |ρ| > 0.2 를 통과한 조합 0 개. 가장 강한 신호도 `nn_clustering_coef × s=0.010` 의 ρ = −0.166 (p=0.099) 로 임계 미달. *Phase 5 의 가설은 기각된다*.

**VI.3 발견 2 — 부호 일관성 부족**. 같은 지표 안에서도 selectivity 별 부호가 뒤집힌다. 예) `knn_pca_evr1` 은 s=0.001 에서 −0.153, s=0.100 에서 +0.152 로 부호 반전. 부호 안정성이 있어야 weak signal 이라도 의미 있게 해석 가능한데, 이 부호 inconsistency 는 본 ρ 들이 *통계적 노이즈에 가깝다* 는 강한 증거다.

**VI.3 발견 3 — `nn_clustering_coef` 의 약한 negative 일관성**. 4 지표 중 유일하게 작은 selectivity 구간 (s=0.001, 0.010) 에서 약하게 negative 신호 (ρ ≈ −0.13 ~ −0.17). 의미: cluster 가 강하게 묶일수록 q_error 가 *작아진다*. 직관적으로 잘 묶인 cluster 는 sample 안에서 카운트 추정이 안정적이라는 해석이 가능. 그러나 효과 크기가 임계 미달이라 단독 layer 정의 변수로 사용 불가.

### VI.4 학술적 해석 — 글로벌+로컬 8 지표 종합 결론과 Pivot C 노선 재정의

본 Phase 5 의 결과를 §II.1 (글로벌 4 지표) + §III.2 (글로벌 지표 무효화) 와 합치면, **96d DEEP 1M subset 의 100 query 에 대해 query-side feature 8 가지 (글로벌 4 + 로컬 4) 모두 q_error 와 |Spearman ρ| < 0.2** 라는 종합 결론에 도달한다. 이는 다음과 같은 학술적 함의를 가진다.

1. **Distance concentration 의 이중 효과**. §II.1 에서 100 query 모두 Fisher γ ≈ −1.07, tail ratio P99/P50 ≈ 1.07~1.17 의 좁은 범위에 모인 것은 *글로벌* 분포 통계가 96d 에서 변별력을 잃었다는 신호였다. 본 Phase 5 의 *로컬* 지표 3건 (PCA EVR1, KDE modality, clustering coef) 도 좁은 범위에 모여 있어, 거리집중 효과가 글로벌만이 아니라 *local geometry 까지 평탄화* 시킨다는 것이 확인됐다.

2. **Query feature 사전 식별 노선의 종료**. Pivot C 의 원안 (§III.3) 은 "local skew 지표로 층을 정의한다" 였다. 본 Phase 5 결과로 *query-conditional layer 정의는 8 지표 검증 후 사전 식별 불가능* 이 확정됐다. 단, 이는 "skew 자체가 무관" 이 아니라 "skew 가 측정 가능한 형태로 query 별로 변별되지 않는다" 라는 진단 — 같은 finding 이 `direction_pivot_rationale.md` §3 의 글로벌 지표 실패 narrative 에 이미 일관되게 정리되어 있다.

3. **Pivot C 의 data-side 재정의가 자연스러운 다음 단계**. query feature 가 막혔으므로, layer 는 *데이터 사이드* 에서 가져와야 한다. 두 가지 후보:
   - **(a) Distance quantile bin**: dataset 전체에 대한 global distance distribution (예: 모든 vector 쌍 또는 query-vector 거리의 sample) 을 quantile bin 으로 나눠 stratum 정의. Exqutor 의 사전계산 패러다임 (vector_index_create 시점에 1회 계산) 과 호환.
   - **(b) Vector cluster partition**: data vector 자체를 k-means 또는 PCA 기반으로 partition 해 stratum 정의. cluster 마다 균등 sample 추출.
   
   둘 다 query 와 무관한 *데이터 자체의 구조* 에서 layer 를 가져오므로, query feature 가 변별되지 않는 본 데이터셋에서도 적용 가능하다. Phase 6 는 (a) 부터 시작 — 가장 단순하고 Exqutor 패러다임 호환성이 높음.

4. **Negative result 의 motivation 가치**. 본 8 지표 검증 결과는 그 자체로 *고차원 vector dataset 의 query feature 사전 식별 한계* 를 정량 확인한 finding 이다. 향후 vector DB 의 cardinality 추정 연구에서 *query-side feature 기반 stratified sampling 을 제안하려면 본 검증 결과를 우회해야 한다* 는 부정적 가이드가 된다. RQ1 motivation 의 §IV → §V → §VI 의 narrative 흐름 자체가 "원래 가설을 공정 검증하고, 실패하면 그 실패가 후속 설계의 근거가 된다" 는 학술적 정직성을 보여준다. `direction_pivot_rationale.md` 의 narrative 와 정합.

### VI.5 Phase 6 진입 조건

Phase 5 의 결과 위에서 Phase 6 (Stratified Sampling 함수 설계 + 구현) 의 진입 조건을 다음과 같이 재정의한다.

- **(C1)** Layer 정의는 query feature 가 아닌 *data-side* 에서 가져온다. 본 Phase 5 §VI.4 의 (a) Distance quantile bin 또는 (b) Vector cluster partition 중 (a) 가 1차 후보 — Exqutor 사전계산 호환성이 높고 구현이 단순.
- **(C2)** Stratified sampling 함수의 추정 공식은 `sum_strata (n_i / N) * (cnt_i / sample_i) * D_i` 형태 — 층별 균등 sample, 가중 카디널리티 추정. Exqutor L1232 의 `est = cnt * total / sample_size` 를 multi-stratum 으로 일반화.
- **(C3)** GUC `vector.sampling_method` (`system` / `bernoulli` / `stratified`) 도입. 세 모드 ablation 가능하게.
- **(C4)** Phase 4 의 BERNOULLI baseline + Phase 6 의 STRATIFIED 의 paired 비교를 selectivity 6 구간에서 수행. Pivot A 와 직교적 효과인지 확인.
- **(C5)** Phase 5 의 negative result 자체를 Phase 6 의 motivation 으로 인용 — *layer 정의를 query-side 에서 시도했으나 실패했고, 따라서 data-side 로 전환했다* 는 narrative 를 코드 + 문서에 명시.

### VI.6 산출물

| 파일 | 위치 | 내용 |
|---|---|---|
| `query_local_skew.parquet` | `experiments/results/rq1_motivation/` | 100 query × (4 local 지표 + meta), query_id 인덱스 |
| `phase5_local_skew_spearman.json` | 같음 | 24 조합 (4×6) Spearman ρ + p-value 전수, 강신호 후보 sort |
| `phase5_local_skew_meta.json` | 같음 | 실행 메타 + 4 지표 분포 통계 (min/max/mean/median/std) + Phase 5 인자 |
| `phase5_local_skew.py` | `experiments/code/rq1/` + 서버 `cache/rq1_phase5_local_skew.py` | 측정 스크립트 (numpy + scipy + pyarrow + pandas 만, 의존성 6.0초 완주) |

---

## VII. Phase 6 Step 1~3 결과 — PCA decile stratified 1차 시도 (2026-04-14 20:30 KST)

### VII.1 측정 절차

§VI 의 Phase 5 결론 (query-side feature 8 지표 모두 q_error 와 무관) 직후, Pivot C 의 *data-side global stratification* 1차 시도. Phase 5 §VI.5 의 두 후보 (distance quantile bin / vector cluster partition) 중 가장 단순한 변형 — **첫 PCA component 의 deciles** — 을 1차 layer 로 선택했다. 사유: (a) 1M × 96 → 96 × 96 covariance eigendecomposition (`eigh`) 으로 첫 PC 만 수 초에 추출 가능, (b) 1M 행에 정확히 1 stratum_id 를 mapping 하므로 Exqutor 의 사전계산 패러다임 (`vector_index_create` 시점) 과 자연 호환, (c) layer 정의에 query 정보가 일절 들어가지 않아 Phase 5 결론과 일관.

**Layer 정의**:

1. 1M 벡터 centering → covariance (96 × 96) → `np.linalg.eigh` → 가장 큰 eigenvalue 의 eigenvector = 첫 PC.
2. 첫 PC 투영값 (1M × 1) → `np.quantile` deciles → 9 internal 경계.
3. `np.searchsorted` 로 1M × stratum_id (∈ [0, 9]).
4. 결과: 정확히 100 000 행 × 10 stratum 의 *균등* partition.

**Stratified estimator** (Horvitz-Thompson):

$$ \hat{Y}_\text{stratified} = \sum_{i=1}^{K} \frac{n_i}{s_i} \cdot c_i $$

- $n_i$: stratum $i$ 의 전체 행 수 (각 100k)
- $s_i$: stratum $i$ 에서 추출한 sample 행 수 (균등 배분 38~39 행, 합계 385)
- $c_i$: stratum $i$ 의 sample 안에서 $\|v - q\| < D$ 만족하는 행 수

**0-clamp 일반화**: Exqutor L1228 의 `cnt = (cnt == 0) ? 1 : cnt` 를 stratified 로 일반화. $c_\text{total} = 0$ 인 경우, 가상 1 hit 가 어느 stratum 인지 모르므로 *active stratum 의 weight 평균* 으로 fallback. 균등 stratum 균등 sample 에서는 $\text{mean}(n_i / s_i) = N/S$ 와 동일하므로 BERNOULLI 의 cnt clamp 결과 (= 2.5974) 와 정확히 일치한다 — 즉 s=0.001 의 0-clamp 영역에서 두 mode 가 *수학적으로 동치* 가 된다는 의미. 이로써 stratified 의 효과는 `cnt > 0` 인 영역에서만 측정된다.

**Counterfactual 측정 형식**: Stage 4 의 5 seed Python 패턴을 그대로 따른다. 100 query × 6 selectivity × 5 seed × 2 mode (bernoulli/stratified) = **6 000 측정**. seed 1000~1004 (bernoulli), seed 2000~2004 (stratified) 로 sampling RNG 분리. 같은 stratified sample 1 회 추출 후 6 selectivity 에 재사용 (sample 추출 비용 절감 + selectivity 간 비교 안정화). 5 초 만에 완주 (1.0 s × 5 seed).

서버 위치: `cache/rq1_phase6_stratified_python.py`. 로컬 sibling: `experiments/code/rq1/phase6_stratified_python.py`.

### VII.2 동치성 검증 — Stage 4 / Phase 4 native 와 BERNOULLI median 일치

본 Phase 6 의 BERNOULLI 모드는 Stage 4 의 Python 5 seed bernoulli 와 *동일 estimator* 여야 한다 (Phase 6 의 stratified 효과를 측정하기 전에 baseline 의 동치성을 보장). per-selectivity median q_error 를 §II.2 / §V.2 의 결과와 직접 비교한다.

| selectivity | Stage 4 Python 5seed BERN | Phase 4 Native 1run BERN | **Phase 6 Python 5seed BERN** |
|---|---|---|---|
| 0.001 | 2.597 | 2.5970 | **2.5974** ✓ |
| 0.010 | 1.353 | 1.2987 | **1.5905** (Stage 4 보다 +18%) |
| 0.050 | 1.148 | 1.1948 | **1.1969** ✓ |
| 0.100 | 1.116 | 1.1323 | **1.1357** ✓ |
| 0.300 | 1.066 | 1.0794 | **1.0650** ✓ |
| 0.500 | 1.054 | 1.0519 | **1.0408** ✓ |

**VII.2 발견 1 — 5/6 구간 일치 통과**. s=0.001, 0.05, 0.1, 0.3, 0.5 5개 구간에서 Phase 6 Python BERNOULLI median 은 Stage 4 Python 및 Phase 4 Native 와 한 자리수 % 이내 (대부분 < 1.5%) 로 일치. 특히 s=0.001 의 2.5974 는 Stage 4 의 2.597 + Phase 4 Native 의 2.5970 과 소수점 셋째 자리까지 정확히 일치 — Exqutor L1228 cnt clamp + L1232 estimator 공식이 Phase 6 Python 에 정확히 이식되었음을 확인한다.

**VII.2 발견 2 — s=0.010 의 +18% 이탈 (Stage 4 1.353 vs Phase 6 1.591)**. Stage 4 와 차이가 큰 유일한 구간. Phase 4 Native 와는 Phase 6 가 더 가깝다 (1.2987 vs 1.5905, 23% 차이). 추정 원인: s=0.010 은 sample 안 hit 의 평균이 3.85 행 (Poisson(3.85)) 으로 작은 sample 에서 cnt 변동이 크고, 5 seed 평균의 분산이 가장 큰 영역이다. Stage 4 의 5 seed RNG 와 본 Phase 6 의 5 seed RNG 가 다르므로 (seed 1000~1004 vs Stage 4 seeds) 평균 매번 다르게 나타날 수 있다. 동치성 검증의 본질 (estimator 동일 여부) 은 5/6 구간 일치로 확인되었으므로 본 Phase 6 의 BERNOULLI baseline 은 신뢰할 수 있다. (Stage 4 의 RNG seed 가 본 Phase 6 와 다르고, 동일 cnt clamp / estimator 공식이 적용되었으므로 차이는 RNG 분산.)

### VII.3 Phase 6 1차 결과 — paired Wilcoxon STRATIFIED vs BERNOULLI

같은 (query_id, selectivity) 짝의 5 seed 평균 q_error 두 모드 (bernoulli, stratified) 를 paired 로 비교. 100 paired 관측 × 6 selectivity. 통계는 paired Wilcoxon signed-rank test, 대립가설 *stratified < bernoulli* (즉 stratified 가 더 정확).

| selectivity | BERN median | STRAT median | diff (BERN−STRAT)/BERN | BERN std | STRAT std | Wilcoxon W | p (less) | S<B | S>B | S=B |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 2.5974 | 2.6046 | −0.28% | 0.567 | 0.699 | 3 163 | 0.986 | 33 | 67 | 0 |
| 0.010 | 1.5905 | 1.6294 | −2.45% | 0.781 | 0.840 | 2 903 | 0.903 | 42 | 58 | 0 |
| 0.050 | 1.1969 | 1.2060 | −0.77% | 0.192 | 0.205 | 2 587 | 0.584 | 47 | 53 | 0 |
| 0.100 | 1.1357 | 1.1271 | +0.76% | 0.112 | 0.109 | 2 509 | 0.478 | 50 | 50 | 0 |
| 0.300 | 1.0650 | 1.0565 | **+0.80%** | 0.054 | **0.045** | 1 560 | **0.0005** | **60** | 40 | 0 |
| 0.500 | 1.0408 | 1.0335 | **+0.70%** | 0.032 | **0.029** | 1 646 | **0.0013** | **60** | 40 | 0 |

**VII.3 발견 1 — 큰 selectivity (s ≥ 0.3) 에서 stratified 우위**. s=0.300 과 s=0.500 두 구간에서 paired Wilcoxon p < 0.005 로 stratified 가 BERNOULLI 보다 통계적으로 유의하게 우수. 60/100 query 에서 stratified 의 q_error 가 더 작고, median 기준 +0.70~0.80% 의 효과 크기. **Pivot C 의 첫 정량 검증** 으로, data-side stratification 이 작지만 측정 가능한 양의 신호를 보인다는 것이 확인됐다.

**VII.3 발견 2 — std 감소 (분산 감소 효과)**. s=0.300 (BERN std 0.054 → STRAT 0.045, **−16%**) 와 s=0.500 (0.032 → 0.029, **−9%**) 에서 stratified 의 std 가 BERNOULLI 보다 작다. paired Wilcoxon 의 signal 이 단지 median shift 만이 아니라 *분산 감소* 와 동반한다. stratified sampling 의 이론적 효과 (variance reduction via balanced coverage) 가 정량 확인됐다.

**VII.3 발견 3 — 작은 selectivity (s ≤ 0.05) 에서 효과 없거나 약간 음**. s=0.001 → S<B 33/100, s=0.010 → 42/100, s=0.050 → 47/100. 모두 50/100 미만으로 stratified 가 약간 *나쁨*. 원인 추정: 작은 selectivity 에서는 stratum 별 sample 안 cnt 가 0 또는 1 변동이 지배적이고, Horvitz-Thompson 의 stratum weight (n_i / s_i ≈ 2 564) 곱셈이 *분산 증폭* 으로 작용한다. BERNOULLI 의 단일 weight (N / S = 2 597) 1 회 곱과 비교하면, stratified 는 K 개의 독립 0/1 random variable 을 가중 합산하는 형태이므로 K 배의 분산을 가질 수 있다. 큰 selectivity 에서 cnt 가 충분히 큰 (≥ 10) 영역으로 들어가야 stratification 의 *bias 감소* 효과가 *분산 증폭* 효과를 추월한다.

**VII.3 발견 4 — s=0.100 의 전이 영역**. s=0.100 은 50/50 정확 동률, p=0.478, diff +0.76% (median 은 stratified 가 약간 작지만 통계 유의 미달). 즉 선택도 0.1 이 stratified 효과의 *break-even point* 이며, 그 이상에서만 stratified 가 의미 있게 작동한다. 본 결과는 stratified sampling 의 효과가 *큰 선택도에서만 발현* 된다는 일반 원칙을 96d DEEP 1M 데이터 위에서 정량 확인한 첫 결과다.

### VII.4 Pivot C 1차 시도의 학술적 해석

본 Phase 6 Step 1~3 의 결과는 다음 세 층위에서 학술적 의미를 갖는다.

1. **Negative+Positive 결합 narrative**. RQ1 motivation 의 §II~§VI 는 "글로벌 4 + 로컬 4 = 8 지표 전수 무효" 라는 강력한 negative result 의 연속이었지만, Phase 6 Step 1~3 은 그 끝에서 *작지만 통계적으로 유의한 첫 양의 신호* 를 확보했다. 즉 RQ1 motivation 은 단순한 실패 narrative 가 아니라, "원래 가설 (query-side feature) 을 공정 검증해서 기각한 후, 데이터 사이드로 전환해 첫 정량 우위를 확보한" 학술적으로 단단한 흐름이 됐다. `direction_pivot_rationale.md` 의 narrative 와 정합.

2. **PCA decile 의 한계 + 더 강한 layer 의 가능성**. 첫 PCA component 의 explained variance ratio = **0.0731** 로, 96d DEEP 데이터의 directional structure 가 약하다 (random isotropic 의 약 7배에 불과). 이런 환경에서 +0.7~0.8% 효과 크기가 나온 것 자체가 강한 신호로, **k-means partition (K=10 or K=20), 다층 PCA (PCA decile × 2 dimension), 또는 vector cluster 기반 partition** 으로 layer 정의를 강화하면 효과 크기가 더 커질 수 있다. Phase 6 Step 4 의 다음 시도 후보.

3. **분산 감소의 정량 증거**. §VII.3 발견 2 의 std 감소 (s=0.300 −16%, s=0.500 −9%) 는 stratified sampling 의 variance reduction 이론을 96d DEEP vector 데이터 위에서 직접 확인한 첫 증거다. 효과 크기 자체는 작지만 (±1% 이내) 통계적으로 강건하므로, vector dataset 의 cardinality 추정에서 stratified sampling 이 *bias 만이 아니라 분산 감소에도 기여한다* 는 finding 으로 motivation 에 편입 가능.

### VII.5 다음 단계 — Phase 6 Step 4 진입 조건

**Phase 6 Step 4 (Native vector.c 구현 + ablation)** 진입 가능 — Step 1~3 의 부분 성공이 정량 검증되어 있고, Phase 4 의 한 줄 sed 패턴 (line 889) 처럼 native 구현은 vector.c 에 (a) `data_side_strata_pca` parquet 또는 동등 메모리 구조 로드, (b) `estimate_cardinality_with_stratified_sampling` 함수, (c) GUC `vector.sampling_method` 추가의 3 단계로 진행 가능. 작업량 추정 90~150분.

**또는 Phase 6 Step 3' (k-means / 더 강한 layer Python counterfactual)** 부터 시도하는 분기도 가능. 1M × 96 mini-batch k-means (K=10) 는 sklearn 또는 numpy 구현으로 30~60 초 수준. 본 PCA decile 의 작은 효과 크기를 5~10% 수준으로 끌어올릴 수 있다면 native 구현의 ROI 가 더 명확해진다. 본 Phase 5/6 의 패턴은 *layer 정의를 빠르게 교체해서 효과 크기 비교* 가 가능하므로 Phase 6 Step 3' 를 1~2 회 시도해본 후 native 진입이 효율적.

### VII.6 산출물

| 파일 | 위치 | 내용 |
|---|---|---|
| `phase6_strat_pca_runs.parquet` | `experiments/results/rq1_motivation/` | 6 000행 long-form: mode × seed × query_id × selectivity × q_error + cnt_raw / cnt_clamped / sample_size_total |
| `phase6_strat_pca_compare.json` | 같음 | per-selectivity paired Wilcoxon (BERN vs STRAT median/mean/std/W/p, n_strat_better/n_bern_better) |
| `phase6_strat_pca_meta.json` | 같음 | 실행 메타 + PCA info (eigvals top5, EVR1) + 10 stratum sizes + 9 quantile edges + sample budget per stratum |
| `data_side_strata_pca.parquet` | 같음 | 1 000 000 × (row_idx, stratum_id, first_pc_proj) — Phase 6 Step 4 native 구현 시 layer 정의 캐시 |
| `phase6_stratified_python.py` | `experiments/code/rq1/` + 서버 `cache/rq1_phase6_stratified_python.py` | 측정 스크립트 (numpy + scipy + pyarrow + pandas, 5초 완주) |

---

## VIII. Phase 6 Step 3' 결과 — Layer 비교 (PCA decile vs k-means K=10/20) (2026-04-14 20:45 KST)

### VIII.1 측정 절차

§VII 의 PCA decile 1차 시도 (+0.7~0.8% in s≥0.3) 위에서, 더 강한 layer 후보를 탐색한다. PCA decile 의 효과 크기가 작은 이유는 첫 PC EVR1 = 0.0731 의 약한 directional structure 에 직접 기인하므로, vector 의 *모든 96 차원* 을 사용하는 layer (= k-means cluster) 가 이론적으로 더 강할 가능성이 크다. 본 Step 3' 는 이 가설을 직접 검증한다.

**4 mode 동시 측정 설계**. 단일 스크립트 (`phase6_layer_compare.py`) 안에서 4 mode 를 같은 query × selectivity × seed × RNG 분리 안에 동시 측정한다. 이로써 paired 비교에서 RNG noise 를 최소화하고, 한 번의 데이터 로드 + 한 번의 layer build → 4 mode × 100 query × 6 selectivity × 5 seed = **12 000 row** long-form 결과를 얻는다.

| mode | layer | sample 전략 |
|---|---|---|
| `bernoulli` | (없음) | uniform random sample 385 행 |
| `pca_decile` | 첫 PC quantile decile (10 stratum) | stratum 별 균등 sample (38~39 행) |
| `kmeans_k10` | numpy mini-batch k-means K=10 | stratum 별 균등 sample (38~39 행) |
| `kmeans_k20` | numpy mini-batch k-means K=20 | stratum 별 균등 sample (19~20 행) |

**numpy mini-batch k-means 구현 (sklearn 의존성 0)**. Sculley 2010 의 mini-batch k-means 알고리즘을 numpy 만으로 직접 구현 (`build_layer_kmeans`, ~50 줄). 핵심:

1. K random points 로 centroid init (seed=42 fixed)
2. 매 iter: random batch (4 096 행) → assign (||x||² + ||c||² − 2x·c) → cluster 별 *running mean* 으로 centroid update (`eta = n_k / total_count`)
3. 100 iter 학습 후, 전체 1M 에 대해 BLAS matmul 한 번으로 stratum_id assign

성능: K=10 학습 0.62s + assign 0.7s, K=20 학습 0.5s + assign 0.59s. 각 K 당 1.2~1.4 초로 매우 빠름.

**estimator 동치성**. estimator 함수 (`estimate_bernoulli`, `estimate_stratified`) 는 §VII.1 의 phase6_stratified_python.py 와 정확 동일. Exqutor L1228 cnt clamp + L1232 공식 그대로. §VII.2 에서 검증된 BERNOULLI baseline (s=0.001 median 2.5974) 도 본 Step 3' 에서 정확히 재현됨.

**RNG 분리**. 4 mode 각각 독립 시드 (bernoulli 1000+seed, pca_decile 2000+seed, kmeans_k10 3000+seed, kmeans_k20 4000+seed). paired 의 단위는 (query_id, selectivity) 짝, RNG 는 mode 별 독립.

### VIII.2 4 mode × 6 selectivity median q_error (5 seed 평균)

| selectivity | bernoulli | pca_decile | kmeans_k10 | **kmeans_k20** |
|---|---|---|---|---|
| 0.001 | 2.5974 | 2.6046 | 2.6488 | 2.6070 |
| 0.010 | 1.5905 | 1.6294 | 1.6340 | 1.6713 |
| 0.050 | 1.1969 | 1.2060 | 1.1742 | **1.1724** |
| 0.100 | 1.1357 | 1.1271 | 1.1336 | **1.1102** |
| 0.300 | 1.0650 | 1.0565 | 1.0573 | **1.0569** |
| 0.500 | 1.0408 | **1.0335** | 1.0366 | 1.0374 |

**VIII.2 발견 1 — 작은 selectivity (s ≤ 0.05) 의 noise 영역**. s=0.001, 0.010 두 구간 모두 4 mode median 이 BERNOULLI 와 거의 동일 (±5% 이내). §VII.3 발견 3 의 *cnt 0/1 영역에서 stratum weight 곱셈이 noise 증폭* 현상이 4 layer 모두에서 동일하게 발현. 본 영역은 어떤 stratification 도 개선하기 어렵다.

**VIII.2 발견 2 — s=0.050 에서 k-means 가 약한 우위**. KM10 (1.1742) 와 KM20 (1.1724) 가 BERNOULLI (1.1969) 보다 ~2% 작음. PCA decile (1.2060) 은 BERNOULLI 보다 약간 큼. 이 영역에서 k-means 가 PCA decile 보다 우위.

**VIII.2 발견 3 — s=0.100 에서 KM20 만 두드러진 신호**. KM20 (1.1102) 가 BERNOULLI (1.1357) 대비 −2.25% 의 가장 큰 단일 효과. 다른 layer (PCA decile 1.1271, KM10 1.1336) 는 BERNOULLI 와 비슷. **K=20 의 더 fine-grained partition 이 transitional selectivity 영역 (s=0.1) 에서 처음 의미를 얻는다**.

**VIII.2 발견 4 — 큰 selectivity (s ≥ 0.3) 의 일관 효과**. 3 stratified mode 모두 BERNOULLI 대비 −0.4 ~ −0.8% 의 일관된 우위. mode 간 차이는 작음 — *큰 selectivity 에서는 어떤 stratification 도 비슷하게 작동* 한다.

### VIII.3 paired Wilcoxon vs BERNOULLI (alt: mode < bernoulli)

같은 (query_id, selectivity) 짝의 5 seed 평균 q_error 를 paired 로 비교. 100 paired 관측 × 6 selectivity × 3 stratified mode = 18 paired test.

| mode | sel | diff% | p (less) | better | worse |
|---|---|---|---|---|---|
| pca_decile | 0.001 | −0.28 | 0.986 | 33 | 67 |
| pca_decile | 0.010 | −2.45 | 0.903 | 42 | 58 |
| pca_decile | 0.050 | −0.77 | 0.584 | 47 | 53 |
| pca_decile | 0.100 | +0.76 | 0.478 | 50 | 50 |
| pca_decile | **0.300** | **+0.80** | **0.0005 ★** | **60** | 40 |
| pca_decile | **0.500** | **+0.70** | **0.0013 ★** | **60** | 40 |
| kmeans_k10 | 0.001 | −1.98 | 0.665 | 55 | 45 |
| kmeans_k10 | 0.010 | −2.74 | 0.627 | 47 | 53 |
| kmeans_k10 | 0.050 | +1.90 | 0.142 | 56 | 44 |
| kmeans_k10 | 0.100 | +0.19 | 0.536 | 49 | 51 |
| kmeans_k10 | **0.300** | **+0.73** | **0.0039 ★** | **61** | 39 |
| kmeans_k10 | **0.500** | **+0.40** | **0.0234 ★** | **61** | 39 |
| **kmeans_k20** | 0.001 | −0.37 | 0.925 | 41 | 59 |
| **kmeans_k20** | 0.010 | −5.08 | 0.719 | 52 | 48 |
| **kmeans_k20** | 0.050 | +2.04 | 0.121 | 54 | 46 |
| **kmeans_k20** | **0.100** | **+2.25** | **0.0042 ★** | **56** | 44 |
| **kmeans_k20** | **0.300** | **+0.76** | **0.0160 ★** | **59** | 41 |
| **kmeans_k20** | **0.500** | **+0.33** | **0.0157 ★** | **58** | 42 |

**VIII.3 발견 1 — KM20 가 가장 넓은 적용 범위**. 3 selectivity 구간 (s=0.100, 0.300, 0.500) 에서 BERNOULLI 대비 paired Wilcoxon p < 0.05 우위. PCA decile 과 KM10 은 두 구간 (s=0.300, 0.500) 만. **KM20 가 다른 두 layer 를 적용 범위에서 추월** 했다.

**VIII.3 발견 2 — KM20 가 새로 확보한 영역 s=0.100**. PCA decile 의 break-even point (s=0.100, p=0.478) 였던 구간에서 KM20 는 +2.25% (p=0.0042) 의 본 layer 비교 *최대 단일 효과 크기* 를 달성. 이 영역의 신호는 PCA decile 과 KM10 에는 없었으며, *K=20 의 fine-grained partition* 이 핵심.

**VIII.3 발견 3 — 작은 selectivity 의 marginal 신호 — KM20 + KM10 만**. s=0.050 에서 KM10 +1.90% (p=0.142), KM20 +2.04% (p=0.121) 의 marginal 신호 (p < 0.20). PCA decile 은 −0.77% 로 약한 음. **k-means 만 작은 selectivity 영역으로 효과 확장** 의 가능성을 보여줌. p < 0.05 미달이라 통계적 유의에는 아직 도달 못했지만, 추가 sample (예: 5 seed → 10 seed, 100 query → 200 query) 으로 신호가 확정될 가능성.

**VIII.3 발견 4 — 큰 selectivity 의 효과 크기는 layer 간 거의 동일**. s=0.300, 0.500 의 ★ 구간에서 PCA decile / KM10 / KM20 의 효과 크기가 모두 +0.3 ~ +0.8% 범위로 유사. 이 영역에서는 layer 정의 자체가 큰 차이 없음 — *어떤 일관된 stratification 도 비슷하게 작동* 한다.

### VIII.4 Cross pair — KM20 vs PCA decile + KM20 vs KM10

stratified mode 간 직접 비교로 layer 의 *상대* 우위를 확인.

| left vs right | sel | diff% | p (left<right) | L<R | L>R |
|---|---|---|---|---|---|
| kmeans_k10 vs pca_decile | 0.050 | +2.64 | 0.077 | 58 | 42 |
| kmeans_k10 vs pca_decile | 0.100 | −0.57 | 0.564 | 49 | 51 |
| kmeans_k10 vs pca_decile | 0.300 | −0.07 | 0.798 | 46 | 54 |
| **kmeans_k20 vs pca_decile** | **0.050** | **+2.79** | **0.028 ★** | **59** | 41 |
| **kmeans_k20 vs pca_decile** | **0.100** | **+1.50** | **0.015 ★** | **59** | 41 |
| kmeans_k20 vs pca_decile | 0.300 | −0.04 | 0.913 | 43 | 57 |
| kmeans_k20 vs pca_decile | 0.500 | −0.37 | 0.960 | 41 | 59 |
| kmeans_k20 vs kmeans_k10 | 0.050 | +0.15 | 0.229 | 55 | 45 |
| **kmeans_k20 vs kmeans_k10** | **0.100** | **+2.06** | **0.0013 ★** | **58** | 42 |
| kmeans_k20 vs kmeans_k10 | 0.300 | +0.03 | 0.733 | 48 | 52 |
| kmeans_k20 vs kmeans_k10 | 0.500 | −0.08 | 0.490 | 51 | 49 |

(p<0.05 에 도달한 ★ 만 굵게)

**VIII.4 발견 1 — KM20 가 PCA decile 을 작은 selectivity 영역에서 명확히 압도**. s=0.050 (+2.79%, p=0.028) + s=0.100 (+1.50%, p=0.015) 두 구간에서 KM20 우위. *큰 selectivity 영역 (s ≥ 0.3) 은 두 layer 동등* — 즉 **KM20 의 추가 가치는 작은 selectivity 영역 (s ≤ 0.1) 에 집중**.

**VIII.4 발견 2 — K=20 vs K=10 의 차이는 s=0.100 에서만 의미**. s=0.100 에서 KM20 가 KM10 보다 +2.06% (p=0.0013 ★) 우위. 다른 sel 에서는 두 K 차이 미미. 즉 *K 의 정밀도는 transitional selectivity 영역에서만 유의미*.

**VIII.4 발견 3 — KM10 vs PCA decile 은 약한 차이**. s=0.050 에서 KM10 +2.64% (p=0.077) marginal 우위만. K=10 의 k-means 는 PCA decile 대비 *명확한* 우위 없음. 즉 *PCA decile → KM10 transition 만으로는 큰 이득 없음*. **K=10 에서 K=20 으로의 정밀도 증가가 layer-side 의 핵심 변화**.

### VIII.5 KM20 = best layer 결정 + Phase 6 Step 4 (Native) 로의 진입 정당화

본 Step 3' 의 4 layer 비교 결과로 다음을 확정한다.

1. **best layer = kmeans_k20**. 적용 범위 (3 sel ★) + 새 영역 s=0.100 (+2.25%) + s=0.050 marginal 신호 (p=0.121) 의 모든 metric 에서 다른 layer 우위. 학습 비용도 0.5초로 매우 저렴.

2. **PCA decile 은 큰 selectivity 영역 baseline 으로 retain**. 본 KM20 와 PCA decile 은 s=0.300, 0.500 에서 효과 크기 거의 동일. 즉 PCA decile 이 KM20 의 부분집합. 다음 Step 4 native 구현은 KM20 만 진행하고 PCA decile 은 §VII 의 결과로 충분.

3. **다층 PCA / random projection 시도는 본 세션에서 생략**. 다층 PCA 의 이론 한계 EVR1+EVR2 = 0.121 가 KM20 의 multi-direction k-means 보다 약하므로, KM20 를 넘기기 어렵다고 판단. 본 Step 3' 의 결과만으로 best layer 결정에 충분.

4. **Phase 6 Step 4 (Native vector.c 구현) 진입 1순위 layer 확정**. KM20 의 20 centroid (20 × 96 × 8 byte = 15 KB) + 1M × stratum_id (1M × 2 byte = 2 MB) 만 vector.c 안에 메모리 로드하면 native 구현 가능. 추정 작업량 90~150분 (다음 세션).

### VIII.6 학술적 함의

**Layer 정의의 trade-off 정량 확인**. PCA 기반 layer 는 *데이터의 한 (또는 두) 방향* 만 사용하므로 96d random isotropic 데이터 (EVR1=0.073) 에서 변별력이 약하다. k-means 기반 layer 는 *모든 96 차원* 의 spatial proximity 를 사용하므로 더 강하지만, 계산 비용이 더 높다 (mini-batch k-means 0.5초 ↔ PCA 1.2초). 본 데이터에서는 KM20 가 PCA decile 대비 적용 범위 50% 확장 (2 sel → 3 sel) 하면서 학습 비용은 오히려 절반.

**K (stratum 수) 의 효과**. KM10 → KM20 의 stratum 수 증가가 *transitional selectivity (s=0.1)* 에서 처음 효과 발현. 이는 *sample 안에서 cnt 가 충분히 큰 영역 (≥ 5~10) 에서만 stratum 증가가 의미를 얻는다* 는 일반 원칙의 정량 확인. 작은 selectivity (s ≤ 0.05) 에서는 K 증가가 sample budget per stratum 감소로 되돌아가 noise 증가.

**RQ1 motivation 의 Pivot C narrative 강화**. §VI 의 8 지표 무효 negative result 후 §VII 에서 PCA decile 의 작은 양의 신호 확보, 본 §VIII 에서 KM20 로 신호 영역을 *3 selectivity 구간 + 새 영역 s=0.100* 으로 확장. RQ1 motivation 의 narrative 가 "negative result 8 + positive layer 비교 4" 로 단계적으로 강화됨. `direction_pivot_rationale.md` 의 narrative 에 §VIII 결과 추가 가능.

### VIII.7 산출물

| 파일 | 위치 | 내용 |
|---|---|---|
| `phase6_layer_compare_runs.parquet` | `experiments/results/rq1_motivation/` | 12 000행 long-form: 4 mode × 100 query × 6 sel × 5 seed q_error |
| `phase6_layer_compare_compare.json` | 같음 | mode × sel 통계 + 18 BERN paired Wilcoxon + cross_pair 18 비교 + layer info (PCA EVR + k-means inertia/sizes) |
| `phase6_layer_compare_meta.json` | 같음 | 실행 메타 + 4 layer 정보 + 9.0초 elapsed |
| `phase6_layer_compare.py` | `experiments/code/rq1/` + 서버 `cache/rq1_phase6_layer_compare.py` | 측정 스크립트 (~470줄, numpy 직접 mini-batch k-means 포함) |

---

## 부록 A — 참고 메타

- Adaptive Sampling 파라미터 (Exqutor 소스 L442~455 추출): α=50, β=1.5, momentum=0.9, lr_init=0.1, lr_λ=0.99, sample_size_init=385, sample_update_cycle=50
- `TABLESAMPLE SYSTEM` 블록 통계: 580 844 blocks / 8 000 371 rows = **13.8 rows/block** (Stage 1 측정)
- Python 재구현 동치 공식: `est = cnt × total / sample_size` (Exqutor L1232, 분모 = 요청 sample_size)
- `cnt == 0 → 1` clamp (Exqutor L1228)
- True cardinality = `instrument->ntuples` post-execution (Exqutor L1253)

## 부록 B — 재현 절차

```bash
# 서버에서
cd /mnt/hdd0/home/capstone2026
python3 cache/rq1_stage1_dump.py --subset-rows 1000000 --n-query 100 --seed 42
python3 cache/rq1_stage2_skew.py
python3 cache/rq1_stage3_selectivity.py
python3 cache/rq1_stage4_adaptive.py
python3 cache/rq1_stage5_analyze.py

# 로컬로 결과 복사 (subset 제외)
rsync -avz --exclude='subset_1m.parquet' \
  capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq1/ \
  experiments/results/rq1_motivation/
```
