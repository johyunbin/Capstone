# handoff 20260520 14:44 — 통계 보강 (analyze_latency.py + 보고서 §5.5 effect size) · v3 polish prompt · 서버 backup (2.6G)

> 이전 handoff(`_internal/handoff/archive/handoff_20260520_141449_deck_v2_vision검증.md`) → 본 문서. 이 문서 하나만 읽으면 0% loss 인계 — self-contained.
>
> **핵심 한 줄**: 사용자가 외출 중인 본 세션(5/20 14:23~14:55)은 (1) **통계 보강** — `analyze_latency.py` 에 paired bootstrap CI · Hedges' g · Cliff's δ 3 함수 추가 + paired_stats() 4 컬럼 + print 분포 + phase2/phase3 paired_stats.csv 11→15 컬럼 재계산 + 보고서 §5.5/§6.4 effect size 본문 2 단락·표 5-3 보강 + md→pdf→docx 신본 `_144446` + (2) **v3 polish prompt** — claude.ai/design 복붙용 polish 3건 (B13 그라데이션·B19 막대 소수점·B2 33.3% 복구) + (3) **서버 backup 2.6G** — 5/21 (수) 서버 권한 종료 전 사용자 추가 요청, 22,117 file (results_3way_5_17 1.8G + cache 436M + Exqutor 261M, NPY/index/PG data/.git pack 제외, 큰 file 1 .gitignore). 결과: baseline anchor 180/180 = 100% 모두 large effect (g·δ·CI) · B1 anchor 13/168 = 7.7% 유의 中 86.9% small effect 로 latency 동등성 강화 · Q12 qid 0 4 method (pca1d·rabitq_strat·sparse_rp·zorder_morton) large effect (g ≈ −1.5, δ = −1.0, CI [−58, −27] ms). 다음 = 사용자 귀가 후 맥북 동기화 + 5/22 미팅·5/25 보고서·5/26 PPTX·5/27 발표·5/28 포스터·6/11 보고서.

---

## 0. 가장 먼저 — 정본·진입점

- **★ 승인된 본 세션 plan**: `~/.claude/plans/virtual-seeking-panda.md` (통계 보강 + polish prompt + 서버 backup + handoff/commit). 본 세션 완료, 폐기 가능.
- **★ 라우팅·구조 정본**: 루트 `CLAUDE.md`. anchor 본 handoff 로 갱신.
- **★ 보고서 신본 (정본)**: `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_144446.{md,pdf,docx}` (§5.5 effect size 본문 보강 + §6.4 둘째 갈래 갱신)
- **★ v3 polish prompt (claude.ai/design 복붙용)**: `submission/_drafts/속도는벡터_발표deck_수정프롬프트_polish_20260520_144446.md`
- **★ paired_stats 통계 보강**: `_internal/scripts/analyze_latency.py` (BOOTSTRAP_N + 3 함수 + 4 컬럼 + print 분포) + 신본 `_internal/cache/rq3/latency/{phase2,phase3}/figures/paired_stats.csv` (11→15 컬럼) + 백업 `paired_stats_pre_effect_20260520_144326.csv`
- **★ 서버 backup**: `_internal/server_backup_20260520/` (2.6G · 22,117 file · `.gitignore` 동봉) — 5/21 서버 권한 종료 전 사용자 추가 요청 산출
- **★ v2 PPTX (5/22 미팅·5/27 발표 base, ship-ready)**: `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` (carry, 1.20MB, 21장 raster image)
- **★ 5축 vision 검증 정본 (carry)**: `_internal/cache/rq3/validation/deck_phase2/v2_axis_{a,b,c,d,e}.md` + `v2_verdict.md` (carry)
- **★ v2 PNG 정본 21장 (carry)**: `_internal/cache/rq3/validation/deck_phase2/v2_images/B{01..21}.png`

## 1. 본 연구 framing (carry · 불변)

본 연구는 Exqutor 논문(arXiv:2512.09695v2) 재현이 아니라 **표본 선택(sample selection) 단계 하나**의 개입(무작위 Bernoulli → 분포 인지 stratification)이 추정 오차(Q-error)에 미치는 영향을 전 변인에 걸쳐 검증한 완전 실험 — 3-way matched B1(기존)·CaseA(완전 대체, 음성 대조군)·CaseB(결합, 산술평균). 발표물은 코드명(B1/CaseA/CaseB)·"영역" 필러·영어 메타 라벨·수식 노출 금지. 보고서는 코드명 사용 OK.

