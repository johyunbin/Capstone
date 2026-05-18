# 통계 보완 — REPORT v12 §9 항목 (7) 4건 재집계

_생성_: 2026-05-17

_출처_: `_internal/cache/rq3/paired_delta_v12.parquet` (paired 1360행) · `_internal/cache/rq3/aggregated_v12_full.parquet` (측정 1444건). 모든 수치는 두 parquet 직접 재계산값이며, REPORT v12 텍스트와 대조했으나 이전 텍스트를 출처로 신뢰하지 않았다.

_재계산 스크립트_: `_internal/cache/rq3/stats_supplement_v12_compute.py` · 검증 파생물: `stats_supplement_v12_detail.parquet`, `stats_supplement_v12_summary.json`, `stats_supplement_v12_percell.csv`

---

## 0. 이 문서가 보완하는 것

REPORT v12 §9 항목 (7)은 본 보고서 통계 처리의 네 가지 한계를 명시했다 — (a) BH-FDR 다중검정 보정의 family 크기, (b) 효과크기 공식의 독립표본 가정, (c) Wilcoxon 검정의 p값 해상도, (d) 집계 가중의 선택. 본 문서는 이 네 가지를 paired_delta_v12.parquet에서 직접 재계산하여 정량화한다.

분석 단위는 REPORT v12 headline과 동일하다. **headline 비교 가능 수치는 K=10 paired 120건을 제외한 1240건**을 쓴다 — K=10 대조군 B1이 strata 의존 결함으로 손상되었기 때문이다 (REPORT v12 §2.3). K=10 포함 전체 1360건 수치는 각 항목에서 별도 라벨을 붙여 병기한다.

먼저 headline 기준값을 parquet에서 재확인했다. K=10 제외 1240건에서 CaseB better(Δ%<0)는 1143건 = **92.18%**, 평균 Δ% **−6.2452%**, 중앙값 **−6.1483%** — REPORT v12 §3.1의 92.2%/−6.25%/−6.15%와 완전 일치한다.

**결론 먼저**: 네 보완 모두 REPORT v12의 headline 결론(약 9할 비교에서 −6% 안팎 Q-error 개선, 견고한 우월)을 **바꾸지 않는다**. 가장 큰 변동은 (d) cell-weighted로, better 비율이 92.18% → 90.61%로 1.57%p 내려간다 — REPORT v12 §9가 예고한 "90.6%·−6.00%"와 정확히 일치한다.

---

## (a) BH-FDR 다중검정 보정 — family 분할 재집계

### 문제

REPORT v12는 paired 비교 전체를 **단일 검정 family**로 묶어 Benjamini-Hochberg FDR을 적용했다. 이질적인 cell·method를 한 family로 합치면 비교 개수 n이 커지고, BH 보정량(p_adj = p × n / rank)이 그만큼 커져 over-correction 경향이 생긴다. §9는 이 때문에 유의 우월 비율(78.3%)이 다소 보수적으로 추정된다고 적었다.

### 재집계 방법

one-sided greater Wilcoxon p값(H1: B1 > CaseB, 즉 CaseB가 더 정확)에 대해 family를 네 가지로 나눠 BH-FDR을 각각 적용하고, "better(Δ%<0)이면서 p_adj<0.05"인 비교 수를 셌다. BH 구현은 `analyze_paper_exact.py`의 `bh_fdr`와 동일하다 (단조 비감소 제약 포함).

### 결과 — HEADLINE (K=10 제외, n=1240)

| family 분할 | family 수 | 유의 우월 (better & p_adj<0.05) | 비율 |
|---|---:|---:|---:|
| raw (보정 없음) | — | 991 / 1240 | 79.9% |
| 단일 family (현행 REPORT) | 1 | 971 / 1240 | **78.3%** |
| cell별 | 24 | 961 / 1240 | 77.5% |
| method별 | 16 | 975 / 1240 | 78.6% |
| (cell, method)별 | 384 | 973 / 1240 | 78.5% |

### 결과 — FULL (K=10 포함, n=1360, 참고)

| family 분할 | family 수 | 유의 우월 | 비율 |
|---|---:|---:|---:|
| raw (보정 없음) | — | 1091 / 1360 | 80.2% |
| 단일 family (현행) | 1 | 1071 / 1360 | 78.8% |
| cell별 | 24 | 1060 / 1360 | 77.9% |
| method별 | 16 | 1078 / 1360 | 79.3% |
| (cell, method)별 | 384 | 1073 / 1360 | 78.9% |

