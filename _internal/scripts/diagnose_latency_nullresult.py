#!/usr/bin/env python3
"""엔진 적용 검증 — latency 무개선 진단 정밀화 (Phase 0a-c).

measure_latency_realengine.py 산출 JSON(phase2+phase3+phase4_extension 56 cell)에서
"B1→CaseB가 왜 latency를 못 줄였나"를 반증 가능한 형태로 정량화한다.

  0a 노이즈 바닥   — 같은 variant 반복(rep) / 같은 plan 공유 variant 의 latency 변동계수
                     = 측정 노이즈. B1↔CaseB 신호가 이 아래면 "신호 < 노이즈".
  0b q-error↔latency — cell 고정효과를 뺀 within-cell 부분상관. naive pooled r 의
                     cell-mix 교란을 제거하고 "추정 정확도가 실행시간을 예측하나"를 본다.
  0c plan 전이     — baseline(HashJoin·base-table SeqScan) → 주입(NestedLoop·IndexScan)
                     plan-shape 전이 카탈로그 + selectivity 별 주입 이득.

서버 불필요 — 로컬 측정 JSON만으로 동작.
실행:  python3 _internal/scripts/diagnose_latency_nullresult.py
"""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "cache" / "rq3" / "latency"
DIRS = ("phase2", "phase3", "phase4_extension")


# --- 기본 유틸 ---------------------------------------------------------------

def plan_sig(plan: dict | None) -> tuple:
    """실행 계획 operator tree → pre-order Node Type 튜플."""
    if not plan:
        return ()
    sig = [plan.get("Node Type", "?")]
    for child in plan.get("Plans", []):
        sig += list(plan_sig(child))
    return tuple(sig)


def vlabel(v: dict) -> str:
    return v["condition"] if v["method"] is None else f"CaseB:{v['method']}"


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    syy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sxy / (sxx * syy) if sxx > 0 and syy > 0 else float("nan")


def pct(vals: list[float], p: float) -> float:
    if not vals:
        return float("nan")
    s = sorted(vals)
    k = (len(s) - 1) * p
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    return s[lo] if lo == hi else s[lo] + (s[hi] - s[lo]) * (k - lo)


def classify_plan(sig: tuple) -> str:
    """plan_signature 를 실행 전략 family 로 분류."""
    if not sig:
        return "미캡처"
    seq = sig.count("Seq Scan")
    idx = sig.count("Index Scan") + sig.count("Index Only Scan")
    hj = sig.count("Hash Join")
    nl = sig.count("Nested Loop")
    if nl >= 2 and idx >= 2:
        return "NL+IndexScan(index-driven)"
    if hj >= 2 and seq >= 3:
        return "HashJoin(base-table SeqScan)"
    return f"mixed(seq{seq}/idx{idx}/hj{hj}/nl{nl})"


# --- 로드 --------------------------------------------------------------------

def load_cells() -> list[dict]:
    cells = []
    for d in DIRS:
        for p in sorted((BASE / d).glob("latency_*.json")):
            try:
                cells.append(json.loads(p.read_text()))
            except Exception as e:  # noqa: BLE001
                print(f"[warn] {p.name}: {e}")
    return cells


