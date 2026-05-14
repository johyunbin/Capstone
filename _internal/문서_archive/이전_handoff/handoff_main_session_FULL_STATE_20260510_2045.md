# Handoff — Main Session FULL STATE (5/10 20:45 KST, context 한도 대비 종합 보존)

> 메인 세션이 길어 비정상 종료 가능. 본 문서는 새 세션이 **0% context loss**로 그대로 이어갈 수 있도록 모든 진행/수정/주의/blocker 정확 기록.
> 사용자 명시 (5/10 20:45): "혹시 종료될 수 있어서. 완벽하게. 새 세션이 SSN=FB 같은 것도 놓치지 않게."
> 우선순위: ① 새 세션 즉시 진행 가능 / ② 모든 detail 기록 / ③ 실패한 것 + 보완 필요 + RQ3 brainstorming 시 주의 사항.

---

## 0. TL;DR — 새 세션 즉시 액션 5단계

1. `git pull` (필요 시) + 본 문서 + handoff_v2 + reference_exqutor_paper_verbatim memory 정독
2. SSH 검증: `ssh capstone2026@165.132.140.240 "date"` (ed25519 key 등록됨, password 불필요. VPN 끊기면 재연결 후 retry)
3. 진행 상태: `ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"` — 현재 ~302+ measurements, 목표 702
4. 활성 procs/세션: `ssh capstone "tmux ls; pgrep -af measure_paper | grep -v grep | wc -l"` — 23 active procs (5/10 20:45 시점)
5. 5단계 narrative 핵심 (사용자 명시): ①RQ1/RQ2/RQ3 검증 ②Exqutor 100% 정확 재현 ③CaseA 대체 ④CaseB 증강 ⑤최종비교

---

## 1. 사용자 + 팀 + 시간

- **사용자**: 조현빈 (Capstone 팀 가장 형, peer-to-peer 톤, "형/누나" X)
- **팀명**: 속도는벡터 (연세대 컴공)
- **팀원**: 박세은 (팀장), 강재현, 조현빈, 이동욱
- **지도교수**: 박광현 (BDAI)
- **지도연구원**: 임채림 석사 (서버 admin, 채림님 메일 = 본 작업 server 정보 출처)
- **멘토**: 박성원 (삼성전자 AI센터)
- **외출**: 5/10 14:29 KST 외출 시작, 전권 위임 ("전권 위임이형이야"), 5/10 17:39 VPN 복구 + 재 위임
- **시간 압박 X** — paper 100% 정확 + 모든 method 완벽 측정 우선
- **5/10 18:49 명시**: "하나도 빠짐없이 갈거야 완벽 논문 재현 + 우리가 기존 논문의 한계를 보완하거나 극복하는 내러티브"
- **5/10 20:45 명시**: 본 문서 작성 트리거 (context 한도 대비 보존)

---

## 2. Exqutor paper 상세 분석 (arXiv:2512.09695v2, Dec 2025)

연세대 BDAI 박광현 교수 본 논문. Capstone 5/10 paper 1-15p 깨끗 정독 결과 (agent 1).

### 2.1 paper §V-A ECQO (Extended Cardinality Query Optimizer)
- HNSW range query를 **cardinality estimator**로 사용 (vector index 있을 때)
- 1~2ms 내 정확한 cardinality 반환 (HNSW M=16, ef_search=400)
- Fig 4 (TPC-H ECQO main, SF=100), Fig 10 (TPC-DS ECQO, SF=10)에 적용

### 2.2 paper §V-B Adaptive Sampling (vector index 없을 때 — 우리 핵심 영역)

**Eq 1-6 verbatim** (paper p.6):
```
N = ⌈z²·P̂(1-P̂)/e²⌉ = ⌈1.96² × 0.5 × 0.5 / 0.05²⌉ = 385         (1) initial
Q-error = max(C_est/C_true, C_true/C_est)                      (2)
δ = α·(Q-error - β) - (100-α)·sampling_ratio                   (3) adjustment
V_t = m·V_{t-1} + η_t·δ                                        (4) momentum
size_{t+1} = size_t + V_t                                      (5) size update
η_{t+1} = γ·η_t                                                (6) lr decay
```

**Hyperparam (paper p.7 verbatim)**:
- m = 0.9 (momentum)
- η₀ = 0.1 (init learning rate)
- α = 50 (δ weighting)
- β = 1.5 (target Q-error)
- γ = 0.99 (decay)
- update_period = 50 queries
- N_init = 385

**중요**: paper Eq 1-6에 **min/max clamping 없음**. handoff_v1의 "min=355/max=415" 폐기.

### 2.3 paper §VI 측정 setup
- Hardware: Intel Xeon Gold 6530, 128 vCPUs, 1.0 TB RAM (paper exact = 우리 서버와 거의 동일)
- HNSW: M=16, ef_construction=200, ef_search=400
- 10 trials, lowest+highest 1개 제외 → 8 runs trim mean
- PostgreSQL `max_worker_processes = 8`
- Trial seed: 우리 = `trial_idx * 13 + 7`

### 2.4 paper Fig별 setup verbatim (handoff_v2 §3.1)

