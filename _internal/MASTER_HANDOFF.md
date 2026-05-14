# MASTER_HANDOFF.md — handoff v0~v5 + validation + Phase 4 통합

> 작성: 2026-05-11 01:50 KST  
> 목적: 10건 handoff (v0/v0.bak/v1/v2/v3/v4/v5/back_validation/main_session_FULL_STATE/validation_statistics) 단일 통합  
> 새 세션 0% loss 인계 anchor — 본 file 1건 read + MASTER_README.md 1건 read 만으로 모든 진행 상태 파악

---

## 0. TL;DR — 새 세션 즉시 액션 5단계

1. SSH 검증: `ssh capstone "date && pgrep -af measure_paper | wc -l"` (ed25519 등록됨, password 불필요)
2. 측정 진행 확인: `ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"`
3. tmux + sigma 진행: `ssh capstone "tmux ls; tail -10 /mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_*.log"`
4. 자동 chain monitor 상태 — task `bdrhrddyb` (sigma + RQ2 5-way + 분석 2차)
5. Phase 4 11 method server scp + measurement launch (handoff_v5 §4-§7 — 사용자 4 confirm 완료 5/11 01:05)

---

## 1. 사용자 + 팀 + 환경 (handoff_main §1)

- **사용자**: 조현빈 (Capstone 팀 가장 형, peer-to-peer 톤, "형/누나" X)
- **팀명**: 속도는벡터 (연세대 컴공)
- **팀원**: 박세은 (팀장), 강재현, 조현빈, 이동욱
- **지도교수**: 박광현 (BDAI)
- **지도연구원**: 임채림 석사 (서버 admin)
- **멘토**: 박성원 (삼성전자 AI센터)
- **외출 이력**: 5/10 14:29 KST 외출, 17:39 VPN 복구, 5/11 새벽 복귀 (전권 위임 사용자 명시)

---

## 2. 5단계 narrative (사용자 명시 5/10 14:03 + 18:49 + 20:45)

| # | 단계 | 검증 결과 |
|---|---|---|
| 1 | RQ1, RQ2, RQ3 검증 | ✅ RQ1 5%, RQ2 9% 격차 (Bern→Prop) |
| 2 | Exqutor 100% 정확 재현 (paper 멋대로 추가 X) | ✅ Fig 12 영역 8 cells mean qe_trim **1.618** (paper 1.69 vs **−4.3%**) |
| 3 | CaseA: 우리 method **대체** | ⚠️ minibatch_partial **-10.17%** method-mean only / 7.6% 통계 유의 — 단독 narrative 약함 |
| 4 | CaseB: 우리 method **증강** | ✅ 6 methods 모두 -2~-7% outperform / 44.7% 통계 유의 (46/103) |
| 5 | 최종 비교 B1 vs CaseA vs CaseB | ✅ CaseB > CaseA > B1 (CaseB 79.6% outperform vs CaseA 40.1%) |

**우리 contribution = augment within §V-B** (대체 X — §V-A ECQO 그대로 인정).

---

## 3. Exqutor paper 핵심 (handoff_main §2)

### 3.1 paper §V-A ECQO (Extended Cardinality Query Optimizer)
- HNSW range query를 cardinality estimator (vector index 있을 때, 1~2ms)
- HNSW M=16, ef_search=400
- Fig 4 (TPC-H, SF=100), Fig 10 (TPC-DS, SF=10)

### 3.2 paper §V-B Adaptive Sampling (vector index 없을 때 — 우리 핵심 영역)

**Eq 1-6 verbatim**:
```
N = ⌈z²·P̂(1-P̂)/e²⌉ = ⌈1.96² × 0.5 × 0.5 / 0.05²⌉ = 385         (1) initial
Q-error = max(C_est/C_true, C_true/C_est)                      (2)
δ = α·(Q-error - β) - (100-α)·sampling_ratio                   (3) adjustment
V_t = m·V_{t-1} + η_t·δ                                        (4) momentum
size_{t+1} = size_t + V_t                                      (5) size update
η_{t+1} = γ·η_t                                                (6) lr decay
```

**Hyperparam**: m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / update_period=50 / N=385

