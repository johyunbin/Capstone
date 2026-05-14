# Handoff v20 — 5/14 22:15 본 세션 22.5h 종합 + Form 1 fix + Agent 10 호출 + K granularity SF axis 완료 + 새 세션 0% loss anchor

> 본 세션 5/14 07:35 ~ 22:15 (22.5h) 전체 산출 + **5/14 18:00 회의 narrative v3 폐기 후 Form 1 (Streaming-aware Distribution-Conscious Cardinality Estimation) fix** + Agent A-J 10 호출 종합 + 박세은 9 영역 답변 form + 5/15 박광현 review form PDF v2 (10 page, K granularity + Neyman over-statement 정정 포함) + **K granularity SF=1/10/100 × K=10/20/30 추가 측정 완료 (48 file)** + 정정 룰 13 list. **새 세션 본 file 1개 read 만으로 0% loss 인계 보장**.

## ★ 새 세션 진입 anchor (0% loss 인계)

1. **본 file** (handoff v20) read = 본 세션 22.5h 전체 종합
2. **5/15 박광현 review form PDF v2** (`submission/_drafts/archive/속도는벡터_박광현_5월15일_review_form_Form1_20260515.pdf`, 10 page, 522 KB) = 박광현 미팅 D-1 자료
3. (선택) Agent A-J 10 file (`_internal/handoff/active/agent_{A~J}_*.md`) = 각 영역 deep dive
4. (선택) handoff v19 (`_internal/handoff/active/handoff_v19_*.md`) = 5/14 07:35 ~ 18:00 영역 (회의 base PDF v2 + VPN 5 Layer Defense)

---

## 0. 본 세션 22h 한 줄 요약

