#!/usr/bin/env python3
"""task A 후속 — B1 1단계(paper-faithful) 재측정 launch 산출물 생성.

task A 검증 결과: B1 의 2단계 subsampling 이 6 cell 중 3개에서 Q-error 를 +3~7%
유의하게 부풀린다(부분적 cell 의존 bias). handoff §5 의 "bias" 분기에 따라
측정 portfolio 전체의 B1 을 1단계(all_vecs 직접) 코드로 재측정한다.

현재 measure_paper_exact.py 의 B1 mode 는 이미 1단계(all_vecs)다 — 그대로 재측정하면
paper-faithful 1단계 B1 이 나온다. 기존 2단계 B1 은 보존(별 results 디렉토리), task I
에서 2단계(primary, REPORT v12 정합) vs 1단계(sensitivity) 양쪽으로 분석한다.

aggregated_v12_full.parquet 의 B1 측정 80건과 동일 (cell, sel, K) 조합으로 재측정.

산출:
  b1redo_tasks_5_17.txt       — "cell|sel|K" 한 줄씩
  launch_b1redo_5_17.sh       — 서버 tmux 용 runner (idempotent skip)
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "_internal/cache/rq3/aggregated_v12_full.parquet"
OUT_DIR = Path(__file__).resolve().parent
TASKS = OUT_DIR / "b1redo_tasks_5_17.txt"
RUNNER = OUT_DIR / "launch_b1redo_5_17.sh"

df = pd.read_parquet(PARQUET)
b1 = df[df["mode"] == "B1"].copy()
b1["K_eff"] = b1["K"].fillna(20).astype(int)
b1["sel_str"] = b1["sel"].astype(float).map(lambda x: f"{x:g}")

tup = b1[["cell", "sf", "sel_str", "K_eff"]].drop_duplicates()
tup = tup.sort_values(["sf", "cell", "sel_str", "K_eff"]).reset_index(drop=True)

n = len(tup)
print(f"B1 rows={len(b1)}  B1 1단계 재측정 tasks={n}")
print("--- sf 분포 ---")
print(tup["sf"].value_counts().sort_index().to_string())
print("--- K 분포 ---")
print(tup["K_eff"].value_counts().sort_index().to_string())
print("--- cell 분포 ---")
print(tup["cell"].value_counts().sort_index().to_string())

TASKS.write_text(
    "\n".join(f'{r.cell}|{r.sel_str}|{r.K_eff}' for r in tup.itertuples()) + "\n"
)

runner = f'''#!/bin/bash
# task A 후속 — B1 1단계(paper-faithful) 재측정 runner. gen_b1redo_launch.py 생성. 5/17.
# b1redo_tasks_5_17.txt 의 {n}건을 --mode B1 로 재측정. 현재 코드 B1 mode = 1단계(all_vecs).
# idempotent: 결과 JSON 존재 시 skip.
#   사용: bash launch_b1redo_5_17.sh /tmp/b1redo_tasks_5_17.txt
set -u
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TASKS=${{1:-/tmp/b1redo_tasks_5_17.txt}}
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_b1redo_1stage_${{TS}}
LOG=$OUT_BASE/logs
mkdir -p "$LOG"
TOTAL=$(wc -l < "$TASKS")
echo "[$(date)] === B1 1단계 재측정 — $TOTAL measurement ===" | tee "$LOG/_main.log"
N=0
while IFS='|' read -r CELL SEL K; do
  [ -z "$CELL" ] && continue
  N=$((N+1))
  OUT=$OUT_BASE/${{CELL}}_sel${{SEL}}_K${{K}}
  mkdir -p "$OUT"
  JF=$OUT/${{CELL}}_B1.json
  if [ -f "$JF" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $N/$TOTAL $CELL sel$SEL K$K B1" | tee -a "$LOG/_main.log"
    continue
  fi
  echo "[$(date +%H:%M:%S)] === $N/$TOTAL $CELL sel$SEL K$K B1 (1단계) ===" | tee -a "$LOG/_main.log"
  ENV=""
  [ "$K" != "20" ] && ENV="STRATA_K=$K"
  env $ENV python3 "$SCRIPT" --rq 3 --phase A --cell "$CELL" --mode B1 \\
      --sel "$SEL" --output "$OUT" \\
      2>&1 | tee "$LOG/${{CELL}}_sel${{SEL}}_K${{K}}_B1.log" \\
      || echo "[WARN] $CELL sel$SEL K$K B1 failed" | tee -a "$LOG/_main.log"
done < "$TASKS"
NJSON=$(find "$OUT_BASE" -name '*_B1.json' -type f 2>/dev/null | wc -l)
NWARN=$(grep -c '\\[WARN\\]' "$LOG/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === B1 1단계 재측정 DONE — JSON $NJSON / $TOTAL, WARN $NWARN ===" | tee -a "$LOG/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
'''
RUNNER.write_text(runner)
print(f"\nwrote {TASKS.name} ({n} lines)")
print(f"wrote {RUNNER.name}")
