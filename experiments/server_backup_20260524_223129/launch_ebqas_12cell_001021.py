"""EB-QAS 12 cell × 2 mode = 24 단위 sequential launch (#5b 세션).

DEEP·SIFT·WIKI × sf{1,10} × 2 prior_mode_init = 12 cell × 2 mode = 24 단위.
1 단위 ~1분 (smoke 1.5분 base) → 전체 ~25분 sequential.

코드 정정 carry (Codex (a)(b)(c)(d)(e)(f) 6 항목):
  - params.n_cap honor (Codex a)
  - no_history mode = Beta(1,1) 고정 + update skip (Codex b)
  - assert_paired_join_invariant 4-tuple key + 전수 비교 (Codex c)
  - make_group_key template_id="default" cold-start gate (Codex d)
  - q_log_floor logging only (Codex f)

각 cell × 각 mode 결과는 EBQAS_24cell_001021/<cell.sub>_<EBQAS|EBQAS-no-history>.json.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")
from measure_paper_exact import measure_ebqas, build_cell_specs

# DEEP·SIFT·WIKI × sf{1,10} = 6 cell × 2 mode = 12 단위
TARGET_SUBS = [
    "A5-scale-sf1", "A5-scale-sf10",        # DEEP × sf{1,10}
    "A5-scale-sf1-SIFT", "A5-scale-sf10-SIFT",   # SIFT × sf{1,10}
    "A6-WIKI-sf1", "A6-WIKI-sf10",          # WIKI × sf{1,10}
]
MODES = ["history", "no_history"]

cells = build_cell_specs()
cells_map = {c.sub: c for c in cells}

output_dir = Path("/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_24cell_001021")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"=== 24 cell launch start (12 cell × 2 mode) ===", flush=True)
print(f"output_dir: {output_dir}", flush=True)
print(f"targets: {TARGET_SUBS}", flush=True)
print(f"modes: {MODES}", flush=True)

results = []
t_start = time.time()

for sub in TARGET_SUBS:
    target = cells_map.get(sub)
    if target is None:
        print(f"[SKIP] cell {sub} not found in build_cell_specs", flush=True)
        continue
    for mode in MODES:
        print(f"\n--- launching cell={sub} mode={mode} ---", flush=True)
        t0 = time.time()
        try:
            result = measure_ebqas(
                target,
                n_queries=1000,
                trials=10,
                prior_mode_init=mode,
                output_dir=output_dir,
            )
            dur = time.time() - t0
            avg_qe = result["avg_q_error_trimmed"]
            n_groups = result["trial_results"][0]["n_groups"]
            mode_switches = sum(tr["mode_switch_count"] for tr in result["trial_results"])
            early_stops = sum(tr["early_stop_count"] for tr in result["trial_results"])
            print(f"  → avg_qe_trimmed={avg_qe:.4f} n_groups={n_groups} "
                  f"mode_switches={mode_switches} early_stops={early_stops} dur={dur:.1f}s",
                  flush=True)
            results.append({
                "cell": sub, "mode": mode,
                "avg_qe": avg_qe, "n_groups": n_groups,
                "mode_switches": mode_switches, "early_stops": early_stops,
                "dur_sec": dur,
            })
        except Exception as e:
            dur = time.time() - t0
            print(f"  ERROR: {type(e).__name__}: {e} (dur={dur:.1f}s)", flush=True)
            results.append({"cell": sub, "mode": mode, "error": str(e), "dur_sec": dur})

t_total = time.time() - t_start
print(f"\n=== 24 cell launch complete: {len(results)} units, total {t_total/60:.1f} min ===",
      flush=True)
print(f"\nsummary (avg_qe by cell × mode):")
for r in results:
    if "error" in r:
        print(f"  {r['cell']:25s} {r['mode']:12s} ERROR: {r['error'][:60]}")
    else:
        print(f"  {r['cell']:25s} {r['mode']:12s} avg_qe={r['avg_qe']:.4f} "
              f"groups={r['n_groups']} dur={r['dur_sec']:.0f}s")
print(f"\nsaved jsons: {output_dir}")
