#!/bin/bash
# Final orchestrator (B option):
# 1. Wait P-chain completion (P4/P1/P2/P5 — P5 not skipped at chain level, but accelerated by killing)
# 2. SIFT 8M build + measure
# 3. P3 RQ2 size 5-mode 8M

LOG=/tmp/final_chain.out
echo "[$(date +%H:%M:%S)] === FINAL CHAIN START ===" | tee -a $LOG

# === PHASE A: Wait P-chain done flag (or P5 process kill) ===
echo "[$(date +%H:%M:%S)] PHASE A: monitor P-chain for P5 start (then skip P5)" | tee -a $LOG
SKIP=0
while [ ! -f /tmp/p_methods_chain_done.flag ]; do
  # P5 시작 검출
  if [ "$SKIP" = "0" ] && pgrep -f run_hilbert_dim > /dev/null; then
    echo "[$(date +%H:%M:%S)]   ★ P5 process detected → kill (B option skip)" | tee -a $LOG
    pkill -f run_hilbert_dim
    pkill -f p_methods_chain.sh
    touch /tmp/p_methods_chain_done.flag
    SKIP=1
    break
  fi
  sleep 30
done
echo "[$(date +%H:%M:%S)] PHASE A END (P-chain done — SKIP=$SKIP)" | tee -a $LOG

# === PHASE B: SIFT 8M chain ===
echo "[$(date +%H:%M:%S)] PHASE B: SIFT 8M chain START" | tee -a $LOG
cd /mnt/hdd0/home/capstone2026/cache
./sift_8m_chain.sh 2>&1 | tee -a $LOG
echo "[$(date +%H:%M:%S)] PHASE B END" | tee -a $LOG

# === PHASE C: P3 RQ2 size 5-mode 8M ===
echo "[$(date +%H:%M:%S)] PHASE C: P3 RQ2 size 5-mode 8M START" | tee -a $LOG
python3 rq2_size_5mode_full.py 2>&1 | tee /tmp/p3_5mode.log
echo "[$(date +%H:%M:%S)] PHASE C END" | tee -a $LOG

# 최종 inventory
echo "=== FINAL INVENTORY ===" | tee -a $LOG
ls -la /mnt/hdd0/home/capstone2026/cache/rq1/rq*sift_8m*.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq2_size_sensitivity_8m_5mode.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_reservoir.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_reservoir.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_km_k_*.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_km_k_*.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_opq.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_opq.parquet 2>&1 | tee -a $LOG

touch /tmp/final_chain_done.flag
echo "[$(date +%H:%M:%S)] === FINAL CHAIN COMPLETE ===" | tee -a $LOG
