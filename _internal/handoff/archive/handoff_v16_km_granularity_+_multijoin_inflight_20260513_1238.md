# Handoff v16 — 5/13 12:38 KST
## km granularity 80 측정 + 분석 완성 + multi-join re-stratification 측정 진행 중 (in-flight)

> **본 세션 5/12 12:13 ~ 5/13 12:38 (24h 25m) 산출**: (1) 박광현 5/15 미팅 자료 부록 F 추가 + 1page §5 / (2) km granularity 80 measurement (K=10/20/30) 회수 + 3-way 분석 / (3) method-level paradigm 내 분산 분석 / (4) PG 16 instance 자체 시작 framework (Exqutor source build binary) / (5) multi-join re-stratification framework 작성 + tmux launch (진행 중, ETA 3-4h) / (6) 박세은+강재현 카톡 답변 가이드 7건 / (7) 채림님 follow-up 메일 paste (자체 해결 통보).

---

## 0. TL;DR — 다음 세션 첫 30초

```bash
# 1. handoff_v16 read

# 2. multi-join 측정 status check (in-flight)
ssh capstone2026 "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_mj_restrat/ | wc -l && tail -5 /tmp/mj_restrat.log && ls /tmp/mj_restrat.flag 2>&1 && tmux list-sessions"
# 예상 ETA: 5/13 15:30 ~ 16:30 KST (~3-4h, sparse_rp A2-Fig9 CaseA 11분째 진행)

# 3. DONE flag 존재 시 → 3-way 비교 분석 진행 + v5 deck 정정 prompt 에 결과 추가

# 4. ScheduleWakeup 12:57 fire — auto monitoring 설정됨
```

---

## 1. 본 세션 산출 — 12 commits (5/12 14:00 ~ 5/13 12:15)

| Commit | 시점 | 내용 |
|---|---|---|
| **이전 v15** | 5/12 23:40 | (handoff_v15 v4 deck 완성 + 박세은/강재현 6건 피드백 반영) |
| 1741680 | 5/13 01:35 | method-level paradigm 내 분산 분석 (강재현 2번 정량 검증) |
| c85d359 | 5/13 02:00 | K=10 vs K=20 K-sensitivity 분석 |
| f1f5999 | 5/13 03:00 | K=10/20/30 3-way 완성 |
| 9424ed4 | 5/13 03:05 | v5 deck 정정 prompt 작성 |
| 636b28f | 5/13 04:06 | 박광현 5/15 미팅 자료 부록 F 추가 |
| aedb8ea | 5/13 12:05 | multi cell K-based learning 간접 비교 |
| **38b0336** | **5/13 12:15** | **v5 정정 prompt 5 추가 — 박세은 12:09 옵션 C (RQ1 SYSTEM vs BERN 재배치)** |

---

## 2. 측정 portfolio update (5/13 12:38 시점)

### 2.1 km granularity sensitivity 80 measurement (회수 + 분석 완료)

| Dir | scope | status |
|---|---|---|
| `paper_exact_km10/` | 4 anchor × 5 cells × 2 modes × K=10 | ✅ 40/40 |
| `paper_exact_km30/` | 4 anchor × 5 cells × 2 modes × K=30 | ✅ 40/40 |
| `paper_exact/` (K=20 base, 기존) | 56 method × 9 cells × 2 modes | 1001 file |

**핵심 finding** (분석 file: `_internal/analysis/km_granularity_sensitivity_3way_K10_K20_K30_20260513.md`):
- **sparse_rp**: K=10 +5.05% / **K=20 -10.60%** / K=30 -6.78% — ★ U-shape, K=20 sweet spot 결정적
- hilbert_real: K=10 -10.86% / K=20 -10.45% / K=30 -11.26% — K-robust
- hyperloglog: K=10 -9.51% / K=20 -9.47% / K=30 -9.86% — K-robust
- chao_weighted: K=10 -10.63% / **K=20 -12.01%** / K=30 -10.39% — K=20 sweet

→ multi-table cell 도 동일 패턴 (sparse_rp 만 K-sensitive)

### 2.2 multi-join re-stratification ⏳ 진행 중

