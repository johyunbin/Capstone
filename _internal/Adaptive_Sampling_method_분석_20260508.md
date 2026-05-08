# Exqutor Adaptive Sampling 정독 + 본 연구 4강 paired 비교 design

**작성**: 2026-05-08, 백그라운드 에이전트 E
**목적**: 5/8 19:30 회의 결정 (박세은 팀장 ⭐⭐⭐) — Exqutor 본 논문 Adaptive Sampling 과 본 연구 stratification 4강 (HDBSCAN / MB_partial / Hilbert / sparse RP) 의 직접 paired Δ% 측정 design
**Source**: [0] Exqutor; Extended Query Optimizer for Vector Augmented Analytical Queries (arXiv:2512.09695v2) PDF page 5–10 직접 정독 + [81] Lipton et al. SIGMOD 1990 보조

---

## 1. Exqutor Adaptive Sampling 알고리즘 정독

### 1.1 위치와 작동 조건

Exqutor 의 두 전략 중 **방법 B**, 즉 "벡터 인덱스 (HNSW) 가 없을 때" 에 한하여 활성화. ECQO (방법 A) 는 인덱스 기반이므로 본 연구의 stratification 비교 대상에서 제외 — 본 연구의 4강은 사전 cluster 학습이 필요한 stratified sampling 이므로 Adaptive Sampling 과 동일 환경 (no-index, full-scan) 에서만 fair 비교가 가능하다.

호출 시점: query planning 단계, 매 query 마다 한 번 호출. 호출 결과 = 카디널리티 추정값 → 옵티마이저 cost model 에 주입 → re-optimized plan 생성.

### 1.2 초기 sample size N (식 1)

$$N = \left\lceil \frac{z^2 \cdot \hat{P} \cdot (1 - \hat{P})}{e^2} \right\rceil$$

| 기호 | 의미 | Exqutor 기본값 |
|------|------|---------------|
| $z$ | 신뢰 수준 임계값 | 1.96 (95% CL) |
| $\hat{P}$ | 유사도 임계값 통과 비율 사전 추정 | 0.5 (max-variance) |
| $e$ | 허용 절대 오차 | 0.05 |

→ **N = 385**. 본 연구의 `SAMPLE_SIZE = 385` 와 정확히 일치 (`_measure_common.py` 60행). 동일 budget 비교 가능.

### 1.3 Q-error 지표 (식 2)

$$\text{Q-error} = \max\!\left(\frac{\text{Card}_{\text{esti}}}{\text{Card}_{\text{true}}},\, \frac{\text{Card}_{\text{true}}}{\text{Card}_{\text{esti}}}\right)$$

추정값과 실제 카디널리티 비율의 max → 1 에 가까울수록 정확. 본 연구의 `q_error` 컬럼과 정의 동일 (`_measure_common.py` 337행).

### 1.4 Adaptive update rule (식 3–6, 본 논문 Section V-B)

매 50 queries 마다 다음 업데이트:

$$\delta_t = \alpha \cdot (\text{Q-error}_t - \beta) - (100 - \alpha) \cdot \text{sampling\_ratio}_t \tag{3}$$

$$V_t = m \cdot V_{t-1} + \eta_t \cdot \delta_t \tag{4}$$

$$\text{sampling\_size}_{t+1} = \text{sampling\_size}_t + V_t \tag{5}$$

$$\eta_{t+1} = \gamma \cdot \eta_t \tag{6}$$

| Hyperparameter | 본 논문 Section VI | 의미 |
|----------------|------------------|------|
| $m$ (momentum) | 0.9 | 진동 억제 (Sutskever et al. 2013 인용) |
| $\eta_0$ (initial learning rate) | 0.1 | δ → ΔSampleSize 변환 게인 |
| $\alpha$ (weight) | 50 | Q-error 항의 기여도 |
| $\beta$ (target Q-error) | 1.5 | "허용" Q-error 임계값 |
| $\gamma$ (LR decay) | 0.99 | 반복마다 학습률 감쇠 |
| update period | 50 queries | sample_size 갱신 주기 |
| 초기 sample_size | 385 (식 1) | 첫 50 queries 까지 고정 |