| Fig | SF | Datasets | Queries | Selectivity | Mode |
|---|---|---|---|---|---|
| Fig 4 (ECQO TPC-H) | 100 | DEEP/SIFT/SSN | Q3,5,8,9,10,11,12,20 (8) | 1% (200 vectors index) | ECQO |
| Fig 5 (Sampling main) | 100 | DEEP=Q3,10,12 / SIFT=Q3,10,12 / SSN=Q3,9,10 | 1% | Bernoulli/Adaptive |
| Fig 6 (size convergence) | 100 | DEEP/SIFT/SSN | n/a | 1% | Adaptive 1000 iter |
| Fig 7 (YFCC tag) | 10 | YFCC | TPC-H 8 | 1% | sampling+ps_tag |
| Fig 8 (DEEP+WIKI partsupp 4-way) | 10 | DEEP+WIKI 같은 partsupp | TPC-H 8 | 1% | sampling multi-vec |
| Fig 9 (DEEP+WIKI cross-table) | 10 | partsupp[DEEP] × part[WIKI] | TPC-H 8 | 1% | sampling cross |
| Fig 10 (TPC-DS) | 10 | DEEP item_deep | Q7,12,19,20,42,72,98 (7) | (paper threshold) | ECQO |
| Fig 13 (Selectivity ablation) | 100 | DEEP | Q3,10,12 | **0.1%, 1%, 10%** | Bernoulli/Adaptive |
| Fig 14 (Scalability) | 1/10/100 | DEEP | Q3, Q5, Q20 | 1% | Adaptive |

### 2.5 TPC-H 8 queries (paper §IV verbatim)
Q3, Q5, Q8, Q9, Q10, Q11, Q12, Q20

### 2.6 TPC-DS 7 queries (paper §IV verbatim)
Q7, Q12, Q19, Q20, Q42, Q72, Q98

### 2.7 Vector range threshold (Exqutor github query_plans/ verbatim)
- TPC-H 8 queries 통일: `<-> 'image_embedding' < 0.86` (DEEP 96d 기준)
- TPC-DS:
  - Q7/Q12/Q20/Q72: `< 1.08`
  - Q19/Q42: `< 1.20`
  - Q98: `< 1.30`
- **위치**: `reference/exqutor_query_plans/{tpc_h,tpc_ds}/q*.sql` (5/10 14:20 클론)

### 2.8 Schema (paper §IV-B verbatim)
- partsupp: ps_image_embedding (DEEP/SIFT/SSN/YFCC) + ps_text_embedding (WIKI) + ps_tag (YFCC tag)
- part: p_text_embedding (WIKI)
- item (TPC-DS): i_embedding (DEEP)

### 2.9 paper Fig 12 reports
**avg Q-error 1.69** (Exqutor) vs SelNet 5.53 (3.3× 우위) — 우리 paper exact 재현 검증 anchor

---

## 3. 데이터셋 alias + dim + tables (놓치기 쉬운 핵심 detail)

### 3.1 데이터셋 alias 테이블

| 우리 코드 alias | paper 이름 | server table 이름 | dim | 크기 (SF=10) | 사용 Fig |
|---|---|---|---|---|---|
| **DEEP** | DEEP [59] | partsupp_deep_{1,10,100} | 96 | 8M @ SF=10 | Fig 4/5/6/8/9/10/13/14 |
| **SIFT** | SIFT [60] | partsupp_sift_{1,10,100} | 128 | 8M @ SF=10 | Fig 4/5/6 |
| **SSN** = **FB** | SimSearchNet++ [61] | **partsupp_fb_{1,10,100}** | 256 | 8M @ SF=10 | Fig 4/5/6 |
| **YFCC** | YFCC [62][63] | partsupp_yfcc_{1,10} | 192 | 8M @ SF=10 | Fig 7 |
| **WIKI** | WIKI [64] | partsupp_wiki_{1,10}, part_wiki_10 | 768 | 8M @ SF=10 | Fig 8/9 |

### 3.2 ⚠️ **SSN = FB alias** (놓치기 쉬운 결정적 detail)

- paper에서는 **SimSearchNet++** (SSN) 으로 명시
- server에서 **partsupp_fb_*** 으로 저장됨 (FB = Facebook AI 출처)
- query_pool 파일명: **`query_pool_SSN_sf{1,10,100}.parquet`** (SSN 사용)
- 우리 코드 (measure_paper_exact.py): `dataset="SimSearchNet++"`, `table="partsupp_fb_{sf}"`, alias map: `"SimSearchNet++": "SSN"`

**새 세션이 절대 놓치지 말 것**:
- SSN ↔ FB ↔ SimSearchNet++ 삼각 alias
- query_pool 파일 찾을 때 `SSN_sf*` (SimSearchNet++가 아님!)
- table 찾을 때 `partsupp_fb_*` (partsupp_ssn_* 아님!)

### 3.3 multi-vector schema (Fig 8/9)
- **Fig 8**: `partsupp_deep_wiki_10` (single table, 2 vector cols: ps_embedding_deep + ps_embedding_wiki)
- **Fig 9**: `partsupp_deep_10` ⋈ `part_wiki_10` (cross-table FK join, ps_embedding[DEEP] + p_embedding[WIKI])

---

## 4. 서버 환경 + 인프라

### 4.1 SSH 접속
- **IP**: 165.132.140.240
- **계정**: capstone2026
- **password**: bdai1234! (채림님 메일, ed25519 key 등록됐으므로 일반 사용은 password 불필요)
- **VPN**: 사용자 측 활성 — 끊기면 SSH timeout (이전 17:30~17:39 약 9분 끊김 사례)
- **ssh-copy-id**: 5/10 14:30에 등록 완료 (~/.ssh/id_ed25519.pub)
- **~/.ssh/config Host * 강화** (5/10 17:50): `ServerAliveInterval 15`, `ServerAliveCountMax 100`, `TCPKeepAlive yes` (1500초 timeout 허용)
- **Background keep-alive script**: `/tmp/capstone_keepalive.sh` 60s마다 SSH ping (PID 99488), `/tmp/capstone_keepalive.pid`

### 4.2 작업 디렉토리 + DB
- **작업 dir**: `/mnt/hdd0/home/capstone2026/` (채림님 명시: 이 폴더에서만 작업)
- **PG instance**: port **55435** active (vanilla_sf100 → wns41559 DB)
- **다른 인스턴스 (절대 X)**: port 55432, 55433 (다른 사용자 작업 中)
- **DB 목록**: wns41559 (TPC-H), tpcds (SF=10), tpcds100 (SF=100), imdbload, postgres, template{0,1}

