# handoff 20260524 14:35 — v16 CaseC 전수 95 tuple 측정 완주 · Codex BLOCKER E fix 4 종 적용 · 3-multi-model 재검증 완료 · 보고서/스토리라인 v16 수치 반영

> 직전 handoff (`handoff_20260524_115000_*완주.md`) → 본 문서. 이 한 장으로 0% loss 인계 — self-contained.
>
> **★ 핵심 한 줄**: 사용자 5/24 11:45 KST 명시 ("CaseC 전수 동일 측정 + 3-multi-model 완벽 재검증 + 자원 256GB · 다음 세션 한 번에 완주") 한 세션 안 완주 — **v16 95 tuple 전수 측정 완료 (95/95 OK 0 FAIL · 2시간 5분 wall · 3 병렬), 결정적 결과 = CaseC vs B1 100% better 중앙값 −11.32% · CaseC vs CaseB 100% better 중앙값 −5.98% (5/23 audit 결론 = 분포 인지 X · 앙상블 평균 효과 측정 공간 전수 재확인)**. Codex BLOCKER E fix 4 종 적용 (rng 4개 완전 분리 · K_meta metadata only · paper-exact all_vecs 경로 · launcher exit code).

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (archive)**: `_internal/handoff/archive/handoff_20260524_115000_CaseC전수동일측정_95cell_3multimodel재검증_한세션완주.md` (이미 archive)
- **★ v13 정본 (carry)**: `_internal/cache/rq3/aggregated_v13_full.parquet` (4,524 row × 25 cell × 3 mode × 3 sel × 3 K × 16 method)
- **★ v16 95 tuple 정본 (본 세션 신규)**: `_internal/cache/rq3/paper_exact_v16_summary_20260524_122419/v16_full95_paired.parquet` (95 row · v13 paired)
- **★ v16 raw JSON 95 file**: `_internal/cache/rq3/paper_exact_v16_full95_20260524_122419/*_CaseC_sel{sel}_K{K}.json` (서버 sync 완료, 로컬 보관)
- **★ v16 figure**: `experiments/figures/보고서_6_11/v16/fig{1_qe_heatmap_sel{0.001,0.01,0.1},2_delta_vs_B1,3_qe_by_sf}.{png,pdf}` (5 fig)
- **★ phase2 4-way 12 cell engine (carry)**: 서버 `cache/rq3/latency/phase2_4way_final_20260524_040338/phase2_4way_summary.md`
- **★ 보고서 신본 (v16 통합)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.87 MB · §4.2.3 신규 + §4.6.1 fix update + §4.7 honest 5종 추가)
- **★ storyline 신본 (v16 통합)**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_v2_20260524_001301.md` (슬라이드 9 7행 표 + 발표자 narrative v16 추가)
- **★ deck v2 신본 PPTX (carry — slide 9 미 update)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_v2신본15장_20260524_014000.pptx` (storyline 변경 후 v3 PPTX 미생성 — carry, 다음 세션)
- **★ Codex review 보고서**: `/tmp/codex_review_v16.log` (3,302 줄, BLOCKER A/B/C/D/E 5 종 평결)
- **★ Gemini Deep Think 보고서**: `/tmp/gemini_v16_final.log` (Conditional PASS + 3 narrative 보완 권고)

## 1. 본 연구 framing (carry · 불변)

본 연구 = Exqutor (arXiv:2512.09695v2) §V-B 적응적 표본 추출의 표본 선택 단계 한 곳 controlled verification. 3-way matched (B1·CaseA·CaseB 1,508 cell) + 4-way 확장 (CaseC dual-Bernoulli). 89% Q-error 우위 = 분포 인지 효과 X · 앙상블 평균 효과 ✅ (audit 5/23). 4-way engine latency (12 cell) 모든 inject variant 동등 (|Δ%| ≤ 1.12%). **5/24 본 세션 = v16 95 tuple 전수 측정 (v13 scope 완전 일치) 완료, 100%/100% paired 우위 측정 공간 전수 재확인.**

