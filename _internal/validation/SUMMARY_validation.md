# 검증 종합 — 5/10 별도 세션 (메인 영향 0)

_생성_: 2026-05-10 KST
_세션_: 별도 검증 세션 (메인 측정 세션과 완전 분리)
_입력_: `/Users/hyunbin/Capstone/_internal/validation/data/` (310 JSON + 5 CSV, server에서 read-only rsync)
_검증 대상_: 메인 분석 스크립트 `analyze_paper_exact.py`, REPORT.md, handoff §1.4 표

---

## 0. TL;DR

| Layer | 항목 | 판정 |
|---|---|---|
| **1. paired Δ%** | 공식 정확성 (per-trial Δ%, trial pairing, inf/nan handling) | **PASS** |
| **2. Wilcoxon + BH-FDR** | scipy.stats.wilcoxon + BH-FDR 구현 | **PASS** (statsmodels max diff 1.11e-16) |
| **3. narrative #1 RQ1/RQ2** | paper sel {0.01, 0.10} 격차 | **PASS** |
| **3. narrative #2 paper Fig 12** | 1.69 재현 | **WARN** (A4-sel 영역 분리 필요) |
| **3. narrative #3 CaseA outperform** | 통계 유의 outperform 비율 | **WARN** (15/197=7.6%, lsh/RP/sobol 43건 worse signif) |
| **3. narrative #4 CaseB outperform** | ensemble 증강 효과 | **PASS** (46/103=44.7% one-sided signif) |
| **3. narrative #5 ordering** | CaseB < CaseA < B1 | **PARTIAL** |
| **4. cherry-picking** | handoff §1.4 표 method-mean 일치 | **WARN** (3/9 일치, 6건 정정 필요) |
| **4. paper 1.69 비교** | A4-sel inflate 효과 | **CRITICAL FIX** (전체 +24.5% vs Fig 12 영역 -4.3%) |

**최우선 권장**:
1. **paper 1.69 비교 정정** — 메인 REPORT.md '+25.5%'를 'Fig 12 영역 8 cells = -4.3% (paper와 거의 일치), A4-sel은 Fig 13 영역으로 분리'로 정정 → narrative 강화 (paper와 일치하는 fact)
2. **handoff §1.4 표 정정** — method-mean으로 통일 (cherry-pick 의심 회피)
3. **CaseA narrative caveat 추가** — '40% method outperform, but lsh/RP/sobol 43건 worse signif (YFCC 192d/SSN 영역)'

---

## 1. Layer 1 — paired Δ% 계산 정확성

### 1.1 검증 결과
- **trim_mean stored ↔ recomp**: max Δ = 0 (paper p.7 lowest 1 + highest 1 제외 공식 정확 일치) → **PASS**
- **paired Δ% formula**: `mean((CaseA - B1) / B1 × 100)` per-trial — 메인 구현 정확
- **trial pairing**: B1 trial i ↔ CaseA trial i (동일 seed `trial_idx*13+7`) 확인
- **inf/nan handling**: `np.isfinite` mask, n_finite count 기록 — 정확
- **alternative formulation 비교**: per-trial mean vs aggregate mean(CaseA)/mean(B1) — 차이 평균 ~0.5%p (per-trial 분포 skew의 자연스러운 산물)

### 1.2 발견 — narrative 영향
- **bootstrap 95% CI에서 0 포함된 mean<0 건수**: **82/161** = 51% — 절반은 CaseA-better 통계적으로 불확실
- **|Δ%|>100% extreme outliers**: 19건 (lsh/RP/sobol on A1-SSN/A2-Fig7 — YFCC 192d 분포 부적합)

### 1.3 출력
- `paired_delta_audit.md`
- `audit_data_paired.csv` (downstream Layer 2/3/4 입력)

---

## 2. Layer 2 — Wilcoxon + BH-FDR

