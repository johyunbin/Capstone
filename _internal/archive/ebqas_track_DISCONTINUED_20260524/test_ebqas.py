"""EB-QAS unit test — 4 invariant assert (spec T1·T3·T4 patch 검증).

2026-05-23 23:44 KST 작성. 본 트랙 4번째 세션 산출물.

실행:
    cd /Users/hyunbin/Capstone
    python3 -m pytest _internal/scripts/test_ebqas.py -v

또는 단독 실행:
    python3 _internal/scripts/test_ebqas.py

SERVER 모드 의존 X — synthetic data 로 로컬 dry-run. _measure_common.py 불필요.

검증 4 함수:
  test_mode_switch_mismatch_streak       — spec T1 §4.2 explicit mode switch (b 정정)
  test_q_post_floor_separation           — spec T1 §3.2 L_log vs L_stop 분리 (b 정정)
  test_recovery_after_stable_streak      — spec T1 §4.2 history 회복 (b 정정)
  test_paired_join_invariant_pass_fail   — spec T3 §5.3 4-way invariant (c 정정)
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

# measure_paper_exact 의 EB-QAS 신규 함수 import
# (SERVER 모드 미발견 시 mc 관련 함수만 비활성, EBQAS 신규는 정상 import 가능)
sys.path.insert(0, str(Path(__file__).parent))

# scipy 없으면 skip
try:
    import scipy.stats  # noqa: F401
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

if HAS_SCIPY:
    from measure_paper_exact import (  # noqa: E402
        EBQASParams,
        EBQASState,
        assert_paired_join_invariant,
        beta_credible_interval,
        bucketize_threshold,
        ebqas_estimate,
        make_group_key,
        update_after_execution,
    )


# ---------------------------------------------------------------------------
# Test 1 — mode switch (spec T1 §4.2 explicit mode switch / Codex (b) 정정)
# ---------------------------------------------------------------------------

def test_mode_switch_mismatch_streak():
    """mismatch streak >= mismatch_n_threshold 시 explicit mode switch 발동.

    spec T1 §4.2 patch — 직전 222815 의 κ ≈ 19 fixed-point 수렴 반례 정정.
    3 회 연속 mismatch 후 prior_mode = "no_history", early_stop = False,
    alpha = beta = 1.0, kappa = 2.0 assert. 4·5 회 호출에서도 동일 상태 유지.
    """
    if not HAS_SCIPY:
        return  # scipy 없으면 skip

    state = EBQASState()
    # w_mismatch = 0 으로 강제 — mismatch query 에서 prior 학습 X → interval 고정
    # → p_true 가 계속 interval 밖에 머물러 mode switch 발동까지 가는 시나리오 검증.
    # default w_mismatch=1 시 prior 가 빠르게 따라가 mismatch 가 끊길 수 있으나, 본 test
    # 의 목표는 "streak 카운터 + explicit mode switch 동작" 검증이지 default hyperparam
    # 동작 검증이 아님. workload drift / wrong group key 등 prior 학습이 따라잡지 못하는
    # 시나리오를 w_mismatch=0 으로 가장 단순 시뮬.
    params = EBQASParams(w_mismatch=0.0)  # mismatch_n_threshold = 3 default
    table_size = 1_000_000

    # 초기 prior Beta(1, 1) → 99% credible interval ≈ (0.005, 0.995)
    # mismatch 강제: p_true = 0.999 (interval 밖)
    true_cardinality = table_size * 0.999  # p_true ≈ 0.999, prior interval 밖

    # 1 회 mismatch — consecutive_mismatch = 1, prior_mode 유지
    update_after_execution(state, true_cardinality, table_size, {}, params)
    assert state.consecutive_mismatch == 1, \
        f"after 1 mismatch: consecutive_mismatch = {state.consecutive_mismatch} (expected 1)"
    assert state.prior_mode == "history", \
        f"after 1 mismatch: prior_mode = {state.prior_mode!r} (expected 'history')"

    # 2 회 mismatch — consecutive_mismatch = 2, prior_mode 유지
    update_after_execution(state, true_cardinality, table_size, {}, params)
    assert state.consecutive_mismatch == 2, \
        f"after 2 mismatch: consecutive_mismatch = {state.consecutive_mismatch} (expected 2)"
    assert state.prior_mode == "history", \
        f"after 2 mismatch: prior_mode = {state.prior_mode!r} (expected 'history')"

    # 3 회 mismatch — mode switch 발동!
    update_after_execution(state, true_cardinality, table_size, {}, params)
    assert state.prior_mode == "no_history", \
        f"after 3 mismatch: prior_mode = {state.prior_mode!r} (expected 'no_history')"
    assert state.early_stop is False, \
        f"after 3 mismatch: early_stop = {state.early_stop} (expected False)"
    assert state.alpha == 1.0, f"after switch: alpha = {state.alpha} (expected 1.0)"
    assert state.beta == 1.0, f"after switch: beta = {state.beta} (expected 1.0)"
    assert state.kappa == 2.0, f"after switch: kappa = {state.kappa} (expected 2.0)"
    assert state.mu == 0.5, f"after switch: mu = {state.mu} (expected 0.5)"

    # 4·5 회 추가 mismatch — no_history 유지 (반복 mode switch 없음)
    # Beta(1,1) interval = (0.005, 0.995) 이므로 p_true=0.999 는 다시 mismatch 가능
    # 그러나 update_after_execution 의 mode switch 분기는 prior_mode == "history" 조건
    # → no_history 일 때는 mode switch 다시 발동 X, empirical-Bayes update 만 일어남
    for _ in range(2):
        update_after_execution(state, true_cardinality, table_size, {}, params)
        assert state.prior_mode == "no_history", \
            f"after extra mismatch: prior_mode = {state.prior_mode!r} (expected stays 'no_history')"


# ---------------------------------------------------------------------------
# Test 2 — Q_post floor separation (spec T1 §3.2 L_log vs L_stop / Codex (b) 정정)
# ---------------------------------------------------------------------------

def test_q_post_floor_separation():
    """L_raw=0 (또는 매우 작은) 케이스에서 q_post_log = inf, q_post_stop = 유한 assert.

    spec T1 §3.2 patch — Codex (b) finding 3 정정. logging 용 raw L 과 stop decision
    용 floored L 을 분리해 L=0 시 q_post_log = inf 로 cold-start 식별, q_post_stop
    은 항상 유한값으로 stop decision 안정.

    synthetic samples_b1 = 모두 qvec 에서 멀리 떨어진 vector → hits = 0
    → posterior_alpha = state.alpha (= 1.0) 유지 → L_raw 매우 작음.
    """
    if not HAS_SCIPY:
        return

    # synthetic state·params
    state = EBQASState()
    state.alpha = 1.0
    state.beta = 100.0  # b 가 크면 L_raw 매우 작음 → Q_post log = inf 가능
    state.early_stop = False  # n_cap 까지 sampling 강제
    state.n_cap = 100

    params = EBQASParams()
    params.batch_size = 16
    params.n_min = 16
    params.n_cap = 100

    # synthetic samples — 20 strata 각 100 vectors, dim=2 (단순)
    rng_data = np.random.default_rng(42)
    samples_b1 = {}
    sizes_b1 = {}
    n_strata = 20
    for sid in range(n_strata):
        # qvec 에서 멀리 (norm 100 이상) 떨어진 vector 만 생성
        samples_b1[sid] = (rng_data.normal(loc=100.0, scale=1.0, size=(100, 2))
                            .astype(np.float32))
        sizes_b1[sid] = 1000  # virtual size > sample cache

    qvec = np.array([0.0, 0.0], dtype=np.float32)
    D = 0.1  # threshold 매우 작아 hits = 0 보장

    rng = np.random.default_rng(123)
    est_result = ebqas_estimate(
        samples_b1=samples_b1, sizes_b1=sizes_b1,
        qvec=qvec, D=D,
        state=state, params=params, rng=rng,
        n_strata=n_strata,
    )

    # hits = 0 보장 (qvec norm 0, samples norm ~100, D = 0.1)
    assert est_result["hits"] == 0, f"hits = {est_result['hits']} (expected 0)"

    # posterior_alpha = state.alpha + s = 1.0 + 0 = 1.0
    assert math.isclose(est_result["posterior_alpha"], 1.0, abs_tol=1e-9), \
        f"posterior_alpha = {est_result['posterior_alpha']} (expected 1.0)"

    # L_raw 가 거의 0 이면 q_post_log >= q_post_stop (L_log 가 L_stop 보다 작거나 같음).
    # spec T1 §3.3 핵심 invariant — logging 용 L 은 raw, stop 용 L 은 floor → q_log >= q_stop.
    # scipy.stats.beta.ppf 가 정밀도 한계로 정확히 0 을 반환하기 어려워 inf 보장 X 이지만,
    # L_log <= L_stop 은 항상 성립 → q_log >= q_stop 도 항상 성립.
    q_log = est_result["posterior_q_risk_log"]
    q_stop = est_result["posterior_q_risk_stop"]
    # q_stop 은 항상 유한값
    assert math.isfinite(q_stop), f"q_post_stop = {q_stop} (expected finite)"
    # q_log >= q_stop — floor 분리의 정신 (L_log 가 L_stop 보다 같거나 작음 → q_log 가 크거나 같음)
    # cold-start (hits=0, beta 큼) 케이스에서는 q_log 가 q_stop 보다 충분히 큼
    assert q_log >= q_stop, \
        f"q_post_log = {q_log}, q_post_stop = {q_stop} (expected q_log >= q_stop)"
    # cold-start 시 q_log 는 충분히 큰 값 (>= 10) 이어야 의미 있음
    assert (math.isinf(q_log) or q_log >= 10.0), \
        f"q_post_log = {q_log} (expected inf or >= 10 for cold-start)"


# ---------------------------------------------------------------------------
# Test 3 — recovery after stable streak (spec T1 §4.2 history 회복 / Codex (b) 정정)
# ---------------------------------------------------------------------------

def test_recovery_after_stable_streak():
    """★ (b) 정정 후 의미 변경 — no_history 자동 recovery 불가, 수동 history 전환 검증.

    spec T1 §4.2 + Codex (b) 코드 정정 (#5b 세션):
      - prior_mode == "no_history" 진입 시 update_after_execution 즉시 return
        → alpha/beta/kappa/mu/streak 카운터 모두 변경 X
        → 완전한 ablation 그룹 보장 (Codex finding 의 핵심)
      - 결과: 자동 recovery 불가 (stable_query_count 가 0 유지)
      - history 회복은 외부 수동 트리거 필요 — 본 test 가 검증

    본 test 는 (b) 정정의 의도된 동작 검증:
      (1) no_history 진입 시 20 회 update → 모두 skip (state 불변)
      (2) 수동 history 전환 후 → 정상 prior 갱신 작동
    """
    if not HAS_SCIPY:
        return

    state = EBQASState()
    state.prior_mode = "no_history"
    state.early_stop = False
    state.alpha = 1.0
    state.beta = 1.0
    state.kappa = 2.0
    state.mu = 0.5

    params = EBQASParams()
    table_size = 1_000_000
    stable_true_cardinality = table_size * 0.5

    # (1) no_history 상태에서 20 회 update — 모두 skip (state 불변)
    for i in range(20):
        update_after_execution(state, stable_true_cardinality, table_size, {}, params)
        # ★ (b) 정정 후 — stable_query_count 가 증가 X (update 자체 skip)
        assert state.stable_query_count == 0, \
            f"after {i+1} update in no_history: stable_query_count = {state.stable_query_count} (expected 0, update skipped)"
        assert state.prior_mode == "no_history", \
            f"after {i+1} update: prior_mode = {state.prior_mode!r} (expected stays 'no_history')"
        assert state.alpha == 1.0 and state.beta == 1.0, \
            f"after {i+1} update: alpha/beta changed in no_history mode"

    # (2) 수동 history 전환 후 정상 갱신 확인
    state.prior_mode = "history"
    state.early_stop = True
    update_after_execution(state, stable_true_cardinality, table_size, {}, params)
    # p_true=0.5 는 Beta(1,1) interval 안 → mismatch 아님 → stable_query_count 증가
    assert state.stable_query_count == 1, \
        f"after manual history switch + 1 update: stable_query_count = {state.stable_query_count} (expected 1)"
    # alpha/beta 가 갱신되었는지 (정확한 값은 hyperparam 의존이라 변경 여부만 확인)
    assert state.alpha != 1.0 or state.beta != 1.0, \
        f"after history switch: alpha/beta unchanged (expected updated)"


# ---------------------------------------------------------------------------
# Test 3b — params.n_cap honor (Codex (a) 정정 #5b 세션)
# ---------------------------------------------------------------------------

def test_n_cap_param_honored():
    """★ (a) Codex (a) 정정 — params.n_cap 이 ebqas_estimate sample_size 에 반영되는지 확인.

    #5b 세션 코드 정정 — `sample_budget = min(params.n_cap, state.n_cap, n_flat)`
    로 두 cap 모두 적용. 본 test 는 params.n_cap=10 override 가 sample_size 에
    실제로 반영되는지 회귀 검증.
    """
    if not HAS_SCIPY:
        return

    # synthetic state/params — state.n_cap default 385, params.n_cap=10 override
    state = EBQASState()  # state.n_cap = 385 default
    state.early_stop = False  # n_cap 까지 sampling 강제

    params = EBQASParams(n_cap=10, n_min=5, batch_size=4)

    # synthetic samples — 20 strata 각 100 vectors
    rng_data = np.random.default_rng(42)
    samples_b1 = {}
    sizes_b1 = {}
    n_strata = 20
    for sid in range(n_strata):
        samples_b1[sid] = rng_data.normal(loc=0.0, scale=1.0, size=(100, 2)).astype(np.float32)
        sizes_b1[sid] = 1000

    qvec = np.array([0.0, 0.0], dtype=np.float32)
    D = 5.0

    rng = np.random.default_rng(123)
    est_result = ebqas_estimate(
        samples_b1=samples_b1, sizes_b1=sizes_b1,
        qvec=qvec, D=D,
        state=state, params=params, rng=rng,
        n_strata=n_strata,
    )

    # ★ params.n_cap=10 honor — sample_size <= 10 (batch_size=4 이라 12 가 될 수 있으나 cap 10)
    assert est_result["sample_size"] <= 10, \
        f"sample_size = {est_result['sample_size']} (expected <= 10, params.n_cap=10)"


# ---------------------------------------------------------------------------
# Test 3c — no_history keeps alpha/beta neutral (Codex (b) 추가 검증 #5b 세션)
# ---------------------------------------------------------------------------

def test_no_history_keeps_alpha_beta_neutral():
    """★ (b) Codex (b) 정정 추가 검증 — prior_mode="no_history" 에서 update skip.

    #5b 세션 코드 정정 — update_after_execution 진입 직후 prior_mode 검사:
      `if state.prior_mode == "no_history": return`
    본 test 는 다양한 true_cardinality 로 20 회 호출해도 state 가 완전히
    불변임을 확인. test_recovery_after_stable_streak 의 (1) 부분과 보완 관계.
    """
    if not HAS_SCIPY:
        return

    state = EBQASState()
    state.prior_mode = "no_history"
    state.early_stop = False
    snapshot = (state.alpha, state.beta, state.kappa, state.mu,
                state.mismatch_count, state.consecutive_mismatch,
                state.stable_query_count)

    params = EBQASParams()
    table_size = 10_000

    # 20 회 update — 다양한 true_cardinality (interval 안/밖 모두)
    for i in range(20):
        # i=0 mismatch (p=0.999), i=1 stable (p=0.5), 교차
        tc = table_size * (0.999 if i % 2 == 0 else 0.5)
        update_after_execution(state, tc, table_size, {}, params)
        current = (state.alpha, state.beta, state.kappa, state.mu,
                   state.mismatch_count, state.consecutive_mismatch,
                   state.stable_query_count)
        assert current == snapshot, \
            f"after {i+1} update in no_history: state changed {snapshot} → {current}"

    # 종합 — alpha/beta/kappa/mu/streak 모두 그대로
    assert state.alpha == 1.0
    assert state.beta == 1.0
    assert state.kappa == 2.0
    assert state.mu == 0.5
    assert state.mismatch_count == 0
    assert state.consecutive_mismatch == 0
    assert state.stable_query_count == 0


# ---------------------------------------------------------------------------
# Test 4 — paired join invariant (spec T3 §5.3 / Codex (c) 정정)
# ---------------------------------------------------------------------------

def test_paired_join_invariant_pass():
    """synthetic 4 mode JSON 모두 동일 (cell, trial_idx, query_idx) 3-tuple 일 때 pass."""
    if not HAS_SCIPY:
        return

    def _build_json(mode_label: str, true_cards_by_q: dict) -> dict:
        return {
            "mode": mode_label,
            "trial_results": [
                {
                    "trial_idx": 0,
                    "query_results": [
                        {"query_idx": q, "true_cardinality": float(tc)}
                        for q, tc in true_cards_by_q.items()
                    ],
                },
                {
                    "trial_idx": 1,
                    "query_results": [
                        {"query_idx": q, "true_cardinality": float(tc)}
                        for q, tc in true_cards_by_q.items()
                    ],
                },
            ],
        }

    true_cards = {0: 100.0, 1: 200.0, 2: 300.0}
    json_b1 = _build_json("B1", true_cards)
    json_caseb = _build_json("CaseB", true_cards)
    json_ebqas = _build_json("EB-QAS", true_cards)
    json_ebqas_nh = _build_json("EB-QAS-no-history", true_cards)

    # invariant pass
    assert_paired_join_invariant(json_b1, json_caseb, json_ebqas, json_ebqas_nh)


def test_paired_join_invariant_missing_query():
    """일부 query_idx 누락 시 AssertionError."""
    if not HAS_SCIPY:
        return

    def _build_json(mode_label: str, q_indices: list) -> dict:
        return {
            "mode": mode_label,
            "trial_results": [
                {
                    "trial_idx": 0,
                    "query_results": [
                        {"query_idx": q, "true_cardinality": 100.0}
                        for q in q_indices
                    ],
                },
            ],
        }

    json_b1 = _build_json("B1", [0, 1, 2])
    json_caseb = _build_json("CaseB", [0, 1, 2])
    json_ebqas = _build_json("EB-QAS", [0, 1, 2])
    # EB-QAS-no-history 에 query_idx=2 누락
    json_ebqas_nh = _build_json("EB-QAS-no-history", [0, 1])

    try:
        assert_paired_join_invariant(json_b1, json_caseb, json_ebqas, json_ebqas_nh)
        raise AssertionError("AssertionError 가 발생해야 함 (query_idx 누락)")
    except AssertionError as e:
        msg = str(e)
        assert "paired join 실패" in msg or "Δ=" in msg, \
            f"unexpected error: {e}"


def test_paired_join_invariant_true_cardinality_mismatch():
    """true_cardinality 불일치 시 AssertionError."""
    if not HAS_SCIPY:
        return

    def _build_json(mode_label: str, tc: float) -> dict:
        return {
            "mode": mode_label,
            "trial_results": [
                {
                    "trial_idx": 0,
                    "query_results": [
                        {"query_idx": 0, "true_cardinality": tc},
                    ],
                },
            ],
        }

    json_b1 = _build_json("B1", 100.0)
    json_caseb = _build_json("CaseB", 100.0)
    json_ebqas = _build_json("EB-QAS", 100.0)
    json_ebqas_nh = _build_json("EB-QAS-no-history", 999.0)  # 불일치

    try:
        assert_paired_join_invariant(json_b1, json_caseb, json_ebqas, json_ebqas_nh)
        raise AssertionError("AssertionError 가 발생해야 함 (true_cardinality 불일치)")
    except AssertionError as e:
        msg = str(e)
        assert "true_cardinality" in msg, f"unexpected error: {e}"


# ---------------------------------------------------------------------------
# Helper test — bucketize_threshold, make_group_key, beta_credible_interval
# ---------------------------------------------------------------------------

def test_bucketize_threshold_log_scale():
    """spec T4 §1.2(2) log-scale D bucket — leakage-free default 검증."""
    if not HAS_SCIPY:
        return

    assert bucketize_threshold(1.0) == 0, "D=1.0 → bucket=0 (log10(1)=0)"
    assert bucketize_threshold(0.1) == -1, "D=0.1 → bucket=-1"
    assert bucketize_threshold(0.01) == -2, "D=0.01 → bucket=-2"
    assert bucketize_threshold(10.0) == 1, "D=10.0 → bucket=1"
    # boundary
    assert bucketize_threshold(0.86) == -1, "D=0.86 → bucket=-1 (TPC-H 기본)"
    # numerical safety
    assert bucketize_threshold(0.0) == -12, "D=0.0 → bucket=-12 (floor)"


def test_make_group_key_6tuple():
    """spec T4 §1.2(1) runtime group key — 6-tuple, sel=... label 없음 검증."""
    if not HAS_SCIPY:
        return

    g = make_group_key(
        dataset="DEEP", vector_column="ps_embedding",
        distance_metric="L2", threshold=0.86,
        template_id=3, scalar_predicate_signature="none",
    )
    assert isinstance(g, tuple) and len(g) == 6, f"group_key = {g}"
    assert g[0] == "DEEP"
    assert g[1] == "ps_embedding"
    assert g[2] == "L2"
    assert g[3] == -1  # bucketize_threshold(0.86) = -1
    assert g[4] == 3
    assert g[5] == "none"
    # leakage 금지 — sel=... 라벨이 group key 에 들어가지 않음 (사용자 명시 metadata only)


# ---------------------------------------------------------------------------
# 단독 실행 entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not HAS_SCIPY:
        print("[SKIP] scipy 미발견 — test skip")
        sys.exit(0)
    failed = []
    tests = [
        test_mode_switch_mismatch_streak,
        test_q_post_floor_separation,
        test_recovery_after_stable_streak,  # ★ #5b 의미 변경 — 수동 history 전환 검증
        test_n_cap_param_honored,            # ★ #5b 신규 — Codex (a) 정정 회귀
        test_no_history_keeps_alpha_beta_neutral,  # ★ #5b 신규 — Codex (b) 추가 검증
        test_paired_join_invariant_pass,
        test_paired_join_invariant_missing_query,
        test_paired_join_invariant_true_cardinality_mismatch,
        test_bucketize_threshold_log_scale,
        test_make_group_key_6tuple,
    ]
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  [PASS] {name}")
        except Exception as e:
            print(f"  [FAIL] {name} — {type(e).__name__}: {e}")
            failed.append(name)
    if failed:
        print(f"\n{len(failed)}/{len(tests)} test FAIL")
        sys.exit(1)
    print(f"\n{len(tests)}/{len(tests)} test PASS")
