#!/usr/bin/env bash
# RQ3 Ensemble 11-method 확장 launcher
# X6 (4강) 완료 결과는 SKIP, 추가 7개 method 만 측정
# total: 5 cell × 2 SF × 7 method = 70 runs (4강 결과 SKIP)

set -u

cd /mnt/hdd0/home/capstone2026

DATASETS=(DEEP SIFT SSN YFCC WIKI)
SFS=(1 10)
# 4강 (X6 결과 활용) + 추가 7
ALL_METHODS=(hdbscan minibatch_partial hilbert sparse_rp \
             minibatch gmm faiss_ivf reservoir pca1d lsh sobol)

LOG_DIR=logs
mkdir -p "$LOG_DIR"

n_skip=0
n_run=0
n_fail=0
t_start=$(date +%s)

for ds in "${DATASETS[@]}"; do
  for sf in "${SFS[@]}"; do
    for base in "${ALL_METHODS[@]}"; do
      out=cache/rq1/rq3_${ds}_sf${sf}_ensemble_${base}.parquet
      if [[ -f "$out" ]]; then
        echo "[skip] $out (exists)"
        n_skip=$((n_skip+1))
        continue
      fi
      log=$LOG_DIR/ensemble11_${ds}_sf${sf}_${base}_20260508.log
      echo "[run ] ds=$ds sf=$sf base=$base -> $log"
      python3 cache/rq3/run_ensemble_4kang_adaptive.py \
        --dataset "$ds" --sf "$sf" --base-method "$base" \
        > "$log" 2>&1
      rc=$?
      if [[ $rc -ne 0 ]]; then
        echo "[FAIL] ds=$ds sf=$sf base=$base rc=$rc (see $log)"
        n_fail=$((n_fail+1))
      else
        n_run=$((n_run+1))
      fi
    done
  done
done

t_end=$(date +%s)
echo
echo "=== ensemble 11-method launcher done ==="
echo "  skipped: $n_skip"
echo "  ran    : $n_run"
echo "  failed : $n_fail"
echo "  elapsed: $((t_end - t_start))s"
