# 5/27 발표 deck slide-by-slide update plan (5/15 박광현 미팅 후 5/16~5/26 작업)

> 작성: 2026-05-11 18:05 KST  
> base: `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.{pdf,pptx}` (5/8 v3 Academic, 16 slide)  
> source: `submission/_drafts/archive/발표자료_v3_source_5월27일발표/academic-deck/Slides.jsx` (950 line, React JSX)  
> 적용 시점: **5/15 박광현 미팅 narrative confirm 후** (5/16~5/26)  
> 마감: 5/21 초안 / 5/26 최종 / **5/27 발표**

---

## 1. 정정 영역 (5/11 paper exact 측정 결과 반영 필수)

| # | slide | 5/8 narrative | 5/11 정정 narrative | 정정 강도 |
|---|---|---|---|:-:|
| **S6** | RQ1 진단 (단조성) | ρ=−0.680 DEEP-KM20 / ρ=−0.140 SIFT-KM20 (4/16 시점) | **+3.74% mean gap** (paper exact 5/11) — DEEP/SIFT/SSN sf=100 + DEEP sf=1/10 | 🟡 중 |
| **S7** | RQ2 distribution-aware | 40/40 cells + Anti-Neyman counterfactual | **Bern→Prop -9.53%** + **Anti 1.540 < Prop 1.580 < Neyman 1.595 paradox** (σ_j range 1.3-1.6× narrow + N_i CV=0 root cause) → "분포 알면 prop allocation 답" + RQ3 자연 전환 | 🔴 강 |
| **S8** | RQ3 4강 ranking + 10-cell heatmap | HDBSCAN -8.04 / MB_p -7.63 / Hilbert -7.54 / Hybrid -7.13 (5/8) | **9 paradigm × 56 method** → CaseB Cliff's δ large better **63.5%** + Hedges' g large **56.4%** + paradigm rollup P10 -11.93 / P9 -10.22 / P3 -6.53 / P4 -5.92 / P2 -5.36. **"4강" framing 폐기** (사용자 5/11 02:14 명시) | 🔴 강 |
| **S9** | ★ Contribution 1 — Hilbert | "production sweet spot" / Tier 1 spread 1.21%p | **★3 Hilbert PCA 2D lex sort alias** (Faloutsos 1989 ❌, 코드 line 449 `(\"hilbert\", \"pca2d_lex\") alias` 정직 명명) + **M6 zorder_morton + M7 skilling_hilbert + hilbert_real 3건 paradigm anchor** 추가 (Wikipedia xy2d 표준) | 🔴 강 |
| **S10** | ★ Contribution 2 — MiniBatch K-means | 1,189× speedup + ARI 1.000 | ★2 MB_partial CaseA -10.17% method-mean 그대로 (5/8 anchor) + CaseB ensemble augment 가치 추가 | 🟡 중 |
| **S11** | ★ Contribution 3 — Negative Control | +0.7 hurt-medium + Distance-Shell / IS bar | **CaseB ensemble climax** narrative — paper §V-B Bernoulli + 우리 method 산술 평균. CaseA 단독 대체 무너짐 (0/437 outperform) + CaseB ensemble 92.9% paired CaseB > CaseA | 🔴 강 |
| **S12** | Cross-scale Sensitivity | 1M → 8M heatmap (4/16 시점) | **A5-scale-sf{1, 10, 100} DEEP** paper exact 측정 완료 — Fig 12 영역 8 cells mean qe_trim 1.6180 / paper 1.69 (-4.26%) | 🟡 중 |
| **S13** | Mechanism — locality + redundancy | Hilbert vs Z-order + ARI matrix | **★3 hilbert + M6 zorder_morton + M7 skilling_hilbert + hilbert_real 4건 비교 anchor**. PCA proxy vs 진짜 Hilbert locality 분리 검증 학술 contribution 명시 | 🟡 중 |
| **S14** | Effect Size Honesty | DEFF 0.338 / ESS 2,325 / per-query routing ρ = 0.78 (4/16) | **CaseB Hedges' g large 56.4% (252/447)** + **Cliff's δ large better 63.5%** + sign test 71.8% p=3.1e-46. SSN++ ceiling 그대로 유지 (cluster_ratio 1.29 + intrinsic_dim 0.88) | 🔴 강 |
| **S15** | Limitation 8-card | L1-L8 (5/8) | **L6 정정**: "Effect size practical small" → "Cliff's δ large better 63.5% (paper review-grade)". **L9 신규**: "측정 미커버 233 cells (20.5%) 9 카테고리 정직 분류". **L10 신규**: "RQ2 Neyman/Anti paradox honest finding" | 🔴 강 |
| S16 | Closing | 감사합니다 / Q&A + GitHub + arXiv | (변경 X) | — |

