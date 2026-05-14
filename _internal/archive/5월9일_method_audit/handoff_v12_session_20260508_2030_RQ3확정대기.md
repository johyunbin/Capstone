# Handoff v12 — 5/8 20:36 KST, RQ3 paradigm 확정 대기

> **이전**: handoff_v11_session_20260508_PostMeeting.md (회의 후 finalize)
> **다음**: handoff_v13 (RQ3 paradigm + 11 method 확정 + Adaptive baseline launch 후)
> **이번 세션 시점**: 5/8 19:00 회의 후 1시간 36분 경과, RQ3 paradigm 확정 대기 + Deep Review Agent 백그라운드 진행

---

## 0. 다음 세션 진입 prompt (복사 사용)

```
@_internal/handoff_v12_session_20260508_2030_RQ3확정대기.md 읽고 이어서 진행.

5/8 회의 후 [N]시간 경과. Deep Review Agent (ac950253eb5332e89) 진행 상태 확인.

# 즉시 launch (Deep Review 와 병렬, RQ3 확정 무관) — 사용자 confirm 후

[E] Adaptive Sampling 본 논문 (Exqutor arXiv:2512.09695v2) method 분석 에이전트 호출 (background)
   → 산출: _internal/Adaptive_Sampling_method_분석_20260508.md
   → Exqutor 의 momentum 기반 동적 sample size 알고리즘 정독 + 본 연구 stratification 과의 paired 비교 설계 + 측정 코드 design (run_adaptive_sampling.py 골격)

# Deep Review 완료 후 (~21:00) 

1. _internal/RQ3_paradigm_심층검증_20260508.md 검토 (메인 세션, with 사용자)
2. 5 paradigm + N method 최종 confirm + ★4 final 결정
3. RQ3 확정 후 백그라운드 4 에이전트 병렬 launch:
   [A] 자문 메일 v3 update (5 paradigm × N method 정정 + 박세은 카톡 reframe)
   [B] Adaptive Sampling 측정 코드 finalize (E 산출 기반, 서버 launch 준비)
   [C] Multi 광범위 wrapper 확장 (measure_multi_paradigm.py, N method 기준)
   [D] 발표 slide redesign 안 (5 paradigm × representative + Top 4 + Pruned)
4. 박세은 카톡 update (paradigm naming 정정)
5. 서버 launch (Adaptive baseline overnight, ~5h) — 5/8 22:00 ~ 5/9 03:00

원칙:
- 메인 세션 = 사용자 대화 + 에이전트 결과 통합 + 결정 (token 절약, 주간 한도 17% 남음)
- 백그라운드 에이전트 = 모든 작업 위임 (분석/코드/측정 준비/narrative redesign)
- E 는 RQ3 확정 무관 → 새 세션 시작 즉시 launch 가능
```

---

## 1. 진행 commit 3건 (5/8 18:48 ~ 20:30)

| Commit | 시각 | 내용 |
|---|---|---|
| `d07a583` | 18:48 | Slides.jsx S12 STAGE 3 update + _drafts 6 파일 archive 이동 |
| `8a030bc` | 20:00 | 5/8 회의록 + handoff_v11 §0 + CLAUDE.md update + 자문 메일 v1 (sub-agent draft, 140 lines) |
| `b2c5160` | 20:08 | 자문 메일 v2 narrative 축소 (110 lines, RQ3 = method 선정 단계로 축소) |

## 2. 5/8 19:00~19:30 비대면 회의 결과 (박세은 팀장 결정)

| 우선순위 | 결정 |
|---|---|
| ⭐⭐⭐ | **Adaptive Sampling 본 논문 비교 + multi-table 4강 적용** (가장 중요) |
| ⭐⭐ | 5/27 발표 준비 |
| ⭐ | SF100 — 시간 여유 시 (현실적 불가 가능성) |

**자문 메일 outline 3줄** (박세은 19:41):
1. (실험) RQ2 Neyman 했음, RQ3 method 들 찾아놓음
2. (데이터셋) SF1·SF10 한정
3. (자문 only) 현재 상황 전체

