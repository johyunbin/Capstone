#!/bin/bash
# SF=100 watchdog: 5분마다 메모리 체크, 안전 시 launcher trigger
LAUNCHER='/mnt/hdd0/home/capstone2026/cache/rq3/launch_sf100_safe.sh'
LOG_DIR='/mnt/hdd0/home/capstone2026/log'
ATTEMPTS=0
MAX_ATTEMPTS=120  # 10시간 = 120 × 5min

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
  ATTEMPTS=$((ATTEMPTS + 1))
  TS=$(date +%H:%M:%S)
  echo "[$TS] watchdog attempt $ATTEMPTS/$MAX_ATTEMPTS"
  
  # bash launch script — exit 0 = 성공, exit 2 = 메모리 미충족
  bash $LAUNCHER > $LOG_DIR/sf100_attempt_$ATTEMPTS.log 2>&1
  EXIT_CODE=$?
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo "[$TS] LAUNCHED SF=100 successfully (attempt $ATTEMPTS)"
    exit 0
  fi
  
  echo "[$TS] gate failed, sleep 5 min..."
  sleep 300
done
echo "watchdog timeout after $MAX_ATTEMPTS attempts"
exit 1
