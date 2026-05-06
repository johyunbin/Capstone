# RQ3 Orchestration Plan — 메인 세션 진입점

> **메인 세션이 8M 보강 측정 끝낸 직후 가장 먼저 읽을 문서.**
> 여러 병렬 세션이 만든 RQ3 wrapper / module 통합 매핑 + 서버 자원 분석 +
> 병렬/순차 실행 전략.
>
> 작성: 2026-05-06 18:1x KST · 병렬 세션이 P3~P8 인벤토리 종합

---

## ★ TL;DR (60초 안에 파악)

- **8M 보강 측정 끝 → `git pull` → §3 명령어 sheet 따라 진입**.
- **권장 = 순차 실행 (~17h)**. 5/8 19:00 마감까지 ~50h 가용이라 안정성 우선.
- **선택적 병렬**: 메모리 OK 면 Online (G/B/H) 3 process 동시 가능 → ~10h 단축.
- 핵심 wrapper: `measure_offline.py` (6 mode 통합) + `run_lsh.py` + Online 3개 self-contained.

---

## 1. 인벤토리 — 8 method × wrapper × module

| # | Method | Paradigm | Wrapper | Module | 예상 시간 | 비고 |
|---|---|---|---|---|---|---|
| - | bernoulli | baseline | `measure_offline.py` | (내장) | (포함) | RQ2 와 동일 baseline |
| - | random20 | baseline | `measure_offline.py` | (내장) | (포함) | recovery 분모 |
| - | km20 | baseline | `measure_offline.py` | (내장) | (포함) | DB stratum_id + equal alloc, recovery 분자 |
| #5 | C. Random Projection | offline | `measure_offline.py` | `offline_simple/random_projection.py` | (포함) | JL, argmax, 결정론 |
| #7 | E. Hilbert Curve | offline | `measure_offline.py` | `hilbert/hilbert_curve.py` | (포함) | PCA 2D + 2^p grid |
| #8 | F. MiniBatch K-means | offline | `measure_offline.py` | `offline_simple/minibatch_kmeans.py` | (포함) | sklearn, 1% 학습 |
| #6 | A. LSH | offline | **`run_lsh.py`** | `lsh/lsh.py` | ~1h | hyperplane sign hash |
| #9 | G. Distance-Shell | online | **`online_weight/distance_shell.py`** (self) | (자체 main) | ~4h | pilot + 5 shell + Neyman |
| #10 | B. KDE-pilot | online | **`kde/kde_pilot.py`** (self) | (자체 main) | ~6h | Silverman + Neyman |
| #11 | H. Importance Sampling | weight | **`online_weight/importance_sampling.py`** (self) | (자체 main) | ~6h | f/g 가중치, 2x2 factorial |

**`measure_offline.py` 한 방에 6 mode 통합 측정** (~20~30분, DEEP+SIFT). 가장 효율적 진입점.

### 1.1 deprecate / reference 만 (P3 산출, 통합 wrapper 와 중복)

| 파일 | 상태 | 사유 |
|---|---|---|
| `experiments/code/rq3/run_minibatch.py` | ⚠️ deprecate | `measure_offline.py` 의 `--modes minibatch` 와 중복 |
| `experiments/code/rq3/run_random_projection.py` | ⚠️ deprecate | 위와 동일 (`--modes random_proj`) |
| `experiments/code/rq3/run_random20.py` | ⚠️ deprecate | 위와 동일 (`--modes random20`) |
| `experiments/code/rq3/_measure_common.py` | ⚠️ deprecate | `measure_offline.py` 가 자체 측정 함수 포함 |

→ 개별 디버깅 시 reference. 통합 측정은 `measure_offline.py` 권장.

> **이유**: P3 (`_measure_common.py` + 개별 wrapper) 는 전체 row fetch (1M~1.5M, ~5분/dataset) 후 in-memory stratum_id. P5+ (`measure_offline.py`) 는 KM cluster 별 LIMIT 500 cache (~10s/dataset) 후 cache 위에서 stratum_id 부여. 측정 결과 일관 가능 (cache 가 sufficient sample). 후자가 ~10배 빠름.

---

## 2. 의존성 그래프

```
PG vector module (port 55436)
        │
        ▼
  fetch (cluster LIMIT 500 fresh conn)
        │
        ▼
  cache_cluster_samples({0..19}: ndarray)
        │
        ├─ KM stratum_id (DB column)        → km20 baseline
        ├─ rng.integers(0,20)                → random20 baseline
        ├─ MiniBatchKMeans.fit().predict()  → minibatch (#8)
        ├─ matrix @ vec → argmax            → random_proj (#5)
        ├─ PCA 2D + Hilbert curve           → hilbert (#7)
        ├─ k hyperplanes sign hash          → lsh (#6, run_lsh.py)
        ├─ pilot D-quantile shell           → distance_shell (#9)
        ├─ KDE Silverman bandwidth + Neyman → kde_pilot (#10)
        └─ f/g importance weight            → importance (#11)
        │
        ▼
  HT estimator: Σ hits_i × (N_i / s_i)
        │
        ▼
  q_error = max(est/true, true/est)
        │
        ▼
  parquet (mode/sel/seed/qid/q_error) + meta json
```