**박세은 카톡 협업 status** (20:18):
- 사용자 (조현빈) 가 §1·§2.1·§2.2·§2.3 narrative 카톡으로 박세은에게 공유
- 박세은 19:49 "넵넵" — narrative direction OK
- **변경 필요 시 paradigm naming 정정 update 카톡 권장** (다음 세션 task)

---

## 3. RQ3 5 paradigm + 11 method 확정 대기 (현재 단계)

### 3.1 사용자 (조현빈) 결정 history (5/8 19:50 ~ 20:32)

| 결정 항목 | 결정 |
|---|---|
| Q1. paradigm 분류 | C (5 main paradigm × sub-paradigm) 채택 |
| Q2. ★4 = sparse RP | OK (Hybrid 비논리 의문 → sparse RP 채택, 단 Deep Review 검증 후 확정) |
| Q3. 자문 메일 vs 지도확인서 | 분리 — 지금 메일 = 지도확인서 (RQ1/RQ2 finalize + RQ3 method 선정 단계), 자문 메일은 RQ3 확정 후 별도 작성 |
| Q1'. 5 paradigm + 11 method 확정 | "지금 방식이 맞는 거 같은데" + **Deep Review Agent 학술 검증 필요** |
| Q2'. ★4 sparse RP 검증 | Q1' 검증과 함께 에이전트 전권 위임 |
| Q3'. 서버 launch | RQ3 확정 후 → 다음 세션으로 내용 전달 |

### 3.2 11 method 확정 후보안 (Deep Review 대기 중)

| # | Paradigm | Sub | Method | 학술 출처 | 결과 (avg Δ%) | 4강 |
|---|---|---|---|---|---:|---|
| 1 | **P1 Cluster-based** | density | **HDBSCAN** | Campello 2013 | -8.04 | ★1 |
| 2 | P1 Cluster-based | centroid | MiniBatch | Sculley 2010 (WWW) | -7.62 | |
| 3 | P1 Cluster-based | distribution | GMM | Dempster 1977 | -7.60 | |
| 4 | **P2 Spatial Indexing** | curve | **Hilbert** | Hilbert 1891 / Faloutsos 1989 | -7.54 | ★3 |
| 5 | P2 Spatial Indexing | tree-VQ | faiss_ivf | Sivic-Zisserman 2003 | -7.71 | |
| 6 | **P3 Streaming** | online cluster | **MB_partial** | Sculley 2010+ | -7.63 | ★2 |
| 7 | P3 Streaming | online sample | Reservoir | Vitter 1985 | -6.78 | |
| 8 | **P4 Dim Reduction** | RP | **sparse RP** | Achlioptas 2003 (JL Lemma) | -6.91 | ★4 후보 |
| 9 | P4 Dim Reduction | PCA | PCA1D | Pearson 1901 / Hotelling 1933 | -7.35 | |
| 10 | **P5 Hashing/QR** | hashing | LSH | Indyk-Motwani 1998 | (Wave 0 failed) | reference |
| 11 | P5 Hashing/QR | quasi-random | Sobol | Sobol 1967 | +0.18 (Pruned) | reference |

### 3.3 5 paradigm 외 제외 method (19종, 명시)

**Hybrid / ambiguous** (6종, 명시적 제외):
- Hybrid (MB+Hilbert) — P1+P2 결합
- pca_kmeans — P4+P1 결합
- coresets — P1+P4 ambiguous
- kde_pilot — KM20 cluster leak suspect (Tier 2 boundary)
- distance_shell — Online QA (5 paradigm 외)
- importance_sampling — weight-based no-partition (5 paradigm 외)

**Redundancy** (13종, paradigm 내 representative 와 중복):
- kmeans_pp / DBSCAN / OPTICS — P1 redundancy (HDBSCAN, MiniBatch 와 중복)
- birch / agglomerative / hkmeans — P1 hierarchical redundancy
- zorder / kdtree / pq — P2 redundancy (Hilbert, faiss_ivf 와 중복)
- random_proj — P4 RP redundancy (sparse RP 와 중복, Wave 0 failed)
- halton / hammersley — P5 QR redundancy (Sobol 와 중복)
- spectral — P4 spectral redundancy

