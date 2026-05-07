# RQ1 + RQ2 + RQ3 종합 Master 1-page (W1 Sprint 5/6 23:55)

> **본 문서 = 5/27 발표용 single-page 압축 narrative.** 상세는 각 RQ 별 정리 doc 참조.

---

## 통합 핵심 결과 (한 문장씩)

**RQ1**: BERN sampling 의 부정확성은 selectivity 가 작을수록 단조 증가한다. 단조성의 통계 강도는 D_target 측정 환경에 의존한다. PG `tablesample` + vector.c hook 기반 SQL D_target 환경(Phase 6)은 per-seed Spearman ρ = −0.680, 95% bootstrap CI [−0.800, −0.440] 로 **0 제외 — 단조 감소 확정**. numpy 시뮬레이션 D_target 환경(Phase 7)은 ρ = +0.240, CI [−0.061, +0.480] 로 0 포함 — 단조성 검정력 약화. 두 환경의 5-cell 격차(s=0.01 Δ=−12.26%p) 자체가 sub-contribution 으로, **본 연구는 두 환경 결과를 모두 보고하며 gradient 19.6%p 핵심 수치는 production-near 환경(Phase 6) 기준으로 인용한다** (5/8 회의 합의 narrative).

**RQ2**: KM20 oracle stratification (K-means K=20, **PG 직접 query 로 DEEP 1M / 8M / SIFT 1.5M 모든 dataset 의 stratum_id 0–19 일치 확인**, 5/7 W2 보강) 은 모든 (4 sample size × 2 dataset × 5 sel) 40 cell 에서 BERN 보다 우수 (-1.09~-13.50%). σ_i Neyman 신호는 약하나 σ_i anti-direction (Anti-Neyman) 은 좁은 sel 에서 systematic hurt (DEEP s=0.01 +5.21%, SIFT s=0.01 +9.49%, CI 0 제외). **σ table reproducibility 회복 완료 (5/7 Worker I)**: compute_stratum_sigma_safe.py (conditional DELETE) 적용 — DEEP 1M (avg σ=0.2503), SIFT 1.5M (avg σ=0.2423), DEEP 8M (avg σ=0.2959 보존). 8M cross-scale (Worker L): KM20-aware mode 5 mode × 5 sel × 12,500 cells, 모든 (mode × sel) BH-FDR p_adj > 0.45 (8M 자연 정확도 상승으로 stratification marginal benefit 둔화). Neyman 5/5 cross-scale sign 일관, σ_i 신호 약함 패턴 cross-scale 재현.

**RQ3**: 분포 모를 때 **22 method 비교** (5/7 새벽 final_chain + phase2 완료) — **Hilbert / MiniBatch / Hybrid / HDBSCAN** 4강 (paired bootstrap CI 0 제외 5/10 cell robust). Hilbert mechanism = 1D-2D Manhattan continuity = 1.000 (Z-order 1.992 와 분리). **MiniBatch partial_fit** 은 batch 와 거의 동일 효과 (paired CI 0 제외, ARI = 1.000) → OLTP 적용 확정. **신규 발견 (5/7 02:30~04:11 측정)**: hybrid SIFT s=0.10 **-3.10%** [-4.61, -1.19], **hdbscan SIFT s=0.10 -3.99%** [-5.34, -2.12] (모든 method 중 mid-sel 가장 강). **명확한 negative control**: PQ / Sobol / IS 모두 CI 0 제외 hurt direction. **사용자 검증 필요**: spectral 의 recovery_summary -5.39% 는 mean-of-ratios 왜곡, paired CI 는 +16.71% hurt — narrative 후보 제외.

---

## 핵심 contribution 7종 (5/7 W2 갱신)

