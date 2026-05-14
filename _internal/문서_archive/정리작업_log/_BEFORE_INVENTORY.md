# _BEFORE_INVENTORY.md — 정리 작업 직전 baseline

> 작성: 2026-05-11 01:25 KST  
> 목적: 4-phase 종합 정리 작업 전 모든 산출물 baseline 보존  
> 범위: 로컬 (_internal/) + memory + server (handoff 정보 기반) — 메인 세션 영향 0

---

## 0. TL;DR — 산출물 카운트

| 영역 | 수 | 상태 |
|---|---|---|
| _internal/handoff_*.md | 10 file | 활성 5 / 폐기 5 |
| _internal/method_verification_20260510/ | 11 file (5,777 lines) | active (P1-P6 audit) |
| _internal/method_verification_20260510_phase4/ | 5 file (~1,500 lines) | active (Phase 4 11 method) |
| _internal/validation/ | 13 file + data/ 319 항목 | active (4-layer audit) |
| _internal/scripts/ | 75 항목 (.py + .sh + .md) | active 32 / 폐기 후보 43 |
| _internal/scripts/methods/ | 26 file | extra2 20 method registry sources |
| _internal/state/ | 12 file | active (current/next/roadmap/...) |
| _internal/archive/ | 4 dir (5/7/8/9 + handoff_v0_to_v18) | history 보존 |
| _internal/cache/ | 13 dir | analysis 결과 캐시 |
| _internal/records/kakaotalk/ | 51 file | 회의록 |
| _internal/records/weekly/ | 3 file | 주간보고 |
| memory/ | 20 file (14 active + archive) | persistent cross-session |
| reference/papers/ | 71 file | 참고 논문 PDF |
| reference/summaries/ | 166 file | 논문 총정리 md/pdf |
| reference/exqutor_query_plans/ | 5 dir | paper Q*.sql verbatim |
| plans/ | 12 file | 연구 설계안 (RQ재정립 v6/v7 + outline_v2) |
| submission/_drafts/ + 제출완료/ | 14+22 항목 | 팀 공유 |
| experiments/results/ | 24 dir | 측정 결과 (rsync 후) |
| Untracked git | 26건 | 본 정리 작업의 핵심 대상 |

---

## 1. _internal/ 루트 32 항목 (완전 list)

