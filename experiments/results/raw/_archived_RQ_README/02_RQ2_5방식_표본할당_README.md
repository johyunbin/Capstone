# 02 — RQ2 5-way Allocation 측정 raw

본 디렉토리는 RQ2 "분포 정보 다 있을 때 sampling 의 최대 한계가 어디?" 의 raw 측정 데이터.

## 핵심 finding (본 narrative §3.3 + §5.4)

5 way allocation (Bernoulli / Equal / Proportional / Neyman / Anti-Neyman) 측정 결과:

- **Bern → Prop @ sel=0.01: 1.748 → 1.584 (−9.38%)** (DEEP sf=100)
- **Neyman Paradox**: Anti 1.540 < Prop 1.580 < **Neyman 1.595** (σ-가중이 Prop 보다 부정확)
- 원인: σ_j range 1.3~1.6× narrow + N_i CV=0 (cluster 크기 균등)
- 본질적 메커니즘: 클러스터링 metric (L2) = query metric (L2) → cluster 안 query 응답 거의 일관 → σ_j narrow → Neyman 의 σ-가중 효과 약함

## 파일

| file | 데이터셋 | SF | row 수 |
|---|---|---:|---:|
| `rq2_DEEP_sf100_5way_allocation.csv` | DEEP | 100 | 80M |
| `rq2_SIFT_sf100_5way_allocation.csv` | SIFT | 100 | 80M |

각 csv = 5 mode × 5 sel × 5 seed × 100 query = 12,500 row

## 출처

- 측정 script: `_internal/scripts/measure_paper_exact.py` (5-way allocation 함수)
- 분석 file: `experiments/results/analysis/method_level_breakdown_20260513.md`
- 본 narrative §3.3: RQ2 천장 측정 결과