- tmux session: **mj_restrat** (5/13 12:25 launch)
- wrapper: `/tmp/launch_multijoin_restrat.py` (864d concat + fresh KM20 학습)
- scope: 4 anchor × A2-Fig9 (DEEP+WIKI cross) × 2 modes = **8 measurement**
- output: `paper_exact_mj_restrat/`
- 진행: 12:25 launch → 12:36 시점 첫 measurement (sparse_rp A2-Fig9 CaseA) 11분째 진행
- 예상 ETA: **5/13 15:30 ~ 16:30 KST** (each measurement ~20-30분 due to large vector + KM20 학습)
- monitoring 자동: ScheduleWakeup 12:57 fire

### 2.3 method-level paradigm 내 분산 (분석 완료)

분석 file: `_internal/analysis/method_level_breakdown_20260513.md`

**핵심 finding**:
- paradigm 평균은 outlier method 가 왜곡 (P1 Cluster wavelet_hist +67.96%, P4 lp_bound +16.43%)
- 진짜 contribution = **12 anchor method 일관성** (cell 전반 -9~-10%, std 2-3 안정)
- 12 anchor: lpm2, hilbert, sparse_rp, hilbert_real, minibatch, chao_weighted, neuram, pca1d, reservoir, thompson_sampling, hyperloglog, opq+pq

### 2.4 multi cell K-based 학습 간접 비교 (분석 완료)

분석 file: `_internal/analysis/multi_cell_km_based_learning_comparison_20260513.md`

| Method | A2-Fig7 Δ% | A2-Fig9 Δ% | 학습 방식 |
|---|---:|---:|---|
| minibatch | -8.30 | -7.25 | 자체 K-means |
| sparse_rp (anchor) | -10.46 | -6.58 | KM20 carry-over |
| hilbert_real | -11.52 | -6.07 | carry-over |
| chao_weighted | -11.77 | -6.00 | carry-over |
| hyperloglog | -8.77 | -5.15 | carry-over |

→ 학습 방식의 차이가 multi cell 결과를 결정짓지 않음 — 둘 다 -6~-12% 범위. **method 자체 특성이 더 결정적**.

---

## 3. PG instance 시작 framework (★ 본 세션 발견)

### 3.1 사건 timeline

- 5/12 20:44 박세은 → 채림님 "서버 사용 안 함" 보고
- 5/13 새벽 ~ 채림님 서버 재부팅 (PG 16 cluster 미시작)
- 5/13 11:30 ~ PG instance start 시도 (PG 16 data dir vs PG 12.5/17 binary mismatch)
- 5/13 11:47 박세은 → 채림님 "PG 16 binary install 부탁" 메일 발송
- **5/13 12:15 자체 해결** — Exqutor source build PG 16.9 binary 발견 → 자체 시작 성공
- 5/13 12:25 박세은 follow-up "도움 cancel" 메일 발송 (사용자 paste)

### 3.2 PG 시작 방법 (sudo 권한 없이)

```bash
ssh capstone2026@165.132.140.240
export LD_LIBRARY_PATH=/mnt/ssd_238/Exqutor/PostgreSQL/pgvector/psql/lib:$LD_LIBRARY_PATH
/mnt/ssd_238/Exqutor/PostgreSQL/pgvector/psql/bin/pg_ctl -D /mnt/hdd0/home/capstone2026/vanilla_sf100 -l /tmp/pg_start.log start

# connection test
/mnt/ssd_238/Exqutor/PostgreSQL/pgvector/psql/bin/psql -h localhost -p 55435 -U wns41559 -d wns41559
```

### 3.3 측정 framework 정보

- PG port: **55435** (`mc.PORT = 55435` in measure_paper_exact.py)
- DB / User: **wns41559** / **wns41559**
- pgvector lib: `/mnt/ssd_238/Exqutor/PostgreSQL/pgvector/psql/lib/`
- pg_ctl 16.9: `/mnt/ssd_238/Exqutor/PostgreSQL/pgvector/psql/bin/pg_ctl`

### 3.4 wrapper scripts

- `/tmp/launch_km_variant.py` (v1) — mc.N_STRATA monkey-patch (K granularity)
- `/tmp/launch_km_variant_v2.py` (v2) — + cache_cluster_samples_inmem + bernoulli_estimate + equal_alloc 정정
- `/tmp/launch_multijoin_restrat.py` — multi-join (partsupp_deep_10 ⨝ part_wiki_10, 864d concat, fresh KM20)

---

## 4. v5 deck 정정 prompt 6 정정 (★ FINALIZED)

