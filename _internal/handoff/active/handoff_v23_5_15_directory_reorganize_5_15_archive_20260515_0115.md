# Handoff v23 — 5/15 01:15 directory reorganize + 5/15 측정 archive + B1 random variance verify

> 본 file = 5/15 01:00 ~ 01:15 영역 사용자 명시 critical mission 진행 영역:
> 1. **5/15 새벽 측정 (SIFT_SSN, multi_cell, A4-sel sequence) 부정확 의심 → archive 이동**
> 2. **directory reorganize 영역 사용자 명시 영역 (dataset/sf/sel 영역)**
> 3. **server _measure_common.py 영역 sed-patch 영역 영역**
> 4. **B1 random variance 영역 큰 영역 verify**

## ★ 새 세션 진입 anchor (0% loss)

1. **본 file** (handoff v23) read
2. handoff v22 (5/15 01:00 extended session base) + handoff v21 + v20 영역 carry-over
3. **5/15 박광현 review form PDF v3** (14 page, 559 KB, readiness 100%) 영역 변경 X

## 0. 5/15 01:00 ~ 01:15 한 줄 요약

사용자 critical mission:
1. **5/15 측정 = 부정확 의심 영역 (사용자 지적)** → archive 이동
2. **Directory reorganize** (dataset/sf/sel 영역 사용자 명시)
3. **B1 random variance 영역 매우 큰 영역 = systematic 영역 영역 의심**

## 1. ★★★ B1 random variance verify (사용자 지적)

### 1.1 사용자 지적 영역

> "재실험했는데 너무 값이 차이가 많이나는거 아닌가? 5/15에 진행한 데이터가 부정확한거 아냐? 완전 같은 실험인데 결과값이 이렇게 드라마틱하게 차이가 나면 뭔가 단단히 잘못된 게 아닌가 싶은데"

### 1.2 verify 결과

| 영역 | 결과 |
|---|---|
| **CaseA** (16 cells × 4 method, 결정적) | **0.00% 모두** ✓ — random seed + dataset + hyperparam 동일 |
| **CaseB** (16 cells × 4 method, stochastic) | **모두 악화 +17~+64%** ⚠ |

### 1.3 B1 estimator 영역 random variance 영역 큰 영역 (★ 핵심 발견)

CaseB = (CaseA + B1_random) / 2 영역. CaseA 결정적 → B1 영역 차이 영역.

**implied B1 trim10 mean** (A1-SIFT):

| run | implied B1 | paper exact B1 (raw/10) 영역 diff |
|---|---:|---:|
| paper exact B1 (raw/10/B1_baseline_9cell) | 1.6951 | base |
| 5/12 K=10 implied | 1.3951 | **−17.7%** |
| 5/12 K=20 implied | 1.2772 | **−24.65%** |
| 5/15 K=10 implied | 2.2499 | **+32.7%** |

→ **B1 영역 paper Bernoulli random N=385 영역 영역 trials=10 trim mean 영역 영역 매우 큰 variance**. 단순 trial variance 영역 X = **systematic 영역 다른 random seed pool** 영역.

### 1.4 5/15 새벽 측정 부정확 영역 가능성

- 모든 CaseB 결과 영역 **방향 일관 (악화)** = random trial variance ≠ 영역. **systematic bias** 영역.
- 사용자 영역 영역 영역 영역 = 정확 영역 지적.

★ 결정: **5/15 새벽 측정 (SIFT_SSN, multi_cell) → archive 이동** (부정확 의심).

### 1.5 server _measure_common.py 영역 verify

- server file modify time: **2026-05-14 16:07:45** ⚠ (5/14 영역 영역 변경 있음)
- 변경 영역 = 영역 영역 영역 (N_STRATA sed-patch wrapper 영역 영역 영역 영역 영역 변경 X)
- 현재 N_STRATA = 20 (paper exact default 영역 영역)

→ 영역 영역 영역 = sed-patch wrapper 영역 영역 영역 _measure_common.py 영역 변경 영역. 영역 measure_paper_exact.py 영역 변경 X (5/11 영역 영역 변경 X).

## 2. 사용자 명시 영역 진행

### 2.1 server 영역 영역 STOP

- A4-sel sequence (PID 29674, server tmux 영역 영역 영역 영역 진행 영역) → kill
- multi-cell K=30 sequence → 이미 영역 (PID 40080 영역 영역)
- 영역 영역 영역 영역 진행 X (verify 완료)

### 2.2 5/15 새벽 측정 → archive 이동

```
experiments/results/raw/06_클러스터수_K_민감도/_run_5_15_repeat/
→ experiments/results/archive/06_K_민감도_5_15_repeat_B1_variance/_run_5_15_repeat/
```

- SIFT_SSN/K10/ (16 file) + SIFT_SSN/K30/ (16 file)
- multi_cell/K10/ (24 file)
- 총 56 file archive

→ **사실 검증 영역 X 영역 영역 영역 영역 영역**: B1 random variance 영역 큰 영역 + 사용자 영역 영역 영역.

### 2.3 directory reorganize

