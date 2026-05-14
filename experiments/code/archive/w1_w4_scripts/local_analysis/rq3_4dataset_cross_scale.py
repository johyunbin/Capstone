#!/usr/bin/env python3
"""4-dataset cross-scale 분석 — DEEP 1M vs 8M, SIFT 1M vs 8M.

rq3_4dataset_matrix.csv 를 읽고 각 (method × sel) 의 cross-scale 변화를
Cohen's d / delta change 으로 정량 비교.

산출:
  rq3_4dataset_cross_scale.csv  (method × sel × scale_pair × stats)
  rq3_4dataset_cross_scale.md   (narrative)
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESULTS = ROOT / "Capstone" / "experiments" / "results" / "rq3_agnostic"
if not RESULTS.exists():
    RESULTS = Path(__file__).resolve().parent.parent.parent / "results" / "rq3_agnostic"

PAIRS = [
    ('DEEP_1M', 'DEEP_8M'),
    ('SIFT_1M', 'SIFT_8M'),
    ('SIFT_1M', 'SIFT_1.5M'),  # legacy comparison
]


def main():
    df = pd.read_csv(RESULTS / 'rq3_4dataset_matrix.csv')
    print(f'loaded {len(df)} cells, datasets: {sorted(df.dataset.unique())}')

    rows = []
    for ds_a, ds_b in PAIRS:
        a_rows = df[df.dataset == ds_a]
        b_rows = df[df.dataset == ds_b]
        if len(a_rows) == 0 or len(b_rows) == 0:
            print(f'  skip {ds_a} vs {ds_b}: missing data')
            continue
        merged = a_rows.merge(b_rows, on=['method', 'sel'], suffixes=(f'_{ds_a}', f'_{ds_b}'))
        for _, r in merged.iterrows():
            d_a = r[f'delta_pct_mean_{ds_a}']
            d_b = r[f'delta_pct_mean_{ds_b}']
            cd_a = r[f'cohen_d_{ds_a}']
            cd_b = r[f'cohen_d_{ds_b}']
            ci0_a = r[f'ci0_excl_{ds_a}']
            ci0_b = r[f'ci0_excl_{ds_b}']
            rows.append({
                'method': r['method'],
                'sel': r['sel'],
                'pair': f'{ds_a}_vs_{ds_b}',
                f'delta_{ds_a}': round(d_a, 3),
                f'delta_{ds_b}': round(d_b, 3),
                'delta_diff': round(d_b - d_a, 3),
                f'cohen_{ds_a}': round(cd_a, 3) if pd.notna(cd_a) else None,
                f'cohen_{ds_b}': round(cd_b, 3) if pd.notna(cd_b) else None,
                'ci_consistent': bool(ci0_a == ci0_b),
                'sign_consistent': bool(np.sign(d_a) == np.sign(d_b) if d_a != 0 and d_b != 0 else True),
            })
        print(f'  {ds_a} vs {ds_b}: {len([r for r in rows if r["pair"] == f"{ds_a}_vs_{ds_b}"])} cells')

    if not rows:
        return
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / 'rq3_4dataset_cross_scale.csv', index=False)
    print(f'saved {RESULTS / "rq3_4dataset_cross_scale.csv"} ({len(out)} cells)')

    # summary stats per pair
    print()
    print('=== Cross-scale summary ===')
    for ds_a, ds_b in PAIRS:
        sub = out[out.pair == f'{ds_a}_vs_{ds_b}']
        if len(sub) == 0:
            continue
        n_consistent_ci = sub.ci_consistent.sum()
        n_consistent_sign = sub.sign_consistent.sum()
        print(f'  {ds_a} vs {ds_b}: {len(sub)} cells')
        print(f'    CI 일관: {n_consistent_ci}/{len(sub)} ({n_consistent_ci/len(sub)*100:.0f}%)')
        print(f'    부호 일관: {n_consistent_sign}/{len(sub)} ({n_consistent_sign/len(sub)*100:.0f}%)')
        print(f'    Δ (B-A) median: {sub.delta_diff.median():+.2f}%')
        # top method-sel cells with large delta_diff
        top_diff = sub.reindex(sub.delta_diff.abs().sort_values(ascending=False).index).head(5)
        print(f'    largest delta_diff (B-A):')
        for _, r in top_diff.iterrows():
            print(f'      {r.method:20s} sel={r.sel} {ds_a}={r[f"delta_{ds_a}"]:+6.2f}%, {ds_b}={r[f"delta_{ds_b}"]:+6.2f}%, diff={r.delta_diff:+6.2f}%')


if __name__ == '__main__':
    main()
