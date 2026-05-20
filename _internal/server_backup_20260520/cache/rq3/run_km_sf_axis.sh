#!/bin/bash
# K granularity sweep for A5-scale-sf{1,10,100} (DEEP single axis)
# 4 anchor × 2 mode × 3 cells = 24 measurement per K
# K=10 + K=30 launch separately
set -e
K=$1
if [ -z "$K" ]; then echo "Usage: $0 <K>"; exit 1; fi
echo "[$(date +%H:%M:%S)] === K=$K launch ==="
cd /mnt/hdd0/home/capstone2026/cache/rq3
cp _measure_common.py _measure_common.py.bak_km_sf_axis 2>/dev/null || true
sed -i "s/^N_STRATA = .*/N_STRATA = $K/" _measure_common.py
echo "[patch] $(grep '^N_STRATA' _measure_common.py)"
OUT_DIR=paper_exact_km${K}_sf_axis
mkdir -p $OUT_DIR
for cell in A5-scale-sf1 A5-scale-sf10 A5-scale-sf100; do
  for method in sparse_rp chao_weighted hilbert_real hyperloglog; do
    for mode in CaseA CaseB; do
      echo "[$(date +%H:%M:%S)] K=$K cell=$cell method=$method mode=$mode"
      python3 measure_paper_exact.py --rq 3 --phase B --cell $cell --mode $mode --method $method --output $OUT_DIR 2>&1 | tail -2
    done
  done
done
mv _measure_common.py.bak_km_sf_axis _measure_common.py
echo "[$(date +%H:%M:%S)] === K=$K DONE, _measure_common.py restored ==="
ls -la $OUT_DIR | wc -l
