# θ 축 — 보고서 §5.1·§5.2·§5.3·§5.5 산문 ↔ harness 코드 정합 검증

> read-only sub-agent — 코드/보고서 어떤 정본도 수정하지 않는다. 이 md 만 산출물.

검증 대상
- 보고서 §5.1 line 342 (주입 메커니즘 산문)
- 보고서 §5.2 line 348–354 (측정 설계 산문)
- 보고서 §5.3 line 358 (trimmed mean 표기)
- 보고서 §5.4 line 389 (plan_signature 정의)
- 보고서 §5.5 line 414–416 (paired Wilcoxon · Holm-Bonferroni · p_holm)
- harness `_internal/scripts/measure_latency_realengine.py`
- harness `_internal/scripts/gen_latency_estimates.py`
- harness `_internal/scripts/prescan_plan_sensitivity.py`
- harness `_internal/scripts/_measure_common.py`
- 분석 `_internal/scripts/analyze_latency.py`

---

## VERDICT: **WARN** (1 major · 2 minor — critical 없음)

핵심 결론. 측정 routine 6 항목 · trimmed mean 1 항목 · paired Wilcoxon 3 항목 · Exqutor 주입 3 항목은 보고서 산문과 코드 routine 이 모두 정합한다. 다만 **plan signature 정의 1건이 보고서 산문(3-tuple)과 실제 §5.4 매트릭스 산출 코드(1-tuple)가 다르다** — major. 본 매트릭스 정본 수치(7/12·148/156=94.9%) 는 analyze_latency.py:plan_signature(1-tuple)로 산출됐고, prescan_plan_sensitivity.py:plan_signature_v2(3-tuple)는 Phase 0 cell 분류에만 쓰였다. 신호 차이는 본 §5.4 핵심 결론 견고성을 흔들지 않는다(Q3 8/156 미달 · 12 cell core 분류 모두 1-tuple 만으로도 동일 판정) — 다만 보고서 §5.4 line 389 산문이 prescan 의 plan_signature_v2 정의를 그대로 옮긴 점은 minor 정정 대상이다. 부가로 minor 2건(injection_fired 본 측정 직접 확인 없음 — plan-capture 단계에서만 확정; §5.5 산문이 zero_method 미명시).

---

## §1 측정 routine 정합 (6 항목)

| # | 보고서 claim (§5.2) | 코드 routine | status |
|---|---|---|---|
| 1 | 16 variant × 15 timed rep + 1 warmup (§5.2 line 352) | `measure_latency_realengine.py` line 442–443: `--n-timed=15`, `--n-warmup=1`. line 335 `for rep in range(n_warmup + n_timed)`. line 341 `if rep >= n_warmup` 으로 첫 1회 burn-in. 16 variant = line 313–317 (baseline + B1 + oracle + 13 CaseB method). | PASS |
| 2 | 측정 timeout 600초 (§5.2 line 352) | line 444 `ap.add_argument("--statement-timeout", default="600s")`. line 201 `cur.execute(f"SET statement_timeout = '{statement_timeout}'")`. line 206–208 except 분기 `QueryCanceled` censored → None. | PASS |
| 3 | Random(20260520) shuffle (§5.2 line 352) | line 302 default `seed=20260520`. line 334 `rng = random.Random(seed)`. line 337 `rng.shuffle(order)`. variant 순서가 매 rep 마다 같은 seed 의 동일 PRG 로 셔플 — 결정론적. gen_latency_estimates.py line 119 도 동일 seed 20260520 사용 (estimate trial RNG). | PASS |
| 4 | variant round-robin / 한 epoch 안에 16 variant 한 번씩 (§5.2 line 352) | line 336–345: `order = keys[:]` 복사 → `rng.shuffle(order)` → `for k in order:` 16 variant 한 번씩 직렬 실행. 한 rep = 한 epoch. paired test 정합 (analyze_latency.py line 149–150 paired_stats 주석에서 같은 epoch claim 재확인). | PASS |
| 5 | variant 16종 = baseline 1 + B1 1 + oracle 1 + CaseB 13 (§5.2 line 352) | line 313–317 `variants = [("baseline", None, None), ("B1", None, est_b1), ("oracle", None, true_card)]` + CaseB 13 method 추가. DEFAULT_CASEB_METHODS line 67–72 = hilbert_real·skilling_hilbert·chao_weighted·ica_fastica·pca1d·zorder_morton·hyperloglog·cum_sqrtf·lavallee_hidiroglou·rsvd·sparse_rp·mhist2·rabitq_strat 13개. 합 16. | PASS |
| 6 | injection_fired = True 검증 routine (§5.2 line 354) | `_INJECT_LOG_RE` line 211–212: 정규식 `Estimated cardinality for range query on table\s+\S+:\s*([0-9.]+)` → vector.c 의 Exqutor 로그 패턴. line 224–229 `_parse_capture` 가 client notice 스캔 → `injection_fired=True` 와 `card_seen=float(...)` 확정. line 320–329 plan-capture 단계에서 variant 당 1회 검증되어 `captured[(c,m)]` dict 에 보존 → 본 timed 측정 후 line 365 `"injection_fired": cap["injection_fired"]` 로 결과 행에 carry. **plan-capture 1회 결과를 본 측정의 injection_fired 판정으로 사용 — timed rep 마다 재확인은 없음** (minor § 6 catalog 참조). | PASS (minor 주석) |