| 항목 | 종류 | 크기/항목 | mtime | 분류 |
|---|---|---|---|---|
| README.md | meta | 1.5 KB | 4/27 | 활성 |
| Adaptive_Sampling_method_분석_20260508.md | doc | 23 KB | 5/8 | history (Adaptive 분석) |
| RQ3_paradigm_심층검증_20260508.md | doc | 23 KB | 5/8 | history (RQ3 paradigm) |
| claude_design_prompt_storyline_20260508.md | doc | 21 KB | 5/8 | history (deck 설계) |
| slide_redesign_v2_20260508.md | doc | 27 KB | 5/8 | history (slide redesign) |
| sync_verify_20260509.md | doc | 3 KB | 5/9 | history (sync 검증) |
| yfcc_compare_20260508.log | log | 0.9 KB | 5/8 | history |
| session_state.json | meta | 0.2 KB | 3/30 | history (오래됨) |
| **handoff_v0_FINAL_SCOPE_20260510_0125.md** | handoff | 51 KB | 5/10 | **archive** (v1~v5 superseded) |
| handoff_v0_FINAL_SCOPE_20260510_0125.bak.md | handoff | 20 KB | 5/10 | **archive** (.bak) |
| **handoff_v1_NEW_SESSION_20260510_1336.md** | handoff | 15 KB | 5/10 | **archive** (v2 superseded) |
| **handoff_v2_paper_verbatim_decisions_20260510_1418.md** | handoff | 17 KB | 5/10 | **active** (5 critical decisions, 직교) |
| **handoff_v3_method_verification_20260510_2030.md** | handoff | 13 KB | 5/10 | **active** (method audit summary) |
| **handoff_validation_statistics_20260510_2030.md** | handoff | 12 KB | 5/10 | **active** (4-layer audit spec) |
| **handoff_back_validation_20260510_2046.md** | handoff | 10 KB | 5/10 | **active** (validation→main feedback) |
| **handoff_main_session_FULL_STATE_20260510_2045.md** | handoff | 34 KB | 5/10 | **active** (16 sections 종합) |
| **handoff_v4_session_20260510_2144.md** | handoff | 11 KB | 5/10 | **active** (자동 chain monitor) |
| **handoff_v5_phase4_brainstorm_20260511_0110.md** | handoff | 16 KB | 5/11 | **active** (latest, Phase 4 11 method) |
| archive/ | dir | 4 sub-dir | 5/10 | history 보존 |
| cache/ | dir | 13 sub-dir | 5/10 | analysis 결과 cache |
| guideline/ | dir | 5 active set + archive | 5/8 | active (실행/제출/문서/미팅/발표) |
| learning/ | dir | kr/us + 클로드코드활용지침 | 4/27 | history (학습 자료) |
| **method_verification_20260510/** | dir | 11 file (5,777 line) | 5/10 | **active** (P1-P6 audit) |
| **method_verification_20260510_phase4/** | dir | 5 file | 5/11 | **active** (Phase 4 11 method) |
| records/ | dir | kakaotalk/51 + weekly/3 | 5/10 | active (회의록) |
| scripts/ | dir | 75 항목 | 5/11 | active + archive 후보 |
| server_wrappers_backup_20260507/ | dir | 4 항목 | 5/9 | history (5/7 wrapper 백업) |
| state/ | dir | 12 file | 5/10 | active (state 분리) |
| **validation/** | dir | 13 file + data/319 | 5/10 | **active** (4-layer audit) |

---

## 2. _internal/handoff_*.md — 10 file 분류

### 2.1 active (다음 세션 즉시 read 권고, 5건)

| File | size | KST | 핵심 | active 사유 |
|---|---|---|---|---|
| **handoff_v5_phase4_brainstorm_20260511_0110.md** | 16 KB | 5/11 01:10 | Phase 4 11 method M1~M11 + scp + measurement launch | latest |
| **handoff_v4_session_20260510_2144.md** | 11 KB | 5/10 21:44 | 자동 chain monitor (sigma + RQ2 5-way) | chain 진행 중 |
| **handoff_main_session_FULL_STATE_20260510_2045.md** | 34 KB | 5/10 20:45 | 16 sections 종합 (5단계 narrative + SSN=FB + 39 method + 자원룰) | 모든 context 보존 |
| **handoff_back_validation_20260510_2046.md** | 10 KB | 5/10 20:46 | 검증→메인 feedback (Fig 12 영역 분리, narrative -25.5% → -4.3%) | 정정 권고 적용 진행 |
| **handoff_v2_paper_verbatim_decisions_20260510_1418.md** | 17 KB | 5/10 14:18 | 5 critical decisions (Fig 5 queries / clamping / sel scope / A3 ECQO / metric) | paper exact baseline |

### 2.2 archive (이전 단계, 5건 — handoff_v0~v3 + validation_statistics)

| File | size | KST | 핵심 | archive 사유 |
|---|---|---|---|---|
| handoff_v0_FINAL_SCOPE_20260510_0125.md | 51 KB | 5/10 01:25 | v0 FINAL SCOPE 36 method × 26 cell × 3 SF=100 | v3/v5 superseded (method registry 정정) |
| handoff_v0_FINAL_SCOPE_20260510_0125.bak.md | 20 KB | 5/10 01:25 | v0.bak | history 보존 |
| handoff_v1_NEW_SESSION_20260510_1336.md | 15 KB | 5/10 13:36 | 새 세션 시작 가이드 | v2 5 decisions 반영 후 superseded |
| handoff_v3_method_verification_20260510_2030.md | 13 KB | 5/10 20:30 | method audit summary (Q1~Q5 confirm 권고) | _SUMMARY.md + Q1~Q5 confirmed (5/11 01:05) |
| handoff_validation_statistics_20260510_2030.md | 12 KB | 5/10 20:30 | validation 4-layer audit spec | back_validation 으로 결과 도착 |

---

## 3. _internal/scripts/ — 75 항목 분류

### 3.1 active (현재 측정 / 분석에 사용 중, 32건)

| File | 용도 | 비고 |
|---|---|---|
| **measure_paper_exact.py** | 메인 측정 (1100+ lines, paper exact + RQ1/RQ2/RQ3) | **변경 X** (메인 측정 中) |
| **_measure_common.py** | 공통 inf (paper N=385 + 5-way mode) | **변경 X** (server-side 공통) |
| **analyze_paper_exact.py** | Phase D 분석 + 5단계 narrative auto-fill | active |
| **compute_stratum_sigma_paper_exact.py** | 신규 (5/10 21:29) σ_j builder | sigma chain 후 사용 |
| **method_phase4_extra.py** | Phase 4 11 method (M1~M11) assign 함수 | server scp 대기 |
| **method_tier1_p9_p10.py** | Q4 Tier 1 6 method (DBSCAN/KDE/MHIST-2/HLL/RSVD/wavelet) | active |
| **method_hilbert_real.py** | 진짜 high-D Hilbert (Q1 (C) rectify) | active |
| **PATCH_phase4_registry.md** | measure_paper_exact.py Phase 4 패치 instruction | scp 대기 |
| **PATCH_hilbert_real_registry.md** | hilbert_real 패치 instruction | applied |
| **measure_multi_vec_patch.md** | A2-Fig8 patch instruction | post-fix 대기 |
| run_phase_b_phase4.sh | Phase 4 launch script (--all/--method/--cell/--dry-run) | server scp 대기 |
| run_phase_b_q1q4.sh | Q4 Tier 1 launch | active |
| run_phase_a2fig8_tier1.sh | A2-Fig8 tier1 launch | post-fix 대기 |
| md2pdf.py / md2pdf_academic.py | doc→PDF (Chrome CDP) | active (문서 생성) |
| md2docx.py / _build_docx_v1.py | doc→DOCX | active |
| methods/ | 26 file (extra2 20 method sources) | active (registry 호출) |
| midterm_pptx/ | 4 항목 | 4/28 중간발표 산출 |

### 3.2 archive 후보 (이전 측정 끝난 script, 43건)

이전 측정/분석 끝난 script (Phase B/C Tier 1 완료 후 폐기 후보):

| File | 용도 | archive 사유 |
|---|---|---|
| analyze_bern_qerr_per_dataset.py | RQ1 Bernoulli analysis | RQ1 paper exact 진행 후 superseded |
| analyze_ensemble.py | Multi 11 method ensemble 분석 | ensemble 확장 후 superseded |
| analyze_failure_modes.py | failure mode 분석 | RQ3 v7 paradigm 분석 후 superseded |
| analyze_k_optimal.py | K sweep 분석 | K-aware sweep 보강 진행 중 → still active |
| analyze_multi_paradigm.py | Multi 11 method paradigm 분석 | 5/9 Multi 측정 후 사용, current X |
| analyze_phase_g.py + .bak_v8 | phase G 분석 (108 KB) | superseded by analyze_paper_exact.py |
| analyze_ssn_ceiling.py | SSN ceiling 분석 | history (5/8) |
| analyze_tier_elimination.py | Tier S/A/B/Q1/Q4 elimination | **사용자 명시 폐기** ("Tier 분류 의미 X") |
| build_FB_single_ensemble.py | FB ensemble 빌더 | 5/9 진행 끝남 |
| build_charts_5_8.py | 5/8 차트 빌더 | 4/28 발표 후 |
| build_native_pptx_5_8.py | PPTX 빌더 (86 KB) | 4/28 발표 후 |
| build_new_multi_cells.py | new multi cells 빌더 | history |
| build_sf100_single.py | SF=100 single setup | RQ1/RQ2 paper exact 진행 후 |
| build_wiki.py / build_yfcc.py | dataset 빌더 | NPY cache 빌드 끝 |
| chain_unified.py | unified chain | superseded by 자동 monitor |
| finalize_5_9_morning.sh | 5/9 morning 완료 script | history |
| launch_sf100_safe.sh | sf100 safe launcher | superseded |
| master_v6_fill_partial.py | master_v6 §10.6 fill helper | history (master 채움 끝) |
| measure_exqutor_replication_DRAFT.py | handoff_v2 §3 초기 design (19 KB) | superseded by measure_paper_exact.py |
| measure_multi_4kang.py | 4강 multi 측정 | history |
| measure_multi_5mode.py | 5-mode multi 측정 | superseded |
| measure_multi_adaptive_sampling.py | Adaptive multi 측정 | history (5/9 끝) |
| measure_multi_all.py | all multi 측정 | superseded |
| measure_multi_ensemble.py + .bak_v8 | multi ensemble | superseded |
| measure_multi_paradigm.py + .bak_v8 (38KB+42KB) | multi paradigm | superseded |
| measure_multi_table_join.py | multi table join | post-fix 대기 |
| measure_multi_vector.py | multi vector | A2-Fig8 post-fix 대기 |
| measure_phase_f_baselines.py | Phase F baseline | superseded by paper exact |
| parallel_download.sh | 병렬 다운로드 | history |
| plot_w4_partial.py | W4 plot | history |
| prepare_cell.py | cell prep | history (5/8) |
| run_*.py / .sh (10건: agglomerative, cell_full, coresets, dbscan, faiss_ivf, fixed_rate_baselines, hierarchical_kmeans, kmeans_pp, optics, pca_kmeans, subset_training) | 단일 method launch | superseded by measure_paper_exact.py |
| setup_multi_sf1.py | multi SF1 setup | NPY cache 빌드 끝 |
| watch_*.sh (3건: final_chain, phase2, post_8m) | 외부 monitor | superseded by Claude Code Monitor tool |

---

## 4. _internal/method_verification_*/ — audit 통합 (16 file, ~7,300 lines)

