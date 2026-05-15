# [속도는벡터] 5/27 발표 후 자문 요청 — v11 framing reframing + 6/11 보고서 narrative + 4 엔진 통합 POC plan

박광현 교수님 안녕하십니까, 연세대학교 캡스톤 디자인 속도는벡터 팀 조현빈입니다.

5월 27일 캡스톤 최종 발표가 성공적으로 마무리되었습니다. 5월 15일 미팅에서 교수님께서 제안해주신 (1) 4 엔진 통합 POC (PostgreSQL pgvector + DuckDB + Faiss + Qdrant) 영역 cross-engine 일반화 검증 + (2) 본 연구 narrative 영역 단순화 방향성 두 input 영역 5/27 발표 deck v11 영역 그대로 반영하였고, 박세은 5/15 20:49 framing 단순화 의도 (sample selection 영역 일관 통일) 영역 prompt v11 (3 part) 영역 deck 영역 적용하였습니다. 본 메일은 6/11 최종 보고서 (LearnUs 제출 + 캡스톤 홈페이지 게시) 마감 전 마지막 자문 요청 영역으로, **5/29 ~ 6/3 영역 회신 받을 수 있다면 6/4 ~ 6/10 sprint 영역 충분히 반영하겠습니다**.

본 메일은 2026-05-28 발송 예정이며, 5/27 발표 직후 정리 영역 첨부 자료 영역 함께 송부합니다.

## § 1. 5/27 발표 영역 결과 보고

5월 27일 발표는 deck v11 (25 slide × 60 sec ≈ 25m + Q&A 5m = 30m) 영역 박세은 팀장 영역 발표 영역 마무리되었습니다. 5/15 미팅 input 영역 반영 영역 핵심 변경 사항은 다음과 같습니다.

| 항목 | 5/15 미팅 시점 (deck v4) | 5/27 발표 (deck v11) |
|---|---|---|
| main theme | "Measurement-driven Distribution-aware **Cardinality Estimation** for VAQ" | "Distribution-aware **Sample Selection** for VAQ Cardinality Estimation" |
| framing layer 분리 | 혼재 (paper 영역 vs 우리 영역 모호) | 3 layer 명확 분리: paper (cardinality 추정 mechanism, 그대로) / 우리 (sample selection augment) / evidence (Q-error paired Δ%) |
| 측정 portfolio | 1001 file (B1 9 + CaseA 495 + CaseB 496) | 약 2039 file (CaseA 폐기 + B1 + CaseB only, v6/v7/v8/v9/v10 chain 영역 1348 file 추가 측정) |
| paradigm 사용 method | 56 method (audit 후 23 폐기) | 16 method 영역 framing 일치 (사용 16 method = P1 3 + P2 3 + P3 1 + P4 4 + P5 2 + P6 2 + P9 1) |
| 본 발표 핵심 evidence | "CaseA vs CaseB 92.5% paired Δ%" | "**sample selection 영역 Q-error paired Δ% 92.5% 개선**" + Pareto Top 5 cell × method best 매핑 + dynamic 할당 mechanism |

발표 후 청중 영역 (지도교수 박광현 교수님 외 캡스톤 심사 교수진) 영역 받은 코멘트 영역 6/11 보고서 영역 반영 plan 영역 ★ § 4 영역 정리되어 있습니다.

<div class="page-break"></div>

## § 2. v11 framing reframing 영역 적용 영역 — paper layer vs 우리 layer 명확 분리

박세은 5/15 20:49 카톡 + 5/16 00:18 정리 영역 핵심 framing 단순화 의도는 다음과 같습니다.

> "우리는 추가 method 통해서 **Q-error 만 보완**하면 되는 게 아니냐. 카디널리티 추정은 알아서 할거고"
> "Exqutor 논문에 완전 기여할 필요 X (별도 트랙). 우리 = sampling 자체에 대해서만 수치 확인 + Q-error 영역 개선 evidence"

본 framing 영역 deck v11 + 본 메일 + 6/11 보고서 outline v3 영역 일관 통일하였습니다. 핵심 layer 분리는 다음과 같습니다.

