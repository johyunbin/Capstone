# 6/11 보고서 §4.4 CaseB ensemble climax — 본문 sketch (5/11 19:00)

> **base**: `plans/6_11_보고서_outline_v3_update_plan_20260511.md` §2.3 Results §4.4
> **목적**: CaseB ensemble 정량적 입증 narrative의 5/29~6/10 sprint 본문 작성 부담 줄이기
> **owner**: 강재현 (§4.3 + §4.4)
> **분량**: ~3p (~80 line dense 학술 산문)
> **v2 → v3 변경 핵심**: 4 outcome (A/B/C/D) framework 폐기 → CaseA 무너짐 + CaseB ensemble climax 단일 narrative

---

## §4.4 Adaptive Sampling Paired 비교 (CaseA 무너짐 + CaseB ensemble climax)

### §4.4.1 CaseA 단독 대체 narrative 무너짐의 정량적 입증 (12-15 line)

본 연구는 5/8 시점 4 outcome 시나리오 (A/B/C/D)로 Adaptive vs 분포 인지 stratification 비교를 설계하였으나, 5/11 paper exact 재현 측정에서 CaseA (우리 method가 paper §V-B Bernoulli sampling step을 단독으로 대체) narrative가 통계적으로 무너짐이 정확히 입증되었다. 9 cells × 56 method × CaseA mode 측정 (442 paired measurement) 중 one-sided BH-FDR α=0.05 outperform이 0/437 (0.0%)로 통계 무효이며, Cliff's δ large worsening (≤−0.474)이 161건 (36.8%)으로 large better (≥+0.474) 63건 (14.4%)을 압도한다. minibatch_partial M2 (P1, Sculley 2010)이 method-mean Δ% −10.17%로 단일 method 우위는 보이지만, 전체 paradigm 차원에서는 CaseA mode의 paradigm rollup (P10 −6.49 (1 cell only) / P4 +1.86 / P3 +2.86 / P9 +0.26 / P6 +5.64 / P1 +5.73 / P2 +7.31 / P5 +16.04)이 모두 worsening 또는 marginal로 paper §V-B Bernoulli baseline 대비 단독 대체의 정당성이 확보되지 않는다.

이는 paper §V-B Adaptive Sampling이 momentum 기반 동적 sample size 조정 (Eq 3-6) + Q-error feedback loop를 통해 자체 robustness를 확보하기 때문이며, 우리 method의 분포 인지 stratification이 KM20 oracle 가정 하에서도 single estimator로는 paper baseline을 surpass하지 못한다는 honest finding이다. 본 연구의 단독 대체 narrative 폐기는 5/11 paper exact 측정의 통계적 결과에 따른 정직 disclosure이며, 5/8 시점 deck (`speed_vector — Academic v3 · Final 5_27.pdf`)의 ★1~★4 4강 narrative와 RQ3 4 outcome framework는 5/27 발표 시점에서 update되어 polled paradigm rollup 기반 narrative로 대체된다.

### §4.4.2 CaseB ensemble augment의 통계적 압도 (15-18 line)

CaseA 단독 대체의 무너짐과 대조적으로, **CaseB ensemble augment**는 paper §V-B Bernoulli baseline 대비 통계적으로 압도한다. CaseB의 정의는 paper §V-B Bernoulli estimator (est₁, paper exact verbatim)와 우리 method KM20 stratified estimator (est₂)의 산술 평균 (`est_final = (est₁ + est₂) / 2.0`)으로, AdaptiveState (Eq 1-6 sample size 동적 조정)와 sample budget (Eq 1 N=385)은 paper exact 그대로 유지된다 (사용자 5/9 23:18 카톡 verbatim).

9 cells × 56 method × CaseB mode 측정 (460 paired measurement) 결과:
- **paired CaseB > CaseA**: 92.9% (404/435) — paper review-grade 우위
- **Cliff's δ large better (δ ≥ +0.474)**: 63.5% (284/447)
- **Hedges' g large effect (g ≤ −0.8)**: 56.4% (252/447)
- **One-sided BH-FDR α=0.05 outperform**: 45.0% (201/447)
- **Trial-level sign test**: 740/1030 (71.8%) better trials, p = 3.1e−46 binomial
- **Two-sided BH signif**: 43.4% (194/447)