**해석**: Q-error 가 β=1.5 보다 크면 δ > 0 → sample_size ↑ (정확도 회복). 작으면 δ < 0 → sample_size ↓ (오버헤드 절감). momentum 0.9 가 over-correction 억제, γ=0.99 로 long-run 수렴 보장. 본 논문 Figure 6 에 따르면 DEEP/SimSearchNet++ 는 약 200 query 후 ~358 까지 수렴하고 (385 → 감소), SIFT 는 ~415 까지 증가 (분포 복잡도 ↑).

### 1.5 Single vs multi-table

본 논문 Section V-B 의 implementation 노트: **"the optimizer maintains separate sample size states for each table"**. 즉 멀티 테이블 쿼리에서도 *테이블별로 독립* 의 sample_size 가 유지되며, 각 테이블의 vector predicate 마다 별도 Adaptive update loop 가 돌아간다. 본 연구의 single-table cell (10 cell) 에서는 *테이블 한 개 = state 한 개*, multi-table 일반화 측정에서는 partsupp / part 각각 state 를 두는 형태로 직접 매핑된다.

### 1.6 Reported accuracy / overhead (본 논문 Section VI)

- Adaptive vs Fixed: 최대 1.4× 추가 속도 향상 (Figure 5).
- Sampling overhead: 28~73 ms (full KNN scan 대비 무시 수준).
- Sample size convergence: dataset 별로 dataset-specific equilibrium (DEEP ~358, SIFT ~415).
- 단점 (Section VI-E): 고차원 (WIKI 768d) 에서는 거리 계산 비용으로 sampling overhead 증가, curse of dimensionality 로 인한 추정 정확도 저하.

---

## 2. 본 연구 stratification 과 paired 비교 설계

### 2.1 동일 측정 framework 매핑 표

| 차원 | 본 연구 4강 | Exqutor Adaptive | 비고 |
|------|------------|-----------------|------|
| Datasets | DEEP / SIFT (× SF1, SF10) | 동일 | `_measure_common.DATASETS` 그대로 |
| Selectivity | {0.01, 0.05, 0.10, 0.30, 0.50} | 동일 | `SELECTIVITIES` 그대로 |
| Seed | {0.1, 0.2, 0.3, 0.4, 0.5} | 동일 | `SEEDS` 그대로 |
| Query/cell | 100 | 동일 | `query_pool.parquet` 같은 ID |
| Sample budget | 385 (initial), allocation = equal | 385 (initial), Adaptive 동적 | 초기 동등 |
| Estimator | Stratified HT (식: $\hat{C} = \sum_i (n_i / s_i) \cdot k_i$) | Bernoulli (식: $\hat{C} = (N/s) \cdot k$) | 본 연구 4강 = stratified, Adaptive = unstratified Bernoulli |
| Cluster training | 학습 sample 1% (DEEP/SIFT 약 10K~15K row) | X (random global sample) | 4강만 학습 phase 존재 |

### 2.2 query_id paired alignment

본 연구 측정은 query_id 가 cell 별로 0~99 고정, D_target 도 (cell × selectivity) 마다 미리 결정된 `query_selectivity_*.parquet` 에서 읽음 (`_measure_common._load_query_pool`). Adaptive 측정도 *동일 query_id 시퀀스* 를 사용해 같은 D_target, 같은 query vector 로 추정 → paired Δ% 가능.

**매 query 단위 row 구조** (`_measure_common.run_method_measurement` 340행):
```
{dataset, mode, selectivity, seed, query_id, D_target, true_card, est, q_error}
```
이 스키마를 Adaptive 도 동일하게 산출 → analyze 단계에서 단순 inner-join (dataset, seed, sel, query_id) 으로 paired 가능.