| layer | 영역 | 본 연구 영역 |
|---|---|---|
| **paper 영역 (그대로 유지)** | (a) §V-A ECQO HNSW range query (b) §V-B Adaptive Sampling Eq 1-6 momentum 보정 (c) cardinality 추정 mechanism 자체 (Bernoulli est_b1) | 간단 소개 (paper Exqutor 본인 contribution 인정), **본 발표 영역 X** |
| **우리 contribution 영역** | (a) Phase 1 = **분포 인지 sample selection** (sample 추출 mechanism) (b) Phase 2 = **dynamic 할당 mechanism** (Type 별 best method 자동 선택) (c) Phase 3 = est_b1 + est_method 산술 평균 minimal augmentation | 본 발표 + 6/11 보고서 핵심 영역 |
| **evidence** | "sample selection 영역 우리 method 가 random Bernoulli 대비 Q-error paired Δ% 92.5% 개선" | slide 18 거대 수치 영역 |

표현 통일 영역 deck v11 + 본 메일 + outline v3 영역 모두 적용하였습니다. ✗ 사용 금지: "cardinality 추정 우리 영역 contribution" / "estimation algorithm 우리 영역 개선". ✓ 사용 강조: "sample selection 영역 우리 영역" / "분포 인지 sample 추출" / "Q-error 영역 paired Δ% 개선".

이 framing reframing 영역 학술적 적절성 영역 첫 번째 자문 영역 부탁드립니다 (★ § 5 영역 자세히).

## § 3. 6/11 보고서 영역 narrative arc — 16 chapter outline v3

6/11 최종 보고서 영역 v5 outline (10 §) 영역 v3 영역 16 chapter 구조 영역 재구성하였습니다 (50-65p, 학술 보고서 dense 영역). v11 framing 영역 chapter 별 명확 분리 영역 달성 목표입니다. 16 chapter 영역 전체 구조 영역 다음과 같습니다.

| Ch | 영역 | 분량 | 작성 |
|---:|---|---:|---|
| 1 | 서론 + RQ + contribution scope reframing (sample selection augment) | 4-5p | 박세은 |
| 2 | paper Exqutor 간단 소개 (§V-A + §V-B + Eq 1-6 + hyperparam 7종 verbatim) | 5-6p | 이동욱 |
| 3 | 우리 영역 framework (Phase 1+2+3 명확 분리) | 4-5p | 조현빈 |
| 4 | 측정 portfolio (약 2039 file, B1 + CaseB only) | 3-4p | 조현빈 |
| 5 | 데이터셋 4 type 분류 (small single / medium single / large single / large multi 224-288d / large multi 864d) | 3p | 강재현 |
| 6 | paradigm 7개 × 사용 16 method (P1-P6 + P9) | 5-6p | 조현빈 |
| 7 | Pareto Top 5 cell × method best 매핑 | 3p | 조현빈 |
| 8 | dynamic 할당 mechanism (Type 별 best sample selection method 자동 선택) | 4-5p | 박세은 |
| 9 | 정확도 evidence — sample selection 영역 Q-error paired Δ% 92.5% | 5p | 조현빈 |
| 10 | 분포 catch speed (sparse_rp 3.67s ~ hilbert_real 43.50s, fit_time 11.9×) | 2-3p | 강재현 |
| 11 | selectivity sweep (sel = 0.001 / 0.01 / 0.10) — selectivity-dependent paradox | 3-4p | 조현빈 |
| 12 | plan robustness (20 cell × 3 sel × 16 method) | 2-3p | 조현빈 |
| 13 | Pareto frontier (정확도 best = 자원 best, 5 method scatter plot) | 2-3p | 강재현 |
| 14 | 결론 Finding 5 (sample selection 일관 5 finding) | 2p | 박세은 |
| 15 | limitation 18 + future work 8 (4 엔진 통합 POC + multi-table aware 등) | 3-4p | 조현빈 + 박세은 |
| 16 | appendix (측정 file 영역 / paper exact 정합 영역 / 환각 회피 룰) | 5-6p | 조현빈 |

<div class="page-break"></div>

본 outline v3 영역 narrative arc 영역 핵심 영역 다음과 같습니다.