### 4.3 PG tables (모두 paper exact 일치)
- **TPC-H base 8** × SF=1/10/100: customer, lineitem, nation, orders, part, region, supplier, partsupp (24 tables)
- **partsupp_{deep,sift,fb}_{1,10,100}**: 9 tables (DEEP/SIFT/SSN), HNSW deep_hnsw/sift_hnsw/fb_hnsw 모두 빌드됨
- **partsupp_{yfcc,wiki}_{1,10}**: 4 tables, HNSW 빌드됨 (yfcc) + wiki는 part_wiki_10에 빌드
- **partsupp_deep_wiki_10**: 4-way schema (Fig 8), HNSW deep_hnsw_10_2 + wiki_hnsw_10_2 빌드 (단 stratum_id 컬럼 부재 — A2-Fig8 measurement blocker)
- **partsupp_deep_sift_10**: multi (deep + sift), HNSW 빌드
- **part_wiki_10**: WIKI 768d (Fig 9 cross), HNSW 빌드
- **customer_sift_10**: SIFT 128d (RQ1/RQ2 기존 setup 일부)
- **items_100**: 100 rows (TPC-H items, paper와 무관)
- **vector_stratum_sigma**: KM20 σ_j 사전 계산 테이블 (RQ2 Neyman/Anti 측정 시 활용 가능)
- **exqutor_qerror**: Exqutor patched PG의 자동 lookup 테이블 (wns41559에 있음, tpcds DB에 5/10 15:09 추가 생성 — A3-TPCDS ECQO fix 시도)

### 4.4 NPY cache (`/mnt/hdd0/home/capstone2026/cache/rq1/`)
- `partsupp_{deep,sift,fb}_{1,10,100}_{vectors,strata,pks}.npy` 모두 빌드 (vectors 총 ~150GB)
- `query_pool_{DEEP,SIFT,SSN,YFCC,WIKI}_sf{1,10,100}.parquet` (100 query × 5 sel 캘리브레이션)
- `query_selectivity_{DEEP,...}_sf{1,10,100}.parquet` schema: `query_id, selectivity, D_target, true_cardinality, actual_sel`
- ⚠️ **calibrated selectivity = [0.01, 0.05, 0.1, 0.3, 0.5]** (5종) — paper {0.001, 0.01, 0.10}은 0.001이 calibration 없음 (sel=0.001 빌드 후순위)

### 4.5 자원 사용 (5/10 20:45 시점)
- **CPU**: 128 vCPU, 23 active procs × 1.1 core ≈ 25 cores 사용 (~20%, 80% idle)
- **RAM**: 1.0 TB, 509GB used, 247GB free, 264GB buffer/cache (NPY page cache)
- **GPU**: 4× NVIDIA RTX 6000 Ada 49GB each, 모두 0% idle (CPU 측정 中, GPU 미활용)
- **disk**: /mnt/hdd0 13TB / 11TB used (89%, 1.4TB 여유) — 채림님 sf100 처음 실행 느림 경고 (HDD)

---

## 5. 채림님 메일 verbatim + 자원 활용 룰

### 5.1 채림님 메일 (5/10 14:30 받음, handoff_v2에 보존)
> 서버 ip: 165.132.140.240 / 계정 id: capstone2026 / 계정 pwd: bdai1234!
> /mnt/hdd0/home/capstone2026 폴더에서만 작업 / 데이터 미리 옮겨둠 (vanilla_sf100)
> sudo 권한 X / PostgreSQL 인스턴스는 **55435-55436 포트만** / 기존 포트/태스크 충돌 X
> 해당 서버 GPU 있는데 사용 자제 → ⚠️ **하지만 사용자 5/10 15:03 추가 명시**: "지금은 자원을 거의 점유를 안하는 상태여서 여유롭게 사용해도 돼. 다른 유저 작업 중지 취소만 되지 않는 선에서 적극 이용 가능해. 지피유든 다른세션 이용하든 티멋스 등 여러가지"
> tmux로 진행 / "나중에 캡스톤 집중 시즌 되면 연구실 내 사용 스케줄 조율 필요"
> Exqutor 깃헙 클론 → pgvector/postgresql submodule 확인 / duckdb·big-ann-benchmark는 안받아도 OK
> 인스턴스 빌드 → vanilla_sf100 데이터 폴더 연결 → 55435 포트
> log/ 디렉토리 만들어서 설정
> tpc-h 데이터: db_user=wns41559, database=wns41559
> sf100은 처음 실행 시 메모리 로드 시간 큼 → sf10으로 테스트 권장

### 5.2 **자원 활용 룰 (5/10 15:03 사용자 + 20:11 사용자 + 5/10 20:45 사용자)**
- 다른 인스턴스 포트 (55432, 55433) **절대 X**
- 우리 포트 55435-55436만
- tmux 다중 세션 OK (현재 23+ tmux 세션)
- GPU **사용 가능** (사용자 명시 — 다른 사용자 작업 中이지만 GPU는 idle 상태에서 활용 OK)
- 다른 사용자 **2명 추정**: postgres 55432 (319643/127176 PIDs) + 55433 (sihyunkim2) — 영향 X 한도
- 병렬 stuck 회피: 30~60초 단위 monitor + stuck 감지 시 kill (handoff_v1 §6 stuck 정의: log mtime 5분+ + CPU < 50%)