### 해석

family를 어떻게 나누든 유의 우월 비율은 **77.5% ~ 78.6% 사이**에 머문다. 단일 family(78.3%)와 다른 분할의 최대 차이는 method별 분할의 +0.3%p, cell별 분할의 −0.8%p로, 모두 1%p 미만이다.

§9가 우려한 over-correction은 사실상 존재하지 않는다. 그 이유는 (c)에서 드러난다 — 비교의 절반 이상이 p값 바닥값(1/1024)에 몰려 있어, BH 보정 후에도 p_adj가 0.05를 넉넉히 밑돈다. family 크기가 n=1240이든 n=16이든, 바닥값 비교는 보정 뒤에도 유의하게 남는다. 흥미롭게도 cell별 분할이 단일 family보다 **더 보수적**(77.5%)인데, 이는 일부 cell(A4-sel, A10-DEEP+WIKI-concat-sf10)에 약한 비교가 집중되어 그 작은 family 안에서 rank 효과가 불리하게 작동하기 때문이다. 즉 family 분할은 "유의 비율을 올려준다"는 단순한 방향성을 갖지 않는다.

**REPORT v12 §3.1의 "유의 우월 78.3%"는 family 분할 방식에 거의 무관하게 안정적이며, 결론을 바꾸지 않는다.**

---

## (b) 효과크기 — paired 설계용 재계산

### 문제

REPORT v12가 보고한 Cliff's δ와 Hedges' g는 **독립표본(independent-sample) 공식**으로 계산되었다. Cliff's δ는 B1 10개 trial과 CaseB 10개 trial의 모든 100쌍(10×10)을 교차 비교했고, Hedges' g는 두 집단을 독립으로 보는 pooled-SD를 분모로 썼다. 그러나 실제 B1–CaseB 비교는 **같은 trial 인덱스를 짝지은 paired 설계**다 (같은 sample budget·같은 측정 run). paired 설계의 trial 간 상관을 반영하지 못하므로 §9는 보고된 effect size가 보수적이라고 적었다.

### 재계산 방법

같은 1360건의 trial qe 리스트(B1 10개, CaseB 10개)를 aggregated parquet에서 재구성하여(`build_paired_trials`), 세 가지 effect size를 다시 계산했다.

- **Cliff's δ (paired)**: 같은 trial 인덱스끼리만 비교 — δ = (#{b1ᵢ>caᵢ} − #{b1ᵢ<caᵢ}) / n. n=10쌍. POSITIVE = CaseB 우위.
- **Hedges' g_av (paired)**: Lakens(2013)의 d_av — diff 평균 / pooled_sd, pooled_sd = √((sd_b1² + sd_ca²)/2). effect-size 단위를 raw SD로 유지해 독립표본 g와 직접 비교 가능. 소표본 보정 J는 paired df = n−1 기준. NEGATIVE = CaseB 우위.
- **Hedges' g_rm (paired, 참고)**: d_rm = d_av × √(2(1−r)), r = trial 간 Pearson 상관. 상관 보정판으로 참고 병기.

### 결과 — HEADLINE (K=10 제외, n=1240)

| 효과크기 | 공식 | large 임계 우월 | mean |
|---|---|---:|---:|
| Cliff's δ | 독립표본 (현행 REPORT) | 1023 / 1240 = **82.5%** | +0.7318 |
| Cliff's δ | paired (재계산) | 996 / 1240 = **80.3%** | +0.7294 |
| Hedges' g | 독립표본 (현행 REPORT) | 1039 / 1240 = **83.8%** | −6.382 |
| Hedges' g | paired g_av (재계산) | 1032 / 1240 = **83.2%** | −6.093 |
| Hedges' g | paired g_rm (상관 보정, 참고) | 1107 / 1240 = 89.3% | −8.567 |

paired Cliff's δ의 강도 분포 (large 임계 0.474 / medium 0.330 / small 0.147): large 996 · medium 81 · small 58 · negligible 33 · (음수 72). paired δ가 정확히 +1.0(10쌍 전부 CaseB 우위)인 비교가 652건이다.

trial 간 Pearson 상관 r: 평균 **−0.013**, 중앙값 −0.019, 범위 [−0.876, +0.842].

