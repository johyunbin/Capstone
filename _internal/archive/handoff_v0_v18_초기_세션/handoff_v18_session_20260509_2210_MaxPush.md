# Handoff v18 — Max Push 모드 (5/9 22:11 KST, Saturday)

> 새 세션 진입용 comprehensive handoff. v17 (5/9 16:12) 이후 6시간 간 결정·구현·실행 history 전부 담음.
> Context 61% 도달 → 새 세션으로 인계, 동일 storyline·동일 자원 plan 으로 즉시 이어가기 가능하도록 작성.

---

## 0. ⚠️ 5/9 22:24 SCOPE EXPANSION (반드시 우선 적용)

**사용자 결정 (5/9 22:24 KST)**: SF=1 + SF=10 가용 single + multi 데이터셋의 **모든 가능한 조합 cell 무조건 다 측정** (Exqutor 표준 외 image×image, YFCC_PCA, WIKI×WIKI 등 포함). SF=100 은 그 이후 가용 자원 보고 결정.

### 0.1 서버 가용 NPY (확인됨)

partsupp emb: **DEEP / SIFT / FB / YFCC / YFCC_PCA / WIKI** × {sf1, sf10} = 12 NPY
part emb: **WIKI** × {sf1, sf10} = 2 NPY

### 0.2 모든 가능 multi cell (42 cells = 30 partsupp 4-way + 12 multi-table join)

**partsupp 4-way (15 pairs × 2 SF = 30 cells)**:
DEEP+SIFT, DEEP+FB, DEEP+YFCC, DEEP+YFCC_PCA, **DEEP+WIKI** ✓ , SIFT+FB, SIFT+YFCC, SIFT+YFCC_PCA, **SIFT+WIKI** ✓ , FB+YFCC, FB+YFCC_PCA, **FB+WIKI** ✓ , YFCC+YFCC_PCA, **YFCC+WIKI** ✓ , YFCC_PCA+WIKI

**multi-table join partsupp(X) ⋈ part(WIKI) (6 X embs × 2 SF = 12 cells)**:
**DEEP** ✓ , **SIFT** ✓ , **FB** ✓ , **YFCC** ✓ , YFCC_PCA, WIKI

→ 현재 covered = 16 cells (★표시), **추가 build + measure 필요 = 26 multi cells** (+ 2 YFCC_PCA single)

### 0.3 모든 가능 single (14 cells)

DEEP / SIFT / SSN / WIKI / YFCC / FB × {sf1, sf10} = 12 (covered/in-progress) + **YFCC_PCA × {sf1, sf10} = 2** (NEW, NPY 존재)

### 0.4 Realistic ETA (full scope)

| 시점 | 작업 |
|---|---|
| 5/10 새벽 ~ 정오 | 현재 16 multi + 12 single + sf=10 빌드 측정 마무리 |
| 5/10 오전 ~ 오후 | 추가 26 multi cells build (parallel 4-6 way) |
| 5/10 오후 ~ 5/11 새벽 | 추가 26 multi × 22 methods 측정 (max parallel) |
| **5/11 새벽 ~ 오전** | **full scope finalize + Phase G analysis + REPORT.md** |
| 5/11 오후 이후 | SF=100 사용자 결정 trigger |

→ 사용자 의향 "내일 새벽 다 마무리" 는 현재 16 cell scope 기준. **full scope 28 추가 cells 는 5/11 새벽-오전 realistic finalize**.

### 0.5 새 세션 첫 작업 (즉시 실행)

1. 현재 19+ active processes 진행 상태 확인 (`pgrep -af 'python3.*(measure_multi|build_new|build_FB|measure_phase_f|run_ensemble)' | wc -l`)
2. Phase C sf=10 finalize 시 Phase E NEW sf=10 watchers 자동 launch 검증
3. **추가 28 cells (26 multi + 2 single) build script launch**:
   - measure_multi_paradigm.py 의 CELL_4WAY/CELL_JOIN 에 22 추가 cell config 등록 (agent dispatch)
   - build_new_multi_cells.py 호출로 NPY artifact 생성 (sequential or 4-way parallel)
   - 그 후 measure_multi_paradigm.py + measure_multi_ensemble.py 로 22 methods 측정
4. 모든 측정 완료 후 Phase G analysis 실행 (`analyze_phase_g.py`)
5. 5/11 새벽-오전 finalize 후 사용자에게 SF=100 trigger 보고

### 0.6 신규 cell 명명 규약 (확장)

기존: `partsupp_<image_X>_wiki_<sf>` (image+text), `multi_join_<image_X>_wiki_<sf>` (image⋈text)

추가:
- `partsupp_<emb_A>_<emb_B>_<sf>` (e.g., `partsupp_deep_sift_1`, `partsupp_yfcc_pca_wiki_10`)
- `multi_join_<emb_X>_<sf>` (e.g., `multi_join_yfcc_pca_1`, `multi_join_wiki_1`)

CELL_4WAY/CELL_JOIN dict 에 동일 schema (kind=4way/join, prebuilt=True, emb1_npy/emb2_npy/partkeys/strata/query_pool/query_sel/true_card paths) 로 등록.

### 0.7 ★ 추가 method 발굴 directive (5/9 22:28 사용자 결정, 반드시 실행)

**사용자 22:28 KST 결정**: 현재 22 method (11 existing + 11 new) **portfolio 최종 X**. 시간 여유 있을 때 **single+multi 모두 강한 추가 method 발굴 필수**. 새 세션 진입 즉시 다음 task:

#### Step 1 — Comprehensive online research agents 병렬 dispatch

기존 4 agent (Agent 1 vector DB lit / Agent 2 high-d sampling / Agent 3 데이터 분석 / Agent 4 critical review) 외에 **추가 5-6 agent** 병렬 dispatch:

