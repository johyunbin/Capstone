# Agent L — post-5/15 mass update mapping (정정 룰 14 × 영향 file 6 matrix)

> 작성: 2026-05-14 22:30 KST  
> base: `handoff_v20_form1_fix_agent_10_session_22h_20260514_2155.md` §4 (정정 룰 14 list) + §15 (영향 file 후보)  
> 목적: 5/15 14:00 박광현 미팅 직후 mass update **일괄 적용** 위한 파일별 line + before/after wording snippet + 우선순위 + cost + 의존성 + 실행 plan  
> 사용자 정책: 학부생 톤 / 한국어 / 정직 disclosure / cherry-picking 회피 (모든 영향 영역 일관 적용) / commit 단위 적절 분할

---

## 0. TL;DR — 14 룰 × 6 file matrix + 5 commit + 3 우선순위

- **영향 영역 총** ≈ **84 cell** (14 룰 × 6 file). 그 中 실제 정정 필요 **42 cell**, 영향 없음 **42 cell**.
- **5 commit 단위** 권장: C1 Registry → C2 회의 PDF v2 → C3 narrative v1 → C4 6/11 outline v3 → C5 5/27 deck v4
- **3 우선순위**:
  - **P0 (5/15 14:00 박광현 미팅 직후 ~ 5/16 24:00)**: 회의 PDF v2 + narrative v1 + Registry (룰 1-12 일괄)
  - **P1 (5/27 발표 전 = 5/16~5/26)**: 5/27 deck v4 → v5 update (룰 1-14 모두 반영)
  - **P2 (6/11 보고서 전 = 5/27~6/10)**: 6/11 outline v3 → v4 + 본문 sprint W5~W6 (룰 1-14 + Form 1 측정 결과)
- **총 cost 추정**: P0 ~5h (line edit + section rewrite 2 영역) + P1 ~12h (slide rewrite) + P2 ~25h (sprint 분담 4 팀원)
- **의존성 graph**: Registry → 회의 PDF v2 → narrative v1 → 5/27 deck → 6/11 outline (왼쪽 정정이 오른쪽의 source)

---

## §1. 정정 룰 14 × 영향 file 6 matrix (cell 별 영향 상태)

표 표기:
- **A=high** (전면 정정, line 또는 section rewrite ≥ 1)
- **B=mid** (1-3 line edit)
- **C=low** (1 wording edit)
- **—** (영향 없음, 정정 불필요)
- **NEW** (해당 file 신규 영역 작성 필요, 룰의 anchor 가 source 자체에 없음)

| 룰 # | 룰 요약 | 회의 PDF v2 md | 5/27 deck v4 | 6/11 outline v2/v3 | narrative v1 | METHOD_REGISTRY | EXPERIMENT_REGISTRY |
|---|---|---|---|---|---|---|---|
| 1 | "5 단계 中 1 단계" → "Eq 1 (Bernoulli) 대체 vs Eq 2-6 유지" | NEW | NEW (slide 10-13) | NEW (§3.3) | NEW (§4) | C (§3.2 P3 narrative) | C (§9 5단계 narrative 정정) |
| 2 | "Algorithm 1 14-step" → "paper §V-B Eq 1-6 + 본 의역 17-step pseudo-code" | NEW | NEW (slide 11-12) | NEW (§3.3 + §5.4) | NEW (§4) | — | — |
| 3 | "AS single-table 不可 = 구조 X" → "paper §V-B single-table OK, 공개 코드 구현 한계" | A (line 642-652) | NEW (slide 4 한정) | C (§1.2 narrative) | — | — | — |
| 4 | "block only 추출" → "block + row hybrid" | A (line 257-301, 508-520) | NEW (slide 6, 11) | C (§2 Background) | C (§4) | — | — |
| 5 | "분포 안다" → L1/L2/L3 layer 분리 | A (line 902-918, 879-928) | NEW (slide 4, 8) | A (§5.3 신규 sub) | A (§9 + §11 multiple) | C (§0 narrative) | — |
| 6 | **★★★ "분포 알면 ECQO?"** → paper §V-B = "without index" 가정 (p.5 verbatim) | NEW (§1 + §4.2 Q6) | NEW (slide 5 anchor) | A (§1.2 + §5.1) | NEW (§1) | C (§3.1 P3 narrative) | — |
| 7 | "RQ3 = streaming" → "RQ3 = 사전 학습 batch baseline, Form 1 = streaming axis" | A (line 540-557, 880-928) | NEW (slide 12, 17) | A (§1.3 + §3.3) | A (§4 + §11.1) | C (§11 storyline 5/27) | C (§9 5단계 narrative) |
| 8 | "0.1~0.5초 런타임" → SF=1 fit time, 매 query fit X | A (line 466-484, 1525-1599) | C (slide 14) | C (§4.5 + §6) | C (§11.1-11.6) | — | — |
| 9 | "Neyman paradox" → sel=0.01 한정, sel=0.1 = Neyman best (selectivity-dependent) | A (line 365-396, 387-389, 957-1031) | NEW (slide 8 + 17) | A (§4.2 + §5.3) | — (narrative 미언급) | C (§11 storyline 단계 2) | C (§9 단계 1+2) |
| 10 | K granularity SF coverage: SF=1+10+100 × K=10/20/30 measured (48 file) ✓ 완료 | B (line 304-327) | C (slide 14 +1 line) | C (§4.5) | C (§11 footnote) | — | — |
| 11 | "Bernoulli → Neyman −10%" → 실제 측정 X (POOL −5~7%, 단일 cell SIFT sel=0.1 −9.16%) | A (line 383-395, 520-535) | C (slide 8) | C (§4.2) | — | — | C (§6.2 5-way) |
| 12 | 회의 PDF v2 §3.2 line 532-533 wording → csv 직접 aggregate 값 출처 verify | A (line 528-535) | — | — | — | — | — |
| 13 | RQ2 5-way 측정 = SF=100 (DEEP+SIFT) **한정**. SF=1/SF=10/SSN 미측정 | A (line 365-395, NEW §7) | C (slide 8 footnote) | A (§4.2 + §5.3) | — | — | C (§6.2 footnote) |
| 14 | "Anti-Neyman > Neyman = 가설 무효" → Neyman 가설 유효 but 분산 uniform 조건 不만족 | A (line 391-395, 957-1031) | NEW (slide 8 + 17) | A (§5.3) | — | C (§4.3 narrative) | C (§9 footnote) |

**cell 영향 상태 종합**:
- A=high 19 cell (전면 정정)
- B=mid 1 cell (line range edit)
- C=low 13 cell (1 line wording)
- NEW 13 cell (anchor 자체가 source 부재 — 신규 작성)
- — 38 cell (영향 없음)

→ **총 정정 영역 46 cell** (84 - 38). 그 中 NEW + A = **32 cell 이 high cost** (전면 작업).

---

## §2. file 별 정정 영역 line + before/after snippet

### 2.1 회의 PDF v2 md (`/Users/hyunbin/Capstone/submission/_drafts/archive/속도는벡터 - 프로젝트 정리 (저녁 긴급 회의 숙지용).md`, 1681 line)

**high-impact 12 영역** (룰 1-14 中 12 룰 영향, 미영향 2 = 룰 12 단독 wording verify):

#### §2.1.1 룰 1 (5 단계 中 1 단계 → Eq 1 vs Eq 2-6) — NEW

- **anchor 부재**: 회의 PDF v2 §V-B narrative 가 "5 단계 中 1 단계" 표기를 직접 안 함. handoff v20 §4 룰 #1 의 source 가 다른 자료 (5/27 deck v3 prompt + agent B 검증).
- **신규 작성 영역**: 회의 PDF v2 §2.4 "sample 수 단계별" 이후 신규 sub-section (§2.4.1) **"본 논문 §V-B Eq 1-6 의 본 연구 정정 영역"** 추가 권장.
- **before** (없음 — 신규 작성)
- **after wording snippet**:
  > "본 논문 §V-B 의 Adaptive Sampling 은 Eq 1 (sample budget N=385 추출) + Eq 2-6 (동적 표본 수 조정) 의 6 식 구성이다. 본 연구는 그 中 Eq 1 (Bernoulli 무작위 추출) 만 distribution-aware 추정량으로 대체하고, Eq 2-6 (period=50 재계산, m=0.9 모멘텀, η₀=0.1 학습률, α=50 warmup, β=1.5 분산 배수, γ=0.99 감쇠) 는 paper exact 그대로 유지한다. 즉 본 연구의 contribution scope 는 Eq 1 의 추출 방식 정정만이다."
- **cost**: 신규 1 paragraph (~10 line) 추가. **30분**.

#### §2.1.2 룰 2 (Algorithm 1 14-step → Eq 1-6 + 17-step pseudo-code) — NEW