### 결과 — FULL (K=10 포함, n=1360, 참고)

| 효과크기 | 공식 | large 우월 | — |
|---|---|---:|---|
| Cliff's δ | 독립표본 | 1126 / 1360 = 82.8% | — |
| Cliff's δ | paired | 1097 / 1360 = 80.7% | — |
| Hedges' g | 독립표본 | 1156 / 1360 = 85.0% | — |
| Hedges' g | paired g_av | 1147 / 1360 = 84.3% | — |

### 해석

§9는 paired 공식이 "trial 간 상관을 반영하여 더 큰(덜 보수적인) effect size를 줄 것"이라고 예고했으나, **실측 결과는 그 예고와 다르다.** 핵심 원인은 trial 간 상관이 0에 가깝다는 점이다 — Pearson r 평균 −0.013, 중앙값 −0.019. B1과 CaseB의 10 trial qe는 사실상 무상관이다. 같은 측정 run 안에서 짝지었어도, 두 추정기가 쓰는 sample selection 방식이 달라 trial별 변동이 동조하지 않기 때문이다.

상관이 0이면 paired 공식과 독립표본 공식이 거의 같은 값을 준다. 그래서:

- **Cliff's δ**: paired(80.3%)가 독립표본(82.5%)보다 오히려 2.2%p 낮다. paired δ는 100쌍이 아닌 10쌍만 보므로 해상도가 거칠어(가능 값이 −1.0, −0.8, …, +1.0의 11단계뿐), large 임계(0.474) 부근에서 일부 비교가 임계 아래로 떨어진다. 즉 paired δ는 "더 정직하지만 더 거친" 추정이다.
- **Hedges' g_av**: paired(83.2%)가 독립표본(83.8%)과 0.6%p 차이로 사실상 동일하다. mean도 −6.38 vs −6.09로 근접한다.
- **g_rm(상관 보정)**: 89.3%로 더 커 보이나, 이는 r이 음수일 때 √(2(1−r)) > √2가 되어 effect를 부풀리는 산식 특성이다. r이 0 근처에서 잡음으로 음수가 되면 g_rm이 과대평가되므로 참고치로만 본다 — g_av가 paired 설계의 주 보고치로 적절하다.

**핵심**: trial 간 상관이 0이라는 사실 자체가 중요한 발견이다. paired 설계라 해서 effect size가 더 커지지 않으며, REPORT v12가 독립표본 공식으로 보고한 Cliff's δ large 82.5%·Hedges' g large 83.8%는 paired 공식으로도 80~83%대로 유지된다 — "효과크기 large 우월 8할 전후"라는 결론은 바뀌지 않는다. §9가 "보수적 추정"이라 적은 것은 정정이 필요하다: 보수적이지 않고, 두 공식이 거의 일치한다.

---

## (c) Wilcoxon p값 해상도 — n=10 floor 정량화

### 문제

paired 비교는 cell·method·sel·K마다 trial n=10으로 수행되었다. n=10 paired 표본에서 exact Wilcoxon signed-rank 검정이 도달할 수 있는 최소 p값은 정해져 있다 — 10개 차이가 모두 같은 부호일 때다.

- **one-sided** 최소 p = 1/2¹⁰ = 1/1024 = **0.0009766**
- **two-sided** 최소 p = 2/1024 = 0.0019531

(scipy `wilcoxon(method='exact')`로 직접 확인: 10 trial 전부 동일 부호 → one-sided greater p = 0.00097656.)

또한 n=10에서 exact Wilcoxon이 만들 수 있는 **고유 p값은 56개**뿐이다 (signed-rank 통계량의 이산 분포, scipy 20k 무작위 표본으로 확인). 효과가 강한 비교들은 모두 바닥값 한 점에 겹쳐, 그들 사이의 미세한 우열은 p값으로 분해되지 않는다.

### 정량화 — HEADLINE (K=10 제외, n=1240)

| 항목 | 값 |
|---|---|
| one-sided greater p값이 바닥(1/1024)에 도달 | 652 / 1240 = **52.6%** |
| ─ 그 중 better(Δ%<0) | 652 / 1240 = 52.6% (전부) |
| two-sided p값이 바닥(2/1024)에 도달 | 667 / 1240 = 53.8% |
| 실제 관측된 고유 one-sided p값 개수 | 51 (이론상 가능 56) |
| 실제 관측된 고유 two-sided p값 개수 | 28 |

