#!/bin/bash
# measure_4par_midnight.sh — sf=10 우선 4 병렬 measure, 5/22 자정 deadline
# 5/21 20:35 사용자 — 4 병렬 재개로 자정까지 최대한. sf=10 = page cache 캐싱 + 128 core 여유.
# 정합성: 정본 phase2(DEEP sf=10)는 sequential — 측정 조건 차이는 honest limitation.
#         sequential 12 cell 은 phase4_extension_seq_backup/ 에 보존 (다음 세션 contention 비교용).
cd /mnt/hdd0/home/capstone2026/cache/rq3
OUT=latency/phase4_extension
LOG=$OUT/measure_4par_midnight.log
DEADLINE=$(date -d "2026-05-21 15:00:00 UTC" +%s)   # KST 5/22 00:00
echo "=========== sf=10 우선 4 병렬 measure start $(date +%F\ %T) — deadline 자정 ===========" >> "$LOG"

measure_one() {
  local ds=$1 sf=$2 q=$3 sel=$4
  local JSON=$OUT/latency_tpc_h_${q}_${ds}_sf${sf}_sel${sel}_qid0.json
  [ -f "$JSON" ] && return
  echo "[$(date +%H:%M:%S)] $ds sf$sf $q sel$sel start" >> "$LOG"
  systemd-run --user --scope -p MemoryMax=60G -p CPUQuota=400% --slice=user.slice \
    nice -n 10 ionice -c 2 -n 7 \
    timeout 40m python3 measure_latency_realengine.py --query $q --dataset $ds --sf $sf \
    --sel $sel --query-id 0 --estimates "$OUT/estimates_${ds}_sf${sf}.parquet" \
    --output "$OUT" --statement-timeout 180s > /dev/null 2>&1
  echo "[$(date +%H:%M:%S)] $ds sf$sf $q sel$sel done" >> "$LOG"
}

# 4 병렬 batch — deadline 체크는 부모 loop (background subshell exit 가 부모 안 죽이므로)
CNT=0
launch_batch() {
  local sf=$1; shift
  for spec in "$@"; do
    if [ "$(date +%s)" -ge "$DEADLINE" ]; then
      wait; echo "[$(date +%H:%M:%S)] ★ 자정 deadline — measure 종료" >> "$LOG"; exit 0
    fi
    set -- $spec
    measure_one $1 $sf $2 $3 &
    CNT=$((CNT + 1))
    if [ $CNT -ge 4 ]; then wait; CNT=0; fi
  done
  wait; CNT=0
}

# sf=10 단일 4종 (DEEP sf=10 = 정본 carry 제외), sel 0.001→0.01→0.1
SF10_SPECS=()
for sel in 0.001 0.01 0.1; do
  for ds in SIFT YFCC SSN WIKI; do
    for q in q3 q9 q10 q12; do
      SF10_SPECS+=("$ds $q $sel")
    done
  done
done
launch_batch 10 "${SF10_SPECS[@]}"

# 시간 남으면 sf=1 단일 5종
SF1_SPECS=()
for sel in 0.001 0.01 0.1; do
  for ds in DEEP SIFT YFCC SSN WIKI; do
    for q in q3 q9 q10 q12; do
      SF1_SPECS+=("$ds $q $sel")
    done
  done
done
launch_batch 1 "${SF1_SPECS[@]}"

echo "=========== measure 완료 $(date +%F\ %T) ===========" >> "$LOG"
ls $OUT/latency_*.json 2>/dev/null | wc -l | xargs -I {} echo "raw JSON 총: {}" >> "$LOG"