- **anchor 부재**: 회의 PDF v2 가 "Algorithm 1" 표기를 직접 사용 안 함. 5/27 deck v3 prompt + Form 1 영역에서 사용 예상.
- **신규 작성 영역**: §2.4.2 또는 §3 본문에 "paper §V-B 자체 algorithm pseudo-code 부재" 정직 disclosure 명시 + 본 연구 의역 17-step 명시.
- **after wording snippet**:
  > "본 논문 §V-B 자체에는 algorithm pseudo-code 가 없다 (Eq 1-6 + 산문 + hyperparam 7종만 명시). 본 연구는 paper Eq 1-6 verbatim 영역 (10 step: Step 1-2, 6, 8-13, 16) + 본 연구 augment 영역 (7 step: Step 3-5, 7, 14-15, 17) = 17-step pseudo-code 로 의역했다. Agent F+G 의 paper 직접 정독 후 정정."
- **cost**: 신규 1 paragraph (~8 line). **20분**.

#### §2.1.3 룰 3 (AS single-table 不可 → 공개 코드 구현 한계) — A=high

- **현 line 642-652** verbatim:
  > "답변 — 본 논문 §V-B Adaptive Sampling 은 single-table 도 다룬다. 본 연구 측정 환경 9 개 중: 단일 테이블 6 cell ... 다중 테이블 3 cell (join). 본 연구의 단독 best (minibatch_partial −10.17%) 도 다중 테이블 (Fig9) 포함 9 cell 평균이다."
- **현 상태**: 회의 PDF v2 는 이미 룰 3 의 정확 wording 으로 정정 완료 (5/14 18:00 회의 직후 정정 영역). 추가 정정 영역 = **§4.1 narrative 본문 + §4.2 Q6 답변**의 일관성 확인. 박세은 9:09 #1 카톡 ("측정 영역의 우연" 측면) 추가 명시 권장.
- **after wording snippet (line 647 추가 보강)**:
  > "본 논문 §V-B Adaptive Sampling 은 single-table 도 다룬다 (paper p.5 좌단 + p.6 §V-B 첫 단락 + §VI-B verbatim 모두 '단일 테이블 + 다중 테이블 양쪽 cover'). 본 연구 측정 영역이 multi-join 으로 자연 이동한 이유는 **공개 코드 영역의 구현 한계**에서 single-table AS 가 동작하지 않아서이지, paper 의 구조적 한계는 아니다. 즉 본 연구의 multi-join 영역 measurement 가 paper 의 구조적 한계라기보다는 우연의 측면 (박세은 9:09 카톡 #1)."
- **cost**: 1 paragraph 보강 + 1 sentence 추가. **15분**.

#### §2.1.4 룰 4 (block only → block + row hybrid) — A=high

- **현 line 257-301** (§2.4 sample 수 단계별, **블록 sample: 본 연구 미사용** 표기) verbatim:
  > "블록 sample: **본 연구 미사용** (정합성 위반 10 종에 chunk 기반 method 폐기)"
- **정정 영역**: paper §V-B 자체가 block + row hybrid (page 단위 + row 단위 모두 cover) 임을 명시. 박세은 9:09 #2 카톡 verbatim.
- **after wording snippet (line 275 정정)**:
  > "블록 sample: paper §V-B 자체 = **block + row hybrid** (page 단위 추출 + row 단위 추출 양쪽 cover). 본 연구 측정 영역은 row 단위 한정 (chunk 기반 method 폐기 영역). paper 의 구조 자체는 block + row 양쪽이지만 본 연구의 measurement scope 가 row 한정. (박세은 9:09 카톡 #2)"
- **cost**: 1 line wording edit + footnote 추가. **15분**.

#### §2.1.5 룰 5 (분포 안다 → L1/L2/L3) — A=high

- **현 line 879-918** (§5.1-5.3 narrative 재정의 영역) — 이미 회의 PDF v2 가 L0/L1/L2/L3/L4 framework 명시함. 다만 박세은 9:09 #3 의 더 정확한 분류 (Agent J anchor) 적용.
- **before** (line 902-913 verbatim, L0-L4 framework 표):
  > "L0: 정보 없음 / L1: + skew flag / L2: + 그룹 정의 / L3: + 그룹 정의 + sz_j / L4: + 그룹 정의 + sz_j + σ_j"
- **after wording snippet (정정 권장 — Agent J + 박세은 9:09 카톡 verbatim 명시)**:
  > "회의 시 박세은 9:09 카톡 #3 verbatim: 본 연구의 '분포 안다' 는 L1 (global skew flag, HHI) / L2 (cluster boundary, K-means K=20 centroid) / L3 (+ σ_j 분산, Neyman allocation) 3 layer 분리. L2 = K-means fit (0.1~0.5초 SF=1), L3 = oracle 가정 (RQ2 측정 시점). 본 회의 §5.3 의 L0-L4 framework 는 본 문서가 처음 정리한 framework 이며, 박세은 9:09 분류 (L1/L2/L3 3 layer) 와 alignment 권장."
- **cost**: 1 sub-section 재정리 + 박세은 verbatim quote 추가. **30분**.

#### §2.1.6 ★★★ 룰 6 (분포 알면 ECQO?) — NEW (★★★ 최대 evidence)

- **anchor 부재**: 회의 PDF v2 §1, §4.2 Q6 답변 등에 "ECQO 대안 가능?" 영역이 직접 명시 안 됨.
- **신규 작성 영역 (★★★ 가장 중요)**: §1 본 연구 anchor 또는 §4.2 새 Q (Q12 후 신규) 또는 §5.x 신규 sub 에 paper §V "without index" anchor 명시.
- **after wording snippet** (Agent J verbatim, ★★★ 카톡 복붙 가능 form):
  > "박세은 9:09 카톡 #4 ★★★ 영역 (ECQO 대안 가능?) 답변: paper p.5 좌단 §V 도입부 verbatim: 'For VAQs with vector indexes, Exqutor employs Exact Cardinality Query Optimization (ECQO)... For VAQs **without index**, Exqutor uses a sampling-based approach to approximate selectivity (subsection V-B).' 즉 paper §V-B 영역 자체가 'without vector index' 가정 위에서 진행. 본 연구 (Form 1) 는 paper §V-B 영역 한정 후속 연구이고, '분포 알면 ECQO 가능?' 영역 (ECQO multi-layer 4: (a) paper §V-B 영역 자체 = without index 가정 / (b) ECQO cost HNSW O(n log n) vs Form 1 cost K-means K=20 fit 0.1~0.5초 / (c) ECQO + Form 1 complementary (high-frequency = ECQO, ad-hoc = Form 1) / (d) '분포 안다' L1/L2/L3 vs L_index 다른 추상화 layer) 는 본 연구 outside."
- **cost**: 신규 1 sub-section (~15-20 line) 작성. **45분**.

#### §2.1.7 룰 7 (RQ3 = streaming → batch baseline + Form 1 streaming axis) — A=high

- **현 line 540-557** (§4.1.4 분포 모를 때 method runtime) verbatim:
  > "RQ3 (분포 모름) 의 measurement protocol: 1. 데이터 도착 → method 학습 / 2. K=20 stratum 분할 / 3. Query 도착 → sample 처리. 학습 (1, 2) 은 **사전 계산**, query 시점에는 sample 처리만 (**실시간**)."
- **정정 영역**: 회의 PDF v2 §4.1.4 line 547 의 "사전 계산" 표기 → "사전 학습 batch baseline" 명확화 + Form 1 (streaming axis) 와 분리. 박세은 9:09 #5 + 9:27 카톡 verbatim 적용.
- **after wording snippet (line 547 정정)**:
  > "본 연구 RQ3 protocol = **사전 학습 batch baseline** (paper period=50 가정 안에서의 정합. 진짜 streaming per-tuple incremental 은 본 RQ3 outside 영역). 박세은 9:09 카톡 #5 의 'RQ3 사전 학습' framing 적용. **Form 1 streaming axis** (Streaming-aware Distribution-Conscious Cardinality Estimation, agent E+F+G+H 종합) = paper §VI-B 'shifting workloads' 영역의 후속 연구 axis, 본 RQ3 와 complementary framework."
- **cost**: 1 sub-section narrative 재정리 (line 540-557, 880-928 영향). **40분**.

#### §2.1.8 룰 8 (0.1~0.5초 런타임 → SF=1 fit time, 매 query fit X) — A=high

- **현 line 466-484** (§3.5 Pareto Top 5 자원 효율, fit time 0.1~0.5초 표기) + **line 1525-1599** (부록 method 별 자원 표) — 모든 위치에서 "fit time 0.1~0.5초" 의 **SF=1 한정** 명시 부재.
- **before** (line 471 verbatim):
  > "hilbert_real | 0.1 ~ 0.5 s | O(N) | −9.27%"