one-sided greater p값 분포 (HEADLINE 1240):

| p값 구간 | 비교 수 | 비율 |
|---|---:|---:|
| 바닥값 ≈ 0.001 | 652 | 52.6% |
| (0.001, 0.01] | 240 | 19.4% |
| (0.01, 0.05] | 99 | 8.0% |
| (0.05, 0.1] | 56 | 4.5% |
| (0.1, 0.5] | 110 | 8.9% |
| (0.5, 1] | 83 | 6.7% |

### 정량화 — FULL (K=10 포함, n=1360, 참고)

one-sided greater 바닥 도달 **746 / 1360 = 54.9%**, two-sided 바닥 768/1360 = 56.5%, 고유 one-sided p값 52개. REPORT v12 §9가 "paired 1360건 중 746건이 바닥값에 몰려 있다"고 적은 수치는 이 FULL one-sided greater 바닥 도달 수와 정확히 일치한다 — 검증 통과.

### 해석

n=10 설계의 직접 귀결이다. headline 1240건의 **절반 이상(52.6%)이 one-sided p값 바닥값 한 점에 겹쳐 있다.** 1240건이 만든 고유 p값은 51개뿐으로, 이론 가능치 56개에 근접한다 — 검정 통계량 자체가 거의 다 쓰였다는 뜻이다.

이것이 분석에 주는 함의는 둘이다. 첫째, **바닥값에 몰린 652건은 "더 강한지 덜 강한지" p값으로 구분되지 않는다.** A5-scale-sf1-SIFT의 −34.96% 비교와 다른 cell의 −8% 비교가 똑같이 p=0.001을 받는다 — 우열 판단은 p값이 아니라 Δ%와 effect size(b 항목)로 해야 한다. 이것이 본 보고서가 Δ%·Cliff's δ·Hedges' g를 함께 보고하는 이유의 정당화다. 둘째, **n=10은 통계적 유의성을 "있다/없다"로만 판별할 뿐, 강도의 미세 분해에는 부적합하다.** trial 수를 늘리면(예: n=30) p값 해상도가 1/2³⁰까지 깊어져 강한 비교들의 우열이 분해되겠지만, 본 보고서의 결론(약 9할이 유의하게 우월)에는 영향이 없다 — 이미 절반 이상이 도달 가능한 최소 p값을 찍었기 때문이다.

**REPORT v12의 통계적 유의 우월 비율(78.3%)은 견고하다.** 다만 그 78.3%는 "78.3%가 강하게 유의하고 나머지는 약하게 유의하다"가 아니라, "52.6%가 도달 가능한 최저 p값을 찍고, 25.8%p가 추가로 0.05를 통과하며, 약 21.7%는 유의하지 않다"는 구조다. 이 구조 자체가 결론을 바꾸지는 않으나, 발표·보고서에서 "유의성"을 강조할 때 n=10의 해상도 한계를 함께 명시하는 것이 정직하다.

---

## (d) cell-weighted 재집계

### 문제

REPORT v12 headline의 92.2%·−6.25%는 **file-weighted** 집계다 — 측정 file(= paired 비교) 한 건마다 동일 가중을 준다. 측정 file 수가 많은 cell이 평균을 더 끌어간다. cell마다 측정 file 수가 다르므로(A1-SIFT 96건 vs A4-sel 16건), 집계 가중에 따라 headline 수치가 달라진다.

### 재집계 방법

같은 1240건(K=10 제외)을 두 방식으로 집계했다.

- **file-weighted (현행)**: 1240개 paired 비교를 동일 가중 → better 비율·평균·중앙값.
- **cell-weighted**: 24개 cell 각각에서 먼저 better 비율·평균·중앙값을 구하고, 그 24개 cell 통계를 동일 가중으로 평균.

### 결과 — HEADLINE (K=10 제외, n=1240, cell 24개)

| 지표 | file-weighted (현행) | cell-weighted | 차이 (cell − file) |
|---|---:|---:|---:|
| better 비율 | **92.18%** | **90.61%** | −1.57%p |
| 평균 Δ% | **−6.245%** | **−6.000%** | +0.245%p |
| 중앙값 Δ% | −6.148% | −6.905% | −0.757%p |

cell당 paired 비교 수: 최소 16 · 최대 96 · 중앙값 48 · 평균 51.7.

