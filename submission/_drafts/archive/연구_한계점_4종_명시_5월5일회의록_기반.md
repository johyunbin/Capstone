# RQ 연구 Limitation 4종 명시 (5/5 회의록 line 122-126)

> **5/27 발표 / 6/11 보고서 의 Limitation 섹션 표준 문서.**
> 5/5 비대면 회의 (line 39, 64-67, 122-126) 합의 사항을 정량 evidence + narrative 로 정리.

---

## Limitation 1 — KM20 oracle, production 솔루션 X

### 회의록 인용

> 박세은: \"인덱스가 없을 때 KM 을 사용하는데, 이 클러스터가 사실상 인덱스를 만드는 것이라 전제 조건 위배 아닌가?\" (5/5 line 47)

### 현황

본 연구의 RQ1/RQ2 baseline 으로 **KM20 K-means full-batch clustering** (sklearn, ~30분 학습 시간, 1.2초 inference per query) 사용. 이는:

- ✅ HNSW index (검색 가속용, 수GB) 와 다른 layer — KM 라벨은 **옵티마이저 단계 추정 정확도용** (4MB)
- ✅ One-time cost — 학습 후 stratum lookup O(1)
- ⚠️ **Production OLTP 환경 (INSERT 빈번) 에서 cluster 재학습 부담**

### 정량 evidence

