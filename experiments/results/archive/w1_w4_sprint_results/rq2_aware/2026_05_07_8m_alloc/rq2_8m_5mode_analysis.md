# RQ2 8M 5-mode allocation × 5 selectivity — Cross-Scale 분석

Worker_L 5/7 핸드오프 Step 5 산출. DEEP 1M ↔ 8M 일관성 정량.

**Source**: `rq2_alloc.parquet` (1M, 25,000 rows) + `rq2_alloc_DEEP_8M_5mode.parquet` (8M, 12,500 rows).

## 1. Cross-scale Δ% (BERN baseline) — per-seed mean ± 95% bootstrap CI

| mode | sel | 1M Δ% (95% CI) | 8M Δ% (95% CI) | sign 일관 | 8M/1M ratio |
|---|---|---|---|---|---|
| equal | 0.01 | +3.39% [-6.71, +13.04] | +0.07% [-4.22, +5.20] | ✓ | 0.02 |
| equal | 0.05 | -4.25% [-5.94, -2.55] | -0.89% [-3.20, +1.34] | ✓ | 0.21 |
| equal | 0.10 | -3.21% [-4.82, -2.11] | -0.09% [-1.31, +0.85] | ✓ | 0.03 |
| equal | 0.30 | -1.92% [-2.49, -1.37] | -0.09% [-0.71, +0.59] | ✓ | 0.05 |
| equal | 0.50 | -0.99% [-1.32, -0.66] | +0.23% [-0.14, +0.60] | × | -0.23 |
| proportional | 0.01 | -6.07% [-12.70, +0.29] | -6.28% [-10.56, -1.99] | ✓ | 1.03 |
| proportional | 0.05 | -4.86% [-6.76, -2.58] | +0.49% [-1.74, +2.94] | × | -0.10 |
| proportional | 0.10 | -4.40% [-5.83, -2.96] | +0.46% [-0.28, +1.05] | × | -0.10 |
| proportional | 0.30 | -1.99% [-2.70, -1.36] | -0.59% [-1.30, +0.05] | ✓ | 0.29 |
| proportional | 0.50 | -0.93% [-1.25, -0.49] | +0.15% [-0.47, +0.78] | × | -0.16 |
| neyman | 0.01 | -2.25% [-10.05, +5.25] | -3.14% [-9.25, +3.56] | ✓ | 1.40 |
| neyman | 0.05 | -4.34% [-6.01, -1.99] | -1.51% [-3.16, -0.23] | ✓ | 0.35 |
| neyman | 0.10 | -3.54% [-4.62, -2.46] | -0.23% [-2.36, +2.16] | ✓ | 0.07 |
| neyman | 0.30 | -1.65% [-2.11, -1.23] | -0.55% [-1.29, +0.09] | ✓ | 0.34 |
| neyman | 0.50 | -0.97% [-1.48, -0.54] | -0.13% [-0.46, +0.36] | ✓ | 0.14 |
| anti_neyman | 0.01 | -1.18% [-7.34, +4.90] | -4.53% [-10.07, +0.50] | ✓ | 3.85 |
| anti_neyman | 0.05 | -5.69% [-7.58, -2.39] | +0.60% [-0.81, +2.07] | × | -0.11 |
| anti_neyman | 0.10 | -3.32% [-5.16, -1.52] | +0.24% [-1.55, +2.06] | × | -0.07 |
| anti_neyman | 0.30 | -1.98% [-2.81, -1.23] | -0.25% [-0.85, +0.30] | ✓ | 0.13 |
| anti_neyman | 0.50 | -1.23% [-1.54, -0.83] | -0.03% [-0.49, +0.49] | ✓ | 0.03 |

**Δ%** = (mode median q_error − BERN median q_error) / BERN × 100. 음수 = mode 가 BERN 보다 정확.

## 2. 8M paired Wilcoxon (per-query × seed pairing, BH-FDR α=0.05)

