# Worker K — NMI / AMI metric 추가 (RQ3 ARI robustness check)

> **임무**: RQ3 딥리뷰 보강 §6.2 W3 P2 — 16 method × 2 dataset 의 NMI (Normalized Mutual Information) + AMI (Adjusted Mutual Information) 계산. ARI orthogonality ranking 의 robustness check.
> **세션 진입**: 본 핸드오프 첫 read → 5 ARI CSV 활용 + sklearn.metrics → 산출 + commit.
> **manager 세션**: 2026-05-07 12:15 KST, Opus 4.7 1M.
> **시간**: 1시간 (pure local 분석, narrative 보강)

---

## 1. 입력 자료

| 자료 | 위치 |
|---|---|
| 5 ARI CSV (16×16) | `experiments/results/rq3_agnostic/rq3_method_redundancy_ari{,_iid_96d,_deep_like_clustered_96d,_sift_like_skewed_128d,_pairs}.csv` |
| RQ3 딥리뷰 보강 (W3 P2 명시) | `_internal/RQ3_딥리뷰_보강_20260507.md` §6.2 |
| 기존 ARI 분석 driver | `experiments/code/local_analysis/rq3_method_redundancy_ari.py` 같은 |

## 2. 작업 단계

### Step 1 (15분) — Synthetic data 의 partition 라벨 재생성

5 ARI CSV는 이미 만들어져 있지만, NMI/AMI 계산을 위해서는 method 별 partition 라벨이 필요. 두 옵션:

**옵션 A**: ARI 계산 시 사용한 partition 라벨 재현 (synthetic IID/clustered/skewed)
**옵션 B**: 새로 synthetic data 생성 (96차원 IID + 20-cluster Gaussian + skewed) → 16 method 적용 → label 산출

**권장 옵션 A** (기존 결과 재현 — ARI 와 동일 condition):

```python
# experiments/code/local_analysis/rq3_method_redundancy_ari.py 의 logic 재현
# 또는 ARI script가 partition label parquet도 함께 저장했다면 그대로 활용
```

### Step 2 (30분) — NMI / AMI 계산

```python
import pandas as pd
import numpy as np
from sklearn.metrics import normalized_mutual_info_score, adjusted_mutual_info_score
from itertools import combinations

# 16 method partition labels (from Step 1)
methods = ['minibatch', 'minibatch_partial', 'random_proj', 'pca1d', 'hilbert',
           'zorder', 'hybrid', 'kdtree', 'pq', 'lsh', 'spectral', 'birch',
           'gmm', 'hdbscan', 'sobol', 'sparse_rp']

for condition in ['iid', 'clust', 'skew']:
    nmi_matrix = pd.DataFrame(index=methods, columns=methods, dtype=float)
    ami_matrix = pd.DataFrame(index=methods, columns=methods, dtype=float)

    labels = {m: load_partition_labels(m, condition) for m in methods}

    for m1, m2 in combinations(methods, 2):
        nmi = normalized_mutual_info_score(labels[m1], labels[m2])
        ami = adjusted_mutual_info_score(labels[m1], labels[m2])
        nmi_matrix.loc[m1, m2] = nmi_matrix.loc[m2, m1] = nmi
        ami_matrix.loc[m1, m2] = ami_matrix.loc[m2, m1] = ami
    for m in methods:
        nmi_matrix.loc[m, m] = ami_matrix.loc[m, m] = 1.0

    nmi_matrix.to_csv(f'experiments/results/rq3_agnostic/rq3_method_redundancy_nmi_{condition}.csv')
    ami_matrix.to_csv(f'experiments/results/rq3_agnostic/rq3_method_redundancy_ami_{condition}.csv')

# avg across 3 conditions
# rq3_method_redundancy_nmi.csv (iid + clust + skew avg)
# rq3_method_redundancy_ami.csv (avg)
```

### Step 3 (10분) — ARI vs NMI vs AMI 비교 narrative

`experiments/results/rq3_agnostic/rq3_method_redundancy_nmi_ami_summary.md`:

```markdown
# RQ3 Method Redundancy — NMI / AMI Robustness Check (W3 P2)

## ARI vs NMI vs AMI 일관성 점검

ARI orthogonality ranking (avg):
1. sparse_rp 0.122
2. pca1d 0.277
3. hilbert/zorder 0.31
4. kdtree 0.331
5. cluster method 4종 0.55+

NMI (avg) ranking 비교:
[표 — 1위~16위]

AMI (avg) ranking 비교:
[표 — AMI는 chance correction 으로 ARI와 더 유사]

→ 핵심 결론:
- 3 metric 모두 sparse_rp 1위 (가장 직교) ✓
- cluster method 4종 (minibatch/birch/spectral/hdbscan) 모두 redundant ✓
- "7-way ablation 의 정보 직교성" narrative 강화 (3 metric 일관)
```

### Step 4 (5분) — commit + push

```bash
git add experiments/results/rq3_agnostic/rq3_method_redundancy_nmi*.csv \
        experiments/results/rq3_agnostic/rq3_method_redundancy_ami*.csv \
        experiments/results/rq3_agnostic/rq3_method_redundancy_nmi_ami_summary.md \
        experiments/code/local_analysis/rq3_nmi_ami_metric.py
git commit -m "Worker K: RQ3 method redundancy NMI/AMI metric 추가 — ARI orthogonality robustness check (W3 P2 deferred 진행)"
git push
```

## 3. 산출 spec

| 산출 | 위치 | 형식 |
|---|---|---|
| NMI matrix 3 condition | `experiments/results/rq3_agnostic/rq3_method_redundancy_nmi_{iid,clust,skew}.csv` | 16×16 |
| AMI matrix 3 condition | `experiments/results/rq3_agnostic/rq3_method_redundancy_ami_{iid,clust,skew}.csv` | 16×16 |
| NMI / AMI avg | `rq3_method_redundancy_{nmi,ami}.csv` | 16×16 |
| Robustness narrative | `rq3_method_redundancy_nmi_ami_summary.md` | markdown |
| 분석 driver | `experiments/code/local_analysis/rq3_nmi_ami_metric.py` | Python |

## 4. 검증 기준

- [ ] 3 metric (ARI / NMI / AMI) 모두 sparse_rp 1위 (orthogonality 일관)
- [ ] cluster method 4종 모두 0.5+ (redundancy 일관)
- [ ] AMI 가 ARI 와 가장 유사 (chance correction 동일)

## 5. 의존성

- 독립 (다른 worker 영향 X)
- 5 ARI CSV 가 입력 — Worker C/E 의 자문 메일 / 보고서 narrative 보강 input 으로 활용 가능

## 6. 본 worker가 만들지 말 것

- ARI 결과 변경 (5 CSV 보존, NMI/AMI 추가만)
- master.md narrative 변경 (manager 책임)
- 새 method 추가 (16 method 보존)

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 12:15 KST
**기반**: RQ3 딥리뷰 보강 commit 1267b8a §6.2 W3 P2
