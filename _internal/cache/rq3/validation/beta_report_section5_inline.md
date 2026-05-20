# β 축 검증 보고서 — 6/11 보고서 §5 엔진 적용 검증 inline 수치 전수 점검

## 메타
- 검증 일시: 2026-05-20 (KST)
- 정본 base:
  - 보고서 §5: `/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_6_11_최종보고서_20260520_093500.md` line 336-449
  - Phase 2 raw stdout: `/Users/hyunbin/Capstone/_internal/cache/rq3/latency/phase2/analyze_stdout_full.txt`
  - paired Wilcoxon: `/Users/hyunbin/Capstone/_internal/cache/rq3/latency/phase2/figures/paired_stats.csv` (348 row)
  - 12 JSON: `/Users/hyunbin/Capstone/_internal/cache/rq3/latency/phase2/latency_tpc_h_{q3,q9,q10,q12}_DEEP_sf10_sel0.001_qid{0,1,2}.json`
- sub-agent 모델: claude-opus-4-7[1m]
- 검증 항목 수: 25개 (전수 점검)

## VERDICT

**WARN** — §5.3 표 5-1 60 cell + §5.4 plan 회복 매트릭스 + §5.5 통계 검정 결과(180/180, 13/168 7.7%)는 raw 와 1:1 일치하나, §5.3 본문 line 381, §5.5 line 425+427, §5.6 line 439+441 의 본문 산문에 **5건의 major 환각 + 2건의 minor**가 산재. 표·수치 자체는 정확하나 그를 해석하는 본문 산문이 raw 와 불일치하는 패턴.

---

## §1. §5.3 표 5-1 60 cell 검증 (12 행 × 5 컬럼)

표 정의: D, true_card, baseline, B1, oracle (단위 ms, trimmed mean). 단위 정합 + 반올림 정합 확인.

