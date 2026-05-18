#!/usr/bin/env python3
"""task A — B1 2단계 vs 1단계 동등성 검증 결과 분석.

verify_b1.py 가 /tmp/b1verify/result_{CELL}_{OLD_2단계,NEW_1단계}.json 에 쓴
N_SEED=100 측정 결과를 읽어, cell별로 OLD(2단계) vs NEW(1단계) 를 비교한다.

verify_b1.py 의 두 경로는 같은 seed_base(s*13+7) 로 trial s 를 측정하므로
vals[s] 는 seed 로 짝지어진다 — paired t-test / Wilcoxon 적용 가능.

판정: diff% 가 trial 변동성(CV ~7-10%) 안 + paired p>0.05 → 노이즈(REPORT v12 확정).
      모든 cell 에서 일관된 유의 차이 → 체계적 bias(B1 재측정 검토).

사용: python3 analyze_b1verify_5_17.py [결과디렉토리]   (default ./b1verify_results)
"""
import json
import glob
import sys
import numpy as np

try:
    from scipy import stats
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

D = sys.argv[1] if len(sys.argv) > 1 else "b1verify_results"
files = sorted(glob.glob(f"{D}/result_*.json"))
if not files:
    print(f"[!] {D}/result_*.json 없음")
    sys.exit(1)

by_cell = {}
for f in files:
    d = json.load(open(f))
    by_cell.setdefault(d["cell"], {})[d["label"]] = d

print(f"=== B1 2단계 vs 1단계 동등성 검증 — {len(by_cell)} cell, scipy={HAVE_SCIPY} ===\n")
hdr = (f"{'cell':<20}{'OLD mean':>10}{'NEW mean':>10}{'diff%':>9}"
       f"{'OLD CV%':>9}{'pair_t_p':>10}{'wilcox_p':>10}{'d_paired':>10}")
print(hdr)
print("-" * len(hdr))

rows = []
for cell, dd in sorted(by_cell.items()):
    old, new = dd.get("OLD_2단계"), dd.get("NEW_1단계")
    if not old or not new:
        print(f"{cell:<20}  (한쪽 결과 누락 — skip)")
        continue
    o = np.array(old["vals"], float)
    n = np.array(new["vals"], float)
    m = min(len(o), len(n))
    o, n = o[:m], n[:m]
    diff_pct = (old["mean"] - new["mean"]) / new["mean"] * 100.0
    old_cv = old["std"] / old["mean"] * 100.0
    pdiff = o - n
    d_paired = pdiff.mean() / pdiff.std(ddof=1) if pdiff.std(ddof=1) > 0 else 0.0
    if HAVE_SCIPY and not np.allclose(o, n):
        tp = stats.ttest_rel(o, n).pvalue
        wp = stats.wilcoxon(o, n).pvalue
    else:
        # manual paired t fallback
        se = pdiff.std(ddof=1) / np.sqrt(m)
        tstat = pdiff.mean() / se if se > 0 else 0.0
        tp = float("nan")
        wp = float("nan")
        print(f"  ({cell}: scipy 없음 — t-stat={tstat:.3f}, p 수동계산 생략)")
    print(f"{cell:<20}{old['mean']:>10.4f}{new['mean']:>10.4f}{diff_pct:>+8.2f}%"
          f"{old_cv:>8.1f}%{tp:>10.4f}{wp:>10.4f}{d_paired:>+10.3f}")
    rows.append((cell, diff_pct, tp, wp, d_paired))

print()
print("=== 종합 ===")
adiff = np.array([abs(r[1]) for r in rows])
print(f"|diff%| — mean {adiff.mean():.2f}%  max {adiff.max():.2f}%  min {adiff.min():.2f}%")
signs = [np.sign(r[1]) for r in rows]
print(f"diff 부호 — OLD>NEW {sum(s>0 for s in signs)} / OLD<NEW {sum(s<0 for s in signs)} (일관성 확인)")
if HAVE_SCIPY:
    n_sig = sum(1 for r in rows if r[2] == r[2] and r[2] < 0.05)
    n_sig01 = sum(1 for r in rows if r[2] == r[2] and r[2] < 0.01)
    print(f"paired t-test 유의 — p<0.05: {n_sig}/{len(rows)}  p<0.01: {n_sig01}/{len(rows)}")
print()
print("판정 가이드:")
print("  - |diff%| 전부 ~3% 이내 + 유의 cell 거의 없음 + 부호 불일치 → 노이즈 → REPORT v12 확정")
print("  - |diff%| 일관되게 크고(>3-5%) 부호 일치 + 대부분 유의 → 체계적 bias → B1 재측정 검토")
print("  - REPORT v12 §9: B1 run-level systematic bias 가 본래 ±10-25% — 그보다 작은 diff 는 노이즈역")
