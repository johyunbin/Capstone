# handoff 20260524 11:50 — CaseC 전수 동일 측정 (95 cell · v13 scope 완전 일치) · 3-multi-model 재검증 · 자원 watchdog 256GB free · 한 세션 안 완주

> 직전 handoff (`handoff_20260524_041000_엔진4way완주_*세션종료.md`) → 본 문서. 이 한 장으로 0% loss 인계 — self-contained.
>
> **★ 핵심 한 줄 (사용자 명시 5/24 11:45 KST)**: "**CaseC 도 CaseA·B 와 전수 동일 (1,508 cell scope) 측정 + 3-multi-model 완벽 재검증을 다음 세션 한 번에 완주**. 서버 자원 256GB RAM 여유 보장." — 본 세션은 4-way controlled experiment 골격만 완성 (CaseC 18/95 tuples), 다음 세션 = **77 신규 tuples 전수 측정 + Codex BLOCKER E fix + 측정 결과 적대 재검증 + 보고서·storyline·deck final patch + 한 세션 완주**.

## 0. 정본·진입점

- **★ 본 handoff** — 이 문서 하나로 인계
- **★ 직전 handoff (archive)**: `_internal/handoff/archive/handoff_20260524_041000_*세션종료.md` (이미 archive)
- **★ v13 정본 (CaseA·CaseB 1,508 cell scope)**: `_internal/cache/rq3/aggregated_v13_full.parquet` (4,524 row · 25 cell · 3 sel · 3 K · 16 method · 3 mode)
- **★ v13 unique (cell × sel × K) tuples 정본**: **95 tuples** (sparse 평면 — 본 handoff §4 표 참조)
- **★ v14 CaseC carry**: 9 tuples (5/23) — mean qe_trim 1.3729
- **★ v15 CaseC 신규**: 9 tuples (5/24 본 세션) — mean qe_trim 1.5510
- **★ 현재 측정 완료 = 18 tuples** (모두 K=20 default · selectivities[0])
- **★ 미측정 = 77 tuples** (sel·K ablation + A9·A10·A11 concat cells)
- **★ phase2 4-way 12 cell engine 정본**: `phase2_4way_final_20260524_040338/phase2_4way_summary.md` — CaseC vs B1 +0.30% 동등
- **★ 보고서 신본**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.71MB)
- **★ storyline 신본**: `submission/_drafts/속도는벡터_5_27_최종발표_storyline_NEW_v2_20260524_001301.md`
- **★ deck v2 신본 PPTX**: `submission/_drafts/속도는벡터_최종발표_슬라이드_v2신본15장_20260524_014000.pptx`

## 1. 본 연구 framing (carry · 불변)

본 연구 = Exqutor (arXiv:2512.09695v2) §V-B 적응적 표본 추출의 표본 선택 단계 한 곳 controlled verification. 3-way matched (B1·CaseA·CaseB 1,508 cell) + 4-way 확장 (CaseC dual-Bernoulli). 89% Q-error 우위 = 분포 인지 효과 X · 앙상블 평균 효과 ✅ (audit 5/23). 4-way engine latency (12 cell) 모든 inject variant 동등 (|Δ%| ≤ 1.12%) — 추정 정확도 ↑가 engine 차이 안 만듦.

## 2. ★ 현재 측정 완료 status — 정확한 scope gap

### A. CaseC 측정 scope 비교 (v13 vs 현재)

| 항목 | v13 (B1·CaseA·CaseB 정본) | 현재 CaseC (v14+v15) | gap |
|---|---|---|---|
| **unique cell sub** | **25** | 18 | 7 cells 미측정 |
| **selectivity 축** | 0.001 · 0.01 · 0.10 (3) | `selectivities[0]` 만 (default) | sel ablation 미측정 |
| **K (n_strata) 축** | 10 · 20 · 30 (3) | K = 20 default 만 | K ablation 미측정 |
| **method 축** | 16 method | N/A (method-agnostic mode) | (mode 정의 차이) |
| **unique (cell × sel × K) tuples** | **95** | **18** | **77 tuples 미측정** |