| 행 | 컬럼 | 보고서 expected | raw actual | status |
|---|---|---:|---:|:--:|
| q3 · qid0  | D         |  0.8612 |  0.8612 | PASS |
| q3 · qid0  | true_card |   7,603 |   7603  | PASS |
| q3 · qid0  | baseline  |   7,242 |   7242.2 | PASS (반올림) |
| q3 · qid0  | B1        |   1,018 |   1018.1 | PASS (반올림) |
| q3 · qid0  | oracle    |   1,000 |   1000.0 | PASS |
| q3 · qid0  | speedup   |   7.24× |   7.24×  | PASS |
| q3 · qid0  | plan=oracle |   ×    | False    | PASS |
| q3 · qid1  | D         |  0.9569 |  0.9569 | PASS |
| q3 · qid1  | true_card |   8,013 |   8013  | PASS |
| q3 · qid1  | baseline  |   6,820 |   6819.9 | PASS (반올림) |
| q3 · qid1  | B1        |     937 |    936.8 | PASS (반올림) |
| q3 · qid1  | oracle    |     935 |    935.4 | PASS (반올림) |
| q3 · qid1  | speedup   |   7.29× |   7.29× | PASS |
| q3 · qid1  | plan=oracle |   ○    | True    | PASS |
| q3 · qid2  | D         |  0.8783 |  0.8783 | PASS |
| q3 · qid2  | true_card |   8,090 |   8090  | PASS |
| q3 · qid2  | baseline  |   8,119 |   8119.3 | PASS (반올림) |
| q3 · qid2  | B1        |   1,217 |   1217.5 | PASS (반올림) |
| q3 · qid2  | oracle    |   1,097 |   1097.1 | PASS (반올림) |
| q3 · qid2  | speedup   |   7.40× |   7.40× | PASS |
| q3 · qid2  | plan=oracle |   ×    | False    | PASS |
| q9 · qid0  | D         |  0.8612 |  0.8612 | PASS |
| q9 · qid0  | true_card |   7,603 |   7603  | PASS |
| q9 · qid0  | baseline  |   2,691 |   2691.3 | PASS (반올림) |
| q9 · qid0  | B1        |     895 |    894.6 | PASS (반올림) |
| q9 · qid0  | oracle    |     912 |    912.3 | PASS (반올림) |
| q9 · qid0  | speedup   |   2.95× |   2.95× | PASS |
| q9 · qid0  | plan=oracle |   ×    | False    | PASS |
| q9 · qid1  | D         |  0.9569 |  0.9569 | PASS |
| q9 · qid1  | true_card |   8,013 |   8013  | PASS |
| q9 · qid1  | baseline  |   2,417 |   2417.1 | PASS (반올림) |
| q9 · qid1  | B1        |     861 |    860.9 | PASS (반올림) |
| q9 · qid1  | oracle    |     826 |    825.9 | PASS (반올림) |
| q9 · qid1  | speedup   |   2.93× |   2.93× | PASS |
| q9 · qid1  | plan=oracle |   ○    | True    | PASS |
| q9 · qid2  | D         |  0.8783 |  0.8783 | PASS |
| q9 · qid2  | true_card |   8,090 |   8090  | PASS |
| q9 · qid2  | baseline  |   2,651 |   2651.0 | PASS |
| q9 · qid2  | B1        |     915 |    915.3 | PASS (반올림) |
| q9 · qid2  | oracle    |     894 |    894.4 | PASS (반올림) |
| q9 · qid2  | speedup   |   2.96× |   2.96× | PASS |
| q9 · qid2  | plan=oracle |   ○    | True    | PASS |
| q10 · qid0 | D         |  0.8612 |  0.8612 | PASS |
| q10 · qid0 | true_card |   7,603 |   7603  | PASS |
| q10 · qid0 | baseline  |   6,303 |   6303.0 | PASS |
| q10 · qid0 | B1        |     974 |    973.9 | PASS (반올림) |
| q10 · qid0 | oracle    |     960 |    960.0 | PASS |
| q10 · qid0 | speedup   |   6.57× |   6.57× | PASS |
| q10 · qid0 | plan=oracle |   ×    | False    | PASS |
| q10 · qid1 | D         |  0.9569 |  0.9569 | PASS |
| q10 · qid1 | true_card |   8,013 |   8013  | PASS |
| q10 · qid1 | baseline  |   6,704 |   6703.7 | PASS (반올림) |
| q10 · qid1 | B1        |   1,065 |   1065.4 | PASS (반올림) |
| q10 · qid1 | oracle    |   1,042 |   1042.2 | PASS (반올림) |
| q10 · qid1 | speedup   |   6.43× |   6.43× | PASS |
| q10 · qid1 | plan=oracle |   ○    | True    | PASS |
| q10 · qid2 | D         |  0.8783 |  0.8783 | PASS |
| q10 · qid2 | true_card |   8,090 |   8090  | PASS |
| q10 · qid2 | baseline  |   6,609 |   6609.1 | PASS (반올림) |
| q10 · qid2 | B1        |   1,060 |   1060.2 | PASS (반올림) |
| q10 · qid2 | oracle    |   1,065 |   1065.0 | PASS |
| q10 · qid2 | speedup   |   6.21× |   6.21× | PASS |
| q10 · qid2 | plan=oracle |   ○    | True    | PASS |
| q12 · qid0 | D         |  0.8612 |  0.8612 | PASS |
| q12 · qid0 | true_card |   7,603 |   7603  | PASS |
| q12 · qid0 | baseline  |   5,966 |   5965.8 | PASS (반올림) |
| q12 · qid0 | B1        |     953 |    952.6 | PASS (반올림) |
| q12 · qid0 | oracle    |     988 |    987.5 | PASS (반올림) |
| q12 · qid0 | speedup   |   6.04× |   6.04× | PASS |
| q12 · qid0 | plan=oracle |   ×    | False    | PASS |
| q12 · qid1 | D         |  0.9569 |  0.9569 | PASS |
| q12 · qid1 | true_card |   8,013 |   8013  | PASS |
| q12 · qid1 | baseline  |   5,365 |   5365.0 | PASS |
| q12 · qid1 | B1        |     899 |    899.2 | PASS (반올림) |
| q12 · qid1 | oracle    |     902 |    901.7 | PASS (반올림) |
| q12 · qid1 | speedup   |   5.95× |   5.95× | PASS |
| q12 · qid1 | plan=oracle |   ○    | True    | PASS |
| q12 · qid2 | D         |  0.8783 |  0.8783 | PASS |
| q12 · qid2 | true_card |   8,090 |   8090  | PASS |
| q12 · qid2 | baseline  |   5,314 |   5313.9 | PASS (반올림) |
| q12 · qid2 | B1        |     830 |    830.2 | PASS (반올림) |
| q12 · qid2 | oracle    |     867 |    867.2 | PASS (반올림) |
| q12 · qid2 | speedup   |   6.13× |   6.13× | PASS |
| q12 · qid2 | plan=oracle |   ○    | True    | PASS |

