# experiments/code — 측정 script (5/14 정리)

> 본 연구의 paper exact 측정 main script 는 `_internal/scripts/` 에 위치. 본 디렉토리는 W1~W4 sprint 옛 script archive 만 보유.

## 활성 측정 script 위치

`_internal/scripts/`:

- `measure_paper_exact.py` — paper §V-B 재현 + 우리 method 측정 (1100 line, 5/10 launch)
- `_measure_common.py` — 공통 측정 library + N_STRATA=20 default
- `analyze_paper_exact.py` — 측정 결과 분석
- `figures_paper_exact.py` — paper_exact_v7/F1~F6.png 생성
- `compute_stratum_sigma_paper_exact.py` — σ_j 계산
- `method_hilbert_real.py` — Hilbert real method 구현 (★3 정정)
- `method_phase4_extra.py` — Phase 4 추가 method
- `method_tier1_p9_p10.py` — Tier 1 P9 InfoTheoretic + P10 Density method
- `run_phase_*.sh` — 측정 chain shell script

server 측정 script (server-only):
- `/tmp/launch_multijoin_restrat_v2.py` (multi-join 재계층화)
- `/tmp/launch_centroid_tuple.py` (Centroid tuple cheap 근사)
- `/tmp/launch_hash_bucketing.py` (B1 Hash)
- `/tmp/launch_pca_lowdim.py` (B2 PCA)
- `/tmp/launch_iter_refine.py` (B3 Iterative)
- `/tmp/launch_multivector_chain.py` (A2-Fig8 multi-vector)
- `/mnt/.../cache/rq3/measure_paper_exact_alpha.py` (α sweep)

## archive 구조

```
code/
├── README.md                              [본 파일]
└── archive/
    └── w1_w4_scripts/                     [W1~W4 sprint script, 4/16~5/10 mtime]
        ├── rq1/                           [27 file, Phase 4-7 + sift_rq1 measurement]
        ├── rq2/                           [5 file, KM20 alloc + sigma compute]
        ├── rq3/                           [43 file, 22 method runner + 16 sub-dir]
        └── local_analysis/                [42 file, figure generation]
```

## sub-dir 별 superseded 사유

### `rq1/` — RQ1 phase 4-7 + sift_rq1 measurement (27 file)

W1~W2 sprint RQ1 motivation script. 4/16 ~ 5/8 mtime.

**superseded by**: paper exact RQ1 측정 (`measure_paper_exact.py` 의 A1 single cell + A4 sel sweep + A5 scale sweep).

### `rq2/` — KM20 alloc + sigma compute (5 file)

W3 sprint RQ2 KM20 5-mode allocation script. 5/8 mtime.

**superseded by**: paper exact RQ2 측정 (`_measure_common.py` 의 `equal_alloc` / `proportional_alloc` / `neyman_alloc` / `anti_neyman_alloc` 함수).

### `rq3/` — RQ3 22 method runner (43 file, 16 sub-dir)

W4 sprint RQ3 method runner script. 4/27 ~ 5/10 mtime.

- 16 sub-dir: birch / gmm / hilbert / hilbert_real / ica_fastica / minibatch / minibatch_partial / opq / pq / rsvd / sparse_rp / thompson_sampling / zorder_morton 등

**superseded by**: paper exact RQ3 측정 (`measure_paper_exact.py` 안 통합된 43 method 측정).

`_measure_common.py` (5/8) 와 `hilbert/` (5/10) 도 본 archive 안 — paper exact framework 가 `_internal/scripts/_measure_common.py` 별도 사용.

### `local_analysis/` — figure generation (42 file)

W1~W4 sprint figure generation matplotlib script. 4/27 ~ 5/8 mtime.

**superseded by**: paper exact figure 생성 (`_internal/scripts/figures_paper_exact.py` 가 `experiments/figures/paper_exact_v7/F1~F6.png` 생성).

## 신규 측정 진행 시

새 measurement 진행 시 `_internal/scripts/` 의 `measure_paper_exact.py` base 사용. archive 안 W1~W4 script 직접 사용 비권장 (paper exact 정합성 보장 X).

server 측정 진행 시 `_internal/SERVER_REGISTRY.md` 참조.

---

작성: 2026-05-14 15:42 KST · 회의 의견 #9 archive 정리
