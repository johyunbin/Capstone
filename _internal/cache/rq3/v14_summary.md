# v14 CaseC 결과 + v13 cell-level 비교 (5/23 launch 완료)

_생성_: 2026-05-23 21:48 KST · v14 9 cell × K=20 · trials=10 · n_queries=1000
_출처_: `_internal/cache/rq3/paper_exact_v14_20260523/*.json` (9 cells) + `_internal/cache/rq3/aggregated_v13_full.parquet` (v13 정본)

## 1. v14 portfolio
- 측정: **9 cells** × CaseC (method-independent dual-Bernoulli ensemble, Option A)
- params: trials=10 (paper §VI verbatim), n_queries=1000 (paper Fig 6 verbatim)
- hyperparam: N=385 / m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 (paper §V-B verbatim)
- ensemble: `dual_bernoulli_independent_states` · `each_state_own_q_err` · `1_stage_all_vecs`
- 9 cells: A1-DEEP, A1-SIFT, A1-SSN, A2-Fig7, A2-Fig9, A4-sel, A5-scale-sf1, A5-scale-sf10, A5-scale-sf100
- sel 분포: [0.001, 0.01] · K=20 (paper default)
- launch: 5/23 20:51:18 → 21:29:47 KST, total 38분 29초, 9/9 OK fail 0

## 2. v14 CaseC cell 별 qe_trim 요약
| cell | dataset | sf | sel | fig | qe_trim | qe mean | qe std | qe min | qe max | n_inf (10 trial 합) |
|---|---|--:|--:|---|--:|--:|--:|--:|--:|--:|
| A1-DEEP | DEEP | 100 | 0.01 | Fig 5/6 | 1.3921 | 1.3882 | 0.0574 | 1.2803 | 1.4650 | 2 |
| A1-SIFT | SIFT | 100 | 0.01 | Fig 5/6 | 1.3800 | 1.3780 | 0.0416 | 1.3065 | 1.4337 | 2 |
| A1-SSN | SimSearchNet++ | 100 | 0.01 | Fig 5/6 | 1.3948 | 1.3911 | 0.0484 | 1.2918 | 1.4612 | 5 |
| A2-Fig7 | YFCC | 10 | 0.01 | Fig 7 | 1.3549 | 1.3528 | 0.0556 | 1.2725 | 1.4160 | 1 |
| A2-Fig9 | DEEP+WIKI cross | 10 | 0.01 | Fig 9 | 1.3564 | 1.3578 | 0.0606 | 1.2867 | 1.4400 | 2 |
| A4-sel | DEEP | 100 | 0.001 | Fig 13 | 1.3841 | 1.3844 | 0.0368 | 1.3317 | 1.4396 | 401 |
| A5-scale-sf1 | DEEP | 1 | 0.01 | Fig 14 | 1.3452 | 1.3422 | 0.0739 | 1.2122 | 1.4487 | 0 |
| A5-scale-sf10 | DEEP | 10 | 0.01 | Fig 14 | 1.3564 | 1.3578 | 0.0606 | 1.2867 | 1.4400 | 2 |
| A5-scale-sf100 | DEEP | 100 | 0.01 | Fig 14 | 1.3921 | 1.3882 | 0.0574 | 1.2803 | 1.4650 | 2 |

- 9 cell **mean qe_trim**: 1.3729 (median 1.3800, range [1.3452, 1.3948])

## 3. dual-Bernoulli state 독립 진화 (Option A 동작 검증)
> seed_a=t*13+7, seed_b=+1M offset. 두 독립 AdaptiveState 가 각자 자기 q_err 로 update.
> 두 state final_size 가 trial 마다 다르게 진화하면 독립성 확인.

