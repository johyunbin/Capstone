#!/bin/bash
# SIFT 8M chain 완료 후 누락 P-method (P1 KM50 8M + P2 OPQ 1M+8M) dispatch
# Sequential — server 동시점유 회피

LOG=/tmp/missing_p_chain.out

# Wait for SIFT 8M chain done (final_chain 의 PHASE B end)
while [ ! -f /tmp/sift_8m_chain_done.flag ]; do
  sleep 60
done
echo "[$(date +%H:%M:%S)] SIFT 8M chain done — start missing P-methods" | tee -a $LOG

cd /mnt/hdd0/home/capstone2026/cache/rq3

# Wait for P1 KM50 1M (still in progress, PID 2485614) to finish
echo "[$(date +%H:%M:%S)] wait P1 KM50 1M (PID 2485614)" | tee -a $LOG
while pgrep -f 'run_km_k_sweep --K 50' > /dev/null; do
  sleep 30
done
echo "[$(date +%H:%M:%S)] P1 KM50 1M done" | tee -a $LOG

# P1 KM50 8M
echo "[$(date +%H:%M:%S)] P1 KM50 8M start" | tee -a $LOG
python3 run_8m_p_methods.py km50 2>&1 | tee /tmp/missing_p1_km50_8m.log
echo "[$(date +%H:%M:%S)] P1 KM50 8M end" | tee -a $LOG

# P2 OPQ 1M
echo "[$(date +%H:%M:%S)] P2 OPQ 1M start" | tee -a $LOG
python3 run_opq.py 2>&1 | tee /tmp/missing_p2_1m.log
echo "[$(date +%H:%M:%S)] P2 OPQ 1M end" | tee -a $LOG

# P2 OPQ 8M
echo "[$(date +%H:%M:%S)] P2 OPQ 8M start" | tee -a $LOG
python3 run_8m_p_methods.py opq 2>&1 | tee /tmp/missing_p2_8m.log
echo "[$(date +%H:%M:%S)] P2 OPQ 8M end" | tee -a $LOG

touch /tmp/missing_p_chain_done.flag
echo "[$(date +%H:%M:%S)] === MISSING P-CHAIN COMPLETE ===" | tee -a $LOG