총: 30 - 11 - 6 - 13 = 0 ✓

---

## 4. Deep Review Agent 결과 (✅ 완료, 5/8 20:43 도착)

**Agent ID**: `ac950253eb5332e89`
**Launch 시각**: 5/8 20:36 KST
**완료 시각**: 5/8 20:43 KST (예상보다 빠름, ~7분)
**산출**: `/Users/hyunbin/Capstone/_internal/RQ3_paradigm_심층검증_20260508.md` (3370 words 한+영 혼용)

### 핵심 변경 사항 (Deep Review 권장, 200자 요약)

| # | 권장 | 비고 |
|---|---|---|
| 1 | **P5 "Hashing/QR" 분리** | LSH (failed) 와 Sobol 의 inductive bias 가 다름 → **P5 = "Low-discrepancy" 단일** 권장. LSH 는 별 paradigm 또는 narrative 사례로 처리 |
| 2 | **★4 = sparse RP 유지 ✅** | data-independent + ARI orthogonality #1 + Achlioptas 2003 canonical reference. 변경 불필요 |
| 3 | **누락 critical 3종 추가 측정 X** | Sketch family / Mean-Shift / R-tree / MinHash → **limitation 명시로 충분** (시간 절약) |
| 4 | **4강 narrative 강함, 변경 불필요** | HDBSCAN(P1) / MB_partial(P3) / Hilbert(P2) / sparse RP(P4) — **5 paradigm 중 4 paradigm distinct representative** → 학술 정합성 확보 |

→ **새 세션 시작 시**: Deep Review md 정독 + 위 4 변경 사항 사용자 confirm + paradigm framework 5→6 분리 (P5 hashing 별도) 결정.

---

## 5. 다음 세션 task list (우선순위)

### Step 0 — 즉시 launch (Deep Review 와 병렬, RQ3 확정 무관)

**Agent E** (백그라운드, 새 세션 시작 즉시 호출)
- Task: Adaptive Sampling 본 논문 (Exqutor arXiv:2512.09695v2) method 분석
- 산출: `_internal/Adaptive_Sampling_method_분석_20260508.md`
- 내용:
  · Exqutor 의 momentum 기반 동적 sample size 알고리즘 정독
  · 본 연구 stratification 과의 paired 비교 설계 (동일 dataset/sel/sample_size 조건)
  · 측정 코드 design (`run_adaptive_sampling.py` 골격)
  · WebFetch 활용 가능 (arXiv:2512.09695v2)
- 시간: ~10-15분
- → Step 2 의 Agent B (코드 finalize) 의 input 으로 활용

### Step 1 — Deep Review Agent 결과 검토 (메인 세션, ~10분)

1. `/Users/hyunbin/Capstone/_internal/RQ3_paradigm_심층검증_20260508.md` 읽기
2. 사용자에게 핵심 변경 사항 보고 (paradigm naming / method 추가-제외 / ★4 권장)
3. 사용자 confirm

### Step 2 — RQ3 확정 후 백그라운드 4 에이전트 동시 launch

| Agent | Task | 시간 | 산출 |
|---|---|---|---|
| **A** | 자문 메일 v3 update (5 paradigm × N method 정정) + 박세은 카톡 reframe message | 5분 | `submission/_drafts/속도는벡터_연구지도확인서_20260508_v3.md` |
| **B** | Adaptive Sampling 본 논문 method 분석 + 측정 코드 작성 | 10분 | `experiments/code/rq3/run_adaptive_sampling.py` + 서버 launch script |
| **C** | Multi 광범위 wrapper 확장 (`measure_multi_4kang.py` → `measure_multi_paradigm.py`, N method 기준) | 10분 | `_internal/scripts/measure_multi_paradigm.py` |
| **D** | 발표 slide redesign 안 (5 paradigm × representative + Top 4 + Pruned narrative) | 10분 | `_internal/slide_redesign_v2_20260508.md` |