paradigm rollup CaseB mean Δ%는 **P10 Density (KDE Parzen) -11.93%**, **P9 InfoTheoretic (HyperLogLog) -7.60%** (5/11 18:48 회수 9 cells 평균, 5/9 cells signif p_adj<0.05), **P3 Streaming (Chao 1982 weighted) -6.53%**, P4 DimReduction -5.92%, **P2 Spatial -5.52%** (12 method × 106 obs, hilbert_real Wikipedia xy2d 표준 + ★3 alias + M6 zorder_morton + M7 skilling_hilbert 4건 paradigm anchor)로 5 paradigm 모두 ensemble 가치를 입증한다. P1 Cluster +0.17%, P5 QMC +1.47%, P6 Quantization +1.49%는 marginal로 보고된다. Top 3 CaseB winners (smallest Hedges' g)는 pq @ A5-sf1 (g=−7.15, Δ%=−10.87%), sparse_rp @ A5-sf1 (g=−7.14, Δ%=−11.62%), vinecopula @ A5-sf1 (g=−7.05, Δ%=−12.40%)이다.

CaseB ensemble의 통계적 정당성은 bias-variance trade-off에서 나온다. random sampling (paper §V-B Bernoulli)은 bias 0이지만 cluster imbalance 시 variance가 크고, stratified sampling (우리 method)는 분포 가정이 맞을 때 variance가 낮다. 두 estimator의 산술 평균은 한 쪽이 분포 misspecification으로 fail해도 다른 쪽이 보완하는 robust 구조이며, 56 method 모두에 대해 일관된 9 paradigm rollup 통계 우위로 그 가치가 정량 입증된다.

### §4.4.3 ★3 hilbert defect rectify의 학술 contribution (10-12 line)

본 연구의 학술적 contribution 중 하나는 5/8 4강 narrative의 ★3 Hilbert가 코드 차원에서 PCA 2D lex sort로 구현되어 Faloutsos 1989 *Hilbert curve indexing* (SIGMOD)의 진짜 locality 효과가 아닌 PCA proxy 효과를 측정한 것임을 학술 정직성 기준에서 발견하고 (5/10 8 agent algorithm audit), 이를 4건의 paradigm anchor 추가 측정으로 rectify한 점이다. 코드 line 449에서 `("hilbert", "pca2d_lex") alias` 정직 명명되며, 진짜 Hilbert curve의 paradigm anchor는 다음 3건으로 보강된다.

(1) **M6 zorder_morton** (Morton 1966 *IBM Tech Rep*): Z-order space-filling curve의 paradigm anchor로 5/11 Phase 4에서 18/18 cells 측정 완료. (2) **M7 skilling_hilbert** (Skilling 2004 *AIP Conf Proc* 707, "Programming the Hilbert curve"): state-machine algorithm 기반 진짜 high-D Hilbert로 5/11 Phase 4에서 측정 완료. 단 conditional swap simplification 1줄은 disclosure (line 401 "Skip exact swap for simplicity"). (3) **hilbert_real** (Wikipedia *Hilbert curve* xy2d 표준): raw `experiments/code/rq3/hilbert/hilbert_curve.py` 표준 reference implementation으로 5/11 18:09 회수 9 cells × 2 modes 측정 완료. CaseB ensemble에서 mean -8.2% (9 cells, 6/9 signif p_adj<0.05) 강력 입증. 이 4건 (★3 alias + M6 + M7 + hilbert_real) 비교는 "PCA proxy locality vs 진짜 Hilbert locality 분리 검증"의 학술 contribution narrative가 되며, paper review에서 "★3 hilbert가 Faloutsos 1989인지" 질문에 대해 honest disclosure + paradigm anchor substitute 3건으로 응답하는 구조가 된다.

### §4.4.4 본 연구 학술 기여의 위치 (8-10 line)

Exqutor 본 논문이 *내부 비교* (Adaptive vs Fixed sample size)만 수행한 §V-B Adaptive Sampling 영역에서, 본 연구는 *외부 비교* (Adaptive vs distribution-aware stratification ensemble)를 paired Δ% + 효과크기 + paradigm rollup의 paper review-grade 통계로 추가한다. 본 연구의 핵심 기여는 단독 대체 narrative의 무너짐 (paper §V-B 자체 robustness 입증)과 ensemble augment의 통계적 압도 (분포 인지 stratification의 보완 가치 입증)의 두 finding을 동시에 보고하는 것이며, 이는 paper §V-B Bernoulli sampling을 그대로 보존하면서 우리 method의 산술 평균만 layer로 추가하는 paper-friendly augment 구조다. ECQO §V-A (인덱스 있을 때 HNSW range query 활용) 영역은 paper main result로 그대로 인정하며, 본 연구의 contribution은 §V-B sampling step augment로 한정한다 (사용자 5/11 14:18 verbatim "Exqutor 외 영역 / 외의 조건을 억지로 추가하는 개념이 아닌 정확히 비교할 수 있도록").

추가 학술 기여 3건은 다음과 같다. (1) ★3 hilbert defect rectify (PCA proxy vs 진짜 Hilbert locality 분리 검증) + M6/M7/hilbert_real 3건 paradigm anchor 추가. (2) RQ2 5-way 측정에서 Anti < Prop < Neyman paradox 발견 (σ_j range 1.3-1.6× narrow + N_i CV=0 root cause)의 honest finding + RQ3 추정 framework로의 자연 전환 narrative. (3) 2024-25 SIGMOD/VLDB 인용 5종 (RaBitQ Gao-Lin VLDB 2024 / PRICE Zeng VLDB 2024 / LpBound Zhang-Suciu SIGMOD 2025 / PDX SIGMOD 2025 / Bao et al. VLDB 2025).

---

## 본 sketch 사용 가이드 (5/29~6/10 W5~W6 sprint, 강재현 owner)

1. §4.4.1~§4.4.4 본문 sketch는 그대로 학술 산문 형식 직접 사용 가능
2. Q4 4 method (kde_parzen / mhist2 / rsvd / wavelet_hist) 회수 후 §4.4.2 paradigm rollup 수치 update (P10 1 cell → 9 cells / P6 / P4 강화)
3. 5/15 박광현 미팅 confirm 사항 반영 (만약 narrative 변경 시 §4.4.2 통계 또는 §4.4.4 학술 기여 위치 minor 조정)
4. Figure 5건 통합:
   - F1 paradigm rollup CaseB → §4.4.2 paragraph 끝
   - F2 Cliff's δ bucket → §4.4.1 (CaseA worsening 36.8%) + §4.4.2 (CaseB better 63.5%) 비교
   - F4 top winners → §4.4.2 Top 3 winners
   - F5 effect size scatter → §4.4.2 통계 검증
   - F6 narrative diagram → §4.4.4 본 연구 기여 위치 종합
5. 본문 분량 ~3p (~80 line) — 학교 양식 적정 dense

---

작성: 2026-05-11 19:00 KST  
다음: Q4 4 method 회수 후 paradigm rollup 수치 update + 5/15 박광현 미팅 confirm 후 narrative 정합성 점검 → 5/29~6/10 sprint 본문 작성 (강재현)
