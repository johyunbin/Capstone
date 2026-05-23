#!/usr/bin/env python3
"""A1 메커니즘 감사 (정정판 + 분해) — CaseB의 B1 우위가 (가)인지 (나)인지.

measure_3way 구조 (코드 정독 확인):
  · B1·CaseA·CaseB 가 각자 독립 AdaptiveState(Eq 1-6) → sample size N 발산.
  · 공유 rng → CaseB 내부 Bernoulli draw 는 B1 draw 와 다름.
  · q_idx < update_period(50) 구간은 전 mode N=385 고정 — 깨끗한 추정량 비교 가능.

판정 통제군:
  CaseB  = (Bernoulli + stratified)/2   ← 연구 주장
  CaseB′ = (Bernoulli + Bernoulli)/2    ← 통제군. method 자리에 또 다른 Bernoulli.
  CaseB ≈ CaseB′ → (나) 평균 아티팩트 / CaseB ≫ CaseB′ → (가) 분포 인지 기여.

★ 주의 — 고정 N 에서도 CaseB·CaseB′ 는 추정량 2개라 query 당 표본 770, B1 은 385.
  '추정량 우열'과 '표본 2배'가 아직 섞임 → budget-matched 통제는 별도 controlled benchmark.

method·sel·dataset 별 분해로 (나)가 균일한지, 예외 regime 이 있는지 본다.

데이터: results_3way_5_17/*/*_3way_<method>.json
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

RESULTS = Path(__file__).resolve().parents[1] / "cache" / "rq3" / "results_3way_5_17"
DIR_RE = re.compile(r"^(?P<cell>.+)_sel(?P<sel>[\d.]+)_K(?P<K>\d+)$")
STRONG = {
    "hilbert_real", "skilling_hilbert", "chao_weighted", "ica_fastica", "pca1d",
    "zorder_morton", "hyperloglog", "cum_sqrtf", "lavallee_hidiroglou", "rsvd",
    "sparse_rp", "mhist2", "rabitq_strat",
}
FIXED_N_Q = 50
CTRL_OFFSET = 5


def qerr(est: np.ndarray, true: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(true > 0, est / true, np.nan)
        return np.where(r > 0, np.maximum(r, 1.0 / np.where(r > 0, r, np.nan)), np.inf)


def fmean(x: np.ndarray) -> float:
    f = x[np.isfinite(x)]
    return float(f.mean()) if f.size else float("inf")


def estimates(block: dict, n: int) -> list[np.ndarray]:
    out = []
    for tr in block.get("trial_results", []):
        e = tr.get("estimates")
        if isinstance(e, list) and len(e) == n:
            out.append(np.asarray(e, dtype=float))
    return out


def betterpct(deltas):
    """deltas = exp 대비 base 의 Δ% 리스트. better = Δ%<0 비율."""
    n = len(deltas)
    if not n:
        return 0, 0, float("nan"), float("nan")
    b = sum(1 for x in deltas if x < 0)
    return b, n, b / n * 100, float(np.median(deltas))


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    files = sorted(RESULTS.glob("*/*_3way_*.json"))
    print(f"=== A1 메커니즘 감사 (정정판+분해) — {len(files)} JSON 스캔 ===")

    records = []     # measurement별 dict
    quad = defaultdict(int)
    n_used = 0

    for fi, path in enumerate(files):
        m = DIR_RE.match(path.parent.name)
        if not m:
            continue
        method = path.stem.split("_3way_")[-1].strip().lower()
        if method not in STRONG:
            continue
        try:
            d = json.loads(path.read_bytes())
        except Exception:
            continue
        true = d.get("true_cards")
        if not isinstance(true, list) or not true:
            continue
        true = np.asarray(true, dtype=float)
        nq = len(true)
        sel = float(m.group("sel"))
        dataset = str(d.get("dataset", "?"))
        B, A, C = d.get("B1", {}), d.get("CaseA", {}), d.get("CaseB", {})

        # 헤드라인 (적응 루프 전체) — trial avg_q_error_finite
        ab = [tr.get("avg_q_error_finite") for tr in B.get("trial_results", [])]
        aa = [tr.get("avg_q_error_finite") for tr in A.get("trial_results", [])]
        ac = [tr.get("avg_q_error_finite") for tr in C.get("trial_results", [])]
        nt = min(len(ab), len(aa), len(ac))
        hA = hB = None
        if nt >= 2:
            dA, dB = [], []
            for t in range(nt):
                if ab[t] and np.isfinite(ab[t]) and ab[t] > 0:
                    dA.append((aa[t] - ab[t]) / ab[t] * 100)
                    dB.append((ac[t] - ab[t]) / ab[t] * 100)
            if dB:
                hA, hB = float(np.mean(dA)), float(np.mean(dB))
        fs = {}
        for mode, blk in (("B1", B), ("CaseA", A), ("CaseB", C)):
            v = [tr.get("final_size") for tr in blk.get("trial_results", [])
                 if tr.get("final_size") is not None]
            fs[mode] = float(np.mean(v)) if v else float("nan")

        # 고정 N=385 (q<50)
        eb, ea, ec = estimates(B, nq), estimates(A, nq), estimates(C, nq)
        ntf = min(len(eb), len(ea), len(ec))
        if ntf < 2:
            continue
        k = min(FIXED_N_Q, nq)
        tk = true[:k]
        acc = {key: [] for key in ("B1", "CaseA", "CaseB", "CaseBp", "CaseAp")}
        for t in range(ntf):
            tj = (t + CTRL_OFFSET) % ntf
            b, a, c = eb[t][:k], ea[t][:k], ec[t][:k]
            acc["B1"].append(qerr(b, tk))
            acc["CaseA"].append(qerr(a, tk))
            acc["CaseB"].append(qerr(c, tk))
            acc["CaseBp"].append(qerr((eb[t][:k] + eb[tj][:k]) / 2.0, tk))
            acc["CaseAp"].append(qerr((ea[t][:k] + ea[tj][:k]) / 2.0, tk))
            for j in range(k):
                T = tk[j]
                if T <= 0:
                    continue
                bs = "over" if b[j] > T else "under"
                as_ = "over" if a[j] > T else "under"
                quad[(bs, as_)] += 1
        rec = {"method": method, "sel": sel, "dataset": dataset, "hA": hA, "hB": hB,
               "fs": fs}
        for key in acc:
            rec[key] = fmean(np.concatenate(acc[key]))
        records.append(rec)
        n_used += 1
        if limit and n_used >= limit:
            break
        if (fi + 1) % 400 == 0:
            print(f"  {fi+1}/{len(files)} 스캔...")

    print(f"\n[로드] 사용 measurement {n_used}")

    # ---- 그룹 보고 헬퍼 ----
    def report_group(label, recs):
        if not recs:
            return
        b1 = np.array([r["B1"] for r in recs])
        out = []
        for key in ("CaseA", "CaseB", "CaseBp", "CaseAp"):
            arr = np.array([r[key] for r in recs])
            delta = [(x - y) / y * 100 for x, y in zip(arr, b1) if y > 0 and np.isfinite(y)]
            out.append((key, float(np.mean(arr[np.isfinite(arr)])), betterpct(delta)))
        # CaseB vs CaseBp
        cbcp = [(r["CaseB"] - r["CaseBp"]) / r["CaseBp"] * 100
                for r in recs if r["CaseBp"] > 0 and np.isfinite(r["CaseBp"])]
        _, _, cbcp_pct, _ = betterpct(cbcp)
        qa = next(o for o in out if o[0] == "CaseA")
        qb = next(o for o in out if o[0] == "CaseB")
        qp = next(o for o in out if o[0] == "CaseBp")
        print(f"  {label:<22} n={len(recs):<4} "
              f"qe[B1 {float(np.mean(b1[np.isfinite(b1)])):.3f} "
              f"CaseA {qa[1]:.3f} CaseB {qb[1]:.3f} CaseB′ {qp[1]:.3f}]  "
              f"better%[CaseA {qa[2][2]:.0f} CaseB {qb[2][2]:.0f} CaseB′ {qp[2][2]:.0f}]  "
              f"CaseB>CaseB′ {cbcp_pct:.0f}%")

    print("\n=== 1. 적응 N 발산 (measurement별 trial-평균 final_size 중앙값) ===")
    for mode in ("B1", "CaseA", "CaseB"):
        v = [r["fs"][mode] for r in records if np.isfinite(r["fs"].get(mode, float("nan")))]
        if v:
            print(f"  {mode:<7}: 중앙값 {np.median(v):>8.0f}  평균 {np.mean(v):>9.0f}")

    print("\n=== 2. 헤드라인 재현 (전 1000 query, 적응) ===")
    for key, lab in (("hA", "CaseA vs B1"), ("hB", "CaseB vs B1")):
        d = [r[key] for r in records if r[key] is not None]
        b, n, pct, med = betterpct(d)
        print(f"  {lab:<14} better {pct:.1f}%  median Δ% {med:+.2f}%  (n={n})")
    print("  기대(v13): CaseA 35.2% · CaseB 89.1%")

    print("\n=== 3. ★ 고정 N=385 (q<50) 깨끗한 추정량 비교 — 전체 ===")
    report_group("전체", records)
    print("  해석: CaseA better%>50 = stratified가 B1보다 우수 / CaseB>CaseB′ <50% = CaseB가 통제군보다 못함")

    print("\n=== 4. method별 분해 (고정 N) — 진짜 신호 있는 method 탐색 ===")
    for meth in sorted({r["method"] for r in records}):
        report_group(meth, [r for r in records if r["method"] == meth])

    print("\n=== 5. selectivity별 분해 (고정 N) ===")
    for sel in sorted({r["sel"] for r in records}):
        report_group(f"sel={sel}", [r for r in records if r["sel"] == sel])

    print("\n=== 6. dataset별 분해 (고정 N) ===")
    for ds in sorted({r["dataset"] for r in records}):
        report_group(ds, [r for r in records if r["dataset"] == ds])

    print("\n=== 7. 부호 구조 (고정 N, q<50 pooled) — B1 vs stratified ===")
    tot = sum(quad.values())
    opp = quad[("over", "under")] + quad[("under", "over")]
    for key in (("over", "over"), ("over", "under"), ("under", "over"), ("under", "under")):
        print(f"  B1={key[0]:<6} strat={key[1]:<6}: {quad[key]:>9} ({quad[key]/tot*100:5.1f}%)")
    print(f"  → 반대 부호 {opp/tot*100:.1f}% (≈50%=독립, >50%=anti-corr)")


if __name__ == "__main__":
    main()
