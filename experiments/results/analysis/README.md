# experiments/results/analysis/ — 본 연구 13 분석 file (5/13 ~ 5/15)

본 디렉토리는 본 연구 narrative 의 **정량 수치 source**. 각 분석 file 은 server 1352 file portfolio 위에서 측정 결과를 정량 분석한 결과.

## 5/15 추가 4 분석 (mini session 자동 진행)

| File | 작성 | 핵심 finding | narrative 위치 |
|---|---|---|---|
| `B1_variance_root_cause_종합분석_20260515_0150.md` | 5/15 01:50 | **B1 inherent CV 6.33%** (n=10 trial) + **measurement run-level systematic bias ±10-25%** (random variance 만으로 설명 불가). 5/12 -23%, 5/14 K=10 +24%, 5/15 archive K=10 +10%. → paper exact base B1 만 reliable denominator | §7 paired narrative caveat |
| `측정_미커버_영역_종합_inventory_20260515_0205.md` | 5/15 02:05 | **paper exact base 98.2% 유효 cover** (495/504, A2-Fig8 scope 외 제외). paper Fig 13 sel sweep 중 **sel=0.10 미측정**. K granularity 9 cell 확장 = 216 file 추가 측정 cover | §10 정직 disclosure |
| `Pareto_Top5_method_cell_cross_validation_20260515_0250.md` | 5/15 02:50 | **★ Pareto Top 5 (sparse_rp/chao/neuram/pca1d/hilbert) × 9 cell = 100% coverage**. paired CaseB < CaseA = **97.78%** (44/45). 전체 56 method 91.46%. robustness rank: hilbert (std 1.55%) > pca1d > sparse_rp > chao_weighted > neuram | §8 자원 효율 + §7 결합 가치 강화 |
| `K_granularity_dimension_dependent_종합검증_20260515_0310.md` | 5/15 03:10 | **dimension-dependent K best 가설 = 약한 evidence**. K=10 best 55%, K=20 25%, K=30 20%. **same DEEP 96d K=10 인데 5/12 (-9.5%) vs 5/14 (+10.3%) = run-level bias 명확**. paper default K=20 robust | 부록 (K granularity caveat 추가) |

## 5/13 ~ 5/14 9 분석 file 인덱스

| File | 작성 | 핵심 finding | narrative 위치 |
|---|---|---|---|
| `multi_join_restratification_results_20260513.md` | 5/13 16:20 | **시나리오 A.5 (Hybrid)**. single-table carry-over (A) vs multi-join 재학습 (B) 비교. quality-sensitive (sparse_rp + chao) 만 B 우위 (−2.63 ~ −3.55%p), quality-robust (hilbert_real + hyperloglog) 거의 동등 | §10 다중 테이블 |
| `centroid_tuple_cheap_approximation_results_20260513.md` | 5/13 19:57 | **새 method axis "Cheap 근사 친화도"**. Centroid tuple 학습 비용 0 + CaseB 보편 우위 (4 method 모두 평균 −0.84%p 추가). 결합 best −7.37% (sparse_rp) source. | §5 결합 시도 + §10 |
| `resource_efficiency_pareto_20260513.md` | 5/13 23:56 | **Pareto Top 5** (sparse_rp / chao_weighted / neuram / pca1d / hilbert) = 12 anchor 일관성 명단과 일치. **reservoir O(1) memory** + −9.25% Δ% = 산업 적용 최강 finding. 산업 적용 3 영역 (A 일반 OLAP / B 정확도 / C Resource-First). | §8 자원 효율 |
| `alpha_sweep_results_20260514.md` | 5/14 00:13 | **★ 시나리오 B 확정**. α sweep 16 measurement. **4 method 中 3 method α=0.5 (산술 평균) best**, U-shape sensitivity. **결합 best −7.37% < 단독 best −10.17%** → 결합으로 단독 능가 X. | §5 가중치 sweep + §6 |
| `cheap_approximation_extended_results_20260514.md` | 5/14 07:05 | cheap 근사 **4 후보 (Centroid / Hash / PCA / Iter) 32 measurement** 종합. **Centroid tuple 만 robust**, B1 Hash spread 큼, B2 PCA marginal, B3 Iter 일관 harmful. | §10 다중 테이블 (cheap 근사) |
| `multi_cell_km_based_learning_comparison_20260513.md` | 5/13 | KM 기반 학습의 multi-cell 비교 | 부록 |
| `km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` | 5/13 03:00 | **K granularity 3-way (K=10/20/30) × 4 anchor × 5 cells = 60 paired**. sparse_rp + chao_weighted = K=20 sweet spot, hilbert_real + hyperloglog = K-robust + K=30 약간 우세. | 부록 (K granularity) |
| `km_granularity_sensitivity_K10_vs_K20_20260513.md` | 5/13 | K=10 vs K=20 1-axis 비교 (3-way 측정 이전 시점) | 부록 |
| `method_level_breakdown_20260513.md` | 5/13 | method-level breakdown — 각 method 의 9-cell paired Δ% mean / std / 일관성 / Cohen's d / Cliff's δ. **단독 best minibatch_partial −10.17% 의 source**. | §4 단독 대체 best |

## 본 narrative 핵심 정량 → source file 매핑