1. **2024-2026 최신 SOTA 리서치**: arXiv / VLDB / SIGMOD / NeurIPS 2024-2026 의 cardinality estimation / vector DB / multi-table sampling 최신 연구
2. **Learned methods 확장**: DeepDB (Hilprecht VLDB 2020), MSCN (Kipf CIDR 2019), VAE cardinality (Hasan SIGMOD 2020), Naru variants, GNN-based join cardinality
3. **Sketch-based 확장**: Theta sketch (Dasgupta 2016), KMV, Bloom join sketch, Coupled count sketch
4. **Multi-relation native 확장**: Wander Join 변형 (XDB), Ripple Join, Index-Based Join Sampling (Leis CIDR 2017), AGM-bound 활용 acyclic join sampling
5. **RL/bandit 확장**: Reinforcement learning sampling, contextual bandit on stratified, Thompson sampling
6. **Tensor / matrix decomp 확장**: Tucker, CP, Non-negative MF, Spectral co-tensor, Random projection in high-d (FastJL, count sketch RP)
7. **신규 paradigm**: Graph-based ANN (HNSW within-cell), differentially-private sampling, online active learning sampling

#### Step 2 — Brainstorming agent dispatch

`superpowers:brainstorming` skill 또는 `general-purpose` agent 로 RQ3 paradigm 차원에서 **누락된 inductive bias** 발굴:

- High-dim 적응 (curse of dim 회피): 어떤 다른 mechanism?
- Multi-relation 적응: join structure 활용 외 다른 방법?
- Adaptive sample budget: Adaptive Sampling 외 다른 dynamic strategy?
- Joint distribution learning: CCA / co-clustering 외 다른 joint 표현?
- Theoretical guarantee: Coreset 외 다른 (1+ε) approximation?

#### Step 3 — 결과 종합 + portfolio 확장

- 발굴된 신규 candidates 5-10 개 추가 → 22 method → ~30+ method portfolio
- 각 candidate 에 대해 paradigm 분류, theoretical fit, multi-relation evidence 평가
- 신규 method 구현 (agent 다중 dispatch) → server sync → 측정 launch

#### Step 4 — 측정 매트릭스 확장

- 22 → 30+ methods × 56 cells = ~1,700 measurement combinations
- 시간 ~50% 추가 예상 (5/11 오후 ~ 5/12 새벽 finalize)
- 디스크 / 메모리 모니터링 지속

#### Step 5 — Phase G 분석에 신규 method 통합

- analyze_phase_g.py 의 G2 (Adaptive gap) / G3 (B4 vs B1) / G7 (production top) 에 신규 methods 포함
- Tier S/A/B/C 외 새 Tier 정의 가능 (Tier S+ for SOTA, Tier R for RL-based 등)

#### 핵심 원칙

- **모든 method 무조건 다 측정** (사용자 22:11 directive 그대로)
- **Tier S/A 적합 method 더 발굴** (사용자 22:28 directive)
- single+multi 모두 강한 method 의 학술 evidence 우선
- 6/11 보고서까지 method 발굴/통합/검증 완료

---

## 1. 현재 시점 (5/9 22:11 KST, Saturday)

### 1.1 모드 — Max Push

서버 자원 max push 모드. **19+ 동시 process** 병렬 실행 중. 사용자 directive (5/9 22:00 KST):

> "다른 사용자 영향 X 안에서 극한 활용, SF=1+10 측정 빨리 마무리 → 5/10 정오 전후 finalize → SF=100 사용자 결정"

### 1.2 인계 사유

- Context 61% 도달 (이번 메인 세션)
- 19+ active process 가 새벽까지 자율 진행 (메인 세션 종료해도 continue)
- 5/10 정오 시점 사용자 SF=100 결정 trigger 시 새 세션 가동 필요

### 1.3 직전 commit

```
9fe1ca2 handoff_v17 — 5/9 16:12 Multi Ensemble running + agent 활용 plan 명시
c895817 자문 메일 v5 deep-review 적용 — code-reviewer agent 8건 필수 수정 반영
ff3ce43 자문 메일 v5 minimal 재작성 — 박세은 카톡 톤 100% 일치
```

---

## 2. 핵심 storyline (사용자 6:27 KST framing 그대로)

### 2.1 7-stage narrative

```
① RQ1+RQ2 single 분포 인지 stratified 효과 입증
   — Δ% −8% 절대 우위 (random sampling 대비)
   — HDBSCAN 10/10 sig (Tier-S, q_error 동등 + sample size −18%)
   — 결론: 분포 정보 + stratified 가 single 에서 valid

② RQ3 single paradigm 우위
   — 5 paradigm × 11 method 전수 비교
   — Tier-S = HDBSCAN, MiniBatch, Hilbert (paired-better ≥ 8/10)
   — 결론: paradigm 별로 강점 영역 분리 가능

③ Multi naive 적용 → 0/66 paired-better
   — 4way (partsupp ⋈ 4×WIKI) + multi-join (partsupp(X) ⋈ part(WIKI)) 6 cells
   — 11 method 중 random adaptive 보다 더 나은 paired-better 가 0건
   — Fail 아님 — q_error 둘 다 비슷, sample size 도 cross-method 평균 유사
   — 결론: single 에서의 가설이 multi 로 naive transfer 불가

④ Failure mode 학술 진단
   — Curse of dimensionality: Geraci 2026 reference 인용, β₁=+0.0079 p=6.8e-85
   — Cochran 1977 §5.5 stratification efficiency 조건 위배
   — Bengtsson 2008 Effective Sample Size: 0.875 (single) → 0.770 (multi)
   — 결론: high-d join 공간에서 stratification 의 variance reduction 이 sublinear

⑤ 신규 11 method 발굴 (Tier S/A/B/C)
   — 기존 11 method 한계 가설 → 4가지 학술 가설 → 11 새 방법 도출
   — Tier S: WanderJoin (Li SIGMOD 2016), AMSCountSketch (Alon STOC 1999),
     NeuroCard (Yang VLDB 2020)
   — Tier A: PQ (Jégou 2011), Coreset (Bachem 2017), DenseRP (Bingham 2001),
     BanditUCB1 (Carpentier 2011), NeurAM (Geraci 2026)
   — Tier B: CCA1D (Hotelling 1936), CoCluster_Nystrom (Dhillon 2003)
   — Tier C: ConditionalAdaptive (Exqutor variant, single-only)
   — 결론: 22 method 전체 측정 → multi paired-better recover 가능성 평가

⑥ Adaptive vs Adaptive+ensemble 직접 비교
   — Phase F 6 baselines (B1: vanilla Adaptive, B2: B1+stratify, B3: B1+ensemble,
     B4: B2+ensemble, B5: B1+stratify+importance, B6: B5+ensemble)
   — 4 axis 비교: q_error, sample size, dropped fraction, time
   — 결론: ensemble 더해서 얻는 marginal recovery 정량화

⑦ Production-ready package — 박광현 BDAI 후속 연구로 인계
   — Best 방법 + 코드 + dataset + benchmark 가 묶여 후속 연구실 자산
   — 5/27 발표 + 6/11 보고서 deadline 충족
```