### B. 미측정 77 tuples 분해

**미측정 cell types (7 cells)** — A9·A10·A11 concat 다중 벡터:
- A9-DEEP+SIFT-concat-sf1, A9-DEEP+SIFT-concat-sf10, A9-DEEP+SIFT-concat-sf100 (3)
- A10-DEEP+WIKI-concat-sf1, A10-DEEP+WIKI-concat-sf10 (2)
- A11-DEEP+YFCC-concat-sf1, A11-DEEP+YFCC-concat-sf10 (2)

**측정된 18 cell types 의 sel × K ablation 미측정 ~70 tuples** (A1-DEEP·A1-SIFT·A1-SSN·A2-Fig7·A2-Fig9·A5-scale-sf{1,10,100}·A4-sel 등의 sel=0.001/0.1·K=10/30 변형).

## 3. ★ 핵심 수치·결과 정본 (carry · 본 세션 추가)

| 지표 | 값 | 출처 |
|---|---|---|
| v13 1,508 cell × 3 mode (B1·A·B) | qe B1 1.458 · CaseA 1.636 · CaseB 1.402 | v13_summary.md |
| v13 결합 better% vs B1 | 89.1% (1,344/1,508) · 중앙값 −4.38% | v13 |
| v14 CaseC 9 cell | mean qe_trim 1.3729 · vs B1 −12~−15% | v14_summary.md |
| v15 CaseC 18 cell (carry+신규) | mean qe_trim 1.4620 (신규 9: 1.5510 sf=1/10 scale-dependent) | v15_portfolio_summary.md |
| phase2 4-way 12 cell engine | CaseC vs B1 +0.30% · 17 variant 모두 |Δ%| ≤ 1.12% · injection 204/204 | phase2_4way_summary.md |
| baseline vs B1 (4-way) | +409.7% (4-5× 느림 carry 일관) | 위 동일 |

## 4. ★★★ 다음 세션 task — CaseC 전수 동일 측정 + 재검증 한 세션 완주 (Phase 1-9)

### Phase 1 — 코드 fix (~1 시간)

1. **★ Codex BLOCKER E fix** — `_internal/scripts/gen_latency_estimates.py` 의 a-side rng 분리:
   ```python
   # 신규: CaseC 전용 별도 generators (method estimates 와 독립)
   rng_caseC_a = np.random.default_rng(20260520 + 2_000_000)
   rng_caseC_b = np.random.default_rng(20260520 + 3_000_000)
   # method estimates 는 기존 rng = np.random.default_rng(20260520) 유지
   # est_b1 a-side 도 별도: rng_b1 = np.random.default_rng(20260520 + 4_000_000)
   ```

2. **★ measure_paper_exact.py `measure_case_c` 함수 sel·K override 추가** — 현재 `selectivities[0]` 만 측정 + K=20 default:
   ```python
   def measure_case_c(cell, n_queries=1000, trials=TRIALS, output_dir=None,
                      sel_override=None, K_override=None):
       sel = sel_override if sel_override else cell.selectivities[0]
       n_strata = K_override if K_override else mc.N_STRATA
       # cache_cluster_samples_inmem 의 n_strata 매개변수 사용
       ...
   ```
   CLI flag 추가: `--sel <0.001|0.01|0.1>` · `--K <10|20|30>`