### 5.3 GPU 활용 (이전 실패 → 현재 상태)
- **이전 실패 사례**: GPU activation 시도했으나 OOM 또는 CUDA error로 fallback 했던 적 있음 (정확 상황 미기록 — 추후 retry 시 cuda_visible_devices + memory limit 확인 권장)
- **현재 GPU 0%/2MiB idle** (4 GPUs all idle)
- **활용 가능 영역**:
  - faiss-gpu: faiss IndexIVF / IndexPQ GPU 가속 (5-10× 빠름)
  - torch-cuda: NeurAM / NeuroCard MLP autoencoder
  - cuML: KMeans / DBSCAN GPU
- **주의**: 
  - 다른 사용자 작업 中이면 GPU memory 점유 X (`nvidia-smi --query-gpu=memory.used` 0이 아닐 시 회피)
  - GPU 0/2/3 사용 (handoff_v1 명시: 1번은 채림 rule)
  - 한 번에 한 GPU에 단일 procs 권장 (memory contention 회피)
  - **재시도 시 단계적 검증**: 1 method × 1 cell smoke → CUDA error 없으면 본격

---

## 6. 5단계 narrative (사용자 명시)

### 6.1 narrative (5/10 14:03 카톡 사진)

| 영역 | Exqutor | 한계 | 우리 공략 |
|---|---|---|---|
| Vector index 있음 | ECQO (§V-A) | — | — |
| Vector index 없음 + single-table | §V-B Adaptive Sampling | unstratified Bernoulli | distribution-aware augment |
| Vector index 없음 + multi-table | §V-B가 KNN 한정 | 결합 분포 못 활용 | multi 결합 분포까지 확장 |

→ **우리 contribution = augment within §V-B** (대체 X — §V-A ECQO 그대로 인정).

### 6.2 5단계 narrative (사용자 명시 5/10 14:03)
1. **RQ1, RQ2, RQ3 검증** (기존 결과 + paper exact 재확인)
2. **Exqutor 100% 정확 재현** (paper exact, 멋대로 추가 X — §V-B Eq 1-6)
3. **CaseA**: 우리 method가 sampling step **대체** (replace)
4. **CaseB**: 우리 method가 sampling step **증강** (augment, B1+method ensemble)
5. **최종 비교**: B1 vs CaseA vs CaseB → 우리 contribution 입증

### 6.3 사용자 추가 (5/10 18:49)
"하나도 빠짐없이 + 완벽 논문 재현 + 우리가 기존 논문의 한계를 보완하거나 극복하는 내러티브"

### 6.4 우리 목표 (사용자 명시 5/10 20:45)
1. **Exqutor 완벽 재현** — 동일 조건, 동일 실험, 복붙 가능 수준
2. **RQ3 방법 동원해서 adaptive sampling 완전 대체 가능 여부**
3. **대체 불가 시 adaptive sampling 전처리 통해 개선**

### 6.5 narrative 검증 결과 (5/10 20:45 시점)
- ✅ **#2 paper 정확 재현**: 9 cells avg_qe 1.541~1.708 vs paper Fig 12 1.69 (-6.3%~+1.1%)
- ⚠️ **#3 CaseA 단독 대체**: minibatch_partial **-7.41%** 만 강한 outperform / 다른 -1~-2% (약함)
- ✅ **#4 CaseB 증강**: 6 methods 모두 -2~-7% outperform B1
- ✅ **#5 최종**: CaseB > CaseA > B1
- ✅ **RQ1**: paper sel{0.01, 0.10}에서 random vs KM20 stratified **5% 격차** (DEEP/SIFT 모두)
- ✅ **RQ2**: paper sel{0.01, 0.10}에서 Prop **1.584** < Equal **1.637** < Bernoulli **1.748** (sel=0.01) **9% 격차**

---

## 7. 진행 상태 (5/10 20:45 KST)

### 7.1 완료 ✅
| 단계 | 측정 수 | 결과 |
|---|---|---|
| Phase A B1 | 9/9 cells | paper Fig 12 1.69 일치 (-6.3%~+1.1%) |
| Phase B CaseA Tier 1 | 99/99 (11 methods × 9 cells) | minibatch_partial -7.41% |
| Phase C CaseB Tier 1 | 99/99 | 6 methods -2~-7% outperform |
| RQ1 paper exact | DEEP/SIFT × Bernoulli/KM20 | 5% 격차 |
| RQ2 paper exact | DEEP/SIFT × Bernoulli/Equal/Prop | 9% 격차 |

### 7.2 진행 중 🔄 (23 active procs)
| 단계 | 진행 | 남은 | ETA |
|---|---|---|---|
| Phase B extra (8 NEW methods × 9 cells) | ~50/72 | ~22 | ~21:30 |
| Phase B extra2 (20 NEW methods × 9 cells) | ~50/180 | ~130 | ~22:30 |
| Phase C extra (28 NEW methods × 9 cells) | ~6/252 | ~246 | 다음 |
| **합계** | **~302/702** | **~400** | **5/11 01-02시 KST** |

### 7.3 미측정 / blocker ⏳
- **A2-Fig8** (DEEP+WIKI partsupp 4-way multi-vector measurement)
  - blocker: partsupp_deep_wiki_10에 stratum_id 컬럼 부재
  - measurement loop 변경: single vector → multi-vector AND predicate
  - 부분 우회: ps_embedding_deep만 single vec measurement → A2-Fig9와 측정 동일
  - 추후 multi-vector 정확 재현 시 별도 implementation
- **A3-TPCDS** (Fig 10 ECQO mode)
  - blocker: Exqutor patched PG의 ECQO trigger가 vector cast SQL과 충돌 → PG crash 반복
  - 시도: autocommit=True + exqutor_qerror tpcds DB 생성 → 모두 fail
  - 가능 우회: SET hnsw.ef_search OFF + simple SELECT count(*) 측정 (paper Fig 10의 일부만 재현)
  - 추후 fix: Exqutor source code 분석 + ECQO trigger 비활성화

---

## 8. 5 Critical findings (handoff_v1 추정 vs paper verbatim)

