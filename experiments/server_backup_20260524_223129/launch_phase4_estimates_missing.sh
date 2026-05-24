#!/bin/bash
# Phase B1 누락 6 file 재생성 (timeout 60m, 5/21 01:48 auto detect)
# 누락: DEEP/SIFT/SSN sf=100, WIKI sf=10, DEEP_SIFT sf=10, DEEP_WIKI sf=10
set -u
cd /mnt/hdd0/home/capstone2026/cache/rq3
LOG=latency/phase4_extension/estimates_gen_missing.log
echo "=========== Missing estimates regen start $(date +%F\ %T) ===========" | tee -a $LOG
# 우선순위: 가벼운 것 먼저 (WIKI/multi sf=10) → sf=100 무거운 것 마지막
for spec in "WIKI 10" "DEEP_SIFT 10" "DEEP_WIKI 10" "DEEP 100" "SIFT 100" "SSN 100"; do
  ds=$(echo $spec | awk "{print \$1}")
  sf=$(echo $spec | awk "{print \$2}")
  echo "" | tee -a $LOG
  if [ -f latency/phase4_extension/estimates_${ds}_sf${sf}.parquet ]; then
    echo "[$(date +%H:%M:%S)] $ds sf=$sf already exists, skip" | tee -a $LOG
    continue
  fi
  echo "[$(date +%H:%M:%S)] $ds sf=$sf start (timeout 60m)" | tee -a $LOG
  nice -n 10 ionice -c 2 -n 7 timeout 60m python3 gen_latency_estimates.py \
    --dataset $ds --sf $sf --n-qvec 1 \
    --output latency/phase4_extension/ 2>&1 | tail -5 | tee -a $LOG
  echo "[$(date +%H:%M:%S)] $ds sf=$sf done" | tee -a $LOG
done
echo "" | tee -a $LOG
echo "=========== Missing estimates regen end $(date +%F\ %T) ===========" | tee -a $LOG
ls -la latency/phase4_extension/estimates_*.parquet | tee -a $LOG
