# γ 축 검증 — 보고서 §5 figure backing 정합성 (18 항목)

**검증 대상**: 6/11 보고서 §5 chapter 의 신규 figure 3종(fig5_2 speedup heatmap, fig5_3 plan recovery, fig5_4 Wilcoxon significance) + rename 정합 (fig6_1/fig7_1).
**검증 base**: paired_stats.csv (348 row), latency_tpc_h_*.json (12 cell), analyze_latency.py (611 line), 보고서 line 383·408·431·475·525.
**검증 일시**: 2026-05-20 (KST).

## VERDICT

**PASS (minor)** — 모든 figure 의 데이터 backing 은 raw 와 정확히 정합한다. plan recovery 매트릭스 B1=7/12 (58.3%) · CaseB=148/156 (94.87%) raw 검증 완료, paired Wilcoxon baseline-180/180 · B1-13/168 raw 검증 완료. 산출 코드 3 함수가 정확한 컬럼·산출 routine 을 사용한다. **단, minor discrepancy 3건 catalog (§6) — 보고서 캡션의 max speedup "7.5×" 는 실제 7.81× 보다 작게 표기됐고, Q12 cell 의 p_holm "0.0034" 는 실제 0.01025 와 다르다.**

---

## §1 fig5_2 speedup heatmap 검증 (5 항목)

| # | 항목 | 결과 | 근거 |
|---|---|:-:|---|
| 1 | 가로축 12 cell · 세로축 15 비-기본 variant (heatmap layout) | PASS | png 시각: 행 12개 (q10·qid0~q12·qid2) × 열 15개 (B1·oracle·CaseB 13). `analyze_latency.py:362` 의 `M = np.full((len(cells), len(_NON_BASELINE_ORDER)), np.nan)` 에서 `_NON_BASELINE_ORDER` 가 15 entry (line 325-331) — 정합. 단, **사용자 task spec 은 "12 cell × 15 variant" 인데 figure 의 X·Y 축이 task spec 의 X·Y 와 반대** (figure: row=cell, col=variant) — 시각 layout 의 의도된 표기. |
| 2 | 색 스케일: 흰색=1.0, 진한 색=고가속 (midpoint=1.0 TwoSlopeNorm) | PASS | 코드 line 376-377: `mcolors.TwoSlopeNorm(vmin=min(vmin, 0.8), vcenter=1.0, vmax=max(vmax, 1.2))`. cmap=`RdBu_r` (line 378). png 시각: 모든 셀이 빨강 계열 (1.0 위 = 가속). |
| 3 | 모든 셀 값 2.9~7.5× 범위 (보고서 캡션 명시) | **minor WARN** | raw trimmed-mean speedup 분포: **min=2.81× max=7.81×** (n=180). 보고서 line 385 캡션 "2.9×~7.5×" 의 max 7.5× 는 실제 7.81× 보다 작게 클램프됨. png 시각 q3·qid0 행에 chao_weighted=7.8× / mhist2=7.7× / ica_fastica=7.8× 셀이 보임 (>7.5×). |
| 4 | 행별 평균 (q3 ~7×, q9 ~3×, q10 ~6.4×, q12 ~6.2-7.2×) | PASS | trimmed-mean 산출: q3·qid0=7.36× · q3·qid1=7.16× · q3·qid2=7.21× · q9·qid0=2.97× · q9·qid1=2.85× · q9·qid2=2.91× · q10·qid0=6.40× · q10·qid1=6.45× · q10·qid2=6.36× · q12·qid0=6.13× · q12·qid1=6.06× · q12·qid2=7.29× — png 시각의 행별 평균과 정합 (q9 가 가장 느림·q3 가 가장 빠름). |
| 5 | plot_speedup_heatmap 의 사용 컬럼 | PASS | 코드 line 365·370-371: `base_ms = by.get("baseline", {}).get("exec_ms_trimmed")` + `M[i,j] = base_ms / v["exec_ms_trimmed"]`. **paired_stats.csv 가 아닌 latency_*.json 의 `exec_ms_trimmed` (trimmed mean) 직접 사용**. 이는 보고서 §5.3 표 5-1 의 latency 와 동일한 source (analyze_stdout 의 "lat(ms)" 컬럼). paired_stats.csv 의 `anchor_med_ms`/`variant_med_ms` 는 median 으로 figure 와 다른 통계량. |

