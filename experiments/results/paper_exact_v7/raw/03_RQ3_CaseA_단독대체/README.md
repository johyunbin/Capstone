# 03 — RQ3 CaseA 단독 대체 측정 raw

본 디렉토리는 본 연구의 **단독 대체 best −10.17% (minibatch_partial, 9-cell mean)** 의 raw 측정 데이터.

## 단독 대체 (CaseA) 의미

paper §V-B Bernoulli 추정값을 우리 method 의 추정값으로 단순 교체. 결합 X.

## 핵심 finding (본 narrative §4 + §11.1)

- **단독 best: minibatch_partial −10.17%** (9-cell mean, B1=2.090 → 1.877)
- 통계 일관 우위 method 15 개 (−5 ~ −12% 범위)
- paper 재현 변동 −4.3% 의 약 2.4 배

## 디렉토리

### pareto_top5_5method/
정확도 + 자원 효율 모두 우위인 5 method 의 9 cell CaseA 측정.

| Method | paradigm | fit 시간 | 9-cell CaseA Δ% mean |
|---|---|---:|---:|
| sparse_rp | 차원 축소 (Li-Hastie-Church 2006) | 0.1s | (분석 file 참조) |
| chao_weighted | 스트리밍 (Chao 1982) | 0.5s | (분석 file 참조) |
| pca1d | 차원 축소 (Pearson 1901) | 0.5s | (분석 file 참조) |
| hilbert / hilbert_real | 공간 분할 (Faloutsos 1989) | 0.1-0.5s | (분석 file 참조) |
| hyperloglog | 정보 이론 (Flajolet 2007) | 0.5s | (분석 file 참조) |

### 단독_best_minibatch_partial/
본 portfolio 단독 best method 의 9 cell CaseA 결과.

cell 별 Δ%:
| Cell | B1 baseline | CaseA | Δ% |
|---|---:|---:|---:|
| A1-DEEP | 1.613 | 1.353 | −15.92% |
| A1-SIFT | 1.670 | 1.301 | −21.73% |
| A1-SSN | 1.621 | 1.655 | +2.10% (worse) |
| A2-Fig7 | 1.633 | 1.413 | −12.61% |
| A2-Fig9 | 1.528 | 1.353 | −10.71% |
| **mean (9 cell)** | **2.090** | **1.877** | **−10.17%** |

## 파일명 규칙

`A{cell번호}_{cell이름}_CaseA_{method}.json`

예시:
- `A1_DEEP_CaseA_minibatch_partial.json`
- `A2-Fig9_CaseA_sparse_rp.json`

## 출처

- 측정 script: `_internal/scripts/measure_paper_exact.py`
- 분석 file: `experiments/results/paper_exact_v7/analysis/method_level_breakdown_20260513.md`
- handoff: `_internal/handoff/active/handoff_v17_session_finalize_20260514_0721.md` §10
- 본 narrative §4 / §11.1: 단독 대체 best
