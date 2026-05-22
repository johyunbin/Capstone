#!/bin/bash
# resource_watchdog.sh v5 — 5초 주기 실시간 자원 양보 daemon
# v5 (5/21 20:35): our_rss 512 cap 제거 — 사용자 "256기가만 남기고 512 말고". server free 256GB 기준만.
# 임계 도달 시 measure/build process 즉시 SIGSTOP, 회복 시 SIGCONT
LOG=/mnt/hdd0/home/capstone2026/resource_watchdog.log
INTERVAL=5
FREE_THRESHOLD_GB=256        # ★ 서버 free RAM 항상 256GB 이상 유지 (이 기준만 — our_rss cap 없음)
OTHER_CPU_THRESHOLD=6400
LOAD_THRESHOLD=80
PATTERN='measure_latency\|make -j\|gen_latency\|build_4engine\|launch_phase4'
echo "[$(date +'%Y-%m-%d %H:%M:%S')] watchdog v5 start (pid=$$, interval=${INTERVAL}s, free>=${FREE_THRESHOLD_GB}GB only)" >> "$LOG"
while true; do
  FREE_GB=$(free -g | awk '/^Mem:/{print $7}')
  OTHER_CPU=$(ps -eo user:20,%cpu --no-headers 2>/dev/null | awk '$1!~/^capston/ && $1!="root"{s+=$2} END{printf "%d", s+0}')
  LOAD=$(awk '{printf "%d", $1}' /proc/loadavg)
  OUR_RSS_GB=$(ps -u capstone2026 -o rss= --no-headers 2>/dev/null | awk '{s+=$1} END{printf "%d", s/1048576}')
  if [ "${FREE_GB:-999}" -lt $FREE_THRESHOLD_GB ] || [ "${OTHER_CPU:-0}" -gt $OTHER_CPU_THRESHOLD ] || [ "${LOAD:-0}" -gt $LOAD_THRESHOLD ]; then
    pkill -STOP -u capstone2026 -f "$PATTERN" 2>/dev/null
    ACT="STOP"
  else
    pkill -CONT -u capstone2026 -f "$PATTERN" 2>/dev/null
    ACT="ok"
  fi
  echo "[$(date +%H:%M:%S)] free=${FREE_GB}GB our_rss=${OUR_RSS_GB}GB load=${LOAD} other_cpu=${OTHER_CPU}% -> $ACT" >> "$LOG"
  sleep $INTERVAL
done
