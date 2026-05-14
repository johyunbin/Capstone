# multi-cell K granularity SF axis — K=10 1차 분석 (5/15 00:50)

> **분석 시점**: 2026-05-15 00:50 KST
> **데이터**: paper_exact_km10_multi_cell (24 file 회수 완료)
> **scope**: A1-DEEP (sf=100) + A2-Fig7 (YFCC sf=10) + A2-Fig9 (DEEP+WIKI cross sf=10) × 4 anchor × K=10 × CaseA/CaseB = 24 measurement
> **trigger**: 사용자 5/15 00:00 명시 "narrative v2 영역 필요한 실험 (K 빠진 값) 진행"
> **K=30 영역 진행 중** (server tmux multi_cell_k30, ETA ~01:00 KST)

---

## 0. B1 baseline (paper Bernoulli trim10 mean)

| Cell | sf | B1 trim10 |
|---|---:|---:|
| A1-DEEP | 100 | 1.6346 |
| A2-Fig7 (YFCC) | 10 | 1.6556 |
| A2-Fig9 (DEEP+WIKI cross) | 10 | 1.5407 |

---

## 1. K=10 결과 (paired Δ% vs B1)

### 1.1 A1-DEEP (sf=100, paper Fig 5/6 영역)

| Method | K=10 trim | Δ% vs B1 CaseA | K=10 trim | Δ% vs B1 CaseB |
|---|---:|---:|---:|---:|
| sparse_rp | 3.0297 | **+85.35%** ⚠ | 2.7099 | **+65.79%** ⚠ |
| chao_weighted | 1.6236 | −0.67% | 1.7964 | +9.90% |
| hilbert_real | 1.5390 | −5.85% | 1.7171 | +5.05% |
| hyperloglog | 1.6853 | +3.10% | 1.8306 | +11.99% |

### 1.2 A2-Fig7 (YFCC sf=10, paper Fig 7 영역)

| Method | K=10 trim | Δ% vs B1 CaseA | K=10 trim | Δ% vs B1 CaseB |
|---|---:|---:|---:|---:|
| sparse_rp | 2.8151 | **+70.03%** ⚠ | 2.6085 | **+57.56%** ⚠ |
| chao_weighted | 1.5355 | **−7.26%** | 1.7776 | +7.37% |
| hilbert_real | 1.6310 | −1.49% | 1.7337 | +4.72% |
| hyperloglog | 1.7292 | +4.44% | 1.8512 | +11.81% |

### 1.3 A2-Fig9 (DEEP+WIKI cross-table sf=10, paper Fig 9 영역)

| Method | K=10 trim | Δ% vs B1 CaseA | K=10 trim | Δ% vs B1 CaseB |
|---|---:|---:|---:|---:|
| sparse_rp | 3.3291 | **+116.07%** ⚠ | 2.3719 | **+53.95%** ⚠ |
| chao_weighted | 1.5690 | +1.83% | 1.6401 | +6.45% |
| hilbert_real | 1.5122 | −1.85% | 1.6313 | +5.88% |
| hyperloglog | 1.6001 | +3.86% | 1.7061 | +10.74% |

---

## 2. K=10 핵심 finding 4

### Finding 1 — sparse_rp K=10 강한 악화 (모든 multi-cell 일관)

| Cell | CaseA Δ% | CaseB Δ% |
|---|---:|---:|
| A1-DEEP (sf=100) | +85.35% | +65.79% |
| A2-Fig7 (sf=10) | +70.03% | +57.56% |
| A2-Fig9 (sf=10) | **+116.07%** | +53.95% |

→ sparse_rp K=10 = paper Fig 5/6/7/9 모두 영역 강한 악화. DEEP A5-sf100 영역 (+77%) + SIFT/SSN 영역 (+96/+61%) 영역 패턴 일관.

→ **paper 모든 single-table / multi-table / cross-table cell 영역** sparse_rp K=10 영역 = 비최적 영역 확정.

### Finding 2 — chao_weighted CaseA K=10 영역 약간 개선 (A2-Fig7 −7.26%)

A2-Fig7 (YFCC sf=10) CaseA chao_weighted K=10 = **−7.26%** 영역 = K=10 영역 일부 cell 영역 영역 strong 영역.

→ multi-table 영역 (tag-based YFCC) 영역 K=10 영역 영역 chao_weighted 영역 약함 영역 = 영역 multi-cell 영역 = single-table 영역 영역 다른 영역 K best 영역 가능성.

### Finding 3 — hilbert_real CaseA K=10 영역 ~flat (모든 cell)

hilbert_real CaseA K=10:
- A1-DEEP: −5.85%
- A2-Fig7: −1.49%
- A2-Fig9: −1.85%

→ hilbert_real K=10 영역 = 약간 개선 영역 (K-robust 영역 정합). K=20/K=30 영역 best K 영역 영역 영역 (K=30 영역 ETA ~01:00).

