#!/usr/bin/env python3
"""est_b1 2-stage vs 1-stage 비교 — codex finding #1 영향 정량 (5/21).

phase4_extension_2stage_backup/ (2-stage cache) vs phase4_extension/ (1-stage all_vecs fix)
의 estimates parquet 에서 est_b1 을 dataset×sf×sel×query_id 별로 매칭 비교.
b1_2stage_verdict_5_17.md §3 의 +3~7% bias 와 대조.
"""
from pathlib import Path
import pandas as pd

BASE = Path("/mnt/hdd0/home/capstone2026/cache/rq3/latency")
OLD = BASE / "phase4_extension_2stage_backup"
NEW = BASE / "phase4_extension"

SPECS = [(ds, sf) for ds in ("DEEP", "SIFT", "SSN") for sf in (1, 10, 100)]
SPECS += [(ds, sf) for ds in ("WIKI", "YFCC") for sf in (1, 10)]

rows = []
for ds, sf in SPECS:
    fn = f"estimates_{ds}_sf{sf}.parquet"
    op, np_ = OLD / fn, NEW / fn
    if not op.exists() or not np_.exists():
        print(f"[skip] {ds} sf{sf}: old={op.exists()} new={np_.exists()}")
        continue
    odf, ndf = pd.read_parquet(op), pd.read_parquet(np_)
    # est_b1 은 method 무관 — dataset/sf/sel/query_id 별 1개 (drop_duplicates)
    okey = odf[["sel", "query_id", "est_b1"]].drop_duplicates()
    nkey = ndf[["sel", "query_id", "est_b1"]].drop_duplicates()
    m = okey.merge(nkey, on=["sel", "query_id"], suffixes=("_old", "_new"))
    if len(m) == 0:
        print(f"[skip] {ds} sf{sf}: 매칭 0")
        continue
    m["diff_pct"] = 100.0 * (m["est_b1_old"] - m["est_b1_new"]) / m["est_b1_new"]
    rows.append({
        "dataset": ds, "sf": sf, "n": len(m),
        "est_b1_old_mean": m["est_b1_old"].mean(),
        "est_b1_new_mean": m["est_b1_new"].mean(),
        "mean_diff_pct": m["diff_pct"].mean(),
        "median_diff_pct": m["diff_pct"].median(),
        "max_abs_diff_pct": m["diff_pct"].abs().max(),
    })

if rows:
    res = pd.DataFrame(rows)
    print("\n=== est_b1 2-stage(old) vs 1-stage(new) 비교 ===")
    print(res.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(f"\n전체 mean |diff%|: {res['mean_diff_pct'].abs().mean():.2f}%")
    print(f"전체 max |diff%|: {res['max_abs_diff_pct'].max():.2f}%")
    print("\nb1_2stage_verdict_5_17.md §3 대조: 메인 캠페인 verify_b1 = mean 3.37%, max 7.10%")
    res.to_csv(BASE / "phase4_extension/est_b1_compare.csv", index=False)
    print(f"saved {BASE / 'phase4_extension/est_b1_compare.csv'}")
else:
    print("비교 가능한 estimates 쌍 없음")
