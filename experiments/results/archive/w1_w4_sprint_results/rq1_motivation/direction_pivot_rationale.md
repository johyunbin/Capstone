# RQ1 방향 전환의 동기 — 4/3 합의에서 4/14 정의로의 진화

**작성일**: 2026-04-14 19:15 KST
**작성자**: 조현빈 (Claude Code 보조)
**용도**: 자문내역서 + 중간보고서 narrative
**대상 미팅**: 2026-04-15~04-17 자문 미팅 (예정)
**관련 문서**: `summary.md` §III.3, `equivalence_check.md` §X, `records/kakaotalk/20260403_교수님미팅 샘플링방향전환.md`

---

## 0. 요약

본 절은 4월 3일 교수님과 합의된 *Distribution-Aware Stratified Sampling for multi-table vector range query* 라는 출발 가설이 4월 14일 하루의 검증 사이클을 거치면서 *Single-table vector range query 사각지대에서의 Pivot A+C 병합 노선* 으로 정교화된 경로를 정직하게 정리한다. 전환은 네 단계로 자연스럽게 이어졌다. ① 4/3 합의의 출발점, ② 4/14 오전 RQ1 1차 실험에서의 가설 H1 기각, ③ 4/14 오후 17:35 KST의 두 가지 대체 신호 발견과 Pivot A+C 정의, ④ 4/14 18:00~19:00 KST 옵션 A 시도 중 발견된 네 가지 Exqutor design constraint와 그중 두 가지의 motivation 격상이다. 각 단계는 직전 단계의 검증 결과 위에서 자연스럽게 이어지며, **이 전환은 우회가 아닌 진화**다. 4/3 합의의 핵심 — Exqutor의 vector range query 카디널리티 추정 정확도를 skewed 환경에서 개선한다 — 는 그대로 유지된 채, 시나리오 정의와 motivation framing이 정량적 데이터 위에서 정교화된 결과다.

본 narrative는 자문 미팅에서 위 4단계 진행 경과를 보고하고 사후 합의를 받기 위한 자료이며, 동시에 중간보고서 (4/28) §3 Motivation 절의 직접 인용 가능한 형태로 작성되었다.

---

## 1. 출발점 — 2026-04-03 교수님 합의

본 연구의 기초는 2026년 4월 3일 금요일 교수님과의 1시간 미팅에서 확정되었다. 그 직전까지 본 팀은 *Cascaded Vector Similarity Decomposition* (플래닝 시간 단축을 위한 단계적 벡터 유사도 분해)을 본선 주제로 검토하고 있었으나, 4/3 미팅에서 교수님은 본 팀의 출발 자산 — Exqutor 논문에 대한 구조적 이해 — 를 살리는 방향으로 **Adaptive Sampling의 정확도 개선**을 제안했다. 핵심 관찰은 Exqutor의 Adaptive Sampling이 데이터가 고르게 분포된(well-distributed) 환경에서는 잘 작동하지만, 분포가 치우친(skewed) 상황에서는 카디널리티 추정 정확도가 떨어진다는 것이었다. 특히 멀티조인 + 필터링된 벡터 데이터베이스 시나리오에서 distribution이 정렬되지 않고 치우쳐 있는 상황을 motivation으로 제시해야 한다는 가이드를 받았다.

이로부터 본 팀은 다음 두 가지 트랙을 본선 노선으로 정의했다. **트랙 A — Distribution-Aware Sampling** 은 분포를 안다는 가정 하에 left-skew, normal, right-skew 각각에 대해 서로 다른 샘플링 전략을 적용하고, 무작위 샘플링 결과의 정확도 차이를 실증한 뒤 더 정확한 추정을 만드는 방법을 제안한다. **트랙 B — Distribution-Agnostic Sampling** 은 분포를 전혀 모르는 상황에서도 skew에 robust한 샘플링 기법을 연구하며, Latin Hypercube Sampling (LHS) 등을 백그라운드로 검토한다. Exqutor 원논문이 LHS를 구현 복잡도 문제로 고려하지 않았다는 점도 본 팀이 탐구할 여지로 명시되었다.

motivation의 학술적 구조는 세 단계로 합의되었다. 첫째, 고른 분포와 skew 분포에서 Exqutor의 sampling 정확도 차이를 실험적으로 보인다. 둘째, 이 차이가 통계적으로 유의미함을 확인해서 *skew-aware sampling이 필요하다* 는 동기를 확보한다. 셋째, distribution-aware와 distribution-agnostic 두 시나리오에서 각각 개선된 샘플링 기법을 제안하고 정량 비교한다. 시나리오 자체는 **multi-table join with vector range filter** 를 본선으로 가정했고, 이는 Exqutor 원논문이 본인의 핵심 기여 영역으로 제시한 시나리오와 일치한다.

본 합의 직후의 후속 작업은 (i) LHS 백그라운드 연구, (ii) 연구실 서버 수령과 환경 세팅, (iii) 기존 설계안과 제안서를 새 방향으로 수정하는 것이었다. 4/3 미팅에서 합의된 motivation의 핵심 가설을 본 보고서는 H1으로 호명하며, 그 정의는 다음과 같다.

> **가설 H1 (4/3 출발)**: 거리 분포의 skewness가 클수록 Exqutor Adaptive Sampling의 카디널리티 추정 Q-error가 증가한다. 특히 Fisher γ의 절대값이 1을 초과하는 분포에서는 Q-error가 uniform 분포 대비 2배 이상 악화된다.

이 가설은 4/3 합의의 motivation을 **검증 가능한 정량적 명제**로 환원한 것이며, 본 팀이 4/14 오전의 1차 실험 설계에 이를 그대로 옮겨 넣었다.

---

## 2. 첫 검증 — 가설 H1 기각 (2026-04-14 오전 RQ1 1차 실험)

