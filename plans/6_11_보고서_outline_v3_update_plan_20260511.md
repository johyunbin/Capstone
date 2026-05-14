# 6/11 최종 보고서 outline v2 → v3 update plan (5/11 paper exact 결과 반영)

> 작성: 2026-05-11 18:35 KST
> base: `plans/최종보고서_outline_v2_20260508.md` (5/8 시점, 8 section ~40p, 4 outcome narrative)
> 적용 시점: 5/29~6/10 sprint (W5~W6, 4 팀원 분담)
> 마감: 6/11 (목) — LearnUs 제출 + 캡스톤 홈페이지 게시

---

## 1. v2 → v3 핵심 변경 요약 (5/8 → 5/11 paper exact 결과 반영)

### 1.1 narrative 핵심 변경

| 영역 | v2 (5/8) | v3 (5/11) |
|---|---|---|
| §3 Methodology | 5 paradigm × 11 method | **9 paradigm × 56 method** (P9 InfoTheoretic + P10 Density 신규 + Phase 4 11 + Q4 6 + ★3 hilbert_real 추가) |
| §4 Results | RQ1 ρ=−0.680 / RQ2 40/40 cells / RQ3 4강 | **paper exact 재현 9 cells × 56 method × 2 modes (908 file, 80.4% coverage)** + **CaseB ensemble paired CaseB > CaseA 92.9%** + **Cliff's δ large better 63.5%** + **Hedges' g large 56.4%** |
| §4.4 Adaptive 비교 | 4 outcome 시나리오 (A/B/C/D) | **CaseA 단독 대체 무너짐 (one-sided BH 0/437) + CaseB ensemble climax** narrative — Outcome A/B framework 폐기 |
| §5 Discussion | 4강 (HDBSCAN / MB_partial / Hilbert / Hybrid) anchor | **paradigm rollup 9 paradigm 모두 통계 입증** anchor (P10 Density / P9 InfoTheoretic 신규 paradigm 최강) |
| §5.3 Limitation | L1~L13 (8 + V7 audit 5) | **L1~L18 (8 + 5 + 5 신규 5/11)**: drop 233 cells 9 카테고리 / RQ2 Neyman paradox / ★3 hilbert PCA alias / ★4 sparse_rp Li 2006 / byte-identical 7쌍 |
| §6 Conclusion + Future Work | 5 paradigm thesis 입증 | **9 paradigm + paper review-grade 검증 (Reproducibility 280/280 byte-identical) + RQ2 paradox honest finding** |
| §7 References | 25종 | **30종** (Phase 4 11 method canonical reference + RaBitQ VLDB 2024 + PRICE VLDB 2024 + LpBound SIGMOD 2025 + PDX SIGMOD 2025 + Bao et al. VLDB 2025) |

### 1.2 분량 변화 추정

| 영역 | v2 lines | v3 lines | Δ |
|---|---:|---:|---:|
| §3 Methodology | 50 | 70 | +20 (paradigm framework P9/P10 신규 + Phase 4/Q4 method) |
| §4 Results | 130 | 180 | +50 (CaseB ensemble climax + paradigm rollup 9 + Cliff's δ/Hedges' g 새 통계) |
| §5 Discussion | 90 | 120 | +30 (RQ2 paradox + 신규 limitation 5종) |
| §7 References | 25 | 35 | +10 (paradigm canonical reference 추가) |
| 전체 | ~430 | ~500 | +70 |

학교 양식 ~40p 유지 (v2와 동일, 본문 dense 화).

---

## 2. Section 별 주요 update 영역

### 2.1 §1 Introduction (3-4p, minor update)

- §1.3 연구 질문 RQ3 정의 update: "분포 모르면 어떤 방식이 최적?" → "분포 모르면 paper §V-B Bernoulli baseline 대비 분포 인지 stratification ensemble augment의 정량적 가치" 명확화
- §1.4 본 연구 contribution 7 → **9** (P9/P10 신규 paradigm 발굴 + ★3 hilbert defect rectify 학술 contribution + RQ2 Neyman paradox honest finding 추가)

### 2.2 §3 Methodology (5-6p → 6-7p, paradigm framework 확장)

