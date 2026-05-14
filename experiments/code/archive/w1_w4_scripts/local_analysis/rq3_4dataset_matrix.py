#!/usr/bin/env python3
"""4-dataset matrix 분석 — DEEP 1M / DEEP 8M / SIFT 1M / SIFT 8M.

Cross-scale × cross-distribution paired CI + Cohen's d + recovery rate.

5/7 14:33 새 세션 — Option 1 (SIFT 1M subset) + SIFT 8M chain debug 완료 후 실행.

산출:
  - rq3_4dataset_matrix.csv  (method × sel × dataset × stats)
  - rq3_4dataset_matrix.md   (cross-scale narrative)
"""
from __future__ import annotations
import sys, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent
RESULTS = ROOT / "Capstone" / "experiments" / "results" / "rq3_agnostic"
RQ1 = ROOT / "Capstone" / "experiments" / "results" / "rq1_motivation"
RQ2 = ROOT / "Capstone" / "experiments" / "results" / "rq2_aware"
if not RESULTS.exists():
    BASE = Path(__file__).resolve().parent.parent.parent / "results"
    RESULTS = BASE / "rq3_agnostic"
    RQ1 = BASE / "rq1_motivation"
    RQ2 = BASE / "rq2_aware"

# Parquet inventory per dataset
# bern source = rq3_km20 / rq3_8m_km20 / per-dataset rq1 km20 (mode='bernoulli')
SOURCES = {
    'DEEP_1M': {
        'bern_path': RESULTS / 'rq3_km20.parquet',
        'rq3_dir': RESULTS,
        'rq3_pattern': 'rq3_{method}.parquet',
        'dataset_filter': 'DEEP',
    },
    'DEEP_8M': {
        'bern_path': RESULTS / 'rq3_8m_km20.parquet',
        'rq3_dir': RESULTS,
        'rq3_patterns': ['rq3_8m_{method}.parquet', 'rq3_8m_{method}_sel_expand.parquet'],
        'dataset_filter': 'DEEP_8M',
    },
    'SIFT_1.5M': {
        'bern_path': RESULTS / 'rq3_km20.parquet',
        'rq3_dir': RESULTS,
        'rq3_pattern': 'rq3_{method}.parquet',
        'dataset_filter': 'SIFT',
    },
    'SIFT_1M': {
        'bern_path': RQ1 / 'rq1_sift_1m_km20.parquet',
        'rq3_dir': RESULTS,
        'rq3_pattern': 'rq3_1m_sift_{method}.parquet',
        'dataset_filter': 'SIFT_1M',
    },
    'SIFT_8M': {
        'bern_path': RQ1 / 'rq1_sift_8m_km20.parquet',
        'rq3_dir': RESULTS,
        'rq3_pattern': 'rq3_8m_sift_{method}.parquet',
        'dataset_filter': 'SIFT_8M',
    },
}

METHODS = ["minibatch", "minibatch_partial", "random_proj", "pca1d",
           "hilbert", "zorder", "hybrid", "kdtree", "pq",
           "lsh", "kde_pilot", "distance_shell", "spectral", "birch",
           "gmm", "hdbscan", "sobol", "sparse_rp",
           "is_p50_noclip", "is_p50_clip", "is_p200_noclip", "is_p200_clip"]

SELECTIVITIES = [0.01, 0.05, 0.10, 0.30, 0.50]


def paired_bootstrap_ci(method_q, bern_q, n_boot=2000, seed=42, alpha=0.05):
    """Paired bootstrap 95% CI for Δ% = (method - bern) / bern * 100, using ratio of paired q_error."""
    rng = np.random.default_rng(seed)
    n = len(method_q)
    if n < 5:
        return float('nan'), float('nan'), float('nan')
    deltas = (method_q - bern_q) / bern_q * 100
    boot = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        boot.append(deltas[idx].mean())
    boot = np.array(boot)
    lo = np.quantile(boot, alpha / 2)
    hi = np.quantile(boot, 1 - alpha / 2)
    return float(deltas.mean()), float(lo), float(hi)


def cohen_d_paired(method_q, bern_q):
    diff = method_q - bern_q
    if len(diff) < 2 or diff.std() < 1e-12:
        return float('nan')
    return float(diff.mean() / diff.std())


