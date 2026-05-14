# 통합 manager session 인계 v3 — 5/7 14:33 KST

> **이전 session**: 2026-05-07 12:36 ~ 14:33 KST, Opus 4.7 1M. Context 한계 임박.
> **인계 목적**: SIFT 8M build chain debug + 옵션 1 (SIFT 1M) + Exqutor 비교 narrative + 분석 + master.md 갱신

---

## 1. 사용자 final 결정 (5/7 14:33)

### 목표
- **최고 정확도, 최고 산출물**
- **분명한 통제 변인 / 조작 변인 대조실험** (각 RQ × cell × 비교 정확)
- **Exqutor 본 논문과의 분명한 비교 + 개선 설명 + 엄밀성**

### 진행 옵션
- ✅ Option 1: SIFT 1M subset 추가 (정확 매칭 2×2)
- ⚠️ Option 2: 80M scale-up (Exqutor SF=100 비교) — 6/11 보고서 future work scope
- ⚠️ Option 4: toy_multi_join Worker H 멀티조인 검증 — 5/8 회의 후

---

## 2. 🚨 Critical Issue: SIFT 8M chain silent fail

### 진행 timeline 의심점
```
[14:25:09] STEP 1-4 START (BIGANN extract + PG COPY)
[14:29:58] STEP 1-4 END (rc=0) ✓ 8M rows 적재 PG verified
[14:29:58] STEP 5-6 START (KMeans + stratum_id + σ)
[14:30:00] STEP 5-6 END  ← 🚨 2s 만에 끝, KMeans 8M fit 불가
[14:30:00] STEP 7 START (query pool + d_target)
[14:30:00] STEP 7 END  ← 🚨 0s 만에 끝, 8M × 100q × 5sel 계산 불가
[14:30:00] STEP 8 RQ1 START (BERN+KM20)
[14:30:14] STEP 8 RQ1 END  ← 🚨 14s, 정상 측정 ~5분 필요
[14:30:14~14:34:46] STEP 11 RQ3 19 method  ← 각 ~20s, silent fail 의심
```

### 산출 검증
- ✅ `customer_sift_8m_subset` PG = 8,000,000 rows 적재 OK
- ❌ `customer_sift_8m_subset_vectors.npy` 미존재 (KMeans wrapper 출력)
- ❌ `query_pool_sift_8m.parquet` 미존재 (querypool wrapper 출력)
- ❌ `query_selectivity_sift_8m.parquet` 미존재
- ❌ `rq1_sift_8m_km20.parquet`, `rq2_alloc_SIFT_8M_5mode.parquet`, `rq3_8m_sift_*.parquet` 모두 미존재

### 디버깅 가설
1. **`sift_8m_kmeans_strata.py`**: psycopg server-side cursor (`cursor(name=...)`) issue + vector::real[] cast 실패 가능성
2. **`sift_8m_querypool.py`**: import 의존성 또는 file path 문제 (8M × 100q distance 4초 불가)
3. **`sift_8m_measure_chain.py`**: import-after-monkey-patch 시 `_measure_common.DATASETS` 가 wrapper module의 `DATASETS` 와 동일 binding 안 됨 (Python module-level constant import-time evaluation issue)
4. **distance_shell wrapper 부재**: `run_distance_shell.py` 가 없음 (1M base에서는 다른 이름) → import error log 유일하게 보였음
5. STEP 11 의 각 method 도 silent fail — _measure_common.run_method_measurement 가 8M PG fetch 시점에 query_pool 미존재로 fail 후 재시도 X

### 디버깅 priority (새 세션)
```
[1] sift_8m_kmeans_strata.py 직접 실행 + log 확인
    ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && python3 -u sift_8m_kmeans_strata.py 2>&1 | head -100"

[2] 성공 시 → sift_8m_querypool.py 직접 실행
    ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && python3 -u sift_8m_querypool.py 2>&1 | head -50"

[3] 성공 시 → sift_8m_measure_chain.py rq1_km20 실행 (각 stage 수동)
    ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u sift_8m_measure_chain.py rq1_km20 2>&1 | head -50"
```

---

## 3. 진행 중 chain 상태 (background, server)

| Process | PID | 상태 |
|---|---|---|
| `final_chain.sh` | 2488683 | PHASE B (silent fail 후 PHASE C 대기 중) |
| `sift_8m_chain.sh` | 2488705 | STEP 11 RQ3 method 실행 끝나는 중 |
| `missing_p_chain.sh` | 2493015 | sift_8m_chain_done.flag 대기 |
| `build_sift_8m.py` | 2488713 | 끝남 (PG 8M rows 적재 verified) |

**예상**: STEP 11 끝나면 sift_8m_chain_done.flag set → final_chain PHASE C (P3) → missing_p_chain (P1 KM50 8M + P2 OPQ 1M+8M) 진행. 단 산출 없음 (silent fail).

