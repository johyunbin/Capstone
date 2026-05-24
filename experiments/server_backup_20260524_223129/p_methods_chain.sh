#!/bin/bash
# P1+P2+P3+P4+P5 sequential chain (server 동시점유 회피)
set -e
cd /mnt/hdd0/home/capstone2026/cache/rq3

LOG=/tmp/p_methods_chain.out
echo "[$(date +%H:%M:%S)] === P-METHODS CHAIN START ===" | tee -a $LOG

# === P3 RQ2 size 5-mode 8M (가장 짧음, ~5분) ===
echo "[$(date +%H:%M:%S)] P3 START — RQ2 size 5-mode 8M" | tee -a $LOG
cd /mnt/hdd0/home/capstone2026/cache
python3 rq2_size_sensitivity_5mode_8m.py 2>&1 | tee /tmp/p3.log
echo "[$(date +%H:%M:%S)] P3 END (rc=${PIPESTATUS[0]})" | tee -a $LOG
cd /mnt/hdd0/home/capstone2026/cache/rq3

# === P4 Reservoir 1M + 8M ===
echo "[$(date +%H:%M:%S)] P4 START — Reservoir 1M" | tee -a $LOG
python3 run_reservoir.py 2>&1 | tee /tmp/p4_1m.log
echo "[$(date +%H:%M:%S)] P4 START — Reservoir 8M" | tee -a $LOG
python3 run_8m_p_methods.py reservoir 2>&1 | tee /tmp/p4_8m.log
echo "[$(date +%H:%M:%S)] P4 END" | tee -a $LOG

# === P1 KM K sweep K=10, K=50 — 1M + 8M ===
echo "[$(date +%H:%M:%S)] P1 START — KM K=10 1M" | tee -a $LOG
python3 run_km_k_sweep.py --K 10 2>&1 | tee /tmp/p1_km10_1m.log
echo "[$(date +%H:%M:%S)] P1 START — KM K=10 8M" | tee -a $LOG
python3 run_8m_p_methods.py km10 2>&1 | tee /tmp/p1_km10_8m.log
echo "[$(date +%H:%M:%S)] P1 START — KM K=50 1M" | tee -a $LOG
python3 run_km_k_sweep.py --K 50 2>&1 | tee /tmp/p1_km50_1m.log
echo "[$(date +%H:%M:%S)] P1 START — KM K=50 8M" | tee -a $LOG
python3 run_8m_p_methods.py km50 2>&1 | tee /tmp/p1_km50_8m.log
echo "[$(date +%H:%M:%S)] P1 END" | tee -a $LOG

# === P2 OPQ 1M + 8M ===
echo "[$(date +%H:%M:%S)] P2 START — OPQ 1M" | tee -a $LOG
python3 run_opq.py 2>&1 | tee /tmp/p2_1m.log
echo "[$(date +%H:%M:%S)] P2 START — OPQ 8M" | tee -a $LOG
python3 run_8m_p_methods.py opq 2>&1 | tee /tmp/p2_8m.log
echo "[$(date +%H:%M:%S)] P2 END" | tee -a $LOG

# === P5 Hilbert 3D + 4D — 1M + 8M (Hilbert distance 계산 시간 큼, 1M만 우선) ===
echo "[$(date +%H:%M:%S)] P5 START — Hilbert 3D 1M" | tee -a $LOG
python3 run_hilbert_dim.py --dim 3 2>&1 | tee /tmp/p5_3d_1m.log
echo "[$(date +%H:%M:%S)] P5 START — Hilbert 4D 1M" | tee -a $LOG
python3 run_hilbert_dim.py --dim 4 2>&1 | tee /tmp/p5_4d_1m.log
echo "[$(date +%H:%M:%S)] P5 END (1M only — 8M 8M Hilbert 3D/4D distance 계산 비용 매우 큼, deferred)" | tee -a $LOG

# 산출 inventory
echo "=== 산출 inventory ===" | tee -a $LOG
ls -la /mnt/hdd0/home/capstone2026/cache/rq1/rq3_reservoir.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_reservoir.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_km_k_10.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_km_k_50.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_km_k_10.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_km_k_50.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_opq.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_8m_opq.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_hilbert_dim_3d.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq3_hilbert_dim_4d.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq1/rq2_size_sensitivity_8m_5mode.parquet 2>&1 | tee -a $LOG

# 완료 flag
touch /tmp/p_methods_chain_done.flag
echo "[$(date +%H:%M:%S)] === P-METHODS CHAIN COMPLETE ===" | tee -a $LOG
