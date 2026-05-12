# 박광현 교수님 5/15 (금) 14:00 미팅 자료

> **일시**: 2026-05-15 (금) 14:00 (D-4 from 5/11)  
> **장소**: 박광현 교수님 연구실 (BDAI, 위치는 박세은이 사전 확인)  
> **참석**: 박광현 교수님 / 박세은(팀장) / 강재현 / 조현빈 / 이동욱  
> **소요**: ~30분 (slide 2장 + Q&A)  
> **시간 확정**: 박세은 5/11 14:59 카톡 verbatim "이번주 금요일 5/15 14시 미팅 가능하시답니다"

---

## 📁 본 폴더 구성 (4 file)

| File | 용도 | 크기 |
|---|---|---:|
| `속도는벡터_박광현미팅_5월15일_slide_draft_20260511.{md,pdf}` | **2 slide 한국어 학술 산문** — slide 1 측정 정합성 + CaseB ensemble climax / slide 2 honest limitation 9 카테고리 + 5/27 storyline confirm 요청 / 부록 A~D + **부록 E 5/12 02:50 실측 update (REPORT v11, B1 9 + CaseA 495 + CaseB 496 = 1001 file 기준)** | 20 KB md / 670 KB PDF |
| `박광현_미팅_예상질문_답변_가이드_20260511.{md,pdf}` | **예상 질문 8건 + 답변 가이드** — paper §V-B 정합성 / CaseB ensemble 정의 / Hilbert 정정 / Limitation 카테고리 등 | 13 KB md / 384 KB PDF |
| `5_27_deck_update_plan_post_5월15일미팅.{md,pdf}` | **5/16~5/26 발표 deck update plan** — slide-by-slide 정정 영역 11종 + 신규 figures 통합 6건 + 신규 slide S6.5/S10.5/S15.5 검토 + Phase 1~3 sprint plan | 6.5 KB md / 417 KB PDF |
| `README.md` | 이 file | — |

---

## 🎯 미팅 narrative 핵심 (slide draft 기반)

### Slide 1 — 측정 완료 보고 (10분)

본 연구는 Exqutor 논문 §V-B Adaptive Sampling 영역에 대해 paper의 모든 hyperparam(m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / period=50 / N_init=385) + query + threshold + trim 정의를 verbatim 재현하였다. paper Fig 12 영역 8 cells mean trim Q-error는 **1.6180** (paper 1.69 대비 -4.26%, paper review-grade).

CaseB ensemble (paper §V-B Bernoulli + 우리 method KM20 stratified 산술 평균)이 paper baseline 대비 **(5/12 02:50 KST 실측 REPORT v11 기준, B1 9 + CaseA 495 + CaseB 496 = 1001 file)**:
- **Cliff's δ large better 63.0%** (311/494)
- **Hedges' g large 55.7%** (275/494)
- **one-sided p<0.05 outperform 45.3%** (224/494)
- **paired CaseB < CaseA 92.5%** (455/492, p < 1×10⁻⁴⁵)
- **negative control CaseA 단독 대체 0/493 = 0%** (large worsening 37.1%)

8 paradigm rollup CaseB (실측 mean Δ%, REPORT §7, outlier |Δ%|>100 제외):
- **P10 Density (KDE Parzen) ⚠**: **-11.93%** (n=1, paradigm anchor n 부족)
- **P9 InfoTheoretic (HyperLogLog)**: **-7.60%** (n=9, 5/11 18:48 회수 ✓, 5/9 cells signif p_adj<0.05) ★ paper review-grade
- **P3 Streaming**: **-6.63%** (n=44, chao_weighted + thompson_sampling)
- **P4 DimReduction**: **-6.03%** (n=104, sparse_rp + pca1d/cca1d/adaptive_bucket_probing + ica_fastica + tucker + rsvd + neuram)
- **P2 Spatial**: **-5.57%** (n=107, hilbert_real + zorder_morton + skilling_hilbert + idistance + lpm1_proper + lpm2)
- P5 QMC: +1.47% (n=62) — paradigm rollup 만 보고, 4 method (lhs/sobol/halton/hammersley) **정합성 위반 폐기**
- P1 Cluster: +2.04% (n=87, minibatch + minibatch_partial + kmeans_neyman + agglomerative 본 세션 추가)
- P6 Quantization: +8.44% (n=53, pq + opq 본 세션 추가 + rabitq_strat)

★ **5 paradigm 통계 압도** (P10/P9/P3/P4/P2). ⚠ paradigm anchor cell 부족. ✗ QMC method 4건 정합성 폐기 (paper N=385 budget 위반).

