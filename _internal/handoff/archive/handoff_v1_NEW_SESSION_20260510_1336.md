# Handoff v1 — NEW SESSION FINAL v3 (5/10 14:05 KST)

> 사용자 외출 + 5/10 14:03 최종 강한 지시:
> **"paper의 모든 항목 완전 똑같이 진행. 멋대로 추가/뺄 X. 단 하나라도 다르면 안 됨. 다음 세션 시작 시 paper 깨끗하게 정독하고 모든 변수 확정 후 작업 시작."**

---

## 0. 사용자 명시 결정 (최종)

### 0.1 5단계 narrative
1. RQ1, RQ2, RQ3 검증 (기존 결과 유지)
2. **Exqutor 100% 정확 재현** (paper 그대로, 멋대로 추가 X)
3. CaseA: 우리 method 대체 (sampling step replace)
4. CaseB: 우리 method 증강 (sampling step augment)
5. 최종 비교: B1 vs CaseA vs CaseB

### 0.2 narrative (이미지 5/10 13:47)
| 영역 | Exqutor | 한계 | 우리 공략 |
|---|---|---|---|
| Vector index 있음 | ECQO | 해당 없음 | — |
| Vector index 없음 + single-table | §V-B Adaptive Sampling | unstratified Bernoulli | distribution-aware augment |
| Vector index 없음 + multi-table | §V-B가 KNN 한정 | 결합 분포 못 활용 | multi 결합 분포까지 확장 |

**우리 contribution = augment within §V-B** (대체 X — §V-A ECQO 그대로).

### 0.3 강한 제약
- **paper 100% 정확 재현 — 단 하나라도 다르면 안 됨**
- **우리가 멋대로 추가한 항목 모두 폐기** (sel {0.05, 0.30, 0.50}, 100 random queries 등)
- 순차 실행 + 자원 max push (CPU 128 threads, GPU 0/2/3, RAM 1 TB)
- 1분 단위 monitor + stuck 즉시 처리

---

## 1. 다음 세션 첫 task — paper 정독 + 변수 확정 (작업 시작 전 필수)

### 1.1 Paper 깨끗하게 정독
- PDF: `/Users/hyunbin/Capstone/reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf`
- **모든 page (1-15) 정독** — 멋대로 skip X
- 특히 §V-B (sampling, p.7~8), §VI Datasets/Indexing/System setup (p.7), §VI-A (ECQO), §VI-B (sampling main, Fig 5/6), §VI-C (multi-vector, Fig 7-10), §VI-D (Discussion, Fig 11-14)

### 1.2 모든 변수 정확 추출 (Fig별 분리)

각 Fig의 정확한 setup 추출:

**Fig 5 (sampling main, §V-B reproduction)**:
- SF=100
- Datasets: DEEP, SIFT, SimSearchNet++
- Queries: 정확 추출 (Q3, Q9, Q10, Q12 인지 다른지)
- Selectivity: 1% (sampling-based threshold)
- 3 configurations: pgvector default / Exqutor fixed (N=385) / Exqutor adaptive

**Fig 6 (sample size convergence)**:
- SF=100
- Datasets: DEEP, SIFT, SimSearchNet++
- Iteration 0~1000
- Adaptive trace: DEEP ~360, SIFT ~410, SSN ~355
- Fixed: 385 dashed

**Fig 7 (YFCC tag filtering)**:
- SF=10
- partsupp + ps_tag
- 8 TPC-H queries (Q3, Q5, Q8, Q9, Q10, Q11, Q12, Q20)

**Fig 8 (DEEP+WIKI partsupp)**:
- SF=10
- partsupp 4-way (DEEP + WIKI 둘 다 partsupp)
- 8 TPC-H queries

**Fig 9 (DEEP+WIKI cross-table)**:
- SF=10
- partsupp[DEEP] × part[WIKI]
- 8 TPC-H queries

**Fig 10 (TPC-DS)**:
- SF=10
- DEEP
- 7 TPC-DS queries (Q7, Q12, Q19, Q20, Q42, Q72, Q98)

**Fig 13 (selectivity ablation)**:
- SF=100, DEEP
- 3 selectivities: 0.1%, 1%, 10%
- 3 queries: Q3, Q10, Q12

