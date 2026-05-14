# PATCH — measure_paper_exact.py registry 추가 (Phase 4 11 method)

작성: 2026-05-11 KST (Phase 4 별도 세션, 메인 chain bvf1k64kw 영향 0)
대상 file: `_internal/scripts/measure_paper_exact.py` (server side: `/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py`)
신규 module: `_internal/scripts/method_phase4_extra.py` (smoke test 11/11 PASS — 10K × 32d, < 8s 총합)

---

## 0. 패치 개요

`_get_method_strata` 함수 (line 407+) 에 11 method 분기 추가. 패턴은 기존 `dbscan/kde_parzen/.../wavelet_hist` (line 471-483, Q4 Tier 1 통합) 와 동일한 단일 분기 + dispatch helper 사용.

### 0.1 신규 method (server scp 후 import 가능)

| code | method_name (registry) | assign_fn (method_phase4_extra) | priority |
|---|---|---|---|
| M1 | `chao_weighted` | `assign_chao_weighted` | P0 |
| M2 | `lpm1_proper` | `assign_lpm1_proper` | P0 (lpm2 misnomer rectify) |
| M3 | `cum_sqrtf` | `assign_cum_sqrtf` | P1 |
| M4 | `lavallee_hidiroglou` | `assign_lavallee_hidiroglou` | P1 |
| M5 | `idistance` | `assign_idistance` | P0 |
| M6 | `zorder_morton` | `assign_zorder_morton` | P0 (paradigm anchor) |
| M7 | `skilling_hilbert` | `assign_skilling_hilbert` | P0 (Q1 (C) ★3 rectify) |
| M8 | `ica_fastica` | `assign_ica_fastica` | P1 |
| M9 | `kmeans_neyman` | `assign_kmeans_neyman` | P0 (RQ2 plug-in) |
| M10 | `rabitq_strat` | `assign_rabitq_strat` | P1 (2024 fresh) |
| M11 | `idistance_neyman` | `assign_idistance_neyman` | P0 (synthesis) |

---

## 1. 패치 위치 1 — _get_method_strata 분기 추가

### 1.1 추가 위치 (Q4 Tier 1 분기 직후, line ~484)

기존 코드:
```python
    if method_name in ("dbscan", "kde_parzen", "mhist2", "hyperloglog", "rsvd", "wavelet_hist"):
        # Tier 1 신규 6 method (handoff_v3 Q4) — P9 InfoTheoretic + P10 Density 신규 paradigm 포함
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from method_tier1_p9_p10 import (
            assign_dbscan, assign_kde_parzen, assign_mhist2,
            assign_hyperloglog, assign_rsvd, assign_wavelet_hist,
        )
        fn_map = {
            "dbscan": assign_dbscan, "kde_parzen": assign_kde_parzen,
            "mhist2": assign_mhist2, "hyperloglog": assign_hyperloglog,
            "rsvd": assign_rsvd, "wavelet_hist": assign_wavelet_hist,
        }
        return fn_map[method_name](all_vecs, n_strata=n_strata, seed=seed)
```

### 1.2 추가 코드 (직후 삽입)

```python
    if method_name in (
        "chao_weighted", "lpm1_proper", "cum_sqrtf", "lavallee_hidiroglou",
        "idistance", "zorder_morton", "skilling_hilbert", "ica_fastica",
        "kmeans_neyman", "rabitq_strat", "idistance_neyman",
    ):
        # Phase 4 신규 11 method (cascade 7 stage 통과)
        # 출처: _internal/method_verification_20260510_phase4/_FINAL_LIST.md
        # 5/27 narrative 강화: P1+RQ2 / P2 (3) / P3 weight / P4 non-Gaussian / P5+RQ2 / P6 1-bit
        sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
        from method_phase4_extra import assign_phase4
        return assign_phase4(method_name, all_vecs, n_strata=n_strata, seed=seed)
```

---

## 2. 패치 위치 2 — METHOD_LIST 또는 Tier list 등록 (해당 시)

`measure_paper_exact.py` 의 `METHOD_LIST` 상수 (있을 경우) 또는 `TIER_S_METHODS` / `TIER_A_METHODS` 등 method registry에 11 method 추가.

기존:
```python
TIER_1_LEGACY = ["sparse_rp", "random_projection", "minibatch", "hilbert", "gmm",
                  "minibatch_partial", "lsh", "pca1d", "sobol", "reservoir", "faiss_ivf"]
TIER_B_EXTRA = ["pq", "kdtree", "halton", "hammersley", "coreset", "birch",
                 "agglomerative", "dense_rp"]
TIER_B_EXTRA2 = ["opq", "kdpp", "banditucb1", ...]
```

추가 (file 끝 또는 아래 line):
```python
TIER_PHASE4 = [
    "chao_weighted", "lpm1_proper", "cum_sqrtf", "lavallee_hidiroglou",
    "idistance", "zorder_morton", "skilling_hilbert", "ica_fastica",
    "kmeans_neyman", "rabitq_strat", "idistance_neyman",
]
```

---

## 3. 서버 SCP 명령 (메인 confirm 후 실행)

```bash
# 1. method_phase4_extra.py scp (신규 module)
scp _internal/scripts/method_phase4_extra.py \
    capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/method_phase4_extra.py

# 2. measure_paper_exact.py 패치 (위 §1.2 코드 추가) 후 scp
scp _internal/scripts/measure_paper_exact.py \
    capstone2026@165.132.140.240:/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py

# 3. server 측 import 검증
ssh capstone2026@165.132.140.240 \
    "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -c 'from method_phase4_extra import assign_phase4, ASSIGN_FN_MAP; print(list(ASSIGN_FN_MAP.keys()))'"

# 4. server 측 smoke test (10K × 32d, < 10s 예상)
ssh capstone2026@165.132.140.240 \
    "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 method_phase4_extra.py"
```

---

## 4. measurement launch 명령 (메인 confirm 후만)

`run_phase_b_phase4.sh` 별도 file 참조. 11 method × 9 cells × 2 modes (CaseA + CaseB) = 198 measurement cells.

ETA 추정:
- Per-cell: 30-60 min (handoff_main §10.1 stuck 정의 mtime 5분 monitor)
- Sequential: ~120-180 h (~5-7일)
- Parallel (4 procs): ~30-45 h (~1.5-2일)

권고: tmux session 4-6개로 분할 + monitor 30-60s polling.

---

## 5. 검증 sequence

1. 로컬 smoke test (이미 PASS): `python3 _internal/scripts/method_phase4_extra.py` → 11/11 ✓
2. server scp + import 검증 (메인 confirm 후)
3. server smoke (10K × 32d): 실행 결과 < 10s
4. server smoke (1M × 96d DEEP_sf1): 실행 결과 ≤ 5 min
5. server measurement single cell (A1-DEEP × CaseA × M9 kmeans_neyman, 5 trials × 100 query): ≤ 30 min
6. → 위 5 단계 통과 시 본 measurement launch

---

## 6. END

작성: 2026-05-11 KST
다음: server scp + import 검증 + smoke (메인 confirm 후) + measurement launch