- **after wording snippet (line 466-484 추가 footnote + line 553 명시 보강)**:
  > "★ 정정 (박세은 9:27 카톡): fit time 0.1~0.5 초 = **SF=1 한정** (1M rows × 96d DEEP, ~384 MB). SF=10/100 fit time = 미측정 (선형 scale-up SF=10 ≈ 1~5초, SF=100 ≈ 10~50초 추정). 본 연구의 'fit time' 은 **사전 학습 1 회 cost** 이고 **매 query 마다 fit 하는 cost 가 아님** (paper period P=50 가정 안에서의 fit). 진짜 streaming per-tuple incremental fit 는 Form 1 영역 (future work)."
- **cost**: 1 sub-section + 부록 표 footnote 추가. **30분**.

#### §2.1.9 룰 9 (Neyman paradox sel=0.01 한정 vs sel=0.1 = Neyman best) — A=high

- **현 line 365-396** (§3.2 RQ2 narrative) + **line 957-1031** (§6 Neyman paradox 진짜 원인) verbatim:
  > "5-way 5 cell × 5 trial 평균 mean Q-error: Bernoulli 1.748 / Equal 1.637 (−6.35%) / Proportional 1.580 (−9.61%) / Neyman 1.595 (−8.75% paradox) / Anti 1.540 (−11.90% anomaly)"
- **정정 영역**: 박세은 9:42 카톡 + Agent B 정정 = selectivity-dependent. sel=0.01 에서만 paradox, sel=0.1 에서는 Neyman best (classical theory 정합).
- **after wording snippet (line 388-396 + line 1015-1031 신규 sub §6.2.1 추가)**:
  > "★ 정정 (박세은 9:42 카톡 verbatim + Agent B 정정): Neyman paradox 는 **sel=0.01 한정** 발현. sel=0.1 에서는 Neyman best (paired n=??): sel=0.01 (paired n=455): Neyman 1.595 / Anti 1.540 / Prop 1.580 → Proportional best (paradox) / sel=0.1: Neyman 1.1076 / Anti 1.1101 / Prop 1.1135 → **Neyman best** (classical theory 정합). selectivity-dependent. 즉 본 회의 §3.2 + §6 의 paradox narrative 는 sel=0.01 영역 한정 명시 권장."
- **cost**: §3.2 + §6 2 영역에 sel=0.01 한정 명시 + sel=0.1 측정값 추가 표. **45분**.

#### §2.1.10 룰 10 (K granularity SF coverage SF=1+10+100 × K=10/20/30 measured 48 file) — B=mid

- **현 line 304-327** (§2.5 K granularity 검증 범위) verbatim:
  > "K 변화 측정은 SF=100 (A1) + SF=10 (A2) 범위에서만 진행했다. **SF=1 영역에서 K=20 이 best 인지는 미측정**."
- **정정 영역**: 5/14 21:00 launch 후 22:10 회수 완료 (handoff v20 §10) → SF=1+10+100 × K=10/20/30 = 48 file 측정 완료. 회의 PDF v2 의 "SF=1 미측정" wording 정정.
- **after wording snippet (line 322 정정)**:
  > "★ 정정 (5/14 22:10 추가 측정 완료): K 변화 측정은 SF=100 (A1) + SF=10 (A2) + **SF=1 (A5-scale-sf1 신규 측정 5/14 22:10 회수)** × K=10/20/30 = **48 file 측정 완료**. 핵심 finding: SF=1 영역 K=20 best 여부 = **method-dependent**. sparse_rp/chao_weighted = K=20 sweet spot, hilbert_real/hyperloglog = K=30 slight edge. **모든 SF axis 에서 패턴 일관**. 회의 PDF v2 의 'SF=1 영역 미측정' wording 정정 가능."
- **cost**: 1 paragraph + 신규 표 (3-way SF=1/10/100 × K=10/20/30) 추가. **30분**.

#### §2.1.11 룰 11 (Bernoulli → Neyman −10% narrative → 실제 측정 X) — A=high

- **현 line 383-395** (§3.2 RQ2 narrative) + **line 520-535** (§4.1.3 Neyman from→to) verbatim:
  > "Neyman 의 absolute mean 은 1.595 로 Bernoulli 1.748 에서 −8.75%. 본 연구가 narrative 에 'Neyman 10% 감소' 라고 표현한 것은 −8.75% 의 반올림 표현이지만, **정확히는 Proportional 이 best (−9.61%)** 이고 Neyman 은 Proportional 에 졌다 (paradox)."
- **정정 영역**: 박세은 9:54 카톡 + RQ2 csv 직접 verify → "Bernoulli → Neyman −10%" 는 **실제 측정 X**. POOL −5~7% (5 cell aggregate), 단일 cell best (SIFT sel=0.1) −9.16% 가 실측 maximum.
- **after wording snippet (line 535 정정)**:
  > "★ 정정 (박세은 9:54 카톡 + 본 verify): 'Bernoulli → Neyman −10%' narrative 는 **실제 측정값 X**. POOL aggregate (5 cell average) Bernoulli → Neyman 실측 Δ% = **−5~7%** (SF=100 DEEP+SIFT 한정), 단일 cell best (SIFT sel=0.1) = **−9.16%** (실측 maximum). 'Neyman 10% 감소' 는 narrative 의 과대 표기. 정확 wording = 'Bernoulli → Proportional −9.53% (POOL aggregate, RQ2 csv 직접 확인 후 정정 권장)'."
- **cost**: 1 sub-section + RQ2 csv 직접 aggregate 값 verify 표 추가. **40분**.

#### §2.1.12 룰 12 (§3.2 line 532-533 wording → csv aggregate verify) — A=high

- **현 line 528-535** verbatim:
  > "| Proportional | 1.580 | −9.61% | / | Neyman | 1.595 (paradox) | −8.75% |"
- **정정 영역**: 본 wording 의 csv 출처 source verify 필요. 회의 PDF v2 가 narrative base 표기인데, 실측 csv 직접 aggregate 값과의 차이가 있을 가능성.
- **after wording snippet (line 528-535 정정)**:
  > "★ 정정 (csv 직접 verify 권장 영역, 박세은 9:54 + 본 verify): | Proportional | 1.580 | −9.61% | (★ narrative base, 5/14 측정 csv 직접 확인 미완) / | Neyman | 1.595 | −8.75% | (★ narrative base, 동상). 실측 csv 직접 aggregate 후 정정 권장. handoff v20 §4 룰 #12."
- **cost**: 5-way 측정 csv 5 cell × 5 trial 직접 aggregate + 정정. **1시간** (csv 직접 verify 작업 포함).

#### §2.1.13 룰 13 (RQ2 5-way 측정 = SF=100 DEEP+SIFT 한정) — A=high

- **현 line 365-395** (§3.2 RQ2) + **line 957-1031** (§6 Neyman paradox) verbatim — 모든 RQ2 narrative 가 "5 cell × 5 trial" 표기인데, 실제 측정 영역 = **SF=100 (DEEP+SIFT) 한정**, SF=1/SF=10/SSN 미측정.
- **정정 영역**: 사용자 22:05 confirm + RQ2 csv file 명 verify → RQ2 5-way scope 정확 명시.
- **after wording snippet (line 365-395 footnote + §7 환각 disclosure 신규 추가)**:
  > "★ 정정 (사용자 22:05 confirm + 본 verify): RQ2 5-way 측정 범위 = **SF=100 (DEEP+SIFT)** 한정. SF=1 / SF=10 / SSN / 다중 테이블 = **미측정 영역**. RQ2 narrative 의 '5 cell × 5 trial 평균' 은 SF=100 영역 한정 표기. 다른 SF / 데이터셋 / 다중 테이블 영역의 Neyman paradox 일반화 가능성 = **미검증** (5/15 박광현 미팅에서 자문 권장)."
- **cost**: §3.2 + §6 + §7.1 (환각 disclosure) 3 영역에 SF=100 한정 명시 + 신규 환각 영역 추가. **45분**.

#### §2.1.14 룰 14 (Anti-Neyman > Neyman 가설 무효 → 가설 유효 but 데이터 조건 不만족) — A=high

- **현 line 391-395** (§3.2 Neyman paradox 박스) + **line 1015-1031** (§6.3 paradox 의미) verbatim:
  > "Anti 1.540 < Prop 1.580 < Neyman 1.595 — 이론상 최적인 Neyman 이 실제로는 Proportional 에게 졌다. σ_j 의 범위가 1.3 ~ 1.6 배로 좁고..."