### 4.1 method_verification_20260510/ (5/10 8 agent audit, 11 file)
- **_SUMMARY.md** (225 line) — 41 method 종합 (3.8/10 평균, 22 critical defect)
- **_HANDOFF_PROMPT_for_main_session.md** (88 line) — 메인 세션 진입 가이드
- additional_methods_brainstorm.md (668 line) — Tier 1 6 method 추가 권고
- paradigm_P1_cluster.md (719 line) — P1 8 method
- paradigm_P2_spatial.md (692 line) — P2 5 method (★3 hilbert 발견)
- paradigm_P3_streaming.md (660 line) — P3 7 method
- paradigm_P4_dimreduction.md (902 line) — P4 8 method (★4 sparse_rp Li 2006)
- paradigm_P5_qmc_hashing.md (815 line) — P5 8 method
- paradigm_P6_quantization_other.md (820 line) — P6 5 method (paradigm 폐지 권고 1.6/10)
- sf_feasibility_matrix.md (501 line) — 615 cell scope

### 4.2 method_verification_20260510_phase4/ (5/11 phase 4 brainstorm, 5 file)
- **_FINAL_LIST.md** (532 line) — 11 method 상세 spec (M1~M11)
- **_BRAINSTORM_REPORT.md** (224 line) — 메인 보고용 ~1,000 단어
- _BRAINSTORM_FULL.md (862 line) — 16 카테고리, 553 method 발굴
- _FILTER_BRAINSTORM.md (392 line) — 14 필터 + 7 critical
- _FILTER_ANALYSIS.md (396 line) — cascade 7 stage drop 사유

