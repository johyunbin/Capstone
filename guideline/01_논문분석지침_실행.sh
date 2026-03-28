#!/bin/bash
# [01] 01_논문분석_실행.sh — Phase별 독립 claude 세션으로 논문분석 실행
# 사용: cd ~/Capstone && ./guideline/01_논문분석지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/논문분석.log"
STATE="guideline/PHASE_STATE_01_논문분석.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 논문분석 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4)
PHASE_NAMES=(
  "인벤토리 + 번호 확인"
  "대상 논문 선택 + 읽기"
  "총정리 md 작성"
  "시리즈 분석 (선택)"
  "품질 체크 + PDF 변환"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 논문분석 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/01_논문분석지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. 한국어 학술 산문, 실험 조건과 한계까지 포함" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 논문분석 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