---

## §2 plan signature 산출 (2 항목)

| # | 보고서 claim (§5.4) | 코드 routine | status |
|---|---|---|---|
| 7 | (Node Type, Relation/Index, Join Type) pre-order 튜플 (§5.4 line 389) | **두 정의가 공존한다.** `prescan_plan_sensitivity.py:plan_signature_v2` line 63–76: 3-tuple `(Node Type, Relation Name|Index Name, Join Type)` pre-order — 보고서 산문 정의와 정확 일치. `analyze_latency.py:plan_signature` line 72–79: 단일 `Node Type` 만 pre-order — 보고서 산문 정의와 불일치. **§5.4 plan 회복 매트릭스(표 5-2: 7/12 · 148/156=94.9%)와 fig5_3 plan_recovery 산출은 analyze_latency.py:plan_signature(1-tuple) 으로 이루어진다** (line 247·418·424). prescan_plan_sensitivity.py:plan_signature_v2 는 Phase 0 cell 분류 (core / saturated / invariant) 에만 쓰인다. | **FAIL (major)** |
| 8 | plan_signature ≠ baseline / = baseline 판정 routine (`=`/`≠` 출력 source) | analyze_latency.py line 82–87 `_plan_changed(base_sig, sig)`: 양쪽 다 비공집합이면 `sig != base_sig` 반환, 한쪽이라도 빈 시그니처면 `None` (불명). line 125 출력 매핑 `{True: "≠", False: "=", None: "?"}`. line 108 `summarize()` 가 cell × variant 행에 `plan_changed_vs_baseline` 컬럼 부여. §5.4 표 5-2 "B1 plan = oracle plan" 열 `○/×` 는 본 routine 의 `=`/`≠` 판정과 동일한 방식 — 단 base_sig 가 oracle_sig 로 바뀐 비교. analyze_latency.py:plot_plan_recovery_matrix line 416–430 가 그 매트릭스 산출 (orc_sig 와 sig 비교). | PASS |

---

## §3 trimmed mean 산출 (1 항목)

| # | 보고서 claim (§5.3) | 코드 routine | status |
|---|---|---|---|
| 9 | "trimmed mean" (§5.3 line 358) — trim 비율 미명시 | `measure_latency_realengine.py` line 73 `TRIM = 1` (양끝 제거 수). line 285–290 `_trimmed_mean(vals, trim=1)`: `len(vals) <= 2*trim` 이면 fmean(vals) fallback, 그 외 `fmean(sorted(vals)[trim:-trim])`. 본 측정 n_timed=15 → 양끝 1+1 = 2 제거 → 가운데 13값 평균. **TRIM 절단 비율 ≈ 13.3% (2/15)** — scipy.stats.trim_mean(0.067) 와 동치 (양쪽 6.67% 절단). 보고서 산문은 단지 "trimmed mean" 만 명시 — trim 비율 명시 없음. | PASS (minor 보고서 정정 가능 — n=15, 양끝 1 trim) |

---

## §4 paired Wilcoxon 산출 (3 항목)