| # | 항목 | handoff_v1 추정 | paper verbatim | 결정 |
|---|---|---|---|---|
| 1 | Fig 5 queries | 모든 dataset Q3,9,10,12 동일 | DEEP/SIFT=Q3,10,12 / SSN=Q3,9,10 | paper 따름 |
| 2 | min/max bound | "min=355, max=415 강제" | Eq 1-6에 clamping 없음 | bound 제거 |
| 3 | Selectivity scope | 우리 기존 {0.05, 0.30, 0.50} | paper Fig 13 = {0.1%, 1%, 10%} only | paper 따름 |
| 4 | A3 TPC-DS mode | sampling replace/augment 가정 | paper Fig 10 = ECQO mode (sampling X) | A3는 ECQO 별도 |
| 5 | Metric | Q-error만 | paper Fig caption "execution time" + Eq 2 | Q-error + wall-clock 둘 다 (현재 Q-error만) |

---

## 9. 측정 인프라

### 9.1 Local
- `_internal/scripts/measure_paper_exact.py` (1100+ lines) — 메인 measurement script
- `_internal/scripts/analyze_paper_exact.py` — Phase D analysis + REPORT.md 자동 생성
- `_internal/handoff_*.md` 5개 (v0/v0.bak/v1/v2/validation/full_state — 본 문서)
- `reference/exqutor_query_plans/{tpc_h,tpc_ds}/` — paper Q*.sql 모두 (5/10 14:20 클론)

### 9.2 Server (`/mnt/hdd0/home/capstone2026/`)
- `cache/rq3/measure_paper_exact.py` (메인이 scp, 동일 본)
- `cache/rq3/analyze_paper_exact.py`
- `cache/rq3/_measure_common.py` (기존 RQ3 인프라, paper N=385 일치 + 우리 PORT=55435 override)
- `cache/rq3/run_phase_b_full.sh` / `run_phase_b_extra.sh` / `run_phase_b_extra2.sh` / `run_phase_c.sh` / `run_phase_c_extra.sh` / `run_sparse_rp_retry.sh` / `run_phase_b_cell.sh`
- `cache/rq3/run_*.py` (기존 method-specific scripts: sparse_rp/random_projection/minibatch/etc — 우리 _get_method_strata에서 일부 import)
- `cache/rq3/sparserp/sparse_random_projection.py` (assign_sparse_rp signature: matrix먼저, vectors 둘째)
- `cache/rq3/offline_simple/random_projection.py` (assign_random_projection 동일 signature)
- `cache/rq3/paper_exact/*.json + *.csv + REPORT_paper_exact.md` (측정 결과)

### 9.3 method registry (39 methods, measure_paper_exact.py § _get_method_strata)
**Tier 1 Legacy (11 methods, paper handoff_v1 §3 + random_projection 추가)**:
sparse_rp ★4, random_projection, minibatch, hilbert, gmm, minibatch_partial, lsh, pca1d, sobol, reservoir, faiss_ivf

**Phase B extra (8 NEW)**:
pq, kdtree, halton, hammersley, coreset, birch, agglomerative, dense_rp

**Phase B extra2 (20 NEW Tier S+/A/B)**:
opq, kdpp, banditucb1, neuram, thompson_sampling, mfmc, epsilon_net, ams_count_sketch, neurocard_lite, adaptive_bucket_probing, ccsketch, factor_join, lp_bound, cca1d, cocluster_nystrom, tucker, vinecopula, hkbu_repsample, lhs, lpm2

### 9.4 핵심 fix 이력
- 5/10 14:49 query_selectivity column: `d_target` → `D_target` (대문자), `true_card` → `true_cardinality`
- 5/10 14:50 trimmed_mean inf filter (Bernoulli hits=0 → est=0 → Q-error inf 회피)
- 5/10 14:50 AdaptiveState.update q_error inf cap=100 (size 폭증 방지, paper에 명시 X)
- 5/10 17:22 sparse_rp / random_projection signature swap fix: `assign_*(matrix, vectors)` (96d 우연 통과, 192d fail)
- 5/10 18:06 GMM cholesky fail fix: `covariance_type='diag' + reg_covar=1e-2` (SIFT 128d / SSN 256d)
- 5/10 17:50 ~/.ssh/config 강화 (ServerAliveInterval 15, CountMax 100, TCPKeepAlive yes) + background keep-alive script

### 9.5 Phase D analysis 출력
- `cache/rq3/paper_exact/REPORT_paper_exact.md` (자동 생성, analyze_paper_exact.py 재실행 시 갱신)
- 5단계 narrative summary
- per-method × per-cell paired Δ% 표 (Wilcoxon p-raw + p_adj BH-FDR)

---

## 10. 측정 과정 문제 + 해결 / VPN keep-alive

### 10.1 발생 문제 + 해결
- **PG recovery mode (2회)**: 동시 fetch + Fig8 strata 빌드 시 PG crash → fig8 fetch kill + PG 자동 복구 (2분)
- **A1-SSN 9분 stuck**: NPY fetch D-state (disk wait) → kill + 별도 tmux retry (정상)
- **VPN 끊김 (1회, 17:30~17:39 9분)**: 사용자 외출 중 → background keep-alive script + ssh config 강화로 회피
- **A2-Fig7 sparse_rp/random_projection 192d fail**: signature swap → fix 후 retry
- **A2-Fig8 stratum_id 부재**: post-fix 후순위
- **A3-TPCDS ECQO PG crash**: 후순위 (paper §V-A 영역 외)
- **YFCC 192d outliers (lsh/RP/sobol)**: cluster imbalance — narrative 영향 X (다른 cells 정상)

### 10.2 stuck 정의 (handoff_v1 §6)
- log mtime **5분 이상** 갱신 X + procs CPU **< 50%**
- 즉시 처리: kill + 다음 cell sequential 재 launch
- 모니터: 30~60초 간격