1. **Ch.1-2 영역 framing layer 분리**: paper 영역 (cardinality 추정 mechanism) vs 우리 영역 (sample selection augment) 영역 명확 표시
2. **Ch.3-8 영역 우리 영역 framework + 측정 + dynamic 할당**: Phase 1+2+3 영역 명확 분리 + 16 method 영역 algorithm 영역 자세히 설명 + Type 별 best method 자동 선택 mechanism
3. **Ch.9-13 영역 5 evidence**: sample selection 영역 Q-error paired Δ% + 분포 catch speed + selectivity sweep + plan robustness + Pareto frontier
4. **Ch.14 영역 Finding 5**: sample selection 일관 5 finding 큰 수치 정리 + paper 영역 cardinality 추정 mechanism 영역 contribution X 강조
5. **Ch.15-16 영역 limitation + future work + appendix**: 환각 회피 룰 + 4 엔진 통합 POC plan + 향후 multi-table aware 영역

## § 4. 박광현 input 4 엔진 통합 POC — cross-engine 일반화 검증 plan

5/15 미팅에서 교수님께서 제안해주신 **4 엔진 통합 POC** 영역 6/11 보고서 §15 future work + (가능하다면) §16 appendix 영역 sketch 영역 추가 plan 영역 다음과 같이 정리하였습니다.

### 4.1 4 엔진 영역 (PostgreSQL pgvector + DuckDB + Faiss + Qdrant)

| 엔진 | 영역 | cardinality estimation 영역 | 본 연구 영역 sample selection augment 영역 적용 가능성 |
|---|---|---|---|
| **PostgreSQL pgvector** | row-store + HNSW/IVFFlat 인덱스 영역 vector column 추가 | pg_class 영역 통계 영역 33.3% 고정 비율 (Exqutor §I 영역 측정) | ★★★ 가장 직접 적용 (Exqutor base와 동일 영역) |
| **DuckDB** | columnar OLAP 영역 vector type extension 영역 | 100% 고정 비율 (Exqutor §I 영역 측정) | ★★ columnar storage 영역 sample 추출 영역 cost model 재검증 필요 |
| **Faiss** | vector-only library 영역 (RDBMS X) | N/A (cardinality 자체 없음, top-k retrieval 영역만) | ★ sample selection 영역 stratified search 영역 quality 비교 (recall@k 영역 metric) |
| **Qdrant** | vector DB 영역 (filtering 영역 RDBMS-like API) | payload filter 영역 cardinality estimation 영역 정확도 vs HNSW search 영역 trade-off | ★★ vector DB native 영역 cross-engine generality 영역 evidence |

### 4.2 본 POC 영역 RQ + scope

| RQ | 질문 | scope |
|---|---|---|
| **RQ4 (★ NEW)** | 본 연구 영역 sample selection augment 영역 4 엔진 영역 cross-engine 영역 일반화 가능한가? | DEEP/SIFT × sf=10 영역 동일 dataset × 4 엔진 영역 동일 sample selection method (Pareto Top 5 = chao_weighted + sparse_rp + pca1d + hilbert_real + hyperloglog) × Q-error paired Δ% 비교 |

scope 영역 6/11 보고서 마감 영역 시간 영역 **3 엔진 (pgvector + DuckDB + Qdrant)** 영역 한정 + Faiss 영역 future work 영역 미루기 plan 영역입니다 (Faiss 영역 cardinality 영역 없음 영역 별도 metric 영역 필요).

<div class="page-break"></div>

### 4.3 timeline plan

| 일자 | 작업 |
|---|---|
| 5/29 ~ 6/1 (3 day) | DuckDB + Qdrant 영역 sample selection method 영역 wrapper 작성 (Pareto Top 5 영역 5 method × 2 엔진 = 10 wrapper) |
| 6/2 ~ 6/4 (3 day) | DEEP/SIFT × sf=10 × 5 method × 3 엔진 영역 paired Δ% 측정 (≈ 30 file × 5 trial = 150 file) |
| 6/5 ~ 6/7 (3 day) | 분석 + 6/11 보고서 §15 영역 future work 영역 sketch 영역 작성 + (성공 시) §16 appendix 영역 추가 |

### 4.4 본 POC 영역 자문 요청

본 POC scope 영역 6/11 보고서 영역 future work 영역 sketch 영역만 추가 vs 별도 chapter (§17 4 엔진 POC) 영역 격상 vs (시간 부족 시) future work 영역만 명시 + 측정 X 의 **3 옵션 영역 적절성** 영역 자문 부탁드립니다. 또한 4 엔진 영역 sample selection 영역 wrapper 영역 학술적 정합성 영역 (각 엔진 영역 storage layout 영역 다름 영역 sample 영역 동일 정의 가능한가) 영역 의견 부탁드립니다.