「엔진 적용 검증」 = 오프라인 검증된 카디널리티 추정치(13종 method 결합 = CaseB ×13)를 패치된 PostgreSQL(서버 55435)에 주입해 "추정치 → 실행 계획 → end-to-end latency" 고리를 닫는 실험. 4조건: 기본엔진(baseline) / 베이스라인(B1) / 결합(CaseB ×13) / 오라클(true_card).

## 2. 본 세션(5/20 14:23~14:55)이 한 일

| 항목 | 상태 | 내용 |
|---|---|---|
| 직전 handoff 정독·base 조사 | ✅ | handoff_20260520_141449 흡수 → 5 file 병렬 정독 + Explore agent — `analyze_latency.py` 611 line, paired_stats 11 컬럼, phase3 8 JSON · 보고서 §5.5 L412~L505 본문, polish 3건 위치. |
| ★ 사용자 추가 요청 흡수 | ✅ | 서버 5/21 권한 종료 전 backup. plan Phase D 추가 (Phase A·B 와 병렬 진행). |
| Plan 작성·승인 | ✅ | `~/.claude/plans/virtual-seeking-panda.md` (4 Phase: A 통계 보강 + B polish prompt + D 서버 backup + C handoff/commit). ExitPlanMode 승인. |
| Phase A.1 — analyze_latency.py 함수 추가 | ✅ | BOOTSTRAP_N=2000 + `_bootstrap_ci_paired_diff` + `_hedges_g_paired` + `_cliffs_delta_paired` 3 함수 + paired_stats() 4 키 (ci_lo_ms·ci_hi_ms·hedges_g·cliffs_delta) + export_paired_csv() 4 fieldname + print_paired_stats() anchor 별 effect size 분포 print. self-test 통과. |
| Phase A.2 — paired_stats.csv 재계산 | ✅ | 백업 (`_pre_effect_20260520_144326.csv`) 후 phase2/phase3 재계산. phase2 348행·phase3 232행 모두 15 컬럼 신본. figures (fig5_2~fig5_4 + latency_*.png) 도 함께 재생성. |
| Phase A.3 — sanity check | ✅ | baseline anchor 180/180 = 100% 모두 large effect (\|g\|≥0.8 + \|δ\|≥0.474 + CI∌0). B1 anchor 13/168 = 7.7% 유의·14/168 = 8.3% large g·146/168 = 86.9% small g (latency 동등성 강화). Q12 qid 0 4 method large effect (g ≈ −1.18~−1.58, δ = −1.0, CI [−58, −27] ms). |
| Phase A.4 — 보고서 §5.5/§6.4 갱신 | ✅ | 신본 `_144446` 타임코드. 표 5-3 컬럼 4→7 (Hedges g + Cliff δ + CI) + 효과크기 본문 2 단락 추가 (baseline 100% large + B1 86.9% small 분석 + Q12 qid 0 large effect 특이성) + §6.4 둘째 갈래 "통계 검증 도구 확장" → "본 보강 + 4 엔진 통합용 cluster bootstrap·variance decomposition" 으로 갱신. md→pdf→docx 3종 생성. |
| Phase B — v3 polish prompt | ✅ | `_144446` 타임코드. polish 1 (B13 hero "13/16" 그라데이션 일관성) + polish 2 (B19 §2 막대 라벨 35%→35.2%·89%→89.1% 정합) + polish 3 (B2 hero "33%"→"33.3%" catalog 복구). 직전 fix prompt `_133527` format carry — 한국어 코드블록·짧고 명확·자가검증 10항·v3 export. |
| Phase D.1·D.3 — 서버 backup | ✅ | `mkdir _internal/server_backup_20260520/` + rsync background. 서버 13T 中 11T 사용, NPY/index/PG data/.git pack 제외 후 2.6G/22,117 file 수신. results_3way_5_17 (1.8G) + cache (436M) + Exqutor (261M) + log (72M) + 작은 results_* (~수 MB). |
| Phase D.4 — 큰 file 정리·gitignore | ✅ | Exqutor/.git (786M) 삭제 (외부 GitHub 재clone 가능). phase7_8m_strata.csv (76M) gitignore. 50MB+ file 1개로 축소. `.gitignore` (Exqutor/.git/·*.pack·phase7_8m_strata.csv·__pycache__/·*.pyc) 생성. |
| Phase C — handoff 작성·archive·CLAUDE.md anchor | (진행 중) | 본 file + 새세션 복붙 프롬프트 + 직전 _141449 archive 이동 + CLAUDE.md anchor 갱신. |
| Phase C — commit·push·gh run watch | (다음) | 통계 보강 + polish prompt + 서버 backup + handoff 통합 commit. push 후 gh run watch 의무. |

