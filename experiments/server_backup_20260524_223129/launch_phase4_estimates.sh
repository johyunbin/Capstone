#!/bin/bash
# Phase B1: estimates parquet 15 file 생성 (5/20 23:30 ~)
# 단일 5종 (DEEP/SIFT/SSN sf=1/10/100, WIKI/YFCC sf=1/10) + 다중 2종 sf=10 (DEEP_SIFT/DEEP_WIKI)
set -u
cd /mnt/hdd0/home/capstone2026/cache/rq3
LOG=latency/phase4_extension/estimates_gen.log
echo "=========== Phase B1 estimates generation start $(date +%F\ %T) ===========" | tee -a $LOG
COUNT=0
TOTAL=15
for spec in "DEEP 1" "DEEP 10" "DEEP 100" \
            "SIFT 1" "SIFT 10" "SIFT 100" \
            "SSN 1" "SSN 10" "SSN 100" \
            "WIKI 1" "WIKI 10" \
            "YFCC 1" "YFCC 10" \
            "DEEP_SIFT 10" "DEEP_WIKI 10"; do
  ds=$(echo $spec | awk "{print \$1}")
  sf=$(echo $spec | awk "{print \$2}")
  COUNT=$((COUNT + 1))
  echo "" | tee -a $LOG
  echo "[$(date +%H:%M:%S)] ($COUNT/$TOTAL) $ds sf=$sf start" | tee -a $LOG
  if [ -f latency/phase4_extension/estimates_${ds}_sf${sf}.parquet ]; then
    echo "  → already exists, skip" | tee -a $LOG
    continue
  fi
  nice -n 10 ionice -c 2 -n 7 timeout 30m python3 gen_latency_estimates.py \
    --dataset $ds --sf $sf --n-qvec 1 \
    --output latency/phase4_extension/ 2>&1 | tee -a $LOG
  echo "[$(date +%H:%M:%S)] ($COUNT/$TOTAL) $ds sf=$sf done" | tee -a $LOG
done
echo "" | tee -a $LOG
echo "=========== Phase B1 estimates generation end $(date +%F\ %T) ===========" | tee -a $LOG
ls -la latency/phase4_extension/estimates_*.parquet | tee -a $LOG