**모니터링**: `ssh capstone "test -f /tmp/sift_8m_chain_done.flag && test -f /tmp/missing_p_chain_done.flag"` — 둘 다 set 되면 chain 종료.

---

## 4. 작성된 wrappers 목록

### Server (PG-attached)
```
/mnt/hdd0/home/capstone2026/cache/
├── build_sift_8m.py                        (✓ 작동, PG 8M 적재)
├── sift_8m_kmeans_strata.py                (🚨 silent fail 의심)
├── sift_8m_querypool.py                    (🚨 silent fail 의심)
├── rq2_size_sensitivity_5mode_8m.py        (🚨 P3 fail — argparse 미지원)
├── rq2_size_5mode_full.py                  (P3 새 wrapper, dispatch 대기)
├── final_chain.sh                          (orchestrator)
├── sift_8m_chain.sh                        (SIFT 8M sequential)
├── missing_p_chain.sh                      (P1 KM50 8M + P2 OPQ 대기)
├── rq3/run_reservoir.py                    (P4 ✓)
├── rq3/run_km_k_sweep.py                   (P1 ✓)
├── rq3/run_opq.py                          (P2)
├── rq3/run_hilbert_dim.py                  (P5, B 옵션 skip)
├── rq3/run_8m_p_methods.py                 (P-method 8M dispatch)
├── rq3/run_km20_sift_5sel.py               (Gap #1 ✓)
├── rq3/run_km20_8m_sel_expand.py           (Gap #3 ✓)
├── rq3/sift_8m_measure_chain.py            (🚨 silent fail 의심)
└── rq3/p_methods_chain.sh                  (이미 진행 + kill됨)
```

### 완료된 commit (origin main)
- `74d6aea` ~ `79e86dc` (W2 종합)
- `79354b0` (W2 부록 — Gap fill 4건 + master.md 갱신)
- `f87b97c` (A1~A5 즉시 분석)

### 산출 inventory (검증)
```
✓ experiments/results/rq1_motivation/rq1_sift_km20_5sel.parquet (Gap #1, 5,000 cells)
✓ experiments/results/rq3_agnostic/rq3_8m_km20_sel_expand.parquet (Gap #3, 3,000 cells)
✓ experiments/results/rq3_agnostic/rq3_8m_paired_ci_cohen_d.csv (90 cells)
✓ experiments/results/rq3_agnostic/rq3_1m_paired_ci_cohen_d.csv (180 cells)
✓ experiments/results/rq3_agnostic/rq3_method_redundancy_{ari,nmi,ami}_8m.csv
✓ experiments/results/rq3_agnostic/rq3_8m_per_query_pivot.csv
✓ experiments/results/rq3_agnostic/rq3_8m_best_method_count_per_sel.csv
✓ experiments/results/rq3_agnostic/rq3_cross_scale_cohen_d.csv
✓ experiments/results/W2_sprint_부록_gap_fill_20260507.md
✓ _internal/팀원공유_RQ진행정리_구어체_20260507.pdf

🚨 미생성 (chain silent fail):
- rq1_sift_8m_km20.parquet
- rq2_alloc_SIFT_8M_5mode.parquet
- rq3_8m_sift_*.parquet (19 method)
- rq3_sift_8m_random20.parquet
- query_pool_sift_8m.parquet, query_selectivity_sift_8m.parquet

⏳ 대기 산출 (chain 진행 중, 산출 없을 가능성):
- rq3_km_k_50_8m.parquet (P1 KM50 8M)
- rq3_opq.parquet, rq3_8m_opq.parquet (P2)
- rq2_size_sensitivity_8m_5mode.parquet (P3)
- rq3_reservoir_8m.parquet (P4 8M)
```

---

## 5. Exqutor 본 논문 비교 framing (5/7 14:30 정리)

### Exqutor 실험 환경
- **데이터 규모**: TPC-H **SF=100 partsupp = 80M rows** (또는 TPC-DS SF=10 11억)
- **Vector datasets**: DEEP/SIFT/SimSearchNet++/YFCC/WIKI (5종)
- **인덱스**: HNSW (M=16, ef_construction=200, ef_search=400)
- **쿼리**: TPC-H 22개 중 Q3/Q5/Q8/Q9/Q10/Q11/Q12/Q20 + range search
- **시스템**: pgvector + VBASE + DuckDB

### 본 연구 위치
| | Exqutor | 본 연구 |
|---|---|---|
| Scale | SF=100 = 80M | **SF=10 = 8M (1M subset)** |
| Vector datasets | 5종 | **DEEP normal + SIFT skew (2종 contrast)** |
| 인덱스 환경 | HNSW + 비인덱스 | **비인덱스 (Adaptive Sampling 영역)** |
| 쿼리 | TPC-H 정식 + range | 100 random query × 5 sel × range |
| Contribution | ECQO + Adaptive Sampling | **단일 테이블 분포 인지 가치 (Exqutor 미커버)** |

