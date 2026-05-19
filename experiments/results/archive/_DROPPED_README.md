# Dropped Scope (5/10 01:25 KST 시점 — v0 final baseline)

> 본 문서는 본 연구의 측정 매트릭스에서 폐기된 데이터셋·셀·method 목록과 폐기 사유를 기록한다. 실제 데이터 (NPY / parquet / CSV) 는 삭제하지 않고 별도 디렉토리에 격리되어 있으며, 향후 reactivation 가능성과 audit log 보존을 위해 모두 유지된다.

---

## 1. 폐기 데이터셋 (1종)

### YFCC_PCA (96d, PCA-projected)

- **폐기 시점**: 5/10 01:14 KST
- **폐기 사유**: Exqutor 본 논문 (arXiv:2512.09695v2) §VI Table I 미수록. 5/7 우리 팀이 "PCA 96d 로 줄여서 DEEP 과 dim 맞추자" 결정으로 임의 추가했던 것이며, Exqutor 비교 baseline 으로서 의미 없음. raw YFCC (192d) 만 본 논문 매치 데이터셋.
- **격리 위치**: `_internal/cache/` 또는 서버 `/mnt/hdd0/home/capstone2026/cache/rq3/_DROPPED_yfcc_pca/` (48 NPY/parquet 격리)

---

## 2. 폐기 셀 (28 cell, sf=1+sf=10 합산)

### 2.1 YFCC_PCA single (4 cell)

- `deep_yfcc_pca_sf1`, `deep_yfcc_pca_sf10` (실제로는 `yfcc_pca_sf1`, `yfcc_pca_sf10`)
- 합계 2 cell (single 영역)

### 2.2 YFCC_PCA multi-4way (10 cell)

- `partsupp_deep_yfcc_pca_{1,10}`
- `partsupp_sift_yfcc_pca_{1,10}`
- `partsupp_fb_yfcc_pca_{1,10}`
- `partsupp_yfcc_yfcc_pca_{1,10}`
- `partsupp_yfcc_pca_wiki_{1,10}`

### 2.3 YFCC_PCA multi-join (2 cell)

- `multi_join_yfcc_pca_wiki_{1,10}`

### 2.4 image+image partsupp 4-way (12 cell, 5/10 01:18 폐기)

- **폐기 사유**: Exqutor Fig 8 = image+text only. partsupp 4-way 의 두 vector column 은 image embedding + text embedding 만 사용하며, image+image (DEEP+SIFT, DEEP+FB 등) 조합은 본 논문 미수록.
- 폐기 cell:
  - `partsupp_deep_sift_{1,10}`
  - `partsupp_deep_fb_{1,10}`
  - `partsupp_deep_yfcc_{1,10}`
  - `partsupp_sift_fb_{1,10}`
  - `partsupp_sift_yfcc_{1,10}`
  - `partsupp_fb_yfcc_{1,10}`

### 2.5 multi_join_wiki self-join (2 cell, 5/10 01:20 폐기)

- **폐기 사유**: Exqutor Fig 9 = image⋈text only (partsupp[image] ⋈ part[wiki]). wiki self-join 미수록.
- 폐기 cell: `multi_join_wiki_{1,10}`

---

## 3. 폐기 method (1)

### HNSW-SS (5/10 00:10 폐기)

- **폐기 사유**: 본 연구 narrative ("vector index 부재 환경") 위반. HNSW-SS 는 pgvector HNSW level-0 connected component 를 stratum 으로 사용하는 method 로, vector index 의 존재를 전제로 함. 우리 §V-B Adaptive Sampling augment 영역은 vector index 부재 환경이므로 narrative 와 충돌.
- 격리 위치: `_internal/scripts/methods/_DROPPED/hnsw_ss_strat.py`
- 대체: HNSW-SS 폐기와 동시에 LPM2 (Grafström-Lundström-Schelin Biometrics 2012, well-spread sampling design) 추가 → 36 method portfolio 유지.

---

## 4. 정리 후 v0 baseline

- **데이터셋**: 5 vector (DEEP, SIFT, FB(=SSN), WIKI, YFCC raw) + 1 join partner (partsupp[TPC-H])
- **셀**: 26 cell (Exqutor 100% 매치) + 3 SF=100 (Fig 4-6 reproducibility) = 29 total
  - Single: 10 cell (5 dataset × 2 sf)
  - Multi 4-way (Fig 8): 8 cell (4 dataset × 2 sf, image+text only)
  - Multi-join (Fig 9): 8 cell (4 dataset × 2 sf, image⋈text only)
  - SF=100 추가: 3 cell (DEEP/SIFT/FB(SSN) × partsupp)
- **Method**: 36 (11 baseline + 7 Tier S+ + 10 Tier A + 7 Tier B + 1 Tier C)
- **측정**: 36 × 26 = 936 + SF=100 36 × 3 = 108 → grand total 1,044 measurement

---

## 5. 격리 디렉토리 위치 (서버)

```
/mnt/hdd0/home/capstone2026/cache/rq3/
├── _DROPPED_yfcc_pca/        # 48 NPY/parquet (YFCC_PCA 4 single + 10 multi-4way + 2 multi-join 영역)
├── _DROPPED_imgimg/          # ~44 parquet (image+image partsupp 4-way 12 cell × 측정 결과)
└── _DROPPED_wiki_selfjoin/   # ~8 parquet (multi_join_wiki self-join 2 cell × 측정 결과)
```

**delete X** — revert 가능성 + audit log 보존 목적. 실험 종료 후 archive 확정 시점에 별도 결정.

---

## 6. 추적성

| 사건 | 기록 위치 |
|---|---|
| YFCC_PCA 폐기 결정 (5/10 01:14) | `_internal/state/_data_scope_decision_20260510_0114.md` |
| HNSW-SS 폐기 결정 (5/10 00:10) | `_internal/state/_kakaotalk_narrative_method_table_20260510_0030.md` §40 (HNSW-SS dropped) |
| image+image / wiki self-join 폐기 (5/10 01:18, 01:20) | `_internal/scripts/measure_multi_paradigm.py` CELL_4WAY/CELL_JOIN comment-out |
| v0 final baseline 확정 (5/10 01:25) | `_internal/handoff_v0_FINAL_SCOPE_20260510_0125.md` |
| v7 설계안 §18 final scope 정정 | `plans/RQ재정립_v7_evidence_20260509_1820.md` §18 |

---

문의: 조현빈 (wh8502@yonsei.ac.kr)