## 3. ★★★ 본 세션 결과 — 다음 세션이 반드시 흡수할 정본

### 3.1 통계 보강 — paired_stats.csv effect size 분포 (보고서 §5.5 정본)

**baseline anchor (n=180, 12 cell × 15 비-기본 variant)**:
- p_holm < 0.05 유의: **180/180 = 100%** (carry)
- Hedges' g large (\|g\|≥0.8): **180/180 = 100%**
- Cliff's δ large (\|δ\|≥0.474): **180/180 = 100%**
- bootstrap 95% CI ∌ 0: **180/180 = 100%**
- 해석: 카디널리티 주입 가속이 통계적 유의뿐 아니라 효과크기에서도 압도적

**B1 anchor (n=168, 12 cell × 14 비-B1 비-기본 variant)**:
- p_holm < 0.05 유의: **13/168 = 7.7%** (carry)
- Hedges' g large (\|g\|≥0.8): **14/168 = 8.3%**
- Hedges' g medium (0.5≤\|g\|<0.8): 8/168 = 4.8%
- Hedges' g small (\|g\|<0.5): **146/168 = 86.9%** ★ (동등성 강화)
- Cliff's δ large (\|δ\|≥0.474): 29/168 = 17.3%
- Cliff's δ small (\|δ\|<0.33): 101/168 = 60.1%
- bootstrap 95% CI ∌ 0: **44/168 = 26.2%**
- 해석: 7.7% 유의도 효과크기로는 small 다수 → 베이스라인·결합·정답 latency 동등성이 효과크기로 강화

**Q12 qid 0 4 method (pca1d·rabitq_strat·sparse_rp·zorder_morton) — 가장 강한 유의 신호 (p_holm = 0.0103)**:
- Hedges' g: −1.18 ~ −1.58 (모두 large effect)
- Cliff's δ: −1.0 (perfect — 15 rep 모두 B1 빠름)
- bootstrap 95% CI: [−58.8, −27.4] ~ [−58.5, −33.2] ms (모두 0 미포함)
- 같은 4 method 의 qid 1·qid 2: g ≈ −0.31 ~ 0.39 (small), p_holm = 1.0
- 해석: §5.4 plan 회복 fragile함과 동일 origin — Q12 qid 0 의 한 특이 cell 에서만 효과크기·유의 large

**phase3 (sel=0.01·0.1 carry-over, n=120 baseline + 112 B1)** carry:
- baseline anchor 60/120 = 50% 유의 (sel=0.01 의 4 cell 모두 + sel=0.1 0건, plan 변화·동일 정합)
- B1 anchor 5/112 = 4.5% 유의

### 3.2 v3 polish prompt 의 3건

| polish | 슬라이드 | 현재 → 정본 | 사유 |
|---|---|---|---|
| 1 | B13 hero "13/16" | navy 단색 → navy `#1E3A5F` → cyan `#0EA5E9` 그라데이션 | B11 "89.1%" 와 시각 일관성 |
| 2 | B19 §2 막대 라벨 | "35%" / "89%" → "35.2%" / "89.1%" | §1 본문 ("89.1%" 정확) 과 한 슬라이드 내 표기 일관 |
| 3 | B2 hero | "33%" → "33.3%" | pgvector catalog 정합 (1/3 ≈ 0.333) |

**의도적 skip 8건** (carry-frozen 또는 의역 carry, 발표 무결성 영향 0): 페이지 번호 부재 6 + 의역 "1508번 측정" 콤마 부재 + B6~B10 hero 부재 (도식 위주). 추가 fix 발행 불요.

### 3.3 서버 backup 산출

| 디렉토리 | 용량 | 내용 |
|---|---|---|
| `results_3way_5_17/` | 1.8G | 1508 portfolio 3-way matched 측정 raw |
| `cache/` | 436M | RQ3 + RQ1 측정 산출 (npy 제외) |
| `Exqutor/` | 261M | PG patch source + DuckDB + query_plans (.git 삭제) |
| `log/` | 72M | 측정 log 누적 |
| 그 외 작은 `results_*` | ~수십 MB | 이전 sprint 결과 (v6~v10·concat_track·b1redo) |
| **총량** | **2.6G** | **22,117 file**, 50MB+ 1개 (.gitignore: `phase7_8m_strata.csv`) |

