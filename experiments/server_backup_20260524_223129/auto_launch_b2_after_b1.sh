#!/bin/bash
# B1 완료 자동 감지 → Phase B/C 측정 sequential launch (5/20 23:54 사용자 전권 위임)
# B1 process pid 3638461 (launch_phase4_estimates.sh) 가 살아있는 동안 대기
LOG=/mnt/hdd0/home/capstone2026/cache/rq3/auto_launch.log
echo "[$(date +%F\ %T)] auto_launch wait for B1 (pid 3638461)" > $LOG
while ps -p 3638461 > /dev/null 2>&1; do sleep 60; done
echo "[$(date +%F\ %T)] B1 done — verify 15 estimates parquet" >> $LOG
ls /mnt/hdd0/home/capstone2026/cache/rq3/latency/phase4_extension/estimates_*.parquet 2>/dev/null | wc -l >> $LOG
echo "[$(date +%F\ %T)] launch B/C measure sequential" >> $LOG
cd /mnt/hdd0/home/capstone2026/cache/rq3
bash launch_phase4_measure.sh all >> $LOG 2>&1
echo "[$(date +%F\ %T)] B/C measure done" >> $LOG
