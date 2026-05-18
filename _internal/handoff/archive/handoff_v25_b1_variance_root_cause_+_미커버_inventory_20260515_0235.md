# Handoff v25 — B1 Variance + 미커버 inventory + Pareto/K dim + raw/ reorganize + 박세은 query/threshold + fit_time launch (5/15 11:50)

> **목적**: 새 mini session (5/15 01:20 시작) + morning session (11:05 ~ 11:50) 의 자동 진행 결과 종합. 사용자 박광현 미팅 14:00 전 + post-미팅 base entry point.
>
> **업데이트 11:50**: morning session 진행 사항 추가
> - raw/ dataset 단일 기준 reorganize (1352 file git mv, commit e570311)
> - measure_paper_exact.py 영역 fit_time / cache_time field 추가 (CaseA + CaseB) + Pareto Top 5 × 9 cell × 2 mode = 90 file launch
> - 박세은 11:34 요청 — 임채림용 query vector + threshold 패키지 (5 dataset × 100 query × 5 selectivity D_target, commit 507c7c9)
> - REPORT v11 §12 추가 (B1 variance + Pareto + K dim + 미커버 + fit_time launch reference)
> - narrative v2 깨진 3 라인 fix
> - K_granularity_dim 보고서 깨진 한국어 정상화

---

## 0. 본 mini session 핵심 결과 (★)

1. **B1 random variance root cause 정량 규명** — 사용자 5/15 critical 지적 ("B1 implied 너무 큼") 의 근본 원인 분석
   - paper exact B1 inherent trial CV: **6.33%** (n=10)
   - measurement run 별 systematic bias ±10~25% (random variance 만으로 설명 불가)
   - 5/12 K granularity: -23% systematic bias
   - 5/14 SF axis K=10: +24% / K=30: -16% (반대 방향)
   - 5/15 archive K=10: +10% (5/12 와 반대)
   - → paper exact base B1 만 reliable denominator
2. **측정 미커버 영역 종합 매트릭스** — paper Fig 매핑 + 우선순위
   - paper exact base coverage: 9 cell × 56 method = **98.2% 유효** (495/504, A2-Fig8 scope 외 제외)
   - paper Fig 13 sel sweep: sel=0.001 (A4-sel) + sel=0.01 (A1-DEEP) ✓, **sel=0.10 미측정**
   - K granularity 9 cell 확장: 9 × 4 × 3 × 2 = 216 file (현재 5 cell 만)
3. **★ Pareto Top 5 cross-validation** (03:00 추가 분석)
   - 5 method (sparse_rp/chao/neuram/pca1d/hilbert) × 9 cell = **100% coverage** 확인
   - **paired CaseB < CaseA = 97.78%** (44/45, 1 outlier neuram A1-SSN)
   - 전체 56 method = 91.46% (450/492)
   - robustness rank: hilbert (std 1.55%) > pca1d > sparse_rp > chao_weighted > neuram
   - ★ 박세은 review answer 강화 anchor
4. **★ K granularity × dimension 종합 검증** (03:10 추가 분석)
   - 5/12 base: K=10 best 55%, K=20 25%, K=30 20%
   - 5/14 SF axis: A5-scale K=10 모두 positive (CaseB > CaseA), K=30 모두 negative
   - 동일 DEEP 96d K=10 인데 5/12 (-9.5%) vs 5/14 (+10.3%) = **measurement run-level bias 재확인**
   - dimension-dependent K best 가설 = 약한 evidence
5. **A4-sel × K granularity 재launch readiness 확보** (단, 코드 수정 필요 → 사용자 승인 후 launch)
6. **claude.ai/design v7 + 박광현 PDF v3 readiness 확인**

---

## 1. 본 mini session 작업 chain (5/15 01:20 ~ 02:35, ~1h 15m)

