---
title: 속도는벡터 × 박광현 교수 미팅 (5/15) — Form 1 review form
subtitle: 본 연구 fix 결정 + paper Exqutor §V-B 후속 + review 요청 항목
date: 2026-05-15 14:00 KST
team: 속도는벡터 (박세은 · 강재현 · 조현빈 · 이동욱)
---

## 0. TL;DR — 본 연구 결정 fix

**main theme** (fix, 변경 X 까지 fix):

> **Streaming-aware Distribution-Conscious Cardinality Estimation for Vector-augmented Analytical Queries: Extending Exqutor's §V-B Framework**

paper §V-B (Adaptive Sampling) 의 **"without vector index" 가정 안**에서 Bernoulli random sample 추출만 **distribution-aware reservoir + online cluster maintenance** 로 대체. paper §V-A ECQO 영역은 본 연구 outside.

**4 측면**: 대체 (Bernoulli random → stratified reservoir) / 보완 (paper §VI-D SelNet only → 3-way framework) / 개선 (paper §V-B Eq 5 sampling_size scalar → group-aware) / 추가검증 (paper §VI-B shifting workloads 정량)

---

## 1. paper §V-B 영역 anchor (Form 1 의 존재 의의)

paper p.5 좌단 §V 도입부 verbatim:

> "For VAQs with vector indexes, Exqutor employs Exact Cardinality Query Optimization (ECQO)... **For VAQs without index**, Exqutor uses a **sampling-based approach** to approximate selectivity (subsection V-B)."

paper p.5 우단 §V-B 첫 단락 verbatim:

> "When a VAQ **lacks a vector index**, ... Exqutor adopts a **sampling-based cardinality estimation approach specifically for KNN queries**."

→ paper 자체가 ECQO (with index) vs §V-B (without index) 영역 명확 분리. **Form 1 = §V-B 영역 한정 후속 연구**.

---

## 2. Form 1 Component A+B+C+D

| Comp | 영역 | base reference | 본 contribution |
|---|---|---|---|
| **A** Stratified Reservoir Sampling | cluster 별 reservoir R_j (Vitter 1985 Algorithm R) | Al-Kateb-Lee-Wang ISJ 2014 SRS / SSDBM 2010 | vector similarity domain 발현 |
| **B** BIRCH CF-tree online cluster maintenance | (N_j, LS_j, SS_j) tuple incremental | Zhang-Ramakrishnan-Livny 1996 SIGMOD | paper period P=50 align |
| **C** paper Eq 2-6 통합 + Eq 5 group-aware augment | scalar new_size → cluster 별 분배 | paper §V-B Eq 1-6 verbatim 100% 정합 | n_inc_j ∝ N_j (Proportional 권장) |
| **D** Distribution-aware stratification | Equal/Prop/Neyman/Anti-Neyman + L2-L4 axis | RQ2 5-way baseline | Proportional default (sel=0.01 paradox 인정) |

본 연구 의역 step-wise pseudo-code = paper Eq 1-6 verbatim **10 step** + 본 augment **7 step** = **17 step**. (paper 자체에는 algorithm pseudo-code 없음, Eq 1-6 + 산문 + hyperparam 7종 m=0.9/η₀=0.1/α=50/β=1.5/γ=0.99/period=50/N=385)

---

## 3. paper 한계 보완 (L1+L5+L6)

| ID | paper verbatim | 본 보완 |
|---|---|---|
| **L1** | §VI-B "sample size trajectory varies depending on the dataset" + "shifting workloads" | Component B+C distribution shift augment |
| **L5** | §VI-D SelNet only 비교 (CE4HD VLDB 2024 미비교) | **3-way framework** (Bernoulli + SelNet + 본 Form 1) — 5/27 phase 1 |
| **L6** | §VII paper differentiation = sampling overhead 동적 axis (vs Lipton-Naughton 1990) | Component A+B streaming-aware base |

---

## 4. 측정 plan

| phase | scope | file | cost |
|---|---|---|---|
| **5/27 phase 1** | 3-way 비교 (Bernoulli + SelNet + 본) + streaming workload simulation sf=100 | 1080 file | 52-87h |
| **6/11 phase 2** | + CE4HD partial + Ada-ef paper level + sf=10 streaming + drift 4 시나리오 | + 2100 file | + 30-50h |
| post-6/11 future | + Form 1 measurement 5 영역 full + multi-table + RELOAD align | + 3000h | post-paper-grade |

**1001 file (기존 batch axis)** = baseline + design 근거 (사전 학습 완료된 baseline framing). 폐기 X, complementary 영역.

---

## 5. timeline

