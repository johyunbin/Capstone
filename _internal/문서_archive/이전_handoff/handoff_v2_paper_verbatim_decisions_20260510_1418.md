# Handoff v2 — paper verbatim 검증 결과 + 사용자 결정 필요 (5/10 14:18 KST)

> **사용자 외출 중 (5/10 13:36 ~ ~5/11 복귀)**
> 본 handoff = handoff_v1 §1.4 점검 list 통과 결과 + 5 critical decisions + 진행 상태.
> 사용자 명시 핵심 제약: "paper 모든 항목 완전 똑같이 진행. 단 하나라도 다르면 안 됨."

---

## 0. TL;DR (사용자 복귀 즉시 read)

### 0.1 paper verbatim 추출 완료 — handoff_v1 vs paper 차이 5건

| # | 항목 | handoff_v1 추정 | paper verbatim | 결정 권고 |
|---|---|---|---|---|
| 1 | Fig 5 queries | 모든 dataset Q3/Q9/Q10/Q12 동일 | DEEP/SIFT = **Q3,10,12** (3개) / SimSearchNet++ = **Q3,9,10** (3개) | paper 따라 정정 |
| 2 | min/max bound | "min=355, max=415 강제" | **paper Eq 1-6에 clamping 없음** (Fig 6 trace는 자연 수렴값) | bound 제거 (Eq 1-6 그대로) |
| 3 | Selectivity scope | 우리 기존 {0.05, 0.30, 0.50} 등 | paper Fig 13 = **{0.1%, 1%, 10%} only** | 우리 추가 폐기 → {0.001, 0.01, 0.10}만 |
| 4 | A3 TPC-DS mode | sampling replace/augment 적용 가정 | paper Fig 10 = **"with vector indexes"** = ECQO mode (sampling X) | A3는 ECQO mode 별도 분기, CaseA/CaseB 적용 X |
| 5 | Metric | Q-error (cardinality) | paper Fig 5 caption = "Query execution time" (wall-clock) | Q-error + wall-clock 둘 다 capture (paper 둘 다 reporting) |

### 0.2 paper에서 신규 확보된 정확 정보 (handoff_v1 미기재)

- **Vector range threshold (TPC-H 8 queries verbatim)**: `<-> 'image_embedding' < 0.86` (DEEP 96d, 8 queries 통일)
- **Vector range threshold (TPC-DS 7 queries verbatim)**:
  - Q7, Q12, Q20, Q72: `< 1.08`
  - Q19, Q42: `< 1.20`
  - Q98: `< 1.30`
- **Sample size formula (Eq 1)**: `N = ⌈z² · P̂(1-P̂) / e²⌉ = ⌈1.96² × 0.5 × 0.5 / 0.05²⌉ = 385`
- **Schema (paper §IV-B verbatim)**: partsupp gets `ps_image_embedding` + `ps_text_embedding` + `ps_tag` / part gets `p_text_embedding` / item (TPC-DS) gets `i_embedding`
- **Hardware**: Intel Xeon Gold 6530, 128 vCPUs, 1.0 TB RAM (verbatim)
- **PostgreSQL setting**: `max_worker_processes = 8` / DuckDB `worker_threads = 128`

### 0.3 SSH publickey 차단 상황 (5/10 14:14 발현)

```
ssh capstone "..." → Permission denied (publickey,password)
```
- 로컬 ed25519 key (`hyunbin@Mac-mini.local`)가 server `~/.ssh/authorized_keys` 에 미등록
- BatchMode → password prompt 차단 (사용자 외출 중 입력 불가)
- **server-side 측정 진행 불가** — 사용자 복귀 시 SSH 복구 후 측정 시작

복구 절차 (사용자 복귀 시):
```bash
# 옵션 A: 비번 1회 입력하면 계속 진행 가능
ssh capstone   # password 입력 → 이후 ssh-agent 활용

# 옵션 B: 영구 등록
ssh-copy-id -i ~/.ssh/id_ed25519.pub capstone
```

### 0.4 진행 상태 (5/10 14:18 KST)

- ✅ Phase 0 §1.4 점검 list **6/7 통과**
  - [x] paper 1-15 page 모두 정독 (agent 1)
  - [x] Fig별 setup 추출 완료 (agent 1)
  - [x] §1.3 변수 모두 verbatim 확인
  - [x] 우리 setup vs paper 차이 list 작성 (5 critical findings)
  - [x] paper 외 추가 항목 명시 폐기 (사용자 결정 필요)
  - [x] paper 정확 재현 measurement script 설계 (paper exact 적용)
  - [ ] 점검 후 작업 시작 (이전 X) ← **사용자 복귀 시 confirm 받고 시작**