### Step 3 — 메인 세션 통합 + 사용자 결정

1. 4 에이전트 결과 검토
2. 박세은 카톡 update 메시지 finalize + 사용자 직접 발송
3. 자문 메일 v3 finalize + PDF 변환 (`python3 _internal/scripts/md2pdf.py`)
4. 서버 ssh + Adaptive Sampling launch (overnight, ~5h)

### Step 4 — 5/9 (토) 결과 분석

1. Adaptive baseline 결과 도착 → 분석 + master_v6 §10.7 update
2. Multi 광범위 launch (overnight, ~10h)
3. (선택) 누락 3종 단일 추가 launch (Mean-Shift / R-tree / MinHash, ~7h)
4. Phase 0d 서버 코드 검증 (halton/hammersley/reservoir/sf_importance, ~5분)

### Step 5 — 5/10~5/11 (일~월) 자문 메일 발송

1. Multi 광범위 결과 분석 + master_v6 §10.6 update
2. 박세은 검토 후 자문 메일 v3 finalize
3. 5/11 또는 5/12 자문 메일 발송 (채림 + 교수님)

### Step 6 — 5/15 자문 회신 후 (W2 끝)

1. 자문 합의 결과 반영
2. 5/27 발표 slide v2 finalize
3. 5/22 교수님 미팅 준비

---

## 6. 핵심 결정 항목 (사용자 confirm 필요, 다음 세션 시작 시)

```
[1] Deep Review Agent 결과 paradigm naming / method 변경 권장
  □ Yes, 변경 적용
  □ No, 현재 11 method 안 유지

[2] ★4 final
  □ sparse RP (현재 후보, 권장)
  □ PCA1D (alternative, 학술 well-known higher)
  □ 다른 method (Deep Review 권장 따라)

[3] 누락 critical 추가 측정?
  □ 추가 X — limitation 명시로 충분 (시간 절약)
  □ Mean-Shift 1종만 추가 (~3h)
  □ 3종 모두 추가 (~7h)

[4] 자문 메일 v3 박세은 재공유
  □ Yes, paradigm naming 정정 카톡 update
  □ No, 현재 v2 narrative 그대로 (박세은 검토 진행 중)
```

---

## 7. 서버 launch plan (RQ3 확정 후)

서버: `165.132.140.240` (capstone2026), 작업 디렉토리 `/mnt/hdd0/home/capstone2026`

### 5/8 (오늘 밤) 22:00 ~ 5/9 03:00 — Adaptive Sampling baseline (~5h)

```bash
ssh capstone2026
cd /mnt/hdd0/home/capstone2026
nohup python3 -u cache/rq3/run_adaptive_sampling.py \
  --datasets DEEP SIFT SSN WIKI YFCC \
  --sf 1 10 \
  --selectivity 0.01 0.05 0.10 0.30 0.50 \
  > logs/adaptive_baseline_20260508.log 2>&1 &
```

→ 단일 10 cell × Adaptive Sampling × 5 sel × 5 seed × 100 query = 2500 measurement

### 5/9 (토) 03:00 ~ 13:00 — Multi 광범위 (~10h)

```bash
nohup python3 -u _internal/scripts/measure_multi_paradigm.py \
  --cells partsupp_deep_sift_10 partsupp_deep_wiki_10 multi_join_deep_wiki \
  --methods HDBSCAN MiniBatch GMM Hilbert faiss_ivf MB_partial Reservoir sparse_rp PCA1D LSH Sobol \
  > logs/multi_paradigm_20260509.log 2>&1 &
```

→ 3 multi cell × 11 method × 5 sel × 5 seed × 100 query = ~8250 measurement

### (선택) 5/10 (일) — 누락 3종 단일 추가 (~7h)

Mean-Shift / R-tree / MinHash·SimHash 측정 코드 작성 + launch

### (deferred) SF100 (80M) — 자문 합의 후

채림 정본 sf100 합의 + 단일 cell 12h+ 소요 → 5/15 자문 회신 후 결정

---

## 8. 메인 세션 vs 백그라운드 에이전트 활용 원칙 (다음 세션부터 적용)