- **정정 영역**: 박세은 10:15 카톡 + Cochran 1977 §5.5 partial → Neyman 가설 **자체는 유효** (textbook theorem). 단 본 데이터셋이 Neyman 의 **가정 조건 (cluster 간 분산 다양함) 不만족**. selectivity-dependent (sel=0.01 paradox / sel=0.1 정합). σ_j 직접 측정 추가 검증 필요 (현재 oracle 가정).
- **after wording snippet (line 391-395 + line 1026-1031 정정)**:
  > "★ 정정 (박세은 10:15 카톡 + Cochran 1977 §5.5 partial + Agent B 검증): Anti-Neyman > Neyman 결과 = **Neyman 가설 자체 무효 X**. 정확 의미: (a) **Neyman 가설 자체는 유효** (textbook theorem, Cochran 1977 §5.5 verbatim) / (b) **본 데이터셋이 Neyman 의 가정 조건 (cluster 간 분산 다양함) 不만족** (σ_j range 1.3-1.6× narrow 의 정량) / (c) **selectivity-dependent** (sel=0.01 paradox / sel=0.1 = Neyman best 정합) / (d) **σ_j 직접 측정 추가 검증 필요** (현재 RQ2 = σ_j oracle 가정, 직접 측정 미완). 즉 본 결과는 Neyman 가설 부정이 아니라 본 데이터 조건 (분산 uniform) 의 특수 케이스."
- **cost**: §3.2 + §6 + §7 3 영역에 정확 의미 명시. **30분**.

#### 회의 PDF v2 md 총 cost = **30+20+15+15+30+45+40+30+45+30+40+60+45+30 = 475분 ≈ 8시간**

→ 단, ★★★ 룰 6 + 룰 7 + 룰 11 + 룰 12 가 P0 최우선 (총 2.5h).  
→ 나머지 룰 1-5 + 룰 8-10 + 룰 13-14 가 P0 + P1 (5시간).

---

### 2.2 narrative v1 (`/Users/hyunbin/Capstone/submission/_drafts/archive/속도는벡터_본연구_narrative_최종정리_v1.md`, 196 line)

**high-impact 7 영역** (룰 1-7 中 일부 + 룰 8 영향):

#### §2.2.1 룰 1 (5 단계 中 1 단계 → Eq 1 vs Eq 2-6) — NEW

- **anchor 부재**: narrative v1 §4 "단독 대체" 영역 (line 21-23 "본 논문의 베르누이 추정값을 우리 method 의 추정값으로 단순히 바꿔 끼우는 방식") 이 "Eq 1 만 대체" 명시 부재.
- **신규 작성 영역**: §4 첫 단락 또는 신규 footnote 에 paper §V-B Eq 구조 + 본 연구 contribution scope 명시.
- **after wording snippet (line 21-23 보강)**:
  > "남은 method 들로 첫 번째 모드를 측정했다. **paper §V-B 의 Adaptive Sampling = Eq 1 (Bernoulli sample budget N=385) + Eq 2-6 (동적 표본 수 조정 6 식) 의 6 식 구성**이다. 본 연구는 그 中 Eq 1 (Bernoulli 무작위 추출) 만 우리 method 의 추정값으로 바꿔 끼우는 방식이다 (Eq 2-6 = paper exact 그대로 유지). 측정 결과 ..."
- **cost**: 1 sentence 보강. **15분**.

#### §2.2.2 룰 2 (Algorithm 1 14-step → 17-step) — NEW

- **anchor 부재**: narrative v1 가 "Algorithm 1" / "14-step" 표기 직접 안 함. handoff v20 §4 룰 #2 의 source 가 다른 자료 (5/27 deck v3 prompt + agent F+G).
- **신규 작성 영역**: §4 또는 §6 (결합 한계) 또는 §11 (method 깊이 소개) 에 paper §V-B pseudo-code 부재 + 본 연구 17-step 정직 명시.
- **after wording snippet (신규 §3.5 또는 §4 footnote 추가)**:
  > "★ 정직 disclosure: paper §V-B 자체에는 algorithm pseudo-code 가 없다. Eq 1-6 + 산문 + hyperparam 7종만 명시. 본 연구의 17-step pseudo-code = paper Eq 1-6 verbatim 영역 10 step + 본 연구 augment 영역 7 step 의 의역. Agent F+G 의 paper 직접 정독 결과."
- **cost**: 신규 footnote (~5 line). **15분**.

#### §2.2.3 룰 5 (분포 안다 → L1/L2/L3) — A=high

- **현 line 11, 21-23, 39-40, 107-152** (§1 + §4 + §8 + §11) 다수 영역에 "분포 정보를 알 수 있다면" 표기.
- **before** (line 11):
  > "본 논문 (Exqutor) 은 벡터 증강 분석 쿼리에서 인덱스가 없을 때 무작위 표집 (베르누이 + 동적 표본 수 조정) 으로 카디널리티를 추정한다. ... 우리는 이 영역에서 '분포 정보를 알 수 있다면 어디까지 정확도를 끌어올릴 수 있나' 를 정량으로 확인했다."
- **after wording snippet**:
  > "본 논문 (Exqutor) 은 벡터 증강 분석 쿼리에서 **인덱스가 없을 때** (paper §V 'without index' verbatim) 무작위 표집 (베르누이 + 동적 표본 수 조정) 으로 카디널리티를 추정한다. ... 우리는 이 영역에서 '**분포 정보 L1 (global skew flag) / L2 (cluster boundary) / L3 (+ σ_j 분산)** 3 layer 各각의 정확도 우위를 정량으로 확인'했다."
- **cost**: §1 + §4 + §8 + §11 4 영역에 L1/L2/L3 명시. **45분**.

#### §2.2.4 ★★★ 룰 6 (분포 알면 ECQO?) — NEW

- **anchor 부재**: narrative v1 §1 출발점이 paper §V "without index" anchor 명시 X.
- **신규 작성 영역**: §1 첫 단락 또는 신규 §1.1 에 paper §V "without index" anchor 명시. ★★★ 가장 중요한 정정.
- **after wording snippet (§1 line 11 정정)**:
  > "본 논문 (Exqutor) 은 벡터 증강 분석 쿼리에서 **인덱스가 없을 때** 무작위 표집 ... (paper p.5 좌단 verbatim: 'For VAQs **without index**, Exqutor uses a sampling-based approach to approximate selectivity (subsection V-B)'). 본 연구 (narrative v1) 는 **paper §V-B 영역 한정** 후속 연구이고, '인덱스가 있을 때 ECQO 가능 영역' (paper §V-A) 은 본 연구 outside 영역."
- **cost**: 1 paragraph 보강. **30분**.

#### §2.2.5 룰 7 (RQ3 = streaming → batch baseline + Form 1 streaming axis) — A=high

- **현 line 23, 31-37, 39-43, 105-152** (§4 단독 대체 + §6-§8 결합 + §11 method 깊이) verbatim 영역.
- **before** (line 11):
  > "우리는 이 영역에서 ... 정량으로 확인했다."
- **after wording snippet (§1 line 11 추가 보강 + §4 보강)**:
  > "본 연구 narrative v1 은 **사전 학습 batch baseline** 영역 (paper period=50 가정 안에서의 정합) 한정. 진짜 streaming per-tuple incremental fit 는 본 narrative v1 outside 영역 (Form 1 streaming axis, handoff v20 §1)."
- **cost**: §1 + §4 + §11 3 영역에 batch baseline framing 명시. **40분**.

#### §2.2.6 룰 8 (0.1~0.5초 런타임 → SF=1 fit time, 매 query fit X) — C=low

- **현 line 112, 120, 128, 136, 144, 152** (§11 method 깊이 소개 6 영역) verbatim:
  > "학습 시간 0.5 초" / "학습 시간 0.1 초" 등
- **정정 영역**: 각 method 별 "학습 시간 X 초" 표기에 **SF=1 한정** footnote 추가.
- **after wording snippet (§11 전체에 1 footnote 추가)**:
  > "★ 정직 disclosure: 본 §11 의 fit time 표기 (0.1~0.5 s) = **SF=1 한정** (1M rows × 96d DEEP). SF=10/100 fit time = 미측정 (선형 scale-up 추정 SF=10 ≈ 1~5초, SF=100 ≈ 10~50초). 매 query 마다 fit X (사전 학습 1 회 cost, paper period P=50 안에서의 fit)."
- **cost**: 1 footnote 추가. **15분**.

#### narrative v1 총 cost = **15+15+45+30+40+15 = 160분 ≈ 2.5시간**

→ P0 (5/16 24:00 까지) 적용 권장.

---

### 2.3 6/11 보고서 outline v2/v3 (`/Users/hyunbin/Capstone/plans/최종보고서_outline_v2_20260508.md` 524 line + `6_11_보고서_outline_v3_update_plan_20260511.md` 134 line)

**high-impact 8 영역** (룰 1-2 + 5-7 + 9 + 13-14 영향):

#### §2.3.1 룰 1+2 (Eq 1 vs Eq 2-6 + 17-step pseudo-code) — A=high (§3.3 신규)