- **5/14 18:00** 회의 narrative v3 폐기 + Form 1 fix
- **5/15 (D-1) 14:00** 박광현 미팅 (본 form)
- **5/27 (D-13)** 발표 phase 1
- **6/11 (D-29)** 보고서 phase 1 full + phase 2 partial
- **post-6/11**: EDBT short paper 10월 deadline (paper-grade publication 시도)

co-author: 박광현 corresponding + 임채림 first + 학부생 4명 (박세은 / 강재현 / 조현빈 / 이동욱)

---

## 6. ★ review 요청 항목 (12 영역)

박세은 9:09 + 9:27 영역 6 (이미 자체 답변 form 작성 + Form 1 통합) + 박광현 자문 6 = **12 항목**:

**박세은 영역 (사전 답변 완료, 박광현 추가 review 요청)**:

1. (★★★ critical) "분포 알면 ECQO 가능?" → paper §V 도입부 verbatim ("without index" 가정) anchor. Form 1 = §V-B 영역 한정. 박광현 의견?
2. "RQ3 = 쿼리 실행 전 학습 필요" → 1001 file = 사전 학습 batch baseline framing. Form 1 streaming axis = 진짜 online incremental. 박광현 의견?
3. "0.1~0.5초 매 query 런타임?" → fit time SF=1 한정. 매 query fit X (paper period P=50 가정). Form 1 = per-tuple amortized. 박광현 의견?
4. "분포 안다" L1/L2/L3 분리 + paper §V-B 영역 = L_index outside. 박광현 의견?
5. "AS = single-table 不可" wording 정정 (구조 X = 구현 한계). 정확 framing 권장?
6. "Neyman paradox" → sel=0.01 한정 (sel=0.1 = Neyman best classical theory 정합). 정확 framing 권장?

**박광현 자문 6 영역**:

7. Form 1 main theme (Streaming-aware Distribution-Conscious) 학술 정당성?
8. Component A+B+C+D framework axis novelty 평가 (개별 component 자체 신규 X — SRS/BIRCH/Cochran 1996-2014 reference 존재. framework 통합 novel)?
9. 5/27 phase 1 timeline 52-87h 가능성?
10. paper-grade publication venue 추천 (EDBT short / VLDB short / ICDE position 中)?
11. 박광현 본업 영역 (RELOAD / CANNON / DFLOP) align 가능성?
12. SelNet impl 8-12h cost + Q-error 재현 risk 10-20% — 5/27 phase 1 risk mitigation 권장?

---

## 6.5 ★ K granularity SF=1/10/100 추가 측정 결과 (5/14 22:00 완료, 박세은 8:50 후속)

박세은 8:50 발견 (회의 PDF v2 §2.5 SF=1 미측정) → 사용자 옵션 B 결정 → 추가 측정 완료. A5-scale-sf{1,10,100} (DEEP single, 3 cells) × K=10/30 × 4 anchor (sparse_rp/chao_weighted/hilbert_real/hyperloglog) × CaseA/CaseB = **48 file 추가**.

| Method | K-pattern | SF=1 K=20 Δ% | SF=10 K=20 Δ% | SF=100 K=20 Δ% |
|---|---|---:|---:|---:|
| sparse_rp | U-shape (K=10 +50~+90% 악화, K=20 sweet) | −11.70% | −6.58% | −11.20% |
| chao_weighted | K=20 sweet spot 모든 SF 일관 | **−14.11%** | −6.00% | −12.20% |
| hilbert_real | K-robust + K=30 slight edge | −11.02% (K=30 −12.25%) | −6.07% (K=30 −6.96%) | −10.91% (K=30 −11.81%) |
| hyperloglog | K-robust + K=30 slight edge | −10.19% (K=30 −12.57%) | −5.15% (K=30 −6.01%) | −10.54% (K=30 −11.62%) |

→ **SF=1 영역 K=20 best 여부 = method-dependent**. sparse_rp/chao_weighted = K=20 sweet spot. hilbert_real/hyperloglog = K=30 slight edge.

→ **SF=10 영역 약한 효과 (−5~−7%)** = data size U-shape 가능성, paper §VI-B "shifting workloads" 정합. future work.

→ 회의 PDF v2 §2.5 "SF=1 영역 K=20 미측정" wording 정정 가능: **SF=1+10+100 axis 모두 측정 완료**, method-dependent K best 패턴 일관.

상세 분석: `experiments/results/analysis/km_granularity_sf_axis_SF1_SF10_SF100_20260515.md`

---

## 6.6 박세은 9:42 + 9:54 영역 — Neyman selectivity-dependent + over-statement 정정

박세은 9:42: "neyman 이 propotional 보다 좋은 건 sel=0.1 영역에서 맞음" (selectivity-dependent confirmed)
박세은 9:54: "전 q error 10% 감소 결과가 bernoulli 대비 neyman 이라고 생각했었어요..."