- ✅ Exqutor github query_plans/ 클론 → `reference/exqutor_query_plans/` 복사 완료
- ⛔ server SSH 차단 → Phase A/B/C/D 측정 진행 X (사용자 복귀 시까지 대기)
- ✅ 로컬 작업 진행: handoff_v2 + measure_exqutor_replication.py 설계 (코드만, 실행 X)

---

## 1. 5 critical decisions 상세 (사용자 confirm 필요)

### Decision 1: Fig 5 queries 정정

**paper p.8 Fig 5 image x-axis verbatim 확인** (agent 1):

| Dataset | Queries (paper Fig 5) | handoff_v1 추정 | 차이 |
|---|---|---|---|
| DEEP (SF=100) | Q3, Q10, Q12 | Q3, Q9, Q10, Q12 | **Q9가 paper에 없음** |
| SIFT (SF=100) | Q3, Q10, Q12 | Q3, Q9, Q10, Q12 | **Q9가 paper에 없음** |
| SimSearchNet++ (SF=100) | Q3, Q9, Q10 | Q3, Q9, Q10, Q12 | **Q12가 paper에 없음** |

**paper p.4 §IV TPC-H 8-query list verbatim**: Q3, Q5, Q8, Q9, Q10, Q11, Q12, Q20 (Fig 4 ECQO 실험만 8개 모두 사용)

**Fig 5 sampling experiment에선 8개 중 3개씩만 선별** (dataset마다 다름).

**결정 권고**: paper 따라 dataset별 분리:
- A1-DEEP: Q3, Q10, Q12 (3 queries)
- A1-SIFT: Q3, Q10, Q12 (3 queries)
- A1-SSN: Q3, Q9, Q10 (3 queries)
- 합계 9개 measurement (3 datasets × 3 queries)

### Decision 2: min/max bound 제거 (Eq 1-6 그대로)

**paper p.6 Eq 1-6 verbatim** (agent 1):

```
N        = ⌈z²·P̂(1-P̂)/e²⌉ = 385                    (1) initial
δ        = α·(Q-error - β) - (100-α)·sampling_ratio (3)
V_t      = m·V_{t-1} + η_t·δ                        (4) momentum
size_{t+1} = size_t + V_t                           (5) update
η_{t+1}  = γ·η_t                                    (6) decay
```

- **clamping logic 없음** (`min(max_size, max(min_size, x))` 같은 boundary 없음)
- Fig 6 trace 안정값 (~358 DEEP / ~415 SIFT / ~362 SSN) = **자연 수렴값**, hard bound X

**결정 권고**: handoff_v1 §1.3 "min_size=355, max_size=415 paper Fig 6 한계 강제" 폐기. Eq 1-6 그대로 (자연 수렴 trust).

### Decision 3: Selectivity scope = paper {0.001, 0.01, 0.10} only

**paper p.10 Fig 13 verbatim** (agent 1):

> "Figure 13 shows the query execution time of both pgvector and Exqutor under the sampling-based estimation method, evaluated at three different selectivity levels: **0.1%, 1%, and 10%**."

- paper Fig 13 = **3 selectivity levels only** (0.1%, 1%, 10%)
- Fig 5/6/7/8/9/10/14는 모두 single selectivity (sampling-based = 1%, index-based = 200 vectors)

**결정 권고**:
- 우리 기존 {0.05, 0.30, 0.50} 폐기 (paper에 없음)
- A4 selectivity ablation에서만 {0.001, 0.01, 0.10} 측정
- A1/A2/A3/A5는 single selectivity = 1% (paper default)

### Decision 4: A3 TPC-DS는 ECQO mode (sampling replace/augment X)

**paper p.9 Fig 10 caption verbatim** (agent 1):

> "Query execution time for TPC-DS VAQs **with vector indexes** on the DEEP using pgvector and Exqutor (SF10)."

- "with vector indexes" → ECQO 측정 (HNSW range query를 cardinality estimator로 사용)
- §V-B sampling은 vector index 없는 경우만 적용
- 즉 Fig 10에서는 **sampling step replace/augment 의미 X**