backup 핵심:
- vector.c 패치 source (재현용)
- harness 3종 + measure_paper_exact.py + 측정 script
- 1508 portfolio 측정 raw (정본 v13_summary base)
- 측정 log (재실행 시 진행 trace)

**skip 한 영역** (재현 가능):
- `vanilla_sf100/` (921G) — vanilla PG data
- `exqutor_sf10/` (32G) — patched PG data
- `cache/rq3/*.npy` (DEEP·SIFT·SSN·WIKI·YFCC 벡터 cache, 수 GB ~ 23GB/file)
- `_DROPPED_*` (이미 drop 된 cell)
- HNSW index · *.fvecs · *.ivecs · *.bin · *.faiss

### 3.4 carry — v2 ship-ready (5/22 미팅·5/27 발표 base)

5축 verdict carry 모두 PASS:
- V-A B1~B5 (표지 Sky) PASS · V-B B6~B10 (방법 Violet) PASS · V-C B11~B14 (결과 Emerald) WARN minor 5 · V-D B15·B16 (신설 14b/14c, fix 1·2·3 정밀) PASS ★ · V-E B17~B21 (적용 Orange·결론·종결) PASS
- critical 0 · major 0 · minor 11 · ship-ready
- fix 1 (B16 4갈래 도식) + fix 2 (메인 hero 그라데이션 6/6) + fix 3 (한글 21/21 깨짐 0건) 모두 PASS
- carry 18장 변동 0건 · 정본 수치 catalog 23/23 = 100%

## 4. ★ 다음 세션 task

1. **[★최우선·사용자 집 복귀 후] 맥북 동기화**:
   - `cd ~/Capstone && git pull --no-rebase origin main` (Capstone repo: 본 세션 push 받아오기)
   - `.claude` rsync 양방향 (sync.md 룰): 맥미니→맥북 push + 맥북→맥미니 pull
   - **★ 새 본 세션 산출 `_internal/server_backup_20260520/` (2.6G) 도 sync 대상** — 큰 file 1개 (.gitignore 처리) 제외 모두 git 으로 동기화. 또는 rsync 양방향으로 phase7_8m_strata.csv 도 전송.
2. **[★시각 렌더 검증·5/22 미팅 전]**:
   - 사용자가 v2 PPTX (`속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx`) PowerPoint·Keynote 로 시각 확인 (raster image 렌더 정상? hero 그라데이션 명확? 페이지 번호 부재 영향?)
   - 또는 사용자가 **v3 polish prompt 를 claude.ai/design 복붙** → v3 PPTX (`_v3.pptx`) 받아옴 → 다음 세션이 5축 vision 재검증 (직전 sub-agent 5 launch pattern carry)
3. **[필수·5/25 까지] 보고서 _144446 신본 팀원 최종 검토**:
   - §5.5 effect size 본문 보강 확인 (Hedges g·Cliff δ·CI 표 5-3 + 본문 2 단락)
   - §6.4 둘째 갈래 갱신 확인
   - PDF 46p~47p 학교 양식 "본문 14~22p" 기준
4. **[토요일 이후·사용자 직접] 포스터·팜플렛·소개영상 신본 작업** (carry):
   - 포스터: `submission/_drafts/속도는벡터_포스터_claudedesign_Phase2반영_20260520_100319.md`
   - 팜플렛: `submission/_drafts/속도는벡터_팜플렛_claudedesign_Phase2반영_20260520_100340.md`
   - 소개영상: `submission/_drafts/속도는벡터_소개영상_claudedesign_Phase2반영_20260520_100403.md`
5. **[후속] 통계 검증 다음 단계 (보고서 §6.4 둘째 갈래)**:
   - plan-level effect size 측정 (같은 cell 에서 plan signature 다른 variant 간 latency 분포 분리)
   - 4 엔진 통합 검증용 cluster 단위 paired bootstrap
   - 변이 분해 (variance decomposition) — 결합·정답의 latency 분산이 베이스라인 대비 좁아지는지 검증

## 5. 서버 접속·실행 (carry, ★ 5/21 권한 종료)

