# 04 — RQ3 CaseB 결합 측정 raw

본 연구의 **결합 best −7.37% (Centroid tuple sparse_rp, A2-Fig9 single cell)** + **단독 대체 92.5% paired 우위** 의 raw 측정 데이터.

## 결합 (CaseB) 의미

paper §V-B Bernoulli 추정값 + 우리 method 의 추정값 산술 평균 (α=0.5).

## 핵심 finding (본 narrative §5 + §7)

- **결합 best: Centroid tuple sparse_rp −7.37%** (A2-Fig9 single cell, B1=1.5407 → 1.4271)
- **paired CaseB < CaseA: 92.5%** (455/492, p<1e-45) → 결합이 단독 대체보다 정확 (handoff_v12)
- 결합 best (−7.37%) < 단독 best (−10.17%) → **결합으로 단독 능가 X**
- 결합의 진짜 가치: method 선택 안정성 + cell spread 줄임 (더 큰 정확도 X)
- α sweep 결과: 4 method 중 3 method 가 α=0.5 (산술 평균) best (자세한 sweep 결과는 05_결합비율_alpha_sweep)

## 디렉토리

### pareto_top5_5method/
정확도 + 자원 효율 우위 5 method 의 9 cell CaseB 측정.

| Method | 9-cell CaseB Δ% mean |
|---|---:|
| sparse_rp | −9.43% |
| chao_weighted | −9.60% (Pareto Top 정확도) |
| pca1d | −9.63% |
| hilbert | −9.41% |
| hyperloglog | −8.65% (std 2.73 최저, 가장 안정) |

### 결합_best_Centroid_tuple/
다중 테이블 cell (A2-Fig9) 의 Centroid tuple cheap 근사 결과. 4 method × 2 mode = 8 file.

- **Centroid tuple** = single-table KM20 결과의 (s_DEEP, s_WIKI) tuple 을 새 stratum_id 로 사용
- 학습 비용 0 추가 (재학습 X)
- 4 method 모두 CaseB 보편 우위 (carry-over 대비 평균 −0.84%p 추가 정확도)

| Method | carry-over CaseB | Centroid tuple CaseB | 차이 |
|---|---:|---:|---:|
| sparse_rp | −6.58% | **−7.37%** ★ | −0.79%p |
| chao_weighted | −6.00% | −6.84% | −0.84%p |
| hilbert_real | −6.07% | −6.91% | −0.84%p |
| hyperloglog | −5.15% | −6.04% | −0.89%p |

## 파일명 규칙

- `A{cell번호}_{cell이름}_CaseB_{method}.json` (pareto_top5)
- `A2-Fig9_CaseB_{method}_Centroid_tuple.json` (결합_best)

## 출처

- 분석 file: `experiments/results/analysis/centroid_tuple_cheap_approximation_results_20260513.md`
- handoff: `_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` §10
- 본 narrative §5 / §7: 결합 시도 + 결합 진짜 가치
