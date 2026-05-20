#!/usr/bin/env python3
"""
8M dtarget JSON → query_selectivity_8m.parquet 5 sel 통합 변환.

Sources:
- phase7_8m_dtarget_midsel.json (sel 0.10, 0.30) — W1 측정
- phase7_8m_dtarget_lowsel.json (sel 0.01, 0.05) — W2 측정 (lowsel script)
- phase7_8m_dtarget_recalc_clean.json (sel 0.50) — 4월 phase7 측정 (단일 sel)

5 sel 모두 통합. 기존 query_selectivity_8m.parquet 덮어씀.
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

CACHE = Path('/mnt/hdd0/home/capstone2026/cache/rq1')

# (path, sel_override or None)
SOURCES = [
    (CACHE / 'phase7_8m_dtarget_midsel.json', None),       # results['0.10']/['0.30']
    (CACHE / 'phase7_8m_dtarget_lowsel.json', None),       # results['0.01']/['0.05']
    (CACHE / 'phase7_8m_dtarget_recalc_clean.json', 0.50), # results=list, sel 강제 부여
]


def main():
    rows = []
    for src, sel_force in SOURCES:
        if not src.exists():
            print(f'[skip] {src.name} (not found)')
            continue
        d = json.load(open(src))
        results = d.get('results', d)  # recalc_clean 은 results=list 직접
        if sel_force is not None and isinstance(results, list):
            for x in results:
                rows.append({
                    'query_id': int(x['query_id']),
                    'selectivity': float(sel_force),
                    'D_target': float(x['D_target_8m']),
                    'true_cardinality': int(x['true_card_8m']),
                    'actual_sel': float(x.get('actual_sel_8m', sel_force)),
                })
            print(f'[load] {src.name}: {len(results)} rows (sel={sel_force} 강제)')
        elif isinstance(results, dict):
            n_rows = 0
            for sel_key, items in results.items():
                sel = float(sel_key)
                for x in items:
                    rows.append({
                        'query_id': int(x['query_id']),
                        'selectivity': sel,
                        'D_target': float(x['D_target_8m']),
                        'true_cardinality': int(x['true_card_8m']),
                        'actual_sel': float(x.get('actual_sel_8m', sel)),
                    })
                    n_rows += 1
            print(f'[load] {src.name}: {n_rows} rows')
    if not rows:
        print('[ERROR] no source data')
        return
    df = pd.DataFrame(rows)
    out = CACHE / 'query_selectivity_8m.parquet'
    df.to_parquet(out, index=False)
    print(f'[saved] {out} ({len(df):,} rows)')
    print('selectivity coverage:')
    print(df.groupby('selectivity').size())

if __name__ == '__main__':
    main()
