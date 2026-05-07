# 아침 진입 핸드오프 — 2026-05-07 (목) 기상 후

> **새 Claude 세션 첫 메시지로 본 파일 read 후 진행.**
> 5/6 밤 ~22:50 마무리 → 8M 측정 + 8M sensitivity overnight 자동 chain 가동.

---

## ★ 30초 현황 파악

| 항목 | 상태 | 확인 명령 |
|------|------|-----------|
| 8M 측정 (`/tmp/measure_8m_done.flag`) | 🔁 진행 중 → 새벽 종료 예정 | `ssh capstone "ls /tmp/measure_8m_done.flag"` |
| 8M sensitivity 자동 trigger (`/tmp/post_8m_done.flag`) | 🔁 watchdog 가동 (post_8m tmux) | `ssh capstone "ls /tmp/post_8m_done.flag"` |
| 8M sensitivity 산출 (`rq3_8m_*.parquet`) | 🔁 done flag 기다린 후 자동 측정 | `ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_*.parquet"` |
| 새 코드 commit (5/6 추가분) | ⬜ 미커밋 | `git status` |
| 5/8 회의 자료 | ✅ 1-page summary ready | `submission/_drafts/속도는벡터_5월8일회의_1page_summary_20260506.md` |

---

## 1. 새벽 자동 chain 흐름 (5/6 22:38 ~ 5/7 새벽)

```
5/6 21:57:49 — 8M 측정 시작 (tmux measure_8m, PID 2146460)
              sel ∈ {0.1, 0.3} × mode ∈ {system, bernoulli, stratified} × 5 seed
              system/bernoulli ~5분/run, stratified ~17분/run
              ETA ~02:30~03:00 KST (stratified 가 5+5 = 10 runs × 17분 = ~3h)
                ↓
              완료 시: /tmp/measure_8m_done.flag 생성
                ↓
5/6 23:19:29 — post_8m watchdog 재시작 (12 method dispatch 반영)
                ↓
              done flag 감지 → 자동 chain:
              1) convert_8m_dtarget_to_parquet.py → query_selectivity_8m.parquet
              2) run_8m_sensitivity.py (12 method × DEEP_8M × 2 sel × 5 seed × 100 query)
                 - minibatch / minibatch_partial / random_proj / pca1d / hilbert / zorder /
                   hybrid / kdtree / pq / spectral / birch / lsh
                 - 추정 시간 ~4-6h (fetch 8M ~1-2h + 측정 12 method × ~10-30min)
              3) summary 출력 (q_error mean per method × dataset × sel)
              4) /tmp/post_8m_done.flag 생성
                ↓
5/7 ~07:00~09:00 KST 예상 — post_8m_done.flag 출현
```

**문제 발생 시 디버깅**:
```bash
# 진행 로그 확인
ssh capstone "cat /mnt/hdd0/home/capstone2026/cache/post_8m_pipeline.log"
ssh capstone "tmux capture-pane -p -t post_8m -S -100"
ssh capstone "tmux capture-pane -p -t measure_8m -S -50"
```

---

## 2. 기상 후 작업 흐름

### Step 1 — 결과 회수 (10분)

```bash
cd ~/Capstone

# 8M 측정 산출 회수
scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/2026_05_06_8m_midsel/*' \
    experiments/results/rq1_motivation/2026_05_06_8m_midsel/

# 8M sensitivity 산출 회수
scp 'capstone:/mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_*.parquet' \
    experiments/results/rq3_agnostic/

# 자동 chain 로그 (디버깅용)
scp capstone:/mnt/hdd0/home/capstone2026/cache/post_8m_pipeline.log \
    _internal/post_8m_pipeline_$(date +%Y%m%d).log
```

### Step 2 — 분석 (15분)

```bash
# 본 분석 driver 가 자동 8M 산출 합산 — METHODS 에 minibatch_partial/zorder/hybrid 등록 완료
python3 experiments/code/local_analysis/rq3_recovery_analysis.py
# 산출: recovery_summary.csv 의 8M 데이터 자동 추가
```

### Step 3 — 1M/1.5M 추가 측정 (필요 시)

8M sensitivity 끝났으면 PG 자유. 1M/1.5M 에서 6 method 측정:

