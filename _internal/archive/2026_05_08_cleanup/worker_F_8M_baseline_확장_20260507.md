# Worker F — DEEP 8M baseline 3개 측정 (KM20 + RANDOM20 + BERN)

> **임무**: 현재 DEEP 8M에 RQ3 19 method만 측정됨 (distribution-agnostic). KM20 oracle + RANDOM20 + BERN baseline 3개 추가 측정 → 8M 22 method 완성. cross-scale 검증 narrative 보강.
> **세션 진입**: 본 핸드오프 첫 read → 서버 측정 dispatch → 회수 → 분석 → commit.
> **manager 세션**: 2026-05-07 12:05 KST, Opus 4.7 1M.

---

## 1. 입력 자료

| 자료 | 위치 |
|---|---|
| 8M 측정 인프라 | `/mnt/hdd0/home/capstone2026/cache/rq3/run_8m_sensitivity.py` (서버) |
| 1M baseline run | `/mnt/hdd0/home/capstone2026/cache/rq3/run_km20.py` 등 (참조) |
| 8M 데이터셋 | `partsupp_deep_10_phase7_8m_subset` (10GB, PG) |
| 8M query selectivity | `/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_8m.parquet` |

## 2. 작업 단계

### Step 1 (15분) — 측정 plan 결정

**현재 8M 19 method**: birch / distance_shell / gmm / hdbscan / hilbert / hybrid / IS / kde_pilot / kdtree / lsh / minibatch / minibatch_partial / pca1d / pq / random_proj / sobol / sparse_rp / spectral / zorder

**추가 측정 3 baseline**:
1. **KM20** (oracle) — 8M K-means K=20, sample 비례 배분
2. **RANDOM20** — 무작위 K=20 분할
3. **BERN** — bernoulli (no clustering)

**측정 변수 (1M과 동일)**:
- selectivity: **2 sel** (0.10 / 0.30) — 1차로 1M cross-scale 일관 검증
- 또는 **5 sel** (0.01 / 0.05 / 0.10 / 0.30 / 0.50) — Worker G와 통합 시 전체 5단계
- seed: 5개
- query: 100개

**권장**: 2 sel (현재 8M 19 method와 동일) → 22 method 완성. 5 sel 확장은 Worker G 영역.

### Step 2 (1h) — 서버 measurement script 작성 + dispatch

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && cat > run_km20_8m.py << 'PYEOF'
# DEEP 8M KM20 baseline
# 패턴: run_km20.py (1M) 의 8M variant
# 8M K-means K=20 fit + per-stratum sample (proportional)
# selectivity 2 sel × 5 seed × 100 query
# 산출: /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_km20.parquet
[원본 코드는 _measure_common.py + run_minibatch.py 참조 작성]
PYEOF
"
```

또는 이미 측정 인프라가 일반화되어 있다면 (`run_8m_sensitivity.py` 의 method whitelist 추가):

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  python3 -u run_8m_sensitivity.py --methods km20,random20,bernoulli \
    --datasets DEEP_8M --sel 0.1,0.3 --seed 0,1,2,3,4 --queries 100 \
    > /tmp/8m_baseline_measure.log 2>&1 &"
```

(스크립트 검증 후 결정 — `_measure_common.py` 의 method registry 확장 가능 여부 점검)

### Step 3 (1h, 측정 진행 중 대기) — 진행 모니터링

```bash
ssh capstone "tail -f /tmp/8m_baseline_measure.log"
```

각 method ~15-30분 소요 (8M K-means fit이 1M보다 ~5-8배). 총 1-2h.

### Step 4 (15분) — 산출 회수

```bash
scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_{km20,random20,bernoulli}.parquet' \
    experiments/results/rq3_agnostic/
```

### Step 5 (30분) — 분석 driver 재실행

```bash
python3 experiments/code/local_analysis/recovery_rate.py
python3 experiments/code/local_analysis/rq3_8m_cross_scale.py  # 8M 22 method 갱신
python3 experiments/code/local_analysis/rq3_bootstrap_effect_size.py
```

### Step 6 (15분) — 결과 검증 + master.md 갱신 (옵션)

8M 22 method recovery rate 표 + cross-scale 1M↔8M 비교 표 갱신.

### Step 7 (15분) — commit + push

```bash
git add experiments/results/rq3_agnostic/rq3_8m_{km20,random20,bernoulli}.parquet \
        experiments/results/rq3_agnostic/recovery_summary.csv \
        experiments/results/rq3_agnostic/rq3_8m_cross_scale.csv
git commit -m "DEEP 8M baseline 3개 추가 (KM20 + RANDOM20 + BERN) — 22 method 완성"
git push
```

## 3. 산출 spec

| 산출 | 위치 | 기대 rows |
|---|---|---|
| `rq3_8m_km20.parquet` | `experiments/results/rq3_agnostic/` | 1,000 (2 sel × 5 seed × 100 q) |
| `rq3_8m_random20.parquet` | 동일 | 1,000 |
| `rq3_8m_bernoulli.parquet` | 동일 | 1,000 |
| recovery_summary.csv 갱신 | 동일 | 8M 22 method 추가 |
| rq3_8m_cross_scale.csv 갱신 | 동일 | 1M↔8M 22 method 비교 |

## 4. 검증 기준

- [ ] 3 parquet rows = 1,000 (NaN < 5%)
- [ ] recovery_summary.csv 의 8M 22 method 행 추가
- [ ] cross-scale 1M↔8M ranking 보존 (DEEP-KM20 8M effect ≈ 1M effect)

## 5. 의존성

- **Worker G (8M sel 5단계 확장)**: 의존성 없음, 병렬 가능. 단 같은 method를 다른 sel에서 측정 — sel별 분리 commit
- **5/8 회의 narrative**: 결과는 회의 후 master.md 보강 자료로 활용 (회의 자료 변경 X)

## 6. 예상 시간

총 **3-4h** (script 작성 30분 + dispatch + 측정 1-2h + 회수/분석 30분 + commit 15분). 측정 시간이 대부분이라 본 worker session 자체는 1-2h 직접 작업 + 측정 대기.

## 7. 본 worker가 만들지 말 것

- 1M 측정 재진행 (이미 22 method 완료)
- KM20 K!=20 (5/5 회의 합의 K=20 보존)
- master.md narrative 갱신 (manager session 책임 — Worker F는 commit message에 결과 명시)

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 12:05 KST
**기반**: 5/5 회의록 + 5/7 측정 검증 결과 (8M 19 method 완료, baseline 3개 빠짐)
