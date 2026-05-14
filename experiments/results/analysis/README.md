# experiments/results/analysis/ — 본 연구 9 분석 file (5/13 ~ 5/14)

본 디렉토리는 본 연구 narrative 의 **정량 수치 source**. 각 분석 file 은 server 1065 file portfolio 위에서 측정 결과를 정량 분석한 결과.

## 9 분석 file 인덱스

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
| §7 결합 가치 | 92.5% paired CaseB < CaseA, cell spread 줄임 | `method_level_breakdown_20260513.md` (handoff_v12 v11 base) |
| §8 Pareto Top 5 | sparse_rp / chao / neuram / pca1d / hilbert | `resource_efficiency_pareto_20260513.md` |
| §8 reservoir O(1) | fit <0.1s + 메모리 O(1) + −9.25% Δ% | `resource_efficiency_pareto_20260513.md` |
| §10 시나리오 A.5 | quality-sensitive vs quality-robust | `multi_join_restratification_results_20260513.md` |
| §10 cheap 근사 | Centroid tuple −0.84%p (4 method 모두) | `cheap_approximation_extended_results_20260514.md` |
| 부록 K granularity | sparse_rp K=20 sweet, hilbert_real K-robust | `km_granularity_sensitivity_3way_K10_K20_K30_20260513.md` |

## 환각 검증 (5/14 환각 검증 agent 결과)

- **Verified**: 47 정량 (대부분 9-cell mean / 1 cell 값 모두 일치)
- **Uncertain 4 영역**:
  1. 5-way Anti / Neyman 절대값 (1.540 / 1.595) — REPORT v11 5-way csv 직접 확인 권장
  2. paired CaseB < CaseA 92.5% — handoff_v12 base, REPORT v11 cross-check 권장
  3. CLAUDE.md "+3.74%" mean gap — 실측 표와 방향 충돌
  4. SIFT 1.5M (4/17 옛 측정) vs SIFT 80M (paper exact) 분리

## 측정 raw 와의 연결

각 분석 file 의 raw 측정 데이터:
- `analysis/multi_join_*` ↔ `raw/08_다중조인_재학습/`
- `analysis/centroid_tuple_*` ↔ `raw/07_저비용_근사_4후보/centroid_tuple/`
- `analysis/cheap_approximation_extended_*` ↔ `raw/07_저비용_근사_4후보/` (전체 4 후보)
- `analysis/alpha_sweep_*` ↔ `raw/05_결합비율_alpha_sweep/`
- `analysis/km_granularity_*` ↔ `raw/06_클러스터수_K_민감도/`
- `analysis/method_level_breakdown` ↔ `raw/03_RQ3_단독대체_CaseA/` + `raw/04_RQ3_결합_CaseB/`
- `analysis/resource_efficiency_pareto` ↔ `raw/10_전체측정_백업/` (분석 종합)

## 정리 history

- **5/13 ~ 5/14**: 본 9 분석 file 작성 (각 측정 회수 직후)
- **5/14 16:00**: `_internal/analysis/` → `experiments/results/paper_exact_v7/analysis/` 이동
- **5/14 16:05**: 사용자 정리 — `paper_exact_v7/` 제거 → `experiments/results/analysis/` 직속

---

작성: 2026-05-14 16:10 KST · narrative 매핑 + raw 연결 명시