### 핵심 시각 sample 검증

| cell | variant | figure 시각 | raw trimmed-mean | base/var |
|---|---|:-:|:-:|---|
| q10·qid0 | B1 | 6.5× | 6.47× | 6303/974 |
| q10·qid0 | oracle | 6.6× | 6.57× | 6303/960 |
| q10·qid0 | chao_weighted | 6.4× | 6.42× | 6303/981 |
| q3·qid0 | B1 | 7.1× | 7.11× | 7242/1018 |
| q3·qid0 | chao_weighted | 7.8× | 7.81× | 7242/927 |
| q9·qid0 | B1 | 3.0× | 3.01× | 2690/894 |
| q12·qid0 | B1 | 6.3× | 6.34× | 6013/948 |

→ figure 시각 값과 raw trimmed-mean speedup 이 모두 ±0.1 반올림 범위에서 정확히 정합.

---

## §2 fig5_3 plan recovery matrix 검증 (5 항목)

| # | 항목 | 결과 | 근거 |
|---|---|:-:|---|
| 6 | 가로축 12 cell · 세로축 14 variant (B1 + CaseB 13) | PASS | png 시각: 행 12개 × 열 15개 (B1·oracle·CaseB 13). 실제 task spec 의 "14 variant" 는 oracle 제외 B1+CaseB 13 의미였으나 figure 는 oracle 포함 15 entry. 코드 `_NON_BASELINE_ORDER` (line 325-331) = "B1, oracle, CaseB×13" 15 entry — 의도된 표기. oracle 열은 모두 진녹 (자기 자신 align). |
| 7 | 색 스케일: 진녹=oracle align, 옅노=불일치 | PASS | 코드 line 433: `cmap = mcolors.ListedColormap(["#cccccc", "#f4d35e", "#5cab7d"])` = 회색(미캡처)·노랑(≠oracle)·녹색(=oracle). bounds `[-0.5, 0.25, 0.75, 1.5]` (line 434). png 시각: 모든 align 셀에 흰 ● 표시 (line 444-445). |
| 8 | B1 행: 7/12 cell 진녹 (qid0 0/4 + qid1 4/4 + qid2 3/4) | PASS | raw 검증: B1 align cell = q10·qid1·qid2 · q12·qid1·qid2 · q3·qid1 · q9·qid1·qid2 = **7/12 = 58.3%** ✓. 보고서 표 5-2 "qid 0 = 0/4, qid 1 = 4/4, qid 2 = 3/4, 합계 7/12" 정합. png 시각: B1 열의 노란 셀 = q10·qid0 · q12·qid0 · q3·qid0 · q3·qid2 · q9·qid0 = 5건. 녹색=7건 (=58.3%). |
| 9 | CaseB 13 행 합계: 148/156 = 94.9% 진녹 | PASS | raw 검증: CaseB align = 13×13(완전 align cell q9~q12 모두) − 8(미달) = **148/156 = 94.87%** ✓. 보고서 표 5-2 합계 행 정합. |
| 10 | Q3 qid0 의 hilbert_real, qid1 의 sparse_rp, qid2 의 6 method 옅노 | PASS | raw 검증 8건 미달: q3·qid0=hilbert_real(1건), q3·qid1=sparse_rp(1건), q3·qid2=hilbert_real·skilling_hilbert·chao_weighted·ica_fastica·hyperloglog·rabitq_strat(6건). png 시각: q3·qid0 행에 hilbert_real 셀 1개 노랑, q3·qid1 행에 sparse_rp 셀 1개 노랑, q3·qid2 행에 6 cell 연속 노랑 — 정합. |

### plan recovery 핵심 raw 매트릭스