4월 14일 오전, 본 팀은 연세대 BDAI Lab 서버 (`capstone2026@165.132.140.240`, vanilla PG 16.9 + pgvector 0.7.1) 위에 Exqutor 1차 환경을 받아 RQ1 1차 motivation 실험 파이프라인을 5단계로 실행했다. 대상 데이터셋은 `partsupp_deep_10` (TPC-H sf10에 96차원 DEEP 벡터를 결합한 8M행 테이블) 의 1M 서브셋으로, `DISTINCT ON (ps_partkey)` 으로 결정론적으로 추출했다. 100개 query를 무작위 추출하고, 각 query에 대해 6개 선택도 (0.001 / 0.010 / 0.050 / 0.100 / 0.300 / 0.500) × 5 seed로 Adaptive Sampling을 Python에서 재구현해서 q-error를 측정했다. 총 query×선택도×seed = 3,000 측정. 같은 query pool에 대해 4가지 글로벌 skewness 지표 — Fisher γ, Log-Fisher γ, Tail ratio P99/P50, Bowley skew — 를 미리 계산해 두었다. 자세한 절차와 산출물은 `summary.md` §I~II에 정리되어 있다.

검증 결과는 가설 H1을 강하게 기각했다. 4가지 글로벌 skew 지표와 query별 median Q-error 사이의 Spearman 순위 상관은 모든 24개 조합 (4지표 × 6선택도) 에서 절대값 0.2 미만으로, 통계적으로 신호 부재였다. 그룹 비교도 마찬가지로 실패했다. `|Fisher γ| > 1` 인 query 그룹과 `|Fisher γ| < 0.5` 인 query 그룹의 median Q-error 비율은 12개 조합 (2 mode × 6선택도) 모두에서 ratio ≈ 1.0 (구체적으로는 0.99~1.04 범위) 이었으며, 가설 H1이 요구한 *2배 이상 악화* 기준에 어떤 조합도 도달하지 못했다. 가장 작은 선택도 `s=0.001` 에서 Mann-Whitney U 검정의 p값이 0.0009로 매우 낮게 나오긴 했지만, 효과의 *방향* 자체가 가설과 반대로 (low γ 그룹이 미세하게 더 높았음) 나타나 효과의 의미가 없었다. 즉 데이터는 *skew가 클수록 Q-error가 커진다* 는 가설을 기각할 뿐 아니라 *반대 방향이라도 의미 있는 신호* 도 발견하지 못했다.

이 결과는 결정적이었다. 100개 query 모두 Fisher γ가 음수 (range −3.86 ~ −0.32, median −1.07) 로 left-skewed 분포였으며, 본래 설계안 v3가 가정했던 *right-skewed 예시 분포* 와 정반대였다. Tail ratio P99/P50도 1.07~1.17 범위로 매우 좁았는데, 이는 96차원 벡터에서도 *고차원 거리 집중 (distance concentration)* 현상이 강하게 나타난다는 것을 의미한다. 즉 글로벌 거리 분포 자체가 4가지 지표 중 어느 것으로 측정해도 query 간에 충분히 다양한 신호를 만들지 못한다. 글로벌 지표는 고차원 벡터 데이터의 query별 상태를 식별하는 데 부적합하다는 것이 본 1차 실험의 가장 중요한 관찰이었다.

H1 기각 자체는 본 연구의 출발 가설을 직접 부정한 것이지만, 그 부정이 *원래 방향이 틀렸다* 는 판결인지, 아니면 *원래 방향을 검증하기에 적절한 실험이 아니었다* 는 진단인지는 해석의 여지가 있었다. 본 팀의 결정은 후자 — 본 1차 실험은 가설 H1의 첫 단계 (글로벌 skew 지표가 Q-error의 설명변수가 될 수 있는가) 만 검증했고, 본 가설이 함의한 두 번째 단계 (skew 그룹별로 stratified sampling이 uniform sampling보다 우수한가) 는 **Python 재구현이 stratified mode를 가지지 않았기 때문에 검증조차 되지 않았다** 는 점에 주목했다. 따라서 4/3 합의의 본질을 폐기하지 않고, 그 검증 경로를 정교화할 필요가 있었다. 이 정교화 작업이 §3과 §4의 두 단계로 이어진다.

---

## 3. 대체 신호 발견 — Pivot A + C 정의 (2026-04-14 오후 17:35 KST)

H1 기각의 정량 결과 위에서, 본 팀은 같은 데이터에서 두 가지 새로운 신호를 발견했다. 두 신호 모두 4/3 합의의 핵심 (Exqutor 정확도 개선) 을 유지한 채 motivation framing을 정교화한다.

**첫 번째 신호 — 선택도 효과**. 모든 4가지 skew 지표가 Q-error의 설명변수로 작동하지 않는다는 사실은 분명했지만, *선택도* 자체는 강력한 설명변수였다. 6개 선택도 구간에서 median Q-error는 단조 감소했다. 가장 작은 선택도 `s=0.001` 에서 median Q-error는 2.597 (max 8.2) 이었고, 가장 큰 선택도 `s=0.500` 에서 1.054였다. 선택도가 작을수록 Q-error가 구조적으로 증가한다는 것은 직관적 결과이지만, `s=0.001` 의 median 2.6은 실무적으로 의미 있는 수준이다. PostgreSQL 옵티마이저가 카디널리티 추정 오차에 따라 join 알고리즘 (nested loop vs hash join) 을 잘못 선택하기 시작하는 임계점이 일반적으로 ratio 2~3 부근으로 알려져 있고, 본 결과는 그 임계점을 **극소 선택도 구간에서 Adaptive Sampling이 구조적으로 통과한다** 는 것을 보여준다. 이는 4/3 합의의 *정확도 개선이 필요하다* 라는 motivation을 skewness 축이 아닌 **선택도 축으로 정량화한 새로운 근거**다.