```bash
ssh capstone
cd /mnt/hdd0/home/capstone2026/cache/rq3
python3 run_zorder.py            # ~12 min on 1M+1.5M
python3 run_hybrid.py            # ~15 min (outer KMeans + 5 inner Hilbert)
python3 run_minibatch_partial.py # ~12 min
python3 run_pca1d.py             # ~8 min (가장 단순)
python3 run_kdtree.py            # ~12 min (tree)
python3 run_pq.py                # ~10 min (FAISS-style)
```

산출 → `cache/rq1/rq3_{zorder,hybrid,minibatch_partial,pca1d,kdtree,pq}.parquet`. 회수 후 `rq3_recovery_analysis.py` 재실행 → 16 method × 2 dataset × 5 sel matrix 완성.

### Step 4 — 5/8 회의 마감 자료 (~3h)

- [ ] 시각화 — `experiments/code/local_analysis/rq3_figures.py` 에 zorder/hybrid/partial_fit + 8M sensitivity 추가
- [ ] 5/8 1-page summary 갱신 (8M 결과 반영)
- [ ] 카톡 §3.2 narrative — 추가 측정 결과 4단계 (a/b/c/d) 메시지 작성
- [ ] git commit + push

---

## 3. 5/6 밤 추가된 산출 (commit 미수행)

**새 RQ3 method 코드** (서버 동기화 완료):
- `experiments/code/rq3/zorder/zorder_curve.py` + `run_zorder.py`
- `experiments/code/rq3/hybrid/minibatch_hilbert.py` + `run_hybrid.py`
- `experiments/code/rq3/offline_simple/minibatch_partial.py` + `run_minibatch_partial.py`
- `experiments/code/rq3/pca1d/pca1d_quantile.py` + `run_pca1d.py` (Hilbert ablation 최상위)
- `experiments/code/rq3/kdtree/kdtree_partition.py` + `run_kdtree.py` (tree paradigm)
- `experiments/code/rq3/pq/product_quantization.py` + `run_pq.py` (FAISS-style 산업 표준)
- `experiments/code/rq3/run_8m_sensitivity.py` (10 method dispatch)
- `experiments/code/rq3/convert_8m_dtarget_to_parquet.py`
- `experiments/code/rq3/post_8m_pipeline.sh` (overnight watchdog → run_8m_sensitivity 가 자동 10-method)

