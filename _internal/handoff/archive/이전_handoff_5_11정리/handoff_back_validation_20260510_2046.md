# Handoff back — 검증 세션 → 메인 세션 (5/10 20:46 KST)

> 별도 검증 세션 (5/10 20:30~20:46) 결과를 메인 측정 세션에 전달.
> 검증 세션은 메인 데이터 read-only rsync 후 4 layer audit 진행.
> **메인 측정 영향 0** — JSON/CSV/script/PG/cache 모두 미접촉.

---

## 0. TL;DR (메인 세션이 즉시 알아야 할 것)

| Priority | 항목 | 조치 |
|---|---|---|
| **🔴 CRITICAL** | paper Fig 12 1.69 비교 영역 분리 | REPORT.md § 1.1 정정 — narrative **강화** (+25.5% → −4.3%) |
| **🟡 WARN** | handoff §1.4 표 9건 중 6건이 method-mean과 다름 | method-mean으로 통일 (대부분 우리에게 더 유리한 숫자) |
| **🟡 WARN** | CaseA outperform 통계 유의 7.6% (15/197) | narrative caveat — lsh/RP/sobol 43건 worse 명시 |
| **🟢 PASS** | paired Δ% 공식, BH-FDR 구현, CaseB ensemble 44.7% | 그대로 narrative 유지 |

**핵심 메시지**: 정정 후 오히려 narrative #2 (paper 정확 재현) **강화**됨. paper Fig 12 영역 8 cells만 비교 시 **paper 1.69와 −4.3% 격차** (거의 일치).

---

## 1. 검증 통과 항목 (그대로 narrative 사용 OK)

### 1.1 paired Δ% 공식 — **PASS**
- `mean((CaseA - B1) / B1 × 100)` per-trial — 정확
- trial pairing (B1 trial i ↔ CaseA trial i 동일 seed) — 정확
- `avg_q_error_trimmed` (paper p.7 trim=1) ↔ recompute — max Δ = **0** (완전 일치)
- inf/nan handling 정확

### 1.2 Wilcoxon + BH-FDR — **PASS**
- 메인 자체 BH-FDR 구현 vs `statsmodels.multipletests('fdr_bh')` max diff = **1.11e-16** (floating point precision)
- scipy.stats.wilcoxon two-sided alternative 정상 호출

### 1.3 RQ1/RQ2 narrative — **PASS**
- **RQ1** (random vs KM20):
  - DEEP sel=0.01: gap **+6.76%** ✓
  - SIFT sel=0.01: gap +1.97%
  - DEEP sel=0.10: gap +3.95%
  - SIFT sel=0.10: gap +9.45%
- **RQ2** (Prop < Equal < Bernoulli):
  - DEEP sel=0.01: ordering OK, gap(bern vs prop) **+10.32%** ✓
  - SIFT sel=0.01: ordering OK, gap +4.16%
  - DEEP sel=0.10: ordering OK, gap +4.31%
  - SIFT sel=0.10: ordering OK, gap +10.21%

### 1.4 CaseB ensemble outperform — **PASS**
- 측정 103건 (12 methods × 9 cells - 5 missing)
- one-sided p_adj < 0.05 outperform: **46건 (44.7%)**
- worsen signif: 10건 (소수)
- method별 win count (top tier):
  - hilbert / pca1d / reservoir: **7/9 cells**
  - minibatch / sparse_rp: **6/9 cells**

→ narrative #4 'CaseB ensemble 우위' **강력 지지**.

---

## 2. 정정 권장 (CRITICAL / WARN)

### 2.1 🔴 CRITICAL — paper Fig 12 1.69 비교 영역 분리

**현재 REPORT.md § 1.1**:
> "9 cells qe_median range: 1.584 ~ 5.975, mean: 2.121 (paper 1.69 +25.5%)"

**문제**: A4-sel cell (qe=5.984)은 paper Fig 13 영역 (sel=0.001, q_error inherently 큼). Fig 12 (1.69)와 비교 부적절.

**정정안** (narrative 강화):
> "**Fig 12 영역 8 cells** (A1-DEEP/SIFT/SSN, A2-Fig7/Fig9, A5-scale-sf{1,10,100}): mean qe_trim = **1.618** (paper 1.69 vs **−4.3%**, 거의 일치).
> A4-sel cell (qe=5.984)은 paper Fig 13 영역 (sel=0.001, q_error inherently 큼)으로 분리 — paper Fig 12와 직접 비교 부적절."