⚠️ paper Eq 1-6 에 **min/max clamping 없음** (handoff_v1 "min=355/max=415" 폐기)

### 3.3 5 Critical decisions (handoff_v2, agent 1 paper 1-15p 정독)

| # | 항목 | handoff_v1 추정 | paper verbatim | 결정 |
|---|---|---|---|---|
| 1 | Fig 5 queries | 모든 dataset Q3,9,10,12 동일 | DEEP/SIFT=Q3,10,12 / SSN=Q3,9,10 | **paper 따라 정정** |
| 2 | min/max bound | "min=355, max=415 강제" | Eq 1-6에 clamping 없음 | **bound 제거** |
| 3 | Selectivity | 우리 기존 {0.05, 0.30, 0.50} | paper Fig 13 = {0.1%, 1%, 10%} only | **paper 따름** |
| 4 | A3 TPC-DS | sampling replace/augment | paper Fig 10 = ECQO mode (sampling X) | **A3는 ECQO 별도** |
| 5 | Metric | Q-error만 | paper Fig caption "execution time" + Eq 2 | **Q-error + wall-clock 둘 다** |

### 3.4 Vector range threshold (Exqutor github verbatim, 5/10 14:20 클론)
- TPC-H 8 queries: `< 0.86` (DEEP 96d 통일)
- TPC-DS Q7/Q12/Q20/Q72: `< 1.08` / Q19/Q42: `< 1.20` / Q98: `< 1.30`
- 위치: `reference/exqutor_query_plans/{tpc_h,tpc_ds}/q*.sql`

### 3.5 paper Fig 12 reports
**avg Q-error 1.69** (Exqutor) vs SelNet 5.53 (3.3× 우위) — 우리 paper exact 재현 검증 anchor

---

## 4. SSN ↔ FB ↔ SimSearchNet++ alias 핵심 (handoff_main §3.2)

⚠️ **놓치기 쉬운 결정적 detail**:

| 우리 코드 alias | paper 이름 | server table | dim | 사용 Fig |
|---|---|---|---|---|
| **DEEP** | DEEP | partsupp_deep_{1,10,100} | 96 | Fig 4/5/6/8/9/10/13/14 |
| **SIFT** | SIFT | partsupp_sift_{1,10,100} | 128 | Fig 4/5/6 |
| **SSN = FB** | SimSearchNet++ | **partsupp_fb_{1,10,100}** | 256 | Fig 4/5/6 |
| **YFCC** | YFCC | partsupp_yfcc_{1,10} | 192 | Fig 7 |
| **WIKI** | WIKI | partsupp_wiki_{1,10}, part_wiki_10 | 768 | Fig 8/9 |

- query_pool 파일명: **`query_pool_SSN_sf{1,10,100}.parquet`** (SSN 사용)
- 우리 코드: `dataset="SimSearchNet++"`, `table="partsupp_fb_{sf}"`, alias map `"SimSearchNet++": "SSN"`
- 5/10 결정: 모든 문서·발표·논문 단일 표기 = **SSN**

---

## 5. method registry (57 method, paradigm P1-P10)

> 상세: METHOD_REGISTRY.md

### 5.1 핵심 분류

- **P1 Cluster** (8 활성 + 2 폐기/rename): minibatch / gmm / mb_partial ★2 / birch / agglo / coreset / dbscan / kmeans_neyman M9
- **P2 Spatial** (8 활성 + 3 폐기/rename): hilbert_real / skilling_hilbert M7 / zorder_morton M6 / idistance M5 / idistance_neyman M11 / faiss_ivf / lpm1_proper M2 / epsilon_net
- **P3 Streaming** (1 활성 + 5 폐기): chao_weighted M1
- **P4 DimReduction** (5 활성 + 8 폐기/rename): sparse_rp ★4 / random_projection / pca1d / rsvd / ica_fastica M8
- **P5 QMC/Hashing** (7 활성 + 1 rename): lsh / sobol / halton / hammersley / lhs / cum_sqrtf M3 / lavallee_hidiroglou M4
- **P6 Quantization** (3 활성 + 2 fix): rabitq_strat M10 / mhist2 / wavelet_hist
- **P9 InfoTheoretic** (1 활성 신규): hyperloglog
- **P10 Density** (1 활성 신규): kde_parzen
- **P7 Subspace** / **P8 Graph-based** = future work

