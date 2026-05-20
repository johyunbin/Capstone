#!/bin/bash
echo "[$(date +%H:%M:%S)] Waiting for 8M redo to complete..."
while [ ! -f /mnt/hdd0/home/capstone2026/cache/rq1/phase7_8m_redo_summary.json ]; do
    sleep 30
done
echo "[$(date +%H:%M:%S)] 8M redo done. Starting remaining experiments..."
cd /mnt/hdd0/home/capstone2026
python3 -u cache/rq1_rq2_remaining_all.py > cache/rq1/rq2_remaining_all.log 2>&1
echo "[$(date +%H:%M:%S)] ALL DONE"