3. **★ measure_offline_casec_portfolio.py 의 KNOWN_CELLS 25 cell 확장**:
   ```python
   KNOWN_CELLS = frozenset({
       # v14 carry 9 + v15 신규 9 = 18 (기존)
       "A1-DEEP", "A1-SIFT", "A1-SSN",
       "A2-Fig7", "A2-Fig8", "A2-Fig9",
       "A4-sel",
       "A5-scale-sf1", "A5-scale-sf10", "A5-scale-sf100",
       "A5-scale-sf1-SIFT", "A5-scale-sf1-SSN",
       "A5-scale-sf10-SIFT", "A5-scale-sf10-SSN",
       "A6-WIKI-sf1", "A6-WIKI-sf10",
       "A7-YFCC-sf1",
       "A8-DEEP+SIFT-sf10",
       # 신규 7 cell (concat 다중 벡터)
       "A9-DEEP+SIFT-concat-sf1", "A9-DEEP+SIFT-concat-sf10", "A9-DEEP+SIFT-concat-sf100",
       "A10-DEEP+WIKI-concat-sf1", "A10-DEEP+WIKI-concat-sf10",
       "A11-DEEP+YFCC-concat-sf1", "A11-DEEP+YFCC-concat-sf10",
   })
   ```

4. **★ 신규 script `measure_offline_casec_full.py` 작성** — 95 tuple (cell, sel, K) list 받아서 각 tuple 별 `measure_paper_exact.py --cell X --mode CaseC --sel Y --K Z` subprocess 호출. tuple list 는 본 handoff §5 의 95 tuples 또는 v13 parquet 에서 추출.

### Phase 2 — 자원 watchdog 256GB free 보장 (~5 분)

```bash
# 신규 watchdog — free RAM ≥ 256GB OR our_rss ≤ 600GB SIGTERM
ssh capstone "cat > /mnt/hdd0/home/capstone2026/resource_watchdog_256.sh << 'EOF'
#!/bin/bash
WATCH_PROCS='measure_offline_casec|measure_paper_exact|measure_latency'
LOG=/tmp/resource_watchdog_256.log
while true; do
  avail_gb=\$(free -g | awk 'NR==2 {print \$7}')
  pids=\$(pgrep -d, -f \"\$WATCH_PROCS\" 2>/dev/null)
  rss_gb=\$(ps -o rss= --pid \"\$pids\" 2>/dev/null | awk '{sum+=\$1} END {print int(sum/1024/1024)}')
  if [ -n \"\$pids\" ] && [ \"\$avail_gb\" -lt 256 ]; then
    echo \"[\$(TZ=Asia/Seoul date +%T)] ALERT avail=\${avail_gb}GB < 256 → SIGTERM\" >> \"\$LOG\"
    pkill -SIGTERM -f \"\$WATCH_PROCS\"
    break
  fi
  if [ \"\$rss_gb\" -gt 600 ]; then
    echo \"[\$(TZ=Asia/Seoul date +%T)] ALERT rss=\${rss_gb}GB > 600 → SIGTERM\" >> \"\$LOG\"
    pkill -SIGTERM -f \"\$WATCH_PROCS\"
    break
  fi
  sleep 5
done
EOF
chmod +x /mnt/hdd0/home/capstone2026/resource_watchdog_256.sh
nohup /mnt/hdd0/home/capstone2026/resource_watchdog_256.sh > /tmp/watchdog_256_nohup.log 2>&1 & disown"
```

### Phase 3 — estimates 재생성 (~30 분)

Phase 1 의 BLOCKER E fix 적용 후 sf=10 estimates 신규 생성 (4-way engine 검증용):
```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \\
  for sf in 1 10 100; do \\
    python3 -u gen_latency_estimates.py --dataset DEEP --sf \$sf --n-qvec 3 \\
      --output latency/estimates_v16_blocker_e_fix; \\
  done"
```
검증: parquet 에 est_caseC 가 method 순서 변경에도 deterministic 인지 확인.

### Phase 4 — ★★★ CaseC offline 전수 95 cell 측정 (~2-3 시간, 3 병렬 sf-adaptive)

