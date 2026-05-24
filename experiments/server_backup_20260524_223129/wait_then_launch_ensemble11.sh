#!/usr/bin/env bash
# X6 (4강 ensemble) 완료 후 11-method launcher sequential 실행
# 목표: HDD I/O 동시점유 회피 (X6 끝날 때까지 대기 → 11-method 시작)

set -u
cd /mnt/hdd0/home/capstone2026

LOG_DIR=logs
mkdir -p "$LOG_DIR"

WAIT_LOG=$LOG_DIR/wait_ensemble11_20260508.log

echo "=== wait for X6 (4강 ensemble) finish ===" | tee -a "$WAIT_LOG"
echo "started at $(date '+%Y-%m-%d %H:%M:%S KST')" | tee -a "$WAIT_LOG"

# X6 처음 PID 확인 (현재 SSN sf10 hdbscan 등 진행중)
while true; do
  # 현재 base 4강 method × cell 중 미완성이 1개라도 있고, ensemble 프로세스가 살아있으면 wait
  remaining=$(python3 -c "
import os
DS = ['DEEP','SIFT','SSN','YFCC','WIKI']
SFS = [1,10]
MS = ['hdbscan','minibatch_partial','hilbert','sparse_rp']
miss = 0
for d in DS:
  for s in SFS:
    for m in MS:
      f = f'cache/rq1/rq3_{d}_sf{s}_ensemble_{m}.parquet'
      if not os.path.exists(f): miss += 1
print(miss)
")
  alive=$(pgrep -f "run_ensemble_4kang_adaptive.py" | wc -l)
  ts=$(date '+%H:%M:%S')
  echo "[$ts] X6 remaining=$remaining alive_procs=$alive" | tee -a "$WAIT_LOG"
  if [[ "$remaining" == "0" ]]; then
    echo "[$ts] X6 4강 done — proceeding to 11-method" | tee -a "$WAIT_LOG"
    break
  fi
  if [[ "$alive" == "0" && "$remaining" != "0" ]]; then
    echo "[$ts] WARNING: ensemble proc down with $remaining missing — proceeding anyway" | tee -a "$WAIT_LOG"
    break
  fi
  sleep 90
done

echo "=== launching 11-method (X6+) ===" | tee -a "$WAIT_LOG"
bash cache/rq3/launch_ensemble_11method.sh >> "$WAIT_LOG" 2>&1
echo "=== done at $(date '+%Y-%m-%d %H:%M:%S KST') ===" | tee -a "$WAIT_LOG"