**§1 표 5-1 60 cell 종합**: **60/60 PASS** — 모든 cell·컬럼이 반올림 단위에서 raw 와 1:1 일치. true_card 가 모든 12 cell 에서 7,603~8,090 범위에 들어 보고서 line 377 의 claim도 PASS. D 컬럼은 qid 0=0.8612 / qid 1=0.9569 / qid 2=0.8783 — 모든 query family 동일 (raw 정합).

---

## §2. §5.3 본문 산문 4개 수치 검증

### 항목 15. 12 cell 평균 speedup = 5.67× (line 379)
- 보고서 line 379 인용: "12 cell의 평균 speedup은 5.67×이다."
- raw 계산: 12 cell speedup = [7.24, 7.29, 7.40, 2.95, 2.93, 2.96, 6.57, 6.43, 6.21, 6.04, 5.95, 6.13] → 평균 5.67×
- **PASS** (1:1 일치)

### 항목 16+17. B1 12 cell 평균 1,005ms vs 정답 957ms 차이 5% 안쪽 (line 381)
- 보고서 line 381 인용: "베이스라인(B1)의 latency는 12 cell 평균 1,005ms로 정답(평균 957ms)과의 차이가 5% 안쪽이고"
- raw 평균:
  - B1: 968.7ms (rounded 969ms)
  - oracle: 957.4ms (rounded 957ms)
  - 차이: (968.7 - 957.4) / 957.4 = +1.18%
- **B1 평균 1,005ms claim — major 환각** (raw = 968.7ms, 보고서 = 1,005ms, 36.3ms 차이 = 3.7%)
- "5% 안쪽" 부분은 raw +1.18% 이므로 충족 — 다만 보고서 claim 의 (1005-957)/957 ≈ 5.0% 도출 자체가 raw 와 어긋남
- oracle 평균 957ms — **PASS** (raw 957.4ms)
- **항목 16: MAJOR**, 항목 17: PASS (결과적으로 5% 안쪽임은 raw 도 일치)

### 항목 18. "모든 cell에서 베이스라인이 기본엔진 대비 3배 이상 빠르다" (line 381)
- 보고서 line 381 인용: "모든 cell에서 베이스라인이 기본엔진 대비 3배 이상 빠르다."
- raw 계산 12 cell baseline/B1 비율:
  - q3/qid0: 7.11× / qid1: 7.28× / qid2: 6.67×
  - q9/qid0: 3.01× / **qid1: 2.81×** / **qid2: 2.90×**
  - q10/qid0: 6.47× / qid1: 6.29× / qid2: 6.23×
  - q12/qid0: 6.26× / qid1: 5.97× / qid2: 6.40×