RQ2 5-way csv (rq2_DEEP_sf100_5way_allocation.csv + rq2_SIFT_sf100_5way_allocation.csv) 직접 aggregate verify:

| dataset | sel | Neyman vs Bernoulli Δ% |
|---|---|---:|
| DEEP | 0.01 | −7.64% |
| DEEP | 0.1 | −4.59% |
| SIFT | 0.01 | −2.58% |
| SIFT | 0.1 | **−9.16% (가장 가까움)** |
| POOL | 0.01 | −5.16% |
| POOL | 0.1 | −6.94% |

→ **"Bernoulli → Neyman −10%" narrative = over-statement** (실제 −5~−9% 범위, 가장 큰 단일 cell = SIFT sel=0.1 의 −9.16%).

→ 회의 PDF v2 §3.2 line 532-533 "Proportional −9.61% / Neyman −8.75%" wording = csv 직접 aggregate (POOL Proportional −6.76% / Neyman −5.16%) **와 일치 X**. 출처 source verify 필요.

→ **RQ2 5-way 측정 = SF=100 (DEEP+SIFT) 한정**. SF=1/SF=10/SSN 미측정.

---

## 6.7 박세은 9:09 #2 영역 (block + row hybrid) + 본문 답변 form 압축

박세은 9:09 #2 영역 (5/14 카톡): "block 단위 추출이 아니라 block + row hybrid 일 가능성?"