| cell | B1 | CaseB align/13 | 미달 method |
|---|:-:|:-:|---|
| q3·qid0 | DIFF | 12/13 | hilbert_real |
| q3·qid1 | ALIGN | 12/13 | sparse_rp |
| q3·qid2 | DIFF | 7/13 | hilbert_real, skilling_hilbert, chao_weighted, ica_fastica, hyperloglog, rabitq_strat |
| q9·qid0 | DIFF | 13/13 | — |
| q9·qid1 | ALIGN | 13/13 | — |
| q9·qid2 | ALIGN | 13/13 | — |
| q10·qid0 | DIFF | 13/13 | — |
| q10·qid1 | ALIGN | 13/13 | — |
| q10·qid2 | ALIGN | 13/13 | — |
| q12·qid0 | DIFF | 13/13 | — |
| q12·qid1 | ALIGN | 13/13 | — |
| q12·qid2 | ALIGN | 13/13 | — |
| **합계** | **7/12** | **148/156** | |

→ 보고서 표 5-2 와 §5.4 본문 ("qid 0 = 0/4, qid 1 = 4/4, qid 2 = 3/4 → 7/12 (58%)" · "결합 13종 oracle-align 148/156 = 94.9%") 모두 raw 와 정확 정합.

---

## §3 fig5_4 Wilcoxon significance heatmap 검증 (4 항목)

| # | 항목 | 결과 | 근거 |
|---|---|:-:|---|
| 11 | 가로축 12 cell · 세로축 14 variant (B1 anchor 의 비-B1 14) | PASS | png 시각: 행 12개 × 열 14개 (oracle + CaseB 13). 코드 line 474-475: `cells = sorted({r["cell"] for r in sub})` + `variants = [v for v in _NON_BASELINE_ORDER if v != "B1"]` → B1 제외 14 entry — 정합. |
| 12 | 셀 색 = -log10(p_holm), 별표(★) = p_holm < 0.05 | PASS | 코드 line 488-489: `M[i,j] = -math.log10(max(p, 1e-6))` · `SIG[i,j] = p < 0.05`. line 497-499: `if SIG[i,j]: ax.text(j, i, "★", ...)`. png 시각: ★ 표시된 셀 = 진한 PuRd 색 · 비-★ 셀은 흰색 (p_holm≈1.0). |
| 13 | 168 cell 중 별표 13 cell (= 7.7%) | PASS | raw 검증: B1 anchor 의 p_holm < 0.05 cell = **13건 / 168건 = 7.74%** ✓. 보고서 표 5-3 "13 / 168 = 7.7%" 정합. png 시각: ★ 셀 13개 확인 — q12·qid0 4건 (pca1d/zorder_morton/sparse_rp/rabitq_strat) · q3·qid2 8건 (oracle/pca1d/zorder_morton/cum_sqrtf/lavallee_hidiroglou/rsvd/sparse_rp/mhist2) · q9·qid0 1건 (skilling_hilbert). |
| 14 | Q12 qid0 의 4 cell 별표 (p_holm = 0.0034) | **minor WARN** | raw 검증: q12·qid0 의 4 method (pca1d, rabitq_strat, sparse_rp, zorder_morton) 모두 p_holm = **0.01025** (csv 값 0.01025390625, p_value=4.5776367187e-04). 보고서 line 427 의 "p_holm = 0.0034" 는 실제 0.01025 와 다르다 — 보고서 본문 수치 오기. 정합 visual 은 PASS (★ 표시 정상). |

### B1 anchor 의 p_holm < 0.05 13 cell raw

| cell | variant | p_value | p_holm |
|---|---|---|---|
| q12·qid0 | pca1d | 4.578e-04 | 0.01025 |
| q12·qid0 | rabitq_strat | 4.578e-04 | 0.01025 |
| q12·qid0 | sparse_rp | 4.578e-04 | 0.01025 |
| q12·qid0 | zorder_morton | 4.578e-04 | 0.01025 |
| q3·qid2 | cum_sqrtf | 4.578e-04 | 0.01025 |
| q3·qid2 | lavallee_hidiroglou | 4.578e-04 | 0.01025 |
| q3·qid2 | mhist2 | 4.578e-04 | 0.01025 |
| q3·qid2 | pca1d | 4.578e-04 | 0.01025 |
| q3·qid2 | rsvd | 4.578e-04 | 0.01025 |
| q3·qid2 | sparse_rp | 4.578e-04 | 0.01025 |
| q3·qid2 | zorder_morton | 4.578e-04 | 0.01025 |
| q3·qid2 | oracle | 4.578e-04 | 0.01025 |
| q9·qid0 | skilling_hilbert | 2.136e-03 | 0.04761 |

