#!/bin/bash
# SessionStart hook: 캡스톤 프로젝트 환경 상태 체크
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 기본 상태
RESEARCH_COUNT=$(ls "$PROJECT_ROOT/Research/"*.md 2>/dev/null | wc -l | tr -d ' ')
PAPERS_COUNT=$(ls "$PROJECT_ROOT/Research/papers/"*.pdf 2>/dev/null | wc -l | tr -d ' ')
HAS_TEMPLATES="false"
[[ -d "$PROJECT_ROOT/Templates/양식" ]] && HAS_TEMPLATES="true"

# Git 상태
BRANCH=$(cd "$PROJECT_ROOT" && git branch --show-current 2>/dev/null || echo "unknown")
UNCOMMITTED=$(cd "$PROJECT_ROOT" && git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

# 최근 변경
LAST_COMMIT=$(cd "$PROJECT_ROOT" && git log -1 --format="%h %s" 2>/dev/null || echo "none")

cat <<EOF
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "캡스톤 프로젝트 | branch: ${BRANCH} | 미커밋: ${UNCOMMITTED}건 | 분석문서: ${RESEARCH_COUNT}md | 원논문: ${PAPERS_COUNT}pdf | 템플릿: ${HAS_TEMPLATES} | 최근커밋: ${LAST_COMMIT}"}}
EOF