- §3.1 paradigm framework: 5 paradigm → **9 paradigm** table (P1-P10, P7/P8 future work)
- §3.2 method registry: 11 method → **56 method** (Phase 4 11 + Q4 6 + extra 28 + Tier 1 11)
- §3.3 paper exact verbatim: paper Eq 1-6 + hyperparam (m=0.9, η₀=0.1, α=50, β=1.5, γ=0.99, period=50, N=385) + queries + threshold + trim 모두 verbatim 명시
- §3.4 CaseB ensemble 정의 (사용자 5/9 23:18 카톡 verbatim): `est_final = (est_b1 + est_method) / 2.0` simple average

### 2.3 §4 Results (12-14p → 14-16p, 핵심 영역)

- **§4.1 RQ1 paper exact**: DEEP/SIFT/SSN sf=100 mean gap **+3.74%** (Bernoulli vs KM20)
- **§4.2 RQ2 paper exact 5-way**: Bern→Prop **-9.53%** + Anti < Prop < Neyman paradox 발견 + σ_j range root cause
- **§4.3 RQ3 paper exact 9 paradigm × 56 method**: paradigm rollup table 새 추가
- **§4.4 Adaptive 비교 (CaseA vs CaseB)**: 4 outcome framework 폐기, 새 narrative
  - §4.4.1 CaseA 단독 대체 무너짐 (one-sided BH 0/437) + Cliff's δ worsening 36.8%
  - §4.4.2 CaseB ensemble climax (Cliff's δ large better 63.5%, Hedges' g large 56.4%, paired 92.9%)
  - §4.4.3 paradigm rollup 9 paradigm anchor: P10 -11.93 / P9 -10.22 / P3 -6.53 / P4 -5.92 / P2 -5.52 / P1 +0.17 / P5 +1.47 / P6 +1.49
  - §4.4.4 ★3 hilbert defect rectify 학술 contribution: PCA proxy locality (★3) vs 진짜 Hilbert (M6 zorder_morton + M7 skilling_hilbert + hilbert_real) 분리 검증
- **§4.5 측정 정합성 검증** (신규 sub): Reproducibility 280/280 byte-identical + Fig 12 영역 mean qe_trim 1.6180 / paper 1.69 (-4.26%) paper review-grade

### 2.4 §5 Discussion (4-5p, narrative 강화)

- §5.1 contribution 7 → **9** (P9/P10 신규 paradigm 발굴 + RQ2 Neyman paradox honest finding 추가)
- §5.2 학술 정합성 backbone: 25 → 30 reference (Phase 4 11 method + 2024-25 SIGMOD/VLDB 5종)
- §5.3 Limitation 8 → **18 (L1~L18)** — 5/11 신규 5건:
  - **L14**: 측정 미커버 233 cells (20.5%) 9 카테고리 정직 분류
  - **L15**: RQ2 Neyman/Anti paradox 발견 (σ_j range 1.3-1.6× narrow + N_i CV=0)
  - **L16**: ★3 hilbert PCA 2D lex sort alias (Faloutsos 1989 ❌ → pca2d_lex 정직 명명)
  - **L17**: byte-identical cells 7쌍 (A1-DEEP ≡ A5-sf100, A2-Fig9 ≡ A5-sf10 등)
  - **L18**: A4-sel sel=0.001 calibration parquet 부재 → D=0.86 fallback heuristic
- §5.4 Production 권고: CaseB ensemble augment 권고 (paper §V-B Bernoulli + KM20 stratified 산술 평균)

### 2.5 §6 Conclusion + Future Work (1-2p, 정정)

- §6.1 결론: 9 paradigm × 56 method paper exact 재현 + CaseB ensemble augment 정량 입증
- §6.2 Future work 우선순위 정정:
  1. **P7 Subspace clustering** (CLIQUE Agrawal 1998) — high-D subspace
  2. **P8 Graph-based** (Leiden Traag 2019, **Bao et al. VLDB 2025** Exqutor HNSW를 분포 정보 추출 용도 재활용) — 신규
  3. multi-table aware ensemble (단일 → 멀티 일반화)
  4. SF=100 cross-scale full validation (현재 80.4% coverage → 100% target)
  5. RQ2 σ range 큰 cluster imbalance 영역에서 Neyman 우위 재검증

