# RQ1 — DEEP 8M 5-sel × 5 seed 단조성 (Worker J, 2026-05-07)

**Methodology**: Phase 7 numpy D_target | sample_size=385 | n_strata=20 (KM20) | 100 queries × 5 seeds × 5 sels

## 1. per-sel mean ± std (5 seed)

| sel | bern q_error (mean ± std) | km20 q_error (mean ± std) | diff_pct (km20-bern, %) |
|---|---|---|---|
| 0.01 | 1.4046 ± 0.0979 | 1.4331 ± 0.0341 | +2.42% ± 7.45 |
| 0.05 | 1.1710 ± 0.0341 | 1.1741 ± 0.0093 | +0.35% ± 3.60 |
| 0.10 | 1.1259 ± 0.0140 | 1.1104 ± 0.0124 | -1.36% ± 2.04 |
| 0.30 | 1.0561 ± 0.0078 | 1.0536 ± 0.0063 | -0.23% ± 0.78 |
| 0.50 | 1.0393 ± 0.0037 | 1.0363 ± 0.0062 | -0.28% ± 0.51 |

## 2. Spearman ρ per seed (단조성 방향)

| ρ on | mean ± std | min | max | n |
|---|---|---|---|---|
| sel ↑ vs **bern_q_error** | -0.980 ± 0.045 | -1.000 | -0.900 | 5 |
| sel ↑ vs **km_q_error** | -1.000 ± 0.000 | -1.000 | -1.000 | 5 |
| sel ↑ vs **diff_pct** | -0.120 ± 0.904 | -1.000 | +1.000 | 5 |

- bern_q_error/km_q_error: ρ ≈ -1 → sel ↑ ⇒ q_error ↓ 강한 단조성 (sample 수 증가 효과).
- diff_pct: km20 우월성의 sel 의존성. ρ < 0 면 low-sel 에서 km20 효과 큼.

## 3. Cross-scale 비교 (1M Phase 7 vs 8M Phase 7)

| sel | 1M diff_pct (mean ± std) | 8M diff_pct (mean ± std) | Δ (8M − 1M, %p) |
|---|---|---|---|
| 0.01 | +3.33% ± 4.60 | +2.42% ± 7.45 | -0.91%p |
| 0.05 | -2.60% ± 2.00 | +0.35% ± 3.60 | +2.95%p |
| 0.10 | -1.31% ± 2.25 | -1.36% ± 2.04 | -0.06%p |
| 0.30 | -0.99% ± 0.71 | -0.23% ± 0.78 | +0.76%p |
| 0.50 | -1.23% ± 0.37 | -0.28% ± 0.51 | +0.94%p |

**해석**: |Δ| 가 1M Phase 6↔7 gradient 19.6%p 보다 작을수록 methodology 통일 시 scale-invariance 강함. 각 sel 의 Δ 부호/크기로 cross-scale 일관성 정량화.

## 4. Gradient 19.6%p 의 8M 재현

- 1M Phase 7 numpy s=0.01 diff_pct: **+3.33%**
- 8M Phase 7 numpy s=0.01 diff_pct: **+2.42%**
- |Δ| (8M − 1M, Phase 7 통일): **0.91%p**
- 1M 자체 Phase 6 vs Phase 7 gradient (참조): **19.6%p** (methodology 효과)

→ 8M Phase 7 vs 1M Phase 7 의 |Δ| 가 0 에 근접 → methodology 통일 시 cross-scale 일관성. 1M Phase 6 vs 1M Phase 7 의 19.6%p gradient 는 methodology 효과.

## 5. Limitations

- 100 queries × 5 seed → bootstrap CI 는 query-level resample 만 (seed-level 추가 안함).
- 8M Phase 6 (SQL D) 미측정 — Phase 7 numpy methodology 단일 비교만.
- Sample size 385 fixed — sample_size sensitivity 별도 분석 (8m_sel_expand worker 영역).