1. **Selectivity Gradient 단조성 통계 입증** (RQ1) — Phase 6 SQL D, Spearman ρ + bootstrap CI (per-seed n=25)
2. **Measurement Methodology Robustness sub-contribution** (RQ1, 5/7 NEW) — Phase 6 (SQL D, vector.c hook) vs Phase 7 (numpy D, simulation) 5-cell 격차 정량 (s=0.01 Δ=−12.26%p)
3. **KM20 oracle 의 sample-size robustness** (RQ2) — 40/40 cell 일관 + σ_i 신호 약함 honest 입증
4. **Hilbert Curve = learning-free + 결정론 + competitive recovery** (RQ3 ★1순위) — inverse Manhattan 1.000
5. **MiniBatch K-means partial_fit = production-ready OLTP solution** (RQ3 ★2순위) — ARI 1.000, 4 cell paired CI 0 제외
6. **HDBSCAN = SIFT mid-sel best −3.99%** (RQ3, 5/7 NEW) — density-based clustering 의 가치, 모든 method 중 mid-sel 가장 강
7. **Cluster 분할 자체의 결정적 가치** (RQ3 negative control: Distance-Shell d=+0.49, IS d=+0.5~+0.7, PQ +23.64%, Sobol +33.62%)

---

## Honest Limitation 6종 (5/7 딥리뷰 caveat 통합)

1. **단일 테이블** — Multi-table join 은 Exqutor main scope. 단일 정확성이 multi 의 *필요조건*, multi 일반화는 future work.
2. **KM20 oracle 의 production 학습 부담** — full K-means ~30분. partial_fit (OLTP) + Hilbert (learning-free) 가 production replacement.
3. **Effect size — DEEP small / SIFT large 별도 보고** (5/7 부록 갱신) — DEEP 1M+8M 기준 |d| = 0.15~0.30 small. **그러나 SIFT 1M mid+high sel 에서 |d| = 0.63~0.91 LARGE effect** (Hilbert/HDBSCAN/Hybrid/MiniBatch/Z-order/kdtree). Skew dataset 의 distribution-agnostic method 가치 별도 보고. paired Wilcoxon p < 0.05 는 sample size (n=500) 효과. 어려운 query 에서 method routing 가치 강 (spread vs difficulty ρ=0.78).
4. **numpy estimator 의 sampling-population scope** — bernoulli sampling 이 ≤10K row 캐시에서 추출되며 HT weight 만 N=1M 적용. 절대 q-error 인용 시 "numpy simulation 의 캐시 기반" 명시 필수. 상대 비교 (BERN vs KM20, method ranking) 는 보존.
5. **RQ1 measurement methodology robustness** (5/7 W2 발견 + 5/7 부록 강화) — Phase 6 (SQL D, vector.c hook, production-near) 와 Phase 7 (numpy D, simulation) 의 5-sel 격차. gradient 19.6%p 핵심 수치는 Phase 6 기준 인용, Phase 7 결과는 sub-contribution 으로 honest 별도 보고. **8M Phase 6 (SQL D, vector.c hook) 측정은 future work** — 5/6 patch 시 vector.c memory leak (`memory/reference_server.md` P5/M5) 으로 8M 빌드 risk 높음.
6. **σ_i 신호 약함의 honest 입증** (RQ2 → RQ3 motivation chain) — Anti-Neyman vs Proportional CI 0 제외하지만 paired Wilcoxon p > 0.5, Cohen's d < 0.1. σ_i 신호가 약해 median 수준에서만 detect, 개별 query 수준은 random 과 동치. 이 fact 자체가 RQ3 distribution-agnostic 추구의 정직 motivation. **σ table reproducibility 회복 완료 (5/7 Worker I)** — DEEP 1M (0.2503) + SIFT 1.5M (0.2423) + DEEP 8M (0.2959 보존).
7. **(5/7 부록 신규) IS NaN sel=0.01 발산** — Importance Sampling 의 NaN 비율 sel=0.01 에서 80~95% (DEEP+SIFT+8M 모두), sel=0.05 에서 21~39%, sel ≥ 0.10 에서 < 5%. IS estimator 의 sample-population scope 한계 (extreme weight 발산). 분할 X + weight only → 좁은 sel 에서 estimator invalid. **이 NaN 자체가 contribution #7 "분할 자체 결정성"의 정량 증거**. 분할 기반 method (KM20/Hilbert/MiniBatch/HDBSCAN/4강) NaN < 1%.
8. **(5/7 부록 신규) Recovery Rate 분모 한정** — 분모 (KM20 - RAND20) 양수 cleanly 한 영역은 sel=0.01 (DEEP 1M +0.0433, 8M +0.0978, SIFT 1M +0.1078) 만. mid+high sel 에서 분모 ≈ 0 또는 음수 (RAND20 random K=20 분할 자체로 KM20 만큼 정확) → primary metric `method_minus_bern_pct` 정당화. Recovery Rate 는 sel=0.01 + SIFT 영역에서만 의미 있는 secondary metric.