**메인 세션 (사용자 대화)**:
- 사용자 결정 항목 처리
- 에이전트 결과 검토 + 통합
- commit / push / 박세은 카톡 update
- 핵심 narrative 결정

**백그라운드 에이전트 (병렬 적극 활용)**:
- Deep Review / 학술 검증
- 코드 작성 (Adaptive baseline / Multi wrapper)
- 측정 결과 분석
- 발표 slide redesign / 자문 메일 update
- 박세은 카톡 message draft

→ **사용자 주간 한도 17% 남음 (4시간) → 토큰 절약 + 작업 효율 max**

---

## 9. 산출물 위치 reference

### 분석 본체
- `experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.{md,pdf}` (5/8 14:13 finalize, 30 method × 10 cell × RQ1/2/3)
- `experiments/results/10cell_narrative_종합_20260508.{md,pdf}`

### 자료 / 문서
- `submission/_drafts/속도는벡터_연구지도확인서_20260508.md` (지도확인서 v2, 110 lines)
- `submission/_drafts/속도는벡터 — Academic v3 · Final 5_27.pdf` (발표 deck, 16 page)
- `_internal/records/kakaotalk/20260508_19시_RQ123sprint_회의.md` (회의록)
- `_internal/handoff_v11_session_20260508_PostMeeting.md` (이전 handoff)
- `_internal/handoff_v12_session_20260508_2030_RQ3확정대기.md` (본 handoff)

### 진행 중 (다음 세션 시 검토)
- `_internal/RQ3_paradigm_심층검증_20260508.md` (Deep Review Agent 산출, ~21:00 ETA)

### 코드 (5 paradigm 11 method)
- `experiments/code/rq3/run_{hilbert,minibatch_partial,hdbscan,minibatch,gmm,kdtree,pca1d,zorder,kde,lsh,sparse_rp,sobol}.py`
- `_internal/scripts/run_{faiss_ivf,coresets,agglomerative,dbscan,optics,kmeans_pp,hierarchical_kmeans,pca_kmeans}.py`
- `experiments/code/rq3/_measure_common.py` (공통 backend)
- `_internal/scripts/measure_multi_4kang.py` (multi 4강 wrapper, 11 method 확장 필요)

---

## 10. Critical 운영 원칙 (handoff_v11 §6 + 본 세션 추가)

| # | 원칙 |
|---|---|
| 1 | PG 백엔드 종료 시 `pg_terminate_backend(pid)` (SIGKILL 금지) |
| 2 | HDD 1개 → 동시 작업 ≤ 2 (IO 경합) |
| 3 | chain_unified.py 의 NPY-first patch 환경 (F2 patch) |
| 4 | analyze_10cell_w4.py 사용 |
| 5 | master_v6 의 §10.5 (Sweet Spot) + §10.6 (Multi/Exqutor + PDX) = 회의 narrative 핵심 |
| 6 | 4강 method × paired Δ% 표 절대 변경 금지 |
| 7 | 내부 용어 (Wave / W4 / MB_p / chain_unified / sprint) 외부 노출 금지 |
| 8 | 채림 정본 (partsupp_yfcc_{1,10}) DROP 절대 X |
| 9 | **(5/8 회의 추가)** Adaptive Sampling 본 논문 비교 = 최우선, multi 적용 |
| 10 | **(5/8 회의 추가)** SF1·SF10 한정, SF100 deferred |
| 11 | **(본 세션 추가)** RQ3 paradigm 확정 = 발표/보고 narrative 핵심, 5 paradigm × N method 명확 매핑 |
| 12 | **(본 세션 추가)** 메인 세션 = 대화 + 결정, 백그라운드 = 에이전트 적극 활용 (token 절약) |

---

> **작성**: Claude Opus 4.7 1M (5/8 20:36 KST PM)
> **이전**: handoff_v11_session_20260508_PostMeeting.md (회의 후 finalize)
> **다음**: handoff_v13 (RQ3 paradigm + 11 method 확정 + Adaptive baseline launch 후)