**95 tuple list 추출**:
```bash
python3 -c "
import pyarrow.parquet as pq
df = pq.read_table('/Users/hyunbin/Capstone/_internal/cache/rq3/aggregated_v13_full.parquet').to_pandas()
tuples = df[['cell','sel','K']].drop_duplicates().sort_values(['cell','sel','K'])
tuples.to_csv('/tmp/v13_casec_95tuples.csv', index=False)
print(f'{len(tuples)} tuples saved to /tmp/v13_casec_95tuples.csv')
"
scp /tmp/v13_casec_95tuples.csv capstone:/mnt/hdd0/home/capstone2026/cache/rq3/
```

**launch**:
```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \\
  TS=\$(TZ=Asia/Seoul date +%Y%m%d_%H%M%S) && \\
  nohup python3 -u measure_offline_casec_full.py \\
    --tuples-csv v13_casec_95tuples.csv \\
    --parallel 3 --trials 10 --n-queries 1000 \\
    --output paper_exact_v16_full95_\$TS \\
    > /tmp/v16_full95_nohup.log 2>&1 & disown"
```

**ETA**: 95 cell × 3-4분/cell sequential = 6 시간 → 3 병렬 (sf-adaptive, sf=100 cell 2 병렬·sf=10·1 cell 4 병렬) ≈ **2-2.5 시간**. 자원 256GB watchdog 안 보호.

### Phase 5 — engine 4-way 확장 측정 (선택, ~3-5 시간)

현재 phase2 12 cell (sf=10 sel=0.001) 완료. 사용자 명시 "전수 동일" 따라 extension 측정:
- sf {1, 10, 100} × sel {0.001, 0.01, 0.1} × Q{Q3, Q9, Q10, Q12} × qid {0, 1, 2} = 108 cell
- 또는 sf {1, 100} × sel {0.01, 0.1} × Q4 × qid 3 = 24 cell 작은 portfolio (~3 시간)
- estimates 추가 생성 (sf=1·100 × 3 sel · 4 query) 필요

**우선순위**: offline 95 cell 먼저 (가설 검증 핵심), engine 확장은 시간 가능 시. 시간 부족하면 carry.

### Phase 6 — aggregate + figure 재생성 (~1 시간)

```bash
ssh capstone "cd /mnt/hdd0/home/capstone2026/cache/rq3 && \\
  python3 aggregate_offline_casec_v15.py \\
    --v15-dir paper_exact_v16_full95_<TS> \\
    --v14-dir paper_exact_v14_20260523 \\
    --output-dir paper_exact_v16_summary_<TS>"
# 또는 신규 aggregate_offline_casec_v16.py (95 cell × 3 sel × 3 K 분해 분석)
```

scp parquet 로컬 → matplotlib figure 재생성:
- `plot_4way_latency.py` (carry, engine)
- `plot_casec_qerror.py` (신규 — 95 cell qe_trim cell × sel × K heatmap)

### Phase 7 — ★ 3-multi-model 재검증 (~1.5 시간)

1. **Codex xhigh 적대 재검증**:
   ```bash
   # patched 코드 5 파일 + 신규 measure_offline_casec_full.py + 95 cell aggregate
   cat /tmp/codex_review_v16_prompt.md  # 신규 prompt 작성
   nohup codex exec --skip-git-repo-check -c model_reasoning_effort=xhigh \\
     "$(cat /tmp/codex_review_v16_prompt.md)" > /tmp/codex_review_v16.log 2>&1 & disown
   ```
   review 항목: (a) BLOCKER E fix 정합성 (rng_caseC_a 분리 후 method 의존성 끊김 검증), (b) 95 cell 측정 결과의 통계적 타당성, (c) load_estimates validation (BLOCKER C 잔여), (d) repo/server _measure_common.py 정합성 (BLOCKER A 잔여).

2. **Gemini Deep Think 측정 narrative 검증**:
   - 95 cell CaseC 결과의 sel·K 평면 패턴 해석 (scale·structure dependent 효과)
   - 보고서 §4.2.2·§4.6.1·§5.6 narrative 의 95 cell 결과 통합 검증
   - figure 시각 검증 (이미지 input)