### 2.3 "동일 sample budget" 정의 — 3 시나리오

본 design 에서는 **모드 A (free-vs-free)** 를 default 로 하고, **모드 B (Adaptive size 를 4강에 부여)** 를 sensitivity check 로 추가 측정한다 (overnight 안에 모두 수용 가능, 후술 §4).

| 모드 | Adaptive | 4강 | 의도 |
|------|----------|-----|------|
| **A. free** (default) | 동적 (385 → eq.) | 385 fixed equal alloc | 본 논문 보고 그대로 — 최대 capability 비교 |
| **B. matched** | 동적 (385 → eq.) | Adaptive 가 query t 에서 사용한 sample_size 동일 부여 | "같은 budget 이면 누가 정확한가" 엄밀 비교 |
| **C. fixed-385** | 385 고정 (Adaptive off) | 385 fixed | Bernoulli (N=385) baseline ↔ 4강 — RQ3 본 분석에서 이미 측정 완료 |

모드 C 는 이미 RQ3 W1 sprint 에서 끝났으므로 (Tier 1 17 method × 5 sel × 10 cell), Adaptive 의 "fixed 모드" 만 추가 measurement 로 산출하면 통합 분석 가능. 따라서 **신규 launch 는 모드 A 만 (~5h budget 핵심)**, 모드 B 는 시간 여유 시 stretch goal 로 둔다.

### 2.4 Δ% 계산 방식

Tier 1 17 method 분석에서 사용한 동일 정의:

$$\Delta\%_{\text{method}} = \frac{R_{\text{method}} - R_{\text{baseline}}}{R_{\text{baseline}}} \times 100$$

여기서 $R$ = recovery rate = $1 - \frac{\text{med}(|\text{est}/\text{true} - 1|)}{1}$ 의 paired query 평균. baseline = BERN random sampling (`_measure_common.bernoulli_estimate`).

**핵심 산출표** (목표):

| Cell | Adaptive Δ% (vs BERN) | HDBSCAN Δ% | MB_partial Δ% | Hilbert Δ% | sparse RP Δ% | 4강 winner – Adaptive |
|------|-----------------------|-----------|---------------|------------|--------------|----------------------|
| DEEP-SF1 | … | -8.04 (기존) | -7.63 | -7.54 | -7.13 | … |
| DEEP-SF10 | … | … | … | … | … | … |
| (10 cell) | … | … | … | … | … | … |

→ 만약 **4강 winner – Adaptive < 0** (즉 4강이 더 작은 q_error → Δ% 더 negative) → 본 thesis 의 "분포 인식 stratification 우위" 주장 정량 confirmation.

---

## 3. 측정 코드 design (`run_adaptive_sampling.py` 골격)

### 3.1 Adaptive Sampling estimator (in-memory, no-index full-scan 모사)

본 연구 측정은 PG 가 아닌 **in-memory simulation** (`fetch_all_vectors_safe` 로 vector 미리 fetch → 거리 계산은 numpy). Adaptive 도 동일 방식으로 단순화: 각 query 마다 random sample $s_t$ rows (현재 sample_size) → Bernoulli estimate. 이는 본 논문의 "no-index → full-scan 일부 sampling" 을 정확히 재현.

