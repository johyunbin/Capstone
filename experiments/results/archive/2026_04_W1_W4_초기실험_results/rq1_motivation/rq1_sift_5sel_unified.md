# RQ1 — SIFT 1.5M 5-sel 통합 단조성 (Worker J, 2026-05-07)

## 데이터 source

- **bern_5sel_canonical**: `rq3_random20_sift.parquet (5 sel × 5 seed × 100 q)`
- **km20_partial**: `sift_mid_sel.parquet (s=0.1, s=0.3 only, 5 seed)`
- **phase7_sql_legacy**: `phase7_sift_{bern,strat}.parquet (s=0.5 SQL, single)`

## BERN 5-sel canonical (rq3_random20_sift, 5 seed × 100 q)

| sel | median q_error (mean ± std, 5 seed) |
|---|---|
| 0.01 | 1.3506 ± 0.1162 |
| 0.05 | 1.1688 ± 0.0260 |
| 0.10 | 1.1224 ± 0.0121 |
| 0.30 | 1.0559 ± 0.0067 |
| 0.50 | 1.0359 ± 0.0021 |

**per-seed Spearman ρ (sel ↑ vs bern q_error ↑)**: -1.000 ± 0.000 (min -1.000, max -1.000, n=5 seeds)

→ ρ 부호로 단조성 방향성 판단 (양수: sel ↑ ⇒ q_error ↑, 음수: 반전).

## KM20 partial (sift_mid_sel, 2 sel × 5 seed × 100 q)

| sel | median q_error (km20, mean ± std) | km20 vs bern Δ% |
|---|---|---|
| 0.10 | 1.0888 ± 0.0114 | -8.85% ±0.97 |
| 0.30 | 1.0386 ± 0.0022 | -7.26% ±0.52 |

## Phase 7 SQL legacy (s=0.5, single measurement)

- bern median q_error: 3875.3428
- km20 median q_error: 9.4750
- Δ%: -99.76% (n=100 q, single seed)

## Limitations

- KM20 5-sel canonical 측정 부재 (s=0.01, s=0.05 km20 미측정).
- phase7_sift s=0.5 는 SQL D_target single measurement → numpy methodology 와 직접 비교 X.
- 통합은 driver 단계에서만 정합 (numpy/SQL D 차이 잔존).

## Cross-scale 의의 (DEEP 1M ↔ 8M ↔ SIFT 1.5M)

- DEEP 1M (5 sel canonical): gradient 19.6%p (s=0.01) — Phase 6/7 비교에서 확인.
- DEEP 8M (별도 산출 `rq1_8m_monotonicity.md` 참조): Phase 7 numpy methodology 통일.
- SIFT 1.5M: BERN ρ 부호 + km20 mid-sel(0.1/0.3) Δ% 로 단조성 일관성 boundary 평가.
