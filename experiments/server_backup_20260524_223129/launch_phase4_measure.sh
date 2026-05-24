#!/bin/bash
# Phase B2~B4: pgvector latency measure — 4 병렬 / sf=100 = 2 병렬 (사용자 5/20 23:38 명시)
# Usage: ./launch_phase4_measure.sh <PHASE>
#   PHASE = sf1_single | sf10_single | sf10_multi | sf100_single | all
set -u
PHASE=${1:-all}
cd /mnt/hdd0/home/capstone2026/cache/rq3
mkdir -p latency/phase4_extension
LOG=latency/phase4_extension/measure_${PHASE}.log
echo "=========== Phase B/C $PHASE measure start $(date +%F\ %T) ===========" | tee -a $LOG

# helper — 단일 measure cell launch (systemd-run wrap, 4 core cap)
run_cell() {
  local ds=$1 sf=$2 q=$3 sel=$4 mem_max=$5 cpu=$6
  local OUT="latency/phase4_extension"
  local EST="$OUT/estimates_${ds}_sf${sf}.parquet"
  local JSON="$OUT/latency_tpc_h_${q}_${ds}_sf${sf}_sel${sel}_qid0.json"
  if [ -f $JSON ]; then echo "[$(date +%H:%M:%S)] SKIP $ds sf$sf $q sel$sel (exists)" | tee -a $LOG; return; fi
  systemd-run --user --scope -p MemoryMax=$mem_max -p CPUQuota=$cpu --slice=user.slice \
    nice -n 10 ionice -c 2 -n 7 timeout 60m \
    python3 measure_latency_realengine.py \
      --query $q --dataset $ds --sf $sf --sel $sel --query-id 0 \
      --estimates $EST --output $OUT --statement-timeout 180s 2>&1 | tail -3
}

# helper — N 병렬 batch launch
run_batch() {
  local N=$1; shift
  local mem=$1; shift
  local cpu=$1; shift
  # 인자 = "ds sf q sel" 묶음들
  local count=0
  for cfg in "$@"; do
    set -- $cfg
    run_cell $1 $2 $3 $4 $mem $cpu &
    count=$((count + 1))
    if [ $count -ge $N ]; then wait; count=0; fi
  done
  wait
}

# sf=1 단일 5종 = 4 병렬 (15 cell/dataset 인데 4 dataset 동시 → 15 batch 한번에)
# 5 dataset × 4 q × 3 sel = 60 cell. 4 병렬로 묶어 launch.
sf1_single() {
  echo "--- sf=1 단일 5종 (60 cell, 4 병렬) ---" | tee -a $LOG
  local cfgs=()
  for ds in DEEP SIFT SSN WIKI YFCC; do
    for q in q3 q9 q10 q12; do
      for sel in 0.001 0.01 0.1; do
        cfgs+=("$ds 1 $q $sel")
      done
    done
  done
  run_batch 1 50G 400% "${cfgs[@]}"
}

# sf=10 단일 신규 4종 = 4 병렬 (DEEP sf=10 carry)
sf10_single() {
  echo "--- sf=10 단일 신규 4종 (48 cell, 4 병렬) ---" | tee -a $LOG
  local cfgs=()
  for ds in SIFT SSN WIKI YFCC; do
    for q in q3 q9 q10 q12; do
      for sel in 0.001 0.01 0.1; do
        cfgs+=("$ds 10 $q $sel")
      done
    done
  done
  run_batch 1 50G 400% "${cfgs[@]}"
}

# sf=10 다중 2종 = 2 병렬
sf10_multi() {
  echo "--- sf=10 다중 2종 (24 cell, 2 병렬) ---" | tee -a $LOG
  local cfgs=()
  for ds in DEEP_SIFT DEEP_WIKI; do
    for q in q3 q9 q10 q12; do
      for sel in 0.001 0.01 0.1; do
        cfgs+=("$ds 10 $q $sel")
      done
    done
  done
  run_batch 1 60G 600% "${cfgs[@]}"
}

# sf=100 단일 3종 = 2 병렬 (peak 회피)
sf100_single() {
  echo "--- sf=100 단일 3종 (36 cell, 2 병렬) ---" | tee -a $LOG
  local cfgs=()
  for ds in DEEP SIFT SSN; do
    for q in q3 q9 q10 q12; do
      for sel in 0.001 0.01 0.1; do
        cfgs+=("$ds 100 $q $sel")
      done
    done
  done
  run_batch 1 80G 800% "${cfgs[@]}"
}

case $PHASE in
  sf1_single)  sf1_single ;;
  sf10_single) sf10_single ;;
  sf10_multi)  sf10_multi ;;
  sf100_single) sf100_single ;;
  all)
    sf1_single
    sf10_single
    sf10_multi
    sf100_single
    ;;
  *) echo "Unknown PHASE: $PHASE"; exit 1 ;;
esac

echo "=========== Phase B/C $PHASE measure end $(date +%F\ %T) ===========" | tee -a $LOG
ls latency/phase4_extension/latency_*.json 2>/dev/null | wc -l | xargs -I {} echo "총 cell file: {}" | tee -a $LOG
