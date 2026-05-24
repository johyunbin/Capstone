#!/bin/bash
# SIFT/SSN K granularity SF=100 axis (paper Fig 5/6 base)
# 정직 disclosure #1 "DEEP single dataset 한정" cover
# K=$1, cells = A1-SIFT + A1-SSN
# 2 dataset × 4 anchor × 2 mode = 16 measurement per K
set -e
K=$1
if [ -z "$K" ]; then echo "Usage: $0 <K>"; exit 1; fi
echo "[$(date +%H:%M:%S)] === SIFT/SSN K=$K launch ==="
cd /mnt/hdd0/home/capstone2026/cache/rq3
cp _measure_common.py _measure_common.py.bak_sift_ssn_k 2>/dev/null || true
sed -i "s/^N_STRATA = .*/N_STRATA = $K/" _measure_common.py
echo "[patch] $(grep '^N_STRATA' _measure_common.py)"
OUT_DIR=paper_exact_km${K}_sift_ssn
mkdir -p $OUT_DIR
for cell in A1-SIFT A1-SSN; do
  for method in sparse_rp chao_weighted hilbert_real hyperloglog; do
    for mode in CaseA CaseB; do
      echo "[$(date +%H:%M:%S)] K=$K cell=$cell method=$method mode=$mode"
      python3 measure_paper_exact.py --rq 3 --phase B --cell $cell --mode $mode --method $method --output $OUT_DIR 2>&1 | tail -2
    done
  done
done
mv _measure_common.py.bak_sift_ssn_k _measure_common.py
echo "[$(date +%H:%M:%S)] === SIFT/SSN K=$K DONE, _measure_common.py restored ==="
ls -la $OUT_DIR | wc -l