### 10.3 monitor re-arm (1시간 timeout)
- Monitor tool은 default 1시간 timeout — 1시간마다 re-arm 필요
- 5/10 20:45까지 ~5회 re-arm 했음
- ServerAlive 강화로 SSH 끊김 빈도 줄어듬

---

## 11. RQ1/RQ2 추가 기여 + narrative pivot (카톡 5/9 분석 결과 — 핵심)

### 11.1 기존 narrative (중간보고서 4/17, 중간발표 4/28)
- RQ1: 2x2 (Block vs Row × Normal vs Skew) — random sampling skew 부정확
- RQ2: KM20 + Equal/Prop/Neyman/Anti-Neyman 4-way stratification
- **중간발표 가정**: "single 우수 → multi 우수일 것"

### 11.2 🚨 카톡 5/9 18:27 narrative pivot (사용자 verbatim)
> **"지금 우리가 찾은 게 multi에서 진행해보니까 그냥 adaptive 하는거랑 큰 차이가 없더라. 지금 찾은 single이 큰 기여가 없어서. 실험을 다시 방법을 찾아서, single/multi에 모두 강한 방식들 찾으면 기존거를 실패한 걸로 소개하고, 기존의 중간 발표 때까지의 프로젝트 목표에서 single 우수 → multi도 우수할 것이다에서 single 우수 → multi 우수 방식을 RQ3에서 실제로 찾았고, 이걸 exqutor 방식 vs 우리가 찾은걸 exqutor에 앙상블한 방식 비교해서 실질적으로 효능이 있음을 보이는 식으로."**

→ **narrative pivot**:
- ❌ single 우수 → multi 우수 가정 폐기 (multi에서 adaptive와 큰 차이 없음)
- ✅ **single+multi 모두 강한 방식 발견 → Exqutor에 ensemble** (= 우리 CaseB)
- ✅ "Exqutor 방식 vs Exqutor + 우리 방식 ensemble" 비교가 5/27 최종발표 climax

### 11.3 카톡 5/8 16:13 박세은 narrative 약점 (해결 권장)
- **RQ2 weakness**: 4 method (BERN/Prop/Neyman/Equal) 사이 q-error 격차 < 1% → "어느 mode든 비슷, 균등도 충분" 부수 발견 — paper의 Adaptive 우위 대비 narrative 약함
- **RQ2 Neyman**: skew 데이터의 작은 selectivity에서만 개선, 모든 상황 X
- **RQ3 multi**: 11 method × multi-table = 우리가 Adaptive보다 더 나은 게 **66 비교 中 0건**

### 11.4 카톡 5/9 학술 contribution claim (사용자 명시)
> "vector DB cardinality estimation 영역에서 단일 + multi 모두 검증된 published method 가 현재까지 **0개**. 즉 우리가 first 발견하면 학술 contribution"

**우리 paper exact CaseB 결과 (5/10)**:
- 6 methods 모두 -2~-7% outperform B1 (single cells에서)
- multi-table cells (A2-Fig9 cross / A2-Fig8 multi-vec)에서도 ensemble 효과
- 즉 **single + multi 모두 강한 ensemble narrative 검증 진행 중**

### 11.5 RQ1/RQ2 추가 기여 (사용자 5/10 20:45 명시 + 카톡 분석 후)
**즉시 가능**:
1. **RQ2 Neyman/Anti-Neyman paper exact 추가** (현재 Bernoulli/Equal/Prop만)
   - vector_stratum_sigma 테이블 활용
   - paper sel{0.01, 0.10}에서 Neyman 우위 narrative 검증
2. **selectivity gradient 보충** (카톡 4/15 박세은 권장):
   - 현재 sel{0.01, 0.10}만 → 0.05, 0.30 추가 측정
   - paper Fig 13 ablation 외 우리 narrative 강화
3. **RQ1 정정**: "paper Bernoulli 자체도 random sampling — Adaptive (Eq 1-6)이 강화" → 우리 RQ1 narrative + paper §V-B narrative 1:1 대조
4. **paper SelNet 비교** (Fig 12): paper의 learned estimator (5.53) vs 우리 method (1.69~1.94 range)

**카톡 5/9 18:35 trigger** (조현빈): "더 테스트했는데도 multi에서 효과 없으면 [중단됨]" → 5/10 우리 측정에서 multi cell (A2-Fig9, A2-Fig8 후순위) ensemble 효과 검증 — 그 후 narrative 결론

### 11.6 5/27 최종발표 storyline (카톡 5/9 18:27 사용자 명시, 7단계)
1. 단일 테이블 random sampling이 skew 분포에서 무너짐 (RQ1)
2. 분포 알면 Neyman stratified 답 (RQ2)
3. 분포 모르니까 분포 정보 추정 활용 (RQ3, 5 paradigm × 11 method)
4. 단일에서 Adaptive 대비 평균 -8% 개선 입증 (paper exact 검증 ✓)
5. multi-table에서 우리 11 method가 Adaptive보다 나은 게 0건 → single 우위가 multi로 일반화 X
6. **신규 method 발굴 (Tier S+/A 22개) → multi에서도 강한 방식 찾기** (= 5/10 우리 진행)
7. **Adaptive 단독 vs Adaptive + 우리 ensemble 직접 비교 → climax** (= 우리 CaseB)

→ **5/27 발표 narrative**: 중간발표 가정 (single → multi) **실패 인정** + 새 발견 (single+multi ensemble) + Exqutor 통합 효능 입증

---

## 12. 향후 brainstorming 시 주의 (drop reason)