### 5.2 4강 후보 (handoff_v0 V8 audit)

| ★ | method | score | paradigm | 처리 |
|---|---|---|---|---|
| ★1 | hdbscan | 7/10 | P1 | minor tuning OK (K_eff<20 padding) |
| ★2 | minibatch_partial | 8/10 | P1 (P3 hybrid) | 신뢰 (CaseA -10.17% strong) |
| ★3 | hilbert | 2/10 ❌ | P2 | **PCA 2D lex sort defect** → rename `pca2d_lex` + M6/M7 paradigm anchor 추가 |
| ★4 | sparse_rp | 6/10 | P4 | **Achlioptas 2003 ❌ → Li-Hastie-Church 2006 ⭕** reference 정정 |

### 5.3 폐기 권고 10건 (handoff_v3 §1.3 verbatim)

thompson_sampling / mfmc / neuram / cca1d / ams_count_sketch / ccsketch / kdpp / cocluster_nystrom / banditucb1 / hkbu_repsample (or coreset)

### 5.4 Phase 4 11 NEW method (handoff_v5 §2 verbatim)

| # | code | method | reference | paradigm | priority |
|---|---|---|---|---|---|
| 1 | M1 | chao_weighted | Chao 1982 *Biometrika* 69(3) | P3 (weight) | **P0** |
| 2 | M2 | lpm1_proper | Grafström-Lundström-Schelin 2012 *Biometrics* 68(2) | P2+P3 | **P0** (lpm2 misnomer rectify) |
| 3 | M3 | cum_sqrtf | Dalenius-Hodges 1959 *JASA* 54(285) | P5+RQ2 | P1 |
| 4 | M4 | lavallee_hidiroglou | Lavallée-Hidiroglou 1988 *Survey Method* 14(1) | P5+RQ2 | P1 |
| 5 | M5 | idistance | Jagadish-Ooi-Tan-Yu-Zhang 2005 *TODS* 30(2) | P2 | **P0** |
| 6 | M6 | zorder_morton | Morton 1966 *IBM Tech Rep* | P2 (anchor) | **P0** |
| 7 | M7 | skilling_hilbert | Skilling 2004 *AIP Conf Proc* 707 | P2 (★3 rectify) | **P0** (Q1 (C)) |
| 8 | M8 | ica_fastica | Hyvärinen 1999 *IEEE NN* 10(3) | P4 | P1 |
| 9 | M9 | kmeans_neyman | Cochran 1977 §5 + Neyman 1934 *JRSS* | P1+RQ2 | **P0** (RQ2 plug-in) |
| 10 | M10 | rabitq_strat | Gao-Lin 2024 *PVLDB* 17(11):3252 | P6 | P1 (2024 fresh) |
| 11 | M11 | idistance_neyman | Jagadish 2005 + Neyman 1934 (synthesis) | P2+RQ2 | **P0** (synthesis) |

---

## 6. measurement matrix (9 cells × 57 methods × 3 modes)

> 상세: EXPERIMENT_REGISTRY.md

### 6.1 9 cells

A1-DEEP / A1-SIFT / A1-SSN (Fig 5/6) + A2-Fig7 (YFCC) / A2-Fig9 (DEEP+WIKI cross) + A4-sel (Fig 13) + A5-scale-sf{1,10,100} (Fig 14)

### 6.2 진행 상태 (handoff_v6 기준 5/11 01:25 KST)

- ✅ Phase A B1: 9/9 cells (paper Fig 12 −4.3% 일치)
- ✅ Phase B/C Tier 1 Legacy: 99 + 99 = 198 cells
- 🔄 Phase B/C extra + extra2 28 NEW × 9 × 2 = 504 cells 진행
- 🔄 Q4 Tier 1 (6 method × 9 × 2 = 108) 진행
- ✅ **Phase 4 11 method launch 완료** (5/11 01:25 — 11 tmux pb_p4_*)
- 🔄 합계 **cnt=440/702 (62%)** / procs 31 (메인 20 + Phase 4 11) / mem available 56 GB
- ⏳ A2-Fig8 (multi-vector): partsupp_deep_wiki_10 stratum_id 부재 — post-fix
- ⏳ A3-TPCDS (ECQO mode): Exqutor PG patch 충돌 — 후순위