3. **Claude 메인 self-verify**:
   - v13 와 v16 (CaseC 95 cell) 의 cell-level paired matched 비교
   - **결정적 가설**: 95 cell × 3 sel × 3 K 평면 CaseC mean qe_trim < CaseB mean qe_trim (9/9 cell · 9/9 sel-K) 인지

### Phase 8 — 보고서·storyline·deck final patch + PDF (~1.5 시간)

1. **보고서 §4.2.2 → §4.2.3 신규** — v16 95 cell 전수 결과:
   - 95 cell × 3 sel × 3 K mean qe_trim 분포
   - CaseC vs B1 cell-level better% (95/95 기대) + median Δ%
   - CaseC vs CaseB cell-level better% + median Δ%
   - scale·structure dependent 패턴 분석
2. **§5.6 4-way engine 확장 결과** — Phase 5 측정 시 update
3. **storyline 슬라이드 11/12** — 95 cell 정본 수치 update
4. **PDF 재생성** (`md2pdf.py`)
5. **figure server sync** → 보고서 reference path 일관

### Phase 9 — handoff close + commit (~30 분)

1. handoff 신본 (timecode 예: 5/24 23:30 KST) + 복붙 프롬프트
2. 직전 handoff (본 문서) archive 이동
3. commit chain: BLOCKER E fix · 95 cell raw · aggregate · figure · 보고서 · handoff
4. **★ push X** (사용자 명시 요청 시만, carry)

## 5. 산출물 경로

| 산출물 | 경로 | 상태 |
|---|---|---|
| ★ 본 handoff | `_internal/handoff/active/handoff_20260524_115000_*.md` | 본 파일 |
| ★ v13 parquet 정본 | `_internal/cache/rq3/aggregated_v13_full.parquet` | carry |
| ★ v14 9 cell CaseC | 서버 `cache/rq3/paper_exact_v14_20260523/*_CaseC.json` | carry |
| ★ v15 18 cell summary | 서버 `cache/rq3/paper_exact_v15_summary_20260524_024053/v15_portfolio_summary.md` | carry |
| ★ phase2 4-way 12 cell | 서버 `cache/rq3/latency/phase2_4way_final_20260524_040338/phase2_4way_summary.md` | carry |
| ★ 4-way figure | `experiments/figures/4way_latency_v15/fig{1,2}_*.{png,pdf}` | carry |
| ★ 측정 코드 (3 patch + 4 신규) | `_internal/scripts/{measure_latency_realengine,gen_latency_estimates,measure_paper_exact,measure_offline_casec_portfolio,aggregate_4way_latency,aggregate_offline_casec_v15,plot_4way_latency}.py` | carry |
| ★ 보고서 patched + PDF | `submission/_drafts/속도는벡터_6_11_최종보고서_20260523_215000.{md,pdf}` (1.71 MB) | carry |
| ★ 95 tuple csv (다음 세션 추출) | `/tmp/v13_casec_95tuples.csv` | 다음 세션 |
| ★ v16 95 cell raw (다음 세션) | 서버 `cache/rq3/paper_exact_v16_full95_<TS>/*.json` | 다음 세션 |
| ★ v16 summary (다음 세션) | 서버 `cache/rq3/paper_exact_v16_summary_<TS>/` | 다음 세션 |

## 6. 환경·자원 (★ 256GB free 보장)

- **자원 watchdog 신규 256GB**: `resource_watchdog_256.sh` (avail_gb < 256 OR our_rss > 600GB → SIGTERM, 5초 주기). 본 세션 60GB 한도와 다름 — 사용자 명시 5/24 11:45 KST.
- **3 병렬 sf-adaptive**: sf=100 cell 2 병렬·sf=10/1 cell 3-4 병렬. fetch RAM 부담 sf=100 = 80GB/cell, sf=10 = 25GB/cell.
- **256GB free 안 측정 cell 동시 수 한도**:
  - sf=100: (avail 780GB − 256GB reserve) / 80GB = 6.5 cell 동시 가능 → 안전 3 cell
  - sf=10: 524GB / 25GB = 20 cell 동시 가능 → 안전 4 cell
  - sf=1: 524GB / 3GB = 170 cell 동시 가능 → 안전 4 cell (병렬 한도 sturetable)
