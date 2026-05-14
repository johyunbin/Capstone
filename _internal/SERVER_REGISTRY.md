# SERVER_REGISTRY.md — Server Resource Inventory

> 작성: 2026-05-11 01:40 KST  
> 출처: handoff_main_session_FULL_STATE §4-§5 + handoff_v4 §3-§4 + 채림님 메일 (5/10 14:30) verbatim  
> 사용자 명시: 우리 PG port 55435-55436 / GPU 사용 OK / tmux 다중 OK / 다른 인스턴스 절대 X

---

## 0. TL;DR — Server 핵심 정보

| 항목 | 값 |
|---|---|
| IP | 165.132.140.240 |
| 계정 | capstone2026 |
| 비밀번호 | bdai1234! (ssh-copy-id 5/10 14:30 등록 — password 불필요) |
| 작업 dir | `/mnt/hdd0/home/capstone2026/` (다른 dir 작업 X) |
| PG port | **55435 active** / 55436 가용 |
| 다른 인스턴스 (절대 X) | 55432, 55433 |
| Hardware | Intel Xeon Gold 6530, 128 vCPUs, 1.0 TB RAM, 4× NVIDIA RTX 6000 Ada 49GB |
| Disk | /mnt/hdd0 13 TB, 11 TB used (89%), 1.4 TB 여유 |
| 측정 진행 (5/11 01:10) | ~316/702 + Phase 4 launch 대기 |
| 자동 chain monitor | `bdrhrddyb` (sigma + RQ2 5-way + 분석 2차) |

---

## 1. SSH 접속 (handoff_main §4.1 verbatim)

### 1.1 기본 명령
```bash
# 기본 (ed25519 등록됨, password 불필요)
ssh capstone2026@165.132.140.240
# alias 사용 가능 (handoff_main §4.1)
ssh capstone
```

### 1.2 ~/.ssh/config 강화 (5/10 17:50 적용)
```
Host *
    ServerAliveInterval 15
    ServerAliveCountMax 100
    TCPKeepAlive yes
```
→ 1500초 timeout 허용. VPN 일시 단절 (이전 17:30~17:39 9분 사례) 회피.

### 1.3 Background keep-alive (handoff_main §4.1)
```bash
# /tmp/capstone_keepalive.sh — 60s 간격 SSH ping
PID 99488 (5/10 17:50 launch)
PID file: /tmp/capstone_keepalive.pid
```

### 1.4 VPN
- 사용자 측 활성 — 끊기면 SSH timeout
- 5/10 17:30~17:39 9분 끊김 사례 (외출 중) → keep-alive script 도입 후 회피

---

## 2. 작업 디렉토리 + DB

### 2.1 절대 경로
```
/mnt/hdd0/home/capstone2026/
├── cache/
│   ├── rq1/        ← NPY cache + query_pool / query_selectivity parquet (~150 GB)
│   └── rq3/        ← measure_paper_exact.py + analyze_paper_exact.py + paper_exact 결과
├── log/            ← paper_exact_phase_*.log + sigma_build_paper_exact_*.log + rq2_paper_exact_5way_*.log
├── vanilla_sf100/  ← PG data dir (port 55435)
├── ...
```

### 2.2 PG instance
- **55435 active**: vanilla_sf100 → wns41559 DB (TPC-H)
- **55436 가용**: 별도 인스턴스 빌드 가능 (채림님 룰 — 사용자 명시 미사용)

### 2.3 DB list (handoff_main §4.2 verbatim)
- wns41559 (TPC-H base + DEEP/SIFT/SSN partsupp)
- tpcds (TPC-DS SF=10)
- tpcds100 (TPC-DS SF=100)
- imdbload, postgres, template{0,1}

### 2.4 핵심 tables (handoff_main §4.3)

**TPC-H base 8 × SF=1/10/100 = 24 tables**:
customer, lineitem, nation, orders, part, region, supplier, partsupp