### 2.1 검증 결과
- **n=10 paired Wilcoxon discrete p-value**: 가능한 최소 two-sided p = 0.0020. 효과크기 -10% 이하면 power 부족 위험
- **BH-FDR 자체 구현 vs statsmodels**: max diff = **1.11e-16** (floating point) → **PASS**
- **two-sided p_adj < 0.05**: **109/300건**
- **one-sided p_adj < 0.05** (CaseA-better hypothesis): **61/300건**
- **차이 −48건**: two-sided에서 signif but one-sided not signif → outliers (lsh/RP/sobol)이 *worse* 방향 signif

### 2.2 narrative 영향
- 'CaseA outperform 통계 유의'은 **109건이 아니라 61건** (one-sided)
- 109 - 61 = 48건은 method가 worse 방향 signif → narrative caveat 필요
- **권장**: one-sided alternative="greater" 사용 (방향성 명확)

### 2.3 출력
- `wilcoxon_bh_fdr_audit.md`
- `audit_data_wilcoxon.csv`

---

## 3. Layer 3 — 5단계 narrative consistency

### 3.1 Step 1 RQ1/RQ2 — **PASS**

**RQ1** (random vs KM20 5% 격차):
- DEEP sel=0.01: bernoulli 1.7479 vs km20 1.6373 → gap **+6.76%** ✓
- SIFT sel=0.01: gap **+1.97%** (paper 5% 보단 낮음, narrative 'around 5%' 범위 내)
- DEEP sel=0.10: gap **+3.95%** ✓
- SIFT sel=0.10: gap **+9.45%** ✓

**RQ2** (Prop < Equal < Bernoulli, 9% 격차):
- DEEP sel=0.01: ordering OK, gap(bern vs prop) **+10.32%** ✓
- SIFT sel=0.01: ordering OK, gap **+4.16%** (9% 보단 낮음)
- DEEP sel=0.10: ordering OK, gap **+4.31%**
- SIFT sel=0.10: ordering OK, gap **+10.21%**

### 3.2 Step 2 — paper Fig 12 1.69 재현 — **WARN (영역 분리 필요)**

| 영역 | n cells | mean qe_trim | paper 1.69 vs |
|---|---|---|---|
| Fig 12 (정상 selectivity) | 8 | 1.6180 | **-4.3%** (paper 거의 일치) |
| Fig 13 (sel=0.001) | 1 (A4-sel) | 5.9856 | (Fig 13 영역, Fig 12 비교 부적절) |
| 9 cells 모두 (현재 REPORT) | 9 | 2.1033 | +24.5% (오해 소지) |

**문제**: 메인 REPORT.md '+25.5%'는 A4-sel inflate 효과. 정확한 paper Fig 12 비교는 -4.3% (paper와 거의 일치).

**정정 권장**: REPORT § 1.1 표현을
> "9 cells qe_median range: 1.584 ~ 5.975, mean 2.121 (paper 1.69 +25.5%)"
→
> "Fig 12 영역 8 cells: mean qe_trim 1.618 (paper 1.69 −4.3%, 거의 일치). A4-sel cell (sel=0.001)은 paper Fig 13 영역으로 별도 표기."

### 3.3 Step 3 — CaseA outperform 검증 — **WARN**

- 측정 197건 (cells × methods)
- one-sided p_adj<0.05 + Δ<0 (실제 CaseA-better signif): **15건 (7.6%)**
- two-sided + Δ>0 (worsen signif): **43건** ← narrative caveat

**method별 win count** (one-sided p_adj<0.05):
- minibatch_partial: 4/9 cells (best)
- faiss_ivf: 3/9
- banditucb1, kdtree, minibatch, opq, pq, sparse_rp, thompson_sampling, vinecopula: 1/9 each

**method별 worsen count**:
- lsh: 7/9, random_projection: 7/9, ccsketch: 4/9, sobol: 4/9
- ams_count_sketch, epsilon_net, kdpp, lp_bound, tucker: 3/9 each
- gmm: 2/9

**handoff §1.4 'minibatch_partial -7.41%' 검증**:
- 실제 cell-mean: **−10.17%** (min −21.73% A1-SIFT, max +3.06% A4-sel)
- −7.41% 은 method-mean 아니고 best도 아님 → 정정 필요

