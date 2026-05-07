# Worker L — DEEP 8M RQ2 5-mode allocation + size sensitivity

> **임무**: DEEP 8M에서 RQ2 5-mode allocation (BERN/Equal/Prop/Neyman/Anti-Neyman) 측정. 현재 Anti-Neyman 1 mode 만 cross-scale (commit 248319a). 나머지 4 mode + size sensitivity 추가 → 8M에서도 KM20 oracle sample-size robust 입증.
> **세션 진입**: 본 핸드오프 첫 read → 서버 측정 dispatch → 회수 → 분석 → commit.
> **manager 세션**: 2026-05-07 12:34 KST, Opus 4.7 1M.
> **시간**: 5-7h (서버 background)

---

## 1. 빠진 실험 (5/7 12:30 검증)

| 항목 | 현재 상태 |
|---|---|
| RQ2 1M 5-mode | ✓ DEEP+SIFT 25,000 cell |
| RQ2 1M size sensitivity | ✓ 40,000 cell |
| RQ2 8M Anti-Neyman | ✓ 1 mode cross-scale (s=0.1 Δ=+1.28% [+0.28, +2.28] CI 0 제외) |
| **RQ2 8M 5-mode allocation** | ⚠️ 4 mode (BERN/Equal/Prop/Neyman) 미측정 |
| **RQ2 8M size sensitivity** | ❌ 미측정 |

## 2. 작업 단계

### Step 1 (10분) — 측정 plan

**8M 5-mode allocation**:
- mode 5종: BERN / Equal / Proportional / Neyman / Anti-Neyman (이미 측정)
- selectivity 5단계 (0.01 / 0.05 / 0.10 / 0.30 / 0.50)
- seed 5개
- query 100개
- = 4 추가 mode × 5 sel × 5 seed × 100 query = **10,000 cell** (Anti-Neyman 보존)

**8M size sensitivity** (선택, 우선순위 낮음):
- ssize 4단계 (100 / 385 / 1000 / 3000)
- mode 2종 (bernoulli / proportional)
- selectivity 5단계
- seed 5개
- = 4 ssize × 2 mode × 5 sel × 5 seed × 100 query = 20,000 cell (~3-4h)

### Step 2 (3-4h) — 5-mode 측정 dispatch (★ 우선)

```bash
ssh capstone "
cd /mnt/hdd0/home/capstone2026/cache
# 1M rq2_alloc_python.py 을 8M 적용
cat > rq2_alloc_python_8m.py << 'PYEOF'
# DEEP 8M × 5 mode × 5 sel × 5 seed × 100 query
# stratum_id 0-19 PG 활용, K-means 재 fit X
# σ_i 는 vector_stratum_sigma 의 8M σ 활용 (이미 valid)
# 산출: rq2_alloc_DEEP_8M_5mode.parquet
[1M rq2_alloc_python.py 패턴 + 8M 적용]
PYEOF

tmux new -d -s 8m_rq2_5mode 'cd /mnt/hdd0/home/capstone2026/cache && python3 -u rq2_alloc_python_8m.py 2>&1 | tee /tmp/8m_rq2_5mode.log'
"
```

### Step 3 (대기) — 모니터링

```bash
ssh capstone "tail -f /tmp/8m_rq2_5mode.log"
```

### Step 4 (15분) — 산출 회수

```bash
scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq2_alloc_DEEP_8M_5mode.parquet' \
    experiments/results/rq2_aware/2026_05_07_8m_alloc/
```

### Step 5 (45분) — 분석

```python
# experiments/code/local_analysis/rq2_8m_5mode_analysis.py 작성
# - 5 mode × 5 sel 평균 Δ% (BERN baseline)
# - paired Wilcoxon p-value
# - 1M ↔ 8M cross-scale 일관성 표
# - σ_i 신호 약함 8M 재현 여부 (Anti-Neyman vs Prop 격차)
# 산출: experiments/results/rq2_aware/2026_05_07_8m_alloc/rq2_8m_5mode_analysis.{md,csv}
```

기대 결과:
- ✓ 모든 stratified > BERN (1M 와 일관)
- ✓ KM20 sample-size robust 8M 재현
- ✓ Anti-Neyman vs Prop 격차 1M (DEEP s=0.01 +5.21%) 와 일관 방향

### Step 6 (선택, 3-4h) — size sensitivity 측정 (우선순위 낮음, 5/8 후 OK)

```bash
# 5-mode 측정 완료 후 dispatch
# rq2_size_sensitivity_8m.py 작성 + tmux background
```

### Step 7 (15분) — narrative + commit

`experiments/results/rq2_aware/2026_05_07_8m_alloc/rq2_8m_5mode_summary.md`:
- 8M 5 mode × 5 sel 결과 표
- 1M ↔ 8M cross-scale 일관성
- KM20 oracle sample-size robust 8M 재현
- 5/27 발표 Slide 7 / 6/11 보고서 Section 4.2 입력

```bash
git add experiments/results/rq2_aware/2026_05_07_8m_alloc/ \
        experiments/code/local_analysis/rq2_8m_5mode_analysis.py
git commit -m "Worker L: DEEP 8M RQ2 5-mode allocation 측정 — KM20 oracle cross-scale robust 입증"
git push
```

## 3. 산출 spec

| 산출 | 위치 | 기대 rows |
|---|---|---|
| 8M 5-mode alloc | `rq2_alloc_DEEP_8M_5mode.parquet` | 10,000 (4 추가 mode × 5 sel × 5 seed × 100 q) |
| 8M 5-mode 분석 | `rq2_8m_5mode_analysis.md` | — |
| (옵션) 8M size sens | `rq2_size_sensitivity_DEEP_8M.parquet` | 20,000 |

## 4. 검증 기준

- [ ] 4 추가 mode × 5 sel × 5 seed × 100 q = 10,000 cell 측정 (NaN < 1%)
- [ ] 모든 stratified > BERN (1M 와 일관)
- [ ] Anti-Neyman vs Prop CI 0 제외 (1M 와 일관 방향)
- [ ] paired Wilcoxon p-value + BH-FDR 보정

## 5. 의존성

- F/G/J 와 PG 8M 동시 read OK (재 fit X, stratum_id 기존 활용)
- I (σ 재계산) 의 8M σ 보존 — RQ2 측정 영향 X (이미 valid)
- master.md narrative 갱신은 manager session 책임

## 6. 본 worker가 만들지 말 것

- 8M K-means K=20 재 fit (PG stratum_id 보존)
- σ table 재 계산 (Worker I 영역)
- 1M 측정 재진행
- master.md 변경 (manager 책임)

---

**작성**: Claude (manager session, Opus 4.7 1M) · 2026-05-07 12:34 KST
**기반**: 5/7 RQ 완전성 검증 — DEEP 8M RQ2 4 mode + size sensitivity 빠짐 발견