**Vector tables (HNSW 빌드 완료)**:
- partsupp_{deep,sift,fb}_{1,10,100} — 9 tables (DEEP/SIFT/SSN)
- partsupp_{yfcc,wiki}_{1,10} — 4 tables
- part_wiki_10 (WIKI 768d)
- partsupp_deep_wiki_10 (4-way schema, Fig 8) — ⚠️ stratum_id 컬럼 부재
- partsupp_deep_sift_10 (multi DEEP+SIFT)
- customer_sift_10 (SIFT 128d, RQ1/RQ2 기존 setup)
- items_100 (TPC-H items, paper 무관)

**보조 tables**:
- vector_stratum_sigma — KM20 σ_j 사전 계산 (RQ2 Neyman/Anti 활용)
- exqutor_qerror — Exqutor patched PG 자동 lookup (wns41559 + tpcds DB)

### 2.5 SSN ↔ FB ↔ SimSearchNet++ alias 핵심 (handoff_main §3.2)

⚠️ **놓치기 쉬운 결정적 detail**:
- paper 표기 = **SimSearchNet++** (SSN)
- server table = **`partsupp_fb_*`** (FB = Facebook AI 출처)
- query_pool 파일 = **`query_pool_SSN_sf*.parquet`** (SSN)
- 우리 코드 (measure_paper_exact.py): `dataset="SimSearchNet++"`, `table="partsupp_fb_{sf}"`, alias map: `"SimSearchNet++": "SSN"`

**5/10 결정** (handoff_state _current §0): 모든 문서·발표·논문 단일 표기 = **SSN (SimSearchNet++)**, server 측 `fb_*` 파일명은 5/10 morning batch rename 예정 (현재 미진행).

---

## 3. 측정 데이터 위치

### 3.1 NPY cache (`/mnt/hdd0/home/capstone2026/cache/rq1/`)

```
partsupp_{deep,sift,fb}_{1,10,100}_{vectors,strata,pks}.npy   ← 9 tables × 3 file = 27 NPY
query_pool_{DEEP,SIFT,SSN,YFCC,WIKI}_sf{1,10,100}.parquet     ← 100 query × 5 sel 캘리브레이션
query_selectivity_{DEEP,...}_sf{1,10,100}.parquet             ← schema: query_id, selectivity, D_target, true_cardinality, actual_sel
```

⚠️ **calibrated selectivity = [0.01, 0.05, 0.1, 0.3, 0.5]** (5종) — paper {0.001, 0.01, 0.10}은 **0.001이 calibration 없음** (sel=0.001 빌드 후순위, 80M × 0.001 = 8000 rows out of 80M의 10x 작음).

### 3.2 측정 결과 (`/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/`)

**Phase A B1** (9 cells): A1-{DEEP,SIFT,SSN}_B1.json + A2-{Fig7,Fig9}_B1.json + A4-sel_B1.json + A5-scale-sf{1,10,100}_B1.json

**Phase B/C CaseA/CaseB** (~700+ files):
- Tier 1 Legacy 11 method × 9 cells × 2 modes = 198 ✅
- Phase B/C extra 28 NEW × 9 cells × 2 modes = 504 진행 中
- Q4 Tier 1 6 NEW × 9 cells × 2 modes = 108 진행 中
- Phase 4 11 NEW × 9 cells × 2 modes = 198 server scp 대기

**RQ1/RQ2 csv** (`paper_exact/rq{1,2}_paper_exact_*.csv`): DEEP/SIFT × Bern/KM20/Equal/Prop/Neyman/Anti

**REPORT** (`paper_exact/REPORT_paper_exact.md`): 자동 생성, 5단계 narrative auto-fill

### 3.3 Server side scripts (`/mnt/hdd0/home/capstone2026/cache/rq3/`)

| File | size | mtime (5/10 12:30+ KST 갱신) |
|---|---|---|
| `measure_paper_exact.py` | ~64 KB | 메인 measurement |
| `analyze_paper_exact.py` | 26 KB (md5 26f12822) | Phase D 분석 + 5단계 narrative |
| `_measure_common.py` | 21 KB (md5 1964d30b) | 공통 inf + 5-way modes |
| `compute_stratum_sigma_paper_exact.py` | 6326 bytes | 신규 (5/10 21:29) σ_j builder |
| `run_phase_*.sh` | 8개 | run_phase_b_full / extra / extra2 / cell / c / c_extra / sparse_rp_retry |
| `methods/` | 26 file | extra2 20 method 별 module |
| `method_phase4_extra.py` | 660 line | **server scp 대기 (handoff_v5)** |
| `run_phase_b_phase4.sh` | 5.2 KB | **server scp 대기** |
| `method_tier1_p9_p10.py` | 21 KB | active (Q4 Tier 1) |
| `sparserp/sparse_random_projection.py` | — | assign signature (matrix, vectors) |
| `offline_simple/random_projection.py` | — | assign 동일 signature |