- **현 outline v2 line 80** (§1.2 문제 정의) + **outline v3 line 49** (§3.3 paper exact verbatim) 둘 다 paper §V-B Eq 구조 표기 부재.
- **신규 작성 영역**: outline v3 → v4 update 시 §3.3 신규 sub "paper §V-B Eq 1-6 구조 + 본 연구 Eq 1 정정 영역" 추가.
- **after wording snippet (v3 line 49 보강)**:
  > "§3.3 paper §V-B Eq 1-6 verbatim + 본 연구 contribution scope: Eq 1 (Bernoulli sample budget N=385) **대체** vs Eq 2-6 (period=50, m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99) **유지**. paper §V-B 자체에는 algorithm pseudo-code 부재 (Eq + 산문 + hyperparam 7종만). 본 연구 = paper Eq 1-6 verbatim 영역 10 step + 본 연구 augment 영역 7 step = 17-step pseudo-code 의역 (handoff v20 §2)."
- **cost**: §3.3 신규 sub (~10 line). **30분**.

#### §2.3.2 룰 5+6 (L1/L2/L3 layer + ECQO anchor) — A=high (§1.2 + §5.1)

- **현 outline v2 line 80** (§1.2 문제 정의) + **v3 line 42** (§1.3 연구 질문 update) verbatim:
  > "v2 §1.2 문제 정의 — 단일 테이블 영역에서 BERN sampling 의 부정확성"
- **신규 작성 영역**: §1.2 anchor 추가 + §5.1 contribution claim 추가.
- **after wording snippet (v3 line 42 → v4 보강)**:
  > "§1.2 문제 정의: paper §V '**without vector index**' 가정 (paper p.5 좌단 + p.6 §V-B 첫 단락 + §VI-B verbatim) 안에서 Bernoulli random sample 추출의 부정확성. 본 연구는 paper §V-B 영역 한정 후속 연구이고, ECQO (§V-A) 영역은 outside. 본 연구의 '분포 안다' 정의 = **L1 (global skew flag) / L2 (cluster boundary) / L3 (+ σ_j)** 3 layer 분리 (박세은 9:09 카톡 #3 + Agent J)."
- **cost**: §1.2 + §5.1 2 영역에 신규 정의 추가. **30분**.

#### §2.3.3 룰 7 (RQ3 = streaming → batch baseline + Form 1 axis) — A=high (§1.3 RQ 재정의)

- **현 outline v3 line 16** (§3 Methodology 표) verbatim:
  > "§4 Results | RQ1 ρ=−0.680 / RQ2 40/40 cells / RQ3 4강 | paper exact 재현 9 cells × 56 method × 2 modes (908 file, 80.4% coverage) + CaseB ensemble paired CaseB > CaseA 92.9%"
- **신규 작성 영역**: §1.3 RQ 재정의 + §3.3 batch baseline framing 명시 + §4.4 Form 1 axis future work 추가.
- **after wording snippet (v3 line 16 → v4)**:
  > "§1.3 RQ 재정의: **RQ3 = 사전 학습 batch baseline 영역 한정** (paper period=50 가정 안에서의 정합). 진짜 streaming per-tuple incremental fit = **Form 1 streaming axis** (handoff v20 §1, Streaming-aware Distribution-Conscious Cardinality Estimation) = 본 RQ3 와 complementary framework, 본 보고서 §6.2 Future Work 영역."
- **cost**: §1.3 + §3.3 + §6.2 3 영역에 batch + streaming framing 명시. **45분**.

#### §2.3.4 룰 9 (Neyman paradox sel=0.01 한정) — A=high (§4.2 + §5.3)

- **현 outline v2 line 95** (§2.2 Stratified Sampling) + **v3 line 17** (§4 Results RQ2) verbatim:
  > "RQ2 paper exact 5-way: Bern→Prop -9.53% + Anti < Prop < Neyman paradox 발견 + σ_j range root cause"
- **정정 영역**: §4.2 + §5.3 영역에 selectivity-dependent 명시.
- **after wording snippet (v3 line 17 → v4 + §5.3 추가)**:
  > "§4.2 RQ2 paper exact 5-way: Bern→Prop −9.53% + Anti < Prop < Neyman paradox **sel=0.01 한정**, sel=0.1 = **Neyman best** (classical theory 정합). selectivity-dependent. σ_j range root cause = 본 데이터 조건 (분산 uniform) 한정 특수 케이스 (Neyman 가설 자체는 textbook 유효, Cochran 1977 §5.5 partial). §5.3 Limitation 14 (Neyman paradox 해석 정확성)."
- **cost**: §4.2 + §5.3 2 영역에 정확 명시. **30분**.

#### §2.3.5 룰 13 (RQ2 5-way 측정 = SF=100 한정) — A=high (§4.2 + §5.3 신규 L19)

- **현 outline v3 line 17** (§4 Results) verbatim — RQ2 측정 영역 = SF=100 (DEEP+SIFT) 한정 명시 부재.
- **after wording snippet (v3 line 17 → v4 + §5.3 L19 신규)**:
  > "§4.2 RQ2 측정 영역: **SF=100 (DEEP+SIFT) 한정**. SF=1 / SF=10 / SSN / 다중 테이블 = **미측정**. §5.3 신규 Limitation **L19 (RQ2 5-way SF=100 한정)**: Neyman paradox 일반화 가능성 (다른 SF / 데이터셋 / 다중 테이블) = 미검증, 5/15 박광현 미팅에서 자문 + 6/11 보고서 future work 영역."
- **cost**: §4.2 footnote + §5.3 신규 L19 추가. **20분**.

#### §2.3.6 룰 14 (Anti-Neyman > Neyman = 가설 자체 유효 but 데이터 조건 不만족) — A=high (§5.3 L15 정정)

- **현 outline v3 line 70** (§5.3 Limitation L15: RQ2 Neyman/Anti paradox 발견) verbatim:
  > "L15: RQ2 Neyman/Anti paradox 발견 (σ_j range 1.3-1.6× narrow + N_i CV=0)"
- **정정 영역**: L15 wording 의 정확 해석 명시 (Neyman 가설 유효, 데이터 조건 不만족).
- **after wording snippet (v3 line 70 → v4 정정)**:
  > "L15: RQ2 Neyman/Anti paradox 발견 정확 해석 (★ 정정 5/14 22:30, handoff v20 §4 룰 #14): **Neyman 가설 자체는 textbook 유효** (Cochran 1977 §5.5 partial). 본 데이터셋이 Neyman 의 **가정 조건 (cluster 간 분산 다양함) 不만족** (σ_j range 1.3-1.6× narrow + N_i CV=0 의 정량). **selectivity-dependent** (sel=0.01 paradox / sel=0.1 = Neyman best). σ_j 직접 측정 추가 검증 필요 (현재 oracle 가정)."
- **cost**: L15 1 paragraph 정정. **20분**.

#### 6/11 outline v2/v3 총 cost = **30+30+45+30+20+20 = 175분 ≈ 3시간**

→ P2 (5/27~6/10 sprint) 적용. 단 박세은 통합 owner, 박광현 미팅 후 5/16 outline v3 → v4 update 1 회 권장.

---

### 2.4 5/27 deck v4 (`/Users/hyunbin/Capstone/submission/_drafts/속도는벡터 · Capstone Final 5_27 (Keynote v4).{pdf,pptx,html}`, 20 slide)

**high-impact 12 영역** (룰 1-14 中 12 룰 영향, NEW 다수):

> **anchor**: 본 deck v4 는 5/12 23:07 export, 5/14 18:00 회의 + Form 1 fix 적용 X 영역 다수. v5 update 시 룰 1-14 모두 반영 필요.

#### §2.4.1 룰 1+2 (Eq 1 vs Eq 2-6 + 17-step) — NEW (slide 10-13)

- **현 slide 10-13 (RQ3 5단계 narrative)** verbatim 영역에 "5 단계 中 1 단계" 표기 가능성. v3 prompt 기반.
- **신규 작성 영역**: slide 10-13 의 RQ3 narrative 를 Eq 1 vs Eq 2-6 + 17-step 정확 wording 으로 정정. Form 1 anchor slide 11-12 신규.
- **cost**: 4 slide rewrite. **2시간**.

#### §2.4.2 룰 5+6 (L1/L2/L3 + ECQO anchor) — NEW (slide 4-5 anchor)

- **현 slide 4-5 (문제 정의 + 본 연구 anchor)**: paper §V "without index" anchor 명시 부재 가능성.
- **신규 작성 영역**: slide 5 ★★★ "paper §V 'without index' anchor (Form 1 의 존재 의의)" 신규 slide 추가. L1/L2/L3 framework slide 8 추가.
- **cost**: 2 slide 신규 + 2 slide rewrite. **2시간 30분**.

#### §2.4.3 룰 7 (RQ3 = batch baseline + Form 1 streaming axis) — NEW (slide 12, 17)

- **현 slide 12 (RQ3 결과)** + **slide 17 (limitation/future)**: batch baseline framing + Form 1 streaming axis 신규 영역 표기 부재.
- **신규 작성 영역**: slide 12 RQ3 = "사전 학습 batch baseline" framing 정정 + slide 17 Form 1 streaming axis future work 신규.
- **cost**: 2 slide rewrite. **1시간 30분**.

