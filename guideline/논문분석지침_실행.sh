#!/bin/bash
# 논문분석지침 자동 실행 스크립트
# 사용법: cd ~/Capstone && ./guideline/논문분석지침_실행.sh [논문PDF경로]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/논문분석지침.log"

echo "=== 논문분석지침 시작: $(date) ===" | tee "$LOG_FILE"

# Phase 0: 인벤토리 + 번호 확인
echo "" | tee -a "$LOG_FILE"
echo "--- Phase 0: 인벤토리 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

PAPERS=$(ls research/papers/*.pdf 2>/dev/null | wc -l | tr -d ' ')
S_MD=$(ls research/summaries/*.md 2>/dev/null | wc -l | tr -d ' ')
S_PDF=$(ls research/summaries/*.pdf 2>/dev/null | wc -l | tr -d ' ')
A_MD=$(ls research/analysis/*.md 2>/dev/null | wc -l | tr -d ' ')
A_PDF=$(ls research/analysis/*.pdf 2>/dev/null | wc -l | tr -d ' ')

echo "papers: ${PAPERS}" | tee -a "$LOG_FILE"
echo "summaries: ${S_MD} md, ${S_PDF} pdf" | tee -a "$LOG_FILE"
echo "analysis: ${A_MD} md, ${A_PDF} pdf" | tee -a "$LOG_FILE"

# 현재 최대 번호
MAX_S=$(ls research/summaries/*.md 2>/dev/null | sed -E 's/.*\[([0-9]+)\].*/\1/' | sort -n | tail -1)
MAX_A=$(ls research/analysis/*.md 2>/dev/null | sed -E 's/.*\(([0-9]+)\).*/\1/' | sort -n | tail -1)

echo "summaries 최대번호: [${MAX_S}] → 다음: [$((MAX_S + 1))]" | tee -a "$LOG_FILE"
echo "analysis 최대번호: (${MAX_A}) → 다음: ($(printf '%02d' $((10#$MAX_A + 1))))" | tee -a "$LOG_FILE"

# 2종 세트 확인
echo "" | tee -a "$LOG_FILE"
echo "--- 2종 세트 확인 ---" | tee -a "$LOG_FILE"
MISSING=0

cd "$PROJECT_ROOT/research/summaries"
for f in *.md; do
  pdf="${f%.md}.pdf"
  if [ ! -f "$pdf" ]; then
    echo "MISSING PDF: summaries/$pdf" | tee -a "$LOG_FILE"
    MISSING=$((MISSING + 1))
  fi
done

cd "$PROJECT_ROOT/research/analysis"
for f in *.md; do
  pdf="${f%.md}.pdf"
  if [ ! -f "$pdf" ]; then
    echo "MISSING PDF: analysis/$pdf" | tee -a "$LOG_FILE"
    MISSING=$((MISSING + 1))
  fi
done

echo "누락 PDF: ${MISSING}건" | tee -a "$LOG_FILE"

# 품질 체크 (파일명 규칙)
echo "" | tee -a "$LOG_FILE"
echo "--- 파일명 규칙 확인 ---" | tee -a "$LOG_FILE"
cd "$PROJECT_ROOT"

python3 -c "
import re, os
s_pat = re.compile(r'^\[\d+\] .+ 총정리\.(md|pdf)$')
a_pat = re.compile(r'^\(\d+\) .+\.(md|pdf)$')
errors = 0

for f in sorted(os.listdir('research/summaries')):
    if f.startswith('.'): continue
    if not s_pat.match(f):
        print(f'summaries 비규격: {f}')
        errors += 1

for f in sorted(os.listdir('research/analysis')):
    if f.startswith('.'): continue
    if not a_pat.match(f):
        print(f'analysis 비규격: {f}')
        errors += 1

print(f'비규격: {errors}건')
" 2>&1 | tee -a "$LOG_FILE"

# 인자로 논문 경로가 주어진 경우 Claude에게 분석 위임
if [ -n "${1:-}" ]; then
  PAPER_PATH="$1"
  echo "" | tee -a "$LOG_FILE"
  echo "--- 논문 분석 요청: ${PAPER_PATH} ---" | tee -a "$LOG_FILE"
  echo "Claude Code에 분석 위임..." | tee -a "$LOG_FILE"
  # claude --print "guideline/논문분석지침_auto.md 읽고 ${PAPER_PATH} 논문 총정리 작성" \
  #   2>&1 | tee -a "$LOG_FILE"
  echo "(claude 명령어 주석 해제하여 실행)"
fi

echo "" | tee -a "$LOG_FILE"
echo "=== 논문분석지침 완료: $(date) ===" | tee -a "$LOG_FILE"
echo "상세 로그: ${LOG_FILE}"
