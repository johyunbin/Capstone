#!/bin/bash
# [01] 01_실험_실행.sh — Phase별 독립 claude 세션으로 실험 실행
# 사용: cd ~/Capstone && ./guideline/01_실험지침_실행.sh
set -euo pipefail
cd ~/Capstone

LOG="guideline/실험.log"
STATE="guideline/PHASE_STATE_01_실험.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep"

echo "=== 실험 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5)
PHASE_NAMES=(
  "환경 확인"
  "환경 구축 (첫 실행 시만)"
  "데이터셋 준비"
  "벤치마크 실행"
  "결과 수집 + 분석"
  "시각화 + 로그 기록"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 실험 Phase $P ($NAME) 실행.

1. $STATE 읽고 이전 Phase 결과 확인
2. guideline/01_실험지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 $STATE 업데이트
4. 환경 정보(PG 버전, HW 스펙) 반드시 기록" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 실험 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
