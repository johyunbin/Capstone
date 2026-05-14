#!/usr/bin/env python3
"""
recovery_rate.py — RQ3 분석 헬퍼 라이브러리

핵심 metric (RQ재정립_20260505_2122 §RQ3):

    recovery_rate = (방법X − RANDOM20) / (KM20 − RANDOM20)

    1.0 → KM20 oracle 수준 회수
    0.0 → RANDOM20 (공간 인식 없음) 수준
    음수 → RANDOM20 보다 나쁨

분모 붕괴 경계 (사전 등록):
    |KM20 − RANDOM20| ≤ 1.0%p 인 셀에서는 Recovery Rate 보고하지 않고,
    절대 Q-error 개선폭 (방법X − BERN) %p 를 primary metric 으로 사용.

7-way 비교 BH-FDR:
    RQ2 의 50-비교 BH-FDR 로직 (`rq2_alloc_BH_FDR_50comparisons`) 을 재활용,
    7 method × 2 dataset × 5 selectivity = 70 비교까지 확장 가능.

사용법:
    from experiments.code.local_analysis.recovery_rate import (
        recovery_rate, paired_wilcoxon_with_bh_fdr, summarize_method,
    )

    # 1) recovery_rate(): cell 단위 단일 값
    rr = recovery_rate(method_q=2.5, random20_q=3.0, km20_q=2.0)
    # → (1.0, 'recovery')

    # 2) paired_wilcoxon_with_bh_fdr(): 다중 비교 일괄
    df_results = paired_wilcoxon_with_bh_fdr(
        df_long,                    # long-form: dataset/mode/selectivity/seed/query_id/q_error
        compare_pairs=[(method, 'bernoulli'), ...],
        n_compare=None,             # None 이면 자동 (행 수)
    )
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Literal

import numpy as np
import pandas as pd
import scipy.stats as sst


# ---------------------------------------------------------------------------
# 1. Cell-level Recovery Rate
# ---------------------------------------------------------------------------

DENOM_COLLAPSE_THRESHOLD_PCT = 1.0  # |KM20 - RANDOM20| ≤ 1.0%p → fall back


@dataclass
class RecoveryResult:
    value: float
    metric: Literal["recovery", "fallback_abs_pct"]
    denom_pct: float           # KM20 − RANDOM20 절대값 (%p)
    method_minus_random_pct: float
    method_minus_bern_pct: float | None  # fall-back 모드에서만 채워짐


def recovery_rate(
    method_q: float,
    random20_q: float,
    km20_q: float,
    bern_q: float | None = None,
    *,
    threshold_pct: float = DENOM_COLLAPSE_THRESHOLD_PCT,
) -> RecoveryResult:
    """단일 cell 의 Recovery Rate.

    Args:
        method_q: 방법X 의 q_error (mean, 또는 single sample 의 절대값).
        random20_q: RANDOM20 의 q_error.
        km20_q: KM20 oracle 의 q_error.
        bern_q: BERNOULLI baseline. fall-back 시 필요. 또한 fall-back 이 아니더라도
            method_minus_bern_pct 보조 metric 산출 위해 권장.
        threshold_pct: 분모 |KM20−RANDOM20| 가 이 값 (%p) 이하면 fall-back.

    Returns:
        RecoveryResult — `metric == 'recovery'` 면 표준 공식,
        `'fallback_abs_pct'` 면 (방법X − BERN) / BERN × 100 (%p) 반환.
        method_minus_bern_pct 는 bern_q 가 주어지면 항상 채워짐 (fall-back 여부 무관).
    """
    denom_pct = abs(random20_q - km20_q) / max(random20_q, 1e-9) * 100.0
    method_minus_random_pct = (method_q - random20_q) / max(random20_q, 1e-9) * 100.0
    method_minus_bern_pct = (
        (method_q - bern_q) / max(bern_q, 1e-9) * 100.0
        if bern_q is not None and not math.isnan(bern_q) else None
    )

    if denom_pct <= threshold_pct:
        if bern_q is None or math.isnan(bern_q):
            raise ValueError(
                f"분모 붕괴 (|KM20−RANDOM20|/RANDOM20 = {denom_pct:.3f}%p ≤ {threshold_pct}%p) — "
                "fall-back 위해 bern_q 전달 필요"
            )
        return RecoveryResult(
            value=method_minus_bern_pct,
            metric="fallback_abs_pct",
            denom_pct=denom_pct,
            method_minus_random_pct=method_minus_random_pct,
            method_minus_bern_pct=method_minus_bern_pct,
        )

    # KM20 이 RANDOM20 보다 작아야 (q_error 가 낮을수록 좋음) 의미가 있음.
    # value > 1 → KM20 oracle 보다 나음 (드묾), 0 → RANDOM20 수준, <0 → RANDOM20 보다 나쁨.
    rr = (method_q - random20_q) / (km20_q - random20_q) if (km20_q - random20_q) != 0 else math.nan
    return RecoveryResult(
        value=rr,
        metric="recovery",
        denom_pct=denom_pct,
        method_minus_random_pct=method_minus_random_pct,
        method_minus_bern_pct=method_minus_bern_pct,
    )


# ---------------------------------------------------------------------------
# 2. Paired Wilcoxon + BH-FDR (RQ2 50-비교 로직 재활용 + 7-way 확장)
# ---------------------------------------------------------------------------

def paired_wilcoxon_with_bh_fdr(
    df: pd.DataFrame,
    compare_pairs: list[tuple[str, str]],
    *,
    datasets: Iterable[str] | None = None,
    selectivities: Iterable[float] | None = None,
    n_compare: int | None = None,
    alternative: Literal["less", "greater", "two-sided"] = "less",
    drop_nan: bool = True,
) -> pd.DataFrame:
    """다중 비교 paired Wilcoxon + Benjamini-Hochberg FDR 보정.

    Args:
        df: long-form DataFrame — 컬럼 [dataset, mode, selectivity, seed, query_id, q_error].
        compare_pairs: [(treatment_mode, control_mode), ...]. 예: [('km20', 'bernoulli'), ('minibatch', 'random20')].
            7-way RQ3 에서는 [('random_proj','random20'), ('lsh','random20'), ...] 처럼 RANDOM20 baseline 비교 권장.
        datasets: None → df 의 unique 전체.
        selectivities: None → df 의 unique 전체.
        n_compare: BH 분모 (총 비교 수). None 이면 결과 행 수 자동 사용 (= len(pairs)·|datasets|·|sel|).
        alternative: paired Wilcoxon alternative. "less" — treatment q_error < control q_error 검증.
        drop_nan: q_error NaN 행 drop 여부 (BERNOULLI 의 0-est 에서 발생).

    Returns:
        DataFrame — [dataset, mode_treat, mode_ctrl, sel, n_pairs, delta_pct, w_stat, p_raw, p_BH, reject_005].
        delta_pct = (treat_med − ctrl_med) / ctrl_med × 100 (%p, 음수일수록 treatment 가 좋음).
    """
    if drop_nan:
        df = df.dropna(subset=["q_error"]).copy()

    if datasets is None:
        datasets = df["dataset"].unique().tolist()
    if selectivities is None:
        selectivities = sorted(df["selectivity"].unique().tolist())

    rows: list[dict] = []
    for ds in datasets:
        for sel in selectivities:
            sub = df[(df["dataset"] == ds) & (df["selectivity"] == sel)]
            for treat, ctrl in compare_pairs:
                a = sub[sub["mode"] == treat].sort_values(["seed", "query_id"])
                b = sub[sub["mode"] == ctrl].sort_values(["seed", "query_id"])
                # paired alignment
                merged = a.merge(
                    b, on=["seed", "query_id"], suffixes=("_t", "_c"), how="inner"
                )
                if len(merged) < 2:
                    rows.append({
                        "dataset": ds, "mode_treat": treat, "mode_ctrl": ctrl,
                        "sel": sel, "n_pairs": len(merged),
                        "delta_pct": math.nan, "w_stat": math.nan,
                        "p_raw": math.nan, "p_BH": math.nan, "reject_005": False,
                    })
                    continue

                qt = merged["q_error_t"].to_numpy()
                qc = merged["q_error_c"].to_numpy()
                # 모두 동일하면 wilcoxon 실패 → p=1
                if np.allclose(qt, qc):
                    p_raw = 1.0
                    w = 0.0
                else:
                    try:
                        res = sst.wilcoxon(qt, qc, alternative=alternative, zero_method="wilcox")
                        w = float(res.statistic)
                        p_raw = float(res.pvalue)
                    except Exception as e:
                        w, p_raw = math.nan, math.nan

                med_t = float(np.median(qt))
                med_c = float(np.median(qc))
                delta_pct = (med_t - med_c) / max(med_c, 1e-9) * 100.0

                rows.append({
                    "dataset": ds, "mode_treat": treat, "mode_ctrl": ctrl,
                    "sel": sel, "n_pairs": len(merged),
                    "delta_pct": delta_pct, "w_stat": w,
                    "p_raw": p_raw, "p_BH": math.nan, "reject_005": False,
                })

    out = pd.DataFrame(rows)
    n_compare_eff = n_compare if n_compare is not None else int(out["p_raw"].notna().sum())
    out = _bh_fdr_inplace(out, p_col="p_raw", out_col="p_BH", n_compare=n_compare_eff)
    out["reject_005"] = (out["p_BH"] <= 0.05) & out["p_BH"].notna()
    return out


def _bh_fdr_inplace(
    df: pd.DataFrame, *, p_col: str = "p_raw", out_col: str = "p_BH",
    n_compare: int | None = None,
) -> pd.DataFrame:
    """Benjamini-Hochberg step-up FDR 보정.

    p_BH[k] = min_{j>=k} (n / rank[j]) · p_raw[j], rank 는 오름차순.
    """
    df = df.copy()
    valid = df[p_col].notna()
    pvals = df.loc[valid, p_col].to_numpy()
    n = n_compare if n_compare is not None else len(pvals)
    if n == 0:
        df[out_col] = math.nan
        return df

    order = np.argsort(pvals)
    ranked = pvals[order]
    bh = ranked * n / (np.arange(len(ranked)) + 1)
    # step-up: 뒤에서부터 누적 min
    bh = np.minimum.accumulate(bh[::-1])[::-1]
    bh = np.clip(bh, 0.0, 1.0)
    p_bh = np.empty_like(pvals)
    p_bh[order] = bh

    df.loc[valid, out_col] = p_bh
    return df


# ---------------------------------------------------------------------------
# 3. summarize_method — 7-way 결과 한 줄 요약
# ---------------------------------------------------------------------------

def summarize_method(
    df: pd.DataFrame,
    method: str,
    *,
    baselines: tuple[str, str, str] = ("random20", "km20", "bernoulli"),
    threshold_pct: float = DENOM_COLLAPSE_THRESHOLD_PCT,
) -> pd.DataFrame:
    """method 의 dataset × selectivity 별 recovery rate 요약.

    Args:
        df: long-form (recovery_rate 와 동일 형식).
        method: 평가 대상 mode (예: 'minibatch').
        baselines: (RANDOM20, KM20, BERNOULLI) mode 이름 — 데이터셋 컨벤션에 맞게 조정.
        threshold_pct: 분모 붕괴 경계.

    Returns:
        DataFrame — [dataset, sel, method_q, random20_q, km20_q, bern_q, denom_pct,
                    recovery, metric, method_minus_random_pct, method_minus_bern_pct].
    """
    rand_name, km_name, bern_name = baselines
    df_clean = df.dropna(subset=["q_error"])

    rows = []
    for ds in df_clean["dataset"].unique():
        for sel in sorted(df_clean["selectivity"].unique()):
            sub = df_clean[(df_clean["dataset"] == ds) & (df_clean["selectivity"] == sel)]

            def _mean_or_nan(mode: str) -> float:
                m = sub[sub["mode"] == mode]["q_error"]
                return float(m.mean()) if len(m) else math.nan

            method_q = _mean_or_nan(method)
            random20_q = _mean_or_nan(rand_name)
            km20_q = _mean_or_nan(km_name)
            bern_q = _mean_or_nan(bern_name)

            if any(math.isnan(v) for v in (method_q, random20_q, km20_q)):
                rows.append({
                    "dataset": ds, "sel": sel,
                    "method_q": method_q, "random20_q": random20_q,
                    "km20_q": km20_q, "bern_q": bern_q,
                    "denom_pct": math.nan, "recovery": math.nan,
                    "metric": "missing",
                    "method_minus_random_pct": math.nan,
                    "method_minus_bern_pct": math.nan,
                })
                continue

            res = recovery_rate(
                method_q=method_q, random20_q=random20_q, km20_q=km20_q,
                bern_q=bern_q if not math.isnan(bern_q) else None,
                threshold_pct=threshold_pct,
            )
            rows.append({
                "dataset": ds, "sel": sel,
                "method_q": method_q, "random20_q": random20_q,
                "km20_q": km20_q, "bern_q": bern_q,
                "denom_pct": res.denom_pct,
                "recovery": res.value if res.metric == "recovery" else math.nan,
                "metric": res.metric,
                "method_minus_random_pct": res.method_minus_random_pct,
                "method_minus_bern_pct": res.method_minus_bern_pct,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. CLI smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # smoke test 1: cell-level recovery_rate
    r1 = recovery_rate(method_q=2.0, random20_q=3.0, km20_q=1.5, bern_q=2.5)
    assert r1.metric == "recovery"
    print(f"[smoke 1] method=2.0, rand=3.0, km=1.5 → recovery={r1.value:.3f} ({r1.metric})")

    # smoke test 2: 분모 붕괴 fall-back
    r2 = recovery_rate(method_q=2.0, random20_q=2.005, km20_q=2.0, bern_q=2.5)
    assert r2.metric == "fallback_abs_pct"
    print(f"[smoke 2] km≈rand → metric={r2.metric}, value={r2.value:.3f}%p")

    # smoke test 3: BH-FDR 단순 케이스
    df_demo = pd.DataFrame({
        "dataset": ["A"] * 10,
        "mode": ["x", "y"] * 5,
        "selectivity": [0.05] * 10,
        "seed": [0] * 10,
        "query_id": [0, 0, 1, 1, 2, 2, 3, 3, 4, 4],
        "q_error": [1.0, 2.0, 1.1, 2.1, 1.2, 2.2, 1.3, 2.3, 1.4, 2.4],
    })
    out = paired_wilcoxon_with_bh_fdr(
        df_demo, compare_pairs=[("x", "y")], alternative="less",
    )
    print(f"[smoke 3] BH-FDR result:\n{out.to_string(index=False)}")
    print("\n✓ recovery_rate.py self-test passed")
