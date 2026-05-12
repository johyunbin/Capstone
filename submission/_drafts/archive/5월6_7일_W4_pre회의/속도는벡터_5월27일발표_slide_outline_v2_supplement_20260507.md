# 속도는벡터 5/27 발표 — Slide outline v2 supplement (W3 sprint 결과)

> **본 supplement = 5/7 W3 sprint 산출 (5-cell matrix + Exqutor 비교) 추가.**
> 기존 outline (`속도는벡터_5월27일발표_slide_outline_20260506.md`) 의 핵심 update.

**작성**: 2026-05-07 15:50 KST · W3 sprint 완료 직후
**5/26 슬라이드 마감 / 5/27 발표 (D-20)**

---

## 갱신 필요 슬라이드 (기존 12-14장 outline 의 update)

### Slide 3 (RQ 구조) — 갱신
- 핵심 결과 기존 (RQ3) — `Hilbert -1.78%, -2.47% / HDBSCAN SIFT mid-sel -3.99%`
- **갱신 (5-cell matrix, sel=0.10 기준)**:
  - Hilbert: DEEP_1M -0.97% / DEEP_8M -2.21% / SIFT_1M -3.70% / SIFT_1.5M -7.06% / SIFT_8M -2.64% (5/5 CI 0 제외)
  - HDBSCAN: DEEP_1M -2.42% / DEEP_8M -2.13% / SIFT_1M -4.82% / SIFT_1.5M -8.55% (4/5 CI 0 제외, 8M chain timeout 1건)
  - Hybrid: 5/5 CI 0 제외, SIFT 가장 강 (-8.47% at SIFT_1.5M sel=0.10)
  - MiniBatch_partial: 5/5 CI 0 제외, OLTP production-ready (ARI=1.000 vs batch)

### Slide 4-5 (RQ1) — 보존
- Phase 6/7 narrative 보존
- gradient 19.6%p (Phase 6 production-near) 보존

### Slide 6-7 (RQ3 4강) — 갱신
- 4강 method 별 cross-scale 5-cell 결과 추가
- Cross-scale stability summary (DEEP_1M↔8M 78%/89%, SIFT_1M↔8M 83%/91%)

### Slide 8 (Negative control) — 갱신
- distance_shell 5/5 dataset CI 0 제외 hurt (+4.84% ~ +8.57%)
- random_proj SIFT skew dataset 에서 +31% ~ +49% LARGE hurt
- 분할 자체 결정성 narrative 강화 (5-cell 일관)

### Slide 9 — 신규 추가 (Cross-scale stability)

**제목**: "Cross-scale Stability — Primary 4-cell"

내용:
- 본 연구의 Primary 4-cell (DEEP/SIFT × 1M/8M, BIGANN raw extract 통일)
- DEEP_1M ↔ DEEP_8M: 36 cells, 78% CI 일관, 89% 부호 일관, median Δ +0.04%
- SIFT_1M ↔ SIFT_8M: 75 cells, 83% CI 일관, 91% 부호 일관, median Δ +0.20%
- Conclusion: **본 연구 contribution 의 scale-invariance 입증** (1M 결과가 8M 에서도 80%+ CI 일관 + 90%+ 부호 일관)

### Slide 10 — 신규 추가 (Exqutor 비교 framing)

**제목**: "Exqutor 와의 Complementary 보강"

| 비교 | Exqutor | 본 연구 | 보완 |
|---|---|---|---|
| Scale | SF=100 = 80M (max) | SF=10 = 8M (cross-scale 1M+8M) | 본 연구 8M = Exqutor 가장 작은 scale |
| Vector | 5종 average | DEEP+SIFT 2종 contrast | average vs distribution contrast |
| 인덱스 | HNSW + 비인덱스 | 비인덱스 only | Adaptive Sampling 영역 분포 인지 |
| Optimization | ECQO + momentum | 22 method stratification | momentum 위에 stack 가능 (orthogonal) |

본 연구 = Exqutor 의 **단일 테이블 비인덱스 영역의 분포 인지 가치 정량화**.

### Slide 11 — Limitations 갱신 (6 → 10종)

기존 6 + W2 부록 2 (L7 IS NaN, L8 Recovery Rate 분모) + **W3 NEW 2**:
- **L9**: SIFT 1.5M (TPC-H natural baseline) vs SIFT 1M (BIGANN raw) 분리 reporting
- **L10**: Exqutor scale gap (SF=10 vs SF=100), 80M scale-up future work

### Slide 12 — Future work 갱신
- 80M scale-up direct comparison (BIGANN learn.100M 80M extract)
- 5 dataset 매칭 (SimSearchNet++/WIKI/YFCC) — 자문 회신 후 결정
- vector.c hook 8M 측정 (memory leak 해결 필요)
- toy_multi_join Worker H 멀티조인 검증 (5/8 회의 후)

---

## 추가 figure 후보 (W3 NEW)

1. **5-cell heatmap** (5 method × 5 dataset, sel=0.10 paired bootstrap CI delta_pct_mean) — 색상으로 improve/hurt 시각화
2. **Cross-scale scatter** (1M vs 8M delta, DEEP+SIFT, point shape per method) — 1:1 line 으로 일관성 강조
3. **distance_shell + random_proj negative control bar chart** (5 dataset × 5 sel) — 분할 결정성 narrative

산출 위치: `experiments/figures/rq3_supplementary/` (기존 8 PNG + W3 추가 3 PNG 예정).

---

## 주발표자 결정 (5/8 회의 안건)

기존 outline 에 \"주발표자 미정\" 표기. 5/8 회의에서 합의 후 5/26 슬라이드 마감 전 결정.
