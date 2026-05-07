# 속도는벡터 5/27 최종발표 — Slide Outline + Speaker Notes

> **5/26 슬라이드 마감 / 5/27 발표 (D-21).**
> 본 outline 은 5/8 회의 narrative 합의 후 최종화 예정. 사전 점검용.

**발표 시간**: 12-15분 (Q&A 5분) / **슬라이드 수**: 12-14장 / **주발표자**: 미정 (회의 합의)

---

## Slide 1 — 제목 + 팀 소개

```
속도는벡터 — Vector-augmented Analytical Query 의
                분포 인지 sampling 가치 정량 연구

Team: 박세은 (팀장) · 강재현 · 조현빈 · 이동욱
지도: [지도교수] / 자문: 채림 (석사)

연세대학교 컴퓨터과학과 캡스톤 디자인 2026-1
```

**Speaker note**: 본 연구의 한 줄 요약 — \"기존 BERNOULLI sampling 의 부정확성 정량 + 분포 인지 sampling 의 가치 정량 + 13 method 비교\".

---

## Slide 2 — 동기 + 본 연구의 위치

배경:
- Exqutor (BDAI 연구실, arXiv:2512.09695) — vector range query 의 cardinality 추정
- Adaptive sampling (Exqutor) 가 *skewed* 분포에서 정확도 저하 가능성

본 연구의 위치:
- **단일 테이블** vector range query (single-relation) 의 sampling 정확도
- 분포 정보 활용한 stratification 의 가치 정량 + alternative 비교

scope 제외 (future work):
- Multi-table join (Exqutor 의 main scope)
- vector.c integration (현재 Python 시뮬레이션)

**Speaker note**: 단일 → 멀티 일반화는 future work, 단일 정확성이 멀티의 *필요조건*. 본 연구가 multi 의 base layer.

---

## Slide 3 — RQ 구조 (3 RQ)

| RQ | 질문 | 답 | 핵심 결과 |
|----|------|-----|----------|
| **RQ1** | 기존 random sampling 이 skew 데이터에서 얼마나 부정확? | 정량 + selectivity-dependent | 단조성 ρ=-0.680 CI 0 제외 |
| **RQ2** | 분포 알 때 어떤 allocation 최적? | KM20 oracle baseline 의 sample-size robustness 확인 | 모든 40 cell 일관 |
| **RQ3** | 분포 모를 때 어떤 stratification 최적? | Hilbert / MiniBatch 양강 (13+ method 비교) | Hilbert: -1.78%, -2.47% |

**Speaker note**: 이 3 RQ 가 점진적 narrative — RQ1 진단 → RQ2 oracle → RQ3 production alternative. 5/5 박세은 팀장 제안 후 확정.

---

## Slide 4 — RQ1 결과: Selectivity Gradient 단조성 확정

핵심 figure: `experiments/figures/rq1_rq2_w1_sprint/figure_3_5sel_grid_2x4.png` 또는 보강

수치:
- DEEP 1M × 5 sel × 5 seed: KM20-BERN 차이 +1.31% (s=0.50) → **+8.93% (s=0.01)**
- per-seed Spearman ρ = **-0.680**, 95% CI **[-0.800, -0.440]** ★ 0 제외
- DEEP-RAND 도 reverse-monotonic 확정 (ρ=+0.560 CI 0 제외)

Two-Level Decomposition:
- Level 1 (proportional allocation): sel 무관 보편적 효과
- Level 2 (spatial awareness): sel 작을수록 강 — 본 결과의 핵심

**Speaker note**: \"sel 이 낮을수록 공간 인식 sampling 의 가치가 커진다\" 의 *통계적 입증*. 단순 trend 가 아닌 ρ + bootstrap CI.

---

## Slide 5 — RQ2 결과: 5-Mode Allocation Ablation + Sample-Size Robustness

핵심 figure: `experiments/figures/rq1_rq2_w1_sprint/figure_5_rq2_alloc.png` 또는 보강