paper §V-B Eq 1 (N=385 초기 sample budget) 이 unstratified random row 추출이고, Eq 5 (sampling_size_{t+1} 동적 update) 가 row 단위. block sample 영역은 paper §V-B 자체 명시 X (paper §IV.6 row group block 영역과 영역 다름 — §IV.6 = HDF 데이터 layout, §V-B = sampling allocation). **본 연구 contribution scope = 추출 방식 random → stratified 정정, block/row 구조 outside**. paper source code level verify 미완 (정직 disclosure #9).

박광현 정확 framing 권장?

**박세은 9 영역 답변 form 압축** (agent_J §1 base, full form 47.9 KB 자세 contents = `_internal/handoff/active/agent_J_박세은_6영역_통합대응_답변form_20260515_0500.md`):

1. (★★★) 분포 알면 ECQO? → paper §V "without index" anchor. ECQO = HNSW (data graph, fit O(n log n) + memory base×1.x~2x), 본 = K-means K=20 메타 (15KB). cost 2-3 order 차이. complementary scenario (high-frequency stable = ECQO / ad-hoc/shifting = Form 1, paper §VI-B align).
2. RQ3 사전 학습 → 1001 file = batch baseline (cold start 1 회 fit 0.1-0.5초 + query ms). Form 1 streaming axis = per-tuple incremental online maintenance.
3. 0.1~0.5초 매 query? → fit time SF=1 한정, cold start 1 회. 매 query fit X (paper period P=50 가정). Form 1 = per-tuple amortized.
4. L1/L2/L3 → L1 (global skew flag, HHI) / L2 (cluster centroid, K-means K=20) / L3 (+σ_j Neyman). RQ2 = L3 oracle 가정. L_index = paper §V-A 영역 (Form 1 outside).
5. AS single-table 不可 → 구조 X = 구현 코드 한계 (paper §V-B 자체는 OK). 임채림 자문 base (5/14 회의 14:57).
6. Neyman paradox → sel=0.01 한정 (Anti 1.540 < Prop 1.580 < Neyman 1.595). sel=0.1 = Neyman best (classical theory 정합, §6.6 표).

---

## 6.8 박세은 10:15 영역 (Anti-Neyman > Neyman = Neyman 가설 무효?)

박세은 10:15 카톡: "anti-neyman 이 neyman 보다 좋으면 neyman 가설 자체가 무효 아닌가?"

**Neyman 가설 (n_j ∝ N_j × σ_j 가 분산 최소) 자체 = 유효** (Neyman 1934 + Cochran 1977 §5.5 partial). 본 측정 데이터셋이 **Neyman 가정 (cluster 간 σ_j range 다양 + N_i CV ≠ 0) 불만족 + selectivity-dependent**:

- **sel=0.01**: σ_j range 1.3-1.6× narrow + N_i CV=0 (cluster size uniform) → Neyman 의 σ-가중 효과 약함 → Anti-Neyman 1.540 > Proportional 1.580 > Neyman 1.595 (paradox)
- **sel=0.1**: σ_j range 더 확보 (sample size 증가 → variance 더 spread) + N_i CV ≠ 0 → Neyman 본래 가설 정합 → Neyman best (SIFT sel=0.1 −9.16% = csv 가장 큰 단일 cell)

→ "Neyman 가설 무효" 영역 = **데이터셋 가정 위반 + selectivity-dependent 의 결과**. 가설 자체 무효 X. **σ_j oracle 가정 + 직접 측정 추가 검증 필요** (현재 RQ2 = L3 oracle, 본 측정 자체 σ_j 직접 estimate X).

박광현 정확 해석 권장? Cochran 1977 §5.5 (stratification with unequal variance) 추가 reference 가능성?

---

## 7. 정직 disclosure 14 영역 (cherry-picking 회피, 사전 명시)

(Agent A-J 7 + 박세은 6 통합)

1. paper §V-B 자체 algorithm pseudo-code 없음 (Eq 1-6 + 산문 + hyperparam 7종만). "14-step" 등은 본 연구 의역
2. framework axis novelty 한정 (각 component 자체 신규 X)
3. CE4HD VLDB 2024 github 미공개 — 5/27 폐기, 6/11 paper level 인용 only
4. Ada-ef arxiv 2512.06636 layer 다름 (HNSW ef search, cardinality estimation X)
5. SelNet [74] Q-error 재현 risk 10-20% (paper Fig.12 Q-error 5.53)
6. BIRCH CF σ_j² 5-15% drift vs offline KMeans
7. batch axis (1001 file) vs streaming axis (Form 1 360 file) boundary
8. paper §V-B single-table 不可 = 구현 코드 한계 (구조 X). source code level verify 미완
9. paper §V-B sampling = block + row hybrid (block only X). source code level verify 미완
10. "분포 안다" L1/L2/L3 multi-layer 분리. RQ2 = L3 oracle (직접 측정 미완)
11. paper §V-B 영역 = "without index" 가정 — paper p.5 verbatim 명시 (Form 1 anchor)
12. RQ3 = 사전 학습 batch baseline. Form 1 streaming axis = phase 1 measurement 미완
13. 0.1~0.5초 fit time = SF=1 (1M rows) 한정. SF=10/100 미측정 (선형 scale-up SF=10 ≈ 1~5s, SF=100 ≈ 10~50s 추정)
14. **Anti-Neyman > Neyman ≠ Neyman 가설 무효** — Neyman 가설 (n_j ∝ N_j × σ_j 가 분산 최소) 자체 유효 (Neyman 1934 + Cochran 1977 §5.5 partial). 본 측정 데이터셋이 Neyman 가정 (cluster 간 σ_j range 다양 + N_i CV ≠ 0) 불만족 + selectivity-dependent (sel=0.01 paradox / sel=0.1 정합). σ_j oracle 가정 + 직접 측정 추가 검증 필요

---

## 8. fix 영역 vs 변경 가능 영역 (박광현 review 후)

| 영역 | fix (변경 X) | 변경 가능 (박광현 추천 적용) |
|---|---|---|
| main theme | ✓ Streaming-aware Distribution-Conscious | |
| 4 측면 (대체/보완/개선/추가검증) | ✓ | |
| paper §V-B "without index" 가정 anchor | ✓ paper verbatim | |
| Component A+B+C+D 영역 | ✓ | 구현 detail 변경 가능 |
| 17-step pseudo-code 영역 | ✓ paper Eq 1-6 + 본 7 augment | |
| 측정 plan 우선순위 | | △ SelNet / streaming workload / drift / CE4HD 우선순위 |
| phase 1 / phase 2 timeline 분담 | | △ 5/27 / 6/11 / post-6/11 timeline |
| paper-grade publication venue | | △ EDBT short / VLDB short / ICDE position |
| 박광현 본업 align | | △ RELOAD / CANNON / DFLOP 영역 통합 가능성 |

---

## 부록 — 본 form 작성 base

- Agent A (paper 재정독) + Agent B (검증, Agent A 신뢰도 78%) + Agent C (8 옵션 deep dive + Cochran 1977 §5.5 발견) + Agent D (paper §VI 한계 + 경쟁 paper + 박광현 BDAI 본업) + Agent E (Form 1 구체화) + Agent F (측정 plan + code plan) + Agent G (paper Eq 1-6 verbatim + 17-step + SelNet/CE4HD/Ada-ef reuse) + Agent H (1001 file batch baseline 재해석 + Form 1 통합) + Agent I (5/27 20 slide + 6/11 §별 세부) + Agent J (박세은 6 영역 답변 form) = **10 agent 호출 종합**
- 정정 룰 list 10 영역 (Agent 발견 2 + 박세은 발견 8, mass update 일괄 적용)
- K granularity 추가 측정 진행 중 (A5-sf1+sf10+sf100 × K=10/30 × 4 anchor × 2 mode = 48 file, server tmux)
- handoff v20 작성 예정

---

작성: 2026-05-14 21:50 KST · 5/14 18:00 회의 narrative v3 폐기 후 Form 1 fix + 박세은 6 영역 사전 대응 + 박광현 미팅 D-1 1-2 page review form
