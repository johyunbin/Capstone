# 07 — cheap 근사 4 후보 측정 raw (강재현 5/13 14:27 motivation)

본 연구의 **multi-table 영역 cheap 근사 검증** 4 후보 측정 (총 32 measurement, 5/13~5/14).

## 강재현 motivation (5/13 14:27 카톡 verbatim)

> "기존에 table 별로 clustering한 거를 저비용으로 multi-reclustering에 근사하는 방법 같은거"

## 핵심 finding (본 narrative §10)

| 후보 | 방법 | 결과 |
|---|---|---|
| **Centroid tuple** | 두 single-table KM20 결과 + (s_A, s_B) tuple top-K frequency folding (K^2=400 → K=20) | ★ **CaseB 보편 우위** (4 method 모두 평균 −0.84%p 추가, 학습 비용 0) |
| B1 Hash bucketing | (s_A × 31 + s_B × 17) % K deterministic hash | spread 매우 큼 (sparse_rp CaseA −10.93%p / hyperloglog CaseA +7.84%p harmful) |
| B2 PCA preprocessing | 864d concat → 64d PCA → KM20 | marginal (대부분 carry-over 와 비슷) |
| B3 Iterative refinement | KM_A centroid init + 864d 위 2 iter update | 일관 harmful (sub-optimal local minima) |

→ **Centroid tuple 만 robust + "더 싸고 더 좋은" 패턴**. 새 method axis "Cheap 근사 친화도" 발견:
- Friendly: hyperloglog + chao_weighted
- Indifferent: sparse_rp
- Hostile: hilbert_real

## 디렉토리

| Dir | 의미 | tmux |
|---|---|---|
| `centroid_tuple/` | ★ Centroid tuple cheap 근사 | mj_centroid (5/13 16:47~19:57) |
| `hash_bucketing_B1/` | B1 Hash bucketing | b1_chain (5/13 21:06 launch) |
| `pca_preprocessing_B2/` | B2 PCA preprocessing | b2_chain |
| `iterative_refinement_B3/` | B3 Iterative refinement | b3_chain |

각 후보: 4 anchor method × A2-Fig9 single cell × 2 mode = 8 file × 4 후보 = 32 file.

## 파일명 규칙

`{후보}_A2-Fig9_{Case}_{method}.json`

예시:
- `centroid_tuple_A2-Fig9_CaseB_sparse_rp.json` (★ 결합 best −7.37%)
- `hash_bucketing_A2-Fig9_CaseA_sparse_rp.json` (−10.93%p harmful)

## 출처

- wrapper script (server /tmp/): `launch_centroid_tuple.py` / `launch_hash_bucketing.py` / `launch_pca_lowdim.py` / `launch_iter_refine.py`
- 분석 file:
  - `experiments/results/analysis/centroid_tuple_cheap_approximation_results_20260513.md`
  - `experiments/results/analysis/cheap_approximation_extended_results_20260514.md`
- 본 narrative §10 다중 테이블: Centroid tuple = "더 싸고 더 좋은" best-of-both-worlds