| 본 narrative §  | 정량 수치 | source 분석 file |
|---|---|---|
| §4 단독 best | −10.17% (minibatch_partial 9-cell mean) | `method_level_breakdown_20260513.md` |
| §5 결합 best | −7.37% (Centroid tuple sparse_rp A2-Fig9) | `centroid_tuple_cheap_approximation_results_20260513.md` |
| §5 α sweep | α=0.5 best, U-shape | `alpha_sweep_results_20260514.md` |
| §6 결합 < 단독 | −7.37% < −10.17% | `alpha_sweep_results_20260514.md` |
| §7 결합 가치 | 92.5% paired CaseB < CaseA, cell spread 줄임 | `method_level_breakdown_20260513.md` |
| §7 강화 | **Pareto Top 5 paired 97.78%** (44/45) | `Pareto_Top5_method_cell_cross_validation_20260515_0250.md` ★ |
| §7 caveat | B1 systematic bias ±10-25% (paired narrative 영향 X) | `B1_variance_root_cause_종합분석_20260515_0150.md` ★ |
| §8 Pareto Top 5 | sparse_rp / chao / neuram / pca1d / hilbert | `resource_efficiency_pareto_20260513.md` |
| §8 reservoir O(1) | fit <0.1s + 메모리 O(1) + −9.25% Δ% | `resource_efficiency_pareto_20260513.md` |
| §8 robustness rank | hilbert std 1.55% > pca1d > sparse_rp > chao_weighted > neuram | `Pareto_Top5_method_cell_cross_validation_20260515_0250.md` ★ |
| §10 시나리오 A.5 | quality-sensitive vs quality-robust | `multi_join_restratification_results_20260513.md` |
| §10 cheap 근사 | Centroid tuple −0.84%p (4 method 모두) | `cheap_approximation_extended_results_20260514.md` |
| §10 정직 disclosure | paper Fig 13 sel=0.10 미측정 + 9 cell coverage 98.2% | `측정_미커버_영역_종합_inventory_20260515_0205.md` ★ |
| 부록 K granularity | sparse_rp K=20 sweet, hilbert_real K-robust + dim-K 가설 약한 evidence + run-level bias | `km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` + `K_granularity_dimension_dependent_종합검증_20260515_0310.md` ★ |

## 환각 검증 (5/14 환각 검증 agent 결과)

- **Verified**: 47 정량 (대부분 9-cell mean / 1 cell 값 모두 일치)
- **Uncertain 4 영역**:
  1. 5-way Anti / Neyman 절대값 (1.540 / 1.595) — REPORT v11 5-way csv 직접 확인 권장
  2. paired CaseB < CaseA 92.5% — handoff_v12 base, REPORT v11 cross-check 권장
  3. CLAUDE.md "+3.74%" mean gap — 실측 표와 방향 충돌
  4. SIFT 1.5M (4/17 옛 측정) vs SIFT 80M (paper exact) 분리

## 측정 raw 와의 연결 (5/15 reorganize 후 dataset 단일 기준 그룹화)

각 분석 file 의 raw 측정 데이터:
- `analysis/multi_join_*` ↔ `raw/DEEP+WIKI_864d/A2-Fig9_multi_join_restratification/`
- `analysis/centroid_tuple_*` ↔ `raw/DEEP+WIKI_864d/A2-Fig9_cheap_approximation/centroid_tuple/`
- `analysis/cheap_approximation_extended_*` ↔ `raw/DEEP+WIKI_864d/A2-Fig9_cheap_approximation/` (전체 4 후보)
- `analysis/alpha_sweep_*` ↔ `raw/DEEP+WIKI_864d/A2-Fig9_alpha_sweep/`
- `analysis/km_granularity_*` ↔ `raw/{dataset}/{cell}_K_granularity/`
- `analysis/method_level_breakdown` ↔ `raw/{dataset}/{cell}_paper_main/`
- `analysis/resource_efficiency_pareto` ↔ `raw/REPORT_분석/` + `raw/{dataset}/{cell}_paper_main/`
- `analysis/B1_variance_root_cause_*` ↔ `raw/{dataset}/B1_baseline_paper_exact/` + `raw/{dataset}/{cell}_K_granularity/`
- `analysis/측정_미커버_영역_*` ↔ raw 전체 + `raw/REPORT_분석/REPORT_paper_exact_v11.md`
- `analysis/Pareto_Top5_*` ↔ `raw/{dataset}/{cell}_paper_main/`
- `analysis/K_granularity_dimension_*` ↔ `raw/{dataset}/{cell}_K_granularity/`

## 정리 history

- **5/13 ~ 5/14**: 본 9 분석 file 작성 (각 측정 회수 직후)
- **5/14 16:00**: `_internal/analysis/` → `experiments/results/paper_exact_v7/analysis/` 이동
- **5/14 16:05**: 사용자 정리 — `paper_exact_v7/` 제거 → `experiments/results/analysis/` 직속
- **5/15 01:50 ~ 03:15**: mini session 자동 진행 — 4 신규 분석 file 추가 (B1 variance + 미커버 inventory + Pareto Top 5 + K dim)
- **5/15 11:25**: raw/ dataset 단일 기준 reorganize (사용자 명시 정책 적용, 1352 file git mv)

---

작성: 2026-05-14 16:10 KST · narrative 매핑 + raw 연결 명시 · 5/15 11:55 update — 4 신규 분석 + dataset reorganize 반영