| sel | mode | n | p (raw) | p (BH-FDR) | reject H0 |
|---|---|---|---|---|---|
| 0.01 | equal | 482 | 0.6849 | 0.9042 | × |
| 0.01 | proportional | 477 | 0.2552 | 0.5669 | × |
| 0.01 | neyman | 480 | 0.1327 | 0.4734 | × |
| 0.01 | anti_neyman | 478 | 0.07373 | 0.4734 | × |
| 0.05 | equal | 500 | 0.2834 | 0.5669 | × |
| 0.05 | proportional | 500 | 0.8837 | 0.9042 | × |
| 0.05 | neyman | 500 | 0.2317 | 0.5669 | × |
| 0.05 | anti_neyman | 500 | 0.283 | 0.5669 | × |
| 0.10 | equal | 500 | 0.8627 | 0.9042 | × |
| 0.10 | proportional | 500 | 0.9042 | 0.9042 | × |
| 0.10 | neyman | 500 | 0.3177 | 0.5776 | × |
| 0.10 | anti_neyman | 500 | 0.4565 | 0.7023 | × |
| 0.30 | equal | 500 | 0.5614 | 0.8021 | × |
| 0.30 | proportional | 500 | 0.06707 | 0.4734 | × |
| 0.30 | neyman | 500 | 0.09985 | 0.4734 | × |
| 0.30 | anti_neyman | 500 | 0.1362 | 0.4734 | × |
| 0.50 | equal | 500 | 0.852 | 0.9042 | × |
| 0.50 | proportional | 500 | 0.7695 | 0.9042 | × |
| 0.50 | neyman | 500 | 0.142 | 0.4734 | × |
| 0.50 | anti_neyman | 500 | 0.3774 | 0.629 | × |

## 3. σ_i 신호 — Anti-Neyman vs Proportional 격차

Anti-Neyman 은 σ_i 와 *역* 비례. Prop 보다 더 hurt → σ_i 신호 작동.
Anti-Neyman ≈ Prop → σ_i 신호 약함 (1M, 8M 공통 패턴).

| scale | sel | Anti-N Δ% | Prop Δ% | (AN − Prop) |
|---|---|---|---|---|
| 1M | 0.01 | -1.18% | -6.07% | +4.89 |
| 1M | 0.05 | -5.69% | -4.86% | -0.83 |
| 1M | 0.10 | -3.32% | -4.40% | +1.07 |
| 1M | 0.30 | -1.98% | -1.99% | +0.01 |
| 1M | 0.50 | -1.23% | -0.93% | -0.30 |
| 8M | 0.01 | -4.53% | -6.28% | +1.75 |
| 8M | 0.05 | +0.60% | +0.49% | +0.11 |
| 8M | 0.10 | +0.24% | +0.46% | -0.22 |
| 8M | 0.30 | -0.25% | -0.59% | +0.33 |
| 8M | 0.50 | -0.03% | +0.15% | -0.19 |

## 4. 핵심 결론

1. **1M 에서 stratified < BERN — 통계적 유의미**: 1M Δ% 음수 + per-seed CI 0 제외 (sel=0.05~0.30). 기존 1M paper finding 재확인.
2. **8M 에선 BERN 자연 정확도 상승 → stratified 우위 둔화**: 모든 (mode × sel) paired Wilcoxon p_adj > 0.45 (BH-FDR), 즉 stratified 와 BERN 평균은 통계적으로 구분 불가. N=8M 에선 BERN sample size 가 충분히 커서 KM20 의 추가 이득 사라짐.
3. **Sign 일관성 (1M ↔ 8M)**: Neyman 5/5 ★ 최우수, Equal 4/5, Anti-Neyman 3/5, Proportional 2/5. Neyman 의 σ-가중 stratification 만 N=8M 에서도 일관된 음수 Δ% 유지.
4. **σ_i 신호 약함 — 1M, 8M cross-scale 재현**: Anti-Neyman vs Prop 격차 sel=0.01 외 < 1%. 즉 σ_i 정보로 Prop 대비 추가 이득 미미 (오라클 sigma 라도). KM20 의 cluster size 정보가 주효과, σ-가중은 marginal.

## 5. 5/27 발표 / 6/11 보고서 입력

- **Slide 7 (RQ2 결론)**: "KM20 oracle 효과는 N↓ × sel↓ 영역에서 두드러짐 — N=1M 에선 stratified < BERN 유의미, N=8M 에선 BERN 자연 정확도 상승으로 둔화. Neyman 만 cross-scale sign 일관."
- **보고서 §4.2**: cross-scale 표 + 8M paired Wilcoxon + Anti-Neyman vs Prop 격차 → KM20 의 σ 정보 활용 한계 + sample-size dependent effect 제한.
- **Limitation 추가**: KM20 oracle 효과는 N↑ 에 따라 둔화 — production database 가 N↑ 일수록 stratification 의 marginal benefit 감소.

**산출**:
- `rq2_8m_5mode_cross_scale.csv` — 1M ↔ 8M Δ% 표 (per-seed mean ± 95% CI)
- `rq2_8m_5mode_wilcoxon.csv` — 8M paired Wilcoxon + BH-FDR (per-query × seed)
- `rq2_8m_sigma_signal_gap.csv` — Anti-Neyman vs Prop 격차 (σ_i 신호 정량)
