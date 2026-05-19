# RQ3 Method Redundancy — NMI / AMI Robustness Check (W3 P2)

ARI orthogonality ranking 의 robustness 점검. 동일 synthetic data +
동일 `_fit_methods` (`rq3_method_redundancy_ari.py` 재사용) 로 partition
label 일관 확보, ARI / NMI / AMI 3 metric 동시 계산.

- **NMI** (Normalized MI): chance correction X, 0~1 normalized
- **AMI** (Adjusted MI): chance correction O — ARI 의 information theoretic 대응
- **ARI** (Adjusted Rand): chance correction O — pairwise agreement (기존 metric)

3 condition (iid 96d / clustered 96d / skewed 128d) avg 기준.

## Orthogonality Ranking — avg pairwise off-diag (lower = more orthogonal)

| method | ARI_avg | rank | NMI_avg | rank | AMI_avg | rank |
|---|---:|---:|---:|---:|---:|---:|
| `sparse_rp` | +0.082 | 1 | +0.215 | 1 | +0.214 | 1 |
| `pca1d` | +0.195 | 2 | +0.401 | 3 | +0.400 | 3 |
| `kdtree` | +0.222 | 3 | +0.402 | 4 | +0.401 | 4 |
| `zorder` | +0.227 | 4 | +0.438 | 6 | +0.437 | 6 |
| `hilbert` | +0.231 | 5 | +0.440 | 7 | +0.440 | 7 |
| `lsh` | +0.236 | 6 | +0.372 | 2 | +0.371 | 2 |
| `hybrid` | +0.254 | 7 | +0.443 | 8 | +0.442 | 8 |
| `random_proj` | +0.268 | 8 | +0.417 | 5 | +0.417 | 5 |
| `sobol` | +0.302 | 9 | +0.479 | 9 | +0.478 | 9 |
| `pq` | +0.313 | 10 | +0.484 | 10 | +0.483 | 10 |
| `minibatch` | +0.369 | 11 | +0.519 | 11 | +0.518 | 11 |
| `minibatch_partial` | +0.381 | 12 | +0.519 | 12 | +0.519 | 12 |
| `gmm` | +0.382 | 13 | +0.524 | 13 | +0.523 | 13 |
| `spectral` | +0.384 | 14 | +0.524 | 14 | +0.524 | 14 |
| `hdbscan` | +0.388 | 15 | +0.528 | 15 | +0.528 | 15 |
| `birch` | +0.405 | 16 | +0.533 | 16 | +0.532 | 16 |

## Robustness 점검

- **Top-1 (가장 직교)**: ARI=`sparse_rp`, NMI=`sparse_rp`, AMI=`sparse_rp`
  → **3 metric 모두 일치** — 직교성 1위 결과 robust.

- **Spearman rank correlation** (3 metric ranking 일관성)
  - ARI ↔ NMI: ρ = +0.947
  - ARI ↔ AMI: ρ = +0.947  (chance correction 동일 — 가장 유사 기대)
  - NMI ↔ AMI: ρ = +1.000

- **Cluster paradigm method redundancy** (3 metric avg off-diag, ≥0.5 = redundant)

  | method | ARI_avg | NMI_avg | AMI_avg |
  |---|---:|---:|---:|
  | `minibatch` | +0.369 | +0.519 | +0.518 |
  | `minibatch_partial` | +0.381 | +0.519 | +0.519 |
  | `birch` | +0.405 | +0.533 | +0.532 |
  | `spectral` | +0.384 | +0.524 | +0.524 |
  | `hdbscan` | +0.388 | +0.528 | +0.528 |
  | `gmm` | +0.382 | +0.524 | +0.523 |

## 3-condition별 NMI/AMI matrix

- iid 96d: `rq3_method_redundancy_{nmi,ami}_iid.csv`
- clustered 96d: `rq3_method_redundancy_{nmi,ami}_clust.csv`
- skewed 128d: `rq3_method_redundancy_{nmi,ami}_skew.csv`
- 3-condition 평균: `rq3_method_redundancy_{nmi,ami}.csv`
- 3 metric ranking 비교: `rq3_method_redundancy_metric_ranking.csv`

## 결론 — RQ3 7-way 정보 직교성 narrative

3 metric (ARI / NMI / AMI) 가 같은 ranking 을 산출하면, 본 연구의 7-way
ablation (offline 4 / online 2 / weight 1) 이 정보적으로 직교한다는 narrative
는 단일 metric 의 artifact 가 아니라 robust 한 결과다. 특히 AMI 가 ARI 와
유사하면서 (chance correction 동일) NMI 와도 일치하면, '본 분석 결과는
metric 선택에 둔감하다' 는 자문 메일 / 보고서 보강 narrative 가 가능.

기존 ARI 5 CSV 는 보존, NMI/AMI 8 CSV + ranking CSV 1 + summary md 만 추가.
