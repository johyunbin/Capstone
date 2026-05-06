# RQ3 Handoff — 메인 세션 다음 작업 가이드

> 8M 보강 측정 마치고 메인 세션이 RQ3 측정·분석으로 넘어갈 때 이 파일부터 읽으세요.
> 병렬 세션들이 미리 준비해둔 코드·템플릿·분석 도구 종합 안내.

---

## 0. 현 상황 (2026-05-06 18:08 KST 기준)

병렬 세션 prep 결과:
- ✅ RQ3 측정 코드 5개 작성·commit 완료: kde_pilot, distance_shell, importance_sampling, lsh, hilbert_curve
- ✅ Offline 측정 driver (run_*) 다른 병렬 세션이 작성 중 (untracked, 곧 commit 예상)
- ✅ 분석 라이브러리 (recovery_rate.py + rq3_figures.py + rq3_combine.py) 완성
- ✅ Narrative + 카톡 템플릿 (`_internal/RQ3_narrative_template.md`, `RQ3_카톡템플릿.md`) 완성

→ 메인 세션은 측정 실행 + 결과 회수 + 분석 실행 + 카톡 발송에 집중.

---

## 1. 진입 절차 (= 통합 + 이해 + 검증)

### 1.1 동기화

```bash
cd ~/Capstone
git pull --no-rebase origin main         # 병렬 세션 commit 모두 회수
git status                                # 미커밋 (있어도 괜찮음 — 측정 산출물)
```

### 1.2 통합 검증 — 7-way 코드 모두 존재?

```bash
# 측정 코드 7-way 점검
for d in offline_simple/run_minibatch.py offline_simple/run_random_projection.py \
         hilbert/hilbert_curve.py lsh/lsh.py kde/kde_pilot.py \
         online_weight/distance_shell.py importance_sampling/importance_sampling.py; do
  test -f "experiments/code/rq3/$d" && echo "✓ $d" || echo "✗ $d 없음"
done

# Hilbert/MiniBatch/RandProj 의 측정 driver 존재 여부 (파일명 가변):
ls experiments/code/rq3/{offline_simple,hilbert}/*.py
```

### 1.3 코드 흐름 이해 (각 method 1줄 요약)

| Method | 패러다임 | 핵심 알고리즘 | 측정 산출 (parquet) |
|---|---|---|---|
| **F. MiniBatch** | Offline 학습 | 1% sample → MiniBatchKMeans → assign → cache | `rq3_minibatch.parquet` |
| **C. Random Projection** | Offline 결정론 | Gaussian matrix (seed 고정) → argmax bucket | `rq3_random_projection.parquet` |
| **E. Hilbert** | Offline 결정론 | PCA 2D → Hilbert curve → quantile 분할 | `rq3_hilbert.parquet` |
| **A. LSH** | Offline 확률 | 5 random hyperplanes → sign hash → mod 20 | `rq3_lsh.parquet` |
| **B. KDE-pilot** | Online query-adaptive | KM strata + pilot σ̂ + Silverman/KDE + Neyman | `rq3_kde_pilot.parquet` |
| **G. Distance-Shell** | Online query-adaptive | pilot 거리 quantile 5-shell + Neyman | `rq3_distance_shell.parquet` |
| **H. Importance Sampling** | 비분할 가중치 | 2x2 factorial (hard/soft × sample/pilot) | `rq3_importance_sampling.parquet` |

모든 측정 코드는 동일 골격: cluster sample 캐시 → numpy 거리 계산 → HT estimator → bernoulli baseline 동시 측정.

### 1.4 환경

```bash
pgrep -lf caffeinate || nohup caffeinate -dimsu >/dev/null 2>&1 & disown
ssh capstone "pgrep -lf python3"     # 서버에 잔존 측정 process 없는지
```

---

## 2. 서버 병렬 가능성 분석 + 권장 실행 전략

### 2.1 결론

**부분 병렬 가능** — method 를 cache pattern 따라 2 그룹으로 나눠 처리.

