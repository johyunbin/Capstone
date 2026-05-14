# 6/11 보고서 §6 Conclusion + Future Work — 본문 sketch (5/11 19:35)

> **base**: `plans/6_11_보고서_outline_v3_update_plan_20260511.md` §2.5 §6
> **목적**: §6 1-2p 본문의 5/29~6/10 sprint 부담 ↓
> **owner**: 박세은 (통합)
> **분량**: ~1p (~25 line dense 학술 산문)

---

## §6 Conclusion + Future Work

### §6.1 결론 (한 단락 압축, 8-10 line)

본 연구는 Exqutor 논문 (arXiv:2512.09695v2) 의 §V-B Adaptive Sampling 영역에 대해 paper의 모든 hyperparam (m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N=385) + query 정의 + threshold + trim 통계를 verbatim 으로 재현하고 (Fig 12 영역 8 cells mean qe_trim 1.6180 vs paper 1.69, -4.26% 일치 + Reproducibility 280/280 byte-identical), 그 위에 우리 method의 KM20 stratified estimator를 산술 평균으로 ensemble augment하는 paper-friendly 구조의 정량적 가치를 9 cells × 56 method × 2 modes (918+ JSON file, coverage 80.4%+) 매트릭스로 검증하였다. CaseA 단독 대체 narrative는 paper §V-B 자체 robustness로 무너짐이 정확 입증되었으며 (one-sided BH-FDR 0/437 (0.0%) outperform + Cliff's δ large worsening 36.8% > better 14.4%), CaseB ensemble augment는 paired CaseB > CaseA 92.9% (404/435) + Cliff's δ large better 63.5% (284/447) + Hedges' g large 56.4% (252/447)로 통계 압도가 paper review-grade로 입증되었다. 9 paradigm rollup CaseB에서 P10 Density (KDE Parzen) -11.93% / P9 InfoTheoretic (HyperLogLog) -7.60% (9 cells × 5/9 signif p_adj<0.05) / P3 Streaming (Chao 1982) -6.53% / P4 DimReduction (sparse_rp ★4) -5.92% / P2 Spatial (★3 alias + M6/M7/hilbert_real 4건 anchor) -5.52%의 5 paradigm이 모두 ensemble 가치를 입증하며, ★3 hilbert defect rectify (PCA proxy locality vs 진짜 Hilbert 분리 검증) + RQ2 Anti<Prop<Neyman paradox honest finding (σ_j range 1.3-1.6× narrow + N_i CV=0 root cause)의 두 학술 contribution이 추가된다. 본 연구의 contribution은 paper §V-B 영역 한정이며, ECQO §V-A는 paper main result로 그대로 인정한다.

### §6.2 Future work 우선순위 8건 (10-12 line)

본 연구의 후속 연구 우선순위는 다음 8건이다.

1. **P7 Subspace clustering** (CLIQUE Agrawal 1998, *SIGMOD*) — high-D subspace clustering paradigm을 9 paradigm framework에 추가하여 cluster overlap 영역에서의 stratification 정합성 검증.

2. **P8 Graph-based** (Leiden Traag 2019 *Sci Rep* + **Bao et al. VLDB 2025** "HNSW로 분포 정보 추출 후 stratification 활용") — Exqutor §V-A의 HNSW 인덱스를 §V-B sampling step의 분포 정보 추출 용도로 재활용하는 cross-paradigm contribution.

3. **multi-table aware ensemble** — 단일 → 멀티 일반화 (joint-aware clustering / multi-vector decomposition / multi-table-join cross-correlation 인지). 본 연구의 단일 정확성 narrative가 multi 정확성의 *필요조건*만 성립하는 한계 극복.

4. **SF=100 cross-scale full validation** — 현재 80.4% coverage → 100% target. KernelDensity (P10) × SF=100 cells (4 cells × 2 modes = 8 measurement)는 본 세션 5/11 19:19 launch 후 며칠 long-running 진행 중 (사용자 명시 "오래걸리더라도 SF=100 시도").

5. **RQ2 σ range 큰 cluster imbalance 영역 Neyman 우위 재검증** — 본 연구의 RQ2 Neyman paradox honest finding (σ_j range 1.3-1.6× narrow boundary case)을 σ range 큰 영역 (예: PartSupp PK가 아닌 multi-modal distribution)에서 Neyman optimal allocation 우위 재현 검증.

6. **CaseB ensemble의 가중 평균 / query-conditional routing** — 본 연구는 산술 평균 (`(est1+est2)/2`)만 사용. 가중 평균 (`α·est1 + (1-α)·est2`) 또는 query-conditional cell × method routing이 추가 정확도 향상 검증.

7. **★3 hilbert defect rectify narrative의 paper acceptance 검증** — 본 연구가 5/10 발견한 ★3 hilbert PCA 2D lex sort alias가 paper review에서 acceptable narrative로 통과 가능한지, 또는 추가 algorithm audit 필요한지 5/15 박광현 교수님 + 박성원 멘토 자문 의견 반영.

8. **2024-25 SIGMOD/VLDB integration** (RaBitQ Gao-Lin VLDB 2024 / PRICE Zeng VLDB 2024 / LpBound Zhang-Suciu SIGMOD 2025 / PDX SIGMOD 2025 / Bao et al. VLDB 2025) — 최신 paper의 algorithm을 본 연구 9 paradigm framework에 integration하여 정합성 검증.

---

## 본 sketch 사용 가이드 (5/29~6/10 W5~W6 sprint, 박세은 통합)

1. §6.1 결론 한 단락은 그대로 학술 산문 형식 직접 사용 가능 (한국어, 영어 학술 용어 병기). 단락 분리 가능 (3-4개 sub-paragraph).
2. §6.2 Future work 8건은 5/15 박광현 미팅 + 5/16~5/20 박성원 멘토 자문 의견 반영 후 우선순위 minor 조정 가능
3. 5/27 발표 S15 Limitation slide와 본 §6.2 Future work는 narrative 일관성 유지
4. 본문 분량 ~1-2p (~25 line) — 학교 양식 적정

---

작성: 2026-05-11 19:35 KST  
다음: Q4 회수 후 §6.1 결론의 측정 portfolio 수치 update (918+ → ~988 file 또는 ~1000+) + 5/15 박광현 미팅 confirm 후 narrative 정합성 점검
