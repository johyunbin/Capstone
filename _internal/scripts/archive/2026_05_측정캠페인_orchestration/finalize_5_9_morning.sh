#!/bin/bash
# 5/9 morning finalize automation
# 5/8 23:40 작성 — 5/9 morning 측정 결과 도착 시 자동 실행
# 사용: bash _internal/scripts/finalize_5_9_morning.sh
#
# 진행 중 5 측정 (5/8 23:40 시점):
#   1. Multi SF10 Adaptive Cell 3/3 (이미 완료)
#   2. Multi SF1 11-method (~5/9 새벽 진행)
#   3. X6 ensemble: Adaptive×4강 (~24:50)
#   4. X7 ensemble: Adaptive×11 (~01:00)
#   5. Multi SF10 11-method (~5/9 03~05)
#
# 회수 + 분석 + 자문 메일 v4 finalize + PDF 변환 자동화

set -e  # 에러 시 즉시 종료
set -u  # undefined var 사용 시 에러

CAPSTONE_ROOT="/Users/hyunbin/Capstone"
SERVER="capstone"
SERVER_ROOT="/mnt/hdd0/home/capstone2026"

echo "==================================================="
echo "5/9 morning finalize automation"
echo "시작: $(date '+%Y-%m-%d %H:%M:%S KST')"
echo "==================================================="

# ===========================================================================
# Step 1: flag 확인 (서버 측정 finalize 검증)
# ===========================================================================
echo ""
echo "[Step 1] 측정 flag 확인 (5/9 morning trigger)"
echo "---------------------------------------------------"

EXPECTED_FLAGS=(
    "/tmp/multi_paradigm_sf10_done.flag"
    "/tmp/multi_paradigm_sf1_done.flag"
    "/tmp/ensemble_4kang_adaptive_done.flag"
    "/tmp/ensemble_11method_adaptive_done.flag"
    "/tmp/multi_adaptive_done.flag"
    "/tmp/yfcc_ksweep_done.flag"
)

for flag in "${EXPECTED_FLAGS[@]}"; do
    if ssh "$SERVER" "test -f $flag" 2>/dev/null; then
        echo "  [OK]   $flag"
    else
        echo "  [WARN] $flag 부재 — 측정 미완료 또는 flag 미작성"
    fi
done

# ===========================================================================
# Step 2: 결과 회수 (rsync, 6 source)
# ===========================================================================
echo ""
echo "[Step 2] 결과 회수 (rsync 6 source)"
echo "---------------------------------------------------"

# 2-1. Multi paradigm 11-method (SF10 + SF1)
mkdir -p "$CAPSTONE_ROOT/_internal/cache/rq3/multi_paradigm"
echo "  [2-1] multi_paradigm CSV (3 cell × 11 method × 2 SF = 66 csv 기대)"
rsync -avz \
    "$SERVER:$SERVER_ROOT/cache/rq3/multi_paradigm/" \
    "$CAPSTONE_ROOT/_internal/cache/rq3/multi_paradigm/" \
    2>&1 | tail -3

# 2-2. Multi Adaptive (SF10 + SF1)
mkdir -p "$CAPSTONE_ROOT/_internal/cache/rq3/multi_adaptive"
echo "  [2-2] multi_adaptive parquet/csv (3 cell × 2 SF = 6 ish)"
rsync -avz \
    "$SERVER:$SERVER_ROOT/_internal/cache/rq3/multi_adaptive/" \
    "$CAPSTONE_ROOT/_internal/cache/rq3/multi_adaptive/" \
    2>&1 | tail -3

# 2-3. Ensemble 결과 (Adaptive×4강 + Adaptive×11)
mkdir -p "$CAPSTONE_ROOT/experiments/results/cache/rq1"
echo "  [2-3] ensemble parquet (40 + 70 = 110 runs)"
rsync -avz \
    "$SERVER:$SERVER_ROOT/cache/rq1/rq3_*ensemble*.parquet" \
    "$CAPSTONE_ROOT/experiments/results/cache/rq1/" \
    2>&1 | tail -3 || echo "  [WARN] ensemble parquet 회수 실패 (측정 미완 가능)"

# 2-4. YFCC K-sweep (옵션)
echo "  [2-4] YFCC K-sweep (4 K)"
rsync -avz \
    "$SERVER:$SERVER_ROOT/cache/rq1/rq1_YFCC_sf10_k*.parquet" \
    "$CAPSTONE_ROOT/experiments/results/cache/rq1/" \
    2>&1 | tail -3 || echo "  [WARN] YFCC K-sweep 회수 실패"

