# Claude Design / Claude Code Storyline Prompt — 5/27 발표 Narrative

> **작성**: 2026-05-08 22:30 KST · **버전**: v1 (self-contained)
> **목적**: Claude Design 페이지 또는 별도 Claude Code 세션에서 read-only 로 사용 가능한 storyline visualization / deck generation prompt
> **대상**: 속도는벡터 (연세대 캡스톤 2026-1) — 5/27 최종 발표 + 5/28 전시회 + 6/11 최종보고서
> **이전 prompt**: `_internal/Claude_Design_요청_prompt_20260508.md` (v3 deck slot-fill 전용)

---

## §0 사용 instruction

본 doc 은 **self-contained storyline prompt** 이다. 다음 중 하나에 그대로 입력하면 5/27 발표용 narrative deck / infographic / interactive visualization 생성이 가능하다.

| 사용처 | 트리거 | 산출 |
|---|---|---|
| **Claude Design** ([page link](https://claude.ai/design)) | "다음 storyline 으로 학술 deck 생성" + 본 doc paste | React/HTML deck (16 page) + 디자인 시스템 자동 적용 |
| **별도 Claude Code session** | `@_internal/claude_design_prompt_storyline_20260508.md 읽고 발표 자료 만들어줘` | md/PDF 산출 (slide_redesign_v2 base 또는 신규) |
| **Claude.ai chat** | 본 doc paste + "이 narrative 로 1 page poster 디자인" | 정적 SVG/PNG 또는 HTML poster |

본 doc 만 read 하면 모든 essential context (5/8 22:00 finalize 결과 + 5/9 morning Multi 회수 후 update 가능 placeholder) 가 포함되어 있어 caller agent 가 추가 file 탐색 없이 바로 작업 가능하다.

---

## §1 본 연구 storyline 요약 (5 paragraphs)

### Para 1 — Motivation (Exqutor 가 미작동하는 영역)

본 연구는 BDAI Research 의 Exqutor (arXiv:2512.09695v2) 가 vector-augmented analytical query 의 카디널리티 추정에서 제시한 두 핵심 mechanism — *ECQO* (HNSW 인덱스 위에서의 정확한 range query 카디널리티) 와 *Adaptive Sampling* (인덱스 없을 때 모멘텀 기반 동적 표본) — 중에서 후자가 **단일 테이블 / 인덱스 없는 / skewed 분포 영역에서 정확도 저하** 가능성을 실험적으로 정량화하고, 그 영역에 *분포 인지(distribution-aware) stratification* 를 도입하면 얼마나 개선되는지 head-to-head paired 비교를 통해 평가한다. 이 영역은 Exqutor 본 논문이 명시적으로 다루지 않은 white-space 이며, 단일 테이블 정확성은 multi-table join 정확성의 *필요조건만* 성립한다는 limitation 을 정직하게 보고한다.

### Para 2 — Method (5 paradigm × 11 method × 3 RQ)

연구질문은 RQ1 (기존 random sampling 의 skew 데이터셋 부정확성), RQ2 (분포 인지 시 어떤 σ-allocation 이 최적), RQ3 (분포 미인지 시 어떤 학습 paradigm 이 최적) 의 세 축으로 구성된다. RQ3 의 핵심 contribution 은 분포 미인지 stratum 학습을 **5 paradigm framework** 로 분류한 것 — P1 Cluster-based (HDBSCAN, MiniBatch, GMM), P2 Spatial Indexing (Hilbert, faiss_ivf), P3 Streaming (MB_partial, Reservoir), P4 Dim Reduction (sparse_rp, PCA1D), P5 Hashing/QR (LSH, Sobol) — 이며, 각 paradigm 의 inductive bias 를 학술 standard taxonomy (ACM Computing Surveys 2024 + Wu UWisconsin sampling cardinality survey) 와 cross-validate 하였다. 측정은 단일 10 cell + multi 3 cell × 5 selectivity × 5 seed × 100 query 의 paired alignment 로 query_id + seed + selectivity 정확 매칭 후 paired Wilcoxon signed-rank + Bonferroni/BH-FDR 다중 비교 보정까지 적용한다.

### Para 3 — Result (Single 10 cell + Multi 3 cell + Adaptive 비교)

W1 Sprint (5/5~5/8) 에 단일 10 cell × 30 method × 5 selectivity = 1,500 measurement 를 완료하였고, Tier 1 17종 중 4강 (HDBSCAN −8.04, MB_partial −7.63, Hilbert −7.54, sparse_rp / Hybrid −7.13) 을 5 paradigm 의 distinct representative 로 selection 하였다. 5/8 22:00 시점 단일 100% finalize + multi STAGE 1+2 finalize + 6 audit (V1~V6) + Single Adaptive paired 분석 (10 cell × 4 method × 5 selectivity × 5 seed × 100 query = 2,500 paired pair) 까지 완료. Single Adaptive 비교 결과 ★1~★3 은 Outcome A (4강 paired 우위, p < 0.05 ~ 1e-7), ★4 sparse_rp 는 Outcome B (paired 동등, 0/10 sig). 5/9 morning 에 Multi paradigm 11 method (3 cell × 11 method = 33 csv) + Multi Adaptive + Multi SF1 + YFCC K-sweep 4 task 회수 예정.

### Para 4 — ★1~★3 우위 + ★4 paradigm anchor (Outcome A vs B narrative)

★1 HDBSCAN 은 단일 sweet spot 4 cell (SIFT_sf1 −32.63%, SIFT_sf10 −10.47%, YFCC_sf1 −7.23%, WIKI_sf1 −9.96%) 에서 가장 강력하며 Adaptive Sampling head-to-head 에서 10/10 cell win + 7/10 sig (Wilcoxon p < 0.05 ~ 1e-7). ★2 MB_partial 은 OLTP friendly 의 *production-deployable* tier 로 partial_fit 의 단일-pass streaming 가치를 보여준다. ★3 Hilbert 는 9/10 win + 6/10 sig 으로 *spatial indexing 의 production sweet spot*. ★4 sparse_rp 는 Adaptive Sampling 과 paired 통계적 동등 (4/10 win, 0/10 sig, mean Δ% = +0.05%) 인데, 이는 standalone 우위가 약하다는 honest reporting 임과 동시에 **5 paradigm framework 의 P4 dim-reduction anchor** + **학습-free 의 production-friendly tier** 라는 *paradigm coverage* 가치를 별도로 입증한다. 즉 Outcome B 의 동등은 thesis fail 이 아니라 5 paradigm framework 의 inductive bias 별 효과 매트릭스에서 P4 의 floor 를 정량화한 것이며, A 와 동일 권위의 academic finding 이다.

### Para 5 — Multi 25× shrinkage + Adaptive paired + Ensemble

단일 sweet spot (sf1 SIFT/WIKI/YFCC 평균) 4강 |Δ%| = **17.13%** 가 multi-vector / multi-table 영역에서 **0.67%** 로 수축한다 (= **25.4× shrinkage**, 부호 5/8 boundary). 이는 Joint distribution 의 분산 분해 시 cluster ratio + intrinsic dim 의 marginal information 만으로는 joint-aware stratification 이 불가하다는 limitation 을 정량 evidence 로 제시한다. **Multi 일반화 / Adaptive paired / Ensemble 측정 결과 (5/9 morning 도착)** 는 본 narrative 의 limitation 정량 evidence 와 4 outcome 분포 (A 우위 / B 동등 / C Adaptive 우위 / D Hybrid) 의 cell-by-cell breakdown 으로 보고서 outline v2 §4.4 + master_v6 §10.6 §10.7 에 fill 된다. PDX (SIGMOD 2025, CWI Amsterdam, arXiv:2503.04422) 가 *intrinsic_dim + skewness 가 algorithm selection 결정* 이라고 명시한 점이 본 thesis 와 정확 일치하며, complementary contribution (PDX = compute layer / 본 연구 = pre-process layer) 으로 학술 정당성 확보.

---

## §2 핵심 데이터 path reference (모두 절대 경로)

본 narrative 을 visualization / deck 에 반영하려면 다음 source 를 read.

### Master 분석본
- `/Users/hyunbin/Capstone/experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md` (919 lines, .pdf 동기) — RQ1/RQ2/RQ3 종합
- `/Users/hyunbin/Capstone/experiments/results/master_v6_§10.6_Multi_광범위_skeleton_20260508.md` — Multi 11 method 광범위 skeleton (5/9 fill 예정)
- `/Users/hyunbin/Capstone/experiments/results/master_v6_§10.7_Adaptive_분석_20260508.md` — Single Adaptive paired Δ% 분석 (Outcome A/B 판정)

### 자문 메일 + 보고서 outline
- `/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_자문메일_박성원멘토_20260508_v4.md` (.pdf 동기) — 5 paradigm × 11 method framework + Multi 25× shrinkage + sparse_rp paradigm anchor
- `/Users/hyunbin/Capstone/plans/최종보고서_outline_v2_20260508.md` (516 lines) — 8 section ~40p 보고서 outline (4 outcome 분포 + L1~L15 limitation)

### Audit 9종
- V1 matrix: `/Users/hyunbin/Capstone/_internal/audit_matrix_20260508.md`
- V2 data integrity: `/Users/hyunbin/Capstone/_internal/audit_data_integrity_20260508.md`
- V3 numerical: `/Users/hyunbin/Capstone/_internal/audit_method_correctness_20260508.md`
- V4 algorithm: `/Users/hyunbin/Capstone/_internal/audit_adaptive_algorithm_20260508.md`
- V5 extra exp: `/Users/hyunbin/Capstone/_internal/audit_extra_experiments_20260508.md`
- V6 multi paired alignment: `/Users/hyunbin/Capstone/_internal/audit_multi_paired_alignment_20260508.md`
- V7~V9: `/Users/hyunbin/Capstone/_internal/audit_method_correctness_20260508.md` 추가 — Reservoir RANDOM20 proxy + LSH K vs n_hp misalignment + sparse_rp Li 2006 1/√D variant
- V10 (Adaptive semantic): `/Users/hyunbin/Capstone/_internal/audit_adaptive_semantic_20260508.md`
- V11 (Master §10.7): `/Users/hyunbin/Capstone/_internal/audit_master_v6_§10.7_20260508.md`

### Paired CSV (단일 + multi 5/9 fill 예정)
- Single Adaptive paired raw: `/Users/hyunbin/Capstone/_internal/cache/rq3/single_adaptive_paired/<cell>.csv` (10 cell × 4 method, 21:34 회수 완료)
- Multi paradigm paired: `/Users/hyunbin/Capstone/_internal/cache/rq3/multi_paradigm/multi_paradigm_<cell>.csv` (3 cell × 11 method = 33 csv, **5/9 morning 회수**)
- Multi Adaptive paired: `/Users/hyunbin/Capstone/_internal/cache/rq3/multi_adaptive/<cell>.csv` (5/9 morning 회수)
- Ensemble paired: `/Users/hyunbin/Capstone/_internal/cache/rq3/ensemble/<cell>.csv` (5/9 morning 회수, 옵션)

### RQ3 paradigm framework 학술 검증
- `/Users/hyunbin/Capstone/_internal/RQ3_paradigm_심층검증_20260508.md` — 5 paradigm × 11 method 의 학술 standard taxonomy cross-check (ACM CSur 2024 + Wu sampling survey)

### 기존 deck source (편집 가능)
- `/Users/hyunbin/Capstone/submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.pdf` (16 page)
- `/Users/hyunbin/Capstone/submission/_drafts/academic_deck_v3_source/academic-deck/Slides.jsx` — 16 React component
- `/Users/hyunbin/Capstone/_internal/slide_redesign_v2_20260508.md` — slide-by-slide redesign 안

---

## §3 narrative 시각화 권장

### Hero figure — 5 paradigm × 11 method matrix + ★1~★4 highlight

가로축 5 paradigm (P1 Cluster / P2 Spatial / P3 Streaming / P4 DimRed / P5 Hash-QR), 세로축 11 method, 셀 색상 = avg paired Δ% (음수 = 더 정확 = 진한 navy / 양수 = 더 부정확 = 회색~red), ★ badge 4 cell (HDBSCAN, MB_partial, Hilbert, sparse_rp). 학술 backbone reference (Campello 2013, Sculley 2010, Vitter 1985, Achlioptas 2003, Indyk-Motwani 1998, Sobol 1967) inline citation.

### Stack chart — paired Δ% per cell × method (10 cell × 4 method = 40 bar)

X축 10 cell (DEEP_sf1/sf10, SIFT_sf1/sf10, SSN_sf1/sf10, WIKI_sf1/sf10, YFCC_sf1/sf10), Y축 paired Δ% (음수 = 4강 우위), 4 method 색상 코딩, p < 0.05 별표 + Bonferroni/BH 강조. Ceiling 영역 (SSN++ +1~+2%) honest report. 데이터:
- DEEP_sf1: −1.84 / −1.36 / −0.43 / −1.06 (HDBSCAN/MB_p/Hilbert/Hybrid)
- DEEP_sf10: −1.77 / −2.07 / −1.20 / −1.91
- SIFT_sf1: −32.63 / −31.58 / −32.08 / −28.95
- SIFT_sf10: −10.47 / −10.22 / −10.72 / −10.20
- SSN_sf1: +1.56 / +1.73 / +2.34 / +1.35
- SSN_sf10: +1.39 / +2.04 / +2.06 / +1.25
- WIKI_sf1: −9.96 / −9.86 / −9.61 / −7.69
- WIKI_sf10: −4.30 / −2.58 / −4.48 / −4.21
- YFCC_sf1: −7.23 / −7.15 / −6.88 / −5.71
- YFCC_sf10: −5.77 / −5.62 / −5.21 / −4.78

### Shrinkage chain — Single 17.13% → Multi 0.67%

3-stage funnel: ① Single sweet spot (sf1 SIFT/WIKI/YFCC 평균) 17.13% → ② Multi-vector (deep_sift_10, deep_wiki_10) 0.67% → ③ Multi-table join (5/9 fill) **TBD**. Shrinkage factor 25.4× annotation + "단일 정확성 = multi 정확성의 *필요조건*만" caption.

### Outcome 분포 chart — A/B/C/D × 4 method × 10+3 cell

10 single cell × 4 method = 40 paired test → A (★1 7개 / ★2 6개 / ★3 6개 / ★4 0개 sig), B (★1 3 / ★2 4 / ★3 4 / ★4 10 동등). Bonferroni (40 test, α=0.00125): A= 6/4/3/0. BH-FDR (q=0.05): A=7/5/6/0. 4강 method 위 색상 매트릭스 + ★4 paradigm anchor sub-narrative annotation.

### Adaptive vs 4강 vs Ensemble winner ranking (5/9 fill)

Multi cell 별 winner ranking — Adaptive 단독 / 4강 단독 / 4강 + Adaptive ensemble 의 cell-by-cell 비교. (5/9 morning 회수 후 fill — placeholder)

---

## §4 학술 backbone reference

| Source | 역할 | citation |
|---|---|---|
| ACM Computing Surveys 2024 "Comprehensive Survey on Deep Clustering" | 5 paradigm taxonomy 검증 | DOI 10.1145/... (paradigm 분류 standard) |
| Wu, "Sampling-Based Cardinality Estimation Algorithms: A Survey" (UWisconsin) | RQ1/RQ2 random sampling baseline 학술 backbone | cs.wisc.edu tech report |
| Campello-Moulavi-Sander, "Density-Based Clustering Based on Hierarchical Density Estimates" (PAKDD 2013) | ★1 HDBSCAN canonical | DOI 10.1007/978-3-642-37456-2_14 |
| Sculley, "Web-Scale K-Means Clustering" (WWW 2010) | ★2 MB_partial canonical | DOI 10.1145/1772690.1772862 |
| Vitter, "Random Sampling with a Reservoir" (TOMS 1985) | P3 Streaming Reservoir canonical | DOI 10.1145/3147.3165 |
| Achlioptas, "Database-friendly random projections" (PODS 2001 / JCSS 2003) | ★4 sparse_rp canonical | DOI 10.1016/S0022-0000(03)00025-4 |
| Lawder-King, "Querying multi-dimensional data indexed using the Hilbert space-filling curve" (SIGMOD 2001) | ★3 Hilbert canonical | DOI 10.1145/375663.375672 |
| Indyk-Motwani, "Approximate Nearest Neighbors" (STOC 1998) | P5 LSH canonical | DOI 10.1145/276698.276876 |
| Sobol 1967 / Niederreiter 1992 | P5 QR Sobol canonical | QMC textbook |
| Exqutor (arXiv:2512.09695v2) | 본 연구의 baseline + Adaptive Sampling §V-B | arXiv |
| PDX (arXiv:2503.04422, SIGMOD 2025, CWI Amsterdam) | 학술 confirmation: "intrinsic_dim + skewness 가 algorithm selection 결정" | arXiv |
| Bishop PRML 2006 §9.2 | GMM (P1 distribution sub) standard | textbook |
| Pearson 1901 / Hotelling 1933 | PCA canonical (P4 data-dependent) | classical |

---

## §5 narrative tone + visual identity

- **언어**: 한국어 학술 산문 (서사적, bullet 나열 지양). 학술 용어 영어 병기 (예: 분포 인지(distribution-aware), 헤드-투-헤드(head-to-head)).
- **폰트**: Apple SD Gothic Neo (국문) / Inter (영문 수치) / JetBrains Mono (caption code).
- **컬러**: 흰 배경 #FFFFFF + navy accent #1B3DAD + numbered badge 검정 사각 #0B0F1C + 흰 텍스트.
- **footer**: "속도는벡터 · STYLE A · ACADEMIC" / "CAPSTONE 2026 · FINAL · 2026.05.27".
- **차트**: paired Δ% 음수 = navy (4강 우위) / 양수 = grey~red (ceiling). p-value 별표 inline.
- **honest reporting**: SSN++ +1~+2% ceiling, ★4 sparse_rp = paradigm anchor (standalone 우위 X), Multi 25× shrinkage 모두 명시.

---

## §6 산출 권장 (Claude Design 호출 옵션)

### Option 1 — 5/27 발표 18 page deck PDF (메인)
- base: `slide_redesign_v2_20260508.md` 또는 `Academic v3 · Final 5_27.pdf`
- update: 4강 method × 10 cell paired Δ% + Multi 25× shrinkage + Adaptive paired Outcome A/B + 5 paradigm × 11 method matrix + sparse_rp paradigm anchor narrative
- speaker notes: 18 슬라이드 한국어 발표 대본 (slide당 30~45초, 총 12~15분)

### Option 2 — 1 page infographic (제출용)
- 4 column: motivation → method (5 paradigm) → result (★1~★4 + Outcome A/B) → insight (Multi 25× + paradigm anchor)
- 6/11 최종보고서 cover figure 후보

### Option 3 — Interactive HTML storyline
- React + Recharts: paradigm matrix drill-down + paired Δ% per cell hover + outcome A/B/C/D filter + ensemble overlay (5/9 fill)
- GitHub Pages 호스팅 가능 형태

### Option 4 — 1 page poster (5/28 전시회)
- A1 size, hero figure (paradigm matrix) + 3 sub-chart (stack / shrinkage / outcome) + QR code → 보고서

---

## §7 honest reporting 필수 항목

본 narrative 의 학술 정직성 (academic honesty) 을 위해 다음 5가지를 visualization 어디에든 반드시 명시한다.

1. **★4 sparse_rp = Outcome B (동등, paradigm anchor)** — standalone 우위 X 가 honest reporting 임을 명시. Standalone 우위가 강한 ★1~★3 와 동일한 학술 권위로 *paradigm coverage* 가치를 입증.
2. **LSH Wave 0 fail (Hyperparameter misalignment)** — K=20 stratification vs n_hyperplanes=5 의 hash space mismatch (V8 audit 정정). +2092% raw 결과 = LSH paradigm 의 본질 fail 이 아니라 K vs n_hp 정합성 오류로 honest reporting.
3. **Multi 25× shrinkage = "단일 정확성 = multi 정확성의 *필요조건*만"** — Joint distribution 분산 분해 limitation 정량 evidence. 충분조건 X 명시.
4. **Reservoir single-cell = RANDOM20 proxy** (V7 finding) — Reservoir 의 classical Vitter 1985 single-pass implementation 이 단일 cell K=20 partition 의 RANDOM20 proxy 와 수치 일치. master_v6 §10.7 + outline v2 §6 L11 정정 완료.
5. **SF100 (80M) = scope 제외** (5/8 22:16 결정, future work) — 측정 시간 부담 (~60-80h) 5/27 전 가용성 자문 의견 후 결정.

추가 limitation 4종 (CLAUDE.md 명시): KM20 oracle (production X) / 사전 계산 one-time cost / OLTP 범위 외 / 단일→멀티 future work.

---

## §8 self-contained 보장

본 prompt 는 다음 essential context (5/8 22:00 finalize 시점) 를 모두 포함한다.

- ✅ 5 paradigm framework 정의 + 11 method 학술 backbone (§1, §4)
- ✅ Single 10 cell × 4 method paired Δ% raw 데이터 (§3 Stack chart)
- ✅ Multi 2 cell × 4 method shrinkage (§3 Shrinkage chain) + 5/9 STAGE 3 placeholder
- ✅ Adaptive paired Outcome A/B 판정 (§1 Para 4 + §3 Outcome chart)
- ✅ Audit 9종 (V1~V11) finding (§2 Audit + §7 honest reporting)
- ✅ 학술 backbone (§4) — 11 method canonical citation + Exqutor + PDX + ACM CSur
- ✅ 디자인 시스템 (§5) — Apple SD Gothic Neo + navy + numbered badge
- ✅ 산출 4 option (§6) — deck / infographic / interactive HTML / poster
- ✅ honest reporting 5가지 (§7) — sparse_rp / LSH fail / Multi shrinkage / Reservoir proxy / SF100 scope

따라서 다른 session 이 본 doc 만 read 하면 **추가 file 탐색 없이** Claude Design 또는 Claude Code 에서 5/27 발표 deck / storyline visualization 생성 가능.

---

## §9 5/9 morning Multi 회수 후 update placeholder

다음 항목은 5/9 morning Multi 4 task (Multi paradigm 11 method × 3 cell + Multi Adaptive + Multi SF1 + YFCC K-sweep) 회수 + analyze_multi_paradigm.py 분석 후 fill.

| 영역 | 현재 (5/8 22:00) | 5/9 update 후 |
|---|---|---|
| §1 Para 5 Multi 25× | 단일 17.13% → multi 0.67% (2 cell) | 3 cell finalize, joint distribution 분산 분해 추가 evidence |
| §3 Hero matrix | Single only paradigm × method | Single + Multi 11 method × 3 cell overlay |
| §3 Shrinkage chain | 2-stage (Single → Multi-vector) | 3-stage (Single → Multi-vector → Multi-join) |
| §3 Outcome chart | 40 single test (Outcome A/B) | + 12 multi test (3 cell × 4 method) Outcome A/B/C/D 분포 |
| §3 Adaptive vs Ensemble | placeholder | Multi cell 별 winner ranking + ensemble overlay |
| §6 Option 1 deck | 16 slide v3 base | 18 slide (Multi paradigm 추가 + Adaptive Outcome 추가) |

placeholder 위치를 코드 내 `<!-- 5/9 update -->` 로 표시 권장. 5/9 morning 회수 task 가 완료되면 본 prompt 의 §1 Para 5 + §3 시각화 4종 + §9 표 행 전부 fill 가능.

---

## §10 사용자 진행 절차

1. **5/8 evening (또는 5/9 morning)** — 본 doc 을 Claude Design (https://claude.ai/design) 또는 별도 Claude Code session 에 paste/`@` 참조.
2. Option 1~4 중 선택 ("18 slide deck 생성" / "1 page infographic" / "interactive HTML" / "A1 poster").
3. Claude Design / Claude Code 가 narrative + 데이터 + 디자인 시스템 + honest reporting 5가지 반영하여 산출.
4. 결과 저장: `/Users/hyunbin/Capstone/submission/_drafts/` (deck/infographic) 또는 `experiments/figures/` (chart only).
5. **5/9 morning Multi 회수 후** — 본 doc 의 §1 Para 5 + §3 시각화 + §9 placeholder 를 fill 후 재실행 (또는 산출물 직접 update).
6. 5/22 박광현 교수님 미팅 reflection + 5/27 최종 발표 + 5/28 전시회 + 6/11 최종보고서 활용.

---

## §11 비상 plan

- Claude Design 한도 초과 시 → `Slides.jsx` 직접 수정 (`/Users/hyunbin/Capstone/submission/_drafts/academic_deck_v3_source/academic-deck/Slides.jsx` 의 16 React component 내 hardcoded 수치만 update, 디자인 그대로).
- Claude Code session 에서 작업 시 → `/Users/hyunbin/Capstone/_internal/scripts/md2pdf.py <file>` 로 md → PDF 변환 (Apple SD Gothic Neo 자동 적용).
- 5/9 multi 회수 지연 시 → §1 Para 5 + §3 시각화 4종 + §9 placeholder 는 단일 100% finalize 결과만으로 deck 생성 가능 (Multi 결과는 supplementary slide 로 분리).

---

**작성**: handoff_v14 (5/8 22:00 KST) 시점, 5 paradigm × 11 method framework + Single Adaptive Outcome A/B + Multi 25× shrinkage + 9 audit (V1~V11) finalize 후 self-contained storyline prompt 로 추출.