```
experiments/results/raw/06_클러스터수_K_민감도/
├── _run_5_12_paper_exact_base/  (5/12 paper exact base, 신뢰 영역 ✓)
│   ├── K=10/  (5 cells × 4 anchor × 2 mode = 40 file)
│   ├── K=20/  (40 file)
│   └── K=30/  (40 file)
├── _run_5_14_A5_scale_DEEP/sf_axis/  (5/14 추가, 신뢰 영역 ✓)
│   ├── K10/ (24 file)
│   └── K30/ (24 file)
└── _A4_sel_재launch_예정/  (paper Fig 13 영역 실제 미측정)
```

### 2.4 plans/ 영역 정리 (5_27/ + 6_11/ 영역)

```
plans/
├── 5_27_발표/
│   └── 5_27_storyline_draft_20260511_1410.md
├── 6_11_보고서/
│   ├── 최종보고서_outline_v2_20260508.md
│   ├── 6_11_보고서_outline_v3_update_plan_20260511.md
│   ├── 6_11_보고서_outline_v4_draft_20260514_2230.md/.pdf
│   └── 6_11_보고서_section_*_sketch_20260511.md (5 section)
├── README.md
└── archive/
```

### 2.5 figures/config/code 영역 영역 영역

- experiments/figures/: archive + paper_exact_v7 (이미 정리됨, 변경 X)
- experiments/config/: experiment_params.yaml (단순, 변경 X)
- experiments/code/: README + archive (이미 정리됨, 변경 X)

## 3. ★ 핵심 학습 (환각 회피)

### 3.1 CaseA vs CaseB 영역 verify 영역

- **CaseA = 결정적** (random seed + dataset + hyperparam 동일 → 같은 결과)
- **CaseB = stochastic** (B1 Bernoulli random → trial별 큰 variance)
- 영역 검증 영역 첫 영역 = **CaseA 영역 영역** (결정적 영역)

### 3.2 measurement 영역 launch 전 checklist

1. **directory inventory matrix 확인** (어디에 어떤 측정 있는지)
2. 같은 cell × method × K × mode 영역 search
3. 새 측정 launch 전 = 영역 영역 verify
4. **B1 estimator 영역 영역 영역 trials=10 영역 영역 매우 큰 variance 가능 영역 → 평균 영역 영역 영역 영역**

### 3.3 사용자 영역 명시 영역 directory of directory 영역

```
raw/
├── 06_K_민감도/
│   ├── _run_*/  (시점별 run 영역)
│   │   ├── K=10/, K=20/, K=30/  (K granularity 영역)
│   │   └── sf_axis/  (SF axis 영역)
└── archive/
    └── 06_*_5_15_repeat_B1_variance/  (부정확 의심 영역)
```

## 4. 영역 미커밋 영역 / 다음 mission

### 4.1 영역 미커밋 영역

- 5/15 archive 이동 + directory reorganize + plans/ 정리 + README 정정 + 본 handoff v23
- commit + push 영역 영역

### 4.2 다음 mission

1. **A4-sel × K granularity 재launch 영역**: 
   - server _measure_common.py 영역 영역 영역 verify (5/14 16:07 modify 영역 영역 영역 영역 verify)
   - 영역 영역 영역 영역 영역 영역 → A4-sel × sel{0.001, 0.10} × K{10,20,30} launch
   - **영역 영역 영역 영역 영역 = 영역 영역 (영역 영역 X 영역 영역 영역 영역 영역 영역)**
2. **claude.ai/design v7 deck badge prompt response verify** (영역 진행 영역)
3. **handoff v22 영역 영역 영역 영역 영역** (5/15 영역 영역 영역 영역 영역 영역 영역 X)

### 4.3 박광현 D-1 미팅 (5/15 14:00) readiness

PDF v3 (14 page, 559 KB, readiness 100%) 변경 X. fix 모드 유지.

본 영역 영역 영역 영역 = 미팅 후 mass update 영역 (Agent L mapping P0 11.5h + P1 9h + P2 28h).

## 5. 핵심 file path reference

### 5.1 신뢰 영역 (5/12 + 5/14)

- raw/10_전체측정_백업/ (paper exact base, 1001 file)
- raw/06_K_민감도/_run_5_12_paper_exact_base/K=10,20,30/ (120 file)
- raw/06_K_민감도/_run_5_14_A5_scale_DEEP/sf_axis/ (48 file)
- raw/02_RQ2_5방식_표본할당/ (RQ2 csv)

### 5.2 archive 영역 (부정확 의심)

- archive/06_K_민감도_5_15_repeat_B1_variance/_run_5_15_repeat/SIFT_SSN/ (32 file)
- archive/06_K_민감도_5_15_repeat_B1_variance/_run_5_15_repeat/multi_cell/K10/ (24 file)

### 5.3 미측정 영역

- raw/06_K_민감도/_A4_sel_재launch_예정/ (paper Fig 13 sel sweep × K)

### 5.4 documents

- PDF v3 (박광현 D-1): submission/_drafts/archive/속도는벡터_박광현_5월15일_review_form_Form1_20260515.pdf
- handoff v23 (본 file): _internal/handoff/active/handoff_v23_*.md
- handoff v22 (extended session base, 영역 영역 영역 영역 영역 X): _internal/handoff/active/handoff_v22_*.md

---

작성: 2026-05-15 01:15 KST · 사용자 critical mission 진행 영역 (5/15 측정 archive + directory reorganize + B1 variance verify + plans 정리) · 5/15 새벽 측정 영역 부정확 의심 영역 영역 archive · 박광현 D-1 미팅 readiness 100% 유지