# 2-5. faiss_ivf (옵션, SF1+SF10 10 cell)
echo "  [2-5] faiss_ivf (옵션)"
rsync -avz \
    "$SERVER:$SERVER_ROOT/cache/rq1/rq3_*faiss_ivf*.parquet" \
    "$CAPSTONE_ROOT/experiments/results/cache/rq1/" \
    2>&1 | tail -3 || echo "  [WARN] faiss_ivf 회수 실패 (측정 미진행 가능)"

# 회수 카운트 점검
echo ""
echo "  회수 카운트:"
echo "  - multi_paradigm:  $(ls "$CAPSTONE_ROOT/_internal/cache/rq3/multi_paradigm/" 2>/dev/null | wc -l)"
echo "  - multi_adaptive:  $(ls "$CAPSTONE_ROOT/_internal/cache/rq3/multi_adaptive/" 2>/dev/null | wc -l)"
echo "  - ensemble:        $(ls "$CAPSTONE_ROOT/experiments/results/cache/rq1/"*ensemble* 2>/dev/null | wc -l)"

# ===========================================================================
# Step 3: 분석 실행 (analyze_multi_paradigm + analyze_ensemble)
# ===========================================================================
echo ""
echo "[Step 3] 분석 실행 (2 script)"
echo "---------------------------------------------------"

cd "$CAPSTONE_ROOT"

echo "  [3-1] analyze_multi_paradigm.py 실행"
python3 _internal/scripts/analyze_multi_paradigm.py \
    || echo "  [WARN] analyze_multi_paradigm 실패 — 입력 부재 가능"

echo ""
echo "  [3-2] analyze_ensemble.py 실행"
python3 _internal/scripts/analyze_ensemble.py \
    || echo "  [WARN] analyze_ensemble 실패 — 입력 부재 가능"

# ===========================================================================
# Step 4: master_v6 §10.6 / §10.7 fill (manual review 요구)
# ===========================================================================
echo ""
echo "[Step 4] master_v6 §10.6 §10.7 fill (manual review 필요)"
echo "---------------------------------------------------"
echo "  대상 파일: experiments/results/RQ1_RQ2_RQ3_종합_master_v6_draft_filled_partial.md"
echo ""
echo "  fill 항목:"
echo "    §10.6 — Multi paradigm 광범위 (3 cell × 11 method × 2 SF, 단일→multi shrinkage 재계산)"
echo "    §10.7 — Multi Adaptive paired Δ% (단일 §10.7 와 비교)"
echo "    §10.8 (NEW) — Ensemble (Adaptive×4강 + Adaptive×11) 결과"
echo ""
echo "  [SKIP] 자동화 X — 분석 결과 검토 후 사용자 판단 + agent 위임 (~5분 each)"

# ===========================================================================
# Step 5: 자문 메일 v4 §2 Multi 결과 fill (manual review 요구)
# ===========================================================================
echo ""
echo "[Step 5] 자문 메일 v4 §2 fill (manual review 필요)"
echo "---------------------------------------------------"
ADVISORY_MD="$CAPSTONE_ROOT/submission/_drafts/속도는벡터_자문메일_박성원멘토_20260508_v4.md"
if [ -f "$ADVISORY_MD" ]; then
    echo "  대상: $ADVISORY_MD"
    echo "  fill: §2 Multi 결과 placeholder → analyze_multi_paradigm 출력 결과로 대체"
    echo "  [SKIP] 자동화 X — narrative 일관성 검토 후 사용자 commit"
else
    echo "  [WARN] $ADVISORY_MD 부재 — handoff_v14 §7 reference 확인"
fi

# ===========================================================================
# Step 6: PDF 재변환 (자문 메일 v4 finalize 후 trigger)
# ===========================================================================
echo ""
echo "[Step 6] PDF 재변환 (자문 메일 v4 finalize 후 수동 trigger)"
echo "---------------------------------------------------"
echo "  명령:"
echo "    python3 _internal/scripts/md2pdf.py \\"
echo "      submission/_drafts/속도는벡터_자문메일_박성원멘토_20260508_v4.md"
echo ""
echo "  [SKIP] §5 fill 후에만 trigger — 자동화 X (재 변환 시점 = 사용자 판단)"

# ===========================================================================
# 종료
# ===========================================================================
echo ""
echo "==================================================="
echo "5/9 morning finalize automation 종료"
echo "완료: $(date '+%Y-%m-%d %H:%M:%S KST')"
echo "==================================================="
echo ""
echo "다음 manual step:"
echo "  1. 분석 산출 review (cache/multi_paradigm_paired/, cache/ensemble_paired/)"
echo "  2. master_v6 §10.6 §10.7 §10.8 fill (agent 위임)"
echo "  3. 자문 메일 v4 §2 fill + PDF 재변환"
echo "  4. The End 리뷰 (_internal/the_end_review_checklist_20260508.md)"
echo "  5. handoff_v15 작성 (_internal/handoff_v15_template_20260508.md base)"
echo "  6. commit + push"