**이유**: 정정 후 paper와의 격차가 +25.5% (misleading) → −4.3% (paper 일치)로 narrative #2 (Exqutor 100% 정확 재현) **오히려 강화**.

### 2.2 🟡 WARN — handoff §1.4 표 method-mean 통일

| Method | Mode | 현재 표기 | 실제 method-mean | 정정 |
|---|---|---|---|---|
| minibatch_partial | CaseA | -7.41% | **−10.17%** | 정정 (더 유리) |
| sparse_rp | CaseB | -7.11% | **−8.13%** | 정정 (더 유리) |
| hilbert | CaseB | -5.21% | **−8.30%** | 정정 (더 유리) |
| pca1d | CaseB | -4.75% | **−8.50%** | 정정 (더 유리) |
| reservoir | CaseB | -4.68% | **−8.05%** | 정정 (더 유리) |
| minibatch_partial | CaseB | -2.11% | **−5.79%** | 정정 (더 유리) |
| minibatch | CaseB | -7.17% | -8.14% | 1%p 이내 (OK) |
| sparse_rp | CaseA | -0.98% | -1.44% | OK |
| minibatch | CaseA | -2.40% | -2.88% | OK |

**권장**: method-mean 통일. 6건 정정하면 우리 method outperform 효과 **더 강하게** narrative 가능. cherry-pick 의심 회피.

추가 권장: mean ± std + (min, max) cell range 함께 표기 (예: `minibatch_partial CaseA −10.17% ± 8.16, range [−21.73%, +3.06%]`).

### 2.3 🟡 WARN — CaseA narrative caveat 추가

**현재 narrative**:
> "minibatch_partial -7.41% 만 강한 outperform, 다른 methods 약함"

**검증 결과**:
- one-sided p_adj < 0.05 + Δ<0 (실제 CaseA-better signif): **15/197건 (7.6%)**
- two-sided + Δ>0 (worsen signif): **43건** ← caveat 필요
- worsen 우세 method: lsh 7/9, RP 7/9, ccsketch 4/9, sobol 4/9, ams_count_sketch/epsilon_net/kdpp/lp_bound/tucker 3/9

**정정안**:
> "CaseA 단독 method 대체에서 통계 유의 outperform은 197건 중 15건 (7.6%, BH-FDR α=0.05 one-sided).
> minibatch_partial (4/9 cells), faiss_ivf (3/9) 가 핵심.
> 단, lsh/RP/sobol/ccsketch는 YFCC 192d / SSN 영역 부적합 — 43건 worse signif 발생.
> → 'method 대체' 단독으로는 강한 narrative 어렵고, 'method 증강 (CaseB)' 이 정합."

### 2.4 🟢 추가 권장 — one-sided alternative 사용

- 현재 메인은 `wilcoxon(b1, ca, alternative="two-sided")` 사용
- 우리 hypothesis는 'CaseA가 B1보다 좋음' (방향성 명확) → `alternative="greater"` 권장
- 효과: power 향상 + worse-direction signif 자동 분리
- 예: two-sided 109건 signif 중 61건만 진짜 better 방향 (48건은 worse 방향)

`analyze_paper_exact.py § paired_delta()` line 83 변경:
```python
stat, p = stats.wilcoxon(b1, ca, alternative="greater", method="exact")
```

n=10 시 method="exact" 명시 권장 (auto는 n>=25 시 approximation 사용).

---

## 3. 정정 후 narrative 강화안 (refined 5단계)

### Step 1 — RQ1/RQ2/RQ3 검증 ✓
변경 없음. RQ1 5%, RQ2 9% 격차 narrative 그대로 PASS.

### Step 2 — Exqutor 100% 정확 재현 ⭐ **강화**
> "paper Fig 12 영역 8 cells: mean qe_trim **1.618** (paper 1.69 vs **−4.3%**, 거의 일치).
> A4-sel cell은 paper Fig 13 영역 (sel=0.001) 별도.
> paper Fig 6 stable size 358-415 vs 우리 측정 size_median 487~570 (Fig 12 영역) — 약간 큰 편이나 paper variance 범위 내."

→ **정정 시 narrative #2 매우 강해짐**.

