#!/usr/bin/env python3
"""
proxy_ensemble_compare.py — CaseB 결합 규칙 비교 (산술/기하/가중 등, 5/17 task I 보조)

질문
----
CaseB est = (est_b1 + est_method) / 2 산술평균 외에 더 나은 결합 규칙이 있나?

방법 (proxy)
-----------
3-way JSON 에 기록된 standalone B1.estimates 와 CaseA.estimates(= est_method) 를
component 로 놓고, 여러 결합 규칙을 후처리로 적용해 Q-error 를 비교한다.

한계: B1·CaseA 는 각자 AdaptiveState 로 budget 을 적응 → 실제 CaseB 내부의
e_b1/e_method (CaseB budget 공유) 와 정확히 같지 않다. 따라서 본 분석은
결합 규칙의 *상대 순위* 를 판단하기 위한 proxy 이며, 절대 Q-error 는 실측 CaseB 와
다르다. 같은 component 쌍에 모든 규칙을 적용하므로 규칙 간 비교는 공정하다.

결합 규칙
--------
arith    : (b1+m)/2                        — 현행 CaseB
geom     : sqrt(b1*m)                      — b1·m 중 0 이면 0 → Q-error inf (zero-collapse)
geom_fb  : sqrt(b1*m) if both>0 else arith — zero-collapse 회피
harm_fb  : 2/(1/b1+1/m) if both>0 else arith
w_b1_0.3 : 0.3*b1 + 0.7*m                  — method 비중 큰 가중
w_b1_0.7 : 0.7*b1 + 0.3*m                  — Bernoulli 비중 큰 가중
min, max : 참고

지표
----
finite_mean : inf 제외 query Q-error 평균 (정확도)
inf_rate    : inf query-trial 비율 (Bernoulli 0-hit 등으로 추정 실패)
capped_mean : inf 를 100 으로 cap 한 Q-error 평균 (정확도+실패 종합 1지표)
paired      : 측정(json) 단위 capped_mean 을 arith 와 짝지어 better% / Δ%

usage: python3 proxy_ensemble_compare.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path(__file__).resolve().parent / "results_3way_5_17"
INF_CAP = 100.0
RULES = ["arith", "geom", "geom_fb", "harm_fb", "w_b1_0.3", "w_b1_0.7", "min", "max"]


def combine(b1: np.ndarray, m: np.ndarray, rule: str) -> np.ndarray:
    """component 행렬 (T,Q) 두 개 → 결합 추정 행렬 (T,Q)."""
    if rule == "arith":
        return (b1 + m) / 2.0
    if rule == "w_b1_0.3":
        return 0.3 * b1 + 0.7 * m
    if rule == "w_b1_0.7":
        return 0.7 * b1 + 0.3 * m
    if rule == "min":
        return np.minimum(b1, m)
    if rule == "max":
        return np.maximum(b1, m)
    both = (b1 > 0) & (m > 0)
    if rule == "geom":
        g = np.zeros_like(b1)
        g[both] = np.sqrt(b1[both] * m[both])
        return g
    if rule == "geom_fb":
        out = (b1 + m) / 2.0
        out[both] = np.sqrt(b1[both] * m[both])
        return out
    if rule == "harm_fb":
        out = (b1 + m) / 2.0
        out[both] = 2.0 / (1.0 / b1[both] + 1.0 / m[both])
        return out
    raise ValueError(rule)


def q_error_mat(est: np.ndarray, true: np.ndarray) -> np.ndarray:
    """est (T,Q), true (Q,) → Q-error (T,Q). est<=0 → inf, true<=0 → nan(제외)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        r = est / true
        qe = np.maximum(r, 1.0 / r)
    qe[est <= 0] = np.inf
    qe[:, true <= 0] = np.nan
    return qe


def load_estimates(block: dict) -> np.ndarray:
    """B1/CaseA 블록 → estimates 행렬 (T,Q)."""
    return np.array([tr["estimates"] for tr in block["trial_results"]], dtype=float)


