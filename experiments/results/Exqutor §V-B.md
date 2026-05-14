# Algorithm 1 — §V-B Adaptive Sampling (Exqutor) — B1 baseline 의사코드

> 본 doc 은 reviewer attack defense **B1** (5/10 handoff_v0 §5.4) 대응 — Phase F B1 baseline 의 §V-B Adaptive Sampling 식 1~6 을 의사코드로 명시. Exqutor 본 논문을 그대로 구현했는지 reviewer 가 확인 가능하도록 제공.
>
> Source: Exqutor: Extended Query Optimizer for Vector-augmented Analytical Queries (arXiv:2512.09695v2) §V-B + 식 (1)~(6)

---

## Algorithm 1: Adaptive Sampling for vector cardinality estimation

```
Inputs:
  q          ∈ ℝ^d      — query vector embedding
  τ          ∈ ℝ_+      — distance threshold (target selectivity)
  T = {x_i}_{i=1..N}    — table of vector embeddings
  Hyperparameters: m, η₀, α, β, γ, P, N₀, N_max, ε

Outputs:
  μ̂_n        — point estimate of selectivity p* = E_x[1{d(q,x) ≤ τ}]
  σ̂²_n       — estimated variance
  n          — final sample size

Steps:
  1.  S ← Bernoulli sample of size N₀ from T          (unstratified)        ⟵ Eq. (1)
  2.  μ̂₀ ← (1/|S|) Σ_{x∈S} 1{d(q,x) ≤ τ}                                    ⟵ Eq. (2)
  3.  σ̂²₀ ← μ̂₀(1 − μ̂₀)                                                     ⟵ Bernoulli variance
  4.  v₀ ← 0,  t ← 0
  5.  while convergence not met AND n < N_max:                              ⟵ Eq. (3) loop
  6.      Δ_t ← (μ̂_t − μ̂_{t-1}) / (|μ̂_{t-1}| + ε_safe)                       (relative grad)
  7.      v_t ← m · v_{t-1} + (1 − m) · Δ_t                                 ⟵ Eq. (4) momentum
  8.      η_t ← η₀ · γ^{⌊t / P⌋}                                            ⟵ Eq. (5) lr decay
  9.      μ̂_t ← μ̂_{t-1} + η_t · v_t                                         ⟵ Eq. (5) update
 10.      n_inc ← N₀ · max(1, β · σ̂²_t / α)                                 ⟵ Eq. (6) batch size
 11.      Sample n_inc more rows via Bernoulli, refresh μ̂_t and σ̂²_t
 12.      if t mod P == 0:  check |μ̂_t − μ̂_{t-1}| / μ̂_{t-1} < ε  ⇒  break
 13.      t ← t + 1
 14.  return μ̂_n, σ̂²_n, n
```

Notes:
- **Unstratified Bernoulli** (Step 1, 11) — i.i.d. random sampling without distribution-aware partitioning. This is the precise gap our distribution-aware stratification (Phase F B4) augments.
- **KNN scope only** — Exqutor §V-B explicitly limits Algorithm 1 to single-table KNN queries ("specifically for KNN queries"). Multi-table joint distribution (our extended scope) is *not* addressed.
- **N₀ = 385** comes from Cochran (1977) §4.5 sample-size table at 95% confidence ±5% margin for a binomial proportion — i.e., the minimum sample size that yields ±5% half-width 95% CI under unstratified Bernoulli regardless of N (as long as N ≫ 385).

---

## Hyperparameter table (Exqutor §V-B values, our B1 baseline matches verbatim)

| Symbol | Name                | Value  | Reference          | Comment                                           |
|--------|---------------------|--------|--------------------|---------------------------------------------------|
| `m`    | momentum            | 0.9    | Exqutor §V-B Eq.4  | matches Adam-style first-moment estimator         |
| `η₀`   | initial learning rate | 0.1  | Exqutor §V-B Eq.5  | base rate before exponential decay                |
| `α`    | curriculum bandwidth | 50    | Exqutor §V-B Eq.6  | controls batch-size growth rate vs σ̂²            |
| `β`    | variance penalty    | 1.5    | Exqutor §V-B Eq.6  | upweights high-variance regions                   |
| `γ`    | lr decay            | 0.99   | Exqutor §V-B Eq.5  | per-period decay (γ^{t/P})                        |
| `P`    | update period       | 50     | Exqutor §V-B Eq.5  | queries between lr / convergence checks           |
| `N₀`   | initial sample size | 385    | Cochran 1977 §4.5  | 95%/±5% binomial half-width                       |
| `N_max`| max sample size     | 5000   | our cap (resource) | empirically suffices for sel ≥ 0.01 in our cells  |
| `ε`    | convergence tol     | 1e-3   | Exqutor §V-B       | relative change threshold                         |

---

## Implementation cross-reference

| Algorithm 1 step                | Code reference                                                 |
|---------------------------------|----------------------------------------------------------------|
| Step 1 (Bernoulli S)            | `_internal/scripts/run_adaptive_sampling.py` — `bernoulli_init` |
| Step 2 (initial μ̂₀)             | same — `mean_indicator()`                                      |
| Step 4 (momentum init)          | same — `velocity = 0.0`                                        |
| Step 7 (momentum update)        | same — `velocity = m*velocity + (1-m)*grad`                    |
| Step 8 (lr decay)               | same — `lr = lr0 * (gamma ** (t // period))`                   |
| Step 9 (μ̂ update)               | same — `mu += lr * velocity`                                   |
| Step 10 (batch size)            | same — `n_inc = N0 * max(1, beta * var / alpha)`               |
| Step 12 (convergence check)     | same — `|mu_t - mu_prev| / mu_prev < tol`                      |

Server-side measurement script: `cache/rq3/run_adaptive_sampling.py` (B1 baseline). All 9 hyperparameters above are exposed as CLI flags (`--momentum`, `--lr0`, `--alpha`, `--beta`, `--gamma`, `--update-period`, `--init-N`, `--max-N`, `--tol`) — measurement reproducibility verifiable by reading parquet `meta.json`.

---

## Why this matters (reviewer attack defense)

Without Algorithm 1 box, a reviewer can challenge:

> "Did you implement Exqutor §V-B *exactly* as described? Without an algorithm box matching the paper's equations 1–6, your B1 baseline could differ in subtle ways (e.g., variance estimator, lr schedule, convergence criterion) — invalidating the paired comparison."

This box answers each line of the equations 1–6 with code reference (table above), reproducible hyperparameter values matching the paper verbatim, and explicit mention of *which scope* the algorithm covers (single-table KNN only — our extension is the multi-table generalization).

---

## END

작성: 2026-05-10 KST
참조: Exqutor §V-B (arXiv:2512.09695v2) + Phase F B1 baseline (`run_adaptive_sampling.py`)