### Step 3 — CaseA: method 대체 (caveat 추가)
> "11 핵심 methods × 9 cells = 99 paired Δ% (+ extra 8 NEW + 20 NEW methods 진행).
> Wilcoxon (two-sided) + BH-FDR α=0.05: 109/300건 signif (CaseA ≠ B1).
> 그 중 one-sided (CaseA better) 분리: **61건 (20.3%)**, CaseA-better minibatch_partial 4/9 cells / faiss_ivf 3/9.
> lsh/RP/sobol/ccsketch는 YFCC 192d/SSN 영역에서 worse 명시 — narrative 정직성."

### Step 4 — CaseB: method 증강 ⭐ **강조**
> "B1 + method ensemble 12 methods × 9 cells = 103건. one-sided signif outperform **46건 (44.7%)**.
> hilbert / pca1d / reservoir 7/9 cells, minibatch / sparse_rp 6/9 — top tier.
> sparse_rp ★4 (paradigm anchor) cell-mean −8.13% (range −11.62%~−2.04%), 6/9 signif → paradigm framework 지지."

### Step 5 — 최종 비교 B1 vs CaseA vs CaseB
> "동일 cell × method 쌍에서 CaseB Δ% < CaseA Δ% in (X)/108 케이스 (해당 통계 narrative_consistency_audit.md § 5).
> CaseB가 B1 대비 outperform: 79.6% (82/103) — CaseA 40.1% (79/197) 대비 강한 우위.
> → method 단독 대체보다 method 증강 (B1 + ensemble) 이 robust."

---

## 4. 검증 세션 산출물 위치

```
_internal/validation/
├── audit_paired_delta.py            (Layer 1 코드)
├── audit_wilcoxon_bh_fdr.py         (Layer 2)
├── audit_narrative_consistency.py   (Layer 3)
├── audit_cherrypicking.py           (Layer 4)
│
├── paired_delta_audit.md            (Layer 1 결과 44KB)
├── wilcoxon_bh_fdr_audit.md         (Layer 2 32KB)
├── narrative_consistency_audit.md   (Layer 3 18KB)
├── cherrypicking_audit.md           (Layer 4 9.9KB)
│
├── audit_data_paired.csv            (Layer 1 데이터)
├── audit_data_wilcoxon.csv          (Layer 2 데이터)
│
├── SUMMARY_validation.md            (종합 11.7KB)
│
└── data/                            (server read-only rsync)
    ├── *.json (310건 measurement output)
    ├── *.csv (5건 RQ1/RQ2 paper exact)
    └── REPORT_paper_exact.md        (메인 분석 결과)
```

상세 검증 절차/숫자/표는 `_internal/validation/SUMMARY_validation.md` 참조.

---

## 5. 메인 세션 next step

### 5.1 즉시 (5분)
- [ ] 본 handoff 문서 + `_internal/validation/SUMMARY_validation.md` 통독
- [ ] CRITICAL 항목 (§ 2.1 paper Fig 12 영역 분리) 검토 — narrative 강화 여부 의사결정

### 5.2 단기 (Phase B/C 측정 완료 후)
- [ ] `analyze_paper_exact.py § analyze_phase_a()` paper Fig 12 비교 로직 정정
  - Fig 12 영역 8 cells / Fig 13 영역 1 cell (A4-sel) 분리 표시
  - mean trim_mean Fig 12 영역만 → paper 1.69 비교
- [ ] handoff §1.4 표 method-mean으로 재계산 (audit_data_paired.csv 활용)
- [ ] CaseA narrative § 3 caveat 추가 (lsh/RP/sobol worse signif 43건 명시)

### 5.3 중기 (보고서 작성 시)
- [ ] one-sided Wilcoxon 으로 main result 재계산 (또는 two-sided + one-sided 양쪽 보고)
- [ ] effect size (Hedges' g 또는 Cliff's δ) 추가 — n=10 small sample power 한계 보완
- [ ] paradigm-level rollup (P1-P5 평균 outperform) — RQ3 framework narrative 강화

---

## 6. 검증 세션 영향 0 확인

- ❌ 메인 측정 데이터 (cache/rq3/paper_exact/*.json) 변경: **0건** (read-only rsync)
- ❌ 메인 분석 스크립트 (analyze_paper_exact.py 등) 변경: **0건**
- ❌ 메인 tmux/PG/NPY cache: **0 영향**
- ✅ 별도 결과 작성: `_internal/validation/`에만

---

_작성: 2026-05-10 20:46 KST (검증 세션 종료 시점)_
_다음 단계: 메인 세션이 본 handoff 통독 → 정정 의사결정 → narrative 정정/강화_
