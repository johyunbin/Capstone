# 06_클러스터수_K_민감도/ — K granularity 측정 결과 (5/15 reorganize)

## ★ 5/15 01:05 directory 재구성 (환각 회피 + 명확 분류)

기존 `K10/K20_default_paper/K30/` 영역 5/12 paper exact base measurement 영역 영역 영역, 5/14~5/15 추가 측정 영역 별도 분리.

### 새 구조

```
06_클러스터수_K_민감도/
├── _run_5_12_paper_exact_base/  ← 5/12 paper exact (5 cells × K=10/20/30)
│   ├── K=10/  (A1-DEEP, A1-SIFT, A1-SSN, A2-Fig7, A2-Fig9 × 4 anchor × 2 mode = 40 file)
│   ├── K=20/  (paper exact base, 40 file)
│   └── K=30/  (40 file)
├── _run_5_14_A5_scale_DEEP/     ← 5/14 추가 (A5-scale-sf{1,10,100})
│   └── sf_axis/
│       ├── K10/ (24 file)
│       └── K30/ (24 file)
├── _run_5_15_repeat/            ← 5/15 새벽 재측정 (trial variance verify)
│   ├── SIFT_SSN/  (A1-SIFT/SSN K=10/30, 32 file)
│   └── multi_cell/K10/  (A1-DEEP/A2-Fig7/A2-Fig9 K=10, 24 file)
└── _A4_sel_재launch_예정/        ← paper Fig 13 영역 (실제 미측정)
```

## 5/15 환각 verify 결과 (★ 중요)

5/15 새벽 추가 측정 영역 (`SIFT_SSN/`, `multi_cell/K10/`) 영역 = 기존 (5/12) 같은 cell 영역 재측정 영역.

### 비교 결과

| 영역 | 차이 |
|---|---|
| **CaseA** (16 cells × 4 method) | **0.00% 모두** ✓ — random seed 동일 + dataset 동일 + hyperparam 동일 (결정적) |
| **CaseB** (16 cells × 4 method) | +17~+64% 차이 — Bernoulli random sampling 영역 trial variance (CaseB = (CaseA + B1)/2, B1 random per trial) |

→ **두 run 모두 valid**. paper Bernoulli random sampling 영역 inherent trial variance 영역. **환각 X**, **잘못된 측정 X**.

→ statistical robust 분석 위해서는 **두 run pool** 가능 (총 trial 영역 ×2).

## 측정 영역 inventory matrix (★ 환각 회피 anchor)

| Cell | dataset | sf | sel | query | K=10 | K=20 | K=30 |
|---|---|---:|---|---|---|---|---|
| A1-DEEP | DEEP 96d | 100 | 0.01 | Q3/Q10/Q12 | _5_12 + _5_15/multi_cell | _5_12 | _5_12 |
| A1-SIFT | SIFT 128d | 100 | 0.01 | Q3/Q10/Q12 | _5_12 + _5_15/SIFT_SSN | _5_12 | _5_12 + _5_15/SIFT_SSN |
| A1-SSN | SimSearchNet 256d | 100 | 0.01 | Q3/Q9/Q10 | _5_12 + _5_15/SIFT_SSN | _5_12 | _5_12 + _5_15/SIFT_SSN |
| A2-Fig7 | YFCC 192d | 10 | 0.01 | Q3-Q20 (8) | _5_12 + _5_15/multi_cell | _5_12 | _5_12 |
| A2-Fig9 | DEEP+WIKI 864d | 10 | 0.01 | Q3-Q20 (8) | _5_12 + _5_15/multi_cell | _5_12 | _5_12 |
| **A4-sel-0.001** | DEEP 96d | 100 | **0.001** | Q3/Q10/Q12 | **⏳ 재launch** | **⏳ 재launch** | **⏳ 재launch** |
| A4-sel-0.01 | DEEP 96d | 100 | 0.01 | Q3/Q10/Q12 | (영역 raw/10 paper exact 영역 sub) | (raw/10) | (raw/10) |
| **A4-sel-0.10** | DEEP 96d | 100 | **0.10** | Q3/Q10/Q12 | **⏳ 재launch** | **⏳ 재launch** | **⏳ 재launch** |
| A5-scale-sf1 | DEEP 96d | 1 | paper thresh | Q3/Q5/Q20 | _5_14/sf_axis | (raw/10) | _5_14/sf_axis |
| A5-scale-sf10 | DEEP 96d | 10 | paper thresh | Q3/Q5/Q20 | _5_14/sf_axis | (raw/10) | _5_14/sf_axis |
| A5-scale-sf100 | DEEP 96d | 100 | paper thresh | Q3/Q5/Q20 | _5_14/sf_axis | (raw/10) | _5_14/sf_axis |

## 미측정 영역 (재launch)

★ **paper Fig 13 영역 A4-sel sel sweep × K granularity** = 실제 미측정:
- sel=0.001 × K{10,20,30} × 4 anchor × 2 mode = 24 file
- sel=0.10 × K{10,20,30} × 4 anchor × 2 mode = 24 file
- **총 48 file 재launch 예정**

→ `_A4_sel_재launch_예정/` 디렉토리 영역 server launch.

## 영역 학습 (환각 회피 원칙)

1. **항상 directory inventory matrix 영역 확인** (어디에 어떤 측정 영역 있는지)
2. **같은 cell × method × K × mode 영역 이미 측정 영역 영역 search**
3. **새 측정 launch 전 = 영역 영역 verify**
4. **trial variance vs 실제 다른 측정 영역 명확 구별**:
   - CaseA = 결정적 (random seed 동일 → 같은 결과)
   - CaseB = stochastic (B1 Bernoulli random → trial별 변동)

## 핵심 finding (5/14 SF axis 추가 측정 영역 base)

DEEP A5-scale (sf=1, CaseB ensemble Δ% vs Bernoulli baseline):

| Method | K=10 | K=20 | K=30 | best K |
|---|---:|---:|---:|---|
| sparse_rp | +77% (악화) | **−11.7%** | −8% | K=20 sweet |
| chao_weighted | −8% | **−14.1%** | −12% | K=20 sweet |
| hilbert_real | −6% | −11.0% | **−12.3%** | K=30 slight |
| hyperloglog | −6% | −10.2% | **−12.6%** | K=30 slight |

→ **dimension-dependent K best 잠정 가설** (DEEP 96d K=20 sweet vs SIFT/SSN 128/256d K=30 best). multi-cell + A4-sel 영역 결과 통합 영역 확정 영역.

## 출처

- 분석 file:
  - `experiments/results/analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md` (DEEP A5 SF axis)
  - `experiments/results/analysis/sift_ssn_k_granularity_20260515_0020.md` (SIFT/SSN, dimension-dependent K)
  - `experiments/results/analysis/multi_cell_k_granularity_K10_20260515_0050.md` (multi-cell K=10)
- handoff: `_internal/handoff/active/handoff_v22_*.md`

작성: 2026-05-15 01:05 KST · 환각 verify + directory reorganize + inventory matrix + 재launch 영역 명시
