#!/bin/bash
# Wave1 — halton + hammersley + reservoir × DEEP_sf1, SIFT_sf1, SSN_sf1
# 5/8 09:55 launched
set -e
cd /mnt/hdd0/home/capstone2026/cache/rq3
mkdir -p logs
LOG=/mnt/hdd0/home/capstone2026/cache/rq3/logs/wave1_$(date +%Y%m%d_%H%M%S).log
exec > >(tee "$LOG") 2>&1

echo "[$(date +%H:%M:%S)] === Wave1 Chain start ==="
for ds_sf in 'DEEP 1' 'SIFT 1' 'SSN 1'; do
  set -- $ds_sf
  DS=$1; SF=$2
  for METHOD in halton hammersley reservoir; do
    STAGE=rq3_$METHOD
    echo ""
    echo "[$(date +%H:%M:%S)] >>> $DS sf$SF $METHOD"
    python3 chain_unified.py --dataset $DS --sf $SF --stage $STAGE --port 55435 || \
      echo "[$(date +%H:%M:%S)] ERROR $DS sf$SF $METHOD — continuing"
  done
done
echo "[$(date +%H:%M:%S)] === Wave1 Chain done ==="