---

## 3. 실행 sheet — Phase 별 명령어

> 모든 명령어는 메인 세션이 서버 (`165.132.140.240`) 에서 실행. 각 Phase 시작 시 톡방 §3.1 / 끝에 §3.2 발송 권장.

### Phase 0 — 진입 (5분)

```bash
# 메인 세션 (mac 로컬)
cd ~/Capstone
git pull --no-rebase origin main          # 병렬 세션 산출 통합

# 서버 동기화 (rq3 디렉토리 통째로)
scp -r experiments/code/rq3 capstone:/mnt/hdd0/home/capstone2026/cache/

# sklearn 확인 (MiniBatch 의존)
ssh capstone "python3 -c 'import sklearn; print(sklearn.__version__)'"
# → 없으면 ssh capstone "pip install --user scikit-learn" (~30s)
```

### Phase 1 — Offline 6 mode 통합 (~30분)

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u measure_offline.py 2>&1 | tee rq3_offline.log"
# 산출: rq1/rq3_offline.parquet (60,000 rows = 6 mode × 2 ds × 5 sel × 5 seed × 100 q)
#       rq1/rq3_offline_meta.json
```

→ **이 단계만으로 random20/km20/bernoulli + 3 method (RandProj/MiniBatch/Hilbert) 모두 측정 완료**.

### Phase 2 — LSH (~1h)

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u run_lsh.py 2>&1 | tee rq3_lsh.log"
# 산출: rq1/rq3_lsh.parquet
```

### Phase 3 — Online 3 method (~16h 순차 / ~6h 병렬)

**옵션 A — 순차 (안정 우선, ~16h)**:

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u online_weight/distance_shell.py 2>&1 | tee rq3_distance_shell.log"   # ~4h
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u kde/kde_pilot.py 2>&1 | tee rq3_kde_pilot.log"                       # ~6h
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u online_weight/importance_sampling.py 2>&1 | tee rq3_importance.log"  # ~6h
```

**옵션 B — 병렬 (시간 우선, ~6h)** — 메모리 OK 시:

```bash
# 3 process 동시 (각각 fresh conn → PG conn 충돌 X, 메모리 ~수십 MB/process)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && nohup python3 -u online_weight/distance_shell.py > rq3_ds.log 2>&1 &"
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && nohup python3 -u kde/kde_pilot.py > rq3_kde.log 2>&1 &"
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && nohup python3 -u online_weight/importance_sampling.py > rq3_is.log 2>&1 &"
ssh capstone "ps -ef | grep python3 | grep -v grep"   # 3 process 확인
```

### Phase 4 — 결과 회수 + 분석 (~30분)

```bash
# 산출물 회수
mkdir -p experiments/results/rq3_agnostic/2026_05_07_first_runs
scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_*.parquet' \
    'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_*_meta.json' \
    experiments/results/rq3_agnostic/2026_05_07_first_runs/

# concat + km20 alias 정리
python3 - <<'PY'
import pandas as pd
from pathlib import Path
d = Path("experiments/results/rq3_agnostic/2026_05_07_first_runs")
parts = []
for pq in d.glob("rq3_*.parquet"):
    df = pd.read_parquet(pq)
    keep = ["dataset", "mode", "selectivity", "seed", "query_id", "D_target",
            "true_card", "est", "q_error"]
    parts.append(df[[c for c in keep if c in df.columns]])
combined = pd.concat(parts, ignore_index=True).drop_duplicates(
    subset=["dataset", "mode", "selectivity", "seed", "query_id"]
)
combined.to_parquet(d / "rq3_combined.parquet", index=False)
print(f"combined {len(combined):,} rows; modes={sorted(combined['mode'].unique())}")
PY

# figures 갱신
python3 experiments/code/local_analysis/rq3_figures.py \
    --rq3 experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_combined.parquet