5-mode (BERN/Equal/Proportional/Neyman/Anti-Neyman) × DEEP/SIFT × 5 sel:
- 모든 stratified > BERN: DEEP -1.3~-7.0%, SIFT -3.7~-10.5% (p ≤ 1e-7~1e-50)
- **Neyman vs Equal**: SIFT × s=0.01 에서만 유의 (-11.9%, p_BH=0.024). σ_i 신호 약.
- **Anti-Neyman vs Proportional**: 좁은 sel 에서 systematic worse (DEEP s=0.01 +5.2%, SIFT s=0.01 +9.5%, CI 0 제외)

Sample-size sensitivity (4 ssize × 2 dataset × 5 sel = 40 cell):
- **모든 40 cell 에서 KM20 > BERN 일관** — Δ% -1.09 ~ -13.50%

**Speaker note**: \"σ_i 신호가 너무 약함\" 의 honest narrative. Anti-Neyman 의 hurt 도 정량.

---

## Slide 6 — RQ3 측정 개관: 13+ Method 비교

핵심 figure: `experiments/figures/rq3_supplementary/rq3_method_minus_bern_heatmap.png`

13 + 추가 코드 ready 16 method:

| Paradigm | Methods |
|----------|---------|
| Offline Cluster | MiniBatch, MiniBatch-partial, Spectral, BIRCH |
| Offline Curve/Hash | PCA-1D, Hilbert, Z-order, LSH, Random Projection |
| Tree | KD-tree |
| Industry Standard | Product Quantization (FAISS) |
| Hybrid | KMeans + Hilbert |
| Online | KDE-pilot, Distance-Shell |
| Weight (비분할) | Importance Sampling |

baseline: BERN, RANDOM20, KM20 oracle.

**Speaker note**: 측정 7 method + 코드 ready 6 method. 16 종합 doc 참조.

---

## Slide 7 — RQ3 핵심 contribution 1: Hilbert Curve = Learning-Free 1순위

수치:
- DEEP 1M: -1.78% (vs BERN), DEEP-best 빈도 94/500
- SIFT 1.5M: -2.47%, SIFT-best 빈도 106/500
- 학습 X, 결정론, ~수초 fit

Mechanism (W1-C 분석):
- inverse Manhattan = **1.000 (perfect 1D-2D continuity)** vs Z-order 1.992
- stratum compactness Z-order 대비 1.25-2.54× compact

핵심 figure: `experiments/figures/rq3_supplementary/curve_path_comparison.png`

**Speaker note**: \"learning-free + 결정론 stratification 도 oracle 수준 회수 가능\" — 본 연구의 1순위 contribution. 채림 석사 자문 사항.

---

## Slide 8 — RQ3 핵심 contribution 2: MiniBatch K-means = Production-Ready

수치:
- DEEP -1.88% / SIFT -1.97%, best 빈도 190/500
- 1% sample 학습, ~수초 fit
- partial_fit 으로 streaming 지원: ARI(batch, partial) = **1.000 (clustered) **

OLTP narrative:
- 데이터 점진 도착 → partial_fit() 호출 (10ms/chunk)
- batch 재학습 X, drift 모니터링 가능

**Speaker note**: 박세은 5/5 의문 \"OLTP 적용 가능?\" 직접 답변. ARI 1.000 의 결정적 evidence.

---

## Slide 9 — RQ3 핵심 contribution 3: Cluster 분할의 결정적 가치

핵심 figure: `experiments/figures/rq3_supplementary/rq3_cohens_d_forest_plot.png`

negative control 결과:
- **Distance-Shell** (cluster X, 거리 ranking 만): Cohen's d +0.490 (small-medium **hurt**)
- **Importance Sampling** (분할 X, weight 만): d +0.498 ~ +0.704 (small-medium hurt)
- LSH/Random Projection: d +0.156 ~ +0.216 (negligible-small hurt)

대비:
- Hilbert d = -0.156, MiniBatch d = -0.151 (negligible-small **improve**)

**Speaker note**: \"cluster-aware partition 자체가 가치\" 의 정량 증명. 부정 결과로 긍정 narrative 강화.

---

## Slide 10 — Honest Limitation: Effect Size 의 한계

수치:
- Hilbert / MiniBatch 의 mean Cohen's d = -0.15 (negligible-small range)
- Bootstrap CI 의 fraction_robust: Hilbert 4/10 cells, MiniBatch 5/10
- p ≤ 1e-13 (paired Wilcoxon) 하지만 sample size 효과 (n=500 paired)