---

## 5. _internal/validation/ — 4-layer audit (13 file + data/319 항목)

### 5.1 audit script (4 file)
- audit_paired_delta.py (Layer 1)
- audit_wilcoxon_bh_fdr.py (Layer 2)
- audit_narrative_consistency.py (Layer 3)
- audit_cherrypicking.py (Layer 4)

### 5.2 audit md (5 file)
- **SUMMARY_validation.md** (271 line) — 종합
- paired_delta_audit.md (450 line) — Layer 1
- wilcoxon_bh_fdr_audit.md (370 line) — Layer 2
- narrative_consistency_audit.md (364 line) — Layer 3
- cherrypicking_audit.md (208 line) — Layer 4

### 5.3 audit data (2 csv + data/319 항목)
- audit_data_paired.csv (48 KB)
- audit_data_wilcoxon.csv (30 KB)
- data/ — server read-only rsync (310 JSON + 5 CSV + REPORT_paper_exact.md)

---

## 6. _internal/state/ — 12 file (분리된 dynamic state)

| File | line | mtime | 활성 |
|---|---|---|---|
| _current.md | 48 | 5/10 | 활성 (v0 FINAL SCOPE reset baseline) |
| _next.md | 30 | 5/9 | 활성 (5/9 morning trigger checklist) |
| _roadmap.md | 19 | 5/9 | 활성 (전체 로드맵) |
| _schedule.md | 25 | 5/9 | 활성 (학기 일정) |
| _artifacts.md | 38 | 5/9 | 활성 (산출물 위치) |
| _consolidation_20260510_1215.md | 256 | 5/10 | history (5/10 12:15 통합) |
| _data_scope_decision_20260510_0114.md | 171 | 5/10 | history (data scope 결정) |
| _kakaotalk_narrative_method_table_20260510_0030.md | 209 | 5/10 | history (카톡 narrative 표) |
| _method_portfolio_v9_extreme_20260509_2335.md | 291 | 5/10 | history (v9 extreme portfolio) |
| archive/_method_portfolio_v8_research_20260509_2235.md | — | 5/10 | history |