**Fig 14 (scalability)**:
- DEEP
- SF=1, 10, 100
- 3 queries: Q3, Q5, Q20

### 1.3 변수 확정 (모두 paper에서 verbatim)

- **Datasets**: 5 (DEEP, SIFT, SimSearchNet++, YFCC, WIKI)
- **SF**: 1, 10, 100 (Fig별 다름)
- **Sample size**: N=385 init, adaptive ~355~415 (Fig 6)
  - **min_size=355, max_size=415** — paper Fig 6 한계 강제 적용
- **Selectivity**: 1% main (Fig 5/6) + 0.1%/1%/10% ablation (Fig 13)
  - **{0.001, 0.01, 0.10} ONLY** — 우리 추가 {0.05, 0.30, 0.50} 폐기
- **Queries**: TPC-H 8 specific (Q3/Q5/Q8/Q9/Q10/Q11/Q12/Q20) + TPC-DS 7 specific (Q7/Q12/Q19/Q20/Q42/Q72/Q98)
  - **specific queries ONLY** — 우리 100 random 폐기
- **Hyperparam**: m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50
- **HNSW**: M=16, ef_construction=200, ef_search=400
- **Q-error**: max(C_est/C_true, C_true/C_est) (Eq 2)
- **Hardware**: 1 TB RAM, 128 vCPU
- **Trials**: 10 trimmed mean (lowest+highest excluded)

### 1.4 작업 시작 전 점검 list (필수)

[ ] paper 1-15 page 모두 정독
[ ] Fig별 setup 추출 완료
[ ] 위 §1.3 변수 모두 verbatim 확인
[ ] 우리 setup vs paper 차이 list 작성
[ ] 모든 paper 외 추가 항목 명시 폐기
[ ] paper 정확 재현 measurement script 설계 완료
[ ] 점검 후 작업 시작 (이전 X)

---

## 2. 측정 매트릭스 (paper 정확 재현, 멋대로 추가 X)

### 2.1 Phase A: Exqutor B1 baseline (paper 정확 재현)

**우리가 측정할 4개 sub-experiment (paper Fig 별 정확 재현)**:

| Sub-experiment | Paper Fig | Datasets | SF | Queries | Selectivity |
|---|---|---|---|---|---|
| **A1: Sampling main** | Fig 5/6 | DEEP, SIFT, SSN | 100 | Q3, Q9, Q10, Q12 (TPC-H) | 1% |
| **A2: Multi-vector** | Fig 7/8/9 | YFCC tag, DEEP+WIKI partsupp, DEEP+WIKI cross | 10 | TPC-H 8 specific | (paper threshold) |
| **A3: TPC-DS** | Fig 10 | DEEP | 10 | TPC-DS 7 specific | (paper threshold) |
| **A4: Selectivity ablation** | Fig 13 | DEEP | 100 | Q3, Q10, Q12 | 0.1%, 1%, 10% |
| **A5: Scalability** | Fig 14 | DEEP | 1, 10, 100 | Q3, Q5, Q20 | (paper threshold) |

### 2.2 Phase B: CaseA (replace) 측정

각 sub-experiment에서 **B1 sampling step만 우리 method 교체**.
- A1 → A1-CaseA: 34 methods replace
- A2 → A2-CaseA
- A3 → A3-CaseA
- A4 → A4-CaseA
- A5 → A5-CaseA

### 2.3 Phase C: CaseB (augment) 측정

같은 sub-experiment에서 **B1 + CaseA ensemble**.

### 2.4 Phase D: paired Δ% 분석

B1 vs CaseA, B1 vs CaseB, CaseA vs CaseB (Wilcoxon + BH-FDR).

---

## 3. Method portfolio (34 active)

**Tier 1 Legacy** (10): MiniBatch, GMM, Hilbert, faiss_ivf, MB_partial, Reservoir, sparse_rp, PCA1D, LSH, Sobol
**Tier S+** (6): AMSCountSketch, NeuroCard-lite, AdaptiveBucketProbing, CCSketch, FactorJoin, LpBound
**Tier A** (10): PQ, Coreset, DenseRP, BanditUCB1, NeurAM, ThompsonSampling, MFMC, EpsilonNetBaseline, kDPP, OPQ
**Tier B** (7): CCA1D, CoCluster_Nystrom, Tucker, VineCopula, HKBU_RepSample, LHS, LPM2
**Tier C** (1): ConditionalAdaptive

