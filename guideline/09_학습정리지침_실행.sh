#!/bin/bash
# [09] 09_학습정리_실행.sh — Phase별 독립 claude 세션으로 학습정리 실행
# 사용: cd ~/Capstone && ./guideline/09_학습정리지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/학습정리.log"
STATE="guideline/PHASE_STATE_09_학습정리.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 학습정리 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5)
PHASE_NAMES=(
  "인벤토리 수집"
  "전수 읽기"
  "주제별 분류 및 핵심 추출"
  "Apple Notes 저장"
  "메모리 + 전역 지침 반영"
  "완료 보고"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 학습정리 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/09_학습정리지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. 전수 읽기 원칙 — 모든 글자를 읽고 구체적 정보 보존" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 학습정리 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
