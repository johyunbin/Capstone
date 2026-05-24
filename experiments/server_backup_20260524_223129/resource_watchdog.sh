#!/bin/bash
# 자원 watchdog — free RAM < 100GB or our_rss > 600GB 시 SIGTERM
# 5초 주기, 10분 모니터 (max launch 동시 진행)
WATCH_PROCS='measure_offline_casec_portfolio|measure_paper_exact|measure_latency'
LOG=/tmp/resource_watchdog.log
echo "[$(TZ=Asia/Seoul date +%FT%H:%M:%S)] watchdog start (PID=$$)" > "$LOG"
while true; do
  free_gb=$(free -g | awk 'NR==2 {print $4}')
  avail_gb=$(free -g | awk 'NR==2 {print $7}')
  pids=$(pgrep -d, -f "$WATCH_PROCS" 2>/dev/null)
  if [ -z "$pids" ]; then
    rss_gb=0
  else
    rss_gb=$(ps -o rss= --pid "$pids" 2>/dev/null | awk '{sum+=$1} END {print int(sum/1024/1024)}')
  fi
  ts=$(TZ=Asia/Seoul date +'%T')
  echo "[$ts] free=${free_gb}GB avail=${avail_gb}GB our_rss=${rss_gb}GB pids=$pids" >> "$LOG"
  if [ -n "$pids" ]; then
    if [ "$free_gb" -lt 60 ] || [ "$rss_gb" -gt 600 ]; then
      echo "[$ts] ALERT free=${free_gb}GB rss=${rss_gb}GB → SIGTERM" >> "$LOG"
      pkill -SIGTERM -f 'measure_offline_casec_portfolio'
      pkill -SIGTERM -f 'measure_paper_exact'
      pkill -SIGTERM -f 'measure_latency_realengine'
      break
    fi
  fi
  sleep 5
done
