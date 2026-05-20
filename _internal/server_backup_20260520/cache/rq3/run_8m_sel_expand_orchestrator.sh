#!/bin/bash
# Worker G — DEEP 8M sel 5단계 확장 orchestrator
# 1) D_target 0.01/0.05 측정 (rebuild OFF, measure, restore)
# 2) convert 5sel 통합
# 3) sensitivity 16 method × 3 sel (sel_expand)
# 4) inline 3 method × 3 sel (kde, distance_shell, IS)
# 5) done flag

set -e
RQ3="/mnt/hdd0/home/capstone2026/cache/rq3"
LOG="/tmp/8m_sel_expand_orchestrator.log"
exec > >(tee -a "$LOG") 2>&1

ts() { date '+%Y-%m-%d %H:%M:%S KST'; }

echo "[$(ts)] === Worker G orchestrator START ==="

# Step 0: Worker F (baseline) 또는 다른 pgvector 사용 프로세스 종료 대기
# pg_ctl restart 가 진행 중인 측정을 죽이지 않도록.
echo "[$(ts)] Step 0/5: pgvector 자유 대기 (run_*_8m.py 점유 모니터)"
WAIT_LIMIT=1800  # 30분 한계
WAIT_ELAPSED=0
while pgrep -af 'python.*run_(km20|random20|bern|.*_baseline)_8m\.py' > /dev/null 2>&1; do
    if [ $WAIT_ELAPSED -ge $WAIT_LIMIT ]; then
        echo "[$(ts)] WARN: 30분 초과 — 계속 진행 (충돌 위험 감수)"
        break
    fi
    sleep 30
    WAIT_ELAPSED=$((WAIT_ELAPSED + 30))
    echo "[$(ts)]   대기 중 (${WAIT_ELAPSED}s) — active: $(pgrep -af 'python.*run_.*_8m\.py' | head -3)"
done
echo "[$(ts)] Step 0 완료 — pgvector 자유"

# Step 1: D_target gen for sel 0.01/0.05 (lowsel script — rebuild OFF/ON 자체 처리)
echo "[$(ts)] Step 1/5: D_target 0.01/0.05 측정"
bash /mnt/hdd0/home/capstone2026/cache/phase7_8m_lowsel_dtarget.sh
echo "[$(ts)] Step 1 완료"

# Step 2: convert 5 sel 통합
echo "[$(ts)] Step 2/5: query_selectivity_8m.parquet 5 sel 통합"
cd "$RQ3"
python3 convert_8m_dtarget_to_parquet_5sel.py
echo "[$(ts)] Step 2 완료"

# Step 3: sensitivity 16 method × 3 sel
echo "[$(ts)] Step 3/5: 16 method × 3 sel sensitivity 측정"
python3 -u run_8m_sensitivity_sel_expand.py
echo "[$(ts)] Step 3 완료"

# Step 4: inline 3 method × 3 sel
echo "[$(ts)] Step 4/5: 3 inline method × 3 sel"
for module in kde_pilot distance_shell importance_sampling; do
    echo "[$(ts)]   running $module"
    python3 -u "run_${module}_8m_sel_expand.py"
done
echo "[$(ts)] Step 4 완료"

# Done flag
echo "DONE_AT_$(date +%Y-%m-%d_%H:%M:%S)" > /tmp/8m_sel_expand_done.flag
echo "[$(ts)] === Worker G orchestrator 전체 완료 ==="