```python
# experiments/code/rq3/run_adaptive_sampling.py 골격 (실제 작성은 Step 2 Agent B)
"""
RQ3 Adaptive Sampling baseline — Exqutor 본 논문 (arXiv:2512.09695v2) Section V-B 구현.

본 연구의 stratification 4강 (HDBSCAN / MB_partial / Hilbert / sparse RP) 와 paired
비교 가능한 형태로, _measure_common.py 의 측정 framework 와 호환되는 row schema 산출.
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _measure_common import (  # noqa: E402
    DATASETS, SAMPLE_SIZE, SEEDS, SELECTIVITIES,
    fetch_all_vectors_safe, kst, save_parquet_meta,
)

# ---------------------------------------------------------------------------
# Adaptive state (식 3~6 구현)
# ---------------------------------------------------------------------------

@dataclass
class AdaptiveState:
    sample_size: float = float(SAMPLE_SIZE)  # 식 1: N=385 from initial
    velocity: float = 0.0                    # V_t
    learning_rate: float = 0.1               # η_t
    momentum: float = 0.9                    # m
    alpha: float = 50.0                      # α
    beta: float = 1.5                        # target Q-error
    gamma: float = 0.99                      # η decay
    update_period: int = 50                  # queries
    min_size: int = 50                       # 안전 하한 (논문 명시 X, 발산 방지)
    max_size: int = 5000                     # 안전 상한 (총 row 보다 작게)
    n_total: int = 0                         # 누적 query count
    qerror_window: list[float] = None        # 최근 50 query 의 q_error

    def __post_init__(self):
        if self.qerror_window is None:
            self.qerror_window = []

    def step(self, qerror: float | None) -> int:
        """매 query 마다 호출. update_period 마다 sample_size 업데이트.
        Returns: 다음 query 에서 사용할 sample_size (int).
        """
        self.n_total += 1
        if qerror is not None and np.isfinite(qerror):
            self.qerror_window.append(qerror)

        if self.n_total % self.update_period == 0 and self.qerror_window:
            mean_qe = float(np.mean(self.qerror_window))
            sampling_ratio = self.sample_size / self.max_size  # 논문 표기 sampling_ratio
            # 식 3
            delta = self.alpha * (mean_qe - self.beta) - (100 - self.alpha) * sampling_ratio
            # 식 4
            self.velocity = self.momentum * self.velocity + self.learning_rate * delta
            # 식 5
            self.sample_size = self.sample_size + self.velocity
            self.sample_size = float(np.clip(self.sample_size, self.min_size, self.max_size))
            # 식 6
            self.learning_rate = self.gamma * self.learning_rate
            # 윈도우 reset
            self.qerror_window.clear()
        return int(round(self.sample_size))


# ---------------------------------------------------------------------------
# Bernoulli estimator (본 논문 no-index → 단순 random sample · 카디널리티 외삽)
# ---------------------------------------------------------------------------

def adaptive_bernoulli_estimate(all_vecs: np.ndarray, qvec: np.ndarray, D: float,
                                 sample_size: int, rng: np.random.Generator) -> int:
    """all_vecs 에서 sample_size 만큼 무작위 샘플 → 거리 계산 → 외삽."""
    n = all_vecs.shape[0]
    s = min(int(sample_size), n)
    idxs = rng.choice(n, size=s, replace=False)
    sub = all_vecs[idxs]
    d = np.linalg.norm(sub - qvec, axis=1)
    hits = int((d < D).sum())
    return hits * (n / s)


# ---------------------------------------------------------------------------
# 측정 main loop — _measure_common.run_method_measurement 와 호환되는 row schema 산출
# (단, query 순서를 강제 = (sel, seed, query_id) 정렬 — Adaptive state 가 stateful 이라
#  병렬 sel × seed 내 순차 update 로 결정론적 재현 보장)
# ---------------------------------------------------------------------------

def run_adaptive_measurement(all_vecs, ds, *, n_queries=100, fixed_size=False) -> list[dict]:
    """
    fixed_size=True 면 Adaptive off (sample_size = 385 고정). 본 연구의 RQ3 BERN baseline 과 동치.
    """
    import pyarrow.parquet as pq
    qp = pq.read_table(ds["query_pool"]).to_pandas().reset_index(drop=True)
    qs_full = pq.read_table(ds["query_sel"]).to_pandas()
    qvecs = np.stack([np.asarray(qp.iloc[i]["embedding"], dtype=np.float32)
                      for i in range(len(qp))])

    rows = []
    method = "adaptive_fixed" if fixed_size else "adaptive_sampling"
    for sel in SELECTIVITIES:
        qs_sel = qs_full[(np.isclose(qs_full["selectivity"], sel)) &
                         (qs_full["query_id"] < n_queries)] \
                  .sort_values("query_id").reset_index(drop=True)
        for seed in SEEDS:
            seed_int = int(seed * 10**9) % (2**31 - 1)
            rng = np.random.default_rng(seed_int)
            state = AdaptiveState(max_size=min(5000, len(all_vecs)))
            sample_size = SAMPLE_SIZE  # 첫 query 는 385
            for _, row in qs_sel.iterrows():
                qid = int(row["query_id"])
                D = float(row["D_target"])
                true_card = int(row["true_cardinality"])
                qvec = qvecs[qid]
                s_used = SAMPLE_SIZE if fixed_size else sample_size
                est = adaptive_bernoulli_estimate(all_vecs, qvec, D, s_used, rng)
                qerr = max(est / true_card, true_card / est) if (est > 0 and true_card > 0) else None
                rows.append({
                    "dataset": ds["name"], "mode": method, "selectivity": sel,
                    "seed": seed, "query_id": qid, "D_target": D,
                    "true_card": true_card, "est": est, "q_error": qerr,
                    "sample_size_used": s_used,  # Adaptive 분석용 추가 컬럼
                })
                if not fixed_size:
                    sample_size = state.step(qerr)
    return rows


def main():
    ap = argparse.ArgumentParser(description="Exqutor Adaptive Sampling 측정")
    ap.add_argument("--out-prefix", default="rq3_adaptive_sampling")
    ap.add_argument("--datasets", nargs="*", default=None)
    ap.add_argument("--n-queries", type=int, default=100)
    ap.add_argument("--fixed-size", action="store_true",
                    help="Adaptive off — sample_size=385 고정 (본 연구 BERN 재현용)")
    args = ap.parse_args()

    use_datasets = DATASETS if not args.datasets else [d for d in DATASETS if d["name"] in args.datasets]
    print(f"[{kst()}] === Exqutor Adaptive Sampling — fixed_size={args.fixed_size} ===")

    all_rows = []
    t_total = time.time()
    for ds in use_datasets:
        print(f"\n[{kst()}] === {ds['name']} ===")
        all_vecs, _ = fetch_all_vectors_safe(ds)
        rows = run_adaptive_measurement(all_vecs, ds,
                                         n_queries=args.n_queries,
                                         fixed_size=args.fixed_size)
        all_rows.extend(rows)

    save_parquet_meta(all_rows, prefix=args.out_prefix, extra_meta={
        "method": "Exqutor Adaptive Sampling (Section V-B, arXiv:2512.09695v2)",
        "hyperparameters": {"m": 0.9, "eta0": 0.1, "alpha": 50, "beta": 1.5,
                            "gamma": 0.99, "update_period": 50, "init_N": 385},
        "fixed_size": args.fixed_size,
        "n_queries": args.n_queries,
        "elapsed_s": round(time.time() - t_total, 1),
    })
    print(f"\n[{kst()}] total elapsed {time.time() - t_total:.1f}s")


if __name__ == "__main__":
    main()
```