- 접속: `ssh capstone` (165.132.140.240, capstone2026, 무암호). PG: `PGPASSWORD=wns41559 psql -h localhost -p 55435 -U wns41559 -d wns41559`.
- 55435 = 우리 패치 바이너리. `vector.injected_card` 기본 −1 = 평소 동작.
- 서버 작업 dir `/mnt/hdd0/home/capstone2026/cache/rq3/`. harness 3종 + `_measure_common.py` + `measure_paper_exact.py` + 산출물 `latency/{phase2,phase3}/`.
- ⚠️ **`build_custom.sh`/`apply_patch.sh` 절대 금지** — 재빌드 필요 시 직접 빌드.
- ★ **서버 권한 5/21 (수) 까지** — 본 세션이 backup 으로 핵심 데이터 (2.6G/22117 file) 로컬 보존. 권한 종료 후에도 backup 으로 4 엔진 통합 PoC·재현 검증 가능.

## 6. 산출물 경로

| 산출물 | 경로 | 상태 |
|---|---|---|
| 승인 본 세션 plan | `~/.claude/plans/virtual-seeking-panda.md` | 정본 (완료, 폐기 가능) |
| **★ analyze_latency.py 보강** | `_internal/scripts/analyze_latency.py` | 정본 (3 함수 + 4 컬럼 + print 분포) |
| **★ phase2 paired_stats.csv** | `_internal/cache/rq3/latency/phase2/figures/paired_stats.csv` | 정본 (348행·15 컬럼) |
| **★ phase3 paired_stats.csv** | `_internal/cache/rq3/latency/phase3/figures/paired_stats.csv` | 정본 (232행·15 컬럼) |
| paired_stats 백업 (pre-effect) | `_internal/cache/rq3/latency/{phase2,phase3}/figures/paired_stats_pre_effect_20260520_144326.csv` | 백업 |
| **★ 보고서 신본** | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_144446.{md,pdf,docx}` | 정본 (§5.5 + §6.4 갱신) |
| 직전 보고서 (_124200, carry) | `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_124200.{md,pdf,docx}` | carry (보존) |
| **★ v3 polish prompt** | `submission/_drafts/속도는벡터_발표deck_수정프롬프트_polish_20260520_144446.md` | 정본 |
| 직전 fix prompt (_133527, carry) | `submission/_drafts/속도는벡터_발표deck_수정프롬프트_20260520_133527.md` | carry |
| **★ 서버 backup** | `_internal/server_backup_20260520/` + `.gitignore` | 정본 (2.6G·22117 file) |
| v2 PPTX (carry, 5/22·5/27 base) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영_v2.pptx` | carry (정본) |
| v1 PPTX (carry) | `submission/_drafts/속도는벡터_최종발표_슬라이드_phase2반영.pptx` | carry |
| 19장 PPTX (carry base) | `submission/_drafts/속도는벡터_최종발표_슬라이드_20260519_223845.pptx` | carry |
| 5축 vision 검증 산출 (carry) | `_internal/cache/rq3/validation/deck_phase2/v2_{axis_*,verdict}.md` + `v2_images/B{01..21}.png` | carry (정본) |
| Phase 2/A 측정 정본 (carry) | `_internal/cache/rq3/latency/{phase2,phase3}/` | carry (정본) |
| archive 이동 (본 세션) | `_internal/handoff/archive/handoff_20260520_141449_*` + `새세션_복붙_프롬프트_20260520_141449.md` | 완료 |

CLAUDE.md anchor 갱신 (line 23): 직전 anchor `handoff_20260520_141449_deck_v2_vision검증.md` → **본 handoff (`handoff_20260520_144446_통계보강_polish_서버backup.md`)**.

## 7. carry-forward / 보류 / 미커밋 (본 세션 직후)

- **★ 미커밋 변경** (본 세션):
  - `_internal/scripts/analyze_latency.py` (수정)
  - `_internal/cache/rq3/latency/phase2/figures/paired_stats.csv` (수정)
  - `_internal/cache/rq3/latency/phase2/figures/paired_stats_pre_effect_20260520_144326.csv` (신규)
  - `_internal/cache/rq3/latency/phase3/figures/paired_stats.csv` (수정)
  - `_internal/cache/rq3/latency/phase3/figures/paired_stats_pre_effect_20260520_144326.csv` (신규)
  - `_internal/cache/rq3/latency/{phase2,phase3}/figures/*.png + *.pdf` (재생성)
  - `submission/_drafts/속도는벡터_6_11_최종보고서_20260520_144446.{md,pdf,docx}` (신규)
  - `submission/_drafts/속도는벡터_발표deck_수정프롬프트_polish_20260520_144446.md` (신규)
  - `_internal/server_backup_20260520/` (신규 2.6G·22117 file·.gitignore)
  - `_internal/handoff/active/handoff_20260520_144446_*` (신규 2 file)
  - `_internal/handoff/archive/handoff_20260520_141449_*` (이동 2 file)
  - `CLAUDE.md` anchor (line 23)