### 3.4 Log (`/mnt/hdd0/home/capstone2026/log/`)
- `paper_exact_phase_*.log` — 각 cell × phase 별
- `sigma_build_paper_exact_20260510_1240.log` — 21:40 launch
- `rq2_paper_exact_5way_*.log` — 자동 chain 후 자동 생성

---

## 4. 자원 사용 (5/10 20:45 시점 + 5/11 01:10 update)

### 4.1 CPU
- 128 vCPU
- **5/10 20:45**: 23 active procs × 1.1 core ≈ 25 cores 사용 (~20%, 80% idle)
- **5/11 01:10 (handoff_v5)**: Phase 4 11 tmux 추가 = 32 procs 가능

### 4.2 RAM
- 1.0 TB total
- **5/10 20:45**: 509 GB used / 247 GB free / 264 GB buffer/cache (NPY page cache)
- **5/10 22:06**: sigma builder kill 후 60 GB → 204 GB 회복
- **5/10 21:44**: 1007 GB total / 142 GB available

### 4.3 GPU
- 4× NVIDIA RTX 6000 Ada 49 GB each
- 모두 **0% / 2 MiB idle** (CPU 측정 中, GPU 미활용)
- 사용자 명시 (5/10 15:03): "지피유든 다른세션 이용하든 ... 적극 이용 가능"
- ⚠️ 채림님 룰 (5/10 14:30 메일): "GPU 사용 자제" → 사용자 override 명시
- **GPU 활용 가능 영역** (handoff_main §5.3):
  - faiss-gpu: faiss IndexIVF / IndexPQ GPU 가속 (5-10× 빠름)
  - torch-cuda: NeurAM / NeuroCard MLP autoencoder
  - cuML: KMeans / DBSCAN GPU
- **이전 실패** (handoff_main §5.3): GPU activation OOM/CUDA error fallback (정확 상황 미기록 — 추후 retry 시 cuda_visible_devices + memory limit 확인)

### 4.4 Disk
- /mnt/hdd0 = 13 TB / 11 TB used (89%, 1.4 TB 여유)
- 채림님 sf100 처음 실행 느림 경고 (HDD 디스크) — sf10으로 테스트 권장

### 4.5 Load (5/10 21:44 기준)
- 1min = 39.97 / 5min = 56.24 / 15min = 51.40 (줄어드는 추세)

---

## 5. 자원 활용 룰 (사용자 + 채림님)

### 5.1 채림님 메일 (5/10 14:30 verbatim, handoff_main §5.1)
- 작업 dir = `/mnt/hdd0/home/capstone2026/` 만
- sudo 권한 X
- PG 인스턴스 = **55435-55436 포트만**
- 다른 인스턴스 / 포트 (55432, 55433) **절대 X** — 다른 사용자 작업 中
- GPU 사용 자제 (사용자 override 명시 — 다른 사용자 idle 시 OK)
- tmux 진행
- "캡스톤 집중 시즌 시 연구실 내 사용 스케줄 조율 필요"
- Exqutor 깃헙 클론 → pgvector / postgresql submodule 확인 (duckdb / big-ann-benchmark 안받아도 OK)
- log/ 디렉토리 만들어서 설정
- DB user/password = wns41559 / wns41559
- sf100 처음 실행 시 메모리 로드 시간 큼 → sf10으로 테스트 권장

### 5.2 사용자 명시 (5/10 15:03 + 20:11 + 20:45 + 5/11 01:05)
- 다른 인스턴스 포트 (55432, 55433) 절대 X
- 우리 포트 55435-55436만
- tmux 다중 세션 OK (현재 23+ tmux + Phase 4 launch 시 32+)
- GPU 사용 가능 (다른 사용자 idle 시)
- 다른 사용자 추정: postgres 55432 (319643/127176 PIDs) + 55433 (sihyunkim2) — 영향 X 한도