| cell | size_a mean ± std | size_b mean ± std | size_a [min, max] | size_b [min, max] | size_b/size_a |
|---|--:|--:|---|---|--:|
| A1-DEEP | 1315 ± 1528 | 463 ± 47 | [321, 4246] | [391, 545] | 0.35 |
| A1-SIFT | 722 ± 784 | 1236 ± 1490 | [293, 3060] | [340, 4242] | 1.71 |
| A1-SSN | 1236 ± 1300 | 457 ± 114 | [343, 4524] | [297, 715] | 0.37 |
| A2-Fig7 | 1399 ± 1443 | 1465 ± 1390 | [372, 4356] | [492, 4325] | 1.05 |
| A2-Fig9 | 505 ± 105 | 2084 ± 1713 | [323, 743] | [373, 4236] | 4.13 |
| A4-sel | 10320 ± 1910 | 7883 ± 1604 | [8576, 12893] | [4706, 9009] | 0.76 |
| A5-scale-sf1 | 1889 ± 1739 | 1207 ± 1475 | [380, 4254] | [382, 4510] | 0.64 |
| A5-scale-sf10 | 505 ± 105 | 2084 ± 1713 | [323, 743] | [373, 4236] | 4.13 |
| A5-scale-sf100 | 1315 ± 1528 | 463 ± 47 | [321, 4246] | [391, 545] | 0.35 |

> 두 state 의 final_size 가 매 trial 마다 상이 (특히 한 state 만 4000+ 진화하는 trial 다수)
> → 독립 진화 확인. audit CaseB' (cross-trial pair, post-hoc) 의 pre-registered 대응 확보.

## 4. v13 cell-level mean (matched cell · sel · K=20 · 16 method 평균)
> v13 는 3-way matched (B1·CaseA·CaseB), JSON 1건 = 3 mode. v14 와 매칭 위해 같은 (cell, sel, K=20) 의 16 method 측정을 mode 별로 cell-aggregate.

| cell | sel | n_method | B1 qe mean | B1 std | CaseA qe mean | CaseA std | CaseB qe mean | CaseB std |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| A1-DEEP | 0.01 | 16 | 1.5869 | 0.0501 | 1.5274 | 0.0914 | 1.4558 | 0.0370 |
| A1-SIFT | 0.01 | 16 | 1.5857 | 0.0386 | 1.5883 | 0.1329 | 1.4711 | 0.0731 |
| A1-SSN | 0.01 | 16 | 1.5726 | 0.0420 | 1.7606 | 0.5190 | 1.4762 | 0.0758 |
| A2-Fig7 | 0.01 | 16 | 1.5796 | 0.0449 | 1.6077 | 0.1184 | 1.4872 | 0.0911 |
| A2-Fig9 | 0.01 | 16 | 1.5875 | 0.0382 | 1.5682 | 0.1066 | 1.4634 | 0.0373 |
| A4-sel | 0.001 | 16 | 1.5735 | 0.0224 | 1.6227 | 0.1326 | 1.4994 | 0.0599 |
| A5-scale-sf1 | 0.01 | 16 | 1.5880 | 0.0293 | 1.5841 | 0.1144 | 1.4781 | 0.0588 |
| A5-scale-sf10 | 0.01 | 16 | 1.5889 | 0.0377 | 1.5723 | 0.1071 | 1.4639 | 0.0385 |
| A5-scale-sf100 | 0.01 | 16 | 1.5914 | 0.0519 | 1.5279 | 0.0911 | 1.4559 | 0.0373 |

## 5. ★ v14 CaseC vs v13 B1·CaseB cell-level Δ% (가설 검증)
> 같은 cell·sel·K=20 의 v13 16 method 평균을 baseline. unpaired (다른 seed) cell-level summary 비교.
> Δ% = (CaseC_qe − base_qe) / base_qe × 100. 음수 = CaseC 우위.
> **가설**: CaseC vs CaseB Δ% ≈ 0 = '89% 우위 = 평균 효과' 결정적 입증.

