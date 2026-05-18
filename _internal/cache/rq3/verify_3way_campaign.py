#!/usr/bin/env python3
"""
verify_3way_campaign.py — 3-way 캠페인 산출물 데이터 품질 전수 검증 (task I)

results_3way_5_17/ 의 3-way JSON 을 전수 스캔해 구조·값·길이·coverage 이상을 찾는다.
캠페인 진행 중 partial 에 돌리면 측정 결함을 조기 발견(미측정 sf100 영역 보강 가능),
완료 후 돌리면 task I 완료 검증.

검사 항목
- 구조 : top-level 키, B1/CaseA/CaseB mode 블록 키
- 길이 : trial_results=trials, estimates/q_errors=n_queries, true_cards=n_queries
- 값   : avg_q_error_trimmed 유한·≥1, final_size_mean 양수, trial avg_q_error_finite 유한
- 실패 : n_inf==n_queries (한 trial 전 쿼리 추정 실패)
- 일관 : 디렉토리명 ↔ JSON cell/selectivity
- 중복 : (cell,sel,K,method) 유일성
- coverage : tasks_3way_5_17.txt 대비 완료/미완

usage: python3 verify_3way_campaign.py
"""
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RESULTS = REPO / "_internal" / "cache" / "rq3" / "results_3way_5_17"
TASKS = REPO / "_internal" / "scripts" / "tasks_3way_5_17.txt"
DIR_RE = re.compile(r"^(?P<cell>.+)_sel(?P<sel>[\d.]+)_K(?P<K>\d+)$")
MODES = ("B1", "CaseA", "CaseB")


def bad_num(x) -> bool:
    """None / NaN / inf 이면 True."""
    return x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))