honest narrative:
- \"meaningful but small improvement\"
- *어려운 query* 에서 method 차이 매우 큼 (spread vs difficulty ρ=0.78)
- → \"method routing\" 의 production 가치

핵심 figure: `experiments/figures/rq3_supplementary/rq3_per_query_difficulty_scatter.png`

**Speaker note**: 학술 발표의 robust narrative — p<0.05 만 보지 않고 effect size honest. 어려운 query 에서 method routing 가치.

---

## Slide 11 — Cross-Scale Validation: 8M Sensitivity

scope:
- DEEP 1M (이미 측정) → DEEP 8M (5/6 overnight 측정)
- 12 method × s={0.1, 0.3} × 5 seed × 100 query

기대:
- 1M 의 단조성 / Hilbert vs MiniBatch 양강 패턴 8M 에서 재현 → cross-scale robustness
- sample_size=385 의 8M 분모 회복 검증

**Speaker note**: 5/6 ~ 5/7 overnight 자동 측정 결과. 1M/1.5M 결과의 외적 타당성.

---

## Slide 12 — RQ 결과 종합 + Future Work

contributions:
1. RQ1: Selectivity gradient 단조성 통계 입증 (ρ=-0.680, CI 0 제외)
2. RQ2: KM20 oracle 의 sample-size robustness + Anti-Neyman 정량 hurt
3. RQ3-1: Hilbert curve = learning-free 1순위
4. RQ3-2: MiniBatch K-means = production-ready (partial_fit OLTP)
5. RQ3-3: Cluster 분할 자체의 결정적 가치 (Distance-Shell/IS negative control)

limitations:
- Single-table only
- KM20 oracle (production X) — sensitivity for trend 만
- Effect size 한계 — practical small

future work:
- 단일 → 멀티 테이블 (Exqutor multi-relation)
- vector.c integration
- Distribution shift 적응 (PCA basis 갱신)

**Speaker note**: 본 연구의 4 limitation 명시. 채림 석사 / 지도교수 자문 의견 반영.

---

## Slide 13 — 일정 + 산출

발표 / 보고서 / 전시:
- 5/27 (화) 최종 발표 — 본 슬라이드
- 5/28 전시회 자료
- 6/11 최종 보고서

산출 (오픈):
- GitHub: github.com/johyunbin/Capstone
- 16 method 코드 + 5 분석 + 8 figures + 종합 doc

**Speaker note**: 산출물 모두 GitHub 공개. 재현 가능.

---

## Slide 14 (선택) — Q&A buffer

예상 질문 + 답변:

**Q1**: \"왜 Hilbert curve 가 PCA-1D 보다 좋은가?\"
A: 1D-2D continuity 정량 (inverse Manhattan 1.000 vs ?). Z-order ablation 으로 입증.

**Q2**: \"Effect size 가 작은데 contribution 인정 받을 수 있나?\"
A: practical small + 어려운 query 에서 strong (spread 0.78). + Production 의 method routing.

**Q3**: \"Multi-table 일반화는?\"
A: 단일 정확성이 멀티의 *필요조건*. 멀티 일반화는 future work — Exqutor multi-relation framework 와 결합.

**Q4**: \"vector.c integration 안 한 이유?\"
A: 5/6 시도 → memory leak (메모 P5/M5). Python 시뮬레이션으로 우회 후 본질 검증. integration 은 future work.

**Q5**: \"산업 표준 (FAISS) 와의 비교는?\"
A: PQ (Product Quantization) 측정 ready (Slide 6). 결과 기반으로 5/27 보강.

---

## 슬라이드 제작 체크리스트

- [ ] PowerPoint 또는 LaTeX (TeXShop) 결정 (5/8 회의)
- [ ] figures 모두 PNG 300dpi 변환
- [ ] 한글 폰트 통일 (Apple SD Gothic Neo)
- [ ] 5/8 회의 narrative 합의 → outline 갱신
- [ ] 5/22 교수님 미팅 직전 draft 검토
- [ ] 5/26 마감 — final 검토

---

**작성**: 조현빈 · 2026-05-06 23:50 KST · 5/27 발표 D-21