- **q9/qid1 (2.81×), q9/qid2 (2.90×) 2 cell이 3배 미달** — claim "모든 cell에서 3배 이상" 위배
- **MAJOR** — 보고서의 absolute 일반화가 raw 와 충돌. raw 기준 정확 표현은 "12 cell 중 10 cell에서 3배 이상, q9/qid1·qid2 2 cell은 2.8~2.9×" 또는 "거의 모든 cell에서 3배 이상"

---

## §3. §5.4 표 5-2 plan 회복 매트릭스 검증

표 5-2 정의: oracle plan signature 기준 align 비율.

| qid | 보고서 B1 align | raw B1 align | 보고서 CaseB 평균 | raw CaseB | Q3 미달 method (보고서) | Q3 미달 method (raw) | status |
|---|:--:|:--:|:--:|:--:|---|---|:--:|
| qid 0 | 0/4 ★ | 0/4 (q3·q9·q10·q12 모두 misalign) | 12.8/13 | 51/52 = 12.75/13 ≈ 12.8/13 | hilbert_real | hilbert_real | PASS |
| qid 1 | 4/4 ★ | 4/4 (4 cell 모두 align) | 12.8/13 | 51/52 = 12.75/13 ≈ 12.8/13 | sparse_rp | sparse_rp | PASS |
| qid 2 | 3/4   | 3/4 (q3 misalign, 나머지 align) | 11.5/13 | 46/52 = 11.5/13 | 6 method split | hilbert_real, skilling_hilbert, chao_weighted, ica_fastica, hyperloglog, rabitq_strat (총 6 method) | PASS |
| 합계 | 7/12 (58%) | 7/12 (58.3%) | 148/156 = 94.9% | 148/156 = 94.87% | — | — | PASS |

**§3 표 5-2 종합**: **4/4 PASS** — 보고서 표 5-2 의 모든 cell이 raw plan_json 시그니처 비교와 1:1 정확 일치. plan_sig 정의((Node Type, Relation/Index, Join Type) pre-order)대로 비교한 결과, B1 align 합계 7/12, CaseB align 148/156 모두 정확.

부수: 보고서 line 402 "qid 0에서는 12 cell 중 4개의 cell 모두에서 베이스라인이 만든 plan이 정답 plan과 다르고" — 정확히 q3/qid0, q9/qid0, q10/qid0, q12/qid0 4 cell 모두 B1≠oracle → **PASS**.

부수: 보고서 line 404 의 q3/qid2 의 "6 method 분할" 도 raw 와 1:1 정확 (hilbert_real, skilling_hilbert, chao_weighted, ica_fastica, hyperloglog, rabitq_strat). → **PASS**

부수: 보고서 line 404 "hilbert_real의 Q-error 1.124, sparse_rp 1.310 등" → raw JSON 에서 hilbert_real Q-error = 1.124, sparse_rp = 1.310 — **PASS** (1:1 일치).

---

## §4. §5.5 표 5-3 + 본문 산문 검증

### 항목 23. baseline anchor 180/180 = 100% (line 422)
- 보고서 line 422 인용: "baseline (기본엔진) | 180 | **180 / 180 = 100%**"
- raw paired_stats.csv: baseline anchor row 180건, 모두 p_holm = 0.010986 (< 0.05)
- **PASS** (180/180 = 100% 정확)

### 항목 24. B1 anchor 13/168 = 7.7% (line 423)
- 보고서 line 423 인용: "B1 (베이스라인) | 168 | **13 / 168 = 7.7%**"
- raw paired_stats.csv: B1 anchor row 168건, p_holm < 0.05 비율 = 13건
- **PASS** (13/168 = 7.74% ≈ 7.7%)