### 2.6 §7 References (2-3p, +5종)

- Phase 4 11 method canonical: Chao 1982 / Grafström 2012 / Dalenius-Hodges 1959 / Lavallée-Hidiroglou 1988 / Jagadish 2005 / Morton 1966 / Skilling 2004 / Hyvärinen 1999 / Cochran 1977 + Neyman 1934 / Gao-Lin VLDB 2024
- Q4 6 method: Ester-Kriegel-Sander-Xu 1996 / Parzen 1962 / Poosala 1997 / Flajolet-Fusy-Gandouet-Meunier 2007 / Halko-Martinsson-Tropp 2011 / Matias-Vitter-Wang 1998
- 2024-25 SIGMOD/VLDB: PRICE Zeng 2024 / LpBound Zhang-Suciu SIGMOD 2025 / PDX SIGMOD 2025 / Bao et al. VLDB 2025
- ★3 hilbert defect rectify reference: Faloutsos 1989 (claim) vs PCA 2D lex sort (실제) — honest disclosure

---

## 3. 4 팀원 분담 정정 (5/29~6/10 sprint, v2 그대로)

| 팀원 | 영역 | v3 추가 작업 |
|---|---|---|
| 박세은 (팀장) | 통합 + Discussion + Front matter | RQ2 paradox + paradigm rollup 9 narrative 통합 |
| 조현빈 | §3 Methodology + §4.1 RQ1 + §4.5 측정 정합성 | paper exact verbatim + 9 paradigm framework + Reproducibility 검증 |
| 이동욱 | §2 Background + §4.2 RQ2 | Neyman paradox + σ_j range root cause 통계 |
| 강재현 | §4.3 RQ3 + §4.4 Adaptive 비교 | CaseB ensemble climax + paradigm rollup figure |

---

## 4. 측정 추가 필요성 평가 (5/27 발표 + 6/11 보고서 모두 반영)

### 4.1 본 세션 18:16 launch (★ Q4 80 measurement, ETA 21:30-22:00)

- P9 hyperloglog × 8 cells × 2 modes (currently 2/18) — paradigm rollup 9 cells 평균 신뢰성 ★
- P10 kde_parzen × 8 cells × 2 modes (currently 2/18) — paradigm rollup 9 cells 평균 신뢰성 ★
- P6 mhist2 / wavelet_hist × 8 cells × 2 modes — P6 rollup 신뢰성 (현재 +1.49%)
- P4 rsvd × 8 cells × 2 modes — P4 rollup 보강 (현재 -5.92%)

### 4.2 추가 검토 (보고서 보강용)

- A4-sel sel=0.001 정정 측정 (~6h) — fallback heuristic 정확 측정 (선택)
- Phase 4 M-series M1-M8/M10 cells coverage 점검 (M9/M11만 18/18) — paradigm anchor 보강
- multi-table A2-Fig8 multi-vector future work 명시 (paper §V-A scope 외)

### 4.3 폐기 (사용자 명시)

- ★1 hdbscan (sklearn KMeans fallback 등가, narrative anchor만 표기)
- A3-TPCDS ECQO mode (paper §V-A scope, PG segfault)
- 5/13 Adaptive×4강 일정 (사용자 5/11 02:14 폐기, "4강" framing 확정 X)

---

## 5. END

작성: 2026-05-11 18:35 KST  
다음 단계: Q4 extend 회수 → REPORT v9 + figures 재생성 → 5/15 박광현 미팅 narrative confirm → 5/29~6/10 W5~W6 sprint 4 팀원 분담 → 6/11 (목) LearnUs 제출

**핵심**: 본 plan은 5/29~6/10 sprint 시점 4 팀원 (박세은 통합 / 조현빈 §3+§4.1+§4.5 / 이동욱 §2+§4.2 / 강재현 §4.3+§4.4) 작업 가이드. v2 (5/8 시점) → v3 (5/11 시점) update의 영역별 정확 변경 사항 명시. 5/15 박광현 미팅 confirm 후 5/16~5/26 5/27 발표 deck update와 병행 진행.
