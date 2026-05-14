#!/usr/bin/env python3
"""
8M dtarget JSON → query_selectivity_8m.parquet 변환.

8M 측정 (phase7_8m_midsel) 의 결과는 phase7_8m_dtarget_midsel.json 형식.
RQ3 wrapper 는 query_selectivity*.parquet 형식 (columns: query_id, selectivity,
D_target, true_cardinality) 을 기대. 본 스크립트가 그 변환을 수행.

사용 (서버):
    python3 /mnt/hdd0/home/capstone2026/cache/rq3/convert_8m_dtarget_to_parquet.py

산출:
    /mnt/hdd0/home/capstone2026/cache/rq1/query_selectivity_8m.parquet

이 산출이 생성되면 _measure_common.DATASETS_8M 의 query_sel 경로가 유효해지고,
RQ3 wrapper (run_minibatch.py 등) 에 --datasets DEEP_8M 으로 8M sensitivity 측정
가능.

8M 측정 sel 확장 (0.01/0.05/0.50 추가) 시 phase7_8m_dtarget_*.json 추가하고
본 스크립트 재실행.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

CACHE = Path("/mnt/hdd0/home/capstone2026/cache/rq1")

# 합칠 source — 우선 midsel (0.1/0.3), 추후 lowsel/highsel 추가 가능
SOURCES = [
    CACHE / "phase7_8m_dtarget_midsel.json",
    # CACHE / "phase7_8m_dtarget_lowsel.json",  # s=0.01/0.05 측정 후 활성
    # CACHE / "phase7_8m_dtarget_highsel.json", # s=0.50 측정 후 활성
]


def main():
    rows = []
    for src in SOURCES:
        if not src.exists():
            print(f"[skip] {src} (not found — 측정 미완료?)")
            continue
        d = json.load(open(src))
        for sel_key, items in d.get("results", {}).items():
            sel = float(sel_key)
            for x in items:
                rows.append({
                    "query_id": int(x["query_id"]),
                    "selectivity": sel,
                    "D_target": float(x["D_target_8m"]),
                    "true_cardinality": int(x["true_card_8m"]),
                    "actual_sel": float(x.get("actual_sel_8m", sel)),
                })
        print(f"[load] {src.name}: {sum(len(v) for v in d.get('results', {}).values())} rows")

    if not rows:
        print("[ERROR] no source data — 8M 측정 완료 후 다시 실행")
        return

    df = pd.DataFrame(rows)
    out = CACHE / "query_selectivity_8m.parquet"
    df.to_parquet(out, index=False)
    print(f"[saved] {out} ({len(df):,} rows)")
    print("\nselectivity coverage:")
    print(df.groupby("selectivity").size())


if __name__ == "__main__":
    main()