# fig6/7/8/9 갱신 → experiments/figures/rq3_distribution_agnostic/
```

---

## 4. 병렬 vs 순차 결정 매트릭스

| 단계 | 순차 시간 | 병렬 가능? | 사유 |
|---|---|---|---|
| Phase 1 (offline 6 mode) | 30분 | N/A (이미 통합) | 한 process 안에서 6 mode 순차 |
| Phase 2 (LSH) | 1h | Phase 1 과 동시 가능 | fetch 패턴 동일, fresh conn 안전 |
| Phase 3-A (Distance-Shell) | 4h | Phase 3 안 동시 가능 | online-only, fetch 후 in-memory |
| Phase 3-B (KDE-pilot) | 6h | 〃 | 〃 |
| Phase 3-C (Importance) | 6h | 〃 | 〃 |

**병렬 안전 영역**:
- ✅ 모든 wrapper 가 cluster 별 fresh conn (vector cast leak 회피, 5/6 검증)
- ✅ out-prefix 다르면 parquet 파일 충돌 X
- ✅ 메모리 부담 작음 (cache 10K rows × float32 = ~수 MB per process)

**병렬 위험 영역**:
- ⚠️ vector cast leak 동시 실행 시 가속화 가능 (5/6 사례, 단 단일 query 위주에서만 검증)
- ⚠️ CPU contention → 측정 변동성 증가 (q_error 노이즈)
- ⚠️ 동시 OOM 시 모든 측정 손실

**최종 추천**:
1. **Phase 1 + Phase 2 병렬** (~1h, 안전): `measure_offline.py` 와 `run_lsh.py` 동시 실행. 가벼움.
2. **Phase 3 순차** (~16h, 안정): Online 3 wrapper 순차. 가장 시간 큰 부분이라 안정성 우선.

총 ~17h. D-2 (5/8 19:00) 까지 ~50h 가용 → 33h 여유.

**시간 부족 시 (D-1 늦은 시점)**: Phase 3 도 병렬 (3 process 동시) → ~7h. 단 측정 변동 risk.

---

## 5. 트러블슈팅

| 증상 | 원인 추정 | 대응 |
|---|---|---|
| `invalid memory alloc request` | vector::real[] cast leak | wrapper 재실행 (이미 fresh conn 패턴), 안 풀리면 PG restart |
| `OOM` | 동시 process 메모리 합 초과 | 동시 process 줄이기, cache_per_cluster 작게 (300 → 200) |
| `module not found: sklearn` | Phase 0 의 sklearn 미설치 | `pip install --user scikit-learn` |
| `q_error 100+` 이상치 | est=0 (cache hit 0) → 1/0 | true_card=0 검증, 정상 (q_error filter) |
| `recovery_rate NaN` | KM20 ≈ RANDOM20 (분모 붕괴) | recovery_rate.py 의 fall-back (방법X−BERN%) 자동 적용 |
| `figures fb=N` 표기 | 분모 붕괴 셀 수 | 정상, fall-back metric 별도 보고 |

---

## 6. 카톡 진행 메시지 — Phase 별

§3.1 시작 / §3.2 완료 메시지는 `_internal/RQ3_handoff_to_main_session.md §1~§5` 참조. 각 Phase 시작/끝 시 발송.

추가로 **Phase 0 진입 메시지 (메인 세션 진입 직후)**:

```
[RQ3 측정 시작 준비] HH:MM

8M 보강 측정 마무리 완료 → RQ3 7-way (8 mode) 측정 진입.

병렬 세션이 만든 wrapper 통합 확인:
- Offline 6 mode (bernoulli/random20/km20/MiniBatch/RandProj/Hilbert): measure_offline.py
- LSH: run_lsh.py
- Distance-Shell / KDE-pilot / Importance: 각 self-contained

순서:
1. Phase 1 — measure_offline.py (~30분) + Phase 2 — run_lsh.py (~1h, 동시 실행)
2. Phase 3 — Online 3 wrapper (순차, ~16h)
3. Phase 4 — 분석 + figures 갱신 (~30분)

총 ~18h. 5/8 19:00 마감까지 여유 ~30h.
```

---

## 7. 검증 체크리스트 (Phase 4 분석 직전)

- [ ] `rq3_offline.parquet` 60,000 rows (6 × 2 × 5 × 5 × 100)
- [ ] `rq3_lsh.parquet` 10,000 rows (1 × 2 × 5 × 5 × 100)
- [ ] `rq3_distance_shell.parquet` 10,000 rows
- [ ] `rq3_kde_pilot.parquet` 10,000 rows
- [ ] `rq3_importance.parquet` 40,000 rows (4 × 2 × 5 × 5 × 100, H의 2x2 factorial)
- [ ] concat 후 unique mode 9개 (bernoulli/random20/km20/minibatch/random_proj/hilbert/lsh/distance_shell/kde_pilot + importance variants)
- [ ] recovery_rate.py self-test 통과 (`python3 recovery_rate.py`)
- [ ] fig6/7/8/9 정상 생성 (PNG 4개 ≥ 100KB)

---

## 8. 산출물 git 정리 (Phase 4 끝)

```bash
git add experiments/results/rq3_agnostic/2026_05_07_first_runs/
git add experiments/figures/rq3_distribution_agnostic/
git commit -m "RQ3 7-way 측정 완료: $(date '+%Y-%m-%d %H:%M') KST 진입 → ${ELAPSED}h 소요. fig6~9 갱신"
git push origin main
```

각 wrapper 별 narrative md (`실험N_결과정리_20260507.md`) 는 measurement 끝난 후 Claude 가 채움.

---

**작성**: 조현빈 + Claude · 2026-05-06 18:1x KST · 병렬 세션
**Hand-off 흐름**: 메인 세션 8M 측정 마무리 → `git pull` → 본 문서 §3 sheet 진입.
**다음 단계 트리거**: 본 문서 + handoff doc + RQ재정립 §RQ3 셋트 모두 메인 세션 컨텍스트로 로드.