def main():
    json_files = sorted(RESULTS.glob("*/*_3way_*.json"))
    if not json_files:
        sys.exit(f"JSON 부재: {RESULTS}")
    print(f"3-way JSON {len(json_files)}건 — 결합 규칙 {len(RULES)}종 proxy 비교\n")

    # per (json, rule): finite_mean, inf_rate, capped_mean  + 메타(sel)
    recs = []
    ref_caseb = []  # 실측 CaseB qe_trim (참고)
    for i, jf in enumerate(json_files, 1):
        try:
            d = json.loads(jf.read_bytes())
        except (json.JSONDecodeError, OSError) as e:
            print(f"  skip {jf.name}: {e}", file=sys.stderr)
            continue
        true = np.array(d["true_cards"], dtype=float)
        b1 = load_estimates(d["B1"])
        m = load_estimates(d["CaseA"])
        if b1.shape != m.shape or b1.shape[1] != len(true):
            print(f"  skip {jf.name}: shape mismatch", file=sys.stderr)
            continue
        sel = d.get("selectivity")
        cell = d.get("cell")
        method = d.get("method")
        sf = d.get("sf")
        ref_caseb.append(d["CaseB"]["avg_q_error_trimmed"])
        for rule in RULES:
            qe = q_error_mat(combine(b1, m, rule), true)
            finite = np.isfinite(qe)
            n_inf = int(np.isinf(qe).sum())
            n_valid = int((~np.isnan(qe)).sum())
            capped = np.where(np.isinf(qe), INF_CAP, qe)
            recs.append({
                "json": str(jf.relative_to(RESULTS)), "rule": rule,
                "sel": sel, "cell": cell, "method": method, "sf": sf,
                "finite_mean": float(np.nanmean(np.where(finite, qe, np.nan))),
                "inf_rate": n_inf / n_valid if n_valid else float("nan"),
                "capped_mean": float(np.nanmean(capped)),
            })
        if i % 300 == 0:
            print(f"  {i}/{len(json_files)} ...")

    df = pd.DataFrame(recs)
    n_meas = df["json"].nunique()
    print(f"\n측정 {n_meas}건 × 규칙 {len(RULES)}종\n")
    print(f"(참고) 실측 CaseB qe_trim 평균 = {np.mean(ref_caseb):.4f} "
          f"— proxy 는 budget 비공유라 절대값 직접 비교 불가, 규칙 간 순위만 유효\n")

    # --- 규칙별 종합 ---
    print("=" * 78)
    print(f"{'rule':<10} {'finite_mean':>12} {'inf_rate%':>10} {'capped_mean':>12}"
          f" {'vs arith better%':>17} {'mean Δ%':>9}")
    print("-" * 78)
    arith_cap = df[df["rule"] == "arith"].set_index("json")["capped_mean"]
    summary = []
    for rule in RULES:
        sub = df[df["rule"] == rule]
        fm = sub["finite_mean"].mean()
        ir = sub["inf_rate"].mean() * 100
        cm = sub["capped_mean"].mean()
        r_cap = sub.set_index("json")["capped_mean"]
        delta = (r_cap - arith_cap) / arith_cap * 100   # 동일 json index 자동 정렬
        better = float((delta < 0).mean() * 100)
        print(f"{rule:<10} {fm:>12.4f} {ir:>10.2f} {cm:>12.4f}"
              f" {better:>16.1f}% {delta.mean():>8.2f}%")
        summary.append((rule, fm, ir, cm, better, delta.mean()))
    print("=" * 78)

    # --- selectivity 별 capped_mean (geom 의 sel 의존 확인) ---
    print("\nselectivity 별 capped_mean:")
    piv = df.pivot_table(index="rule", columns="sel", values="capped_mean", aggfunc="mean")
    piv = piv.reindex(RULES)
    print(piv.round(4).to_string())

    # --- 대안이 arith 를 이기는 분포: regime 인가 scatter 인가 ---
    print("\n대안 규칙이 arith 를 이기는 측정의 분포 (regime 존재 여부):")
    meta = df[df["rule"] == "arith"].set_index("json")[["method", "sf", "sel"]]
    for rule in ["geom_fb", "w_b1_0.7", "max"]:
        r_cap = df[df["rule"] == rule].set_index("json")["capped_mean"]
        dd = meta.copy()
        dd["delta"] = (r_cap - arith_cap) / arith_cap * 100
        win = dd[dd["delta"] < 0]
        print(f"  [{rule}] arith 보다 나은 측정 {len(win)}/{len(dd)}건"
              f" (평균 우위폭 {win['delta'].mean():.2f}%)" if len(win) else
              f"  [{rule}] arith 보다 나은 측정 0건")
        if len(win):
            print(f"    method 분포: {win.groupby('method').size().sort_values(ascending=False).to_dict()}")
            print(f"    sf 분포: {win.groupby('sf').size().to_dict()}  "
                  f"sel 분포: {win.groupby('sel').size().to_dict()}")

    # --- 판정 ---
    best_cm = min(summary, key=lambda x: x[3])
    best_fm = min(summary, key=lambda x: x[1])
    print(f"\n판정: capped_mean 최소 = {best_cm[0]} ({best_cm[3]:.4f}), "
          f"finite_mean 최소 = {best_fm[0]} ({best_fm[1]:.4f})")
    arith_cm = next(s for s in summary if s[0] == "arith")[3]
    print(f"      현행 arith capped_mean = {arith_cm:.4f}")


if __name__ == "__main__":
    main()