### 2.2 Thesis (사용자 18:35 sharpen)

> "Distribution-aware stratification 을 sampling augment 로 사용하면, single/multi 모두에서 q_error 동등 이상 + sample size convergence 빠름 → resource saving + Exqutor multi-table limitation 보완"

핵심 주장 = **q_error 동등 이상** (paired-better wins) + **sample size convergence faster** (resource saving). multi-table 에서는 Adaptive+ensemble 이 baseline 에 가까운 성능에 도달하는 데 걸리는 sample 수가 적다는 게 valuable.

---

## 3. v7 design portfolio

### 3.1 22 methods (11 existing + 11 new)

#### 기존 11 method (5 paradigm)

| Paradigm | Method | Reference |
|---|---|---|
| **P1 Cluster** | HDBSCAN | Campello et al. 2013 |
|  | MiniBatch (KMeans) | Sculley 2010 |
|  | GMM | Reynolds 1995 |
| **P2 Spatial** | Hilbert | Faloutsos 1989 |
|  | faiss_ivf | Johnson FAISS 2017 |
| **P3 Streaming** | MB_partial | partial fit MiniBatch |
|  | Reservoir | Vitter 1985 |
| **P4 DimReduction** | sparse_rp | Achlioptas 2003 (Li 2006 1/√D variant) |
|  | PCA1D | Pearson 1901 |
| **P5 QuasiRandom** | LSH | Indyk-Motwani 1998 (K=20) |
|  | Sobol | Sobol 1967 |

#### 신규 11 method (Tier S/A/B/C)

| Tier | Method | Reference | Cost | GPU |
|---|---|---|---|---|
| **S** | WanderJoin | Li SIGMOD 2016 | high | CPU |
|  | AMSCountSketch | Alon STOC 1999 | mid | CPU |
|  | NeuroCard | Yang VLDB 2020 | very high | **GPU auto-detect** |
| **A** | PQ | Jégou 2011 | mid | CPU |
|  | Coreset | Bachem 2017 | high | CPU |
|  | DenseRP | Bingham 2001 | mid | CPU |
|  | BanditUCB1 | Carpentier 2011 | low | CPU |
|  | NeurAM | Geraci 2026 | very high | **GPU auto-detect** |
| **B** | CCA1D | Hotelling 1936 | mid | CPU |
|  | CoCluster_Nystrom | Dhillon 2003 | high | CPU |
| **C** | ConditionalAdaptive | Exqutor variant | low | CPU (single only) |

총 **22 method** × **28 cells** = 616 measurement combinations.

### 3.2 28 cells

#### Single (12 cells)

DEEP / SIFT / SSN / WIKI / YFCC / FB × {sf=1, sf=10}

```
DEEP_sf1, DEEP_sf10
SIFT_sf1, SIFT_sf10
SSN_sf1, SSN_sf10
WIKI_sf1, WIKI_sf10
YFCC_sf1, YFCC_sf10
FB_sf1, FB_sf10
```

#### Multi 4way partsupp ⋈ WIKI (8 cells)

```
partsupp_<image_X>_wiki_<sf>:
  X ∈ {DEEP, SIFT, FB, YFCC} × sf ∈ {1, 10}
```

= partsupp(image_DEEP) ⋈ wiki, partsupp(image_SIFT) ⋈ wiki, etc.

#### Multi-table join partsupp(X) ⋈ part(WIKI) (8 cells)

```
multi_join_<X>_wiki_<sf>:
  X ∈ {DEEP, SIFT, FB, YFCC} × sf ∈ {1, 10}
```

기존 partsupp_deep_sift 는 v7 에서 drop 됨 (5/9 21:50 agent fix). cell prefix 가 `<DATASET>_sf<N>` (single) vs `partsupp_<X>_wiki_<N>` / `multi_join_<X>_wiki_<N>` (multi) 로 분리됨 — 새 세션 주의 필요.

---

## 4. 핵심 산출물 위치

### 4.1 Design / 분석 doc

| File | 내용 | Line |
|---|---|---|
| `plans/RQ재정립_v7_evidence_20260509_1820.md` | v7 design (storyline + 22 method + 28 cell) | 557 |
| `_internal/cache/failure_mode_analysis/REPORT.md` | Phase B 결과 (multi naive 0/66 진단) | ~600 |

### 4.2 신규 11 method 구현

`_internal/scripts/methods/` (~3,800 lines, 11 file):

```
methods/wanderjoin.py          (Tier S, Li SIGMOD 2016)
methods/ams_countsketch.py     (Tier S, Alon STOC 1999)
methods/neurocard.py           (Tier S, Yang VLDB 2020, GPU auto-detect)
methods/pq.py                  (Tier A, Jégou 2011)
methods/coreset.py             (Tier A, Bachem 2017)
methods/dense_rp.py            (Tier A, Bingham 2001)
methods/bandit_ucb1.py         (Tier A, Carpentier 2011)
methods/neuram.py              (Tier A, Geraci 2026, GPU auto-detect)
methods/cca1d.py               (Tier B, Hotelling 1936)
methods/cocluster_nystrom.py   (Tier B, Dhillon 2003)
methods/conditional_adaptive.py (Tier C, Exqutor variant)
```

### 4.3 측정 / 분석 script