**DROPPED (3)**: HNSW-SS, WanderJoin, HDBSCAN

---

## 4. 현재 진행 (5/10 14:05)

### Active procs
- **Phase F v3 RESUME (PID 2489825)**: 14 cells × B1~B6 sequential. 13:51 SSN_sf1 시작.
- **단 sample_size paper 한계 초과 (max=5000)** — RQ1/RQ2/RQ3 검증용. **Exqutor 정확 재현 X**.

### 결과 활용
- 이전 결과 (multi_paradigm_*, phase_f_v2_full, phase_f_v3) → RQ1/RQ2/RQ3 검증 + 우리 ablation
- 새 측정 (Exqutor 정확 재현, max=415) → NEW SESSION에서 진행

---

## 5. NEW SESSION 작업 sequence (사용자 외출 동안)

### Phase 0: 진입 즉시 (10-20분, 필수 점검)
1. handoff_v1 §1 전체 정독
2. **Exqutor paper 1-15 page 모두 정독** (멋대로 skip X)
3. Fig 5/6/7/8/9/10/13/14 setup 정확 추출
4. §1.4 점검 list 모두 통과
5. Phase F v3 monitor (1분 단위)

### Phase 1: measure_exqutor_replication.py 작성 (4-6h)
- paper §V-B Eq 1-6 + §VI hyperparam 정확 구현
- **min_size=355, max_size=415** (paper Fig 6 한계 준수)
- 3 mode: B1 (Bernoulli), CaseA (replace), CaseB (augment)
- 5 sub-experiment (A1~A5) 지원
- 34 method registry
- TPC-H 8 + TPC-DS 7 specific queries
- selectivity {0.001, 0.01, 0.10} ONLY
- 10 trimmed mean
- dry-run validation (Fig 6 sample size convergence trace 비교)

### Phase 2: Phase A measurement (paper B1 정확 재현)
- A1~A5 sub-experiment sequential
- 순차 1 procs, ETA ~5-8h

### Phase 3: Phase B measurement (CaseA replace)
- A1~A5 × 34 methods sub-experiments
- ETA ~10-15h

### Phase 4: Phase C measurement (CaseB augment)
- A1~A5 × 34 methods
- ETA ~10-15h

### Phase 5: Phase G analysis (paired Δ% B1 vs CaseA/CaseB, BH-FDR)

### Phase 6: REPORT.md 5단계 narrative

**Total ETA**: ~30-50h → **5/12 ~ 5/13 finalize**

---

## 6. 자원 max push 설정

```bash
export OMP_NUM_THREADS=128
export MKL_NUM_THREADS=128
export OPENBLAS_NUM_THREADS=128
nvidia-smi  # GPU 0/2/3 (1번 채림 rule)
```

---

## 7. NEW SESSION 시작 복붙 프롬프트 (FINAL v3)

