#!/bin/bash
# [05] 05_주간보고_실행.sh — Phase별 독립 claude 세션으로 주간보고 실행
# 사용: cd ~/Capstone && ./guideline/05_주간보고지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/주간보고.log"
STATE="guideline/PHASE_STATE_05_주간보고.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 주간보고 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4)
PHASE_NAMES=(
  "데이터 수집"
  "주간 요약 작성"
  "노션 동기화 확인"
  "다음 주 계획"
  "리포트 출력"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 주간보고 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/05_주간보고지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. 저장 위치: records/weekly/주간보고_$(date +%Y-%m-%d).md" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 주간보고 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
