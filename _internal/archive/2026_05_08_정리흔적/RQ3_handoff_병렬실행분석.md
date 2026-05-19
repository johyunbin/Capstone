# RQ3 측정 병렬/순차 실행 분석 + wrapper 보완 가이드

> **`_internal/RQ3_handoff_to_main_session.md` 의 보강 자료.**
> 메인 세션이 8M 보강 측정 마무리 후 RQ3 측정에 진입할 때 "병렬로 돌릴 수 있는가, 순차로만 돌려야 하는가" 의 의사결정 자료.
>
> 작성: 병렬 세션 (조현빈 + Claude) · 2026-05-06 18:18 KST

---

## ★ 30초 결론

- **시나리오 B (DEEP / SIFT 두 process 동시 실행) 권장**. 서버 자원 충분, 시간 50% 절감 (~7h → ~3.5h).
- 미완성 wrapper 1종 (`run_hilbert.py`) 메인 세션 진입 직후 ~10분이면 보완 가능 (`run_random_projection.py` 패턴 그대로).
- 각 method 의 wrapper 는 독립 fetch 실행 — fetch 캐시 (npz) 재활용은 추가 인프라 필요, W2 후반에 검토.

---

## 1. 현재 wrapper 상태 (2026-05-06 18:14 KST 기준)

### 1.1 commit 된 wrapper (`_measure_common.py` 백엔드 사용)