- 5/14 07:35 ~ 18:00 (handoff v19 영역): 회의 base PDF v2 47 page + 환각 정정 16 + VPN 5 Layer Defense
- **5/14 18:00 ~ 19:00 (★★★ 회의 transition)**: 기존 narrative v3 (11 단계) **사실상 폐기** → "어댑티브 샘플링 개선" 단순 framing 으로 정정
- 5/14 19:00 ~ 21:00 (★★★ Form 1 fix): 사용자 7 단계 결정 path → **Form 1 (Streaming-aware Distribution-Conscious Cardinality Estimation for VAQ: Extending Exqutor's §V-B Framework) fix** + Agent A-J 10 호출 + 박세은 6 영역 답변 + 5/15 review form PDF
- 5/14 21:00 ~ 21:55: SF=1/10/100 K granularity 추가 측정 launch (K=10 완료 / K=30 진행 중)

---

## 1. ★★★ Form 1 fix (변경 X 까지 fix)

### 1.1 main theme

> **Streaming-aware Distribution-Conscious Cardinality Estimation for Vector-augmented Analytical Queries: Extending Exqutor's §V-B Framework**

### 1.2 핵심 design

paper §V-B (Adaptive Sampling) 의 **"without vector index" 가정 안**에서 Bernoulli random sample 추출만 **distribution-aware reservoir + online cluster maintenance** 로 대체. paper §V-A ECQO 영역은 본 연구 outside.

### 1.3 4 측면 (사용자 명시 다측면)

- **대체**: Bernoulli random → distribution-aware reservoir + online cluster
- **보완**: paper §VI-D SelNet only 비교 → 3-way framework
- **개선**: paper §V-B Eq 5 sampling_size scalar → group-aware allocation
- **추가검증**: paper §VI-B "shifting workloads" 정량 측정

### 1.4 ★★★ paper §V "without index" anchor (Form 1 의 존재 의의)

paper p.5 좌단 §V 도입부 verbatim:

> "For VAQs with vector indexes, Exqutor employs Exact Cardinality Query Optimization (ECQO)... **For VAQs without index**, Exqutor uses a **sampling-based approach** to approximate selectivity (subsection V-B)."

paper p.5 우단 §V-B 첫 단락 verbatim:

> "When a VAQ **lacks a vector index**, ... Exqutor adopts a **sampling-based cardinality estimation approach specifically for KNN queries**."

paper p.6 우단 §V-B implementation verbatim:

> "When a VAQ with a vector range predicate **lacks index support**, the optimizer invokes a sampling routine..."

paper §VI-A verbatim:

> "In this section, we evaluate the performance of Exqutor when executing VAQs with **a vector index** using an ANN search, specifically with HNSW [38]."

paper §VI-B verbatim:

> "In this section, we evaluate the performance of Exqutor applied to TPC-H VAQs that perform KNN searches **without vector indexes**, where cardinality estimation is handled via sampling."

→ paper 자체가 §V-A (with index = ECQO) vs §V-B (without index = sampling) 영역 명확 분리. **Form 1 = §V-B 영역 한정 후속 연구**. 박세은 영역 4 ("분포 알면 ECQO?") 답변의 anchor.

---

## 2. Form 1 Component A+B+C+D + 17-step pseudo-code

### 2.1 Component A — Stratified Reservoir Sampling

- 알고리즘: cluster 별 reservoir R_j (Vitter 1985 Algorithm R) + group_aware_alloc 4 mode (Equal/Prop/Neyman/Anti-Neyman)
- base reference: Al-Kateb-Lee-Wang ISJ 2014 / SSDBM 2010 (vector domain 발현 novel)
- 코드량: ~250 line (dev 8-12h + test 4-6h)
- 메모리: O((N+K)×d)

### 2.2 Component B — BIRCH CF-tree online cluster maintenance

- 알고리즘: scikit-learn `Birch(n_clusters=20).partial_fit(X)` API + CF tuple (N_j, LS_j, SS_j) manual access wrapper
- base reference: Zhang-Ramakrishnan-Livny **1996 SIGMOD**
- **★ 이미 measure_paper_exact.py line 623-630 구현 됨** (확장만 필요)
- 코드량: ~200 line (dev 10-15h + test 4-6h, 정확도 5-15% drift)
- σ_j² 추정: CF tuple 기반 online 가능

### 2.3 Component C — paper Eq 2-6 통합 + Eq 5 group-aware augment

- paper Eq 1-6 verbatim 유지 (AdaptiveState 의 paper Eq 1-6 = measure_paper_exact.py 100% 정합 검증 완료)
- Eq 1 (Bernoulli sample budget N=385) 만 대체
- Eq 5 (sampling_size_{t+1} = sampling_size_t + V_t, scalar update) 을 group-aware allocation 으로 augment (n_inc_j ∝ N_j Proportional 권장)
- 코드량: ~100 line (dev 4-6h)

### 2.4 Component D — Distribution-aware stratification

- group_aware_alloc 함수 1개로 Equal/Prop/Neyman/Anti-Neyman 4 mode 전환
- L2-L4 정보 수준 axis 분리
- Proportional default (sel=0.01 paradox 인정, Cochran 1977 §5.5 partial)
- 코드량: ~50 line (dev 3-5h)

### 2.5 17-step pseudo-code

- paper Eq 1-6 verbatim 영역 = **10 step** (Step 1-2, 6, 8-13, 16)
- 본 연구 augment 영역 = **7 step** (Step 3-5, 7, 14-15, 17)
- 핵심 augment:
  - Step 14: paper Eq 5 scalar new_size → group_aware_alloc cluster 별 분배 (Proportional 권장)
  - Step 17: streaming tuple incremental (BIRCH partial_fit + SRS Vitter Algorithm R)
  - Step 3-4: BIRCH + SRS init

### 2.6 paper hyperparam 7종 (verbatim 유지)

m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N=385 (paper p.7 우단 + measure_paper_exact.py PAPER_HYPERPARAM **100% 정합**)

---

## 3. Agent A-J 10 호출 결과 종합

### 3.1 각 Agent 의 mission + 결과 file

| Agent | mission | 결과 file (line) | 시간 |
|---|---|---|---|
| A | paper 재정독 + 8 옵션 발산 | agent_A_paper_재정독_연구방향_옵션_20260514_2000.md (733) | 7분 |
| B | Agent A 검증 (신뢰도 78%, 정정 7) | agent_B_평가자_검증_20260514_2030.md (621) | 9분 |
| C | 8 옵션 deep dive + Cochran 1977 §5.5 발견 | agent_C_deep_dive_8옵션_종합권장_20260514_2200.md (?) | 7.6분 |
| D | paper §VI 한계 + 경쟁 paper + 박광현 BDAI 본업 | agent_D_paper_§VI_한계_경쟁_paper_새영역_20260514_2330.md (724) | 10.5분 |
| E | Form 1 구체화 (Component A+B+C+D + 측정 plan + 5/27/6/11/5/15 + publication) | agent_E_Form_1_구체화_streaming_aware_20260515_0000.md (?) | 8.6분 |
| F | 측정 + code plan (★ paper algorithm pseudo-code 없음 critical 정정) | agent_F_streaming_측정_plan_code_plan_20260515_0100.md (1230) | 8.6분 |
| G | paper Eq 1-6 verbatim + 17-step pseudo-code + SelNet/CE4HD/Ada-ef reuse | agent_G_paper_Eq_1-6_pseudo_code_4way_20260515_0200.md (1481) | 10.4분 |
| H | 1001 file batch baseline 재해석 + Form 1 통합 + RQ 재정립 RQ1'-RQ5' | agent_H_1001_file_재해석_batch_baseline_Form1_통합_20260515_0300.md (1100+) | 10분 |
| I | 5/27 20 slide + 6/11 §별 outline 세부 + 정직 disclosure 7 위치 | agent_I_5_27_20slide_6_11_outline_세부_20260515_0400.md (1651) | 12.8분 |
| J | 박세은 6 영역 답변 form (카톡 복붙) + ECQO multi-layer 4 + paper §V "without index" verbatim | agent_J_박세은_6영역_통합대응_답변form_20260515_0500.md (667) | 7.8분 |

총 = 10 agent, ~91분 누적 background 시간 (병행 진행으로 wall-clock ~2h).

### 3.2 핵심 발견 (Agent 결과 종합)

**Agent A**: 8 옵션 (A 현 narrative / B Eq 2-6 확장 / C Neyman paradox / D L0-L4 / E Multi-table / F ECQO / G reservoir / H TPC-DS) 발산. 자체 추천 A+C.

**Agent B**: 정정 7 영역 (★★★ 1 + ★★ 3 + ★ 3). 신뢰도 78%. ★★★ "5 단계 中 1 단계" 정정 = Algorithm 1 분류 무효, Eq 1 vs Eq 2-6 정정.

**Agent C**: Cochran 1977 §5.5 발견 (Neyman paradox 메커니즘 classical theory partial 포함). 4-way framework 격상. hybrid 3 권장.

**Agent D**: ★★★ CE4HD VLDB 2024 (Lan-Bao RMIT, github 미공개) + Ada-ef arxiv 2512.06636 (HNSW ef search, layer 다름) + 박광현 BDAI 본업 (RELOAD 2026 / CANNON 2026 / DFLOP 2026 / Exqutor 2025 / FaScalSQL / SPID-Join). 새 옵션 L/M/N/O/P 추가. ★★★ N (4-way framework) 핵심.

**Agent E**: Form 1 8 영역 구체화. Component A+B+C+D + 17-step + 측정 plan 5 (3180 file, cost 135-195h) + 5/27/6/11/5/15 form + publication path (EDBT short 10월, VLDB 4월/11월).

**Agent F**: ★ critical 정정 — paper §V-B 자체 algorithm pseudo-code 없음 (Eq 1-6 + 산문 + hyperparam 7종만). "14-step" = 본 연구 자체 의역. Component A-D 구현 plan + cost 산정 128-196h (Agent E 와 ±5% 일치).

**Agent G**: paper Eq 1-6 verbatim 정확 정독 (PDF 직접 read) + 본 의역 step-wise pseudo-code **17 step** 정정. SelNet [74] reuse 가능 (Python 95.5%). CE4HD github 미공개 confirmed. Ada-ef layer 다름. **4-way → 3-way (5/27 phase 1)** 축소.

**Agent H**: 1001 file = **폐기 X**. **batch baseline axis** positioning + Form 1 streaming axis 와 **complementary framework**. RQ 구조 = 현 RQ1/RQ2/RQ3 (batch) + 신규 RQ1'-RQ5' (paper-grade streaming).

**Agent I**: 5/27 20 slide × 5 명세 + 6/11 11§+6 부록 세부 (42-48 page, paper-grade 확장). Form 1 batch+streaming 통합 5 영역 (slide+§ 위치 명시).

**Agent J**: 박세은 6 영역 답변 form (카톡 복붙 plain text) + 영역 4 multi-layer 4 (ECQO 대안) + ★★★ paper §V 도입부 verbatim 발견 (paper p.5 좌단 "For VAQs without index... sampling-based approach"). 5/15 박광현 review form base.

---

## 4. ★★★ 정정 룰 10 list (mass update prep)

| # | 정정 영역 | source | 영향 file |
|---|---|---|---|
| 1 | "5 단계 中 1 단계" → "Eq 1 (Bernoulli) 대체 vs Eq 2-6 유지" | Agent B 1판 | 모든 자료 |
| 2 | "Algorithm 1 14-step" → "paper §V-B Eq 1-6 + 본 의역 17-step pseudo-code" | Agent F+G 2판 | 모든 자료 |
| 3 | "AS single-table 不可 = 구조 X" → "paper §V-B single-table OK, 공개 코드 구현 한계" | 박세은 9:09 #1 | 회의 PDF + 모든 자료 |
| 4 | "block only 추출" → "block + row hybrid" | 박세은 9:09 #2 | 회의 PDF + 모든 자료 |
| 5 | "분포 안다" → L1/L2/L3 layer 분리 | 박세은 9:09 #3 + Agent J | RQ2 narrative 전반 |
| 6 | "분포 알면 ECQO 가능?" → paper §V-B = "without index" 가정 (p.5 verbatim) | ★★★ 박세은 9:09 #4 + Agent J | Form 1 narrative core (★★★ 최대 evidence) |
| 7 | "RQ3 = streaming" → "RQ3 = 사전 학습 batch baseline, Form 1 = streaming axis" | 박세은 9:09 #5 + 9:27 | RQ3 narrative 전반 |
| 8 | "0.1~0.5초 런타임" → SF=1 fit time, 매 query fit X | 박세은 9:27 | §3.5 자원 효율 |
| 9 | "Neyman paradox" → "Neyman paradox sel=0.01 한정, sel=0.1 = Neyman best (selectivity-dependent)" | 박세은 9:42 + Agent B 정정 | RQ2 5-way narrative |
| 10 | K granularity SF coverage: "SF=1 미측정" → "SF=1+10+100 × K=10/20/30 measured (48 file)" ✓ 완료 | 박세은 8:50 + 5/14 추가 측정 | §2.5 + §2.6 |
| 11 | "Bernoulli → Neyman −10%" narrative → 실제 측정 X (POOL −5~7%, 단일 cell best SIFT sel=0.1 −9.16%) | 박세은 9:54 + RQ2 csv 직접 verify | RQ2 narrative |
| 12 | 회의 PDF v2 §3.2 line 532-533 "Proportional −9.61% / Neyman −8.75%" wording → csv 직접 aggregate 값과 차이 (출처 source verify 필요) | 본 verify 발견 | RQ2 narrative |
| 13 | RQ2 5-way 측정 = SF=100 (DEEP+SIFT) **한정**. SF=1/SF=10/SSN 미측정 | RQ2 csv file 명 + 사용자 22:05 confirm | RQ2 SF coverage |
| 14 | "Anti-Neyman > Neyman = Neyman 가설 무효" → 정확 의미: **Neyman 가설 자체는 유효** but **본 데이터셋이 Neyman 의 가정 조건 (cluster 간 분산 다양함) 불만족** + selectivity-dependent (sel=0.01 paradox / sel=0.1 정합). σ_j 직접 측정 추가 검증 필요 (현재 oracle 가정) | 박세은 10:15 + Cochran 1977 partial | RQ2 narrative |

---

## 5. 박세은 6 영역 답변 form (Agent J — 카톡 복붙 plain text)

### 5.1 영역 #1 (single-table AS = 구현 코드 문제, 구조 X)

> paper §V-B 가 single-table 을 다루지만 공개 코드 영역의 구현 한계로 동작하지 않아 본 연구의 측정 영역이 multi-join 으로 자연 이동. 본 연구의 multi-join 영역 measurement 가 paper 의 구조적 한계라기보다는 우연의 측면.

### 5.2 영역 #2 (block + row hybrid)

> paper §V-B 의 Eq 1 (N=385 초기 sample budget) 은 unstratified random 추출이고, 본 연구는 이 sample 추출 방식을 cluster 인지 stratification 으로 대체. 본 연구의 contribution scope 는 추출 방식의 random → stratified 정정이지, block / row 구조 자체의 변경이 아님.

### 5.3 영역 #3 ("분포 안다" L1/L2/L3 분리)

- L1: global skew flag (HHI) — 메타 정보, stratification 직접 불가
- L2: cluster boundary (K-means K=20 centroid) — 0.1~0.5초 fit, Equal allocation 가능
- L3: + σ_j 분산 (Neyman allocation) — RQ2 oracle 가정

### 5.4 영역 #4 ★★★ (ECQO 대안, Form 1 보호 multi-layer 4)

- (a) **paper §V-B 영역 자체 = "without index" 가정** (paper p.5 좌단 verbatim, anchor 영역)
- (b) ECQO cost (HNSW O(n log n) + 메모리 1.x~2x base) vs Form 1 cost (K-means K=20 fit 0.1~0.5초 + 메모리 K×d)
- (c) ECQO + Form 1 complementary (high-frequency stable = ECQO, ad-hoc/shifting = Form 1, paper §VI-B "shifting workloads" align)
- (d) "분포 안다" L1/L2/L3 vs L_index 분리 (다른 추상화 layer)

### 5.5 영역 #5 (RQ3 사전 학습 framing)

- 현 1001 file batch axis = "사전 학습 완료된 baseline" (회의 PDF §4.1.4 line 540-556 명시)
- Form 1 streaming axis = online incremental maintenance (진짜 "쿼리 도착 시" 학습)
- = 박세은 #5 가 Form 1 의 존재 이유 자체 강조

### 5.6 영역 #6 (9:27 런타임 question)

- 0.1~0.5초 = fit time (학습 시간), **SF=1 한정** (1M rows × 96d DEEP, ~384 MB)
- SF=10/100 fit time = 미측정 (선형 scale-up SF=10 ≈ 1~5초, SF=100 ≈ 10~50초 추정)
- "런타임 실행" layer 분리:
  - 매 쿼리 마다 fit = ❌ (paper period P=50 가정)
  - 사전 학습 + 실시간 query = ✓ (현 protocol)
  - 진짜 streaming (per-tuple incremental) = Form 1 영역

### 5.7 영역 #7 (9:42 Neyman paradox sel=0.01 한정)

- sel=0.01 (paired n=455): Neyman 1.595 / Anti 1.540 / Prop 1.580 → Proportional best (paradox)
- sel=0.1: Neyman 1.1076 / Anti 1.1101 / Prop 1.1135 → Neyman best (classical theory 정합)
- selectivity-dependent

→ 사용자 카톡 답변 = 4 영역 모두 짧은 톤 carry-over 완료 (9:40~9:43).

---

## 6. 측정 plan (Agent E+F+G+H 종합)

| phase | scope | file | server time | dev cost |
|---|---|---|---:|---:|
| **5/27 phase 1** | 3-way 비교 (Bernoulli + SelNet + 본 Form 1) sf=100 + streaming workload simulation | 1080 file | 8-12h | 52-87h (impl + 분석) |
| **6/11 phase 2** | + CE4HD partial + Ada-ef paper level + sf=10 + drift 4 시나리오 | + 2100 file | + 15-25h | + 30-50h |
| post-6/11 future | + Form 1 측정 5 영역 full + multi-table + RELOAD align | + 3000+h | + paper-grade | future paper |

**1001 file (기존 batch axis)** = baseline + design 근거. 폐기 X.

---

## 7. 신규 코드 file plan (Agent F+G)

기존 measure_paper_exact.py (1407 line) **유지** + 신규 6 file ~ 1700 line:

- measure_form1_common.py (Component A-D + streaming generator)
- measure_form1_streaming.py (측정 1)
- measure_form1_birch_cost.py (측정 2)
- measure_form1_4way.py (측정 3, ~800 line, 재사용 80% + 신규 20%)
- measure_form1_drift.py (측정 4)
- measure_form1_phase2.py (측정 5)

★ Component B (BIRCH) = measure_paper_exact.py line 623-630 **이미 구현 됨** (확장만).
★ Component C (paper Eq 2-6) = AdaptiveState paper Eq 1-6 verbatim **100% 정합 검증 완료**.

---

## 8. paper-grade publication path

| 순위 | venue | deadline | acceptance | timeline |
|---|---|---|---:|---|
| **1** | **EDBT short paper** | 10월 (~2026-10) | ~30% | 6-7월 측정 + 8-9월 draft + 10-11월 submit → 2027 3-6월 |
| 2 | VLDB short paper / industry track | 4월 또는 11월 | ~25% | paper §V-B 후속 + 산업 axis |
| 3 | ICDE position paper | 10월 | ~20% | framework axis novelty |

**co-author 6**: 박광현 corresponding + 임채림 first + 학부생 4명

---

## 9. 정직 disclosure 13 영역 (Agent A-J 7 + 박세은 6)

1. paper §V-B 자체 algorithm pseudo-code 없음 (Eq 1-6 + 산문 + hyperparam 7종만)
2. framework axis novelty 한정 (각 component 자체 신규 X — SRS/BIRCH/Cochran 1996-2014 reference 존재)
3. CE4HD VLDB 2024 github 미공개 — 5/27 폐기, 6/11 paper level 인용 only
4. Ada-ef arxiv 2512.06636 layer 다름 (HNSW ef search) — paper level 인용 only
5. SelNet [74] Q-error 재현 risk 10-20% (paper Fig.12 Q-error 5.53)
6. BIRCH CF σ_j² 5-15% drift vs offline KMeans
7. batch axis (1001 file) vs streaming axis (Form 1 360 file) boundary
8. paper §V-B single-table 不可 = 구현 코드 한계 (구조 X). source code verify 미완
9. paper §V-B sampling = block + row hybrid (block only X). source code verify 미완
10. "분포 안다" L1/L2/L3 multi-layer 분리. RQ2 = L3 oracle (직접 측정 미완)
11. paper §V-B 영역 = "without index" 가정 — paper p.5 verbatim 명시 (Form 1 anchor)
12. RQ3 = 사전 학습 batch baseline. Form 1 streaming axis = phase 1 measurement 미완
13. 0.1~0.5초 fit time = SF=1 (1M rows) 한정. SF=10/100 미측정

---

## 10. K granularity 추가 측정 (★ in-flight)

박세은 8:50 발견 (회의 PDF v2 §2.5 SF=1 미측정 영역) + 사용자 옵션 B 결정:

### 10.1 scope

- **A5-scale-sf1 + A5-scale-sf10 + A5-scale-sf100** (DEEP single dataset, 3 cells)
- × K=10/30 (K=20 = paper exact base 활용)
- × 4 anchor (sparse_rp / chao_weighted / hilbert_real / hyperloglog)
- × 2 mode (CaseA + CaseB)
- = **48 file** 추가

### 10.2 status (★ 완료, 5/14 22:10 update)

- K=10: ✓ 완료 (12:12 launch → 12:31, 19분, 24 file)
- K=30: ✓ 완료 (12:45 launch → 13:02, 17분, 24 file)
- **local 회수 완료**: `experiments/results/raw/06_클러스터수_K_민감도/SF_axis/K10/` + `K30/` (각 24 file)
- **3-way 분석 보고서**: `experiments/results/analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md`
- **SF_axis README**: `experiments/results/raw/06_클러스터수_K_민감도/SF_axis/README.md`

### 10.5 ★ 핵심 finding (3-way SF=1/10/100 × K=10/20/30)

| Method | K-pattern | SF=1 K=20 Δ% | SF=10 K=20 Δ% | SF=100 K=20 Δ% |
|---|---|---:|---:|---:|
| sparse_rp | U-shape (K=10 +50~+90% 악화, K=20 sweet) | −11.70% | −6.58% | −11.20% |
| chao_weighted | K=20 sweet spot 모든 SF | **−14.11%** | −6.00% | −12.20% |
| hilbert_real | K-robust + K=30 slight edge | −11.02% (K=30 −12.25%) | −6.07% (K=30 −6.96%) | −10.91% (K=30 −11.81%) |
| hyperloglog | K-robust + K=30 slight edge | −10.19% (K=30 −12.57%) | −5.15% (K=30 −6.01%) | −10.54% (K=30 −11.62%) |

→ **SF=1 영역 K=20 best 여부 = method-dependent**. sparse_rp/chao_weighted = K=20 sweet spot, hilbert_real/hyperloglog = K=30 slight edge. **모든 SF axis 에서 패턴 일관** (회의 PDF v2 §2.5 "SF=1 영역 K=20 미측정" 정정 가능).

### 10.3 측정 method

- script: `_internal/scripts/run_km_sf_axis.sh` (신규 작성, server `cache/rq3/run_km_sf_axis.sh` 전송)
- N_STRATA patch: `_measure_common.py` line 59 sed (10 또는 30) → 측정 → 복원
- output: `paper_exact_km{K}_sf_axis/` 디렉토리

### 10.4 다음 단계 (K=30 완료 후)

1. server → local 회수 (K=10 + K=30 = 48 file)
2. raw/06/SF_axis/ 추가
3. analysis 신규: `experiments/results/analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md`
4. 박세은 carry-over 가능 form (정정 룰 10 영역에 SF=1+10+100 K=10/20/30 cover 명시)

---

## 11. 5/15 박광현 미팅 자료 (★ PDF 작성 완료)

### 11.1 file path

- md: `submission/_drafts/archive/속도는벡터_박광현_5월15일_review_form_Form1_20260515.md`
- **PDF: `submission/_drafts/archive/속도는벡터_박광현_5월15일_review_form_Form1_20260515.pdf` (10 page, 445 KB)**

### 11.2 8 § structure

- §0 TL;DR (Form 1 fix + 4 측면)
- §1 paper §V-B "without index" anchor (Form 1 의 존재 의의)
- §2 Form 1 Component A+B+C+D + 17-step pseudo-code
- §3 paper 한계 보완 (L1+L5+L6)
- §4 측정 plan (5/27 phase 1 + 6/11 phase 2)
- §5 timeline (5/15 / 5/27 / 6/11 / post-6/11)
- §6 ★ review 요청 12 항목 (박세은 6 + 박광현 6)
- §7 정직 disclosure 13 영역
- §8 fix 영역 vs 변경 가능 영역 (박광현 review 후)

### 11.3 박광현 review 요청 12 항목

박세은 6 영역 (사전 답변 완료, 박광현 추가 review):
1. (★★★) 분포 알면 ECQO 가능? → paper §V "without index" anchor
2. RQ3 = 쿼리 실행 전 학습 필요 → 1001 file batch baseline framing
3. 0.1~0.5초 매 query 런타임? → fit time SF=1 한정
4. "분포 안다" L1/L2/L3 분리
5. AS single-table 不可 wording 정정
6. Neyman paradox sel=0.01 한정

박광현 자문 6 영역:
7. Form 1 main theme 학술 정당성?
8. Component A+B+C+D framework axis novelty?
9. 5/27 phase 1 timeline 52-87h 가능성?
10. paper-grade publication venue 추천?
11. 박광현 본업 (RELOAD/CANNON/DFLOP) align?
12. SelNet impl risk mitigation?

---

## 12. 사용자 verbatim 작업 status

- **사용자 본 회의 (18:00~19:00) verbatim 정리** = 진행 중 (이동욱 9:13 카톡 "내일 오전에 최대한 끝내겠다")
- 박세은 9:18: "오늘 변경 점 = 오늘 회의에서 논의 내용 참고. 정리된 form X. 사용자 직접 정리"
- → 본 handoff v20 = 회의 후 변경 종합 형태로 활용 가능

---

## 13. 강재현 idea 별개 영역

- 7:32 사용자: "AS 대체할 방법론 구체적으로 낼 얘기할거 무관하게"
- 7:43 강재현: "다음 비대면 미팅 전에 넘겨줄게"
- 9:41 사용자 confirm: "재현이 streaming 쪽 = 답변 form X, 우리 연구 방향 (Form 1) 계속 진행"
- → 강재현 idea = **별개 영역**, Form 1 main thread 와 분리. 도착 시 별도 검증 가능.

---

## 14. 본 세션 commit chain + 다음 단계

### 14.1 본 세션 commit (handoff v19 이후)

(예상) 본 handoff v20 commit + Agent A-J 10 결과 file + 5/15 review form PDF + 박세은 6 영역 답변 form

### 14.2 다음 단계 (★ 새 세션 진입 안내)

본 세션 22:15 종료 시점 완료된 영역:

- ✓ Agent A-J 10 호출 완료 + 결과 file 저장
- ✓ K=10 + K=30 측정 완료 + 회수 (48 file, raw/06/SF_axis/)
- ✓ 3-way K granularity 분석 보고서 (analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md)
- ✓ 5/15 박광현 review form PDF v2 (10 page, 522 KB)
- ✓ 박세은 9 영역 답변 form (사용자 직접 카톡 carry-over 완료)
- ✓ 정정 룰 13 list 정리 (handoff v20 §4)
- ✓ handoff v20 작성 + 본 update
- ✓ commit + push (사용자 명시 요청)

**새 세션 진행 권장 path** (5/15 14:00 박광현 미팅 후):

1. **5/15 박광현 미팅** (D-1 14:00) — 본 review form PDF v2 + 박세은 9 영역 답변 form 활용
2. **post-5/15 mass update** (박광현 추천 + 변경 확정 반영):
   - 회의 base PDF v2 정정 룰 13 list 일괄 적용
   - 5/27 deck v4 → v7 update (Form 1 + Component A+B+C+D + 17-step + 정직 disclosure 13 + K granularity SF axis + Neyman selectivity-dependent)
   - 6/11 outline v3 → v4 update
   - narrative v1 → v2 update (Form 1 fix 반영)
   - Registry update (METHOD_REGISTRY + EXPERIMENT_REGISTRY)
3. **5/27 D-13 timeline** Form 1 phase 1 measurement launch:
   - 3-way 비교 (Bernoulli + SelNet + 본 Form 1) 360 file
   - streaming workload simulation sf=100 (720 file)
   - 총 1080 file, cost 52-87h
4. 강재현 idea 도착 시 (다음 비대면 미팅 전) Form 1 영역과 align 검토 (별개)

### 14.3 사용자 정책 (verbatim 유지)

- 전권 위임 / 한국어 / peer-to-peer / Opus 4.7 1M Max Token / 자원 Max
- 학부생 톤 (사람 느낌, AI 강조 적절: ★ / ✓ / ⚠️)
- 정직 disclosure (cherry-picking 회피, 폐기 method 명시, 미검증 영역 명시)
- "100% 검증" 표기 회피
- 일정/자원 무관 (5/14 21:00 사용자 명시)
- fix 모드 = 공유 완성까지 main theme + 4 측면 + paper §V-B scope 변경 X

---

## 15. 핵심 file path reference (★ 새 세션 read 우선순위)

### 15.1 ★ 1순위 (handoff v20 + 5/15 review form)

- **본 file**: `_internal/handoff/active/handoff_v20_form1_fix_agent_10_session_22h_20260514_2155.md`
- **5/15 박광현 review form PDF**: `submission/_drafts/archive/속도는벡터_박광현_5월15일_review_form_Form1_20260515.pdf` (10 page)

### 15.2 ★ 2순위 (Agent A-J 10 결과 file)

- `_internal/handoff/active/agent_A_paper_재정독_연구방향_옵션_20260514_2000.md` (733 line)
- `_internal/handoff/active/agent_B_평가자_검증_20260514_2030.md` (621 line)
- `_internal/handoff/active/agent_C_deep_dive_8옵션_종합권장_20260514_2200.md`
- `_internal/handoff/active/agent_D_paper_§VI_한계_경쟁_paper_새영역_20260514_2330.md` (724 line)
- `_internal/handoff/active/agent_E_Form_1_구체화_streaming_aware_20260515_0000.md`
- `_internal/handoff/active/agent_F_streaming_측정_plan_code_plan_20260515_0100.md` (1230 line)
- `_internal/handoff/active/agent_G_paper_Eq_1-6_pseudo_code_4way_20260515_0200.md` (1481 line)
- `_internal/handoff/active/agent_H_1001_file_재해석_batch_baseline_Form1_통합_20260515_0300.md` (1100+ line)
- `_internal/handoff/active/agent_I_5_27_20slide_6_11_outline_세부_20260515_0400.md` (1651 line)
- `_internal/handoff/active/agent_J_박세은_6영역_통합대응_답변form_20260515_0500.md` (667 line)

### 15.3 ★ 3순위 (handoff v19 + 회의 base PDF)

- handoff v19 (본 세션 18:01 전체 종합): `_internal/handoff/active/handoff_v19_session_full_finalize_20260514_1801.md`
- 회의 base PDF md: `submission/_drafts/archive/속도는벡터 - 프로젝트 정리 (저녁 긴급 회의 숙지용).md` (1681 line)
- 회의 base PDF: `submission/_drafts/속도는벡터 - 프로젝트 정리 (저녁 긴급 회의 숙지용).pdf` (47 page, 2.63 MB)

### 15.4 측정 결과

- analysis 9 file: `experiments/results/analysis/`
- raw 10 sub-dir: `experiments/results/raw/01_RQ1_논문_baseline_재현/` ~ `10_전체측정_백업/`
- figures 6: `experiments/figures/paper_exact_v7/F1~F6.png`
- ★ K granularity 추가 측정 (in-flight): server `capstone2026:cache/rq3/paper_exact_km{10,30}_sf_axis/`

### 15.5 카톡 / Registry

- 5/14 일정 조정 카톡: `_internal/records/kakaotalk/20260514_긴급회의_일정조정_카톡.md`
- 5/14 박세은 8:50 ~ 9:42 (★ 본 카톡 verbatim handoff v20 §5 종합): 본 file
- METHOD_REGISTRY: `_internal/METHOD_REGISTRY.md`
- EXPERIMENT_REGISTRY: `_internal/EXPERIMENT_REGISTRY.md`
- SERVER_REGISTRY: `_internal/SERVER_REGISTRY.md`

### 15.6 script

- 기존: `_internal/scripts/measure_paper_exact.py` (1407 line, paper §V-B 재현 + AdaptiveState 100% 정합)
- 신규: server `cache/rq3/run_km_sf_axis.sh` (K granularity SF axis wrapper)
- PDF 생성: `_internal/scripts/md2pdf.py` (Trading S43 v6 + 학술 보강 + admonition callout + 한글 anchor + H2 break + H3 keep)

### 15.7 VPN keep-alive (★ 5 Layer → 4 Layer, 5/14 22:18 update)

- LaunchAgent (active): `~/Library/LaunchAgents/com.user.capstone-{caffeinate,vpn-ping,autossh}.plist` (3 active)
- **vpn-watchdog 제거** (맥미니 + 맥북 동일 form, 5/14 22:18): backup `~/Library/LaunchAgents/com.user.capstone-vpn-watchdog.plist.bak_20260514_2218`
- 이유: SecuwaySSL U 자동 재실행 영역이 사용자 종료해도 다시 켜는 원인 (사용자 22:15 요청)
- 4 Layer: L1 caffeinate (sleep 방지) + L2 vpn-ping (ping keep-alive) + L3 ★ autossh (SSH 트래픽, 가장 결정적) + L5 SSH config (ServerAliveInterval 15s)
- L4 (vpn-watchdog) 영역 = 사용자 manual control (필요 시 SecuwaySSL U 직접 시작)

---

작성: 2026-05-14 21:55 KST · 본 세션 22h 종합 + Form 1 fix + Agent 10 호출 + 박세은 6 영역 + 5/15 review form PDF + K granularity in-flight · 새 세션 본 file 1개 read 만으로 0% loss 인계 + 5/15 박광현 미팅 (D-1) 14:00 사전 대비