### 3.2 CLI launch 예시

```bash
# 단일 cell (DEEP-SF1) Adaptive 측정 — smoke test
python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_adaptive_sampling.py \
    --datasets DEEP --out-prefix rq3_adaptive_DEEP_SF1 \
    > logs/adaptive_DEEP_SF1_$(date +%Y%m%d_%H%M).log 2>&1

# 전체 10 cell overnight launch (단일 process, 순차 cell)
python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_adaptive_sampling.py \
    --out-prefix rq3_adaptive_baseline_20260508 \
    > logs/adaptive_baseline_20260508.log 2>&1 &

# Adaptive off (fixed=385) — 본 연구 BERN 재현 sanity check
python3 /mnt/hdd0/home/capstone2026/cache/rq3/run_adaptive_sampling.py \
    --fixed-size --out-prefix rq3_adaptive_fixed_sanity \
    > logs/adaptive_fixed_sanity_20260508.log 2>&1
```

### 3.3 정합성 검증 (Step 2 Agent B 수행)

1. **fixed=True sanity**: `rq3_adaptive_fixed_sanity.parquet` 의 `q_error` 분포가 기존 `rq3_random20.parquet` 의 BERN mode 와 paired 동일해야 함 (random sample 로직 동치). Δ < 0.5%p 면 OK.
2. **state convergence**: meta.json 에 cell 별 마지막 sample_size 기록 → 본 논문 Figure 6 (DEEP ~358, SIFT ~415) 와 ±10% 이내면 reproduction OK.
3. **paired join**: Adaptive 결과 + 4강 결과를 (dataset, sel, seed, query_id) 로 inner-join → row count = 10 cell × 5 sel × 5 seed × 100 query = 25000 일치.