def main() -> None:
    cells = load_cells()
    print(f"=== latency 무개선 진단 — {len(cells)} cell "
          f"({', '.join(DIRS)}) ===")

    # =====================================================================
    # 0a — 노이즈 바닥
    # =====================================================================
    print("\n" + "=" * 78)
    print("0a. 노이즈 바닥 — 측정 자체의 변동")
    print("=" * 78)

    rep_cv = []          # variant 1개 내부 15 rep 의 변동계수
    samepl_spread = []   # cell 내 같은 plan 공유 주입 variant 들의 (max-min)/median
    for r in cells:
        groups: dict[tuple, list[float]] = defaultdict(list)
        for v in r["variants"]:
            ex = v.get("exec_ms") or []
            if len(ex) >= 3:
                m = statistics.fmean(ex)
                if m > 0:
                    rep_cv.append(statistics.pstdev(ex) / m)
            # 주입 발동한 비-baseline variant 만 plan group 에
            if v["condition"] == "baseline":
                continue
            if not v.get("injection_fired", False):
                continue
            md = v.get("exec_ms_median")
            sig = plan_sig(v.get("plan_json"))
            if md is not None and sig:
                groups[sig].append(md)
        for sig, lats in groups.items():
            if len(lats) >= 3:
                med = statistics.median(lats)
                if med > 0:
                    samepl_spread.append((max(lats) - min(lats)) / med)

    print(f"\n[rep CV] 한 variant 의 15 rep 반복 변동계수 (모든 조건 고정 → 순수 타이밍 노이즈)")
    print(f"  n={len(rep_cv)}  중앙값 {statistics.median(rep_cv)*100:.1f}%  "
          f"p90 {pct(rep_cv,0.9)*100:.1f}%  최대 {max(rep_cv)*100:.1f}%")
    print(f"\n[same-plan spread] cell 내 '같은 plan·다른 주입값' variant 들의 latency 퍼짐")
    print(f"  (계획이 같으니 이 퍼짐은 노이즈 + plan 경계 미만의 추정값 효과)")
    print(f"  n={len(samepl_spread)} group  중앙값 {statistics.median(samepl_spread)*100:.1f}%  "
          f"p90 {pct(samepl_spread,0.9)*100:.1f}%  최대 {max(samepl_spread)*100:.1f}%")
    print(f"\n  → 측정 노이즈 바닥 = rep CV 중앙값 {statistics.median(rep_cv)*100:.0f}% "
          f"(p90 {pct(rep_cv,0.9)*100:.0f}%). 한 cell 안 latency 차이가 이 바닥")
    print(f"    아래면 측정으로 분리 불가 — B1↔CaseB 직접 paired 검정은 0d 참조.")

    # =====================================================================
    # 0b — q-error ↔ latency (within-cell 부분상관)
    # =====================================================================
    print("\n" + "=" * 78)
    print("0b. q-error ↔ latency — cell 고정효과 제거 부분상관")
    print("=" * 78)

    per_cell: list[tuple[str, list[tuple[float, float]]]] = []
    n_zero_inj = 0      # injection 발동했으나 injected_card==0 (zero-hit 추정)
    n_missing_inj = 0   # injected_card 필드 부재
    for r in cells:
        true_card = r.get("true_card")
        pts: list[tuple[float, float]] = []
        for v in r["variants"]:
            if v["condition"] == "baseline":
                continue
            if not v.get("injection_fired", False):
                continue
            inj = v.get("injected_card")
            md = v.get("exec_ms_median")
            if inj is None:
                n_missing_inj += 1
                continue
            if inj == 0:
                # zero-hit 추정 → injected_card=0 → q-error 정의상 무한대.
                # Pearson 에 못 넣지만 '존재'는 보고한다 (조용히 버리지 않는다).
                n_zero_inj += 1
                continue
            if true_card and inj > 0 and md:
                qerr = max(inj / true_card, true_card / inj)
                pts.append((qerr, md))
        if len(pts) >= 4:
            label = f"{r['query']} {r['dataset']} sf{r['sf']} sel{r['sel']} qid{r['query_id']}"
            per_cell.append((label, pts))

    naive_q = [q for _, pts in per_cell for q, _ in pts]
    naive_l = [l for _, pts in per_cell for _, l in pts]
    naive_r = pearson(naive_q, naive_l)

    res_q, res_l, cell_rs = [], [], []
    for _, pts in per_cell:
        qs = [q for q, _ in pts]
        ls = [l for _, l in pts]
        mq, ml = sum(qs) / len(qs), sum(ls) / len(ls)
        for q, l in pts:
            res_q.append(q - mq)
            res_l.append(l - ml)
        cell_rs.append(pearson(qs, ls))
    within_r = pearson(res_q, res_l)
    cell_rs_valid = [r for r in cell_rs if r == r]

    print(f"\n  주입 variant {len(naive_q)}개 / {len(per_cell)} cell  (q-error∈"
          f"[{min(naive_q):.3f}, {max(naive_q):.3f}])")
    print(f"  ※ injection_fired 中 injected_card=0 (zero-hit) {n_zero_inj}건 · 필드부재 "
          f"{n_missing_inj}건 — q-error 무한대라 상관서 제외 (q-error 분포 상단 절단 유의)")
    print(f"  naive pooled Pearson r          = {naive_r:+.3f}  (cell-mix 교란 포함)")
    print(f"  within-cell 부분상관 r          = {within_r:+.3f}  (cell 고정효과 제거)")
    print(f"  cell별 r 중앙값                 = {statistics.median(cell_rs_valid):+.3f}  "
          f"(n={len(cell_rs_valid)} cell)")
    print(f"  |cell별 r| > 0.5 인 cell         = "
          f"{sum(1 for r in cell_rs_valid if abs(r) > 0.5)}/{len(cell_rs_valid)}")
    print(f"\n  → within-cell r ≈ 0 이면: 한 cell 안에서 추정값을 정확히 해도(q-error↓) "
          f"실행시간이 따라오지 않는다 = 디커플.")

    # =====================================================================
    # 0c — plan-shape 전이
    # =====================================================================
    print("\n" + "=" * 78)
    print("0c. plan-shape 전이 — baseline → 주입")
    print("=" * 78)

    fam_count: dict[str, int] = defaultdict(int)
    transition: dict[tuple[str, str], int] = defaultdict(int)
    by_sel: dict[float, list[float]] = defaultdict(list)
    inj_help_by_sel: dict[float, list[float]] = defaultdict(list)

    for r in cells:
        by = {vlabel(v): v for v in r["variants"]}
        base = by.get("baseline")
        b1 = by.get("B1")
        orc = by.get("oracle")
        base_fam = classify_plan(plan_sig(base.get("plan_json"))) if base else "미캡처"
        for lab in ("baseline", "B1", "oracle"):
            v = by.get(lab)
            if v:
                fam_count[classify_plan(plan_sig(v.get("plan_json")))] += 1
        # baseline → oracle plan family 전이
        if base and orc:
            orc_fam = classify_plan(plan_sig(orc.get("plan_json")))
            transition[(base_fam, orc_fam)] += 1
        # sel별 주입 이득 (baseline_ms / oracle_ms)
        sel = r.get("sel")
        if sel is None:
            continue
        if base and orc:
            bm = base.get("exec_ms_median")
            om = orc.get("exec_ms_median")
            if bm and om and om > 0:
                by_sel[sel].append(bm / om)
        # sel별 baseline 대비 주입 cell — B1 기준
        if base and b1:
            bm = base.get("exec_ms_median")
            b1m = b1.get("exec_ms_median")
            if bm and b1m and b1m > 0:
                inj_help_by_sel[sel].append(bm / b1m)

    print("\n[plan family 분포] baseline/B1/oracle variant 전체")
    for fam, n in sorted(fam_count.items(), key=lambda kv: -kv[1]):
        print(f"  {fam:<34} {n}")

    print("\n[baseline → oracle plan family 전이]")
    for (bf, of), n in sorted(transition.items(), key=lambda kv: -kv[1]):
        arrow = "  ← 핵심 전이" if (bf.startswith("HashJoin") and of.startswith("NL")) else ""
        print(f"  {bf:<32} → {of:<28} {n} cell{arrow}")

    print("\n[selectivity별 주입 이득]  baseline_ms / 주입_ms  (>1 = 주입이 빠르게)")
    print(f"  {'sel':>8} {'n':>4} {'oracle 가속 중앙':>16} {'B1 가속 중앙':>14}")
    for sel in sorted(by_sel):
        orc_sp = by_sel[sel]
        b1_sp = inj_help_by_sel.get(sel, [])
        print(f"  {sel:>8} {len(orc_sp):>4} {statistics.median(orc_sp):>15.2f}× "
              f"{(statistics.median(b1_sp) if b1_sp else float('nan')):>13.2f}×")
    print(f"\n  → 주입 이득은 저 selectivity 에 집중. sel 이 커지면 baseline 의 "
          f"기본 추정(33%)이 우연히 맞는 영역이라 주입해도 이득이 사라진다.")

    # =====================================================================
    # 0d — B1 ↔ CaseB paired latency (직접 대조)
    # =====================================================================
    print("\n" + "=" * 78)
    print("0d. B1 ↔ CaseB paired latency — 같은 cell 내 직접 대조")
    print("=" * 78)

    pair_delta: list[float] = []   # (CaseB_ms − B1_ms)/B1_ms × 100, cell×method pair
    pair_cells: set[int] = set()
    for r in cells:
        by = {vlabel(v): v for v in r["variants"]}
        b1 = by.get("B1")
        if not b1:
            continue
        b1m = b1.get("exec_ms_median")
        if not b1m or b1m <= 0:
            continue
        for lab, v in by.items():
            if not lab.startswith("CaseB"):
                continue
            cm = v.get("exec_ms_median")
            if not cm or cm <= 0:
                continue
            pair_delta.append((cm - b1m) / b1m * 100.0)
            pair_cells.add(id(r))

    if pair_delta:
        faster = sum(1 for d in pair_delta if d < 0)
        slower = len(pair_delta) - faster
        med = statistics.median(pair_delta)
        mean = statistics.fmean(pair_delta)
        noise = statistics.median(rep_cv) * 100
        print(f"\n  B1↔CaseB pair {len(pair_delta)}개 / {len(pair_cells)} cell")
        print(f"  paired Δ% = (CaseB_ms − B1_ms)/B1_ms × 100   (음수 = CaseB 가 빠름)")
        print(f"  중앙값 {med:+.2f}%  평균 {mean:+.2f}%  "
              f"p10 {pct(pair_delta,0.1):+.1f}%  p90 {pct(pair_delta,0.9):+.1f}%")
        print(f"  CaseB 빠름 {faster} · 느림 {slower}  (≈50:50 이면 방향성 없음)")
        verdict = ("노이즈 미만 — latency 차이를 측정으로 분리 불가"
                   if abs(med) < noise else "노이즈 이상 — 추가 검정 필요")
        print(f"\n  → |중앙값 Δ% {abs(med):.2f}%| vs 측정 노이즈 바닥 rep CV {noise:.0f}%: {verdict}.")
    else:
        print("\n  [warn] B1↔CaseB pair 0개 — variant 라벨(B1 / CaseB:*) 확인 필요")

    print("\n" + "=" * 78)
    print(f"종합: (0a) 측정 노이즈 바닥 rep CV 중앙값 {statistics.median(rep_cv)*100:.0f}% · "
          f"(0d) B1↔CaseB paired Δ%")
    print("      중앙값이 그 노이즈 바닥 미만 → latency 차이를 측정으로 분리 불가 ·")
    print("      (0b) q-error 와 latency 디커플(within-cell r≈0) · (0c) latency 이득의")
    print("      정체 = base 테이블 SeqScan+HashJoin → IndexScan 이진 전이 — 주입값")
    print("      '정확도'가 아니라 '주입 유무'가 가른다. → B1→CaseB latency 개선 부재.")
    print("=" * 78)


if __name__ == "__main__":
    main()
