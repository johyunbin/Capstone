# 05 — α sweep 측정 raw (★ 시나리오 B 확정의 핵심)

본 연구의 **시나리오 B 확정 narrative** (5/14 00:13 회수) 의 raw 측정 데이터.

## α sweep 의미

결합 mode 의 가중 평균: `est_final = α × est_B1 + (1-α) × est_method`

- α=0 = 우리 method 단독
- α=1 = paper Bernoulli 단독
- α=0.5 = 산술 평균 (default)

paper N=385 budget 안에서 두 estimator 공유.

## 핵심 finding (본 narrative §5 + §6)

- **4 method 중 3 method 가 α=0.5 (산술 평균) 에서 best** (sparse_rp / hilbert_real / chao_weighted)
- hyperloglog 만 α=0.6 best (0.26%p marginal)
- **양쪽 극단 (0.3 or 0.7) 에서 효과 감소** = U 자 형태 sensitivity
- **결합 best (−7.37% sparse_rp α=0.5) < 단독 best (−10.17% minibatch_partial)** → 결합으로 단독 능가 X
- 결론: **산술 평균이 결합 방식 중 best, 가중치 변화로 더 큰 개선 어려움** → 시나리오 B 확정

## 디렉토리

| Dir | α 값 | 의미 |
|---|---|---|
| `alpha_0.3/` | 0.3 | 우리 method 가중 (B1 0.3) |
| `alpha_0.4/` | 0.4 | 우리 method 가중 |
| `alpha_0.5_default/` | **0.5 ★** | **산술 평균 (default)** |
| `alpha_0.6/` | 0.6 | B1 가중 |
| `alpha_0.7/` | 0.7 | B1 가중 |

각 α 별 4 method (sparse_rp / hilbert_real / hyperloglog / chao_weighted) × A2-Fig9 single cell × CaseB = 4 file × 5 α = 20 file + default 16 file.

## 파일명 규칙

`alpha_{α}_{method}_A2-Fig9_CaseB.json`

예시:
- `alpha_0.3_sparse_rp_A2-Fig9_CaseB.json`
- `alpha_0.5_chao_weighted_A2-Fig9_CaseB.json`

## 출처

- 측정 script: server `/mnt/hdd0/.../cache/rq3/measure_paper_exact_alpha.py` (line 1067 의 `est_final` 계산을 `ALPHA_SWEEP` env var 받는 형태로 변경)
- tmux session: `alpha_sweep` (5/13 23:55 launch, 00:13 회수)
- 분석 file: `experiments/results/paper_exact_v7/analysis/alpha_sweep_results_20260514.md`
- 본 narrative §5 가중치 sweep: 시나리오 B 확정의 핵심