| File | 내용 | Line |
|---|---|---|
| `_internal/scripts/analyze_failure_modes.py` | Phase B failure mode analysis | 749 |
| `_internal/scripts/build_new_multi_cells.py` | Phase C neue multi cell build (sf=1, sf=10) | 680 |
| `_internal/scripts/build_FB_single_ensemble.py` | FB single ensemble build | 389 |
| `_internal/scripts/measure_multi_paradigm.py` | Paradigm baseline 측정 (CELL_4WAY/CELL_JOIN 18 cells, NEW method dispatch) | ~1,400 |
| `_internal/scripts/measure_multi_ensemble.py` | (1) ensemble 측정 (동일 update) | ~1,300 |
| `_internal/scripts/measure_phase_f_baselines.py` | Phase F 6 baselines | 1,557 |
| `_internal/scripts/analyze_phase_g.py` | Phase G analysis (7 sections + REPORT) | 1,732 |

### 4.4 자문 메일 v5

```
submission/_drafts/속도는벡터_자문메일_박성원멘토_20260509_v5.pdf
submission/_drafts/속도는벡터_자문메일_박성원멘토_20260509_v5.md
```

5/9 deep-review 적용 (code-reviewer agent 8건 필수 수정 반영) + 박세은 카톡 톤 100% 일치 (장황함 제거).

### 4.5 v7 storyline § 3 sharpened (5/9 18:35)

`plans/RQ재정립_v7_evidence_20260509_1820.md` § 3 = 사용자 framing 1:1 반영. 7-stage narrative 의 ④ failure mode 학술 진단 부분이 가장 핵심 — Geraci 2026 / Cochran 1977 / Bengtsson 2008 정확한 인용 + numeric.

---

## 5. 사용자 결정 history (반드시 기억)

### 5.1 5/9 17:50 ~ 22:11 사이 결정

| 시각 (KST) | 결정 |
|---|---|
| 17:50 | "기존 top method only 폐기" → 22 methods 전체 측정 필요 |
| 17:55 | "SF=100 제외 결정" (1차) — 디스크/시간 제약 인지 |
| 18:00 | "최대 토큰 / 최대 시간 / 최고 성능" — 자율 결정 권한 위임 |
| 18:10 | "타임라인 신경 X" — 5/27 발표 무관, 최선 결과 우선 |
| 18:35 | v7 storyline § 3 sharpen (Thesis 문장 확정) |
| 19:30 | "GPU 사용 가능" — 다른 사용자 영향 X 시 |
| 20:48 | 채림 rules 강조 (포트 55435/55436, GPU 양보, sudo X) |
| 21:00 | "메인 세션 보호 위해 agent 적극 활용" |
| 22:00 | "현재 측정 끝나면 가용 자원 보고 SF=100 결정" (재오픈) |
| 22:05 | "다른 사용자 영향 X 안에서 극한 활용, 5/10 정오 finalize" |

### 5.2 사용자 = 팀 가장 형 (조현빈)

`memory/project_team_hierarchy.md` 참조. 카톡 톤 = peer-to-peer (격식 X, 권위 X).

### 5.3 Deadline

- **5/27 발표** — 최종 발표
- **6/11 보고서** — 최종 보고서

둘 다 fit 가능. 5/10 정오 finalize 기준이면 5/13 분석 완료, 5/15 draft, 5/20 review, 5/25 final.

---

## 6. 채림 rules (5/9 20:48 사용자 강조, 반드시 준수)

`memory/reference_server.md` 참조. 

### 6.1 Port

```
55432, 55433  — chaerim 의 PostgreSQL 인스턴스 (절대 X)
55435, 55436  — 우리 PostgreSQL 인스턴스 (이것만)
```

### 6.2 GPU

- 사용 자제 (4 GPU 다른 사용자 공유 자원)
- **idle 시 OK** (지금 다른 사용자 0%) 
- 다른 사용자 등장 시 **즉시 release**
- 모니터링: `nvidia-smi` 주기적 (현재 GPU 0/2/3 정상, GPU 1 ERR)

### 6.3 sudo

- 사용 권한 X
- 모든 작업 user-level 만 (Python venv, conda 등)

### 6.4 Disk

- HDD 86% used (1.8T 여유)
- 디스크 사용량 모니터링 필수
- SF=100 시점 1 cell ~276GB NPY → 6 cells = 1.66TB (거의 전부)

### 6.5 Process

- tmux 권장 (또는 nohup OK)
- 메인 세션 종료 후에도 계속 실행

---

## 7. 서버 자원 상태 (5/9 22:11)

### 7.1 인프라

```
Host       : capstone2026@165.132.140.240
WorkDir    : /mnt/hdd0/home/capstone2026
CPU        : 128 cores (load avg 80, ~65% 활용)
RAM        : 1 TB (530 GB 사용, 470 GB 여유)
GPU        : 4× RTX 6000 Ada (49 GB each)
             — GPU 1 ERR
             — GPU 0/2/3 정상
             — CUDA_VISIBLE_DEVICES=0,2,3 으로 회피
PyTorch    : 2.5.1+cu121 (NeurAM/NeuroCard GPU auto-detect 활성)
HDD        : 86% used, 1.8T 여유
```

### 7.2 다른 사용자

```
chaerim    : 0.2% CPU only (idle)
sihyunkim2 : idle
```

→ 우리가 사실상 독점 중. Max push 가능 상태.

### 7.3 CUDA driver

- driver 12.6 → torch cu121 OK
- cu130 부적합 (driver 와 mismatch)

---

## 8. 19+ active processes (5/9 22:11)

### 8.1 Foreground (메인 launch)

| PID | 작업 | 상태 |
|---|---|---|
| **339513** | (1) Multi Ensemble: Cell 3 multi_join_deep_wiki GMM 진행 | HDBSCAN/MiniBatch 끝, **8 method 남음**, ~22:30 finalize 예상. Cells 4–6 (sf=1) 자동 진행 후 종료 |
| 451582 | partsupp_deep_wiki_10 × 10 NEW methods (paradigm) sf=10 | running |
| 515931 | **Launch A**: 6 NEW sf=1 cells × 21 methods (paradigm) | running |
| 592612 | **Launch B v4**: 3 existing sf=1 cells × 8 methods | running |
| 776609 | partsupp_deep_sift_10 × 10 NEW methods (paradigm) | running |
| 776610 | multi_join_deep_wiki × 10 NEW methods (paradigm) | running |
| 807789 | 3 existing sf=1 cells × NeurAM+NeuroCard (CPU mode) | running |