### 3.4 Step 4 — CaseB outperform 검증 — **PASS**

- 측정 103건
- one-sided signif outperform: **46건 (44.7%)**
- worsen signif: 10건

**method별 CaseB win count**:
- hilbert/pca1d/reservoir: 7/9 cells (★ top tier)
- minibatch/sparse_rp: 6/9
- lsh/minibatch_partial: 4/9
- faiss_ivf/pq: 2/9, random_projection: 1/9

**handoff §1.4 'sparse_rp -7.11%' 검증**:
- 실제 cell-mean: **−8.13%** (min −11.62%, max −2.04%)
- 6/9 cells one-sided signif

### 3.5 Step 5 — ordering CaseB < CaseA < B1 — **PARTIAL**

12 common methods × 9 cells = 108 paired (cell × method) checks:
- CaseB가 CaseA보다 작음: **부분 성립** (ordering claim 일관성 검증 detail은 narrative_consistency_audit.md § 5)

### 3.6 YFCC 192d outliers narrative
- A1-SSN, A2-Fig7 (YFCC) cells에서 lsh/random_projection/sobol → q_error 수십~수만배
- 이건 **narrative-supporting fact** (low-discrepancy / random projection이 192d 분포에 부적합)
- but '대부분 outperform' framing은 위험 — 'lsh/RP/sobol은 YFCC 192d / SSN 영역 안 맞음' 명시 필요

### 3.7 출력
- `narrative_consistency_audit.md`

---

## 4. Layer 4 — Cherry-picking 검증

### 4.1 Δ% 전체 분포 (CaseA / CaseB)

| Bin | CaseA | CaseB |
|---|---|---|
| ≤−20% | 7 | 0 |
| −20~−10% | 17 | 6 |
| −10~−5% | 17 | 30 |
| −5~−1% | 25 | 36 |
| **CaseA outperform 전체** | **79/197 (40.1%)** | **82/103 (79.6%)** |

CaseB가 압도적으로 outperform 비율 높음 (79.6% vs 40.1%) → narrative #4/#5 강화.

### 4.2 handoff §1.4 표 정합성

| Method | Mode | handoff claim | mean across cells | 일치 |
|---|---|---|---|---|
| minibatch_partial | CaseA | -7.41% | **-10.17%** | NO (mean 더 좋음) |
| sparse_rp | CaseB | -7.11% | **-8.13%** | NO (mean 더 좋음) |
| minibatch | CaseB | -7.17% | -8.14% | YES (1%p 이내) |
| hilbert | CaseB | -5.21% | **-8.30%** | NO |
| pca1d | CaseB | -4.75% | **-8.50%** | NO |
| reservoir | CaseB | -4.68% | **-8.05%** | NO |
| minibatch_partial | CaseB | -2.11% | **-5.79%** | NO |
| sparse_rp | CaseA | -0.98% | -1.44% | YES |
| minibatch | CaseA | -2.40% | -2.88% | YES |

**판정**: 9건 중 3건만 method-mean 일치, 6건은 다른 출처 (subset cells? trim 다름?). **method-mean 통일** 권장 — 우리 method가 더 outperform 표기.

### 4.3 paper 1.69 비교 (재확인)
- **CRITICAL FIX**: A4-sel 포함 시 +24.5%, Fig 12 영역만 -4.3%

### 4.4 method spread (cell variance) — 정직한 표기 권장

CaseA 분포 (handful 기준):
- minibatch_partial: mean −10.17%, std 8.16, range [−21.73%, +3.06%], spread 24.8
- gmm: mean +13.91%, std 19.02, range [−4.89%, +46.37%], spread 51.3
- lsh: mean +3953.28%, range [+0.70%, +22581.26%] — extreme outlier

→ 단일 number "method = -X%"로 표기 시 cell variance 가려짐. mean ± std + min/max 함께 표기 권장.