#### §2.4.4 룰 9+14 (Neyman paradox sel=0.01 한정 + 가설 정확 해석) — NEW (slide 8, 17)

- **현 slide 8 (RQ2 5-way 결과)** + **slide 17 (limitation)**: Neyman paradox 의 selectivity-dependent + 정확 해석 명시 부재.
- **신규 작성 영역**: slide 8 RQ2 narrative 정정 + slide 17 Limitation L15 추가.
- **cost**: 2 slide rewrite. **1시간 30분**.

#### §2.4.5 룰 8 + 10 + 11 + 12 + 13 (자원 효율 + K granularity + Neyman wording) — C=low (slide 14, 8, footnote)

- **현 slide 14 (자원 효율 Pareto)** + **slide 8 (Neyman 수치)**: footnote 추가 권장.
- **cost**: 5 footnote 추가. **30분**.

#### 5/27 deck v4 총 cost (v5 update) = **120+150+90+90+30 = 480분 ≈ 8시간**

→ P1 (5/16~5/26) 적용. 5/12 deck v4 → v5 (Form 1 + 룰 1-14 종합) update. 박세은 디자인 review 별도.

---

### 2.5 METHOD_REGISTRY (`/Users/hyunbin/Capstone/_internal/METHOD_REGISTRY.md`, 317 line)

**low-impact 6 영역** (룰 1 + 5 + 6 + 7 + 9 + 14 영향, 모두 C=low):

#### §2.5.1 룰 1 (Eq 1 vs Eq 2-6) — C=low

- **현 line 247-253** (§11 5/27 발표 narrative 강화 storyline 5단계 표) verbatim:
  > "1 단일 random sampling skew 무너짐 (RQ1) | RANDOM20 baseline + chao_weighted M1"
- **정정 영역**: line 247 storyline 5단계 narrative 표 에 "Eq 1 (Bernoulli) 대체 vs Eq 2-6 (유지)" footnote 추가.
- **cost**: 1 footnote. **5분**.

#### §2.5.2 룰 5+6+7 (L1/L2/L3 + ECQO anchor + batch + streaming) — C=low (§0 + §11)

- **현 line 10-24** (§0 TL;DR) + **line 244-254** (§11 storyline) verbatim 영역 — 모두 narrative anchor 정정 가능.
- **cost**: 2 footnote. **10분**.

#### §2.5.3 룰 9+14 (Neyman paradox 정확 해석) — C=low (§1.8 + §11)

- **현 line 43** (P1.8 kmeans_neyman M9: Cochran 1977 §5 + Neyman 1934) + **line 248** (storyline 2단계) verbatim.
- **정정 영역**: kmeans_neyman M9 method 의 "RQ2 plug-in" narrative 에 sel=0.01 한정 + 데이터 조건 footnote.
- **cost**: 2 footnote. **10분**.

#### METHOD_REGISTRY 총 cost = **5+10+10 = 25분 ≈ 0.5시간**

→ P0 (5/16 24:00 까지) 적용 가능. 영향 low, cost minimal.

---

### 2.6 EXPERIMENT_REGISTRY (`/Users/hyunbin/Capstone/_internal/EXPERIMENT_REGISTRY.md`, 248 line)

**low-impact 4 영역** (룰 1 + 7 + 9 + 11 영향, 모두 C=low):

#### §2.6.1 룰 1 + 7 (5 단계 narrative 정정) — C=low (§9 5단계 narrative)

- **현 line 231-240** (§9 5단계 narrative + handoff_main §6.2 + handoff_v4 §7) verbatim:
  > "| 1 | RQ1/RQ2/RQ3 검증 | RANDOM20 baseline + KM20 stratified | ✅ RQ1 5%, RQ2 9% 격차 |"
- **정정 영역**: §9 5단계 표 의 "Eq 1 vs Eq 2-6" 명시 + "RQ3 batch baseline + Form 1 streaming axis" framing 명시.
- **cost**: 1 footnote 또는 1 row 추가. **15분**.

#### §2.6.2 룰 9 + 11 (Neyman paradox sel=0.01 한정 + −10% narrative 정정) — C=low (§6.2)

- **현 line 174** (§6.2 5-way 확장: + Neyman + Anti-Neyman) verbatim:
  > "### 6.2 5-way 확장 (+ Neyman + Anti-Neyman) — 자동 chain 진행 中"
- **정정 영역**: §6.2 5-way 결과 narrative 에 sel=0.01 한정 + −10% wording 정정 footnote.
- **cost**: 1 footnote. **10분**.

#### EXPERIMENT_REGISTRY 총 cost = **15+10 = 25분 ≈ 0.5시간**

→ P0 (5/16 24:00 까지) 적용 가능. 영향 low, cost minimal.

---

## §3. 우선순위 (P0 / P1 / P2)

### 3.1 P0 (5/15 14:00 박광현 미팅 직후 ~ 5/16 24:00) — 룰 1-14 회의 PDF + narrative + Registry 일괄

**Scope**: 박광현 review 직후 즉시 정정 영역. 박세은 9 영역 + Agent A-J 10 종합 + 정정 룰 14 즉시 반영. 5/27 발표 + 6/11 보고서의 source.

| file | 룰 영역 | cost |
|---|---|---|
| 회의 PDF v2 md (1681 line) | 1-14 中 12 룰 | 8h |
| narrative v1 (196 line) | 1+2+5+6+7+8 | 2.5h |
| METHOD_REGISTRY (317 line) | 1+5+6+7+9+14 | 0.5h |
| EXPERIMENT_REGISTRY (248 line) | 1+7+9+11 | 0.5h |
| **P0 총 cost** | | **11.5h** |

→ 5/15 14:00 미팅 후 ~ 5/16 24:00 (≈ 30h 가용) 안에서 11.5h 작업. 분할 시 5/15 21:00 ~ 5/16 09:00 야간 / 5/16 12:00 ~ 18:00 주간 split 가능.

### 3.2 P1 (5/27 발표 전 = 5/16~5/26) — 5/27 deck v4 → v5 + 회의 PDF v2 후속 정리

**Scope**: 5/27 발표 자료 update. Form 1 + 룰 1-14 종합 + 박광현 추천 (5/15 미팅) 반영.

| file | 룰 영역 | cost |
|---|---|---|
| 5/27 deck v4 (20 slide) → v5 | 1+2+5+6+7+8+9+10+11+12+13+14 | 8h |
| 회의 PDF v2 후속 (룰 12 csv verify) | 12 | 1h |
| **P1 총 cost** | | **9h** |

→ 5/16 ~ 5/26 (≈ 10 day 가용) 안에서 9h 작업. 박세은 deck 디자인 review 별도 (~5h).

### 3.3 P2 (6/11 보고서 전 = 5/27~6/10) — 6/11 outline v3 → v4 + sprint W5~W6 본문

**Scope**: 6/11 최종 보고서 sprint. outline v4 + 4 팀원 분담 본문 작성.

| file | 룰 영역 | cost |
|---|---|---|
| 6/11 outline v3 (134 line) → v4 | 1+2+5+6+7+9+13+14 | 3h |
| 본문 sprint W5-W6 (40p 본문) | 1-14 모두 | 25h (4 팀원 분담) |
| Form 1 측정 결과 통합 (post-5/27) | post-측정 | 별도 |
| **P2 총 cost** | | **28h** |

→ 5/27 ~ 6/10 (≈ 14 day) 안에서 28h 작업. 4 팀원 분담 (박세은 통합 7h / 조현빈 §3+§4.1+§4.5 8h / 이동욱 §2+§4.2 6h / 강재현 §4.3+§4.4 7h).

---

## §4. 적용 cost 추정 (분 단위 정확)

### 4.1 P0 cost 분해 (회의 PDF v2 한 file 만 = 11.5h 中 8h)

| 영역 | line range | 룰 | cost |
|---|---|---|---|
| §2.1.1 Eq 1 vs Eq 2-6 신규 sub | §2.4 line 304-329 후 신규 | 1 | 30분 |
| §2.1.2 17-step pseudo-code 신규 | §2.4.1 후 신규 | 2 | 20분 |
| §2.1.3 single-table 보강 | line 642-652 | 3 | 15분 |
| §2.1.4 block + row hybrid | line 275 + footnote | 4 | 15분 |
| §2.1.5 L1/L2/L3 정정 | line 902-913 + 박세은 verbatim | 5 | 30분 |
| §2.1.6 ★★★ ECQO anchor 신규 | §1 또는 §4.2 신규 | 6 | 45분 |
| §2.1.7 RQ3 batch + Form 1 streaming | line 540-557 + 880-928 | 7 | 40분 |
| §2.1.8 fit time SF=1 footnote | line 466-484 + 1525-1599 | 8 | 30분 |
| §2.1.9 Neyman selectivity-dependent | §3.2 + §6 신규 sub | 9 | 45분 |
| §2.1.10 K granularity SF=1 측정 추가 | line 304-327 | 10 | 30분 |
| §2.1.11 −10% wording 정정 | line 383-395 + 520-535 | 11 | 40분 |
| §2.1.12 §3.2 csv verify | line 528-535 (★ csv 직접 작업) | 12 | 60분 |
| §2.1.13 RQ2 SF=100 한정 | §3.2 + §6 + §7 footnote | 13 | 45분 |
| §2.1.14 Anti-Neyman 정확 해석 | §3.2 + §6 + §7 정정 | 14 | 30분 |
| **회의 PDF v2 총** | | | **475분 (≈ 8h)** |