- **서버 자원**: 1007GB total · available 750~780GB (carry) · CPU 128 vCPU · 4× RTX 6000 Ada 49GB · uptime 11+ days
- **PG port**: 55435 (patched binary carry)
- **미커밋**: 본 세션 종료 시 모두 commit 완료 (5 commit carry)
- **push X** (carry — 사용자 명시 요청 시만)

## 7. 일정 (carry)

- **5/24 (일) 오늘** ★★★ 다음 세션 한 번에 CaseC 전수 95 cell + 재검증 완주 (사용자 명시)
- **5/24 (일)** 박성원 멘토 3차 자문 회신 예정
- **5/26 (화) 23:59** 발표 슬라이드 LearnUs 마감 ★★ critical path
- **5/27 (수)** · **5/29 (금)** 최종 발표
- **5/28 (목) 12:00** 포스터·영상 LearnUs 마감
- **6/5 (금)** 전시회
- **6/11 (목) 23:59** 최종 보고서·상호평가 결과 마감

## 8. ★ 환각 회피 룰 (carry · 본 세션 추가)

- v13 1,508 cell 정본 (3-way matched) · v14 9 cell CaseC carry · v15 18 cell CaseC 신규 · phase2 12 cell 4-way carry — 모두 진짜 측정. 본 세션 patch 후 smoke + 12 cell + portfolio 완주.
- ★ 89% Q-error 우위 = 앙상블 평균 효과 (분포 인지 X) — controlled verification
- CaseC = (B1+B1)/2 dual-Bernoulli 통제군 (method-agnostic) — q-error 1.46 (18 cell) · engine paired Δ% +0.30% (12 cell)
- **★ 다음 세션 핵심**: CaseC 전수 95 cell (v13 scope 완전 일치) 측정 + Codex BLOCKER E fix + 3-multi-model 재검증. 한 세션 안 완주 (8-10 시간 ETA).
- **★ 자원 watchdog 256GB free 보장** — 사용자 명시 5/24 11:45 KST. 60GB carry 한도 → 256GB 신규.
- 자원 watchdog 위반 시 자동 stop (조건: avail_gb < 256 OR our_rss > 600GB)
- 측정 코드 변경 시 smoke 우선 — Codex BLOCKER E fix 후 1 cell smoke 필수
- 비가역 작업 (git push --force · DB DROP · rm -rf) — 사용자 자는 동안 사전 위임 없음 → carry
- git push X (사용자 명시 요청 시만, carry)
- 보고서 §2.2 식 1-6 = paper §V-B verbatim 확정 (Gemini + AdaptiveState ground truth, 본 세션 patch 완료)
- 보고서 §2.3 Cochran §5.5 Optimum Allocation 정확 (본 세션 patch 완료)
- 코드명 (B1·CaseA·CaseB·CaseC) = 보고서·기술 문서 OK, 발표물 (deck·포스터·영상) 노출 금지 — storyline 슬라이드 11/12 한국어 명시 carry
- handoff 룰: 종료 시 active 직전 set archive → 신본 timecode 작성 ✓

---

작성: 2026-05-24 11:50 KST. 사용자 일어남 + 명시 "CaseC 전수 동일 + 3-multi-model 재검증 + 자원 256GB · 다음 세션 한 번에 완주". → 다음 세션 = Phase 1-9 명확 chain (코드 fix → 자원 watchdog → estimates → CaseC 95 cell → engine 확장(선택) → aggregate → 재검증 → 문서 → close). 본 세션 까지 5 commit + 측정·문서 carry 모두 보존. 본 세션은 4-way controlled experiment 골격만 완성, 다음 세션은 전수 측정 정합성 + 재검증 완주.