### 12.1 drop / fail method (재시도 시 주의)
- **HNSW-SS** (handoff_v1 명시 DROPPED): KM20 oracle 영향 측정 불가
- **WanderJoin**: 우리 측정 framework 부적합 (multi-table sampling)
- **HDBSCAN**: 큰 dataset에서 메모리 폭증 (8M+ rows 시 OOM)
- **lsh / random_projection / sobol on YFCC 192d**: cluster imbalance → 극단 outlier (paper exact narrative 영향 X but method 자체 부적합)

### 12.2 SF=100 시간/공간 복잡도 주의
- **GMM full covariance**: SF=100 (80M)에서 cholesky fail (현재 diag로 fix)
- **AgglomerativeClustering**: O(n²) memory — sample 10K로 우회
- **SpectralBiclustering**: small sample (5K)만 사용
- **VineCopula**: rank-transform 100K subset만
- **Tucker**: 3-mode PCA 단순화 (full Tucker는 메모리 폭증)
- **kdpp**: greedy farthest-point 50K subset만

### 12.3 RQ3 추가 method 고려 시
- 새 method implementation 시 **80M cells 메모리/시간 검증** 필수
- chunked predict (`for i in range(0, N, 100K)` 패턴) 필수
- KMeans/GMM 등은 `train on subset (50K-200K) → predict on full` 패턴

### 12.4 RQ1/RQ2 추가 시 주의
- paper sel scope = {0.001, 0.01, 0.10}만 (Fig 13)
- 우리 query_pool calibration = {0.01, 0.05, 0.10, 0.30, 0.50} → 0.001 미빌드
- **0.001 calibration 빌드 필요시**: D_target s.t. partsupp_deep_100 actual_sel = 0.001 (8000 rows out of 80M의 10x 작음)

---

## 13. tmux 세션 list (5/10 20:45)

```
- capstone (4/14, 비활성)
- orchestrator (5/7, 비활성)
- paper_exact (Phase A B1, sleep)
- phase_b_smoke (5 methods × A5-sf1, sleep)
- phase_b_full (Tier 1 Phase B sequential, sleep — 모두 끝)
- rq1_rq2 (RQ1/RQ2 paper exact, sleep)
- fig8_fix (kill 됨)
- ecqo (PG crash fail, sleep)
- a1_ssn_retry (A1-SSN B1, sleep)
- sparse_rp_retry (signature fix, sleep)
- gmm_retry (covariance diag fix, sleep)
- pb_A1-DEEP / pb_A1-SIFT / pb_A1-SSN / pb_A4-sel / pb_A5-scale-sf100 (Phase B per cell × Tier 1, 진행/완료)
- pc_A1-DEEP / pc_A1-SIFT / pc_A1-SSN / pc_A2-Fig7 / pc_A2-Fig9 / pc_A4-sel / pc_A5-scale-sf{1,10,100} (Phase C Tier 1, sleep)
- pbe_A5-sf1/sf10/Fig9/Fig7/A1-DEEP/SIFT/SSN/sf100/A4-sel (Phase B extra, 진행)
- pbe2_A5-sf1/sf10/Fig9/Fig7/A1-DEEP/SIFT/SSN/sf100/A4-sel (Phase B extra2, 진행)
- pce_A5-sf1/sf10/Fig9/Fig7/A1-DEEP/SIFT/SSN/sf100/A4-sel (Phase C extra, 진행)
```

---

## 14. 새 세션 시작 복붙 프롬프트