### 항목 25. p_holm 분포 (line 425)
- 보고서 line 425 인용: "12 cell 각각의 15 variant에 대해 p_holm은 보정 전 p값의 바닥인 1/2^15 = 약 3.05e-5에 모이고 보정 후에는 약 1.10e-2 수준에 균일하게 분포한다."
- raw paired_stats.csv baseline anchor 180건 모두 p_value = 6.1035e-5, p_holm = 0.010986 (1.10e-2)
- **3.05e-5 claim — minor 부정확**: Wilcoxon n=15 의 양쪽꼬리 최소 p값은 2/2^15 = **6.10e-5** (= raw). 1/2^15 = 3.05e-5 는 **한쪽꼬리**에 해당. 보고서가 양쪽꼬리 검정을 하면서 한쪽꼬리 이론값을 claim
- "1.10e-2 균일 분포" — **PASS** (180건 모두 0.010986)
- **MINOR** — 결론 (1.10e-2 균일)은 정확하나 도출 이론 (1/2^15) 은 minor 부정확

### 보조 항목. line 427 "13건도 절반 이상이 베이스라인이 결합보다 약간 빠른 경우"
- 보고서 line 427 인용: "그 13건도 절반 이상이 베이스라인이 결합보다 약간 빠른 경우다."
- raw 13건 분석:
  - B1 빠른 (median_diff_ms < 0): 5건 (q12/qid0 4 + q9/qid0 1)
  - variant 빠른 (median_diff_ms > 0): 8건 (q3/qid2 7 + oracle 1)
  - 비율: B1 빠른 = 5/13 = 38.5% → **절반 미만**
- **MAJOR** — 실측과 반대 해석. variant(결합) 빠른 경우가 8/13 다수, B1 빠른 경우가 5/13 소수. raw 기준 정확 표현은 "13건 중 5건은 베이스라인이, 8건은 결합이 더 빠른 경우" 또는 "8건은 결합 빠른 경우"

### 보조 항목. line 427 "Q12 4 method (pca1d·rabitq_strat·sparse_rp·zorder_morton) p_holm = 0.0034 ... 약 9~16ms 더 빠른 케이스"
- 보고서 line 427 인용: "가장 강한 유의 신호는 Q12의 네 method(pca1d·rabitq_strat·sparse_rp·zorder_morton, p_holm = 0.0034)에서 나오는데 이들도 모두 베이스라인이 결합보다 약 9~16ms 더 빠른 케이스다."
- raw paired_stats.csv (q12/qid0, B1 anchor, 4 method):
  - p_holm = **0.0103** (4건 모두) — 보고서 0.0034 와 **약 3배 차이**
  - median_diff_ms = -39.8 / -34.4 / -34.6 / -36.9 (절댓값 34.4~39.8ms)
- **MAJOR (2건)** — p_holm = 0.0034 환각 (실측 0.0103), 9~16ms 차이 환각 (실측 34~40ms)

---

## §5. §5.6 honest 한계 5건 수치 검증

### 첫째 (line 439): "core 4 cell의 12개 측정 모두에서 베이스라인의 주입값이 1.0으로 클램프"
- 보고서 인용: "core 4 cell의 12개 측정 모두에서 베이스라인의 주입값(injected_card_seen)이 1.0으로 클램프되며"
- raw JSON 12 cell B1 의 injected_card_seen:
  - qid 0 (4 cell: q3·q9·q10·q12): **1.0** (모두 클램프, q_error=None)
  - qid 1 (4 cell): **4155.844156** (클램프 X)
  - qid 2 (4 cell): **10389.610390** (클램프 X)
- **MAJOR** — 12개 측정 중 4개 (qid 0)만 1.0 클램프. qid 1, qid 2 의 8개는 클램프되지 않음 (각각 4155.84, 10389.61 추정값). 보고서 "12개 측정 모두" claim 은 raw 와 정면 충돌
- raw 기준 정확 표현은 "core 4 cell × qid 0 의 4개 측정에서 베이스라인 주입값이 1.0으로 클램프되며, qid 1·qid 2 의 8개 측정에서는 베르누이 표본이 정상 적중하여 4,156·10,390 추정값이 주입된다" — 그리고 그 4개 cell (qid 0) 모두에서 정확히 B1 plan 이 oracle 과 다르다는 표 5-2 결과와 정합