**우리 5단계 narrative 영향**:
- Phase 2 Exqutor B1 정확 재현: A3는 ECQO 모드 (HNSW range query 1~2ms)
- Phase 3 CaseA (sampling replace): A3 적용 X (sampling 자체가 없음)
- Phase 4 CaseB (sampling augment): A3 적용 X

**결정 권고**: A3 (TPC-DS Fig 10) 별도 분기:
- mode = ECQO (HNSW range query baseline)
- 비교 대상 = pgvector default heuristic (33.3%) vs ECQO
- 우리 method 비교 X (sampling 영역 외)
- A1/A2/A4/A5는 그대로 sampling mode 3-way (B1 / CaseA / CaseB)

### Decision 5: Metric = Q-error + wall-clock 둘 다

**paper Fig 5/6/13 caption verbatim**: "Query execution time" (wall-clock)
**paper Eq 2 verbatim**: `Q-error = max(C_est/C_true, C_true/C_est)` (cardinality accuracy)

paper는 두 metric 모두 reporting:
- Q-error: §VI-D Table II + Fig 12 narrative ("avg Q-error 1.69")
- Wall-clock: Fig 4/5/7/8/9/10/12/13/14 (모두 execution time)

**우리 RQ3 = cardinality estimation accuracy = Q-error 영역**.
**paper exact 재현은 wall-clock 영역**.

**결정 권고**: 두 metric 모두 capture
- **Q-error**: 모든 measurement (B1, CaseA, CaseB) 의 Q-error 측정 (Eq 2)
- **Wall-clock (선택)**: A1 + A4 만 EXPLAIN ANALYZE 추가 (전체 적용 시 측정 시간 ×3)
- A2/A3/A5는 Q-error만 (시간 압박 시)

---

## 2. 새 measurement matrix (paper exact 적용)

### 2.1 Phase A: Exqutor B1 baseline (paper 정확 재현)

| Sub | Paper Fig | Datasets | SF | Queries | Selectivity | Mode |
|---|---|---|---|---|---|---|
| **A1-DEEP** | Fig 5/6 | DEEP | 100 | Q3, Q10, Q12 (3) | 1% (threshold 0.86) | sampling 3-way (B1/CaseA/CaseB) |
| **A1-SIFT** | Fig 5/6 | SIFT | 100 | Q3, Q10, Q12 (3) | 1% | sampling 3-way |
| **A1-SSN** | Fig 5/6 | SimSearchNet++ | 100 | Q3, Q9, Q10 (3) | 1% | sampling 3-way |
| **A2-Fig7** | Fig 7 | YFCC + tag | 10 | Q3,5,8,9,10,11,12,20 (8) | (paper threshold) | sampling 3-way |
| **A2-Fig8** | Fig 8 | DEEP+WIKI partsupp | 10 | Q3,5,8,9,10,11,12,20 (8) | (paper threshold) | sampling 3-way |
| **A2-Fig9** | Fig 9 | DEEP+WIKI cross | 10 | Q3,5,8,9,10,11,12,20 (8) | (paper threshold) | sampling 3-way |
| **A3-TPCDS** | Fig 10 | DEEP item_deep | 10 | Q7,12,19,20,42,72,98 (7) | threshold 1.08/1.20/1.30 | **ECQO mode (no sampling)** |
| **A4-sel** | Fig 13 | DEEP | 100 | Q3, Q10, Q12 (3) | **{0.1%, 1%, 10%}** | sampling 3-way |
| **A5-scale** | Fig 14 | DEEP | 1, 10, 100 | Q3, Q5, Q20 (3) | (paper threshold) | sampling 3-way |

**총 sub-experiment cells**: A1 9 + A2 24 + A3 7 + A4 9 + A5 9 = **58 cells**
- Sampling 3-way (B1/CaseA/CaseB) 적용: 9+24+9+9 = 51 cells
- ECQO mode: 7 cells

### 2.2 Phase B: CaseA (replace) 34 methods

51 sampling cells × 34 methods = **1,734 measurements** (sampling step replace)
- 각 cell마다 100 trial × 10-trimmed mean = 100 query × 8 sample = 800 estimation per method
- 합계 ~1.4M estimations

### 2.3 Phase C: CaseB (augment) 34 methods

51 sampling cells × 34 methods × ensemble (B1 + method) = **1,734 measurements** + B1 baseline weight tuning

### 2.4 Phase D: paired Δ% 분석