## § 5. EDBT short paper 영역 venue 가능성 영역 추가 자문 요청

본 연구 영역 5/27 발표 + 6/11 보고서 영역 마무리 후 영역 학술 venue 영역 publish 가능성 영역 검토하고 있습니다. 후보 venue 영역 다음과 같이 정리하였습니다.

| venue | 영역 | submission 영역 | scope 영역 적합성 |
|---|---|---|---|
| **EDBT 2027** | European Conference on Extending Database Technology | short paper (4-6p) 영역 마감 ≈ 9월 (2026) | ★★★ vector DB + cardinality estimation + sample selection 영역 EDBT scope 영역 일치 |
| **VLDB 2027** | Very Large Data Bases | research paper (12p) 영역 마감 ≈ 3월 (2027) | ★★ scope 적합 + 측정 portfolio 영역 추가 + multi-table aware 영역 확장 영역 필요 |
| **SIGMOD 2027** | ACM SIGMOD | research paper (12p) 영역 마감 ≈ 7월 (2026) | ★★ scope 적합 + Exqutor base 영역 SIGMOD venue 일치 (Exqutor arXiv 2512 = 2026 venue) |
| **(국내) KDB** | 한국정보과학회 데이터베이스 영역 | short paper (6p) 영역 마감 ≈ 매년 6월 | ★★ 학부 capstone 영역 적합 + 추가 측정 영역 X |

본 연구 영역 가장 직접 적합 venue 영역 **EDBT 2027 short paper (4-6p)** 영역 판단하고 있습니다. 본 연구 영역 scope 영역 4 엔진 통합 POC 영역 추가 영역 EDBT short paper 영역 적합한가 영역 자문 부탁드립니다. 또한 학부 capstone 영역 EDBT submission 영역 첫 author 영역 적절성 (지도교수 영역 박광현 교수님 + 학부생 4명 영역 author 영역 정합성) 영역 의견 부탁드립니다.

가능하시다면 **6/3 (수)** 까지 회신 받을 수 있다면 6/4 ~ 6/10 sprint 영역 충분히 반영하겠습니다 (★ § 4 4 엔진 POC + § 5 venue 영역 두 영역 영역 6/11 보고서 영역 마감 영역 직접 영향 영역).

감사합니다.

**속도는벡터 팀 조현빈 드림**

<div class="page-break"></div>

## § 6. 첨부 자료

본 메일 영역 narrative 영역 학술 detail 영역 다음 자료 영역 확인 가능합니다.

| 영역 | 자료 영역 | 위치 |
|---|---|---|
| 5/27 발표 deck v11 | 25 slide × 60 sec ≈ 25m + Q&A 5m = 30m | `submission/_drafts/속도는벡터_5_27_키노트_prompt_v11_part{1,2,3}_*.md` (3 part) + 영역 generate deck v11 PDF |
| 6/11 보고서 outline v3 | 16 chapter × 50-65p, 4 팀원 분담 | `plans/최종보고서_outline_v3_20260516.md` + PDF |
| 5/27 발표 storyline v3 | 25 slide flow + speaker notes | `plans/5_27_storyline_v3_20260516.md` + PDF |
| narrative 본문 v6 draft | 10 단계 narrative 영역 v11 framing 영역 통일 | `submission/_drafts/속도는벡터_본연구_narrative_v6_draft_20260516.md` + PDF |
| 측정 분석 본체 REPORT v12 | 약 2039 file 영역 paired Δ% 분석 + paradigm rollup + Pareto Top 5 매핑 | `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md` (1500+ line) |
| handoff v32 영역 (참고) | 5/16 새벽 chain 영역 진행 + framing 영역 reframing 영역 commit chain | `_internal/handoff/active/handoff_v32_5_16_v10chain진행중_20260516_0116.md` |
| 5/15 박광현 미팅 자료 | 4 file 영역 (5/12 11:56 PDF + 12:15 README update) | `submission/_drafts/박광현_5월22일_미팅/` |
| 4 엔진 통합 POC plan | DuckDB + Qdrant wrapper 영역 sample selection augment 영역 timeline | (★ § 4 영역) |

작성: 2026-05-28 KST (5/27 발표 후) · 발송 예정: 2026-05-29 (5/27 발표 청중 영역 코멘트 영역 정리 후) · 자문 요청 회신 마감: 2026-06-03 (수)