| wrapper | 측정 method | 입력 | 산출 |
|---|---|---|---|
| `run_random20.py` | RANDOM20 baseline (recovery 분모) | `assign_random20()` 무작위 stratum_id | `rq3_random20.parquet` |
| `run_minibatch.py` | F. MiniBatch K-means (#8) | `train_minibatch_kmeans` + `assign_minibatch` | `rq3_minibatch.parquet` |
| `run_random_projection.py` | C. Random Projection (#5) | `make_projection` + `assign_random_projection` | `rq3_random_proj.parquet` |
| `run_lsh.py` | A. LSH (#6) | hyperplane sign hash + mod K | `rq3_lsh.parquet` |

→ 위 4종은 동일 패턴 — `fetch_all_vectors_safe(ds)` → method 별 stratum_id 부여 → `run_method_measurement()`.

### 1.2 자체 `main()` 보유 method (wrapper 불필요, 단독 실행)

| 측정 모듈 | 측정 method | 비고 |
|---|---|---|
| `kde/kde_pilot.py` | B. KDE-pilot (#10) | Online — query-time pilot, cluster cache 자체 구현 |
| `online_weight/distance_shell.py` | G. Distance-Shell (#9) | Online — flat cache, 5-shell quantile + Neyman |
| `online_weight/importance_sampling.py` | H. Importance Sampling (#11) | Weight — 비분할, KDE proposal × pilot×clip 2x2 |

→ 위 3종은 `_measure_common.py` 우회. 자체 `cache_cluster_samples` + `bernoulli_estimate` + main(). `python3 kde_pilot.py` 식 단독 실행.

### 1.3 미완성 wrapper

| wrapper (필요) | 측정 method | 보완 작업 |
|---|---|---|
| `run_hilbert.py` | E. Hilbert Curve (#7) | `run_random_projection.py` 패턴 + `hilbert/hilbert_curve.py` 의 `fit_hilbert_mapper` + `assign_hilbert` 호출. ~10분 |

→ **권장 진입 절차**: 메인 세션이 진입 직후 첫 ~10분에 `run_hilbert.py` 작성 후 측정 시작. (또는 W2 시작에 작성, 그 전에 #5/#6/#8/#9/#10/#11 부터 측정 시작도 무방.)

---

## 2. 병렬 vs 순차 실행 시나리오 분석

### 2.1 측정 단계의 cost 분해

각 wrapper 의 실행 시간:
- **Phase 1: fetch_all_vectors_safe**: cluster 단위 fresh conn 으로 ~1M (DEEP) / 1.5M (SIFT) vector fetch. 약 **5~7분** (DEEP), **7~10분** (SIFT).
- **Phase 2: stratum_id 부여**: method 별, 보통 **1초~수십초** (MiniBatch 30초, 나머지 ~수초).
- **Phase 3: cache_cluster_samples_inmem**: in-memory 분할 + sample. **~수초**.
- **Phase 4: 측정 (5 sel × 5 seed × 100 query × HT estimator)**: 약 **20~30분** / dataset.

→ 단일 wrapper 단일 dataset = **~30분 (fetch) + 20~30분 (측정) ≈ 30~40분**.

자체 `main()` method 들 (kde/distance_shell/importance) 은 fetch 대신 cluster 별 LIMIT 500 sample (~수십초) → 단일 method 단일 dataset = **~30분**.

### 2.2 시나리오 A — 단일 process, 순차 (가장 단순)

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && \
  python3 rq3/run_random20.py --include-bernoulli && \
  python3 rq3/run_minibatch.py && \
  python3 rq3/run_random_projection.py && \
  python3 rq3/run_lsh.py && \
  python3 rq3/run_hilbert.py && \
  python3 rq3/online_weight/distance_shell.py && \
  python3 rq3/kde/kde_pilot.py && \
  python3 rq3/online_weight/importance_sampling.py"
```

- 8 measurement (RANDOM20 baseline + 7 method) × 평균 35분 ≈ **~5h**
- 실측 가까이는 fetch 가 8 × 2 dataset = 16번 (~2h) + 측정 8 × 2 dataset = 16번 × 25분 = 6h 40분. 합쳐 약 **8h~9h** (debug 시간 포함 시 더).

→ **장점**: 디버깅 단순. 한 wrapper 가 실패하면 다음으로 진행 안 함.
→ **단점**: 8h+ 소요. 5/8 19:00 회의 + W2 측정 시간 압박.

### 2.3 시나리오 B — DEEP / SIFT 두 process 병렬 (★ 권장)

```bash
# Terminal 1 (DEEP 만)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && \
  python3 rq3/run_random20.py --datasets DEEP --include-bernoulli && \
  python3 rq3/run_minibatch.py --datasets DEEP && \
  python3 rq3/run_random_projection.py --datasets DEEP && \
  python3 rq3/run_lsh.py --datasets DEEP && \
  python3 rq3/run_hilbert.py --datasets DEEP && \
  python3 rq3/online_weight/distance_shell.py --datasets DEEP && \
  python3 rq3/kde/kde_pilot.py --datasets DEEP && \
  python3 rq3/online_weight/importance_sampling.py --datasets DEEP"

# Terminal 2 (SIFT 만, 동시)
ssh capstone "... 같은 명령, --datasets SIFT"

# 두 process 의 출력 parquet 명이 충돌하면 안 되므로:
#   --out-prefix rq3_minibatch_deep / rq3_minibatch_sift 형태로 분리 권장
#   (또는 데이터셋 컬럼이 들어가니 어차피 분석 시 concat 으로 무방)
```

- DEEP / SIFT process 동시 → 총 시간 = **max(DEEP, SIFT) ≈ 4~4.5h**
- 두 process 의 PG 동시 connection: 각 fresh conn per cluster (KM20 의 20 cluster) × 2 dataset = peak ~40 connections + 2 process = ~42. PG `max_connections` default 100 이상 → **안전**.
- 메모리: 각 process 가 vector 1M~1.5M × 96~128d float32 = ~500MB~700MB. 두 process = ~1.5GB. 서버 RAM 통상 32GB+ → **안전**.
- CPU: 측정 phase 는 numpy 단일 thread bound — 두 process = 2 core 점유. 서버 16+ core 가정 → **안전**.

→ **장점**: 단순 (옵션 `--datasets DEEP/SIFT` 분리만), ~50% 시간 절감.
→ **주의**: parquet 파일명 충돌 회피 위해 `--out-prefix` 갈라야 함. 또는 측정 종료 후 DEEP/SIFT 결과 concat 해서 단일 parquet 으로.

### 2.4 시나리오 C — method 단위 병렬 (비추천)

8 method × 2 process 동시 실행. fetch 가 16번 동시 → PG load 폭증 + 메모리 ~12GB. 서버 자원 측면에서 큰 부담. 시간 단축 효과는 fetch bottleneck 으로 제한적.

→ **비추천**.

### 2.5 시나리오 D — fetch 캐시 + method 순차 (W2 후반 검토)

각 wrapper 가 매번 fetch 하는 비효율을 제거하기 위해 fetch 결과를 npz 로 dump:

```python
# 1회 실행 (DEEP / SIFT 각각)
all_vecs, km_sids = fetch_all_vectors_safe(ds)
np.savez("/tmp/rq3_cache_deep.npz", vecs=all_vecs, km_sids=km_sids)

# 각 wrapper 가 npz 부터 load (fetch 안 함)
data = np.load("/tmp/rq3_cache_deep.npz")
all_vecs = data["vecs"]; km_sids = data["km_sids"]
```

→ 효과: 7 wrapper × 2 dataset 의 fetch 를 1 dataset 1번으로 압축. 시간 추가 ~1h 절감.
→ 단점: wrapper 들 모두 수정 필요 (`fetch_all_vectors_safe` → `load_cached_vectors`). 추가 인프라.
→ **W2 후반** 시간 여유 시 검토. **W1 sprint (~5/8) 안에는 시나리오 B 권장**.

---

## 3. 권장 실행 순서 (시나리오 B 적용)

### 3.1 메인 세션 진입 직후 (8M 측정 마무리 후 ~30분)

```bash
# 0. 동기화
cd ~/Capstone
git pull --no-rebase origin main

# 1. (선택) run_hilbert.py 보완 — 미완성 wrapper 보완. ~10분
#    `run_random_projection.py` 를 base 로 hilbert/hilbert_curve.py 의
#    fit_hilbert_mapper / assign_hilbert 로 교체.
cp experiments/code/rq3/run_random_projection.py experiments/code/rq3/run_hilbert.py
# (편집: import 경로 + method 호출 + extra_meta)

# 2. 서버 sync
scp -r experiments/code/rq3 capstone:/mnt/hdd0/home/capstone2026/cache/

# 3. RANDOM20 baseline (recovery 분모, 1번만, 두 dataset 동시 OK)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && \
  python3 rq3/run_random20.py --include-bernoulli"   # ~10분
```

### 3.2 7-way 병렬 측정 (시나리오 B)

```bash
# 두 ssh terminal 동시 실행. 우선순위 순:
# Priority 1: F (#8) MiniBatch — 가장 중요, recovery 75~95% 기대
# Priority 2: C (#5) Random Projection — 단순 하한
# Priority 3: E (#7) Hilbert — contribution 후보
# Priority 4: A (#6) LSH
# Priority 5: B (#10) KDE-pilot — 이론 상한
# Priority 6: G (#9) Distance-Shell
# Priority 7: H (#11) Importance Sampling

# Terminal 1 (DEEP)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && \
  python3 rq3/run_minibatch.py --datasets DEEP --out-prefix rq3_minibatch_deep && \
  python3 rq3/run_random_projection.py --datasets DEEP --out-prefix rq3_random_proj_deep && \
  python3 rq3/run_hilbert.py --datasets DEEP --out-prefix rq3_hilbert_deep && \
  python3 rq3/run_lsh.py --datasets DEEP --out-prefix rq3_lsh_deep && \
  python3 rq3/kde/kde_pilot.py --datasets DEEP --out-prefix rq3_kde_pilot_deep && \
  python3 rq3/online_weight/distance_shell.py --datasets DEEP --out-prefix rq3_distance_shell_deep && \
  python3 rq3/online_weight/importance_sampling.py --datasets DEEP --out-prefix rq3_importance_deep"

# Terminal 2 (SIFT, 위 명령 완전 동일하나 DEEP → SIFT)
```

→ **두 process 동시 → 약 3.5~4h 소요.**

### 3.3 결과 회수 + 통합

```bash
# 모든 parquet 회수
mkdir -p experiments/results/rq3_agnostic/2026_05_07_first_runs
scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_*.parquet' \
    'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_*_meta.json' \
    experiments/results/rq3_agnostic/2026_05_07_first_runs/

# DEEP/SIFT 분리 parquet 들을 method 별 통합 (또는 Python concat 직접)
python3 -c "
import pandas as pd, glob
for m in ['minibatch','random_proj','hilbert','lsh','kde_pilot','distance_shell','importance']:
    parts = [pd.read_parquet(f) for f in glob.glob(f'experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_{m}_*.parquet')]
    if parts:
        pd.concat(parts).to_parquet(f'experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_{m}.parquet')
"
```

### 3.4 분석 + figures (단일 process, ~10분)

```bash
# RQ2 alloc + RQ3 통합 → fig6/7/8/9 생성
python3 experiments/code/local_analysis/rq3_figures.py \
  --rq3 experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_combined.parquet \
  --rq2 experiments/results/rq2_aware/2026_05_06_alloc/rq2_alloc.parquet \
  --random20 experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_random20.parquet
```

(`rq3_combined.parquet` 는 위 concat 결과 또는 wrapper 별 parquet 직접 multi-load.)

---

## 4. 시나리오 B 의 안전 조건 (메인 세션 사전 점검)

병렬 실행 전 확인:

| 점검 | 명령 | 안전 기준 |
|---|---|---|
| PG `max_connections` | `ssh capstone "psql -p 55436 wns41559 -c 'SHOW max_connections;'"` | ≥ 60 (peak ~42 connection 예상) |
| 서버 RAM 여유 | `ssh capstone "free -h"` | available ≥ 4GB (두 process 합 ~1.5GB + buffer) |
| 서버 코어 수 | `ssh capstone "nproc"` | ≥ 4 (두 process 측정 + 시스템) |
| caffeinate (맥북) | 로컬 `pgrep -lf caffeinate` | 살아있어야 ssh 끊김 방지 |

→ 위 4 항목 모두 통과면 시나리오 B 진행. 한 항목이라도 실패면 시나리오 A 로 fallback.

---

## 5. 측정 진행 중 모니터링

### 5.1 실시간 진행 확인

```bash
# 서버에 ssh 후 측정 process tail
ssh capstone "tail -f /tmp/rq3_deep.log"   # nohup 으로 띄웠을 때

# 또는 현재 실행 중 측정 process 확인
ssh capstone "ps aux | grep python3 | grep rq3"
```

### 5.2 중단 / 재개

각 wrapper 는 method 단위로 독립 산출 — 중간에 끊겨도 이미 완료된 method 의 parquet 은 그대로 보존. 다음 wrapper 부터 재시작하면 됨.

```bash
# 예: minibatch 까지는 끝났고 hilbert 부터 끊김 → hilbert 부터 재개
ssh capstone "cd ... && python3 rq3/run_hilbert.py --datasets DEEP ..."
```

### 5.3 PG memory leak 의심 시

5/6 발견된 `vector::real[]` cast 누수가 재발하면:
1. `fetch_all_vectors_safe` 자체에서 cluster 별 fresh conn 보장됨 → 안전
2. 만약 여전히 OOM 발생하면 `_measure_common.py` 의 `fetch_all_vectors_safe` 에 cluster 별 LIMIT 추가 (현재 cluster 전체 fetch)

---

## 6. wrapper 보완 (run_hilbert.py 작성 시 5분 가이드)

`run_random_projection.py` 를 base 로 method 호출만 교체:

```python
# run_random_projection.py 의 핵심 부분:
from offline_simple.random_projection import (  # noqa: E402
    assign_random_projection, cluster_size_summary, make_projection,
)
...
matrix = make_projection(dim=ds["vec_dim"], k=N_STRATA, seed=args.proj_seed)
stratum_ids = assign_random_projection(matrix, all_vecs)

# → 이걸 hilbert 로 교체:
from hilbert.hilbert_curve import (  # noqa: E402
    assign_hilbert, cluster_size_summary, fit_hilbert_mapper,
)
...
mapper = fit_hilbert_mapper(all_vecs, n_strata=N_STRATA, p=args.p, seed=args.fit_seed)
stratum_ids = assign_hilbert(mapper, all_vecs)

# extra_meta 갱신:
extra_meta={
    "method": "Hilbert Curve (E)",
    "p": args.p,        # default 10 (1024×1024 grid)
    "fit_seed": args.fit_seed,
    ...
},
```

→ ~10분 안에 `run_hilbert.py` 완성 가능.

---

## 7. 미해결 사항 (메인 세션 판단)

(가) **out-prefix 갈래 vs concat 처리**: 시나리오 B 시 DEEP/SIFT 별 parquet 갈라야 한다. wrapper 마다 `--out-prefix` 옵션 있으니 명시 가능. 단 `kde_pilot.py` / `distance_shell.py` / `online_weight/importance_sampling.py` 의 `--out-prefix` 옵션 존재 여부 확인 필요. 없으면 두 dataset 동시 실행 시 마지막 dataset 이 전 dataset 결과를 덮어쓸 위험.

→ 점검: `python3 rq3/kde/kde_pilot.py --help` 등으로 `--out-prefix` 지원 확인. 미지원 시 코드 1줄 추가 또는 시나리오 B 대신 시나리오 A 폴백.

(나) **`run_hilbert.py` 미작성 — W2 첫 작업으로**: 위 §6 가이드 따라 메인 세션이 직접 작성. 또는 다음 병렬 세션이 작성 후 commit.

(다) **fetch 캐시 (시나리오 D)**: 시간 추가 절감 가능하나 W2 후반 또는 W3 에서 검토. W1 sprint (~5/8) 에는 시나리오 B 로 충분.

(라) **분석 wrapper concat 자동화**: 위 §3.3 의 Python one-liner 를 `experiments/code/local_analysis/concat_rq3_results.py` 로 추출하면 메인 세션이 `python3 ... concat_rq3_results.py` 만으로 통합 parquet 생성 가능.

---

## 8. 시간 예산 (5/8 19:00 회의 + W2 마감 기준)

| 단계 | 시나리오 A | 시나리오 B | 비고 |
|---|---|---|---|
| RANDOM20 baseline | ~10분 | ~10분 (병렬 의미 X, 1회) | 두 dataset 한 번 실행 |
| 7-way 측정 | ~7h | ~3.5h | DEEP / SIFT 분리 |
| 분석 + figures | ~10분 | ~10분 | 단일 process |
| 회의 자료 통합 | ~30분 | ~30분 | 4단계 narrative 작성 |
| **총계** | **~8h** | **~4.5h** | **시나리오 B 시간 절감 ~3.5h** |

→ 5/8 19:00 회의까지는 충분. 단 메인 세션이 8M 마무리 후 새벽~오전에 진입 시 시나리오 B 권장 (잠 1번 자고 일어나면 다 끝나 있음).

---

## 9. 진입 절차 요약 (Mac mini ↔ 서버)

```bash
# 1. 핸드오프 + 보강 자료 읽기
cat _internal/RQ3_handoff_to_main_session.md
cat _internal/RQ3_handoff_병렬실행분석.md   # ← 본 문서

# 2. git pull + 서버 sync
git pull --no-rebase origin main
scp -r experiments/code/rq3 capstone:/mnt/hdd0/home/capstone2026/cache/

# 3. (선택) run_hilbert.py 보완 (~10분, §6 가이드)

# 4. 안전 조건 확인 (§4 의 4 항목)

# 5. RANDOM20 baseline 측정 (~10분)
ssh capstone "cd ... && python3 rq3/run_random20.py --include-bernoulli"

# 6. 7-way 병렬 측정 시작 (시나리오 B, 두 ssh terminal, ~3.5h)

# 7. 결과 회수 + 분석 (§3.3 + §3.4)

# 8. 4단계 narrative 작성 (§5 of RQ3_handoff_to_main_session.md 의 골격 활용)
```

---

**작성**: 조현빈 + Claude · 2026-05-06 18:18 KST · 병렬 세션
**연결**: `_internal/RQ3_handoff_to_main_session.md` (메인 진입 가이드) → 본 문서 (병렬 실행 분석)

---

## 10. 보강 (18:21 KST 시점) — 다른 병렬 세션의 결론과 비교

본 문서 작성 직후 (18:18 → 18:21) 다른 병렬 세션이 더 깊이 분석하여 다음 산출을 만들었다:

- `experiments/code/rq3/cache_vectors.py` — fetch 1회 + npy 디스크 캐시 (본 문서 §2.5 시나리오 D 의 인프라 완성)
- `_internal/handoff_P6_to_main_20260506_1820.md` — 메인 세션 P6 진입 핸드오프
- `_internal/RQ3_session_status_20260506_1815.md` — 병렬 세션 진행 상태 종합

**다른 세션 결론 (cache_vectors.py 의 docstring 인용)**:
> 병렬 vs 순차 분석 (5/6 18:14 KST):
> - **병렬 비추천**: PG `vector::real[]` cast 누수 (5/6 검증) + 동시 fetch 시 worker 경합
> - **순차 + cache 권장**: 안전성 + 디버깅 + 메인 세션 부담 최소

→ 본 문서 §2.3 의 시나리오 B (DEEP/SIFT 두 process 병렬) 는 PG `vector::real[]` cast 의 동시 fetch 위험을 충분히 고려하지 못한 분석이다. **5/6 검증된 누수 함정의 재발 위험을 감안하면 다른 세션의 결론 (시나리오 D, fetch 캐시 + method 순차) 이 더 안전한 권장이다**.

**메인 세션 진입 시 권장 절차 (수정)**:
1. (서버) `python3 rq3/cache_vectors.py` 1회 실행 (~12분, fetch + npy 디스크 캐시)
2. (서버) wrapper 들 순차 실행 (각 wrapper 가 cache 자동 load, fetch 없이 ~10초 + 측정 30분)
3. 총 시간 = 12분 + 8 method × 30분 = ~4h (시나리오 A 의 ~8h 대비 절반, 시나리오 B 와 거의 같음, 안전성 ↑)

**본 문서의 가치 (시나리오 D 권장 후에도)**:
- §2 의 시나리오 분석은 메인 세션이 시나리오 D 인프라 (cache_vectors.py) 가 어떤 trade-off 의 산물인지 이해하는 reference
- §6 의 `run_hilbert.py` 작성 가이드는 미완성 wrapper 보완 시 활용
- §4 의 안전 조건 점검 (PG max_connections / RAM / CPU / caffeinate) 은 시나리오 D 에서도 유효

→ **결론**: 시나리오 D (cache_vectors.py + 순차) 권장. 본 문서는 "왜 그게 권장인가" 의 비교 reference 로 보존.