def load_method_data(ds_key, method, ds_meta):
    """Load method parquet for ds, filter to dataset (some files have multiple)."""
    paths = []
    if 'rq3_patterns' in ds_meta:
        paths = [ds_meta['rq3_dir'] / p.format(method=method) for p in ds_meta['rq3_patterns']]
    elif 'rq3_pattern' in ds_meta:
        paths = [ds_meta['rq3_dir'] / ds_meta['rq3_pattern'].format(method=method)]
    df = None
    for p in paths:
        if p.exists():
            try:
                df_chunk = pd.read_parquet(p)
                if 'dataset' in df_chunk.columns:
                    df_chunk = df_chunk[df_chunk['dataset'] == ds_meta['dataset_filter']]
                if len(df_chunk) > 0:
                    df = df_chunk if df is None else pd.concat([df, df_chunk], ignore_index=True)
            except Exception:
                continue
    return df


def load_bern_data(ds_key, ds_meta):
    """BERN baseline (mode=bernoulli) from km20-style parquet."""
    p = ds_meta.get('bern_path')
    if p is None or not p.exists():
        return None
    df = pd.read_parquet(p)
    if 'mode' not in df.columns:
        return None
    if 'dataset' in df.columns:
        df = df[df['dataset'] == ds_meta.get('dataset_filter', ds_key)]
    df = df[df['mode'] == 'bernoulli']
    if len(df) == 0:
        return None
    return df


def compute_paired(method_df, bern_df, sel):
    if method_df is None or bern_df is None:
        return None
    m = method_df[method_df['selectivity'].round(2) == round(sel, 2)]
    b = bern_df[bern_df['selectivity'].round(2) == round(sel, 2)]
    if len(m) == 0 or len(b) == 0:
        return None
    keys = ['seed', 'query_id']
    merged = m.merge(b, on=keys, suffixes=('_m', '_b'))
    if len(merged) == 0:
        return None
    merged = merged.dropna(subset=['q_error_m', 'q_error_b'])
    merged = merged[(merged['q_error_m'] > 0) & (merged['q_error_b'] > 0)]
    if len(merged) < 5:
        return None
    mean_d, ci_lo, ci_hi = paired_bootstrap_ci(merged['q_error_m'].values, merged['q_error_b'].values)
    cd = cohen_d_paired(merged['q_error_m'].values, merged['q_error_b'].values)
    return {
        'n': len(merged),
        'delta_pct_mean': round(mean_d, 3),
        'ci_lo': round(ci_lo, 3),
        'ci_hi': round(ci_hi, 3),
        'ci0_excl': bool(ci_lo > 0 or ci_hi < 0),
        'cohen_d': round(cd, 4) if not np.isnan(cd) else None,
        'method_median': round(float(merged['q_error_m'].median()), 4),
        'bern_median': round(float(merged['q_error_b'].median()), 4),
    }


def main():
    rows = []
    for ds_key, ds_meta in SOURCES.items():
        bern = load_bern_data(ds_key, ds_meta)
        if bern is None:
            print(f'  skip {ds_key}: no BERN baseline')
            continue
        for method in METHODS:
            md = load_method_data(ds_key, method, ds_meta)
            if md is None:
                continue
            for sel in SELECTIVITIES:
                r = compute_paired(md, bern, sel)
                if r is None:
                    continue
                r.update({'dataset': ds_key, 'method': method, 'sel': sel})
                rows.append(r)
        print(f'  {ds_key}: {sum(1 for r in rows if r["dataset"] == ds_key)} cells')

    if not rows:
        print('no data — chain not yet finished?')
        return

    df = pd.DataFrame(rows)
    out_csv = RESULTS / 'rq3_4dataset_matrix.csv'
    df = df[['method', 'dataset', 'sel', 'n', 'delta_pct_mean', 'ci_lo', 'ci_hi',
             'ci0_excl', 'cohen_d', 'method_median', 'bern_median']]
    df.to_csv(out_csv, index=False)
    print(f'saved {out_csv} ({len(df)} cells)')

    # cross-scale summary table
    pivot = df.pivot_table(index=['method', 'sel'], columns='dataset',
                            values='delta_pct_mean', aggfunc='first')
    pivot_path = RESULTS / 'rq3_4dataset_pivot.csv'
    pivot.to_csv(pivot_path)
    print(f'saved {pivot_path}')

    # Cohen's d pivot
    cd_pivot = df.pivot_table(index=['method', 'sel'], columns='dataset',
                              values='cohen_d', aggfunc='first')
    cd_pivot_path = RESULTS / 'rq3_4dataset_cohen_d_pivot.csv'
    cd_pivot.to_csv(cd_pivot_path)
    print(f'saved {cd_pivot_path}')


if __name__ == '__main__':
    main()