### 정직 비교 narrative (5/27 발표 + 6/11 보고서)
1. 본 연구 = Exqutor 의 **complementary 보강** (단일 테이블 비인덱스 영역)
2. Scale 8M = Exqutor 의 가장 작은 SF=10 와 매칭. **80M scale-up 시 Exqutor SF=100 직접 비교** (future work)
3. Vector 2종 (DEEP+SIFT) = distribution contrast 충실. 5 dataset 평균 비교는 Exqutor 의 강점, distribution contrast 는 본 연구의 강점

### 추가 가용 dataset (서버 kgh1030)
- **yandex_deep base.1B.fbin** (DEEP 1B, 384GB) — DEEP 80M extract 가능
- **bigann base.1B.u8bin** (SIFT 1B, 128GB) — SIFT 80M extract 가능
- bigann learn.100M (12.8GB) — SIFT 8M extract (현재 진행 중) ✓
- yandex_deep learn.350M.fbin (134GB) — DEEP 100M까지 가능
- cohere/laion/msmarco — 다른 distribution
- **toy_multi_join (1M rows, PG 적재 완료)** — Worker H 멀티 조인 검증용 ready

---

## 6. 새 세션 진행 plan

### Phase A — 디버깅 (~30분)
1. `sift_8m_kmeans_strata.py` 직접 수동 실행 + 로그 분석
2. silent fail 원인 파악 (psycopg cursor / vector cast / module path)
3. wrapper fix → 재실행 → SIFT 8M dataset 완성

### Phase B — SIFT 8M 모든 측정 재실행 (~2-3h)
- KMeans → query pool → RQ1 → RQ2 → RQ3 21 method 순차
- 각 산출 verify (rows / NaN%)

### Phase C — Option 1 SIFT 1M subset 추가 (~30분)
- BIGANN learn.100M에서 1M extract → PG `customer_sift_1m_subset` 적재
- KMeans + querypool + 동일 측정
- → 2×2 (1M/8M × DEEP/SIFT) 정확 매칭 완성

### Phase D — Missing P-method 보강
- P1 KM50 8M (이미 chain 대기 중)
- P2 OPQ 1M+8M
- P3 RQ2 size 5-mode 8M (`rq2_size_5mode_full.py`)

### Phase E — 종합 분석 + master.md 갱신
- 4 dataset matrix (DEEP 1M / SIFT 1.5M / DEEP 8M / SIFT 8M / + SIFT 1M)
- 통제/조작 변인 명확화 표
- Exqutor 비교 framing (Q1 답변 통합)
- Limitations 8 → 9~10종 갱신 (Exqutor 직접 비교 가능 narrative)
- 종합 paired CI / Cohen's d / per-query / ARI 4 dataset

### Phase F — Final commit + push
- W2 부록 v2 doc (4 dataset 통합)
- master.md final
- 종합 보고서

---

## 7. 핵심 reference doc (새 세션 read 필수)

- `experiments/results/RQ1_RQ2_RQ3_종합_master.md` — 본 연구 master narrative
- `experiments/results/W2_sprint_8m_종합_20260507.md` — W2 sprint 8M 종합
- `experiments/results/W2_sprint_부록_gap_fill_20260507.md` — 5/7 부록 (Gap fill + paired CI)
- `reference/analysis/(02) Exqutor 통합요약.md` — Exqutor 본 논문 정리
- `reference/summaries/[0] Exqutor ... 총정리.md` — Exqutor 상세
- `_internal/worker_INDEX_v2_20260507.md` — 12 worker handoff history

---

## 8. 메모리 (자주 사용 명령)

### Chain 상태 확인
```bash
ssh capstone "test -f /tmp/sift_8m_chain_done.flag && echo 'sift done' || echo 'sift running'
test -f /tmp/missing_p_chain_done.flag && echo 'missing done' || echo 'missing running'
test -f /tmp/final_chain_done.flag && echo 'final done' || echo 'final running'"
```

### 산출 inventory
```bash
ssh capstone "ls -la /mnt/hdd0/home/capstone2026/cache/rq1/ | grep -iE 'sift_8m|sift_1m|km_k|opq|reservoir|size_sensitivity_8m_5mode'"
```

### PG SIFT 8M
```bash
ssh capstone "psql -h /tmp -p 55436 -d wns41559 -U wns41559 -tAc \"SELECT count(*) FROM customer_sift_8m_subset\""
```

---

**작성**: Claude (Opus 4.7 1M, 통합 manager session, 2026-05-07 14:33 KST)
**다음 manager session 진입 prompt**: 본 doc + master.md + Exqutor 통합요약 read → Phase A (디버깅) 부터 진행