### 4.5 paradigm-level rollup (RQ3 framework)
**CaseA paradigm 평균 Δ%**:
- (audit_cherrypicking.md § 5 참조)
- P3-Streaming, P4-DimReduction이 outperform 우세

### 4.6 출력
- `cherrypicking_audit.md`

---

## 5. 메인 세션 권장 정정 (handoff back)

### 5.1 즉시 정정 (CRITICAL)
1. **REPORT.md § 1.1 paper Fig 12 비교**:
   - 변경 전: '9 cells mean: 2.121 (paper 1.69 +25.5%)'
   - 변경 후: 'Fig 12 영역 8 cells mean: 1.618 (paper 1.69 −4.3%, 거의 일치). A4-sel은 Fig 13 영역 (sel=0.001) 별도 표기.'
   - 이유: A4-sel 포함하면 paper 격차 inflate. 영역 분리하면 paper와 거의 일치 → narrative #2 강화.

2. **handoff §1.4 표 method-mean 통일**:
   - 6건 cell-mean과 다른 숫자 → 정확한 method-mean으로 통일
   - 예: minibatch_partial CaseA = **−10.17%** (handoff −7.41% 정정)
   - 이유: cherry-pick 회피, narrative 정직성

3. **CaseA narrative caveat 추가**:
   - '40% method outperform' but 'lsh/RP/sobol 43건 worse signif (YFCC 192d/SSN 영역 부적합)' 명시
   - one-sided p_adj<0.05 outperform 실제 15/197건 (7.6%)

### 5.2 narrative 강화 (PASS, 그대로 가능)
- RQ1/RQ2 paper 격차 narrative ✓
- CaseB ensemble 46/103 = 44.7% one-sided signif ✓ — 메인 narrative #4 그대로 강화
- B1 trial pairing + paper trim mean 공식 ✓ — 정확

### 5.3 추가 권장
- one-sided Wilcoxon으로 다시 통계 (메인은 two-sided)
  - power +48건 conservative하게 정직 narrative — 그러나 two-sided로 109건 보고 후 'one-sided 환산 시 61건' 추가 표기도 OK
- effect size 같이 표기 (Hedges' g 또는 Cliff's δ) — n=10 small sample power 한계 보완
- A4-sel cell 결과는 narrative에서 별도 처리 (paper Fig 13 영역, sel=0.001 inherently 큰 q_error)

---

## 6. 산출 파일 list

```
_internal/validation/
├── audit_paired_delta.py           # Layer 1 코드
├── audit_wilcoxon_bh_fdr.py        # Layer 2 코드
├── audit_narrative_consistency.py  # Layer 3 코드
├── audit_cherrypicking.py          # Layer 4 코드
│
├── paired_delta_audit.md           # Layer 1 결과
├── wilcoxon_bh_fdr_audit.md        # Layer 2 결과
├── narrative_consistency_audit.md  # Layer 3 결과
├── cherrypicking_audit.md          # Layer 4 결과
│
├── audit_data_paired.csv           # Layer 1 데이터
├── audit_data_wilcoxon.csv         # Layer 2 데이터
│
├── SUMMARY_validation.md           # 본 파일
│
└── data/                           # server rsync (read-only copy)
    ├── *.json (310건)
    ├── *.csv (5건)
    └── REPORT_paper_exact.md       # 메인 결과 (read-only)
```

---

## 7. 메인 세션 영향 0 확인

- ❌ 메인 측정 데이터 변경: **0건** (server 데이터 read-only rsync)
- ❌ 메인 분석 스크립트 변경: **0건** (`analyze_paper_exact.py` 등 server-side 미접촉)
- ❌ 메인 tmux 세션 영향: **0건** (별도 SSH 명령만 실행)
- ❌ PG/cache/NPY 변경: **0건**
- ✅ 별도 결과 작성: 본 디렉토리 (`_internal/validation/`)에만

---

_검증 세션 종료 — 메인 세션이 본 SUMMARY 반영 (정정 또는 강화) 권장._