### Slide 2 — Honest Limitation Disclosure + 5/27 storyline confirm (10분)

본 연구는 측정 미커버 233 cells (20.5%)를 9 카테고리로 정직 분류한다. (1) algorithm audit drop 23 method, (2) 자원 한계 (birch CFNode tree 50-200GB RSS, A1-SSN 80GB NPY fetch 37-88분), (3) paper §V-A scope 외 (A2-Fig8 multi-vector, A3-TPCDS ECQO PG segfault), (4) wrapper timeout 부재, (5) 사용자 결정 (★1 hdbscan sklearn KMeans fallback 등가).

method-level 정직 disclosure 4건: ★3 hilbert (PCA 2D lex sort alias, Faloutsos 1989 ❌ → pca2d_lex 명명) + M6 zorder_morton + M7 skilling_hilbert + hilbert_real 4건 P2 paradigm anchor / ★4 sparse_rp (Achlioptas 2003 ❌ → Li-Hastie-Church 2006 ⭕) / RQ2 Anti < Prop < Neyman paradox (σ_j range 1.3-1.6× narrow + N_i CV=0 root cause) honest finding.

**미팅 confirm 요청 (부록 E 실측 update 반영)**:
1. **climax stat 92.5% / Cliff's δ 63.0% / negative control 0/493** — paper review-grade anchor 적절성
2. **paradigm rollup 8** — P5 QMC paradigm-level 만 보고 (method 4건 개별 폐기) 학술 정직성
3. **정합성 위반 9 method 폐기** — paper N=385 budget 위반 (final_size 폭증) 폐기 사유 충분성
4. **byte-identical duplicates 7쌍** (REPORT §11) — paradigm rollup caveat 표명
5. ★3 hilbert PCA alias + M6/M7/hilbert_real 4건 P2 Spatial paradigm anchor 명명
6. **사용자 정책: 측정 미커버 method 완전 폐기** (future work X) 학술 적절성

REPORT v11 (1362 line) full text + paired Δ% table + paradigm rollup 자료는 미팅 시 배포 (서버 `/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/REPORT_paper_exact.md` 또는 local `/tmp/REPORT_v11.md`).

---

## 🛠 미팅 직전 준비 (5/14~5/15)

| 작업 | 시점 | 상태 |
|---|---|---|
| ~~Q4 나머지 4 method 회수 + REPORT v9 재생성~~ → **사용자 정책 폐기** (측정 미커버 method 완전 배제, future work X) | — | ✓ 결정 (5/11 23:37) |
| 본 세션 18/18 회수 9 method (Tier 1 7 + Tier 3 2: agglomerative/vinecopula) + REPORT v11 회수 + slide draft 부록 E 추가 + PDF 재변환 | 5/12 02:45-11:56 | ✓ 완료 |
| 박세은 / 강재현 / 이동욱 검토 (카톡 공유) | 5/13~5/14 | ⏳ |
| 미팅 직전 자료 4 file 인쇄 또는 iPad 준비 (slide draft + 예상질문 + update plan + README) | 5/15 12:00 | ⏳ |
| 박세은 사전 인사 + 자리 안내 | 5/15 13:50 | ⏳ |

---

## 📅 미팅 후 (5/15 후 5/16~5/26)

미팅 confirm 결과를 다음 자료에 반영:
- `5_27_deck_update_plan_post_5월15일미팅.md` (Phase 1-3 sprint plan)
- **`submission/_drafts/속도는벡터 — Final 5_27 키노트.{pdf,pptx}` 5/27 발표 deck minor 정정** (5/12 morning claude.ai/design 새 conversation 으로 v2 FINAL 생성 예정 → `submission/_drafts/속도는벡터_5_27_키노트_prompt_v2_FINAL.md` 사용)
- `plans/5_27_storyline_draft_20260511_1410.md` storyline v2 → v3 (필요 시)
- `plans/6_11_보고서_outline_v3_update_plan_20260511.md` 6/11 보고서 plan minor update (5/29~6/10 sprint 가이드)

---

작성: 2026-05-11 18:55 KST  
**update**: 2026-05-12 12:15 KST (부록 E 5/12 02:50 실측 + 사용자 정책 측정 폐기 반영, climax stat 92.9% → 92.5% 동기화)  
다음: 5/13~5/14 박세은 검토 → 5/15 14:00 미팅 (D-3) → 5/27 19:00 최종 발표 (D-15)
