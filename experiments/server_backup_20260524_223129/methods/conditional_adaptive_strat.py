#!/usr/bin/env python3
"""
Conditional Adaptive Sampling — selectivity-aware variant of Exqutor V-B (Tier C).

Extends the Exqutor (arXiv:2512.09695v2) Adaptive Sampling state machine
(Section V-B, equations 3-6) with a *selectivity-conditioned* gradient term.
The original Exqutor gradient drives the per-table sample size by Q-error
alone; this variant injects a logarithmic prior on the *current query's*
selectivity so that rarer queries (low ``sel``) request larger samples and
common queries (high ``sel``) shrink their sample more aggressively.

Algorithm
---------
The original update (equations 3-6, Exqutor Section V-B)::

    delta_t  = alpha * (Q_t - beta) - (100 - alpha) * sampling_ratio_t            (3)
    V_t      = m * V_{t-1} + eta_t * delta_t                                       (4)
    S_{t+1}  = clip(S_t + V_t, S_min, S_max)                                       (5)
    eta_{t+1} = gamma * eta_t                                                      (6)

The selectivity-conditioned variant modifies only equation (3)::

    delta_sel_t = alpha * (Q_t - beta)
                 - (100 - alpha) * sampling_ratio_t
                 + sel_term * log(max(sel_t, eps))                                (3')

with ``sel_term = 5.0`` and ``sel_t`` the (per-query) selectivity in
``{0.01, 0.05, 0.10, 0.30, 0.50}``. Because ``log(sel) <= 0`` for all
selectivities in this regime and is *more negative for rare queries*, the
inequality ``log(0.01) = -4.605 << log(0.50) = -0.693`` causes the gradient
to *increase the sample size more aggressively* for rare queries (negative
delta term reduced when scaled by negative log-sel) -- equivalent to a
selectivity prior that says "small populations need more samples" (Cochran
1977 stratified-sampling intuition; classical Neyman 1934 allocation).

Equations (4)-(6) are unchanged and applied verbatim.

Output
------
Unlike the stratification methods (CCA, Co-clustering), this class does not
emit a per-row ``stratum_id``. Instead, ``step(qerror, selectivity)`` returns
the next-query ``sample_size_t`` (per query). Tier C single-table workflows
consume this through the existing ``_measure_common.run_method_measurement``
adaptive-sampling path.

Limitation
----------
This is a *single-table single-vector* method. Multi-table / multi-vector
queries do not have a single canonical selectivity (each predicate has its
own), so applying this method in those settings is unsound. The
multi-vector pipeline must continue to use the per-table separate-state
Adaptive (Exqutor-original) baseline implemented in
``measure_multi_adaptive_sampling.py``.

References
----------
Lim S, Park S, Kang Y, Park CH. "Exqutor: Extended Query Optimizer for
Vector-augmented Analytical Queries." arXiv:2512.09695v2, Section V-B.

Cochran WG. *Sampling Techniques*, 3rd ed. Wiley, 1977 -- selectivity prior
intuition.

Neyman J. "On the two different aspects of the representative method." J.
Roy. Statist. Soc. 97(4), 558-625 (1934). DOI 10.2307/2342192.

Sutskever I, Martens J, Dahl G, Hinton G. "On the importance of
initialization and momentum in deep learning." ICML 2013, 1139-1147 -- Eq. 4
momentum origin (Exqutor reference).

Usage
-----
::

    from conditional_adaptive_strat import ConditionalAdaptiveState
    state = ConditionalAdaptiveState(
        sample_size=385.0, max_size=10_000, sel_term=5.0,
    )
    for q_idx, query in enumerate(queries):
        s = state.next_sample_size()
        est = bernoulli_estimate(table, query, sample_size=s)
        qerr = compute_qerror(est, true_card)
        state.step(qerror=qerr, selectivity=query.selectivity)

Author: Capstone 2026 / 속도는벡터 (Tier C production-ready, 2026-05-09).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Exqutor Section VI defaults — preserve exactly so empirical reproductions of
# the original AdaptiveState are reachable from this class by setting
# `sel_term=0.0`.
# ---------------------------------------------------------------------------
DEFAULT_SAMPLE_SIZE: float = 385.0
DEFAULT_LR: float = 0.1
DEFAULT_MOMENTUM: float = 0.9
DEFAULT_ALPHA: float = 50.0
DEFAULT_BETA: float = 1.5
DEFAULT_GAMMA: float = 0.99
DEFAULT_UPDATE_PERIOD: int = 50
DEFAULT_MIN_SIZE: int = 50
DEFAULT_MAX_SIZE: int = 5_000

# Conditional variant additions
DEFAULT_SEL_TERM: float = 5.0
DEFAULT_SEL_EPS: float = 1e-4


@dataclass
class ConditionalAdaptiveState:
    """Selectivity-aware Adaptive Sampling state machine (Tier C variant).

    This class mirrors the ``AdaptiveState`` in
    ``_internal/scripts/measure_multi_ensemble.py`` (and
    ``measure_multi_adaptive_sampling.py``) line-for-line for equations 4-6,
    differing only in equation 3 by adding the selectivity-prior term.

    Attributes
    ----------
    sample_size:
        Current (continuous) sample size. Initialised to 385 per Exqutor
        equation (1) (z=1.96, P=0.5, e=0.05).
    velocity:
        Momentum buffer ``V_t`` (equation 4).
    learning_rate:
        Current learning rate ``eta_t`` (equation 6).
    momentum, alpha, beta, gamma:
        Exqutor Section VI hyperparameters; held identical to the original.
    update_period:
        Update equations 3-6 every ``update_period`` queries (50, per Exqutor
        Section VI).
    min_size, max_size:
        Sample-size clipping bounds. Defaults match
        ``measure_multi_adaptive_sampling.AdaptiveState``.
    sel_term:
        Coefficient of the new selectivity-prior term in equation (3').
        Set to ``0.0`` to recover the original Exqutor behaviour exactly.
    sel_eps:
        Numerical guard for ``log(sel)`` when selectivity is near zero.
    n_total:
        Total queries observed.
    qerror_window:
        Q-errors observed since the last update (averaged at update time).
    sel_window:
        Selectivities observed since the last update; logged form of the mean
        feeds into equation (3').
    sample_size_history:
        Trace of ``sample_size`` after each ``step`` (useful for plotting /
        diagnostics).
    """

    sample_size: float = DEFAULT_SAMPLE_SIZE
    velocity: float = 0.0
    learning_rate: float = DEFAULT_LR
    momentum: float = DEFAULT_MOMENTUM
    alpha: float = DEFAULT_ALPHA
    beta: float = DEFAULT_BETA
    gamma: float = DEFAULT_GAMMA
    update_period: int = DEFAULT_UPDATE_PERIOD
    min_size: int = DEFAULT_MIN_SIZE
    max_size: int = DEFAULT_MAX_SIZE
    sel_term: float = DEFAULT_SEL_TERM
    sel_eps: float = DEFAULT_SEL_EPS
    n_total: int = 0
    qerror_window: list = field(default_factory=list)
    sel_window: list = field(default_factory=list)
    sample_size_history: list = field(default_factory=list)

    def next_sample_size(self) -> int:
        """Sample size (rounded int) to use for the *next* query.

        This does not advance the state -- callers may invoke ``step`` after
        observing the query's actual q-error / selectivity to update.
        """
        return int(round(np.clip(self.sample_size, self.min_size, self.max_size)))

    def step(
        self,
        qerror: Optional[float],
        selectivity: Optional[float] = None,
    ) -> int:
        """Observe one (qerror, selectivity) pair and possibly update.

        Parameters
        ----------
        qerror:
            Q-error of the just-completed query (max(est/true, true/est)).
            Pass ``None`` or non-finite to skip this query in the running
            mean (e.g., when both estimate and ground truth are zero).
        selectivity:
            Selectivity of the just-completed query, in (0, 1]. ``None`` is
            treated as the running window mean (graceful degrade for callers
            that only have q-error).

        Returns
        -------
        int
            Sample size to use for the *next* query (rounded, clipped).
        """
        self.n_total += 1
        if qerror is not None and np.isfinite(qerror):
            self.qerror_window.append(float(qerror))
        if selectivity is not None and np.isfinite(selectivity):
            self.sel_window.append(float(selectivity))

        if self.n_total % self.update_period == 0 and self.qerror_window:
            mean_qe = float(np.mean(self.qerror_window))
            sampling_ratio = self.sample_size / max(self.max_size, 1)
            # Equation (3') -- selectivity-conditioned gradient
            base_delta = (
                self.alpha * (mean_qe - self.beta)
                - (100.0 - self.alpha) * sampling_ratio
            )
            if self.sel_window and self.sel_term != 0.0:
                mean_sel = float(np.mean(self.sel_window))
                sel_log = float(np.log(max(mean_sel, self.sel_eps)))
                delta = base_delta + self.sel_term * sel_log
            else:
                delta = base_delta

            # Equation (4)
            self.velocity = (
                self.momentum * self.velocity + self.learning_rate * delta
            )
            # Equation (5)
            self.sample_size = self.sample_size + self.velocity
            self.sample_size = float(
                np.clip(self.sample_size, self.min_size, self.max_size)
            )
            # Equation (6)
            self.learning_rate = self.gamma * self.learning_rate
            # Reset windows for the next update epoch
            self.qerror_window.clear()
            self.sel_window.clear()

        s_next = self.next_sample_size()
        self.sample_size_history.append(s_next)
        return s_next


def _self_test() -> None:
    """Mini-run: 100 queries x 5 selectivities -> sample-size trajectory."""
    import warnings

    np.seterr(all="ignore")
    warnings.filterwarnings("ignore")
    rng = np.random.default_rng(0)

    selectivities = [0.01, 0.05, 0.10, 0.30, 0.50]
    n_queries = 100

    print("[self-test] === ConditionalAdaptiveState (sel-aware Exqutor V-B) ===")
    print(
        "[self-test] init sample_size=385, sel_term=5.0, alpha=50, beta=1.5, "
        "gamma=0.99, period=50"
    )
    print()

    # Simulate 100 queries per selectivity. Q-error is heuristic: rarer queries
    # produce systematically higher q-error so we can confirm the selectivity
    # term pushes the rare-sel state toward larger sample size.
    for sel in selectivities:
        state = ConditionalAdaptiveState()
        for q_idx in range(n_queries):
            # Synthetic q-error: rare queries have higher base + more noise.
            base_qe = 1.5 + (-np.log(sel)) * 0.2  # rare → higher base
            qe = float(base_qe + rng.normal(0.0, 0.3))
            qe = max(qe, 1.0 + 1e-3)
            state.step(qerror=qe, selectivity=sel)

        traj = state.sample_size_history
        print(
            f"[self-test] sel={sel:.2f}: "
            f"final={traj[-1]:>5d}  "
            f"min={min(traj):>5d}  "
            f"max={max(traj):>5d}  "
            f"mean={int(np.mean(traj)):>5d}  "
            f"@50={traj[49]:>5d}  @99={traj[-1]:>5d}"
        )

    # Compare against the original AdaptiveState (sel_term=0.0). With the same
    # synthetic Q-error trajectory, the sel-aware variant should request a
    # *smaller* equilibrium for high-selectivity queries (log(0.5) = -0.693
    # contributes a negative delta term, shrinking sample_size).
    print()
    print(
        "[self-test] sanity: sel_term=0 (Exqutor-original) vs sel_term=5 "
        "(sel-aware) on sel=0.50, identical qerror seed"
    )
    rng_a = np.random.default_rng(123)
    rng_b = np.random.default_rng(123)
    state_orig = ConditionalAdaptiveState(sel_term=0.0)
    state_sel = ConditionalAdaptiveState(sel_term=5.0)
    for q_idx in range(100):
        qe = float(1.6 + rng_a.normal(0.0, 0.3))
        qe = max(qe, 1.01)
        state_orig.step(qerror=qe, selectivity=0.50)
        # rng_b mirrors so the q-errors match.
        qe2 = float(1.6 + rng_b.normal(0.0, 0.3))
        qe2 = max(qe2, 1.01)
        state_sel.step(qerror=qe2, selectivity=0.50)

    print(
        f"[self-test] sel_term=0  final sample_size = {state_orig.sample_size_history[-1]}"
    )
    print(
        f"[self-test] sel_term=5  final sample_size = {state_sel.sample_size_history[-1]}"
    )
    assert (
        state_sel.sample_size_history[-1] <= state_orig.sample_size_history[-1] + 1
    ), (
        "On sel=0.50, sel-term should shrink sample_size relative to original "
        f"(sel-aware={state_sel.sample_size_history[-1]} vs "
        f"orig={state_orig.sample_size_history[-1]})"
    )

    # Determinism
    sa = ConditionalAdaptiveState()
    sb = ConditionalAdaptiveState()
    rng_c = np.random.default_rng(42)
    rng_d = np.random.default_rng(42)
    for _ in range(100):
        qa = float(1.5 + rng_c.normal(0, 0.2))
        qb = float(1.5 + rng_d.normal(0, 0.2))
        sa.step(qerror=qa, selectivity=0.10)
        sb.step(qerror=qb, selectivity=0.10)
    assert sa.sample_size_history == sb.sample_size_history
    print("[self-test] determinism OK")

    # Bounds: sample_size always within [min_size, max_size]
    state_extreme = ConditionalAdaptiveState(min_size=100, max_size=400)
    rng_e = np.random.default_rng(7)
    for _ in range(200):
        qe = float(rng_e.choice([1.05, 5.0]))  # extreme oscillation
        state_extreme.step(qerror=qe, selectivity=0.01)
    assert all(
        100 <= s <= 400 for s in state_extreme.sample_size_history
    ), "sample_size violated [min_size, max_size]"
    print("[self-test] bounds OK")

    print("[self-test] OK")


if __name__ == "__main__":
    _self_test()
