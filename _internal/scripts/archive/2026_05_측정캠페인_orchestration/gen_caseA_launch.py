#!/usr/bin/env python3
"""task C — CaseA 전체 portfolio launch 산출물 생성.

aggregated_v12_full.parquet 의 CaseB 측정을 읽어, 동일 (cell, sel, K, method) 조합으로
CaseA(--mode CaseA) 측정 task 목록과 runner 스크립트를 생성한다.

CaseA = est_method 단독 (Bernoulli 미사용)이므로 B1 2단계 subsampling 이슈와 무관 —
task A 결론과 독립적으로 측정 가능.

산출:
  caseA_tasks_5_17.txt        — "cell|sel|K|method" 한 줄씩 (light cell 먼저 정렬)
  launch_caseA_full_5_17.sh   — 서버 tmux 용 runner (idempotent skip, || WARN, COMPLETE.flag)
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "_internal/cache/rq3/aggregated_v12_full.parquet"
OUT_DIR = Path(__file__).resolve().parent
TASKS = OUT_DIR / "caseA_tasks_5_17.txt"
RUNNER = OUT_DIR / "launch_caseA_full_5_17.sh"

df = pd.read_parquet(PARQUET)
cb = df[df["mode"] == "CaseB"].copy()
cb["K_eff"] = cb["K"].fillna(20).astype(int)
cb["sel_str"] = cb["sel"].astype(float).map(lambda x: f"{x:g}")

tup = cb[["cell", "sf", "sel_str", "K_eff", "method"]].drop_duplicates()
tup = tup.sort_values(["sf", "cell", "sel_str", "K_eff", "method"]).reset_index(drop=True)

n = len(tup)
print(f"CaseB rows={len(cb)}  CaseA mirror tasks={n}")
print("--- sf 분포 ---")
print(tup["sf"].value_counts().sort_index().to_string())
print("--- cell 분포 ---")
print(tup["cell"].value_counts().sort_index().to_string())
print("--- K 분포 ---")
print(tup["K_eff"].value_counts().sort_index().to_string())

# task 목록
TASKS.write_text(
    "\n".join(f'{r.cell}|{r.sel_str}|{r.K_eff}|{r.method}' for r in tup.itertuples()) + "\n"
)

# runner
runner = f'''#!/bin/bash
# task C — CaseA 전체 portfolio 측정 runner. gen_caseA_launch.py 가 생성. 5/17 세션.
# caseA_tasks_5_17.txt 의 {n}건을 --mode CaseA 로 측정. CaseA = est_method 단독.
# idempotent: 결과 JSON 존재 시 skip — 중단 후 재실행 안전.
#   사용: tmux new -d -s caseA 'bash launch_caseA_full_5_17.sh /tmp/caseA_tasks_5_17.txt'
set -u
SCRIPT=/mnt/hdd0/home/capstone2026/cache/rq3/measure_paper_exact.py
TASKS=${{1:-/tmp/caseA_tasks_5_17.txt}}
TS=$(date +%Y%m%d_%H%M)
OUT_BASE=/mnt/hdd0/home/capstone2026/results_caseA_full_${{TS}}
LOG=$OUT_BASE/logs
mkdir -p "$LOG"
TOTAL=$(wc -l < "$TASKS")
echo "[$(date)] === CaseA full portfolio — $TOTAL measurement ===" | tee "$LOG/_main.log"
N=0
while IFS='|' read -r CELL SEL K METHOD; do
  [ -z "$CELL" ] && continue
  N=$((N+1))
  OUT=$OUT_BASE/${{CELL}}_sel${{SEL}}_K${{K}}
  mkdir -p "$OUT"
  JF=$OUT/${{CELL}}_CaseA_${{METHOD}}.json
  if [ -f "$JF" ]; then
    echo "[$(date +%H:%M:%S)] SKIP $N/$TOTAL $CELL sel$SEL K$K $METHOD" | tee -a "$LOG/_main.log"
    continue
  fi
  echo "[$(date +%H:%M:%S)] === $N/$TOTAL $CELL sel$SEL K$K CaseA $METHOD ===" | tee -a "$LOG/_main.log"
  ENV=""
  [ "$K" != "20" ] && ENV="STRATA_K=$K"
  env $ENV python3 "$SCRIPT" --rq 3 --phase B --cell "$CELL" --mode CaseA \\
      --method "$METHOD" --sel "$SEL" --output "$OUT" \\
      2>&1 | tee "$LOG/${{CELL}}_sel${{SEL}}_K${{K}}_CaseA_${{METHOD}}.log" \\
      || echo "[WARN] $CELL sel$SEL K$K $METHOD failed" | tee -a "$LOG/_main.log"
done < "$TASKS"
NJSON=$(find "$OUT_BASE" -name '*_CaseA_*.json' -type f 2>/dev/null | wc -l)
NWARN=$(grep -c '\\[WARN\\]' "$LOG/_main.log" 2>/dev/null || echo 0)
echo "[$(date)] === CaseA full DONE — JSON $NJSON / $TOTAL, WARN $NWARN ===" | tee -a "$LOG/_main.log"
touch "$OUT_BASE/COMPLETE.flag"
'''
RUNNER.write_text(runner)
print(f"\nwrote {TASKS.name} ({n} lines)")
print(f"wrote {RUNNER.name}")