### 둘째 (line 441): "추정값이 참 카디널리티보다 약 12~30% 과대 추정되면"
- 보고서 인용: "추정값이 참 카디널리티보다 약 12~30% 과대 추정되면 Hash Join이 잔존하는 plan으로 갈린다."
- raw Q3 미달 8건 q_error:
  - q3/qid0 hilbert_real: **1.124** (12.4% 과대)
  - q3/qid1 sparse_rp: **1.310** (31.0% 과대)
  - q3/qid2 hilbert_real: 1.163 / skilling_hilbert: 1.293 / chao_weighted: 1.150 / ica_fastica: 1.293 / hyperloglog: 1.212 / rabitq_strat: **1.406** (40.6% 과대)
- 실측 범위 = **12.4 ~ 40.6%** (sparse_rp 31% 와 rabitq_strat 41% 가 30% 초과)
- **MINOR** — 보고서 "12~30%"가 raw 의 12~41% 범위를 좁게 잡았다. 8건 중 2건 (sparse_rp, rabitq_strat) 이 보고서 범위 밖. 보다 정확한 표현은 "약 12~41% 과대 추정"

### 셋째 (line 443): "saturated·invariant cell의 latency 분산 측정은 §6.4의 향후 작업"
- 보고서 inline 수치 없음, 분류 분류만 — narrative claim → **N/A** (검증 대상 없음)

### 넷째 (line 445): DEEP·sf=10·256차원·8천만 행
- 보고서 인용: "DEEP 256차원·sf=10(8천만 행) 위에서 측정된다"
- raw JSON metadata: `"dataset":"DEEP","sf":10,"vec_table":"partsupp_x_deep_sf10"` 모두 정합. true_card 7603~8090 (sel=0.001 × 8천만 = 8천 = 일관)
- **PASS** (claim narrative + raw 일치)

### 다섯째 (line 447): plan signature 단순화 (Hash Join build/probe swap·Sort 위치)
- 보고서 inline 수치 없음, 정의 narrative → **N/A** (검증 대상 없음)

부수: 보고서 line 449 "13종 강한 method가 94.9%의 비율로 정답 plan을 견고하게 회복" — 148/156 = 94.87% — **PASS**.

부수: 보고서 line 449 "모든 12 cell에서 기본엔진 대비 3배에서 7배까지의 가속" — raw 12 cell speedup 범위 [2.93×, 7.40×]. 하한 2.93 (= q9/qid1) → 보고서 "3배" 와 미달 (3 대신 2.93). **MINOR** (반올림 영향).

---

## §6. 발견 issue catalog (severity 정리)

### CRITICAL
- **0건** — 표 데이터·매트릭스·통계 결과(180/180, 13/168, 148/156)에 자릿수 오류 없음.

