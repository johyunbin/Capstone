# ICDE_Exqutor.pptx verbatim 발췌 — 박광현 #4 자산 차용 source

> 작성: 2026-05-23 12:50 KST · 출처: `submission/_drafts/ICDE_Exqutor.pptx` (27장, 5/22 15:09 박광현 미팅 자료, BDAI 연구실 Kim·Lim·An·Sen·Park 저)
> 용도: 5/27 최종 발표 deck 재프레이밍 신본 (storyline_NEW · redline · prompt) 에 ICDE 자산을 "맥락 차용 + 차이 명시" 방식으로 반영하기 위한 verbatim 참조본
> 차용 4 자산 (사용자 5/23 12:33 결정): RAG analyst 시나리오 · HW spec · TPC-H VAQ + plan viz · step-by-step VSS cardinality 흐름

---

## 자산 1 — RAG analyst 시나리오 (ICDE 슬라이드 3-9, "VAQ in RAG Scenario")

verbatim 핵심 문장 (slide 6-7):

> "Given supplier parts similar to this image, analyze customer comments from 2024 data and determine an appropriate discount rate."
> — Analyst (사용자 페르소나)

분석 흐름 (slide 7-9):
- Relational filters and joins
- Vector Similarity Search — "To find semantically related items by calculating their distance"
- 둘이 결합 → Vector-augmented Analytical Queries (VAQs)

**한국어 번역 (deck 차용 시 사용)**:
> "공급자 부품 이미지와 비슷한 부품들을 찾아, 2024년 데이터에서 고객 리뷰를 분석해 적절한 할인율을 결정하라"

비전공자 진입 효과: 분석가가 "이미지로 유사 부품 검색 + 텍스트 리뷰 분석" 을 한 SQL 쿼리로 처리하는 시나리오 — VAQ 의 직관적 예시.

---

## 자산 2 — HW spec (ICDE 슬라이드 12, 25, 26 footer)

verbatim (slide 12, 25, 26 각 출처):

> "*Experiment Setup
> Intel Xeon Gold 6530 with 128 vCPUs and 1.0 TB of RAM."

(slide 25·26 footer 도 동일: "*Intel Xeon Gold 6530 configured with 128 vCPUs and 1.0 TB of RAM.")

**우리 측정 환경 (carry 확인)**: 서버 `165.132.140.240` = 동일 환경 (`_internal/SERVER_REGISTRY.md` 참조). HW carry 명시 가능.

---

## 자산 3 — TPC-H VAQ + plan visualization (ICDE 슬라이드 10, 25)

verbatim (slide 10):

> "Vector-augmented SQL Analytics"
> "TPC-H and TPC-DS benchmark (SF100) are extended with vector datasets: DEEP (96 dim), SIFT (128 dim), and SimSearchNet (256 dim)"
> "New vector columns (yellow) in TPC-H benchmark"
> "VAQ derived from TPC-H Query 12"

verbatim (slide 25):

> "Evaluation (1) Vector Index-based Exact Cardinality Query Optimization"
> "Exqutor achieves performance gains up to four orders of magnitude."
> "Table including vector is pushed down"
> "Hash to Nested Loop Join"
> "Query execution time for TPC-H VAQs (SF100)"
> "Query plan comparison for TPC-H Q3 based VAQ on DEEP dataset"

**우리 측정 정합 (carry 확인)**: 우리도 TPC-H Q3·Q9·Q10·Q12 × DEEP (96 dim) 사용. 쿼리·하네스 ICDE carry, 단 결론은 음성.

---

## 자산 4 — Step-by-step VSS cardinality 흐름 (ICDE 슬라이드 13-17, "Wrong VSS Cardinality")

verbatim 흐름 (slide 13 → 17 점진 전개):

**Slide 13-14 — 문제 인식**:
> "Wrong VSS Cardinality"
> "Existing systems use fixed heuristic cardinality of VSS."
> "However, the cardinality of VSS can be changed by vector distance threshold D"
> "${user-defined parameter}"
> "A small D implies high similarity"