| Group | Method | Cache 방식 | 동시 실행 | 비고 |
|---|---|---|---|---|
| **G1 — KM-strata Online** | KDE-pilot, Distance-Shell, Importance Sampling | KM20 stratum_id 의 `LIMIT 500/cluster` 동일 (3 method 가 같은 cache 공유 가능) | **3 process 동시 안전** | 각 method 별 fresh conn 20개 × 3 = 60 short-lived conn (PG OK) |
| **G2 — Custom-bucketing Offline** | LSH, MiniBatch, RandProj, Hilbert | full 1M chunk-scan + 자체 bucket 부여 + reservoir cache | **순차 권장** (병렬 시 PG OOM 위험) | 각 method 가 ~20 long-lived conn × 50K chunk → 동시 4개면 80 conn 부담 |

### 2.2 안전 근거

서버 함정 메모 (5/6 vector.c 패치 시도 결과) 기준:
- **PG vector::real[] cast 누적 leak**: 단일 conn 의 LIMIT 500 까지 OK, 다수 conn 동시면 누수 합산. G1 처럼 짧은 conn (cluster sample 한 번 → close) 은 안전, G2 의 chunk-scan 은 긴 conn 다수 → 동시 X.
- **vector_stratum_sigma 테이블**: KDE-pilot 만 read-only 참조, RQ2 가 이미 INSERT 완료. 동시 read 안전.
- **CPU/RAM**: G1 3 process × 500MB = 1.5GB. G2 1 process = 1GB. 서버 capstone2026 여유.
- **Python GIL 무관**: 각 process 는 별도 PID, numpy 거리 계산은 BLAS 멀티스레드 (process 마다 thread cap 권장).

### 2.3 실행 전략 (3가지 옵션)