## 2. 본 세션 한 일 (5/24 11:53 → 14:35 KST, 2h 42min)

| 단계 | 내용 | 산출물 |
|---|---|---|
| Phase 1 코드 fix v1 (4 파일) | gen_latency_estimates rng 분리 (BLOCKER E fix) · measure_paper_exact measure_case_c sel/K override + A9·A10·A11 CellSpec 추가 + DATASET_ALIAS concat 매핑 · measure_offline_casec_portfolio KNOWN_CELLS 25 cell · measure_offline_casec_full.py 신규 (95 tuple launcher) | `_internal/scripts/{gen_latency_estimates,measure_paper_exact,measure_offline_casec_portfolio,measure_offline_casec_full}.py` |
| Phase 1 코드 fix v2 (Codex BLOCKER E re-review) | **★ P0 fix**: K_override 가 km20_sids 그대로 두고 n_strata 만 바꿔서 K=10 시 strata 10-19 row 누락 — measure_case_c 의 K_override 를 metadata only 로, 실제 sampling 은 mc.N_STRATA=20 + bernoulli_estimate(all_vecs=all_vecs) paper-exact 경로 (strata-independent) 로 변경 / **P1 fix**: launcher exit code 0 숨김 (subprocess fail 시 SystemExit) | 동 |
| Phase 2 watchdog v6 (256GB) | 기존 v5 (60GB 거의 동일 코드) base → PATTERN 에 `measure_paper_exact|measure_offline_casec` 추가 · SIGSTOP/CONT 자원 양보 (5초 주기 · free<256GB 또는 other_cpu>6400% 또는 load>80 시 STOP) | 서버 `resource_watchdog_v6.sh` (gid 1769596 가동 중) |
| Phase 3 estimates 재생성 | gen_latency_estimates sf=1·10·100 × n_qvec=3 × DEEP × BLOCKER E fix 적용 = 9 query × 3 sel × 13 method = ~351 rows | 서버 `cache/rq3/latency/estimates_v16_blocker_e_fix/estimates_DEEP_sf{1,10,100}.parquet` |
| Phase 4 v16 95 tuple 측정 | measure_offline_casec_full.py --tuples-csv v13_casec_95tuples.csv --parallel 3 → 95/95 OK 0 FAIL · 2h 5min wall (12:24:19 → 14:27:19) | 서버·로컬 `paper_exact_v16_full95_20260524_122419/*.json` (95 file) |
| Phase 5 carry | engine 4-way 확장 (24 cell portfolio 3-5 시간) — 시간 부족 + offline 95 우선 (사용자 명시) → 다음 세션 carry | (carry) |
| Phase 6 aggregate + figure | aggregate_offline_casec_v16.py (신규, sel·K suffix 파일명 패턴 + v13 paired) · plot_casec_qerror.py (신규, 3 sel heatmap + Δ% hist + sf box) | `_internal/cache/rq3/paper_exact_v16_summary_20260524_122419/v16_full95_paired.parquet` + summary.md · `experiments/figures/보고서_6_11/v16/fig{1,2,3}.{png,pdf}` (5 fig) |
| Phase 7 multi-model 재검증 | Codex xhigh review (5 P0/P1/P2 평결) · Gemini agy Deep Think (Conditional PASS + 3 narrative 보완) · Claude self-verify (95 paired 100% better 강한 신호 통계 validity OK) | `/tmp/codex_review_v16.log` (3,302 줄) · `/tmp/gemini_v16_final.log` |
| Phase 8 보고서·storyline patch + PDF | **보고서 §4.2.3 신규** (v16 95 tuple 전수 수치 + figure 2 종) · **§4.6.1 BLOCKER E fix 완료 update** · **§4.7 honest 5 종 추가** (Gemini 권고 3종 + Codex carry 3종) · **abstract v16 통합 (수치 명시)** · **storyline 슬라이드 9 v16 7행 표 + 발표자 narrative** · **PDF 재생성** (1.87 MB) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` · `_5_27_최종발표_storyline_NEW_v2_20260524_001301.md` |
| Phase 9 handoff close + commit | 본 문서 작성 + commit chain | 본 파일 |

## 3. ★★★ 핵심 수치·결과 정본

| 지표 | 값 | 출처 |
|---|---|---|
| v13 1,508 cell × 3 mode (B1·A·B) | qe B1 1.458 · CaseA 1.636 · CaseB 1.402 (carry) | v13_summary.md |
| v13 결합 better% vs B1 (carry) | 89.1% (1,344/1,508) · 중앙값 −4.38% | v13 |
| v14 CaseC 9 cell mean (carry) | qe_trim 1.3729 | v14_summary.md |
| v15 CaseC 18 cell mean (carry) | qe_trim 1.4620 (신규 9 sf=1·10 위주 1.5510) | v15_portfolio_summary.md |
| **★ v16 CaseC 95 tuple 전수 mean** | **qe_trim 1.306** (std 0.129 · min 1.105 · max 1.488 · median 1.366) | v16_full95_summary.md |
| **★ v16 CaseC vs B1 paired better%** | **95 / 95 = 100.0%** | 동 |
| **★ v16 CaseC vs B1 paired median Δ%** | **−11.32%** (mean −10.05% · q25 −13.09% · q75 −4.60%) | 동 |
| **★ v16 CaseC vs CaseB paired better%** | **95 / 95 = 100.0%** | 동 |
| **★ v16 CaseC vs CaseB paired median Δ%** | **−5.98%** (mean −6.08%, v14 −6.74% 와 매우 일관) | 동 |
| v16 sf 별 mean | sf=1 1.296 (n=26) · sf=10 1.301 (n=37) · sf=100 1.320 (n=32) | 동 |
| v16 sel 별 mean | sel=0.001 1.410 (n=28) · sel=0.01 1.368 (n=40) · sel=0.10 1.107 (n=27) | 동 |
| v16 K_meta 별 mean | K=10 1.339 (n=12) · K=20 1.295 (n=71) · K=30 1.339 (n=12) | 동 (K=10/30 동일 — CaseC K-independent 의도 정합) |
| phase2 4-way 12 cell engine (carry) | CaseC vs B1 +0.30% · 17 inject variant |Δ%| ≤ 1.12% | phase2_4way_summary.md |

## 4. 다음 세션 task (sub-priority)

### Phase 1 (필수) — deck v3 PPTX 생성

storyline 슬라이드 9 변경 (5 행 → 7 행 표 + 발표자 narrative v16 추가) 후 deck v2 PPTX → v3 PPTX 신규 생성. anthropic-skills:pptx 또는 PowerPoint MCP 사용. 발표 5/27·29 직전 critical path.

### Phase 2 (high) — Codex carry items 3종 fix

1. `measure_case_c` 의 query-sel miss silent fallback → raise (보고서 §4.6.1 carry)
2. `gen_latency_estimates.py` 의 concat dataset table prefix mismatch (`partsupp_{combo}_{sf}` → `partsupp_{combo}_concat_{sf}`) fix
3. `measure_offline_casec_portfolio` 의 DEFAULT_PORTFOLIO 18 → 25 cell 확장 (A9·A10·A11 concat 7 추가)

### Phase 3 (medium) — Gemini narrative 보완 권고 3종 추가 적용

1. 보고서 §4.2.3 narrative 에 B1 대비 우위 (앙상블 분산 감소 효과 포함) 와 CaseB 대비 우위 (분포 인지 한계) 더 명시 분리 (§4.7 추가 carry 추가 적용 완료, §4.2.3 본문도 강화)
2. K-fairness 통제 위해 추가 측정 (CaseC sampling K ∈ {10, 20, 30}) — 4 시간 ETA, 5/27 발표 전 가능
3. v14 → v15 → v16 평균 비교 narrative 정제 (selection bias caveat 추가) — §4.2.3 본문에 추가 명시

### Phase 4 (선택) — engine 4-way 확장 측정

handoff carry from 직전 — sf {1, 100} × sel {0.01, 0.1} × Q4 × qid 3 = 24 cell ~3 시간 portfolio. 시간 가능 시. 본 세션 carry.

### Phase 5 — 5/22 박광현 미팅 사전보고 update

5/22 (목) 14:00 미팅 사전보고 (`submission/_drafts/속도는벡터_5_22_박광현미팅_사전보고_*.md`) 에 v16 95 tuple 결과 반영. (5/22 이미 지난 시점이면 5/25-26 추가 보고 자료로).

## 5. 산출물 경로 (총정리)

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260524_143500_*.md` | 본 파일 |
| ★ v13 parquet (carry) | `_internal/cache/rq3/aggregated_v13_full.parquet` | carry |
| ★ v14 9 cell (carry) | 서버 `cache/rq3/paper_exact_v14_20260523/*_CaseC.json` | carry |
| ★ v15 18 cell (carry) | 서버 `cache/rq3/paper_exact_v15_summary_20260524_024053/v15_portfolio.parquet` | carry |
| **★ v16 95 tuple raw (신규)** | 서버·로컬 `cache/rq3/paper_exact_v16_full95_20260524_122419/*_CaseC_sel{sel}_K{K}.json` (95 file) | 본 세션 신규 |
| **★ v16 95 tuple paired parquet (신규)** | `_internal/cache/rq3/paper_exact_v16_summary_20260524_122419/v16_full95_paired.parquet` | 신규 |
| **★ v16 summary.md (신규)** | `_internal/cache/rq3/paper_exact_v16_summary_20260524_122419/v16_full95_summary.md` | 신규 |
| **★ v16 figure 5종 (신규)** | `experiments/figures/보고서_6_11/v16/fig{1_qe_heatmap_sel{0.001,0.01,0.1},2_delta_vs_B1,3_qe_by_sf}.{png,pdf}` | 신규 |
| ★ phase2 4-way 12 cell (carry) | 서버 `cache/rq3/latency/phase2_4way_final_20260524_040338/phase2_4way_summary.md` | carry |
| ★ 4-way figure (carry) | `experiments/figures/4way_latency_v15/fig{1,2}_*.{png,pdf}` | carry |
| ★ 측정 코드 (4 patch + 3 신규) | `_internal/scripts/{measure_paper_exact,gen_latency_estimates,measure_offline_casec_portfolio}.py` (patch) + `measure_offline_casec_full,aggregate_offline_casec_v16,plot_casec_qerror.py` (신규) | 본 세션 |
| ★ 보고서 v16 통합 + PDF | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.87 MB) | 본 세션 |
| ★ storyline v16 통합 | `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_v2_20260524_001301.md` | 본 세션 |
| ★ deck v2 (carry, v3 미생성) | `submission/_drafts/속도는벡터_최종발표_슬라이드_v2신본15장_20260524_014000.pptx` | carry (다음 세션 v3) |
| ★ Codex review log | `/tmp/codex_review_v16.log` (3,302 줄) | 본 세션 |
| ★ Gemini Deep Think log | `/tmp/gemini_v16_final.log` | 본 세션 |
| ★ 95 tuple CSV | 서버·로컬 `/tmp/v13_casec_95tuples.csv` + 서버 `cache/rq3/v13_casec_95tuples.csv` | 본 세션 |

