#!/usr/bin/env python3
"""
aggregate_v13.py — 3-way matched 캠페인 통합 집계 (task I, 5/17 세션)

목적
----
results_3way_5_17/ 의 3-way JSON 을 통합. 각 JSON 은 measure_3way 가 한 측정에서
B1·CaseA·CaseB 를 matched 산출한 결과로, B1/CaseA/CaseB nested 키를 갖는다.
→ JSON 1건 = 3 row (mode 별). 1508 JSON → 통합 4524 row.

framing
-------
- B1     = 대조군: paper §V-B Bernoulli random sampling + Adaptive Eq 1-6.
           본 캠페인의 B1 은 1단계 (all_vecs 직접) — 2단계 strata 캐시를 우회한다
           (b1_2stage_verdict_5_17 조치).
- CaseA  = 실험군 (완전 대체): est = est_method (16 method stratification 단독).
- CaseB  = 실험군 (결합):     est = (est_b1 + est_method) / 2 simple average.
B1·CaseA·CaseB 가 한 측정에서 같은 trial·query 조건으로 나와 완벽히 matched.

v12 와의 차이
------------
- v12: JSON 1건 = 1 mode. B1 80 + CaseB 1364 별도 측정 → pairing 시 B1 lookup·fallback.
- v13: JSON 1건 = 3 mode. matched → fallback 불필요, K=10 B1 결함 없음
       (B1 1단계, STRATA_K 2단계 캐시 우회).

Schema (long, 1 row per (cell,sel,K,method,mode))
-------------------------------------------------
json_id, cell, dataset, sf, dim, type_label, single_multi,
mode, method, paradigm, K, sel, n_queries, trials,
qe_trim, qe_mean, qe_median, qe_std,
final_size, final_size_std, n_inf_total, n_finite_total,
trial_qe_list, trial_size_list, eta_final,
fit_time_sec, cache_time_sec, kst, json_path

usage
-----
  python3 aggregate_v13.py [--results-dir DIR] [--out-suffix _full]
입력: _internal/cache/rq3/results_3way_5_17/{cell}_sel{sel}_K{K}/{cell}_3way_{method}.json
출력: _internal/cache/rq3/aggregated_v13_full.parquet  (+ .csv)
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "_internal" / "cache" / "rq3"))
from aggregate_v12 import CELL_META, PARADIGM_MAP  # noqa: E402

DEFAULT_RESULTS = REPO_ROOT / "_internal" / "cache" / "rq3" / "results_3way_5_17"
OUT_DIR = REPO_ROOT / "_internal" / "cache" / "rq3"

MODES = ("B1", "CaseA", "CaseB")
# 디렉토리명 = {cell}_sel{sel}_K{K} — cell 은 하이픈/sf 포함 가능, _sel·_K 가 경계
DIR_RE = re.compile(r"^(?P<cell>.+)_sel(?P<sel>[\d.]+)_K(?P<K>\d+)$")


def parse_mode_block(block: dict) -> dict:
    """B1/CaseA/CaseB 블록 → trial-level 집계."""
    trial_results = block.get("trial_results", []) or []
    qe_list, size_list, eta_list = [], [], []
    n_inf_total = n_finite_total = 0
    for tr in trial_results:
        if not isinstance(tr, dict):
            continue
        qv = tr.get("avg_q_error_finite")
        sv = tr.get("final_size")
        ev = tr.get("final_eta")
        if qv is not None:
            qe_list.append(float(qv))
        if sv is not None:
            size_list.append(float(sv))
        if ev is not None:
            eta_list.append(float(ev))
        n_inf_total += int(tr.get("n_inf", 0) or 0)
        n_finite_total += int(tr.get("n_finite", 0) or 0)
    qe_s = pd.Series(qe_list, dtype="float64")
    size_s = pd.Series(size_list, dtype="float64")
    return {
        "qe_trim": block.get("avg_q_error_trimmed"),
        "qe_mean": float(qe_s.mean()) if len(qe_s) else None,
        "qe_median": float(qe_s.median()) if len(qe_s) else None,
        "qe_std": float(qe_s.std(ddof=1)) if len(qe_s) > 1 else None,
        "final_size": block.get("final_size_mean"),
        "final_size_std": block.get("final_size_std"),
        "size_median": float(size_s.median()) if len(size_s) else None,
        "n_inf_total": n_inf_total,
        "n_finite_total": n_finite_total,
        "trial_qe_list": json.dumps(qe_list),
        "trial_size_list": json.dumps(size_list),
        "eta_final": float(pd.Series(eta_list).mean()) if eta_list else None,
    }


def parse_one(path: Path) -> list:
    """3-way JSON 1건 → 3 row (B1/CaseA/CaseB). 실패 시 []."""
    try:
        d = json.loads(path.read_bytes())
    except (json.JSONDecodeError, OSError) as e:
        print(f"  skip {path.name}: {e}", file=sys.stderr)
        return []

    # K 는 디렉토리명에서만 — JSON top-level 에 없음. cell/sel 은 JSON 우선, 디렉토리와 cross-check.
    m = DIR_RE.match(path.parent.name)
    if not m:
        print(f"  skip {path}: 디렉토리명 패턴 불일치", file=sys.stderr)
        return []
    K = int(m.group("K"))
    dir_cell = m.group("cell")
    dir_sel = float(m.group("sel"))

    cell = d.get("cell", dir_cell)
    sel = float(d.get("selectivity", dir_sel))
    method = (d.get("method") or "").strip().lower()
    if cell != dir_cell:
        print(f"  warn {path.name}: cell mismatch json={cell} dir={dir_cell}", file=sys.stderr)
    if abs(sel - dir_sel) > 1e-9:
        print(f"  warn {path.name}: sel mismatch json={sel} dir={dir_sel}", file=sys.stderr)

    cm = CELL_META.get(cell, {})
    base = {
        "json_id": f"{cell}|{sel:g}|{K}|{method}",
        "cell": cell,
        "dataset": cm.get("dataset", d.get("dataset", "")),
        "sf": d.get("sf", cm.get("sf")),
        "dim": cm.get("dim"),
        "type_label": cm.get("type", "?").replace("Type", "Type "),
        "single_multi": cm.get("single_multi", "?"),
        "method": method,
        "paradigm": PARADIGM_MAP.get(method, "Pother"),
        "K": K,
        "sel": sel,
        "n_queries": d.get("n_queries"),
        "trials": d.get("trials"),
        "fit_time_sec": d.get("fit_time_sec"),
        "cache_time_sec": d.get("cache_time_sec"),
        "kst": d.get("kst"),
        "json_path": str(path.relative_to(REPO_ROOT)),
    }
    rows = []
    for mode in MODES:
        block = d.get(mode)
        if not isinstance(block, dict):
            print(f"  warn {path.name}: {mode} 블록 부재", file=sys.stderr)
            continue
        row = dict(base)
        row["mode"] = mode
        row.update(parse_mode_block(block))
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default=str(DEFAULT_RESULTS))
    ap.add_argument("--out-suffix", default="_full")
    args = ap.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        sys.exit(f"results dir 부재: {results_dir}")

    json_files = sorted(results_dir.glob("*/*_3way_*.json"))
    print(f"3-way JSON: {len(json_files)}건 스캔  ({results_dir})")

    rows, n_fail = [], 0
    for i, p in enumerate(json_files, 1):
        r = parse_one(p)
        if not r:
            n_fail += 1
        rows.extend(r)
        if i % 200 == 0:
            print(f"  {i}/{len(json_files)} ...")

    df = pd.DataFrame(rows)
    print(f"\n통합 row: {len(df)}  (JSON {len(json_files)} × 3 mode 기대 {len(json_files) * 3})")
    if n_fail:
        print(f"  파싱 실패 JSON: {n_fail}건")

    out_parquet = OUT_DIR / f"aggregated_v13{args.out_suffix}.parquet"
    out_csv = OUT_DIR / f"aggregated_v13{args.out_suffix}.csv"
    df.to_parquet(out_parquet, index=False)
    df.to_csv(out_csv, index=False)
    print(f"  wrote {out_parquet}")
    print(f"  wrote {out_csv}")

    # --- sanity ---
    print("\n=== sanity ===")
    print(f"  cells: {df['cell'].nunique()}  methods: {df['method'].nunique()}")
    print(f"  mode 분포: {df.groupby('mode').size().to_dict()}")
    print(f"  K 분포: {df.groupby('K').size().to_dict()}")
    print(f"  sel 분포: {df.groupby('sel').size().to_dict()}")
    mode_cnt = df.groupby("json_id")["mode"].nunique()
    bad = mode_cnt[mode_cnt != 3]
    print(f"  json_id 3-mode 완비: {int((mode_cnt == 3).sum())} / 불완전: {len(bad)}")
    # K=10 B1 qe_trim 검증 — v12 K=10 B1 결함 (qe_trim 2.2~3.3) 대비 정상 (1.6~1.7) 여부
    print("  --- B1 qe_trim by K (v12 K=10 결함 검증) ---")
    for K in sorted(df["K"].dropna().unique()):
        b1k = df[(df["mode"] == "B1") & (df["K"] == K)]
        if not b1k.empty:
            print(f"  B1 K={int(K)}: qe_trim mean={b1k['qe_trim'].mean():.4f} "
                  f"[{b1k['qe_trim'].min():.4f}, {b1k['qe_trim'].max():.4f}]  "
                  f"n_inf_total mean={b1k['n_inf_total'].mean():.1f}  n={len(b1k)}")


if __name__ == "__main__":
    main()