### 8.2 Phase C build (sf=10 prebuilt NPY)

| PID | 작업 |
|---|---|
| 775832 | Cell 1 sf=10 build |
| 775833 | Cell 2 sf=10 build |
| 775834 | Cell 3 sf=10 build |
| 775835 | Cell 4 sf=10 build |
| 775836 | Cell 5 sf=10 build |
| 775837 | Cell 6 sf=10 build |
| 775838 | (auxiliary build) |
| 775839 | (auxiliary build) |

→ ~22:30 첫 cell 완료 예상.

### 8.3 FB single ensemble

| PID | 작업 |
|---|---|
| 807778 | FB single sf=1 ensemble (sequential 11 methods) |
| 823039 | FB single sf=10 ensemble (sequential 11 methods) |

> 주의: underlying script = `run_ensemble_4kang_adaptive.py`. SSN 으로 저장된 후 FB renaming 됨.

### 8.4 Phase F baselines

| PID | 작업 |
|---|---|
| 823306 | Phase F B1+B2 × 8 sf=1 multi cells |
| 837103 | Phase F B1+B2 × 12 single (대부분 SKIP, FB ERROR) |
| 837109 | Phase F B1+B2 × 2 sf=10 existing multi |
| 878254 | Phase F B3+B6 × 10 multi cells |
| 1606191 | Phase F B5+B1 × 8 sf=1 multi cells |

### 8.5 Phase E watchers (Phase C 완료 시 자동 launch trigger)

```
PIDs 1605534, 1605536, 1605537, 1605538, 1605540, 1605541
```

→ 6 watchers, Phase C sf=10 cell 완료 감지 → CUDA_VISIBLE_DEVICES=0,2,3 환경에서 자동으로 Phase E NEW sf=10 launch.

---

## 9. 주요 file path (sync 필수)

### 9.1 서버 측 (`/mnt/hdd0/home/capstone2026/cache/rq3/`)

```
methods/                       — 11 new method files (~3,800 lines)
measure_multi_paradigm.py      — CELL_4WAY/CELL_JOIN 18 cells, NEW method dispatch
measure_multi_ensemble.py      — 동일 update (앙상블 (1))
measure_phase_f_baselines.py   — 6 baselines
                                 cell prefix: `<DATASET>_sf<N>` (single) /
                                              `partsupp_<X>_wiki_<N>` (multi 4way) /
                                              `multi_join_<X>_wiki_<N>` (multi-join)
analyze_phase_g.py             — 7 sections + REPORT
analyze_failure_modes.py       — Phase B
build_new_multi_cells.py       — Phase C
build_FB_single_ensemble.py    — FB single ensemble
```

### 9.2 로컬 측 (`_internal/scripts/`)

위 모든 file 의 source. server 와 sync 됨.

### 9.3 측정 결과

```
서버 /mnt/hdd0/home/capstone2026/cache/rq3/multi_paradigm_*/<cell>.csv
   — paradigm baseline measurement

서버 /mnt/hdd0/home/capstone2026/cache/rq3/multi_ensemble/<cell>.csv
   — (1) ensemble measurement

서버 /mnt/hdd0/home/capstone2026/cache/rq3/phase_f/phase_f_<cell>.csv
   — Phase F 6 baselines

서버 /mnt/hdd0/home/capstone2026/cache/rq1/rq3_FB_sf<N>_ensemble_<method>.parquet
   — FB single ensemble per-method
```

### 9.4 분석 결과

```
서버 /mnt/hdd0/home/capstone2026/cache/rq3/failure_mode_analysis/REPORT.md
   — Phase B 진단

서버 /mnt/hdd0/home/capstone2026/cache/rq3/phase_g_analysis/REPORT.md
   — Phase G 종합 (TBD ~5/10 09:00)
```

---

## 10. ETA + 다음 monitoring schedule

### 10.1 Timeline

| 시점 | 예상 진행 |
|---|---|
| **5/9 22:30** | (1) Cell 3 finalize (GMM 종료) + Phase C sf=10 첫 cell 완료 + Phase E NEW sf=10 자동 launch |
| **5/9 23:00** | Phase C 6 cells 모두 완료 + 6 Phase E NEW sf=10 모두 launch (메모리 ~890 GB peak) |
| **5/10 02:00** | sf=1 측정 모두 완료 + sf=10 절반 진행 |
| **5/10 06:00 ~ 09:00** | sf=10 측정 모두 완료 |
| **5/10 09:00 ~ 12:00** | Phase F 완료 + Phase G analysis + REPORT.md draft |
| **5/10 정오 ~ 오후** | **전체 finalize → 사용자에게 SF=100 결정 trigger** |

### 10.2 새 세션 첫 monitoring

22:30 KST — (1) Cell 3 finalize + Phase C 첫 cell 완료 + Phase E NEW sf=10 자동 launch.

---

## 11. 다음 세션 진입 prompt (복사 사용)

```
@_internal/handoff_v18_session_20260509_2210_MaxPush.md 읽고 이어서 진행.

5/9 22:11 시점 (max push 모드):
- 19+ active processes 진행 중
- v7 design 22 methods × 28 cells 측정 진행 중
- (1) Cell 3 GMM, Phase C sf=10 building, Phase E NEW sf=10 watchers 대기
- ETA: 5/10 정오 finalize → SF=100 사용자 결정

채림 rules 준수 (GPU 0/2/3 사용 OK, port 55432/55433 X, sudo X).
다음 monitoring 22:30 (Cell 3 finalize + Phase C 첫 cell + Phase E NEW sf=10 자동 launch).
```

---

## 12. lesson + next-session 주의사항

### 12.1 Cell 명 prefix 차이 (5/9 21:50 agent fix)

```
single        : DEEP_sf1, SIFT_sf10, ...
multi 4way    : partsupp_deep_wiki_1, partsupp_sift_wiki_10, ...
multi-join    : multi_join_deep_wiki_1, multi_join_sift_wiki_10, ...
```

