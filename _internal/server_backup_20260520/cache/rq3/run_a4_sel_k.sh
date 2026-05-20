#!/bin/bash
# A4-sel K granularity (paper Fig 13 sel sweep cover)
# 1 cell × 4 anchor × 2 mode = 8 measurement per K
set -e
K=$1
if [ -z "$K" ]; then echo "Usage: $0 <K>"; exit 1; fi
echo "[$(date +%H:%M:%S)] === A4-sel K=$K launch ==="
cd /mnt/hdd0/home/capstone2026/cache/rq3
cp _measure_common.py _measure_common.py.bak_a4sel_k 2>/dev/null || true
sed -i "s/^N_STRATA = .*/N_STRATA = $K/" _measure_common.py
echo "[patch] $(grep '^N_STRATA' _measure_common.py)"
OUT_DIR=paper_exact_km${K}_a4_sel
mkdir -p $OUT_DIR
for method in sparse_rp chao_weighted hilbert_real hyperloglog; do
  for mode in CaseA CaseB; do
    echo "[$(date +%H:%M:%S)] K=$K cell=A4-sel method=$method mode=$mode"
    python3 measure_paper_exact.py --rq 3 --phase B --cell A4-sel --mode $mode --method $method --output $OUT_DIR 2>&1 | tail -2
  done
done
mv _measure_common.py.bak_a4sel_k _measure_common.py
echo "[$(date +%H:%M:%S)] === A4-sel K=$K DONE ==="
ls -la $OUT_DIR | wc -l
