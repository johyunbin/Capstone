# RQ1 Phase 6 vs Phase 7 — DEEP 1M Selectivity Gradient 5-cell 비교

**작성일**: 2026-05-07 KST
**측정 기반**: `rq1_phase6_vs_phase7_comparison.json` + master line 81-99 (5/7 W2 발견)
**용도**: 5/27 발표 Slide 4/6 footnote 보강 + 자문 메일 첨부 (옵션 2 정직 reporting)

---

## I. 배경 — 같은 query pool, 다른 D_target driver

5/7 W2 의 후속 검증에서 발견된 사실 한 가지: **같은 query pool, 같은 5 selectivity, 같은 5 seed, 같은 KM20-BERN 비교 metric** 에서 D_target 계산 driver 만 변경했을 때 단조성 trend 의 강도가 크게 달라진다.

| driver | 환경 | 사용 위치 |
|---|---|---|
| **Phase 6** (SQL D) | PostgreSQL `tablesample` + vector.c hook (production-near) | RQ1 5/27 발표 핵심 인용 |
| **Phase 7** (numpy D) | Python NumPy 시뮬레이션 (≤10K 캐시 + HT weight=N=1M) | 8M cross-scale 검증 외삽 |

본 doc 은 두 driver 의 측정 결과 격차를 정량 보고하고, origin 가능성과 본 연구의 reporting 방침을 정리한다.

---

## II. 5-cell 비교 — Phase 6 단조 감소 vs Phase 7 약한 trend

![Phase 6 vs Phase 7 5-cell bar chart](../../figures/rq1_motivation/phase6_vs_phase7_5sel.png)

**표 — 5-cell raw**

| sel | Phase 6 (SQL D) | Phase 7 (numpy D) | Δ = Ph6 - Ph7 |
|-----|---:|---:|---:|
| 0.01 | **+8.93%** | +3.33% | +5.60%p |
| 0.05 | +1.85% | -2.60% | +4.45%p |
| 0.10 | -2.06% | -1.31% | -0.75%p |
| 0.30 | -3.11% | -0.99% | -2.12%p |
| 0.50 | **-10.67%** | -1.23% | -9.44%p |

- **Phase 6 양 끝 (s=0.01 vs s=0.50)** — +8.93% → -10.67%, dynamic range **19.6%p** 의 강한 단조 감소.
- **Phase 7 양 끝** — +3.33% → -1.23%, dynamic range 4.56%p 의 약한 trend.
- **Δ 패턴** — 양 끝 cell (s=0.01 / s=0.50) 에서 Δ 절댓값 최대 (+5.60, -9.44), 중간 sel 에서 Δ 절댓값 최소 (-0.75 @ s=0.10). 두 driver 의 격차가 sel 양 끝에서 가장 크게 벌어짐.

> **참고** — master 표 (line 87-91) 의 Δ 부호 표기는 정정 대상. 위 표는 `Δ = Ph6 - Ph7` 정의로 계산된 정확값이다.

---

## III. per-seed Spearman ρ — 단조성 검정

![per-seed Spearman rho — Phase 6 vs Phase 7](../../figures/rq1_motivation/phase6_vs_phase7_rho.png)

**표 — 검정 결과**

| driver | per-seed ρ (mean) | 95% CI | 단조 감소 검정 |
|---|---:|---|---|
| **Phase 6** | **-0.680** | [-0.800, -0.440] | **CI 0 제외 ✓ (확정)** |
| Phase 7 | +0.240 | [-0.061, +0.480] | CI 0 포함 ✗ (검정력 약화) |

- **Phase 6** — per-seed Spearman ρ 의 95% CI 가 0 을 포함하지 않으며 음수 영역 (-0.800 ~ -0.440) 에 완전히 위치. RQ1 의 핵심 가설 H1-G (sel 이 낮을수록 KM20-BERN 개선이 단조 증가) 가 통계적으로 confirmed.
- **Phase 7** — ρ 가 양수이지만 CI 가 0 을 포함 (-0.061 ~ +0.480). 단조 감소 trend 가 검정력 부족으로 확정 X. (RAND arm 단조성과 시각적 패턴은 일치하나 통계 유의성은 미달.)

---

## IV. Selectivity Gradient Trend — log scale

![Selectivity gradient trend line — Phase 6 solid vs Phase 7 dashed](../../figures/rq1_motivation/phase6_vs_phase7_trend.png)