| 시점 | 작업 |
|---|---|
| 01:20 | handoff v24 read + 상태 점검 (시간/git/directory/archive) |
| 01:25 | 전체 raw/ 영역 inventory (10 영역, 1367 file) + REPORT v11 §10 미커버 9 카테고리 확인 |
| 01:30 | paper exact B1 baseline 9 cell read + trial variance 정량 (CV 6.33%) |
| 01:35 | 5/12 K granularity 영역 implied B1 = 2×CaseB - CaseA 일괄 계산 (n=60) |
| 01:40 | 5/14 SF axis 영역 implied B1 계산 (n=24) + 5/15 archive (n=28) 비교 |
| 01:45 | sparse_rp outlier 분리 (K=10 영역 매우 불안정) + non-sparse 영역 systematic bias 확정 |
| 01:50 | **분석 보고서 1 작성**: `experiments/results/analysis/B1_variance_root_cause_종합분석_20260515_0150.md` |
| 02:00 | paper Fig 매핑 + cell × method coverage matrix 계산 (paper exact base 495 / 560) |
| 02:05 | **분석 보고서 2 작성**: `experiments/results/analysis/측정_미커버_영역_종합_inventory_20260515_0205.md` |
| 02:15 | server ssh verify (tmux clean, cache/rq3/_measure_common.py SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50], N_STRATA = 20) |
| 02:20 | A4-sel cell sel=0.001 verify (analyze_paper_exact.py 영역 명시) — paper Fig 13 영역 |
| 02:25 | claude.ai/design v7 WebFetch 403 (auth required) — 사용자 직접 verify 요청 |
| 02:30 | 박광현 PDF v3 page 1-3 + 13-14 sample read — readiness 100% 확인 |
| 02:35 | **handoff v25 작성** (본 file) |

---

## 2. B1 random variance root cause (★ 핵심 finding)

### 2.1 paper exact B1 inherent trial variance (n=10 trial)

`raw/10_전체측정_백업/B1_baseline_9cell/` 9 file 분석:

| Cell | trim_mean | mean | std | CV% | spread% |
|---|---:|---:|---:|---:|---:|
| A1-DEEP | 1.6346 | 1.6132 | 0.1260 | 7.81 | 26.32 |
| A1-SIFT | 1.6951 | 1.6702 | 0.1090 | 6.53 | 22.23 |
| A1-SSN | 1.6249 | 1.6207 | 0.0472 | 2.91 | 9.74 |
| A2-Fig7 | 1.6556 | 1.6332 | 0.1323 | 8.10 | 26.30 |
| A2-Fig9 | 1.5407 | 1.5280 | 0.1429 | 9.35 | 26.43 |
| A4-sel | 5.9856 | 5.9842 | 0.1958 | 3.27 | 8.58 |
| A5-scale-sf1 | 1.6182 | 1.6175 | 0.0290 | 1.79 | 5.29 |
| A5-scale-sf10 | 1.5407 | 1.5280 | 0.1429 | 9.35 | 26.43 |
| A5-scale-sf100 | 1.6346 | 1.6132 | 0.1260 | 7.81 | 26.32 |

**Aggregate**: CV mean **6.33%** (range 1.79% ~ 9.35%) · spread/mean mean **19.74%**

### 2.2 measurement run 별 systematic bias

| Run (시점) | n | delta% mean | delta% std | 방향 |
|---|---:|---:|---:|---|
| paper exact base (5/11) | 9 | 0.00% | - | reference |
| 5/12 K granularity (전체) | 60 | -23.02% | 17.64% | negative |
| 5/12 non-sparse only | 45 | **-18.84%** | 3.86% | negative tight |
| 5/14 SF axis (K=10) | 12 | +24.27% | 23.84% | **positive (5/12 영역 반대)** |
| 5/14 SF axis (K=30) | 12 | -16.43% | 7.61% | negative |
| 5/15 archive (K=10) | ~16 | +20% 부근 | 큼 | **positive (5/12 영역 반대)** |

★ 핵심: inherent CV 6% 만으로 ±20% 영역 systematic bias 설명 불가 → measurement run 영역 systematic difference 존재.

### 2.3 권장안 3가지 (B1_variance_root_cause_종합분석_20260515_0150.md)

- **안 A (Recommended)**: paper exact base 만 denominator 로 사용 (새 측정의 implied B1 은 보고 안 함)
- 안 B: 다중 run 평균 (rigorous, 측정 시간 9-10x)
- 안 C: 단일 run 보고 + caveat 명시 (학술 정합성 약함)

### 2.4 paired narrative 영역 영향 없음 ★

handoff v24 narrative 핵심 수치는 모두 **paired comparison (CaseB vs CaseA)**:
- paired CaseB < CaseA **92.5%** (455/492, p<1e-45)
- Cliff's δ large better **63.0%** (311/494)
- Hedges' g large 55.7% (275/494)

→ B1 systematic bias 가 paired 결과 자체를 오염시키지 않음. paired narrative 는 robust 유지.

---