**두 번째 신호 — 블록 샘플링 편향 (Block Sampling Bias)**. Python 재구현은 두 가지 sampling mode 를 가지고 있었다. `bernoulli` mode는 행 단위 독립 베르누이 샘플링이고, `block_system` mode는 PostgreSQL의 `TABLESAMPLE SYSTEM` 을 모방한 블록 단위 샘플링이다. 두 mode 모두 같은 Python 함수에서 mask 생성 단계만 달리해서 동일한 q-error 계산 경로를 거친다. 결과는 모든 선택도 (0-clamp 영향 구간 `s=0.001` 제외) 에서 `block_system` 의 median Q-error가 `bernoulli` 대비 일관되게 3.8% (`s=0.010`) 부터 9.1% (`s=0.500`) 까지 더 높았다. Wilcoxon signed-rank paired test (대립가설: SYSTEM > Bernoulli) 도 `s≥0.050` 에서 p < 0.001로 유의했고, `s=0.500` 에서는 100 query 중 89개에서 SYSTEM 쪽이 불리한 방향으로 움직였다. 즉 *블록 단위 샘플링이 행 단위 베르누이 샘플링보다 구조적으로 Q-error를 키운다* 는 것이 4가지 skew 지표 실패와 별개로 통계적으로 강하게 확인되었다.

이 두 번째 신호의 의미는 Exqutor 소스를 정밀 검증한 후에야 드러났다. Stage 4.5 수학적 검증 (`equivalence_check.md` §III~VII) 에서 본 팀은 Exqutor의 `estimate_cardinality_with_sampling()` 함수의 query 조립부 (`vector.c` line 1188~1195) 가 **오직 `TABLESAMPLE SYSTEM`만 사용** 한다는 사실을 확인했다. Exqutor 패치 1562줄 전체에서 `BERNOULLI` 라는 문자열은 단 한 번도 등장하지 않는다. 즉 Python의 `bernoulli` mode는 Exqutor에 존재하지 않는 *counterfactual 시뮬레이션* 이며, "만약 Exqutor가 SYSTEM 대신 BERNOULLI를 썼다면 어떻게 달라질까" 를 측정한 결과다. 따라서 위 9.1%p의 Q-error 차이는 *현재 Exqutor가 자신의 선택으로 떠안은 손실의 크기* 이며, 동시에 **`vector.c` 한 줄을 `TABLESAMPLE SYSTEM(%f)` 에서 `TABLESAMPLE BERNOULLI(%f)` 로 교체하는 한 줄 변경** 이라는 매우 좁고 명확한 개선 경로를 식별해 준다.

이 두 신호로부터 본 팀은 같은 날 17:35 KST에 **Pivot A + Pivot C 병합 노선** 을 확정했다. Pivot A는 *블록 → 베르누이 한 줄 교체* 이고, Pivot C는 *글로벌 skew 지표를 local skew 4지표로 교체한 stratified sampling 본 구현* 이다. Pivot B (선택도 적응형 β) 는 채택하지 않았다. 자세한 결정 근거는 `summary.md` §III.3에 정리되어 있다. 핵심을 요약하면, Pivot A는 **기여가 아니라 fair baseline 구축 도구** 로 재정의되며 (Exqutor의 sampling method 선택이 근거 없이 SYSTEM으로 고정된 점을 정량 ablation으로 드러내는 역할), Pivot C는 **트랙 A의 본 구현** 으로 본선에 배치된다 (글로벌 지표 실패의 연장선에서 local 지표로 skew를 재정의해 stratified sampling을 처음으로 실제 구현).

이 시점 (17:35 KST) 의 본 연구의 학술적 구조는 다음과 같이 정리되었다. Exqutor가 암묵적으로 가정한 두 가지 — *TABLESAMPLE SYSTEM이 적절한 샘플링 메서드이다* 와 *naive uniform sampling이 충분하다* — 를 각각 Pivot A와 Pivot C로 해체한다. 두 해체는 직교적이므로 SYSTEM / BERNOULLI / STRATIFIED × dataset의 ablation matrix로 각 개선의 기여를 분리할 수 있다. 본 1차 실험의 결과 자체 — 글로벌 지표 4종 모두 실패 — 는 이 새 구조에서 *글로벌 지표는 고차원 벡터에서 관측력을 잃는다* 는 부정적 발견 (negative result) 으로 motivation에 편입되어, Pivot C가 local 지표로 전환하는 정당화로 직접 기여한다.

이 17:35 KST 정의는 4/3 합의의 motivation을 두 가지 차원에서 정교화했다. 첫째, 4/3 합의의 skewness 가설이 데이터로 부정되었다는 사실을 *부정 결과 (negative result) 도 기여* 라는 학술적 입장으로 받아들여 motivation의 일부로 편입했다. 둘째, 그 부정 결과 위에서 발견한 두 가지 새 신호 (선택도 효과, 블록 편향) 를 Pivot A의 근거로 삼고, 글로벌 지표 실패의 진단을 Pivot C의 시나리오 정당화로 사용했다. 4/3 합의의 핵심 (Exqutor 정확도 개선) 은 두 Pivot 모두에서 직접 측정되는 학술적 명제로 보존되었다.

---

## 4. Exqutor Design Constraint 발견 — Motivation 강화 (2026-04-14 18:00~19:00 KST)