**옵션 A — 안전 우선 (순차)** ★ 처음 권장
- G2 4개 + G1 3개 모두 직렬, 우선순위 (#8 → #5 → #7 → #6 → #10 → #9 → #11) 순서 그대로
- 총 ~25-30분 (각 ~3-5분)
- 위험 0, 디버그 쉬움, 측정 결과 q_error 변동성 최소

**옵션 B — 스마트 병렬 (권장 균형)**
1. G2 sequential 시작: LSH → (LSH 끝나면) MiniBatch → ... 순차
2. G2 첫 method (LSH) 끝나면 G1 3개 동시 실행:
   ```bash
   ssh capstone "cd cache/rq3 && python3 -u kde/kde_pilot.py > /tmp/kde.log 2>&1 &
                                  python3 -u online_weight/distance_shell.py > /tmp/ds.log 2>&1 &
                                  python3 -u importance_sampling/importance_sampling.py > /tmp/is.log 2>&1 &
                                  wait"
   ```
3. G2 의 나머지 3개 (MiniBatch/RandProj/Hilbert) 는 G1 종료 기다리지 않고 순차 진행
4. 총 ~15-20분 (G1 6분 + G2 19분 중 overlap 효과)

**옵션 C — 풀 병렬** ✗ 비권장
- 7개 동시 실행 → PG conn 100+ 동시, leak 가속, q_error 측정 변동성 증가, 디버그 어려움

### 2.4 권장 흐름 (옵션 B 기준 구체)

```bash
# t=0: 카톡 §3.1 발송 (LSH 부터)
# t=0: ssh capstone, cd cache/rq3
# t=0~5min: LSH 측정 (chunk-scan ~3분 + 측정 ~2분)
ssh capstone "cd cache/rq3 && python3 -u lsh/lsh.py > /tmp/lsh.log 2>&1"
scp capstone:/mnt/hdd0/.../rq1/rq3_lsh.parquet experiments/results/rq3_agnostic/$(date +%Y_%m_%d)/

# t=5min: G1 3개 동시 시작 (background)
ssh capstone "cd cache/rq3 && nohup python3 -u kde/kde_pilot.py > /tmp/kde.log 2>&1 & \
                              nohup python3 -u online_weight/distance_shell.py > /tmp/ds.log 2>&1 & \
                              nohup python3 -u importance_sampling/importance_sampling.py > /tmp/is.log 2>&1 & \
                              wait"
# t=11min: G1 끝 (~6min). 회수
scp capstone:.../rq3_{kde_pilot,distance_shell,importance_sampling}.parquet experiments/results/.../

# t=11min~16min: MiniBatch (training 5초 + chunk-scan 3분 + 측정 1분)
ssh capstone "cd cache/rq3 && python3 -u offline_simple/run_minibatch.py"
scp ...

# t=16~19min: RandProj (~3분, training X)
ssh capstone "cd cache/rq3 && python3 -u offline_simple/run_random_projection.py"
scp ...

# t=19~25min: Hilbert (PCA 5% sample + chunk-scan + 측정)
ssh capstone "cd cache/rq3 && python3 -u hilbert/<driver>.py"
scp ...

# t=25min: 모든 method 완료 → 통합 분석 (§3)
```

> **MiniBatch/RandProj/Hilbert driver 파일명**: 다른 병렬 세션이 작성 중인 `_measure_common.py` + `run_*.py` 패턴이 commit 되면 위치 확정. 미commit 상태라면 `git pull` 후 `experiments/code/rq3/` 직하 또는 method 폴더 안 확인.

---

## 2.5 측정 우선순위 + 코드 위치 (참조 표)

| 순위 | # | Method | Group | 코드 | 단독 예상 |
|---|---|---|---|---|---|
| 1 | #8 | F. MiniBatch K-means | G2 | `rq3/offline_simple/run_minibatch.py` | ~5min |
| 2 | #5 | C. Random Projection | G2 | `rq3/offline_simple/run_random_projection.py` | ~3min |
| 3 | #7 | E. Hilbert Curve | G2 | `rq3/hilbert/` driver | ~6min |
| 4 | #6 | A. LSH | G2 | `rq3/lsh/lsh.py` | ~5min |
| 5 | #10 | B. KDE-pilot | G1 | `rq3/kde/kde_pilot.py` ✅ standalone | ~6min |
| 6 | #9 | G. Distance-Shell | G1 | `rq3/online_weight/distance_shell.py` ✅ standalone | ~4min |
| 7 | #11 | H. Importance Sampling | G1 | `rq3/importance_sampling/importance_sampling.py` ✅ standalone | ~6min |

> 단독 예상 시간은 next_session_prompt.md 의 "시간" 칼럼 (~1h~6h) 보다 짧음 — 그것은 *신규 작성* + *측정* + *분석* 합산이고, 코드 작성이 끝난 지금은 *측정 only* 만 남음 (~3-6분/method).

**측정 패턴 (각 method 마다 동일 6단계)**

```bash
# 0. 카톡 §3.1 발송 (_internal/RQ3_카톡템플릿.md 의 §§X-1 복사)

# 1. 코드 서버 전송
scp -r experiments/code/rq3/ capstone:/mnt/hdd0/home/capstone2026/cache/

# 2. 서버 측정 실행 (예: F. MiniBatch)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && python3 -u offline_simple/run_minibatch.py"
# 또는 nohup + tail -f log

# 3. parquet 회수
scp capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_minibatch.parquet \
    experiments/results/rq3_agnostic/$(date +%Y_%m_%d)/

# 4. 분석 (모든 method 끝났거나 중간 점검)
python3 experiments/code/local_analysis/rq3_combine.py

# 5. narrative md 채우기 (_internal/RQ3_narrative_template.md 의 placeholder)

# 6. 카톡 §3.2 발송 + git commit + push
```

---

## 3. 통합 분석 흐름 (모든 method 측정 끝난 후)

```bash
# 1. 모든 parquet → combined long-form + summary CSV
python3 experiments/code/local_analysis/rq3_combine.py
# → experiments/results/rq3_agnostic/<YYYY_MM_DD>/
#    ├─ rq3_combined.parquet
#    ├─ rq3_summary.csv
#    ├─ rq3_pairwise.csv
#    ├─ rq3_ranking.csv
#    └─ rq3_combine_meta.json

# 2. Figures 생성 (fig6~9)
python3 experiments/code/local_analysis/rq3_figures.py \
    --rq3 experiments/results/rq3_agnostic/<YYYY_MM_DD>/rq3_combined.parquet
# → experiments/figures/rq3_distribution_agnostic/fig6~9.png

# 3. Narrative md 갱신
# _internal/RQ3_narrative_template.md 의 7-way placeholder 채워서
# experiments/results/RQ3 실험 결과 정리.md 로 복사·편집

# 4. 종합 카톡 (_internal/RQ3_카톡템플릿.md 의 ⭐ 종합 보고)
```

---

## 4. 함정 회피 (이번 세션에서 발견된 4가지)

### 4.1 vector.c 패치 X — Python 시뮬레이션 사용 ★

5/6 vector.c Neyman/Anti-Neyman 패치 시도 시 PG memory leak. RQ3 도 Python 시뮬레이션 (cluster sample 캐시 + numpy 거리 계산) 으로 우회 — 모든 측정 코드가 이 패턴.

### 4.2 PG vector::real[] cast 누적 leak

LIMIT 500 까지 단일 conn OK, 그 이상 unstable. **cluster 마다 fresh connection** 패턴 (`with psycopg.connect(...) as c:`) 모든 코드에 적용 완료.

### 4.3 휴면 방지

새 세션 시작 시:
```bash
pgrep -lf caffeinate || nohup caffeinate -dimsu >/dev/null 2>&1 & disown
```

### 4.4 데이터 위치 (서버)

```
DEEP query pool:  /mnt/hdd0/home/capstone2026/cache/rq1/query_pool.parquet
                  /mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity.parquet
SIFT query pool:  /mnt/hdd0/home/capstone2026/cache/rq1/query_pool_sift.parquet
                  /mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_sift_v2.parquet

DEEP table:  partsupp_deep_10_subset_1m  (stratum_id smallint, indexed) — 1M rows
SIFT table:  customer_sift_10_phase7_noidx_subset (stratum_id smallint, indexed) — 1M rows
```

---

## 5. 마감 카운트다운 (참고)

| 마감 | 산출물 | D-day |
|------|--------|-------|
| 5/8 (금) 19:00 | RQ1+RQ2+RQ3 실험 마감 + 비대면 회의 | D-2 |
| ~5/15 | 자문 요청 발송 (채림 + 교수님) | D-9 |
| ~5/21 | 발표자료 초안 마감 | D-15 |
| 5/22 | 교수님 미팅 | D-16 |
| 5/26 | 발표자료 최종 마감 | D-20 |
| **5/27** | **최종 발표** | **D-21** |
| 6/11 | 최종 보고서 | D-36 |

---

## 6. Quick Reference — 분석 파일 경로

| 파일 | 용도 |
|---|---|
| `experiments/code/local_analysis/recovery_rate.py` | 분석 라이브러리 (recovery_rate, paired_wilcoxon_with_bh_fdr, summarize_method) |
| `experiments/code/local_analysis/rq3_combine.py` | 7-way parquet 통합 + summary CSV 생성 |
| `experiments/code/local_analysis/rq3_figures.py` | fig6/7/8/9 PNG 생성 |
| `_internal/RQ3_narrative_template.md` | 7-way 4단계 narrative 채움 폼 |
| `_internal/RQ3_카톡템플릿.md` | §3.1 + §3.2 메시지 템플릿 14장 |
| `_internal/next_session_prompt.md` | 다음 세션 진입점 |

---

**작성**: 병렬 세션 (조현빈) · 2026-05-06 18:10 KST
**다음**: 메인 세션이 8M 측정 마치고 본 파일 → §1 진입 절차 → §2 측정 진행