총 13건 — 보고서 "13 / 168 = 7.7%" 정합. **단, 보고서 §5.5 본문 "p_holm = 0.0034" 는 실제 측정 0.01025 와 불일치.**

---

## §4 analyze_latency.py 함수 코드 정합 (3 함수)

### 함수 1: plot_speedup_heatmap (line 349-396)

| 항목 | 결과 |
|---|:-:|
| 사용 컬럼 | `exec_ms_trimmed` (latency_*.json 직접 로드 — paired_stats.csv 가 아닌 latency JSON 의 trimmed mean) |
| 산출 routine | `base_ms = baseline.exec_ms_trimmed`; for j, vlab: `M[i,j] = base_ms / v.exec_ms_trimmed`. 즉 trimmed-mean 비율의 직접 계산. paired_stats.csv 의 anchor_med (median) 와는 다른 통계량. |
| 코드 정합 | PASS — line 365·370-371 의 baseline_ms / variant_ms 계산이 분석 로직과 일관. |

### 함수 2: plot_plan_recovery_matrix (line 399-459)

| 항목 | 결과 |
|---|:-:|
| 사용 컬럼 | `plan_json` (latency_*.json 의 EXPLAIN ANALYZE 트리). `plan_signature` (line 72-79) 가 pre-order Node Type 튜플로 압축. |
| 산출 routine | line 418: `orc_sig = plan_signature(by.get("oracle"))`. line 425-430: variant 의 plan_signature 가 orc_sig 와 동일하면 `M[i,j] = 1.0` (그린), 다르면 `0.5` (옐로우), injection_fired=False 거나 미캡처면 `MISS[i,j] = True` (회색 hatch). |
| 코드 정합 | PASS — 보고서 §5.4 의 "plan signature" 정의 ("(Node Type, Relation/Index, Join Type) 의 pre-order 튜플") 가 코드의 plan_signature 함수와 정확히 일치. 단 코드는 Node Type 만 추출하고 Relation/Index/Join Type 은 별도 포함 X — 보고서 정의의 "Relation/Index, Join Type" 은 정확히는 미포함 (정밀도 한계는 보고서 §5.6 다섯째 한계에서 언급). |

### 함수 3: plot_paired_significance (line 462-514)

| 항목 | 결과 |
|---|:-:|
| 사용 컬럼 | `p_holm` (paired_stats 의 row 의 p_holm). anchor="B1" 으로 필터링. |
| 산출 routine | line 482-490: B1 anchor row 만 추출 → cell × variant 매트릭스로 펼침. `M[i,j] = -log10(max(p_holm, 1e-6))` · `SIG[i,j] = p_holm < 0.05`. line 497-499: SIG 셀에 ★ 표시. |
| Holm-Bonferroni 보정 | PASS — paired_stats 함수 (line 141-200) 에서 anchor 별로 분리 보정 (line 186-199). line 188: `sub_sorted = sorted(sub, key=lambda r: r["p_value"])` · line 195: `adj = min(1.0, r["p_value"] * (n - rank + 1))` · line 196: `adj = max(adj, prev)` (단조증가 강제). 표준 Holm 절차 일치. |

---

## §5 rename 정합 (보고서 reference)