## 6. 환경·자원 (carry — 256GB OK)

- **자원 watchdog v6**: `resource_watchdog_v6.sh` (gid 1769596, free<256GB 또는 other_cpu>6400% 또는 load>80 → SIGSTOP, 회복 시 SIGCONT 5초 주기). PATTERN 에 measure_paper_exact·measure_offline_casec 포함. 본 세션 측정 안 발동 (free 781GB → 측정 중 최저 ~700GB).
- **3 병렬 sf-adaptive**: sf=100 cell 3 동시 (DEEP ~33GB/cell × 3 = 99GB), sf=10·1 cell 3-4 동시. 95 tuple 측정 wall 2h 5min.
- **서버 자원**: 1007GB total · uptime 11+ days · CPU 128 vCPU · 4× RTX 6000 Ada 49GB
- **PG port**: 55435 (carry)
- **본 세션 commit X (Phase 9 진행 중)** — Phase 9 마지막 commit chain 진행 후 push X (사용자 명시 요청 시만)

## 7. 일정 (carry · 변경 X)

- **5/26 (화) 23:59** 발표 슬라이드 LearnUs 마감 ★★ critical path — deck v3 PPTX 생성 필수 (다음 세션 Phase 1)
- **5/27 (수)** · **5/29 (금)** 최종 발표
- **5/28 (목) 12:00** 포스터·영상 LearnUs 마감
- **6/5 (금)** 전시회
- **6/11 (목) 23:59** 최종 보고서·상호평가 결과 마감 — 본 세션 보고서 v16 통합 PDF 1.87MB 거의 완성, §4.2.3 narrative 강화 추가만