`measure_phase_f_baselines.py --cells <name>` 호출 시 prefix 정확히 맞춰야 함. 잘못된 prefix 사용 시 SKIP 또는 KeyError 발생.

### 12.2 partsupp_deep_sift 는 v7 에서 drop 됨

기존 multi cell 중 `partsupp_deep_sift_*` 는 v7 에서 제외. 새 multi 4way 는 partsupp(X) ⋈ WIKI 로 통일.

### 12.3 CSV 존재 시 SKIP 로직

`measure_multi_paradigm.py` / `measure_phase_f_baselines.py` 모두 동일 cell 의 CSV 존재 시 SKIP. 재측정 필요 시:
- `--out-dir` 분리 (다른 결과 디렉토리)
- 또는 `--no-skip-existing` flag (구현 확인 필요)

### 12.4 SSH 명령어 cd 누락 함정

원격에서 명령어 실행 시 cd 가 안 먹어서 경로가 ~/ 로 reset 됨. 항상 **절대 경로** 사용:

```bash
# ❌ 위험
ssh capstone2026 "cd /mnt/hdd0/.../rq3 && python measure_*.py ..."

# ✅ 안전
ssh capstone2026 "python /mnt/hdd0/home/capstone2026/cache/rq3/measure_*.py ..."
```

### 12.5 CUDA driver 12.6 + torch cu121 OK, cu130 부적합

NeurAM / NeuroCard GPU auto-detect 시 torch 2.5.1+cu121 만 사용. cu130 wheel 사용하지 말 것.

### 12.6 FB single 의 underlying script

```
파일명     : run_ensemble_4kang_adaptive.py
저장경로   : SSN 으로 저장된 후 FB renaming
```

→ measurement 결과 file 이 SSN 명으로 들어와도 패닉 X. rename 단계에서 FB 로 변경됨.

### 12.7 GPU 1 ERR 상태 — CUDA_VISIBLE_DEVICES=0,2,3

GPU 1 hardware error 상태. 모든 GPU 작업 시:

```bash
export CUDA_VISIBLE_DEVICES=0,2,3
```

자동 상속됨 (Phase E watchers 도 동일 환경). 새 GPU 작업 launch 시 명시 필수.

### 12.8 SF=100 디스크 + 메모리 한계

```
1 cell  ~  276 GB NPY (sf=100)
6 cells ~ 1,656 GB NPY
디스크    1,800 GB 여유
```

→ sf=100 6 cells 시 거의 디스크 만석. 사용자 결정 필요 (메모리도 peak 1+ TB 가능 — RAM 1TB 초과).

### 12.9 v7 storyline § 3 = thesis 문장 확정 (5/9 18:35)

> "Distribution-aware stratification 을 sampling augment 로 사용하면, single/multi 모두에서 q_error 동등 이상 + sample size convergence 빠름 → resource saving + Exqutor multi-table limitation 보완"

이 문장 그대로 사용. paraphrase X.

### 12.10 Storyline 7 stages (사용자 framing 100% 보존)

```
① RQ1+RQ2 single 분포 인지 stratified 효과 입증
② RQ3 single paradigm 우위
③ Multi naive 적용 → 0/66 paired-better
④ Failure mode 학술 진단
⑤ 신규 11 method 발굴 (Tier S/A/B/C)
⑥ Adaptive vs Adaptive+ensemble 직접 비교
⑦ Production-ready package — 박광현 BDAI 후속 연구로
```

각 stage 의 numeric (−8% Δ%, 10/10 sig, 0/66, ESS 0.875→0.770, β₁=+0.0079, p=6.8e-85) 정확히 인용.

### 12.11 사용자 = 가장 형 (peer-to-peer)

격식체 X, 권위 X. 카톡 톤 그대로. `memory/project_team_hierarchy.md` 참조.

### 12.12 Failure mode 학술 reference (정확히 인용)

```
Curse of dimensionality
  — Geraci (2026), β₁=+0.0079, p=6.8e-85

Stratification efficiency 조건
  — Cochran (1977) §5.5

Effective Sample Size
  — Bengtsson (2008): single 0.875 → multi 0.770
```

paraphrase X. 출처 정확히.

### 12.13 자문 메일 v5 deep-review 8건 수정 사항

5/9 deep-review (code-reviewer agent) 적용된 수정 8건 — `submission/_drafts/속도는벡터_자문메일_박성원멘토_20260509_v5.md` 그대로 사용. 추가 수정 없이.

### 12.14 메인 세션 보호 (agent 적극 활용)

20:48 사용자 directive — 메인 세션 보호 위해 agent (`Task` tool) 적극 활용. 새 세션도 동일 원칙. 긴 측정 launch / multi-step build 는 agent 위임.

### 12.15 Notion / Apple Notes / 카톡 일정 sync

3곳 동시 업데이트 룰 준수. 5/10 finalize 시:
- CLAUDE.md (`_internal/state/_current.md` 갱신)
- Notion 캡스톤 일정 DB
- 카톡 자문 채널 (필요 시)

---

## 13. v7 design 의 7 phase 요약 (참고)

```
Phase A  : 11 existing method × 28 cells 측정 (완료 ~5/9 18:00)
Phase B  : Multi naive failure mode analysis (완료 ~5/9 19:00)
Phase C  : Phase E 위한 prebuilt NPY build sf=10 (현재 진행)
Phase D  : 11 NEW method 코드 (완료 ~5/9 17:30)
Phase E  : 11 NEW method × 28 cells 측정 (sf=1 진행 중, sf=10 watcher 대기)
Phase F  : 6 baselines × 28 cells (B1/B2/B3/B5/B6 진행 중)
Phase G  : 종합 analysis + REPORT (예정 5/10 09:00)
```

---

## 14. 주의: 추가 발견 사항

### 14.1 FB ERROR (Phase F sf=1 single)

PID 837103 (Phase F B1+B2 × 12 single) 에서 FB single sf=1 측정 시 ERROR. SSN/FB rename 함정 또는 FB single 의 underlying NPY 미존재 가능성. 22:30 monitoring 시 확인 필요.

