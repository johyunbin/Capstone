# RQ2 5-mode × Selectivity 단조성 검정

RQ1 단조성 검정 (DEEP-KM20 ρ=-0.680, CI 0 제외) 과 동일 framework 로 RQ2 의 
5-mode (Equal/Proportional/Neyman/Anti-Neyman) 단조성 정량.

## per-seed Spearman ρ + 95% bootstrap CI

| dataset | mode | per-seed mean ρ | 95% CI | pooled ρ (sel mean) | MK p | 결론 |
|---------|------|---------------:|--------|--------------------:|-----:|------|
| DEEP | `equal` | +0.300 | [-0.160, +0.760] | +0.000 | 0.806 | 약함 |
| DEEP | `proportional` | +0.220 | [-0.080, +0.620] | +1.000 | 0.027 | 약함 |
| DEEP | `neyman` | +0.200 | [-0.040, +0.600] | +0.700 | 0.221 | 약함 |
| DEEP | `anti_neyman` | +0.160 | [-0.060, +0.540] | +0.000 | 0.806 | 약함 |
| SIFT | `equal` | -0.240 | [-0.600, +0.080] | -0.300 | 0.806 | 약함 |
| SIFT | `proportional` | +0.240 | [-0.120, +0.660] | +0.600 | 0.462 | 약함 |
| SIFT | `neyman` | +0.240 | [-0.160, +0.680] | +0.000 | 0.806 | 약함 |
| SIFT | `anti_neyman` | +0.160 | [-0.340, +0.660] | -0.100 | 1.000 | 약함 |

## 해석

**예상 패턴**:
- Equal/Proportional/Neyman: ρ < 0 (sel↓ → diff%↑, KM20 의 Level 2 효과).
- Anti-Neyman: ρ < 0 도 가능하나 reverse-direction 의 hurt 가 sel 에 따라 어떻게 변하는지.

**ρ CI 가 0 을 제외하는 mode** 가 "단조성 통계 확정" 으로 narrative 강화.
RQ1 의 KM20 single-arm 단조성과 RQ2 의 4-mode 단조성을 합쳐 본 연구의 "Level 2 효과"
narrative 가 통일.
