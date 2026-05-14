# 06 — K granularity 측정 raw (K=10 / K=20 / K=30)

본 연구의 **method 별 K-sensitivity 분기** 측정 (강재현 5/13 1:00 정량 답변 요청).

## K granularity 의미

KM20 (paper §V-B default K=20) 대신 K=10 / K=30 도 측정해서 cluster granularity 가 method 의존적인지 검증.

## 핵심 finding (본 narrative 부록 + 회의 의견 #2)

| Method | K=10 mean Δ% | K=20 mean Δ% | K=30 mean Δ% | 패턴 |
|---|---:|---:|---:|---|
| **sparse_rp** | +5.05% (악화) | **−10.60%** | −6.78% | **U-shape, K=20 sweet spot** |
| **chao_weighted** | −10.63% | **−12.01%** | −10.39% | **K=20 sweet spot** |
| hilbert_real | −10.86% | −10.45% | **−11.26%** | **K-robust** |
| hyperloglog | −9.51% | −9.47% | **−9.86%** | **K-robust** |

→ **K=20 이 모든 method 의 best 가 아님**. method 의존적:
- quality-sensitive (sparse_rp / chao_weighted) = K=20 sweet spot
- quality-robust (hilbert_real / hyperloglog) = K=30 약간 우세

## ⚠️ Honest Limitation

**K granularity 측정은 SF=1 영역만 cover** (A1-DEEP/SIFT/SSN sf=100 + A2-Fig7/Fig9 sf=10 = 5 cells).
SF=10 영역 (A5-scale-sf10) 에서 K=20 이 best 인지는 본 측정 portfolio 에서 직접 검증 X.
→ 향후 추가 측정 영역 (회의 의견 #2).

## 디렉토리

| Dir | K 값 | 의미 |
|---|---|---|
| `K10/` | 10 | 거친 분할 (큰 cluster) |
| `K20_default_paper/` | **20 ★** | **paper §V-B default** |
| `K30/` | 30 | 미세 분할 (작은 cluster) |

각 K 별: 4 anchor method × 5 cells × 2 mode = 40 file × 3 K = 120 file (paired comparison 60)

## 파일명 규칙

`K{값}_{cell}_CaseB_{method}.json`

예시:
- `K10_A1-DEEP_CaseB_sparse_rp.json`
- `K30_A2-Fig9_CaseB_hilbert_real.json`

## 출처

- 분석 file:
  - `experiments/results/analysis/km_granularity_sensitivity_3way_K10_K20_K30_20260513.md`
  - `experiments/results/analysis/km_granularity_sensitivity_K10_vs_K20_20260513.md`
- 본 narrative 부록 (3-axis sensitivity 분석)
