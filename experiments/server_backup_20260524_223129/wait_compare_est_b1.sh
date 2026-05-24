#!/bin/bash
# estimates 13 file 완료 감지 → est_b1 2-stage vs 1-stage 비교
cd /mnt/hdd0/home/capstone2026/cache/rq3
while [ "$(ls latency/phase4_extension/estimates_*.parquet 2>/dev/null | wc -l)" -lt 13 ]; do
  sleep 120
done
sleep 30
python3 compare_est_b1.py > latency/phase4_extension/est_b1_compare.log 2>&1
