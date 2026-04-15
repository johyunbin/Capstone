#!/bin/bash
# [10] 10_클로드코드활용_실행.sh — Phase별 독립 claude 세션으로 CC 활용 점검
# 사용: cd ~/Capstone && ./guideline/10_클로드코드활용지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/활용.log"
STATE="guideline/PHASE_STATE_10_활용.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== CC활용 점검 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5)
PHASE_NAMES=(
  "현재 상태 진단"
  "CLAUDE.md 최적화"
  "컨텍스트 전략 점검"
  "워크플로우 자동화 점검"
  "구현"
  "검증 + 기록"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 CC활용 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/10_클로드코드활용지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. Phase 4(구현)에서는 각 변경을 기록만 하고, 실적용은 사용자 승인 후" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== CC활용 점검 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
