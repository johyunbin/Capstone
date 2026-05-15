# Handoff v29 — 5/15 본 세션 CaseA 완전 폐기 + 대조군/실험군 reframing + 재정렬 (23:05)

> 5/15 21:23 ~ 23:05 (1h 42m) 본 세션. v28 → v29. 핵심: 사용자 framing reframing (대조군 vs 실험군) + CaseA 완전 폐기 + Type 별 재정렬 + KeyError fix + v6_caseB 재 launch.

---

## 1. 본 세션 commit chain (예상)

| commit | 시점 | 영역 |
|---|---|---|
| 8e92216 | 22:00 | v5_ext 측정 launch (handoff v28 + tmux v5_ext) |
| edcbfb6 | 22:29 | 정리 작업 (DEEP+WIKI 중복 + README + handoff v27 archive) |
| 60bced3 | 22:30 | fix backup file gitignore |
| **(본 commit)** | **23:05** | **handoff v29 + CaseA 완전 폐기 + Type 별 재정렬 + KeyError fix + v6_caseB launch** |

---

## 2. 사용자 framing reframing (★ 5/15 22:51 카톡 + dismiss → 22:55 확정)

### 2.1 새 framing

> "기존 베르누이 + 어댑티브샘플링(대조군) vs 우리의 동적할당 매커니즘 + 어댑티브샘플링(실험군) 방식"

| 영역 | 정의 |
|---|---|
| **대조군 (Baseline)** | Bernoulli + Adaptive Sampling (paper §V-B 원본) |
| **실험군 (Treatment)** | dynamic 할당 mechanism + Adaptive Sampling |
| **dynamic 할당** | 데이터셋 진입 → type 판별 → type 별 best method 자동 선택 |

### 2.2 측정 모드 framing 안 위치

| 측정 모드 | framing 안 위치 |
|---|---|
| **B1** (Bernoulli 단독) | **대조군** ✓ |
| **CaseB** (Bernoulli + 우리 method 결합) | **실험군** ✓ (산술 평균 결합) |
| CaseA (Bernoulli 통째 대체) | framing 안 아님 → **완전 폐기** |

비교 axis: **실험군 (CaseB) vs 대조군 (B1) paired Δ%**.

### 2.3 v5 narrative 재구성 framing 컨펌 받음

| 영역 | 기존 v5 | v5 v6 재구성 |
|---|---|---|
| §1 측정 portfolio | 1352 file (B1 9 + CaseA 495 + CaseB 496 + 추가) | **~691 file** (B1 + CaseB only) |
| §4 정확도 evidence | CaseA -10.17% + CaseB -7.37% | **실험군 (CaseB) vs 대조군 (B1) paired Δ%** |
| §5 plan robustness | CaseA worsening 37.1% (positive contrast) | **제거** + selectivity paradox 유지 |
| §6 Pareto frontier | CaseA / CaseB 둘 다 | **실험군 only** |
| §3 4 type / §7 dynamic flow | 유지 | 유지 (★ 본 framing 핵심) |
| §8 Finding 3 (정확도 92.5%) | CaseB < CaseA | **실험군 < 대조군 ?%** (v6 회수 후 update) |

---

## 3. CaseA 완전 폐기 (★ 사용자 결정)

### 3.1 rm 진행

| 영역 | 폐기 file 수 |
|---|---:|
| RQ3_CaseA dir 9개 (각 cell) | ~145 |
| paper_main/CaseA dir 10개 | 499 |
| K_granularity / multi_join_restratification / cheap_approximation 안 CaseA file | 113 |
| **Total** | **757 file rm** |

전체: 1352 → **691 file** (B1 + CaseB only).

### 3.2 README 정리 보류

`_archived_RQ_README/03_RQ3_단독대체_CaseA_README.md` 도 rm 됨 (CaseA 영역).

---

## 4. KeyError: 20 root cause fix

### 4.1 root cause

`measure_paper_exact.py` 의 `cache_cluster_samples_inmem` 호출 site 4 곳에서 `n_strata` 명시 전달 안 함 → `_measure_common.py` default `N_STRATA=20` 사용 → K=30 일 때 samples dict 안 sid 20~29 안 populate → estimator `samples[sid]` lookup KeyError.

### 4.2 fix

```python
# 변경 전:
mc.cache_cluster_samples_inmem(all_vecs, sids, seed=42)

# 변경 후:
mc.cache_cluster_samples_inmem(all_vecs, sids, n_strata=mc.N_STRATA, seed=42)
```

4 호출 site (line 359, 979, 1077, 1084) 모두 fix. local + server 동기화 완료. dry-run K=10/30 정상 ✓.

---

## 5. experiments/results 재정렬 (Type 별)

### 5.1 새 구조

