#!/bin/bash
# v10 → v9 chain — v10 launch 완료 후 자동 v9 launch
# 5/16 00:30 session — handoff v31 chain script
#
# 동작:
#   1. v10 launch (background tmux session)
#   2. v10 COMPLETE.flag polling (60s 간격)
#   3. flag 출현 → v9 launch (background tmux session)
#   4. 종료
#
# 사용 (server 영역):
#   tmux new-session -d -s v10_v9_chain "bash /mnt/hdd0/home/capstone2026/_internal/scripts/v10_v9_chain.sh"
#
# 또는 수동 launch:
#   tmux new-session -d -s v10_full16 "bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_v10_full_16method_5_16.sh"
#   (v10 완료 후) tmux new-session -d -s v9_sel_sweep "bash /mnt/hdd0/home/capstone2026/_internal/scripts/launch_v9_sel_sweep_5_15.sh"

set -uo pipefail

V10_SCRIPT=/mnt/hdd0/home/capstone2026/_internal/scripts/launch_v10_full_16method_5_16.sh
V9_SCRIPT=/mnt/hdd0/home/capstone2026/_internal/scripts/launch_v9_sel_sweep_5_15.sh
LOG=/mnt/hdd0/home/capstone2026/_internal/v10_v9_chain.log

KST() {
    TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M:%S KST'
}

echo "[$(KST)] === v10 → v9 chain START ===" | tee $LOG

# === Step 1: v10 launch ===
echo "[$(KST)] step 1: v10 launch (tmux session=v10_full16)" | tee -a $LOG
tmux new-session -d -s v10_full16 "bash $V10_SCRIPT 2>&1 | tee /tmp/v10_full16_console.log"
sleep 5

# === Step 2: v10 COMPLETE.flag polling ===
echo "[$(KST)] step 2: v10 COMPLETE.flag polling (60s 간격)" | tee -a $LOG
POLL_COUNT=0
while true; do
    POLL_COUNT=$((POLL_COUNT + 1))
    # 최신 v10 result dir 영역 COMPLETE.flag 확인
    LATEST_V10=$(ls -td /mnt/hdd0/home/capstone2026/results_v10_full16_* 2>/dev/null | head -1)
    if [ -n "$LATEST_V10" ] && [ -f "$LATEST_V10/COMPLETE.flag" ]; then
        echo "[$(KST)] v10 COMPLETE.flag detected after $POLL_COUNT polls (~${POLL_COUNT} min)" | tee -a $LOG
        break
    fi
    if [ $((POLL_COUNT % 10)) -eq 0 ]; then
        echo "[$(KST)] v10 still running ($POLL_COUNT min)" | tee -a $LOG
    fi
    sleep 60
done

# === Step 3: v9 launch ===
echo "[$(KST)] step 3: v9 launch (tmux session=v9_sel_sweep)" | tee -a $LOG
tmux new-session -d -s v9_sel_sweep "bash $V9_SCRIPT 2>&1 | tee /tmp/v9_sel_sweep_console.log"
sleep 5

echo "[$(KST)] === v10 → v9 chain DONE — v9 영역 background 영역 진행 중 ===" | tee -a $LOG
echo "[$(KST)] v9 monitoring: tmux attach -t v9_sel_sweep" | tee -a $LOG