def main():
    json_files = sorted(RESULTS.glob("*/*_3way_*.json"))
    print(f"3-way JSON 전수 스캔: {len(json_files)}건  ({RESULTS})\n")

    anomalies = []          # (file, issue)
    issue_cat = Counter()   # 이슈 카테고리별 집계
    seen = Counter()        # (cell,sel,K,method) → 횟수
    completed = set()
    qt_range = defaultdict(lambda: [float("inf"), float("-inf")])  # mode → [min,max]

    for jf in json_files:
        rel = str(jf.relative_to(RESULTS))

        def bad(cat, msg):
            anomalies.append((rel, msg))
            issue_cat[cat] += 1

        m = DIR_RE.match(jf.parent.name)
        if not m:
            bad("dir", "디렉토리명 패턴 불일치")
            continue
        K = int(m.group("K"))
        dir_cell, dir_sel = m.group("cell"), float(m.group("sel"))
        try:
            d = json.loads(jf.read_bytes())
        except (json.JSONDecodeError, OSError) as e:
            bad("parse", f"JSON 파싱 실패: {e}")
            continue

        for k in ("cell", "method", "selectivity", "n_queries", "trials",
                  "true_cards", "B1", "CaseA", "CaseB"):
            if k not in d:
                bad("struct", f"top-level 키 '{k}' 부재")
        if any(k not in d for k in ("B1", "CaseA", "CaseB", "true_cards",
                                    "n_queries", "trials", "cell")):
            continue

        cell = d["cell"]
        method = (d.get("method") or "").strip().lower()
        nq, ntr = d["n_queries"], d["trials"]

        if cell != dir_cell:
            bad("consist", f"cell 불일치 json={cell} dir={dir_cell}")
        if abs(float(d.get("selectivity", -1)) - dir_sel) > 1e-9:
            bad("consist", f"sel 불일치 json={d.get('selectivity')} dir={dir_sel}")

        key = (cell, f"{dir_sel:g}", K, method)
        seen[key] += 1
        completed.add(key)

        if len(d["true_cards"]) != nq:
            bad("len", f"true_cards len {len(d['true_cards'])} != n_queries {nq}")

        for mode in MODES:
            blk = d.get(mode)
            if not isinstance(blk, dict):
                bad("struct", f"{mode} 블록 부재/비dict")
                continue
            for k in ("avg_q_error_trimmed", "final_size_mean", "trial_results"):
                if k not in blk:
                    bad("struct", f"{mode}.{k} 부재")

            qt = blk.get("avg_q_error_trimmed")
            if bad_num(qt):
                bad("value", f"{mode}.avg_q_error_trimmed 비정상 ({qt})")
            else:
                if qt < 0.999:
                    bad("value", f"{mode}.avg_q_error_trimmed < 1 ({qt:.4f}) — Q-error 정의 위반")
                rng = qt_range[mode]
                rng[0], rng[1] = min(rng[0], qt), max(rng[1], qt)

            fs = blk.get("final_size_mean")
            if bad_num(fs) or (fs is not None and fs <= 0):
                bad("value", f"{mode}.final_size_mean 비정상 ({fs})")

            tr = blk.get("trial_results", []) or []
            if len(tr) != ntr:
                bad("len", f"{mode}.trial_results {len(tr)} != trials {ntr}")
            for ti, t in enumerate(tr):
                if not isinstance(t, dict):
                    bad("struct", f"{mode}.trial{ti} 비dict")
                    continue
                if len(t.get("estimates", [])) != nq:
                    bad("len", f"{mode}.trial{ti}.estimates len {len(t.get('estimates', []))} != {nq}")
                if len(t.get("q_errors", [])) != nq:
                    bad("len", f"{mode}.trial{ti}.q_errors len {len(t.get('q_errors', []))} != {nq}")
                af = t.get("avg_q_error_finite")
                if bad_num(af):
                    bad("fail", f"{mode}.trial{ti}.avg_q_error_finite 비정상 ({af}) — 전 쿼리 실패 가능")
                if (t.get("n_inf") or 0) >= nq:
                    bad("fail", f"{mode}.trial{ti} 전 쿼리 inf (n_inf={t.get('n_inf')})")

    # --- 중복 ---
    dups = {k: c for k, c in seen.items() if c > 1}

    # --- coverage (tasks_3way_5_17.txt 대비) ---
    task_keys = set()
    if TASKS.exists():
        for ln in TASKS.read_text().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split("|")
            if len(parts) != 5:
                continue
            c, _sf, s, k, mth = parts
            task_keys.add((c, f"{float(s):g}", int(k), mth))
    missing = task_keys - completed
    extra = completed - task_keys

    # --- 보고 ---
    print("=" * 70)
    print("검증 결과")
    print("=" * 70)
    print(f"스캔 {len(json_files)}건 · 측정 unique {len(completed)} · anomaly {len(anomalies)}건")
    print(f"중복 (cell,sel,K,method): {len(dups)}건")
    if task_keys:
        print(f"coverage: task {len(task_keys)} 중 완료 {len(task_keys & completed)} / "
              f"미완 {len(missing)} / task목록밖 {len(extra)}")
    print(f"\nmode 별 avg_q_error_trimmed 범위 (B1 K=10 결함 시 3.0대):")
    for mode in MODES:
        lo, hi = qt_range[mode]
        print(f"  {mode}: [{lo:.4f}, {hi:.4f}]")

    if anomalies:
        print(f"\n--- anomaly {len(anomalies)}건 · 카테고리: {dict(issue_cat)} ---")
        for f, msg in anomalies[:40]:
            print(f"  {f}: {msg}")
        if len(anomalies) > 40:
            print(f"  ... 외 {len(anomalies) - 40}건")
    else:
        print("\n✅ anomaly 0건 — 구조·값·길이 전부 정상")

    if dups:
        print(f"\n--- 중복 측정 {len(dups)}건 ---")
        for k, c in list(dups.items())[:20]:
            print(f"  {k}: {c}회")
    if extra:
        print(f"\n--- task 목록에 없는 측정 {len(extra)}건 ---")
        for k in list(extra)[:20]:
            print(f"  {k}")
    if missing:
        print(f"\n미완 {len(missing)}건 — campaign 진행 중이면 정상, 완료 후엔 0이어야.")
        miss_cells = Counter(k[0] for k in missing)
        print(f"  미완 cell 분포: {dict(miss_cells)}")

    verdict = "PASS" if (not anomalies and not dups and not extra) else "CHECK"
    print(f"\n=== {verdict} ===")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