(B1 vs CaseA), (B1 vs CaseB), (CaseA vs CaseB) × 51 cells × 34 methods × Wilcoxon + BH-FDR

---

## 3. measure_exqutor_replication.py 설계 (paper exact)

### 3.1 핵심 spec

```python
PAPER_HYPERPARAM = {
    "z": 1.96,           # 95% confidence (Eq 1)
    "P_hat": 0.5,        # proportion estimate (Eq 1)
    "e": 0.05,           # margin of error (Eq 1)
    "N_init": 385,       # initial sample size (Eq 1 result)
    "m": 0.9,            # momentum coefficient (Eq 4)
    "eta_0": 0.1,        # initial learning rate (Eq 4)
    "alpha": 50,         # δ weighting factor (Eq 3)
    "beta": 1.5,         # target Q-error (Eq 3)
    "gamma": 0.99,       # learning rate decay (Eq 6)
    "update_period": 50, # update every 50 queries
    # min_size, max_size: paper에 없음 → clamping 제거
}

PAPER_HNSW = {"M": 16, "ef_construction": 200, "ef_search": 400}

PAPER_QUERIES = {
    "tpc_h": ["q3", "q5", "q8", "q9", "q10", "q11", "q12", "q20"],
    "tpc_h_threshold": 0.86,  # all 8 queries (DEEP 96d)
    "tpc_ds": {
        "q07": 1.08, "q12": 1.08, "q19": 1.20, "q20": 1.08,
        "q42": 1.20, "q72": 1.08, "q98": 1.30,
    },
}

PAPER_SELECTIVITIES = [0.001, 0.01, 0.10]  # Fig 13 only

PAPER_MEASUREMENT = {
    "trials": 10,
    "trim": "lowest+highest",  # 8 runs avg
    "warmup": 1,
    "max_worker_processes": 8,  # PostgreSQL
    "worker_threads": 128,      # DuckDB (참고용)
}
```

### 3.2 AdaptiveState class (Eq 1-6 verbatim)

```python
class AdaptiveState:
    """Paper Eq 1-6 verbatim. NO min/max clamping (Eq 1-6에 없음)."""
    def __init__(self):
        self.size = 385          # Eq 1
        self.m = 0.9             # Eq 4
        self.eta = 0.1           # Eq 4 (initial)
        self.alpha = 50          # Eq 3
        self.beta = 1.5          # Eq 3
        self.gamma = 0.99        # Eq 6
        self.V_prev = 0.0        # momentum t-1
        self.iter = 0

    def update(self, q_error: float, sampling_ratio: float) -> int:
        """Update sample size after every 50 queries (paper §VI-B)."""
        self.iter += 1
        if self.iter % 50 != 0:
            return self.size
        # Eq 3: delta
        delta = self.alpha * (q_error - self.beta) - (100 - self.alpha) * sampling_ratio
        # Eq 4: momentum
        V_t = self.m * self.V_prev + self.eta * delta
        # Eq 5: size update (NO clamping)
        self.size = max(1, int(self.size + V_t))  # >= 1 guard only
        self.V_prev = V_t
        # Eq 6: decay
        self.eta = self.gamma * self.eta
        return self.size
```

### 3.3 Modes

```python
def measure_cell(cell_spec, mode, method=None):
    """
    Args:
        cell_spec: A1-A5 sub-experiment + dataset + SF + Q + selectivity
        mode: 'B1' / 'CaseA' / 'CaseB' / 'ECQO'
        method: 34 method registry (CaseA/CaseB만)
    Returns:
        {'q_error': float, 'wall_clock_ms': float, 'sample_size': int}
    """
    if mode == 'B1':
        # Bernoulli sampling N=385 (initial) → AdaptiveState
        # paper §V-B exact
        ...
    elif mode == 'CaseA':
        # method가 sampling step 대체 (385 sample 추출 X, method 직접 cardinality estimate)
        ...
    elif mode == 'CaseB':
        # B1 + method ensemble (가중 평균 또는 fallback)
        ...
    elif mode == 'ECQO':
        # HNSW range query (vector index 활용)
        # A3 TPC-DS만
        ...
```

### 3.4 Validation (dry-run)

paper Fig 6 trace 비교:
- DEEP: stable point ~358-365
- SIFT: stable point ~410-415
- SSN: stable point ~362
- 우리 dry-run trace가 paper trace와 ±5% 이내 → validation pass

---

## 4. 진행 sequence (사용자 복귀 후)