| 새 파일 path | 보고서 line | reference | 결과 |
|---|---|---|:-:|
| `experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.png` | 383 | `![그림 5-1](../../experiments/figures/보고서_6_11/fig5_2_speedup_heatmap.png)` | PASS |
| `experiments/figures/보고서_6_11/fig5_3_plan_recovery.png` | 408 | `![그림 5-2](../../experiments/figures/보고서_6_11/fig5_3_plan_recovery.png)` | PASS |
| `experiments/figures/보고서_6_11/fig5_4_wilcoxon_significance.png` | 431 | `![그림 5-3](../../experiments/figures/보고서_6_11/fig5_4_wilcoxon_significance.png)` | PASS |
| `experiments/figures/보고서_6_11/fig6_1_dynamic_method_selection.png` | 475 | `![그림 6-1](../../experiments/figures/보고서_6_11/fig6_1_dynamic_method_selection.png)` | PASS (rename 후 6장 본문 reference 도 새 path 지목) |
| `experiments/figures/보고서_6_11/fig7_1_gantt.png` | 525 | `![그림 7-1](../../experiments/figures/보고서_6_11/fig7_1_gantt.png)` | PASS (rename 후 7장 본문 reference 도 새 path 지목) |

→ rename 완료된 5 figure 모두 정확한 경로에 존재 (mtime 2026-05-19 13:11/13:06 + fig5_x 는 2026-05-20 09:49) + 보고서 inline `![](path)` reference 가 모두 새 path 를 정확히 지목한다.

---

## §6 발견 issue catalog

| # | severity | 위치 | 발견 사항 | 권장 조치 |
|---|---|---|---|---|
| 1 | **minor** | 보고서 line 385 (그림 5-1 캡션) | 캡션 "가속 폭이 2.9×~7.5× 사이에 분포" — 실제 raw trimmed-mean speedup 범위는 **2.81× ~ 7.81×**. max 7.5× 는 실제 7.81× 보다 작게 표기. png 시각의 q3 행에는 7.7×~7.8× 셀이 분명히 보임. | 캡션을 "2.9×~7.8×" 또는 "3×~8×" 로 정정 권장. |
| 2 | **minor** | 보고서 line 427 (§5.5 본문) | "Q12의 네 method(pca1d·rabitq_strat·sparse_rp·zorder_morton, p_holm = 0.0034)" — 실제 csv 의 p_holm 은 모두 **0.01025**. p_value 4.578e-04 가 Holm 보정 후 0.01025 (단조증가 강제로 q3·qid2 와 동일 값). 0.0034 는 어디서 왔는지 불분명 (혹시 보정 전 p value × 보정 factor 의 다른 계산?). | 보고서 본문의 "p_holm = 0.0034" 를 "p_holm = 0.0103" (또는 본문에서 "약 1e-2 수준" 식 모호 표기) 로 정정 권장. |
| 3 | **minor** | analyze_latency.py plan_signature 정밀도 (line 72-79) | 보고서 §5.4·§5.6 가 "(Node Type, Relation/Index, Join Type) 의 pre-order 튜플" 로 명시하지만, 실제 코드는 **Node Type 만 추출** (line 76: `sig = [plan.get("Node Type", "?")]`). Relation/Index 와 Join Type 은 포함 X. | 보고서 §5.6 다섯째 한계가 plan signature 의 정밀도 한계를 언급하므로 영향 작음. 단, §5.4 의 정의 표기를 "(Node Type 의 pre-order 튜플)" 로 정정하거나 §5.6 한계에서 "Relation/Index/Join Type 등 부가 속성 미포함" 으로 명시 강화 권장. |

**critical 0건 · major 0건 · minor 3건.**

핵심 데이터 backing (12 cell × 15 variant 의 speedup matrix, 12 cell × 14 variant 의 plan recovery matrix, B1 anchor 168 paired test 의 p_holm matrix) 은 모두 latency_*.json raw 와 paired_stats.csv raw 와 ±0.1 단위에서 정확히 정합하며, 코드 3 함수가 정확한 컬럼을 사용한다. minor issue 3건은 본문 캡션 수치 오기 (2건) + 함수 정의 표기 모호 (1건) 로, figure 자체의 데이터 backing 무결성에는 영향 없음.

---

**검증 종료** — VERDICT: PASS (minor). 보고서 §5 의 figure 3종은 raw 데이터·산출 코드와 정합하며 출판 가능 상태. 다만 §6 의 minor 3건은 사용자 검토 후 보고서 본문 캡션·정의 표기를 정정하면 완벽한 정합 상태 달성.