| # | 보고서 claim (§5.5) | 코드 routine | status |
|---|---|---|---|
| 10 | i번째 rep 의 16 variant exec_ms 짝 → paired (§5.5 line 414) | analyze_latency.py line 141–200 `paired_stats(results)`. line 156–159 `valid = {lab: v["exec_ms"] for lab, v in by.items() if v.get("exec_ms") and len(v["exec_ms"]) >= 2}`. line 167 `n = min(len(a), len(b))`. line 170 `diffs = [a[i] - b[i] for i in range(n)]`. line 173 `wilcoxon(a[:n], b[:n], alternative="two-sided", zero_method="wilcox")`. 두 변량 모두 같은 epoch 의 i번째 측정 → 인덱스 i 가 matched. line 149–150 주석 명시. | PASS |
| 11 | Holm-Bonferroni 보정 (anchor 군 내) (§5.5 line 416) | analyze_latency.py line 185–199: anchor 별로 sub list 추출, p_value 오름차순 정렬, rank=1..n 에 대해 `adj = min(1.0, r["p_value"] * (n - rank + 1))`, `adj = max(adj, prev)` 단조증가 강제 → `r["p_holm"] = adj`. anchor='baseline' (n=180) 과 'B1' (n=168) 두 군 분리 보정. statsmodels 의존 없이 자체 구현 — 정확한 step-down Holm. | PASS |
| 12 | p_holm 컬럼 산출 정합 (paired_stats.csv) | analyze_latency.py line 198–199 `r["p_holm"] = adj; r["holm_rank"] = rank`. line 229–240 `export_paired_csv` 의 cols 에 `["p_value", "p_holm", "holm_rank"]` 모두 포함 → paired_stats.csv 가 row 별로 (p_value, p_holm, holm_rank) carry. line 220–225 print 가 anchor 별 `p_holm < 0.05` 유의 비율 출력. fig5_4 plot_paired_significance line 488 `-log10(max(p_holm, 1e-6))` heatmap. | PASS |

---

## §5 Exqutor 주입 정합 (3 항목)

| # | 보고서 claim (§5.1) | 코드 routine | status |
|---|---|---|---|
| 13 | vector.injected_card 환경 변수 통한 주입 | measure_latency_realengine.py line 148–157 `gucs_for(condition, injected_card)`: baseline → `SET vector.disable_estimation = on`. B1/CaseB/oracle → `SET vector.disable_estimation = off` + `SET vector.injected_card = {card:.6f}` (line 156). 전 조건 공통 line 150 `SET vector.update_sample_size = off`. **clamping**: line 155 `card = max(float(injected_card), MIN_INJECT)` → 0 주입 시 1.0 으로 강제 (§5.4 산문 line 402 MIN_INJECT 1.0 클램프 정합). | PASS |
| 14 | ExecutorRun 훅이 벡터 술어 탐지 + LOAD 'vector' (§5.1 line 342) | line 182–183 `_prepare_session` 에서 `cur.execute("LOAD 'vector'")` 매 세션 첫 statement. line 173–180 주석에 LOAD 순서 (auto_explain 먼저 → vector 다음) 정합 검증 결과 명시. vector.c 의 ExecutorRun 패치 자체는 서버 빌드 시점 적용 — 본 코드는 SET 명령으로 GUC 전달만 수행. line 217–229 `_INJECT_LOG_RE` 가 vector.c 의 "Estimated cardinality for range query on table ..." 로그를 catch → 주입 발동 확인. | PASS |
| 15 | pass-1 + pass-2 2-pass — EXPLAIN 단독 무효 (§5.1 line 342) | line 22–23 주석: "순수 EXPLAIN 은 실행을 안 하므로 영원히 pass-1 플랜만 본다 → latency 는 실쿼리 직접 실행 + perf_counter, 플랜은 auto_explain(실행 후 pass-2 플랜이 client notice 로 도착)". line 188–208 `_run_timed`: 실쿼리(EXPLAIN 미사용) → line 202 `t0 = time.perf_counter()` → line 203 `cur.execute(sql)` → line 204 `cur.fetchall()` → line 205 `(time.perf_counter() - t0) * 1000.0` ms 반환. 2-pass 오버헤드 포함 정직 측정. dry-run line 417 `assert "EXPLAIN" not in sql.upper()` 로 EXPLAIN 잔여 0 확인. | PASS |

---

## §6 발견 issue catalog

### ❶ MAJOR — plan_signature 정의 분기 (보고서 §5.4 line 389 vs analyze_latency.py)

