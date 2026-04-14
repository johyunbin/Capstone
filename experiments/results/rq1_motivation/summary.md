# RQ1 Motivation — 1차 실험 결과 요약

**실행 일자**: 2026-04-14 16:46 ~ 16:55 KST
**실행자**: 조현빈 (Claude Code 보조)
**파이프라인 문서**: `experiments/plans/RQ1_motivation_pipeline_20260414_162857.md` (v2)
**실행 환경**: 연세대 BDAI Lab 서버 `capstone2026@165.132.140.240`, PG 16.9 + pgvector 0.7.1 (Exqutor patched)
**대상**: `partsupp_deep_10` 의 1M 서브셋 (96d DEEP, `DISTINCT ON (ps_partkey)`)

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

### II.5 Block vs Bernoulli paired (Wilcoxon signed-rank, 대립가설: block > bernoulli)

| s | median diff | mean diff | W | p | block > bern | bern > block |
|---|---|---|---|---|---|---|
| 0.001 | 0.000 | 0.000 | 0.0 | — | 0 | 0 |
| 0.010 | 0.000 | −0.018 | 1 554.5 | 0.691 | 39 | 42 |
| 0.050 | 0.057 | 0.047 | 2 968.0 | **0.001** | 59 | 34 |
| 0.100 | 0.053 | 0.065 | 3 853.5 | **< 0.001** | 70 | 29 |
| 0.300 | 0.078 | 0.088 | 4 689.5 | **< 0.001** | 83 | 17 |
| 0.500 | 0.102 | 0.103 | 4 926.0 | **< 0.001** | 89 | 11 |

**발견 7 — Block bias의 강력한 실증**. 선택도 0.050 이상에서 `TABLESAMPLE SYSTEM`이 Bernoulli 대비 Q-error를 유의하게 키운다. 선택도가 클수록 더 많은 query에서 block > bern 방향으로 이동(s=0.500에서 89/100 query가 block 쪽이 더 큰 Q-error). 설계안 v3에 없던 **새로운 기여축**.

---

## III. 해석 — RQ1 방향 재정립 필요

### III.1 가설 H1 기각

> **H1 (원안)**: Skewness가 클수록 Q-error가 증가한다. 특히 `|γ| > 1`인 분포에서 Q-error가 uniform 대비 2배 이상 악화.

위 결과는 H1을 강하게 기각한다. 4개 skew 지표 중 어느 것과도 Q-error 상관이 거의 0이며, 그룹 간 median 비율도 1.0 근처다. 이는 설계안 v3가 구상했던 "distribution-aware stratified sampling"의 전제를 흔드는 결과다.

### III.2 그러나 2개의 강력한 대체 신호

데이터는 두 가지 새로운 서술을 강력하게 뒷받침한다.

1. **선택도 효과**. Exqutor Adaptive Sampling은 극소 선택도(`s ≤ 0.01`)에서 구조적으로 취약하다. `s = 0.001`에서 median Q-error 2.6은 실무 관점에서 의미가 있다(옵티마이저 플랜 선택에 영향을 주는 수준).
2. **Block sampling bias**. `TABLESAMPLE SYSTEM`이 행 단위 Bernoulli 대비 일관되게 Q-error를 키운다. 가장 큰 효과는 `s = 0.500`에서 89/100 query가 block 방향으로 움직임. 원인은 블록 내부의 행 상관성(physical clustering)으로 추정된다.

### III.3 설계안 pivot 후보

세션 종료 시점(2026-04-14 17:00 KST)의 잠정 방향 후보 3가지. **팀/사용자 논의 필요**.

- **Pivot A — Block → Bernoulli 단순 교체**. `TABLESAMPLE BERNOULLI` 사용만으로도 Q-error 개선 가능하다는 매우 단순·강력한 주장. 기여의 폭은 좁지만 실용성 높음.
- **Pivot B — 선택도 적응형 샘플링**. 극소 선택도에서만 샘플을 적극적으로 키우는 변형. 현재 Exqutor의 `grad = α(med_q − β) − (100−α)(sample/total)` 구조는 "Q-error와 비용"을 균형한다. 선택도별 β를 다르게 하는 변형 — 예: `s < 0.01`일 때 β를 낮춰 수렴 타겟을 엄격하게.
- **Pivot C — 원안 유지 + RQ 확장**. Fisher γ 기반이 아니더라도 skew의 또 다른 정의(예: 거리 분포의 modality, cluster density, local PCA 스펙트럼)를 탐색. 범위 확대이나 일정 리스크 큼.

### III.4 현재 결과의 한계

- 1M 서브셋. 원본 sf10(`partsupp_deep_10`, 8M)에서 재현해야 일반화 가능.
- 단일 테이블. 128d SIFT(`customer_sift_10`)와 768d WIKI(`part_wiki_10`)에서 재현 필수.
- Python 재구현과 Exqutor 네이티브의 equivalence check(Stage 4.5)가 아직 수행되지 않음. 구현 오류로 인한 false negative 가능성이 남아 있다(우선 순위 최상).
- 시각화(Stage 5b)가 아직 없음. 산점도·박스플롯으로 위 수치가 실제로 어떤 모양인지 확인 필요.

---

## IV. 다음 세션 우선 작업

1. **Equivalence check (Stage 4.5)** — Exqutor 서버 네이티브와 Python 재구현 결과 대조. 우선 순위 최상. 일치하면 본 결과 확정. 불일치하면 원인 파악 후 본 문서 재검증.
2. **시각화 (Stage 5b)** — matplotlib 설치 + 4개 figure 생성(F1~F5 설계안 기반, 일부 본 결과에 맞게 조정).
3. **다른 테이블 재현** — `customer_sift_10`(128d)에서 동일 파이프라인 실행. 블록 효과와 선택도 효과가 차원/테이블 독립적인지 확인.
4. **사용자/팀 논의** — Pivot A/B/C 중 하나 선택. 중간발표 4/28까지 14일 남음, 방향 결정은 늦어도 4/17까지.

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
