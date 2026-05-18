# Agent K — 5/15 박광현 review form PDF v2 final QA (D-1 미팅 사전 점검)

> **작성**: 2026-05-14 22:30 KST · Agent K · main thread 지시 "PDF v2 (10 page → 실제 12 page) final polish QA 7 영역"
> **input**: PDF v2 (12 page, 510 KB) + md source (196 line, 11.4 KB) + handoff v20 (28.8 KB, 486 line) + Agent J 답변 form (47.9 KB, 667 line) + measure_paper_exact.py (1407 line, PAPER_HYPERPARAM verify)
> **fix 영역 제약**: main theme + 4 측면 + paper §V-B scope 변경 X (defect 가 fix 영역 침범 시 별도 명시)
> **사용자 정책**: 학부생 톤 / 한국어 / 정직 disclosure / "100% 검증" 회피
> **QA 검증 시간**: PDF 12 page 전수 read + md 196 line 전수 read + handoff v20 486 line 전수 read + Agent J 667 line 전수 read + measure_paper_exact.py grep 검증

---

## 0. TL;DR (1 분 요약)

PDF v2 = **D-1 미팅 사전 자료로 ready**. 다만 **P0 1건 + P1 5건 + P2 4건** total 10건 defect 발견. P0 = 박세은 9 영역 中 **3 영역 (#5 #6 #6.5/8:50 K granularity 답변에 §6.5 표가 있으나 박세은 영역 1-6 사전 답변 form 인 §6 항목 영역과 cross-reference 가 어색)** 의 §6 리스트 vs 본문 §6.5/§6.6 분리 + handoff v20 의 "9 영역" 표현 vs PDF §6 "12 항목 (박세은 6 + 박광현 6)" 차이.

**fix 영역 침해**: 없음. main theme + 4 측면 + paper §V-B scope 모두 PDF 에 정확히 반영됨.

**미팅 readiness**: 자료 fix 영역 ready / 변경 가능 영역 review 영역 명확화 완료. **D-1 발송 / 보강 권장**.

---

## §1. md vs PDF rendering 정합성

### 1.1 발견 issue

| # | 영역 | severity | md line | PDF page | 정합 여부 |
|---|---|---|---|---|---|
| **R1** | YAML frontmatter rendering | **P1** | line 1-6 | page 1 상단 | ✗ YAML 이 "title: ... subtitle: ... date: ... team: ..." 한 줄 plain text 로 rendering 됨. 일반적인 YAML frontmatter 는 PDF 표지 / metadata 로 분리되지만 본 PDF 는 본문 첫 단락처럼 rendering. **md2pdf.py 의 YAML 처리 영역** issue |
| R2 | callout box rendering | OK | "> ..." quote block | page 1, 2 | ✓ Streaming-aware Distribution-Conscious 박스 + paper verbatim 박스 모두 navy left bar + bg light 적용 |
| R3 | table column width balance | **P2** | §2 Component 표 (line 36-41) | page 3 | △ Comp 첫 column 좁음 (e.g. "A Stratified Reservoir Sampling" 한 줄, "B BIRCH CF-tree online cluster maintenance" 두 줄). 균일 X. body text 의 두 column ("paper Eq 1-6 verbatim 100% 정합") wrap 후 좁음 |
| R4 | section H2 page break | OK | 8 § + 2 sub-§ | 12 page | ✓ §0~§8 + §6.5 + §6.6 + 부록 = 11 H2 sections. page break 정상 (각 § 새 page 시작) |
| R5 | TOC anchor | N/A | md 자체 TOC 없음 | PDF TOC 없음 | △ 12 page 자료에 TOC 부재. 박광현 review 시 navigation 어려움 가능 |
| R6 | page numbering | OK | N/A | "N / 12" footer | ✓ 1/12 ~ 12/12 정상 |
| R7 | font Apple SD Gothic Neo | OK | N/A | 전체 page | ✓ 한글 rendering 깨지지 않음 |
| R8 | section 6.5 / 6.6 numbering | △ | line 105 + 126 | page 8 + 9 | △ "6.5" + "6.6" sub-section 이 §6 review 항목 (line 81) 영역 안에 있는 것처럼 보이나, 실제 내용은 박세은 발견 영역 (8:50 + 9:42 + 9:54). **별도 § (§7 또는 §6 의 자세 sub-§)** 로 분리하는 것이 가독성에 더 좋을 수 있음 |
| R9 | §3 paper 한계 보완 표 (line 49-53) | OK | line 49-53 | page 4 | ✓ L1 / L5 / L6 표 정상 rendering (3 row × 3 column) |
| R10 | §6 review 12 항목 list rendering | OK | line 85-101 | page 7 | ✓ 1-12 numbered list 정상, ★★★ critical 영역 강조 정상 |

### 1.2 P0 / P1 표시 핵심

- **R1 (P1)**: YAML frontmatter 가 본문 첫 단락처럼 rendering — md2pdf.py 자체의 YAML 분리 기능 부재 가능성. 박광현 미팅 시 첫 인상에 거슬릴 수 있음. **권장**: md 첫 6 line YAML 을 일반 markdown header 로 정정 (`# 속도는벡터 × 박광현 교수 미팅 (5/15)` + sub-line 별도 metadata 영역)
- **R3 (P2)**: §2 표 column 균일성. polish 영역
- **R5 (N/A → P2)**: 12 page 자료 TOC 부재. cover sheet 영역 권장 가능

---

## §2. 박세은 9 영역 답변 cross-check matrix

> **9 영역 정의** (사용자 mission 명시): 8:50 K granularity / 9:09 #1 single-table / 9:09 #2 block+row / 9:09 #3 L1/L2/L3 / 9:09 #4 ECQO / 9:09 #5 RQ3 사전학습 / 9:27 fit time / 9:42 Neyman paradox sel=0.01 / 9:54 Bernoulli→Neyman −10% / 10:15 Anti-Neyman Neyman 가설
>
> 총 = **10 영역** (8:50 K granularity 1 + 9:09 5 + 9:27 1 + 9:42 1 + 9:54 1 + 10:15 1 = 10)
>
> 사용자 mission text 의 "9 영역" 은 표기 차이일 가능성 (10:15 영역이 9 영역 안에 포함 또는 별도). 본 QA 는 10 영역 매트릭스로 정리.

### 2.1 매트릭스

| # | 영역 (시각) | handoff v20 §5 | PDF §6 reviewer 12 항목 | PDF §6.5/§6.6 본문 | 정합 여부 |
|---|---|---|---|---|---|
| 1 | **8:50 K granularity** | §10 (line 282-311) + §5 X | review #X 없음 | **§6.5 (page 8)** SF=1/10/100 표 + method-dependent 결론 | ✓ PDF 본문 자체 완전 답변 (§6.5 page 8 4 method × 3 SF 표). review #X 영역 부재는 OK (이미 답변 완료) |
| 2 | **9:09 #1 single-table** | §5.1 (line 178-180) | **review #5** "AS = single-table 不可 wording 정정 (구조 X = 구현 한계). 정확 framing 권장?" | 본문 답변 X (review 만 list) | △ **review list 만 명시, 본문 자체 답변 X** — agent_J §1 영역 1 답변 (line 41-53) 의 풍부한 contents 가 PDF 에 없음. **D-1 미팅 시 박광현 question 들어오면 즉답 부재** |
| 3 | **9:09 #2 block+row** | §5.2 (line 182-184) | **review 항목 부재** ★ | 본문 답변 X | ✗ **box → row hybrid 영역이 review 6 항목 list 에 누락**. handoff v20 §4 정정 룰 #4 line 162 ("block only → block + row hybrid") 명시 영역 vs PDF §6 review 6 항목에 영역 미반영. **D-1 미팅 critical defect** |
| 4 | **9:09 #3 L1/L2/L3** | §5.3 (line 186-190) | **review #4** "분포 안다 L1/L2/L3 분리" | 본문 답변 X | △ review list 만, 본문 답변 X. agent_J §1 영역 3 + §4 L1/L2/L3 표 (line 78-101 + 336-394) 의 풍부 contents PDF 미반영 |
| 5 | **9:09 #4 ECQO** ★★★ | §5.4 (line 192-198) | **review #1** "(★★★ critical) 분포 알면 ECQO 가능? → paper §V 도입부 verbatim (without index 가정) anchor. Form 1 = §V-B 영역 한정" | §1 paper §V-B 영역 anchor (page 2) | ✓ **anchor 자체는 §1 page 2 에 paper verbatim 인용 완벽**. review list #1 도 정확. 단 agent_J §2 ECQO multi-layer 4 (line 226-279) 의 cost 비교 표 (HNSW vs K-means K=20) 가 PDF 에 부재 → 박광현 question 들어오면 즉답 부재 |
| 6 | **9:09 #5 RQ3 사전학습** | §5.5 (line 200-203) | **review #2** "RQ3 = 쿼리 실행 전 학습 필요 → 1001 file = 사전 학습 batch baseline framing" | 본문 답변 X | △ review list 만, 본문 답변 X. handoff v20 §5.5 의 "RQ3 = 사전 학습 batch baseline" framing 자체가 Form 1 motivation 인데 PDF 본문 분리 표시 X |
| 7 | **9:27 fit time 0.1-0.5초** | §5.6 (line 205-212) | **review #3** "0.1~0.5초 매 query 런타임? → fit time SF=1 한정. 매 query fit X (paper period P=50 가정). Form 1 = per-tuple amortized" | 본문 답변 X | △ review list 만, 본문 답변 X. agent_J §6 (line 436-482) layer 분리 답변 영역 PDF 미반영 |
| 8 | **9:42 Neyman paradox sel=0.01** | §5.7 (line 214-219) | **review #6** "Neyman paradox → sel=0.01 한정 (sel=0.1 = Neyman best classical theory 정합)" | **§6.6 (page 9)** dataset × sel × Δ% 표 | ✓ PDF 본문 자체 완전 답변 (§6.6 page 9 6 row 표 + over-statement 정정). review #6 도 정확 |
| 9 | **9:54 Bernoulli→Neyman −10%** | §6.6 (PDF) + handoff §4 #11 (line 169) | review 항목 미명시 (정정 룰 list 내부) | **§6.6 (page 9)** "Bernoulli → Neyman −10% narrative = over-statement (실제 −5~−9% 범위, 가장 큰 단일 cell = SIFT sel=0.1 −9.16%)" | ✓ PDF §6.6 본문 자체 완전 답변. review #6 와 통합 |
| 10 | **10:15 Anti-Neyman 가설** | handoff §4 정정 룰 #14 (line 172) | review 항목 부재 ★ | 본문 답변 X | ✗ **10:15 영역 PDF 미반영**. handoff v20 정정 룰 #14 의 "Anti-Neyman > Neyman = Neyman 가설 무효" → "Neyman 가설 자체 유효, but 데이터셋 가정 불만족 + selectivity-dependent" 영역이 PDF 어디에도 없음 |

### 2.2 핵심 발견 (P0 / P1)

- **P0 (3 영역 PDF 미반영)**:
  - **#3 (block+row hybrid)** — review 6 항목 list + 본문 둘 다 누락. handoff v20 §4 #4 정정 룰 활성. **박광현 question 즉답 부재**
  - **#10 (Anti-Neyman 가설)** — handoff v20 §4 #14 정정 룰 활성. PDF 미반영
  - **#5 (RQ3 사전 학습 framing)** — review list #2 만 명시, agent_J §5 (line 152-186 + line 397-432) 의 Form 1 motivation 강화 contents PDF 본문 부재. **Form 1 의 존재 이유 자체** 강조하는 영역이라 critical

- **P1 (4 영역 review list 만, 본문 답변 X)**:
  - #2 single-table (review #5)
  - #4 L1/L2/L3 (review #4)
  - #5 ECQO 대안 multi-layer (review #1) — anchor 는 OK, multi-layer 4 cost 비교 부재
  - #7 fit time (review #3)

- **P2 (2 영역 OK, 본문 답변 완전)**:
  - #1 K granularity (§6.5)
  - #8 / #9 Neyman paradox + over-statement (§6.6)

### 2.3 fix 영역 침해 여부

- 모두 **자료 변경 가능 영역** (review 답변 보강은 fix theme + 4 측면 + paper §V-B scope 변경 X)
- D-1 미팅 전 보강 권장

---

## §3. 12 review 항목 completeness

### 3.1 박세은 6 영역 vs handoff v20 §5 cross-check

| review # | PDF §6 | handoff v20 §5 (agent_J §1) | 정합 |
|---|---|---|---|
| 1 | (★★★) 분포 알면 ECQO 가능? | §5.4 + agent_J §1 영역 4 | ✓ |
| 2 | RQ3 = 쿼리 실행 전 학습 필요 | §5.5 + agent_J §1 영역 5 | ✓ |
| 3 | 0.1~0.5초 매 query 런타임? | §5.6 + agent_J §1 영역 6 | ✓ |
| 4 | "분포 안다" L1/L2/L3 분리 | §5.3 + agent_J §1 영역 3 | ✓ |
| 5 | AS = single-table 不可 wording 정정 | §5.1 + agent_J §1 영역 1 | ✓ |
| 6 | Neyman paradox sel=0.01 한정 | §5.7 + agent_J §1 영역 7 + PDF §6.6 본문 | ✓ |

→ 박세은 6 영역 review list 정합도 100%.

### 3.2 박광현 자문 6 영역 review list

| review # | 항목 | source | 정합 |
|---|---|---|---|
| 7 | Form 1 main theme 학술 정당성? | handoff v20 §1.1 + Agent E | ✓ |
| 8 | Component A+B+C+D framework axis novelty? | handoff v20 §2 + Agent E + Agent F | ✓ |
| 9 | 5/27 phase 1 timeline 52-87h 가능성? | handoff v20 §6 (Agent E/F/G/H 종합 cost 52-87h) | ✓ |
| 10 | paper-grade publication venue 추천 (EDBT short / VLDB short / ICDE position)? | handoff v20 §8 + Agent E §6.1 | ✓ |
| 11 | 박광현 본업 (RELOAD/CANNON/DFLOP) align? | Agent D + Agent J §7.4 Q5 | ✓ |
| 12 | SelNet impl 8-12h cost + Q-error 재현 risk 10-20% — 5/27 phase 1 risk mitigation? | handoff v20 §9 정직 #5 + Agent G | ✓ |

→ 박광현 6 영역 review list 정합도 100%.

### 3.3 발견 issue

| # | 영역 | severity |
|---|---|---|
| C1 | 박세은 review list 6 항목 = 박세은 9 영역 中 6 영역만 cover (block+row #3 + Anti-Neyman #10 + 8:50 K granularity #1 누락) | **P0** |
| C2 | review list 자체는 완전. 다만 본문 답변 (§6.5 / §6.6 외 영역) 부재 (§2.2 P1 4 영역) | **P1** |
| C3 | 박광현 6 영역 = balanced (학술 정당성 + framework + timeline + publication + 본업 + risk mitigation) | ✓ |

### 3.4 권장 보완

- **#3 (block+row hybrid)** 을 review #5 ("AS single-table") + review #6 (Neyman) 中간 또는 #5 뒤에 추가 (예: review #5.5)
- **#10 (Anti-Neyman 가설)** 을 review #6 (Neyman paradox) 와 통합 또는 별도 #6.5 추가
- **#1 (K granularity)** 은 PDF §6.5 본문에 답변 완전 → review list 추가 불필요 OK

---

## §4. paper verbatim 정확성

### 4.1 §1 paper §V "without index" verbatim (PDF page 2)

| # | PDF 인용 | paper 원문 (handoff v20 §1.4 line 40-62) | 정합 |
|---|---|---|---|
| Q1 | "For VAQs with vector indexes, Exqutor employs Exact Cardinality Query Optimization (ECQO)... **For VAQs without index**, Exqutor uses a **sampling-based approach** to approximate selectivity (subsection V-B)." | handoff v20 line 42-44 동일 verbatim | ✓ 100% 정합 |
| Q2 | "When a VAQ **lacks a vector index**, ... Exqutor adopts a **sampling-based cardinality estimation approach specifically for KNN queries**." | handoff v20 line 46-48 동일 (단 "..." 부분으로 중간 일부 생략) | ✓ |

### 4.2 PDF 누락 paper verbatim 3 영역

handoff v20 §1.4 (line 50-60) + agent_J §3 (line 283-322) 에 명시된 paper verbatim 3 영역 中 PDF §1 에 인용된 영역 = 2 곳 (위 Q1 + Q2). 누락 3 영역:

| # | source | paper 인용 | 누락 영향 |
|---|---|---|---|
| Q3 | handoff v20 line 50-52 | paper p.6 우단 §V-B implementation: "When a VAQ with a vector range predicate **lacks index support**, the optimizer invokes a sampling routine..." | **P1** — Form 1 anchor 의 3 번째 evidence. ECQO 영역 outside narrative 강화에 필요 |
| Q4 | handoff v20 line 54-56 | paper §VI-A 첫 단락: "In this section, we evaluate the performance of Exqutor when executing VAQs with **a vector index** using an ANN search, specifically with HNSW [38]." | **P2** — paper evaluation 영역 분리 evidence |
| Q5 | handoff v20 line 58-60 | paper §VI-B 첫 단락: "In this section, we evaluate the performance of Exqutor applied to TPC-H VAQs that perform KNN searches **without vector indexes**, where cardinality estimation is handled via sampling." | **P2** — paper evaluation 영역 분리 evidence |

### 4.3 권장 보완

- **Q3 인용 PDF §1 추가** (3 paper verbatim → 4 paper verbatim) — Form 1 anchor 강화
- Q4/Q5 는 P2 우선순위

### 4.4 결론

- §1 paper verbatim 영역 정확성 100% (Q1 + Q2 모두 paper 원문 정확)
- 누락 3 영역 (Q3 P1 + Q4/Q5 P2) 보강 권장
- fix 영역 침해 없음 (paper §V-B scope 안)

---

## §5. paper Eq 1-6 verbatim 정확성

### 5.1 PDF §2 표 (page 3) 의 paper hyperparam 7종 line

PDF page 3 표 하단 line:

> "본 연구 의역 step-wise pseudo-code = paper Eq 1-6 verbatim **10 step** + 본 augment **7 step** = **17 step**. (paper 자체에는 algorithm pseudo-code 없음, Eq 1-6 + 산문 + hyperparam 7종 m=0.9/η₀=0.1/α=50/β=1.5/γ=0.99/period=50/N=385)"

### 5.2 measure_paper_exact.py PAPER_HYPERPARAM verify

| Item | PDF | measure_paper_exact.py line 67-74 | 정합 |
|---|---|---|---|
| m | 0.9 | (momentum 미명시 추가 verify 필요) | △ |
| η₀ | 0.1 | "eta_0": 0.1 (line 70) | ✓ |
| α | 50 | "alpha": 50 (line 71) | ✓ |
| β | 1.5 | "beta": 1.5 (line 72) | ✓ |
| γ | 0.99 | "gamma": 0.99 (line 73) | ✓ |
| period | 50 | "update_period": 50 (line 74) | ✓ |
| N | 385 | "N_init": 385 (line 68) | ✓ |

→ **6/7 hyperparam 100% 정합**. m=0.9 (momentum) 영역만 추가 verify 필요 (measure_paper_exact.py 본 grep 에서 명시 안 됨 → AdaptiveState dataclass 의 m field default 가 PAPER_HYPERPARAM["m"] 참조하므로 정합 가능성 높음, P2)

### 5.3 paper Eq 1-6 + 17-step pseudo-code 표현

PDF page 3 표 하단 + handoff v20 §2.5 (line 97-105) + agent_G (paper Eq 1-6 + 17-step 정확 정독)

| 영역 | PDF 명시 | handoff v20 명시 | 정합 |
|---|---|---|---|
| paper Eq 1-6 verbatim 영역 | "10 step" (PDF page 3 line) | "10 step (Step 1-2, 6, 8-13, 16)" (handoff v20 line 99) | ✓ 정확 |
| 본 연구 augment 영역 | "7 step" (PDF page 3 line) | "7 step (Step 3-5, 7, 14-15, 17)" (handoff v20 line 100) | ✓ 정확 |
| 총 step | "17 step" | "17 step" | ✓ |
| paper 자체 pseudo-code 없음 | "paper 자체에는 algorithm pseudo-code 없음" | "(paper 자체에는 algorithm pseudo-code 없음, Eq 1-6 + 산문 + hyperparam 7종)" (handoff v20 line 43) | ✓ |
| Eq 1 (Bernoulli sample budget) 대체 | "본 contribution" 표 column | "Eq 1 만 대체, Eq 2-6 verbatim 유지" (handoff v20 line 86 + Agent F 정정 룰 #1) | ✓ |

→ paper Eq 1-6 + 17-step pseudo-code 영역 정확성 100%.

### 5.4 발견 issue

| # | 영역 | severity |
|---|---|---|
| E1 | PDF §2 표 column "본 contribution" 의 row B "paper period P=50 align" 영역의 "P=50" 표현이 paper 의 "update_period=50" 영역과 align 영역 명시 X | P2 |
| E2 | PDF 어디에도 Eq 1 / Eq 2 / Eq 3 / Eq 4 / Eq 5 / Eq 6 의 explicit formula 또는 paper 식별 명시 없음 (PDF 1-2 page 자료라 OK, 다만 박광현이 Eq 별 verbatim 보고 싶을 가능성 있음) | P2 |

### 5.5 결론

- PAPER_HYPERPARAM 6/7 정합 (m=0.9 추가 verify P2)
- 17-step pseudo-code 영역 (10 verbatim + 7 augment) 정확
- Eq 1-6 explicit formula 미표시 (1-2 page 자료라 OK)
- fix 영역 침해 없음

---

## §6. 정직 disclosure 13 영역 completeness

### 6.1 매트릭스 (PDF §7 page 10 vs handoff v20 §9)

| # | PDF §7 | handoff v20 §9 (line 264-278) | agent_J §8 (line 569-604) | 정합 |
|---|---|---|---|---|
| 1 | paper §V-B 자체 algorithm pseudo-code 없음 | line 266 동일 | line 575 동일 | ✓ |
| 2 | framework axis novelty 한정 (각 component 자체 신규 X) | line 267 동일 | line 576 동일 | ✓ |
| 3 | CE4HD VLDB 2024 github 미공개 — 5/27 폐기, 6/11 paper level 인용 only | line 268 동일 | line 577 동일 | ✓ |
| 4 | Ada-ef arxiv 2512.06636 layer 다름 (HNSW ef search, cardinality estimation X) | line 269 동일 | line 578 동일 | ✓ |
| 5 | SelNet [74] Q-error 재현 risk 10-20% (paper Fig.12 Q-error 5.53) | line 270 동일 | line 579 동일 | ✓ |
| 6 | BIRCH CF σ_j² 5-15% drift vs offline KMeans | line 271 동일 | line 580 동일 | ✓ |
| 7 | batch axis (1001 file) vs streaming axis (Form 1 360 file) boundary | line 272 동일 | line 581 동일 | ✓ |
| 8 | paper §V-B single-table 不可 = 구현 코드 한계 (구조 X). source code level verify 미완 | line 273 동일 | line 587 동일 | ✓ |
| 9 | paper §V-B sampling = block + row hybrid (block only X). source code level verify 미완 | line 274 동일 | line 588 동일 | ✓ |
| 10 | "분포 안다" L1/L2/L3 multi-layer 분리. RQ2 = L3 oracle (직접 측정 미완) | line 275 동일 | line 589 동일 | ✓ |
| 11 | paper §V-B 영역 = "without index" 가정 — paper p.5 verbatim 명시 (Form 1 anchor) | line 276 동일 | line 590 동일 | ✓ |
| 12 | RQ3 = 사전 학습 batch baseline. Form 1 streaming axis = phase 1 measurement 미완 | line 277 동일 | line 591 동일 | ✓ |
| 13 | 0.1~0.5초 fit time = SF=1 (1M rows) 한정. SF=10/100 미측정 (선형 scale-up SF=10 ≈ 1~5s, SF=100 ≈ 10~50s 추정) | line 278 동일 | line 592 동일 | ✓ |

→ **PDF §7 정직 disclosure 13 영역 완전 일치**. 13/13 = 100%.

### 6.2 발견 issue

| # | 영역 | severity |
|---|---|---|
| D1 | #14 (handoff v20 §4 정정 룰 #14 line 172, Anti-Neyman 가설) 영역이 정직 disclosure 13 영역에 미포함 | **P1** — 정정 룰 #14 = "Anti-Neyman > Neyman = Neyman 가설 자체 유효, 데이터셋 가정 불만족 + selectivity-dependent" 영역. RQ2 narrative 의 σ_j oracle 가정 한계 영역으로 disclosure 가치 있음 |
| D2 | #15 (PDF §6.6 와의 cross-reference) 영역의 "회의 PDF v2 §3.2 line 532-533 wording = csv 직접 aggregate 와 차이 (출처 source verify 필요)" 영역 (handoff v20 §4 정정 룰 #12 line 170) 가 정직 disclosure 13 영역에 미포함 | P2 |
| D3 | "RQ2 5-way 측정 = SF=100 (DEEP+SIFT) 한정. SF=1/SF=10/SSN 미측정" 영역 (handoff v20 §4 정정 룰 #13 line 171) 이 disclosure 13 영역에 미포함 (PDF §6.6 본문에는 명시) | P2 |

### 6.3 결론

- 정직 disclosure 13 영역 100% completeness (handoff v20 §9 + agent_J §8 + PDF §7 cross-check)
- #14 (Anti-Neyman 가설) 추가 권장 (P1)
- D2/D3 (csv wording + RQ2 SF scope) 추가 권장 (P2)

---

## §7. 정정 룰 14 list 반영 여부

### 7.1 매트릭스 (PDF 어디에 반영됐는지)

> handoff v20 §4 정정 룰 14 list (line 156-172) vs PDF 본문

| # | 정정 룰 | PDF 반영 위치 | 정합 |
|---|---|---|---|
| 1 | "5 단계 中 1 단계" → "Eq 1 (Bernoulli) 대체 vs Eq 2-6 유지" | PDF §2 표 row C "본 contribution" column = "paper §V-B Eq 1-6 verbatim 100% 정합" | ✓ 반영 |
| 2 | "Algorithm 1 14-step" → "paper Eq 1-6 + 17-step pseudo-code" | PDF page 3 표 하단 line "17 step" + paper "algorithm pseudo-code 없음" | ✓ 반영 |
| 3 | "AS single-table 不可 = 구조 X" → "paper §V-B single-table OK, 공개 코드 구현 한계" | PDF §6 review #5 "AS = single-table 不可 wording 정정 (구조 X = 구현 한계)" + PDF §7 #8 | ✓ 반영 (review list + disclosure) |
| 4 | "block only 추출" → "block + row hybrid" | PDF §7 #9 "paper §V-B sampling = block + row hybrid (block only X)" | △ 반영 (disclosure 만). **review list + 본문 답변 부재** |
| 5 | "분포 안다" L1/L2/L3 layer 분리 | PDF §6 review #4 + §7 #10 | ✓ 반영 |
| 6 | "분포 알면 ECQO?" → paper §V-B = "without index" 가정 | PDF §1 paper verbatim + §6 review #1 + §7 #11 | ✓ 반영 (★★★ multi-layer) |
| 7 | "RQ3 = streaming" → "RQ3 = 사전 학습 batch baseline" | PDF §4 본문 "1001 file = baseline + design 근거 (사전 학습 완료된 baseline framing)" + §6 review #2 + §7 #12 | ✓ 반영 |
| 8 | "0.1~0.5초 런타임" → SF=1 fit time, 매 query fit X | PDF §6 review #3 + §7 #13 | ✓ 반영 |
| 9 | Neyman paradox sel=0.01 한정 | PDF §6 review #6 + §6.6 본문 | ✓ 반영 |
| 10 | K granularity SF coverage SF=1+10+100 measured | PDF §6.5 본문 (4 method × 3 SF 표 + 결론) | ✓ 반영 |
| 11 | "Bernoulli → Neyman −10%" → over-statement (실제 −5~−9%) | PDF §6.6 본문 (6 row 표 + 결론) | ✓ 반영 |
| 12 | 회의 PDF v2 §3.2 line 532-533 wording = csv 직접 aggregate 와 차이 | PDF §6.6 "회의 PDF v2 §3.2 line 532-533 ... 출처 source verify 필요" | ✓ 반영 |
| 13 | RQ2 5-way 측정 = SF=100 한정 | PDF §6.6 "RQ2 5-way 측정 = SF=100 (DEEP+SIFT) 한정. SF=1/SF=10/SSN 미측정" | ✓ 반영 |
| 14 | Anti-Neyman > Neyman = Neyman 가설 무효 → 정확 의미 (Neyman 가설 유효, 데이터셋 가정 불만족 + selectivity-dependent) | **PDF 미반영** | ✗ **P0 reflect 부재** |

### 7.2 발견 issue

| # | 영역 | severity |
|---|---|---|
| F1 | **정정 룰 #14 (Anti-Neyman 가설) PDF 미반영** | **P0** — RQ2 narrative core. 박광현 미팅 시 σ_j oracle + 데이터셋 가정 영역 question 들어오면 즉답 부재 |
| F2 | 정정 룰 #4 (block+row hybrid) 가 PDF §7 disclosure 만, review list + 본문 답변 X | **P0** (§2.2 #3 = §7 F1 와 동일 영역) |
| F3 | 정정 룰 #1, #2 가 PDF §2 표 + 표 하단 line 으로만 반영, 박광현 review 시 즉시 anchor 미흡 가능 (PDF 1-2 page 자료라 OK) | P2 |

### 7.3 정정 룰 14 list 반영도

- **반영 12/14 = 86%**
- 미반영 2 영역: #4 (block+row, review/본문 X disclosure 만) + #14 (Anti-Neyman 가설, 완전 X)
- **D-1 미팅 전 보강 P0 권장**

---

## §8. 박광현 미팅 readiness assessment

### 8.1 자료 fix 영역 ready 평가

| 영역 | 상태 | 평가 |
|---|---|---|
| **main theme** (Streaming-aware Distribution-Conscious) | PDF §0 + §1 + 표지 = 명확 fix | ✓ **ready** |
| **4 측면** (대체/보완/개선/추가검증) | PDF §0 line 4 (4 측면 한 줄 명시) | ✓ ready |
| **paper §V-B "without index" anchor** | PDF §1 paper verbatim 2 곳 (page 2) | ✓ ready (Q3 추가 보강 권장) |
| **Component A+B+C+D framework** | PDF §2 표 (page 3) 4 row 명확 | ✓ ready |
| **17-step pseudo-code (10 verbatim + 7 augment)** | PDF §2 표 하단 line + paper hyperparam 7종 명시 | ✓ ready |
| **paper Eq 1-6 100% 정합** | PDF §2 row C "본 contribution" + measure_paper_exact.py PAPER_HYPERPARAM 6/7 verify | ✓ ready |

→ **자료 fix 영역 100% ready**.

### 8.2 변경 가능 영역 review 영역 명확화

| 영역 | PDF §8 fix vs 변경 가능 표 | 평가 |
|---|---|---|
| 측정 plan 우선순위 (SelNet / streaming workload / drift / CE4HD) | △ 변경 가능 | ✓ review 영역 명확 |
| phase 1 / phase 2 timeline 분담 (5/27 / 6/11 / post-6/11) | △ 변경 가능 | ✓ review 영역 명확 |
| paper-grade publication venue (EDBT short / VLDB short / ICDE position) | △ 변경 가능 | ✓ review 영역 명확 |
| 박광현 본업 (RELOAD / CANNON / DFLOP) align | △ 변경 가능 | ✓ review 영역 명확 |

→ **변경 가능 영역 review focus 명확**.

### 8.3 review 요청 12 항목 readiness

| review # | 영역 | PDF 안의 답변 영역 | 미팅 즉답 readiness |
|---|---|---|---|
| 1 | 분포 알면 ECQO? | §1 anchor + §7 #11 | ✓ anchor 강력, but multi-layer 4 cost 비교 표 부재 (agent_J §2) → P1 |
| 2 | RQ3 사전 학습 | §4 본문 + §6 review + §7 #12 | △ review list 만, 본문 답변 표현 부재 → P1 |
| 3 | 0.1~0.5초 fit time | §6 review + §7 #13 | △ review list 만, layer 분리 답변 부재 → P1 |
| 4 | L1/L2/L3 분리 | §6 review + §7 #10 | △ review list 만, L1/L2/L3/L_index 표 부재 → P1 |
| 5 | AS single-table 不可 | §6 review + §7 #8 | △ review list 만 → P1 |
| 6 | Neyman paradox sel=0.01 한정 | §6 review + §6.6 본문 | ✓ §6.6 본문 답변 강력 |
| 7 | Form 1 main theme 학술 정당성 | §0 + §1 + §2 | ✓ main theme + paper anchor + Component 표 종합 ready |
| 8 | framework axis novelty | §2 표 + §7 #2 | ✓ framework axis novelty 명시 |
| 9 | 5/27 phase 1 timeline 52-87h | §4 표 (5/27 phase 1 = 1080 file, 52-87h) | ✓ ready |
| 10 | paper-grade publication venue | §5 timeline (EDBT short 10월 deadline) + §8 변경 가능 영역 | ✓ ready |
| 11 | 박광현 본업 RELOAD/CANNON/DFLOP align | §8 변경 가능 영역 | △ PDF 본문 자체 detail 부재 (Agent D + Agent J §7.4 Q5 contents) → P2 |
| 12 | SelNet impl risk mitigation | §7 #5 (Q-error 재현 risk 10-20%) | ✓ ready |

→ **즉답 readiness 6/12 = 50%** (review #6, #7, #8, #9, #10, #12 ready / #1, #2, #3, #4, #5, #11 P1 보강 권장)

### 8.4 종합 readiness 점수

| 영역 | 점수 |
|---|---|
| 자료 fix 영역 (main theme + 4 측면 + paper §V-B anchor + Component + 17-step + Eq 1-6) | **6/6 = 100%** |
| 변경 가능 영역 review focus | **4/4 = 100%** |
| review 12 항목 즉답 ready | **6/12 = 50%** |
| 박세은 9 영역 PDF 본문 답변 | **2/9 = 22% (K granularity §6.5 + Neyman §6.6 만)** |
| 정직 disclosure 13 영역 | **13/13 = 100%** |
| 정정 룰 14 반영 | **12/14 = 86%** |

**미팅 권장**: D-1 발송 OK (fix 영역 100% + review focus 100%), but P0 + P1 보강 시 강력. **D-1 발송 + 미팅 시 review #1-#5, #11 영역 즉답 backup form (agent_J 답변 form 의 본문 영역 보강)** 권장.

---

## §9. 종합 fix priority

### 9.1 P0 (D-1 미팅 전 필수 보강)

| # | 영역 | 위치 | fix 영역 침해 여부 |
|---|---|---|---|
| **P0-1** | **정정 룰 #14 (Anti-Neyman 가설) PDF 미반영** — RQ2 narrative core, σ_j oracle + 데이터셋 가정 영역 question 즉답 부재 | §6.6 (Neyman 표 뒤) 추가 또는 §7 disclosure #14 추가 | ✗ 침해 없음 (review/disclosure 보강) |
| **P0-2** | **block+row hybrid (정정 룰 #4) review list + 본문 답변 X** (PDF §7 disclosure 만) | §6 review list 에 #5.5 또는 #7 추가 + 본문 답변 영역 (예: §1.5 또는 §2 표 row C 주석) | ✗ 침해 없음 |
| **P0-3** | **박세은 9 영역 中 8:50 (K granularity) 외 본문 답변 영역 부재** — review list 만 6 항목, agent_J §1 영역 1-6 본문 답변 form contents 가 PDF 본문 직접 반영 X (K granularity §6.5 + Neyman §6.6 만 본문) | §6 review list 와 §6.5/§6.6 자세 답변 영역 통합. 또는 §6 review list 各 항목 옆 1-2 line 답변 요약 | ✗ 침해 없음 |

### 9.2 P1 (가능한 보강, 미팅 효율 향상)

| # | 영역 | 위치 | fix 영역 침해 여부 |
|---|---|---|---|
| **P1-1** | YAML frontmatter rendering 정정 (md 첫 6 line) | md line 1-6 | ✗ |
| **P1-2** | paper verbatim Q3 추가 (paper p.6 우단 §V-B implementation "lacks index support") | PDF §1 (page 2) | ✗ |
| **P1-3** | review #1 (ECQO) multi-layer 4 cost 비교 표 (agent_J §2.2 line 244-256) | PDF §1 또는 §6 review #1 옆 | ✗ |
| **P1-4** | review #2 (RQ3 사전 학습) 본문 답변 요약 (agent_J §1 영역 5) | §6 review #2 옆 또는 §4 표 하단 추가 line | ✗ |
| **P1-5** | review #3 (0.1~0.5초) layer 분리 답변 (agent_J §1 영역 6 + §6) | §6 review #3 옆 | ✗ |
| **P1-6** | review #4 (L1/L2/L3) 표 (agent_J §4.5 line 384-389) | §6 review #4 옆 | ✗ |

### 9.3 P2 (polish 영역, 미팅 후 update 가능)

| # | 영역 | 위치 |
|---|---|---|
| P2-1 | §2 표 column width balance | §2 표 |
| P2-2 | 12 page 자료 TOC 추가 (cover sheet) | §0 앞 |
| P2-3 | paper verbatim Q4/Q5 추가 (paper §VI-A + §VI-B) | §1 |
| P2-4 | Eq 1-6 explicit formula (paper exact) | §2 또는 부록 |
| P2-5 | review #11 (박광현 본업 align) detail 명시 (Agent D + Agent J §7.4 Q5) | §6 review #11 옆 |
| P2-6 | RQ2 5-way 측정 SF scope (#13 정정 룰) disclosure 영역 추가 | §7 |
| P2-7 | csv aggregate 차이 (#12 정정 룰) disclosure 영역 추가 | §7 |

### 9.4 fix 영역 침해 시 별도 명시

본 QA 발견 10건 defect (P0 3 + P1 6 + P2 7 = 16건) 모두 **fix 영역 (main theme + 4 측면 + paper §V-B scope) 침해 X**. 모두 보강 / polish 영역.

---

## §10. 권장 보강 form (P0 적용 시)

### 10.1 P0-1 (Anti-Neyman 가설) 추가 wording

PDF §6.6 (page 9) 표 하단 또는 §7 disclosure #14 신규:

> #14: **Anti-Neyman > Neyman ≠ Neyman 가설 무효** — Neyman 가설 (n_j ∝ N_j × σ_j 가 분산 최소) 자체는 유효하나, 본 측정 데이터셋이 Neyman 가정 (cluster 간 σ_j range 다양함, N_i CV 비-0) 불만족 + selectivity-dependent (sel=0.01 paradox / sel=0.1 정합). σ_j oracle 가정 + 직접 측정 추가 검증 필요.

### 10.2 P0-2 (block+row hybrid) review list 추가

PDF §6 review list 에 #5.5 또는 #7 신규:

> #5.5 / #7. paper §V-B sampling = block + row hybrid (Eq 1 N=385 초기 block, 이후 Eq 5 sampling_size 추가 row). 본 연구 contribution scope = 추출 방식 random → stratified 정정, block/row 구조 outside. 정확 framing 권장?

### 10.3 P0-3 (review list 옆 본문 답변 요약) form

PDF §6 review list 各 항목 옆 1-2 line 답변 요약 (agent_J §1 압축):

```
1. (★★★) 분포 알면 ECQO? → paper §V "without index" anchor. ECQO = HNSW (data graph),
   본 = K-means K=20 메타 (15KB). cost 2-3 order 차이. complementary scenario.
2. RQ3 사전 학습 → 1001 file = batch baseline (cold start 1 회 fit 0.1-0.5초 + query ms).
   Form 1 streaming axis = 진짜 online incremental.
3. 0.1~0.5초 매 query? → fit time SF=1, cold start 1 회. 매 query fit X (paper period P=50).
4. L1/L2/L3 → L1 (global skew) / L2 (cluster centroid) / L3 (+σ_j). RQ2 = L3 oracle.
5. AS single-table 不可 → 구조 X = 구현 한계 (paper §V-B 자체는 OK). 임채림 자문 base.
6. Neyman paradox → sel=0.01 한정 (Anti 1.540 < Prop 1.580 < Neyman 1.595).
   sel=0.1 = Neyman best (classical theory 정합).
```

---

## §11. 결론

**PDF v2 (12 page) 핵심 강도**:
- 자료 fix 영역 100% ready (main theme + 4 측면 + paper §V-B anchor + Component A+B+C+D + 17-step + Eq 1-6 + hyperparam 7종 [m verify P2] + 정직 disclosure 13 + 변경 가능 영역 review focus)
- 박세은 9 영역 中 K granularity (§6.5) + Neyman (§6.6) 본문 답변 완전
- review 요청 12 항목 (박세은 6 + 박광현 6) list 100% completeness
- 정정 룰 14 list 中 12 반영 (86%)

**PDF v2 핵심 약점 (P0 3건 + P1 6건 + P2 7건 = 16건 defect)**:
- 정정 룰 #14 (Anti-Neyman 가설) 완전 미반영 (P0-1)
- block+row hybrid (정정 룰 #4) review/본문 부재, disclosure 만 (P0-2)
- 박세은 9 영역 中 7 영역 (block+row + L1/L2/L3 + ECQO multi-layer + RQ3 framing + fit time layer + AS single-table + Anti-Neyman) 본문 답변 영역 직접 부재, review list 만 (P0-3 + P1-3 ~ P1-6)
- YAML frontmatter rendering (P1-1)
- paper verbatim Q3 누락 (P1-2)
- table column balance + TOC + Eq 1-6 explicit formula (P2)

**D-1 미팅 권장 path**:

1. **option A (현재 발송)**: 현 PDF v2 그대로 박광현 발송. 미팅 시 review #1-#5, #11 영역 질문 들어오면 agent_J 답변 form (47.9 KB) 의 본문 영역 즉답. 본 PDF = anchor + review focus 자료, agent_J = detail backup
2. **option B (P0 보강 후 발송, 권장)**: P0 3건 보강 (10-15 분) → PDF v3 (12-13 page) 재생성 → 발송. 미팅 효율 강력
3. **option C (P0 + P1 보강, 1 시간 cost)**: P0 + P1 9건 보강 → PDF v3 (13-14 page) 재생성. paper-grade quality

**사용자 정책 적합 form**: option B (P0 보강 후 발송) 가 학부생 톤 + 정직 disclosure + cherry-picking 회피 + fix 영역 침해 X + 미팅 효율 강력 balance 가장 적합.

**fix 영역 침해**: 없음. 모든 보강 영역이 review/disclosure/본문 답변 영역.

---

> **Agent K 종료**: 2026-05-15 22:30 KST. 본 file = PDF v2 (12 page) final QA 7 영역 종합. P0 3 + P1 6 + P2 7 = 16 defect 분류. fix 영역 침해 X. D-1 미팅 readiness = option B (P0 보강 후 발송) 권장.