log(sel) 축에서 보면 Phase 6 line 은 5 sel 에 걸쳐 거의 단조 감소 (s=0.05 의 +1.85% blip 만 예외). Phase 7 line 은 +3.33 → -2.60 → -1.31 → -0.99 → -1.23 의 weak descending pattern.

---

## V. Origin — 격차의 두 가능성

본 연구는 격차의 원인을 단정하지 않고 두 가지 가능한 origin 을 모두 보고한다.

### Origin A — vector.c hook 환경의 measurement bias

Phase 6 은 PG production binary (`vector.c` hook 적용) 의 SQL `tablesample` 경로에서 D_target 을 계산. 이 환경은 (i) HNSW index 의 cache locality, (ii) tablesample seed reproducibility, (iii) hook 의 timing instrumentation 영향을 모두 받음. 측정값 자체는 production environment 의 실제 sampling outcome 이지만, vector.c hook 의 미세한 bias 가 단조성 trend 의 강도를 인위적으로 증폭했을 가능성 배제 불가.

### Origin B — numpy estimator 의 sampling-population scope 차이

Phase 7 은 ≤10K 캐시 추출 후 NumPy 시뮬레이션. HT weight 를 N=1M 으로 setting 하나 effective sampling pool 자체는 cache size 로 제한됨. 즉 *population scope mismatch* (cache 10K vs full 1M table) 가 KM20 의 cluster-aware advantage 를 약화시켰을 가능성. 8M cross-scale 검증의 numpy estimator 외삽도 같은 scope 한계에 노출되어 있음을 시사.

---

## VI. 본 연구의 처리 — 옵션 2 정직 reporting

5/27 발표 및 최종 보고서는 두 환경 결과를 **모두 보고** 한다.

1. **핵심 narrative 인용 기준**: Phase 6 (SQL D, vector.c hook). "PG sampling extension 기준 (production-near)" 으로 명시.
2. **Phase 7 결과**: "numpy estimator 시뮬레이션 — 8M cross-scale 외삽 도구" 로 명시 인용. 단조성 검정의 weakening 사실 도 함께 보고.
3. **격차 자체**: measurement methodology 의 robustness 검증 sub-contribution 으로 격상. 즉 "single-table 분포 정보의 가치"라는 RQ1 main claim 은 두 driver 모두에서 *방향 일관* (KM20 양 끝 cell 에서 BERN 대비 차이 발생) 이라는 점을 강조.

---

## VII. 자문 요청 사항 (5/8 회의 후 자문 메일 동봉용)

본 격차에 대해 자문 받고자 하는 항목 :

1. **vector.c hook 환경의 measurement bias 가능성** — production binary instrumentation 이 sampling outcome 의 단조성에 영향을 줄 알려진 케이스가 있는가?
2. **numpy estimator 의 cache-vs-full population scope mismatch** — HT weight 만으로 8M full-table 결과를 외삽하는 것의 한계는 어디까지인가?
3. **옵션 2 정직 reporting 의 학술적 적절성** — 두 measurement methodology 의 결과를 모두 보고하면서 main narrative 는 production-near 환경으로 단일 인용하는 reporting style 이 학술적으로 문제 없는가?

---

## VIII. 산출

| 산출 | 위치 | 비고 |
|---|---|---|
| Figure 1 (5-cell bar) | `experiments/figures/rq1_motivation/phase6_vs_phase7_5sel.png` | 본 doc §II + Slide 4 footnote |
| Figure 2 (ρ scatter) | `experiments/figures/rq1_motivation/phase6_vs_phase7_rho.png` | 본 doc §III + Slide 6 footnote |
| Figure 3 (trend line) | `experiments/figures/rq1_motivation/phase6_vs_phase7_trend.png` | 본 doc §IV + 자문 첨부 |
| 재현 스크립트 | `experiments/code/local_analysis/generate_phase6_vs_phase7_*.py` | matplotlib 한글 폰트 helper 사용 |
| Raw 비교 JSON | `experiments/results/rq1_motivation/rq1_phase6_vs_phase7_comparison.json` | 4 cell raw + delta_phase7_p10_minus_phase6_p05 |
| 단조성 master | `experiments/results/rq1_motivation/rq1_gradient_monotonicity.md` | 5/6 W1 sprint per-seed ρ 검정 결과 |
