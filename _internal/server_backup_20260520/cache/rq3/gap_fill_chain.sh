#!/bin/bash
# Gap #1 + Gap #3 sequential 측정 (server 동시점유 회피)
set -e
cd /mnt/hdd0/home/capstone2026/cache/rq3

echo "=== [$(date +%H:%M:%S)] Gap #1 START — RQ1 SIFT KM20 5-sel canonical ==="
python3 run_km20_sift_5sel.py 2>&1 | tee /tmp/gap1_sift_km20_5sel.log
SIFT_RC=${PIPESTATUS[0]}
echo "=== [$(date +%H:%M:%S)] Gap #1 END (rc=$SIFT_RC) ==="

if [ "$SIFT_RC" != "0" ]; then
  echo "Gap #1 FAILED, abort chain"
  exit 1
fi

echo "=== [$(date +%H:%M:%S)] Gap #3 START — RQ3 8M KM20 sel_expand ==="
python3 run_km20_8m_sel_expand.py 2>&1 | tee /tmp/gap3_8m_km20_sel_expand.log
KM20_RC=${PIPESTATUS[0]}
echo "=== [$(date +%H:%M:%S)] Gap #3 END (rc=$KM20_RC) ==="

# 산출 위치 확인
echo "=== 산출 inventory ==="
ls -la /mnt/hdd0/home/capstone2026/cache/rq3/rq1_sift_km20_5sel.parquet \
       /mnt/hdd0/home/capstone2026/cache/rq3/rq3_8m_km20_sel_expand.parquet 2>&1

# 완료 flag
touch /tmp/gap_fill_done.flag
echo "=== [$(date +%H:%M:%S)] CHAIN COMPLETE — flag 생성 ==="
