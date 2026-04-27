#!/bin/bash
# [00] 00_점검_실행.sh — Phase별 독립 claude 세션으로 점검 실행
# 사용: cd ~/Capstone && ./guideline/00_점검지침_실행.sh
# 로그: guideline/점검.log 에 전체 출력 기록

set -euo pipefail
cd ~/Capstone

LOG="guideline/점검.log"
STATE="guideline/PHASE_STATE_00_점검.md"
TOOLS="Read,Write,Edit,Bash,Glob,Grep,WebFetch"

echo "=== 점검 시작: $(date) ===" | tee "$LOG"

PHASES=(0 1 2 3 4 5 6 7)
PHASE_NAMES=(
  "인벤토리 수집"
  "2종 세트 완성도 검증"
  "PDF 폰트 검증"
  "파일명 규칙 검증"
  "orphan 및 중복 검사"
  "원논문 ↔ 총정리 대응"
  "일정 + 사이트 점검"
  "종합 리포트"
)

for i in "${!PHASES[@]}"; do
  P="${PHASES[$i]}"
  NAME="${PHASE_NAMES[$i]}"
  echo "" | tee -a "$LOG"
  echo "=== Phase $P: $NAME 시작 — $(date) ===" | tee -a "$LOG"

  claude -p "Capstone 프로젝트 점검 Phase $P ($NAME) 실행.

1. guideline/PHASE_STATE_00_점검.md 읽고 이전 Phase 결과 확인
2. guideline/00_점검지침_auto.md 의 Phase $P 체크리스트 수행
3. 완료 후 guideline/PHASE_STATE_00_점검.md 업데이트
4. 발견 사항 기록, 수정은 하지 않음 (점검 = 읽기 전용)" \
    --allowedTools "$TOOLS" \
    --permission-mode "bypassPermissions" \
    2>&1 | tee -a "$LOG"

  echo "=== Phase $P: $NAME 완료 — $(date) ===" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=== 점검 전체 완료: $(date) ===" | tee -a "$LOG"
echo "결과 확인: cat $STATE" | tee -a "$LOG"
