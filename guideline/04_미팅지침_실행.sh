#!/bin/bash
# [04] 04_미팅_실행.sh — Phase별 독립 claude 세션으로 미팅 지원 실행
# 사용: cd ~/Capstone && ./guideline/04_미팅지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/미팅.log"
STATE="guideline/PHASE_STATE_04_미팅.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 미팅 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4)
PHASE_NAMES=(
  "미팅 유형 파악 + 인벤토리"
  "미팅 전 — 브리핑/심층분석"
  "미팅 후 — 회의록 작성"
  "후속 과제 추출 및 추적"
  "종합 확인"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 미팅 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/04_미팅지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. 회의록 저장: records/kakaotalk/YYYYMMDD_제목.md" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 미팅 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