---

## 2. 신규 figure 통합 (`experiments/figures/paper_exact_v7/`)

5/11 신규 6 figure를 발표 deck에 통합:

| Figure | 위치 | 통합 slide |
|---|---|---|
| F1 paradigm rollup CaseB | 5/27 storyline anchor | **S8 RQ3 ranking 대체** (9 paradigm bar) |
| F2 Cliff's δ bucket | CaseA worsening 36.8% vs CaseB better 63.5% (4.4×) | **S11 Negative Control 대체** |
| F3 CaseA vs CaseB violin | distribution comparison | **S14 Effect Size 추가** |
| F4 Top winners CaseB | Hedges' g top 5 | **S10 Contribution 2 update** |
| F5 Effect size scatter | Hedges' g × Cliff's δ 일관성 | **S14 Effect Size 대체** |
| F6 Narrative diagram | B1 → CaseA fail → CaseB climax | **S6 RQ1 진단 또는 S5 접근** |

⚠️ Korean font 적용 필요 (Apple SD Gothic Neo) — `_internal/scripts/figures_paper_exact.py` 5/11 18:00 update 완료 (`font.family` rcParams 적용). 재생성 시 자동 반영.

---

## 3. 신규 슬라이드 추가 검토 (선택적)

| 신규 slide 안 | 위치 | 내용 |
|---|---|---|
| **S6.5 Phase 4 11 method × 18 cells** | S6 후 | M9 kmeans_neyman / M11 idistance_neyman + RQ2 plug-in 직접 강화 narrative |
| **S10.5 CaseB ensemble climax** | S10 후 | paper §V-B Bernoulli + 우리 method 산술 평균 정의 + bias-variance trade-off |
| S15.5 Drop list 9 카테고리 | S15 후 | algorithm audit drop 23 / 자원 한계 / paper §V-A scope 외 / wrapper timeout 부재 / 사용자 결정 |

→ 16 slide → 18-19 slide 확장 검토. 단 12-15분 발표 시간 제약 고려 필요.

---

## 4. 변경 우선순위 (5/16~5/26 sprint)

### Phase 1 (5/16~5/18, 3일) — narrative 정정 강 영역
- S7/S8/S9/S11/S14/S15 6 slide 본문 + figure update
- F1/F2/F4/F5 4 figure 통합
- 5/15 박광현 미팅 confirm 사항 즉시 반영

### Phase 2 (5/19~5/21, 3일) — 신규 slide + minor 정정
- S6.5 + S10.5 신규 slide (선택)
- S6/S10/S12/S13 minor update
- 5/21 초안 마감 → 박세은 검토

### Phase 3 (5/22~5/26, 5일) — finalize + 리허설
- 박세은 검토 사항 반영
- F3/F6 figure 추가 통합
- 5/25~5/26 발표 리허설 (강재현)
- 5/26 최종 마감

---

## 5. 빌드 + 검증 명령

```bash
# Slides.jsx 수정 (React JSX)
cd /Users/hyunbin/Capstone/submission/_drafts/archive/발표자료_v3_source_5월27일발표/academic-deck/
# index.html을 브라우저에서 open → 16 slide preview
# print to PDF (Chrome) → submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.pdf

# Speaker notes update (index.html JSON 부분)

# figures Korean font 재생성
cd /Users/hyunbin/Capstone/_internal/scripts/
python3 figures_paper_exact.py --out-dir <server cache mirror> --fig-dir /Users/hyunbin/Capstone/experiments/figures/paper_exact_v7
```

---

## 6. END

작성: 2026-05-11 18:05 KST  
**핵심**: 5/15 박광현 미팅 confirm 사항이 deck update의 trigger. 정정 강 영역 6 slide (S7-S15)는 paper exact 5/11 결과 반드시 반영. 4강 framing 폐기 + paradigm rollup 9 카드 + CaseB ensemble climax narrative가 5/27 climax.