### Step 0: 사용자 confirm 받기 (5 decisions)

상기 §1 의 5 decisions 사용자가 OK 하면 다음 진행. NO 면 폐기 후 재설계.

### Step 1: SSH 복구 (5분)

```bash
ssh capstone   # password 1회 입력
# 또는
ssh-copy-id -i ~/.ssh/id_ed25519.pub capstone
```

### Step 2: server side 사전 setup (1-2h)

1. Exqutor query_plans/ 서버 복사: `scp -r reference/exqutor_query_plans capstone:/mnt/hdd0/home/capstone2026/`
2. tpcds DB SF 확인 + (필요 시) tpcds-kit dsdgen SF=10 재생성
3. item_deep 테이블 생성 + DEEP base.1B.fbin 첫 ~100K rows binding + HNSW index
4. partsupp_deep_*_sf{1,10,100} HNSW index 빌드 상태 확인 (M=16, ef_c=200)

### Step 3: measure_exqutor_replication.py 작성 + dry-run (2-3h)

- AdaptiveState class implementation
- Fig 6 trace validation (DEEP/SIFT/SSN convergence trace 비교)
- 통과 시 본 measurement 진입

### Step 4: Phase A (B1 baseline) measurement (5-8h)

- A1 (9 cells) + A2 (24 cells) + A3 (7 cells, ECQO) + A4 (9 cells) + A5 (9 cells)
- 순차 1 procs, OMP_NUM_THREADS=128
- 1분 monitor + stuck 즉시 처리

### Step 5: Phase B (CaseA replace) measurement (10-15h)

51 sampling cells × 34 methods (1,734 measurements)

### Step 6: Phase C (CaseB augment) measurement (10-15h)

51 sampling cells × 34 methods × ensemble

### Step 7: Phase D + REPORT.md (3-5h)

paired Δ% + Wilcoxon + BH-FDR + 5단계 narrative

**Total ETA (사용자 복귀 후)**: ~30-50h → 5/12 ~ 5/13 finalize

---

## 5. 사용자 외출 동안 로컬 진행 (server 차단)

server 측정 X 가능. 다음만 진행:

1. ✅ paper 정독 + verbatim 추출 (agent 1, 완료)
2. ✅ Exqutor github query_plans/ 클론 + Capstone 복사 (완료)
3. ✅ handoff_v2 작성 (이 file)
4. 🔄 measure_exqutor_replication.py 설계 (코드만, 실행 X)
5. 🔄 work-log + memory 갱신
6. (선택) Capstone CLAUDE.md 새 변수 갱신

**측정은 사용자 복귀 + SSH 복구 후 시작** — handoff_v1 §0 "돌아왔을 때 실험 정확히 진행 중" 요건은 SSH 차단으로 충족 불가. 대신 paper exact 적용한 설계 완료 + 사용자 confirm 즉시 measurement 시작 가능 상태.

---

## 6. 새 measurement dirs 위치

```
server: /mnt/hdd0/home/capstone2026/cache/rq3/
  ├── exqutor_replication_phase_a/   # B1 baseline (paper exact)
  ├── exqutor_replication_phase_b/   # CaseA replace
  ├── exqutor_replication_phase_c/   # CaseB augment
  └── exqutor_replication_phase_d/   # paired Δ% analysis

local: /Users/hyunbin/Capstone/experiments/results/exqutor_replication/
  └── (rsync after measurement)
```

기존 결과 (RQ1/RQ2/RQ3 검증, max=5000) — `cache/rq3/multi_paradigm_*, multi_ensemble, phase_f_v2_full, phase_f_v3` 보존.

---

## 7. END

작성: 2026-05-10 14:18 KST (외출 중)
다음 step: 사용자 복귀 시 §1 5 decisions confirm + SSH 복구 + Step 2~7 sequential.

**핵심**:
- paper 100% 정확 재현 = handoff_v1 추정 5건 폐기 (Fig 5 Q9, min/max bound, sel {0.05/0.30/0.50}, A3 sampling, Q-error only)
- paper 신규 발견 5건 추가 (threshold 0.86/1.08/1.20/1.30, schema spec verbatim, hardware spec verbatim)
- SSH 차단으로 server 측정 진행 X — 복귀 시 1회 password 입력으로 복구
- 로컬에서 measure_exqutor_replication.py 설계 진행 중

**비가역 0** (paper 정독 + 보고서 작성만, server 변경 X)