**Slide 15 — 결함 노출**:
> "Set D to a small value"
> "Existing systems contains vectors"
> "Fixed VSS selectivity 0.333" (pgvector)
> "Fixed VSS selectivity 1.0" (duckdb-vss)
> "query plan from pgvector"

**Slide 16-17 — ECQO fix**:
> "Exqutor"
> "query plan from pgvector with Exqutor"
> "Accurate VSS cardinality estimation is the key of the performance VAQ!!"

**Slide 19-23 — Exqutor 두 메커니즘**:
> "An open-source, pluggable framework for improving VSS cardinality estimation in existing DBMSs"
> "Two complementary mechanisms"
> "(1) Vector Index-based Exact Cardinality Query Optimization (ECQO)"
> "(2) Sampling-based Cardinality Estimation"
> "When vector index is not available, Exqutor estimates VSS cardinality with sampling"
> "Momentum-based adjustment algorithm: Exqutor adaptively adjusts the sample size based on Q-error."

**Slide 26 — Adaptive Sampling 결과**:
> "Evaluation (2) Sampling-based Cardinality Estimation"
> "With adaptive sampling, Exqutor achieves up to 3.2x speedup."
> "Skewed vector dataset needs more samples for estimating cardinality."

**우리 위치 정합**: ICDE 의 (2) Sampling-based Cardinality Estimation = 우리 본 연구의 § V-B 영역. ICDE 는 momentum-based adjustment 전체를 답으로 제시하나, 우리는 그 안의 "표본 선택" 단 한 단계 (Bernoulli vs 분포 인지 층화) 만 분리해 통제 실험.

---

## 차이 명시 — 우리가 ICDE 와 다르게 답한 지점 (4 사용처 공통 carry)

| 사용처 | ICDE 가 한 일 | 우리가 한 일 |
|---|---|---|
| RAG 시나리오 (자산 1) | VAQ 의 동기 example 로 제시 | 동일 시나리오 진입 → 우리는 카디널리티 추정 단계 한 곳만 검증 |
| HW spec (자산 2) | 측정 setup 명시 | 동일 HW carry · 측정 범위는 56 cell phase2 sequential 로 한정 |
| TPC-H VAQ + plan viz (자산 3) | 4 쿼리 × 3 벡터 데이터셋 plan 시각화 → up to 4 orders of magnitude speedup 입증 | 동일 쿼리·하네스 carry · 결론은 음성 (베이스라인이 이미 정답 수준 plan 회복, 결합 추가 개선 없음) |
| Step-by-step (자산 4) | (V-A) plan 결함 fix → ECQO + (V-B) Adaptive Sampling 전체 = Exqutor 의 답 | (V-B) Adaptive Sampling 안의 "표본 선택" 단 한 단계만 분리 → 통제 실험으로 89% 우위가 분포 인지 효과 아님을 규명 |

---

## 박광현 #3 reject 사유 (이중 명시 공통 verbatim)

> "박광현 교수님 5/22 미팅 #3 '쿼리 흐름 (exqutor → skew → 제안 → optimal)' 권고는 89% Q-error 개선 = 분포 인지 층화 효과 라는 인과 가정 위에 서 있었다. 5/23 03:14 KST 감사 (Codex 적대 재검증) 결과 89% = 앙상블 평균 효과 (통제군 평균 비교군 1.459 ≤ 결합 1.477), latency 56 cell paired Δ% +0.13% 무개선 — '제안 → optimal' 단계 자체가 음성. 따라서 #3 flow 폐기 불가피. #1 (실험 상황 명시) 과 #4 (ICDE pptx 참고) 자산은 selectively 차용·차이 명시 형태로 반영. 사전 보고 절차는 박세은 팀장 합의 후 박광현 교수님 미팅 또는 메일."

---

작성: 2026-05-23 12:50 KST · 박광현 #4 ICDE 자산 차용 verbatim source · 산출물 3건 (storyline_NEW · redline · prompt) 패치에 cross-reference