### MAJOR (5건)
1. **line 381 "B1 12 cell 평균 1,005ms"** → 실측 968.7ms (차이 36.3ms, 3.7%). 환각 가능성: 다른 데이터 portfolio 의 B1 평균을 잘못 가져왔을 가능성. 수정 권고: "B1 평균 969ms vs oracle 957ms 차이 1.2% (5% 안쪽)"
2. **line 381 "모든 cell에서 베이스라인이 기본엔진 대비 3배 이상 빠르다"** → q9/qid1(2.81×), q9/qid2(2.90×) 2 cell이 3배 미달. 수정 권고: "거의 모든 cell에서 3배 이상 빠르며, Q9 의 두 cell(qid1·qid2)만 2.8~2.9×에 머문다" 또는 "10/12 cell에서 3배 이상"
3. **line 427 "13건도 절반 이상이 베이스라인이 결합보다 약간 빠른 경우"** → 실측 B1 빠른 5/13 (38.5%), variant 빠른 8/13 다수. 환각 가능성: B1 anchor median_diff 의 부호 해석 반전. 수정 권고: "13건 중 5건은 베이스라인이, 8건은 결합·정답이 더 빠른 경우"
4. **line 427 "Q12 4 method ... p_holm = 0.0034"** → 실측 p_holm = 0.0103 (4 method 모두). 약 3배 차이. 환각 가능성: 보정 전 p값 (`p_value` 컬럼) 약 5.7e-5 와의 헷갈림이 아니라 단순 자릿수 오타 추정. 수정 권고: "p_holm = 0.0103"
5. **line 427 "베이스라인이 결합보다 약 9~16ms 더 빠른 케이스"** → 실측 median_diff 절댓값 34.4~39.8ms (Q12 4 method). 약 4배 차이. 환각 가능성: 다른 컬럼 (variant_med 와 oracle_med 차이 등) 을 잘못 가져왔을 가능성. 수정 권고: "약 34~40ms 더 빠른 케이스"
6. **line 439 "core 4 cell의 12개 측정 모두에서 베이스라인의 주입값이 1.0으로 클램프"** → 실측 12 중 4개 (qid 0 cell 4개)만 1.0 클램프. qid 1·qid 2 8개는 4155.84·10389.61 정상 추정값. 수정 권고: "core 4 cell × qid 0 의 4개 측정에서 베이스라인 주입값이 1.0으로 클램프되며, qid 1·qid 2 의 8개 측정에서는 정상 추정값이 주입된다"

### MINOR (3건)
1. **line 404 "약 14% 정도 과대 추정"** → 미달 8건 평균 q_error = 1.215 (21.5% 과대). hilbert_real qid0=1.124 (12.4%) 만 가까움. 수정 권고: "약 12~41% 과대 추정"
2. **line 425 "보정 전 p값의 바닥인 1/2^15 = 약 3.05e-5"** → Wilcoxon 양쪽꼬리 최소는 2/2^15 = 6.10e-5 (= raw). 한쪽꼬리 이론값(1/2^15)을 보고. 수정 권고: "보정 전 p값의 바닥인 2/2^15 = 약 6.1e-5"
3. **line 441 "12~30% 과대 추정"** → 실측 범위 12~41% (sparse_rp 31%, rabitq_strat 41%). 수정 권고: "12~41% 과대 추정" 또는 "주로 12~30% 범위에서 과대 추정 (최대 41%)"

---

## main 종합 verdict 에 carry 할 fix 권고

검증 25 항목 중 **PASS 17 / MAJOR 5 / MINOR 3** (CRITICAL 0). 보고서 표·매트릭스·핵심 통계(180/180·13/168·148/156·평균 speedup 5.67×·oracle 평균 957ms)는 raw 와 1:1 정확하나, 본문 산문 6 줄에 정정이 필요하다.

### 즉시 fix 권고 (보고서 §5 본문 line 381, 427, 439, 441 정정)