17:35 KST에 Pivot A+C 노선이 확정된 직후, 본 팀은 옵션 A — Exqutor의 네이티브 바이너리로 Python 재구현 결과를 bitwise 검증 — 를 같은 날 추가 세션에서 즉시 시도했다. 옵션 A의 목표는 §III~V의 수학적 검증을 한 단계 더 강화하는 것이었으며, *Python 재구현의 q-error 분포가 Exqutor 네이티브 q-error 분포와 ±5% 이내로 일치하는가* 를 확인해서 17:35 KST 결정 (Pivot A+C 노선) 의 데이터 신뢰도를 마지막으로 확보하는 것이었다. 본 시도는 4단계로 진행되었으며, 자세한 기록은 `equivalence_check.md` §X에 정리되어 있다. 결론을 먼저 말하면, **옵션 A는 부분 실패** 했고, 그 실패 자체가 본 연구의 motivation을 한 단계 더 강화하는 finding이 되었다.

### 4.1 Phase 2 — 데이터 로드 완주

Vanilla PG 55435의 `partsupp_deep_10` 8M행을 Exqutor PG 55436으로 이전했다. `pg_dump --data-only -Fp -t partsupp_deep_10 | psql --single-transaction` pipe 방식으로 273초 만에 4537 MB를 옮겼고, FK·인덱스·HNSW를 사전에 모두 제외해서 sampling 경로를 강제했다. 같은 Exqutor PG 안에서 `CREATE TABLE partsupp_deep_10_subset_1m AS SELECT DISTINCT ON (ps_partkey) ... WHERE ps_partkey BETWEEN 1 AND 1000000` 로 1M subset을 결정론적으로 재현하고, query_pool.parquet 첫 10개의 ps_partkey/ps_suppkey/벡터 5 element가 1M subset의 같은 행과 완전히 일치함을 확인했다. Phase 2는 완전 통과.

### 4.2 Design Constraint 1 — Hook trigger 조건 (`table_count > 2`)

Phase 3 (네이티브 bitwise 검증) 의 1 query sanity check에서 첫 결함이 드러났다. 모든 query에서 EXPLAIN ANALYZE 의 `Plan Rows` 가 `333,333` (= 1M × 1/3) 으로 동일하게 나왔으며, 50 query 시퀀스를 끝까지 돌려도 `exqutor_qerror` 테이블이 빈 채로 남았다. 즉 Exqutor의 sampling hook이 **단 한 번도 trigger되지 않았다**. PostgreSQL의 default selectivity가 unknown function 에 대해 1/3 인 사실로 미루어, 우리 query는 Exqutor의 hook 경로를 우회해서 PG default fall-through로 갔다는 것이 분명했다.

원인은 Exqutor 패치의 `pgvector_Exqutor.patch` line 547에서 발견되었다. 핵심 한 줄은 다음과 같다.

```c
table_count = 0;
count_total_tables(parse, &table_count);
if (table_count > 2)        // <-- 핵심
{
    ordering_needed = true;
    ...
}
```

`count_total_tables` 함수 (line 1329~) 는 query rangetable의 `RTE_RELATION` 을 세고 `RTE_SUBQUERY` 와 CTE를 재귀로 카운트한다. 본 팀의 검증 query인 `SELECT count(*) FROM partsupp_deep_10_subset_1m WHERE (ps_embedding <-> q) < D` 는 단일 테이블이므로 `table_count = 1 ≤ 2` 이고, 따라서 `ordering_needed = false` 로 남는다. 이후 `pgvector_set_baserel_rows_estimate_hook` 은 standard fall-through 경로 (line 731 `set_baserel_rows_estimate_standard(root, rel)`) 로 빠지며, **sampling 함수 자체에 도달하지 못한다**.

이 발견의 의미는 자명했다. **Exqutor의 Adaptive Sampling은 multi-table join with vector range filter 시나리오로 trigger 조건이 좁혀져 있고, 단일 테이블 vector range query는 PG default selectivity 1/3을 그대로 사용하는 사각지대다**. 이 design constraint는 Exqutor 원논문 본문에 명시되지 않으며, 본 팀의 직접 소스 검증으로 처음 정량 확인된 사실이다. 단일 테이블 vector range query — 예를 들어 *주어진 사진과 유사한 사진을 K개 찾되 거리가 임계값 이하인 것만* — 가 실무에서 더 흔한 시나리오임을 고려하면, 이 사각지대는 본 연구가 새로 제기할 RQ로 자연스럽게 편입된다. 이 첫 번째 design constraint 는 4/14 18:50 KST에 본 연구 motivation의 새 첫 줄 (`summary.md` §III.3 강화 정의 §X.3) 로 격상되었다.

### 4.3 우회 시도 — vector.c line 243 한 줄 수정

옵션 A의 본래 목적 — Python 재구현과 Exqutor 네이티브의 q-error 분포 직접 비교 — 를 살리기 위해, 본 팀은 `vector.c` line 243의 `if (table_count > 2)` 를 `if (table_count >= 1)` 로 한 줄 수정하고, incremental rebuild로 새 `vector.so` (md5 9cd874b... → abbc818a..., 227408 bytes) 를 생성한 뒤 Exqutor PG를 fast restart했다. 변경 전 vector.c는 `vector.c.bak.20260414_1840` 으로 백업했다. 변경 후 1 query EXPLAIN ANALYZE에서 `Plan Rows = 148052` (333,333에서 변동값으로 바뀜) 로 hook이 trigger되고 sampling estimate가 plan에 반영되기 시작했다. 그러나 즉시 세 가지 추가 design constraint 가 드러났다.

### 4.4 Design Constraint 2 — Outer plan replacement (Sample Scan)

Hook trigger 후 EXPLAIN ANALYZE 전체 JSON을 출력했더니 outer query의 plan tree 가 다음과 같이 변경되어 있었다.

```
Aggregate
  └─ Sample Scan on partsupp_deep_10_subset_1m
       Sampling Method: system
       Sampling Parameters: ['0.0385'::real]
       Filter: (ps_embedding <-> '...'::vector) < '1.150729'::double precision
       Plan Rows: 153247    Actual Rows: 38
       Rows Removed by Filter: 322
```

