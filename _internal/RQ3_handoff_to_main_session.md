# RQ3 handoff — 메인 세션 진입 가이드

> **이 문서는 8M 보강 측정 마무리 직후 메인 세션이 곧바로 RQ3 측정에 진입하기 위한 부품 모음.**
> 작성: 병렬 세션 (2026-05-06 17:5x KST), 작성자: 조현빈 + Claude
> 실험 우선순위: `_internal/next_session_prompt.md §2.2` 참조 — F (#8) > C (#5) > E (#7) > A (#6) > B (#10) > G (#9) > H (#11)

---

## 0. 메인 세션 진입 체크리스트

```bash
# 1. 8M 보강 측정 완료 확인 (다른 세션) → commit + push 끝났는지
cd ~/Capstone
git pull --no-rebase origin main         # 병렬 세션 산출 (recovery_rate.py + RQ3 wrappers) 받음

# 2. 서버 동기화 — RQ3 wrapper 디렉토리 통째로 scp
scp -r experiments/code/rq3 capstone:/mnt/hdd0/home/capstone2026/cache/

# 3. 서버에서 sklearn 확인 (MiniBatch 의존)
ssh capstone "python3 -c 'import sklearn; print(sklearn.__version__)'"
# → 없으면 pip install --user scikit-learn (~30초)

# 4. RANDOM20 baseline 측정 (~10분, recovery 분모 필수, 1번만)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && python3 rq3/run_random20.py --include-bernoulli"

# 5. 실험 #8 — F. MiniBatch K-means (~1h, 1순위)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && python3 rq3/run_minibatch.py"

# 6. 실험 #5 — C. Random Projection (~30분, 2순위)
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache && python3 rq3/run_random_projection.py"

# 7. 결과 회수
mkdir -p experiments/results/rq3_agnostic/2026_05_07_first_runs
scp capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_*.parquet \
    capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_*_meta.json \
    experiments/results/rq3_agnostic/2026_05_07_first_runs/

# 8. 분석 — recovery_rate + figures (fig6/7/8/9) 갱신
python3 experiments/code/local_analysis/rq3_figures.py \
    --rq3 experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_minibatch.parquet \
    --rq2 experiments/results/rq2_aware/2026_05_06_alloc/rq2_alloc.parquet \
    --random20 experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_random20.parquet
# (실 데이터는 concat 도 가능 — 여러 --rq3 인자 미지원 시 사전에 pandas concat)
```

---

## 1. 카톡 §3.1 — 실험 #8 시작 메시지 (즉시 발송 가능)

```
[RQ3 #8 시작] HH:MM

실험명: F. MiniBatch K-means (Offline Partition, ~1% 학습)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~1h (DEEP fetch 5m + SIFT fetch 7m + 학습 30s × 2 + 측정 30m)

[기획 의도]
- 박세은 비판 ("사전 계산 비용") 에 대한 직접 답.
- KM20 (전체 데이터 전수 학습) 의 oracle 에 가장 근접 가능한 distribution-agnostic 방법.
- "데이터 1~5% 만 보고도 KM20 에 가까운 효과를 낼 수 있는가?" 의 답.

[측정 목표 + 가설]
- H3-F: recovery_rate 75~95% (MiniBatch 가 KM20 oracle 의 75% 이상 회수)
- 정량: KM20-equal 대비 개선폭 차이 ≤ 25% 안에 들어가는가?
- 사전: 1% 학습 fraction, sklearn MiniBatchKMeans 한 줄

[기대치]
- DEEP 1M: recovery 80% 내외 (cluster 구조 명확, sample 학습 OK)
- SIFT 1.5M: recovery 75% 내외 (skew 있어 학습 분산 큼)

[측정 조건]
- DEEP/SIFT 2 dataset, 5 sel (0.01/0.05/0.1/0.3/0.5) × 5 seed × 100 query
- sample_size 385 고정, equal allocation
- learn_frac 0.01 (1%, ~10K~15K rows)

진행 후 결과 다시 공유드리겠습니다 🙏
```

---

## 2. 카톡 §3.1 — 실험 #5 시작 메시지

```
[RQ3 #5 시작] HH:MM

실험명: C. Random Projection (Offline, 학습 X)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~30분

[기획 의도]
- 7-way 의 "단순 하한" baseline.
- Johnson-Lindenstrauss lemma — 거리 보존만 보장, cluster 구조 X.
- "최단순 방법도 RANDOM20 보다는 낫다" 정도 입증되면 충분.

[측정 목표 + 가설]
- H3-C: recovery_rate 10~40% (단순 하한, RANDOM20 < C ≤ KM20 예상)
- 정량: argmax bucket 부여로도 RANDOM20 대비 양의 개선 발생하는가?

[기대치]
- DEEP/SIFT 모두 recovery 0.2~0.4 (낮은 효과 예상)
- argmax bucket 사이즈 매우 unbalanced (한 dim 으로 쏠림 자연스러움)

[측정 조건]
- 실험 #8 과 동일

진행 후 결과 다시 공유드리겠습니다 🙏
```

---

## 3. 카톡 §3.1 — RANDOM20 baseline (recovery 분모) 측정

```
[RQ3 baseline 측정] HH:MM

실험명: RANDOM20 baseline (recovery_rate 분모)
RQ: RQ3 (분포 모를 때 어떤 방식?)
예상 시간: ~10분

[기획 의도]
- recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20) 의 분모를 위한 측정.
- KM20 oracle (RQ2 의 'equal' mode = KM20-equal) 은 이미 측정됨.
- RANDOM20 (무작위 K=20 분할, 공간 인식 0) 은 새 측정 필요.

[측정 조건]
- DEEP/SIFT 2, 5 sel × 5 seed × 100 query, sample_size 385
- partition_seed 42 (결정론적 무작위 부여, 측정 seed 와 별개)
- BERN baseline 도 동시 측정 (--include-bernoulli)

진행 후 모든 7-way 분석 (recovery rate 계산) 가능.
```

---

## 4. 카톡 §3.2 — 실험 #8 완료 메시지 골격 (측정 후 채움)

```
[RQ3 #8 완료] HH:MM (소요 ~Nh)

실험명: F. MiniBatch K-means
산출 위치: experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_minibatch.parquet

═══ [동기 → 가설 → 예상 → 실제] 4단계 ═══
(a) 동기 — 사전 계산 비용 비판에 대한 답. "1% 만 학습해도 oracle 의 80%?"
(b) 가설 — H3-F: recovery_rate 75~95%
(c) 예상 결과 — DEEP 80% / SIFT 75%
(d) 실제 결과 — DEEP {DEEP_REC}% / SIFT {SIFT_REC}%, 가설 {입증/반증}, 예상 {일치/불일치}

  - DEEP × KM20-equal Δ% (BERN 대비) = {KM_DEEP}%
  - DEEP × MiniBatch  Δ% (BERN 대비) = {MB_DEEP}% → recovery {DEEP_REC}
  - SIFT × KM20-equal Δ% = {KM_SIFT}%
  - SIFT × MiniBatch  Δ% = {MB_SIFT}% → recovery {SIFT_REC}

  paired Wilcoxon (MiniBatch vs RANDOM20): {p_BH 표}
  추가 발견: {clustersize/learn_frac/edge case}

═══ 의의 + 다음 ═══
- {박세은 비판 답변 narrative 강화 / 7-way 1순위 매듭 / 추가 측정 필요성}
- 다음 실험 #5 (C. Random Projection) 진행

자동 git commit + push 완료 (commit {hash})
```

---

## 5. narrative 결과정리.md 골격 (`experiments/results/rq3_agnostic/2026_05_07_first_runs/실험8_결과정리_20260507.md`)

> 측정 직후 Claude 가 채움. 패턴은 `experiments/results/rq2_aware/2026_05_06_alloc/실험4_결과정리_20260506.md` 와 동일.

```markdown
# 실험 #8 — RQ3 F. MiniBatch K-means

> **측정 시각**: 2026-05-07 HH:MM:SS KST 시작 → HH:MM:SS 종료 ({elapsed}s)
> **위치**: `experiments/results/rq3_agnostic/2026_05_07_first_runs/rq3_minibatch.parquet` ({n_rows} rows)

---

## 한 줄 요약

{한 문장 — 가설 입증/반증 + 핵심 수치 1개}

---

## 1. 동기

{박세은 비판 + KM20 사전 학습 비용 + Sculley 2010 + "1% 학습으로 충분한가" 의 답}

---

## 2. 가설

**H3-F (MiniBatch recovery)**: 1% 학습 sample 로도 KM20 oracle 의 75~95% 회수.

기대치:
- DEEP 1M: recovery 80% 내외
- SIFT 1.5M: recovery 75% 내외

---

## 3. 실제 결과

### DEEP × MiniBatch vs RANDOM20 / KM20

| sel | RANDOM20 Δ% | MiniBatch Δ% | KM20 Δ% | recovery |
|---|---|---|---|---|
| 0.01 | ... | ... | ... | ... |
| 0.05 | ... | ... | ... | ... |
| 0.10 | ... | ... | ... | ... |
| 0.30 | ... | ... | ... | ... |
| 0.50 | ... | ... | ... | ... |

### SIFT × MiniBatch vs RANDOM20 / KM20

(동일 표)

### paired Wilcoxon + BH-FDR (MiniBatch vs RANDOM20)

| dataset | sel | Δ% | p_raw | p_BH | reject_005 |
|---|---|---|---|---|---|
| DEEP | 0.01 | ... | ... | ... | ... |
| ... | | | | | |

---

## 4. 가설 확인 / 반증

### H3-F 75~95% recovery — {입증/반증}

{설명}

### 새 발견 (있으면)

{cluster 분포 / learn_frac 효과 / edge case}

---

## 5. 의의 + narrative 보강

### 박세은 비판 ("사전 계산 비용") 답변

{recovery 80% × learn_frac 1% × 학습 30초 → "비용 1/100 로 oracle 80% 회수" 형 narrative}

### 다음

- 실험 #5 (C. Random Projection) — 단순 하한과 비교 → 7-way 1, 2순위 매듭

---

**자동 git commit + push 완료**: commit {hash}
```

---

## 6. 주의사항 — 메인 세션이 측정 시 명심

### 6.1 server fresh conn (vector cast 누수)

- `_measure_common.py:fetch_all_vectors_safe()` 가 cluster 단위 fresh conn 으로 fetch
- 단일 conn 으로 LIMIT 50K 이상 시 unstable (5/6 검증)
- 만약 OOM 같은 에러 발생 시: cluster 별 LIMIT 추가 (지금은 cluster 전체 fetch)

### 6.2 sklearn version

- MiniBatch 학습 약간의 부동소수점 비결정성. random_state 고정해도 1~2% 차이 가능
- learn_seed 42 로 고정, n_init=3 default

### 6.3 RQ3 분석 시 데이터 통합

`rq3_figures.py` 는 단일 parquet 가정 (--rq3 하나). 여러 method 측정 후 분석할 때:

```python
import pandas as pd
df = pd.concat([
    pd.read_parquet("rq3_random20.parquet"),
    pd.read_parquet("rq3_minibatch.parquet"),
    pd.read_parquet("rq3_random_proj.parquet"),
    pd.read_parquet("rq2_alloc.parquet").query("mode in ['bernoulli', 'equal']")
        .rename(columns={"mode": "mode"})  # equal → km20 alias 필요시
        .assign(mode=lambda d: d["mode"].replace({"equal": "km20"})),
], ignore_index=True)
df.to_parquet("rq3_combined.parquet")
# 이후 rq3_figures.py --rq3 rq3_combined.parquet
```

KM20 alias 주의: RQ2 의 'equal' 모드 == KM20-equal allocation. recovery 계산 시 'km20' 이름으로 변환 필요.

---

## 7. 산출 위치 요약

| 파일 | 위치 | 용도 |
|---|---|---|
| `_measure_common.py` | `experiments/code/rq3/` | 측정 백엔드 |
| `run_random20.py` | `experiments/code/rq3/` | RANDOM20 baseline |
| `run_minibatch.py` | `experiments/code/rq3/` | 실험 #8 |
| `run_random_projection.py` | `experiments/code/rq3/` | 실험 #5 |
| `recovery_rate.py` | `experiments/code/local_analysis/` | recovery + BH-FDR |
| `rq3_figures.py` | `experiments/code/local_analysis/` | fig6/7/8 |

서버 작업 디렉토리: `/mnt/hdd0/home/capstone2026/cache/rq3/` (scp 후 위 wrapper 들 위치)

---

**작성**: 조현빈 + Claude · 2026-05-06 17:5x KST · 병렬 세션
**Hand-off**: 메인 세션 8M 보강 측정 마무리 → git pull → §0 체크리스트 따라 진입.
