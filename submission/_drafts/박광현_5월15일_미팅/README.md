# 박광현 교수님 5/15 (금) 14:00 미팅 자료

> **일시**: 2026-05-15 (금) 14:00 (D-4 from 5/11)  
> **장소**: 박광현 교수님 연구실 (BDAI, 위치는 박세은이 사전 확인)  
> **참석**: 박광현 교수님 / 박세은(팀장) / 강재현 / 조현빈 / 이동욱  
> **소요**: ~30분 (slide 2장 + Q&A)  
> **시간 확정**: 박세은 5/11 14:59 카톡 verbatim "이번주 금요일 5/15 14시 미팅 가능하시답니다"

---

## 📁 본 폴더 구성 (3 file)

| File | 용도 | 크기 |
|---|---|---:|
| `속도는벡터_박광현미팅_5월15일_slide_draft_20260511.{md,pdf}` | **2 slide 한국어 학술 산문** — slide 1 측정 정합성 + CaseB ensemble climax / slide 2 honest limitation 9 카테고리 + 5/27 storyline confirm 요청 / 부록 A 측정 portfolio + 부록 B paradigm rollup + 부록 C ★3 hilbert defect rectify + 부록 D P9 InfoTheoretic 강화 | 12 KB md / 520 KB PDF |
| `5_27_deck_update_plan_post_5월15일미팅.{md,pdf}` | **5/16~5/26 발표 deck update plan** — slide-by-slide 정정 영역 11종 + 신규 figures 통합 6건 + 신규 slide S6.5/S10.5/S15.5 검토 + Phase 1~3 sprint plan | 6.5 KB md / 417 KB PDF |
| `README.md` | 이 file | — |

---

## 🎯 미팅 narrative 핵심 (slide draft 기반)

### Slide 1 — 측정 완료 보고 (10분)

본 연구는 Exqutor 논문 §V-B Adaptive Sampling 영역에 대해 paper의 모든 hyperparam(m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N_init=385) + query + threshold + trim 정의를 verbatim 재현하였다. paper Fig 12 영역 8 cells mean trim Q-error는 **1.6180** (paper 1.69 대비 -4.26%, paper review-grade).

CaseB ensemble (paper §V-B Bernoulli + 우리 method KM20 stratified 산술 평균)이 paper baseline 대비:
- **Cliff's δ large better 63.5%** (284/447)
- **Hedges' g large 56.4%** (252/447)
- **paired CaseB > CaseA 92.9%** (404/435)

9 paradigm rollup CaseB:
- **P10 Density (KDE Parzen)**: -11.93% (1 cell, 본 세션 5/11 18:16 launch 8 cells 추가 진행 중 → 회수 후 9 cells 평균으로 강화 예정)
- **P9 InfoTheoretic (HyperLogLog)**: **-7.60% mean (9 cells, 5/11 18:48 회수 ✓, 5/9 cells signif p_adj<0.05)** ★ paper review-grade
- P3 Streaming (Chao 1982): -6.53%
- P4 DimReduction: -5.92%
- **P2 Spatial**: **-5.52% (12 method × 106 obs, hilbert_real 9 cells × 2 modes 5/11 18:09 회수 ✓ + ★3 alias rename + M6/M7 paradigm anchor 추가)** ★

### Slide 2 — Honest Limitation Disclosure + 5/27 storyline confirm (10분)

본 연구는 측정 미커버 233 cells (20.5%)를 9 카테고리로 정직 분류한다. (1) algorithm audit drop 23 method, (2) 자원 한계 (birch CFNode tree 50-200GB RSS, A1-SSN 80GB NPY fetch 37-88분), (3) paper §V-A scope 외 (A2-Fig8 multi-vector, A3-TPCDS ECQO PG segfault), (4) wrapper timeout 부재, (5) 사용자 결정 (★1 hdbscan sklearn KMeans fallback 등가).

method-level 정직 disclosure 4건: ★3 hilbert (PCA 2D lex sort alias, Faloutsos 1989 ❌ → pca2d_lex 명명) + M6 zorder_morton + M7 skilling_hilbert + hilbert_real 4건 P2 paradigm anchor / ★4 sparse_rp (Achlioptas 2003 ❌ → Li-Hastie-Church 2006 ⭕) / RQ2 Anti < Prop < Neyman paradox (σ_j range 1.3-1.6× narrow + N_i CV=0 root cause) honest finding.

**미팅 confirm 요청 4건**:
1. 7단계 storyline narrative 적절성 (paper §V-B 영역 한정)
2. drop 233 cells 9 카테고리 disclosure 충분성
3. ★3 hilbert PCA alias + M6/M7/hilbert_real 4건 paradigm anchor
4. P7 Subspace (CLIQUE 1998) + P8 Graph-based (Leiden 2019, **Bao et al. VLDB 2025** Exqutor HNSW 분포 정보 추출 재활용) future work

---

## 🛠 미팅 직전 준비 (5/14~5/15)

| 작업 | 시점 |
|---|---|
| Q4 나머지 4 method (kde_parzen / mhist2 / rsvd / wavelet_hist) 회수 + REPORT v9 + figures 재생성 + slide PDF 재변환 | 5/12 morning |
| 부록 B/D 수치 update (P10/P6/P4 강화) | 5/12 |
| 박세은 / 강재현 / 이동욱 검토 (카톡 공유) | 5/13~5/14 |
| 미팅 직전 figures 6건 + slide PDF 인쇄 또는 iPad 준비 | 5/15 12:00 |
| 박세은 사전 인사 + 자리 안내 | 5/15 13:50 |

---

## 📅 미팅 후 (5/15 후 5/16~5/26)

미팅 confirm 결과를 다음 자료에 반영:
- `5_27_deck_update_plan_post_5월15일미팅.md` (Phase 1-3 sprint plan)
- `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.{pdf,pptx}` 5/27 발표 deck update
- `plans/5_27_storyline_draft_20260511_1410.md` storyline v2 → v3 (필요 시)
- `plans/6_11_보고서_outline_v3_update_plan_20260511.md` 6/11 보고서 plan minor update (5/29~6/10 sprint 가이드)

---

작성: 2026-05-11 18:55 KST  
다음: 5/12 morning Q4 회수 + slide PDF 재변환 → 5/13~5/14 박세은 검토 → 5/15 14:00 미팅
