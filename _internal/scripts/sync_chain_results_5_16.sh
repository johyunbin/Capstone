#!/bin/bash
# sync_chain_results_5_16.sh
# 서버 (capstone, 165.132.140.240) chain 결과 → local repo `_internal/cache/rq3/server_sync/` rsync.
#
# 5/15 chain 결과 5 stage:
#   v6_caseB_20260515_1404   (40 file, COMPLETE)
#   v7_extras_20260515_1515  (12 file, COMPLETE)
#   v6v7_fix_20260515_1602   (~16 file, 진행 중)
#   v10_full16_20260515_1613 (129 file, 진행 중)
#   v9_sel_sweep_*           (680 file, 대기 — 서버 上 미생성, placeholder)
#
# 사용법:
#   ./sync_chain_results_5_16.sh                # 전체 5 stage 실측 sync
#   ./sync_chain_results_5_16.sh --dry-run      # dry-run (전송 없이 plan 출력)
#   ./sync_chain_results_5_16.sh --stage v6_caseB --dry-run   # 1 stage 만 sample dry-run
#   ./sync_chain_results_5_16.sh --stage v6_caseB             # 1 stage 만 실측 sync
#
# 다음 단계: `python3 _internal/scripts/reorganize_chain_results_5_16.py`
# 로 server_sync/ → experiments/results/raw/Type{1..4b}/{cell}_RQ3_CaseB/ reorganize.

set -euo pipefail

# 경로
LOCAL_BASE="/Users/hyunbin/Capstone/_internal/cache/rq3/server_sync"
SERVER_BASE="/mnt/hdd0/home/capstone2026"
SSH_HOST="capstone"

# stage 정의 (server 디렉토리명 → local 서브디렉토리명)
declare -a STAGES=(
  "results_v6_caseB_20260515_1404:v6_caseB"
  "results_v7_extras_20260515_1515:v7_extras"
  "results_v6v7_fix_20260515_1602:v6v7_fix"
  "results_v10_full16_20260515_1613:v10_full16"
  "results_v9_sel_sweep_*:v9_sel_sweep"
)

# argument parsing
DRY_RUN=""
STAGE_FILTER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN="--dry-run"
      shift
      ;;
    --stage)
      STAGE_FILTER="$2"
      shift 2
      ;;
    -h|--help)
      sed -n '2,18p' "$0"
      exit 0
      ;;
    *)
      echo "[ERR] unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

mkdir -p "$LOCAL_BASE"

echo "[INFO] sync_chain_results_5_16.sh $(date '+%Y-%m-%d %H:%M:%S KST')"
echo "[INFO] LOCAL_BASE=$LOCAL_BASE"
echo "[INFO] SERVER=$SSH_HOST:$SERVER_BASE"
[[ -n "$DRY_RUN" ]] && echo "[INFO] mode=DRY-RUN"
[[ -n "$STAGE_FILTER" ]] && echo "[INFO] stage filter=$STAGE_FILTER"
echo ""

for entry in "${STAGES[@]}"; do
  src_pattern="${entry%%:*}"
  dst_name="${entry##*:}"

  # stage filter
  if [[ -n "$STAGE_FILTER" && "$dst_name" != "$STAGE_FILTER" ]]; then
    continue
  fi

  dst_dir="$LOCAL_BASE/$dst_name"
  mkdir -p "$dst_dir"

  echo "===> [$dst_name] $src_pattern"

  # server 上 디렉토리 존재 여부 확인 (wildcard 포함)
  if ! ssh "$SSH_HOST" "ls -d $SERVER_BASE/$src_pattern" >/dev/null 2>&1; then
    echo "  [SKIP] 서버 上 미존재 ($src_pattern) — placeholder, 추후 launch 후 재실행."
    continue
  fi

  # rsync (-avz --update, log 디렉토리 제외, COMPLETE.flag 포함)
  rsync -avz --update $DRY_RUN \
    --exclude='logs/' \
    --exclude='__pycache__/' \
    "$SSH_HOST:$SERVER_BASE/$src_pattern/" \
    "$dst_dir/" \
    2>&1 | tail -20

  echo ""
done

echo "[DONE] $(date '+%Y-%m-%d %H:%M:%S KST')"
echo ""
echo "다음:"
echo "  python3 /Users/hyunbin/Capstone/_internal/scripts/reorganize_chain_results_5_16.py --dry-run"
echo "  python3 /Users/hyunbin/Capstone/_internal/scripts/reorganize_chain_results_5_16.py"
