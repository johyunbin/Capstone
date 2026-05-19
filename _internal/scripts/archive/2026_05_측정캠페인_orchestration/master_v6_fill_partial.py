#!/usr/bin/env python3
"""W4 master_v6_draft.md placeholder fill — partial result safe.
Reads /tmp/w4_15cell_summary.csv (scp'd locally to _internal/) and updates
[TBD measured] placeholders in master_v6_draft.md with current numbers.

Usage: python3 master_v6_fill_partial.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

LOCAL_CSV = Path("/Users/hyunbin/Capstone/_internal/_w4_partial_summary.csv")
MASTER = Path("/Users/hyunbin/Capstone/experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft.md")
WINNERS = ["hilbert", "hybrid", "minibatch_partial", "hdbscan"]


def main() -> None:
    if not LOCAL_CSV.exists():
        raise SystemExit(f"missing CSV: {LOCAL_CSV}")
    df = pd.read_csv(LOCAL_CSV)
    print(f"loaded {len(df)} rows from {LOCAL_CSV.name}")

    print("\n=== W4 cell coverage ===")
    cov = df.groupby(["dataset", "sf"]).size()
    for (ds, sf), n in cov.items():
        print(f"  {ds}_sf{sf:<3} : {n} method×sel rows")

    sub = df[
        (df["selectivity"] == 0.10)
        & (df["method"].isin(WINNERS))
        & df["paired_pct_vs_bern"].notna()
    ]
    if sub.empty:
        print("\n(no paired CI yet — sf1_pg UPDATE 미완 or rq2_5mode parquet 미생성)")
        return

    pivot = sub.pivot_table(
        index=["dataset", "sf"], columns="method", values="paired_pct_vs_bern"
    ).reindex(columns=WINNERS)

    print("\n=== 4강 method @ sel=0.10 (paired Δ% vs bern) ===")
    print(pivot.round(2).to_string())

    n_lines = []
    n_lines.append("## W4 4강 method paired Δ% vs bernoulli — sel=0.10\n")
    n_lines.append("| Cell | Hilbert | Hybrid | MB_partial | HDBSCAN |\n|---|---|---|---|---|")
    for (ds, sf), row in pivot.iterrows():
        cells = [f"{row.get(m, np.nan):+.2f}%" if pd.notna(row.get(m)) else "—" for m in WINNERS]
        n_lines.append(f"| {ds}_sf{sf} | {' | '.join(cells)} |")
    block = "\n".join(n_lines)

    print("\n=== injecting block into master_v6_draft.md ===")
    text = MASTER.read_text()
    marker = "<!-- FILL_4KANG_TABLE -->"
    if marker in text:
        new = re.sub(rf"{marker}.*?{marker}", f"{marker}\n{block}\n{marker}", text, flags=re.DOTALL)
        MASTER.write_text(new)
        print("  marker found — updated")
    else:
        out = MASTER.parent / (MASTER.stem + "_filled_partial.md")
        out.write_text(text + f"\n\n{marker}\n{block}\n{marker}\n")
        print(f"  marker missing — appended to {out.name}")


if __name__ == "__main__":
    main()
