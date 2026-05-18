#!/bin/bash
# task A — B1 2단계 subsampling vs 1단계 direct 동등성 검증.
# verify_b1.py 를 6 cell x N_SEED=100 x 1000 query 로 실행.
# 5/17 세션 (전권 위임). 결과: /tmp/b1verify/result_{CELL}_{OLD_2단계,NEW_1단계}.json + log.
#
# cell 선택: DEEP sf1/10/100 (scale 축) + SIFT/SSN sf100 + WIKI sf10 (dataset/dim 축).
# 2단계 cache 의 reweighting bias 는 dataset 무관 mechanism 이므로 6 cell 이 대표성 충분.
# 가벼운 cell 먼저 -> 무거운 sf100 마지막.
set -u
mkdir -p /tmp/b1verify
cd /mnt/hdd0/home/capstone2026/cache/rq3

echo "[$(date)] === b1verify START — 6 cell x N_SEED=100 x 1000 query ==="
for CELL in A5-scale-sf1 A5-scale-sf10 A6-WIKI-sf10 A1-DEEP A1-SIFT A1-SSN; do
  echo "[$(date)] === verify_b1 $CELL N_SEED=100 ==="
  python3 verify_b1.py "$CELL" 100 1000 2>&1 | tee "/tmp/b1verify/log_${CELL}_5_17.txt" \
    || echo "[WARN] $CELL verify_b1 failed"
done

touch /tmp/b1verify/ALLDONE_5_17
echo "[$(date)] === b1verify ALL DONE ==="