---

## 4. 5h overnight launch plan

### 4.1 측정 규모 산정

- 단일 10 cell × Adaptive × 5 sel × 5 seed × 100 query = **2500 estimation × 5 sel = 12500 measurement** (cell 당 2500).
- 비교: 기존 4강 단일 cell 측정 시간 (`run_minibatch_partial.py`, `run_hilbert.py` 의 reported elapsed) ≈ 30 min/cell (fetch 5–7 min + 측정 25 min).

### 4.2 cell 당 추정 시간

본 연구의 Adaptive 측정은 stratification 학습 phase 가 없으므로 *fetch + estimation only*:

| 단계 | DEEP-SF1 | DEEP-SF10 | SIFT-SF1 | SIFT-SF10 | 비고 |
|------|----------|-----------|---------|-----------|------|
| fetch (vector load) | 5 min | ~50 min | 7 min | ~70 min | KM20 cluster fresh-conn |
| estimation (5 sel × 5 seed × 100 q) | 8 min | ~30 min | 12 min | ~45 min | 매 query random sample 385 + dist |
| **cell total** | ~13 min | ~80 min | ~19 min | ~115 min | |

10 cell 합계 (DEEP/SIFT/SSN/WIKI/YFCC × SF1/SF10): SF1 5 cell × ~15 min + SF10 5 cell × ~95 min = **75 min + 475 min = ~550 min ≈ 9.2 h**.

→ **5h budget 안에 수용 불가**. 우선순위 cut 필요.

### 4.3 우선순위 launch plan (5h cap)

**Phase 1 (3h, 5/8 22:00–01:00)**: SF1 5 cell (DEEP/SIFT/SSN/WIKI/YFCC) — overnight 안전 zone
- 약 75 min, 단일 process 순차 → 단일 HDD IO 경합 회피
- 산출: `rq3_adaptive_SF1.parquet` (5 cell × 12500 row = 62500)

**Phase 2 (2h, 5/9 01:00–03:00)**: DEEP-SF10 + SIFT-SF10 (~115 min × 2 = 230 min) — *동시 2 process 병렬 (HDD IO 경합 허용 한계)*
- 본 연구의 RQ3 W1 sprint 에서 검증된 동시성 한계 = 2 cell (HDD 1개)
- SSN-SF10 / WIKI-SF10 / YFCC-SF10 는 5/9 daytime 으로 deferred

**Phase 3 (deferred to 5/9 09:00+)**: SSN/WIKI/YFCC-SF10 3 cell — 추가 ~290 min, 자문 대기 중 background

### 4.4 동시 실행 가능 cell 수

`feedback_session_topology.md` (메모리) 와 W1 sprint 경험에 따르면:
- HDD 1개 IO 경합 → ≤ 2 cell 동시 (3 cell 부터 fetch 단계에서 throughput 50% 이하로 떨어짐)
- PG socket 충돌 → fetch 시간 한정 1 cell 권장, estimation phase 는 in-memory 라 2 cell OK