즉 본 팀의 outer query `SELECT count(*) FROM partsupp_deep_10_subset_1m WHERE ...` 가 `SELECT count(*) FROM partsupp_deep_10_subset_1m TABLESAMPLE SYSTEM(0.0385) WHERE ...` 로 **plan-tree 자체가 교체** 되었다. Decisive evidence는 별도 connection에서 `vector.update_sample_size = off` 로 GUC를 끄고 같은 query를 실행해도 `SELECT count(*)` 가 32를 반환했다는 것이다 (Python parquet의 true_cardinality는 100,000). 즉 outer query 의 결과 값 자체가 sample 안의 부분 카운트로 격하되었다.

이 동작의 의미는 다음과 같다. Exqutor의 hook은 단순 cardinality estimation 만을 위한 baserel rows set이 아니라, **plan-tree의 base relation 노드를 PostgreSQL의 Sample Scan 노드로 직접 교체** 하는 동작을 한다. Multi-table join 시나리오에서는 outer query 가 join 결과를 반환하므로 base table sample scan으로의 교체가 join 결과에 부분 영향만 주지만 (join probe 시 다른 테이블의 join key matching 이 정확성을 복원), **단일 테이블 시나리오에서는 outer query 자체가 sample 안 부분 카운트로 격하** 되어 의미를 잃는다. 즉 Exqutor의 hook이 단순한 *추정 정확도 개선* 이 아니라 *추정과 실행을 결합한 plan replacement* 라는 것이 본 발견의 핵심이다.

이 두 번째 design constraint 도 본 연구의 motivation으로 격상되었다 (`summary.md` §III.3 강화 정의 §X.5). "Exqutor의 hook은 cardinality estimation과 plan replacement를 결합해서 동작하는데, 이는 multi-table join 에서는 정상이지만 단일 테이블 vector range query 에서는 outer query의 정확성 자체를 깨뜨린다" 는 finding 은 본 연구의 새 motivation 두 번째 줄이 된다. 첫 번째 design constraint (X.3) 와 함께, 이 두 finding은 본 연구가 Exqutor의 *multi-table only design intent의 사각지대* 를 정량적으로 드러낸다는 학술적 입장을 형성한다.

### 4.5 Design Constraint 3 & 4 — q-error inf 발산과 sample_size NaN 발산

Hook trigger 우회 + plan replacement 우회 후에도 두 가지 추가 결함이 드러났다. 먼저 1 query 실행 직후 `exqutor_qerror` row 를 조회했더니 `recent_qerrors[0] = inf` 이었다. Q-error inf 는 division by zero 의 결과이며, Exqutor 의 q_error 계산식 `Max(estimated/true, true/estimated)` 에서 `true_cardinality = 0` 이라야 한다. 그러나 우리 query 의 outer Sample Scan 의 Actual Rows = 38이므로 `true = 38` 이어야 정상이다. 추정 원인은 plan replacement로 인한 *이중 sampling* 이다 — Exqutor 가 plan-time SPI subquery 에서 한 번 sampling 하고, ExecutorRun 에서 두 번째 sampling 이 일어나는데, 두 sample 의 RNG 가 다르므로 다른 행 집합을 가지며, 첫 sample 에서 0개 매칭이 나온 경우 q_error 계산에 inf 가 들어간다. 두 번째로, 50 query 시퀀스를 돌리는 도중 q[25] 쯤에서 `TABLESAMPLE SYSTEM(NaN)` PostgreSQL parser 에러가 발생했다 (`column "nan" does not exist`). `sample_size` 가 NaN 으로 발산해서 `sample_ratio = NaN` 이 되었고, query string 조립 시 `appendStringInfo("TABLESAMPLE SYSTEM(%f)", NaN)` 이 `nan` 을 column name 으로 PostgreSQL 이 파싱한 결과다. Adaptive Sampling 의 update 식 `sample_size = sample_size + v_grad` 에서 `v_grad` 가 NaN 으로 발산했고, autocommit=False 로 SPI write 을 정상 transaction context 에 넣어도 NaN은 재현되었다.

이 두 추가 결함은 Python 재구현이 60 run 동안 한 번도 발산하지 않았던 사실과 정확히 대비된다. Python은 단일 테이블 시뮬레이션이며 안정적이고, Exqutor 네이티브는 단일 테이블 시나리오에서 수치적으로 발산한다. 이는 **Exqutor 의 Adaptive Sampling loop 가 multi-table only design intent 를 가정하고 만들어진 결과** 임을 한 번 더 확증한다. 다만 이 두 결함은 motivation 의 새 첫 줄로 격상할 정도의 임팩트는 아니며, Phase 4~6 의 구현 단계에서 q_error 계산 경로와 Adaptive loop 안정성을 sanitize해야 함을 시사하는 *기술적 발견* 으로 분류한다.

### 4.6 옵션 A 종합 판정

옵션 A는 다음 의미로 **부분 실패** 다. 단일 테이블 1M subset 시나리오에서 Python Stage 4 의 q-error 분포와 Exqutor 네이티브 의 q-error 분포를 직접 ±5% 이내로 비교하는 검증은 위 네 가지 design constraint 로 인해 불가능하다. 그러나 이는 Python 재구현이 틀렸다거나 Exqutor 가 망가졌다는 의미가 **아니다**. Exqutor 는 자신의 design intent (multi-table join with vector range filter) 에서는 정상 동작하며, 단일 테이블 시나리오는 Exqutor 의 *명시되지 않은 사각지대* 다. 본 연구는 이 사각지대를 새 motivation 의 첫 줄로 격상함으로써, 옵션 A 의 부분 실패를 negative result 로 학술적으로 흡수했다.