```
line 381 (MAJOR ×2):
"베이스라인(B1)의 latency는 12 cell 평균 1,005ms로 정답(평균 957ms)과의 차이가 5% 안쪽이고, 모든 cell에서 베이스라인이 기본엔진 대비 3배 이상 빠르다."
→ "베이스라인(B1)의 latency는 12 cell 평균 969ms로 정답(평균 957ms)과의 차이가 1.2%로 매우 작고, 12 cell 중 10 cell에서 베이스라인이 기본엔진 대비 3배 이상 빠르며 Q9 의 두 cell(qid1·qid2)만 2.8~2.9× 가속에 머문다."

line 404 (MINOR):
"14% 정도 과대 추정만으로도"
→ "12~41% 과대 추정만으로도" 또는 hilbert_real 한정 표현 유지 (1.124 = 12%)

line 425 (MINOR):
"1/2^15 = 약 3.05e-5"
→ "2/2^15 = 약 6.1e-5 (양쪽꼬리 최소)"

line 427 (MAJOR ×3):
"168건 중 7.7%인 13건만이 베이스라인 대비 통계적으로 유의한 latency 차이를 보이며, 그 13건도 절반 이상이 베이스라인이 결합보다 약간 빠른 경우다. 가장 강한 유의 신호는 Q12의 네 method(pca1d·rabitq_strat·sparse_rp·zorder_morton, p_holm = 0.0034)에서 나오는데 이들도 모두 베이스라인이 결합보다 약 9~16ms 더 빠른 케이스다."
→ "168건 중 7.7%인 13건만이 베이스라인 대비 통계적으로 유의한 latency 차이를 보이며, 그 13건 중 5건은 베이스라인이, 8건은 결합·정답이 더 빠른 경우다. 가장 강한 유의 신호는 Q12의 네 method(pca1d·rabitq_strat·sparse_rp·zorder_morton, p_holm = 0.0103)에서 나오는데 이들 모두 베이스라인이 결합보다 약 34~40ms 더 빠른 케이스다."

line 439 (MAJOR):
"core 4 cell의 12개 측정 모두에서 베이스라인의 주입값(injected_card_seen)이 1.0으로 클램프되며"
→ "core 4 cell × qid 0 의 4개 측정에서 베이스라인 주입값(injected_card_seen)이 1.0으로 클램프되며 (qid 1·qid 2 의 8개 측정에서는 베르누이 표본이 정상 적중하여 약 4,156·10,390 추정값이 주입된다)"

line 441 (MINOR):
"약 12~30% 과대 추정되면"
→ "약 12~41% 과대 추정되면"
```

### main 종합에 carry 할 핵심 line 번호 + raw 값

| 보고서 line | 환각 수치 | raw 정합 값 | severity |
|---:|---|---|:--:|
| 381 | "B1 평균 1,005ms" | **968.7ms (969ms 반올림)** | MAJOR |
| 381 | "모든 cell ... 3배 이상" | **10/12 cell — q9/qid1·qid2 미달 (2.81×, 2.90×)** | MAJOR |
| 404 | "14% 정도 과대 추정" | **q_error 1.124 (hilbert_real qid0)만 14% 가까움; 8건 평균 21%** | MINOR |
| 425 | "1/2^15 = 3.05e-5" | **2/2^15 = 6.10e-5 (양쪽꼬리)** | MINOR |
| 427 | "절반 이상이 베이스라인이 더 빠른" | **5/13 (38.5%) — 절반 미만, variant 빠른 8/13** | MAJOR |
| 427 | "p_holm = 0.0034" | **p_holm = 0.0103** | MAJOR |
| 427 | "약 9~16ms 더 빠른" | **약 34~40ms 더 빠른** | MAJOR |
| 439 | "12개 측정 모두에서 1.0 클램프" | **4개 측정(qid 0)만 1.0; 8개는 4156·10390** | MAJOR |
| 441 | "12~30% 과대 추정" | **12~41%** | MINOR |

### 정합 ★ 항목 (carry 시 강조)
- 표 5-1 60 cell : raw 와 1:1 정확
- 표 5-2 plan 회복 매트릭스 7/12 + 148/156 : raw plan_json 시그니처 비교와 정확 일치
- 평균 speedup 5.67× : 정확
- oracle 평균 957ms : 정확
- 베이스라인 anchor 180/180 = 100% : 정확
- B1 anchor 13/168 = 7.7% : 정확
- p_holm 1.10e-2 균일 분포 : 정확
- Q3 qid2 6 method 분할 : 정확 (hilbert_real, skilling_hilbert, chao_weighted, ica_fastica, hyperloglog, rabitq_strat)
- Q-error 1.124 / 1.310 : 정확

종합: 표·매트릭스·통계 결과 자체는 신뢰할 수 있다. 본문 산문 6개 줄에 정정이 필요하다.