### 14.2 Memory peak ~890 GB (5/9 23:00 예상)

Phase C 6 cells 모두 prebuilt 시 + 6 Phase E NEW sf=10 launch 시 메모리 peak ~890 GB. RAM 1 TB 한계 근접. swap 발생 시 즉시 일부 process 일시 정지 필요할 수 있음.

### 14.3 Cell 3 multi_join_deep_wiki GMM 끝나면

(1) Multi Ensemble (PID 339513) Cells 4–6 자동 진행. Cell 4 = multi_join_sift_wiki, Cell 5 = multi_join_fb_wiki, Cell 6 = multi_join_yfcc_wiki. 각 cell 11 method × ~5 시간 → ~5/10 02:00 ~ 05:00 sf=1 multi 측정 모두 완료.

### 14.4 5/27 발표 deck 작성 시기

5/13 분석 완료 → 5/15 draft → 5/20 review → 5/25 final 일정 fit 가능. 5/10 정오 finalize 후 1주일 분석, 그 다음 1주일 deck 작업.

---

## Appendix A — File paths for quick reference

### A.1 Storyline / design

```
plans/RQ재정립_v7_evidence_20260509_1820.md           — v7 design (557 lines)
plans/RQ재정립_v6_storyline_20260505_2122.md          — v6 (이전, 참고만)
_internal/cache/failure_mode_analysis/REPORT.md       — Phase B 진단
_internal/handoff_v17_session_20260509_1612_MultiEnsembleRunning.md  — 직전 handoff
_internal/handoff_v18_session_20260509_2210_MaxPush.md  — THIS FILE
```

### A.2 Method 구현 (서버/로컬 양쪽)

```
서버: /mnt/hdd0/home/capstone2026/cache/rq3/methods/
로컬: /Users/hyunbin/Capstone/_internal/scripts/methods/
   — wanderjoin.py, ams_countsketch.py, neurocard.py
   — pq.py, coreset.py, dense_rp.py, bandit_ucb1.py, neuram.py
   — cca1d.py, cocluster_nystrom.py, conditional_adaptive.py
```

### A.3 측정 / 분석

```
서버: /mnt/hdd0/home/capstone2026/cache/rq3/
로컬: /Users/hyunbin/Capstone/_internal/scripts/
   — measure_multi_paradigm.py, measure_multi_ensemble.py
   — measure_phase_f_baselines.py
   — analyze_phase_g.py, analyze_failure_modes.py
   — build_new_multi_cells.py, build_FB_single_ensemble.py
```

### A.4 측정 결과

```
서버: /mnt/hdd0/home/capstone2026/cache/rq3/
   multi_paradigm_*/<cell>.csv          — paradigm baseline
   multi_ensemble/<cell>.csv            — (1) ensemble
   phase_f/phase_f_<cell>.csv           — Phase F 6 baselines
   failure_mode_analysis/REPORT.md      — Phase B 종합

서버: /mnt/hdd0/home/capstone2026/cache/rq1/
   rq3_FB_sf<N>_ensemble_<method>.parquet  — FB single per-method
```

### A.5 자문 메일 / 외부 문서

```
submission/_drafts/속도는벡터_자문메일_박성원멘토_20260509_v5.pdf
submission/_drafts/속도는벡터_자문메일_박성원멘토_20260509_v5.md
   — 5/9 deep-review 적용 (code-reviewer 8건 수정)
```

---

## Appendix B — Server commands for monitoring

### B.1 Process 상태

```bash
ssh capstone2026 "ps -ef | grep -E 'measure_|build_|run_ensemble' | grep -v grep"
```

### B.2 GPU 상태

```bash
ssh capstone2026 "nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv"
```

### B.3 디스크 상태

```bash
ssh capstone2026 "df -h /mnt/hdd0"
```

### B.4 측정 결과 CSV 갯수

```bash
ssh capstone2026 "ls /mnt/hdd0/home/capstone2026/cache/rq3/multi_paradigm_*/  | wc -l"
ssh capstone2026 "ls /mnt/hdd0/home/capstone2026/cache/rq3/multi_ensemble/ | wc -l"
ssh capstone2026 "ls /mnt/hdd0/home/capstone2026/cache/rq3/phase_f/ | wc -l"
```

### B.5 메모리 + load

```bash
ssh capstone2026 "free -h && uptime"
```

### B.6 Phase C sf=10 build 상태

```bash
ssh capstone2026 "ls -la /mnt/hdd0/home/capstone2026/cache/rq3/multi_data_sf10/"
```

---

## Appendix C — v7 design 22 methods overview matrix

| # | Method | Tier | Paradigm | Reference | Cost | GPU | Multi-table OK |
|---|---|---|---|---|---|---|---|
| 1 | HDBSCAN | (existing) | P1 Cluster | Campello 2013 | mid | CPU | yes |
| 2 | MiniBatch | (existing) | P1 Cluster | Sculley 2010 | low | CPU | yes |
| 3 | GMM | (existing) | P1 Cluster | Reynolds 1995 | mid | CPU | yes |
| 4 | Hilbert | (existing) | P2 Spatial | Faloutsos 1989 | low | CPU | yes |
| 5 | faiss_ivf | (existing) | P2 Spatial | FAISS 2017 | mid | CPU/GPU | yes |
| 6 | MB_partial | (existing) | P3 Streaming | (partial fit) | low | CPU | yes |
| 7 | Reservoir | (existing) | P3 Streaming | Vitter 1985 | low | CPU | yes |
| 8 | sparse_rp | (existing) | P4 DimReduction | Achlioptas 2003 | low | CPU | yes |
| 9 | PCA1D | (existing) | P4 DimReduction | Pearson 1901 | low | CPU | yes |
| 10 | LSH | (existing) | P5 QuasiRandom | Indyk-Motwani 1998 | low | CPU | yes |
| 11 | Sobol | (existing) | P5 QuasiRandom | Sobol 1967 | low | CPU | yes |
| 12 | WanderJoin | **S** | (Tier-specific) | Li SIGMOD 2016 | high | CPU | yes (multi-only) |
| 13 | AMSCountSketch | **S** | (Tier-specific) | Alon STOC 1999 | mid | CPU | yes |
| 14 | NeuroCard | **S** | (Tier-specific) | Yang VLDB 2020 | very high | **GPU** | yes |
| 15 | PQ | A | (Tier-specific) | Jégou 2011 | mid | CPU | yes |
| 16 | Coreset | A | (Tier-specific) | Bachem 2017 | high | CPU | yes |
| 17 | DenseRP | A | (Tier-specific) | Bingham 2001 | mid | CPU | yes |
| 18 | BanditUCB1 | A | (Tier-specific) | Carpentier 2011 | low | CPU | yes |
| 19 | NeurAM | A | (Tier-specific) | Geraci 2026 | very high | **GPU** | yes |
| 20 | CCA1D | B | (Tier-specific) | Hotelling 1936 | mid | CPU | yes |
| 21 | CoCluster_Nystrom | B | (Tier-specific) | Dhillon 2003 | high | CPU | yes |
| 22 | ConditionalAdaptive | C | (Exqutor variant) | (single only) | low | CPU | **single only** |

