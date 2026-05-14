# Worker G — DEEP 8M selectivity 5단계 확장 측정 (19 method)

> **임무**: 현재 DEEP 8M은 2 sel (0.10 / 0.30) 만 측정. 5 sel (0.01 / 0.05 / 0.10 / 0.30 / 0.50) 로 확장 → 1M와 동일 변수 grid → cross-scale 외적 타당성 강화.
> **세션 진입**: 본 핸드오프 첫 read → 서버 측정 dispatch → 회수 → 분석 → commit.
> **manager 세션**: 2026-05-07 12:05 KST, Opus 4.7 1M.

---

## 1. 입력 자료

| 자료 | 위치 |
|---|---|
| 8M 측정 인프라 | `/mnt/hdd0/home/capstone2026/cache/rq3/run_8m_sensitivity.py` (서버) |
| 1M 측정 결과 (5 sel × 22 method) | `experiments/results/rq3_agnostic/rq3_*.parquet` |
| 8M 현재 측정 (2 sel × 19 method) | `experiments/results/rq3_agnostic/rq3_8m_*.parquet` |
| 8M 데이터셋 | `partsupp_deep_10_phase7_8m_subset` (10GB) |
| 8M query selectivity | `/mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_8m.parquet` (5 sel 모두 포함 확인됨) |

## 2. 작업 단계

### Step 1 (15분) — 추가 측정 plan

**현재 8M**: 19 method × 2 sel (0.10 / 0.30) × 5 seed × 100 query = 19,000 cell

**추가 측정**: 19 method × **3 sel 추가** (0.01 / 0.05 / 0.50) × 5 seed × 100 query = 28,500 cell

→ 8M 5 sel 완성: 19 method × 5 sel × 5 seed × 100 query = **47,500 cell**

(Worker F 의 baseline 3 추가 시: 22 method × 5 sel = 55,000 cell)

### Step 2 (1h) — 서버 측정 dispatch

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \
  for sel in 0.01 0.05 0.5; do
    python3 -u run_8m_sensitivity.py \
      --methods all \
      --sel \$sel \
      --seed 0,1,2,3,4 \
      --queries 100 \
      --output_suffix _sel\${sel} \
      >> /tmp/8m_sel_expand.log 2>&1 &
  done
"
```

또는 (script 형태가 다르면) 단일 wrapper 작성:

```bash
ssh capstone "cat > /mnt/hdd0/home/capstone2026/cache/rq3/run_8m_sel_expand.sh << 'SHEOF'
#!/usr/bin/env bash
# DEEP 8M sel 5단계 확장 — 19 method × 3 추가 sel
cd /mnt/hdd0/home/capstone2026/cache/rq3
for sel in 0.01 0.05 0.5; do
  for method in birch distance_shell gmm hdbscan hilbert hybrid \
                importance_sampling kde_pilot kdtree lsh minibatch \
                minibatch_partial pca1d pq random_proj sobol \
                sparse_rp spectral zorder; do
    python3 -u run_\${method}.py --dataset DEEP_8M --sel \$sel \
      --seed 0 1 2 3 4 --queries 100 \
      > /tmp/8m_\${method}_sel\${sel}.log 2>&1
  done
done
echo 'done' > /tmp/8m_sel_expand_done.flag
SHEOF
chmod +x /mnt/hdd0/home/capstone2026/cache/rq3/run_8m_sel_expand.sh
tmux new -d -s 8m_sel_expand /mnt/hdd0/home/capstone2026/cache/rq3/run_8m_sel_expand.sh
"
```

(서버 script 패턴 검증 후 정확한 형태로 작성)

### Step 3 (3-4h, 측정 진행) — 모니터링

19 method × 3 sel × ~5-15분/cell = 약 4-8h 소요. 백그라운드 진행 + watchdog.

```bash
# tmux 진행도 확인
ssh capstone "tmux ls | grep 8m_sel_expand"
ssh capstone "ls /tmp/8m_*sel*.log | wc -l"  # 진행률
```

### Step 4 (30분) — 산출 회수

```bash
# 기존 8M parquet 와 merge (또는 별도 파일로 회수)
scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_*_sel*.parquet' \
    experiments/results/rq3_agnostic/8m_sel_expand/

# 또는 기존 8M parquet 통합 갱신 (sel column으로 distinguish)
```

### Step 5 (30분) — 분석 driver 재실행

```bash
python3 experiments/code/local_analysis/rq3_8m_cross_scale.py  # 5 sel × 19 method
python3 experiments/code/local_analysis/recovery_rate.py
python3 experiments/code/local_analysis/rq3_bootstrap_effect_size.py
```

### Step 6 (30분) — narrative 결과 정리

8M sel 5단계 ranking + 1M ↔ 8M cross-scale 일관성 표 작성:

`experiments/results/rq3_agnostic/rq3_8m_5sel_cross_scale.md`:
- 5 sel × 19 method × DEEP 1M vs 8M
- 핵심: 8M 에서 ranking 보존 → 외적 타당성 강화

### Step 7 (15분) — commit + push

```bash
git add experiments/results/rq3_agnostic/rq3_8m_*_sel*.parquet \
        experiments/results/rq3_agnostic/rq3_8m_5sel_cross_scale.{csv,md} \
        experiments/results/rq3_agnostic/recovery_summary.csv
git commit -m "DEEP 8M selectivity 5단계 확장 (19 method × 3 추가 sel) — cross-scale 외적 타당성 보강"
git push
```

## 3. 산출 spec

| 산출 | 위치 | 기대 rows |
|---|---|---|
| 19 method × 3 sel × 1,500 rows | `experiments/results/rq3_agnostic/8m_sel_expand/` | 28,500 |
| 8M 5 sel cross-scale 종합 | `experiments/results/rq3_agnostic/rq3_8m_5sel_cross_scale.md` | — |
| recovery_summary.csv 갱신 | 동일 | 8M 5 sel 행 추가 |

## 4. 검증 기준

- [ ] 19 method × 3 sel = 57 cell 모두 측정 (각 5 seed × 100 query = 500 row 이상)
- [ ] NaN ratio: IS는 < 5% (8M에서 자연 안정화), 나머지 < 1%
- [ ] cross-scale ranking 1M↔8M 일관 (top 4 method: Hilbert / partial / HDBSCAN / Hybrid 보존)

## 5. 의존성

- **Worker F (baseline 3개)**: 병렬 가능. 본 worker 끝난 후 22 method × 5 sel cross-scale 통합 가능
- **5/27 발표 narrative**: 본 결과는 Slide 11 (cross-scale validation) 보강

## 6. 예상 시간

총 **5-7h** (측정 4-6h + 분석 1h). 본 worker session 자체는 1-2h 직접 작업 + 측정 대기.

## 7. 본 worker가 만들지 말 것

- 1M 측정 재진행
- KM20 측정 (Worker F 영역)
- 새 method 추가 (5/8 회의 합의 후)

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 12:05 KST
**기반**: 5/7 측정 검증 결과 (8M 2 sel만, 5 sel 확장 = W2 권고)