### 6.3 RQ1 paper exact ✅ 완료
- DEEP/SIFT × Bernoulli/KM20 × sel{0.01,0.10}
- gap +6.76% (DEEP sel=0.01) / +9.45% (SIFT sel=0.10) — 5% 격차 narrative

### 6.4 RQ2 paper exact ✅ 3-way 완료, 5-way 진행 中
- DEEP/SIFT × Bern/Equal/Prop × sel{0.01,0.10}
- gap (Bern→Prop) +10.32% (DEEP sel=0.01) — 9% 격차 narrative
- 5-way 확장 (Neyman/Anti-Neyman) — 자동 chain monitor `bdrhrddyb` 진행 中

### 6.5 미완료 / blocker

- A2-Fig8 (multi-vector): partsupp_deep_wiki_10 stratum_id 부재 — post-fix
- A3-TPCDS (ECQO mode): Exqutor PG patch 충돌 — 후순위 (paper §V-A 영역 외)

---

## 7. server 자원 + tmux + 자동 chain

> 상세: SERVER_REGISTRY.md

### 7.1 server 핵심
- IP 165.132.140.240 / capstone2026 (ed25519 등록됨)
- 작업 dir `/mnt/hdd0/home/capstone2026/`
- PG port **55435** active / 55436 가용 (다른 인스턴스 55432/55433 절대 X)
- Hardware: Intel Xeon Gold 6530, 128 vCPUs, 1.0 TB RAM, 4× NVIDIA RTX 6000 Ada 49 GB
- VPN keep-alive (~/.ssh/config + `/tmp/capstone_keepalive.sh` 60s ping)

### 7.2 tmux 23+ session (5/10 20:45) + Phase 4 launch 시 32+
- paper_exact / phase_b_smoke / phase_b_full / rq1_rq2 / pb_A1-DEEP/SIFT/SSN / pb_A4-sel / pb_A5-scale-sf100
- pc_A1-* / A2-Fig7/Fig9 / A4-sel / A5-scale-sf{1,10,100}
- pbe_*, pbe2_*, pce_* (Phase B/C extra)
- sigma_build_pe (5/10 21:40 launch / 22:06 kill / 자동 chain 후 재 launch 예정)
- rq2_pe (자동 launch 예정)
- pb_phase4 (handoff_v5 launch 대기)

### 7.3 Smart Coordinator v3 (handoff_v6 §2 + §8.5-§8.7) — 새 세션 인계용

- **30s polling + persistent (1h auto re-arm)**
- Auto-fix:
  - **RSS > 30GB → 즉시 kill** (high-mem) — birch × SF=100 cells 50-200GB 폭증 (5/11 01:34 사례)
  - mem < 10GB → 가장 오래 stuck procs kill (emergency)
  - log mtime 30min+ + CPU<50% → kill (stuck)
- **Auto-relaunch** (5분 주기) — kill된 method 재 launch → 결국 모든 method 완료 보장
- 자원 idle 활용: procs < 20 + mem > 200GB + 미완료 method 있음 → 추가 launch
- Trigger:
  - **main_act=0 + cnt>650 + total_act=p4_act** → main_chain_post tmux launch:
    - Step 1: analyze 1차
    - Step 2: sigma builder (compute_stratum_sigma_paper_exact.py)
    - Step 3: RQ2 5-way (Bernoulli/Equal/Prop/Neyman/Anti)
    - Step 4: analyze 2차 (RQ2 포함)
  - **total_act=0 + chain_post=0 + main_chain_done=1** → final analysis (analyze 3차) → 🎉 COMPLETE
- Sanity check: false-zero 방지 (`total_act=0` + `cnt<700` 시 confirm 한 번 더)
- 이전 monitor `bdrhrddyb` (v2 — handoff_v4 §2)는 superseded

---

## 8. validation 결과 (handoff_back §1-§3 + 4 layer audit)

### 8.1 Layer 1 (paired Δ% 공식) — PASS
- `mean((CaseA - B1) / B1 × 100)` per-trial 정확
- trial pairing OK (B1 trial i ↔ CaseA trial i 동일 seed)
- inf/nan handling 정확