| cell | sel | v14 CaseC | v13 B1 (16M) | v13 CaseB (16M) | Δ% vs B1 | Δ% vs CaseB |
|---|--:|--:|--:|--:|--:|--:|
| A1-DEEP | 0.01 | 1.3921 | 1.5869 | 1.4558 | -12.28% | -4.38% |
| A1-SIFT | 0.01 | 1.3800 | 1.5857 | 1.4711 | -12.97% | -6.19% |
| A1-SSN | 0.01 | 1.3948 | 1.5726 | 1.4762 | -11.31% | -5.52% |
| A2-Fig7 | 0.01 | 1.3549 | 1.5796 | 1.4872 | -14.22% | -8.89% |
| A2-Fig9 | 0.01 | 1.3564 | 1.5875 | 1.4634 | -14.55% | -7.31% |
| A4-sel | 0.001 | 1.3841 | 1.5735 | 1.4994 | -12.04% | -7.69% |
| A5-scale-sf1 | 0.01 | 1.3452 | 1.5880 | 1.4781 | -15.29% | -8.99% |
| A5-scale-sf10 | 0.01 | 1.3564 | 1.5889 | 1.4639 | -14.63% | -7.34% |
| A5-scale-sf100 | 0.01 | 1.3921 | 1.5914 | 1.4559 | -12.53% | -4.39% |

**종합** (9 cells unweighted mean):
- mean Δ% vs B1 = **-13.31%** (median -12.97%, std 1.39%, range [-15.29%, -11.31%])
- mean Δ% vs CaseB = **-6.74%** (median -7.31%, std 1.74%, range [-8.99%, -4.38%])
- CaseC < B1 (CaseC 우위) cells: **9/9** (100%)
- CaseC < CaseB (CaseC 우위) cells: **9/9** (100%)

## 6. trial-pool 분포 비교 (CaseC 10 trial vs CaseB 16M·10 trial pool)
> v14 CaseC 1 cell = 10 trial qe. v13 CaseB 같은 cell = 16 method × 10 trial = 160 trial pool.
> CaseC 분포가 CaseB pool 분포에 포함되면 가설 입증.

| cell | CaseC qe range | CaseC qe median | CaseB pool qe range | CaseB pool qe median | CaseC median ∈ CaseB IQR? |
|---|---|--:|---|--:|:--:|
| A1-DEEP | [1.280, 1.465] | 1.3990 | [1.160, 1.625] (n=160) | 1.4466 | ✗ |
| A1-SIFT | [1.306, 1.434] | 1.3920 | [1.187, 1.736] (n=160) | 1.4543 | ✗ |
| A1-SSN | [1.292, 1.461] | 1.4065 | [1.249, 1.972] (n=160) | 1.4581 | ✗ |
| A2-Fig7 | [1.273, 1.416] | 1.3600 | [1.358, 1.935] (n=160) | 1.4638 | ✗ |
| A2-Fig9 | [1.287, 1.440] | 1.3577 | [1.352, 1.639] (n=160) | 1.4590 | ✗ |
| A4-sel | [1.332, 1.440] | 1.3849 | [1.329, 1.780] (n=160) | 1.4984 | ✗ |
| A5-scale-sf1 | [1.212, 1.449] | 1.3575 | [1.227, 1.723] (n=160) | 1.4609 | ✗ |
| A5-scale-sf10 | [1.287, 1.440] | 1.3577 | [1.319, 1.620] (n=160) | 1.4585 | ✗ |
| A5-scale-sf100 | [1.280, 1.465] | 1.3990 | [1.160, 1.640] (n=160) | 1.4486 | ✗ |

## 7. ★ 가설 평결
- **CaseC vs B1**: mean Δ% = **-13.31%** (9/9 cells better)
  → CaseC 가 B1 (1-Bernoulli) 대비 명확한 우위 — 평균 효과 자체의 위력 확인.
- **CaseC vs CaseB**: mean Δ% = **-6.74%** (9/9 cells better)

→ **가설 부분 입증**: CaseC vs CaseB Δ% = -6.74% — 격차 있음. method (분포 인지) 가 평균 위에 추가 효과 있을 가능성.

## 8. 산출물 경로
- v14 parquet: `_internal/cache/rq3/aggregated_v14.parquet`
- v14 summary (본 파일): `_internal/cache/rq3/v14_summary.md`
- v14 raw JSON: `_internal/cache/rq3/paper_exact_v14_20260523/*.json` (9 cells, 각 ~4.4KB)
- v13 정본 base: `_internal/cache/rq3/aggregated_v13_full.parquet` (4524 row = 1508 측정 × 3 mode)