### Finding 4 — CaseB ensemble K=10 영역 모두 악화 (모든 cell × method)

| Cell | CaseB Δ% range |
|---|---|
| A1-DEEP | +5.05% (hilbert) ~ +65.79% (sparse_rp) |
| A2-Fig7 | +4.72% (hilbert) ~ +57.56% (sparse_rp) |
| A2-Fig9 | +5.88% (hilbert) ~ +53.95% (sparse_rp) |

→ K=10 + CaseB ensemble = 모든 cell × method 영역 paper baseline 영역 영역 악화. **K=10 + CaseB 영역 = 비최적 영역**.

→ K=20 (paper exact base) + K=30 (in-flight) 영역 영역 영역 영역 best K 영역.

---

## 3. K granularity SF axis 종합 (5/14 + 5/15)

### 3.1 모든 cell × K granularity 영역 (CaseB best K 영역)

| Cell | dim | sf | K=10 best | K=20 best | K=30 best |
|---|---:|---:|---|---|---|
| DEEP A5-sf1 (handoff v20) | 96 | 1 | X | sparse_rp/chao = K=20 sweet | hilbert/HLL = K=30 slight |
| DEEP A5-sf10 | 96 | 10 | X | K=20 sweet | K=30 slight |
| DEEP A5-sf100 | 96 | 100 | X | K=20 sweet | K=30 slight |
| **A1-SIFT** (본) | 128 | 100 | X | (K=20 base, raw/10) | K=30 best ★ |
| **A1-SSN** (본) | 256 | 100 | X | (K=20 base, raw/10) | K=30 best ★ |
| **A1-DEEP** (본) | 96 | 100 | X | (K=20 base, raw/10) | ⏳ K=30 in-flight |
| **A2-Fig7** (본) | 192 | 10 | (chao −7.26% CaseA only) | (K=20 base, raw/10) | ⏳ K=30 in-flight |
| **A2-Fig9** (본) | 96+768=864 | 10 | X | (K=20 base, raw/10) | ⏳ K=30 in-flight |

### 3.2 dimension-dependent K best 패턴 (잠정)

| Dim | Cells | K best 패턴 |
|---|---|---|
| 96d (DEEP) | A5-sf1/10/100 | K=20 sweet (sparse_rp/chao), K=30 slight (hilbert/HLL) |
| 128d (SIFT) | A1-SIFT | **K=30 best** (모든 method) |
| 256d (SSN) | A1-SSN | **K=30 best** (모든 method) |
| 192d (YFCC) | A2-Fig7 | K=30 영역 ETA ~01:00 |
| 864d (DEEP+WIKI cross) | A2-Fig9 | K=30 영역 ETA ~01:00 |

→ 잠정 패턴: **dimension ↑ → K=30 영역 우세**. (DEEP 96d K=20 vs SIFT/SSN 128/256d K=30). 영역 K=30 결과 (A1-DEEP / A2-Fig7 / A2-Fig9) 영역 영역 영역 정합 영역.

---

## 4. 정직 disclosure

1. 본 K=10 분석 영역 = K=20 (paper exact base) + K=30 (in-flight) 영역 영역 영역 영역. K=10 단독 영역 best K 영역 결정 불가
2. paper exact K=20 base 영역 raw/10_전체측정_백업 영역 = 본 영역 분석 X (carry-over). 영역 K=10/K=20/K=30 영역 paired 영역 = K=30 회수 + 영역 영역 통합 분석 영역 진행 영역
3. A2-Fig7 chao_weighted CaseA K=10 −7.26% 영역 = 영역 multi-table 영역 영역 영역 영역 강조 X (CaseB +7.37% 영역 영역 영역 영역 영역 영역 cherry-pick 영역)
4. dimension-dependent K best 패턴 영역 = **잠정** 가설. K=30 영역 (A1-DEEP/A2-Fig7/A2-Fig9) 영역 영역 영역 영역 영역 확정 영역

---

## 5. 다음 작업 (~01:00 KST 추정)

1. multi-cell K=30 결과 회수 (24 file) + 통합 분석 (K=10 vs K=20 base vs K=30, dimension-dependent K best 영역 확정)
2. A4-sel K=10/K=30 결과 회수 (16 file) + selectivity 영역 K granularity 영역 분석
3. handoff v22 final 작성 + 모든 결과 종합
4. claude.ai/design v7 S21 정정 verify + S15 영역 영역 정합 verify
5. 추가 측정 영역 (σ_j 직접 측정 + fit time SF=10/100 + Exqutor source verify) 영역 launch (post-sequence)

---

작성: 2026-05-15 00:50 KST · multi-cell K=10 회수 (24 file) + 1차 분석 + dimension-dependent K best 잠정 가설 + K=30 결과 영역 통합 분석 영역 예정