§III~V 의 수학적 검증은 **여전히 유효** 하다. Adaptive Sampling 의 상수 8개, 수식 5개, 제어 3축은 Exqutor 소스의 multi-table 호출 경로에서도 동일하게 호출되며, Python 재구현은 그 함수의 동작을 정확히 모사한다. 단지 Exqutor 가 그 함수를 호출하기 위한 trigger 조건이 multi-table 시나리오로 제한되어 있을 뿐, 함수 자체는 같다. 따라서 본 연구의 Pivot A 네이티브 검증은 단일 테이블 시나리오에서 두 모드 (SYSTEM, BERNOULLI) 모두 같은 plan replacement 경로를 타도록 강제한 채로 **상대값 (SYSTEM 대비 BERNOULLI 의 q-error 차이)** 을 측정하는 방향으로 재정의된다. 절대값 비교가 아니므로 plan replacement 의 부작용은 두 모드에서 동일하게 나타나 cancel 되며, 이는 Phase 4 의 작업 절차가 된다.

---

## 5. 종합 — 우회가 아닌 진화

위 4단계는 4/3 합의에서 19:10 KST 정의로 옮겨가는 과정 전체를 시간 순서로 정리한 것이다. 이 전환은 *다른 주제로 우회* 가 아니라 *같은 주제의 정교화* 다. 4/3 합의의 핵심은 두 가지였다. 첫째, Exqutor 의 Adaptive Sampling 이 가진 정확도 한계를 데이터로 보여라. 둘째, 그 한계를 해소하는 샘플링 방법을 제안하라. 19:10 KST 정의는 두 핵심 모두를 보존한다. 4/14 1차 실험 (§2) 에서 글로벌 skewness 가 한계의 원인이 아니라는 negative result 를 정직하게 받아들였고, 같은 데이터에서 발견한 두 가지 새 신호 (선택도 효과, 블록 편향) 위에서 Pivot A 와 Pivot C 두 노선을 정의했다 (§3). 옵션 A 부분 실패에서 발견한 네 가지 design constraint 중 두 가지를 motivation 의 새 첫 줄로 격상해서, *Exqutor 의 명시되지 않은 사각지대를 정량적으로 드러낸다* 는 학술적 입장을 추가했다 (§4). 결과적으로 본 연구는 다음과 같은 좁고 정확한 명제를 갖는다.

> 본 연구는 Exqutor 가 자신의 multi-table only design intent 로 배제한 단일 테이블 vector range query 사각지대를, 두 단계로 분석하고 개선한다. 첫째 단계는 finding 제시다 — Hook trigger 사각지대 (X.3) 와 plan replacement 부작용 (X.5) 을 직접 소스 검증과 EXPLAIN ANALYZE 로 정량 드러낸다. 둘째 단계는 개입 측정이다 — `TABLESAMPLE SYSTEM` 의 block bias 를 BERNOULLI 한 줄 교체 (Pivot A) 로 sanitize 하고, naive uniform sampling 을 local skew 4 지표 기반 stratified sampling (Pivot C) 으로 sanitize 한다. 두 sanitize 의 정확도 이득은 직교적 ablation 으로 분리 측정된다.

이 명제는 4/3 합의의 두 핵심을 모두 보존하면서 두 가지 차원에서 정교화한다. 첫째, *데이터로 한계를 보여라* 는 핵심을 *4가지 구조적 한계 (글로벌 skew 무관성, 선택도 취약, 블록 편향, hook 사각지대) 를 정량적 negative result 와 finding 으로 보여라* 로 정교화한다. 둘째, *해소 방법을 제안하라* 는 핵심을 *직교적 두 sanitize 를 ablation matrix 로 분리 측정하라* 로 정교화한다. 두 정교화 모두 4/3 합의 직후의 *추측 (이러한 한계가 있을 것이다)* 을 *측정 (이러한 한계가 이만큼 있다)* 으로 격상하는 방향이다.

이 정교화의 비용은 한 가지다. 시나리오가 multi-table join with vector range filter 에서 단일 테이블 vector range query 로 좁혀졌다. 비용의 대응은 두 가지로 정당화된다. 첫째, Exqutor 의 hook 동작 (plan replacement) 이 단일 테이블 시나리오에서 outer query 의미를 깨뜨린다는 finding 자체가 *왜 단일 테이블 시나리오를 새로 다뤄야 하는가* 의 학술적 동기를 제공한다. 둘째, 단일 테이블 vector range query 는 실무에서 더 흔한 시나리오 — 이미지 검색, 추천 시스템, RAG 의 retrieval 단계 — 이며, Exqutor 가 이를 명시적으로 배제한 것은 본 연구가 채울 수 있는 빈자리다. 이 시나리오 전환은 4/3 합의 직후에는 본 팀의 시야에 없던 기회이며, 4/14 의 4단계 검증 사이클을 통해 비로소 정량적으로 식별되었다.

### 5.1 큰 3단계 구조의 보존과 단계별 정교화

4/3 합의의 큰 골격은 **베이스라인 측정 → skew-aware sampling 개선 (트랙 A) → distribution-agnostic sampling 확장 (트랙 B)** 의 3단계 구조였으며, 19:10 KST 정의는 이 3단계 구조를 그대로 유지한 채 각 단계 안에서만 정교화가 일어난 결과다. 본 연구의 어떤 단계도 4/3 합의에서 새로 추가되거나 폐기되지 않았다. 단계별 정교화는 다음과 같이 매핑된다.

