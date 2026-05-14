# A2-Fig8 Multi-Vector Measurement Patch (paper exact)

**작성**: 2026-05-10 22:50 KST
**unblocker session 산출** (handoff §1.4 §7.3 §10.1 후속)

## 개요

A2-Fig8 (paper Fig 8, DEEP+WIKI partsupp 4-way schema) measurement는 두 가지 경로 가능:

- **옵션 1 (unblocker, 본 세션 빌드 완료)**: deep-only single-vec 측정 (A2-Fig9와 동일 방식)
  - NPY symlink만으로 즉시 측정 가능
  - paper Fig 8 의 deep-vector 부분만 capturing → narrative 단축
- **옵션 2 (정확 multi-vec)**: dual-predicate (DEEP AND WIKI) measurement
  - 본 patch에서 design — 별도 implementation 필요

## 옵션 1 — 빌드된 NPY symlinks (본 세션 완료)

```bash
# server: /mnt/hdd0/home/capstone2026/cache/rq1/
ls -la partsupp_deep_wiki_10*.npy
# vectors -> /mnt/hdd0/home/capstone2026/cache/rq3/partsupp_deep_wiki_10_emb1.npy (8M × 96d, DEEP)
# strata  -> /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_deep_10_strata.npy   (8M, KM20 0~19)
# pks     -> /mnt/hdd0/home/capstone2026/cache/rq1/partsupp_deep_10_pks.npy
```

### 검증

- partsupp_deep_wiki_10 emb1 ≡ partsupp_deep_10 vectors (numpy.allclose 3 sample 통과)
- 두 테이블 PK range 동일 (1~2M part × 1~100K supp), row count 동일 (8M)
- ordering 동일 → strata.npy 그대로 reuse 가능

### Smoke 측정 결과 (5/10 22:43-22:45 KST)

```bash
python3 measure_paper_exact.py --rq 3 --phase A --cell A2-Fig8 --mode B1 \
    --n-queries 100 --trials 2 --output /tmp/a2_fig8_smoke
```

- NPY-only fast path 진입 (84.3s 로드, 3GB)
- B1 trial 1: avg_qe=1.705, finite=97/100, final_size=389
- B1 trial 2: avg_qe=1.805, finite=99/100, final_size=405
- avg_q_error_trimmed=1.755 — paper Fig 6 normalized 영역
- final_size_mean=397 (paper "DEEP stable ~358" 영역)

→ measurement loop 정상 동작, paper Fig 8 측정 즉시 launch 가능

### 메인 launch command

```bash
# A2-Fig8 B1
python3 measure_paper_exact.py --rq 3 --phase A --cell A2-Fig8 --mode B1 \
    --n-queries 1000 --trials 10 --output /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact

# A2-Fig8 CaseA (각 method 마다 — 22 method 권장)
python3 measure_paper_exact.py --rq 3 --phase B --cell A2-Fig8 --mode CaseA \
    --method minibatch --n-queries 1000 --trials 10 \
    --output /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact

# A2-Fig8 CaseB (각 method 마다 ensemble)
python3 measure_paper_exact.py --rq 3 --phase C --cell A2-Fig8 --mode CaseB \
    --method minibatch --n-queries 1000 --trials 10 \
    --output /mnt/hdd0/home/capstone2026/cache/rq3/paper_exact
```

## 옵션 2 — 정확 multi-vec (별도 patch design)

### 핵심 차이

paper Fig 8의 *진짜* 측정은 multi-vec query:
```sql
SELECT count(*) FROM partsupp_deep_wiki_10
WHERE ps_embedding_deep <-> qvec_deep < t_deep
  AND ps_embedding_wiki <-> qvec_wiki < t_wiki;
```

옵션 1(deep-only)은:
```sql
SELECT count(*) FROM partsupp_deep_wiki_10
WHERE ps_embedding_deep <-> qvec_deep < t_deep;
```

→ deep AND wiki 의 cardinality가 deep 단독 cardinality 보다 훨씬 작음 (selectivity 곱)
→ Bernoulli sampling 효율 + Adaptive convergence 패턴이 다름

### 옵션 2 patch 위치

`measure_paper_exact.py`에 새 함수 3개 추가:

1. `measure_b1_paper_dual(cell, ...)` — B1 dual-vec
2. `measure_case_a_dual(cell, method_name, ...)` — CaseA dual-vec
3. `measure_case_b_dual(cell, method_name, ...)` — CaseB dual-vec

### Implementation skeleton

