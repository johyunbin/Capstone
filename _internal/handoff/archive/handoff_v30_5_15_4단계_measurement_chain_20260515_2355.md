# Handoff v30 — 5/15 본 세션 4단계 chain + 사용 16 method 확정 + selectivity sweep (23:55)

> 5/15 21:23 ~ 23:55 (~2h 32m). v29 → v30. 핵심: 사용 16 method 영역 정의 + selectivity sweep axis 추가 + 4단계 measurement chain (v6→v7→v8→v9, 1348 file 자동 측정 / 5/18 새벽 완료 예상).

---

## 1. 본 세션 commit chain (5 commit, 모두 push ✓)

| commit | 시점 | 영역 |
|---|---|---|
| 8e92216 | 22:00 | v5_ext 측정 launch (handoff v28) |
| edcbfb6 | 22:29 | 정리 작업 (DEEP+WIKI 중복 + handoff v27 archive) |
| 60bced3 | 22:30 | gitignore backup fix |
| f2fd877 | 23:07 | **v6 reframing + CaseA 폐기 + Type 별 재정렬 + KeyError fix** |
| 932fc68 | 23:25 | v7 extras 3 cell (미커버 PG 적재 cover) |
| 846c62e | 23:35 | v8 전수 method 보강 (600 file) |
| **fa8b736** | **23:55** | **v9 selectivity sweep (680 file)** |

---

## 2. 사용자 framing 확정 (5/15 22:51 카톡 + 23:30 추가 결정)

### 2.1 핵심 framing

> "기존 베르누이 + 어댑티브샘플링(대조군) vs 우리의 동적할당 매커니즘 + 어댑티브샘플링(실험군)"

| 영역 | 정의 |
|---|---|
| **대조군 (Baseline)** | Bernoulli + Adaptive Sampling (paper §V-B 원본) |
| **실험군 (Treatment)** | dynamic 할당 mechanism + Adaptive Sampling |
| **dynamic 할당** | 데이터셋 진입 → Type 판별 → Type 별 best method 자동 선택 |

### 2.2 측정 모드 framing 안

| 모드 | framing |
|---|---|
| **B1** (Bernoulli 단독) | **대조군** ✓ |
| **CaseB** (Bernoulli + 우리 method 결합) | **실험군** ✓ |
| CaseA (Bernoulli 통째 대체) | framing 안 아님 → **완전 폐기** (757 file rm) |

---

## 3. 사용 16 method 확정 (Pareto Top 5 + paradigm rep 11)

폐기 40 method = 정합성 위반 10 + audit drop 23 + 측정 미커버 7 (사용자 결정: **C 측정 미커버 7 도 완전 폐기**, narrative 미언급).

| Paradigm | 사용 method |
|---|---|
| P1 Cluster (3) | minibatch_partial, gmm, faiss_ivf |
| P2 Spatial (3) | **hilbert_real** ★, zorder_morton, skilling_hilbert |
| P3 Streaming (1) | **chao_weighted** ★ |
| P4 DimReduction (4) | **sparse_rp** ★, **pca1d** ★, rsvd, ica_fastica |
| P5 QMC (2) | cum_sqrtf, lavallee_hidiroglou |
| P6 Quantization (2) | rabitq_strat, mhist2 |
| P9 InfoTheoretic (1) | **hyperloglog** ★ |

★ = Pareto Top 5.

폐기 40 method 자료 archive 시점: v8 + v9 완료 후 (다음 세션).

---

## 4. 4단계 measurement chain (1348 file 자동 측정)

| stage | scope | file | server time | 시점 |
|---|---|---:|---|---|
| **v6_caseB** (진행 중 23:47 = 35/50) | P1+P3a+P5 × Pareto Top 5 + B1 | 50 | ~30분 남음 | 23:30 → 00:00 |
| **v7_extras** (chain) | A6-WIKI-sf1, A7-YFCC-sf1, A8-DEEP+SIFT-sf10 × Pareto Top 5 + B1 | 18 | 1-2h | 00:00 → 02:00 |
| **v8_full** (chain) | 12 cell × 50 잔여 method × CaseB | 600 | ~27h | 02:00 → **5/17 새벽** |
| **v9_sel_sweep** (chain) | 20 cell × 2 sel × 17 (B1 + 16 method) | 680 | ~27-30h | 5/17 새벽 → **5/18 새벽** |

