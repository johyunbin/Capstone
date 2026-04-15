#!/bin/bash
# SessionStart hook: 캡스톤 프로젝트 환경 상태 체크
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Git pull (최신 상태 동기화)
PULL_RESULT=$(cd "$PROJECT_ROOT" && git pull --no-rebase origin main 2>&1)
if echo "$PULL_RESULT" | grep -q "Already up to date"; then
  PULL_STATUS="최신"
elif echo "$PULL_RESULT" | grep -qE "^Updating|Fast-forward"; then
  PULL_STATUS="업데이트됨"
else
  PULL_STATUS="pull실패: $(echo "$PULL_RESULT" | head -1)"
fi

# 기본 상태
RESEARCH_COUNT=$(ls "$PROJECT_ROOT/research/summaries/"*.md 2>/dev/null | wc -l | tr -d ' ')
PAPERS_COUNT=$(ls "$PROJECT_ROOT/research/papers/"*.pdf 2>/dev/null | wc -l | tr -d ' ')
HAS_TEMPLATES="false"
[[ -d "$PROJECT_ROOT/templates/forms" ]] && HAS_TEMPLATES="true"

# Git 상태
BRANCH=$(cd "$PROJECT_ROOT" && git branch --show-current 2>/dev/null || echo "unknown")
UNCOMMITTED=$(cd "$PROJECT_ROOT" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

# 최근 변경
LAST_COMMIT=$(cd "$PROJECT_ROOT" && git log -1 --format="%h %s" 2>/dev/null || echo "none")

# Remote Control 상태 확인
RC_STATUS="⚠️ Remote Control 비활성 — 재시작: \`~/.local/bin/claude --rc\`"
# 부모 프로세스 체인에서 --rc / --remote-control 플래그 확인
CHECK_PID=$$
for _ in 1 2 3 4 5; do
  CHECK_PID=$(ps -p $CHECK_PID -o ppid= 2>/dev/null | tr -d ' ')
  [[ -z "$CHECK_PID" || "$CHECK_PID" == "1" ]] && break
  CMD=$(ps -p $CHECK_PID -o args= 2>/dev/null || echo "")
  if echo "$CMD" | grep -qE '\-\-rc\b|\-\-remote-control\b'; then
    RC_STATUS="✅ Remote Control 활성화"
    break
  fi
done

# 고아 워크트리 감지
WORKTREE_COUNT=0
WORKTREE_MERGED=0
if [ -d "$PROJECT_ROOT/.claude/worktrees" ]; then
  WORKTREE_COUNT=$(find "$PROJECT_ROOT/.claude/worktrees" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  for wt in "$PROJECT_ROOT/.claude/worktrees"/*/; do
    [ -d "$wt" ] || continue
    WT_BRANCH=$(cat "$wt/.git" 2>/dev/null | grep -o 'refs/heads/[^ ]*' | head -1)
    if [ -n "$WT_BRANCH" ] && cd "$PROJECT_ROOT" && git branch --merged main 2>/dev/null | grep -q "$(basename "$WT_BRANCH")"; then
      WORKTREE_MERGED=$((WORKTREE_MERGED + 1))
    fi
  done
fi

# stale 메모리 감지 (2주+ 미수정)
MEMORY_DIR="$HOME/.claude/projects/-Users-hyunbin-Capstone/memory"
STALE_MEMORY=0
if [ -d "$MEMORY_DIR" ]; then
  STALE_MEMORY=$(find "$MEMORY_DIR" -name "*.md" -not -name "MEMORY.md" -not -path "*/archive/*" -mtime +14 2>/dev/null | wc -l | tr -d ' ')
fi

HYGIENE_STATUS=""
[ "$WORKTREE_COUNT" -gt 0 ] && HYGIENE_STATUS="워크트리: ${WORKTREE_COUNT}개"
[ "$WORKTREE_MERGED" -gt 0 ] && HYGIENE_STATUS="${HYGIENE_STATUS} (${WORKTREE_MERGED} merged)"
[ "$STALE_MEMORY" -gt 0 ] && HYGIENE_STATUS="${HYGIENE_STATUS} | stale 메모리: ${STALE_MEMORY}건"

cat <<EOF
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "캡스톤 프로젝트 | branch: ${BRANCH} | git pull: ${PULL_STATUS} | 미커밋: ${UNCOMMITTED}건 | 분석문서: ${RESEARCH_COUNT}md | 원논문: ${PAPERS_COUNT}pdf | 템플릿: ${HAS_TEMPLATES} | 최근커밋: ${LAST_COMMIT} | RC: ${RC_STATUS} | ${HYGIENE_STATUS}"}}
EOF