### 4.2 P1 cost 분해 (5/27 deck v4 → v5 = 8h)

| slide | 룰 | cost |
|---|---|---|
| slide 4-5 ECQO anchor + L1/L2/L3 신규 | 5+6 | 150분 |
| slide 8 RQ2 Neyman 정정 | 9+11+14 | 90분 |
| slide 10-13 RQ3 narrative (Form 1) | 1+2+7 | 120분 |
| slide 14 자원 효율 footnote | 8 | 30분 |
| slide 17 Limitation L15 + L19 | 13+14 | 90분 |
| **deck v5 총** | | **480분 (≈ 8h)** |

### 4.3 P2 cost 분해 (6/11 outline + sprint = 28h)

| 영역 | 담당 | cost |
|---|---|---|
| outline v3 → v4 update | 본인 (조현빈) | 3h |
| §1 Introduction (3-4p) | 박세은 | 4h |
| §2 Background (3-4p) | 이동욱 | 4h |
| §3 Methodology (5-6p, paper §V-B Eq 1-6 + 17-step) | 조현빈 | 6h |
| §4 Results (12-14p) — RQ1/RQ2/RQ3/Form 1 | 조현빈 (4.1+4.5) + 이동욱 (4.2) + 강재현 (4.3+4.4) | 12h |
| §5 Discussion (4-5p, L14-L19 추가) | 박세은 | 5h |
| §6 Conclusion + Future Work (1-2p, Form 1 streaming axis) | 박세은 | 2h |
| §7 References (2-3p) | 박세은 | 2h |
| §8 Appendix (4-6p) | 조현빈 | 4h |
| **sprint 총** | | **42h (4 팀원 분담)** |

> 단 P2 cost 는 본 mass update 외 본문 작성까지 포함. mass update 만 한 경우 ~5h.

---

## §5. 실행 plan (mass update 순서 + commit 단위 5-10 commit 분할 권장)

### 5.1 의존성 graph (왼쪽 정정이 오른쪽의 source)

```
P0:
[METHOD_REGISTRY (5분)] → [EXPERIMENT_REGISTRY (15분)] → [회의 PDF v2 (8h)] → [narrative v1 (2.5h)]
                                                            ↓
                                                       [Agent A-J 참조 only]

P1:
[회의 PDF v2 정정 완료] → [5/27 deck v4 → v5 (8h)] → [회의 PDF v2 후속 (csv verify 1h)]
                              ↓
                         [Form 1 측정 결과 (post-5/27)]

P2:
[회의 PDF v2 + narrative v1 정정 완료] → [6/11 outline v3 → v4 (3h)] → [4 팀원 sprint W5-W6 (25h)]
```

### 5.2 commit 단위 5 commit 분할 권장 (mass commit 회피)

#### C1 (5/16 09:00, ~0.5h): Registry 정정 (가장 lightweight, 다른 file 의 source)

```bash
# scope: METHOD_REGISTRY + EXPERIMENT_REGISTRY 일괄 정정 (룰 1+5+6+7+9+11+14)
# cost: 25분 + 25분 = 50분
git add _internal/METHOD_REGISTRY.md _internal/EXPERIMENT_REGISTRY.md
git commit -m "$(cat <<'EOF'
Registry 정정 룰 1+5+6+7+9+11+14 footnote 추가 (handoff v20 §4)

- METHOD_REGISTRY: 5단계 storyline 표 (line 247-253) + kmeans_neyman M9 (line 43) Neyman sel=0.01 한정 + Eq 1 vs Eq 2-6 footnote
- EXPERIMENT_REGISTRY: §9 5단계 narrative (line 231-240) + §6.2 5-way (line 174) selectivity-dependent + −10% 정정 footnote

handoff v20 §4 정정 룰 14 list 中 6 룰의 Registry 영역 일괄 적용.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

#### C2 (5/16 10:00 ~ 5/16 18:00, ~8h): 회의 PDF v2 md 정정 룰 1-14

```bash
# scope: 회의 PDF v2 md 1681 line 일괄 정정 (모든 14 룰)
# cost: 475분 ≈ 8h
git add "submission/_drafts/archive/속도는벡터 - 프로젝트 정리 (저녁 긴급 회의 숙지용).md"
git commit -m "$(cat <<'EOF'
회의 PDF v2 정정 룰 1-14 일괄 적용 (handoff v20 §4)

- §1 paper §V "without index" anchor (★★★ 룰 6) 신규 sub
- §2.4 Eq 1 vs Eq 2-6 + 17-step pseudo-code 신규 (룰 1+2)
- §2.5 K granularity SF=1+10+100 × K=10/20/30 측정 완료 wording (룰 10)
- §3.2 RQ2 SF=100 한정 + Neyman selectivity-dependent + −10% wording 정정 (룰 9+11+12+13)
- §3.5 fit time SF=1 한정 footnote (룰 8)
- §4.1.4 RQ3 batch baseline + Form 1 streaming axis (룰 7)
- §4.2 Q6 single-table 공개 코드 한계 + block + row hybrid (룰 3+4)
- §5.1-§5.3 L1/L2/L3 layer 박세은 9:09 verbatim (룰 5)
- §6 Neyman paradox 정확 해석 + Cochran 1977 §5.5 (룰 14)
- §7 환각 disclosure 신규: SF=100 한정 + Neyman 일반화 미검증 (룰 13)

총 14 룰 中 12 룰 영향. cost 8h.
박세은 9 영역 카톡 verbatim + Agent A-J 10 종합 + 박광현 5/15 미팅 review 반영.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

#### C3 (5/16 19:00 ~ 5/16 22:00, ~3h): narrative v1 정정 + PDF 재생성

```bash
# scope: narrative v1 196 line + PDF 재생성
# cost: 160분 + 30분 (PDF) ≈ 3h
python3 _internal/scripts/md2pdf.py "submission/_drafts/archive/속도는벡터_본연구_narrative_최종정리_v1.md"
git add "submission/_drafts/archive/속도는벡터_본연구_narrative_최종정리_v1.md" "submission/_drafts/archive/속도는벡터_본연구_narrative_최종정리_v1.pdf"
git commit -m "$(cat <<'EOF'
narrative v1 정정 룰 1+2+5+6+7+8 + PDF 재생성 (handoff v20 §4)

- §1 출발점: paper §V "without index" anchor 명시 (★★★ 룰 6) + L1/L2/L3 framework (룰 5)
- §4 단독 대체: Eq 1 vs Eq 2-6 + 17-step footnote (룰 1+2) + batch baseline framing (룰 7)
- §11 method 깊이: fit time SF=1 한정 footnote (룰 8)

총 6 룰 영향. cost 2.5h + PDF 0.5h.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

#### C4 (5/16 22:00 ~ 5/17 01:00, ~3h): 6/11 outline v3 → v4 + PDF 재생성

```bash
# scope: 6/11 outline v3 134 line → v4 (룰 1+2+5+6+7+9+13+14)
# cost: 175분 + 30분 (PDF) ≈ 3h
git add plans/6_11_보고서_outline_v4_post_5월15일미팅_*.md plans/최종보고서_outline_v3_*.md
git commit -m "$(cat <<'EOF'
6/11 outline v3 → v4 정정 룰 1+2+5+6+7+9+13+14 (handoff v20 §4)

- §1.2 문제 정의: paper §V "without index" anchor + L1/L2/L3 (룰 5+6)
- §1.3 RQ 재정의: RQ3 batch baseline + Form 1 streaming axis (룰 7)
- §3.3 Methodology: paper §V-B Eq 1-6 verbatim + 17-step pseudo-code (룰 1+2)
- §4.2 Results RQ2: SF=100 한정 + Neyman selectivity-dependent (룰 9+13)
- §5.3 Limitation L15 정확 해석 + L19 신규 (룰 14+13)
- §6.2 Future Work: Form 1 streaming axis post-6/11 측정 (룰 7)

박광현 5/15 미팅 review 반영. 4 팀원 sprint W5-W6 (5/29~6/10) base.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

#### C5 (5/17 ~ 5/26, ~8h spread): 5/27 deck v4 → v5 신규 작성