```python
def _load_dual_vecs(cell: CellSpec):
    """A2-Fig8 only: emb1 + emb2 NPY 직접 load (concat이 아닌 dual)."""
    if cell.sub != "A2-Fig8":
        raise ValueError("dual measurement only supported for A2-Fig8")
    e1 = np.load("/mnt/hdd0/home/capstone2026/cache/rq3/partsupp_deep_wiki_10_emb1.npy")  # 96d
    e2 = np.load("/mnt/hdd0/home/capstone2026/cache/rq3/partsupp_deep_wiki_10_emb2.npy")  # 768d
    sids = np.load("/mnt/hdd0/home/capstone2026/cache/rq1/partsupp_deep_10_strata.npy")   # KM20 on deep
    return e1, e2, sids

def _build_dual_query_pool(e1, e2, n_queries=1000, sel=0.01, seed=1234):
    """measure_multi_5mode.py의 build_query_pool 준용 — paper Fig 8 sel=0.01 quantile.
    
    Returns: qids, q1, q2, D1_vec, D2_vec, true_card_dict
    """
    # measure_multi_5mode.py:264 build_query_pool 그대로 reuse 가능
    ...

def measure_b1_paper_dual(cell, n_queries=1000, trials=10, output_dir=None):
    """A2-Fig8 dual B1: emb1 + emb2 양쪽 모두 hit threshold + AdaptiveState."""
    e1, e2, km20_sids = _load_dual_vecs(cell)
    s1, s2, sizes = _cache_dual_samples(e1, e2, km20_sids)  # measure_multi_5mode.py:243 reuse
    qids, q1, q2, D1_vec, D2_vec, true_card = _build_dual_query_pool(e1, e2, n_queries)
    
    # Trial loop — AdaptiveState dual estimator
    for trial_idx in range(trials):
        rng = np.random.default_rng(trial_idx * 13 + 7)
        state = AdaptiveState()  # paper Eq 1-6 그대로
        q_errs = []
        for q_idx in range(n_queries):
            qi = q_idx % len(qids)
            qid = qids[qi]
            tc = true_card[(int(qid), 0.01)]  # paper sel=0.01
            # Bernoulli dual at AdaptiveState.size (measure_multi_5mode.py:336 reuse)
            est = bernoulli_estimate_dual(s1, s2, sizes, q1[qi], q2[qi],
                                           D1_vec[qi], D2_vec[qi], rng, budget=state.size)
            q_err = q_error(est, tc)
            q_errs.append(q_err)
            state.update(q_err, state.size / total_rows)
        ...

def measure_case_a_dual(cell, method_name, ...):
    """A2-Fig8 dual CaseA: method-specific stratification on emb1+emb2 concat."""
    e1, e2, km20_sids = _load_dual_vecs(cell)
    # method strata on concat([e1 || e2])
    concat = np.concatenate([
        e1 / np.linalg.norm(e1, axis=1, keepdims=True).mean(),
        e2 / np.linalg.norm(e2, axis=1, keepdims=True).mean()
    ], axis=1)
    method_sids = _get_method_strata(method_name, concat)  # 기존 함수 reuse
    s1, s2, sizes = _cache_dual_samples(e1, e2, method_sids)
    ...
    # measurement loop — stratified_estimate_dual
```

### 메인 launch (옵션 2 patch 후)

```bash
# 새 mode 추가 필요: 'B1-dual', 'CaseA-dual', 'CaseB-dual'
python3 measure_paper_exact.py --rq 3 --phase A --cell A2-Fig8 --mode B1-dual \
    --n-queries 1000 --trials 10
```

## 옵션 1 vs 옵션 2 결정

| 비교 | 옵션 1 (deep-only) | 옵션 2 (dual) |
|---|---|---|
| 빌드 비용 | 0 (symlink만, 완료) | ~50 lines patch + 1 mode arg |
| 측정 정확도 | paper Fig 8의 일부 capturing | paper Fig 8 정확 재현 |
| 비교 narrative | A2-Fig9와 동일 (단일 deep-vec) | "multi-vec에서도 우리 ensemble 효과" |
| 시간 (cell 별) | ~30분 (B1+CaseA+CaseB) | ~45분 (sample fetch 추가, dual estimator overhead) |
| 권고 | unblocker 즉시 launch | 본 세션 후 paper exact narrative 정합 위해 |

## 권고 sequence

1. **즉시**: 옵션 1로 A2-Fig8 B1+CaseA(11 method)+CaseB(11 method) launch
   - 메인 세션 측정과 병렬 실행 가능 (다른 cell 영향 X)
   - ~6시간 소요 estimate
2. **차후 (본 세션 종료 후)**: 옵션 2 patch 구현 + 측정
   - paper Fig 8 narrative 정합 위해 필요
   - 옵션 1 결과와 비교 → "deep-only로도 narrative consistent" 또는 "dual에서 효과 다름" 확인

## 다음 step

사용자 confirm:
- [ ] 옵션 1 즉시 launch 승인
- [ ] 옵션 2 patch 우선순위 (W1 sprint 내 / W2로 deferral)
- [ ] 메인 세션 22 procs와의 자원 경합 estimation (3GB load × 1 fast path → 영향 미미 expectation)