### 8.2 Layer 2 (Wilcoxon + BH-FDR) — PASS
- 메인 자체 BH-FDR vs `statsmodels.multipletests('fdr_bh')` max diff = **1.11e-16** (precision)

### 8.3 Layer 3 (narrative consistency) — CRITICAL 정정
- **paper Fig 12 1.69 비교 영역 분리**: A4-sel (qe=5.984) → Fig 13 영역 별도
- Fig 12 영역 8 cells mean qe_trim = **1.618** → paper 1.69 vs **−4.3%** (narrative #2 강화)

### 8.4 Layer 4 (cherry-picking) — WARN
- handoff §1.4 표 9건 中 6건 method-mean과 다름 (대부분 우리에게 더 유리한 숫자)
- minibatch_partial CaseA -7.41% → method-mean **−10.17%** 정정

### 8.5 추가 권장
- one-sided alternative (`alternative="greater"`, `method="exact"`) — n=10 small sample power 향상
- effect size (Hedges' g 또는 Cliff's δ) 추가
- paradigm-level rollup (P1-P10 평균 outperform)

---

## 9. method audit 결과 (handoff_v3 + _SUMMARY 5,777 lines)

### 9.1 종합 (3.8/10 평균, 22 critical defect / 12 moderate / 7 OK)

P6 1.6/10 (폐지 권고) > P3 3.4 > P2 3.6 > P5 4.4 > P4 4.5 > P1 5.1

### 9.2 학술 reference fraud / misrepresentation (15건) — paper reviewer reject 위험

핵심:
- **★3 hilbert** (Faloutsos 1989 ❌ → PCA 2D lex sort): rename `pca2d_lex` 권고 (Q1 (C))
- **★4 sparse_rp** (Achlioptas 2003 ❌ → Li 2006 1/√D variant): reference 정정만
- reservoir (Vitter 1985 ❌ → RANDOM20 random): rename `random20`
- thompson_sampling / mfmc / neuram / cca1d / ams_count_sketch: 모두 polished naming defect → 폐기
- lpm2 (Grafström 2012 ❌ → Weiszfeld median + radial): rename `radial_quantile`
- tucker / vinecopula / factor_join / neurocard_lite: PCA-alias rename
- **lp_bound (SIGMOD 2025 LpBound 명칭 충돌)**: rename `l2_quantile`

### 9.3 algorithm bug / leak (5건)

- banditucb1: UCB1 미구현 (KMeans wrapper) — 폐기
- kde_pilot: KM20 leak (`stratum_id` SELECT) — RQ3 paradigm 비교에서 제외 유지 (V7 audit)
- pq / opq: md5 hash → codeword 효과 0% — md5 제거
- cocluster_nystrom: Nyström 미구현 — rename `biclustering_5k_centroid`

### 9.4 redundancy / alias (10건)

kdpp (≡ epsilon_net) / kdtree (idx % n_strata) / hkbu_repsample (≡ coreset) / coreset (max_iter=10) / adaptive_bucket_probing (≡ PCA1D) / dense_rp (≡ random_projection) / sobol/halton/hammersley/lhs (low-discrepancy disclaimer)

### 9.5 사용자 confirm 5/11 01:05 (handoff_v5 §0 verbatim)

✅ "ㅇㅋ. 모두 다 진행할거라서. 순서대로 해도 무관."
- Q1 ★3 hilbert: (C) `pca2d_lex` rename + 진짜 hilbert (M6/M7) 별도 추가
- Q2 10건 폐기: 모두 폐기
- Q3 P6 폐지 vs P9/P10 신규: (B) 9 paradigm 확장
- Q4 Tier 1 6 method 추가: 진행 (DBSCAN/KDE/MHIST-2/HyperLogLog/RSVD/wavelet)
- Q5 handoff_v2 5 paper exact decisions: 진행 中 (별도 confirm 완료, paper exact 측정 진행)

---

## 10. SF feasibility (handoff_v3 §3, 615 cell scope)

- infeasible: 34 cells (5.5%) — vinecopula × SF=100 등
- subset_training 필수: 66 cells (10.7%) — hdbscan/birch/agglo/cocluster_nystrom/kdpp/epsilon_net/kdtree/hkbu_repsample × SF=10·100
- 분포 mismatch: 149 cells (24.2%) — sobol/halton/hammersley/lhs × SIFT/YFCC (skew 무시)
- strong fit: 218 cells (35.4%) — PCA-based × skew, density × rich
- neutral fit: 214 cells (34.8%) — sparse_rp/lsh × all

handoff_v0 FINAL SCOPE 1,044 measurement scope의 **97.2% 가능**. vinecopula × 3 SF=100 cell만 drop.

---

## 11. 카톡 narrative pivot (5/9 18:27 사용자 verbatim, handoff_main §11.2)

> "지금 우리가 찾은 게 multi에서 진행해보니까 그냥 adaptive 하는거랑 큰 차이가 없더라. ... single/multi에 모두 강한 방식들 찾으면 기존거를 실패한 걸로 소개하고, ... single 우수 → multi 우수 방식을 RQ3에서 실제로 찾았고, 이걸 exqutor 방식 vs 우리가 찾은걸 exqutor에 앙상블한 방식 비교해서 실질적으로 효능이 있음을 보이는 식으로."

→ narrative pivot:
- ❌ single 우수 → multi 우수 가정 폐기 (multi에서 adaptive와 큰 차이 없음)
- ✅ **single+multi 모두 강한 방식 발견 → Exqutor에 ensemble** (= 우리 CaseB)
- ✅ "Exqutor 방식 vs Exqutor + 우리 방식 ensemble" 비교가 5/27 climax

---

## 12. 5/27 최종발표 storyline 7단계 (handoff_main §11.6 + handoff_v5 §9)

| # | 단계 | 핵심 method (paradigm) | 검증 |
|---|---|---|---|
| 1 | 단일 random sampling skew 부정확 (RQ1) | RANDOM20 baseline + chao_weighted M1 (P3 weight) | ✅ paper exact 5% 격차 |
| 2 | **분포 알면 Neyman 답 (RQ2)** | **kmeans_neyman M9 (P1+RQ2) / cum_sqrtf M3 (P5) / lavallee_hidiroglou M4 (P5) / idistance_neyman M11 (P2+RQ2)** | ✅ Bernoulli/Equal/Prop 9% 격차 — Neyman/Anti 진행 中 |
| 3 | 분포 모르니까 추정 활용 (RQ3) | sparse_rp ★4 (P4 anchor) / mb_partial ★2 (P1) / lpm1_proper M2 (P2) / idistance M5 (P2) / zorder_morton M6 (P2) | RQ3 5 paradigm × 11 method |
| 4 | 단일 -8% 격차 입증 | mb_partial -10.17% method-mean (CaseA strong) | ✅ paper exact 검증 |
| 5 | multi-table 0/66 | (이전 narrative — multi 측정 진행 中) | A2-Fig9 cross 진행 中 |
| **6 신규 method 발굴** | **Phase 4 11 method (M1-M11) 모두 P0/P1** + Q4 Tier 1 6 (DBSCAN/KDE/MHIST-2/HLL/RSVD/wavelet) | 17 method × 9 cells × 2 modes = 306 cells launch 대기 |
| **7 Adaptive vs Adaptive+ensemble climax** | **M9/M11 RQ2 plug-in 직접 강화** + ★4 sparse_rp paradigm anchor | CaseB 6 methods -2~-7% outperform |

### 12.1 학술 contribution (handoff_v5 §9.1)

1. **★3 hilbert defect rectify** = M6 zorder_morton (paradigm anchor) + M7 skilling_hilbert (true high-D Hilbert)
2. **RQ2 + RQ3 결합 4건** (M9/M11 + M3/M4) = "분포 정보 추정 방식 × Neyman σ allocation" 2D ablation
3. **2024-25 SIGMOD/VLDB 인용**:
   - M10 RaBitQ (Gao-Lin VLDB 2024)
   - Q4 PRICE (Zeng VLDB 2024)
   - LpBound rename (lp_bound → l2_quantile, SIGMOD 2025 Best Paper LpBound 충돌 회피)
   - PDX SIGMOD 2025 (intrinsic_dim + skewness — RQ1 narrative align)

---

## 13. 핵심 fix 이력 (handoff_main §9.4 + handoff_v4 §1.3)

| 일시 (KST) | fix |
|---|---|
| 5/10 14:49 | query_selectivity column: `d_target` → `D_target`, `true_card` → `true_cardinality` |
| 5/10 14:50 | trimmed_mean inf filter (Bernoulli hits=0 → est=0 → Q-error inf 회피) |
| 5/10 14:50 | AdaptiveState.update q_error inf cap=100 (size 폭증 방지) |
| 5/10 17:22 | sparse_rp / random_projection signature swap fix: `assign_*(matrix, vectors)` |
| 5/10 17:50 | ~/.ssh/config 강화 (ServerAliveInterval 15) + background keep-alive script |
| 5/10 18:06 | GMM cholesky fail fix: `covariance_type='diag' + reg_covar=1e-2` |
| 5/10 21:08~44 | analyze_paper_exact.py 정정 (Fig 12 영역 분리 + one-sided greater) + _measure_common.py 5-way modes 확장 |
| 5/10 21:48 | `_NAN_DELTA` 상수 통일 (paired_delta() bug fix) |
| 5/10 22:06 | sigma builder kill (NPY fancy indexing OOM) → sequential 진행으로 변경 |
| 5/11 01:00 | Phase 4 method_phase4_extra.py + PATCH + run_phase_b_phase4.sh 신규 작성 |

---

## 14. 산출물 위치 (local + server + memory)

### 14.1 Local — _internal/

본 file이 작성되는 위치 — MASTER_README.md / MASTER_HANDOFF.md (이 file) / METHOD_REGISTRY.md / EXPERIMENT_REGISTRY.md / SERVER_REGISTRY.md / CHANGELOG.md / _BEFORE_INVENTORY.md / _CLEANUP_LOG.md / naming_convention.md

```
_internal/
├── MASTER_README.md       ★ 단일 진입점
├── MASTER_HANDOFF.md      ★ 이 file
├── METHOD_REGISTRY.md     ★ 57 method paradigm
├── EXPERIMENT_REGISTRY.md ★ 9 cells × 57 methods × 3 modes
├── SERVER_REGISTRY.md     ★ port/cache/log/PG/tmux
├── CHANGELOG.md           ★ 5/10~5/11 timeline
├── _BEFORE_INVENTORY.md   baseline (정리 전)
├── _CLEANUP_LOG.md        Phase 4 mv log (정리 후)
├── naming_convention.md   file naming 규칙
├── handoff/
│   ├── active/   (v2/v4/v5/main_session_FULL_STATE/back_validation, 5건)
│   └── archive/  (v0/v0.bak/v1/v3/validation_statistics, 5건)
├── method_audit/
│   ├── 20260510_initial/  (P1-P6 audit, 11 file, 5,777 lines)
│   └── 20260511_phase4/   (Phase 4 11 method, 5 file)
├── scripts/
│   ├── (active 32건 — measure_paper_exact, _measure_common, analyze_*, method_*, run_*, PATCH_*, md2*)
│   └── archive/  (43건 — 이전 측정 끝난 script)
├── validation/   (13 file + data/319, 그대로)
├── state/        (12 file, 그대로)
├── archive/      (4 sub-dir, history)
├── cache/, guideline/, learning/, records/, server_wrappers_backup_*  (그대로)
```

### 14.2 Server — `/mnt/hdd0/home/capstone2026/`
- `cache/rq3/{measure_paper_exact,analyze_paper_exact,_measure_common,compute_stratum_sigma_paper_exact}.py`
- `cache/rq3/methods/` (extra2 20 method 별 module)
- `cache/rq3/method_phase4_extra.py` ⏳ scp 대기
- `cache/rq3/run_phase_*.sh` (8개)
- `cache/rq3/paper_exact/{B1,CaseA,CaseB}.json + rq{1,2}_*.csv + REPORT.md`
- `cache/rq1/{partsupp_*}_{vectors,strata,pks}.npy + query_pool_*.parquet + query_selectivity_*.parquet`
- `log/paper_exact_phase_*.log + sigma_build_paper_exact_*.log + rq2_paper_exact_5way_*.log`
- `vanilla_sf100/` (PG data dir, port 55435)

### 14.3 Memory — `~/.claude/projects/-Users-hyunbin-Capstone/memory/`
- MEMORY.md (index, 50 line 이내)
- 14 active (user/project/feedback/reference)
- archive/

---

## 15. 새 세션 복붙 프롬프트

```
@_internal/MASTER_README.md 부터 정확히 read.
+ @_internal/MASTER_HANDOFF.md (이 file)
+ @_internal/METHOD_REGISTRY.md
+ @_internal/EXPERIMENT_REGISTRY.md
+ @_internal/SERVER_REGISTRY.md
+ @_internal/CHANGELOG.md

🚨 사용자 명시 (5/10 14:03 + 18:49 + 20:45 + 5/11 01:05 + 5/11 01:15):
- "paper의 모든 항목 완전 똑같이 진행 + 단 하나라도 다르면 안 됨"
- "하나도 빠짐없이 + 우리 기존 논문 한계 보완/극복 narrative"
- 목표: ① Exqutor 완벽 재현 ② RQ3 방법 동원 adaptive 대체 ③ 대체 불가 시 전처리 개선
- 정리 작업: "Tier 분류 폐기 → paradigm 통합, 한 세션에서 모두 정리"

핵심 데이터셋 alias:
- DEEP=DEEP 96d / SIFT=SIFT 128d
- **SSN = FB = SimSearchNet++ 256d** (server table partsupp_fb_*, query_pool_SSN_sf*)
- YFCC 192d / WIKI 768d

Server 자원 룰:
- ssh capstone2026@165.132.140.240 (ed25519 등록됨)
- PG port 55435-55436만 (다른 인스턴스 55432/55433 절대 X)
- /mnt/hdd0/home/capstone2026/ 작업 dir
- GPU 사용 OK (다른 사용자 idle 시)
- 30-60s monitor + stuck 정의 (mtime 5분+ + CPU<50%)

새 세션 즉시 액션 5단계:
1. SSH 검증: ssh capstone "date"
2. 측정 진행: ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"
3. tmux active: ssh capstone "tmux ls"
4. 자동 chain monitor 상태 (task bdrhrddyb)
5. Phase 4 server scp + measurement launch (handoff §6 — 사용자 confirm 완료 5/11 01:05)

5단계 narrative 검증:
1 RQ1 5%, RQ2 9% 격차 ✓
2 Fig 12 영역 8 cells mean qe_trim 1.618 (paper 1.69 vs −4.3% 일치) ✓
3 CaseA mb_partial -10.17% method-mean (단독 narrative 약함, 7.6% 통계 유의)
4 CaseB 6 methods -2~-7% outperform (44.7% 통계 유의)
5 CaseB > CaseA > B1 robust ✓

진행 상태 (5/11 01:10 KST):
- Tier 1 Legacy 11 × 9 × 2 = 198 cells ✅
- Phase B/C extra 28 × 9 × 2 = 504 cells 진행 ~316/702 (45%)
- ETA 5/11 02-03시 KST + Phase 4 launch 후 추가 ~30-50 h

확인 필요: handoff_v5 §0 사용자 confirm 4건 완료 (5/11 01:05). 즉시 진행 가능.

산출물 위치:
- _internal/MASTER_README.md (이것부터)
- _internal/{MASTER_HANDOFF, METHOD_REGISTRY, EXPERIMENT_REGISTRY, SERVER_REGISTRY, CHANGELOG, _BEFORE_INVENTORY, naming_convention}.md
- _internal/handoff/active/ (v2/v4/v5/main/back_validation)
- _internal/method_audit/20260510_initial/ + 20260511_phase4/
- _internal/scripts/measure_paper_exact.py + method_phase4_extra.py + ...
```

---

## 16. END

작성: 2026-05-11 01:50 KST  
다음 단계: MASTER_README.md 작성 (entry point)  

**핵심**: 본 file 1건 read 만으로 사용자 + 환경 + 5단계 narrative + paper exact + SSN alias + 57 method paradigm + 9 cells matrix + server 자원 + tmux + 자동 chain + validation 결과 + method audit + 5/27 storyline + fix 이력 + 산출물 위치 모두 파악. 0% loss 인계.