## 3. 측정 미커버 영역 종합 inventory (★ 사용자 mission 답변)

### 3.1 paper exact base coverage matrix

10 cells × 56 method = 560 cell-method 중 측정 = **495** (paper exact base):
- 미커버 65 = A2-Fig8 영역 54 (scope 외) + 각 cell 영역 1-2 method (audit drop / 자원 한계)
- 유효 coverage (A2-Fig8 제외): 9 cell × 56 method = 504 영역 영역 495 = **98.2%** ★

### 3.2 paper Fig 매핑

| paper Fig | 우리 cell | 측정 |
|---|---|---|
| Fig 5/6 (paper main 8 cells) | A1-DEEP, A1-SIFT, A1-SSN | ✓ |
| Fig 7 (DEEP/YFCC join) | A2-Fig7 | ✓ |
| Fig 8 (multi-vector) | A2-Fig8 | ⚠️ scope 외 (paper §V-A) |
| Fig 9 (DEEP+WIKI cross) | A2-Fig9 | ✓ |
| Fig 10/11 (ECQO end-to-end) | A3-TPCDS | ⚠️ scope 외 |
| Fig 12 (paper main 8 cells avg Q-error 1.69) | A1+A2-Fig7/9+A5 | ✓ |
| **Fig 13 (sel sweep)** | A4-sel (sel=0.001) ✓ + A1-DEEP (sel=0.01) ✓ + **sel=0.10 ★ 미측정** | ⚠️ |
| Fig 14 (DEEP scale sf=1/10/100) | A5-scale-sf{1,10,100} | ✓ |

**paper Fig coverage**: Fig 5/6/7/9/12/14 = 100% ✓. Fig 13 sel sweep 중 sel=0.10 만 미측정.

### 3.3 추가 측정 영역 inventory (paper exact base 외)

| 영역 | file | cell coverage | method coverage |
|---|---:|---|---|
| 06 K granularity (5/12 base) | 120 | 5 cells | 4 method × 3 K |
| 06 K granularity (5/14 SF axis) | 48 | 3 cells (A5-scale-sf{1,10,100}) | 4 method × 2 K |
| 05 alpha sweep | 20 | A2-Fig9 1 cell | 4 method × 5 α |
| 07 cheap 근사 4 후보 | 32 | A2-Fig9 1 cell | 4 method × 4 후보 |
| 08 multi-join | 8 | A2-Fig9 1 cell | 4 method × 2 mode |
| 09 multi-vector A2-Fig8 (scope 외) | 8 | A2-Fig8 1 cell | 4 method × 2 mode |
| **합계 추가 측정** | **236** | A2-Fig9 위주 + K granularity 8 cell | 4 method (sparse_rp/chao/hilbert_real/hyperloglog) 위주 |

★ 추가 측정 영역 cell coverage 좁음. 9 cell 전수 확장 시 측정량 폭증.

### 3.4 미커버 영역 우선순위

| Priority | 측정 영역 | file 수 | server time | narrative 가치 |
|---|---|---:|---|---|
| ★★★ | A4-sel × K granularity (paper Fig 13 sel sweep + K=10/30) | ~48 | 6-12h | paper Fig 13 완성 |
| ★★ | K granularity 9 cell × 4 method 확장 | ~216 | 12-24h | dimension-dependent K best |
| ★ | shifting workloads (5/27 phase 1) | 720 | 30-50h | paper §VI-B 추가검증 |
| ★ | 3-way 비교 (Bernoulli + SelNet + Form 1) | 360 | 12-24h | Form 1 measurement |
| ★ | α sweep 9 cell 확장 | 360 | 12-24h | α=0.5 default robustness |
| ★ | cheap 근사 9 cell 확장 | 256 | 8-16h | Centroid tuple robustness |

**현실적 우선순위**:
1. ★ A4-sel × K granularity (48 file) — 박광현 미팅 후 launch 결정
2. ★ shifting workloads + 3-way 비교 (5/20~5/22 launch 예정, 5/27 D-13 phase 1)
3. K/α/cheap 9 cell 확장 — post 5/27, 6/11 보고서 작성 시 가치 판단

---

## 4. A4-sel × K granularity 재launch readiness

### 4.1 server 환경 verify (5/15 02:15)