→ ConditionalAdaptive 는 single cell 12개에만 적용 (multi 16 cells 제외).

---

## Appendix D — Phase F 6 baselines detail

Adaptive Sampling 의 stratification + ensemble 효과 정량화 위한 6 baselines:

| Code | Name | Description |
|---|---|---|
| **B1** | vanilla Adaptive | Exqutor 본 논문 그대로 |
| **B2** | B1 + stratify | Adaptive + 분포 인지 stratified |
| **B3** | B1 + ensemble | Adaptive + (1) ensemble |
| **B4** | B2 + ensemble | Adaptive + stratified + (1) ensemble |
| **B5** | B1 + stratify + importance | Adaptive + stratified + importance sampling |
| **B6** | B5 + ensemble | Adaptive + stratified + importance + (1) ensemble |

### 4 axis 비교

각 baseline 별로:
1. **q_error** — 최종 cardinality 추정 오차
2. **sample size** — 도달까지 sampled tuple 수
3. **dropped fraction** — 제외된 표본 비율
4. **time** — wall-clock time

### Storyline ⑥ 의 핵심

> "ensemble 더해서 얻는 marginal recovery 정량화"

= B3 vs B1, B6 vs B5 비교가 핵심. marginal recovery = paired-better wins 의 차이.

---

## Appendix E — Storyline ④ failure mode 학술 진단 detail

### E.1 Curse of dimensionality (Geraci 2026)

원문 인용:

> "In high-dimensional joint space, the variance of stratified estimator decays as O(d^β₁ · n^−1) where β₁ ≈ +0.0079 (p=6.8e-85)"

→ **stratification efficiency 가 sublinear** in dimension. multi-table join 의 결합 차원이 single 보다 훨씬 높음 (예: partsupp ⋈ wiki 는 4096+768=4864-d).

### E.2 Cochran 1977 §5.5

> "Stratified sampling is more efficient than simple random sampling iff
>  σ_within < σ_overall and stratum sizes are correctly proportional"

→ multi-table join 공간에서는 두 조건 모두 약화. σ_within ≈ σ_overall (high-d 에서 within-stratum variance 가 줄지 않음).

### E.3 Bengtsson 2008 Effective Sample Size

```
ESS = (Σ w_i)² / Σ w_i²

Single  : ESS = 0.875
Multi   : ESS = 0.770
```

→ **multi 에서 effective sample size 가 12% 감소**. 같은 N 으로 sample 해도 actual information 이 적음. random sampling 에 stratified 더해도 information gain 이 marginal.

### E.4 결론

Multi naive 0/66 paired-better = stratification 의 variance reduction 이 high-d join 공간에서 사라짐. → 신규 11 method 도입 = "high-d 에 robust 한 sampling" 가설 검증.

---

## Appendix F — Storyline ⑤ 신규 11 method 도출 가설

### F.1 4 가지 학술 가설

```
H1: 차원 축소 후 sampling
    → DenseRP (Bingham 2001), CCA1D (Hotelling 1936), PQ (Jégou 2011)

H2: Coreset (모든 query 에 강한 representative)
    → Coreset (Bachem 2017), CoCluster_Nystrom (Dhillon 2003)

H3: Online learning (multi-armed bandit)
    → BanditUCB1 (Carpentier 2011), ConditionalAdaptive (Exqutor variant)

H4: Sketch / hash-based (memory-efficient)
    → AMSCountSketch (Alon STOC 1999), WanderJoin (Li SIGMOD 2016)

[bonus] Neural-based (deep learning)
    → NeuroCard (Yang VLDB 2020), NeurAM (Geraci 2026)
```

### F.2 Tier 구분 logic

```
Tier S : multi paired-better recover 강한 후보 (3 method)
Tier A : moderate 후보 (5 method)
Tier B : 보조 후보 (2 method)
Tier C : single-only 보완 (1 method)
```

→ 측정 후 paired-better wins 갯수로 Tier 재배치 가능.

---

## Appendix G — 새 세션 첫 작업 checklist

새 세션 시작 시 (5/10 정오 무렵):

```
[1] git pull --no-rebase origin main
[2] @_internal/handoff_v18_session_20260509_2210_MaxPush.md 읽기
[3] ssh capstone2026 "ps -ef | grep -E 'measure_|build_' | grep -v grep" 로 process 상태 확인
[4] CSV 갯수로 진행도 측정 (Appendix B.4)
[5] failure_mode_analysis/REPORT.md + phase_g_analysis/REPORT.md 확인
[6] Phase G analysis 미완 시 launch
[7] 사용자에게 SF=100 결정 trigger 메시지 작성
    — 디스크 여유 확인
    — 메모리 peak 예측
    — 시간 estimate (sf=100 6 cells × 11~21 method)
    — 사용자 결정 대기
```

---

## END

**Status**: Max push 모드 진행 중. 19+ active processes. 5/10 정오 finalize 예정.
**Next**: 22:30 monitoring (Cell 3 finalize + Phase C 첫 cell + Phase E NEW sf=10 자동 launch).
**Action**: 사용자 SF=100 결정 trigger (5/10 정오 ~ 오후).