### 결과 — FULL (K=10 포함, n=1360, 참고)

| 지표 | file-weighted | cell-weighted | 차이 |
|---|---:|---:|---:|
| better 비율 | 91.69% | 89.81% | −1.88%p |
| 평균 Δ% | −8.063% | −6.540% | +1.524%p |
| 중앙값 Δ% | −6.581% | −7.054% | −0.474%p |

### per-cell breakdown (HEADLINE, 평균 Δ% 오름차순)

| cell | n | better% | 평균 Δ% | 중앙값 Δ% |
|---|---:|---:|---:|---:|
| A5-scale-sf1-SIFT | 48 | 100.0% | −25.85% | −25.95% |
| A6-WIKI-sf1 | 48 | 100.0% | −10.95% | −11.27% |
| A5-scale-sf10-SIFT | 48 | 91.7% | −9.12% | −10.12% |
| A7-YFCC-sf1 | 48 | 93.8% | −8.47% | −9.04% |
| A1-SIFT | 96 | 91.7% | −7.67% | −8.76% |
| A11-DEEP+YFCC-concat-sf10 | 48 | 95.8% | −7.42% | −6.10% |
| A10-DEEP+WIKI-concat-sf1 | 48 | 97.9% | −7.36% | −8.25% |
| A1-DEEP | 52 | 100.0% | −7.01% | −7.90% |
| A5-scale-sf100 | 52 | 100.0% | −7.00% | −7.90% |
| A11-DEEP+YFCC-concat-sf1 | 48 | 100.0% | −6.64% | −6.47% |
| A2-Fig7 | 52 | 94.2% | −6.61% | −7.66% |
| A5-scale-sf1 | 52 | 94.2% | −6.59% | −5.39% |
| A5-scale-sf1-SSN | 48 | 97.9% | −6.29% | −4.19% |
| A9-DEEP+SIFT-concat-sf1 | 48 | 89.6% | −6.05% | −6.44% |
| A9-DEEP+SIFT-concat-sf100 | 48 | 95.8% | −5.60% | −4.63% |
| A6-WIKI-sf10 | 48 | 87.5% | −5.53% | −7.83% |
| A9-DEEP+SIFT-concat-sf10 | 48 | 91.7% | −5.04% | −5.09% |
| A1-SSN | 96 | 93.8% | −4.89% | −4.55% |
| A8-DEEP+SIFT-sf10 | 48 | 83.3% | −3.56% | −4.57% |
| A5-scale-sf10-SSN | 48 | 91.7% | −3.54% | −4.16% |
| A5-scale-sf10 | 52 | 82.7% | −3.52% | −4.53% |
| A2-Fig9 | 52 | 82.7% | −3.45% | −4.53% |
| A4-sel | 16 | 37.5% | +3.02% | +4.25% |
| A10-DEEP+WIKI-concat-sf10 | 48 | 81.2% | +11.22% | −4.63% |

### 해석

**cell-weighted 재집계는 REPORT v12 §9가 예고한 "better 90.6%·평균 −6.00%"를 정확히 재현한다** (90.61%·−6.00%) — 검증 통과.

file-weighted에서 cell-weighted로 바꾸면 better 비율이 1.57%p 내려간다(92.18 → 90.61%). 이유는 per-cell 표에서 명확하다. 측정 file이 많은 cell(A1-SIFT 96건, A1-DEEP·A2-Fig7·A5-scale 계열 각 52건)은 대체로 better 비율이 높고(91~100%), 측정 file이 적은 cell 중 약한 두 cell — A4-sel(16건, better 37.5%)과 A10-DEEP+WIKI-concat-sf10(48건, better 81.2%) — 이 cell-weighted에서 다른 cell과 동등한 1/24 가중을 받으며 평균을 끌어내린다. file-weighted에서는 이 두 약한 cell의 비교 수(16+48=64)가 1240분의 64로 희석되지만, cell-weighted에서는 2/24로 확대된다.

평균 Δ%는 방향이 반대다 — cell-weighted(−6.00%)가 file-weighted(−6.25%)보다 0.25%p 덜 음수다. 이는 가장 강한 cell A5-scale-sf1-SIFT(−25.85%, 48건)의 영향이 cell-weighted에서 1/24로 묶이기 때문이다. file-weighted에서는 이 cell의 48건이 평균을 더 끌어내린다. 중앙값은 반대로 cell-weighted(−6.90%)가 더 음수인데, 약한 cell들이 양수 평균을 갖더라도 cell별 "중앙값"은 음수인 경우가 많아(A10조차 중앙값 −4.63%) cell 중앙값들의 평균이 더 음수로 모이기 때문이다.

