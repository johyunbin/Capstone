#!/bin/bash
# measure_seq_midnight.sh — sf=10 우선 sequential measure, 5/22 자정 deadline
# 5/21 18:40 사용자 — 실험 21일 자정까지만 (22일 다른 분 서버 사용). 미팅 데이터 확보.
# 우선순위: sf=10 단일 4종 (injection 발동·dataset 일반화 = 미팅 핵심) → sf=1
# sel 0.001(core) → 0.01 → 0.1, dataset dim 작은 순 (SIFT128 YFCC192 SSN256 WIKI768)
cd /mnt/hdd0/home/capstone2026/cache/rq3
OUT=latency/phase4_extension
LOG=$OUT/measure_seq_midnight.log
DEADLINE=$(date -d "2026-05-21 15:00:00 UTC" +%s)   # KST 5/22 00:00 = UTC 5/21 15:00 (server UTC)
echo "=========== sf=10 우선 measure start $(date +%F\ %T) — deadline 자정 ===========" >> "$LOG"

measure_one() {
  local ds=$1 sf=$2 q=$3 sel=$4
  local JSON=$OUT/latency_tpc_h_${q}_${ds}_sf${sf}_sel${sel}_qid0.json
  [ -f "$JSON" ] && return
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    echo "[$(date +%H:%M:%S)] ★ 자정 deadline 도달 — measure 종료" >> "$LOG"
    exit 0
  fi
  echo "[$(date +%H:%M:%S)] $ds sf$sf $q sel$sel start" >> "$LOG"
  systemd-run --user --scope -p MemoryMax=50G -p CPUQuota=400% --slice=user.slice \
    nice -n 10 ionice -c 2 -n 7 \
    timeout 40m python3 measure_latency_realengine.py --query $q --dataset $ds --sf $sf \
    --sel $sel --query-id 0 --estimates "$OUT/estimates_${ds}_sf${sf}.parquet" \
    --output "$OUT" --statement-timeout 180s 2>&1 | tail -2 >> "$LOG"
  echo "[$(date +%H:%M:%S)] $ds sf$sf $q sel$sel done" >> "$LOG"
}

# --- sf=10 단일 4종 (DEEP sf=10 은 정본 phase2 carry — 제외) ---
for sel in 0.001 0.01 0.1; do
  for ds in SIFT YFCC SSN WIKI; do
    for q in q3 q9 q10 q12; do
      measure_one $ds 10 $q $sel
    done
  done
done
# --- 시간 남으면 sf=1 단일 5종 ---
for sel in 0.001 0.01 0.1; do
  for ds in DEEP SIFT YFCC SSN WIKI; do
    for q in q3 q9 q10 q12; do
      measure_one $ds 1 $q $sel
    done
  done
done
echo "=========== measure 완료 $(date +%F\ %T) ===========" >> "$LOG"
ls $OUT/latency_*.json 2>/dev/null | wc -l | xargs -I {} echo "raw JSON 총: {}" >> "$LOG"