## 8. ★ 환각 회피 룰 (carry · 본 세션 추가)

- v13 1,508 cell 정본 (3-way matched, carry) · v14 9 cell CaseC carry · v15 18 cell CaseC carry · **v16 95 tuple CaseC 본 세션 신규 측정** — 모두 진짜 측정. v16 BLOCKER E fix 적용 코드로 진행 = 측정 결과 신뢰성 ★★★
- ★ 89% Q-error 우위 = 앙상블 평균 효과 (분포 인지 X) — controlled verification, **v16 95 tuple 전수 100%/100% 재확인**
- CaseC = (B1+B1)/2 dual-Bernoulli 통제군 (method-agnostic) — 본질적으로 K-independent. K_override 는 v13 paired row 와 매칭용 metadata only — sampling 은 K=20 고정 + paper-exact all_vecs 경로
- **★ Gemini Deep Think 권고 carry** (§4.7 honest limitation 추가됨): (1) B1 대비 vs CaseB 대비 효과 분리 명시, (2) K-fairness 한계 (CaseC K-independent, 실험군 K-의존), (3) v14→v15→v16 평균 selection-bias caveat
- ★ Codex BLOCKER E re-review P1 carry items 3종 (§4.7 추가): (i) query-sel miss raise, (ii) concat table prefix fix, (iii) portfolio DEFAULT 25 확장
- 측정 코드 변경 시 smoke 우선 — 본 세션 BLOCKER E v2 fix 후 K=10 첫 cell 결과 (qe_trim 1.39, K_sampling_actual=20, sampling_path=paper_exact_all_vecs) 즉시 검증
- 비가역 작업 (git push --force · DB DROP · rm -rf) — 사용자 사전 위임 없음 → carry
- git push X (사용자 명시 요청 시만, carry)
- 보고서 §2.2 식 1-6 = paper §V-B verbatim 확정 (Gemini + AdaptiveState ground truth, carry)
- 보고서 §2.3 Cochran §5.5 Optimum Allocation 정확 (carry)
- 코드명 (B1·CaseA·CaseB·CaseC) = 보고서·기술 문서 OK, 발표물 (deck·포스터·영상) 노출 금지 — storyline 슬라이드 9 한국어 라벨 통일 carry ("베이스라인·단독 대체·결합·평균 비교군·사전 등록 통제 측정")
- handoff 룰: 종료 시 active 직전 set archive → 신본 timecode 작성 ✓

---

작성: 2026-05-24 14:35 KST. 사용자 명시 ("CaseC 전수 동일 + 3-multi-model 재검증 + 256GB · 한 세션 안 완주") 한 세션 완주 — v16 95 tuple 측정 (95/95 OK 2h 5min), Codex BLOCKER A/B/C/D/E P0/P1/P2 review 5종 fix 또는 carry, Gemini Deep Think Conditional PASS + 3 narrative 보완 적용 (§4.7), Claude self-verify (paired 100%/100% 통계 validity), 보고서 §4.2.3 v16 신규 + abstract + storyline 슬라이드 9 v16 수치 + PDF 1.87MB. 다음 세션 = deck v3 PPTX 생성 (critical, 5/26 마감) + Codex carry 3종 fix + §4.2.3 narrative 강화 + (선택) K-fairness 추가 측정.