claude.ai/design 한도 80% — 5/16 토 reset 후 paste 또는 PPTX manual edit.

| # | 정정 | 핵심 |
|---|---|---|
| 1 | **S7 RQ1** SYSTEM vs BERN 재배치 (박세은 12:09 옵션 C) | MAX 17.32% (SIFT s=0.05) + Cross-dataset 격차 표 |
| 2 | S15 paradigm rollup + method-level breakdown table | paradigm 내 std + outlier 명시 |
| 3 | S16 신규 "왜 replace 만으로 안 되는가" | BUDGET + ASSUMPTION + NEGATIVE CONTROL 0/493 |
| 4 | S17 anchor method consistency narrative 재배치 | 12 anchor method std 2-3 일관성 강조 |
| 5 | S18 신규 K-sensitivity by method | sparse_rp U-shape vs robust anchor 3개 |
| 6 | Limitation 보강 | K-sensitivity + multi-table scope + ensemble cost |

source file: `submission/_drafts/archive/2026_05_12_cleanup/속도는벡터_5_27_키노트_prompt_v5_km_granularity_+_method_breakdown_20260513.md`

multi-join re-stratification 회수 후 정정 7 추가 plan: A2-Fig9 cell 의 multi-join re-stratification 결과 narrative + carry-over vs re-stratified paired 비교.

---

## 5. 카톡 답변 paste 가이드 (5/13 11:00 ~ 12:24 7건)

본 세션 안 강재현/박세은 카톡 답변 paste form 작성 (모두 줄글, 박세은 22:50 요청 형식). 모든 답변은 사용자가 paste 진행.

| 시점 | 답변자 | 주제 | 정량 검증 |
|---|---|---|---|
| 11:00 | 강재현 (5/13 0:20+1:00+1:32) | km granularity + paradigm 내 분산 | ✅ method_level + km_granularity 두 분석 |
| 11:32 | 박세은 (slide 7 SYSTEM-vs-BERN) | SYSTEM vs BERN 사용 가능 여부 + 3 옵션 | ✅ 5/6 측정 raw 활용 |
| 11:44 | 강재현 (multi-join metric) | single 과 multi 둘 다 q-error (qe_trim) | ✅ JSON schema 일치 |
| 12:09 | 박세은 (옵션 C 결정) | RQ1 narrative SYSTEM vs BERN 재배치 + 17.32% | ✅ v5 prompt 정정 5 추가 |
| 12:11 | 강재현 (km10/30 vs PG 메일 의도) | km10/30 완료 + multi-join 위해 PG 시작 | ✅ status 명확화 |
| 12:14 | 강재현 (carry-over 한계 확인) | multi-join 중단 + paradigm outlier 동의 | ✅ framework 한계 명시 |
| 12:20 | 강재현 (method 자체 klustering + km20 best) | method 자체 학습 framework + km20 sweet spot | ✅ 정량 답변 |
| 12:24 | 강재현 (피드백 환영) | 진행 중 status 알림 | ✅ acknowledged |

---

## 6. 박광현 5/15 미팅 자료 (D-2) update 완료

### 6.1 file 5종 (submission/_drafts/박광현_5월15일_미팅/)

| File | size | update |
|---|---:|---|
| 속도는벡터_박광현미팅_5월15일_slide_draft_20260511.{md,pdf} | 24KB md / **741KB PDF** | ★ 부록 F 추가 (km granularity + paradigm 내 분산) |
| 박광현+임채림_사전보고_간결_1page_20260512.{md,pdf} | 5KB / 388KB | ★ §5 추가 finding 섹션 |
| 박광현+임채림_5월15일_사전보고_요약_20260512.{md,pdf} | (변경 X) | 부록 E 5/12 02:50 실측 |
| 박광현_미팅_예상질문_답변_가이드_20260511.{md,pdf} | (변경 X) | |
| 5_27_deck_update_plan_post_5월15일미팅.{md,pdf} | (변경 X) | |

### 6.2 박광현 미팅 confirm 요청 (D-3 → D-2)

- climax stat 92.5% / Cliff's δ 63.0% / negative 0/493
- paradigm rollup 8 + method-level outlier 명시
- ★ cluster granularity sensitivity method 의존적 (sparse_rp U-shape vs 다른 anchor robust)
- ★ multi-join re-stratification 측정 진행 status (회수 시점 결과 추가)
- 정합성 위반 9 method 폐기
- ★ 학습 방식 (carry-over vs 자체 K-means vs multi-join re-stratification) 비교