**첫째 단계 — 베이스라인 측정**. 4/3 합의 시점에는 *현행 Exqutor 의 multi-table join 시나리오에서 카디널리티 추정 정확도 한계를 데이터로 드러낸다* 라는 한 줄 정의였다. 19:10 KST 정의에서는 이 단계가 multi-table 시나리오에 단일 테이블 vector range query 사각지대까지 확장되었으며, 사각지대 자체가 §4.2 의 hook trigger 조건 (X.3) 과 §4.4 의 plan replacement 부작용 (X.5) 이라는 두 finding 으로 정량 측정되었다. 즉 4/3 합의의 *베이스라인 한계* 가 *Exqutor design constraint 의 4가지 정량 finding* 으로 정교화되었으며, 그중 두 가지가 본 연구의 새 motivation 첫 줄로 격상되었다.

**둘째 단계 — skew-aware sampling 개선 (트랙 A)**. 4/3 합의 시점에는 *글로벌 skewness 지표로 분포를 분류하고 분류별로 다른 샘플링을 적용한다* 였다. 4/14 1차 실험에서 4가지 글로벌 지표 모두 Q-error 의 설명변수가 되지 못한다는 negative result (가설 H1 기각) 가 나오면서, 이 단계는 두 가지 직교적 sanitize 로 분리되었다. **Pivot C — local skew 4지표 기반 stratified sampling 본 구현** 이 트랙 A 의 본 sanitize 다. 글로벌 지표가 고차원 거리 집중에 취약하다는 진단을 받아들여 *글로벌 → local* 으로 측정 도구를 교체하고, 4/3 합의의 *층화 (stratified) 의 정확도 이득* 을 본 연구에서 처음으로 실제 구현으로 측정한다 (4/3 시점의 Python 재구현은 stratified mode 가 부재했다). **Pivot A — `TABLESAMPLE SYSTEM → BERNOULLI` 한 줄 교체** 는 Pivot C 의 측정을 위한 fair baseline 도구로, 블록 편향 신호 (3.8~9.1%p) 위에서 sampling method ablation 의 단독 단위로 분리 측정된다. 두 Pivot 은 직교적이므로 SYSTEM/BERNOULLI/STRATIFIED × dataset 의 ablation matrix 로 각 sanitize 의 기여를 분리할 수 있다. 즉 4/3 합의의 *분류별 다른 샘플링* 이 *local skew 층 기반 stratified + sampling method ablation* 으로 정교화되었다.

**셋째 단계 — distribution-agnostic sampling 확장 (트랙 B)**. 4/3 합의 시점에는 *분포를 모르는 상황에서도 robust한 샘플링 — Latin Hypercube Sampling (LHS) 등 — 을 검토한다* 였다. 19:10 KST 정의에서 이 단계는 *KDE-pilot online 층화* 로 본 구현이 정의되었으며, 중간발표 (4/28) 까지의 Phase 1~7 에서는 진입하지 않고 최종보고서 (6/11) 까지의 Phase 8 에서 합류한다. 트랙 B 의 본선 진입 시점이 후기로 이동했지만, 노선 자체는 보존되며 Pivot C (둘째 단계의 본 sanitize) 의 자연스러운 확장 경로 — 분포를 알 때 사용한 local skew 층 정의를 분포를 모를 때는 KDE pilot 으로 자동 학습 — 로 합류한다. 즉 4/3 합의의 *Track B 진입* 이 *Phase 8 KDE-pilot 합류로 시점 조정* 되었지만 단계 자체는 폐기되지 않았다.

본 매핑이 보여주는 핵심은 다음과 같다. **큰 3단계 구조는 4/3 합의에서 19:10 KST 정의로 옮겨 오는 동안 단 한 단계도 추가되거나 폐기되지 않았다**. 첫째 단계는 4가지 정량 finding 으로 베이스라인 한계의 측정 도구가 정교화되었고, 둘째 단계는 글로벌 negative result 위에서 local 측정 + ablation matrix 로 분리되었으며, 셋째 단계는 본선 노선을 보존한 채 시점만 후기로 이동했다. 본 연구의 학술적 골격 — *Exqutor 의 정확도 한계를 데이터로 드러내고, 그 한계를 두 트랙 (분포 인지 / 분포 무인지) 으로 sanitize 한다* — 는 4/3 합의 그대로 유지된다.

### 5.2 핵심 한 줄

본 narrative 의 핵심 한 줄은 다음과 같다. **본 연구는 4/3 합의의 큰 3단계 구조 (베이스라인 → 트랙 A → 트랙 B) 와 그 핵심 동기 (Exqutor 정확도 개선) 를 그대로 보존한 채, 각 단계의 측정 정의를 4/14 의 4단계 검증 사이클이 만들어낸 정량 데이터 위에서 정교화한 결과다. 시나리오 좁힘 (multi-table → 단일 테이블 사각지대 포함) 은 부담이 아니라 새 학술적 빈자리의 발견이며, motivation 강화는 negative result 의 흡수와 finding 의 격상을 동시에 수행한다.**

---

## 6. 자문 미팅 보고 항목 (2026-04-15~04-17 예정)

본 narrative 를 기반으로 자문 미팅에서 다음 6개 항목에 대해 사후 합의를 받는다.

**6.1 시나리오 전환의 학술적 정당성**. 4/3 합의의 multi-table join with vector range filter 시나리오가 19:10 KST 정의에서 단일 테이블 vector range query 사각지대로 전환된 것이 학술적으로 정당한지. §4.2~4.5 의 네 가지 design constraint 가 시나리오 전환의 충분 근거인지. 본 팀의 입장은 *충분 근거이며 동시에 새 학술적 기회*. 자문 결과에 따라 §5 의 narrative 톤을 조정한다.

**6.2 가설 H1 기각의 보고와 Pivot C framing**. §2 의 4가지 글로벌 지표 실패 (24개 조합 모두 |ρ| < 0.2, 12개 조합 모두 ratio ≈ 1.0) 를 *negative result* 로 보고하는 것이 적절한지, 그 negative result 가 Pivot C (local skew 4지표) 의 정당화로 사용되는 framing 이 reviewer 관점에서 자연스러운지. 본 팀의 입장은 *글로벌 지표 실패가 local 지표 전환의 직접 근거이며, 부정 결과의 학술적 가치는 보존*. 단 본 framing 이 *원래 가설을 폐기한 것* 으로 잘못 읽히지 않도록 narrative 표현을 다듬을 필요가 있을 수 있다.