- **deferred tool 로드 패턴**: 새 세션은 `ToolSearch select:TaskCreate,EnterPlanMode,ExitPlanMode,Monitor,TaskUpdate,TaskList` 선제 로드.
- **★ 사용자 귀가 후 맥북 동기화 deferred** — `~/.claude/rules/sync.md` 절차 그대로. 본 세션 산출 `_internal/server_backup_20260520/` 도 sync 대상.

## 8. ★ 환각 회피 룰 (carry, 보강 결과와 정합)

- 정본 수치 정합 = `_internal/cache/rq3/latency/{phase2,phase3}/figures/paired_stats.csv` (15 컬럼 신본) + 보고서 §5.5 표 5-3 + 본 handoff §3.1.
- **B1 plan 회복은 qid 의존 fragile (7/12)** — qid=0 만으로 generalize 금지. (V-D B16 좌측 0:0/4·1:4/4·2:3/4 carry)
- **CaseB > B1 latency 측면 우열은 없음** (paired Wilcoxon 7.7% 유의 中 5건 B1 빠름·8건 CaseB 빠름, 효과크기 86.9% small g). plan 회복 robustness 측면 우위만 강조. → B16 메시지 "실행 시간 거의 같다 / 결합 가치 = 견고함" 정합. **★ 본 세션 신규 carry — effect size 도 동일 결론 보강** (small effect 86.9% 가 latency 동등성 정량화).
- **Q12 qid 0 large effect (g ≈ −1.5)** — 같은 4 method 의 qid 1·qid 2 는 small effect (g < 0.4), p_holm = 1.0. plan recovery fragile 함과 동일 origin (sub-optimal plan latency 구간 1 cell).
- **core 4 cell sel=0.001 한정** — sel 일반화 금지. **★ 본 세션 신규 carry — phase3 sel=0.01·0.1 carry-over effect size 도 산출됨** (baseline anchor 50% 유의 = sel=0.01 의 4 cell 모두, sel=0.1 0건).
- **plan_signature 정의 = Node Type pre-order 튜플 (1-tuple)** — 보고서 정정 완료 (carry).
- **q9 sel=0.1 honest exception** — plan ≠ baseline 인데 speedup < 1.0. 보고서 §5.6 + §6.4 (1) 갈래 carry.
- vector.c·`build_custom.sh`/`apply_patch.sh` 손대지 말 것 (서버 backup 의 source 만 받음).
- **보고서 코드명(B1/CaseA/CaseB) 사용 OK / 발표물 코드명 노출 금지** — 발표물은 한국어 라벨(기본 엔진/베이스라인 방식/정답/결합 방식). v2 vision 검증 결과 코드명 노출 0건 carry.
- 이전 세션 (v11/v12) 수치 generalize 금지 — RQ3 portfolio (1508건) 와 「엔진 적용 검증」 latency (2880회 + Phase A 1920회) 는 별개.
- v2 = raster image PPTX 통째 변환 (XML 검증 불가 vision 만) carry — 다음 deck rebuild (v3) 시 PPTX 형식 사전 확인 권장. v3 polish 도 raster image PPTX 로 export 예상.
- **★ 본 세션 신규 carry — Hedges' g·Cliff's δ·bootstrap CI 정의**: g = mean(diff)/sd(diff) × Hedges 보정 j = 1 − 3/(4n−9) (paired diff). δ = (#a>b − #a<b)/n (paired). CI = paired diff 평균의 2.5/97.5 percentile bootstrap (n_boot=2000, rng_seed=7).

---

작성: 2026-05-20 14:55 KST — 본 세션 (통계 보강 + polish prompt + 서버 backup) 완료. 보고서 §5.5/§6.4 갱신 · v3 polish prompt · server_backup_20260520 2.6G/22117 file · paired_stats.csv 11→15 컬럼. → 다음 = 사용자 집 복귀 후 맥북 동기화 + 5/22·5/25·5/26·5/27·5/28·6/11 마감.