```
results/raw/
├── Type1_small_single_sf1/          ← 0.1M single (DEEP A5-sf1)
├── Type2_medium_single_sf10/        ← 1M single (DEEP A5-sf10)
├── Type3_large_single_sf100/        ← 10M single
│   ├── DEEP_A1/ + DEEP_A4-sel/ + DEEP_A5-sf100/
│   ├── SIFT_A1/
│   └── SSN_A1/
├── Type4a_large_multi_288d/         ← DEEP+YFCC A2-Fig7
├── Type4b_large_multi_864d/         ← DEEP+WIKI A2-Fig9 (+ alpha_sweep + cheap_approximation 등)
├── _shared_B1/                       ← 대조군 baseline (DEEP/SIFT/SSN/YFCC/DEEP+WIKI)
├── _reports/                         ← cell 별 REPORT 분석
├── _rq1_rq2_summary/                 ← cell 별 RQ1/RQ2 csv
├── _scope_외/                        ← DEEP+CC3M / TPCDS
└── _archived_RQ_README/              ← 옛 README
```

opt 옛 dir (DEEP_96d, SIFT_128d, SSN_256d, YFCC_192d, DEEP+WIKI_864d) 모두 rmdir.

### 5.2 narrative align

- §3 Type 별 적합 method 표 = Type 별 dir 안 CaseB 결과 정렬
- §7 dynamic flow = Type 판별 → 해당 Type dir 안 best method 자동 선택

---

## 6. tmux v6_caseB launch (50 file)

### 6.1 launch script

`/mnt/hdd0/home/capstone2026/_internal/scripts/launch_v6_caseB_only_5_15.sh` (+ local copy)

### 6.2 scope (CaseA framing 안 제거)

| 영역 | cell | mode × method | file |
|---|---|---|---:|
| **P1** (Type 1/2 evidence) | A5-sf{1,10}-{SIFT,SSN} 4 cell | B1 + CaseB × 5 | 24 |
| **P3a** (Type 4b single baseline) | A6-WIKI-sf10 | B1 + CaseB × 5 | 6 |
| **P5** (K granularity Type 3) | A1-SIFT/SSN × K=10/30 | B1 + CaseB × 4 anchor | 20 |

총 **50 file**, 추정 server time **3-6h** (5/16 새벽 ~ 오전 완료).

### 6.3 launch 정상 확인 ✓

23:04 첫 cell A5-scale-sf1-SIFT CaseB sparse_rp 측정 완료 (15초). fit_time/cache_time 분리 정상. monitor 재시작.

---

## 7. 보류 영역 (다음 세션)

| 영역 | 이유 | 다음 세션 |
|---|---|---|
| **v5 narrative v6 본문 재구성** | v6_caseB 측정 결과 회수 후 정확 수치 update | 회수 + 분석 + draft |
| **claude.ai/design v9 paste** | 사용자 직접 paste 효율 | 사용자 직접 |
| **P2/P3b multi-table build** | 10+h DB build 필요 | 향후 결정 |
| **v6 측정 결과 회수 + Type 별 dir 통합** | 측정 완료 후 | rsync server → local Type dir |

---

## 8. 다음 세션 action (5/16 새벽 또는 오전)

### 즉시
1. **v6_caseB COMPLETE.flag 확인** → 50 file 회수
2. rsync server `/mnt/hdd0/home/capstone2026/results_v6_caseB_20260515_1404/` → local Type 별 dir
3. KeyError fix 검증 (K=30 file 정상 생성 여부)

### 분석
1. **실험군 (CaseB) vs 대조군 (B1) paired Δ%** (50 file + 기존 691 file 통합)
2. Type 별 method best 정리 (§3 표 update)
3. analyze_paper_exact.py 의 cell list update (A5-sf{1,10}-{SIFT,SSN}, A6-WIKI-sf10)

### narrative
1. v5 narrative v6 본문 재구성 (대조군/실험군 framing 으로 4-8 section 재작성)
2. §1 측정 portfolio 691 file → ~741 file (v6 추가 후) update
3. §4/§5/§6 paired Δ% 수치 update

### deck v9
1. claude.ai/design Capstone project 새 message paste (사용자 직접)
2. deck v9 generate 결과 확인

---

## 9. 서버 + 측정 portfolio 상태

- server: 165.132.140.240 (capstone2026), /mnt/hdd0/home/capstone2026
- tmux: **v6_caseB** session 진행 중 (5/15 23:04 ~ 5/16 새벽 예상)
- 측정 portfolio: 1352 → **691 file** (CaseA 폐기) + v6 추가 ~50 file = **~741 file** 예상 (B1 + CaseB only)
- monitor: bz4dy0d03 (persistent)

---

## 10. 환각 회피 룰 (carry-over)

본 세션 적용 ✓:
- 작은 단위 Edit (cell 추가 + STRATA_K override + fix 분리)
- dry-run 검증 후 launch
- 사용자 framing 컨펌 받기 (한 번에 dismiss 안 됨)

---

작성: 2026-05-15 23:05 KST · 본 세션 5/15 21:23 ~ 23:05 (1h 42m) · framing reframing + CaseA 폐기 + KeyError fix + Type 별 재정렬 + v6_caseB launch 완료