**6.3 Pivot A 추가의 적절성**. §3 에서 발견한 블록 샘플링 편향 신호 위에서 Pivot A (BERNOULLI 한 줄 교체) 가 추가된 것이 4/3 합의의 본선과 별개로 정당한 기여인지, 아니면 *기여 인플레이션* 으로 보일 위험이 있는지. 본 팀의 입장은 *Pivot A는 fair baseline 구축 도구이며 동시에 sampling method ablation 의 단독 단위로 학술적 가치 보유*. Pivot A 만 단독으로는 한 줄 변경이지만, Pivot C 와 결합한 ablation matrix 의 일부로서 정당하다.

**6.4 Track B (LHS) 우선순위 하향의 적절성**. 4/3 합의 시 검토하기로 한 Track B (Distribution-Agnostic, Latin Hypercube Sampling) 의 본선 진입을 Phase 8 (최종보고서 국면) 로 하향한 것이 적절한지. 본 팀의 입장은 *Pivot A+C 노선이 Track A 의 본 구현이며, Track B 는 Pivot C 의 자연스러운 확장 경로로 Phase 8 에서 KDE-pilot online 층화로 합류*. 중간발표 (4/28) 까지는 Track A 만으로 노선의 타당성을 증명하는 것이 우선.

**6.5 Hook trigger 우회 + plan replacement finding 의 reviewer 관점 노출 수위**. §4.3 에서 본 팀이 `vector.c` line 243 을 한 줄 수정한 것이 *Exqutor 를 임의로 patch 한 것* 으로 보일 위험이 있는지, 아니면 *finding 을 드러내기 위한 정당한 진단 도구* 로 받아들여질지. 본 팀의 입장은 *후자이며, 변경된 vector.c 와 변경 전 백업을 모두 보존하고 변경 라인을 narrative 에 명시하는 것이 reviewer 신뢰의 근거*. 다만 자문 결과에 따라 변경된 vector.so 를 본선 측정에서 아예 사용하지 않고 (즉 multi-table query format 으로 전환) 진행하는 옵션도 보존 가능.

**6.6 4/28 중간발표 슬라이드의 finding 노출 수위**. §4 의 네 가지 design constraint 중 어디까지를 중간발표 슬라이드에 드러낼 것인지. 본 팀의 후보는 (a) 첫째·둘째만 (motivation 강화 목적) , (b) 네 가지 모두 (정직한 보고 목적) , (c) 첫째만 (시간 제약 고려) 이다. 자문 결과로 결정. 본 팀의 선호는 (a) 로, 첫째·둘째는 motivation 의 새 첫 줄로 격상되었으므로 슬라이드 1~2장으로 정량 보고하고, 셋째·넷째는 부록 슬라이드 또는 보고서에만 기록한다.

자문 결과는 `templates/forms/자문내역서/프로젝트전문가자문내역서(양식).docx` 양식에 정리해서 자문내역서로 저장한다. 자문 결과에 따라 본 narrative 의 §1~5 표현이 미세 조정될 수 있으며, 그 조정은 본 문서의 v2 로 별도 commit 된다.

---

## 7. 다음 작업 — Phase 4 본격 측정

본 narrative 작성 완료 후 즉시 진입하는 작업은 `summary.md` §IV Phase 4 — *Pivot A 네이티브 BERNOULLI 교체 실측* 이다. 작업 절차는 다음과 같다.

(1) `Exqutor/PostgreSQL/pgvector/pgvector/src/vector.c` 에서 `TABLESAMPLE SYSTEM(%f)` 위치 (patch 기준 line 1192) 를 grep 으로 정확히 재확인. (2) 그 한 줄을 `TABLESAMPLE BERNOULLI(%f)` 로 교체. (3) `vector.c.bak.20260414_1840_after_bernoulli` 로 한 번 더 백업. (4) `make USE_PGXS=1 PG_CONFIG=$PREFIX/bin/pg_config && make USE_PGXS=1 PG_CONFIG=$PREFIX/bin/pg_config install` 로 새 `vector.so` 생성, md5 로 변경 확인. (5) PG 55436 fast restart. (6) 1 query EXPLAIN ANALYZE 에서 `Sampling Method: bernoulli` 확인. (7) 100 query × 6 selectivity × 1 seed = 600 query 측정, 각 query 직후 EXPLAIN 의 Sample Scan node Plan Rows + Actual Rows 추출. (8) 결과 parquet 저장. (9) SYSTEM 모드도 같은 방식으로 baseline 측정 (변경 전 `vector.c.bak.20260414_1840` 로 복원 → 재빌드 → 측정 → BERNOULLI 로 다시 교체) . (10) 두 모드의 median q-error 차이가 Python counterfactual 의 +3.8~9.1%p 감소와 일치하는지 확인.

Phase 4 의 핵심 측정은 *상대값* 이며, plan replacement 부작용은 두 모드에서 동일하게 cancel 된다. 자세한 절차와 예상 작업량은 `MEMORY/session_resume.md` §F.2 에 정리되어 있다.

본 narrative 작성과 Phase 4 진입 후, 자문 미팅 (4/15~4/17) 일정이 확정되면 본 문서를 자문 미팅 자료로 인쇄해서 직접 보고한다. 자문 미팅 일정 잡기는 박세은 팀장과 협의해서 4/15~4/17 사이 30분 슬롯으로 확정하는 것이 본 narrative 작성 외부의 우선 작업이다.