server 측 chain watcher (nohup background):
- `v6_v7_chain.sh` (PID 1599300)
- `v7_v8_chain.sh` (PID 1600789)
- `v8_v9_chain.sh` (PID 1603641)

전체 측정 portfolio (5/18 새벽 시점): 기존 691 + 1348 = **2039 file** (대조군 + 실험군 only, CaseA 영역 완전 제거).

---

## 5. PG 적재 dataset cover 영역 (LAION 제외)

| Dataset | sf=1 | sf=10 | sf=100 | sel sweep |
|---|---|---|---|---|
| DEEP 96d | ✓ | ✓ | ✓ + A4-sel | v9 추가 |
| SIFT 128d | v6 ✓ | v6 ✓ | ✓ + K granularity (K=10/30 v6) | v9 추가 |
| SSN 256d | v6 ✓ | v6 ✓ | ✓ + K granularity (K=10/30 v6) | v9 추가 |
| WIKI 768d | **v7 ✓** | v6 ✓ | — | v9 추가 |
| YFCC 192d | **v7 ✓** | ✓ (A2-Fig7) | — | v9 추가 |
| DEEP+SIFT multi | — | **v7 ✓** | — | v9 추가 |
| DEEP+WIKI multi | — | ✓ (A2-Fig9) | — | v9 추가 |

→ **LAION 제외 PG 적재 dataset 모두 cover** (대조군 + 실험군 둘 다, 모든 selectivity).

---

## 6. v5 narrative 재구성 framing (다음 세션 본문 작성 영역)

| 영역 | 기존 v5 | v6/v9 framing 재구성 |
|---|---|---|
| §1 측정 portfolio | 1352 file (CaseA 포함) | **2039 file** (B1 + CaseB only) |
| §2 분포 catch speed | fit_time 11.9× | 유지 + v8+v9 측정 결과 update |
| §3 데이터셋 4 type | Type 별 best method | **사용 16 method 안에서 cell × method best 매핑** |
| §4 정확도 evidence | CaseA + CaseB | **실험군 (CaseB) vs 대조군 (B1) paired Δ%** only |
| §5 plan robustness | CaseA worsening 37.1% | **selectivity-dependent 대조군 vs 실험군 비교** (v9 evidence) |
| §6 Pareto frontier | CaseA + CaseB | 실험군 (CaseB) only |
| §7 dynamic flow | dynamic method selection | 유지 (★ 본 framing 핵심) |
| §8 결론 Finding | CaseA finding 포함 | CaseA 제거 + selectivity sweep finding 추가 |

폐기 40 method 영역 narrative 미언급 (사용자 결정).

---

## 7. 다음 세션 action (5/17 새벽 또는 오전 / 5/18 새벽)

### Phase 1: v6+v7+v8+v9 회수 (1-2h)
1. COMPLETE.flag 4개 확인 (server)
2. rsync server → local Type 별 dir (1348 file)
3. 폐기 method file (v8 측정 안 50 method 中 폐기 영역 일부) → archive

### Phase 2: 분석 (3-4h)
1. **실험군 vs 대조군 paired Δ%** 분석 (2039 file)
2. **cell × method best 매핑** (dynamic mechanism evidence)
3. **selectivity-dependent 비교** (v9 evidence)
4. K granularity sweet spot SF axis 일관 evidence

### Phase 3: v5 narrative v6 본문 재구성 (3-4h)
1. CaseA 영역 모두 제거
2. 사용 16 method paradigm 별 제시
3. cell × method × sel 영역 정합 매핑
4. 의미 있는 method (Pareto Top 5) 알고리즘 자세히 소개

### Phase 4: claude.ai/design v9 paste (사용자 직접)
1. prompt v9 carry-over + 사용 16 method 영역 update
2. deck v9 generate + 검토

---

## 8. 보류 영역 (post-narrative)

- 박광현 input 4 엔진 통합 POC (5/27 발표 후 ~ 6/11 사이)
- narrative §3 Type 4a 정의 정확성 점검 (YFCC 192d single vs DEEP+YFCC 288d)

---

작성: 2026-05-15 23:55 KST · 5/15 21:23 ~ 23:55 (2h 32m) · framing reframing + CaseA 폐기 + 4단계 chain (1348 file) + 사용 16 method 확정
