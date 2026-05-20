#!/bin/bash
# multi-cell K granularity (narrative v2 §11 cover 영역 확장)
# A1-DEEP + A2-Fig7 (YFCC multi-table) + A2-Fig9 (DEEP+WIKI cross)
# 3 cells × 4 anchor × 2 mode = 24 measurement per K
set -e
K=$1
if [ -z "$K" ]; then echo "Usage: $0 <K>"; exit 1; fi
echo "[$(date +%H:%M:%S)] === multi-cell K=$K launch ==="
cd /mnt/hdd0/home/capstone2026/cache/rq3
cp _measure_common.py _measure_common.py.bak_multi_cell_k 2>/dev/null || true
sed -i "s/^N_STRATA = .*/N_STRATA = $K/" _measure_common.py
echo "[patch] $(grep '^N_STRATA' _measure_common.py)"
OUT_DIR=paper_exact_km${K}_multi_cell
mkdir -p $OUT_DIR
for cell in A1-DEEP A2-Fig7 A2-Fig9; do
  for method in sparse_rp chao_weighted hilbert_real hyperloglog; do
    for mode in CaseA CaseB; do
      echo "[$(date +%H:%M:%S)] K=$K cell=$cell method=$method mode=$mode"
      python3 measure_paper_exact.py --rq 3 --phase B --cell $cell --mode $mode --method $method --output $OUT_DIR 2>&1 | tail -2
    done
  done
done
mv _measure_common.py.bak_multi_cell_k _measure_common.py
echo "[$(date +%H:%M:%S)] === multi-cell K=$K DONE ==="
ls -la $OUT_DIR | wc -l
