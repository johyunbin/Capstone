# 추가 측정/실험 plan — narrative v5 base

작성: 2026-05-15 21:15 KST · v5 narrative commit fdb9e04 base
목적: narrative v5 의 4 type + dynamic method selection axis 영역 measurement gap 식별 + 추가 측정 priority

---

## 1. 현재 1352 file 측정 portfolio 의 4 type 영역 cell 분포

| Type | 정의 | 현재 cells | cell 수 | gap |
|---|---|---|---:|---|
| **Type 1** | small single sf=1 (0.1M, 96d) | A5-scale-sf1 (DEEP) | 1 | ★ evidence 약함 (1 cell 만) |
| **Type 2** | medium single sf=10 (1M) | A5-scale-sf10 (DEEP) | 1 | ★ evidence 약함 (1 cell 만) |
| **Type 3** | large single sf=100 저-중차원 | A1-DEEP / A1-SIFT / A1-SSN / A4-sel / A5-scale-sf100 | 5 | ✓ evidence 강력 |
| **Type 4a** | large multi 288d | A2-Fig7 (DEEP+YFCC) | 1 | ★ evidence 약함 (1 cell 만) |
| **Type 4b** | large multi 864d | A2-Fig9 (DEEP+WIKI) | 1 | ★ evidence 약함 (1 cell 만) |

핵심 gap: Type 1 / Type 2 / Type 4a / Type 4b 각 1 cell 만 → evidence base 약함. 추가 측정 필요.

---

## 2. 추가 측정 priority 5 영역

### Priority 1 (★★★): Type 1 + Type 2 영역 SF axis 다른 dataset 확장
- 현재: A5-scale (DEEP 96d) 만 sf=1/10/100 측정
- 필요: SIFT 128d + SSN 256d 영역 sf=1/10/100 측정 (small/medium scale axis 확장)
- 측정량: 2 dataset × 2 scale (sf=1, sf=10) × 5 method (Pareto Top 5) × 2 mode (CaseA/CaseB) × 10 trial = 40 file
- + B1 baseline 2 cell × 2 scale = 4 file
- **총 ~44 file**
- server time 추정: 약 4-8h
- 가치: Type 1/Type 2 의 cell 수 1 → 3 (DEEP + SIFT + SSN) 으로 확장. sf=10 sweet spot 약화 evidence 가 dataset axis 일관 확인

### Priority 2 (★★★): Type 4a 영역 multi-table 중차원 다른 dataset
- 현재: A2-Fig7 (DEEP+YFCC 288d) 만 1 cell
- 필요: DEEP+SIFT (96+128=224d) 또는 SIFT+YFCC (128+192=320d) 등 추가 multi-table 중차원 cell
- 측정량: 1 new cell × 5 method × 2 mode × 10 trial = 10 file + B1 baseline 1 file = 11 file
- server time: 약 1-2h
- 가치: Type 4a evidence 1 → 2 cells

### Priority 3 (★★): Type 4b 영역 multi-table 고차원 다른 dataset
- 현재: A2-Fig9 (DEEP+WIKI 864d) 만 1 cell
- 필요: WIKI single (768d) 또는 SSN+WIKI (256+768=1024d) 등 추가 고차원
- 측정량: 1 new cell × 5 method × 2 mode × 10 trial = 10 file + B1 1 file = 11 file
- server time: 약 1-2h
- 가치: Type 4b evidence 1 → 2 cells

### Priority 4 (★★): Type 3 영역 추가 selectivity axis
- 현재: A4-sel = sel=0.001 (paper Fig 13 영역 첫 selectivity point) 만 1 cell
- 필요: A4-sel-0.05 + A4-sel-0.10 (paper Fig 13 sel sweep 완성) 추가
- 측정량: 2 new cells × 56 method × 2 mode × 10 trial = 약 220 file + B1 2 file = 222 file
- server time: 약 10-15h
- 가치: paper Fig 13 sel sweep 완성 (selectivity axis 영역 plan robustness evidence)

### Priority 5 (★): Type 별 K granularity 확장
- 현재: K granularity SF axis = A5-scale (DEEP) × K=10/30 × 4 anchor × 2 mode = 48 file
- 필요: SIFT / SSN 도 K=10/30 추가 측정 (Type 별 K best pattern 일관 검증)
- 측정량: 2 dataset × 3 sf × 2 K × 4 anchor × 2 mode = 96 file
- server time: 약 5-8h
- 가치: K=20 sweet (sparse_rp/chao_weighted) vs K=30 slight edge (hilbert_real/hyperloglog) patterns 가 dataset axis 일관 확인

---

## 3. 박광현 input 4 — 엔진 통합 POC

사용자 5/15 20:55 의도: 이전 narrative 정리 후 엔진 통합 실험 진행. v5 narrative 안 포함 (post-narrative).

### POC plan (post-narrative direction, 5/27 이후 가능)

**Phase 1 (5/27 발표 후 ~ 6/11 사이)**:
- PostgreSQL pgvector planner 영역 sampling routine swap-in 시도
- Type 판별 + dynamic method selection logic 구현
- TPC-H 영역 VAQ Q1-Q22 영역 plan 정확도 측정

**Phase 2 (post-6/11)**:
- DuckDB / 다른 엔진 통합 시도
- 실제 query 영역 end-to-end latency 비교
- POC 결과 → 후속 paper 형식 narrative 영역 통합

server time: Phase 1 약 20-40h dev + 10-20h 측정 = 30-60h total

---

## 4. 측정 priority 결정 영역 사용자 확인 영역

| priority | 측정량 | server time | 가치 |
|---|---:|---|---|
| P1 (Type 1/2 SF axis 확장 SIFT+SSN) | 44 file | 4-8h | Type 1/2 evidence cell 1→3 |
| P2 (Type 4a multi-table 중차원 추가) | 11 file | 1-2h | Type 4a evidence cell 1→2 |
| P3 (Type 4b multi-table 고차원 추가) | 11 file | 1-2h | Type 4b evidence cell 1→2 |
| P4 (A4-sel sel sweep 완성) | 222 file | 10-15h | paper Fig 13 sel sweep 완성 |
| P5 (K granularity dataset 확장) | 96 file | 5-8h | K pattern dataset 일관 |
| **P1+P2+P3 (Type 별 evidence 보강)** | **66 file** | **6-12h** | **★ 가장 효율적** |
| 박광현 input 4 엔진 통합 POC | dev 20-40h + 측정 10-20h | 30-60h | post-narrative axis |

---

## 5. 권장 진행 순서

**즉시 (5/15 ~ 5/16)**:
1. P1+P2+P3 통합 launch (66 file, 6-12h server time) — Type evidence 보강
2. K granularity dataset 확장 (P5, 96 file) — Type 별 K pattern 일관 evidence

**5/20 ~ 5/27 (D-7)**:
3. P4 A4-sel sel sweep (222 file, 10-15h) — paper Fig 13 완성 (선택적)

**5/27 발표 후**:
4. 박광현 input 4 엔진 통합 POC (Phase 1)

---

작성: 2026-05-15 21:15 KST · v5 narrative 4 type + dynamic method selection axis 영역 measurement gap + 추가 측정 priority 5 영역