```
@_internal/handoff_v1_NEW_SESSION_20260510_1336.md 부터 정확히 read.

🚨 가장 중요한 사용자 명시 (5/10 14:03):
"paper의 모든 항목 완전 똑같이 진행. 멋대로 추가/뺄 X. 단 하나라도 다르면 안 됨. 깨끗한 세션에서 paper 다시 정확하게 정독하고 모든 변수/항목 값 확정 후 작업 시작."

**작업 시작 전 필수 점검 (Phase 0, 10-20분)**:
1. handoff_v1 §1 (paper 정독 + 변수 확정 절차) 전체 read
2. Exqutor paper 1-15 page 모두 정독:
   /Users/hyunbin/Capstone/reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf
   - §V-B (p.7-8 sampling 식 1-6 + hyperparam)
   - §VI Datasets/Indexing/System setup (p.7)
   - §VI-A ECQO (Fig 4)
   - §VI-B sampling main (Fig 5/6)
   - §VI-C multi-vector (Fig 7-10)
   - §VI-D Discussion (Fig 11-14)
   - 멋대로 skip X
3. Fig별 setup 정확 추출 (paper verbatim):
   - Fig 5 (sampling): SF=100, DEEP/SIFT/SSN, Q3/Q9/Q10/Q12, sel=1%
   - Fig 6 (sample size convergence): SF=100, DEEP/SIFT/SSN, 1000 iter, fixed N=385 vs adaptive ~355~415
   - Fig 7 (YFCC tag): SF=10, partsupp ps_tag, 8 TPC-H queries
   - Fig 8 (DEEP+WIKI partsupp): SF=10, partsupp 4-way, 8 queries
   - Fig 9 (DEEP+WIKI cross): SF=10, partsupp[DEEP] × part[WIKI], 8 queries
   - Fig 10 (TPC-DS): SF=10, DEEP, 7 TPC-DS queries
   - Fig 13 (selectivity): SF=100, DEEP, Q3/Q10/Q12, sel=0.1%/1%/10%
   - Fig 14 (scalability): DEEP, Q3/Q5/Q20, SF=1/10/100
4. 모든 변수 verbatim 확정 (handoff_v1 §1.3):
   - Datasets: DEEP/SIFT/SSN/YFCC/WIKI (5)
   - SF: 1/10/100 (Fig별 다름)
   - Sample size: N=385 init, min=355, max=415 (Fig 6 paper 한계 강제)
   - Selectivity: paper {0.001, 0.01, 0.10} ONLY (우리 추가 {0.05, 0.30, 0.50} 폐기)
   - Queries: TPC-H 8 specific (Q3/Q5/Q8/Q9/Q10/Q11/Q12/Q20) + TPC-DS 7 (Q7/Q12/Q19/Q20/Q42/Q72/Q98) ONLY (우리 100 random 폐기)
   - Hyperparam: m=0.9/η₀=0.1/α=50/β=1.5/γ=0.99/period=50
   - HNSW: M=16, ef_c=200, ef_s=400
   - Q-error: max(C_est/C_true, C_true/C_est) (Eq 2)
   - 10 trimmed mean
5. handoff_v1 §1.4 점검 list 모두 통과 확인 (이전 X)

**점검 통과 후 작업 시작**:

**5단계 narrative (사용자 명시)**:
1. RQ1, RQ2, RQ3 검증 (기존 결과 유지)
2. Exqutor 100% 정확 재현 (paper exact, 멋대로 추가 X)
3. CaseA: 우리 method 대체
4. CaseB: 우리 method 증강
5. 최종 비교 B1 vs CaseA vs CaseB

**현재 진행 procs**:
- Phase F v3 RESUME (PID 2489825): 14 cells × B1~B6 sequential, 13:51 SSN_sf1 시작
- 단 sample_size paper 한계 초과 (이전 setup) — RQ1/RQ2/RQ3 검증용. Exqutor 정확 재현 X.

**즉시 액션**:
1. Phase F v3 1분 monitor (stuck 즉시 처리):
   ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/phase_f_v3/*.csv 2>/dev/null | wc -l; tail -5 /mnt/hdd0/home/capstone2026/log/phase_f_v3_resume_*.log; pgrep -af 'measure_phase_f' | grep -v grep | wc -l"

2. agent 적극 dispatch (paper 정확 매핑 검증 추가):
   - agent 1: Exqutor paper 1-15 page 모두 read + Fig 5/6/7/8/9/10/13/14 정확 setup 추출 (verbatim 인용 + page 번호)
   - agent 2: TPC-H Q3/Q5/Q8/Q9/Q10/Q11/Q12/Q20 vector predicate 정확 정의 + 우리 NPY 캐시 (partsupp_*_{1,10,100}_vectors.npy) 활용 가능 여부
   - agent 3: TPC-DS Q7/Q12/Q19/Q20/Q42/Q72/Q98 정의 + 우리 측정 가능 여부

3. measure_exqutor_replication.py 작성 (paper exact):
   - paper §V-B 식 1-6 verbatim 구현 (AdaptiveState)
   - hyperparam: m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50
   - **min_size=355, max_size=415** (Fig 6 한계 강제)
   - 5 sub-experiment 지원 (A1~A5):
     * A1: SF100, DEEP/SIFT/SSN, Q3/Q9/Q10/Q12, sel=1% (Fig 5/6)
     * A2: SF10, multi-vector partsupp/cross-table, TPC-H 8 (Fig 7/8/9)
     * A3: SF10, DEEP, TPC-DS 7 (Fig 10)
     * A4: SF100, DEEP, Q3/Q10/Q12, sel 0.1/1/10% (Fig 13)
     * A5: SF1/10/100, DEEP, Q3/Q5/Q20 (Fig 14)
   - 3 mode: B1 (Bernoulli), CaseA (replace), CaseB (augment)
   - 34 active methods registry
   - **selectivity {0.001, 0.01, 0.10} ONLY**
   - **TPC-H 8 + TPC-DS 7 specific queries ONLY**
   - 10 trimmed mean
   - dry-run validation (Fig 6 sample size convergence trace 비교 — DEEP ~360, SIFT ~410, SSN ~355)

4. Phase 2~4 sequential 측정:
   export OMP_NUM_THREADS=128 MKL_NUM_THREADS=128 OPENBLAS_NUM_THREADS=128
   nvidia-smi  # GPU 0/2/3 사용 가능 확인

5. Phase G analysis + REPORT.md 5단계 narrative

**채림 rules**: GPU 0/2/3 (1번 채림 rule), port 55435, 55432/55433 절대 X, sudo X
**사용자 (조현빈)**: 팀 가장 형, peer-to-peer 톤
**시간 압박 X — paper 100% 정확 재현 + 모든 method 완벽 측정**
**사용자 외출 — 돌아왔을 때 실험 정확히 진행 중이어야 함 + paper exact**
**1분 monitor + stuck 즉시 처리 + 순차 max push**
**우리 멋대로 추가한 항목 모두 폐기 — paper에 있는 것만 측정**

**Critical findings (이전 분석, 참조)**:
- B1 (sample 770) vs methods (385) = sample size unfair (우리 setup 잘못)
- B6 Oracle vs B2 = -1.12% (dist-aware ceiling ~1%)
- 사용자 가설: paper 정확 재현 baseline (sample 385 ± 30) + 우리 method 대체/증강 → B1 outperform 가능

**측정 dirs 위치**:
- 이전 결과 (RQ1/RQ2/RQ3 검증, max=5000): cache/rq3/multi_paradigm_*, multi_ensemble, phase_f_v2_full, phase_f_v3
- 새 측정 (Exqutor 정확 재현, max=415): cache/rq3/exqutor_replication_<phase>/

**1분 monitor 절차**:
ssh capstone "now=\$(date +%s); for log in /mnt/hdd0/home/capstone2026/log/*.log; do mtime=\$(stat -c %Y \$log); age=\$((now-mtime)); [ \$age -lt 600 ] && echo \"\${age}s \$(basename \$log)\"; done | sort -n | head -20; pgrep -af 'measure_' | grep -v grep | wc -l"

**stuck 정의**: log mtime 5분 이상 update X + procs CPU < 50% → kill + 다음 cell sequential 재 launch

**다음 세션 첫 task (재 강조)**:
1. handoff_v1 §1 정독
2. **Exqutor paper 1-15 page 모두 깨끗하게 정독** (이전 세션 read 신뢰 X — 새 세션에서 다시)
3. Fig별 setup verbatim 추출
4. §1.4 점검 list 통과
5. **점검 통과 후 작업 시작** — 이전 X

작업 시작 전 paper 정독 + 변수 확정이 사용자 명시 핵심 제약. 변수 하나라도 paper와 다르면 측정 폐기.
```

---

## 8. END

작성: 2026-05-10 14:05 KST (NEW SESSION FINAL v3)
사용자 외출 — 5/10 저녁/밤 ~ 5/11 복귀.
**"paper 100% 정확 재현 + 멋대로 추가 X + paper 정독 + 변수 확정 후 작업 시작"** 가 사용자 명시 핵심.
다음 세션: §7 복붙 프롬프트로 시작 + paper 깨끗 정독부터.