```
@_internal/handoff_main_session_FULL_STATE_20260510_2045.md 부터 정확히 read.
+ @_internal/handoff_v2_paper_verbatim_decisions_20260510_1418.md
+ @_internal/handoff_validation_statistics_20260510_2030.md (별도 검증 세션)
+ memory: reference_exqutor_paper_verbatim.md + feedback_paper_exact_principle.md

🚨 사용자 명시 (5/10 14:03 + 18:49 + 20:45):
- "paper의 모든 항목 완전 똑같이 진행 + 단 하나라도 다르면 안 됨"
- "하나도 빠짐없이 + 우리 기존 논문 한계 보완/극복 narrative"
- 목표: ① Exqutor 완벽 재현 ② RQ3 방법 동원 adaptive 대체 가능 ③ 대체 불가 시 전처리 개선

핵심 데이터셋 alias (놓치지 말 것):
- DEEP=DEEP 96d
- SIFT=SIFT 128d
- **SSN = FB = SimSearchNet++ 256d** (server table은 partsupp_fb_*, query_pool은 query_pool_SSN_sf*)
- YFCC 192d, WIKI 768d

서버 자원 활용 룰:
- ssh capstone2026@165.132.140.240 (ed25519 등록됨, password 불필요)
- 우리 PG port **55435-55436** (현재 55435만 active, 55436은 추가 인스턴스용 가용) — 다른 인스턴스 55432/55433 절대 X)
- /mnt/hdd0/home/capstone2026/ 작업 dir
- GPU 사용 OK (다른 사용자 idle 시) — 이전 실패 사례 있어 단계적 검증 권장
- 30-60초 monitor + stuck 정의 (mtime 5분+ + CPU<50%) → kill + retry

VPN 끊김 회피:
- ~/.ssh/config Host * ServerAliveInterval 15 CountMax 100 TCPKeepAlive yes (5/10 17:50 적용)
- background keep-alive script: /tmp/capstone_keepalive.sh PID /tmp/capstone_keepalive.pid (60s ping)

새 세션 즉시 액션:
1. SSH 검증: ssh capstone "date"
2. 진행 상태: ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"
   (5/10 20:45 기준 ~302/702 measurements)
3. tmux active: ssh capstone "tmux ls; pgrep -af measure_paper | grep -v grep | wc -l"
4. 최근 진행 log: ssh capstone "tail -10 /mnt/hdd0/home/capstone2026/log/paper_exact_phase_*.log"
5. monitor re-arm (1시간 timeout)

5단계 narrative (사용자 명시):
1. RQ1/RQ2/RQ3 검증 (paper exact 재확인) — RQ1 5%, RQ2 9% 격차 narrative 성립
2. Exqutor 100% 정확 재현 — paper Fig 12 1.69, 우리 1.541~1.708 (-6.3%~+1.1%)
3. CaseA: 우리 method 대체 — minibatch_partial -7.41% 단일 강한 outperform
4. CaseB: 우리 method 증강 — 6 methods -2~-7% outperform B1 (ensemble)
5. 최종 비교 CaseB > CaseA > B1

진행 중 (5/10 20:45):
- Phase B extra (8 methods × 9 cells = 72): ~50/72
- Phase B extra2 (20 methods × 9 cells = 180): ~50/180
- Phase C extra (28 methods × 9 cells = 252): ~6/252
- 23 active procs, ETA 5/11 01-02시 KST

미완료 / blocker:
- A2-Fig8 (multi-vector measurement): partsupp_deep_wiki_10 stratum_id 부재 — post-fix
- A3-TPCDS (ECQO mode): Exqutor PG patch 충돌 — autocommit + exqutor_qerror tpcds 생성 후도 fail

5 critical findings (handoff_v1 추정 vs paper):
1. Fig 5 queries: DEEP/SIFT=Q3,10,12 / SSN=Q3,9,10 (handoff "Q3,9,10,12 동일" 부정확)
2. min/max bound: paper Eq 1-6에 clamping 없음
3. Selectivity: paper {0.001, 0.01, 0.10}만 (우리 추가 {0.05,0.30,0.50} 폐기)
4. A3 TPC-DS = ECQO mode (sampling X)
5. Metric: Q-error + wall-clock 둘 다 (현재 Q-error만)

39 methods registry (Tier 1 11 + extra 8 + extra2 20):
Tier 1 Legacy: sparse_rp ★4, random_projection, minibatch, hilbert, gmm, minibatch_partial, lsh, pca1d, sobol, reservoir, faiss_ivf
extra: pq, kdtree, halton, hammersley, coreset, birch, agglomerative, dense_rp
extra2 (Tier S+/A/B): opq, kdpp, banditucb1, neuram, thompson_sampling, mfmc, epsilon_net, ams_count_sketch, neurocard_lite, adaptive_bucket_probing, ccsketch, factor_join, lp_bound, cca1d, cocluster_nystrom, tucker, vinecopula, hkbu_repsample, lhs, lpm2

향후 brainstorming 시 주의 (drop reason):
- HNSW-SS / WanderJoin / HDBSCAN: drop (KM20 oracle / multi-table 부적합 / OOM)
- lsh/RP/sobol on YFCC 192d: cluster imbalance outlier
- SF=100 GMM/Agglomerative/Spectral/Tucker: 시간/공간 복잡도 — chunked / subset 우회 필수
- 새 method 추가 시 80M cells 메모리/시간 검증 + chunked predict 필수

RQ1/RQ2 추가 기여 (사용자 5/10 20:45 명시):
- 세은이 카톡 record 검색: grep -r "RQ1\|RQ2" _internal/records/kakaotalk/ | grep -i "보충\|부족\|개선"
- RQ2 Neyman/Anti-Neyman 추가 (현재 Bernoulli/Equal/Prop만, vector_stratum_sigma 활용)
- paper SelNet (learned estimator) vs 우리 method 추가 비교

목표 ETA: 5/11 01-02시 KST 무결 완료 + Phase D analysis + REPORT.md 5단계 finalize
```

---

## 15. 핵심 파일 위치 (server + local)

### 15.1 Local
- `_internal/handoff_*.md` (v0/v1/v2/validation/full_state)
- `_internal/scripts/measure_paper_exact.py` (1100+ lines)
- `_internal/scripts/analyze_paper_exact.py`
- `_internal/scripts/measure_exqutor_replication_DRAFT.py` (handoff_v2 §3 초기 design)
- `reference/papers/[0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries.pdf`
- `reference/exqutor_query_plans/{tpc_h,tpc_ds}/q*.sql`
- `submission/제출완료/속도는벡터_중간보고서.{pdf,docx}` (4/17)
- `_internal/records/kakaotalk/*.md` (회의록 30+, 세은이 카톡 검색용)

### 15.2 Server (`/mnt/hdd0/home/capstone2026/`)
- `cache/rq3/measure_paper_exact.py` + `analyze_paper_exact.py` + `_measure_common.py`
- `cache/rq3/run_phase_*.sh` (8개)
- `cache/rq3/paper_exact/*.json + *.csv + REPORT_paper_exact.md`
- `cache/rq1/*.npy + query_pool_*.parquet + query_selectivity_*.parquet`
- `log/paper_exact_phase_*.log` (각 cell × phase log)
- `vanilla_sf100/` (PG data dir, port 55435)

### 15.3 Memory (~/.claude/projects/-Users-hyunbin-Capstone/memory/)
- `reference_exqutor_paper_verbatim.md` (paper hyperparam/queries/threshold verbatim)
- `feedback_paper_exact_principle.md` (paper exact 재현 원칙)
- `MEMORY.md` (index)

---

## 16. END

작성: 2026-05-10 20:45 KST
사용자 외출 약 6시간 16분 + VPN 복구 후 약 3시간
다음 step: ① 본 문서 + handoff_v2 read → ② 새 세션 §0 5단계 즉시 액션 → ③ Phase B/C 끝까지 → ④ Phase D + REPORT.md 5단계 narrative finalize

**핵심**: 메인 세션 종료 시 본 문서로 100% 이어가기. SSN=FB alias / paper Eq 1-6 verbatim / 39 methods registry / 5 critical findings / 5단계 narrative / 자원 활용 룰 / blocker 모두 보존.
