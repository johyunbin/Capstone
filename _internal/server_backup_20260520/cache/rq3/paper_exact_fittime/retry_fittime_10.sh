#!/bin/bash
# 10 file retry — fit_time_sec field 누락 영역
# A1-DEEP CaseA × 5 + A1-DEEP CaseB × 3 + A1-SIFT CaseA × 2 = 10 file
cd /mnt/hdd0/home/capstone2026
LOG=/mnt/hdd0/home/capstone2026/cache/rq3/paper_exact_fittime/retry_launch.log
echo "=== 5/15 16:50 retry launch ===" | tee -a $LOG
date | tee -a $LOG

# A1-DEEP CaseA × 5
for m in sparse_rp chao_weighted neuram pca1d hilbert_real; do
  echo "[$(date '+%H:%M:%S')] A1-DEEP CaseA $m ..." | tee -a $LOG
  python3 cache/rq3/measure_paper_exact.py --rq 3 --phase B --cell A1-DEEP --mode CaseA --method $m --output cache/rq3/paper_exact_fittime 2>&1 | tee -a $LOG
done

# A1-DEEP CaseB × 3 (영역 영역 영역 영역 영역)
for m in sparse_rp chao_weighted neuram; do
  echo "[$(date '+%H:%M:%S')] A1-DEEP CaseB $m ..." | tee -a $LOG
  python3 cache/rq3/measure_paper_exact.py --rq 3 --phase C --cell A1-DEEP --mode CaseB --method $m --output cache/rq3/paper_exact_fittime 2>&1 | tee -a $LOG
done

# A1-SIFT CaseA × 2
for m in sparse_rp chao_weighted; do
  echo "[$(date '+%H:%M:%S')] A1-SIFT CaseA $m ..." | tee -a $LOG
  python3 cache/rq3/measure_paper_exact.py --rq 3 --phase B --cell A1-SIFT --mode CaseA --method $m --output cache/rq3/paper_exact_fittime 2>&1 | tee -a $LOG
done

echo "=== retry 완료 ===" | tee -a $LOG
date | tee -a $LOG