- KM20 vs MiniBatch K-means (RQ3 #8) recovery rate ≈ 75-95%
  - DEEP: KM20 vs BERN -1.64~-8.93% / MiniBatch vs BERN -1.88%
  - Recovery rate ratio 0.75 ~ 0.95 — MiniBatch 가 KM20 의 75-95% 회수
- MiniBatch 학습: 1% sample, ~수초 (KM20 의 1/100 ~ 1/600)
- **MiniBatch partial_fit** (RQ3 #8b): chunk 별 incremental update, ARI(batch, partial) = **1.000 (clustered)** → OLTP 적용 검증

### Mitigation

- 본 연구는 **KM20 = oracle benchmark**, MiniBatch + partial_fit = **production solution** 의 분리 framing
- RQ3 의 7-method 비교가 production-realistic alternative 정량

---

## Limitation 2 — 사전 계산 = One-Time Cost (HNSW 와 같은 Layer)

### 회의록 인용

> 박세은: \"클러스터링 사전 계산 시간이 길면 빠른 쿼리 응답 요구와 충돌, 비효율적이지 않은가?\" (5/5 line 48)

### 현황

KM20 학습 ~30분 (DEEP 1M). 그러나:

- HNSW index 빌드도 ~수분~수십분 — vector DB 의 표준 인프라 패턴
- 학습 후 stratum lookup = O(1)
- **DEEP 1M 의 KM20 학습 1.2초** (Phase 6 측정 — fast convergence)

### 정량 evidence

| Layer | 비용 | 빈도 | 비고 |
|-------|------|------|------|
| HNSW index | 수분~수십분 | 1회 빌드 + INSERT 시 incremental | ANN 검색 인프라 |
| **KM20 학습** | **1.2~30분** | **1회 빌드 + INSERT 시 재학습 X** | 본 연구 oracle |
| MiniBatch | ~수초 | 1회 빌드 + partial_fit 매 chunk | RQ3 production |
| 쿼리 응답 | ms 단위 | 매 query | optimizer 단계 |

→ KM20 사전 계산 = HNSW 와 같은 build-time layer. **Query 응답 시간과 무관**.

### Mitigation

- Production deploy 패턴: HNSW 빌드와 함께 KM20 (또는 MiniBatch) 빌드 → optimizer 의 stratum_id metadata 로 저장
- INSERT 빈번 OLTP 는 **Limitation 3** 으로 별도 framing

---

## Limitation 3 — INSERT/UPDATE 빈번한 OLTP 범위 외

### 회의록 인용

> \"INSERT 빈번 OLTP 는 본 연구 범위 외 — RQ3 의 F (MiniBatch) 가 부담 1/20~1/100 수준 완화\" (5/5 line 52)

### 현황

본 연구는 **OLAP-style 분석 쿼리** (vector range query 의 cardinality 추정) 에 초점. INSERT 빈번 OLTP 는:

- KM20 의 cluster 무효화 빈도 ↑ → 재학습 비용 누적
- BERN sampling 의 row 단위 sample (block 무관) 은 INSERT 에 robust

### 정량 evidence (RQ3 #8b MiniBatch partial_fit)

- partial_fit chunk size 1,000 rows, ~10ms/chunk (학습 sample 기준)
- 1M rows / chunk_size 1,000 = 1,000 chunks → 총 ~10초 incremental update
- 비교: KM20 full re-fit ~30분 → **partial_fit 이 ~180× 빠름**
- ARI(batch, partial) = 1.000 (clustered) → 정확도 손실 없음 (clustered data)

### Mitigation

- partial_fit 의 INSERT 빈도별 update 정책 제안 (e.g., 매 1K row INSERT 마다 partial_fit)
- Drift detection (centroid shift threshold) → 임계 초과 시 full re-fit
- **5/27 발표 narrative: \"OLTP 적용 가능성의 정량 증명, 실제 deployment 는 future work\"**

---

## Limitation 4 — 단일 → 멀티 테이블 일반화 = Future Work

### 회의록 인용

> 박세은: \"Exqutor 와 연관 지으려면 멀티테이블 환경에서 검증을 통해 단일 → 멀티 개선이 이루어지는지 검증 절차가 필요하지 않은가?\" (5/5 line 21)
>
> 결정 (line 23-27): \"멀티테이블 검증은 KM20 의 stratum_id 가 join 후에도 의미를 유지하는지의 이론적 문제부터 다시 풀어야 하는 새 연구 분량. 캡스톤 범위 외. **(A) Exqutor 가 미작동하는 단일테이블 영역에 대한 새 솔루션, 멀티는 future work** 채택.\"

### 현황

- 본 연구의 모든 측정: **single-relation vector range query** (DEEP 1M / SIFT 1.5M / DEEP 8M).
- Exqutor 의 main scope: multi-table join 의 카디널리티 추정.
- 단일 정확성은 멀티 정확성의 **필요조건** (iff 아님).

### 정량 evidence — 단일 → 멀티 *필요조건* framing

```
Single-Relation 의 카디널리티 추정 정확도 = E[q_error_single]
Multi-Relation join 의 카디널리티 추정 정확도 = f(E[q_error_single], join cardinality propagation)

→ 단일 부정확 (q_error_single >> 1) → 멀티 부정확 보장
   단일 정확 (q_error_single ~ 1) → 멀티 정확 *가능성*
```

본 연구는 **단일의 정확도** 를 정량 — 멀티의 *필요조건* 인 layer 검증.

### Mitigation / Future Work

- **Phase 1 (본 연구)**: 단일 테이블 cardinality 추정 정확도 (Hilbert, MiniBatch 등 7+ method)
- **Phase 2 (future)**: KM20 stratum_id 가 join 후에도 의미를 유지하는 이론 분석 (multi-relational K-means)
- **Phase 3 (future)**: Exqutor 의 multi-table framework 와 본 연구의 single-table optimization 통합

→ **Phase 1 자체가 publishable contribution**. Phase 2/3 은 별도 연구 분량.

---

## Limitation 표준 narrative (5/27 발표 / 6/11 보고서 인용용)

> 본 연구는 다음 4 가지 한계를 명시한다:
>
> (1) **KM20 = oracle benchmark, production 솔루션 X** — full-batch K-means 의 사전 학습 부담. 이는 RQ3 의 MiniBatch K-means (1/100 비용) 와 partial_fit (streaming OLTP) 가 production replacement 로 검증.
>
> (2) **사전 계산 비용은 HNSW 와 같은 build-time layer** — query 응답 시간과 무관. KM20 학습 1.2~30분 (DEEP 1M) 은 HNSW 빌드와 같은 인프라 비용.
>
> (3) **INSERT 빈번 OLTP 환경은 본 연구 범위 외** — partial_fit (~10ms/chunk × 1K rows) 의 ARI 1.000 (clustered) 측정으로 적용 가능성 정량 증명. 실제 deployment 의 drift detection 은 future work.
>
> (4) **단일 → 멀티 테이블 일반화는 future work** — 단일 카디널리티 정확도가 멀티의 *필요조건*. 본 연구는 Exqutor 의 단일 테이블 미작동 영역 에 대한 새 솔루션. 멀티는 별도 연구 분량 (multi-relational K-means 의 이론 정의 등).

---

## 본 문서의 위치

- **5/27 최종 발표 슬라이드 12** (RQ 결과 종합 + Future work)
- **6/11 최종 보고서 §Limitation 및 Future Work** 섹션
- **자문 메일 (지도교수)** 의 첨부 — limitation 정량 framing 자문 요청

---

**작성**: 조현빈 · 2026-05-07 00:15 KST · 5/5 회의 합의 정리
