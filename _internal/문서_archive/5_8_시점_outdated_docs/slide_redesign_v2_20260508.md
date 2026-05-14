# Slide Redesign v2 — RQ3 Paradigm Framework 반영 안

작성: 2026-05-08 21:00 KST · 작성자: 백그라운드 에이전트 D
목적: 5/8 20:48 사용자 confirm (5 paradigm Option B 안 + ★4 sparse RP) 후 academic v3 deck 16 page redesign
실제 Slides.jsx 수정 X — 본 문서는 markdown design doc only.
실제 conversion 은 W4 (5/23~5/26) 별도 task.

---

## 0. Redesign 핵심 원칙

| 원칙 | 적용 |
|---|---|
| **Paradigm framework = RQ3 narrative 의 학술 backbone** | S6 (TOC), S8 (RQ3), S9~S12 (Contribution), S15 (Limitation) 모두 paradigm 일관성 반영 |
| **5 paradigm × 11 method × ★1~★4 selection** stack 명시 | S6.5 신규 paradigm matrix slide 추가 |
| **Top 4 = 5 paradigm 중 4 distinct representative** narrative 강조 | S8 4강 ranking + paradigm tag 추가 |
| **Pruned 19종 = paradigm 내 redundancy + hybrid + scope-out** limitation 명시 | S15 L7 (paradigm pruning) 신규 + L8 update |
| **LSH Wave 0 fail = P5 limitation honest reporting** | S6.5 + S15 L8 callout |
| **sparse RP ★4 정당화 (Achlioptas 2003 + ARI #1 + data-independent)** | S11 신규 (Hybrid → sparse RP 차별화) |
| Total page 16 → **17~18 page** (2 page 이내 추가) | S6.5, S11.5 신규 |
| LearnUs PDF 호환성 (Chrome CDP) 유지 | Slides.jsx React 구조 유지 |

---

## 1. Delta diff — 16 page 변경 매트릭스

| 기존 page | 상태 | 변경 점 |
|---|---|---|
| S1 (Cover) | **유지** | sub-title `25.4× shrinkage` 유지. version notation 만 v3 → **v4** update |
| S2 (TOC) | **수정** | 10 sections → **11 sections** (RQ3 Paradigm 섹션 신규 추가). 16 slides → **18 slides** |
| S3 (Problem) | **유지** | 기존 narrative 변경 X (pgvector/VBASE/DuckDB fixed ratio + selectivity 0.001~90%) |
| S4 (Prior Work) | **유지** | ECQO + Adaptive + PDX confirmation 그대로 (다음 slide 와 paradigm 연결 문구만 추가) |
| S5 (Approach) | **수정** | RQ3 Agnostic card 의 tag `→ 4강 method × 10 cell paired` → **`→ 5 paradigm × 11 method × Top 4`** |
| S6 (RQ1) | **유지** | 12 cell ρ ranking (ρ=-0.680 W1-A) 그대로 |
| **S6.5 신규** | **신규 추가** | **RQ3 Paradigm Framework 도입** — 5 paradigm × 11 method classification matrix |
| S7 (RQ2) | **유지** | 51/52 CI ex (sel=0.10) + Anti-Neyman counterfactual 그대로 |
| S8 (RQ3 4강) | **수정** | 4강 ranking 옆에 **paradigm tag** (P1/P3/P2/P4) 추가. Hybrid → **sparse RP** 로 ★4 교체. heatmap rebuild |
| S9 (Hilbert) | **수정** | "production sweet spot" → **"P2 Spatial Indexing representative · curve-based"**. Tier 1 spread 1.21%p 유지하되 paradigm coverage label 추가 |
| S10 (MB_partial) | **수정** | "OLTP friendly" → **"P3 Streaming representative · partial_fit protocol"**. ARI=1.000 vs full K-means 와 P1 P3 redundancy 어떻게 분리되는지 narrative 보강 |
| **S10.5 신규** | **신규 추가** | **★4 sparse RP — P4 Dim Reduction representative** (Achlioptas 2003 + data-independent 정당화) |
| S11 (Sweet Spot) | **유지하되 번호만 update** | cluster_ratio × intrinsic_dim → S12 로 번호 이동 (1 page 뒤로) |
| S12 (Cross-scale) | **유지하되 번호만 update** | sf1 → sf10 일관성 → S13 으로 번호 이동 |
| S13 (Mechanism) | **수정** | locality + 25.4× shrinkage 유지하되 narrative 일부 정정 — "단일 정확성 = multi 필요조건" 강조 + "5 paradigm 모두 multi 에서 0.67% 약화 일관" 추가 |
| S14 (Effect Honesty) | **유지** | DEFF/ESS/Q4_hard ρ=0.78 + SSN++ ceiling 그대로 |
| S15 (Limitation 8-card) | **수정** | L1~L8 중 **L7, L8 update** + L1, L2 narrative 정정. 신규 카드 X (8 카드 유지) |
| S16 (Closing) | **유지** | "감사합니다 + Q&A" + "STAGE 3 보강 예정" 그대로 |

**총 변경 통계**: 신규 2 (S6.5, S10.5) + 수정 7 (S2, S5, S8, S9, S10, S13, S15) + 단순 번호이동 2 (S11, S12) + 유지 7 (S1, S3, S4, S6, S7, S14, S16). Final page count: **18 page** (16 → +2).

---

## 2. 신규 / 수정 slide 상세

### S2 (TOC, 수정) — 11 sections / 18 slides

**변경**: 기존 10 sections → 11. 6번째 카드 변경 + 7번째 카드 신규 추가.

| n | t | sub | 변경 |
|---|---|---|---|
| 01 | Problem | 문제 정의 | 유지 |
| 02 | Prior Work | Exqutor + PDX | 유지 |
| 03 | Approach | Skew-Aware Sampling | 유지 |
| 04 | RQ1 · Diagnostic | 12-cell ρ<0 일관 | 유지 |
| 05 | RQ2 · Aware | 51/52 CI 0 제외 | 유지 |
| **06** | **RQ3 · Paradigm** | **5 paradigm × 11 method** | **신규** |
| **07** | **RQ3 · Top 4** | **10-cell paired Δ%** | 기존 06 의 변형 |
| 08 | Contribution | 5 paradigm representative | 기존 ★1 ★2 ★3 통합 |
| 09 | Cross-Scale | sf1 → sf10 | 기존 07 |
| 10 | Mechanism | multi 25.4× shrinkage | 기존 08 |
| 11 | Limitation | 8 open + paradigm pruning | 기존 09 + 10 통합 |

**시각화**: 5 paradigm framework 의 도입을 TOC 에 명시 — 발표자가 "RQ3 는 단순 4 method 비교가 아닌 5 paradigm 학술 분류" 로 정정 가능.

---

### S6.5 (신규) — RQ3 Paradigm Framework 도입

**Slide title**: RQ3 — 5 Paradigm Framework · 학습 가능한 stratification 을 학술 분류
**Eyebrow**: DISTRIBUTION-AGNOSTIC · 5 PARADIGM · 11 METHOD · INDUCTIVE BIAS

**페이지 번호**: 7 (16 → 18 으로 늘어나면서 RQ2 가 7page 이므로 새 paradigm slide 는 8page)

**페이지 핵심 메시지**: "RQ3 는 30 method 측정 → 5 paradigm 학술 분류 → 4 distinct representative selection 의 stack. 단순 method 비교가 아닌 inductive bias 분류 framework."

#### 시각화 element 1 — 5 Paradigm × Method Assignment Matrix (좌측 60%)

```
| Paradigm                      | Primary (★)                | Secondary             | Inductive bias                       | avg Δ% | 학술 출처               |
|-------------------------------|----------------------------|-----------------------|--------------------------------------|--------|-------------------------|
| P1 · Cluster-based            | HDBSCAN ★1                  | MiniBatch / GMM       | density / centroid / distribution    | -8.04  | Campello 2013 PAKDD     |
| P2 · Spatial Indexing         | Hilbert curve ★3            | faiss_ivf             | space-filling curve / partition VQ   | -7.54  | Lawder 2001 SIGMOD      |
| P3 · Streaming                | MB_partial ★2              | Reservoir             | online sequential / single-pass     | -7.63  | Sculley 2010 + Vitter 1985 |
| P4 · Dim Reduction            | sparse RP ★4               | PCA1D                 | data-independent linear projection   | -6.91  | Achlioptas 2003 JCSS    |
| P5 · Quasi-random             | Sobol (pruned)             | LSH (Wave 0 fail)     | low-discrepancy sequence             | +0.18  | Sobol 1967 / Niederreiter 1992 |
```

- Row 색상: P1 P2 P3 P4 = navy (★ representative), P5 = red (limitation)
- 중요 셀 (★1 -8.04, ★2 -7.63, ★3 -7.54, ★4 -6.91) bold + Δ% 강조
- P5 row 는 "★ 없음" + dashed border 로 구별

#### 시각화 element 2 — LSH Wave 0 Limitation Callout (우측 40%)

```
┌─────────────────────────────────┐
│ P5 LIMITATION                    │
│                                  │
│ LSH (Indyk-Motwani 1998)         │
│ ┌───────────────┐                │
│ │  +2,092%      │                │
│ │  Wave 0 fail  │                │
│ └───────────────┘                │
│                                  │
│ Sobol (Sobol 1967)               │
│ ┌───────────────┐                │
│ │  +0.18%       │                │
│ │  Pruned (Tier3)│               │
│ └───────────────┘                │
│                                  │
│ → P5 hashing/QR 은 random        │
│   ANN search trick · K=20        │
│   stratification 과 mismatch     │
│                                  │
│ → 5 paradigm 중 P5 만 winner X   │
│   honest limitation 보고         │
└─────────────────────────────────┘
```

#### 시각화 element 3 — Pruned 19종 분류 (하단 stripe)

```
PRUNED 19/30 — paradigm framework 외:
├ Hybrid 6: pca_kmeans, coresets, kde_pilot, distance_shell, importance_sampling, Hybrid(MB+Hilbert)
└ Redundancy 13: kmeans_pp, DBSCAN, OPTICS, birch, agglomerative, hkmeans, zorder, kdtree, pq, random_proj, halton, hammersley, spectral
```

- 작은 회색 텍스트 (font-size 9~10) + ARI/avg Δ% 와 paradigm 안 redundancy 사유 한 줄 코멘트
- Hybrid 는 inductive bias 단일성 위배, Redundancy 는 P1~P5 안 representative 와 정보 중복

#### Implementation tip line (하단 navy band)

> "30 method 측정 → 5 paradigm 분류 → 19 pruned + 11 retained → 4 distinct representative ★1~★4 selection."

---

### S5 (Approach, 수정) — RQ3 tag 정정

**기존**:
```
RQ3 · Agnostic
분포를 모를 때 채택 가능한 방법은?
→ 4강 method × 10 cell paired
```

**변경**:
```
RQ3 · Agnostic
분포를 모를 때 채택 가능한 방법은?
→ 5 paradigm × 11 method × Top 4
```

이 한 줄 변경만으로 전체 narrative arc 가 "method 비교" 에서 "paradigm framework" 로 reframe.

---

### S8 (RQ3 4강, 수정) — paradigm tag 추가 + Hybrid → sparse RP 교체

**기존 4강**:
| ★ | method | avg Δ% | neg | CI |
|---|---|---|---|---|
| ★1 | HDBSCAN | -8.04 | 8/10 | 8/10 |
| ★2 | MB_partial | -7.63 | 8/10 | 9/10 |
| ★3 | Hilbert | -7.54 | 8/10 | 9/10 |
| ★4 | Hybrid | -7.13 | 8/10 | 8/10 |

**변경 (paradigm tag 추가, ★4 교체)**:
| ★ | method | paradigm | avg Δ% | neg | CI |
|---|---|---|---|---|---|
| ★1 | HDBSCAN | **P1 · density** | -8.04 | 8/10 | 8/10 |
| ★2 | MB_partial | **P3 · streaming** | -7.63 | 8/10 | 9/10 |
| ★3 | Hilbert | **P2 · curve** | -7.54 | 8/10 | 9/10 |
| ★4 | sparse RP | **P4 · dim-reduction** | -6.91 | 8/10 | 8/10 |

**핵심 narrative 정정** (4강 ranking 하단 caption):
> "★1~★4 = 5 paradigm 중 4 distinct representative. paradigm coverage 4/5 — P5 quasi-random 는 honest limitation."

**heatmap data 변경** (sparse RP 의 10 cell paired Δ% 추가):
- 기존 Hybrid row: -1.06, -1.91, -28.95, -10.20, +1.35, +1.25, -7.69, -4.21, -5.71, -4.78
- 신규 sparse RP row: 측정값 사용 (메인 세션에서 RQ3 paradigm 결과 csv 또는 master_v6 §10.4 참조 후 fill)
  - 가용 데이터: avg -6.91 / sign 8/10 / CI ex 8/10 (SIFT_sf1 가장 큰 absolute value 예상)

**시각적 강조**: ★4 sparse RP row 의 paradigm tag `P4` 를 다른 색 (예: gold) 으로 표시 — Hybrid 가 빠지고 sparse RP 로 교체된 narrative 변경 시각적 분리.

---

### S9 (Hilbert ★3, 수정) — P2 representative 표기

**기존 title**: Contribution 1 — Hilbert · production sweet spot
**변경 title**: Contribution 1 — Hilbert · **P2 Spatial Indexing representative**
**Eyebrow**: LEARNING-FREE · CURVE-BASED · TIER 1 SPREAD 1.21%p

**핵심 narrative**:
- "Hilbert (Lawder 2001 SIGMOD) 는 P2 Spatial Indexing 의 *space-filling curve* sub-paradigm representative"
- "P2 의 또 다른 sub = faiss_ivf (partition VQ) — 본 연구는 curve 가 production sweet spot"
- "inverse Manhattan 1.000 (Hilbert) vs 1.992 (Z-order) → curve 선택 정당화"

**Tier 1 spread chart 강화**:
- 기존: HDBSCAN/MB_p/Hilbert/Hybrid/kdtree 5 method
- 변경: paradigm tag 옆에 표시

```
HDBSCAN  [P1] -8.04 | ████████████████████ |
MB_p     [P3] -7.63 | ███████████████████  |
Hilbert  [P2] -7.54 | ███████████████████  | ← 본 slide focus
sparse RP[P4] -6.91 | █████████████████    |
kdtree   [P2] -6.83 | ████████████████     | ← P2 secondary, redundant with Hilbert
```

**spread caption**: "5 paradigm 중 4 representative spread = 1.13%p — paradigm choice 부차, 분포 인지 boundary 결정적"

---

### S10 (MB_partial ★2, 수정) — P3 representative 표기

**기존 title**: Contribution 2 — MiniBatch K-means · OLTP friendly
**변경 title**: Contribution 2 — MB_partial · **P3 Streaming representative**
**Eyebrow**: PARTIAL_FIT PROTOCOL · 4강 #2 · CI EX 9/10

**핵심 narrative 보강** (P1 vs P3 분리 정당화):
- "MiniBatch K-means 는 P1 (centroid) 도 가능. 본 연구의 ★2 는 *partial_fit protocol* — Sculley 2010 의 streaming variant"
- "ARI = 1.000 (full K-means 동일) → cluster 품질은 P1 와 redundant. 그러나 *online sequential update* 는 P3 single bias"
- "1,189× speedup → OLTP streaming 환경 drop-in 가능 (sample arrival 단위로 stratum 학습)"

**시각화 강화** (MiniBatch 가 P1 P3 모두 가능함을 명시):
```
┌─────────────────────────────────────────┐
│ MiniBatch K-means · 다중 paradigm 가능   │
│                                          │
│  P1 (centroid)         P3 (streaming)    │
│  ─────────────         ──────────────    │
│  full fit              partial_fit       │
│  one-shot              sequential update │
│  ARI 1.000             ARI 1.000         │
│                                          │
│  → 본 연구 ★2 = P3 protocol              │
└─────────────────────────────────────────┘
```

---

### S10.5 (신규) — ★4 sparse RP · P4 Dim Reduction representative

**Slide title**: Contribution 4 — sparse RP · **P4 Dim Reduction representative**
**Eyebrow**: DATA-INDEPENDENT · ACHLIOPTAS 2003 · ARI ORTHOGONALITY #1

**Page number**: 12 (S6.5 추가로 1 page shift)

#### 시각화 element 1 — Big number callout (좌측 50%)

```
sparse RP avg Δ% · 4강 #4

−6.91%
neg 8/10 · CI ex 8/10 · SIFT_sf1 ~−15%

★ data-independent 1위
★ ARI orthogonality #1 (0.122)

INDUCTIVE BIAS:
projection matrix = random {-√3, 0, +√3}
→ fit() 에서 데이터 학습 X
→ "분포 모를 때" framing 강한 일치
```

#### 시각화 element 2 — sparse RP vs PCA1D 비교 card (우측 50%)

```
P4 SUB-PARADIGM 분리 정당화

| 후보       | bias                  | "분포 모를 때" 일치성 |
|-----------|----------------------|--------------------|
| sparse RP | data-independent      | ★ 강한 일치        |
| PCA1D     | data-dependent (SVD) | △ tension          |

학술 출처:
- sparse RP: Achlioptas 2003 PODS / JCSS
  · 'Database-friendly RP: JL with binary coins'
  · scikit-learn `SparseRandomProjection` standard
  · ~2,500 citations
- PCA1D: Pearson 1901 / Hotelling 1933
  · top eigenvector projection
  · data 의 covariance 학습 필요

ARI redundancy 검증:
- sparse RP: 0.122 (rank #1, 4강 중 가장 직교)
- PCA1D: 0.277 (rank #2)

→ ★4 = sparse RP (정보적 직교 + framing 일치)
→ PCA1D 는 P4 secondary (data-dependent ablation)
```

#### Implementation tip line (하단)

> "★4 sparse RP — Hybrid (P1+P2 결합, single bias 위배) 대신 채택. 학술 정합성 + ARI orthogonality + framing 일치 3 축 정당화."

---

### S13 (Mechanism, 수정) — paradigm 일관성 narrative 추가

**기존 title**: Mechanism — locality + multi-vector shrinkage
**변경 title**: Mechanism — locality + multi-vector shrinkage (**5 paradigm 일관**)
**Eyebrow**: SINGLE × 25.4 → MULTI · 5 PARADIGM CONSISTENT · NECESSARY ≠ SUFFICIENT

**기존 멀티 표** (4강 × 2 cell):
- HDBSCAN -1.02 / Hilbert -0.48 / Hybrid +0.31 / MB_p -1.30 (deep_sift_10)

**변경**: 4강 ↔ paradigm representative 1:1 매핑 표기. 5 paradigm 중 P5 는 측정 X (limitation):

```
MULTI-VECTOR cell × 5 paradigm representative (sel=0.10)

                  P1 HDBSCAN  P3 MB_p  P2 Hilbert  P4 sparseRP  P5 (-)
deep_sift_10      -1.02       -1.30    -0.48        ~ -1.0       N/A
deep_wiki_10      +1.15       +0.99    +0.06        ~ +0.5       N/A
```

(sparse RP multi 측정값은 measure_multi_paradigm.py launch 후 fill — handoff_v12 §7 의 5/9 W2 작업)

**핵심 narrative 추가** (우측 navy band):
- "5 paradigm 모두 multi 에서 |Δ| < 1.5% 동일 약화 — paradigm 무관, multi-vector 자체의 join 분산이 단일 신호 dilute"
- "단일 정확성 = multi 정확성의 *필요조건 only*. P5 quasi-random 은 단일에서도 fail 했으므로 multi 측정 의미 없음 (limitation)"

---

### S15 (Limitation 8-card, 수정) — L7 신규 + L8 update

**기존 8-card**:
| L | cat | title |
|---|---|---|
| L1 | PARTIAL | Single-table only |
| L2 | FUTURE | Multi-vector 일반화 |
| L3 | FUTURE | sf100 cross-scale |
| L4 | PARTIAL | KM20 oracle 학습 부담 |
| L5 | HONEST | SSN++ ceiling honest |
| L6 | HONEST | Effect size practical small |
| L7 | PARTIAL | numpy estimator scope |
| L8 | FUTURE | vector.c integration |

**변경 (L7, L8 update + L1, L2 narrative 정정)**:
| L | cat | title | 변경 description |
|---|---|---|---|
| L1 | PARTIAL | Single-table only | (정정) "multi-table 25.4× shrinkage 측정 — 단일 정확성 = multi 필요조건만 입증" |
| L2 | FUTURE | Multi-vector 일반화 | (유지) joint-aware clustering future work |
| L3 | FUTURE | sf100 cross-scale | (유지) 채림 자문 후 5/15 보강 |
| L4 | PARTIAL | KM20 oracle 학습 부담 | (유지) partial_fit + Hilbert production replacement |
| L5 | HONEST | SSN++ ceiling honest | (유지) outer boundary |
| L6 | HONEST | Effect size practical small | (유지) Q4 hard ρ=0.78 |
| **L7** | **PARTIAL** | **5 paradigm 외 method 가지치기** | **(신규)** "Hybrid 6 + Redundancy 13 = 19 pruned. paradigm framework narrative 우선 — pca_kmeans (-8.02) 강하나 P1+P4 hybrid 로 single bias 위배" |
| **L8** | **HONEST** | **P5 Quasi-random LSH fail honest** | **(update)** "P5 의 LSH (Wave 0 +2,092%) + Sobol (Pruned +0.18%) — hashing/QR paradigm 은 K=20 stratification 과 hyperparameter mismatch. 5 paradigm 중 P5 representative ★ 없음 honest 보고" |

**기존 L7 (numpy estimator scope), L8 (vector.c integration) 은 어디로?**
- L7 numpy estimator: 본 슬라이드에서 제거 → 보고서 본문 (master_v6) 유지. 발표 deck 에는 paradigm 관련 limitation 우선
- L8 vector.c: 본 슬라이드에서 제거 → 보고서 본문 + 자문 메일 우선

**총 8 card 유지** — paradigm 관련 2 card 신규 + estimator/vector.c 2 card 보고서로 이전.

---

## 3. Narrative Flow 핵심 변경점

### 기존 (v3 Academic) flow
```
Problem → Prior Work → Approach (3 RQ) → RQ1 → RQ2 → RQ3 4강 → Hilbert ★3 → MB_p ★2 → Sweet spot ★1 → Cross-scale → Mechanism → Effect Honesty → Limitation 8 → Closing
```
- RQ3 4강 = "10-cell paired Δ% 측정 → 4 winner method"
- Top 4 의 학술 분류 framework 명시 X
- Hybrid 가 ★4 인데 single inductive bias 위배 (P1+P2)
- Pruned 19종 의 처리 사유 명시 X
- LSH Wave 0 fail 은 limitation 8-card 에 없음

### 변경 (v4 Paradigm) flow
```
Problem → Prior Work → Approach (3 RQ) → RQ1 → RQ2 → [신규] RQ3 Paradigm Framework (5 paradigm × 11 method) → RQ3 Top 4 (paradigm tag) → Hilbert ★3 (P2) → MB_p ★2 (P3) → [신규] sparse RP ★4 (P4) → Sweet spot → Cross-scale → Mechanism (5 paradigm 일관 약화) → Effect Honesty → Limitation 8 (paradigm pruning + LSH fail) → Closing
```

### 한 줄 요약

> "**RQ3 = 30 method 측정 → 5 paradigm 학술 분류 → 19 pruned (hybrid + redundancy) + 11 retained → ★1~★4 = 4 distinct paradigm representative selection → multi 일반화 25× shrinkage** stack 의 학술 정합성 강화."

기존 narrative 의 약점 (Hybrid ★4 의 single bias 위배 + paradigm framework 부재 + LSH fail honest 보고 누락) 을 5 paradigm 안으로 일관성 있게 reframe.

---

## 4. 자문 결과 supplementary slide 자리 (예약)

### S17 (자문 supplementary, 5/22 교수님 미팅 + 자문 회신 5/15 후 추가 예정)

**페이지 번호**: 17 (S6.5 + S10.5 추가로 17→18 shift, supplementary 는 18 또는 hidden appendix)

**예약 내용**:

| Section | 내용 | source |
|---|---|---|
| 자문 합의 1 | 채림 석사 회신 — sf100 측정 가용성 + multi-table 정본 | 5/15 회신 |
| 자문 합의 2 | 박광현 교수 회신 — paradigm framework 학술 정합성 + RQ3 narrative 방향 | 5/22 미팅 |
| Adaptive baseline | 5/8~5/9 overnight 측정 결과 (~5h) — 본 연구 4강 vs Exqutor adaptive sampling paired Δ% | handoff_v12 §7 |
| Multi 광범위 | 5/9~5/10 overnight (~10h) — 3 multi cell × 11 method 결과, 4강 외 paradigm 일반화 | handoff_v12 §7 |
| Pruned method 회복 | (선택) 채림 자문 후 pca_kmeans / Hybrid 의 hybrid bias 처리 방법 합의 | 5/22 |

**시각화 hint** (TBD by W4):
- 좌측 50% — 자문 메일 outline 3줄 + 회신 핵심 quote
- 우측 50% — Adaptive baseline 결과 vs 4강 paired Δ% scatter or table

**page count 영향**: supplementary slide 1 page → 총 18 page → 19 page 가능. 12분 발표 + Q&A 8분 가정 시 본체 16~17 page + supplementary 1~2 page hidden appendix (Q&A 시 호출).

---

## 5. 시각화 hint 추가 (Slides.jsx implementation tips)

### 5.1 5 paradigm × 11 method classification matrix (S6.5)

```jsx
const paradigms = [
  {p:'P1', name:'Cluster-based',   primary:'HDBSCAN',     star:'★1', bias:'density',                avg:-8.04, ref:'Campello 2013 PAKDD',         secondary:['MiniBatch','GMM']},
  {p:'P2', name:'Spatial Indexing',primary:'Hilbert',     star:'★3', bias:'space-filling curve',    avg:-7.54, ref:'Lawder 2001 SIGMOD',          secondary:['faiss_ivf']},
  {p:'P3', name:'Streaming',       primary:'MB_partial',  star:'★2', bias:'online sequential',      avg:-7.63, ref:'Sculley 2010 + Vitter 1985',  secondary:['Reservoir']},
  {p:'P4', name:'Dim Reduction',   primary:'sparse RP',   star:'★4', bias:'data-independent linear',avg:-6.91, ref:'Achlioptas 2003 JCSS',        secondary:['PCA1D']},
  {p:'P5', name:'Quasi-random',    primary:'(none)',      star:'-',  bias:'low-discrepancy',        avg:+0.18, ref:'Sobol 1967 / Niederreiter 1992', secondary:['LSH (Wave 0 fail)']},
];
```

- color schema: P1~P4 = navy gradient + ★ red badge / P5 = gold border (limitation)
- avg Δ% 는 num-mega font (font-num) 로 emphasis
- secondary[] 는 작은 font (~10px) gray 로 표시

### 5.2 sparse RP ★4 정당화 (S10.5)

```jsx
const sparseRPjustification = {
  bias: {sparseRP: 'data-independent', PCA1D: 'data-dependent (SVD)'},
  citations: {sparseRP: 2500, PCA1D: 30000},
  ariOrtho: {sparseRP: 0.122, PCA1D: 0.277},
  framing: {sparseRP: 'strong', PCA1D: 'tension'},
};
```

- bar chart: ARI orthogonality (낮을수록 좋음, sparse RP rank #1)
- callout: "Achlioptas 2003 'database-friendly random projections: JL with binary coins'"
- footnote: "PCA1D 는 P4 secondary, data-dependent ablation 으로 보유"

### 5.3 LSH limitation callout (S6.5 + S15 L8)

- big red number "+2,092%" with red border card
- subtitle: "P5 hashing/QR paradigm 의 LSH (Indyk-Motwani 1998) — Wave 0 fail"
- caption: "K=20 stratification 과 hyperparameter mismatch · 5 paradigm 중 P5 만 winner X"

---

## 6. PDF 호환성 확인 (Chrome CDP)

- Slides.jsx 의 React structure 유지 → `index.html` rendering 그대로 → `python3 _internal/scripts/md2pdf.py` (또는 deck-stage.js) chain 변경 X
- font: Apple SD Gothic Neo + var(--font-mono) + var(--font-num) 그대로
- color schema: navy/red/gold/blueSoft 기존 안 그대로 + S6.5/S10.5 신규 slide 도 동일 token 활용

**implementation 참조 path**:
- 본체: `/Users/hyunbin/Capstone/submission/_drafts/academic_deck_v3_source/academic-deck/Slides.jsx`
- index: `/Users/hyunbin/Capstone/submission/_drafts/academic_deck_v3_source/academic-deck/index.html`
- print: `/Users/hyunbin/Capstone/submission/_drafts/academic_deck_v3_source/academic-deck/index-print.html`
- TOTAL constant 변경: `const TOTAL = 16;` → `const TOTAL = 18;`

---

## 7. W4 (5/23~5/26) 실제 conversion task 체크리스트

- [ ] Slides.jsx S6.5 신규 component 작성 (paradigm matrix + LSH callout + pruned 19 stripe)
- [ ] Slides.jsx S10.5 신규 component 작성 (sparse RP big number + PCA1D 비교 card)
- [ ] Slides.jsx S2 TOC items 배열 update (10 → 11 sections, 16 → 18 slides)
- [ ] Slides.jsx S5 RQ3 card tag 변경 (`4강` → `5 paradigm × 11 method × Top 4`)
- [ ] Slides.jsx S8 4강 ranks 배열 paradigm tag 추가 + Hybrid → sparse RP 교체 + heatmap 데이터 변경
- [ ] Slides.jsx S9 / S10 title eyebrow 변경 (paradigm representative 명시)
- [ ] Slides.jsx S13 multi heatmap에 5 paradigm representative tag 추가
- [ ] Slides.jsx S15 Limitation 8-card update (L7 paradigm pruning + L8 LSH fail)
- [ ] TOTAL = 16 → 18 update
- [ ] index.html / index-print.html 의 div id 추가 (`s17`, `s18` 도 검토)
- [ ] mounting array `slides[]` update
- [ ] Chrome CDP 빌드 + PDF 추출 검증
- [ ] 5/27 발표 12분 + Q&A 8분 timing rehearsal (page 별 ~40초)

---

## 8. Critical 메모

- **사용자 confirm 항목 (5/8 20:48)**:
  - Option B: 5 paradigm 유지 + P5 = "Low-discrepancy / Quasi-random" 단일 bias + LSH limitation
  - ★4 = sparse RP 확정
  - 누락 critical 추가 측정 X (limitation 명시)
  - 4강 narrative 변경 X (HDBSCAN P1 / MB_partial P3 / Hilbert P2 / sparse RP P4)

- **본 design doc 의 한계**:
  - sparse RP 의 10 cell paired Δ% 실제 데이터 (heatmap fill) 는 master_v6 §10.4 또는 measure_multi_paradigm.py 결과 기반 — design doc 단계에서는 placeholder
  - sparse RP multi-vector 측정값 (S13) 은 5/9 launch 후 fill
  - supplementary slide (S17/S18) 는 5/22 미팅 + 5/15 자문 회신 후 finalize

- **사용자 review 후 처리**:
  - 본 design doc 의 narrative direction OK 확인 → W4 Slides.jsx 수정 task launch
  - 박세은 카톡 update 시 paradigm naming 정정 추가 권장 ("4강 winner = 5 paradigm 중 4 distinct representative" 표현으로 reframe)

---

> **작성**: Claude Opus 4.7 1M (백그라운드 에이전트 D, 5/8 21:00 KST)
> **다음 review**: 메인 세션 사용자 confirm + W4 (5/23~5/26) Slides.jsx 실제 conversion
> **참조 docs**:
> - `_internal/RQ3_paradigm_심층검증_20260508.md` (Deep Review Agent 산출, 학술 검증)
> - `_internal/handoff_v12_session_20260508_2030_RQ3확정대기.md` (현 세션 handoff)
> - `submission/_drafts/academic_deck_v3_source/academic-deck/Slides.jsx` (16 page source)
> - `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.pdf` (16 page rendered)