---

## 7. 일정 + 다음 세션 mission

### 7.1 핵심 일정

| 일시 | event |
|---|---|
| **5/13 (수) 12:25 ~ 15:30** | multi-join re-stratification 측정 진행 중 (in-flight) |
| 5/13 morning ~ 저녁 | 박세은/강재현 추가 카톡 wait |
| 5/14 (목) D-1 | 박광현 미팅 자료 최종 점검 |
| **5/15 (금) 14:00** | **박광현 교수 미팅 D-3 → D-day** |
| 5/16 (토) | claude.ai/design 사용 한도 reset (현재 80%) — v5 deck 정정 prompt paste |
| 5/16 ~ 5/26 | deck finalize sprint |
| 5/26 (월) | finalize 마감 |
| **5/27 (화) 19:00** | **최종 발표 D-15** |
| **5/28 (목)** | 임채림 박사 SAP 미팅 |

### 7.2 다음 세션 mission

**즉시 (5/13 morning 또는 사용자 active 시)**:
1. multi-join 측정 status check (DONE flag 또는 진행 중)
2. DONE 시 → carry-over vs 자체 K-means vs multi-join re-stratification 3-way 비교 분석
3. v5 deck 정정 prompt 7 추가 (multi-join re-stratification 결과 narrative)

**5/13 ~ 5/14 (D-1)**:
4. 추가 카톡 답변 (강재현/박세은/이동욱)
5. 박광현 미팅 자료 v6 (multi-join 결과 부록 G 추가)

**5/15 (D-day)**:
6. 박광현 교수 미팅 (자료 5 file + v4 deck PDF + 분석 결과 share)

**5/16 ~ 5/26**:
7. v5 deck 정정 prompt claude.ai/design paste (한도 reset 후)
8. 또는 PPTX manual edit 진행
9. 6/11 최종보고서 outline v3 작성 시작

---

## 8. 사용자 정책 (5/12 ~ 5/13 verbatim)

- 5/12 12:36 "chrome 제어 열어놨으니까 남은 작업 또한 너가 전권 위임 받아서 진행하자"
- 5/12 13:04 "RQ1, RQ2, RQ3, exqutor 재현 및 추가 이런 식으로 진행"
- 5/12 14:23 storyline 7단계 verbatim
- 5/12 14:39 "추가 실험보다는 이제 내용 이해랑 정리, 방향성 결정"
- 5/12 22:50 박세은 "줄글 형식으로 바꿔주실 수 있을까요"
- 5/12 23:39 "3, 4, 5번 다 실행해서 다운 받았어"
- 5/13 00:51 "서버 사용 가능해. future work로 미루는 게 아니라 진행하는 걸로"
- 5/13 11:32 "클로드 디자인 수정은 최종적으로 실험이나 카톡에서 요청한 것들에 대한 작업 모두 마치고 나서 진행"
- 5/13 12:14 "재현이 요청한 게 있어서 (PG 메일 의도)"
- 5/13 12:23 "채림님한테 메일 다시 내가 보낼게 내용만 알려줘. 실험해야되는 것은 진행을 그대로"

**핵심 원칙 (5/13 12:38 시점)**:
- multi-join re-stratification 측정 진행 중 (ETA 15:30 ~ 16:30)
- v5 deck 정정 prompt 6 정정 finalized + 7 정정 (multi-join) 회수 후 추가
- 박세은/강재현 카톡 답변 모두 줄글 형식 + paste 가능 form 으로 작성
- 채림님 메일 cancel 완료 (자체 PG start 성공)
- 5/15 박광현 미팅 D-2 자료 ready (부록 F 추가)
- 학술 정직 narrative — paradigm 평균 X, anchor method 일관성 ✓

---

## 9. END

작성: 2026-05-13 12:38 KST  
다음 세션 진입: handoff_v16 + v15 + v12 read 로 0% loss 보장  
즉시 진행: multi-join 측정 monitoring + DONE 시 3-way 분석 + v5 deck 정정 plan finalize  
다음 mission: 5/15 박광현 미팅 D-day → 5/27 최종 발표 D-15 → 5/28 임채림 SAP