```bash
# scope: 5/27 deck v4 20 slide → v5 (Form 1 + 룰 1-14)
# cost: 480분 ≈ 8h (10일 spread)
# 박세은 디자인 review 별도 (~5h)
git add "submission/_drafts/속도는벡터 · Capstone Final 5_27 (Keynote v5).{pdf,pptx,html}"
git commit -m "$(cat <<'EOF'
5/27 deck v4 → v5: Form 1 + 정정 룰 1-14 일괄 반영 (post-5/15 박광현 미팅)

신규 slide 영역:
- slide 5 ★★★ paper §V "without index" anchor (룰 6)
- slide 8 RQ2 selectivity-dependent + Neyman 가설 정확 해석 (룰 9+14)
- slide 10-13 Form 1 Component A+B+C+D + 17-step pseudo-code (룰 1+2)
- slide 17 Limitation L15 + L19 + Form 1 future work (룰 13+14+7)

footnote 추가:
- slide 8 RQ2 SF=100 한정 (룰 13)
- slide 14 fit time SF=1 한정 (룰 8)
- slide 14 K granularity SF=1+10+100 × K=10/20/30 (룰 10)

박세은 디자인 review 별도 진행.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

### 5.3 commit 분할 정책 (cherry-picking 회피)

- **각 commit = 하나의 file scope** (회의 PDF / narrative / outline / deck / Registry).
- **각 commit 안에서 모든 영향 룰 일괄 적용** (cherry-picking X). 회의 PDF v2 commit 안에서 룰 1+2+3+4+5+6+7+8+9+10+11+12+13+14 모두 반영.
- **수정 단위 ≠ 룰 단위** (룰별 분할 commit X). 한 룰이 여러 file 영향 시, 각 file commit 안에서 그 룰 영역 일괄 적용.
- **commit 메시지 = 영향 룰 list + cost + 영역 (file + line)** 명시. 추후 rollback / review 시 traceability 확보.

### 5.4 실행 timeline (5/15 14:00 ~ 5/26 24:00, 11 day)

```
5/15 14:00 박광현 D-1 미팅 (review form PDF v2 활용)
5/15 16:00 ~ 21:00 박광현 추천 정리 + Form 1 변경 가능 영역 확정
5/16 09:00 C1 Registry 정정 (0.5h)
5/16 10:00 ~ 18:00 C2 회의 PDF v2 정정 (8h)
5/16 19:00 ~ 22:00 C3 narrative v1 정정 + PDF (3h)
5/16 22:00 ~ 5/17 01:00 C4 6/11 outline v4 + PDF (3h)
5/17 ~ 5/26 (10 day spread, ~1h/day) C5 5/27 deck v5 (8h)
5/27 발표 (D-13)

→ P0 (5/16) + P1 (5/17~5/26) 일괄 적용. P2 (5/27~6/10 sprint) 별도.
```

---

## §6. 의존성 graph (정정 source 흐름)

```
[5/15 14:00 박광현 미팅]
        ↓ (박광현 review 결과 + Form 1 변경 가능 영역 확정)
        ↓
[handoff v20 §4 정정 룰 14 list (5/14 22:15 ★ source)]
        ↓
[METHOD_REGISTRY (C1) ← lightweight anchor]
        ↓
[EXPERIMENT_REGISTRY (C1)]
        ↓
[회의 PDF v2 md (C2) ← P0 main, 8h, 14 룰 中 12 룰 일괄 정정]
        ↓
        ├──→ [narrative v1 (C3) ← 회의 PDF v2 정정 → narrative 자연 alignment, 6 룰 영향]
        │
        └──→ [6/11 outline v3 → v4 (C4) ← 회의 PDF v2 정정 → outline source 자연 alignment, 8 룰 영향]
                ↓
                [4 팀원 sprint W5-W6 본문 (P2, 5/27~6/10) ← outline v4 source]
        
[회의 PDF v2 정정 완료] ──→ [5/27 deck v4 → v5 (C5) ← P1, 8h spread, 12 룰 영향 + Form 1 종합]
        
[Agent A-J 10 file (참조 only, edit X)]
        ↓
        ├──→ Agent F+G 17-step pseudo-code (룰 2 source)
        ├──→ Agent J 박세은 9 영역 답변 form (룰 6 source ★★★)
        ├──→ Agent B 정정 7 영역 (룰 1 source)
        └──→ Agent E Form 1 8 영역 (룰 1+2+7 source)
```

### 의존성 핵심 관찰

1. **회의 PDF v2 가 P0 main source** (8h 정정). 정정 후 narrative v1 + 6/11 outline + 5/27 deck 모두 source alignment.
2. **Registry (METHOD + EXPERIMENT) 는 lightweight anchor**. C1 이 다른 commit 의 reference (METHOD_REGISTRY 의 정정 wording 이 회의 PDF v2 의 narrative 내 참조). 가장 먼저 적용.
3. **narrative v1 + 6/11 outline 은 회의 PDF v2 의 derivative** (C3+C4 가 C2 의 source 활용). 5/16 야간 (C3) + 5/16 자정 (C4) 작업 권장.
4. **5/27 deck v4 → v5 는 P1 spread** (5/17~5/26, ~1h/day). Form 1 종합 + 박세은 디자인 review 별도.
5. **6/11 outline v4 의 4 팀원 sprint (P2) 는 별도 영역** (5/27~6/10). mass update 직접 영향 X, 본문 작성 sprint 의 source 만 제공.

---

## §7. 박광현 5/15 미팅 직후 즉시 적용 영역 (최우선 5 영역)

P0 中 가장 시급한 5 영역 (5/15 14:00 미팅 직후 ~ 5/16 09:00 작업):

1. **룰 6 ★★★ paper §V "without index" anchor** (회의 PDF v2 + narrative v1, ~1.5h)
2. **룰 12 csv 직접 verify** (회의 PDF v2 §3.2 line 528-535 csv aggregate, ~1h)
3. **룰 9+14 Neyman paradox 정확 해석** (회의 PDF v2 §3.2 + §6, ~1.25h)
4. **룰 10 K granularity SF=1+10+100 측정 완료 wording** (회의 PDF v2 §2.5, ~0.5h)
5. **룰 13 RQ2 SF=100 한정 + 환각 disclosure** (회의 PDF v2 §3.2 + §7, ~0.75h)

**최우선 5 영역 총 cost ≈ 5h** (5/15 19:00 ~ 5/16 02:00 한 세션 가능).

→ 이 5 영역만 5/16 09:00 까지 완료 후 본 commit 1 회 (즉시 박세은/팀원 공유 가능).

---

## §8. 정직 disclosure (본 mapping 의 한계)

1. **5/27 deck v4 실제 내용 미확인** — 본 mapping 은 handoff v20 §15 + 파일명 + 5/27 storyline v2 base 추정. 실제 deck 의 slide-by-slide 영역은 5/16 작업 시점 직접 확인 권장.
2. **회의 PDF v2 csv source 직접 verify 미완** — 룰 12 (§3.2 line 532-533) 의 csv aggregate 직접 확인이 mass update 의 prerequisite. C2 (회의 PDF v2 정정) 시작 전 별도 작업.
3. **6/11 outline v4 는 P2 sprint W5-W6 의 4 팀원 분담 작업** — 본 mapping 의 outline 영역 cost (3h) 는 단독 update 한정. 본문 작성 (25h) 은 별도.
4. **Form 1 측정 결과 통합** = post-5/27 영역. mass update 직접 영향 X. P1 (5/27 deck v5) 는 Form 1 plan 만 명시, 측정 결과 X.
5. **박광현 review 결과 미확인** — 5/15 14:00 미팅 직후 박광현 추천 사항이 본 mapping 의 cost / 영역 / 우선순위 변경 가능. 미팅 직후 본 mapping 재검토 권장.

---

## §9. END

작성: 2026-05-14 22:30 KST  
source: handoff v20 §4 정정 룰 14 list + §15 영향 file 후보  
total cost 추정 = P0 11.5h + P1 9h + P2 28h = **48.5h** (5/15 ~ 6/10 spread)  
commit 분할 = **5 commit** (C1 Registry / C2 회의 PDF / C3 narrative / C4 outline / C5 deck v5)  
의존성 = Registry → 회의 PDF → narrative + outline → deck 순서  

박광현 5/15 미팅 직후 P0 최우선 5 영역 (룰 6+12+9+14+10+13, ~5h) 즉시 적용 권장. P0 잔여 6.5h 는 5/16 야간/주간 split.

**핵심 원칙** (사용자 정책 verbatim):
- cherry-picking 회피: 한 commit 안에서 모든 영향 룰 일괄 적용
- mass commit 회피: 5 commit 으로 file scope 단위 분할
- 정직 disclosure: 본 mapping 의 한계 5 영역 §8 명시
- 학부생 톤 / 한국어 / peer-to-peer
- 일정/자원 무관 (사용자 5/14 21:00 명시) — cost 추정은 참고용 reference, 실제 진행 시 박광현 review 결과에 따라 조정
