#!/usr/bin/env python3
"""
RQ3 8M sensitivity — sel 5단계 확장 dispatcher (sel 0.01/0.05/0.50 추가 측정만).

기존 run_8m_sensitivity.py 의 16-method dispatch 를 그대로 사용하되:
- _measure_common.SELECTIVITIES 를 [0.01, 0.05, 0.50] 로 override (이미 측정된 0.10/0.30 제외)
- output prefix 에 _sel_expand suffix 추가 → rq3_8m_{method}_sel_expand.parquet

사용:
    python3 run_8m_sensitivity_sel_expand.py
    python3 run_8m_sensitivity_sel_expand.py --methods minibatch hilbert  # 일부만
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import _measure_common as mc

# === 핵심: SELECTIVITIES override (run_method_measurement 내부 loop 가 mc.SELECTIVITIES 참조) ===
mc.SELECTIVITIES = [0.01, 0.05, 0.50]
print(f'[INFO] SELECTIVITIES override: {mc.SELECTIVITIES}')

from _measure_common import DATASETS_8M, fetch_all_vectors_safe, kst, save_parquet_meta
import run_8m_sensitivity as base
# base.METHOD_DISPATCH, base.measure_one_method 그대로 사용


def main():
    ap = argparse.ArgumentParser(description='RQ3 8M sel 5단계 확장')
    ap.add_argument('--methods', nargs='*', default=list(base.METHOD_DISPATCH.keys()))
    ap.add_argument('--n-queries', type=int, default=100)
    ap.add_argument('--learn-seed', type=int, default=42)
    ap.add_argument('--learn-frac', type=float, default=0.01)
    args = ap.parse_args()

    print(f'[{kst()}] === RQ3 8M sel_expand (sel ∈ {mc.SELECTIVITIES}) ===')
    print(f'[{kst()}] methods: {args.methods}')

    for ds in DATASETS_8M:
        if not ds['query_sel'].exists():
            print(f'⚠️ {ds["query_sel"]} 없음')
            continue
        print(f'\n[{kst()}] === fetching 8M vectors ({ds["table"]}) ===')
        all_vecs, _ = fetch_all_vectors_safe(ds)

        for method in args.methods:
            if method not in base.METHOD_DISPATCH:
                print(f'⚠️ unknown method "{method}" — skip')
                continue
            t_method = time.time()
            try:
                rows = base.measure_one_method(
                    method, ds, all_vecs, args.n_queries,
                    args.learn_seed, args.learn_frac,
                )
                save_parquet_meta(
                    rows, prefix=f'rq3_8m_{method}_sel_expand',
                    extra_meta={
                        'method': method, 'dataset': ds['name'],
                        'learn_seed': args.learn_seed, 'learn_frac': args.learn_frac,
                        'n_queries': args.n_queries,
                        'sel_filter': mc.SELECTIVITIES,
                    },
                )
                print(f'[{kst()}]   {method} total: {time.time()-t_method:.0f}s, {len(rows)} rows')
            except Exception as e:
                print(f'[ERROR] {method}: {e}')
                import traceback; traceback.print_exc()

    print(f'\n[{kst()}] === RQ3 8M sel_expand 완료 ===')


if __name__ == '__main__':
    main()
