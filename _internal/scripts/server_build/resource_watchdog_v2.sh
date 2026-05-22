#!/bin/bash
# resource_watchdog_v2.sh — 5초 주기 사실상 실시간 자원 양보 daemon (5/21 00:32 사용자 명시 강화)
# 임계치 도달 시 우리(capstone2026) measure/build process 즉시 SIGSTOP, 회복 시 SIGCONT
# log throttle: 평소 1분(12 cycle)에 1회, STOP/CONT 전환 시 즉시 log
LOG=/mnt/hdd0/home/capstone2026/resource_watchdog.log
INTERVAL=5
FREE_THRESHOLD_GB=200        # free RAM 임계 (이전 150 → 200, 더 보수)
OTHER_CPU_THRESHOLD=6400     # 다른 user CPU 임계 (50 core)
LOAD_THRESHOLD=80            # system load 임계 (128 core 中 62.5%)
PATTERN='measure_latency\|make -j\|gen_latency\|build_4engine\|launch_phase4'
echo "[$(date +'%Y-%m-%d %H:%M:%S')] watchdog v2 start (pid=$$, interval=${INTERVAL}s, free<${FREE_THRESHOLD_GB}GB | other_cpu>${OTHER_CPU_THRESHOLD}% | load>${LOAD_THRESHOLD})" >> $LOG
PREV_STATUS="ok"
LOG_CYCLE=0
while true; do
  FREE_GB=$(free -g | awk '/^Mem:/ {print $7}')
  LOAD=$(uptime | awk -F'load average:' '{print $2}' | cut -d, -f1 | xargs)
  LOAD_INT=$(echo "$LOAD" | awk -F. '{print $1}')
  OTHER_CPU=$(ps -eo user,%cpu --no-headers | awk '$1!="capston+" && $1!="root" {s+=$2} END {printf "%.0f", s}')
  STATUS="ok"
  if [ "$FREE_GB" -lt $FREE_THRESHOLD_GB ] || [ "$OTHER_CPU" -gt $OTHER_CPU_THRESHOLD ] || [ "$LOAD_INT" -gt $LOAD_THRESHOLD ]; then
    pkill -STOP -u capstone2026 -f "$PATTERN" 2>/dev/null
    STATUS="STOP"
  else
    pkill -CONT -u capstone2026 -f "$PATTERN" 2>/dev/null
  fi
  LOG_CYCLE=$((LOG_CYCLE + 1))
  if [ "$STATUS" != "$PREV_STATUS" ] || [ $LOG_CYCLE -ge 12 ]; then
    echo "[$(date +%H:%M:%S)] free=${FREE_GB}GB load=${LOAD} other_cpu=${OTHER_CPU}% → $STATUS" >> $LOG
    LOG_CYCLE=0
  fi
  PREV_STATUS=$STATUS
  sleep $INTERVAL
done