---

## 7. memory (~/.claude/projects/-Users-hyunbin-Capstone/memory/) — 20 file

### 7.1 active (14 file)
- MEMORY.md (index)
- user_profile.md
- project_capstone.md / project_schedule.md / project_team_hierarchy.md / project_seeun_reminder_20260511.md
- feedback_document_style.md / feedback_pdf_theme.md / feedback_apple_notes_format.md
- feedback_research_scope_control.md / feedback_session_topology.md / feedback_deck_design.md
- feedback_paper_exact_principle.md (5/10 14:27)
- feedback_method_audit_findings.md (5/10 21:53, 4.8 KB)
- reference_server.md / reference_notion.md / reference_apple_notes.md
- reference_document_templates.md / reference_exqutor_paper_verbatim.md (5/10 14:27)

### 7.2 archive (1 dir)
- archive/session_resume_20260415_1132.md

---

## 8. 핵심 측정 결과 위치 (server)

> 메인 세션 영향 0 원칙 — read-only 정보로만 inventory.

### 8.1 Server `/mnt/hdd0/home/capstone2026/cache/rq3/`
- measure_paper_exact.py + analyze_paper_exact.py + _measure_common.py + compute_stratum_sigma_paper_exact.py (모두 5/10 12:30+ KST)
- paper_exact/*.json + *.csv + REPORT_paper_exact.md (~316/702 measurements as of 5/10 21:44)
- run_phase_*.sh (8개)
- methods/ (extra2 20 method 별 module)

### 8.2 Server `/mnt/hdd0/home/capstone2026/cache/rq1/`
- partsupp_{deep,sift,fb}_{1,10,100}_{vectors,strata,pks}.npy (~150 GB)
- query_pool_{DEEP,SIFT,SSN,YFCC,WIKI}_sf{1,10,100}.parquet
- query_selectivity_{DEEP,...}_sf{1,10,100}.parquet (sel = [0.01, 0.05, 0.1, 0.3, 0.5])

### 8.3 Server `/mnt/hdd0/home/capstone2026/log/`
- paper_exact_phase_*.log (cell × phase 개별)
- sigma_build_paper_exact_*.log
- rq2_paper_exact_5way_*.log

### 8.4 Server tmux sessions (handoff_main §13 verbatim)
- capstone / orchestrator / paper_exact / phase_b_smoke / phase_b_full / rq1_rq2 / fig8_fix (kill) / ecqo / a1_ssn_retry / sparse_rp_retry / gmm_retry
- pb_A1-DEEP/SIFT/SSN, pb_A4-sel, pb_A5-scale-sf100 (Phase B per cell)
- pc_A1-* / A2-Fig7/Fig9 / A4-sel / A5-scale-sf{1,10,100} (Phase C)
- pbe_*, pbe2_*, pce_* (Phase B/C extra 진행 中)
- 5/11 Phase 4 11 tmux 추가 launch 예정 (handoff_v5)

---

## 9. Untracked Git 26건 (정리 대상)

| File/Dir | 크기/항목 | 분류 |
|---|---|---|
| handoff_back_validation_20260510_2046.md | 10 KB | active |
| handoff_main_session_FULL_STATE_20260510_2045.md | 34 KB | active |
| handoff_v2_paper_verbatim_decisions_20260510_1418.md | 17 KB | active |
| handoff_v3_method_verification_20260510_2030.md | 13 KB | archive |
| handoff_v4_session_20260510_2144.md | 11 KB | active |
| handoff_v5_phase4_brainstorm_20260511_0110.md | 16 KB | active |
| handoff_validation_statistics_20260510_2030.md | 12 KB | archive |
| method_verification_20260510/ | 11 file | method_audit/20260510_initial/ |
| method_verification_20260510_phase4/ | 5 file | method_audit/20260511_phase4/ |
| records/kakaotalk/raw_export/ | unknown | records/kakaotalk/raw_export/ (그대로) |
| scripts/PATCH_hilbert_real_registry.md | 5 KB | active |
| scripts/PATCH_phase4_registry.md | 6 KB | active |
| scripts/_measure_common.py | 21 KB | active |
| scripts/analyze_paper_exact.py | 26 KB | active |
| scripts/compute_stratum_sigma_paper_exact.py | 6 KB | active |
| scripts/measure_exqutor_replication_DRAFT.py | 19 KB | archive (superseded) |
| scripts/measure_multi_vec_patch.md | 8 KB | active (post-fix instruction) |
| scripts/measure_paper_exact.py | 64 KB | active |
| scripts/method_hilbert_real.py | 10 KB | active |
| scripts/method_phase4_extra.py | 26 KB | active |
| scripts/method_tier1_p9_p10.py | 21 KB | active |
| scripts/run_phase_a2fig8_tier1.sh | 1.6 KB | active |
| scripts/run_phase_b_phase4.sh | 5.2 KB | active |
| scripts/run_phase_b_q1q4.sh | 1.9 KB | active |
| validation/ | 13 file + data/319 | active |
| reference/exqutor_query_plans/ | 5 dir | active (paper Q*.sql verbatim) |

---

## 10. 핵심 method registry (measure_paper_exact.py line 416-880)

### 10.1 Total 57+ method dispatch

**메인 측정 method** (active branch in line 416-880):

| line | method_name | 분류 |
|---|---|---|
| 416 | bernoulli | baseline |
| 420 | sparse_rp | ★4 (Li 2006 reference 정정 필요) |
| 429 | random_projection | extra |
| 435 | minibatch | Tier 1 |
| 441 | gmm | Tier 1 |
| 449 | hilbert / pca2d_lex | ★3 (PCA 2D lex sort, defect) |
| 463 | hilbert_real | true high-D Hilbert (Q1 (C) rectify) |
| 471 | dbscan / kde_parzen / mhist2 / hyperloglog / rsvd / wavelet_hist | **Q4 Tier 1 6 method** |
| 485 | chao_weighted / lpm1_proper / cum_sqrtf / lavallee_hidiroglou / idistance / zorder_morton / skilling_hilbert / ica_fastica / kmeans_neyman / rabitq_strat / idistance_neyman | **Phase 4 11 method (M1~M11)** |
| 499 | minibatch_partial | ★2 |
| 509 | lsh | Tier 1 |
| 520 | pca1d | Tier 1 |
| 530 | sobol | Tier 1 (low-discrepancy) |
| 539 | reservoir | Tier 1 (RANDOM20 random rename 권고) |
| 544 | faiss_ivf | Tier 1 |
| 558 | pq | extra (md5 hash defect) |
| 573 | kdtree | extra (idx % n_strata defect) |
| 581 | halton | extra (low-discrepancy) |
| 588 | hammersley | extra (low-discrepancy) |
| 598 | coreset | extra |
| 606 | birch | extra |
| 615 | agglomerative | extra |
| 632 | dense_rp | extra (random_projection alias) |
| 643 | opq | extra2 (md5 defect) |
| 657 | kdpp | extra2 (≡ epsilon_net) |
| 675 | banditucb1 | extra2 (UCB1 미구현 defect) |
| 683 | neuram | extra2 (≡ PCA1D defect) |
| 695 | thompson_sampling | extra2 (defect) |
| 704 | mfmc | extra2 (defect) |
| 716 | epsilon_net | extra2 |
| 733 | ams_count_sketch | extra2 (≡ lsh defect) |
| 743 | neurocard_lite | extra2 (≡ PCA8+KMeans, rename) |
| 754 | adaptive_bucket_probing | extra2 (≡ PCA1D defect) |
| 765 | ccsketch | extra2 (defect) |
| 775 | factor_join | extra2 (≡ PCA2D+grid, rename) |
| 789 | lp_bound | extra2 (SIGMOD 2025 LpBound 명칭 충돌, rename `l2_quantile`) |
| 797 | cca1d | extra2 (≡ PCA1D defect) |
| 807 | cocluster_nystrom | extra2 (Nyström 미구현 defect) |
| 833 | tucker | extra2 (≡ PCA3D+grid, rename) |
| 846 | vinecopula | extra2 (rank+PCA1D, rename) |
| 860 | hkbu_repsample | extra2 (max_iter=5 미수렴) |
| 867 | lhs | extra2 (low-discrepancy) |
| 875 | lpm2 | extra2 (Weiszfeld median + radial, rename `radial_quantile`) |

**총 합**: 1 baseline + 7 main + 1 hilbert_real + 6 Q4 + 11 Phase 4 + 5 Tier 1 + 4 + 8 extra + 20 extra2 = **63 dispatch branches**, 사용자 명시 "57 methods" 와 매칭 (별칭 / 폐기 method 제외 시).

### 10.2 폐기 후보 (Q2 audit 권고 + 중복)
**10건 폐기 권고** (handoff_v3 §1.3): thompson_sampling, mfmc, neuram, cca1d, ams_count_sketch, ccsketch, kdpp, cocluster_nystrom, banditucb1, hkbu_repsample (or coreset)

---

## 11. 정리 작업 후 목표 구조

```
_internal/
├── MASTER_README.md             ★ 단일 진입점
├── MASTER_HANDOFF.md            ★ handoff 통합 (v0~v5 + validation + phase 4)
├── METHOD_REGISTRY.md           ★ 57 method paradigm 분류 + 폐기 사유
├── EXPERIMENT_REGISTRY.md       ★ 9 cells × 57 methods × 3 modes matrix
├── SERVER_REGISTRY.md           ★ port/cache/log/PG/tmux inventory
├── CHANGELOG.md                 ★ 5/10~5/11 timeline
├── _BEFORE_INVENTORY.md         (이 파일, baseline 보존)
├── _CLEANUP_LOG.md              ★ Phase 4 mv log
├── naming_convention.md         ★ file naming 규칙
├── README.md                    (기존, 활성)
│
├── handoff/
│   ├── active/    (v2/v4/v5 + main_session_FULL_STATE + back_validation, 5건)
│   └── archive/   (v0/v0.bak/v1/v3/validation_statistics, 5건)
│
├── method_audit/
│   ├── 20260510_initial/   (P1-P6 audit, 11 file)
│   └── 20260511_phase4/    (Phase 4 11 method, 5 file)
│
├── scripts/
│   ├── (active 32건 — measure_paper_exact, _measure_common, analyze_*, method_*, run_*, PATCH_*, md2*)
│   └── archive/   (43건 — 이전 측정 끝난 script)
│
├── validation/                  (13 file + data/319, 그대로)
├── state/                       (12 file, 그대로)
├── archive/                     (4 sub-dir, 그대로 — 5/7/8/9 + handoff_v0_to_v18)
├── cache/, guideline/, learning/, records/, server_wrappers_backup_*  (그대로)
└── (history doc 6건: Adaptive_Sampling_method_분석, RQ3_paradigm_심층검증, claude_design_prompt_storyline, slide_redesign_v2, sync_verify, yfcc_compare — _internal/archive/2026_05_08_history/ 후순)
```

---

## 12. END

작성: 2026-05-11 01:25 KST (정리 작업 시작 baseline)  
다음 단계: Phase 2 (paradigm 재분류 + naming) → Phase 3 (6 file 작성) → Phase 4 (mv + cleanup log)  

**검증 anchor**: 모든 mv는 git untracked 또는 본 baseline 기록 후만 진행. server 영향 0.