**권장 schedule**: Phase 1 = 1 cell at a time (안전), Phase 2 = 2 cell 병렬 (DEEP-SF10 + SIFT-SF10). 두 SF10 cell 의 fetch 가 HDD 단일 thread 로 ~10 min 간격 staggered 이면 충돌 회피.

### 4.5 실패 시 fallback

| 실패 시나리오 | 감지 | 조치 |
|-------------|------|------|
| 특정 cell 의 fetch 실패 (PG socket 누수) | log 의 "psycopg.OperationalError" | 해당 cell 만 `--datasets <CELL_NAME>` 로 재실행, parquet append |
| Adaptive state 발산 (sample_size > 5000) | log 의 sample_size > max_size clip 경고 | β=1.5 가 dataset 에 too tight → β=2.0 으로 재실행 (sensitivity slot 으로 분류) |
| paired alignment 깨짐 (query_id mismatch) | analyze 단계 inner-join row count < 25000 | `query_pool*.parquet` hash 검증, 필요시 cell 재측정 |
| overnight 5h 초과 | 03:00 까지 Phase 2 미완 | Phase 2 강제 kill, daytime 재개 |

### 4.6 산출물 위치

```
서버 /mnt/hdd0/home/capstone2026/cache/rq1/
  rq3_adaptive_SF1.parquet                  Phase 1 산출
  rq3_adaptive_SF1_meta.json
  rq3_adaptive_DEEP_SF10.parquet            Phase 2-a
  rq3_adaptive_SIFT_SF10.parquet            Phase 2-b
  rq3_adaptive_fixed_sanity.parquet         3.3 §1 검증용 (선택)

로컬 logs/
  adaptive_baseline_20260508.log            전체 종합 log
  adaptive_DEEP_SF10_20260509.log           Phase 2-a
  adaptive_SIFT_SF10_20260509.log           Phase 2-b
```

### 4.7 분석 단계 (5/9 daytime, 별도 session)

`experiments/code/local_analysis/analyze_adaptive_vs_4kang.py` (Step 3 Agent C 작성):
1. 4강 parquet (`rq3_hdbscan.parquet`, `rq3_minibatch_partial.parquet`, `rq3_hilbert.parquet`, `rq3_sparse_rp.parquet`) 와 Adaptive parquet inner-join.
2. cell × method 별 paired Δ% 계산 (BERN baseline 동일).
3. paired CI 95% (bootstrap 1000) → "4강 winner – Adaptive" delta 의 0 포함 여부 검증.
4. 본 논문 Figure 6 reproduction: cell 별 sample_size 시계열 plot.

---

## 부록 A: 본 연구 4강과 Adaptive 의 알고리즘 카테고리 차이

| 차원 | Adaptive Sampling | 본 연구 4강 |
|------|------------------|-----------|
| 분포 인식 | X (uniform random sample) | O (cluster id 기반 stratified) |
| 학습 cost | 0 (online tuning only) | 1% sample 학습 (~1 min) |
| 동적 조정 | sample_size 만 조정 | stratum 분배 (equal alloc) 고정, 학습은 1회 |
| State | per-table sample_size + velocity | per-table cluster centroids |
| 본 thesis 위치 | "분포 무지" → 본 연구 baseline 의 **상한** | "분포 인식" 우위 정량 입증 대상 |

본 연구의 thesis: **"distribution-aware stratification (4강) 이 distribution-agnostic adaptive sampling (Exqutor) 보다 paired Δ% 에서 우위"**. 이를 검증하는 직접 측정이 본 design 의 목표.

---

**작성**: 2026-05-08, 백그라운드 에이전트 E (analysis only — 실제 코드는 Step 2 Agent B)
**Output destination**: `/Users/hyunbin/Capstone/_internal/Adaptive_Sampling_method_분석_20260508.md`
**Next step**: Step 2 Agent B 가 본 §3 골격 → 실제 `experiments/code/rq3/run_adaptive_sampling.py` 구현, 5/8 22:00 launch.
