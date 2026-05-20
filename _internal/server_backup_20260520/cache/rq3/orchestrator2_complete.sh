#!/bin/bash
# Worker G/H 통합 dispatcher — Step 4 inline 완료 대기 → RQ2 5mode 5sel + RANDOM20 5sel
# 본 세션에서 모든 8M 빈틈 채우기 위한 후속 orchestrator
set -e
RQ3="/mnt/hdd0/home/capstone2026/cache/rq3"
LOG="/tmp/8m_complete_orchestrator.log"
exec > >(tee -a "$LOG") 2>&1
ts() { date '+%Y-%m-%d %H:%M:%S KST'; }

echo "[$(ts)] === Phase 2 orchestrator START (Worker G post-Step 4) ==="

# Step A: Worker G Step 4 (inline 3 method) 완료 대기
echo "[$(ts)] Step A: 8m_sel_expand done flag 대기"
WAIT_LIMIT=3600
WAIT_ELAPSED=0
while [ ! -f /tmp/8m_sel_expand_done.flag ]; do
    if [ $WAIT_ELAPSED -ge $WAIT_LIMIT ]; then
        echo "[$(ts)] WARN: 1시간 초과, 강제 진행"
        break
    fi
    sleep 30
    WAIT_ELAPSED=$((WAIT_ELAPSED + 30))
done
echo "[$(ts)] Step A 완료: $(cat /tmp/8m_sel_expand_done.flag 2>/dev/null)"

# Step B: RQ2 8M 5 mode × 5 sel
echo "[$(ts)] Step B: RQ2 alloc 8M 5 mode × 5 sel (12,500 cell)"
cd /mnt/hdd0/home/capstone2026/cache
python3 -u rq2_alloc_python_8m_5mode.py 2>&1 | tail -50
echo "[$(ts)] Step B 완료"

# Step C: RANDOM20 8M sel 0.01/0.05/0.50 (sel_expand)
echo "[$(ts)] Step C: RANDOM20 8M sel_expand 측정"
python3 -u /mnt/hdd0/home/capstone2026/cache/rq3/run_random20_8m_sel_expand.py 2>&1 | tail -30
echo "[$(ts)] Step C 완료"

echo "DONE_AT_$(date +%Y-%m-%d_%H:%M:%S)" > /tmp/8m_complete_done.flag
echo "[$(ts)] === Phase 2 orchestrator 전체 완료 ==="