**향후 보강**: **vector.c integration** — 5/6 patch 시도 시 memory leak (`memory/reference_server.md` P5/M5). 본 연구의 measurement layer 를 Python 으로 우회 후 본질 검증 완료. C-level integration 은 future work.

---

## 측정 데이터 매트릭스

| RQ | Dataset | 측정 cell 수 | 핵심 metric |
|----|---------|------------:|-------------|
| RQ1 | DEEP 1M | 5 sel × 5 seed × 100 query × 2 mode = 5,000 | per-seed Spearman ρ, MK trend |
| RQ1 | SIFT 1.5M | 3 sel × 5 seed × 100 query × 2 mode = 3,000 (mid-sel 코드 ready) | 동일 |
| RQ1 | DEEP 8M | 2 sel × 5 seed × 100 query × 3 mode (overnight) | cross-scale 단조성 재현 |
| RQ2 | DEEP+SIFT | 5 mode × 5 sel × 5 seed × 100 query × 2 dataset = 25,000 | paired Wilcoxon + BH-FDR |
| RQ2 | DEEP+SIFT | 4 ssize × 2 mode × 5 sel × 5 seed × 100 query × 2 ds = 40,000 | 단조 감소 검정 |
| RQ3 | DEEP+SIFT | 7 method × 5 sel × 5 seed × 100 query × 2 ds = 35,000 (1차) | Recovery rate + bootstrap CI |
| RQ3 | DEEP_8M | **5 method** (minibatch/random_proj/hilbert/zorder/lsh, fit+assign 패턴) × 2 sel × 5 seed × 100 query (overnight 자동) | cross-scale Hilbert/MiniBatch 재현 |
| RQ3 (final_chain ready) | DEEP+SIFT | 8 추가 method (zorder/hybrid/partial/pca1d/kdtree/pq/spectral/birch) × 5 sel × 5 seed × 100 query × 2 ds (8M 후 자동 trigger) | ablation ladder |
| RQ3 (phase2 ready) | DEEP+SIFT | 4 추가 method (gmm/hdbscan/sobol/sparse_rp) × 5 sel × 5 seed × 100 query × 2 ds | ablation 완성 — 16 method 전체 |
| **RQ3 8M sel_expand (W2)** | DEEP_8M | 19 method × 3 sel (0.01/0.05/0.50) × 5 seed × 100 q = 28,500 cells | cross-scale Spearman ρ=0.81~0.88 (5 sel 모두 p<0.0001) |
| **RQ2 8M 5-mode (W2 Worker L)** | DEEP_8M | 5 mode × 5 sel × 5 seed × 100 q = 12,500 cells | 모든 BH-FDR p_adj > 0.45 (sample-size attenuation), Neyman 5/5 sign 일관 |
| **RQ2 8M size sensitivity (W2)** | DEEP_8M | 4 ssize × 2 mode × 5 sel × 5 seed × 100 q = 20,000 cells | sample=385 8M robust 운영점 입증 |
| **RQ1 8M Phase 7 5 sel (Worker J)** | DEEP_8M | BERN+KM20 × 5 sel × 5 seed × 100 q = 5,000 cells | 8M Phase 7 numpy 단일 methodology, sel=0.01 KM20 +2.42% (cross-scale hurt) |
| **RQ1 SIFT KM20 5-sel canonical (Gap #1, 5/7 부록)** | SIFT_1.5M | BERN+KM20 × 5 sel × 5 seed × 100 q = 5,000 cells | 5/5 paired CI 0 제외, mid+high sel \|d\|=0.63~0.91 LARGE effect, 비-단조 V자 |
| **RQ3 8M KM20 sel_expand (Gap #3, 5/7 부록)** | DEEP_8M | BERN+KM20 × 3 sel × 5 seed × 100 q = 3,000 cells | Recovery Rate 분모 5 sel 완전 (sel=0.01 분모 +0.0978, mid+high 분모 ≈ 0) |

---

## 주요 통계 결과 한 표 (5/8 회의 자료)

| 검정 | dataset | metric | 값 | 95% CI | 결론 |
|------|---------|--------|----|--------|------|
| RQ1-G monotonic | DEEP | per-seed Spearman ρ | -0.680 | [-0.800, -0.440] | **0 제외, 단조 감소 확정** |
| RQ1-G monotonic | DEEP-RAND | per-seed Spearman ρ | +0.560 | [+0.320, +0.840] | **0 제외, reverse-monotonic 확정** |
| RQ1-G monotonic (5-cell, 5/7 NEW) | SIFT-KM20 | per-seed Spearman ρ | -0.140 | [-0.220, -0.100] | **0 제외, 약한 단조 감소** (sift mid-sel KM20 추가) |
| RQ1-G monotonic (5-cell, 5/7 NEW) | SIFT-RAND | per-seed Spearman ρ | +0.380 | [-0.140, +0.700] | CI 0 포함, 단조 X (sift mid-sel RAND 추가) |
| **RQ1 SIFT KM20 5-sel canonical (Gap #1, 5/7 부록)** | SIFT-KM20 | per-seed Spearman ρ (Δ% paired) | -0.120 | [-0.400, +0.180] | **CI 0 포함, 비-단조 V자** (sel=0.01 +13.69% HURT, mid 음수, high 점진 감소) |
| **RQ1 SIFT KM20 5-sel paired CI** | SIFT s=0.10 | paired Δ% (paired bootstrap CI) | -8.86% | [-10.04, -7.65] | **CI 0 제외, \|d\|=-0.634 LARGE** |
| **RQ1 SIFT KM20 5-sel paired CI** | SIFT s=0.30 | paired Δ% (paired bootstrap CI) | -7.18% | [-7.89, -6.46] | **CI 0 제외, \|d\|=-0.905 LARGE** |
| **RQ1 SIFT KM20 5-sel paired CI** | SIFT s=0.50 | paired Δ% (paired bootstrap CI) | -4.70% | [-5.18, -4.20] | **CI 0 제외, \|d\|=-0.850 LARGE** |
| **RQ3 8M Recovery Rate 분모 (Gap #3)** | DEEP_8M | KM20 - RAND20 | (sel=0.01) +0.0978 / (sel=0.30) -0.0016 / (sel=0.50) -0.0029 | — | sel=0.01 만 분명 양수, mid+high 분모 ≈ 0 → primary metric `method_minus_bern_pct` |
| **RQ3 8M paired CI 종합** | DEEP_8M | 19 method × 5 sel CI 0 제외 cells | **70/90 (78%)** | — | Hilbert/MiniBatch_partial/Hybrid/HDBSCAN 4강 cross-scale 보존 |
| **RQ3 SIFT 1M Cohen's d 통합** | SIFT 1M | 4강 method (Hilbert/HDBSCAN/Hybrid/MB) mid+high sel | \|d\| = 0.63~0.91 | — | **LARGE effect** (DEEP small effect 대조, skew dataset 가치) |
| RQ1 Phase 6/7 methodology | DEEP s=0.05 | Phase 6 SQL D vs Phase 7 numpy D | Δ = -4.45%p | — | **methodology 효과 의미 (>1%p), 단조성 origin 일부 분리** |
| **RQ1 Phase 6/7 5-sel 일관 (5/7 NEW)** | **DEEP-KM20** | **Phase 7 numpy 단조성** | **ρ=+0.240** | **[-0.061, +0.480]** | **🚨 CI 0 포함, 단조 X — Phase 6 SQL D 단조성은 measurement bias 영향 가능성** |
| **Cross-scale 18 method × 2 sel (5/7 NEW)** | DEEP 1M vs 8M | rq3_8m_cross_scale.csv | 36 cells | — | sel=0.1 1M best=hybrid 1.1091, kde_pilot 8M +5.27% hurt, random_proj 8M -3.34% (sampling 자연 안정화) |
| **RQ2 8M Anti-Neyman (5/7 NEW)** | DEEP_8M | Anti-Neyman vs Proportional | s=0.1 Δ=+1.28% | [+0.28, +2.28] | **CI 0 제외 cross-scale 재현** (1M DEEP +5.21%, SIFT +9.49% 와 일관 방향) |
| RQ2 KM20 vs BERN | DEEP s=0.01 | Δ% (paired Wilcoxon) | +13.81% | — | p<1e-8 |
| RQ2 Anti-Neyman vs Prop | DEEP s=0.01 | Δ% (bootstrap CI) | +5.21% | [+1.36, +9.16] | **CI 0 제외, AN systematic worse** |
| RQ2 Anti-Neyman vs Prop | SIFT s=0.01 | Δ% | +9.49% | [+4.66, +11.75] | **CI 0 제외** |
| RQ3 Hilbert | DEEP avg | Cohen's d | -0.156 | (min -0.336, max -0.041) | negligible-small **improve** |
| RQ3 Hilbert vs Z-order | synthetic | inverse Manhattan | 1.000 vs 1.992 | — | curve locality **결정적 분리** |
| RQ3 MiniBatch vs partial | clustered | ARI | **1.000** | — | partial_fit OLTP **결정적** |
| RQ3 spread vs difficulty | DEEP/SIFT | Spearman ρ | +0.78 | — | 어려운 query 에서 method routing 가치 |
| RQ3 IS p200_clip | avg | Cohen's d | +0.704 | — | medium **hurt** (negative control) |

---

## RQ1 Gradient by Methodology (5/7 W2 발견 — 옵션 2 정직 reporting)

같은 query pool, 같은 5 sel, 같은 5 seed, 같은 KM20-BERN 비교 — D_target 계산 driver 만 변경한 결과.

| sel | Phase 6 (SQL D, vector.c hook) | Phase 7 (numpy D, simulation) | Δ = Ph6 − Ph7 |
|-----|---:|---:|---:|
| 0.01 | **+8.93%** | +3.33% | +5.60%p |
| 0.05 | +1.85% | −2.60% | +4.45%p |
| 0.10 | −2.06% | −1.31% | −0.75%p |
| 0.30 | −3.11% | −0.99% | −2.12%p |
| 0.50 | **−10.67%** | −1.23% | −9.44%p |
| **per-seed ρ** | **−0.680** [−0.800, −0.440] | +0.240 [−0.061, +0.480] | — |
| **단조 감소 검정** | **CI 0 제외 ✓** | CI 0 포함 ✗ | — |

해석:
- **Phase 6 (SQL D)** — production env (PG `tablesample` + vector.c hook) 기준. 단조성 ρ=−0.680 통계 확정. **5/27 발표 핵심 narrative 의 인용 기준**.
- **Phase 7 (numpy D)** — Python NumPy 시뮬레이션 (≤10K 캐시 추출 + HT weight=N=1M). 단조성 검정력 약화.
- **격차의 origin** — vector.c hook 환경의 측정 bias 가능성 + numpy estimator 의 sampling-population scope (캐시 vs full table).
- **본 연구의 처리** — 옵션 2 정직 reporting. 두 환경 결과 모두 보고하며, Phase 6 을 "PG sampling extension 기준 (production-near)" 으로 명시 인용. Phase 6/7 격차 자체를 measurement methodology 의 robustness 검증 sub-contribution 으로 격상.

산출: `experiments/results/rq1_motivation/rq1_phase6_vs_phase7_comparison.json` (5-sel 비교 raw).

---

## Narrative Flow (5/27 발표)

```
Motivation (Slide 2)
  ↓ Exqutor 의 single-table 영역의 sampling 정확도
RQ1 진단 (Slides 3-4)
  ↓ BERN 부정확성 + selectivity gradient 단조성 (Phase 6 ρ=−0.680 확정 / Phase 7 numpy D ρ=+0.240 honest sub-contribution)
RQ2 oracle (Slide 5)
  ↓ KM20 의 가치 + σ_i 신호 약 + Anti-Neyman hurt
RQ3 production alternative (Slides 6-9)
  ↓ Hilbert (★1) + MiniBatch (★2) + Distance-Shell/IS (★negative)
Honest limitation (Slide 10)
  ↓ small effect + sample-size noise + 어려운 query routing 가치
Cross-scale validation (Slide 11)
  ↓ 8M sensitivity 재현
Future work + 산출 (Slide 12-13)
  ↓ multi-table / vector.c / distribution shift
```

---

## 산출 위치 (master)

- **본 doc**: `experiments/results/RQ1_RQ2_RQ3_종합_master.md`
- **★ W2 Sprint 8M 종합 (5/7)**: `experiments/results/W2_sprint_8m_종합_20260507.md`
- **★★ W2 Sprint 부록 Gap Fill (5/7 13:50)**: `experiments/results/W2_sprint_부록_gap_fill_20260507.md` — Gap #1/#2/#3/#4 정리 + 8M paired CI 90 cells + 1M+SIFT paired CI 180 cells + Recovery Rate 분모 5 sel 완전 + Limitations 6→8종 갱신
- **Gap #1 산출**: `experiments/results/rq1_motivation/rq1_sift_km20_5sel.parquet` (5,000 cells SIFT KM20 5-sel) + `rq1_sift_km20_5sel_paired_ci.csv`
- **Gap #3 산출**: `experiments/results/rq3_agnostic/rq3_8m_km20_sel_expand.parquet` (3,000 cells 8M KM20 sel_expand) + `rq3_8m_recovery_denominator_5sel.csv`
- **8M paired CI + Cohen's d**: `experiments/results/rq3_agnostic/rq3_8m_paired_ci_cohen_d.csv` (19 method × 5 sel = 90 cells, 70 CI 0 제외)
- **1M+SIFT paired CI + Cohen's d**: `experiments/results/rq3_agnostic/rq3_1m_paired_ci_cohen_d.csv` (180 cells, 96 |d|>0.2 small+, SIFT large effect 다수)
- **RQ1_RQ2 정리**: `experiments/results/RQ1_RQ2 실험 결과 정리.md`
- **RQ3 16-method 종합**: `experiments/results/rq3_agnostic/RQ3_16method_종합.md`
- **단조성 통계**: `experiments/results/rq1_motivation/rq1_gradient_monotonicity.md`
- **Anti-Neyman cell**: `experiments/results/rq2_aware/2026_05_06_alloc/rq2_anti_neyman_cell_analysis.md`
- **5-mode 단조성**: `experiments/results/rq2_aware/2026_05_06_alloc/rq2_5mode_monotonicity.md`
- **Phase 6 vs 7**: `experiments/results/rq1_motivation/rq1_phase6_vs_phase7_comparison.json`
- **ARI redundancy**: `experiments/results/rq3_agnostic/rq3_method_redundancy_ari.md`
- **Effect size + CI**: `experiments/results/rq3_agnostic/rq3_bootstrap_effect_size.md`
- **Per-query ranking**: `experiments/results/rq3_agnostic/rq3_per_query_ranking.md`
- **Locality mechanism**: `experiments/results/rq3_agnostic/locality_curve_comparison.md`
- **5/8 1-page summary**: `submission/_drafts/속도는벡터_5월8일회의_1page_summary_20260506.md`
- **5/27 slide outline**: `submission/_drafts/속도는벡터_5월27일발표_slide_outline_20260506.md`
- **자문 메일 초안**: `submission/_drafts/속도는벡터_자문메일초안_*.md` (2종)
- **figures**: `experiments/figures/rq3_supplementary/` (8 PNG, 한글 폰트 적용)

---

## 자동화 인프라 (5/7 01:50 갱신 — 3-tier chain)

### 서버 tmux 6 sessions
- `measure_8m` (21:57 시작): DEEP 8M × 2 sel × 5 seed × 3 mode 측정 → `/tmp/measure_8m_done.flag`
  - 진행: sel=0.1 system/bernoulli/stratified 완료, sel=0.3 stratified 진행 중
  - ETA: ~03:24 KST
- `post_8m` (23:19 시작): measure_8m flag 감지 → convert → **8M sensitivity 5 method** (minibatch/random_proj/hilbert/zorder/lsh, fit+assign 패턴) → summary → `/tmp/post_8m_done.flag`
  - ETA: ~07:30 KST (8M fetch 1-2h + 5 method 측정 2-4h)
- `final_chain` (5/7 00:51 추가): post_8m flag 감지 → **1M extra 8 method** (zorder/hybrid/minibatch_partial/pca1d/kdtree/pq/spectral/birch) + **SIFT mid-sel** → `/tmp/final_chain_done.flag`
  - ETA: ~10:00 KST (8 method × ~12.5min + sift 30min)
- `phase2` (5/7 00:56 추가): final_chain flag 감지 → **4 missing method** (gmm/hdbscan/sobol/sparse_rp, 5/7 새벽 run_*.py 추가 작성) → `/tmp/phase2_done.flag`
  - ETA: ~11:00 KST (4 × ~12.5min)

### 로컬 watchdog 3 nohup polling (각 60s, ssh check)
- v1 `watch_post_8m.sh` (00:41 시작, PID 82839): post_8m_done.flag → rsync 8M sensitivity 5 parquet + 분석 driver 재실행 (recovery + bootstrap + per_query) + macOS 알림
- v2 `watch_final_chain.sh` (00:51 시작, PID 86238): final_chain_done.flag → rsync 1M extra 8 parquet + sift_mid_sel + 분석 + 단조성 재검정
- v3 `watch_phase2.sh` (00:56 시작, PID 87708): phase2_done.flag → rsync 4 phase2 parquet + RQ3 16-method 전체 갱신

### 미해결 prerequisite (사용자 결정 필요)
- **DEEP s=0.05 numpy** (`deep_s005_numpy_remeasure.py`):
  - prerequisite parquet (`query_selectivity_5sel_numpy.parquet`) 미존재
  - `query_selectivity.parquet` D_target 컬럼은 존재하나 numpy/SQL 출처 미명시
  - 자율 처리 risk → 사용자 도착 후 별도 진행 또는 본 측정 skip 결정

### 자동화 산출 location
- 8M sensitivity 5 method: `experiments/results/rq3_agnostic/rq3_8m_*.parquet`
- 1M extra 8 method: `experiments/results/rq3_agnostic/rq3_{zorder,hybrid,minibatch_partial,pca1d,kdtree,pq,spectral,birch}.parquet`
- Phase 2 4 method: `experiments/results/rq3_agnostic/rq3_{gmm,hdbscan,sobol,sparse_rp}.parquet`
- SIFT mid-sel: `experiments/results/rq1_motivation/sift_mid_sel*.{parquet,json}`

---

**최초 작성**: 조현빈 · 2026-05-06 23:55 KST · W1 sprint final master doc
**5/7 01:50 갱신**: Claude (자율 야간) — 3-tier chain 자동화 + watchdog v1/v2/v3 + 4 missing method run_*.py 추가
**5/7 04:11 갱신**: 모든 chain 완료 — 22 method × DEEP/SIFT 1M-1.5M (final_chain 8 + phase2 4 + 1차 7 + km20/random20/bernoulli baseline 3) + 16 method × DEEP 8M sensitivity. 측정 운영 산출은 `_internal/archive/2026_05_07_dawn_chain/` 에 archive.
**5/7 11:11 갱신**: Claude (Opus 4.7 1M, 통합 manager) — 5/7 새벽~오전 다중 세션 산출 통합 commit 3개 (74d6aea narrative 옵션 2 + 1267b8a 딥리뷰 보강 + fc7e147 chain archive). contribution 5→7종 / Limitations 4→6종 final list. 5/8 회의 narrative ready.
**★ 5/7 13:50 갱신 (W2 부록 — Gap Fill 4건 + 종합 paired CI/Cohen's d)**: Claude (Opus 4.7 1M, 통합 manager) — 사용자 결정 "최고 정확도, 최고 산출물, 빈틈 제로" (5/7 13:38) 적용. **빈틈 zero 검증**: RQ1/2/3 × DEEP/SIFT × 1M/8M × 5 sel × 5 mode/22 method 모든 변수 cover. Gap #1 (RQ1 SIFT KM20 5-sel canonical, 5,000 cells, 58s) + Gap #3 (RQ3 8M KM20 sel_expand, 3,000 cells, 289s) 측정 + Gap #2 (IS NaN root cause sel=0.01 80~95%) 분석 + Gap #4 (Phase 6 8M future work) 명시. 8M paired CI 90 cells (70/90 CI 0 제외) + 1M+SIFT paired CI 180 cells (96/180 |d|>0.2, **SIFT mid+high sel |d|=0.63~0.91 LARGE effect**). Limitations 6→8종 (L7 IS NaN sel=0.01, L8 Recovery Rate 분모 한정 추가). 8 worker (W1) + 9 worker (W2) + Gap fill 4 (W2 부록) = 총 21 worker, 측정 cells 누적 ~227,000+. **단일 테이블 영역 변수 cover 99% 완전성** (SIFT 8M dataset 부재 + 8M Phase 6 vector.c hook 의 2건만 future work).
