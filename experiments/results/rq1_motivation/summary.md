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

**총 실행 시간**: 약 3 분. 단일 세션 내 RQ1 전체 파이프라인 완주.

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

**Phase 4 (다음 세션 첫 작업)** — Pivot A 네이티브 실증. `src/vector.c` L1192의 `TABLESAMPLE SYSTEM(%f)`을 `TABLESAMPLE BERNOULLI(%f)`로 한 줄 교체 + `vector.so` 재빌드 + 동일 100 query 재실행. 단일 테이블 시나리오에서 두 모드 모두 같은 plan replacement 경로를 타도록 강제한 채로 **상대값(SYSTEM 대비 BERNOULLI의 q_error 차이)**을 측정. 절대값 비교가 아니므로 plan replacement의 부작용은 두 모드에서 동일하게 cancel. Python counterfactual의 +3.8~9.1%p 감소 수치와 일치하는지 확인. 또는 multi-table 검증 query format(`partsupp_deep_10_subset_1m JOIN part_10 JOIN supplier_10`)으로 전환해서 Exqutor의 design intent에서 직접 측정하는 옵션도 보존 (Phase 4 진입 시점에 결정).

**Phase 5 — Local skew 지표 4종 구현 + 재측정**. global 4 지표 대신 local 지표로 전환: (i) k-NN distance entropy(k=50), (ii) query 주변 k-NN의 PCA explained variance ratio, (iii) KDE modality count(pilot sample n=500), (iv) query-conditional NN clustering coefficient. Python Stage 2 확장으로 구현 → Phase 4의 BERNOULLI baseline 위에서 4 지표 × Q-error Spearman 재측정. 유의 신호 보인 지표 식별이 Phase 6의 층 정의 후보가 된다.

**Phase 6 — Stratified Sampling 함수 설계 + 구현**. Exqutor에 `estimate_cardinality_with_stratified_sampling(total_rows, num_strata)` 추가. 구조는 (a) dataset 전체에 대해 pre-compute된 global distance histogram으로 층 경계(예: 10 분위수) 산출, (b) 층별 균등 샘플 추출, (c) 가중 카디널리티 추정. 새 GUC `vector.sampling_method` (`system` / `bernoulli` / `stratified`) 도입해 세 모드 ablation 가능하게. Phase 5의 유의 지표를 층 정의 기준으로 사용.

**Phase 7 — 중간발표용 부분 실증 (~4/26)**. `partsupp_deep_10` 단일 dataset에서 3 mode × 6 selectivity × 5 seed 최소 ablation. Table: SYSTEM vs BERNOULLI vs STRATIFIED의 median/mean/p95 Q-error. 방향의 타당성 증명이 목표.

**Phase 8 — 최종보고서용 완성 실증 (~6/11)**. 3 dataset(deep 96d/sift 128d/wiki 768d) × 1000 query × 20 seed × 3 mode × 8 selectivity × 4 skew bin 전면 ablation. Track B(KDE-pilot online 층화) 추가 구현. Stage 5b 시각화 7~8 figure 완성.

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