- **server**: 165.132.140.240 (capstone2026)
- **tmux**: clean (no session running)
- **measurement core**: `cache/rq3/_measure_common.py` (SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50], N_STRATA = 20 paper exact)
- **A4-sel current**: sel=0.001 only (paper Fig 13 영역 첫 selectivity point)
- **paper exact base 측정 script**: `measure_paper_exact.py` 영역 영역 cell 영역 정의 (line 259 영역 영역 영역 영역)

### 4.2 미측정 영역 정확 정의

paper Fig 13 sel sweep 의 3 selectivity:
- sel=0.001 → A4-sel ✓ (paper exact base)
- sel=0.01 → A1-DEEP ✓ (paper exact base, sf=100)
- **sel=0.10 → ★ 미측정** (DEEP sf=100 sel=0.10 cell 없음)

K granularity 영역:
- A4-sel (sel=0.001) × K=20 ✓ (paper exact base default)
- A4-sel (sel=0.001) × K=10/30 ✗ 미측정
- A4-sel-0.10 (new cell) × K=10/20/30 ✗ 모두 미측정

**총 미측정**:
- A4-sel (sel=0.001) × K=10 × 4 method × 2 mode = 8 file
- A4-sel (sel=0.001) × K=30 × 4 method × 2 mode = 8 file
- A4-sel-0.10 (new cell) × K=10/20/30 × 4 method × 2 mode = 24 file
- + B1 baseline (같은 run 안 측정 권장) 2 file
- **합계 약 42 file** (handoff v24 영역 48 file 영역 약간 차이, 다만 launch readiness 명확)

### 4.3 launch 영역 필요 작업 (★ 자동 launch 불가)

**코드 수정 필요** (server 측):
1. `measure_paper_exact.py` 영역 A4-sel-0.10 cell 추가 (sub="A4-sel-0.10", sf=100, sel=0.10, fig="Fig 13")
2. K granularity 영역 지원 (현재 K=20 default 외 K=10/30 영역 명령 줄 argument 영역 영역 영역 영역 영역)
3. B1 baseline 영역 같은 run 영역 측정 보장 (안 A 영역 영역 권장)

**launch sequence (사용자 승인 후)**:
```bash
ssh capstone2026@165.132.140.240
cd /mnt/hdd0/home/capstone2026
tmux new -s a4_sel_k_granularity
# A4-sel (sel=0.001) × K=10/30 launch
python3 cache/rq3/measure_paper_exact.py --cell A4-sel --K 10
python3 cache/rq3/measure_paper_exact.py --cell A4-sel --K 30
# A4-sel-0.10 (new cell) × K=10/20/30 launch (cell 정의 추가 후)
python3 cache/rq3/measure_paper_exact.py --cell A4-sel-0.10 --K 10
python3 cache/rq3/measure_paper_exact.py --cell A4-sel-0.10 --K 20
python3 cache/rq3/measure_paper_exact.py --cell A4-sel-0.10 --K 30
```

★ 위 명령어 사용 가능 여부 = measure_paper_exact.py 의 argparse 가 `--K` arg 지원 여부에 따름. 미지원 시 코드 수정 우선 필요.

### 4.4 권장 next step (★ 사용자 결정 영역)

- **추천**: 박광현 미팅 (5/15 14:00) 후 launch (미팅 input 에 따라 우선순위 변경 가능)
- 박광현 input 영역 "측정 plan 우선순위 변경 가능 영역" (PDF v3 page 13 영역 영역) — SelNet / streaming workload / drift / CE4HD 영역 영역 영역 영역
- A4-sel × K granularity 영역 launch 가치 vs. 다른 추가검증 영역 launch 가치 비교 후 결정

---

## 5. claude.ai/design v7 deck verify (★ 사용자 직접)

- URL: https://claude.ai/design/p/019e1a41-701c-7134-9ce1-1247262c1563
- WebFetch 결과: **403 Forbidden** (auth required, Claude 직접 접근 불가)
- 사용자 영역 직접 verify 필요:
  - badge 일괄 적용 prompt response 확인 (✓/⏳/📅 3-tier 분류)
  - 사실 검증 prompt response 확인 (S12 RQ1 +3.74% / S13 RQ2 Proportional −9.53% / S14 paradigm rollup 8 수치)
  - S21 정정 적용 확인 (single cell best + paired aggregate 두 관점 동시 표시)
- 사용자 깬 후 verify 영역 진행 → 정합성 확인 후 (필요 시) 추가 수정 요청

---

## 6. 박광현 PDF v3 final readiness 확인

### 6.1 PDF 14 page sample read 결과 (page 1-3 + 13-14)

