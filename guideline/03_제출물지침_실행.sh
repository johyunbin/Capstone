#!/bin/bash
# 제출물지침 자동 실행 스크립트
# 사용법: cd ~/Capstone && ./guideline/03_제출물지침_실행.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/03_제출물지침.log"

echo "=== 제출물지침 시작: $(date) ===" | tee "$LOG_FILE"

# Phase 0: 일정 확인 + 다음 마감 식별
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 0: 일정 확인 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

echo "== CLAUDE.md 미완료 일정 ==" | tee -a "$LOG_FILE"
grep "⬜" CLAUDE.md 2>/dev/null | tee -a "$LOG_FILE" || echo "(미완료 항목 없음)" | tee -a "$LOG_FILE"

python3 -c "
from datetime import date
deadlines = {
    '연구제안서 + 수행계획서': date(2026, 4, 2),
}
today = date.today()
print(f'오늘: {today}')
for name, d in sorted(deadlines.items(), key=lambda x: x[1]):
    delta = (d - today).days
    if delta > 0:
        print(f'{name}: D-{delta}')
    elif delta == 0:
        print(f'{name}: D-DAY!')
    else:
        print(f'{name}: D+{abs(delta)} (지남)')
" 2>&1 | tee -a "$LOG_FILE"

# Phase 1: 양식 확인
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 1: 양식 확인 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

echo "== templates/forms/ ==" | tee -a "$LOG_FILE"
ls templates/forms/ 2>/dev/null | grep -v DS_Store | tee -a "$LOG_FILE" || echo "(양식 없음)" | tee -a "$LOG_FILE"

echo "== templates/samples/ ==" | tee -a "$LOG_FILE"
ls templates/samples/ 2>/dev/null | grep -v DS_Store | tee -a "$LOG_FILE" || echo "(샘플 없음)" | tee -a "$LOG_FILE"

# Phase 2: 기존 자료 수집
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 2: 기존 자료 현황 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

echo "설계안: $(ls plans/연구_설계안_* 2>/dev/null | wc -l | tr -d ' ')건" | tee -a "$LOG_FILE"
echo "기획안: $(ls plans/연구_기획안_* 2>/dev/null | wc -l | tr -d ' ')건" | tee -a "$LOG_FILE"
echo "분석 시리즈: $(ls research/analysis/*.md 2>/dev/null | wc -l | tr -d ' ')건" | tee -a "$LOG_FILE"
echo "총정리: $(ls research/summaries/*.md 2>/dev/null | wc -l | tr -d ' ')건" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "== 기존 제출물 ==" | tee -a "$LOG_FILE"
ls submission/ 2>/dev/null | grep -v DS_Store | tee -a "$LOG_FILE" || echo "(제출물 없음)" | tee -a "$LOG_FILE"

# Phase 3~5: Claude Code에게 위임
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 3~5: Claude Code 위임 ---" | tee -a "$LOG_FILE"
echo "제출물 작성/검증/일정 동기화는 Claude Code 세션에서 실행합니다." | tee -a "$LOG_FILE"
echo "아래 명령어로 Claude에게 위임:" | tee -a "$LOG_FILE"
echo '  claude --print "guideline/03_제출물지침_auto.md 읽고 전체 Phase 실행"' | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== 제출물지침 완료: $(date) ===" | tee -a "$LOG_FILE"
echo "상세 로그: ${LOG_FILE}"

# Claude Code 연동 (전체 Phase를 Claude에게 위임할 경우)
# claude --print "guideline/03_제출물지침_auto.md 읽고 전체 Phase 실행" 2>&1 | tee -a "$LOG_FILE"
