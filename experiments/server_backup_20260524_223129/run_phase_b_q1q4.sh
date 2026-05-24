#!/bin/bash
# Q1 (hilbert_real) + Q4 (Tier 1 6 method) 신규 cell measurement launch
# 5/10 audit (handoff_v3): 41 method 中 critical defect 정정 후 신규 method 측정
# 권고: chain step 1-4 (analyze + sigma + RQ2 + analyze 2차) 끝난 후 launch

cd /mnt/hdd0/home/capstone2026/cache/rq3

# Q1: hilbert_real (진짜 Hilbert curve, Wikipedia xy2d)
# Q4: dbscan, kde_parzen, mhist2, hyperloglog, rsvd, wavelet_hist (P9/P10 신규 paradigm)
NEW_METHODS="hilbert_real dbscan kde_parzen mhist2 hyperloglog rsvd wavelet_hist"

# 10 cell × 7 methods × 2 modes (CaseA/CaseB) = 140 measurements
# A2-Fig8 추가 — Agent C (5/10 22:46) NPY symlink unblocker 빌드 후 가능
# Cell당 1 tmux: 한 cell에서 fetch 한 번 + method/mode loop sequential
CELLS="A1-DEEP A1-SIFT A1-SSN A2-Fig7 A2-Fig8 A2-Fig9 A4-sel A5-scale-sf1 A5-scale-sf10 A5-scale-sf100"

LOG_DIR="/mnt/hdd0/home/capstone2026/log"
TS=$(date +%Y%m%d_%H%M)

for cell in $CELLS; do
  session="q1q4_${cell//-/_}"
  log="${LOG_DIR}/paper_exact_q1q4_${cell}_${TS}.log"

  cmd="cd /mnt/hdd0/home/capstone2026/cache/rq3 && export OMP_NUM_THREADS=128 && {"
  for method in $NEW_METHODS; do
    for mode in CaseA CaseB; do
      cmd="$cmd echo '[\$(date +%H:%M:%S)] === ${cell} × ${method} × ${mode} ===' | tee -a $log;"
      cmd="$cmd python3 -u measure_paper_exact.py --rq 3 --phase B --cell $cell --mode $mode --method $method 2>&1 | tee -a $log;"
    done
  done
  cmd="$cmd echo '[\$(date +%H:%M:%S)] DONE ${cell}' | tee -a $log; }"

  tmux new -d -s "$session" "$cmd"
  echo "[$(date +%H:%M:%S)] launched $session → $log"
  sleep 0.5
done

echo "[$(date +%H:%M:%S)] All 9 cells launched (Q1 hilbert_real + Q4 6 methods × CaseA/CaseB)"
echo "[$(date +%H:%M:%S)] Total: 9 tmux × 14 measurements/cell = 126 measurements"
echo "[$(date +%H:%M:%S)] ETA ~30-60 minutes (per-cell fetch 22min + 14 method-modes × 1-3min)"