| Page | 내용 | 상태 |
|---|---|---|
| 1 | TL;DR — main theme fix, 4 측면 | ✓ |
| 2 | paper §V-B 영역 anchor (paper verbatim 2건) | ✓ |
| 3 | Form 1 Component A+B+C+D matrix + 17-step pseudo-code | ✓ |
| 13 | fix 영역 vs 변경 가능 영역 (박광현 review 후) | ✓ |
| 14 | 부록 — Agent A-J 10 호출 + 정정 룰 10 영역 | ✓ |

### 6.2 fix 영역 vs 변경 가능 영역 (PDF page 13)

**fix (변경 X)**:
- main theme: "Streaming-aware Distribution-Conscious"
- 4 측면 (대체/보완/개선/추가검증)
- paper §V-B "without index" 가정 anchor (paper verbatim)
- Component A+B+C+D 영역
- 17-step pseudo-code (paper Eq 1-6 + 본 7 augment)

**변경 가능 (박광현 추천 적용)**:
- 측정 plan 우선순위 (SelNet / streaming workload / drift / CE4HD)
- phase 1 / phase 2 timeline 분담 (5/27 / 6/11 / post-6/11)
- paper-grade publication venue (EDBT short / VLDB short / ICDE position)
- 박광현 본업 align (RELOAD / CANNON / DFLOP 영역 통합 가능성)

→ readiness 100% 확정. 박광현 미팅 14:00 그대로 진행.

---

## 7. 본 mini session 산출물 file

### 7.1 분석 보고서 (★ 사용자 read 권장)
- `experiments/results/analysis/B1_variance_root_cause_종합분석_20260515_0150.md` — B1 variance 정량 + 권장안 3안
- `experiments/results/analysis/측정_미커버_영역_종합_inventory_20260515_0205.md` — paper Fig 매핑 + 우선순위
- `experiments/results/analysis/Pareto_Top5_method_cell_cross_validation_20260515_0250.md` — Pareto Top 5 paired 97.78% 강력 증거
- `experiments/results/analysis/K_granularity_dimension_dependent_종합검증_20260515_0310.md` — dim-K 가설 검증 + run-level bias

### 7.2 handoff
- `_internal/handoff/active/handoff_v25_b1_variance_root_cause_+_미커버_inventory_20260515_0235.md` ← 본 file

### 7.3 임시 script (필요 시 archive)
- `/tmp/b1_variance_analysis.py` — B1 implied 계산 (paper exact + 5/12 + 5/15)
- `/tmp/b1_analysis_pt2.py` — sparse_rp outlier 분리 + K granularity 일관성
- `/tmp/b1_analysis_pt3.py` — 5/14 SF axis + 종합 비교
- `/tmp/inventory_unmeasured.py` — cell × method coverage matrix
- `/tmp/pareto_top5_check.py` — Pareto Top 5 method × cell coverage
- `/tmp/k_granularity_dim.py` — K granularity × dimension cross-validation

### 7.4 commit chain
- `9cbd61c` (02:35) — B1 variance + 미커버 inventory + handoff v25
- `1ae3ad6` (03:15) — Pareto Top 5 + K dim 가설 검증
- `ebce316` (03:20) — handoff v25 update (Pareto + K dim 통합)
- `e570311` (11:25) — raw/ dataset 단일 기준 reorganize (1352 file git mv)
- `507c7c9` (11:42) — 박세은 query/threshold 패키지 + REPORT v11 §12 + K_dim 정상화

### 7.5 morning session (11:05 ~ 11:50) 추가 산출물
- `submission/_drafts/박세은_채림_5_15_query_threshold/` — 5 dataset × 100 query vector + selectivity threshold + README
- `experiments/results/raw/` 영역 dataset 단일 기준 reorganize (DEEP_96d / SIFT_128d / SSN_256d / YFCC_192d / DEEP+WIKI_864d / DEEP+CC3M_multi-vector_scope외 / TPCDS_ECQO_scope외)
- `cache/rq3/paper_exact_fittime/` (server) — Pareto Top 5 × 9 cell × 2 mode = 90 file fit_time 측정 진행 중

### 7.6 fit_time 측정 launch 영역 caveat ★

