"""EB-QAS smoke 1 cell launch (#5b 세션).

DEEP × sf=10 (A5-scale-sf10) × sel=0.01 (PAPER_SEL_DEFAULT) × n_queries=1000 × trials=10.
prior_mode_init="history" (정상 EB-QAS).

검증 항목 (Codex 결론 carry):
  - n_groups (코드 정정 후 cold-start gate — template_id="default" 효과)
  - avg_q_error_trimmed (finite, 측정 가능성 confirm)
  - mode_switch_count (안전장치 작동 빈도)
  - early_stop_count (sample_budget 도달 비율)
"""
import sys
from pathlib import Path

sys.path.insert(0, "/mnt/hdd0/home/capstone2026/cache/rq3")

from measure_paper_exact import measure_ebqas, build_cell_specs

cells = build_cell_specs()
target = next(c for c in cells if c.sub == "A5-scale-sf10")
print(f"smoke target: cell={target.sub} dataset={target.dataset} sf={target.sf} "
      f"table={target.table} sel={target.selectivities}")

output_dir = Path("/mnt/hdd0/home/capstone2026/cache/rq3/EBQAS_smoke_001021")
output_dir.mkdir(parents=True, exist_ok=True)

result = measure_ebqas(
    target,
    n_queries=1000,
    trials=10,
    prior_mode_init="history",
    output_dir=output_dir,
)

print("=" * 70)
print(f"smoke summary (history mode):")
print(f"  avg_q_error_trimmed = {result['avg_q_error_trimmed']:.4f}")
print(f"  n_trials            = {len(result['trial_results'])}")
for i, tr in enumerate(result["trial_results"]):
    print(f"  trial {i}: avg_qe={tr['avg_q_error_finite']:.3f} "
          f"n_groups={tr['n_groups']} early_stops={tr['early_stop_count']}/{1000} "
          f"mode_switches={tr['mode_switch_count']}")
print("=" * 70)
print(f"saved: {output_dir}/{target.sub}_EBQAS.json")