### 5.3 병렬 stuck 회피 (handoff_main §10.2 정의)
- log mtime **5분 이상** 갱신 X + procs CPU **< 50%** = stuck
- 즉시 처리: kill + 다음 cell sequential 재 launch
- 모니터: 30~60초 간격
- Monitor tool 1시간 timeout — 1시간마다 re-arm (5/10 20:45까지 ~5회 re-arm)

---

## 6. tmux 세션 list (handoff_main §13 verbatim, 5/10 20:45 + 5/11 01:10 update)

### 6.1 5/10 20:45 list (23+ tmux)
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
- pc_A1-* / pc_A2-Fig7 / pc_A2-Fig9 / pc_A4-sel / pc_A5-scale-sf{1,10,100} (Phase C Tier 1, sleep)
- pbe_A5-sf1/sf10/Fig9/Fig7/A1-DEEP/SIFT/SSN/sf100/A4-sel (Phase B extra, 진행)
- pbe2_A5-* (Phase B extra2, 진행)
- pce_A5-* (Phase C extra, 진행)
```

### 6.2 5/10 21:44 신규
- `sigma_build_pe` — compute_stratum_sigma_paper_exact.py 진행 중 (PID 3429378 wrapper / 3429380 python)
- `rq2_pe` — **자동 launch 예정** (sigma + 측정 완료 시)

### 6.3 5/11 01:10 launch 대기 (handoff_v5 §6)
- `pb_phase4` (Phase 4 11 method, --all)
- 또는 6 tmux 분할 (M1/M5/M6/M7/M9/M11 P0 + M2/M3/M4/M8/M10 P1)

---

## 7. Monitor 자동 chain 설정 (handoff_v4 §2 — 5/10 22:06 sigma kill + 재구성)

### 7.1 새 monitor (task `bdrhrddyb`, persistent)

Sequential chain:
- 측정만 모니터 (60s polling)
- `act=0` AND `cnt>300` 시 trigger:
  - **Step 1/4**: 분석 1차 (`python3 analyze_paper_exact.py` — Fig 12 영역 분리 + one-sided greater 적용)
  - **Step 2/4**: sigma builder launch (tmux `sigma_build_pe`) + 180s polling 대기 (자원 충분, 15-45분 예상)
  - **Step 3/4**: RQ2 5-way launch (tmux `rq2_pe`, `--rq 2`) + 180s polling 대기 (~30분)
  - **Step 4/4**: 분석 2차 (`python3 analyze_paper_exact.py` — RQ2 Neyman/Anti 데이터 포함)
  - COMPLETE break

### 7.2 monitor 끊겼을 시 재시작 (handoff_v4 §3)

```bash
# Monitor (Claude Code MCP) 재시작 명령:
# description: 측정+sigma persistent 모니터 — 완료 시 분석 + RQ2 자동 trigger
# timeout: 3600000ms, persistent: true
```

---

## 8. Vector range threshold (paper exact, reference/exqutor_query_plans/)

### 8.1 TPC-H 8 queries 통일
- `<-> 'image_embedding' < 0.86` (DEEP 96d 기준, 8 queries 모두)

### 8.2 TPC-DS verbatim (Exqutor github query_plans/ 5/10 14:20 클론)
- Q7, Q12, Q20, Q72: `< 1.08`
- Q19, Q42: `< 1.20`
- Q98: `< 1.30`

### 8.3 위치
- 로컬: `reference/exqutor_query_plans/{tpc_h,tpc_ds}/q*.sql` (5/10 14:20 클론)
- Server scp 대기 (handoff_v2 Step 2): `scp -r reference/exqutor_query_plans capstone:/mnt/hdd0/home/capstone2026/`

---

## 9. 진행 상태 (5/11 01:10 KST 추정)

### 9.1 메인 chain (handoff_v4 §4)
- Total measurement: ~316/702 (45%) → 5/11 01-02시 완료 ETA
- Active procs: 22 (5/10 21:44)
- 분당 ~+0.5건 (NPY fetch SF=100 22분 bottleneck)

### 9.2 Sigma build (handoff_v4 §4)
- 시작: 5/10 21:40:13
- 진행: DEEP sf=100 partsupp_deep_100 — 100 queries load 완료, stratum 0~19 cluster materialize
- ETA: 5/10 23~24시 KST (DEEP/SIFT/SSN 순차)
- log: `sigma_build_paper_exact_20260510_1240.log`

### 9.3 Phase 4 launch (handoff_v5 §0)
- ⏳ Server scp 대기 (method_phase4_extra.py + measure_paper_exact.py PATCH + run_phase_b_phase4.sh)
- ETA 통합 launch (Phase 4 11 + Q4 Tier 1 6 = 17 method × 9 cells × 2 modes = 306 cells):
  - Sequential: ~180-280 h
  - Parallel 6 tmux: ~30-50 h (~1.5-2일)

---

## 10. 발생 문제 + 해결 (handoff_main §10.1)

| 문제 | 해결 |
|---|---|
| PG recovery mode (2회) | 동시 fetch + Fig8 strata 빌드 시 PG crash → fig8 fetch kill + PG 자동 복구 (2분) |
| A1-SSN 9분 stuck | NPY fetch D-state (disk wait) → kill + 별도 tmux retry (정상) |
| VPN 끊김 (1회, 17:30~17:39 9분) | 사용자 외출 중 → background keep-alive script + ssh config 강화 |
| A2-Fig7 sparse_rp/random_projection 192d fail | signature swap → fix 후 retry (5/10 17:22) |
| A2-Fig8 stratum_id 부재 | post-fix 후순위 |
| A3-TPCDS ECQO PG crash | 후순위 (paper §V-A 영역 외) |
| YFCC 192d outliers (lsh/RP/sobol) | cluster imbalance — narrative 영향 X (다른 cells 정상) |
| sigma builder 27분 무진행 → kill (22:06) | NPY fancy indexing on 30GB mmap + 측정 procs 동시 access → 메모리 압박 — 측정 끝난 후 sequential 진행으로 변경 |

---

## 11. 핵심 fix 이력 (handoff_main §9.4)

| 일시 (KST) | fix |
|---|---|
| 5/10 14:49 | query_selectivity column: `d_target` → `D_target` (대문자), `true_card` → `true_cardinality` |
| 5/10 14:50 | trimmed_mean inf filter (Bernoulli hits=0 → est=0 → Q-error inf 회피) |
| 5/10 14:50 | AdaptiveState.update q_error inf cap=100 (size 폭증 방지, paper 명시 X) |
| 5/10 17:22 | sparse_rp / random_projection signature swap fix: `assign_*(matrix, vectors)` (96d 우연 통과, 192d fail) |
| 5/10 17:50 | ~/.ssh/config 강화 (ServerAliveInterval 15, CountMax 100, TCPKeepAlive yes) + background keep-alive script |
| 5/10 18:06 | GMM cholesky fail fix: `covariance_type='diag' + reg_covar=1e-2` (SIFT 128d / SSN 256d) |
| 5/10 21:48 | analyze_paper_exact.py validation 정정 (Fig 12 영역 분리 + one-sided greater + CASEA_OUTLIER_METHODS) |

---

## 12. 새 세션 SSH 즉시 검증 (handoff_v5 §0 + handoff_v4 §0)

```bash
# 1. SSH 검증
ssh capstone "date && pgrep -af measure_paper | wc -l"

# 2. 측정 진행
ssh capstone "ls /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact/*Case*.json | wc -l"

# 3. tmux 진행
ssh capstone "tmux ls | grep -E 'sigma_build_pe|rq2_pe|pb_'"

# 4. sigma 진행
ssh capstone "tail -10 /mnt/hdd0/home/capstone2026/log/sigma_build_paper_exact_*.log"

# 5. 자원 상태
ssh capstone "free -h | head -3 && nvidia-smi --query-gpu=memory.used --format=csv"
```

---

## 13. END

작성: 2026-05-11 01:40 KST  
다음 단계: CHANGELOG.md 작성  

**핵심**: server 작업은 read-only 우선 (메인 chain monitor + Phase 4 측정 영향 0). 변경 시 사용자 confirm 필수. SSN=FB=SimSearchNet++ alias 필수 인지.