**두 집계 모두 결론을 바꾸지 않는다.** better 비율은 90.6~92.2%, 평균 Δ%는 −6.0~−6.25%로, 어느 가중을 쓰든 "약 9할 비교에서 −6% 안팎 개선"이라는 REPORT v12 결론이 유지된다. 절대 수치는 가중 방식에 따라 better ±1.6%p·평균 ±0.25%p 안에서 움직인다. 발표·보고서에서 headline을 인용할 때 file-weighted 92.2%임을 명시하고, cell-weighted 90.6%를 robustness 근거로 병기하는 것이 정직하다.

---

## 종합 — 4건 결과 요약과 결론 영향

| 보완 | REPORT v12 §9 우려 | 재계산 결과 | headline 결론 영향 |
|---|---|---|---|
| (a) BH-FDR family 분할 | 단일 family는 over-correction → 78.3%가 보수적 | family를 cell·method·(cell,method)로 나눠도 유의 우월 77.5~78.6%. over-correction 거의 없음 | **없음.** 78.3%는 family 분할에 무관하게 안정 |
| (b) paired 효과크기 | 독립표본 공식이 paired effect를 보수적으로 추정 | trial 간 상관 r≈−0.01(무상관). paired Cliff's δ large 80.3%, paired Hedges' g_av large 83.2% — 독립표본판(82.5%/83.8%)과 거의 동일 | **없음.** §9의 "보수적" 진단은 정정 필요 — 두 공식이 일치 |
| (c) Wilcoxon p값 해상도 | n=10 → 최소 p=1/1024, 바닥값에 몰림 | headline 1240건 중 652건(52.6%)이 one-sided 바닥값. 고유 p값 51개뿐. FULL 746건은 REPORT 수치와 일치 | **없음.** 유의 78.3%는 견고. 단 강도 미세분해는 p값 아닌 Δ%·effect size로 |
| (d) cell-weighted 재집계 | file-weighted 92.2%는 측정 많은 cell에 치우침 | cell-weighted = better 90.61%·평균 −6.00%. REPORT §9 예고치 정확 재현 | **없음.** 90.6~92.2% / −6.0~−6.25%, 결론 유지 |

### REPORT v12 headline 결론을 바꾸는 것이 있는가 — 없다

네 보완 모두 REPORT v12의 핵심 finding을 바꾸지 않는다.

- **better 비율**: file-weighted 92.2% · cell-weighted 90.6% — 어느 쪽이든 "약 9할".
- **평균 Δ%**: file-weighted −6.25% · cell-weighted −6.00% — 어느 쪽이든 "−6% 안팎 개선".
- **통계적 유의 우월**: BH family 분할 무관 77.5~78.6% — "약 8할 유의".
- **효과크기 large 우월**: paired 공식으로도 Cliff's δ 80.3% · Hedges' g 83.2% — "약 8할 large".

다만 REPORT v12 §9 항목 (7)의 본문 서술 중 **한 곳은 정정이 필요하다.** §9는 "Cliff's δ와 Hedges' g가 독립표본 공식이라 paired effect를 보수적으로(작게) 추정한다"고 적었으나, 재계산 결과 trial 간 상관이 0에 가까워(r≈−0.013) paired 공식과 독립표본 공식이 거의 같은 값을 준다. 보수적 추정이 아니라 "두 공식이 사실상 일치"가 정확한 진단이다. paired Cliff's δ(80.3%)는 10쌍 해상도 한계로 오히려 독립표본판(82.5%)보다 약간 낮다. REPORT v13 작성 시 §9 항목 (7) 셋째 문장을 이 실측에 맞게 고칠 것을 권한다.

나머지 세 항목은 §9 서술과 부합하며, 본 문서가 정량화를 보강한다 — (a) over-correction 우려는 실측상 1%p 미만으로 미미하고, (c) 바닥값 집중은 52.6%(headline)/54.9%(full)로 정량화되며, (d) cell-weighted 90.6%/−6.00%는 §9 예고치와 정확히 일치한다.