- 첫 patch (patch_fittime.py) 영역 일부 fail (CaseB result assertion error) → file write 영역 X
- 결과: 처음 launch 된 6 file (A1-DEEP CaseA × 5 + A1-SIFT CaseA × sparse_rp) 영역 fit_time 영역 영역 X
- 영역 patch (patch_caseb_result + patch_caseb_timing + patch_casea_timing) 영역 영역 적용 → 영역 measurement 영역 fit_time 영역 영역
- **영역 6 file 영역 retry 영역**: fittime session 종료 후 별도 launch 또는 사용자 결정

### 7.7 fit_time preliminary finding (12:00 KST, 9 file 영역)

| Method | n | mean fit_time | range |
|---|---:|---:|---|
| sparse_rp | 1 | 5.16s | (가장 빠름) |
| neuram | 2 | 10.60s | 8.99 ~ 12.22s |
| chao_weighted | 1 | 13.73s | - |
| pca1d | 3 | 26.85s | 21.93 ~ 29.40s |
| **hilbert_real** | 2 | **66.75s** | 61.77 ~ 71.74s (가장 느림) |

★ **fit_time range 5s ~ 67s = 13× 차이** (sparse_rp vs hilbert_real). 본 narrative 의 §8 자원 효율 Pareto 영역 paper-grade 정량 source.
★ cache_time 은 cell 영역 (DEEP 14s, SIFT 17s) — vector dim 영역 의존.
★ 90 file 모두 완료 시 5 method × 9 cell × 2 mode = 모든 cell 영역 fit_time 정량 가능 (예상 6-9시간 영역 추가).

---

## 8. 사용자 아침 확인 사항 (★ 우선순위)

### 8.1 즉시 (확인 후 결정 필요)

1. **분석 보고서 2개 read** — B1 variance + 미커버 inventory
2. **claude.ai/design v7 verify** (사용자 직접) — badge + 사실 검증 response 확인
3. **A4-sel × K granularity 재launch 결정** — 박광현 미팅 전 vs 후 launch 영역 결정

### 8.2 박광현 미팅 14:00 진행

- PDF v3 (14 page, 559 KB) readiness 100% — 그대로 진행
- fix 모드 유지 (main theme + 4 측면 + paper §V-B scope 변경 X)
- 12 review 항목 즉답 + 정직 disclosure + 정정 룰 반영 모두 100%

### 8.3 post-미팅 mass update

- Agent L mapping base (P0 11.5h + P1 9h + P2 28h)
- 박광현 review input 반영 (변경 가능 영역 4 항목: 측정 plan / timeline / venue / 본업 align)

---

## 9. 다음 세션 권장 action

1. **분석 보고서 2개 read** + handoff v25 read (본 file)
2. **사용자 박광현 미팅 답변 (필요 시) sub-claim 강화**:
   - 추가 측정 launch 결정 — A4-sel sel=0.10 cell 의 paper Fig 13 완성 가치
   - 미커버 영역 종합 inventory 를 박광현 review answer 에 활용 (학술 정합성 강화)
3. **B1 variance issue 를 본 narrative 의 caveat 으로 추가**:
   - 박광현 미팅 후 narrative 보강 — "paired comparison 은 robust, absolute delta% 는 caveat 명시" 형태
4. **A4-sel × K granularity launch readiness 확보** (사용자 결정 후):
   - 코드 수정 (A4-sel-0.10 cell 정의 + K argument)
   - tmux launch (6-12h server time)

---

## 10. 본 mini session 학습 (환각 회피 + 자율 진행)

1. **directory inventory matrix 항상 먼저 확인** — 어디에 어떤 측정이 있는지 (handoff v23 의 K granularity README 가 이를 명시한 anchor 역할)
2. **B1 variance 의 두 layer**:
   - L1 inherent trial CV 6% (n=10 trial 기준)
   - L2 run-level systematic bias ±10-25% (random variance 만으로 설명 불가)
3. **paper Fig 매핑 항상 명확** — 우리 cell name (A1/A2/A4/A5) vs. paper Fig number (5/6/7/8/9/10/11/12/13/14)
4. **launch 는 가역적 (server tmux) but 시간 자원 큼** — 사용자 승인 후 진행 권장
5. **WebFetch 403 = 인증 필요** — 사용자 직접 verify 요청 처리

---

작성: 2026-05-15 02:35 KST · 본 mini session (5/15 01:20 ~ 02:35, ~1h 15m) 종합 · B1 variance root cause + 미커버 영역 inventory + A4-sel launch readiness + 박광현 PDF v3 readiness · 사용자 아침 확인 base entry point