**새 분석 코드**:
- `experiments/code/local_analysis/rq1_gradient_monotonicity.py`
- `experiments/code/local_analysis/locality_curve_comparison.py`
- `experiments/code/local_analysis/rq3_method_redundancy_ari.py` (10-method ARI matrix)
- `experiments/code/local_analysis/rq3_bootstrap_effect_size.py` (Cohen's d + bootstrap CI)
- `experiments/code/local_analysis/rq3_per_query_ranking.py` (query 난이도 vs method 적합성)

**수정**:
- `experiments/code/rq3/_measure_common.py` — DATASETS_8M 추가
- `experiments/code/local_analysis/recovery_rate.py` — method_minus_bern_pct 항상 계산
- `experiments/code/local_analysis/rq3_recovery_analysis.py` — 추가 method/parquet 등록

**산출 (분석 결과)**:
- `experiments/results/rq1_motivation/rq1_gradient_monotonicity.{md,csv,json}` — DEEP-KM20 ρ=-0.680 CI [-0.800, -0.440] 0 제외
- `experiments/results/rq3_agnostic/locality_curve_comparison.{md,csv}` — Hilbert inverse Manhattan 1.000 vs Z-order 1.992
- `experiments/results/rq3_agnostic/rq3_method_redundancy_ari.{md,csv}` + `*_pairs.csv` — Hilbert↔Z-order ARI 0.479, MiniBatch↔partial clustered=1.000
- `experiments/results/rq3_agnostic/rq3_bootstrap_effect_size.{md,csv}` — Cohen's d (Hilbert -0.156 negligible-small, IS +0.5~+0.7 hurt-medium)
- `experiments/results/rq3_agnostic/rq3_per_query_ranking.{md,csv}` + `rq3_query_difficulty_method.csv` — best 빈도 (Hilbert 200, MiniBatch 190, KM20 172), spread vs difficulty 상관 0.78
- `experiments/results/rq3_agnostic/recovery_summary.csv` (재생성, method_minus_bern_pct 채움)

**문서**:
- `submission/_drafts/속도는벡터_5월8일회의_1page_summary_20260506.md` — 5/8 회의 자료
- `experiments/results/RQ1_RQ2 실험 결과 정리.md` — §W1 Sprint 보강 섹션 추가
- `CLAUDE.md` — 5/6 22:30 상태 반영
- `_internal/handoff_morning_20260507.md` (본 파일)

**commit 권장 (기상 후 우선)**:
```bash
git add experiments/code/rq3/{zorder,hybrid,run_zorder.py,run_hybrid.py,run_8m_sensitivity.py,convert_8m_dtarget_to_parquet.py,post_8m_pipeline.sh,_measure_common.py,offline_simple/minibatch_partial.py,run_minibatch_partial.py} \
        experiments/code/local_analysis/{rq1_gradient_monotonicity.py,locality_curve_comparison.py,recovery_rate.py,rq3_recovery_analysis.py} \
        experiments/results/rq1_motivation/rq1_gradient_monotonicity.* \
        experiments/results/rq3_agnostic/{locality_curve_comparison.*,recovery_summary.csv,wilcoxon_*.csv} \
        "experiments/results/RQ1_RQ2 실험 결과 정리.md" \
        CLAUDE.md \
        submission/_drafts/속도는벡터_5월8일회의_1page_summary_20260506.md \
        _internal/handoff_morning_20260507.md

git commit -m "RQ3 보강 — Z-order/hybrid/partial_fit + Hilbert mechanism 분석 + 단조성 통계"
git push origin main
```

---

## 4. 5/8 회의 (D-2) 마감 체크리스트

- [✅] RQ1 narrative + 단조성 통계 확정
- [✅] RQ2 분석 완료 (5/6 commit 037c425)
- [✅] RQ3 7-way 측정 완료 (5/6 commit 589d66e)
- [✅] RQ3 추가 3 method 코드 ready (Z-order/hybrid/partial_fit)
- [✅] Hilbert mechanism 정량 분리 (locality_curve_comparison.md)
- [✅] 5/8 1-page summary
- [🔁] 8M sensitivity 측정 — overnight 자동 진행
- [⬜] 1M/1.5M 추가 method 측정 (8M sensitivity 끝난 후)
- [⬜] 시각화 figures 갱신
- [⬜] 카톡 §3.2 narrative + RQ3 결과 종합 메시지
- [⬜] 자문 요청 메일 초안 (회의에서 합의 후 작성, 5/15 발송)

---

## 5. 핵심 결과 한 줄 정리 (회의 ready)

```
RQ1: KM20 vs BERN 의 단조성 ρ=-0.680 (CI [-0.800, -0.440] 0 제외) → "sel↓ → 공간 인식 가치↑" 확정
RQ2: KM20 oracle 5-way 우위 (-1.3~-10.5%) + sample_size robustness 모든 40 cell 일관
RQ3: Hilbert (-1.78%, -2.47%) + MiniBatch (-1.88%, -1.97%) 양강. Hilbert 의 1D-2D Manhattan=1.000 (Z-order 1.992) → contribution origin 정량 분리
RQ3 보강:
  - ARI: Hilbert↔Z-order=0.479 (curve+PCA 중첩), MiniBatch↔partial=1.000 (OLTP 결정적)
  - Effect size: Hilbert d=-0.156 (negligible-small, honest 한계), IS d=+0.5~0.7 (hurt-medium)
  - Per-query: best 빈도 Hilbert 200 > MiniBatch 190 > KM20 172. spread vs difficulty 0.78 (어려운 query 에서 method 차이 결정적)
contribution: Hilbert (★1순위) + MiniBatch (★production) + IS/Distance-Shell (★negative control)
새 method (8M dispatch + 측정 ready): pca1d (Hilbert ablation 최상위), kdtree (tree paradigm), pq (FAISS-style)
```

---

**작성**: 조현빈 · 2026-05-06 22:55 KST
**다음 트리거**: 5/7 아침 새 Claude 세션 → `cat _internal/handoff_morning_20260507.md` 또는 본 파일 read.