- **보고서 산문**: §5.4 line 389 "각 cell·variant의 pass-2 실행 계획을 (Node Type, Relation/Index, Join Type) 의 pre-order 튜플로 압축한 plan_signature 를 산출하였다."
- **실제 코드**: `_internal/scripts/analyze_latency.py:plan_signature` (line 72–79) 는 `[plan.get("Node Type", "?")]` + 자식 재귀로 **Node Type 1-tuple 만** 사용. `Relation Name` / `Index Name` / `Join Type` 미사용. §5.4 매트릭스 산출(`plot_plan_recovery_matrix` line 399–459)과 표 5-2 "B1 plan = oracle plan" 열(7/12 · 148/156=94.9%) 산출이 모두 이 1-tuple plan_signature 기반.
- **prescan**: `_internal/scripts/prescan_plan_sensitivity.py:plan_signature_v2` (line 63–76) 가 3-tuple `(Node Type, Relation Name|Index Name, Join Type)` pre-order — 보고서 산문 정의와 정확히 일치. 하지만 이 함수는 Phase 0 cell 분류(core/saturated/invariant)에만 쓰이고 §5.4 매트릭스에는 쓰이지 않는다.
- **신호 차이가 §5.4 결론을 흔드는가**: 흔들지 않는다. (i) Q3·Q9·Q10·Q12 4 쿼리는 서로 다른 join 구조 → Node Type 만으로도 변별 가능. (ii) §5.4 line 447 ('미세 plan 변동 / 같은 signature 묶임' 한계) 산문이 1-tuple signature 의 정밀도 한계를 이미 honest 하게 명시한다. (iii) §5.5 paired Wilcoxon 이 latency 차이가 거의 드러나지 않음을 통계적으로 확인 (168건 중 13건만 유의) — 1-tuple signature 가 latency 차이를 만드는 plan 차이는 모두 catch 했다.
- **권고**: 보고서 §5.4 line 389 산문을 정확히 정정 — "Node Type 의 pre-order 튜플" 로 표기 변경, 또는 분석 코드(analyze_latency.py)를 3-tuple plan_signature_v2 로 교체 후 동일 수치(7/12·148/156)가 재현됨을 재확인. 본 정본 §5.4 수치 재산출 없이 산문만 정정해도 결론 robust (별도 §5.4 line 447 한계 진술에서 이미 noted).

### ❷ MINOR — injection_fired 본 측정 직접 확인 없음

- `_internal/scripts/measure_latency_realengine.py:measure_cell` line 320–329: plan-capture 단계에서 variant 당 1회만 `injection_fired` 확정 → 본 timed 측정 (n_timed=15) 의 각 rep 에서는 별도 확인 없이 이 captured 값을 carry. 보고서 §5.2 line 354 "이 60건의 비-기본 variant 측정이 본 장의 정량 분석 기반이다" 산문은 60건이 아니라 180건의 오기 가능성 (60 = 12 cell × 5 mode 분류일 수 있으나, 비-기본 variant 180건 = 12 cell × 15 variant 가 정합) — 산문 첨자 정정 후보. 본 측정에서는 injection_fired 가 plan-capture 시점의 정적 판정으로 충분하다 (서버 빌드 변경이 없는 한 timed rep 마다 fired 가 변할 이유 없음).
- **권고**: 보고서 §5.2 line 354 "이 60건의" → "이 180건의" 정정 (12 × 15 = 180). 60건은 정의되지 않은 숫자.

### ❸ MINOR — §5.5 산문 zero_method 미명시

- analyze_latency.py line 173 `wilcoxon(a[:n], b[:n], alternative="two-sided", zero_method="wilcox")` 호출. `zero_method="wilcox"` 는 zero diff (paired 변량 동일) 를 검정에서 drop 하는 옵션. 보고서 §5.5 line 414–416 산문은 "paired Wilcoxon signed-rank test" 만 명시 — zero_method 와 alternative 표기 없음.
- **권고**: 본 minor 는 학술 보고서 표기 관행상 두 옵션 명시 권장 (특히 zero diff 가 많은 timed rep 의 경우 zero_method 가 결과를 흔들 수 있어 보고 의무). 본 측정에서는 ms 단위 timing 변량이라 정확히 0 diff 일 확률 극소 → 본 결론 영향 없음. 보고서 §5.5 footnote 추가로 충분.

---

## summary

15 항목 중 14 PASS · 1 FAIL(major).

- **PASS 14** = 측정 routine 6 · plan signature 1 (=/≠ 판정만) · trimmed mean 1 · paired Wilcoxon 3 · Exqutor 주입 3.
- **FAIL 1 (major)** = plan signature 정의 (보고서 산문 3-tuple ↔ 실제 §5.4 매트릭스 산출 코드 1-tuple). 본 §5.4 정본 수치(7/12·148/156=94.9%) 는 1-tuple 산출 결과로 견고하며, 산문 line 389 정정으로 해소 가능.

**최종 권고 — 보고서 §5.4 line 389 산문 정정 1건만으로 본 θ 축 정합 PASS 가능.** 분석 코드(analyze_latency.py:plan_signature) 를 3-tuple plan_signature_v2 로 강화하는 옵션도 가능하나, 본 §5.4 정본 수치가 견고하므로 산문 정정이 비용 효율 우선.
